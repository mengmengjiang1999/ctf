省去了安装的过程，如果有能力建议直接看英文原版，此篇根据官方文档排版而作。  
官方文档：<https://docs.pwntools.com/en/stable/intro.html>

## 开始

为了能够熟练的使用pwntools，下面我将列一些使用案例。

    
    
    >>> from pwn import *

这句导入了许多实用的东西到全局命名空间。到底导入了什么能，可以参考：<https://docs.pwntools.com/en/stable/globals.html>

## 建立连接

如果你想PWN掉一个目标程序那么首先得和它建立连接对吧? pwntools 使用 `pwnlib.tubes`模块简化了一系列复杂的操作。

因为这个模块有一个标准的接口与程序、套接字、串口等进行交互。比如远程连接可以通过`pwnlib.tubes.remote`.

    
    
    >>> conn = remote('ftp.ubuntu.com',21)
    >>> conn.recvline() # doctest: +ELLIPSIS
    b'220 ...'
    >>> conn.send(b'USER anonymous\r\n')
    >>> conn.recvuntil(b' ', drop=True)
    b'331'
    >>> conn.recvline()
    b'Please specify the password.\r\n'
    >>> conn.close()

当然它也可以很容易的监听反向连接

    
    
    >>> l = listen()
    >>> r = remote('localhost', l.lport)
    >>> c = l.wait_for_connection()
    >>> r.send(b'hello')
    >>> c.recv()
    b'hello'

使用 `pwnlib.tubes.process`很容易能够与某进程进行交互

    
    
    >>> sh = process('/bin/sh')
    >>> sh.sendline(b'sleep 3; echo hello world;')
    >>> sh.recvline(timeout=1)
    b''
    >>> sh.recvline(timeout=5)
    b'hello world\n'
    >>> sh.close()

比上面更简单的方法，不用手动方式，让它自动交互

    
    
    >>> sh.interactive() # doctest: +SKIP
    $ whoami
    user

甚至还有一个SSH模块`pwnlib.tubes.ssh`。当使用SSH进入平台执行local/setuid利用时，可以快速开启进程并获取输出，或开启进程与之平滑的交互。

    
    
    >>> shell = ssh('bandit0', 'bandit.labs.overthewire.org', password='bandit0', port=2220)
    >>> shell['whoami']
    b'bandit0'
    >>> shell.download_file('/etc/motd')
    >>> sh = shell.run('sh')
    >>> sh.sendline(b'sleep 3; echo hello world;') 
    >>> sh.recvline(timeout=1)
    b''
    >>> sh.recvline(timeout=5)
    b'hello world\n'
    >>> shell.close()

## 打包整数

在写EXP过程中，我们常常需要转换一些整数和字节序，也不用麻烦的使用Python内建的`struct`模块，pwntools使用
`pwnlib.util.packing`模块，更容易上手：

    
    
    >>> import struct
    >>> p32(0xdeadbeef) == struct.pack('I', 0xdeadbeef)
    True
    >>> unhex('37130000')
    b'7\x13\x00\x00'
    >>> u32(b'abcd') == struct.unpack('I', b'abcd')[0]
    True

packing/unpacking操作是以位宽来决定的

    
    
    >>> u8(b'A') == 0x41
    True

## 设置目标的架构和操作系统的类型

设置好目标机的一些全局参数，调用某些函数会少一些麻烦，比如下面

    
    
    >>> asm('nop')
    b'\x90'
    >>> asm('nop', arch='arm')
    b'\x00\xf0 \xe3'

我们把操作系统的字长，字节序设置在全局中的话，会少了很多麻烦

    
    
    >>> context.arch      = 'i386'
    >>> context.os        = 'linux'
    >>> context.endian    = 'little'
    >>> context.word_size = 32

此外，也可以用`context()`函数，一次性设置好所有

    
    
    >>> asm('nop')
    b'\x90'
    >>> context(arch='arm', os='linux', endian='big', word_size=32)
    >>> asm('nop')
    b'\xe3 \xf0\x00'

## 设置日志详细程度

还是通过`context`来设置日志等级：

    
    
    >>> context.log_level = 'debug'

这个设置会将通过`tube`收发的内容都打印在屏幕上

