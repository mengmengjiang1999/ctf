***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***文章原创作者：xiongchaochao，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  

## 引言

 **本篇文章适用于想要学习ARM汇编在漏洞方面的骚年们。特别是对那些对ARM平台上的漏洞利用写作感兴趣的人，本篇文章是根据azeria-labs.com上面的教程自学而成，总结出一些属于自己的一些学习成果，特意分享给大家。**

您可能已经注意到ARM处理器无处不在，就像我们日常用的Android、IOS系统都因了ARM处理器架构。当我环顾四周时，我可以计算出比我的处理器更多的家用ARM处理器的设备。这包括电话，路由器，不要忘记最近销售似乎爆炸的物联网设备。也就是说，ARM处理器已成为全球最广泛的CPU核心之一。

这使我们认识到，像PC一样，物联网设备容易受到不正确的输入验证滥用，例如缓冲区溢出。鉴于基于ARM的设备的广泛使用以及滥用的可能性，对这些设备的攻击变得更加普遍。不管你是想学嵌入式、漏洞挖掘、Android开发等都是需要了解ARM，快来入手新的技能吧！

每次程序启动的时候，为他分配的内存空间可以分为很多区段，大致归为三类：

> Program Image
>
> Stack
>
> Heap

![1.png](https://image.3001.net/images/20181224/1545652055_5c20c757b4b7f.png!small)

## 栈溢出

这里不介绍栈了，需要了解栈的详细介绍可以看我的另一篇文章[ARM汇编之栈](https://www.jianshu.com/p/49711344487b),下面直接进入正题这里使用的C代码：

    
    
    #include "stdio.h"
    int main(int argc, char **argv)
    {
            char buffer[8];
            gets(buffer);
    }
    

当我们快要执行到gets函数的时候，我们看一下栈分布，红框框起来的两个栈地址，其首地址马上要附给r0，然后作为参数传进gets函数：

![2.png](https://image.3001.net/images/20181224/1545652083_5c20c77348479.png!small)

执行完gets函数，输入7个a后，r0存放的那个栈地址刚好被写满，这里需要留有1字节空间让gets写入空字符（gets会自动补充空字符给输入的字符串后面，所以如果出入的是8个a，那么下面的帧指针地址的低8位就会被空字符覆盖），表示一句字符串的结束。我们可以看见这些用户输入的字符存放的位置是很危险的，在他的下面就是上一个栈帧的帧指针，再往下就是当前栈帧的返回地址，也是当前栈帧的首地址。
**返回地址？** ，如果我们覆盖了它，那还不想干啥就干啥。

![3.png](https://image.3001.net/images/20181224/1545652109_5c20c78d346cd.png!small)

下面我们就具体多输入几个字符，比如输入15个a再看看，可以看到覆盖返回地址完成：

![1.png](https://image.3001.net/images/20181224/1545652140_5c20c7ac5c9f8.png!small)

## 堆溢出：堆（Heap）是一个更复杂的内存区域

堆溢出主要分两类：块内堆溢出、块间堆溢出，为什么分为这两种方式呢？主要是因为他的管理方式，堆会将每个对象打包成一个堆块（eg:malloc,分配堆块的函数）。所以就出现了两个情况，一个堆块内可以覆盖相邻变量的内容、相邻堆块的覆盖堆块结构：头、用户数据区。

![heap1-1.png](https://image.3001.net/images/20181224/1545652182_5c20c7d6860df.png!small)

### 块内堆溢出

下面通过一个例子来帮助理解块内堆溢出。主要是通过给一个有两个变量的结构体申请堆块，然后使用一个变量来覆盖另一个变量，从而达到块内堆溢出存在溢出的代码：

    
    
    #include 
    #include 
    struct struct_a
    {
            char string[8];
            int number;
    };
    int main()
    {
            struct struct_a* objA = malloc(sizeof(struct struct_a));
            objA->number = 1234;
            gets(objA->string);
            if(objA->number==1234)
            {
                    puts("Memory valid!");
            }else{
                    puts("Memory corrupted!");
            }
            return 0;
    }
    

编译后的结果，可以看到当输入8字节的数据的时候，结构体对象内部（堆块内）发生了更改，造成变量number的值变了：

    
    
    pi@raspberrypi:~/Desktop $ ./a.out 
    aaaa
    Memory valid!
    pi@raspberrypi:~/Desktop $ ./a.out 
    aaaaaaa
    Memory valid!
    pi@raspberrypi:~/Desktop $ ./a.out 
    aaaaaaaa
    Memory corrupted!
    

### **详细分析**

先找到gets函数的位置，disassemble
main反汇编程序，第一个bl是malloc申请堆块，第二个bl就是执行gets函数了，然后下断点，运行过去即可：

![1.png](https://image.3001.net/images/20181224/1545652210_5c20c7f2cd978.png!small)

运行过去后，执行这个函数，正常输入7字节数据，即7个a，这个时候我们使用vmmap查看整个内存空间的映射，可以从下图看到，这个堆块的开始位置是0x00021000，然后使用x/8x查看堆后的8个双字的数据。可以看到7个a成功写入这个区域，并且紧随其后的就是结构体的另一个int型变量number，很明显如果不对输入进行长度判断，就会导致堆块内另一个变量的内存数据进行覆盖，下面具体操作一下。

这次验证我们选择输入8个a，再次进行上面同样的操作，和上面 的输出对比，0x000004d2被改成了0x00000400,为什么会这样呢?因为
gets函数会自动向字符串结尾添加空字符并且堆块内的这个字符数组变量被占满了，所以gets向下添加空字符，造成同一个堆块内的另一个int型变量被覆盖了。

    
    
    gef> x/8x 21000
    0x21000:    0x00000000    0x00000011    0x61616161    0x61616161
    0x21010:    0x00000400    0x00020ff1    0x00000000    0x00000000
    

### 块间堆溢出

这里申请了两个堆块，一个字符型堆块、一个int型堆块：

    
    
    #include 
    #include 
    int main()
    {
        char string = malloc(8);
        int number = malloc(4);
        *number = 1234;
    gets(string);
    
    if(*number == 1234)
    {
            puts("Memory vaild!");
    }else
    {
            puts("Memory corrupted!");
    }
    return 0;
    }
    

这里我们展示一下，溢出覆盖过程。第一次输入15个a，int型堆块内的数据正常、但是输入16个a后，int型堆块就被覆盖了。 **为什么会这样呢？**
首先int型堆块（4字节）在char型堆块后面（8字节），当char型堆块向后覆盖时，需要先覆盖int型堆块的8字节长度的堆头，然后就覆盖到了int型堆块的用户数据区，也就是至少需要16字节数据才可以。

    
    
    pi@raspberrypi:~/Desktop $ ./a.out 
    aaaaaaaaaaaaaaa
    Memory vaild!
    pi@raspberrypi:~/Desktop $ ./a.out 
    aaaaaaaaaaaaaaaa
    Memory corrupted!
    

下面我们查看用户输入16字节数据后的内存数据：

1.gdb ./a.out

2.disassemble main找到第三个ld就是gets的指令地址，然后下断点，运行到断点处，执行后输入7字节和16字节，做对比

3.vmmap查找整个内存空间映射

4.x/8x
21000:查看申请堆块内的数据输入7字节数据后，第一行是char型堆块的堆头和用户数据输入16字节数据后，明显int型堆块的堆头被覆盖后，gets函数将空字符写入到用户数据空间，覆盖了1234的低8位：

![微信图片_20181225180114.png](https://image.3001.net/images/20181225/15457320852831.png!small)

到此基本比较基础的介绍了ARM汇编在堆栈溢出的运用。

## 参考文章

> [azeria-labs官方的Arm汇编教程](https://azeria-labs.com/process-memory-and-memory-> corruption/)

 ***文章原创作者：xiongchaochao，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

