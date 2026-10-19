PE文件中大多数EXE文件只有导入表而没有导出表，除非这个EXE对外提供可调用的功能，比如某些自解压缩的文件等。  
DLL通常是既有导出也有导入表。  
DLL文件通过输出表向系统输出函数名，序号和入口地址等信息。

#### EXPORT_TABLES 导出表

代码重用机制提供了重用代码的动态链接库，用于说明库里面的哪些函数是可以被别人调用的，这就是导出表。

##### MAGE_EXPORT_DIRECTORY

    
    
    typedef struct _IMAGE_EXPORT_DIRECTORY {
        DWORD   Characteristics;// 属性旗标；没有定义 总是为0
        DWORD   TimeDateStamp;  //时间戳
        WORD    MajorVersion; //0
        WORD    MinorVersion;//0
        DWORD   Name;   //指向导出表文件名字符串
        DWORD   Base;   //导出函数起始序号
        DWORD   NumberOfFunctions;  //所有导出函数的个数
        DWORD   NumberOfNames;  //以函数名字导出的函数的个数
        DWORD   AddressOfFunctions;     // 导出函数地址表的RVA
        DWORD   AddressOfNames;         // 导出函数名称表的RVA
        DWORD   AddressOfNameOrdinals;  // 导出函数序号表的RVA
    } IMAGE_EXPORT_DIRECTORY, *PIMAGE_EXPORT_DIRECTORY;
    

Export
Table的主要结构，序数是指定DLL中某个函数的16位数字(独一无二的)，《加密与解密》中提到不建议用通过序数来找到地址调用函数，会带来DLL维护上的问题。  
因为DLL被升级或者修改，序数会变化。

##### IMAGE_DATA_DIRECTORY

NT表中的`IMAGE_OPTIONAL_HEADER`的 **扩展PE头**
，其中有一个结构体为_IMAGE_DATA_DIRECTORY，里面记录了导出表的起始地址和大小。

    
    
    typedef struct _IMAGE_DATA_DIRECTORY {
        DWORD   VirtualAddress;  //导出表的起始地址
        DWORD   Size;  //导出表的大小
    } IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;
    

##### CFF Explorer

