# linux内核漏洞调试：配置双机调试环境

阅读量 **271930**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-04-24 11:00:46

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01da57829a99697f21.jpg)

## 选择kernel的版本

搜索含有dbgsym的内核版本  
`apt-cache search linux-image | grep dbgsym | grep 4.11`  
搜索特定source code的内核版本  
`apt-cache search linux-source`  
然后选择一个

## 安装内核

搜索要下载的linux内核版本  
`apt-cache search linux-image | grep linux-image | grep generic`  
安装内核  
`sudo apt-get install linux-image-4.10.0-19-generic`  
查看安装的内核版本  
`sudo dpkg --list | grep linux-image`  
重启，在grub之前，按住shift，选择我们的内核  
  

验证新内核启用  
`uname -sr`

## 安装符号文件

在终端输入下面的代码

    
    
    codename=$(lsb_release -c | awk  '{print $2}')
    sudo tee /etc/apt/sources.list.d/ddebs.list << EOF
    deb http://ddebs.ubuntu.com/ ${codename}      main restricted universe multiverse
    deb http://ddebs.ubuntu.com/ ${codename}-security main restricted universe multiverse
    deb http://ddebs.ubuntu.com/ ${codename}-updates  main restricted universe multiverse
    deb http://ddebs.ubuntu.com/ ${codename}-proposed main restricted universe multiverse
    EOF
    

添加访问符号服务器的密钥文件：  
`wget -O - http://ddebs.ubuntu.com/dbgsym-release-key.asc | sudo apt-key add
-`  
执行`sudo apt-get update`更新  
执行如下命令开始下载符号包：

    
    
    sudo apt-get install linux-image-`uname -r`-dbgsym
    

## 安装kernel对应的源代码

打开/etc/apt/sources.list，启用deb-src，sudo apt-get update更新

    
    
    vim /etc/apt/sources.list
    去掉下面这句话的注释
    deb-src http://us.archive.ubuntu.com/ubuntu/ xenial main restricted
    
    ...
    sudo apt-get update
    

  * 搜索所有版本的source code:`apt-cache search linux-source`
  * 安装指定版本的source code:`sudo apt-get install linux-source-4.10.0`

下载好的源码会被放在/usr/src目录下。  
  

解压缩得到源码  
`sudo tar -xvf linux-source-4.10.0.tar.bz2`

一切都安装好了之后，就可以拷贝一份我们的虚拟机，一个作为host,一个作为target

## 移除打印机，添加串口

打印机会占用我们的串口

###  target

