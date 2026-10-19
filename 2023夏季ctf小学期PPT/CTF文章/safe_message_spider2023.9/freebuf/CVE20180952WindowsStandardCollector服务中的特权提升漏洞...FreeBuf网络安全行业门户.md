***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**如果你对寻找bug的过程不感兴趣，或者是“太长不看”那种，那么[ATREDIS-2018-0004](https://github.com/atredispartners/advisories/blob/master/ATREDIS-2018-0004.md)是个不错的选择，而且[这里还有一个概念性证明（PoC）](https://github.com/atredispartners/CVE-2018-0952-SystemCollector)。**

[Process Monitor](https://docs.microsoft.com/en-us/sysinternals/downloads/procmon)已经是我研究和开发时最喜欢的一个工具。在开发安全工具时，我频繁地用它来监视工具如何与Windows交互，以及它们是如何被检测到的。今年早些时候，我在Visual
Studio中调试一段代码并用Procmon监视时注意到一些有趣的行为。一般来说，我会为Visual
Studio设置过滤以减少干扰。但在设置过滤之前，我注意到一个SYSTEM进程写入用户拥有的目录：

![1.png](https://image.3001.net/images/20180916/1537085637_5b9e10c568945.png!small)

StandardCollector.Service.exe 写入用户临时文件夹

当拥有权限的服务写入用户拥有的资源时，可能会产生符号链接（symlink）攻击向量的可能性，为了确定如何直接影响服务的行为，我通过查看服务加载的库开始研究Standard
Collector服务：

![2.png](https://image.3001.net/images/20180916/1537085669_5b9e10e57ee6e.png!small)

Visual Studio DLLs被StandardCollector.Service.exe加载

库的路径显示Standard Collector服务是Visual
Studio诊断工具的一部分，在浏览了相关文件夹的一些库和可执行文件之后，我发现有几个二进制文件是用.NET写的，其中包括一个叫VSDiagnostics.exe的独立命令行工具，下图为控制台的输出：

![3.png](https://image.3001.net/images/20180916/1537085705_5b9e1109b3a8e.png!small)

VSDiagnostics命令行工具的输出

将VSDiagnostics加载到dnSpy中会发现很多关于该工具以及它如何与Standard
Collector服务服务交互的内容。首先，获取IStandardCollectorService的实例，并使用会话配置创建ICollectionSession：

![4.png](https://image.3001.net/images/20180916/1537085748_5b9e11347e799.png!small)

初始配置诊断收集会话的步骤

接下来，用CLSID和DLL名称将代理添加到ICollectionSession，这也是一个比较有趣的用户控制行为。它也让我记得以前的研究就是利用了这种DLL加载行为。此时，看起来Visual
Studio Standard Collector服务与Windows 10中包含的诊断中心Standard
Collector服务非常相似甚至相同。我开始使用OleViewDotNet查询服务来查询其支持的接口：

![5.png](https://image.3001.net/images/20180916/1537085815_5b9e117772e9d.png!small)

OleViewDotNet中的Windows诊断中心Standard Collector服务

查看IStandardCollectorService的proxy
definition会显示其他熟悉的接口，特别是VSDiagnostics源中的ICollectionSession接口：

![6.png](https://image.3001.net/images/20180916/1537085852_5b9e119c547b1.png!small)

OleViewDotNet中的ICollectionSession接口定义

记下接口ID（“IID”）后，我返回到.NET操作库来比较IID，然而发现它们不同：

![7.png](https://image.3001.net/images/20180916/1537085884_5b9e11bc00b27.png!small)

具有不同IID的Visual Studio ICollectionSession定义

深入研究.NET代码，我发现这些Visual Studio特定的接口是通过代理DLL加载的：

![8.png](https://image.3001.net/images/20180916/1537085943_5b9e11f7007d4.png!small)

VSDiagnostics.exe函数加载DLL

对DiagnosticsHub.StandardCollector.Proxy.dll中的ManualRegisterInterfaces函数的预览显示了一个迭代IID数组的简单循环。包含在IID数组中的是属于ICollectionSession的数组：

![9.png](https://image.3001.net/images/20180916/1537085985_5b9e122131b8e.png!small)

ManualRegisterInterfaces DLL的函数

![10.png](https://image.3001.net/images/20180916/1537086046_5b9e125ee4e1d.png!small)

要注册的IID数组中的Visual Studio ICollectionSession IID

在更好地理解Visual Studio
Collector服务之后，我想看看是否可以重用相同的.NET代码来控制WindowsCollector服务。为了与正确的服务进行交互，我需要用正确的Windows
Collector服务CLSID和IID替换Visual Studio
CLSID和IID。接下来，我使用修改后的代码构建一个客户端，该客户端只是创建并启动了Collector服务的诊断会话：

![11.png](https://image.3001.net/images/20180916/1537086091_5b9e128b8a816.png!small)

用于与Collector服务交互的客户端的代码片段

启动Procmon并运行客户端会在指定的C:\Temp临时目录中创建多个文件和文件夹。在Procmon中分析这些事件表明，初始目录创建是在客户端模拟的情况下执行的：

![12.png](https://image.3001.net/images/20180916/1537086150_5b9e12c6b3511.png!small)

虽然初始目录是在模拟客户端时创建的，但后续文件和文件夹是在没有模拟的情况下创建的：

![13.png](https://image.3001.net/images/20180916/1537086158_5b9e12ceeddf1.png!small)

在深入了解其他文件操作之后，有几个比较突出。下图是Stand Collector服务执行的各种文件操作的注释细分：

![14.png](https://image.3001.net/images/20180916/1537086199_5b9e12f7aaef2.png!small)

最有趣的行为是在创建诊断报告期间发生的文件复制操作。下图显示了相应的调用堆栈和此行为的事件：

![15.png](https://image.3001.net/images/20180916/1537086244_5b9e1324f2493.png!small)

现在确定了用户影响的行为，我构建了一个可能实现的任意文件创建漏洞利用计划：

> 1.服务调用CloseFile后立即获取合并的ETL文件（{GUID} .1.m.etl）的操作锁定。
>
> 2.查找报告子文件夹并将其转换为挂载点于C:\Windows\System32。
>
> 3.用恶意DLL替换{GUID} .1.m.etl的内容。
>
> 4.释放op-lock以允许通过挂载点复制ETL文件。
>
> 5.使用复制的ETL作为代理DLL启动新的会话，从而触发提权的代码执行。

为了编写漏洞利用程序，我通过利用James Forshaw的NtApiDotNet C＃库创建op-lock和挂载点来扩展客户端。下图显示了用于获取op-lock的代码片段以及相应的Procmon输出，说明了循环和op-lock获取：

![01.png](https://image.3001.net/images/20180916/1537086358_5b9e1396135e9.png!small)![02.png](https://image.3001.net/images/20180916/1537086372_5b9e13a4cff92.png!small)

获取文件上的op-lock实质上会停止CopyFile，且允许覆盖内容，并控制CopyFile何时发生。接下来，该漏洞会查找Report文件夹并扫描它以查找需要转换为挂载点的随机命名的子目录。成功创建挂载点后，.etl的内容将被恶意DLL替换。最后，关闭.etl文件并释放op-lock，允许CopyFile操作继续。 此步骤的代码段和Procmon输出如下图所示：

![03.png](https://image.3001.net/images/20180916/1537086421_5b9e13d54c358.png!small)![arbitrary_file_write.png](https://image.3001.net/images/20180916/1537086534_5b9e1446bf21a.png!small)

有几种技术可以通过任意文件写入来提升权限，但是对于此漏洞，我选择使用collector服务的代理DLL加载功能来使其与单个服务隔离。你会注意到在上图中，我没有使用挂载点+符号链接技巧将文件重命名为.dll，因为DLL可以任何扩展名被加载。出于此漏洞的目的，DLL只需要在System32文件夹中，以便Collector服务加载它。下图显示了漏洞利用程序的成功执行以及相应的Procmon输出：

![05.png](https://image.3001.net/images/20180916/1537086972_5b9e15fc2349e.png!small)

上面的截图显示漏洞是以用户“Admin”身份运行的，所以这里有一个GIF，显示它是作为“bob”运行的，这是一个低权限的用户帐户：

![1.gif](https://image.3001.net/images/20180916/1537087319_5b9e1757afeaf.gif!small)

你也可以试试SystemCollector的[PoC](https://github.com/atredispartners/CVE-2018-0952-SystemCollector)，NtApiDotNet库同时也是一个Powershell模块，可以让事情变得更简单。

 ***参考来源：[atredis](https://www.atredis.com/blog/cve-2018-0952-privilege-escalation-vulnerability-in-windows-standard-collector-service)，FB小编Covfefe编译，转载请注明来自FreeBuf.COM**

