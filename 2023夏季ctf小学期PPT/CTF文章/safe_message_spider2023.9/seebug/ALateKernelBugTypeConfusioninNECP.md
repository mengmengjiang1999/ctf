**作者：Zhuo Liang of Qihoo 360 Nirvan Team  
博客：<https://blogs.projectmoon.pw/2018/11/30/A-Late-Kernel-Bug-Type-Confusion-in-NECP/>**

### 1 介绍

Apple 对于代码开放的态度一直为广大的安全研究员们所诟病，代码更新总是扭扭捏捏滞后很多于系统发版时间。比如当前 macOS 的最新版本为 Mojave
10.14.1，而最新的代码还停留在 10.13.6。本文将要提到的是笔者在审计 10.13.6
的代码时发现的一个内核漏洞，而在验证的时候发现在最新版本已经无法触发，经过分析发现这不是一个 0-day，而是一个已经在 macOS 10.14 和 iOS
12.0 上已经修补了的问题。由于这个漏洞的触发没有权限限制和强制访问控制，漏洞本身也有一定代表性，特记录分享一下。

### 2 背景知识

#### 2.1 一切皆文件

`*nix` 世界众多的优秀品质(所谓设计哲学)最广为人知的可能就是“一切皆文件”了。在这种设计理念下，在 `*nix` 下特别是在 Linux
里，大部分内核对象，比如普通文件、socket、共享内存和信号量等，都是由内核给用户态暴露一个文件描述符，并提供对于文件描述符的统一操作，常见的比如
read、write、close 和 select 等。
很显然，内核对于这些文件描述符本身所代表的对象类型都是有标记的，通过类型将这些同样的系统调用分配到各自的回调函数中，这就是 C 语言里的多态。 Linux
里另外一个重度依赖多态的模块就是 VFS，与本文要谈的漏洞无关，所以此处不谈。

macOS 和 iOS 内核(以下统一称 XNU)的部分代码也遵循“一切皆文件”这条原则。在 XNU
里，内核为每个进程维护一张文件描述符与文件表项的映射表`struct filedesc *
p_fd`，每一个文件表项即为每一个与文件有关操作的第一步需要获取的对象，其定义如下：

    
    
    // bsd/sys/file_internal.h
    /*
     * Kernel descriptor table.
     * One entry for each open kernel vnode and socket.
     */
    
    struct fileproc {
        unsigned int f_flags;
        int32_t f_iocount;
        struct fileglob * f_fglob;
        void * f_wset;
    };

在这个结构体的成员中，最重要的一项即为 `struct fileglob * f_fglob`，其定义如下：

    
    
    // bsd/sys/file_internal.h
    
    struct fileglob {
        LIST_ENTRY(fileglob) f_msglist; /* list of active files */
        int32_t fg_flag;                /* see fcntl.h */
        int32_t fg_count;               /* reference count */
        int32_t fg_msgcount;            /* references from message queue */
        int32_t fg_lflags;              /* file global flags */
        kauth_cred_t fg_cred;           /* credentials associated with descriptor */
        const struct fileops {
            file_type_t fo_type; /* descriptor type */
            int (*fo_read)(struct fileproc * fp, struct uio * uio, int flags, 
                           vfs_context_t ctx);
            int (*fo_write)(struct fileproc * fp, struct uio * uio, int flags, 
                            vfs_context_t ctx);
    #define FOF_OFFSET 0x00000001 /* offset supplied to vn_write */
    #define FOF_PCRED 0x00000002  /* cred from proc, not current thread */
            int (*fo_ioctl)(struct fileproc * fp, u_long com, caddr_t data, 
                            vfs_context_t ctx);
            int (*fo_select)(struct fileproc * fp, int which, void * wql, 
                             vfs_context_t ctx);
            int (*fo_close)(struct fileglob * fg, vfs_context_t ctx);
            int (*fo_kqfilter)(struct fileproc * fp, struct knote * kn, 
                               struct kevent_internal_s * kev, 
                               vfs_context_t ctx);
            int (*fo_drain)(struct fileproc * fp, vfs_context_t ctx);
        } * fg_ops;
        off_t fg_offset;
        void * fg_data;    /* vnode or socket or SHM or semaphore */
        void * fg_vn_data; /* Per fd vnode data, used for directories */
        lck_mtx_t fg_lock;
    #if CONFIG_MACF
        struct label * fg_label; /* JMM - use the one in the cred? */
    #endif
    };

