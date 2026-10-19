**i春秋作家：W1ngs**

**原文来自：[堆入门的必备基础知识](https://bbs.ichunqiu.com/thread-46714-1-1.html?from=beef)**

## 前言

堆的利用相对于栈溢出和格式化字符串会复杂很多，这里对堆的一些基本知识点和实现原理进行了一些小小的总结，写的如有不当恳请大佬们斧正。

## 堆的实现原理

>
> 对堆操作的是由堆管理器来实现的，而不是操作系统内核。因为程序每次申请或者释放堆时都需要进行系统调用，系统调用的开销巨大，当频繁进行堆操作时，就会严重影响程序的性能

例如 glibc 中使用了 ptmalloc2 作为堆管理器：

> 目前 Linux 标准发行版中使用的堆分配器是 glibc 中的堆分配器：ptmalloc2。ptmalloc2 主要是通过 malloc/free
> 函数来分配和释放内存块。

程序向系统申请堆空间的时候相当于一种 "批发" 和 "零售" 的关系：

堆管理器就像一个中间商，将向内核申请到空间根据分配算法来把空间真正的分配给程序。

这里为了理解简单画了一张图，如果有错误的话敬请指正。

![image.png](https://image.3001.net/images/20181012/1539330849_5bc0532126c77.png!small)  

## 0x00 创建、释放堆的函数

    
    
    malloc、realloc、calloc

### malloc 函数：

    
    
    #include <stdlib.h>
    void *malloc(size_t size);

  * 在使用malloc的时候要进行强制类型转换为指针类型

malloc函数申请地址成功后返回一个指针，指向大小为至少size字节的内存块

  * 当size = 0 时，返回当前系统允许的堆的最小内存块  
即malloc(0) 在32位系统下会分配 8 个字节的空间，在 64 位系统下会分配 16 字节的空间

> malloc会使用 mmap 来创建独立的匿名映射段，malloc 的背后是用 brk 函数来实现内存地址申请的。

查看方法：`cat /proc/PID/maps`

  
![image.png](https://image.3001.net/images/20181012/1539330858_5bc0532a19cd3.png!small)  

> 使用 malloc() 申请的内存，释放后，仍然归还回原处，再次申请同样大小的内存区时，还是从第 1 次那里获得

每次申请会获取比申请到更大的值，这样的话，就避免了多次内核态与用户态的切换，提高了程序的效率

> 分配器视堆为一组不同大小的块（chunk）的集合。每个块就是一个连续的虚拟内存片。

### free 函数：

    
    
    #include <stdlib.h>
    void free(void *ptr);

free 函数会释放由 p 所指向的内存块，这个内存块可以是通过malloc或者readlloc函数分配的块。

  * 当 p 为空指针时，函数不执行任何操作，当释放过 p 内存块再次释放后，会产生错误（double free）。

> 当一个堆块释放了（通过调用free函数），它会检查之前的堆块是否被释放了。如果之前的堆块没有在使用，那么就会和当前的堆块合并。

unlink 的源码：

    
    
    /* Take a chunk off a bin list */
    
    void unlink(malloc_chunk *P, malloc_chunk *BK, malloc_chunk *FD)
    
    {
    
        FD = P->fd;
    
        BK = P->bk;
    
        FD->bk = BK;
    
        BK->fd = FD;
    
    }

chunk 合并的过程与双向链表删除节点的过程相同：

![image.png](https://image.3001.net/images/20181012/1539330868_5bc0533473e09.png!small)  

其实这块论坛里有一篇关于 unlink 函数的利用这一块讲的很清楚了，可以参考他的文章：  
<https://bbs.ichunqiu.com/thread-46614-1-1.html>

## 0x01 内存分配有关的函数

    
    
    brk
    sbrk

![image.png](https://image.3001.net/images/20181012/1539330882_5bc05342c6dc7.png!small)  

> 对于每个堆，变量brk指向堆的顶部，不过有下面的两个前提

  * 不开启 ASLR 保护时，brk 会指向 data/bss 段的结尾。
  * 开启 ASLR 保护时，brk 也会指向同一位置，只是这个位置是在 data/bss 段结尾后的随机偏移处。

brk和sbrk主要的工作是实现虚拟内存到内存的映射

  * 当 sbrk() 中的参数为 0 时，我们可以找到 program break 的位置。 也就是 sbrk(0) 时，指针指向的就是program break，也就是堆顶

![image.png](https://image.3001.net/images/20181012/1539330891_5bc0534b4ad96.png!small)  

  * brk 函数和 sbrk 函数通常都配合使用，如下示例：

### 示例：

1.sbrk(0) -- > 初始化堆，将 start_brk 以及堆的当前末尾 brk 指向同一地址

在执行下面的两条语句之后，使用 `cat /proc/PID/maps` 会发现没有堆空间

    
    
    tmp_brk = curr_brk = sbrk(0);
    printf("Program Break Location1:%p\n", curr_brk);

![image.png](https://image.3001.net/images/20181012/1539330900_5bc05354336df.png!small)  

2.brk(curr_brk+4096) -- > 重新定义堆顶的指针

    
    
    brk(curr_brk+4096);
    
    curr_brk = sbrk(0);
    printf("Program break Location2:%p\n", curr_brk);

  
![image.png](https://image.3001.net/images/20181012/1539330907_5bc0535bcfcff.png!small)  

3.此时再调用 sbrk(0)，堆顶指针就会变化

    
    
     brk(tmp_brk);
    
    curr_brk = sbrk(0);
    printf("Program Break Location3:%p\n", curr_brk);

  
![image.png](https://image.3001.net/images/20181012/1539330914_5bc0536255cfa.png!small)  

## 0x02 mmap、munmap函数

> mmap函数要求内核创建一个新的虚拟内存区域

map函数原型：

    
    
    void *mmap(void *start,size_t length,int prot,int flags,int fd,off_t offset)

### prot参数指定虚拟内存区域的访问权限，有以下几个

    
    
    PROT_EXEC    //这个区域由可以被CPU执行的指令组成
    PROT_READ    //可读
    PROT_WRITE   //可写
    PROT_NONE    //不可访问

### flags参数描述被映射对象类型的位组成，有以下几个

    
    
    MAP_ANON或者MAP_ANONYMOUS    //表示被映射的对象是一个匿名对象，相应的虚拟页面是请求二进制零的
    MAP_PRIVATE                 //对象属性为私有、写时复制的
    MAP_SHARED                  //表示共享对象

  * 对于大于 128 KB 的堆申请请求来说，根据分配算法会使用 mmap 函数为她分配一块匿名空间，在这个匿名空间里为用户分配空间。

eg.申请132KB的虚拟内存区域

    
    
    addr = mmap(NULL, (size_t)132*1024, PROT_READ|PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

### mmap 函数与 brk 函数的区别

对于小于 128 KB 的请求来说，会在现有的空间中按照堆分配算法（brk、sbrk）为它分配一个堆空间，大于 128 kB 时，就使用 mmap
函数分配一个匿名空间给用户使用。

简单来说就是两个区别：

1.一个是在现有的堆空间中分配，一个是在设置了 MAP_ANONYMOUS 属性的匿名空间中分配。  
2.一个是用于申请小空间时使用，一个是在用于申请大空间时使用

* * *

### mmap 函数的另一种用法

在栈溢出的利用时，若 system 和 execve 函数都被禁用的时候，我们可以使用 mmap 或者 mprotect 函数将 bss
段的内存权限设置为可执行，这样我们再把 shellcode 写入到里面，接着将 eip 执行他，就可以达到直接执行 shellcode 的效果。

例如，jarvisoj 的 level5：

![image.png](https://image.3001.net/images/20181012/1539330944_5bc05380b732d.png!small)  

WriteUp的链接如下，里面讲到了详细的用法和参数设置。

<https://blog.csdn.net/zszcr/article/details/79703642>

munmap函数原型：

    
    
    int munmap(void *start,size_t length)

eg.删除已经创建的虚拟内存区域

    
    
    ret = munmap(addr, (size_t)132*1024);

### 分配的过程：

  
![image.png](https://image.3001.net/images/20181012/1539330950_5bc05386c9d21.png!small)  

## 0x03 堆的使用场景

  1. new 一个新对象
  2. 传参为数组时

## 0x03 Bin

    
    
    fast bins
    small bins
    large bins
    unsorted bin

### fast bins

用于一些较小的 chunk 释放之后发现存在与之相邻的空闲的 chunk 并将它们进行合并

    
    
    typedef struct malloc_chunk *mfastbinptr;
    
    /*
        This is in malloc_state.
        /* Fastbins */
        mfastbinptr fastbinsY[ NFASTBINS ];
    */

## 参考文章

[Libc堆管理机制及漏洞利用技术 (一）](https://blog.csdn.net/sdulibh/article/details/50443160)

[Heap overflow using unlink](https://sploitfun.wordpress.com/2015/02/26/heap-overflow-using-unlink/)

[ctf-wiki](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/heap/heap_structure/#bin)

[浅析Linux堆溢出之fastbin](http://www.freebuf.com/news/88660.html)

  

# 大家有任何问题可以提问，更多文章可到[i春秋论坛](https://bbs.ichunqiu.com/portal.php?from=beef)阅读哟~

