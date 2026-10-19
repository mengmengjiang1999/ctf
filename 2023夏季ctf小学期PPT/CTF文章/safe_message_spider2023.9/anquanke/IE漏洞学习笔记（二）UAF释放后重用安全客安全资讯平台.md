# IE漏洞学习笔记（二）：UAF释放后重用

阅读量 **1041642**

|评论 **7**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-11-11 16:30:38

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## UAF基础概念

UAF漏洞全称为use after
free，即释放后重用。漏洞产生的原因，在于内存在被释放后，但是指向指针并没有被删除，又被程序调用。比较常见的类型是C++对象，利用UAF修改C++的虚函数表导致的任意代码执行。

在了解UAF是导致任意代码执行的细节，首先让我们了解几个概念：

悬挂指针、内存占坑、C++虚函数

实验源码如下

    
    
    // UAFv1.cpp : 定义控制台应用程序的入口点。
    //
    #include<iostream>
    using namespace std;
    #include "stdafx.h"
    #include<stdio.h>
    #include<Windows.h>
    #define size 32
    
    
    class Base
    {
    public :
        int base;
        virtual void f(){ cout<<"Base::f()"<<endl;}
        virtual void g(){cout<<"Base::g()"<<endl;}
        virtual void h(){cout<<"Base::h()"<<endl;}
    };
    class Child:public Base
    {
    public:
        int child;
        void f(){cout<<"Child::f()"<<endl;}
        void g1(){cout<<"Child::g1()"<<endl;}
        void h1(){cout<<"Child::h1()"<<endl;}
    };
    
    int _tmain(int argc, _TCHAR* argv[])
    {
        char *buf1;
        char * buf2;
        //Lab1
        buf1=(char *)malloc(size);
        printf("buf1:0x%pn",buf1);
        free(buf1);
    
        buf2=(char *)malloc(size);
        printf("buf2:0x%pn",buf2);
    
        memset(buf2,0,size);
        printf("buf2:%dn",*buf2);
    
        printf("====Use Afrer Free====n");
        strncpy(buf1,"hack",5);
        printf("buf2:%snn",buf2);
    
        free(buf2);
        //Lab2
        Base *B=new Base();
        Base *C=new Child();
    
    
    
        getchar();
        return 0;
    }
    

