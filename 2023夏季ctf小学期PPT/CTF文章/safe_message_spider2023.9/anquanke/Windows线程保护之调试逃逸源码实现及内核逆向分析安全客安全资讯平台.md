# Windows线程保护之调试逃逸源码实现及内核逆向分析

阅读量 **211022**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-08-11 10:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t017b23b6d7943a70ea.png)

## 0、引言

有过Windows下调试和反调试经历的同事可能都遇到过无法调试程序的经历，这其中所涉及的反调试手段非常多，有直接检测当前程序运行环境是否有调试器进程的，原理大抵是遍历进程，比较进程名字；腾讯的一些游戏就是这么干的；或者遍历窗口，看看窗口名字或者窗口类名字是否是某些调试器的；也有间接检测的，比如判断PEB的调试字段，GFLAGS的标志位；与堆相关的调试开关；还有一些诸如调试端口是否为空；还有一些检测当前进程加载的模块是否以D结尾的；等等诸如此类的各种检测手段；那么有没有一种系统原生的“保护方式”，来确保指定的线程无法被调试，或者说实现调试逃逸？答案当然是肯定的。这便是此文需要讲述的内容。

涉及到的知识：

1、反调试常见的手段；  
2、内核调试；  
3、IDA逆向分析及常规技巧；  
4、x64架构下，gs寄存器的用途；  
5、异常分发的关键流程及API；

## 1、背景

有时候因为某些原因，必须要调试一些程序，然而这些程序也不是傻白甜，都有一定程度的反调试措施，做破解用的比较多的调试器恐怕要数OD了，国人也为其编写了很多插件，用以实现自动过反调试，如下图所示，掌握常规的反调试技术对于做破解，安全的人来说，其好处是显而易见的；今天就来讲一下另一种系统原生的线程调试逃逸技术，笔者第一次接触这个技术是当时做一个项目，需要逆向某软件，找到它的某些关键数据的来源时，用Windbg
Attach上去之后，发现对某个线程下的断点，断不下来，而其他线程的断点都是没有问题的，后来研究了下，发现了这么个技术，撰写此文，与君分享。

