2020年2月24日-28日，网络安全行业盛会RSA Conference将在旧金山拉开帷幕。今天绿盟君将介绍创新沙盒十强初创公司之一：
**ForAllSecure** 。

一、公司介绍

ForAllSecure是由来自卡耐基梅隆大学的ForAllSecure安全研究团队于2012年创立的公司，工作地点包括宾夕法尼亚州匹兹堡、旧金山湾区和弗吉尼亚州水晶城。创始人David
Brumley、Thanassis Avgerinos和Alex
Rebert均来自卡耐基梅隆大学并拥有相关专业背景。公司在A轮融资中获得1500万美元，由New Enterprise
Associates领投。其主打“下一代”模糊测试技术，并基于此技术实现模糊测试系统Mayhem，凭借Mayhem的出色表现以大幅领先优势在美国国防部先进项目研究局（DARPA）于2016年主办的网络超级挑战赛（CGC）中一举夺魁。ForAllSecure还在2017年被「麻省理工科技评论」选入“全球最聪明的50家公司”榜单（位列第35名）。

![https://mmbiz.qpic.cn/mmbiz_jpg/IpYUt4DIvZezicIWVtDzyKJKGYF50S4zmdUo5PXeQPIR3XickPbThd0nxM7A2VYARBSSFqibRa4SlickV39m1KzOSw/640?wx_fmt=jpeg](https://image.3001.net/images/20200220/1582170833_5e4e02d14b290.jpg!small)

公司提供Mayhem模糊测试解决方案，将自动化持续性安全测试融入DevOps流程，力求在早期发现漏洞、修复漏洞，以提高软件安全性。与传统模糊测试技术相比，该“下一代”模糊测试技术结合使用“符号执行”技术和“导向型模糊测试”技术，能够针对测试发现的安全漏洞自动化生成概念性验证（PoC）和补丁，在一定程度上避免传统白盒测试的高误报和黑盒测试的盲目性，具有很高的创新性和价值。

二、背景介绍

根据Cybersecurity
Ventures的应用安全报告显示，应用程序的攻击面正在以每年1110亿行代码的速度增长，另外，0day漏洞利用程序被公布的速率已经从2015年的“每周一个”增长到2021年的“每天一个”。

与此同时，DevOps正在被越来越多的团队和组织接受和采用。然而，绝大多数应用安全工具并不能跟上DevOps的脚步。例如，由于其居高不下的误报率，“静态代码分析”工具大大限制了安全、开发和测试人员的生产力。

另一方面，企业级漏洞管理方案则是有限应对策略。例如，“软件组成分析”工具只能检测那些已经被公开并分配了CVE编号的漏洞。

面对这些限制和问题，ForAllSecure提供“下一代模糊测试”安全方案Mayhem，兼具导向型模糊测试的可靠性和符号执行技术的创造力，帮助企业在软件开发生命周期中更早地发现安全风险并快速消除。

三、产品介绍

Mayhem是一个帮助企业以机器级速度和规模测试软件的辅助型智能行为测试解决方案。它结合使用符号执行和导向型模糊测试技术，通过监控目标程序的行为来动态生成测试用例。

官方并未直接给出Mayhem的架构组成。绿盟君根据官方公开资料整理出的大致架构如下：

![https://mmbiz.qpic.cn/mmbiz_jpg/IpYUt4DIvZezicIWVtDzyKJKGYF50S4zml4pEYSZf3BqXZh9iahX1m3fyxK4YJ7ticq7WUU6yWicBIBRwibdgomicBnQ/640?wx_fmt=jpeg](https://image.3001.net/images/20200220/1582170847_5e4e02df0f3a8.jpg!small)

其中：

Translator用于将二进制程序翻译为易于分析的中间表示；

Offensive Tools用于寻找漏洞并构建PoC或ExP；

Defensive Tools用于生成补丁；

Controller用于统筹整个流程；

Mayhem的工作流程如下：

![https://mmbiz.qpic.cn/mmbiz_jpg/IpYUt4DIvZezicIWVtDzyKJKGYF50S4zmRYMjPiaJamia6qEDaEjriaVR76uI8jNV0E8RQ9ibzYicDSAAmIvyX3FdJPw/640?wx_fmt=jpeg](https://image.3001.net/images/20200220/1582170855_5e4e02e79ce71.jpg!small)

我们可以看到，上述流程正是DevOps的一部分：

1、用户向SCM（代码仓库）提交应用代码；

2、系统自动基于SCM最新代码构建应用；

3、系统自动将构建的应用提交给Mayhem进行测试，而Mayhem的测试又可分为三个相辅相成的逻辑模块：

发送测试数据

监视目标行为

收集、分类并储存结果

4、 用户与Mayhem交互，查询应用的风险情况并进行下一步处理。

另外，Mayhem支持多种语言、平台和DevOps环境，能够满足不同用户的需求：

![https://mmbiz.qpic.cn/mmbiz_jpg/IpYUt4DIvZezicIWVtDzyKJKGYF50S4zmbvwUuDLkhzhz7lriba9ib3TTIN0lXlgyb5lh7Y0xpee6wAVNpicMnUichg/640?wx_fmt=jpeg](https://image.3001.net/images/20200220/1582170864_5e4e02f09bdde.jpg!small)

接下来，我们展示一个具体的应用案例。借助这个案例，我们能够真正触摸到Mayhem，对其工作流程有深层次的理解；另一方面，也能够在一定程度上体会到它的实力和价值所在。

开始测试

Mayhem提供了友好的用户交互界面。初始化完成后，正式进入测试阶段，可以看到测试正在进行：

![https://mmbiz.qpic.cn/mmbiz_jpg/IpYUt4DIvZezicIWVtDzyKJKGYF50S4zmhhdlq43k7qM6xxIF9hpKGznxsJiaGC1ic1ks25tUom2CIZ1YCVaLAVow/640?wx_fmt=jpeg](https://image.3001.net/images/20200220/1582170873_5e4e02f95181f.jpg!small)

查看基本测试结果

测试结束后，可以查看测试结果，了解应用的脆弱点：

![https://mmbiz.qpic.cn/mmbiz_jpg/IpYUt4DIvZezicIWVtDzyKJKGYF50S4zmOYrXxbVa4hGWRpyHJ3fDsA8VZW6iczkX1WEvFFloUDXqocEppNK2Cmw/640?wx_fmt=jpeg](https://image.3001.net/images/20200220/1582170883_5e4e03038fd4d.jpg!small)

值得注意的是，Mayhem根据CWE对脆弱点进行了分类：

![https://mmbiz.qpic.cn/mmbiz_jpg/IpYUt4DIvZezicIWVtDzyKJKGYF50S4zmQnfs574OduGlicfMW6yDxIxoibsFhn1DM26sVucqTUibCbbO5nYUXFa7g/640?wx_fmt=jpeg](https://image.3001.net/images/20200220/1582170894_5e4e030e4acac.jpg!small)

![https://mmbiz.qpic.cn/mmbiz_jpg/IpYUt4DIvZezicIWVtDzyKJKGYF50S4zm5TWicEnzPvsnVcicvcR0Ribgcyzribv8k2CXcAQXH9H9fImglq0h75Ryibw/640?wx_fmt=jpeg](https://image.3001.net/images/20200220/1582170901_5e4e03157160b.jpg!small)

查看详细测试结果

我们还可以查看具体测试用例的输入输出，从而精确定位问题（甚至可以看到反汇编后的代码）：

![https://mmbiz.qpic.cn/mmbiz_jpg/IpYUt4DIvZezicIWVtDzyKJKGYF50S4zmTx7T9DNNyIyNSJNhQfa2w6buml3fdhzsI4vk0MMyfcd438Gykej3Vg/640?wx_fmt=jpeg](https://image.3001.net/images/20200220/1582170909_5e4e031de6dc1.jpg!small)

![https://mmbiz.qpic.cn/mmbiz_jpg/IpYUt4DIvZezicIWVtDzyKJKGYF50S4zmLNLctw0nwH1NNZTQt6AyRfh4vq0t2vZ9KekdyvlEAIT2C62RtBC6Rg/640?wx_fmt=jpeg](https://image.3001.net/images/20200220/1582170917_5e4e03256ec2a.jpg!small)

ForAllSecure强调Mayhem的优势之一是零误报。那么如何做到零误报呢？从上面的测试结果我们可以略知一二。Mayhem自动构建的测试用例等效于研究人员手工验证漏洞时编写的PoC。一般来说，如果能够导致程序出现崩溃或其他异常（代码逻辑预期之外的行为），我们便认为PoC是有效的，同时认为漏洞存在。

四、产品特点

持续性深度分析：随着目标程序知识的积累，Mayhem的分析将逐渐深入，代码覆盖率将逐渐提升。

零误报：Mayhem报告的所有缺陷均是准确的（因为它会自动生成PoC去测试）。

自动化生成测试用例：基于团队在卡耐基梅隆大学的专利技术，Mayhem能够利用目标反馈在运行时自动化生成测试用例。

安全左移：在安全开发流程中，Mayhem将动态分析、模糊测试及威胁建模等测试与验证步骤左移，帮助企业控制修复成本。它能够直接插入到CI流水线中，将持续性测试作为DevOps工作流的一部分。

软件供应链管理：Mayhem能够对应用依赖的开源或第三方代码进行威胁评估，以减少软件供应链中存在的风险。

五、总结

在整个调研过程中，绿盟君能够从各路媒体报道和ForAllSecure官方对Mayhem技术原理的概括性描述中感受到其团队拥有的深厚技术积淀。抛开立场不一的媒体，三个事实足够证明他们的雄厚实力：

**1** **、** 公司未立，技术先行：作为一支来自卡耐基梅隆大学的科研团队，其技术的诞生时间比公司成立时间早很多年；

**2** **、** 以绝对优势获得DARPA
CGC决赛第一名：挑战赛**了全球安全领域的顶尖团队，ForAllSecure从104支队伍中脱颖而出进入七强杀入决赛、并获得冠军，这是硬实力的体现；

**3** **、** 获得New Enterprise Associates领投的1500万美元融资：这是资本的评估和认可。

另一方面，ForAllSecure对当前安全测试技术的痛点把握得十分到位。安全从业者往往会有这样的感受：自动化白盒测试（如静态代码分析等）具有不小的误报率；自动化黑盒测试（如漏洞扫描等）既有一定的误报率，同时也有自身的局限性——受限于漏洞知识库；人工渗透测试虽然效果显著，但自动化的缺失导致其无法融入DevOps流程；而传统模糊测试技术的主要玩家通常是职业或半职业的漏洞猎人。

在此形势下，ForAllSecure给出了一个支持DevOps的企业级模糊测试方案，并在一定程度上证明了该方案的有效性（DARPA
CGC），这无疑是令人振奋的。

然而，我们也要提出问题：Mayhem是否真如ForAllSecure描述的那么优秀？他们是否在把握住痛点的同时较好地解决了难点？

![https://mmbiz.qpic.cn/mmbiz_jpg/IpYUt4DIvZezicIWVtDzyKJKGYF50S4zmIcL9URGk2u0eYIqv1mmqcyGf5WWW4Kw7VU6dl2pmyzT6jV1fw3sIlg/640?wx_fmt=jpeg](https://image.3001.net/images/20200220/1582170930_5e4e033292f94.jpg!small)

符号执行和模糊测试本身并不是新技术，人们对两者的优势和缺陷也都早有研究。符号执行技术更多地具有理论上的先进性，但是在应用到复杂程序时往往会遇到路径爆炸等问题；模糊测试的结果则与输入集的数量和质量有着密切的关系。

通过DARPA
CGC，我们看到了Mayhem在漏洞检测和验证上的有效实力，但是我们也注意到，在比赛中Mayhem需要大量的水来进行冷却（CGC决赛为七支队伍配备了180吨水进行水冷）和大规模的算力、能源支持，这些都是前述技术局限性在具体实现上的客观反映。有时候，产品和方案的优秀并不完全由技术上的优势决定。安全行业的特点决定了成本与效果——也就是性价比往往才是最重要的。因此，Mayhem的成本和市场定位也许是需要初创团队考虑的问题，也是客户关心的问题。

滚滚长江东逝水，浪花淘尽英雄。ForAllSecure真的能够推动DevSecOps发展，还是仅仅昙花一现？Mayhem到底是学术界的玩物，还是真的能够成为业界一大杀器？这些都需要时间的检验。然而，就本次创新沙盒竞赛而言，综合考虑技术实力与团队背景，绿盟君认为ForAllSecure具有极强的竞争力，同时看好他们的后续发展。让我们拭目以待。

· 参考文献 ·

[1] Mayhem, the Machine ThatFinds Software Vulnerabilities, Then Patches Them

[2] MIT Technology Review Reveals50 Smartest Companies List in Annual Business
Issue

[3] ForAllSecure

[4] ForAllSecure: About us

[5] DARPA网络超级挑战赛情况及思考

[6] 符号执行技术总结（A Brief Summary of SymbolExecution）- wcventure

注：第3节引用了来自VDALabs的资料Using-Next-Generation-Fuzzing-Tools.pdf；第4节参考了ForAllSecure官方资料FY19 DS Mayhem General v3.7.pdf。

  

