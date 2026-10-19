生活在信息时代的今天，信息技术的发展日新月异。软件系统作为信息技术的核心，在轨道交通、汽车电子、医疗器械、航空航天等安全攸关领域有着广泛的应用。由于软件安全的问题而导致的恶劣事件是屡见不鲜。2017年上半年的WannaCry勒索病毒全球大爆发，给全球超过150个国家、30万名网络用户带来了超过80亿美元的损失。该病毒是由不法分子利用操作系统软件的漏洞，入侵他人Windows，将大量重要资料进行加密后，使得众多受感染的用户无法正常工作，影响巨大。

 **操作系统内核作为软件系统的核心，确保操作系统内核的安全性与可靠性是构造高可信软件最为关键的一步。采用形式化方法（Formal
Methods）是实现操作系统安全可靠的途径之一。**
形式化方法是采用数学化的方法、工具、技术对软硬件系统进行研究、建立精确的模型，并验证其是否满足特定规范的方法。

目前软件的形式化验证技术有模型检测和定理证明，每种验证方法都有各自的特点。
**模型检测是将软件系统建立有限状态机模型，通过自动搜索有限状态空间和路径来验证模型与规范是否保持一致。**
模型检测的优势在于其自动化，易于被工业界接受，但缺点也是很明显，随着状态和路径的增加，则会出现状态爆炸问题。
**定理证明技术是站在数学逻辑的角度对软件系统进行描述，利用数学推导演绎规则对软件系统进行证明。**
定理证明优点在于能对系统进行精确的描述，相较于模型检测技术不存在状态空间爆炸问题，缺点是自动化程度低，要求验证工程师需具有较高的数学逻辑功底。

 **操作系统内核是软件系统的核心，操作系统内核可靠性直接影响着整个软件系统的运行** 。然而操作系统的验证仍面临着诸多挑战。

近些年来，学术界有诸多的研究将形式化方法运用到操作系统验证的工作中，目前已经取得了一定的研究成果。比较著名的有澳大利亚研究中心NICTA的SeL4项目、由德国联邦教育与研究部资助的Verisoft项目和它的后续项目Verisoft-XT项目、美国耶鲁大学Zhong
Shao团队组成的Flint研究组关于操作系统内核的验证，以及华盛顿大学Hyperkernel的项目。国内关于操作系统内核的形式化验证研究也是发展非常迅速，包括浙江大学、中科大、北航、中科院、华师大等多所高校研究所都做出了贡献。

##  **01** **SeL4的形式化验证**

在2009年，澳大利亚的SeL4项目组宣称世界上第一个成功完成了对操作系统内核的完全形式化验证，在同年该项目组关于SeL4的论文被评为了当年计算机顶级会议（SOSP）的最佳论文，是世界上首个通过正规机器检测证明的通用操作系统，这对形式化领域和操作系统领域具有重大的开创意义。

SeL4的验证框架如图1所示[1]，项目组首先使用Isabelle工具写出IPC、Syscall调度等为内核对象的抽象规范；然后使用Haskell写出可执行规范，运用状态机原理，对于第一步中抽象规范的每一步状态转换，Haskell写出的可执行规范都能产生唯一对应的状态转换；最后通过由SML编写的C-Isabelle转换器和Haskabelle联合形式证明C代码和第二步由Haskell定义的语义保持一致。

