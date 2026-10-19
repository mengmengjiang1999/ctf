**译者：知道创宇404实验室翻译组  
原文链接：<https://unit42.paloaltonetworks.com/manageengine-godzilla-nglite-kdcsponge/>**

## 摘要

2021年9月16日，美国网络安全和基础设施安全局(CISA)发布了一个警报，警告APT攻击组织的攻击者正在积极利用一个漏洞，该漏洞是在自助密码管理和单点登录解决方案
ManageEngine ADSelfService Plus 中新发现的。该警告解释说，我们观察到恶意攻击者部署特定的 webshell
和其他技术，以保持受害者环境中的持久性; 然而，在随后的日子里，我们观察到第二个不同的攻击行为，是利用了同一漏洞。

早在9月17日，这位攻击者就利用美国的租赁基础设施扫描了互联网上数百个易受攻击的组织。随后，对漏洞的利用在9月22日开始了，可能持续到了10月初。在此期间，这个攻击者成功地攻击至少9个全球实体，涉及科技、国防、医疗、能源和教育等行业。

经过初步步骤，一个安装了 Godzilla webshell有效载荷被上传到受害者网络。这种操作对所有受害者中都是一致的;
然而，我们也观察到一小部分受到危害的组织随后收到了一个名为 NGLite 的修改版本的新后门。然后，攻击者使用 webshell 或者 NGLite
有效载荷来运行命令，并横向移动到网络上的其他系统，而他们只要网络服务器上下载，就可以提取利益相关的文件。如果攻击者们想攻击一个域控制器，他们就安装了一个新的窃取证书工具，我们称之为
KdcSponge。

KdcSponge和 NGLite 都是按照中文说明开发的，可以在 GitHub
上公开下载。我们认为，攻击者将这些工具结合使用，作为冗余的一种形式，以维护对高利益网络的访问。Godzilla 是一个功能丰富的
webshell，它解析入站 HTTP POST 请求，用私密密钥解密数据，执行解密内容以执行额外的功能，并通过 HTTP
响应返回结果。这使得攻击者可以将可能被标记为恶意的代码与目标系统隔开，直到他们准备好动态执行它。

NGLite是一个“基于区块链技术的匿名跨平台远程控制程序”它利用新型网络(NKN)基础设施进行命令和控制(C2)通信，从理论上讲，这会为用户带来匿名性。需要注意的是，NKN
是一个合法的网络服务，它使用区块链技术来支持分散的对等点网络。使用 NKN 作为
c2通道是非常罕见的。我们已经看到的只有13个样本与分散的对等点网络通信——共9个 NGLite
样本和4个相关的一个合法的开放源码实用程序（Surge），它使用 NKN 用来文件共享。

最后，KdcSponge 是一种新型的证书窃取工具，用于针对域控制器窃取证书。KdcSponge
将自己注入到本地安全认证子系统服务服务器进程(LSASS)中，并将挂接特定的函数来收集用户名和密码，这些用户名和密码是从尝试通过 Kerberos
验证到域的帐户中获得的。恶意代码将盗取的证书写入文件，但依赖于其他功能进行提取。

## 初始访问

从9月17日开始一直到10月初，我们观察到，ManageEngine ADSelfService
Plus服务器被扫描。通过全球遥测，我们认为攻击者仅在美国就瞄准了至少370台Zoho
ManageEngine服务器。鉴于规模，我们评估这些扫描基本上是完全随机的，因为目标范围从教育到国防部实体。
在获得扫描结果后，攻击者于9月22日转变了攻击企图。这些攻击集中于CVE-2021-40539，CVE-2021-40539允许REST
API身份验证绕过，从而在受攻击的设备中执行远程代码。为了实现这一结果，攻击者向REST API LicenseMgr交付了精心编制的POST语句。

虽然我们尚不了解此次活动中被侵害的组织总数，但我们认为，在全球范围内，技术、国防、医疗保健、能源和教育行业至少有九家实体受到了损害。成功利用该漏洞后，攻击者上传了一个有效负载，该负载部署了一个Godzilla
webshell，从而能够额外访问受害者网络。我们观察到美国的以下租用IP地址与受损服务器交互：

24.64.36[.]238  
45.63.62[.]109  
45.76.173[.]103  
45.77.121[.]232  
66.42.98[.]156  
140.82.17[.]161  
149.28.93[.]184  
149.248.11[.]205  
199.188.59[.]192

