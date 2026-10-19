远程控制木马（Remote Access Trojans，简称为 RAT）是一种主流的恶意程序，它赋予了攻击者远程监控和控制受害者主机的能力。目前，基于
RAT
的攻击已经变得非常普遍，这对个人安全、企业安全、甚至国家安全构成严重威胁，包括个人账户、企业知识产权的窃取以及涉及政治目的的高级持续性攻击（Advanced
Persistent Threat）等，例如，Poison Ivy RAT 参与了 RSA SecurID 攻击以及针对化学公司的 Nitro
攻击；DarkComet RAT 参与了叙利亚激进分子攻击并在查理周刊枪击案中被用于恶意软件传播。Xtreme RAT
参与了针对美国、英国、以色列以及其它中东国家政府部门的攻击。

尽管基于 RAT 的攻击已经在全世界造成了巨大的危害，但是现阶段依旧缺乏对 RAT 的全面调研。本文将对大量真实世界的 RAT 进行调研，包括 RAT
的工作方式、具有的功能以及功能实现方式。具体地，本文首先描述了 RAT 攻击的基本工作流程，然后描述了收集大规模的真实世界的 RAT
家族的方法，最后对收集的 RAT 样本进行了动态分析和静态分析，并报告了关于这些 RAT 的重要发现。

##  ** **R**** ** **AT**** ** **的基本工作流程****

一个 RAT 工具包含两个个基本模块：RAT Stub 和 RAT Controller。当 RAT stub
被发送到受害者机器上（如钓鱼邮件）并且被安装后，攻击者就获得了受害者机器的完全控制权。而 RAT Controller
安装在攻击者机器上，其包含一个控制面板用于提供可视化的界面，攻击者通过简单的鼠标点击就能够控制 RAT Stub
在受害者机器上执行对应的恶意功能（键盘记录、录音和监控摄像头等）。值得注意的是，在收到 RAT Controller 的命令前，RAT Stub
会保持沉默，潜伏在受害者机器不做任何行为。图表1展示了一个 RAT Controller 控制面板的案例。

