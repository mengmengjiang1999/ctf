**作者：riusksk  
原文链接：<https://mp.weixin.qq.com/s/c494rGETcdoMe0Udi7kLQg>**

注：本文由ChatGPT与Claude联合生成

#### 总结

根据上述的USENIX Security' 23会议接受的论文,可以总结出以下几个方面:

一、攻击与防御研究占比较大比重,大约有30篇论文涉及系统、网络和机器学习模型的各类攻击与防御。包括侧信道攻击、模糊测试技术、认证和授权攻击、隐私攻击与防御等。攻击与防御仍然是重要的研究方向。

二、自动化技术也是重点研究内容,大约有25篇论文提出各种自动化技术来发现漏洞、生成测试用例、分析协议等。包括模糊测试、静态/动态分析、机器学习等。自动化技术变得越来越重要来应对系统复杂性的不断增长。

三、隐私与透明度也成为重点,大约有15篇论文探讨提升隐私的技术、用户研究以了解隐私观念、物联网设备的透明度、数据最小化等。这反映出人们对用户数据安全性和隐私的持续关注。

四、机器学习安全也是活跃的研究方向,有大约12 篇论文讨论面向机器学习模型的攻击与防御,包括对抗示例、公平性、解释性等。
总的来说，自动化技术、攻击与防御以及隐私相关的研究仍然是该会议最活跃的方面。展望未来，预测物联网、边缘计算、区块链、5G等新兴技术的安全将变得更加重要。隐私和安全性方面的可用户性也将继续受到关注。总的来说，对安全可信任的系统的需求将推动网络安全研究的创新和进步。

对于高校与企业的安全研究人员而言，推荐选择具有市场需求和前景光明的研究方向,同时贴近实际问题,以加快研究进度和成果转化。

#### 1、Improving Logging to Reduce Permission Over-Granting Mistakes

Bingyu Shen, UC San Diego; Tianyi Shan, University of California San Diego;
Yuanyuan Zhou, UC San Diego
为了阻止对敏感数据的非法访问，访问控制配置是一个重要的门卫。然而，系统管理员有时会在解决合法用户报告的意外访问拒绝问题时过度授予权限，这可能为攻击者打开安全漏洞。主要原因之一是现代软件没有提供信息丰富的日志记录，以指导系统管理员了解报告的问题。

本文尝试（据我们所知）第一次帮助开发人员改进日志消息，以帮助系统管理员正确理解和修复访问拒绝问题，而不会过度授予权限。首先，我们进行了观察研究，以了解服务器软件中访问拒绝日志记录的当前实践。我们的研究表明，许多访问控制程序位置没有任何日志消息；现有日志消息的很大一部分缺乏有用的信息，无法指导系统管理员正确理解和解决问题。在我们的观察基础上，我们构建了SECLOG，使用静态分析技术自动帮助开发人员找到缺失的访问拒绝日志位置，并识别日志位置的相关信息。

我们对十个广泛部署的服务器应用程序进行了SECLOG评估。总体而言，SECLOG识别出380个新的访问拒绝日志记录，并提供了550个现有访问拒绝日志消息的诊断信息。我们向这些应用程序的开发人员报告了114个日志记录，到目前为止，其中70个已被他们的主分支接受。我们还对32名系统管理员进行了用户研究，针对6个真实的访问拒绝问题。SECLOG可以将不安全的修复次数从27次减少到1次，并将诊断时间平均缩短了64.2%。

#### 2、V-Cloak: Intelligibility-, Naturalness- & Timbre-Preserving Real-Time
Voice Anonymization

Jiangyi Deng, Fei Teng, and Yanjiao Chen, Zhejiang University; Xiaofu Chen and
Zhaohui Wang, Wuhan University; Wenyuan Xu, Zhejiang University

即时通讯或社交媒体应用程序生成的语音数据包含独特的用户语音特征，可能被恶意对手滥用以进行身份推断或身份盗窃。现有的语音匿名化技术，例如信号处理和语音转换/合成，会导致感知质量降低。在本文中，我们开发了一个名为V-Cloak的语音匿名化系统，可以在保持音频的可理解性、自然性和音色的情况下实现实时语音匿名化。我们设计的匿名化器具有单次生成模型，可以在不同频率级别上调制原始音频的特征。我们使用精心设计的损失函数训练匿名化器。除了匿名损失外，我们还进一步结合了可理解性损失和基于心理听觉的自然度损失。匿名化器可以实现非指向性和指向性匿名化，以实现不可识别性和不可关联性的匿名目标。

我们在四个数据集上进行了广泛实验，即LibriSpeech（英语）、AISHELL（中文）、CommonVoice（法语）和CommonVoice（意大利语），五个自动说话人验证（ASV）系统（包括两个基于深度神经网络的、两个统计学的和一个商业ASV），以及十一个自动语音识别（ASR）系统（针对不同的语言）。实验结果证实，V-Cloak在匿名性能方面优于五个基线。我们还展示了仅在VoxCeleb1数据集上针对ECAPA-TDNN ASV和DeepSpeech2 ASR训练的V-Cloak对其他ASV具有可转移的匿名性和对其他ASR的跨语言可理解性。此外，我们验证了V-Cloak对各种去噪技术和自适应攻击的鲁棒性。希望V-Cloak可以为我们在五颜六色的世界中提供一层保护。

#### 3、PatchVerif: Discovering Faulty Patches in Robotic Vehicles

Hyungsub Kim, Muslum Ozgur Ozmen, Z. Berkay Celik, Antonio Bianchi, and
Dongyan Xu, Purdue University

现代软件经常会进行补丁修复以解决漏洞和安全问题。在机器人车辆（RVs）中，补丁非常重要，因为安全和安全漏洞可能会导致严重的物理损害。然而，由于现有自动化方法无法系统地确定引入的行为修改如何影响RV与物理环境的交互，因此现有自动化方法很难确定RV中的故障补丁。
在本文中，我们介绍了PATCHVERIF，这是一个自动化补丁分析框架。PATCHVERIF的目标是评估给定补丁是否在已修复的RV控制软件中引入了漏洞。为此，PATCHVERIF使用静态和动态分析的组合来衡量分析的补丁如何影响RV的物理状态。具体而言，PATCHVERIF使用专门的输入突变算法来生成RV输入，最大化原始代码和修补后代码之间在物理空间中的行为，PATCHVERIF使用专门的输入突变算法来生成RV输入，最大化原始代码和修补后代码之间在物理空间中的行为差异。利用收集到的关于补丁引入的行为修改的信息，PATCHVERIF使用支持向量机（SVM）来推断补丁是否有故障或正确。

我们在两个流行的RV控制软件（ArduPilot和PX4）上对PATCHVERIF进行了评估，它成功地识别出了故障补丁，平均精度和召回率分别为97.9％和92.1％。此外，PATCHVERIF发现了115个以前未知的漏洞，其中103个已被确认，其中51个已经得到了修复。

#### 4、DISTDET: A Cost-Effective Distributed Cyber Threat Detection System

Feng Dong, School of Cyber Science and Engineering, Huazhong University of
Science and Technology / Sangfor Technologies Inc.; Liu Wang and Xu Nie,
Beijing University of Posts and Telecommunications; Fei Shao, Case Western
Reserve University; Haoyu Wang, School of Cyber Science and Engineering,
Huazhong University of Science and Technology; Ding Li, Key Laboratory of
High-Confidence Software Technologies (MOE), School of Computer Science,
Peking University; Xiapu Luo, The Hong Kong Polytechnic University; Xusheng
Xiao, Arizona State University

构建考虑软件行为之间因果关系的溯源图可以更好地提供关于网络攻击的上下文信息，特别是对于高级攻击，如高级持续性威胁（APT）攻击。尽管在协助攻击调查方面具有很大的潜力，但现有使用溯源图进行攻击检测的方法存在两个根本性限制。第一，现有方法采用集中式检测架构，将所有系统审计日志发送到服务器进行处理，导致数据传输、数据存储和计算成本难以承受。第二，他们采用基于规则的技术，无法检测未知威胁，或者采用产生大量虚警的异常检测技术，在APT检测中无法实现精确度和召回率的平衡。为了解决这些根本性挑战，我们提出了DISTDET，一个分布式检测系统，通过以下方式检测APT攻击：（1）在客户端构建主机模型，执行轻量级检测；（2）基于警报属性的语义过滤虚警；（3）补充主机模型的本地偏差，推导全局模型。我们在大规模工业环境（1,130个主机，14天，约1.6亿个事件）和DARPA
TC数据集上的实验表明，DISTDET可以像现有技术一样有效地检测攻击，同时将网络带宽从11.28Mb/s降低到17.08Kb/S（减少了676.5倍），内存使用量从364MB降低到5.523MB（减少了66倍），存储从1.47GB降低到130.34MB（减少了11.6倍）。截至撰写本文时，DISTDET已在50多个工业客户中部署了超过6个月，覆盖了22,000多个主机，并识别出了900多个真实的攻击。

#### 5、The Impostor Among US(B): Off-Path Injection Attacks on USB
Communications

Robert Dumitru, The University of Adelaide and Defence Science and Technology
Group; Daniel Genkin, Georgia Tech; Andrew Wabnitz, Defence Science and
Technology Group; Yuval Yarom, The University of Adelaide

USB是现代计算机系统中最普遍的外围接口，其固有的不安全性使其成为一个吸引人的攻击向量。USB的一个众所周知的限制是流量未加密。这使得路径上的对手可以轻松地执行中间人攻击。已经显示了可能攻击机密通信的离线攻击。然而，到目前为止，还没有展示出违反USB通信完整性的离线攻击。

在这项工作中，我们展示了即使对于离线攻击者，USB通信的完整性也不能保证。具体来说，我们设计并构建了恶意设备，即使放置在受害者设备和主机之间的路径之外，也可以向该路径注入数据。使用我们开发的注入器，我们可以伪造由主机计算机系统解释的数据输入的来源。通过代表受信任的受害者设备进行注入，我们可以规避计算机系统针对常见USB攻击采用的任何基于软件的授权策略防御。我们展示了两种具体攻击。第一种注入按键，允许攻击者执行命令。第二种演示文件内容替换，包括从USB磁盘进行系统安装期间的内容替换。我们在29个USB
2.0和USB 3.x集线器上测试了这些攻击，并发现其中14个易受攻击。

#### 6、Fuzztruction: Using Fault Injection-based Fuzzing to Leverage Implicit
Domain Knowledge

Nils Bars, Moritz Schloegel, Tobias Scharnowski, and Nico Schiller, Ruhr-Universit?t Bochum; Thorsten Holz, CISPA Helmholtz Center for Information
Security

今天的数字通信依赖于用于交换结构化消息和数据的复杂协议和规范。通信自然涉及两个端点：一个产生数据，一个消费数据。传统的模糊测试方法将一个端点，也就是生成器，替换为模糊器，并快速在测试的目标程序上测试许多变异的输入。虽然这种完全自动化的方法对于松散结构的格式效果很好，但对于高度结构化的格式（特别是经过压缩或加密等复杂转换的格式）则不适用。

在这项工作中，我们提出了一种新的观点，在高度复杂的格式中生成输入，而不依赖于重量级程序分析技术、粗粒度语法近似或人类领域专家。我们不是对目标程序的输入进行变异，而是向数据生成程序注入故障，使得这些数据几乎符合预期的格式。这样的数据可以绕过消费者程序的初始解析阶段，并激发更有趣的程序行为，从而测试更深层次的程序状态。为了实现这个概念，我们提出了一组编译时和运行时分析，以有针对性地变异生成器，使其保持完整，并产生满足复杂格式约束的半有效输出。我们在一个名为Fuzztruction的原型中实现了这种方法，并展示它优于现有的模糊器AFL++、SYMCC和WEIZZ。Fuzztruction比现有方法找到了更多的覆盖范围，特别是在使用加密原语的目标上。在我们的评估过程中，Fuzztruction发现了151个唯一的崩溃（经过自动去重后）。到目前为止，我们手动处理并报告了27个错误，并分配了4个CVE编号。

#### 7、NVLeak: Off-Chip Side-Channel Attacks via Non-Volatile Memory Systems

Zixuan Wang, UC San Diego; Mohammadkazem Taram, Purdue University and UC San
Diego; Daniel Moghimi, UT Austin and UC San Diego; Steven Swanson, Dean
Tullsen, and Jishen Zhao, UC San Diego

在这项研究中，我们研究了非易失性RAM（NVRAM）DIMM上的微架构侧信道攻击和防御。在这项研究中，我们首先对Intel Optane
DIMM实现的NVRAM进行反向工程，并揭示了其以前未记录的微架构细节：DIMM上的缓存结构（NVCache）和磨损平衡策略。基于这些发现，我们首先开发了跨核心和跨VM的隐蔽通道，以建立这些共享硬件资源的通道容量。然后，我们在NVLeak的框架下设计了基于NVCache的侧信道攻击。我们将NVLeak应用于一系列攻击案例研究，包括攻击支持NVRAM的数据库和键值存储的隐私，并在将NVRAM用作易失性运行时内存时监视代码页面的执行路径。我们的结果表明，利用NVRAM的侧信道攻击是实际可行的，并且可以打败以前提出的仅关注芯片硬件资源的防御方法。为了填补这种防御的差距，我们开发了基于缓存分区的系统级缓解措施，以防止从NVCache泄漏的侧信道泄漏。

#### 8、A Research Framework and Initial Study of Browser Security for the
Visually Impaired

Elaine Lau and Zachary Peterson, Cal Poly, San Luis Obispo

基于Web的恶意软件和网络钓鱼攻击的增长促进了在浏览器加载可疑网站内容之前使用插页警告页面和模态框的研究和应用方面的重大进展。这些警告通常使用视觉提示来吸引用户的注意力，包括专门的图标、颜色以及按钮的位置和大小，以传达情境的重要性。虽然视觉技术的功效已经提高了有视力的用户的安全性，但这些技术并不适合盲人和视力受损的用户。我们认为这不是由于浏览器制造商缺乏兴趣或技术能力，而是由于缺乏研究文献来指导他们的选择，加上缺乏明确的方法来对这个人群进行研究。事实上，挑战是多方面的。在本文中，我们分析和解决了使用视力受损人群进行安全和隐私研究的方法论挑战，并提出了一组新的方法论最佳实践，适用于进行这种类型的研究。使用我们的方法论，我们进行了一项初步研究，分析了视力受损人群在浏览器安全警告方面的体验，进行主题分析，识别了视力受损用户经常遇到的共同挑战，并提出了一些初步的解决方案，以改善这个人群的安全性。

#### 9、PUMM: Preventing Use-After-Free Using Execution Unit Partitioning

Carter Yagemann, The Ohio State University; Simon P. Chung, Brendan
Saltaformaggio, and Wenke Lee, Georgia Institute of Technology

关键软件是用易受内存错误攻击的非内存安全语言编写的，例如use-after-free和double
free错误。这导致提出了通过策略性地推迟内存重新分配来保护内存分配器，使得此类错误无法被利用。然而，现有的解决方案存在高运行时和内存开销。为了寻求更好的解决方案，我们提出了对程序进行分析，以识别与单个任务处理相对应的代码单元。根据这样一个直觉，在运行时应该很少或几乎没有数据在不同的任务之间流动，因此，被当前执行单元释放的内存的重新分配被推迟到其完成之后；只需要足够长的时间来防止use-after-free攻击。

为了展示我们设计的有效性，我们为Linux实现了一个原型PUMM，它由一个离线分析器和一个在线执行器组成，通过透明地包装标准库来保护C/C++二进制文件。在我们对40个真实世界和3,000个合成漏洞进行的26个程序的评估中，包括Chakra
JavaScript引擎等复杂的多线程案例，PUMM成功阻止了所有真实世界的攻击，并只允许4个合成攻击，同时将内存开销降低了52.0%，平均运行时开销为2.04%。

#### 10、POLICYCOMP: Counterpart Comparison of Privacy Policies Uncovers
Overbroad Personal Data Collection Practices

Lu Zhou, Xidian University and Shanghai Jiao Tong University; Chengyongxiao
Wei, Tong Zhu, and Guoxing Chen, Shanghai Jiao Tong University; Xiaokuan
Zhang, George Mason University; Suguo Du, Hui Cao, and Haojin Zhu, Shanghai
Jiao Tong University

