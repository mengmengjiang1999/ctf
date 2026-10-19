Sysmon是微软的一款轻量级的系统监控工具，被常常用来进行入侵检测分析，它通过系统服务和驱动程序实现记录进程创建、文件访问以及网络信息的记录，并把相关的信息写入并展示在windows的日志事件里。经常有安全人员使用这款工具去记录并分析系统进程的活动来识别恶意或者异常活动，下面开始讲解该软件的原理与实现。

下面开始上篇的讲解，ring3实现对网络数据记录以及对驱动返回的数据进行解析，而驱动部分则返回进程相关的信息以及进程访问文件注册表的数据给ring3。

 **1\. 判断当前操作系统是否是64位，如果是就执行64位的sysmon**

动态获取 **IsWow64Process** 的函数地址，然后调用 **IsWow64Process** 函数，判断当前是否是 **wow64**
，如果是就执行 **SysmonLunchIsAmd64** (),进入 **SysmonLunchIsAmd64** 函数

![1535817715_5b8ab7f34da0c.png!small](https://image.3001.net/images/20180902/1535817715_5b8ab7f34da0c.png!small)

通过 **GetNativeSystemInfo** 函数判断当前 **SystemInfo.wProcessorArchitecture**!=
**PROCESSOR_ARCHITECTURE_AMD64** 的值

![1535817741_5b8ab80da1aaa.png!small](https://image.3001.net/images/20180902/1535817741_5b8ab80da1aaa.png!small)

如果是 **PROCESSOR_ARCHITECTURE_AMD64** 则释放资源节中id =
1001的资源到当前进程的所在目录，这是一个内嵌在资源里的64位版本的sysmon的exe，释放完毕后，就开始执行这个64的Sysmon。下面就是Symon的64位资源图

![1535817767_5b8ab82750d2a.png!small](https://image.3001.net/images/20180902/1535817767_5b8ab82750d2a.png!small)

![1535817778_5b8ab832eff12.png!small](https://image.3001.net/images/20180902/1535817778_5b8ab832eff12.png!small)

本文还是主要以32位的sysmon来讲解，我们继续往下讲解

 **2\. 参数的检查**

**![1535817947_5b8ab8db94d32.png!small](https://image.3001.net/images/20180902/1535817947_5b8ab8db94d32.png!small)**接下来sysmon
会对参数进行检查，检查是否 **config、configuration、h、--nologon、？、help** **，**
非这些参数后，然后会接着解析具体的参数，根据参数是否加载规则。

![1535817991_5b8ab90792b87.png!small](https://image.3001.net/images/20180902/1535817991_5b8ab90792b87.png!small)我们看
**SysmonAnalyzeInitArgv** 函数具体看看sysmon有哪些参数，

![1535818011_5b8ab91b6b812.png!small](https://image.3001.net/images/20180902/1535818011_5b8ab91b6b812.png!small)g_commandLine里固定存贮所有的
sysmon参数，这里大概只列举出一部分，
**Install、i、Uninstall、Configuration、c、u、Manifest、m、DebugMode、nologo、AcceptEula、ConfigDefault、HashAlgorithms、NetworkConnect、ImageLoad、l、DriverName、ProcessAccess、CheckRevocation、PipeMonitoring**
等等。

![1535818069_5b8ab9554baf3.png!small](https://image.3001.net/images/20180902/1535818069_5b8ab9554baf3.png!small)如果是相应的参数就继续往下执行相应的动作。

![1535818086_5b8ab966cfbb0.png!small](https://image.3001.net/images/20180902/1535818086_5b8ab966cfbb0.png!small)通过检测参数
**sha、sha-1、md5、md-5、sha、sha256、imphash、imp-hash** 计算当前使用何种hash算法

![1535818118_5b8ab986151d9.png!small](https://image.3001.net/images/20180902/1535818118_5b8ab986151d9.png!small)

Sha： 1算法、Md5： 2 算法、sha：3算法、imphash：4 算法

接下来会加载内置在exe 内的 **Sysmonschema.xml**

![1535818162_5b8ab9b28f19b.png!small](https://image.3001.net/images/20180902/1535818162_5b8ab9b28f19b.png!small)

![1535819068_5b8abd3ce19d3.png!small](https://image.3001.net/images/20180902/1535819068_5b8abd3ce19d3.png!small)

 **Sysmonschema.xml** 的 **configuration** 规定了一些进程参数的说明，而events描述说明一些记录信息事件，比如

    
    
    <event name="SYSMON_CREATE_PROCESS"value="1" level="Informational" template="ProcessCreate" rulename="ProcessCreate" ruledefault="include"version="5">
    
    <data name="UtcTime" inType="win:UnicodeString"outType="xs:string" />
    
    <data name="ProcessGuid"inType="win:GUID" />
    
    <data name="ProcessId"inType="win:UInt32" outType="win:PID" />
    
    <data name="Image"inType="win:UnicodeString" outType="xs:string" />
    
    <data name="FileVersion"inType="win:UnicodeString" outType="xs:string" />
    
    <data name="Description"inType="win:UnicodeString" outType="xs:string" />
    
    <data name="Product"inType="win:UnicodeString" outType="xs:string" />
    
    <data name="Company"inType="win:UnicodeString" outType="xs:string" />
    
    <data name="CommandLine"inType="win:UnicodeString" outType="xs:string" />
    
    <data name="CurrentDirectory"inType="win:UnicodeString" outType="xs:string" />
    
    <data name="User"inType="win:UnicodeString" outType="xs:string" />
    
    <data name="LogonGuid" inType="win:GUID"/>
    
    <data name="LogonId"inType="win:HexInt64" />
    
    <data name="TerminalSessionId"inType="win:UInt32" />
    
    <data name="IntegrityLevel"inType="win:UnicodeString" outType="xs:string" />
    
    <data name="Hashes"inType="win:UnicodeString" outType="xs:string" />
    
    <data name="ParentProcessGuid"inType="win:GUID" />
    
    <data name="ParentProcessId"inType="win:UInt32" outType="win:PID" />
    
    <data name="ParentImage"inType="win:UnicodeString" outType="xs:string" />
    
    <data name="ParentCommandLine"inType="win:UnicodeString" outType="xs:string" />
    
    </event>

就说明了SYSMON_CREATE_PROCESS创建进程上报信息的一些数据内容及说明。

如果参数是PrintSchema

![1535819132_5b8abd7ca2878.png!small](https://image.3001.net/images/20180902/1535819132_5b8abd7ca2878.png!small)  
则解析并获取Sysmonschema的version，然后打印Sysmonschema 的信息

![1535819168_5b8abda01c6a8.png!small](https://image.3001.net/images/20180902/1535819168_5b8abda01c6a8.png!small)![1535819178_5b8abdaa7ad88.png!small](https://image.3001.net/images/20180902/1535819178_5b8abdaa7ad88.png!small)

 **3\. 注册日志记录事件**

![1535819195_5b8abdbb4dc58.png!small](https://image.3001.net/images/20180902/1535819195_5b8abdbb4dc58.png!small)

![1535819210_5b8abdca36278.png!small](https://image.3001.net/images/20180902/1535819210_5b8abdca36278.png!small)

Sysmon接着会通过 **EventRegister** ()函数注册一个GUID为 **{
5770385F-C22A-43E0-BF4C-06F5698FFBD9}** 的日志事件。然后sysmon会通过系统的
**wevtutil.exe的程序去注册该GUID的系统日志trace类** 。

![1535819284_5b8abe146e451.png!small](https://image.3001.net/images/20180902/1535819284_5b8abe146e451.png!small)

获取系统是否存在 **Microsoft-Windows-Sysmon** 的trace类，如果没有就加载exe资源中“ **SYSMONMAN**
”的资源到内存，然后释放写入系统临时目录下的文件名 **MANXXXX.tmp** 文件里

![1535819312_5b8abe30d7e4f.png!small](https://image.3001.net/images/20180902/1535819312_5b8abe30d7e4f.png!small)

该文件是定义 **{5770385F-C22A-43E0-BF4C-06F5698FFBD9}** 的 **Microsoft-Windows-Sysmon** 的trace事件的provider，用于sysmon的后续数据解析。

![1535819366_5b8abe66d3606.png!small](https://image.3001.net/images/20180902/1535819366_5b8abe66d3606.png!small)

![1535819375_5b8abe6fe1774.png!small](https://image.3001.net/images/20180902/1535819375_5b8abe6fe1774.png!small)

最后调用系统的 **”wevtutil.exe imMANXXXX.tmp”** 去注册安装事件类

![1535819413_5b8abe95705bb.png!small](https://image.3001.net/images/20180902/1535819413_5b8abe95705bb.png!small)

 **4\. 安装minifilter驱动**

![1535819430_5b8abea6d5f43.png!small](https://image.3001.net/images/20180902/1535819430_5b8abea6d5f43.png!small)

释放资源文件为 **1002** 的到系统目录 **Tmp/Sysmon.sys** ，资源 **1002** 文件是个 **pe**
文件，实际上是sysmon的文件注册表监控驱动。

![1535819453_5b8abebd2c3a7.png!small](https://image.3001.net/images/20180902/1535819453_5b8abebd2c3a7.png!small)

接下来继续就是安装这个驱动

![1535819475_5b8abed3cd682.png!small](https://image.3001.net/images/20180902/1535819475_5b8abed3cd682.png!small)

  
![1535819502_5b8abeee26820.png!small](https://image.3001.net/images/20180902/1535819502_5b8abeee26820.png!small)

Sysmon还会设置 **minifilter** 驱动的 **Altitude** 值为 **385201**

![1535819592_5b8abf480e97c.png!small](https://image.3001.net/images/20180902/1535819592_5b8abf480e97c.png!small)

最后开启驱动服务

![1535819568_5b8abf302b38b.png!small](https://image.3001.net/images/20180902/1535819568_5b8abf302b38b.png!small)

往驱动发送IO控制码： **0x8340008** （该控制码是给驱动更新配置规则）

![1535819604_5b8abf54603fe.png!small](https://image.3001.net/images/20180902/1535819604_5b8abf54603fe.png!small)

以上过程是大致的安装与启动的过程，接下来就是执行Sysmon服务的SysmonServiceMain例程。

![1535819625_5b8abf69450eb.png!small](https://image.3001.net/images/20180902/1535819625_5b8abf69450eb.png!small)

![1535819635_5b8abf7308845.png!small](https://image.3001.net/images/20180902/1535819635_5b8abf7308845.png!small)

 **5.数据的获取与解析**

接下来开始执行取数据的工作了。

 **第一步：文件进程注册表的事件监控**

![1535819647_5b8abf7f75da1.png!small](https://image.3001.net/images/20180902/1535819647_5b8abf7f75da1.png!small)

通过发送IO控制码: **0x83400000** ，打开文件驱动功能，接着sysmon会开启一个线程从驱动获取监控数据，通过发送IO控制码：
**0x83400004** ，去反复获取

![1535819668_5b8abf949341b.png!small](https://image.3001.net/images/20180902/1535819668_5b8abf949341b.png!small)

每隔500毫秒发送一次获取数据，堆大小 **0x400000** ,获取了数据后，则开始解析这raw data，这个raw数据的首四个字节是表示数据类型

Typedefstruct_Sysmon_Raw_Data

{

ULONG DataType;

}Sysmon_Raw_Data;

Case 1: 上报进程创建

ReportEventWriteEvent((int)&v147,(unsigned __int16 *)&g_CreateProcess,
(int)v1, v17);

Case 2: 文件时间改变

ReportEventWriteEvent((int)&v147,(unsigned __int16 *)&g_CreateFileTime,
(int)v1, v30);

Case 3：进程关闭

ReportEventWriteEvent((int)&v147,(unsigned __int16 *)&g_TerminateProcess,
(int)v1, 0);

Case 5：加载镜像

ReportEventWriteEvent((int)&v146,&g_ImageLoad, (int)v1, v50);

Case 7：创建远程线程

ReportEventWriteEvent((int)&v146,(unsigned __int16 *)&g_CreateRemoteThread,
(int)v1, 0);

Case 8：文件读

ReportEventWriteEvent((int)&v146,(unsigned __int16 *)&g_FileRead, (int)v1, 0);

Case 9：访问进程

ReportEventWriteEvent((int)&v146,(unsigned __int16 *)&g_ProcessAccess,
(int)v1, 0);

Case 10：文件创建

ReportEventWriteEvent((int)&v146,(unsigned __int16 *)&g_FileCreate, (int)v1,
v32);

Case 11：文件流事件

ReportEventWriteEvent((int)&v146,(unsigned __int16 *)&g_FileStreamCreate,
(int)v1, v35);

Case 12：注册表相关的事件

![1535819689_5b8abfa98596d.png!small](https://image.3001.net/images/20180902/1535819689_5b8abfa98596d.png!small)

Case 13：管道类事件

![1535819702_5b8abfb6f2702.png!small](https://image.3001.net/images/20180902/1535819702_5b8abfb6f2702.png!small)

 **第二步：网络链接事件的监控**

Sysmon还会创建一个ETW事件去监控网络连接的访问事件

![1535819721_5b8abfc94c554.png!small](https://image.3001.net/images/20180902/1535819721_5b8abfc94c554.png!small)

Net Trace 名：L"SYSMON TRACE";或者使用系统的L"NT Kernel Logger";

方法参考微软官方实例：<https://docs.microsoft.com/en-us/windows/desktop/etw/configuring-and-starting-the-nt-kernel-logger-session>

![1535819736_5b8abfd89624c.png!small](https://image.3001.net/images/20180902/1535819736_5b8abfd89624c.png!small)

事件回调EventCallBack()接受数据

![1535819751_5b8abfe774787.png!small](https://image.3001.net/images/20180902/1535819751_5b8abfe774787.png!small)

在解析数据时使用的是WMI Mof的方法来解析

![1535819765_5b8abff5a8f5f.png!small](https://image.3001.net/images/20180902/1535819765_5b8abff5a8f5f.png!small)![1535819774_5b8abffea5ce1.png!small](https://image.3001.net/images/20180902/1535819774_5b8abffea5ce1.png!small)

可以参考微软的官方例子：

<https://docs.microsoft.com/en-us/windows/desktop/etw/retrieving-event-data-using-mof>

 **第三步：接受上报数据写入windows的Application日志**

在第二部中我们可以看到通过ReportEventWriteEvent函数上报信息，在ReportEventWriteEvent函数里分两种情况系统API上报

![1535819828_5b8ac034c8482.png!small](https://image.3001.net/images/20180902/1535819828_5b8ac034c8482.png!small)

通过ReportEvent或者EventWrite两个其中一个API上报，而上报的事件IDD
类都是前面我们看到的Sysmon自己注册到系统的里<provider name="Microsoft-Windows-Sysmon"guid="{5770385F-C22A-43E0-BF4C-06F5698FFBD9}"symbol="SYSMON_PROVIDER"
resourceFileName="%filename%"messageFileName="%filename%">

<events>

的 **Microsoft-Windows-Sysmon**
事件代理，这个会生成到windows日志的Application项目下，具体会使用哪个API是根据windows的版本来选择的

![1535819864_5b8ac0587a3cf.png!small](https://image.3001.net/images/20180902/1535819864_5b8ac0587a3cf.png!small)

这里可以看到如果操作系统主版本，如果是vista之前的操作系统使用ReportEvent，如果是vista以及以上操作系统则使用EventWrite函数。

Sysmon记录上报了数据源通过注册的WMIEvent的wmi数据持久化过滤事件去过滤不会被记录的事件，我们下面看它如何实现的。

![1535819879_5b8ac067e7025.png!small](https://image.3001.net/images/20180902/1535819879_5b8ac067e7025.png!small)

在之前的服务启动入口有一个函数RegisterWmiEvent，该函数就是注册过滤WmiEvent的函数，我们继续往下看

函数开头会创

![1535819890_5b8ac0726fea7.png!small](https://image.3001.net/images/20180902/1535819890_5b8ac0726fea7.png!small)建实例
**IDD_WebCImv** ，class Id: **IID_IWbemLocatorGUID2**

 **< 0dc12a687h,0737fh,011cfh,088h,04dh,000h,0aah,000h,04bh,02eh,024h> **

链接”ROOT\\\Subscription”的服务

接着创建Stub插口

![1535819963_5b8ac0bb3d790.png!small](https://image.3001.net/images/20180902/1535819963_5b8ac0bb3d790.png!small)

 **g_WMIListenerEvent** 接口类型是 **IWbemObjectSink** ,其定义如下

    
    
    MIDL_INTERFACE("7c857801-7381-11cf-884d-00aa004b2e24")
    
    IWbemObjectSink :publicIUnknown
    
     {
    
    public:
    
    virtualHRESULTSTDMETHODCALLTYPEIndicate(
    
    /*[in] */longlObjectCount,
    
    /*[size_is][in] */__RPC__in_ecount_full(lObjectCount) IWbemClassObject **apObjArray)= 0;
    
    virtualHRESULTSTDMETHODCALLTYPESetStatus(
    
    /*[in] */longlFlags,
    
    /*[in] */HRESULThResult,
    
    /*[unique][in] */__RPC__in_optBSTRstrParam,
    
    /*[unique][in] */__RPC__in_optIWbemClassObject *pObjParam) =0;
    
        };

![1535819983_5b8ac0cf29b45.png!small](https://image.3001.net/images/20180902/1535819983_5b8ac0cf29b45.png!small)

然后执行

    
    
    "SELECT * FROM__InstanceOperationEventWITHIN 5WHERE TargetInstance ISA '__EventConsumer' ORTar"
    
                            "getInstance ISA'__EventFilter' OR TargetInstance ISA '__FilterToConsumerBinding'"
    
    g_WmiSubscriptProxy->lpVtbl->ExecNotificationQueryAsync(
    
    g_WmiSubscriptProxy,
    
    strQueryLanguage,
    
    strQuery,
    
               128,
    
               0,
    
               (IWbemObjectSink*)g_pIWebmObjectSink);

去设置 **WMiEvent** 的过滤事件，操作类型是所有操作 **InstanceOperationEvent** ，设置三种事件

 **EventConsumer'、EventFilter'、FilterToConsumerBinding'** ，查询时间是5秒一次，这样就注册了。

下面我们看 **g_WMIListenerEvent** 结构

![1535819997_5b8ac0dd8faf5.png!small](https://image.3001.net/images/20180902/1535819997_5b8ac0dd8faf5.png!small)

过滤事件就是在 **Indicate()** 函数中实现，会通过 **IWbemClassObject****
数组的形式输入，函数内会枚举数据，如果是要过滤的数据则循环枚举否则中断枚举。

至此本篇对sysmon的大致原理流程我们分析完毕，通过对它分析，学习它的实现过程，可以自己完成实现一个sysmon，当然也可以绕过sysmon的监控，这就需要读者自己去研究与发现。

