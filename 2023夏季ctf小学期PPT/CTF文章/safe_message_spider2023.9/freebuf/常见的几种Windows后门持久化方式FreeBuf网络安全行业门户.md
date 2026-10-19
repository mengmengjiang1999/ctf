***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ** ***本文原创作者：si1ence，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
**

##  **0x0 背景**  

**持久化后门是指当入侵者通过某种手段拿到服务器的控制权之后，通过在服务器上放置一些后门（脚本、进程、连接之类），来方便他以后持久性的入侵，简单梳理一下日常遇见windows用的比较多的一些持久化方式方便以后排查问题使用。**

![图片1.png](https://image.3001.net/images/20190216/1550309021_5c67d69d22977.png!small)

##  **0x1 注册表自启动**

最常见的在指定键值添加一个新的键值类型为REG_SZ,数据项中添写需要运行程序的路径即可以启动，此类操作一些较为敏感容易被本地AV拦截，目前也是较为常见的一种方式。

![图片2.png](https://image.3001.net/images/20190216/1550309033_5c67d6a988577.png!small)

键值路径如下：

    
    
    HKEY_LOCAL_MACHINE\SOFTWARE\Microft\windows\currentversion\run

自启动项目如下：

![图片3.png](https://image.3001.net/images/20190216/1550309072_5c67d6d08a76c.png!small)

##  **0x2 用户登录**

在注册表路径：HKCU\Environment\

创建字符串键值：UserInitMprLogonScript

键值设置为特定的脚本路径即可：

![图片4.png](https://image.3001.net/images/20190216/1550309110_5c67d6f6b2dfc.png!small)

另外一种实现方式是修改winlogon Userinit字段：

    
    
    HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\Userinit

![图片5.png](https://image.3001.net/images/20190216/1550309123_5c67d70320520.png!small)

Powershell的一键修改命令如下：

    
    
    Set-ItemProperty "HKLM:\SOFTWARE\Microsoft\WINDOWS NT\CurrentVersion\Winlogon" -name Userinit -value "C:\Windows\system32\userinit.exe,***************"

##  **0x3 定时任务**

Windows实现定时任务主要有schtasks与at二种方式，一定层次说上schtasks是at命令的升级版、主要行为特别表现从一个特定的外网地址下载downloader样本或病毒母体或者维持CC通信的心跳包。

![图片6.png](https://image.3001.net/images/20190216/1550309138_5c67d712ae92a.png!small)

使用以下命令可以一键实现：

    
    
    "schtasks /create /sc minute /mo 1 /tn "chrome" /tr wscript.exe C:\Users\\AppData\Local\Temp\13442980_crypted.vbs"

![图片7.png](https://image.3001.net/images/20190216/1550309151_5c67d71f20f4b.png!small)

##  **0x4 WMI**

WMI是微软基于Web的企业管理（WBEM）的实现版本，这是一项行业计划，旨在开发用于访问企业环境中管理信息的标准技术。主要与Powershell命令配合使用可以实现无文件攻击重要方式，具有良好的隐蔽性也是目前较为常用的持久化手段。

关键实现的代码如下：

![图片8.png](https://image.3001.net/images/20190216/1550309166_5c67d72e43557.png!small)

WMI对象主要是执行一个WQL(WMI Query
Language)的查询后，本地调用Powershell执行响应的代码由于没有文件保存在本地磁盘能够较好的免查杀。

![图片9.png](https://image.3001.net/images/20190216/1550309179_5c67d73b067b0.png!small)

Black Hat
2015公布了一个WMIBackdoor的poc毕竟还是经典，在流行的powersploit与nishang框架里面也有相关的ps1文件。  

传送门： _<https://github.com/mattifestation/WMI_Backdoor>_

##  **0x5 webshell**

在指定的web服务器路径藏的很深的那种放置一个webshell，同时做好免杀后的shell往往比常规的系统后门更难被发现，这个操作很常规。

![图片10.png](https://image.3001.net/images/20190216/1550309192_5c67d7481d60a.png!small)

各类webshell种类比较多传送门：

 _<https://github.com/xl7dev/WebShell>_

##  **0x6 自启动服务** ****

简单的分为二种方式将自己的恶意的可执行文件注册成服务或者调用系统进程如svchost加载dll文件运行服务。第二种方式相对隐蔽性较好由于系统进程的特殊性往往不敢轻易终止进程，由于此类均在PE文件或者其他类型文件在磁盘中容易被查杀，特殊处理过的除外。

Metasploit可以使用Metsvc创建服务，此类操作极容易被AV查杀。

如下是永恒之蓝挖矿病毒一个常见病毒，通过伪装服务名为系统服务瞒天过海。

![图片11.png](https://image.3001.net/images/20190216/1550309207_5c67d7573992e.png!small)

在Meterpreter下可以运行run metsvc将会在目标主机上以Meterpreter的服务的形式注册在服务列表中，并开机自动自动：

![图片12.png](https://image.3001.net/images/20190216/1550309224_5c67d76884cec.png!small)

Windows服务端服务注册成功：

![图片13.png](https://image.3001.net/images/20190216/1550309238_5c67d776f25ab.png!small)

##  **0x7 dll劫持** ****

如果在进程尝试加载一个DLL时没有指定DLL的绝对路径，那么Windows会尝试去指定的目录下查找这个DLL；如果攻击者能够控制其中的某一
个目录，并且放一个恶意的DLL文件到这个目录下，这个恶意的DLL便会被进程所加载，从而造成代码执行。

比较常用的如LPK.dll的劫持：

win7及win7以上系统增加了KnownDLLs保护，需要在注册表：

    
    
    HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SessionManager\ExcludeFromKnownDlls

下添加 "lpk.dll" 才能顺利劫持：

![图片14.png](https://image.3001.net/images/20190216/1550309261_5c67d78d9ac11.png!small)

另外一种思路是通过查看被劫持的DLL的导出函数表，编程实现劫持DLL向原DLL的导出函数的转发，并加入你的恶意代码达到一个劫持的效果。

##  **0x8 COM劫持**

主要通过修改CLSID下的注册表键值，实现对CAccPropServicesClass和MMDeviceEnumerator劫持，而系统很多正常程序启动时需要调用这两个实例，所以，这就可以用作后门来使用，并且，该方法也能够绕过Autoruns对启动项的检测。

传送门如下： ** _<https://www.gdatasoftware.com/blog/2014/10/23941-com-object-hijacking-the-discreet-way-of-persistence>_**

![图片15.png](https://image.3001.net/images/20190216/1550309282_5c67d7a22082c.png!small)

Powershell版本的poc： _<https://github.com/3gstudent/COM-Object-hijacking>_

![图片16.png](https://image.3001.net/images/20190216/1550309298_5c67d7b29a8af.png!small)

##  **0x9 B** **ootkit**

MBR后门主要的思路是读取主引导记录和把分区表从主引导记录中复制出来。然后把自己的包含恶意二进制数据的主引导记录放到主引导扇区，并复制新的分区表到它。但是，并非只有分区表需要保留，还有原来的主引导记录也需要保存下来，MBR病毒复制原始主引导记录到其它64个未用到的扇区。到MBR病毒执行完自己的操作后在读取原始的主引导记录并跳到0x7c00处执行来引导开机。目前比较流行的比如暗云木马系列：

![图片17.png](https://image.3001.net/images/20190216/1550309314_5c67d7c21b710.png!small)

详细可参考腾讯的研究报告： **_<https://slab.qq.com/news/tech/1308.html>_**

通过PCHunter也能够进行简单的MBR的异常判断，此类后门往往具有较大的实施难度病毒种类往往也较少。

![图片18.png](https://image.3001.net/images/20190216/1550309327_5c67d7cfb7c5f.png!small)

##  **0x10 总结**

Windows环境的持久化还有更多霸气侧漏的姿势没有遇见总结到，相对于之前建立隐藏账户、网站跟目录下的webshell、一个后门的exe程序、定时任务这些手法一些更新的手法显得更加隐蔽与难以查杀，希望能给日常背锅的运维、安全应急、开发大佬与首席道歉师在客户现场搞的焦头烂额时候提供一些排查思路吧。

 ***本文原创作者：si1ence，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

