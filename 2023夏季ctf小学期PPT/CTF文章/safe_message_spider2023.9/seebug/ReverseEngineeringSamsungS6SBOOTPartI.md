原文：[blog.quarkslab.com](http://blog.quarkslab.com/reverse-engineering-samsung-s6-sboot-part-i.html)

原作者：Quarkslab

译： **Holic (知道创宇404安全实验室)**

现在有许多搭载三星 Exynos 智能手机使用了 SBOOT 专属 bootLoader。目前三星 Galaxy S7，Galaxy S6 和 Galaxy
A3 即是如此，当然在三星 Exynos Showcase [1] 上可能还会有更多的智能手机采用，我也有一次在审计各种 TEE 实现的时候逆向了一部分
BootLoader 。本文是 SBoot 系列的第一篇，它回顾了 ARMv8
的一些概念，阐述了我的方法论，正确或错误的假设，同时在没有文档的情况下分析了一堆三星 S6 的一堆东西。

### 来龙去脉

最近，作为日常工作，我有幸在几次可信执行环境（TEE）的应用中审计出了几个 bug。在项目之余，我开始挖掘更多的 TEE
应用，特别是在我的智能手机上，个人用或在工作中，巧合的是，他们来自同一个软件编辑器，即由 ARM，G&D 和 Gemalto 共同创立的Trustonic
[2]。目前我手上的智能手机的共同点就是他们都基于 Exynos 。

Trustonic 的 TEE，名为 <t-base ，由 Mobicore, G&D 的 TEE 原型演变而来。据我所知，这个 TEE
及以前的版本中很少有公开的技术信息。分析变得富有挑战性，超出我的预想范围。我们针对三星 Galaxy S6 进一步调查吧！

然而在文件系统上识别受信任的应用是最困难的挑战，而据我分析在 Exynos 智能手机上查找 TEE OS
相当于大海捞针。实际上，你可以在一些智能手机上找到的（例如基于 Qualcomm 的 SoC）专门存储 TEE OS
镜像的特定分区，在这里已经无法找到了。它一定是存储在其他地方，也许是在 bootloader 自身，这就我要逆向 SBOOT
的原因了。本文是系列首篇，叙述了我的 TEE OS 逆向之旅，主要讲在 IDA 中确定三星 S6 SBOOT 的基地址的方法。

### ARMv8 相关概念

在启动 IDA Pro 之前，我们来回顾一下 ARMv8 的一些基本原理。我在这里先介绍几个概念，对 ARMv8 新手但已经使用过 ARMv7
的人来说是有用的。有关更准确完整的文档，参考 ARMv8 程序员指南[3]。由于我不是 ARMv8 专家，如果你看到任何错误和不准确的之处，请随时评论。

#### Exception Levels

ARMv8 通过定义异常级别的概念引入一个新的异常模型。异常级别确定运行软件组件的权限级别（PL0到PL3）和运行它的处理器模式（非安全和安全）。在 ELn
处执行对应权限 PLn，并且 n 越大，执行级别具有的特权越多。

![](https://images.seebug.org/content/images/2017/03/exception-vectors.png-w331s)

#### 异常向量表

当异常发生时，处理器分到异常向量表运行响应的处理程序。在 ARMv8 上，每个异常级别都有自己的异常向量表。习惯与逆向 ARMv7 bootloader
的人，你会注意到它的格式与 ARMv7 完全不同：

![](https://images.seebug.org/content/images/2017/03/exception-table.png-w331s)

机智的读者可能已经注意，异常向量表对应的条目为 128（0x80）字节长度，而在 ARMv7 上每条仅为 4 字节宽，并且每条保持一些了异常处理指令。虽然在
ARMv7 上异常向量表的位置由的 VTOR（Vector Table Offset Registe）确定，但在 ARMv8 上使用了三个
VBAR（Vector Based Address
Registers）VBAR_EL3，VBAR_EL2，VBAR_EL1。这里注意，对于特定级别将执行的处理程序（或者表项）的运行取决于：

  * 异常类型（SError，FIQ，IRQ 或 Synchronous）
  * 如果异常在相等的异常级别发生，则使用堆栈指针（SP0或SPx）。
  * 如果异常在较低的异常级别发生，则切换下一个较低级别（AArch64 或 AArch32）的执行状态。

运行在特定级别的组件可以使用专用指令在与底层异常级别上运行的软件交互。比如例如，用户模式的进程（EL0）通过发起 Supervisor
调用（SVC），来执行由内核（EL1）处理的系统调用，内核便能使用 Hypervisor 调用（HVC）与 hypervisor（EL2）
交互，或者直接通过安全监控（EL3）的安全监视调用（SMC）等方法进行交互。这些 **服务调用** 生成的 **同步异常** ，由异常向量表同步处理器处理。

### 反汇编 SBOOT

据我所知，SBOOT 使用了尚未公开记录的专有格式。

#### SBOOT 加载到 IDA Pro

三星 Galaxy S6 由 1.5GHz 64八核 Exynos 7420 CPU 驱动。回想到 ARMv8 可以运行由 AArch32 和
AArch64 构建的应用程序。因此，可以试着将 SBOOT 加载为32位或者64位的 ARM 二进制文件。

我猜 BootROM 还没有切换到 AArch32 状态，并将其作为64位的二进制文件加载到 IDA Pro 中，保留默认选项：

  * Processor Type: ARM Little Endian [ARM]
  * Disassemble as 64-bit code: Yes

许多 AArch64 指令被自动识别。当涉及到反汇编指令，基本块还是有意义的，让我想到我真的在处理 AArch64 代码。

![](https://images.seebug.org/content/images/2017/03/ida-load-s6-as-binary.png-w331s)

#### 确定基址

我花了几天时间来确定正确的基地址。先直接给你解决方案毫无意义的，我会先详细说明我所尝试的东西，直到假设正确，给我正确的基地址。正如谚语所说：“授之以鱼，不如授之以渔”。

##### Web Search

我开始在各个搜索引擎搜索三星 bootloader 和 SBOOT 相关内容。很不幸，结果很少，相关内容只有 2015年三月
reverseengineering.stackexchange.com 上的一条帖子[5]。

这个帖子主要给我两个提示。 J-Cho 感觉 bootloader 从文件偏移 0x3F000 处开始加载，这点挺有用，而它实际从 0x10 处开始。

正如我想证实的假设，bootloader 的基地址是 0x00000000，它的代码总是从 0x10 开始，我开始在其他 Exynos 智能手机使用的
bootloader。魅族的 SBOOT 并没有在 0x10 给出有效指令，澄清了我怀疑之处：

![](https://images.seebug.org/content/images/2017/03/ida-load-mz-as-binary.png-w331s)

我还分析了其它bootloader中是否留有调试字符串，这会对找到 SBOOT 在内存中加载的位置有所提示。不幸:( 但是还有一条线索：在魅族 SBOOT
的一些字符串说明使用了 U-Boot 。即使 U-Boot 不使用三星 Galaxy S6，这是一个值得探索的路线，我开始进一步探索。

##### U-Boot Respsitory

U-Boot 是开源的，支持多个 Exynos 芯片。例如，Exynos 4 和 Exynos 5 已经支持 5 年多了。Exynos 7
的支持尚未完全登录主线[6]，Exynos 7 ESPRESSO 开发板还存在一些补丁。

我可能错过了这一点，但纵览 ESPRESSO 开发板的补丁，并没有得到相应结果:(我的 Exynos 7 上试过多个 Exynos
4已知的的基地址，无果。是时候换个姿势了。

##### ARM Literal Pools（文字池）

如果你熟悉 ARM 逆向，你一定注意到了大量的文字池来保存要加载到寄存器的常量。此属性可以帮助我们查找在何处加载
SBOOT，特别是从文字池加载目标分支地址时。

我搜索了 IDA Pro 在操作数中所有标记有错误的分支指令（以红色突出显示）。由于 bootloader
代码是自包含的，我可以大胆猜想大多数分支目标代码的最终必须指向 bootloader 本身。带着这个假设，我可以估计 bootloader 的基地址。

![](https://images.seebug.org/content/images/2017/03/ida-literal-pool-error.png-w331s)

这些代码段有个很有意思的地方：

  1. 分支指令 BR（跳转分支到寄存器）是无条件跳转，意味着没有返回。
  2. 两个分支操作数相同（0x2104010），并且位于 bootloader 前面一部分。
  3. 最后一个字节 0x10，正是 bootloader 代码开始的偏移量。

我猜地址 0x2104010 是个复位地址，我试着在 0x2104010 加载 SBOOT 二进制文件，带着下列选项：

  * Processor Type: ARM Little Endian [ARM]
  * Start ROM Address: 0x2104000
  * Loading Address: 0x2104000
  * Disassemble as 64-bit code: Yes

##### ARM 系统寄存器

现在我有了潜在可能的基地址，继续逆向 SBOOT ，希望代码流中没有异常。

由于我想找到 TEE
OS，我开始搜索在安全监视器中执行的代码片段。找到安全监视器有一个相当简单的技巧，就是寻找设置或读取相关指令，该指令只能从安全监视器设置或者读取寄存器。如前所述，安全监视器运行与
EL3 中。VBAR_EL3 是一个很好的找到 EL3 代码的候选方案，因为它保存了 EL3 的异常向量表的基址并指向 SMC 处理程序。

![](https://images.seebug.org/content/images/2017/03/ida-vbar-el3-search.png-w331s)

你还记得本文开头介绍的异常向量表的格式吗？它由 16 个 0x80
字节的条目组成，保存异常处理程序的代码。在搜索结果中，0x2111000处的代码似乎指向一个有效的异常向量表：

![](https://images.seebug.org/content/images/2017/03/ida-exception-vectors-table.png-w331s)

即便如此，所选择的基地址仍不是正确的:( 当验证设置 VBAR_EL3 的其它指令时，可以注意一下 0x210F000 在函数当中：

![](https://images.seebug.org/content/images/2017/03/ida-wrong-exception-vectors-table.png-w331s)

这些异常表明 0x2104000 不是正确的基地址。

我们试试别的东西吧。

##### Service Descriptors

三星 Galaxy S6 SBOOT 部分基于 ARM 可信固件[7]。ARM 可信固件是开源的，作为 ARMv8-A
提供了安全世界软件的参考实现，包括在异常级别3（EL3）执行的安全监视器。安全监视器对应的汇编代码与 ARM
可信固件中的汇编代码完全相同。好消息，因为它节省了我不少时间，节省了不少逆向的工夫。

我试着在反汇编中找到另一个锚点，以确定 SBOOT 的基地址。在结构体中的 char *
类型的成员特别有趣，因为它们指向在编译时就定义其地址的字符串。在比较 SBOOT 反汇编代码和 ARM
可信固件的源码时，我确定了一个结构，`rt_svc_desc_t`，它具有我正在在找的属性。

    
    
    typedef struct rt_svc_desc {
        uint8_t start_oen;
        uint8_t end_oen;
        uint8_t call_type;
        const char *name;
        rt_svc_init_t init;
        rt_svc_handle_t handle;
    } rt_svc_desc_t;

根据 ARM 可信固件的源码，`rt_svc_descs` 是一个 `rt_svc_desc_t` 数组，用于保存服务导出的运行时服务描述符。它使用于函数
`runtime_svc_init` 中，通过调用函数 `bl31_main` 中的调试字符串可轻易将其放置在 SBOOT 中：

![](https://images.seebug.org/content/images/2017/03/ida-rt-svc-desc.png-w331s)

我想把二进制映射到不同的地址，并检测是否可以找到 `rt_svc_desc.name` 条目的有效字符串。这是一段挺小的暴破脚本：

    
    
    import sys
    import string
    import struct
    
    RT_SVC_DESC_FORMAT  = "BBB5xQQQ"
    RT_SVC_DESC_SIZE    = struct.calcsize(RT_SVC_DESC_FORMAT)
    RT_SVC_DESC_OFFSET  = 0xcb50
    RT_SVC_DESC_ENTRIES = (0xcc10 - 0xcb50) / RT_SVC_DESC_SIZE
    
    if len(sys.argv) != 2:
        print("usage: %s <sboot.bin>" % sys.argv[0])
        sys.exit(1)
    
    sboot_file = open(sys.argv[1], "rb")
    sboot_data = sboot_file.read()
    
    rt_svc_desc = []
    for idx in range(RT_SVC_DESC_ENTRIES):
        start = RT_SVC_DESC_OFFSET + (idx << 5)
        desc = struct.unpack(RT_SVC_DESC_FORMAT,
                             sboot_data[start:start+RT_SVC_DESC_SIZE])
        rt_svc_desc.append(desc)
    
    strlen = lambda x: 1 + strlen(x[1:]) if x and x[0] in string.printable else 0
    
    for base_addr in range(0x2100000, 0x21fffff, 0x1000):
        names = []
        print("[+] testing base address %08x" % base_addr)
        for desc in rt_svc_desc:
            offset = desc[3] - base_addr
            if offset < 0:
                sys.exit(0)
            name_len = strlen(sboot_data[offset:])
            if not name_len:
                break
            names.append(sboot_data[offset:offset+name_len])
        if len(names) == RT_SVC_DESC_ENTRIES:
            print("[!] w00t!!! base address is %08x" % base_addr)
            print("    found names: %s" % ", ".join(names))

在要分析的 SBOOT 上运行此脚本，给出以下输出：

    
    
    $ python bf_sboot.py sboot.bin
    [+] testing base address 02100000
    [+] testing base address 02101000
    [+] testing base address 02102000
    [!] w00t!!! base address is 02102000
        found names: mon_smc, std_svc, tbase_dummy_sip_fastcall,
                     tbase_oem_fastcall, tbase_smc, tbase_fastcall
    [...]

成功！三星 Galaxy S6 SBOOT 的基址为 0x02102000 。用这个基址重新加载二进制到 IDA
Pro，似乎纠正了我之前看到的所有反汇编代码中的奇怪之处。我们现在一定可以获得正确的结果。

#### 增强反汇编

逆向工程像是解谜一样。试着将一些信息放到一起来理解软件的运行原理。因此，你拥有的信息越多，解谜的难度就越大。这里有一些小技巧，帮助我找到了正确的基地址。

##### 缺少的函数

尽管 IDA Pro
在反汇编常用文件格式方面做得很出色，但在逆向未知格式的二进制可能会漏掉很多函数。这种情况下，通常是写脚本查找起始指令，并声明函数存在于此。一个简单的
AArch64 函数序列如下：

    
    
    // AArch64 PCS assigns the frame pointer to x29
    sub     sp, sp, #0x10
    stp     x29, x30, [sp]
    mov     x29, sp

指令mov x29，sp是 AArch64 起始语句相当可靠的标记。找到函数入口点的思路在于搜索这个标记，并在发现公共起始语句的时候进行反汇编。在 IDA
Python 中搜索 AArch64 函数入口点的函数如下：

    
    
    import idaapi
    
    def find_sig(segment, sig, callback):
        seg = idaapi.get_segm_by_name(segment)
        if not seg:
            return
        ea, maxea = seg.startEA, seg.endEA
        while ea != idaapi.BADADDR:
            ea = idaapi.find_binary(ea, maxea, sig, 16, idaapi.SEARCH_DOWN)
            if ea != idaapi.BADADDR:
                callback(ea)
                ea += 4
    
    def is_prologue_insn(ea):
        idaapi.decode_insn(ea)
        return idaapi.cmd.itype in [idaapi.ARM_stp, idaapi.ARM_mov, idaapi.ARM_sub]
    
    def callback(ea):
        flags = idaapi.getFlags(ea)
        if idaapi.isUnknown(flags):
            while ea != idaapi.BADADDR:
                if is_prologue_insn(ea - 4):
                    ea -= 4
                else:
                    print("[*] New function discovered at %#lx" % (ea))
                    idaapi.add_func(ea, idaapi.BADADDR)
                    break
        if idaapi.isData(flags):
            print("[!] %#lx needs manual review" % (ea))
    
    mov_x29_sp = "fd 03 00 91"
    find_sig("ROM", mov_x29_sp, callback)

##### ARM64 IDA Plugins

**AArch64 mov simplifier**

编译器有时会优化代码，使其不易读。使用 IDA Pro 的 API ，可以变形特定架构的代码简化器。我发现由
[@xerub](https://twitter.com/xerub) 分享的 AArch64 代码简化器非常管用：

    
    
    ROM:0000000002104200                 BL              sub_2104468
    ROM:0000000002104204                 MOV             X19, #0x814
    ROM:0000000002104208                 MOVK            X19, #0x105C,LSL#16
    ROM:000000000210420C                 MOV             X0, X19

[@xerub](https://twitter.com/xerub) 的“ AArch64 mov 简化器”将反汇编更改成下面的样子：

    
    
    ROM:0000000002104200                 BL              sub_2104468
    ROM:0000000002104204                 MOVE            X19, #0x105C0814
    ROM:000000000210420C                 MOV             X0, X19

机智的读者应该注意到了，MOVE 不是有效的 ARM64 指令。MOVE 只是一个标间，告诉逆向工程师当前的指令已经被简化并被这条指令取代。

##### FRIEND

在 IDA Pro 中逆向 ARM 的低级代码总是无聊的。确定与系统控制处理器相关的指令是一次可怕的经理，因为 IDA Pro
在没有寄存器别名的情况下进行反汇编。如果可以选择，你喜欢读哪一个：

`msr vbar_el3, x0`

或者

`msr #6, c12, c0, #0, x0`

ARM 的帮助插件有助于改进 IDA Pro 的反汇编，来自Stefan Esser（[@
i0n1c](https://twitter.com/i0n1c)）的 IDA AArch64
Helper插件[9]是一个这样的插件。不幸的是，它并不公开。Alex
Hude（[@getorix](https://twitter.com/getorix)）为MacOS写了一个类似的插件FRIEND
[10]。如果你密切关注这个项目，我最近提交修改[11]，上周已经合并，支持跨平台。现在可以在 Windows，Linux和MacOS上使用 FRIENDs
了 :)。

#### Signatures

前面说过，SBOOT部分基于ARM可信固件[12]。由于源代码可用，可以通过浏览源代码，重新编译它并做二进制差分（或签名匹配）来节省大量的逆向工作，以便尽可能多恢复符号。

我通常结合多个二进制 diffing 工具来增强二进制的符号识别：

  * Rizzo [13] from Craig Heffner (devttys0)
  * Bindiff [14] from Zymanics
  * Diaphora [15] from Joxean Koret (@matalaz)

它们通常具有互补的效果。

### 结论

在本文中，我描述了如何确定三星Galaxy S6 SBOOT的基地址以及如何加载到IDA
Pro。这里描述的方法应该适用于其他三星的智能手机，并可能适用于使用 Exynos SoC 的其他制造商的产品。

### 参考

  * [1] http://www.samsung.com/semiconductor/minisite/Exynos/w/showcase/smartphones/
  * [2] https://www.trustonic.com/about-trustonic
  * [3] <http://infocenter.arm.com/help/topic/com.arm.doc.den0024a/DEN0024A_v8_architecture_PG.pdf>
  * [4] http://quoteinvestigator.com/2015/08/28/fish/
  * [5] http://reverseengineering.stackexchange.com/questions/10995/problem-with-ida-pro-6-8-disassemble-galaxy-s6-sboot
  * [6] http://lists.denx.de/mailman/listinfo/u-boot
  * [7] https://github.com/ARM-software/arm-trusted-firmware
  * [8] https://gist.github.com/xerub/c6936d219db8e6635d25
  * [9] https://youtu.be/dg6byIiAwtc
  * [10] https://github.com/alexhude/FRIEND
  * [11] https://github.com/alexhude/FRIEND/pull/6
  * [12] https://github.com/ARM-software/arm-trusted-firmware
  * [13] https://github.com/devttys0/ida/blob/master/plugins/rizzo/rizzo.py
  * [14] https://www.zynamics.com/software.html
  * [15] https://github.com/joxeankoret/diaphora

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/242/>