由于移动应用的隐私政策通常很复杂，因此开发了各种工具来检查隐私政策是否存在矛盾，并验证隐私政策是否与应用的行为一致。然而，据我们所知，以前的工作并没有回答一个问题，即应用程序隐私政策中的个人数据收集做法（PDCPs）是否针对特定目的是必要的（即是否符合数据最小化原则）。尽管大多数现有隐私法规/法律（如GDPR）都对数据最小化原则进行了定义，但该原则已被转化为不同的隐私做法，具体取决于不同的上下文（例如，各种开发人员和目标用户）。最终，只要开发人员获得了用户的授权，他们就可以收集隐私政策中所声称的个人数据。

目前，主要依赖于法律专家根据特定上下文手动审核个人数据收集的必要性，这对于数百万应用程序来说并不可扩展。在这项研究中，我们旨在从对等比较的角度自动调查应用程序隐私政策中的PDCPs是否过于宽泛。我们的基本见解是，如果一个应用程序在其隐私政策中声称收集的个人数据比大多数同类应用程序多得多，那么它更有可能进行过于宽泛的收集。为了实现这一目标，我们提出了一个自动检测过于宽泛的PDCPs的框架POLICYCOMP。我们使用POLICYCOMP对10,042个隐私政策进行了大规模分析，并标记了48.29%的PDCPs为过于宽泛。我们向2,000个应用程序开发人员分享了我们的发现，并收到了52个回复，其中39个承认了我们的发现并采取了行动（例如删除过于宽泛的PDCPs）。

#### 11、The Maginot Line: Attacking the Boundary of DNS Caching Protection

Xiang Li, Chaoyi Lu, and Baojun Liu, Tsinghua University; Qifan Zhang and Zhou
Li, University of California, Irvine; Haixin Duan, Tsinghua University, QI-ANXIN Technology Research Institute, and Zhongguancun Laboratory; Qi Li,
Tsinghua University and Zhongguancun Laboratory

很抱歉，这篇论文目前正在禁止发布期间，将在研讨会的第一天公布。

在这篇论文中，我们报告了MaginotDNS，一种针对同时充当转发器和递归解析器（称为CDNS）的DNS服务器的强大缓存污染攻击。通过利用自上世纪90年代以来DNS安全的基石之一——边界检查算法中的漏洞，该攻击成为可能，并影响了包括BIND和Microsoft
DNS在内的多个流行DNS软件的多个版本。通过现场测试，我们发现该攻击非常有效，允许攻击者接管整个DNS区域，甚至包括顶级域（例如.com和.net）。通过大规模的测量研究，我们还确认了CDNS在实际网络中的广泛使用（在我们探测到的开放DNS服务器中高达41.8%），并发现至少35.5%的所有CDNS都容易受到MaginotDNS的攻击。在与ISP的访谈之后，我们展示了各种CDNS使用案例和实际攻击。我们已经向DNS软件供应商报告了所有发现的漏洞并收到了所有供应商的确认。已分配了3个CVE-id，并有2个供应商修复了其软件。我们的研究引起了人们对不同DNS软件和服务器模式（即递归解析器和转发器）中安全检查逻辑实现不一致的关注，并呼吁软件供应商进行标准化和协议。

#### 12、One Server for the Price of Two: Simple and Fast Single-Server Private
Information Retrieval

Alexandra Henzinger, Matthew M. Hong, and Henry Corrigan-Gibbs, MIT; Sarah
Meiklejohn, Google; Vinod Vaikuntanathan, MIT

SimplePIR是已知最快的单服务器私人信息检索方案。SimplePIR的安全性基于学习与错误假设。为了回答客户端的查询，SimplePIR服务器每个数据库字节执行不到一个32位乘法和一个32位加法。SimplePIR实现了每个核心10
GB/s的服务器吞吐量，这接近于机器的内存带宽和最快的需要非合谋服务器的两个服务器私人信息检索方案的性能。在查询一个1
GB的数据库时，SimplePIR的通信成本相对较高：客户端必须下载一个约121
MB的关于数据库内容的“提示”；此后，客户端可以进行无限次查询，每次查询需要242
KB的通信。我们还提出了第二种单服务器方案DoublePIR，将提示缩小到16 MB，但每次查询的通信成本略高（345 KB），吞吐量略低（7.4
GB/s/core）。最后，我们将我们的新私人信息检索方案与一种近似集合成员关系的新型数据结构结合起来，应用于证书透明度的私人审计任务。我们实现了比Google
Chrome当前方法更加严格的隐私保护，通信量增加了13倍：每周下载16 MB，以及每个TLS连接1.5 KB。

#### 13、Exploring User Reactions and Mental Models Towards Perceptual
Manipulation Attacks in Mixed Reality

Kaiming Cheng, Jeffery F. Tian, Tadayoshi Kohno, and Franziska Roesner,
University of Washington

感知操纵攻击（PMA）涉及通过混合现实（MR）内容操纵用户对世界的多感官（例如视觉、听觉、触觉）感知，以影响用户的判断和后续行动。例如，一个预计显示安全关键输出的MR驾驶应用程序也可能（恶意或无意地）在交通标志上叠加错误的信号，误导用户急刹车。虽然目前的MR技术足以创建这样的攻击，但很少有研究来了解用户如何感知、反应和防御这种潜在的操纵。为了为理解和解决MR中的PMA提供基础，我们进行了一项21名参与者的现场研究。我们开发了三种PMA，分别针对三种不同的感知进行攻击：视觉、听觉和情境感知。我们的研究首先通过评估参与者在基准和不同攻击条件下的“微基准”任务表现来调查用户反应如何受到影响。我们观察到攻击的一级和二级影响，后者甚至在非攻击条件下也会影响参与者的表现。我们随后进行了访谈，总结了参与者对PMA的各种反应和解释。通过对我们观察和访谈的定性数据分析，我们识别出了参与者开发的各种防御策略，并观察到这些策略有时会适得其反。根据我们的发现，我们提出了未来调查和防御方向的建议。

#### 14、Eavesdropping Mobile App Activity via Radio-Frequency Energy
Harvesting

Tao Ni, Shenzhen Research Institute, City University of Hong Kong, and
Department of Computer Science, City University of Hong Kong; Guohao Lan,
Department of Software Technology, Delft University of Technology; Jia Wang,
College of Computer Science and Software Engineering, Shenzhen University;
Qingchuan Zhao, Department of Computer Science, City University of Hong Kong;
Weitao Xu, Shenzhen Research Institute, City University of Hong Kong, and
Department of Computer Science, City University of Hong Kong

无线电频率（RF）能量收集是一项有前途的技术，可用于为物联网（IoT）设备提供电源，以驱动传感器并延长电池寿命。在本文中，我们提出了一种新颖的侧信道攻击，利用RF能量收集信号窃听移动应用程序的活动。为了演示这种新型攻击，我们提出了AppListener，一种自动化攻击框架，可以从收集的RF能量中识别出细粒度的移动应用程序活动。RF能量是从自定义的RF能量收集器中收集的，该收集器从环境Wi-Fi传输中生成电压信号，而应用程序活动则是从三级分类算法中识别出来的。我们使用四个移动设备运行40个常见的移动应用程序（例如YouTube、Facebook和WhatsApp），这些应用程序属于五个类别（即视频、音乐、社交媒体、通信和游戏），每个类别都包含五个应用程序特定的活动。实验结果表明，AppListener可以在区分四个不同移动设备方面达到超过99％的准确性，在分类40个不同应用程序方面达到超过98％的准确性，在识别五组应用程序特定活动方面达到86.7％的准确性。此外，我们进行了全面的研究，表明AppListener对于多个影响因素具有鲁棒性，例如距离、环境和非目标连接设备。将AppListener集成到商业IoT设备中的实践表明，它易于部署。最后，我们提出了对抗措施作为防御这种新型攻击的第一步。

#### 15、Side-Channel Attacks on Optane Persistent Memory

Sihang Liu, University of Virginia; Suraaj Kanniwadi, Cornell University;
Martin Schwarzl, Andreas Kogler, and Daniel Gruss, Graz University of
Technology; Samira Khan, University of Virginia

在云环境中，技术的不断发展包括新型存储技术的开发，例如持久性存储器。新发布的英特尔Optane持久性存储器为数据中心中的存储类应用程序提供高性能、持久性和字节寻址访问，而Optane的直接数据管理速度快且高效，但不清楚它是否存在不良的安全影响。这是有问题的，因为云租户在同一硬件上物理共存。

在本文中，我们首次对英特尔Optane持久性存储器进行了侧信道安全分析。我们对Optane存储器的内部缓存层次结构、缓存大小、关联性、替换策略和磨损平衡机制进行了逆向工程。基于这种逆向工程，我们构建了四种针对Optane内部组件的新攻击原语。然后，我们通过这些攻击原语提供了四个案例研究。首先，我们基于Optane的内部缓存提供本地隐蔽通道。其次，我们通过英特尔的Optane优化键值存储pmemkv演示了一种远程用户的按键侧信道攻击。第三，我们通过pmemkv研究了一种完全远程的隐蔽通道。第四，我们通过pmemkv提出了我们的Note
Board攻击，使两个参与者可以在服务器的长时间间隔和甚至电源周期内隐蔽地存储和交换消息。最后，我们讨论了对抗我们攻击的缓解措施。

#### 16、A Study of Multi-Factor and Risk-Based Authentication Availability

Anthony Gavazzi, Ryan Williams, Engin Kirda, and Long Lu, Northeastern
University; Andre King, Andy Davis, and Tim Leek, MIT Lincoln Laboratory

尽管密码验证（PBA）存在长期已知的不安全性，但它仍然是Web上最流行的用户验证形式。考虑到PBA的缺陷，许多在线服务支持多因素认证（MFA）和/或基于风险的认证（RBA）以更好地保护用户帐户。MFA和RBA的安全性、可用性和实现已经得到了广泛的研究，但是尝试测量它们在流行的Web服务中的可用性缺乏广度。此外，没有研究分析MFA和RBA的普及程度以及单点登录（SSO）提供程序的存在如何影响Web上MFA和RBA的可用性。

在本文中，我们对Tranco前5K中支持帐户创建的208个流行网站进行了研究，以了解Web上MFA和RBA的可用性，可用于MFA和RBA的其他身份验证因素以及通过更安全的SSO提供程序登录网站如何改变用户身份验证安全的情况。我们发现，只有42.31％的网站支持任何形式的MFA，只有22.12％的网站阻止明显的账户劫持尝试。尽管大多数网站不提供MFA或RBA，但SSO完全改变了情况。如果一个人通过支持MFA和/或RBA的SSO提供程序在每个网站上创建帐户（如果有），则80.29％的网站将可以访问MFA，72.60％的网站将阻止明显的账户劫持尝试。但是，通过SSO的这种扩散会带来隐私权妥协，因为几乎所有支持MFA和RBA的SSO提供程序都是主要第三方跟踪器。

#### 17、Person Re-identification in 3D Space: A WiFi Vision-based Approach

Yili Ren and Yichao Wang, Florida State University; Sheng Tan, Trinity
University; Yingying Chen, Rutgers University; Jie Yang, Florida State
University

人员再识别（Re-ID）在支持广泛的安全应用方面越来越重要。传统的人员再识别主要依赖于基于光学摄像头的系统，由于人们外观的变化、遮挡和人体姿势的变化而产生了几个限制。在这项工作中，我们提出了一种基于WiFi视觉的系统3D-ID，用于在3D空间中进行人员再识别。我们的系统利用WiFi和深度学习的进步，帮助WiFi设备“看到”人，识别和识别人。特别地，我们利用下一代WiFi设备上的多个天线和信号反射的2D
AoA估计来使WiFi能够在物理环境中可视化人。然后，我们利用深度学习将人的可视化数字化为3D身体表示，并提取静态身体形状和动态步行模式，用于人员再识别。我们在各种室内环境下进行的评估结果表明，3D-ID系统的总体排名1准确率为85.3％。结果还表明，我们的系统对各种攻击具有抵抗力。因此，所提出的3D-ID非常有前途，因为它可以增强或补充基于摄像头的系统。

#### 18、Fourteen Years in the Life: A Root Server’s Perspective on DNS
Resolver Security

Alden Hilton, Sandia National Laboratories; Casey Deccio, Brigham Young
University; Jacob Davis, Sandia National Laboratories

我们考虑DNS安全和隐私情况随时间的演变，使用在2008年至2021年间在A-root收集的数据。我们考虑诸如安全和隐私机制的部署，包括源端口随机化、TXID随机化、DNSSEC和QNAME最小化等。我们发现，实现新的安全实践的普遍采用是一个缓慢而持续的过程。特别值得注意的是，我们发现大量的解析器几乎缺乏我们考虑的所有安全机制，即使到2021年仍然如此。具体而言，在2021年，超过4％的解析器未受源端口随机化、DNSSEC验证、DNS
cookie或0x20编码的保护。令人振奋的是，我们发现具有安全实践的解析器的流量量明显高于其他解析器。

#### 19、ClepsydraCache -- Preventing Cache Attacks with Time-Based Evictions

Jan Philipp Thoma, Ruhr University Bochum; Christian Niesler, University of
Duisburg-Essen; Dominic Funke, Gregor Leander, Pierre Mayr, and Nils Pohl,
Ruhr University Bochum; Lucas Davi, University of Duisburg-Essen; Tim Güneysu,
Ruhr University Bochum & DFKI

在最近的过去，我们目睹了向微架构CPU级别的攻击的转变。特别是缓存侧信道攻击在其中扮演了主导角色，因为它们允许攻击者利用CPU微架构来窃取机密信息。这些微妙的攻击利用了冲突缓存地址的架构可见性。在本文中，我们提出了ClepsydraCache，它使用缓存衰减和索引随机化的新组合来缓解最先进的缓存攻击。每个缓存条目都与一个生存时间（TTL）值相关联。我们提出了一种新的TTL动态调度机制，它在防止这些攻击的同时保持性能起着基本作用。ClepsydraCache有效地保护免受最新的缓存攻击，如Prime+（Prune+）Probe。我们在gem5中展示了一个完整的原型，并提出了一个TTL机制的概念验证硬件设计，证明了在现实世界系统中部署ClepsydraCache的可行性。

#### 20、Guarding Serverless Applications with Kalium

Deepak Sirone Jegan, University of Wisconsin-Madison; Liang Wang, Princeton
University; Siddhant Bhagat, Microsoft; Michael Swift, University of
Wisconsin-Madison

随着一种新兴的应用范式，无服务器计算吸引了越来越多攻击者的注意。不幸的是，传统Web应用程序的安全工具不能轻易地移植到无服务器计算中，由于其分布式特性，现有的无服务器安全解决方案专注于强制执行用户指定的信息流策略，无法检测应用程序控制流路径中函数顺序的操纵。在本文中，我们提出了Kalium，一个可扩展的安全框架，利用本地函数状态和全局应用程序状态来强制执行无服务器应用程序中的控制流完整性（CFI）。我们使用现实的开源应用程序评估了Kalium的性能开销和安全性。结果表明，Kalium可以缓解多个攻击类别，具有相对较低的性能开销，并优于最先进的无服务器信息流保护系统。

#### 21、DynSQL: Stateful Fuzzing for Database Management Systems with Complex
and Valid SQL Query Generation

Zu-Ming Jiang, ETH Zurich; Jia-Ju Bai, Tsinghua University; Zhendong Su, ETH
Zurich

数据库管理系统（DBMS）是现代软件的重要组成部分。为确保DBMS的安全性，最近的方法是通过自动生成SQL查询来自动测试DBMS。然而，现有的DBMS模糊器在生成复杂和有效的查询方面受到限制，因为它们严重依赖于预定义的语法模型和关于DBMS的固定知识，但未捕获DBMS特定状态信息。因此，这些方法错过了许多DBMS中的深层次漏洞。

在本文中，我们提出了一种新颖的有状态模糊测试方法，以有效地测试DBMS并发现深层次漏洞。我们的基本思想是，在DBMS处理每个SQL语句之后，有用的状态信息可以被动态收集，以便后续查询生成。基于这个想法，我们的方法执行动态查询交互，使用捕获的状态信息逐步生成复杂和有效的SQL查询。为了进一步提高生成查询的有效性，我们的方法使用查询处理的错误状态来过滤无效的测试用例。我们将我们的方法实现为一个完全自动化的模糊测试框架DynSQL。DynSQL在6个广泛使用的DBMS（包括SQLite、MySQL、MariaDB、PostgreSQL、MonetDB和ClickHouse）上进行评估，并发现了40个独特的漏洞。其中38个已经得到确认，21个已经修复，19个已经分配了CVE
ID。在我们的评估中，DynSQL的性能优于其他最先进的DBMS模糊器，实现了41％的更高代码覆盖率，并找到了其他模糊器错过的许多漏洞。

