Linux内核调试-ARM64

[ 程序员kevin](https://www.jianshu.com/u/1d7d7764c34d)关注赞赏支持

# Linux内核调试-ARM64

 **环境如下**

宿主机:

    
    
    Ubuntu20.04 
    5.13.0-40-generic  
    GNU gdb (Ubuntu 9.2-0ubuntu1~20.04.1) 9.2
    gdb-multiarch
    

qemu虚拟机:

    
    
    Ubuntu18.04
    4.15.0
    

## 安装qemu

    
    
    apt-get install qemu qemu-system qemu-user
    

## 安装交叉编译环境

    
    
    sudo apt install gcc-aarch64-linux-gnu
    

## 安装gdb-multiarch

    
    
    sudo apt install gdb-multiarch
    

## 下载并编译内核

    
    
    wget https://mirrors.edge.kernel.org/pub/linux/kernel/v4.x/linux-4.19.tar.xz
    tar -xvf linux-4.19.tar.xz
    cd linux-4.19
    export ARCH=arm64
    export CROSS_COPILE=aarch64-linux-gnu-
    make defconfig
    # 开启调试信息
    ./scripts/config -d COMPILE_TEST -e DEBUG_KERNEL -e DEBUG_INFO  
      
    # 开始编译
    # 如果编译报错参考谷歌/百度
    make -j8 ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-
    

## 制作根文件系统

    
    
    cd ..
    # 下载Ubuntu基础镜像
    wget  http://cdimage.ubuntu.com/ubuntu-base/releases/18.04.2/release/ubuntu-base-18.04.5-base-arm64.tar.gz
    
    # 制作虚拟磁盘
    mkdir rootfs
    fallocate -l 10G rootfs.img
    mkfs.ext4 rootfs.img
    sudo mount -t ext4 rootfs.img rootfs/
    sudo tar -xvzf ubuntu-base-18.04.5-base-i386.tar.gz -C rootfs/
    # 准备环境 
    sudo cp /usr/bin/qemu-aarch64-static rootfs/usr/bin/
    sudo cp /etc/resolv.conf rootfs/etc/resolv.conf
    sudo mount -t proc /proc rootfs/proc
    sudo mount -t sysfs /sys rootfs/sys
    sudo mount -o bind /dev rootfs/dev
    sudo mount -o bind /dev/pts rootfs/dev/pts
    sudo chroot rootfs
    
    # 安装必要软件
    apt-get update
    apt-get install systemd -y
    apt-get install sudo vim bash-completion -y
    apt-get install openssh-server net-tools ethtool ifupdown network-manager iputils-ping -y
    apt-get install rsyslog resolvconf udev -y
    
    # 系统配置
    adduser user
    adduser user sudo
    echo "user-pc" >/etc/hostname
    echo "127.0.0.1 localhost" >/etc/hosts
    echo "127.0.0.1 user-pcuser-pc">>/etc/hosts
    dpkg-reconfigure resolvconf
    dpkg-reconfigure tzdata
    cd /etc/systemd/system/getty.target.wants
    cp -d getty@tty1.service getty@ttyS0.service
    
    # 清理环境
    exit
    sudo umount rootfs/proc
    sudo umount rootfs/sys
    sudo umount rootfs/dev/pts
    sudo umount rootfs/dev
    sudo umount rootfs
    

## 开始调试

    
    
    # 使用-S -s参数启动内核
    qemu-system-aarch64 -S -s -machine virt,gic_version=3 -machine virtualization=true -cpu cortex-a57 -machine type=virt -nographic -smp 4 -m 4096 -kernel linux-4.19/arch/arm64/boot/Image -append "console=ttyAMA0 root=/dev/vda rw" -drive if=none,file=./rootfs.img,id=hd0,format=raw -device virtio-blk-device,drive=hd0  
    
    # 再开一个终端, 使用gdb连接qemu, 设置断点开始调试
    gdb-multiarch ./linux-4.19/vmlinux
    (gdb) target remote localhost:1234
    (gdb) b start_kernel
    (gdb) c
    (gdb) focus
    

## 使用Linux提供的gdb脚本的示例

    
    
    # 需要先设置add-auto-load-safe-path再启动gdb
    # 把path/to/linux-build替换成/linux-4.15目录的绝对路径
    echo add-auto-load-safe-path /path/to/linux-build >> ~/.gdbinit
    gdb ./linux-4.19/vmlinux 
    
    # 加载模块（以及主内核）符号:
    (gdb) lx-symbols
    
    # 查看内核的日志缓冲区:
    (gdb) lx-dmesg
    
    # 查看当前task struct结构体的字段（仅x86和arm64支持）:
    (gdb) p $lx_current().pid
    
    # 使用container_of查看更多hrtimers信息:
    (gdb) set $next = $lx_per_cpu("hrtimer_bases").clock_base[0].active.next
    (gdb) p *$container_of($next, "struct hrtimer", "node")
    

## 命令和辅助调试功能列表

    
    
    (gdb)  apropos lx
    function lx_current -- Return current task.
    function lx_module -- Find module by name and return the module variable.
    function lx_per_cpu -- Return per-cpu variable.
    function lx_task_by_pid -- Find Linux task by PID and return the task_struct variable.
    function lx_thread_info -- Calculate Linux thread_info from task variable.
    function lx_thread_info_by_pid -- Calculate Linux thread_info from task variable found by pid
    lx-cmdline --  Report the Linux Commandline used in the current kernel.
    lx-cpus -- List CPU status arrays
    lx-dmesg -- Print Linux kernel log buffer.
    lx-fdtdump -- Output Flattened Device Tree header and dump FDT blob to the filename
    lx-iomem -- Identify the IO memory resource locations defined by the kernel
    lx-ioports -- Identify the IO port resource locations defined by the kernel
    lx-list-check -- Verify a list consistency
    lx-lsmod -- List currently loaded modules.
    lx-mounts -- Report the VFS mounts of the current process namespace.
    lx-ps -- Dump Linux tasks.
    lx-symbols -- (Re-)load symbols of Linux kernel and currently loaded modules.
    lx-version --  Report the Linux Version of the current kernel.
    

可以通过“help <command-name>”或“help function <function-name>”命令
获取指定命令或指定调试功能的更多详细信息。

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [Linux下ARM程序的编译运行及调试](https://www.jianshu.com/p/dc8e263d6466)

Linux下ARM程序的编译运行及调试 环境：Ubuntu18.04 安装交叉编译环境arm-linux-gcc-...

[静水流深ylyang](https://www.jianshu.com/u/73ef54ebda4d)阅读 8,273评论 0赞 2

  * [Linux内核调试--使用qemu](https://www.jianshu.com/p/77765d57933d)

环境如下 宿主机: qemu虚拟机: 安装qemu 下载并编译内核 制作根文件系统 开始调试 使用Linux提供的...

[程序员kevin](https://www.jianshu.com/u/1d7d7764c34d)阅读 547评论 0赞 3

  * [Linux内核编译运行和调试](https://www.jianshu.com/p/bca7232dba47)

这一篇是关于linux内核源码下载，编译，运行，调试（搭建Qemu+gdb和Eclipse）的相关学习笔记。操作系...

[Amber_9](https://www.jianshu.com/u/8620dd072568)阅读 971评论 0赞 1

  * [ARM FVP(固定虚拟平台)Linux内核调试简明手册](https://www.jianshu.com/p/c0a9a4b9569d)

1\. 介绍 2. DS-5准备工作2.1 DS-5下载安装2.2 获取序列号 3. 调试官方Linux内核demo...

[古斟布衣](https://www.jianshu.com/u/0514b2e9f969)阅读 4,984评论 0赞 4

  * [Pwn环境搭建 （含Arm Pwn 环境）](https://www.jianshu.com/p/a7e2da50263e)

从零开始的CTF Pwn环境搭建 做一个合格的Pwn手需要一套标准的作业环境，就目前所接触到的环境和题目，将Pwn...

[WhiteYan](https://www.jianshu.com/u/1d54cd69bb7a)阅读 11,296评论 1赞 5

 