# NSA超级后门Bvp47隐身技能：进程隐身

> 本文是基于[Bvp47技术报告(PDF)](https://www.pangulab.cn/files/The_Bvp47_a_top-> tier_backdoor_of_us_nsa_equation_group.zh-cn.pdf)和`Linux`内核写的。

在`Linux`如何隐藏一个进程呢？

平时，我们都是使用`ps`来查看进程信息。但`ps`做了什么呢？  
执行`strace ls`看一下，可以看到输出结果有如下几行

    
    
    openat(AT_FDCWD, "/proc", O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_DIRECTORY) = 5
    newfstatat(5, "", {st_mode=S_IFDIR|0555, st_size=0, ...}, 
    getdents64(5, 0x55aa4987a120 /* 311 entries */, 32768) = 7856
    

好吧，果然是`Unix`思想“一切皆文件”，连`ps`命令只是读取`/proc`下面的内容。所以，很多主机入侵检测系统(`HIDS`)检查恶意进程也是读取`/proc`下的内容。安卓手机上很多检测`rooted`的方案也会使用这种方法来检测`su`进程来确定是否`rooted`过了。而同样，安卓不少`rooted`工具是通过挂钩读取文件相关的系统调用如`open`,`openat`,`opendir`,`getdents`等来隐藏`su`进程，从而躲避检测。

那么，在`Linux`隐藏一个进程，就和隐藏一个文件类似，一般是两种方法：

  * 劫持`libc.so`或系统调用的API，针对单个进程隐藏，可以给该进程设置`LD_PRELOAD`环境变量或者调整`LD_LIBRARY_PATH`环境变量里路径的顺序。对所有进程隐藏，则把劫持的so文件的路径加入到`/etc/ld.so.preload`
  * 最复杂，也是最困难，就是在内核里进程相关的函数挂钩劫持。

> 因为`proc`文件系统是虚拟文件系统，它不会像普通文件那样使用`.`开头的文件，所以和文件隐藏又不大一样。

而`Bvp47`是在`Linux`内核挂钩劫持。看看它对内核里哪些进程相关的函数挂钩。

  * proc_root_lookup - 在/proc下查看进程
  * proc_pid_readdir - 读取某进程的/proc目录
  * "kill_"前缀 - 杀死进程
  * sys_kill - 杀死进程
  * sys_rt_sigqueueinfo - 进程信号队列信息
  * sys_tkill - 杀死进程
  * sys_tgkill - 杀死进程
  * sys_getpriority - 获取进程优先级
  * sys_setpriority - 设置进程优先级
  * sys_getpgid - 获取进程组id
  * sys_getsid - 获取进程会话id
  * sys_capget - 获取进程能力
  * setscheduler - 调度进程
  * sys_sched_getscheduler - 获取进程调度器
  * sys_sched_getparam - 进程参数获取
  * sched_getaffinity - 进程与cpu绑定的关系获取
  * sched_setaffinity - 设置进程绑定CPU
  * sys_sched_rr_get_interval - 调度间隔
  * sys_ptrace - 调试进程
  * sys_wait4 - 等待进程执行结束
  * sys_waitid - 等待进程执行结束
  * do_execve - 执行命令
  * do_fork - 创建进程
  * release_task - 退出进程
  * do_acct_process - BSD进程审计功能

根据上面`strace
ls`的结果，所以，`Bvp47`要隐藏它自身进程第一步，就是对遍历`/proc`的函数挂钩。由于`proc`是虚拟文件系统，所以，在内核态中，它并不是像隐藏文件那样挂钩`vfs_readdir`，而挂钩`proc_root_lookup`来隐藏自身进程。

由于`pid`的范围是一定的，最小值是1，最大值在`/proc/sys/kernel/pid_max`里,
比如我的电脑是4194304，那么可以通过检测`/proc/<pid>`这个目录是否存在来确定进程是否存在。所以，`Bvp47`就通过挂钩`proc_pid_readdir`来隐藏自身进程。

但对于`HIDS`开发人员来说，读取`/proc`下的方式实际上是一种指纹检测的方法,而`HIDS`往往会采用更多基于行为检测的方法。

当一个进程存在时，虽然它从`proc`系统里隐身了，但它还是存在于系统中，它可以接收信号，接受调度，可以被调试，接受系统调用对它的状态查询。由于`pid`的范围是一定的，可以通过枚举整个范围`pid`，对它们发信呈，调度，调试，状态查询，再对照`proc`的结果来检测出进程是否隐藏。

最简单的是使用`kill`命令，用`shell`脚本就可以实现。

    
    
    kill -0 <pid>
    echo $?
    

`-0`并不会杀掉进程，只是获取它的存在，如果存在,`$?`就是0。

> 有兴趣的读者可以从全球最大同性交友网站`github`上搜索`linux
> rootkits`来检验一下，记着用虚拟机，还要保存快照。有些`rootkit`运行了，用`ps`是看不到它的，但使用上面脚本是可以获取它的存在。

而`kill`命令其实就是使用`kill`这个系统调用，所以，`Bvp47`必须对内核态对应的函数`sys_kill`,`sys_tkill`,`sys_tgkill`,`kill_`前缀的挂钩，从而屏蔽这些信号的探测。

同理，要信号屏蔽，`Bvp47`就肯定要对`sys_rt_sigqueueinfo`挂钩。

如果对这些函数原型进行查看，它们的参数里有一个是`pid`或参数的成员是`pid`，都可以通过枚举所有`pid`来检测进程是否隐藏，所以，这也是`Bvp47`对这些函数挂钩来隐藏的原因。

  * sys_getpriority - 获取进程优先级
  * sys_setpriority - 设置进程优先级
  * sys_getpgid - 获取进程组id
  * sys_getsid - 获取进程会话id
  * sys_capget - 获取进程能力
  * setscheduler - 调度进程
  * sys_sched_getscheduler - 获取进程调度器
  * sys_sched_getparam - 进程参数获取
  * sched_getaffinity - 进程与cpu绑定的关系获取
  * sched_setaffinity - 设置进程绑定CPU
  * sys_sched_rr_get_interval - 调度间隔
  * sys_ptrace - 调试进程
  * sys_wait4 - 等待进程执行结束
  * sys_waitid - 等待进程执行结束

> 在平时工作中，使用`kill`,
> `getsid`之类系统调用枚举`pid`来检测隐藏进程的方法，不光用于`HIDS`，还用于安卓检测`rooted`和`iOS`程序检测越狱中。

貌似通过上面手法，`Bvp47`已经可以隐藏掉它的进程，那为什么它还要对这些函数挂钩呢？

  * do_execve - 执行命令
  * do_fork - 创建进程
  * release_task - 退出进程
  * do_acct_process - BSD进程审计功能

由于上面的检测方法都是主动检测，只能定时，从而有时间间隙来绕过。而目前大多数`HIDS`都使用实时进程事件检测的方式来建模，发现威胁。

而`Linux`实时进程事件检测的方法主要是几种：

  1. 用户态挂钩系统调用`fork`,`execve`,`clone`,`exit`等系统调用，从而捕获它的事件。腾讯洋葱`HIDS`，滴滴驭龙`HIDS`采用这种方式
  2. 用户态使用`netlink`的`kernel connector`模式。华为云`HIPS`，腾讯洋葱`HIDS`采用这种方式。
  3. 用户态调用`audit`框架。青藤云`HIDS`采用这种方式
  4. 内核态`eBPF+kprobe`方式。美团`HIDS`采用这种方式，据说阿里云`HIDS`也是这种。
  5. 内核态驱动`kprobe`方式。字节跳动`HIDS`采用这种方式

而上面这些方式，在内核里面，最后都会落入到`do_execve`,`do_fork`,
`release_task`，`do_acct_process`,其中前两者创建的，后两者是退出的（均在`do_exit`函数的执行流）。

所以，`Bvp47`就可以通过挂钩这四个函数，直接把进程创建和退出事件直接扼杀在摇篮中，让外界都无法知晓。

那，现在的HIDS有没有可能检测得到呢？按照目前的执行流来看，无论进程是否隐藏，它做任何操作都需要调用系统调用。而每个操作均可以分为几阶段：

  1. 进程调用系统调用,如`fork`
  2. 由用户态切换到内核态
  3. 内核态入口按照调用号去调用对应内核接口函数，如`sys_fork`
  4. 进入内核接口函数，如`sys_fork`
  5. 内核接口函数调用实际函数，进入实际函数,如`do_fork`
  6. 实际函数执行完，返回结果
  7. 内核接口函数返回结果
  8. 内核态入口返回结果，切换到用户态

`HIDS`在第3，4，7，8步挂钩，是可以检测到一些异常情况的。（3，8这两步启用`audit`框架，会自动挂钩，而4，7这两步一般是`eBPF`或驱动级使用`kprobe`来挂钩）

如创建一个进程，却发现获取不到当前进程的信息。但这种消息会淹没大量进程创建事件中，需要非常细心地筛选才能够找到。

不过，本人对`Linux`内核所知甚少，也许会有其它方法可以检测得到。

