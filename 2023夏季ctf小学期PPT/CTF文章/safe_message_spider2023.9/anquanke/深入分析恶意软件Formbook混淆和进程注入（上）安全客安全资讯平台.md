# 深入分析恶意软件Formbook：混淆和进程注入（上）

阅读量 **215377**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-04-03 14:03:30

 **x**

##### 译文声明

本文是翻译文章，文章原作者 RÉMI JULLIAN，文章来源：thisissecurity.stormshield.com

原文地址：<https://thisissecurity.stormshield.com/2018/03/29/in-depth-formbook-malware-analysis-obfuscation-and-process-injection/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01ca12b3ba9eabc7b1.jpg)

传送门：[深入分析恶意软件Formbook：混淆和进程注入（下）](https://www.anquanke.com/post/id/103429)

## 一、介绍

Formbook是用C语言和x86汇编语言编写的窗体捕获和窃取的恶意软件。这是一个已经准备售卖的恶意软件，可以被任何不具备恶意软件开发技能的犯罪分子所使用。在通过邮件分发Formbook样本的期间，我们捕获到一个Word文档样本，并作为本文的分析样本。我们使用了基于云的沙盒引擎Breach
Fighter（ <https://www.stormshield.com/products/breach-fighter/>
）对该样本进行了捕获，并且使用该引擎对样本文件进行了分析。  
此前，我们曾经发表过一篇文章（ <https://thisissecurity.stormshield.com/2017/09/28/analyzing-form-grabber-malware-targeting-browsers/>
），文中对于一个简单的窗体捕获类恶意软件进行了分析，该恶意软件主要用于捕获常见浏览器发出的HTTP请求，以窃取用户密码。在该篇文章中，我们讨论了内联钩子的机制。除此之外，我们注意到目前已经有一些关于Formbook的文章发布。第一篇文章由Arbor
Networks发布于2017年9月（ <https://www.arbornetworks.com/blog/asert/formidable-formbook-form-grabber/> ），主要讲解了该恶意软件所使用的混淆方法。第二篇文章发由FireEye发布于2017年10月（
<https://www.fireeye.com/blog/threat-research/2017/10/formbook-malware-distribution-campaigns.html>
），主要分析该恶意软件的功能，并且涉及到一些混淆的技巧。考虑到上述已有的研究成果，我们决定关注一些新的细节，因此本文将涉及到以下内容：  
1、Formbook所使用的混淆方法，以及对其进行逆向工程的过程；  
2、反调试、反沙盒技巧；  
3、如何使用IDA Python来进行自动分析；  
4、Formbook如何通过浏览器的线程劫持和APC注入来进行进程镂空（Process Hollowing）。

## 二、反分析技巧

###  2.1 字符串加密

通过该恶意软件的字符串命令，我们并没有获知该恶意软件的运行流程。其原因在于，该恶意软件所使用的所有字符串都是混淆或加密的。关于加密字符串的存储和所使用的加密算法，我们在“数据加密”这一节进行了详细说明。

###  2.2 字符串散列

恶意软件通常会试图使用尽可能少的（加密后的）字符串。举例来说，如果要检查内存中是否存在某个字符串（例如进程名称），恶意软件并不会将已经加密的字符串进行解密后再执行比较，而是会对获取到的字符串运行散列函数，并检查其是否与此前预先计算的散列值相匹配。  
Formbook使用的散列函数是BZip2 CRC32，该函数会应用于已经转换为小写字母的字符串：

    
    
    >>> from crccheck.crc import Crc32Bzip2
    >>> hex(Crc32Bzip2.calc(bytearray("NtCreateProcessEx".lower())))
    '0xf653b199L'
    

在本文中，每个对字符串散列的引用都指向了关联字符串的BZip2 CRC32散列。

###  2.3 数据加密

恶意软件存储于加密的缓冲区，会直接隐藏在文本部分。由于该恶意软件使用了一个常见的技巧，所以我们能够逐一地将每个加密缓冲区的地址都检索出来。由于调用指令会将从被调用方返回时要执行的指令地址压入堆栈，所以一个操作数为0x00000000的调用指令（0xE8）会在调用后的地址处进行跳转。随后，可以使用以下“pop
eax”指令来检索当前指令的指针值，从而找到加密缓冲区的起始位置，是位于两个字节之后：  
  
在Arbor Networks的文章中，已经对这种机制进行了描述，并且发布了一个Python脚本（
<https://github.com/tildedennis/malware/blob/master/formbook/formbook_decryption.py>
），该脚本中包含两个解密函数decrypt_func1()和decrypt_func2()，用于对这种加密后的缓冲区进行解密。其中，decrypt_func1()函数使用比解密输出缓冲区大的输入缓冲区作为参数，原因在于一些字节要被用于描述该进行哪种转换的“操作码”。而decrypt_func2()函数会对输入缓冲区进行两次简单转换，随后使用长度为20字节的密钥（由SHA-1消息摘要产生）执行RC4解密，并在输入缓冲区进一步应用两个更为简单的转换操作。

###  2.4 解密已加密的哈希数组

接下来，我们来研究一下在恶意软件的早期分析阶段是如何使用这两个函数的，特别是解密包含多个哈希值的数组。通过了解这一部分内容，能使我们更好地进行后续执行动态加载分析和反调试、反沙盒技巧学习。  
两个加密的缓冲区encbuf1和encbuf3被分配给decrypt_func1()函数，并且其输出将用于计算两个SHA-1哈希值，这两个值会作为RC4的密钥（rc4_key_one和rc4_key_two）使用。第三个加密缓冲区encbuf2首先提供给decrypt_func1()函数，随后会使用之前生成的RC4密钥rc4_key_one将其提供给decrypt_func2()函数。使用decrypt_func2()函数和RC4密钥rc4_key_two解密生成的缓冲区，从而得到encbuf2_s3。最后，通过计算该缓冲区的SHA-1以获得最终的RC4密钥。下图说明了上述的过程：  
  
我们编写了一个用于解密哈希数组并打印关联字符串的IDA Python脚本，并在GitHub上发布（
<https://github.com/ThisIsSecurity/malware/blob/master/formbook/formbook_decrypt_hash_string.py>
）。为了找到于动态加载函数相关的散列值，我们修改了shellcode_hashes插件（
<https://github.com/fireeye/flare-ida/tree/master/shellcode_hashes>
），增加了对BZip2
CRC32的支持。由于加密的数组还包含用于进行反调试和反沙盒的字符串散列，因此我们编写了另一个用于请求包含可能被恶意软件使用的字符串的JSON文件的Python脚本。该脚本同样可以用于借助字符串散列分析其他恶意软件，所以我们也在GitHub上发布了这一脚本（
<https://github.com/ThisIsSecurity/sinkhole/tree/master/malware_hash>
），并且将在发现新的恶意软件时对其进行更新。希望大家能够积极发起Pull Request，以便我们改进JSON知识库。  
在执行IDA Python脚本后，我们可以发现其动态函数加载过程以及反VM、反沙箱和反分析的技巧。

    
    
    12 0xf653b199 NtCreateProcessEx
    13 0xc8c42cc6 NtOpenProcess
    ..
    ..
    79 0x3ebe9086 vmwareuser.exe
    80 0x4c6fddb5 vmwareservice.exe
    ..
    83 0x85cf9404 sandboxiedcomlaunch.exe
    84 0xb2248784 sandboxierpcss.exe
    85 0xcdc7e023 procmon.exe
    86 0x11f5f50 filemon.exe
    ..
    ..
    114 0x24a48dcf guard32.dll
    115 0xe11da208 SbieDll.dll
    

本Formbook样本运行脚本后得到的完整输出内容可以在我们的GitHub上获得（
<https://github.com/ThisIsSecurity/malware/blob/master/formbook/func_index_hashes.txt>
）。我们的分析文件格式基于Arbor
Network分析结果的格式，详细参考此文件：<https://github.com/tildedennis/malware/blob/master/formbook/func_index_hashes.txt>
。

###  2.5 手动映射NTDLL的副本

正如我们在CFF Explorer中看到的那样，Formbook的导入目录表（Import Directory
Table）为空，这通常意味着可能会存在动态函数加载的情况：  
  
即使在导入表中没有引用DLL，Windows加载程序也会在进程地址空间中加载ntdll.dll。基于用户空间钩子的安全解决方案经常会拦截ntdll.dll中的函数来监视进程活动。为了避开监控，Formbook映射了该DLL的一个副本，并通过该DLL与操作系统进行许多交互。FireEye在他们的文章中将这种方法称为“Lagos
Island方法”。在本节中，我们将详细描述Formbook是如何执行此操作的。  
大家可能了解，存储在磁盘上的DLL视图和映射到内存中的DLL视图是不一样的，这是由于受到了PE文件格式规范的限制。为了能够分页，就要求每个节在映射到内存中时都必须保证从虚拟地址开始，该虚拟地址需要是IMAGE_OPTIONAL_HEADER.SectionAlignment（默认为0x1000）的倍数。另外，在PE文件中，构成每个节的原始数据都要以IMAGE_OPTIONAL_HEADER.FileAlignement（默认为0x200）的倍数开始。磁盘上每个节的大小，总会取整为IMAGE_OPTIONAL_HEADER.FileAlignement的倍数。但针对内存中的节，则理论上不需要将其取整为IMAGE_OPTIONAL_HEADER.SectionAlignment的倍数（实际上操作系统会分配4KB大小的页）。关于这一部分的更多信息，可以阅读Win32可移植可执行文件格式的相关说明（
<https://msdn.microsoft.com/en-us/library/ms809762.aspx> ）。  
接下来，就让我们看看Formbook是如何处理这些PE规范，以便复制并映射其自身版本的ntdll.dll：

####  2.5.1 检索原始ntdll的完整路径

为了检索由Windows映像加载器加载的ntdll基地址，Formbook使用了一个名为get_module_base_address_by_hash()的函数。该函数会遍历LIST_ENTRY
“InMemoryOrderModuleList”中的每一个LDR_DATA_TABLE_ENTRY条目，以计算出映像名称（LDR_DATA_TABLE_ENTRY.BaseDllName）的散列值，并检查该值是否与参数中的值相匹配。  
如果匹配，则会返回DLL基地址。随后，会使用另一个我们命名为get_module_data_table_entry_by_base_address()的函数，该函数功能大体相似，但会在LDA_DATA_TABLE_ENTRY条目中返回一个指针，其中包含基地址的条目（如果找到）。从该条目中，可以提取原始ntdll模块的完整路径（LDR_DATA_TABLE_ENTRY.FullDllName）。

####  2.5.2 将ntdll的原始副本从磁盘转到内存

接下来，是使用先前检索到的完整路径，将ntdll的原始副本从磁盘转到内存中执行，这一过程是通过以下步骤进行的：  
1、使用NtCreateFile()与’FILE_OPEN’ CreateDisposition获取磁盘上ntdll.dll的句柄；  
2、使用NtQueryInformationFile()与类’FileStandardInformation’检索ntdll大小；  
3、使用RtlAllocateHeap()分配适当大小的缓冲区，用于存储文件副本；  
4、使用NtReadFile()将原始文件从磁盘读取到内存中。

####  2.5.3 将原始副本中的ntdll头部和节映射到内存中

如前所述，在磁盘上和在内存中的PE文件视图是不一样的。因此，我们将ntdll的副本从磁盘转移到内存中之后，需要进行以下步骤：  
1、检查原始复制缓冲区中的MZ头和PE头（0x4550）；  
2、从可选头部读取SizeOfImage字段，并使用NtAllocateVirtualMemory()分配相应大小的缓冲区（新映射的DLL缓冲区）；  
3、从Optional Header中读取SizeOfHeaders字段并复制PE头部；  
4、从COFF Header读取NumberOfSections；  
5、对于节表中的每个节，读取RawSize、RawAddress、VirtualSize和VirtualAddress字段；  
6、从ntdll.dll文件的缓冲区中,复制大小为VirtualSize的每个节，从偏移量RawAddress开始，直至偏移量为VirtualAddress的新手动映射的DLL。  
到现在，ntdll的手动映射版本会以几乎类似于被Windows
Loader映射的方式加载，因此可以被Formbook使用。在这里，有一个非常重要的区别是，手动映射的DLL是在一个单独的提交区域中，由PAGE_EXECUTE_READWRITE进行保护。而由Windows
Loader加载的版本会被映射到具有充分保护的几个提交区域中（例如，PE头部对应的是PAGE_READONLY，.text段对应的是PAGE_EXECUTE_READ）。

###  2.6 在进程地址空间中加载额外的DLL

除了使用本地API的未公开函数之外，Formbook还使用由DLL（如kernel32.dll或user32.dll）导出的更高级别的函数。
这些DLL使用来自手动映射的ntdll实例的未记录函数LdrLoadDll()加载到进程地址空间中。
用于动态解析LdrLoadDll()的方法将在下一节中详细介绍。

###  2.7 动态函数加载

通过执行动态函数加载，可以解析包含在ntdll.dll手动映射版本和使用LdrLoadDll()加载的其他DLL中的地址。我们使用名为import_func_by_hash的函数，在进程地址空间中找到相应DLL的地址以及所需要的函数名称哈希值，从而加载函数。其工作原理如下：  
1、检查相应DLL基址的MZ头和PE头（0x4550）；  
2、从Optional
Header中读取SizeOfExportTable和ExportTable（RVA）字段；3、从导出表中读取AddressOfNames（RVA）、NumberOfNames、AddressOfFunctions（RVA）、NumberOfFunction和AddressOfNameOrdinals（RVA）字段；  
4、对于字符串数组指针AddressOfNames的每个条目，计算函数名称的哈希值并检查是否与预期的哈希值相匹配；  
5、如果匹配，从WORDs数组中的AddressOfNameOrdinals获取函数的索引；  
6、从前面读取的索引处，函数地址AddressOfFunctions数组中，读取函数的地址（RVA）。  
函数的地址（RVA）最终被添加到DLL基地址中，并通过Formbook缓存在导入的函数指针数组中。如果Formbook需要再次调用此函数，就不用重新进行加载。

###  2.8 反调试、反分析技巧

在Formbook映射了其ntdll副本之后，就可以执行恶意操作了。在本小节中，我们将主要讲解Formbook所使用的几种自身防护方法：  
1、检查被安全工具挂钩的系统调用；  
2、检查正在运行的进程是否与黑名单匹配；  
3、检查是否有与黑名单匹配的注入的DLL；  
4、检查是否处于调试、虚拟化或沙盒环境。  
在执行每项检查之后，其检查结果都存储在自定义结构的相应字节中。随后将会检查该结构中的每个字段，从而决定该进程是否要终止执行。如果上述检查中发现一项或一项以上的异常，那么该函数会返回0：  
  
比较麻烦的是，在调试这个恶意软件的过程中，如果只修改这个函数的返回值是不够的。实际上，一旦恶意软件发现问题，还会修改加密哈希数组中的一些哈希值，从而导致动态函数加载过程失败。

####  2.8.1 检查WOW32Reserved挂钩

由于Formbook是一个32位的PE，为了检查其自身是否在以WOW64兼容模式（即在64位Windows操作系统上运行的32位PE）运行，它会检查ntdll.dll的完整路径是否包含“wow64”。  
当PE文件以wow64模式运行时，特定的32位版本的ntdll将会被映射，每个系统调用例程都会以对[fs:0xc0]的调用作为结束。但在Windows
10上除外（ <https://www.malwaretech.com/2015/07/windows-10-system-call-stub-changes.html>
），然而出于兼容性考虑，[fs:0xc0]仍然可用。这实际上是对包含在TEB结构中的字段Wow32Reserved中地址的调用，会启动位于wow64cpu.dll中的例程。该例程通过执行带有段选择子（Segment
Selector）0x33的跳转指令，将本地代码从32位转换为64位。  
  
为了追踪wow64模式下PE所执行的系统调用，我们可以在Wow32Reserved字段设置一个钩子。这一过程可以使用Stealth64 OllyDbg插件（
<https://www.virusbulletin.com/virusbulletin/2010/08/anti-unpacker-tricks-part-eleven> ）进行。其目的在于，用自定义代码部分的地址替换WoW32Reserved字段，从而阻断系统调用。  
为了检查是否部署了钩子，Formbook会执行以下步骤来检查Wow32Reserved字段是否指向了属于PE64
DLL的代码段（即wow64cpu.dll）：  
1、使用类MemoryBasicInformation调用NtQueryVirtualMemory()以检索WOW32Reserved的AllocationBase（即wow64cpu.dll基地址）；  
2、解析PE DOS头部并提取定义PE文件类型的COFF Magic；  
3、检查COFF Magic是否等于0x020B（表示文件是PE64）。

####  2.8.2 检查加载的DLL是否与黑名单匹配

Formbook会检查是否将模块SbieDll.dll（ <https://www.sandboxie.com/>
）加载到其地址空间中。为完成这项工作，它使用了我们之前所提及的名为get_dll_base_address_by_hash()的函数。如果找到预期的校验和（SbieDll.dll对应着0xe11da208），该函数将返回此模块的基址，并修改与此项检查相关的标志。

####  2.8.3 检查当前运行的进程是否与黑名单匹配

为了检查当前正在运行的进程是否与黑名单匹配，Formbook使用类SystemProcessInformation来调用NtQuerySystemInformation()。随后，遍历每个SYSTEM_PROCESS_INFORMATION条目，以计算字段ImageName的散列值。如果有散列值与黑名单相匹配，则会检查加密散列数组（从偏移量79到98）。  
从解密的哈希列表（
<https://github.com/ThisIsSecurity/malware/blob/master/formbook/func_index_hashes.txt>
）中，我们发现其包含如下映像名称：

    
    
    79 0x3ebe9086 vmwareuser.exe
    80 0x4c6fddb5 vmwareservice.exe
    81 0x276db13e vboxservice.exe
    82 0xe00f0a8e vboxtray.exe
    83 0x85cf9404 sandboxiedcomlaunch.exe
    84 0xb2248784 sandboxierpcss.exe
    85 0xcdc7e023 procmon.exe
    86 0x11f5f50 filemon.exe
    87 0x1dd4bc1c wireshark.exe
    88 0x8235fce2 netmon.exe
    89 0x21b17672 unknown
    90 0xbba64d93 unknown
    91 0x2f0ee0d8 prl_cc.exe
    92 0x9cb95240 unknown
    93 0x28c21e3f vmtoolsd.exe
    94 0x9347ac57 vmsrvc.exe
    95 0x9d9522dc vmusrvc.exe
    96 0x911bc70e python.exe
    97 0x74443db9 perl.exe
    98 0xf04c1aa9 regmon.exe
    

####  2.8.4 检查是否存在调试器

Formbook通过调用两个不同类中的NtQuerySystemInformation()来检查它是否正处于调试模式之中：  
SystemKernelDebuggerInformation：用于检查是否连接了Ring 0的调试器；  
ProcessDebugPort：用于检查是否连接了Ring 3的调试器。  
PEB结构中的BeingDebugged字段稍后也会用于Formbook，只要连接了用户级调试器，就会从无限循环中断。

####  2.8.5 检查进程映像名称是否与黑名单匹配

Formbook会检查自身的映像名称（BaseDllName）是否以哈希为0x7c81c71d的字符串结尾。这一检查可能是针对某个特定的沙盒环境，该沙盒会在执行前更改PE文件的映像名称。

####  2.8.6 检查加载的模块路径是否与黑名单匹配

Formbook会检查加在的模块是否位于7个黑名单路径之中。为实现该项检查，它将遍历LIST_ENTRY
“InMemoryOrderModuleList”，提取每个模块的完整路径（FullDllName）并计算每个目录完整路径的哈希值。然后，在加密散列数组（从偏移量99到105）中检查每个散列值。在研究过程中，我们未能发现黑名单中所包含的目录名称。如果您有所发现，期待能够告知，我们会对解密哈希列表（
<https://github.com/ThisIsSecurity/malware/blob/master/formbook/func_index_hashes.txt>
）进行更新。

####  2.8.6 检查用户名是否与黑名单匹配

Formbook使用带有变量名“USERNAME”的RtlQueryEnvironmentVariable_U()函数，从环境中检索用户名。随后，它在加密散列数组中（从偏移量106到112）检查用户名是否与黑名单相匹配。根据解密的哈希列表，我们发现黑名单中包含如下内容：

    
    
    106 0xed297eae cuckoo
    107 0xa88492a6 sandbox-    108 0xb21b057c nmsdbox-    109 0x70f35767 xxxx-ox-    110 0xb6f4d5a8 cwsx-    111 0x67cea859 wilbert-sc
    112 0xc1626bff xpamast-sc
    

该恶意软件是一个较为复杂的恶意软件，通过对其进行透彻地分析，可以使我们对于混淆和进程注入的理解有所提升。在下篇中，作者对该恶意软件如何进行进程注入展开详细的分析，希望大家继续关注！

本文翻译自thisissecurity.stormshield.com
[原文链接](https://thisissecurity.stormshield.com/2018/03/29/in-depth-formbook-malware-analysis-obfuscation-and-process-injection/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **P!chu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/103403](/post/id/103403)

安全客 - 有思想的安全新媒体

本文转载自:
[thisissecurity.stormshield.com](https://thisissecurity.stormshield.com/2018/03/29/in-depth-formbook-malware-analysis-obfuscation-and-process-injection/)

如若转载,请注明出处： <https://thisissecurity.stormshield.com/2018/03/29/in-depth-formbook-malware-analysis-obfuscation-and-process-injection/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [样本分析](/tag/样本分析)
  * [哈希](/tag/哈希)
  * [Formbook](/tag/Formbook)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhimg.com/t01bd1dba67fe13cdc6.png) P!chu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