#### 22、Automated Security Analysis of Exposure Notification Systems

Kevin Morio and Ilkan Esiyok, CISPA Helmholtz Center for Information Security;
Dennis Jackson, Mozilla; Robert Künnemann, CISPA Helmholtz Center for
Information Security

我们首次对两种最广泛部署的接触者通知系统ROBERT和Google和Apple Exposure
Notification（GAEN）框架的安全性进行了正式的分析和比较。

ROBERT是集中式接触者通知方法中最受欢迎的安装，其中风险评分由中央服务器计算。相比之下，GAEN采用分散式方法，其中用户的手机计算风险。集中式和分散式系统的相对优点已被证明是一个有争议的问题。以前的大部分分析都集中在这些系统的隐私影响上，我们的研究是第一个正式评估已部署系统的安全性-误报风险的缺失。

我们对ROBERT的法国部署和最广泛部署的GAEN变体-德国的Corona-Warn-App进行了建模。我们确定了这些系统防止误报的确切条件。我们确定了对手如何通过网络和蓝牙嗅探、数据库泄露或手机、后端系统和卫生机构的妥协来破坏系统。我们还调查了DP3T协议原始规范的安全性，以确定拟议方案与最终部署之间的差距。

我们发现了总共27种攻击模式，包括许多区分集中式和分散式方法的攻击，以及区分所有三种协议的授权过程攻击。我们的研究结果表明，ROBERT的集中式设计更容易受到试图执行大规模通知攻击的机会主义和高资源攻击者的攻击。

#### 23、xNIDS: Explaining Deep Learning-based Network Intrusion Detection
Systems for Active Intrusion Responses

Feng Wei, University at Buffalo; Hongda Li, Palo Alto Networks; Ziming Zhao
and Hongxin Hu, University at Buffalo

最近，基于深度学习的网络入侵检测系统（DL-NIDS）得到了广泛探索，并显示出卓越的性能，但由于其检测结果与可行的解释之间存在语义差距，它们无法积极响应检测到的入侵。此外，它们的高错误成本使网络运营商不愿仅基于其检测结果做出响应。这些缺点的根本原因可以追溯到DL-NIDS的可解释性不足。虽然已经开发出一些用于解释基于深度学习的系统的方法，但它们无法处理结构化数据的历史输入和复杂特征依赖关系，并且在解释DL-NIDS方面表现不佳。

本文介绍了XNIDS，一种新颖的框架，通过解释DL-NIDS来促进主动入侵响应。我们的解释方法突出了以下特点：（1）对历史输入进行逼近和采样；（2）捕捉结构化数据的特征依赖关系，以实现高保真度的解释。基于解释结果，XNIDS可以进一步生成可行的防御规则。我们使用四种最先进的DL-NIDS对XNIDS进行评估。我们的评估结果表明，XNIDS在保真度、稀疏性、完整性和稳定性方面优于以前的解释方法，这些都对主动入侵响应非常重要。此外，我们证明XNIDS可以高效地生成实用的防御规则，帮助理解DL-NIDS的行为并排除检测错误。

#### 24、Pspray: Timing Side-Channel based Linux Kernel Heap Exploitation
Technique

Yoochan Lee and Jinhan Kwak, Seoul National University; Junesoo Kang and
Yuseok Jeon, UNIST; Byoungyoung Lee, Seoul National University

攻击的隐蔽性对于攻击者而言是最关键的考虑因素，因为这样可以在不被检测到的情况下达到他们的目标。因此，攻击者会花费大量精力来提高攻击的成功率，以免因失败而暴露攻击者和攻击尝试的信息。内核漏洞是攻击者的主要目标，通常利用基于堆的漏洞，而这些漏洞的成功率通常较低（例如平均为56.1%），这是由于默认Linux内核堆分配器SLUB的工作原理所致。

本文介绍了一种基于时序侧信道攻击的利用技术——Pspray，它可以显著提高利用成功的概率。根据我们的评估，使用10个现实世界的漏洞，Pspray显著提高了所有这些漏洞的成功率（例如平均从56.1%提高到97.92%）。为了防止攻击者滥用这种利用技术，我们进一步引入了一种新的防御机制来缓解Pspray的威胁。在应用缓解措施后，Pspray的总体成功率变得与使用Pspray之前相似，而且性能开销（0.25%）和内存开销（0.52%）几乎可以忽略不计。

#### 25、Strategies and Vulnerabilities of Participants in Venezuelan Influence
Operations

Ruben Recabarren, Bogdan Carbunar, Nestor Hernandez, and Ashfaq Ali Shafin,
Florida International University

在线影响力行动的研究，即协调努力传播和放大虚假信息的行动，通常关注社交网络或公开可用的恶意账户数据集的法证分析。然而，我们对影响力行动中人类参与者的经验和挑战了解甚少。我们对19名参与塑造委内瑞拉在线形象的影响力行动参与者进行了半结构化访谈，以了解他们的动机、能力和策略，以在规避检测的同时推广内容。为了验证他们部分答案的准确性，我们利用他们控制的Twitter账户收集了近四个月的数据进行量化调查。

我们发现了各种不同的参与者，包括亲政府和反对派支持者、代理人和基层活动家、假人账户所有者和真实用户。尽管亲政府和反对派参与者具有相似的目标和推广策略，但他们在动机、组织、对手和检测规避策略上存在差异。我们报道了Patria框架，这是一个政府平台，供代理人记录活动并获得福利。我们系统化了参与者推广政治内容和规避和恢复Twitter惩罚的策略，并确定了与这些策略相关的漏洞点，并提出了更为精细的防御措施来对抗影响力行动。

#### 26、Investigating Verification Behavior and Perceptions of Visual Digital
Certificates

Da?iel Gerhardt and Alexander Ponticello, CISPA Helmholtz Center for
Information Security and Saarland University; Adrian Dabrowski and Katharina
Krombholz, CISPA Helmholtz Center for Information Security

本文介绍了一项定性研究，探讨个人如何理解和验证具有QR码的视觉数字证书。在COVID-19大流行期间，欧盟使用这些证书提供标准化的疫苗接种证明。

我们对17名负责验证COVID-19证书的参与者进行了半结构化访谈。使用双重主题分析方法，我们确定并分类了多种行为模式，包括不足的依赖视觉线索作为正确数字验证的代理方法。

我们根据研究结果提出了设计和结构建议，包括概念变更和改进存储和验证应用程序，以限制捷径机会。我们的实证研究结果对于提高视觉数字证书及其验证的可用性、鲁棒性和有效性至关重要。

#### 27、Remote Attacks on Speech Recognition Systems Using Sound from Power
Supply

Lanqing Yang, Xinqi Chen, Xiangyong Jian, Leping Yang, Yijie Li, Qianfei Ren,
Yi-Chao Chen, and Guangtao Xue, Shanghai Jiao Tong University; Xiaoyu Ji,
Zhejiang University

语音识别（SR）系统用于智能手机和扬声器中进行查询、撰写电子邮件和发起电话。但是，它们也带来了严重的安全风险。研究人员已经证明，引入某些声音可以威胁到SR系统的安全。然而，大多数这些方法需要攻击者靠近受害者的短距离，从而限制了这些方案的适用性。其他研究人员使用外围设备（例如激光）远程攻击SR系统；然而，这些方法需要视线范围内的始终开启的扬声器并接近受害者。据我们所知，本文提出的SingAttack方案是第一个使用受害者设备的开关模式电源中生成的类人声音来操纵SR系统的方案。攻击信号通过电网传输，可以对现有的SR系统进行长距离攻击。所提出的SingAttack系统不依赖于外部硬件或关于设备访问的不切实际的假设。在对十个SR系统进行实验时，SingAttack在距离23米处发起攻击，实现了7.8的Mel-Cepstral畸变。

#### 28、HOMESPY: The Invisible Sniffer of Infrared Remote Control of Smart TVs

Kong Huang, YuTong Zhou, and Ke Zhang, The Chinese University of Hong Kong;
Jiacen Xu, University of California, Irvine; Jiongyi Chen, National University
of Defense Technology; Di Tang, Indiana University Bloomington; Kehuan Zhang,
The Chinese University of Hong Kong

红外（IR）遥控是一种广泛应用于家庭的技术，由于其简单性和低成本而被广泛使用。由于在家庭中使用的视线范围内，大多数人认为它是“安全的”。本文重新审视了IR遥控方案的安全性，并在互联网连接的智能家居环境下检查它们的安全假设。我们关注两个特定的问题：（1）是否可以通过物联网设备嗅探IR信号；（2）通过嗅探到的IR控制信号可以泄露哪些信息。

为了回答这些问题，我们设计了一个嗅探模块，使用一款商用的树莓派上的IR接收器，并展示了智能电视遥控器发出的红外（IR）信号可以被附近的物联网设备（例如智能空调）捕获，即使信号并没有瞄准空调。IR信号的范围和接收角度比大多数人想象的要大。我们还开发了算法来从嗅探到的IR控制信号中提取语义信息，并进行了真实世界应用的评估。结果表明，许多敏感信息都可以通过嗅探到的IR控制信号泄露出去，包括账户名和密码、PIN码，甚至是支付信息。

#### 29、FuzzJIT: Oracle-Enhanced Fuzzing for JavaScript Engine JIT Compiler

Junjie Wang, College of Intelligence and Computing, Tianjin University; Zhiyi
Zhang, CodeSafe Team, Qi An Xin Group Corp.; Shuang Liu, College of
Intelligence and Computing, Tianjin University; Xiaoning Du, Monash
University; Junjie Chen, College of Intelligence and Computing, Tianjin
University

我们提出了一种新的模糊测试技术FuzzJIT，用于暴露JavaScript引擎中JIT编译器的漏洞。我们的洞察力是，JIT编译器只应该加速执行，而不应该改变JavaScript代码的执行结果。FuzzJIT可以为每个测试用例激活JIT编译器，并敏锐地捕捉由JIT编译器引起的任何执行差异。成功的关键在于设计一个输入包装模板，它可以主动激活JIT编译器，并使生成的样本自身具有oracle感知性，oracle在执行过程中自发地进行测试。我们还设计了一组变异策略，以强调在揭示JIT编译器漏洞方面有前途的程序元素。FuzzJIT深入到JIT编译器中，同时保留了模糊测试的高效性。我们已经实现了这个设计，并将原型应用于发现四个主流JavaScript引擎中的新的JIT编译器漏洞。在一个月的时间里，分别在JavaScriptCore、V8、SpiderMonkey和ChakraCore中发现了10、5、2和16个新漏洞，其中三个可以被利用。

#### 30、TPatch: A Triggered Physical Adversarial Patch

Wenjun Zhu and Xiaoyu Ji, USSLAB, Zhejiang University; Yushi Cheng, BNRist,
Tsinghua University; Shibo Zhang and Wenyuan Xu, USSLAB, Zhejiang University

自动驾驶车辆越来越多地利用基于视觉的感知模块获取有关行驶环境和障碍物的信息。正确的检测和分类对于确保安全的驾驶决策非常重要。现有的研究已经证明，使用印刷的对抗性补丁可以欺骗感知模型，如物体检测器和图像分类器。然而，大多数这些攻击方法是对每个经过的自动驾驶车辆都进行攻击，缺乏针对性。本文提出了TPatch，一种由声音信号触发的物理对抗性补丁。与其他对抗性补丁不同，TPatch在正常情况下保持良性，但可以通过信号注入攻击引入的设计失真来触发隐藏、创建或更改攻击。为了避免引起人类驾驶员的怀疑，并使攻击在现实世界中实际且具有鲁棒性，我们提出了基于内容的伪装方法和攻击鲁棒性增强方法来加强攻击。我们对三个物体检测器（YOLO
V3/V5和Faster
R-CNN）和八个图像分类器进行了评估，证明了TPatch在模拟和实际世界中的有效性。我们还讨论了可能的传感器、算法和系统级别的防御方法。

#### 31、TAP: Transparent and Privacy-Preserving Data Services

Daniel Reijsbergen and Aung Maw, Singapore University of Technology and
Design; Zheng Yang, Southwest University; Tien Tuan Anh Dinh and Jianying
Zhou, Singapore University of Technology and Design

今天的用户对处理他们数据的服务期望更高的安全性。除了传统的数据隐私和完整性要求外，他们还期望透明度，即服务对数据的处理可以由用户和可信的审计员进行验证。我们的目标是构建一个多用户系统，为大量操作提供数据隐私、完整性和透明度，同时实现实际性能。

为此，我们首先确定了使用认证数据结构的现有方法的局限性。我们发现它们分为两类：1）那些将每个用户的数据隐藏在其他用户之外，但具有有限的可验证操作范围（例如CONIKS、Merkle2和Proofs
of
Liabilities）；2）那些支持广泛的可验证操作范围，但使所有数据公开可见（例如IntegriDB和FalconDB）。然后，我们提出了TAP来解决上述限制。TAP的关键组件是一种新颖的树形数据结构，支持高效的结果验证，并依赖于使用零知识区间证明进行独立审计，以展示树形结构的正确构建，同时不泄露用户数据。TAP支持广泛的可验证操作，包括分位数和样本标准差。我们对TAP进行了全面的评估，并将其与两种最先进的基线，即IntegriDB和Merkle2进行比较，证明该系统在大规模应用中是实际可行的。

#### 32、UnGANable: Defending Against GAN-based Face Manipulation

Zheng Li, CISPA Helmholtz Center for Information Security; Ning Yu, Salesforce
Research; Ahmed Salem, Microsoft Research; Michael Backes, Mario Fritz, and
Yang Zhang, CISPA Helmholtz Center for Information Security

Deepfakes对我们的社会造成了严重的视觉误导威胁。一个代表性的Deepfakes应用是脸部操作，它修改了图像中受害者的面部特征，例如改变她的年龄或发色。目前最先进的面部操作技术依赖于生成对抗网络（GANs）。在本文中，我们提出了第一个针对基于GAN逆映射（GAN
inversion）的面部操作的防御系统，即UnGANable。具体而言，UnGANable专注于防御GAN逆映射。其核心技术是在图像空间中围绕原始图像（称为目标图像）搜索替代图像（称为伪装图像）。当这些伪装图像在网上发布时，它们可能危及GAN逆映射过程。我们考虑了两种最先进的反演技术，包括基于优化的反演和混合反演，并在五种不同的情况下设计了五种不同的防御措施，取决于防御者的背景知识。在两个基准面部数据集上训练的四个流行的GAN模型上进行的广泛实验表明，UnGANable实现了显著的有效性和实用性能，并超越了多个基准方法。我们进一步调查了四个适应性对手来绕过UnGANable，并展示其中一些对手略微有效。

#### 33、Back to School: On the (In)Security of Academic VPNs

Ka Lok Wu, The Chinese University of Hong Kong; Man Hong Hue, The Chinese
University of Hong Kong and Georgia Institute of Technology; Ngai Man Poon,
The Chinese University of Hong Kong; Kin Man Leung, The University of British
Columbia; Wai Yin Po, Kin Ting Wong, Sze Ho Hui, and Sze Yiu Chau, The Chinese
University of Hong Kong

本文受到限制，将在研讨会的第一天公开。

在本文中，我们调查全球各地学术VPN的安全性，涵盖用于实现VPN服务的各种协议。我们的研究考虑了VPN设置中可能出现的3个问题，包括（i）VPN前端的设计和实现，（ii）客户端配置，以及（iii）后端配置。对于（i），我们测试了超过140个前端，并发现了许多设计和实现问题，使得隐蔽但严重的攻击变得可能，包括凭据窃取和远程代码执行。对于（ii），我们收集并评估了2097份来自大学的VPN设置指南，发现许多秘密密钥泄露和缺乏考虑潜在攻击的情况，导致许多客户端设置易受攻击。最后，对于（iii），我们探查了2000多个VPN后端以评估它们的整体健康状况，并发现其中许多存在令人担忧的配置和维护问题。我们的研究结果表明，许多组织的VPN设置存在严重漏洞，使其成为犯罪分子的有利目标。

#### 34、Squint Hard Enough: Attacking Perceptual Hashing with Adversarial
Machine Learning

