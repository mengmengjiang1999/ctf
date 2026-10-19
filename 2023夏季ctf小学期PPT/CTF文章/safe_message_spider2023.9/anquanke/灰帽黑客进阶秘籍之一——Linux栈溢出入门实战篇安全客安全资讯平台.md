# 灰帽黑客进阶秘籍之一——Linux栈溢出入门实战篇

阅读量 **350826**

|评论 **14**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-17 10:30:27

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0107167204b5bf7c4e.jpg)

## 前言

大家好，上一篇文章小弟发表/解了一个简单的pwn，剩下的2个level也已经有小伙伴帮忙解题了，感觉大家好像都挺喜欢该类型的。这次小弟打算开始写一个新的系列文章，如果写的不好，或者有什么意见、建议欢迎各位大佬点评。本篇文章为入门篇故仅提供了8个level的栈溢出练习实验，
**均未开启任何保护的** 。后面的文章会进一步升级。

## 下载、实验环境

实验代码下载：<https://pan.baidu.com/s/16bpbJoI5qdWctH3n6owqnw>  
实验环境：ubuntu 4.15  
辅助插件：Peda 下载地址：<https://github.com/longld/peda>

![](https://p0.ssl.qhimg.com/t01f873b45337ae75f2.png)

## 开始实验

本次实验环境分别为 level0-level7 均提供了源码和编译好的程序

###  level0

我们先查看一下c源码：

![](https://p4.ssl.qhimg.com/t0152d5ef8cffd372d0.png)

通过源码可以看出存在明显的栈溢出漏洞，我们先来运行看看，

![](https://p4.ssl.qhimg.com/t01a0382f71b178641d.png)

通过简单的输入12个A和6个6，可以看到我们还是没有成功，

![](https://p2.ssl.qhimg.com/t01796750af1cc98205.png)

当我们输入70个‘A’时，发现程序弹出 我们已经能成功更改‘modified’变量了。

###  level1

查看源码：

![](https://p5.ssl.qhimg.com/t0192f5f4f47b643b39.png)

下面我们运行一个这个程序，当我们不带任何字符时，程序给出

![](https://p5.ssl.qhimg.com/t0108fcea1643c34b55.png)

说明我们还在“argc”代码块。

当我们运行并带入20个“A”时，程序给出

![](https://p2.ssl.qhimg.com/t010951a5b492b50be5.png)

说明我们已经来到了“modified”函数出，但是我们还没到溢出点。

当我们运行并带入70个“A”时，程序给出

![](https://p4.ssl.qhimg.com/t01dd6513233118a2ab.png)

说明我们已经来到了“modified”函数出，并且我们也已经找到到溢出点。

（此处的0x41414141 为ascii码的 大写“A”）

通过上面简单的调试，我们就知道该怎么做了，如图：

![](https://p0.ssl.qhimg.com/t016c0e314464c76c60.png)

![](https://p3.ssl.qhimg.com/t015d677b9bdf114861.png)

###  level2

查看源码：

![](https://p0.ssl.qhimg.com/t0152110a9892c1a1c0.png)

下面我们运行一个这个程序，当我们不带任何字符时，程序给出

![](https://p0.ssl.qhimg.com/t01d03389e8b924a84d.png)

请让我们设置 ‘GREENIE’的环境变量，我们搜索一下看看本系统有没有，如图：

![](https://p2.ssl.qhimg.com/t01bd135cb64cf7c6e3.png)

可以看到在该系统中并没有设置定义，下面我们就设置一下看看

本次就写了一个python，运行

![](https://p2.ssl.qhimg.com/t01d603e4758724fafc.png)

![](https://p5.ssl.qhimg.com/t01c91148cf76037221.png)

###  level3

我们查看一下源码：

![](https://p5.ssl.qhimg.com/t01c551c59b3586f963.png)

下面我们运行一下这个程序看看，

![](https://p4.ssl.qhimg.com/t0133d22ad885dea565.png)

通过输入70个“A”，可以发现程序接收了我们的输入，并成功控制了内存地址指针，但是我们还是在main下的‘fp’函数判断处，通过源代码我们知道有个‘win’函数，我们查看一下

![](https://p1.ssl.qhimg.com/t0153565246d5edceea.png)

通过 objdump 搜索到了，该函数的地址 “0x08048424”

![](https://p3.ssl.qhimg.com/t011e164d6a95a32487.png)

（这里小伙伴们也可以使用IDA搜索）

下面我们就直接利用了

![](https://p3.ssl.qhimg.com/t01fdf87cfa078156a3.png)

如图，我们已经成功控制内存地址跳转到win函数并执行。

###  level4

我们查看一下源码：

![](https://p0.ssl.qhimg.com/t01a6b379351971b8ab.png)

可以看到源码里的‘win’函数被定义了，但是没有被程序直接调用，该等级还是一样，我们要控制内存指针到win函数运行。

下面我们开始如何判断偏移量，需要借助 gdb工具的 peda插件，能帮助我们节省很多工作

1.用gdb加载该level，并使用 “pattern_create” 来生产80个规律且均不一样的字符

2.使用 run 运行该程序，并输入刚刚生产的字符，回车

![](https://p5.ssl.qhimg.com/t012cb75b5c4b2d3a4d.png)

3.eip成功被改为 0x41344141

4.通过 “pattern_offset” 得出偏移量为 76个字节

![](https://p5.ssl.qhimg.com/t01a32ef3cccfbffae3.png)

最后我们确认一下该偏移量是否正确，如图：

![](https://p4.ssl.qhimg.com/t01b68e2e32d2731977.png)

![](https://p1.ssl.qhimg.com/t01919a79ebf6820480.png)

可以看到溢出位是正确的，下面我们跟上面一样继续搜索 ‘win’函数的地址

![](https://p4.ssl.qhimg.com/t01016c3d57f17404fd.png)

最后利用成功：

![](https://p4.ssl.qhimg.com/t0161f505050e14c42c.png)

###  level5

我们查看一下源码：

![](https://p4.ssl.qhimg.com/t01a113e4f6e0970976.png)

下面老规矩，我们来确定偏移量，操作如图：

![](https://p4.ssl.qhimg.com/t01e1c8ded0f82d3c2c.png)

![](https://p5.ssl.qhimg.com/t01ed92ee5f9d22bc67.png)

这里为什么要生产200个字符哪？因为我们要往内写入shellcode，所以我们要判断一下大概能写入多少字节，防止shellcode过大，无法放入的问题，

如图：

![](https://p3.ssl.qhimg.com/t01e58968e3057b5c2d.png)

可以看到刚刚生产的200个字符，覆盖掉偏移量后剩下的字符被成功放入，其实地址从 0xffffd0c8 – 0xffffd050 = 0x78
转化为十进制刚刚好是120个字节，故我们能写入一些正常的shellcode（msf生成的大部分为100个字节左右），

下一步我们就是直接编写exploit的了，如图：

![](https://p0.ssl.qhimg.com/t018e1b6193c7470a12.png)

76个‘A’后面跟的是ESP的地址上图有，后面带入10个‘nop’空指令（防止我们的shellcode被破坏），最后为shellcode代码
输出到s5.txt文件内，（该段shellcode代码为在本机开启1337端口等待链接
（其他更多功能shellcode，请移步[https://www.exploit-db.com/shellcodes））](https://www.exploit-db.com/shellcodes%EF%BC%89%EF%BC%89)  
下面我们让程序来加载s5.txt运行

![](https://p1.ssl.qhimg.com/t01bdea2a1c4d1f5518.png)

我们确认一下shellcode是否成功被执行，查看一下：

![](https://p4.ssl.qhimg.com/t011a7908ed231cba74.png)

本机1337端口成功被打开并等待链接，我们使用nc链接并成功拿到shell

![](https://p2.ssl.qhimg.com/t01462ad3bdee4a5167.png)

###  level6

我们查看一下源码：

![](https://p2.ssl.qhimg.com/t0177e0786b36d7642f.png)

下面老规矩，我们来确定偏移量，操作如图：

![](https://p2.ssl.qhimg.com/t01eebddc9b11f0aed1.png)

![](https://p1.ssl.qhimg.com/t01a8e75ed68a695e58.png)

偏移量为80，下面我们来确认一下偏移量是否正确，

![](https://p3.ssl.qhimg.com/t01de0dc2b173887c2c.png)

通过测试可以看到偏移量是对的，我们也能成功控制ESP，下面我们来确认查看写入内存空间的大小，如图：

![](https://p0.ssl.qhimg.com/t01b9a382d4a3e8b548.png)

可以看到一大堆，那写shellcode就够了，小弟懒就不去算了。。。

下面重点来了，这里可以看到我们的源代码处要求我们在0xbf00000内找ret，但是我们这里的环境没有这个地址，那怎么办呢？各位请注意，它不是要‘ret’吗？那我们就找一下本地系统的ret给它啊，反正我们不是也能控制指令吗？那么如图：

![](https://p2.ssl.qhimg.com/t012e2cbd23a98a5d98.png)

可以看到我们找到很多，这里就随便挑一个吧，所以我们这里的exp是这样的：

echo `python -c "print
'A'*80+'x5fx83x04x08'+'x44xd0xffxff'+'x90'*10+'x6ax66x58x6ax01x5bx31xf6x56x53x6ax02x89xe1xcdx80x5fx97x93xb0x66x56x66x68x05x39x66x53x89xe1x6ax10x51x57x89xe1xcdx80xb0x66xb3x04x56x57x89xe1xcdx80xb0x66x43x56x56x57x89xe1xcdx80x59x59xb1x02x93xb0x3fxcdx80x49x79xf9xb0x0bx68x2fx2fx73x68x68x2fx62x69x6ex89xe3x41x89xcaxcdx80'"`
> s6.txt

我们执行后，成功拿到shell

![](https://p1.ssl.qhimg.com/t016eacc7e9af515f80.png)

![](https://p5.ssl.qhimg.com/t0112caf2d926b0f58f.png)

###  level7

我们先查看一下源码

![](https://p2.ssl.qhimg.com/t01e4cc5b7247e59ef6.png)

下面老规矩，我们来确定偏移量，操作如图：

![](https://p1.ssl.qhimg.com/t01670d19f1b4b46ebd.png)

![](https://p0.ssl.qhimg.com/t0113af43d14073c81e.png)

‘ret’地址查找

![](https://p2.ssl.qhimg.com/t01fedcd450d9187f59.png)

下面我们来写个规范一点exploit脚本，如图：

![](https://p0.ssl.qhimg.com/t01810d187a715ab8dd.png)

（注：小弟在写这个exp的时候虚拟机重启一下，故 esp地址发生的改变，只需要获取新地址修改一下即可。shellcode为上面那个）

下面运行脚本，加载执行文件，如图：

![](https://p4.ssl.qhimg.com/t016c057b5f0f4733db.png)

成功拿到shell。

最后再说一下，本次文章中的前面几个level，均未开启任何保护，如图：

level7:

![](https://p1.ssl.qhimg.com/t01d0c79b7a8c38bb53.png)

level1:

![](https://p1.ssl.qhimg.com/t01c253e13a5009e759.png)

## 结语

通过本章的学习，相信小伙伴们也都能理解什么叫栈溢出，栈溢出是怎么调试操作的，希望各位小伙伴们也在自己环境中调试实验，希望小伙伴们都能理解，因为后面的文章难度会加高。最后祝您及家人生活愉快，新春快乐！！
：）

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **d3ckx1** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/169554](/post/id/169554)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [靶机](/tag/靶机)

 **+1** __14赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t017a53cae377f0cd5e.jpg) d3ckx1

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

