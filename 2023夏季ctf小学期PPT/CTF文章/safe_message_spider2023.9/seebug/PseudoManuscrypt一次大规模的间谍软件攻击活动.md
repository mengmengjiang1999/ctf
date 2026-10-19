**译者：知道创宇404实验室翻译组  
原文链接：<https://ics-cert.kaspersky.com/reports/2021/12/16/pseudomanuscrypt-a-mass-scale-spyware-attack-campaign/>**

2021年6月，Kaspersky ICS CERT 专家发现了一个恶意软件，其加载程序与 Manuscrypt
恶意软件有一些相似之处，Manuscrypt 是 Lazarus APT
组织的武器库的一部分。2020年，该组织在攻击不同国家的国防企业时使用了Manuscrypt。这些攻击在报告中被描述为[“Lazarus用ThreatNeedle攻击国防工业”](https://ics-cert.kaspersky.com/reports/2021/02/25/lazarus-targets-defense-industry-with-threatneedle/)。

奇怪的是，恶意软件的数据外泄通道使用了 KCP 协议的一个实现，这个实现以前只被看作是 APT41组织工具集的一部分。

我们将新发现的恶意软件命名为 PseudoManuscrypt。

PseudoManuscryptd的加载程序通过一个 MaaS 平台进入用户系统，这个 MaaS
平台在盗版软件安装档案中分发恶意软件。具体举例，PseudoManuscrypt 下载器是通过 Glupteba 僵尸网络安装的，Glupteba
僵尸网络的主要安装程序也是通过盗版软件安装程序分发平台发布的。这意味着，使用PseudoManuscrypt的攻击者所使用的恶意软件分发策略并没有显示出特定的目标。

在2021年1月20日至11月10日期间，卡巴斯基的产品在全球195个国家的35000多台电脑上阻止了 PseudoManuscrypt
恶意软件。如此大量的受攻击系统数量并不是 Lazarus 组织或 APT 组织攻击的特点。

攻击的目标包括大量的工业和政府组织，包括军事工业复合体的企业和研究实验室。

根据我们的遥测数据，至少有7.2%
受到了PseudoManuscrypt的攻击的计算机与工业控制系统有关，而这些系统被工程、智能建筑、能源、制造、建筑、公用事业和水管理等行业的组织所使用。

主要的 PseudoManuscrypt 模块具有广泛而多样的监视功能。它包括盗取 VPN
连接数据、记录按键、截取屏幕截图和视频、用麦克风录音、盗取剪贴板数据和操作系统事件日志数据(这也使盗取 RDP
认证数据成为可能)等等。从本质上讲，PseudoManuscrypt的功能几乎为攻击者提供了对受感染系统的完全控制。

## 技术细节

### 识别加载程序.一般信息

2021年6月，Kaspersky ICS CERT 专家发现了一系列针对全球组织的攻击，包括政府组织和工业企业。

最初，当它用来检测 Lazarus APT
的活动触发防病毒解决方案的检测逻辑时，这个恶意软件被检测到。然而，整体情况太不寻常，不能将恶意行为与Lazarus联系起来。具体来说，PseudoManuscrypt恶意软件至少攻击了35,000个系统，这不是定向攻击的特征。

研究表明，攻击中使用的恶意软件从系统注册中心加载有效负载并解密。对于每个受感染的系统，有效负载在注册表中的位置是唯一的。

新发现的恶意软件加载程序与 Manuscrypt 恶意软件使用的加载程序有一些相似之处。2020年，Lazarus 组织使用 Manuscrypt
来攻击不同国家的国防企业。

两个恶意程序都从系统注册表加载并解密有效负载; 在这两种情况下，都使用 CLSID
格式的特殊值来确定有效负载在注册表中的位置。两个恶意程序的可执行文件实际上有相同的导出表:

[![img](https://images.seebug.org/content/images/2021/12/21/1640073820000-1cetyd.png-w331s)](https://ics-cert.kaspersky.com/wp-content/uploads/sites/6/2021/12/2112-pseudomanuscrypt-1.png) _两个恶意程序导出表的比较_

此外，这两个恶意程序使用类似的可执行文件命名格式:

[![img](https://images.seebug.org/content/images/2021/12/21/1640073821000-2xyhxc.png-w331s)](https://ics-cert.kaspersky.com/wp-content/uploads/sites/6/2021/12/2112-pseudomanuscrypt-2.png) _可执行文件名_

为了强调新发现的恶意软件与 Manuscrypt 的相似性，同时又没有其他东西可以将其与 Lazarus 组织联系起来，我们决定将其命名为 Trojan
PseudoManuscrypt。

### 系统感染

PseudoManuscrypt
加载程序通过许多其他恶意文件的安装和创建许多不同进程的复杂链路进入用户系统。这些链路是多种多样的，但他们都开始伪造盗版软件安装档案。档案名称包含不同类型和用途的软件的案例，例子如下:

    
    
    microsoft_office_365_july_keygen_by_keygensumo.zip
    windows_10_pro_full_keygen_by_keygensumo.zip
    adobe_acrobat_v8_0_keygen_by_keygensumo.zip
    garmin_1_serial_keygen.zip
    call_of_duty_black_ops_keygen_by_keygensumo.zip
    kaspersky_antivirus_keys_july_keygen_by_keygensumo
    solarwinds_broadband_engineers_keymaker.zip
    modscan32_v8_a00_crack.zip

值得注意的是，这些档案中包括专门针对 ICS 的软件的伪装安装程序，例如一个创建一个 MODBUS 主设备以接收来自 PLC
的数据的应用程序，以及一些更通用的软件，这些软件仍然用于 OT 网络，例如一个供网络工程师和系统管理员使用的 SolarWinds 工具的密钥生成器。

[![img](https://images.seebug.org/content/images/2021/12/21/1640073822000-3tepub.png-w331s)](https://ics-cert.kaspersky.com/wp-content/uploads/sites/6/2021/12/2112-pseudomanuscrypt-3.png)
_搜索引擎结果中包含安装程序的恶意网页_

用于分发此类安装程序的资源可以在搜索引擎结果页面的顶部位置找到。这表明攻击者正在积极地为这些资源执行搜索引擎优化。

### 执行流程

PseudoManuscrypt安装的过程中，不同的恶意程序的执行流程有许多可能的变化。

除了本文分析，恶意软件安装程序还下载并执行大量其他恶意程序，包括间谍软件、后门、加密货币挖掘程序和广告软件。

在每个阶段，我们检测到大量不同的dropper安装和模块下载，数据盗窃功能复制在不同的模块且每个模块使用自己的命令和控制服务器。这可能表明安装程序是由攻击者通过
MaaS 平台提供的，可能提供给不同恶意活动的众多运营商，其中之一显然是PseudoManuscrypt分发活动。

下面显示的示例和图片说明了安装 pseudonuscrypt 的进程链。

#### 变体1

[![img](https://images.seebug.org/content/images/2021/12/21/1640073822000-4yjght.png-w331s)](https://ics-cert.kaspersky.com/wp-content/uploads/sites/6/2021/12/2112-pseudomanuscrypt-4.png) _执行流程，变体1_

在第一种变体中:

  * 文件密钥.bat是从伪造安装程序中提取的，
  * 密钥.bat执行Keygen-step-4.exe（e41826b342686c7f879474c49c7eed98），
  * Keygen-step-4.exe安装并执行flash player.exe（2aab0ec738374db4e872812a84a0bc11），
  * flashplayer.exe安装并执行2.exe（8b9f6b0c98c0afdd75c2322f1ca4d0e8）
  * 文件2.exe 使用链接 hxxps://google [ . ] diragame [ . ] com/userf/3002/gogonami.exe 下载主要的PseudoManuscrypt 模块--game.exe (0001759655eacb4e57bdf5e49c6e7585)。

#### 变体2

[![img](https://images.seebug.org/content/images/2021/12/21/1640073823000-5teykw.png-w331s)](https://ics-cert.kaspersky.com/wp-content/uploads/sites/6/2021/12/2112-pseudomanuscrypt-5.png) _执行流程，变体2_

在第二种变体中:

  * 文件main_setup_x86x64.exe（1fecb6eb98e8ee72bb5f006dd79c6f2f）是从伪造安装程序中提取的，
  * main_setup_x86x64.exe安装并执行setup_installer.exe（5de2818ced29a1fedb9b24c1044ebd45），
  * setup_installer.exe安装并执行setup_install.exe（58EFF6FA04A8D7201AB19170785CE85）。
  * setup_install.exe安装并执行文件metina_8.exe（839e9e4d6289eba53e40916283f73ca6）。
  * 文件metina _ 8.exe 提取并执行PseudoManuscrypt-crack.exe (89c8e5a1e24f05ede53b1cab721c53d8)。

这种变体包含 Glupteba 基础设施和恶意软件安装程序(例如 setup _ install.exe)。自2011年以来，研究人员已经知道了
Glupteba
僵尸网络。它是一个多模块平台，在不同的时间段下载广告软件、间谍软件、加密货币挖矿恶意软件、勒索软件、垃圾邮件模块和其他常见的与网络犯罪活动相关的软件。Glupteba平台相当复杂，包括许多不同的模块，例如利用各种漏洞，包括利用路由器以及
rootkit。这就是为什么 rootkit，EternalBlue 漏洞的模块，以及其他 Glupteba 模块会通过 Glupteba
僵尸网络被PseudoManuscrypt感染。

在 BitDefender
描述的另一个变体中，PseudoManuscrypt安装程序(8acd95006ac6d1eabf37683d7ce31052)是使用链接`hxxps://jom[.]diregame[.]live/userf/2201/google-game.exe`下载的。根据我们的遥测数据，至少在2021年5月17日下载就开始了。值得注意的是，在不同的时间段，这个链接可以用来下载不同组织的恶意软件。

### 搜索恶意软件的其他组件

在搜索该恶意软件的其他组件和版本的过程中，我们找到了100多个不同版本的 PseudoManuscrypt 加载程序。

根据我们的遥测数据，本文所描述的加载器变体的大规模分发始于2021年5月10日。然而，早在2021年3月27日，早在攻击开始之前，它的早期变体就被发现了。

三月份发现的大多数文件都是测试版本。开发人员一个接一个地删除了恶意程序的部分代码，显然是想通过防病毒解决方案找出代码的哪些部分触发了检测。

大约在同一时间，恶意软件的开发者添加了 VirtualAlloc 函数的动态导入。该函数用于分配存储负载所需的内存，负载从系统注册表加载。

奇怪的是，一些加载程序的测试版本在可执行文件的元数据字段中包含注释。这些注释是用中文写的，表明恶意软件开发者可能会说和写中文:

[![img](https://images.seebug.org/content/images/2021/12/21/1640073823000-6rktwv.png-w331s)](https://ics-cert.kaspersky.com/wp-content/uploads/sites/6/2021/12/2112-pseudomanuscrypt-6.png) _恶意软件的可执行文件中的元数据_

### 恶意软件的主要组成部分

最后，我们识别出了PseudoManuscrypt的主要模块，其功能包括在系统上安装恶意软件，并包含一个有效载荷，由此我们可以知道攻击者感兴趣的数据类型。

#### 安装

恶意软件的主模块将其代码写入HKEY_LOCAL_MACHINE\SOFTWARE\Classes\CLSID密钥中的特殊注册表值。值名称(CLSID
值)对于每个系统都是唯一的，因为它是使用注册表键HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography\MachineGuid生成的，其中包含系统的唯一标识符。恶意程序的代码以加密的形式存储在系统注册表中。

接下来，恶意软件提取，到`% TEMP%`文件夹或`% windr%`文件夹(取决于恶意软件的修改) ，加载程序组件是一个 DLL 库，在`[0-Z
]{10}.tmp`格式中有一个随机文件名，例如，`I59RFRLY9J.tmp`。

为了确保有效负载在系统启动后自动执行，木马创建了一个服务，该服务将加载器组件作为其可执行文件。在最早发现的恶意软件样本中，由恶意软件创建的服务名为
AppService。

最后，这个恶意软件通过修改注册表关键字HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows
Defender\Exclusions\Paths，将自己加入到 Windows Defender 防病毒解决方案的排除列表中。

随后，在系统重启后，恶意软件加载程序被执行。使用 MachineGuid
密钥的值来确定有效负载在系统注册表中的位置，加载程序加载、解密并执行恶意软件的主要组件。

[![img](https://images.seebug.org/content/images/2021/12/21/1640073824000-7uithh.png-w331s)](https://ics-cert.kaspersky.com/wp-content/uploads/sites/6/2021/12/2112-pseudomanuscrypt-7-en.png) _恶意软件的安装和执行_

#### 破坏性活动，第一版

第一个需要识别的PseudoManuscrypt主模块的变体包括几个模块，这些模块的共同目标是从受害者的计算机中窃取机密信息。

1.键盘记录器。使恶意软件能够拦截用户在键盘上按下的键的代码。除了密钥代码，恶意软件还记录了输入数据的应用程序窗口的名称，以及输入信息的日期和时间。攻击者从其他恶意软件-Fabookie (Trojan.Win32.Fabookie) 借用这个恶意组件，Fabookie有几个模块用于窃取各种服务和网站的身份验证凭证。

作者只借用了 Fabookie
的键盘记录器模块，而忽略了为以最快的方式将攻击货币化而设计的模块，例如，从网页中窃取银行信息的模块。这为我们提供了一个视角，尽管是间接的，来研究攻击目标。

2.从剪贴板中窃取数据。使攻击者能够截获在受感染系统上工作的用户复制的信息

3.窃取 VPN 连接数据。该恶意软件获取 Windows 服务文件的内容，这些文件用于在被感染系统上配置的 VPN 连接上存储数据:

    
    
    %UserProfile%\Application Data\Microsoft\Network\Connections\pbk\rasphone.pbk
    %ProgramData%\Microsoft\Network\Connections\pbk\rasphone.pbk

木马试图从上述档案中提取以下资料:

  * 要连接的服务器的地址
  * 登录账号和密码，如果已经被保存了的话

值得强调的是，恶意软件的不同组成部分同时运作，为攻击者提供来自不同来源的信息。攻击者可以将这些信息组合在一起并使用所有这些信息。

例如，恶意软件可以从文件 rasphone.pbk 中获取以连接参数形式保存的 VPN
服务器地址。同时，键盘记录器模块可以截获连接所需的登录名和密码。如果用户使用剪贴板复制连接参数，恶意软件的相关模块将截获数据。

4.除了窃取 VPN 连接数据之外，PseudoManuscrypt 的功能还包括读取 Windows
应用程序、系统和安全事件日志。我们不能确定攻击者使用操作系统日志文件中的数据来做什么，但是理论上，它可以用来(与其他位的
PseudoManuscrypt功能一起)为 RDP 窃取身份验证数据。这看起来很合理，因为恶意软件具有盗取 VPN 证书的能力

5.录制连接到被感染系统的麦克风的声音。这个功能是在恶意软件命令和控制服务器的命令下激活的。

#### 破坏性活动，第二版

恶意软件的第二个变体在2021年7月被发现。攻击者已经增加了扩展间谍功能的变体。增加了以下模块:

1.从电脑屏幕上捕捉视频。该功能与其他用于截取信息的模块一起工作，如键盘记录器和从剪贴板窃取数据的模块。捕获屏幕视频使攻击者能够看到用户填写的字段和窗口，以及跟踪光标的移动，看到用户用鼠标点击的区域。值得一提的模块特性包括透明窗口支持(aero
peek 技术)和使用 GNU GPL XviD 1.3.0编解码器的视频压缩。

2.从亚洲流行的 QQ 和微信消息应用程序中窃取身份验证凭证。

3.收集详细的系统信息: Windows 版本、构建编号、 servicepack、安装更新信息和 Windows
版本，以及系统的角色，例如，系统是否执行网域控制器功能。

4.收集网络连接数据。该恶意软件收集网络适配器的名称，以及连接类型信息(有线连接、 Wi-Fi、光纤连接等)。

5.禁用防病毒解决方案。该恶意软件试图获得 SeDebugPrivilege 特权并终止以下安全解决方案进程:

    
    
    sepWscSvc.exe
    HipsTray.exe
    UnThreat.exe
    DF5Serve.exe
    DefenderDaemon.exe
    PowerRemind.exe
    SafeDogSiteIIS.exe
    SafeDogTray.exe
    SPIDer.exe
    f-secure.exe
    avgwdsvc.exe
    BaiduSdSvc.exe
    ServUDaemon.exe
    1433.exe
    vsserv.exe
    remupd.exe
    PSafeSysTray.exe
    AliIM.exe
    mssecess.exe
    MsMpEng.exe
    QUICK HEAL
    QUHLPSVC.EXE
    V3Svc.exe
    patray.exe
    AYAgent.aye
    Miner.exe
    TMBMSRV.exe
    knsdtray.exe
    K7TSecurity.exe
    QQPCTray.exe
    ksafe.exe
    rtvscan.exe
    ashDisp.exe
    avcenter.exe
    kxetray.exe
    egui.exe
    Mcshield.exe
    RavMonD.exe
    KvMonXP.exe
    360sd.exe
    360tray.exe
    DR.WEB
    cfp.exe
    DUB.exe
    avp.exe

该恶意软件还会删除属于安全解决方案的服务的注册表项，这些服务的名称包含以下子字符串:

    
    
    Symantec
    UnThreat
    Defender
    PowerShadow
    QuickHeal
    F-Secure
    BitDefender
    Windows Defender
    1433
    NOD32

6.收集有关在 TCP 和 UDP 端口上接受网络连接的进程的信息

7.PseudoManuscrypt有一个功能会删除一个名为“TestDown”的文件，该文件与恶意程序位于同一文件夹中，然后从浏览器的缓存中清除URL地址`htt[p]://sw.bos.baidu.com/sw-search-sp/software/df60f52e0e897/qqpcmgr_12.7.18996.207_1328_0.exe`
，再次从上述URL地址下载文件，以替换删除的文件“TestDown”，并将新创建的文件的属性设置为“hidden”和“system”。

8.清除 Windows 应用程序、安全性和系统事件日志

9.将从恶意软件C2服务器接收到的数据写入系统文件
`%System32%\drivers\etc\hosts`，从而使攻击者能够将用户重定向到恶意网络资源或阻止对选定网站的访问

10.在C2服务器和恶意软件之间交换文本信息。恶意软件可以通过聊天打开一个窗口。

新的PseudoManuscrypt版本的服务以“ iexplore”的名称安装在系统中，显示名称为“ System Remote Data
Simulation Layeerr”。新的恶意软件版本的功能还包括更新其可执行文件，并根据恶意软件C2服务器的命令从系统中删除自己。

奇怪的是，其中一个恶意软件样本使用 IP
地址192.168.1.2作为代理服务器。这可能表明，在某些情况下，攻击者根据受害者使用的特定网络结构准备了恶意软件样本。

在新版本的 PseudoManuscrypt 中，攻击者还添加了别的功能，能将用户按下的密钥代码写入本地日志文件:`% System32%
9cda11af69ab0a2b6a9167f7131e7b93.key`。

最后，新版本的木马在连接到恶意软件C2服务器时发送以下 HTTP 头信息:

    
    
    HTTP/1.1
    Accept: image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, application/x-shockwave-flash, application/vnd.ms-excel, application/vnd.ms-powerpoint, application/msword, */*
    Accept-Language: zh-cn
    Accept-Encoding: gzip, deflate
    User-Agent:Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)
    Connection: Close
    Cache-Control: no-cache

可以看出，恶意软件告诉服务器，首选答复语言是中文。

#### 向攻击者发送数据

恶意软件收集的数据被发送到恶意软件命令控制服务器。在我们的研究过程中，确定了四个这样的服务器: `email.yg9[.]me`,
`google.vrthcobj[.]com`, `toa.mygametoa[.]com` 和 `tob.mygametob[.]com`。

KCP 协议用于连接到服务器。根据它的开发者的说法，该协议比 TCP 快10%-20% 。攻击者使用了 KCP 协议的特定实现。

奇怪的是，根据 FireEye的一份[报告](https://www.fireeye.com/blog/threat-research/2020/03/apt41-initiates-global-intrusion-campaign-using-multiple-exploits.html)，PseudoManuscrypt使用的 KCP
库也被apt41组织利用，来攻击各行各业的工业组织，包括工程和国防工业企业。除了上面提到的两种情况，我们对恶意软件集合的分析没有发现这个库被用于其他恶意软件。

一些被识别出来的恶意软件样本也使用一个名为 d.diragame. com 的恶意软件专有服务器来发送新系统感染的信息。我们认为这可能是一个 MaaS
平台的统计数据收集机制。

## 受害者

在2021年1月20日至11月10日期间，卡巴斯基产品在全球195个国家的35000多台电脑上阻止了 PseudoManuscrypt。

下面的图表显示了已阻止 PseudoManuscrypt
的计算机数量的日常变化。图表上的两个明显的激增——3月27日和5月15日——对应的是新的PseudoManuscrypt版本发布/分发的开始日期。

[![img](https://images.seebug.org/content/images/2021/12/21/1640073824000-8bjqlu.png-w331s)](https://ics-cert.kaspersky.com/wp-content/uploads/sites/6/2021/12/2112-pseudomanuscrypt-8.png)
_每天检测到PseudoManuscrypt的系统数量_

阻止的计算机里，至少有7.2% 的计算机是 ICS 计算机。

[![img](https://images.seebug.org/content/images/2021/12/21/1640073824000-9ukacs.png-w331s)](https://ics-cert.kaspersky.com/wp-content/uploads/sites/6/2021/12/2112-pseudomanuscrypt-9-en.png)
_工业系统在受攻击计算机系统中所占的份额_

如下图所示，近三分之一(29.4%)的非 ics 计算机位于俄罗斯(10.1%) ，印度(10%)和巴西(9.3%)。

[![img](https://images.seebug.org/content/images/2021/12/21/1640073825000-10agqml.png-w331s)](https://ics-cert.kaspersky.com/wp-content/uploads/sites/6/2021/12/2112-pseudomanuscrypt-10-en.png) _不同国家非 ics
计算机受到PseudoManuscrypt攻击的百分比_

非 ICS 计算机受到PseudoManuscrypt攻击的国家分布情况与 ICS
计算机相似。然而，一些国家，其中大多数位于亚洲和中东，在被攻击的ICS计算机的国家排名中所占百分比显著高于(按1.5-2的系数)被攻击的非ICS计算机的国家排名中所占百分比。

[![img](https://images.seebug.org/content/images/2021/12/21/1640073825000-11gzeqg.png-w331s)](https://ics-cert.kaspersky.com/wp-content/uploads/sites/6/2021/12/2112-pseudomanuscrypt-11-en.png)
_被PseudoManuscrypt攻击的 ICS 计算机百分比，按国家分列_

有相当一部分(31.5%)的工业系统显然是用于工程，即开发和启动各种工业产品的生产，以及用于国防和能源工业等不同行业的 ICS 开发和集成。这包括用于3 d
建模和物理模拟的计算机，以及安装了创建数字双胞胎软件的计算机。

此外，在阻止了PseudoManuscrypt的电脑中，约有12.5% 属于智能建筑系统(包括视频监控、访问控制系统、通知系统等) ，1.8%
属于能源部门，2.1% 属于各种制造设施，0.7% 属于建筑(结构工程) ，0.1% 属于公用事业电脑，0.1% 属于用于水处理系统。

在阻止了PseudoManuscrypt的电脑中，大约51.2% 的工业计算机是通用 ICS，我们还不敢肯定，将其与特定行业联系起来。

[![img](https://images.seebug.org/content/images/2021/12/21/1640073825000-12ylboz.png-w331s)](https://ics-cert.kaspersky.com/wp-content/uploads/sites/6/2021/12/2112-pseudomanuscrypt-12-en.png)
_工业系统中被PseudoManuscrypt攻击的分布情况_

除以上提到的外，攻击受害者还包括与军事工业复合体有联系的企业(如研究实验室)。

另一个奇怪的事实是，根据来自公共来源的信息判断，一些被“PseudoManuscrypt”攻击的组织与遭受卡巴斯基报告所述攻击的组织有商业和生产联系:
“[Lazarus用ThreatNeedle攻击国防工业](https://ics-cert.kaspersky.com/reports/2021/02/25/lazarus-targets-defense-industry-with-threatneedle/)”。

## 关于攻击者

我们已经发现的一系列线索有利于研究攻击者的起源或关系:

  1. 一些恶意软件样本在可执行文件元数据中包含中文注释
  2. 数据通过一个以前只用于中国组织 apt41的恶意软件的库发送到攻击者的服务器
  3. 当连接到C2服务器时，恶意软件指定中文为首选语言
  4. 这个恶意文件包含连接到百度的代码，百度是中国流行的文件云存储
  5. 开发者在每天上载新版本的PseudoManuscrypt加载器的时间，是在 GMT + 8时区的上午11时至下午7时之间，而多个东亚及亚太国家位于该时区内

[![img](https://images.seebug.org/content/images/2021/12/21/1640073826000-13argwz.png-w331s)](https://ics-cert.kaspersky.com/wp-content/uploads/sites/6/2021/12/2112-pseudomanuscrypt-13-en.png)
_攻击者恶意软件测试活动频次_

## 总结

尽管我们收集和分析了大量的数据，但是在我们看来，我们的许多发现仍然无法解释，也不符合任何已知的方案。

因此，我们不能肯定地说，这场攻击是犯法的逐利行为，还是与某些政府的利益相关的行为。然而，受到攻击的系统来自不同国家知名组织的计算机，这一事实使我们评估威胁程度较高。

受到攻击的系统数量很大，我们不确定重点在具体的哪个产业组织。然而，由于全球有大量的 ICS
计算机(仅根据我们的遥测数据就有数百台——实际上很可能还有更多)在这场运动中受到攻击，这种威胁当然值得负责车间系统的安保和安全及其持续运行的专家给予最密切的关注。

大量的工程计算机受到攻击，包括用于3 d 和物理模型的系统，数字双胞胎的开发和使用使工业间谍活动成为可能。

我们还没有结束我们的调查，并将持续发布新的发现的消息

## IOC

### 校验和(MD5)

在本节中，我们列出了那些我们认为用于攻击的文件的 md5散列，但没有列出恶意软件测试样本的 md5散列

    
    
    1fecb6eb98e8ee72bb5f006dd79c6f2f
    4da2c2abcf1df9749b64b34160bd3ebf
    5dc7fbf2141f7dfe5215c94895bf959c
    70e9416833b2f933b765042f8e1ea0bc
    8074f73f7742309b033676cd03eb0928
    8ae40c8418b2c36b58d2a43153544ddd

### 文件路径

    
    
    %WinDir%\System32\[0-Z]{10}.tmp e.g. I59RFRLY9J.tmp
    %TEMP%\[0-Z]{10}.tmp e.g. I59RFRLY9J.tmp
    %WinDir%\System32\9cda11af69ab0a2b6a9167f7131e7b93.key

### 安全解决方案

    
    
    Trojan.Win64.Manuscrypt.do

### URL 地址

    
    
    hxxp://email.yg9[.]me
    hxxp://google.vrthcobj[.]com
    hxxp://d.diragame[.]com
    toa.mygametoa[.]com
    tob.mygametob[.]com

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1790/>

