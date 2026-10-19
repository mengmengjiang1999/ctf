# 分析供应链攻击中的C/C++运行时库代码篡改技术

阅读量 **249030**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-04-24 10:39:05

 **x**

##### 译文声明

本文是翻译文章，文章原作者 trendmicro，文章来源：blog.trendmicro.com

原文地址：<https://blog.trendmicro.com/trendlabs-security-intelligence/analyzing-c-c-runtime-library-code-tampering-in-software-supply-chain-attacks/>

译文仅供参考，具体内容表达以及含义原文为准。

## 一、前言

在过去几年里，作为安全行业的重要支撑，软件及服务器已经成为网络犯罪分子首选的攻击和篡改目标。攻击者会通过各种方式入侵原始软件，比如恶意篡改软件源代码、更新服务器，或者同时攻击这两个目标。不论如何，攻击者的目标都是悄无声息地入侵目标网络或主机，这种方法也就是所谓的供应链攻击。根据具体的技术能力以及隐蔽行动方式，攻击者对目标软件的恶意篡改方式可能也各不相同。

目前我们在实际攻击案例中主要观察到四类攻击方法：

1、在目标软件源代码级别注入恶意代码，适用于解释型/即时编译型语言，如C/C++、Java以及.NET；

2、在C/C++编译器运行时（CRT）库中注入恶意代码，例如污染特定的C运行时函数；

3、其他较少使用的入侵方法，比如入侵更新服务器，使服务器在更新过程中使用恶意的后门来替代正常的更新版本。这种恶意后门可能部署在已被入侵的下载服务器上，或者受攻击者控制的另一个完全独立的服务器；

4、使用恶意后门重新封装合法软件。这类后门软件要么托管在软件厂商已被入侵的官方网站上，要么通过BitTorrent或者其他方式进行传播。

本文依据上述四类攻击方法分析过去十年中出现的供应链攻击事件，重点关注的是第二类，我们列出来被攻击者污染的所有C/C++运行时函数，同时定位了相关的恶意软件家族。此外，我们还以ShadowPad攻击事件为例，详细分析了这类攻击方式。

第一及第二类攻击方法比较特别，涉及在代码层面上更为隐蔽及入侵程度较深的篡改操作，因此可以独立成一个类别。然而，相比较之下，第二类攻击方法更为隐蔽，因为开发人员或者任何源代码解析器都无法察觉到攻击者对代码的修改，只有在编译/链接时才会涉及到恶意代码。

## 二、攻击案例回顾

涉及第一类及第三类方法的攻击事件包括：