在部署了webshell之后，我们还发现了在一个受损网络子集中部署的额外工具的使用。具体来说，攻击者部署了一个名为NGLite的自定义开源后门变体和一个我们跟踪的凭证收集工具KdcSponge。下面几节将详细分析这些工具。

## 恶意软件

利用阶段，两个不同的可执行文件被保存到受感染的服务器:`ME_ADManager.exe`和`ME_ADAudit.exe`。`ME_ADManager.exe`文件作为一个dropper木马，不仅保存了一个Godzilla的webshell到系统，而且还安装和运行保存到系统的其他可执行文件，特别是`ME_ADAudit.exe`。`ME_ADAudit.exe`可执行文是基于NGLite，威胁攻击者将其用作在系统上运行命令的有效负载。

### `ME_ADManager.`dropper

初始利用完成后，dropper病毒保存到以下路径:

`c:\Users\[username]\AppData\Roaming\ADManager\ME_ADManager.exe`

对该文件的分析显示，该有效负载的作者在构建样本时没有删除调试符号。因此，在样本中存在以下调试路径，并建议使用用户名pwn创建此有效负载:

`c:\Users\pwn\documents\visual studio
2015\Projects\payloaddll\Release\cmd.pdb`

在执行时，该示例首先创建以下通用互斥锁，这些互斥锁在网上的许多代码示例中都可以找到，这是为了避免运行多个droper案例:

`cplusplus_me`

然后，dropper尝试编写一个硬编码的Godzilla webshell到下列位置，我们将在稍后的报告中提供详细的分析，

    
    
    ../webapps/adssp/help/admin-guide/reports.jsp
    c:/ManageEngine/ADSelfService Plus/webapps/adssp/help/admin-guide/reports.jsp
    ../webapps/adssp/selfservice/assets/fonts/lato/lato-regular.jsp
    c:/ManageEngine/ADSelfService Plus/webapps/adssp/selfservice/assets/fonts/lato/lato-regular.jsp

然后，dropper创建文件夹`%APPDATA%\ADManager`，然后创建以下注册表项，以在重启后持续运行，并将自己复制到`%APPDATA%\ADManager\ME_ADManager.exe`，

    
    
    Software\Microsoft\Windows\CurrentVersion\Run\ME_ADManager.exe : %APPDATA%\ADManager\ME_ADManager.exe
    Software\Microsoft\Windows\CurrentVersion\Run\ME_ADAudit.exe : %SYSTEM32%\ME_ADAudit.exe

然后，dropper将ADAudit.exe从当前目录复制到以下路径，并使用WinExec运行该文件:

`%SYSTEM32%\ME_ADAudit.exe`

Dropper不会将`ME_ADAudit.exe`文件写入磁盘，这意味着攻击者必须在dropper执行之前将该文件上传到服务器，这可能是cve - 201
-40539漏洞的一部分。在我们对多个事件的分析中，我们发现ME_ADAudit.exe样本保持了一致的SHA256哈希值`805b92787ca7833eef5e61e2df1310e4b6544955e812e60b5f834f904623fd9f`，因此表明攻击者针对多个目标部署了相同的定制版本的NGLite后门。

## Godzilla webshell

如前所述，最初的拖dropper含一个硬编码的Java Server Page (JSP)
webshell。通过对webshell的分析，确定为中文版哥斯拉webshell V3.00+。Godzilla
webshell是由用户BeichenDream开发的，他说他们创建这个webshell是因为当时可用的webshell在红队比赛时经常被安全产品检测到。因此，作者宣称它将通过利用AES对其网络流量加密来避免检测，并且在安全厂商产品保持非常低的静态检测率。

