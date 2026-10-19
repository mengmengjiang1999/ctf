**作者 |** 郭建 上海控安可信软件创新研究院特聘专家

 **版块 |** 鉴源论坛 ·
观模汽车工业发展至今，硬件方面如车身材料、发动机等已无太大升值空间，而汽车电子则有着广阔的前景。为此各大汽车厂商对汽车电子的研究都投入了大量的人力财力。2003
年，汽车开放系统架构AUTOSAR（AUTomotive Open
SystemArchitecture）由全球汽车制造商、部件供应商及其他电子、半导体和软件系统公司联合建立，主要目标是为汽车软件体系架构建立一个开放的、标准化工业标准，以同时满足供应商和生产商之间的需求。AUTOSAR
通过控制复杂度不断增长的汽车电子体系架构，将软件从硬件中分离开来，允许软件的重用，从而减少二次开发和验证的成本。AUTOSAR包括了汽车电子功能划分、统一软件架构和软件开发过程等整套基于汽车电子开发的方法学。  
CAN、TTCAN、LIN、FlexRay等是可用于汽车内部网络通信的协议。在现阶段CAN及TTCAN协议因其稳定可靠、结构简单、通信灵活等特点而最常被使用。基于AUTOSAR的网络协议规范已有很多被发布。如基于AUTOSAR的CAN协议、基于AUTOSAR的TTCAN协议等，这些规范详细阐述了在AUTOSAR规范下该网络协议的驱动及接口规范，隐藏了底层网络通信的细节，向上层应用软件提供调用底层服务的接口。通过这种方式使软硬件分离，使上层软件的开发更为灵活，对功能的扩充更方便，缩短了开发周期。  
 **本文针对AUTOSAR的TTCAN协议进行研究，并用Timed CSP（Timed Communication Sequential
Processes）形式化语言对其进行建模，通过LTL（linear temporal
logic）及断言（Assertion）对TTCAN模型需要满足的性质进行描述，运用模型检验工具PAT完成了对模型的验证。**  
  

##  **01** **AUTOSAR体系架构**

AUTOSAR的主要目标是为汽车电子创建一个开放的、标准化的软件架构，
这个架构有利于车辆电子系统软件的交换与更新，并为高效管理愈来愈复杂的车辆电子软件系统提供了一个基础。此外，AUTOSAR在确保产品及服务质量的同时，提高了产品研发的效率。AUTOSAR定义了设计汽车系统的方法和描述它们的软件的架构方式。图
1 展示了AUTOSAR软件分层体系架构。

