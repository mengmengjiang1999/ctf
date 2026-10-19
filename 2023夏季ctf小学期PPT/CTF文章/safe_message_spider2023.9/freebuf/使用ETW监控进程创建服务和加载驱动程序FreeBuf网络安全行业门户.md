做edr的同学大概都晓得edr中经常需要监控windows服务以及windows驱动模块的加载的监控，windows驱动的加载的监控的方法通常使用和windows模块加载监控的方法一样。

在内核驱动里使用PsSetLoadImageNotifyRoutine设置模块加载回调例程来监控ring3模块以及ring0模块的加载，回调函数
PsSetLoadImageNotifyRoutine的第二个参数判断，如果 Process Id是0 ，则表示加载驱动，如果Process
Id非零，则表示加载DLL。

但是这种方法监控驱动加载通常的进程Id是0，因为驱动加载的时候使用的是APC线程，当前上下文在系统线程内，所以得不到具体的进程id，堆栈如下  
![image](https://image.3001.net/images/20210521/1621609378_60a7cba2b85e66bdee22f.png!small)

# RetAddr : Args to Child : Call Site

00 fffff800`04b1748d : fffff880`0456b8a0 fffff880`031ac0d0 00000000`00000001
fffff800`04b74dfe : nt!DebugService2+0x5 01 fffff800`04b74ecb :
fffff880`031ac000 fffffa80`016de070 fffff880`0456b9b8 00000000`00000007 :
nt!DbgLoadImageSymbols+0x4d  
02 fffff800`04e47bfd : fffffa80`00eeee20 fffff8a0`0000001c fffff800`04d84a30
fffff880`0456b888 : nt!DbgLoadImageSymbolsUnicode+0x2b 03 fffff800`04e6286b :
fffff880`031ac000 fffff880`0456b8f8 00000000`00000000 fffff880`0456b8d8 :
nt!MiDriverLoadSucceeded+0x2bd  
04 fffff800`04e64ebd : fffff880`0456b9b8 00000000`00000000 00000000`00000000
00000000`00000000 : nt!MmLoadSystemImage+0x80b 05 fffff800`04e65875 :
00000000`00000001 00000000`00000000 00000000`00000000 fffffa80`0231c1e0 :
nt!IopLoadDriver+0x44d  
06 fffff800`04a8b161 : fffff800`00000000 ffffffff`8000077c fffff800`04e65820
fffffa80`006db040 : nt!IopLoadUnloadDriver+0x55 07 fffff800`04d21166 :
00000000`00000000 fffffa80`006db040 00000000`00000080 fffffa80`006b71d0 :
nt!ExpWorkerThread+0x111  
08 fffff800`04a5c486 : fffff800`04bf6e80 fffffa80`006db040 fffffa80`006da680
00000000`00000000 : nt!PspSystemThreadStartup+0x5a 09 00000000`00000000 :
fffff880`0456c000 fffff880`04566000 fffff880`0456ae60 00000000`00000000 :
nt!KiStartSystemThread+0x16

所以在当到达PsSetLoadImageNotifyRoutine的时候加载驱动模块的加载的时候pid就是0了，是否有其他方法可以监控到具体的进程？答案是肯定的，
那就是ETW。

ETW是个windows日志事件Trace，每个Trace日志都有他自己的Guid，要监控服务以及驱动加载的日志就得找到对应的GUID,这个GUID是多少呢，下面我们就来具体分析。  
最好的方式就是逆向调试分析，打开一个安装驱动服务的软件，比如我们这次使用的是  
![image](https://image.3001.net/images/20210521/1621609434_60a7cbda317bb111ce986.png!small)

![image](https://image.3001.net/images/20210521/1621609451_60a7cbeb8f3f6d62b50cf.png!small)

接下来就是上调试器附加这个进程  
![image](https://image.3001.net/images/20210521/1621609660_60a7ccbc459a52a577a2e.png!small)  
在调试器里找到CreateServiceW函数，发现这个函数会调用sechost.dll的sechost.CreateServiceW的函数  
![image](https://image.3001.net/images/20210521/1621609706_60a7cceac922a18db6d16.png!small)  
发现最终的实现是在这个sechost模块的CreateServiceW,在windows/system32的目录下找到对应的模块，在IDA下以及调试器看到，在运行到最后会调用
**NdrClientCall4**  
![image](https://image.3001.net/images/20210521/1621609741_60a7cd0d1f07c461c23da.png!small)

![image](https://image.3001.net/images/20210521/1621609760_60a7cd20dbfa4a4c9aac5.png!small)

![image](https://image.3001.net/images/20210521/1621609773_60a7cd2d028021260f69a.png!small)

注意该函数的第一个参数是pStubDescriptor，它的类型是PMIDL_STUB_DESC pStubDescriptor，是一个结构体

    
    
    typedef struct _MIDL_STUB_DESC {
    void *RpcInterfaceInformation;
    void * )(size_t) *(pfnAllocate;
    void()(void *) * pfnFree;
    union {
    handle_t *pAutoHandle;
    handle_t *pPrimitiveHandle;
    PGENERIC_BINDING_INFO pGenericBindingInfo;
    } IMPLICIT_HANDLE_INFO;
    const NDR_RUNDOWN *apfnNdrRundownRoutines;
    const GENERIC_BINDING_ROUTINE_PAIR *aGenericBindingRoutinePairs;
    const EXPR_EVAL *apfnExprEval;
    const XMIT_ROUTINE_QUINTUPLE *aXmitQuintuple;
    const unsigned char *pFormatTypes;
    int fCheckBounds;
    unsigned long Version;
    MALLOC_FREE_STRUCT *pMallocFreeStruct;
    long MIDLVersion;
    const COMM_FAULT_OFFSETS *CommFaultOffsets;
    const USER_MARSHAL_ROUTINE_QUADRUPLE *aUserMarshalQuadruple;
    const NDR_NOTIFY_ROUTINE *NotifyRoutineTable;
    ULONG_PTR mFlags;
    const NDR_CS_ROUTINES *CsRoutineTables;
    void *ProxyServerInfo;
    const NDR_EXPR_DESC *pExprInfo;
    } MIDL_STUB_DESC;

最主要的是结构体中的第一个字段RpcInterfaceInformation，这个结构是RPC接口的信息，定义这RPC的GUID，当前对应的是全局内存是dword_10008F38，所以它对应的是RPC的GUIID  
![image](https://image.3001.net/images/20210521/1621609851_60a7cd7b00ce7a3d45d34.png!small)  
可以看出GUID是 367ABB81-9844-35F1-AD32-98F038001003

![image](https://image.3001.net/images/20210521/1621609876_60a7cd94d1129f616cc2d.png!small)  
这个RPC 的GUID我们可以在微软的官方网页里找到

https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-scmr/4c8b7701-b043-400c-9350-dc29cfaa5e7a

The server interface is identified by UUID
367ABB81-9844-35F1-AD32-98F038001003, version 2.0, using the RPC well-known
endpoint "\PIPE\svcctl". The server MUST use RPC over SMB, ncacn_np or RPC
over TCP, or ncacn_ip_tcp as the RPC protocol sequence to the RPC
implementation, as specified in [MS-RPCE]. The server MUST specify the Simple
and Protected GSS-API Negotiation Mechanism (SPNEGO) (0x9) or NT LAN Manager
(NTLM) (0xA), or both, as the RPC Authentication Service (as specified in [MS-RPCE]). See [MS-RPCE] section 3.3.1.5.2.2 and [C706] section 13.

意思就是说说这个GUID的RPC对应的名字是\PIPE\svcctl，而且它是在server.exe的这个服务进程里创建的。

接下来的工作就是去逆向service.exe这个进程。  
在server.exe的程序里我们可以找到对应的RPC 接口函数是RCreateServiceW  
![image](https://image.3001.net/images/20210521/1621609941_60a7cdd5ee0f20a190989.png!small)  
接着会调用ScCreateServiceRpc

![image](https://image.3001.net/images/20210521/1621609956_60a7cde4779bcc567398d.png!small)  
在下面的地方我们会看到一个函数  
I_RpcBindingInqLocalClientPID(0i64, &Pid);，这个函数会获取当前RPC的客户端进程id  
![image](https://image.3001.net/images/20210521/1621609989_60a7ce05788ea1d334b32.png!small)  
接着就是输出日志，当然前提是这个日志已经开启并且有人去接收它，

![image](https://image.3001.net/images/20210521/1621610002_60a7ce123e0c7fccb0ae5.png!small)  
V22 就是pid，0x28是当前输出的KeyId，a17是模块名，a2是路径

注意此处的WPP_410463680eaf3577d867156ad5450ae6_Traceguids并非Etw的事件GUID，需要从WPP_GLOBAL_Control对应的结构体去找，在服务的进程的初始化会填充初始化这个GUID

在服务启动入口函数Main里  
![image](https://image.3001.net/images/20210521/1621610039_60a7ce37a7e615b30bfb9.png!small)  
会开启StarttraceSession  
![image](https://image.3001.net/images/20210521/1621610054_60a7ce4650bbf16e3709a.png!small)

![image](https://image.3001.net/images/20210521/1621610080_60a7ce60f1e4e1dd6832f.png!small)

ScStartTracingSession开函数里启动EnableTrace Etw日志  
![image](https://image.3001.net/images/20210521/1621610102_60a7ce761bb08bdd63ada.png!small)  
对应的GUID就是**ScmWppLoggingGuid ：{EBCCA1C2-AB46-4A1D-8C2A-906C2FF25F39}  
**  
![image](https://image.3001.net/images/20210521/1621610126_60a7ce8e3490ff9097e3d.png!small)  
 **其实ScmWppLoggingGuid对应的微软官方Trace名是Service Control Manager Trace**  
最终我们获取的就是这个GUID，当有了这个名字后我们就可以写demo去获取相应的信息来验证我们研究的结果  
伪代码如下  
GUID CBlueToothApiEvent::RegistryProvGuid = { 0xEBCCA1C2, 0xAB46, 0x4A1D,
0x8c, 0x2a, 0x90, 0x6c, 0x2f, 0xf2, 0x5f, 0x39 };

………….（注意中间略去ETW的创建开启代码，网络上很多这种代码。）

最关键的是Monitor的地方对PEVENT_RECORD值的判断要判断key id 是否是0x28,因为之前我们逆向时发现输出的key id是0x28  
Void Monitor(PEVENT_RECORD pEvent)  
{  
if (pEvent->EventHeader.EventDescriptor.Id == 0x28)  
{  
int i = 0;  
i++;  
}  
else if (pEvent->EventHeader.EventDescriptor.Id == 0x2A)  
{  
}  
}

写好之后我们就可以调试。使用之前的程序去创建服务。  
![image](https://image.3001.net/images/20210521/1621610164_60a7ceb44cfb6c0963385.png!small)

![image](https://image.3001.net/images/20210521/1621610190_60a7cece79305c0a583e3.png!small)  
他对应的Pid 是** 3356**

当点击安装的时候demo断点断捕获下来了  
![image](https://image.3001.net/images/20210521/1621610212_60a7cee4a690105065ccc.png!small)  
可以在内存里查看  
![image](https://image.3001.net/images/20210521/1621610223_60a7ceef51c9293552721.png!small)

UserData  
![image](https://image.3001.net/images/20210521/1621610252_60a7cf0cdd2db885e16af.png!small)

可以看到前面就是创建的服务名，那个e4 0d 00 00 就是进程Pid，内存颠倒过来就是00000de4 == 3356 ,
后面还有一块区域是要创建的服务对应的模块地址。  
到此验证ok，还有其他一些OpenService、StartService都可以找出来对应的key id，这个读者可以自行去研究发现。

