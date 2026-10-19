作者：Leeqwind  
作者博客：<https://xiaodaozhi.com/exploit/29.html>

这篇文章翻译自一篇多年之前的论文，原文系统地描述了 win32k 的用户模式回调机制以及相关的原理和思想，可以作为学习 win32k
漏洞挖掘的典范。早前曾经研读过，近期又翻出来整理了一下翻译，在这里发出来做个记录。原文链接在文后可见。

#### 摘要

十五年之前，Windows NT 4.0 引入了 win32k.sys 来应对旧的客户端-服务端图形子系统模型的固有限制。至今为止，win32k.sys
仍旧是 Windows 架构的基础组件之一，管理着窗口管理器（User）和图形设备接口（GDI）。为了更精确地与用户模式数据相连接，win32k.sys
使用了用户模式回调：一种允许内核反向调用到用户模式的机制。用户模式回调启用各种任务，例如调用应用程序定义的挂钩、提供事件通知，以及向/从用户模式拷贝数据等。在这篇文章中，我们将讨论涉及在
win32k 中用户模式回调的很多挑战和问题。我们将特别展示 win32k
的全局锁机制依赖性在提供一个线程安全环境时与用户模式回调的思想融合时的缺陷。虽然与用户模式回调有关的很多漏洞已被修补，但它们的复杂特性表明，仍有更多潜在的缺陷可能仍旧存在于
win32k 中。因此，为了缓解一些更加普遍的 BUG 类型，关于对用户自身来说如何预防将来可能遭受的内核攻击，我们将总结性地提出一些建议。

关键词：win32k，用户模式回调，漏洞

#### 1\. 简介

在 Windows NT 中，Win32 环境子系统允许应用程序与 Windows
操作系统相连接，并与像窗口管理器（User）和图形设备接口（GDI）这样的组件进行交互。子系统提供一组统称为 Win32 API
的函数，并遵循一个主从式模型，在该模型中客户端应用程序与更高特权级的服务端组件进行交互。

传统情况下，Win32 子系统的服务端在客户端-服务端运行时子系统（CSRSS）中执行。为了提供最佳性能，每个客户端的线程在 Win32
服务端都有一个对应的线程，在一种被称作快速 LPC 的特殊的进程间通信装置中等待。由于在快速 LPC
中配对线程之间的切换不需要内核中的调度事件，服务端线程能够在抢占式线程调度程序中轮到其执行之前，执行客户端线程的剩余时间片。另外，在大数据传递和向客户端提供对服务端管理的数据结构的只读访问时使用共享内存，用来最小化在客户端和
Win32 服务端之间进行切换的需要。

虽然在 Win32 子系统中进行了性能优化，微软仍决定在 Windows NT 4.0 版本中将大部分服务端组件移至内核模式实现。这导致了
win32k.sys
的引入，一个负责管理窗口管理器（User）和图形设备接口（GDI）的内核模式驱动程序。通过拥有更少的线程和上下文的切换（并使用更快的用户/内核模式传递）以及减少的内存需求，到内核模式的迁移极大地减少了与陈旧的子系统设计有关的开销。然而，由于与在同一特权级下的直接代码/数据访问相比，用户/内核模式传递仍是相对缓慢的，因此在客户端地址空间的用户模式部分中，例如管理器结构缓存之类的一些陈旧机制仍旧被维持下来。此外，一些管理器结构被特地存储在用户模式下，以避免环的传递。由于
win32k 需要一种访问这些信息并支持例如窗口挂钩的基础功能的途径，它需要一种途径来传递对用户模式客户端的控制。这通过用户模式回调机制实现。

用户模式回调允许 win32k
反向调用到用户模式并执行像调用应用程序定义的挂钩、提供事件通知，以及向/从用户模式拷贝数据之类的任务。在这篇文章中，我们将讨论涉及 win32k
中的用户模式回调的很多挑战和问题。我们将特别展示 win32k
在维护数据完整性（例如在依赖全局锁机制方面）方面的设计与用户模式回调的思想融合时的缺陷。最近，MS11-034 [7] 和 MS11-054 [8]
修复了一些漏洞，以实现修复多种与用户模式回调相关的 BUG
的目的。然而，由于其中一些问题的复杂特性，以及用户模式回调的普遍应用，更多潜在的缺陷很可能仍旧存在于 win32k 中。因此，为了缓解一些更加普遍的 BUG
种类，关于对微软和终端用户来说能够做的进一步缓解在将来 win32k 子系统中遭受攻击风险的事情，我们总结性地讨论一些观点。

这篇文章的剩余部分组织如下。在第 2 节，我们将审查必要的背景材料，来理解这篇文章的剩余部分，专注于用户对象和用户模式回调。在第 3 节，我们将讨论在
win32k 中的函数命名修饰，并将展示针对 win32k 和用户模式回调的某些特殊的漏洞种类。在第 4
节，我们将评估被用户模式回调触发的漏洞的利用，同时在第 5 节将尝试为普遍漏洞种类提出缓解措施以应对这些攻击。

最后，在第 6 节我们将就 win32k 的未来提供的一些想法和建议，并在第 7 节提出这篇文章的结论。

#### 2\. 背景

在这一节中，我们审查必要的背景信息来理解这篇文章的剩余部分。在移步更多像窗口管理器（专注于用户对象）和用户模式回调机制这样的特定组件之前，我们从简要地介绍
Win32k 和它的架构开始。

##### 2.1 Win32k

微软在 Windows NT 4.0 的改变中将 Win32k.sys 作为改变的一部分而引入，用以提升图形绘制性能并减少 Windows
应用程序的内存需求
[10]。窗口管理器（User）和图形设备接口（GDI）在极大程度上被移出客户端/服务端运行时子系统（CSRSS）并被落实在它自身的一个内核模块中。在
Windows NT 3.51 中，图形绘制和用户接口管理由 CSRSS
通过在应用程序（客户端）和子系统服务端进程（CSRSS.EXE）之间使用一种快速形式的进程间通信机制来执行。虽然这种设计已被进行过性能优化，但是
Windows 的图形集约化特性导致开发人员转向一种通过更快的系统调用的方式的基于内核的设计。

Win32k 本质上由三个主要的组件组成：图形设备接口（GDI），窗口管理器（User），以及针对 DirectX 的形实替换程序，以支持包括
Windows XP/2000 和 LongHorn（Vista）在内的操作系统的显示驱动模型（有时也可认为是 GDI 的一部分）。窗口管理器负责管理
Windows
用户接口，例如控制窗口显示，管理屏幕输出，收集来自键盘和鼠标的输入，并向应用程序传递消息。图形设备接口（GDI），从另一方面来说，主要与图形绘制和落实
GDI 对象（笔刷，钢笔，Surface，设备上下文，等等）、图形绘制引擎（Gre）、打印支持、ICM 颜色匹配、一个浮点数学库以及字体支持有关。

与 CSRSS 的传统子系统设计被建立在每个用户一个进程的基础上相类似地，每个用户会话拥有它自己的 win32k.sys 映射副本。会话的概念也允许
Windows 在用户之间提供一个更加严格的隔离（又称会话隔离，session isolation）。从 Windows Vista
开始，服务也被移至它自己的非交互式会话 [2] 中，用来避免一系列与共享会话相关的问题，例如粉碎窗口攻击 [12]
和特权服务漏洞。此外，用户接口特权隔离（UIPI） [1] 实施完整级别的概念并确保低特权级的进程不能干扰（例如发送消息给）拥有高完整性的进程。

