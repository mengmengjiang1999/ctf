## 导出表概念

> 导出表描述了当前PE文件提供了哪些函数。
> PE文件相当于一个饭店，那么菜单就是导出表.，导出表一般用于DLL文件,但并不是EXE文件不可以有导出表，本质都是PE文件，都可以拥有导出表。DLL导出了什么函数都记录在导出表上,在数据目录的第1项,下标为0

### 1.如何定位导出表：

数据目录项的第一个结构，就是导出表.

    
    
    typedef struct _IMAGE_DATA_DIRECTORY {    
    DWORD   VirtualAddress;     
    DWORD   Size;       
    } IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;    
    ​

VirtualAddress 导出表的RVA ​ Size 导出表大小 （ Size 字段不一定是真实的）

### 2.导出表结构

上面的结构，只是说明导出表在哪里，有多大，并不是真正的导出表. ​
**如何在FileBuffer中找到这个结构呢？在VirtualAddress中存储的是RVA,如果想在FileBuffer中定位 ​
必须要先将该RVA转换成FOA.** ​ 真正的导出表结构如下：

  

![1669854978_6387f702957f43ce82046.png!small?1669854980452](https://image.3001.net/images/20221201/1669854978_6387f702957f43ce82046.png!small?1669854980452)

 **NAME** ：指针(Rva)，指向导出表文件名字 字符串. xx.dll

#### AddressOfFunctions说明：

该地址存着dll或EXE所有导出函数的入口地址

该表中元素宽度为4个字节 ​ 该表中存储所有导出函数的地址 ​ 该表中个数由NumberOfFunctions决定 ​ 该表项中的值是RVA,
加上ImageBase才是函数真正的地址 ​ 定位： ​ IMAGE_EXPORT_DIRECTORY->AddressOfFunctions
中存储的是该表的RVA 需要先转换成FOA

#### AddressOfNames说明：

该地址存着dll或EXE所有导出函数名字的地址

该表中元素宽度为4个字节 该表中存储所有以名字导出函数的名字的RVA 该表项中的值是RVA, 指向函数真正的名称

![1669854999_6387f717ebd3e4de3b276.png!small?1669855002071](https://image.3001.net/images/20221201/1669854999_6387f717ebd3e4de3b276.png!small?1669855002071)

#### AddressOfNameOrdinals

该地址存着dll或EXE所有导出函数的序号

![1669855014_6387f7268fcbb63e5c930.png!small?1669855016273](https://image.3001.net/images/20221201/1669855014_6387f7268fcbb63e5c930.png!small?1669855016273)

### 总结：

为什么要分成3张表？ ​ 1、函数导出的个数与函数名的个数未必一样.所以要将函数地址表和函数名称表分开. ​ 2、函数地址表是不是一定大于函数名称表？ ​
未必，一个相同的函数地址，可能有多个不同的名字. ​ 3、如何根据函数的名字获取一个函数的地址？

![1669855028_6387f734abafbd6f4e2e8.png!small?1669855030387](https://image.3001.net/images/20221201/1669855028_6387f734abafbd6f4e2e8.png!small?1669855030387)

4、如何根据函数的导出序号获取一个函数的地址？

![1669855040_6387f7403fb4a973e2ed6.png!small?1669855042039](https://image.3001.net/images/20221201/1669855040_6387f7403fb4a973e2ed6.png!small?1669855042039)

为了再巩固一下，这里再举一个真实的例子，根据上面的规则自己走一遍。

.dll 导出函数由以下def 文件导出，可见序号为 2 3 5 6

    
    
    EXPORTS   
      
    Plus    @2  
    Sub     @5 NONAME  
    Mul     @3  
    Div     @6

## 练习：

#### 1、编写程序打印所有的导出表信息

  

    
    
    VOID PutExportTable()  
    {  
    PVOID pFileBuffer;  
    PIMAGE_DOS_HEADER pDosHeader = NULL;  
    PIMAGE_FILE_HEADER pPEHeader = NULL;  
    PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;  
    PIMAGE_SECTION_HEADER pSectionHeader = NULL;  
    PIMAGE_EXPORT_DIRECTORY pExportTable = NULL;  
    ​  
    DWORD AddressOfNameFOA = NULL;  
    DWORD AddressOfNameOrdinalsFOA = NULL;  
    DWORD AddressOfFunctions = NULL;  
    WORD Ordinal = NULL;  
    ​  
    BOOL isOk = FALSE;  
    DWORD size = 0;  
    ReadPEFile(file_path, &pFileBuffer);  
    if (!pFileBuffer)  
    {  
    printf("读取文件失败");  
    return;  
    }  
    pDosHeader = (PIMAGE_DOS_HEADER)pFileBuffer;  
    pPEHeader = (PIMAGE_FILE_HEADER)((DWORD)((DWORD)pFileBuffer + pDosHeader->e_lfanew) + 4);  
    pOptionHeader = (PIMAGE_OPTIONAL_HEADER32)(((DWORD)pFileBuffer + pDosHeader->e_lfanew) + 4 + IMAGE_SIZEOF_FILE_HEADER);  
    pSectionHeader = (PIMAGE_SECTION_HEADER)(((DWORD)pFileBuffer + pDosHeader->e_lfanew) + 4 + IMAGE_SIZEOF_FILE_HEADER + pPEHeader->SizeOfOptionalHeader);  
    ​  
    pExportTable = (PIMAGE_EXPORT_DIRECTORY)((DWORD)pFileBuffer+ RvaToOffset(pOptionHeader->DataDirectory[0].VirtualAddress ,pFileBuffer));  
    printf("DIRECTORY_ENTRY_EXPORT ViltualAddress:%X\n", pOptionHeader->DataDirectory[0].VirtualAddress);  
    ​  
    printf("Characteristics: %#x\n", pExportTable->Characteristics);  
    printf("TimeDateStamp: %#x\n", pExportTable->TimeDateStamp);  
    printf("MajorVersion: %#x\n", pExportTable->MajorVersion);  
    printf("MinorVersion: %#x\n", pExportTable->MinorVersion);  
    printf("Name: %s\n", (PVOID)((DWORD)pFileBuffer + RvaToOffset(pExportTable->Name, pFileBuffer)));//(PVOID)((DWORD)pFileBuffer + RvaToOffset(pExportTable->Name,pFileBuffer))  
    printf("Base: %#x\n", pExportTable->Base);  
    printf("NumberOfFunctions: %#x\n", pExportTable->NumberOfFunctions);  
    printf("NumberOfNames: %#x\n", pExportTable->NumberOfNames);  
    printf("AddressOfFunctions: %#x\n", pExportTable->AddressOfFunctions);  
    printf("AddressOfNames: %#x\n", pExportTable->AddressOfNames);  
    printf("AddressOfNameOrdinals: %#x\n", pExportTable->AddressOfNameOrdinals);//52590  
    ​  
    }

#### 2、编写函数 GetFunctionAddrByName ( FileBuffer指针，函数名指针)

    
    
    DWORD GetFunctionAddressByName(LPVOID pFileBuffer, LPCSTR Name)  
    {  
    PIMAGE_DOS_HEADER pDosHeader = (PIMAGE_DOS_HEADER)pFileBuffer;  
    PIMAGE_NT_HEADERS32 pNtHeader = (PIMAGE_NT_HEADERS32)((DWORD)pFileBuffer + pDosHeader->e_lfanew);  
    PIMAGE_FILE_HEADER pFileHeader = (PIMAGE_FILE_HEADER)((DWORD)pFileBuffer + pDosHeader->e_lfanew + 4);  
    PIMAGE_OPTIONAL_HEADER pOptionalHeader = (PIMAGE_OPTIONAL_HEADER)((DWORD)pFileBuffer + pDosHeader->e_lfanew + 4 + IMAGE_SIZEOF_FILE_HEADER);  
    PIMAGE_SECTION_HEADER pSectionHeader = (PIMAGE_SECTION_HEADER)((DWORD)pFileBuffer + pDosHeader->e_lfanew + 4 + IMAGE_SIZEOF_FILE_HEADER + pFileHeader->SizeOfOptionalHeader);  
    ​  
    PIMAGE_DATA_DIRECTORY pDirectory = (PIMAGE_DATA_DIRECTORY)pOptionalHeader->DataDirectory;  
    PIMAGE_EXPORT_DIRECTORY pExportTable = (PIMAGE_EXPORT_DIRECTORY)((DWORD)pFileBuffer + Rva_To_FOA(pFileBuffer, pDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress));  
    if (!pExportTable)  
    {  
    printf("没有导出表");  
    free(pFileBuffer);  
    return 0;  
    }  
    //将Rva的值转为Foa  
    PDWORD AddressOfNames = (PDWORD)((DWORD)pFileBuffer + Rva_To_FOA(pFileBuffer, pExportTable->AddressOfNames));  
    PDWORD AddressOfFunctions = (PDWORD)((DWORD)pFileBuffer + Rva_To_FOA(pFileBuffer, pExportTable->AddressOfFunctions));  
    PWORD AddressOfNameOrdinals = (PWORD)((DWORD)pFileBuffer + Rva_To_FOA(pFileBuffer, pExportTable->AddressOfNameOrdinals));  
    ​  
    for (int i = 0; i < pExportTable->NumberOfNames; i++)  
    {  
    if (!strcmp((LPCSTR)((DWORD)pFileBuffer + Rva_To_FOA(pFileBuffer, AddressOfNames[i])), Name))  
    {  
    return AddressOfFunctions[AddressOfNameOrdinals[i]];  
    }  
    }  
    ​  
    return 0;  
    ​  
    }

#### 3、编写函数 GetFunctionAddrByOrdinals ( FileBuffer指针，函数名导出序号)

    
    
    DWORD GetFunctionAddressByOrdinals(LPVOID pFileBuffer, DWORD Ordinals)  
    {  
    PIMAGE_DOS_HEADER pDosHeader = (PIMAGE_DOS_HEADER)pFileBuffer;  
    PIMAGE_NT_HEADERS32 pNtHeader = (PIMAGE_NT_HEADERS32)((DWORD)pFileBuffer + pDosHeader->e_lfanew);  
    PIMAGE_FILE_HEADER pFileHeader = (PIMAGE_FILE_HEADER)((DWORD)pFileBuffer + pDosHeader->e_lfanew + 4);  
    PIMAGE_OPTIONAL_HEADER pOptionalHeader = (PIMAGE_OPTIONAL_HEADER)((DWORD)pFileBuffer + pDosHeader->e_lfanew + 4 + IMAGE_SIZEOF_FILE_HEADER);  
    PIMAGE_SECTION_HEADER pSectionHeader = (PIMAGE_SECTION_HEADER)((DWORD)pFileBuffer + pDosHeader->e_lfanew + 4 + IMAGE_SIZEOF_FILE_HEADER + pFileHeader->SizeOfOptionalHeader);  
    ​  
    PIMAGE_DATA_DIRECTORY pDirectory = (PIMAGE_DATA_DIRECTORY)pOptionalHeader->DataDirectory;  
    PIMAGE_EXPORT_DIRECTORY pExportTable = (PIMAGE_EXPORT_DIRECTORY)((DWORD)pFileBuffer + Rva_To_FOA(pFileBuffer, pDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress));  
    if (!pExportTable)  
    {  
    printf("没有导出表");  
    free(pFileBuffer);  
    return 0;  
    }  
    //将Rva的值转为Foa  
    PDWORD AddressOfNames = (PDWORD)((DWORD)pFileBuffer + Rva_To_FOA(pFileBuffer, pExportTable->AddressOfNames));  
    PDWORD AddressOfFunctions = (PDWORD)((DWORD)pFileBuffer + Rva_To_FOA(pFileBuffer, pExportTable->AddressOfFunctions));  
    PWORD AddressOfNameOrdinals = (PWORD)((DWORD)pFileBuffer + Rva_To_FOA(pFileBuffer, pExportTable->AddressOfNameOrdinals));  
      
    return AddressOfFunctions[Ordinals-pExportTable->Base];  
    }

