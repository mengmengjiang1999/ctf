# 滥用COM注册表结构：劫持及加载技术

阅读量 **264979**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-09-10 11:25:55

 **x**

##### 译文声明

本文是翻译文章，文章来源：bohops.com

原文地址：<https://bohops.com/2018/08/18/abusing-the-com-registry-structure-part-2-loading-techniques-for-evasion-and-persistence/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01a613234619b38d11.jpg)

## 一、前言

攻击者可以通过各种方式利用COM劫持技术实现隐蔽加载及本地持久化，典型的例子包括CLSID遗留（子）键的引用、CLISID覆盖以及链接等。

许多程序及实用工具都可以调用COM注册表载荷，比如`Rundll32.exe`、`Xwizard.exe`、`Verclsid.exe`、`Mmc.exe`以及`Task
Scheduler`（任务计划程序）。从传统角度来看，任何程序只要解析不存在且/或未引用的COM类，都有可能会受到“非预期的”加载攻击的影响（比如劫持攻击）。

劫持COM服务器程序（比如MMC）可以衍生出许多有趣的用例。攻击者可以使用`-Embedding`参数以隐藏方式打开GUI程序。

可以考虑使用一些防御手段，比如采用强大的应用白名单策略、监控脱离正常父进程（如`svchost.exe`）的某些命令行用法（如使用`-Embedding`）及注册表键值（如`TreatAs`、`ScriptletUrl`）的创建操作等。

## 二、背景介绍

