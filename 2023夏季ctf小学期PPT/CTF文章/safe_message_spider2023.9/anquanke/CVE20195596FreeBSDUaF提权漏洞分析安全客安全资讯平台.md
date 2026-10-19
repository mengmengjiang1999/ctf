# CVE-2019-5596 : FreeBSD UaF提权漏洞分析

阅读量 **338424**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-07-18 10:30:14

 **x**

##### 译文声明

本文是翻译文章，文章原作者 secfault-security，文章来源：secfault-security.com

原文地址：<https://secfault-security.com/blog/FreeBSD-SA-1902.fd.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0195407cf02d5af97b.jpg)

## 0x01 引言

2019年2月，`FreeBSD`项目发布了一份关于文件描述符处理可能存在漏洞的[报告](https://www.freebsd.org/security/advisories/FreeBSD-SA-19:02.fd.asc)。

类UNIX系统（如FreeBSD）允许通过`UNIX域套接字`将文件描述符发送给其他进程。例如，将文件访问权限传递给接收进程。

在内核中，文件描述符是用于间接引用存储文件对象的相关信息的C结构。例如，对vnode的引用（vnode描述文件系统的文件、文件类型或访问权限）。

如果使用UNIX域套接字将文件描述符发送到另一个进程，会发生这样的情况：对于接收进程，在内核内部会创建对此结构的引用。新文件描述符和原文件描述符是对同一文件对象的引用，因此将继承所有的信息。例如正常情况下进程的所有者无法写文件，如果存在此漏洞，将允许该进程对设备上的文件进行写操作。

该报告描述了`FreeBSD
12.0`在此机制中引入的一个错误。由于文件描述符信息是通过套接字发送的，因此发送方和接收方必须为该过程分配缓冲区。如果接收缓冲区不够大，FreeBSD内核会尝试关闭收到的文件描述符，以防止描述符泄漏给发送方。但是，当处理函数关闭文件描述符时，它无法将文件描述符中的引用释放到文件对象。这可能导致引用计数器换行。

该报告进一步指出，此错误可能导致本地权限提升，以获得root权限或越权逃逸。但是，报告的作者并没有提供概念验证。

本文抓住了这一点，并描述了Secfault Security的研究，以利用该bug提权获得root权限。

> 在下一节中，将分析漏洞，以便对错误类进行声明，并猜测可能的利用方法。  
>  之后，解决了漏洞触发问题。  
>  讨论了三种开发策略，同时讨论了其中两种方法失败的原因。  
>  倒数第二节中，讨论了工作漏洞原语。它介绍了（至少根据作者的知识）针对FreeBSD中这些漏洞的新开发技术。解决了exploit的稳定性问题。  
>  最后一部分进行总结，并指出了下一步的工作及挑战。  
>  此外，附录部分描述了加速漏洞测试的条件，包括测试设置和内核补丁。

应该提到的是，该漏洞被回迁到了FreeBSD 11开发分支中。目前，此分支中的漏洞也已修复，因此它不会出现在11.3版本中。

该问题指定的CVE为[CVE-2019-5596](https://nvd.nist.gov/vuln/detail/CVE-2019-5596)。

> 注意：所有引用的代码都指的是最初的FreeBSD
> 12版本附带的易受攻击的源代码。如果没有另外提及，可以在[此处](https://download.freebsd.org/ftp/releases/amd64/amd64/12.0-RELEASE/src.txz)找到源代码。

所有PoC代码都可以在[这里下载](https://secfault-security.com/stuff/heavy_cyber_weapon.tbz)。

## 0x02 漏洞分析

为寻找漏洞的第一个线索，可以从查看发布的FreeBSD
12工程分支修订版`r343790`中的补丁开始。该修订在报告中提到过。它可以在FreeBSD开源平台的实例：[FreeBSD’s Phrabricator
instance. ](https://reviews.freebsd.org/rS343790)中找到。此修订版的修复内容如下：

    
    
      1578  void
      1579  m_dispose_extcontrolm(struct mbuf *m)
      1580  {
      ...
      1606          while (nfd-- > 0) {
      1607          fd = *fds++;
      1608          error = fget(td, fd, &cap_no_rights,
      1609                       &fp);
    - 1610              if (error == 0)
    + 1610              if (error == 0) {
      1611                  fdclose(td, fp, fd);
    + 1612                  fdrop(fp, td);
    + 1613              }
      1614          }
      ...
      1621  }
    

仅在文件`uipc_syscalls.c`中的`m_dispose_extcontrol()`函数中的添加了一个调用。该函数缺少对宏`fdrop()`的调用引入了漏洞。很自然的会有一个问题：这个宏是干什么用的？

fdrop()有两个参数，`fp`和`td`。后者是当前线程的内核指针。前者是指向struct文件对象的指针，该对象在`sys/sys/file.h`的第170行中定义。

    
    
    170  struct file {
    171  void *f_data;    /* 文件描述符特定数据*/
    172  struct fileops    *f_ops;        /* 文件操作*/
    173      struct ucred    *f_cred;    /* 相关凭据 */
    174      struct vnode     *f_vnode;    /*NULL或适用的vnode */
    175      short    f_type;        /* 描述符类型*/
    176      short    f_vnread_flags;     /*(f)睡眠锁定*/
    177      volatile u_int    f_flag;        /* 见fcntl.h*/
    178      volatile u_int     f_count;    /* 参考计数 */
    179      /*
    180    * DTYPE_VNODE特定字段 
    181 */
    182      int    f_seqcount;    /* （a）顺序访问次数 */
    183      off_t    f_nextoff;    /* 下一个预期的读/写偏移量 */
    184      union {
    185          struct cdev_privdata *fvn_cdevpriv;
    186                  /* （d）cdev的私人数据 */
    187          struct fadvise_info *fvn_advice;
    188      } f_vnun;
    189      /*
    190    *DFLAG_SEEKABLE特定字段
    191    */
    192      off_t    f_offset;
    193      /*
    194    *强制访问控制信息
    195    */
    196      void    *f_label;    /*  MAC标签的占位符*/
    197  };
    

`fdrop()`本身是一个宏，它先调用`refcount_release()`。此函数自动将struct定义的第178行中的`f_count`减1，如果在调用函数之前`f_count`小于或等于1则返回1，否则返回0。
如果返回值为1，则宏调用`_fdrop()`函数。

`_fdrop()`在`sys/kern/kern_descrip.c`中定义。

    
    
    2943  int __noinline
    2944  _fdrop(struct file *fp, struct thread *td)
    2945  {
    2946      int error;
    2947  
    2948      if (fp->f_count != 0)
    2949          panic("fdrop: count %d", fp->f_count);
    2950      error = fo_close(fp, td);
    2951      atomic_subtract_int(&openfiles, 1);
    2952      crfree(fp->f_cred);
    2953      free(fp->f_advice, M_FADVISE);
    2954      uma_zfree(file_zone, fp);
    2955  
    2956      return (error);
    2957  }
    

有趣的是第2954行，这里调用了`uma_zfree()`函数。这是一个内核内置的函数，可以释放堆上已分配的块。内核堆管理的细节超出了本文的讨论范围。内核分配器的内部工作原理由argp和karl在[Phrack
#0x42, Phile
#0x08](http://phrack.org/issues/66/8.html#article)中讲解。另一个资源是McKusick等人编写的“The
Design and Implementation of the FreeBSD Operating System”一书。

对于本篇文章，以下有关内核堆的知识就足够了：FreeBSD内核的堆分配器允许定义“区域（zones）”。每个区域用于通过创建“桶（buckets）”来管理特定大小的页面块。要在内核堆上分配块，必须调用`uma_zalloc()`函数并使用指定区域的参数。该函数返回一个指向取自该区域的“桶”的指针。如果“桶”为空，则为该区域分配新页面并按区域的块大小切块。

例如，套接字区域用于分配大小为872字节的块，内核使用这些块来为套接字对象分配堆空间。还有一些匿名区域，如256，它们被内核中的malloc()调用。

可以使用命令`vmstat -z`查看所有可用区域，包括其统计信息。

当内核通过`uma_zalloc()`释放堆块时，释放的堆块将被放回到区域的”桶”中。后续调用`malloc()`或`uma_zalloc()`函数时，将以LIFO（后进先出）式从这些存储“桶”中获取块。

目前，有趣的见解是：

> uma_zfree()被file_zone调用  
>  file_zone指的是一个名为Files的用于存放struct文件类型的特殊区域  
>  如果另一个函数从Files分配一个struct文件，它最终会收到_fdrop()释放的指针

最新观察结果：在`sys/kern/kern_descrip.c`的fdclose()函数的第2384行调用了fdrop()。

    
    
    2376  fdclose(struct thread *td, struct file *fp, int idx)
    2377  {
    2378      struct filedesc *fdp = td->td_proc->p_fd;
    2379  
    2380      FILEDESC_XLOCK(fdp);
    2381      if (fdp->fd_ofiles[idx].fde_file == fp) {
    2382          fdfree(fdp, idx);
    2383          FILEDESC_XUNLOCK(fdp);
    2384          fdrop(fp, td);
    2385      } else
    2386          FILEDESC_XUNLOCK(fdp);
    2387  }
    

漏洞的描述中提到了引用计数器的包装，可以看到缺少第二个fdrop()会导致相应struct文件中的引用计数器`f_count`溢出。这可能会导致`use-after-free（UaF）`漏洞（Vitaly
Nikolenko的[https://ruxcon.org.au/assets/2016/slides/ruxcon2016-Vitaly.pdf，](https://ruxcon.org.au/assets/2016/slides/ruxcon2016-Vitaly.pdf%EF%BC%8C)
获得相似的漏洞示例）。

为了捋清这个问题，我们将研究`m_dispose_extcontrolm()`的确切目的和易受攻击路径。

## 0x03 漏洞触发路径

引入`m_dispose_extcontrolm()`函数的[目的](https://reviews.freebsd.org/D16561)，是为了使用UNIX域套接字发送文件描述符。发送文件描述符是由`sendmsg()`函数完成的，它允许将所谓的控制数据放入消息中（有关详细信息，请参阅手册页）。文件描述符是由控制消息类型`SCM_RIGHTS`负责发送的。

[很久以前就观察到](https://bugs.freebsd.org/bugzilla/show_bug.cgi?id=131876)，如果接收器的缓冲区太小，会导致文件描述符的泄漏。列出的漏洞条目表明，在接收缓冲区不够大的情况下，接收进程必须关闭已打开的文件描述符，因为并非所有描述符都被接收了。但是，由于接收到的文件描述符被处理并且创建了对文件对象的引用（如引言中所述），如果没有关闭文件描述符，这些文件描述符就有可能被泄露。

因此，引入了新函数`m_dispose_extcontrol()`解决这一问题。看`sys/kern/uipc_syscalls.c`中`kern_recvit()`的第998行进入判断后，在第1033行中的调用。

    
    
    902  int
    903  kern_recvit(struct thread *td, int s, struct msghdr *mp, enum uio_seg fromseg,
    904      struct mbuf **controlp)
    905  {
    ...
    998      if (mp->msg_control && controlp == NULL) {
    999  #ifdef COMPAT_OLDSOCK
    ...
    1018  #endif
    1019          ctlbuf = mp->msg_control;
    1020          len = mp->msg_controllen;
    1021          mp->msg_controllen = 0;
    1022          for (m = control; m != NULL && len >= m->m_len; m = m->m_next) {
    1023              if ((error = copyout(mtod(m, caddr_t), ctlbuf,
    1024                  m->m_len)) != 0)
    1025                  goto out;
    1026  
    1027              ctlbuf += m->m_len;
    1028              len -= m->m_len;
    1029              mp->msg_controllen += m->m_len;
    1030          }
    1031          if (m != NULL) {
    1032              mp->msg_flags |= MSG_CTRUNC;
    1033              m_dispose_extcontrolm(m);
    1034          }
    1035      }
    

可见，如果发送包含控制部分中的文件描述符的消息，则遵循此路径运行，但用于接收此消息的`recvmsg()`函数是不需要控制消息的。但是由于第1020行中的`len`将为0，而`m->m_len`更大，这将触发`m_dispose_controlm()`函数。因为在发送的消息中存在控制消息，程序不执行第1022行中的循环，而是分配给`m`非NULL的内容。

也就是说，要调用`m_dispose_constrolm()`，必须完成以下操作：

> 1.创建一个UNIX域套接字  
>  2.分配一个足够大的缓冲区，通过包含文件描述符的套接字发送消息  
>  3.分配一个不够大的缓冲区，通过包含文件描述符的套接字接收消息  
>  4.使用sendmsg（）发送消息  
>  5.使用recvmsg（）接收消息

现在，可以找到漏洞位置了。再次观察`m_dispose_extcontrolm()`的第1606行。

    
    
    1578  void
    1579  m_dispose_extcontrolm(struct mbuf *m)
    1580  {
    ...
    1606                  while (nfd-- > 0) {
    1607                      fd = *fds++;
    1608                      error = fget(td, fd, &cap_no_rights,
    1609                          &fp);
    1610                      if (error == 0)
    1611                          fdclose(td, fp, fd);
    1612                  }
    

有趣的部分是对`fget()`的调用。此函数最终会导致`fget_unlocked()`，它从文件描述符fd中提取指向struct文件对象的指针，将地址保存在指针fp中，并将struct文件对象的引用计数器`f_count`加1。但是，因为接收器使用自己的文件描述符保存对同一struct文件对象的引用，发送文件描述符时也会增加引用计数器的值，因此，计数器总共增加了2。

最后，第1611行中的`fdclose()`关闭了接收者的文件描述符，删除了对结构的引用，但没有考虑到调用fget()过程中f_count总共增加了2。

因此，该函数会产生一个可以将f_count增加1的语句。因为f_count的类型为u_int，其大小为32位，所以可以在合理的时间内溢出该变量。可以通过迭代增加f_count的语句，直到结果超过32位。变量将删除高于32位的所有位，再次回绕到0。

如果用这种方法将f_count溢出为1，则有可能实现UaF。为此，发送进程需要将两个文件描述符保存到同一个struct文件中，可以利用`dup()`函数复制一个文件描述符来实现这一操作。现在，如果其中一个文件描述符在溢出后关闭，则调用`fdrop()`。如上所述，此调用会看到`f_count`为1，释放struct文件对象。而此时，仍然可以通过第二个仍然打开的文件描述符引用释放的块。

现在捋清了基本的想法。因为这部分非常重要，所以应该更详细地描述如何触发漏洞，以及一些需要解决的问题。

首先，使用`open()`打开文件，并使用`dup()`复制文件描述符。这会使两个文件描述符引用相同的struct文件对象。因此，`f_count`是2。

接下来，如上所述，重复触发`m_dispose_extcontrolm()`以溢出f_count，最后再次将其设置为1。但这有一些问题。在这一过程中不可能发送任意数量的文件描述符。因为每个文件描述符都需要占用发送消息的空间，但内核内部只有有限的`mbufs`（构建消息以供进一步处理的空间）可用。

幸运的是，在调用`m_dispose_extcontrolm()`递减计数器前可以通过套接字多次发送文件描述符会多次增加引用计数器。

因此，UaF的准备需要一些时间。用于本研究的虚拟机，大概需要准备20分钟（2G内存，双核处理器）。

此外，重要的是要注意溢出必须使`f_count == 1`而不是0，因为如果f_count ==
0时调用fdrop()，会导致内核崩溃。这是因为`refcount_release()`仅通过检查计数器是否为0判断是否空闲，但_fdrop()会使f_count正好为0。如果计数器为负，`_fdrop`会使程序崩溃（通过将引用计数器增加到0xffffffff
= -1`二进制补码`，可以将此行为用作概念验证，因为在递减到0xffffffff之前，f_count将为0）。

将`f_count`调整为1后，其中一个文件描述符被“手动”关闭。调用_fdrop()使f_count递减为0后将触发`free`。使struct文件对象释放到Files区域的存储“桶”中。由于之前的`dup()`，第二个文件描述符仍引用已释放的struct文件对象，但因为对象本身被标记为无效,对第二个文件描述符来说，这个已释放的struct文件对象现在是无效的。

在这有另一个问题：struct文件的其他系统调用如`read()`或`write()`会用到`fget_unlocked()`函数。此函数将检查所使用的文件描述符是否小于最大有效文件描述符。因此，最好关闭第一个文件描述符，因为重复的文件描述符通常会更大。

至此，我们已经获得了一个引用无效结构文件的文件描述符。一旦这个struct文件的内存被另一个`open()`函数重用，我们的“悬空”的文件描述符将再次生效。但是，它将指向新打开的文件。“悬空”文件描述符可用于与新打开的文件描述符相同的操作。因为它们共享相同的struct文件，所以新打开的文件描述符的所有权限都由“悬挂”的文件描述符继承。例如，如果第一个文件是以只读方式打开而第二个文件是可写的，则可以使用悬空文件描述符写入新打开的文件。

将在下一节和之后的部分讲解如何利用它。

总结触发策略：

> 用open（）打开一个文件  
>  使用dup（）复制文件描述符  
>  通过调用m_dispose_extcontrol（）溢出f_count为1  
>  关闭第一个文件描述符并触发free  
>  再次调用open（）以从Files区域分配另一个struct文件，从而产生利用“悬空”的文件描述符的对象

可以在`trigger_uaf.c`中找到第一个概念验证。值得注意的是，程序关闭时会导致内核崩溃。这将在最终的漏洞利用中得到解决。感兴趣的读者可以在继续阅读之前尝试找出解决的方案。

## 0x04 漏洞利用策略

本节将讨论三种可能的漏洞利用策略，其中两种在研究期间失败了。

###  1.利用suid程序

最简单的策略之一是检查是否有可能触发UaF并在此之后执行suid程序(如passwd)，使“悬挂”的文件描述符得到root权限。

exploit需要将结构体对象完全放入Files区域的“桶”中。如果suid程序以可写方式打开root所拥有的文件（如master.passwd或libmap.conf），则可以从用户上下文写入此文件。

理论上这种策略是有效的。可以在文件`setuid_test_client.c`和`setuid_test_server.c`中找到概念验证（注意：编译的setuid_test_server.c和suid必须是root所有的）。

但是，找到这样一个程序非常难。标准安装中的大多数实用程序以只读方式打开可利用的文件或很快就关闭它们。

因此这种方法很早就被pass了。

###  2.内存损坏

另一种典型的办法是找到破坏内核内存的方法，以便执行用户提供的代码。这意味着可能要覆盖例如结构文件对象内的函数指针或可以由结构文件对象间接引用的另一个对象。

实际上，[fail0verflow](https://fail0verflow.com/blog/2017/ps4-namedobj-exploit/)使用了一种非常类似的技术,利用了基于FreeBSD 9的PlayStation 4操作系统中的漏洞。他们打开了一个kqueue-一个监视内核事件的FreeBSD机制。

kqueue-files利用结构体中的`f_data`指针来管理kqueue。堆空间是从其中一个匿名区域分配的。因此，可以使用`ioctl()`对该区域进行堆喷射，并覆盖文中描述的函数指针。

但是，fail0verflow使用的漏洞与本研究中使用的漏洞之间存在显着差异：前者允许任意free，例如`f_data`指针。后者只允许释放struct文件。当内核清理所有可用的struct字段和指针时，不可能使用fail0verflow的代码。

在研究期间，对所有其他可能依赖于struct文件的对象都及进行了尝试，但是由于刚才所说的原因，无法通过内存损坏来利用漏洞。

###  3.在write()期间交换文件对象

这是第一种方法的变体。

一旦用户尝试通过文件描述符写入，FreeBSD内核就会检查文件是否可写。如果检查通过，则准备执行写操作。这创建了一个基于`Time-of-Check-Time-of-Use（TOCTOU）`条件竞争的方案。

思路如下：传递的检查和写入操作之间的时间窗口会产生条件竞争。可以利用漏洞释放struct文件对象，并立即打开另一个只读文件。由于此时写入检查已经完成，但struct文件被替换被，最终会在只读文件上执行写入操作。

由于此策略最终成功用于利用UaF获取root权限，因此将在下一节中详细介绍。

值得一提的是，Google Project Zero的Jann Horn在Linux中利用了相似的漏洞并使用了类似的方法。2016年在Project
Zero上发布的[相关文章](https://bugs.chromium.org/p/project-zero/issues/detail?id=808)。

## 0x05 提权

如上一节所述，基于Time-of-Check-Time-of-Use（TOCTOU）条件竞争的攻击：对用户可写的文件调用write()。系统调用首先检查文件描述符引用的文件是否确实可由用户写入，如果没有写权限，将导致系统错误。检查通过后，将触发UaF漏洞，之后普通用户可以打开root所拥有的只读文件。

检查的工作方式如下：`write()`函数将调用在`sys/kern/sys_generic.c`中的内核函数`sys_write()`。随后，调用同一文件中的`kern_writev()`，这会调用`fget_write()`函数。后者在`sys/kern/kern_descrip.c`中定义。此函数用于检索文件描述符的struct文件对象，并检查是否可写。

为此，该函数会调用`_fget()`函数。

    
    
    2716  static __inline int
    2717  _fget(struct thread *td, int fd, struct file **fpp, int flags,
    2718      cap_rights_t *needrightsp, seq_t *seqp)
    2719  {
    2720      struct filedesc *fdp;
    2721      struct file *fp;
    2722      int error;
    2723  
    2724      *fpp = NULL;
    2725      fdp = td->td_proc->p_fd;
    2726      error = fget_unlocked(fdp, fd, needrightsp, &fp, seqp);
    ...
    2738      switch (flags) {
    2739      case FREAD:
    2740      case FWRITE:
    2741          if ((fp->f_flag & flags) == 0)
    2742              error = EBADF;
    2743          break;
    ...
    2753      }
    2754  
    2755      if (error != 0) {
    2756          fdrop(fp, td);
    2757          return (error);
    2758      }
    2759  
    2760      *fpp = fp;
    2761      return (0);
    2762  }
    

请看第2741行的检查函数，`f_flag`是在第一次调用open()时设置的struct文件中的一个字段。调用write()会检查`FWRITE`位。因此，仅当用户对打开的文件具有写权限时才能设置该位。

应注意：假设此时已经准备好UaF，即f_count变量溢出为1，且调用fget_unlocked()将f_count增加到了2。计数器将在调用write()结束时再次减少到1。

但是，如果通过检查，则可以通过UaF和另一个open()操作将文件对象变换为只读文件。之后将能在第二个文件中写入。可以在`test_rd_only_write.c`中找到第一个概念验证（请注意，如文件开头的注释中所述，该测试需要内核补丁;详细信息，请参阅附录）。

检查通过后，`kern_writev()`将调用同一文件中的`dofilewrite（）`。

    
    
    545  static int
    546  dofilewrite(struct thread *td, int fd, struct file *fp, struct uio *auio,
    547      off_t offset, int flags)
    548  {
    ...
    564      if (fp->f_type == DTYPE_VNODE &&
    565          (fp->f_vnread_flags & FDEVFS_VNODE) == 0)
    566          bwillwrite();
    567      if ((error = fo_write(fp, auio, td->td_ucred, flags, td))) {
    ...
    576          }
    577      }
    ...
    587  }
    

这个函数有两个有趣的函数调用。第一个是第567行中的`fo_write()`。该函数最终会执行写操作。也就是说，struct文件变换必须在调用此函数之前(或者在fo_write()内部的后续函数调用中，这不是必需的)。

不过，条件竞争过程非常紧张，如果其他条件不满足也难以成功。此外，必须一次就成功，否则内核将会崩溃。

假设在通过检查时`f_count`为2。此时必须调用`close()`两次。但是如果检查尚未通过或者write()已经完成，f_count仍然是1。`_fdrop（）`将判断引用计数器正好为0，但是调用两次`close()`会使函数将引用计数器解释为负数。错误的判断将导致程序崩溃。

Jann
Horn通过编写FUSE文件系统来延迟Linux的内核操作，该系统延迟能够帮助赢得竞争条件，提高写入操作的成功率。在标准的FreeBSD中由于无法加载FUSE（并且可供相应用户使用），是不可能实现的。

在第566行中对`bwillwrite()`的调用创造了条件。此函数和`buf_dirty_count_severe()`函数在`sys/kern/vfs_bio.c`中定义。

    
    
    2564  bwillwrite(void)
    2565  {
    2566  
    2567      if (buf_dirty_count_severe()) {
    2568          mtx_lock(&bdirtylock);
    2569          while (buf_dirty_count_severe()) {
    2570              bdirtywait = 1;
    2571              msleep(&bdirtywait, &bdirtylock, (PRIBIO + 4),
    2572                  "flswai", 0);
    2573          }
    2574          mtx_unlock(&bdirtylock);
    2575      }
    2576  }
    2577  
    2578  /*
    2579   * Return true if we have too many dirty buffers.
    2580   */
    2581  int
    2582  buf_dirty_count_severe(void)
    2583  {
    2584  
    2585      return (!BIT_EMPTY(BUF_DOMAINS, &bdhidirty));
    2586  }
    

最值得注意的是第2571行的`msleep()`函数。函数手册中提到，sleep()函数会使线程在没有超时的情况下进入休眠状态。通过查看唤醒的通道`bdirtywait`可以发现,线程将被`vfs_bio.c`中`buf_daemon()`调用的`bdirtywakeup()`函数唤醒。

调用`msleep()`的条件和`buf_daemon()`的目的是关联的：如果内核持有太多脏缓冲区（即等待写入的缓冲区），则`buf_dirty_count_severe()`返回1并且唤醒`buf_daemon()`函数执行刷新操作以减少计数的值。之后，调用`bdirtywakeup()`来唤醒在第2571行等待的所有写操作。

有两个内核变量用作监视是否有`lodirtybuffers`和`hidirtybuffers`这两个脏缓冲区的标志。这些变量是在程序启动时设置的，取决于RAM（调用sysctl
vfs.hidirtybuffers和sysctl
vfs.lodirtybuffers以显示特定系统的值）。如果脏缓冲区的数量大于`hidirtybuffers`，则设置`bdhidirty`位（第2585行）同时`buf_dirty_count_severe`返回1，从而调用`msleep()`。

因此，需要一种快速增加脏缓冲区数量的技术。经过尝试后，很快就找到了一种简单的方法：用exploit打开大量的引用同一个文件的文件流。但是，在使用fopen()打开文件流后，在下次调用fopen()之前，应当先取消相应文件的链接。如果exploit尝试并行写入这些文件流，脏缓冲区的数量就会增加。

可以在`test_dirty.c`中找到此技术的演示。

目前的exploit的工作原理如下：一旦脏缓冲区的数量足够，另一个线程就会获得一个信号，尝试写入先前打开的随机的可写文件。同时，向另一个线程发送触发UaF的信号并打开只读文件。通过关闭用于准备UaF场景的文件描述符和重复的场景（请记住此时`f_count`等于2）来触发UaF。现在打开只读文件将导致struct文件对象的转换。

为了提高exploit赢得条件竞争的概率，尽可能让UaF触发线程和写入线程在不同的核上运行，并且让UaF延迟几微秒触发。如前文所述，如果写入线程的操作没有完成，那么exploit可能会导致内核崩溃，因为free之后的use发生得太快，`_fdrop()`会触发崩溃。

可以在`arbitary_file_write`中找到任意写入的概念验证。应该注意，`hammer`线程是同步的。否则继续创建线程并触发漏洞会导致攻击不可靠。此外，同步写入会更快地触发`msleep()`条件。  
完成最终的exploit还有两个挑战：获取root权限并防止内核崩溃。

后者可以通过使用导致参考计数器溢出的语句来实现。崩溃的原因是程序试图关闭它认为打开的所有文件描述符。然而，UaF使参考计数器很小，导致前面提到的`_fdrop()`中的判断失败了。

因为在写操作时被利用的struct文件的`f_count`被UaF和后面的open()置为1，所以在最后调用`fdrop()`时`write()`将再次释放文件对象。因此，需要第三次调用`open()`来获取损坏的struct文件的文件描述符。之后，引用计数器增加语句可增加f_count的值，防止内核崩溃。

kingcope于2005年发布了[FreeBSD root exploit](https://www.exploit-db.com/exploits/1230)，使权限提升变得很容易，该文件将导致写入`/etc/libmap.conf`文件。如果程序启动，此配置文件可用于挂钩加载的动态库。因此，该exploit创建了一个动态库，它将`/bin/sh`复制到另一个文件并为该副本设置suid位。钩子库是`libutil`，可以由su调用。因此，用户对su的调用将导致`/bin/sh`副本的执行，实现sudi（对于其他测试系统，可能需要调分支、线程和文件的值。此exploit中提供的数字适用于具有2GB内存和双核的VM系统）。

最终的exploit可以在`heavy_cyber_weapon.sh`中找到。

## 0x06 结论及下步打算

本文介绍了在FreeBSD中利用的一个简单但易被忽视的漏洞。

虽然UaF触发器的开发非常简单，但研究利用漏洞的方法需要付出很多的努力。写这篇文章的主要原因是研究内核代码的合理工程（the reasonable good
engineering of the kernel code ）以及FreeBSD漏洞write-up的稀缺。作者希望这篇文章对以后的研究工作做出贡献，或者在他们自己的研究中确实有所帮助。

据本文作者所知，本文首次描述了此漏洞的工作原理，并首次描述了所需的技术。

在可以在Files区域触发UaF的类似情况下，开发技术应该派上用场。应该留存没有做大更改的内核代码。

此外，在其他安装程序甚至CPU架构使用此exploit时，逻辑漏洞的优势就突显出来了。该漏洞已在ARM处理器上成功测试。

最后，应该提一下下步打算：

>
> 1.目前，漏洞利用技术仅适用于UFS。虽然这是过去的标准文件系统，现在ZFS被FreeBSD安装程序广泛运用。但是由于脏缓冲机制不同（如果它存在的话），该技术并不适用于ZFS。因此，不会触发msleep()，这会导致竞争条件不可靠。必须找到另一种延迟机制。  
>  2.通过执行大量的并行写入来创建脏缓冲区从而使竞争条件可靠的代码不够优化。也许有另一种方法来创建写延迟，但这是目前为止最快的方法。  
>
> 3.可能有完全不同的方式来利用此漏洞。例如，可以考虑欺骗suid程序从不想读取的文件中读取（例如，从用户提供的文件而不是/etc/pam.d/su中读取su）。

## 0x00 附录：环境设置

为了测试和调试漏洞和bug，选择了[VirtualBox](https://www.virtualbox.org/)。此外，可以应用一些内核补丁来加速uAf条件的准备。

###  1.VirtualBox设置

目前已经有可以为FreeBSD内核调试创建测试环境的指导书，例如[argp](https://argp.github.io/2009/07/02/freebsd-kernel-debugging/)。  
这是指南的最新更新，以及设置的说明。

> 1.从这里获取FreeBSD-12-RELEASE disc1  
>  2.将所有内容安装到新的VirtualBox VM中
>

>> 使用UFS  
>  暂时不要施加任何硬化  
>  安装源（/usr/src)、SSH和调试功能
>
> 3.安装后重新启动，不要忘记“弹出”光盘映像  
>  4.配置SSH、用户等  
>  5.使用pkg安装gdb：`pkg install gdb`  
>  6.按以下方式编译自定义内核
>

>> `cd /usr/src/sys/amd64/conf`  
>  创建一个名为DEBUG的新文件，并添加以下内容
>>  
>>  
>>     include GENERIC

>>     ident DEBUG

>>     makeoptions DEBUG=-g

>>     options DDB

>>     options GDB

>>     options KDB

>>     - Create /etc/make.conf with CFLAGS=-pipe -O0for the content

>>     - Change all-O2to-O0in /usr/src/sys/conf/kern.pre.mk

>>     - Execute cd /usr/src

>>     - Execute make buildkernel

>>     -j8 KERNCONF=DEBUG

>>     - Execute make installkernel

>>     KERNCONF=DEBUG

>>     - Execute reboot`

>>  
>
> 7.执行`sysctl debug.kdb.enter = 1`以检查是否可以进入调试模式
>

>> 注意，调试器在VM窗口中启动，而不是在SSH会话中启动

>
> 8.克隆机器，使用专家模式创建链接克隆，然后保留其余部分  
>  9.克隆机器是目标，而原始机器是调试器主机  
>  10.对于目标，在VM设置中激活串口COM1作为主机管道
>

>> 请勿选中与管道连接的框  
>  路径可以是`/tmp/fbsdpipe`
>
> 11.对调试器执行相同操作
>

>> 选中与管道连接的框，使用与目标相同的路径

>
> 12首先启动目标主机  
>  13.如果需要，更改主机名  
>  14.在`/boot/device.hints`中将`hint.uart.0.flags`更改为0x90  
>  15.重新启动目标  
>  16.启动调试器  
>  17.切换到目标中的调试模式并在调试器会话中执行gdb  
>  18.在调试器中执行：
>  
>  
>     cd /usr/obj/usr/src/amd64.amd64/sys/DEBUG
>     kgdb -b 38400 kernel.debug
>     kgdb> target remote / dev / cuau0
>  
>
> 19.应该看到kgdb中目标的调试器会话

###  2.内核补丁

为了简化漏洞利用测试并避免每次运行等待很长时间，`m_dispose_extcontrolm()`中的补丁是一种可能的解决方案。需要在函数末尾添加以下内容：

    
    
    1618    }
    1619    if (fp->f_count == 1234) fp->f_count = 0xfffffff2;
    1620  }
    

这种方法还需要替换所有代码文件中的for循环，使用以下代码准备UaF（基于减少i的上限并且一次只发送一个文件描述符）：

    
    
    for (i = 0; i < 1232; i++)
        send_recv(fd, sv, 0x1);
    

在研究期间，使用另一个内核补丁，在调用`bwillwrite()`之后提供了很长的延迟。在`sys/kern/sys_generic.c`中调用函数后添加以下判断条件：

    
    
      if (fp->f_type == DTYPE_VNODE &&
    565      (fp->f_vnread_flags & FDEVFS_VNODE) == 0) {
    566      bwillwrite();
    567      if (fd == 16000)
    568          pause("", 100);
    569  }
    

需要在所有代码文件中改变对open（）的调用为一下内容，以便打开临时文件：

    
    
    do {
      if ((fd = open_tmp()) == -1) {
        perror("open_tmp");
        exit(1);
      }
    } while(fd != 16000);
    

`test_rd_only_write.c`还需要使用最后一个内核补丁。`sys/kern/sys_generic`中,在函数`kern_writev()`调用`fget_write()`之后，需要以下补丁：

    
    
    491  if (fd == 22)
    492    __asm__("int3");
    

这产生了一个断点，允许更换struct文件对象，如概念验证所述。

本文翻译自secfault-security.com [原文链接](https://secfault-security.com/blog/FreeBSD-SA-1902.fd.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **fbird666** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/182014](/post/id/182014)

安全客 - 有思想的安全新媒体

本文转载自: [secfault-security.com](https://secfault-security.com/blog/FreeBSD-SA-1902.fd.html)

如若转载,请注明出处： <https://secfault-security.com/blog/FreeBSD-SA-1902.fd.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [系统安全](/tag/系统安全)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhimg.com/t014755f870454f364b.png) fbird666

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

