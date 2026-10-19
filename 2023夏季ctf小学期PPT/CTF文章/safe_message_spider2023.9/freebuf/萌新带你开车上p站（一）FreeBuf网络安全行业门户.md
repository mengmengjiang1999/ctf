原创 萌新 合天智汇

0x01前言：

这一系列文章为pwnable.krToddlr’s
Bottle的全部题解，其中有三道题目相对而言稍难或者说比较经典，单独成篇，其他题目的题解放在一起发出来。

0x02fd

Ssh连接

![v2-fe47c1be910af69dfdc8a2a415d72b11_720w](https://pic1.zhimg.com/80/v2-fe47c1be910af69dfdc8a2a415d72b11_720w.jpg)

看一下目录

![v2-18ac33998c40158acb43b5ee9dce001c_720w](https://pic4.zhimg.com/80/v2-18ac33998c40158acb43b5ee9dce001c_720w.jpg)

我们需要执行flag，或者查看flag的内容

看题目的提示就知道这题和文件描述符有关

![v2-896f650f7fe5e87792195f703e2187ff_720w](https://pic2.zhimg.com/80/v2-896f650f7fe5e87792195f703e2187ff_720w.jpg)

看看源码

![v2-10e851edd1a350885f89dd06e3f27fd3_720w](https://pic4.zhimg.com/80/v2-10e851edd1a350885f89dd06e3f27fd3_720w.jpg)

在代码中我们可以看到要通过strcmp()比较后会输出

查看strcmp的用法

![v2-5c22e21984f362077e97a385e3a6231f_720w](https://pic2.zhimg.com/80/v2-5c22e21984f362077e97a385e3a6231f_720w.jpg)

可知，strcmp()中，若参数s1和s2字符串相同则返回0，s1大于s2则返回大于0的值，s1小于s2则返回小于0的值。

代码中要cat flag执行的话if语句应满足strcmp返回0，即buf的内容应为LETMEWIN

那么buf的值哪来的呢

man read可知

![v2-117b8ba0198cfaec33f2a5c4548ff916_720w](https://pic3.zhimg.com/80/v2-117b8ba0198cfaec33f2a5c4548ff916_720w.jpg)

buffer的值由read控制，从fd读入count个字节内容

fd在代码中的值为atoi(argv[1])-0x1234

atoi（）用于把字符串转换为整数

由linux下文件描述符可知（源码在/usr/include/unistd.h）

![v2-3f4d8dc09af3e8c0843f7db4fe6e98d2_720w](https://pic1.zhimg.com/80/v2-3f4d8dc09af3e8c0843f7db4fe6e98d2_720w.jpg)

即文件描述符0表示标准输入，也就是我们可以从命令行中控制的。

Atoi接收的参数我们可以控制，只要令argv[1]为0x1234（argv[0]为程序名称，argv[1]为输入参数），0x1234十进制为4660，经过运算最后赋值给fd的就是0，然后再传入read()，由于fd为0，所以我们在命令行中输入什么，则在buffer中写入的就是什么，只要输入LETMEWIN就可以了

分析完毕，接下来测试一下

![v2-7a04524f1ae8031b12f9f2a9fda14228_720w](https://pic3.zhimg.com/80/v2-7a04524f1ae8031b12f9f2a9fda14228_720w.jpg)

通过,logout关闭ssh连接

![v2-b3053b0b9eae9bbd9c982d25cac1db6a_720w](https://pic1.zhimg.com/80/v2-b3053b0b9eae9bbd9c982d25cac1db6a_720w.jpg)

0x02collision

![v2-69943c8f297f35b5f8e0bfc735c27f2e_720w](https://pic2.zhimg.com/80/v2-69943c8f297f35b5f8e0bfc735c27f2e_720w.jpg)

看题目描述应和哈希碰撞相关

![v2-364572ce8d5ba9633da8e75c137758b9_720w](https://pic4.zhimg.com/80/v2-364572ce8d5ba9633da8e75c137758b9_720w.jpg)

看看源代码

![v2-81ac7db52afc0e23d6fe5559800212e1_720w](https://pic2.zhimg.com/80/v2-81ac7db52afc0e23d6fe5559800212e1_720w.jpg)

在main（）中看到传入的argv[1]需要满足条件：

长度为20字节，传给check_password后的返回值为硬编码的0x21dd09ec

那么我们需要来看一下check_password的逻辑

可以看到传参为char型指针，在逻辑中被强制类型转换为int型指针

从大小的角度来看即1字节转换为4字节，一共20字节，20/4=5，刚好对应for循环里的5次，for循环是做了个累加的操作，即累加和等于0x21DD09EC即可

emmm简单理解，就是说输入20字节，每4字节一组，共5组，5组相加后等于0x21dd09ec即可。

这就很简单了

我设16个字节为0x1，那么另外的4字节应为差值0x1dd905e8，又因为小端序，所以写的时候倒过来写即可，如下所示

![v2-d069bad076568bf3622b184daea96af9_720w](https://pic3.zhimg.com/80/v2-d069bad076568bf3622b184daea96af9_720w.jpg)

0x03bof

根据题目描述这是一道缓冲区溢出的题目

![v2-b314e9b6507ea3845ea6a6b0a151cdfa_720w](https://pic3.zhimg.com/80/v2-b314e9b6507ea3845ea6a6b0a151cdfa_720w.jpg)

下载bof及其代码

![v2-6d02b9721e9bb9f0a268037dd56be95c_720w](https://pic1.zhimg.com/80/v2-6d02b9721e9bb9f0a268037dd56be95c_720w.jpg)

看看源码

![v2-b285791afa2558df830bfb64be1474ea_720w](https://pic3.zhimg.com/80/v2-b285791afa2558df830bfb64be1474ea_720w.jpg)

看到main中调用了func，传参为0xdeadbeef

而func()中可以看到需要传参为0xcafebabe才可以getshell

我们注意到func中我们可以通过gets控制输入，gets像本题的这种用法是非常危险的，容易造成缓冲区溢出攻击，这次我们就来pwn掉它

我们尝试输入写字符看看

![v2-4b2591e829b08b435fc98f19c5b71d98_720w](https://pic3.zhimg.com/80/v2-4b2591e829b08b435fc98f19c5b71d98_720w.jpg)

那么基本的思路有了，就是找到确定的偏移，然后使用0xcafebabe覆盖0xdeadbeef。

偏移是多少呢

配合gdb来看看

![v2-c7e69a09d89cd84fcb4f0c858f6025b4_720w](https://pic2.zhimg.com/80/v2-c7e69a09d89cd84fcb4f0c858f6025b4_720w.jpg)

在main下断点

输入r启动

![v2-94cfdbaeb0239723ee5f1c60cabd2b6e_720w](https://pic1.zhimg.com/80/v2-94cfdbaeb0239723ee5f1c60cabd2b6e_720w.jpg)

在断点处停下了

我们反汇编func看看比较key和0xcafebabe指令在哪儿

![v2-ef6c8262abe8adac592ea471bed1555d_720w](https://pic2.zhimg.com/80/v2-ef6c8262abe8adac592ea471bed1555d_720w.jpg)

看到上图的红框中的cmp指令了，这就是关键

可以看到地址是0x56555654

在这里下个断点

![v2-b019fe6072f1c50c0ddcbfd8cd247c0b_720w](https://pic4.zhimg.com/80/v2-b019fe6072f1c50c0ddcbfd8cd247c0b_720w.jpg)

按c继续执行

![v2-219e6261c68aabcb30955903c9fa2336_720w](https://pic4.zhimg.com/80/v2-219e6261c68aabcb30955903c9fa2336_720w.jpg)

命中第二个断点后，我们来看看栈的布局

![v2-0577ccd8c6efd6dc78e78fbe15e66ede_720w](https://pic2.zhimg.com/80/v2-0577ccd8c6efd6dc78e78fbe15e66ede_720w.jpg)

可以看到0xdeadbeef在0xffffd330,而我们输入的A是从0xffffd2fc开始

emmm，数一下，从最开始的0x41到0xdeadbeef之前查了13*4=52个字节，在53-56处写入0xcafebabe覆盖掉原有的0xdeadbeef即可

编写pwntools脚本

![v2-69645eb777a1d4817a4775419f201771_720w](https://pic2.zhimg.com/80/v2-69645eb777a1d4817a4775419f201771_720w.jpg)

测试如图，打回了一个shell

![v2-bae5c2d0d74a01142dbbc5eca5cbfc72_720w](https://pic3.zhimg.com/80/v2-bae5c2d0d74a01142dbbc5eca5cbfc72_720w.jpg)

未完待续！

《缓冲区溢出基础与实践》：主要介绍了缓冲区溢出基础与实例，通过本实验的学习，你能够了解缓冲区溢出的原理与危害，掌握防范缓冲区溢出的基本方法，学会进行常见的缓冲区溢出攻击。

阅读原文做实验：

[实验:缓冲区溢出基础与实践(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=9613f998-8cd2-4981-9bc5-9900c97371de)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

