# Glibc-2.23 源码分析——malloc部分下

阅读量 **206854**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-15 10:00:51

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t012c013e0cd2066334.jpg)

## 前言

终于抽出时间对glibc动态内存管理部分源码进行初略的探究，试着从源码和动调来分析free函数执行过程和一些pwn的攻击技巧，分析的不是很全面，有错误的地方望提出指正，共同进步。ps:欢迎白帽子们关注
涂鸦智能安全响应中心

* * *

## Malloc的执行流程

###  情况3：申请mmap

测试代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int main()
    {
        malloc(0x20);
        malloc(0x24000);
        return 0;
    }
    

申请的size 大于 av->top

![](https://p2.ssl.qhimg.com/t015f8ac50a6212c16b.png)

执行调用链: Malloc -> int_malloc -> sysmalloc

![](https://p4.ssl.qhimg.com/t01cde17f4c5a8c4452.png)

Nb = 0x24010 > mp.mmapthreshold 且 (mp.nmmaps < mp.n_mmaps_max，满足条件进入mmap()的调用。

![](https://p3.ssl.qhimg.com/t01092fb68977f29e9a.png)

![](https://p3.ssl.qhimg.com/t010b14b648512ac9b6.png)

计算出满足页对齐的size后调用 MMAP()

![](https://p4.ssl.qhimg.com/t01c01b31655f6dc8c0.png)

申请的size大小为 0x24030 满足页对齐的size是 0x25000

![](https://p4.ssl.qhimg.com/t0197b55c0c2c199bb4.png)

执行后申请到的mmap 空间

![](https://p0.ssl.qhimg.com/t01b7f9829093fb2578.png)

之后对mmap 空间写入 size头,并在标志位上 打上 Mmap标志 0x2

![](https://p5.ssl.qhimg.com/t0114ca31c498c5f154.png)

执行效果

![](https://p0.ssl.qhimg.com/t01e7af8c19039f3591.png)

## calloc执行流程

测试代码

    
    
    #include<stdio.h>
    #include<stdlib.h>
    
    int main(){
        int *p1 = calloc(0x20, 1);
        int *p2 = calloc(0x20, 1);
        free(p1);
        calloc(0x20, 1);
        return 0;
    }
    

###  堆初始化执行流程

**libc_calloc() - > _int_malloc(),和**libc_malloc()一样的堆初始化流程,之后通过malloc_hook跳转
malloc_hook_ini(),与malloc()的区别在于会将申请的堆空间全部置零。

![](https://p0.ssl.qhimg.com/t01b5449a4b206787d1.png)

之后有关main_arena取chunk的申请也是通过int_malloc(),最后都会置空堆空间

![](https://p1.ssl.qhimg.com/t01e220575bb296aeeb.png)

整体上看calloc是一个malloc的调用接口,输出前加上了置空堆空间

## realloc执行流程

测试代码

    
    
    #include<stdio.h>
    #include<stdlib.h>
    
    int main(){
        int *p1 = malloc(0x10);
        int *p2 = malloc(0x10);
        int *p_realloc = realloc(p1, 0x30);
        return 0;
    }
    

realloc调用流程 realloc->realloc_hook_ini(通过 **realloc_hook跳转** )

****

**清空** malloc_hook,__realloc_hook之后跳转 _libc_realloc()执行

![](https://p2.ssl.qhimg.com/t015cc2d531c7a6bd9c.png)

之后进入_int_realloc()  
_int_realloc()函数是一个_int_free()和_int_malloc()的结合体，释放剩余旧堆块，若申请新堆块,则复制堆块内容

![](https://p2.ssl.qhimg.com/t0142862c6d077ce150.png)

先对新申请的堆块与原先堆块进行比对

###  若新申请堆块大于原先堆块

若新申请的size大于原先的size,尝试向top_chunk申请堆块

![](https://p0.ssl.qhimg.com/t018d611fe67650f7ea.png)

新申请堆块的话，需要进行数据复制，将原先堆块的数据拷贝到新申请堆块中

![](https://p2.ssl.qhimg.com/t01f35416d6b2ea7fde.png)

之后释放原先堆块

![](https://p1.ssl.qhimg.com/t01abb0c30f287beb06.png)

###  若新申请堆块小于原先堆块

若新申请的堆块小于原先堆块分割原先堆块,并且位于原先堆块中,释放剩余部分,

![](https://p2.ssl.qhimg.com/t0112ba74addd5c2183.png)

整体来看realloc是个功能丰富的缝合怪属于是。  
realloc可以通过构造制定大小修改,实现free 特定size的remainder_chunk  
realloc(0, size) 可以当做malloc(size)使用

![](https://p2.ssl.qhimg.com/t0135b38788a2cc8267.png)

realloc(chunk_ptr, 0) 可以当做free(chunk_ptr)使用

![](https://p0.ssl.qhimg.com/t0137f9e5932f08d9d3.png)

* * *

本文作者：Jambolt@涂鸦智能安全实验室

漏洞悬赏计划：涂鸦智能安全响应中心（<https://src.tuya.com>) 欢迎白帽子来探索。

招聘内推计划：涵盖安全开发、安全测试、代码审计、安全合规等所有方面的岗位，简历投递[sec@tuya.com](mailto:sec@tuya.com)，请注明来源。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **jambolt** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/253044](/post/id/253044)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [调试分析](/tag/调试分析)
  * [glibc](/tag/glibc)

 **+1** __1赞

 __收藏

![](https://p2.ssl.qhimg.com/t010e9067d13df1f225.png) jambolt

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

