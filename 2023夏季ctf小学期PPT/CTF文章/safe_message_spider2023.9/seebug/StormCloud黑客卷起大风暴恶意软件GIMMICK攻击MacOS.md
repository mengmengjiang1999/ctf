**译者：知道创宇404实验室翻译组  
原文链接:<https://www.volexity.com/blog/2022/03/22/storm-cloud-on-the-horizon-gimmick-malware-strikes-at-macos/>**

![img](https://images.seebug.org/content/images/2022/03/23/1648015005000-1pnqke.png-w331s)

2021年底，Volexity 发现了一起入侵事件，发生在网络安全监控服务的局部环境。Volexity 检测到一个运行
**[frp](https://github.com/fatedier/frp)**
的系统，或称为快速反向代理，随后不久检测到内部端口扫描。这个流量被确定为未经授权的，该运行 macOS 11.6(Big Sur)的 MacBook
Pro系统，被分离出来进行进一步的分析。Volexity 能够运行 [Surge
Collect](https://www.volexity.com/products-overview/surge/)
以获取系统内存(RAM)并从机器中选择需要的文件进行分析。因而 一个macOS 变种的恶意软件植入被发现， Volexity 称其为 **GIMMICK**
。在之前的几个事件中，Volexity 都遇到过 Windows 版本的恶意软件。

中国间谍黑客 [Storm Cloud](https://www.volexity.com/blog/2020/03/31/storm-cloud-unleashed-tibetan-community-focus-of-highly-targeted-fake-flash-campaign/),以攻击亚洲各地的组织而闻名，他在定向攻击中使用了 GIMMICK。它是一个功能丰富、多平台的恶意软件组，使用公共云托管服务(如
Google Drive)作为命令控制(C2)通道。新发现的 macOS 变体主要使用 Objective c 编写，Windows
版本使用两种语言编写,.NET 和 Delphi。尽管使用的编程语言和针对的操作系统存在核心差异，但 Volexity
通过共享的C2架构、文件路径和所有变体使用的行为模式，判断两个变体是同款恶意软件。

![img](https://images.seebug.org/content/images/2022/03/23/1648015008000-2ucdgs.png-w331s)
图1. GIMMICK 工作流

这篇博文深入分析了GIMMICK的 macOS 变体，同时也展示了 Windows版本 变体的特点。Volexity
通过对受感染系统的内存分析发现了这个样本，并且从内存和磁盘中恢复了植入程序。文件名和安装路径对受害者系统来说是唯一的，并且以一种旨在与用户的工作性质相融合的方式进行了配置。此外，GIMMICK
被配置为只在工作日与其基于 Google drive 的 c2服务器通信，以便进一步融入目标环境中的网络通信。

Volexity 能够从硬盘获得的文件 SHA1散列是“ fe3a3e65b86d2b07654f9a6104c8cb392c88b7e8”。

与苹果密切合作，在他们的用户中加入了对 GIMMICK 恶意软件的防护。2022年3月17日，苹果向 XProtect 和 MRT
推出了新的签名，以阻止和删除
GIMMICK。虽然在默认情况下，用户可以通过验证“‘安装系统数据文件和安全更新’框在他们的设置中被选中”来确认他们是受到保护的([说明点此处](https://support.apple.com/guide/mac-help/get-macos-updates-mchlpx1065/mac))。

### 启动和初始化

在 macOS 上，GIMMICK 支持作为系统上的守护进程启动或由用户启动。如果直接由用户启动，它将通过植入一个包含内容的 PLIST
文件来安装自身作为启动代理，安装到 _/Users/ /Library/LaunchAgents_，如下所示。二进制、 PLIST
和代理的名称根据样本而有所不同。在 Volexity 观察到的案例中，植入物被设计成模仿目标用户通常启动的应用程序。值得注意的是，Volexity
发现的GIMMICK 的 Windows 版本没有想要建立自己的持久性。

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    
    <plist version="1.0">
    
    <dict>
    
    <key>Label</key>
    
    <string>com. /[applicationname].va.plist</string>
    
    <key>ProgramArguments</key>
    
    <array>
    
    <string>/Users/#####/Library/Preferences/[pathto/binary]>/</string>
    
    </array>
    
    <key>RunAtLoad</key>
    
    <true/>
    
    <key>StartInterval</key>
    
    <integer>30</integer>
    
    <key>ThrottleInterval</key>
    
    <integer>2</integer>
    
    <key>WorkingDirectory</key>
    
    <string>/Users/<removed>/Library/Preferences/[applicationname]string>
    
    </dict>
    
    </plist>

同样，植入程序提供了一个卸载函数，可以通过在命令行上添加参数“ uninstall”来实现。这会删除植程序物和所有相关文件，然后终止进程。

在初始化过程中，样本使用旋转加法算法解码恶意软件操作中至关重要的几段数据。

第一个解码循环产生一个 JSON 对象，其中包含OAuth2凭据，用于建立到 Google Drive 的会话。图2显示了一个 JSON 对象的例子:

![img](https://images.seebug.org/content/images/2022/03/23/1648015008000-3vzfzt.png-w331s)
图2. 一个示例 JSON 对象，其中包含使用 Google Drive 进行身份验证所需的凭据

第二个循环解码32字节的字符串“943c3743f72f06e58e60fa147481db83”。此字符串通过一个附加的转换阶段运行，该转换阶段一次将两个字符转换为数字表示形式，并将生成的字节写入缓冲区。在对[CCCrypt()](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/CCCrypt.3cc.html)
函数的多个调用中，这个缓冲区被用作 AES 密钥。

![img](https://images.seebug.org/content/images/2022/03/23/1648015009000-4qiicf.png-w331s)
图3. AES 密钥转换

最后的解码完成，其结果是一个200字节的配置数据二进制 blob对象，只有一些看似可见的数据边界。

![img](https://images.seebug.org/content/images/2022/03/23/1648015011000-5bgqjw.png-w331s)
图4: Config blob

除了这种数据混淆，以及对某些外部文件使用 AES 之外，恶意软件几乎不会尝试混淆系统中它的功能或它的存在。

### C2 协议

初始化后， GIMMICK恶意软件的操作是高度异步的。之前的 Windows 恶意软件变种已经使用
程序内部线程池技术来应对这个问题。技术是由`Delphi的 System.Threading.TThreadPool`和 `.NET的
System.Thread and System.Action`提供的。然而，macOS 的变种使用苹果的[Grand Central Dispatch
(GCD)](https://en.wikipedia.org/wiki/Grand_Central_Dispatch)技术来管理协议。此特性允许开发人员将任务分发到系统管理的线程池中，以便以后进行处理。这些任务被封装到称为[blocks](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ProgrammingWithObjectiveC/WorkingwithBlocks/WorkingwithBlocks.html)的自包含对象中，这些对象被安排在调度队列上进行处理。GCD的确切结构和执行细节相当复杂，超出了本文件的范围,dan
附录中提供了一些资源。

恶意软件中有三个自定义的 ObjectiveC 类,管理C2协议的关键方面: DriveManager、 FileManager 和
GCDTimerManager。

DriveManager有几个职责:

  * 管理 Google Drive 和代理会话。
  * 在内存中维护 googledrive 目录层次结构的本地映射。
  * 管理 Google Drive 会话上同步任务的锁。
  * 处理 Google Drive 会话的下载和上传任务。

根据恶意软件枚举命令文件的方式，谷歌驱动器似乎被每个受感染主机的目录填充。此目录的名称因平台而略有不同。Windows植入程序会生成一个独特的 GUID
作为其 ID，而 macOS 植入程序则使用苹果自己的 Hardware UUID。

FileManager 管理一个本地目录层次结构，其中包含C2信息和处于不同完成阶段的命令任务。一些旧版本的 GIMMICK
使用了略有不同的目录名称，但它们在最近的几个变体中保持了一致性。macOS
植入程序将这个层次结构存储在应用程序主[包]((https://developer.apple.com/library/archive/documentation/CoreFoundation/Conceptual/CFBundles/BundleTypes/BundleTypes.html)
的根目录中一个名为“ MGD”的目录中。目录结构中的每个文件夹都被指定用于在 c2进程中保存单一类型的文件。下表给出了所有目录及其用途。

**Name** | **解释** | **内容**  
---|---|---  
tmp | Temporary | 用于写入文件的临时安全位置; 此目录中没有检查文件的调度代码  
c | Credentials | 存储初始化期间解码的 AES 加密凭据 JSON  
e | Errors | 将错误日志存储为单独的文件; 错误报告为四位数的不透明整数值  
p | Proxies | 存储由主机和端口组成的代理定义文件，中间以“:”分隔  
u | Upload Command | 存储的 AES 加密的命令结果，等待上传  
d | Download Command | 存储挂起的下载命令文件，每个文件包含要下载的命令文件的Google Drive 路径  
ds D | Download Success | 下载的等待处理的AES加密命令文件的存储位置  
df | Download Failed | 失败的下载命令的临时位置，在可以重试或清除它们前放在这里  
l | List Command | 存储命令文件的挂起列表，这些文件指示Google Drive 目录  
ls | List Success | 存储包含要下载的远程 Google Drive 文件路径的临时列表文件  
lf | List Failed | T失败列表命令的临时位置，在可以重试或清除它们前放在此处  
  
并不是所有GIMMICK的变体使用所有的目录。例如，macOS 植入程序不使用“ df”目录，它创建但不访问“ lf”和“ p”目录。

GCDTimerManager 管理各种 GCD
对象，以确保植入程序的正常调度，并保存调度计时器的集合及其相应的块。该恶意软件创建了几个命名的调度队列，用于管理特定的与 c2相关的任务:

**名字** | **目的**  
---|---  
SendBaseinfoQueue | Regularly generates and sends a system reconnaissance
heartbeat message to the C2 containing the following: 定期生成并向
c2发送一个系统侦察信息，包含以下内容:Hardware UUID；Eth0接口的 MAC 地址；CPU 模型字符串；OS 版本字符串  
list_request_queue | 在“l”目录中生成一个列表请求文件，其中包含一个格式为“/”的路径  
ls_cmd_queue | 解析“ ls”目录中的文件，并为每一行写一个相应的下载命令文件到“ d”目录  
ReadCmdQueue 1. readcmdlet | 从“ ds”目录解密和解析文件，并执行包含在其中的命令，将结果保存到“ u”目录  
CredsCheck | 检查 Google Drive 会话是否超时，并在必要时重新进行身份验证  
DriveClearTrashQueue | 定期删除 Google Drive 的垃圾文件  
DriveDownQueue | 解析存储在“ d”中的文件，并将相应的文件从 Google Drive 下载到“ ds”目录  
DriveUploadQueue | 上传存储在“ u”目录中的反馈文件  
DriveFailUploadQueue | 第二次尝试上传失败的上传项目。第二次尝试无论结果如何，标记为成功。  
fileListQueue | 解析存储在“ l”目录中的文件，并为每个文件更新 Google Drive 的 DriveManager
目录映射，并生成要下载到“ ls”目录中的文件列表  
  
此外，GCDTimerManager
使用在初始化过程中解码的静态配置信息来设置植入程序的运作时间，限制可能引起防御者注意的连接。它在配置数据的最开始从字符串解析工作时间。这个字符串以一组由连字符分隔的单位数字开始，然后是两个冒号字符和两个由连字符分隔的两位数字。第一组数字表示恶意软件活动的日期，第0天是星期天。第二组两位数字表示活动时间范围。以“1-2-3-4-5:
: 00-23”的初始值为准，植入程序将在工作日上午12点至晚上11点激活ー这是图4所示的配置 blob 中的第一个数据。

### 命令的生命周期

由于恶意软件操作的异步特性，命令执行需要分阶段的方法。虽然每个步骤是异步执行的，但每个命令都遵循相同的步骤:

1.攻击者将加密的有效载荷上传到 Google Drive。

2.“list_request_queue”触发调度计时器

  * 将写入“ l”目录的新请求文件

3.“fileListQueue”触发调度计时器

  * 从“ l”目录读取列表请求
  * 从 Google Drive 会话更新 DriveManager 状态
  * 将列表文件拖放到“ ls”目录中

4.“ls_cmd_queue” 触发调度计时器

  * 从“ ls”目录解析列表文件
  * 为“ d”目录中的每个远程文件放入下载命令文件
  * 从“ ls”目录中删除列表文件

5.“DriveDownloadQueue” 触发调度计时器

  * 枚举“d”目录中的文件
  * 将下载的命令文件排队到“ ds”目录
  * 下载完成后，删除远程 Google Drive 文件和本地下载命令文件的队列

6.“ReadCmdQueue” 触发调度计时器

  * 从“ ds”目录读取和解密命令文件
  * 处理命令执行
  * 删除本地命令文件
  * 将加密的“反馈”文件写入“ u”目录

7.“DriveUploadQueue” 触发调度计时器

  * 枚举“u”目录中的文件
  * 将结果文件的上传排成队列
  * 上载完成后，对本地结果文件的删除进行排队

### 命令和反馈

命令作为“ds”目录中的加密文件到达系统，一旦使用植入程序的静态 AES 密钥解密，将生成 JSON 对象。命令解析器只读取四个 JSON 字段。

**Name** | **Type**  
---|---  
CMDType | Number  
content | String  
params | String  
savepath | String  
  
虽然每个命令 JSON 必须有一个CMDType 字段，但是所需的字段因命令而异。下表总结了可用的命令及其必需字段。

**Enum** | **描述** | **附加必需的 JSON 字段**  
---|---|---  
0 | 传输基本系统信息 | None  
1 | 上传文件到 C2 | params  
2 | Download file to client | content, savepath  
3 | 执行 shell 命令并将输出写入 C2 | params  
4 | 设置客户端的 Google Drive 计时器间隔 | params  
5 | 为客户端信息心跳消息设置客户端计时器间隔 | params  
6 | 覆盖目标工作时间信息 | params  
  
对C2的反馈也被格式化为 JSON，其字段与命令非常相似。但是，所有反馈 JSON 对象都有一个额外的必需字段“ UUID”，该字段由设备的
Hardware UUID 填充。

### 总结

Storm Cloud
是一个高级的和多功能的黑客，调整其工具集，以配合攻击目标的不同的操作系统。他们利用内置的操作系统工具、开源工具和定制的恶意软件植入来实现他们的目标。利用
c2的云平台，比如使用 Google Drive，增加了不被网络监控解决方案发现的可能性。加上恶意软件只在受害者工作日发出信号这一事实，其隐蔽性更甚。

排除平台因素，GIMMICK
恶意软件组的样本相当庞大和复杂，部分原因在于其异步设计的复杂性，例如它的线程和锁定机制。将这个恶意软件移植到一个新的操作系统(macOS)并使其适应这个系统的工作并非轻而易举的事情，这表明它背后的黑客拥有充足的资源、娴熟的技能和多才多艺。值得注意的是，Volexity
只观察到过 Storm Cloud 使用过 GIMMICK (macOS 和 Windows版本)。然而，这个恶意软件植入程序是否由 Storm
Cloud开发或专有还是不确定的

### 附录

以下资源描述了苹果的Grand Central Dispatch:

  * [https://www.amazon.com/dp/099105556X/ref=cm_sw_em_r_mt_dp_RYJ6VS3327WSY7SE551Y?_encoding=UTF8&psc=1](https://www.amazon.com/dp/099105556X/ref=cm_sw_em_r_mt_dp_RYJ6VS3327WSY7SE551Y?_encoding=UTF8&psc=1) -> ISDN-13: 978-0991055562 
  * [ttps://www.amazon.com/dp/0321706250/ref=cm_sw_em_r_mt_dp_7J0VBS0DW5NWAZAFT5ZF](https://www.amazon.com/dp/0321706250/ref=cm_sw_em_r_mt_dp_7J0VBS0DW5NWAZAFT5ZF) ISDN-13: 978-0321706256 
  * [ttps://www.galloway.me.uk/2012/10/a-look-inside-blocks-episode-1/](https://www.galloway.me.uk/2012/10/a-look-inside-blocks-episode-1/)
  * [ttps://opensource.apple.com/source/libclosure/libclosure-67/BlockImplementation.txt.auto.html](https://opensource.apple.com/source/libclosure/libclosure-67/BlockImplementation.txt.auto.html)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1854/>

