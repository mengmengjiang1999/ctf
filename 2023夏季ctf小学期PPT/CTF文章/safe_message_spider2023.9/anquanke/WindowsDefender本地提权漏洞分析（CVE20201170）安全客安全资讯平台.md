# Windows Defender 本地提权漏洞分析（CVE-2020-1170）

阅读量 **226831**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-06-28 10:00:06

 **x**

##### 译文声明

本文是翻译文章，文章原作者 github，文章来源：itm4n.github.io

原文地址：<https://itm4n.github.io/cve-2020-1170-windows-defender-eop/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t012e4fcfaf12ced152.png)

## 简介

在深入了解此漏洞的技术细节之前，我想简单介绍一下时间线。大概8个月前，我最初通过ZDI报告了这个漏洞。向他们发送我的报告后，我收到了一个回复，他们对收购此漏洞不感兴趣。当时，我只有几个星期的Windows安全研究经验，所以我有点依赖他们的判断，把这个发现放在一边。

5个月后，即2020年3月下旬，我再次浏览了笔记，看到了这份报告，但是这次，我的想法不同了。通过我直接发送给Microsoft其他的一些报告，我获得了一些经验。因此，我知道它可能符合潜在的条件，因此我决定花更多时间在它上面。这是一个很好的决定，因为我甚至找到了一种触发漏洞的更好方法。我在4月初向微软报告了此事，几周后得到了认可。

## 初步思考过程

你可以阅读Microsoft发布的[公告](https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-1170):

    
    
    Windows Defender中存在的权限提升漏洞会导致系统上任意文件的删除。
    

像平常一样，描述的非常笼统。你会发现它不仅仅是“ 任意文件删除 ”

我发现的问题与Windows Defender日志文件的处理方式有关。Windows
Defender使用2个日志文件MpCmdRun.log和MpSigStub.log，都位于C:WindowsTemp中，该目录是SYSTEM帐户的默认临时文件夹，但也是每个用户都具有写入访问权限的文件夹。

虽然这听起来很糟糕，但其实并没有那么糟糕，因为文件的权限设置正确，默认情况下，管理员和SYSTEM可以完全控制这些文件，而普通用户甚至无法读取它们。

