# Vidar窃密木马分析（上）

阅读量 **384862**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-25 15:30:04

 **x**

##### 译文声明

本文是翻译文章，文章原作者 fumik0，文章来源：fumik0.com

原文地址：<https://fumik0.com/2018/12/24/lets-dig-into-vidar-an-arkei-copycat-forked-stealer-in-depth-analysis/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01155554bb6172bce2.jpg)

## 前言

有时，当你对海量的恶意软件检测结果进行分析时，你可能并不希望一些看似无关痛痒的小细节会对最终的判定造成影响。

前不久，我因为将遇到的恶意软件误认为 Arkei（一款功能强大的窃密木马）而付出了代价。根据当时我设置的Yara规则，显示匹配到的是
Arkei，但是经过逆向分析之后，我发现遇到的这个恶意软件并非Arkei。一些与Arkei特征相关的字符串都被删除了，取而代之的是“Vidar”。经过深度分析后，我发现
它是由Arkei优化改进得到的，除了一些细节之外，其他部分和Arkei区别不大。

这款恶意软件使用C++编写，似乎在2018年10月初就已经开始活动，它具有窃取木马的所有典型功能：

  * 搜索特定文档
  * 从浏览器窃取cookie
  * 窃取浏览器历史记录（包括tor浏览器）
  * 窃取数字货币钱包
  * 从带有2FA（双因素认证）的软件窃取数据
  * 从消息应用中窃取数据
  * 屏幕截图
  * 安装Loader
  * Telegram通知（服务器端）
  * 获取受害者计算机信息快照

在黑市/论坛中，这款窃密木马以250-700美元的价格进行出售。购买后，可以通过访问C2域名来生成专属的payload，所以没有统一管理端。除此之外，C2域名每4天就会进行更新。

在本文中，我将对4.1版本的Vidar进行深入分析，并介绍其管理面板，说明它和Arkei的差异。

## 定向投递

