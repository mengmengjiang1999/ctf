# 【安全报告】XShellGhost事件技术回顾报告

阅读量 **137945**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-09-15 18:59:12

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

****

**0x00 背景介绍**

8月份，NetSarang公司（NetSarang Computer, Inc.
是一家致力于全球安全连接解决方案领域的研发的公司，产品和服务覆盖全球90多个国家。）与安全厂商卡巴斯基联合发布声明，
”在2017年7月18日发布的全线产品在内的版本，均被植入了一份后门性质的恶意代码，该后门可能可以被攻击者直接利用”。

该事件被称为“ **XShellGhost**
”事件，“XShellGhost”被定性为因入侵感染供应链厂商引发的大范围安全事件，将直接导致使用NetSarang系列软件用户成为被远程控制的受害者。

360CERT获悉此事件后对该事件展开了分析，确认NetSarang公司在2017年7月18发布的Xmanager, Xshell, Xftp,
Xlpd等产品中的 **nssock2.dll** 模块中被植入了恶意代码。

本报告是360CERT对事件中所使用的攻击技术的一个回顾和总结。

**0x01 事件概述**

8月7日，NetSarang公司发布安全公告，称其最近更新（7月18日）的Xmanager
Enterprise、Xmanager、Xshell、Xftp、Xlpd五款软件存在安全漏洞，并表示8月5日已经发布了修复版本。

随后，经安全研究人员分析发现NetSarang公司在7月18日发布的nssock2.dll模块中被植入了恶意代码，直接影响到使用该系列软件的用户。

８月16日，NetSarang公司与安全厂商卡巴斯基联合发布声明，披露了恶意代码的相关信息。NetSarang公司并未解释漏洞的成因，外部分析可能是在产品发布生命周期被攻击，导致7月18日的版本被植入后门。

****

**0x02 官方声明**

长期以来为应对层出不穷的网络攻击，NetSarang公司采取了一系列的方法和举措来强化自身产品线的安全性，避免被恶意代码感染、商业间谍组织渗入的情况发生。

遗憾的是，在2017年7月18日发布的全线产品在内的版本，均被植入了一份后门性质的恶意代码，该后门可能可以被攻击者直接利用。

我们深知，客户和用户的安全是我们公司最高的优先级和根本，更是我们的职责所在。当今世界，通过攻击商业、合法性质的软件来获利或蓄意攻击其用户的攻击团伙和组织正在日益增长是一个真切的现实问题，在这里，NetSarang会和其它计算机软件行业里的公司一样，认真的应对这一挑战。

NetSarang致力于保护用户的隐私安全，且已经整合了一套坚实的体系来保证不会再有类似的具有安全缺陷的产品被输送到用户手中。NetSarang会继续评估和改进我们的安全，这不仅仅是为了打击来自世界各处的网络间谍团伙，更是为了让公司的忠实用户能够继续信任我们。”

目前Kaspersky的产品已经支持检测名为“Backdoor.Win32.ShadowPad.a”的ShadowPad样本。

Kaspersky实验室建议用户尽快更新到NetSarang产品软件的最新版本，在最新版本中恶意代码已经被移除，此外建议检测系统是否有对应的恶意域名访问记录。相关的C2域名和后门恶意代码技术信息已经在相关的技术报告中提及。

注：更多信息可以见[参考7]

****

**0x03 事件影响面**

**1.影响面**

该事件属于重大网络安全事件，实际影响范围广。

安全预警等级：橙色预警

**2.影响版本**

根据官方安全通告，确定涉及如下版本：

**Xmanager Enterprise 5.0 Build 1232**

**Xmanager 5.0 Build 1045**

**Xshell 5.0 Build 1325**

**Xshell 5.0 Build 1322**

**Xftp 5.0 Build 1218**

**Xlpd 5.0 Build 1220**

****

**0x04 恶意代码技术细节**

**1.整体流程**

受害者在安装，启动了带有后门的客户端后，nssock2.dll模块中的攻击代码会以Shellcode形式在后台被调用解密执行。

该Shellcode分为多加密块，基于插件模型架构，各模块之间负责不同功能且协调工作、相互调用，实际分析后发现中间存在大量对抗设计，隐秘性较强，该后门还包含了如下几个特点：

**无自启动项，无独立落地文件**

**存在花指令和部分加密函数设计**

**多种通信协议的远程控制**

**主动发送受害主机基本信息**

**通过特定的DGA(域名生成算法)产生的DNS域名传送至远程命令控制服务器**

**C &C服务器可动态下发任意代码至用户机器执行**

整体流程如下图所示：

后门的整体流程大致分为以下9个步骤：

1\. Xshell启动后会加载动态链接库nssock2.dll。

2\. 在DllMain执行前由全局对象构造启动引子代码。

3\. 引子代码主要功能就是解密shellcode1并跳转到入口处执行。

4\. shellcode1(loader)加载shellcode2。

