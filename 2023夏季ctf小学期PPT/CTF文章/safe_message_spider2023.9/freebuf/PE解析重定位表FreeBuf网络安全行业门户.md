## 一、程序加载过程

1、每个程序都有一个独立的4G内存空间，当你双击一个程序时，操作系统就为你开辟一个虚拟的4g内存空间，然后就开始贴图，将各个PE文件贴到内存空间，当贴完之后，eip指向程序入口点就开始跑了

> 低2G为用户空间，前后64K不会被分配，0-FFFF用于做各种无效检查（空指针就只向这里）
>
> 后64K 7FFF0000 - 8000000 用来做内核的交互。高2G空间是内核使用的。

2、一般情况下，EXE都是可以按照ImageBase的地址进行加载的.因为Exe拥有自己独立的4GB 的虚拟内存空间，但DLL不是
，DLL是有EXE使用它，才加载到相关EXE的进程空间的.

![1669855905_6387faa1ce0947730709b.png!small?1669855907539](https://image.3001.net/images/20221201/1669855905_6387faa1ce0947730709b.png!small?1669855907539)

3、为了提高搜索的速度，模块间地址也是要对齐的 模块地址对齐为10000H 也就是64K

![1669855918_6387faaebf38436ad5d4a.png!small?1669855920663](https://image.3001.net/images/20221201/1669855918_6387faaebf38436ad5d4a.png!small?1669855920663)

## 二、重定位表

![1669855931_6387fabb6134cbd368b44.png!small?1669855933149](https://image.3001.net/images/20221201/1669855931_6387fabb6134cbd368b44.png!small?1669855933149)

    
    
    1、也就是说，如果程序能够按照预定的ImageBase来加载的话，那么就不需要重定位表，这也是为什么exe很少有重定位表，而DLL大多都有重定位表的原因              
      
    2、一旦某个模块没有按照ImageBase进行加载，那么所有类似上面中的地址就都需要修正，否则，引用的地址就是无效的.           
      
    3、该程序往4GB空间加载时的位置如果不是文件中的 ImageBase，也就是说没占住原先设定的起始位置，那么上面写的绝对地址，肯定出大问题的。一个EXE中，需要修正的地方会很多，那我们需要重定位表来记录都有哪些地方需要修正   

## 三，重定位表的定位

数据目录项的第6个结构，就是重定位表.

![1669855943_6387fac7302bf19fec03b.png!small?1669855944855](https://image.3001.net/images/20221201/1669855943_6387fac7302bf19fec03b.png!small?1669855944855)

通过 IMAGE_DATA_DIRECTORY（数据目录）第六个结构的VirtualAddress 属性
找到第一个IMAGE_BASE_RELOCATION 结构

重定位表只有上述这个 IMAGE_BASE_RELOCATION 结构若干个，这两个字段后面还接有一大块表数据，为图中的“具体项”，如下图：

![1669855956_6387fad4c5318c836283d.png!small?1669855958823](https://image.3001.net/images/20221201/1669855956_6387fad4c5318c836283d.png!small?1669855958823)

## 代码实现

按照上述思路，可写代码打印重定位表的信息（不打印具体项，但按照上面公式打印具体项的数量）但这里注意一个问题，就是遍历这个重定位表，是根据这一块的
VirtualAddress 和 SizeOfBlock 结束后，下一块 VirtualAddress 和 SizeOfBlock 是否全0
来判断重定位表是否结束的

    
    
    VOID OutputRepositionTable()  
    {  
    PVOID pFileBuffer;  
    PIMAGE_DOS_HEADER pDosHeader = NULL;  
    PIMAGE_FILE_HEADER pPEHeader = NULL;  
    PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;  
    PIMAGE_SECTION_HEADER pSectionHeader = NULL;  
    PIMAGE_BASE_RELOCATION pRelocationTable = NULL;  
    ​  
    ReadPEFile(file_path, &pFileBuffer);  
    if (!pFileBuffer)  
    {  
    printf("读取文件到缓冲区失败");  
    return;  
    }  
    pDosHeader = (PIMAGE_DOS_HEADER)pFileBuffer;  
    pPEHeader = (PIMAGE_FILE_HEADER)((DWORD)((DWORD)pFileBuffer + pDosHeader->e_lfanew) + 4);  
    pOptionHeader = (PIMAGE_OPTIONAL_HEADER32)(((DWORD)pFileBuffer + pDosHeader->e_lfanew) + 4 + IMAGE_SIZEOF_FILE_HEADER);  
      
    pRelocationTable = (PIMAGE_BASE_RELOCATION)((DWORD)pFileBuffer+ RvaToOffset(pFileBuffer,pOptionHeader->DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].VirtualAddress));  
    ​  
    printf("RelocationTable VirtualAddress:%X\n",RvaToOffset( pFileBuffer,pOptionHeader->DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].VirtualAddress));  
    printf("RelocationTable Size:%X\n", pOptionHeader->DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].Size);  
    if (!pOptionHeader->DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].VirtualAddress)  
    {  
    printf("没有重定向表");  
    return;  
    }  
    int i = 1;  
    for (;pRelocationTable->VirtualAddress && pRelocationTable->SizeOfBlock;i++)  
    {  
    printf("第%d个快VirtualAddress：%X\n", i, pRelocationTable->VirtualAddress);  
    printf("第%d个块SizeOfBlock:%X\n", i, pRelocationTable->SizeOfBlock);  
    printf("第%d个块项数：%d\n", i, (pRelocationTable->SizeOfBlock - 8)/2);  
    pRelocationTable = (PIMAGE_BASE_RELOCATION)(pRelocationTable->SizeOfBlock + (DWORD)pRelocationTable);  
      
    }  
    }

  

## 修复重定位表

重定位表是由于在代码中写入的绝对地址，而 DLL 不能按照设想的 ImageBase
作起始加载位置去了别的地方占坑，那么需要根据重定位表记录的这些绝对地址在内存中的位置（RVA），逐一去到这些位置修复绝对地址，而产生的表。

表中记录的是 **需要修改的函数的地址偏移** ，需要根据偏移去到这个RVA修改掉这四字节的绝对地址

    
    
    //修改ImageBase  
    pOptionHeader->ImageBase += 0x1000000;  
    printf("ImageBase:%x\n", pOptionHeader->ImageBase);  
    ​  
    //修改重定位表中的值并输出  
    i = 1;  
    PWORD pItem;        //重定向表块中的项指针，2字节不断移动  
    int NumberOfItems;  //重定向表一块中的项数  
    int ItemAdd;        //重定向表一项中表示的地址变量，后续会不断变换为Rva FOA  
    pRelocationTable = (PIMAGE_BASE_RELOCATION)((DWORD)pFileBuffer + Rva_To_FOA(pFileBuffer, pOptionHeader->DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].VirtualAddress));  
    ​  
    printf("RelocationTable VirtualAddress%d\n", pOptionHeader->DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].VirtualAddress);  
    for (int i = 1; pRelocationTable->SizeOfBlock && pRelocationTable->VirtualAddress; i++)  
    {  
    printf("第%d个块VirtualAddress:%x\n", i, pRelocationTable->VirtualAddress);  
    printf("第%d个块SizeOfBlock:%x\n", i, pRelocationTable->SizeOfBlock);  
    NumberOfItems = (pRelocationTable->SizeOfBlock - 8) / 2;  
    pItem = (PWORD)((DWORD)pRelocationTable + 8);//定位到具体项开始处  
    printf("第%d个块项数:%d\n", i, NumberOfItems);  
    ​  
    for (int j = 0; j < NumberOfItems; j++)  
    {  
      
    if (*pItem &&0xF000 == 0x3000)  
    {  
    printf("项:%x   ", *pItem);  
    ItemAdd = (*pItem) & 0xFFF;  
    printf("修复前%X", ItemAdd);  
    ItemAdd = pRelocationTable->VirtualAddress + ItemAdd;  
    printf("项Rva:%x\n", ItemAdd);  
    *((PDWORD)ItemAdd) += 0x1000000;  
    printf("项Rva:%x\n", ItemAdd);  
    }  
    }  
    pRelocationTable = (PIMAGE_BASE_RELOCATION)(pRelocationTable->SizeOfBlock + (DWORD)pRelocationTable);  
    ​  
    }  
    //保存文件  
    isOk = MemoryToFile(pFileBuffer, size, write_file_path);  
    if (isOk)  
    {  
    printf("存盘成功");  
    return;  
    }  
    free(pFileBuffer);  
    ​  
    return;

