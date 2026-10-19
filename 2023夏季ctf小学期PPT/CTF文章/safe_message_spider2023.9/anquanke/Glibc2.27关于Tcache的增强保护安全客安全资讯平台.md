# Glibc 2.27关于Tcache的增强保护

阅读量 **372014**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-10-23 14:00:00

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01ecc36a06cafbb3f5.jpg)

## 0x01 前言

在2020年09月10日，`Ubuntu`基金会发布了名为为`2.27-3ubuntu1.3`的更新，本次更新进行了对于`Tcache`分配机制的更新，这将导致一批对于`Tcache`的利用失效，本文从源码的角度分析了变动的源码与保护。

## 0x02 获取源码

由于此软件包目前还处于测试状态(`proposed`)，我们无法使用`apt-get update && apt-get upgrade`直接获取到此版本。

运行以下命令启用获取测试状态软件包源码：

    
    
    sudo echo 'deb http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
    ' >> /etc/apt/sources.list
    sudo echo 'deb-src http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
    ' >> /etc/apt/sources.list
    

接下来运行`sudo apt-get update`更新软件源

![](https://p1.ssl.qhimg.com/t0118afa629f5ce0ef4.png)

🚫：更新完软件源后，严禁直接使用`sudo apt-get
upgrade`更新软件，部分测试版核心软件(例如`glibc`)一旦被更新到测试版将无法进行降级。

接下来运行`sudo apt-get source libc6/bionic-proposed`以获取目标源码

![](https://p4.ssl.qhimg.com/t016137c2a4f81f8e0c.png)

⚠️：接下来请编辑`/etc/apt/sources.list`，注释掉刚刚添加的源，并运行`sudo apt-get update`更新软件源

![](https://p3.ssl.qhimg.com/t018f81028fdc8779d1.png)

## 0x03 代码变更

### 1.`Tcache`结构体定义变更

原始定义：

    
    
    /* We overlay this structure on the user-data portion of a chunk when
       the chunk is stored in the per-thread cache.  */
    typedef struct tcache_entry
    {
      struct tcache_entry *next;
    } tcache_entry;
    

新定义：

    
    
    /* We overlay this structure on the user-data portion of a chunk when
       the chunk is stored in the per-thread cache.  */
    typedef struct tcache_entry
    {
      struct tcache_entry *next;
      /* This field exists to detect double frees.  */
      struct tcache_perthread_struct *key;
    } tcache_entry;
    

意义：

加入了额外指针`key`，可以用来检查链表完整性。

### 2.加入`Tcache`数量限制

原始定义：

无

新定义：

    
    
    #define MAX_TCACHE_COUNT 127    /* Maximum value of counts[] entries.  */
    

意义：

限制`Tcache`的数量

### 3.`tcache_put`加入了新步骤

原始定义：

    
    
    /* Caller must ensure that we know tc_idx is valid and there's room
       for more chunks.  */
    static __always_inline void tcache_put (mchunkptr chunk, size_t tc_idx)
    {
      tcache_entry *e = (tcache_entry *) chunk2mem (chunk);
      assert (tc_idx < TCACHE_MAX_BINS);
      e->next = tcache->entries[tc_idx];
      tcache->entries[tc_idx] = e;
      ++(tcache->counts[tc_idx]);
    }
    

新定义：

    
    
    /* Caller must ensure that we know tc_idx is valid and there's room
       for more chunks.  */
    static __always_inline void tcache_put (mchunkptr chunk, size_t tc_idx)
    {
      tcache_entry *e = (tcache_entry *) chunk2mem (chunk);
      assert (tc_idx < TCACHE_MAX_BINS);
    
      /* Mark this chunk as "in the tcache" so the test in _int_free will
         detect a double free.  */
      e->key = tcache;
    
      e->next = tcache->entries[tc_idx];
      tcache->entries[tc_idx] = e;
      ++(tcache->counts[tc_idx]);
    }
    

意义：

现在，将`chunk`置入`Tcache`中时，将会新增一个指针指向`Tcache`，用于检查`Double Free`。

### 4.`tcache_get`加入了新步骤

原始定义：

    
    
    /* Caller must ensure that we know tc_idx is valid and there's
       available chunks to remove.  */
    static __always_inline void *
    tcache_get (size_t tc_idx)
    {
      tcache_entry *e = tcache->entries[tc_idx];
      assert (tc_idx < TCACHE_MAX_BINS);
      assert (tcache->entries[tc_idx] > 0);
      tcache->entries[tc_idx] = e->next;
      --(tcache->counts[tc_idx]);
      return (void *) e;
    }
    

新定义：

    
    
    /* Caller must ensure that we know tc_idx is valid and there's
       available chunks to remove.  */
    static __always_inline void *
    tcache_get (size_t tc_idx)
    {
      tcache_entry *e = tcache->entries[tc_idx];
      assert (tc_idx < TCACHE_MAX_BINS);
      assert (tcache->entries[tc_idx] > 0);
      tcache->entries[tc_idx] = e->next;
      --(tcache->counts[tc_idx]);
      e->key = NULL;
      return (void *) e;
    }
    

意义：

现在，将`chunk`从`Tcache`中移除时，将会清空新增的指针。

### 5.`int_free`中加入了新检查

原始定义：

    
    
    #if USE_TCACHE
      {
        size_t tc_idx = csize2tidx (size);
    
        if (tcache
        && tc_idx < mp_.tcache_bins
        && tcache->counts[tc_idx] < mp_.tcache_count)
          {
        tcache_put (p, tc_idx);
        return;
          }
      }
    #endif
    

新定义：

    
    
    #if USE_TCACHE
      {
        size_t tc_idx = csize2tidx (size);
        if (tcache != NULL && tc_idx < mp_.tcache_bins)
          {
            /* Check to see if it's already in the tcache.  */
            tcache_entry *e = (tcache_entry *) chunk2mem (p);
    
            /* This test succeeds on double free.  However, we don't 100%
               trust it (it also matches random payload data at a 1 in
               2^<size_t> chance), so verify it's not an unlikely
               coincidence before aborting.  */
            if (__glibc_unlikely (e->key == tcache))
              {
                tcache_entry *tmp;
                LIBC_PROBE (memory_tcache_double_free, 2, e, tc_idx);
                for (tmp = tcache->entries[tc_idx]; tmp; tmp = tmp->next)
                  if (tmp == e)
                    malloc_printerr ("free(): double free detected in tcache 2");
                    /* If we get here, it was a coincidence.  We've wasted a
                       few cycles, but don't abort.  */
              }
    
            if (tcache->counts[tc_idx] < mp_.tcache_count)
              {
                tcache_put (p, tc_idx);
                return;
              }
          }
      }
    #endif
    

意义：

现在，调用`int_free`时，将会检查整个`Tcache`链表，如果发现将要释放的`chunk`已存在于链表中将会报错`free(): double
free detected in tcache 2`。

### 6.`_int_realloc`中更改了定义

原始定义：

    
    
    void*
    _int_realloc(mstate av, mchunkptr oldp, INTERNAL_SIZE_T oldsize,
             INTERNAL_SIZE_T nb)
    {
      .........
    
      unsigned long    copysize;        /* bytes to copy */
      unsigned int     ncopies;         /* INTERNAL_SIZE_T words to copy */
      INTERNAL_SIZE_T* s;               /* copy source */
      INTERNAL_SIZE_T* d;               /* copy destination */
    
      .........
                {
                  /*
                     Unroll copy of <= 36 bytes (72 if 8byte sizes)
                     We know that contents have an odd number of
                     INTERNAL_SIZE_T-sized words; minimally 3.
                   */
    
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
    
    .........
    }
    

新定义：

    
    
    void* _int_realloc(mstate av, mchunkptr oldp, INTERNAL_SIZE_T oldsize,
             INTERNAL_SIZE_T nb)
    {
    .........
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
                    memcpy (newmem, chunk2mem (oldp), oldsize - SIZE_SZ);
                  _int_free (av, oldp, 1);
                  check_inuse_chunk (av, newp);
                  return chunk2mem (newp);
                }
            }
        }
    
    .........
    }
    

意义：

此处由原来的逐位复制直接变更为使用`memcpy`，实现上更加简洁。

### 7.`do_set_tcache_count`发生了变更

原始定义：

    
    
    static inline int __always_inline do_set_tcache_count (size_t value)
    {
      LIBC_PROBE (memory_tunable_tcache_count, 2, value, mp_.tcache_count);
      mp_.tcache_count = value;
      return 1;
    }
    

新定义：

    
    
    static inline int __always_inline do_set_tcache_count (size_t value)
    {
      if (value <= MAX_TCACHE_COUNT)
        {
          LIBC_PROBE (memory_tunable_tcache_count, 2, value, mp_.tcache_count);
          mp_.tcache_count = value;
        }
      return 1;
    }
    

意义：

限制`tcache_count`的数目必须小于`MAX_TCACHE_COUNT`(即`127`)，防止发生溢出。

## 0x04 变化总结

以上几大变化基本上都是针对的`Tcache`进行的更新，且更新后的代码基本`100%`照搬`Glibc
2.31`的代码，因此我们可以直接利用`2.31`的思路，直接篡改`key`指针就可以完成利用了。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ERROR404** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/219292](/post/id/219292)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Tcache](/tag/Tcache)
  * [Glibc 2.27](/tag/Glibc 2.27)

 **+1** __3赞

 __收藏

![](https://p5.ssl.qhimg.com/t01fc6ae8fa56997fe6.jpg) ERROR404

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