在 `struct fileglob` 中，需要关注的几个成员如下：

a) fg_flag 对于文件操作的权限，比如 FWRITE和FREAD，读写操作对应的不同类型的对象有不同的解释。

b) fileops 文件操作定义，其中需要关注 fo_type 也就是对象类型，在 XNU 中目前存在的几种类型如下：

    
    
    // bsd/sys/file_internal.h
    /* file types */
    typedef enum {
        DTYPE_VNODE = 1, /* file */
        DTYPE_SOCKET,    /* communications endpoint */
        DTYPE_PSXSHM,    /* POSIX Shared memory */
        DTYPE_PSXSEM,    /* POSIX Semaphores */
        DTYPE_KQUEUE,    /* kqueue */
        DTYPE_PIPE,      /* pipe */
        DTYPE_FSEVENTS,  /* fsevents */
        DTYPE_ATALK,     /* (obsolete) */
        DTYPE_NETPOLICY, /* networking policy */
    } file_type_t;

c) `fg_data` 代表真正的对象以及上下文信息，`fileops` 里的 `fo_*` 回调函数最终都是操作对应的 `fg_data` 对象。

下面以 socket 的创建为例说明上述大致流程。

    
    
    // bsd/kern/uipc_syscall.c 
    
    static int
    socket_common(struct proc * p, int domain, int type, int protocol, pid_t epid, 
        int32_t * retval, int delegate)
    {
        ...
        error = falloc(p, &fp, &fd, vfs_context_current());
        if (error) {
            return (error);
        }
        fp->f_flag = FREAD | 
            FWRITE; // [a]，这里的 f_flag 实际上是指向 fileops 的 fg_flag，下同。
        fp->f_ops  = &socketops; // [b]
    
        if (delegate)
            error = socreate_delegate(domain, &so, type, protocol, epid);
        else
            error = socreate(domain, &so, type, protocol); // [c]
    
        if (error) {
            fp_free(p, fd, fp);
        } else {
            fp->f_data = (caddr_t)so; // [d]
            ...
        }
        return (error);
    }

在用户态调用 socket(AF_INET, SOCK_STREAM, 0) 后，内核代码将进入如上流程，首先分配文件表项和 fileglob 对象，然后在
[a] 处将 fg_flag 设置为可读可写，表示可以对这个 socket 进行发送和接收数据相关操作。在 [b] 处，将 fileops 设置为
socketops，对于该变量的定义如下：

    
    
    // bsd/kern/sys_socket.c
    
    const struct fileops socketops = {
        .fo_type     = DTYPE_SOCKET,
        .fo_read     = soo_read,
        .fo_write    = soo_write,
        .fo_ioctl    = soo_ioctl,
        .fo_select   = soo_select,
        .fo_close    = soo_close,
        .fo_kqfilter = soo_kqfilter,
        .fo_drain    = soo_drain,
    };

该变量里设置的成员回调函数即为用户态的系统调用将会真正触发的函数。在 [c] 处， `socreate` 函数会根据 domain、type 和
protocol 创建 `struct socket` 对象， 并在 [d] 处赋给 fg_data，即为真正的 backend object。

#### 2.2 NECP

NECP, Network Extension Control Policy，顾名思义是一种网络控制策略，下面是内核对其作出的解释：

    
    
    // bsd/net/necp.c
    
    /*
     * NECP - Network Extension Control Policy database
     * ------------------------------------------------     * The goal of this module is to allow clients connecting via a
     * kernel control socket to create high-level policy sessions, which
     * are ingested into low-level kernel policies that control and tag
     * traffic at the application, socket, and IP layers.
     */

简单的说就是用户态程序可以通过 NECP 来创建一些策略并将其注入到内核网络流量处理的模块中，对于应用层、socket 层和 IP
层的流量进行控制以及标记。本文不对与本漏洞无关的业务逻辑进行阐述，感兴趣的读者可以自行阅读内核代码。