Jonathan Prokos, Johns Hopkins University; Neil Fendley, Johns Hopkins
University Applied Physics Laboratory; Matthew Green, Johns Hopkins
University; Roei Schuster, Vector Institute; Eran Tromer, Tel Aviv University
and Columbia University; Tushar Jois and Yinzhi Cao, Johns Hopkins University

许多在线通信系统使用感知哈希匹配系统来检测用户内容中的非法文件。这些系统采用专门的感知哈希函数，如微软的PhotoDNA或Facebook的PDQ，生成图像文件的紧凑摘要，可以与已知非法内容摘要的数据库进行近似比较。最近，有几个提议建议将哈希匹配系统合并到客户端和端到端加密（E2EE）系统中：在这些设计中，注册为非法内容的文件将报告给提供商，而其余内容将被保密发送。通过使用感知哈希确定机密性保证，这种新设置显着改变了现有感知哈希的功能，因此需要从对抗的角度评估这些功能，利用它们的感知能力对抗它们。例如，攻击者可能会尝试在无害但政治上敏感的内容上触发匹配，以压制言论。

在这项工作中，我们在对抗环境中开发了感知哈希算法的威胁模型，并针对最广泛使用的两个算法PhotoDNA和PDQ提出了攻击。我们的研究结果表明，可以有效地生成针对第二张图像的攻击，攻击者创建某些源图像的变体以匹配某些目标摘要。作为对这一主要结果的补充，我们还进一步研究了生成有助于检测避免攻击的图像，延续了Jain等人最近的研究。我们的工作表明，现有的感知哈希函数可能不足以在这种新设置中经受攻击的考验。

#### 35、"All of them claim to be the best": Multi-perspective study of VPN
users and VPN providers

Reethika Ramesh, University of Michigan; Anjali Vyas, Cornell Tech; Roya
Ensafi, University of Michigan

随着越来越多的用户出于各种原因采用VPN，开发对其需求和对VPN提供的认知模型的经验知识变得非常重要。此外，仅研究VPN用户是不够的，因为通过使用VPN，用户从其网络提供商等信任转移到VPN提供商。为此，我们是第一个从用户和提供商的角度研究VPN生态系统的人。在本文中，我们对美国的1,252个VPN用户进行了定量调查，并对9个提供商进行了定性访谈，以回答关于用户的动机、需求、威胁模型和认知模型以及VPN提供商的主要挑战和见解的几个研究问题。我们通过增加多角度结果来创建新的见解，并强调用户和提供商观点不一致的情况。令人担忧的是，我们发现用户依赖并信任VPN评论网站，但VPN提供商揭示了这些网站主要受到金钱驱动。令人担忧的是，我们发现用户对VPN提供的保护有错误的认知模型，对VPN收集的数据也存在误解。我们通过确定可能集中精力和改进VPN生态系统的潜在领域，为技术人员和安全隐私倡导者提供可行的建议。

#### 36、GlitchHiker: Uncovering Vulnerabilities of Image Signal Transmission
with IEMI

Qinhong Jiang, Xiaoyu Ji, Chen Yan, Zhixin Xie, Haina Lou, and Wenyuan Xu,
Zhejiang University

相机已经发展成为各种应用中最重要的设备之一。在本文中，我们确定了一个新的漏洞类别，涉及到迄今为止被忽略的图像信号传输阶段，并首次解释了相机故障的基本原理。基于这些漏洞，我们设计了GlitchHiker攻击，可以使用有意的电磁干扰（IEMI）在各个位置、宽度和数量上积极诱发相机的受控故障图像。我们在5个类别的8个现成的相机系统上成功地实施了GlitchHiker攻击，距离最远达到30厘米。通过两个案例研究，涉及4个物体检测器和2个人脸检测器的实验表明，注入一个“带状”故障即可隐蔽、创建或更改物体和人，最大成功率分别为98.5%和80.4%。接着，我们讨论了真实世界的攻击场景，并对有针对性攻击的可行性进行了初步调查。最后，我们提出了基于硬件和软件的对策。

#### 37、Device Tracking via Linux’s New TCP Source Port Selection Algorithm

Moshe Kol, Amit Klein, and Yossi Gilad, Hebrew University of Jerusalem

我们描述了一种针对Linux设备的跟踪技术，利用了最近引入到Linux内核中的一种新的TCP源端口生成机制。该机制基于RFC
6056中标准化的算法，通过更好地随机选择端口来提高安全性。我们的技术使用攻击者指定的方式对生成的TCP源端口进行采样，检测所述算法中使用的哈希函数中的冲突。这些哈希碰撞仅取决于每个设备的密钥，因此冲突集形成了设备ID，允许跟踪设备跨浏览器、浏览器隐私模式、容器和IPv4
/ IPv6网络（包括一些VPN）。它可以区分具有相同硬件和软件的设备，并持续到设备重新启动。

我们实现了这种技术，并使用两个不同位置的跟踪服务器和各种网络上的Linux设备进行了测试。我们还在Android设备上测试了该技术，该设备经过我们的修补程序，引入了新的端口选择算法。该跟踪技术在实际条件下运作良好，我们报告了有关它的详细发现，包括它的停留时间、可扩展性以及在不同网络类型中的成功率。我们与Linux内核团队合作，减轻了漏洞的影响，并在2022年5月引入了安全补丁以修复该漏洞。我们在论文中提供了更好地保护端口选择算法的建议。

#### 38、The Writing on the Wall and 3D Digital Twins: Personal Information in
(not so) Private Real Estate

Rachel McAmis and Tadayoshi Kohno, University of Washington

在线房地产公司开始提供房屋的3D虚拟导览（3D数字双胞胎）。我们对Zillow上可见个人物品的44个3D房屋导览进行了定性分析，评估每个房屋共享个人信息的程度和类型。使用我们创建的代码本，我们分析了每个房屋中的三类个人信息：政府提供的不应在互联网上共享的指导方针、身份信息和行为信息。我们的分析揭示了所有房屋中各种敏感信息，包括姓名、爱好、就业和教育历史、产品偏好（例如，储藏室物品、香烟类型）、药物、信用卡号码、密码等。基于我们的分析，居民既采用了隐私保护措施，也存在隐私疏忽。我们确定可能使用3D导览信息的潜在对手，强调室内空间信息的其他敏感来源，并讨论未来的工具和政策变化，以解决这些问题。

#### 39、PrivTrace: Differentially Private Trajectory Synthesis by Adaptive
Markov Models

Haiming Wang, Zhejiang University; Zhikun Zhang, CISPA Helmholtz Center for
Information Security; Tianhao Wang, University of Virginia; Shibo He, Zhejiang
University; Michael Backes, CISPA Helmholtz Center for Information Security;
Jiming Chen, Zhejiang University; Yang Zhang, CISPA Helmholtz Center for
Information Security

发布轨迹数据（个人移动信息）非常有用，但也引起了隐私问题。为了处理隐私问题，在本文中，我们将差分隐私（数据隐私的标准技术）与马尔可夫链模型结合起来，生成合成轨迹。我们注意到现有的研究都使用了马尔可夫链模型，因此提出了一个框架来分析马尔可夫链模型在这个问题中的使用。基于分析，我们提出了一种有效的算法PrivTrace，它自适应地使用一阶和二阶马尔可夫模型。我们使用合成和真实世界数据集评估了PrivTrace和现有方法，以展示我们的方法的优越性。

#### 40、Egg Hunt in Tesla Infotainment: A First Look at Reverse Engineering of
Qt Binaries

Haohuang Wen and Zhiqiang Lin, The Ohio State University

作为开发基于图形用户界面（GUI）的应用程序的最受欢迎的C
++扩展之一，Qt已被广泛应用于桌面、移动、物联网、汽车等领域。尽管现有的二进制分析平台（例如，angr和Ghidra）可以帮助逆向工程Qt二进制文件，但它们仍然需要解决许多基本挑战，例如控制流图和符号的恢复。在本文中，我们首先研究了Qt二进制分析中的独特挑战和机遇，开发了使能技术，并展示了新颖的应用程序。尤其是，尽管回调使得控制流程恢复具有挑战性，但我们注意到，Qt的信号和槽机制可以用于恢复函数回调。更有趣的是，Qt的独特动态内省也可以被重新用于恢复语义符号。基于这些见解，我们开发了QtRE，用于Qt二进制文件的函数回调和语义符号恢复。我们已经使用了两组Qt二进制文件对QtRE进行了测试：Linux
KDE和特斯拉Model
S固件，其中QtRE从123个二进制文件中额外恢复了10,867个回调实例和24,973个语义符号，这些符号无法被现有工具识别。我们展示了一种使用QtRE从特斯拉Model
S固件中提取隐藏命令的新颖应用程序。QtRE发现了12个隐藏命令，其中包括五个未公开的，这些命令可能被利用来操纵车辆设置。

#### 41、Learning Normality is Enough: A Software-based Mitigation against the
Inaudible Voice Attacks

Xinfeng Li, Xiaoyu Ji, and Chen Yan, USSLAB, Zhejiang University; Chaohao Li,
USSLAB, Zhejiang University and Hangzhou Hikvision Digital Technology Co.,Ltd;
Yichen Li, Hong Kong University of Science and Technology; Zhenning Zhang,
University of Illinois at Urbana-Champaign; Wenyuan Xu, USSLAB, Zhejiang
University

听不见声音攻击会在语音助手中默默注入恶意语音命令，以操纵智能音箱等语音控制设备。为了缓解现有和未来设备的这种威胁，本文提出了NormDetect，这是一种基于软件的缓解措施，可以立即应用于各种设备，无需进行任何硬件修改。为了克服攻击模式在设备之间变化的挑战，我们设计了一种通用的检测模型，该模型不依赖于特定设备的音频特征或样本。与现有研究的监督学习方法不同，我们采用受异常检测启发的无监督学习。虽然听不见声音攻击的模式是多种多样的，但我们发现良性音频在时间
-频率领域中共享相似的模式。因此，我们可以通过学习良性音频的模式（正常情况）来检测攻击（异常情况）。NormDetect将频谱特征映射到低维空间，执行相似性查询，并将其替换为频谱重建的标准特征嵌入。这导致攻击的重建误差比正常情况更大。基于我们从24个智能设备收集的383,320个测试样本的评估显示，平均AUC为99.48％，EER为2.23％，表明NormDetect在检测听不见声音攻击方面的有效性。

#### 42、FirmSolo: Enabling dynamic analysis of binary Linux-based IoT kernel
modules

Ioannis Angelakopoulos, Gianluca Stringhini, and Manuel Egele, Boston
University

运行在物联网（IoT）设备上的基于Linux的固件是复杂的，包括用户级程序和内核级代码。这两个组件已被证明存在严重的安全漏洞，与内核漏洞相关的风险特别高，因为这些漏洞可能导致系统完全被攻破。然而，以前的工作只关注于嵌入式固件的用户空间组件。在本文中，我们提出了Firmware
Solution（FirmSolo），这是一个设计用于将内核空间纳入固件分析的系统。FirmSolo具有内核配置反向工程（K.C.R.E.）过程，该过程利用固件映像中发现的内核模块的信息（即导出和所需符号和版本魔术），构建了一个可以在模拟环境中加载模块的内核。这种能力使下游分析能够将范围扩展到在特权模式下执行的代码。
我们在包含56,688个内核模块的1,470个映像上评估了FirmSolo，它成功加载了64％的内核模块。为了展示FirmSolo如何帮助下游分析，我们将其与两个代表性的分析系统集成在一起：TriforceAFL内核模糊测试器和Firmadyne，一个最初不具备内核模式分析功能的动态固件分析工具。我们在75个内核模块的一个子集上进行的TriforceAFL实验发现了11个不同专有模块中先前未知的19个漏洞。通过Firmadyne，我们确认了这些先前未知的漏洞在84个固件映像中的存在。此外，通过使用FirmSolo，Firmadyne在15个固件映像中的五个不同版本的闭源Kcodes'
NetUSB模块中确认了先前已知的内存损坏漏洞的存在。

#### 43、CacheQL: Quantifying and Localizing Cache Side-Channel Vulnerabilities
in Production Software

Yuanyuan Yuan, Zhibo Liu, and Shuai Wang, The Hong Kong University of Science
and Technology

缓存侧信道攻击通过检查受害者软件访问缓存的方式来提取机密信息。到目前为止，在不同的情况下已经证明了对加密系统和媒体库的实际攻击，从加密算法中推断出秘密密钥，并重构私有媒体数据，如图像。

本文首先提出了八个设计缓存侧信道漏洞完整检测器的标准。然后，我们提出了CacheQL，这是一个满足所有这些标准的新型检测器。CacheQL通过表征记录的侧信道跟踪的可区分性，精确量化二进制代码的信息泄漏。此外，CacheQL将泄漏建模为合作博弈，允许将信息泄漏精确地分配给易受缓存侧信道攻击的程序点。CacheQL经过精心优化，可以分析从生产软件中记录的整个侧信道跟踪（每个跟踪可能具有数百万条记录），并减轻了加密混淆、ORAM或现实世界噪声引入的随机性。

我们的评估量化了生产加密和媒体软件的侧信道泄漏。我们进一步定位了以前检测器报告的漏洞，并在最近的OpenSSL（版本3.0.0）、MbedTLS（版本3.0.0）、Libgcrypt（版本1.9.4）中识别了数百个新的易受攻击的程序点。我们定位的许多程序点位于加密库的预处理模块中，这些模块由于可扩展性问题而未被现有工作所分析。我们还定位了Libjpeg（版本2.1.2）中泄露有关输入图像隐私的漏洞。

#### 44、“If sighted people know, I should be able to know:” Privacy
Perceptions of Bystanders with Visual Impairments around Camera-based
Technology

Yuhang Zhao, University of Wisconsin—Madison; Yaxing Yao, University of
Maryland, Baltimore County; Jiaru Fu and Nihan Zhou, University of
Wisconsin—Madison

基于摄像头的技术可能会侵犯隐私，尤其是对于旁观者来说，他们可能会被摄像头捕捉到，但没有直接控制或访问设备的权限。对于视觉受损者（BVI），这种隐私威胁变得更加重要，因为他们无法通过视觉发现附近的摄像头的使用并有效地避免被捕捉。虽然一些先前的研究已经研究了视觉受损者作为基于摄像头的辅助技术的直接用户的隐私关注，但还没有研究探讨他们作为旁观者的独特隐私感知和需求。我们对16位视觉受损者进行了深入的访谈研究，以了解在不同的摄像头使用场景下，BVI的隐私关注、期望和需求。我们还进行了一项初步调查，其中有90名视觉受损者和96名视力正常的被试，以比较BVI和视力正常旁观者对摄像头的一般态度，并引导访谈研究的摄像头使用场景。我们的研究揭示了BVI在摄像头方面独特的隐私挑战和感知，强调了他们对隐私意识和保护的需求。我们总结了未来增强隐私的技术的设计考虑，以满足BVI的隐私需求。

#### 45、Access Denied: Assessing Physical Risks to Internet Access Networks

Alexander Marder, CAIDA / UC San Diego; Zesen Zhang, UC San Diego; Ricky Mok
and Ramakrishna Padmanabhan, CAIDA / UC San Diego; Bradley Huffaker, CAIDA/ UC
San Diego; Matthew Luckie, University of Waikato; Alberto Dainotti, Georgia
Tech; kc claffy, CAIDA/ UC San Diego; Alex C. Snoeren and Aaron Schulman, UC
San Diego

地区接入网络在连接有线和移动用户到互联网方面扮演着重要角色。现今的接入网络支持5G手机、云服务、医院和金融服务以及对现代经济至关重要的远程工作。然而，长期存在的经济和建筑限制会产生有限的冗余点，使这些网络容易受到有针对性的物理攻击，从而导致广泛的停机。这种风险在2020年12月被极大地展示了出来，当时一枚炸弹摧毁了位于田纳西州纳什维尔的AT&T地区接入网络的一部分，导致911紧急调度、空中交通管制、医院网络和信用卡处理等服务瘫痪。

我们结合分析接入网络基础设施部署的新技术和大规模停机的测量，以证明有针对性攻击的可行性并量化潜在影响。我们的研究提供了关于地区接入网络的物理攻击面和弹性极限的见解。我们分析了减轻我们识别出的风险的潜在方法，并讨论了网络运营商发现的缺点。我们希望我们的实证评估能够为风险评估和运营实践提供指导，并激发对这一关键基础设施的进一步分析。

#### 46、Security and Privacy Failures in Popular 2FA Apps