用CFF Explorer打开查看，数据目录处可以看到导出表的信息  
![image](https://image.3001.net/images/20230510/1683683828_645af9f4a36a58013a001.png!small)  
导出表中包含了三张表  
_IMAGE_EXPORT_DIRECTORY.AddressOfFunctions; // 导出函数地址表EAT的RVA  
_IMAGE_EXPORT_DIRECTORY.AddressOfNames; // 导出函数名称表ENT的RVA  
_IMAGE_EXPORT_DIRECTORY.AddressOfNameOrdinals; //
导出函数序号表的RVA。这个表是字的数组。将ENT(程序入口点)中的数组索引映射到相应的输出地址表条目。

这里直接可以看到导出表在offset对应的值，就是FOA  
![image](https://image.3001.net/images/20230510/1683683846_645afa068e901b6ced69a.png!small)  
![image](https://image.3001.net/images/20230510/1683683853_645afa0db57010e0ff2dc.png!small)

通过导出表的三个 函数地址RVA、函数名字地址RVA、函数序列号RVA带入`VA20ffset()`函数来计算出FOA地址，找到在磁盘中的对应地址。  
加上缓冲区地址buffer得到实际的地址

    
    
    //打印导出表
    
            //导出表文件名的字符串
            DWORD NameFOA = VA2Offset(exporttable->Name + imagebase, ReadNTHeaders, m_pSecHdr);
            //导出表函数地址FOA
            DWORD AddresOfFunctionsFOA = VA2Offset(exporttable->AddressOfFunctions + imagebase, ReadNTHeaders, m_pSecHdr);
            //导出表函数名字地址FOA
            DWORD AddressOfNamesFOA = VA2Offset(exporttable->AddressOfNames + imagebase, ReadNTHeaders, m_pSecHdr);
            //导出表函数序列号FOA
            DWORD AddressOfNameOrdinalsFOA = VA2Offset(exporttable->AddressOfNameOrdinals + imagebase, ReadNTHeaders, m_pSecHdr);
    
            printf("\ndll_name:%s\n",(char *)(NameFOA+(LPBYTE)buffer));
    
            //AddressOfFunctions指向导出函数地址表
            DWORD* pAddressTable = (DWORD*)(buffer+ AddresOfFunctionsFOA);
    
            //AddressOfNameOrdinalsFOA指向导出函数序号表
            WORD* pOrdinals = (WORD*)(buffer + AddressOfNameOrdinalsFOA);
            //函数的名称，转换RVA，获取函数名
            DWORD* pNameTable=(DWORD*)(buffer + AddressOfNamesFOA);
    

#####  

##### VA2Offset RVA-->FOA

`VA2Offset(虚拟地址 NT表地址 第一个Section节表地址)`  
我们写函数方法来计算出FOA地址

    
    
    DWORD  VA2Offset(DWORD dwva, PIMAGE_NT_HEADERS m_pNtHdr, PIMAGE_SECTION_HEADER m_pSecHdr)
    {
        //imagebase文件基地址
        DWORD dwImageBase = m_pNtHdr->OptionalHeader.ImageBase;
    
        //文件对齐和内存对齐相等且不在文件头中
        if (m_pNtHdr->OptionalHeader.FileAlignment == m_pNtHdr->OptionalHeader.SectionAlignment || dwva <= m_pNtHdr->OptionalHeader.SizeOfHeaders)
        {
            return dwva;
        }
        else
        {
            for (int nInNum = 0; nInNum < m_pNtHdr->FileHeader.NumberOfSections; nInNum++)
            {
                if (dwva >= dwImageBase + m_pSecHdr[nInNum].VirtualAddress && dwva <= dwImageBase + m_pSecHdr[nInNum].VirtualAddress + m_pSecHdr[nInNum].Misc.VirtualSize)
                {
    
                    return m_pSecHdr[nInNum].PointerToRawData + dwva - m_pSecHdr[nInNum].VirtualAddress - m_pNtHdr->OptionalHeader.ImageBase;
                }
            }
        }
    }
    

pAddressTable指向各个导出函数的地址

##### 判断导出方式

不同的导出方式（也称为导出修饰符）会影响函数名称的形式，以及其他模块加载和调用该函数时所需要的方式。  
AddressOfNameOrdinals序号表保存的是AddressOfNames地址表的一个`[X]`下标;  
如果X这个下标 **保存在序号表中，说明是名称导出** ， **如果序号表中不存在，则是以序号导出** 。

> 当有AddressOfNameOrdinals[Y] 和AddressOfNames[X]  
> 且存在AddressOfNameOrdinals[Y] =X 时候就为名称导出

![image](https://image.3001.net/images/20230510/1683683875_645afa23dccd28eb22703.png!small)

    
    
    //判断是序号导出还是函数名导出
            BOOL bIndexIsExist = FALSE;
            for (int i = 0; i < exporttable->NumberOfFunctions; ++i) {
    
                // 打印虚序号、导出函数地址表(RVA)
                printf("虚序号[%d] ", i);
                printf("地址(RVA)： %08X", pAddressTable[i]);
    
                // 判断当前的这个地址是否是以名称方式导出的
                // 判断依据：
                //   序号表保存的是地址表的一个下标，这个下标记录着
                //   地址表中哪个地址是以名称方式导出的。
                //   如果当前的这个下标保存在序号表中，则说明这个地址
                //   是一个名称方式导出，如果这个下标在序号表中不存在，
                //   则说明，这个地址不是一个名称方式导出，而是以序号进行导出
    
    
                bIndexIsExist = FALSE;
                // 以导出名称导出的函数个数的数量循环
                int nNameIndex = 0;
                for (; nNameIndex < exporttable->NumberOfNames; ++nNameIndex) {
    
                    // 判断地址表的下标是否存在于序号表中 i==AddressOfNameOrdinals[Y]
                   // printf("  \n   %d   ",pOrdinals[nNameIndex]); 
                    if (i == pOrdinals[nNameIndex]) {
                        bIndexIsExist = TRUE;
                        break;
                    }
                }
                // 判断如果bIndexIsExist为真就是函数名导出，否则以函数序号导出。
               // 函数名要多转换一层RVA
                if (bIndexIsExist == TRUE) {
    
                    // 得到名称表中的RVA
                    DWORD dwNameRva = pNameTable[nNameIndex];
    
                    // 将名称Rva转换成存有真实函数名称的文件偏移
                    char* pFunName =
                        (char*)(buffer + VA2Offset(dwNameRva + imagebase, ReadNTHeaders, m_pSecHdr));
    
                    printf(" 函数名:【%s】\t", pFunName);
                    // i ： 是地址表中的索引号，也就是一个虚序号
                    // 真正的序号 = 虚序号 + 序号基数(起始序号)
                    printf(" 序号:【%d】 ", i + exporttable->Base);
                }
                // 当没有导出函数名称，则是以序号进行导出使用
                if (bIndexIsExist == FALSE)
                {
    
                    // 判断地址表当前索引到的位置是否保存着地址
                    if (pAddressTable[i] != 0) {
    
                        printf(" 函数名:【-】\t");
                        // i ： 是地址表中的索引号，也就是一个虚序号
                        // 真正的序号 = 虚序号 + 序号基数
                        printf(" 序号:【%d】", i + exporttable->Base);
                    }
                }
    
                printf("\n");
            }
    

##### 实例

这里写一个标准的简单dll，有6个方法  
![image](https://image.3001.net/images/20230510/1683683893_645afa353ef540d66e537.png!small)  
为了区分序号导出和名称导出，在Source.def里面定义myFunc 为1 Add为2  
![image](https://image.3001.net/images/20230510/1683683899_645afa3bceb0225f96ea0.png!small)  
然后执行程序判断petest.dll的导出表里面具体的方法的导出方式  
![image](https://image.3001.net/images/20230510/1683683906_645afa428d062744d3a8d.png!small)  
可以看到实际序号为1，2的是我们def定义的myFunc、和Add，其余的函数为名称导出。

Base:这个字段包含用于这个PE文件输出表的起始序数值(基数)。在正常情况下这个值是1。  
当通过序数来查询一个输出函数时，这个值从序数里被减去，其结果将作为进人输出地址表(EAT)的索引。  
例如：Base 的值为 1，序号为 5 的函数的实际序号(虚序号)为 5-1=4，那么在 EAT 中查找索引为 4 的地址即可找到对应的导出函数。

#### 小结

1.导出表就是此PE文件对外提供了可以用的API的信息.  
2.通过AddressOfNames和AddressOfNameOrdinals的对应关系来判断导出方式。  
3.在EAT Hook中就是通过修改导出函数，在别的进程调用到此PE文件的函数功能的时候，就完成hook了。必须需要修改磁盘中的PE文件本身。

### IMPORT_TABLES 导入表

可执行文件使用来自其他DLL的代码或者数据称之为导入。  
导入表中保存的是函数名和所需DLL名等动态链接所需要的信息。  
导入表在加壳技术中地位很重要。

##### 导入函数

导入函数是被程序调用但执行代码不在程序中的函数，位于相关的DLL中。  
对于磁盘上的PE文件来说，无法得知这些导入函数在内存中的地址。当PE文件被载入内存后，Windows加载器会根据导入表把相关DLL载入，把调用函数和相关地址联系起来。

##### 隐式和显示加载

当程序调用一个DLL的代码或者数据时，程序在被隐式地链接到DLL，过程完全由Windows加载器完成。  
显式则是目标DLL已经被加载，然后寻找API的地址，几乎都是通过调用`LoadLibrary()`和`GetProcAddress()`完成的。  
其中有一组数据结构，分别对应与被输入导入的DLL。

##### IMAGE_IMPORT_DESCRIPTOR

1.在数据⽬录中的第⼆个⽬录，即`IMAGE_DIRECTORY_ENTRY_IMPORT`  
2.每个DLL都对应⼀个`IMAGE_IMPORT_DESCRIPTOR`结构,导⼊的DLL⽂件与  
`IMAGE_IMPORT_DESCRIPTOR`是⼀对⼀的关系

    
    
    typedef struct _IMAGE_IMPORT_DESCRIPTOR {
    union {
    DWORD Characteristics; 
    DWORD OriginalFirstThunk; // 导⼊名称表的RVA
    } DUMMYUNIONNAME;
    DWORD TimeDateStamp; // 时间戳,可判断是否绑定了函数地址 
    
    DWORD ForwarderChain; // 该字段⼀般为0
    DWORD Name; // 该字段为DLL名称的指针，该指针也为⼀个RVA
    DWORD FirstThunk; // 导⼊地址表（IAT）的RVA，IAT
    } IMAGE_IMPORT_DESCRIPTOR;
    

OriginalFirstThun:包含指向导入入名称表(INT)的RVA。Import Name
Table是一个`IMAGE_THUNK_DATA`结构的数组。  
TimeDateStamp 一个32位的时间标志  
ForwarderChain 一般为0  
Name:DLL名字的指针。字符包含输入的DLL名字。  
FirstThunk：包含指向IAT的RVA。  
OriginalFirstThun和FirstThunk相似，分别指向两个本质上相同的`IMAGE_THUNK_DATA`结构。也就是INT和IAT了。

##### IMAGE_THUNK_DATA

    
    
    typedef struct _IMAGE_THUNK_DATA32{
    union {
     PBYTE ForwarderString; //指向⼀个转向者字符串的RVA
     PDWORD Function; //输⼊的函数的内存地址
     DWORD Ordinal; //输⼊的API的序号值
     PIMAGE_IMPORT_BY_NAME AddressOfData; //指向IMAGE_IMPORT_BY_NAME的RVA
     }u1;
    }IMAGE_THUNK_DATA32;
    

Function 输入的函数内存地址  
Ordinal：输入的API序号值  
AddressOfData：指向`IMAGE_IMPORT_BY_NAME`结构体

IMAGE_THUNK_DATA占⽤4个字节，当`IMAGE_THUNK_DATA`的最⾼位为1时，表示函数以  
序号⽅式导⼊，直接去掉最⾼位，剩下的31位的值便是dll函数在导出表中的导出序号；  
当其最⾼位为0时
表示函数以函数名字符串的⽅式导⼊，这时双字`_IMAGE_THUNK_DATA`的值表示⼀个RVA，并指向`IMAGE_IMPORT_BY_NAME`结构体。

下图是标识一个可执行文件从"USER32.dll"里面导入一些API函数。  
也就是说在`IMAGE_THUNK_DATA`高位不同的时候，同一个地址指向的内容，会出现不同，高位为IAT，低位为INT，这两个指针指向同一个`IMAGE_IMPORT_BY_NAME`  
![image](https://image.3001.net/images/20230510/1683684135_645afb273baac23463efd.jpg!small)

这里同时输出了originalFirstThunk和FirstThunk的地址，可以看到输出指向的地址一样，  
![image](https://image.3001.net/images/20230510/1683684142_645afb2ebf736bcd1f00b.jpg!small)  
现在看着两个地址是一样的，但是在DLL完成函数加载后，`FirstThunk`会由PE加载器重写，  
先搜索OriginalFirstThunk，如果找到，加载程序迭代搜索数组中的每个指针，找出每个  
`IMAGE_IMPORT_BY_NAME`结构所指向的输⼊函数地址，然后加载器函数真正的⼊⼝地址来替代由  
FirstThunk指向的`IMAGE_THUNK_DATA`结构体。

可以理解成完成加载后，FirstThunk会被重写来指向载入进来的API真正的地址。  
加载到内存之后导⼊表的内容将会被操作系统填充为新的函数的地址。  
![image](https://image.3001.net/images/20230510/1683684152_645afb384ed2545450e2e.png!small)

##### IMAGE_IMPORT_BY_NAME

    
    
    typedef struct _IMAGE_IMPORT_BY_NAME {
     WORD Hint; //表示该函数在其DLL中的导出表中的序号
     CHAR Name[1]; //函数名
    } IMAGE_IMPORT_BY_NAME, *PIMAGE_IMPORT_BY_NAME;
    

Hint：本函数在其DLL的输出表中的序号。用于快速查询函数，不是必须的。  
Name:含有输入函数的函数名。

#### 代码获取导出表

##### Import Name Address(INT)

    
    
    printf("\n导入表：\n");
            //通过NTHeaders来找到Import Directory的虚拟地址
            DWORD Rva_importdata = ReadNTHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress;
            if (Rva_importdata!=0)
            {
                //RVA转换成FOA
                DWORD importTableOffset = VA2Offset(Rva_importdata + imagebase, ReadNTHeaders, m_pSecHdr);
    
                if (importTableOffset > 0)
                {
                    HMODULE library = NULL;
                    PIMAGE_IMPORT_BY_NAME functionName = NULL;
                    int i = 0;
                    LPCSTR libraryName;
                    PIMAGE_IMPORT_DESCRIPTOR import_descrip = (PIMAGE_IMPORT_DESCRIPTOR)(importTableOffset + buffer);
                    //打印Import Name Table 信息
                    while (import_descrip->Name)
                    {
                        //计算出Name的FOA 直接打印出dll名称
                        libraryName = (LPCSTR)(VA2Offset(import_descrip->Name + imagebase, ReadNTHeaders, m_pSecHdr) + buffer);
                        printf("dll名称：%s\n", libraryName);
    
                        //用LoadLibray加载出dll
                        library = LoadLibrary(libraryName);
                        if (library)
                        {
                            PIMAGE_THUNK_DATA originalFirstThunk = NULL, firstThunk = NULL;
                            //计算出INT导入名称表的FOA
                            originalFirstThunk = (PIMAGE_THUNK_DATA)(VA2Offset(import_descrip->OriginalFirstThunk + imagebase, ReadNTHeaders, m_pSecHdr) + buffer);
                            firstThunk = (PIMAGE_THUNK_DATA)(VA2Offset(import_descrip->FirstThunk + imagebase, ReadNTHeaders, m_pSecHdr) + buffer);
                            //判断最高位是否位0，为0以名字导入，64位系统为例
                            //IMAGE_THUNK_DATA的最高位是否为0  Ordinal输⼊的API的序号值
                            if (!(originalFirstThunk->u1.Ordinal & IMAGE_ORDINAL_FLAG))
                            {
                                int j = 1;
                                //判断PIMAGE_THUNK_DATA双字值的最高位为1 是以序号输入
                                while (originalFirstThunk->u1.AddressOfData != NULL)
                                {
                                    //指向IMAGE_IMPORT_BY_NAME的RVA
                                    functionName = (PIMAGE_IMPORT_BY_NAME)(VA2Offset(originalFirstThunk->u1.AddressOfData + imagebase, ReadNTHeaders, m_pSecHdr) + buffer);
                                    printf("函数名字符串的方式导入：%s\n", functionName->Name);
                                    //输⼊的函数的内存地址
                                    printf("originalFirstThunk指向的输入的函数的内存地址%x\n", originalFirstThunk->u1.Function);
                                    printf("FirstThunk指向的输入的函数的内存地址：%x\n", firstThunk->u1.Function);
                                    //指向IMAGE_IMPORT_BY_NAME的RVA
                                    printf("指向IMAGE_IMPORT_BY_NAME的RVA：%08x\n", firstThunk->u1.AddressOfData);
                                    printf("\n\n");
                                    ++originalFirstThunk;
                                    ++firstThunk;
                                    ++j;
                                }
                            }
                            //以序号方式导入
                            else
                            {
                                int j = 1;
                                while (originalFirstThunk->u1.Ordinal != NULL)
                                {
                                    DWORD dwOrdinal = originalFirstThunk->u1.Ordinal & ~IMAGE_ORDINAL_FLAG;
                                    printf("序号方式导入：%d", dwOrdinal);
                                    ++originalFirstThunk;
                                    ++firstThunk;
                                    ++j;
                                }
                            }
    
    
                        }
                        ++import_descrip;
    
                    }
    
                }
    
            }
    

![image](https://image.3001.net/images/20230510/1683684169_645afb4937bb28f54dff3.png!small)

##### Import Address Tables(IAT)

`IMAGE_IMPORT_DESCRIPTOR`中我们知道`FirstThunk`指向另外一个`IMAGE_THUNK_DATA`也就是IAT，这里可以直接通过NTHeader调用DataDirectory[]来直接获取IAT的RVA地址，也可以和前面一样通过找到指向`IMAGE_IMPORT_DESCRIPTOR`的指针来找到`FirstThunk`。

    
    
    //Import Address Tables 导入地址表
            printf("\nIAT：\n");
            //通过IMAGE_DIRECTORY_ENTRY_IAT序号来找到FirstThunk的RVA
           //DWORD  iatTable = ReadNTHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IAT].VirtualAddress;
    
            if (Rva_importdata != 0)
            {
                //RVA转换城FOA
                DWORD importTableOffset = VA2Offset(Rva_importdata + imagebase, ReadNTHeaders, m_pSecHdr);
    
                if (importTableOffset > 0)
                {
                    HMODULE library = NULL;
                    PIMAGE_IMPORT_BY_NAME functionName = NULL;
                    int i = 0;
                    LPCSTR libraryName;
                    PIMAGE_IMPORT_DESCRIPTOR import_descrip = (PIMAGE_IMPORT_DESCRIPTOR)(importTableOffset + buffer);
                    DWORD iatTable = import_descrip->FirstThunk;
                    DWORD  iatTable2 = ReadNTHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IAT].VirtualAddress;
                    printf("iatTable:%x   iatTable2:%x\n", iatTable, iatTable2);
    
                    PIMAGE_THUNK_DATA piat = (PIMAGE_THUNK_DATA)(VA2Offset((iatTable + imagebase), ReadNTHeaders, m_pSecHdr) + buffer);
                   //u1是IMAGE_THUNK_DATA的命名，里面的Function 表示 导入函数的内存地址
                    while (piat->u1.Function != NULL)
                    {
                        //加上缓存buffer 输出内存地址
                        FARPROC fpAddress = (FARPROC)(buffer + piat->u1.Function);
                        printf("fpAddress:%x\n", fpAddress);
                        piat++;
                    }
                }
            }
    

两者地址是一样的  
![image](https://image.3001.net/images/20230510/1683684179_645afb5365ca1e43d2244.png!small)

##### DLL加载 API

LoadLibrary() 函数用于加载指定的 DLL 文件到进程空间中，并返回一个指向该 DLL 的句柄。通过调用 LoadLibrary()
函数，应用程序可以在运行时动态地链接并加载 DLL，从而可以使用 DLL 中的函数和数据。

GetProcAddress() 函数用于在加载到进程空间中的 DLL 中查找并返回指定函数的地址。通过调用 GetProcAddress()
函数，应用程序可以在运行时获取 DLL 中函数的地址，然后通过函数指针调用这些函数。

##### 隐藏导入表

使用VSStudio自带的一个叫作`dumpbin.exe`的PE文件可以很方便的查看导入导出表  
`dumpbin.exe /import name.exe`  
这里可以看到我们的程序需要使用的导出DLL,以及对应的API  
一些杀软会通过导出表来判断是调用了敏感函数  
![image](https://image.3001.net/images/20230510/1683684379_645afc1b98b248c45545c.png!small)  
实现隐藏文件的导入表，首先需要找到敏感函数的类型定义  
比如`HeapCreate`创建可以由进程使用的句柄API  
![image](https://image.3001.net/images/20230510/1683684198_645afb6618d50f8c214f1.png!small)  
然后在代码里面申明定义  
![image](https://image.3001.net/images/20230510/1683684205_645afb6d28d2955f95724.png!small)  
为了确保能找到API地址，再用`LoadLibray()`来打开这些API所属的DLL  
{一般情况windows本身会加载一些常用的dll比如kernel32.dll ntdll.dll USER32.dll这些}  
![image](https://image.3001.net/images/20230510/1683684212_645afb743563e751dfc95.png!small)  
然后用GetProcAddress()再去找对应API的地址就一定能找到  
![image](https://image.3001.net/images/20230510/1683684220_645afb7c0e4511c87f914.png!small)  
现在有了API的地址，就可以直接调用功能完全相同，但不会被写入导入表的API了

可以看到，通过隐藏操作后，USER32.dll不会被导出，之前使用的`HeapCreate`、`HeapAlloc`API也不存在了，但是Loadlibray、GetProcAddress是会被导入的  
![image](https://image.3001.net/images/20230510/1683684226_645afb827162ec840b592.png!small)

#### 小结

1.导入表主要作用就是保存PE文件所需要使用到其他DLL的函数方法相关信息。  
2.INT和IAT指向同一个结构体，在Windows Loader未装载完成DLL的时候，也就是我们看到上面输出的地址 OriginalFirstThun
和FirstThunk指向地址相同；装载完成后Windows Loader会将函数地址写入Image Thunk
Data结构体，并改写FirstThunk指向。  
3.IAT
Hook是通过修改PE文件导入表中的函数地址，PE文件启动时候会调用导入表中的函数，这时候就完成了Hook。这是在程序动态加载的时候完成的，在内存中就可以完成。  
4.EAT Hook比IAT Hook更难以实现和更危险，因为它可以影响到整个系统中调用该PE文件导出函数的所有进程，而IAT
Hook只会影响到当前进程中的调用。