为了与 NT 执行体进行适当的连接，win32k 注册若干呼出接口（Callout，PsEstablishWin32Callouts）来支持面向 GUI
的对象，例如桌面和窗口站。重要的是，win32k 也为线程和进程注册呼出接口来定义 GUI 子系统使用的每线程和每进程结构体。

    
    
    int __stdcall PsEstablishWin32Callouts(int a1)
    {
      int result; // eax@1
    
      PspW32ProcessCallout = *(int (__stdcall **)(_DWORD, _DWORD))a1;
      PspW32ThreadCallout = *(int (__stdcall **)(_DWORD, _DWORD))(a1 + 4);
      ExGlobalAtomTableCallout = *(_DWORD (__stdcall **)())(a1 + 8);
      KeGdiFlushUserBatch = *(_DWORD *)(a1 + 28);
      PopEventCallout = *(_DWORD *)(a1 + 12);
      PopStateCallout = *(_DWORD *)(a1 + 16);
      PopWin32InfoCallout = *(_DWORD *)(a1 + 20);
      PspW32JobCallout = *(_DWORD *)(a1 + 24);
      ExDesktopOpenProcedureCallout = *(_DWORD *)(a1 + 32);
      ExDesktopOkToCloseProcedureCallout = *(_DWORD *)(a1 + 36);
      ExDesktopCloseProcedureCallout = *(_DWORD *)(a1 + 40);
      ExDesktopDeleteProcedureCallout = *(_DWORD *)(a1 + 44);
      ExWindowStationOkToCloseProcedureCallout = *(_DWORD *)(a1 + 48);
      ExWindowStationCloseProcedureCallout = *(_DWORD *)(a1 + 52);
      ExWindowStationDeleteProcedureCallout = *(_DWORD *)(a1 + 56);
      ExWindowStationParseProcedureCallout = *(_DWORD *)(a1 + 60);
      result = *(_DWORD *)(a1 + 68);
      ExWindowStationOpenProcedureCallout = *(_DWORD *)(a1 + 64);
      ExLicensingWin32Callout = result;
      return result;
    }

GUI 线程和进程

由于并不是所有的线程都使用 GUI 子系统，预先为所有的线程分配 GUI 结构体将造成空间浪费。因此，在 Windows 中，所有的线程都作为非 GUI
线程启动（12 KB 栈）。如果某线程访问任意 USER 或 GDI 系统调用（调用号 >= 0x1000），Windows 将该线程提升为 GUI
线程（nt!PsConvertToGuiThread）并调用进程和线程呼出接口。GUI 线程在极大程度上拥有一个更大的线程栈，用来来更好地处理 win32k
的递归特性，以及更好地支持会为陷阱帧和其他元数据请求额外栈空间（在 Vista 及更新的系统中，用户模式回调使用专用的内核线程栈）的用户模式回调。

    
    
    int __stdcall PsConvertToGuiThread()
    {
      _KTHREAD *Thread; // esi@1
      int result; // eax@2
    
      Thread = KeGetCurrentThread();
      if ( !Thread->PreviousMode )
      {
        return 0xC000000D;
      }
      if ( !PspW32ProcessCallout )
      {
        return 0xC0000022;
      }
      if ( Thread->ServiceTable != &KeServiceDescriptorTable )
      {
        return 0x4000001B;
      }
    
      result = PspW32ProcessCallout(Thread->ApcState.Process, 1);
      if ( result >= 0 )
      {
        Thread->ServiceTable = &KeServiceDescriptorTableShadow;
        result = PspW32ThreadCallout(Thread, 0);
        if ( result < 0 )
          Thread->ServiceTable = &KeServiceDescriptorTable;
      }
      return result;
    }

当进程的线程首次被转换成 GUI 线程并调用 W32pProcessCallout 时，win32k 将调用
win32k!xxxInitProcessInfo 来初始化每进程 W32PROCESS/PROCESSINFO 结构体（W32PROCESS 是
PROCESSINFO 的子集， 处理 GUI 子系统，而 PROCESSINFO 还包含特定于 USER 子系统的信息）。该结构体具体保存针对于每个进程的
GUI 相关的信息，例如相关联的桌面、窗口站，以及用户和 GDI 句柄计数。在调用 win32k!xxxUserProcessCallout 初始化
USER 相关的域及随后调用 GdiProcessCallout 初始化 GDI 相关的域之前，该函数通过调用
win32k!xxxAllocateW32Process 分配结构体自身。

另外，win32k 也为所有被转换为 GUI 线程的线程初始化一个每线程 W32THREAD/THREADINFO 结构体。该结构体存储与 GUI
子系统相关的特定信息，例如线程消息队列中的信息，注册的窗口挂钩，所有者桌面，菜单状态，等等。在这里，W32pThreadCallout 调用
win32k!AllocateW32Thread 来分配该结构体，随后调用 GdiThreadCallout 和 UserThreadCallout
来初始化 GUI 和 USER 子系统各自特有的信息。在该处理过程中最重要的函数是
win32k!xxxCreateThreadInfo，其负责初始化线程信息结构体。

##### 2.2 窗口管理器

窗口管理器的重要功能之一是追踪实体，例如窗口，菜单，光标，等等。其通过将此类实体表示为用户对象来实现该功能，并通过用户会话维护自身句柄表来追踪这些实体的使用。这样一来，当应用程序请求在某个用户实体中执行行为时，将提供自己的句柄值，句柄管理器将这个句柄有效地映射在内核内存中对应的对象。

用户对象

用户对象被划分成不同的类型，从而拥有它们自己类型的特定结构体。例如，所有的窗口对象由 win32k!tagWND 结构体定义，而菜单由
win32k!tagMENU 结构体定义。虽然对象类型在结构上不同，但它们都共享一个通用的被称为 HEAD 结构体的头部。

HEAD
结构体存储句柄值（h）的一份副本，以及一个锁计数（cLockObj），每当某对象被使用时其值增加。当该对象不再被一个特定的组件使用时，它的锁计数减小。在锁计数达到零的时候，窗口管理器知道该对象不再被系统使用然后将其释放。

    
    
    typedef struct _HEAD {
        HANDLE    h;
        ULONG32   cLockObj;
    } HEAD, *PHEAD;

虽然 HEAD 结构体相当小，但很多时候对象使用像 THRDESKHEAD 和 PROCDESKHEAD
这样的进程和线程特有的头结构体。这些结构体提供一些特殊的域，例如指向线程信息结构体 tagTHREADINFO
的指针，和指向关联的桌面对象（tagDESKTOP）的指针。通过提供这些信息，Windows
能够限制对象在其他桌面中被访问，并因此提供桌面间隔离。同样地，由于此类对象通常被一个线程或进程所有，共存于同一桌面的线程和进程间的隔离也能够被实现。例如，一个线程不能通过简单地调用
DestroyWindow
销毁其他线程创建的对象，而是需要发送一个经过完整性级别检查等额外校验的窗口消息。然而，对象间隔离并未规定成一种统一集中的方式，任何不做必要检查的函数都能够允许攻击者用以绕过这个限制。不可否认，这是引入高特权级的服务和已登录用户会话之间的会话间隔离（session
separation，Vista
及更新）的原因之一。由于运行在同一会话中的所有进程共享同一个用户句柄表，低特权级的进程能够潜在地发送消息给某个高特权级的进程，或者与后者所拥有的对象进行交互。

句柄表

所有的用户句柄被索引在所属会话的句柄表中。该句柄表在 win32k!Win32UserInitialize 函数中被初始化，每当 win32k
的新实例被加载时调用该函数。句柄表自身存储在共享段的基地址（win32k!gpvSharedBase），同样在 Win32UserInitialize
函数中初始化。随后该共享段被映射进每个新的 GUI
进程，这样一来将允许进程在不发起系统调用的情况下从用户模式访问句柄表信息。将共享段映射进用户模式的决策被视为有益于改善性能，并且也被应用在基于非内核的
Win32 子系统中，用以缓解在客户端应用程序和客户端-服务端运行时子系统进程（CSRSS）之间频繁的上下文切换。在 Windows 7
中，在共享信息结构体（win32k!tagSHAREDINFO）中存在一个指向句柄表的指针。在用户模式（user32!gSharedInfo，仅
Windows 7）和内核模式（win32k!gSharedInfo）都存在一个指向该结构体的指针。

用户句柄表中的每项都被表示为 HANDLEENTRY
结构体。具体来说，该结构体包含关于其对象特定于句柄的信息，例如，指向对象自身的指针（pHead），它的所有者（pOwner），以及对象类型（bType）。所有者域要么是一个指向某进程或线程结构体的指针，要么是一个空指针（在这种情况下其被认为是一个会话范围的对象）。举个例子会是监视器或键盘布局/文件对象，其被认为在会话中是全局的。

    
    
    typedef struct _HANDLEENTRY {
        struct _HEAD* phead;
        VOID*         pOwner;
        UINT8         bType;
        UINT8         bFlags;
        UINT16        wUniq;
    } HANDLEENTRY, *PHANDLEENTRY;