![](https://p4.ssl.qhimg.com/t01f9853c23006efe7e.png)

下面是一个示例日志文件的摘要。正如您所看到的，它用于记录如签名更新之类的事件，但您也可以找到一些与防病毒扫描相关的条目。

![](https://p3.ssl.qhimg.com/t014b52277f0b302579.png)

签名更新会定期自动完成，但是也可以使用PowerShell命令Update-MpSignature手动触发，这并不需要任何特殊特权。因此，这些更新可以作为一个普通用户触发，如下面的截图所示。

![](https://p1.ssl.qhimg.com/t01d91b522f253a017b.png)

在此过程中，我们可以看到Windows Defender 正在向C:WindowsTempMpCmdRun.log写入某些信息（如NT
AUTHORITYSYSTEM）。

![](https://p1.ssl.qhimg.com/t0191ce1e54ba411dc2.png)

这意味着，作为低权限用户，我们可以通过运行NT
AUTHORITYSYSTEM的进程触发日志文件写入操作。尽管我们无法访问该文件，也无法控制其内容。我们甚至对Temp文件夹本身都没有访问权限，因此也无法将其设置为挂载点。我现在想不出一个更无用的攻击载体了。

不过，我根据CVE-2020-0668的经验，这是Windows服务中一个微不足道的权限提升漏洞，我知道它可能不仅仅是一个日志文件写入。

仔细思考一下，每次签名更新完成时，都会向文件中添加一个新条目，该条目大约1
KB。虽然不多，但是，几个月甚至几年后，它将有多少呢？在这种情况下，通常会采用日志轮换机制，以便对旧日志进行压缩、存档或删除。因此，我想知道是否也实现了这种机制来处理MpCmdRun.log文件。如果是这样，可能存在滥用文件操作特权的地方。

## 搜索日志旋换机制

为了找到潜在的日志轮换机制，我首先逆向了MpCmdRun.exe可执行文件。在IDA中打开文件后，我要做的第一件事就是搜索MpCmdRun字符串，我最初的目标是查看如何处理日志文件，看到Strings窗户通常是一个好的开始。

![](https://p4.ssl.qhimg.com/t01ba3c5a2835fef956.png)

不出所料，第一个结果是MpCmdRun.log，不过，这个搜索还得到了另一个非常有趣的结果：MpCmdRun_MaxLogSize。我正在寻找一种对轮换机制，该字符串等同于“
Follow the white Rabbit ”。查看Xrefsof
MpCmdRun_MaxLogSize，我发现它仅在MpCommonConfigGetValue()函数中使用。

![](https://p5.ssl.qhimg.com/t01b2367518b4831088.png)

MpCommonConfigGetValue()函数本身是从MpCommonConfigLookupDword()调用的。

![](https://p3.ssl.qhimg.com/t015d4852acb2d14649.png)

最后，MpCommonConfigLookupDword()从CLogHandle::Flush()方法中调用。

![](https://p2.ssl.qhimg.com/t01def4ba6bdf31fd28.png)

CLogHandle::Flush()特别有趣，因为它负责写入日志文件。

![](https://p0.ssl.qhimg.com/t015150b68e19e4a77d.png)

首先，我们可以看到在GetFileSizeEx()中调用了hObject，这是指向日志文件MpCmdRun.log的句柄。此函数的结果返回在FileSize，这是一个LARGE_INTEGER结构。

    
    
    typedef union _LARGE_INTEGER {
      struct {
        DWORD LowPart;
        LONG  HighPart;
      } DUMMYSTRUCTNAME;
      struct {
        DWORD LowPart;
        LONG  HighPart;
      } u;
      LONGLONG QuadPart;
    } LARGE_INTEGER;
    

因为mpcmdrunk
.exe是一个64位的可执行文件，所以使用QuadPart直接获取文件大小为LONGLONG。这个值存储在v11中，然后与MpCommonConfigLookupDword()返回的值进行比较。

因此，在继续之前，我们需要获取MpCommonConfigLookupDword()的返回值。为此，我找到的最简单的方法是在这个函数调用之后设置一个断点，并从RAX寄存器获取结果。

![](https://p3.ssl.qhimg.com/t012f57f34aef6d15ab.png)

断点命中后的样子如下：

![](https://p3.ssl.qhimg.com/t01b71ecc68a2ae4a8c.png)

因此，我们现在知道文件的最大大小是0x1000000，即16,777,216字节(16MB)。

接下来的问题是:当日志文件大小超过这个值时会发生什么?如前所述，当日志文件的大小超过16MB时，将调用PurgeLog()函数。根据名称，我们可以假设可能会在这个函数中找到第二个问题的答案。

![](https://p3.ssl.qhimg.com/t01217ba0d1def63f4c.png)

调用此函数时，首先通过连接原始文件名和.bak来准备一个新文件名。然后，原始文件被移动，这意味着mpcmdrun.com
.log被重命名为mpcmdrun.com .log.bak。现在我们有了答案:确实实现了日志旋换机制。

在这里，我可以继续进行逆向分析，但是我还有其他想法。考虑到这些，我想采用一种更简单的方法。其思路是检查该机制在各种条件下的行为，并使用Procmon观察结果。

## 漏洞

以下是我们所知道的：

  * Windows Defender将一些日志事件写入C:WindowsTempMpCmdRun.log（例如：签名更新）。
  * 任何用户都可以在C:WindowsTemp中创建文件和目录。
  * 日志旋换机制通过将日志文件移动到C:WindowsTempMpCmdRun.log.bak并创建一个新文件来防止其超过16MB 。

你能发现潜在的问题吗？如果已经有一个名为mpcmdrunk.log.bak的文件存在，会发生什么?

为了回答这个问题，我考虑了以下测试方案:

  * 1.在C: WindowsTemp目录创建一个名为MpCmdRun.log.bak文件。
  * 2.使用任意数据填充C: WindowsTempMpCmdRun.log文件，使其大小接近16MB。
  * 3.触发签名更新
  * 4.使用Procmon观察结果

如果mpcmdrunk.log.bak是一个现有的文件，它只是被覆盖。我们可以假设这是预期行为，因此此测试不是很确定。相反，我想到的第一个测试场景是：如果MpCmdRun.log.bak是目录呢？

如果MpCmdRun.log.bak不是一个简单的文件，我们可以假设它不能简单地被覆盖。所以，我最初的假设是日志轮换将完全失败。与其创建原始日志文件的备份，不如将其覆盖。不过，我用Procmon观察到的行为远比这有趣。Defender实际上删除了该目录，然后继续正常的日志轮换。因此，我决定重做该测试，但是，这次我还在里面创建了C:WindowsTempMpCmdRun.log.bak文件和目录。原来，删除实际上是递归的！

这很有趣!现在的问题是:我们是否可以重定向这个文件操作?

这是这个测试用例的初始设置:

  * 创建一个虚拟的目标目录:C:ZZ_SANDBOXtarget。
  * MpCmdRun.log.bak被创建为一个目录并被设置为此目录的挂载点。
  * 这个MpCmdRun.log日志文件中包含16777002字节的任意数据。

![](https://p3.ssl.qhimg.com/t01d2237dd49c0f68bb.png)

挂载点的目标目录包含一个文件夹和一个文件。

![](https://p3.ssl.qhimg.com/t0156f0763ef146ee36.png)

这是我在执行PowerShell命令Update-MpSignature后在Procmon中观察到的内容：

![](https://p3.ssl.qhimg.com/t01947eb619a2d6561e.png)

Defender在挂载后，以递归方式删除每个文件和文件夹，最后删除文件夹C:WindowsTempMpCmdRun.log.bak本身。这意味着，作为普通用户，我们可以欺骗该服务删除文件系统上任何文件或文件夹…

## 可利用性

正如我们在前面看到的，利用是非常简单的。我们要做的唯一一件事就是创建目录C:
WindowsTempMpCmdRun.log.bak，并将其设置为文件系统上另一个位置的挂载点。

注意:实际上并没有那么简单，因为如果我们想要执行目标文件或目录删除，需要额外的技巧，但这里我不讨论这个。

不过，我们面临一个实际问题：填充日志文件需要多长时间，直到其大小超过16MB，这对于一个简单的日志文件来说是相当高的值。因此，我做了几个测试，并测量了每个命令所需的时间。然后，我推断了结果，以估计所需的总时间。应当注意，该Update-MpSignature命令不能并行运行多次。

###  测试1

作为第一个测试，我选择了一个幼稚的方法。我运行了Update-MpSignature命令一百次，并测量了整个过程。

![](https://p4.ssl.qhimg.com/t011a851b5bcd81ed31.png)

![](https://p3.ssl.qhimg.com/t012c9b799a969163ce.png)

下面是第一次测试的结果。使用这种技术，如果我们在循环中运行Update-MpSignature命令，则需要超过22个小时来填充文件并触发漏洞。

DESCRIPTION | TIME | FILE SIZE | # OF CALLS  
---|---|---|---  
Raw data for 100 calls | 650s (10m 50s) | 136,230 bytes | 100  
Estimated time to reach the target file size | 80,050s (22h 14m 10s) |
16,777,216 bytes | 12,316  
  
至少可以说，这不太实际。

###  测试2

在测试1之后，我检查了Update-MpSignature命令的文档，以查看是否可以对其进行调整以加快整个过程。这个命令的选项非常有限，但有一个引起了我的注意。

![](https://p4.ssl.qhimg.com/t0173d814a77e0d4a49.png)

此命令接受一个UpdateSource作为参数，实际上是一个枚举，如我们在上面截图所见。使用大多数可用值时，将立即返回错误消息，并且不会向日志文件中写入任何内容，因此它们对于这种利用场景毫无用处。

但是，在使用InternalDefinitionUpdateServer值时，我观察到了一个有趣的结果。

![](https://p2.ssl.qhimg.com/t01ac6a090bdcd35a1f.png)

因为我的VM是在Windows中独立安装的，所以它没有配置使用“内部服务器”进行更新。相反，它们直接从MS服务器接收，因此出现错误消息。

此方法的主要优点是几乎立即返回错误消息，但事件仍会写入日志文件，这使得它非常适合在这种特定情况下进行利用。

![](https://p2.ssl.qhimg.com/t017f1999e6394d1525.png)

因此，我也运行了该命令一百次，并观察了结果。

![](https://p5.ssl.qhimg.com/t016d87154bd82c158e.png)

这一次，100次调用用了不到4秒的时间完成。这还不足以计算相关的统计数据，所以这次我用10,000次调用运行相同的测试。

![](https://p1.ssl.qhimg.com/t011a146c840fd88910.png)

DESCRIPTION | TIME | FILE SIZE | # OF CALLS  
---|---|---|---  
Raw data for 10,000 calls | 363s (6m 2s) | 2,441,120 bytes | 10,000  
Estimated time to reach the target file size | 2,495s (41m 35s) | 16,777,216
bytes | 68,728  
  
稍作调整，整个操作将需要大约40分钟，而不是前一个命令的22个多小时。因此，这将大大减少填充日志文件所需的时间。还应该注意的是，这些值对应于最坏情况，即日志文件最初为空。我认为这个值是可以接受的，所以我在Poc中实现了这一方法，下面截图显示了结果。

![](https://p1.ssl.qhimg.com/t01d1bed750745b62c7.png)

从一个空的日志文件开始，PoC用了大约38分钟完成，这与我之前所做的估算非常接近。

顺便说一下，如果您注意到最后一个屏幕截图，您可能会注意到我指定了C:
ProgramDataMicrosoftWindowsWER作为要删除的目录。我不是随机选择这个的。我选择这个是因为，一旦这个文件夹被删除，你就可以像[@jonaslyk](https://github.com/jonaslyk
"@jonaslyk")在这篇文章中解释的那样，以NT AUTHORITYSYSTEM的形式执行代码:  
[From directory deletion to SYSTEM
shell](https://secret.club/2020/04/23/directory-deletion-shell.html)。

## 结论

这可能是我写的关于这种特权文件操作滥用的最后一篇文章。在发给所有漏洞研究人员的电子邮件中，微软宣布他们改变了奖金的范围。因此，这种利用不再符合条件。这个决定是合理的，因为一个通用补丁正在开发中，它将解决这类bug。

我不得不说，这个决定听起来有点过早。如果这个补丁已经在最新的Windows
10预览版中实现了，这是可以理解的，但事实并非如此。我认为这更多的是一个经济决定，而不是纯粹的技术问题，因为这样的赏金计划可能意味着每月几十万美元的成本。

## Links & Resources

  * CVE-2020-1170 | Microsoft Windows Defender Elevation of Privilege Vulnerability  
<https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-1170>

  * SECRET CLUB – From directory deletion to SYSTEM shell  
<https://secret.club/2020/04/23/directory-deletion-shell.html>

本文翻译自itm4n博客,[原文地址](https://itm4n.github.io/cve-2020-1170-windows-defender-eop/)。

本文翻译自itm4n.github.io [原文链接](https://itm4n.github.io/cve-2020-1170-windows-defender-eop/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **qwert** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/209032](/post/id/209032)

安全客 - 有思想的安全新媒体

本文转载自: [itm4n.github.io](https://itm4n.github.io/cve-2020-1170-windows-defender-eop/)

如若转载,请注明出处： <https://itm4n.github.io/cve-2020-1170-windows-defender-eop/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __3赞

 __收藏

![](https://p2.ssl.qhimg.com/t01de37baca165a5b78.png) qwert

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

