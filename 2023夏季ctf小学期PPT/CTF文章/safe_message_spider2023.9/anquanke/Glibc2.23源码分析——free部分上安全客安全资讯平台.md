# Glibc-2.23 源码分析——free部分上

阅读量 **197747**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-17 10:00:32

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t012c013e0cd2066334.jpg)

## 前言

终于抽出时间对glibc动态内存管理部分源码进行初略的探究，试着从源码和动调来分析free函数执行过程和一些pwn的攻击技巧，分析的不是很全面，有错误的地方望提出指正，共同进步。ps:欢迎白帽子们关注
涂鸦智能安全响应中心。

* * *

## Free in fastbin

###  正常情况下的free in fastbin

测试代码

![](https://p2.ssl.qhimg.com/t01bf0ae797ce57e670.png)

Free -> **libc_free,正常进入 free(p1)时,** free_hook为空，修改
**free_hook为onegadget或者其他payload 可以任意执行**

****

**非mmap空间，进入** int_free()

![](https://p1.ssl.qhimg.com/t01ac3d0157fbf889ec.png)

Chunk_size的检查

![](https://p3.ssl.qhimg.com/t01b0fe51bcada7c28c.png)

![](https://p0.ssl.qhimg.com/t018bdece275e2a8070.png)

Chunk_size <= 0x80 进入 fastbin的处理

![](https://p2.ssl.qhimg.com/t01932ed8fe0f60e8b3.png)

对相邻下一块chunk进行size的对齐检查

![](https://p3.ssl.qhimg.com/t01950748c7a81bb444.png)

Fastbin 建立 与串联链表 部分

![](https://p0.ssl.qhimg.com/t015a25729a5b555d7b.png)

![](https://p1.ssl.qhimg.com/t01e261690929fce27b.png)

触发double free 异常

    
    
    free(p1);
    free(p1);
    

此时free_chunk与 old相等 导致报错

![](https://p5.ssl.qhimg.com/t011932f47245d98db3.png)

###  Double free绕过方式

测试代码

![](https://p2.ssl.qhimg.com/t0106c0ffbe7500284f.png)

Double free p1需要先释放另一个满足此fastbin size的堆块，修改old

![](https://p3.ssl.qhimg.com/t014606baced6f76e76.png)

运行结果

![](https://p5.ssl.qhimg.com/t014377c3e5ae01b39d.png)

再次申请一个fastbin size的chunk，修改chunk的fd指针后，完成use after free，控制fastbin的申请区域

###  Use after free

代码

![](https://p4.ssl.qhimg.com/t01af4624423906de78.png)

释放堆块后未对指针置空，并且能修改指针的情况下，可以直接use after free  
运行结果:  
之后第二次的malloc(0x20 ~ 0x2f)的申请 可以请求到构造的fake_chunk地址上。

![](https://p2.ssl.qhimg.com/t019aaaba8b3ede3d07.png)

###  Malloc in fastbin

测试代码

![](https://p2.ssl.qhimg.com/t01234d7c81da644f46.png)

Fastbin 处理代码 位于 **int_malloc()，类似于** int_free()中fastbin处理，是一个相互的逆过程

![](https://p4.ssl.qhimg.com/t017b90f2034539b0e9.png)

fastbins链表结构为 main_arena + 0x10 -> p2 -> p1->0

![](https://p4.ssl.qhimg.com/t01a3041f0dc094247f.png)

对于取出fastbins表头的校验

![](https://p5.ssl.qhimg.com/t01e46414aecdb846d6.png)

之后对fastbin[0x20]表进行替换列表头的操作

![](https://p0.ssl.qhimg.com/t01ef4c59d7c8a13d69.png)

之后对取出chunk的size进行检测(伪造size需要满足size移位之后等于对应的idx,即 若idx=7时fake_size应满足 0x70 ~
0x7f)

![](https://p2.ssl.qhimg.com/t01d184d04b1812bed4.png)

程序运行结果

![](https://p3.ssl.qhimg.com/t011fcbc71ab15fc10f.png)

## Free in unsortedbins

第一次进行free_in_unsortedbin  
测试代码

![](https://p5.ssl.qhimg.com/t01d6d2b1ba3009f6d7.png)

由free() ->
__int_free(),不满足之前对于fastbin的检测后，接着进行下面的逻辑判断，对于top_chunk的保护以及size是否对齐的判断

![](https://p4.ssl.qhimg.com/t0167ed1afc3bea6439.png)

之后进入 unsortedbin 的处理部分(涉及 chunk overlap绕过技巧)

![](https://p4.ssl.qhimg.com/t018320a7e9e91c49b3.png)

之后进入 unsortedbin 的链表处理，此时 fwd == bck，之后进行unsortedbin双链表的串联

![](https://p5.ssl.qhimg.com/t013d1679a344c7deef.png)

此时的链表示意图，为了方便展示将fwd 和 bck分开放置

![](https://p1.ssl.qhimg.com/t0174bec060e0e2046b.png)

###  堆块向前overlapping

测试代码

![](https://p1.ssl.qhimg.com/t0151fc9e6f0be6e3af.png)

通过置空prev_inuse 设置fake prev_size 欺骗unsortedbins的合并堆块机制

![](https://p3.ssl.qhimg.com/t01147680fc8933cc4d.png)

构造合适的prev_size 可以使堆块合并在已经被free的unsortedbin上,吞并未被释放的p2,p3

![](https://p1.ssl.qhimg.com/t01942f759d81ce2596.png)

fake_prev_size = size_p1 + size_p2 + size_p3 = 0xb0 + 0x20 + 0x20 = 0xf0  
之后重写写上size+ prev_size 的chunk头和下一块堆块的prev_size后，完成堆块的吞并

![](https://p0.ssl.qhimg.com/t01a7134962c4831013.png)

之后再申请出制定大小的堆块后，可以用于构造fastbin中的use after free

![](https://p3.ssl.qhimg.com/t010872df85e7b0f522.png)

![](https://p1.ssl.qhimg.com/t011474f4a5a4ebac92.png)

###  Unlink

测试代码  
How2heap/glibc-2.23/unsafe_unlink.c

Unlink触发过程,伪造上一个堆块已被释放

![](https://p2.ssl.qhimg.com/t01243bbe260d131137.png)

unlink函数源代码

![](https://p1.ssl.qhimg.com/t01402fe68eea4d1e3b.png)

构造的堆块

![](https://p0.ssl.qhimg.com/t0169f7c3eb4a3827c1.png)

Gdb没有挂载到unlink函数 直接分析汇编代码对应源码  
p->prev_size 是否为0

![](https://p3.ssl.qhimg.com/t01f21203ee68dcf6d7.png)

builtin_expect (P->fd_nextsize->bk_nextsize != P, 0)

****

builtin_expect (P->bk_nextsize->fd_nextsize != P, 0)

![](https://p4.ssl.qhimg.com/t015bab8da5b91da5f0.png)

之后汇编代码逻辑

![](https://p2.ssl.qhimg.com/t0155cb526223838fa8.png)

目标地址 0x601068(P->fd_nextsize -> bk_nextsize P->bk_nextsize -> fd_nextsize
为同一地址)  
目标地址先被写上 p->bk_nextsize(0x601058)

![](https://p3.ssl.qhimg.com/t01f30c046a5372bc98.png)

接着写上 p->fd_nextsize(0x601050)

![](https://p2.ssl.qhimg.com/t01a16ada0af0195c59.png)

**Unlink构造条件**

1.伪造 被释放堆块的prev_inuse和prev_size  
2.伪造被释放堆块的prev_chunk 的 fd_nextsize 和 bk_nextsize  
3.fd_nextsize = target – 0x18 bk_nextsize = target – 0x10,目标地址target 被写上
fd_nextsize

## Malloc in unsortedbins

正常处理逻辑  
测试代码

![](https://p4.ssl.qhimg.com/t0114d842f3e9d5e749.png)

对 0x128 的unsortedbins 申请 0x100的chunk  
unsortedbin 申请chunk代码段在 _int_malloc()函数中

![](https://p1.ssl.qhimg.com/t0140bbb9bbcc6c88a0.png)

![](https://p0.ssl.qhimg.com/t017b706644f778c133.png)

运行效果:清空unsortedbins的操作为在 main_arena中清空 bins 表

![](https://p1.ssl.qhimg.com/t01310b61a35aaefe8c.png)

之后 通过bck赋值变量fwd

![](https://p1.ssl.qhimg.com/t01f1835e1cd03e2f14.png)

改变申请的堆块的fd和bk指针

![](https://p2.ssl.qhimg.com/t018020483be6f58fab.png)

申请出的chunk被串入双链表

![](https://p5.ssl.qhimg.com/t015d219ccfe2a40c74.png)

之后将申请出的chunk写上正确的size，并将剩余的bin串入 unsortedbins 并且写上size

![](https://p5.ssl.qhimg.com/t01c356680f4bebc661.png)

![](https://p5.ssl.qhimg.com/t01adbae41e5c2776eb.png)

Remainder 堆块的设置

![](https://p4.ssl.qhimg.com/t016486c336b62dfaf5.png)

![](https://p0.ssl.qhimg.com/t0127b421161239ca29.png)

###  House_of_lore

若双链表的bk指针被篡改指向伪造区域，并且在伪造的区域满足fd指针等于victim，申请到的堆地址将可控  
测试代码:  
how2heap/glibc-2.23/house_of_lore.c  
先利用正常情况free一个smallbin进入 unsortedbins

![](https://p1.ssl.qhimg.com/t011e44e610d0054ac4.png)

此时双链表正常，之后篡改 unsortedbin的bk指针

![](https://p4.ssl.qhimg.com/t0146dd80c527aaaf77.png)

之后进入 _int_malloc()的处理的校验逻辑

![](https://p2.ssl.qhimg.com/t01edf30c220aff0fcf.png)

伪造的堆块被串联进入 bin

![](https://p4.ssl.qhimg.com/t019292538f01b2c9ef.png)

再次申请smallbins，申请到了伪造区域

![](https://p2.ssl.qhimg.com/t01b0cb95e298aea4b4.png)

* * *

本文作者：Jambolt@涂鸦智能安全实验室

漏洞悬赏计划：涂鸦智能安全响应中心（<https://src.tuya.com>) 欢迎白帽子来探索。

招聘内推计划：涵盖安全开发、安全测试、代码审计、安全合规等所有方面的岗位，简历投递[sec@tuya.com](mailto:sec@tuya.com)，请注明来源。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **jambolt** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/253042](/post/id/253042)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [调试分析](/tag/调试分析)
  * [glibc](/tag/glibc)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhimg.com/t010e9067d13df1f225.png) jambolt

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

