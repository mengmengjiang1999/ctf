# 【技术分享】如何开发自定义的Boot Loader

阅读量 **131507**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-08-10 14:04:26

 **x**

##### 译文声明

本文是翻译文章，文章来源：codeproject.com

原文地址：<https://www.codeproject.com/Articles/36907/How-to-develop-your-own-Boot-Loader>

译文仅供参考，具体内容表达以及含义原文为准。

  

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

  

在本文中，我们以一个简单的boot loader开发过程为例，简单介绍了如何使用低级语言完成自定义boot loader的开发。

读者可访问[此处](https://www.codeproject.com/KB/tips/boot-loader/bootloader.zip)下载我们创建的自制boot loader。

  

**一、目标读者**

****

首先需要明确的是，这篇文章是为始终对不同事物的工作原理保持兴趣的那些人而准备的。具体说来，如果你是一名开发者，经常使用类似C、C++或Java之类的高级语言来开发应用程序，但有时依然需要使用低级语言来开发，那么你正是本文的目标受众。在本文中，我们会以具体案例，介绍低级编程语言在系统加载过程中的应用。

本文会分析计算机启动后的工作流程以及系统加载的具体过程，介绍如何开发自制的boot loader，而boot loader正是系统启动过程的第一个落脚点。

  

**二、什么是Boot Loader**

****

**Boot Loader**
是位于硬盘第一个扇区的程序，该扇区也是系统开始启动的扇区。在主机加电后，BIOS会自动将第一个扇区的所有内容读入内存，然后跳转到相应位置。第一个扇区也称之为
**主引导记录** （Master Boot
Record）。实际上硬盘的第一个扇区没必要非得用来引导，只是历史上开发者使用这种机制来引导他们的操作系统，久而久之这个习惯就保留了下来。

  

**三、深入分析**

****

在这一部分，我会向大家介绍开发自制的boot loader所需要的背景知识以及相关工具，顺便也会介绍有关系统启动的一些背景知识。

**3.1 自制Boot Loader所需掌握的语言**

在计算机工作的第一个阶段，对硬件的控制主要是通过 **中断**
（interrupt）这个BIOS功能来实现的。中断功能的实现代码仅有汇编语言版本，因此如果你有一点汇编语言的功底是再好不过的一件事。不过这也不是一个非满足不可的条件，因为我们可以使用“混合代码（mixed
code）”这种技术，这种情况下，我们可以将高级语言结构与低级语言命令结合在一起，减轻任务的复杂度。

本文所使用的开发语言主要是C++。如果你对C已经了如指掌，那么学习所需的C++知识肯定易如反掌。通常情况下，单单掌握C语言就已经足够，但此时你还需要修改我给出的示例代码。

如果你非常熟悉Java或C#，很不幸地告诉你，这一技能对我们的任务毫无帮助。症结在于Java和C#代码经过编译后生成的是中间代码，需要使用专门的虚拟机（对Java来说是Java
Machine，对C#来说是.NET）来处理这些代码，以便将中间代码转化为处理器指令。只有经过转化代码才能执行。这种实现机制导致这些语言无法使用混合代码技术，而
**混合代码技术是我们用来减轻任务工作量不得不使用的技术** ，因此Java及C#不适应这种使用场景。

因此，为了开发自制的boot
loader，你需要了解C或C++语言，如果能知道关于汇编语言的一些知识那再好不过，因为所有的高级语言代码最后都会转化为汇编语言。

**3.2 所需的编译器**

为了使用混合代码技术，你至少需要两种编译器： **汇编语言以及C/C++编译器**
，你也需要链接器（linker）将对象文件（.obj）连接到可执行文件中。

现在我们来讨论一些特别的细节。处理器在功能上有两种模式：实模式（real mode）以及保护模式（protected
mode）。保护模式为32位，完全用于操作系统的运行流程。当主机启动时，处理器处于16位工作模式下。因此，为了构建应用程序并生成可执行文件，你需要16位模式下汇编语言的编译器以及链接器。对于C/C++而言，你只需要能够创建16位模式下对象文件的编译器。

现在流行的编译器仅适用于32位应用程序，因此我们无法使用这些编译器。

我尝试了一些免费以及商业版本的16位模式编译器，最终选择使用微软出品的编译器。微软在Visual Studio
1.52软件包中集成了汇编语言、C以及C++的编译器及链接器，我们也可以从微软官网上下载这些工具。我们所需的编译器具体版本信息如下所示：

* **ML 6.15** ：微软出品的16位模式汇编语言编译器。

* **LINK 5.16** ：用来创建16位模式的.com文件的链接器。

* **CL** ：16位模式下C以及C++的编译器。

你也可以使用一些替代工具：

* **DMC** ：Digital Mars出品的一款免费编译器，可作为16位以及32位模式下的汇编语言、C以及C++编译器。

* **LINK** ：DMC编译器的免费版链接器。

此外，Borland也出品了一些工具：

* **BCC 3.5** ：可以创建16位模式下文件的C以及C++编译器。

* **TASM** ：用于16位模式的汇编语言编译器。

* **TLINK** ：可以创建16位模式下.com文件的链接器。

本文涉及的所有代码均使用了微软的工具进行编译构建。

**3.3 系统启动过程**

为了完成我们既定的任务，我们需要回想一下系统的启动过程。

让我们简单思考一下，系统在启动时，各系统组件之间的交互过程，如图1所示。

图1.系统启动过程

当控制权移交给0000:7C00地址时， **主引导记录（MBR）**
开始工作，触发操作系统引导过程。你可参考[此处链接](http://en.wikipedia.org/wiki/Master_boot_record)了解MBR结构的详细信息。

  

**四、编写代码**

****

在下一节中，我们将直接面对低级语言，也就是说，我们即将开发自己的boot loader。

**4.1 程序架构**

我们开发的boot loader仅用于教学目的，其任务只包含以下几点：

1\. 正确载入内存中0000:7C00地址处。

2\. 调用BootMain函数，该函数使用高级语言实现。

3\. 以底层信息形式在显示器上显示“Hello, world…”信息。

程序架构如图2所示。

程序架构中，第一个实体是StartPoint，该实体完全由汇编语言开发而成，因为高级语言不具备我们所需的那些指令。StartPoint会告诉编译器应该使用什么内存模型，以及从磁盘读取数据后，需要将数据加载到RAM中的哪个地址。StartPoint也会校正处理器的寄存器，将控制权交给BootMain，后者使用高级语言编写而成。

作为下一个实体，BootMain的功能与main类似，也就是说，该实体是集中了所有程序功能的主函数模块。

CDisplay以及CString类负责程序的功能部分，会在屏幕上显示相应信息。如图2所示，CDisplay类在在工作过程中使用了CString类。

**4.2 开发环境**

在本文中，我使用的是标准的开发环境：Microsoft Visual Studio
2005或者2008开发环境。当然读者也可以使用其他工具，但经过某些设置后，使用这两个工具可以让程序的编译及运行更加简单也更加方便。

首先，我们需要创建一个Makefile Project类型的工程，该工程负责主要工作（如图3所示）。

依次选择如下菜单：

File->NewProject->GeneralMakefile Project

图3. 创建Makefile类型工程

**4.3 BIOS中断及屏幕清理**

为了能在屏幕上显示我们的信息，我们首先应该清除屏幕上已有的信息。我们需要使用特定的BIOS中断来完成这一任务。

为了与视频适配器、键盘、硬盘系统之类的计算机硬件交互，BIOS提供了许多类型的中断。每种中断都具备如下类型的结构：

    
    
    int [number_of_interrupt];

其中，number_of_interrupt代表的是中断的序号。

每种中断都包含特定数量的参数，在调用中断前必须设置这些参数。ah处理器寄存器始终用来负责当前中断的函数序号，其他寄存器通常用于处理当前操作所用的其他参数。让我们分析下汇编语言中int
10h中断的执行过程。我们使用00函数来改变视频模式，也用来清除屏幕：

    
    
    mov al, 02h ; setting  the graphical mode 80x25(text)
    mov ah, 00h ; code  of function of changing video mode
    int 10h   ; call  interruption

在我们的应用程序中，我们只会使用这些中断以及函数。我们需要使用如下代码：

    
    
    int 10h, function 00h – performs changing of video mode and clears  screen;
    int 10h, function 01h – sets the cursor type;
    int 10h, function 13h – shows the string on the screen;

**4.4 代码混合**

C++编译器支持内嵌汇编语言，也就是说，当我们使用高级语言编写代码时，我们同时也可以使用低级语言。在高级语言代码中使用的汇编指令也可以称为
**asm插入** 。为了实现asm插入，我们需要包含__asm关键词，并将汇编代码用大括号包裹起来：

    
    
    __asm ;  key word that shows the beginning of the asm insertion
      { ;  block beginning
      … ; some asm code
      } ;  end of the block

为了演示混合代码，我们可以将前面用来清除屏幕的汇编代码与C++代码结合在一起。

    
    
    void ClearScreen()
    {
     __asm
    {
     mov al, 02h ; setting the graphical mode 80x25(text)
    mov ah, 00h ; code  of function of changing video mode
    int 10h   ; call interrupt
    }
    }

**4.5 CString实现**

CString是用来处理字符串的一个类。类中包含了一个Strlen()方法，传入字符串指针，可以返回字符串中字符的数量。

    
    
    // CString.h 
    #ifndef __CSTRING__
    #define __CSTRING__
    #include "Types.h"
    class CString 
    {
    public:
        static byte Strlen(
            const char far* inStrSource 
            );
    };
    #endif // __CSTRING__
    // CString.cpp
    #include "CString.h"
    byte CString::Strlen(
            const char far* inStrSource 
            )
    {
            byte lenghtOfString = 0;
            while(*inStrSource++ != '')
            {
                ++lenghtOfString;
            }
            return lenghtOfString;
    }

**4.6 CDisplay实现**

CDisplay是用来处理屏幕相关功能的一个类，包含如下几个方法：

1\. TextOut()：用来在屏幕上打印字符串。

2\. ShowCursor()：用来管理屏幕上鼠标的显示状态，即显示（show）或隐藏（hide）状态。

3\. ClearScreen()：修改视频模式，从而清除屏幕。

    
    
    // CDisplay.h
    #ifndef __CDISPLAY__
    #define __CDISPLAY__
    //
    // colors for TextOut func
    //
    #define BLACK0x0
    #define BLUE0x1
    #define GREEN0x2
    #define CYAN0x3
    #define RED0x4
    #define MAGENTA0x5
    #define BROWN0x6
    #define GREY0x7
    #define DARK_GREY0x8
    #define LIGHT_BLUE0x9
    #define LIGHT_GREEN0xA
    #define LIGHT_CYAN0xB
    #define LIGHT_RED      0xC
    #define LIGHT_MAGENTA   0xD
    #define LIGHT_BROWN0xE
    #define WHITE0xF
    #include "Types.h"
    #include "CString.h"
    class CDisplay
    {
    public:
        static void ClearScreen();
        static void TextOut(
            const char far* inStrSource,
            byte            inX = 0,
            byte            inY = 0,
            byte            inBackgroundColor   = BLACK,
            byte            inTextColor         = WHITE,
            bool            inUpdateCursor      = false
            );
        static void ShowCursor(
            bool inMode
            );
    };
    #endif // __CDISPLAY__
    // CDisplay.cpp
    #include "CDisplay.h"
    void CDisplay::TextOut( 
            const char far* inStrSource, 
            byte            inX, 
            byte            inY,  
            byte            inBackgroundColor, 
            byte            inTextColor,
            bool            inUpdateCursor
            )
    {
        byte textAttribute = ((inTextColor) | (inBackgroundColor &lt;&lt; 4));
        byte lengthOfString = CString::Strlen(inStrSource);
        __asm
         {
            pushbp
            moval, inUpdateCursor
            xorbh, bh
            movbl, textAttribute
            xorcx, cx
            movcl, lengthOfString
            movdh, inY
            movdl, inX  
            mov     es, word ptr[inStrSource + 2]
            mov     bp, word ptr[inStrSource]
            movah,13h
            int10h
            popbp
        }
    }
    void CDisplay::ClearScreen()
    {
        __asm
        {
            mov     al, 02h
            mov     ah, 00h
            int     10h
        } 
    }
    void CDisplay::ShowCursor(
            bool inMode
            )
    {
        byte flag = inMode ? 0 : 0x32;
        __asm
        {
            mov     ch, flag
            mov     cl, 0Ah
            mov     ah, 01h
            int     10h
        }
    }

**4.7 Types.h实现**

Types.h是一个头文件，包含数据类型以及宏的定义。

    
    
    // Types.h
    #ifndef __TYPES__
    #define __TYPES__     
    typedef unsigned char   byte;
    typedef unsigned short  word;
    typedef unsigned long   dword;
    typedef char            bool;
    #define true            0x1
    #define false           0x0
    #endif // __TYPES__

**4.8 BootMain.cpp实现**

BootMain()是程序的主功能函数，也是第一个入口点（类似于main()）。程序的主要功能实现位于该函数中。

    
    
    // BootMain.cpp
    #include "CDisplay.h"
    #define HELLO_STR               ""Hello, world…", from low-level..."
    extern "C" void BootMain()
    {
        CDisplay::ClearScreen();
        CDisplay::ShowCursor(false);
        CDisplay::TextOut(
            HELLO_STR,
            0,
            0,
            BLACK,
            WHITE,
            false
            );
        return;
    }

**4.9 StartPoint.asm实现**

    
    
    ;------------------------------------------------------------    .286   ; CPU type
    ;------------------------------------------------------------    .model TINY   ; memory of model
    ;---------------------- EXTERNS -----------------------------    extrn_BootMain:near   ; prototype of C func
    ;------------------------------------------------------------    ;------------------------------------------------------------   
    .code   
    org07c00h   ; for BootSector
    main:
    jmp short start   ; go to main
    nop
    ;----------------------- CODE SEGMENT -----------------------    start:
            cli
            mov ax,cs               ; Setup segment registers
            mov ds,ax               ; Make DS correct
            mov es,ax               ; Make ES correct
            mov ss,ax               ; Make SS correct        
            mov bp,7c00h
            mov sp,7c00h            ; Setup a stack
            sti
                                    ; start the program 
            call           _BootMain
            ret
            END main                ; End of program

**  
**

**五、编写汇编代码**

****

**5.1 创建COM文件**

现在，在编写代码时，我们需要将代码转化为16位操作系统中可用的文件。这些文件是 **.com文件**
。我们可以通过命令行运行每个编译器（即汇编语言编译器、C及C++编译器），输入必要的参数，然后生成几个目标文件。下一步我们需要启动链接器，将所有.obj文件转化为可执行的.com文件。这是可行的工作方式，但做起来不是特别容易。

我们可以自动化完成这个过程。为了实现自动化，我们创建了.bat文件，将命令及必要的参数输入脚本文件中。应用程序汇编处理的完整过程如图4所示。

图4. 程序编译过程

**Build.bat**

现在，我们需要将编译器以及链接器放在当前工程目录中。在同一个目录下，我们创建了.bat文件，根据演示需求往文件中添加适当命令（你可以将其中的VC152替换为编译器及链接器所在的那个目录名）：

    
    
    .VC152CL.EXE /AT /G2 /Gs /Gx /c /Zl *.cpp
    .VC152ML.EXE /AT /c *.asm
    .VC152LINK.EXE /T /NOD StartPoint.obj bootmain.obj cdisplay.obj cstring.obj
    del *.obj

**5.2 自动化汇编**

作为本节的最后一部分，我们将介绍如何设置微软的Visual Studio
2005/2007，让其支持任意编译器，使其成为合适的开发环境。让我们跳转到工程属性，依次选择如下菜单：Project->Properties->Configuration
PropertiesGeneral->Configuration Type

**Configuration Properties** 选项卡包含三个选项： **General、Debugging** 以及 **NMake** 。转到
**NMake** 选项，将 **Build Command Line** 以及 **Rebuild Command Line** 字段设置为
**build.bat** ，如图5所示。

图5. NMake工程设置

如果一切进展顺利，那么你就可以使用熟悉的 **F7** 或者 **Ctrl + F7**
方式来编译工程，所有的输出信息都会在Output窗口中显示。这样做的主要优点不仅在于能够自动化完成汇编工作，当代码出现错误时，这样做也能快速定位错误代码。

  

**六. 测试及用例展示**

****

本节主要介绍的是如何查看boot loader的引导效果，测试并调试boot loader。

**6.1 如何测试boot loader**

你可以在真实的硬件上测试boot loader，也可以使用专用的VMware虚拟机来完成这一任务。使用真实的硬件进行测试时，你可以确保boot
loader能够正常工作，而使用虚拟机进行测试时，你只能得出boot
loader可以工作的结论。当然，我们可以说VMware是测试及调试的绝佳选择。在本文中，这两种方法都会涉及到。

首先，我们需要一个工具，以便将我们的boot
loader写入虚拟磁盘或物理磁盘上。据我所知，有一些免费或者商业的基于控制台或者GUI的应用程序能够完成这一任务。对于Windows系统，我选择的是
**Disk Explorer for NTFS 3.66** 这个工具（适用于FAT的版本为Disk Explorer for FAT），对于MS-DOS系统，我选择的是 **Norton Disk Editor 2002** 。

在这里我只会介绍Disk Explorer for NTFS 3.66这个工具，因为使用该工具是满足我们的需求的最为简单的一种方法。

**6.2 使用VMware虚拟机进行测试**

**6.2.1 创建虚拟机**

我们需要5.0、6.0或者更高版本的VMware程序。为了测试boot
loader，我们需要创建一个新的虚拟机，磁盘大小设为最小（如1Gb）。将硬盘格式化为NTFS文件系统。现在我们需要将格式化后的硬盘映射到VMware中的虚拟磁盘。依次选择如下菜单：

**File- >Map or Disconnect Virtual Disks…**

之后就会弹出一个窗口，这里我们需要点击“Map”按钮。在弹出窗口中，我们需要将路径设置为硬盘所在的路径。然后我们需要指定硬盘的盘符。如图6所示。

图6. 设置虚拟磁盘映射参数

不要忘记勾掉 **“Open file in read-only mode (recommended)”**
复选框。选中该复选框则意味着硬盘会以只读模式打开，阻止写入操作以避免数据损坏。

之后我们可以像使用Windows逻辑磁盘那样来使用虚拟机的磁盘。现在我们需要使用Disk Explorer for NTFS 3.66,将boot
loader写入到物理偏移为0的地址处。

**6.2.2 使用Disk Explorer for NTFS**

程序启动后，我们需要转到我们的那个磁盘（ **File- >Drive**）。在弹出窗口中，转到“Logical
Drives”部分，选择包含特定盘符的那个硬盘（本例中为Z盘），如图7所示。

图7. 在Disk Explorer for NTFS中选择磁盘

现在，在菜单栏中选择 **View** 以及 **As Hex**
命令，在生成的窗口中，我们可以看到以16进制呈现的硬盘数据，硬盘数据按扇区和偏移量进行分隔。从窗口中我们发现一堆的0，因为此时此刻硬盘是个空硬盘。第一个扇区情况如图8所示。

图8. 硬盘第1个扇区的数据

现在我们应该将我们的boot loader写入第一个扇区中。将光标设定在00处，如图8所示。为了复制boot loader，我们使用 **Edit**
菜单项，选择 **Paste from file** 命令。在打开的窗口中，指定文件的路径，然后点击 **Open**
按钮。之后，第一个扇区的内容应该会发生改变，如图9所示（如果你没有修改代码，那么扇区数据肯定会发生改变）。

你还需要在距离扇区起始位置的1FE偏移处写入55AAh特征数据。如果不这么做，BIOS会检查最后两个字节，找不到这个特征后，会将该扇区视为不可引导扇区，不会将其读入内存。

要想切换回编辑模式，你可以按下 **F2** 键，再写入55AAh这个特征数据，然后按下 **Esc** 键离开编辑模式。

接下来我们需要确认数据写入情况。

图9.引导扇区数据

要完成数据写入，我们需要转到 **Tools- >Options**，在弹出窗口中，选择 **Mode** 子项，选择写入方式（为 **Virtual
Write** ），点击 **Write** 按钮，如图10所示。

之后程序会经过一系列的操作，完成写入过程，现在我们可以看到从本文开头就一直在开发的研究成果。回到VMware中，断开虚拟磁盘（选择 **File->Map**或者 **Disconnect Virtual Disks…** ，然后点击 **Disconnect** ）。

现在我们可以试着启动虚拟机。我们可以看到屏幕中出现了我们熟悉的那个字符串： **“Hello, world…”, from low-level…**
。如图11所示。

**6.3 在真实硬件上进行测试**

在真实硬件上的测试过程与在虚拟机上的测试过程非常类似，只不过此时如果某些功能无法正常工作，相对比简单地创建新的虚拟机，你可能需要花费更多的时间才能修复出现的问题。在测试boot
loader时，为了避免造成数据损坏（一切都有可能发生），我建议你使用闪存驱动器（flash
drive），但首先你需要重启计算机，进入BIOS，检查BIOS是否支持从闪存驱动器启动。如果支持，那么一切都会非常顺利，如果不支持，那么测试过程还是仅限于虚拟机环境比较好。

使用Disk Explorer for NTFS 3.66将boot
loader写入闪存驱动器中与虚拟机的写入过程相同。你只需要选择硬盘驱动器本身，而不是选择硬盘驱动器的逻辑分区来完成写入过程即可。如图12所示。

图12.选择物理期盼作为目标设备

**6.4 调试**

如果整个过程中出现问题（通常都会发生这种情况），你需要某些工具来调试boot
loader。我想说的是，这是非常复杂、非常烦人同时又非常耗时的一个过程。你需要在汇编机器码中遨游，因此你需要熟练掌握这门语言。我列了一些工具，仅供参考：

1\. **TD (Turbo Debugger)** ：Borland出品的用于16位实模式的非常好的一个调试器。

2\. **CodeView** ：微软出品的用于16位模式的非常好的一个调试器。

3\. **Bocsh** ：虚拟机程序模拟器，包含机器命令调试器。

  

**七、参考资料**

****

**Kip R. Irvine** 写的 **"Assembly Language for Intel-Based Computers"**
这本书非常好，详细介绍了计算机的内部结构以及汇编语言的开发细节，从中你也能找到如何安装、配置及使用MASM 6.15编译器的相关信息。

你也可以访问<http://en.wikipedia.org/wiki/BIOS_interrupt_call>了解BIOS中断列表。

  

**八、总结**

****

在本文中，我们介绍了boot
loader的基本知识、BIOS的工作原理、系统启动时系统各组件之间的交互过程等信息。在实践部分，我们介绍了如何开发一个简单的自定义的boot
loader。我们介绍了混合代码技术，也介绍了如何使用微软的Visual Studio 2005、2008来自动化完成程序的汇编过程。

当然，与低级编程语言方面翔实的参考资料相对比，本文只能算九牛一毛，但如果能引起广大读者的兴趣就已足够。

读者可以参考[Apriorit](http://www.apriorit.com/case-studies.html)网站了解更多研究成果。

本文翻译自codeproject.com [原文链接](https://www.codeproject.com/Articles/36907/How-to-develop-your-own-Boot-Loader)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86595](/post/id/86595)

安全客 - 有思想的安全新媒体

本文转载自: [codeproject.com](https://www.codeproject.com/Articles/36907/How-to-develop-your-own-Boot-Loader)

如若转载,请注明出处： <https://www.codeproject.com/Articles/36907/How-to-develop-your-own-Boot-Loader>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

