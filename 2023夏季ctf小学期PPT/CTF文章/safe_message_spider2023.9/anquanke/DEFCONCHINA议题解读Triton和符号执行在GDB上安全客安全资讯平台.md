# DEFCON CHINA议题解读 | Triton和符号执行在 GDB 上

阅读量 **259086**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-05-15 12:02:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t016c0c5ecd68b0fe4c.jpg)

突突兔@DMZlab

## 讲师介绍：

陈威伯(陳威伯) 大三后开始学习资安，创立交大网路安全策进会也是 Bamboofox CTF team
的成员，台湾国立交通大学的一名硕士研究生，目前刚从SQLab毕业。

个人博客：<https://bananaappletw.github.io/>

GitHub：<https://github.com/bananaappletw>

邮箱：[bananaappletw@gmail.com](mailto:bananaappletw@gmail.com)

## 文章目录

1.什么是符号执行

2\. 介绍Triton

3.将GDB与符号执行结合起来的工具SymGDB

## 什么是符号执行

以前人们做逆向工程的时候有两种方法：

静态分析

动态分析

在静态分析中经常会使用到的工具：

Objdump

IDA PRO

在动态分析中经常会使用到的工具：

GDB

Ltrace

Strace

但是现在出现了一种新的逆向工程的分析方法：符号执行

符号执行 （Symbolic
Execution）是一种程序分析技术。其可以通过分析程序来得到让特定代码区域执行的输入。使用符号执行分析一个程序时，该程序会使用符号值作为输入，而非一般执行程序时使用的具体值。在达到目标代码时，分析器可以得到相应的路径约束，然后通过约束求解器来得到可以触发目标代码的具体值。

系统级别的符号执行工具：

S2e(<http://s2e.systems/>)

用户级别的符号执行工具：

Angr(<http://angr.io/>)

Triton(<https://triton.quarkslab.com/>)

基于代码的符号执行工具：

klee(<http://klee.github.io/>)

更多的资源可以在这里查看：

<https://github.com/ksluckow/awesome-symbolic-execution>

举个例子：

这段代码有个IF判断，有两个分支，一个是z等于12时会执行fail函数，z不等于12时会打印OK。

## Triton(https://github.com/JonathanSalwan/Triton)：

用C ++编写的动态二进制分析框架。

由Jonathan Salwan开发

Python bindings

Triton组件：

Symbolic execution engine

Tracer

AST representations

SMT solver Interface

Triton的结构：

接下来讲了一些Triton的应用和例子，由于文章篇幅有限就不进行阐述。

## SymGDB (https://github.com/SQLab/symgdb)

给GDB添加符号执行对插件

SymGDB结合了：

Triton

GDB Python API

Symbolic environment

Symbolize argv

GDB Python API

Failed method

Successful method

Flow

SymGDB System Structure

Implementation of System Internals

Relationship between SymGDB classes

Supported Commands

Symbolic Execution Process in GDB

Symbolic Environment

symbolic argv

Debug tips

SymGDB的结构：

SymGDB支持的命令：

SymGDB使用的Demo：

<https://github.com/SQLab/symgdb/tree/master/demo_videos>

SymGDB的缺点：

Triton不支持GNU C库

支持SMT语义：

https://triton.quarkslab.com/documentation/doxygen/SMT_Semanti

cs_Supported_page.html

Triton必须实现系统调用接口来支持GNU C库

Triton VS Angr：

## References

Wiki: https://en.wikipedia.org/wiki/Symbolic_execution

Triton: https://triton.quarkslab.com/

GDB Python API:https://sourceware.org/gdb/onlinedocs/gdb/Python-API.html

Peda:https://github.com/longld/peda

Ponce:https://github.com/illera88/Ponce

Angr:http://angr.io/

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **突突兔@DMZlab** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/144984](/post/id/144984)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Defcon China](/tag/Defcon China)
  * [DEFCON](/tag/DEFCON)
  * [议题解读](/tag/议题解读)

 **+1** __0赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/XaBDWRSsd025sicpiaVQOf7M26YDN1hRbIUPSRGOeuXVhKsSiasv3VoU5XctcrkyJibvFZK80w6gWntr0MOIFmWWjw/132)
突突兔@DMZlab

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

