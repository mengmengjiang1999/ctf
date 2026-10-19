上文讲解了sysmon的ring3部分实现原理，本文则开始讲解ring0部分。Sysmon的ring0是一个minifilter类型的驱动，内部实现了进程信息、文件访问信息以及注册表访问信息的记录，下面开始具体讲解它的实现流程。

##  **一、** **驱动DriverEntry** **的初始化**

从 **DriverEntry(PDRIVER_OBJECTDriverObject, UNICODE_STRING *pRegistry)**
的pRegistry中截取末尾名称去获取并计算出设备名和DosDevices的名字。

    
    
    pDriverName= pRegistry->Buffer;   Len = pRegistry->Length >> 1;   pFirstName = &pDriverName[Len];   if ( pFirstName == pDriverName )   { LABEL_8:     if ( *pFirstName != '\\' )       goto LABEL_10;   }   else   {     while ( *pFirstName != '\\' )     {       --pFirstName;       if ( pFirstName == pDriverName )         goto LABEL_8; }   }   ++pFirstName;

![1537273661_5ba0ef3d15daa.png!small](https://image.3001.net/images/20180918/1537273661_5ba0ef3d15daa.png!small)然后从pRegistry注册表中去获取sysmon的策略规则

![1537273679_5ba0ef4f48d13.png!small](https://image.3001.net/images/20180918/1537273679_5ba0ef4f48d13.png!small)

使用RtlQueryRegistryValues函数，填入5个RTL_QUERY_REGISTRY_TABLE结构体

    
    
    RTL_QUERY_REGISTRY_TABLE QueryRegTable[5];
    
    RtlInitUnicodeString(&g_ProcessAccessNamesRule,0);
    
      memset(QueryRegTable, 0, 560u);
    
      QueryRegTable[0].Flags = 1;
    
      QueryRegTable[0].Name =L"Parameters";   QueryRegTable[3].EntryContext =&ampOptionRulesv18   QueryRegTable[4].EntryContext =&hash_alogrithms;   QueryRegTable[1].Flags = 304;   QueryRegTable[1].Name =g_Name_ProcessAccessNames;   QueryRegTable[1].EntryContext =&g_ProcessAccessNamesRule;   QueryRegTable[1].DefaultType = 0x7000007;   QueryRegTable[1].DefaultData =&unk_10015C34;   QueryRegTable[1].DefaultLength = 4;   QueryRegTable[2].Flags = 304;   QueryRegTable[2].Name = L"ProcessAccessMasks";   QueryRegTable[2].EntryContext =&g_ProcessAccessMasksRule;   QueryRegTable[2].DefaultType = 0x3000000;   QueryRegTable[3].Flags = 304;   QueryRegTable[3].Name =(PWSTR)&g_wOption;   QueryRegTable[3].DefaultType = 0x4000000;   QueryRegTable[4].Flags = 304;   QueryRegTable[4].Name =(PWSTR)&g_wHashingalgorithm;   QueryRegTable[4].DefaultType = 0x4000000;   RtlQueryRegistryValues(0,g_SysmonRegisterPath.Buffer, QueryRegTable, 0, 0);   if ( !g_ProcessAccessNamesRule.Buffer     || g_ProcessAccessNamesRule.Length <= 2u     || g_ProcessAccessNamesRule.MaximumLength<= 4u )   {    RtlFreeUnicodeString(&g_ProcessAccessNamesRule);    RtlInitUnicodeString(&g_ProcessAccessNamesRule, 0);   }
    
      g_OptionRules =(OptionRulesv18 >> 1) & 1;

对应的注册表键分别是L"Parameters"、L”ProcessAccessNames”、L"ProcessAccessMasks" 、L”
Option”、L” Hashingalgorithm”

![1537273707_5ba0ef6b1e738.png!small](https://image.3001.net/images/20180918/1537273707_5ba0ef6b1e738.png!small)然后再次获取L"Parameters"项下面的对应的L"Rules"的KeyValues信息，这里是驱动设置的规则。

![1537273723_5ba0ef7bb31e3.png!small](https://image.3001.net/images/20180918/1537273723_5ba0ef7bb31e3.png!small)下面展示出部分规则的数组

![1537273737_5ba0ef89a6def.png!small](https://image.3001.net/images/20180918/1537273737_5ba0ef89a6def.png!small)

上面的过程结束后就开始判断操作系统是否支持flt

![1537273756_5ba0ef9ccfb28.png!small](https://image.3001.net/images/20180918/1537273756_5ba0ef9ccfb28.png!small)

如果支持只实现IRP_MJ_CREATE、IRP_MJ_CLOSE
、IRP_MJ_DEVICE_CONTROL三个例程，后续会注册miniFlt过滤，如果不支持Flt就使用老的模式Sfilter的模式

    
    
    DriverObject->MajorFunction[IRP_MJ_DEVICE_CONTROL]= (PDRIVER_DISPATCH)SysmonDispatchIrp;   DriverObject->MajorFunction[IRP_MJ_CLOSE]= (PDRIVER_DISPATCH)SysmonDispatchIrp;   DriverObject->MajorFunction[IRP_MJ_CREATE]= (PDRIVER_DISPATCH)SysmonDispatchIrp;   if ( IsOpenPipeConnect &&!IsSupportFlt )
    
      {
    
       DriverObject->MajorFunction[IRP_MJ_CREATE] =(PDRIVER_DISPATCH)SysmonDispatchIrp;     DriverObject->MajorFunction[1] =(PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_CLOSE] =(PDRIVER_DISPATCH)SysmonDispatchIrp;     DriverObject->MajorFunction[IRP_MJ_READ]= (PDRIVER_DISPATCH)SysmonDispatchIrp;     DriverObject->MajorFunction[IRP_MJ_WRITE]= (PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_QUERY_INFORMATION] =(PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_SET_INFORMATION] =(PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_QUERY_EA] =(PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_SET_EA] =(PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_FLUSH_BUFFERS] =(PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_QUERY_VOLUME_INFORMATION] =(PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_SET_VOLUME_INFORMATION] =(PDRIVER_DISPATCH)SysmonDispatchIrp;     DriverObject->MajorFunction[IRP_MJ_DIRECTORY_CONTROL]= (PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_FILE_SYSTEM_CONTROL] =(PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_DEVICE_CONTROL] =(PDRIVER_DISPATCH)SysmonDispatchIrp;     DriverObject->MajorFunction[IRP_MJ_INTERNAL_DEVICE_CONTROL]= (PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_SHUTDOWN] =(PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_LOCK_CONTROL] = (PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_CLEANUP] =(PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_CREATE_MAILSLOT] =(PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_QUERY_SECURITY] =(PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_SET_SECURITY] =(PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_POWER] =(PDRIVER_DISPATCH)SysmonDispatchIrp;     DriverObject->MajorFunction[IRP_MJ_SYSTEM_CONTROL]= (PDRIVER_DISPATCH)SysmonDispatchIrp;
    
       DriverObject->MajorFunction[IRP_MJ_DEVICE_CHANGE] =(PDRIVER_DISPATCH)SysmonDispatchIrp;    DriverObject->MajorFunction[IRP_MJ_QUERY_QUOTA] =(PDRIVER_DISPATCH)SysmonDispatchIrp;     DriverObject->MajorFunction[IRP_MJ_SET_QUOTA]= (PDRIVER_DISPATCH)SysmonDispatchIrp;
    
      } 

然后就是常规过程，IoCreateDevice、IoCreateSymbolicLink。

![1537273784_5ba0efb85f136.png!small](https://image.3001.net/images/20180918/1537273784_5ba0efb85f136.png!small)然后根据操作系统是否支持FltRegisterFilter(Driver,
&g_Registration, &g_pFilter);

![1537273797_5ba0efc5f03b0.png!small](https://image.3001.net/images/20180918/1537273797_5ba0efc5f03b0.png!small)具体创建了哪些minifilter，接着看结构体

![1537273811_5ba0efd3d1cee.png!small](https://image.3001.net/images/20180918/1537273811_5ba0efd3d1cee.png!small)

    
    
    OperationRegistrationdd IRP_MJ_CREATE  ; DATA XREF:.data:10015014↓o
    
    .rdata:10013454                 dd 0
    
    .rdata:10013458                 dd offset PreOperation
    
    .rdata:1001345C                 dd offset PostOperation
    
    .rdata:10013460                 dd 0
    
    .rdata:10013464                 dd IRP_MJ_CLEANUP
    
    .rdata:10013468                 dd 0
    
    .rdata:1001346C                 dd offset PreOperation
    
    .rdata:10013470                 dd offset PostOperation
    
    .rdata:10013474                 dd 0
    
    .rdata:10013478                 dd IRP_MJ_SET_INFORMATION
    
    .rdata:1001347C                 dd 0
    
    .rdata:10013480                 dd offset PreOperation
    
    .rdata:10013484                 dd offset PostOperation
    
    .rdata:10013488                 dd 0
    
    .rdata:1001348C                 dd IRP_MJ_CLOSE
    
    .rdata:10013490                 dd 0
    
    .rdata:10013494                 dd offset PreOperation
    
    .rdata:10013498                 dd offset PostOperation
    
    .rdata:1001349C                 dd 0
    
    .rdata:100134A0                 dd IRP_MJ_CREATE_NAMED_PIPE
    
    .rdata:100134A4                 dd 0
    
    .rdata:100134A8                 dd offset PreOperation
    
    .rdata:100134AC                 dd offset PostOperation
    
    .rdata:100134B0                 dd 0
    
    .rdata:100134B4                 dd IRP_MJ_OPERATION_END
    
    .rdata:100134B8                 dd 0
    
    .rdata:100134BC                 dd 0
    
    .rdata:100134C0                 dd 0
    
    .rdata:100134C4                 dd 0

从上可以看到minifilter过滤了 **IRP_MJ_CREATE** 、 **IRP_MJ_CLEANUP** 、
**IRP_MJ_SET_INFORMATION** 、 **IRP_MJ_CLOSE** 、 **IRP_MJ_CREATE_NAMED_PIPE**

文件系统相关的注册完毕，然后就是设置一些进程、线程相关的回调函数例程

    
    
    PsSetLoadImageNotifyRoutine(SysmonLoadImageNotifyRoutine); PsSetCreateThreadNotifyRoutine(PsCreateThreadNotifyRoutine); PsSetCreateProcessNotifyRoutine(PsCreateProcessNotifyRoutine, 0);

![1537273834_5ba0efea27450.png!small](https://image.3001.net/images/20180918/1537273834_5ba0efea27450.png!small)

![1537273843_5ba0eff3598b2.png!small](https://image.3001.net/images/20180918/1537273843_5ba0eff3598b2.png!small)为了记录注册表sysmon还注册表注册表CmRegisterCallback(RegisterCallback,
0, &Cookie);回调，

![1537273858_5ba0f002545aa.png!small](https://image.3001.net/images/20180918/1537273858_5ba0f002545aa.png!small)

为了记录进程open对象的事件注册了ob事件

    
    
    g_bIsRegisterCallback= 1;
    
      g_OperationRegistration.ObjectType =(POBJECT_TYPE *)PsProcessType;
    
      g_OperationRegistration.Operations = 1;
    
      g_OperationRegistration.PreOperation =PreProcessOperation;
    
      g_OperationRegistration.PostOperation =PostProcessOperation;
    
      g_CallbackRegistration.OperationRegistration= &g_OperationRegistration;
    
      *(_DWORD*)&g_CallbackRegistration.Version = 0x10100;
    
      g_CallbackRegistration.RegistrationContext =0;
    
      RtlInitUnicodeString(&g_CallbackRegistration.Altitude,L"1000");
    
      Status =g_ObRegisterCallbacks(&g_CallbackRegistration, &RegistrationHandle);

![1537273875_5ba0f013e196b.png!small](https://image.3001.net/images/20180918/1537273875_5ba0f013e196b.png!small)

为了获取管道的事件，它挂接了设备L\\\Device\\\NamedPipe，创建了L\\\Device\\\SysmonPipeFilter的过滤设备

![1537273892_5ba0f0242f271.png!small](https://image.3001.net/images/20180918/1537273892_5ba0f0242f271.png!small)至此sysmon的DriverEntry的初始化动作基本结束了。

##  **二、** **IRP_MJ_DEVICE_CONTROL** **例程**

 **Case 0x83400000:**

打开驱动开启标志，并且获取且保存当前UI进程的句柄

![1537273918_5ba0f03edab05.png!small](https://image.3001.net/images/20180918/1537273918_5ba0f03edab05.png!small)![1537273924_5ba0f04479633.png!small](https://image.3001.net/images/20180918/1537273924_5ba0f04479633.png!small)

 **Case 0x83400004** **：**

Ring3请求事件信息，并返回到ring3的缓冲区

![1537273940_5ba0f0549713b.png!small](https://image.3001.net/images/20180918/1537273940_5ba0f0549713b.png!small)

 **Case 0x83400008** **：**

加载策略规则

![1537273955_5ba0f063760e1.png!small](https://image.3001.net/images/20180918/1537273955_5ba0f063760e1.png!small)

 **Case 0x8340000C** ：

获取传入进程的相关信息（包括TokenUser、pTokenStatics、TokenGroup、TokenSeesion）

![1537273969_5ba0f071a979e.png!small](https://image.3001.net/images/20180918/1537273969_5ba0f071a979e.png!small)![1537273976_5ba0f07895880.png!small](https://image.3001.net/images/20180918/1537273976_5ba0f07895880.png!small)还会获取进程pImagePathName、pCommandLine、CurrentDirectory

![1537273987_5ba0f083ca84a.png!small](https://image.3001.net/images/20180918/1537273987_5ba0f083ca84a.png!small)获取进程的CreateTime

![1537273999_5ba0f08fd45b6.png!small](https://image.3001.net/images/20180918/1537273999_5ba0f08fd45b6.png!small)该事件类型为4或者1

![1537274011_5ba0f09b971da.png!small](https://image.3001.net/images/20180918/1537274011_5ba0f09b971da.png!small)

##  **三、文件信息的记录**

Minifilter的PreOperation(PFLT_CALLBACK_DATA pData,
PFLT_RELATED_OBJECTSFltObjects, PVOID
*CompletionContext)例程为主要的判断逻辑例程，先判断当前FileObject的路径是否为管道路径，管道事件直接记录上报事件

![1537274031_5ba0f0afb7199.png!small](https://image.3001.net/images/20180918/1537274031_5ba0f0afb7199.png!small)特别判断下IRP_MJ_SET_INFORMATION、IRP_MJ_CLEANUP,并且分别上报_，注意在判断IRP_MJ_SET_INFORMATION的时候只记录了RequestorMode是1即USER_MODE，并且是设置FileBasicInformation的请求。

![1537274045_5ba0f0bd0334c.png!small](https://image.3001.net/images/20180918/1537274045_5ba0f0bd0334c.png!small)![1537274050_5ba0f0c2091c3.png!small](https://image.3001.net/images/20180918/1537274050_5ba0f0c2091c3.png!small)PreOperation处理完毕，则PostOperation(PFLT_CALLBACK_DATA
pData, PFLT_RELATED_OBJECTSpFltFileObj, PVOID CompletionContext, int
Flags)对前者处理的上下文CompletionContext进行记录日志或者释放的处理，以IRP_MJ_SET_INFORMATION为例，PostOPerate则对PreOperate的CompletionContext的数据进行上报。

![1537274063_5ba0f0cfe72bf.png!small](https://image.3001.net/images/20180918/1537274063_5ba0f0cfe72bf.png!small)

##  **四、注册表信息的记录**

Sysmon初始化的时候注册了一个注册表过滤，CmRegisterCallback(RegisterCallback, 0,
&Cookie);回调函数是NTSTATUS__stdcall RegisterCallback(PVOID CallbackContext, PVOID
Argument1, PVOIDArgument2)，参数Argument1是过滤的注册表操作类型，sysmon过滤了0（RegNtDeleteKey /
RegNtPreDeleteKey） 、4(
RegNtRenameKey\RegNtPreRenameKey)、11（RegNtPostCreateKey）、15（RegNtPostDeleteKey）、16（RegNtPostSetValueKey）、17（RegNtPostDeleteValueKey）、19（RegNtPostRenameKey）27（RegNtPostCreateKeyEx）的注册表操作

![1537274082_5ba0f0e225aef.png!small](https://image.3001.net/images/20180918/1537274082_5ba0f0e225aef.png!small)![1537274087_5ba0f0e702125.png!small](https://image.3001.net/images/20180918/1537274087_5ba0f0e702125.png!small)![1537274092_5ba0f0ec86889.png!small](https://image.3001.net/images/20180918/1537274092_5ba0f0ec86889.png!small)

##  **五、进程操作过滤**

Sysmon注册了进程操作过滤，g_ObRegisterCallbacks(&g_CallbackRegistration,
&RegistrationHandle);，

![1537274145_5ba0f121bf908.png!small](https://image.3001.net/images/20180918/1537274145_5ba0f121bf908.png!small)他只记录操作类型为OB_OPERATION_HANDLE_CREATE，并且只记录A进程操作B进程，A和B不是同一个进程，注意RtlWalkFrameChain这个函数是获取当前操作线程的线程栈，KeQuerySystemTime(&pOpenInfo.CreateTime);是获取当前系统时间，并且会把这些信息上报。

##  **六、其他重点技术细节**

1\. 进程模块的枚举

![1537274172_5ba0f13c574d9.png!small](https://image.3001.net/images/20180918/1537274172_5ba0f13c574d9.png!small)

ZwQueryInformationProcess(ProcessHandle,
ProcessBasicInformation,&ProcessInformation, 0x18u,
0)获取ProcessInformation的信息，从PebBaseAddress=
ProcessInformation.PebBaseAddress;取得进程PEB的地址，在PEB结构中得到LDR的地址，LDR是进程加载模块的结构体，

    
    
    struct _PEB
    
    {
    
    UCHAR InheritedAddressSpace;
    
    UCHAR ReadImageFileExecOptions;
    
    UCHAR BeingDebugged;
    
    UCHAR BitField;
    
    PVOID Mutant;
    
    PVOID ImageBaseAddress;
    
    PPEB_LDR_DATA Ldr;
    
    PRTL_USER_PROCESS_PARAMETERS ProcessParameters;
    
    PVOID SubSystemData;
    
    PVOID ProcessHeap;
    
    PRTL_CRITICAL_SECTION FastPebLock;
    
    PVOID AtlThunkSListPtr;
    
    PVOID IFEOKey;
    
    ULONG CrossProcessFlags;
    
    unsigned __int32 ProcessInJob : 1;
    
    unsigned __int32 ProcessInitializing : 1;
    
    unsigned __int32 ReservedBits0 : 30;
    
    union
    
    {
    
    PVOID KernelCallbackTable;
    
    PVOID UserSharedInfoPtr;
    
    };
    
    ULONG SystemReserved[1];
    
    。。。。。。
    
    } 

PPEB_LDR_DATA Ldr;这个就是加载模块的结构，有三种加载表内存加载表，加载顺序表，初始化加载表从中可以枚举出模块信息。

struct _PEB_LDR_DATA

{

ULONG Length;

UCHAR Initialized;

PVOID SsHandle;

LIST_ENTRY InLoadOrderModuleList;

LIST_ENTRY InMemoryOrderModuleList;

LIST_ENTRY InInitializationOrderModuleList;

};

![1537274198_5ba0f15681b1d.png!small](https://image.3001.net/images/20180918/1537274198_5ba0f15681b1d.png!small)

2\. 进程参数的获取

大致可以看到如下，首先要KeStackAttachProcess进程的空间，然后获取PEB地址，从PEB中的到ProcessParameters的结构

![1537274218_5ba0f16a0be0d.png!small](https://image.3001.net/images/20180918/1537274218_5ba0f16a0be0d.png!small)

ProcessParameters结构如下：

    
    
    struct _RTL_USER_PROCESS_PARAMETERS
    
    {
    
    ULONG MaximumLength;
    
    ULONG Length;
    
    ULONG Flags;
    
    ULONG DebugFlags;
    
    PVOID ConsoleHandle;
    
    ULONG ConsoleFlags;
    
    PVOID StandardInput;
    
    PVOID StandardOutput;
    
    PVOID StandardError;
    
    CURDIR CurrentDirectory;
    
    UNICODE_STRING DllPath;
    
    UNICODE_STRINGImagePathName;
    
    UNICODE_STRING CommandLine;
    
    PVOID Environment;
    
    ULONG StartingX;
    
    ULONG StartingY;
    
    ULONG CountX;
    
    ULONG CountY;
    
    ULONG CountCharsX;
    
    ULONG CountCharsY;
    
    ULONG FillAttribute;
    
    ULONG WindowFlags;
    
    ULONG ShowWindowFlags;
    
    UNICODE_STRING WindowTitle;
    
    UNICODE_STRING DesktopInfo;
    
    UNICODE_STRING ShellInfo;
    
    UNICODE_STRING RuntimeData;
    
    RTL_DRIVE_LETTER_CURDIRCurrentDirectores[32];
    
    ULONG EnvironmentSize;
    
    }; 

可以看到该结构中进程参数相关的各种信息。

3\. 进程Token相关信息的获取

![1537274241_5ba0f18161a94.png!small](https://image.3001.net/images/20180918/1537274241_5ba0f18161a94.png!small)

![1537274254_5ba0f18eb0ef7.png!small](https://image.3001.net/images/20180918/1537274254_5ba0f18eb0ef7.png!small)![1537274259_5ba0f1936a8f2.png!small](https://image.3001.net/images/20180918/1537274259_5ba0f1936a8f2.png!small)![1537274263_5ba0f197c8f74.png!small](https://image.3001.net/images/20180918/1537274263_5ba0f197c8f74.png!small)

都是通过ZwQueryInformationToken函数去获取，只是是使用不同的ClassInformation类去获取，定义如下

    
    
    typedef enum _TOKEN_INFORMATION_CLASS {
    
      TokenUser                             ,
    
      TokenGroups                           ,
    
      TokenPrivileges                       ,
    
      TokenOwner                            ,
    
      TokenPrimaryGroup                     ,
    
      TokenDefaultDacl                      ,
    
      TokenSource                           ,
    
      TokenType                             ,
    
      TokenImpersonationLevel               ,
    
      TokenStatistics                       ,
    
      TokenRestrictedSids                   ,
    
      TokenSessionId                        ,
    
      TokenGroupsAndPrivileges              ,
    
      TokenSessionReference                 ,
    
      TokenSandBoxInert                     ,
    
      TokenAuditPolicy                      ,
    
      TokenOrigin                           ,
    
      TokenElevationType                    ,
    
      TokenLinkedToken                      ,
    
      TokenElevation                        ,
    
      TokenHasRestrictions                  ,
    
      TokenAccessInformation                ,
    
      TokenVirtualizationAllowed            ,
    
      TokenVirtualizationEnabled            ,
    
      TokenIntegrityLevel                   ,
    
      TokenUIAccess                         ,
    
      TokenMandatoryPolicy                  ,
    
      TokenLogonSid                         ,
    
      TokenIsAppContainer                   ,
    
      TokenCapabilities                     ,
    
      TokenAppContainerSid                  ,
    
      TokenAppContainerNumber               ,
    
      TokenUserClaimAttributes              ,
    
      TokenDeviceClaimAttributes            ,
    
     TokenRestrictedUserClaimAttributes   ,
    
     TokenRestrictedDeviceClaimAttributes ,
    
      TokenDeviceGroups                     ,
    
      TokenRestrictedDeviceGroups           ,
    
      TokenSecurityAttributes               ,
    
      TokenIsRestricted                     ,
    
      TokenProcessTrustLevel                ,
    
      TokenPrivateNameSpace                 ,
    
      TokenSingletonAttributes              ,
    
      TokenBnoIsolation                     ,
    
      TokenChildProcessFlags                ,
    
      MaxTokenInfoClass
    
    } TOKEN_INFORMATION_CLASS, *PTOKEN_INFORMATION_CLASS;

需要获取那个就可以选择那一个。

本文大致讲解完毕，内部还有很多很有意思的技术细节由于篇幅原因，读者可以自己深入挖掘，在做一个产品的时候，我们可以分析他人的产品，不仅可以了解他人的产品的长处和不足，同时也可以补充自己产品的不足的之处，一个好的产品就是在不断的琢磨研究与推翻，更重要的是细节的体现才能做好产品。

  