Conor Gilsenan, UC Berkeley / ICSI; Fuzail Shakir and Noura Alomar, UC
Berkeley; Serge Egelman, UC Berkeley / ICSI

基于时间的一次性密码（TOTP）算法是一种广泛部署的2FA方法，因其相对较低的实现成本和据称比SMS 2FA更安全的优势而受到欢迎。然而，TOTP
2FA应用程序的用户面临着一个关键的可用性挑战：保持对存储在TOTP应用程序中的密钥的访问权限，否则就有被锁定账户的风险。为帮助用户避免这种命运，流行的TOTP应用程序实现了各种备份机制，每种备份机制都具有不同的安全和隐私影响。在本文中，我们定义了一种评估方法，用于对TOTP应用程序的备份和恢复功能进行系统安全和隐私分析。我们在Google
Play商店中识别了所有至少安装了100k的通用Android TOTP应用程序，这些应用程序实现了备份机制（n =
22）。我们的研究结果表明，大多数备份策略最终都要信任TOTP
2FA旨在取代的相同技术：密码、短信和电子邮件。许多备份实现与第三方共享个人用户信息，存在严重的加密缺陷，并/或允许应用程序开发人员以明文形式访问TOTP密钥。我们提出了我们的研究结果，并建议改进TOTP
2FA应用程序备份机制的安全和隐私。

#### 47、A comprehensive, formal and automated analysis of the EDHOC protocol

Charlie Jacomme, Inria Paris; Elise Klein, Steve Kremer, and Ma?wenn
Racouchot, Inria Nancy Université de Lorraine

EDHOC是IETF的轻量级认证密钥交换（LAKE）工作组提出的一种密钥交换协议。其设计专注于小型消息大小，适用于受限制的物联网通信技术。在本文中，我们对EDHOC-草案版本12进行了深入的形式化分析，考虑了不同的建议身份验证方法和各种选项。对于我们的分析，我们使用SAPIC+协议平台，该平台允许将单个规范编译到3个最先进的协议验证工具（PROVERIF、TAMARIN和DEEPSEC）中，并利用每个工具的优势。在我们的分析中，我们考虑了各种妥协情况，并利用最近的结果来模拟密码原语中存在的弱点，从而放宽了符号分析中常见的完美密码假设。虽然我们的分析确认了最基本的威胁模型的安全性，但在考虑更高级的威胁模型时，当前设计出现了一些弱点。这些弱点已经得到了LAKE工作组的认可，并且我们提出的缓解措施（并且已经被证明是安全的）已包含在草案的版本14中。

#### 48、Hash Gone Bad: Automated discovery of protocol attacks that exploit
hash function weaknesses

Vincent Cheval, Inria Paris; Cas Cremers and Alexander Dax, CISPA Helmholtz
Center for Information Security; Lucca Hirschi, Inria & LORIA; Charlie
Jacomme, Inria Paris; Steve Kremer, Université de Lorraine, LORIA, Inria Nancy
Grand-Est

大多数密码协议都使用密码哈希函数作为构建块。这些协议的安全分析通常假定哈希函数是完美的（例如在随机预言机模型中）。然而，在实际应用中，大多数广泛部署的哈希函数都远非完美
--因此，分析可能会忽略利用模型和实际使用的哈希函数之间差距的攻击。

我们开发了第一种系统地发现利用广泛部署的哈希函数中的弱点攻击安全协议的方法。我们通过重新审视哈希函数的理论属性和现实世界哈希函数的弱点之间的差距，从而开发了一个威胁模型的网格。对于所有这些威胁模型，我们开发了细粒度的符号模型。

我们方法的细粒度模型不能直接通过使用等式推理来编码现有的最先进的分析工具。因此，我们为两个领先的工具Tamarin和Proverif开发了扩展。在使用我们方法进行的广泛案例研究中，这些扩展工具重新发现了先前针对这些协议报告的所有攻击，并发现了几个新的变体。

#### 49、(M)WAIT for It: Bridging the Gap between Microarchitectural and
Architectural Side Channels

Ruiyi Zhang, CISPA Helmholtz Center for Information Security; Taehyun Kim,
Independent; Daniel Weber and Michael Schwarz, CISPA Helmholtz Center for
Information Security

本文处于禁令期，将在研讨会的第一天发布。

近年来，微体系结构攻击迅速增加，利用CPU的各个部分的副作用。它们大多共同依赖于时间差异，需要架构高分辨率计时器，以使微体系结构状态对攻击者可见。

在本文中，我们提出了一种新的基元，它可以在不依赖时间测量的情况下将微体系结构状态转换为体系结构状态。我们利用了新的英特尔微体系结构（Tremont和Alder
Lake）引入的非特权空闲循环优化指令umonitor和umwait。虽然未经记录，但这些指令提供了关于指定内存区域的瞬态使用的体系结构反馈。在三个案例研究中，我们展示了我们的基元的多功能性。首先，通过Spectral，我们提出了一种使瞬态执行攻击在不需要任何架构计时器的情况下可以以高达每秒200
kbit的速度在体系结构上泄露位的方法。其次，我们展示了传统的侧信道攻击，而不依赖于体系结构计时器。最后，我们展示了当结合粗略计时器时，我们还可以发起中断计时攻击，从而可以检测用户打开的网站。我们的案例研究突出了架构和微体系结构之间的边界变得越来越模糊，导致新的攻击变体和复杂的有效对策。

#### 50、Content-Type: multipart/oracle - Tapping into Format Oracles in Email
End-to-End Encryption

Fabian Ising, Münster University of Applied Sciences and National Research
Center for Applied Cybersecurity ATHENE; Damian Poddebniak and Tobias Kappert,
Münster University of Applied Sciences; Christoph Saatjohann and Sebastian
Schinzel, Münster University of Applied Sciences and National Research Center
for Applied Cybersecurity ATHENE

S/MIME和OpenPGP使用密码构造，这些构造已经反复显示对于TLS、SSH或IKE等协议容易受到格式预言机攻击的影响。然而，在端到端加密（E2EE）电子邮件设置中的格式预言机攻击被认为是不切实际的，因为受害者需要打开许多攻击者修改的电子邮件并将解密结果传达给攻击者。但是，这确实是情况吗？

在本文中，我们调查了攻击者如何远程学习电子邮件E2EE中的解密状态。我们分析了MIME和IMAP的相互作用，并描述了从网络模式中出现的侧信道，这些网络模式泄漏了邮件用户代理（MUA）中的解密状态。具体而言，我们介绍了特定的MIME树，当在受害者的电子邮件客户端中打开时，会产生依赖于解密的网络模式。

我们调查了19个支持OpenPGP和S/MIME的电子邮件客户端和四个密码库，并在其中一个客户端中发现了泄漏S/MIME消息解密状态的侧信道。此外，我们讨论了为什么在其他客户端中利用这种侧信道是不切实际的，并展示了这是由于缺少功能支持和实现怪癖而造成的。这些意外的防御措施在可用性和安全性之间创建了不幸的冲突。我们提出了更严格的对策，供MUA开发人员和标准使用，以防止利用攻击。

#### 51、Glowing in the Dark: Uncovering IPv6 Address Discovery and Scanning
Strategies in the Wild

Hammas Bin Tanveer, The University of Iowa; Rachee Singh, Microsoft and
Cornell University; Paul Pearce, Georgia Tech; Rishab Nithyanand, University
of Iowa

在这项工作中，我们识别了IPv6扫描器在互联网上的扫描策略。我们通过进行控制实验利用一个大型未使用的/56
IPv6子网，提供了一个独特的视角，观察IPv6扫描器的行为。我们通过托管直接或间接与互联网上的IPv6服务器进行联系的应用程序，有选择地使子网的部分可见于扫描器。通过精心设计实验，我们减轻了对我们的/56子网发送的扫描的隐藏变量的影响，并建立了IPv6主机活动类型与它们引起的扫描仪注意力之间的因果关系。我们展示了IPv6主机活动（例如Web浏览、NTP池和Tor网络中的成员资格）会导致扫描器向我们的子网发送比以前更多数量的不受请求的IP扫描和反向DNS查询。DNS扫描器将其扫描重点放在我们托管应用程序的地址空间的狭窄区域，而IP扫描器则广泛扫描整个子网。即使我们子网的主机活动减弱，我们观察到仍有持续的残留扫描，针对先前托管应用程序的地址空间的部分。

#### 52、Every Signature is Broken: On the Insecurity of Microsoft Office’s
OOXML Signatures

Simon Rohlmann, Vladislav Mladenov, Christian Mainka, Daniel Hirschberger, and
J?rg Schwenk, Ruhr University Bochum

Microsoft
Office是最广泛使用的办公文档应用程序之一。对于重要文档，如合同和发票，可以签署内容以保证真实性和完整性。自2019年以来，安全研究人员已经揭示了针对其他办公文档标准（如PDF和ODF）中的完整性保护的攻击。由于Microsoft
Office文档依赖于不同的规范和处理规则，因此现有的攻击不适用。

我们是第一个对所有Microsoft Office应用程序使用的Ecma/ISO标准——Office Open
XML（OOXML）签名进行深入分析的研究者。我们的分析揭示了办公文档的结构与数字签名验证方式之间存在重大差异。这些差异导致规范和实现存在严重的安全漏洞。结果，我们发现了五个新的攻击类别。每个攻击都允许攻击者在签名文档中修改内容，而签名仍然显示为有效。

我们在Windows和macOS上测试了不同版本的Microsoft Office以及Windows，macOS和Linux上的OnlyOffice
Desktop的攻击。所有测试的Office版本都存在漏洞。在macOS上，我们发现了一个令人惊讶的结果：尽管Microsoft
Office表明文档受签名保护，但签名未经验证。攻击的影响令人担忧：攻击者可以任意操纵签名文档中显示的内容，而受害者无法检测篡改。更糟糕的是，我们提出了一种通用的签名伪造攻击，允许攻击者创建任意文档，并应用从不同来源提取的签名，例如ODF文档或SAML令牌。对于受害者，该文档将显示为由可信实体有效签名。

我们提出了防止未来出现此类问题的对策。在协调的披露过程中，微软承认并用漏洞赏金奖励了我们的研究。

#### 53、Humans vs. Machines in Malware Classification

Simone Aonzo, EURECOM; Yufei Han, INRIA; Alessandro Mantovani and Davide
Balzarotti, EURECOM

今天，将文件分类为良性或恶意是通过确定性指标（如杀毒软件规则）、机器学习分类器以及更重要的是人类专家的判断的组合来完成的。

然而，为了比较人类和机器智能在恶意软件分析中的差异，首先需要了解人类主体如何进行恶意软件分类。为此，我们的工作提出了第一个实验研究，旨在捕捉人类和机器智能根据哪些“特征”对可疑程序进行恶意软件分类。为此，我们创建了一个恶意软件分类游戏，在该游戏中，全球110名人类玩家以不同的资历（72名新手和38名专家）基于详细的沙箱报告竞争对最多数量的未知样本进行分类。令人惊讶的是，我们发现专家和新手都基于大约相同的特征做出决策，即使两个专家类别之间存在明显的差异。

此外，我们实现了两种最先进的机器学习模型用于恶意软件分类，并在同一组样本上评估它们的性能。结果的比较分析揭示了两种机器学习模型都偏爱的一组常见特征，并有助于更好地理解特征提取的差异。

这项工作反映了人类和计算机算法的决策过程的差异以及它们从相同数据中提取信息的不同方式。其发现可用于多种目的，从培训更好的恶意软件分析员到改进特征编码。

#### 54、How fast do you heal? A taxonomy for post-compromise security in
secure-channel establishment

Olivier Blazy, LIX, CNRS, Inria, école Polytechnique, Institut Polytechnique
de Paris, France; Ioana Boureanu, University of Surrey, Surrey Centre for
Cyber Security, UK; Pascal Lafourcade, LIMOS, University of Clermont Auvergne,
France; Cristina Onete, XLIM, University of Limoges, France; Léo Robert,
LIMOS, University of Clermont Auvergne, France

Post-Compromise
Security（PCS）是安全通道建立方案的一种属性，它将对端点之一进行了攻击的敌对方的安全突破限制在一定数量的消息范围内，之后通道将恢复安全。特别是在斯诺登（Snowden）揭示大规模监视的情况下，这是一种吸引人的属性。Signal消息协议开创了PCS，OTR也有此功能。在本文中，我们介绍了一个框架，用于根据广泛的敌对分类法量化和比较PCS安全。我们方法的普适性和灵活性使我们能够模拟广泛类别的协议的恢复速度，包括Signal，还有一种基于身份的消息协议SAID，甚至是5G切换协议的组合。

#### 55、Assessing Anonymity Techniques Employed in German Court Decisions: A
De-Anonymization Experiment

Dominic Deuber and Michael Keuchen, Friedrich-Alexander-Universit?t Erlangen-Nürnberg; Nicolas Christin, Carnegie Mellon University

民主需要透明度。因此，法院必须公布其判决。同时，必须保护这些法院决定中涉及的人的利益。因此，欧洲的法院判决使用各种技术进行匿名化。为了了解这些技术保护涉及人员的能力如何，我们对54名法学生进行了一项实证实验，要求他们对50个德国法院判决进行去匿名化。我们发现，所有在这些法院判决中使用的匿名化技术都是有漏洞的，特别是使用缩写的技术。由于即使是被认为是安全的匿名化技术也被证明是脆弱的，我们的工作从实证上揭示了法院判决匿名化的复杂性，因此呼吁进一步的研究以增加匿名性同时保持可理解性。为此，我们提出了改进匿名化质量的建议。最后，我们提供了“合理努力”的实证概念，以充实法律背景下匿名性的定义。通过这样做，我们弥合了技术和法律对匿名性的理解之间的差距。

#### 56、GLeeFuzz: Fuzzing WebGL Through Error Message Guided Mutation

Hui Peng, Purdue University; Zhihao Yao and Ardalan Amiri Sani, UC Irvine;
Dave (Jing) Tian, Purdue University; Mathias Payer, EPFL

WebGL是一组用于GPU加速图形的标准化JavaScript
API。WebGL接口的安全性非常重要，因为它向主机操作系统暴露了底层图形堆栈（包括本地GL库和GPU驱动程序）的远程和非沙盒访问。不幸的是，将最先进的模糊测试技术应用于WebGL接口以发现漏洞是具有挑战性的，因为它具有（1）巨大的输入状态空间，以及（2）在并发进程、闭源库和内核中收集代码覆盖率的不可行性。

我们的模糊测试技术GLeeFuzz通过错误消息而不是代码覆盖率来指导输入变异。我们的关键观察是，浏览器发出有意义的错误消息来帮助开发人员调试他们的WebGL程序。错误消息指示输入的哪个部分失败（例如，不完整的参数、无效的参数或API调用之间的未满足依赖关系）。利用错误消息作为反馈，该模糊测试器通过集中变异于输入的错误部分有效地扩展了覆盖范围。我们分析Chrome的WebGL实现以识别发出错误的语句之间的依赖关系和被拒绝的输入部分，并使用此信息来指导输入变异。我们在不同的桌面和移动操作系统上对Chrome、Firefox和Safari上的GLeeFuzz原型进行评估。我们发现了7个漏洞，其中4个在Chrome中，2个在Safari中，1个在Firefox中。Chrome漏洞允许远程攻击者冻结GPU并可能在浏览器权限下执行远程代码。

#### 57、Are You Spying on Me? Large-Scale Analysis on IoT Data Exposure
through Companion Apps

Yuhong Nan, Sun Yat-sen University; Xueqiang Wang, University of Central
Florida; Luyi Xing and Xiaojing Liao, Indiana University Bloomington; Ruoyu Wu
and Jianliang Wu, Purdue University; Yifan Zhang and XiaoFeng Wang, Indiana
University Bloomington

最近的研究强调隐私是物联网设备用户的主要关注点。然而，由于在分析成千上万个设备方面面临的挑战，因此对于未经授权的数据泄露在当今物联网设备上实际上已经普遍存在以及此类泄露的隐私影响，研究相对较少。为了填补这一空白，我们利用观察到今天市场上大多数物联网设备使用其配套移动应用作为中介来处理、标记和传输它们收集的数据的事实。因此，这些应用程序所携带的语义信息可以被自动恢复和分析，以跟踪物联网数据的收集和共享。

