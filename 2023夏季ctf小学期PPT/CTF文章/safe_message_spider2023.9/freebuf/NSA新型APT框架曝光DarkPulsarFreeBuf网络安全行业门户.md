## 前言

 **2017年3月，ShadowBrokers放出了一份震惊世界的机密文档，其中包括两个框架：DanderSpritz和FuzzBunch。**

DanderSpritz完全由插件组成，用于收集情报、利用漏洞和操控已接管的设备。它基于Java编写，提供类似于僵尸网络管理面板的图形界面以及类似Metasploit工具的控制面板。它还整合了用于非FuzzBunch受控设备的后门和插件。

![DanderSprit界面](https://image.3001.net/images/20181023/15402744494025.png!small)

DanderSprit界面

## 概述

Fuzzbunch为不同的实用程序提供了一个用于交互和协同工作的框架，包含各种类型的插件，其目的是分析对象、利用漏洞、植入任务等。FuzzBunch框架插件包中的文件分为三种类型：

    
    
    ％pluginName％-version.fb

这是框架的实用程序文件。它从XML复制标头并包含插件的ID。

    
    
    ％pluginName％-version.exe

当FuZZbuNch收到执行命令时，运行此可执行文件。

    
    
    ％pluginName％-version.xml

此配置文件描述了插件的输入和输出参数的名称、类型和描述。这些信息都可以通过FuzzBunch界面显示。这种文件类型划分规范了默认参数的设置，从而提升了框架的可用性。

ImplantConfig是一个Fuzzbunch可调用的工具包，包含一个名为 **DarkPulsar**
的管理模块，用于管理受控设备的插件，用于控制名为“sipauth32.tsp”的远程控制后门。

它支持以下命令：

    
    
    Burn
    
    RawShellcode
    
    EDFStagedUpload
    
    DisableSecurity
    
    EnableSecurity
    
    UpgradeImplant
    
    PingPong

Burn、RawShellcode、UpgradeImplant和PingPong支持移除/升级植入软件、运行任意代码和检查后门是否已安装在远程机器上，其他命令的目的暂不明确。

卡巴斯基实验室在分析DarkPulsar时发现了几个用于加密C＆C和植入软件之间流量的常量：

![加密常量](https://image.3001.net/images/20181023/15402745432880.png!small)

卡巴斯基认为这些常量可以作为进一步深入调查的抓手，所以构建了一个检测器。几个月后，神秘的DarkPulsar后门浮出水面，而且包含32位和64位版本。研究人员发现大约50个案例，分别位于俄罗斯、伊朗和埃及，常见感染Windows
2003/2008服务器，涉及 **核能** 、 **电信** 、 **IT** 、 **航空航天** 和 **研发** 等领域。

## DarkPulsar技术亮点

DarkPulsar植入的是一个动态库文件，从其工作负载导出的函数来看可以实现以下几类功能：

> 两个匿名函数用于在系统中安装后门。

> 名称与TSPI（电话服务提供程序接口）操作相关的函数，用于确保后门存在于自动运行列表中并自动启动。

> 名称与SSPI（安全支持提供程序接口）操作相关的函数，主要用于运行恶意代码。

SSPI和TSPI接口的实现很简单，使得DarkPulsar导出的函数与接口函数的名称相同即可，只不过用恶意代码替代了正确的电话服务。

这个动态库通过匿名函数安装在系统中，调用具有管理员权限的`Secur32.AddSecurityPackage`以及参数中它自己库的路径来启动后门，使得`lsass.exe`将DarkPulsar加载为SSP/AP并调用其导出的函数`SpLsaModeInitialize`，由DarkPulsar初始化后门。其中AddSecurityPackage用于将代码注入到`lsass.exe`。它还在`HKLM\Software\Microsoft\Windows\CurrentVersion\Telephony\Providers`中添加了其库文件名。

这样一来Telephony
API（TapiSrv）开始加载随着远程访问连接管理器（RasMan）服务启动开始加载，将该启动类型设置为“自动”。加载电话服务提供商的库时，TapiSrv调用`TSPI_lineNegotiateTSPIVersion`，其中包含AddSecurityPackage调用以将恶意代码注入到`lsass.exe`中。

DarkPulsar通过为`SpAcceptLsaModeContext`（负责身份验证的函数）安装钩子来实现恶意功能。此类注入行为在进程`lsass.exe`中的多个系统身份验证数据包中进行，并允许Darkpulsar根据以下协议控制身份验证过程：

> 1、Msv1_0.dll - 用于NTLM协议，
>
> 2、Kerberos.dll - 用于Kerberos协议，
>
> 3、Schannel.dll - 用于TLS / SSL协议，
>
> 4、Wdigest.dll - 用于摘要协议，
>
> 5、Lsasrv.dll-用于谈判协议。

在完成这个过程之后，Darkpulsar能够将恶意软件流量嵌入到系统协议中。由于此类网络活动是根据系统标准进行的，因此它只会反映在系统进程中，也就是说它使用了为上述协议保留的系统端口，而不会妨碍其正常运行。

![嵌入到系统协议](https://image.3001.net/images/20181023/15402746398441.png!small)

成功连接到DarkPulsar植入软件的网络流量

控制身份验证过程的第二个优势是可以绕过输入用户名和密码保护，以获取对需要身份验证的对象的访问权限，例如进程列表、远程注册表、SMB文件系统。发送Darkpulsar的DisableSecurity命令后，受控设备的后门钩子将调用`SpAcceptLsaModeContext`函数，使得该函数传递的凭据有效，然后系统将提供对客户端的受保护对象的访问权限。

## 使用DarkPulsar

Darkpulsar-1.1.0.exe提供基于“一个命令+一次启动”原则构建的管理界面。要执行的命令必须在配置文件Darkpulsar-1.1.0.9.xml中指定，或者作为命令行参数指定，至少详细说明：

> 目标机器是使用32位还是64位系统；

> 协议（支持SMB、NBT、SSL、RDP协议）以提供命令和端口号；

> 用于解密会话AES密钥的私有RSA密钥。

Darkpulsar-1.1.0是Fuzzbunch框架的插件，可以管理参数和协调不同的组件。以下是Fuzzbunch中的DisableSecurity命令实例：

![DisableSecurity命令实例](https://image.3001.net/images/20181023/15402746937264.png!small)

下面是运行DisableSecurity之后的进程表实例，允许执行任何没有有效凭据的插件，并通过常规系统功能（远程注册表服务）进行操作：

![常规系统功能（远程注册表服务）](https://image.3001.net/images/20181023/15402747137280.png!small)  

## DanderSpritz

DanderSpritz是用于控制受感染机器的框架，与FuZZbuNch不同，因为后者为具有特定功能的后期开发阶段提供了部分工具包，例如DisableSecurity和DarkSeuls的EnableSecurity。

DanderSpritz适用于更大范围的后门，在受控设备中使用PeedleCheap来启动攻击者的恶意软件。PeddleCheap是DanderSpritz的插件，可用于配置植入软件并连接到受感染的机器。建立连接后，所有DanderSpritz后期开发功能均可用。

这就是EDFStagedUpload模式中的DarkPulsar通过植入恶意软件感染设备的渠道：PCDllLauncher（Fuzzbunch的插件）在受控设备一侧部署PeddleCheap植入软件，DanderSpritz提供用户友好的开发界面。所以，PCDllLauncher的全名是'PeddleCheap
DLL Launcher'。

整合DanderSpritz方案、PeddleCheap插件、DarkPulsar插件和PCDllLauncher到一起实现恶意功能共包含四个步骤：

> 通过FuZZbuNch，运行命令EDFStagedUpload以启动DarkPulsar。

> 在DanderSpritz中，运行命令pc_prep（PeedelCheap Preparation）以准备恶意代码和要启动的库文件。

> 在DanderSpritz中，运行命令pc_old（这是命令pc_listen -reuse -nolisten
> -key默认的别名），这会将其设置为等待来自Pcdlllauncher的socket。

> 通过FuZZbuNch启动Pcdlllauncher并指定使用ImplantFilename参数中的命令pc_prep准备的有效路径。

![DanderSpritz](https://image.3001.net/images/20181023/15402747644362.png!small)

DanderSpritz

![文件系统插件](https://image.3001.net/images/20181023/15402747924269.png!small)

文件系统插件

## 总结

FuzzBunch和DanderSpritz框架提供了很大的灵活性，包含诸多专为不同任务设计的插件，比如说FuzzBunch插件负责监控和攻击设备，DanderSpritz框架中的插件则是为管理已感染的受害者而开发的。

DarkPulsar后门的发现有助于理解它作为两个泄露框架之间的桥梁作用，以及它们如何成为同一攻击平台的一部分。这些平台是为长期潜伏攻击而设计的，从DarkPulsar的持久性和潜伏能力（例如将其流量封装到合法协议中并绕过密码保护以通过身份验证）可以看出背后的开发者非常之专业。

### 检测恶意网络活动

在受感染的计算机中执行EDFStagedUpload时，会建立永久连接，这是出现端口445流量的原因。`lsass.exe`中还出现了一对绑定的socket：

![检测恶意网络活动](https://image.3001.net/images/20181023/15402748392012.png!small)

当DanderSpritz通过PcDllLauncher插件部署PeddleCheap的恶意代码时，网络活动会急剧增加：

![检测恶意网络活动](https://image.3001.net/images/20181023/15402748614697.png!small)

当终止与受感染计算机的连接时，网络活动将停止，并且只保留`lsass.exe`中两个绑定socket：

![检测恶意网络活动](https://image.3001.net/images/20181023/15402748809131.png!small)

### IOC

植入 - 96f10cfa6ba24c9ecd08aa6d37993fe4

文件路径 - ％SystemRoot％\ System32 \ sipauth32.tsp

注册表 - HKLM \Software\Microsoft\Windows\CurrentVersion\Telephony\Providers

 ***参考来源：[securityweek](https://www.securityweek.com/nsa-linked-darkpulsar-exploit-tool-detailed)，Freddy编译整理，转载请注明来自
[FreeBuf.COM](http://freebuf.com/)。**