前阶段我写了篇[文章](https://bohops.com/2018/06/28/abusing-com-registry-structure-clsid-localserver32-inprocserver32/)，介绍了滥用COM注册表结构的一些技巧。在上一篇文章中，我们讨论了一些有趣的技术，比如如何寻找被遗弃的注册表键值、COM劫持、横向渗透、规避防御机制、绕过应用白名单以及持久化技术等。在这篇文章中，我们将更进一步，重点关注其他一些劫持方法以及可用于规避的加载技术，主要内容包括：

1、COM劫持技术；

2、用于规避及持久化的CLSID加载技术；

3、滥用COM服务端：MMC（Microsoft Management Console）使用案例；

4、防御方法。

## 三、COM劫持技术

为了在没有注册的情况下加载和执行COM载荷，攻击者必须以一定的方式去影响COM注册表结构，其中一种方法就是使用COM劫持（COM
Hijacking）技术。关于COM劫持这个概念[Mitre ATT&CK
Framework](https://attack.mitre.org/)已经给出了非常准确的定义：

> COM（Microsoft Component Object
> Model，Microsoft组件对象模型）是Windows上的一个系统，可以通过操作系统实现软件组件之间的交互。攻击者可以使用该系统，通过劫持COM引用和关系在合法软件中插入恶意代码，达成持久化目标。劫持COM对象需要修改Windows注册表，替换某个合法系统组件的引用，该操作可能导致该组件无法正常执行。当系统组件通过正常系统调用执行时，攻击者的代码就会被执行。攻击者可能会劫持频繁使用的对象，以维持一定程度的持久化驻留，但不大会破坏系统内的常见功能，避免系统出现不稳定状态导致攻击行为被发现。

**以上参考[COM劫持（T1122）](https://attack.mitre.org/wiki/Technique/T1122)，Mitre
ATT&CK**

接下来我们重点介绍常见的一些COM劫持技术。

###  利用被遗弃的COM键

`InprocServer32`以及`LocalServer32`（此外还包括`InprocServer`和`LocalServer`）的键值（key-values）是COM服务器（即`DLL`、`CPL`、`EXE`以及`OCX`程序）的引用点。当攻击者[发现](https://bohops.com/2018/06/28/abusing-com-registry-structure-clsid-localserver32-inprocserver32/)（存在漏洞的）一个引用点后，就可以在适当条件下（比如路径可写时）将载荷投放到已被遗弃的PE（Portable
Executable）引用路径上。如果被调用时（比如加载器或者程序引用了COM键时），由于调用方会尝试实例化CLSID入口点下的COM对象，因此PE载荷就会得到加载机会。前一篇[文章](https://bohops.com/2018/06/28/abusing-com-registry-structure-clsid-localserver32-inprocserver32/)中我介绍了`VMware
vmnetbridge.dll`这个例子，这里再简单回顾一下。

在这个例子中，VMware
Workstation卸载程序会遗留下一些COM键（处于未注册状态）。运行一个探测脚本后，我们可以发现`LocalServer32`键指向了之前已被移除的一个DLL路径。攻击者可以简单替换这个文件，劫持COM节点结构，如下图所示：

![](https://p2.ssl.qhimg.com/t01cf04e90b5bfab4c2.png)

图1. 被遗弃的COM键注册表路径

![](https://p1.ssl.qhimg.com/t019586a8bc035e4564.png)

图2. 被遗弃的COM键文件路径

![](https://p5.ssl.qhimg.com/t01a01f6103473ff170.png)

图3. 利用二进制引用替换法劫持被遗弃的键

###  覆盖COM键

覆盖COM对象可能是影响COM结构载荷的更为实用的方法。在`HKCU`注册表中添加正确的键值后，当引用目标COM对象时，`HKLM`中的键值就会被覆盖（并且“添加”到`HKCR`中）。在Casey
Smith（@subTee）给出的“SqibblyDoo”[样例](https://github.com/api0cradle/LOLBAS/blob/master/OSScripts/Payload/Slmgr_calc.sct)中，攻击者可以导入如下[注册表文件](https://github.com/api0cradle/LOLBAS/blob/master/OSScripts/Payload/Slmgr.reg)，使用另一个类标识（CLSID）成功劫持`scripting.dictionary`
COM程序标识（ProgID）：

![](https://p2.ssl.qhimg.com/t01756a0deda59df3ca.png)

图4. 包含`Scripting.Dictionary` COM覆盖键值的注册表文件

实际上，任何程序或者脚本只要尝试实例化`scripting.dictionary` COM程序或尝试加载被劫持的类标识时，都会调用攻击者布置的载荷。

### 链接COM键（使用`TreatAs`键）

影响COM载荷加载的另一种方法就是使用`TreatAs`键，该键实际上充当的是另一个（未注册的）CLSID键的快捷方式（或链接）。许多（原生的）Windows程序会引用不存在的CLSID注册表节点（注意：我们可以使用[SysInternals](https://docs.microsoft.com/en-us/sysinternals/)的ProcMon工具来识别这些悬空式引用)。根据具体的加载程序以及CLSID键，攻击者可以使用带有`TreatAs`引用的被劫持的CLSID节点结构，在CLSID键被引用时（如程序或者脚本启动时）达到加载目的。实际上攻击者可以通过以下两步完成这个任务：

1、劫持程序的未引用的COM CLSID路径或者带有`TreatAs`键的合法路径；

2、然后将带有`TreatAs`键的CLSID结构链接到另一个（被劫持的）COM CLSID键，后者包含恶意的加载器。

我们来看看Matt Nelson（@enigma0x3）和Casey
Smith（@subTee）给的一个例子。Matt和Casey曾做过名为[Windows Operating System
Archaeology](https://github.com/enigma0x3/windows-operating-system-archaeology)的专题演讲，其中提到了如下所示的注册表导入文件：

![](https://p2.ssl.qhimg.com/t0146698c453e1b42ef.png)

图5. `TreatAs`注册表文件

在图5中，攻击者创建了2个主要的CLSID节点（如果`HKLM`中存在这些CLSID值则会被覆盖掉）。一旦`{3734FF83-6764-44B7-A1B9-55F56183CDB0}`这个CLSID键（橙色高亮部分）被引用（比如程序加载或者其他调用/加载方法），`TreatAs`键就会充当一个超链接快捷键角色，“重定向”到`{00000001-0000-0000-0000-0000FEEDACDC}`这个CLSID键（绿色高亮部分），调用相应的载荷。当调用者/加载者调用时，大致的抽象逻辑可以分为以下几个步骤：

1、直接引用CLSID节点

[调用方] -> [CLSID入口点] -> [COM服务器] -> [载荷（比如`Scrobj.dll Scriptlet`）]

2、使用`TreatAs`链接引用CLSID节点

[调用方] -> [第一个CLSID入口点] -> [`TreatAs`键应用] -> [第二个CLSID入口点] -> [COM服务器] ->
[载荷（比如`Scrobj.dll Scriptlet`）]

注意：这里应该着重表扬下TrustedSec的Jason
Lang（@curi0usJack），他在识别和利用这些未引用的COM路径方面做了许多杰出的工作。Jason在BlackHat
2018的TrustedSec Purple
Team培训课程中详细介绍了这方面内容。此外，大家也可以参考Adam（@Hexacorn）的一篇[文章](http://www.hexacorn.com/blog/2018/08/17/beyond-good-ol-run-key-part-84/)，里面介绍了关于劫持TreatAs实例化过程的一些基本知识。

## 四、用于规避及持久化的CLSID加载技术

现在我们讨论下用于规避的COM加载技术。

###  引用加载器

如前文所述，如果脚本以及程序尝试实例化或者调用已被劫持COM节点的类以及/或者程序标识符时，就（很可能）会在执行的某个时刻加载其他载荷。覆盖或者链接恶意COM节点的操作通常需要考虑如下几个因素：

1、成功识别并劫持（缺失的）引用，并且不会对程序正常行为造成负面影响（比如造成程序崩溃）；

2、可以承担未知后果的影响，选择可能不会（或者不大会）影响系统或者用户体验的COM节点（比如，没有任何明显的线索表明程序或者主机的行为存在异常）；

3、此外，也可以尝试“修补”已劫持的路径，解决“程序执行流”（注意：这个概念很有意思，超出了本文的讨论范围）。

比如，当我们用Casey Smith的“SquibblyDoo”载荷劫持`scripting.dictionary`
COM节点然后运行`WinRm`时，我们可以看到当`scripting.dictionary`被实例化时会出现一些非预期的结果：

![](https://p4.ssl.qhimg.com/t01c946424d35ba99f2.png)

图6. 使用`WinRM`加载被劫持的COM节点

**注意：**
并不是所有被劫持的路径都会导致（可见的）程序性故障。有许多无缝的、可被劫持的路径不会对程序执行流造成负面影响，其中某些路径还可以作为隐蔽的持久化技术来使用。

###  Rundll32

如前一篇[文章](https://bohops.com/2018/06/28/abusing-com-registry-structure-clsid-localserver32-inprocserver32/)所述，通过CLSID键（或者PROGID）调用载荷的一种方法就是在`rundll32`中使用`-sta`（single
threaded apartment）参数，这种方法并没有那么广为人知，具体命令为：

    
    
    rundll32.exe -sta {CLSID}
    

或者

    
    
    rundll32.exe -sta ProgID
    

`-sta`参数并没有详细的说明文档，但该参数的确可用，并且有被滥用的潜在风险。如下图所示，我们使用这种方法来实现了前文描述的COM节点直接加载以及通过链接方式（`TreatAs`）加载：

![](https://p3.ssl.qhimg.com/t01bcfd23e0dc6a20cb.png)

图7. COM节点的直接加载及链接（`TreatAs`）加载

我们也可以使用`rundll32`配合ProgID（Program Identifier，程序标识符）来调用我们劫持的COM节点：

![](https://p2.ssl.qhimg.com/t012b98bf53cdc6898f.png)

图8. Rundll.exe：`-sta`与ProgID配合执行

在使用`AutoRuns`实现本地持久化方面，`rundll32`命令无法规避过滤器的筛查，但可以使用隐藏的注册表载荷来迷惑人们的双眼：

![](https://p3.ssl.qhimg.com/t01a2dbc5ccf2046c34.png)

图9. Rundll32 -sta登录启动项

###  利用计划任务实现持久化

几年以前，Matt
Nelson（@enigma0x3）写了一篇[文章](https://enigma0x3.net/2016/05/25/userland-persistence-with-scheduled-tasks-and-com-handler-hijacking/)，介绍了利用计划任务和COM处理程序劫持实现用户模式下的本地持久化技术。Matt在文章中介绍了如何寻找计划任务中`Action`设置为`Custom
Handler`的可疑项。查看计划任务对应的XML文件后，我们可以看到这个`Action`实际上是与“COM处理程序”对应的一个CLSID值。劫持这个CLSID结构后，载荷的利用就非常简单。当计划任务运行时（比如系统登录时），恶意载荷就会被运行。

![](https://p5.ssl.qhimg.com/t01c5283b189e15e063.png)

图10. 计划任务配置文件（来源：Matt Nelson的[文章](https://enigma0x3.net/2016/05/25/userland-persistence-with-scheduled-tasks-and-com-handler-hijacking/)）

###  利用Verclsid调用载荷

根据微软的[说明文档](https://docs.microsoft.com/en-us/security-updates/securitybulletins/2006/ms06-015)，`verclsid.exe`可以“在Windows资源管理器实例化一个COM对象前验证该对象”，这一点非常有趣。Nick
Tyrer（@NickTyrer）在Github上演示了`Verclsid`的一种用法，如下所示：

    
    
    verclsid.exe /S /C {CLSID}
    

使用合适的CLSID运行上述命令后，就可以调用攻击者设定的载荷，如下所示：

![](https://p3.ssl.qhimg.com/t0153cdb2efb506f058.png)

图11. 利用CLSID执行Verclsid

###  利用Xwizard调用载荷

根据Nick
Tyrer的描述，`Xwizard`是加载CLSID节点的另一种方式。@harr0ey提供了一种[运行方式](https://twitter.com/harr0ey/status/980786352374665216)，不会弹出错误信息：

    
    
    xwizard.exe RunWizard /taero /u {CLSID}
    

**注意：**
已经有钓鱼恶意软件攻击活动中使用了`Verclsid.exe`这个工具，大家可参考这篇[文章](https://www.redcanary.com/blog/verclsid-exe-threat-detection/)（来自Red Canary）了解详细信息。

## 五、滥用COM服务器

Windows系统中有一些内置程序能够在特定服务（如远程主机管理）的上下文环境中充当COM/DCOM服务器。经过正确的调用和实例化后，当使用`-Embedding`参数调用DCOM/COM应用时，就可以利用这些应用的公开属性及方法（这一点需要进一步验证）。然而这里存在一个“有趣的”副作用，那就是（许多）具有GUI/可见窗口组件的启用COM的应用（如`mmc.exe`、`mspaint.exe`、`winword.exe`、`iexplore.exe`等）会以服务器模式来运行，但却不呈现GUI组件。我们来看些具体例子：

MMC（Microsoft Management
Console）工具的功能和可扩展性非常强大，因此可能是Windows系统管理员最喜欢的得力助手。MMC允许（高权限）用户添加多个“snap-ins”（管理单元），在本地或者远程管理Windows系统，然而这个应用也会暴露一些攻击面，可能被攻击者滥用。去年年初时候，Matt
Nelson（@enigma0x3）发现MMC对外公开了一种方法，通过该方法攻击者可以借助DCOM协议辅助执行远程命令。Matt在一篇[文章](https://enigma0x3.net/2017/01/05/lateral-movement-using-the-mmc20-application-com-object/)中详细介绍了这种技术。

虽然这种方法不像常见的远程命令执行/横向渗透技术那样令人兴奋，但MMC可以用来调用CLSID载荷，实现规避加载以及通过`Run`注册表键值实现本地驻留。下面我们可以开始配置MMC控制台文件，了解具体利用方法。

###  MMC：CLSID Web地址链接

首先，我们需要创建一个CLSID链接，将我们的配置信息保存成控制台文件（`.msc`文件）。我们可以打开MMC，通过“Add/Remove Snap-In”窗口来设置载荷。为了简单起见，我们选择“the Link to Web Address”（指向Web地址的链接）这个snap-in来打开向导，在“Path or URL”文本框中输入被劫持的/引用的CLSID键，如下图所示：

![](https://p2.ssl.qhimg.com/t01869b1de8a036cd31.png)

图12. 添加MMC Snap-In：Web地址链接

接下来，为这个Snap-In设置一个名称，然后选择“Finish”，如下图所示：

![](https://p5.ssl.qhimg.com/t01e2714b52caa4961a.png)

图13. 添加MMC Snap-In：设置名称

经过这些操作后，“Console Root”节点下就会创建我们设置的“test”项。只要选择“test”菜单项，就会调用相应的CLSID链接。

![](https://p5.ssl.qhimg.com/t01c04a276cd0b0f611.png)

图14. MMC Snap-In：在选中时启动CLSID载荷

###  MMC：MSC文件加载

创建并启用我们的载荷配置后，我们可以将控制台保存为`test.msc`。确保相应的Snap-In标签（如`test`）处于选中状态以保持当前控制台状态。如果没有选中，我们的载荷就无法在控制台文件打开时被调用。

为了进一步确认这个条件，我们可以使用文本编辑器打开这个控制台文件，验证配置信息以及CLSID指针的值是否正确：

![](https://p5.ssl.qhimg.com/t0158cea20613c0f35c.png)

图15. MMC XML配置文件

保存好控制台文件后，我们可以通过命令行启动msc文件，通过`-Embedding`标志（注意：大小写敏感）以隐蔽的方式调用CLSID载荷：

    
    
    mmc.exe -Embedding c:pathtotest.msc
    

![](https://p4.ssl.qhimg.com/t01a2677b3c79f09583.png)

图16. 利用`-Embedding`参数实现MMC隐蔽启动

###  利用MMC实现本地持久化

在利用`AutoRuns`实现本地持久化方面，由于`mmc.exe`是经过微软签名的二进制程序，因此可以规避默认的过滤器，如下图所示：

![](https://p3.ssl.qhimg.com/t01a94ad59f78b7ca17.png)

图17. MMC AutoRuns Run注册表键值：过滤器处理结果

移除过滤器后，我们可以看到对应的启动项：

![](https://p1.ssl.qhimg.com/t01b1176ab351e86c7f.png)

图18. MMC AutoRuns Run注册表键值：不使用过滤器的处理结果

在登录时，由于我们劫持了注册表键以及引用，所以系统会执行我们的载荷：

![](https://p5.ssl.qhimg.com/t01af56caf913ede07d.png)

图19. MMC Run注册表键值：登录时执行

综合考虑后，`mmc.exe`可能不是最实用的利用对象，然而如果其他COM程序以类似方式来调用，可能会具备更高的实用性。

## 六、防御策略

1、在完美的场景中，经过正确配置的应用程序白名单（AWL）解决方案与代码完整性保护机制结合起来后可能会阻止（许多）这类载荷的执行；

2、可以监控某些有趣的COM应用的使用情况以及`Run`注册表键值。`Embedding`参数可能是比较有趣的一个特征，但正常的DCOM远程管理和本地实例化过程中可能也会使用该参数。对COM应用的正常调用/实例化行为应该源自于Service
Host（`svchost.exe`）进程，来自其他父进程的调用可能都值得怀疑；

3、可以监控进程创建事件，比如感兴趣命令行操作以及CLSID调用程序的使用；

4、评估新创建的注册表键值，特别要注意包含`TreatAs`以及/或者`ScriptletURL`键值的新增内容。

## 七、他人研究成果

1、James Forshaw（@tiraniddo）在“[COM In 60
Seconds](https://www.youtube.com/watch?v=dfMuzAZRGm4)”中详细介绍了COM的每一步工作流程（现在我仍在重复观看这个视频）。如果您不熟悉James的研究成果，我强烈推荐大家尽快去学习一下；

2、PhilipTsukerman（@PhilipTsukerman）在“[New lateral movement techniques abuse
DCOM technology](https://www.cybereason.com/blog/dcom-lateral-movement-techniques)”这篇文章中为我们介绍了COM技术的入门知识，也很好概述了DCOM横向渗透技术；

3、Rob Maslen（@rbmaslen）在“[COM and the
PowerThief](https://www.youtube.com/watch?v=xmbjRP5W-yk&feature=youtu.be)”视频中介绍了COM与Internet
Explorer交互的背景知识，此外我们还可以参考Rob开发的[PowerThIEf](https://github.com/nettitude/Invoke-PowerThIEf)工具来滥用正在运行的IE实例。

本文翻译自bohops.com [原文链接](https://bohops.com/2018/08/18/abusing-the-com-registry-structure-part-2-loading-techniques-for-evasion-and-persistence/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/159211](/post/id/159211)

安全客 - 有思想的安全新媒体

本文转载自: [bohops.com](https://bohops.com/2018/08/18/abusing-the-com-registry-structure-part-2-loading-techniques-for-evasion-and-persistence/)

如若转载,请注明出处： <https://bohops.com/2018/08/18/abusing-the-com-registry-structure-part-2-loading-techniques-for-evasion-and-persistence/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [注册表](/tag/注册表)
  * [COM](/tag/COM)
  * [劫持加载](/tag/劫持加载)

 **+1** __4赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

