![](https://image.3001.net/images/20191014/1571049238_5da44f1608a3b.png!small)

##  介绍

 **近期，SafeBreach Labs的安全研究人员在惠普的HP Touchpoint
Analytics软件中发现了一个新型的安全漏洞，该漏洞将导致攻击者在目标设备上实现非法提权。该漏洞的漏洞编号为CVE-2019-6333，CVSS评级为中危漏洞。**

在这篇文章中，我们将跟大家介绍该漏洞将如何导致攻击者实现提权，以及如何利用SYSTEM权限在目标服务中加载任意未签名的DLL。

除此之外，我们还将演示如何利用该漏洞来实现一些潜在的恶意活动。

本文还提供了一份[PoC代码](https://github.com/QCute/WinRing0)，该PoC使用了第三方库来读取目标设备中的物理内存数据。

###  HP Touchpoint Analytics

HP Touchpoint Analytics这个服务很多惠普PC都会预装，该服务可以匿名收集目标硬件性能的诊断信息。

该服务能够以“NT AUTHORITY\SYSTEM”权限运行，这也给该服务提供了非常强大的权限支持。

###  Open Hardware Monitor

允许HP Touchpoint Analytics访问敏感数据和底层硬件（例如物理内存、MSR和SMBios）的，是一个名叫“[Open Hardware
Monitor](https://www.freebuf.com/wp-admin/1%E3%80%81https%3A/github.com/openhardwaremonitor/openhardwaremonitor)”的开源硬件监控库。[Open
Hardware Monitor](https://www.freebuf.com/wp-admin/1%E3%80%81https%3A/github.com/openhardwaremonitor/openhardwaremonitor)库提供了一个名叫“WinRing0”的已签名内核驱动，它可以在代码库运行时完成提取和安装。

本文中，我们将对HP Touchpoint Analytics和Open Hardware
Monitor组件中的漏洞进行分析，并给大家演示如何利用该漏洞来实现提权，并最终获取到SYSTEM权限。

##  漏洞分析

###  漏洞发现

在我们的初步研究过程中，我们之所以将目标锁定在了HP Touchpoint
Analytics服务上，是因为我们认为这种关键服务应该具有PC硬件的高级别访问权以及诱导实现提权的能力。

在HP Touchpoint Analytics服务启动后，它会以“NT
AUTHORITY\SYSTEM”权限执行TouchpointAnalyticsClientService.exe。

执行之后，该服务中的PerformanceMonitor 类会加载已签名的Open Hardware Monitor第三方库，从而启用以下三类检测-GPU、CPU和RAM：

![](https://image.3001.net/images/20191014/1571049265_5da44f319e23c.png!small)

接下来，该服务于会加载Open Hardware
Monitor第三方库。这个库能够从各种不同的硬件源收集信息，代码库完成加载后，我们可以在ProcMon中观察到下列活动：

![](https://image.3001.net/images/20191014/1571049269_5da44f35da2d5.png!small)

注意：上图中我们已经过滤掉了不相关的事件。

你可以看到，服务会尝试加载三个缺失的DLL文件，最终的加载路径为“ c:\python27”目录：

> atiadlxx.dll
>
> atiadlxy.dll
>
> Nvapi64.dll

###  DLL劫持漏洞演示

在我们的虚拟机中，c:\python27有一个ACL，允许任何认证用户向ALC中写入文件，这将使得提权变得非常简单，并允许常规用户向其中写入缺失的DLL文件，最终以“NT
AUTHORITY\SYSTEM”权限执行任意代码。

需要注意的是，管理员用户或进程必须设置目录ACL来允许访问非管理员用户的账号，然后将该目录路径添加至系统的PATH环境变量中。

为了测试这个提权漏洞，我们编译了一个未签名的DLL，它可以将下列文件名写入至txt文件：

> 1、执行目标文件的用户名；
>
> 2、DLL文件名；

![](https://image.3001.net/images/20191014/1571049286_5da44f4683e68.png!small)

![](https://image.3001.net/images/20191014/1571049290_5da44f4a569f0.png!small)

此时，我们就可以加载三个任意DLL，并以“NT AUTHORITY\SYSTEM”权限执行我们的代码。

##  漏洞根源分析

当OpenHardwareMonitor库加载之后，它会初始化一个GPU检测类，并尝试加载Nvidia和ATL DLL库以确保自己的API能够正常使用。

###  ATI逻辑

我们可以看到系统加载了ATI DLL库 - atiadlxx.dll和atiadlxy.dll，以确保自己的API能够正常使用。

![](https://image.3001.net/images/20191014/1571049300_5da44f54c7817.png!small)

![](https://image.3001.net/images/20191014/1571049304_5da44f584cf9d.png!small)

![](https://image.3001.net/images/20191014/1571049307_5da44f5b89c18.png!small)

###  Nvidia逻辑

我们可以看到，系统加载了Nvidia DLL库 - NVApi64.dll来确保自己的API能够正常使用。

![](https://image.3001.net/images/20191014/1571049315_5da44f635df83.png!small)

![](https://image.3001.net/images/20191014/1571049318_5da44f66b205b.png!small)

![](https://image.3001.net/images/20191014/1571049322_5da44f6a8ae8e.png!small)

我们可以看到，这就是导致漏洞出现的两个根本原因。

**未控制的搜索路径-缺少DLL加载的安全管理机制**

代码库会使用[DllImportAttribute](https://docs.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.dllimportattribute)来尝试加载上述未托管的DLL文件，问题就在于，它只会使用DLL文件名来调用，而不是通过DLL的绝对路径。因此，这里需要使用[DefaultDllImportSearchPathsAttribute](https://docs.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.defaultdllimportsearchpathsattribute)类来控制DLL加载文件的路径。

**缺少数字证书认证**

程序不会验证它所加载的DLL文件是否拥有数字签名，因此攻击者将能够加载任意未签名的DLL。

##  漏洞利用（物理内存读取/写入）

###  Open Hardware Monitor的已签名驱动程序

正如之前所说的，惠普的Touchpoint Analytics软件会使用Open Hardware
Monitor库来实现硬件诊断，而这个库使用了第三方签名驱动程序来执行某些底层操作。接下来，我们将演示如何利用该漏洞来获取“NT
AUTHORITY\SYSTEM”权限，并使用已签名驱动程序来从物理内存中读取数据。

###  PoC-读取物理内存

Open Hardware
Monitor库是完全开源的，这也就意味着它的驱动也是开源的。根据我们对驱动程序对外函数的分析，我们发现程序可以通过发送特质的IOCTL来读取/写入物理内存数据。我们使用的代码段所实现的指令能够向驱动程序发送一个IOCTL，并返回某个物理内存地址的内容数据。

![](https://image.3001.net/images/20191014/1571049343_5da44f7fdf80c.png!small)

![](https://image.3001.net/images/20191014/1571049347_5da44f83a5146.png!small)

接下来，我们将其编译成了DLL，并利用该漏洞以SYSTEM权限实现了加载。

###  从物理内存读取任意地址数据

比如说，我们选取地址0xC00F0，驱动程序将允许访问和读取的地址区间为0xC0000至0xFFFFF。

首先，我们使用内核模式调试器WinDbg来检测该物理地址的内容：

![](https://image.3001.net/images/20191014/1571049357_5da44f8d12ac7.png!small)

现在，我们可以利用该漏洞来加载未签名的DLL，并将输出结果写入至txt文件中：

![](https://image.3001.net/images/20191014/1571049361_5da44f911f660.png!small)

大家可以看到，在该漏洞的帮助下，我们能够轻松将任意物理内存地址的内容打印出来。

##  受影响产品

HP Touchpoint Analytics客户端：版本号低于v4.1.4.2827的所有版本。

##  参考资料

> 1、<https://github.com/openhardwaremonitor/openhardwaremonitor>
>
> 2、<https://support.hp.com/us-en/document/c06463166>

 *** 参考来源：[safebreach](https://safebreach.com/Post/HP-Touchpoint-Analytics-DLL-Search-Order-Hijacking-Potential-Abuses-CVE-2019-6333)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

