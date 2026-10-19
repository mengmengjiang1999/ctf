**作者：Hcamael@知道创宇404实验室**  
**英文版本：<https://paper.seebug.org/976/>**

最近在搞IoT的时候，因为没有设备，模拟跑固件经常会缺`/dev/xxx`，所以我就开始想，我能不能自己写一个驱动，让固件能跑起来？因此，又给自己挖了一个很大坑，不管最后能不能达到我的初衷，能学到怎么开发Linux驱动，也算是有很大的收获了。

### 前言

我写的这个系列以实践为主，不怎么谈理论，理论可以自己去看书，我是通过《Linux Device
Drivers》这本书学的驱动开发，Github上有这本书中讲解的实例的代码[[1]](https://github.com/jesstess/ldd4
"\[1\]")。

虽然我不想谈太多理论，但是关于驱动的基本概念还是要有的。Linux系统分为内核态和用户态，只有在内核态才能访问到硬件设备，而驱动可以算是内核态中提供出的API，供用户态的代码访问到硬件设备。

有了基本概念以后，我就产生了一系列的问题，而我就是通过我的这一系列的问题进行学习的驱动开发：

  1. 一切代码的学习都是从Hello World开始的，怎么写一个Hello World的程序？
  2. 驱动是如何在/dev下生成设备文件的？
  3. 驱动怎么访问实际的硬件？
  4. 因为我毕竟是搞安全的，我会在想，怎么获取系统驱动的代码？或者没有代码那能逆向驱动吗？驱动的二进制文件储存在哪？以后有机会可能还可以试试搞驱动安全。

### Everything start from Hello World

提供我的Hello
World代码[[2]](https://raw.githubusercontent.com/Hcamael/Linux_Driver_Study/master/hello.c
"\[2\]")：

    
    
    #include <linux/init.h>
    #include <linux/module.h>
    
    MODULE_LICENSE("Dual BSD/GPL");
    MODULE_AUTHOR("Hcamal");
    
    int hello_init(void)
    {
        printk(KERN_INFO "Hello World\n");
        return 0;
    }
    
    void hello_exit(void)
    {
        printk(KERN_INFO "Goodbye World\n");
    }
    
    module_init(hello_init);
    module_exit(hello_exit);

Linux下的驱动是使用C语言进行开发的，但是和我们平常写的C语言也有不同，因为我们平常写的C语言使用的是Libc库，但是驱动是跑在内核中的程序，内核中却不存在libc库，所以要使用内核中的库函数。

比如`printk`可以类比为libc中的`printf`，这是在内核中定义的一个输出函数，但是我觉得更像Python里面logger函数，因为`printk`的输出结果是打印在内核的日志中，可以使用`dmesg`命令进行查看

驱动代码只有一个入口点和一个出口点，把驱动加载到内核中，会执行`module_init`函数定义的函数，在上面代码中就是`hello_init`函数。当驱动从内核被卸载时，会调用`module_exit`函数定义的函数，在上面代码中就是`hello_exit`函数。

上面的代码就很清晰了，当加载驱动时，输出`Hello World`，当卸载驱动时，输出`Goodbye World`

PS：`MODULE_LICENSE`和`MODULE_AUTHOR`这两个不是很重要，我又不是专业开发驱动的，所以不用关注这两个

PSS: `printk`输出的结果要加一个换行，要不然不会刷新缓冲区

#### 编译驱动

驱动需要通过make命令进行编译，`Makefile`如下所示:

    
    
    ifneq ($(KERNELRELEASE),)
    
        obj-m := hello.o
    
    else
    
        KERN_DIR ?= /usr/src/linux-headers-$(shell uname -r)/
        PWD := $(shell pwd)
    
    default:
        $(MAKE) -C $(KERN_DIR) M=$(PWD) modules
    
    endif
    
    
    clean:
        rm -rf *.o *~ core .depend .*.cmd *.ko *.mod.c .tmp_versions

一般情况下，内核的源码都存在与`/usr/src/linux-headers-$(shell uname -r)/`目录下

比如：

    
    
    $ uname -r
    4.4.0-135-generic
    
    /usr/src/linux-headers-4.4.0-135/  --> 该内核源码目录
    /usr/src/linux-headers-4.4.0-135-generic/    --> 该内核编译好的源码目录

