KCon 2018 在经过高质量的闭门培训，以及两天干货议题演讲过后，于8月26日圆满落幕。

一直以来，[KCon](http://kcon.knownsec.com/ "KCon")
都以高质量技术分享闻名，应各位参会者的要求，并通过与演讲者的沟通取得同意后，我们现在将公布18大议题中的14个议题PPT！

![](https://images.seebug.org/content/images/2018/09/2a2fea3e-8d9e-4e62-816a-85850ae32020.jpg-w331s)

### 侠盗猎车 -- 数字钥匙 Hacking

**Kevin2600**  
安全研究员，Team-Trinity 小组成员

汽车安全话题日渐火热，而其中汽车门禁系统的安全性尤为受到关注。传统车辆门禁依赖于 RF 控制模块，但最新 TESLA Model 3
淘汰了传统方式，转而使用通过智能手机进行身份验证和解锁车辆的数字钥匙系统。但特斯拉不是市场上唯一的玩家,
其他主要制造商如沃尔沃和一些小型创业公司也在开发数字钥匙系统。本议题我们将分享针对某款数字钥匙系统的研究成果。与会者不仅可了解此类系统潜在的安全缺陷，还将知道如何绕过汽车安全研究过程中的那些坑。

[【PPT下载】](https://github.com/knownsec/KCon/blob/master/2018/25%E6%97%A5/25%E6%97%A5No.2-KEVIN2600.pdf
"\[ppt下载\]")

* * *

### 智能家居安全——身份劫持

**戴中印**  
百度高级安全工程师

本议题以如何劫持(窃取)智能家居时代设备的身份“安全凭证”为出发点，调研并分析了目前国内市场的主流产品和设备交互协议，及其所依赖身份凭证的安全性，最终通过“身份劫持”，实现设备和产品的任意远程控制。

[【PPT下载】](https://github.com/knownsec/KCon/blob/master/2018/25%E6%97%A5/25%E6%97%A5No.3-%E6%99%BA%E8%83%BD%E5%AE%B6%E5%B1%85%E5%AE%89%E5%85%A8%E8%BA%AB%E4%BB%BD%E5%8A%AB%E6%8C%81-%E6%8C%BD%E7%A7%8B.pdf
"【PPT下载】")

* * *

### 工业网络安全——某款PLC远控实现

**剑思庭**  
复旦大学，软件工程硕士，现任罗克韦尔自动化（中国）有限公司工业安全高级技术顾问

此演讲主要是针对某品牌 PLC 做远程控制，通过对运行的 PLC 做隐藏的控制代码下载到 PLC 内，使 PLC
开启特殊端口，接受外部指令，从而达到可以在工业网络完成 PLC 内网对其他 PLC
的攻击和传染。直接会造成工业基础设施的瘫痪，其危害在于行为十分隐秘，不容易被工控维护人员发现，可以长期控制工业基础设施。

[【PPT下载】](https://github.com/knownsec/KCon/blob/master/2018/25%E6%97%A5/25%E6%97%A5No.4-PLC%E8%BF%9C%E6%8E%A7-%E5%89%91.pdf
"【PPT下载】")

* * *

### BGP安全之殇

**张玉兵**  
360企业安全集团--360威胁情报中心  
高级安全研究员、资深攻防专家、安全攻防研究团队负责人

从2003到2018年，全球出现了数十起由于BGP自身安全缺陷造成的知名重大安全事故。本议题从 BGP
协议基础入手，从攻防角度及当前安全现状由浅入深逐步剖析 BGPv4 协议信任机制(confidence mechanism)、Special-Prefix、AS_PATH、TTL adjustment
等属性存在的安全缺陷引入的安全攻击问题；站在攻击者角度结合现实情况进行BGP路由安全缺陷的利用，现场通过演示环境模拟/视频演示完成
MITM、DOS、DDOS 和攻击痕迹隐藏等技巧。

并以防御者的视角针对以上攻击从多维度用不同的方法进行检测和有效防御进行研究分享。最后，结合近期权威机构暴出的 NSA 监控项目与 BGP
安全问题，深度剖析其千丝万缕的因果关系。希望再次引起国内相关行业对 BGP 有足够的重视和防护改进。

[【PPT下载】](https://github.com/knownsec/KCon/blob/master/2018/25%E6%97%A5/25%E6%97%A5No.5-BGP%E5%AE%89%E5%85%A8%E4%B9%8B%E6%AE%87_%E5%BC%A0%E7%8E%89%E5%85%B5.pdf
"【PPT下载】")

* * *

### 短链接攻击与防御——被忽略的攻击面

**彦修**  
腾讯安全平台部安全工程师

随着微博等新兴媒体的快速发展，短链接开始大面积应用到互联网的各个领域之中。据不完全统计，使用了第三方或自身提供的短链接服务的厂商占到了80%。但是另一方面，短链接的安全问题却一直被用户和厂商所忽视。本议题主要从攻击者角度入手，系统介绍短链接应用的常见算法、利用场景，攻击手法等，并且列举有短连接业务的互联网企业的实际安全问题，理论联系实际为企业的短连接业务提出行之有效的防御方法。

[【PPT下载】](https://github.com/knownsec/KCon/blob/master/2018/25%E6%97%A5/25%E6%97%A5NO.6-%E7%9F%AD%E7%BD%91%E5%9D%80%E7%9A%84%E6%94%BB%E5%87%BB%E4%B8%8E%E9%98%B2%E5%BE%A1-%E5%BD%A6%E4%BF%AE.pdf
"【PPT下载】")

* * *

### 识“黑”寻踪之内存取证

**伍智波**  
现就职于中国网安集团旗下的广州三零卫士信息安全有限公司，任信息安全专家，且主要负责为广州市公安局网警支队的网络犯罪案件技术分析工作

本议题将主要讲述在 Windows 下的易失性内存RAM的取证分析。不仅有内存取证技术起源于发展、Windows
的三大内存管理机制、不同环境下的内存取证方法、Volatility
内存分析框架的使用方法，更有通过真实的犯罪侦查案例（将会脱敏），介绍如何安全获取犯罪现场的内存样本，再利用内存取证技术对取得的内存样本进行分析，获得如网络连接记录、进程表记录、注册表信息、命令执行记录等可能有助于破案的电子证据信息，继而进行各类电子证据的交叉分析，尽可能还原出犯罪情景。

[【PPT下载】](https://github.com/knownsec/KCon/blob/master/2018/25%E6%97%A5/25%E6%97%A5NO.7-%E8%AF%86%E9%BB%91%E5%AF%BB%E8%B8%AA%E4%B9%8B%E5%86%85%E5%AD%98%E5%8F%96%E8%AF%81-%E4%BC%8D%E6%99%BA%E6%B3%A2-ok.pdf
"【PPT下载】")

* * *

### 射频攻击—从键盘钩子木马到无线键鼠套装劫持

**石冰**  
本科信息安全专业大三在读，数学与信息安全爱好者，cisp-pte 注册渗透测试工程师，owasp 中国分会项目研究小组研究员，看雪安全、i春秋平台安全讲师

键盘是用户在使用计算机过程中重要的输入工具，如果键盘一旦被攻击者监听或控制，那么个人隐私很大程度上也就暴露在了攻击者的视野当中。本议题将展示如何利用射频攻击来进行无线键鼠的监听、劫持来完成用户信息的嗅探，以及对传统和新时代下针对键盘攻击的思路和技巧进行进一步的分析，并在最后给出一些可行的应对方案和措施。

[【PPT下载】](https://github.com/knownsec/KCon/tree/master/2018/25%E6%97%A5/25%E6%97%A5No.8-%E7%9F%B3%E5%86%B0
"【PPT下载】")

* * *

### Chakra 引擎的非 JIT 漏洞与利用

**宋凯**  
Kai Song (@exp-sky)腾讯安全玄武实验室高级安全研究员

我们赢得2017年 Pwn2Own 比赛，赛场上包括我们的多支参赛队伍都使用了 Chakra JIT
相关的漏洞。所以近年来脚本引擎的JIT相关的漏洞引起了大家的广泛关注。但这并不代表 Chakra
脚本引擎中其它的逻辑就是安全的。我会在这次议题中详细介绍一个 Chakra
脚本引擎，非JIT相关的漏洞，以及这个漏洞利用的详细过程。在最开始写这个漏洞利用的时候，曾一度认为其是不可用的，最后通过组合多种技巧，成功实现在 Edge
浏览器中的任意代码执行。

[【PPT下载】](https://github.com/knownsec/KCon/blob/master/2018/26%E6%97%A5/26%E6%97%A5No.1-Chakra%E5%BC%95%E6%93%8E%E7%9A%84%E9%9D%9EJIT%E6%BC%8F%E6%B4%9E%E4%B8%8E%E5%88%A9%E7%94%A8-%E5%AE%8B%E5%87%AF.pdf
"【PPT下载】")

* * *

### WASM双刃剑——机制剖析与逆向

**赵光远**  
绿盟科技安全研究员

WebAssembly（WASM）是一种专为浏览器设计的新技术。它旨在定义一种可移植，大小和加载时间有效的二进制格式，作为编译目标，可以通过利用通用硬件编译为以本机速度执行
可在各种平台上使用，包括移动和物联网。

在我们演讲中，我们将介绍 WebAssembly 的实现机制，运行机制，以及使用场景。与此同时，我们以使用 WASM
编写的挖矿木马为例，来详细介绍应该如何对这类样本进行分析。

[【PPT下载】](https://github.com/knownsec/KCon/blob/master/2018/26%E6%97%A5/26%E6%97%A5No.2-WASM-%E8%B5%B5%E5%85%89%E8%BF%9C.pdf
"【PPT下载】")

* * *

### Attacking Kerberos

**n1nty@360 A-TEAM**  
360 企业安全集团安全研究员

Kerberos, Windows 域环境下默认的身份验证协议。本次议题带你全面走进 Kerberos 的三种子协议以及针对这三种子协议的攻击手法。

[【PPT下载】](https://github.com/knownsec/KCon/blob/master/2018/26%E6%97%A5/26%E6%97%A5No.4-Attacking%20Kerberos-n1nty.pdf
"【PPT下载】")

* * *

### 动态审计Python代码

**聂心明**  
n0tr00t 团队成员，亚信安全开发工程师

利用 python 语言的特性，hook python
中危险的函数，把进入到危险函数中的关键参数打印到日志中，利用fuzzing的方法，帮助代码审计人员能快速发现 python
程序中诸如命令执行，sqli，xss 等漏洞，从而提高代码审计效率。

[【PPT下载】](https://github.com/knownsec/KCon/blob/master/2018/26%E6%97%A5/26%E6%97%A5No.5-python%E5%8A%A8%E6%80%81%E4%BB%A3%E7%A0%81%E5%AE%A1%E8%AE%A1-%E8%81%82%E5%BF%83%E6%98%8E.pdf
"【PPT下载】")

* * *

### Hacking you without password

**泳少@YongShao**  
Mobike Security Team，安全工程师，网络尖刀成员。曾为苹果、微软、美团等国内外厂商提交过多个安全漏洞。

本议题主要以 Oauth2.0协议提及多个厂商开发不严，导致身份凭证易让攻击者获得，且讲解如何实现拿到凭证后进行登陆他人账户。以及在即使做了白名单限制后
bypass 的方法和一些修复建议。

本提议中将会介绍 Jetbrains team work 0day
及国内外存在风险的厂商，希望通过本议题能够推动该协议避免的问题。同时还会以某博客某个设计缺陷导致双向登陆等一系列问题为实例。

[【PPT下载】](https://github.com/knownsec/KCon/blob/master/2018/26%E6%97%A5/26%E6%97%A5No.7-Hacking%20You%20Without%20Password-%E6%B3%B3%E5%B0%91.pdf
"【PPT下载】")

* * *

### 智能合约开发中的安全SDLC实践

**Pavlo Radchuk**  
Hacken 应用安全工程师

演讲涉及安全 SDLC 实践在智能合约开发中的适用性。

比起大约5000万行代码的 windows 来说，可以用100行代码组成的智能合约的规模要小得多。然而，比起一个 PC 来说，1个 ICO
智能合约风险要高得多。

智能合约变得越来越复杂，我们肯定有些合同可以通过安全 SDLC 的一些实践使合同更安全并将风险降至最低。

[【PPT下载】](https://github.com/knownsec/KCon/blob/master/2018/26%E6%97%A5/26%E6%97%A5No.8-Secure%20SDLC%20Practices%20in%20Smart%20Contracts%20Development%20-Palvo.pdf
"【PPT下载】")

* * *

### PDF JS 引擎交互式 Fuzzing

**Swan@0x557**  
Palo Alto Networks Distinguished Engineer

**Heige@0x557**  
Knownsec 404 Team Leader

PDF 文件格式及相关漏洞一直以来就是安全研究的热点。最近一段时间，我们通过改进五年前的一套 fuzz 框架，结合新颖的自动化测试策略，也发现了一大批
Adobe Reader
的安全问题。在这个议题里，我们将与大家分享相关研究思路的由来和实现机制，并详细介绍如何将交互元素引入测试中，自动化寻找那些常人难以发现的漏洞。

[【PPT下载】](https://github.com/knownsec/KCon/blob/master/2018/26%E6%97%A5/26%E6%97%A5No.10-PDF%20%20JS%E5%BC%95%E6%93%8E%E4%BA%A4%E4%BA%92%E5%BC%8FFuzzing-%E9%BB%91%E5%93%A5%26swan.pdf
"【PPT下载】")

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/697/>

