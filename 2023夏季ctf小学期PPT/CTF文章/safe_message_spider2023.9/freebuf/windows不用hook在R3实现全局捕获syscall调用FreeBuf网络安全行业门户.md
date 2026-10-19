## 前言

在R3下ETW实现了一套接口允许你拿到一些syscall调用信息，  
在cmd下,输入如下代码:

    
    
    logman start "NT Kernel Logger" -p "Windows Kernel Trace" (syscall) -o sys.etl -ets
    

一段时间后停止

    
    
    logman stop "NT Kernel Logger" -ets

接着转换成可读的格式:

    
    
    tracerpt sys.etl

你就看到对应的syscall了:

![](https://image.3001.net/images/20211022/1634871982_61722aae107726ac19f70.png!small)

 **但是,看情况我们目前只能拿得到两个信息:**

>   1. syscall的index
>   2. syscall的处理器id
>   3. syscall的地址
>

 **我们没办法拿到的信息并且是关键信息的有:**

>   1. syscall的进程id
>   2. syscall的具体名字/内容
>

 **我将会在这篇文章介绍一种非常巧妙的移花接木的方法来获取这些必要信息并且实现r3的dll注入检测。**

## 线程切换

我们需要第一步推导出syscall的调用者是谁,但是etw并没有给我们更多的详细信息,因此我们需要做一个hack去获取它,那就是通过线程切换事件。  
线程切换事件ETW也会给我们消息,我们能知道:  
1.老线程id  
2.新线程id  
3.老线程的状态  
4.当前处理器id

 **换言之,我们可以知道当前处理器在处理哪个线程,并且我们可以通过线程拿到进程id!**  
ETW的thread context switch event的flag名字为  
EVENT_TRACE_FLAG_CSWITCH,同时他的userdata结构为

    
    
    struct CSwitch
    {
        UINT32 NewThreadId;                        // + 0x00
        UINT32 OldThreadId;                        // + 0x04
        INT8 NewThreadPriority;                    // + 0x08
        INT8 OldThreadPriority;                    // + 0x09
        UINT8 PreviousCState;                    // + 0x0A
        INT8 SpareByte;                            // + 0x0B
        INT8 OldThreadWaitReason;                // + 0x0C
        INT8 OldThreadWaitMode;                    // + 0x0D
        INT8 OldThreadState;                    // + 0x0E
        INT8 OldThreadWaitIdealProcessor;        // + 0x0F
        UINT32 NewThreadWaitTime;                // + 0x10
        UINT32 Reserved;                        // + 0x14
    };
    C_ASSERT(sizeof(CSwitch) == 0x18);

opcode为36  
这是我自己给OldThreadState定义的enum:

    
    
    enum SwitchState
    {
        _SwitchState_Initialized = 0,
        _SwitchState_Ready = 1,
        _SwitchState_Running = 2,
        _SwitchState_Standby = 3,
        _SwitchState_Terminated = 4,
        _SwitchState_Waiting = 5,
        _SwitchState_Transition = 6,
        _SwitchState_DeferredReady = 6,
    };

实现起来非常简单,我们需要:  
当发生切换的时候,我们需要知道CPUID从哪个线程切换到哪个线程,然后我们把切换到的线程设计为活动,被切换的old
thread设置为不活动,只需要两个hashmap就能解决这个问题:

    
    
    CSwitch* pThrSwitch = (CSwitch*)EventRecord->UserData;
                _ASSERT(EventRecord->UserDataLength == sizeof(CSwitch));
                dwNewThrId = pThrSwitch->NewThreadId;
                dwOldThrId = pThrSwitch->OldThreadId;
    
                g_dwProcesserWithThreadsMap[cpuId] = dwNewThrId;
                if (g_dwProcessWithThreadidsMap.count(dwNewThrId) == 0) {
                    NewProcessAdd(dwNewThrId);
                }
                if (g_dwProcessWithThreadidsMap.count(dwOldThrId) == 0) {
                    NewProcessAdd(dwOldThrId);
                }
                if (g_dwProcessWithThreadidsMap.count(dwOldThrId) != 0 && pThrSwitch->OldThreadState == _SwitchState_Terminated) {
                    if (g_dwProcessNameWithProcessIdMap.count(g_dwProcessWithThreadidsMap[dwOldThrId]) != 0) {
                        g_dwProcessNameWithProcessIdMap.erase(g_dwProcessWithThreadidsMap[dwOldThrId]);
                    }
                    g_dwProcessWithThreadidsMap.erase(dwOldThrId);
                }

此外,当有新的线程被加入的时候,我们还需要缓存他的线程id->进程名字表

    
    
    VOID WINAPI NewProcessAdd(DWORD pThreadId) {
        HANDLE ThreadHandle = OpenThread(THREAD_QUERY_INFORMATION, FALSE, pThreadId);
        if (ThreadHandle != INVALID_HANDLE_VALUE && ThreadHandle != NULL) {
            DWORD ProcessId = GetProcessIdOfThread(ThreadHandle);
            if (ProcessId != NULL) {
                std::wstring TempStr = GetProcessNameByPid(ProcessId);
                if (TempStr.find(L"unknown") == std::wstring::npos) {
                    g_dwProcessWithThreadidsMap[pThreadId] = ProcessId;
                    g_dwProcessNameWithProcessIdMap[ProcessId] = TempStr;
                    g_StopDetectList[TempStr] = false;
                }
            }
            CloseHandle(ThreadHandle);
        }
    }

此时我们就有了三个表：  
线程id <-> 进程id  
进程pid <-> 进程名字  
处理器id <-> ThreadId  
设置trace flag为EVENT_TRACE_FLAG_SYSTEMCALL,Trace syscall 事件  
syscall的opcode为51  
此时我们就可以通过处理器id拿到线程id(因为调用syscall的时候线程id始终是在被处理器调用的)  
也可以根据进程id拿到进程名字。

    
    
    DWORD ThreadId = g_dwProcesserWithThreadsMap[cpuId];
    std::wstring ProcessName = g_dwProcessNameWithProcessIdMap[g_dwProcessWithThreadidsMap[ThreadId]];

## Syscall -> Name

此时我们可以知道某个进程调用了syscall,但是我们不知道调用的syscall具体名字,因为微软甚至是连syscall
index都没有给,只是给了个内核地址.为了解决这个问题,有两个方案可以选择:  
1.加载ntos,手动搜索到ssdt table,计算真实function的地址,然后对应地址做解析  
2.加载符号  
我这边选择了加载符号  
加载符号使用dbghelp.h相关的api,如下:  
DownloadSymbol、SymFromName、SymFromAddr  
其中值得注意的是,调用SymFromAddr的时候需要。

    
    
    地址 - ntosbase + ntosbase的长度

调用SymFromName的时候反着来，

    
    
    SymInfo->Address - ntosbase的长度 + NtosBase
    

源码如下:

    
    
    BOOL
    WINAPI
    GetSystemFunctionName(
        IN ULONG64 pAddress,
        OUT CHAR* pName
    ) {
        DWORD64  dwDisplacement = 0;
        char buffer[sizeof(SYMBOL_INFO) + MAX_SYM_NAME * sizeof(TCHAR)];
        PSYMBOL_INFO pSymbol = (PSYMBOL_INFO)buffer;
    
        pSymbol->SizeOfStruct = sizeof(SYMBOL_INFO);
        pSymbol->MaxNameLen = MAX_SYM_NAME;
    
        BOOL result = SymFromAddr(g_symbols_ProcessHandle, pAddress - NtosBase + NtosKrnl, &dwDisplacement, pSymbol);
        memcpy(pName, pSymbol->Name, strlen(pSymbol->Name));
        return result;
    }

此时,我们就能成功解析出名字。

![](https://image.3001.net/images/20211022/1634872181_61722b75c052fdf061a66.png!small)

## 注入检测[meme]

我们可以给文件名字做个分组，  
当依次调用下面API的时候,我们可以认为他在注入进程:

    
    
    NtCreateFile
    NtCreateThreadEx
    NtAllocateVirtualMemory
    NtWriteVirtualMemory
    NtOpenProcess
    NtOpenProcessToken
    NtCreateThread

简单的逻辑,虽然是meme,但是也挺好玩的:

![](https://image.3001.net/images/20211022/1634872222_61722b9ed507cc79c5d27.png!small)

## 反思

本来想通过zwquerythreadinformation的lastsystemcall字段拿到线程上次syscall信息。但是,R3要拿到这个字段的前提是线程必须是挂起状态(waitting),所以失败了。R0是可以直接解析结构体拿到这个字段的。

