  

> 写完这个文章我就去干老本行去了,不想再在游戏安全部分下太多功夫
>
> 游戏安全就跟网络安全一样尴尬, **做白的赚钱赚不过黑的.**
>
>  **虽然看着曾经*************************************,自己还在啃方便面.**
> 不过自己还是不会碰那条红线,所以决定转行去干回自己的老本行—— **网络安全了**.也许下一次CIS我就会上去说说我的研究.
>
> 2018-2020年的反作弊手段就这些了,基本上涵盖了目前所有的游戏安全方面问题,直接上吧.
>
> 文中代码有些故意设置了反粘贴.思路不会错的
>
> 本文只考虑驱动情况

## LOGO

![](https://image.3001.net/images/20201123/1606131944_5fbba0e8df7587e96bf24.jpg!small)

## 进程与线程保护

注册obg回调,去掉句柄,防止游戏被打开句柄:

    
    
    NTSTATUS InstallCallBacks()
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
    		OBOperationRegistration[1].PreOperation = MyHandleProcessCallbacks;
    		OBOperationRegistration[1].PostOperation = HandleAfterCreat;
    		OBOperationRegistration[0].ObjectType = PsThreadType;
    		OBOperationRegistration[0].Operations = OB_OPERATION_HANDLE_CREATE | OB_OPERATION_HANDLE_DUPLICATE;
    		OBOperationRegistration[0].PreOperation = MyHandleThreadCallbacks;
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
    			//DebugPrint("[DebugMessage] Failed to install ObRegisterCallbacks: 0x%08X.\n", NtHandleCallback);
    			return STATUS_UNSUCCESSFUL;
    		}
    	}
    	return STATUS_SUCCESS;
    }

  

回调代码如下:

    
    
    OB_PREOP_CALLBACK_STATUS MyHandleProcessCallbacks(PVOID RegistrationContext, POB_PRE_OPERATION_INFORMATION OperationInformation)
    {
    	if (g_StarterPid == (DWORD64)-1)
    		return OB_PREOP_SUCCESS;
    	PEPROCESS OpenedProcess = (PEPROCESS)OperationInformation->Object, CurrentProcess = PsGetCurrentProcess();
    	ULONG ulProcessId = (ULONG)PsGetProcessId(OpenedProcess);
    	ULONG myProcessId = (ULONG)PsGetProcessId(CurrentProcess);
    
    	
    	if ((ulProcessId == (ULONG)g_FlagProcessPid || ulProcessId == (ULONG)g_StarterPid) && myProcessId != ulProcessId)
    	{
    		if (OperationInformation->Operation == OB_OPERATION_HANDLE_CREATE)
    		{
    			if ((OperationInformation->Parameters->CreateHandleInformation.OriginalDesiredAccess & PROCESS_VM_OPERATION) == PROCESS_VM_OPERATION)
    			{
    				//Modify the address space of the process, such as by calling the user-mode WriteProcessMemory and VirtualProtectEx routines.
    				OperationInformation->Parameters->CreateHandleInformation.DesiredAccess &= ~PROCESS_VM_OPERATION;
    			}
    			if ((OperationInformation->Parameters->CreateHandleInformation.OriginalDesiredAccess & PROCESS_VM_READ) == PROCESS_VM_READ)
    			{
    				//Read to the address space of the process, such as by calling the user-mode ReadProcessMemory routine.
    				OperationInformation->Parameters->CreateHandleInformation.DesiredAccess &= ~PROCESS_VM_READ;
    			}
    			if ((OperationInformation->Parameters->CreateHandleInformation.OriginalDesiredAccess & PROCESS_VM_WRITE) == PROCESS_VM_WRITE)
    			{
    				//Write to the address space of the process, such as by calling the user-mode WriteProcessMemory routine.
    				OperationInformation->Parameters->CreateHandleInformation.DesiredAccess &= ~PROCESS_VM_WRITE;
    			}
    		}
    	}
    	return OB_PREOP_SUCCESS;
    }

