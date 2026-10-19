# 深入理解win32（六）

阅读量 **199771**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-28 15:30:16

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01e94717568627114f.jpg)

## 前言

我们在上一节通过跟入od破解了一个简单的小程序以及了解了如何提取图标和寻找标题在资源文件中的位置，其中资源部分的一个重要的结构 —
资源表。在pe结构中最复杂的一个表便是资源表，在win32层面我们要做的操作其实都离不开pe结构，所以在这里我们首先要对pe文件中几个重要的表进行了解并用代码进行解析，这一节我们首先了解的是导出表和重定位表。

## 导出表

导出表的基本概念如下：

> 导出表是PE文件为其他应用程序提供自身的一些变量、函数以及类，将其导出给第三方程序使用的一张清单，里面包含了可以导出的元素。

1、exe程序一般只有导入表，但并不是一定，有可能也有导出表  
2、dll程序一般导出表和导入表都有

一个可执行程序是由一堆PE文件构成的，我加载的是一个.exe，但是后面还有需要的.dll文件，大家都知道.dll也有PE文件，这里也就又有一个问题了，为什么要引入这么多的.dll文件呢？

因为一个exe还需要使用这些.dll中所提供的函数，这些dll中就有相应的导出表，然后exe用LoadLibrary动态加载，最后通过GetProcAddress到获取函数的地址。

