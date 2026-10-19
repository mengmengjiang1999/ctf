# 前言

近日想研究一下arm架构下的linux kernel。文章记录了一下qemu虚拟化启动linux kernel与linux
kernel的交叉编译与动态调试。

# 0x1 qemu手动编译安装

安装ninja

    
    
    apt install re2c
    git clone https://github.com/ninja-build/ninja.git && cd ninja
    ./configure.py --bootstrap
    sudo cp ninja /usr/bin/
    
    依赖解决
    sudo apt-get install libglib2.0-dev
    sudo apt-get install libpixman-1-dev
    
    编译安装qemu
    wget https://download.qemu.org/qemu-7.1.0-rc2.tar.xz
    tar -xf qemu-7.1.0-rc2.tar.xz
    cd qemu-7.1.0-rc2
    ./configure
    make -j8
    编译后的产物在build文件夹
    

之后将build目录添加进 PATH  
![image.png](https://image.3001.net/images/20220921/1663742453_632ab1f58897c06c7e710.png!small)  
手动编译的qemu相较于通过apt安装的qemu支持更多的虚拟化机器类型。Apt安装的qemu的版本相对较低很多。

# 0x2 linux Kernel编译

安装依赖

    
    
    sudo apt install libncurses-dev
    sudo apt install bison flex
    

linux kernel获取与编译

    
    
    git clone https://github.com/torvalds/linux
    
    切换指定分支后通过qemu配置生成 .config
    make ARCH=arm vexpress_defconfig
    
    编译内核
    make ARCH=arm CROSS_COMPILE=arm-linux-gnueabi- zImage
    
    make ARCH=arm CROSS_COMPILE=arm-linux-gnueabi- all
    

![image.png](https://image.3001.net/images/20220921/1663742516_632ab234c86e92f8e78dd.png!small)

# 0x3 busybox文件系统制作

![image.png](https://image.3001.net/images/20220921/1663742544_632ab2505d2f5520b78e6.png!small)

    
    
    make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- menuconfig
    

设置生成静态可执行文件  
Setting->Build Options->  
![image.png](https://image.3001.net/images/20220921/1663742575_632ab26f3436e5d45f100.png!small)

    
    
    #busybox编译与安装
    make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- 
    
    make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- install
    

rootfs镜像制作

    
    
    #进入busybox编译目录的上级目录 建立目录结构 
    cd ../
    mkdir rootfs
    mkdir rootfs/proc rootfs/sys rootfs/dev rootfs/etc rootfs/tmp
    cp -a ../busybox-1.35.0/examples/bootfloppy/etc/* rootfs/etc
    dd if=/dev/zero of=rootfs.ext3 bs=1M count=32
    mkfs.ext3 rootfs.ext3
    mkdir -p tmpfs
    sudo mount -o loop rootfs.ext3 tmpfs
    sudo cp -r rootfs/* tmpfs/
    sudo umount tmpfs
    

# 0x4 qemu-system-arm 启动Kernel

启动时需要添加一下 dtb

    
    
    qemu-system-arm -M vexpress-a9 -dtb arch/arm/boot/dts/vexpress-v2p-ca9.dtb -kernel arch/arm/boot/zImage -nographic -sd rootfs.ext3 -append "root=/dev/mmcblk0 console=ttyAMA0"
    

![image.png](https://image.3001.net/images/20220921/1663742663_632ab2c7e63cac1dced2f.png!small)

# 0x5 qemu-system-arm 调试Kernel

    
    
    qemu-system-arm -M vexpress-a9 -dtb arch/arm/boot/dts/vexpress-v2p-ca9.dtb -kernel arch/arm/boot/zImage -nographic -sd rootfs.ext3 -append "root=/dev/mmcblk0 console=ttyAMA0" -s -S -gdb tcp::1234
    

由于是arm架构使用了gdb插件 gef

    
    
    gef➤  set architecture arm
    gef➤  file vmlinux
    gef➤  target remote localhost:1234
    

由于qemu启动未挂载rootfs，故而gdb会停在mount过程  
直接一个continue 一跑到底，看到了kernel启动过程的函数调用栈  
![image.png](https://image.3001.net/images/20220921/1663742695_632ab2e7a01bc241828bd.png!small)

# 0x6 arm 架构的Kernel启动流程

依据gdb中的trace对每个函数进行定位。当前使用的是kernel源码中的arch/arm 架构

## ret_from_fork

arch\arm\kernel\entry-common.S  
![image.png](https://image.3001.net/images/20220921/1663742718_632ab2fe4cacf85ac5d43.png!small)  
Gdb看到编译产物的汇编代码和源码中略有区别，直接向pc赋值跳转到Kernel_init  
![image.png](https://image.3001.net/images/20220921/1663742753_632ab3212986394152e77.png!small)

## Kernel_init

首先下个断点，然后重新开始qemu联调  
gef➤ b kernel_init  
gef➤ c  
![image.png](https://image.3001.net/images/20220921/1663742764_632ab32c30f611dc76e22.png!small)  
函数位置 init\main.c  
![image.png](https://image.3001.net/images/20220921/1663742773_632ab335922e363b2fa7b.png!small)  
直接进入kernel_init_freeable执行

## Kernel_init_freeable

函数位置init\main.c  
通过TRACE确认 之后要执行prepare_namespace  
![image.png](https://image.3001.net/images/20220921/1663742789_632ab3454fe0e6b59518c.png!small)

## prepare_namespace

函数位置 init\do_mounts.c  
依据逻辑校验判定，开始执行mount挂载目录  
![image.png](https://image.3001.net/images/20220921/1663742826_632ab36a940400d1145de.png!small)

initrd_load  
![image.png](https://image.3001.net/images/20220921/1663742837_632ab375b501e88145414.png!small)

## mount_root

Linux中的源码

![image.png](https://image.3001.net/images/20220921/1663742849_632ab381d9b970df09913.png!small)

挂载ext3 文件体统后，进入 ksys_chroot  
![image.png](https://image.3001.net/images/20220921/1663742857_632ab3895f8bf506c268c.png!small)  
![image.png](https://image.3001.net/images/20220921/1663742864_632ab390228a3ba760800.png!small)

之后跳转 load_default_elevator_module

校验 /dev/console  
![image.png](https://image.3001.net/images/20220921/1663742875_632ab39b5f9300c29a05e.png!small)  
校验 ramdisk_execute_command 成功后 进行prepare_namespace  
![image.png](https://image.3001.net/images/20220921/1663742882_632ab3a22e7da606e7e80.png!small)  
Ksys的挂载与chroot  
![image.png](https://image.3001.net/images/20220921/1663742887_632ab3a72ef2aa28421da.png!small)

测试初始化  
![image.png](https://image.3001.net/images/20220921/1663742893_632ab3adaae68ad47ae9f.png!small)

## 终端的命令执行

最后定位到了 do_idle函数循环执行初始化任务，开启/bin/sh 并且执行linux命令  
![image.png](https://image.3001.net/images/20220921/1663742904_632ab3b853c6b89b9e98e.png!small)

* * *

本文作者：Jambolt@涂鸦智能安全实验室

