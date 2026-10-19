Wine是一个兼容层，能够在几个符合POSIX标准的操作系统上运行Windows应用程序，如Linux、macOS和BSD（https://www.winehq.org）

如果你使用Linux已经有一段时间了，你有可能在某些时候使用过Wine。也许是为了运行那个没有Linux版本的非常重要的Windows程序，也许是为了玩《魔兽世界》或其他一些游戏。有趣的是，Valve的Steam
Deck使用基于Wine的解决方案来运行游戏（称为Proton）

在过去的一年里，我花了相当多的时间来开发一个调试器，能够同时调试Wine层和与之一起运行的Windows应用程序。了解Wine的内部结构非常有趣--我以前曾多次使用Wine，但从不知道它的工作原理。如果你曾经想知道为什么可以把一个Windows的可执行文件，不经任何修改就在Linux上运行--欢迎阅读这篇文章

## 免责声明

这篇文章大大简化了现实，我并不声称知道所有的细节。然而，我希望这里的解释能让你大致了解Wine是如何运作的。

## 不是一个模拟器

在描述Wine如何工作之前，让我们先探讨一下它如何不工作。Wine是一个递归的缩写，它代表着 "Wine Is Not an
Emulator"。为什么不是呢？有很多很好的模拟器，既适用于老式架构，也适用于现代游戏机。Wine可以作为一个模拟器来实现吗？是的，但有很好的理由不这样做。让我们快速看一下模拟器一般是如何工作的。

想象一下，我们有一些简单的硬件，有两条指令：

  * push - 将给定的值推入堆栈

  * setpxl - 从堆栈中弹出三个值，并在(arg2, arg3)处画出一个带有arg1颜色的像素。

(这应该足以创造一些很酷的演示场景，对吗？)

    
    
    > dump-instructions game.rom
    ...
    # draw red dot at (10,10)
    push 10
    push 10
    push 0xFF0000
    setpxl
    # draw green dot at (15,15)
    push 15
    push 15
    push 0x00FF00
    setpxl
    

游戏二进制文件（或ROM盒）是这些指令的序列，硬件可以将其加载到内存中，然后执行。真正的硬件可以原生地执行它们，但如果我们想在现代的笔记本电脑上玩游戏呢？我们将创建一个软件模拟器
--一个将ROM加载到内存中然后执行其指令的程序。如果你愿意的话，一个解释器或一个虚拟机。我们的双指令控制台的模拟器的实现可以很简单。

    
    
    enum Opcode {
        Push(i32),
        SetPixel,
    };
    
    let program: Vec<Opcode> = read_program("game.rom");
    let mut window = create_new_window(160, 144); // Virtual screen of 160x144 pixels
    let mut stack = Vec::new(); // Stack for passing arguments
    
    for opcode in program {
        match opcode {
            Opcode::Push(value) => {
                stack.push(value);
            }
            Opcode::SetPixel => {
                let color = stack.pop();
                let x = stack.pop();
                let y = stack.pop();
                window.set_pixel(x, y, color);
            }
        }
    }
    

真正的模拟器要复杂得多，但基本思路是一样的：维护一些上下文（内存、寄存器等），处理输入（如键盘/鼠标）和输出（如绘制到某个窗口），解析输入数据（ROM）并逐一执行指令，应用其副作用。

这可能是实现Wine的一种方式，但有两个理由反对它。首先，模拟器很 "慢"--以编程方式执行每一条指令的开销很大。这对于旧的硬件来说可能是可以接受的，但对于最先进的技术来说就不是那么回事了（而视频游戏一直是要求最高的应用类型之一）。第二个原因是，没有必要！Linux/MacOS完全有能力处理这些问题。Linux/MacOS完全有能力原生运行Windows二进制文件，它们只需要一点推动力......

让我们为Linux和Windows编译一个简单的程序，并比较结果。

    
    
    int foo(int x) {
        return x * x;
    }
    
    int main(int argc) {
        int code = foo(argc);
        return code;
    }
    

![image.png](https://image.3001.net/images/20221016/1665903066_634ba9daa68d7fafeee44.png!small)(左
- Linux, 右 - Windows)

结果明显不同，但指令集实际上是相同的：push, pop, mov, add, sub, imul, ret。因此，如果我们有一个能够执行这些指令的
"模拟器"，理论上它应该能够执行这两条指令。而事实证明，我们确实有这个东西--那就是我们的CPU。

## Linux如何运行二进制文件

