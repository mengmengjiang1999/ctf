作者： 0x1

# 写在前面

对于Windows
PE文件结构，个人认为还是非常有必要掌握和了解的，不管是在做逆向分析、免杀、病毒分析，脱壳加壳都是有着非常重要的技能。但是PE文件的学习又是一个非常枯燥过程，希望本文可以帮你有一个了解。

# PE文件结构的基本介绍

先来大概说说什么是PE文件格式，PE(Portable
Executable)，也就是我们说的可执行文件，在Windows中exe,dll,sys,ocx文件都是PE文件格式。而PE文件结构就是所有的PE文件按照结构的方式组织是有规律的排列组成。  
从整个PE件结构大概来分成2部分,PE头和PE体。PE头又存在MS-DOS头和NT头(PE头)，PE体主要就是一些表结构构成,存放代码，数据，资源等。后面我们开始对这些信息进行逐一分析和讲解。

# MS-DOS头

首先来看DOS头，DOS头位于整个PE文件的首位部分，是PE文件结构的第一个头，对于现在的系统来说，作用就是用来定位真正的PE头。在peview中可以看到对应IMAGE_DOS_HEADER和MS-DOS Stub Program，IMAGE_DEBUG_TYPE这里可以忽略，是调试类型，对应debug和relese。  
![图片.png](https://image.3001.net/images/20220415/1649987372_6258cf2cbe72f263e729c.png!small)  
在二进制中查看，以4D 5A开头,十六进制转ASCII码就是MZ，是MS-DOS设计者名字缩写  
![image](https://image.3001.net/images/20220415/1649987539_6258cfd3a4b3664e712f3.jpg!small)  
在010
editor或者peview中，可以看到header占位在00000000-0000003C,而整个大小是64字节，额外需要注意的字节顺序，以小尾方式存在。  
![image](https://image.3001.net/images/20220415/1649987618_6258d022231d5ab4a3f03.jpg!small)  
来看具体的IMAGE_DOS_HEADER是在winnt.h中定义，对于我们来说，我们只关心两个参数，e_magic是程序的头指纹和e_lfanew是指向真正PE头偏移地址。  
![image](https://image.3001.net/images/20220415/1649987654_6258d0465cf6cadf0b99e.jpg!small)  
这里我们可以尝试修改上面程序，将除了e_magic和e_lfanew对应的地址全部修改成0,可以看到程序还是可以正常运行。所以有用的数据只占6个字节（e_magic为WORD型占2个字节，e_lfanew为DWORD型占4个字节）  
![image](https://image.3001.net/images/20220415/1649987679_6258d05f545f445b5d006.jpg!small)  
![image](https://image.3001.net/images/20220415/1649987693_6258d06db04db713631f7.jpg!small)  
MS-DOS stub Program是DOS头的代码块，告诉用户程序不能在DOS下运行。  
![image](https://image.3001.net/images/20220415/1649987715_6258d083b494d1ee55947.jpg!small)

# NT头(PE头)

PE头以50 45 00 00 开头,也就是PE..  
![image](https://image.3001.net/images/20220415/1649987765_6258d0b5899923cbda984.jpg!small)  
来看下PE头结构IMAGE_NT_HEADERS，包括3个部分，Signature,IMAGE_FILE_HEADER,IMAGE_OPTIONAL_HEADER32(或64)，而PE..就是Signature字段，这个字段是PE文件标准特征，是不能进行修改的，强行修改后程序无法正常运行。  
![image](https://image.3001.net/images/20220415/1649987790_6258d0ce7a3977e7e3d7b.jpg!small)  
IMAGE_FILE_HEADER共20字节，其中重要有4个部分，从010editor中可以看到Machine,NumberOfSections,TimeDateStamp,Characteristics这4个部分是最重要的。  
![image](https://image.3001.net/images/20220415/1649987810_6258d0e26913911ebe111.jpg!small)  
![image](https://image.3001.net/images/20220415/1649987826_6258d0f2cf4b4ae05a54b.jpg!small)

### Machine

共4个字节头两个字节表示机器类型，用于标识CPU的类型，后两个字节表示CPU为Intel
386或后继处理器及其兼容处理器。具体机器类型的值可以在010中自行查看。  
![image](https://image.3001.net/images/20220415/1649987884_6258d12ced3269f43dd50.jpg!small)

### NumberOfSections

表示节的数目,这里的节的数目指的就是区段表的数量，这里我们显示5，说明有个区段表数。  
![image](https://image.3001.net/images/20220415/1649987930_6258d15ac5c5bdc24d19f.jpg!small)

也可以利用lordpe查看区段表。  
![image](https://image.3001.net/images/20220415/1649987970_6258d1825203e729b15e5.jpg!small)

### TimeDateStamp

为时间戳，也就是PE文件创建的时间。

### Characteristics

文件属性的标志，共15个常用属性标志，每个bit都有不同含义，如下在010中可以看到:  
我们从上往下进行看：  
`IMAGE_FILE_RELOCS_STRIPPED:为1表示文件中没有重定向信息`  
`IMAGE_FILE_EXECUTABLE_IMAGE:为1表示该文件是可执行文件`  
`IMAGE_FILE_LINE_NUMS_STRIPPED:为1表示文件中不存在行信息`  
`IMAGE_FILE_LOCAL_SYMS_STRIPPED:为1表示没有局部符号信息`  
`IMAGE_FILE_AGGRESIVE_WS_TRIM:表示调整工作集`  
`IMAGE_FILE_LARGE_ADDRESS_AWARE:为1表示程序能处理大于2G的地址`  
`IMAGE_FILE_BYTES_REVERSED_LO:小尾方式`  
`IMAGE_FILE_32BIT_MACHINE:为1只在32位平台上运行`  
`IMAGE_FILE_DEBUG_STRIPPED:为1不包含调试信息`  
`IMAGE_FILE_REMOVABLE_RUN_FROM_SWAP:为1不能从可移动盘运行`  
`IMAGE_FILE_NET_RUN_FROM_SWAP:为1不能从网络运行`  
`IMAGE_FILE_SYSTEM:为1表示文件为系统文件而不是程序`  
`IMAGE_FILE_DLL:为1表示是一个dll文件`  
`IMAGE_FILE_UP_SYSTEM_ONLY:为1表示文件只能运行于单处理器机器上`  
`IMAGE_FILE_BYTES_REVERSED_HI:大尾方式`  
![image](https://image.3001.net/images/20220415/1649988027_6258d1bb5b52e07b65c4c.jpg!small)

再来看看PE头下的可选头IMAGE_OPTIONAL_HEADER,它是PE头部重要的部分，之所以被称为可选头是指该结构体的部分数据在不同文件中是不同的。  
![image](https://image.3001.net/images/20220415/1649988151_6258d23764359c06b5a77.jpg!small)

同样，对照010中对不同的PE文件可进行分析查看修改。  
![image](https://image.3001.net/images/20220415/1649988186_6258d25abf54d6c42ac10.jpg!small)

# 节表

PE文件所有的节属性都定义节表中，节表是由IMAGE_SECTION_HEADER结构排列而组成的，且节表的位置在MS-DOS+PE头下面。  
![image](https://image.3001.net/images/20220415/1649988220_6258d27cde2c03f8a6d4f.jpg!small)

IMAGE_SECTION_HEADER结构  
![image](https://image.3001.net/images/20220415/1649988253_6258d29db7698d90e1e45.jpg!small)

对于上面的字段来说，我们来说一说重要的的字段。在说字段前，再把三个地址概念复习下,后面会具体说地址转换计算。  
`1.VA：VirtualAddress虚拟内存地址，范围00000000h - 0fffffffh，就是进程的基地址 + RVA相对虚拟内存地址。
2.RVA：相对虚拟内存地址。
是PE文件中的数据、模块等运行在内存中的实际地址相对PE文件装载到内存的基址之间的距离。如果PE文件装入虚拟地址(VA)空间的400000h处，且进程从虚址401000h开始执行，我们可以说进程执行起始地址在RVA
1000h。 3.FOA：文件偏移地址，文件头的偏移地址。`

### NAME

8个字节ASCII的名称，必须要8个字节，不够可以用null值来填充，这里的名称可以自己起也可以编译器来定义。  
![image](https://image.3001.net/images/20220415/1649988321_6258d2e1931c17dbd23f6.jpg!small)

### VirtualSize

对应表的区块的大小，这是区块的数据在没有进行对齐处理前的实际大小，通俗的来说就是节的数据真实大小。

### VirtualAddress

该区块装载到内存中的RVA 地址。

### SizeOfRawData

文件偏移量（文件大小）

### PointerToRawData

指出节在磁盘文件中所处的位置。这个数值是从文件头开始算起的偏移量。

### Characteristics

节的属性，可读写等。

# 地址转换

前面说到三个地址，学习地址转化可以对程序的一些功能修改或添加，地址转化非常重要，后面的加密，对壳的操作，对感染性病毒修复都非常关键。  
还是以前面的程序节表来看。  
![image](https://image.3001.net/images/20220415/1649988401_6258d3318bab1d4ee33d9.jpg!small)

我们来计算hello world!字符串偏移地址。  
![image](https://image.3001.net/images/20220415/1649988436_6258d35401b93188bfb79.jpg!small)

首先可以看到字符串起始位置是983006，结束在983011。  
![image](https://image.3001.net/images/20220415/1649988460_6258d36cd662cd2df0c1a.jpg!small)

计算过程：

1.通过VA转RVA  
用起始位置-程序入口地址，程序入口地址980000,也就是  
983006-980000 = 3006 RVA地址  
这里说明一点，计算是十六进制计算，后面都一样。

2.找RVA所在的节  
可以看到3006是在.data0983000到0098400之间，所以所属的节是.data  
![image](https://image.3001.net/images/20220415/1649988499_6258d3938abac520f9bc3.jpg!small)  
3.计算.data节起始的RVA和起始的FOA的差值  
3000-A00=2600

4.通过RVA减去差值  
3006-2600 = A06  
用010打开exe程序，可以看到字段起始和我们计算出来的一致  
![image](https://image.3001.net/images/20220415/1649988538_6258d3bae8ea7bf38162c.jpg!small)

在lordpe中直接算偏移量,可以看到和我们算出的一致。  
![image](https://image.3001.net/images/20220415/1649988565_6258d3d57816e645b1213.jpg!small)

# 添加节，给程序做入口弹框

对于加壳保护，病毒来说，一般情况下都会添加节，会将可执行程序保护的代码或者将病毒代码写在新添加的节中。  
步骤：1.增加节表项；2.修正文件的映像程度；3.修正一个节的数量；4.增加文件的节数据。

以PEview程序为例，添加一个弹框。  
用lordpe打开程序，首先看到区段表数量是5  
![image](https://image.3001.net/images/20220415/1649988605_6258d3fd4509cf065ae7c.jpg!small)  
选择一个表名称，右键-添加区段  
![image](https://image.3001.net/images/20220415/1649988626_6258d41236776fdaa4915.jpg!small)

将所有的地址记下来  
00015000 00000000 00010A00 00000000 E00000E0  
对于不清楚含义的可以再回头看看  
![image](https://image.3001.net/images/20220415/1649988694_6258d45635bbd495ac39b.jpg!small)

先将映射入内存后的长度（虚拟大小）改为1000，将磁盘文件中的长度（物理大小）改为200  
![image](https://image.3001.net/images/20220415/1649988723_6258d4735d56a363d2cc6.jpg!small)

在区段标志（节属性）中，将可写和初始化去掉，节属性变成60000020。  
![image](https://image.3001.net/images/20220415/1649988750_6258d48e8819191779686.jpg!small)

字节大小转换：  
前面我们插入200长度大小，为16进制，转换成10进制为512个字节  
将程序使用010打开，在文件末尾添加512个字节，可以看到最末一个是109FF,109FF+1刚好是10A00  
![image](https://image.3001.net/images/20220415/1649988793_6258d4b93e2959d7f743a.jpg!small)

所以添加数据从最后一位插入512个字节数据  
![image](https://image.3001.net/images/20220415/1649988841_6258d4e903dc7f2da59ec.jpg!small)

修正大小，前面将虚拟内存的大小修改为1000，镜像大小还是15000，发现程序是无法运行的  
![image](https://image.3001.net/images/20220415/1649988867_6258d503b3944f39ca688.jpg!small)

将镜像大小修正为16000  
![image](https://image.3001.net/images/20220415/1649988895_6258d51fcb77825df4e53.jpg!small)

再次打开可以运行  
![image](https://image.3001.net/images/20220415/1649988926_6258d53ec4464959005ab.jpg!small)

接下来添加我们需要的程序。  
反编译进行调试，发现程序入口的位置是00401000，再往下走程序就运行了。  
![image](https://image.3001.net/images/20220415/1649988954_6258d55a6803ea5e5f627.jpg!small)

前面我们说过程序的入口是imagebase（基地址）+entrypoint（入口点）组成，我们回头再验证一下，加起来为00401000一致。  
![image](https://image.3001.net/images/20220415/1649988973_6258d56d885e957421b39.jpg!small)

所以需要程序从我们给添加的节开始执行，我们添加的节是00015000，所以需要让入口点修改为我们的节地址。新的入口点00415000。  
![image](https://image.3001.net/images/20220415/1649989002_6258d58ad863b72707ef8.jpg!small)

选定00415020，右键转储跟随选定的地址。  
![image](https://image.3001.net/images/20220415/1649989040_6258d5b06df6238a0de86.jpg!small)

编辑内容，同样在00415030出编辑内容。  
![image](https://image.3001.net/images/20220415/1649989127_6258d6077b3c8a7b8a5fd.jpg!small)

在程序入口处00415000写入弹框  
![image](https://image.3001.net/images/20220415/1649989145_6258d6197ae930a45a320.jpg!small)

然后再入口处F8单步调试，发现成功弹框。  
![image](https://image.3001.net/images/20220415/1649989171_6258d633e66491c59f5c0.jpg!small)

然后还没有成功，这里只是弹框，没有打开我们PEview主程序，还需要进行跳转，跳转的位置就是最开始的00401000这个位置，jmp
00401000,然后步入，可以发现主程序打开。  
![image](https://image.3001.net/images/20220415/1649989195_6258d64b40750d87e7cde.jpg!small)

接着保存数据，修改的数据全部选中，右键复制到可执行文件  
![image](https://image.3001.net/images/20220415/1649989215_6258d65fe980bca8cb8ec.jpg!small)

右键保存文件  
![image](https://image.3001.net/images/20220415/1649989232_6258d670e9d08833d0c5c.jpg!small)  
就完成了通过添加节，添加一个弹框案例。

# 后记

WindosPE文件结构还有几个节表本次没有涉及到，后面可以自行了解。对于逆向来说，PE文件结构是基础中的基础，不仅要对汇编熟悉，还要懂得调试程序，后面我会讲讲脱壳加壳的内容。大家一起努力吧！

