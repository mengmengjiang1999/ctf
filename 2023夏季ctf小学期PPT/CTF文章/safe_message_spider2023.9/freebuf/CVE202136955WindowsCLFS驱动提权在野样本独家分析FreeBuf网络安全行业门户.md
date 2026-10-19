## 前 言

2021年9月14日，微软Patch
Tuesday修补了倍受瞩目的mshtml漏洞CVE-2021-40444，该漏洞除了通过IE也可以通过docx/xlsx文件投递，大量安全团队都将注意力集中在了对该漏洞的分析上。

宁静之盾斩月实验室注意到微软当月的补丁中还有三个CVE比较有意思（CVE-2021-36955/36963/38633），这是三个针对微软内核模块
clfs.sys 的补丁，近五年来该内核模块一共修补了近20个漏洞，但并没有发现可利用的在野样本。

当月火眼发布的一篇报告中也提到了有APT组织对 clfs 中的 blf 文件的恶意利用[1][2]。对blf文件的正常操作是调用clfsw32.dll 的
CreateLogFile/ReserveAndAppendLog/CreateLogMarshallingArea/ReadLogFile
等API[3]，但攻击者也可以只调用基本的文件读写API使用clfs。

![](https://image.3001.net/images/20211224/1640337132_61c58eec519d40911e1c7.png!small)

近年的CLFS公共日志文件系统漏洞

微软公告中明确指出 CVE-2021-36955 可利用度为more
likely（很可能被利用），同时利用代码成熟度为Functional(可编写出利用代码)，斩月实验室第一时间对该漏洞进行了补丁比较，并依据补丁比较得来的线索发现在野样本一枚，该样本还在内部测试阶段，在调试状态下会输出调试信息，成功利用该漏洞会创建
SYSTEM 权限的 cmd 进程，本文主要对该在野样本进行了分析。

## 样 本 分 析

### 一. 判断当前操作系统版本等信息

调用 GetLogicalProcessorInformation
获取CPU信息并设置内核池对齐参数（一般是40H）同时判断是否为X64平台(该样本工具只针对X64平台)，同时调用 RtlGetVersion 获取
windows 版本号，该样本工具非常通用，支持win7/8/8.1/10，其中win10系统判断了从win10 1507到 20h1的所有小版本。  
  
![](https://image.3001.net/images/20211224/1640337211_61c58f3ba943dc99a850d.png!small)

然后根据内核版本，设置利用需要的内核偏移，比如gs:[188h]的位置存储的是_KTHREAD结构的地址，这个结构基址在WIN10下+0x220的位置存储的就是_KPROCESS，样本通过该结构可以获取
SYSTEM 进程的 TOKEN ，然后复制给新创建的CMD进程。

![](https://image.3001.net/images/20211224/1640337231_61c58f4f07020f914ce03.png!small)

同时也会根据不同系统版本在 hal 或者 ntoskrnl 中利用硬编码去定位函数地址。在win7下会获取 XmXchgOP 和
HalpDmaPowerCriticalTransitionCallback
的地址，在后续操作中通过在恶意blf文件中设置这两个地址，漏洞触发就后会调用这两个函数。

![](https://image.3001.net/images/20211224/1640337251_61c58f63ea15c340504b6.png!small)

另外还会调用 NtQuerySystemInformation 函数，使用 SystemModuleInformation 类型用来获取 ntoskrnl
模块和 hal 模块的地址。

最终会构造包含如下成员的自定义结构：

> struct VulATTRIBUTE  
> {  
> HANDLE hReadPipe; //管道读句柄  
> HANDLE hWritePipe; //管道写句柄  
> DWORD Tag1; //管道属性名  
> ULONG64 pooladdr1; //管道属性内核地址  
> DWORD Tag2; //管道属性名  
> ULONG64 pooladdr2; //管道属性内核地址  
> PVOID pReadAttribute;  
> ULONG64 HALaddr; //HAL基地址  
> ULONG64 NTOSKRNLaddr; //ntoskrnl基地址  
> }  
> （前7个成员在本文第三节中被填充）

### 二.创建恶意 blf 记录构造任意地址写

该样本简单模拟了应用层CLFS API的操作去生成恶意blf文件，首先会访问 \\\GLOBAL\\\LOG 对象判断日志文件系统是否正常工作，后续对
blf 文件的操作与普通文件是一样的，但会触发 clfs.sys 的解析。

![](https://image.3001.net/images/20211224/1640337304_61c58f9828fa9ffe9bde1.png!small)

最后调用 SetFileInformationByHandle
删除文件后在驱动层会触发对恶意clfsContainer的解析，进而触发内核任意内容写任意地址。

具体流程为：  
// 1. 在TEMP目录创建 wct打头的临时blf文件 ，判断日志文件系统是否正常工作。

![](https://image.3001.net/images/20211224/1640337325_61c58fadeab23ada7ab8b.png!small)

// 2. 创建恶意 blf文件内容 。blf 的创建过程如下：

![](https://image.3001.net/images/20211224/1640337349_61c58fc5c42c99b83fc8b.png!small)![](https://image.3001.net/images/20211224/1640337359_61c58fcf96173576dd1cc.png!small)

先生成blf文件，并将800字节的 control record 数据写入其中。  
  
// 2.1生成tmp文件，并写入512KB大小的数据，其中包括仅有_CLFS_LOG_BLOCK_HEADER
结构的损坏数据到其中用于对漏洞点的攻击。在前述blf文件中生成 baselog recoder ：创建 BaseLogRecord 结构，并将 tmp
文件的路径和可以在用户层控制的地址块写入其中。

![](https://image.3001.net/images/20211224/1640337379_61c58fe339d8570de271a.png!small)

// 2.2 使用 NtCreateFile 打开 blf 文件句柄，这时 clfs.sys 将对该文件进行解析，并以此 blf 为 clfs 的
RootDirectory ，打开名为“test”对应由blf 知道的目录相对路径名，实际上就是 tmp 文件的句柄。

![](https://image.3001.net/images/20211224/1640337427_61c59013b039d7c8ddc4a.png!small)

通过Windbg 查看文件句柄，可以查看到这两文件的句柄。  
![](https://image.3001.net/images/20211224/1640337443_61c59023baa0be15a7a4e.png!small)

打开test 名称的文件句柄，可以看到该文件为wct4EFA.tmp文件的路径，且文件对象的DeleteAccess值为0。  
![](https://image.3001.net/images/20211224/1640337456_61c590307a78428b27209.png!small)

// 2.3 最后调用 SetFileInformationByHandle 函数对刚刚创建的 test
文件设置可删除的文件属性并执行删除操作。在成功删除该文件后再次删除 blf 文件时，由于在 clfs 中对其对象未进行有效性检查造成漏洞。

![](https://image.3001.net/images/20211224/1640337474_61c59042919f1922394ca.png!small)

最终在调用 SetFileInformationByHandle 触发漏洞后，由于伪造的CclfsContainer
对象没有完全的校验，导致用户可以对这个对象内的数据进行控制，在进入到内核层后，该对象在进入到
CClfsBaseFilePersisted::RemoveContainer
该函数时，由于用户层可以完全控制该对象的内部数据，导致在内核层使用该回调时可以进入到攻击者指定的内核函数中，比如在第一步通过硬编码获取的 XmXchgOP
，同时函数参数也可以在恶意文件中指定，最终就会造成任意内存地址写。  
![](https://image.3001.net/images/20211224/1640337496_61c59058c705c97cd00bb.png!small)

恶意blf文件头如下：  
![](https://image.3001.net/images/20211224/1640337513_61c5906923ee01feada6b.png!small)

整个利用过程中，触发了两次漏洞，第一次是修改内核中pipe的attribute结构来构造内核读写原语，第二次是替换cmd进程的token。

### 三.内核读写原语与Token复制

该样本使用了NPFS（命名管道文件系统）与 bigpool 的特性来获取 pipe attribute 结构的内核地址，这也算是一种绕过 KASLR
的技巧，与CVE-2021-31955类似。

具体过程为：

// 1.调用 NtCreateNamedPipeFile 创建一个名为"WWWAITER"的命名管道文件，然后调用 NtFsControlFile
控制码为0x110018。0x110018是FSCTL_PIPE_WAIT，暂停这个管道服务器。

// 2.调用 CreatePipe 创建一个匿名管道，并调用 NtFsControlFile
控制码为0x11003C，设置这个管道的attribute，样本中设置了两个pipe attribute。

设置了属性后，在内核中就会分配如下结构体来存放属性。

//PipeAttribute是未公开的结构体

> struct PipeAttribute {  
> LIST_ENTRY list;  
> char * AttributeName;  
> uint64_t AttributeValueSize ;  
> char * AttributeValue ;  
> char data [0];  
> };

其中属性名 AttributeName 和属性值 AttributeValue 是指向数据区 data 不同偏移的两个指针，如果被修改就可以任意地址读。  
![](https://image.3001.net/images/20211224/1640337579_61c590ab155639ea27360.png!small)![](https://image.3001.net/images/20211224/1640337586_61c590b2946ccf0b35804.png!small)

伪代码

// 3.接着调用 NtQuerySystemInformation 查询 SystemBigPoolInformation (0x42)，PoolFlag
== tApN的信息，这样就可以获取到内核中刚才创建的两个pipe attribute结构的地址。

如下R3层代码可以显示BigPool在内核的地址等信息：

> res = NtQuerySystemInformation(SystemBigPoolInformation,  
> bigPoolInfo,  
> 4 * 1024 * 1024,  
> &resultLength);  
>  
> printf("TYPE ADDRESS\tBYTES\tTAG\n");  
> for (i = 0; i < bigPoolInfo->Count; i++)  
> {  
> printf("%s0x%p\t0x%lx\t%c%c%c%c\n",  
> bigPoolInfo->AllocatedInfo[i].NonPaged == 1 ?  
> "Nonpaged " : "Paged ",  
> bigPoolInfo->AllocatedInfo[i].VirtualAddress,  
> bigPoolInfo->AllocatedInfo[i].SizeInBytes,  
> bigPoolInfo->AllocatedInfo[i].Tag[0],  
> bigPoolInfo->AllocatedInfo[i].Tag[1],  
> bigPoolInfo->AllocatedInfo[i].Tag[2],  
> bigPoolInfo->AllocatedInfo[i].Tag[3]);  
> }

相关数据结构如下：  
![](https://image.3001.net/images/20211224/1640337647_61c590ef87165f54cebc1.png!small)![](https://image.3001.net/images/20211224/1640337654_61c590f66df5a7445341e.png!small)

注意：如果是调用 WriteFile 向管道 write_pipe 句柄写入数据，那么 tag 成员字符串是 rFpN ，调用
NtFsControlFile 设置管道属性的tag成员字符串是tApN ，不同 pool 的 tag 字符串可以参见 wdk 的 pooltag.txt
。  
// 4.通过 clfs 漏洞将上一步获取到的内核地址作为目的地址，然后写入想要获取数据的地址，比如 SYSTEM 进程 TOKEN
的地址，再通过下一步就创造出了任意内核地址读原语。  
// 5. 然后用 0x110038 控制码调用 NtFsControlFile
来读取pipe属性值，属性值指针和属性值大小在内核中将被用于读取属性值并返回给用户。因为属性值指针在上一步已经通过漏洞被修改，那么就可以在内核中任意读取数据了，但不能任意写。

![](https://image.3001.net/images/20211224/1640337679_61c5910fd0afb7b5a773a.png!small)

读取pipe attribute属性值

![](https://image.3001.net/images/20211224/1640337719_61c59137d91d8a5f743f7.png!small)将TOKEN写到自身进程EPROCESS

###
四.完成提权创建子进程![](https://image.3001.net/images/20211224/1640337764_61c59164adfeec9a22b2d.png!small)

###
五.整个漏洞利用过程![](https://image.3001.net/images/20211224/1640337784_61c591785a7b8a0ef8e0a.png!small)

## 漏 洞 分 析

下载9月份的补丁，确定补丁的文件是 clfs.sys ，使用 BINDIFF 对比更新前后变化。

补丁后的 clfs 模块中增加了一个名为 CClfsBaseFile::IsValidOffset(ulong) 的函数。

![](https://image.3001.net/images/20211224/1640337811_61c591934957efcdb6687.png!small)

并且，该函数在 CClfsBaseFile::GetSymbol(long,ulong,_CLFS_CONTAINER_CONTEXT * *)
函数流程中用于对数据合法性的校验。

![](https://image.3001.net/images/20211224/1640337832_61c591a822b7e960f59bc.png!small)

通过对更新前后的clfs.sys 文件进行反汇编，并定位到
CClfsBaseFile::GetSymbol(long,uchar,_CLFS_CLIENT_CONTEXT * *) 函数的位置进行分析，跟进
clfs 模块并进入到该函数中，我们发现在更新前的版本中，会直接对传入的第二个参数——BaseLogRecord 对象中的偏移值计算为
_CLFS_CONTAINER_CONTEXT 对象地址并使用，并不会判断该对象的合法性，也即对象内数据是否合法，是否已经损坏。

![](https://image.3001.net/images/20211224/1640337860_61c591c432ba27c7c43c7.png!small)

而在更新后的版本中，在进行地址计算前，通过调用新增的 CClfsBaseFile::IsValidOffset(ulong)
对传入的参数二BaseLogRecord 对象中的偏移地址所求得的 RecordIndex 进行判断，以验证 BaseLogRecord 对象的合法性。

![](https://image.3001.net/images/20211224/1640337897_61c591e9eb1fc541f0ef5.png!small)

### 触发蓝屏

上面提到，漏洞修补后，在CClfsBaseFile::GetSymbol(long,uchar,_CLFS_CLIENT_CONTEXT * *)
函数的入口处，通过调用 CClfsBaseFile::IsValidOffset(ulong) 对传入的参数二 BaseLogRecord
对象中的偏移地址所求得的 RecordIndex 进行判断，用以验证对应的 BaseLohRecord 对象的合法性。

接着转到 CClfsBaseFile::GetSymbol(long,uchar,_CLFS_CLIENT_CONTEXT * *) 函数的上层调用
CClfsBaseFilePersisted::RemoveContainer ，在该函数中，通过调用 GetSymbol 获取容器上下文
_CLFS_CONTAINER_CONTEXT 对象，该结构定义如下。

![](https://image.3001.net/images/20211224/1640337933_61c5920d39996409856da.png!small)

到这里，我们大概知道，由于对于传入的对象未进行完整的有效性检测，导致会将一个包含错误 Container 对象的容器上下文经 GetSymbol
返回，在取得错误的Container
对象后，如果对该对象进行解析，则会造成漏洞。![](https://image.3001.net/images/20211224/1640337954_61c59222666840638220a.png!small)

如果在用户层可以实现对 Container 对象的控制，就可以通过伪造该对象，从而进一步修改这两处的回调函数地址，实现内核的任意函数执行。

事实上，通过分析发现，在用户层通过构造 BaseLogRecord 对象可以实现将伪造的Container向内核传递，并通过释放对应的句柄实现进入
CClfsBaseFilePersisted::RemoveContainer
函数内进行利用。通过分析样本程序，我们得到了上述利用过程。接着，通过对漏洞利用程序中的伪造Container
进行修改，实现对漏洞利用的回调函数进行干预，触发蓝屏。

![](https://image.3001.net/images/20211224/1640337980_61c5923c5d918c5463ff1.png!small)

![](https://image.3001.net/images/20211224/1640337989_61c5924588302e313f7c2.png!small)

毫无疑问，当执行到此处的时候，内核由于调用非法内存空间造成蓝屏。

![](https://image.3001.net/images/20211224/1640338011_61c5925b2439ddffd3b82.png!small)

### 总结

漏洞原理就是 clfs.sys 驱动对 Base Log Record 的数据处理存在一处缺陷，导致攻击者可以通过精心构造的BaseLog Record
来传入一个伪造的 CclfsContainer 对象。由于被伪造的 CclfsContainer
对象数据完全可控，攻击者通过伪造CclfsContainer对象的虚函数表和其他数据，劫持了CClfsBaseFilePersisted::RemoveContainer函数内调用的两个虚函数CClfsContainer::Release
和 CClfsContainer::Remove，并结合其他伪造的数据实现了一个任意地址写入原语，可以将任意数据写到任意内核地址。

### 威胁评估

该漏洞不仅可以在本地利用，在 webshell 中也可以利用，致使该漏洞的实际威胁程度上升。建议用户重视该漏洞的威胁性，即时安装官方提供的补丁。

在win8以后的系统中，低信任级别的程序不再有权限调用NtQuerySystemInformation查询SystemBigPoolInformation和SystemModuleInformation，因此该样本的利用方式在沙盒程序中是无效的。

> 注：
>
> 1、本文仅为宁静之盾斩月实验室技术交流文章，旨在提升安全防御水平。
>
> 2、目前厂商已发布升级补丁以修复漏洞，补丁获取链接：
>
> https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-36955

 **参考链接：**

[1]https://www.4hou.com/posts/AWJj

[2]https://gbhackers.com/new-malware-family-using-clfs-log-files-to-evade-detection/

[3]https://docs.microsoft.com/en-us/previous-versions/windows/desktop/clfs/common-log-file-system-functions

[4]https://blog.csdn.net/weixin_33955681/article/details/87981469

[5]https://zhuanlan.zhihu.com/p/364188890

[6]https://paper.seebug.org/1743/

[7]https://paper.seebug.org/324/