而我们需要的是编译好后的源码的目录，也就是`/usr/src/linux-headers-4.4.0-135-generic/`

驱动代码的头文件都需要从该目录下进行搜索

`M=$(PWD)`该参数表示，驱动编译的结果输出在当前目录下

最后通过命令`obj-m := hello.o`，表示把`hello.o`编译出`hello.ko`, 这个ko文件就是内核模块文件

#### 加载驱动到内核

需要使用到的一些系统命令：

  * `lsmod`: 查看当前已经被加载的内核模块
  * `insmod`: 加载内核模块，需要root权限
  * `rmmod`: 移除模块

比如:

    
    
    # insmod hello.ko        // 把hello.ko模块加载到内核中
    # rmmod hello            // 把hello模块从内核中移除

旧版的内核就是使用上面这样的方法进行内核的加载与移除，但是新版的Linux内核增加了对模块的验证，当前实际的情况如下:

    
    
    # insmod hello.ko
    insmod: ERROR: could not insert module hello.ko: Required key not available

从安全的角度考虑，现在的内核都是假设模块为不可信的，需要使用可信的证书对模块进行签名，才能加载模块

解决方法用两种:

  1. 进入BIOS，关闭UEFI的Secure Boot
  2. 向内核添加一个自签名证书，然后使用证书对驱动模块进行签名，参考[[3]](https://jin-yang.github.io/post/kernel-modules.html "\[3\]")

#### 查看结果

![
](https://images.seebug.org/content/images/2019/01/aba5c16b-6a1e-46fe-8cc7-7de03bd1aa97.png-w331s)

### 在/dev下增加设备文件

同样先提供一份代码，然后讲解这份实例代码[[4]](https://raw.githubusercontent.com/Hcamael/Linux_Driver_Study/master/scull.c
"\[4\]")

    
    
    #include <linux/init.h>
    #include <linux/module.h>
    #include <linux/kernel.h>   /* printk() */
    #include <linux/slab.h>     /* kmalloc() */
    #include <linux/fs.h>       /* everything... */
    #include <linux/errno.h>    /* error codes */
    #include <linux/types.h>    /* size_t */
    #include <linux/fcntl.h>    /* O_ACCMODE */
    #include <linux/cdev.h>
    #include <asm/uaccess.h>    /* copy_*_user */
    
    
    MODULE_LICENSE("Dual BSD/GPL");
    MODULE_AUTHOR("Hcamael");
    
    int scull_major =   0;
    int scull_minor =   0;
    int scull_nr_devs = 4;
    int scull_quantum = 4000;
    int scull_qset = 1000;
    
    struct scull_qset {
        void **data;
        struct scull_qset *next;
    };
    
    struct scull_dev {
        struct scull_qset *data;  /* Pointer to first quantum set. */
        int quantum;              /* The current quantum size. */
        int qset;                 /* The current array size. */
        unsigned long size;       /* Amount of data stored here. */
        unsigned int access_key;  /* Used by sculluid and scullpriv. */
        struct mutex mutex;       /* Mutual exclusion semaphore. */
        struct cdev cdev;     /* Char device structure. */
    };
    
    struct scull_dev *scull_devices;    /* allocated in scull_init_module */
    
    /*
     * Follow the list.
     */
    struct scull_qset *scull_follow(struct scull_dev *dev, int n)
    {
        struct scull_qset *qs = dev->data;
    
            /* Allocate the first qset explicitly if need be. */
        if (! qs) {
            qs = dev->data = kmalloc(sizeof(struct scull_qset), GFP_KERNEL);
            if (qs == NULL)
                return NULL;
            memset(qs, 0, sizeof(struct scull_qset));
        }
    
        /* Then follow the list. */
        while (n--) {
            if (!qs->next) {
                qs->next = kmalloc(sizeof(struct scull_qset), GFP_KERNEL);
                if (qs->next == NULL)
                    return NULL;
                memset(qs->next, 0, sizeof(struct scull_qset));
            }
            qs = qs->next;
            continue;
        }
        return qs;
    }
    
    /*
     * Data management: read and write.
     */
    
    ssize_t scull_read(struct file *filp, char __user *buf, size_t count,
                    loff_t *f_pos)
    {
        struct scull_dev *dev = filp->private_data;
        struct scull_qset *dptr; /* the first listitem */
        int quantum = dev->quantum, qset = dev->qset;
        int itemsize = quantum * qset; /* how many bytes in the listitem */
        int item, s_pos, q_pos, rest;
        ssize_t retval = 0;
    
        if (mutex_lock_interruptible(&dev->mutex))
            return -ERESTARTSYS;
        if (*f_pos >= dev->size)
            goto out;
        if (*f_pos + count > dev->size)
            count = dev->size - *f_pos;
    
        /* Find listitem, qset index, and offset in the quantum */
        item = (long)*f_pos / itemsize;
        rest = (long)*f_pos % itemsize;
        s_pos = rest / quantum; q_pos = rest % quantum;
    
        /* follow the list up to the right position (defined elsewhere) */
        dptr = scull_follow(dev, item);
    
        if (dptr == NULL || !dptr->data || ! dptr->data[s_pos])
            goto out; /* don't fill holes */
    
        /* read only up to the end of this quantum */
        if (count > quantum - q_pos)
            count = quantum - q_pos;
    
        if (raw_copy_to_user(buf, dptr->data[s_pos] + q_pos, count)) {
            retval = -EFAULT;
            goto out;
        }
        *f_pos += count;
        retval = count;
    
      out:
        mutex_unlock(&dev->mutex);
        return retval;
    }
    
    ssize_t scull_write(struct file *filp, const char __user *buf, size_t count,
                    loff_t *f_pos)
    {
        struct scull_dev *dev = filp->private_data;
        struct scull_qset *dptr;
        int quantum = dev->quantum, qset = dev->qset;
        int itemsize = quantum * qset;
        int item, s_pos, q_pos, rest;
        ssize_t retval = -ENOMEM; /* Value used in "goto out" statements. */
    
        if (mutex_lock_interruptible(&dev->mutex))
            return -ERESTARTSYS;
    
        /* Find the list item, qset index, and offset in the quantum. */
        item = (long)*f_pos / itemsize;
        rest = (long)*f_pos % itemsize;
        s_pos = rest / quantum;
        q_pos = rest % quantum;
    
        /* Follow the list up to the right position. */
        dptr = scull_follow(dev, item);
        if (dptr == NULL)
            goto out;
        if (!dptr->data) {
            dptr->data = kmalloc(qset * sizeof(char *), GFP_KERNEL);
            if (!dptr->data)
                goto out;
            memset(dptr->data, 0, qset * sizeof(char *));
        }
        if (!dptr->data[s_pos]) {
            dptr->data[s_pos] = kmalloc(quantum, GFP_KERNEL);
            if (!dptr->data[s_pos])
                goto out;
        }
        /* Write only up to the end of this quantum. */
        if (count > quantum - q_pos)
            count = quantum - q_pos;
    
        if (raw_copy_from_user(dptr->data[s_pos]+q_pos, buf, count)) {
            retval = -EFAULT;
            goto out;
        }
        *f_pos += count;
        retval = count;
    
            /* Update the size. */
        if (dev->size < *f_pos)
            dev->size = *f_pos;
    
      out:
        mutex_unlock(&dev->mutex);
        return retval;
    }
    
    /* Beginning of the scull device implementation. */
    
    /*
     * Empty out the scull device; must be called with the device
     * mutex held.
     */
    int scull_trim(struct scull_dev *dev)
    {
        struct scull_qset *next, *dptr;
        int qset = dev->qset;   /* "dev" is not-null */
        int i;
    
        for (dptr = dev->data; dptr; dptr = next) { /* all the list items */
            if (dptr->data) {
                for (i = 0; i < qset; i++)
                    kfree(dptr->data[i]);
                kfree(dptr->data);
                dptr->data = NULL;
            }
            next = dptr->next;
            kfree(dptr);
        }
        dev->size = 0;
        dev->quantum = scull_quantum;
        dev->qset = scull_qset;
        dev->data = NULL;
        return 0;
    }
    
    int scull_release(struct inode *inode, struct file *filp)
    {
        printk(KERN_DEBUG "process %i (%s) success release minor(%u) file\n", current->pid, current->comm, iminor(inode));
        return 0;
    }
    
    /*
     * Open and close
     */
    
    int scull_open(struct inode *inode, struct file *filp)
    {
        struct scull_dev *dev; /* device information */
    
        dev = container_of(inode->i_cdev, struct scull_dev, cdev);
        filp->private_data = dev; /* for other methods */
    
        /* If the device was opened write-only, trim it to a length of 0. */
        if ( (filp->f_flags & O_ACCMODE) == O_WRONLY) {
            if (mutex_lock_interruptible(&dev->mutex))
                return -ERESTARTSYS;
            scull_trim(dev); /* Ignore errors. */
            mutex_unlock(&dev->mutex);
        }
        printk(KERN_DEBUG "process %i (%s) success open minor(%u) file\n", current->pid, current->comm, iminor(inode));
        return 0;
    }
    
    /*
     * The "extended" operations -- only seek.
     */
    
    loff_t scull_llseek(struct file *filp, loff_t off, int whence)
    {
        struct scull_dev *dev = filp->private_data;
        loff_t newpos;
    
        switch(whence) {
          case 0: /* SEEK_SET */
            newpos = off;
            break;
    
          case 1: /* SEEK_CUR */
            newpos = filp->f_pos + off;
            break;
    
          case 2: /* SEEK_END */
            newpos = dev->size + off;
            break;
    
          default: /* can't happen */
            return -EINVAL;
        }
        if (newpos < 0)
            return -EINVAL;
        filp->f_pos = newpos;
        return newpos;
    }
    
    struct file_operations scull_fops = {
        .owner =    THIS_MODULE,
        .llseek =   scull_llseek,
        .read =     scull_read,
        .write =    scull_write,
        // .unlocked_ioctl = scull_ioctl,
        .open =     scull_open,
        .release =  scull_release,
    };
    
    /*
     * Set up the char_dev structure for this device.
     */
    static void scull_setup_cdev(struct scull_dev *dev, int index)
    {
        int err, devno = MKDEV(scull_major, scull_minor + index);
    
        cdev_init(&dev->cdev, &scull_fops);
        dev->cdev.owner = THIS_MODULE;
        dev->cdev.ops = &scull_fops;
        err = cdev_add (&dev->cdev, devno, 1);
        /* Fail gracefully if need be. */
        if (err)
            printk(KERN_NOTICE "Error %d adding scull%d", err, index);
        else
            printk(KERN_INFO "scull: %d add success\n", index);
    }
    
    
    void scull_cleanup_module(void)
    {
        int i;
        dev_t devno = MKDEV(scull_major, scull_minor);
    
        /* Get rid of our char dev entries. */
        if (scull_devices) {
            for (i = 0; i < scull_nr_devs; i++) {
                scull_trim(scull_devices + i);
                cdev_del(&scull_devices[i].cdev);
            }
            kfree(scull_devices);
        }
    
        /* cleanup_module is never called if registering failed. */
        unregister_chrdev_region(devno, scull_nr_devs);
        printk(KERN_INFO "scull: cleanup success\n");
    }
    
    
    int scull_init_module(void)
    {
        int result, i;
        dev_t dev = 0;
    
        /*
         * Get a range of minor numbers to work with, asking for a dynamic major
         * unless directed otherwise at load time.
         */
        if (scull_major) {
            dev = MKDEV(scull_major, scull_minor);
            result = register_chrdev_region(dev, scull_nr_devs, "scull");
        } else {
            result = alloc_chrdev_region(&dev, scull_minor, scull_nr_devs, "scull");
            scull_major = MAJOR(dev);
        }
        if (result < 0) {
            printk(KERN_WARNING "scull: can't get major %d\n", scull_major);
            return result;
        } else {
            printk(KERN_INFO "scull: get major %d success\n", scull_major);
        }
    
            /*
         * Allocate the devices. This must be dynamic as the device number can
         * be specified at load time.
         */
        scull_devices = kmalloc(scull_nr_devs * sizeof(struct scull_dev), GFP_KERNEL);
        if (!scull_devices) {
            result = -ENOMEM;
            goto fail;
        }
        memset(scull_devices, 0, scull_nr_devs * sizeof(struct scull_dev));
    
            /* Initialize each device. */
        for (i = 0; i < scull_nr_devs; i++) {
            scull_devices[i].quantum = scull_quantum;
            scull_devices[i].qset = scull_qset;
            mutex_init(&scull_devices[i].mutex);
            scull_setup_cdev(&scull_devices[i], i);
        }
    
        return 0; /* succeed */
    
      fail:
        scull_cleanup_module();
        return result;
    }
    
    module_init(scull_init_module);
    module_exit(scull_cleanup_module);

#### 知识点1 -- 驱动分类

![
](https://images.seebug.org/content/images/2019/01/7a625b7c-f8b7-4624-9721-69d741997f42.png-w331s)

驱动分为3类，字符设备、块设备和网口接口，上面代码举例的是字符设备，其他两种，之后再说。

如上图所示，`brw-rw----`权限栏，b开头的表示块设备(block)，c开头的表示字符设备(char)

#### 知识点2 -- 主次编号

主编号用来区分驱动，一般主编号相同的表示由同一个驱动程序控制。

一个驱动中能创建多个设备，用次编号来区分。

主编号和次编号一起，决定了一个驱动设备。

如上图所示,

    
    
    brw-rw----  1 root disk      8,   0 Dec 17 13:02 sda
    brw-rw----  1 root disk      8,   1 Dec 17 13:02 sda1

设备`sda`和`sda1`的主编号为8，一个此编号为0一个此编号为1

#### 知识点3 -- 驱动是如何提供API的

在我的概念中，驱动提供的接口是`/dev/xxx`，在Linux下`Everything is
File`，所以对驱动设备的操作其实就是对文件的操作，所以一个驱动就是用来定义，打开/读/写/......一个`/dev/xxx`将会发生啥，驱动提供的API也就是一系列的文件操作。

有哪些文件操作？都被定义在内核`<linux/fs.h>`[[5]](https://raw.githubusercontent.com/torvalds/linux/master/include/linux/fs.h
"\[5\]")头文件中，`file_operations`结构体

上面我举例的代码中：

    
    
    struct file_operations scull_fops = {
        .owner =    THIS_MODULE,
        .llseek =   scull_llseek,
        .read =     scull_read,
        .write =    scull_write,
        .open =     scull_open,
        .release =  scull_release,
    };

我声明了一个该结构体，并赋值，除了`owner`，其他成员的值都为函数指针

之后我在`scull_setup_cdev`函数中，使用`cdev_add`向每个驱动设备，注册该文件操作结构体

比如我对该驱动设备执行open操作，则会去执行`scull_open`函数，相当于hook了系统调用中的`open`函数

#### 知识点4 -- 在/dev下生成相应的设备

对上面的代码进行编译，得到scull.ko，然后对其进行签名，最后使用`insmod`加载进内核中

查看是否成功加载：

![
](https://images.seebug.org/content/images/2019/01/b129b201-93ce-491b-b1b2-351c4c357c36.png-w331s)

虽然驱动已经加载成功了，但是并不会在/dev目录下创建设备文件，需要我们手动使用`mknod`进行设备链接:

![
](https://images.seebug.org/content/images/2019/01/2118fab7-653e-4d2f-ac15-b299e77e92be.png-w331s)

### 总结

在该实例中，并没有涉及到对实际物理设备的操作，只是简单的使用`kmalloc`在内核空间申请一块内存。代码细节上的就不做具体讲解了，都可以通过查头文件或者用Google搜出来。

再这里分享一个我学习驱动开发的方法，首先看书把基础概念给弄懂，细节到需要用到的时候再去查。

比如，我不需要知道驱动一共能提供有哪些API(也就是file_operations结构都有啥)，我只要知道一个概念，驱动提供的API都是一些文件操作，而文件操作，目前我只需要`open,
close, read, write`，其他的等有需求，要用到的时候再去查。

### 参考

  1. <https://github.com/jesstess/ldd4>
  2. <https://raw.githubusercontent.com/Hcamael/Linux_Driver_Study/master/hello.c>
  3. <https://jin-yang.github.io/post/kernel-modules.html>
  4. <https://raw.githubusercontent.com/Hcamael/Linux_Driver_Study/master/scull.c>
  5. <https://raw.githubusercontent.com/torvalds/linux/master/include/linux/fs.h>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/779/>