在谈 NECP 的同时可以简单的介绍一下 Kernrl Control，通过官网对 Kernel Control
的[介绍](https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/NKEConceptual/control/control.html
"介绍")可以知道，Kernel Control 的主要作用就是用来使用户态程序有能力配置和控制内核以及内核扩展，这就是 NECP
最开始提供给用户态访问的最原始的形式。具体而言，内核首先通过 Kernel Control 提供的 KPI 注册一种 socket
类型，使用户态可以通过诸如 `socket(PF_SYSTEM, SOCK_DGRAM, SYSPROTO_CONTROL)` 访问到。注册部分的代码如下：

    
    
    // bsd/net/necp.c
    
    static errno_t
    necp_register_control(void)
    {
        struct kern_ctl_reg kern_ctl;
        errno_t result = 0;
    
        // Create a tag to allocate memory
        necp_malloc_tag = OSMalloc_Tagalloc(NECP_CONTROL_NAME, OSMT_DEFAULT);
    
        // Find a unique value for our interface family
        result = mbuf_tag_id_find(NECP_CONTROL_NAME, &necp_family);
        if (result != 0) {
            NECPLOG(LOG_ERR, "mbuf_tag_id_find_internal failed: %d", result);
            return (result);
        }
    
        bzero(&kern_ctl, sizeof(kern_ctl));
        strlcpy(kern_ctl.ctl_name, NECP_CONTROL_NAME, sizeof(kern_ctl.ctl_name));
        kern_ctl.ctl_name[sizeof(kern_ctl.ctl_name) - 1] = 0;
        kern_ctl.ctl_flags                               = CTL_FLAG_PRIVILEGED; // Require root
        kern_ctl.ctl_sendsize                            = 64 * 1024;
        kern_ctl.ctl_recvsize                            = 64 * 1024;
        kern_ctl.ctl_connect                             = necp_ctl_connect;
        kern_ctl.ctl_disconnect                          = necp_ctl_disconnect;
        kern_ctl.ctl_send                                = necp_ctl_send;
        kern_ctl.ctl_rcvd                                = necp_ctl_rcvd;
        kern_ctl.ctl_setopt                              = necp_ctl_setopt;
        kern_ctl.ctl_getopt                              = necp_ctl_getopt;
    
        result = ctl_register(&kern_ctl, &necp_kctlref);
        if (result != 0) {
            NECPLOG(LOG_ERR, "ctl_register failed: %d", result);
            return (result);
        }
    
        return (0);
    }

内核使用 `ctl_register` 函数将一个 `kern_ctl` 的对象注册到一个全局的数据集中。同样这里也有几点需要关注：

a) `NECP_CONTROL_NAME` 内核定义的宏，定义为字符串 `com.apple.net.necp_control`。

b) `kern_ctl.ctl_flags` 标记为需要 `root` 才能访问，后面会有提到。

c) `necp_ctl_*` 系列函数，作为回调函数会被对 NECP Kernel Control 的套接字的操作触发。

用户态在创建相关套接字后，通过 connect 系统调用可以创建与内核 NECP 模块交互的会话，并通过 write 的方式配置网络策略，通过 read
的方式读取内核通知。

#### 2.3 代码审计的一点思考

至此，对于本漏洞的基本知识已介绍完毕，本小结作为笔者审计代码的一点小感受，与本文主题无关，不感兴趣的读者可以直接阅读第3部分。

本文提到的代码广义上都是多态，而在 C
语言里多态的实现基本要依赖回调函数。对于更加复杂的诸如此类的回调函数系统实际上是很容易出问题的，阅读理解困难、调试不方便，这点笔者在曾经作为开发者参与开发维护一个回调满天飞的软件时深有体会，很显然会出现的问题有如下两点：

a) 资源管理
底层语言程序员们肯定会听过“谁开发，谁保护；谁污染，谁治理”的资源管理原则，但是事情总是这样吗？在实际的案例中，再优美的设计也有可能被历史包袱和奇葩的需求所打败，最后落得一地鸡毛。当然，遵循一种统一的资源管理原则肯定是值得提倡的，问题是软件开发初期肯定会有考虑欠周的地方，加上开发中后期人员的变动，后来参与的成员可能会因为不能熟悉该软件中的统一规范而导致写了危险的代码。

b) 处理逻辑
这里提到的处理逻辑是指回调函数设计之初所期望的开发者对于这些回调函数的参数、返回值的处理以及实际逻辑所能访问的边界有足够的意见一致性，这些问题较多出现在扩展性质的程序中。而对这些约定的东西处理不当又极易导致资源管理的问题。