1、[MediaGet](https://www.zdnet.com/article/windows-attack-poisoned-bittorrent-client-set-off-huge-dofoil-outbreak-says-microsoft/)供应链攻击事件。MediaGet是一款BitTorrent客户端，攻击者通过升级过程来布置后门（2018年2月中旬），涉及恶意更新组件以及包含木马功能的`mediaget.exe`副本；

2、针对[M.E.Doc](https://blog.talosintelligence.com/2017/07/the-medoc-connection.html)的Nyetya/MeDoc攻击事件。这是Intellect
Service提供的一款会计软件，攻击者通过软件更新系统来传播Nyetya/NotPetya勒索软件（2017年4月份），篡改了`ZvitPublishedObjects.dll`
.NET模块并在其中植入后门；

3、针对EventID的[KingSlayer](https://www.rsa.com/en-us/blog/2017-02/kingslayer-a-supply-chain-attack)攻击事件，攻击者成功入侵了Windows Event Log
Analyzer软件源代码（程序使用.NET开发）及更新服务器（2015年3月份）。

[Monju事件](https://www.contextis.com/en/blog/context-threat-intelligence-the-monju-incident)中只用到了第三类方法，攻击者入侵了GOM
Player（GOMLab提供的一款媒体播放器）更新服务器，针对特定目标投放Gh0st RAT变种。

[Havex攻击事件](https://www.netresec.com/?page=Blog&month=2014-10&post=Full-Disclosure-of-Havex-Trojans)用到了第四类方法，攻击者入侵了多个工业控制系统（ICS）网站及软件安装程序（2013年及2014年）。

同时使用第二类和第三类方法的攻击案例包括：

1、[ShadowHammer](https://securelist.com/operation-shadowhammer/89992/)攻击事件，攻击者入侵了计算机厂商的更新服务器，根据网卡适配器的MAC地址来筛选攻击目标（具体目标用户仍未澄清）（2018年6月份），攻击者使用了一个恶意的更新组件；

2、针对[游戏产业](https://www.welivesecurity.com/2019/03/11/gaming-industry-scope-attackers-asia/)的攻击事件（Winnti.A），攻击者入侵了3个游戏公司，在主程序执行文件中植入后门（2019年3月份）；

3、[CCleaner](https://www.theverge.com/2017/9/18/16325202/ccleaner-hack-malware-security)攻击事件，攻击者入侵了Piriform公司，在CCleaner软件中植入后门（2017年8月份）；

4、[ShadowPad](https://www.trendmicro.com/vinfo/us/security/news/cybercrime-and-digital-threats/shadowpad-backdoor-found-in-server-management-software)攻击事件，攻击者入侵了NetSarang Computer,
Inc.，在公司所有产品中植入后门（2017年7月份）。攻击者将恶意代码注入`nssock2.dll`库，而该公司所有产品都会使用这个库。

[Winnti](https://securelist.com/winnti-more-than-just-a-game/37029/)攻击组织同样用到了第二类及第三类方法，该组织针对的是在线视频游戏行业，入侵了目标企业的更新服务器，使用AheadLib传播恶意后门或者程序库（2011年）。

另一个案例是[XcodeGhost](https://unit42.paloaltonetworks.com/novel-malware-xcodeghost-modifies-xcode-infects-apple-ios-apps-and-hits-app-store/)攻击事件（2015年9月），攻击者修改了Apple的Xcode集成开发环境（IDE）以及编译器的CoreServices Mach-O目标文件，在其中注入了恶意软件，感染使用该Xcode
IDE编译的每个iOS应用。包含后门的IDE环境托管在国内的多个文件共享服务平台上，导致数百个应用被后门感染并发布在iOS App Store上。

关于供应链攻击还有另一个案例比较有趣：[event-stream](https://blog.npmjs.org/post/180565383195/details-about-the-event-stream-incident)攻击事件（2018年11月）。Event-Stream是npm（Node.js包管理器）广泛使用的一个包，而npm是JavaScript编程语言的包管理器。event-stream包的原始开发者/维护者将发布权委托给第三方（攻击者），而攻击者在event-stream包中添加了flatmap-stream依赖项。这个恶意包针对的是特定开发人员，这些开发者用到了Copay比特币钱包应用，攻击者的最终目的是窃取比特币。当开发者执行build脚本执行时就会写入恶意代码，这也增加了攻击过程的隐蔽性。

在过去十年内发生的大多数供应链攻击案例中，我们并不知道攻击者最开始的攻击途径，或者相关信息并没有公之于众。此外，无论是从数字取证还是TTP的角度来看，关于恶意代码如何注入正常软件代码库的具体细节也没有公开。然而，在本文中我们将以ShadowPad案例作为样本，来分析攻击者在供应链攻击中所使用的第二类方法，这种方法对代码的篡改方式比较复杂，难以检测。

## 三、深入分析ShadowPad

第一类方法涉及对源代码的篡改，第二类方法涉及对C/C++运行时的篡改，这两种方法之间有细微的差别。根据篡改代码的特点及位置，第一种方法可能更容易被检测出来，而如果没有文件监控及一致性检查机制，第二种方法检测起来更加困难。

目前关于C/C++运行时库污染或篡改的供应链攻击报告都集中在Windows二进制文件，每个攻击案例都使用微软Visual
C/C++编译器以及不同版本的链接器进行静态编译。此外，被污染的所有函数都不是C/C++标准库，但都与微软Visual
C/C++编译器运行时初始化例程有关。如表1所示，我们可以看到目前已知的所有恶意软件家族以及所篡改的运行时函数：

![](https://p3.ssl.qhimg.com/t0129c88b4c16a5ed6b.png)

表1. 供应链攻击中被污染/修改的Microsoft Visual CRT函数

链接器（linker）负责为启动代码准备必要的CRT库，开发者可以通过显示链接器标志来指定使用不同的CRT库，否则就会使用默认静态链接的CRT库（`libcmt.lib`）或者另一个库。在执行程序的`main()`函数之前，启动代码会先执行各种环境设置操作，这些操作包括异常处理、线程数据初始化、程序终止以及cookie初始化。需要注意的是，CRT的具体实现与编译器、编译器选项、编译器版本以及具体平台有关。

微软之前曾会提供Visual C运行时库头文件以及编译文件，开发者可以使用这些文件自行编译。比如，对于Visual Studio
2010，这些头文件具体路径为`Microsoft Visual Studio
10.0\VC\crt`，而被ShadowPad篡改的[`_initterm()`](https://docs.microsoft.com/en-us/cpp/c-runtime-library/reference/initterm-initterm-e?view=vs-2019&ranMID=24542&ranEAID=je6NUbpObpQ&ranSiteID=je6NUbpObpQ-gOaHg9N7Bc2EHjXX58aMnw&epi=je6NUbpObpQ-gOaHg9N7Bc2EHjXX58aMnw&irgwc=1&OCID=AID681541_aff_7593_1243925&tduid=\(ir__xxrrjfb1ekkfrjbgxmlij6lydu2xmphmclcw2t9900)(7593)(1243925)(je6NUbpObpQ-gOaHg9N7Bc2EHjXX58aMnw)()&irclickid=_xxrrjfb1ekkfrjbgxmlij6lydu2xmphmclcw2t9900)函数位于`crt0dat.c`中，如下所示（为保持简洁性，我们删除了所有注释）：

![](https://p3.ssl.qhimg.com/t0187295670c9349812.jpg)

这个内部函数负责遍历函数指针表（跳过null表项）并初始化函数指针，只有在C++程序初始化阶段才会调用该函数。被修改的`nssock2.dll`采用C++语言编写。

`pfbegin`参数指向指针表中的第一个有效元素，而`pfend`指向的是最后一个有效元素。`_PVFV`函数类型的定义位于`internal.h`
CRT文件中，如下所示：

![](https://p2.ssl.qhimg.com/t01e721398e8de7e86f.jpg)

以上函数定义位于`crt0dat.c`文件中，而`crt0dat.c`目标文件位于`libcmt.lib`库中。

![](https://p5.ssl.qhimg.com/t01b9a4f245e000c180.jpg)

图. 被ShadowPad修改的`_initterm()`运行时函数

与ShadowPad
`_initterm()`函数对应的函数指针表如下图所示（介于`pfbegin`以及`pfend`之间），这个表用于在程序开头构造对象（特别是用来调用C++构造函数），具体流程如下图所示：

![](https://p3.ssl.qhimg.com/t017ec40300485f78a1.jpg)

图. 被ShadowPad修改的`_initterm()`运行时函数的函数指针表

如上图所示，函数指针表中`0x1000F6A0`虚拟地址处的`malicious_code`已被修改，指向恶意代码（`0x1000E600`）。更确切地说，攻击者实际上修改的是函数指针表，而不是`_initterm()`函数。

编译好的ShadowPad代码对`_initterm()`
CRT函数的交叉引用关系图如下所示。从该图中我们可以找到调用该函数的所有调用路径（可达性路径）以及该函数自己调用的其他函数。执行ShadowPad代码的实际调用路径为：

    
    
    DllEntryPoint() -> __DllmainCRTStartup() -> _CRT_INIT() -> _initterm() -> __imp_initterm() -> malicious_code()
    

![](https://p4.ssl.qhimg.com/t01cc45341ccc80aded.jpg)

图. 被ShadowPad修改的`_initterm()`运行时函数的交叉引用关系图

需要注意的是，`_initterm()`内部函数由CRT初始化函数`__CRT_INIT()`调用，该函数负责C++ DLL初始化，原型如下：

![](https://p4.ssl.qhimg.com/t01896974f8af740021.jpg)

如前文所述，该函数的一个功能就是调用`nssock2.dll`中C++代码的构造函数，具体实现位于`crtdll.c` CRT文件 ->
`crtdll.obj`目标文件 -> `msvcrt.lib`库文件中。

`_CRT_INIT()`函数的具体实现如下代码片段所示：

![](https://p5.ssl.qhimg.com/t013deb387add321f87.jpg)

那么攻击者如何才能篡改这些CRT函数呢？攻击者可以覆盖原始的`libcmt.lib`/`msvcrt.lib`库，将其替换为恶意库，或者修改链接器标志，使其指向恶意的库文件。另一个可能就是劫持链接过程，当链接器将所有引用解析成各种函数时，攻击者的工具可以监控该过程，拦截并提供被修改的函数定义。此外，编译器的关键可执行程序（如linker程序）如果被插入后门，也是另一种隐蔽的攻击方式。

## 四、总结

虽然使用第二种方法的攻击事件非常少，也难以预测，并且这类攻击活动针对性更强，但当发生时就是一起黑天鹅事件：受害者将措手不及，并且攻击造成的影响将非常严重且影响范围非常广泛。

在供应链攻击中，篡改CRT库函数的确是非常大的安全威胁，需要整个安全社区进一步关注这方面风险（特别是需要验证和检查开发和构建环境的完整性）。

开发者可以采取措施，确保软件开发和构建环境足够安全。此外，维护和交叉验证源代码及所有编译器库和程序的完整性也是不错的选择。在集成和部署之前，开发者必须检查和扫描所使用的第三方库和代码，寻找是否存在任何恶意特征。正确的网络划分可以将构建和发布环境（更新服务器）中的关键资产与网络中的其他部分分离，这也是必不可少的措施。此外，开发者还需要对发布服务器和端点采取非常严格的访问限制策略，部署多因素身份认证。当然，如果开发者如果对自己的系统不上心，没有持续负责监控，那么以上所有措施也无济于事。

本文翻译自blog.trendmicro.com [原文链接](https://blog.trendmicro.com/trendlabs-security-intelligence/analyzing-c-c-runtime-library-code-tampering-in-software-supply-chain-attacks/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/177106](/post/id/177106)

安全客 - 有思想的安全新媒体

本文转载自: [blog.trendmicro.com](https://blog.trendmicro.com/trendlabs-security-intelligence/analyzing-c-c-runtime-library-code-tampering-in-software-supply-chain-attacks/)

如若转载,请注明出处： <https://blog.trendmicro.com/trendlabs-security-intelligence/analyzing-c-c-runtime-library-code-tampering-in-software-supply-chain-attacks/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [供应链攻击](/tag/供应链攻击)
  * [代码安全](/tag/代码安全)

 **+1** __2赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

