# Glibc-2.23 源码分析——malloc部分上

阅读量 **214550**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-14 10:30:56

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t012c013e0cd2066334.jpg)

## 前言

终于抽出时间对glibc动态内存管理部分源码进行初略的探究，试着从源码和动调来分析free函数执行过程和一些pwn的攻击技巧，分析的不是很全面，有错误的地方望提出指正，共同进步。ps:欢迎白帽子们关注
涂鸦智能安全响应中心

* * *

## 相关结构体

###  Chunk的结构体 malloc_chunk

![](https://p0.ssl.qhimg.com/t011d946fbb91d173c1.png)

对于inuse的chunk 只有malloc_chunk.size是生效的，fd，bk指针对于free
chunk生效，fd_nextsize，bk_nextsize对于largebins生效。

###  Malloc_par 结构体

![](https://p1.ssl.qhimg.com/t016819ecd1f86491c1.png)

与sbrk 与 mmap的申请与释放相关结构体，源码中变量 mp_.

###  64bits 下chunk的内存布局结构

**Allocated chunk**

结构示意图

![](https://p2.ssl.qhimg.com/t019a05a78cdaffecc4.png)

**标志位**

标志位判定代码

![](https://p4.ssl.qhimg.com/t012d1d0f8ebcfdc723.png)

    
    
    P   0b0001
    M   0b0010
    A   0b0100
    

**Free chunk**

结构示意图

![](https://p5.ssl.qhimg.com/t013ac0e52da26bcb3e.png)

**标志位**

P: 标志前一个chunk是否在使用中，配合 size_of_previous_chunk使用进行合并堆块。  
P=0 前一个堆块并未被alloc,prev_size生效  
P=1 前一个堆块在使用中

**相关指针**

    
    
    offset            name
    0x10-0x17        *fd                指向bins中的下一个bin
    0x11-0x1f        *bk                指向bins中的上一个bin
    Freechunk是Largebin 的情况下
    0x20-0x27        *fd_nextsize        指向下一个largebin.size
    0x28-0x2f        *bk_nextsize        指向上一个largebin.size
    

## 动态内存申请执行流程

###  hook跳转的定义部分

![](https://p2.ssl.qhimg.com/t0104f6b1b8044c0749.png)

###  Malloc的执行流程

**hook的获取与调用**

获取 **malloc_hook的值，只要值不为空，跳转**
malloc_hook的值进行函数执行(修改__malloc_hook为onegadget或其他执行流的执行点)

![](https://p5.ssl.qhimg.com/t01f3fe970662476756.png)

![](https://p3.ssl.qhimg.com/t012751bfd9569ca745.png)

Hook取值 malloc_hook_ini 后跳转执行

![](https://p1.ssl.qhimg.com/t01c589f48aa5be4e2f.png)

**情况1：未有topchunk时申请chunk**

在调用 **malloc_hook后hooks.c malloc_hook_ini()执行**

****

**清空** malloc_hook 之后调用 arena.c>ptmalloc_init()  
返回后在进入__libc_malloc()接着调用 _int_malloc()

**_int_malloc()中的处理逻辑**

1.对可用arenas进行检索

![](https://p3.ssl.qhimg.com/t013e34c0b939978b9d.png)

2.对fastbin进行申请堆块大小的检索

![](https://p4.ssl.qhimg.com/t014819fee18b944eab.png)

![](https://p1.ssl.qhimg.com/t016912720d66ce06ba.png)

此时 getmax_fast为0 跳过检索

__

3.对smallbins进行检索

__

Victim == 0 进入执行 malloc_consolidate()  
在malloc_consolidate()中不满足检索条件 进入 malloc_init_state()执行进行堆空间的初始化

__

__

4.初始化top过程

__

av->top赋值

__

5.sysmalloc 初始化 heap区域

之后跳回__int_malloc()中,当前未有heap空间且未初始化堆，进入sysmalloc()

![](https://p5.ssl.qhimg.com/t01aca41a7cb187c588.png)

使用 sbrk()从系统 中分配 size 大小的虚拟内存块,第一次申请0x20 的chunk，sysmalloc()会指向申请一个topchunk
0x1000

![](https://p3.ssl.qhimg.com/t0180e81fa5b8fa6f1e.png)

申请完brk后 将brk地址挂载入 struct malloc_par mp.sbrkbase

![](https://p4.ssl.qhimg.com/t01a21c000a3bd93c72.png)

挂在后的程序内存分布以及 mp结构体查看

![](https://p2.ssl.qhimg.com/t0134089c29044ab7d9.png)

之后对申请的空间设置chunk头,先设置申请大小的空间并且设置inuse位, 0x21001

![](https://p3.ssl.qhimg.com/t016714e1e99843fbf3.png)

6.计算申请chunk大小，对heap进行分割

![](https://p2.ssl.qhimg.com/t01b1caf25899e9e247.png)

申请出的区域先写上申请到的chunk_size

![](https://p3.ssl.qhimg.com/t01bef566d638606135.png)

之后再写上top_chunk的chunk_size

![](https://p3.ssl.qhimg.com/t012bc3b936a76a1c60.png)

初始化申请堆空间调用执行顺序为  
 **malloc_hook - > malloc_hook_ini -> **libc_malloc -> _int_malloc ->
sysmalloc() -> brk

**情况2：已有 topchunk时申请小size的chunk**

初始化堆块后__malloc_hook == 0,直接进入 _int_malloc 执行

![](https://p5.ssl.qhimg.com/t016e79e6f4e2a61046.png)

1.对av(main_arena)校验是否存在，进入之后对bins检索需要申请的空间大小

![](https://p4.ssl.qhimg.com/t0133b2c3450b0c23ed.png)

2.Fastbins 检索

![](https://p5.ssl.qhimg.com/t0180e03716fb192377.png)

3.unsortedbins 检索

![](https://p0.ssl.qhimg.com/t01f795dcccb11314f7.png)

4.use_top_chunk  
之后进入 use_top 分割topchunk

![](https://p1.ssl.qhimg.com/t01cb8287a4c8493349.png)

通过set_head函数 同上一节写入 chunk_size的方式分别写入 new_chunk 和 topchunk头

![](https://p5.ssl.qhimg.com/t01281f7a84e6d0c999.png)

![](https://p2.ssl.qhimg.com/t01c29041a0b00e62fa.png)

* * *

本文作者：Jambolt@涂鸦智能安全实验室

漏洞悬赏计划：涂鸦智能安全响应中心（<https://src.tuya.com>) 欢迎白帽子来探索。

招聘内推计划：涵盖安全开发、安全测试、代码审计、安全合规等所有方面的岗位，简历投递[sec@tuya.com](mailto:sec@tuya.com)，请注明来源。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **jambolt** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/253043](/post/id/253043)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [调试分析](/tag/调试分析)
  * [glibc](/tag/glibc)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhimg.com/t010e9067d13df1f225.png) jambolt

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

