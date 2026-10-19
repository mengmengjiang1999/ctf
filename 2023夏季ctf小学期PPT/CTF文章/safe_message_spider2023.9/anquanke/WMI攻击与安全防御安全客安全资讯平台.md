# WMI攻击与安全防御

阅读量 **212333**

发布时间 : 2020-06-30 17:30:39

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

####

作者：夜影实验室（安全平台部）-Addddd

## 简介

WMI是一项Windows管理技术，其全称是Windows Management
Instrumentation，即Windows管理规范。大多数基于Windows的软件依赖于此服务。因此有些黑客会针对WMI进行攻击。本文介绍了 WMI
的攻击和安全防御方法，以供大家交流讨论。

每个WMI 对象都是代表着获取各种操作系统信息与进行相关操作的类实例，以ROOTCIMV2 作为默认的命名空间，CIM为数据库，并以WQL 查询语句用于查询
WMI 对象实例、类和命名空间。

## WMI 的主要交互方式

1、Powershell(Get-WmiObject、Set-WmiInstance、Invoke-WmiMethod等)

例如：Get-WmiObject-Namespace “ROOT” -Class __NAMESPACE

2、Wmic

例如：wmic/NAMESPACE:”rootCIMV2″ PATH Win32_OperatingSystem

## WMI事件

WMI事件会创建一个查询请求，请求中定义了我们需要执行的操作，一旦事件发生就会执行我们定义的操作，支持两种事件。

###  1、临时事件

要创建事件的进程处于活动状态，临时事件就会被激活（以当前权限运行）

例如：

![](https://p3.ssl.qhimg.com/t0118db6b7c47635eb9.png)

每打开一个新进程就会输出进程名称：

![](https://p3.ssl.qhimg.com/t01ac838104ab33c716.png)

###  2、持久事件

事件存储在CIM数据库中，并且会一直处于活动状态，直到从数据库中删除（以system权限运行，且重启保持不变）

## 持久事件与后门

利用持久事件来做后门(创建需要管理员权限)需要三个部分。

1、事件过滤器(Filter)：用来定义触发的条件，包括系统启动、特定程序执行、特定时间间隔等，存储在ROOTsubscription的实例__
EventFilter对象中，多数事件使用WQL WITHIN子句指定轮询间隔。

2、事件消费者(Consumer)：用来指定要执行的具体操作，包括执行命令(CommandLineEventConsumer)、运行脚本(ActiveScriptEventConsumer)、添加日志条目(NTEventLogEventConsumer)或者发送邮件(SMTPEventConsumer)。

3、绑定机制：将过滤器绑定到消费者(FilterToConsumerBinding类)

## 后门实例

不管是powershell,wmic还是mof文件，都由三个部分组成。

###  Powershell实现

![](https://p1.ssl.qhimg.com/t01ff59f4f8bc9b7dbe.png)

效果：每60秒运行一次powershell命令。

###  Wmic实现

![](https://p1.ssl.qhimg.com/t014447b7cb62993c58.png)

![](https://p0.ssl.qhimg.com/t01bebd5496d634a4b8.png)

效果：定时触发反弹

现如今，WMI攻击在很多APT行为中也经常被利用：

![](https://p4.ssl.qhimg.com/t0116e2949fccd1a4ad.png)

###  Mof实现

![](https://p0.ssl.qhimg.com/t01c1876578e4322201.png)

执行命令：

    
    
    Mofcomp xx.mof

效果：每30分钟触发反弹。

也可以直接执行vbs脚本文件：

    
    
    instance ofActiveScriptEventConsumer as $Cons
    {
    Name = “ASEC”;
    ScriptingEngine = “VBScript”;
    ScriptFileName = “c:asec.vbs”;
    };

## 安全防御

查看：

![](https://p0.ssl.qhimg.com/t0175b4449f942e9bc1.png)

删除：

![](https://p3.ssl.qhimg.com/t0129eed41bc38e5856.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **锦行科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/209210](/post/id/209210)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Windows](/tag/Windows)

 **+1** __3赞

 __收藏

![](https://p3.ssl.qhimg.com/t0178bf4a1b5818189f.png) 锦行科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