R3的就打不开进程了.但是可以通过crss.exe、system.exe、steam.exe等打开,所以要有句柄降权

别忘了这个:

    
    
    // 绕过MmVerifyCallbackFunction。
    	PLDR_DATA_TABLE_ENTRY64 ldr = (PLDR_DATA_TABLE_ENTRY64)DriverObject->DriverSection;
    	ldr->Flags |= 0x20;

## 句柄降权

剥夺所有线程与进程的游戏操作权限

    
    
    VOID StripHandlePermission()
    {
    	__try
    	{
    		CheckDebugPort(g_FlagProcessPid);
    		CheckDebugPort((HANDLE)g_StarterPid);
    		PSYSTEM_HANDLE_INFORMATION_EX HandleInfo = QueryHandleTable();
    		if (HandleInfo) {
    			for (int i = 0; i < HandleInfo->NumberOfHandles; i++)
    			{
    				//7 是 process 属性
    				if (HandleInfo->Information[i].ObjectTypeNumber == 7 || HandleInfo->Information[i].ObjectTypeNumber == OB_TYPE_INDEX_PROCESS || HandleInfo->Information[i].ObjectTypeNumber == OB_TYPE_INDEX_THREAD)
    				{
    					if (g_FlagProcessPid == (HANDLE)-1)
    						break;
    					if (HandleInfo->Information[i].ProcessId == (ULONG)g_FlagProcessPid || HandleInfo->Information[i].ProcessId == 4)
    						continue;
    					bool bCheck = ((HandleInfo->Information[i].GrantedAccess & PROCESS_VM_READ) == PROCESS_VM_READ ||
    						(HandleInfo->Information[i].GrantedAccess & PROCESS_VM_OPERATION) == PROCESS_VM_OPERATION ||
    						(HandleInfo->Information[i].GrantedAccess & PROCESS_VM_WRITE) == PROCESS_VM_WRITE);
    					PEPROCESS pEprocess = (PEPROCESS)HandleInfo->Information[i].Object;
    					if (pEprocess) {
    						HANDLE handle_pid = *(PHANDLE)((PUCHAR)pEprocess + g_OsData.UniqueProcessId);
    						HANDLE handle_pid2 = *(PHANDLE)((PUCHAR)pEprocess + g_OsData.InheritedFromUniqueProcessId);
    						if (bCheck && (handle_pid == g_FlagProcessPid || handle_pid2 == g_FlagProcessPid)) {
    							pEprocess = NULL;
    							NTSTATUS status = PsLookupProcessByProcessId((HANDLE)HandleInfo->Information[i].ProcessId, &pEprocess);
    							if (NT_SUCCESS(status)) {
    								//DebugPrint("Full Acess Handle! pid: %d \n", HandleInfo->Information[i].ProcessId);
    								PHANDLE_TABLE HandleTable = *(PHANDLE_TABLE*)((PUCHAR)pEprocess + g_OsData.ObjTable);
    								if (MmIsAddressValid((void*)HandleTable)) {
    									ExEnumHandleTable(HandleTable, g_isWin7 ? (DWORD64*)&StripHandleCallback_win7 : (DWORD64*)&StripHandleCallback_win10, (PVOID)HandleInfo->Information[i].Handle, NULL);
    								}
    								ObDereferenceObject(pEprocess);
    							}
    						}
    					}
    				}
    			}
    			ExFreePoolWithTag(HandleInfo, POOL_TAG);
    		}
    	}
    	__except (EXCEPTION_EXECUTE_HANDLER)
    	{
    		return;
    	}
    	
    }