![](https://p5.ssl.qhimg.com/t01d03c0a5e59d4ee2b.png)

###  host

![](https://p0.ssl.qhimg.com/t01eb7ad9a5d96cdc33.jpg)

## 配置target

需要让target在开机时候进入kgdb的调试状态，首先需要修改grub文件，增加grub引导时候的菜单项。

`sudo vim /etc/grub.d/40_custom`  
修改的内容从/boot/grub/grub.cfg里复制，复制一个菜单项（menuentry）过来，再把菜单名中增加调试信息，然后在内核命令行中增加KGDB选项，即下面这样：  
 **新增部分：kgdbwait kgdb8250=io,03f8,ttyS0,115200,4 kgdboc=ttyS0,115200 kgdbcon
nokaslr**

    
    
    #!/bin/sh
    exec tail -n +3 $0
    # This file provides an easy way to add custom menu entries.  Simply type the
    # menu entries you want to add after this comment.  Be careful not to change
    # the 'exec tail' line above.
    menuentry 'Ubuntu,KGDB with nokaslr' --class ubuntu --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-4.10.0-19-generic-advanced-32ee8e9c-31e6-494c-a9ea-1a416cbfeca7' {
                    recordfail
                    load_video
                    gfxmode $linux_gfx_mode
                    insmod gzio
                    if [ x$grub_platform = xxen ]; then insmod xzio; insmod lzopio; fi
                    insmod part_msdos
                    insmod ext2
                    set root='hd0,msdos1'
                    if [ x$feature_platform_search_hint = xy ]; then
                      search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1  32ee8e9c-31e6-494c-a9ea-1a416cbfeca7
                    else
                      search --no-floppy --fs-uuid --set=root 32ee8e9c-31e6-494c-a9ea-1a416cbfeca7
                    fi
                    echo    'Ubuntu,KGDB with nokaslr ...'
                    linux   /boot/vmlinuz-4.10.0-19-generic root=UUID=32ee8e9c-31e6-494c-a9ea-1a416cbfeca7 ro find_preseed=/preseed.cfg auto noprompt priority=critical locale=en_US quiet kgdbwait kgdb8250=io,03f8,ttyS0,115200,4 kgdboc=ttyS0,115200 kgdbcon nokaslr
                    echo    'Loading initial ramdisk ...'
                    initrd  /boot/initrd.img-4.10.0-19-generic
            }
    

修改grub的配置后，需要执行sudo update-grub来更新。更新后目标机器就准备好了。  
重启按住shift,进入刚才添加的menu即可进入到被调试状态。

## 配置host

设置串口通信的波特率  
`sudo stty -F /dev/ttyS0 115200`  
要查看是否设置成功  
`sudo stty -F /dev/ttyS0`  
注意这个每次host重启都要再输入一遍，嗯，写个shell吧。

## 调试

编写config，用source加载（直接在gdb里输入也可）

    
    
    set architecture i386:x86-64:intel
    target remote /dev/ttyS0
    

使用gdb来调试带符号的vmlinux

    
    
    gdb -s /usr/lib/debug/boot/vmlinux-4.10.0-19-generic
    gdb > source config
    

符号加载完成，bt查看当前栈帧，c运行内核。  
  
  

## 查看源码遇到的问题

![](https://p2.ssl.qhimg.com/t01d7d4dd0e5c37d559.png)

可以看到，list本来应该显示具体的源码，但是这里只是打印出了它所在的文件，这是因为在这个路径下没有源码。  
所以说我们就建立这个路径，然后把源码放进去

  
然后dir设置好目录  
`dir /build/linux-hwe-edge-gyUj63/linux-hwe-edge-4.10.0`  
现在就可以查看源码了。  

## 单步调试

我从头开始说：

  * host  
target remote /dev/ttyS0  
按c继续运行target

  * target  
一开始停在下图这个地方，host按c之后，target继续运行进入系统  
  
然后输入`sudo su && echo g > "/proc/sysrq-trigger"`  
  
这时候target应该进入假死状态，其实就是完全动不了。  
这一步就是打开target的kgdb调试。

  * host  
这时候host那里不再是  
  
而是停下来了，可以下断了  
  
在你想要调试的函数下断点，然后按c，恢复target执行。

  * target  
这样就可以运行我们的poc了  

  * host  
回到host，此时应该已经停在断点了，然后按n可以单步调试。  
  

至此，内核调试的整个配置和调试方法都写完了。

## 参考链接

[ubuntu内核调试要点](http://advdbg.org/blogs/advdbg_system/search.aspx?q=%E5%86%85%E6%A0%B8%E8%B0%83%E8%AF%95&p=1)

## 其他

内核调试的坑实在太深，一开始参考了muhe师傅的文章用gdb+qemu调，然后编译了kernel
4.x之后，编译不报错，但是调试过程简直了，gdb花式挂不上去，看网上说某些版本要改gdb源码重新编译gdb……放弃了放弃了。  
感谢教我搭建双机调试的师傅……  
内核还是很容易调飞的，有时候花式加载不出来。

另外如果下载符号文件太慢，可以参考我的这篇文章，在虚拟机里用ss代理。  
<http://eternalsakura13.com/2018/02/02/proxy/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **sakura** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/105342](/post/id/105342)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [内核漏洞](/tag/内核漏洞)
  * [配置环境](/tag/配置环境)

 **+1** __3赞

 __收藏

![](https://thirdqq.qlogo.cn/qqapp/101430193/44110799D419F015C1D87EF97B55B122/40)
sakura

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

