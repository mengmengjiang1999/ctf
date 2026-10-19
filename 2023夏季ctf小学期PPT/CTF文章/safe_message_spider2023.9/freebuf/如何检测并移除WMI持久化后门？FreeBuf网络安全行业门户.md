**![0_Qxa02RcVVLc4L79Q.jpg](https://image.3001.net/images/20181027/1540600275_5bd3b1d34c0b7.jpg!small)**

## 前言

 **Windows Management
Instrumentation（WMI）事件订阅，是一种常被攻击者利用来在端点上建立持久性的技术。因此，我决定花一些时间研究下[Empire](https://github.com/EmpireProject/Empire)的WMI模块，看看有没有可能检测并移除这些WMI持久化后门。此外，文中我还回顾了一些用于查看和移除WMI事件订阅的PowerShell命令。这些命令在实际测试当中都非常的有用，因此我也希望你们能记录它们。**

有关更多“Windows Management Instrumentation事件订阅”的内容，请参考MITRE ATT&CK Technique
[T1084](https://attack.mitre.org/wiki/Technique/T1084)。

攻击者可以使用WMI的功能订阅事件，并在事件发生时执行任意代码，从而在目标系统上建立一个持久化后门。

##  **WMI 介绍**

[WMI](https://docs.microsoft.com/en-us/windows/desktop/wmisdk/about-wmi)是微软基于Web的企业管理（WBEM）的实现版本，这是一项行业计划，旨在开发用于访问企业环境中管理信息的标准技术。WMI使用公共信息模型（CIM）行业标准来表示系统，应用程序，网络，设备和其他托管组件。

[事件过滤器](https://docs.microsoft.com/en-us/windows/desktop/wmisdk/creating-an-event-filter)（event filter[ ）](https://docs.microsoft.com/en-us/windows/desktop/wmisdk/creating-an-event-filter)是一个WMI类，用于描述WMI向事件使用者传递的事件。此外，事件过滤器还描述了WMI传递事件的条件。

##  **配置Sysmon日志记录**

我们可以将[Sysmon](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon)配置为记录WmiEventFilter，WmiEventConsumer和WmiEventConsumerToFilter活动，并启用WMI滥用检测。

![配置Sysmon日志记录](https://image.3001.net/images/20181027/1540600309_5bd3b1f53fbad.png!small)

Roberto Rodriguez
的（[@Cyb3rWard0g](https://twitter.com/Cyb3rWard0g)）[Sysmon](https://gist.github.com/Cyb3rWard0g/136481552d8845e52962534d1a4b8664)配置文件将捕获上述事件ID。

执行以下命令安装Sysmon，并应用配置文件。

    
    
    sysmon.exe -i -c .\config_file.xml

##  **建立持久化后门**

下面，我们使用Empire的Invoke-WMI模块，在受害者端点上创建一个永久的WMI订阅。

![建立持久化后门](https://image.3001.net/images/20181027/1540600338_5bd3b21295613.png!small)![建立持久化后门](https://image.3001.net/images/20181027/1540600338_5bd3b212d145e.png!small)![建立持久化后门](https://image.3001.net/images/20181027/1540600338_5bd3b212b14da.png!small)

## 检测

查看Sysmon日志，我们可以看到Empire模块：

> 注册了一个WMI事件过滤器；
>
> 注册了一个WMI事件使用者；
>
> 将事件使用者绑定到事件过滤器。

![查看Sysmon日志](https://image.3001.net/images/20181027/1540600362_5bd3b22a09fe5.png!small)

WMI事件过滤器为stager设置了相应执行条件，其中包括对系统正常运行时间的引用。

![为stager设置了相应执行条件](https://image.3001.net/images/20181027/1540600383_5bd3b23f8a453.png!small)

WMI事件使用者包含了以Base64编码形式的Empire stager，并使用了一个不易引起人们怀疑的名称Updater进行注册。

![进行注册](https://image.3001.net/images/20181027/1540600401_5bd3b251a2be4.png!small)

WMI事件使用者CommandLineEventConsumer.Name=\"Updater\"，被绑定到了事件过滤器__EventFilter.Name=\"Updater\"

![绑定到了事件过滤器](https://image.3001.net/images/20181027/1540600418_5bd3b2628521e.png!small)

现在，事件使用者被绑定到了事件过滤器。如果事件过滤条件为真，那么将会触发相应的事件使用者（stager）。

## 后门移除

最简单的办法就是，使用Autoruns从WMI数据库中删除条目。以管理员身份启动Autoruns，并选择WMI选项卡查看与WMI相关的持久性后门。

![9_HrM52HnYVK7UH3DQGYykGg.png](https://image.3001.net/images/20181027/1540600436_5bd3b27434b39.png!small)

![查看与WMI相关的持久性后门](https://image.3001.net/images/20181027/1540600454_5bd3b2867752a.png!small)

右键单击恶意WMI数据库条目，然后选择“Delete”删除即可。

或者，你也可以从命令行中删除WMI事件订阅。

在PowerShell中，我们使用Get-WMIObject命令来查看事件过滤器绑定的WMI事件过滤器，事件使用者和使用者过滤器。这里我要感谢Boe
Prox（[@proxb](https://twitter.com/proxb)）在[他的博客](https://learn-powershell.net/2013/08/14/powershell-and-events-permanent-wmi-event-subscriptions/)上详细解释了这些命令。

    
    
    # Reviewing WMI Subscriptions using Get-WMIObject
    # Event Filter
    Get-WMIObject -Namespace root\Subscription -Class __EventFilter -Filter “Name=’Updater’”
    
    # Event Consumer
    Get-WMIObject -Namespace root\Subscription -Class CommandLineEventConsumer -Filter “Name=’Updater’”
     
    # Binding
    Get-WMIObject -Namespace root\Subscription -Class __FilterToConsumerBinding -Filter “__Path LIKE ‘%Updater%’”

使用Remove-WMIObject命令，移除WMI持久性后门的所有组件。

    
    
    # Removing WMI Subscriptions using Remove-WMIObject
    # Event Filter
    Get-WMIObject -Namespace root\Subscription -Class __EventFilter -Filter “Name=’Updater’” | Remove-WmiObject -Verbose
    
    # Event Consumer
    Get-WMIObject -Namespace root\Subscription -Class CommandLineEventConsumer -Filter “Name=’Updater’” | Remove-WmiObject -Verbose
     
    # Binding
    Get-WMIObject -Namespace root\Subscription -Class __FilterToConsumerBinding -Filter “__Path LIKE ‘%Updater%’” | Remove-WmiObject -Verbose

![移除WMI持久性后门的所有组件](https://image.3001.net/images/20181027/1540600495_5bd3b2af4aa81.png!small)

完成后我们再次运行Autoruns，以验证持久化后门是否已被我们成功清除。

![验证持久化后门是否已被我们成功清除](https://image.3001.net/images/20181027/1540600510_5bd3b2be91861.png!small)

 ***参考来源：[medium](https://medium.com/threatpunter/detecting-removing-wmi-persistence-60ccbb7dff96) ，FB小编secist编译，转载请注明来自FreeBuf.COM**  

