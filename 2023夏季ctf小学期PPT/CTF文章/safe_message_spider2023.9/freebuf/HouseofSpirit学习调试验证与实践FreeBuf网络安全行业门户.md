作家：[Bug制造机](https://bbs.ichunqiu.com/thread-43678-1-1.html?from=beef)  

原文来自：[House of
Spirit学习调试验证与实践](https://bbs.ichunqiu.com/thread-43678-1-1.html?from=beef)

House of
Spirit和其他的堆的利用手段有所不同。它是将存在的指针改写指向我们伪造的块（这个块可以位于堆、栈、bss任何一个位置）并且free掉欺骗glibc达到把伪造块回收到bins中不过在free之前，需要设置当前伪造块和下一个伪造块的size字段，满足free()的安全检测机制，从而欺骗glibc。  
下面是一个demo小程序先感性的体会下：

    
    
    #include<stdio.h>
    #include<stdlib.h>
    struct fast_chunk
    {
    size_t pre_size;
    size_t size;
    struct fast_chunk *fd;
    struct fast_chunk *bk;
    char buf[0x20];
    };
    
    int main(void)
    {
    struct fast_chunk fake_chunks[2];
    void *ptr,*victim;
    ptr=malloc(0x30);
    fake_chunks[0].size=sizeof(struct fast_chunk);
    fake_chunks[1].size=sizeof(struct fast_chunk);
    ptr=(void *)&fake_chunks[0].fd;
    free(ptr);
    victim=malloc(0x30);
    }
    

### 调试验证

申请两块fake_chunk。  
![image.png](https://image.3001.net/images/20180807/1533627144_5b694b087904e.png!small)![image.png](https://image.3001.net/images/20180807/1533627153_5b694b115218a.png!small)  

所以:

&fake_chunks[0]=0x7fffffffdda0  
&fake_chunks[1]=0x7fffffffdde0

为绕过安全监测机制，设置好当前块和下一块的size字段  
![image.png](https://image.3001.net/images/20180807/1533627159_5b694b1781457.png!small)  

![image.png](https://image.3001.net/images/20180807/1533627168_5b694b2069617.png!small)改写一个指针指向伪造的块![image.png](https://image.3001.net/images/20180807/1533627175_5b694b27c90e0.png!small)![image.png](https://image.3001.net/images/20180807/1533627180_5b694b2c0fcb2.png!small)  

因为是fd的地址，所以是：0x7fffffffddb0

free之后,伪造的块已经加入到了fastbin的链表中去了

  
![image.png](https://image.3001.net/images/20180807/1533627195_5b694b3bdfd7f.png!small)此时再申请和伪造的块大小一样的块![image.png](https://image.3001.net/images/20180807/1533627209_5b694b4915a4b.png!small)  

返回了和之前free的伪造块一样的块。

至于地址为什么是&fake_chunks[0]+0x10是因为返回的可用memory就是位于pre_size和size字段之后。这个和chunk的结构有关

## 为什么当前构造块和下一个构造块要填充size字段？

分析下free的源码就知道了：

    
    
    void 
    public_fRE(Void_t* mem)
    {
        mstate ar_ptr;
        mchunkptr p; // mem相应的chunk
        ...
        p = mem2chunk(mem);    //将 mem转换为chunk地址
        if (chunk_is_mmapped(p))   //检查chunk的mmp位
        {
            munmap_chunk(p);       //用unmmap的方式直接取消映射
            return;
        }
        ...
        ar_ptr = arena_for_chunk(p);  //找到chunk对应的area
        ...
        _int_free(ar_ptr, mem);       //调用init_free（）函数进入正常的free块并检测以及回收的流程
    }

为了让伪造的块进入到正常的free流程，所以要使得构造的当前chunk的size字段的mmp对应位是0就行了。

接下来是_init_free函数：

    
    
    void _int_free(mstate av, Void_t* mem)
    {
        mchunkptr p; // mem相应的chunk
        INTERNAL_SIZE_T size; //size，大小
        mfastbinptr* fb; //联系fast bin
        ...
        p = mem2chunk(mem);   //memory转换为chunk
        size = chunksize(p);   //获得chunksize
        ...
        if ((unsigned long)(size) <= (unsigned long)(av->max_fast))    //当前chunk的size字段的比较，不能超过fastbin的最大值
        {
            if (chunk_at_offset(p, size)->size <= 2 * SIZE_SZ
                || __builtin_expect(chunksize(chunk_at_offset(p, size))
                                                >= av->system_mem, 0))            //比较下一个chunk的size字段，2*SIZE_ZE<chunksize<av->system_mem
    
            {
                errstr = "free(): invalid next size (fast)";
                goto errout;
            }
            ...
            fb = &(av->fastbins[fastbin_index(size)]);
            ...
            p->fd = *fb;
            *fb = p;
        }
    }

所以要设置好下个chunk的size字段。

看懂了，在网上找了道题练练手：  
xdctf2016的pwn200：  
虽然存在另外的解法，这里不管，只是为了学习HouseOfSpirit。

### 先分析流程：

  
![image.png](https://image.3001.net/images/20180807/1533627231_5b694b5f74c81.png!small)  

存在offbyone，只要完整的输入48个字节，就会泄露出ebp的值,因此是可以使用shellcode的，至于怎么触发shellcode，肯定需要修改返回地址，由于程序在每个函数返回前会进入下一个函数执行，因此在开始的函数里面想要直接写入返回地址，得避免破坏掉调用的子函数的栈帧才行，不太可能

执行测试就知道：![image.png](https://image.3001.net/images/20180807/1533627242_5b694b6a57e6c.png!small)划线的就是泄露的ebp的值。![image.png](https://image.3001.net/images/20180807/1533627249_5b694b71709fb.png!small)

输入id的值。

然后进入：![image.png](https://image.3001.net/images/20180807/1533627263_5b694b7f5e638.png!small)

申请了一个块，然后先通过buff获得输入，然后再通过strcpy复制到申请的块当中，并将块的地址赋值到全局变量的指针ptr中去，并且这个ptr是可以被覆盖重写的。

然后进入：![image.png](https://image.3001.net/images/20180807/1533627272_5b694b88e62f7.png!small)这个函数的内容和经典的菜单题没什么区别。![image.png](https://image.3001.net/images/20180807/1533627283_5b694b93d9ece.png!small)checkout函数是把块给free掉![image.png](https://image.3001.net/images/20180807/1533627292_5b694b9cc3825.png!small)checkin则是申请块，并填充块的内容：![image.png](https://image.3001.net/images/20180807/1533627301_5b694ba5e4299.png!small)

仔细调试分析可以发现,在提示输入who are u？的函数里边，id是我们可以控制的，然后进入了函数400A29

然后分配了money局部变量，也是我们可控的，stack的图大致如下

    
    
    =============stack===================
    
              money
              ...
              返回地址
              ...
              id
    =====================================

money和id都是可控的。就返回地址不可控，再结和文章开始houseofspirit的使用条件是两个可控的chunk。  
那其实这道题是HouseOfSpirit,已经很明显了。

### 解题思路

  * 从程序流程开始，先在栈中布置shellcode，并泄露出ebp的值，从而计算出shellcode在栈中的值。

  * 输入id作为下一个chunk的size字段的id的值

  * 将局部分量money伪造成一个chunk,构造好大小并且使得大小把返回地址包括在内，把ptr的值溢出覆盖为构造的chunk的地址，这个地址可以通过泄露的ebp计算出来

  * free掉伪造的chunk

  * 重新申请大小和伪造的chunk一致的块，使得系统将伪造的chunk分配给我们

  * 申请回来之后，返回地址就是我们可控的了，再将shellcode的地址写入返回地址处，控制程序返回就可以getshell

### 栈中布置图

在本地调试时，获得了关键的变量的地址，然后自己拼了这个图：  
![image.png](https://image.3001.net/images/20180807/1533627324_5b694bbccc089.png!small)  

调试关键：  
[md]0x400ac7处打断点，查看泄露ebp以及shellcode布置相关  
0x400b26处打断点，查看id在栈中的位置  
0x400a5f处打断点，伪造chunk

  

exp  

![image.png](https://image.3001.net/images/20180807/1533627364_5b694be4747ba.png!small)[阅读原文](https://bbs.ichunqiu.com/thread-43678-1-1.html?from=beef)可查看源文件哦~  

