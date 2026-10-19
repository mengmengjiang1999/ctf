# 概述

unlink是一个宏定义，它的作用是将空闲chunk脱离它当前所在bin。例如当使用malloc的时候可能会从bin中分配堆空间，这时处于free状态的chunk会从bin中脱离然后被堆管理器分配给用户。

先看一下源代码

    
    
    /* Take a chunk off a bin list */
    #define unlink(AV, P, BK, FD) {
        FD = P->fd;
        BK = P->bk;
        if (__builtin_expect (FD->bk != P || BK->fd != P, 0))
          malloc_printerr (check_action, "corrupted double-linked list", P, AV);
        else {
            FD->bk = BK;
            BK->fd = FD;
            if (!in_smallbin_range (P->size)
                && __builtin_expect (P->fd_nextsize != NULL, 0)) {
            if (__builtin_expect (P->fd_nextsize->bk_nextsize != P, 0)
            || __builtin_expect (P->bk_nextsize->fd_nextsize != P, 0))
    
              malloc_printerr (check_action,
                       "corrupted double-linked list (not small)",
                       P, AV);
                if (FD->fd_nextsize == NULL) {
                    if (P->fd_nextsize == P)
                      FD->fd_nextsize = FD->bk_nextsize = FD;
                    else {
                        FD->fd_nextsize = P->fd_nextsize;
                        FD->bk_nextsize = P->bk_nextsize;
                        P->fd_nextsize->bk_nextsize = FD;
                        P->bk_nextsize->fd_nextsize = FD;
                      }
                  } else {
                    P->fd_nextsize->bk_nextsize = P->bk_nextsize;
                    P->bk_nextsize->fd_nextsize = P->fd_nextsize;
                  }
              }
          }
    }
    

# 代码详解

## __builtin_expect函数

__builtin_expect(EXP,N)的意思是EXP==N的概率很大，__builtin_expect(x,0)意思是x的值大概率为假，__builtin_expect(x,1)的意思是x的值大概率为真。这个函数存在的意义就是用来进行代码优化的，使用__builtin_expect((x),1)执行if语句的机会更大，使用__builtin_expect(x,0)执行else语句的机会更大。那么在代码的编译过程中，会将可能性更大的代码紧跟前面的代码。从而减少指令跳转带来的性能上的下降。和if一起使用的时候，重点关注的是x的值，后面的0和1只是为了优化代码

## in_smallbin_range宏

这是一个宏定义，我们直接看代码

    
    
    #define in_smallbin_range(sz)  \
      ((unsigned long) (sz) < (unsigned long) MIN_LARGE_SIZE)
    

我们都知道，x86和x64的标准字长分别为4B和8B。smallbin中的chunk是以公差为两个标准字长排列，，这个宏就是为了告诉我们smallbin的最大的大小。x86不超过512，x64不超过1024

## 代码解读

陌生的函数也就前面一两个，可能还有陌生的函数类似于malloc_printerr函数，但是这个函数能够望文生义，也就是malloc的相关错误信息的输出，我们正式开始解读代码

  1. 首先有一个chunk名为P，而且定义了P的前一chunk和后一chunk

  2. 然后如果前一chunk的bk指针不为P或者后一chunk的fd指针不为P，则输出报错信息(就像站队一样，你前面的后面还应该是你，要不然就出问题了)

  3. 然后后面的else语句才是最主要的，将P的前一chunk的bk指针设置为后一chunk，后一chunk的fd指针指向前一chunk，很明显这已经开始脱离链表了

  4. 后面的有点长，简化一下就是`!in_smallbin_range (P->size)&&P->fd_nextsize != NULL`，意思就是说如果这是一个largechunk(largebin中的chunk)并且P的fd_nextsize不等于NULL，则继续往下执行

  5. 我们先不看后面的语句，直接看else语句，很明显也是和前面一样的，前一个chunk的bk指针直接指向P的后一个chunk，P的后一个chunk直接指向前一个chunk。

  6. 然后再回到原来的地方，就到了`if (__builtin_expect (P->fd_nextsize->bk_nextsize != P, 0)|| __builtin_expect (P->bk_nextsize->fd_nextsize != P, 0))`，依旧是将它简化为`P->fd_nextsize->bk_nextsize != P&&P->bk_nextsize->fd_nextsize != P`，这个也是和上面一样，前面的后面不等于自己，然后进行报错

  7. 继续往下就简单很多，就是看P的前一个largechunk的fd_nextsize指针是否是空，如果是空则再次进入一个条件，看P的fd_nextsize是否为P，如果确实为P，则P的前一chunk的fd_nextsize指针和bk_nextsize指针指向P

  8. 最后执行

    
    
    FD->fd_nextsize = P->fd_nextsize;
                        FD->bk_nextsize = P->bk_nextsize;
                        P->fd_nextsize->bk_nextsize = FD;
                        P->bk_nextsize->fd_nextsize = FD;
    

# 总结

语句是c语言写的，还是比较简单的。关键需要考虑为什么要这样编写，总的来说这还是一个脱链的操作，具体为什么这样写，在理清代码逻辑以后，我们再具体解释

**本文参考自[阿里](https://zhuanlan.zhihu.com/p/24790164)、[堆利用](https://blog.csdn.net/Plus_RE/article/details/79270350)、[相关函数](https://www.jianshu.com/p/23148488014b)，感谢大佬们**

