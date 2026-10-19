# 羊城杯2021-EasyVM

阅读量 **422110**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-02 10:00:03

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t011aedd5e3ceea9686.jpg)

## 1.初次分析

IDA打开：

![](https://p0.ssl.qhimg.com/t01bd7aa527c9952fa2.png)

![](https://p0.ssl.qhimg.com/t017d2b05556903fd8b.png)

看到这种情况，大致可以确实代码会在运行的自修改。  
代码自修改函数

![](https://p3.ssl.qhimg.com/t01f8e5e5b937e93ab0.png)

![](https://p5.ssl.qhimg.com/t01019f913a1ca8ac51.png)

这里大致有2种方法来得到解密后的代码，一个是动态运行后dump下来，一个是根据自修改函数写idapython来修改，我这里选择的是dump（懒狗是这样的）。

## 2.动态调试dump代码

未修改前：

![](https://p5.ssl.qhimg.com/t01c1e307fde0d22974.png)

修改后：

![](https://p1.ssl.qhimg.com/t01ddfd14ac9b2f41af.png)

可以看到第一个机器码从0x86变为0x55，而0x55的汇编是push ebp。  
通过IDA分析此函数的地址范围是0x80487A8~0x8048F44。  
输入命令 **dump memory 保存路径 0x80487a8 0x8048f44** dump下代码。

## 3.分析dump代码

利用idapython修改分析机器码  
修改前

![](https://p2.ssl.qhimg.com/t0134f1caddfff572b4.png)

修改后

![](https://p0.ssl.qhimg.com/t015d205e1e7a3c1d36.png)

![](https://p0.ssl.qhimg.com/t01d1ef4a84a9ac0893.png)

可以看到虚拟机的op_code的对应操作。

## 4.虚拟机分析

虚拟机初始化

![](https://p3.ssl.qhimg.com/t0185b0a2a095dab9d6.png)

![](https://p4.ssl.qhimg.com/t017e7563fecb9e72f0.png)

为了后面更好的分析虚拟机的操作，这里定义一些寄存器。  
v1[1]:rax; v1[2]:rbx; v1[3]:rdx; v1[4]:rex; v1[5]:rfx; v1[9]:rcx;

首先确定运行时会用到的指令，利用IDApython。这里代码贴一部分。

![](https://p0.ssl.qhimg.com/t0140cefbebce6718e7.png)

然后根据指令来分析相应的汇编。(no表示不会用到)

![](https://p3.ssl.qhimg.com/t013e11f6f4fd131012.png)

![](https://p3.ssl.qhimg.com/t0195e049f66c871b6d.png)

![](https://p0.ssl.qhimg.com/t0112de315d747d184e.png)

![](https://p5.ssl.qhimg.com/t01558895a491fecdfa.png)

![](https://p5.ssl.qhimg.com/t01cccee2cfe5b00cee.png)

![](https://p0.ssl.qhimg.com/t01e809d018d54bbd0e.png)

洗出汇编代码

**part1(input[0x0~0x1f])**

read input  
mov rax,input[0x0]  
mov rcx,0x7B  
xor rax,rcx  
cmp 0x4a,rax  
mov rax,input[0x1]  
mov rcx,0x2F  
xor rax,rcx  
cmp 0x19,rax  
mov rax,input[0x2]  
mov rcx,0xE8  
xor rax,rcx  
cmp 0xdd,rax  
mov rax,input[0x3]  
mov rcx,0x37  
xor rax,rcx  
cmp 0xf,rax  
mov rax,input[0x4]  
mov rcx,0x2F  
xor rax,rcx  
cmp 0x1b,rax  
mov rax,input[0x5]  
mov rcx,0xE8  
xor rax,rcx  
cmp 0x89,rax  
mov rax,input[0x6]  
mov rcx,0x7B  
xor rax,rcx  
cmp 0x19,rax  
mov rax,input[0x7]  
mov rcx,0x37  
xor rax,rcx  
cmp 0x54,rax  
mov rax,input[0x8]  
mov rcx,0x7B  
xor rax,rcx  
cmp 0x4f,rax  
mov rax,input[0x9]  
mov rcx,0x7B  
xor rax,rcx  
cmp 0x4e,rax  
mov rax,input[0xa]  
mov rcx,0x37  
xor rax,rcx  
cmp 0x55,rax  
mov rax,input[0xb]  
mov rcx,0x37  
xor rax,rcx  
cmp 0x56,rax  
mov rax,input[0xc]  
mov rcx,0xE8  
xor rax,rcx  
cmp 0x8e,rax  
mov rax,input[0xd]  
mov rcx,0x2F  
xor rax,rcx  
cmp 0x49,rax  
mov rax,input[0xe]  
mov rcx,0x37  
xor rax,rcx  
cmp 0xe,rax  
mov rax,input[0xf]  
mov rcx,0x7B  
xor rax,rcx  
cmp 0x4b,rax  
mov rax,input[0x10]  
mov rcx,0x37  
xor rax,rcx  
cmp 0x6,rax  
mov rax,input[0x11]  
mov rcx,0x37  
xor rax,rcx  
cmp 0x54,rax  
mov rax,input[0x12]  
mov rcx,0x2F  
xor rax,rcx  
cmp 0x1a,rax  
mov rax,input[0x13]  
mov rcx,0x7B  
xor rax,rcx  
cmp 0x42,rax  
mov rax,input[0x14]  
mov rcx,0x37  
xor rax,rcx  
cmp 0x53,rax  
mov rax,input[0x15]  
mov rcx,0x7B  
xor rax,rcx  
cmp 0x1f,rax  
mov rax,input[0x16]  
mov rcx,0x37  
xor rax,rcx  
cmp 0x52,rax  
mov rax,input[0x17]  
mov rcx,0xE8  
xor rax,rcx  
cmp 0xdb,rax  
mov rax,input[0x18]  
mov rcx,0x7B  
xor rax,rcx  
cmp 0x19,rax  
mov rax,input[0x19]  
mov rcx,0xE8  
xor rax,rcx  
cmp 0xd9,rax  
mov rax,input[0x1a]  
mov rcx,0x7B  
xor rax,rcx  
cmp 0x19,rax  
mov rax,input[0x1b]  
mov rcx,0x37  
xor rax,rcx  
cmp 0x55,rax  
mov rax,input[0x1c]  
mov rcx,0x2F  
xor rax,rcx  
cmp 0x19,rax  
mov rax,input[0x1d]  
mov rcx,0x37  
xor rax,rcx  
cmp 0x0,rax  
mov rax,input[0x1e]  
mov rcx,0x7B  
xor rax,rcx  
cmp 0x4b,rax  
mov rax,input[0x1f]  
mov rcx,0x2F  
xor rax,rcx  
cmp 0x1e,rax

**part2(input[0x20~0x23])**

mov rax,input[0x20]  
mov rbx,0x18  
shl rax,rbx  
mov rcx,rax  
mov rax,input[0x21]  
mov rbx,0x10  
shl rax,rbx  
add rcx,rax  
mov rax,input[0x22]  
mov rbx,0x8  
shl rax,rbx  
add rcx,rax  
mov rax,input[0x23]  
add rcx,rax  
mov rax,rcx  
mov rbx,0x5  
shr rax,rbx  
xor rax,rcx  
mov rcx,rax  
mov rbx,0x7  
shl rax,rbx  
mov rbx,0x98f17723  
and rax,rbx  
xor rax,rcx  
mov rcx,rax  
mov rbx,0x18  
shl rax,rbx  
mov rbx,0x35e4b920  
and rax,rbx  
xor rax,rcx  
mov rcx,rax  
mov rbx,0x12  
shr rax,rbx  
xor rax,rcx  
cmp rax,0x6febf967

**part3(input[0x24~0x27],input[0x28~0x2b])**

mov rax,input[0x24]  
mov rbx,0x18  
shl rax,rbx  
mov rcx,rax  
mov rax,input[0x25]  
mov rbx,0x10  
shl rax,rbx  
add rcx,rax  
mov rax,input[0x26]  
mov rbx,0x8  
shl rax,rbx  
add rcx,rax  
mov rax,input[0x27]  
add rcx,rax  
mov rax,rcx  
mov rdx,0x20  
mul rax,rdx  
mov rex,rax  
xor rax,rcx  
mov rbx,0x11  
shr rax,rbx  
mov rfx,rax  
mov rax,rfx  
xor rax,rex  
xor rax,rcx  
mov rbx,0xd  
shl rax,rbx  
xor rax,rcx  
xor rax,rex  
xor rax,rfx  
mov rcx,rax  
mov rdx,0x20  
mul rax,rdx  
mov rex,rax  
xor rax,rcx  
mov rbx,0x11  
shr rax,rbx  
mov rfx,rax  
mov rax,rfx  
xor rax,rex  
xor rax,rcx  
mov rbx,0xd  
shl rax,rbx  
xor rax,rcx  
xor rax,rex  
xor rax,rfx  
cmp 0xCF1304DC,rax  
mov rax,input[0x28]  
mov rbx,0x18  
shl rax,rbx  
mov rcx,rax  
mov rax,input[0x29]  
mov rbx,0x10  
shl rax,rbx  
add rcx,rax  
mov rax,input[0x2a]  
mov rbx,0x8  
shl rax,rbx  
add rcx,rax  
mov rax,input[0x2b]  
add rcx,rax  
mov rax,rcx  
mov rdx,0x20  
mul rax,rdx  
mov rex,rax  
xor rax,rcx  
mov rbx,0x11  
shr rax,rbx  
mov rfx,rax  
mov rax,rfx  
xor rax,rex  
xor rax,rcx  
mov rbx,0xd  
shl rax,rbx  
xor rax,rcx  
xor rax,rex  
xor rax,rfx  
mov rcx,rax  
mov rdx,0x20  
mul rax,rdx  
mov rex,rax  
xor rax,rcx  
mov rbx,0x11  
shr rax,rbx  
mov rfx,rax  
mov rax,rfx  
xor rax,rex  
xor rax,rcx  
mov rbx,0xd  
shl rax,rbx  
xor rax,rcx  
xor rax,rex  
xor rax,rfx  
cmp 0x283B8E84,rax  
end

把汇编翻译成高级语言

![](https://p2.ssl.qhimg.com/t0139e49736df4311f4.png)

根据翻译出的代码来逆出正确输入。  
input[0x0~0x1f]简单异或一下可以得到结果。  
input[0x20~0x23]

![](https://p0.ssl.qhimg.com/t01cc04bb26e141cc07.png)

input[0x24~0x27]  
此处的逻辑为：  
b^(b<<0xd)=cmp_data

a^(a>>0x11)=b

input^(input<<0x5)=a  
利用python的z3求解来解决

![](https://p2.ssl.qhimg.com/t01ca7a8269cf2d790f.png)

![](https://p3.ssl.qhimg.com/t012007d4324cb5eee9.png)

最后求出字符串为：16584abc45baff901c59dde3b1bb6701a254b06cdc23

**第一次连续花12个小时来做一道题，又苦又快乐了属于是。**

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **fake_haha** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/253057](/post/id/253057)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __3赞

 __收藏

![](https://p3.ssl.qhimg.com/t010857340ce46bb672.jpg) fake_haha

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

