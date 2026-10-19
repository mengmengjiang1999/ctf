# 【技术分享】利用GDB调试ARM代码

阅读量 **218918**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-08-02 13:13:28

 **x**

##### 译文声明

本文是翻译文章，文章来源：azeria-labs.com

原文地址：<https://azeria-labs.com/debugging-with-gdb-introduction/>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

  

在本文中，我们将简要介绍如何利用GDB完成ARM二进制文件的编译和基本调试。当然，阅读过程中，如果读者想要对ARM汇编代码动手进行实验的话，则需要准备一个备用的ARM设备，或者在虚拟机中设置相应的实验室环境，具体操作请参考[How-To](https://azeria-labs.com/emulate-raspberry-pi-with-qemu/)这篇文章。

此外，您还将通过下面取自 [Part 7 – Stack and Functions](https://azeria-labs.com/functions-and-the-stack-part-7/)这篇文章中的代码来熟悉GDB的基本调试功能。

    
    
    .section .text
    .global _start
    
    _start:
        push {r11, lr}    /* Start of the prologue. Saving Frame Pointer and LR onto the stack */
        add r11, sp, #0   /* Setting up the bottom of the stack frame */
        sub sp, sp, #16   /* End of the prologue. Allocating some buffer on the stack */
        mov r0, #1        /* setting up local variables (a=1). This also serves as setting up the first parameter for the max function */
        mov r1, #2        /* setting up local variables (b=2). This also serves as setting up the second parameter for the max function */
        bl max            /* Calling/branching to function max */
        sub sp, r11, #0   /* Start of the epilogue. Readjusting the Stack Pointer */
        pop {r11, pc}     /* End of the epilogue. Restoring Frame pointer from the stack, jumping to previously saved LR via direct load into PC */
    
    max:
        push {r11}        /* Start of the prologue. Saving Frame Pointer onto the stack */
        add r11, sp, #0   /* Setting up the bottom of the stack frame */
        sub sp, sp, #12   /* End of the prologue. Allocating some buffer on the stack */
        cmp r0, r1        /* Implementation of if(a<b) */
        movlt r0, r1      /* if r0 was lower than r1, store r1 into r0 */
        add sp, r11, #0   /* Start of the epilogue. Readjusting the Stack Pointer */
        pop {r11}         /* restoring frame pointer */
        bx lr             /* End of the epilogue. Jumping back to main via LR register */

就个人而言，我更喜欢使用作为GDB增强版的[GEF](https://github.com/hugsy/gef)，它用起来要更加得心应手，具体下载地址[https://github.com/hugsy/gef](https://github.com/hugsy/gef%E3%80%82)

将上述代码保存到名为max.s的文件中，然后使用以下命令进行编译：

    
    
    $ as max.s -o max.o
    $ ld max.o -o max

这个调试器是一个强大的工具，可以：

**在代码崩溃后加载内存dump（事后剖析调试）**

**附加到正在运行的进程（用于服务器进程）** ****

**启动程序并进行调试** **** ****

根据二进制文件、核心文件或进程ID启动GDB：

附加到一个进程：$ gdb -pid $（pidof <process>）

调试二进制代码：$ gdb ./file

检查内核（崩溃）文件：$ gdb -c ./core.3243

    
    
    $ gdb max

如果您安装了GEF，将会显示gef>提示符。

可以通过下列方式获取帮助：

(gdb) h

(gdb) apropos <search-term>

    
    
    gef> apropos registers
    collect -- Specify one or more data items to be collected at a tracepoint
    core-file -- Use FILE as core dump for examining memory and registers
    info all-registers -- List of all registers and their contents
    info r -- List of integer registers and their contents
    info registers -- List of integer registers and their contents
    maintenance print cooked-registers -- Print the internal register configuration including cooked values
    maintenance print raw-registers -- Print the internal register configuration including raw values
    maintenance print registers -- Print the internal register configuration
    maintenance print remote-registers -- Print the internal register configuration including each register's
    p -- Print value of expression EXP
    print -- Print value of expression EXP
    registers -- Display full details on one
    set may-write-registers -- Set permission to write into registers
    set observer -- Set whether gdb controls the inferior in observer mode
    show may-write-registers -- Show permission to write into registers
    show observer -- Show whether gdb controls the inferior in observer mode
    tui reg float -- Display only floating point registers
    tui reg general -- Display only general registers
    tui reg system -- Display only system registers

断点命令：

break (or just b) <function-name>

break <line-number>

break filename:function

break filename:line-number

break *<address>

break +<offset>

break –<offset>

tbreak (设置一个临时断点）

del <number> （删除编号为x的断点）

delete (删除所有断点）

delete <range>（删除指定编号范围内的断点）

disable/enable <breakpoint-number-or-range> (不删除断点，只是启用/禁用它们）

continue (or just c) – （继续执行，直到下一个断点）

continue <number> (继续，但忽略当前断点指定次数。对循环内的断点非常有用）

finish继续，直至函数末尾）

    
    
    gef> break _start
    gef> info break
    Num Type Disp Enb Address What
    1 breakpoint keep y 0x00008054 <_start>
     breakpoint already hit 1 time
    gef> del 1
    gef> break *0x0000805c
    Breakpoint 2 at 0x805c
    gef> break _start

这将删除第一个断点，并在指定的内存地址处设置一个断点。当您运行程序时，它将在这个指定的位置停下来。
如果不删除第一个断点，然后又设置一个断点并运行，则它还是在第一个断点处停下来。

启动和停止：

启动一个程序，从头开始执行

run

r

run <command-line-argument>

停止程序的运行

kill

退出GDB调试器

quit

q

    
    
    gef> run

现在，我们的程序在指定的位置停下来了，这样就可以开始检查内存了。 命令“x”可以用来以各种格式显示内存内容。

语法 : x/<count><format><unit>

格式单位

x – 十六进制 b – 字节

d – 十进制h – 半字（2字节）

i – 指令w – 字（4字节）

t – 二进制（two）g – 巨字（8字节）

o – 八进制

u – 无符号整数

s – 字符串

c – 字符

    
    
    gef> x/10i $pc
    => 0x8054 <_start>: push {r11, lr}
     0x8058 <_start+4>: add r11, sp, #0
     0x805c <_start+8>: sub sp, sp, #16
     0x8060 <_start+12>: mov r0, #1
     0x8064 <_start+16>: mov r1, #2
     0x8068 <_start+20>: bl 0x8074 <max>
     0x806c <_start+24>: sub sp, r11, #0
     0x8070 <_start+28>: pop {r11, pc}
     0x8074 <max>: push {r11}
     0x8078 <max+4>: add r11, sp, #0
    gef> x/16xw $pc
    0x8068 <_start+20>: 0xeb000001  0xe24bd000  0xe8bd8800  0xe92d0800
    0x8078 <max+4>:     0xe28db000  0xe24dd00c  0xe1500001  0xb1a00001
    0x8088 <max+20>:    0xe28bd000  0xe8bd0800  0xe12fff1e  0x00001741
    0x8098:             0x61656100  0x01006962  0x0000000d  0x01080206

用于单步调试的命令：单步执行下一条命令。可以进入函数内部

stepi

s

step <number-of-steps-to-perform>

执行下一行代码。不会进入函数内部

nexti

n

next <number>

继续处理，直到达到指定的行号、函数名称、地址、文件名函数或文件名：行号

until

until <line-number>、

显示当前行号以及所在的函数

where

    
    
    gef> nexti 5
    ...
    0x8068 <_start+20> bl 0x8074 <max> <- $pc
    0x806c <_start+24> sub sp, r11, #0
    0x8070 <_start+28> pop {r11, pc}
    0x8074 <max> push {r11}
    0x8078 <max+4> add r11, sp, #0
    0x807c <max+8> sub sp, sp, #12
    0x8080 <max+12> cmp r0, r1
    0x8084 <max+16> movlt r0, r1
    0x8088 <max+20> add sp, r11, #0

使用info registers或i r命令检查寄存器的值

    
    
    gef> info registers
    r0     0x1     1
    r1     0x2     2
    r2     0x0     0
    r3     0x0     0
    r4     0x0     0
    r5     0x0     0
    r6     0x0     0
    r7     0x0     0
    r8     0x0     0
    r9     0x0     0
    r10    0x0     0
    r11    0xbefff7e8 3204446184
    r12    0x0     0
    sp     0xbefff7d8 0xbefff7d8
    lr     0x0     0
    pc     0x8068  0x8068 <_start+20>
    cpsr   0x10    16

命令“info registers”能够提供当前的寄存器状态。
我们可以看到，这里包括通用寄存器r0-r12，专用寄存器SP、LR和PC，以及状态寄存器CPSR。 函数的前四个参数通常存储在r0-r3中。
在这种情况下，我们可以通过手动方式将其值移动到r0和r1。

显示进程内存映射：

    
    
    gef> info proc map
    process 10225
    Mapped address spaces:
    
     Start Addr   End Addr    Size     Offset objfile
     0x8000     0x9000  0x1000          0   /home/pi/lab/max
     0xb6fff000 0xb7000000  0x1000          0          [sigpage]
     0xbefdf000 0xbf000000 0x21000          0            [stack]
     0xffff0000 0xffff1000  0x1000          0          [vectors]

通过命令“disassemble”，我们可以查看函数max的反汇编输出。

    
    
    gef> disassemble max
     Dump of assembler code for function max:
     0x00008074 <+0>: push {r11}
     0x00008078 <+4>: add r11, sp, #0
     0x0000807c <+8>: sub sp, sp, #12
     0x00008080 <+12>: cmp r0, r1
     0x00008084 <+16>: movlt r0, r1
     0x00008088 <+20>: add sp, r11, #0
     0x0000808c <+24>: pop {r11}
     0x00008090 <+28>: bx lr
     End of assembler dump.

GEF特有的命令（可以使用命令“gef”查看更多命令）：

将所有已加载的ELF镜像的所有节dump到进程内存中

X档案

proc map的增强版本，包括映射页面中的RWX属性

vmmap

给定地址的内存属性

xinfo

检查运行的二进制文件内置的编译器级保护措施

checksec

    
    
    gef> xfiles
         Start        End  Name File
    0x00008054 0x00008094 .text /home/pi/lab/max
    0x00008054 0x00008094 .text /home/pi/lab/max
    0x00008054 0x00008094 .text /home/pi/lab/max
    0x00008054 0x00008094 .text /home/pi/lab/max
    0x00008054 0x00008094 .text /home/pi/lab/max
    0x00008054 0x00008094 .text /home/pi/lab/max
    0x00008054 0x00008094 .text /home/pi/lab/max
    0x00008054 0x00008094 .text /home/pi/lab/max
    0x00008054 0x00008094 .text /home/pi/lab/max
    0x00008054 0x00008094 .text /home/pi/lab/max
    gef> vmmap
         Start        End     Offset Perm Path
    0x00008000 0x00009000 0x00000000 r-x /home/pi/lab/max
    0xb6fff000 0xb7000000 0x00000000 r-x [sigpage]
    0xbefdf000 0xbf000000 0x00000000 rwx [stack]
    0xffff0000 0xffff1000 0x00000000 r-x [vectors]
    gef> xinfo 0xbefff7e8
    ----------------------------------------[ xinfo: 0xbefff7e8 ]----------------------------------------    Found 0xbefff7e8
    Page: 0xbefdf000 -> 0xbf000000 (size=0x21000)
    Permissions: rwx
    Pathname: [stack]
    Offset (from page): +0x207e8
    Inode: 0
    gef> checksec
    [+] checksec for '/home/pi/lab/max'
    Canary:                  No
    NX Support:              Yes
    PIE Support:             No
    RPATH:                   No
    RUNPATH:                 No
    Partial RelRO:           No
    Full RelRO:              No

故障排除

为了更高效地使用GDB进行调试，很有必要了解某些分支/跳转的目标地址。 某些（较新的）GDB版本能够解析分支指令的地址，并能显示目标函数的名称。
例如，下面是缺乏这些功能的GDB版本的输出内容：

    
    
    ...
    0x000104f8 <+72>: bl 0x10334
    0x000104fc <+76>: mov r0, #8
    0x00010500 <+80>: bl 0x1034c
    0x00010504 <+84>: mov r3, r0
    ...

而下面则是提供了上述功能的GDB版本的的输出结果：

    
    
    0x000104f8 <+72>:    bl      0x10334 <free@plt>
    0x000104fc <+76>:    mov     r0, #8
    0x00010500 <+80>:    bl      0x1034c <malloc@plt>
    0x00010504 <+84>:    mov     r3, r0

如果您的GDB版本中没有提供这些功能，可以升级Linux（前提是它们提供了更新的GDB），或者自己编译较新的GDB。
如果您选择自己编译GDB，可以使用以下命令：

    
    
    cd /tmp
    wget https://ftp.gnu.org/gnu/gdb/gdb-7.12.tar.gz
    tar vxzf gdb-7.12.tar.gz
    sudo apt-get update
    sudo apt-get install libreadline-dev python-dev texinfo -y
    cd gdb-7.12
    ./configure --prefix=/usr --with-system-readline --with-python && make -j4
    sudo make -j4 -C gdb/ install
    gdb --version

我使用上面提供的命令来下载、编译和运行Raspbian（jessie）上的GDB，并且没有遇到任何问题。同时，这些命令也将取代以前版本的GDB。如果您不想这样做的话，请跳过以单词install结尾的命令。此外，我在QEMU中模拟Raspbian时也是这样做的，不过这个过程非常耗时，大概需要几个小时，因为模拟环境的资源（CPU）有限。
我使用的GDB版本为7.12，但是你还可以使用更高的版本，为此可以点击此处查看其他版本。

本文翻译自azeria-labs.com [原文链接](https://azeria-labs.com/debugging-with-gdb-introduction/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **shan66** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86536](/post/id/86536)

安全客 - 有思想的安全新媒体

本文转载自: [azeria-labs.com](https://azeria-labs.com/debugging-with-gdb-introduction/)

如若转载,请注明出处： <https://azeria-labs.com/debugging-with-gdb-introduction/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t0137bdcb0fbd458b88.jpg) shan66

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

