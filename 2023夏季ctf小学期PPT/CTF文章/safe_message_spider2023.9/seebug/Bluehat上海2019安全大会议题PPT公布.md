在过去的十五年间，微软安全应急响应中心（MSRC）在微软北美总部和以色列举办了多届 BlueHat 安全大会。2019年5月29-30日，[BlueHat
安全大会](https://www.microsoft.com/china/bluehatshanghai/2019/#Agenda "BlueHat
安全大会")在上海召开，其目的是希望可以为中国的安全专家和白帽子带来最精彩和最前沿的技术干货以及创造一个有趣的技术交流环境。此次 BlueHat
安全大会主要是面向中国以及亚太地区的白帽子、安全工程师和安全从业者，是一个专注于漏洞挖掘、响应与防护的安全大会。

  

# 5月29日

  

## Welcome to BlueHat Shanghai

演讲嘉宾：Eric Doerr@Microsoft Security Response Center

2019 年，中国的安全研究员是微软漏洞赏金计划中成果最多，影响力最大的贡献者。来自中国的安全研究人员和合作公司已经证明了自己的技术实力，帮助我们一起在
2019 年保护广大的用户和整个安全生态圈。MSRC对安全的投入历史悠久，且在新版 Windows
中获得了回报。微软的未来将更加数字化，我们的主攻方向是Github 和 微软云 Azure。无论现在亦或未来，在这段旅途上我们需要与所有的合作伙伴一起前行。

议题PPT下载：[中文版](https://images.seebug.org/archive/BlueHat_Shanghai_Keynote-CN.pdf "中文版") &
[英文版](https://images.seebug.org/archive/BlueHat_Shanghai_Keynote-EN.pdf "英文版")

  

## China Cyber Landscape 2018

演讲嘉宾：Yunqian Zhu@CNCERT

通过对多种数据资源的分析，该简报结合全球趋势和事件背景，回顾2018年中国网络安全形势。我们为中国网络空间中发现的主要威胁提供可操作的见解，例如网站损毁、网站钓鱼、恶意软件、漏洞利用等。通过对中国的案例分析，我们为减少网络攻击提供深刻的见解和实践经验。最后，我们将在2019年保持这种趋势。

  

## Liar Game: The Secret of Mitigation Bypass Techniques

演讲嘉宾：Yunhai Zhang@NSFOCUS

在过去的五年中，我们开发了十几种缓解旁路技术，其中大多数都赢得了微软的赏金。那么，这些技术的发展是否有任何共性？是否仍然可以以相同的方式开发更多的缓解旁路技术？未来我们能避免这种情况发生吗？在本次演讲中，我们对这些缓解旁路技术的发展进行回顾，并解释在该过程中使用的策略，总结出其背后的方法。在此基础上，给出一些开发建议，帮助提高系统的安全性。

  

## Advances in Machine Learning at Microsoft Threat Protection

演讲嘉宾：Christian Seifert@Microsoft

在今天，没有机器学习的安全解决方案是不可想象的。在本次演讲中，我们分享了如何在Windows
Defender中应用机器学习。我们对构成模型基础的数据，平台和功能进行讨论，然后深入了解选择的ML模型。本次演讲不仅仅是描述传统的分类系统，而是深入探讨高级主题，例如构建语言模型，异常模型和对抗性防御。

  

## Is my Container Secure? - Large-Scale Empirical Study on Container
Vulnerabilities

演讲嘉宾：Cecilia Hu & Yue Guan@Palo Alto Networks

容器作为一种轻量级虚拟化技术，使企业能够自动化Web应用程序部署的许多方面。Docker作为最受欢迎的容器实现之一，已被广泛用于DevOps实践中。当DevOps团队通过发出简单命令（例如docker
pull /
push）来部署Docker镜像时，人们自然会开始质疑：我可以安全部署下载的镜像吗？它有什么关键的漏洞吗？如果我的运行容器中存在漏洞，我该如何解决？在本次演讲中，我们试图通过回顾Docker镜像中发现的漏洞来回答这些问题，我们对公共Docker库的容器镜像进行了大规模的实证研究。我们的数据集包括40,000多个单独的镜像，并且我们通过多个数据源（如开源镜像扫描仪和在线镜像分析仪）收集单个镜像的漏洞信息。通过分析从这些镜像中发现的8,000多个独特的漏洞，我们发现了有趣的漏洞演变趋势。我们还提供了关于这些趋势的解释，并预测了它们未来的变化。最后，结合我们自己的漏洞数据库，我们希望对这些漏洞提供一些重要的见解。本次演讲还精心讨论以下问题，如：我们能否在我们的容器设置中利用这些漏洞？如何精准地确定这些漏洞的优先级？

议题PPT下载：[中文版](https://images.seebug.org/archive/Large-Scale_Empirical_Study_on_Container_Vulnerabilities-CN.pdf "中文版") &
[英文版](https://images.seebug.org/archive/Large-Scale_Empirical_Study_on_Container_Vulnerabilities-EN.pdf "英文版")

  

## Advanced Lateral Movement on Kubernetes Cluster

Zhaoyan Xu@Palo Alto Networks

谷歌的Kubernetes(又名k8s)已经成为软件容器编排的标杆，如何保护Kubernetes成为安全社区的一个开放性问题。但是，目前对此进行全面的研究。诸如“k8s漏洞的影响有多大?”，“正确且安全地配置系统有多难?”或者“有什么工具可以帮助我吗?”等问题是DevOps团队最常见的。为了克服这些挑战，我们从安全角度对k8s编排进行了系统研究。我们简要而全面地介绍了现有的k8s漏洞，以及我们新发现的漏洞，以便让人们对k8s安全有一个深入而广泛的认识。然后，我们专注于新的研究，以显示攻击者如何在云原生容器系统中发起攻击，而不是关注单个漏洞利用。此外，我们重点介绍了攻击者如何在容器环境中执行横向移动，并分析在漏洞和配置错误的编排器的情况下，如何执行此类攻击。更重要的是，我们演示了我们的K8s安全工具，alk8s，它不仅可以检测脆弱的K8s服务器上的漏洞，还可以检测针对错误配置的编排器的异常网络输入。它利用机器学习和规范性的检测策略的组合来分析编排器行为。

议题PPT下载：[中文版](https://images.seebug.org/archive/Advanced_Lateral_Movement_on_Kubernetes_Cluster-CN.pdf "中文版") &
[英文版](https://images.seebug.org/archive/Advanced_Lateral_Movement_on_Kubernetes_Cluster-EN.pdf "英文版")

  

## Enhance Security Awareness with Data Mining: Data-driven Intrusion
Detection Solutions in Alibaba Cloud

演讲嘉宾：Yue Xu & Han Zheng@Alibaba Cloud

今天，随着机器学习的不断突破，越来越多的公司开始在各种安全解决方案中应用机器学习。但是，这些工作要么专注于提出新算法，要么只是发现新的应用场景。很少有人谈到少量的学术成果与各种云应用之间的差距。在本次演讲中，我们首先展示了云安全意识的挑战，特别是应用层面的威胁。在此基础上，我们提出了几种基于数据挖掘技术的最先进的入侵检测解决方案，如暴力破解、异常进程启动、恶意脚本、Web攻击等。现在所有的解决方案都在为阿里云服务，每天都会向我们的客户发出成千上万的入侵警报。最后，我们讨论了何时以及如何使用数据挖掘技术来增强安全意识并给出我们的建议。

议题PPT下载：[中文版](https://images.seebug.org/archive/Data-driven_Intrusion_Detection_Solutions_in_Alibaba_Cloud-CN.pdf "中文版") &
[英文版](https://images.seebug.org/archive/Data-driven_Intrusion_Detection_Solutions_in_Alibaba_Cloud-EN.pdf "英文版")

  

## From Dvr to See Exploit of IoT Device

演讲嘉宾：Fan Wu@Qihoo 360

近年来，物联网设备的安全日益受到人们的关注。我们的日常工作是在物联网设备上找到不安全因素，因此有机会在会议上介绍数字视频存储的基本利用。我们从审核Web端口和固件本身的安全性开始，通过重新打包固件而获得的调试端口找到堆栈溢出。最后，我们根据漏洞背景来去除监视器，并通过调整后的arm
shellcode来getshell。我们希望您能学习关于物联网设备利用的知识，并与我们一起解决未来可能遇到的挑战。

议题PPT下载：[中文版](https://images.seebug.org/archive/From_Dvr_to_See_Exploit_of_IoT_Device-CN.pdf "中文版") &
[英文版](https://images.seebug.org/archive/From_Dvr_to_See_Exploit_of_IoT_Device-EN.pdf "英文版")

  

## Betrayal of Reputation: Trusting the Untrustable Hardware and Software with
Reputation

演讲嘉宾：Seunghun Han@National Security Research Institute of South Korea

人们往往会直接信任体量大、信誉高的公司所提供的软硬件，但信誉良好的产品真的值得信赖吗？在本次演讲中，我介绍了一些硬件和软件，尤其是BIOS /
UEFI固件、英特尔可信执行技术（TXT）和可信平台模块（TPM）的情况，这些都辜负了您的信任。信誉良好的公司定义并实施规范，具有UEFI /
BIOS固件和英特尔TXT的TPM已被广泛使用并成为人们信任的根源。我发现了两个与休眠过程相关的漏洞：CVE-2017-16837和CVE-2018-6622。与以前的研究不同，这些漏洞可以在没有物理访问的情况下破坏TPM。为了减少这些漏洞，我还介绍了一些对策和一个工具Napper来进行检测。休眠过程是漏洞的一个重要组成部分，所以Napper会让您的系统短暂地进入休眠状态并检查它们。

议题PPT下载：[中文版](https://images.seebug.org/archive/Trusting_the_Untrustable_Hardware_and_Software_with_Reputation-CN.pdf "中文版") &
[英文版](https://images.seebug.org/archive/Trusting_the_Untrustable_Hardware_and_Software_with_Reputation-EN.pdf.pdf "英文版")

  

## MesaTEE SGX: Redefining AI and Big Data Analysis with Intel SGX

演讲嘉宾：Yu Ding@Baidu X-Lab

Intel SGX旨在保护用户隐私和私钥，而SGX 飞地的简单缓冲区溢出将泄露这些宝贵的数据或密钥，并导致数十亿美元的损失。内存损坏是Intel SGX
飞地的第一个敌人。我们需要一个完整的解决方案来构建内存安全的Intel SGX飞地。在本次演讲中，我们介绍了MesaTEE SGX 软件栈。MesaTEE
SGX
软件栈提供了用Rust/RPython编写的内存安全库，并提供了一些有用的内存安全库，比如序列化器/反序列化器、TLS终止、更多的加密原语、快速的ML库、WASM解释器，甚至还有一个内存安全的pypy解释器。开发人员可以使用这些库轻松地开发Intel
SGX应用程序，并通过几个简单的步骤将更多的Rust /
Python库移植到飞地中。我们在SGX软件设计和实现中遇到了大量陷阱，并在本次演讲中分享了它们。这些陷阱通常与可信/不可信输入和分区方法/哲学有关。他们之前没有提出相应的解决方案，我相信我们的故事应该是“目前已知的最佳实践”。详细地说，我们讨论了“混合内存安全性经验法则”的理念，以及面向安全的标准库设计，基于认证的TLS，安全快速的解释器或
ML 实现等。我们坚信，通过Intel SGX和一种新颖的面向安全的软件设计和实现，本次讲话使Bluehat受众受益匪浅。

议题PPT下载：[中文版](https://images.seebug.org/archive/Redefining_AI_and_Big_Data_Analysis_with_Intel_SGX-CN.pdf "中文版") &
[英文版](https://images.seebug.org/archive/Redefining_AI_and_Big_Data_Analysis_with_Intel_SGX-EN.pdf "英文版")

  

# 5月30日

  

## Advancing Windows Security

演讲嘉宾:David Weston@Microsoft

Windows的安全性正在不断增强，平台功能正在快速变化。为了更好地应对新式攻击，Windows
也在快速变革。我们的的目标在于跨越不断成长的威胁模型并提供更强大的保障。欢迎研究人员和社区帮我们继续完善。漏洞赏金和征集缓解措施的项目非常重要。我们希望与中国及更多地区的研究人员群体共同努力，更好地了解当前和未来的攻击。

议题PPT下载:[中文版](https://images.seebug.org/archive/Advancing_Windows_Security-CN.pdf "中文版") &
[英文版](https://images.seebug.org/archive/Advancing_Windows_Security-EN.pdf
"英文版")

  

## Exploring the Maze of Memory Layouts Towards Exploits

演讲嘉宾：Yan Wang & Chao Zhang@Chinese Academy of Sciences & Tsinghua University

漏洞利用生成的障碍之一是内存布局操作。大量的内存损坏漏洞（例如，堆溢出和UAF）只能在特定的内存布局中被利用。在实践中，它需要人力来操纵内存布局。因此，自动内存布局操作是一个有趣的主题，它可以为自动利用生成(AEG)铺平道路。在这次演讲中，我们介绍了我们的解决方案Maze，它能够将PoC样本的不可利用内存布局转换为可利用的布局，并在可能的情况下自动生成各种可用的漏洞。首先，它应用程序分析技术来识别代码片段（表示为内存操作原语），这些代码片段可以执行内存（de）分配操作，并且可以根据需要进行重新输入和调用。然后，它应用一种新的算法Dig
&
Fill，按一定的顺序调用这些内存操作原语来精确地操作内存布局。我们实现了一个基于二进制分析引擎S2E的Maze原型，并在一组带有堆溢出和UAF漏洞的CTF（捕获标志）程序上对其进行了评估。实验结果表明，Maze可以将30个PoC样本的内存布局转换为可利用状态，并成功生成大多数PoC样本的漏洞利用样本。

  

## Needle in A Haystack: Catch Multiple Zero-Days Using Sandbox

演讲嘉宾：Qi Li & Quan Jin@Qihoo 360

在过去几年中，我们一直在开发沙箱检测技术，以探索如何使用沙箱来检测和过滤样本，并发现高级威胁。在此过程中，我们继续改进自动分析平台，并在过去两年中发现了多个零日漏洞。在本次演讲中，我们介绍了我们的沙箱平台，并描述如何从头开始构建Office零日检测系统，并最终捕获多个与Office相关的零日漏洞。我们还分享了我们在Windows内核和其他漏洞检测中的做法，以及如何使用沙箱自动过滤特殊样本。

议题PPT下载：[中文版](https://images.seebug.org/archive/Catch_Multiple_Zero-Days_Using_Sandbox-CN.pdf "中文版") &
[英文版](https://images.seebug.org/archive/Catch_Multiple_Zero-Days_Using_Sandbox-EN.pdf "英文版")

  

## How to Find Twelve Kernel Information Disclosure Vulnerabilities in Three
Months

演讲嘉宾：Tanghui Chen@Baidu,Inc

本次演讲分享了一种轻量级、高效的内核信息泄露漏洞的检测方法。有两种方法在业界取得了显著的成果，一种是Mateusz
Jurczyk的BochsPwn，来自Google Project
Zero，另一种是潘剑锋的DigTool。BochsPwn使用CPU指令模拟技术，其性能非常差。DigToolcai采用重量级VT技术。在深入研究内核信息泄露漏洞后，我们发现其本质是内核将一些未初始化的数据复制到用户模式的内存中，导致信息泄露。另外，我们在Windows内核中积累了大量技术。在找出漏洞的原因后，我们提出了一种检测漏洞的新方法。该方法由许多不同的技术实现，如内核nirvana和hook，可以快速检测内核信息泄漏。在过去的三个月中，已经发现了12个Windows内核信息泄露漏洞，这证明了这种方法非常有效。

议题PPT下载：
[中文版](https://images.seebug.org/archive/How_to_Find_Twelve_Kernel_Information_Disclosure_Vulnerabilities_in_Three_Months-CN.pdf "中文版") &
[英文版](https://images.seebug.org/archive/How_to_Find_Twelve_Kernel_Information_Disclosure_Vulnerabilities_in_Three_Months-EN.pdf "英文版")

  

## Momigari: Overview of the Latest Windows OS Kernel Exploits Found in the
Wild

演讲嘉宾：Boris Larin & Anton Ivanov@Kaspersky Lab

Momigari（红叶狩猎）是日本人在秋天寻找最美丽的树叶的传统。在2018年秋季仅仅一个月的时间里，我们发现了一些针对Microsoft
Windows操作系统的零日攻击。其中两个针对最新且完全更新的Windows 10 RS4，在此之前，Windows 10
RS4还没有已知的内存损坏漏洞。我们还发现了一些漏洞，这些漏洞在安全更新时无意中得到了修复，但在此之前很长一段时间内都没有补丁。这些研究结果表明，漏洞利用编写者将继续寻找可靠地利用不稳定漏洞的新方法，并绕过最安全的操作系统的现代缓解技术。其中最有趣的是，大多数漏洞都是相互关联的。这表明他们背后的策划者并不害怕一次浪费大量的零日漏洞，因为他们的军火库已经满了。在本次演示中，我们研究了多个在野特权提升（EOP）零日漏洞，并揭示了这些漏洞采用的开发框架。这个框架可以带有多个漏洞利用程序（嵌入或从远程资源接收）。每个漏洞利用都提供了可执行内核shellcode的接口。在本次演示中，我们分享以下内容：
\- 深入分析用于零日漏洞利用开发的框架 \- 深入分析攻击者使用的漏洞 \- 用于绕过漏洞利用缓解机制的有趣技术。

议题PPT下载：[中文版](https://images.seebug.org/archive/Overview_of_the_Latest_Windows_OS_Kernel_Exploits_Found_in_the_Wild-CN.pdf "中文版") &
[英文版](https://images.seebug.org/archive/Overview_of_the_Latest_Windows_OS_Kernel_Exploits_Found_in_the_Wild-EN.pdf "英文版")

  

## New and Effective Methods to Probe Vulnerabilities in Hardware Devices

演讲嘉宾：Shupeng Gao@Baidu,Inc

我们如何才能更有效地探测智能设备的漏洞？虽然智能设备在品牌，外观和功能上有所不同，但它们都具有类似的结构：CPU \ memory \ storage \
input \
output，因此我们可以应用类似的方法来分析和发现它们的漏洞。在本次演讲中，我们展示了几种新的有效漏洞探测技术和工具，包括：使用编程器和焊接设备读写闪存芯片，如SPI闪存/
NAND闪存/ EMMC和EMCP（超过95％的智能设备使用这三种）；获取root shell的各种方法，包括修改U-boot内核参数，通过CPU数据表确定串口以及在线和离线编辑flash；介绍各种网络连接的嗅探和编辑方法，包括WiFi实时解密，挂机模式和GPRS中间人攻击。然后，我们展示了如何组合这些方法，并最终发现控制设备中的高风险漏洞。这些技术非常有效。在过去的三年里，他们帮助我们在中国赢得了六次硬件设备破解比赛(Geekpwn,
Xpwn)。最后，我们提出了有效提高硬件设备安全性的想法和建议。

议题PPT下载：[中文版](https://images.seebug.org/archive/New_and_Effective_Methods_to_Probe_Vulnerabilities_in_Hardware_Devices-CN.pdf "中文版") &
[英文版](https://images.seebug.org/archive/New_and_Effective_Methods_to_Probe_Vulnerabilities_in_Hardware_Devices-EN.pdf "英文版")

  

## Browser Script Engine Zero Days in 2018

演讲嘉宾：Elliot Cao@Trend Micro

浏览器是进入互联网世界的窗口，脚本使其更加丰富多彩。因为大多数脚本语言都是动态的、弱类型的，并且不需要考虑内存管理，所以人们可以轻松地开发浏览器应用程序。这一切都归功于脚本引擎。但复杂的脚本引擎似乎很脆弱。2018年，我们看到了一些基于这些脚本引擎（例如Flash，VBScript和JScript）的在野零日攻击。本次演讲包含以下内容：首先，我们对2018年的浏览器脚本引擎漏洞进行快速的回顾，主要是在野零日漏洞攻击。其次，介绍我们自主开发的工具VBSEmulator，它可以对vbs混淆的样本进行反混淆处理，并检测GodMode或ROP。最后，快速浏览用于Microsoft
Edge的JavaScript引擎Chakra，并解释如何在Chakra中进行利用。

议题PPT下载：
[中文版](https://images.seebug.org/archive/Browser_Script_Engine_Zero_Days_in_2018-CN.pdf
"中文版") &
[英文版](https://images.seebug.org/archive/Browser_Script_Engine_Zero_Days_in_2018-EN.pdf
"英文版")

  

## Fighting Malicious Insider Threat with User Profile Based Anomaly Detection

演讲嘉宾：Lei He@Microsoft

心怀不满的恶意内部人员仍然是Microsoft和Office 365的主要威胁之一。成千上万的员工和供应商全天候运营Office
365服务;心怀不满的员工或受损的凭证可能导致未经授权的数据访问和盗窃，且渗透测试人员经常对O365模拟这些威胁。虽然基于渗透测试的监督学习涵盖了已知的模式，但苏州的M365安全团队开发了一种近乎实时的异常检测来覆盖未知的威胁。该模型基于操作员历史活动数据中心概况，在运用了多种实用技术进行细化的情况下，其精度达到了90%。

议题PPT下载： [中文版
](https://images.seebug.org/archive/Fighting_Malicious_Insider_Threat_with_User_Profile_Based_Anomaly_Detection-CN.pdf "中文版 ")&
[英文版](https://images.seebug.org/archive/Fighting_Malicious_Insider_Threat_with_User_Profile_Based_Anomaly_Detection-EN.pdf "英文版")

  

## Discovering Vulnerabilities with Data-Flow Sensitive Fuzzing

演讲嘉宾：Shuitao Gan & Chao Zhang@State Key Laboratory of Mathematical Engineering
and Advanced Computing & Tsinghua University

我们认为数据流对于探索复杂的代码（例如，校验和和幻数检查）以及发现漏洞非常有用。在本次演讲中，我们介绍了基于数据流控制的fuzzer工具GreyOne。首先，它利用数据流的经典特征——污点——来指导模糊测试，例如，确定要修改的字节以及如何修改。然后，它使用数据流的新特性——约束一致性——来调整模糊的演化方向，例如，有效地满足未触及分支的约束。为了支持这些数据流特性，我们提出了一种轻量级且可靠的模糊驱动污点推断(FTI)来推测变量的污点。评估结果表明，GreyOne在代码覆盖率和漏洞发现方面都优于各种先进的fuzzer(包括AFL、Honggfuzz、VUzzer和CollAFL)。其总共发现了105个新的安全漏洞，其中41个被CVE确认。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/950/>

