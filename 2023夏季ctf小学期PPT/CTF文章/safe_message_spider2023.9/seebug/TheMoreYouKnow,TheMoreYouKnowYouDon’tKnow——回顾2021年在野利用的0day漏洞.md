**作者：Maddie Stone@Google Project Zero  
译者：知道创宇404实验室翻译组  
原文链接：<https://googleprojectzero.blogspot.com/2022/04/the-more-you-know-more-you-know-you.html>**

这是我们回顾在野利用 0day 漏洞的第三个年度 [[2020
年](https://googleprojectzero.blogspot.com/2021/02/deja-vu-lnerability.html)，[2019
年](https://googleprojectzero.blogspot.com/2020/07/detection-deficit-year-in-review-of-0.html)]。每年我们都会回顾所有检测到和披露的在野
0day，并综合分析其趋势和要点。本报告旨在整体分析年度漏洞利用，寻找趋势、差距，总结经验教训等等。如果你对单个漏洞利用感兴趣，可以查看我们的[分析](https://googleprojectzero.blogspot.com/p/rca.html)。

我们发布这篇分析报告是希望 0day 漏洞利用变得更有难度，希望攻击者使用 0day 所花费的成本和资源更高。2021
年的趋势也更强调了这一点如此重要。我们一遍又一遍地听到各国政府如何将记者、少数群体、政客、人权捍卫者，甚至是世界各地的安全研究人员作为目标。我们切身体会到，在安全和技术社区做出的决定会对社会和人类的生活产生真正的影响。

本文正文中将会提供我们分析结论的证据和过程，总结下一步的想法和对 2022 年的希望。

### 摘要

2021 年共检测和披露的在野 0day 漏洞有 58 个，这是自从 2014 年年中 Project Zero
团队开始跟踪以来记录到最多的一年，是之前的最高值——2015 年检测到 28 个的两倍多，2020 年我们仅检测到 25 个。自 2014
年年中以来，我们一直在[此表格](https://docs.google.com/spreadsheets/d/1lkNJ0uQwbeC1ZTRrxdtuPLCIl7mlUreoKfSIgajnSyY/edit#gid=0)中跟踪公开的在野利用
0day 漏洞。

虽然我们经常谈论在野 **利用** 的 0day 漏洞数量 **，** 但我们实际上讨论的是在野 **检测到和披露** 的 0day
漏洞利用数量。这也是我们的第一个结论：2021 年在野 0day 漏洞的大幅上升是由于检测和披露的增加，而不是简单的 0day 漏洞利用的增加。

通过对这些在野 0day 的分析，我们发现攻击者的方法实际上与前几年相比并没有太大变化，他们成功地使用了相同的模式和技术，并针对相同的攻击面。Project
Zero 团队的使命是“让利用 0day 变得更难”。总的来说，当攻击者无法使用公开的方法和技术来开发利用时，0day 的利用才将更加困难。而 2021
年这 58 个 0day，与以前公开已知的漏洞都很相似，只有两个 0day
脱颖而出：一个是因为其漏洞利用的技术复杂性，另一个是因为它使用逻辑错误来逃离沙箱。

因此，虽然我们认识到业界在检测和披露在野 0day 漏洞数量方面取得了进步，但我们也承认还有很多改进工作要做。 攻击者利用 0day
的事实表明了，他们能够使用先前已知的技术和方法取得成功，而不必投入开发新的技术，这对科技行业来说也是一个机会。

我们在 2021 年拥有比过去更多的数据点来了解攻击者的行为，然而，这些数据也给我们留下了更多的问题。攻击者不会分享他们正在使用的
0day，以及我们在调查中遗漏了多少 0day，因此我们永远无法确切知道这些公开披露的 0day 所占比例是多少。

根据我们对 2021 年 0day 的分析，我们希望在 2022 年看到以下进展，以继续采取措施使 0day利用变得更有难度：

  1. 所有厂商都同意在其安全公告中披露漏洞的在野利用状态；
  2. 漏洞利用示例或漏洞利用的详细技术描述可以更广泛的共享；
  3. 继续共同努力减少内存损坏漏洞，或者使其无法被利用。启动一些缓解措施来影响内存损坏漏洞的利用。

### 在野 0day 漏洞破纪录的一年

2021 年是在野 0day 漏洞数量创纪录的一年。到底发生了什么呢？
[![](https://images.seebug.org/content/images/2022/04/c5a619c1-7630-4b4f-9f5c-f4d5fb357d81.png-w331s)](https://docs.google.com/spreadsheets/d/1lkNJ0uQwbeC1ZTRrxdtuPLCIl7mlUreoKfSIgajnSyY/edit#gid=2129022708
"!\[\]\(https://images.seebug.org/content/images/2022/04/c5a619c1-7630-4b4f-9f5c-f4d5fb357d81.png-w331s\)")

是软件安全性越来越差？还是攻击者更多地使用了 0day 漏洞？还是我们发现和披露 0day 的能力有所提高？从 2020 年到 2021
年的显著增长，我们认为这主要是由于后者。虽然我们认为过去几年攻击者对 0day
利用的兴趣和投入一直在稳步增长，而且软件安全性也仍需迫切提高，但似乎最主要的原因还是安全行业检测和披露 0day 漏洞的能力提升了。

虽然我们经常谈论“在野 **利用** 的 0day 漏洞”，但我们实际调查的是“ **检测到并披露** 的在野利用 0day 漏洞”。除了 **利用**
之外，还有更多因素导致该数量的增加，最值得注意的是：检测和披露。更好地检测 0day 漏洞和更透明地披露被利用的 0day
漏洞是行业安全和进步的一项积极指标。

总而言之，我们可以将在野 0day 数量的提升分解为：

  * 更多的在野 0day 漏洞检测；
  * 更多的公开披露在野 0-day 漏洞利用。

#### 更多检测

在 [2019 年的回顾中](https://googleprojectzero.blogspot.com/2020/07/detection-deficit-year-in-review-of-0.html)，我们写了关于“检测赤字”——“ **作为一个社区，我们严重缺乏检测在野利用 0day
的能力，以至于收集数据的缺乏和偏差，使我们无法得出有意义的结论** 。” 在过去的两年里，我们相信这方面已经取得了进展。

我们听说有更多人已经开始致力于检测 0day 漏洞。从数量上看，虽然是一个非常粗略的衡量标准，但我们也看到报告的在野 0day
数量正在增加。所以有理由认为，如果努力寻找 0day 漏洞利用的人数增加，那么检测到的在野 0day 漏洞数量可能会增加。

[![](https://images.seebug.org/content/images/2022/04/51962db4-e509-4f4c-b27f-9af20a71da65.png-w331s)](https://docs.google.com/spreadsheets/d/1lkNJ0uQwbeC1ZTRrxdtuPLCIl7mlUreoKfSIgajnSyY/edit#gid=2129022708
"!\[\]\(https://images.seebug.org/content/images/2022/04/51962db4-e509-4f4c-b27f-9af20a71da65.png-w331s\)")

[![](https://images.seebug.org/content/images/2022/04/52a0dfd7-eaf9-4780-8bf3-97a66463d42f.png-w331s)](https://docs.google.com/spreadsheets/d/1lkNJ0uQwbeC1ZTRrxdtuPLCIl7mlUreoKfSIgajnSyY/edit#gid=2129022708
"!\[\]\(https://images.seebug.org/content/images/2022/04/52a0dfd7-eaf9-4780-8bf3-97a66463d42f.png-w331s\)")

我们还看到在自己产品中检测到在野 0day 漏洞的厂商数量也在增加，无论这些厂商之前是否检测，在 2021
年他们似乎找到了更成功的方法。厂商对他们自身产品有拥有更多的遥测技术和全面的知识，因此他们投资检测针对自己产品的
0day。如上图所示，厂商在自家产品中发现的在野 0day 数量显著增加。谷歌在他们自己的产品中发现了 7 个 0day，而微软在他们的产品中发现了 10
个！

#### 更多披露

在野 0day 漏洞数量增加的第二个原因就是由于有了更多地披露。 Apple 和 Google Android（这里把“Google”和“Google
Android”区分开，是因为 Google Chrome 在过去几年一直安全公告中有添加注释） 首先分别在 2020 年 11 月和 2021 年 1
月开始在其安全公告中使用有关潜在野外利用的信息来标记漏洞。当厂商不在发布公告中添加注释时，我们了解 0day
被疯狂利用的唯一方法是发现该利用的研究人员站出来说明。如果 Apple 和 Google Android
之前没有注释他们的漏洞发布公告，公众可能不会知道至少有 7 个 Apple 的在野 0day 漏洞和 5 个 Android 的在野 0day
漏洞。为什么？因为这些漏洞是由“匿名人士”报道的，如果他们不想因为发现漏洞而受到赞扬，他们就不太可能公开说这些漏洞有被利用的迹象。 如果 Apple 和
Google Android 没有透明化地注释它们的安全公告，那么就有 12 个 0day 就不会被列入今年的漏洞列表。

[![](https://images.seebug.org/content/images/2022/04/bcb7fefe-f07d-4f91-b4e4-6dca0da5949f.png-w331s)](https://docs.google.com/spreadsheets/d/1lkNJ0uQwbeC1ZTRrxdtuPLCIl7mlUreoKfSIgajnSyY/edit#gid=2129022708
"!\[\]\(https://images.seebug.org/content/images/2022/04/bcb7fefe-f07d-4f91-b4e4-6dca0da5949f.png-w331s\)")

向 Microsoft、Google Chrome 和 Adobe 致敬并感谢他们多年来一直在为其安全公告添加注释以提高漏洞状态透明化。还要感谢
Apache 在
过去一年中还为[CVE-2021-41773](https://httpd.apache.org/security/vulnerabilities_24.html)
的公告添加了注释。

高通和 ARM 产品中的在野 0day 在 Android 安全公告中被注释为在野，但在厂商自己的安全公告中却没有。

很有可能在 2021 年，还有其他 0day 在野利用并被检测到，但厂商在其公告中并未提及这一点。在 2022
年，我们希望更多厂商在修补已被广泛利用的漏洞时注意这一点。在我们确信所有厂商都在透明地披露在野利用状态之前，还有一个大的问题：到底有多少个在野 0day
被发现了，但没有被厂商公开标注。

### 新的一年，不变的技术

在 2021 年我们拥有破纪录数量的数据点，以了解攻击者如何实际利用 0day
漏洞。不过，让人有点惊讶的是，在所有这些数据点中，这些数据中并没有什么新东西。0day
漏洞被认为是攻击者可以使用的最先进的攻击方法之一，因此我们很容易从中总结出攻击者使用的特殊技巧和攻击面。但相反，我们在 2021 年发现的 0day
基本上遵循之前在公开研究中出现的相同模式、攻击面和利用方法。一旦“利用 0day
很困难”，攻击者要想成功就必须使用前所未有的利用方法，以及在新的攻击面中找到新的漏洞。总体来说，这一年的数据并没有展现出这一点。在 58 个 0day
中，除了两个例外（在下面的 iOS 部分中描述），我们看到的一切都非常标准。

在这一年中的 58 个在野 0day 中，有 39 个也就是 67%
是内存损坏漏洞。在过去的几十年里，内存损坏漏洞一直是攻击软件的标准，并且仍然是攻击者取得成功的方式。在这些内存损坏漏洞中，大多数还停留在非常普遍和众所周知的漏洞类型：

  * 17 个释放后重用漏洞
  * 6 个越界读写漏洞
  * 4 个缓冲区溢出漏洞
  * 4 个整数溢出漏洞

接下来，我们将深入探讨今年每个主流平台的在野 0day漏洞。分享漏洞利用的趋势，以及解释为什么我们所看到的非常普通。

#### Chromium (Chrome)

Chromium 在 2021 年检测和披露的 0day 数量创下历史新高，有 14 个。在这 14 个中，10 个是渲染器远程代码执行漏洞，2
个是沙箱逃逸漏洞，1 个是信息泄露漏洞，还有 1 个被用于打开除谷歌 Chrome 之外的 Android 应用程序的网页。

14 个 0day 漏洞位于以下组件中：

  * 6 个 JavaScript 引擎 - v8（[CVE-2021-21148](https://chromereleases.googleblog.com/2021/02/stable-channel-update-for-desktop_4.html)、[CVE-2021-30551](https://chromereleases.googleblog.com/2021/02/stable-channel-update-for-desktop_4.html)、[CVE-2021-30563](https://chromereleases.googleblog.com/2021/07/stable-channel-update-for-desktop.html)、[CVE-2021-30632](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-30632.html)、[CVE-2021-37975](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-37975.html)、[CVE-2021-38003](https://chromereleases.googleblog.com/2021/10/stable-channel-update-for-desktop_28.html)）

  * 2 个 DOM 引擎 - Blink ( [CVE-2021-21193](https://chromereleases.googleblog.com/2021/03/stable-channel-update-for-desktop_12.html) & [CVE-2021-21206](https://chromereleases.googleblog.com/2021/04/stable-channel-update-for-desktop.html) )

  * 1 个 WebGL ( [CVE-2021-30554](https://chromereleases.googleblog.com/2021/06/stable-channel-update-for-desktop_17.html) )

  * 1 个 IndexedDB ( [CVE-2021-30633](https://chromereleases.googleblog.com/2021/09/stable-channel-update-for-desktop.html) )

  * 1 个 webaudio ( [CVE-2021-21166](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-21166.html) )

  * 1 个 Portals ( [CVE-2021-37973](https://chromereleases.googleblog.com/2021/09/stable-channel-update-for-desktop_24.html) )

  * 1 个 Android Intents ( [CVE-2021-38000](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-38000.html) )

  * 1 个内核 ( [CVE-2021-37976](https://chromereleases.googleblog.com/2021/09/stable-channel-update-for-desktop_30.html) )

当我们查看这些漏洞所针对的组件时，它们都是在以前公开的安全研究和漏洞利用中看到过的攻击面。如果有不同的话，与以前相比，DOM
的漏洞少了一些，而针对浏览器的这些其他组件（如 IndexedDB 和 WebGL）则更多。14 个 Chromium 0day 中有 13
个是内存损坏漏洞。与去年类似，这些内存损坏漏洞中的大多数都是释放后重用漏洞。

一些 Chromium 漏洞甚至与之前的在野 0day
相似。[CVE-2021-21166](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-21166.html) 是 webaudio
中`ScriptProcessorNode::Process()`
中的一个问题，主线程和音频渲染线程都可以同时访问缓冲区。[CVE-2019-13720](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2019/CVE-2019-13720.html) 是 2019 年的一个 0day。它是 webaudio
中 `ConvolverHandler::Process()`中的一个漏洞，也是主线程和音频渲染线程都可以同时访问缓冲区。

[CVE-2021-30632](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-30632.html) 是 2021 年的另一个 Chromium 在野 0day。这是 Chromium 的
JavaScript 引擎 v8 中 TurboFan JIT
中的类型混淆，在修改属性映射后，TurboFan不能对代码进行反优化。CVE-2021-30632 特别处理存储全局属性的代码。CVE-2020-16009
也是一个在野 0day，原因是在地图弃用后，Turbofan未能对代码进行反优化。

#### WebKit (Safari)

在 2021 年之前，Apple 只承认了 1 个针对 WebKit/Safari 的公开已知的在野 0day，是由外部研究人员的贡献。在 2021
年这个数量达 7 个。因为没有历史样本可供参考，我们很难评估这其中的趋势或变化。所以，我们在其他未知的 Safari 漏洞和其他浏览器 0day
漏洞的背景下来看 2021 年的 WebKit 漏洞。

7 个在野 0day 分别针对以下组件：

  * 4 个 Javascript 引擎 - JavaScript 内核（[CVE-2021-1870](https://support.apple.com/en-us/HT212146)、[CVE-2021-1871](https://support.apple.com/en-us/HT212146)、[CVE-2021-30663](https://support.apple.com/en-us/HT212336)、[CVE-2021-30665](https://support.apple.com/en-us/HT212336)）

  * 1 个 IndexedDB ( [CVE-2021-30858](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-30858.html) )

  * 1 个 Storage ( [CVE-2021-30661](https://support.apple.com/en-us/HT212317) )

  * 1 个插件( [CVE-2021-1879](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-1879.html) )

有点惊喜是没有发现和披露 DOM 错误。在前几年，DOM 引擎中的漏洞通常占浏览器 0day 的 15-20%，但 2021 年 WebKit
没有检测到和披露这类。

如果攻击者开始转向其他模块，例如第三方库或 IndexedDB
之类的东西，这也就不足为奇了。今后，这些模块可能对攻击者更有帮助，因为漏洞可能存在于多个浏览器或平台中。 例如，Chromium 中的 webaudio
漏洞 [CVE-2021-21166 ](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-21166.html)也存在于 WebKit 中，尽管没有证据表明它在 WebKit
中被广泛利用，它也被修复为 [CVE-2021-1844](https://support.apple.com/en-us/HT212223)。在 2021
年针对 Safari 使用的 IndexedDB 在野
0day，[CVE-2021-30858](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-30858.html)，与 2020 年 1 月在 Chromium
中修复的一个[漏洞](https://bugs.chromium.org/p/chromium/issues/detail?id=1032890)非常非常相似。

#### Internet Explorer

自从我们开始调查在野 0day 以来，Internet Explorer 每年的 0day 数量一直非常稳定。尽管 Internet Explorer
在浏览器用户中的市场份额持续下降，但 2021 年实际上与 2016 年我们所追溯的在野 0day 数量齐平。

[
![](https://images.seebug.org/content/images/2022/04/b5e3cd51-d173-4933-8a14-d30c309be711.png-w331s)](https://docs.google.com/spreadsheets/d/1lkNJ0uQwbeC1ZTRrxdtuPLCIl7mlUreoKfSIgajnSyY/edit#gid=2129022708
"
!\[\]\(https://images.seebug.org/content/images/2022/04/b5e3cd51-d173-4933-8a14-d30c309be711.png-w331s\)")

尽管市场份额发生了变化，为什么我们看到的在野 0day 数量变化如此之小呢？即使用户不使用 Internet Explorer
作为其浏览器，Internet Explorer 仍然是初始进入 Windows 机器的成熟攻击面。虽然 0day
数量与我们在前几年看到的基本一致，但攻击的目标组件和发送方式发生了变化。2021 年出现的 4 个 0day 中有 3 个针对 MSHTML
浏览器引擎，并且是通过 Office 文档或其他文件格式发送给目标的。

4个 0day 分别针对以下组件：

  * MSHTML 浏览器引擎（[CVE-2021-26411](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-26411.html)、[CVE-2021-33742](https://googleprojectzero.github.io/0days-in-the-wild/0day-RCAs/2021/CVE-2021-33742.html)、[CVE-2021-40444](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-40444)）

  * Javascript 引擎 - JScript9 ( [CVE-2021-34448](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-34448) )

针对 [CVE-2021-26411](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-26411.html) 的攻击目标最初收到一个`.mht`文件，该文件提示用户在
Internet Explorer 中打开。一旦在 Internet Explorer
中打开它，漏洞利用程序就会被下载并运行。[CVE-2021-33742](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-33742.html)
和[CVE-2021-40444](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-40444) 通过恶意 Office 文档发送给目标。

[CVE-2021-26411](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-26411.html) 和
[CVE-2021-33742](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-33742.html)
是两种常见的内存损坏漏洞模式：一个是释放后重用漏洞，是由于在使用对象的两个操作之间有一个用户控制的回调，用户在回调期间释放对象；一个是缓冲区溢出漏洞。

在使用 [CVE-2021-40444](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-40444) 的利用链中使用了几个不同的漏洞，但 MSHTML 中的一个是一旦打开 Office
文档，有效负载就会运行：下载一个 CAB 文件，解压，然后执行该CAB DLL中的一个函数。与前两个 MSHTML 漏洞不同，这是 URL
解析中的逻辑漏洞，而不是内存损坏漏洞。

#### Windows

与往年相比，Windows 是我们看到目标组件变化最大的平台。然而，这种转变通常已经进行了几年，并预测到 2020 年 Windows 7
的生命周期结束，因此它不是特别新颖。

2021 年有 10 个 Windows 在野 0day 针对 7 个不同的组件：

  * 2 个 Enhanced crypto provider （[CVE-2021-31199](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-31199)、[CVE-2021-31201](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-31201)）

  * 2 个 NTOS 内核（[CVE-2021-33771](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-33771)、[CVE-2021-31979](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-31979)）

  * 2 个 Win32k ( [CVE-2021-1732](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-1732.html)、[CVE-2021-40449](https://securelist.com/mysterysnail-attacks-with-windows-zero-day/104509/) )

  * 1 个 Windows update medic ( [CVE-2021-36948](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-36948) )

  * 1 个 SuperFetch ( [CVE-2021-31955](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-31955) )

  * 1 个 dwmcore.dll ( [CVE-2021-28310](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-28310) )

  * 1 个 ntfs.sys ( [CVE-2021-31956](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-31956) )

不同的目标组件的数量与过去几年相比有所不同。例如，2019 年 75% 的 Windows 0day 以 Win32k 为目标，而在 2021 年
Win32k 仅占 Windows 0day 的 20%。之所以能预料到这一点，是因为 2019 年针对 Win32k 的 8 个 0day 中有 6
个没有针对当时最新版本的 Windows 10，而是旧版本。随着 Windows 10 开始投入越来越多的资源来减少 Win32k
的攻击面，因此随着那些旧版本的生命周期结束，Win32k 越来越没有吸引力。

与多年来看到的许多 Win32k 漏洞类似，两个 2021 年的 Win32k 在野 0day
是由于用户自定义回调造成的。用户调用在回调期间更改对象状态的函数，而 Win32k
无法正确处理这些更改。[CVE-2021-1732](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-1732.html)
是一个类型混淆漏洞，由于`xxxClientAllocWindowClassExtraBytes`
中的用户回调导致越界读写。如果在回调期间调用了`NtUserConsoleControl`，则会在窗口结构中设置一个标志，表明字段是内核堆中的偏移量。`xxxClientAllocWindowClassExtraBytes`不检查这个，并在不清除标志的情况下将该字段作为用户模式指针写入。在2022年检测和披露的第一个在野
0day，[CVE-2022-21882](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2022/CVE-2022-21882.html)，是由于
[CVE-2021-1732](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-1732.html)
实际上没有完全修复。攻击者找到了绕过原始补丁触发漏洞的方法。[CVE-2021-40449](https://securelist.com/mysterysnail-attacks-with-windows-zero-day/104509/)
是NtGdiResetDC中的一个释放后重用漏洞，因为在用户回调期间对象被释放。

#### iOS/macOS

正如上面“更多披露”部分所讨论的，2021 年是 Apple 第一次在其漏洞公告中完整注释其漏洞状态。今年检测并披露了 5 个 iOS 在野
0day。还发现了第一个公开的 macOS 在野 0day([CVE-2021-30869](https://blog.google/threat-analysis-group/analyzing-watering-hole-campaign-using-macos-exploits/))。在本节中，我们将把 iOS 和 macOS一同讨论，因为这两个操作系统包含相似的组件，以及 macOS 的样本量非常小。

[![](https://images.seebug.org/content/images/2022/04/5906d7ef-92d9-4d16-8d97-d6067a21bfaf.png-w331s)](https://docs.google.com/spreadsheets/d/1lkNJ0uQwbeC1ZTRrxdtuPLCIl7mlUreoKfSIgajnSyY/edit#gid=2129022708
"!\[\]\(https://images.seebug.org/content/images/2022/04/5906d7ef-92d9-4d16-8d97-d6067a21bfaf.png-w331s\)")

对于总共 5 个 iOS 和 macOS 在野 0day ，他们针对 3 个不同的攻击面：

  * IOMobileFrameBuffer ( [CVE-2021-30807](https://support.apple.com/en-us/HT212623)、[CVE-2021-30883](https://support.apple.com/en-us/HT212846) ) 

  * XNU 内核 ( [CVE-2021-1782](https://support.apple.com/en-us/HT212146) & [CVE-2021-30869](https://blog.google/threat-analysis-group/analyzing-watering-hole-campaign-using-macos-exploits/) )

  * CoreGraphics ( [CVE-2021-30860](https://googleprojectzero.blogspot.com/2021/12/a-deep-dive-into-nso-zero-click.html) )

  * CommCenter（[FORCEDENTRY 沙箱逃逸](https://googleprojectzero.blogspot.com/2022/03/forcedentry-sandbox-escape.html) \- 已申请 CVE，尚未分配）

这 4 个攻击面并不新颖。IOMobileFrameBuffer 多年来一直是安全研究的目标。例如，2016 年盘古越狱使用了
[CVE-2016-4654](https://www.blackhat.com/docs/us-16/materials/us-16-Wang-Pangu-9-Internals.pdf)，这是 IOMobileFrameBuffer 中的堆缓冲区溢出漏洞。IOMobileFrameBuffer
管理屏幕的帧缓冲区，对于 iPhone 11 (A13) 及更低版本，IOMobileFrameBuffer 是内核驱动程序。从 A14 开始，它在协处理器
DCP 上运行。这是一个受欢迎的攻击面，因为从历史上看，它可以从沙盒应用访问。2021 年，IOMobileFrameBuffer 中有两个在野
0day。[CVE-2021-30807](https://support.apple.com/en-us/HT212623)
是越界读取漏洞，[CVE-2021-30883](https://support.apple.com/en-us/HT212846)
是整数溢出漏洞，都是常见的内存损坏漏洞。2022 年，我们检测到 IOMobileFrameBuffer 中另一个在野
0day，[CVE-2022-22587](https://support.apple.com/en-us/HT213053)。

一个 iOS 0day 和 macOS 0day 都利用了 XNU 内核中的漏洞，并且这两个漏洞都在与 XNU 的进程间通信 (IPC)
功能相关的代码中。[CVE-2021-1782](https://support.apple.com/en-us/HT212146) 利用了 mach
凭证中的漏洞，而 [CVE-2021-30869](https://blog.google/threat-analysis-group/analyzing-watering-hole-campaign-using-macos-exploits/) 利用了 mach 消息中的漏洞。这不是我们第一次看到 iOS
在野 0day，更不用说针对 mach 凭证和 mach
消息的安全研究了。[CVE-2019-6625](https://support.apple.com/en-us/HT209443) 作为[针对 iOS
11.4.1-12.1.2 的利用链](https://googleprojectzero.blogspot.com/2019/08/in-wild-ios-exploit-chain-5.html)的一部分被利用 ，也是mach
凭证中的一个[漏洞](https://googleprojectzero.blogspot.com/2019/01/voucherswap-exploiting-mig-reference.html)。

Mach 消息也一直是安全研究的热门目标。在 2020 年，mach 消息中也有两个在野
0day：[CVE-2020-27932](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2020/CVE-2020-27932.html)
和[CVE-2020-27950](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2020/CVE-2020-27950.html)。今年的
[CVE-2021-30869](https://blog.google/threat-analysis-group/analyzing-watering-hole-campaign-using-macos-exploits/) 与 2020 年的
[CVE-2020-27932](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2020/CVE-2020-27932.html) 非常接近。 Tielei Wang 和 Xinru Chi 实际上在 2021 年 4 月的
Zer0con 2021
上介绍了这个[漏洞](https://github.com/wangtielei/Slides/blob/main/zer0con21.pdf)。他们说在对
[CVE-2020-27932](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2020/CVE-2020-27932.html) 进行变体分析时发现了这个漏洞。Tielei Wang
在推特[解释](https://twitter.com/WangTielei/status/1486266258152726530)他们在 2020 年
12 月发现了该漏洞，并注意到它已在 iOS 14.4 和 macOS 11.2 的 beta 版本中得到修复，这就是他们在 Zer0Con
上展示它的原因。在野利用仅针对 macOS 10，但使用了与所介绍相同的利用技术。

两个
FORCEDENTRY（[CVE-2021-30860](https://googleprojectzero.blogspot.com/2021/12/a-deep-dive-into-nso-zero-click.html)
和[沙盒逃逸](https://googleprojectzero.blogspot.com/2022/03/forcedentry-sandbox-escape.html)）漏洞是今年我们都眼前一亮的漏洞
。因为[CVE-2021-30860](https://googleprojectzero.blogspot.com/2021/12/a-deep-dive-into-nso-zero-click.html)，CoreGraphics 中的整数溢出漏洞：

  1. 多年来我们都听说过攻击者如何使用 0-click iMessage 漏洞，终于我们有了一个公开的例子；
  2. 该漏洞利用十分令人印象深刻。

而沙箱逃逸（CVE 已申请，尚未分配）令人印象深刻，是因为这是我们见过的为数不多的只使用逻辑错误而不是标准内存损坏漏洞的沙箱逃逸之一。

对于[CVE-2021-30860](https://googleprojectzero.blogspot.com/2021/12/a-deep-dive-into-nso-zero-click.html)，漏洞本身并不是特别引人注目：CoreGraphics PDF 解码器的 JBIG2
解析器中的经典整数溢出。然而，Samuel Gro? 和 Ian Beer
将该漏洞描述为“他们见过的技术最复杂的漏洞之一”。他们的[博文](https://googleprojectzero.blogspot.com/2021/12/a-deep-dive-into-nso-zero-click.html)分享了漏洞细节，但重点是该漏洞利用 JBIG2
中可用的逻辑运算符来构建用于构建自己的计算机架构的 NAND 门。然后，该漏洞利用该新的自定义架构编写其剩余的漏洞利用。他们的博文中说道：

_他们使用超过 70,000 个定义逻辑位操作的段命令，定义了一个小型计算机体系结构，具有寄存器和完整的 64
位加法器和比较器等功能，用于搜索内存和执行算术运算。它不如 Javascript 快，但在计算上基本上是等效的。_

_沙盒逃逸漏洞的引导操作被编写为在这个逻辑电路上运行，整个程序运行在这个怪异的模拟环境中，这个模拟环境是通过一个JBIG2流进行一次解压缩而创建的。这很不可思议，同时也很可怕。_

这是使 0day 漏洞利用变得困难的一个例子 ： 攻击者必须开发一种新颖的方法来利用漏洞，而这种方法需要大量的专业知识或者时间来开发。 今年，两个
FORCEDENTRY 漏洞是 58 个 0day 中唯一给我们留下深刻印象的。希望在未来，任何成功的漏洞利用都需要像这样。

#### Android

今年检测并披露了 7 个 Android 在野 0day。在 2021 年之前只有 1 个，而且是在 2019
年：[CVE-2019-2215](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2019/CVE-2019-2215.html)。与 WebKit
一样，这种缺乏数据的情况让我们很难评估其趋势和变化。所以，我们将其与公共安全研究进行比较。

对于 7 个 Android 0day，他们针对以下组件：

  * Qualcomm Adreno GPU 驱动程序（[CVE-2020-11261](https://source.android.com/security/bulletin/2021-01-01)、[CVE-2021-1905](https://googleprojectzero.github.io/0days-in-the-wild/0day-RCAs/2021/CVE-2021-1905.html)、[CVE-2021-1906](https://source.android.com/security/bulletin/2021-05-01)）

  * ARM Mali GPU 驱动程序（[CVE-2021-28663](https://source.android.com/security/bulletin/2021-05-01)、[CVE-2021-28664](https://source.android.com/security/bulletin/2021-05-01)）

  * Upstream Linux 内核 ( [CVE-2021-1048](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-1048.html) , [CVE-2021-0920](https://source.android.com/security/bulletin/2021-11-01#kernel-components) )

2021 年的 7 个 0day 中有 5 个针对 GPU 驱动程序。 考虑到 Android 生态系统的演变以及最近对 Android
的公共安全研究，这实际上并不令人惊讶。Android 生态系统相当分散：许多不同的内核版本、不同的制造商定制等等。如果攻击者想要针对“Android
设备”，他们通常需要维护许多不同的漏洞，才能覆盖相当大比例的 Android 生态系统。但是，如果攻击者选择针对 GPU
内核驱动程序，他们将只需要两个漏洞，因为大多数 Android 设备使用 2 个 GPU 中的一个：Qualcomm Adreno GPU 或 ARM
Mali GPU。

公共安全研究在过去几年也反映了这一选择，在针对 Android 设备开发完整的漏洞利用链（用于防御目的）时， [Guang
Gong](https://github.com/secmob/TiYunZong-An-Exploit-Chain-to-Remotely-Root-Modern-Android-Devices/blob/master/us-20-Gong-TiYunZong-An-Exploit-Chain-to-Remotely-Root-Modern-Android-Devices-wp.pdf)、[Man Yue
Mo](https://securitylab.github.com/research/one_day_short_of_a_fullchain_android/)和[Ben
Hawkes](https://googleprojectzero.blogspot.com/2020/09/attacking-qualcomm-adreno-gpu.html) 都选择攻击 GPU 内核驱动程序以进行本地提权。看到在野 0day 也针对 GPU，这更像是一种确认，而不是揭示。在针对
GPU 驱动程序的 5 个 0day 中，3 个在 Qualcomm Adreno 驱动程序中，2 个在 ARM Mali 驱动程序中。

两个非 GPU 驱动程序
0day（[CVE-2021-0920](https://source.android.com/security/bulletin/2021-11-01#kernel-components) 和[CVE-2021-1048](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-1048.html)）针对 Linux 内核。不幸的是，这 2 个漏洞与 2019 年出现的
Android 在野 0day 具有一个共同特征：3 个漏洞在 Android 被利用之前之前是已知的。尽管样本量很小，我们还是惊讶地发现所有已知针对内核的
Android 0day 都是在被利用之前实际上就已知的。

现在称为
[CVE-2021-0920](https://source.android.com/security/bulletin/2021-11-01#kernel-components) 的漏洞实际上是在 2016 年 9 月发现的，并在[ Linux
内核邮件列表](https://lore.kernel.org/lkml/CAOssrKcfncAYsQWkfLGFgoOxAQJVT2hYVWdBA6Cw7hhO8RJ_wQ@mail.gmail.com/)中进行了讨论。甚至早在[
2016 年](https://lore.kernel.org/lkml/1475150954-10152-1-git-send-email-mszeredi@redhat.com/)就开发了一个补丁，但最终没有提交。 在检测到针对 Android 的在野漏洞利用后，该漏洞最终于 2021 年 7
月在 Linux
内核中得到[修复](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=cbcf01128d0a92e131bd09f1688fe032480b65ca)，[该补丁](https://source.android.com/security/bulletin/2021-11-01#kernel-components)随后于 2021 年 11 月进入Android 安全公告。

[CVE-2021-1048](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-1048.html) 在 Linux 内核中修补后，在 Android 中 14 个月仍未修补。Linux
内核实际上只在几周内易受此问题的影响，但由于 Android 补丁，这几周对某些 Android 设备来说几乎变成一年。如果 Android OEM
同步到上游内核，那么他们很可能在某个时候针对该漏洞进行了修补。但是许多设备，例如最近的三星设备，都没有这样做，因此很容易受到攻击。

### Microsoft Exchange Server

2021 年，有 5 个针对 Microsoft Exchange Server 的在野 0day。这是我们开始跟踪在野 0day 以来第一次检测和披露
Exchange Server
的漏洞。前4个（[CVE-2021-26855](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-26855.html)、[CVE-2021-26857](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26857)、[CVE-2021-26858](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26858)和[CVE-2021-27065](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-27065)）都同时披露和修补，并且在[一次操作](https://www.microsoft.com/security/blog/2021/03/02/hafnium-targeting-exchange-servers/)中一起使用。第5个 (
[CVE-2021-42321](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-42321) ) 于 2021 年 11
月自行修补，这个漏洞在天府杯上展示，然后被微软在野发现。攻击者至少需要另一个 0day 才能成功利用这个漏洞，因为它是一个身份验证后漏洞。目前没有发现其它
0day 和 [CVE-2021-42321](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-42321) 作为一个利用链所使用。

在前 4 个 Exchange 在野 0day
中，[CVE-2021-26855](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-26855.html)（也称为“ProxyLogon”）是唯一一个预授权的。[CVE-2021-26855](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2021/CVE-2021-26855.html) 是一个服务器端请求伪造 (SSRF)
漏洞，允许未经身份验证的攻击者作为 Exchange 服务器发送任意 HTTP
请求。其他3个漏洞是身份验证后漏洞。例如，[CVE-2021-26858](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26858)
和[CVE-2021-27065](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-27065)
允许攻击者将任意文件写入系统。[CVE-2021-26857](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26857) 是由于统一消息服务中的反序列化错误导致的远程代码执行漏洞，允许攻击者以 SYSTEM
用户权限运行代码。

[CVE-2021-42321](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-42321) 与
[CVE-2021-26858](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26858) 一样，是由于反序列化不安全而导致的身份验证后 RCE 漏洞。微软似乎在尝试强化
Exchange 时无意中引入了另一个反序列化漏洞。

尽管 2021 年在 Exchange 中检测并披露了大量的 0day，但它们仅在两个不同的活动中被利用。这就是为什么我们不建议使用产品中的 0day
数量作为评估产品安全性的指标。要求攻击者使用 4 个 0day获得成功，比攻击者只需要一个 0day 来获得访问权限更可取。

虽然这是 Project Zero 团队首次检测和披露 Exchange 在野 0day，但这并不意外。2020 年Exchange Server 被利用了
[nday](https://www.cisa.gov/uscert/ncas/current-activity/2020/03/10/unpatched-microsoft-exchange-servers-vulnerable-cve-2020-0688)。无论这是攻击者开始 0day
漏洞利用的第一年，还是防御者开始检测 0day 漏洞利用的第一年，这都不是一个意外的变化，很可能会持续到 2022 年。

### 突出的问题

尽管在检测和披露方面取得了进展，但这也表明还有很多工作要做。我们获得的数据越多，关于检测偏差的问题就越多，我们遗漏了什么以及为什么，以及厂商和研究人员都需要提高透明度。

除非攻击者决定与我们分享他们所有的漏洞利用，否则我们不能完全知道有多少 0day
是公开的。然而，当我们把作为安全研究人员的专业知识和业内其他人的见闻结合起来时，它描绘出了一些我们很可能缺失的数据。因此，进入2022年，我们会问自己一些关键问题：

#### 未知的 0day 在哪里？

尽管 2021 年发现了许多 0day，但发现的 0day 中仍然缺少关键目标。例如，我们知道 WhatsApp、Signal、Telegram
等即时通讯应用是攻击者感兴趣的目标，但只有 1 个即时通讯应用 iMessage，在过去一年中发现了 0day。自从我们在 2014
年年中开始跟踪以来，总共有2个：2019 年的 WhatsApp 0day 和 2021 年发现的 iMessage 0day。

除了即时通讯应用之外，还有其他平台/目标我们希望看到 0day，但没有或很少有公开示例。例如，自 2014 年年中以来，macOS 和 Linux
各只有一个在野 0day。目前没有已知的针对云、CPU 漏洞或其他手机组件（如 WiFi 芯片或基带）的在野 0day。

这就引出了这样一个问题：这些 0day 的缺乏是由于没有检测到、没有披露，还是两者兼而有之？

#### 一些厂商没有公开的 0day，是因为从未发现，还是因为不公开披露？

除非厂商告诉我们他们将公开披露其所有漏洞的利用状态，否则我们公众不知道没有注释是否意味着没有已知的漏洞利用，或者存在漏洞利用，但厂商只是没有公开分享这些信息。值得庆幸的是，这个问题有一个非常明确的解决方案：当有证据表明他们的产品存在漏洞时，所有设备和软件厂商都同意公开披露。

#### 我们看到相同的漏洞模式是否是因为这是我们知道如何检测的？

正如我们在本报告前面所述，我们在 2021 年看到的所有 0day
都与之前看到的漏洞有相似之处。这让我们想知道这是否真的代表了攻击者所使用的，攻击者是否真的只使用以前公开的错误类别和组件中的漏洞取得成功？
或者我们用已知的漏洞模式来检测所有这些
0day，因为这是我们知道如何检测的？公共安全研究表明，是的，攻击者在大多数情况下仍然能够成功地利用已知组件和错误类别中的漏洞。但我们仍然希望看到一些新奇和意想不到的漏洞。我们早在2019年的年度回顾中就提出了这个问题，现在这个问题仍然存在。

#### spl0itz 在哪里？

要成功利用漏洞，有两个关键部分：被利用的漏洞和利用方法（如何将该漏洞转化为有用的东西）。

但是这份报告只能真正分析其中一个组成部分：漏洞。在 58 个 0day 中，只有 5 个公开了漏洞利用示例。在野发现的 0day
是攻击者的失败案例，也是防御者了解攻击者正在做什么的关键机会，并以此使其更难、更耗时、更昂贵。然而，如果没有利用样本或基于样本的详细技术文章，我们只能专注于修复漏洞而不是减轻利用方法的影响。这意味着攻击者能够继续使用他们现有的利用方法，而不必构建新的利用方法。虽然我们承认共享漏洞利用样本可能具有挑战性（我们也面临这样的挑战！），但我们仍希望在2022年将会有更多共享漏洞利用示例或详细的技术文章，以便我们可以使用一切可能的信息，使攻击者更难利用更多用户。

顺便说一句，如果您愿意与我们分享漏洞利用示例，请与我们联系。无论是与我们分享，让我们撰写详细的技术描述和分析，还是让我们公开分享，我们都很乐意合作。

### 结论

回首 2021 年，我脑海里浮现的是“婴儿阶段”。我们可以看到在 0day
漏洞的检测和披露方面，行业有明显的进步。但更好的检测和披露也突出了其他进步的机会。作为一个行业，我们并没有让 0day
利用变得更加困难。攻击者利用与我们之前看到的类似的漏洞，以及之前被讨论为攻击面的组件中的漏洞取得了成功。我们的目标是每次我们检测到攻击者的一个漏洞时都迫使攻击者从头开始：他们被迫发现一个全新的漏洞，他们必须投入时间学习和分析新的攻击面，他们必须开发一种全新的利用方法。虽然我们在检测和披露方面取得了显著进展，但它向我们展示了可以继续改进的领域。

虽然这一切令人望而生畏，但有希望的是我们以前就这样做过：我们在以前令人生畏的目标上取得了明显的进展。2019 年，我们讨论了 0day
漏洞的巨大检测缺陷，2
年后发现并披露了超过两倍的漏洞。因此，虽然还有很多工作要做，但这是一个容易解决的问题。科技和安全行业可以采取一些具体措施来取得更大进展：

  1. 当有证据表明产品中的漏洞正在被利用时，让所有厂商公开披露成为行业标准行为；
  2. 厂商和安全研究人员共享漏洞利用样本或漏洞利用技术的详细描述；
  3. 继续共同努力减少内存损坏漏洞或使其无法利用。

到 2021 年，我们不断看到对用户和实体使用 0day
漏洞对现实世界的影响。国际特赦组织、公民实验室和其他机构一再强调，政府如何使用商业监控产品来对付记者、人权捍卫者和政府官员。我们看到许多企业都在争先恐后地修复和保护自己免受
Exchange Server 0day 的影响。我们甚至了解到同行安全研究人员已成为朝鲜政府黑客的目标，虽然地球上的大多数人不需要担心自己被 0day
攻击的风险，但 0day 攻击仍然影响着我们所有人。这些 0day
往往会对社会产生巨大的影响，因此我们需要继续尽我们所能，让攻击者更难在这些攻击中取得成功。

2021 年表明我们正走在正确的轨道上并取得了进展，但要让 0day 利用变得艰难，我们还有很多工作要做。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1886/>

