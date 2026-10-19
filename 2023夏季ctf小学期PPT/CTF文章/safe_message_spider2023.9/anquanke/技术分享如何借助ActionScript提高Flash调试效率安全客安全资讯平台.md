# 【技术分享】如何借助ActionScript提高Flash调试效率

阅读量 **130094**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-05-10 15:44:16

 **x**

##### 译文声明

本文是翻译文章，文章来源：checkpoint.com

原文地址：<http://blog.checkpoint.com/2017/05/05/debug-instrumentation-via-flash-actionscript/>

译文仅供参考，具体内容表达以及含义原文为准。

****

**  
**

****

翻译：[ **興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

**预估稿费：200RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**一、前言**

浏览器插件一直以来都是攻击者热衷的攻击目标。在过去的几年中，最热门的攻击目标无疑是Flash。仅在2016年，与Flash有关的CVE漏洞就有250多个，几乎每个[
**漏洞利用平台**](https://www.recordedfuture.com/top-vulnerabilities-2016/)中都包含这些漏洞的利用工具。针对Flash的攻击无所不在，值得我们注意。

作为安全研究人员，我们经常会处理一些攻击案例，为了分析这些案例，我们需要收集尽可能多的信息，研究漏洞利用的内部工作机制。这个过程通常来说是非常乏味和费时的，使研究任务无法完美完成。由于大多数漏洞利用的主体部分（如ROP链、shellcode以及载荷等）都是在运行时才生成，因此我们决定采用另一种办法，利用现有的原生层调试器（native
level debugger）的功能，使分析过程能够提供更多的信息，提高调试效率。

通过这种方法，我们能够更广泛地了解Flash漏洞利用的内部工作机制，使研究过程更加快速、简单、可控。

这篇文章中详细介绍了我们所使用的具体方法及其优点，并结合一些常见案例阐述该方法的具体应用场景。在了解这种Flash分析技术之前，我们可以先来回顾一下SWF的基础知识。

**  
**

**二、Flash基础知识**

**2.1 SWF**

人们之所以引入SWF格式，主要是想在互联网上分发矢量图形（不幸的是也可以用来分发漏洞利用程序）。在设计之初，人们就考虑到了网络分发的因素，因此将SWF格式设计为一种二进制格式，使用了压缩、位封装（bit-packing）以及包含可选字段的结构体来减少SWF文件的大小。

基本上说来，一个SWF文件由一系列带有标签的数据块组成。标签（Tag）可以用来定义需要显示的形状或者需要播放的音频流，但对于漏洞利用来说，标签更重要的功能是用来分发ActionScript
3.0字节码。

**2.2 DoABC**

DoABC标签包含一个ActionScript字节码（ActionScript
Bytecode，ABC）数据块，ABC数据块可以使用ActionScript 3.0虚拟机进行解析。

这个标签还可以包含静态值、类以及Flash文件所使用的方法的常量池。

比如，某段代码如下所示：

这段代码编译后会生成如下所示的字节码：

正如上述结果，pushstring指令引用的是常量池中的第13（0d）号字符串，如下所示：

另外getlex以及callpropvoid引用的是常量池中的限定名称（qualified name，QNAME），如下所示：

  

**三、分析方法**

目前我们在分析Flash漏洞利用技术时，可以使用一些常见的分析方法。

**3.1 源代码反编译及编辑方法**

最简单的一种方法是使用诸如FFDEC之类的反编译工具，获取实际的源代码并进行编辑源代码。

这种方法能够获取漏洞利用源代码，听起来非常吸引人，但事情并没有那么简单。攻击者会使用复杂的混淆和封装技术，导致我们难以理解生成的代码。此外，漏洞利用作者通常会加入垃圾代码以及不可达标签，利用这些方法对抗反编译器。

与此同时，即便我们通过反编译过程获得了有效的代码，这个过程中还是存在字节码被错误处理的可能性，这会导致代码生成错误，困扰安全分析人员。

**3.2 反汇编及追踪方法**

另一种方法是对SWF文件进行反汇编处理。我们可以使用诸如[
**RABCdasm**](https://github.com/CyberShadow/RABCDAsm)之类的反汇编器，从SWF文件中导出ABC标签的字节码（而不是反编译这个文件），之后就可以对字节码进行修改和重新汇编处理。

根据[ **Matt Oh**](https://community.hpe.com/t5/Security-Research/Playing-with-Adobe-Flash-Player-Exploits-and-Byte-Code/ba-p/6505942#.WFZDAFN96Ht)的研究成果，我们可以通过改变字节码，在关键节点注入某些调试功能（比如追踪（trace）功能）。这种方法毫无疑问非常强大，然而，hook反汇编后的代码、插入trace功能后，我们的分析能力也被限制在Flash
player调试器的自身能力范围内。

**3.3 我们提出的反汇编和调试方法**

有时候我们可以使用某些原生层调试功能，获得比Flash
player调试更有用的结果。当我们面对的是JIT层的函数或者想要分析漏洞存在的根本原因时，这种方法更加有用。

当我们分析IE浏览器的漏洞利用原理时，常见的技巧是将某个调试字符串作为参数，传递给某些不常用函数（如Math::Atan2()），将该函数插入程序中，同时在WinDBG中观察字符串的活动情况（我们可以通过WinDBG更好地观察内存和代码的布局，参考[
**此链接**](http://d0cs4vage.blogspot.co.il/2013/06/windbg-tricks-javascript-windbg.html)获取更详细信息）。

我们决定将这种技术应用到Flash
ActionScript中。我们可以通过这种方法，更好地了解漏洞利用过程中堆（heap）的分布情况，我们无法通过Flash
player调试器完成这一任务。通过插入某些不常用的函数（本例中我们使用的是JSON.stringify函数），我们能够打破字符串混淆的限制，查看字节数组的真实内容，因为这些数组都是被动态创建和分配的。

我们通过SWF文件的反汇编字节码，将不常用函数插入到SWF文件中，通过这种方法，绕过漏洞利用作者可能使用的任何对抗反编译器的技术。

这个方法主要包含两部分工作：

1、在WinDBG的合适位置设置断点；

2、使用我们的指示函数（即上文所述的不常用函数）hook原始的SWF文件。

由于Adobe并没有向公众提供调试符号，因此我们需要做一些逆向工程方面的工作。

**3.3.1 在WinDBG中设置必要的断点**

我们唯一的需求是指示函数可以处理字符串，并且希望该指示函数永远不会被漏洞利用程序调用。因此我们选择[
**JSON.stringify**](http://help.adobe.com/en_US/FlashPlatform/reference/actionscript/3/JSON.html#stringify\(\))函数作为指示函数。

在Flash库中查找指示函数的偏移量相对而言比较简单。我们分配一个字符串对象，使用WinDBG在内存中搜索这个对象，设置在访问字符串时触发断点，然后引导JSON.stringify函数处理字符串，如下所示：

编译ActionScript工程后，我们将创建的SWF文件嵌入到一个本地html文件中，使用IE浏览器打开这个文件。我们将WindDBG附加到IE进程上，在ExternalInterface.call(“alert(123)”)这一行设置断点。

当alert弹出时，Flash会暂停运行。此时，我们使用[
**Mona.py**](https://www.corelan.be/index.php/2011/07/14/mona-py-the-manual/)查找已分配的字符串对象，使用“ba”指令，设置WinDBG在读取这个具体的位置时触发断点：

在我们恢复Flash的运行后，断点自然会被触发：

现在我们需要验证当前操作的确与JSON.stringify()有关。在IDA中查看这个地址，我们发现情况的确如此：

如果一切按照计划执行，在函数返回时，eax中应该保存一个指向字符串化对象的指针。

大功告成，我们可以将以上步骤结合在一起，在WinDBG控制台中，创建断点，打印发往json.stringify()函数的所有所有字符串，如下所示：

    
    
    bp (Flash32_17_0_0_188 + 006a201a)  “.echo ——-; da poi(eax)”

**3.3.2 使用指示函数hook原始的SWF文件**

在处理各种对象和数据类型时，单单打印字符串是远远不够的。然而，我们可以将自己的类添加到flash文件中，这样我们就能够执行更加复杂的逻辑处理，处理各种数据类型。我们使用的类名为“exploit_common”，使用的主函数是debugPrint()。这个类能接受任何对象作为参数，并根据对象的具体类型进行处理，因此能够简化整个hook流程。然而，我们不能简单地将ActionScript代码以文本形式添加到漏洞利用程序中，因此，我们利用Adobe提供的[
**Flex SDK**](http://www.adobe.com/devnet/flex/flex-sdk-download.html)，使用如下命令编译库文件：

其中“as”是ActionScript库的实际路径。接下来，我们使用RABCDasm反汇编这个新创建的SWF文件。

之后我们拷贝库的.asasm文件，放在一边留待后用。

  

**四、案例演示**

现在我们以实际的漏洞利用程序为例，介绍这种方法的具体应用。

Sundown是目前最活跃的漏洞利用工具之一。我们可以从[ **Malware-traffic-analysis**](http://www.malware-traffic-analysis.net/2017/01/06/2017-01-06-Sundown-EK-sends-Terdot.A-Zloader.pcap.zip)上下载Sundown最新的Flash漏洞利用工具。

首先我们需要导出恶意SWF文件的DoABC标签，对类进行反汇编处理。

需要注意的是，abcexport命令导出的DoABC标签中包含附加的索引值，我们需要反汇编第一个索引（索引值从0开始）。

每个标签反汇编之后都会生成一些.class.asasm以及.script.asasm文件，以及一个main.asasm文件。

我们需要编辑main.asasm，包含我们的自定义库。

当然我们也需要将我们之前生成的.asasm文件添加进去：

现在我们已经可以在漏洞利用工具内部调用我们自己的函数。分析经过混淆处理的flash漏洞利用工具不是特别容易，对于Sundown来说，它的某些类名似乎是随机生成的。

**4.1 导出shellcode**

这个SWF文件的主类名为“unfaithfulness”。

我们在主类的初始化函数内部，找到一个非常长的混淆字符串。我们对这个字符串的功能比较感兴趣。

上图中高亮的那一行代码在ABC指令中的形式如下：

图1. 生成的字节码

在字节码中，当变量从AVM栈中弹出时，会使用setlocal_n指令完成变量的本地分配。因此，hook点应该挂在_loc6_的分配完成之后，如下所示：

现在我们可以保存.asasm文件了，汇编处理.asasm文件，生成.abc文件，将漏洞利用工具中的DoABC标签替换为我们hook过的标签。

Abcreplace.exe工具接受以下三个参数：

1、需要修改的.SWF文件；

2、需要替换的标签的索引值

3、我们修改过的标签

将hook后的SWF文件嵌入到一个HTML文件中，使用调试器开始调试。

设置断点、运行漏洞利用工具后，我们可以看到断点已被触发：

我们可以看到_loc6_的打印信息，它看起来像是一个shellcode，这段shellcode以XOR循环开始：

能够导出解码后的shellcode看起来的确很酷，但这种方法的最大的功能是能够了解堆的布局结构。现在让我们来看看如何做到这一点。

**4.2 查看堆结构**

以下是漏洞利用工具调用的第一个函数：

Spray_obj()中创建了两个Vector：

Vector
obj20中包含大小为20字节的数组，长度为0x200000。这些数组都包含明显特征，数组开头为一个有序增加的整数，整数基址为0xFACE0000，如下所示：

Vector obj4000保存0x4000个“everyday”类的实例：

“everyday”类的结构如下所示：

可以看出来，这个对象头部包含某些特征，应该会被漏洞利用工具大量填充到堆中（即所谓的堆喷射技术）。

所有的堆操作和设置准备完毕后，我们现在可以触发漏洞了。我们执行一次数组溢出读取操作，读取数组范围之外的78字节数据。由于obj20只有0x200000字节长，因此我们需要读取0x200078长度的数据。堆喷射成功后，泄露的对象（紧挨着obj20的最后一个成员所在的地址）的类型应该为“everyday”。代码如下图所示：

这个位置就是我们希望hook的关键位置，与一些信息描述字符串以及_local7的值有关：

我们可以借此获取有关堆结构的一些关键信息。与之前操作类似，我们需要保存、汇编以及替换我们修改过的标签。

在WindDBG中设置必要的断点，断点触发情况如下所示：

在0x78偏移处，我们找到了第一个“everyday”成员：

从前文分析，我们已知obj20字节数组的长度为0x200000，因此我们应该可以在0x090a0000处找到它，如下所示：

我们只是通过这个示例说明这种方法的强大功能。从此时开始，我们可以设置更多的断点，访问泄露的对象，搜索漏洞利用工具在内存中的模式和特征，了解所分配空间的特点等等。

  

**五、结论**

Flash漏洞利用无所不在，从漏洞利用工具以及目标攻击活动等各方面都能看到它的身影。这些漏洞利用程序使用高强度的混淆机制，试图逃避基于静态特征的检查，提高安全研究人员的分析难度。我们有可能使用[
**跟踪（trace）**](http://help.adobe.com/en_US/FlashPlatform/reference/actionscript/3/package.html#trace\(\))功能、使用[
**Flash Debug
Player**](https://www.adobe.com/support/flashplayer/debug_downloads.html)运行漏洞利用工具，避免在原生层进行调试。然而，虽然原生层的调试比较具有挑战性，但在处理具有底层虚拟机（例如Flash）的应用时，这种调试方式依然非常强大，具有多个优点。我们可以使用某些不常用的指示函数作为断点、提供有价值信息，在漏洞利用的执行流程中的关键点中断执行流程，打印有价值的数据，对恶意SWF文件进行调试。对比传统的debug
player调试方法，我们可以通过这种方法获得维度更广的信息。

本文翻译自checkpoint.com [原文链接](http://blog.checkpoint.com/2017/05/05/debug-instrumentation-via-flash-actionscript/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86060](/post/id/86060)

安全客 - 有思想的安全新媒体

本文转载自: [checkpoint.com](http://blog.checkpoint.com/2017/05/05/debug-instrumentation-via-flash-actionscript/)

如若转载,请注明出处： <http://blog.checkpoint.com/2017/05/05/debug-instrumentation-via-flash-actionscript/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

