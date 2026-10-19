  

# 前言

在windows里面调试跟异常息息相关，如果想要对调试得心应手，异常处理的知识是必不可少的，本文主要介绍的是软件调试方面的有关知识，讲解调试程序和被调试程序之间如何建立联系

## 调试对象

调试器和被调试程序

![image-20220331111724999.png](https://image.3001.net/images/20220531/1654000759_62960c77d52d02562202a.png!small)

调试器与被调试程序之间建立起联系的两种方式

  * CreateProcess

  * DebugActiveProcess

### 与调试器建立连接

首先看一下`DebugActiveProcess`

![image-20220331111629799.png](https://image.3001.net/images/20220531/1654000768_62960c804555212ee58ca.png!small)

调用`ntdll.dll`的`DbgUiConnectToDbg`

![image-20220331111914219.png](https://image.3001.net/images/20220531/1654000772_62960c84b111f300dadf6.png!small)

![image-20220331112008360.png](https://image.3001.net/images/20220531/1654000776_62960c886c709ca1550fd.png!small)

再调用`ZwCreateDebugObject`

![image-20220331112048790.png](https://image.3001.net/images/20220531/1654000780_62960c8c5f5fed690de26.png!small)

通过调用号进入0环

![image-20220331112119321.png](https://image.3001.net/images/20220531/1654000784_62960c906fe8b0e6da83c.png!small)

进入0环创建`DEBUG_OBJECT`结构体

    
    
    typedef struct _DEBUG_OBJECT {
         KEVENT EventsPresent;
         FAST_MUTEX Mutex;
         LIST_ENTRY EventList;
         ULONG Flags;
    } DEBUG_OBJECT, *PDEBUG_OBJECT;
    

然后到`ntoskrnl`里面看一下`NtCreateDebugObject`

![image-20220331113057515.png](https://image.3001.net/images/20220531/1654000788_62960c94f3344f4419f79.png!small)

然后调用了`ObInsertObject`创建`DebugObject`结构返回句柄

![image-20220331113136955.png](https://image.3001.net/images/20220531/1654000793_62960c999e26084d2abf9.png!small)

再回到`ntdll.dll`，当前线程回0环创建了一个`DebugObject`结构，返回句柄到3环存放在了TEB的`0xF24`偏移处

也就是说，遍历TEB的`0xF24`偏移的地方，如果有值则一定是调试器

![image-20220331113252356.png](https://image.3001.net/images/20220531/1654000798_62960c9e3bf67771f2308.png!small)

### 与被调试程序建立连接

还是回到`kernel32.dll`的`DebugActiveProcess`，获取句柄之后调用了`DbgUiDebugActiveProcess`

![image-20220331114614705.png](https://image.3001.net/images/20220531/1654000803_62960ca374e764f96d8a9.png!small)

调用`ntdll.dll`的`DbgUiDebugActiveProcess`

![image-20220331114716677.png](https://image.3001.net/images/20220531/1654000807_62960ca70f00eeeaf16c7.png!small)

跟到`ntdll.dll`里面的`DbgUiDebugActiveProcess`，传入两个参数，分别为调试器的句柄和被调试进程的句柄

![image-20220331114846279.png](https://image.3001.net/images/20220531/1654000810_62960caa024524decb548.png!small)

通过调用号进0环

![image-20220331115013208.png](https://image.3001.net/images/20220531/1654000813_62960cadccc998b15d739.png!small)

来到0环的`NtDebugActiveProcess`， 第一个参数为被调试对象的句柄，第二个参数为调试器的句柄

![image-20220331115116879.png](https://image.3001.net/images/20220531/1654000818_62960cb2c5f33e91267c7.png!small)

执行`ObReferenceObjectByHandle`，把被调试进程的句柄放到第五个参数里面，这里eax本来存储的是调试器的`EPROCESS`，执行完之后eax存储的就是被调试进程的`EPROCESS`

![image-20220331120028495.png](https://image.3001.net/images/20220531/1654000822_62960cb64a8aca4495a0d.png!small)

这里判断调试器打开的进程是否是自己，如果是自己则直接退出

![image-20220331143227822.png](https://image.3001.net/images/20220531/1654000826_62960cba43118a8c93f1c.png!small)

也不能调试系统初始化的进程

![image-20220331143429325.png](https://image.3001.net/images/20220531/1654000829_62960cbdc08f345df28e2.png!small)

然后获取调试对象的地址，之前是句柄，但是句柄在0环里面是无效的，这里就要找真正的地址

![image-20220331143605658.png](https://image.3001.net/images/20220531/1654000833_62960cc1e542b0b5c976d.png!small)

获取到调试对象的地址之后还是存到`ebp+Process`的地方，这里之前是被调试对象的地址，现在存储的是调试对象的地址

![image-20220331143902163.png](https://image.3001.net/images/20220531/1654000838_62960cc6299ba7377a256.png!small)

将调试进程和被调试的`PEPROCESS`传入`_DbgkpSetProcessDebugObject`，将调试对象和被调试进程关联起来

![image-20220331145648149.png](https://image.3001.net/images/20220531/1654000842_62960cca6e32fc0947838.png!small)

跟进函数，发现有判断`DebugPort`是否为0的操作，ebx为0，edi为被调试进程的EPROCESS，那么`edi+0bc`就是调试端口

![image-20220331145849944.png](https://image.3001.net/images/20220531/1654000846_62960cce7d41ceee50477.png!small)

然后再把调试对象的句柄放到被调试对象的`DebugPort`里面

![image-20220331150347451.png](https://image.3001.net/images/20220531/1654000851_62960cd3748b90adbfba0.png!small)

## 调试事件的采集

调试事件的种类

    
    
    typedef enum _DBGKM_APINUMBER
    {
        DbgKmExceptionApi = 0,	//异常
        DbgKmCreateThreadApi = 1,	//创建线程
        DbgKmCreateProcessApi = 2,	//创建进程
        DbgKmExitThreadApi = 3,	//线程退出
        DbgKmExitProcessApi = 4,	//进程退出
        DbgKmLoadDllApi = 5,		//加载DLL
        DbgKmUnloadDllApi = 6,	//卸载DLL
        DbgKmErrorReportApi = 7,	//已废弃
        DbgKmMaxApiNumber = 8,	//最大值
    } DBGKM_APINUMBER;	
    

调试事件的采集函数

![image-20220331160251734.png](https://image.3001.net/images/20220531/1654000856_62960cd8f1dc7c5ad5e9f.png!small)

当创建进程或者线程的时候，一定会调用`PspUserThreadStartup`

![image-20220331160332662.png](https://image.3001.net/images/20220531/1654000860_62960cdc99f8638778dda.png!small)

判断当前线程是否为当前进程的第一个线程，如果是的话就生成一个编号为1的调试事件

![image-20220331160457595.png](https://image.3001.net/images/20220531/1654000864_62960ce076447d50ae570.png!small)

再看一下退出线程必经的函数`PspExitThread`

![image-20220331172528276.png](https://image.3001.net/images/20220531/1654000868_62960ce41edd2ff0ed379.png!small)

判断`Debugport`是否为0，如果为0则不搜集信息

![image-20220331172641988.png](https://image.3001.net/images/20220531/1654000872_62960ce8385536e28bc37.png!small)

![image-20220331173503130.png](https://image.3001.net/images/20220531/1654000876_62960cec00bbcb94de6b1.png!small)

进入跳转，判断这个线程是不是当前最后一个线程，如果是则调用`DbgkExitProcess`

![image-20220331173645459.png](https://image.3001.net/images/20220531/1654000880_62960cf03b3f8f2236a19.png!small)

如果不是则调用`DbgkExitThread`

![image-20220331174052501.png](https://image.3001.net/images/20220531/1654000884_62960cf4146082a5544d7.png!small)

### DbgkpSendApiMessage

`DbgkpSendApiMessage`这个api主要就是将各种调试信息封装成一个结构体写到`_DEBUG_OBJECT`结构里面，无论是哪种事件，最后都会调用`DbgkpSendApiMessage`，如果想隐藏进程/线程的创建，就可以给`DbgkCreateThread`挂钩子，如果想隐藏所有的调试事件那么就可以给`DbgkpSendApiMessage`挂钩子

![image-20220331174541264.png](https://image.3001.net/images/20220531/1654000888_62960cf82938267c26985.png!small)

这里跟一下`DbgkExitThread`找`DbgkpSendApiMessage`的过程，跟进函数直接就可以看到`DbgkpSendApiMessage`

![image-20220331174839809.png](https://image.3001.net/images/20220531/1654000891_62960cfbad9245cb0684f.png!small)

所有搜集调试事件的api都会调用`DbgkpSendApiMessage`

![image-20220331175318674.png](https://image.3001.net/images/20220531/1654000895_62960cff559c6cd0df279.png!small)

![image-20220331175326227.png](https://image.3001.net/images/20220531/1654000899_62960d0349a0a229b550a.png!small)

`DbgkpSendApiMessage(x, x)`参数说明：

  1. 第一个参数：消息结构 每种消息都有自己的消息结构 共有7种类型

  2. 第二个参数：要不要把本进程内除了自己之外的其他线程挂起。

有些消息需要把其他线程挂起，比如CC
有些消息不需要把线程挂起，比如模块加载。`DbgkSendApiMessage`是调试事件收集的总入口，如果在这里挂钩子，调试器将无法调试。

### LoadLibrary

首先在`kernel32.dll`里面调用`RtlAllocateHeap`

![image-20220331175840245.png](https://image.3001.net/images/20220531/1654000904_62960d08a20df23ee4b07.png!small)

然后跟到`ntdll.dll`调用了`NtQueryPerformanceCounter`

![image-20220331175913433.png](https://image.3001.net/images/20220531/1654000908_62960d0c07d72343cb14b.png!small)

通过调用号进0环

![image-20220331175926381.png](https://image.3001.net/images/20220531/1654000911_62960d0f9717a24c6512d.png!small)

![image-20220331175949840.png](https://image.3001.net/images/20220531/1654000915_62960d1332b28ec0a0a1f.png!small)

总结来说，`LoadLibrary`首先调用`CreateMapping`创建一块共享内存，再通过`NtMapViewOfSection`映射到线性地址，调用`DbgkMapViewOfSection`将结构体发送给`DbgkpSendApiMessage`

### _DEBUG_OBJECT

    
    
    typedef struct _DEBUG_OBJECT {
         KEVENT EventsPresent;		//+00 用于指示有调试事件发生
         FAST_MUTEX Mutex;			//+10 用于同步互斥对象
         LIST_ENTRY EventList;		//+30 保存调试消息的链表
         ULONG Flags;				//+38 标志 调试消息是否已读取
    } DEBUG_OBJECT, *PDEBUG_OBJECT;
    

## 调试事件的处理

因为每种事件的调试信息不一样，所以会有很多种类(7种)的api去采集

![image-20220331220729871.png](https://image.3001.net/images/20220531/1654000920_62960d18ee06c0c881491.png!small)

编号的值也是对应的

![image-20220331221540163.png](https://image.3001.net/images/20220531/1654000924_62960d1cc8d8baaabfbaf.png!small)

![image-20220331221558581.png](https://image.3001.net/images/20220531/1654000928_62960d203b19cd22af1d7.png!small)

    
    
    // Debug1.cpp : Defines the entry point for the console application.
    //
    
    
    #include "stdafx.h"
    #include <iostream>
    #include <Windows.h>
    #include <stdlib.h>
    
    void TestDebugger()
    {
    	BOOL nIsContinue = NULL;
        STARTUPINFOA sw = { 0 };
        PROCESS_INFORMATION pInfo = { 0 };
        auto retCP = CreateProcessA("C:\\Dbgview.exe",NULL, NULL, NULL, TRUE,DEBUG_PROCESS|| DEBUG_ONLY_THIS_PROCESS, NULL, NULL, &sw, &pInfo);
        
    	if (retCP == 0)
        {
            printf("CreateProcess error : %d\n", GetLastError());
    		return;
        }
    
        while (TRUE)
        {
            DEBUG_EVENT debugEvent = { 0 };
            auto rDebugEvent = WaitForDebugEvent(&debugEvent, -1);
    
            if (rDebugEvent)
            {
    			switch (debugEvent.dwDebugEventCode)
    			{
    				 case EXCEPTION_DEBUG_EVENT:
    					 printf("EXCEPTION_DEBUG_EVENT\n");
    					 break;
    
    				 case CREATE_THREAD_DEBUG_EVENT:
    					 printf("CREATE_THREAD_DEBUG_EVENT\n");
    					 break;
    
    				 case CREATE_PROCESS_DEBUG_EVENT:
    					 printf("CREATE_PROCESS_DEBUG_EVENT\n");
    					 break;
    
    				 case EXIT_THREAD_DEBUG_EVENT:
    					 printf("EXIT_THREAD_DEBUG_EVENT\n");
    					 break;
    
    				 case EXIT_PROCESS_DEBUG_EVENT:
    					 printf("EXIT_PROCESS_DEBUG_EVENT\n");
    					 break;
    
    				 case LOAD_DLL_DEBUG_EVENT:
    					 printf("LOAD_DLL_DEBUG_EVENT\n");
    					 break;
    
    				 case UNLOAD_DLL_DEBUG_EVENT:
    					 printf("UNLOAD_DLL_DEBUG_EVENT\n");
    					 break;
    
    				 case OUTPUT_DEBUG_STRING_EVENT:
    					 printf("OUTPUT_DEBUG_STRING_EVENT\n");
    					 break;
    			} 
            }
    		//在发送事件event给调试器debugger时，被调试进程会被挂起，直到调试器调用了continueDebugEvent函数
            ContinueDebugEvent(debugEvent.dwProcessId, debugEvent.dwThreadId,DBG_CONTINUE);
        }
    }
    
    int main()
    {
        TestDebugger();
        system("pause");
        return 0;
    }
    
    

这里用调试模式启动windbg

![image-20220401105959845.png](https://image.3001.net/images/20220531/1654000934_62960d26d3f67589c53c8.png!small)

可以发现这里有一个异常，这里先打印一下异常处理返回的代码

    
    
    printf("EXCEPTION_DEBUG_EVENT : %x %x %x\n",debugEvent.u.Exception.ExceptionRecord.ExceptionAddress,debugEvent.u.Exception.ExceptionRecord.ExceptionCode,debugEvent.u.Exception.ExceptionRecord.ExceptionFlags);
    

![image-20220401110739388.png](https://image.3001.net/images/20220531/1654000938_62960d2a971e7272d8054.png!small)

将程序拖入OD看到系统有一个`int3`断点

![image-20220401111013210.png](https://image.3001.net/images/20220531/1654000942_62960d2e56beab77ffcb5.png!small)

那么为什么会有一个异常处理的事件呢？这里首先看一下进程的创建过程

    
    
    1.映射exe文件
    2.创建内核对象EPROCESS
    3.映射系统dll(ntdll.dll)
    4.创建线程内核对象ETHREAD
    5.系统启动线程
        映射dll(ntdll.LdrInitializeThunk)
        线程开始执行
    

在映射dll的过程中调用了`LdrInitializeThunk`这个api，`LdrInitializeThunk`会调用`LdrpInitializeProcess`初始化进程

首先找到TEB，然后找TEB的0x30偏移的PEB放入ebx

![image-20220401111818596.png](https://image.3001.net/images/20220531/1654000947_62960d33556074e60fcbe.png!small)

`DbgBreakPoint`其实就是`int3`的封装

![image-20220401111950688.png](https://image.3001.net/images/20220531/1654000950_62960d36c1a2b883784bc.png!small)

看一下交叉引用，可以看到`LdrpRunInitializeRoutines`引用了`DbgBreakPoint`

![image-20220401112037459.png](https://image.3001.net/images/20220531/1654000954_62960d3a3917c07f26992.png!small)

这里只有当程序处于调试模式的时候才会启动

![image-20220401112129503.png](https://image.3001.net/images/20220531/1654000957_62960d3db6e6f571bbc4d.png!small)

在内核文件里面看一下`NtDebugActiveProcess`

![image-20220401113546366.png](https://image.3001.net/images/20220531/1654000962_62960d42c44e920fa10b7.png!small)

会发送线程和模块的加载信息

![image-20220401113811656.png](https://image.3001.net/images/20220531/1654000966_62960d46773d18acd3a05.png!small)

但是这个信息是不靠谱的，因为这个api是通过遍历PEB链表的方式来寻找模块

在PEB的Ldr结构里面有三个模块，`DbgkpPostFakeProcessCreateMessages`这个api就是通过查询这个结构来判断加载了哪些模块

也就是说当程序加载完成之后，这个api才会去链表里面找模块，但是这个时候可能信息已经被摘除，所以如果要想更准确的获取信息，就可以通过遍历vad树的方式来获取1

## 异常的处理流程

处理流程

![image-20220401135907896.png](https://image.3001.net/images/20220531/1654000972_62960d4c10da13ed00191.png!small)

正常的异常处理流程

![image-20220401140234726.png](https://image.3001.net/images/20220531/1654000975_62960d4f64d7eb0775e0e.png!small)

产生异常的时候首先会将异常传递给调试器，如果调试器不处理则继续寻找异常处理函数

这里设置为异常为忽略的话就会执行自己的异常处理函数

![image-20220401140635618.png](https://image.3001.net/images/20220531/1654000978_62960d5291e6dfbd6f376.png!small)

![image-20220401141003958.png](https://image.3001.net/images/20220531/1654000981_62960d55f3ab5852cbaf0.png!small)

如果设置为不忽略的情况下就会一直断在某一行

![image-20220401141053693.png](https://image.3001.net/images/20220531/1654000985_62960d59701b37c9e62f9.png!small)

### UnhandledExceptionFilter

相当于编译器为我们生成了一段伪代码

    
    
    __try
    {
    
    }
    __except(UnhandledExceptionFilter(GetExceptionInformation())
    {
    	//终止线程
    	//终止进程
    }
    

只有程序被调试时，才会存在未处理异常

`UnhandledExceptionFilter`的执行流程：

    
    
    1) 通过NtQueryInformationProcess查询当前进程是否正在被调试，如果是，返回EXCEPTION_CONTINUE_SEARCH，此时会进入第二轮分发 
    
    2) 如果没有被调试： 
    
    查询是否通过SetUnhandledExceptionFilter注册处理函数 如果有就调用 
    
    如果没有通过SetUnhandledExceptionFilter注册处理函数 弹出窗口 让用户选择终止程序还是启动即时调试器 
    
    如果用户没有启用即时调试器，那么该函数返回EXCEPTION_EXECUTE_HANDLER
    

#### SetUnhandledExceptionFilter

如果没有通过`SetUnhandledExceptionFilter`注册异常处理函数，则程序崩溃

![image-20220401142104425.png](https://image.3001.net/images/20220531/1654000992_62960d607b0701fea3d3e.png!small)

![image-20220401142146258.png](https://image.3001.net/images/20220531/1654000996_62960d6437f5417782ecc.png!small)

测试代码如下，我自己构造一个异常处理函数`callback`并用`SetUnhandledExceptionFilter`注册，构造一个除0异常，当没有被调试的时候就会调用`callback`处理异常，然后继续正常运行，如果被调试则不会修复异常，因为这是最后一道防线，就会直接退出，起到反调试的效果

    
    
    // SEH7.cpp : Defines the entry point for the console application.
    //
    
    #include "stdafx.h"
    #include <windows.h>
    
    long _stdcall callback(_EXCEPTION_POINTERS* excp)
    {
    	excp->ContextRecord->Ecx = 1;
    	return EXCEPTION_CONTINUE_EXECUTION;
    }
    
    int main(int argc, char* argv[])
    {
    	SetUnhandledExceptionFilter(callback);
    
    	_asm
    	{
    		xor edx,edx
    		xor ecx,ecx
    		mov eax,0x10
    		idiv ecx
    	}
    
    	printf("Run again!");
    	getchar();
    	return 0;
    }
    

直接启动可以正常运行

![image-20220329113645787.png](https://image.3001.net/images/20220531/1654001061_62960da5244e555359a7e.png!small)

使用od打开则直接退出

![image-20220329113851211.png](https://image.3001.net/images/20220531/1654001057_62960da17a6073d381299.png!small)

![image-20220329113905022.png](https://image.3001.net/images/20220531/1654001065_62960da9c85b82b7ffb6f.png!small)

    
    
    // Debug3.cpp : Defines the entry point for the console application.
    //
    
    #include "stdafx.h"
    #include <windows.h>
    DWORD g_Test = 0;
    
    LONG NTAPI TopLevelExceptFilter(PEXCEPTION_POINTERS pExcepinfo)
    {
    	printf("The top_function fix the exception!\n");
    	g_Test = 1;
    	return EXCEPTION_CONTINUE_EXECUTION;
    
    }
    
    int main(int argc, char* argv[])
    {
    	int x = 0;
    	int y = 100;
    
    	SetUnhandledExceptionFilter(&TopLevelExceptFilter);
    
    	x = y/g_Test;
    
    	printf("正常逻辑开始执行\n");
    
    	for (int i=0;i<10;i++)
    	{
    		::Sleep(1000);
    		printf("%d\n", i);
    	}
    
    	getchar();
    	return 0;
    }
    

正常情况下执行程序

![image-20220401144025331.png](https://image.3001.net/images/20220531/1654001075_62960db30394e50e87c73.png!small)

如果是调试程序则直接退出

![image-20220401144253203.png](https://image.3001.net/images/20220531/1654001079_62960db7a8a843cb55d54.png!small)

