近日，安全狗海青实验室在研究powershell攻击运用到主机实战场景时，对powershell在主机中是否存在安全问题进行了一次较为全面的分析，并介绍了powershell从灰色工具逐步演变成为攻击利用工具的过程、攻击者的利用手段，最后分享了如何针对powershell攻击做效防御。

从0到1的突破是极为困难的；从1到N却容易得多，powershell的攻击也是如此。从0到1的突破困难，但从1复制到N个1却容易得多，即，先从无到有，而后powershell攻击方式已比比皆是，成为臭名昭著的攻击利用工具。

##  ** **一、powershell攻击工具的演变****

Powershell 从诞生至今，其命令行程序内置在每一个受支持的Windows版本中 (Windows
7或更高版本)，它提供了高超的灵活性和管理系统的能力。如下图所示：

![](https://image.3001.net/images/20210108/1610108777_5ff84f6919cc4445875cf.png!small)

（Powershell查看主机系统信息）

![](https://image.3001.net/images/20210108/1610108787_5ff84f7370ec1e5b592aa.png!small)

（Powershell查看主机进程信息）

![](https://image.3001.net/images/20210108/1610108800_5ff84f8028f8e17770b66.png!small)

（Powershell操纵注册表）

也因为这种能力，powershell逐渐成为了一个流行且效果拔群的攻击工具，并被大多数攻击者“滥用”在各种主机攻击场景中。如：常见的内网渗透、APT攻击、后门技术，甚至包括目前流行的勒索病毒软件中。

##  ** **二、P**** ** **owershell不止有“exe”****

Powershell是 Windows 系统中的一个核心组件 （不可移除），它存在于 System.Management.Automation.dll
动态链接库文件 (DLL) 里，并能附加到不同的运行空间中进行有效的PowerShell 实例化（PowerShell.exe 和
PowerShell_ISE.exe）。通俗来说，powershell能实现的功能比cmd更为强大，并且具备脚本编写的能力（ps1类型脚本文件）。

![](https://image.3001.net/images/20210108/1610108810_5ff84f8a47332fa7580ab.png!small)

（使用ps1脚本调用计算器）

![](https://image.3001.net/images/20210108/1610108819_5ff84f9307cde668cad83.png!small)

（编写后门ps1脚本）

##  ** **三、PowerShell 执行策略并不能提供真正的安全****

默认情况下，主机上powershell执行策略是不允许执行ps类型脚本的。这意味着在默认情况下，powershell禁用了所有的脚本文件执行。如下图所示：

![](https://image.3001.net/images/20210108/1610108829_5ff84f9d7818bad602b56.png!small)

（powershell禁用脚本执行）

尽管如此，攻击者仍可以通过手动输入执行命令或是绕过执行策略的方式执行攻击命令。首先，先要了解powershell的六种执行策略：

Unrestricted

|

权限最高，可以不受限制执行任意脚本  
  
---|---  
  
Restricted

|

默认策略，不允许任意脚本的执行  
  
AllSigned

|

所有脚本必须经过签名运行  
  
RemoteSigned

|

本地脚本无限制，但是对来自网络的脚本必须经过签名  
  
 ** **Bypass****

|

 ** **没有任何限制和提示（常用手段）****  
  
Undefined

|

没有设置脚本的策略  
  
（powershell的六种执行策略）

攻击者通常会用到以下方式来达到绕过执行策略来执行ps1文件的目的。如下图所示：

![](https://image.3001.net/images/20210108/1610108847_5ff84faf43940cdc4a1eb.png!small)

（远程执行ps1文件）

![](https://image.3001.net/images/20210108/1610108861_5ff84fbdb673f78cfa770.png!small)

（使用特殊标记执行本地ps1文件）

![](https://image.3001.net/images/20210108/1610108870_5ff84fc64cf9795d3c385.png!small)

（使用管道符执行本地ps1文件）

![](https://image.3001.net/images/20210108/1610108880_5ff84fd017d799f419d9a.png!small)

（调用参数替换执行ps1文件）

![](https://image.3001.net/images/20210108/1610108888_5ff84fd85edbc4b88b417.png!small)

（修改注册表项执行ps1文件）

在实际测试过程中，powershell的执行策略并不能给主机带来安全，攻击者能用以上任意方式绕过执行策略，达到在主机上运行恶意脚本的目的。

##  ** **四、P**** ** **owershell实质上是一个攻击平台！****

随着powershell攻击平台的逐渐兴起，攻击者通常将powershell作为“后期渗透利用”工具。以至于在实际攻击场景中，攻击者只要能获取主机系统访问权限，就很有可能会运行恶意的powershell代码。一旦攻击者获得了主机系统访问权限，并借助powershell攻击工具，那么主机上所有的操作系统标准工具和实用程序都能被攻击者利用。

一般来说，在攻击利用工具领域里，极少有工具能真正运用在整个攻击中。Powershell也是如此。PowerShell通常被运用在整个攻击手段的“后渗透”环节中，其常用的攻击手段如下表所示：

WMI

|

计算机管理  
  
---|---  
  
HTA脚本

|

HTML应用程序  
  
CHM

|

编译的HTML帮助文件  
  
Java

|

JAR文件  
  
编码混淆

|

bash64 / ASCII / HEX /AES /BXOR  
  
其它脚本类型

|

VBS / WSH / BAT / CMD  
  
Microsoft Office宏

|

VBA  
  
（powershell常用攻击手段）

以下分别展示常见的WMI、HTA和编码混淆类型的攻击手段。

###  ** **1、WMI****

攻击者使用WMI配合powershell做到内网隐藏后门技术。编写door.ps1文件脚本，并将脚本放在内网客户端上，攻击者在服务端上就能查看到客户端的主机信息。具体代码如下：

![](https://image.3001.net/images/20210108/1610109006_5ff8504eedadeac37fa3f.png!small)

（远程连入服务端后门）

攻击者在服务端上执行命令即可查看到客户端上的状态信息。如下图所示：

![](https://image.3001.net/images/20210108/1610109018_5ff8505a89e9189a46632.png!small)

（远程查看客户端主机信息）

###  ** **2、HTA****

利用HTA脚本也是攻击者在内网主机渗透中的一贯做法。HTA文件类型脚本本质上是HTML的应用程序文件，也就是安全检测规则里常见白名单内容，被誉为“披着羊皮的狼”。攻击者可以使用以下代码来实现添加系统用户test。

![](https://image.3001.net/images/20210108/1610109028_5ff85064099e641ab2ba2.png!small)

（添加系统test用户的hta脚本）

将以上HTA脚本保存在主机中并执行，系统中将会增加一个test用户。如下图所示：

![](https://image.3001.net/images/20210108/1610109037_5ff8506d393b813e0276e.png!small)

（创建test用户成功）

###  ** **3、编码混淆****

在powershell实战场景中攻击者经常会用到powershell攻击命令混淆编码，能有效隐匿攻击者的操作、绕过杀毒软件。以下是经过ASCII编码后的“ipconfig”命令。如下图所示：

![](https://image.3001.net/images/20210108/1610109046_5ff850767617aa2aa62e3.png!small)

（ASCII编码后的命令）

既然powershell的功能已经强大到“攻其详、退可隐”的地步，那把powershell直接从主机系统中禁用不就行了吗？（如下图所示）然而这样的做法通常是无效的，因为去掉powershell
2.0勾选并重启电脑后主机系统仍能正常使用powershell（v5.0版本）功能。

![](https://image.3001.net/images/20210108/1610109065_5ff85089a23dd96e97b29.png!small)

（禁用powershell功能）

事实上，攻击者可在cmd中借助攻击工具做到无powershell执行powershell命令，并对主机系统发起攻击。如下图所示：

![](https://image.3001.net/images/20210108/1610109074_5ff85092d34101c0710db.png!small)

（无powershell执行powershell命令）

##  ** **五、如何有效预防powershell攻击****

powershell之所以被“滥用”，就是因为它具有功能强大且运用方式灵活的特点。随着利用powershell进行攻击的趋势愈演愈烈，掌握有效的防御和检测powershell攻击的方法就很有必要。用户可以通过以下操作来防范powershell攻击：

### 启用powershell模块日志记录

在本地组策略编辑器中找到powershell模块，并启用打开模块日志记录（如下图所示）。启用powershell日志记录功能需要powershell
v3版本及更高版本的支持。

  

![](https://image.3001.net/images/20210108/1610109116_5ff850bc213fc07591fc9.png!small)

### 启用脚本块日志记录

在本地组策略编辑器中找到powershell模块，并启用打开脚本块日志记录（如下图所示）。脚本块日志在事件日志中提供了能记录混淆powershell执行命令的能力。大多数攻击者通常会进行命令混淆处理。

![](https://image.3001.net/images/20210108/1610109124_5ff850c404a3cd179cec3.png!small)

### 安装有效的powershell入侵防护软件

这是最有效也是最方便快捷的防护方法，目前大部杀毒安全软件都具备了一定程度的powershell入侵防护功能。虽然不是很成熟，但足以抵御住部分的powershell攻击。

##  ** **六、**** ** **结语****

目前，powershell在Windows主机中仍然存在很大的安全隐患，尤其当powershell配合其它攻击工具时，更是花样百出、防不胜防。因此，研究powershell攻击手段以及powershell安全对策仍是主机安全领域中关键性内容。

攻击不停于眼前，防守不止于现在。无攻则不促防，无防则不有攻，攻防对抗，应是对立，相存紧依，不可分离。