在Linux上运行Windows二进制文件之前，让我们先弄清楚如何运行一个正常的Linux二进制文件。

    
    
    ❯ cat app.cc
    #include <stdio.h>
    
    int main() {
      printf("Hello!\n");
      return 0;
    }
    
    ❯ clang app.cc -o app
    
    ❯ ./app
    Hello!  # works!
    
    

够简单了，让我们再深入一点。当我们做./app时会发生什么？

    
    
    ❯ ldd app
            linux-vdso.so.1 (0x00007ffddc586000)
            libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f743fcdc000)
            /lib64/ld-linux-x86-64.so.2 (0x00007f743fed3000)
    
    ❯ readelf -l app
    
    Elf file type is DYN (Position-Independent Executable file)
    Entry point 0x1050
    There are 13 program headers, starting at offset 64
    
    Program Headers:
      Type           Offset             VirtAddr           PhysAddr
                     FileSiz            MemSiz              Flags  Align
      PHDR           0x0000000000000040 0x0000000000000040 0x0000000000000040
                     0x00000000000002d8 0x00000000000002d8  R      0x8
      INTERP         0x0000000000000318 0x0000000000000318 0x0000000000000318
                     0x000000000000001c 0x000000000000001c  R      0x1
          [Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
    ...
    

首先，我们看到该应用程序是一个动态的可执行文件。这意味着它依赖于一些动态库，需要它们在运行时存在才能运行。这里另一个有趣的事情是 "请求程序解释器
"部分。解释器在这里做什么？我以为C++是一种编译的语言，与Python不同...

在这种情况下，解释器就是 "动态加载器"。它是一个特殊的程序，引导原始程序的执行：它解决并加载其依赖关系，然后将控制权交给它。

    
    
    ❯ ./app
    Hello!  # This works!
    
    ❯ /lib64/ld-linux-x86-64.so.2 ./app
    Hello!  # This works too!
    
    # Homework exercise, run this and try to make sense of the output.
    ❯ LD_DEBUG=all /lib64/ld-linux-x86-64.so.2 ./app
    

当运行可执行文件时，Linux内核会检测到它是动态的，需要一个加载器。然后它执行加载器，加载器完成所有的工作。例如，我们可以通过在调试器下运行该程序来验证这一点。

    
    
    ❯ lldb ./app
    (lldb) target create "./app"
    Current executable set to '/home/werat/src/cpp/app' (x86_64).
    (lldb) process launch --stop-at-entry
    Process 351228 stopped
    * thread #1, name = 'app', stop reason = signal SIGSTOP
        frame #0: 0x00007ffff7fcd050 ld-2.33.so`_start
    ld-2.33.so`_start:
        0x7ffff7fcd050 <+0>: movq   %rsp, %rdi
        0x7ffff7fcd053 <+3>: callq  0x7ffff7fcdd70            ; _dl_start at rtld.c:503:1
    
    ld-2.33.so`_dl_start_user:
        0x7ffff7fcd058 <+0>: movq   %rax, %r12
        0x7ffff7fcd05b <+3>: movl   0x2ec57(%rip), %eax       ; _dl_skip_args
    Process 351228 launched: '/home/werat/src/cpp/app' (x86_64)
    

这里我们可以看到，执行的第一条指令是ld-2.33.so，而不是应用程序的二进制文件。

总结一下，在Linux上运行一个动态链接的可执行文件的过程大致是这样的：

  1. 内核加载映像（≈二进制文件）并看到它是一个动态可执行文件

  2. 内核加载动态加载器（ld.so）并给它控制权

  3. 动态加载器解决依赖关系并加载它们

  4. 动态加载器将控制权交还给原始二进制文件

  5. 原始二进制文件在_start()中开始执行，最终进入main()。

在这一点上，我们很清楚为什么简单地运行一个Windows可执行文件是行不通的--它有不同的格式，内核根本不知道该怎么处理它。

    
    
    ❯ ./HalfLife4.exe
    -bash: HalfLife4.exe: cannot execute binary file: Exec format error
    

然而，如果我们能越过第1-4步，以某种方式到达第5步，理论上应该是可行的，对吗？既然我们在谈论 "执行"，从操作系统的角度来看，"运行
"二进制文件是什么意思？

每个可执行文件都有.text部分，其中包含序列化的CPU指令。

    
    
    ❯ objdump -drS app
    
    app:     file format elf64-x86-64
    
    ...
    
    Disassembly of section .text:
    
    0000000000001050 <_start>:
        1050:       31 ed                   xor    %ebp,%ebp
        1052:       49 89 d1                mov    %rdx,%r9
        1055:       5e                      pop    %rsi
        1056:       48 89 e2                mov    %rsp,%rdx
        1059:       48 83 e4 f0             and    $0xfffffffffffffff0,%rsp
        105d:       50                      push   %rax
        105e:       54                      push   %rsp
        105f:       4c 8d 05 6a 01 00 00    lea    0x16a(%rip),%r8        # 11d0 <__libc_csu_fini>
        1066:       48 8d 0d 03 01 00 00    lea    0x103(%rip),%rcx        # 1170 <__libc_csu_init>
        106d:       48 8d 3d cc 00 00 00    lea    0xcc(%rip),%rdi        # 1140 <main>
        1074:       ff 15 4e 2f 00 00       call   *0x2f4e(%rip)        # 3fc8 <__libc_start_main@GLIBC_2.2.5>
        107a:       f4                      hlt
        107b:       0f 1f 44 00 00          nopl   0x0(%rax,%rax,1)
    ...
    

为了 "运行
"可执行文件，操作系统将二进制文件加载到内存中（特别是.text部分），将当前指令指针设置为代码所在的地址，就这样，可执行文件开始运行。我们可以对Windows的可执行文件做同样的事情吗？

是的! 可执行文件内的代码在Windows和Linux之间是 "可移植
"的（假设CPU架构相同）。如果我们只是把代码从Windows的可执行文件中取出来，加载到内存中，并把%rip指向正确的地方--处理器会很高兴地执行它。  
![image.png](https://image.3001.net/images/20221016/1665903107_634baa039a9d4bd84c930.png!small)

## 你好，Wine！

本质上，wine是Windows可执行文件的
"动态加载器"。它是一个原生的Linux二进制文件，因此它可以正常运行，而且它知道如何处理EXE和DLLs。它有点类似于ld-linux-x86-64.so.2。

    
    
    # running an ELF binary
    ❯ /lib64/ld-linux-x86-64.so.2 ./app
    
    # running a PE binary
    ❯ wine64 HalfLife4.exe
    

wine将Windows可执行文件加载到内存中，解析它，找出依赖关系，找出可执行代码的位置（即.text部分），然后最终跳转到该代码。

好吧，在现实中，它跳入类似ntdll.dll!RtlUserThreadStart()的东西，这是Windows世界中的 "用户空间
"入口点。它最终会进入mainCRTStartup()（相当于_start），然后最终进入实际的main()。

在这一点上，我们的Linux系统正在执行最初为Windows编译的代码，一切似乎都在工作。除了...

## 系统调用

系统调用，或简称为syscalls，是使Wine如此复杂的原因。Syscall是对一个函数的调用，这个函数是在操作系统中实现的（因此是系统调用），而不是在应用程序的二进制文件或其任何动态库中。操作系统提供的一套syscall本质上是操作系统的API。

Linux上的例子：read, write, open, brk, getpid

Windows上的例子：NtReadFile, NtCreateProcess, NtCreateMutant 囧

系统调用不是代码中的常规函数调用。例如，打开一个文件，必须由内核自己执行，因为它是跟踪文件描述符的人。因此，应用程序代码需要一种方法来 "中断
"自己，将控制权交给内核（这种操作通常称为上下文切换）。

在每个操作系统上，操作系统所暴露的函数集和调用这些函数的方式都是不同的。例如，在Linux上，为了调用read()，二进制文件会把文件描述符放到寄存器%rdi中，把缓冲区指针放到%rsi中，把要读取的字节数放到%rdx中。然而，在Windows系统中，内核中没有read()函数。这些参数也没有任何意义。因此，为Windows编译的二进制文件将使用Windows的方式进行系统调用，这在Linux上是行不通的。我不会深入研究syscalls到底是如何工作的，这里有一篇关于Linux实现的好文章
--https://blog.packagecloud.io/the-definitive-guide-to-linux-system-calls/。

让我们再编译一个小程序，比较一下在Linux和Windows上生成的代码。

    
    
    #include <stdio.h>
    
    int main() {
        printf("Hello!\n");
        return 0;
    }
    

![image.png](https://image.3001.net/images/20221016/1665903130_634baa1a1f1b2ae69bbe0.png!small)(左
- Linux, 右 - Windows)

这一次我们从标准库中调用一个函数，而这个函数最终会执行一个系统调用。在上面的截图中，Linux版本调用puts，而Windows版本则调用printf。这些函数来自标准库（Linux的libc.so，Windows的ucrtbase.dll），应用程序使用它来简化与内核的通信。在Linux上，现在建立静态链接的二进制文件是相当普遍的，它不依赖于任何动态库。在这种情况下，put的实现被嵌入到二进制文件中，在运行时没有libc.so的参与。

在Windows上，至少在不久前，"只有恶意软件才会使用直接的系统调用"[引用者注]。正常的应用程序总是依赖于kernel32.dll/kernelbase.dll/ntdll.dll，它们隐藏了与内核通信的低级魔法。应用程序只是调用一个函数，其余的由库来处理。

![image.png](https://image.3001.net/images/20221016/1665903149_634baa2d83a3f5157dda5.png!small)

(感谢 https://alice.climent-pommeret.red/posts/a-syscall-journey-in-the-windows-kernel/)

在这一点上，你可能已经对我们接下来要做的事情有了感觉 2333。

## 系统调用的运行时翻译

如果我们能 "拦截
"一个系统调用呢？比如，每当应用程序调用NtWriteFile()时，我们就会介入，调用write()，并以二进制文件所期望的格式返回结果。这应该是可行的。上面的例子的简单粗暴的解决方案可能看起来像这样。

    
    
    // HelloWorld.exe
    lea     rcx, OFFSET FLAT:`string'
    call    printf
      ↓↓
    // "Fake" ucrtbase.dll
    mov edi, rcx   // Convert the arguments to Linux ABI
    call puts@PLT  // Call the real Linux implementation
      ↓↓
    // Real libc.so
    mov rdi, <stdout>  // write to STDOUT
    mov rsi, edi       // pointer to "Hello"
    mov rdx, 5         // how many chars to write
    syscall
    

我们可以提供一个自定义版本的ucrtbase.dll，它将有一个特殊的printf实现。它不会试图调用Windows内核，而是遵循Linux
ABI，调用libc.so的写函数。然而，在实践中，应用程序可以静态地与ucrtbase.dll链接，而且我们不能修改二进制文件的代码，原因有很多--这很混乱和复杂，会弄乱DRM，等等。

因此，我们将修改介于二进制文件和内核之间的地方 - ntdll.dll。这是进入内核的
"网关"，Wine确实提供了它的自定义实现。在Wine的最新版本中，它由两部分组成：ntdll.dll（这是一个PE库）和ntdll.so（这是一个ELF库）。第一个部分是一个薄层，只是将调用重定向到ELF对应部分。ELF对应库包含一个名为__wine_syscall_dispatcher的特殊函数，它执行了一个将当前堆栈从Windows转换到Linux并返回的魔术。

因此，当进行系统调用时，与Wine一起运行的进程的调用栈看起来像这样。

![image.png](https://image.3001.net/images/20221016/1665903167_634baa3fa1fbf98144622.png!small)

系统调用调度器是连接Windows世界和Linux世界的桥梁。它负责处理调用惯例--分配一些堆栈空间，移动寄存器，等等。一旦在Linux库（ntdll.so）中执行，我们就可以自由地使用任何常规的Linux
API（例如libc或syscall），并可以实际读/写文件，锁定/解锁互斥等等。

## 是这样吗？

这听起来几乎太容易了。而且确实如此。首先，有大量的Windows
APIs。而且它们的文档很差，有已知的（和未知的，哈哈）错误，必须完全按原样保留。Wine的大部分源代码是各种Windows DLLs的实现。

第二，有不同的方法来执行系统调用。从技术上讲，没有什么可以阻止应用程序通过syscall指令进行直接的系统调用，理想情况下这也应该是可行的（记住，Windows游戏会做各种疯狂的事情）。Linux内核有一个特殊的机制来处理这个问题，当然这只会增加复杂性。

第三，还有这整个32位与64位的兼容问题。有很多老的32位游戏，它们永远不会被重新发布为64位。Wine对两者都有支持，这再次增加了系统的整体复杂性。

第四，我甚至没有提到Wine-server--一个由Wine催生的独立进程，它维护着内核的 "状态"（打开的文件描述符、互斥符等）。

第五，哦，你想运行一个游戏吗？而不仅仅是一个hello
world？那么你需要处理DirectX、音频、输入设备（游戏手柄、操纵杆）等等。这是一个很大的工作!

Wine已经开发了很多年，并取得了长足的进步。今天，你可以运行最新的游戏，如《赛博朋克2077》或《Elden
Ring》，没有任何问题。该死的，有时候Wine的性能甚至比Windows还要好! 这是一个怎样的时代啊...

* * *

我希望这篇文章能让您对Wine的工作原理有一个基本的了解。正如我在免责声明中警告的那样，我简化了一大堆事情，在一些细节上可能是错误的(希望不会太多)。如果你发现我完全是在误导别人，请伸出援手纠正我！

作者：Andy Hippo, 原文地址：<https://werat.dev/blog/how-wine-works-101/>