用户对象的实际类型由 bType 值定义，并且在 Windows 7 下其取值范围从 0 到 21，可见下表。bFlags
域定义额外的对象标志，通常用来指示一个对象是否已被销毁。通常是这种情况：如果一个对象被请求销毁，但其锁计数非零值的话，它将仍旧存在于内存中。最后，wUniq
域作为用来计算句柄值的唯一计数器。句柄值以 handle = table_entry_id | (wUniq << 0x10)
的方式计算。当对象被释放时，计数器增加，以避免后续的对象立即复用之前的句柄。应当指出的是，由于 wUniq 只有区区 16
比特位，导致当足够多的对象被分配和释放时其值将会回绕的现象，所以这种机制不应被当作是一种安全特性。

    
    
    ID  TYPE              OWNER        MEMORY
     0  Free
     1  Window            Thread       Desktop Heap / Session Pool
     2  Menu              Process      Desktop Heap
     3  Cursor            Process      Session Pool
     4  SetWindowPos      Thread       Session Pool
     5  Hook              Thread       Desktop Heap
     6  Clipboard Data                 Session Pool
     7  CallProcData      Process      Desktop Heap
     8  Accelerator       Process      Session Pool
     9  DDE Access        Thread       Session Pool
    10  DDE Conversation  Thread       Session Pool
    11  DDE Transaction   Thread       Session Pool
    12  Monitor                        Shared Heap
    13  Keyboard Layout                Session Pool
    14  Keyboard File                  Session Pool
    15  Event Hook        Thread       Session Pool
    16  Timer                          Session Pool
    17  Input Context     Thread       Desktop Heap
    18  Hid Data          Thread       Session Pool
    19  Device Info                    Session Pool
    20  Touch (Win 7)     Thread       Session Pool
    21  Gesture (Win 7)   Thread       Session Pool

为了验证句柄的有效性，窗口管理器会调用任何 HMValidateHandle
API。这些函数将句柄值和句柄类型作为参数，并在句柄表中查找对应的项。如果查找到的对象具有所请求的类型，对象的指针将作为返回值被函数返回。

内存中的用户对象

在 Windows
中，用户对象和其相关的数据结构能够存在于桌面堆、共享堆或会话内存池中。通用规则是，与某个特定桌面相关的对象被存储在桌面堆中，其余对象被存储在共享堆中。然而，每个句柄类型的实际位置由一个被称作句柄类型信息表（win32k!ghati）的数据表定义。这个表保存针对每个句柄类型的属性，当分配或释放用户对象时，句柄管理器会用到该值。具体来说，句柄类型信息表中的每项由一个不透明的结构（未编制的）定义，该结构保存对象分配标记、类型标志，以及一个指向类型特定的销毁例程的指针。每当某对象锁计数到达零时，这个销毁例程就会被调用，在这种情况下窗口管理器调用类型特定的销毁例程来恰当地释放该对象。

临界区

不像 NT 执行体管理的对象那样，窗口管理器不会特定地锁定每一个用户对象，而是在 win32k
中通过使用临界区（资源）实行每个会话一个全局锁的机制。具体来说，操作用户对象或用户管理结构的每个内核例程（通常是 NtUser
系统调用）必须首先进入用户临界区（即请求 win32k!gpresUser 资源）。例如，更新内核模式结构体的函数，在修改数据之前，必须首先调用
UserEnterUserCritSec
并为独占访问请求用户资源。为减少窗口管理器中锁竞争的数量，只执行读取操作的系统调用进入共享的临界区（EnterSharedCrit）。这允许 win32k
实现某些并行处理而无视全局锁设计，因为多线程可能会同时执行 NtUser 调用。

##### 2.3 用户模式回调

Win32k
很多时候需要产生进入用户模式的反向调用来执行任务，例如调用应用程序定义的挂钩、提供事件通知、以及向/从用户模式拷贝数据等。这种调用通常被以用户模式回调
[11][3] 的方式提交处理。这种机制自身在 KeUserModeCallback 函数中执行，该函数被 NT 执行体导出，并执行很像反向系统调用的操作。

    
    
    NTSTATUS KeUserModeCallback (
      IN  ULONG     ApiNumber,
      IN  PVOID     InputBuffer,
      IN  ULONG     InputLength,
      OUT PVOID    *OutputBuffer,
      IN  PULONG    OutputLength
      );

当 win32k 产生一个用户模式回调时，它通过想要调用的用户模式函数的 ApiNumber 调用 KeUserModeCallback 函数。这里的
ApiNumber 是表示函数指针表（USER32!apfnDispatch）项的索引，在指定的进程中初始化 USER32.dll
期间该表的地址被拷贝到进程环境变量块（PEB.KernelCallbackTable）中。Win32k 通过填充 InputBuffer
缓冲区向相应的回调函数提供输入参数，并在 OutputBuffer 缓冲区中接收来自用户模式的输出。

    
    
    0:004> dps poi($peb+58)
    00000000`77b49500 00000000`77ac6f74 USER32!_fnCOPYDATA
    00000000`77b49508 00000000`77b0f760 USER32!_fnCOPYGLOBALDATA
    00000000`77b49510 00000000`77ad67fc USER32!_fnDWORD
    00000000`77b49518 00000000`77accb7c USER32!_fnNCDESTROY
    00000000`77b49520 00000000`77adf470 USER32!_fnDWORDOPTINLPMSG
    00000000`77b49528 00000000`77b0f878 USER32!_fnINOUTDRAG
    00000000`77b49530 00000000`77ae85a0 USER32!_fnGETTEXTLENGTHS
    00000000`77b49538 00000000`77b0fb9c USER32!_fnINCNTOUTSTRING

在调用一个系统调用时，nt!KiSystemService 或 nt!KiFastCallEntry
在内核线程栈中存储一个陷阱帧（TRAP_FRAME）来保存当前线程上下文，并使在返回到用户模式时能够恢复寄存器的值。为了在用户模式回调中实现到用户模式的过渡，KeUserModeCallback
首先使用由线程对象保存的陷阱帧信息将输入缓冲区拷贝至用户模式栈中，接着通过设为 ntdll!KiUserCallbackDispatcher 的 EIP
创建新的陷阱帧，代替线程对象的 TrapFrame 指针，最后调用 nt!KiServiceExit 返回对用户模式回调分发的执行。

由于用户模式回调需要一个位置存储例如陷阱帧等线程状态信息，Windows XP 和 2003
会扩大内核栈以确保足够的空间可用。然而，因为通过递归调用回调栈空间会被很快耗尽，Vista 和 Windows 7
转而在每个用户模式回调中创建新的内核线程栈。为了达到追踪先前的栈等目的，Windows 在栈的基地址位置为 KSTACK_AREA
结构体保留空间，紧随其后的是构造的陷阱帧。

    
    
    kd> dt nt!_KSTACK_AREA
       +0x000 FnArea                  : _FNSAVE_FORMAT
       +0x000 NpxFrame                : _FXSAVE_FORMAT
       +0x1e0 StackControl            : _KERNEL_STACK_CONTROL
       +0x1fc Cr0NpxState             : Uint4B
       +0x200 Padding                 : [4] Uint4B
    
    kd> dt nt!_KERNEL_STACK_CONTROL -b
       +0x000 PreviousTrapFrame       : Ptr32
       +0x000 PreviousExceptionList   : Ptr32
       +0x004 StackControlFlags       : Uint4B
       +0x004 PreviousLargeStack      : Pos 0, 1 Bit
       +0x004 PreviousSegmentsPresent : Pos 1, 1 Bit
       +0x004 ExpandCalloutStack      : Pos 2, 1 Bit
       +0x008 Previous                : _KERNEL_STACK_SEGMENT
          +0x000 StackBase               : Uint4B
          +0x004 StackLimit              : Uint4B
          +0x008 KernelStack             : Uint4B
          +0x00c InitialStack            : Uint4B
          +0x010 ActualLimit             : Uint4B

一旦用户模式回调执行完成，其将调用 NtCallbackReturn 来恢复并继续在内核中的执行。该函数将回调的结果复制回原来的内核栈，并通过使用保存在
KERNEL_STACK_CONTROL
结构体中的信息恢复原来的陷阱帧（PreviousTrapFrame）和内核栈。在跳转到其先前弃用的位置之前，内核回调栈将被删除。

    
    
    NTSTATUS NtCallbackReturn (
      IN PVOID Result OPTIONAL,
      IN ULONG ResultLength,
      IN NTSTATUS Status
      );

