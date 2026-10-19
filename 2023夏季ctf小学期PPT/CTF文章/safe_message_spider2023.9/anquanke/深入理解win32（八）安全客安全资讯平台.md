# 深入理解win32（八）

阅读量 **104805**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-10 14:30:07

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01e94717568627114f.jpg)

## 前言

在上一节里面我们对导入表以及绑定导入表进行了了解以及代码解析，在这一节里面我们来对PE结构中比较复杂的一个表 — 资源表来进行了解。

## 资源表

资源表是PE所有表里边最复杂的表，造成资源表复杂是有历史原因的，简单说就是微软设计PE的时候错误的以为只要定义16位中的资源类型就够了，后来发现远远不够，但是PE结构已经定下来了，只能在原有基础上修改，因此就造成了资源表这块比较不好理解。

所谓的不好理解，就是它里边用到的结构，其中的属性会出现位段/位域的用法，同一个4字节，要根据高位判断它到底是一个整数还是一个偏移；然后偏移并不是RVA，而是相对于资源表的偏移。

首先我们来看一下资源表在PE里面的位置，位于数据目录项的第三个

![](https://p0.ssl.qhimg.com/t01713745a54a6d6d1b.jpg)

资源目录的结构如下

    
    
    typedef struct _IMAGE_RESOURCE_DIRECTORY {                                
        DWORD   Characteristics;                        //资源属性  保留 0        
        DWORD   TimeDateStamp;                        //资源创建的时间        
        WORD    MajorVersion;                        //资源版本号 未使用 0        
        WORD    MinorVersion;                        //资源版本号 未使用 0        
        WORD    NumberOfNamedEntries;                        //以名称命名的资源数量        
        WORD    NumberOfIdEntries;                        //以ID命名的资源数量        
    //  IMAGE_RESOURCE_DIRECTORY_ENTRY DirectoryEntries[];                                
    } IMAGE_RESOURCE_DIRECTORY, *PIMAGE_RESOURCE_DIRECTORY;
    

在资源表里面有很多属性是保留或者未使用的，我们只需要关注`NumberOfNamedEntries`和`NumberOfIdEntries`这两个结构，与导入导出表相似，资源表也是根据以ID命名和以名称命名来统计具体资源的个数的

但是这并不是资源表的真正结构，资源表的真正结构如下所示

![](https://p5.ssl.qhimg.com/t0134d9b519e57dc697.jpg)

其中每一层都有一个资源目录这个结构，这个结构的意义就是用来统计有多少个`IMAGE_RESOURCE_DIRECTORY_ENTRY`结构，如下所示

    
    
    typedef struct _IMAGE_RESOURCE_DIRECTORY_ENTRY {                                
        union {                        //目录项的名称、或者ID        
            struct {                                
                DWORD NameOffset:31;                                
                DWORD NameIsString:1;                                
            };                                
            DWORD   Name;                                
            WORD    Id;                                
        };                                
        union {                                
            DWORD   OffsetToData;                        //目录项指针        
            struct {                                
                DWORD   OffsetToDirectory:31;                                
                DWORD   DataIsDirectory:1;                                
            };                                
        };                                
    } IMAGE_RESOURCE_DIRECTORY_ENTRY, *PIMAGE_RESOURCE_DIRECTORY_ENTRY;
    

`IMAGE_RESOURCE_DIRECTORY_ENTRY`这个结构在每一层里面的含义都是不相同的，如图所示，在第一层里面用来判断资源的类型，第二层里面用来判断资源的编号，第三层里面表示的是代码页

我们继续探究`IMAGE_RESOURCE_DIRECTORY_ENTRY`这个结构里面的值，首先是第一个联合体，占4字节

    
    
        union {                        //目录项的名称、或者ID        
            struct {                                
                DWORD NameOffset:31;                                
                DWORD NameIsString:1;                                
            };                                
            DWORD   Name;                                
            WORD    Id;                                
        };
    

看一下这里`DWORD NameOffset:31;`和`DWORD
NameIsString:1;`这两个值，`NameOffset:31`就是表示占低31位，而`NameIsString`则占剩下的1位，之前提到过在第一层里面`Name`表示的就是资源类型，那么什么是资源类型呢？每种资源有类型及名字，它们是数值标识符或字符串。windows定义了十六种预定义类型，如光标对应1，位图对应2，图标对应3等等。而资源类型既可以用序号表示，也可以用字符串表示，那么我们该如何判断资源类型到底用什么表示呢？这里就需要看`NameIsString`的值了

当最高位为1时，即`NameIsString = 1`
时，低31位为一个UNICODE指针，指向`_IMAGE_RESOURCE_DIR_STRING_U`结构，在这个结构里面`Length`表示长度，`NameString[1]`表示的是真正UNICODE起始的地址

    
    
    typedef struct _IMAGE_RESOURCE_DIR_STRING_U {                        
        WORD    Length;                        
        WCHAR   NameString[ 1 ];                        
    } IMAGE_RESOURCE_DIR_STRING_U, *PIMAGE_RESOURCE_DIR_STRING_U;
    

当最高位为0时，表示字段的值作为ID使用

再就是第二个联合体，作为目录项指针，这个结构的作用就是指向第二层的结构地址

    
    
        union {                                
            DWORD   OffsetToData;                        //目录项指针        
            struct {                                
                DWORD   OffsetToDirectory:31;                                
                DWORD   DataIsDirectory:1;                                
            };                                
        };
    

当这里有一个注意的点就是`OffsetToData`这个值并不是一个RVA，当`OffsetToData`的最高位为1时，这里需要用资源表的起始地址加上`OffsetToData`的低31位得到的内存地址，就是第二层结构所在的起始地址，若最高位为0，则指向`IMAGE_RESOURCE_DATA_ENTRY`结构

来到第二层过后，还是跟第一层相同的`IMAGE_RESOURCE_DIRECTORY`跟`IMAGE_RESOURCE_DIRECTORY_ENTRY`结构，这时候的`Name`字段表示的就是资源的编号了，可以理解为有几个资源的意思，我们用  
程序来看一下，这里相当于第二层就有4个`IMAGE_RESOURCE_DIRECTORY_ENTRY`结构，解析的方法跟第一层相同，判断最高位的值是否为1来判断是字符串还是序号。

![](https://p1.ssl.qhimg.com/t011f829b9fd60b6cde.jpg)

然后第二个联合体的解析方法也跟第一层的相似，这里若最高位为1，通过第二层的起始地址加上`OffsetToData`的低31位得到的内存地址即可指向第三层结构所在的起始地址

    
    
        union {                                
            DWORD   OffsetToData;                        //目录项指针        
            struct {                                
                DWORD   OffsetToDirectory:31;                                
                DWORD   DataIsDirectory:1;                                
            };                                
        };
    

得到第三层结构的起始地址后，还是跟第一层、第二层相同的`IMAGE_RESOURCE_DIRECTORY`跟`IMAGE_RESOURCE_DIRECTORY_ENTRY`结构，这里的`Name`字段表示的就是代码页，那么什么是代码页呢？

>
> 代码页是字符集编码的别名，也有人称”内码表”。早期，代码页是IBM称呼电脑BIOS本身支持的字符集编码的名称。当时通用的操作系统都是命令行界面系统，这些操作系统直接使用BIOS供应的VGA功能来显示字符，操作系统的编码支持也就依靠BIOS的编码。现在这BIOS代码页被称为OEM代码页。图形操作系统解决了此问题，图形操作系统使用自己字符呈现引擎可以支持很多不同的字符集编码。  
>
> 早期IBM和微软内部使用特别数字来标记这些编码，其实大多的这些编码已经有自己的名称了。虽然图形操作系统可以支持很多编码，很多微软程序还使用这些数字来点名某编码。

这里通俗点来说的话，就是每个国家自己的语言都有一个代码页，简体中文的代码页编号就是2052，如下所示

![](https://p5.ssl.qhimg.com/t010df8fab04cabd231.jpg)

还是通过第一个联合体判断是以字符串还是以数值表示，然后第二个联合体也跟之前的方法相同，这里通过计算得到的地址就是指向数据项即`_IMAGE_DATA_DIRECTORY`结构

    
    
    typedef struct _IMAGE_DATA_DIRECTORY {                    
        DWORD   VirtualAddress;                    
        DWORD   Size;                    
    } IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;
    

这里`VirtualAddress`是rva，表示资源真正存储的位置，`Size`表示资源的大小

## 代码解析

我们在上面已经了解了资源表的结构，那么我们接下来进行资源表的代码解析，在`IMAGE_RESOURCE_DIRECTORY_ENTRY`结构的第一个联合里面要进行最高位的判断，那么这里可以用与1相与的方法来判断最高位是否为1，或者直接用指针指向`NameIsString`结构进行判断

    
    
    printf("%x\n",(pResourceEntry[i].Name & 0x80000000) == 0x80000000);                            
    printf("%x\n",pResourceEntry[i].NameIsString == 1)
    

那么首先是第一层，定义指针判断最高位是否为0

    
    
    if (!pResEntry[i].NameIsString)
    

判断是否为windows预定义的资源类型，我们知道windows有16种预定义资源类型，转换为十六进制为0x10

    
    
    if (pResEntry[i].Id < 0x11)
    

若最高位为1则指向结构体并复制名称

    
    
        PIMAGE_RESOURCE_DIR_STRING_U pStringRes = (PIMAGE_RESOURCE_DIR_STRING_U)((DWORD)pResource + pResEntry[i].NameOffset);
    
        WCHAR szStr[MAX_PATH] = { 0 };
        memcpy(szStr, pStringRes->NameString, pStringRes->Length*sizeof(WCHAR));
    
        printf("First floor->资源名称:%ls \n", szStr);
    

第二层、第三层与第一层的解析类似，主要是最后一个指向`_IMAGE_DATA_DIRECTORY`结构，定义指针即可

    
    
                if(!pResEntry3[i].DataIsDirectory)
                {
                    //取数据偏移
                    PIMAGE_RESOURCE_DATA_ENTRY pResData = (PIMAGE_RESOURCE_DATA_ENTRY)((DWORD)pResource + pResEntry3->OffsetToData);
                    printf("Third floor->数据RVA:%x,数据大小:%x\n", pResData->OffsetToData, pResData->Size);
                }
    

完整代码如下

    
    
    void PrintResourceTable()
    {
        //定义windows自带的资源
    
        static char* szResName[0x11] = 
        { 0, "鼠标指针", "位图", "图标", "菜单", "对话框", "字符串列表",
    
        "字体目录", "字体", "快捷键", "非格式化资源", "消息列表",
    
        "鼠标指针组", "zz", "图标组", "xx", "版本信息"
        };
    
        LPVOID FileBuffer = NULL;
        PIMAGE_DOS_HEADER pDosHeader = NULL;
        PIMAGE_NT_HEADERS pNTHeader = NULL;
        PIMAGE_FILE_HEADER pPEHeader = NULL;
        PIMAGE_OPTIONAL_HEADER32 pOptionHeader = NULL;
        PIMAGE_SECTION_HEADER pSectionHeader = NULL;
        PIMAGE_IMPORT_DESCRIPTOR pImport = NULL;
        PIMAGE_BOUND_IMPORT_DESCRIPTOR pBoundImport = NULL;
        PIMAGE_RESOURCE_DIRECTORY pResource = NULL;
        PIMAGE_RESOURCE_DIRECTORY  pResourceDirectory = NULL;
    
        DWORD NumEntry = NULL;
        DWORD NumEntry2 = NULL;
        DWORD dwResourceData = NULL;
        DWORD FileAddress = NULL;
        PDWORD pSectionAddress = NULL;
    
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
        pSectionHeader = (PIMAGE_SECTION_HEADER)((DWORD)pOptionHeader + pPEHeader->SizeOfOptionalHeader);
    
        //定位资源目录
        FileAddress = RvaToFoa((char*)IN_path, pOptionHeader->DataDirectory[2].VirtualAddress) + (DWORD)FileBuffer;
        pResource = (PIMAGE_RESOURCE_DIRECTORY)FileAddress;
        //printf("NumberOfNamedEntries:%d,NumberOfIdEntries:%d\n", pResource->NumberOfNamedEntries, pResource->NumberOfIdEntries);
    
        //获取Resourceentry个数
        NumEntry = pResource->NumberOfNamedEntries + pResource->NumberOfIdEntries;
    
        //资源目录表的宽度
    
        dwResourceData = sizeof(PIMAGE_RESOURCE_DIRECTORY);
    
        //定位资源目录节点
        PIMAGE_RESOURCE_DIRECTORY_ENTRY pResEntry = (PIMAGE_RESOURCE_DIRECTORY_ENTRY)((DWORD)pResource + 16);
    
    
        //第一层
    
        for( int i = 0; i < NumEntry ; i++)
        {
            if (!pResEntry[i].NameIsString)        //最高位为0,指向数字
            {
                if (pResEntry[i].Id < 0x11)        //windows共有16种预定义资源类型,当Id > 0x11则为自己写的资源
                {
                    printf("First floor->资源ID:%p,资源名称:%s\n", pResEntry[i].Id, szResName[pResEntry[i].Id]);
                }
                else    
                {
                    char type[20];
                    sprintf(type, "%d", pResEntry[i].Id);
                    printf("First floor->资源ID:%p,资源名称:%s\n", pResEntry[i].Id, type);
                }
            }
            else    //最高位为1,指向结构体
            {
                //获取偏移
                PIMAGE_RESOURCE_DIR_STRING_U pStringRes = (PIMAGE_RESOURCE_DIR_STRING_U)((DWORD)pResource + pResEntry[i].NameOffset);
    
                //定义一个用来接收自定义字符串的宽数组然后直接复制
                WCHAR szStr[MAX_PATH] = { 0 };
                memcpy(szStr, pStringRes->NameString, pStringRes->Length*sizeof(WCHAR));
    
                printf("First floor->资源名称:%ls \n", szStr);
    
            }
    
            //第二层
            if (pResEntry[i].DataIsDirectory)    //目录项指针为1
            {
                printf("Second floor->目录偏移:%p\n", pResEntry[i].OffsetToDirectory);
    
                //定义指向第二层目录的指针
                PIMAGE_RESOURCE_DIRECTORY pResource2 = (PIMAGE_RESOURCE_DIRECTORY)((DWORD)pResource + pResEntry[i].OffsetToDirectory);
                PIMAGE_RESOURCE_DIRECTORY_ENTRY pResEntry2 = (PIMAGE_RESOURCE_DIRECTORY_ENTRY)((DWORD)pResource2 + 16);
    
                //获取Resourceentry个数
                NumEntry2 = pResource2->NumberOfIdEntries + pResource2->NumberOfNamedEntries;
    
                for (int i = 0 ; i < NumEntry2 ; i++)
                {
    
                    if (!pResEntry2[i].NameIsString)
                    {
                        printf("Second floor->资源表示ID:%d\n", pResEntry2[i].Id);
                    }
                    else
                    {
                        //获取偏移
                        PIMAGE_RESOURCE_DIR_STRING_U pStringRes2 = (PIMAGE_RESOURCE_DIR_STRING_U)((DWORD)pResource + pResEntry2[i].NameOffset);
    
                        //定义一个用来接收自定义字符串的宽数组然后直接复制
                        WCHAR szStr2[MAX_PATH] = { 0 };
                        memcpy(szStr2, pStringRes2->NameString, pStringRes2->Length*sizeof(WCHAR));
    
                        printf("Second floor->资源字符串:%ls \n", szStr2);
    
                    }
                }
    
                //第三层
    
                //定义指向第三层目录的指针
    
                PIMAGE_RESOURCE_DIRECTORY pResource3 = (PIMAGE_RESOURCE_DIRECTORY)((DWORD)pResource + pResEntry2[i].OffsetToDirectory);
                PIMAGE_RESOURCE_DIRECTORY_ENTRY pResEntry3 = (PIMAGE_RESOURCE_DIRECTORY_ENTRY)((DWORD)pResource3 + 16);
                printf("Third floor->资源:%d\n", pResource3[i].Characteristics);
    
                if(!pResEntry3[i].DataIsDirectory)
                {
                    //取数据偏移
                    PIMAGE_RESOURCE_DATA_ENTRY pResData = (PIMAGE_RESOURCE_DATA_ENTRY)((DWORD)pResource + pResEntry3->OffsetToData);
                    printf("Third floor->数据RVA:%x,数据大小:%x\n", pResData->OffsetToData, pResData->Size);
                }
    
            }
            printf("\n\n");
    
        }
    
    }
    

这里通过我们的代码解析跟程序解析进行对比相同，证明解析成功

![](https://p4.ssl.qhimg.com/t012ceb531edeb0bef1.jpg)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Drunkmars** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/264912](/post/id/264912)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [win32](/tag/win32)

 **+1** __4赞

 __收藏

![](https://p0.ssl.qhimg.com/t019bb9b9add2982923.jpg) Drunkmars

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

