今天进行的实验是CTF PWN练习之返回地址覆盖，来体验一下新的溢出方式。

学习地址覆盖之前还有些小知识需要掌握，不然做题的时候你肯定一脸懵逼,首先是函数调用约定，然后还要知道基本的缓冲区溢出攻击模型。

 **函数调用约定**

函数调用约定描述了函数传递参数的方式和栈协同工作的技术细节，不同的函数调用约定原理基本相同，但在细节上是有差别的，包括函数参数的传递方式、参数的入栈顺序、函数返回时由谁来平衡堆栈扥。本实验中着重讲解C语言函数调用约定。

通过前面几个PWN系列实验的学习，我们可以发现在gdb中通过disas指令对main函数进行反汇编时，函数的开头和结尾的反汇编指令都是一样的：

push %ebp

mov %esp,%ebp

......

leave

ret

在函数大开头，首先是一条push %ebp指令，将ebp寄存器压入栈中，用于保存ebp寄存器的值，接着是mov
%esp,%ebp将esp寄存器的值传递给ebp寄存器；在函数的末尾，leave指令相当于mov %ebp,%esp和pop
%ebp两条指令，其作用刚好与开头的两条指令相反，即恢复esp和ebp寄存器的内容。

如果在函数A中调用了函数B，我们称函数A为主调函数，函数B为被调函数，如果函数B的声明为int B(int arg1, int arg2, int
arg3)，那么函数A中的调用函数B时的汇编指令的形式如下：

push arg3

push arg2

push arg1

call B

连续三个push将函数的参数按照从右往左的顺序进行压栈，然后执行call
B来调用函数B。注意在gdb中看到的效果可能不是三个push，而是三个mov来对栈进行操作，这是因为Linux采用AT&T风格的汇编，而上面的指令使用的是Intel风格的汇编，比较容易理解。

call指令的内部细节为：将下一条指令的地址压入栈中，然后跳转到函数B去执行代码。这里说的call下一条指令的地址也就是通常所说的返回地址。函数B最后一条retn指令会从栈上弹出返回地址，并赋值给EIP寄存器，达到返回函数A继续执行的目的。

![headImg.action?news=666b7c59-65b8-4d61-a443-512ac67c7322.png](https://image.3001.net/images/20210322/1616398871_60584a1734733e7521621.png!small)

 **基本的缓冲区溢出攻击模型**

基本的缓冲区溢出攻击通常是通过改写函数返回地址的形式来发起攻击的。如A调用B函数，正常情况下B函数返回时执行retn指令，从栈上取出返回地址跳转回A函数继续执行代码。而一旦返回地址被缓冲区溢出数据改写，那么我们就可以控制函数B跳转到指定的地方去执行代码了。

![headImg.action?news=2a74cade-00ba-4e0f-ba1f-5393ae106750.png](https://image.3001.net/images/20210322/1616398871_60584a17c0aa517a0d32c.png!small)

### 1\. 实验内容和步骤

本文涉及相关实验：[《PWN练习之返回地址覆盖》](https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182014110409173900001&pk_campaign=freebuf-wemedia)。

做实验前先好好审题，看一下描述。

主机/home/test/5目录下有一个pwn5程序，执行这个程序可以输入数据进行测试，正常情况下程序接收输入数据后不会产生任何输出信息并直接退出，然后当输入一定的数据量时，可能会提示
**Segmentation fault**
的错误信息，当输入的精心构造的输入数据时可对程序发起溢出攻击，达到改写程序执行流程的目的，攻击成功时将输出如下信息：

 **Congratulations, you pwned it.**

请对pwn5程序进行逆向分析和调试，找到程序内部的漏洞，并构造特殊的输入数据，使之输出成功的提示信息。

使用cd /home/test/5切换到程序所在目录，执行cat pwn5.c即可看到源代码：

#include <stdio.h>

void win()

{

printf("Congratulations, you pwned it.\n");

}

int main(int argc, char** argv)

{

char buffer[64];

gets(buffer); // 存在缓冲区溢出

return 0;

}

程序定义了一个64字节大小的buffer数组，然后使用gets获取输入数据，我们知道gets是不安全的函数，这里会引发缓冲区溢出，栈上函数的返回地址可以被改写，当返回地址被改写为win函数的地址时，就可以输出成功提示的信息。

gets(buffer)这个溢出太明显了，问题就是不知道我们要输入多少位才能溢出。

执行gdb pwn5即可开始通过gdb对pwn5进行调试，现在我们需要阅读main函数的汇编代码，在gdb中执行disas main命令即可：

我们首先使用b *0x080483f8对main函数的第一条指令下一个断点，同时使用b
*0x08048408对gets函数的调用下一个断点，然后输入r命令运行程序，将会在第一个断点处断下，如下图所示：

![headImg.action?news=c22021b3-9df2-4ce3-9d2c-a715d4eca654.png](https://image.3001.net/images/20210322/1616398872_60584a18754f6a1028241.png!small)

这时候运行i r
$esp来查看esp寄存器的值，通过前面对函数调用约定的分析，我们知道这时候栈顶存储的就是返回地址，这时候esp寄存器的值为0xffffd6cc。

在gdb中输入c命令让程序继续执行，将在第二个断点断下，通过对汇编指令的分析，我们知道eax寄存器存储了buffer的起始地址，所以运行i r
$eax来查看buffer的地址：

![headImg.action?news=99013fac-420f-4438-ac24-5ef7ee1ba589.png](https://image.3001.net/images/20210322/1616398873_60584a19002f5d4a09be0.png!small)

我们看到eax寄存器的值为0xffffd680，那么这两个地址的差为76，如下图下图所示：

![headImg.action?news=39a214e9-c1a3-49f6-b706-bbbbdd70a068.png](https://image.3001.net/images/20210322/1616398874_60584a1a03d43b3f4ee8a.png!small)

也就是说，在覆盖了76字节数据后，如果再覆盖4个字节，就可以把返回地址覆盖为我们想要的地址了。

在gdb中执行disas win查看win函数的地址为0x080483e4，接下来就可以构造输入数据来发起溢出攻击了。

我们只要合理控制输入数据的第77~80字节的内容，就可以实现对函数返回地址进行覆盖，从而成功发起溢出攻击了。

现在win函数的地址为0x080483e4，转换为小端格式是’\xe4\x83\x04\x08’，那么可以构造这样的命令来进行溢出测试：

python -c "print 'A'*76+'\xe4\x83\x04\x08'" | ./pwn5

攻击效果如下图所示：

![headImg.action?news=fde503c7-e89e-4654-88ba-927a42493016.png](https://image.3001.net/images/20210322/1616398874_60584a1a9b0ca2df366b3.png!small)