![](https://s2.ax1x.com/2019/11/07/MA1z9S.png)

###  1.1悬挂指针(Dangling pointer)

指向被释放的对象内存的指针。

成因：释放掉后没有将指针重置为null，导致指针依旧可以访问，并且继续指向已经释放的内存.UAF便是调用悬挂指针（多为C++对象），通过对这段内存提前的设计，使得程序调用我们设计好的程序。

案例程序中，为buf1分配了一段32字节的空间，然后将其释放。

但是当使用strncpy对已经释放的buf1拷贝字符串时，发现被free的buf1依然是可以访问的，并且指向的内存没有变化。

![](https://s2.ax1x.com/2019/11/07/MA1XAP.png)

![](https://s2.ax1x.com/2019/11/07/MA1T6H.png)

释放后的buf1依然指向原来的内存，此时的buf1就是一个悬挂指针。

![](https://s2.ax1x.com/2019/11/07/MA1bnA.png)

![](https://s2.ax1x.com/2019/11/07/MA1htK.png)

###  1.2占坑

了解堆分配的占坑机制，需要了解SLUB系统内存分配机制。和SLAB不同，这种利用方法对对象类型没有限制，两个对象只要大小差不多就可以重用同一块内存，也就是说我们释放掉对象A以后马上再申请对象B，只要两者大小相同，那么B就很有可能重用A的内存。

见案例中，释放buf1时，buf1指向0xa35470的内存。而在buf1释放之后，立即分配一个相同大小的内存给buf2指针，发现buf2获取的指针指向的就是buf1被释放的内存地址。

这就是buf2占坑了buf1的内存空间。

此时发散一下思维，buf2可控，而buf1仍然指向buf2的内存空间，是不是就有可能造成程序出现问题。

![](https://s2.ax1x.com/2019/11/07/MA39Xj.png)

![](https://s2.ax1x.com/2019/11/07/MA1htK.png)

![](https://s2.ax1x.com/2019/11/07/MA3VhT.png)

![](https://s2.ax1x.com/2019/11/07/MA3m3F.png)

###  1.3虚函数

C++中的虚函数的作用主要是实现了多态的机制。简而言之就是用父类型别的指针指向其子类的实例，然后通过父类的指针调用实际子类的成员函数。这种技术可以让父类的指针有“多种形态”。代码表现形式就是C++类中Virtaul开头的函数。

同时C++的虚函数是漏洞攻击的重点对象，C++对象中有一个非常重要的结构—虚函数表。

覆盖C++虚函数造成的漏洞利用技术的风靡程度，不亚于经典栈溢出的覆盖手法。更重要的是覆盖虚函数表还可以从本质上绕过GS等内存保护机制，这里不展开说了。

详细的逆向分析，非常推荐《C++反汇编揭秘》这本书，将虚函数的反汇编代码和C++代码进行对比，理解会比较深刻。

![](https://s2.ax1x.com/2019/11/07/MA3Mu9.png)

代码分别实例化了Base和Child为B和C，查看内存结构。

Base对象B的首地址存放_vfptr(虚函数表)，指向三个虚函数f()、g()、 h()

![](https://s2.ax1x.com/2019/11/07/MA33Ax.png)

Child对象C的首地址是对基类（Base）的一个拷贝，值得注意的是Base类里的虚函数表，这里的f()函数被Child重写，g和h函数则依然指向Base实例化时其在虚函数表中的地址。

C的第二个地址则指向自己的虚函数表。

![](https://s2.ax1x.com/2019/11/07/MA3Nge.png)

这些继承关系，可以简单概括为下面三张图。

![](https://s2.ax1x.com/2019/11/07/MA3G4K.png)

![](https://s2.ax1x.com/2019/11/07/MA3wDA.png)

![](https://s2.ax1x.com/2019/11/07/MA3rUP.png)

接下来我们观察代码是如何生成C++虚函数表的。

首先v2=operator new(8u) 对应Base *B=new Base()实例化对象，v2为指向对象的指针。

实例化对象之后，C++会将虚函数表的地址放在对象内存的开头。

![](https://s2.ax1x.com/2019/11/07/MA3ggg.png)

进入sub_411140函数之后经过二次跳转进入sub_4117A0函数

    
    
    text:004117C3                 mov     eax, [ebp+var_8]
    
    .text:004117C6                 mov     dword ptr [eax], offset ??_7Base@@6B@ ; const Base::`vftable'
    

mov操作将虚函数表地址放到[eax]的位置，而此时eax的值就是通过上层函数传递下来的v2的指针。所以这段代码就完成了将虚表放置到对象头部的效果。

这一步骤之后，也就能理解为什么虚函数表会在对象表头，同时这个操作也是我们用来判断C++对象创建的一个非常好的信号，还可以获取这个对象的头部地址和虚表。

![](https://s2.ax1x.com/2019/11/07/MA3fDs.png)

## 通过PWN题掌握UAF

在掌握了基础之后，我们可以拿pwnalbe.kr 的UAF题来快速理解利用原理。

使用scp下载二进制文件和源码（密码:guest）

    
    
    $ scp -P2222 uaf@pwnable.kr:/home/uaf/uaf  /Users/p0kerface/
    
    $ scp -P2222 uaf@pwnable.kr:/home/uaf/uaf.cpp  /Users/p0kerface/
    

主要思路便是利用占坑的方法，向被释放的空间写入数据覆盖vfptr（虚函数表），然后调用悬挂指针完成UAF，这题非常经典值得在做UAF之前的复习。

调试过程中，意识到自己阅读C++的反汇编水平还是不够，类和对象没有源码只看IDA还是非常困难的。所以会把一些逆向的笔记记录下来。

程序源码

    
    
    uaf.cpp
    
    
    
    #include <fcntl.h>
    
    #include <iostream> 
    
    #include <cstring>
    
    #include <cstdlib>
    
    #include <unistd.h>
    
    using namespace std;
    
    
    
    class Human{
    
    private:
    
    ​    virtual void give_shell(){
    
    ​        system("/bin/sh");
    
    ​    }
    
    protected:
    
    ​    int age;
    
    ​    string name;
    
    public:
    
    ​    virtual void introduce(){
    
    ​        cout << "My name is " << name << endl;
    
    ​        cout << "I am " << age << " years old" << endl;
    
    ​    }
    
    };
    
    
    
    class Man: public Human{
    
    public:
    
    ​    Man(string name, int age){
    
    ​        this->name = name;
    
    ​        this->age = age;
    
    ​        }
    
    ​        virtual void introduce(){
    
    ​        Human::introduce();
    
    ​                cout << "I am a nice guy!" << endl;
    
    ​        }
    
    };
    
    
    
    class Woman: public Human{
    
    public:
    
    ​        Woman(string name, int age){
    
    ​                this->name = name;
    
    ​                this->age = age;
    
    ​        }
    
    ​        virtual void introduce(){
    
    ​                Human::introduce();
    
    ​                cout << "I am a cute girl!" << endl;
    
    ​        }
    
    };
    
    
    
    int main(int argc, char* argv[]){
    
    ​    Human* m = new Man("Jack", 25);
    
    ​    Human* w = new Woman("Jill", 21);
    
    
    
    ​    size_t len;
    
    ​    char* data;
    
    ​    unsigned int op;
    
    ​    while(1){
    
    ​        cout << "1. usen2. aftern3. freen";
    
    ​        cin >> op;
    
    
    
    ​        switch(op){
    
    ​            case 1:
    
    ​                m->introduce();
    
    ​                w->introduce();
    
    ​                break;
    
    ​            case 2:
    
    ​                len = atoi(argv[1]);
    
    ​                data = new char[len];
    
    ​                read(open(argv[2], O_RDONLY), data, len);
    
    ​                cout << "your data is allocated" << endl;
    
    ​                break;
    
    ​            case 3:
    
    ​                delete m;
    
    ​                delete w;
    
    ​                break;
    
    ​            default:
    
    ​                break;
    
    ​        }
    
    ​    }
    
    
    
    ​    return 0;    
    
    }
    

###  2.1代码分析

通过IDA反汇编，不过C++的代码已经非常难以看懂了，代码主要分两大块解析。

第一部分是类和子类的定义，定义的父类Human和子类Man和Woman。其中父类包含get_shell函数，虽然子类并没有定义，但是通过继承关系可知，在实例化过程中，虚函数表中函数会包含这个函数。

第二部分就是类的实例化和use after free 三个功能。

接下来我们将程序重要的部分分析一下，以便理解漏洞。

（1）实例化对象

Human* m = new Man(“Jack”, 25);这句在IDA翻译如下，变量v3为实例化Man对象之后的指针。

![](https://s2.ax1x.com/2019/11/07/MA3IU0.png)

找到对应的反汇编，0x400F13这个地方是对象实例化的函数，在call执行结束之后，EBX中便保存这Man对象的指针，即上文中的v3变量。可以通过gdb下断点进行调试。

当实例完对象之后，ebx存放的地址（0x401570），也就是前文中所说的虚函数表vfptr，指向的第一个函数Human继承下来的give_shell。

![](https://s2.ax1x.com/2019/11/07/MA37CT.png)

![](https://s2.ax1x.com/2019/11/07/MA3OKJ.png)

![](https://s2.ax1x.com/2019/11/07/MA3jbR.png)

让我们查看虚表的内存，可以看到Man的虚表中有两个函数。虚表偏移8字节便是introduce函数。

![](https://s2.ax1x.com/2019/11/07/MA8C8O.png)

（2）调用方法

源代码

    
    
    case 1:
    
    ​                m->introduce();
    
    ​                w->introduce();
    
    ​                break;
    

IDA中对应的伪代码

![](https://s2.ax1x.com/2019/11/07/MA8ixe.png)

指针v13和v14分别对应实例化的Man和Woman，Woman的虚函数表的结构与Man是相同的（地址不同），所以不再赘述。

通过观察虚函数表结构，我们已经知道introduce为虚表表头偏移8个字节，所以便有了v13+8字节偏移。

这里就埋下一个伏笔，如果对虚表指针的地址进行改写，将虚表向前偏移8个字节，这样本来调用introduce方法就会调用getshell方法。

对应的反汇编如下，非常建议自己动态调试一遍，能够加深印象。

![](https://s2.ax1x.com/2019/11/07/MA8ZVI.png)

###  2.2UAF利用流程

（1）程序实例化Man和Women

（2）使用Free将Man和Women分别Free （free）

（3）再分配内存，这里我们需要分配24字节，为了占坑。（after）

![](https://s2.ax1x.com/2019/11/07/MA8mIP.png)

因为24字节（0x18）和之前分配的Man和Women一样（上图所示），所以会发生占坑现象，也就是说程序会将之前被释放的Man和Women空间分配给这个指针。此时读取文件（poc）的内容，因为占坑之后内存指针指向的第一个字符就是，覆盖之前Man和Women的虚函数。

Poc的内容就是$ python -c “print ‘x68x15x40x00x00x00x00x00’”> poc

即0x401468=0x401570-8，原虚函数表地址-8字节。

（4）调用Man的悬挂指针，因为虚函数表被我们从poc读入的数据改写，调用intruduce会调用getshell

（5）利用结束

使用UAF修改C++虚表，改变程序流程。

调试过程中，建议下如下的断点，可以让程序停在关键的地方。也可以在调试过程中，多尝试用Ctrl+C呼叫程序暂停，然后设置断点。

    
    
    gdb-peda$ b *0x400f13
    
    Breakpoint 1 at 0x400f13
    
    gdb-peda$ b *0x400fcd
    
    Breakpoint 2 at 0x400fcd
    
    gdb-peda$ b *0x40102d
    
    Breakpoint 3 at 0x40102d
    
    gdb-peda$ b *0x401076
    
    Breakpoint 4 at 0x401076
    

根据如下的操作，我们很容易就获取了shell，注意传递参数poc文件

![](https://s2.ax1x.com/2019/11/07/MA8MRS.png)

![](https://s2.ax1x.com/2019/11/07/MA88qs.png)

## 小结

UAF在浏览器漏洞中多为对C++对象（虚函数）的修改，悬挂指针是UAF利用的关键，调用被Free的函数，如果这个函数的位置已经被别的对象占坑，进行了修改，那么调用悬挂指针就可能能够造成任意代码执行。结合Heap
Spray会产生很好的效果。

![](https://p2.ssl.qhimg.com/t012c03e81bc9250cae.jpg)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Migraine殇** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/190589](/post/id/190589)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Pwn](/tag/Pwn)
  * [二进制](/tag/二进制)
  * [UAF](/tag/UAF)

 **+1** __5赞

 __收藏

![](https://p1.ssl.qhimg.com/t017c97fc7e3becfd42.jpg) Migraine殇

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

