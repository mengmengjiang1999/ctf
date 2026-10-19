**Author: Hcamael@Knownsec 404 Team**  
**Chinese Version:<https://paper.seebug.org/779/>**

Recently, when I was studying IoT, due to the lack of devices, simulating
running firmware would often be short of `/dev/xxx`, so I began to wonder if I
could write a driver myself to make the firmware run. No matter how hard it is
and whether it can achieve my original intention or not, it pays off a lot if
you learn how to develop Linux driver.

### Introduction

The series I wrote is mainly about practice, which doesn't talk much about
theory. I learn how to develop the driver from the book _Linux Device Drivers_
, and there is the code for the examples explained in this book on the GitHub
[[1]](https://github.com/jesstess/ldd4 "\[1\]").

As for the basic concept, Linux system is divided into kernel mode and user
mode. The hardware device can only be accessed in the kernel mode, and the
driver can be regarded as an API provided in the kernel mode to let the code
of the user mode access the hardware device.

With the basic concepts in mind, I have come up with a series of problems,
which inspire me to learn the development of driver.

  1. All code learning starts with Hello World, so how to write a Hello World program?

  2. How does the driver generate device files under /dev?

  3. How does the driver access the actual hardware?

  4. How do I get system-driven code? Or can it reverse the driver without code? Where are the binaries that store the drivers? In the future, there may be opportunities to try to study the drive security.

### Everything Starts from Hello World

My Hello World code is as follows
[[2]](https://raw.githubusercontent.com/Hcamael/Linux_Driver_Study/master/hello.c
"\[2\]"):

    
    
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

The Linux driver is developed by means of C Language, which is different form
the normal one we use. What we often use is Libc library, which doesn’t exist
in the kernel. While the driver is a program running in the kernel, we use the
library functions in the kernel.

For example, `printk` is analogous to `printf` in Libc, an output function
defined in the kernel. But I think it's more like the logger function in
Python, because the output of `printk` is printed in the kernel's log, which
can be viewed via `dmesg` command.

There is only one entry point and one exit point in the driver code. Loading
the driver into the kernel will execute the function defined by the
`module_init` function, which in the above code is the `hello_init` function.
When the driver is unloaded from the kernel, the function defined by the
`module_exit` function is called, which in the above code is the `hello_exit`
function.

The code above makes it clear that when the driver is loaded, it prints `Hello
World` and when the driver is unloaded, it prints `Goodbye World`.

PS: `MODULE_LICENSE` and `MODULE_AUTHOR` are not very important. I'm not a
professional development driver, so needn’t pay attention to them.

PSS: There should add a newline for the output of `printk`, otherwise the
buffer will not be flushed.

#### Compile the Driver

The driver needs to be compiled by the make command, and the `Makefile` is
shown below:

    
    
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

In general, the source code of the kernel exists in the `/usr/src/linux-headers-$(shell uname -r)/` directory, such as:

    
    
    $ uname -r
    4.4.0-135-generic
    
    /usr/src/linux-headers-4.4.0-135/  --> 该内核源码目录
    /usr/src/linux-headers-4.4.0-135-generic/    --> 该内核编译好的源码目录

And what we need is the compiled source directory, which is `/usr/src/linux-headers-4.4.0-135-generic/`.

The header files of the driver code need to be searched from this directory.

The parameter `M=$(PWD)` indicates that the output of the driver compilation
is in the current directory.

Finally, through the command `obj-m := hello.o`, which means to compile
`hello.o` into `hello.ko`, and the ko file is the kernel module file.

#### Load the Driver into the Kernel

Some system commands that need to be used:

`Lsmod`: View the kernel module that is currently loaded.

`Insmod`: Loads the kernel module and requires root permissions.

`Rmmod`: Remove the module.

For example:

    
    
    # insmod hello.ko        // Load the hello.ko module into the kernel
    # rmmod hello          // Remove the hello module from the kernel

The old kernel is using the above method to load and remove the kernel, but
the new version of the Linux kernel adds verification of the module. The
current actual situation is as follows:

    
    
    # insmod hello.ko
    insmod: ERROR: could not insert module hello.ko: Required key not available

From a security perspective, the current kernel assumes that the module is
untrustworthy and needs to be signed with a trusted certificate to load the
module.

Two solutions:

  1. Enter the BIOS and turn off the Secure Boot of UEFI.

  2. Add a self-signed certificate to the kernel and use it to sign the driver module (You can refer to [[3]](https://jin-yang.github.io/post/kernel-modules.html "\[3\]")).

#### View the Results

![
](https://images.seebug.org/content/images/2019/01/aba5c16b-6a1e-46fe-8cc7-7de03bd1aa97.png-w331s)

### Add Device Files under /dev

Once again, we firstly provide the code, and then explain the example code
[[4]](https://raw.githubusercontent.com/Hcamael/Linux_Driver_Study/master/scull.c
"\[4\]").

    
    
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

#### Knowledge Point 1 -- Classification of Drivers

![
](https://images.seebug.org/content/images/2019/01/7a625b7c-f8b7-4624-9721-69d741997f42.png-w331s)

Drivers are divided into three categories: character devices, block devices
and network interface. The above code is an example of character devices, and
the other two will be discussed later.

As shown above, `brw-rw--` \-- the permission bar, block devices starts with
"b" and the character devices starting with "c".

#### Knowledge Point 2 -- The Major and Minor Numbers

The major number is used to distinguish the driver. In general, the same major
number indicates that it is controlled by the same driver.

Multiple devices can be created in one drive, distinguished by minor numbers.
The major and minor numbers determine a driver device together (as shown
above).

    
    
    brw-rw----  1 root disk      8,   0 Dec 17 13:02 sda
    brw-rw----  1 root disk      8,   1 Dec 17 13:02 sda1

The major number of equipment `sda` and `sda1` is 8, and one minor number is 0
and the other minor number is 1.

#### Knowledge Point 3 -- How the Driver Provides the API

In my mind, the interface provided by the driver is `/dev/xxx`, and under
Linux, "everything is about file", so the operation of the driver device is
actually the operation of the file and the driver is used to
define/open/read/write...what `/dev/xxx` will happen. The API of driver you
can think is all about file operations.

What file operations are there? They are all defined in the `file_operations`
structure of the kernel
`<linux/fs.h>`[[5]](https://raw.githubusercontent.com/torvalds/linux/master/include/linux/fs.h
"\[5\]") header file.

In the code I illustrated above:

    
    
    struct file_operations scull_fops = {
        .owner =    THIS_MODULE,
        .llseek =   scull_llseek,
        .read =     scull_read,
        .write =    scull_write,
        .open =     scull_open,
        .release =  scull_release,
    };

I declare a structure and assign it. Except for the `owner`, the values of
other members are function pointers.

Then I used `cdev_add` to register the file operation structure with each
driver in the `scull_setup_cdev` function.

For example, if I perform "open" operation on the driver device, I will
execute the `scull_open` function, which is equivalent to "hooking" the `open`
function in the system call.

#### Knowledge Point 4 -- Generate the Corresponding Device under /dev

Compile the above code, get `scull.ko`, then sign it, and finally load it into
the kernel via `insmod`.

Check if it is loaded successfully:

![
](https://images.seebug.org/content/images/2019/01/b129b201-93ce-491b-b1b2-351c4c357c36.png-w331s)

Although the driver has been loaded successfully, it does not create a device
file in the /dev directory. We need to manually use `mknod` for device
linking:

![
](https://images.seebug.org/content/images/2019/01/2118fab7-653e-4d2f-ac15-b299e77e92be.png-w331s)

### Summary

In this example, there is no operation on the actual physical device, just
simply use `kmalloc` to apply for a block of memory in the kernel space.

No more details about the code, which can be found by looking up the header
files or Google.

Here I would like to share my way of learning the development of drivers: read
books to understand the basic concept firstly, and then look up for the
details when you need to use them.

For example, I don't need to know what API the driver can provide, and all I
need to know is that the API provided by the drivers is all about file
operations. As for the file operations, currently I only need to `open`,
`close`, `read` and `write`. I will look up for more file operations when
necessary.

### Reference

  1. <https://github.com/jesstess/ldd4>
  2. <https://raw.githubusercontent.com/Hcamael/Linux_Driver_Study/master/hello.c>
  3. <https://jin-yang.github.io/post/kernel-modules.html>
  4. <https://raw.githubusercontent.com/Hcamael/Linux_Driver_Study/master/scull.c>
  5. <https://raw.githubusercontent.com/torvalds/linux/master/include/linux/fs.h>

### About Knownsec & 404 Team

Beijing Knownsec Information Technology Co., Ltd. was established by a group
of high-profile international security experts. It has over a hundred frontier
security talents nationwide as the core security research team to provide
long-term internationally advanced network security solutions for the
government and enterprises.

Knownsec's specialties include network attack and defense integrated
technologies and product R&D under new situations. It provides visualization
solutions that meet the world-class security technology standards and enhances
the security monitoring, alarm and defense abilities of customer networks with
its industry-leading capabilities in cloud computing and big data processing.
The company's technical strength is strongly recognized by the State Ministry
of Public Security, the Central Government Procurement Center, the Ministry of
Industry and Information Technology (MIIT), China National Vulnerability
Database of Information Security (CNNVD), the Central Bank, the Hong Kong
Jockey Club, Microsoft, Zhejiang Satellite TV and other well-known clients.

404 Team, the core security team of Knownsec, is dedicated to the research of
security vulnerability and offensive and defensive technology in the fields of
Web, IoT, industrial control, blockchain, etc. 404 team has submitted
vulnerability research to many well-known vendors such as Microsoft, Apple,
Adobe, Tencent, Alibaba, Baidu, etc. And has received a high reputation in the
industry.

The most well-known sharing of Knownsec 404 Team includes: [KCon Hacking
Conference](http://kcon.knownsec.com/#/ "KCon Hacking Conference"), [Seebug
Vulnerability Database](https://www.seebug.org/ "Seebug Vulnerability
Database") and [ZoomEye Cyberspace Search Engine](https://www.zoomeye.org/
"ZoomEye Cyberspace Search Engine").

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/976/>