由于递归或嵌套回调会导致内核栈的无限增长（XP）或创建任意数目的栈，内核会为每个运行中的线程在线程对象结构体（KTHREAD->CallbackDepth）中追踪回调的深度（内核栈空间被用户模式回调完全使用）。在每个回调中，线程栈已使用的字节数（栈的基地址
- 栈指针）被加到 CallbackDepth 变量中。每当内核尝试迁移至新栈时，nt!KiMigrateToNewKernelStack 确保
CallbackDepth 总计不会超过 0xC000，否则将返回 STATUS_STACK_OVERFLOW 栈溢出的错误码。

#### 3\. 通过用户模式回调实施的内核攻击

在这一节中，我们将提出一些会允许对手从用户模式回调中执行特权提升的攻击载体。在更详细地讨论每个攻击载体之前，我们首先从研究用户模式回调如何处理用户临界区开始。

##### 3.1 Win32k 命名约定

像在 2.2 节中所描述的那样，在操作内部管理器结构体时，窗口管理器使用临界区和全局锁机制。由于用户模式回调能够潜在地允许应用程序冻结 GUI
子系统，win32k 总是在反向调用进用户模式之前离开临界区。通过这种方式，win32k
能够在用户模式代码正在执行的同时，执行其他任务。在从回调中返回时，在函数在内核中继续执行之前，win32k 重入临界区。我们可以在任何调用
KeUserModeCallback 的函数中观察到这种行为，如下面的指令片段所示。

    
    
    call   _UserSessionSwitchLeaveCrit@0
    lea    eax, [ebp+var_4]
    push   eax
    lea    eax, [ebp+var_8]
    push   eax
    push   0
    push   0
    push   43h
    call   ds:__imp__KeUserModeCallback@20
    call   _UserEnterUserCritSec@0

在从用户模式回调中返回时，win32k
必须确保被引用的对象和数据结构仍处于可预知的状态。由于在进入回调之前离开临界区，用户模式回调代码可随意修改对象属性、重分配数组，等等。例如，某个回调能够调用
SetParent()
函数来改变窗口的父级，如果内核在调用回调之前存储对父级窗口的引用，并在返回后在没有执行属性检查或对象锁定的情况下继续操作该引用，这将引发一处安全漏洞。

由于对潜在地反向调用至用户模式的函数的追踪非常重要（为了使开发者做出预防措施），win32k.sys 使用它自己的函数命名约定。需要注意的是，函数以 xxx
或 zzz 作为前缀取决于其会以何种方式调用用户模式回调。以 xxx
作为前缀的函数在大多数情况下离开临界区并调用用户模式回调。然而，在一些情况下函数可能会请求特定的参数以偏离回调实际被调用的路径。这就是为什么有时你会看到无前缀的函数调用
xxx 函数的原因，因为它们提供给 xxx 函数的参数不会引发一个回调。

以 zzz 作为前缀的函数调用异步或延时的回调。这通常是拥有确定类型的窗口事件的情况，因为各种各样的原因，不能或不应立刻进行处理。在这种情况下，win32k
调用 xxxFlushDeferredWindowEvents 来清理事件队列。对 zzz 函数来说需要注意的重要一点是，其要求在调用
xxxWindowEvent 之前确保 win32k!gdwDeferWinEvent 为非空值。如果不是这种情况，那么回调会被立即处理。

Win32k 使用的命名约定的问题是缺乏一致性。在 win32k
中一些函数调用回调，但是并未被视作其理应被视作的类型。这样的原因是不透明，但一个可能的解释是：随着时间的推移，函数已被修改，但没有更新函数名称的必要。因此，开发者可能会被误导地认为某个函数可能不会实际地调用回调，因此而避免做类似的不必要的验证（例如对象保持非锁定状态，以及指针不重新验证）。在
MS11-034 [7] 针对漏洞的应对方案中，有些函数名称已被更新成正确反映其对用户模式回调使用的格式。

    
    
    Windows 7 RTM          Windows 7 (MS11-034)
    MNRecalcTabStrings     xxxMNRecalcTabStrings
    FreeDDEHandle          xxxFreeDDEHandle
    ClientFreeDDEHandle    xxxClientFreeDDEHandle
    ClientGetDDEFlags      xxxClientGetDDEFlags
    ClientGetDDEHookData   xxxClientGetDDEHookData

##### 3.2 用户对象锁定

像在 2.2
节中所解释的那样，用户对象实行引用计数来追踪对象何时被使用及应该从内存中释放。正因如此，在内核离开用户临界区之后预期有效的对象必须被锁定。锁定通常有两种形式：线程锁定和赋值锁定。

线程锁定（Thread Locking）

线程锁定通常在某些函数中用来锁定对象或缓冲区。线程锁定的每个项被存储在线程锁定结构体中（win32k! _TL_
），通过单向的线程锁定链表连接，线程信息结构体中存在指向该链表的指针（THREADINFO.ptl）。在表项被 push 进或被 pop
出时，线程锁定链表的操作遵循先进先出（FIFO）队列原则。在 win32k 中，线程锁定一般内联地执行，并能够被内联的指针增量识别，通常在 xxx
函数调用之前（如下清单所示）。当给定的一个 win32k 中的函数不再需要对象或缓冲区时，其调用 ThreadUnlock()
来从线程锁定列表中删除锁定表项。

    
    
    mov    ecx, _gptiCurrent
    add    ecx, tagTHREADINFO.ptl  ; thread lock list
    mov    edx, [ecx]
    mov    [ebp+tl.next], edx
    lea    edx, [ebp+tl]
    mov    [ecx], edx              ; push new entry on list
    mov    [ebp+tl.pobj], eax      ; window object
    inc    [eax+tagWND.head.cLockObj]
    push   [ebp+arg_8]
    push   [ebp+arg_4]
    push   eax
    call   _xxxDragDetect@12       ; xxxDragDetect(x,x,x)
    mov    esi, eax
    call   _ThreadUnlock1@0        ; ThreadUnlock1()

在对象已被锁定但未被适当地解锁（例如由正在处理用户模式回调时的进程销毁导致）的情况下，在线程销毁时 win32k
处理线程锁定列表来释放任何遗留的表项。这可以在 xxxDestroyThreadInfo 函数中调用 DestroyThreadsObjects
函数时被观察到。

赋值锁定（Assignment Locking）

不像线程锁定那样，赋值锁定用于对用户对象实施更加长期的锁定。例如，当在一个桌面中创建窗口时，win32k
在窗口对象结构体中适当的偏移位置对桌面对象执行赋值锁定。与在列表中操作相反，赋值锁定项只是存储在内存中的（指向锁定对象的）指针。如果在 win32k
需要对某个对象执行赋值锁定的位置有已存在的指针，模块在锁定前会先解锁已存在的项，并用请求的项替换它。

句柄管理器提供提过执行赋值锁定和解锁的函数。在对对象执行锁定时，win32k 调用 HMAssignmentLock(Address,Object)
函数，并类似地调用 HMAssignmentUnlock(Address)
来释放对象引用。值得注意的是，赋值锁定不提供安全保障，但线程锁定会提供。万一线程在回调中被销毁，线程或用户对象清理例程自身负责逐个释放那些引用。如果不这样做，将会导致内存泄漏；如果该操作能被任意重复的话，也将导致引用计数溢出（在
64 位平台中，由于对象的 PointerCount 域的 64 位长度，导致似乎不可行）。

窗口对象释放后使用（CVE-2011-1237）

在安装计算机辅助训练（CBT）挂钩时，应用程序能够接收到各种关于窗口处理、键盘和鼠标输入，以及消息队列处理的通知。例如，在新窗口被创建之前，HCBT_CREATEWND
回调允许应用程序通过提供的 CBT_CREATEWND
结构体检查并修改用于确认窗口大小和轴向的参数。通过提供指向已有窗口（当前新窗口将会被插在该窗口的后面）的句柄（hwndInsertAfter），该结构体也允许应用程序选择窗口的层叠顺序。设置该句柄时，xxxCreateWindowEx
获取对应的对象指针，在后面将新窗口链入层叠顺序链表时会用到该对象指针。然而，由于该函数未能适当地锁定该指针，攻击者能够在随后的回调中销毁在
hwndInsertAfter 中提供的窗口，并在返回时迫使 win32k 操作已释放的内存。

获取关于 CBT_CREATEWND 更多信息请访问：<https://msdn.microsoft.com/zh-cn/ms644962>