![1617784177_606d6d719c346883b6263.png!small?1617784179010](https://image.3001.net/images/20210407/1617784177_606d6d719c346883b6263.png!small?1617784179010)

图表 1 RAT Controller 控制面板的案例

##  ** **RAT 样本的收集****

由于 RAT Stub 的行为只能被 RAT Controller 触发，因此本文需要同时收集 RAT Stub 和 RAT
Controller。用户会将机器上的可疑程序上传到公开的病毒数据库（如
VirusTota）进行检测，因而病毒数据库包含大量恶意程序样本，这是样本采集最常见的一种数据来源。然而，像收集其他病毒样本一样从公开的病毒数据库收集大量的
RAT Controller 样本是不可行的。原因是 RAT Controller 安装在攻击者机器上，受害者机器上只安装了 RAT
Stubs，这导致病毒数据库只存在大量的 RAT Stubs样本，而缺乏对应的 RAT Controller 样本。

为了解决这个问题，本文发现在黑客论坛上， RAT Controller 经常会被破解和售卖，因而本文在黑客论坛上进行了充分搜索，共获取了 53 个 RAT
家族（具体描述见表1）。其中大多数 RAT 家族都是非常有名的，并且在很多安全事件中被使用。例如，Poison Ivy RAT（首次出现于 2006
年）参与了 RSA SecurID 攻击和针对化学公司的 Nitro 攻击；DarkComet RAT （首次出现于 2008
年）参与了叙利亚激进分子攻击并在查理周刊枪击案中被用于恶意软件传播。 XtremeRAT（首次出现于 2010
年）参与了针对美国、英国、以色列和其它中东国家政府部门的攻击。Adwind RAT（首次出现于 2012
年）参与了针对航空航天企业的攻击和针对丹麦公司的攻击。

 **编程语言**

|

 **RAT** **家族**

|

 **数量**  
  
---|---|---  
  
.NET based

(C#.NET and

VB.NET)

|

Back Connect

|

Mega

|

ctOs

|

24  
  
BXRAT

|

MLRAT

|

KilerRat  
  
Cloud Net

|

MQ5

|

L6-RAT  
  
Coringa

|

NanoCore

|

xRAT  
  
Imperium

|

NingaliNET

|

Vantom  
  
Imminent Monitor

|

NjRAT

|

SpyGate  
  
Quasar

|

Proton

|

Revenge  
  
Virus RAT

|

Comet RAT

|

D-RAT  
  
Delphi

|

Alusinus

|

Greame

|

Pandora

|

17  
  
CyberGate

|

NovaLite

|

Spycronic  
  
Dark Comet

|

Nuclear

|

Spy-Net  
  
  

|

  

|

  
  
  
  

|

Turkojan

|

Orion

|

Sub-7

|

  
  
  
Xena

|

Rabbit-Hole

|

Bozok  
  
DHRat

|

Xtreme

|

  
  
  
Java

|

Crimson

|

jSpy

|

Maus

|

5  
  
Frutas

|

Adwind

|

  
  
  
Visual Basic

(Native)

|

SkyWyder

|

HAKOPS

|

njworm

|

3  
  
C++

|

Babylon

|

ucuL

|

  

|

2  
  
Python

|

pupy

|

  

|

  

|

1  
  
MASM

|

Poison Ivy

|

  

|

  

|

1  
  
表 1 53 个 RAT 家族所使用的编程语言及其分布

除此之外，根据网上公开的白皮书、技术文档、RAT文件的创建时间等信息，本文识别了每个 RAT 家族的首次出现时间。图2列出了 53 个 RAT
家族的首次出现时间分布。

![1617784233_606d6da9979e449d84279.png!small?1617784234843](https://image.3001.net/images/20210407/1617784233_606d6da9979e449d84279.png!small?1617784234843)

图表 2 RAT 家族在首次出现时间轴上的分布

总之，本文收集了一组具有代表性的 RAT 家族样本（活跃于 1999 年至 2016 年的 53 个 RAT
家族），并且已经将样本在网络上公开，相信该组样本能够对其他研究者产生帮助。

##  ** **大规模**** ** **RAT 样本分析与关键发现****

通过对收集到的 RAT 家族样本进行静态程序分析和动态程序分析，本文获得了 4 个关键发现。接下来，本节将详细地描述每个关键发现，以及使用的分析方法。

###  **关键发现 1：RAT 开发者更倾向于使用高级编程语言。**

本文利用一个成熟的文件分析工具 Detect-It-Easy对每个 RAT 家族的 RAT Stub 进行了分析，识别了其使用的编程语言。

具体地，对每个 RAT 家族，本文通过 RAT Controller 生成了一个 RAT Stub，然后将这个 Stub 输入到 Detect-It-Easy 工具中。这个工具会自动地对 Stub 文件进行静态分析，并且从中识别出 Stub 使用的编程语言（如 C++、Delphi 和Java）。

表1 列出了每个 RAT 家族使用的编程语言。由表可知，基于 .NET 的编程语言（C# 和 VB.NET）和 Delphi 是最受欢迎的语言。原因在于
(1) 这些编程语言对运行时依赖没有要求（Delphi）或运行时依赖已经默认安装（.NET），所以编写出来的 RAT 就可以运行在绝大多数的 Windows
版本上。(2) .NET 和 Delphi 具有大量公开可用的编程库，基于这些库 RAT 开发者可以快速地实现 RAT 的功能。例如，本文发现 Vantom
和 Mega RAT 使用了第三方公开的库 DirectX.Capture 来实现录音。相比之下，其它的编程语言，如 Java、Python 和 C++
很少被使用，原因在于这些编程语言要么需要安装额外的运行时依赖，要么无法适用于敏捷开发。

###  **关键发现 2：RAT 常常配备了数十种潜在恶意功能（Potential Harmful Functions）。**

在此调研中，本文获取了 53 个 RAT 家族的 PHF 列表以及每个功能出现的频率。前文提到了每个 RAT
家族拥有一个可视化的控制面板，该面板清楚明确地列出了 RAT 可用的 PHF。因此，遍历 53 个 RAT 家族的控制面板就能够获得一个完整的 PHF
列表及其对应的出现频率。值得注意的是，无论是白皮书、博客，还是研究经验都没有发现任何一个 PHF
能够不通过控制面板触发。因此，本文通过此方式获取的结果是准确的。表2列出了 RAT 常用的几个功能。表格的第三列（出现频率）表示在所有 RAT
家族中某个特定 PHF 出现的频率。由表可知，约 49% 到 85% 的 RAT 家族具有这些功能。

 **潜在恶意功能（** **PHF** **）**

|

 **描述**

|

 **出现频率**  
  
---|---|---  
  
Key Logging

|

记录受害者的键盘输入

|

81.13%  
  
Remote Shell

|

远程打开一个 shell，并允许攻击者执行

|

81.13%  
  
Download and Execute

|

远程打开一个 shell，并允许攻击者执行

|

84.90%  
  
Remote Camera

|

远程访问受害者的摄像头

|

66.03%  
  
Audio Record

|

远程记录受害者的麦克风

|

49.05%  
  
表 2 RAT 配备的常见潜在恶意功能（PHFs）

###  **关键发现 3：不同的 RAT 家族在实现同一个 PHF 时使用了类似的实现方式。**

在此调研中，本文识别了 5 个常用 PHF（如表2 所示）的实现方式。由于识别 PHF 的实现方式需要人工参与，同时考虑到 RAT 具有数十种
PHF，因此完成这个实验需要大量人力，于是本文选择了 RAT 家族中出现频率高的 5 个 PHF。

具体地，由于本文同时拥有 RAT Controller 和 Stub，因此通过点击 RAT Controller 控制面板对应的 PHF
按钮，日志采集器能够收集到每个 PHF 的动态执行数据（如 Windows API 和系统调用）。接下来，手工对这些动态数据进行分析，观察每个 PHF
调用了哪种 Windows API。新的 API 一旦出现就表明 PHF 可能使用了一种新的实现方式。然后再仔细阅读关于新的 API 的文档，确认该 API
是否能够用于 PHF 的实现。如果没有新的 API，就将该动态执行数据归类到已经发现的实现方式上。实验结果表明不同的 RAT
家族在使用类似的方式来实现相同的 PHF。以 Key Logging 为例，表3 列出了 3
种实现方式，表格的第三列表示某一种实现方式的出现频率。由于操作系统并不会提供大量不同的 API 来实现同一个特定的功能，因此此发现是合理的。其他 PHF
的实现方式总结在表4-7中展示。

 **实现方式**

|

 **描述**

|

 **出现频率**  
  
---|---|---  
  
K1

|

RAT 通过调用 NtUserSetWindowsHookEx 注册了一个消息回调函数，当用户敲击键盘时，回调函数就会接收到被敲击的字符的虚拟码。

|

53.65%  
  
K2

|

RAT 不停地调用 NtUserGetAsyncKeyState 来轮询当前的键盘状态。

|

39.02%  
  
K3

|

RawInput 是获取用户输入的另外一种方式， RAT 通过调用

NtUserGetRawInputData 来获取用户输入。

|

7.33%  
  
表 3 RAT 的 Key Logging 实现方式总结

 **实现方式**

|

 **描述**

|

 **出现频率**  
  
---|---|---  
  
S1

|

RAT 首先调用 CreatePipe 和 CreateProcess 来创建具有重定向输入和输出功能的 cmd.exe 进程。然后，RAT 调用
WriteFile 和 PeekNamedPipe 将命令发送到 cmd.exe，并获取 cmd.exe 的输出。

|

100%  
  
表 4 RAT 的 Remote Shell 实现方式总结

 **实现方式**

|

 **描述**

|

 **出现频率**  
  
---|---|---  
  
C1

|

利用 DirectShow 访问远程摄像头。DirectShow 是 Windows 操作系统的一个多媒体框架。RAT 首先调用
CoCreateInstance 和 CreateClassEnumerator

来查找视频输入设备。然后， RAT 调用多个 API （如SetFiltergraph、SetOutputFileName 等）来进行一些配置工作。最后，
RAT 调用 RenderStream 来捕获摄像头视频。

|

69.69%  
  
C2

|

VFW 是 Microsoft 开发的另一个多媒体框架，该框架允许 Windows 应用程序播放和编码数字视频。 RAT 首先调用
capGetDriverDescription 检索视频输入设备的信息，然后调用 capCreateCaptureWindow 创建捕获窗口。最后， RAT
调用 SendMessage 将消息发送到创建的窗口来连接和捕获摄像头。

|

30.31%  
  
表 5 RAT 的 Remote Camera 实现方式总结

 **实现方式**

|

 **描述**

|

 **出现频率**  
  
---|---|---  
  
A1

|

利用内置的 Waveform-Audio 接口捕获音频。 RAT 首先调用 waveInOpen 来打开音频输入设备。然后， RAT 调用
waveInPrepareHeader 和 waveInAddBuffer 为音频数据准备缓冲区。最后，调用 waveInStart 开始捕获音频。

|

54.54%  
  
A2

|

媒体控制接口（Media Control Interface ，简称为 MCI ）是另一个内置接口，该接口提供录制多媒体设备的标准命令。 RAT首先使用
mciSendCommand 发送一条命令 MCI OPEN 来打开音频输入设备，然后调用相同的API mciSendCommand 发送另一个命令 MCI
RECORD来开始音频记录。

|

45.46%  
  
表 6 RAT 的 Audio Record 实现方式总结

 **实现方式**

|

 **描述**

|

 **出现频率**  
  
---|---|---  
  
D1

|

RAT 首先调用 InternetOpen 来初始化 Windows Internet（WinINet）功能。然后，调用 InternetOpenUrl 和
InternetReadFile 来打开和下载给定 URL 的文件。最后，调用 ShellExecute 或 CreateProcess 来执行下载的文件。

|

37.5%  
  
D3

|

Windows 上内置的 .NET 框架还提供用于处理 Web 资源的 API。RAT通过调用 WebClient.DownloadFile 或
Network.DownloadFile 可以轻松地从某个 URL 下载文件。然后，调用 Process.start 来执行下载的文件。

|

47.5%  
  
D4

|

RAT 调用 socket 创建套接字对象。然后，调用 connect、send 和 recv 来连接套接字和下载文件。最后，调用 ShellExecute
或 CreateProcess 来执行下载的文件。

|

2.5%  
  
表 7 RAT 的 Download & Execute 实现方式总结

理解一个 PHF 的实现方式对于攻防演练中的红队是非常重要的。但是，由于缺乏对 RAT 的调研，即便是最先进的攻击模拟工具也存在无法模拟 RAT
攻击，或只能模拟一种实现方式的问题。为了填补这个空缺，本文研究了每个实现方式的代码实现。图3提供了键盘记录（Key Logging）这个 PHF 的 3
种实现方式的伪代码。本文相信将这些调研获得的情报集成到现有的攻击模拟工具中，能够帮助其他 RAT 研究人员更好地模拟 RAT 攻击。

![1617784374_606d6e3678b03d1b55296.png!small?1617784376163](https://image.3001.net/images/20210407/1617784374_606d6e3678b03d1b55296.png!small?1617784376163)

图表 3 Key Logging三种实现方式的伪代码

###  **关键发现 4：90% 的 RAT 只能运行在 Windows 平台。**

通过分析 RAT Stub 的文件类型，调研发现 90% 的类型都是 Windows 平台独有的类型，如 Windows PE 格式、Windows
批处理格式等。这些格式的文件只能运行在Windows 平台上，这表示大多数的 RAT 的攻击目标只有 Windows 平台。由于 Windows
依旧是市场份额最大的操作系统，尤其是对企业环境来说，因此这个发现是合理的。

本文作者：杨润青, 陈许同, 陈焰@奇盾安全

