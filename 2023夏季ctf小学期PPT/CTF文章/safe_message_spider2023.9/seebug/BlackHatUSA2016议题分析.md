来源链接：http://riusksk.me/2016/09/25/BlackHat-USA-2016-议题分析/

作者： **riusksk（泉哥）**

主页：http://riusksk.me

本文已发表于2016年9月CSDN的《程序员》杂志，转载请注明出处。

* * *

### 大会概述

BlackHat USA 是世界上最著名的黑客大会BlackHat的主场，规模远超亚洲、欧洲等分会，今年大约有15000人参会，依然在美国拉斯维加斯举办。

大会全程共6天，包括 Training 培训、Keynote 议题分享、Arsenal 工具展示以及素有”黑客奥斯卡“之称的 Pwnie Awards
颁奖。

今年有上百个议题入选，涉及的安全领域也是相当广泛全面，包括移动安全、物联网、软件安全、加密、工控、企业安全、Web安全、逆向工程、恶意软件等等，整体上跟往年的议题类型差不多。

每年的BlackHat
USA都代表着一个安全技术发展的”风向标“，在这可以看到全球顶端安全研究人员的研究成果，以及业界安全发展趋势。不少政府人员，比如FBI经常会出现在会场，以前也有FBI在现场带走一些有犯罪记录的人员，或者禁止涉及过于敏感内容的演讲，但一般是在BlackHat的兄弟会议Defcon上下手，比如曾经某黑客在Defcon演讲完后，在回旅馆的路上被抓了，还有之前MIT学生破解波士顿地铁免费乘坐地铁的演讲也被禁止掉。

### 精彩议题分析

笔者针对BlackHat官网上公布的各个议题pdf筛选了一遍，挑选出一些大家可能感兴趣，或者技术新颖有兴趣的议题作简要介绍和点评。

#### 1、《Using EMET to Disable EMET》——绕过微软EMET防护工具实现软件漏洞利用的方法