![](https://p4.ssl.qhimg.com/t014d1cff7ac9195c9e.jpg)

首先我们在PE Format里面看一下导出表的具体定位，导出表位于数据目录项的第一个结构

![](https://p1.ssl.qhimg.com/t0145b045602f42aa63.jpg)

    
    
    typedef struct _IMAGE_DATA_DIRECTORY {
    
    DWORD VirtualAddress;
    
    DWORD Size;
    
    } IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;
    

这里的VirtualAddress为导出表的RVA，首先了解一下RVA跟FOA之间的区别

> RVA: RVA就是相对虚拟偏移，就是偏移地址，例如  
>  0x1000，虚拟地址0x00401000的RVA就是0x1000，RVA = 虚拟地址-ImageBase
>
> FOA: 文件偏移，就是文件中所在的地址

可以通俗的这么理解：在可执行文件运行之前需要在内存空间中展开，在内存空间中的地址就是RVA，在可执行文件没有运行的时候就是FOA

而Size就是导出表的大小，在这个地方的结构只是说明了导出表在内存中所存在的地址以及导出表的大小，并不是真正的导出表，那么这里我们就需要通过RVA去找到导出表真正存在的地址。

通过地址得到真正导出表的结构如下

    
    
    typedef struct _IMAGE_EXPORT_DIRECTORY {
    
    DWORD Characteristics; // 未使用
    
    DWORD TimeDateStamp; // 时间戳
    
    WORD MajorVersion; // 未使用
    
    WORD MinorVersion; // 未使用
    
    DWORD Name; // 指向该导出表文件名字符串
    
    DWORD Base; // 导出函数起始序号
    
    DWORD NumberOfFunctions; // 所有导出函数的个数
    
    DWORD NumberOfNames; // 以函数名字导出的函数个数
    
    DWORD AddressOfFunctions; // 导出函数地址表RVA
    
    DWORD AddressOfNames; // 导出函数名称表RVA
    
    DWORD AddressOfNameOrdinals; // 导出函数序号表RVA
    
    } IMAGE_EXPORT_DIRECTORY, *PIMAGE_EXPORT_DIRECTORY;
    

这里我们要关注的是NumberOfFunction、NumberOfNames以及AddressOfFunctions、AddressOfNames、AddressOfNameOrdinals

在导出表里面有两种方式进行导出，分别是以名字导出、以序号导出

AddressOfFunctions、AddressOfNames、AddressOfNameOrdinal这三个RVA指向的是三个存放了函数具体地址的表，如下图所示，其中AddressOfFunctions存放的地址数量由NumberOfFuntions决定，AddressOfNameOrdinals和AddressOfNames存放的地址数量由NumberOfNames来决定

![](https://p2.ssl.qhimg.com/t017a3494131fe9d7d9.png)

首先我们来看AddressOfNames，这个表里面的宽度为4字节，即0x12345678，存放的地址也为rva，在这个表里面，名称是按字符顺序排序的，例如有一个函数名称为apple，另外一个函数名称为bee，那么apple的rva就在这个表里面的第一项，bee的rva就在这个表里面的第二项，但是这个可能并不是函数真正的名字，如下图所示

![](https://p3.ssl.qhimg.com/t01361949c9c5815a28.jpg)

我们再看AddressOfNameOrdinals，这个表里面的宽度为2字节，存放的地址也为rva，通过这个表里面的内容加上Base就可以得到函数的导出序号

我们最后来看AddressOfFunctions，这个表里面的宽度也是4字节，存放的是所有导出函数的地址，这个地址也是rva，所以要想得到真正的地址需要加上ImageBase

那么我们就可以得到：  
在按名称导入的情况下，首先查询AddressOfName这个表，得到一个指向函数序号表的地址，在这个地址里面又有一个序号，这个序号对应的就是AddressOfFunctions里面的序号，得到AddressOfFunctions对应序号里面的rva之后，加上ImageBase，即可以得到真正的导出函数的地址

如果是按序号导入的情况下，就不需要查询AddressOfNames这个表，直接去查AddressOfFunctions这个表，通过序号 –
Base得到与AddressOfFunctions里面对应的序号，拿到rva之后，加上ImageBase，即可以得到真正导出函数的地址

那么总结如下：

> 以名字导出  
>
> 首先遍历名字表，用名字表中的地址找字符串，与目标字符串比对。如果找到字符串一样的，得到该处的索引。按照相同的索引号从序号表中找到序号值，再通过序号值为索引，从地址表中找到目标函数的地址。
>
> 以序号导出  
>  用目标序号-BASE，得到一个值，直接用这个值为索引，从地址表中找函数的地址。

这里导入表分为AddressOfFunctions、AddressOfNames、AddressOfNameOrdinal三个表的主要原因是因为函数导出的个数跟函数名的个数未必一样，所以就需要把函数地址表跟函数名称表分开。

关于以名字导出的情况，我们有以下几个注意的点，首先我们看一看图

![](https://p4.ssl.qhimg.com/t01ac68a8fe3dd0e080.jpg)

>
> AddressOfFuctions和AddressOfNames大小不一定相等，而AddressOfFuctions也不一定比AddressOfNames大，因为可能存在AddressOfNames里的两个名字指向同一个地址的情况
>
>
> AddressOfNameOrdinals与Base关联紧密，Base取的是函数序列表里面的最小值，而寻找AddressOfFuctions则是用AddressOfNameOrdinals里面的数字减去Base得到
>
>
> NumberOfNames不准确，它的计算方法是用AddressOfNameOrdinals里面的最大值减去最小值后加1，但是这就出现了一个问题，可能表里面的值不是按序号排列的（即2.3.5.6），就会导致不准确的情况发生
>
>
> 接以上原理，因为NumberOfNames不准确，导致用名字寻址的方法取找AddressOfFuctions时就可能出现找不到的情况，所以AddressOfFuctions里面的值可以为0

那么了解了导入表的原理，我们就可以编写代码来解析导出表并打印信息

首先是需要编写一个FileBuffer转换为ImageBuffer以及FOA转换成ROA的函数，如下所示

    
    
    DWORD FileBufferToImageBuffer(IN LPVOID pFileBuffer, OUT LPVOID* pImageBuffer)
    {
        if (pFileBuffer == NULL)
        {
            printf("PE文件读取失败");
            return 0;
        }
    
        if (*(PWORD)pFileBuffer != IMAGE_DOS_SIGNATURE)
        {
            printf("不是有效的MZ头");
            return 0;
        }
    
        LPVOID p1ImageBuffer = NULL;
        PIMAGE_DOS_HEADER pDosHeader = NULL;
        PIMAGE_NT_HEADERS pNTHeader = NULL;
        PIMAGE_FILE_HEADER pPEHeader = NULL;
        PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;
        PIMAGE_SECTION_HEADER pSectionHeader = NULL;
        pDosHeader = (PIMAGE_DOS_HEADER)pFileBuffer;
    
        if (*(PDWORD)((DWORD)pFileBuffer + pDosHeader->e_lfanew) != IMAGE_NT_SIGNATURE)
        {
            printf("不是有效的PE签名");
            free(pFileBuffer);
            return 0;
        }
    
        pNTHeader = (PIMAGE_NT_HEADERS)((DWORD)pFileBuffer + pDosHeader->e_lfanew);
    
        pPEHeader = (PIMAGE_FILE_HEADER)((DWORD)pNTHeader + 4);
    
        pOptionHeader = (PIMAGE_OPTIONAL_HEADER32)((DWORD)pPEHeader + IMAGE_SIZEOF_FILE_HEADER);
    
        pSectionHeader = (PIMAGE_SECTION_HEADER)((DWORD)pOptionHeader + pPEHeader->SizeOfOptionalHeader);
    
        p1ImageBuffer = malloc(pOptionHeader->SizeOfImage);
    
        if (!p1ImageBuffer)
        {
            printf("申请ImageBuffer堆空间失败");
            return 0;
        }
    
        memset(p1ImageBuffer, 0, pOptionHeader->SizeOfImage);
        memcpy(p1ImageBuffer, pFileBuffer, pOptionHeader->SizeOfHeaders);
        PIMAGE_SECTION_HEADER ptempSectionHeader = pSectionHeader;
    
        for (int k = 0; k < pPEHeader->NumberOfSections; k++)
        {
            memcpy((void*)((DWORD)p1ImageBuffer+ ptempSectionHeader->VirtualAddress), (void*)((DWORD)pFileBuffer + ptempSectionHeader->PointerToRawData), ptempSectionHeader->SizeOfRawData);
            //printf("%x\n", ptempSectionHeader->SizeOfRawData);
            ptempSectionHeader++;
        }
    
        *pImageBuffer = p1ImageBuffer;
        ptempSectionHeader = NULL;
        return pOptionHeader->SizeOfImage;
    }
    
    DWORD FoaToRva(IN LPSTR PATH,IN DWORD Foa)
    {
        LPVOID FileBuffer = NULL;
        LPVOID ImageBuffer = NULL;
        LPVOID NewBuffer = NULL;
        PIMAGE_DOS_HEADER pDosHeader = NULL;
        PIMAGE_NT_HEADERS pNTHeader = NULL;
        PIMAGE_FILE_HEADER pPEHeader = NULL;
        PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;
        PIMAGE_SECTION_HEADER pSectionHeader = NULL;
        DWORD Rva = 0;
    
        FileToFileBuffer(PATH,&FileBuffer);
    
        if (!FileBuffer)
        {
            printf("File->FileBuffer失败");
            return 0;
        }
    
        FileBufferToImageBuffer(FileBuffer, &ImageBuffer);
        if (!ImageBuffer)
        {
            printf("FileBUffer->ImageBuffer失败");
            return 0;
        }
    
        pDosHeader = (PIMAGE_DOS_HEADER)ImageBuffer;
        pNTHeader = (PIMAGE_NT_HEADERS)((DWORD)pDosHeader + pDosHeader->e_lfanew);
        pPEHeader = (PIMAGE_FILE_HEADER)((DWORD)pNTHeader + 4);
        pOptionHeader = (PIMAGE_OPTIONAL_HEADER32)((DWORD)pPEHeader + IMAGE_SIZEOF_FILE_HEADER);
        pSectionHeader = (PIMAGE_SECTION_HEADER)((DWORD)pOptionHeader + pPEHeader->SizeOfOptionalHeader);
    
        PIMAGE_SECTION_HEADER ptempSectionHeader = pSectionHeader;
        PIMAGE_SECTION_HEADER ptempSectionHeader1 = pSectionHeader;
    
        for (int i = 0; i < pPEHeader->NumberOfSections; i++, ptempSectionHeader++);
        if ( Foa <= FileAlignment((DWORD)ptempSectionHeader) - ((DWORD)FileBuffer))
        {
            Rva = Foa;
            free(FileBuffer);
            return Rva;
        }
    
        for (int k = 0 ; k < pPEHeader->NumberOfSections - 1 ; k++)
        {
            if (ptempSectionHeader1->PointerToRawData < Foa && (ptempSectionHeader1 + 1) ->PointerToRawData)
            {
                Rva = ptempSectionHeader1->VirtualAddress + (Foa - ptempSectionHeader1->PointerToRawData);
                free(FileBuffer);
                return Rva;
            }
            if (ptempSectionHeader1->PointerToRawData == Foa)
            {
                Rva = Foa;
                free(FileBuffer);
                return Rva;
            }
            ptempSectionHeader1++;
        }
    
        if (ptempSectionHeader1->PointerToRawData <= Foa)
        {
            Rva = ptempSectionHeader1->VirtualAddress + (Foa - ptempSectionHeader1->PointerToRawData);
            free(FileBuffer);
            return Rva;
        }
        free(FileBuffer);
        return 0;    
    }
    

然后根据以上原理解析导出表

    
    
    void PrintExportDirectory()
    {
        LPVOID FileBuffer = NULL;
        PIMAGE_DOS_HEADER pDosHeader = NULL;
        PIMAGE_NT_HEADERS pNTHeader = NULL;
        PIMAGE_FILE_HEADER pPEHeader = NULL;
        PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;
        PIMAGE_SECTION_HEADER pSectionHeader = NULL;
    
        PIMAGE_EXPORT_DIRECTORY pexport = NULL;
        DWORD FileAddress = NULL;
        PDWORD AddressName = NULL;
        PWORD AddressOrdinals = NULL;
        PDWORD AddressFunction = NULL;
    
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
    
    
        FileAddress = RvaToFoa((char*)IN_path,pOptionHeader->DataDirectory[0].VirtualAddress) + (DWORD)FileBuffer;
        pexport = (PIMAGE_EXPORT_DIRECTORY)FileAddress;
        AddressOrdinals = (PWORD)(RvaToFoa((char*)IN_path,pexport->AddressOfNameOrdinals) + (DWORD)FileBuffer);
        AddressName = (PDWORD)(RvaToFoa((char*)IN_path, pexport->AddressOfNames) + (DWORD)FileBuffer);
        AddressFunction = (PDWORD)(RvaToFoa((char*)IN_path, pexport->AddressOfFunctions) + (DWORD)FileBuffer);
    
        printf("Characteristics:%x\n\n", pexport->Characteristics);
        printf("timedatestamp:%x\n\n", pexport->TimeDateStamp);
        printf("Name:%x\n\n", pexport->Name);
        printf("Base:%x\n\n", pexport->Base);
        printf("NumberOfFunctions:%x\n\n", pexport->NumberOfFunctions);
        printf("NumberOfNames:%x\n\n", pexport->NumberOfNames);
        printf("AddressOfFunctions(函数地址):%x\n\n", pexport->AddressOfFunctions);
        printf("AddressOfNameOrdinals(序号):%x\n\n", pexport->AddressOfNameOrdinals);
        printf("AddressOfNames(存储的是名字的地址):%x\n\n", pexport->AddressOfNames);
    
        printf("*************函数地址表**************\n");
        for (DWORD i = 0; i < pexport->NumberOfFunctions; i++)
        {
            printf("函数地址:%x\n", *AddressFunction);
            AddressFunction++;
        }
    
        printf("*************函数序号表**************\n");
        for (DWORD j = 0; j < pexport->NumberOfNames; j++)
        {
            printf("序号:%x\n", *AddressOrdinals);
            AddressOrdinals++;
        }
    
        printf("*************函数名称表**************\n"); 
        for (DWORD k = 0; k < pexport->NumberOfNames; k++)
        {
            printf("函数名称:%s\n", (DWORD)FileBuffer + RvaToFoa((char*)IN_path, *AddressName));
            AddressName++;
        }
    }
    

结果如下所示

![](https://p4.ssl.qhimg.com/t01e745b74f35a916dd.jpg)

![](https://p4.ssl.qhimg.com/t014d5b57f8bf128f7d.png)

## 重定位表

重定位表（Relocation Table）用于在程序加载到内存中时，进行内存地址的修正。

为什么要进行内存地址的修正？我们举个例子来说：test.exe可执行程序需要三个动态链接库dll（a.dll，b.dll，c.dll），假设test.exe的ImageBase为400000H，而a.dll、b.dll、c.dll的基址ImageBase均为1000000H。

那么操作系统的加载程序在将test.exe加载进内存时，直接复制其程序到400000H开始的虚拟内存中，接着一一加载a.dll、b.dll、c.dll：假设先加载a.dll，如果test.exe的ImageBase
+ SizeOfImage +
1000H不大于1000000H，则a.dll直接复制到1000000H开始的内存中；当b.dll加载时，虽然其基址也为1000000H，但是由于1000000H已经被a.dll占用，则b.dll需要重新分配基址，比如加载程序经过计算将其分配到1200000H的地址，c.dll同样经过计算将其加载到150000H的地址。如下图所示：

![](https://p3.ssl.qhimg.com/t015904df766b35eef2.jpg)

但是b.dll和c.dll中有些地址是根据ImageBase固定的，被写死了的，而且是绝对地址不是相对偏移地址。比如b.dll中存在一个call
0X01034560，这是一个绝对地址，其相对于ImageBase的地址为 0X01034560 – 0X01000000 =
0X34560H；而此时的内存中b.dll存在的地址是1200000H开始的内存，加载器分配的ImageBase和b.dll中原来默认的ImageBase（1000000H）相差了200000H，因此该call的值也应该加上这个差值，被修正为0X01234560H，那么0X01234560H
– 0X01200000H =
0X34560H则相对不变。否则call的地址不修正会导致call指令跳转的地址不是实际要跳转的地址，获取不到正确的函数指令，程序则不能正常运行。

由于一个dll中的需要修正的地址不止一两个，可能有很多，所以用一张表记录那些“写死”的地址，将来加载进内存时，可能需要一一修正，这张表称作为重定位表，一般每一个PE文件都有一个重定位表。当加载器加载程序时，如果加载器为某PE（.exe、.dll）分配的基址与其自身默认记录的ImageBase不相同，那么该程序文件加载完毕后就需要修正重定位表中的所有需要修正的地址。如果加载器分配的基址和该程序文件中记录默认的ImageBase相同，则不需要修正，重定位表对于该dll也是没有效用的。比如test.exe和a.dll的重定位表都是不起作用的（由于一般情况.exe运行时被第一个加载，所以exe文件一般没有重定位表，但是不代表所有exe都没有重定位表）。同理如果先加载b.dll后加载a.dll、c.dll，那么b.dll的重定位表就不起作用了。

初步了解了重定位表之后，我们来看看重定位表在PE里面的结构，重定位表位于数据目录项的第6个结构

    
    
    typedef struct _IMAGE_DATA_DIRECTORY {
        DWORD   VirtualAddress;
        DWORD   Size;
    } IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;
    

跟导出表相同，VirtualAddress存放的是指向真正重定位表地址的rva，而Size重定位表的大小，通过RVA->FOA在FileBuffer定位后得到真正重定位表的结构如下：

    
    
    typedef struct _IMAGE_BASE_RELOCATION {
        DWORD   VirtualAddress;
        DWORD   SizeOfBlock;
    } IMAGE_BASE_RELOCATION;
    typedef IMAGE_BASE_RELOCATION ，* PIMAGE_BASE_RELOCATION;
    

这里的VirtualAddress还是RVA，SizeOfBlock则是重定位表的核心结构，存储的值以字节为单位，表示的是重定位表的大小，那么如果我们要知道重定位表结构的数量该怎么办呢？

这里规定在最后一个结构的VirtualAddress和SizeOfBlock的值都为0，这里就可以进行判断来获取重定位表有多少个结构

我们来看一看直观的重定位表图，假设我们这里重定位结构的数量为3，那么在最后8字节即VirtualAddress和SizeOfBlock的值都为0，可以说重定位表就是很多个块结构所构成的。

![](https://p4.ssl.qhimg.com/t01d396b72be9f41959.jpg)

在每一块结构的VirtualAddress和SizeOfBlock里面，都有很多宽度为2字节的十六进制数据，这里我们称他们为具体项。在内存中页大小的值为1000H，即2的12次方，也就是通过这个1000H就能够表示出一个页里面所有的偏移地址。而具体项的宽度为16位，页大小的值为低12位，那么高4位是用来表示什么呢？

这里高4位只可能有两种情况，0011或0000，对应的十进制就是3或0。

当高4位的值为0011的时候，我们需要修复的数据地址就是VirtualAddress +
低12位的值。例如这里我的VirtualAddress是0x12345678，具体项的数值为001100000001，那么这个值就是有意义的，需要修改的RVA
= 0x12345678+0x00000001 = 0x12345679。

当高4位的值为0000的时候，这里就不需要进行重定位的修改，这里的具体项只是用于数据对齐的数据。

也就是说，我们如果要进行重定位表的修改，就只需要判断具体项的高4位是否为0011，若是则进行重定位表的修复即可

那么根据以上原理我们来进行重定位表的解析

    
    
    void PrintRelocationTable()
    {
        LPVOID FileBuffer = NULL;
        PIMAGE_DOS_HEADER pDosHeader = NULL;
        PIMAGE_NT_HEADERS pNTHeader = NULL;
        PIMAGE_FILE_HEADER pPEHeader = NULL;
        PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;
        PIMAGE_DATA_DIRECTORY DataAddress = NULL;
        PIMAGE_BASE_RELOCATION AddressReloc = NULL;
    
        PWORD p = NULL;
        FileToFileBuffer((char*)IN_path, &FileBuffer);
    
        if (!FileBuffer)
        {
            printf("File->FileBuffer失败!");
            return;
        }
        pDosHeader = (PIMAGE_DOS_HEADER)FileBuffer;
        pNTHeader = (PIMAGE_NT_HEADERS)((DWORD)pDosHeader + pDosHeader->e_lfanew);
        pPEHeader = (PIMAGE_FILE_HEADER)((DWORD)pNTHeader + 4);
        pOptionHeader = (PIMAGE_OPTIONAL_HEADER32)((DWORD)pPEHeader + IMAGE_SIZEOF_FILE_HEADER);
    
        DataAddress = pOptionHeader -> DataDirectory;
        AddressReloc = (PIMAGE_BASE_RELOCATION)((DWORD)FileBuffer + RvaToFoa((char*)IN_path, (DataAddress + 5) ->VirtualAddress));
        for (DWORD i = 0;AddressReloc->VirtualAddress || AddressReloc->SizeOfBlock; i++)
        {
            printf("***************此为重定位表的第%x块***************\n",i+1);
            printf("VirtualAddress:%x\n",AddressReloc->VirtualAddress);
            printf("SizeOfBlock:%x\n",AddressReloc->SizeOfBlock);
            p = (PWORD)AddressReloc + 4;
    
            for (DWORD i = 0 ; k < (AddressReloc->SizeOfBlock - 8) / 2 ; i++,p++)
            {
                printf("地址:%x,属性:%x\n",AddressReloc->VirtualAddress + (0xFFF & *p),(0xF000 & *p) >>12);
            }
    
            AddressReloc = (PIMAGE_BASE_RELOCATION)((DWORD)AddressReloc + AddressReloc->SizeOfBlock);
        }
    }
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Drunkmars** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/262543](/post/id/262543)

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

