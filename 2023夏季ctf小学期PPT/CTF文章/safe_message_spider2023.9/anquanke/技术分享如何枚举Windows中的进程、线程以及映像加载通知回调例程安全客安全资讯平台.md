# 【技术分享】如何枚举Windows中的进程、线程以及映像加载通知回调例程

阅读量 **214554**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-09-22 16:41:07

 **x**

##### 译文声明

本文是翻译文章，文章来源：triplefault.io

原文地址：<http://www.triplefault.io/2017/09/enumerating-process-thread-and-image.html>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**一、前言**

****

大多数人都知道，Windows包含内核模式下的各种回调例程，驱动开发者可以使用这些例程接收各种事件通知。本文将介绍其中某些函数的工作机制。具体说来，我们会研究进程创建及终止回调例程（[nt!PsSetCreateProcessNotifyRoutine](https://msdn.microsoft.com/en-us/library/windows/hardware/ff559951\(v=vs.85\).aspx)、
[nt!PsSetCreateProcessNotifyRoutineEx](https://msdn.microsoft.com/en-us/library/windows/hardware/ff559953\(v=vs.85\).aspx)和[nt!PsSetCreateProcessNotifyRoutineEx2](https://msdn.microsoft.com/en-us/library/windows/hardware/mt805891\(v=vs.85\).aspx)）、线程创建及终止回调例程（[nt!PsSetCreateThreadNotifyRoutine](https://msdn.microsoft.com/en-us/library/windows/hardware/ff559954\(v=vs.85\).aspx)和[nt!PsSetCreateThreadNotifyRoutineEx](https://msdn.microsoft.com/en-us/library/windows/hardware/dn957857\(v=vs.85\).aspx)）以及映像加载通知回调例程（[nt!PsSetLoadImageNotifyRoutine](https://msdn.microsoft.com/en-us/library/windows/hardware/ff559957\(v=vs.85\).aspx)）的内部工作原理。此外，我们也会提供一个便于操作的WinDbg脚本，你可以利用这个脚本枚举这几种回调例程。

如果你想跟随本文的脚步，我建议你跟我一样使用Windows x64
10.0.15063（创造者更新版）中的系统文件。本文所使用的伪代码以及反汇编代码都是在这个发行版的基础上编写的。

如果你还没有搭建内核调试环境，不要担忧，我们给出了一个[教程](http://www.triplefault.io/2017/07/setting-up-kernel-debugging-using.html)，一步一步教你如何使用WindDbg以及VMware搭建基本的内核调试环境。

  

**二、回调例程的作用**

****

在某些事件发生时，驱动开发者可以使用这些回调例程来接收事件的通知。比如，[nt!PsSetCreateProcessNotifyRoutine](https://msdn.microsoft.com/en-us/library/windows/hardware/ff559951\(v=vs.85\).aspx)这个基本的进程创建回调会注册一个用户定义的函数指针（“
**NotifyRoutine**
”），每当进程创建或者删除时，Windows都会调用这个函数指针。作为事件通知的一部分，用户提供的这个处理函数可以获得大量信息。在我们的演示案例中，这些信息包括父进程的PID（如果父进程存在的话）、实际进程的PID以及一个布尔值，标识进程处于创建还是终止状态。

安全软件可以利用这些回调来仔细检查主机上运行的代码。

  

**三、深入分析**

****

**3.1 已公开的API**

万事开头难，我们先得找个出发点。没有什么比官方文档中的函数更适合上手，我们选择的是[nt!PsSetCreateProcessNotifyRoutine](https://msdn.microsoft.com/en-us/library/windows/hardware/ff559951\(v=vs.85\).aspx)这个函数。MSDN称这个例程自Windows
2000起就一直存在。[ReactOS](https://www.reactos.org/)似乎很早以前就已经[实现](https://doxygen.reactos.org/dd/dbe/psnotify_8c.html#a3253d05870ac48d9fa4c0886343d12cb)了这个例程。接下来，我们会具体分析从Windows
2000到现在的这17年中，这个函数发生过什么变化（如果这么多年这些函数的确发生过变化的话）。

    
    
    NTSTATUS __stdcall PsSetCreateProcessNotifyRoutine(PVOID NotifyRoutine, BOOLEAN Remove)
    {
      return PspSetCreateProcessNotifyRoutine(NotifyRoutine, Remove != 0);
    }

这个函数似乎会调用一个nt!PspSetCreateProcessNotifyRoutine例程。实际上，其他类似的函数（[nt!PsSetCreateProcessNotifyRoutineEx](https://msdn.microsoft.com/en-us/library/windows/hardware/ff559953\(v=vs.85\).aspx)及[nt!PsSetCreateProcessNotifyRoutineEx2](https://msdn.microsoft.com/en-us/library/windows/hardware/mt805891\(v=vs.85\).aspx)）也会调用这个例程：

唯一的区别在于传递给nt!PspSetCreateProcessNotifyRoutine的第二个参数。这些参数属于有效的标识符。在基础函数（
**nt!PsSetCreateProcessNotifyRoutine**
）中，根据“Remove”参数的状态，这些标识的值为1或者0。如果“Remove”为TRUE，那么Flags=1。如果“Remove”为FALSE，那么Flags=0。在扩展函数（
**nt!PsSetCreateProcessNotifyRoutineEx** ）中，这些标识的值为2或者3。

    
    
    NTSTATUS __fastcall PsSetCreateProcessNotifyRoutineEx(PVOID NotifyRoutine, BOOLEAN Remove)
    {
      return PspSetCreateProcessNotifyRoutine(NotifyRoutine, (Remove != 0) + 2);
    }

对于 **nt!PsSetCreateProcessNotifyRoutineEx2** 而言，这些标识的值为6或者7：

    
    
    NTSTATUS __fastcall PsSetCreateProcessNotifyRoutineEx2(int NotifyType, PVOID NotifyInformation, BOOLEAN Remove)
    {
      NTSTATUS result; // eax
    
      if ( NotifyType )                             // Only PsCreateProcessNotifySubsystems is supported.
        result = STATUS_INVALID_PARAMETER;
      else
        result = PspSetCreateProcessNotifyRoutine(NotifyInformation, (Remove != 0) + 6);
      return result;
    }

因此，我们可以推测出传递给nt!PspSetCreateProcessNotifyRoutine函数的标识符具体定义如下：

    
    
    #define FLAG_REMOVE_FROM_ARRAY 0x1
    
    // This is why flags from PsSetCreateProcessNotifyRoutineEx can have a value of 2 or 3
    // FLAG_IS_EXTENDED = 0x2
    // FLAG_IS_EXTENDED | FLAG_REMOVE_FROM_ARRAY = 0x3
    #define FLAG_IS_EXTENDED 0x2
    
    // This is why flags from nt!PsSetCreateProcessNotifyRoutineEx2 can have a value of 6 or 7
    // FLAG_IS_EXTENDED2 = 0x6
    // FLAG_IS_EXTENDED2 | FLAG_REMOVE_FROM_ARRAY = 0x7
    #define FLAG_IS_EXTENDED2 (0x4 | FLAG_IS_EXTENDED)

**3.2 未公开文档**

**nt!PspSetCreateProcessNotifyRoutine**
稍微有点复杂，该函数的具体定义如下，我建议你还是在另一个[窗口](https://gist.github.com/nmulasmajic/a14b2d51596a4c6fb261fc8f8e83b279)中好好阅读这段代码，便于理解。

    
    
    NTSTATUS __fastcall PspSetCreateProcessNotifyRoutine(PVOID NotifyRoutine, DWORD Flags)
    {
      BOOL bIsRemove;
      BOOL bIsExRoutine;
      DWORD UpperFlagBits;
      DWORD LdrDataTableEntryFlags;
      _EX_CALLBACK_ROUTINE_BLOCK *NewCallBackBlock;
      _ETHREAD *CurrentThread;
      size_t Index;
      _EX_CALLBACK_ROUTINE_BLOCK *CallBackBlock;
    
      // Copy over everything to UpperFlagBits from Flags, but bit 0.
      UpperFlagBits = ((DWORD)Flags & 0xFFFFFFFE);
      
      // Check if bit 1 is set. This will only be true if the caller is PsSetCreateProcessNotifyRoutineEx
      // or PsSetCreateProcessNotifyRoutineEx2.
      bIsExRoutine = (Flags & 2);
      
      // Bit 0 will be set if "Remove" == TRUE from the caller.
      bIsRemove = (Flags & 1);
      
      // Bit 0 is set. We want to remove a callback.
      if (bIsRemove)
      {
        // Disable APCs.
        CurrentThread = (_ETHREAD *)KeGetCurrentThread();
        --CurrentThread->Tcb.KernelApcDisable;
      
        Index = 0;
        while ( 1 )
        {
          CallBackBlock = ExReferenceCallBackBlock(&PspCreateProcessNotifyRoutine[Index]);
          
          if ( CallBackBlock )
          {
            if ( /* Is it the same routine? */ 
                 ExGetCallBackBlockRoutine(CallBackBlock) == NotifyRoutine
                 /* Is it the same type? e.g. PsSetCreateProcessNotifyRoutineEx vs PsSetCreateProcessNotifyRoutineEx2 vs PsSetCreateProcessNotifyRoutine. */
                 && (_DWORD)ExGetCallBackBlockContext(CallBackBlock) == (_DWORD)UpperFlagBits
                 /* Did we successfully NULL it out? */
                 && ExCompareExchangeCallBack(&PspCreateProcessNotifyRoutine[Index], NULL, CallBackBlock) )
            {
              // Decrement global count.
              if ( bIsExRoutine )
                _InterlockedDecrement(&PspCreateProcessNotifyRoutineExCount);
              else
                _InterlockedDecrement(&PspCreateProcessNotifyRoutineCount);
    
              ExDereferenceCallBackBlock(&PspCreateProcessNotifyRoutine[Index], CallBackBlock);
              KiLeaveCriticalRegionUnsafe(CurrentThread);
              ExWaitForCallBacks(CallBackBlock);
              ExFreePoolWithTag(CallBackBlock, 0);
              return STATUS_SUCCESS;
            }
            ExDereferenceCallBackBlock(&PspCreateProcessNotifyRoutine[Index], CallBackBlock);
          }
       
          Index++;
        
          // Maximum callbacks == 64
          if ( Index >= 0x40 )
          {
            KiLeaveCriticalRegionUnsafe(CurrentThread);
            return STATUS_PROCEDURE_NOT_FOUND; // Could not find entry to remove.
          }
        }
      }
      else // We want to add a callback.
      {
        if ( bIsExRoutine )
          LdrDataTableEntryFlags = 0x20; // "Ex" routine must have _KLDR_DATA_TABLE_ENTRY.IntegrityCheck bit set.
        else
          LdrDataTableEntryFlags = 0;
      
        if ( !MmVerifyCallbackFunctionCheckFlags(NotifyRoutine, LdrDataTableEntryFlags) )
          return STATUS_ACCESS_DENIED;
        
          // Allocate new data structure.
        NewCallBackBlock = ExAllocateCallBack(NotifyRoutine, UpperFlagBits);
        if ( !NewCallBackBlock )
          return STATUS_INSUFFICIENT_RESOURCES;
      
        Index = 0;
        while ( !ExCompareExchangeCallBack(&PspCreateProcessNotifyRoutine[Index], NewCallBackBlock, NULL) )
        {
          Index++;
        
          if ( Index >= 0x40 )
          {
            // No space for callbacks.
            ExFreePoolWithTag(NewCallBackBlock, 0);
            return STATUS_INVALID_PARAMETER;
          }
        }
        
        // Increment global counters.
        if ( bIsExRoutine )
        {
          _InterlockedIncrement(&PspCreateProcessNotifyRoutineExCount);
          if ( !(PspNotifyEnableMask & 4) )
            _interlockedbittestandset(&PspNotifyEnableMask, 2u); // Have "Ex" callbacks.
        }
        else
        {
          _InterlockedIncrement(&PspCreateProcessNotifyRoutineCount);
          if ( !(PspNotifyEnableMask & 2) )
            _interlockedbittestandset(&PspNotifyEnableMask, 1u); // Have base-type of callbacks.
        }
        
        return STATUS_SUCCESS;
      }
    }

幸运的是，从Windows
2000起，与回调例程有关的许多内部数据结构并没有发生改动。[ReactOS](https://www.reactos.org/)的前辈们已经给出过这些结构的定义，因此在可能的情况下，我们会使用这些结构定义，以避免重复劳动。

每个回调都对应一个全局数组，该数组最多可以包含64个元素。在我们的案例中，用于进程创建回调的数组的起始元素为
**nt!PspCreateProcessNotifyRoutine** 。数组中的每个元素均为EXCALLBACK类型。

    
    
    // Source: https://doxygen.reactos.org/de/d22/ndk_2extypes_8h_source.html#l00545
    
    //
    // Internal Callback Handle
    //
    typedef struct _EX_CALLBACK
    {
        EX_FAST_REF RoutineBlock;
    } EX_CALLBACK, *PEX_CALLBACK;

为了避免同步问题，系统使用了nt!ExReferenceCallBackBlock来安全获取底层回调对象的引用（EXCALLBACKROUTINEBLOCK，如下所示）。我们以非线程安全形式的代码重现这一过程：

    
    
    /*
        nt!_EX_CALLBACK
           +0x000 RoutineBlock     : _EX_FAST_REF
    */
    _EX_CALLBACK* CallBack = &PspCreateProcessNotifyRoutine[Index];
    
    /*
        kd> dt nt!_EX_FAST_REF
           +0x000 Object           : Ptr64 Void
           +0x000 RefCnt           : Pos 0, 4 Bits
           +0x000 Value            : Uint8B
    */
    _EX_FAST_REF ReferenceObject = CallBack->RoutineBlock;
    
    // We need to find the location of the actual "Object" from the
    // _EX_FAST_REF structure. This is a union, where the lower 4 bits
    // are the "RefCnt". So, this means we're interested in the remaining
    // 60 bits.
    
    // Strip off the "RefCnt" bits.
    _EX_CALLBACK_ROUTINE_BLOCK* CallBackBlock = (_EX_CALLBACK_ROUTINE_BLOCK*)(ReferenceObject.Value & 0xFFFFFFFFFFFFFFF0);
    
    
    // Source: https://doxygen.reactos.org/db/d49/xdk_2extypes_8h_source.html#l00179
    
    typedef struct _EX_RUNDOWN_REF {
      _ANONYMOUS_UNION union {
        volatile ULONG_PTR Count;
        volatile PVOID Ptr;
      } DUMMYUNIONNAME;
    } EX_RUNDOWN_REF, *PEX_RUNDOWN_REF;
    
    // Source: https://doxygen.reactos.org/de/d22/ndk_2extypes_8h_source.html#l00535
    
    //
    // Internal Callback Object
    //
    typedef struct _EX_CALLBACK_ROUTINE_BLOCK
    {
        EX_RUNDOWN_REF RundownProtect;
        PEX_CALLBACK_FUNCTION Function;
        PVOID Context;
    } EX_CALLBACK_ROUTINE_BLOCK, *PEX_CALLBACK_ROUTINE_BLOCK;

如果我们想要删除某个回调对象（“Remove”为TRUE），我们要确保在数组中找到正确的EXCALLBACKROUTINEBLOCK。具体的方法是，首先使用nt!ExGetCallBackBlockRoutine来检查目标“NotifyRoutine”是否与当前的EXCALLBACK_ROUTINE相匹配：

    
    
    PVOID __fastcall ExGetCallBackBlockRoutine(_EX_CALLBACK_ROUTINE_BLOCK *CallBackBlock)
    {
      return CallBackBlock->Function;
    }

随后，使用 **nt!ExGetCallBackBlockContext**
检查目标类型是否正确（即是否使用正确的nt!PsSetCreateProcessNotifyRoutine/Ex/Ex2创建而得）：

    
    
    PVOID __fastcall ExGetCallBackBlockContext(_EX_CALLBACK_ROUTINE_BLOCK *CallBackBlock)
    {
      return CallBackBlock->Context;
    }

此时，我们已经找到了数组中的那个元素。我们需要通过 **nt!ExCompareExchangeCallback**
将EXCALLBACK的值设置为NULL，减少其对应的全局计数值（为nt!PspCreateProcessNotifyRoutineExCount或者nt!PspCreateProcessNotifyRoutineCount），通过nt!ExDereferenceCallBackBlock解除EXCALLBACKROUTINEBLOCK的引用，等待使用EXCALLBACK的其他代码（nt!ExWaitForCallBacks），最后释放内存（nt!ExFreePoolWithTag）。从这个过程中，我们可知微软为了避免释放在用的回调对象做了许多工作。

如果遍历所有64个元素后，我们依然无法在nt!PspCreateProcessNotifyRoutine数组中找到需要删除的元素，那么系统就会返回STATUSPROCEDURENOT_FOUND错误信息。

另一方面，如果我们想要往回调数组中添加新的元素，过程会稍微简单点。nt!MmVerifyCallbackFunctionCheckFlags函数会执行完整性检查，以确保已加载模块中存在“NotifyRoutine”。这样一来，未链接的驱动（或shellcode）就无法收到回调事件。

    
    
    BOOL __fastcall MmVerifyCallbackFunctionCheckFlags(PVOID NotifyRoutine, DWORD Flags)
    {
      struct _KTHREAD *CurrentThread; // rbp
      BOOL bHasValidFlags; // ebx
      _KLDR_DATA_TABLE_ENTRY *Entry; // rax
    
      if ( MiGetSystemRegionType(NotifyRoutine) == 1 )
        return 0;
      CurrentThread = KeGetCurrentThread();
      bHasValidFlags = 0;
      --CurrentThread->KernelApcDisable;
      ExAcquireResourceSharedLite(&PsLoadedModuleResource, 1u);
      Entry = MiLookupDataTableEntry(NotifyRoutine, 1u);
      if ( Entry && (!Flags || Entry->Flags & Flags) )
        bHasValidFlags = 1;
      ExReleaseResourceLite(&PsLoadedModuleResource);
      KeLeaveCriticalRegionThread(CurrentThread);
      return bHasValidFlags;
    }

通过完整性检查后，系统会使用nt!ExAllocateCallBack来分配一个EXCALLBACKROUTINEBLOCK。这个函数可以用来确认EXCALLBACKROUTINEBLOCK结构的大小及布局：

    
    
    _EX_CALLBACK_ROUTINE_BLOCK *__fastcall ExAllocateCallBack(PEX_CALLBACK_FUNCTION Function, PVOID Context)
    {
      _EX_CALLBACK_ROUTINE_BLOCK *CallbackBlock;
    
      CallbackBlock = (_EX_CALLBACK_ROUTINE_BLOCK *)ExAllocatePoolWithTag(
                                                      NonPagedPoolNx,
                                                      sizeof(_EX_CALLBACK_ROUTINE_BLOCK),
                                                      'brbC');
      if ( CallbackBlock )
      {
        CallbackBlock->Function = Function;
        CallbackBlock->Context = Context;
        ExInitializePushLock(&CallbackBlock->RundownProtect);
      }
      
      return CallbackBlock;
    }

随后，系统会使用 **nt!ExCompareExchangeCallBack** 将新分配的EXCALLBACKROUTINEBLOCK添加到
**nt!PspCreateProcessNotifyRoutine**
数组中的空闲（NULL）位置（需要确保数组没有超过64个元素大小限制）。最后，对应的全局计数值会增加计数，
**nt!PspNotifyEnableMask** 中也会设置一个全局标识，表明系统中注册了用户指定类型的回调函数。

**3.3 其他回调**

幸运的是，线程以及映像创建回调与进程回调非常类似，它们使用了相同的底层数据结构。唯一的区别在于，线程创建/终止回调存储在nt!PspCreateThreadNotifyRoutine数组中，而映像加载通知回调存储在
**nt!PspLoadImageNotifyRoutine** 中。

  

**四、实用脚本**

****

现在我们可以将这些信息综合利用起来。我们可以使用WinDbg创建一个简单便捷的脚本来自动枚举进程、线程以及镜像回调例程。

我选择使用其他方法，而不去使用WinDbg自带的脚本引擎来完成这个任务。WinDbg中有个非常棒的第三方扩展PyKd，可以在WinDbg中运行Python脚本。安装这个扩展的过程非常简单，你只需要使用正确版本的Python即可（如64位的WinDbg需要安装64位版）。

    
    
    ''' Module Name: enumwincallbacks.py
    Abstract:
        Iterates over the nt!PspCreateProcessNotifyRoutine,
        nt!PspCreateThreadNotifyRoutine, and nt!PspLoadImageNotifyRoutine 
        callback arrays.
    Requirements:
        WinDbg: https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/
        PyKd: https://pykd.codeplex.com/
    Author:
        Nemanja (Nemi) Mulasmajic <nm@triplefault.io>
            http://triplefault.io
    ''' from pykd import * import argparse
    Discovers the size of a pointer for this system.
    SIZEOFPOINTER = (8 if (is64bitSystem()) else 4)
    The number of potential callback objects in the array.
    MAXIMUMNUMBEROF_CALLBACKS = 0
    def readptr(memory): ''' Read a pointer of memory. ''' try: return (ptrPtr(memory)) except: print "ERROR: Could not read {} bytes from location {:#x}.".format(SIZEOF_POINTER, memory) exit(-4)
    def read_dword(memory): ''' Read a DWORD of memory. ''' try: return (ptrDWord(memory)) except: print "ERROR: Could not read 4 bytes from location {:#x}.".format(memory) exit(-5)
    def getaddressfromfastref(EXFASTREF): ''' Given a EXFAST_REF structure, this function will extract the pointer to the raw object. '''
    # kd> dt nt!_EX_FAST_REF
    #   +0x000 Object           : Ptr64 Void
    #   +0x000 RefCnt           : Pos 0, 4 Bits
    #   +0x000 Value            : Uint8B
    # Remove the last 4 bits of the pointer.
    return ((_EX_FAST_REF >> 4) << 4)
    def enumerateovercallbacks(array): ''' Given the base of a callback array, this function will enumerate over all valid callback entries. ''' for i in xrange(MAXIMUMNUMBEROFCALLBACKS): # Get the i'th entry in the array. entry = (array + (i * SIZEOFPOINTER)) entry = readptr(entry)
        # Not currently in use; skipping.
        if entry == 0:
            continue
        # Extract just the object pointer from the _EX_FAST_REF structure.
        callback_object = get_address_from_fastref(entry)
        print "{}: _EX_CALLBACK_ROUTINE_BLOCK {:#x}".format(i, callback_object)
        # _EX_CALLBACK_ROUTINE_BLOCK
        #   +0x000 RundownProtect   : EX_RUNDOWN_REF
        #   +0x008 Function         : PVOID
        #   +0x010 Context          : PVOID
        rundown_protect = read_ptr(callback_object + (SIZE_OF_POINTER * 0))
        callback_function = read_ptr(callback_object + (SIZE_OF_POINTER * 1))
        context = read_ptr(callback_object + (SIZE_OF_POINTER * 2))
        print "tRundownProtect: {:#x}".format(rundown_protect)
        print "tFunction: {:#x} ({})".format(callback_function, findSymbol(callback_function))
        type = ""
        if context == 0:
            type = "(Normal)"
        elif context == 2:
            type = "(Extended)"
        elif context == 6:
            type = "(Extended #2)"
        else:
            type = "(Unknown)"
        print "tContext: {:#x} {}".format(context, type)
    def getaddressfrom_symbol(mod, name): ''' Attempts to locate the address of a given symbol in a module. ''' try: return (mod.offset(name)) except: print "ERROR: Failed to retrieve the address of {}!{}. Are symbols loaded?".format(m.name(), name) exit(-3)
    parser = argparse.ArgumentParser(description='Iterates over the nt!PspCreateProcessNotifyRoutine, nt!PspCreateThreadNotifyRoutine, and nt!PspLoadImageNotifyRoutine callback arrays.')
    parser.addargument("-p", action="storefalse", default=True, dest="processcallbacks", help="Exludes iteration of the process callback array (nt!PspCreateProcessNotifyRoutine).") parser.addargument("-t", action="storefalse", default=True, dest="threadcallbacks", help="Excludes iteration of the thread callback array (nt!PspCreateThreadNotifyRoutine).") parser.addargument("-i", action="storefalse", default=True, dest="image_callbacks", help="Excludes iteration of the image load callback array (nt!PspLoadImageNotifyRoutine).")
    args = parser.parse_args()
    Must be kernel debugging to use this.
    if not isKernelDebugging() and not isLocalKernelDebuggerEnabled(): print "ERROR: This script can only be used while kernel debugging." exit(-1)
    try: mod = module("nt") except: print "ERROR: Could not find the base address of ntoskrnl. Are symbols loaded?" exit(-2)
    spacer = "=" * 100
    ver = getSystemVersion()
    Vista+ can store 64 entries in the callback array.
    Older versions of Windows can only store 8.
    MAXIMUMNUMBEROF_CALLBACKS = (64 if (ver.buildNumber >= 6000) else 8)
    For process callbacks.
    if args.processcallbacks: PspCreateProcessNotifyRoutine = getaddressfromsymbol(mod, "PspCreateProcessNotifyRoutine") PspCreateProcessNotifyRoutineCount = readdword(getaddressfromsymbol(mod, "PspCreateProcessNotifyRoutineCount"))
    if ver.buildNumber >= 6001: # Vista SP1+ 
        PspCreateProcessNotifyRoutineExCount = read_dword(get_address_from_symbol(mod, "PspCreateProcessNotifyRoutineExCount"))
    else:
        PspCreateProcessNotifyRoutineExCount = 0
    print "nIterating over the nt!PspCreateProcessNotifyRoutine array at {:#x}.".format(PspCreateProcessNotifyRoutine)
    print "Expecting {} nt!PspCreateProcessNotifyRoutineCount and {} nt!PspCreateProcessNotifyRoutineExCount entries.".format(PspCreateProcessNotifyRoutineCount, PspCreateProcessNotifyRoutineExCount)
    print spacer
    enumerate_over_callbacks(PspCreateProcessNotifyRoutine)
    print spacer
    For thread callbacks.
    if args.threadcallbacks: PspCreateThreadNotifyRoutine = getaddressfromsymbol(mod, "PspCreateThreadNotifyRoutine") PspCreateThreadNotifyRoutineCount = readdword(getaddressfromsymbol(mod, "PspCreateThreadNotifyRoutineCount"))
    if ver.buildNumber >= 10240: # Windows 10+
        PspCreateThreadNotifyRoutineNonSystemCount = read_dword(get_address_from_symbol(mod, "PspCreateThreadNotifyRoutineNonSystemCount"))
    else:
        PspCreateThreadNotifyRoutineNonSystemCount = 0
    print "nIterating over the nt!PspCreateThreadNotifyRoutine array at {:#x}.".format(PspCreateThreadNotifyRoutine)
    print "Expecting {} nt!PspCreateThreadNotifyRoutineCount and {} nt!PspCreateThreadNotifyRoutineNonSystemCount entries.".format(PspCreateThreadNotifyRoutineCount, PspCreateThreadNotifyRoutineNonSystemCount)
    print spacer
    enumerate_over_callbacks(PspCreateThreadNotifyRoutine)
    print spacer
    For image callbacks.
    if args.imagecallbacks: PspLoadImageNotifyRoutine = getaddressfromsymbol(mod, "PspLoadImageNotifyRoutine") PspLoadImageNotifyRoutineCount = readdword(getaddressfromsymbol(mod, "PspLoadImageNotifyRoutineCount"))
    print "nIterating over the nt!PspLoadImageNotifyRoutine array at {:#x}.".format(PspLoadImageNotifyRoutine)
    print "Expecting {} nt!PspLoadImageNotifyRoutineCount entries.".format(PspLoadImageNotifyRoutineCount)
    print spacer
    enumerate_over_callbacks(PspLoadImageNotifyRoutine)
    print spacer

这个脚本读起来应该没什么困难，我已经尽量在代码中给出了足够多的注释。这段代码的兼容性也不错，可以兼容从XP以来的所有Windows系统（32位及64位都兼容）。

在WinDbg中使用“!py”命令运行这段脚本后，输出结果如下所示：

    
    
    kd> !py "C:UsersrootDesktopWinDbgScriptsenumwin_callbacks.py"
    Iterating over the nt!PspCreateProcessNotifyRoutine array at 0xfffff8036e6042d0.
    Expecting 6 nt!PspCreateProcessNotifyRoutineCount and 4 nt!PspCreateProcessNotifyRoutineExCount entries.
    0: EXCALLBACKROUTINEBLOCK 0xffffc98b8c84b660 RundownProtect: 0x20 Function: 0xfffff8036e3979f0 (nt!ViCreateProcessCallback) Context: 0x0 (Normal) 1: EXCALLBACKROUTINEBLOCK 0xffffc98b8c8f1410 RundownProtect: 0x20 Function: 0xfffff8099e9358a0 (cng!CngCreateProcessNotifyRoutine) Context: 0x0 (Normal) 2: EXCALLBACKROUTINEBLOCK 0xffffc98b8dd607a0 RundownProtect: 0x20 Function: 0xfffff8099f33bcf0 (WdFilter!MpCreateProcessNotifyRoutineEx) Context: 0x6 (Extended #2) 3: EXCALLBACKROUTINEBLOCK 0xffffc98b8dd6db60 RundownProtect: 0x20 Function: 0xfffff8099de7a0c0 (ksecdd!KsecCreateProcessNotifyRoutine) Context: 0x0 (Normal) 4: EXCALLBACKROUTINEBLOCK 0xffffc98b8d7c9670 RundownProtect: 0x20 Function: 0xfffff8099ee88080 (tcpip!CreateProcessNotifyRoutineEx) Context: 0x6 (Extended #2) 5: EXCALLBACKROUTINEBLOCK 0xffffc98b8e05b070 RundownProtect: 0x20 Function: 0xfffff8099f2ec860 (iorate!IoRateProcessCreateNotify) Context: 0x2 (Extended) 6: EXCALLBACKROUTINEBLOCK 0xffffc98b8e0736a0 RundownProtect: 0x20 Function: 0xfffff8099e8c8b30 (CI!IPEProcessNotify) Context: 0x0 (Normal) 7: EXCALLBACKROUTINEBLOCK 0xffffc98b8cb9e440 RundownProtect: 0x20 Function: 0xfffff8099f4e2e60 (dxgkrnl!DxgkProcessNotify) Context: 0x2 (Extended) 8: EXCALLBACKROUTINEBLOCK 0xffffc98b8e3ed150 RundownProtect: 0x20 Function: 0xfffff809a0e13ecc (vm3dmp+13ecc) Context: 0x0 (Normal) 9: EXCALLBACKROUTINE_BLOCK 0xffffc98b8eec1a30 RundownProtect: 0x20 Function: 0xfffff809a07ebbe0 (peauth+2bbe0)
    Context: 0x0 (Normal)
    Iterating over the nt!PspCreateThreadNotifyRoutine array at 0xfffff8036e6040d0.
    Expecting 2 nt!PspCreateThreadNotifyRoutineCount and 0 nt!PspCreateThreadNotifyRoutineNonSystemCount entries.
    0: EXCALLBACKROUTINEBLOCK 0xffffc98b8dd627a0 RundownProtect: 0x20 Function: 0xfffff8099f33c000 (WdFilter!MpCreateThreadNotifyRoutine) Context: 0x0 (Normal) 1: EXCALLBACKROUTINEBLOCK 0xffffc98b8c8df4a0 RundownProtect: 0x20 Function: 0xfffff809a0721ae0 (mmcss!CiThreadNotification)
    Context: 0x0 (Normal)
    Iterating over the nt!PspLoadImageNotifyRoutine array at 0xfffff8036e603ed0.
    Expecting 2 nt!PspLoadImageNotifyRoutineCount entries.
    0: EXCALLBACKROUTINEBLOCK 0xffffc98b8dd617a0 RundownProtect: 0x20 Function: 0xfffff8099f33fa50 (WdFilter!MpLoadImageNotifyRoutine) Context: 0x0 (Normal) 1: EXCALLBACKROUTINEBLOCK 0xffffc98b8df671c0 RundownProtect: 0x20 Function: 0xfffff8099fb45d60 (ahcache!CitmpLoadImageCallback)
    Context: 0x0 (Normal)

**  
**

**五、总结**

****

理清Windows中系统回调函数的工作原理后，我们就可以做许多有趣的事情。如上所述，我们可以编个程序，遍历每个回调数组，探测已注册的所有回调。这对于安全取证来说非常重要。

此外，这些底层数组不受[PatchGuard](https://en.wikipedia.org/wiki/Kernel_Patch_Protection)的保护。为了开发与64位系统上PatchGuard完美兼容的驱动，反病毒产品或多或少都需要注册回调函数，因此恶意软件可以动态禁用（或者替换）已注册的这些回调函数，以禁用安全防护服务。还有其他可能性能够实现相同目的。

非常感谢[ReactOS](https://www.reactos.org/)精心准备的文档资料。需要着重感谢的是ReactOS的[Alex
Ionescu](http://www.alex-ionescu.com/)，我用到的大多数结构都是他识别出来的。此外，也顺便感谢[PyKd](https://pykd.codeplex.com/)的[开发者](https://pykd.codeplex.com/team/view)，在我看来，这个工具比WinDbg原生脚本接口更加好用。

如果读者有需要的话，欢迎提出意见及建议。

本文翻译自triplefault.io [原文链接](http://www.triplefault.io/2017/09/enumerating-process-thread-and-image.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86909](/post/id/86909)

安全客 - 有思想的安全新媒体

本文转载自: [triplefault.io](http://www.triplefault.io/2017/09/enumerating-process-thread-and-image.html)

如若转载,请注明出处： <http://www.triplefault.io/2017/09/enumerating-process-thread-and-image.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