在下面的清单中，xxxCreateWindowEx 调用 PWInsertAfter 来获取（使用 HMValidateHandleNoSecure）在
CBT_CREATEWND 挂钩结构体中提供的 hwndInsertAfter 句柄的窗口对象指针。随后函数将获取到的对象指针存储在一个局部变量中。

    
    
    .text:BF892EA1    push   [ebp+cbt.hwndInsertAfter]
    .text:BF892EA4    call   _PWInsertAfter@4             ; PWInsertAfter(x)
    .text:BF892EA9    mov    [ebp+pwndInsertAfter], eax   ; window object

由于 win32k 没有锁定 pwndInsertAfter，攻击者能够在随后的回调中释放在 CBT 挂钩中提供的窗口（例如通过调用
DestroyWindow 函数）。在 xxxCreateWindowEx 的末尾（如下清单所示），函数使用窗口对象指针并尝试将其链入（通过
LinkWindow
函数）窗口层叠顺序链表。由于该窗口对象可能已经不存在了，这就变成了一处“释放后使用”漏洞，允许攻击者在内核上下文中执行任意代码。我们将在第 4
节讨论“释放后使用”漏洞对用户对象的影响。

    
    
    .text:BF893924    push   esi              ; parent window
    .text:BF893925    push   [ebp+pwndInsertAfter]
    .text:BF893928    push   ebx              ; new window
    .text:BF893929    call   _LinkWindow@12   ; LinkWindw(x,x,x)

键盘布局对象释放后使用（CVE-2011-1241）

键盘布局对象用来为线程或进程设置活跃键盘布局。在加载键盘布局时，应用程序调用 LoadKeyboardLayout
并指定要加载的输入局部标识符的名称。Windows 也提供未文档化的 LoadKeyboardLayoutEx
函数，其接受一个额外的键盘布局句柄参数，在加载新布局之前 win32k 首先根据该句柄尝试卸载对应的布局。在提供该句柄时，win32k
没有锁定对应的键盘布局对象。这样一来，攻击者能够在用户模式回调中卸载提供的键盘布局并触发“释放后使用”条件。

在下面的清单中，LoadKeyboardLayoutEx 接受首先卸载的键盘布局的句柄并调用 HKLtoPKL 来获取键盘布局对象指针。HKLtoPKL
遍历活跃键盘布局列表（THREADINFO.spklActive）直到其找到与提供的句柄匹配的条目。LoadKeyboardLayoutEx
随后将对象指针存储在栈上的局部变量中。

    
    
    .text:BF8150C7    push   [ebp+hkl]
    .text:BF8150CA    push   edi
    .text:BF8150CB    call   _HKLtoPKL@8    ; get keyboard layout object
    .text:BF8150D0    mov    ebx, eax
    .text:BF8150D2    mov    [ebp+pkl], ebx ; store pointer

由于 LoadKeyboardLayoutEx 没有充分锁定键盘布局对象指针，攻击者能够在用户模式回调中卸载该键盘布局并且从而释放该对象。由于函数随后调用
xxxClientGetCharsetInfo
来从用户模式取回字符集信息，这种攻击手法是可能实现的。在下面的清单中，LoadKeyboardLayoutEx
继续使用之前存储的键盘布局对象指针，因此，其操作的可能是已释放的内存。

    
    
    .text:BF8153FC    mov    ebx, [ebp+pkl]   ; KL object pointer
    
    .text:BF81541D    mov    eax, [edi+tagTHREADINFO.ptl]
    .text:BF815423    mov    [ebp+tl.next], eax
    .text:BF815426    lea    eax, [ebp+tl]
    .text:BF815429    push   ebx
    .text:BF81542A    mov    [edi+tagTHREADINFO.ptl], eax
    .text:BF815430    inc    [ebx+tagKL.head.cLockObj]   ; freed memory ?

##### 3.3 对象状态验证

为了追踪对象是如何被使用的，win32k
将一些标志和指针与用户对象关联起来。对象假设在一个确定的状态，应该一直确保其状态是已验证的。用户模式回调能够潜在地修改状态并更新对象属性，例如改变一个窗口对象的父窗口、使一个下拉菜单不再被激活，或在
DDE 会话中销毁伙伴对象。缺乏对状态的检查会导致向空指针引用和释放后使用之类的 BUG，这取决于 win32k 如何使用对象。

DDE 会话状态漏洞

动态数据交换（DDE）协议是一种使用消息和共享内存在应用程序之间交换数据的遗留协议。DDE 会话在内部被窗口挂力气表示为 DDE
会话对象，发送者和接收者使用同一种对象定义。为了追踪哪个对象正忙于会话中以及会话对方的身份，会话对象结构体（未文档化）存储指向对方对象的指针（使用赋值锁定）。这样一来，如果拥有会话对象的窗口或线程销毁了，其在伙伴对象中存储的赋值锁定的指针未被解锁（清理）。

由于 DDE 会话在用户模式中存储数据，它们依靠用户模式回调来向/从用户模式拷贝数据。在发送 DDE 消息时，win32k 调用 xxxCopyDdeIn
从用户模式拷入数据。相似地，在接收到 DDE 消息时，win32k 调用 xxxCopyCopyDdeOut
将数据拷回到用户模式。在拷贝行为已发生之后，win32k 会通知伙伴会话对象对目标数据起作用，例如，其等待对方的应答。

在用于向/从用户模式拷入/出数据的用户模式回调处理之后，一些函数未能适当地重新验证伙伴会话对象。攻击者能够在用户模式回调中销毁会话，并从而在发送者或接收者对象结构体中解锁伙伴会话对象。在下面的清单中，我们看到在
xxxCopyDdeIn 函数中会调用回调，但在将伙伴会话对象指针传递给 AnticipatePost
之前，没有对其进行重新验证。这样反过来导致一个空指针引用，并允许攻击者通过映射零页（见第 4.3 节）来控制该会话对象。

    
    
    .text:BF8FB8A7    push   eax
    .text:BF8FB8A8    push   dword ptr [edi]
    .text:BF8FB8AA    call   _xxxCopyDdeIn@16
    .text:BF8FB8AF    mov    ebx, eax
    .text:BF8FB8B1    cmp    ebx, 2
    .text:BF8FB8B4    jnz    short loc_BF8FB8FC
    
    .text:BF8FB8C5    push   0              ; int
    .text:BF8FB8C7    push   [ebp+arg_4]    ; int
    .text:BF8FB8CA    push   offset _xxxExecuteAck@12
    .text:BF8FB8CF    push   dword ptr [esi+10h] ; conversation object
    .text:BF8FB8D2    call   _AnticipatePost@24

菜单状态处理漏洞

菜单管理是 win32k 中最复杂的组件之一，其中保存了想必起源于现代 Windows
操作系统早期时候的未知代码。虽然菜单对象（tagMENU）其自身如此简单，并且只包含与实际菜单项有关的信息，但是菜单处理作为一个整体依赖于多种十分复杂的函数和结构体。例如，在创建弹出菜单时，应用程序调用
TrackPopupMenuEx
在菜单内容显示的位置创建菜单类的窗口。接着该菜单窗口通过一个系统定义的菜单窗口类过程（win32k!xxxMenuWindowProc）处理消息输入，用以处理各种菜单特有的信息。此外，为了追踪菜单如何被使用，win32k
也将一个菜单状态结构体（tagMENUSTATE）与当前活跃菜单关联起来。通过这种方式，函数能够知道菜单是否在拖拽操作中调用、是否在菜单循环中、是否即将销毁，等等。

获取关于 TrackPopupMenuEx 更多信息请访问：<https://msdn.microsoft.com/zh-cn/ms648003>

在处理各种类型的菜单消息时，win32k 在用户模式回调之后没有对菜单进行适当的验证。特别是，当正在处理回调时关闭菜单（例如通过向菜单窗口类过程发送
MN_ENDMENU 消息），win32k
在很多情况下没有适当检查菜单是否仍处于活跃状态，或者被诸如弹出菜单结构体（win32k!tagPOPUPMENU）之类的有关结构体引用的对象指针是否不为空。在下面的清单中，win32k
通过调用 xxxHandleMenuMessages 尝试处理某种类型的菜单消息。由于该函数会调用回调，随后对菜单状态指针（ESI）的使用会造成
win32k 操作已释放的内存。原本可以通过使用 tagMENUSTATE 结构体（未编制的）中的 dwLockCount
变量来锁定窗口状态以避免这种特殊情况。

    
    
    push   [esi+tagMENUSTATE.pGLobalPopupMenu]
    or     [esi+tagMENUSTATE._bf4], 200h   ; fInCallHandleMenuMessages
    push   esi
    lea    eax, [ebp+var_1C]
    push   eax
    mov    [ebp+var_C], edi
    mov    [ebp+var_8], edi
    call   _xxxHandleMenuMessages@12   ; xxxHandleMenuMessages(x,x,x)
    and    [esi+tagMENUSTATE._bf4], 0FFFFFDFFh   ; <-- may have been freed
    mov    ebx, eax
    mov    eax, [esi+tagMENUSTATE._bf4]
    cmp    ebx, edi
    jz     short loc_BF968B0B   ; message processed ?