首先，如果受害者机器使用[GetUserDefaultLocaleName](https://docs.microsoft.com/en-us/windows/desktop/api/winnls/nf-winnls-getuserdefaultlocalename)来配置语言，我们可以使用很经典的方式（改变系统语言）来中止恶意软件。这也是检查恶意软件是否不会对一些特定的国家/地区进行感染最简单的办法之一。

![](https://p4.ssl.qhimg.com/t011b2bfdff8f13fb71.png)

正如MSDN所声明的，“local”中以集合的方式展示用户的语言偏好。窃密软件将检查被入侵主机的是否设置为以下语言：

![](https://p5.ssl.qhimg.com/t011401ba566595d730.png)

谷歌一下，我们就能知道这是哪些哪些国家/地区的简称：

![](https://p2.ssl.qhimg.com/t01530af0bf0dfc868d.png)

LCID Structure – <https://msdn.microsoft.com/en-us/library/cc233968.aspx>  
Language Code Table – <http://www.lingoes.net/en/translator/langcode.htm>  
LocaleName – <https://docs.microsoft.com/fr-fr/windows/desktop/Intl/locale-names>  
Locale – <https://docs.microsoft.com/fr-fr/windows/desktop/Intl/locales-and-languages>

## 互斥体

对于每个受害者，Vidar将生成唯一的特征字符串。它的形成很简单，就是由2个字符串拼接后得到的。

**硬件配置ID**  
[GetCurrentHwProfileA](https://docs.microsoft.com/en-us/windows/desktop/api/winbase/nf-winbase-getcurrenthwprofilea)用于检索具有[szHwProfileGuid](https://docs.microsoft.com/en-us/windows/desktop/api/winbase/ns-winbase-taghw_profile_infoa)值的计算机的当前硬件配置信息。如果执行失败，它将返回“Unknown”。

![](https://p0.ssl.qhimg.com/t01d2258f72ea49f37e.png)

**计算机GUID**  
通过[RegOpenKeyExA](https://docs.microsoft.com/en-us/windows/desktop/api/winreg/nf-winreg-regopenkeyexa)，可以在注册表中获取该值：  
`HKEY_LOCAL_MACHINESOFTWAREMicrosoftCryptographyMachineGuid`  
Windows在安装操作系统时会生成[UUID](https://msdn.microsoft.com/en-us/library/windows/desktop)。

![](https://p2.ssl.qhimg.com/t0100bba37696198546.png)

以上操作完成后，将生成互斥体，如下图所示：

![](https://p4.ssl.qhimg.com/t0182fe9c3600829c0c.png)

## 字符串设置

当Vidar执行main函数时，会先驻存一些必要的字符串，以便后续步骤的正常进行。

![](https://p4.ssl.qhimg.com/t012aeea4f7bf613281.png)

当所有字符串的RVA（相对虚拟地址）都存储在.data中后，恶意软件将访问被请求的字符串。

![](https://p3.ssl.qhimg.com/t01ea5b508c2d1488e5.png)

这种做法会给静态分析带来一些难度，但影响不大。

## C2域名&Profile ID

当builder在受害主机生成恶意软件时，随之会硬编码一个唯一ID。在恶意域名上输入该ID，将检索出攻击者想要从受害者计算机上窃取到的指定配置信息。

如下图，展示的是Profile ID为“178”的感染计算机，如果恶意软件没有进行配置，那么其Profile ID默认为“1”。

![](https://p0.ssl.qhimg.com/t01cb96efb81fd24355.png)

C2域名只是简单的进行了异或操作。只需要使用异或函数就可以解密出原始数据。

![](https://p1.ssl.qhimg.com/t01efba46ad9c34f512.png)

解密可以得到C2域名为“newagenias.com”。

![](https://p0.ssl.qhimg.com/t01281bf9e9b8dfaca2.png)

可以使用我GItHub仓库中的脚本[izanami.py](https://github.com/Fmk0/scripts/blob/master/izanami.py)来完成配置信息的提取。

## 配置字段说明

以下是恶意软件可以从C2获取的默认配置信息：

    
    
    1,1,1,1,1,1,1,1,1,1,250,Default;%DESKTOP%;*.txt:*.dat:*wallet*.*:*2fa*.*:*backup*.*:*code*.*:*password*.*:*auth*.*:*google*.*:*utc*.*:*UTC*.*:*crypt*.*:*key*.*;50;true;movies:music:mp3;
    

我使用”；”来区分各个部分，下面是各部分的解释说明：  
 **第一部分**

![](https://p2.ssl.qhimg.com/t01a2e1b41c7a79c94f.png)

**第二部分**

![](https://p3.ssl.qhimg.com/t011272d3ab2f9f13ae.png)

**第三部分**

`*.txt:*.dat:*wallet*.*:*2fa*.*:*backup*.*:*code*.*:*password*.*:*auth*.*:*google*.*:*utc*.*:*UTC*.*:*crypt*.*:*key*.*`

**第四部分**

![](https://p2.ssl.qhimg.com/t01109d0c48971c2084.png)

**第五部分**

_movies:music:mp3;_  
这是一个特殊的部分，在Grabber递归的检索指定文件夹时，以上文件将会直接过滤。  
如果直接看代码，这些设置显得很混乱，因为每个变量都存储在byte或dword变量中。

![](https://p1.ssl.qhimg.com/t015ffb3ab5a919621d.png)

## 文件夹生成

总结一下Vidar可能生成的的文件/文件夹，如下：

    
    
    \files                   <- 主文件夹
    \files\Autofill         <- 自动填充文件
    \files\CC               <- 信用卡
    \files\Cookies          <- Cookies
    \files\Downloads        <- 浏览区下载记录
    \files\Files            <- 通用配置
    \files\History          <- 浏览器历史记录
    \files\Soft             <- 目标软件的主文件夹
    \files\Soft\Authy      <- 2FA软件
    \files\Telegram         <- Telegram消息
    \files\Wallets          <- 加密货币钱包
    

通用文件：

    
    
    \filesscreenshot.jpg     <- 实时屏幕截图
    \filespasswords.txt      <- 整合后的密码
    \files\information.txt   <- 计算机设置 快照
    

## 窃密所需的库文件

每当我阅读恶意软件说明时，我总希望不需要安装库文件或其他插件，双击该恶意软件就可以直接运行。然而对代码进行深入研究或分析通信数据流，会发现它还是需要下载一些DLL文件以便完成特定的功能。

基于这种情况，针对不同的浏览器，在窃取信息时需要下载以下文件。

![](https://p4.ssl.qhimg.com/t01f792f01b7a413af1.png)

执行完成后，这些文件就会被删除。

![](https://p0.ssl.qhimg.com/t0175512ee0c1191c84.png)

## FTP

Vidar支持对以下FTP软件信息的窃取。

  * FileZilla
  * WinSCP

## 双因素认证（2FA）软件

我发现Vidar对2FA软件是有针对性的窃密，这种功能并不常见。但可以肯定的是这种情况会越来越普遍。随着各种防护措施的出现，用户需要明白带有2FA并不代表账户就一定安全，这也可能为漏洞的出现开启了另一扇门。

因此，Vidar将认证软件作为了目标……

![](https://p5.ssl.qhimg.com/t010f3f6cb3d1b23b88.png)

因为大部分SQLite 文件存放在%APPDATA% 目录下，所以看起来窃密软件想要从那里窃取Discord及Chrome等软件的数据信息。

![](https://p0.ssl.qhimg.com/t017c23a3ea8b6254e7.png)

所以小伙伴们，不要对你的2FA软件掉以轻心。

![](https://p5.ssl.qhimg.com/t01cc7d5d08b4fefdc5.png)

## 浏览器

需要注意的事，Vidar对Tor浏览器也有效。

以下浏览器中的信息将会被窃取：

  * 360 Browser
  * Amigo
  * BlackHawk
  * Cent Browser
  * Chedot Browser
  * Chromium
  * CocCoc
  * Comodo Dragon
  * Cyberfox
  * Elements Browser
  * Epic Privacy
  * Google Chrome
  * IceCat
  * Internet Explorer
  * K-Meleon
  * Kometa
  * Maxthon5
  * Microsoft Edge
  * Mozilla Firefox
  * Mustang Browser
  * Nichrome
  * Opera
  * Orbitum
  * Pale Moon
  * QIP Surf
  * QQ Browser
  * Sputnik
  * Suhba Browser
  * Tor Browser
  * Torch
  * URAN
  * Vivaldi
  * Waterfox

如果浏览器是基于chromium引擎，那么需要重视起来。

## Messengers/Mailer

在本文中，我不会介绍这些技术如何实现，因为在我以前的[博文](https://fumik0.com/2018/10/15/predator-the-thief-in-depth-analysis-v2-3-5/)中曾对相关技术进行过说明（特别是Telegram部分）。

  * Bat!
  * Pidgin
  * Telegram
  * Thunderbird

## 钱包

  * Anoncoin
  * BBQCoin
  * Bitcoin
  * DashCore
  * DevCoin
  * DigitalCoin
  * Electron Cash
  * ElectrumLTC
  * Ethereum
  * Exodus
  * FlorinCoin
  * FrancoCoin
  * JAXX
  * Litecoin
  * MultiDoge
  * TerraCoin
  * YACoin
  * Zcash

当然，如果攻击者指定了其他文件夹，对受害者机器特定区域进行搜索，那么这个名单会持续增加下去。

## Grabber

介绍到现在，Grabber可以说是Vidar功能最复杂的模块，也是它在实现上与Arkei区别最大的部分。

首先，它会根据已下载的配置文件来选择是否启用Grabber模块。如果该选项被激活，那它将生成文件夹路径字符串并设置 **func_grabber**
何时被调用。

![](https://p4.ssl.qhimg.com/t0158bf598cfff890c0.png)

在分析到 **func_grabber** 时，现实比我想象的残酷一些：

![](https://p1.ssl.qhimg.com/t01e8f3f1cd482fdd38.png)

看到这个，我的内心是拒绝的。我的脑海中已经大概想到了它是如何分配内存的。然而摆在我面前的的是所有恶意软件分析师都想挑战（或者根本不想遇到）的融合了多种技巧的恶意模块：

  * 糟糕的情况突如其来
  * 一个函数中又调用了另一个函数（就行俄罗斯套娃一样）
  * 调用API
  * 等等…

但实际上，它并没有预想中那么复杂。接下来我会举一个例子进行说明。

在下面的示例中，如果从C2下载的配置文件中存在“％APPDATA％”字符串。它将跳转进入该功能，并进行一系列验证，直到进入最重要的
**func_VidarSearchFile** 函数。

![](https://p1.ssl.qhimg.com/t011f7e14e54afb9499.png)

在不同的场景下，几乎都会执行以上过程。

以下是Grabber模块可能用到的目录：

  * %ALL_DRIVES% ([GetDriveTypeA](https://docs.microsoft.com/en-us/windows/desktop/api/fileapi/nf-fileapi-getdrivetypea) Necessary)
  * %APPDATA%
  * %C%
  * %D%
  * %DESKTOP%
  * %DOCUMENTS%
  * %DRIVE_FIXED%
  * %DRIVE_REMOVABLE%
  * %LOCALAPPDATA%
  * %USERPROFILE%

## 屏幕截图

屏幕截图功能的实现很简单：

  * 首先调用[GdiplusStartup](https://docs.microsoft.com/en-us/windows/desktop/api/gdiplusinit/nf-gdiplusinit-gdiplusstartup)函数来初始化Windows GDI +
  * 接着调用[GetSystemMetrics](https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-getsystemmetrics)来代替GetDeviceCaps ，使用SM_CYSCREEN (1) 和SM_CXSCREEN (0)来获取屏幕高度的宽度。  

然后使用一个DC对象来创建生成图像所需的兼容位图，通过选择兼容memory DC并使用Bit Block API函数来完成数据传输。完成这些操作后，将进入
**func_GdipSaveImageToFile** 函数。

![](https://p0.ssl.qhimg.com/t01dd43c9a78bde1020.png)

最后从生成的位图中将数据复制到一个缓冲区中，在缓冲区中生成生成屏幕截图。

![](https://p0.ssl.qhimg.com/t01282f6bb98db3fcc7.png)

## 信息日志

在这部分中，我只对如何生成日志进行了分析，其他的是一些相关API的调用，通过设置断点跟踪，花一些时间，你也可以轻松的进行分析。

首先，它会说明这是哪个版本的Vidar。

![](https://p4.ssl.qhimg.com/t01b4943db000af945d.png)

如果你没有在日志文件中看到“Vidar”字符串，这意味着你分析的是之前的版本。

![](https://p5.ssl.qhimg.com/t019acc535100023274.png)

获取操作系统平台及版本时采用了很经典的组合，首先，使用[RegOpenKeyExA](https://docs.microsoft.com/en-us/windows/desktop/api/winreg/nf-winreg-regopenkeyexa)来获取注册表项的值。

    
    
    HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsNTCurrentVersionProductName
    

接下来，会对运行的Windows环境为32位还是64位进行检测，该软件会通过[IsWow64Process](https://docs.microsoft.com/en-us/windows/desktop/api/wow64apiset/nf-wow64apiset-iswow64process)来检测自身是否运行在[WOW64](https://docs.microsoft.com/en-us/windows/desktop/api/wow64apiset/nf-wow64apiset-iswow64process) 下。

![](https://p1.ssl.qhimg.com/t01b4943db000af945d.png)

![](https://p4.ssl.qhimg.com/t01bcf780789f741480.png)

为了获得当前用户所使用屏幕的分辨率。将通过调用[CreateDCA](https://docs.microsoft.com/en-us/windows/desktop/api/wingdi/nf-wingdi-createdca)来为“Display”创建设备环境，并使用[GetDeviceCaps](https://docs.microsoft.com/en-us/windows/desktop/api/wingdi/nf-wingdi-getdevicecaps)来获取屏幕的长度和宽度。

![](https://p2.ssl.qhimg.com/t01a0fe2fafe1ff6185.png)

这部分的源代码如下：

    
    
    HDC hDC = CreateDCA("DISPLAY", NULL, NULL, NULL);  
    int width = GetDeviceCaps(hDC, HORZRES); // HORZRES = 0x8
    int height = GetDeviceCaps(hDC, VERTRES); // VERTRES = 0x0A
    

继续进行分析,得到：

![](https://p3.ssl.qhimg.com/t0129d97d166b340e64.png)

在下一部分，将继续针对Vidar的通信、Loader、Killing、管理面板等模块进行介绍，敬请期待…

本文翻译自fumik0.com [原文链接](https://fumik0.com/2018/12/24/lets-dig-into-vidar-an-arkei-copycat-forked-stealer-in-depth-analysis/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **西格玛** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/170191](/post/id/170191)

安全客 - 有思想的安全新媒体

本文转载自: [fumik0.com](https://fumik0.com/2018/12/24/lets-dig-into-vidar-an-arkei-copycat-forked-stealer-in-depth-analysis/)

如若转载,请注明出处： <https://fumik0.com/2018/12/24/lets-dig-into-vidar-an-arkei-copycat-forked-stealer-in-depth-analysis/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [样本分析](/tag/样本分析)

 **+1** __2赞

 __收藏

![](https://p3.ssl.qhimg.com/t019d477bc1e93f1cf7.png) 西格玛

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

