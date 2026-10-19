**译者：知道创宇404实验室翻译组**  
**原文链接：<https://www.welivesecurity.com/2020/09/02/kryptocibule-multitasking-multicurrency-cryptostealer/>**

## 前言

ESET研究人员发现了迄今未记录的恶意软件家族，我们将其命名为KryptoCibule。对加密货币而言，这种恶意软件具有三重威胁。它利用受害者的资源来挖掘硬币，试图通过替换剪贴板中的钱包地址来劫持交易，并泄漏与加密货币相关的文件，同时部署多种技术来避免检测。KryptoCibule在其通信基础架构中广泛使用了Tor网络和BitTorrent协议。

该恶意软件用C编写，还使用了一些合法软件。有些东西，例如Tor和Transmission
torrent客户端，与安装程序捆绑在一起。其他的则在运行时下载，包括Apache httpd和Buru
SFTP服务器。图1显示了各种组件及其相互作用的概述。
![](https://images.seebug.org/content/images/2020/09/4e7dfb67-8348-421a-8623-6127f89a1df1.png-w331s)

首次执行恶意软件时，主机被分配一个唯一的标识符，格式为`{adjective}-{noun}`，其中`{adjective}`和`{noun}`是从两个硬编码列表中随机抽取的单词，它们提供了超过一千万个唯一的组合。然后，该标识符用于标识与C＆C服务器通信的主机。

除了与加密相关的组件外，KryptoCibule还具有RAT功能。它支持的命令包括EXEC（可以执行任意命令）和SHELL（可以从C＆C下载PowerShell脚本）。然后，此脚本加载使用[Pupy](https://github.com/n1nj4sec/pupy
"Pupy")生成的后门。

KryptoCibule这个名称源自捷克语和斯洛伐克语中的“crypto””和“onion”两个词。

## 时间线

我们发现了该恶意软件的多个版本，这使我们能够追溯到2018年12月的演变。图2显示了KryptoCibule随着时间的变化。
![](https://images.seebug.org/content/images/2020/09/b9b1494d-eeb5-4060-b5c1-3db74592fceb.png-w331s)

## 目标

根据ESET遥测技术（如图3所示），该恶意软件似乎主要针对捷克（捷克共和国）和斯洛伐克的用户。这反映了被感染的站点所在的用户群。
![](https://images.seebug.org/content/images/2020/09/26ddbb7b-c507-4380-8b83-fe57fabce702.png-w331s)
如图3所示，在遥测数据中，超过85％的检测结果位于捷克和斯洛伐克。

几乎所有的恶意种子都可以在uloz.to上找到。图4显示了一个在Czechia和Slovakia
受欢迎的文件共享站点。在下一部分中，我们将解释如何使用这些洪流传播KryptoCibule。
![](https://images.seebug.org/content/images/2020/09/ce10d980-e2c2-4097-9f21-1c4d2067d888.png-w331s)
图4为uloz.to上的恶意种子之一。

如下面的“防检测和防分析技术”部分所述，KryptoCibule专门检查ESET、Avast和AVG端点安全产品。ESET的总部位于斯洛伐克，而其他两家为Avast拥有。

## 危害

KryptoCibule利用BitTorrent协议传播给新的受害者，并下载和更新其他工具。

KryptoCibule通过ZIP文件进行恶意传播，其内容伪装成破解或盗版软件和游戏的安装程序。尽管可能包括其他文件，如图5所示，但所有KryptoCibule安装程序档案共有五个文件。packed.001是恶意软件，而packed.002是预期软件的安装程序。两者都使用Setup.exe中包含的密钥进行XOR加密。

当执行Setup.exe时，它将对恶意软件和预期的安装程序文件进行解码。然后，它在后台启动恶意软件，并在前端和中间启动预期的安装程序，不会给受害者留下任何迹象。
![](https://images.seebug.org/content/images/2020/09/ffc90016-b0d5-439d-a657-c3d6906c832b.png-w331s)
图5. Dead.Cells.Incl.All.DLC归档文件的内容，仅显示了最小的通用KryptoCibule安装程序文件集。

#### 附加软件和更新

BitTorrent协议还用于下载对恶意软件和其他软件的更新。

KryptoCibule安装了传输守护程序
Torrent客户端，并通过其端口9091上具有传输远程功能的RPC接口发出命令来对其进行管理。RPC接口使用硬编码的凭证superman：krypton。

要安装其他软件以供恶意软件使用，例如SFTP服务器，启动器组件会向`%C&C%/softwareinfo?title=<software
name>`发出HTTP GET请求，并接收一个JSON响应，其中包含要下载的Torrent
的吸引人的URI。以及其他指示如何安装和执行程序的信息。图6显示了这种响应的示例。
![](https://images.seebug.org/content/images/2020/09/54e906fb-df3e-4a6f-b43a-3b5b264767fa.png-w331s) 图6. `GET / softwareinfo？title =
ssh_server`请求的响应示例。

与获取更新的机制类似，该恶意软件首先通过HTTP从`％C＆C％/
settingsv5`获取全局设置。此响应包含最新版本恶意软件的URI。然后，它向`％C＆C％/
version`发出GET请求，以获取最新的版本号。如果本地版本低于该版本，则会下载并安装torrent。

使用以下命令将torrent添加到“传输”中： `transmission-remote localhost -n superman:krypton -a
“<magnet URI>”`

50个跟踪器的硬编码列表用于获取所有torrent的对等对象。

#### 播下恶意种子

受感染的主机从`％C＆C％/ magnets`获取URI列表，将其全部下载并继续传播。这样这些文件可供其他人广泛下载，且能加快下载速度，提供冗余。、

## 抗检测和抗分析技术

该恶意软件利用多种技术来避免检测以及反分析。

从初始访问向量开始，ZIP归档文件中包含的可执行文件是一个相当不错的安装程序，它可以伪装成合法的InstallShield程序。该文件已用开源程序[Obfuscar加密](https://github.com/obfuscar/obfuscar
"Obfuscar加密")。所有恶意软件的自定义可执行文件都使用同一工具。恶意代码本身位于XOR加密的文件内，密钥是Setup.exe中经过硬编码的GUID
。

然后，将恶意软件安装到硬编码路径`％ProgramFiles（x86）％\ Adob​​e \ Acrobat Reader DC \ Reader \
update`，并将合法的Adobe Acrobat Reader可执行文件名称用于捆绑的Tor可执行文件及其本身。安装文件夹中包含的某些文件如图7所示。
![](https://images.seebug.org/content/images/2020/09/d52415f1-41da-4231-8e7a-c41db9e9625e.png-w331s)
图7.安装文件夹中的某些文件。Armsvc.exe是恶意软件，而ADelRCP.exe是Tor可执行文件。

为了实现持久性，KryptoCibule使用以下命令创建了一个计划的任务，该任务每五分钟运行一次。再次使用Adobe Reader相关名称。

`schtasks.exe / CREATE / SC MINUTE / MO 5 / TN“ Adobe Update Task ” / TR
\”“％ProgramFiles（x86）％\ Adob​​e \ Acrobat Reader DC \ Reader \ Update \
armsvc.exe \”” [/ RL最高] / F [/ RU系统]`

在执行有效负载之前以及在主循环的每次迭代之前，该恶意软件都会使用以下列表对运行分析软件进行检查。如果找到任何具有匹配名称的进程，它将停止所有正在运行的组件并退出。
![](https://images.seebug.org/content/images/2020/09/b05210f9-19c9-42a1-9b1f-79a9505d96b2.png-w331s)

#### 防病毒规避

在初始化cryptominer组件之前，该恶意软件对`rootSecurityCenter2 \ AntiVirusProduct
WMI`对象的字符串avast，avg和eset进行不区分大小写的检查，如图8的反编译代码所示。如果检测到这些字符串中的任何一个，将不会安装cryptominer组件。
![](https://images.seebug.org/content/images/2020/09/a9bc97ef-0859-4f06-9cf0-4ebeb1e7135c.png-w331s)
图8.清理了用于检查特定安全产品的函数的反编译代码。

每当恶意软件自行安装、更新或安装新组件时，通过发出以下命令，将使用的安装路径从Windows Defender自动扫描中排除：

`powershell -c “Add-MpPreference -ExclusionPath ‘<install path>'”`

它还会创建防火墙规则，以使用看起来无害的名称显式允许其组件的入站和出站流量。图9所示的函数还创建了一条规则，以阻止来自ESET内核服务（ekrn.exe）的出站流量。
![](https://images.seebug.org/content/images/2020/09/16c1b091-63a7-42e6-845c-35b7ea1a9495.png-w331s)
图9.阻止来自Windows防火墙中的ekrn.exe的出站流量的功能。

#### Tor网络使用

KryptoCibule带来了tor.exe命令行工具，其伪装为ADelRCP.exe，以及一个配置文件（如图10所示）为libstringutils.dll。
![](https://images.seebug.org/content/images/2020/09/234c05ae-fc0d-4ffa-baaf-6b32762ab229.png-w331s) 图10.最新版本的恶意软件使用的Tor配置文件。

这将在端口9050上设置一个SOCKS代理，恶意软件使用该代理通过Tor网络中继与C&C服务器的所有通信。这有两个好处：加密通信并使跟踪这些uri背后的实际服务器变得几乎不可能。

配置文件的第二部分在受害主机上设置洋葱服务。运营商可以通过Tor网络访问这些内容。首次启动这些服务时，Tor会自动为主机生成一个.onion
URI。然后，此唯一主机名将发送到`%C&C%/transferhost/<unique name>`。我们将在接下来的部分中讨论如何使用这些洋葱服务。
![](https://images.seebug.org/content/images/2020/09/bb8c6686-ef23-4d05-b724-d5312423b888.png-w331s)

恶意软件中包含两个C＆C服务器的洋葱URI。其中一个提供了REST API，恶意软件将其用于大多数通信，而另一个则用于下载文件。通过向`％C＆C％/
server`发出请求，可以一次获得一个附加的URI
。某些较旧版本的恶意软件使用这些恶意软件通过端口12461下载更新。我们相信这些URI指向其他受感染的主机。使用它们的恶意软件版本具有代码，可将其下载的更新放置在同一端口上的MiniWeb
HTTP Server服务的目录中。

我们能够在遥测数据中为文件服务器C＆C标识一个IP地址。

## 获取加密货币

KryptoCibule具有三个组件，这些组件利用受感染的主机来获取加密货币。

#### 密码挖掘

KryptoCibule的最新版本使用XMRig（一个使用CPU挖掘Monero的开源程序）和kawpowminer（另一个使用GPU挖掘以太坊的开源程序）。第二个仅在主机上找到专用GPU时使用。这两个程序都设置为通过Tor代理连接到操作员控制的挖掘服务器。

在主循环的每次迭代中，恶意软件都会检查电池电量以及自上次用户输入以来的时间。然后，它将基于此信息启动或停止矿工进程。如果主机在最近3分钟内未收到任何用户输入，并且电池电量至少为30％，则GPU和CPU矿机都将不受限制地运行。否则，GPU矿工将被挂起，并且CPU矿工被限制为一个线程。如果电池电量不足10％，则两个矿工都将停止。这样做是为了减少被受害者注意的可能性。

#### 剪贴板劫持

第二个组件伪装为SystemArchitectureTranslation.exe。它使用[AddClipboardFormatListener函数](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-addclipboardformatlistener
"AddClipboardFormatListener函数")来监视对剪贴板的更改，并将从`％C＆C％/
regexes`获得的替换规则应用于其内容。该侦听器的代码如图11所示。值0x31D对应于WM_CLIPBOARDUPDATE常量。

这些规则以`<regular_expresssion>！<wallet>`的形式匹配加密货币钱包地址的格式，并将其替换为由恶意软件操作员控制的钱包地址。这是尝试将受害者进行的交易重定向到运营商的钱包。每当settings.cfg文件更改时，此组件便使用[FileSystemWatcher](https://docs.microsoft.com/en-us/dotnet/api/system.io.filesystemwatcher?view=netcore-3.1
"FileSystemWatcher")重新加载替换规则。
![](https://images.seebug.org/content/images/2020/09/e48006d7-2748-4284-86d5-0d4972ca6f47.png-w331s)
图11.剪贴板挂钩使用的侦听器功能的反编译代码。

在撰写本文时，剪贴板劫持组件使用的钱包收到了略高于1800美元的比特币和以太坊。图12中显示了一个这样的钱包。通过将与相同交易中的来源的钱包相关联，我们能够发现至少四个可能属于KryptoCibule运营商的其他比特币钱包。
![](https://images.seebug.org/content/images/2020/09/4fa8bcb7-4a8b-49e1-9fcc-54c09766fecd.png-w331s)
图12.剪贴板劫持组件使用的比特币钱包。

#### 文件渗透

第三个组件遍历每个可用驱动器的文件系统，并查找包含某些术语的文件名。我们在调查中获得的此类术语的列表如图13所示。
![](https://images.seebug.org/content/images/2020/09/27e0c26a-b65c-4e72-bd19-4ebe540f21fe.png-w331s)
图13.要搜索的单词列表，取自GET％C＆C％/ settingsv5响应。

大多数术语指的是加密货币，钱包或矿工，但也存在一些更通用的术语，例如加密货币（多种语言），种子和密码。该列表包含捷克语和斯洛伐克语中的类似术语，例如heslo，hesla和banka（分别是“
password”，“ passwords”和“
bank”两个词）。一些术语也对应于路径或文件，这些路径或文件可以提供其他有趣的数据（Desktop，私有），包括私有密钥（.ssh和.aws）。它收集每个匹配文件的完整路径，并将列表发送到`%C&C%/found/<unique
name>`。

我们认为，这与在端口9187上作为洋葱服务运行的SFTP服务器协同工作有关系。此服务器为每个可用驱动器创建映射，并使用在恶意软件中硬编码的凭据使它们可用。因此，通过使攻击者控制的计算机通过SFTP从受感染的主机请求收集的路径，可以将其用于文件扩散。

KryptoCibule还会安装合法的Apache httpd服务器，该服务器配置为无限制地充当转发代理，并且可以作为端口9999上的洋葱服务访问。

## 结论

自2018年底以来，KryptoCibule恶意软件一直在泛滥，并且仍处于活动状态，但到目前为止似乎并没有引起太多关注。它使用合法的开放源代码工具以及广泛部署的反检测方法可能是造成此问题的原因。受害人数相对较少（数百人），而且他们大多局限于两个国家，这也可能是造成这种情况的原因。KryptoCibule在其生命周期中定期添加了新功能，并且仍在积极开发中。

据推测，恶意软件操作员通过窃取钱包和挖掘加密货币能够比在剪贴板劫持组件所使用的钱包中发现的收入更高。仅由该组件产生的收入似乎不足以证明所观察到的开发工作的合理性。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1326/>