![](https://p5.ssl.qhimg.com/t01e88773a45a85ebc8.png)

## 2、demo源码演示

###  2.1源码如下

    
    
    typedef NTSTATUS (NTAPI *NTSETINFORMATIONTHREAD)(IN HANDLE ThreadHandle,IN DWORD ThreadInformationClass,IN PVOID ThreadInformation,IN ULONG ThreadInformationLength);
    bool TestThreadHideFromDebugger();
    int ExceptionFilter(PEXCEPTION_POINTERS pExceptionPointer);
    
    int main()
    {
        if(!TestThreadHideFromDebugger())
            return -1;
    
        while(1)
        {
            printf("main thread id:%u\n",GetCurrentThreadId());
            Sleep(500);
        }
    }
    
    DWORD WINAPI MyThreadFun(LPVOID lpThreadParameter)
    {
        __try
        {
            while(1)
            {
                printf("work thread id:%u\n",GetCurrentThreadId());
                Sleep(500);
            }
        }
        __except (ExceptionFilter(GetExceptionInformation()))
        {
            printf("Others\n");
        }
    
        return 0;
    }
    
    bool TestThreadHideFromDebugger()
    {
        DWORD dwTid = 0;
    
        HANDLE hThread = CreateThread(NULL,0,MyThreadFun,NULL,CREATE_SUSPENDED,&dwTid);
        if(!hThread)
        {
            printf("Error:%u\n",GetLastError());
            return false;
        }
    
        HMODULE hModule = GetModuleHandle(TEXT("ntdll.dll"));
        NTSETINFORMATIONTHREAD NtSetInformationThread = (NTSETINFORMATIONTHREAD)GetProcAddress(hModule, "NtSetInformationThread");
        NTSTATUS status = NtSetInformationThread(hThread, 0x11, 0, 0);//ThreadHideFromDebugger
        if(status != 0)
        {
            printf("Error:%u\n",GetLastError());
            return false;
        }
    
        ResumeThread(hThread);
        return true;
    }
    
    int ExceptionFilter(PEXCEPTION_POINTERS pExceptionPointer)
    {
        if(pExceptionPointer->ExceptionRecord->ExceptionCode == EXCEPTION_BREAKPOINT)
        {//这边有很多,诸如EXCEPTION_SINGLE_STEP调试相关的,演示时只处理了int 3的情况
            PVOID ExceptionAddress = pExceptionPointer->ExceptionRecord->ExceptionAddress;
            printf("Addr:%X\n",ExceptionAddress);
    
            DWORD dwOldProtect = 0;
            VirtualProtect(ExceptionAddress,10,PAGE_EXECUTE_READWRITE,&dwOldProtect);
            *(PBYTE)ExceptionAddress = 0x8B;
    
            MessageBox(NULL,NULL,NULL,NULL);
            return EXCEPTION_CONTINUE_EXECUTION;
        }
        else
        {
            return EXCEPTION_CONTINUE_SEARCH;
        }
    }
    

简单说明下上边的代码的作用：

1、TestThreadHideFromDebugger()这个函数内以挂起的方式创建了一个线程，
创建完后，调用NtSetInformationThread()来修改线程的“ThreadHideFromDebugger”属性，使得线程能够逃出调试器；修改完成后，再恢复线程执行；

2、线程函数MyThreadFun()内同主线程，一个死循环不停的打印当前的线程ID；值得注意的是，工作线程必须套一层 **try**
except，不然进程会直接挂掉；原因也是很清晰的；当触发int
3断点时，CPU将该异常报告给OS，当然报告的方式是通过执行IDT表中相应的异常处理例程了，而后OS内核接管该异常；进过一系列的异常分发，最终到了决定是先交给调试器还是直接交给进程时，内核的异常分发引擎会判断当前线程的ThreadHideFromDebugger属性是否置位了，如果置位的话，正如我们demo中所示的这样，那内核的异常分发引擎直接将次异常抛给进程中对应的线程，CPU的模式从Ring0即切换回Ring3即从内核态切换回用户态；此时用户态的异常分发函数KiUserExceptionDispatcher()接手继续处理，处理的方式也很简单，三步走，第一步便是遍历VEH，没人处理的话，那就进行第二步，接着遍历SEH，也同样没人处理，那就到了UEH了，无他，系统默认的处理方式便是拉起WerFault.exe这个进程，然后挂掉整个进程；其实还有最后一个第三步，那就是VCH，不过这个VCH比较特殊，依赖于“别人”；关于这个异常分发，从CPU到内核再到用户态，以及双击调试时，内核调试引擎的调试数据包与Windbg之间的交互后边会专门撰文讲解，这里大家就先简单了解下就好；回到正题，加了这层
**try**
except就是为了在SEH遍历的过程中，拦截住这个异常，并且进行一些修改，去掉Windbg丢下的断点，这也正是很多软件开发商特别是游戏开发商做保护时用到的技术手段；

简单的分析下，在SEH中我们调用了
VirtualProtect()修改内存属性，改为可读可写可执行，下边紧接着就是将异常发生的地址处的数据改为0x8B，为什么是0x8B下边demo演示时会有讲解；然后返回

EXCEPTION_CONTINUE_EXECUTION，告知内核调试引擎，继续刚刚触发异常的地方执行；

3、主线程中就是一个简单的死循环，不停的打印线程ID，与工作线程中的形成对比，我们做实验时，分别在工作线程和主线程的printf处下断点，看看效果；

###  2.2 演示过程及效果见下图讲解

实验1：

先把TestThreadHideFromDebugger()中设置线程调试逃逸的代码注释掉，看看工作线程是否能够命中断点断下来:  
  
是OK的，下边我们就模拟游戏的做法，来实际感受下这个技术的利用手段；

实验2：  
  
先如图1所示，在这两个地方下断点，当图1的断点命中时，看一下工作线程中printf处断点所对应的地址和字节码，这两个信息我们后边有用；再如图2所示，先屏蔽掉修改内存属性的代码，看看执行效果；如下图图3和图4所示：

![](https://p1.ssl.qhimg.com/t016e0617b6afe79ece.png)

![](https://p1.ssl.qhimg.com/t011daf55797112310a.png)

如预期，我们在工作线程的printf处下了断点，当程序执行到此处时，调试器并没有接管到该断点异常，相反我们的异常处理try
except接管到了，原因就是我上边讲的；在异常处理中，我们打印出了异常触发即断点指令的代码地址即0x011A1AB8，图3和图4是吻合的，并且我们在异常处理中也弹出了消息框，按照图2的方式，我们没有修改0x011A1AB8处的代码，按理说这里还是int
3，那么我们点完确定按钮，消息框关闭后，CPU又会返回到该出继续执行int
3，这样又会继续到我们的异常处理程序中，消息框又会再次弹出，如此重复，大家可尝试看看效果；

实验2：

将图2中注释掉的代码恢复回来，如下图所示：  
  
此时，消息框只会弹一次，因为后续CPU再回去继续执行时，代码已经不是int3所对应的0xCC了，而是被我们复原了，那CPU再次执行时，当然不会再次报告异常；这便是很多软件中反调试用到的技术手段的全部内容，当然游戏里边反调试用这个方法的更多，特别是韩国的游戏保护；

## 3、OS实现该调试逃逸的原理逆向分析

###  3.1、用户态逆向分析NtSetInformationThread()的内部动作

![](https://p5.ssl.qhimg.com/t010178b2a087b154bd.png)

如上图所示，NtSetInformationThread()内部啥也没干，直接进了内核，只不过进内核时，会判断下用那种方式进，当前架构下有很多种进内核的方式，比如调用门，中断门，陷阱门，。。。Windows系统早先用的是陷阱门，索引号为0x2E，即IDT表中的0x2E号；后来intel为了提升模式切换的性能，搞了个快速调用，即syscall指令；这个有兴趣的可以去了解下；有一个比较重要的是，0x7FFE0308这个是直接写死的额，看着是全局变量，那这个全局变量指向的数据结构是什么呢？
如下，这块内存是Ring3和Ring0共享的，Ring3只读权限，Ring0可读可写；两个虚拟地址空间映射到同一个物理页上，很简单，搞一下页表即可；这个页剩下的地址空间可以做很多事情，大家可以尝试想想；

    
    
    0:012> dt _KUSER_SHARED_DATA
    ntdll!_KUSER_SHARED_DATA
       +0x000 TickCountLowDeprecated : Uint4B
       +0x004 TickCountMultiplier : Uint4B
       +0x008 InterruptTime    : _KSYSTEM_TIME
       +0x014 SystemTime       : _KSYSTEM_TIME
       +0x020 TimeZoneBias     : _KSYSTEM_TIME
       +0x02c ImageNumberLow   : Uint2B
       +0x02e ImageNumberHigh  : Uint2B
       +0x030 NtSystemRoot     : [260] Wchar
       +0x238 MaxStackTraceDepth : Uint4B
       +0x23c CryptoExponent   : Uint4B
       +0x240 TimeZoneId       : Uint4B
       +0x244 LargePageMinimum : Uint4B
       +0x248 AitSamplingValue : Uint4B
       +0x24c AppCompatFlag    : Uint4B
       +0x250 RNGSeedVersion   : Uint8B
       +0x258 GlobalValidationRunlevel : Uint4B
       +0x25c TimeZoneBiasStamp : Int4B
       +0x260 NtBuildNumber    : Uint4B
       +0x264 NtProductType    : _NT_PRODUCT_TYPE
       +0x268 ProductTypeIsValid : UChar
       +0x269 Reserved0        : [1] UChar
       +0x26a NativeProcessorArchitecture : Uint2B
       +0x26c NtMajorVersion   : Uint4B
       +0x270 NtMinorVersion   : Uint4B
       +0x274 ProcessorFeatures : [64] UChar
       +0x2b4 Reserved1        : Uint4B
       +0x2b8 Reserved3        : Uint4B
       +0x2bc TimeSlip         : Uint4B
       +0x2c0 AlternativeArchitecture : _ALTERNATIVE_ARCHITECTURE_TYPE
       +0x2c4 BootId           : Uint4B
       +0x2c8 SystemExpirationDate : _LARGE_INTEGER
       +0x2d0 SuiteMask        : Uint4B
       +0x2d4 KdDebuggerEnabled : UChar
       +0x2d5 MitigationPolicies : UChar
       +0x2d5 NXSupportPolicy  : Pos 0, 2 Bits
       +0x2d5 SEHValidationPolicy : Pos 2, 2 Bits
       +0x2d5 CurDirDevicesSkippedForDlls : Pos 4, 2 Bits
       +0x2d5 Reserved         : Pos 6, 2 Bits
       +0x2d6 Reserved6        : [2] UChar
       +0x2d8 ActiveConsoleId  : Uint4B
       +0x2dc DismountCount    : Uint4B
       +0x2e0 ComPlusPackage   : Uint4B
       +0x2e4 LastSystemRITEventTickCount : Uint4B
       +0x2e8 NumberOfPhysicalPages : Uint4B
       +0x2ec SafeBootMode     : UChar
       +0x2ed VirtualizationFlags : UChar
       +0x2ee Reserved12       : [2] UChar
       +0x2f0 SharedDataFlags  : Uint4B
       +0x2f0 DbgErrorPortPresent : Pos 0, 1 Bit
       +0x2f0 DbgElevationEnabled : Pos 1, 1 Bit
       +0x2f0 DbgVirtEnabled   : Pos 2, 1 Bit
       +0x2f0 DbgInstallerDetectEnabled : Pos 3, 1 Bit
       +0x2f0 DbgLkgEnabled    : Pos 4, 1 Bit
       +0x2f0 DbgDynProcessorEnabled : Pos 5, 1 Bit
       +0x2f0 DbgConsoleBrokerEnabled : Pos 6, 1 Bit
       +0x2f0 DbgSecureBootEnabled : Pos 7, 1 Bit
       +0x2f0 DbgMultiSessionSku : Pos 8, 1 Bit
       +0x2f0 DbgMultiUsersInSessionSku : Pos 9, 1 Bit
       +0x2f0 DbgStateSeparationEnabled : Pos 10, 1 Bit
       +0x2f0 SpareBits        : Pos 11, 21 Bits
       +0x2f4 DataFlagsPad     : [1] Uint4B
       +0x2f8 TestRetInstruction : Uint8B
       +0x300 QpcFrequency     : Int8B
       +0x308 SystemCall       : Uint4B
       +0x30c SystemCallPad0   : Uint4B
       +0x310 SystemCallPad    : [2] Uint8B
       +0x320 TickCount        : _KSYSTEM_TIME
       +0x320 TickCountQuad    : Uint8B
       +0x320 ReservedTickCountOverlay : [3] Uint4B
       +0x32c TickCountPad     : [1] Uint4B
       +0x330 Cookie           : Uint4B
       +0x334 CookiePad        : [1] Uint4B
       +0x338 ConsoleSessionForegroundProcessId : Int8B
       +0x340 TimeUpdateLock   : Uint8B
       +0x348 BaselineSystemTimeQpc : Uint8B
       +0x350 BaselineInterruptTimeQpc : Uint8B
       +0x358 QpcSystemTimeIncrement : Uint8B
       +0x360 QpcInterruptTimeIncrement : Uint8B
       +0x368 QpcSystemTimeIncrementShift : UChar
       +0x369 QpcInterruptTimeIncrementShift : UChar
       +0x36a UnparkedProcessorCount : Uint2B
       +0x36c EnclaveFeatureMask : [4] Uint4B
       +0x37c TelemetryCoverageRound : Uint4B
       +0x380 UserModeGlobalLogger : [16] Uint2B
       +0x3a0 ImageFileExecutionOptions : Uint4B
       +0x3a4 LangGenerationCount : Uint4B
       +0x3a8 Reserved4        : Uint8B
       +0x3b0 InterruptTimeBias : Uint8B
       +0x3b8 QpcBias          : Uint8B
       +0x3c0 ActiveProcessorCount : Uint4B
       +0x3c4 ActiveGroupCount : UChar
       +0x3c5 Reserved9        : UChar
       +0x3c6 QpcData          : Uint2B
       +0x3c6 QpcBypassEnabled : UChar
       +0x3c7 QpcShift         : UChar
       +0x3c8 TimeZoneBiasEffectiveStart : _LARGE_INTEGER
       +0x3d0 TimeZoneBiasEffectiveEnd : _LARGE_INTEGER
       +0x3d8 XState           : _XSTATE_CONFIGURATION
    

比较有意思的一些字段如TimeZoneId、KdDebuggerEnabled、DbgSecureBootEnabled、SystemCall、ImageFileExecutionOptions等等

###  3.2、内核态逆向分析NtSetInformationThread()的内部动作

说明下，我这里分析的是基于Win10
16299版本的ntoskrnl.exe这份文件；这个函数比较大，从IDA给出来的数据看，有一千多行，分几次截图，给出关键的代码数据进行分析；

![](https://p0.ssl.qhimg.com/t01967af7a6de359382.png)

函数的原型如上所示，函数实现关键部分如下图所示：

![](https://p4.ssl.qhimg.com/t012e2192bdb27adb49.png)

![](https://p5.ssl.qhimg.com/t01b88806211511cb00.png)

![](https://p3.ssl.qhimg.com/t011abf32926b2f1308.png)

上边的代码简单解释下，代码中根据ThreadInformationClass对其做了简单的归类，根据我们传入的ThreadHideFromDebugger对应的数据是0x11，会执行go
LABEL_5;到了这个标签这，会顺序执行，最终来到第245行，按着这个if比较往下走，最终会来到下图所示的部分：

![](https://p2.ssl.qhimg.com/t0190c3124f9c63b4d7.png)

由上图所示，先一个if判断，判断传入的参数ThreadInformationLength是否为0，如果不是则直接返回错误，且错误码为0xC0000004，在全面的demo中，知道该参数传入的确实为0；紧接着下边调用ObpReferenceObjectByHandleWithTag()根据现场的句柄找到线程对象；通过第三个参数返回，即Thread；紧接着调用了InterlockedOr()，这个API是实现原子或操作的；但IDA给出的伪代码不太好，字段解析的有问题，我们看下反汇编代码，如下：

![](https://p0.ssl.qhimg.com/t01b15dc6da9c393c3a.png)

下边我们需要看下ETHREAD的0x6D0偏移处的字段是什么，直接用Windbg双机调试看下是最快的如下：

![](https://p2.ssl.qhimg.com/t019d530fca0ecd7ccc.png)

原来是设置的这个地方的HideFromDebugger位置，将其位置1；OK；NtSetInformationThread()的分析还差最后一步；即返回，如下图：

![](https://p0.ssl.qhimg.com/t0141930a2c0057ae75.png)

就直接返回了，简单明了；

###  3.3、OS在异常分发时，又是如何利用此数据的

想要知道如何使用的，最简单的办法就是在刚在这个位置，针对特定的线程下内存访问断点，直接命中就能通过栈回溯来找到；这个就留给大家自己去完成了；我们下边直接分析；张银奎老师那本《软件调试》书上有专门针对异常分析的具体讲解，核心的API有这么一个DbgkForwardException()；下面我们来逆向分析下这个API；

![](https://p5.ssl.qhimg.com/t0194e60e72e54a473c.png)

但是IDA反汇编的不好，为什么这么说呢？内核里几乎很少会用到TEB的东西，因为TEB里有的数据ETHREAD中都有，此外，这里访问TEB时也没加_try
_except，所以这里反汇编出来的伪代码很不好，我们直接看反汇编代码更为清晰，汇编代码如下：

![](https://p5.ssl.qhimg.com/t01fbb2ca7a8632d863.png)

有一些辅助知识，需要说明下，在x64架构的内核里，gs寄存器保存的是KPCR的基地址，KPCR是内核里，操作系统为每个CPU核维护的一份数据结构；该结构如下：

![](https://p5.ssl.qhimg.com/t011837f60c42d15140.png)

KPRCB作为KPCR的拓展字段，里边记录的数据更多，很多字段也都是非常常用的；其中有三个非常重要的字段：  
+0x008 CurrentThread : Ptr64 _KTHREAD：指向当前CPU正在执行的代码所属的线程的线程对象，即当前被调度到的线程对象；

+0x010 NextThread : Ptr64 _KTHREAD： 指向下一次调度时，需要调度的线程对象；

+0x018 IdleThread : Ptr64
_KTHREAD：指向当没有线程可调度时，可被调度的线程对象，这个线程一般做一些清理动作，比如清理内存，整理内存的那几个链表等等；优先级非常低；

看看上边的这个偏移，大概你也应该猜测到了吧，

    
    
    mov     rax, gs:188h
    mov     ecx, [rax+6D0h]
    test    cl, 4
    jnz     short loc_14044BDE0
    

这个指令就是获取的CurrentThread，然后取的偏移0x6D0处的数据；而这个0x6D0在上边也已经就分析过了，恰为_KTHREAD.HideFromDebugger；喔喔，异常分发函数DbgkForwardException()在分发异常时，查看了这个数据；如果这里置位了的话，那么逻辑就如下图所示了：

![](https://p2.ssl.qhimg.com/t014e17bb72028ad907.png)

直接返回了，也就意味了不发送给调试器了，这就是线程调试逃逸的全部原理了；

## 4、总结

在本文中，自己编码实现了线程调试逃逸，学会运用这里技术手段；详细讲解了实现的技术细节，特别的讲解了为什么需要加一层try
except；而后我们由通过逆向手段来详细分析了OS是如何实现这一技术的，并且详细分析了在CPU触发报告异常到OS接管异常进行异常分发时是如何利用此数据达到对调试器隐藏线程异常的；特别的还拓展介绍了gs寄存器在x64架构下，内核是如何使用的；涉及到了KPCR，KPRCB等等关键数据结构；至此，整个技术点全部剖析完毕。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **void *** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/213421](/post/id/213421)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [调试逃逸](/tag/调试逃逸)
  * [内核逆向](/tag/内核逆向)

 **+1** __7赞

 __收藏

![](https://p5.ssl.qhimg.com/t013c5d4d3bc7c086d8.jpg) void *

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

