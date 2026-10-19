**作者：360漏洞研究院 许仕杰 宋建阳 李林双  
原文链接：<https://vul.360.net/archives/438>**

## 概述

近两年通用日志文件系统模块 (clfs) 成为了 Windows 平台安全研究的热点，本文首先会介绍一些关于 clfs
的背景知识，然后会介绍我们是如何对这个目标进行 fuzz ，最后将分享几个漏洞案例以及我们是如何使用一种新方法实现本地提权。

## 背景知识

根据微软官方文档可以知道，通用日志文件系统 (clfs) 是 Windows Vista
引入的一种新的日志记录机制，它负责提供一个高性能、通用的日志文件子系统，供专用客户端应用程序使用，多个客户端可以共享以优化日志访问。

我们可以使用 `CreateLogFile` 函数创建或打开一个日志文件 (.blf)。日志名决定这个日志为单路日志还是多路日志，日志名格式为 `(log
:[::])` ，日志可以通过 `CloseHandle` 函数关闭。

    
    
    CLFSUSER_API HANDLE CreateLogFile(
      [in]           LPCWSTR               pszLogFileName,
      [in]           ACCESS_MASK           fDesiredAccess,
      [in]           DWORD                 dwShareMode,
      [in, optional] LPSECURITY_ATTRIBUTES psaLogFile,
      [in]           ULONG                 fCreateDisposition,
      [in]           ULONG                 fFlagsAndAttributes
    );

我们可以通过查询微软官方文档或者逆向clfs.sys驱动获取一些日志相关操作函数。

## Fuzz CLFS

我们首先查阅了一些前辈的研究资料(链接会放在文末)，可以发现攻击面主要分为两类

  * clfs.sys 中日志文件解析相关漏洞
  * clfs.sys 中 IoCode 处理相关漏洞

