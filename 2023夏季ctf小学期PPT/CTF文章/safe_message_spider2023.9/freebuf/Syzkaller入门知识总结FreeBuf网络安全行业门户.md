Linux 内核 fuzz目前最流行的工具是 syzkaller，该工具是 2015 年前后由 Google 开源，和 AFL 一样，也是具有划时代意义的
fuzzer，发现的内核漏洞不计其数，并且衍生了很多工具。

之前我们已说过 syzkaller 的详细用法，但对于入门来说，还是不够全面。犹记得第一次接触 syzkaller
时，看到网上各类文章，还是觉得一头雾水，不知道 syzkaller 用于内核 fuzzing 的整体步骤。本篇博客就是想告诉新手，什么是
syzkaller？使用 syzkaller 进行 fuzzing 的步骤有哪些？syzkaller 到底是黑盒还是白盒测试？使用 syzkaller
的条件是什么？...

## Syzkaller

### 概念

syzkaller 是一个基于覆盖引导（coverage-guided），能够对 **内核** 进行 fuzz 的 **白盒**
测试工具。syzkaller 本身支持多种系统调用，但是针对驱动进行 fuzz，主要关注
`open`、`read`、`write`、`ioctl`、`mmap`。

### 疑问

什么是覆盖引导（ **coverage-guided** ）？

  * 覆盖引导，即 **通过向目标程序插桩，统计代码覆盖，反馈给模糊测试引擎（fuzzer，即模糊测试工具），反馈信息用于变异种子，生成更高质量的输入，使得 fuzzer 能够用更好的输入让被测程序达到更高的代码覆盖率。**

  * 对于每个目标，fuzzer 都会构建一个输入的语料库，随着 fuzzer 通过变异语料库发现新的输入，覆盖率会不断增长。常见的模糊测试引擎（fuzzer，即模糊测试工具）有 afl、honggfuzz、libfuzzer 以及本次所说的 syzkaller，这些都是经典的 fuzzing 工具。

使用 syzkaller 条件是什么？

  * 必备材料：内核源码 + go 语言环境 + syzkaller 源码

  * 需要编写： **系统调用描述** 文件（syscall description）、 **配置文件** （configuration）

  * 需要编译：内核、系统调用描述及 syzkaller

需要编译哪些代码或文件？

  * 编译内核：需要内核源码和编译环境

  * 编译系统调用描述：需要 **内核源码** （提供头文件），编译内核生成的中间件 **KERNEL_OBJ** （提供头文件）

  * 编译 syzkaller：需要 go 语言环境

使用 syzkaller 的难点是什么？

  * 对于新手来说，毫无疑问，编写驱动对应的 txt（即系统调用描述）是最难的。不同驱动的入口结构体、系统调用都是不同的，相对应的 txt 也是不一样的。最好的方法是结合 syzkaller 给出的大量已编写好的 txt，并且根据相应的驱动源码，学习 syzkaller 系统调用描述的语法。

  * 需要内核源码的支持，也就是说，我们并不能以黑盒的方式测试其他 Android 厂商的手机，而只能在有内核源码的情况下，编译带有 KCON+KASAN 编译选项的内核镜像。

  * 在测试过程中，有一定的误报率，待测设备（Android 手机）往往跟我们的监控设备（Linux 主机）无故断开连接，也会出现死机等现象，在一定程度上增加了测试周期。

syzkaller 的优点是什么？

  * syzkaller 优点还是很明显的，会根据代码覆盖率变异系统调用的输入，增加代码覆盖率。驱动包含的复杂结构体，用白盒审计的方式往往难以发现深层次问题，通过 fuzzing 可以很容易找到一些隐藏深处的代码安全漏洞。

### 原理