回调如下,win10和win7的不同:

    
    
    BOOLEAN StripHandleCallback_win10(
    	IN PHANDLE_TABLE HandleTable,
    	IN PHANDLE_TABLE_ENTRY HandleTableEntry,
    	IN HANDLE Handle,
    	IN PVOID EnumParameter
    )
    {
    	BOOLEAN result = FALSE;
    	POBJECT_TYPE ObjectType = NULL;
    	ULONG64 Object = 0;
    	if (g_FlagProcessPid == (HANDLE)-1)
    		return FALSE;
    	if (ExpIsValidObjectEntry(HandleTableEntry))
    	{
    		POBJECT_TYPE ObjectType = NULL;
    		ULONG64 Object = 0;
    		if (Handle == (HANDLE)EnumParameter)
    		{
    			HandleTableEntry->GrantedAccessBits = (SYNCHRONIZE | THREAD_QUERY_LIMITED_INFORMATION);
    			//DebugPrint("Fuck Handle: %08X \n", Handle);
    			goto _exit;
    		}
    		
    	}
    	else {
    		return FALSE;
    	}
    _exit:
    	// Release implicit locks
    	_InterlockedExchangeAdd8((char*)&HandleTableEntry->VolatileLowValue, 1);  // Set Unlocked flag to 1
    	if (HandleTable != NULL && HandleTable->HandleContentionEvent)
    		ExfUnblockPushLock(&HandleTable->HandleContentionEvent, NULL);
    	return FALSE;
    }
    BOOLEAN StripHandleCallback_win7(PHANDLE_TABLE_ENTRY HandleTableEntry, HANDLE Handle, PVOID EnumParameter)
    {
    	POBJECT_TYPE ObjectType = NULL;
    	ULONG64 Object = 0;
    	if (g_FlagProcessPid == (HANDLE)-1)
    		return FALSE;
    	if (ExpIsValidObjectEntry(HandleTableEntry))
    	{
    		if (Handle == (HANDLE)EnumParameter)
    		{
    			HandleTableEntry->GrantedAccessBits = (SYNCHRONIZE | THREAD_QUERY_LIMITED_INFORMATION);
    			//DebugPrint("Fuck Handle: %08X \n", Handle);
    			return FALSE;
    		}
    
    	}
    	return FALSE;
    }

## 随机化进程名字