5\. shellcode2中将搜集用户信息构造DNS
TXT包传送至根据年份和月份生成的DGA域名，同时接收解密shellcode3的key并写入注册表，一旦注册表中查询到对应的值随即解密shellcode3并执行。

6\. Shellcode3(loader)主要负责加载Root模块并跳转到入口处执行。

7\. Root被加载后接着分别加载Plugin，Config，Install，Online和DNS模块。

8\. Install模块会创建svchost.exe并把Root模块注入，实现持久化运行。

9\. Online模块会根据其配置初始化网络相关资源，向指定服务地址发送信息，并等待云端动态下发代码进行下一步攻击。

**2.Shellcode1(Loader)**

该后门是基于插件模式开发的，Root模块提供了插件的基本框架，各插件之间会相互调用，而在各个插件加载时都会多次用到同一个loader，loader中的代码中加入了化指令进行干扰，具体实现细节为如下8个步骤:

1\. 获取kernel32基地址。

2\. 获取所需相关函数地址（Loadlibary、GetProcAddress、VirtualAlloc、Sleep）。

3\. 申请空间，解密数据存储到申请的空间。

4\. 修复重定位。

5\. 填写导入表。

6\. 在函数头部判断是否下了INT3断点。

7\. 加密IAT项，手法比较简单，仅是将原API地址求补。

8\. 跳向shellcode入口

**3.Shellcode2**

Shellcode2主要作用就是将搜集的数据传出，并接收服务端传来的key解密shellcode3，执行后门的核心部分，Shellcode2实现细节如下：

1\. Shellcode2首先创建工作线程。

2\. 工作线程首先获取VolumeSerialNumber值并且异或0xD592FC92 这个值用来创建注册表项。

3\. 创建注册表项，位置为HKEY_CURRENT_USERSOFTWARE-[0-9](步骤2生成的数值)。

4\. 通过RegQueryValueExA查询步骤3创建注册表中Data键的值。

5\. 如果注册表Data已经存放key会直接用key解密shellcode3并执行。

6\. 不存在key则继续执行下面的循环，当不满足时间条件时循环每隔10秒获取一次时间， 满足时间条件时进入主流程执行步骤7。

7\. 主流程首先根据当前时间生成DGA域名 ，当前8月时间为nylalobghyhirgh.com

部分年份-月份生成的域名对应关系如下：

8\. 接着根据获取的当前网络、hostName 、DomainName 、UserNmae用特定算法生成字符串构造DNS_TXT数据包并向8.8.8.8
| 8.8.4.4 | 4.2.2.1 | 4.2.2.2 | 当前时间DGA域名
发送，然后等待服务器返回数据（解密Shellcode3的key）。此外，通过对12个域名分析NS解析情况后发现，
7月开始被注册解析到qhoster.net的NS Server上，所以猜测这个恶意代码事件至少是从7月开始的。

9\.
当接收到服务器的数据包后设置注册表Data数据，然后解密Shellcode3，Shellcode3依然是一个loader,该loader加载Root模块，其loader功能同上述的细节相同。

**4.Module Root**

Root模块是后门的关键部分，为其它模块提供了基本框架和互相调用的API，其中会加载五个模块分别为：Plugin、Online、Config、Install、DNS。

将自身函数表地址共享给其他模块使用，主要这些API主要涉及到一些模块加载、加解密等功能。

搜索5个模块Plugin、Online、Config、Install、DNS中的Install模块，还是可以通过跟上文一样，使用同样的Loader加载。

具体流程上：

1\. 解密后可以一个个dump下来

2\. 尝试调用Install模块(0x67)：

**5.Module Install**

Install负责把RootModule的Code注入到傀儡进程中和Online模块的初始化。

相关细节操作：

1\. 提升自身进程相关权限

2\. 调用config模块读取配置信息

3\.
根据不一样的配置信息走不一样的流程，如果都不等于的话将会注入winlogon.exe或者运行scvhost.exe并注入Root模块，启动执行Online模块。

**6.Module Config**

Config模块主要负责配置信息的存储和读取功能，当模块初始化函数传入的参数为100时，会保存一些默认配置信息到磁盘中，同时Config模块也提供了将配置信息发送到CC服务器的接口。

当插件入口函数参数 a2==100时会执行加密配置信息写入到磁盘，具体存储位置根据磁盘的VolumeSerialNumber生成。

如%ALLUSERSPROFILE%XXXXXXXXXXXXXX(其中X由运算生成)，存储的内容如下：

**7.Module Plugin**

Plugin模块为后门提供插件管理功能，包括插件的加载、卸载、添加、删除操作，管理功能完成后会通过调用Online的0x24项函数完成回调，向服务器返回操作结果。模块的辅助功能为其它插件提供注册表操作。

具体行为上：

1\. 创建线程调用config模块的第三个导出函数，遍历注册表项SOFTWAREMicrosoft<MachineID>。

2\. 使用RegNotifyChangeKeyValue函数监测插件注册表键值是否被更改，被更改后则解密并加载模块。

