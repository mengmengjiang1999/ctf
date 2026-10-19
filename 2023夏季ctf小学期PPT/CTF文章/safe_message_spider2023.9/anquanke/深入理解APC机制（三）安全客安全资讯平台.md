# 深入理解APC机制（三）

阅读量 **222979**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-26 15:30:52

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0178b919fb5c17d3b6.jpg)

## 0x01深入内核

​
我们直接从ReactOS中了解其中的具体实现，比如[NtQueueApcThreadEx](https://doxygen.reactos.org/da/d3c/ntoskrnl_2ps_2state_8c_source.html#l00504)，其中主要使用了一个KAPC对象：

    
    
     typedef struct _KAPC {
       UCHAR Type;
       UCHAR SpareByte0;
       UCHAR Size;
       UCHAR SpareByte1;
       ULONG SpareLong0;
       struct _KTHREAD *Thread;
       LIST_ENTRY ApcListEntry;
     #ifdef _NTSYSTEM_
       PKKERNEL_ROUTINE KernelRoutine;
       PKRUNDOWN_ROUTINE RundownRoutine;
       PKNORMAL_ROUTINE NormalRoutine;
     #else
       PVOID Reserved[3];
     #endif
       PVOID NormalContext;
       PVOID SystemArgument1;
       PVOID SystemArgument2;
       CCHAR ApcStateIndex;
       KPROCESSOR_MODE ApcMode;
       BOOLEAN Inserted;
     } KAPC, *PKAPC, *RESTRICTED_POINTER PRKAPC;
    

​ 从内核模式对用户 APC 进行排队非常简单。每个 APC 对象都由一个 KAPC 对象表示。KAPC 对象主要有 3 个重要功能：

  * **NormalRoutine** ：这是在交付 APC 时应在用户模式下执行的函数。（ApcRoutine）
  * **KernelRoutine** : 这是一个在 APC 被交付之前在内核模式下的 APC_LEVEL 中执行的函数。
  * **RundownRoutine** ：这是一个函数，如果线程在 APC 被传递到用户模式之前终止，它应该释放 APC 对象。

对于用户态 APC，我们需要在 KeInitializeApc 的 ApcMode 参数中指定“UserMode”，其中 SystemArgument1
被传递给 KeInitializeApc，而 SystemArgument2 和 SystemArgument3 被传递给
KeInsertQueueApc。

KeInsertQueueApc 将 APC
插入到目标线程的队列中，如果线程处于alertable等待状态，它还可以“取消等待状态”线程并确保当它返回到用户模式时 APC
将执行。这两个函数（KiInitializeApc 和 KeInsertQueueApc）都由 NTOSKRNL
导出，例如，NSA开发的DoublePulsar内核模式payload使用KeInsertQueueApc在用户模式下执行payload：

![](https://p0.ssl.qhimg.com/t01dcbb9bce53f460d9.png)

​ 那我们就来看看KeInsertQueueApc 实现：

    
    
     BOOLEAN
     NTAPI
     KeInsertQueueApc(IN PKAPC Apc,
                      IN PVOID SystemArgument1,
                      IN PVOID SystemArgument2,
                      IN KPRIORITY PriorityBoost)
     {
         PKTHREAD Thread = Apc->Thread;
         KLOCK_QUEUE_HANDLE ApcLock;
         BOOLEAN State = TRUE;
         ASSERT_APC(Apc);
         ASSERT_IRQL_LESS_OR_EQUAL(DISPATCH_LEVEL);
    
         /* Get the APC lock */
         KiAcquireApcLockRaiseToSynch(Thread, &ApcLock);
    
         /* Make sure we can Queue APCs and that this one isn't already inserted */
         if (!(Thread->ApcQueueable) || (Apc->Inserted))
         {
             /* Fail */
             State = FALSE;
         }
         else
         {
             /* Set the System Arguments and set it as inserted */
             Apc->SystemArgument1 = SystemArgument1;
             Apc->SystemArgument2 = SystemArgument2;
             Apc->Inserted = TRUE;
    
             /* Call the Internal Function */
             KiInsertQueueApc(Apc, PriorityBoost);
         }
    
         /* Release the APC lock and return success */
         KiReleaseApcLockFromSynchLevel(&ApcLock);
         KiExitDispatcher(ApcLock.OldIrql);
         return State;
     }
    

先获取锁，将 APC 插入 APC 队列。APC队列实际上是一个链表，保存在KTHREAD对象的ApcState成员中。

## 0x02 KiSignalThreadForApc

​ KeInsertQueueApc 将 APC 插入目标队列后，KiSignalThreadForApc 运行。该函数的目的是根据 APC
的类型检查是否应该向目标线程发出信号以及如何发出信号。主要检查以下三个点：

  1. 线程正在等待。
  2. 线程是否挂起——当一个线程被挂起时，它处于waiting状态——内核不让挂起的线程等待执行 APC。
  3. 线程是alertable——当线程使用 Alertable = TRUE 调用 KeWaitForSingleObject 时，“Alertable”成员变为 TRUE。

## 0x03 KiDeliverApc

​ KiDeliverApc 处理所有类型的 APC：

  1. 获取 APC 队列锁。
  2. 检查 APC 队列是否为空。如果不是，则从队列中弹出第一个用户 APC
  3. 调用内核例程。KernelRoutine 是在 APC 传递到用户模式之前运行在 APC_LEVEL 的代码。最常见的是，此代码释放 APC (ExFreePool)。APC 的值保存在局部变量中，KernelRoutine 可以根据需要更改这些值。
  4. 初始化 TRAP_FRAME 以返回 APC 代码而不是现有代码。

这里我使用起进程注入dll的方式，实际演示：

    
    
    RemoteLibAddress = WriteLibraryNameToRemote(ProcessInformation.hProcess, L"calc.dll");
    Status = NtQueueApcThread(
    ProcessInformation.hThread,
    (PPS_APC_ROUTINE)LdrLoadDll,
    NULL, // PathToFile
    0,  // Flags
    RemoteLibAddress // ModuleFileName
    );
    

![](https://p2.ssl.qhimg.com/t0142fd075e83e43591.png)

![](https://p5.ssl.qhimg.com/t01e22f3155f1bd7209.png)

## 0x04 总结

​ 用户 APC 用于在 Windows 中实现异步回调，用户 APC 使用 KeInsertQueueApc 在内核模式下排队，用户 APC
被保存为每个线程队列中的 KAPC 对象，用户 APC 最常在线程返回用户模式且 UserApcPending = TRUE 之前执行，当使用
Alertable = TRUE 调用 KeWaitForSingleObject 或调用 NtTestAlert 时，UserApcPending 为
TRUE。所以利用此方式在实战攻防中绕过杀软还是可行的。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **anw2** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254026](/post/id/254026)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Windows](/tag/Windows)
  * [APC](/tag/APC)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhimg.com/t010857340ce46bb672.jpg) anw2

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

