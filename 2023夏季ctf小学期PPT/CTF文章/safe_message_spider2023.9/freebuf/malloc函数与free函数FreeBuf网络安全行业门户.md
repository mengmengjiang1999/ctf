**上一篇简单的讲了一下堆的概述，还有brk和mmap的系统调用，这些都是比较底层的东西。在具体实现上就是malloc函数和free函数了。我们这次来看一下malloc函数和free函数到底干了些什么，开整。**

# 代码演示

    
    
    /* Per thread arena example. */
    #include <stdio.h>
    #include <stdlib.h>
    #include <pthread.h>
    #include <unistd.h>
    #include <sys/types.h>
    void* threadFunc(void* arg) {
            printf("Before malloc in thread 1\n");
            getchar();
            char* addr = (char*) malloc(1000);
            printf("After malloc and before free in thread 1\n");
            getchar();
            free(addr);
            printf("After free in thread 1\n");
            getchar();
    }
    int main() {
            pthread_t t1;
            void* s;
            int ret;
            char* addr;
            printf("Welcome to per thread arena example::%d\n",getpid());
            printf("Before malloc in main thread\n");
            getchar();
            addr = (char*) malloc(1000);
            printf("After malloc and before free in main thread\n");
            getchar();
            free(addr);
            printf("After free in main thread\n");
            getchar();
            ret = pthread_create(&t1, NULL, threadFunc, NULL);
            if(ret)
            {
                    printf("Thread creation error\n");
                    return -1;
            }
            ret = pthread_join(t1, &s);
            if(ret)
            {
                    printf("Thread join error\n");
                    return -1;
            }
            return 0;
    }
    

这里引用的是一位师傅的代码，我还是用的glibc2.21版本，如何改版本之前已经写过了。

# 代码调试

  1. 最开始没有heap segment  
![image.png](https://image.3001.net/images/20210909/1631175769_6139c459d6495b98ad634.png!small)

  2. 当调用了malloc函数之后出现了heap segment![image.png](https://image.3001.net/images/20210909/1631175825_6139c4916f26837eae8fc.png!small)
  3. 然后free掉请求的内存，但是会发现heap segment并不会发生变化(后文会讲到)![image.png](https://image.3001.net/images/20210909/1631175923_6139c4f38f6d0ba34aada.png!small)
  4. 这个程序使用了多线程，然后可以看一下发生了什么![image.png](https://image.3001.net/images/20210909/1631177722_6139cbfa291d8201b59ae.png!small)
  5. 然后新线程使用malloc函数![image.png](https://image.3001.net/images/20210909/1631178256_6139ce1029cec1f4b8459.png!small)
  6. 然后释放掉空间，会发现和主线程一样没有变化![image.png](https://image.3001.net/images/20210909/1631178940_6139d0bce944030c7d894.png!small)

使用malloc到free的全过程。

# 详解

首先在第一个图中，没有调用malloc函数的时候并没有出现heap segment。

而第二幅图出现了heap segment，但是我们会发现我们只申请了1000字节的内存，但是heap
segment给我们返回了21000字节的内存。这片区域就是arena(后面发文章讲arena)

同样的，当释放空间的时候也不会直接将这些空间交还给系统，而是还给堆管理器，所以大家看到的heap segment并没有变化

接下来提升难度。当线程1调用malloc之前，线程1的stack区域就已经被分配好了(多个线程共享进程的资源)，然后调用malloc

新的线程调用malloc的时候，会发现多了两个空间，那两个空间都是分配给新的线程的，但是大家可以看一下线程1调用完malloc以后，其中只有一个空间有读写权限，那才是线程1的arena，是线程1真正可以利用的空间。

同样新线程的释放和主线程一样，也是交还给堆管理器。

**这也就是c语言中malloc调用时底层发生的情况，至于什么是arena，arena做了些什么，我们后面再讲。这篇文章也参考了一些大神的作品，但是我更希望自己写一下，主要还是面向新手，毕竟我是菜鸡**

 **本文参考自[ctfwiki](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/heap-structure/)、[知乎阿里聚安全](https://zhuanlan.zhihu.com/p/24753861)，感谢大佬们**