防止外挂通过进程名字得到pid

    
    
    void randstring(char* randomString, size_t length) {
    
    	static char charset[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    	ULONG seed = KeQueryTimeIncrement();
    	if (randomString)
    	{
    		for (int n = 0; n <= length; n++)
    		{
    			int key = RtlRandomEx(&seed) % (int)(sizeof(charset) - 1);
    			randomString[n] = charset[key];
    		}
    		//randomString[length] = '\0';
    	}
    }
    void FuckName(PUNICODE_STRING v1, WCHAR* ProcessName) {
    	if (v1->Buffer != 0) {
    		RtlZeroMemory(v1->Buffer, v1->MaximumLength);
    		RtlCopyMemory(v1->Buffer, ProcessName, wcslen(ProcessName) * 2);
    		v1->Length = wcslen(ProcessName) * 2;
    	}
    }
    BOOLEAN PathSeAuditProcessCreationInfo(PEPROCESS Process, WCHAR* ProcessName) {
    	PUNICODE_STRING Name;
    	PUNICODE_STRING SelocateName;
    	SeLocateProcessImageName(Process, &SelocateName);
    
    	ExFreePool(SelocateName);
    
    	Name = (PUNICODE_STRING)(*(PULONG_PTR)((ULONG_PTR)Process + g_OsData.SeAuditProcessCreationInfo));//+0x468 SeAuditProcessCreationInfo
    
    	FuckName(Name, ProcessName);
    	return TRUE;
    }
    
    BOOLEAN PatchImageFileName(PEPROCESS Process, char* cName)
    {
    	char    szNameBuff[15] = { 0 };
    	UCHAR* szProcessBuff = NULL;
    	size_t  cNamelen = 0;
    	cNamelen = strlen(cName);
    	RtlZeroMemory(szNameBuff, sizeof(szNameBuff));
    	if (cNamelen > 15)
    		RtlCopyMemory(szNameBuff, cName, sizeof(szNameBuff));
    	else
    		RtlCopyMemory(szNameBuff, cName, cNamelen);
    	szProcessBuff = PsGetProcessImageFileName(Process);
    	RtlZeroMemory(szProcessBuff, sizeof(szNameBuff));
    	RtlCopyMemory(szProcessBuff, szNameBuff, sizeof(szNameBuff));
    	return TRUE;
    }
    void PatchPEB(PEPROCESS Process, WCHAR* ProcessName) {
    	
    	KeAttachProcess((PEPROCESS)Process);
    	DWORD64 _peb = *(PDWORD64)((PUCHAR)Process + g_OsData.peb);
    	DWORD64 peb_ProcessParameters = *(PDWORD64)((ULONG_PTR)_peb + g_OsData.peb_ProcessParameters);
    	PUNICODE_STRING peb_ImagePathName = (PUNICODE_STRING)((ULONG_PTR)peb_ProcessParameters + g_OsData.peb_ImagePathName);
    	PUNICODE_STRING peb_WindowTitle = (PUNICODE_STRING)((ULONG_PTR)peb_ProcessParameters + g_OsData.peb_WindowTitle);
    	
    	PUNICODE_STRING peb_CommandLine = (PUNICODE_STRING)((ULONG_PTR)peb_ProcessParameters + g_OsData.peb_CommandLine);
    	//PUNICODE_STRING peb_DllPath = (PUNICODE_STRING)((ULONG_PTR)peb_ProcessParameters + g_OsData.peb_DllPath);
    	
    	FuckName(peb_ImagePathName, ProcessName);
    	FuckName(peb_WindowTitle, ProcessName);
    	FuckName(peb_CommandLine, ProcessName);
    	KeDetachProcess();
    }
    bool Win10ImageNamePoint(PEPROCESS Process, WCHAR* szFullName)
    {
    	BOOLEAN bRet;
    	PFILE_OBJECT pFileObject;
    	pFileObject = (PFILE_OBJECT)(*(PULONG_PTR)((ULONG_PTR)Process + g_OsData.ImageFilePointer)); //+0x448 ImageFilePointer 
    
    	RtlZeroMemory(pFileObject->FileName.Buffer, pFileObject->FileName.MaximumLength);
    	RtlCopyMemory(pFileObject->FileName.Buffer, szFullName, wcslen(szFullName) * 2);
    	pFileObject->FileName.Length = wcslen(szFullName) * 2;
    
    	return true;
    }
    
    BOOLEAN FuckProcessModify(HANDLE pid)
    {
    	PEPROCESS Process = NULL;
    	NTSTATUS status = PsLookupProcessByProcessId((HANDLE)pid, &Process);
    	if (!NT_SUCCESS(status))
    	{
    		return FALSE;
    	}
    	if (CheckProcessTermination(Process)) {
    		return FALSE;
    	}
    	CHAR temp_char[10] = { 0x0 };
    	randstring(temp_char, 10 - 1);
    	WCHAR temp_wchar[50] = { 0 };
    	status = RtlStringCbPrintfW(temp_wchar, 50, L"%hs", temp_char);
    	if (NT_SUCCESS(status))
    	{
    		PatchImageFileName(Process, temp_char);
    		if (g_isWin7 == false)
    			Win10ImageNamePoint(Process, temp_wchar);
    		PathSeAuditProcessCreationInfo(Process, temp_wchar);
    		PatchPEB(Process, temp_wchar);
    	}
    	ObDereferenceObject(Process);
    	return TRUE;
    }

在createprocessnotifycallbackex使用

## 反调试

检查进程是否被调试,eprocess->debugport,发现调试器直接蓝屏,BE是直接关游戏

    
    
    VOID CheckDebugPort(HANDLE pid) {
    	if (pid == (HANDLE)-1 || pid == (HANDLE)0) {
    		return;
    	}
    	PEPROCESS process;
    	NTSTATUS status = PsLookupProcessByProcessId(g_FlagProcessPid, &process);
    	if (!NT_SUCCESS(status) || process == NULL)
    		return;
    	ObDereferenceObject(process);
    	if (CheckProcessTermination(process)) {
    		return;
    	}
    	if (MmIsAddressValid((PULONG)((PUCHAR)process + g_OsData.ep_debugport))) {
    		ULONG debug_port = *(PULONG)((PUCHAR)process + g_OsData.ep_debugport);
    		if (debug_port != 0) {
    			KeBugCheck(2);
    		}
    	}
    }

## 反回调注入

让ImageLoadCallback无效,防止外挂在游戏启动时注入(注意win7 第一个版本会蓝屏)

    
    
    ULONG64 GetNotifyVarAddress()  
    {  
    if (g_PspNotifyEnableMaskAddr == 0) {  
    ULONG64 i = 0;  
    PULONG64 pAddrOfFnc = 0;  
    UNICODE_STRING fncName;  
    //8B 05 ?? ?? ?? ?? A8 01 75 09 F0 0F BA  
    CHAR pattern_PspNotifyEnableMask[] = "\x8B\x05\xCC\xCC\xCC\xCC\xA8\x01\x75\x09\xF0\x0F\xBA";  
    NTSTATUS status = UtilScanSection(g_KernelBase, "PAGE", (PCUCHAR)pattern_PspNotifyEnableMask, 0xCC, sizeof(pattern_PspNotifyEnableMask) - 1, (PVOID*)&g_PspNotifyEnableMaskAddr);  
    if (!NT_SUCCESS(status))  
    {  
    //DebugPrint("[DebugMessAge] g_PspNotifyEnableMaskAddr not found! :( \n");  
    return 0;  
    }  
    else {  
    //g_PspNotifyEnableMaskAddr = g_PspNotifyEnableMaskAddr + 5;  
    LONG OffsetAddr = 0;  
    memcpy(&OffsetAddr, (UCHAR*)(g_PspNotifyEnableMaskAddr + 2), 4);  
    pAddrOfFnc = (ULONG64*)(OffsetAddr + g_PspNotifyEnableMaskAddr + 0x6);  
    //DebugPrint("[DebugMessAge] g_PspNotifyEnableMaskAddr : %08X  \n", pAddrOfFnc);  
    g_PspNotifyEnableMaskAddr = (ULONG64)pAddrOfFnc;  
    return (ULONG64)g_PspNotifyEnableMaskAddr;  
    }  
    }  
    else {  
    return (ULONG64)g_PspNotifyEnableMaskAddr;  
    }  
    }  
    VOID ChangeNotifyAddress(BOOLEAN enableImage)
    {
    	ULONG64 varaddress = GetNotifyVarAddress();
    	if (varaddress)
    	{
    		//DebugPrint("[DebugMessage] NotifyVarAddress: %08X \n", varaddress);
    		if (MmIsAddressValid((PVOID)*(ULONG*)(varaddress))) {
    			return;
    		}
    		ULONG val = *(ULONG*)(varaddress);
    		/*
    		if (!enableThread)
    		{
    			UNSETBIT(val, 3);
    			UNSETBIT(val, 4);
    		}
    		else
    		{
    			SETBIT(val, 3);
    			SETBIT(val, 4);
    		}
    		*/
    		if (!enableImage)
    		{
    			g_InvalidationLoadImage = true;
    			UNSETBIT(val, 0);
    		}
    		else
    		{
    			g_InvalidationLoadImage = false;
    			SETBIT(val, 0);
    		}
    
    		*(ULONG*)(varaddress) = val;
    	}
    	else {
    		//DebugPrint("[DebugMessage] Can't find NotifyVarAddress \n");
    	}
    }

具体原理百度PspNotifyEnableMask,这个是被PG保护的,所以不能一直关掉.启动后必须马上打开

## Thread stack walk

回溯系统进程,判断是否是外挂线程

    
    
    for (ULONG index = 4; index < 0x30000; index += 4) {
    	PETHREAD ThreadObject;
    	DWORD64 CurrtThreadAddress;
    	if (!NT_SUCCESS(PsLookupThreadByThreadId((HANDLE)index, &ThreadObject)))
    		continue;
    	GetThreadStartAddress(ThreadObject, &CurrtThreadAddress);
    	if (!MmIsAddressValid((PVOID)CurrtThreadAddress))
    		continue;
    	if (!PsIsSystemThread(ThreadObject) || ThreadObject == KeGetCurrentThread()) {
    		if (PsIsSystemThread(ThreadObject) && ThreadObject != KeGetCurrentThread()) {
    			if (CurrtThreadAddress > *(PULONG)DUCK_ANTI_PASTE) {
    				//如果这个地址在kernel speace里面,但是不是系统线程,dump它发到服务端
    				rpc::CallReportByThreadID(index,RESULT_FAKE_SYSTEMTHREAD);
    			}
    		}
    		DWORD64 kthread_apc_state = *(PDWORD64)((ULONG_PTR)ThreadObject + g_OsData.thread_apcstate);
    		if (!MmIsAddressValid((PVOID)kthread_apc_state))
    			continue;
    		PEPROCESS apc_process = (PEPROCESS)((ULONG_PTR)kthread_apc_state + g_OsData.kacp_process);
    		if (!MmIsAddressValid((PVOID)apc_process))
    			continue;
    		if (apc_process) {
    			HANDLE target_id = (HANDLE)PsGetProcessId(apc_process);
    			//DebugPrint("apc_process addr = %p target_id: %p \n", apc_process, target_id);
    			if (target_id == g_FlagProcessPid) {
    				//DebugPrint("detect memeory read at thread addr = %p\n", thrd_id);
    				//APC挂靠,多半是外挂在用MmCopyVirtualMemory,也就是所谓的驱动读写内核
    				rpc::CallReportByThreadID(index,RESULT_APC);
    			}
    		}
    		if (CurrtThreadAddress && (memcmp((void*)start_addr, "\xFF\xE1", 2) == 0) && 
    			(CurrtThreadAddress < g_ntoskrnl_exe_base || CurrtThreadAddress > g_ntoskrnl_exe_base + g_ntoskrnl_exe_len)) {
    			// jmp rcx
    			rpc::CallReportByThreadID(index,RESULT_JMP_RCX);
    		}
    		ThreadStackWalkStruct stack_walk[];
    		GetThreadRip(ThreadObject,stack_walk);
    		if(CheckRipOutSideSystemMoudles(stack_walk)) {
    			rpc::CallReportByThreadID(index,RESULT_OUTSIDE_MOUDLE);
    		}
    		if(stack_walk->chect_jmp == true){
    			//多次跳板
    			rpc::CallReportByThreadID(index,RESULT_CHECT_JMP);
    		}
    		ObDereferenceObject(ThreadObject);
    		continue;
    	}
    }

  

## 虚拟机检测

检测是否存在外挂虚拟机

    
    
    ULONG rdtsc_diff_vmexit() {
    	auto t1 = __rdtsc();
    	int r[4];
    	__cpuid(r, 1);
    	return __rdtsc() - t1;
    }
    bool TimeBaseAttack() {
    	int i;
    	unsigned long long avg = 0;
    	for (i = 0; i < 10; i++) {
    		avg = avg + rdtsc_diff_vmexit();
    		sleep(500);
    	}
    	avg = avg / 10;
    	return (avg < 2100 && avg > 0);
    }
    
    if(TimeBaseAttackNum > 5 && CheckKnownHypervistor() == false){
    	//如果检测到虚拟机但是没有发现正常虚拟机标志
    	//...
    }

## pool内存检测

外挂可以通过有漏洞的驱动加载,检测之

    
    
    void ScanCheatPool()
    {
    	ULONG len = 4 * 1024 * 1024;
    	auto tmpMemory = ExAllocatePoolWithTag(POOL_TYPE::NonPagedPool, len, POOL_TAG);
    	if (NT_SUCCESS(pfn_NtQuerySystemInformation((SYSTEM_INFORMATION_CLASS)0x42, tmpMemory, len, &len))) {
    		auto pBuf = reinterpret_cast<PSYSTEM_BIGPOOL_INFORMATION>(tmpMemory);
    		for (ULONG i = 0; i < pBuf->Count; i++) {
    			bool bCehck1 = CheckBlackTagName(pBuf->AllocatedInfo[i].TagUlong); // 检查名字. 0mVZ SldT rcIC csIC enoN d68x 
    			bool bCheck2 = CheckPoolPeHead(tmpMemory); //检查pe头
    			if (bCehck1 || bCheck2) { //dump给服务端
    				rpc::CallReportByPool(tmpMemory,bCehck1,bCheck2);
    			}
    		}
    	}
    	ExFreePoolWithTag(tmpMemory, POOL_TAG);
    }

## 进程、线程隐藏

抄了老外的,

    
    
    NTSTATUS RemovePspCidTable(PEPROCESS pep, HANDLE pid)
    {
        __try
        {
            void *PspCidTable = *((void **)MAKEPTR(KernelBase, OFS_PspCidTable));
            if (!ExDestroyHandle(PspCidTable, pid, NULL))
            {
                return STATUS_ACCESS_DENIED;
            }
    
            *((ULONG64 *)MAKEPTR(pep, 0x180)) = 0;  // _EPROCESS->UniqueProcessId = 0 (avoid CID_HANDLE_DELETION bsod)
    
            LIST_ENTRY *ThreadListHead = (LIST_ENTRY *)MAKEPTR(pep, 0x308); // _EPROCESS->ThreadListHead
            LIST_ENTRY *pLE = ThreadListHead;
    
            while ((pLE = pLE->Flink) != ThreadListHead)
            {
                PETHREAD pet = (PETHREAD)MAKEPTR(pLE, -0x428);  // _ETHREAD->ThreadListEntry offset
                HANDLE tid = PsGetThreadId(pet);
                HANDLE tpid = PsGetThreadProcessId(pet);
                DbgPrint("pid: %I64x, tid: %I64x, tpid: %I64x", pid, tid, tpid);
    
                if (pid == tpid)    // just making sure..
                {
                    DbgPrint("Removing thread: %I64x (tid: %I64x)", pet, tid);
                    if (!ExDestroyHandle(PspCidTable, tid, NULL))
                    {
                        return STATUS_ACCESS_DENIED;
                    }
    
                    //*((ULONG64 *)MAKEPTR(pet, 0x3b8 + 0x00)) = 0; // _ETHREAD->Cid.UniqueProcess = 0
                    *((ULONG64 *)MAKEPTR(pet, 0x3b8 + 0x08)) = 0;   // _ETHREAD->Cid.UniqueThread = 0 (avoid CID_HANDLE_DELETION bsod)
                }
            }
        }
        __except (EXCEPTION_EXECUTE_HANDLER)
        {
            return STATUS_ACCESS_DENIED;
        }
    
        return STATUS_SUCCESS;
    }

## 其他

请自己谷歌,不方便透露:

> minifilter反dll注入
>
> createthreadnotifycallback回溯线程
>
> Driver Dispatch Hijack检测
>
> PhysicalMemory检测
>
> 反作弊自我保护
>
> PG状态检测
>
> VAD->enclave 防代码段修改

 **要是多年后你是通过这篇文章启蒙的,请务必私信我**

