**近日，美国四所大学的一组学者发现了全新的旁路攻击方法，他们能够利用现代CPU中的推测执行功能来获取用户CPU数据，泄漏敏感数据和数据安全边界。这种旁路攻击方法与今年年初的
Meltdown 和 Specter 漏洞利效果相似，但研究人员这次利用的是CPU推测执行功能中的一个新片段。**

![BranchScope.png](https://image.3001.net/images/20180328/15222047762058.png!small)  

## BranchScope 与 Spectre variant 2 十分相似

来自威廉玛丽学院、卡内基梅隆大学、加州大学河滨分校和宾厄姆顿大学的研究人员将这一新技术命名为 BranchScope
。这种在攻击方式上主要针对“分支预测”行为，这个特点与 Spectre 变体2（CVE-2017-5715）的漏洞利用方法十分相似。但Spectre 变体
2利用的是分支的目标缓冲区域（Branch Target Buffer），BranchScope 利用的是模式历史表（Pattern History
Table）。

BranchScope 方法可以让攻击者取代 CPU
进行指令执行的决策。在这种方式之下，攻击者可以在计算机的特定区域上获取敏感信息。目前，研究员已经成功在因特尔处理器上通过了漏洞利用复现测试。

![Microsoft-Intel-Meltdown-Spectre-patches.jpg](https://image.3001.net/images/20180328/15222073431683.jpg!small)  

## BranchScope 已在 Intel 处理器上实现利用

学术界表示，BranchScope
是第一个针对“分支预测”的旁路攻击方法，并且该技术也可用于检索存储在SGX的内容（英特尔CPU的安全区域）。攻击者不需要逆向设计分支预测器操作的细节，只需要从用户空间的预测执行状态进行简单的操作，BranchScope方法也可以扩展到攻击SGX飞地上。  

研究团队在实例测试中对 Intel x86处理器进行了漏洞利用，如Sandy Bridge，
Haswell，以及Skylake。攻击者只需要具备用户权限即可开始执行漏洞利用过程，失败概率小于1%。

这种全新的攻击手段目前还没有应对方案。之前 Spectre 漏洞补丁无法应对这次的 BranchScope 攻击。

但据研究团队表示，针对 BranchScope 攻击进行安全补丁的修复应该不是难题——仍然需要从软件和硬件层面进行双重的修复工作。

![jobs-sites-intel-sign-3x1.jpg.rendition.cq5dam.webintel.960.320.jpg](https://image.3001.net/images/20180328/15222073161270.jpg!small)  

英特尔发言人表示，

>
> 我们正在在与这些研究人员合作，目前已经了解到这个漏洞的细节信息了。我们预计现有的软件修复措施，可用于已知的旁路攻击，我们相信与研究界的密切合作会是保护客户及其数据的最佳途径之一。我们很感谢研究团队为之的努力工作。

 **研究团队的研究结果 “BranchScope:A New Side-Channel Attack on Directional Branch
Predictor”[[1](http://www.cs.ucr.edu/~nael/pubs/asplos18.pdf),2]
会在第23届ACM国际编程语言和操作系统架构会议 (ASPLOS 2018)上公开。**

## 软件及硬件解决方案

针对这个漏洞，研究者也提出了从软件或者硬件方面进行的缓解方案：

### 1、软件方面缓解

通过算法移除依赖于秘密数据的分支结果，这种技术被称为if-conversion，是一种编译器优化技术。它使用条件指令（如cmov）将条件分支转换为顺序代码，有效地将控制依赖关系转化为数据依赖关系。通过移除条件分支指令，从而缓解BranchScope攻击。然而，将这种保护机制应用于大型代码库是很困难的，只能局限于使用敏感数据的程序的关键部分。

### 2、硬件防御

通过对分支预测器的结构进行重新设计也可缓解这个攻击，具体的缓解措施包含：

 **(1)PHT随机化**

BranchScope需要在PHT（模式历史表，pattern history
table）中创建可预测的冲突(例如，基于虚拟地址)。为了防止这种冲突，可以修改PHT索引函数作为该软件实体唯一的输入数据。这可以作为SGX硬件状态的一部分，也可以是进程生成的一些随机数。一次随机化容易受到探测攻击，因此可使用周期性的随机化（这会牺牲一些性能），这个解决方案类似于将缓存映射的随机化作为防止侧信道攻击的保护。尽管这种缓解技术具有负面的性能开销，但它为大多数安全敏感分支提供了完美的安全保护。

 **(2)BPU分区**

BPU（branch prediction
unit，分支预测单元）分区可使攻击者和受害者不共享相同的结构。如，SGX代码可使用不同于普通代码的分支预测器，或者结构支持BPU私有分区，通过分区，攻击者失去了与受害者产生冲突的能力。

 **(3)其它解决方案**

除了以上的缓解措施，也可通过移除或增加性能计数器的噪声或测量时间来消除攻击者测量分支结果的准确能力。另一种方案是更改有限状态机（FSM，FiniteState
Machines），使其更随机，从而干扰攻击者推断受害者分支方向的能力。最后一种解决方案主要在于探测攻击的痕迹，如果检测到正在进行的攻击，可冻结或者杀死攻击者的进程。在SGX中攻击者如果已经破坏了操作系统，这样就比较难办，检测到攻击程序正在进行时，需要SGX代码重新映射自身或停止执行。

***参考来源：[bleepingcomputer](https://www.bleepingcomputer.com/news/security/academics-discover-new-cpu-side-channel-attack-named-branchscope/)，
Elaine、JingleCats编译整理，转载请注明FreeBuf.COM**  

