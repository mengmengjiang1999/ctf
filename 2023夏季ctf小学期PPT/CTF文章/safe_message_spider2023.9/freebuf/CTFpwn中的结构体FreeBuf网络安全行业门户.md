**这段时间我一直在做CTF的堆溢出题目，漏洞利用其实并不算太难，做多了就有经验了。难点在代码审计，使用IDA进行反汇编以后的代码实在太难看了，遇到了很多问题，这里遇到了一个二重指针，搞得我花了一天时间重新学习结构体**

# 反汇编出二级指针

![image.png](https://image.3001.net/images/20211006/1633501534_615d415eb713bf27d4917.png!small)  
![image.png](https://image.3001.net/images/20211006/1633501550_615d416ec6841b128c9e2.png!small)  
其实这个问题早就出现了，但是之前都是硬着头皮过了，但如果不搞明白这个问题，我就无法继续好好做题。这里ptr本身就是个指针类型，结果再次进行取址斌且求其偏移，最开始以为是一个二维数组，但是看wp的时候大佬分析出了结构体，我就明白了我对C语言还是不太了解

# 结构体的相关知识

我们之前很早就了解过结构体，但是真的了解结构体嘛？首先写一段代码

    
    
    #include <stdio.h>
    typedef struct Node{
        int a;
        char *b;
        char c;
    } node;
    
    int main(){
        node n1;
        printf("%d\n",sizeof(n1.a));
        printf("%d\n",sizeof(n1.b));
        printf("%d\n",sizeof(n1.c));
        printf("%d\n",sizeof(n1));
    
    }
    

然后我们进行编译一下  
![image.png](https://image.3001.net/images/20211006/1633502692_615d45e4c5120c15d9d8c.png!small)我们发现这三个变量大小相加以后小于变量n1的大小。  
系统在读取代码的时候，其实是按照一个标准字长的跨步是最快的。所以我们申请了结构体变量以后会存在内存对齐。int类型占4个字节，指针占一个标准字长(64位就是八个字节)，而一个char类型占1个字节。大部分的程序编译为汇编语言以后，在栈中都是以RBP寄存器来定位的(大部分，因为我之前做过有的题里面是以RSP来定位的)，因为RBP在栈帧中是不会变的。我们可以再看一下它的地址

    
    
    #include <stdio.h>
    typedef struct Node{
        int a;
        char *b;
        char c;
    } node;
    
    int main(){
        node n1;
        printf("%p\n",&n1.a);
        printf("%p\n",&n1.b);
        printf("%p\n",&n1.c);
    
    
    }
    

![image.png](https://image.3001.net/images/20211006/1633503254_615d4816435ebac1e91f5.png!small)画个图大概是这个样子  
![image.png](https://image.3001.net/images/20211006/1633503675_615d49bbe85d352b25ae7.png!small)

# 结构体的变量名

我们都知道&n1代表了结构体的首地址，也是上面代码中n1.a的地址![image.png](https://image.3001.net/images/20211006/1633503830_615d4a56257cb848e172f.png!small)

    
    
    #include <stdio.h>
    typedef struct Node{
        int a;
        char *b;
        char c;
    } node;
    
    int main(){
        node n1;
        printf("%p\n",&n1.a);
        printf("%p\n",&n1.b);
        printf("%p\n",&n1.c);
        printf("%p\n",&n1);
        printf("%p\n",n1);
    
    }
    

![image.png](https://image.3001.net/images/20211006/1633503905_615d4aa184d5078988d22.png!small)我这次把n1也放进去了，我想知道结构体的变量名表示什么。当然我们已经知道了&n1=&n1.a，那么单一个变量名又是什么意思？我在gdb中进行了一波调试。  
首先是运行的结果![image.png](https://image.3001.net/images/20211006/1633504202_615d4bca82d260b21df39.png!small)然后我们调试，我们都知道在64位操作系统中先将参数放入寄存器然后再call函数。![image.png](https://image.3001.net/images/20211006/1633504326_615d4c465a9a6c78b615a.png!small)没错，与我们的输出是一样的，但是RSI里面存放的到底是什么？  
![image.png](https://image.3001.net/images/20211006/1633504422_615d4ca68a1cc2fc21794.png!small)  
![image.png](https://image.3001.net/images/20211006/1633504446_615d4cbe1cf1fc5c080f4.png!small)虽然挺离谱，但是不得不相信，我们第五次调用print之前，是没有对RSI做出改动的。也就是说RSI里面的值是第四次printf的时候用剩下的产物。注意看RSI的地址中存放的内容![image.png](https://image.3001.net/images/20211006/1633504621_615d4d6d3439ddd336e35.png!small)这是在第四次printf之前RSI里面存放的内容，而调用完printf以后![image.png](https://image.3001.net/images/20211006/1633504693_615d4db5b9090147f3fee.png!small)也就是说我们的RSI是在第四次printf中发生了改变，并且把之前的地址放入另外一个地址中。

综上所述，结构体变量名什么也不能代表，而是上一次变动完以后剩下来的产物

**没错，结果就是挺离谱的。花了这么长的时间，结果就是它什么也不是。但是这并不是没有任何意义的，至少我们探寻出了一个结果。那么还剩下一个问题就是为什么RSI最后的地址，存放着上一次RSI的值？这究竟是巧合还是作者有意为之？大家可以自己再调试一下看一看，我估计是有意为之**

# 二级指针

我们已经完全了解了结构体。但是二级指针又怎么说呢？如何就会出现二级指针呢？首先我们要知道IDA的反汇编并不一定是绝对正确的。在这样的一个前提下，反汇编的内容我们可以相信一部分，我们还需要脑补一部分(如果不脑补的话有些语句我们确实无法理解)，于是我们可以这样构造一个结构体

    
    
    typedef struct Test{
        char *a;
        int b;
        char c;
    } test;
    test *t1;
    int main(){
        t1 = malloc(num);
    }
    
    

这样我们看一下如何出现二级指针  
我们已经知道了a占8字节，b占4字节，c占1字节，那么我们应该如何寻找a？`t1->a`这个就代表一个字符串。它还可以这么写`*(&t1->a)`。

好的，现在已经出现二级指针，那么我们该如何寻找b呢？也就是说t1->a加上a和b的偏移量也就是8，我们可以这么写`*(&t1->a+1)`，我们回过头看看CTF中截的那张图![image.png](https://image.3001.net/images/20211006/1633509121_615d5f014a86aab4cf5a4.png!small)格式一模一样。那么为什么是加1呢？这里的a由于是指针类型，所以加1就相当于加8.例如

    
    
    int a[10]
    

那么a+1是和头指针偏移量为1吗？并不是，应该是一个int的大小，同理这里也一样，如果想要改，可以进行强制类型转换`(char*)a+4`,效果一样。于是我们可以得出b的位置就是(char*)&n1->a+8。同理c也一样。

    
    
    #include <stdio.h>
    #include <stdlib.h>
    typedef struct Node{
        char *a;
        int b;
        char c;
    } node;
    node *n1;
    int main(){
        n1 = malloc(100);
        printf("%p\n",((char*)&n1->a+8));
        printf("%p\n",(&n1->b));
    
    }
    

![image.png](https://image.3001.net/images/20211006/1633510283_615d638bccd3f049d8888.png!small)

**这篇文章说了很多的废话和十分基础的东西，可能大佬都已经会了，但是这些都是我在写的过程中遇到的坑，小白可能更容易接受。我的C也是两年前学的，很多基础的知识后来都没有使用过，所以忘了不少东西。但是这次确实学会很多东西**

 **本文章参考的文章太多了，都是有关pwn的，这里就不写了，总之感谢前辈大佬**

