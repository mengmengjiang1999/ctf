> DLL侧加载(DLL side-> loading)是一种常见的攻击方法，也就是我们常说的“白加黑”技术，它利用了Windows中处理动态链接库(DLL)的方式。Qakbot恶意软件的开发者通过使用Windows7系统在被感染的计算机上侧加载恶意负载，最终达到感染设备的效果。

近日，[安全](https://www.ipplus360.com/)研究人员ProxyLife发现，从今年7月11日开始Qakbot滥用Windows 7
Calculator应用程序进行DLL侧加载攻击。这种方法也被继续被用于恶意垃圾邮件活动。

Qakbot
恶意软件的开发者通过使用Windows7系统在被感染的计算机上侧加载恶意负载，最终达到感染设备的效果。![](https://image.3001.net/images/20220726/1658815569_62df84518f7ef024c6235.png!small)

##  ** **DLL侧**** ** **加**** ** **载**** ** **(**** ** **DLL side-loading****
** **)****

动态链接DLL是包含了若干个函数、类和资源的库文件。它可以被其他可执行文件(如.EXE文件和其它DLL文件)动态调用。使用DL的第一个优点是使多个应用程序,甚至是不同语言编写的应用程序可以共享一个DL文件,真正实现了“资源共享”;另一个优点是将DL文件作为应用程序一个独立的模块设计时,可以提高软件的开发速度,为软件升级提供了方便。

![](https://image.3001.net/images/20220726/1658815581_62df845d8f681a1340469.png!small)

而DLL侧加载(DLL side-loading)是一种常见的攻击方法，也就是我们常说的“白加黑”技术，它利用了Windows中处理动态链接库(DLL)的方式。DLL侧加载(DLL
side-loading)恶意软件通过欺骗一个合法的DLL，会在Windows的WinSxS目录中放置一个伪造的恶意DLL文件，以便操作系统加载它而不是合法文件。

##  ** **DLL侧加载攻击（DLL side-loading Attack）****

通常在Microsoft
Windows中，程序可以通过指定完整路径或使用清单等其他机制来定义在运行时加载哪些库或文件夹。程序清单可以包括DLL重定向、文件名或完整路径。因此，如果清单只引用了一个库文件名，它被视为弱引用并且容易受到DLL侧加载攻击。

DLL侧加载攻击主要是利用弱库引用和Windows默认的搜索顺序，在系统上放置一个伪装成合法DLL的恶意DLL文件，合法程序将自动加载该文件。

DLL侧加载通常会被勒索软件运营商使用，他们利用DLL侧加载来执行勒索软件有效载荷，以逃避安全产品的检测。

![](https://image.3001.net/images/20220726/1658815661_62df84ad51b5b9609f987.png!small)

##  ** **Qakbot病毒****

 ** **Qakbot病毒最开始是一种银行木马，受影响系统为微软Windows。****
Qakbot最早被发现于2009年，根据微软的分析，Qakbot被认为是由网络犯罪组织Gold Lagoon创建的。

Qakbot专门针对企业、银行、医疗、教育等机构进行强大的信息窃取功能，并持续监控用户的银行活动以欺诈大量钱财。

近年来，Qakbot发现了多个升级的变种，利用高级技术进行反检测与自我伪装，试图躲过了杀毒软件检测。后来Qakbot演变成了恶意软件投递器，勒索软件团伙在攻击的早期阶段使用它来投递攻击信标，造成了许多重大经济损失。

而且Qakbot交付的其它勒索软件包括RansomExx、Maze、ProLock和Egregor，最近，还发布了Black Basta勒索软件。

![](https://image.3001.net/images/20220726/1658815674_62df84baf0e2312fd90e9.png!small)

##  ** **Qakbot**** ** **新型感染链****

 ** **那么Qakbot病毒是如何运行**** ** **DLL侧**** ** **加**** ** **载**** ** **(**** **
**DLL side-loading**** ** **)？****

为了防御这种危险链接和攻击，ProxyLife和Cyble的研究人员记仔细研究和记录了 ** **新型的Qakbot**** ** **感染链。****

在最新的活动中使用的电子邮件带有一个HTML文件附件，该附件下载了一个有密码保护的ZIP压缩包，其中包含一个ISO文件。

打开ZIP文件的密码显示在HTML文件中，锁定存档的原因是为了躲避反病毒软件的检测。

ISO包含一个lnk文件，一个“calc.exe”(Windows计算器)的副本，以及两个DLL文件，即WindowsCodecs.dll和一个名7533.dll的有效负载。

 **
**![](https://image.3001.net/images/20220726/1658815685_62df84c51c61ab0e70edc.png!small)****

当用户挂载ISO文件时，它只显示lnk文件，该文件被伪装成有重要信息的PDF文件或使用Microsoft Edge浏览器打开的文件。

然而，在Windows中，快捷方式指向计算器应用程序。

单击快捷方式通过命令提示符执行Calc.exe最终就会触发感染。

 ** **Qakbot恶意软件的新型感染链的关键在于感染文件会被伪装成其它文件。**** 因为在加载时，Windows
7系统会自动搜索并尝试加载合法的WindowsCodecs DLL文件。

但是，Windows
7系统不会检查某些硬编码路径中的DLL，如果将DLL文件放置在与Calc.exe可执行文件相同的文件夹中，它将加载具有相同名称的任何DLL。

 ** **威胁者就是利用这个漏洞，创建他们自己的恶意WindowsCodecs.dll文件，然后启动其它[编号].dll文件。****

通过像Windows系统程序安装Qakbot后，一些安全软件在加载恶意软件时则无法检测出它，造成了这种威胁逃避了[安全](https://www.ipuu.net/Home)软件检测。

![](https://image.3001.net/images/20220726/1658815697_62df84d1696c11e70b1d8.png!small)

但是有一点，此DLL侧加载漏洞不适用于Windows 10 Calc.exe及以后版本， ** **这也是威胁者会针对Windows 7版本的原因****
。

Qakbot已经有十多年的历史了，虽然投放这种病毒的活动并不频繁，但是根据记载，Emotet僵尸网络曾经通过散布这种病毒来投放勒索软件的有效载荷。

> （部分消息链接：https://www.bleepingcomputer.com/news/security/qbot-phishing-uses-> windows-calculator-sideloading-to-infect-devices/）