![image](https://image.3001.net/images/20220303/1646301409_622090e1e32a2fcdabc94.png!small)

  * `syz-manager`进程启动、监视和重新启动多个 VM 实例，并 **syz-fuzzer** 在 VM 内部启动一个进程。 **syz-manager** 负责持久化语料库和崩溃存储。它运行在具有稳定内核的主机上，不会具有模糊器负载。

  * `syz-fuzzer`过程在可能不稳定的虚拟机中运行。引导模糊测试过程（输入生成、变异、最小化等），并且通过RPC将那些引起了新的覆盖（coverage）的输入回送到 **syz-manager** 。 **syz-fuzzer** 也负责启动短暂的 **syz-executor** 进程。

  * 每个`syz-executor`进程执行一个输入（一系列系统调用）。它接收 **syz-fuzzer** 的用例，并执行，返回结果。它被设计为尽可能简单（不干扰模糊测试过程），用 C++ 编写，编译为静态二进制文件并使用共享内存进行通信。

### 目录结构

syzkaller 源码目录结构如下，对于新手来说，需要重点关注的目录已用黑体字表粗。

  * Godeps：go 的依赖包管理。

  * dashboard：与 syzbot 有关，syzbot 会自动 fuzz linux 内核主线分支并向内核邮件列表报告发现的错误。

  *  **docs：syzkaller 所有帮助文档。**

  * executor：syz-executor 的源码。

  * pkg：配置文件。

  * prog：目标系统相关信息及需要执行的系统调用。

  *  **sys：系统调用描述** 。我们自己编写的 txt 可以放在这个目录下。

  * sys-ci：持续运行syzkaller的系统。

  * sys-fuzzer：syz-fuzzer 的源码。

  * sys-hub：将多个 syz-manager 连接在一起并允许它们交换程序。

  * sys-manager：syz-manager 目录。

  * tools：一些工具。这些工具大都是对 pkg 目录下代码的一些封装。

  * vm：被测对象操控相关处理的代码存放路径，手机用的就是 adb 目录下的 adb.go；vm.go是所有 vm 的抽象接口，供 syz-manager 调用。

## 测试步骤

初学时，对 syzkaller 的测试步骤很迷茫，最终实践过多次，才明白各个步骤真正的含义。这里只是简要介绍一下大体的 fuzzing
流程，实际上还是需要多多实践，才能更好的理解 syzkaller。

  * 编写待测试驱动对应的 txt 文件（即系统调用描述）。可参考官方文档：[syscall_descriptions_syntax.md](https://github.com/google/syzkaller/blob/master/docs/syscall_descriptions_syntax.md)，syzkaller 源码对应的 `sys`目录也给出了大量示例 。

  * 编译系统调用描述文件，使用 `syz-extract`将其转换为 .const 文件，使用 `syz-sysgen`生成 .go 文件。

  * 编译 syzkaller，生成 `syz-manager`、`syz-fuzzer`以及`syz-executor`。

  * 编写配置文件，可参考 [configuration.md](https://github.com/google/syzkaller/blob/master/docs/configuration.md)，运行 `syz-manager --config my.cfg`，syz-manager 会根据配置文件，将 `syz-fuzzer`和 `syz-executor`push 到目标设备，并开始 fuzzing。

![image](https://image.3001.net/images/20220303/1646300346_62208cba570548ce89386.png!small)

## 总结

Syzkaller 作为一个优秀的内核 fuzz 工具，后来衍生了很多其他的工具，归根结底使用的还是 syzkaller
的思想。这里只是一些入门知识总结，对于新手来说，通读此文，相信你一定有所收获，知道 syzkaller 是什么，进行 fuzz 的条件是什么，fuzz
对象又是什么。

## 参考文献

如果你想知道更多细节，将 syzkaller 用于实战，可以参考如下文章

  * Android 模拟器内核：[从0开始Fuzzing之旅: 使用Syzkaller进行Linux驱动漏洞挖掘](https://www.freebuf.com/sectool/285699.html)

  * Linux 内核：[从0到1开始使用syzkaller进行Linux内核漏洞挖掘](https://bbs.pediy.com/thread-265405.htm)

  * Android 手机： [Fuzzing a Pixel 3a Kernel with Syzkaller](https://blog.senyuuri.info/2020/04/16/fuzzing-a-pixel-3a-kernel-with-syzkaller/)

  * 源码分析：[内核漏洞挖掘技术系列(4)——syzkaller(1)](https://xz.aliyun.com/t/5079)

如果你想了解更多的 syzkaller 衍生工具，可以参考如下安全顶会论文

  * [MoonShine: Optimizing OS Fuzzer Seed Selection with Trace Distillation](https://www.usenix.org/conference/usenixsecurity18/presentation/pailoor)（2018）：哥伦比亚大学团队开发的 MoonShine，这是一种新颖的策略，可从真实程序的系统调用中提取 fuzz 种子。作为对 Syzkaller 的扩展， MoonShin 能够将 Syzkaller 的 Linux 内核代码覆盖率平均提高 13％。

  * [Razzer: Finding Kernel Race Bugs through Fuzzing](https://www.computer.org/csdl/proceedings-article/sp/2019/666000a296/19skfwZLirm)（2019）：韩国科学技术院 (KAIST) DR Jeong 设计并提出了针对内核中的数据竞争类型漏洞的模糊测试（fuzzing）工具 Razzer 。 Razzer 的两阶段模糊测试基于Syzkaller。确定性调度程序是使用 QEMU / KVM 实现的。

  * [HFL: Hybrid Fuzzing on the Linux Kernel](https://www.unexploitable.systems/publication/kimhfl/)(2020)：美国俄勒冈州立大学提出的一个新兴混合 fuzz 工具。据作者所属，HFL 代码覆盖率分别比 Moonshine 和 Syzkaller 高出15%和26%，并发现 20+ 个内核漏洞。该工具好像没有开源。

  * [CoLaFUZE: Coverage-Guided and Layout-Aware Fuzzing for Android Drivers](https://www.jstage.jst.go.jp/article/transinf/E104.D/11/E104.D_2021NGP0005/_pdf)(2021)， _南方电网数字电网研究院有限公司_ 的 Tianshi Mu 等人介绍了CoLaFUZE，一个覆盖率引导和布局感知的模糊工具，用于自动生成有效输入和探索驱动程序代码。用于模糊测试 **安卓驱动程序** 。

如果你在使用 syzkaller 的过程中发现一些奇奇怪怪的问题，并且一些中文博客无法解决这样的问题，不要吝啬，[打开 syzkaller 项目
issue](https://github.com/google/syzkaller/issues)，搜索关键字！如果 issue
里没有你想要的答案，也可以自己提交 issue，syzkaller 项目开发人员答复很快的。