![](http://riusksk.me/media/14710526596463/14711374846572.jpg)
图1：禁用EMET前后LoadLibraryA函数入口代码的对比情况

该议题来自国外著名安全公司FireEye的分享，是一家专门为企业提供安全防护产品的公司，该公司曾发现许多0Day漏洞以及APT攻击事件。

**【内容简介】**

Microsoft’s Enhanced Mitigation Experience Toolkit
(EMET)是一款针对用户程序的内存防护工具，可以提高软件的漏洞利用难度。

FireEye安全研究人员介绍了一种新型的禁用EMET技术，同时举例了一些以前针对EMET的攻击方式。他们介绍的新型绕过技术主要是利用ROP技术找到DLLMain函数入口，然后实现以下代码的调用：

    
    
    BOOL WINAPI DllMain (GetModuleHandleA("EMET.dll") , DLL_PROCESS_DETACH , NULL);

EMET主要通过向保护的用户进程注入emet.dll或者emet64.dll，同时因为`GetModuleHandleA`
未被Hook，所以使用以上方法去卸载EMET.dll中的各种API Hook，虽然这不会将EMET从内存中移除，但已经足够禁用它的所有防护功能。

**【点评】**

在著名的黑客赛事Pwn2Own中，微软要求必须绕过EMET和沙盒保护攻下64位IE浏览器才算成功，因此绕过EMET成了攻破IE的必经之路。

不过，由于EMET并非默认在系统上开启的，需要用户自行安装，因此实际上使用EMET来保护系统软件的用户并不会太多，甚至包括一些安全人员也很少使用它，在诸多实际攻击案例中，大多不用绕过EMET就可以攻下系统。

#### 2、《Exploiting Curiosity and Context》——针对陌生链接点击情况的安全调查报告

![](http://riusksk.me/media/14710526596463/14711403836865.jpg)

该议题来自德国萨尔州大学和埃尔朗根-纽伦堡大学安全研究人员的分享。

**【内容简介】**

这是一份安全调查报告，关于点击陌生链接的调查情况，作者通过邮件与Facebook两种途径进行调查分析，专门构造特定的消息内容，或者链接中包含对方id等各种方式来引起点击者的好奇，最后统计出点击占比，以及引导用户点击的各种主要影响因素。

**【点评】**

很多漏洞或者病毒都是通过链接、邮件等方式进行恶意传播，通过邮件利用漏洞进行攻击是当前APT攻击事件中最常用的手段，因此提高安全意识，不要随意打开陌生链接、邮件附件是相当有必要的。当然反之，这份报告对于黑产人士也是有一种借鉴作用，如何构造出能够引起目标用户的兴趣和好奇，增加点击成功率也是一个参考方向。

从报告中可以看出，一些社交平台如Facebook，这种比邮件交互性更大的网络平台，更容易引起用户的点击，而且一些点名道性的链接内容，或者一些能引起用户兴趣的内容，也更容易诱使用户点击。

#### 3、《DOES DROPPING USB DRIVES REALLY WORK?》——U盘社工调查报告

![](http://riusksk.me/media/14710526596463/14711422054269.jpg) 图3：U盘社工调查的统计结论

该议题来自Google的Elie Bursztein研究员，主要从事反欺诈工作。

**【内容简介】**

该议题主要是基于社工技术的一份安全调查，使用类似以前”BadUSB“技术，基于Teensy（俗称”橡皮鸭“）编写模拟输入功能的U盘，能够回连后门的恶意功能，支持Windows、Linux和OSX等多系统平台。

每个U盘成本大约$40美元，假装丢在各个不同的地方，共放了297个，成本$11880美元（￥78792人民币），投入成本也是很大。

最后的调查结果是：至少48%的人打开U盘执行了恶意程序。

**【点评】**

一份挺有趣的安全调查报告，安全技术要求不高，主要注重于动手实践能力，自己动手制作297个U盘也是需要一定耐心和时间的，同时花近8万块的成本，也是颇舍得投入的。

#### 4、《Subverting Apple Graphics Practical Approaches To Remotely Gaining
Root》——Pwn2Own 2016 OSX项目所用漏洞的利用分析

![](http://riusksk.me/media/14710526596463/14711451665465.jpg)

来自腾讯科恩实验室的分享，之前通过挖掘到的OSX漏洞赢得Pwn2Own 2016的OSX项目，并在该议题里面作了详细的技术分享。

**【内容简介】**

从用户层和内核层的角度分析Apple Graphics图像处理系统的攻击面并结合漏洞实例进行分析。

用户层攻击面分析中，以Windows Server为例介绍了一些漏洞实例，比如CVE-2014-1314的API _XCreateSession
涉及敏感动作setuid，而没有对用户传递的路径参数进行严格校验，导致setuid可以越权逃逸沙盒，最后苹果以拒绝所有沙盒进程调用_XCreateSession
来修复此漏洞。同时也列举了一些其它API接口存在漏洞，比如_XSetMessageFile、_XSetGlobalForceConfig等等，后面又详细介绍了CVE-2016-1804
UAF漏洞的利用。

内核层攻击面分析中，主要介绍苹果图表驱动接口IOAccelSurface的漏洞，也就是此前他们在Pwn2Own上用于攻破OSX内核的漏洞，分享了漏洞利用技巧，包括ROP绕过SMEP/SMAP/SIP、利用信息泄露绕过kASLR等等。

**【点评】**

一份颇有干货的议题，此前他们在CanSecWest黑客大会上分享过关于Apple Graphics 内核驱动漏洞挖掘的议题《Don’t Trust Your
Eye- Apple Graphics Is Compromised》，而此次的议题主要是分享Pwn2Own上的漏洞分析与利用，侧重点不同，推荐一阅。

#### 5、《CANSPY：A Platform for Auditing CAN Device》——汽车CAN设备安全审计工具

![](http://riusksk.me/media/14710526596463/14711499419536.jpg)图5：CANSPY硬件

来自Airbus空中客车公司（欧洲一家民航飞机制造公司）的安全研究员作的分享。

**【内容简介】**

关于汽车CAN（Controller Area
Network,控制器局域网络）安全的议题，作者发布的CANSPY是一款硬件设备，支持CAN数据伪造攻击、中间人攻击等手段，固件相关代码已在github上开源。

**【点评】**

这几年的汽车安全议题开始逐渐火起来了，关注CAN/ODB安全的人越来越多，一些工具也逐渐有安全研究人员开源出来，这都是一些不错的学习资料。笔者在些推荐一本关于汽车安全的电子书《Car
Hacker’s Manual》，有兴趣的读者可以阅读下。 这个议题涉及的技术细节较少，这是不足的一点，但关于工具CANSPY可以关注下。

#### 6、《Viral Video : exploiting SSRF in video converters》——
视频转换工具的SSRF漏洞分析与利用

![](http://riusksk.me/media/14710526596463/14711507668619.jpg)图6：ffmpeg
SSRF漏洞利用示例

来自俄罗斯 Mail.RU 公司的两名安全研究员分享的议题

**【内容简介】**

总结了之前出现的FFmpeg视频转换时出现的SSRF漏洞，可读取服务器上的任意文件，比如/etc/passwd被用于攻破很多大公司的服务器，在很多漏洞平台上被刷爆了。

**【点评】**

只是对过去出现的历史漏洞的总结，但这个漏洞也是相当经典，影响甚广，所以这里列出来提下，并没有其它新内容。

#### 7、《Advanced Cross-Site Search Attacks》——跨站搜索攻击技术

![](http://riusksk.me/media/14710526596463/14711525967284.jpg) 图7：XS-Search技术示例

来自Cyberpion公司，以色列巴伊兰大学博士的安全研究员分享的议题。

**【内容简介】**

Cross-Site Search (XS-search)
Attack，跨站搜索攻击，通过向目标站点发送搜索请求，从而探测到用户的敏感信息，因为受害者的浏览器通常包含一些涉及隐私信息的服务授权（比如Gmail）。

虽然攻击者因为”同源策略“无法直接获取到响应数据，但可以测量响应时间，根据响应时间的差异来判断隐私信息的准确性。

**【点评】**

一种新型的Web攻击方式，基于时间差异和服务搜索功能来获取用户隐私信息，更像是一种边信道攻击。虽然思路很好，但在实战应用过程中，可能就比较受限，而且只有捕获或可搜索信息量够大时，才比较有实际价值的信息获取，同时也基于搜索关键词的健全性，有它的局限性所在。

#### 8、《Web Application Firewalls: Attacking detection logic
mechanisms》——基于正则缺陷绕过WAF

![](http://riusksk.me/media/14710526596463/14711547098778.jpg)
图8：绕过Edge浏览器的XSS过滤器

来自Positive安全公司的技术分享。

**【内容简介】**

针对主流的开源WAF（比如OWASP CRS、ModSecurity、Comodo
WAF、PHPIDS、QuickDefense、Libinjection)中的正则表达式进行逻辑测试，主要偏重于正则上的缺陷进行WAF绕过。

**【点评】**

WAF不是万能的，被绕过也是正常的，市面上的各处WAF也都基本被绕过，但通过它可以大大地提高攻击成本，还是可以阻断一部分黑客的。
该议题偏重于WAF正则问题，更系统化的WAF绕过技术总结，推荐PHDays黑客大会上的《Web Application Firewall
Bypassing》议题。

#### 9、《Pwning Your Java Messaging With Deserialization
Vulnerabilities》——JMS反序列化漏洞分析与利用

![](http://riusksk.me/media/14710526596463/14711579996412.jpg)
图9：挖掘到的Java反序列化漏洞修复情况

来自Code White安全公司的分享议题。

**【内容简介】**

关于Java反序列化漏洞的相关技术分享，介绍Java Message
Service（JMS）存在的攻击面，利用ObjectMessage消息类型中包含的序列化对象，经getObject函数处理时，如不正当使用，可能会反序列化用户传递的任意对象，就可能造成反序列化漏洞。然后作者通过分析很多主流的Java应用服务发现了不少漏洞。最后，作者分享一款Java消息反序列化漏洞的利用工具JMET（Java
Message Exploitation Tool），并且已在GitHub上开源。

**【点评】**

现在BlackHat上关于Web的议题已经越来越少，有干货的Web安全议题更是少之又少，该议题还是不错的Web议题，而且有实际的漏洞产出，思路值得借鉴和延伸。

#### 10、《The Art of Defense：How vulnerabilities help shape security features
and mitigations in Android》——Google通过Android漏洞制定的通用防御策略介绍

![](http://riusksk.me/media/14710526596463/14711593522037.jpg)
图10：Android主要的安全防御机制

来自 Google Android 平台安全团队的负责人 Nick Kralevich 针对 Android 的防御机制所做的技术分享

**【内容简介】**

列举了当前Android平台主要的安全机制，并以多个经典的Android漏洞（PingPong、Stagefright等等）为例，分析其中的一些攻防思路，如何根据报告的漏洞举一反三，以解决同一类问题是防御的关键。

**【点评】**

企业内部在做业务安全时，单纯修复外部报告的漏洞本身，是远远不够的。Google做了很好的示范，应该举一反三，思考如何去解决各个业务中同类问题。这种思路无论在软件系统，还是Web上，都是通用的。外部报告一个漏洞，如何提高自身安全系统的检测能力去批量发现同类漏洞？如何提高自身系统的防御能力去增加攻击成本？

#### 11、《$hell on Earth: From Browser to System Compromise》——Pwn2Own 2016
各项目漏洞原理与利用

![](http://riusksk.me/media/14710526596463/14711621506431.jpg)
图11：腾讯科恩实验室的OSX项目（从safari到内核提权）的演示demo

来自趋势科技 Zero Day Initiative 的安全研究员针对Pwn2Own 2016 黑客大赛上各种被攻破的项目做的技术分享。

**【内容简介】**

对Pwn2Own 2016黑客大赛上的每个攻破项目所涉及的漏洞原理、利用技巧进行简要地分析，并提供demo演示。

漏洞包括腾讯科恩发现的Safari漏洞到内核提权漏洞、Flash到系统提权漏洞、Edge到系统提权的漏洞，韩国神童Lokihardt发现的Safari漏洞到内核提权漏洞、Edge到系统提权漏洞，360发现的Chrome到内核提权的漏洞、Flash到系统提权漏洞。

**【点评】**

标题已经足够牛逼，但每个漏洞也就简短的几页精要地介绍下，其实涉及的内容还是蛮多的，要是扩展出来细说，可以说的技术内容就太多了。

其实每个攻破的项目都可以作为一个BlackHat议题拿来讲的，现在被ZDI的人一次性讲完，各个团队可能也不太方便再拿出来讲了。

#### 12、《The Art of Reverse Engineering Flash Exploits》——Flash
Exploit样本的逆向分析方法

![](http://riusksk.me/media/14710526596463/14711637873500.jpg)
图12：议题中分析的flash样本列表

来自微软安全研究人员Jeong Wook Oh的技术分享。

**【内容简介】**

介绍了多个不错的Flash分析工具，并挑选几个经典的Flash漏洞案例以及利用技术（比如Vector长度和ByteArray长度篡改、JIT攻击、绕过CFG的技术）进行分析。

**【点评】**

一个不错的议题，对过去近一年的经典Flash漏洞利用样本进行逆向分析，介绍了当前流行的主流Flash漏洞利用技术，上面的截图已经详细地列出各个漏洞所使用的利用技术，是对过去Flash漏洞利用技术很好的总结，推荐阅读。

#### 13、《The Year In Flash》—— Google Project Zero对过去一年多的Flash漏洞成因和发展趋势的分析

![](http://riusksk.me/media/14710526596463/14711649291416.jpg)
图13：近一年多的Flash漏洞时间轴

来自 Google Project Zero 的一位女安全研究员Natalie Silvanovich所做的分享。

**【内容简介】**

主要也是对过去一年多的Flash漏洞以及Adobe针对Flash增加的内存安全保护机制进行分析，相对上一个Flash议题的不同，它更多地分析漏洞成因，以及一些安全事件，并对未来Flash漏洞的发展进行预测。

每个阶段经常出现同一类型的Flash漏洞，比如Flash解析其它多媒体文件（比如MP4）、或者图片文件，也对每个Flash漏洞挖掘方式进行推测，绝大部分是Fuzzing出来的。

**【点评】**

对过去一年多Flash漏洞进行总结，其中可以看到一些Flash漏洞挖掘的趋势，单纯Fuzzing
SWF文件基本已经很难发现漏洞，复合文件的Fuzzing是趋势，比如SWF+MP4、SWF+JPG等等，还有AS3漏洞等。

上述趋势以及最后作者的总结，都可以作为漏洞挖掘者尝试的Fuzzing方向，不过现在各大浏览器已经开始禁用Flash，相信未来会逐步被Html5所代替，但饿死的骆驼比马大，其短期内还是会继续受漏洞影响的。

#### 14、《Pangu 9 Internals》——盘古越狱团队针对iOS9越狱技术原理的剖析

![](http://riusksk.me/media/14710526596463/14711670070390.jpg) 图14：iOS内核攻击面

来自盘古越狱团队针对iOS 9越狱技术的分享议题。

**【内容简介】**

讲解通过XPC调用服务com.apple.PersistentURLTranslator.Gatekeeper实现跨目录读写任意文件，最后再从任意文件读写转换成代码执行，然后再介绍在iOS9越狱中使用到的内核漏洞。

**【点评】**

笔者对iOS越狱技术研究相对较少，技术内容就不点评了，但只需要知道一点，会写iOS越狱程序的都很牛逼。

* * *

### 安全发展趋势

从所有BlackHat议题中可以发现当前业界的安全关注点，以及未来安全发展趋势的风向。笔者对所有议题内容过了一遍，对于安全发展趋势，总结出以下3点供大家参考：

#### 1、机器学习在安全领域的运用会逐渐增加

目前在一些漏洞检测、入侵检测系统，恶意软件分类和僵尸网络流量识别领域已经使用到机器学习。Defcon
CTF大赛现场也有一支机器人队伍，全自动化挖洞补洞，并战胜两个人类队伍（能进入Defcon决赛也不会太差），从这些都可以看到机器学习在未来运用到安全领域将来越来越多。

#### 2、Flash漏洞的利用难度再不断上升，但仍可能被攻破，同时未来Flash可能退出历史舞台

目前一些主流浏览器，比如Chrome、Firefox已经开始禁用Flash，开始用Html5代替。再加上Adobe针对Flash增加的一些安全防御机制，大大增加了漏洞攻击成本，提高了漏洞利用难度，但还是有可能被攻破的。

#### 3、物联网安全与云安全依然倍受关注

最近两年各大安全大会上，一般都会有关于物联网安全与云虚拟化安全的相关议题，本次BlackHat也不例外。各种智能设备目前仍处于起步阶段，很多还不够成熟，但随着未来发展，在普通民众普及开来后，安全的影响面就更大了。云安全更多是一些互联网厂商当前需要解决的，攻防之战已经展开了，在云上被经常使用的虚拟化软件VM、QEMU、XEN的漏洞也会被经常曝光，主要用于逃逸虚拟机。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/55/>