篇幅有限，这里不进行展开，观点仅作为一点不成熟的小建议。

### 3 类型混淆

目前为止所提到的内容都是没问题的，问题出在 Apple 在2017年7月份一次更新(没有仔细看，感兴趣的读者可以自行查证)中添加的关于 `necp`
模块的几个系统调用里面。这些系统调用作为 2.2 中提到的用 socket 的方式操作 NECP 的一种替代品。具体来说就是
`necp_session_*` 和 `necp_client_*` 这两类函数。这些函数是怎么实现相关功能的这里不讨论，只谈与漏洞相关的地方。

内核提供 `necp_open` 和 `necp_session_open`
这两个系统调用，并且两个系统调用都返回文件描述符，根据之前提到的，文件描述符所对应的内核真正的对象的类型应该是不同的。通过查看代码发现，确实不同。两个函数的代码如下：

    
    
    // bsd/net/necp.c 
    int necp_session_open(struct proc * p, struct necp_session_open_args * uap, int * retval)
    {
        int error                     = 0;
        struct necp_session * session = NULL;
        struct fileproc * fp          = NULL;
        int fd                        = -1;
    
        uid_t uid = kauth_cred_getuid(proc_ucred(p));
        if (uid != 0 && priv_check_cred(kauth_cred_get(), 
            PRIV_NET_PRIVILEGED_NECP_POLICIES, 0) != 0) { // [a]
            NECPLOG0(LOG_ERR, "Process does not hold necessary entitlement to open NECP session");
            error = EACCES;
            goto done;
        }
    
        error = falloc(p, &fp, &fd, vfs_context_current());
        if (error != 0) {
            goto done;
        }
    
        session = necp_create_session(); // [b]
        if (session == NULL) {
            error = ENOMEM;
            goto done;
        }
    
        fp->f_fglob->fg_flag = 0;
        fp->f_fglob->fg_ops  = &necp_session_fd_ops; // [c]
        fp->f_fglob->fg_data = session; // [d]
    
        proc_fdlock(p);
        FDFLAGS_SET(p, fd, (UF_EXCLOSE | UF_FORKCLOSE));
        procfdtbl_releasefd(p, fd, NULL);
        fp_drop(p, fd, fp, 1);
        proc_fdunlock(p);
    
        *retval = fd;
    done:
        if (error != 0) {
            if (fp != NULL) {
                fp_free(p, fd, fp);
                fp = NULL;
            }
        }
    
        return (error);
    }
    
    
    // bsd/net/necp_client.c
    int necp_open(struct proc * p, struct necp_open_args * uap, int * retval)
    {
        int error                     = 0;
        struct necp_fd_data * fd_data = NULL;
        struct fileproc * fp          = NULL;
        int fd                        = -1;
        ...
        error = falloc(p, &fp, &fd, vfs_context_current());
        if (error != 0) {
            goto done;
        }
    
        if ((fd_data = zalloc(necp_client_fd_zone)) == NULL) { // [f]
            error = ENOMEM;
            goto done;
        }
    
        memset(fd_data, 0, sizeof(*fd_data));
    
        fd_data->necp_fd_type = necp_fd_type_client;
        fd_data->flags        = uap->flags;
        RB_INIT(&fd_data->clients);
        TAILQ_INIT(&fd_data->update_list);
        lck_mtx_init(&fd_data->fd_lock, necp_fd_mtx_grp, necp_fd_mtx_attr);
        klist_init(&fd_data->si.si_note);
        fd_data->proc_pid = proc_pid(p);
    
        fp->f_fglob->fg_flag = FREAD;
        fp->f_fglob->fg_ops  = &necp_fd_ops; // [g]
        fp->f_fglob->fg_data = fd_data; // [h]
    
        proc_fdlock(p);
    
        *fdflags(p, fd) |= (UF_EXCLOSE | UF_FORKCLOSE);
        procfdtbl_releasefd(p, fd, NULL);
        fp_drop(p, fd, fp, 1);
        ...
        return (error);
    }