**8.Module DNS**

DNS模块的主要功能是使用DNS协议处理CC通信过程。DNS数据包有三种类型，分别代表上线，数据和结束。

**0类(上线)：**

**1类(数据)：**

**3类(结束)：**

此外，

1\. 该模块会调用GetAdaptersAddresses获取适配器的DNS，最多收集0x10个DNS。

2\. 在模块入口函数100编号对应的初始化过程中，模块会开启线程等待其他插件数据到来，当收到数据时将数据通过DNS发送到CC服务器。

**9.Module Online**

Online模块是本次攻击的网络通信管理模块。该模块会读取配置文件，收集系统信息，并且能够调用DNS，HTTP，SSL等模块通信，不过在代码中暂时只有前面所述的DNS模块。

收集并发送的系统信息包括注册表中的处理器信息，gethostbyname()获取的host信息，GlobalMemoryStatus()获取的内存信息，GetSystemTime()获取的时间信息，GetDiskFreeSpaceEx()获取的磁盘空间信息，EnumDisplaySettingsW()获取的显示器信息，GetSystemDefaultLCID()获取的系统语言信息，RtlGetVersion()获取的系统版本信息，GetSystemMetrics()获取的分辨率等信息，GetNetworkParams()获取的网络信息，GetNativeSystemInfo()获取的SYSTEM_INFO信息，LookupAccountSidW()获取的用户名信息等等。

0x16E1337函数首先读取配置文件，然后每隔1秒调用0x16E1995函数，0x16E1995函数还会调用0x16E1E9A函数，如果0x16E1E9A函数返回20000则函数逻辑彻底结束。

在0x16E1995函数中调用InternetCrackUrlA分解配置信息中的URL(www.noteped.com)并根据字符串前面的协议类型采取不同的连接方式，每个协议对应一个ID，同时也是协议插件的ID，目前取得的样本中使用的DNS协议对应ID为203。其它几个网络模块(TCP、HTTP、UDP、HTTPS、SSL)虽然在代码当中有所体现，但是在shellcode当中尚未主动运行。

此外，还调用了0x16E2D3F函数，试图调用Plugin模块设置注册表项SoftwareMicrosoftWindowsCurrentVersionInternet
SettingsSecureProtocols以修改IE浏览器的安全设置。

还会根据指定的参数使用HTTP-GETHTTPS-GETFTP来下载文件。

****

**0x05 修复建议**

NetSarang官方已经在以下几个软件的最新Builds版本中完成了安全修复。我们建议受影响的用户，及时更新到对应的修复版本：

**Xmanager Enterprise Build 1236**

**Xmanager Build 1049**

**Xshell Build 1326**

**Xftp Build 1222**

**Xlpd Build 1224**

****

**0x06 总结**

XShellGhost事件暗示着信息安全领域中又一个“潘多拉魔盒”已经被打开了，它表明了安全人员长期以来担心的基础软件、供应链被攻击后带来的大范围影响已经真实的发生了。

360CERT在实际分析跟踪中，除了看到XShellGhost中所使用的一系列精巧攻击技术外，更重要是看到了背后攻击组织在实施攻击道路上的决心。

在未来，安全人员担心的种种安全风险会不可避免的慢慢出现，但同时我们也在慢慢的看到，一方面基础软件厂商正在以积极的态度通过联合安全厂商等途径来加强和解决自身的产品安全，另一方面安全厂商之间也已经在威胁情报和安全数据等方面方面进行更为明确化，纵深化的整合。

****

**0x07 时间线**

2017-08-07 NetSarang官方发布安全更新

2017-08-14 360CERT发布《nssock2.dll恶意代码预警》

2017-08-16 360CERT发布《NetSarang 关于nssock2.dll恶意代码事件声明》

2017-09-07 360CERT完成《XshellGhost事件技术回顾报告》

****

**0x08 参考**

1.360天眼实验室：Xshell被植入后门代码事件分析报告（完整版）

<http://bobao.360.cn/learning/detail/4278.html>

2.360追日团队：Xshellghost技术分析——入侵感染供应链软件的大规模定向攻击

<http://bobao.360.cn/learning/detail/4280.html>

3.ShadowPad in corporate networks

<https://securelist.com/shadowpad-in-corporate-networks/81432/>

4.Security Exploit in July 18, 2017 Build

<https://www.netsarang.com/news/security_exploit_in_july_18_2017_build.html>

5.ShadowPad: popular server management software hit insupply chain attack

<https://cdn.securelist.com/files/2017/08/ShadowPad_technical_description_PDF.pdf>

6.nssock2.dll恶意代码预警|影响Xshell,Xmanager等多款产品

<https://cert.360.cn/warning/detail?id=07450801f090579304c01e9338cb0ffb>

7.NetSarang 关于nssock2.dll恶意代码事件声明

<https://cert.360.cn/warning/detail?id=38b82e99cf9538cd8cab0fe7d98f2c69>

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86860](/post/id/86860)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

