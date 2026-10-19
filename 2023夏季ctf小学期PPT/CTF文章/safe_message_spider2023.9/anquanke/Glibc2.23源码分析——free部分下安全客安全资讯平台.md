# Glibc-2.23 源码分析——free部分下

阅读量 **329299**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-18 10:30:51

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t012c013e0cd2066334.jpg)

## 前言

终于抽出时间对glibc动态内存管理部分源码进行初略的探究，试着从源码和动调来分析free函数执行过程和一些pwn的攻击技巧，分析的不是很全面，有错误的地方望提出指正，共同进步。ps:欢迎白帽子们关注
涂鸦智能安全响应中心

* * *

###  Mmap 处理

####  释放mmap空间内存

测试代码

![](https://p0.ssl.qhimg.com/t01e216356addd1dbd6.png)

断点于free

![](https://p1.ssl.qhimg.com/t0144fa405a1d79f44e.png)

__libc_free()中Mmap_free处理代码

![](https://p5.ssl.qhimg.com/t012a9f80b83fcc423d.png)

![](https://p3.ssl.qhimg.com/t013c2bd96aa8396d22.png)

之后进入 mummap_chunk() 释放 mmap区域

![](https://p0.ssl.qhimg.com/t01982f408130eef036.png)

###  malloc_consolidate函数

malloc_consolidate()算是一个特殊的free函数,作用是初识化main_arena->bin或者清空main_arena中的fastbins[]  
源码文本搜索 malloc_consolidate (av) 一共在glibc-2.23/glibc/malloc/malloc.c
>_int_malloc() 中出现了3次

**情况1**

申请smallbin size的堆块,并且当前bin未初始化

![](https://p3.ssl.qhimg.com/t0155a96b04e3037ace.png)

测试代码

![](https://p5.ssl.qhimg.com/t01881a8b91192c6b7b.png)

关键判断逻辑 bin->bk 是否为0

![](https://p2.ssl.qhimg.com/t01583ca73863c7dbf3.png)

之后进入 malloc_consolidate(),malloc_init_state()初始化 main_arena的bin

    
    
        //执行流程
      if (get_max_fast () != 0) {
        .........
      }
      else {
        malloc_init_state(av);
        check_malloc_state(av);
      }
    

执行结果

![](https://p5.ssl.qhimg.com/t01d93626ba1ad24786.png)

**情况2**

申请largebin size的堆块,并且main_arena中的fastbin不为空

![](https://p1.ssl.qhimg.com/t01c7119edb97d9f67a.png)

测试代码

![](https://p1.ssl.qhimg.com/t014c4ff4b8d3f26e62.png)

idx=0x40,have_fastchunks校验通过

![](https://p0.ssl.qhimg.com/t012526b08f32e207bb.png)

进入malloc_consolidate()函数后，在fastbin初始化后get_max_fast()=0x80通过校验

![](https://p3.ssl.qhimg.com/t01f21c8180cebccf7e.png)

clear_fastchunks的作用是将 main_arena 的结构体变量 flag置为1

![](https://p2.ssl.qhimg.com/t01c26d19fe0bc9e3bc.png)

atomic_exchange_acq()清空 main_arena中的fastbin[size]链表

![](https://p5.ssl.qhimg.com/t01775f59487c3fb197.png)

malloc_consolidate函数之后的代码逻辑

![](https://p4.ssl.qhimg.com/t01126f83b7b23936e4.png)

执行效果，之前fastbin[0x20]中的堆块 0x602000被串入unsortedbin

![](https://p0.ssl.qhimg.com/t015ec4e0283bc7f4e5.png)

**情况3**

在有fastbin的前提下，申请的chunk的size大于top_chunk,且申请size的大小属于smallbin

![](https://p3.ssl.qhimg.com/t01d5f330f1dc80ac96.png)

测试代码

![](https://p5.ssl.qhimg.com/t012505528bcd69a91b.png)

调试到malloc_init_state()执行条件判断处,当前满足拥有fastchunks

![](https://p5.ssl.qhimg.com/t01b20edb52ba2e8ba7.png)

进入malloc_consolidate()后清空了 fastbin

**情况4**

_int_free()中出现了1次

![](https://p3.ssl.qhimg.com/t017ac347979fcb4454.png)

分析源码需要满足逻辑 在被释放的chunk的nextchunk是topchunk,且top_chunk size 大于等于
FASTBIN_CONSOLIDATION_THRESHOLD 情况下触发  
测试代码

![](https://p0.ssl.qhimg.com/t01b600722cc8cda43f.png)

进入_int_free函数之后的关键逻辑 nextchunk = chunk_at_offset(free_chunk, size)是否为topchunk

![](https://p3.ssl.qhimg.com/t01df295d9f0779b68d.png)

之后合并free_chunk和topchunk

![](https://p0.ssl.qhimg.com/t0136c1b8c73cd032b4.png)

之后判断当前topchunk_size是否大于FASTBIN_CONSOLIDATION_THRESHOLD且存在fastbin之后执行
malloc_consolidate()  
FASTBIN_CONSOLIDATION_THRESHOLD = 0xffff

![](https://p0.ssl.qhimg.com/t0157b3a01a001a5f04.png)

具体函数内执行情况与情况2相同,遍历fastbin合并放入unsortedbins  
执行结果

![](https://p1.ssl.qhimg.com/t016b4b5fb33fa5bd16.png)

* * *

本文作者：Jambolt@涂鸦智能安全实验室

漏洞悬赏计划：涂鸦智能安全响应中心（<https://src.tuya.com>) 欢迎白帽子来探索。

招聘内推计划：涵盖安全开发、安全测试、代码审计、安全合规等所有方面的岗位，简历投递[sec@tuya.com](mailto:sec@tuya.com)，请注明来源。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **jambolt** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/253049](/post/id/253049)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [调试分析](/tag/调试分析)
  * [glibc](/tag/glibc)

 **+1** __4赞

 __收藏

![](https://p2.ssl.qhimg.com/t010e9067d13df1f225.png) jambolt

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

