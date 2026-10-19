# 【技术分享】使用符号执行技术解决Android Crackme

阅读量 **204015**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-02-09 16:16:57

 **x**

##### 译文声明

本文是翻译文章，文章来源：vantagepoint.sg

原文地址：<http://www.vantagepoint.sg/blog/81-solving-an-android-crackme-with-a-little-symbolic-execution>

译文仅供参考，具体内容表达以及含义原文为准。

****

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：180RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**  
**

**0x00 前言**

二进制分析框架提供给我们强大的自动化分析的方法。本文中，我们将看下Angr，一个python实现的用于静态和动态分析的分析框架。它基于Valgrind的VEX中间层语言。使用一个精简的加载器“CLE
Loads Everything”，这个加载器不是完全精确的，但是能够加载ELF/ARM的可执行文件，因此对于处理Android的原生库有帮助。

我们的目标程序是一个授权验证程序。虽然在应用商店中不会总是发现类似的东西，但是用来描述基本的符号分析是足够的。您可以在混淆的Android二进制文件中以许多创造性的方式使用这些技术。

  

**0x01 符号执行**

在21世纪后期，基于符号执行的测试就在用于确认安全漏洞的领域非常流行。符号“执行”实际上是指代表通过程序的可能路径作为一阶逻辑中的公式的过程，其中变量由符号值表示。通过SMT解释器来验证并给这些公式提供解决方案，我们能得到到达每个执行点的需要的数据。

简单来说，工作过程如下：

1\. 将程序的一个路径翻译为一个逻辑表达式，其中的一些状态用符号表示

2\. 解决公式

3\. 得到结果

这是一个简化的描述，实际上更加复杂。执行引擎首先枚举程序中所有可能的路径。对于每个分支，引擎将由分支条件施加的约束保存在分支所依赖的符号变量上。最终得到一个非常大的路径公式，并解决相关的公式，你将得到覆盖所有路径的输入变量。

然而，解决公式是困难的一部分。为了理解这个如何工作，让我们回顾下布尔可满足性(SAT)问题。SAT是一个确定命题逻辑公式的是否满足的问题，例如(x1 ∨
¬x2) ∧ (¬x1 ∨ x2 ∨
x3)（意思是，根据输入可能产生一个true的结果）。然而命题逻辑不足以编码在我们的程序中发生的所有可能的约束：毕竟，分支决定依赖符号变量之间的复杂的关系。

因此我们需要将SAT扩展到SMT。SMT能用非二进制变量的集合断言代替SAT公式。每个断言的输出是一个二进制值。一个线性代数中的断言可以是“2x+3y>1”。因此，当“2x+3y>1”满足时一个特殊的分支可能被采用。

每个路径公式都是SMT问题。负责解决问题的SAT解释器简单地将理论断言的连接传递给各个理论的专用求解器，例如线性算术，非线性算术和位向量。最终，问题被简化为SAT求解程序，可以处理的一个普通的布尔SAT实例。

  

**0x02 实例分析**

