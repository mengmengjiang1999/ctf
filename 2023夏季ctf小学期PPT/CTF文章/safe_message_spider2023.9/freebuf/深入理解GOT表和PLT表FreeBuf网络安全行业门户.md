作者：threepwn 合天智汇

## 0x01 前言  

操作系统通常使用动态链接的方法来提高程序运行的效率。在动态链接的情况下，程序加载的时候并不会把链接库中所有函数都一起加载进来，而是程序执行的时候按需加载，如果有函数并没有被调用，那么它就不会在程序生命中被加载进来。这样的设计就能提高程序运行的流畅度，也减少了内存空间。而且现代操作系统不允许修改代码段，只能修改数据段，那么GOT表与PLT表就应运而生。

## 0x02 初探GOT表和PLT表  

我们先简单看一个例子

![v2-eaa85e6df5c7dc0f87909583f6ee69ae_720w](https://pic1.zhimg.com/80/v2-eaa85e6df5c7dc0f87909583f6ee69ae_720w.jpeg)

我们跟进一下scanf@plt

![v2-0491b77a2dc372567dc088691d6e7516_720w](https://pic1.zhimg.com/80/v2-0491b77a2dc372567dc088691d6e7516_720w.jpeg)

会发现，有三行代码

    
    
    jmp 一个地址
    push 一个值到栈里面
    jmp 一个地址

看函数的名字就可以知道这是scanf函数的plt表，先不着急去了解plt是做什么用的，我们继续往下看我们先看一下第一个jmp是什么跳到哪里。

![v2-314a43f1c1e2b3cf0c0e14b6f6abef83_720w](https://pic4.zhimg.com/80/v2-314a43f1c1e2b3cf0c0e14b6f6abef83_720w.jpeg)

其实这是plt表对应函数的got表，而且我们会发现0x201020的值是压栈命令的地址，其他地方为0，此时就想问：

一、got表与plt表有什么意义，为什么要跳来跳去？

二、got表与plt表有什么联系，有木有什么对应关系？

那么带着疑问先看答案，再去印证我们要明白操作系统通常使用动态链接的方法来提高程序运行的效率，而且不能回写到代码段上。

在上面例子中我们可以看到，call scanf —> scanf的plt表
—>scanf的got表，至于got表的值暂时先不管，我们此刻可以形成这样一个思维，它能从got表中找到真实的scanf函数供程序加载运行。

我们这么认为后，那么这就变成了一个间接寻址的过程

![v2-20de0560853f029fa3b3e4232c2e502d_720w](https://pic1.zhimg.com/80/v2-20de0560853f029fa3b3e4232c2e502d_720w.jpeg)

我们就把获取数据段存放函数地址的那一小段代码称为PLT（Procedure Linkage
Table）过程链接表存放函数地址的数据段称为GOT（Global Offset Table）全局偏移表。我们形成这么一个思维后，再去仔细理解里面的细节。

## 0x03 再探GOT表和PLT表  

已经明白了这么一个大致过程后，我们来看一下这其中是怎么一步一步调用的上面有几个疑点需要去解决：

一、got表怎么知道scanf函数的真实地址？

二、got表与plt表的结构是什么？我们先来看plt表刚才发现scanf@plt表第三行代码是 jmp 一个地址 ，跟进看一下是什么

![v2-4990eed69a2b7caa09d4d02ab996f192_720w](https://pic1.zhimg.com/80/v2-4990eed69a2b7caa09d4d02ab996f192_720w.jpeg)

其实这是一个程序PLT表的开始（plt[0]），它做的事情是：

    
    
    push got[1]
    jmp **got[2]

后面是每个函数的plt表。此时我们再看一下这个神秘的GOT表

![v2-c38a6bf59d0f7e5cabc414245d060e81_720w](https://pic3.zhimg.com/80/v2-c38a6bf59d0f7e5cabc414245d060e81_720w.jpeg)

除了这两个（printf和scanf函数的push 0xn的地址，也就是对应的plt表的第二条代码的地址），其它的got[1]， got[2]
为0，那么plt表指向为0的got表干什么呢？因为我们落下了一个条件，现代操作系统不允许修改代码段，只能修改数据段，也就是回写，更专业的称谓应该是运行时重定位。我们把程序运行起来，我们之前的地址和保存的内容就变了在这之前，我们先把链接时的内容保存一下，做一个对比

![v2-4ab8f1f06d7dd3d1f0c44c122405ddd1_720w](https://pic3.zhimg.com/80/v2-4ab8f1f06d7dd3d1f0c44c122405ddd1_720w.jpeg)

    
    
    ② 寻找printf的plt表
    ③ jmp到plt[0]
    ④ jmp got[2] -> 0x00000
    ⑤⑥ printf和scanf的got[3] got[4] -> plt[1] plt[2]的第二条代码的地址
    ⑦⑧ 证实上面一点

运行程序，在scanf处下断点

![v2-a0be6e3cdcdd559556d6e8cb7c8d88bb_720w](https://pic2.zhimg.com/80/v2-a0be6e3cdcdd559556d6e8cb7c8d88bb_720w.jpeg)

可以发现，此时scanf@plt表变了，查看got[4]里内容

![v2-4a0d2e0cce578618842844cb74af0353_720w](https://pic4.zhimg.com/80/v2-4a0d2e0cce578618842844cb74af0353_720w.jpeg)

依然是push 0x1所在地址继续调试，直到这里，got[4]地址被修改

![v2-81a0ec04fac6a29c5878d36fbbc8e184_720w](https://pic1.zhimg.com/80/v2-81a0ec04fac6a29c5878d36fbbc8e184_720w.jpeg)

此时想问了，这是哪里？

![v2-67e10026e200097795d1190e4f799f46_720w](https://pic3.zhimg.com/80/v2-67e10026e200097795d1190e4f799f46_720w.jpeg)

![v2-ced317c3938ffbb117c41a7fc672e6b7_720w](https://pic1.zhimg.com/80/v2-ced317c3938ffbb117c41a7fc672e6b7_720w.jpeg)

然后就是got[2]中call<_dl_fixup>从而修改got[3]中的地址；

那么问题就来了，刚才got[2]处不是0吗，怎么现在又是这个(_dl_runtime_resolve)？这就是运行时重定位。

其实got表的前三项是：

    
    
    got[0]：address of .dynamic section 也就是本ELF动态段(.dynamic段）的装载地址
    got[1]：address of link_map object( 编译时填充0）也就是本ELF的link_map数据结构描述符地址，作用：link_map结构，结合.rel.plt段的偏移量，才能真正找到该elf的.rel.plt
    got[2]：address of _dl_runtime_resolve function (编译时填充为0) 也就是_dl_runtime_resolve函数的地址，来得到真正的函数地址，回写到对应的got表位置中。

那么此刻，got表怎么知道scanf函数的真实地址？

这个问题已经解决了。我们可以看一下其中的装载过程：

![v2-cfeafb30d49c7d1f2c095020b3fad1e8_720w](https://pic2.zhimg.com/80/v2-cfeafb30d49c7d1f2c095020b3fad1e8_720w.jpeg)

![v2-812bc1d83acf48908d5e6bfdd050cdce_720w](https://pic2.zhimg.com/80/v2-812bc1d83acf48908d5e6bfdd050cdce_720w.jpeg)

说到这个，可以看到在_dl_runtimw_resolve之前和之后，会将真正的函数地址，也就是glibc运行库中的函数的地址，回写到代码段，就是got[n]（n>=3）中。也就是说在函数第一次调用时，才通过连接器动态解析并加载到.got.plt中，而这个过程称之为延时加载或者惰性加载。

到这里，也要接近尾声了，当第二次调用同一个函数的时候，就不会与第一次一样那么麻烦了，因为got[n]中已经有了真实地址，直接jmp该地址即可。

## 0x04 尾记  

只是个人的见解，如有错误，希望各位大佬指出。

关联文章

栈溢出漏洞原理详解与利用

通过write实现信息泄漏

[](https://zhuanlan.zhihu.com/p/128593736)<https://www.freebuf.com/column/232415.html>

介绍信息泄露、GOT、PLT等相关概念，着重讲解信息泄露在缓冲区溢出中的重要作用。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

