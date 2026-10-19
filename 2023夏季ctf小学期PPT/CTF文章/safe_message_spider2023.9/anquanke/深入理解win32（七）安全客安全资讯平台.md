# 深入理解win32（七）

阅读量 **129388**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-05 10:30:29

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01e94717568627114f.jpg)

## 前言

在前一节中我们介绍了PE中两个比较重要的表，分别为导出表和重定位表，这一节中我们来进行导入表的解析，在导入表里面又有两个比较重要的结构，分别是IAT表和INT表。

## 导入表

导入表是记录PE文件中用到的动态连接库的集合，一个dll库在导入表中占用一个元素信息的位置，这个元素描述了该导入dll的具体信息。如dll的最新修改时间、dll中函数的名字/序号、dll加载后的函数地址等。这里比如我们用od打开一个exe，找到他的导入表如下所示

![](https://p2.ssl.qhimg.com/t0120368bee024c2571.jpg)

通俗的理解就是在程序加载的过程中需要调用到windows提供的一些api，那么这些api并不是能够直接进行调用的，这些api存放在dll里面，所以需要用`LoadLibrary`把dll加载到程序的进程空间里来使用这些api。换个说法，通过`LoadLibrary`将dll加载进程空间的dll，都会在导入表里面出现，如果自己通过代码来实现`LoadLibrary`的功能将要使用的dll加载进进程空间，那么在导入表里面就不会出现要使用的dll，这就是后面隐藏模块的原理。

我们再回到导入表的话题，导入表位于数据目录项的第二个结构，如下图所示

![](https://p0.ssl.qhimg.com/t015c27f69affe92ec4.jpg)

这里首先看一下结构

    
    
    typedef struct _IMAGE_DATA_DIRECTORY {
        DWORD   VirtualAddress;
        DWORD   Size;
    } IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;
    

这里跟导出表与重定位表相似，VirtualAddress是指向真正导入表结构的RVA，而Size为导入表的大小，我们通过VirtualAddress的RVA转换FOA之后在FileBuffer中定位后得到如下结构

    
    
    typedef struct _IMAGE_IMPORT_DESCRIPTOR {
        union {
            DWORD   Characteristics;         
            DWORD   OriginalFirstThunk;        //RVA 指向IMAGE_THUNK_DATA结构数组（即INT表）
            };
        DWORD   TimeDateStamp;              //时间戳    
        DWORD   ForwarderChain;                      
        DWORD   Name;                        //RVA,指向dll名字，该名字以0结尾                    
        DWORD   FirstThunk;                 //RVA,指向IMAGE_THUNK_DATA结构数组（即IAT表）          
    } IMAGE_IMPORT_DESCRIPTOR;                            
    typedef IMAGE_IMPORT_DESCRIPTOR UNALIGNED *PIMAGE_IMPORT_DESCRIPTOR;
    

这里要注意的就是两个结构，OriginalFirstThunk和FirstThunk，其中OriginalFirstThunk对应的就是IAT表(即Import
Address Table)，FirstThunk对应的就是INT表(即Import Name Table)。

我们看一下PE文件加载前内存中的情况，在PE文件加载前，INT表跟IAT表都是存储的相同的结构并指向IMAGE_IMPORT_BY_NAME

![](https://p3.ssl.qhimg.com/t01fe942dea1c4bc02b.jpg)

在PE加载完成后INT表的结构不变，而IAT表则是直接存储了函数的地址

![](https://p5.ssl.qhimg.com/t018eb1072661febfeb.jpg)

## IAT表&INT表

加载到内存前我们看到IAT和INT都指向一个结构体数组，有多少个函数被导入，这个数组就有多少个成员，并且该数组以0结尾。这个数组存储了序号和函数名。IAT和INT的元素为IMAGE_THUNK_DATA结构，而其指向为IMAGE_IMPORT_BY_NAME结构，这两个结构体如下所示：

IMAGE_THUNK_DATA结构体汇总只有一个联合体，一般用四字节的AddressOfData来获取IMAGE_IMPORT_BY_NAME的地址。

    
    
    typedef struct _IMAGE_THUNK_DATA32 {
        union {
            DWORD ForwarderString;      // PBYTE 
            DWORD Function;             // PDWORD
            DWORD Ordinal;
            DWORD AddressOfData;        //RVA 指向_IMAGE_IMPORT_BY_NAME 
        } u1;
    } IMAGE_THUNK_DATA32;
    typedef IMAGE_THUNK_DATA32 * PIMAGE_THUNK_DATA32;
    

首先要判断最高位是否为1，如果最高位的值为1，那么去除最高位的值之后，即为函数的导出序号，如果最高位的值不为1，那么这个值就是一个RVA，在转成FOA之后指向`IMAGE_IMPORT_BY_NAME`这个结构

    
    
    typedef struct _IMAGE_IMPORT_BY_NAME {                
        WORD    Hint;                
        BYTE    Name[1];                
    } IMAGE_IMPORT_BY_NAME, *PIMAGE_IMPORT_BY_NAME;
    

Hint为2字节，为当前函数在导出表中的索引，但是这个值一般起不到什么作用。我们思考一下，如果我们最高位值为1是以序号导出，最高位值不为1则以名字导出，而以名字导出的时候我们才会用到`IMAGE_IMPORT_BY_NAME`结构，但是我们按名字导出也就不需要管函数的索引了，所以Hint这个值可以忽略，在一些编译器里面会直接将Hint的值置为0。我们主要是看一下`Name[1]`这个结构，可以看到它是BYTE，大小为1字节，那么有人可能就会问了，函数名1字节能够保证存下吗？这里正是因为考虑到了函数名字长度的不确定性，设计者只将函数开头的1字节存到`Name[1]`这个结构中，函数名是以`\0`结尾的，也就是说在找到`Name[1]`里面所存的首字节后，一直往后遍历，直到找到0即为函数名的结束。

## 绑定导入表

PE在加载前INT、IAT表都指向一个名称表，但是有的exe程序，在打印IAT表的时候，会发现里面是地址。这是因为我们的PE程序在加载的时候，IAT表会填写函数地址。但是这就造成了一个问题，PE程序启动慢，每次启动都要给IAT表填写函数地址。那么这里我们就可以使用到绑定导入表来使PE程序的启动变快。

那么我们还需要注意的一个点就是`TimeDataStamp`，即时间戳。PE加载EXE相关的DLL时，首先会根据`IMAGE_IMPORT_DESCRIPTOR`结构中的`TimeDateStamp`来判断是否要重新计算IAT表中的地址

若`TimeDataStamp == 0` 则未绑定，`TimeDataStamp == -1` 则已绑定

![](https://p1.ssl.qhimg.com/t014e964865aa1454d6.jpg)

一般的PE文件在加载前INT和IAT表中都是指向`IMAGE_IMPORT_BY_NAME`这张表的，也就是说INT表和IAT表在PE加载前表中所存的内容都是一样的，PE在加载后，IAT表里存的才是函数的地址，这种情况就属于没有绑定导入表的情况，即`TimeDataStamp`为0的情况。

我们知道，IAT表的本质是在PE文件加载后存放是函数地址，因为dll存在可能被其他系统dll占用空间的情况出现，所以一般都不会将函数地址直接写在IAT表里面。如果将要使用绑定导入表，最大的优点就是程序的启动速度会变快，因为省去了一个IAT重组的过程，一般windows系统自带的一些exe会选择将导入表绑定，即`TimeDataStamp
= fffffff`，转换为十进制便是0

真正的绑定导入表位于目录的第12项，其中`TimeDataStamp`为真正的时间戳，`OffsetModuleName`为剩余dll的名字，`NumberOfModuleForwarderRefs`为依赖dll的数量。

    
    
    typedef struct _IMAGE_BOUND_IMPORT_DESCRIPTOR {
        DWORD   TimeDateStamp;　　　　　　　　　　　　　　　　//真正的时间戳
        WORD    OffsetModuleName;　　　　　　　　　　　　　　//DLL的名字,PE的文件名
        WORD    NumberOfModuleForwarderRefs;　　　　　　　　//依赖的另外的DLL有几个
    // Array of zero or more IMAGE_BOUND_FORWARDER_REF follows
    } IMAGE_BOUND_IMPORT_DESCRIPTOR,  *PIMAGE_BOUND_IMPORT_DESCRIPTOR;
    

其中要注意的是`OffsetModuleName`这个值有点特殊，它既不是foa，也不是rva，它的计算公式为第一个`DESCRIPTOR`的值加上所在结构体的`OffsetMoudeleName`得到。如果`NumberOfModuleForwarderRefs`的值为2，则绑定导入表一共就有3个dll。

如果`NumberOfModuleForwarderRefs`的值不为0，绑定导入表下面还会跟一张依赖dll的绑定导入表结构，含义的话跟绑定导入表相同，`Reserved`值可以不用管。

    
    
    typedef struct _IMAGE_BOUND_FORWARDER_REF {
        DWORD   TimeDateStamp;
        WORD    OffsetModuleName;
        WORD    Reserved;
    } IMAGE_BOUND_FORWARDER_REF, *PIMAGE_BOUND_FORWARDER_REF;
    

## 代码实现

###  导入表

那么我们这里就对导入表进行代码解析的实现

我们首先定位到导入表，位于数据目录项的第二个结构

    
    
    FileAddress = RvaToFoa((char*)IN_path, pOptionHeader->DataDirectory[1].VirtualAddress) + (DWORD)FileBuffer;
    

定义一个指向导入表的指针

    
    
    pImport = (PIMAGE_IMPORT_DESCRIPTOR)FileAddress;
    

首先输出dll名称，通过指针指向Name结构

    
    
    printf("dll名称:%s\n", (DWORD)FileBuffer + RvaToFoa((char*)IN_path, pImport->Name));
    

再通过指向`OriginalFirstThunk`结构找到INT表的首地址

    
    
    printf("INT表首地址:%x\n", pImport->OriginalFirstThunk);
    

然后判断最高位是否为1，这里使用到于0x80000000相与的方法对最高位进行判断

    
    
            OriginalFT = (PDWORD)((DWORD)FileBuffer + RvaToFoa((char*)path, pImport->OriginalFirstThunk));
            while (*OriginalFT)
            {
                if ((*OriginalFT) & 0x80000000)
                {
                    printf("按序号导入:%x\n", (*OriginalFT) & 0x0FFF);
                }
                else
                {
                    pName = (PIMAGE_IMPORT_BY_NAME)((DWORD)FileBuffer+RvaToFoa((char*)path, *OriginalFT));
                    printf("按名字导入hint/name:%x-%s\n", pName->Hint,pName->Name);
                }
                OriginalFT++;
            }
    

IAT表的打印同理，使用指针指向FirstThunk结构即可

    
    
            FT = (PDWORD)((DWORD)FileBuffer + RvaToFoa((char*)path, pImport->FirstThunk));
            OriginalFT = (PDWORD)((DWORD)FileBuffer + RvaToFoa((char*)path, pImport->OriginalFirstThunk));
            FT = (PDWORD)((DWORD)FileBuffer + RvaToFoa((char*)path, pImport->FirstThunk));
            while (*OriginalFT)
            {
                if ((*OriginalFT) & 0x80000000)
                {
                    printf("按序号导入:%x\n", (*OriginalFT) & 0x0FFF);
                }
                else
                {
                    pName = (PIMAGE_IMPORT_BY_NAME)((DWORD)FileBuffer+RvaToFoa((char*)path, *OriginalFT));
                    printf("按名字导入hint/name:%x-%s\n", pName->Hint,pName->Name);
                }
                OriginalFT++;
            }
    

完整代码如下

    
    
    void PrintImportTable()
    {
        LPVOID FileBuffer = NULL;
        PIMAGE_DOS_HEADER pDosHeader = NULL;
        PIMAGE_NT_HEADERS pNTHeader = NULL;
        PIMAGE_FILE_HEADER pPEHeader = NULL;
        PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;
        PIMAGE_SECTION_HEADER pSectionHeader = NULL;
        PIMAGE_IMPORT_DESCRIPTOR pImport = NULL;
        //OriginalFirstThunk
        PDWORD OriginalFT = NULL;
        //FirstThunk
        PDWORD FT = NULL;
        PIMAGE_IMPORT_BY_NAME pName = NULL;
    
        DWORD FileAddress = NULL;
    
        FileToFileBuffer((char*)IN_path, &FileBuffer);
    
        if (!FileBuffer)
        {
            printf("File->FileBuffer失败");
            return;
        }
    
        pDosHeader = (PIMAGE_DOS_HEADER)FileBuffer;
        pNTHeader = (PIMAGE_NT_HEADERS)((DWORD)pDosHeader + pDosHeader->e_lfanew);
        pPEHeader = (PIMAGE_FILE_HEADER)((DWORD)pNTHeader + 4);
        pOptionHeader = (PIMAGE_OPTIONAL_HEADER32)((DWORD)pPEHeader + IMAGE_SIZEOF_FILE_HEADER);
        FileAddress = RvaToFoa((char*)IN_path, pOptionHeader->DataDirectory[1].VirtualAddress) + (DWORD)FileBuffer;
        pImport = (PIMAGE_IMPORT_DESCRIPTOR)FileAddress;
    
        for( ;pImport->FirstThunk || pImport->OriginalFirstThunk;pImport++)
        {
            printf("dll名称:%s\n", (DWORD)FileBuffer + RvaToFoa((char*)IN_path, pImport->Name));
            printf("INT表首地址:%x\n", pImport->OriginalFirstThunk);
            OriginalFT = (PDWORD)((DWORD)FileBuffer + RvaToFoa((char*)IN_path, pImport->OriginalFirstThunk));
            FT =(PDWORD)((DWORD)FileBuffer + RvaToFoa((char*)IN_path, pImport->FirstThunk));
            while (*OriginalFT)
            {
                if((*OriginalFT) & 0x80000000)
                {
                    printf("按序号导入:%x\n" , (*OriginalFT) & 0x0FFF);
                }
                else
                {
                    pName = (PIMAGE_IMPORT_BY_NAME)((DWORD)FileBuffer + RvaToFoa((char*)IN_path, *OriginalFT));
                    printf("按名字导入<hint/name>:%x/%s\n", pName->Hint, pName->Name);
                }
                OriginalFT++;
            }
            printf("IAT表首地址:%x\n" , pImport->FirstThunk);
            while (*FT)
            {
                if((*FT) & 0x80000000)
                {
                    printf("按序号导入:%x\n" , (*FT) & 0x7FFFFFFF);
                }
                else
                {
                    pName = (PIMAGE_IMPORT_BY_NAME)((DWORD)FileBuffer + RvaToFoa((char*)IN_path, *FT));
                    printf("按名字导入<hint/name>:%x/%s\n", pName->Hint, pName->Name);
                }
                FT++;
            }
    
    
        }
        free(FileBuffer);
    
    }
    

实现效果如下

![](https://p3.ssl.qhimg.com/t01e4e59bcc9ceca696.jpg)

![](https://p0.ssl.qhimg.com/t0198ed2a20f7b76f77.jpg)

###  绑定导入表

我们再来进行绑定导入表的代码解析，首先还是看一下绑定导入表的结构

    
    
    typedef struct _IMAGE_BOUND_IMPORT_DESCRIPTOR {
        DWORD   TimeDateStamp;　　　　　　　　　　　　　　　　//真正的时间戳
        WORD    OffsetModuleName;　　　　　　　　　　　　　　//DLL的名字,PE的文件名
        WORD    NumberOfModuleForwarderRefs;　　　　　　　　//依赖的另外的DLL有几个
    // Array of zero or more IMAGE_BOUND_FORWARDER_REF follows
    } IMAGE_BOUND_IMPORT_DESCRIPTOR,  *PIMAGE_BOUND_IMPORT_DESCRIPTOR;
    

之前我们分析过了绑定导入表的结构，位于数据目录项的第12位，那么我们首先定义一个指针指向绑定导入表

    
    
    pBoundImport = (PIMAGE_BOUND_IMPORT_DESCRIPTOR)(RvaToFoa((char*)IN_path, pOptionHeader->DataDirectory[11].VirtualAddress) + (DWORD)FileBuffer);
    

我们之前提到了，如果绑定导入表的值为1的时候，才表示已绑定，绑定导入表才会有意义，那么我们首先就需要进行判断

    
    
    if (pImport->TimeDateStamp != 0)
    

若`TimaDateStamp`的值不为0才继续向下解析，然后就是定义好的指针指向绑定导入表里面的几个结构

    
    
                printf("时间戳:%x\n", ptempBoundImport->TimeDateStamp);
                printf("名称:%s\n", (PBYTE)((DWORD)ptempBoundImport + ptempBoundImport->OffsetModuleName));
                printf("还用到了%x个其他dll\n", ptempBoundImport->NumberOfModuleForwarderRefs);
    

当`NumberOfModuleForwarderRefs`的值不为0时，绑定导入表下面还会跟一张依赖dll的绑定导入表结构，含义的话跟绑定导入表相同，那么我们再定义一个指针与之前指向绑定导入表的指针相同即可

    
    
    ptempBoundImport = pBoundImport;
    

然后再使用一个for循环遍历ref结构

    
    
                for (DWORD i = 0; i < pBoundImport->NumberOfModuleForwarderRefs; i++, ptempBoundImport1++)
                {
                    printf("时间戳:%x\n", ptempBoundImport1->TimeDateStamp);
                    printf("名称:%s\n", (PBYTE)((DWORD)pBoundImport + ptempBoundImport1->OffsetModuleName));
                }
    

完整代码如下

    
    
    void printBoundImporttable()
    {
        PIMAGE_BOUND_IMPORT_DESCRIPTOR pBoundImport = NULL;
        PIMAGE_BOUND_IMPORT_DESCRIPTOR ptempBoundImport = NULL;
        PIMAGE_BOUND_FORWARDER_REF ptempBoundImport1 = NULL;
        //OriginalFirstThunk
        PDWORD OriginalFT = NULL;
        //FirstThunk
        PDWORD FT = NULL;
        PIMAGE_IMPORT_BY_NAME pName = NULL;
    
        DWORD FileAddress = NULL;
    
        FileToFileBuffer((char*)IN_path, &FileBuffer);
    
        if (!FileBuffer)
        {
            printf("File->FileBuffer失败");
            return;
        }
        pBoundImport = (PIMAGE_BOUND_IMPORT_DESCRIPTOR)(RvaToFoa((char*)IN_path, pOptionHeader->DataDirectory[11].VirtualAddress) + (DWORD)FileBuffer);
        ptempBoundImport = pBoundImport;
        while (pBoundImport->OffsetModuleName && pBoundImport->TimeDateStamp)
        {
            if (pImport->TimeDateStamp != 0)
            {
                printf("时间戳:%x\n", ptempBoundImport->TimeDateStamp);
                printf("名称:%s\n", (PBYTE)((DWORD)ptempBoundImport + ptempBoundImport->OffsetModuleName));
                printf("还用到了%x个其他dll\n", ptempBoundImport->NumberOfModuleForwarderRefs);
                ptempBoundImport1 = (PIMAGE_BOUND_FORWARDER_REF)(ptempBoundImport++);
                for (DWORD i = 0; i < pBoundImport->NumberOfModuleForwarderRefs; i++, ptempBoundImport1++)
                {
                    printf("时间戳:%x\n", ptempBoundImport1->TimeDateStamp);
                    printf("名称:%s\n", (PBYTE)((DWORD)pBoundImport + ptempBoundImport1->OffsetModuleName));
                }
            }
        }
        free(FileBuffer);
    
    
    }
    

实现效果如下

![](https://p3.ssl.qhimg.com/t01914cf08b4ecdbc0f.jpg)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Drunkmars** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/264297](/post/id/264297)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [win32](/tag/win32)

 **+1** __3赞

 __收藏

![](https://p0.ssl.qhimg.com/t019bb9b9add2982923.jpg) Drunkmars

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

