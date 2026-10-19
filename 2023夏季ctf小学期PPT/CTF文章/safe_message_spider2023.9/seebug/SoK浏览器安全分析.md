**译者:知道创宇404实验室翻译组  
原作者：Jungwon Lim _, Yonghwi Jin_ †, Mansour Alharthi, Xiaokuan Zhang, Jinho
Jung, Rajat Gupta, Kuilin Li, Daehee Jang‡, Taesoo Kim**

`摘要`
Web浏览器是每个人日常生活中不可或缺的一部分。它们经常用于注重安全性和隐私敏感的事情，银行交易和检查医疗记录时都会用到。不幸的是，现代Web浏览器过于复杂，难免会有漏洞（例如，Chrome中有2500万行代码），它们作为网络空间接口的作用使它们容易受到攻击。因此，Web浏览器自然成为展示攻击者先进漏洞利用技术和浏览器供应商最先进防御措施的舞台。可以说，Web浏览器是学习最新安全问题和技术的绝佳之地，但由于其快速变化的特性和复杂的代码库，对于大多数安全研究人员来说，
Web浏览器仍然如魔法一般不好捉摸。

为了弥补这一差距，本文将通过研究流行的安全漏洞类型、它们的漏洞利用技术和部署的防御措施,
来系统化讲述现代Web浏览器的安全环境。具体来讲，我们首先介绍了一个统一的架构，展示四大Web浏览器的安全设计。其次，我们分享了近10年有关浏览器漏洞纵向研究的见解。第三，我们提出了应对计划及其有效性的时间表和背景。第四，我们分享了我们在2020年
Pwn2Own
比赛中使用的全链漏洞利用的经验教训。我们相信，这种系统化的关键点梳理可以揭示如何推进改善现代网络浏览器的现状，更重要的是，如何在未来创建安全不易攻破的软件。

## I. 序

Web浏览器在现代互联网连接生活方式中发挥着不可或缺的作用。我们依靠网络浏览器来支付抵押贷款、安排疫苗接种并与世界各地的人们联系。换句话说，网络浏览器成为网络空间的守门人，它们的不安全性对我们社会的安全、公平和隐私构成严重威胁。不幸的是，网络浏览器一直是网络攻击中最具吸引力、最有价值的目标——2021年[58]，50%的0-day漏洞都是对web浏览器的攻击，这威胁到互联网上的每一个人[103],
[141], [195], [196], [211], [230], [231]。

因此，希望使用新型漏洞利用技术入侵的攻击者与希望通过最先进的应对方案保护用户安全的浏览器供应商自然把现代Web浏览器当做战场。浏览器供应商确实是通过以下方式推进现代安全实践的重要参与者:
1\. 不仅开源当前架构和代码，还开源设计过程本身[45]、[52]、[210]; 2\. 引入漏洞赏金奖励以鼓励发现0-day漏洞[116]、[176];
3\. 通过在云上开发和运行最先进的模糊测试器[109]，[111]，主动发现可利用的漏洞

不幸的是，详细的安全设计决策和针对新漏洞利用的新缓解措施的见解通常不是那么容易做到，Web浏览器社区中已经见识到了难度。一部分原因是它们复杂的架构、快速变化的实现方法和庞大的代码库，但主要是因为同时清晰且客观地系统化所有主要Web浏览器的知识并非易事。每个浏览器供应商的专家都试图提供他们对安全设计和决策的看法，例如
Chrome[44]、IE[51]、Firefox[54]。之前在2017年发表的行业报告[90]、[226]主要侧重于以一种临时的、实时的的方式描述个别技术和防御措施，而没有发展学术观点或提供有助于为社区设想未来方向的见解和教训。

本文大胆尝试将现代Web浏览器的安全环境系统化梳理。我们首先提供了四种主要网络浏览器在安全方面的统一模型，并通过使用提供的模型比较和对比它们的安全决策。其次，基于该模型，我们分析了过去10年在每个开源浏览器中发现的安全漏洞，并展示了它们与新应对方案的开发、漏洞赏金计划和已知的漏洞利用技术的关系。第三，根据我们的研究，我们分享我们的见解和经验教训，以激励正在塑造网络浏览器未来的研究人员和开发人员。我们希望这样的尝试可以帮助他们全面了解每个供应商的方法，从而增强他们的安全设计，以最大限度地减少安全影响和攻击面。

`挑战`: 三个独特的特点使得将网络浏览器安全知识系统化变得具有挑战性。 1\. 研究对象不断在变化:
浏览器供应商做出决策非常快速（例如，每周更新），他们的开发速度比人类构建的任何其他软件都要快得多。为了推断出有见地的经验教训，我们努力专注于Web浏览器中的基本设计问题和方法。
2\. 海量的研究量: 现代网络浏览器是用几百万行代码构建的，例如，Chrome由2500万行代码组成
[16]。除了项目规模之外，有关Web浏览器的信息（例如0-day漏洞利用和缓解措施）分散在整个Internet中，无法提供安全形势的整体总结和概述。在本文中，我们将精力集中在四种主要的网络浏览器上，即Chrome、Firefox、Safari和Edge，并研究众多公共资源以解决它们的安全问题：issue跟踪器[43]、[48]、CVE报告
[2]、[4]、[5]、[7]、[9]、[11]、[12]、[14]、[55]、代码库 [30]、[45]、[52]、[60]，以及来自供应商的技术报告
[49]、[58]、[65]、[67]、[79]、[86]、[152]、[161]、[163]、[170]、[171]、[204]、[208]、[230]、[231]。
3\. 单独的规范:
同样重要的是，要就其安全问题提供客观的观点；每个浏览器在做出决策时都有自己的规范和要求（例如，发布截止日期），专注于基本问题是至关重要的。为了解决这个问题，我们提供了一个统一的架构，可以在概念上比较和对比每个浏览器的设计，而不会影响它们的实现细节。

`贡献`: 本文做出以下贡献: \- 提供现代浏览器架构在沙盒方案方面的结构的详细比较； \- 对浏览器漏洞进行为期10年的纵向研究； \-通过详细分析对浏览器漏洞进行分类； \- 研究浏览器上最先进的通用缓解措施； \- 对真实世界的全链漏洞利用进行详细研究。

`非本文的目标`。本研究的主要重点是网络浏览器安全，涉及其自身漏洞的安全性。我们不考虑其他与Web相关的安全问题，例如Web或Web服务器安全问题，例如跨站点脚本(XSS)、SQL注入等。请注意，尽管通用跨站点脚本(UXSS)[166]听起来类似于XSS，它通常源于浏览器的实现和设计中的问题，因此被认为是网络浏览器安全（§III-E）。

## II. 现代浏览器架构

本节提供了每个Web浏览器的统一模型，可以客观地比较它们的方法。

### A. 概述

现代网络浏览器采用最小权限原则，将操作系统进程作为保护域。通过使用进程域，可以使用三种类型的进程来描述每个Web浏览器，即`浏览器(browser)进程`（标记为绿色）、`渲染器(renderer)进程`（标记为洋红色magenta,
实际上在图中偏紫的那部分）和`特定任务的进程`（标记为黄色），如图1所示。