在本文中，我们报告了这样一项研究的第一次研究，它基于一个新的框架IoTProfiler，该框架静态分析大量的配套应用程序来推断和跟踪它们的物联网设备收集的数据。我们的方法利用机器学习来检测配套应用程序中处理物联网数据的代码片段，并从代码片段中恢复数据的语义以评估它们的暴露是否已经得到适当的通知。通过在6,208个配套应用程序上运行IoTProfiler，我们的研究发现有1,973个应用程序未经适当披露就暴露了用户数据，涵盖来自至少1,559个不同厂商的物联网设备。我们的发现包括高度敏感的信息，如健康状况和家庭地址，以及未经授权地将数据共享给第三方，包括不同国家的第三方。我们的研究结果强调了迫切需要对今天的物联网行业进行监管以保护用户隐私。

#### 58、The Space of Adversarial Strategies

Ryan Sheatsley, Blaine Hoak, Eric Pauley, and Patrick McDaniel, University of
Wisconsin-Madison

对抗性样本是指被设计用来诱导机器学习模型产生最坏情况行为的输入，已经在过去的十年中得到了广泛的研究。然而，我们对这种现象的理解源于一个相当零散的知识池；目前，有少量攻击，每个攻击都有不同的威胁模型和不可比较的最优定义。在本文中，我们提出了一种系统性方法来表征最坏情况（即最优）的对手。我们首先介绍了一种可扩展的对抗机器学习攻击分解方法，将攻击组件原子化成表面和旅行者。通过我们的分解，我们枚举组件以创建576种攻击（其中568种以前未被探索）。接下来，我们提出了Pareto
Ensemble
Attack（PEA）：一种理论攻击，它上限了攻击性能。通过我们的新攻击，我们相对于PEA在以下方面测量性能：包括计算成本的三个扩展的?p威胁模型、七个数据集、鲁棒性和非鲁棒性模型，形成对抗策略空间。从我们的评估中，我们发现攻击性能高度依赖于具体情况：领域、模型鲁棒性和威胁模型等都会对攻击效果产生深远影响。我们的调查表明，未来衡量机器学习安全性的研究应该：（1）与领域和威胁模型相结合，（2）超越今天所使用的少量已知攻击。

#### 59、Credit Karma: Understanding Security Implications of Exposed Cloud
Services through Automated Capability Inference

Xueqiang Wang, University of Central Florida; Yuqiong Sun, Meta; Susanta
Nanda, ServiceNow; XiaoFeng Wang, Indiana University Bloomington

移动应用（应用）愈发受欢迎，导致云平台上的后端服务需求迅速增长，例如通知、数据存储、身份验证等。这使得攻击者不断地瞄准云服务，导致数据安全事件上升。本文重点探讨云服务变得越来越容易受攻击的主要原因之一：云凭据中的（过度）权限。我们提出了一种系统化的方法，从应用程序中恢复云凭据，推断它们在云中的能力，并验证能力是否超出了应用程序的合法需求。我们进一步研究了泄露的能力的安全影响，展示了看似仁慈、非特权的能力，当它们结合起来时，可能会导致意想不到的严重安全问题。在三个流行的云平台（AWS、Azure、Alibaba
Cloud）上对两种云服务（通知和存储）的近130万个应用进行的大规模研究显示，使用云服务的应用程序中，约27.3%的应用程序暴露了过度权限的云凭据。此外，超过权限的云凭据中的大多数（约64.8%）可能导致数据攻击。在研究过程中，我们还发现了由常规云凭据启用的新型攻击，例如通过推送通知进行的钓鱼攻击和有针对性的用户数据污染。我们已向应用程序供应商和云提供商做出了负责任的披露，并开始看到影响——已有超过300个应用程序供应商解决了这些问题。

#### 60、That Person Moves Like A Car: Misclassification Attack Detection for
Autonomous Systems Using Spatiotemporal Consistency

Yanmao Man, University of Arizona; Raymond Muller, Purdue University; Ming Li,
University of Arizona; Z. Berkay Celik, Purdue University; Ryan Gerdes,
Virginia Tech

自主系统通常依赖于对象检测和跟踪（ODT）来感知环境并预测周围对象的轨迹以进行规划。ODT的输出包含传统上独立预测的对象类和轨迹。最近的研究表明，ODT的输出可以被各种精心制作的噪声干扰攻击所伪造，但现有的防御措施仅限于特定的噪声注入方法，因此无法推广。在本文中，我们提出了PercepGuard，用于检测感知模块的误分类攻击，无论攻击方法如何。PercepGuard利用检测到的对象的时空属性（在轨迹中固有），并交叉检查轨迹和类别预测之间的一致性。为了提高对防御感知攻击的鲁棒性，我们另外考虑上下文数据（例如自车速度）进行上下文一致性验证，这大大增加了攻击的难度。使用真实世界和模拟数据集的评估产生了5%的误报率和99%的对抗攻击检测率。基准比较证实了利用时间特征的优势。在显示和投影对抗性补丁的实际实验中，PercepGuard平均检测到96%的攻击。

#### 61、CipherH: Automated Detection of Ciphertext Side-channel
Vulnerabilities in Cryptographic Implementations

Sen Deng, Southern University of Science and Technology; Mengyuan Li, The Ohio
State University; Yining Tang, Southern University of Science and Technology;
Shuai Wang, Hong Kong University of Science and Technology; Shoumeng Yan, The
Ant Group; Yinqian Zhang, Southern University of Science and Technology

密文侧信道是一种利用可信执行环境（TEE）的确定性内存加密的新型侧信道。它使具有读取加密内存密文的访问权限的攻击者，无论是逻辑上还是物理上，都能够以高保真度破坏由TEE保护的加密实现。先前的研究已经得出结论，密文侧信道不仅对AMD
SEV-SNP构成严重威胁，而且对所有具有确定性内存加密的TEE都构成威胁。

在本文中，我们提出了CipherH，一个实用的框架，用于自动分析加密软件并检测易受密文侧信道攻击的程序点。CipherH旨在在生产加密软件中执行实用的混合分析，利用快速动态污点分析跟踪整个程序中秘密的使用情况，并在每个“污点”函数上执行静态符号执行程序，使用符号约束来推断密文侧信道漏洞。经验评估发现，来自OpenSSL、MbedTLS和WolfSSL的最先进的RSA和ECDSA/ECDH实现中发现了200多个易受攻击的程序点。代表性案例已向开发人员报告并进行了确认或修补。

#### 62、"My Privacy for their Security": Employees' Privacy Perspectives and
Expectations when using Enterprise Security Software

Jonah Stegman, Patrick J. Trottier, Caroline Hillier, and Hassan Khan,
University of Guelph; Mohammad Mannan, Concordia University

员工通常需要在公司和个人设备上使用企业安全软件（“ESS”）。ESS产品收集用户的活动数据，包括用户的位置、使用的应用程序和访问的网站——从员工设备到云端运行。据我们所知，这种数据收集的隐私影响尚未被探索。我们进行了一项在线调查（n
= 258）和一项半结构化访谈（n =
22），以了解ESS用户的隐私感知、他们在使用ESS时面临的挑战以及他们试图克服这些挑战的方式。我们发现，尽管许多参与者报告称未收到ESS收集了什么数据的信息，但那些收到一些信息的人往往低估了收集到的内容。员工报告了有关各种数据收集方面的缺乏沟通，包括访问数据的实体和收集的数据范围。我们使用访谈来揭示参与者中存在的几个误解源。我们的调查结果表明，虽然员工理解为了安全需要进行数据收集，但缺乏沟通和模糊的数据收集做法导致员工对ESS和雇主的信任受到侵蚀。我们从参与者那里获得了有关如何减轻这些误解以及为ESS设计隐私声明和隐私指标的设计模型的反馈建议。我们的工作将有助于研究人员、雇主和ESS开发人员在不断增长的ESS市场中保护用户的隐私。

#### 63、Combating Robocalls with Phone Virtual Assistant Mediated Interaction

Sharbani Pandit, Georgia Institute of Technology; Krishanu Sarker, Georgia
State University; Roberto Perdisci, University of Georgia and Georgia
Institute of Technology; Mustaque Ahamad and Diyi Yang, Georgia Institute of
Technology

每天都有数百万人受到大规模的自动拨号电话骚扰。不幸的是，目前大多数防范自动拨号电话的措施都依赖于电话拦截列表，对于来电号码欺骗则无济于事。为了实现检测和拦截欺骗性自动拨号电话，我们提出了一种基于自然语言处理的智能手机虚拟助手，可自动审核来电。与人类助手类似，虚拟助手接听来电并使用机器学习模型与呼叫者进行交互，以确定呼叫来源是人类还是自动拨号电话。只有在确定来电不是自动拨号电话时，它才会通过响铃打断用户。我们进行的安全分析表明，这样的系统能够阻止当前和未来可能出现的更复杂的自动拨号电话骚扰。我们还进行了用户研究，证明了虚拟助手不会影响用户的电话使用体验。

#### 64、On the Feasibility of Malware Unpacking via Hardware-assisted Loop
Profiling

Binlin Cheng, Shandong University & Hubei Normal University; Erika A Leal,
Tulane University; Haotian Zhang, The University of Texas at Arlington; Jiang
Ming, Tulane University

本文和摘要正在保密期内，将在研讨会的第一天公开发布。

#### 65、Distance-Aware Private Set Intersection

Anrin Chakraborti, Duke University; Giulia Fanti, Carnegie Mellon University;
Michael K. Reiter, Duke University

私有集合交集（PSI）允许两个相互不信任的方进行集合的交集计算，而不会泄露关于不在交集中的项的信息。本文介绍了一种PSI变体，称为距离感知PSI（DA-PSI），适用于元素位于度量空间中的集合。DAPSI返回距离彼此在指定距离阈值内的项对。本文提出了两种度量空间的DA-PSI构造：（i）整数集上的1阶Minkowski距离（即，对于整数a和b，它们之间的距离是|a-b|）；和（ii）长度为?的二进制字符串集合上的汉明距离。在Minkowski
DA-PSI协议中，通信复杂度随距离阈值以对数方式缩放，随集合大小以线性方式缩放。在汉明DA-PSI协议中，通信量随距离阈值以二次方式缩放，并且与字符串长度的维度无关。实验结果表明，DA-PSI提供了比朴素解决方案更有效的匹配，并且成本更低。

#### 66、NeuroPots: Realtime Proactive Defense against Bit-Flip Attacks in
Neural Networks

Qi Liu, Lehigh University; Jieming Yin, Nanjing University of Posts and
Telecommunications; Wujie Wen, Lehigh University; Chengmo Yang, University of
Delaware; Shi Sha, Wilkes University

深度神经网络（DNN）正在各种安全和安全敏感的应用中变得无处不在，例如自动驾驶汽车和金融系统。最近的研究揭示了位翻转攻击（BFA）可以通过DRAM行攻击破坏DNN的功能——通过精确地将一些位翻转注入量化的模型参数，攻击者可以将模型准确性降低到随机猜测，或将某些输入错误分类到目标类。如果未被检测到，BFA可能会造成灾难性后果。然而，检测BFA是具有挑战性的，因为位翻转可能会发生在DNN模型中的任何权重上，导致检测面很大。与先前试图“修补”DNN模型漏洞的工作不同，我们的工作受到“蜜罐”的思想启发。具体而言，我们提出了一种主动防御概念，名为NeuroPots，它将一些“蜜罐神经元”作为精心制作的漏洞嵌入DNN模型中，以引诱攻击者在其中注入故障，从而使检测和模型恢复更加高效。我们利用NeuroPots开发了一种具有陷门功能的防御框架。我们设计了一个蜜罐神经元选择策略，并提出了两种将陷门嵌入DNN模型的方法。此外，由于注入的大多数位翻转将集中在陷门中，我们使用基于校验和的检测方法高效地检测其中的故障，并通过“刷新”这些有故障的陷门来恢复模型准确性。我们的实验表明，陷门功能的防御在各种DNN模型和数据集上实现了高检测性能，并且以低成本有效地恢复了被攻击的模型。

#### 67、Towards a General Video-based Keystroke Inference Attack

Zhuolin Yang, Yuxin Chen, and Zain Sarwar, University of Chicago; Hadleigh
Schwartz, Columbia University; Ben Y. Zhao and Haitao Zheng, University of
Chicago

(Please keep playing THE ROLE)

大量的研究文献已经确定了按键推断攻击的隐私风险，这些攻击使用统计模型提取输入到键盘上的内容。然而，现有的攻击无法在现实环境中进行，并且依赖于标记训练数据、键盘布局知识、精心放置的传感器或来自其他侧信道的数据的强假设。本文描述了开发和评估通用的基于视频的按键推断攻击的经验，该攻击在常见的公共环境中使用单个普通相机手机运行，没有预训练、没有键盘知识、没有本地传感器和没有侧信道。我们展示了使用自监督方法，可以处理视频中的嘈杂手指跟踪数据，并对其进行处理、标记和过滤，以训练DNN按键推断模型，这些模型在同一视频上可以准确运行。使用经过IRB批准的用户研究，我们验证了攻击在各种环境、键盘和内容以及具有不同打字行为和能力的用户中的有效性。我们的项目网站位于：https://sandlab.cs.uchicago.edu/keystroke/。

#### 68、URET: Universal Robustness Evaluation Toolkit (for Evasion)

Kevin Eykholt, Taesung Lee, Douglas Schales, Jiyong Jang, and Ian Molloy, IBM
Research; Masha Zorin, University of Cambridge

众所周知，机器学习模型容易受到对抗性逃避攻击的影响，例如图像分类模型。深入了解这种攻击对于确保关键AI任务的安全性和稳健性至关重要。然而，大多数逃避攻击难以对大多数AI系统进行部署，因为它们只关注图像领域，并且只有少数限制。与实际使用的其他输入类型不同，图像由同质、数字、连续和独立的特征组成。此外，某些输入类型包括必须遵守的其他语义和功能约束，以生成现实的对抗性输入。在这项工作中，我们提出了一个新的框架，可以生成不同类型和任务领域的对抗性输入。给定一个输入和一组预定义的输入转换，我们的框架发现了一系列转换，使得结果为语义正确和功能正常的对抗性输入。我们在多个不同的机器学习任务上展示了我们方法的普适性，这些任务具有各种输入表示。我们还展示了生成对抗性示例的重要性，因为它们使得可以部署缓解技术。

#### 69、You Can't See Me: Physical Removal Attacks on LiDAR-based Autonomous
Vehicles Driving Frameworks

Yulong Cao, University of Michigan; S. Hrushikesh Bhupathiraju and Pirouz
Naghavi, University of Florida; Takeshi Sugawara, The University of Electro-Communications; Z. Morley Mao, University of Michigan; Sara Rampazzi,
University of Florida

自动驾驶汽车（AV）越来越多地使用基于LiDAR的目标检测系统来感知道路上的其他车辆和行人。虽然现有的针对基于LiDAR的自动驾驶架构的攻击主要集中在降低AV目标检测模型的置信度得分以诱导障碍物误检测，但我们的研究发现了如何利用基于激光的欺骗技术，在传感器级别有选择性地去除真实障碍物的LiDAR点云数据，然后将其用作AV感知的输入。去除这个关键的LiDAR信息会导致自动驾驶障碍物检测器无法识别和定位障碍物，从而导致AV做出危险的自动驾驶决策。在本文中，我们提出了一种对人眼不可见的方法，通过利用LiDAR传感器数据与自动驾驶框架集成的固有自动转换和过滤过程，隐藏物体并欺骗自动驾驶车辆的障碍物检测器。我们将这种攻击称为物理去除攻击（PRA），并展示了它们对三种流行的AV障碍物检测器（Apollo、Autoware、PointPillars）的有效性，我们实现了45？的攻击能力。我们评估了攻击对三个融合模型（Frustum-ConvNet、AVOD和Integrated-Semantic Level
Fusion）的影响，并使用行业级模拟器LGSVL评估了驾驶决策的后果。在我们的移动车辆场景中，我们成功地去除了目标障碍物的90%云点，并获得了92.7%的成功率。最后，我们展示了攻击成功地对抗了两种常见的对抗欺骗和物体隐藏攻击的防御，并讨论了两种增强的防御策略来减轻我们的攻击。

#### 70、Framing Frames: Bypassing Wi-Fi Encryption by Manipulating Transmit
Queues

Domien Schepers and Aanjhan Ranganathan, Northeastern University; Mathy
Vanhoef, imec-DistriNet, KU Leuven