![1.png](https://image.3001.net/images/20220802/1659417923_62e8b543aa064b987a7fb.png!small)

图1 SeL4的形式化验证框架

##  **02** **PikeOS的形式化验证**

德国的Verisoft项目[2]组提出了一个命名为CVM的验证框架，通过CVM验证框架验证了一个实际运行的操作系统内核。该验证框架包括了较为完整的操作系统组件、内存、外设、处理器的形式化语义以及通过验证的C0编译器。操作系统的主要部分都是由C0语言编写的，运用霍尔逻辑将由C0编写的内核代码和应用代码在源代码层上进行验证。Verisoft-XT项目使用由微软研究院研发的推理证明工具VCC对PikeOS进行了形式化的验证，通过在源代码层面上添加注释代码（Annotated
Code）可用来验证并发的C代码程序。

##  **03** **mCertiKOS的形式化验证**

美国耶鲁大学Flint研究组是在Zhong
Shao研究团队的带领下一直研究对操作系统进行形式化验证。研究团队运用Coq工具对其自行开发的mCertiKOS操作系统进行了端到端的完整的形式化验证[3]，其中mCertiKOS是特定为了用于形式化验证而从CertiKOS的基础上进行精简而来的。该项目组借助于CompCert编译器的拓展版本CompCertX将C原语进行可信编译，采用分层抽象并在相关的抽象层上建立观测函数的方法，将mCertiKOS内核中的C和汇编的混合代码进行了完整的验证，其架构如图2所示。

![2.png](https://image.3001.net/images/20220802/1659417925_62e8b5450d1b1c93c60d9.png!small)

图2 基于混合语言的操作系统的验证

  

##  **04** **xv6操作系统内核的形式化验证**

美国的华盛顿大学Hyperkernel项目则是基于对一个类Unix的教学操作系统名为xv6内核的接口程序进行了一键式的自动化形式化验证，该项目组所验证的内核代码是由纯C语言编写而成的，包括了系统调用、异常处理和中断代码。首先去除掉了所有的循环和递归；其次内核运行在用户空间下彼此分离的地址空间；然后他们将C语言代码转化为了中间表达语言LLVM；最后运用Z3
SMT自动求解器对LLVM语言上进行端到端的全自动化验证，其架构如图3所示。

![3.png](https://image.3001.net/images/20220802/1659417926_62e8b5462a3a69d362c39.png!small)

图3 Hyperkernel的开发流程

  

##  **05** **µC/OS-II的形式化验证**

中国科技大学的冯新宇团队，他们是国内首个对一个商用的操作系统内核µC/OS-II进行了较为完整的形式化验证[4]，其验证框架如图4所示。他们的工作采用了基于依赖/保证关系的并发程序证明方法，在保证多任务可组合的前提下，将多任务程序的精化证明分解为单任务的精化证明，从而减小了证明难度。对于内核中的汇编程序，该工作将其封装并抽象为高级语言（C
语言）原语。验证工作是在定理证明工具Coq中实现的，使用约22万行验证脚本代码验证了3450行操作系统内核实现代码。

![4.png](https://image.3001.net/images/20220802/1659417927_62e8b5473144e19d41dc0.png!small)

图4 mC/OS II验证框架

##  **06** **ARINC653的形式化验证**

北京航天航空大学赵永望团队建立了符合ARINC653的分区内核模型，该模型实现了ARINC653的完整功能和接口，在该项目中他们采用了Event-B对系统所有的功能和服务进行了形式化的建模，并利用精化方法和功能规范进行了安全性分析与验证[5]，其架构图如图5所示。采用基于精化的方法建立了两层规范模型，其高层模型主要用来描述内核初始化、分区调度、分区间通信等系统层面行为，精化模型则以进程为单位，描述进程调度和进程管理等机制。他们的工作验证了ARINC
653标准和基于该标准的一些操作系统源码的安全（Security）性，并发现了ARINC 653标准中潜在的进程内信息泄露等缺陷。

![5.png](https://image.3001.net/images/20220802/1659417929_62e8b5492242b42ceb00a.png!small)

图5 ARINC653形式化验证框架

##  **07** **AUTOSAR OS的形式化验证**

AUTOSAR规范是目前被广泛应用的车载操作系统规范之一，旨在为汽车电子体系架构建立统一的开放工业标准。华东师范大学研究团队分别使用PAT、K框架等形式化验证工具对基于AUTOSAR规范的操作系统的总线通信协议、调度机制、中断机制、内存管理机制等部分进行了验证。

研究团队采用基于时间的进程代数对AUTOSAR操作系统总线协议进行了形式化描述，并应用PAT工具自动化验证了总线协议的安全性、公平性、无饥饿性等性质。

团队应用K框架验证AUTOSAR操作系统中任务调度、中断管理等模块的实时特性。K是用于描述程序语言操作语义的形式化语言，通过定义操作语义可以执行对应的代码，从而达到代码分析与验证的目的。借用该思想，团队在K下定义了AUTOSAR中API的操作语义，进而搭建了一个形式化的AUTOSAR系统，在该系统上可以“执行”其应用，分析与验证应用的正确性。

作为基础软件的操作系统，其安全性将会影响到整个软件系统的安全性，如何保证其安全性，本文从形式化方法的角度讨论了目前国内外的研究状况。

 **作者 | 郭建 上海控安可信软件创新研究院特聘专家**

  

 **参考资料：**

> [1] Gerwin Klein,etc.seL4: Formal Verification of an Operating-System
> Kernel. DOI :10.1145/1743546.1743574.
>
> [2] BECKERT B, MOSKAL M. Deductive Verification of System Software in the
> Verisoft XT Project[J]. KI, 2010, 24(1) : 57–61.
>
> [3] Costanzo D, Shao Z, Gu R. End-to-end verification of information-flow
> security for C and assembly programs[J]. ACM SIG***N Notices, 2016, 51(6):
> 648-664.
>
> [4] Fengwei Xu, Ming Fu, Xinyu Feng, Xiaoran Zhang, Hui Zhang, Zhaohui Li: A
> Practical Verification Framework for Preemptive OS Kernels. CAV (2) 2016:
> 59-79.
>
> [5] Y. Zhao, D. Sanán, F. Zhang and Y. Liu, "Refinement-Based Specification
> and Security Analysis of Separation Kernels," in IEEE Transactions on
> Dependable and Secure Computing, vol. 16, no. 1, pp. 127-141, 1 Jan.-Feb.
> 2019, doi: 10.1109/TDSC.2017.2672983.
>
> [6] Jizheng Ding, Xiaoran Zhu, Jian Guo. “End-to-End Automated Verification
> for OS Kernels”, The 25th Asia-Pacific Software Engineering Conference
> (APSEC)：2018，139-148, Nara, Japan, December 4-7, 2018.
>
> [7] Rongkun Yan and Jian Guo, “Timing Modeling and Analysis for AUTOSAR OS
> Schedule Tables”, Hase 2019：123-130，2019-01-03, Hangzhou, China.
>
> [8] Xiaoran Zhu , Min Zhang , Jian Guo, Xin Li, Huibiao Zhu, and Jifeng He
> Toward a Unified Executable Formal Automobile OS Kernel and Its
> Applications，IEEE TRANSACTIONS ON RELIABILITY, VOL. 68, NO. 3：1117-1133，
> SEPTEMBER 2019.

