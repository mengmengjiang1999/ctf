在正式开始之前，说明一下，本篇文章一方面算是完成瑞不可当团队交代的作业之一，另一方面算是在各位技术大牛针对这个漏洞的分析文章的基础之上来个锦上添花。所以，要先感谢之前各位大牛针对这个漏洞(CVE-2022-0847)的详细描述，我只是从gdb调试的角度来复现这个漏洞的利用过程（本次是从用户态层面调试，下次是从内核态层面调试），参考文章很多，不一一列举，包括但不限于如下内容：

> 《大白话图解 Linux 脏管道(Dirty Pipe) 漏洞(CVE-2022-0847)》
>
> [
> _https://blog.csdn.net/weixin_44820088/article/details/123364275_](https://blog.csdn.net/weixin_44820088/article/details/123364275)
>
> 《Linux内核权限提升漏洞“DirtyPipe”（CVE-2022-0847）分析》
>
> [
> _https://mp.weixin.qq.com/s/RoGHvNW2Y6dZOjgsBVVm5Q_](https://mp.weixin.qq.com/s/RoGHvNW2Y6dZOjgsBVVm5Q)

##  **一、Exp文件的编译执行**

从这个地址下载exp文件并编译：

<https://haxx.in/files/dirtypipez.c>

![](https://image.3001.net/images/20220422/1650615951_6262668f6a92b95c02af8.png!small)

该exp执行效果简单直接，一步到位：![](https://image.3001.net/images/20220422/1650615992_626266b85d148a1f6860f.png!small)

该漏洞的另外一种利用方法的介绍也可以参看如下链接发布的内容：

<https://mp.weixin.qq.com/s/nfX29mmLbkLtmr-055oX1Q>

##  **二、EXP文件的两个要素：**

整个exp有详细的备注内容，非常清晰。我这里就说两个关键要素：

> 关键结构体pipe-buf指向某个page，实际指向了suid文件。我们在exp执行过程中使用/usr/bin/chsh这个文件，意思就是pipe-> buf指向了/usr/bin/chsh这个文件。
>
> 关键结构体pipe-buf 带着PIPE_BUF_FLAG_CAN_MERGE，意思就是还可以向这个page中写入内容。

结合这两个关键因素，就相当于可以向/usr/bin/chsh文件中写入内容，就这样一个只是可读的suid就变成了可写的文件。至于写成什么样子，就是各个exp攻击灵活的地方了。但是根本上同时构建这两个要素就是所有该漏洞exp的基础。

##  **三、EXP执行过程中用户态动态调试**

###  **第一阶段：main函数准备环节**

Gdb进入main函数：![](https://image.3001.net/images/20220422/1650616728_6262699896b072bc62638.png!small)

设置main断点，一步一步调试：
![](https://image.3001.net/images/20220422/1650616795_626269db3eb35ab674416.png!small)

这一段就是将fd中的从第1个字节开始算起，406个字节长度的内容拷贝到orig_byte中。
备份好，后面恢复的时候会使用上。![](https://image.3001.net/images/20220422/1650616823_626269f7e1c69d5d5b106.png!small)

其中对应的data如下内容：  
![](https://image.3001.net/images/20220422/1650616879_62626a2f711e51c37b076.png!small)

其中，/usr/bin/chsh获得的fd如下：![](https://image.3001.net/images/20220422/1650616946_62626a7244a3ac6e69f09.png!small)

对应的elfcode的长度为406：![](https://image.3001.net/images/20220422/1650616978_62626a92c21b349cf7f00.png!small)

这里的0x7f被注释掉，因为用不到，因为fd会设置offset为1。![](https://image.3001.net/images/20220422/1650617030_62626ac69e5894adf5195.png!small)

至此，main函数完成了准备阶段，将/usr/bin/chsh的offset为1之后的406个字节拷贝到orig_bytes中。

###  **第二阶段：exp的hax函数**

源码如下：

![](https://image.3001.net/images/20220422/1650617267_62626bb376bce77acdd41.png!small)

关键是进入到hax中去执行：![](https://image.3001.net/images/20220422/1650617288_62626bc82f247787209dd.png!small)

汇编代码进入hax函数：

![](https://image.3001.net/images/20220422/1650617358_62626c0e700ac04f0c622.png!small)

解释一下：file就是/usr/bin/chsh, offset 设置为1，data指向我们构建好的elfcode，len就是406个字节。

![](https://image.3001.net/images/20220422/1650617413_62626c45727b227f6de2e.png!small)![](https://image.3001.net/images/20220422/1650617434_62626c5acc8097e384871.png!small)是的，再次打开suid文件：

![](https://image.3001.net/images/20220422/1650617479_62626c87c3e23a0c26205.png!small)是的，再次得到3：

###
![](https://image.3001.net/images/20220422/1650617517_62626cad2b2d5dd7b89c1.png!small)
**第三阶段：进入prepare函数**

进入这个函数的目的就是实现关键要素里面的第二个要素。

![](https://image.3001.net/images/20220422/1650617666_62626d4219446e0f5a65e.png!small)此时p[2]

![](https://image.3001.net/images/20220422/1650617691_62626d5b0e0b382ccfbe1.png!small)

栈上的一堆乱码而已。完成pipe之后：

![](https://image.3001.net/images/20220422/1650620969_62627a298728b27216dfc.png!small)接着两个for循环：

![](https://image.3001.net/images/20220422/1650617716_62626d74c8d2015f43835.png!small)

其中buffer的大小为4096，

![](https://image.3001.net/images/20220422/1650617795_62626dc3827036dad0db7.png!small)

而r的初始大小为65536![](https://image.3001.net/images/20220422/1650617875_62626e138707ac5ff1df0.png!small)![](https://image.3001.net/images/20220422/1650617909_62626e35a8b62bbfaf099.png!small)两个for循环的操作下来的效果就是16个page，连续注入和然后连续清空。目的就是保存flag为0x10，就是can
merge后续的内容，这里留个悬念，我会在复现内核态的gdb调试效果里面展开。

###  **第四个阶段：进入splice函数**

这个环节主要目的就是实现exp的第一个要素：

![](https://image.3001.net/images/20220422/1650618072_62626ed861d5137517e16.png!small)还记得上面获得pipe

![](https://image.3001.net/images/20220422/1650618106_62626efa3791568592151.png!small)这里就是说，根据如下的描述：

![](https://image.3001.net/images/20220422/1650618129_62626f114dc913f480d77.png!small)从/usr/bin/chsh
这个文件的offset为0的地方开始，move（传递，搬动）一个1字节的内容到，pipe的出口fd的offset为0的地方。

![](https://image.3001.net/images/20220422/1650618144_62626f208e3cb28f350c7.png!small)Flag为0，不是上面这些数值，说明正常处理，不做其他特殊处理：

![](https://image.3001.net/images/20220422/1650618208_62626f6094b15696aa770.png!small)这里的splice的效果非常妙，是整个漏洞的核心，在内核态（很快我会来补充这个漏洞在内核态的gdb的调试效果），效果就是将/usr/bin/chsh的page，挂到了pipe管道结构体中的pipe_buffer上。从这张图中的信息，就是pipe-buf通过splice函数的操作，直接指向了我们在程序设置/usr/bin/chsh文件，碰巧同时pipe-buf指向的page还保留了PIPE_BUF_FLAG_CAN_MERGE这个flag。

###  **第五阶段：改造可写的suid文件**

目前为止，已经凑齐了两个要素，剩下的就是充分利用内存中这个可写的suid文件page：

接着向pipe中写入我们之前准备的elfcode内容。

![](https://image.3001.net/images/20220422/1650618319_62626fcfbef3be4ca2661.png!small)这里的data就是我们前面准备的elfcode，而len就是elfcode的长度。Write完成之后，查看一下nbytes的数值：

![](https://image.3001.net/images/20220422/1650618416_6262703007de15708a6d4.png!small)Ok，说明顺利将elfcode写入到了suid文件中，现在的suid就是我们想要的样子了。下面就好办了。

![](https://image.3001.net/images/20220422/1650618434_626270427f085817155c0.png!small)最后hax函数收尾。下面就又回到main函数中了。

###  **第六阶段：执行全新的suid文件和收尾**

Call hax之后就回到main了：

![](https://image.3001.net/images/20220422/1650618452_62627054ea5d1d2adc4d4.png!small)这个阶段的源码如下三个部分：

![](https://image.3001.net/images/20220422/1650618479_6262706fbe89049031bd8.png!small)

第一个部分就是先执行新的suid程序，最终会产生能够产生/tmp/sh文件，该文件可以启动root权限的shell。

![](https://image.3001.net/images/20220422/1650618497_6262708144a8de0c4f407.png!small)第二个部分就是还是使用hax函数来恢复我们修改过的suid的文件为最初的suid，如何恢复，使用我们最初保存的orig_bytes,这样做还是比较讲究的，执行完收尾工作。

![](https://image.3001.net/images/20220422/1650618627_62627103d8522ce58a897.png!small)第三个部分就是整个exp的结尾，启动具有root权限的shell

![](https://image.3001.net/images/20220422/1650619850_626275cadf0db09e1df61.png!small)这个阶段的三个部分调试之前，在还未执行该system(path)之前，tmp文件夹的内容如下：

![](https://image.3001.net/images/20220422/1650618648_626271182c5a14738ee12.png!small)

之所以，这个三个部分一起调试，是因为system函数会产生子进程，该子进程回去执行elfcode的操作：

![](https://image.3001.net/images/20220422/1650618810_626271ba084433d2c5acf.png!small)执行一下，gdb直接到了shell：

![](https://image.3001.net/images/20220422/1650618839_626271d727f44c7c4fb5d.png!small)同时tmp文件下也产生了对应的sh文件。

![](https://image.3001.net/images/20220422/1650618862_626271ee25e4b216d20fc.png!small)可以看到tmp文件夹下也生成的sh文件。至此，gdb在用户态的调试也结束了，可以看到顺利拿到shell。后续，会详细分析内核态下两个关键要素的状态。