注意代码中标记字母的地方。在 [d] 和 [h] 处对应赋值的两个对象的类型分别为 `struct necp_session` 和 `struct
necp_fd_data` 类型。再注意 [c] 和 [g] 处， 给 fileops 赋值的值分别为：

    
    
    // bsd/net/necp.c
    static const struct fileops necp_session_fd_ops = {
        .fo_type     = DTYPE_NETPOLICY,
        .fo_read     = noop_read,
        .fo_write    = noop_write,
        .fo_ioctl    = noop_ioctl,
        .fo_select   = noop_select,
        .fo_close    = necp_session_op_close,
        .fo_kqfilter = noop_kqfilter,
        .fo_drain    = NULL,
    };
    
    
    // bsd/net/necp_client.c
    static const struct fileops necp_fd_ops = {
        .fo_type     = DTYPE_NETPOLICY,
        .fo_read     = noop_read,
        .fo_write    = noop_write,
        .fo_ioctl    = noop_ioctl,
        .fo_select   = necpop_select,
        .fo_close    = necpop_close,
        .fo_kqfilter = necpop_kqfilter,
        .fo_drain    = NULL,
    };

fo_type 都是 `DTYPE_NETPOLICY`，类型居然一样！再看从文件描述符到具体对象转换的函数：

    
    
    // bsd/net/necp.c
    
    static int
    necp_session_find_from_fd(int fd, struct necp_session ** session)
    {
        proc_t p             = current_proc();
        struct fileproc * fp = NULL;
        int error            = 0;
    
        proc_fdlock_spin(p);
        if ((error = fp_lookup(p, fd, &fp, 1)) != 0) {
            goto done;
        }
        if (fp->f_fglob->fg_ops->fo_type != DTYPE_NETPOLICY) { // [a]
            fp_drop(p, fd, fp, 1);
            error = ENODEV;
            goto done;
        }
        *session = (struct necp_session *)fp->f_fglob->fg_data; // [b]
    
    done:
        proc_fdunlock(p);
        return (error);
    }

另外一个函数对应也一样，可自行查阅。在这里，[a] 处先判断该类型是否为 DTYPE_NETPOLICY，[b] 处，直接就转换成 struct
necp_session 对象。单个的看是没有问题的，但如果传进来的是一个代表了 struct necp_fd_data 的文件描述符呢，此时在 [a]
处， CHECK！[b] 处，TYPE CONFUSION。下载
[PoC](https://blogs.projectmoon.pw/2018/11/30/A-Late-Kernel-Bug-Type-Confusion-in-NECP/NECPTypeConfusion.c "PoC") 可验证这一猜想。

### 4 权限与沙箱

在 PoC 中，使用的是 necp_open 创建 necp_fd_data 对象， 然后以把其当做 necp_session
对象。反过来其实也行，但是由于 necp_session_open 函数因为 `PRIV_NET_PRIVILEGED_NECP_POLICIES`
的检查是普通用户无法成功调用的，所以最好是以 PoC 中的方式触发。同时，在这几个函数中，是没有沙盒限制的，意味着这个类型混淆漏洞可以用来绕过任意沙盒。

### 5 漏洞修复

查证了内核最新代码(没有源代码，只有二进制)，修复的方式是加了一个子类型的检查。

necp_session_find_from_fd 函数： ![
](https://images.seebug.org/content/images/2018/12/6ba1af9c-e31c-4d06-8fb6-3a129432aa20.png-w331s)

necp_find_fd_data 函数： ![
](https://images.seebug.org/content/images/2018/12/57a3b228-3597-40af-a0f3-7d3723c21790.png-w331s)

在 fg_data 的第一个字节存储的就是这个类型信息，这个在漏洞修复之前就存在，只是没有利用起来。

### 6 One More

在验证漏洞失败后的失望之余，在[苹果公告](https://support.apple.com/en-us/HT209193
"苹果公告")上找到了可能的漏洞致谢信息。

![
](https://images.seebug.org/content/images/2018/12/dc8f7907-b88e-4f1b-8cd8-d12e0f67343b.png-w331s)

随后又去 [ZDI](https://www.zerodayinitiative.com/advisories/ZDI-18-1325/ "ZDI")
上证实了这个信息，编号为 CVE-2018-4425。

![
](https://images.seebug.org/content/images/2018/12/8baddf4f-9921-42b9-9826-53e8e7c38171.png-w331s)

行文仓促，难免会有不严谨的地方，[欢迎指出](brightiup.zhuo@gmail.com "欢迎指出") 。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/752/>

