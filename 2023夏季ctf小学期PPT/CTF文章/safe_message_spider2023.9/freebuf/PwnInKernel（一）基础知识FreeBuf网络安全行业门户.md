## Kernel Pwn In CTF

 **简单分析一下 CTF Kernel Pwn 题目的形式，以 2017 CISCN babydrive 为例。**

 ****先对文件包解压 ****

    
    
    ➜  example ls
     babydriver.tar
     ➜  example file babydriver.tar 
     babydriver.tar: POSIX tar archive
     ➜  example tar -xvf babydriver.tar 
     boot.sh
     bzImage
     rootfs.cpio
     ➜  example ls
     babydriver.tar  boot.sh  bzImage  rootfs.cpio

得到 boot.sh，bzImage，rootfs.cpio 三个文件

### boot.sh

    
    
     ➜  example cat -n boot.sh
          1  #!/bin/bash
          2  qemu-system-x86_64 \
          3  -initrd rootfs.cpio \
          4  -kernel bzImage \
          5  -append 'console=ttyS0 root=/dev/ram oops=panic panic=1' \
          6  -enable-kvm \
          7  -monitor /dev/null \
          8  -m 64M \
          9  --nographic  \
         10  -smp cores=1,threads=1 \
         11  -cpu kvm64,+smep
    

boot.sh 文件是用来启动这个程序的，调用 qemu 来加载 rootfs.cpio 与 bzImage 运行起来

上面的参数都是 qemu 的参数

    
    
     -initrd rootfs.cpio，使用 rootfs.cpio 作为内核启动的文件系统
     -kernel bzImage，使用 bzImage 作为 kernel 映像
     -cpu kvm64,+smep，设置 CPU 的安全选项，这里开启了 smep
     -m 64M，设置虚拟 RAM 为 64M，默认为 128M
    

### bzImage

    
    
     ➜  example file bzImage       
     bzImage: Linux kernel x86 boot executable bzImage, version 4.4.72 (atum@ubuntu) #1 SMP Thu Jun 15 19:52:50 PDT 2017, RO-rootFS, swap_dev 0x6, Normal VGA
    

bzImage 是经压缩过的 linux 内核文件

### rootfs.cpio

    
    
     ➜  example file rootfs.cpio
     rootfs.cpio: gzip compressed data, last modified: Tue Jul  4 08:39:15 2017, max compression, from Unix
    

这是一个 linux 内核文件系统压缩包，我们可以对其解压并重新压缩，从而修改这个系统的文件

新建一个文件夹来解压

    
    
     ➜  example mkdir fs && cd fs
     ➜  fs cp ../rootfs.cpio ./rootfs.cpio.gz
     ➜  fs gunzip ./rootfs.cpio.gz
     ➜  fs cpio -idmv < rootfs.cpio 
     .
     etc
     etc/init.d
     etc/passwd
     etc/group
     bin
     ......
     linuxrc
     home
     home/ctf
     5556 blocks
     ➜  fs ll                  
     total 2.8M
     drwxrwxr-x 2 mask mask 4.0K 1 月  20 12:16 bin
     drwxrwxr-x 3 mask mask 4.0K 1 月  20 12:16 etc
     drwxrwxr-x 3 mask mask 4.0K 1 月  20 12:16 home
     -rwxrwxr-x 1 mask mask  396 6 月  16  2017 init
     drwxr-xr-x 3 mask mask 4.0K 1 月  20 12:16 lib
     lrwxrwxrwx 1 mask mask   11 1 月  20 12:16 linuxrc -> bin/busybox
     drwxrwxr-x 2 mask mask 4.0K 6 月  15  2017 proc
     -rwxrwxr-x 1 mask mask 2.8M 1 月  20 12:15 rootfs.cpio
     drwxrwxr-x 2 mask mask 4.0K 1 月  20 12:16 sbin
     drwxrwxr-x 2 mask mask 4.0K 6 月  15  2017 sys
     drwxrwxr-x 2 mask mask 4.0K 6 月  15  2017 tmp
     drwxrwxr-x 4 mask mask 4.0K 1 月  20 12:16 usr
    