符号执行对于需要找到到达特定代码块的正确输入是很有用的。在下面的例子中，将使用Angr来自动化解决一个简单Android
Crackme。这个crackme采用的原生ELF二进制文件在[这里](https://github.com/angr/angr-doc/tree/master/examples/android_arm_license_validation)下载到。

**安装Angr**

Angr使用python 2编写，在PyPi提供。可以通过pip简单的安装：

    
    
    $ pip install angr

建议用[Virtualenv](https://virtualenv.pypa.io/en/stable/)创建一个专用的虚拟环境，因为它的一些依赖项包含覆盖原始版本的分支版本Z3和PyVEX（如果不使用这些库，则可以跳过此步骤
– 另一方面， 使用Virtualenv总是一个好主意）。

Angr在[gitbooks](https://docs.angr.io/)上提供了非常容易理解的文档，包括安装指导，教程和用法示例。还有完整的[API参考](http://angr.io/api-doc/)提供。

在安卓设备中运行可执行文件能得到如下的输出。

    
    
    $ adb push validate /data/local/tmp
    [100%] /data/local/tmp/validate
    $ adb shell chmod 755 /data/local/tmp/validate
    $ adb shell /data/local/tmp/validate
    Usage: ./validate <serial>
    $ adb shell /data/local/tmp/validate 12345
    Incorrect serial (wrong format).

到目前为止，一切都很好，但是我们不知道任何关于可靠的授权序列号是啥样的。通过IDA先大致浏览以下代码。

在反汇编中主要功能定位到地址0x1874处（注意到这是一个开启PIE的二进制文件，并且IDA选择了0x0作为映像基址）。函数名称是没有的，但是我们能看到一些调试字符串的引用：出现在base32解密输入字符串中（调用到sub_1340）。在main函数开始处，对于loc_1898有个长度校验用来验证输入字符串的长度是否是16。因此我们需要一个16个字符的base32加密的字符串。解码输入被传入函数sub_1760中，验证授权序列号的可靠性。

16个字符的base32字符串被解码成10个字节，因此我们知道验证函数希望有个10字节的二进制字符串。接下来，我们看下位于0x1760的验证函数：

    
    
    .text:00001760 ; =============== S U B R O U T I N E =======================================
    .text:00001760
    .text:00001760 ; Attributes: bp-based frame
    .text:00001760
    .text:00001760 sub_1760                                ; CODE XREF: sub_1874+B0
    .text:00001760
    .text:00001760 var_20          = -0x20
    .text:00001760 var_1C          = -0x1C
    .text:00001760 var_1B          = -0x1B
    .text:00001760 var_1A          = -0x1A
    .text:00001760 var_19          = -0x19
    .text:00001760 var_18          = -0x18
    .text:00001760 var_14          = -0x14
    .text:00001760 var_10          = -0x10
    .text:00001760 var_C           = -0xC
    .text:00001760
    .text:00001760                 STMFD   SP!, {R4,R11,LR}
    .text:00001764                 ADD     R11, SP, #8
    .text:00001768                 SUB     SP, SP, #0x1C
    .text:0000176C                 STR     R0, [R11,#var_20]
    .text:00001770                 LDR     R3, [R11,#var_20]
    .text:00001774                 STR     R3, [R11,#var_10]
    .text:00001778                 MOV     R3, #0
    .text:0000177C                 STR     R3, [R11,#var_14]
    .text:00001780                 B       loc_17D0
    .text:00001784 ; ---------------------------------------------------------------------------    .text:00001784
    .text:00001784 loc_1784                                ; CODE XREF: sub_1760+78
    .text:00001784                 LDR     R3, [R11,#var_10]
    .text:00001788                 LDRB    R2, [R3]
    .text:0000178C                 LDR     R3, [R11,#var_10]
    .text:00001790                 ADD     R3, R3, #1
    .text:00001794                 LDRB    R3, [R3]
    .text:00001798                 EOR     R3, R2, R3    ; Aha! You're XOR-ing a byte with the byte next to it. In a loop! You bastard.
    .text:0000179C                 AND     R2, R3, #0xFF
    .text:000017A0                 MOV     R3, #0xFFFFFFF0
    .text:000017A4                 LDR     R1, [R11,#var_14]
    .text:000017A8                 SUB     R0, R11, #-var_C
    .text:000017AC                 ADD     R1, R0, R1
    .text:000017B0                 ADD     R3, R1, R3
    .text:000017B4                 STRB    R2, [R3]
    .text:000017B8                 LDR     R3, [R11,#var_10]
    .text:000017BC                 ADD     R3, R3, #2
    .text:000017C0                 STR     R3, [R11,#var_10]
    .text:000017C4                 LDR     R3, [R11,#var_14]
    .text:000017C8                 ADD     R3, R3, #1
    .text:000017CC                 STR     R3, [R11,#var_14]
    .text:000017D0
    .text:000017D0 loc_17D0                                ; CODE XREF: sub_1760+20
    .text:000017D0                 LDR     R3, [R11,#var_14]
    .text:000017D4                 CMP     R3, #4
    .text:000017D8                 BLE     loc_1784
    .text:000017DC                 LDRB    R4, [R11,#var_1C] ; Now you're comparing the xor-ed bytes with values retrieved from - somewhere...
    .text:000017E0                 BL      sub_16F0
    .text:000017E4                 MOV     R3, R0
    .text:000017E8                 CMP     R4, R3
    .text:000017EC                 BNE     loc_1854
    .text:000017F0                 LDRB    R4, [R11,#var_1B]
    .text:000017F4                 BL      sub_170C
    .text:000017F8                 MOV     R3, R0
    .text:000017FC                 CMP     R4, R3
    .text:00001800                 BNE     loc_1854
    .text:00001804                 LDRB    R4, [R11,#var_1A]
    .text:00001808                 BL      sub_16F0
    .text:0000180C                 MOV     R3, R0
    .text:00001810                 CMP     R4, R3
    .text:00001814                 BNE     loc_1854
    .text:00001818                 LDRB    R4, [R11,#var_19]
    .text:0000181C                 BL      sub_1728
    .text:00001820                 MOV     R3, R0
    .text:00001824                 CMP     R4, R3
    .text:00001828                 BNE     loc_1854
    .text:0000182C                 LDRB    R4, [R11,#var_18]
    .text:00001830                 BL      sub_1744
    .text:00001834                 MOV     R3, R0
    .text:00001838                 CMP     R4, R3
    .text:0000183C                 BNE     loc_1854
    .text:00001840                 LDR     R3, =(aProductActivat - 0x184C)  ; This is where we want to be!
    .text:00001844                 ADD     R3, PC, R3      ; "Product activation passed. Congratulati"...
    .text:00001848                 MOV     R0, R3          ; char *
    .text:0000184C                 BL      puts
    .text:00001850                 B       loc_1864
    .text:00001854 ; ---------------------------------------------------------------------------    .text:00001854
    .text:00001854 loc_1854                                ; CODE XREF: sub_1760+8C
    .text:00001854                                         ; sub_1760+A0j ...
    .text:00001854                 LDR     R3, =(aIncorrectSer_0 - 0x1860) ; This is where we DON'T wanna be!
    .text:00001858                 ADD     R3, PC, R3      ; "Incorrect serial."
    .text:0000185C                 MOV     R0, R3          ; char *
    .text:00001860                 BL      puts
    .text:00001864
    .text:00001864 loc_1864                                ; CODE XREF: sub_1760+F0
    .text:00001864                 SUB     SP, R11, #8
    .text:00001868                 LDMFD   SP!, {R4,R11,PC}
    .text:00001868 ; End of function sub_1760

我们能在loc_1784看到异或操作，应该是解码操作。从loc_17DC开始，我们能看到一系列的解码值的比较。尽管它看起来高度复杂，我们还需要更多的逆向分析并生成授权传给它。但是通过动态符号执行，我们不需要做更多的深入分析。符号执行引擎能够映射一条在校验授权的开始处（0x1760）和输出消息“Product
activation passed”的地方（0x1840）之间的路径，决定每种输入的约束。求解引擎能发现满足那些约束的输入值即可靠的授权序列号。

我们只需要提供几种输入给符号执行引擎：

1\. 开始执行的地址。我们使用串行验证函数的第一条指令来初始化状态。这能使任务变得简单，因为我们避免了符号执行base32实现。

2\. 我们想要执行到达的代码块地址。在这个例子中，我们想找到一个输出“Product activation
passed”消息的有效路径。这个块的其实地址是0x1840。

3\. 我们不想到达的地址。这种情况下，我们对于任何到达输出“incorrect serial”消息的路径不感兴趣（0x1854）。

Angr加载器在基址0x400000处加载PIE可执行文件，因此我们必须将这个添加到上述地址中。解决方案如下。

    
    
    #!/usr/bin/python
     
    # This is how we defeat the Android license check using Angr!
    # The binary is available for download on GitHub:
    # https://github.com/b-mueller/obfuscation-metrics/tree/master/crackmes/android/01_license_check_1
    # Written by Bernhard -- bernhard [dot] mueller [at] owasp [dot] org
     
    import angr
    import claripy
    import base64
     
    load_options = {}
     
    # Android NDK library path:
    load_options['custom_ld_path'] = ['/Users/berndt/Tools/android-ndk-r10e/platforms/android-21/arch-arm/usr/lib']
     
    b = angr.Project("./validate", load_options = load_options)
     
    # The key validation function starts at 0x401760, so that's where we create the initial state.
    # This speeds things up a lot because we're bypassing the Base32-encoder.
     
    state = b.factory.blank_state(addr=0x401760)
     
    initial_path = b.factory.path(state)
    path_group = b.factory.path_group(state)
     
    # 0x401840 = Product activation passed
    # 0x401854 = Incorrect serial
     
    path_group.explore(find=0x401840, avoid=0x401854)
    found = path_group.found[0]
     
    # Get the solution string from *(R11 - 0x24).
     
    addr = found.state.memory.load(found.state.regs.r11 - 0x24, endness='Iend_LE')
    concrete_addr = found.state.se.any_int(addr)
    solution = found.state.se.any_str(found.state.memory.load(concrete_addr,10))
     
    print base64.b32encode(solution)

注意到程序的最后一部分，能获得我们最终想要的输入字符串。然而我们从符号内存中读不到任何字符串或指针。真实发生的是求解器计算的具体的值能在程序状态中找到。

运行脚本能得到以下输出：

    
    
    (angr) $ python solve.py
    WARNING | 2017-01-09 17:17:03,664 | cle.loader | The main binary is a position-independent executable. It is being loaded with a base address of 0x400000.
    JQAE6ACMABNAAIIA

最终的授权序列号应该能使程序输出成功的消息。

同时，符号执行是一种强大的技术，能用于漏洞挖掘，解混淆和逆向工程。

  

**0x03 参考**

Angr – [http://angr.io](http://angr.io/)

Axel Souchet, Jonathan Salwan, Jérémy Fetiveau – Keygenning with KLEE –
[http://doar-e.github.io/blog/2015/08/18/keygenning-with-klee/](http://doar-e.github.io/blog/2015/08/18/keygenning-with-klee/)

Logic for Computer Science –
[http://www.cs.ru.nl/~herman/onderwijs/soflp2013/reeves-clarke-lcs.pdf](http://www.cs.ru.nl/~herman/onderwijs/soflp2013/reeves-clarke-lcs.pdf)

Concolic Testing:
[https://en.wikipedia.org/wiki/Concolic_testing](https://en.wikipedia.org/wiki/Concolic_testing)

本文翻译自vantagepoint.sg [原文链接](http://www.vantagepoint.sg/blog/81-solving-an-android-crackme-with-a-little-symbolic-execution)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **root** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85445](/post/id/85445)

安全客 - 有思想的安全新媒体

本文转载自: [vantagepoint.sg](http://www.vantagepoint.sg/blog/81-solving-an-android-crackme-with-a-little-symbolic-execution)

如若转载,请注明出处： <http://www.vantagepoint.sg/blog/81-solving-an-android-crackme-with-a-little-symbolic-execution>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __3赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) root

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