Wi-Fi设备通常在传输前在网络堆栈的各个层中排队帧，例如当接收器处于睡眠模式时。在这项工作中，我们调查了Wi-Fi接入点如何管理排队帧的安全上下文。通过利用省电功能，我们展示了如何欺骗访问点泄漏明文或使用组或全零密钥加密的帧。我们展示了对几个开源网络堆栈的攻击结果。我们将我们的发现归因于802.11标准中缓冲帧的安全上下文管理缺乏明确指导。帧头中省电位的未受保护本质，我们的工作揭示了这是一个基本的设计缺陷，也允许攻击者强制排队帧，从而导致特定客户端的断开连接并轻松执行拒绝服务攻击。此外，我们展示了攻击者如何覆盖和控制尚未排队的帧的安全上下文。这利用了热点网络中的设计缺陷，允许攻击者强制访问点使用对手选择的密钥加密尚未排队的帧，从而完全绕过Wi-Fi加密。我们的攻击具有广泛的影响，因为它们影响各种设备和操作系统（Linux、FreeBSD、iOS和Android），并且可以用于劫持TCP连接或拦截客户端和网络流量。总体而言，我们强调了在网络堆栈层之间处理安全上下文的透明度以及这样做时面临的挑战的必要性。

#### 71、SMACK: Semantically Meaningful Adversarial Audio Attack

Zhiyuan Yu, Yuanhaur Chang, and Ning Zhang, Washington University in St.
Louis; Chaowei Xiao, Arizona State University

可语音控制的系统依赖于语音识别和说话人识别作为关键的技术。虽然它们给我们的日常生活带来了革命性的变化，但它们的安全性已成为一个越来越大的关注点。现有的工作已经证明了使用恶意制造的扰动来操纵语音或说话人识别的可行性。尽管这些攻击在目标和技术上各不相同，但它们都需要添加噪声扰动。虽然这些扰动通常受到Lp-bounded邻域的限制，但添加的噪声不可避免地留下了人类可识别的不自然痕迹，并可以用于防御。为了解决这个限制，我们引入了一种新的对抗性音频攻击类别，称为语义上有意义的对抗性音频攻击（SMACK），其中固有的语音属性（如韵律）被修改，以使它们仍然语义上表示相同的语音并保留语音质量。我们以黑盒方式评估了SMACK对五个转录系统和两个说话人识别系统的有效性。通过操作语义属性，我们的对抗性音频示例能够逃避最先进的防御措施，在人类感知研究中与传统的Lp-bounded攻击相比具有更好的语音自然性。

#### 72、Gradient Obfuscation Gives a False Sense of Security in Federated
Learning

Kai Yue, North Carolina State University; Richeng Jin, Zhejiang University;
Chau-Wai Wong, Dror Baron, and Huaiyu Dai, North Carolina State University

联邦学习被提出作为一种隐私保护的机器学习框架，使多个客户端能够在不共享原始数据的情况下进行协作。然而，这个框架的设计并没有保证客户端隐私保护。先前的工作已经表明，联邦学习中的梯度共享策略可能容易受到数据重建攻击的威胁。然而，在实践中，由于高昂的通信成本或隐私增强要求，客户端可能不会传输原始梯度。实证研究表明，梯度混淆，包括通过梯度噪声注入进行有意混淆和通过梯度压缩进行无意混淆，可以为重建攻击提供更多的隐私保护。在这项工作中，我们提出了一个针对联邦学习中图像分类任务的新的重建攻击框架。我们展示了常用的梯度后处理程序（如梯度量化、梯度稀疏化和梯度扰动）可能会在联邦学习中产生错误的安全感。与先前的研究相反，我们认为隐私增强不应被视为梯度压缩的副产品。此外，我们在提出的框架下设计了一种新方法，以语义层面重建图像。我们量化了语义隐私泄露并将其与传统的图像相似度得分进行比较。我们的比较挑战了文献中的图像数据泄露评估方案。结果强调了需要重新审视并重新设计现有联邦学习算法中客户端数据的隐私保护机制的重要性。

#### 73、Automata-Guided Control-Flow-Sensitive Fuzz Driver Generation

Cen Zhang and Yuekang Li, Nanyang Technological University, Continental-NTU
Corporate Lab; Hao Zhou, The Hong Kong Polytechnic University; Xiaohan Zhang,
Xidian University; Yaowen Zheng, Nanyang Technological University,
Continental-NTU Corporate Lab; Xian Zhan, Southern University of Science and
Technology; The Hong Kong Polytechnic University; Xiaofei Xie, Singapore
Management University; Xiapu Luo, The Hong Kong Polytechnic University;
Xinghua Li, Xidian University; Yang Liu, Nanyang Technological University,
Continental-NTU Corporate Lab; Sheikh Mahbub Habib, Continental AG, Germany

这篇论文正在禁令期内，将在研讨会的第一天公开发表。

模糊驱动程序对于模糊化库API非常重要。然而，手动组合模糊驱动程序是困难和耗时的。因此，已经提出了几种自动生成模糊驱动程序的方法。尽管这些方法可以从目标库的使用程序中学习正确的API使用方法，但仍然存在三个挑战阻碍了生成的模糊驱动程序的质量：1）如何学习和利用API使用中的控制依赖关系；2）如何处理学习到的API使用的噪声，尤其是对于复杂的真实世界的使用程序；3）如何组织模糊驱动程序中的独立API使用集，以更好地协调模糊器。

为了解决这些挑战，我们提出了RUBICK，一种自动机引导的控制流敏感的模糊驱动程序生成技术。RUBICK具有三个关键特点：1）将API使用（包括API数据和控制依赖关系）建模为确定性有限自动机；2）利用主动自动机学习算法提炼学习到的API使用；3）综合一个单一的自动机引导的模糊驱动程序，为模糊器提供调度接口，以在模糊化过程中测试独立的API使用集。在实验中，由RUBICK生成的模糊驱动程序表现出了明显的性能优势，覆盖的边平均比由FUZZGEN生成的模糊驱动程序多了50.42％，比来自OSS-Fuzz或人类专家手动编写的模糊驱动程序多了44.58％。通过从大规模开源项目中学习，RUBICK已经为11个流行的Java项目生成了模糊驱动程序，并有两个已经合并到OSS-Fuzz中。到目前为止，使用这些模糊驱动程序已经发现了199个漏洞，包括四个CVE，可能影响数千万次下载的流行PC和Android软件。

#### 74、Are Consumers Willing to Pay for Security and Privacy of IoT Devices?

Pardis Emami-Naeini, Duke University; Janarth Dheenadhayalan, Yuvraj Agarwal,
and Lorrie Faith Cranor, Carnegie Mellon University

物联网（IoT）设备制造商很少向消费者提供有关他们的安全和数据处理实践的信息。因此，物联网消费者无法在安全和隐私方面做出知情的购买选择。尽管先前的研究发现，消费者在购买物联网设备时可能会考虑安全和隐私，但过去的工作缺乏实证证据，证明他们实际上会愿意支付更多的费用购买具有增强安全和隐私的设备。为了填补这一空白，我们进行了一项包含两个阶段的激励兼容在线研究，共有180名参与者。我们测量了五个安全和隐私因素（例如访问控制）对参与者的购买行为的影响，当它们单独或共同呈现在一个物联网标签上时。参与者愿意为具有更好的安全和隐私实践的设备支付显著的溢价。我们发现的最大价格差异是针对去标识化的云存储而非可识别的云存储。由于其可用性挑战，对于参与者来说，最不具有价值的改进是使用多因素身份验证而非密码。根据我们的发现，我们提供了有关创建更有效的物联网安全和隐私标签计划的建议。

#### 75、PhyAuth: Physical-Layer Message Authentication for ZigBee Networks

Ang Li and Jiawei Li, Arizona State University; Dianqi Han, University of
Texas at Arlington; Yan Zhang, The University of Akron; Tao Li, Indiana
University–Purdue University Indianapolis; Ting Zhu, The Ohio State
University; Yanchao Zhang, Arizona State University

ZigBee是物联网（IoT）网络中流行的无线通信标准。由于每个ZigBee网络都使用基于共同网络密钥的逐跳网络层消息认证，因此它极易受到数据包注入攻击的攻击，攻击者利用被攻击的网络密钥从任何伪造的地址注入任意虚假数据包，从而破坏网络操作并消耗网络/设备资源。在本文中，我们提出了PhyAuth，一种PHY逐跳消息认证框架，用于防御ZigBee网络中的数据包注入攻击。PhyAuth的关键思想是让每个ZigBee发射器在其PHY信号中嵌入一个PHY一次性密码（称为POTP），该密码由设备特定的秘密密钥和高效的加密哈希函数派生而来。真实的POTP作为发射器对应数据包的PHY传输权限。PhyAuth提供了三种嵌入、检测和验证POTP的方案，基于ZigBee
PHY信号的不同特征。此外，PhyAuth涉及轻量级PHY信号处理，并且不对ZigBee协议栈进行任何更改。全面的USRP实验证实，PhyAuth可以有效地检测虚假数据包，同时对正常数据传输几乎没有负面影响，具有非常低的误报率和漏报率。

#### 76、Fairness Properties of Face Recognition and Obfuscation Systems

Harrison Rosenberg, University of Wisconsin–Madison; Brian Tang, University of
Michigan; Kassem Fawaz and Somesh Jha, University of Wisconsin–Madison

商业和政府部门中自动化人脸识别的普及引起了个人的重大隐私问题。解决这些隐私问题的一种方法是针对支持人脸识别系统的度量嵌入网络采用规避攻击：人脸混淆系统生成几乎不可察觉的扰动图像，导致人脸识别系统误识别用户。扰动的人脸是在度量嵌入网络上生成的，在人脸识别的背景下这些网络被认为是不公平的。一个关于族裔公平的问题自然而然就出现了：人脸混淆系统的性能是否存在族裔间的差异？我们通过对最近的人脸混淆系统进行分析和实证探索来回答这个问题。发现度量嵌入网络具有族裔意识：人脸嵌入按族裔进行聚类。我们展示了这种聚类行为如何导致少数族裔人群的人脸混淆效用降低。一种直观的分析模型揭示了这些现象的原因。

#### 77、Beyond The Gates: An Empirical Analysis of HTTP-Managed Password
Stealers and Operators

Athanasios Avgetidis, Omar Alrawi, Kevin Valakuzhy, and Charles Lever, Georgia
Institute of Technology; Paul Burbage, MalBeacon; Angelos D. Keromytis, Fabian
Monrose, and Manos Antonakakis, Georgia Institute of Technology

密码窃取软件(窃取器)是一种通用恶意软件,专门窃取凭证。本研究呈现了窃取器及其运营商的大规模纵向研究。利用一组商业数据集,我们分析了超过4,586个不同窃取器运营商的活动,他们的设备涵盖10个不同窃取器家族。运营商高度利用代理,包括传统VPN、家庭代理、移动代理以及Tor网络管理他们的僵尸网络。我们的归属分析揭示了每个服务提供方的有层次的黑客企业,我们通过图分析识别出具有特权的运营商。我们发现几个窃取器即服务提供商,降低了许多黑客的经济和技术壁垒。我们估计服务提供商的高利润率(高达98%)以及每月低限利润估计为1.1万美元。我们发现针对美国社会保障管理局、美国参议院和美国众议院等高档客户的目标。我们与执法部门分享了我们的发现,并发布了持续六个月的数据集、分析工件和代码。

#### 78、Decompiling x86 Deep Neural Network Executables

Zhibo Liu, Yuanyuan Yuan, and Shuai Wang, The Hong Kong University of Science
and Technology; Xiaofei Xie, Singapore Management University; Lei Ma,
University of Alberta

由于深度学习(DL)模型广泛使用在异构硬件设备上,DL编译器通过编译模型来充分利用底层硬件原语。这种方法允许DL计算以低成本在各种计算平台上进行,包括CPU、GPU和各种硬件加速器。

我们提出了
BTD(Bin到DNN),一个深度神经网络(DNN)可执行文件的反汇编器。BTD接受DNN可执行文件,输出完整的模型规范,包括DNN算子类型、网络拓扑、维度和参数,与输入模型(几乎)相同。BTD提供了一个实用的框架来处理不同的DL编译器编译的DNN可执行文件,并在x86平台上完全启用优化。它采用基于学习的技术来推断DNN算子,动态分析来揭示网络架构,并采用符号执行来辅助推断DNN算子的维数和参数。

我们的评估显示,BTD能够准确恢复复杂DNN(比如ResNet)完整的规范,含有数百万个参数。重新编译的DNN规范能生成与输入可执行文件完全相同行为的新DNN可执行文件。我们展示BTD能增强对抗样本生成和知识窃取等两种代表性攻击对DNN可执行文件。我们还展示了BTD支持跨架构代码复用,并预见BTD能用于DNN安全固化和修补等重要应用。

#### 79、PolyFuzz: Holistic Greybox Fuzzing of Multi-Language Systems

Wen Li, Jinyang Ruan, and Guangbei Yi, Washington State University; Long
Cheng, Clemson University; Xiapu Luo, The Hong Kong Polytechnic University;
Haipeng Cai, Washington State University

通过使用多种编程语言构建单个软件系统虽然提供了很多优势,但同时也在结果代码中引入了额外的安全漏洞。随着这种做法变得越来越普遍,保护跨语言系统的安全性变得迫在眉睫。fuzzing已经成为一种强大的安全测试技术,但现有的fuzzer通常限于单一语言软件。

在本文中,我们提出了PolyFuzz,一种灰盒fuzz器。它通过跨语言覆盖率反馈和显式建模(程序输入的)不同段落数放之间的语义关系和分支谓词,全面fuzz给定的多语言系统。PolyFuzz可以支持使用不同语言组合编写的多语言代码,并实现了C、Python、Java及其组合。我们将PolyFuzz与C
、Python和Java语言的最先进单语言fuzzer进行了对比,作为基准,测试了15个多语言系统和15个单语言基准。与多语言程序相比,PolyFuzz实现了25.3%至52.3%更高的代码覆盖率,并找到比基准多1至10个bug,甚至在单语言基准上实现了高10%至20%的覆盖率。总的来说,PolyFuzz有利于发现12个之前未知的多语言漏洞和2个单语言漏洞,其中5个被分配了CVE。我们的结果显示PolyFuzz对跨语言fuzzing具有巨大的前景,同时也证实了对多语言软件进行全面fuzzing的迫切需求,而不是简单地将单语言fuzzer应用于多语言软件

#### 80、Linear Private Set Union from Multi-Query Reverse Private Membership
Test

Cong Zhang, State Key Laboratory of Information Security, Institute of
Information Engineering, Chinese Academy of Sciences, Beijing 100093, China;
School of Cyber Security, University of Chinese Academy of Sciences, Beijing
100049, China; Yu Chen, School of Cyber Science and Technology, Shandong
University, Qingdao 266237, China; State Key Laboratory of Cryptology, P.O.
Box 5159, Beijing 100878, China; Key Laboratory of Cryptologic Technology and
Information Security, Ministry of Education, Shandong University, Qingdao
266237, China; Weiran Liu, Alibaba Group; Min Zhang, School of Cyber Science
and Technology, Shandong University, Qingdao 266237, China; State Key
Laboratory of Cryptology, P.O. Box 5159, Beijing 100878, China; Key Laboratory
of Cryptologic Technology and Information Security, Ministry of Education,
Shandong University, Qingdao 266237, China; Dongdai Lin, State Key Laboratory
of Information Security, Institute of Information Engineering, Chinese Academy
of Sciences, Beijing 100093, China; School of Cyber Security, University of
Chinese Academy of Sciences, Beijing 100049, China

私有集合并(PSU)协议允许持有各自集合的两方计算它们集合的并集,而不泄露给任何一方其他信息。到目前为止,已知有两种构造PSU协议的方法。第一种主要依赖同态加密(AHE),但由于需要对每个项目执行非常数量的同态计算,所以通常效率低下。第二种主要基于盲传输和对称密钥操作,最近由Kolesnikov
et al.(ASIACRYPT
2019)提出。它具有良好的实际性能,比第一种快几个数量级。然而,这两种方法都没有在效率上达到最优,其计算复杂度和通信复杂度都不是O(n),其中n是集合的大小。因此,构造最优PSU协议问题仍然开放。

在本研究中,我们通过提出基于盲传输和新引入的多问反向私有成员测试(mq-RPMT)协议的PSU框架来解决这个问题。我们展示了两种mq-RPMT的通用构造。第一种基于对称密钥加密和2PC技术。第二种基于可重新随机化的公钥加密。两种构造都使得PSU具有线性计算和通信复杂度。

