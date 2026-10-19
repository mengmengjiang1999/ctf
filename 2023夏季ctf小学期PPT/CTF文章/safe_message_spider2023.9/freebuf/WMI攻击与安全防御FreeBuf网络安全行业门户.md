### 作者：夜影实验室（安全平台部）-Addddd  

# 简介

  

WMI是一项Windows管理技术，其全称是Windows Management
Instrumentation，即Windows管理规范。大多数基于Windows的软件依赖于此服务。因此有些黑客会针对WMI进行攻击。本文介绍了 WMI
的攻击和安全防御方法，以供大家交流讨论。

每个WMI 对象都是代表着获取各种操作系统信息与进行相关操作的类实例，以ROOT\CIMV2 作为默认的命名空间，CIM为数据库，并以WQL
查询语句用于查询 WMI 对象实例、类和命名空间。

## WMI 的主要交互方式

1、Powershell(Get-WmiObject、Set-WmiInstance、Invoke-WmiMethod等)

例如：Get-WmiObject-Namespace “ROOT” -Class __NAMESPACE

2、Wmic

例如：wmic/NAMESPACE:"\\\root\CIMV2" PATH Win32_OperatingSystem

## WMI事件

WMI事件会创建一个查询请求，请求中定义了我们需要执行的操作，一旦事件发生就会执行我们定义的操作，支持两种事件。

1、临时事件：要创建事件的进程处于活动状态，临时事件就会被激活（以当前权限运行）

例如：

![1.png](https://image.3001.net/images/20200624/1592997173_5ef33535a5412.png)  

每打开一个新进程就会输出进程名称：

![2.png](https://image.3001.net/images/20200624/1592997193_5ef335497c2a8.png)  

2、持久事件：事件存储在CIM数据库中，并且会一直处于活动状态，直到从数据库中删除（以system权限运行，且重启保持不变）

## 持久事件与后门

利用持久事件来做后门(创建需要管理员权限)需要三个部分。

1、事件过滤器(Filter)：用来定义触发的条件，包括系统启动、特定程序执行、特定时间间隔等，存储在ROOT\subscription的实例__
EventFilter对象中，多数事件使用WQL WITHIN子句指定轮询间隔。

2、事件消费者(Consumer)：用来指定要执行的具体操作，包括执行命令(CommandLineEventConsumer)、运行脚本(ActiveScriptEventConsumer)、添加日志条目(NTEventLogEventConsumer)或者发送邮件(SMTPEventConsumer)。

3、绑定机制：将过滤器绑定到消费者(FilterToConsumerBinding类)

# 后门实例

不管是powershell,wmic还是mof文件，都由三个部分组成。  

## Powershell实现

![3.png](https://image.3001.net/images/20200624/1592997229_5ef3356d94289.png)  

效果：每60秒运行一次powershell命令。

## Wmic实现

![4.1.png](https://image.3001.net/images/20200624/1592997249_5ef3358154e42.png)![5.png](https://image.3001.net/images/20200624/1592997254_5ef33586e08b1.png)

效果：定时触发反弹

  

现如今，WMI攻击在很多APT行为中也经常被利用：

![6.png](https://image.3001.net/images/20200624/1592997295_5ef335af5fc1f.png)

## Mof实现

![7.png](https://image.3001.net/images/20200624/1592997361_5ef335f1b451a.png)

  

执行命令：

Mofcomp xx.mof

效果：每30分钟触发反弹。

也可以直接执行vbs脚本文件：

instance ofActiveScriptEventConsumer as $Cons

{

Name = "ASEC";

ScriptingEngine = "VBScript";

ScriptFileName = "c:\\\asec.vbs";

};

# 安全防御

查看：

#List EventFilters

Get-WMIObject-Namespace root\Subscription -Class __EventFilter

#List EventConsumers

Get-WMIObject-Namespace root\Subscription -Class __EventConsumer

#List EventBindings

Get-WMIObject-Namespace root\Subscription -Class __FilterToConsumerBinding

删除：

#Filter

Get-WMIObject-Namespace root\Subscription -Class __EventFilter
-Filter"Name='BotFilter82'" | Remove-WmiObject -Verbose

#Consumer

Get-WMIObject-Namespace root\Subscription -Class CommandLineEventConsumer
-Filter"Name='BotConsumer23'" | Remove-WmiObject -Verbose

#Binding

Get-WMIObject-Namespace root\Subscription -Class __FilterToConsumerBinding
-Filter"__Path LIKE '%BotFilter82%'" | Remove-WmiObject -Verbose