![](https://images.seebug.org/content/images/2022/01/65f7082d-9461-434b-99e2-099b58c9b2c9.png-w331s)

图1: 四大浏览器的内部架构。所有浏览器都部署了一个沙箱（粉红色区域）来限制渲染器，而详细的沙箱方法因底层操作系统而异。浏览器之间存在细微但重要的差异。

`浏览器进程`:
当Web浏览器启动时，浏览器进程以与用户相同的特权级别（即更高的特权）运行，并将沙箱配置文件传递给操作系统以限制其他进程的特权（即较低的特权）。它管理所有子进程（例如渲染器），并且是唯一通过系统调用（和用户界面）直接与用户交互的进程。

`渲染器进程`: 此进程负责解析和渲染不受信任的Web内容。Web上不断增长的数据类型导致渲染器进程包含各种各样的组件，例如媒体解析器、DOM 和 JS
引擎。由于它们是浏览器bug的主要来源，因此它们被限制在限制性沙箱中（参见§II-C）。渲染器进程通常是按浏览器选项卡或每个网页来生成的。每个渲染器的隔离策略因每个Web浏览器的安全策略或功能（例如，站点隔离）、运行时可用资源（例如，移动设备中的内存不足）甚至用户配置而异。

`其他进程`:
现代浏览器的架构是高度模块化的。这种模块化设计使浏览器能够根据进程的角色拥有不同的权限级别。与外部驱动程序交互的服务（例如，网络或GPU进程）被隔离为一个单独的进程，这为不需要此类访问的进程（如渲染器进程）启用了更严格的沙盒。Web浏览器通常也将扩展和插件放在不同的进程中。这可以保护具有更高权限级别的插件免受恶意Web内容的侵害，并保护浏览器在恶意插件的情况下不被劫持。

`进程间通信(IPC)`:
由于这些进程不能直接访问彼此的内存，它们总是通过操作系统提供的IPC通道进行通信，并且通信通常由浏览器（代理）进程进行调解。换句话说，浏览器进程作为一个关系监视器，限制从其他进程直接访问重要数据或高权限操作（例如，cookie或系统调用）。由于这种多进程架构，攻击总是从类似渲染进程这样的低权限进程发起，攻击者的目标是闯入以用户权限运行的浏览器进程。同时，它可以从渲染器进程中的良性bug导致的崩溃中恢复，从而使浏览器对稳定性问题具有弹性。

`同源政策(SOP)`:
实际上，网站由来自不同来源的大量内容组成，例如，将CDN用于常见的JavaScript库，通过iframe嵌入外部站点，或启用社交网络中的点赞按钮。网站的复杂性促成了每个Web浏览器的众多安全策略和独特功能。根据每个网站的来源[94]，浏览器进程和渲染器进程限制允许网页与哪些资源(例如cookie)进行交互，这就是同源策略(SOP)[94]。

### B. 浏览器的差异

到目前为止讨论的设计同样适用于所有四种主流浏览器。然而，如图1所示，一些实现细节会因浏览器的设计及其底层操作系统的不同而有所不同。例如，Chrome和Safari中的
GPU进程与渲染器进程是分开的，使用沙盒配置文件使它们能够访问3D API 平台[67]（参见
§II-C）。此外，Chrome、Firefox和Safari各自有一个单独的进程来处理网络服务，而Chrome网络服务则置于沙箱之外。Chrome团队目前正在实现其网络服务的沙箱
[28]。

`站点隔离`: 沙盒机制的确可以保护浏览器；但是，随着通用跨站脚本 (UXSS)
攻击的出现，攻击者可以窃取用户数据而无需沙箱逃逸。为了处理此类攻击，Chrome团队提出了站点隔离[186]以进一步将不同的站点来源分离到不同的进程中。它为每个站点来源创建了一个专用进程，因此不同站点来源之间没有隐式共享。站点隔离是解决UXSS的有效措施，它也有利于防止基于硬件的瞬态执行攻击[137]、[147]。Firefox有一个类似的项目，名为Fission[175]，它在Firefox_88_Beta[174]中发布。

`JavaScript引擎`: JavaScript引擎是现代浏览器的核心，它将JavaScript代码转换为机器代码。主流浏览器使用即时编译(Just-In-Time, JIT)[36][34][33]来加速代码执行。此外，JIT编译器对所有操作的结果和副作用(side-effects)进行建模，并运行各种分析过程以优化代码。如果其中任何一个出错，就会生成并执行具有内存损坏问题的本机代码，这可能导致严重的安全隐患[26]、[121]。虽然每个引擎都有不同的实现，但它们使用相似的设计原则并具有共同的攻击面（参考§III-D）。因此，攻击者可以构建出跨不同引擎的通用攻击原语，例如fakeobj和addrof原语[154]、[189]以及元素类型转换
[153]、[190]。JavaScript引擎也在浏览器之外被使用（例如Node.js使用V8），放大了JavaScript引擎中安全漏洞的影响。我们在§VI-A中讨论了由同类型的浏览器引擎引起的问题。

`渲染引擎`: 渲染引擎负责解释资源和渲染网页。四大浏览器中的每一个都有自己的渲染引擎：Safari使用WebKit;
Chrome使用Blink（衍生自WebKit）; Firefox使用 Gecko;
Edge使用Blink（替换EdgeHTML）。Web标准[219]、[224]用作浏览器供应商实现其渲染引擎的基线规范和参考。由于Web标准不断发展新功能，渲染引擎也发生了快速变化，即实现新功能或删除已弃用的功能。由于不同的决策过程和实现策略，在不同浏览器的渲染引擎中实现的特性有很大的不同[42]，攻击面[228]因而也是不同的。我们将在§III中讨论攻击面。

### C. 沙盒方案的差异

沙盒会限制程序执行，以防其偏离预期任务。然而，用于构建沙盒环境的底层技术和架构在操作系统之间存在显著差异。为了检查沙盒实现的内部结构，我们进行了如下操作，并在表I中总结了我们的发现。
1\. 审核浏览器的源代码 2\. 监控沙盒API的行为 3\. 分析预定义的沙盒策略文件(例如, Safari浏览器的配置)。

![](https://images.seebug.org/content/images/2022/02/b751e2e1-b197-4f43-b5d7-061e7429c20f.png-w331s)
表I. 沙盒对比(Chrome, Firefox, Edge, Safari; on Windows, Linux, MacOS)

`对沙盒原语进行分类`: 在表I中，我们根据作用将沙盒原语分为三类: 1\. 权限削减, 使用DAC/MAC等平台的权限系统对沙盒进程应用更多受限制的权限；
2\. 域分离, 为沙盒进程分配一个分离的资源空间； 3\. 减少攻击面, 限制对系统服务、内核或设备驱动程序的访问。

`浏览器的特定特征`:
浏览器供应商根据给定的约束(如，可用内存)使用不同的原语。例如，站点隔离通过在受感染的渲染器和特权网页[107]、[108]之间设置一个原始的、进程级的安全边界来防止RCE漏洞转化为UXSS或沙盒逃逸。

`特定于操作系统的行为`: 我们还比较了不同操作系统(即Windows、Linux和macOS)的沙盒功能。

  * `Windows`: 通过使用安全令牌(security token)来限制每个进程[117]。与基于功能的模型(capability-based model)类似，获得某个令牌级别的进程可以访问具有适当安全描述符级别的特权资源。例如，渲染器进程以低完整性令牌级别(low integrity token level)运行，代理进程以中等完整性令牌级别(medium integrity token level)运行，因此在默认情况下，从渲染器进程到代理进程的任何写入访问都将受到限制。

然而，细粒度的访问控制没有统一的协议。为了解决这个问题，Chrome和Firefox使用自己的IPC机制和资源相关功能的二进制级代码补丁以支持细粒度规则集[117]。微软在Windows
8中引入了AppContainer，通过添加"附加到进程令牌"的功能概念，对资源实施更细粒度的访问控制。Edge创建了一个基于AppContainer[89]的沙箱。从默认拒绝策略(deny-by-default)开始，Edge为所需的系统资源创建了一组功能。Chrome也在试验基于AppContainer的沙箱[28]。浏览器还利用各种功能来应对沙盒逃逸。例如，备用桌面和备用窗口站(alternate
window
station)可用于应对基于UI的攻击，例如Shatter[180]；引入"锁定默认DACL"[24]和"随机限制SID"[38]以执行更加严格的DACL，因此受感染的沙盒进程无法访问其他沙盒进程。

  * `Linux`: 与Windows不同，Linux沙箱主要基于seccomp、chroot和namespace。首先，seccomp是基于eBPF语言的标准系统调用过滤器。由于默认的seccomp配置过于严格，浏览器会定义自己的过滤规则。例如，Chrome将其自定义的seccomp规则应用于除代理进程(broker process)之外的所有进程，并且每个进程的详细规则各不相同。其次，为了限制文件访问，基于Linux的浏览器沙箱会利用chroot监禁。一旦使用chroot限制了进程，就无法访问文件系统的更高层次结构。例如，Firefox将chroot监禁应用于所有渲染器，并且仅允许它们根据从代理进程获得的文件描述符访问特定文件。此外，浏览器使用namespace[74]为各种资源（例如用户、网络和IPC）创建单独的空间。例如，创建和加入用户命名空间使沙盒进程能够位于单独的UID和GID中，从而有效地禁用对其他未沙盒进程的访问。

  * `macOS`: 虽然Windows和Linux支持各种类型的沙箱原语，但macOS支持专门格式化的沙箱配置文件(.sb)[75]来描述给定进程的沙箱策略。通常，该文件提供允许访问的绝对文件路径的允许列表，并默认阻止所有其他文件访问。该配置文件还定义了访问其他资源（如网络和共享内存）的能力，并支持基于系统调用的过滤，如Linux的seccomp，尽管它仅部署在Safari上。

`移动平台`:
由于基于进程的沙箱使用大量内存，因此移动平台会在沙箱策略中引入细微差异，或者根据可用资源禁用它们。例如，在Android上，只有当设备有足够的内存（>1.9GB）并且用户需要在网站上输入密码时，才会启用Chrome中的站点隔离[77]。在iOS上，Safari使用与macOS不同的沙盒规则，因为不同的系统服务和IOKit驱动程序是暴露在移动设备上的。由于这些差异，一些漏洞利用可能仅适用于移动平台[152]。

### D. 浏览器漏洞利用

浏览器利用的目标是窃取其用户的敏感数据或安装恶意软件以采取进一步行动。攻击者可以执行UXSS之类的攻击直接窃取数据，或者先执行代码，然后尝试沙箱逃逸。攻击者可能会试图通过攻击内核来获得系统特权沙箱逃逸，这超出了本文的范围。幸亏有各种应对方案（参见§III，§IV），攻击者需要将多个bug（例如，利用4个bug组合直到沙盒逃逸[134]）链接在一起以获得任意执行。即使在控制流被劫持之后，由于渲染器进程在沙箱内运行，攻击者需要在代理进程中找到另一组bug以进行沙箱逃逸。根据武器库中可用的漏洞，攻击者经常试图利用系统服务、驱动程序或内核中的错误而不是代理进程来突破沙箱[155]。

## III. 浏览器漏洞和应对措施

在本节中，我们首先对过去十年中公开报告的浏览器漏洞进行统计研究，以推断趋势，然后介绍主要的漏洞类型（例如JavaScript引擎错误）及其供应商发布的相应应对措施。

![](https://images.seebug.org/content/images/2022/02/4ea6c1cc-974b-4edc-a7a1-2f7d052a2a1c.png-w331s)
图2. 浏览器利用场景和漏洞分类。我们主要关注浏览器安全相关问题，省略了基本的软件攻击/防御技术，如ROP、NX和ASLR。"Exploit
example"箭头描绘了§V中描述的利用路径。

### A. 浏览器漏洞趋势

`数据采集`: 我们研究了四种主要浏览器的公开CVE和漏洞报告:  
1\. 来自“浏览器供应商[53]的定期更新的安全公告  
2\. 供应商[43][48]发布的公共问题跟踪  
3\. 开放源代码存储库有将bug修复提交到已发布漏洞的常规做法[30][45][60][52]  
4\. 国家漏洞数据库(NVD)[55]中的CVE报告  
5\. 现实世界中使用的安全漏洞利用，例如Pwn2Own[61]中使用的bug，以及Google Project
Zero报告[49]、[58]。表II总结了我们数据收集工作的成果。

![](https://images.seebug.org/content/images/2022/02/f3028ce4-217c-404d-a24b-6a42490d9b18.png-w331s)
表II. (1)NVD数据库中的CVE总数[55](2)收集到的bug数量.
对于开源浏览器，我们从供应商的bug跟踪器中收集了额外的的漏洞信息[48][43]. 对于这些浏览器, 我们忽略了机密漏洞和与bug跟踪器问题无关的漏洞。
对于闭源浏览器，我们使用NVD[55]作为CVE数据的唯一来源. (3)和(4)是用于收集被利用漏洞数据的来源.

`错误和代码库大小`:
图3显示了所有浏览器中，特别是从2010年之后，安全漏洞的急剧增加。我们认为这种漏洞的增加与不断增长的浏览器代码库有关，因为新功能不断添加。此外，2010年之后漏洞挖掘技术的进步发挥了相当大的作用，我们在§VI-C中强调了这一点。

![](https://images.seebug.org/content/images/2022/02/b9ddca85-00db-4393-b114-63aff8bad449.png-w331s)
图3. 左y轴: 安全漏洞数量; 右y轴: 两个开源浏览器(Firefox和Chromium)的LoC. LoC是基于每年的首个主要版本更新. 注: LoC
= Lines of Code

`动态攻击向量`:
浏览器的庞大规模和不断变化的特性使得攻击向量不断变化。对于开源浏览器Firefox和Chromium，我们将bug映射到它们各自的主机组件和bug类，如图4所示。对于这两种浏览器，我们使用开发人员分配的特质将bug映射到它们的主机浏览器组件，并使用关键字匹配漏洞描述以对其进行分类。

渲染器错误在Firefox和Chromium中都占主导地位，因为渲染器是浏览器的核心。自2016年以来，Chromium的URL欺骗漏洞的增加凸显了在以前未探索的区域中查找漏洞的容易程度。一般来说，内存错误，特别是UAF错误，仍然是两种浏览器最大的共同点。

另一个大体上的发现是这两个浏览器多年来在两个方面上的漏洞数量不同。例如，对于bug组件，Chromium最近有更多的DOM和HTML漏洞，但Firefox的DOM和HTML漏洞数量正在减少。对于bug类别，2019年Chromium中的大多数bug被归类为UAF、OOB和URL欺骗漏洞，但Firefox多年来对bug分布的描述相对统一。因此，这种差异不仅直观表现出不断变化的攻击向量，还表现了不同浏览器的安全漏洞分类策略的变化。

![](https://images.seebug.org/content/images/2022/02/938d1a1e-526b-492c-a040-34873e7f1e6b.png-w331s)
图4. 将bug映射到Firefox和Chromium中的主机浏览器组件和漏洞类. 该图突出了浏览器攻击面逐年变化的性质. 每个图中的数字都是按最小-最大比例缩放的.

浏览器针对bug的努力也可以在图中体现。Chromium的站点隔离[39]、[186]作为对UXSS漏洞的应对措施，使得2017年实施站点隔离后上述漏洞明显减少（图4b）。某些漏洞类型仍然是bug的主要来源，例如DOM和HTML组件，我们将在§III-C中详细说明。

`内存安全的语言`:
内存安全漏洞在浏览器中至关重要且占主导地位。例如，Chromium将超过70%的高严重性漏洞标记为内存安全问题，其中一半是UAF错误[50]。我们在图5中展示了浏览器中内存安全漏洞的比率。如图所示，尽管有应对措施[212][59]，但过去十年内存安全漏洞仍然占主导地位。最近，有人努力使用内存安全语言（例如
Rust）重写浏览器以减少内存安全漏洞。例如，Mozilla正在一个名为Oxidation[57]的项目中用Rust重写Firefox的部分内容。直到2020年，Oxidation项目已经用Rust(编写的等效模块)替换了12%的Firefox组件。五个被替换的子组件属于渲染器的媒体解析组件。我们也在图5中画出了渲染器的媒体解析组件中的内存安全漏洞数量。很明显，自2015年
Oxidation项目开始以来，Firefox中的内存安全漏洞数量呈现出小幅但稳定的下降，其中在渲染器的媒体组件中的内存安全漏洞明显减少。尽管浏览器供应商多次尝试解决内存安全问题，但都没有像Firefox的Oxidation那样产生显著效果。

![](https://images.seebug.org/content/images/2022/02/47216a99-c29f-45b7-b96a-c80c25c48c9a.png-w331s)
图5. Firefox和其他浏览器中内存安全漏洞与其他漏洞的数量。RM-Mem是Firefox渲染器中媒体解析组件中内存安全漏洞的数量，描述了从2015年开始用Rust部分重写后的下降趋势。

    
    
    Lession 1: 使用内存安全语言可以有效减少内存安全漏洞。
    如图5所示，在Firefox中使用Rust有效地减少了内存安全漏洞。尽管需要付出很多努力，但它是一种基本的方法，也是最有可能消除内存安全漏洞的方法。我们建议其他浏览器供应商遵循此最佳方法，并逐步将其浏览器转换为内存安全的语言。

`漏洞赏金计划`:
谷歌等主流浏览器厂商为那些帮助他们修复漏洞的安全错误报告提供奖励[116]。在大多数情况下，这些赏金考虑了多种因素，例如漏洞类型、可利用性以及报告者所做的额外有意义的工作。更高的赏金更能激励研究员和白帽去发掘漏洞。我们在图6中将每年的平均支付金额与Chromium中每年的漏洞数量相关联。我们特别展示了内存安全、UXSS和URL欺骗漏洞，因为它们与支付金额的关联模式很有意思。

![](https://images.seebug.org/content/images/2022/02/2e839cc3-dc9a-43cd-94a8-3f37db882365.png-w331s)
图6. 平均支付金额(上图)与Chromium中每年的漏洞数量(下图)之间的相关性. 红色区域是所有类别的平均赏金金额.
超过红色区域的漏洞类别表示比平均水平有更高的赏金.

支付金额会影响为各个类别发现的漏洞数量(图6)。平均赏金金额高于总体平均金额的错误类别（例如，2014-2016年的UXSS和2017-2020年的Mem错误）的数量似乎在这些年有所增加。然而，这种相关性也有例外：某个类别的漏洞数量的增加不会带来更高的赏金金额。该图进一步强调了研究人员在挖洞时除了寻求更高回报外的其他重要因素，例如
1) 寻求探索未知攻击向量(URL欺骗)的好处; 2) 瞄准具有更高影响的漏洞(UXSS在2016的增多);
3）避开具有有效应对措施的漏洞类别(2017年发布的站点隔离和2018年减少的UXSS错误)。

    
    
    Lession 2: 更高的赏金会激发更多的漏洞报告。
    浏览器厂商尝试增加漏洞赏金计划的覆盖面和预算，这收获了更多的漏洞报告。因此，增加漏洞赏金支出可以有效地吸引安全研究人员的兴趣并减少攻击面。

`漏洞严重性评级的分歧`: 通用漏洞评分系统(CVSS)[46]是作为漏洞严重性评估的免费和开源标准而开发的。 National Vulnerability
Database[55]使用CVSS标准为每个发布的CVE编号提供漏洞严重性基础评分。同样，Firefox和Chromium在其bug跟踪器[43][48]和安全建议[53]中提供了对漏洞严重性的评估，使用的是他们自己的漏洞评级系统。表III比较了NVD的CVSS-V3与Firefox和Chromium的漏洞严重性评估。本研究的目的是衡量使用NVD的CVSS-V3分数作为浏览器中漏洞严重程度的统一度量的有效性。

![](https://images.seebug.org/content/images/2022/02/a9eba2d6-3fac-40fe-9710-69b5eb6dae7a.png-w331s)
表III. NVD分配的CVSS-V3分数与供应商的漏洞严重程度分数之间的比较. 错误等级为: 低、中、高和严重.
表中省略了年久而无法获得CVSS-V3分数的bug. 最后一列是用于此比较的漏洞总数, 以及分配了不同漏洞等级的漏洞数.
该表在两个维度上强调了漏洞评级的差异: 1) CVSS分数与供应商分数中分类为低的漏洞数量(加粗); 2) 供应商之间评级为严重的漏洞(下划线).

在表中，我们注意到评级系统（供应商与NVD）之间存在差异。NVD对Firefox一半以上的漏洞进行了不同严重程度的评分，而它在Chromium的bug评分上也仅有58%与Chromium一致。虽然我们预计两个评级系统之间不会完全一致，但评分的巨大差距令人惊讶。这些差异也发生在供应商之间。查看这两种浏览器中严重漏洞的数量，我们可以看到，与Chromium相比，Firefox将其bug评为"严重"的百分比要高得多。我们的分析结果，与之前对使用CVSS分数作为bug分类和优先级的指标的担忧相一致[132][205][156]。

`浏览器漏洞`:
被实际攻击中的浏览器漏洞值得更多关注，因为从攻击者的角度来看，它们表明了已确定的攻击向量。为了研究此类漏洞，我们从仅获取高度可利用漏洞的可靠来源收集信息。对于在野使用的漏洞，我们参考Google定期更新的Project
Zero报告，该报告跟踪自2014年以来所有公开的0day漏洞利用案例[58]。我们还收集了Pwn2Own[40]中利用的漏洞，这是一场由Zero Day
Initiative[61]赞助的real-world黑客竞赛。我们根据漏洞类别和目标浏览器组件，在图7中突出显示过去十年中最常被利用的漏洞。

![](https://images.seebug.org/content/images/2022/02/4512d1e5-485a-4b19-b3c9-9b379a012316.png-w331s)
图7. 被利用的浏览器组件和错误类别的趋势. 数据包括来自所有浏览器的错误. 线上是累积的数量.
JavaScript引擎和UAF错误分别主导了被利用的bug组件和漏洞类型。

如图7所示，对于浏览器组件，DOM漏洞占主导地位，直到2017年被JS引擎漏洞取代。尽管如此，DOM漏洞在今天仍然存在，并且即使在添加了许多缓解措施后仍显示出缓慢而稳定的增长。对于漏洞类型，尽管采取了所有应对措施，实际利用中UAF漏洞等内存安全bug仍然比其他漏洞类型更多。一个有趣的发现是关于出现的漏洞类别和组件的对应趋势。对于图中的大多数线条，我们看到早些年的增长相当陡峭，但之后增长放缓（JavaScript引擎漏洞除外）。这种趋势直观呈现了:
攻击者为寻找和探索新的攻击技术而付出的努力，以及供应商为消除和应对新漏洞而采取的反应性对策。

`本节中包含的漏洞类型`: 基于图7所示的bug趋势，在本节中，我们主要讨论bug的趋势类型，即:  
1\. 解析器bug (§III-B)  
2\. DOM bug (§III-C)  
3\. JavaScript引擎漏洞 (§III-D)  
4\. SOP绕过和UXSS漏洞 (§III-E)

### B. 解析器漏洞

解析器经常遭受内存损坏问题；浏览器中的解析器也不例外。在Web浏览器中，大多数解析器漏洞都出现在媒体解析器或网络协议解析器中。如图4a所示，渲染器（媒体）占据很大份额。这些漏洞更容易在渲染器进程中被利用，因为它们可用于破坏
JS 对象并创建更强大的漏洞利用原语。

`当前状态`:
在强化堆分配器（§IV-B）之后，这种利用变得更加困难或不可行，主要是因为堆上JS对象的划分。不过，像ClusterFuzz[111]这样的大规模模糊器也发现了许多解析器漏洞。浏览器供应商正在研究沙盒化网络代码，并使用Rust[57]等内存安全语言重写浏览器代码。结果，这些漏洞变少且难以利用。尽管如此，在解析数据时仍然存在多个第三方库的依赖关系，因此需要对安全更新进行严格控制。

### C. DOM漏洞

DOM漏洞是攻击者的热门目标；根据图7，2014年大多数被利用的漏洞是DOM漏洞。由于其中大多数是UAF漏洞，因此已部署了应对措施以降低它们的可利用性，例如堆隔离与延迟释放(§IV-B)。

`当前状态`:
虽然fuzzer还在继续识别新的DOM漏洞[111]、[129]、[227]，如图7所示，但由于利用DOM漏洞的难度增加，最近已知的在野全链漏洞利用倾向于使用其他组件中的漏洞。

    
    
    Lession 3: UAF应对措施可有效减少DOM漏洞利用。
    由于DOM错误主要依赖于UAF问题，因此它们大多已通过UAF应对措施得到处理。依赖指针类型混淆的常规利用技术已经变得不可行，因为堆按对象类型隔离，并且没有公开的替代技术。 因此，利用DOM漏洞不再是破坏渲染器的首选方法。

### D. JS引擎错误

在最近的浏览器漏洞利用中，JS引擎漏洞是浏览器漏洞利用最流行的目标之一，尤其是优化相关的漏洞。至少34%的被利用漏洞（图7）使用JS引擎漏洞来破坏渲染器进程，这通常是全链浏览器漏洞利用的第一步。JS引擎漏洞可用于生成强大的漏洞利用原语，例如addrof（泄露任何JS对象的地址）和fakeobj（将任意地址作为对象访问）。

如§II-B中所述，JS引擎中的JIT编译器使用推测优化(speculative
optimization)。这些优化机制中的漏洞比传统的内存安全漏洞（例如释放后重用或缓冲区溢出）更为严重，因为它们难以处理，但为攻击者提供了强大的利用原语。从高层次上看，JS引擎的bug主要可以分为四类：
\- JIT分析漏洞：JIT编译器的分析过程或模型中的漏洞。此类漏洞具有最高的可利用性和影响。 \- JIT代码变异/生成漏洞：操作JIT
graphs或生成代码过程中的漏洞。 \- 非JIT副作用漏洞(Non-JIT side-effect
bugs)：JavaScript内置函数中的副作用漏洞，主要与快速路径(fast-path)相关。 \-非JIT传统内存损坏漏洞：不属于上述类别的其他内存损坏漏洞

我们检查了图7中的45个被利用的漏洞；有13个JIT分析漏洞、9个非JIT副作用漏洞和11个传统内存损坏漏洞，但没有JIT代码突变/生成漏洞。我们怀疑这是因为此漏洞很难利用。JIT编译器中的大多数漏洞都是逻辑漏洞。由于它是一个编译器基础设施，逻辑漏洞可以被放大为JIT编译代码中的内存安全漏洞。因此，很难对JIT错误做出一般性的缓解。在这里，我们介绍了三大类防御：`原语消除`、`覆盖保护`和`基于jit的代码重用缓解`。

  * `原语消除(Primitive elimination)`: 原语消除技术旨在防止攻击者 1.将漏洞转换为利用原语; 2.将利用原语升级为更强大的原语(例如, 为了构造可靠和稳定的读/写原语, 攻击者可以利用addrof和fakeobj原语来伪造一个带有完全受控的后备存储指针的ArrayBuffer对象, 这就是原语的升级)。

a. `对象形状认证(Object shape authentication)`:
这种类型的应对旨在防止攻击者使用fakeobj原语伪造有效对象。例如，在JavaScriptCore中，StructureID
Randomization使用7个随机熵位对StructureID进行编码，这使得攻击者很难猜测[121]、[204]。由于StructureID表示JS对象的类型和形状，猜测StructureID错误会导致形状无效，访问它最终会导致进程崩溃[221]。

b. `地址空间隔离(Address space isolation)`: 此类应对措施隔离不同对象，以防止对象被伪造或覆盖。
GigaCage[83]是一个4GB的虚拟内存区域，将不同的对象分成不同的堆（或HeapKinds）。关键思想是防止跨不同堆的内存访问，并使用堆基地址的相对偏移量来定位GigaCaged对象，而不是使用绝对地址。因此，即使指针已损坏，它也不能指向其原始堆之外的任何内容。PACCage[121]用于保护TypedArray的后备存储缓冲区指针，并在GigaCage之上使用指针验证码(PAC)进一步增强安全性。Chrome
V8 Heap Sandbox
[119]是实验性的，其目标类似于GigaCage，但它尝试使用单独的指针表来保护外部指针，之后攻击者无法为外部指针创建任意值。

  * `覆盖保护(Overwrite protection)`: 覆盖保护是防止攻击者引入任意可执行代码的标准保护机制，可以看作是浏览器漏洞利用上下文中的最后一道防线。它们主要包括四种机制: `W ⊕ X` [106]、`强化JIT映射` [139]、`快速权限切换`[128]、[139]和`进程外JIT`[164]。

a. `W ⊕ X`: W ⊕ X
是一个重要的安全原则，它强制内存要么可执行但不可写，要么可写但不可执行。这种应对比传统的shellcode注入攻击更出色，并为许多其他保护技术提供了基础[62]、[232]。令人惊讶的是，由于性能原因，JIT代码页通常不受这种基本缓解的影响，并被映射为rwx
[106]。

b. `仅执行内存(Execute only memory)`: ARMv8设备上的iOS
10获得了对仅执行内存(XOM)[139]的硬件支持，使JIT编译的代码能够将秘密数据作为即时值包含在内。Safari利用XOM向攻击者隐藏可写可执行映射的地址，方法是引入一个仅执行的jit_memcpy函数，该函数内部具有JIT映射的基地址。这使得任意读/写不足以覆盖JIT代码页，并迫使攻击者采取替代路径，例如劫持控制流来调用jit_memcpy。

c. `快速权限切换: APRR & MPK`: 引入对快速权限切换的硬件支持，以减少使用mprotect()切换页面权限的开销。自ARMv8设备上的iOS
11以来，APRR[139]被部署以通过将页面权限(r,w,x)映射到指示线程的实际页面权限的八个专用寄存器来启用每线程权限。类似地，英特尔MPK[128]每页添加一个单独的4位整数，以实施两个额外的保护：禁用访问和禁用写入。因此，JIT区域将始终为r-x，并且仅允许来自专用数据复制线程的写入操作，通过调用解锁函数将权限更改为
rw- 仅适用于目标线程。

d. `进程外JIT`: 在Windows上，Arbitrary Code Guard
(ACG)等缓解措施可确保进程只能将签名代码映射到其内存中。但是，浏览器出于性能目的大量使用JIT编译器，这会在内容进程中生成未签名的本机代码。引入了进程外JIT[164]以启用带有JIT编译器的ACG。因此，JIT功能被转移到一个单独的进程中，该进程在它自己的沙箱中运行，它负责编译JS代码并将其映射到进程中。因此，内容进程将永远不被允许映射或修改其自己的JIT代码页。

  * `基于JIT的代码重用缓解措施(JIT-based code-reuse mitigations)`: JIT Spray [158]是一种将大量攻击者控制的JIT代码（标记为可执行文件）注入内存中可预测的地址以绕过ASLR/DEP的技术，类似于Heap spray [95]。为了缓解JIT Spray，浏览器对JIT代码设置了大小限制，并切换到具有高熵ASLR的64位平台，这使得JIT spray不可行。不过，如果攻击者知道它们的地址，则可以利用JIT code gadgets。这种攻击称为基于JIT的代码重用攻击(JCRA)。在这里，我们简要总结了此类攻击的应对措施。

a. `受控字节消除(Controlled bytes elimination)`:
JCRA有一个基本假设，即通过控制立即操作数和特定操作码，攻击者可以控制在堆内存中生成的JITed代码。因此，应对措施是要消除攻击者控制字节的可预测性，例如混淆大常量[71]、[144]、置换立即操作数和局部变量的寄存器分配[144]、[222]以及在函数的调用帧中混杂指令[144]、[222]。

b. `内部随机化(Internal randomization)`:
攻击者还可以利用指令彼此的相对位置或与基地址的可预测偏移量。一些应对措施旨在使JIT代码布局多样化，包括：随机化不同指令对之间的相对偏移量[126]、[144]、[225]，以及在第一个代码单元之前随机插入空闲空间
[106]，[144]。

`当前状态`:
虽然有一些试验可以防止某些类型的漏洞(§IV-D)，但很难涵盖所有这些漏洞。因此，JS引擎中的应对措施侧重于消除攻击原语。最近，Edge团队添加了一个名为Super
Duper Secure
Mode(SDSM)[17]、[19]的新安全功能，它基本上禁用了JIT编译。用户可以选择在访问频率较低的网站上禁用JIT。虽然要牺牲一些性能，但它是减少攻击面的好方法。尽管已经引入了多种应对措施，JCRA仍然是有用的[87]、[106]，因为供应商没有投入很多资源来实施或维护应对措施。

    
    
    Lesson 4: 应对JS引擎漏洞很困难。
    JavaScript引擎漏洞，尤其是JIT编译器漏洞，非常强大，因为攻击者可以发出存在内存损坏问题的代码。因为处理逻辑漏洞通常很难，许多应对措施目的是防止利用原语升级。因此，供应商经常部署打破利用路径的缓解措施，并不断增强它们以防止未来的攻击。

### E. SOP-Bypass 和 UXSS 漏洞

同源策略(SOP)[94]由Web浏览器强制执行，以保持不同源之间的安全边界。SOP绕过漏洞可用于在不同程度上破坏SOP，从泄漏一比特到窃取整页数据。UXSS漏洞是最强大的SOP绕过漏洞类型，可用于促进跨域JavaScript代码执行。在UXSS攻击中，攻击者可以通过利用Web浏览器[13]、[14]或第三方扩展[31]、[35]中的漏洞将脚本注入任何受影响的上下文，达到与在目标网站利用XSS漏洞相同的效果。

`当前状态`:
站点隔离[39]、[186]是针对UXSS攻击的最重要的应对措施之一。站点隔离在进程级别强制执行SOP，这使得大多数现有的UXSS漏洞无法利用。2017年后逐步应用站点隔离后，报告的UXSS漏洞数量明显减少，如图6所示。但第三方扩展中的UXSS漏洞仍然存在；在流行的扩展[31]、[35]中发现了多个UXSS漏洞，这些漏洞使攻击者能够绕过站点隔离并窃取用户的凭据。

    
    
    Lession 5: UXSS漏洞主要通过站点隔离来缓解。
    站点隔离是针对UXSS漏洞的有效缓解措施。然而，只有Chrome和Firefox部署了站点隔离，因为它需要大量的工程工作（附录 D）。

### F. 总结

由于威胁研究和改进的补丁部署，1-day漏洞利用的影响减小，并且在野0-day漏洞利用一旦被捕获就会迅速修补。然而，供应商的进攻性研究仍然远远不足。尽管供应商正在努力，但他们在这场军备竞赛中始终落后。供应商的缓解措施大多是被动的，这意味着它们是在每一波攻击之后很久才行动。当攻击面最终关闭时，攻击者已经想出了更好的利用方式。这是一项艰巨的任务，但供应商应该更加主动，并在考虑安全隐患的情况下实施新功能，例如，在部署新功能之前研究潜在的新攻击。

## IV. 浏览器中的更多安全措施

在本节中，我们将介绍浏览器供应商实施的更通用的应对措施，这些措施未在前几节中介绍。我们对过去十年在四种主流浏览器中实施的应对措施以及它们的应用和停用日期进行了纵向研究，见表IV。在本节中，我们将详细讨论其中的部分。

![](https://images.seebug.org/content/images/2022/02/f5d3a644-fee5-4734-b19e-18bff8f7eb16.png-w331s)
表IV: 浏览器中的应对措施

### A. 沙箱

沙箱对浏览器安全至关重要，因为它限制了渲染器进程中漏洞的影响，其中包含各种容易出问题的组件。除了像UXSS这样的情况，攻击者需要利用内核、系统服务或浏览器进程的漏洞来逃离渲染器沙箱。因此，它显著提高了攻击的门槛，因为攻击者需要破解利用这两个组件（渲染器和沙箱）才能进行全链0-day攻击。

`Win32k锁定`: 由于大多数Windows内核漏洞都存在于Win32k系统调用中，因此Microsoft引入了系统调用禁用策略---2012年针对Windows的Win32k锁定[130]。Windows应用程序的开发人员可以完全阻止对Win32k系统调用表的访问，从而显著减少攻击面。Edge、Chrome和Firefox已经采用这种机制来保护浏览器。因此，从渲染器进程中实现沙箱逃逸变得更加复杂。

`基于Hypervisor的沙盒`: Windows
Defender应用程序防护(WDAG)[161]由微软引入，用于隔离企业场景中不受信任的网站或资源（例如文件）。WDAG使用Hyper-V在硬件层创建新的Windows实例，其中包括单独的内核副本和最低限度的Windows平台服务，以确保Edge浏览器正常运行。WDAG在Edge中实施，以防止可以绕过浏览器沙箱的高级攻击。使用WDAG，攻击者需要逃离沙盒和Hyper-V虚拟机。

### B. 强化分配器

出于性能和安全原因，浏览器对许多对象使用专门的堆分配器[96]，[150]。这些分配器使用特定的设计，通过限制攻击原语来帮助减少损害。

`堆隔离(Isolated heap)`: 堆隔离是一种有效的防御措施，可以防止UAF攻击升级为类型混淆攻击。通过基于: 1)类型;
2)安全风险级别(例如嵌入v-table指针);
3)JavaScript可达性（例如ArrayBuffer）来隔离对象，堆隔离有效地提高了UAF漏洞利用的门槛。隔离可防止攻击者使用具有不同布局的对象重新声明已释放的对象，这在浏览器UAF利用中是经典操作。

现代浏览器在JavaScript可达对象(JavaScript-reachable
objects)和其他对象之间实现了基本级别的堆分离[83]、[85]、[100]、[123]。但是，仍然有可能通过
UAF在同一堆中但其他类型的对象之间造成类型混淆。为了防止这种攻击，Safari[73]和Firefox[98]为特定类别中的每种类型引入了单独的堆，这提供了更细粒度的隔离。因此，没有公开的、通用的利用方法来利用所有浏览器中的UAF漏洞。

`延迟释放(Delayed free)`:
另一种应对措施，延迟释放，有效地增加了利用UAF漏洞的难度，但这种方法不能限制垂悬指针的回收。浏览器使用各种垃圾回收(GC)算法来释放没有引用的堆上对象。GC算法的一些变体额外扫描栈和堆[96]、[150]区域以查找可能被忽略的引用，这被称为保守扫描(conservative
scanning)[80]或延迟释放[123]。值得注意的是，Firefox放弃了这一策略，转而支持exact
rooting，并编写了一个静态分析工具来查找堆栈中引用的不安全使用[99]、[167]。Chrome也有一个类似的工具[15]，但它只在特定区域强制执行。然而，延迟释放引入了侧通道原语，可被用于击溃ASLR机制，因为它无法通过设计[41]、[81]、[104]、[123]来区分指向堆的指针和用户控制的整数。

`堆元数据保护(Heap metadata protection)`:
堆元数据保护是一种检查堆块的元数据部分以防止堆损坏和堆中的静默漏洞传播的方法。例如，堆分配器可能会在危险数据结构之前放置一个随机值[151]以检测堆漏洞。Chrome中的PartitionAlloc删除了内联元数据并放置了保护页面以防止线性堆溢出覆盖元数据[85]。在元数据保护方面也有一些操作系统级别的努力[148]、[151]。

`堆上的其他缓解措施`:Firefox 中的`Frame
poisoning`会释放地址指向不可访问内存页面的内存块[98]。类似地，在Edge中，这是通过在释放堆块时填充零来完成的[228]。Chrome中的GWP-ASan[115]在保护页面之前/之后随机放置一小部分分配的对象，并在释放块时释放整个页面以检测在野的堆错误。

### C. 控制流完整性

由于攻击者经常操纵指令指针的值来实现代码执行，因此强制控制流完整性以防止他们劫持控制流，从而使攻击更加困难。编译器基础设施、操作系统和硬件支持提供了这一类别中的大多数缓解措施，例如通过引入canary
value[165]来保护虚拟函数表，并允许通过检查目标地址来列出间接分支[159]、[177]。

正在进行的工作是防止任意内存写入修改攻击者可执行的代码区域（§III-D）。基于硬件支持，浏览器可以在不显著降低性能的情况下应用额外的应对措施，例如在ARM64
[149]上使用PAC添加指针完整性检查，还有使用Intel MPK[118]对JIT编译的代码添加额外的W ⊕ X保护和APRR[198]。

### D. 侧信道

浏览器也容易受到侧信道攻击。迄今为止的研究表明，浏览器中的敏感信息可以通过以下方式推断: 1\.
微架构状态[137]、[147]、[157]、[179]、[197]; 2\. GPU[142]、[178]; 3\. 浮点时序通道 [64]; 4\.
特定于浏览器的测信道[201]、[216]-[218]
研究人员引入了防御机制[84]、[138]、[194]、[202]来保护浏览器免受侧信道攻击，例如DeterFox[84]和FuzzyFox[138]。此外，浏览器供应商已经实施的防御[97]、[114]、[127]，可分为以下两类：

`降低定时器的分辨率`:
由于大多数攻击依赖于精确计时，为了阻碍对微小计时差异的检测，浏览器供应商降低了精确计时器的分辨率（例如，performance.now()）并引入了随机抖动来防止分辨率恢复[22],[66],[168]。在Spectre[137]和Meltdown[147]的发现之后，供应商进一步降低了计时器的精度[86]、[171]、[209]。由于SharedArrayBuffer可用于创建高分辨率计时器，因此在Spectre[137]发现后不久，SharedArrayBuffer在所有现代浏览器中都被禁用[88]。

`防止资源共享`: 另一种应对技术是防止受害者和攻击者之间的资源共享。站点隔离[39]、[186]
(§II-B)有效地处理了基于Javascript的瞬态执行。引入了Cross-Origin-Opener-Policy(COOP)和Cross-Origin-Embedder-Policy(COEP)[131]来建立跨域隔离环境。COOP允许网站在顶级document中包含响应头，确保跨域文档不与自身共享相同的浏览上下文组，从而防止直接DOM访问。COEP阻止页面加载任何未明确授予该页面权限的跨域资源。这些都是使用HTTP头强制执行的，并且它们在Chrome
83、Firefox 79和Edge 83[92]、[93]中提供，而截至2021年11月，Safari还不支持它们。

在引入站点隔离和COOP/COEP之后，Chrome和Firefox重新启用了SharedArrayBuffer[27]、[172]的使用。然而，一项研究表明，重新引入SharedArrayBuffer使隐蔽通道容量分别增加了2,000倍和800,000倍[187]。最近的两篇论文[63]、[135]表明，尽管Chrome中存在站点隔离，攻击者仍然可以获取跨域的敏感信息。

### E. 其他应对措施

`UAF缓解`:
为了从根本上解决垃圾回收或其他安全措施未涵盖的UAF问题，Chrome团队引入了一个名为`MiraclePtr`[184]、[185]的术语，它代表一组可以在C/C++中包装原始指针的算法，这样它们就不能通过UAF被利用。MiraclePtr预计将很快投入使用[79]。

`提高内存安全性`:
Chrome团队已经探索了他们的C＋＋代码库的改进，通过限制特定语言特性的使用（例如，C＋＋异常[112]）和围绕整数运算引入包装类[212]，可以消除或减少特定类型的漏洞。

`改进JIT编译器`: 已有许多努力用于保护JIT编译器内部的危险优化操作。例如，许多漏洞利用边界检查消除(bounds check
elimination)[192]来消除"看似多余"的边界检查。为了处理这种情况，Chrome团队引入了一个补丁，将此类检查标记为"中止(aborting)"，而不是简单地删除它们[133]。因此，攻击者最多只能触发一个SIGTRAP。此外，为了使标准JS函数的字节码生成更不容易出错，Chrome团队制作了一种特定领域的语言Torque[113]，它取代了现有的C++实现并减少了很多LoC。

    
    
    Lession 6：在应对方面的协作努力是有益的。
    当一个供应商部署应对措施时，其他供应商可能会效仿。在表IV中，我们看到众多应对措施已被多个浏览器采用。如果在一个浏览器中发现漏洞，供应商可以快速与其他供应商共享信息，他们可以一起使用集体知识构建更好的解决措施。在Spectre/Meltdown攻击[137]、[147]的情况下，浏览器供应商共同制定了减轻直接威胁的计划[86]、[171]、[209]，这是协作努力的一个很好的例子。

## V. 案例研究: 全链利用

由于现代浏览器具有不同的安全功能，因此浏览器利用通常需要链接多个攻击以最终执行恶意操作。结合所有这些步骤通常被称为全链利用(full-chain
exploitation)。作为全链浏览器利用的代表性案例研究，我们分析了2020年Pwn2Own竞赛中针对Safari[134]的成功攻击，即图2所示的漏洞利用示例。

这种攻击渗透到渲染器进程，从JIT编译器优化漏洞[37]开始：当满足有关代理对象的特殊条件时，Safari
JavaScript渲染器中的DFG编译器错误地模拟了"in"运算符的副作用。这个漏洞允许攻击者构建标准addrof/fakeobj原语，从而产生任意内存读/写，并最终产生任意代码执行。为了使用fakeobj构造一个有效的对象，攻击者利用一种众所周知的技术[221]绕过对象形状认证(object
shape authentication, §III-D中的结构ID随机化)。在伪造一个JavaScript对象后，他们使用已知技术[183]绕过地址空间隔离（第III-D节中的Gigacage）并在渲染器进程中获得任意读/写原语。

一旦渲染器进程受到破坏，沙盒逃逸就是下一步，并且更具挑战性。在这次攻击中，攻击者巧妙地将多个逻辑/内存漏洞拼接在一起以逃出沙盒。攻击者首先额外从CVMServer
XPC服务（内置OpenGL框架的一部分）获得任意代码执行，该服务虽然是沙盒，但具有创建符号链接的能力，而渲染器进程不具备这种能力。此外，Safari中有一个IPC方法，didFailProvisionalLoad()，如果提供了指向应用程序文件夹的符号链接，它可以启动任意应用程序。通过组合它们，攻击者可以通过Safari启动任意应用程序。至此，沙箱被成功攻破，因为他们可以在渲染器沙箱之外执行任意应用程序，类似于启动Safari的用户。

我们总结的Pwn2Own示例是具体但有影响力的。基于此，我们以更通用的方式描述全链浏览器利用。首先，要找到渲染器中的漏洞，可以利用模糊测试技术[122]、[125]、[182]或手动审核浏览器源代码。发现可利用的错误将是最具挑战性的步骤之一。发现此类漏洞后，下一步是在渲染器进程上下文中实现任意代码执行原语。然而，控制渲染器只是一个开始，因为渲染器受到沙盒机制的限制。为了突破沙盒，攻击者通常针对浏览器进程、操作系统内核或IPC协议中的缺陷。与攻击渲染器不同，沙盒逃逸通常需要针对多个系统组件链接高级逻辑漏洞。一旦沙盒逃逸，攻击者就可以执行与浏览器同等安全级别的任意程序，实现全链攻击。

## VI. 讨论

在本节中，我们将讨论与浏览器安全相关的几个方面。附录中有更多讨论。

### A. 补丁间隙问题

由于存在公共存储库和问题跟踪器，开源浏览器中的补丁可以先公开，早于新版本完成发布并提供给最终用户，从而使攻击者能够评估补丁的可利用性。例如，iOS
Safari由于1.5个月的补丁间隙而被利用[193]。为了缩小间隙，Chrome引入了每两周一次的安全更新，并将发布周期从六周缩短到四周[78]。Firefox在发布[173]、[193]之前阻止将安全修复推送到存储库，并建议不要在补丁提交中包含漏洞信息[173]。

### B. 浏览器引擎的同质性

许多"次级浏览器"使用与领先浏览器相同的浏览器引擎（例如，Chrome
V8）。因此，一个浏览器引擎中的漏洞可能会影响公用引擎的其他浏览器。在最受欢迎的15款浏览器
[206]中，有11款基于Chrome的引擎（包括Microsoft
Edge[136]），如表V所示。当新版本的Chrome发布并修复bug时，它不会立即应用于次级浏览器，次级浏览器融合它们之前存在一个时间间隔。

![](https://images.seebug.org/content/images/2022/02/0acf883b-01f2-453f-9704-ea1baebe7fc8.png-w331s)
表V: 浏览器引擎的同质性。一些浏览器提供多个引擎以确保网页的兼容性，或顺应特定平台要求（例如iOS上的WebKit）[69]。

根据次级浏览器的发布历史，在应用发布的安全补丁之前存在时间间隔，这为攻击者提供了一个攻击窗口。例如，一个WebKit漏洞在被报告给WebKit错误跟踪器[29]数月后还可以在PlayStation固件上被利用。这也是Android中的一个问题，其中应用程序附带捆绑的渲染引擎，例如，在向Chromium[7]报告大约一个月后，三星浏览器(Samsung
Internet)[6]上报告了一个UXSS漏洞。Apple通过强制所有应用程序使用操作系统提供的WebKit库并拒绝其App
Store[69]中的不合规应用程序来解决iOS中的这个问题。

此外，渲染器和JavaScript引擎等Web浏览器组件的使用进一步扩展到使用Electron和Android
WebView等框架的应用程序。此外，Node.js[56]和Deno[47]使用Google的V8引擎在浏览器上下文之外启用JavaScript（例如，用于实现Web服务器）。因此，浏览器引擎的漏洞和漏洞利用不仅会影响浏览器本身，对更好的防御机制以避免灾难性后果的需求也扩大了。

    
    
    Lession 7: 浏览器引擎的同质性造成了严重的问题；需要更好的修补方法。由于浏览器引擎的同质性，一个浏览器引擎中的漏洞会影响其他许多浏览器和应用程序。我们建议领先的浏览器（如Chrome）将其JavaScript引擎作为共享库提供给其他应用程序使用，以便通过无线更新更容易地部署补丁，而不是手动集成补丁。

### C. 漏洞发现工具

人们已经做出许多努力来开发用于发现浏览器引擎错误的最新的工具，这些工具主要可以分为两类：`模糊测试`和`静态分析`。

`模糊测试(Fuzzing)`:
Fuzzing是发现bug的最有效策略之一，自2012年以来一直有被应用于发现浏览器bug。我们在表VI（附录）中总结了过去十年中有关浏览器fuzzer的论文，其中包括他们在Chrome中发现的bug统计信息、Firefox、Safari和Edge（基于ChakraCore和V8），以及它们的关键技术。这些模糊器在两种经典模式之间进行选择：突变模糊测试（mutational
fuzzing，例如，Montage[143]）和生成模糊测试（generational
fuzzing，例如，CodeAlchemist[122]）。一些模糊器，如Lang-Fuzz[125]和DIE[182]，利用了两种模式的混合以及覆盖反馈(coverage
feedback)。构建像DIE[182]和LangFuzz[125]这样的句法和语义感知输入对于产生更多的崩溃很有用。一些关于模糊浏览器的产业性的努力在发现复杂的浏览器漏洞方面非常有效。例如，ClusterFuzz[111]在超过25,000个核心[109]上运行，并在Chrome中发现了超过29,000个漏洞[110]。

`静态分析(Static analysis)`:
最近，在以fuzzing为主导的浏览器漏洞挖掘领域出现了另一项工作。SYS[82]是首个用于在浏览器代码中查找错误的"静态/符号"工具，静态分析可以通过将浏览器的巨大代码库分解成小块来扩展它们。具体来说，SYS使用静态检查器来查找潜在的漏洞位置，然后使用它们的可扩展符号执行(extensible
symbolic execution)来分析这些漏洞位置。因此，SYS在通过静态分析发现浏览器bug领域为未来的工作指明了一个很好的方向。

    
    
    Lession 8：自动化漏洞挖掘很棒，但仍需要改进。
    业界最先进的模糊器在捕获浏览器中的漏洞方面做得很好。然而，尽管它们的性能很好，但这些工具仍然无法替代手动审计，而手动审计仍然是发现复杂逻辑漏洞的主要方法。因此，学术界和行业内都需要更先进的漏洞挖掘技术。

### D. 主动应对措施

大多数现有的缓解措施都是被动的，这意味着它们是在发现漏洞后实施的，这还不够好。如果可以在攻击发生之前采取措施（主动方法），那将是理想的，这可以击败未知威胁。例如，站点隔离[186]最初旨在使用进程外iframe缓解UXSS攻击，但它也有助于击败Spectre/Meltdown攻击，这是研究人员在站点隔离项目开始很久后发现的。这是应对未知威胁的主动方法的一个很好的例子。

在应对漏洞利用的游戏中，防御者永远无法击败攻击者，因为防御者的行为对攻击者是透明的。供应商可以通过秘密部署新的应对措施来改变这种情况，例如，在安全浏览基础设施的沙箱中。这还可以通过收集极有可能是恶意的样本来帮助检测在野漏洞并修补错误。此外，供应商可以尝试更积极的应对措施，这些措施可能会影响此类环境中的用户体验。例如，如果在发布公告之前就将StructureID随机化(§III-D)部署在安全浏览沙箱中，则大多数涉及fakeobj原语的JIT漏洞都会被检测到。

## VII. 结论

在本文中，我们呈现了第一个浏览器安全
SoK。我们首先提供了一个统一的模型来研究四大浏览器的安全设计，并提出了一个为期10年的浏览器漏洞纵向研究来研究趋势。然后我们介绍突出的漏洞类型，并提出最先进的应对措施。我们还详细研究了Pwn2Own
2020的真实世界全链漏洞利用。本文阐明了浏览器安全领域，并提出了一些关键要点，可以启发研究人员和浏览器供应商了解未来提高浏览器安全性的方向。

* * *

## 附录

### A. 漏洞挖掘工具

我们在表VI中总结了过去十年中有关浏览器模糊器的论文。

![](https://images.seebug.org/content/images/2022/02/abcfe365-6099-4e50-bcf5-426b4235fca4.png-w331s)
表VI: 浏览器引擎模糊器的比较

Fuzzer | Year | C+E† | FF | S | E‡ | G | M | SM | SN | Cov | OS | 关键技术  
---|---|---|---|---|---|---|---|---|---|---|---|---  
SoFi [124] | 2021 | 1 | 5 | 1 | 18 | × | √ | √ | √ | √ | × |
使用细粒度的程序分析和修复策略来生成语义上有效的输入  
Token-Level Fuzzing [191] | 2021 | 16 | 3 | 4 | 6 | × | √ | × | × | √ | × |
通过更改或替换整个单词在token-level应用突变  
Favocado [91] | 2021 | 8 | NA | 5 | NA | × | √ | √ | √ | × | √ |
根据语义信息生成测试用例，并跟踪状态突变  
DIE [182] | 2020 | 4 | NA | 16 | 28 | √ | √ | √ | √ | √ | √ |
保留有益的特性和条件，被称为aspects across mutation  
FREEDOM [227] | 2020 | 4 | 5 | 13 | NA | √ | √ | √ | √ | √ | √ | 使用定制的IR(FD-IR)来描述HTML文档和定义突变  
Montage [143] | 2020 | 1 | 0 | 2 | 34 | × | √ | √ | √ | × | √ | 将JS
AST转换为序列以训练神经网络语言模型(Neural Network Language Models)  
Nautilus [70] | 2019 | NA | NA | NA | 2 | × | √ | × | √ | √ | √ |
将基于语法的输入生成与覆盖反馈(coverage feedback)相结合  
Deity [145] | 2019 | NA | NA | 1 | 1 | √ | √ | × | √ | √ | √ |
使用以前已知的bug和PoC生成基于语法的JS代码  
Superion [220] | 2019 | NA | NA | 16 | 3 | × | √ | × | √ | √ | √ |
使用基于树和字典的变异对语法感知(grammar-aware)测试输入进行修剪  
CodeAlchemist [122] | 2019 | 2 | NA | 10 | 7 | √ | × | √ | √ | × | √ |
使用约束标记代码块，定义何时与其他代码块组合  
LangFuzz [125] | 2012 | 11 | 20 | NA | NA | √ | √ | √ | √ | × | × |
生成语法感知测试输入，并利用以前已知的错误程序  
      
    
    G: Generational 生成(模糊测试样本)
    M: Mutational 变异(模糊测试样本)
    SM: Semantic Aware (语义感知)
    SN: Syntactic Aware (语法/词法感知)
    Cov: Coverage Feedback 代码覆盖率反馈
    OS: Open Source 开源
    C: Chrome
    FF: Firefox
    E†: : 基于V8引擎的Edge
    E‡ : 基于ChakraCore引擎的Edge

### B. 浏览器隐私保护

网络浏览中最令人担忧的隐私泄露内容之一是用户的IP地址。由于Web服务器可以轻松收集和存储IP，因此可以根据网络环境（例如NAT）以精细的粒度立即公开用户的地理位置。Tor浏览器[213]使用洋葱协议解决了这个问题，该协议使用Tor网络中的多个随机节点重新路由用户的连接，并且每个节点不能同时知道用户的身份（IP）和目的地。然而，通过观察加密的网络数据包序列[181]、[199]，仍然可以通过网站指纹技术破坏隐私。另一种浏览器Brave[203]通过删除网站中包含的所有广告和广告跟踪器来阻止网站跟踪用户，但用户的浏览历史仍然可能被泄露[214]、[223]。

### C. 插件和扩展

插件和扩展是通过提供多种功能来定制浏览器功能的小型软件程序。Java和Flash等插件在网页上下文中运行，而扩展程序将附加功能附加到浏览器。尽管它们有好处，但插件是浏览器不稳定的主要来源[8]、[9]。插件还使渲染器进程的沙箱化变得不切实际，因为插件是由第三方编写的，浏览器供应商无法控制他们对操作系统的访问。此外，扩展在浏览器中具有特殊权限，使它们成为攻击者眼中有吸引力的目标[10]-[12]。

`NPAPI插件`。
NPAPI允许浏览器供应商开发具有通用接口的插件。当浏览器访问具有未知内容类型的页面时，它会搜索并加载可用插件来委派内容处理。因此，攻击者可以通过为网页分配特定的内容类型来触发漏洞，从而欺骗浏览器加载具有漏洞的特定插件。利用NPAPI插件的攻击在不同的浏览器和平台上很普遍，特别是在Java、Flash和PDF[163]上。为了应对这个问题，浏览器将插件进程与浏览器的主进程分开，即进程外插件缓解(out-of-process plugin
mitigation)[170]、[188]。但是，插件仍然可以用于浏览器利用，并被指责为性能下降、浏览器崩溃的原因。最后，所有浏览器都停止了对NPAPI插件的支持[169]。

### D. 部署应对措施的难度

浏览器供应商很难部署应对措施，原因如下：

a. `兼容性`:
第三方代码（例如浏览器插件）依赖于浏览器代码才能正常运行。在引入浏览器缓解措施时，可能会破坏浏览器供应商无法控制的第三方代码。例如，当尝试在Windows中为Chrome的Pepper
Plugin API(PPAPI)引入Win32k锁定时，在Windows
8.1及更低版本上应用补丁时存在稳定性问题，Chrome团队无法追踪[130]，影响Flash、PDFium和Widevine等插件。因此，PPAPI
Win32k锁定仅针对Windows 10而非Windows 8/8.1启用以避免稳定性问题。

b. `性能`:
添加安全缓解措施的成本很高。为了减轻安全威胁，浏览器供应商有时会选择以性能换取安全，反之亦然。例如，2018年初在所有现代浏览器中禁用SharedArrayBuffer(SAB)作为Spectre攻击的对策，正如§IV-D中所讨论的那样，极大地危害了性能，因为SAB最初旨在实现worker之间的轻量级同步[76] .

c. `安全`:
更多的代码通常意味着更多的安全漏洞。通常，引入缓解措施或补丁会增加攻击面。在为浏览器部署新补丁后，浏览器供应商通常会寻找漏洞报告以尽快解决新的安全问题。例如，Firefox单独为主动应对措施中的安全漏洞推出了一类全新的漏洞奖励[215]。

`还原的缓解措施`:
一些缓解措施被临时部署以处理即时威胁，同时开发更好的缓解措施。例如，在上面提到的SAB案例中，在引入更强大的应对措施（即站点隔离和COOP/COEP）后不久，Chrome和Firefox重新启用了SAB[27]、[172]。
尽管尽了所有努力来确保缓解措施是安全的、高性能的和兼容的，但有时缓解措施由于它们带来的一些严重后果而不得不撤销。例如，在表IV中，Chrome内置的XSS过滤器XSS
Auditor[72]遭受了许多安全副作用，导致其在2019年退役[207]。

* * *

## 参考链接

[1] CVE-2003-1048. Double free vulnerability in mshtml.dll.  
[2] CVE-2006-5579. Access of previously freed memory in Internet Explorer 6.  
[3] CVE-2011-3046. Universal XSS in Chromium with largest reward amount
($60k).  
[4] CVE-2013-6632. Memory corruption leads to sandbox escape in Chrome
browser.  
[5] CVE-2016-4622. Remote code execution on WebKit.  
[6] CVE-2017-17859. SOP Bypass on Samsung Internet referred as CVE-2017-5124
in Chromium Engine.  
[7] CVE-2017-5124. SOP Bypass on Google Chrome.  
[8] CVE-2019-5647. Insufficient Session Expiration in Chrome Plugin.  
[9] CVE-2019-6481. Second-Factor Auth Bypass in Chrome Plugin.  
[10] CVE-2020-15655. Bypass same-origin policy in Firefox extension.  
[11] CVE-2020-6554. Use After Free in Chrome extension.  
[12] CVE-2020-6809. Arbitrary read on local files in Firefox extension.  
[13] CVE-2021-1879. UXSS in Webkit iOS 14.4.2 and iPadOS 14.4.2.  
[14] CVE-2021-34506. Microsoft Edge (Chromium-based) Security Feature Bypass
Vulnerability.  
[15] gcmole. https://github.com/v8/v8/tree/master/tools/gcmole.  
[16] Languages - Chromium (Google Chrome).
https://www.openhub.net/p/chrome/analyses/latest/languages_summary.  
[17] Microsoft unveils ‘Super Duper Secure Mode’ in latest version of Edge.
https://portswigger.net/daily-swig/microsoft-unveils-super-duper-secure-mode-in-latest-version-of-edge.  
[18] Restricted Tokens - Win32 apps. https://docs.microsoft.com/en-us/windows/win32/secauthz/restricted- tokens.  
[19] Super Duper Secure Mode.
https://microsoftedge.github.io/edgevr/posts/Super- Duper- Secure- Mode/.  
[20] SELinux leaked file descriptor, 2010. https://bugzilla.redhat.com/show_
bug.cgi?id=581256.  
[21] Add an option to mark JIT pages as non-writable.
https://bugzilla.mozilla.org/show_bug.cgi?id=977805, 2014.  
[22] Reduce resolution of performance.now to prevent timing attacks.
https://bugs.chromium.org/p/chromium/issues/detail?id=506723, 2015.  
[23] Add New Process Mitigation Policies for Win10+.
https://bugs.chromium.org/p/chromium/issues/detail?id=504006, 2016.  
[24] Security: Block GPU Process Opening Renderer Processes.
https://bugs.chromium.org/p/chromium/issues/detail?id=596862, 2016.  
[25] Enable new FORCE_MS_SIGNED mitigation, 2017.
https://bugs.chromium.org/p/chromium/issues/detail?id=750886.  
[26] Off-by-one causes JIT optimization error, 2017.
https://bugs.chromium.org/p/chromium/issues/detail?id=762874.  
[27] Re-enable sharedarraybuffer + atomics.
https://bugs.chromium.org/p/chromium/issues/detail?id=821270, 2018.  
[28] Sandbox the network service on Windows, 2018.
https://bugs.chromium.org/p/chromium/issues/detail?id=841001.  
[29] setAttributeNodeNS UAF Write-up. https://github.com/Cryptogenic/Exploit-Writeups/blob/master/WebKit/setAttributeNodeNS%20UAF%20Write-up.md, 2018.  
[30] ChakraCore, The core part of the Chakra JavaScript engine that powers
Microsoft Edge, 2019. https://github.com/microsoft/ChakraCore.  
[31] Comply with new security requirements for Chrome, 2019.
https://github.com/uBlockOrigin/uBlock-issues/issues/710.  
[32] Enable ACG for jitless v8 in pdfium, 2019.
https://bugs.chromium.org/p/chromium/issues/detail?id=961831.  
[33] JavaScriptCore, The built-in JavaScript engine for WebKit, 2019.
https://trac.webkit.org/wiki/JavaScriptCore.  
[34] SpiderMonkey, JavaScript engine for Mozilla products, including Firefox,
2019. https://developer.mozilla.org/en-US/docs/Mozilla/Projects/SpiderMonkey.  
[35] UXSS bug found in Lastpass, 2019.
https://blog.lastpass.com/2019/09/lastpass-bug-reported-resolved/.  
[36] V8, Open source JavaScript and WebAssembly engine for Chrome and Node.js,
2019. https://v8.dev/.  
[37] 2020. Incorrect JIT modeling in WebKit that leads to type confusion.  
[38] Add support for random restricted SID. https://chromium-review.googlesource.com/c/chromium/src/+/2085751, 2020.  
[39] The Chromium Projects. Site Isolation, 2020.
https://www.chromium.org/Home/chromium-security/site-isolation.  
[40] Zero Day Initiative - Pwn2Own Returns to Vancouver for 2020.
https://www.zerodayinitiative.com/blog/2020/1/8/pwn2own-returns-to-vancouver-for-2020, 2020.  
[41] Bypassing ASLR using Oilpan’s conservative garbage collector.
https://bugs.chromium.org/p/chromium/issues/detail?id=1144662, 2021.  
[42] Can I use... Support tables for HTML5, CSS3, etc. https://caniuse.com/,
2021.  
[43] Chromium Bug Tracker, 2021.
https://bugs.chromium.org/p/chromium/issues/list.  
[44] Chromium Security - The Chromium Projects, 2021.
https://www.chromium.org/Home/chromium- security.  
[45] Chromium source code, 2021.
https://chromium.googlesource.com/chromium/src.  
[46] Common Vulnerability Scoring System SIG, 2021.
https://www.first.org/cvss/.  
[47] Deno - A modern runtime for JavaScript and TypeScript, 2021.
https://deno.land/.  
[48] Firefox Bugzilla, 2021. https://bugzilla.mozilla.org/home.  
[49] Google’s Project Zero bug tracker, 2021.
https://bugs.chromium.org/p/project- zero/issues/list?q=&can=1.  
[50] Memory Safety in Chromium, 2021. https://www.chromium.org/Home/chromium-security/memory- safety.  
[51] Modern security protection for vulnerable legacy apps, 2021.
https://docs.microsoft.com/en-us/deployedge/microsoft-edge-security-iemode-safer-than-ie.  
[52] Mozilla Firefox source code, 2021. https://hg.mozilla.org/.  
[53] Mozilla Foundation Security Advisories, 2021. https://www.mozilla.org/en-US/security/advisories/.  
[54] Mozilla Security Blog, 2021. https://blog.mozilla.org/security/.  
[55] National Vulnerability Database, 2021. https://nvd.nist.gov/.  
[56] Node.js, 2021. https://nodejs.org/en/.  
[57] Oxidation, 2021. https://wiki.mozilla.org/Oxidation.  
[58] Project Zero: 0day "In the Wild", 2021.
https://googleprojectzero.blogspot.com/p/0day.html.  
[59] Smart Pointer Guidelines in Firefox, 2021. https://firefox-source-docs.mozilla.org/dom/workersAndStorage/CodeStyle.html#plain- pointers.  
[60] V8 source code, 2021. https://chromium.googlesource.com/v8/v8.  
[61] Zero Day Initiative - Published advisories, 2021.
https://www.zerodayinitiative.com/advisories/published/.  
[62] Martín Abadi, Mihai Budiu, Ulfar Erlingsson, and Jay Ligatti. Control-flow integrity principles, implementations, and applications. TISSEC09.  
[63] Ayush Agarwal, Sioli O’Connell, Jason Kim, Shaked Yehezkel, Daniel
Genkin, Eyal Ronen, and Yuval Yarom. Spook.js: Attacking chrome strict site
isolation via speculative execution. In SP22.  
[64] Marc Andrysco, David Kohlbrenner, Keaton Mowery, Ranjit Jhala, Sorin
Lerner, and Hovav Shacham. On subnormal floating point and abnormal timing. In
SP15.  
[65] Apple. Changeset 160983 in webkit.
https://trac.webkit.org/changeset/160983/webkit, 2013.  
[66] Apple. Changeset 186208 in webkit for
trunk/source/webcore/page/performance.cpp.
http://trac.webkit.org/changeset/186208/webkit/trunk/
Source/WebCore/page/Performance.cpp, 2015.  
[67] Apple. Changeset 253098 in webkit.
https://trac.webkit.org/changeset/253098/webkit, 2015.  
[68] Apple. Allow Execution of JIT-compiled Code Entitlement, 2018.
https://developer.apple.com/documentation/bundleresources/entitlements/com_apple_security_cs_allow-jit.  
[69] Apple. App Store Review Guidelines. https://developer.apple.com/app-store/review/guidelines/, 2020.  
[70] Cornelius Aschermann, Tommaso Frassetto, Thorsten Holz, Patrick Jauernig,
Ahmad-Reza Sadeghi, and Daniel Teuchert. Nautilus: Fishing for deep bugs with
grammars. In NDSS19.  
[71] Michalis Athanasakis, Elias Athanasopoulos, Michalis Polychronakis,
Georgios Portokalidis, and Sotiris Ioannidis. The devil is in the constants:
Bypassing defenses in browser jit engines. In NDSS15.  
[72] Daniel Bates, Adam Barth, and Collin Jackson. Regular expressions
considered harmful in client-side xss filters. In WWW10.  
[73] Niklas Baumstark. Compressing Type Information in Modern C Programs using
Type Isolation, 2019.  
[74] Eric W Biederman and Linux Networx. Multiple instances of the global
linux namespaces. In Proceedings of the Linux Symposium.  
[75] Dionysus Blazakis. The apple sandbox. In Black Hat DC 11.  
[76] blink-dev Google Groups. Intent to implement: Shared array buffers.
https://groups.google.com/a/chromium.org/g/blink-dev/c/d-0ibJwCS24, 2015.  
[77] Google Chromium Blog. Recent Site Isolation improvements.
https://blog.chromium.org/2019/10/recent-site-isolation-improvements.html,
2019.  
[78] Google Chromium Blog. Speeding up Chrome’s release cycle.
https://blog.chromium.org/2021/03/speeding-up-release-cycle.html, 2021.  
[79] Google Security Blog. An update on memory safety in chrome.
https://security.googleblog.com/2021/09/an-update-on-memory-safety-in-chrome.html, 2021.  
[80] Hans-Juergen Boehm and Mark Weiser. Garbage collection in an
uncooperative environment. Software: Practice and Experience.  
[81] E. Bosman, K. Razavi, H. Bos, and C. Giuffrida. Dedup est machina: Memory
deduplication as an advanced exploitation vector. In SP16.  
[82] FraserBrown,DeianStefan,andDawsonEngler.Sys:Astatic/symbolic tool for
finding good bugs in good (browser) code. In USENIX Security 20.  
[83] Sam Brown. Some brief notes on webkit heap hardening.
https://labs.f-secure.com/archive/some-brief-notes-on-webkit-heap-hardening/,
2018.  
[84] Yinzhi Cao, Zhanhao Chen, Song Li, and Shujiang Wu. Deterministic
browser. In CCS17.  
[85] R. Chris. Partitionalloc - a shallow dive and some rand, 2016.
https://struct.github.io/.  
[86] Chromium. Clamp performance.now() to 100us. https://chromium-review.googlesource.com/c/chromium/src/+/853505, 2018.  
[87] Chromium. Security: Constant blinding bypass via Wasm, 2020.  
[88] ComputerWorld. Browser makers build bulwarks to stump spectre attacks.
https://www.computerworld.com/article/3246210/browser-makers-build-bulwarks-to-stump-spectre-attacks.html, 2018.  
[89] Crispin Cowan. Strengthening the Microsoft Edge Sandbox, 2017.  
[90] Cure53. Cure53 Browser Security White Paper.
https://github.com/cure53/browser-sec-whitepaper, 2017.  
[91] Sung Ta Dinh, Haehyun Cho, Kyle Martin, Adam Oest, Kyle Zeng, Alexandros
Kapravelos, Gail-Joon Ahn, Tiffany Bao, Ruoyu Wang, Adam Doupé, et al.
Favocado: Fuzzing the binding code of javascript engines using semantically
correct test cases.  
[92] MDN Web Docs. Cross-origin-embedder-policy.
https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cross-Origin-Embedder-Policy, 2021.  
[93] MDN Web Docs. Cross-origin-opener-policy.
https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cross-Origin-Opener-Policy, 2021.  
[94] MDN Web Docs. Same-origin policy. https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy, 2021.  
[95] eEye Digital Security. Microsoft Internet Information Services Remote
Buffer Overflow, 2001.  
[96] Filip Pizlo. Introducing Riptide: WebKit’s Retreating Wavefront
Concurrent Garbage Collector. 2017.  
[97] Filip Pizlo. What Spectre and Meltdown Mean For WebKit. 2018.  
[98] Firefox. Always poison deallocated objects in the frame arena, 2009.
https://bugzilla.mozilla.org/show_bug.cgi?id=497495.  
[99] Firefox. Exact stack rooting, 2014. https://developer.mozilla.org/en-US/docs/Mozilla/Projects/SpiderMonkey/Internals/GC/Exact_Stack_Rooting.  
[100] Firefox. [meta] store content-controlled buffers in a separate heap,
2014. https://bugzilla.mozilla.org/show_bug.cgi?id=1052575.  
[101] Firefox. Implement win/osx sandboxing for new RDD process, 2018.
https://bugzilla.mozilla.org/show_bug.cgi?id=1498624.  
[102] Firefox. Enable Code Integrity Guard on RDD Process, 2019.
https://bugzilla.mozilla.org/show_bug.cgi?id=1563774.  
[103] Fortinet. Microsoft MSHTML Remote Code Execution Vulnerability Exploited
in the Wild (CVE-2021-40444). https://www.fortinet.com/blog/threat-research/microsoft-mshtml-remote-code-execution-vulnerability-exploited-in-wild-cve-2021-40444, 2021.  
[104] Ivan Fratric. Dude, where’s my heap? 2015.  
[105] Pietro Frigo, Cristiano Giuffrida, Herbert Bos, and Kaveh Razavi. Grand
pwning unit: Accelerating microarchitectural attacks with the gpu. In SP18.  
[106] Robert Gawlik and Thorsten Holz. Sok: Make jit-spray great again. In
WOOT18. [107] Guang Gong. Security: Pwn2Own mobile case, out-of-bound access
in json stringifier. In Chromium Bug Tracker, 2015.  
[108] Guang Gong. Pwn a nexus device with a single vulnerability. In
CanSecWest, 2016.  
[109] Google. Open sourcing clusterfuzz.
https://security.googleblog.com/2019/02/open-sourcing-clusterfuzz.html.  
[110] Google. Scalable fuzzing infrastructure.
https://github.com/google/clusterfuzz.  
[111] Google. Clusterfuzz. https://google.github.io/clusterfuzz/, 2015.  
[112] Google. Google C Style Guide, 2017.  
[113] Google. Torque: Applying leverage to the CodeStubAssembler, 2018.  
[114] Google. Chrome - Mitigating Side-Channel Attacks, 2019.
https://www.chromium.org/Home/chromium-security/ssca.  
[115] Google. GWP-ASan: Sampling heap memory error detection in-the-wild.
https://sites.google.com/a/chromium.org/dev/Home/chromium-security/articles/gwp-asan, 2019.  
[116] Google. Chrome Vulnerability Reward Program Rules. https://www.
google.com/about/appsecurity/chrome-rewards/, 2021.  
[117] Google. Chromium design docs - sandboxing.
https://chromium.googlesource.com/chromium/src/+/refs/heads/main/docs/design/sandbox.md,
2021.  
[118] Google. wasm: Write-protection of generated code with PKEYs/PKU, 2021.  
[119] Google Chrome Team. V8 Heap Sandbox - High-Level Design Doc.
https://docs.google.com/document/d/1FM4fQmIhEqPG8uGp5o9A-mnPB5BOeScZYpkHjo0KKA8/,
2021.  
[120] Samuel Groβ. Pwn2Own 2018: Safari + macOS, 2018.
https://github.com/saelo/pwn2own2018.  
[121] SamuelGroβandProjectZero.Jitsploitationii:Gettingread/write.
https://googleprojectzero.blogspot.com/2020/09/jitsploitation-two.html, 2020.  
[122] HyungSeok Han, DongHyeon Oh, and Sang Kil Cha. Codealchemist: Semantics-aware code generation to find vulnerabilities in javascript engines. In
NDSS19.  
[123] Abdul-Aziz Hariri, Brian Gorenc, and Simon Zuckerbraun. Abusing Silent
Mitigations: Understanding weaknesses within Internet Explorer’s Isolated Heap
and MemoryProtection. In Black Hat USA 15.  
[124] Xiaoyu He, Xiaofei Xie, Yuekang Li, Jianwen Sun, Feng Li, Wei Zou, Yang
Liu, Lei Yu, Jianhua Zhou, Wenchang Shi, and Wei Huo. Sofi: Reflection-augmented fuzzing for javascript engines. In CCS21.  
[125] Christian Holler, Kim Herzig, and Andreas Zeller. Fuzzing with code
fragments. In USENIX Security 12.  
[126] Andrei Homescu, Stefan Brunthaler, Per Larsen, and Michael Franz.
Librando: transparent code randomization for just-in-time compilers. In CCS13.  
[127] Jann Horn. Mozilla Foundation Security Advisory 2018-01, 2018.
https://www.mozilla.org/en-US/security/advisories/mfsa2018-01/.  
[128] Intel. Intel® 64 and IA-32 Architectures Software Developer Manuals,
2021.  
[129] Ivan Fratric. Domato - DOM fuzzer.
https://github.com/googleprojectzero/domato, 2017.  
[130] James Forshaw. Breaking the Chain.
https://googleprojectzero.blogspot.com/2016/11/breaking-chain.html, 2016.  
[131] Artur Janc, Charlie Reis, and Anne van Kesteren. Coop and coep
explained.
https://docs.google.com/document/d/1zDlfvfTJ_9e8Jdc8ehuV4zMEu9ySMCiTGMS9y0GU92k,
2020.  
[132] Jeff Aboud. Why You Need to Stop Using CVSS for Vulnerability
Prioritization. https://www.tenable.com/blog/why-you-need-to-stop-using-cvss-for-vulnerability-prioritization, 2020.  
[133] Jeremy Fetiveau. Circumventing Chrome’s hardening of typer bugs.
https://doar-e.github.io/blog/2019/05/09/circumventing-chromes-hardening-of-typer-bugs/.  
[134] Yonghwi Jin, Jungwon Lim, Insu Yun, and Taesoo Kim. Compromising the
macOS kernel through Safari by chaining six vulnerabilities. In Black Hat USA
20.  
[135] Zihao Jin, Ziqiao Kong, Shuo Chen, and Haixin Duan. Timing-based
browsing privacy vulnerabilities via site isolation. In SP22.  
[136] Joe Belfiore and Windows Experience Blog. Microsoft Edge: Making the web
better through more open source collaboration, 2018.  
[137] Paul Kocher, Jann Horn, Anders Fogh, Daniel Genkin, Daniel Gruss, Werner
Haas, Mike Hamburg, Moritz Lipp, Stefan Mangard, Thomas Prescher, et al.
Spectre attacks: Exploiting speculative execution. In SP19.  
[138] David Kohlbrenner and Hovav Shacham. Trusted browsers for uncertain
times. In USENIX Security 16.  
[139] Ivan Krstic. Behind the scenes of ios and mac security. In Black Hat USA
16.  
[140] Ivan Krstic. App sandbox and the mac app store. In WWDC 2011, 2011.
https://developer.apple.com/videos/play/wwdc2011/204/.  
[141] The Citizen Lab. The Million Dollar Dissident: NSO Group’s iPhone Zero-Days used against a UAE Human Rights De- fender.
https://citizenlab.ca/2016/08/million- dollar- dissident- iphone- zero-day-nso-group-uae/, 2016.  
[142] Sangho Lee, Youngsok Kim, Jangwoo Kim, and Jong Kim. Stealing webpages
rendered on your browser by exploiting gpu vulnerabilities. In SP14.  
[143] Suyoung Lee, HyungSeok Han, Sang Kil Cha, and Sooel Son. Montage: A
neural network language model-guided javascript engine fuzzer. In USENIX
Security 20.  
[144] Wilson Lian, Hovav Shacham, and Stefan Savage. A call to arms:
Understanding the costs and benefits of jit spraying mitigations. In NDSS,
2017.  
[145] Hongyang Lin, Junhu Zhu, Jianshan Peng, and Dixia Zhu. Deity: Finding
deep rooted bugs in javascript engines. In ICCT19.  
[146] Linux. Seccomp BPF (SECure COMPuting with filters). 2012.  
[147] Moritz Lipp, Michael Schwarz, Daniel Gruss, Thomas Prescher, Werner
Haas, Anders Fogh, Jann Horn, Stefan Mangard, Paul Kocher, Daniel Genkin, et
al. Meltdown: Reading kernel memory from user space. In USENIX Security 18.  
[148] LLVM Project. Scudo Hardened Allocator. https://llvm.org/docs/
ScudoHardenedAllocator.html, 2019.  
[149] ARM LTD. ARMv8 architecture reference manual, for ARMv8-A architecture
profile (ARM DDI 0487C.a). 2017.  
[150] Mads Ager and Erik Corry and Vyacheslav Egorov and Kentaro Hara and
Gustav Wibling and Ian Zerny. Oilpan: Tracing garbage collection for blink.
2013.  
[151] Adrian Marinescu. Windows vista heap management enhancements: Security,
reliability and performance. In Black Hat USA 06.  
[152] Mark Brand and Sergei Glazunov and Project Zero. Analysis of CVE-2020-16010: Chrome for Android ConvertToJavaBitmap Heap Buffer Overflow.
https://googleprojectzero.github.io/0days-in-the-wild/0day-RCAs/2020/CVE-2020-16010.html, 2021.  
[153] Mathias Bynens. Elements kinds in V8, 2017.  
[154] Mathias Bynens. JavaScript engine fundamentals: Shapes and Inline
Caches, 2018.  
[155] Matt Molinyawe, Abdul-Aziz Hariri, Jasiel Spelman. $hell on Earth: From
Browser to System Compromise. In Black Hat USA 16.  
[156] McAfee Labs. Don’t Substitute CVSS for Risk: Scoring System Inflates
Importance of CVE-2017-3735. https://www.mcafee.com/blogs/other- blogs/mcafee-labs/dont- substitute- cvss- for- risk- scoring- system- inflates-importance-of-cve-2017-3735/, 2017.  
[157] Ross Mcilroy, Jaroslav Sevcik, Tobias Tebbi, Ben L Titzer, and Toon
Verwaest. Spectre is here to stay: An analysis of side-channels and
speculative execution. arXiv preprint arXiv:1902.05178, 2019.  
[158] Microsoft. JIT Spraying Never Dies - Bypass CFG By Leveraging WARP
Shader JIT Spraying. https://sites.google.com/site/bingsunsec/ WARPJIT.  
[159] Microsoft. Control Flow Guard, 2015.  
[160] Microsoft. Introducing windows defender application guard for microsoft
edge. https://blogs.windows.com/msedgedev/2016/09/27/ application-guard-microsoft-edge/, 2016.  
[161] Microsoft. Microsoft defender application guard overview.
https://docs.microsoft.com/en- us/windows/security/threat- protection/
microsoft-defender-application-guard/md-app-guard-overview, 2021.  
[162] Microsoft. Microsoft edge support for microsoft defender application
guard. https://docs.microsoft.com/en- us/deployedge/microsoft- edge- security-windows-defender-application-guard, 2021.  
[163]Microsoft Defender Security Research Team. Exploit kits remain a
cybercrime staple against outdated software – 2016 threat landscape review
series. https://www.microsoft.com/security/blog/2017/01/23/exploit-kits-remain-a-cybercrime-staple-against-outdated-software-2016-threat-landscape-review-series/, 2017.  
[164] Matt Miller. Mitigating arbitrary native code execution in Mi- crosoft
Edge, 2017. https://blogs.windows.com/msedgedev/2017/02/ 23/mitigating-arbitrary- native- code- execution/.  
[165] Matthew R. Miller, Kenneth D. Johnson, and Timothy William Burrell.
Using virtual table protections to prevent the exploitation of object
corruption vulnerabilities.  
[166] Max Moroz and Sergei Glazunov. Analysis of UXSS exploits and mitigations
in Chromium. Technical report, 2019.  
[167] Mozilla. Static Analysis for Rooting and Heap Write Hazards.
https://firefox-source-docs.mozilla.org/js/HazardAnalysis/index.html.  
[168] Mozilla. Spy in the sandbox - security issue related to high resolution
time api. https://bugzilla.mozilla.org/show_bug.cgi?id=1167489, 2015.  
[169] Mozilla. Plugin Roadmap for Firefox. 2016.  
[170] Mozilla. Changes affecting Adobe Flash on Firefox for Mac.
https://support.mozilla.org/en-US/kb/changes-affecting-adobe-flash-firefox-mac, 2018.  
[171] Mozilla. Mitigations landing for new class of timing at- tack.
https://blog.mozilla.org/security/2018/01/03/mitigations-landing-new-class-timing-attack/, 2018.  
[172] Mozilla. Firefox 79 for developers. https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/79#javascript, 2020.  
[173] Mozilla. Security Bug Approval Process. https://firefox-source-docs.mozilla.org/bug-mgmt/processes/security-approval.html, 2020.  
[174] Mozilla. Introducing site isolation in firefox.
https://blog.mozilla.org/security/2021/05/18/introducing-site-isolation-in-firefox/, 2021.  
[175] Mozilla. Project fission - mozillawiki.
https://wiki.mozilla.org/Project_Fission, 2021.  
[176] Mozilla. Security Bug Bounty Program. https://www.mozilla.org/en-US/security/bug-bounty/, 2021.  
[177] Paul Muntean, Matthias Neumayer, Zhiqiang Lin, Gang Tan, Jens
Grossklags, and Claudia Eckert. Analyzing Control Flow Integrity with LLVM-CFI. In ACSAC19.  
[178] Hoda Naghibijouybari, Ajaya Neupane, Zhiyun Qian, and Nael Abu-Ghazaleh. Rendered insecure: Gpu side channel attacks are practical. In CCS18.  
[179] Yossef Oren, Vasileios P Kemerlis, Simha Sethumadhavan, and Ange- los D
Keromytis. The spy in the sandbox: Practical cache attacks in javascript and
their implications. In CCS15.  
[180] Chris Paget. Exploiting design flaws in the Win32 API for privilege
escalation. White Paper, 2002.  
[181] Andriy Panchenko, Fabian Lanze, Jan Pennekamp, Thomas Engel, An- dreas
Zinnen, Martin Henze, and Klaus Wehrle. Website fingerprinting at internet
scale. In NDSS16.  
[182] SoyeonPark,WenXu,InsuYun,DaeheeJang,andTaesooKim.Fuzzing javascript
engines with aspect-preserving mutation. In SP20.  
[183] phoenhex team. CVE-2018-4233 Exploit.
https://github.com/phoenhex/files/blob/master/exploits/ios-11.3.1/, 2018.  
[184] The Chromium Project. Miracleptr aka raw_ptr aka backuprefptr.
https://chromium.googlesource.com/chromium/src/+/ddc017f9569973a731a574be4199d8400616f5a5/base/memory/raw_ptr.md,
2021.  
[185] The Chromium Project. Miracleptr one pager. https:
//docs.google.com/document/d/1pnnOAIz_DMWDI4oIOFoMAqLnf_ MZ2GsrJNb_dbQ3ZBg,
2021.  
[186] Charles Reis, Alexander Moshchuk, and Nasko Oskov. Site isolation:
Process separation for web sites within the browser. In USENIX Security 19.  
[187] Thomas Rokicki, Clémentine Maurice, and Pierre Laperdrix. Sok: In search
of lost time: A review of javascript timers in browsers. In EuroSP21.  
[188] Paul Sabanal and Mark Vincent Yason. Digging deep into the flash
sandboxes.  
[189] Saelo. Attacking JavaScript Engines: A case study of JavaScriptCore and
CVE-2016-4622. http://www.phrack.org/issues/70/3.html, 2016.  
[190] Saelo. Compile Your Own Type Confusions: Exploiting Logic Bugs in
JavaScript JIT Engines. http://phrack.org/issues/70/9.html, 2019.  
[191] Christopher Salls, Chani Jindal, Jake Corina, Christopher Kruegel, and
Giovanni Vigna. Token-level fuzzing. In USENIX Security 21.  
[192] Samuel Gro?. New Trends in Browser Exploitation: Attacking Client- Side
JIT Compilers. In Black Hat USA 18.  
[193] Samuel Gro? and Project Zero. JSC Exploits.
https://googleprojectzero.blogspot.com/2019/08/jsc-exploits.html, 2019.  
[194] Michael Schwarz, Moritz Lipp, and Daniel Gruss. Javascript zero: Real
javascript and zero side-channel attacks. In NDSS18.  
[195] SecureList. Chrome 0-day exploit CVE-2019-13720 used in Operation
WizardOpium. https://securelist.com/chrome-0-day-exploit-cve-2019-13720-used-in-operation-wizardopium/94866/, 2019.  
[196] SecureList. PuzzleMaker attacks with Chrome zero-day exploit chain.
https://securelist.com/puzzlemaker- chrome- zero- day- exploit- chain/102771/,
2021.  
[197] Anatoly Shusterman, Daniel Genkin, Ayush Agarwal, Yossi Oren, Sioli
O’Connell, and Yuval Yarom. Prime + Probe 1, JavaScript 0: Overcoming Browser-based Side-Channel Defenses.  
[198] siguza. APRR | Apple hardware secrets. https://siguza.github.io/APRR/,
2019.  
[199] Payap Sirinam, Mohsen Imani, Marc Juarez, and Matthew Wright. Deep
fingerprinting: Undermining website fingerprinting defenses with deep
learning. CCS18.  
[200] Stephen Smalley, Chris Vance, and Wayne Salamon. Implementing selinux as
a linux security module. NAI Labs Report.  
[201] Michael Smith, Craig Disselkoen, Shravan Narayan, Fraser Brown, and
Deian Stefan. Browser history re: visited. In WOOT18.  
[202] Peter Snyder, Cynthia Taylor, and Chris Kanich. Most websites don’t need
to vibrate: A cost-benefit approach to improving browser security. In CCS17.  
[203] Brave Software. Brave Browser: Secure, Fast & Private Web Browser with
AdBlocker. https://brave.com, 2021.  
[204] WebKit Source. Structureid randomization.
https://github.com/WebKit/WebKit/blob/main/Source/JavaScriptCore/runtime/StructureIDTable.h,
2021.  
[205] Spring, Jonathan and Hatleback, Eric and Householder, Allen D. and
Manion, Art and Shick, Deana. Towards Improving CVSS. https:
//resources.sei.cmu.edu/library/asset-view.cfm?assetid=538368, 2018.  
[206] Statcounter Global Stats. Browser Market Share Worldwide, 2021. [207]
Sven Morgenroth. Goodbye XSS Auditor. https://www.netsparker.com/blog/web-security/goodbye-xss-auditor/, 2019.  
[208] Google Threat Analysis Group (TAG). How we protect users from 0-day
attacks. https://blog.google/threat-analysis-group/how-we-protect-users-0-day-attacks/, 2021.  
[209] Microsoft Edge Team. Mitigating speculative execution side-channel
attacks in microsoft edge and internet explorer.
https://blogs.windows.com/msedgedev/2018/01/03/speculative-execution-mitigations-microsoft-edge-internet-explorer/, 2018.  
[210] The Chromium Team. The Chromium Project. http://www.chromium.org/Home,
2021.  
[211] ArsTechnica.Firefox0-dayinthewildisbeingusedtoattackTorusers.
https://arstechnica.com/information-technology/2016/11/firefox- 0day- used-against- tor- users- almost- identical- to- one- fbi- used- in- 2013/, 2016.  
[212] The Chromium Team. Safer Usage Of C++, 2021.  
[213] Inc. The Tor Project. Tor Project | Anonymity Online.
https://www.torproject.org, 2021.  
[214] Trishita Tiwari and Ari Trachtenberg. Alternative (ab) uses for HTTP
Alternative Services. In WOOT19.  
[215] Tom Ritter. Bug Bounty Program Updates: Adding (another) New Class of
Bounties. https://blog.mozilla.org/attack-and-defense/2020/08/18/exploit-mitigation-bounty/, 2020.  
[216] Tom Van Goethem, Wouter Joosen, and Nick Nikiforakis. The clock is still
ticking: Timing attacks in the modern web. In CCS15.  
[217] Tom Van Goethem, Christina P?pper, Wouter Joosen, and Mathy Vanhoef.
Timeless timing attacks: Exploiting concurrency to leak secrets over remote
connections. In USENIX Security 20.  
[218] Pepe Vila and Boris K?pf. Loophole: Timing attacks on shared event loops
in chrome. In USENIX Security 17.  
[219] W3C. Standards - W3C. https://www.w3.org/standards/, 2021.  
[220] Junjie Wang, Bihuan Chen, Lei Wei, and Yang Liu. Superion: Grammar-aware greybox fuzzing. In ICSE19.  
[221] Yong Wang. Thinking outside the JIT Compiler: Understanding and
bypassing StructureID Randomization with generic and old-school methods. In
Black Hat USA 19.  
[222] Tao Wei, Tielei Wang, Lei Duan, and Jing Luo. Secure dynamic code
generation against spraying. In CCS10.  
[223] WeLiveSecurity. Brave browser’s Tor mode exposed users’ dark web
activity. https://www.welivesecurity.com/2021/02/22/brave-browser-tor-mode-exposed-dark-web-activity/, 2021.  
[224] WHATWG. Web Hypertext Application Technology Working Group (WHATWG).
https://whatwg.org/, 2021.  
[225] Rui Wu, Ping Chen, Bing Mao, and Li Xie. Rim: A method to defend from
jit spraying attack. In ARES12.  
[226] X41. X41 Browser Security White Paper. https://browser-security.x41-dsec.de/X41-Browser-Security-White-Paper.pdf, 2017.  
[227] Wen Xu, Soyeon Park, and Taesoo Kim. Freedom: Engineering a state-of-the-art dom fuzzer. In CCS20.  
[228] Mark Vincent Yason. Understanding the Attack Surface and Attack
Resilience of Project Spartan’s (Edge) New EdgeHTML Rendering Engine.  
[229] Zhang Yunhai. Bypass control flow guard comprehensively. In Black Hat
USA 15.  
[230] Google Project Zero. A very deep dive into iOS Exploit chains found in
the wild. https://googleprojectzero.blogspot.com/2019/08/a-very-deep-dive-into-ios-exploit.html, 2019.  
[231] Google Project Zero. In-the-Wild Series: Chrome Exploits.
https://googleprojectzero.blogspot.com/2021/01/in-wild-series-chrome-exploits.html, 2021.  
[232] Chao Zhang, Tao Wei, Zhaofeng Chen, Lei Duan, Laszlo Szekeres, Stephen
McCamant, Dawn Song, and Wei Zou. Practical control flow integrity and
randomization for binary executables. In SP13.

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1818/>

