# CVE-2019-3969：Comodo沙箱逃逸提权漏洞分析

阅读量 **230119**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-07-26 14:30:13

 **x**

##### 译文声明

本文是翻译文章，文章原作者 tenable-techblog，文章来源：medium.com

原文地址：<https://medium.com/tenable-techblog/comodo-from-sandbox-to-system-cve-2019-3969-b6a34cc85e67>

译文仅供参考，具体内容表达以及含义原文为准。

## 0x00 前言

AV（反病毒软件）一直以来都是漏洞挖掘的绝佳目标，这是因为其中涉及到巨大的攻击面、复杂的解析过程以及以高权限运行的各种组件。几个月之前，我决定分析最新版的Comodo
Antivirus
v12.0.0.6810，最终我找到了一些有趣的信息，但这里我想跟大家分享其中一个沙箱逃逸问题，可以将权限提升至`SYSTEM`级别。在本文中，我们会滥用各种COM对象，绕过二进制签名检查，劫持关键服务。下面开始进入主题。

![](https://p5.ssl.qhimg.com/t01af3b66dd61fde244.gif)

## 0x01 Comodo沙箱机制

首先我想介绍一下Comodo的沙箱技术，Comodo称之为“Containment”，在本文中我将交替使用“Containment”以及“沙箱”这两个词。这种沙箱技术可以限制不可信应用（[RTATC](https://containment.comodo.com/how-it-works/?source=post_page---------------------------)）在类沙箱环境中运行，同时OS中还能运行其他进程。这种技术涉及到用户模式hook以及内核模式驱动，可以阻止对主机上文件或注册表的任何修改操作。该环境中可以读取文件及注册表，但一旦执行写操作，文件I/O就会被转移到沙箱文件系统，后续读取操作将与沙箱文件系统交互，使调用方误认为自己在与正常的文件系统交互。

Comodo通过过滤器驱动`Cmdguard.sys`来实现该功能。该驱动会使用[`FltRegisterFilter`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/fltkernel/nf-fltkernel-fltregisterfilter?source=post_page---------------------------)
API注册一个[`_FLT_REGISTRATION`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/fltkernel/ns-fltkernel-_flt_registration?source=post_page---------------------------)结构，该结构包含与来自用户模式应用的各种[IRP](https://docs.microsoft.com/en-us/windows-hardware/drivers/gettingstarted/i-o-request-packets?source=post_page---------------------------)（比如[文件访问](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-create?source=post_page---------------------------)、[文件写入](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-write?source=post_page---------------------------)等）对应的回调例程，并且可以执行对应的拦截/处理操作。此外，ALPC（用于各种OS组件的一种Microsoft
IPC）也会被沙箱化处理，Comodo会将ALPC连接转移到“沙箱化”的`svchost.exe`实例，避免通过RPC/ALPC实现沙箱逃逸。这种containment技术工作原理如下图所示：

![](https://p4.ssl.qhimg.com/t015bca9f6747138539.png)

图1. Comodo Containment技术逆向分析图

`Cmdguard.sys`不仅可以过滤文件/注册表I/O，也会使用[`PsSetCreateProcessNotifyRoutine`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/ntddk/nf-ntddk-pssetcreateprocessnotifyroutine?source=post_page---------------------------)注册[`CREATE_PROCESS_NOTIFY_ROUTINE`](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/ntddk/nc-ntddk-pcreate_process_notify_routine?source=post_page---------------------------)，跟踪正在运行的进程。当进程运行时，Comodo会将containment状态、信任等级以及其他相关属性跟踪并保存到存储在内核中的一个进程列表。`Cmdguard.sys`会对外提供“filter
ports”，以便用户模式下的Comodo组件通信。Comodo会向`cmdAuthPort`
filterport发送特定消息来设置containment状态，随后内核模式驱动会在该消息指定的目标进程上设置“containment”标志。

在创建沙箱化进程后，`Guard64.dll`（几乎每个运行的进程中都会注入该dll）负责从用户模式中发送这些containment消息。例如，`Guard64.dll`会hook
`Explorer.exe`的`CreateProcessInternalW`
API，这样当用户执行不可信进程时，就会向`Cmdguard.sys`过滤器端口发送一个“containment”消息。现在当不可信进程启动时，驱动程序会将打上“contained”标记，阻止文件、注册表I/O操作。此外，`Cmdguard.sys`会将`Guard64.dll`注入沙箱化进程中，执行用户模式下的hook操作。

![](https://p2.ssl.qhimg.com/t0108189260a48f62b8.png)

图2. `Cmdguard.sys` dll注入流程

`Guard64.dll`在用户模式下设置的hook如下图所示：

![](https://p5.ssl.qhimg.com/t018caafbe179d47184.png)

图4. `Guard64.dll`用户模式hook

这些hook有个相同的功能，就是避免沙箱化的进程连接非沙箱化进程创建的安全对象。为了完成该任务，Comodo会将一个`!comodo_6`标记附加到沙箱化进程创建或打开的每个对象名，避免对象名与系统上已有的安全对象发生名字冲突（或者关联）。

实际上，这也是RPC/ALPC沙箱隔离的工作原理。RPC/ALPC流量会被转移到沙箱化的`Svchost.exe`实例（参考上图），这是因为`!comodo_6`会附加到沙箱化进程尝试连接的端口名，而沙箱化的`Svchost.exe`实例也会创建附加`!comodo_6`的端口名。如下图所示，我们可以看到沙箱化的MSI安装程序尝试运行，发起RPC调用后最终会创建沙箱化的`MSIexec.exe`服务组件（父进程为`cmdvirth.exe`）。

![](https://p0.ssl.qhimg.com/t01c5b6f021a92cfdbc.png)

图5. 沙箱化的ALPC生成沙箱化的MSIExec实例

绕过这些用户模式hook并不难，但想通过这种方式实现沙箱逃逸并不容易。如果想简单patch与ALPC相关的hook，通过WMI实现逃逸显然不可能，因为这些位置同样会被`CmdAgent.exe`监控并阻止。了解关于Comodo沙箱环境的基本知识后，下面我们来研究下如何实现沙箱逃逸及权限提升。

## 0x02 创建Comodo COM客户端

Comodo在各种AV组件之间使用了许多IPC机制，包括：过滤端口、共享内存、LPC以及COM。这里我们将重点关注COM。如果大家想了解COM，可以参考[这篇文章](https://docs.microsoft.com/en-us/windows/desktop/com/the-component-object-model?source=post_page---------------------------)。简而言之，COM的全称为“Component
Object
Model”，是微软提供的一种技术，允许不同模块创建由COM服务端定义的各种对象并与之交互。COM服务端可以本地部署（在当前进程中加载的一个COM服务端dll）或者远程部署，可以通过ALPC进行交互。在利用形式上，远程部署可能是更为有趣的应用场景。

我们发现Comodo可以从低权限进程（如`explorer.exe`，通过Context Shell
Handler（当用户右键点击时出现的菜单）或者`Cis.exe`（Comodo客户端GUI））发起扫描任务。这些扫描任务可以通过调用`CAVWP.exe`中的例程来发起，而该程序以`SYSTEM`权限执行。

如果我们能澄清如何按照Comodo的方式连接到这个服务，那么可能我们会找到一种新的攻击面，发现除“扫描”之外更多有趣的函数。我们需要通过COM实现与`CAVWP.exe`的远程交互，因为从注册表中可知，`CAVWP.exe`是一个进程外的COM服务端：

![](https://p3.ssl.qhimg.com/t017c8d3d051b848d1e.png)

图5. `CAVWP.exe` COM服务端

接下来分析`Explorer.exe`以及Comodo
COM客户端如何通过COM远程触发这些“扫描”动作。前面提到过，Comodo在`Explorer.exe`的Shell Context
Menu中注册了一个handler（`CavShell.dll`），因此低权限客户端`Explorer.exe`可以发起扫描动作。

![](https://p3.ssl.qhimg.com/t0179e954a0c56cd6a4.png)

图6. `Explorer.exe`中的Comodo Context Menu Handler

逆向分析这个shell扩展接口后，我发现其中Comodo实现了一个“扫描”客户端COM例程。理解这个函数可以帮助我们了解如何构造自己的COM客户端。

![](https://p3.ssl.qhimg.com/t01fc17257abc4dc09e.png)

图7. `Cavshell.dll`（Context Menu Handler）的“Scan File”例程

该代码流程中对`CoGetClassObject`的调用比较有趣。`CoGetClassObject`会返回指向某个接口的一个指针，而该接口对应与CLSID关联的某个对象。在注册表中查找后，我们发现这个CLSID对应“Cis
Gate Class”，并且很快我们意识到`CAVavWp.exe`与这个类没有任何关系，该类对应的实际COM服务端为`CmdAgent.exe`。

![](https://p2.ssl.qhimg.com/t01334a0f9cd1b10b5b.png)

图8. 根据CLSID（CLSID_CisGate）发现COM服务端为`Cmdagent.exe`。

经过研究后我们发现，`CmdAgent`充当的是低权限COM客户端与`CavWp`之间的代理角色，`CavWp`会代表我们通过`CisGate`接口向`CmdAgent`发起扫描请求。这里我们的主要目标是理解并设置这些绑定关系，这样才能进一步利用更多的攻击面。

逆向分析客户端（以及部分`CmdAgent`逻辑）后，我们成功迁移了COM代码，澄清了正确的方法偏移地址，并且重新设计我们的代码，以模拟这些COM对象的操作。

![](https://p4.ssl.qhimg.com/t01e13d06afba23da56.png)

图9. 模拟“伪造的”Comodo COM客户端

## 0x03 代码签名问题

然而，这段代码无法运行成功，`CisClassFactory`的`CreateInstance`会调用失败，返回`E_ACCESSDENIED`。这一点比较奇怪，因为我们的进程权限与`Explorer.exe`以及`Cis.exe`一样，而后者却能成功调用，原因究竟是什么？

在调试器中调试`CmdAgent.exe`，可以看到程序会收到我们执行的`CreateInstance`调用，并且进入一个自定义的`E_ACCESS_DENIED`消息分支。

![](https://p0.ssl.qhimg.com/t01d4a13919de561925.png)

图10. `Cmdagent.exe`阻止未签名进程通过COM进行交互

这意味着这个`ACCESS_DENIED`并不是由Windows发出，而是Comodo自己做出的决定。

这个决策实际上是基于签名检查，签名检查会验证请求实例的COM客户端是可信的、“经过签名的”程序。观察`Cmdagent.exe`中的签名检查例程，可以看到文件需要由Comodo或者微软签名，这一点也能够理解，因为这样只有`Explorer.exe`或者`Cis.exe`这两个客户端才能调用`CmdAgent.exe`中的COM方法。

![](https://p4.ssl.qhimg.com/t01e779fcb23363a12d.png)

图11. `Cmdagent.exe`签名校验类（`HardMicrosoftSigner`/`HardComodoSigner`）

其实这个签名校验过程很容易被绕过，大家能不能发现问题所在？这里`CmdAgent.exe`会解析COM客户端的进程名，以便后续从磁盘上执行签名检查过程：

![](https://p4.ssl.qhimg.com/t01389b41d7340cdeb8.png)

图12. `Cmdagent.exe`查找COM客户端的完整映像名

大家可能知道一点，[GetModuleFileNameEx](https://docs.microsoft.com/en-us/windows/desktop/api/psapi/nf-psapi-getmodulefilenameexa?source=post_page---------------------------)实际上只会查询目标进程的[PEB-](https://docs.microsoft.com/en-us/windows/desktop/api/winternl/ns-winternl-_peb?source=post_page---------------------------)>Ldr->`InMemoryOrderModuleList`，以便获取完整映像名。然而这个路径我们可以控制，因此我们可以在自己的进程中轻松修改这个特征。

还有另一种解决办法，我们可以将代码注入可信的微软程序或者Comodo程序，从中发起COM请求。然而Comodo会阻止dll注入操作，因此为了绕过这一点，我们需要对可信的Comodo程序执行Process
Hollowing操作。

这个过程比操作我们自己的PEB还麻烦，但能给我们带来更大的优势。通过这种方法，`Cmdguard.sys`驱动就不会注入`Guard64.dll`，因此也不会在我们的进程中设置各种hook。如果目标进程“不可信”，那么`Cmdguard.sys`就会调用`InjectDll`例程，如下图所示。如果我们对`C:\Program
Files\COMODO\COMODO Internet
Security\CmdVirth.exe`执行Hollowing操作，那么就可以绕过`IsProcessUntrusted`检查，因为驱动会根据可执行文件路径来判断该程序为可信程序，因此会成功放行。

![](https://p5.ssl.qhimg.com/t013b68a29a7b5a7414.png)

图13. 如果目标进程“可信”，`Cmdguard.sys`就不会注入`Guard64.dll`

现在我们添加了一个Process Hollowing例程，用来处理`C:\Program Files\COMODO\COMODO Internet
Security\CmdVirth.exe`实例（该程序由Comodo签名），用我们的代码替换其中的可执行代码。现在注入的代码会执行我们前面设置的COM处理逻辑，并且能够绕过签名检查，不存在任何hook。我们重新运行这段代码，成功通过低权限进程，在设置沙箱标记的情况下触发扫描任务！

![](https://p1.ssl.qhimg.com/t0198f7bd0faa05b13e.png)

图14. 从自定义的未签名的COM客户端成功触发扫描操作

## 0x04 寻找可滥用的COM接口

可以从沙箱进程中执行扫描操作后，我们现在可以寻找`CmdAgent`中是否存在更多有趣的COM接口。观察我们提取到的60多个`CisGate`接口后，我们只找到了1个值得关注的对象，但这些接口都正确使用了[`CoImpersonateClient`](https://docs.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-coimpersonateclient?source=post_page---------------------------)，成功阻止了我想要找到的逻辑错误。当然还有许多方法可以研究，因为我们其实能提取出更多的接口。前面提到过，我们可以使用`CreateInstance`在`CmdAgent.exe`中创建一个CisGate对象。因此我们有可能创建更多的对象，研究更多的方法，让我们回到CmdAgent。

`ICisClassFactory`->`CreateInstance`函数会创建所需的对象，调用`CisGate`->`QueryInterface`返回请求的接口指针。这里提一下，[QueryInterface](https://docs.microsoft.com/en-us/windows/desktop/api/unknwn/nf-unknwn-iunknown-queryinterface\(refiid_void)?source=post_page—————————————-)是`IUnknown`中的一个核心函数，是所有COM类的基类。简而言之，该函数会将[
_riid_](https://docs.microsoft.com/en-us/windows/desktop/learnwin32/asking-an-object-for-an-interface?source=post_page---------------------------)（接口标识符）解析成对象接口，这样客户端（比如我们开发的客户端）就可以调用接口上的方法。了解这一点后，我们可以逆向分析`CmdAgent.exe`的`QueryInterface`函数，观察其中支持哪些接口。

![](https://p0.ssl.qhimg.com/t010e457f86f093fe9e.png)

图15. `CmdAgent.exe`支持的接口

我们列出了`QueryInterface`支持的`supported_interfaces`，根据注册表中发现的信息来命名每个GUID。这里`IID_ICisFacade`这个riid用来返回`CisGate`对象，另一个比较有趣的目标是`IID_IServiceProvider`。查看[IID_IServiceProvider](https://msdn.microsoft.com/en-us/ie/cc678965\(v=vs.94)?source=post_page—————————————-)官方文档，貌似该接口可以给我们提供很多信息。在`Cis.exe`（Comodo
GUI Client）中搜索`IID_IServiceProvider`
GUID，发现Comodo的确在使用该接口。逆向分析代码逻辑后，我们可以澄清自己如何使用该接口、Comodo想使用的服务以及想执行的操作。

## 0x05 注册表读取

`Cis.exe`会使用`IServiceProvider`来执行[QueryService](https://docs.microsoft.com/en-us/windows/desktop/winauto/using-queryservice-to-expose-a-native-object-model-interface-for-an-iaccessible-object?source=post_page---------------------------)操作，用来获取Comodo定义的`SvcRegistryAccess`对象，部分代码片段如下图所示：

![](https://p3.ssl.qhimg.com/t01f5f7ab847ce8b1a7.png)

图16. `Cis.exe`获取`ISvcRegistryAccess`

这表明`Cis.exe`会从`CmdAgent.exe`获取`SvcRegistryAccess`对象，然后调用该对象中的方法读取注册表键值并返回数据。能让具备`SYSTEM`权限的进程帮我们读取注册表，这听起来已经是比较不错的一个攻击路径，但我感觉开发者不会只把这个`SvcRegistryAccess`当成一个“只读”类。让我们回到`CmdAgent`，观察这个COM类的实现机制。

在`CmdAgent`中，我们可以看到被远程调用的`ISvcRegistryAccess`方法会直接读取注册表键值，将数据返回给客户端，整个过程不涉及到`CoImpersinateClient`。这意味着我们可以使用`SYSTEM`权限读取注册表键值，因为这也是`CmdAgent`所具备的权限。

![](https://p4.ssl.qhimg.com/t01bc3af6c895c2a13d.png)

图17. `CmdAgent.exe` `ISvcRegistryAccess`以`SYSTEM`权限读取注册表，没有使用模拟机制

## 0x06 注册表写入

现在来看一下这个COM对象是否支持注册表写入。进一步研究`vtable`后，我们看到其中某个方法会调用`RegSetValueExW`。

![](https://p4.ssl.qhimg.com/t01d055d87ab34c5cf7.png)

图18. `CmdAgent.exe`会调用更加有趣的一些方法（设置注册表键值）

![](https://p2.ssl.qhimg.com/t01da9305fdf885bf59.png)

图19. `CmdAgent.exe` `ISvcRegistryAccess`方法以`SYSTEM`权限设置注册表键值

显然，如果我们调用该方法，就能以`SYSTEM`权限执行注册表写入操作，因为我没有在代码中找到对任何身份模拟API的调用。我们修改了自己的COM客户端代码，获取`IServiceProvider`，解析`ISvcRegistryAccess`，然后调用这个“注册表写入”方法。如果我们观察通过调用`GetRegInterface`来获取`regInterface`的过程，就可以看到`CmdAgent.exe`实际上只创建了一个只读的注册表键值句柄，因此尝试调用这个“写注册表”方法就会出现`ACCESS_DENIED`问题。幸运的是，我发现了`ISvcRegKey`
vtable中由另一个方法，通过传递一些额外参数，可以将我们的注册表句柄变成“可写”状态。

在原有代码中调用该方法，同时传入适当参数，这样就能获取“可写的”`ISvcRegistryAccess`。

![](https://p0.ssl.qhimg.com/t018ec87f7a295e93a0.png)

图20. 修改COM客户端以获取可写的注册表接口

整合在一起，我们最终得到了如下代码，能够以`SYSTEM`权限执行注册表写入操作。

![](https://p0.ssl.qhimg.com/t0174ae1408fe6b5217.png)

图21. 最终的COM客户端代码

![](https://p1.ssl.qhimg.com/t012b8ea2ff4b6922ea.png)

图22. 成功覆盖高权限注册表键值

## 0x07 提升至SYSTEM权限

稍微总结下，我们运行沙箱化应用，对Comodo签名的程序执行Process
Hollowing操作（以便绕过CmdAgent的签名校验机制），然后通过该程序运行我们开发的COM代码，从我们“沙箱化的”进程中以`SYSTEM`权限执行注册表写入操作。如果想通过这种方法实现权限提升，典型的方法就是劫持已有的服务，这里我们可以选择`CmdAgent.exe`。通过替换注册表`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\CmdAgent`对应的`ImagePath`值，我们就可以将`CmdAgent`服务替换成我们自己的程序，然后以`SYSTEM`权限运行。

![](https://p0.ssl.qhimg.com/t0146c53c6ffdbfbf6b.png)

图23. `CmdAgent.exe`服务

然而，如果我们想要第一时间获得`SYSTEM`权限，我们需要重启`CmdAgent`服务（不然就要等待下次重启）。幸运的是，我们有办法能够完成该任务，我找到了让`CmdAgent`崩溃的方法，这样服务就会自动重启，最终启动我们的程序。想让`CmdAgent`崩溃非常简单，该进程会对外提供结构化数据的一个[Section
Object](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/section-objects-and-views?source=post_page---------------------------)（内存区对象），而`EVERYONE`具备该对象的写入权限：

![](https://p3.ssl.qhimg.com/t0127251121d4704b02.png)

图24. `CmdAgent.exe` `Section Object`公开可写的对象数据（`SharedMemoryDictionary`）

`CmdAgent`将这个缓冲区当成一个`SharedMemoryDictionary`，这是共享内存中对外公开的一个类对象。我们可以在对象成员中写入错误的大小值，这样当`CmdAgent`尝试读取这个`SharedMemoryDictionary`时（`CmdAgent`经常会执行该操作），就会出现越界读取问题，最终导致`CmdAgent`崩溃。当服务恢复时，就会执行我们设置的程序，最终让我们提升至`SYSTEM`权限。

![](https://p4.ssl.qhimg.com/t01910ee0560fc0fb80.png)

图25. 成功提升至`SYSTEM`权限

大家可以观看[此处视频](https://youtu.be/rHKRiSy8FoA)了解攻击过程，点击[此处](https://github.com/tenable/poc/tree/master/Comodo/Comodo%20Antivirus?source=post_page---------------------------)下载源代码。

本文翻译自medium.com [原文链接](https://medium.com/tenable-techblog/comodo-from-sandbox-to-system-cve-2019-3969-b6a34cc85e67)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/182763](/post/id/182763)

安全客 - 有思想的安全新媒体

本文转载自: [medium.com](https://medium.com/tenable-techblog/comodo-from-sandbox-to-system-cve-2019-3969-b6a34cc85e67)

如若转载,请注明出处： <https://medium.com/tenable-techblog/comodo-from-sandbox-to-system-cve-2019-3969-b6a34cc85e67>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [沙箱](/tag/沙箱)
  * [本地提权](/tag/本地提权)
  * [Comodo](/tag/Comodo)

 **+1** __7赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

