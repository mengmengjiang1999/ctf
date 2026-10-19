**最近刚刚接触到PLT与GOT，所以就想以此篇文章来巩固一下我对于这对姐妹花的理解啦！刚刚接触，理解不深，还请大佬轻喷！**

> 环境：ubantu 16.04

## 一、程序运行过程

首先我们对于程序运行来有一个基本的概念，程序运行起来应经过四个步骤：预处理、编译、汇编和链接，过程如下。

![](https://image.3001.net/images/20200402/1585809624_5e8588d81ae53.png!small)

汇编过程调用汇编器as来完成，是用于将汇编代码转换成机器可以执行的指令，每一个汇编语句几乎都对应一条机器指令。汇编生成的文件时test.o。

链接的主要内容就是将各个模块之间相互引用的部分正确的衔接起来。它的工作就是把一些指令对其他符号地址的引用加以修正。链接过程主要包括了地址和空间分配、符号决议和重定向。

## 二、代码示例引入

对程序运行有个大致的概念后，我们再利用一个小程序来引入对PLT和GOT姐妹花的正式的讲解啦！

首先咱上程序：

    
    
    #include<stdio.h>
    void print_banner()
    {
    printf("Welcome to World of PLT and GOT\n");
    }
    int main(void)
    {
    print_banner();
    return 0;
    }  
    

（PS：如果执行以下两步出现：fatal error: sys/cdefs.h: No such file or
directory的错误，请参照[链接](<https://blog.csdn.net/huangwei2014/article/details/93191309>)，还有错误的话，就自行百度吧！应该不麻烦，没事，顶多改几天配置嘛，哈哈！）

编译

    
    
    gcc -Wall -g -o test.o -c test.c -m32

链接：  

    
    
    gcc -o test test.o -m32

由程序运行我们可以知道，汇编完成后形成文件 test.o，所以接下来我们通过以下命令查看反汇编代码。  

    
    
    objdump -d test.o

### 1、链接重定向的产生

按照程序执行的逻辑，执行函数调用时调用
call+函数地址，然后再函数运行完ret指令进行返回，这样便完成了一次函数的调用。因此print_banner()函数反汇编的代码应该类似于下面：call
+ printf的地址

    
    
     00000000 <print_banner>:
       0:	       	push   %ebp
       1:	       	mov    %esp,%ebp
       3:	       	sub    $0x8,%esp
       6:	       	sub    $0xc,%esp
       9:	       	push   $0x0
       e:	       	call   *printf的地址*
      13:	       	add    $0x10,%esp
      16:	       	nop
      17:	       	leave  
      18:	       	ret   

但是事实和我们的想象总是那么的不符！！

![](https://image.3001.net/images/20200402/1585810101_5e858ab584961.png!small)

从上图我们可以看出，编译完成后，直接看 call +<>，似乎是 call + printf 函数的地址，但是看机器码我们发现，main() 和
print_banner() 函数中 ”<> “ 中指的都是机器码 “ff ff ff fc”（表示），这表示 “ff ff ff fc”
只是一个函数地址的代号。也就是说链接前函数都是用 ff ff ff fc 代替，也就是有符号数字 “-4”代替。

这也就表示尽管 printf_banner() 函数调用了 printf函数，但是在链接前无法知道printf的地址的。那么
printf的地址在哪里呢？printf函数在glibc动态链接库中。

现在我们可以知道，程序执行时，glibc动态库装载了（即printf函数的地址确定了），但是程序在汇编时是不知道 printf
函数的地址，也就是说在函数链接时才知道 printf函数的地址；即函数在链接时，call + printf函数地址，但是之前汇编时 call 为 “call
+ -4”，这说明运行时call发生了链接重定向。

拓展：静态链接和动态连接

在这里我们对链接的过程进行简要的介绍一下：

>
> [参考链接](https://blog.csdn.net/weixin_41143631/article/details/81221777?depth_1-utm_source=distribute.pc_relevant.none-> task&utm_source=distribute.pc_relevant.none-task)

静态链接是由链接器在链接时将库的内容加入到可执行程序中的做法。链接器是一个独立程序，将一个或多个库或目标文件（先前由编译器或汇编器生成）链接到一块生成可执行程序。静态链接是指把要调用的函数或者过程链接到可执行文件中，成为可执行文件的一部分。

动态链接所调用的函数代码并没有被拷贝到应用程序的可执行文件中去，而是仅仅在其中加入了所调用函数的描述信息（往往是一些重定位信息）。仅当应用程序被装入内存开始运行时，在Windows的管理下，才在应用程序与相应的DLL之间建立链接关系。当要执行所调用DLL中的函数时，根据链接产生的重定位信息，Windows才转去执行DLL中相应的函数代码。

### 2、链接重定向的分析

在这里我们的是动态链接，我么可以发现尽管在链接时函数call发生了链接重定位，对call后面的内容进行了修改。但是并不能直接修改成call +
printf的glibc动态库地址，因为glibc的动态库地址是在运行时才与应用程序产生关系的，而运行时call所处的代码段不能发生修改。那么如何将call与printf的glibc动态链接库连接起来呢？

答案是：如果要将call与printf的glibc动态链接库连接起来的话，那么在链接重定向时，首先call+0xXX，然后链接器在0xXX处应该产生一个链接代码，对printf进行调用，从而将二者连起来。

链接器生成的伪代码如下:

    
    
    .text
    ...
    
    
    // 调用printf的call指令
    call printf_stub
    ...
    
    
    printf_stub:
        mov rax, [printf函数的储存地址] // 获取printf重定位之后的地址
        jmp rax // 跳过去执行printf函数
    
    
    .data
    ...
    printf函数的储存地址：
    　　这里储存printf函数重定位后的地址
      
    

链接阶段，printf定义在动态库中，链接器生成一段小代码printf_stub，然后代码段中call
+printf_stub，形成对printf_stub的调用。从而转化为链接阶段对printf_stub做链接重定位，而运行时才对printf做运行重定位。如下是对于代码的一个雏形图。

![](https://image.3001.net/images/20200402/1585810321_5e858b912ce26.png!small)

### 3、GOT和PLT的形成

由上我们可以知道，连接代码有以下两部分组成：

> 调用跳转代码：调用函数的绝对地址然后跳转到动态链接库。
>
> 库函数的地址为跳转代码做准备。

当文件中出现多个函数调用时，那么每个函数调用都会出现这两个东西，因此对这两个代码段进行命名。

存放函数地址的数据表，称为全局偏移表（GOT：主要存放所有的全局指针，存放着函数的绝对地址）。

存放调用跳转代码的过程表，称为过程链接表（PLT：call跳转PLT表，然后PLT表在call + GOT的绝对地址实现函数的调用）。

如下，为动态链接的一个简要示意图：

![](https://image.3001.net/images/20200402/1585810447_5e858c0fbda3a.png!small)

现在我们知道了函数在调用时需要产生PLT表和GOT表作为连接代码将代码和动态库进行连接，那么代码到底是怎么实现这个链接的呢？我们接着往下看。

## 三、延迟重定位

从上面可知，当需要对一个函数进行调用时，他的汇编代码call首先会掉用PLT表，然后PLT再通过调用GOT与动态库实现重定位连接，这样函数调用动态库时便类似于间接
jmp+地址。

但是如果当一个文件中存在大量的函数时，如果在程序运行前就重定位好所有的函数调用的话虽然会减轻函数调用的时间，但是会大大增加程序的启动时间，是整个程序变得很慢。因此Linux便产生了延迟重定位：也就是当你调用函数的时候函数才开始执行重定位和地址解析工作。

因此便形成了以下代码来实现延迟定位：

    
    
    //一开始没有重定位的时候将 printf@got 填成 lookup_printf 的地址
    void printf@plt()
    {
    address_good:
        jmp *printf@got            // 链接器将printf@got填成下一语句lookup_printf的地址
    
    
    lookup_printf:
            调用重定位函数查找printf地址，并写到printf@got
    
    
            goto address_good;
    }
      
    

从代码可知，没有重定位时执行printf@plt时，printf@got存放的是下一句的地址，类似于 jmp
lookup_printf，而在lookup函数中查找printf地址，然后写到printf@got中，最后在利用 goto 回到 jmp
printf@got，实现 printf 函数的调用。如下为函数调用的示意图。

![](https://image.3001.net/images/20200402/1585810552_5e858c78744e8.png!small)

## 四、代码验证重定位

接下来，我们用上面的代码示例对其进行验证。

我们利用以下代码查看plt中的内容。

    
    
    objdump -d test > test.asm  
    

接下来打开test.asm，查看其中的地址。（在这里由于第一个是一个公共的我先将改为common@plt便于之后理解，至于为什么是公共的请接着往下看。）  

    
    
    Disassembly of section .plt:
    
    080482d0 <common@plt-0x10>:
     80482d0:       ff 35 04 a0 04 08       pushl  0x804a004
     80482d6:       ff 25 08 a0 04 08       jmp    *0x804a008
     80482dc:       00 00                   add    %al,(%eax)
            ...
    080482e0 <puts@plt>:
     80482e0:       ff 25 0c a0 04 08       jmp    *0x804a00c
     80482e6:       68 00 00 00 00          push   $0x0
     80482eb:       e9 e0 ff ff ff          jmp    80482d0 <_init+0x28>
    
    080482f0 <__libc_start_main@plt>:
     80482f0:       ff 25 10 a0 04 08       jmp    *0x804a010
     80482f6:       68 08 00 00 00          push   $0x8
     80482fb:       e9 d0 ff ff ff          jmp    80482d0 <_init+0x28>
      
    

下面我们用gdb命令查看.plt中jmp跳转地址内的指定的内容，命令如下：gdb test 和 b main  

    
    
    gdb-peda$ x/x 0x804a00c
    0x804a00c:	0x080482e6
    gdb-peda$ x/x 0x804a010
    0x804a010:	0x080482f6
    gdb-peda$ x/x 0x804a008
    0x804a008:	0x00000000  
    

之前的plt，如下图，我们发现，<puts@plt>和<__libc_start_main@plt>的第一个jmp跳转的是下一句的地址

![](https://image.3001.net/images/20200402/1585810772_5e858d5432595.png!small)

接下来，我们开始（run）运行程序，由于我们的断点是在b main，如下图程序停在了call
<print_banner>处，这说明main开始调用了但是print_banner并没有开始调用。

![](https://image.3001.net/images/20200402/1585810795_5e858d6b1242c.png!small)

然后我们查看之前plt中jmp的地址。发现<__libc_start_main@plt>和<common@plt>中的jmp后面的地址发生了改变，即他们发生了重定向，而<puts@plt>的并没有改变，刚好main被调用了了，而printer_banner并没有调用。这刚好证实了前面说的延迟重定位机制，只有当函数调用的时候才开始重定向。

    
    
    gdb-peda$ x/x 0x804a00c
    0x804a00c:	0x080482e6
    gdb-peda$ x/x 0x804a010
    0x804a010:	0xf7e1c540
    gdb-peda$ x/x 0x804a008
    0x804a008:	0xf7fee000  
    

## 五、函数执行流程图

下面，附上两张大佬的调用图吧！

![](https://image.3001.net/images/20200402/1585810874_5e858dbab5852.png!small)

![](https://image.3001.net/images/20200402/1585810926_5e858dee25ae1.png!small)

最后，文章就到这吧，其他的后续想到再来续写吧！

## 参考链接

>
> 【1】[Pwn基础：PLT&GOT表以及延迟绑定机制](https://mp.weixin.qq.com/s?__biz=MzU5OTU3NDEzOQ==&mid=2247484367&idx=1&sn=8303e2efdcc817e43a0973c2768d36d7&chksm=feb390dbc9c419cd89b304489454e52f1d1c82d3725f4a5951af97df72921083055f0be1e890&mpshare=1&scene=23&srcid=0401NIjTxyVk8V4NhJt1nTyW&sharer_sharetime=1585711929327&sharer_shareid=ff83fe2fe7db7fcd8a1fcbc183d841c4#rd)
>
>
> 【2】[聊聊Linux动态链接中的PLT和GOT（１）——何谓PLT与GOT](https://blog.csdn.net/linyt/article/details/51635768)
>
>
> 【3】[聊聊Linux动态链接中的PLT和GOT（２）——延迟重定位](https://blog.csdn.net/linyt/article/details/51636753?depth_1-utm_source=distribute.pc_relevant.none-> task&utm_source=distribute.pc_relevant.none-task)
>
>
> 【4】[聊聊Linux动态链接中的PLT和GOT（３）——公共GOT表项](https://blog.csdn.net/linyt/article/details/51637832?depth_1-utm_source=distribute.pc_relevant.none-> task&utm_source=distribute.pc_relevant.none-task)
>
> 【5】[聊聊Linux动态链接中的PLT和GOT（4）——
> 穿针引线](https://blog.csdn.net/linyt/article/details/51893258?depth_1-utm_source=distribute.pc_relevant.none-> task&utm_source=distribute.pc_relevant.none-task)

 ***本文作者：Plutol，转载请注明来自FreeBuf.COM**

