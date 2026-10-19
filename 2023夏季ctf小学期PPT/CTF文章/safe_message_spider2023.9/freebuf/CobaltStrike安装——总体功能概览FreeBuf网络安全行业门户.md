## Cobalt Strike 介绍

Cobalt Strike简称CS。是一个java编写的成熟的渗透测试框架，常用来做内网渗透。

集成了端口转发、服务扫描，自动化溢出，多模式端口监听，windows exe 木马生成，windows dll 木马生成，java 木马生成，office
宏病毒生成，木马捆绑。钓鱼攻击包括：站点克隆，目标信息获取，java 执行，浏览器自动攻击等等强大的功能！

在其3.0的版本之前是基础Metasploit框架工作，可使用metasploit的漏洞库。从3.0版本开始不在使用metasploit的框架，成为一个独立的渗透测试平台。  

## 安装Cobalt Strike运行环境

需要安装Java1.8的环境。

### 1.下载java1.8

 **地址：**

<https://www.oracle.com/java/technologies/javase/javase8u211-later-archive-downloads.html>

![1638280279_61a62c57ace99c4188949.png!small?1638280280434](https://image.3001.net/images/20211130/1638280279_61a62c57ace99c4188949.png!small?1638280280434)

### 2.安装

可选择在自己的公网服务器或者其他地方安装。

###
![1638280300_61a62c6cbceeeb25444ef.png!small?1638280301534](https://image.3001.net/images/20211130/1638280300_61a62c6cbceeeb25444ef.png!small?1638280301534)

### 3.配置环境变量

方法：1、右键点击【计算机】，选择【属性】，点击【高级系统设置】，打开环境变量设置；2、新建【JAVA_HOME】变量，并编辑【Path】变量；3、新建【Classpath】变量并编辑即可。

![1638280313_61a62c798799e21d30a4a.png!small?1638280314481](https://image.3001.net/images/20211130/1638280313_61a62c798799e21d30a4a.png!small?1638280314481)

### 4.查看结果

cmd查看java安装是否完毕（java -version）

![1638280328_61a62c8880c9c670b9e3d.png!small?1638280329273](https://image.3001.net/images/20211130/1638280328_61a62c8880c9c670b9e3d.png!small?1638280329273)

至此，如果跟上图结果一致，那么java1.8的环境就安装完毕了。

## 运行Cobalt Strike服务端与客户端

### 1.运行

Windows使用命令：teamserver IP 密码（一般服务端是放在公网的服务器上）

![1638280374_61a62cb68c1ab49044ecc.png!small?1638280375308](https://image.3001.net/images/20211130/1638280374_61a62cb68c1ab49044ecc.png!small?1638280375308)

### 2.客户端连接

主机：服务端的地址

端口：CS开启的端口，一般都是默认的50050（可更改）

用户：可自定义（不要与其他的冲突）

密码：在启动CS团队服务器的时间输入的密码

![1638280387_61a62cc3b8c339ffb1fd5.png!small?1638280388468](https://image.3001.net/images/20211130/1638280387_61a62cc3b8c339ffb1fd5.png!small?1638280388468)

### 3.坑点：连接超时。

![1638280403_61a62cd3604fddf703343.png!small?1638280404090](https://image.3001.net/images/20211130/1638280403_61a62cd3604fddf703343.png!small?1638280404090)

  1. 要注意端口是否开启
  2. 防火墙是否放行端口。
  3. 每次创建新的CS服务器时，都会验证一个指纹并且每次都不一样。作用是为了防篡改。  

## Cobalt Strike 功能概览

### 一、CS页面介绍

![1638280443_61a62cfb7ee3a986dfdf3.png!small?1638280444241](https://image.3001.net/images/20211130/1638280443_61a62cfb7ee3a986dfdf3.png!small?1638280444241)

分为：菜单栏、快捷栏、目录列表、命令输出区和命令输入区。

### 二、Cobalt strike模块详览

![1638280651_61a62dcb5f5cff5c1813f.png!small?1638280652170](https://image.3001.net/images/20211130/1638280651_61a62dcb5f5cff5c1813f.png!small?1638280652170)

New Connection：新建连接。

Preferences：偏好设置，首选项，设置主界面、控制台、Teamserver连接记录、报告的样式。

Visualization：可视化页面，将主机以不同的权限展示出来。

VPN interfaces：设置VPN的接口。

Listeners：创建监听器。

Script Manager：查看和加载CNA脚本

Close：关闭

### 三、View（视图）模块

![1638280670_61a62dde1e320c0c895e1.png!small?1638280670876](https://image.3001.net/images/20211130/1638280670_61a62dde1e320c0c895e1.png!small?1638280670876)

Applications：显示被控机器的应用信息。

Credentials：凭证信息，通过HashDump或mimikatz获取的密码或散列值都储存在这里。

Downloads：文件下载，从被控制的机器中。

Event Log：日志，主机上线记录，团队聊天记录和操作记录。

Keystrokes：键盘记录。

Proxy Pivots：代理

Screenshots：屏幕截图。

Script Console：脚本控制台，可加载各种脚本。

Targets：查看目标。

Web Logs：web日志。

### 四、Attacks（攻击）模块

![1638280688_61a62df0351a7cd809887.png!small?1638280689038](https://image.3001.net/images/20211130/1638280688_61a62df0351a7cd809887.png!small?1638280689038)

主要分为：后门攻击、钓鱼攻击。

### 五、Packages（后门）模块

![1638280719_61a62e0f4818d690de23d.png!small?1638280720076](https://image.3001.net/images/20211130/1638280719_61a62e0f4818d690de23d.png!small?1638280720076)

HTML
Application：基于HTML应用的payload模块，通过HTML调用其他语言的应用组件进行攻击，提供可执行文件、Powershell、VBA三种方法。

MS Office Macro：生成基于Office病毒的payload。

Payload Generator：Payload生成器，可以生成基于C、C#、COM
Script、Java、Perl、Poweshell、Python、Ruby、VBA等的payload。

Windows
Ececutable：可生成32位和64位的EXE和基于服务的EXE、DLL等后门。在32位Windows系统中无法执行64位的payload，而且对于后渗透的相关模块，使用32位和64位的payload会产生不同的影响。

Windows Ececutable(S)：用于生成一个exe可执行文件，其中包含Beacon的完整payload，不需要阶段性的请求。与Windows
Executable模块相比，该模块额外提供了代理设置，以便在较为苛刻的环境中进行渗透测试。该模块还支持powershell脚本，可用于将Stageless
Payload注入内存。

### 六、Web Drive-by（钓鱼攻击）模块

![1638280793_61a62e593d41be20664e1.png!small?1638280794773](https://image.3001.net/images/20211130/1638280793_61a62e593d41be20664e1.png!small?1638280794773)

Manage：管理器，对开启的web服务进行管理

Clone Site：克隆网站，可以记录受害者提交的数据

Host File：将指定文件加载到web中，支持修改Mime Type。

Scripted Web Delivery：基于web的攻击测试脚本，可自动生成payload，类似于Metasploit的web_delivery

Signed Applet Attack：使用java自签名的程序进行钓鱼攻击(该方法已过时)。

Smart Applet Attack：自动检测java版本并进行攻击，针对Java 1.6.0_45以下以及Java
1.7.0_21以下版本(该方法已过时)。

System Profiler：客户端。检测工具，用来获取系统信息，如系统版本，Flash版本，浏览器版本等。

### 七、Reporting（报告）模块

![1638280821_61a62e75e5a6b27ea9a25.png!small?1638280822843](https://image.3001.net/images/20211130/1638280821_61a62e75e5a6b27ea9a25.png!small?1638280822843)

可配合CS的操作记录、结果等，直接生成相关报告。

# Cobalt Strike 功能详解

### 监听（Listeners）模块payload详解

![1638280847_61a62e8f439faba0ef4ab.png!small?1638280847992](https://image.3001.net/images/20211130/1638280847_61a62e8f439faba0ef4ab.png!small?1638280847992)

包含了DNS、HTTP、HTTPS、SMB、TCP、External C2、Foreign HTTP、Foreign HTTPS。

 **DNS Beacon：**

采用DNS的方式对目标主机进行管理。在CS4.0版本后，DNS Beacon 是一个仅 DNS 的 payload， DNS Beacon 可以通过 DNS
TXT 记录、DNS AAAA 记录或 DNS A
记录下载任务。背后的原理其实也是很简单，域名解析服务器记录它指定该域名由哪个DNS服务器来进行解析而我们把它指向xxx.xxx也就是我们的CS服务器，这样每次查询xxx1.xxx.xxx，最后都会来和我们的CS服务器进行通信。
**注意** ：Beacon DNS payload上线后是不会显示目标信息的。

 **HTTP与HTTPS Beacon：**

HTTP和HTTPS基本上没有太大的区别，监听器配置选项都是一样的，只是HTTPS会多一个SSL证书配置，有较高得隐蔽性。HTTP与HTTPS
Beacon通过 HTTP GET 请求来下载任务。这些 Beacon 通过 HTTP POST 请求传回数据。

 **SMB Beacon：**

使用命名管道通过一个父 Beacon 进行通信。仅需配置一项Pipename(C2)也就是命名管道的名字。注意：
1.因为是将命名管道封装到SMB协议中，进行通信所以目标至少得能进行SMB协议通信开启SMB服务（必须接受445端口上得连接）2.因为是使用SMB协议，所以还需要注意一下访问权限否则可能无法连接对方（必须有目标主机的管理员组的权限或者说是拥有具有管理员组权限的凭据）。

 **TCP Beacon：**

与SMB Beacon类似只不过TCP Beacon不是使用SMB与父Beacon进行通信而是使用TCP socket进行通信。Bind to
localhost only选项是来配置TCP
Beacon监听绑定地址的，如果勾选上则仅绑定127.0.0.1本地ip，默认不勾选绑定在0.0.0.0，如果只绑定127.0.0.1那么只能进行本地连接，远程主机是无法访问的，0.0.0.0是监听所有地址（注：监听绑定非127.0.0.1
windows防火墙会有提示，远程主机不要勾选。）

 **External C2：**

外部C2，是一种特殊的监听器。

 **Foreign HTTP和Foreign HTTPS：**

对外监听器，这两种并没有什么太大的区别他们的关系和Beacon
HTTP(S)基本上差不多，这两种监听器一般用来派生会话到Metasploit或Empire。

  

## 后渗透模块

![1638281035_61a62f4b563c575e7daa0.png!small?1638281036299](https://image.3001.net/images/20211130/1638281035_61a62f4b563c575e7daa0.png!small?1638281036299)

 **转储Hash：**

beacon中输入hashdump，beacon会话框输出了目标机的用户名和密码hash值。

 **Run Mimikatz（导出凭证）：**

在beacon中执行logonpasswords命令当会话为管理员权限时，才能dump成功，如果权限很低，请先提权。通过视图模块的凭证信息，即可查看之前dump过的凭据信息。（注意：如果操作系统更新了KB2871997补丁或者版本高于Windows
Server2012，就无法在默认情况下抓取明文。）

 **SOCKS Server：**

简单来说就是把本机和目标机器通过Socks协议开启一个安全不受防火墙拦截的通道。

通过其他工具的proxy插件，并设定socks代理（代理的地址为teamserver的IP地址，端口为cs中显示的端口），配置完成以后，便可以通过受控机跳转到其内网。

 **Beacon常用命令：**

Getuid：获取当前beacon是使用哪个用户身份运行的、是否有管理员权限等。

Getsystem：尝试获取system权限。

Getprivs：获取当前beacon包含的所有权限。

## Cobalt Strike 简单操作

### 一、Cobalt Strike 监听器创建

 **1.打开Listen（可通过菜单栏和快捷栏打开）**

![1638280480_61a62d2029d16705ac4d9.png!small?1638280480903](https://image.3001.net/images/20211130/1638280480_61a62d2029d16705ac4d9.png!small?1638280480903)![1638280475_61a62d1b5bf63f7b79672.png!small?1638280476130](https://image.3001.net/images/20211130/1638280475_61a62d1b5bf63f7b79672.png!small?1638280476130)

 **2.添加一个新的监听器**

![1638280491_61a62d2bbd816c54be9c0.png!small?1638280493272](https://image.3001.net/images/20211130/1638280491_61a62d2bbd816c54be9c0.png!small?1638280493272)![1638280499_61a62d33b57d0bb2e9d36.png!small?1638280500621](https://image.3001.net/images/20211130/1638280499_61a62d33b57d0bb2e9d36.png!small?1638280500621)![1638280505_61a62d398a2e0313cac0c.png!small?1638280506276](https://image.3001.net/images/20211130/1638280505_61a62d398a2e0313cac0c.png!small?1638280506276)

 **3.攻击**

点击菜单栏Attacks，使用Web Drive-by中的Script Web Delivery。

 **注意：生成payload的端口与监听器的端口不可重复否则就会冲突。**

![1638280526_61a62d4e1d65e44b2279b.png!small?1638280526894](https://image.3001.net/images/20211130/1638280526_61a62d4e1d65e44b2279b.png!small?1638280526894)

 **4.执行**

点击开始，复制payload，放到cmd里面执行。

![1638280538_61a62d5a26da802a0cf29.png!small?1638280538947](https://image.3001.net/images/20211130/1638280538_61a62d5a26da802a0cf29.png!small?1638280538947)

 **5.上线成功**

对上线的主机进行右键，进入Beacon，在里面可以输入相应的命令进行查看操作等。

注意：1.输入shell命令时，要在命令前面加shell。如：shell whoami

2.Beacon每次回连的时间默认为60秒，可修改（sleep 0 回连时间0，建议不要太快流量会很明显）。

![1638280630_61a62db66a16b12f0dab5.png!small?1638280631164](https://image.3001.net/images/20211130/1638280630_61a62db66a16b12f0dab5.png!small?1638280631164)

###  **二、利用CS反弹shell（派生）**

 **1.创建msf外置监听器**

HTTPS Host写上msf IP，HTTPS Port写上msf监听端口。

![1638280954_61a62efa9e73d72231e0d.png!small?1638280955445](https://image.3001.net/images/20211130/1638280954_61a62efa9e73d72231e0d.png!small?1638280955445)

 **2.启动msf监听**

>  
>
>
> msf > use exploit/multi/handler
>
> msf exploit(handler) > set payload windows/meterpreter/reverse_https
>
> payload => windows/meterpreter/reverse_https
>
> msf exploit(handler) > set lhost msf ip
>
> lhost => msf ip
>
> msf exploit(handler) > set lport 8888
>
> lport => 8888
>
> msf exploit(handler) > exploit

 **3.反弹（派生）**

对已上线的主机右键，增加会话，并选择创建的msf外置监听器，msf即可接收到会话。（注意：派生时候，msf选择payload注意一下架构（x86）,在控制台输入“spawn
msf”也可。）

![1638281016_61a62f382149c213e1002.png!small?1638281016899](https://image.3001.net/images/20211130/1638281016_61a62f382149c213e1002.png!small?1638281016899)

![1638281023_61a62f3f0084ba0e6e7a7.png!small?1638281023785](https://image.3001.net/images/20211130/1638281023_61a62f3f0084ba0e6e7a7.png!small?1638281023785)