这些就是运行起来后这个系统拥有的文件，查看这个 init 文件

    
    
     ➜  fs cat -n ./init           
          1  #!/bin/sh
          2   
          3  mount -t proc none /proc
          4  mount -t sysfs none /sys
          5  mount -t devtmpfs devtmpfs /dev
          6  chown root:root flag
          7  chmod 400 flag
          8  exec 0</dev/console
          9  exec 1>/dev/console
         10  exec 2>/dev/console
         11
         12  insmod /lib/modules/4.4.72/babydriver.ko
         13  chmod 777 /dev/babydev
         14  echo -e "\nBoot took $(cut -d' ' -f1 /proc/uptime) seconds\n"
         15  setsid cttyhack setuidgid 1000 sh
         16
         17  umount /proc
         18  umount /sys
         19  poweroff -d 0  -f
    

看到第 12 行的 insmod /lib/modules/4.4.72/babydriver.ko，意味着要调试这个 ko 文件，使用 IDA
对其进行分析，利用漏洞

对此文件系统进行打包也是要在这个目录下进行

    
    
     ➜  fs find . | cpio -o --format=newc > rootfs.cpio
     cpio: File ./rootfs.cpio grew, 43008 new bytes not copied
     5640 blocks
    

### vmlinux

有些题目会给 vmlinux 这个文件，这是编译出来的最原始的内核文件，未压缩的，是个 ELF 形式，方便找 gadget

