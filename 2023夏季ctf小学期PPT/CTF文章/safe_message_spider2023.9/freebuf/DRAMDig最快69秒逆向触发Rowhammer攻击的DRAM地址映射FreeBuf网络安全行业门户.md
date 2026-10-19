**谈到Rowhammer攻击，整个安全行业一定都不陌生，2014卡内基梅隆大学宣布发现一种存在于动态随机储存器（下称DRAM）的漏洞，借助这项漏洞，攻击者可以通过反复加载内存的特定行来实现账户提权，研究一经发表，便掀起业内极大轰动，因为这表明了不管是PC、手机，不管操作系统是Linux、Windows··，几乎所有搭载DRAM内存的X86构架CPU的设备都会都会存在安全隐患，影响不言而喻。**  

本文介绍了DRAM address
mapping逆向工具——DRAMDig，能够在平均7~8分钟时间（最快仅需要69秒），快速、可靠地逆向出DRAM地址映射 ——
Rowhammer攻击实现的关键步骤。该工具可用来评估个人主机、云计算基础设施是否受到Rowhammer攻击的威胁。

那么，究竟颠覆攻击逻辑的Rowhammer到底是什么？安全研究员新研究设\\]]]]\\]]]]]计的映射逆向工具DRAMDig，又是如何快速、可靠地逆向出触发Rowhammer攻击的DRAM地址映射？

##  **一** **、“一招通杀”所有设备 —— Rowhammer攻击原理**

从硬件角度来看，计算机就是一个庞大的集成电路，由大量的电子管、继电器和各种电气元件组合而成。其中用来存储信息用的物理内存，就是我们上面提到的DRAM。就像去图书馆找一本书，你需要通过书的类型和编码，定位到它在哪一个书架，哪一排，哪一格，DRAM里想要找到存储的某一数据，也有一套明确的访问路径：channel
→DIMM → rank → chip → bank → cell。所以，计算机内存就是由无数个内存存储单元（下简称cell）构成的电路板。

