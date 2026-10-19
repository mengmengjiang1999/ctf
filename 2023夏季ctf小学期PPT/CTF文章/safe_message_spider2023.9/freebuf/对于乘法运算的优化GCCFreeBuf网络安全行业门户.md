# 序

主要通过观察反汇编代码来观测编译器对代码的优化策略，主要观察 **默认情况下的优化策略** 与`-O1`编译选项下的优化策略

 **乘法指令对应的汇编指令为：**

  * 有符号乘法`imul`
  * 无符号乘法`mul`

乘法指令执行周期过长，编译器 **会首先通过移位配合加法、减法来完成** ，当使用这些指令都无法完成时，才会使用乘法指令

# 实例代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int main(int argc,char** argv)
    {
    
            int nVarOne = argc;
            int nVarTwo = argc;
    
            printf("nVarOne * 15 = %d",nVarOne * 15);
    
            printf("nVarOne * 16 = %d",nVarOne * 16);
    
            printf("nVarOne * 4 + 5 = %d",nVarOne * 4 + 5);
    
            printf("nVarOne * nVarTwo = %d",nVarOne * nVarTwo);
    
            return 0;
    }
    

# 逐行观察

## 无优化选项

### 基础变量的赋值

![1666766785_6358d7c18ab37dae98a0c.png!small?1666766777773](https://image.3001.net/images/20221026/1666766785_6358d7c18ab37dae98a0c.png!small?1666766777773)

如图所示，在不优化的前提下，会先将`argc`与`argv`(地址)
分别放入栈中，之后再依据代码，将`argc`分别放在`nVarOne`和`nVarTwo`变量所对应的地址中

`nVarOne : $rbp - 0x8`

`nVarTwo : %rbp - 0x14`

### 1：`printf("nVarOne * 15 = %d",nVarOne * 15);`

![1666766790_6358d7c6226bb6cfc177d.png!small?1666766782378](https://image.3001.net/images/20221026/1666766790_6358d7c6226bb6cfc177d.png!small?1666766782378)

`nVarOne * 15`的操作在红色方框中实现，编译器并没有直接使用乘法指令，而是 **借助了`16 - 1 =
15﻿`这个简单的机制**，进行了一定的优化：

  1. `mov edx,DWORD PTR [rbp-0x8]`将`nVarOne`的值（也就是`1`） 放入`rdx`寄存器低位中
  2. `mov eax,edx`再将`1`放入`rax`寄存器的低位中
  3. `shl eax,0x4`关键操作：使用左移运算将乘法拆分， **左移 4 位，此时`eax = 16`**
  4. `sub eax,edx`由于`edx`中的值为`1`，所以完成`16 - 1 = 15`的运算，这也正是我们`nVarOne * 15`的结果
  5. `mov esi,eax`将结果放入`esi`，用于后续传给`printf`即可

### 2：`printf("nVarOne * 16 = %d",nVarOne * 16);`

![1666766793_6358d7c94c879d7e63a1d.png!small?1666766785535](https://image.3001.net/images/20221026/1666766793_6358d7c94c879d7e63a1d.png!small?1666766785535)

有了上一个优化的方法，这个就非常简单了， **直接 左移 4 位即可**

  * `shl eax,0x4`左移`4`位`eax = 16`

### 3：`printf("nVarOne * 4 + 5 = %d",nVarOne * 4 + 5);`

![1666766796_6358d7cc72a6e5b1f3988.png!small?1666766788670](https://image.3001.net/images/20221026/1666766796_6358d7cc72a6e5b1f3988.png!small?1666766788670)

方式同上：将`nVarOne * 4 + 5`转换为`nVarOne << 2 + 5`

`shl eax,0x2``add eax,0x5`

### 4：`printf("nVarOne * nVarTwo = %d",nVarOne * nVarTwo);`

![1666766799_6358d7cf4f8fafe9ca2e8.png!small?1666766791564](https://image.3001.net/images/20221026/1666766799_6358d7cf4f8fafe9ca2e8.png!small?1666766791564)

此时由于`nVarOne`与`nVarTwo`均为未知变量，而不像上述几种情况中带有常量，所以在非 O1 优化的情况下，
**直接使用`imul`有符号乘法进行相乘**

## O1 优化选项

在 O1 优化的情况下，没有给`nVarOne`与`nVarTwo`分配空间，而是直接将参数作为局部变量来使用，所以甚至没有设置`rbp`的值，唯一的开辟的
8 字节空间只是为了保存之前`rbp`的值

### 1：`printf("nVarOne * 15 = %d",nVarOne * 15);`

![1666766803_6358d7d30084aa515b177.png!small?1666766795225](https://image.3001.net/images/20221026/1666766803_6358d7d30084aa515b177.png!small?1666766795225)

整体的思路还是`1 << 4 - 1`但此时没有使用栈空间，而是直接将`argc`的值放入`ebp`中 （`mov ebp ,
edi`），再直接对`ebp`进行移位与减法的操作，最终将其放入`rdx`进行输出即可

![1666766806_6358d7d663cd51ad93a49.png!small?1666766798745](https://image.3001.net/images/20221026/1666766806_6358d7d663cd51ad93a49.png!small?1666766798745)

### 2：`printf("nVarOne * 16 = %d",nVarOne * 16);`

![1666766809_6358d7d94d3a7eebf2aae.png!small?1666766801544](https://image.3001.net/images/20221026/1666766809_6358d7d94d3a7eebf2aae.png!small?1666766801544)

此处直接传递`ebp`中的值，由于`ebp`之前的值未`1 << 4`，所以此处直接输出即可

### 3：`printf("nVarOne * 4 + 5 = %d",nVarOne * 4 + 5);`

![1666766812_6358d7dcb9313503ee247.png!small?1666766804954](https://image.3001.net/images/20221026/1666766812_6358d7dcb9313503ee247.png!small?1666766804954)

之前将`edi`的值传递了两次，一个份放在了`ebp`中，一份放在了`ebx`中，此处的这种优化方式就比较有意思了，区别于之前的先移位在做加法，此处直接借用`lea`指令完成计算，当这种组合运算中的乘数`≠
2、4、8`时，编译器首先会尝试将乘数拆分为`2、4、8`的一种再配合其余运算，若无法拆分则使用`imul`计算或其余优化方式

`nVarOne * 9 + 5`

![1666766816_6358d7e0f0079059ab4a8.png!small?1666766809127](https://image.3001.net/images/20221026/1666766816_6358d7e0f0079059ab4a8.png!small?1666766809127)

### 4：`printf("nVarOne * nVarTwo = %d",nVarOne * nVarTwo);`

![1666766819_6358d7e3d0dcc04ed9a20.png!small?1666766812085](https://image.3001.net/images/20221026/1666766819_6358d7e3d0dcc04ed9a20.png!small?1666766812085)

此处依旧是使用`imul`无符号乘法进行运算

