# CVE-2020-16898：Windows TCP/IP远程执行代码漏洞分析

阅读量 **55134**

发布时间 : 2020-10-11 15:30:55

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01b11dafbc863c5c49.png)

## 0x01 前言

### 1.1 环境搭建

（1）攻击机环境：Ubuntu 20.04

安装scapy

    
    
    sudo apt install python-pip3
    sudo pip3 install scapy
    

（2）受害机环境：Windows 10 1909 x64

tcpip.sys 驱动版本：10.0.18362.476

（3）双机调试Windows 驱动：

<https://blog.csdn.net/qq_21000273/article/details/52027708>

断点：

    
    
    bp tcpip!Ipv6pUpdateRDNSS
    bp tcpip!Ipv6pHandleRouterAdvertisement
    bp tcpip!Ipv6pHandleRouterAdvertisement+0xae4cc
    bp tcpip!Ipv6pHandleRouterAdvertisement+0xae4db
    bp tcpip!Ipv6pUpdateRDNSS+0x99
    bp tcpip!Ipv6pUpdateRDNSS+0xca
    

### 1.2 背景知识

**涉及的包类型：**

    
    
    type:24   Route Information Option
    type:25   Recursive DNS Server Option
    type：134  IMCPv6 Router Advertisement
    

**涉及的结构：**

**_MDL结构**

    
    
    typedef __struct_bcount (Size ) struct _MDL {
        struct _MDL *Next ;
        CSHORT Size ;
        CSHORT MdlFlags ;
        struct _EPROCESS *Process ;
        PVOID MappedSystemVa ;
        PVOID StartVa ;
        ULONG ByteCount ;
        ULONG ByteOffset ;
    } MDL , *PMDL ;
    

**_NET_BUFFER 结构**

    
    
    typedef struct _NET_BUFFER {
      union {
        struct {
          PNET_BUFFER Next;
          PMDL        CurrentMdl;
          ULONG       CurrentMdlOffset;
          union {
            ULONG  DataLength;
            SIZE_T stDataLength;
          };
          PMDL        MdlChain;
          ULONG       DataOffset;
        };
        SLIST_HEADER      Link;
        NET_BUFFER_HEADER NetBufferHeader;
      };
      USHORT                ChecksumBias;
      USHORT                Reserved;
      NDIS_HANDLE           NdisPoolHandle;
      PVOID                 NdisReserved[2];
      PVOID                 ProtocolReserved[6];
      PVOID                 MiniportReserved[4];
      NDIS_PHYSICAL_ADDRESS DataPhysicalAddress;
      union {
        PNET_BUFFER_SHARED_MEMORY SharedMemoryInfo;
        PSCATTER_GATHER_LIST      ScatterGatherList;
      };
    } NET_BUFFER, *PNET_BUFFER;
    

**相关函数：**

**NdisGetDataBuffer 函数**

    
    
    PVOID NdisGetDataBuffer(
      PNET_BUFFER NetBuffer,
      ULONG       BytesNeeded,
      PVOID       Storage,
      UINT        AlignMultiple,
      UINT        AlignOffset
    );
    

NetBuffer：指向NET_BUFFER 结构的指针

BytesNeeded：请求的连续数据的字节数

Storage：指向缓冲区的指针，如果调用者未提供缓冲区，则为NULL。缓冲区的大小必须大于或等于BytesNeeded中指定的字节数。如果此值为非NULL，并且请求的数据不连续，则NDIS将请求的数据将复制到Storage指向的地址。

Windows通过Ipv6pHandleRouterAdvertisement 函数处理 IPv6 路由器通告数据，在该函数中调用
NdisGetDataBuffer 函数从 NET_BUFFER 结构中访问连续或不连续的数据，通过 NET_BUFFER
->CurrentMdlOffset 字段来记录要访问数据起始地址相对于_MDL->MappedSystemVa 的偏移。

## 0x02 漏洞分析

### 2.1 漏洞背景