可以使用一个工具来从 bzImage 中导出 vmlinux，[extract-vmlinux](https://raw.githubusercontent.com/torvalds/linux/master/scripts/extract-vmlinux)

    
    
    ➜  example ./extarct-vmlinux ./bzImage > vmlinux
    ➜  example file bzImage                                
    bzImage: Linux kernel x86 boot executable bzImage, version 4.4.72 (atum@ubuntu) #1 SMP Thu Jun 15 19:52:50 PDT 2017, RO-rootFS, swap_dev 0x6, Normal VGA
    ➜  example file vmlinux 
    vmlinux: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, BuildID[sha1]=e993ea9809ee28d059537a0d5e866794f27e33b4, stripped
    

### exploit

Kernel Pwn 就是找出内核模块中的漏洞，然后写一个 C
语言程序，放入文件系统中打包，重新运行取来，此时用户一般都是普通用户，运行程序调用此模块的功能利用漏洞，从而提升权限到 root 用户，读取 flag

    
    
    / $ ls
    bin          exp          lib          root         sys
    dev          home         linuxrc      rootfs.cpio  tmp
    etc          init         proc         sbin         usr
    / $ whoami
    ctf
    / $ ./exp 
    [   18.277799] device open
    [   18.278768] device open
    [   18.279760] alloc done
    [   18.280706] device release
    / # whoami
    root
    

比赛时一般是上传 C 语言程序的 base64 编码到服务器，然后运行

## Kernel Pwn Debug

要对内核模块进行调试，在启动脚本中加入

    
    
    -gdb tcp::1234
    

然后使用 gdb 连接

    
    
    gdb -q -ex "target remote localhost:1234"
    

如果显示 Remote 'g' packet reply is too long 一长串数字，要设置一下架构

    
    
    gdb -q -ex "set architecture i386:x86-64:intel" -ex "target remote localhost:1234"
    

要调试内核模块，可以先查看内核加载地址，在/sys/module/中是加载的各个模块的信息

    
    
    / $ cd sys/module/                                         
    /sys/module $ ls                                           
    8250                ipv6                scsi_mod           
    acpi                kdb                 sg                 
    acpi_cpufreq        kernel              spurious           
    acpiphp             keyboard            sr_mod             
    apparmor            kgdb_nmi            suspend            
    ata_generic         kgdboc              sysrq              
    ata_piix            libata              tcp_cubic          
    babydriver          loop                thermal            
    battery             md_mod              tpm                
    block               module              tpm_tis            
    core                mousedev            uhci_hcd           
    cpuidle             netpoll             uinput             
    debug_core          pata_sis            usbcore            
    dm_mod              pcc_cpufreq         virtio_balloon     
    dns_resolver        pci_hotplug         virtio_blk         
    dynamic_debug       pci_slot            virtio_mmio        
    edd                 pcie_aspm           virtio_net         
    efivars             pciehp              virtio_pci         
    ehci_hcd            ppp_generic         vt                 
    elants_i2c          printk              workqueue          
    ext4                processor           xen_acpi_processor 
    firmware_class      pstore              xen_blkfront       
    fuse                rcupdate            xen_netfront       
    i8042               rcutree             xhci_hcd           
    ima                 rfkill              xz_dec             
    intel_idle          rng_core            zswap
    

获取 babydrive 模块的加载地址

    
    
    /sys/module $ cd babydriver/                            
    /sys/module/babydriver $ ls                             
    coresize    initsize    notes       sections    taint   
    holders     initstate   refcnt      srcversion  uevent  
    /sys/module/babydriver $ cd sections/                   
    /sys/module/babydriver/sections $ grep 0 .text          
    0xffffffffc0000000
    

在 gdb 中载入符号信息，就可以对内核模块进行下断调试

    
    
    pwndbg> add-symbol-file ./fs/lib/modules/4.4.72/babydriver.ko 0xffffffffc00000
    00
    add symbol table from file "./fs/lib/modules/4.4.72/babydriver.ko" at
            .text_addr = 0xffffffffc0000000
    Reading symbols from ./fs/lib/modules/4.4.72/babydriver.ko...done.
    pwndbg> b*babyopen 
    Breakpoint 1 at 0xffffffffc0000030: file /home/atum/PWN/my/babydriver/kernelmo
    dule/babydriver.c, line 28.
    

## Basic Knowledge

### Kernel

Kernel 是一个程序，是操作系统底层用来管理上层软件发出的各种请求的程序，Kernel 将各种请求转换为指令，交给硬件去处理，简而言之，Kernel
是连接软件与硬件的中间层

Kernel 主要提供两个功能，与硬件交互，提供应用运行环境

在 intel 的 CPU 中，会将 CPU 的权限分为 Ring 0，Ring 1，Ring 2，Ring
3，四个等级，权限依次递减，高权限等级可以调用低权限等级的资源

在常见的系统（Windows，Linux，MacOS）中，内核处于 Ring 0 级别，应用程序处于 Ring 3 级别

### LKM

内核模块是 Linux Kernel 向外部提供的一个插口，叫做动态可加载内核模块（Loadable Kernel Module，LKM），LKM 弥补了
Linux Kernel 的可拓展性与可维护性，类似搭积木一样，可以往 Kernel 中接入各种 LKM，也可以卸载，常见的外设驱动就是一个 LKM

LKM 文件与用户态的可执行文件一样，在 Linux 中就是 ELF 文件，可以利用 IDA 进行分析

LKM 是单独编译的，但是不能单独运行，他只能作为 OS Kernel 的一部分

与 LKM 相关的指令有如下几个

> insmod：接入指定模块
>
> rmmod：移除指定模块
>
> lsmod：列出已加载模块

这些都是 shell 指令，可以在 shell 中运行查看

    
    
    ➜  ~ lsmod 
    Module                  Size  Used by
    rfcomm                 77824  2
    vmw_vsock_vmci_transport    32768  2
    vsock                  36864  3 vmw_vsock_vmci_transport
    ......
    

### ioctl

ioctl 是设备驱动程序中对设备的 I/O 通道进行管理的函数

所谓对 I/O 通道进行管理，就是对设备的一些特性进行控制，例如串口的传输波特率、马达的转速等等。它的调用个数如下： int ioctl(int fd,
ind cmd, …)；

其中 fd 是用户程序打开设备时使用 open 函数返回的文件标示符，cmd
是用户程序对设备的控制命令，至于后面的省略号，那是一些补充参数，一般最多一个，这个参数的有无和 cmd 的意义相关

ioctl 函数是文件结构中的一个属性分量，就是说如果你的驱动程序提供了对 ioctl 的支持，用户就可以在用户程序中使用 ioctl 函数来控制设备的
I/O 通道。

意思就是说如果一个 LKM 中提供了 iotcl 功能，并且实现了对应指令的操作，那么在用户态中，通过这个驱动程序，我们可以调用 ioctl
来直接调用模块中的操作

### Land Switch

在程序运行时，总是会经历 user space 与 kernel space 之前的切换，因为用户态应用程序在执行某些功能时，是由 Kernel
来执行的，这就涉及到两个 space 之前的切换

 **user land - > kernel land**

当用户态程序执行系统调用，异常处理，外设终端时，会从用户态切换到内核态，切换过程如下：

> 1.swapgs 指令修改 GS 寄存器切换到内核态
>
> 2.将当前栈顶（sp）记录在 CPU 独占变量区域，然后将此区域里的内核栈顶赋给 sp
>
> 3.push 各寄存器的值
>
> 4.通过汇编指令判断是否为 32 位
>
> 5.通过系统调用号，利用函数表 sys_call_table 执行响应操作
    
    
    ENTRY(entry_SYSCALL_64)
     /* SWAPGS_UNSAFE_STACK 是一个宏，x86 直接定义为 swapgs 指令 */
     SWAPGS_UNSAFE_STACK
    
     /* 保存栈值，并设置内核栈 */
     movq %rsp, PER_CPU_VAR(rsp_scratch)
     movq PER_CPU_VAR(cpu_current_top_of_stack), %rsp
    
    /* 通过 push 保存寄存器值，形成一个 pt_regs 结构 */
    /* Construct struct pt_regs on stack */
    pushq  $__USER_DS      /* pt_regs->ss */
    pushq  PER_CPU_VAR(rsp_scratch)  /* pt_regs->sp */
    pushq  %r11             /* pt_regs->flags */
    pushq  $__USER_CS      /* pt_regs->cs */
    pushq  %rcx             /* pt_regs->ip */
    pushq  %rax             /* pt_regs->orig_ax */
    pushq  %rdi             /* pt_regs->di */
    pushq  %rsi             /* pt_regs->si */
    pushq  %rdx             /* pt_regs->dx */
    pushq  %rcx tuichu    /* pt_regs->cx */
    pushq  $-ENOSYS        /* pt_regs->ax */
    pushq  %r8              /* pt_regs->r8 */
    pushq  %r9              /* pt_regs->r9 */
    pushq  %r10             /* pt_regs->r10 */
    pushq  %r11             /* pt_regs->r11 */
    sub $(6*8), %rsp      /* pt_regs->bp, bx, r12-15 not saved */
    

**kernel land - > user land**

内核态返回用户态流程：

> 1.swapgs 指令恢复用户态 GS 寄存器
>
> 2.sysretq 或者 iretq 恢复到用户空间

## Kernel Functions

内核态与用户态的函数有一些区别

> printk：类似与 printf，但是内容不一定会在终端显示起来，但是会在内核缓冲区里，可以用 dmsg 命令查看
>
> copy_from_user：实现了将用户空间的数据传送到内核空间
>
> copy_to_user：实现了将内核空间的数据传送到用户空间
>
> kmalloc：内核态内存分配函数
>
> kfree：内核态内存释放函数

用来改变权限的函数：

> int commit_creds(struct cred *new)
>
> struct cred prepare_kernel_cred(struct task_struct daemon)

执行 commit_creds(prepare_kernel_cred(0)) 即可获得 root 权限

### Expoit Mitigations

内核态与用户态的保护方式有所区别

相同的保护措施：DEP，Canary，ASLR，PIE，RELRO

不同的保护措施：MMAP_MIN_ADDR，KALLSYMS，RANDSTACK，STACKLEAK，SMEP，SMAP

 **MMAP_MIN_ADDR**

MMAP_MIN_ADDR 保护机制不允许程序分配低内存地址，可以用来防御 null pointer dereferences

如果没有这个保护，可以进行如下的攻击行为：

> 1.函数指针指针为 0，程序可以分配内存到 0x000000 处。
>
> 2.程序在内存 0x000000 写入恶意代码。
>
> 3.程序触发 kernel BUG（）。这里说的 BUG() 其实是 linux kernel
> 中用于拦截内核程序超出预期的行为，属于软件主动汇报异常的一种机制。
>
> 4.内核执行恶意代码。

 **KALLSYMS**

/proc/kallsyms 给出内核中所有 symbol 的地址，通过 grep /proc/kallsyms
就可以得到对应函数的地址，我们需要这个信息来写可靠的
exploit，否则需要自己去泄露这个信息。在低版本的内核中所有用户都可读取其中的内容，高版本的内核中缺少权限的用户读取时会返回 0。

 **SMEP**

管理模式执行保护，保护内核是其不允许执行用户空间代码。在 SMEP 保护关闭的情况下，若存在 kernel stack
overfolw，可以将内核栈的返回地址覆盖为用户空间的代码片段执行。在开启了 SMEP 保护下，当前 cpu 处于 ring 0
模式，当返回到用户态执行时会触发页错误。

操作系统是通过 CR4 寄存器的第 20 位的值来判断 SMEP 是否开启，1 开启，0 关闭，检查 SMEP 是否开启

    
    
    cat /proc/cpuinfo | grep smep
    

可通过 mov 指令给 CR4 寄存器赋值从而达到关闭 SMEP 的目的，相关的 mov 指令可以通过 ropper，ROPgadget 等工具查找

 **SMAP**

管理模式访问保护，禁止内核访问用户空间的数据

 **KASLR**

内核地址空间布局随机化，并不默认开启，需要在内核命令行中添加指定指令。

qemu 增加启动参数 -append "kaslr" 即可开启

### Privilege Escalation

提取，越狱，就是要以 root 用户拿到 shell，获取 root 的方式有几种

在内核态调用 commit_creds(prepare_kernel_cred(0))，返回用户态执行起 shell

    
    
    void get_r00t() {
        commit_creds(prepare_kernel_cred(0));
    }
    int main(int argc, char *argv) {
        ...
        trigger_fp_overwrite(&get_r00t);
        ...
        // trigger fp use
        trigger_vuln_fp();
        // Kernel Executes get_r00t()
        ...
        // Now we have root
        system("/bin/sh");
    }
    

SMEP 防预这种类型的攻击的方法是：如果处理器处于 ring0 模式，并试图执行有 user 数据的内存时，就会触发一个页错误。

也可以修改 cred 结构体，cred 结构体记录了进程的权限，每个进程都有一个 cred
结构体，保存了进程的权限等信息（uid，gid），如果修改某个进程的 cred 结构体（uid = gid = 0），就得到了 root 权限

    
    
    struct cred {
        atomic_t    usage;
    #ifdef CONFIG_DEBUG_CREDENTIALS
        atomic_t    subscribers;    /* number of processes subscribed */
        void        *put_addr;
        unsigned    magic;
    #define CRED_MAGIC    0x43736564
    #define CRED_MAGIC_DEAD    0x44656144
    #endif
        kuid_t        uid;        /* real UID of the task */
        kgid_t        gid;        /* real GID of the task */
        kuid_t        suid;        /* saved UID of the task */
        kgid_t        sgid;        /* saved GID of the task */
        kuid_t        euid;        /* effective UID of the task */
        kgid_t        egid;        /* effective GID of the task */
        kuid_t        fsuid;        /* UID for VFS ops */
        kgid_t        fsgid;        /* GID for VFS ops */
        unsigned    securebits;    /* SUID-less security management */
        kernel_cap_t    cap_inheritable; /* caps our children can inherit */
        kernel_cap_t    cap_permitted;    /* caps we're permitted */
        kernel_cap_t    cap_effective;    /* caps we can actually use */
        kernel_cap_t    cap_bset;    /* capability bounding set */
        kernel_cap_t    cap_ambient;    /* Ambient capability set */
    #ifdef CONFIG_KEYS
        unsigned char    jit_keyring;    /* default keyring to attach requested
                         * keys to */
        struct key __rcu *session_keyring; /* keyring inherited over fork */
        struct key    *process_keyring; /* keyring private to this process */
        struct key    *thread_keyring; /* keyring private to this thread */
        struct key    *request_key_auth; /* assumed request_key authority */
    #endif
    #ifdef CONFIG_SECURITY
        void        *security;    /* subjective LSM security */
    #endif
        struct user_struct *user;    /* real user ID subscription */
        struct user_namespace *user_ns; /* user_ns the caps and keyrings are relative to. */
        struct group_info *group_info;    /* supplementary groups for euid/fsgid */
        struct rcu_head    rcu;        /* RCU deletion hook */
    } __randomize_layout;
    

## Build Linux Kernel

### Source Code

先下载一份 Kernel 源码，我用的是 2.6.32，由于我的机子是 ubuntu 16.04，预装的 make 与 gcc 版本过高，编译 2.6 的
kernel 会失败，所以需要降级

    
    
    # 4.7 gcc
    sudo apt install gcc-4.7 g++-4.7
    sudo rm /usr/bin/gcc /usr/bin/g++
    sudo ln -s /usr/bin/gcc-4.7 /usr/bin/gcc
    sudo ln -s /usr/bin/g++-4.7 /usr/bin/g++
    # 3.80 make
    wget https://mirrors.tuna.tsinghua.edu.cn/gnu/make/make-3.80.tar.gz
    tar -xvf make-3.80.tar.gz
    cd make-3.80/
    ./configure
    make
    sudo make install
    

3.80 的 make 生成在源码目录里，稍后需要用这个 make 文件

修改三处 2.6 源码文件

> 1.arch/x86/vdso/Makefile 中第 28 行的 -m elf_x86_64 改成 -m64，第 72 行的-m elf_i386
> 改成-m32
>
> 2.drivers/net/igbvf/igbvf.h 中注释第 128 行
>
> 3.kernel/timeconst.pl 中第 373 行 defined(@val) 改成 @val
>
> 4.（可选）关闭 canary 保护需要编辑源码中的.config 文件 349 行，注释掉 CONFIG_CC_STACKPROTECTOR=y
> 这一项

### bzImage

安装必备依赖

    
    
    sudo apt-get install build-essential libncurses5-dev
    

解压后进入源码目录，使用刚安装的 make

    
    
    ~/MAKE/make-3.80/make menuconfig
    

进入 kernel hacking，勾选 Kernel debugging，Compile-time checks and compiler
options-->Compile the kernel with debug info，Compile the kernel with frame
pointers 和 KGDB，然后开始编译

    
    
    ~/MAKE/make-3.80/make bzImage
    

大概 10 分钟的样子，出现这个信息就说明编译成功了

    
    
    Setup is 15036 bytes (padded to 15360 bytes).
    System is 3754 kB
    CRC 4505d1c3
    Kernel: arch/x86/boot/bzImage is ready  (#1)
    

vmlinux 在源码根目录下，bzImage 在/arch/x86/boot/里

### rootfs.cpio

编译 busybox

    
    
    wget https://busybox.net/downloads/busybox-1.27.2.tar.bz2
    tar -jxvf busybox-1.27.2.tar.bz2
    cd busybox-1.27.2
    make menuconfig
    

勾选 Busybox Settings -> Build Options -> Build Busybox as a static binary

    
    
    make install
    

编译完成后源码目录下会有一个_install 文件夹，进入

    
    
    mkdir -pv {bin,sbin,etc,proc,sys,usr/{bin,sbin}}
    mkdir etc/init.d
    touch etc/init.d/init
    

编辑 etc/inittab 文件，加入以下内容（貌似这一步可以省略）

    
    
    ::sysinit:/etc/init.d/rcS
    ::askfirst:/bin/ash
    ::ctrlaltdel:/sbin/reboot
    ::shutdown:/sbin/swapoff -a
    ::shutdown:/bin/umount -a -r
    ::restart:/sbin/init
    

编辑 etc/init.d/init 文件，加入以下内容

    
    
    #!/bin/sh
    mount -t proc none /proc
    mount -t sys none /sys
    /bin/mount -n -t sysfs none /sys
    /bin/mount -t ramfs none /dev
    /sbin/mdev -s
    

接着就可以打包成 rootfs.cpio

    
    
    chmod +x ./etc/init.d/rcS
    find . | cpio -o --format=newc > ../rootfs.cpio
    

### boot

得到三个文件后，可以利用 qemu 运行起来，启动脚本 boot.sh

    
    
    #!/bin/sh
    qemu-system-x86_64 \
     -initrd rootfs.cpio \
     -kernel bzImage \
     -nographic \
     -append "console=ttyS0 root=/dev/ram rdinit=/sbin/init" \
     -m 64M \
     -monitor /dev/null \
    
    
    
    / # uname -a
    Linux (none) 2.6.32 #1 SMP Sun Jan 26 21:51:02 CST 2020 x86_64 GNU/Linux
    

## Run LKM

### build

简单写一个 hello 的程序，hello.c 内容如下

    
    
    #include <linux/init.h>
    #include <linux/module.h>
    #include <linux/kernel.h>
    #include <linux/proc_fs.h>
    int hello_write(struct file *file, const char *buf, unsigned long len)
    {
        printk("You write something.");
        return len;
    }
    static int __init hello_init(void)
    {
        printk(KERN_ALERT "hello driver init!\n");
        create_proc_entry("hello", 0666, 0)->write_proc = hello_write;
        return 0;
    }
    static void __exit hello_exit(void)
    {
        printk(KERN_ALERT "hello driver exit\n");
    }
    module_init(hello_init);
    module_exit(hello_exit);
    

Makefile 内容如下，注意 xxx.c 与 xxx.o 文件名一致，KERNELDR 目录是内核源代码

    
    
    obj-m := hello.o
    KERNELDR := /home/mask/kernel/linux-2.6.32
    PWD := $(shell pwd)
    modules:
        $(MAKE) -C $(KERNELDR) M=$(PWD) modules
    modules_install:
        $(MAKE) -C $(KERNELDR) M=$(PWD) modules_install
    clean:
        $(MAKE) -C $(KERNELDR) M=$(PWD) clean
    

make 出来后得到.ko 文件

    
    
    ➜  helloworld ls
    helloc.c   helloc.mod.c  helloc.o  modules.order
    helloc.ko  helloc.mod.o  Makefile  Module.symvers
    ➜  helloworld file helloc.ko                                                                      
    helloc.ko: ELF 64-bit LSB relocatable, x86-64, version 1 (SYSV), BuildID[sha1]=08aaa94df43f8333c14
    9073cddf3043e52b28107, not stripped
    ➜  helloworld checksec helloc.ko       
    [*] '/home/mask/kernel/test/linux4.4/module/helloworld/helloc.ko'
        Arch:     amd64-64-little
        RELRO:    No RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x0)
    

再写一个调用程序 call.c

    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <fcntl.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <sys/mman.h>
    int main()
    {
        int fd = open("/proc/hello", O_WRONLY);
        write(fd, "Mask", 4);
        return 0;
    }
    

### run

将 helloc.ko 文件与 call 文件复制.

进文件系统，也就是 busybox 目录里的_install 文件夹，重新打包 rootfs.cpio，运行起来即可看见模块

    
    
    / # insmod hello.ko 
    [   11.743066] hello driver init!
    / # ./call
    [   25.860294] You write something.
    

### Reference

> [qemu+gdb 调试 kernel](http://eternalsakura13.com/2018/04/13/qemu/)
>
> [Linux Kernel Pwn ABC(Ⅰ)](http://m4x.fun/post/linux-kernel-pwn-abc-1/)
>
> [Linux Syscall](https://xinqiu.gitbooks.io/linux-insides-> cn/content/SysCall/linux-syscall-2.html)

 ***本文作者：Mask6asok，转载请注明来自FreeBuf.COM**