我们决定先研究 blf 日志文件格式，然后对该日志文件格式进行fuzz，最后我们总结出 blf 格式如下图
![](https://images.seebug.org/content/images/2022/06/979b20f4-359c-436c-b74a-bdbbf1957e49.png-w331s)

知道日志文件格式和日志处理函数之后，我们的 fuzz 设计就很简单，大致思路如下

  * 创建日志文件(单路、多路、是否设置 Container 容器)
  * 根据文件格式随机数据
  * 调用函数使 clfs.sys 对日志文件进行解析

需要注意的是在每次随机文件内容的时候，需要绕过一个 CRC 检查，伪代码如下

    
    
    __int64 __fastcall CCrc32::ComputeCrc32(BYTE* Ptr, int Size)
    {
      unsigned int Crc;
    
      for ( int i = 0; i < Size; i++ )
      {
        data = Ptr[i];
        Crc = (Crc >> 8) ^ CCrc32::m_rgCrcTable[(unsigned __int8)Crc ^ data];
      }
    
      return ~Crc;
    }

在逆向过程中，我们观察到一些以 Get 和 Acquire 开头的函数会直接从 blf 文件中读取数据，所以我们在随机数据的时候重点关注这些函数即可。

![](https://images.seebug.org/content/images/2022/06/00ef864d-f9f7-47b3-9632-c654f4f172cf.png-w331s)

## 漏洞分析

经过一段时间的 fuzz，我们得到了一些崩溃，这里分享其中两个

**CVE-2022-21916**

第一个漏洞出现在 `CClfsBaseFilePersisted::ShiftMetadataBlockDescriptor` 函数，其伪代码如下所示

    
    
    CClfsBaseFilePersisted::ShiftMetadataBlockDescriptor(this,UINT iFlushBlock,UINT iExtendBlock)
    {
      // ...
    
      NewTotalSize = -1;
      TotalSize = iExtendBlock * this->SectorSize;
      if ( TotalSize > 0xFFFFFFFF )
        return STATUS_INTEGER_OVERFLOW;
      TotalSectorSize = this->BaseMetaBlock[iFlushBlock].TotalSectorSize; // OOB read
      if ( TotalSectorSize + TotalSize >= TotalSectorSize )
        NewTotalSize = TotalSectorSize + TotalSize;
      Status = TotalSectorSize + TotalSize < TotalSectorSize ? STATUS_INTEGER_OVERFLOW : 0;
      this->BaseMetaBlock[iFlushBlock].TotalSectorSize = NewTotalSize;
      return Status;
    }

该函数在解析 `CLFS_CONTROL_RECORD` 结构的时候出现了问题，该结构可以在 blf 文件偏移 0x70 的位置找到，其中
iFlushBlock 存在于 blf 文件的 0x8A 处，iExtendBlock 存在于文件的 0x88
处，此函数未正确对这两个参数进行检查导致了越界漏洞的产生。到达此函数还需要将 eExtendState 字段设置为 2，此字段存在于 blf 文件 0x84
的位置，如下所示：

![](https://images.seebug.org/content/images/2022/06/71557df9-c26c-4ccd-aaad-e04ddb976053.png-w331s)

**Vulnerability for TianfuCup**

第二个漏洞出现在 `CClfsLogFcbPhysical::OverflowReferral` 函数，与 CVE-2022-21916
类似，该漏洞也是在解析 blf 文件格式时出现问题，该函数主要与 ownerpage 操作相关。伪代码如下

    
    
    CClfsLogFcbPhysical::OverflowReferral(CClfsLogFcbPhysical *this, struct _CLFS_LOG_BLOCK_HEADER * LogBlockHeader)
    {
      // NewOwnerPage is a Paged Pool of size 0x1000
      NewOwnerPage = &LogBlockHeader->MajorVersion + LogBlockHeader->RecordOffsets[2]; 
      OldOwnerPage = &this->OwnerPage->MajorVersion + this->OwnerPage->RecordOffsets[2];
      ClientId = CClfsBaseFile::HighWaterMarkClientId(this->CClfsBaseFilePersisted); // BaseLogRecord->cNextClient - 1
      i = 0;
      do
      {
        i = i++;
        i *= 2i64;
        *(CLFS_LSN *)&NewOwnerPage[8 * i] = CLFS_LSN_INVALID; // OOB Write
        *(_QWORD *)&NewOwnerPage[8 * i + 8] = *(_QWORD *)&OldOwnerPage[8 * i + 8];
      }
      while ( i <= ClientId ); // Overflow occurs when ClientId is greater than 0x60
    }

`CClfsBaseFile::HighWaterMarkClientId` 函数负责获取 blf 文件中的 ClientId 信息，可以通过修改
`CLFS_BASE_RECORD_HEADER` 结构中的 cNextClient 字段从而控制 ClientId ，而 cNextClient
可以直接从 blf 文件中找到并修改。 当 cNextClient 被修改为其他值的时候，它会被用作错误的索引，从而导致越界漏洞。下图就是我们在文件中找到的
cNextClient

![](https://images.seebug.org/content/images/2022/06/aedc00c6-9d47-4d36-82ef-0c52fffc48ec.png-w331s)

总结而言，此漏洞是一个大小为 0x1000 的分页池溢出漏洞，它将 CLFS_LSN_INVALID 和 OldOwnerPage 数据写入下一个池的头部。

## 漏洞利用介绍

Windows 分页池溢出的利用方式一般有如下两种:

  * WNF  
通过溢出占用 _WNF_NAME_INSTANCE 结构的 StateData 指针可以实现有限制的任意地址读写

  * 命名管道  
通过溢出占用 PipeAttribute 结构的 Flink 指针可以实现任意地址读

WNF 的利用方式有一些限制，比如 _WNF_NAME_INSTANCE 结构的大小为 0xC0 或者 0xD0，而我们的漏洞是一个大小为 0x1000
的分页池溢出漏洞。我们无法将 0xC0 或者 0xD0 大小的分页池分配在 0x1000 的分页池后面，所以我们无法利用这个漏洞去溢出
WNF的_WNF_NAME_INSTANCE 结构。

但是我们可以去溢出 0x1000 大小的 _WNF_STATE_DATA 结构，通过溢出 _WNF_STATE_DATA 结构中的
AllocatedSize 字段，我们可以实现最大长度为 0x1000 的越界写，它只能越界写 0x1000 大小的 _WNF_STATE_DATA
结构后的数据，并且刚好只能越界写 16 个字节。所以我们需要找到一个 0x1000 大小的分页池结构，然后通过修改这个结构的前 16
个字节来实现任意地址写，我们在 Windows ALPC 中找到了这个结构。

我们也找到了一种新的通用的 Windows 分页池溢出的利用方式，通过溢出占用 _ALPC_HANDLE_TABLE 结构的 Handles
指针，我们可以实现任意地址的读写。

_ALPC_HANDLE_TABLE 的结构如下：

    
    
    kd> dt nt!_ALPC_HANDLE_TABLE
       +0x000 Handles          : Ptr64 _ALPC_HANDLE_ENTRY
       +0x008 TotalHandles     : Uint4B
       +0x00c Flags            : Uint4B
       +0x010 Lock             : _EX_PUSH_LOCK

你可以通过调用 NtAlpcCreateResourceReserve 函数来创建一个 Reserve Blob，它会调用
AlpcAddHandleTableEntry 函数把刚创建的 Reserve Blob 的地址写入到 _ALPC_HANDLE_TABLE
结构的Handles数组中。

当你创建alpc端口时，AlpcInitializeHandleTable 函数会被调用来初始化 HandleTable 结构。Handles
是一个初始大小为 0x80 的数组，它存放着 blob 结构的地址。当越来越多 blob 被创建时，Handles 的大小成倍增加，所以 Handles
的大小可以为 0x1000。

_KALPC_RESERVE 的结构如下所示：

    
    
    kd> dt nt!_KALPC_RESERVE
       +0x000 OwnerPort        : Ptr64 _ALPC_PORT
       +0x008 HandleTable      : Ptr64 _ALPC_HANDLE_TABLE
       +0x010 Handle           : Ptr64 Void
       +0x018 Message          : Ptr64 _KALPC_MESSAGE
       +0x020 Size             : Uint8B
       +0x028 Active           : Int4B

当你溢出占用 Handles 数组中的 _KALPC_RESERVE 结构的指针时，你就可以伪造一个虚假的 Reserve Blob。因为
_KALPC_RESERVE 中存储着 Message 的地址，所以你可以进一步伪造一个虚假的 _KALPC_MESSAGE 结构。

_KALPC_MESSAGE 的结构如下：

    
    
    kd> dt nt!_KALPC_MESSAGE
       +0x000 Entry            : _LIST_ENTRY
       +0x010 PortQueue        : Ptr64 _ALPC_PORT
       +0x018 OwnerPort        : Ptr64 _ALPC_PORT
       +0x020 WaitingThread    : Ptr64 _ETHREAD
       +0x028 u1               : <anonymous-tag>
       +0x02c SequenceNo       : Int4B
       +0x030 QuotaProcess     : Ptr64 _EPROCESS
       +0x030 QuotaBlock       : Ptr64 Void
       +0x038 CancelSequencePort : Ptr64 _ALPC_PORT
       +0x040 CancelQueuePort  : Ptr64 _ALPC_PORT
       +0x048 CancelSequenceNo : Int4B
       +0x050 CancelListEntry  : _LIST_ENTRY
       +0x060 Reserve          : Ptr64 _KALPC_RESERVE
       +0x068 MessageAttributes : _KALPC_MESSAGE_ATTRIBUTES
       +0x0b0 DataUserVa       : Ptr64 Void
       +0x0b8 CommunicationInfo : Ptr64 _ALPC_COMMUNICATION_INFO
       +0x0c0 ConnectionPort   : Ptr64 _ALPC_PORT
       +0x0c8 ServerThread     : Ptr64 _ETHREAD
       +0x0d0 WakeReference    : Ptr64 Void
       +0x0d8 WakeReference2   : Ptr64 Void
       +0x0e0 ExtensionBuffer  : Ptr64 Void
       +0x0e8 ExtensionBufferSize : Uint8B
       +0x0f0 PortMessage      : _PORT_MESSAGE

当你调用 NtAlpcSendWaitReceivePort 函数发送消息时，它会将用户传入的数据写入到 _KALPC_MESSAGE 结构中
ExtensionBuffer 所指向的地址，我们可以用它来实现任意地址写入。

当你调用 NtAlpcSendWaitReceivePort 函数接收消息时，它会读取 _KALPC_MESSAGE 结构中 ExtensionBuffer
所指向的地址处的数据，我们可以用它来实现任意地址读取。

实现任意地址读写的整个过程如下：

![](https://images.seebug.org/content/images/2022/06/1a9a3207-8313-4821-b03f-e0e961c88fa4.png-w331s)

首先，通过溢出占用 Handles 结构的 _KALPC_RESERVE 指针，我们可以构造一个虚假的 Reserve Blob，然后继续构造一个虚假的
_KALPC_MESSAGE 结构，那么我们就可以通过 _KALPC_MESSAGE 结构中的 ExtensionBuffer 字段和
ExtensionBufferSize 字段来实现任意地址读写。

## 漏洞利用

下面来详解一下漏洞利用具体的流程。

首先我们要结合 WNF 和 ALPC 达到漏洞利用，我们需要调用 NtUpdateWnfStateData 去喷射大量的 0x1000 大小的
_WNF_STATE_DATA 结构，然后让它们在内存中相邻排列。

![](https://images.seebug.org/content/images/2022/06/fbd526df-4a79-4321-ab26-816d9cbf2bda.png-w331s)

接着我们需要调用 NtDeleteWnfStateName 函数去创建大量的内存空洞。

![](https://images.seebug.org/content/images/2022/06/51343f05-e869-439e-b392-f69c47664bad.png-w331s)
然后我们要创建 Ownerpage，也就是存在漏洞的池块。我们需要创建一个 Multiplexed 类型的 blf 文件，并存在两个 container
文件，然后向 container 中写入大量的 record 记录，当记录的长度超过 0x7f000 的时候，写入 record 时会自动创建
Ownerpage 页到 container 中。之后我们需要调用 CreateLogFile 去打开一个 Multiplexed 类型的 blf
文件，该函数会解析 container，并在内存中创建 Ownerpage 池块。

创建好 Ownerpage 池块后，流程会进入到 OverflowReferral 函数，此时会导致越界写操作，覆盖相邻的 WNF 池块的内容。

![](https://images.seebug.org/content/images/2022/06/06cbcb60-2a85-4a2b-97ad-319b50ae1d0a.png-w331s)

我们将 WNF 的 AllocatedSize 成员覆盖为 0xffffffff，这样就可以通过 WNF 向下一个块进行任意内容越界写。

![](https://images.seebug.org/content/images/2022/06/9d09c367-7a7c-4667-b187-bd15e2599960.png-w331s)

然后我们在 WNF 块后面分配一个 Handles 结构，该结构的所有成员都是 ALPC_RESERVE 结构的指针。由于 WNF 有 0x1000
大小的写入限制，写入的起始位置在WNF 结构 +0x10 的偏移处，所以我们只能向下一个块写入16字节长度的内容，不过这已经足够了。

![](https://images.seebug.org/content/images/2022/06/ec492676-06ae-42f1-b8c4-2ca475e80d81.png-w331s)

我们将 Handles 原来的指针成员，替换成了我们自己的指针 0x00000282`99055970，该指针指向我们在用户态伪造的
ALPC_RESERVE 结构。

![](https://images.seebug.org/content/images/2022/06/c18f087c-29df-433a-83b4-fe22b56494ae.png-w331s)

之后我们调用 NtAlpcSendWaitReceivePort 函数，会进入到 AlpcpLookupMessage 函数内，然后再调用
AlpcReferenceBlobByHandle 函数，从 Handles 中获取到我们伪造的用户态地址。

![](https://images.seebug.org/content/images/2022/06/b24193b3-d485-40b1-af16-cc031a1cfedf.png-w331s)

ALPC_RESERVE 结构的 Message 成员是我们在用户态伪造的 _KALPC_MESSAGE 结构。

![](https://images.seebug.org/content/images/2022/06/cb2d0713-7e3f-442b-a196-98d46627bac0.png-w331s)

我们在伪造 _KALPC_MESSAGE 时，需要将 Token 的地址，写入在 _KALPC_MESSAGE+0xe0 偏移处，也就是
ExtensionBuffer 的位置。

![](https://images.seebug.org/content/images/2022/06/4108ce79-5f8d-4bf1-aa52-665be7ad1ed1.png-w331s)

最后当我们调用 NtAlpcSendWaitReceivePort 后，流程会进入到 AlpcpCaptureMessageDataSafe 函数，会调用
memmove 向 ExtensionBuffer (Token的地址) 写入可控的任意内容。我们将 token 的 Privileges
全部覆盖为0xff，获得所有特权。

![](https://images.seebug.org/content/images/2022/06/10267735-7e79-4ace-ab1c-f816dc9a0166.png-w331s)

![](https://images.seebug.org/content/images/2022/06/55ebee7f-0124-45d0-83ad-6f59072d8d33.png-w331s)

我们打开Procexp.exe 查看利用进程的权限，发现已经获得了 SeDebugPrivilege 权限，拥有了该权限我们就可以向
Winlogon.exe 进程注入 shellcode，从而最终达到特权提升。

![](https://images.seebug.org/content/images/2022/06/c3d949fb-23ce-4a6d-8ebb-3462f4361c23.png-w331s)

## 为什么是通用的？

我们在本次利用中到了三个结构，分别是_WNF_STATE_DATA 、Handles 和
_KALPC_MESSAGE。它们都有一个共同的特性，就是结构大小可控。根据我们的测试它们可以适配 0x30 ~ 0x11000+ 大小的池块。

**0x30 ~ 0x1000 size ：**

  * _WNF_STATE_DATA (0x30 ~ 0x1000)
  * _ALPC_HANDLE_TABLE->Handles (0x90、0x110、0x210、0x410 、0x810、0x1000…0x10000…)
  * _KALPC_MESSAGE (0x160 ~ 0x11000)

**> 0x1000 size:**

  * _ALPC_HANDLE_TABLE->Handles
  * _KALPC_MESSAGE

**> 0x11000 size:**

  * _ALPC_HANDLE_TABLE->Handles (0x90、0x110、0x210、0x410 、0x810、0x1000…0x10000…)

### 通用利用之WNF

WNF的结构可以适配 0x30 ~ 0x1000 的大小，通过修改 AllocatedSize 成员，可以达到越界写。通过修改 DataSize
成员，可以达到越界读。WNF 存在一个限制，就是越界读写的最大长度是 0x1000。

![](https://images.seebug.org/content/images/2022/06/8f6749eb-211a-467a-869a-03b4735c93ce.png-w331s)

### 通用利用之Handles

Handles结构长度的增长规律是成倍的，例如：0x90、0x110、0x210、0x410 、0x810、0x1000…0x10000… 。超过
0x1000 以后是没有池头的，所以并不会被分配成 0x1010。我们可以覆盖 Handles 的成员为我们伪造的 _KALPC_RESERVE
指针，然后再调用 NtAlpcSendWaitReceivePort 达到任意地址写。

利用 Handles 结构比较方便，因为即使你向 Handles 结构写入错误的地址，你仍然可以调用 VirtualAlloc 将错误的地址映射成正常的
_KALPC_RESERVE 指针地址。到了这一步利用基本就成功了。

### 通用利用之 _KALPC_MESSAGE

_KALPC_MESSAGE 的适配范围在 0x160 ~ 0x11000。利用方法比较简单，只需要通过溢出覆盖 0xe0 偏移处的地址，然后再调用
NtAlpcSendWaitReceivePort，即可达到任意地址写。

![](https://images.seebug.org/content/images/2022/06/f0ecb5a9-e427-4e70-bb05-a0be3338f96c.png-w331s)

## 参考链接

[CLFS Internals](https://github.com/ionescu007/clfs-docs/) – Alex Ionescu  
[DeathNote of Microsoft Windows
Kernel](https://www.slideshare.net/PeterHlavaty/deathnote-of-microsoft-windows-kernel) – Keen Lab  
[Microsoft Windows 10 CLFS.sys ValidateRegionBlocks privilege escalation
vulnerability](https://talosintelligence.com/vulnerability_reports/TALOS-2020-1098)
– Cisco Talos

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1920/>