![图片](https://image.3001.net/images/20221230/1672378023_63ae76a72a8ba17d7ec7c.png!small)

图1 AUTOSAR软件分层体系架构

 **应用层（application layer）** 包含了实现所需功能的软件组件SWC（SoftWare
Component）的规约，它形成了OEM（Original Equipment Manufacturer）厂商之间的竞争基础。  
 **运行时环境层 RTE（RunTime Environment）** 为应用软件提供了通信服务，它使
AUTOSAR的软件组件独立于特定的ECU。RTE是虚拟功能总线VFB（Virtual Function
Bus）的一个实现，不指定用来交换数据的通信技术。因此，AUTOSAR可用LIN、CAN、TTCAN或者FlexRay等多种通信平台。用VFB定义软件组件的数据交换可使它们独立于底层的硬件平台，此外，可以使注意力集中到软件组件之间的通信而不用关心数据是否在ECU
内部或ECU之间传输。  
 **基础软件层BSW（Basic SoftWare）** 由服务层、ECU抽象层、复杂驱动层和MCU（Micro Controller
Unit）抽象层等子层组成。服务层处于基础软件层的顶层， 包含了操作系统、汽车网络通信、管理服务、内存服务和诊断服务。ECU
抽象层包含了输入输出（I/O）和通信硬件抽象，它使更高的软件层独立于ECU 硬件组件。复杂驱动层是硬件和 RTE
之间的桥梁，它提供与AUTOSAR无关的、专用的功能，如设备驱动等。MCU抽象层处于基础软件层的最底层，它包含了直接访问的微控制器内部设备的驱动和内存映射的微控制器外部设备的驱动。

##  **02** **AUTOSAR的TTCAN协议**

基于AUTOSAR的网络通信协议位于体系架构的基础软件层中，AUTOSAR为其提供接口的规范。TTCAN协议在AUTOSAR基础软件层的接口，位于通信硬件抽象层和通信服务层之间，是为上层通信层提供
TTCAN 协议驱动服务的接口。图 2 是AUTOSAR规范下的
TTCAN协议层次的架构。TTCAN协议接口模块是CAN接口模块的扩展，它包含了TTCAN协议所有与硬件独立的任务。

![图片](https://image.3001.net/images/20221230/1672378172_63ae773c894919eb2f0f4.png!small)

图2 AUTOSAR规范下的TTCAN协议层次架构

TTCAN协议接口主要完成上层通信层对控制流和数据流的需求，比如：消息传输需求、消息传输确认、消息接收指示、出错通知等。TTCAN协议接口的一个典型流程是，接收来自上层通信层的消息请求，通过TTCAN协议驱动传输给
TTCAN协议控制器完成消息的传输，然后向上层通信层返回消息成功传输的确认。TTCAN协议接口为TTCAN协议网络的控制和服务提供了访问低层服务的通信抽象，通过接口将TTCAN协议状态，管理器的状态变化请求推送到底层的TTCAN协议驱动，然后底层事件再通过接口推送到高层相关的网络管理模块。  

## **03** **基于AUTOSAR的TTCAN协议的形式化建模与分析**

AUTOSAR规范下TTCAN协议的抽象主要为三个层次。 **一是应用层** ，即软件组件层，包含了各种软件组件消息传输请求的序列，对应于 TTCAN
协议的系统矩阵。 **二是运行时环境层** ，对上层应用层隐藏了下层的通信细节，实现虚拟功能总线，是对TTCAN协议通信通道的抽象。 **三是基础软件层**
，即TTCAN通信网络所处位置，完成TTCAN协议基本的通信功能，即节点消息传输、总线仲裁和错误处理功能。

![图片](https://image.3001.net/images/20221230/1672378220_63ae776cee22c90aec799.png!small)

图3 基于AUTOSAR的TTCAN协议抽象

图3描述了基于AUTOSAR的TTCAN协议抽象，运行时环境层可以接收来自于软件组件的任何数据请求，通过内部的接口调用底层基础软件的通信功能，完成消息的传输。在AUTOSAR软件体系架构中，位于运行时环境层之下的基础软件层对于应用层来说是不可见的，因此，基础软件层可采用不同的通信协议来完成通信功能。基于AUTOSAR的TTCAN协议则是在基础软件层中采用了TTCAN协议来进行消息的传输。

![图片](https://image.3001.net/images/20221230/1672378237_63ae777d599377528bdc7.png!small)

图4 TTCAN协议与基于AUTOSAR的TTCAN协议的关系

图4简单描述了这两者之间的关系。AUTOSAR规范中定义了一系列TTCAN协议的接口，通过对这些接口的实现完成TTCAN协议的各种功能。本文主要研究TTCAN协议中节点消息传输、总线仲裁和错误处理的功能如何在AUTOSAR规范下实现，并可通过定义的接口进行调用，从而完成消息的传输。

对TTCAN协议和基于AUTOSAR的TTCAN协议进行分析、形式化建模和验证的研究框架如图 5 所示。该框架主要分为三个阶段：

![图片](https://image.3001.net/images/20221230/1672378253_63ae778d2724ca323887f.png!small)

图5 基于AUTOSAR的TTCAN协议建模与分析框架

 **第一阶段**
对TTCAN协议的需求进行分析，对于消息传输相关的四个主要部分系统矩阵、节点消息传输、总线仲裁及错误处理进行抽象，并分析这四个部分之间的关系以及消息的传输过程。分别对这四个部分进行形式化的描述，以Timed
CSP建立模型。同时，在这一阶段，分析并提取TTCAN协议中死锁、安全性、不变性及公平性等相关的性质，以LTL公式及断言的形式描述并加以文字注释说明。  
 **第二阶段**
根据AUTOSAR软件体系架构和基于AUTOSAR的TTCAN协议规范，在TTCAN模型的基础上，将其迁移至AUTOSAR，这一过程关键之处在于明确TTCAN模型各功能模块应处于AUTOSAR体系结构的哪一层次。然后在分析的基础上，以Timed
CSP建立基于AUTOSAR的TTCAN层次模型，该模型包含了软件组件、运行时环境和基础软件三个层次。其中，软件组件实现TTCAN协议模型中系统矩阵的功能，为系统提供消息传输请求的列表；运行时环境为上下层之间的通信提供了虚拟功能总线，包含了多种接口以供上层模块调用底层通信服务，是对TTCAN协议模型通信通道的抽象；基础软件包含了TTCAN协议模型中的节点消息传输、总线仲裁和错误处理模块，提供消息传输的服务。最后对模型进行性质的提取，提取的性质不仅需要满足TTCAN协议的需求，还要满足AUTOSAR规范的需求。  
 **第三阶段** 是模型的实现和性质的验证阶段。模型检测工具PAT支持并发实时系统建模、模拟以及推理，支持Timed
CSP建模语言，同时也支持LTL公式及断言描述性质。因此，以PAT实现模型，使模型能得到准确的描述。建模实现的同时，对前两个阶段中提取的性质在工具PAT中进行验证，并对验证结果进行分析。图6所示的是在PAT上模型实现的部分代码，图7给出了PAT对模型的验证结果。

![图片](https://image.3001.net/images/20221230/1672378281_63ae77a91168c27c42932.png!small)

图6 模型在PAT中的实现

![图片](https://image.3001.net/images/20221230/1672378297_63ae77b9b47f22354b907.png!small)

图7 基于AUTOSAR的TTCAN协议模型性质验证结果

##  **04** **小结**

AUTOSAR规范的提出为高效管理愈来愈复杂的汽车电子提供了一个基础。AUTOSAR通信栈位于运行时环境（RTE）与微控制器抽象层（MCAL）之间，其简化ECU之间的通信服务，实现不同类型或速率总线间的数据交互，并对应用层隐藏了与总线相关的协议和报文的属性。本文针对AUTOSAR
的TTCAN通信协议进行了研究，实现其形式化建模与分析。

参考文献：

[1] Specification of Operating System
https://www.autosar.org/fileadmin/user_upload
/standards/classic/21-11/AUTOSAR_SWS_OS.pdf.

[2] Bunzel S. AUTOSAR - the Standardized Software Architecture.[J]. Informatik
Spektrum, 2011, 34(1):79-83.

[3] Barthe G, Pardo A, Schneider G. SEFM: software engineering and formal
methods[J]. Software & Systems Modeling, 2015, 14(1):3-4.

[4] 冉钦文，基于AUTOSAR 的汽车电子通讯协议的研究[D]. 华东师范大学,2015.

[5] ISO 11898- Part4, Road vehicles - Controller area network (CAN) - Part 4:
Time triggered communication. 2004.

[6] Skoglund M, Svensson H, Eriksson H, et al. Checking Verification
Compliance of Technical Safety Requirements on the AUTOSAR Platform Using
Annotated Semi-formal Executable Models[M]//Computer Safety, Reliability, and
Security. Springer International Publishing, 2014: 19-26.

[7] Ahmed M. Hamed, M. Watheq El-Kharashi, Ashraf Salem, Mona Safar: A
Multicycle Pipelined GCM-Based AUTOSAR Communication ASIP. IEEE Access 10:
46312-46329 (2022).