## 汇编与反汇编

来看看由 `pwnlib.asm`模块提供的函数

    
    
    >>> enhex(asm('mov eax, 0'))
    'b800000000'

如果你构造好shellcode了，他也能够很容易的反汇编

如果你构造好shellcode了，他也能够很容易的反汇编

    
    
    >>> print(disasm(unhex('6a0258cd80ebf9')))
       0:   6a 02                   push   0x2
       2:   58                      pop    eax
       3:   cd 80                   int    0x80
       5:   eb f9                   jmp    0x0

所以pwntools的魔力就在这，大多时候你甚至不需要自己写shellcode, 有一些非常实用的 shellcode都已经在
`pwnlib.shellcraft`模块里提供了

比如我们想要先 setreuid(getuid(), getuid()) 然后复制四个文件描述符到stdin, stdout, and stderr，那么

    
    
    >>> enhex(asm(shellcraft.setreuid() + shellcraft.dupsh(4))) # doctest: +ELLIPSIS
    '6a3158cd80...'

## 有用的杂项工具

有`pwnlib.util.fiddling`模块，我们不需要其他HEX工具的辅助就可以生成一个HEX序列  
有`pwnlib.cyclic`模块，我们可以很容易找到造成程序崩溃的偏移地址

    
    
    >>> print(cyclic(20).decode())
    aaaabaaacaaadaaaeaaa
    >>> # Assume EIP = 0x62616166 (b'faab' which is pack(0x62616166))  at crash time
    >>> print(cyclic_find(b'faab'))
    120

## 剖析 ELF 文件

不用手动！用`pwnlib.elf`模块可以在程序运行时查看这些。

    
    
    >>> e = ELF('/bin/cat')
    >>> print(hex(e.address)) #doctest: +SKIP
    0x400000
    >>> print(hex(e.symbols['write'])) #doctest: +SKIP
    0x401680
    >>> print(hex(e.got['write'])) #doctest: +SKIP
    0x60b070
    >>> print(hex(e.plt['write'])) #doctest: +SKIP
    0x401680

你甚至可以直接打补丁和保存文件

    
    
    >>> e = ELF('/bin/cat')
    >>> e.read(e.address, 4)
    b'\x7fELF'
    >>> e.asm(e.address, 'ret')
    >>> e.save('/tmp/quiet-cat')
    >>> disasm(open('/tmp/quiet-cat','rb').read(1))
    '   0:   c3                      ret'

## 实战小结

### pwntools使用的一般流程

  1. 使用process/remote建立交互
  2. 通过调试，泄露堆栈信息找到利用点。
  3. 构造Payload利用
  4. 开启交互式shell，完成利用。

### process/remote模块

PWN题一开始就要建立与可执行程序的交互。这就是通过这两个模块实现的。如果是本地调试的话，就使用process模块，本地调试好了就是远程利用拿FLAG了，用的是remote模块。  
一般使用pwntools的脚本和可执行文件放在同一目录，方便管理。使用process的过程为：

    
    
    # 引入模块
    from pwn import process
    # 生成实例
    p = process('./pwn')
    
    # 向进程发信息, 模拟用户的输入，在输入后添加回车，传递给进程。
    p.sendline('some thing')
    
    # 接收进程输出信息
    # 交互时，要确定进程的状态，通过recvuntil，确保程序是运行在期望的状态下，
    # 可以保证Payload是在合适的时机发送的。
    p.recvuntil('some thing')
    
    # 开启交互shell
    # 这个时候要确认进程已已经成功get shell了，这个函数能开启一个shell。如果
    # Payload 有异常这时脚本会异常中止。
    p.interactive()

### ELF模块

  * .text: 代码段
  * .data: 数据段

需要动态链接的程序还会有以下段：

  * .plt: procedure link table, 过程链接表
  * .got: global offset table，全局偏移表。  
通过ELF加载了可执行文件，就可以方便地读取一些信息了。

    
    
    elf = ELF('./pwn')
    # symbols里包含了变量，函数的地址。如果没有开启地址随机化的话，读到的地址，就是其实际加载的地址。
    elf.symbols['system']
    # 也可以读bss段的地址
    elf.bss()﻿

