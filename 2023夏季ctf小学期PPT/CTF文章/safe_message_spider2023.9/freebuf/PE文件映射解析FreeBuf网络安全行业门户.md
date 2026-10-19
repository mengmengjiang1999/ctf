# 一. 映射基础

### 1.1 文件结构

在了解 PE 文件的内存映射之前，需要先了解 PE 文件的结构特征。针对 PE 文件结构部分的内容，可以参考我之前发过的文章[《 PE
文件结构解析》](https://coonaa.cn/index.php/archives/184/)。

### 1.2 结构成员

PE 文件的 _IMAGE_OPTIONAL_HEADER 结构中存在两个非常重要的结构成员：SectionAlignment 和
FileAlignment 。

 **SectionAlignment** ：内存对齐粒度，即 PE 文件映射到内存时的对齐粒度；默认值为系统页面大小 0x1000
B（4KB）；该值必须大于或等于 FileAligment 的值。

 **FileAlignment** ：磁盘对齐粒度，即 PE 文件在磁盘中存储时的对齐粒度；默认值为磁盘页面大小 0x200 B（512B）；如果
SectionAlignment 的值小于系统页面大小，则该值必须与 SectionAlignment 的值相同。

### 1.3 地址偏移

PE 文件中几个重要地址的基本概念：

 **VA** （Virtual Address）：虚拟地址  
PE 文件映射到内存空间时，数据在内存空间中对应的地址。

 **ImageBase** ：映射基址  
PE 文件在内存空间中的映射起始位置，是个 VA 地址。

 **RVA** （Relative Virtual Address）：相对虚拟地址  
PE 文件在内存中的 VA 相对于 ImageBase 的偏移量。

 **FA** （File Offset Address，FOA）：文件偏移地址  
PE 文件在磁盘上存放时，数据相对于文件开头位置的偏移量，文件偏移地址等于文件地址。

### 1.4 映射方式

PE 文件在执行的时候，映射到内存中的结构布局与该文件在磁盘中存储时的结构布局是一致的。  
Windows 装载器（又称 PE 装载器）在载入一个 PE 文件时，把磁盘中的 PE
文件映射到进程的内存地址空间，是一种从磁盘偏移地址到内存偏移地址的转换。

从 “头部” 和 “区块” 两部分进行 PE 文件的大小和映射分析：

 **（1）头部**  
DOS Header 部分的大小一般固定为 0x40 字节；  
DOS Stub 部分的大小可能随文件的不同而不同；  
PE Header 部分的大小一般固定为 0xF8 字节；  
Section Table 部分的大小可能随具体区块的数目不同而不同。

一般而言，整个 PE 文件头部的大小固定为 0x400 字节，不足 0x400 字节的部分用 0 填充。

DOS 首部的起始位置，即 FA = 0 的位置，映射到内存地址空间后所对应的地址即为 ImageBase ，同时该位置 RVA = 0 。  
从 FA = 0 的位置开始，将整个 PE 文件头部以类似于 “复制” 的形式，映射到以 ImageBase 为起始位置的内存地址空间中。

 **（2）区块**  
PE 文件中的区块数目不固定，同时每个区块的大小也不固定，这取决于 PE 文件的实际需要。  
但每个区块在磁盘中的大小都应该是 FileAlignment 值的整数倍，在内存地址空间中的大小都应该是 SectionAlignment
值的整数倍，不足的部分用 0 填充。

由于整个 PE 文件头部的大小固定为 0x400 字节，因此 PE 文件中第一个区块的起始位置为 FA = 0x400 ，映射后 RVA = 0x1000
。

从第二个区块开始，每个区块映射后的起始位置为 RVA = 0x1000 + 0x1000 * N 。其中 N 为正整数，其值由区块的实际大小决定。

  
一个简单的 PE 文件内存映射对齐关系，用图表示如下：  
![PE文件内存映射对齐](https://image.3001.net/images/20210913/1631527301_613f2185c345e5fa27d36.png!small)  
  

# 二. 映射实现

### 2.1 重点函数

内存文件映射的一般方法（三大函数步骤）：  
**CreateFile()**函数：创建文件内核对象，获得文件内核对象句柄；  
**CreateFileMapping()**函数：创建文件映射对象，获得文件映射对象句柄；  
**MapViewOfFile()**函数：将文件映射对象映射到进程地址空间，获得映射基址。

 **2.1.1 CreateFileA function**

 **函数定义** （该函数定义于 fileapi.h 头文件）：

    
    
    HANDLE CreateFileA(
      LPCSTR                lpFileName,
      DWORD                 dwDesiredAccess,
      DWORD                 dwShareMode,
      LPSECURITY_ATTRIBUTES lpSecurityAttributes,
      DWORD                 dwCreationDisposition,
      DWORD                 dwFlagsAndAttributes,
      HANDLE                hTemplateFile
    );
    

**函数参数** ：  
（1）lpFileName：要创建或打开的文件或设备的名称。  
（2）dwDesiredAccess：要对文件或设备使用的访问权限。部分取值：

> GENERIC_READ：可读  
> GENERIC_WRITE：可写  
> GENERIC_READ | GENERIC_WRITE：可读可写  
> 0：皆非，只允许获取某些元数据，例如设备属性等

（3）dwShareMode：要对文件或设备使用的共享模式。部分取值：

> FILE_SHARE_READ：可读  
> FILE_SHARE_WRITE：可写  
> FILE_SHARE_DELETE：可删除  
> FILE_SHARE_READ | FILE_SHARE_WRITE：可读可写  
> FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE：全部  
> 0：皆非，阻止其它进程共享或在句柄关闭之前同时打开该文件或设备

（4）lpSecurityAttributes：指向 SECURITY_ATTRIBUTES
结构的指针，该结构包含两个数据成员：可选的安全描述符、确定返回的句柄是否可以被子进程继承的布尔值。部分取值：

> NULL：CreateFile 返回的句柄不能被应用程序可能创建的任何子进程继承，并且与返回的句柄关联的文件或设备将获得默认安全描述符。

（5）dwCreationDisposition：对存在或不存在的文件或设备采取的操作。对于文件以外的设备，此参数通常设置为 OPEN_EXISTING
。部分取值：

> CREATE_ALWAYS：总是创建一个新文件。如果指定文件存在且可写则覆盖该文件，如果指定文件不存在且路径是可写的有效路径则创建一个新文件。  
> CREATE_NEW：仅当指定文件不存在且路径有效时，创建一个新文件。  
> OPEN_ALWAYS：始终打开一个文件。如果指定文件不存在且路径是可写的有效路径则创建一个新文件。  
> OPEN_EXISTING：仅当指定文件或设备存在时，打开该文件或设备。  
> TRUNCATE_EXISTING：仅当指定文件存在时，打开该文件并将其截断为零字节。

（6）dwFlagsAndAttributes：文件或设备的属性和标志。对于文件来讲此参数通常的默认值为 FILE_ATTRIBUTE_NORMAL 。  
（7）hTemplateFile：具有 GENERIC_READ
访问权限的模板文件的有效句柄。模板文件为正在创建的文件提供文件属性和扩展属性。此参数通常设置为 NULL 。

 **返回值** ：  
如果函数成功，则返回值是指定文件、设备等的句柄。  
如果函数失败，则返回值是 INVALID_HANDLE_VALUE 。

 **2.1.2 CreateFileMappingA function**

 **函数定义** （该函数定义于 winbase.h 头文件）：

    
    
    HANDLE CreateFileMappingA(
      HANDLE                hFile,
      LPSECURITY_ATTRIBUTES lpFileMappingAttributes,
      DWORD                 flProtect,
      DWORD                 dwMaximumSizeHigh,
      DWORD                 dwMaximumSizeLow,
      LPCSTR                lpName
    );
    

**函数参数** ：  
（1）hFile：要从中创建文件映射对象的文件句柄。  
（2）lpFileMappingAttributes：指向 SECURITY_ATTRIBUTES
结构的指针，该结构确定返回的句柄是否可以被子进程继承。部分取值：

> NULL：句柄不能被继承，文件映射对象获得一个默认的安全描述符。

（3）flProtect：指定文件映射对象的页面保护方式。对象的所有映射视图必须与此保护兼容。部分取值：

> PAGE_EXECUTE_READ：允许将视图映射为只读、写时复制、执行。必须使用 GENERIC_READ 和 GENERIC_EXECUTE
> 访问权限创建文件句柄。
>
> PAGE_EXECUTE_READWRITE：允许将视图映射为只读、写时复制、读写、执行。必须使用 GENERIC_READ
> 、GENERIC_WRITE 和 GENERIC_EXECUTE 访问权限创建文件句柄。
>
> PAGE_EXECUTE_WRITECOPY：允许将视图映射为只读、写时复制、执行，此值等效于 PAGE_EXECUTE_READ 。必须使用
> GENERIC_READ 和 GENERIC_EXECUTE 访问权限创建文件句柄。
>
> PAGE_READONLY：允许将视图映射为只读、写时复制，尝试写入特定区域会导致访问冲突。必须使用 GENERIC_READ 访问权限创建文件句柄。
>
> PAGE_READWRITE：允许将视图映射为只读、写时复制、读写。必须使用 GENERIC_READ 和 GENERIC_WRITE
> 访问权限创建文件句柄。
>
> PAGE_WRITECOPY：允许将视图映射为只读、写时复制，此值等效于 PAGE_READONLY 。必须使用 GENERIC_READ
> 访问权限创建文件句柄。

（4）dwMaximumSizeHigh：文件映射对象最大大小（DWORD）的高位。  
（5）dwMaximumSizeLow：文件映射对象最大大小（DWORD）的低位。  
（6）lpName：文件映射对象的名称。部分取值：

> NULL：新建的文件映射对象没有名称。  
> 若此参数与现有映射对象的名称匹配，则该函数将请求访问具有 flProtect 指定保护的对象。

 **返回值** ：  
如果函数成功，则返回值是新创建的文件映射对象的句柄。  
如果映射对象先前已存在，则返回值是已有映射对象的句柄。  
如果函数失败，则返回值是 NULL 。

 **2.1.3 MapViewOfFile function**

 **函数定义** （该函数定义于 memoryapi.h 头文件）：

    
    
    LPVOID MapViewOfFile(
      HANDLE hFileMappingObject,
      DWORD  dwDesiredAccess,
      DWORD  dwFileOffsetHigh,
      DWORD  dwFileOffsetLow,
      SIZE_T dwNumberOfBytesToMap
    );
    

**函数参数** ：  
（1）hFileMappingObject：文件映射对象句柄。  
（2）dwDesiredAccess：对文件映射对象的访问类型。部分取值：

> FILE_MAP_ALL_ACCESS：文件的读写视图被映射。必须使用 PAGE_READWRITE 或 PAGE_EXECUTE_READWRITE
> 保护方式创建文件映射对象。当与 MapViewOfFile 函数一起使用时，FILE_MAP_ALL_ACCESS 等效于 FILE_MAP_WRITE
> 。
>
> FILE_MAP_READ：文件的只读视图被映射，尝试写入文件视图会导致访问冲突。必须使用
> PAGE_READONLY、PAGE_READWRITE、PAGE_EXECUTE_READ 或 PAGE_EXECUTE_READWRITE
> 保护方式创建文件映射对象。
>
> FILE_MAP_WRITE：文件的读写视图被映射。必须使用 PAGE_READWRITE 或 PAGE_EXECUTE_READWRITE
> 保护方式创建文件映射对象。当与 MapViewOfFile 函数一起使用时，(FILE_MAP_WRITE | FILE_MAP_READ) 和
> FILE_MAP_ALL_ACCESS 均等效于 FILE_MAP_WRITE 。

（3）dwFileOffsetHigh：视图起始位置文件偏移量（DWORD）高位。偏移量必须是系统内存分配粒度的整数倍。  
（4）dwFileOffsetLow：视图起始位置文件偏移量（DWORD）低位。偏移量必须是系统内存分配粒度的整数倍。  
（5）dwNumberOfBytesToMap：要映射到视图的文件映射对象的字节数，数值必须在 CreateFileMapping
指定的最大范围内。部分取值：

> 0：映射从指定的偏移量扩展到文件映射对象的末尾。

 **返回值** ：  
如果函数成功，则返回值是映射视图的起始地址。  
如果函数失败，则返回值为 NULL 。

### 2.2 程序实现

通过运用上文中的三个函数来完成对文件的内存映射，同时对其是否是 PE 文件进行判断。

**判断是否是 PE 文件？**两个标志位：  
（1）_IMAGE_DOS_HEADER 中字段 e_magic 的取值是否等于 IMAGE_DOS_SIGNATURE 。  
（2）_IMAGE_NT_HEADER 中字段 Signature 的取值是否等于 IMAGE_NT_SIGNATURE 。

程序代码如下：

    
    
    /*将项目属性中的字符集设置为“未设置”。*/
    
    #include <stdio.h>
    #include <Windows.h>
    #include <fileapi.h>
    #include <winbase.h>
    #include <memoryapi.h>
    #include <winnt.h>
    
    int main() {
    	LPCSTR FilePath;			//磁盘文件路径
    	HANDLE hFile;				  //文件内核对象句柄
    	HANDLE hMapping;			//文件映射对象句柄
    	LPVOID ImageBase;			//映射基址
    	PIMAGE_DOS_HEADER pDH = NULL;	//指向 _IMAGE_DOS_HEADER 结构的指针
    	PIMAGE_NT_HEADERS pNH = NULL;	//指向 _IMAGE_NT_HEADERS 结构的指针
    
    	//指定磁盘文件路径。
    	FilePath = "D:\\execase.exe";
    
    	//创建文件内核对象，返回文件内核对象句柄。
    	hFile = CreateFile(FilePath, GENERIC_READ | GENERIC_WRITE | GENERIC_EXECUTE, 0, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    	if (!hFile) {
    		printf("Create File Kernel Object Error! \n");
    		return FALSE;
    	}
    
    	//创建文件映射对象，获得文件映射对象句柄。
    	hMapping = CreateFileMapping(hFile, NULL, PAGE_EXECUTE_READWRITE | SEC_IMAGE, 0, 0, NULL);
    	if (!hMapping) {
    		printf("Create File Image Object Error! \n");
    		CloseHandle(hFile);
    		return FALSE;
    	}
    
    	//将文件映射对象映射到进程地址空间，获得映射基址。
    	ImageBase = MapViewOfFile(hMapping, FILE_MAP_ALL_ACCESS, 0, 0, 0);
    	if (!ImageBase) {
    		printf("Memory Mapping Error! \n");
    		CloseHandle(hMapping);
    		CloseHandle(hFile);
    		return FALSE;
    	}
    	printf("ImageBase: 0x%p \n", ImageBase);
    
    	//获取对应结构体指针。
    	pDH = (PIMAGE_DOS_HEADER)ImageBase;
    	pNH = (PIMAGE_NT_HEADERS)((DWORD)pDH + pDH->e_lfanew);
    
    	//判断标志位。
    	if (pDH->e_magic == IMAGE_DOS_SIGNATURE && pNH->Signature == IMAGE_NT_SIGNATURE)
    		printf("The file is a PE file! ");
    	else
    		printf("The file is not a PE file! ");
    
    	//关闭视图和句柄。
    	UnmapViewOfFile(ImageBase);
    	CloseHandle(hMapping);
    	CloseHandle(hFile);
    
    	return 0;
    }
    

# 三. 映射结果

以某个 PE 文件 execase.exe 为例，对映射结果进行对比分析。

### 3.1 判断结果

程序判断 execase.exe 为一个正常有效的 PE 文件，如图：  
![ImageBase &
PE](https://image.3001.net/images/20210913/1631527302_613f21866390c4a91d8f2.jpg!small)

### 3.2 对齐结果

PE 文件 execase.exe 在磁盘中存储时的结构及大小如下：  
![execase.exe
磁盘文件结构](https://image.3001.net/images/20210913/1631527303_613f218711242b2ad904f.jpg!small)  
（1）头部映射对齐： FA = 0x0 映射到 ImageBase = 0x00D30000 。  
![磁盘](https://image.3001.net/images/20210913/1631527303_613f2187d9b09f23f3eb2.jpg!small)  
![内存](https://image.3001.net/images/20210913/1631527304_613f2188db7f32d2b7ed6.jpg!small)  
（2）区块 .text 映射对齐： FA = 0x400 映射到 VA = 0x00D31000 。  
![磁盘](https://image.3001.net/images/20210913/1631527305_613f2189c4f10b076ade0.jpg!small)  
![内存](https://image.3001.net/images/20210913/1631527306_613f218aeb41753370cdc.jpg!small)  
（3）区块 .rdata 映射对齐： FA = 0xE00 映射到 VA = 0x00D32000 。  
![磁盘](https://image.3001.net/images/20210913/1631527308_613f218c019270d495e89.jpg!small)  
![内存](https://image.3001.net/images/20210913/1631527309_613f218d4ec5a37dd2a7a.jpg!small)  
（4）区块 .data 映射对齐： FA = 0x1600 映射到 VA = 0x00D33000 。  
![磁盘](https://image.3001.net/images/20210913/1631527310_613f218e7defd63c0b9bd.jpg!small)  
![内存](https://image.3001.net/images/20210913/1631527311_613f218fae70227b5ab4f.jpg!small)  
（5）后续区块以此类推继续往后对齐。

  
 **参考资料：**  
<https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea>  
<https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createfilemappinga>  
<https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-mapviewoffile>

 **特别感谢：**  
 **Winder** (School of software, Yunnan University)

**个人博客：[coonaa.cn](https://coonaa.cn)【[本文博客同步地址](https://coonaa.cn/index.php/archives/191/)】**  
 **相关文章：**[《 PE 文件结构解析》](https://coonaa.cn/index.php/archives/184/)

如有错误遗漏之处，欢迎补充交流。

