## 前言

功能：一个源程序加壳与解壳的过程。

原理：

> 加壳过程，即在壳文件上加一个新节（加密后的源程序）。
>
> 解壳过程，即在加密壳的进程空间中，为解密后的源程序分配空间，再卸载壳程序将控制权交给源程序。

备注：

> 这里假设读者已经对PE文件的结构有所了解，所以对PE文件的操作不再赘述。
>
> 壳和源程序其实都是独立的程序，加载到内存执行都会有自己的4GB空间。

欢迎大佬指正，新人共勉！

## 符号说明：

> src.exe 没有加壳的源程序
>
> shell.exe 壳程序
>
> shell.exe.encrypt.exe 加密壳程序
>
> OEP 程序入口点

## 实现环境

> win10，VC++6.0

## 加壳过程

加壳过程很简单，处理好新增的节基本就没啥问题了。步骤如下：

> 1、获取 shell.exe 的路径
>
> 2、获取 src.exe 的路径
>
> 3、将 src.exe 程序读取到内存中，加密
>
> 4、在 shell.exe 程序中新增一个节，并在新节中加入 加密后的src.exe 。

加壳过程如图：

![](https://image.3001.net/images/20200427/1587963163_5ea6651b11918.png!small)

## 解壳过程

1、获取 shell.exe.encrypt.exe 的路径

2、在shell.exe.encrypt.exe 中获取 src.exe 的数据

> （0）定位到shell.exe.encrypt.exe的最后一个节
>
> （1）取出最后一个节的数据，解密

3、拉伸解密后的PE文件，存储到缓冲区

PE文件有两种状态：磁盘中的文件映像、内存中拉伸的状态

为什么会有两种状态呢？ 首先得知道PE文件的执行过程：

当一个PE文件被执行时，PE装载器首先根据PE header的偏移量，跳转到PE header的位置。

当PE装载器跳转到PE header后，检查PE header是否有效。如果该PE header有效，就跳转到PE header的尾部。

接着是PE header尾部的节表，PE 装载器开始读取节表中的信息，并采用文件映射方法将这些节段映射到内存。

PE文件映射入内存后，PE装载器将继续处理PE文件中其他的目录表。

如上可知，PE文件执行的过程中，有一个从文件映射到内存的过程，所以就有PE的两种状态。

我们要做的是模仿PE加载器，让PE文件执行起来，所以就需要在内存中做拉伸。

4、以挂起方式运行shell.exe.encrypt.exe 进程

挂起主线程，是为了创建一个子线程来修改主线程的运行环境（CONTEXT），修改的运行环境为 shell.exe的运行环境。

（0）以挂起的方式创建shell.exe.encrypt.exe 进程，并得到主线程的 CONTEXT

（1）卸载外壳程序的文件镜像

如果shell.exe和 shell.exe.encrypt.exe
进程有相同基址，并且shell.exe的内存镜像小于进程shell.exe.encrypt.exe 的内存镜像，

那么只需要调用WriteProcessMemory来把可执行程序shell.exe的镜像写到进程shell.exe.encrypt.exe的内存空间中，并从
基址 开始执行即可。

否则，需要调用ZwUnmapViewOfSection来取消shell.exe.encrypt.exe的映像映射，然后通过 VirtualAllocEx
在shell.exe.encrypt.exe 进程中为

可执行程序 shell.exe 分配足够的空间。调用VirtualAllocEx的时候，必须提供可执行程序 shell.exe 的
基址，用来分配从指定位置开始的的空间。

然后把可执行程序 shell.exe 的镜像复制到进程 shell.exe.encrypt.exe 的内存空间，并从分配的空间的起始地址开始执行。

（2）在指定的位置申请指定大小的内存

指定的位置：src.exe 的 基址

指定大小：src.exe 的 SizeOfImage

内存分配：VirtualAllocEx

CONTEXT对象的ebx寄存器指向进程的PEB，eax寄存器的值为进程的OEP，ebx+8 为进程的基址。

（3）如果申请内存失败，查看 src.exe 是否有重定位表的数据，如果有，就在任意位置申请指定大小的内存，然后修复重定位表。 指定大小：src.exe 的
SizeOfImage

（4）如果申请内存失败，并且没有重定位表的数据，返回失败

如果指定位置的内存申请失败，说明该位置已经被占用，如果这时候要让程序在别的位置也能够正常运行，就依赖于重定位表，如果没有重定位表，那么程序就无法正常执行了。

（5）如果内存申请成功，复制PE数据到shell的进程空间中

（6）修正运行环境的ImageBase和OEP

5、恢复执行主进程，解壳完成。

解壳过程如图：

![](https://image.3001.net/images/20200427/1587963173_5ea66525d9b55.png!small)

备注：这里的难点在于理解 挂起创建进程 的过程，在挂起的过程中 涉及到的两个重点函数ZwUnmapViewOfSection VirtualAllocEx
也比较难理解，需要了解操作系统的内存机制。

[(CreateProcessA)创建一个新的进程，新进程在调用进程的安全上下文中运行。](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessa)

    
    
    BOOL CreateProcessA(  
      LPCSTR                lpApplicationName, //执行的模块名，可为null  
      LPSTR                 lpCommandLine, //要执行的命令行，可为null  
      LPSECURITY_ATTRIBUTES lpProcessAttributes, //该指针决定子进程是否可以继承新进程对象的返回句柄,如果为空，则不能继承句柄。  
      LPSECURITY_ATTRIBUTES lpThreadAttributes,//该指针决定子线程是否可以继承新进程对象的返回句柄,如果为空，则不能继承句柄。  
      BOOL                  bInheritHandles, //处理每个可继承句柄是否被新进程继承的选项，true表示可继承，否表示不可继承  
      DWORD                 dwCreationFlags, //控制优先级类和流程创建的标志。  
      LPVOID                lpEnvironment,   //指向新进程的环境块的指针。  
      LPCSTR                lpCurrentDirectory, //进程当前目录的完整路径。  
      LPSTARTUPINFOA        lpStartupInfo, //启动信息  
      LPPROCESS_INFORMATION lpProcessInformation //进程信息  
    );

[(ZwUnmapViewOfSection)卸载内存中的文件映射](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-zwunmapviewofsection)

    
    
      
    NTSYSAPI NTSTATUS ZwUnmapViewOfSection(  
      HANDLE ProcessHandle, //要取消映射的进程句柄  
      PVOID BaseAddress //从虚拟地址空间此处开始取消映射  
    );

[（VirtualAllocEx分配最佳内存）](https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualallocex)  

    
    
    LPVOID VirtualAllocEx(  
      HANDLE hProcess, //在此进程空间内分配内存  
      LPVOID lpAddress, //为要分配的页区域指定所需的起始地址的指针  
      SIZE_T dwSize,   //分配的内存大小  
      DWORD  flAllocationType, //分配的内存页的大小  
      DWORD  flProtect //要分配的页区域的内存保护  
    );

## 几点思考

1、以前只会用工具，死记步骤，现在除了用工具，还可以写简单的工具(hai shi yong gong ju)（~~o(>_<)o ~~）。

2、更重要的收获是，从哪些大佬的写的工具当中汲取一点智慧。

3、以前老师逼着学都学不下去的操作系统，现在居然饶有兴趣地看了Over And Over Again (but, yi ran shi xiao cai)。

4、程序加壳是为了保护程序，那么这种"保护"是不是也可以成为恶意软件的”护身符“，绕过杀软的扫描？后续会带着这些思考继续学习逆向工程。

## 主要代码实现

代码中都有详细的备注，由于篇幅有限，没有贴上全部的代码。

### 1、AES加壳

    
    
    #include "stdafx.h"
    #include<stdio.h>
    #include<stdlib.h>
    #include<time.h>
    
    #include "AES.h"
    #include "PEOperate.h"
    
    /* AES 加密*/
    BOOL Packer()
    {
    
    	TCHAR* shellPath = "shell.exe";
    	TCHAR* srcPath = "src.exe";
    
    	DWORD SrcFileSize=0;
    	LPVOID pSrcFileBuffer = LoadPEFile(srcPath,SrcFileSize);
    	CHAR* pOld = (CHAR*)pSrcFileBuffer;
    
    	//循环加密
    	//DWORD fileSize = 0;	
    	LPVOID pSrcFileBufferEncode = malloc(SrcFileSize);
    	memset(pSrcFileBufferEncode,SrcFileSize,0);
    	CHAR* pNew = (CHAR*)pSrcFileBufferEncode;
    
    	//void TestAddSecToFile(LPSTR lpszFile)
    	//数据加密
    
    	unsigned char key[] =
    	{
    		0x2b, 0x7e, 0x15, 0x16,
    		0x28, 0xae, 0xd2, 0xa6,
    		0xab, 0xf7, 0x15, 0x88,
    		0x09, 0xcf, 0x4f, 0x3c
    	};
    	AES aes(key);
    	aes.Cipher(pSrcFileBuffer, SrcFileSize);
    	pSrcFileBufferEncode = pSrcFileBuffer;
    	/*
    	将加密代码加入到文件内部
    	shellPath 源壳文件
    	pSrcFileBufferEncode  源程序加密后的文件
    	SrcFileSize 加密文件的长度，由于这里使用的加密算法(AES)只是异或和移位循环，所以源文件和加密文件的长度都是一样的
    	*/
    	AddSecToFile(shellPath,pSrcFileBufferEncode,SrcFileSize);
    
    	return TRUE;
    }
    
    /* 异或加密
    BOOL Packer()
    {
    
    	TCHAR* shellPath = "shell.exe";
    	TCHAR* srcPath = "src.exe";
    
    	DWORD SrcFileSize=0;
    	LPVOID pSrcFileBuffer = LoadPEFile(srcPath,SrcFileSize);
    	CHAR* pOld = (CHAR*)pSrcFileBuffer;
    
    	//循环加密
    	//DWORD fileSize = 0;	
    	LPVOID pSrcFileBufferEncode = malloc(SrcFileSize);
    	memset(pSrcFileBufferEncode,SrcFileSize,0);
    	CHAR* pNew = (CHAR*)pSrcFileBufferEncode;
    
    	//void TestAddSecToFile(LPSTR lpszFile)
    	//数据加密
    	for(int i=0;i<(int)SrcFileSize;i++)
    	{
    		pNew[i] = pOld[i]^KEY;	
    	}
    	
    
    	//将加密代码加入到文件内部
    	//shellPath 源壳文件
    	//pSrcFileBufferEncode  源程序加密后的文件
    	//SrcFileSize 加密文件的长度，由于这里使用的加密算法(AES)只是异或和移位循环，所以源文件和加密文件的长度都是一样的
    	
    	AddSecToFile(shellPath,pSrcFileBufferEncode,SrcFileSize);
    
    	return TRUE;
    }
    */
    
    #ifndef DEBUG //测试
    void main()
    {
    	Packer();
    }
    #endif  
    

### 2、AES解壳

    
    
    #include "stdafx.h"
    #include<stdio.h>
    #include<stdlib.h>
    #include<time.h>
    
    #include "AES.h"
    #include "PEOperate.h"
    
    			
    // 重定向PE用到的地址  
    void DoRelocation(LPVOID pFileBuffer, void *OldBase, void *NewBase) 
    { 
    	PIMAGE_DOS_HEADER pDosHeader = NULL;
    	pDosHeader = (PIMAGE_DOS_HEADER)pFileBuffer;	
    	PIMAGE_NT_HEADERS peH = (PIMAGE_NT_HEADERS)((DWORD)pFileBuffer+pDosHeader->e_lfanew);
    	
        unsigned long Delta = (unsigned long)NewBase - peH->OptionalHeader.ImageBase;  
        PImageBaseRelocation p = (PImageBaseRelocation)((unsigned long)OldBase   
            + peH->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].VirtualAddress);  
        while(p->VirtualAddress + p->SizeOfBlock)  
        {  
            unsigned short *pw = (unsigned short *)((int)p + sizeof(*p));  
            for(unsigned int i=1; i <= (p->SizeOfBlock - sizeof(*p)) / 2; ++i)  
            {  
                if((*pw) & 0xF000 == 0x3000){  
                    unsigned long *t = (unsigned long *)((unsigned long)(OldBase) + p->VirtualAddress + ((*pw) & 0x0FFF));  
                    *t += Delta;  
                }  
                ++pw;  
            }  
            p = (PImageBaseRelocation)pw;  
        }  
    }  
    
    VOID GetEncryptFileContext(LPVOID pFileBuffer,DWORD &OEP,DWORD &ImageBase)
    {
    	PIMAGE_DOS_HEADER pDosHeader = NULL;
    	PIMAGE_NT_HEADERS pNTHeader = NULL;
    	PIMAGE_FILE_HEADER pPEHeader = NULL;
    	PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;
    	PIMAGE_SECTION_HEADER pSectionHeader = NULL;
    	//pFileBuffer= ReadPEFile(lpszFile);
    	
    	if(!pFileBuffer)
    	{
    		printf("文件读取失败\n");
    		return;
    	}
    	
    	//MZ标志
    	if(*((PWORD)pFileBuffer)!=IMAGE_DOS_SIGNATURE)
    	{
    		printf("不是有效的MZ标志\n");
    		free(pFileBuffer);
    		return;
    	}
    	//DOS头
    	pDosHeader = (PIMAGE_DOS_HEADER)pFileBuffer;
    
    	//判断是否是有效的PE 
    	if(*((PDWORD)((DWORD)pFileBuffer+pDosHeader->e_lfanew))!=IMAGE_NT_SIGNATURE)
    	{
    		printf("不是有效的PE标志\n");
    		free(pFileBuffer);
    		return;
    	}
    	
    	pNTHeader = (PIMAGE_NT_HEADERS)((DWORD)pFileBuffer+pDosHeader->e_lfanew);
    	
    	//PE头
    	pPEHeader = (PIMAGE_FILE_HEADER)(((DWORD)pNTHeader)+4);
    	
    	//可选择PE头
    	pOptionHeader = (PIMAGE_OPTIONAL_HEADER32)((DWORD)pPEHeader+IMAGE_SIZEOF_FILE_HEADER);
    
    	//获取信息
    	OEP = pOptionHeader->AddressOfEntryPoint;
    	ImageBase = pOptionHeader->ImageBase;
    
    }
    
    VOID GetNtHeaderInfo(LPVOID pFileBuffer,DWORD &ImageBase,DWORD &ImageSize)
    {
    	PIMAGE_DOS_HEADER pDosHeader = NULL;
    	PIMAGE_NT_HEADERS pNTHeader = NULL;
    	PIMAGE_FILE_HEADER pPEHeader = NULL;
    	PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;
    	PIMAGE_SECTION_HEADER pSectionHeader = NULL;
    
    	if(!pFileBuffer)
    	{
    		printf("文件读取失败\n");
    		return;
    	}
    	
    	//MZ标志
    	if(*((PWORD)pFileBuffer)!=IMAGE_DOS_SIGNATURE)
    	{
    		printf("不是有效的MZ标志\n");
    		free(pFileBuffer);
    		return;
    	}
    		
    	//DOS头
    	pDosHeader = (PIMAGE_DOS_HEADER)pFileBuffer;
    
    	//判断是否是有效的PE 
    	if(*((PDWORD)((DWORD)pFileBuffer+pDosHeader->e_lfanew))!=IMAGE_NT_SIGNATURE)
    	{
    		printf("不是有效的PE标志\n");
    		free(pFileBuffer);
    		return;
    	}
    
    	pNTHeader = (PIMAGE_NT_HEADERS)((DWORD)pFileBuffer+pDosHeader->e_lfanew);
    
    	//NT头
    	pPEHeader = (PIMAGE_FILE_HEADER)(((DWORD)pNTHeader)+4);
    
    	//可选择PE头
    	pOptionHeader = (PIMAGE_OPTIONAL_HEADER32)((DWORD)pPEHeader+IMAGE_SIZEOF_FILE_HEADER);
    
    
    	//获取信息
    	ImageBase = pOptionHeader->ImageBase;
    	ImageSize = pOptionHeader->SizeOfImage;
    	
    }
    
    
    //是否有重定位表
    BOOL HasRelocationTable(LPVOID pFileBuffer)  
    {  
    
    	PIMAGE_DOS_HEADER pDosHeader = NULL;
    	PIMAGE_NT_HEADERS pNTHeader = NULL;
    	PIMAGE_FILE_HEADER pPEHeader = NULL;
    	PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;
    	PIMAGE_SECTION_HEADER pSectionHeader = NULL;
    	PIMAGE_DATA_DIRECTORY DataDirectory=NULL;
    	
    	//Header信息
    	pDosHeader = (PIMAGE_DOS_HEADER)pFileBuffer;
    	pNTHeader = (PIMAGE_NT_HEADERS)((DWORD)pFileBuffer+pDosHeader->e_lfanew);
    	pPEHeader = (PIMAGE_FILE_HEADER)(((DWORD)pNTHeader)+4);
    	pOptionHeader = (PIMAGE_OPTIONAL_HEADER32)((DWORD)pPEHeader+IMAGE_SIZEOF_FILE_HEADER);
    	pSectionHeader = (PIMAGE_SECTION_HEADER)((DWORD)pOptionHeader+pPEHeader->SizeOfOptionalHeader);
    
    	//定位Directory_Data;
    	DataDirectory = pOptionHeader->DataDirectory;
    	
        return (DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].VirtualAddress)  
            && (DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].Size);  
    }  
    
    /*
    在指定位置分配空间
    
    shellDirectory : 原始壳的地址
    shellProcess : 加密壳的进程句柄
    encryptFileBuffer :加密壳程序的FileBuffer
    位置： Src的ImageBase
    大小:  Src的SizeOfImage
    */
    LPVOID AllocShellSize(LPSTR shellDirectory,HANDLE shellProcess,LPVOID encryptFileBuffer)
    {
    	typedef void *(__stdcall *pfVirtualAllocEx)(unsigned long, void *, unsigned long, unsigned long, unsigned long);  
    	pfVirtualAllocEx MyVirtualAllocEx = NULL;  
    	MyVirtualAllocEx = (pfVirtualAllocEx)GetProcAddress(GetModuleHandle("Kernel32.dll"), "VirtualAllocEx"); //获取VirtualAllocEx 函数地址
    	
    	LPVOID pShellBuffer = ReadPEFile(shellDirectory);
    
    	DWORD shellImageBase=0;
    	DWORD shellImageSize=0;
    	DWORD encryptImageBase=0;
    	DWORD encryptImageSize=0;
    
    	//获得ImageBase ImageSize， 进行信息比较
    	GetNtHeaderInfo(pShellBuffer,shellImageBase,shellImageSize);
    	GetNtHeaderInfo(encryptFileBuffer,encryptImageBase,encryptImageSize);
    
    	if(shellImageBase == 0 || shellImageSize==0 || encryptImageBase == 0 || encryptImageSize==0)
    	{
    		MessageBox(0,"申请空间失败","失败",0);
    		return NULL;
    	}
    
    	void *p = NULL;  
    
    	//在指定进程的指定位置分配内存
    	/*
    		VirtualAllocEx：在指定进程的虚拟空间保留或提交内存区域，除非指定MEM_RESET参数，否则将该内存区域置0。
    		LPVOID VirtualAllocEx(
    		HANDLE hProcess, // 申请内存所在的进程句柄
    		LPVOID lpAddress, // 保留页面的内存地址；一般用NULL自动分配
    		SIZE_T dwSize, // 欲分配的内存大小，字节单位；注意实际分 配的内存大小是页内存大小的整数倍
    		DWORD flAllocationType,
    		DWORD flProtect
        */
    	//如果指定位置内存没有被占用，则取 MAX(shellImageSize,encryptImageSize)
    	if(shellImageBase == encryptImageBase )
    	{
    		shellImageSize = (shellImageSize >= encryptImageSize) ? shellImageSize: encryptImageSize;
    		// 最小的分配方式，具体用法查MSDN，分配失败会返回NULL
    		p = VirtualAllocEx(shellProcess,(void*)shellImageBase,shellImageSize,MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    	}
    	
    	// 指定位置被占用 & 进程中有重定位表
    	if((p == NULL) && HasRelocationTable(encryptFileBuffer)){  
    		//任意位置分配空间
    		p = VirtualAllocEx(shellProcess, NULL, encryptImageSize, MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE); 
    	    
    		//重定位处理
    		if(p) {
    			DoRelocation(encryptFileBuffer, (void*)encryptImageBase, p);
    		}else{
    			
    			MessageBox(0,"申请空间失败3","失败3",0);
    			return NULL;
    		}
        }
    
    	return p;
    }
    
    /*
     卸载(释放)原外壳占用内存
     ProcHnd: 卸载的进程句柄
     BaseAddr: 卸载的基址
     返回：TRUE 卸载成功
           FALSE 卸载失败
    */
    BOOL UnloadShell(HANDLE ProcHnd, unsigned long BaseAddr)  
    {  
        typedef unsigned long (__stdcall *pfZwUnmapViewOfSection)(unsigned long, unsigned long);  
        pfZwUnmapViewOfSection ZwUnmapViewOfSection = NULL;  
        BOOL res = FALSE;  
        HMODULE m = LoadLibrary("ntdll.dll");  
        if(m){  
    		ZwUnmapViewOfSection = (pfZwUnmapViewOfSection)GetProcAddress(m, "ZwUnmapViewOfSection"); 
    
    		if(ZwUnmapViewOfSection)  
    			res = (ZwUnmapViewOfSection((unsigned long)ProcHnd, BaseAddr) == 0);  //取消映射目标进程的内存
    		FreeLibrary(m);  
        }  
        return res;  
    }  
    
    
    LPVOID GetLastSecData(LPSTR lpszFile,DWORD &fileSize)
    {
    
    	LPVOID pFileBuffer = NULL;
    	pFileBuffer= ReadPEFile(lpszFile);
    	if(!pFileBuffer)
    	{
    		printf("文件读取失败\n");
    		return NULL;
    	}
    
    
    	PIMAGE_DOS_HEADER pDosHeader = NULL;
    	PIMAGE_NT_HEADERS pNTHeader = NULL;
    	PIMAGE_FILE_HEADER pPEHeader = NULL;
    	PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;
    	PIMAGE_SECTION_HEADER pSectionHeader = NULL;
    	PIMAGE_SECTION_HEADER pSectionHeader_LAST = NULL;
    
    	//Header信息
    	pDosHeader = (PIMAGE_DOS_HEADER)pFileBuffer;
    	pNTHeader = (PIMAGE_NT_HEADERS)((DWORD)pFileBuffer+pDosHeader->e_lfanew);
    	pPEHeader = (PIMAGE_FILE_HEADER)(((DWORD)pNTHeader)+4);
    	pOptionHeader = (PIMAGE_OPTIONAL_HEADER32)((DWORD)pPEHeader+IMAGE_SIZEOF_FILE_HEADER);
    	pSectionHeader = (PIMAGE_SECTION_HEADER)((DWORD)pOptionHeader+pPEHeader->SizeOfOptionalHeader);
    	pSectionHeader_LAST = (PIMAGE_SECTION_HEADER)((DWORD)pSectionHeader+(pPEHeader->NumberOfSections-1)*40);
    
    	int fileLength = pSectionHeader_LAST->PointerToRawData+pSectionHeader_LAST->SizeOfRawData;
    	
    	//判断是否已经加壳
    	if(strcmp((char*)pSectionHeader_LAST->Name,".NewSec")!=0)
    	{
    		MessageBox(0,"没有加壳","错误",0);
    		return NULL;
    	}
    	
    	fileSize = pSectionHeader_LAST->SizeOfRawData;
    	LPVOID pEncryptBuffer = malloc(fileSize);
    	memset(pEncryptBuffer,0,fileSize);
    	CHAR* pNew = (CHAR*)pEncryptBuffer;
    
    	CHAR* pOld = (CHAR*)((DWORD)pFileBuffer+pSectionHeader_LAST->PointerToRawData);
    
    	//将最后一个段的数据拷贝到pEncryptBuffer中,并解密
    	unsigned char key[] =
    	{
    		0x2b, 0x7e, 0x15, 0x16,
    		0x28, 0xae, 0xd2, 0xa6,
    		0xab, 0xf7, 0x15, 0x88,
    		0x09, 0xcf, 0x4f, 0x3c
    	};
    	AES aes(key);
    	aes.InvCipher(pOld, fileSize);
    	pEncryptBuffer = pOld;
    	
    	return pEncryptBuffer;
    }
    
    #ifdef DEBUG
    int main()
    {
    
    	char* shellDirectory = "shell.exe.encrypt1.exe"; //这是加壳后的程序
    	DWORD encryptSize = 0;
    
    	LPVOID encryptFileBuffer = NULL;
    	encryptFileBuffer = GetLastSecData(shellDirectory,encryptSize);
    	
    	//失败则结束
    	if(encryptFileBuffer == NULL)
    	{
    		MessageBox(0,"解密失败","失败",0);
    		return 0;
    	}
    	
    	/*
    	以挂起的形式创建进程
    	创建子进程，并且需要在子进程初始化之前修改运行环境（修改壳程序的运行环境-->子进程的运行环境）
    	*/
    	STARTUPINFO si={0};
    	si.cb = sizeof(STARTUPINFO);
    	PROCESS_INFORMATION pi;
    	CreateProcessA(shellDirectory,
    		NULL,
    		NULL,
    		NULL,
    		FALSE,
    		CREATE_SUSPENDED,
    		NULL,
    		NULL,
    		&si,π);
    	
    	TCHAR szTempStr[256]={0};
    	
    	sprintf(szTempStr,"进程消息： %x , %x \n",pi.hProcess,pi.hThread);
    	CONTEXT contx;  //外壳的上下文环境
    	contx.ContextFlags = CONTEXT_FULL;
    	GetThreadContext(pi.hThread,&contx);
    	DWORD shellOEP = contx.Eax; //OEP的值存在EAX寄存器中
    	
    	char* baseAddress = (CHAR*)contx.Ebx+8;//获取IMAGE_BASE的信息
    	TCHAR szBuffer[4]={0};
    	ReadProcessMemory(pi.hProcess,baseAddress,szBuffer,4,NULL);
    	int* fileImageBase;
    	fileImageBase = (int*)szBuffer;
    	DWORD shellImageBase  = *fileImageBase;
    
    	BOOL isUnload = UnloadShell(pi.hProcess,shellImageBase);//卸载外壳程序内存
    
    	LPVOID p = AllocShellSize(shellDirectory,pi.hProcess,encryptFileBuffer);//在外壳进程空间的指定位置分配内存
    	if(p == NULL)
    	{
    		MessageBox(0,"内存分配失败","错误",0);
    		return 0;
    	}
    	
    
    	DWORD pEncryptImageSize=0;
    	LPVOID pEncryptImageBuffer = FileBufferToImageBuffer(encryptFileBuffer,pEncryptImageSize);//将加密的源程序数据拷贝到新分配的内存空间
    	
    	unsigned long old;
    	WriteProcessMemory(pi.hProcess, (void *)(contx.Ebx+8), &p, sizeof(DWORD), &old); 
    
    	if(WriteProcessMemory(pi.hProcess, p, pEncryptImageBuffer, pEncryptImageSize, &old))
    	{// 复制PE数据到shell的进程空间中  
    
    		DWORD encryptFileOEP = 0;
    		DWORD encryptFileImageBase = 0;
    				
    		GetEncryptFileContext(encryptFileBuffer,encryptFileOEP,encryptFileImageBase);
    
            contx.ContextFlags = CONTEXT_FULL; 
    				
    		//修复入口地址为源程序的入口
    		contx.Eax = encryptFileOEP + (DWORD)p;
            SetThreadContext(pi.hThread, &contx);// 更新主进程的运行环境为源程序的运行环境
    	
    		LPVOID szBufferTemp = malloc(pEncryptImageSize);
    		memset(szBufferTemp,0,pEncryptImageSize);
    		ReadProcessMemory(pi.hProcess,p,szBufferTemp,pEncryptImageSize,NULL);
    		
    		//////这个是测试用的 实际壳程序将加密文件解密后直接跳转到源程序的入口执行：脱壳后程序保存到文件////////
    		MemeryTOFile(szBufferTemp,"111111.exe");
    		///////////////////////////////////////////////////////////////////////////////////////////////////////
    
            ResumeThread(pi.hThread);// 恢复执行主线程  
            CloseHandle(pi.hThread);  
         } 
    	return 0;
    }
    #endif
    

## 参考资料

> 《加密与解密（第4版）》
>
> 《WINDOWS内核原理与实现》
>
> 《应用密码学：协议、算法与C源程序》

 ***本文作者：m0h1e0，转载请注明来自FreeBuf.COM**