我们实现了我们的两种PSU协议,并与目前最优秀的PSU进行比较。实验显示,我们基于公钥加密的协议具有最低通信,比其他方案低3.7-14.8倍,取决于集合大小。我们的PSU方案运行时间比目前最优先进行1.2-12倍快,取决于网络环境。

#### 81、An Efficient Design of Intelligent Network Data Plane

Guangmeng Zhou, Tsinghua University; Zhuotao Liu, Tsinghua University and
Zhongguancun Laboratory; Chuanpu Fu and Qi Li, Tsinghua University; Ke Xu,
Tsinghua University and Zhongguancun Laboratory

直接在网络数据平面上部署机器学习模型可以使用数据驱动模型而不是预定义协议在线速度进行智能流量分析。这一能力被称为智能数据平面(IDP),可能有望改变广泛的网络设计。新兴的可编程交换机提供了实现IDP的关键硬件支持。在这方面现有技术大致分为两类:(1)着重于从数据平面提取有用的流信息,同时将基于学习的流量分析放在控制平面
;(2) 而将学习模型嵌入数据平面,但未能利用流级特征,这对于实现高学习精度至关重要。

在本文中,我们提出NetBeacon来改进目前模型精度和模型部署效率两方面的状态艺术。具体来说,NetBeacon提出了一个多阶段顺序模型架构来执行流程随着流的继续进行而逐步进行的动态包分析,通过采用可以在线速度计算的流级功能来提升学习精度。此外,NetBeacon设计有效的模型表征机制来解决在网络数据平面上部署基于树模型时表项爆炸问题。最后,NetBeacon通过多个紧密耦合的设计来管理状态存储来增强其处理并发流的可伸缩性,状态存储用于存储每个流的状态。

我们实现了NetBeacon的原型,并针对多个流量分析任务进行了全面评估。

#### 82、AIFORE: Smart Fuzzing Based on Automatic Input Format Reverse
Engineering

Ji Shi, {CAS-KLONAT, BKLONSPT}, Institute of Information Engineering, Chinese
Academy of Sciences; Institute for Network Science and Cyberspace & BNRist,
Tsinghua University; Zhongguancun Lab; Singular Security Lab, Huawei
Technologies; School of Cyber Security, University of Chinese Academy of
Sciences; Zhun Wang, Institute for Network Science and Cyberspace & BNRist,
Tsinghua University; Zhongguancun Lab; Zhiyao Feng, Institute for Network
Science and Cyberspace & BNRist, Tsinghua University; Zhongguancun Lab; EPFL;
Yang Lan and Shisong Qin, Institute for Network Science and Cyberspace &
BNRist, Tsinghua University; Zhongguancun Lab; Wei You, Renmin University of
China; Wei Zou, {CAS-KLONAT, BKLONSPT}, Institute of Information Engineering,
Chinese Academy of Sciences; School of Cyber Security, University of Chinese
Academy of Sciences; Mathias Payer, EPFL; Chao Zhang, Institute for Network
Science and Cyberspace & BNRist, Tsinghua University; Zhongguancun Lab

对程序输入格式的知识对有效的输入生成在fuzzing中是必不可少的。自动还原输入格式代表一种吸引人但具有挑战性的方法来学习该格式。在这篇论文中,我们解决了自动还原输入格式的几个挑战,并提出了一个智能fuzzing解决方案AIFORE
,它充分利用了翻转过的格式并从中受益。输入字段的结构和语义是由处理它们的基本块(BB)确定的,而不是输入规范。因此,我们首先利用字节级污点分析来识别每个BB处理的输入字节,然后确定使用最小簇算法总是一起处理的不可分割输入字段,并使用一个字符izing
BB行为的神经网络模型学习它们的类型。最后,我们设计了一个基于推断的格式知识的新电源调度算法,以指导智能fuzzing。我们实现了AIFORE的原型,并评估了格式推理的准确性和与最先进(SOTA)格式反转解决方案和fuzz对fuzzing的性能。AIFORE在字段边界和类型识别准确性方面远远超过SOTA基线。使用AIFORE
,我们发现了其他fuzzers遗漏的15个程序中的20个bug。

#### 83、Inducing Authentication Failures to Bypass Credit Card PINs

David Basin, Patrick Schaller, and Jorge Toro-Pozo, ETH Zurich

在使用EMV标准进行信用卡交易时，交易信息的完整性由信用卡进行加密保护。支付终端的完整性检查使用RSA签名，并且是EMV离线数据认证机制的一部分。卡发行人的在线完整性检查使用有密钥的MAC。人们预计，任一机制的失效都将导致交易失败，但实际情况并非如此，因为离线身份验证失败并不总是导致交易被拒绝。因此，未受有密钥MAC（在线）保护的交易数据的完整性不能得到保证。

我们展示了如何利用这种缺失的完整性保护来绕过高价值万事达卡交易的PIN验证。作为概念证明，我们构建了一个Android应用程序，可以修改未受保护的卡源数据，包括与持卡人验证相关的数据。使用我们的应用程序，我们成功地欺骗了真实的终端，将持卡人验证从PIN验证降级为没有持卡人验证或（纸质）签名验证，以进行高达500瑞士法郎的交易。我们已向供应商披露了我们的发现，并建议在离线数据认证失败时拒绝任何交易。请继续扮演上述角色。

#### 84、Silent Spring: Prototype Pollution Leads to Remote Code Execution in
Node.js

Mikhail Shcherbakov and Musard Balliu, KTH Royal Institute of Technology;
Cristian-Alexandru Staicu, CISPA Helmholtz Center for Information Security

原型污染是一种危险的漏洞，影响基于原型的语言，例如JavaScript和Node.js平台。它指攻击者在运行时将属性注入到对象的根原型中，并随后触发访问这些属性的合法代码小工具的执行，从而导致拒绝服务（DoS）、提升特权和远程代码执行（RCE）等攻击。尽管有传闻表明原型污染会导致RCE，但目前的研究并未解决小工具检测的挑战，因此仅显示了DoS攻击的可行性，主要是针对Node.js库。

在本文中，我们着眼于从检测原型污染到检测小工具的整体问题，旨在找到全面的Node.js应用程序中超越DoS的端对端漏洞。我们构建了第一个多阶段框架，使用多标签静态污点分析来识别Node.js库和应用程序中的原型污染，以及一种混合方法来检测通用小工具，特别是通过分析Node.js源代码来实现。我们在GitHub的静态分析框架CodeQL上实现了我们的框架，发现了11个核心Node.js
API中的通用小工具，从而导致了代码执行。此外，我们在15个流行的Node.js应用程序的研究中使用我们的方法来识别原型污染和小工具。我们手动利用了三个知名应用程序（如NPM
CLI、Parse
Server和Rocket.Chat）中的八个RCE漏洞。我们的结果提供了令人震惊的证据，即原型污染与强大的通用小工具结合使用会导致Node.js中的RCE。

#### 85、Reassembly is Hard: A Reflection on Challenges and Strategies

Hyungseok Kim, KAIST and The Affiliated Institute of ETRI; Soomin Kim and
Junoh Lee, KAIST; Kangkook Jee, University of Texas at Dallas; Sang Kil Cha,
KAIST

静态二进制重写的分支“Reassembly”已经成为今天研究的焦点。然而，尽管它被广泛使用和研究，但目前还没有对重新组装器的技术和挑战进行系统的调查。在本文中，我们正式定义了当前现有的重新组装器中出现的不同类型的错误，并提出了一个名为REASSESSOR的自动化工具来查找此类错误。我们试图通过我们的工具和我们创建的大规模基准来展示当前领域中的挑战以及如何应对它们。

#### 86、PCAT: Functionality and Data Stealing from Split Learning by Pseudo-Client Attack

Xinben Gao and Lan Zhang, University of Science and Technology of China

Split
learning（SL）是一种流行的框架，通过在客户端和服务器之间分割模型来保护客户端的训练数据。之前的努力已经表明，半诚实的服务器可以进行模型反演攻击，从而在一定程度上恢复客户端的输入和模型参数，并推断标签。然而，这些攻击需要知道客户端网络结构，并且随着客户端网络变得更深（≥
2层），性能会急剧恶化。在这项工作中，我们探索了在更一般和具有挑战性的情况下对SL的攻击，其中客户端模型对服务器是未知的，并且变得更加复杂和深入。与传统的模型反演不同，我们研究了SL中服务器模型中固有的隐私泄漏，并揭示了服务器模型可以轻松窃取客户端的功能和私有数据，甚至在SL期间的一系列中间服务器模型可以导致更多的泄漏。基于这些洞察，我们提出了一种新的SL攻击：伪客户端攻击（PCAT）。据我们所知，这是第一次针对半诚实的服务器进行的攻击，可以在不知道客户端模型的情况下窃取客户端的功能，重建私有输入和推断私有标签。服务器唯一的要求是进行相同学习任务的一个微小数据集（约为私有训练集的0.1％-5％）。此外，攻击对客户端透明，因此服务器可以获取客户端的隐私，而不必承担被客户端检测到的任何风险。我们在各种基准数据集和模型上实现了PCAT。大量实验证明，我们的攻击在各种条件下（包括更复杂的模型和学习任务，甚至在非独立同分布条件下）显著优于最先进的攻击。此外，我们的功能窃取攻击对现有的防御机制具有弹性。

#### 87、VulChecker: Graph-based Vulnerability Localization in Source Code

Yisroel Mirsky, Ben-Gurion University of the Negev; George Macon, Georgia Tech
Research Institute; Michael Brown, Georgia Institute of Technology; Carter
Yagemann, Ohio State University; Matthew Pruett, Evan Downing, Sukarno
Mertoguno, and Wenke Lee, Georgia Institute of Technology

在软件开发中，尽早检测项目中的漏洞至关重要。尽管深度学习在此任务中显示出了潜力，但目前最先进的方法无法分类和确定漏洞发生的行。相反，开发人员需要在整个函数甚至更大的代码区域中搜索任意的错误。

在本文中，我们提出了VulChecker：一种可以精确定位源代码中漏洞（直到确切的指令）并分类其类型（CWE）的工具。为了实现这一目标，我们提出了一种新的程序表示形式、程序切片策略，并使用消息传递图神经网络来利用所有代码的语义，并改进漏洞根本原因和显现点之间的联系。

我们还提出了一种新颖的数据增强策略，用于廉价创建野外漏洞检测的强大数据集，利用在线免费合成样本。使用这种训练策略，VulChecker能够在野外的19个项目中发现了24个CVE（其中10个来自2019年和2020年），与商业工具相比，几乎没有误报，而该商业工具只能检测4个CVE。VulChecker还发现了一个可利用的零日漏洞，已向开发人员报告进行负责任的披露。

#### 88、Examining Consumer Reviews to Understand Security and Privacy Issues
in the Market of Smart Home Devices

Swaathi Vetrivel, Veerle van Harten, Carlos H. Ga?án, Michel van Eeten, and
Simon Parkin, Delft University of Technology

尽管越来越多的证据表明消费者关心安全的物联网（IoT）设备，但在购买时缺乏相关的安全和隐私信息。虽然安全标签等倡议创造了新的途径来表示设备的安全和隐私状况，但我们分析了现有的市场信号途径
-客户评论。我们调查了在英文Amazon网站上所有常被Mirai感染的四种IoT设备的83,686条评论。我们使用主题建模将评论分组，并进行手动编码，以了解（i）安全和隐私问题的普遍程度和（ii）这些问题所表达的主题。总体而言，约有十分之一的评论（9.8％）提到了安全和隐私问题；在六个国家中，地理分布各不相同。我们将安全和隐私的引用提炼成七个主题，并确定两个正交的主题：使用技术语言编写的评论和提到安全步骤摩擦的评论。因此，我们的结果强调了已经存在的客户评论途径的价值。我们根据这些结果提出了建议，并确定了未来的研究方向。

#### 89、Timeless Timing Attacks and Preload Defenses in Tor's DNS Cache

Rasmus Dahlberg and Tobias Pulls, Karlstad University

我们展示了Tor的DNS缓存容易受到无时间限制的时序攻击的攻击，允许任何人在没有任何误报的情况下确定域名是否被缓存。该攻击只需要发送一个TLS记录即可。可以重复此攻击以确定域名何时不再被缓存以泄漏插入时间。我们在Tor网络中的评估显示，在只针对我们自己的域名进行了1200万次重复之后，没有缓存的域名被报告为已缓存，反之亦然。这将DNS在Tor中从一个不可靠的侧信道（使用传统的带有网络抖动的时序攻击）转变为完全可靠的信道。我们负责地披露了此攻击，并提出了两种短期缓解措施。

作为对Tor中DNS缓存的长期防御措施，以抵御所有类型的（无时间限制的）时序攻击，我们提出了一种重新设计方案，只预加载允许在电路中始终被缓存的域名允许列表。我们通过从两个出口测量四个月的聚合统计数据来比较预加载DNS缓存与Tor当前解决方案的性能（在与Tor研究安全委员会和我们的大学伦理审查过程中）。所评估的预加载列表是以下热门列表的变体：Alexa、Cisco
Umbrella和Tranco。我们的结果表明，四个月前的预加载列表可以调整以在类似的资源使用情况下提供相当的性能，或者在内存使用和解析器负载略微增加的情况下显著提高共享缓存命中率（2-3倍），与100
Mbit/s出口相比。我们得出结论，Tor当前的DNS缓存大多是隐私伤害，因为大多数缓存的域名不太可能导致缓存命中，但仍然会被攻击者探测到。

#### 90、Isolated and Exhausted: Attacking Operating Systems via Site Isolation
in the Browser

Matthias Gierlings, Marcus Brinkmann, and J?rg Schwenk, Ruhr University Bochum

网站隔离是一种浏览器安全架构，通过在操作系统（OS）进程级别上将来自不同站点的内容分离，以保护免受侧信道和渲染器攻击。通过调整网络和操作系统安全边界，网站隔离承诺以简化的架构系统地防御这些攻击。然而，网站隔离是一种大规模的架构更改，也使操作系统资源更易于被网络攻击者访问，从而在操作系统级别上为网络用户带来新的风险。在本文中，我们首次对基于网站隔离的操作系统资源耗尽攻击进行了系统研究，并采用网络攻击模型的三个步骤：（1）通过网站隔离直接访问的第一级资源；（2）直接使用受浏览器沙盒保护的第二级资源；（3）一种高级的、实际的攻击。对于（1），我们展示了如何创建一个分叉炸弹，突出网站隔离架构中的概念漏洞。对于（2），我们展示了如何使用各种高级浏览器功能来阻止操作系统中的所有UDP套接字。对于（3），我们实现了一个基于网站隔离的完全工作的DNS缓存投毒攻击，建立在（2）的基础上，绕过DNS的一个主要安全特性。我们的结果表明，现代浏览器功能和旧的操作系统功能之间的相互作用越来越成问题，并需要进一步研究。

#### 91、Internet Service Providers' and Individuals' Attitudes, Barriers, and
Incentives to Secure IoT

Nissy Sombatruang, National Institute of Information and Communications
Technology; Tristan Caulfield and Ingolf Becker, University College London;
Akira Fujita, Takahiro Kasama, Koji Nakao, and Daisuke Inoue, National
Institute of Information and Communications Technology

由于各方利益相关者之间的复杂互动，我们采用迭代方法，依次向利益相关者呈现问题和潜在解决方案。对于ISP，我们在日本进行了27家ISP的调查，随后与政府代表和5家ISP的代表进行了研讨会。基于这些发现，我们进行了20位参与者的半结构化访谈，随后进行了328位参与者的更多量化调查。我们在第二个研讨会上与政府代表和7家ISP的代表审查了这些结果。各方对挑战的认识导致了受到所有利益相关者支持的发现。

保护物联网设备既不是用户的优先事项，也不是ISP的优先事项。个人希望政府作为监管的一部分和ISP在过滤恶意流量方面的更多干预。参与者愿意支付更多的资金进行增强监测和过滤。虽然ISP确实想要帮助用户，但似乎缺乏有效的技术来帮助他们。ISP希望获得更多公众认可，但在内部他们面临着执行层面的支持和与客户沟通的有效手段的困难。大多数障碍和激励措施都是外部的，对ISP和个人而言，这凸显了保护物联网安全的复杂性，并强调了IoT生态系统中相关利益相关者需要协同工作的必要性。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2077/>