##### 3.4 缓冲区重新分配

很多用户对象拥有与它们相关联的条目数组或其他形式的缓冲区。在添加或删除元素时，条目数组通常被调整大小以节省内存。例如，如果元素个数大于或小于某个特定的阈值，缓冲区将会以更合适的大小重新分配。类似地，如果数组置空，缓冲区会被释放。重要的是，任何能够在回调期间被重新分配或释放的缓冲区都必须在返回时重新检查（如下图所示）。任何没有做重新检查的函数都可能会潜在地操作已释放地内存，从而允许攻击者控制赋值锁定的指针或损坏随后分配的内存。

![](https://images.seebug.org/content/images/2018/04/6e12b909-e026-4831-8a87-01f9cb19fdd0.jpg-w331s)

菜单条目数组释放后使用

为了追踪由弹出或下拉菜单保存的菜单条目，菜单对象（win32k!tagMENU）定义一个指向菜单条目数组的指针（rgItems）。每个菜单条目（win32k!tagITEM）定义一些属性，例如显示的字符串、内嵌图像、指向子菜单的指针等等。菜单对象结构体在
cItems 变量中追踪数组所包含条目的个数，并在 cAlloced
变量中追踪有多少条目能够适应所分配的缓冲区。在向/从菜单条目数组中添加/删除元素时，例如通过调用 InsertMenuItem() 或
DeleteMenu() 函数，如果 win32k 注意到 cAlloced 即将变得小于 cItems 变量（见下图所示），或者如果 cItems 和
cAlloced 变量差异超过 8 个条目，其将尝试调整数组大小。

![](https://images.seebug.org/content/images/2018/04/79030cf1-5279-49f8-827d-34ccab7b1b27.jpg-w331s)

win32k
中的一些函数在用户模式回调返回之后没有充分地验证菜单条目数组缓冲区。由于无法“锁定”菜单条目，像这样的具有用户对象的案例，要求任意能够调用回调的函数重新验证菜单条目数组。这同样适用于将菜单条目作为参数的函数。如果菜单条目数组缓冲区在用户模式回调中被重新分配，随后的代码将有可能操作已释放的内存或被攻击者控制的数据。

SetMenuInfo 函数允许应用程序设置指定菜单的各种属性。在设置了菜单信息结构体（MENUINFO）中的 MIM_APPLYTOSUBMENUS
标志掩码值的情况下，win32k 同时会将更新应用到菜单的所有子菜单。这种行为可以在 xxxSetMenuInfo
函数中观察到：函数遍历每个菜单条目项并递归处理每个子菜单以部署更新的设置。在处理菜单条目数组和产生任意递归调用之前，xxxSetMenuInfo
将菜单条目的个数（cItems）和菜单条目数组指针（rgItems）存储在局部变量/寄存器中（见下面的清单）。

    
    
    .text:BF89C779    mov    eax, [esi+tagMENU.cItems]
    .text:BF89C77C    mov    ebx, [esi+tagMENU.rgItems]
    .text:BF89C77F    mov    [ebp+cItems], eax
    .text:BF89C782    cmp    eax, edx
    .text:BF89C784    jz     short loc_BF89C7CC

一旦 xxxSetMenuInfo 的递归调用到达最深层的菜单，函数停止递归并处理菜单项。到这时，函数会通过调用 xxxMNUpdateShownMenu
来调用用户模式回调，从而可能允许调整菜单条目数组的大小。然而，当 xxxMNUpdateSHownMenu 返回后，xxxSetMenuInfo
在从递归调用返回时没有充分验证菜单条目数组缓冲区和存储在数组中的条目个数。如果在 xxxMNUpdateShownMenu
调用回调时，攻击者从该回调内部通过调用 InsertMenuItem() 或 DeleteMenu() 调整菜单条目数组的大小，那么下面清单中的 ebx
寄存器将可能指向已释放的内存。另外，由于 cItems 反映的是在函数调用的时间点上包含在数组中的元素个数，xxxSentMenuInfo
将可能会操作所分配数组之外的条目。

    
    
    .text:BF89C786    add    ebx, tagITEM.spSubMenu
    ...
    .text:BF89C789    mov    eax, [ebx]          ; spSubMenu
    .text:BF89C78B    dec    [ebp+cItems]
    .text:BF89C78E    cmp    eax, edx
    .text:BF89C790    jz     short loc_BF89C7C4
    ...
    .text:BF89C7B2    push   edi
    .text:BF89C7B3    push   dword ptr [ebx]
    .text:BF89C7B5    call   _xxxSetMenuInfo@8   ; xxxSetMenuInfo(x,x)
    .text:BF89C7BA    call   _ThreadUnlock1@0    ; ThreadUnlock1()
    .text:BF89C7BF    xor    ecx, ecx,
    .text:BF89C7C1    inc    ecx,
    .text:BF89C7C2    xor    edx, edx
    ...
    .text:BF89C7C4    add    ebx, 6Ch            ; next menu item
    .text:BF89C7C7    cmp    [ebp+cItems], edx   ; more items ?
    .text:BF89C7CA    jnz    short loc_BF89C789

为了应对在调用菜单条目处理时的漏洞，微软在 win32k 中引入了新的 MNGetpItemFromIntex
函数。该函数接受菜单对象指针和请求的菜单条目索引作为参数，并根据在菜单对象中提供的信息返回条目指针。

SetWindowPos 数组释放后使用

Windows 允许应用程序延时窗口位置更新，这样使多个窗口可以被同时更新。为此，Windows 使用一个特殊的 SetWindowPos
对象（SWP），该对象保存指向窗口位置结构体数组的指针。当应用程序调用 BeginDeferWindowPos() 时初始化 SWP
对象和这个数组。该函数接受数组元素（窗口位置结构体）的个数以对其进行预先分配。随后应用程序通过调用 DeferWindowPos()
将窗口位置的更新推迟到下一个可用的位置结构体被填充时。万一要求延时更新的数量超过预分配项的数量限制，win32k 用更合适的大小（4
个追加的项）重新分配数组。一旦所有要求的窗口位置更新都已被延时，应用程序调用 EndDeferWindowPos() 来处理窗口更新列表。

![](https://images.seebug.org/content/images/2018/04/af5d399f-b2a7-4d92-806e-d87581a34902.jpg-w331s)

在操作 SMWP 数组时，win32k 在用户模式回调之后并非总是适当地验证数组指针。在调用 EndDerWindowPos
来处理多窗口位置结构体时，win32k 调用 xxxCalcValidRects 来计算在 SMWP
数组中引用的每个窗口的位置和大小。该函数遍历每一项并执行各种操作，例如通知每个窗口它的位置正在改变（WM_WINDOWPOSCHANGING）。由于该消息会调用用户模式回调，攻击者能够对同一个
SWP 对象产生多次 DeferWindowPos 的调用来引发 SMWP 数组的重新分配（见下面的清单）。由于 xxxCalcValidRects
将窗口句柄写回原缓冲区中，这反过来会导致一个释放后使用漏洞。

    
    
    .text:BF8A37B8    mov ebx, [esi+14h]        ; SMWP array
    .text:BF8A37BB    mov [ebp+var_20], 1
    .text:BF8A37C2    mov [ebp+cItems], eax     ; SMWP array count
    .text:BF8A37C5    js loc_BF8A3DE3           ; exit if no entries
    ...
    .text:BF8A3839    push ebx
    .text:BF8A383A    push eax
    .text:BF8A383B    push WM_WINDOWPOSCHANGING
    .text:BF8A383D    push esi
    .text:BF8A383E    call _xxxSendMessage@16   ; user-mode callback
    .text:BF8A3843    mov eax, [ebx+4]
    .text:BF8A3846    mov [ebx], edi            ; window handle
    ...
    .text:BF8A3DD7    add ebx, 60h              ; get next entry
    .text:BF8A3DDA    dec [ebp+cItems]          ; decrement cItems
    .text:BF8A3DDD    jns loc_BF8A37CB

不像菜单条目那样，调用 SMWP 数组操纵的漏洞，被通过在 SMWP 数组处理期间拒绝缓冲区的重新分配来应对。这可以在
win32k!DeferWindowPos 函数中观测到，函数在那里检查“正被处理的”标志位并只允许不会导致缓冲区重新分配的项被添加进数组。

#### 4\. 可利用性

在这一节中，我们评估由用户模式回调引发的漏洞的可利用性。由于我们关注两种漏洞原型——释放后使用和空指针引用，我们将聚焦于攻击者是如何能够将这类 BUG
施加在利用 win32k 漏洞上的。为了在第 5 节中提出合理的缓解措施或变通方案，评估它们的可利用性是必不可少的。

##### 4.1 内核堆

如同在第 2.2
节中提到的，用户对象和它们的相关数据结构位于会话内存池、共享堆，或桌面堆中。存储在桌面堆或共享堆中的对象和数据结构由内核堆分配器管理。内核堆分配器可以看作是一个精简版的用户模式堆分配器，它使用类似的由
NT 执行体导出的函数来管理堆块，例如 RtlAllocateHeap 和 RtlFreeHeap 等。

虽然用户堆和内核堆极其相似，但它们有一些关键的不同之处。不像用户模式堆那样，被 win32k 使用的内核堆不采用任何前置分配器。这可以通过查看
HEAP_LIST_LOOKUP 结构体的 ExtendedLookup 值来观察到，该结构体在堆基址（HEAP）中引用。当设置为 NULL
时，堆分配器不使用任何旁视列表或低分片堆 [13]。此外，在转储堆基址结构体（见下面的清单）时，我们可以观察到，由于 EncodingFlagMask 和
PointerKey 都被设置为 NULL，所以并未使用任何堆管理结构体的编码或混淆。前者决定是否使用堆头编码，而后者用来编码 CommitRoutine
指针，每当堆需要被延伸时会调用该例程指针。

    
    
    Kd> dt nt!_HEAP fea00000
       ...
       +0x04c EncodeFlagMask   : 0
       +0x050 Encoding         : _HEAP_ENTRY
       +0x058 PointerKey       : 0
       ...
       +0x0b8 BlocksIndex      : 0xfea00138 Void
       ...
       +0x0c4 FreeLists        : _LIST_ENTRY [ 0xfea07f10 - 0xfea0e4d0 ]
       ...
       +0x0d0 CommitRoutine    : 0x93a4692d  win32k!UserCommitDesktopMemory
       +0x0d4 FrontEndHeap     : (null)
       +0x0d8 FrontHeapLockCount : 0
       +0x0da FrontEndHeapType : 0 ''
    
    Kd> dt nt!_HEAP_LIST_LOOKUP fea00138
       +0x000 ExtendedLookup   : (null)
       ...

当处理像“释放后使用”这样的内核堆损坏问题时，确切知道内核堆管理器如何工作是必不可少的。有很多非常好的文章详细说明了用户模式堆机制的内部工作机制
[13][6][9]，这些可以在学习内核堆时作为参考。根据当前讨论的需要，理解内核堆是一块根据分配内存的数量可伸缩的相邻内存区域就足够了。由于未使用前置管理器，所有被释放的内存块被索引在一个单向的空闲列表中。一般情况下，堆管理器总是尝试分配最近释放的内存块（例如通过列表建议使用），来更好地利用
CPU 缓存器。

##### 4.2 释放后使用利用

为了利用 win32k
中的释放后使用漏洞，攻击者需要能够重新分配已释放的内存并在某种程度上控制它的内容。因为用户对象和相关的数据结构和字符串存储在一起，通过设置存储为
Unicode
字符串的对象属性，有可能可以强制进行任意大小的分配以及完全控制最近释放内存中的内容。只要避免空字符（除了字符串终止符），任意字节组合可以被用在操作作为对象或数据结构访问的内存。

为了桌面堆中的释放后使用漏洞，攻击者会通过调用 SetWindowTextW 设置窗口标题栏的文本，以强制进行任意大小的桌面堆分配。相似地，可以通过调用
SetClassLongPtr 并指定 GCLP_MENUNAME 以设置与某窗口类关联的某个菜单资源的菜单名称字符串来触发任意大小的会话内存池分配。

    
    
    eax=41414141 ebx=00000000 ecx=ffb137e0 edx=8e135f00 esi=fe74aa60 edi=fe964d60
    eip=92d05f53 esp=807d28d4 ebp=807d28f0 iopl=0         nv up ei pl nz na pe cy
    cs=0008  ss=0010  ds=0023  es=0023  fs=0030  gs=0000             efl=00010207
    win32k!xxxSetPKLinThreads+0xa9:
    92d05f53 89700c   mov   dword ptr [eax+0Ch],esi ds:0023:4141414d=????????
    
    kd> dt win32k!tagKL @edi -b
       +0x000 head             : _HEAD
          +0x000 h                : 0x41414141
          +0x004 cLockObj         : 0x41414142
       +0x008 pklNext          : 0x41414141
       +0x00c pklPrev          : 0x41414141
       ...

在上面的清单中（展示在 3.2
节中描述的漏洞，作为键盘布局对象的字符串，CVE-2011-1241），键盘布局对象已被用户控制的字符串所替换，该字符串是在桌面堆中分配的。在这种特殊情况下，键盘布局对象已被释放，但
win32k 尝试将其链入键盘布局列表中。这允许攻击者通过控制被释放的键盘布局对象的 pklNext 指针来选择写入 esi 时的地址。

由于对象通常包含指向其他对象的指针，win32k 使用赋值锁定机制来确保对象依赖性得到满足。照此，在 win32k
尝试释放对象引用时，影响主体中包含赋值锁定指针的对象的释放后使用漏洞会允许攻击者递减任意地址。以下描述的攻击方法的变体可作为这种利用的一种可能的方式：从用户模式回调中返回一个已销毁的菜单句柄索引。在线程销毁时，这导致释放类型为
(0) 的销毁例程被调用。由于该释放类型未定义销毁例程，win32k 将调用零页，而零页在 Windows 中是允许用户映射的（见第 4.3 节）。

    
    
    eax=deadbeeb ebx=fe954990 ecx=ff910000 edx=fea11888 esi=fea11888 edi=deadbeeb
    eip=92cfc55e esp=965a1ca0 ebp=965a1ca0 iopl=0         nv up ei ng nz na pe nc
    cs=0008  ss=0010  ds=0023  es=0023  fs=0030  gs=0000             efl=00010286
    win32k!HMUnlockObject+0x8:
    92cfc55e ff4804          dec     dword ptr [eax+4]    ds:0023:deadbeef=????????
    
    965a1ca0 92cfc9e0 deadbeeb 00000000 fe954978 win32k!HMUnlockObject+0x8
    965a1cb0 92c60cb1 92c60b8b 004cfa54 002dfec4 win32k!HMAssignmentLock+0x45
    965a1cc8 92c60bb3 965a1cfc 965a1cf8 965a1cf4 win32k!xxxCsDdeInitialize+0x67
    965a1d18 8284942a 004cfa54 004cfa64 004cfa5c win32k!NtUserDdeInitialize+0x28
    965a1d18 779864f4 004cfa54 004cfa64 004cfa5c nt!KiFastCallEntry+0x12a

由于攻击者会推测在内核内存中的用户句柄表的地址，他或她会递减窗口对象句柄表项 (1) 的类型（bType）值。在销毁窗口时，这会导致释放类型为 (0)
的销毁例程被调用并引发任意内核代码执行。在上面的清单中（作为 DDE
对象的字符串，CVE-2011-1242），攻击者控制赋值解锁定的指针，导致任意内核递减。

##### 4.3 空指针利用

不像其他类似 Linux
的平台那样，Windows（为保持向后兼容性）允许无特权的用户通过用户进程的上下文映射零页。由于内核和用户模式组件共享同样的虚拟地址空间，攻击者会潜在地能够通过映射零页并控制解引用数据来利用内核空指针解引用漏洞。为了在
Windows 中分配零页，应用程序只需简单地调用 NtAllocateVirtualMemory 并请求一个比 NULL
大但比比页尺寸小的基地址。应用程序也可以通过使用这样的基地址和 MEM_DOS_LIM 功能标志位启用页对齐的区段（仅 x86 有效）调用
NtMapViewOfSection 来内存映射零页。

    
    
    pwnd = (PWND) 0;
    pwnd->head.h = hWnd; // valid window handle
    pwnd->head.pti = NtCurrentTeb()->Win32ThreadInfo;
    pwnd->bServerSideWindowProc = TRUE;
    pwnd->lpfnWndProc = (PVOID) xxxMyProc;

在 win32k
中的空指针漏洞很多时候是由于对用户对象指针的检查不充分导致，因此，攻击者能够通过创建假的零页对象来利用这样的漏洞，并在随后引发任意内存写或控制函数指针的值。例如，由于在
win32k
中最近的很多空指针漏洞都与窗口对象指针有关，攻击者可以在零页安置假的窗口对象并定义一个自定义的服务端窗口过程（见上面的清单，在零页安置假的窗口对象）。如果有任何消息随后被传递给这个
NULL 对象，这会允许攻击者获得任意内核代码执行的能力。

#### 5\. 缓解措施

在这一节中，我们将评估在第 4 节中讨论的这类漏洞的缓解措施。

##### 5.1 释放后使用漏洞

如同在前面的章节中提到的，释放后使用漏洞依靠攻击者重新分配并控制先前释放内存的能力。不幸的是，由于 CPU
没有讲述内存是否属于特定对象或结构体的合法途径，由于只有操作系统生成的抽象，因此缓解释放后使用漏洞是非常苦难的。如果我们看得更仔细一些，这些问题本质上归结于那些攻击者，他们能够在处理回调期间释放对象或缓冲区，并随后在回调返回时
win32k
再次使用对象之前对内存进行重新分配。这样一来，通过还原内核内存池或堆的分配或通过隔离特定的分配以使像字符串这样的简单可控原型不被从相同资源分配，使得缓解释放后使用漏洞的可利用性成为可能。

由于操作系统总是知道回调何时处于激活状态（例如通过
KTHREAD.CallbackDepth），延迟释放的方法可以被用在处理用户模式回调时。这将阻止攻击者立即重新使用已释放的内存。然而，这样的机制无法抵消在这种情况中的利用：在释放后使用条件被触发前调用多个连续的回调。另外，由于用户模式回调机制不在
win32k 中执行，在回调返回时不得不执行附加逻辑来执行必要的延迟释放列表的处理。

与其通过关注分配的可预见性来尝试应对释放后使用利用，我们也可以着眼于利用通常是如何执行的。如同在第 4 节中讨论的，Unicode
字符串和大部分数据可控的分配（例如含 cbWndExtra
定义的窗口对象）对攻击者来说是十分有用的。因此隔离这样的分配可以用来阻止攻击者为简单地重新分配已释放对象的内存而使用可伸缩的原型（例如字符串）。

##### 5.2 空指针漏洞

为了应对 Windows
中的空指针漏洞我们需要进制用户模式应用程序映射或控制零页内容的能力。虽然有很多种方法处理这种问题，例如系统调用挂钩（系统调用挂钩不被微软建议使用，并由于
Kernel Patch Protection 强制进行的完整性检查而不能轻易在 64
位中使用）或页表项（PTE）修改，但是使用虚拟地址描述符（AVD）似乎是一种更加合适的解决方案 [5]。由于 AVD 描述进程内存空间并提供给
Windows 用来正确设置页表项的信息，所以可以用来以一种统一和通用的方式阻止零页映射。然而，由于 32 位版本 Windows 的 NTVDM
子系统依赖于这种能力来正确支持 16 位可执行程序，阻止零页映射也造成向后兼容成本的增加。

#### 6\. 备注

像我们在这篇文章中展示的，用户模式回调似乎导致很多问题并在 win32k 中引入了很多漏洞。这在一定程度上是因为
win32k，或具体地说是窗口管理器，被设计来使用一种全局锁机制（用户临界区段）来允许模块是线程安全的。虽然在个案分析的基础上应对这些漏洞足以作为一种短期的解决方案，但是
win32k
在某些点上需要大的改造，来更好地支持多核架构并在窗口管理方面提供更好的性能。在当前的设计中，同一会话中没有两个线程能够同时处理它们的消息队列，即使他们在两个单独的桌面上单独的应用程序中。理想情况下，win32k
应该遵循 NT 执行体的更加一直的设计，并在每个对象或每个结构的基础上执行互斥。

在缓解 win32k 中的利用以及 Windows
中的通用内核利用方面的重要的一步，是去除掉在用户和内核模式之间的共享内存区段。那些共享内存区段历来被视为对 win32k
不需要使用系统调用方面的优化，因此避免与它们相关的开销。自从这种设计被决定以来，系统调用不再使用更慢的基于中断的方式，因此性能的提升很可能是极小的。虽然在某些情况下，共享区段仍然是首选，但共享的信息应该被保持在最低限度。当前，win32k
子系统为对手提供了大量的内核地址空间信息，并且也在最近的 CSRSS 漏洞利用中开辟了所示的额外攻击向量
[4]。因为子系统中的内存是进程间共享的而无视它们的特权级，攻击者有能力从一个无特权进程中操作高特权进程的地址空间。

#### 7\. 结论

在这篇文章中，我们讨论了有关 win32k
中用户模式回调的很多挑战和问题。尤其是，我们展示了窗口管理器的全局锁设计不能很好地与用户模式回调的概念相结合。虽然涉及围绕用户模式回调的使用的不充分验证的大量漏洞已被应对，那些问题的一些复杂特性表明更多不易察觉的缺陷很可能仍旧存在于
win32k 中。这样一来，为了实现缓解一些更猖獗的这类 BUG，我们总结性地提出一些观点，作为对微软以及终端用户来说，能够做什么来降低将来在 win32k
中可能面临的攻击的风险。

#### 引用

[1] Edgar Barbosa: Windows Vista UIPI.

[http://www.coseinc.com/en/index.php?rt=download&act=publication&file=Vista_UIPI.ppt.pdf](http://www.coseinc.com/en/index.php?rt=download&act=publication&file=Vista_UIPI.ppt.pdf)

[2] Alex Ionescu: Inside Session 0 Isolation and the UI Detection Service.

<http://www.alex-ionescu.com/?p=59>

[3] ivanlef0u: You Failed!

<http://www.ivanlef0u.tuxfamily.org/?p=68>

[4] Matthew 'j00ru' Jurczyk: CVE-2011-1281: A story of a Windows CSRSS
Privilege Escalation vulnerability.

<http://j00ru.vexillium.org/?p=893>

[5] Tarjei Mandt: Locking Down the Windows Kernel: Mitigating Null Pointer
Exploitation.

<http://mista.nu/blog/2011/07/07/mitigating-null-pointer-exploitation-on-windows/>

[6] John McDonald, Chris Valasek: Practical Windows XP/2003 Heap Exploitation.
Black Hat Brieﬁng USA 2009.

<https://www.blackhat.com/presentations/bh-usa-09/MCDONALD/BHUSA09-McDonald-WindowsHeap-PAPER.pdf>

[7] Microsoft Security Bulletin MS11-034. Vulnerabilities in Windows Kernel-Mode Drivers Could Allow Elevation of Privilege.

<http://www.microsoft.com/technet/security/bulletin/ms11-034.mspx>

[8] Microsoft Security Bulletin MS11-054. Vulnerabilities in Windows Kernel-Mode Drivers Could Allow Elevation of Privilege.

<http://www.microsoft.com/technet/security/bulletin/ms11-054.mspx>

[9] Brett Moore: Heaps About Heaps.

<http://www.insomniasec.com/publications/Heaps_About_Heaps.ppt>

[10] MS Windows NT Kernel-mode User and GDI White Paper.

<http://technet.microsoft.com/en-us/library/cc750820.aspx>

[11] mxatone: Analyzing Local Privilege Escalations in Win32k. Uninformed
Journal vol. 10.

[http://uninformed.org/?v=10&a=2](http://uninformed.org/?v=10&a=2)

[12] Chris Paget: Click Next to Continue: Exploits & Information about Shatter
Attacks.

<https://www.blackhat.com/presentations/bh-usa-03/bh-us-03-paget.pdf>

[13] Chris Valasek: Understanding the Low Fragmentation Heap. Black Hat
Brieﬁngs USA 2010.

<http://illmatics.com/Understanding_the_LFH.pdf>

原文链接

<http://media.blackhat.com/bh-us-11/Mandt/BH_US_11_Mandt_win32k_WP.pdf>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/575/>