![image.png](https://image.3001.net/images/20200422/15875359251875.png!small)

_图1. 内存存储单元cell结构_

cell由一个晶体管和一个电容组成，就像一个小电池，每个cell存放1
bit数据，而计算机里所有的内容，本质上都是一堆数据编码，都可以用类似01010101001这样的二进制来表达 ——
体现在cell上，晶体管通电状态表示1，不通电状态表示0。所以说，不管你在电脑里存放的文档、照片，下载的游戏、音乐程序，亦或是计算机本身的操作系统，其实归根结底都是通过一定规则存储在cell里的“0”或“1”。

然而近年来，随着人们生产生活对计算机存储的需求要求更高，设备厂商在不改变内存电路板面积大小的前提下，让其能够存储更多的数据，只能将cell的设计越做越多，排列越来越近，密度大幅度增加，虽然制作工艺有所提升，但还是会存在一种假设，那就是相邻的cell在运行中可能会受到干扰，如果频繁“轰炸”某两行（行话称之为row），就可能会造成中间一排腹背受敌、上下夹击，从而出现比特位翻转，也就是0变成1，1变成0...

业内把这种上下敲击的疯狂操作，称为double-sided Rowhammer
test，而导致比特位翻转的这个攻击方式就叫做Rowhammer攻击，Row是行，Hammer是反复敲击，如此简洁明了，一针见血。

当然如果只是单纯的疯狂改写数据，以此来搞破坏也过太小看Rowhammer攻击的威力了，其实攻击者的深层目标是利用Rowhammer攻击来提升账号权限，获得通往各路关卡的“通行证”。此前就有学者发现，通过rowhammer可以打破进程间隔离，user-kernel隔离，VM间隔离以及VM-VMM间隔离，从而获得更多系统权限。

再举个例子，有攻击者企图获取你的网银支付密码，但此类程序开发者为了安全起见，都会将诸如密码、身份证号等核心数据，设立重重关卡，存放在金字塔的顶端，除了用户自身，其他人无法触及。而有了Rowhammer攻击，虽然被设立关卡，攻击者却可以绕过这些，选择通过更底层去找到储存核心数据的cell，然后反复敲击其“隔壁邻居”，引起比特位翻转，来实现最终获取支付密码的目的。

##  **二** **、“说起来容易做起来难” —— Rowhammer攻击难点**

读到现在，你是不是会有一个这样的疑问，计算机内存里密密麻麻分布着cell，即使理解了Rowhammer攻击的操作手法，如果不知道哪些cell里隐藏着账号提权的核心线索，一顿轰炸操作无异于随机“抽盲盒”，能不能找到关键全靠运气。

所以很长时间以来，对于Rowhammer攻击的研究只停留在理论阶段，归根结底原因是：找到那最为关键的两个row实在是太难了！

专业上，定位到最关键的两个row需要解决的核心问题，是要找出DRAM核心数据所在的DRAM地址，其实也就是逆向DRAM地址映射（下简称DRAM
address mapping）的过程。

上文我们讲到过，在计算机里，不管是什么类型的文件、信息、数据，最终都会以0101011的形式被存储在内存里，程序运行中需要访问到这些数据，只能通过虚拟地址来访问。这些虚拟地址在操作系统中首先转换成物理地址，然后物理地址再通过CPU中的Memory
Controller转为为DRAM中的地址。物理地址与DRAM中地址的映射关系是一段未公开的“咒语”，需要逆向分析来解决。

对此，安全研究员调研了的目前行业公开的所有DRAM address
mapping逆向工具并做了分析，结果显示这些工具的表现并不尽如人意，或是无法通用于各类型号的CPU，或是操作时间过长，需要数小时的时间，还有的甚至检测多次，得出的结果前后不一致。

而此次安全所研究设计的DRAM address mapping逆向工具——DRAMDig，
能够在平均7~8分钟时间（最快仅需要69秒），快速、可靠地逆向出DRAM地址映射，并且通用于包括Non-ECC
DDR3\DDR4内存条，以及当前市面上流行的Intel CPU（Sandy Bridge ~ Coffee Lake）。

##  **三** **、“更经得起推敲”—— DRAMDig 工具核心原理**

目前已有逆向工具（如DRAMA）无法稳定、快速、准确逆向出DRAM address
mapping，主要有如下几个方面原因。首先，已有工具对DRAM自身信息挖掘不到位，比如缺乏对bank数目、row/column位数的理解；其次，已有工具中存在物理地址盲目的随机选取，导致逆向结果不稳定、不准确，同时存在大量的穷举操作，导致较大时间开销；最后，已有工具对interleaved
mode形式的DRAM address mapping逆向能力有限。

由安全研发的新型DRAM address mapping映射逆向工具——DRAMDig，提出了Domain-knowledge
assisted的方案，能够充分挖掘、利用已有的knowledge来辅助逆向，使得最终得到的逆向结果准确、稳定、快速。Domain
knowledge包括三个方面：

> 1）DDR3/DDR4 Specification。我们从Specification中能够获取有关DRAM row/column bits的确切数量；
>
> 2）系统信息。通过程序来获取DRAM中bank数量，系统的物理内存大小（物理地址中有效地址位数）等信息；
>
> 3）经验观察。我们认为Intel CPU上的bank寻址采用的是线性XOR计算方式，参与XOR计算的是物理地址中的特定bits（称之为bank
> bits）。例如，在某款Intel CPU，以及一个包含8个bank的DRAM的设定下，bank寻址函数表示为：(BA0, BA1, BA2)。其中，

![image.png](https://image.3001.net/images/20200422/15875360824345.png!small)

DRAM address mapping逆向目标是确定物理地址到DRAM中地址的映射关系。包括两个方面，第一，还原物理地址中bits的角色，即哪些是row
bits，column bits和bank
bits；第二，确定bank寻址函数。图3描述了DRAMDig的工作流程。在介绍具体流程之前，我们首先简要介绍一个DRAMDig逆向所依赖的一个基本操作原语，它是DRAMDig工作的基石。

![image.png](https://image.3001.net/images/20200422/15875359706005.png!small)

_图2. DRAMDig 逆向流程_

这个操作原语是一个timing channel。具体而言，这个timing channel是由同一DRAM bank中的row
buffer冲突引起的。DRAM中每个bank都有一个row
buffer来缓存最后访问到的row。如果一对地址在同一bank的两个不同row中，交替访问它们时row
buffer将反复重新加载、清除这两个row，导致row buffer 冲突。而如果两个地址位于同一row或不同bank中，访问这两个地址时不会发生row
buffer 冲突。显然发生row
buffer冲突情况下，也就是两个地址在同一bank不同row时，得到的latency更大。因此，根据两个地址的latency测量结果的高低，可以判断它们是否在同一bank不同row。

在这个操作原语基础之上，我们来简要介绍DRAMDig的逆向流程。主要分为三个阶段。

> 第一阶段，精心选取多对物理地址，利用timing channel进行latency测量，根据测量结果对row、column和bank
> bits范围进行初步的划分。首先从高到低考察物理地址中每个bit，选取仅有这个bit不同的两个物理地址测量latency。如果是high
> latency，则说明它们在同一个bank不同row，当前只有1个bit不同，所以这个bit是row bit。然后选定1个row bit和一个非row
> bit，再选取仅有这2 bit不同的物理地址测量latency。如果是high则说明它们在同一bank不同row，这个非row bit不会是bank
> bit，而是column bit。这样两轮测量之后能够得到row bits和column bits的位置范围，剩余的bits是bank bits。
>
> 第二阶段，选取覆盖bank bits所有取值情况的物理地址，再次利用timing
> channel来测量latency。将latency为high的地址划分到一堆，最终这些物理地址将被划分为#bank堆，同一堆物理地址都在一个bank中，而且每一堆的物理地址个数大致相同。然后依次在每堆中考察bank
> bits之间的XOR组合情况，找出堆中所有物理地址都满足的bits
> XOR方式，作为候选bank寻址函数。在所有地址堆都考察完毕后，将候选bank寻址函数进行消元处理，得到最终的bank寻址函数。
>
> 第三阶段，确定具有多重角色的bits，这是由于存在interleave mode的寻址情况，例如，有些bit既是row bit也是bank
> bit，有些bit既是column bit也是bank bit。还原多重角色row
> bits的方式是，考察2-bit的bank寻址函数，选取仅有这2个bit不同的两个物理地址，测量它们的latency。如果测量结果是high
> latency，则认为高位bit是row bit。对于多重角色的column bits，根据Domain
> knowledge和第一阶段的还原结果，能够获知未还原的column bits数量（N）。在已还原出column
> bits的位置基础上，按照从低到高的顺序，将未还原数量（N）的bits认为是column bits。

由于DRAMDig选取了覆盖所有bank
bits取值情况的物理地址，不但能够真实且完整揭示bank寻址方式，而且能够根据latency测量结果将这些地址均匀地划分到#bank堆，保证了bank
寻址函数还原结果的准确性和稳定性。另外，DRAMDig仅需要在bank
bits空间内的寻找bank寻址函数，不需要在所有bits空间内穷举，大大降低了时间开销。

据介绍，利用DRAMDig在9台具有不同CPU和内存设定的机器上进行了DRAM address
mapping逆向实验。实验结果如表1所示。可以看到，实验的CPU涵盖Sandy Bridge、Ivy Bridge到Coffee
Lake等多个新老微架构（Microarch.），内存条涵盖DDR3和DDR4 (DRAM Type,Size)，和包含多种DRAM设定方式（DRAM
Config）。

![image.png](https://image.3001.net/images/20200422/1587536109705.png!small)

_表1. DRAMDig在9个不同机器设置上的逆向结果_

其中Config表示如下参数：#channel，#DIMM/channel，#rank/DIMM，#bank/rank.

在这些逆向实验中，最多需要17分钟，最少需要69
秒可以获得逆向结果，如图4所示。相比较逆向工具DRAMA而言，DRAMDig具备更短的时间开销。其中，在第3和第7台机器中，DRAMA花费了将近2小时都没有输出逆向结果。此外，百度安全研究员在实验中发现，运行DRAMA多次，很大几率会出现每次逆向结果都不相同的情况，因此DRAMA在逆向结果的准确性和稳定性方面均无法保证。

![image.png](https://image.3001.net/images/20200422/1587536136759.png!small)

_图3. DRAMDig和DRAMA逆向时间开销（单位：秒）_

在获得逆向结果基础之上，为进一步验证，百度安全研究员还在多台机器上进行了double-sided
Rowhammer测试，并且和DRAMA进行了对比。使用两个工具在不同的机器上分别进行了5次测试，每次测试5分钟，最后统计bit翻转的数量。可以从表2中看到，DRAMDig能够产生更多的bit
flips。有一些测试中DRAMA甚至没有出现翻转，而DRAMDig敲出了翻转，这也能够说明DRAMDig逆向结果的正确性。由此可见，准确的逆向DRAM
address mapping对bit翻转具有很重要的影响，对Rowhammer威胁评估具有非常关键的作用。

**Machine** |  **T1** |  **T2** |  **T3** |  **T4** |  **T5** |  **Total**  
---|---|---|---|---|---|---  
No.  |  DRAMDig / DRAMA  |  |  |  |  |  
No.1  |  296 / 197  |  418 / 179  |  226 / 177  |  627 / 259  |  484 / 286  |
2051 / 1098  
No.2  |  959 / 240  |  934 / 0  |  976 / 18  |  1039 / 947  |  955 / 670  |
4863 / 1875  
No.5  |  12 / 7  |  12 / 0  |  12 / 0  |  10 / 0  |  11 / 0  |  57 / 7  
  
表2. DRAMDig和DRAM执行5次double-sided rowhammer测试，每次测试持续5分钟。DRAMDig比DRAMA产生了更多的bit
flip。

结语：毫无疑问，DRAMDig的诞生，大大提升了对DRAM address
mapping逆向的效率和准确性，对于高效评估个人主机、云计算平台等基础设施是否受到Rowhammer攻击的威胁有着重要意义。对于硬件厂商修复Rowhammer漏洞，提升芯片制作工艺，也提供了新的思路。据悉，百度安全正在计划将DRAMDig开源。同时，百度安全也开放自身顶尖技术能力，以开放共享的姿态，欢迎整个行业上下游携手一道，打破技术壁垒，推进安全生态建设，保护数据隐私安全。

 ***本文作者： 百度安全实验室，转载请注明来自FreeBuf.COM**  
  