2020年10月14日，360CERT监测发现 `Microsoft` 发布了 `TCP/IP远程代码执行漏洞` 的风险通告，该漏洞是由于Windows
TCP/IP堆栈 在处理IMCPv6 Router Advertisement（路由通告）数据包时存在漏洞，远程攻击者通过构造特制的ICMPv6
Router Advertisement（路由通告）数据包
，并将其发送到远程Windows主机上，可造成远程BSOD，漏洞编号为CVE-2020-16898。

### 2.2 漏洞成因

根据[rfc5006](https://tools.ietf.org/html/rfc5006)
描述，RDNSS包的length应为奇数，而当攻击者构造的RDNSS包的Length为偶数时，Windows TCP/IP
在检查包过程中会根据Length来获取每个包的偏移，遍历解析，导致对 Addresses of IPv6 Recursive DNS Servers
和下一个 RDNSS 选项的边界解析错误，从而绕过验证，将攻击者伪造的option包进行解析，造成栈溢出，从而导致系统崩溃。

RDNSS Option 数据包格式如下：

Type： 占8-bit，RDNSS 的类型为25

Length：8-bit无符号整数，单位长度为8个字节，所以Type, Length, Reserved,
Lifetime一共占8个字节，一个单位长度，而一个IPv6地址占16个字节，两个单位长度，所以Length的最小值为3，且为奇数。

Reserved：保留字段

Lifetime：32-bit无符号整数，存活周期。

Addresses of IPv6 Recursive DNS
Servers：保存RNDSS的IPv6地址，每个占16个字节，地址的数量会影响Length字段，number=(Length – 1) /
2。每增加一个地址，Length加2。

漏洞点存在于tcpip.sys -> Ipv6pHandleRouterAdvertisement 函数

漏洞调用链为：Icmpv6ReceiveDatagrams -> Ipv6pHandleRouterAdvertisement ->
Ipv6pUpdateRDNSS

Ipv6pHandleRouterAdvertisement
函数存在两个循环，第一个循环遍历所有headers，做一些基本的验证，如length的大小，第二个循环用于处理包，并且该阶段不再验证，两个循环的伪代码如下：

    
    
    // 循环1
    
    while ( 1 )
      {
            ……
        v28 = (KIRQL *)NdisGetDataBuffer(v9, 2u, v182, 1u, 0);
        v27 = v9->DataLength;
        actual_length_bytes = 8 * v28[1];
            ……
        switch ( v25 )
        {
          case 0x18u:       // case 0x18 (ICMPv6NDOptRouteInfo)
                ……
            if ( actual_length_bytes > 0x18u
              || (v144 = *((_BYTE *)NdisGetDataBuffer(v9, actual_length_bytes, v220, 1u, 0) + 2), v144 > 0x80u)
              || v144 > 0x40u && actual_length_bytes < 0x18u  // <-----【1】验证实际字节数，不能大于0x18
              || v144 && actual_length_bytes < 0x10u )
            {
              *a3 = 24;
              goto LABEL_275;
            }
            break;
          case 0x19u:  // case 0x19 (ICMPv6NDOptRDNSS)    // <-----【2】
            if ( (*(_BYTE *)(v11 + 404) & 0x40) != 0 && actual_length_bytes < 0x18u )  
              *a3 = 25;
            break;
         }
            ……
          if ( actual_length_bytes )
            {
          v31 = actual_length_bytes + v9->CurrentMdlOffset;
          if ( v31 >= *(_DWORD *)(v9->Link.Region + 0x28) )
          {
            NdisAdvanceNetBufferDataStart(v9, actual_length_bytes, 0, 0i64);// <---actual_length_bytes=4*8=0x20
          }
          else
          {                                         
            v9->DataOffset += actual_length_bytes;
            v9->DataLength -= actual_length_bytes;
            v9->CurrentMdlOffset = v31;        // 更新CurrentMdlOffset
          }
        }
        v21 += actual_length_bytes;
      }
    
        ……
    
    // 循环2 
    while ( 1 )
    {
        ……
         if ( *v75 == 0x18 )                   // case 0x18 (ICMPv6NDOptRouteInfo)
              {
                       ……
                v153 = (unsigned __int8 *)NdisGetDataBuffer(NetBuffer_1, actual_option, Storage_1, 1u, 0); // <--- 【3】
                v225 = _mm_load_si128((const __m128i *)&_xmm);
                v174 = v225.m128i_u32[((unsigned __int64)v153[3] >> 3) & 3];
                     ……
              }
              if ( *v75 == 0x19 )      // case 0x19 (ICMPv6NDOptRDNSS)
              {
                if ( (*(_BYTE *)(v11 + 0x194) & 0x40) != 0 )
                {
                  Ipv6pUpdateRDNSS(v11, NetBuffer_1, Buf2, v189, &v170);  // <---- 【4】
                  goto LABEL_309;
                }
              }
              else if ( *v75 == 31 && (*(_BYTE *)(v11 + 404) & 0x40) != 0 )
              {
                Ipv6pUpdateDNSSL(v11, NetBuffer_1, Buf2, (unsigned int)v189, &v170);
    LABEL_309:
                v77 = v166;
                goto LABEL_118;
              }
                    ……
    }
    

第一个循环用于验证各个header的有效性，首先获取第一个option包，length为0x4，实际字节数为length*8=0x20个字节，首先更新_net_buffer结构，根据实际字节数计算option的偏移，解析到后面的option2，后面依次根据option.length
解析到option3, option4 ……

所以并没有处理’\x18\x22’，因此绕过了【1】处case:0x18中对length的验证。所以如果Option1.length设为3时，构造图中的包由于长度0x22校验不通过，会当成无效包被舍弃。

第二个循环处理各个option包，但在case:0x19 的Ipv6pUpdateRDNSS函数中，计算ipv6地址个数是通过（length-1）/2
，这样导致length=0x4时和length=0x3时计算的结果一样，都是根据ipv6地址个数*8+8（Type/Length/
Reserved/Lifetime），所以跳过0x18个字节解析到’\x18\x22’，将其当成了type=0x18的option包，并且没有了长度的验证。

综上，漏洞是由于检查和解析包时根据length计算的偏移不同，导致绕过检查，解析到攻击者伪造的option包，造成栈溢出。

## 0x03 漏洞利用

具体调试利用过程如下：

（1）首先进入循环1中的【2】处，判断length实际字节数是否小于0x18，然后调用NdisAdvanceNetBufferDataStart，更新_NET_BUFFER结构，得到下一个Option的偏移，依次处理后面的Option：

调用NdisAdvanceNetBufferDataStart前:

    
    
    kd> dt ndis!_NET_BUFFER @r14
       +0x000 Next             : (null) 
       +0x008 CurrentMdl       : 0xffffe20b`aea77e70 _MDL
       +0x010 CurrentMdlOffset : 0x10
       +0x018 DataLength       : 0x188
       +0x018 stDataLength     : 0x188
       +0x020 MdlChain         : 0xffffe20b`b0a9c220 _MDL
       +0x028 DataOffset       : 0x70
       +0x000 Link             : _SLIST_HEADER
       +0x000 NetBufferHeader  : _NET_BUFFER_HEADER
       +0x030 ChecksumBias     : 0
       +0x032 Reserved         : 0
       +0x038 NdisPoolHandle   : 0xffffe20b`ae45cb40 Void
       +0x040 NdisReserved     : [2] (null) 
       +0x050 ProtocolReserved : [6] 0x00000198`00000000 Void
       +0x080 MiniportReserved : [4] (null) 
       +0x0a0 DataPhysicalAddress : _LARGE_INTEGER 0x0
       +0x0a8 SharedMemoryInfo : (null) 
       +0x0a8 ScatterGatherList : (null) 
    
    kd> dt ndis!_MDL 0xffffe20b`aea77e70
       +0x000 Next             : 0xffffe20b`aea77b10 _MDL
       +0x008 Size             : 0n56
       +0x00a MdlFlags         : 0n4
       +0x00c AllocationProcessorNumber : 0xffff
       +0x00e Reserved         : 0xffff
       +0x010 Process          : (null) 
       +0x018 MappedSystemVa   : 0xffffe20b`aea77eb0 Void
       +0x020 StartVa          : 0xffffe20b`aea77000 Void
       +0x028 ByteCount        : 0x30
       +0x02c ByteOffset       : 0xeb0
    kd> db 0xffffe20b`aea77eb0+0x10
    ffffe20b`aea77ec0  19 04 00 00 00 00 03 84-30 30 30 30 30 30 30 30  ........00000000    // <--- Option1
    ffffe20b`aea77ed0  30 30 30 30 30 30 30 30-18 22 fd 81 00 00 03 84  00000000."......
    ffffe20b`aea77ee0  00 bf 09 02 73 6d 41 72-00 00 03 00 dd bf 04 04  ....smAr........   
    

调用NdisAdvanceNetBufferDataStart后：

    
    
    kd> dt ndis!_NET_BUFFER @r14
       +0x000 Next             : (null) 
       +0x008 CurrentMdl       : 0xffffe20b`aea77b10 _MDL
       +0x010 CurrentMdlOffset : 0
       +0x018 DataLength       : 0x168
       +0x018 stDataLength     : 0x168
       +0x020 MdlChain         : 0xffffe20b`b0a9c220 _MDL
       +0x028 DataOffset       : 0x90
       +0x000 Link             : _SLIST_HEADER
       +0x000 NetBufferHeader  : _NET_BUFFER_HEADER
       +0x030 ChecksumBias     : 0
       +0x032 Reserved         : 0
       +0x038 NdisPoolHandle   : 0xffffe20b`ae45cb40 Void
       +0x040 NdisReserved     : [2] (null) 
       +0x050 ProtocolReserved : [6] 0x00000198`00000000 Void
       +0x080 MiniportReserved : [4] (null) 
       +0x0a0 DataPhysicalAddress : _LARGE_INTEGER 0x0
       +0x0a8 SharedMemoryInfo : (null) 
       +0x0a8 ScatterGatherList : (null) 
    
    kd>   dt ndis!_MDL 0xffffe20b`aea77b10
       +0x000 Next             : 0xffffe20b`aea78890 _MDL
       +0x008 Size             : 0n56
       +0x00a MdlFlags         : 0n4
       +0x00c AllocationProcessorNumber : 0xe20b
       +0x00e Reserved         : 0xffff
       +0x010 Process          : (null) 
       +0x018 MappedSystemVa   : 0xffffe20b`aea77b50 Void
       +0x020 StartVa          : 0xffffe20b`aea77000 Void
       +0x028 ByteCount        : 0x30
       +0x02c ByteOffset       : 0xb50
    kd> db 0xffffe20b`aea77b50
    ffffe20b`aea77b50  19 05 00 00 00 00 03 84-41 41 41 41 41 41 41 41  ........AAAAAAAA    // <--- Option2
    ffffe20b`aea77b60  41 41 41 41 41 41 41 41-42 42 42 42 42 42 42 42  AAAAAAAABBBBBBBB
    ffffe20b`aea77b70  42 42 42 42 42 42 42 42-19 05 00 00 00 00 03 84  BBBBBBBB........
    

（2）进入循环2中的【4】处：

进入Ipv6UpdateRDNSS，处理第一个type为0x19，length为4的option，Ipv6pUpdateRDNSS 中计算IPv6
地址数量是通过下面代码实现的：

调试结果如下：

rbx 保存option 包的起始位置，[rbx+1]
取的是length字段的值，此时为4，esi的值为1，ecx的值为2，所以这段汇编的计算的ipv6地址个数为（length-1）/2 =1 .

所以length设置为4，其实和length=3计算结果是相同的：

    
    
    (4-1)/2 = 1
    (3-1)/2 = 1
    

因此会按照0x18（一个ipv6地址加上Type/Length/ Reserved/Lifetime）
的偏移进行解析下一个Option，即解析到伪造的Option。

调用Ipv6UpdateRDNSS前：

    
    
    kd> dt ndis!_NET_BUFFER @r14
       +0x000 Next             : (null) 
       +0x008 CurrentMdl       : 0xffffe20b`aea77e70 _MDL
       +0x010 CurrentMdlOffset : 0x10
       +0x018 DataLength       : 0x188
       +0x018 stDataLength     : 0x188
       +0x020 MdlChain         : 0xffffe20b`b0a9c220 _MDL
       +0x028 DataOffset       : 0x70
       +0x000 Link             : _SLIST_HEADER
       +0x000 NetBufferHeader  : _NET_BUFFER_HEADER
       +0x030 ChecksumBias     : 0
       +0x032 Reserved         : 0
       +0x038 NdisPoolHandle   : 0xffffe20b`ae45cb40 Void
       +0x040 NdisReserved     : [2] (null) 
       +0x050 ProtocolReserved : [6] 0x00000198`00000000 Void
       +0x080 MiniportReserved : [4] (null) 
       +0x0a0 DataPhysicalAddress : _LARGE_INTEGER 0x0
       +0x0a8 SharedMemoryInfo : (null) 
       +0x0a8 ScatterGatherList : (null) 
    kd> dt ndis!_MDL 0xffffe20b`aea77e70
       +0x000 Next             : 0xffffe20b`aea77b10 _MDL
       +0x008 Size             : 0n56
       +0x00a MdlFlags         : 0n4
       +0x00c AllocationProcessorNumber : 0xffff
       +0x00e Reserved         : 0xffff
       +0x010 Process          : (null) 
       +0x018 MappedSystemVa   : 0xffffe20b`aea77eb0 Void
       +0x020 StartVa          : 0xffffe20b`aea77000 Void
       +0x028 ByteCount        : 0x30
       +0x02c ByteOffset       : 0xeb0
    kd> db 0xffffe20b`aea77eb0+0x10
    ffffe20b`aea77ec0  19 04 00 00 00 00 03 84-30 30 30 30 30 30 30 30  ........00000000  // <--- Option1
    ffffe20b`aea77ed0  30 30 30 30 30 30 30 30-18 22 fd 81 00 00 03 84  00000000."......
    ffffe20b`aea77ee0  00 bf 09 02 73 6d 41 72-00 00 03 00 dd bf 04 04  ....smAr........
    

调用Ipv6UpdateRDNSS后：

    
    
    kd> dt ndis!_NET_BUFFER @r14
       +0x000 Next             : (null) 
       +0x008 CurrentMdl       : 0xffffe20b`aea77e70 _MDL
       +0x010 CurrentMdlOffset : 0x28
       +0x018 DataLength       : 0x170
       +0x018 stDataLength     : 0x170
       +0x020 MdlChain         : 0xffffe20b`b0a9c220 _MDL
       +0x028 DataOffset       : 0x88
       +0x000 Link             : _SLIST_HEADER
       +0x000 NetBufferHeader  : _NET_BUFFER_HEADER
       +0x030 ChecksumBias     : 0
       +0x032 Reserved         : 0
       +0x038 NdisPoolHandle   : 0xffffe20b`ae45cb40 Void
       +0x040 NdisReserved     : [2] (null) 
       +0x050 ProtocolReserved : [6] 0x00000198`00000000 Void
       +0x080 MiniportReserved : [4] (null) 
       +0x0a0 DataPhysicalAddress : _LARGE_INTEGER 0x0
       +0x0a8 SharedMemoryInfo : (null) 
       +0x0a8 ScatterGatherList : (null) 
    kd> dt ndis!_MDL 0xffffe20b`aea77e70
       +0x000 Next             : 0xffffe20b`aea77b10 _MDL
       +0x008 Size             : 0n56
       +0x00a MdlFlags         : 0n4
       +0x00c AllocationProcessorNumber : 0xffff
       +0x00e Reserved         : 0xffff
       +0x010 Process          : (null) 
       +0x018 MappedSystemVa   : 0xffffe20b`aea77eb0 Void
       +0x020 StartVa          : 0xffffe20b`aea77000 Void
       +0x028 ByteCount        : 0x30
       +0x02c ByteOffset       : 0xeb0
    kd> db 0xffffe20b`aea77eb0+0x28
    ffffe20b`aea77ed8  18 22 fd 81 00 00 03 84-00 bf 09 02 73 6d 41 72  ."..........smAr // <---  伪造的option
    ffffe20b`aea77ee8  00 00 03 00 dd bf 04 04-00 60 6d b0 0b e2 ff ff  .........`m.....
    

（3）进入循环2中的【3】处case:0x18，处理伪造的type为0x18，length为0x22的option。

对于type为0x18会进入下面的流程处理，调用NdisGetDataBuffer函数，其中第二个参数为长度的实际字节大小，等于length
_8，所以此时传入的actual_length_bytes = 0x22_ 8 = 0x110：

而Storage_1 为栈上的数组变量，将0x110个字节赋值过去，就会造成栈上的溢出，实际的崩溃是溢出覆盖了stack
cookie，触发tcpip!_security_check_cookie，造成蓝屏（BSOD）：

调用NdisGetDataBuffer函数前：

    
    
    kd> r rdx  // actual_length_bytes_1
    rdx=0000000000000110
    kd> dd r8 // Storage_1
    fffff806`6ce9a348  00000000 00000000 00000000 00000000
    fffff806`6ce9a358  00000000 00000000 00000000 00000000
    fffff806`6ce9a368  00000000 00000000 b3b18770 ffffe20b
    fffff806`6ce9a378  aea77eb0 ffffe20b b021bce0 ffffe20b
    fffff806`6ce9a388  00000000 00000000 aea77eb0 ffffe20b
    fffff806`6ce9a398  00000000 00000000 b0210040 00000000
    

调用NdisGetDataBuffer函数后：

    
    
    kd> dd fffff806`6ce9a348
    fffff806`6ce9a348  81fd2218 84030000 00000519 84030000
    fffff806`6ce9a358  41414141 41414141 41414141 41414141
    fffff806`6ce9a368  42424242 42424242 42424242 42424242
    fffff806`6ce9a378  00000519 84030000 41414141 41414141
    fffff806`6ce9a388  41414141 41414141 42424242 42424242
    kd> k
    Child-SP          RetAddr           Call Site
    fffff806`6ce9a090 42424242`42424242 tcpip!Ipv6pHandleRouterAdvertisement+0xae522
    fffff806`6ce9a440 84030000`00000519 0x42424242`42424242
    fffff806`6ce9a448 41414141`41414141 0x84030000`00000519
    fffff806`6ce9a450 41414141`41414141 0x41414141`41414141
    fffff806`6ce9a458 00000000`00000000 0x41414141`41414141
    

最后需要注意的是如果从NetBuffer_1请求的数据是连续的，则会将数据存放在NDIS提供的地址，这样无法造成溢出。所以需要从NetBuffer_1请求的数据不是连续的，才会将数据存放在Storage_1上。数据非连续的实现是通过
**fragmentation** （碎片化），将Router Advertisement包通过scapy的fragment6函数拆分成多个IPv6
fragments进行发送。

蓝屏崩溃现场：

## 0x04 补丁分析

补丁前第一个循环case:0x19的伪代码：

补丁后：

补丁加入了针对length的奇偶验证，v32为length *8的结果， 如果 length 为偶数，(v32-8)&0xf
将不等于0，则转入错误处理流程。

## 0x05 时间线

**2020-10-13** 微软发布漏洞通告

**2020-10-14** 360CERT发布通告

**2020-10-16** 360CERT监测到网上公开相关Poc

**2020-10-16** 360CERT更新通告

**2020-10-19** 360CERT发布漏洞分析报告

## 0x06 参考链接

  1. <https://tools.ietf.org/html/rfc8106>
  2. <https://www.mcafee.com/blogs/other-blogs/mcafee-labs/cve-2020-16898-bad-neighbor>
  3. <http://blog.pi3.com.pl/?p=780>
  4. <https://blog.quarkslab.com/beware-the-bad-neighbor-analysis-and-poc-of-the-windows-ipv6-router-advertisement-vulnerability-cve-2020-16898.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/219948](/post/id/219948)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

