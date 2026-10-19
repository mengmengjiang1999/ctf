**这篇文章是在看了ctfwiki以后又查询了几篇文章进行学习，但是大同小异而且感觉比较啰嗦。我们只要不需要知道chunk搜寻其他chunk的源码，我们只需要知道chunk搜寻其他的chunk，都是通过该chunk的size域以及prev_size域，都是基于本堆块去搜寻其他的堆块的相关信息**

# 篡改fastbin的size域

首先先上源码

    
    
    int main(void)
    {
        void *ptr,*ptr1;
    
        ptr=malloc(0x10);//分配第一个0x10的chunk
        malloc(0x10);//分配第二个0x10的chunk
    
        *(long long *)((long long)ptr-0x8)=0x41;// 修改第一个块的size域
    
        free(ptr);
        ptr1=malloc(0x30);// 实现 extend，控制了第二个块的内容
        return 0;
    }
    //都是基于64位操作系统，后面也是
    

创建了两个指针，首先使用ptr指针申请0x10的内存，然后申请了一个没有指针的堆块。*ptr-0x8就是chunk的size域。然后释放掉ptr。再利用ptr1申请0x30的chunk，接下来我们gdb调一下(glibc2.21版本)![image.png](https://image.3001.net/images/20210922/1632311030_614b16f68e1d9c1f9c7c4.png!small)这是刚申请完两个malloc以后的堆![image.png](https://image.3001.net/images/20210922/1632311126_614b175636019b644f2a7.png!small)然后我们通过
*ptr-0x8修改了之前的chunk的size域  
![image.png](https://image.3001.net/images/20210922/1632311496_614b18c8b189b07e7978a.png!small)![image.png](https://image.3001.net/images/20210922/1632311528_614b18e8e68b5dae3aec9.png!small)我们会发现申请的两个chunk都被free掉了，可以看一下fastbin中的地址很明显放在了0x40的地方![image.png](https://image.3001.net/images/20210922/1632311657_614b19696f019c014b668.png!small)![image.png](https://image.3001.net/images/20210922/1632311676_614b197c95cbf3597e632.png!small)我们又申请了0x30的内存，分配的还是原来的地址。因为最开始修改0x41是因为size域记录了chunk
head和user域，其实可用大小一共也就0x30。  
现在，我们可以直接对chunk2的所有数据进行操控，这就像是将堆进行重叠，所以也称为overlapping chunk

# 篡改使用中的smallchunk

    
    
    int main()
    {
        void *ptr,*ptr1;
    
        ptr=malloc(0x80);//分配第一个 0x80 的chunk1
        malloc(0x10); //分配第二个 0x10 的chunk2
        malloc(0x10); //防止与top chunk合并
    
        *(long long *)((long long)ptr-0x8)=0xb1;//这里会发现和ctfwiki上的不一样，因为我尝试了编译CTFwiki上的那段代码，报了段错误，然后我尝试寻找原因。可能是因为64位int最大只能存放2147483648，但是对于地址来说我当时地址是0x5555555546bc，不能存放在int中，如果使用int会造成精度的损失，所以报了段错误(不知道是不是，如果不是希望大佬的斧正，先感谢了)
        free(ptr);
        ptr1=malloc(0xa0);
    }
    

申请两个堆块与一个防止和topchunk合并的堆块，然后篡改，释放以后再次申请，我们直接调试  
![image.png](https://image.3001.net/images/20210922/1632312265_614b1bc949b371a466a60.png!small)申请的所有的chunk![image.png](https://image.3001.net/images/20210922/1632315127_614b26f7a3001af29985c.png!small)可以看到size字段已经被成功篡改![image.png](https://image.3001.net/images/20210922/1632315185_614b2731ebcfe874bddc7.png!small)释放以后，可以看见直接将两个chunk全部释放并且合并，并且放入unsortedbin中![image.png](https://image.3001.net/images/20210922/1632315420_614b281c4ce2457028704.png!small)我们申请了0xa0的内存以后，直接将整个chunk分配给了我们，所以我们可以控制整个堆块，chunk2我们可以任意修改

# 篡改free后的smallchunk

    
    
    int main()
    {
        void *ptr,*ptr1;
    
        ptr=malloc(0x80);//分配第一个0x80的chunk1
        malloc(0x10);//分配第二个0x10的chunk2
    
        free(ptr);//首先进行释放，使得chunk1进入unsorted bin
    
        *(int *)((int)ptr-0x8)=0xb1;
        ptr1=malloc(0xa0);
    }
    

这次代码也是申请了两个chunk，但是我们先要释放第一个chunk  
![image.png](https://image.3001.net/images/20210922/1632316094_614b2abe8a2bc7cb8de67.png!small)首先我们先申请了两个chunk![image.png](https://image.3001.net/images/20210922/1632316127_614b2adf0de6f3e6a2e53.png!small)free掉第一个chunk以后该chunk进入了unsortedbin![image.png](https://image.3001.net/images/20210922/1632316285_614b2b7d1c69c0c5f92ac.png!small)然后我们修改它的size字段大小，并且会发现修改完大小以后第二个chunk直接被第一个chunk合并并且进入unsortedbin中![image.png](https://image.3001.net/images/20210922/1632316612_614b2cc408af427ab32f9.png!small)然后我们malloc以后同样可以使用两个chunk的空间，第二个chunk可以进行任意修改

 **我们这三个示例中，都可以对第二个chunk写入任意数据，那么我们可以精心构造我们的数据，例如fd或bk字段，从而实现overlapping利用**

# 后向的overlapping

    
    
    int main()
    {
        void *ptr,*ptr1;
    
        ptr=malloc(0x10);//分配第1个 0x80 的chunk1
        malloc(0x10); //分配第2个 0x10 的chunk2
        malloc(0x10); //分配第3个 0x10 的chunk3
        malloc(0x10); //分配第4个 0x10 的chunk4    
        *(int *)((int)ptr-0x8)=0x61;
        free(ptr);
        ptr1=malloc(0x50);
    }
    

这个就是比较正常的overlapping，通过修改size字段来合并高地址chunk![image.png](https://image.3001.net/images/20210922/1632317353_614b2fa91ff39eec1ac27.png!small)申请chunk![image.png](https://image.3001.net/images/20210922/1632317497_614b303914a3d4be8ee96.png!small)更改chunk![image.png](https://image.3001.net/images/20210922/1632317517_614b304d8747ccb5de275.png!small)释放chunk![image.png](https://image.3001.net/images/20210922/1632317538_614b306218bf55af98110.png!small)再次申请，就可以任意篡改下面的chunk的数据了

# 前向overlapping``

![image.png](https://image.3001.net/images/20210922/1632317954_614b3202b1b0fb3bf7a8e.png!small)首先我们还是申请了内存  
![image.png](https://image.3001.net/images/20210922/1632317981_614b321dc41d50a9f876c.png!small)释放掉第一个chunk  
![image.png](https://image.3001.net/images/20210922/1632318038_614b3256078497c3a7666.png!small)修改第四个chunksize的最低为和prev_size位  
![image.png](https://image.3001.net/images/20210922/1632318061_614b326d370867e415b26.png!small)释放第四个内存以后将前面的内存全部合并并且释放

 **这就是对chunk块prev_size和size域的修改，可以造成chunk的overlapping，我们可以写入任意数据**

 **本文参考自[CTFwiki](https://ctf-wiki.org/pwn/linux/user-mode/heap/ptmalloc2/chunk-extend-overlapping/#5extendoverlapping)，感谢大佬**