![](https://images.seebug.org/content/images/2021/11/8af095d2-a35f-4323-91a8-9c445a16fdcb.png-w331s)
VirusTotal对Godzilla webshell的检测

区域威胁组织入侵时，采用Godzilla
webshell并不奇怪，因为它提供了比相同组织使用的其他webshell(如ChinaChopper)更多的功能和网络逃避。

就功能而言，JSP webshell本身相当简单，并保持了轻量级的内存占用。它的主要功能是解析HTTP
POST，使用秘密密钥解密内容，然后执行有效负载。这使得攻击者可以将可能被标记为恶意的代码隔离在目标系统之外，直到他们准备好动态执行它。

下图显示了默认JSP webshell的初始部分以及解密函数。

![](https://images.seebug.org/content/images/2021/11/05fcf3de-6ae6-47aa-a79f-ef65b446272a.png-w331s)
默认Godzilla JSP webshell的头部

值得注意的是变量`xc`和`pass`在代码的第一行和第二行。这些是每次操作符生成新的webshell时都会更改的主要组件，这些变量表示在该webshell中用于AES解密的秘密密钥。

当您手动生成webshell时，您需要指定明文传递和密钥。默认情况下，它们是`pass`和`key`。

![](https://images.seebug.org/content/images/2021/11/d4c1cb6d-62d9-47ba-9217-2e643067df48.png-w331s)

为了弄清楚这些是如何在webshell本身中呈现的，我们可以看看Godzilla JAR文件。

下面，您可以看到代码在`/shells/cryptions/JavaAES/GenerateShellLoder`函数下替换了其中一个嵌入式webshell模板中的字符串。

![](https://images.seebug.org/content/images/2021/11/ebdcb906-b542-4175-aa38-1df61eca855b.png-w331s)
Generate.class文件中的GenerateShellLoder函数

因此，我们知道webshell中的`xc`变量将是AES密钥，如模板中所示。

    
    
    String xc="{secretKey}"; String pass="{pass}"; String md5=md5(pass+xc)

我们观察到xc值似乎是一个散列，存在`/core/shell/ShellEntity.class`文件下，我们可以看到代码使用MD5散列的前16个字符作为明文密钥。

    
    
    public String getSecretKeyX()
    {
    
    return functions.md5(getSecretKey()).substring(0, 16);
    
    }

这样，我们就知道`3c6e0b8a9c15224a`的`xc`值是单词key的MD5散列的前16个字符。

鉴于此，`xc`和`pass`变量是两个主要字段，可用于跟踪和尝试跨事件映射活动。在本博客中，我们生成了一个Godzilla
webshell，其中包含用于分析的默认选项；其中，默认选项与攻击中观察到的值之间的唯一区别是`xc`和`pass`值不同。

此webshell的一个重要特征是，作者称它缺乏静态检测，通过避免关键字或安全产品签名可能识别的常见结构，使此文件不太显眼。一种特别有趣的静态规避技术是使用Java三元条件运算符来指示解密。

这里的条件是`m？1:2–m`是传递给该函数的布尔值，如下图所示，如果m为真，则使用第一个表达式常量（`1`）。否则，第二（`2`）项通过。参考Java文档，`1`是加密模式，而`2`是解密模式。

![](https://images.seebug.org/content/images/2021/11/ce326eaa-1914-4ece-80fc-826e1337ade7.png-w331s)

当webshell执行此函数`x`时，它不会设置m的值，因此会强制`m`为False并将其设置为解密。

    
    
    response.getWriter（）.write（base64Encode（x（base64Decode（f.toString（）），true））；

为了理解Godzilla的功能，我们可以查看`/shell/payloads/java/JavaShell.class`。该类文件包含提供给操作者的所有函数。下面是`getFile`函数的一个示例。

![](https://images.seebug.org/content/images/2021/11/ab36a83f-9020-4a44-9de9-bcbf14bf2470.png-w331s)

有效载荷功能：

    
    
    getFile
    downloadFile
    getBasicsInfo
    uploadFile
    copyFile
    deleteFile
    newFile
    newDir
    currentDir
    currentUserName
    bigFileUpload
    bigFileDownload
    getFileSize
    execCommand
    getOsInfo
    moveFile
    getPayload
    fileRemoteDown
    setFileAttr

从函数的名称可以看出，Godzilla webshell为远程系统导航、与远程系统之间的数据传输、远程命令执行和枚举提供了大量有效负载。

这些有效载荷将使用前面描述的密钥进行加密，操作软件将向包含数据的受损系统发送HTTP POST。

此外，如果我们检查`core/ui/component/dialog/ShellSetting.class`文件（如下所示），`initAddShellValue（）`函数包含远程网络访问的默认配置设置。因此，可以识别诸如静态HTTP头和用户代理字符串之类的元素，以帮助取证搜索web访问日志，寻找潜在的危害。

    
    
    private void initAddShellValue() {
    
    this.shellContext = new ShellEntity();
    
    this.urlTextField.setText("http://127.0.0.1/shell.jsp");
    this.passwordTextField.setText("pass");
    this.secretKeyTextField.setText("key");
    this.proxyHostTextField.setText("127.0.0.1");
    this.proxyPortTextField.setText("8888");
    this.connTimeOutTextField.setText("60000");
    this.readTimeOutTextField.setText("60000");
    this.remarkTextField.setText("??");
    this.headersTextArea.setText("User-Agent: Mozilla/5.0 (Windows NT
    10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\nAccept-Language:
    zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2\n");
    
    this.leftTextArea.setText("");
    this.rightTextArea.setText("");
    
    }

下面是web服务器访问日志的一个片段，其中显示了使用Curl应用程序并发送自定义URL负载以触发CVE-2021-40539漏洞的初始攻击。然后，它显示了Godzilla
webshell的后续访问，它已被初始Dropper放入硬编码路径中。通过查看用户代理，我们可以确定威胁攻击者从利用漏洞攻击到最初访问webshell的时间仅四多分钟。

    
    
    - /./RestAPI/LicenseMgr "-" X.X.X.X Y.Y.Y.Y POST [00:00:00] - - 200 "curl/7.68.0"
    - /help/admin-guide/reports.jsp "-" X.X.X.X Y.Y.Y.Y POST [+00:04:07] - - 200 "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"

## 定制NGLite

NGLite是一个用Go语言编写的开源后门（特别是Go版本1.13）。它可以从公共GitHub存储库[下载](https://github.com/Maka8ka/NGLite)。NGLite是一种后门木马，只能运行通过其C2通道接收的命令。虽然这些功能是后门的标准功能，但NGLite使用了一种新颖的C2通道，该通道利用基于合法NKN的分散网络在后门和攻击者之间进行通信。

NKN鼓吹他们的分散网络使用公共区块链，可以支持数百万对等方之间的通信，每个对等方都由唯一的NKN地址而不是典型的网络标识符（如IP地址）标识。因此，NGLite工具在其C2通道中与之通信的即时IP地址只是分散网络中的对等地址，不太可能代表攻击者的网络位置。这种设计使得NGLite
C2通信信道的检测和预防变得困难。

幸运的是，将NKN用作C2通道的情况非常少见。我们总共只看到13个样本使用NKN通信——9个NGLite样本，还有4个与一个名为Surge的开源实用程序相关，该实用程序使用NKN进行文件共享。VirusTotal扫描了9个已知NGLite样本中的8个。四个未被检测到，三个被一个抗病毒病毒检测到，其余一个样本被五个抗病毒检测到。如此低的检测率表明NGLite在此次攻击活动中几乎没有防病毒覆盖。

如前一节所述，dropper创建注册表项并执行NGLite后门的自定义变量：
`SHA256:805b92787ca7833eef5e61e2df1310e4b6544955e812e60b5f834f904623fd9f`

它保存在以下路径： `C:\Windows\system32\ME\u ADAudit.exe`

基于Go语法的后门中的数据结构包含以下路径，用于在开发人员系统上存储此自定义NGLite变体的主要源代码：
`/mnt/hgfs/CrossC2-2.2/src/ng.com/lprey/main.go`

基于这条路径，有人可能会猜测，攻击者使用CrossC2构建了一个跨平台的Cobalt打击C2有效载荷；然而，我们并不认为该有效载荷实际上是基于CrossC2的，因为该有效载荷是公开可用的NGLite后门的定制版本。

攻击者可能将CrossC2控制系统串作为误导方向放入路径中，希望迷惑威胁分析人员，使他们认为他们正在交付Cobalt
Strike有效载荷。我们已经看到以下NGLite样本使用的源代码路径，可以追溯到8月11日，这表明该攻击者已经使用该工具几个月了：

    
    
    3da8d1bfb8192f43cf5d9247035aa4445381d2d26bed981662e3db34824c71fd
    5b8c307c424e777972c0fa1322844d4d04e9eb200fe9532644888c4b6386d755
    3f868ac52916ebb6f6186ac20b20903f63bc8e9c460e2418f2b032a207d8f21d

此攻击中使用的自定义NGLite样本检查了命令行参数中的`g`或`group`值。如果此开关不存在，有效负载将使用默认字符串`7AA7AD1BFA9DA581A7A044896279517EEF9357B81E406E3AEE1A66101FE824`，NGLite将其称为种子标识符。

有效负载将创建一个`prey
id`，该id通过连接系统网络接口卡（NIC）的MAC地址和IPv4地址生成，并用连字符（-）分隔这两个地址。该目标标识符将用于C2通信。

NGLite有效载荷将使用NKN分散网络进行C2通信。请参见下面示例中的NKN客户端配置：

![](https://images.seebug.org/content/images/2021/11/cdafd86a-be5e-47a0-bfba-ae05fa1a03e0.png-w331s)

该样本首先通过TCP/30003访问`seed.nkn[.]org`，具体来说是一个HTTP POST请求，其结构如下：

![](https://images.seebug.org/content/images/2021/11/3dd218b7-0b86-48b1-bfac-4a79bf201019.png-w331s)

它还将发送HTTP POST请求，`monitor_03`作为目标id，如下所示：
![](https://images.seebug.org/content/images/2021/11/78b40dee-d00e-4946-92ee-187246bdb6c7.png-w331s)

`seed.nkn[.]org`服务器使用JSON中的`[prey id（MAC-IPv4）]`响应此请求，其结构如下：

    
    
    {"id":"nkn-sdk-go","jsonrpc":"2.0","result":{"addr":"66.115.12.89:30002","id":"223b4f7f4588af02badaa6a83e402b33dea0ba8908e4cd6008f84c2b98a6a7de","pubkey":"38ce48a2a3cffded7c2031514acaef29851ee39303795e4b3e7fce5a6619e6be","rpcAddr":"66.115.12.89:30003"}}

这表明有效负载将通过TCP/30003在`66.115.12.89`与对等方通信。然后，`seed.nkn[.]org`服务器用以下内容响应`monitor_03`请求，这表明有效负载将通过TCP/30003与`54.204.73.156`通信：

    
    
    {"id":"nkn-sdk-go","jsonrpc":"2.0","result":{"addr":"54.204.73.156:30002","id":"517cb8112456e5d378b0de076e85e80afee3c483d18c30187730d15f18392ef9","pubkey":"99bb5d3b9b609a31c75fdeede38563b997136f30cb06933c9b43ab3f719369aa","rpcAddr":"54.204.73.156:30003"}}

从`seed.nkn[.]org`获得响应后，负载将向JSON中`addr`字段中提供的IP地址和TCP端口发出HTTP
GET请求。这些HTTP请求如下所示，但请记住，这些系统不是由攻击者控制的；相反，它们只是最终将返回攻击者内容的对等链中的第一个对等：

![](https://images.seebug.org/content/images/2021/11/e07ae1b6-41fe-472e-b94c-a246940bdea7.png-w331s)

最终，自定义NGLite客户端和服务器之间的网络通信使用AES加密，密钥如下： `WHATswrongwithUu`

自定义NGLite样本将首先向C2发送一个初始信标，该信标包含whoami命令的结果，还有字符串`#windows`，如下所示：
`[username]#windows`

发送初始信标后，NGLite示例将运行一个名为`Preylistener`的子函数，该函数创建一个侦听入站请求的服务器。该样本还将侦听入站通信，并尝试使用默认AES密钥`1234567890987654`对其进行解密。它将通过Go方法`os/exec.command`以命令的形式运行解密的内容。然后使用相同的AES密钥对结果进行加密并发送回请求者。

## 攻击之后

在破坏网络后，威胁攻击者迅速从最初的立足点转移到目标网络上的其他系统，通过其NGLite负载和Godzilla
webshell运行命令。在获得对初始服务器的访问权后，攻击者集中精力从本地域控制器收集和过滤敏感信息，例如Active
Directory数据库文件（`ntds.dit`）和注册表中的系统配置单元。不久之后，我们观察到攻击者正在安装KdcSponge凭证窃取程序，这个我们将在下面详细讨论。最终，参与者感兴趣的是窃取凭据、维护访问权限以及从受害者网络收集敏感文件进行过滤。

## 凭证获取和KdcSponge

在分析过程中，Unit42发现了一些日志，这些日志表明攻击者使用PwDump和内置的`comsvc.dll`创建了`lsass.exe`进程的小型转储，用于凭证窃取；然而，当攻击者希望从域控制器窃取凭据时，他们安装了自定义工具，我们跟踪该工具为
**KdcSponge** 。

KdcSponge的目的是从LSASS进程中钩住API函数，从通过Kerberos服务（“KDC服务”）进行身份验证的入站尝试中窃取凭据。KdcSponge会将域名、用户名和密码捕获到系统上的一个文件中，然后攻击者会通过对服务器的现有访问手动过滤该文件。

我们知道有两个KdcSponge样本，它们都被命名为`user64.dll`。它们具有以下SHA256哈希：

    
    
    3C90DF0E02CC9B1CF1A86F9D7E6F777366C5748BD3C4070B49460B48B4D4090
    b4162f039172dcb85ca4b85c99dd77beb70743ffd2e6f9e0ba78531945577665

要启动KdcSponge凭据窃取程序，攻击者将运行以下命令加载并执行恶意模块： `regsvr32/s user64.dll`

在第一次执行时，`regsvr32`应用程序运行`user64.dll`导出的`DllRegisterServer`函数。`DllRegisterServer`函数解析`sfc_os.dll`中的`SetSfcFileException`函数，并尝试在`c:\Windows\system32\kdcsvc.dll`文件上禁用Windows文件保护（WFP）。然后，它尝试通过以下方式将自身注入正在运行的`lsass.exe`进程：

  1. 使用`OpenProcess`打开`lsass.exe`进程。
  2. 使用`VirtualAllocEx`在远程进程中分配内存。
  3. 使用`WriteProcessMemory`将字符串`user64.dll`写入分配的内存。
  4. 使用`RtlCreateUserThread`，在`lsass.exe`进程内以`user64.dll`作为参数调用`LoadLibraryA`。

现在`user64.dll`正在`lsass.exe`进程中运行，它将首先创建以下注册表项，以通过系统重新启动建立持久性：

    
    
    HKEY\U LOCAL\U MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce\KDC服务：regsvr32/s user64.dll

从这里开始，样本将通过尝试获取以下模块之一的句柄来确保系统正在运行Kerberos服务：

    
    
    kdcsvc.dll
    kdccli.dll
    Kdcsvs.dll

KdcSponge尝试使用以下三种方法定位三个未记录的API函数——特别是`KdcVerifyEncryptedTimeStamp`、`KerbHashPasswordEx3`和`KerbFreeKey`：

  1. 标识Kerberos模块的版本，并使用API函数的硬编码偏移量进行挂钩。
  2. 联系Microsoft的symbol server以查找Kerberos模块中API函数的偏移量，并通过与硬编码字节序列进行比较来确认正确的函数。
  3. 在Kerberos模块中搜索硬编码字节序列。

KdcSponge定位要挂接的API函数的主要方法是基于可移植可执行文件（PE）的`IMAGE_FILE_HEADER`部分中`TimeDateStamp`来确定Kerberos模块的版本。一旦确定了Kerberos模块的版本，KdcSponge就具有硬编码的偏移量，它将使用这些偏移量在该版本的模块中钩住适当的函数。KdcSponge查找以下TimeDateStamp值：

    
    
    2005-12-14 01:24:41
    2049-10-09 00:46:34
    2021-04-08 07:30:26
    2021-03-04 04:59:27
    2020-03-13 03:20:15
    2020-02-19 07:55:57
    2019-12-19 04:15:06
    2019-07-09 03:15:04
    2019-05-31 06:02:30
    2018-10-10 07:46:08
    2018-02-12 21:47:29
    2017-03-04 06:27:32
    2016-10-15 03:52:20
    2020-11-26 03:04:23
    2020-06-05 16:15:22
    2017-10-14 07:22:03
    2017-03-30 19:53:59
    2013-09-04 05:49:27
    2012-07-26 00:01:13

如果KdcSponge无法确定Kerberos模块的版本，并且域控制器运行的是Windows Server 2016或Server
2019（主版本10），则负载将接触到Microsoft的符号服务器（`msdl.Microsoft.com`），试图找到几个未记录的API函数的位置。该样本将向如下结构的URL发出HTTPS
GET请求，URL的GUID部分是PE的`IMAGE_DEBUG_TYPE_CODEVIEW`部分中RSDS结构的GUID值：
`/download/symbols/[library name].pdb/[GUID]/[library name].pdb`

样本将结果保存到以下位置的文件中，同样，文件名的GUID是`IMAGE_DEBUG_TYPE_CODEVIEW`部分中RSDS结构的GUID值：
`ALLUSERPROFILE\Microsoft\Windows\Caches\[GUID].db:`

如上所述，我们认为代码访问symbol服务器的原因是查找三个未记录的Kerberos相关函数的位置：`KdcVerifyEncryptedTimeStamp`、`KerbHashPasswordEx3`和`KerbFreeKey`。此样本主要在以下库中查找这些函数：
`kdcsvc.KdcVerifyEncryptedTimeStamp kdcsvc.KerbHashPasswordEx3
kdcpw.KerbHashPasswordEx3 kdcsvc.KerbFreeKey kdcpw.KerbFreeKey`

如果找到这些函数，样本将搜索特定的字节序列，如表1所示，以确认函数是否正确，并验证它们是否未被修改。

Function | Hex bytes  
---|---  
kdcsvc.KdcVerifyEncryptedTimeStamp | 48 89 5c 24 20 55 56 57 41 54 41 55 41 56
41 57 48 8d 6c 24 f0 48 81 ec 10 01 00 00 48 8b 05 a5  
kdcsvc.KerbHashPasswordEx3 | 48 89 5c 24 08 48 89 74 24 10 48 89 7c 24 18 55
41 56 41 57 48 8b ec 48 83 ec 50 48 8b da 48 8b  
kdcpw.KerbHashPasswordEx3 | 48 89 5c 24 08 48 89 74 24 10 48 89 7c 24 18 55 41
56 41 57 48 8b ec 48 83 ec 50 48 8b da 48 8b  
kdcpw.KerbFreeKey | 48 89 5c 24 08 57 48 83 ec 20 48 8b d9 33 c0 8b 49 10 48
8b 7b 18 f3 aa 48 8b 4b 18 ff 15 72 19  
kdcsvc.KerbFreeKey | 48 89 5c 24 08 57 48 83 ec 20 48 8b 79 18 48 8b d9 48 85
ff 0f 85 00 c5 01 00 33 c0 48 89 03 48  
  
如果域控制器运行的是Windows Server 2008或Server
2012（主要版本6），KdcSponge不会接触到符号服务器，而是会在整个`kdcsvc.dll`模块中搜索表2中列出的字节序列以查找API函数。

Function | Hex bytes  
---|---  
kdcsvc.KdcVerifyEncryptedTimeStamp | 48 89 5C 24 20 55 56 57 41 54 41 55 41 56
41 57 48 8D 6C 24 F9 48 81 EC C0 00 00 00 48 8B  
kdcsvc.KerbHashPasswordEx3 | 48 89 5C 24 08 48 89 74 24 10 48 89 7C 24 18 55
41 56 41 57 48 8B EC 48 83 EC 40 48 8B F1  
kdcsvc.KerbFreeKey | 40 53 48 83 EC 20 48 8B D9 48 8B 49 10 48 85 C9 0F 85 B4
B9 01 00 33 C0 48 89 03 48 89 43  
  
一旦找到`KdcVerifyEncryptedTimeStamp`、`KerbHashPasswordEx3`和`KerbFreeKey`函数，该样本将尝试钩住这些函数，以监视对它们的所有调用，意图窃取凭据。当向域控制器发出身份验证请求时，将调用Kerberos服务（KDC服务）中的这些函数，示例将捕获入站凭据。然后将凭据写入以下位置的磁盘：
`%ALLUSERPROFILE%\Microsoft\Windows\Caches\system.dat`

被盗凭证使用单字节异或算法加密，使用0x55作为密钥，并按以下结构每行写入system.dat文件：
`[<timestamp>]<domain><username><cleartextpassword>`

## 归因

虽然归因仍在进行中，我们无法确认攻击行为背后的参与者，但我们确实观察到了我们分析的案例中使用的战术和工具与威胁组织3390（TG-3390，Emissary
Panda，APT27）之间的一些相关性。

具体而言，正如SecureWorks在一篇关于先前[TG-3390](https://www.secureworks.com/research/threat-group-3390-targets-organizations-for-cyberespionage)操作的文章中所记录的，我们可以看到TG-3390在利用合法被盗凭证进行横向移动和攻击域控制器之前，同样使用了web攻击和另一种流行的称为ChinaChopper的中文webshell作为其初始立足点。虽然WebShell和漏洞利用有所不同，但一旦攻击者实现了对环境的访问，我们注意到他们的一些过滤工具中存在重复。

SecureWorks表示，攻击者正在使用WinRar伪装为不同的应用程序，将数据拆分为Recycler目录中的RAR归档文件。他们从部署用于执行此工作的批处理文件中提供了以下代码段：

    
    
    @echo off
    c:\windows\temp\svchost.exe a -k -r -s -m5 -v1024000 -padmin-windows2014 “e:\recycler\REDACTED.rar” “e:\ProgramData\REDACTED\”
    Exit

从我们对最近针对ManageEngine ADSelfService
Plus的攻击的分析中，我们发现到了相同的技术——将相同的参数顺序和位置传递给重命名的WinRar应用程序。

    
    
    @echo off
    dir %~dp0>>%~dp0\log.txt
    %~dp0\vmtools.exe a -k -r -s -m5 -v4096000 -pREDACTED "e:\$RECYCLE.BIN\REDACTED.rar" "E:\Programs\REDACTED\REDACTED"

一旦文件被暂存，在这两种情况下，它们都可以在面向外部的web服务器上访问。然后，攻击者将通过直接HTTP GET请求下载它们。

## 结论

2021年9月，Unit42 观察到一次攻击活动，攻击者利用Zoho的ManageEngine产品ADSelfService
Plus中最近修补的漏洞（在CVE-2021-40539中跟踪）初步访问目标组织。技术、国防、医疗保健、能源和教育行业中至少有九家实体在这次攻击活动中受到了损害。

攻击后，攻击者迅速在网络中横向移动，并部署多个工具来运行命令，以执行攻击后活动。参与者非常依赖Godzilla
webshell，在操作过程中将开放源代码webshell的几个变体上传到受损服务器。

其他一些工具具有新颖的特性，或者在以前的攻击中没有公开讨论，特别是NGLite后门和KdcSponge stealer。

例如，NGLite后门使用一种新的C2通道，该通道使用称为NKN的分散网络，而KdcSponge窃取器钩住未记录的函数，从入站Kerberos身份验证尝试中获取凭据到域控制器。

Unit
42认为，攻击者的主要目的是获得对网络的持久访问，以及从受损组织收集和过滤敏感文档。攻击者将敏感文件收集到暂存目录，并在Recycler文件夹中创建了受密码保护的多卷RAR存档。攻击者通过直接从面向外部的web服务器下载单个RAR档案来过滤文件。

## IoCs

### Dropper SHA256

    
    
    b2a29d99a1657140f4e254221d8666a736160ce960d06557778318e0d1b7423b
    5fcc9f3b514b853e8e9077ed4940538aba7b3044edbba28ca92ed37199292058

### NGLite SHA256

    
    
    805b92787ca7833eef5e61e2df1310e4b6544955e812e60b5f834f904623fd9f
    3da8d1bfb8192f43cf5d9247035aa4445381d2d26bed981662e3db34824c71fd
    5b8c307c424e777972c0fa1322844d4d04e9eb200fe9532644888c4b6386d755
    3f868ac52916ebb6f6186ac20b20903f63bc8e9c460e2418f2b032a207d8f21d

### Godzilla Webshell SHA256

    
    
    a44a5e8e65266611d5845d88b43c9e4a9d84fe074fd18f48b50fb837fa6e429d
    ce310ab611895db1767877bd1f635ee3c4350d6e17ea28f8d100313f62b87382
    75574959bbdad4b4ac7b16906cd8f1fd855d2a7df8e63905ab18540e2d6f1600
    5475aec3b9837b514367c89d8362a9d524bfa02e75b85b401025588839a40bcb

### KdcSponge SHA256

    
    
    3c90df0e02cc9b1cf1a86f9d7e6f777366c5748bd3cf4070b49460b48b4d4090
    b4162f039172dcb85ca4b85c99dd77beb70743ffd2e6f9e0ba78531945577665

### 攻击者IP地址

24.64.36 [.]238
([ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=24.64.36%5B.%5D238))  
45.63.62[.]109([ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=45.63.62%5B.%5D109))  
45.76.173[.]103([ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=45.76.173%5B.%5D103))  
45.77.121[.]232([ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=45.77.121%5B.%5D232))  
66.42.98[.]156([ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=66.42.98%5B.%5D156))  
140.82.17[.]161([ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=140.82.17%5B.%5D161))  
149.28.93[.]184([ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=149.28.93%5B.%5D184))  
149.248.11[.]205([ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=149.248.11%5B.%5D205))  
199.188.59[.]192([ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=199.188.59%5B.%5D192))

### 注册表项

`Software\Microsoft\Windows\CurrentVersion\Run\ME_ADManager.exe
Software\Microsoft\Windows\CurrentVersion\Run\ME_ADAudit.exe
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce\KDC
Service`

### Additional Resources

[KdcSponge ATOM](https://unit42.paloaltonetworks.com/atoms/kdcsponge/) [Threat
actor DEV-0322 exploiting ZOHO ManageEngine ADSelfService
Plus](https://www.microsoft.com/security/blog/2021/11/08/threat-actor-dev-0322-exploiting-zoho-manageengine-adselfservice-plus/)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1756/>

