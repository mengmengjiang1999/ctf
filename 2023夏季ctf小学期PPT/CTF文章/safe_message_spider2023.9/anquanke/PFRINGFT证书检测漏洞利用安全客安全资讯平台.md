# PF_RING FT 证书检测漏洞利用

阅读量 **190277**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-08-05 16:30:30

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t013eb0b91fefc2c2ee.png)

## 0x01 PF_RING FT功能介绍

源码地址： <https://github.com/ntop/PF_RING>

简介：  
PF_RING™ FT is taking one step further, it assists any flow processing
application in the packet classification activity. PF_RING™ FT implements a
flow table that can be used to keep track of flows and provides many hooks to
be able to customize and extend it for building any type of application on top
of it, including probes, IDSs, IPSs, L7 firewalls.  
Although PF_RING™ FT is distributed with PF_RING™, it is possible to use the
library with any third-party packet capture framework (including Libpcap and
DPDK), as its data-ingestion API is capture-agnostic.

API： <https://github.com/ntop/PF_RING/blob/dev/doc/ft.rst>

## 0X02 安装过程

安装文档： <https://www.ntop.org/guides/pf_ring/get_started/git_installation.html>

FT 模式需要安装nDPI，nDPI源码地址： <https://github.com/ntop/nDPI>

## 0X03 利用过程

###  情报收集

搜到几篇文章，普遍认为pfring_ft_create_table 的 callq <license_init> 用于检测
license，只要修改这部分逻辑变可以利用该漏洞。

###  情报验证

1）运行PF_RING/userland/examples_ft/ftflow，程序提示需要购买一个证书

![](https://p4.ssl.qhimg.com/t014a8e310e8fd37665.png)

2）反汇编PF_RING/userland/examples_ft/ftflow，得到ftflow.s （objdump -d ftflow >
ftflow.s），重点关注pfring_ft_create_table 函数的2aa1e,2aa23两条指令

![](https://p1.ssl.qhimg.com/t01cdfcc132ed538811.png)

3）使用gdb调试PF_RING/userland/examples_ft/ftflow程序

    
    
    1. 在2aa1e处下断点。b *(&pfring_ft_create_table + 30)
    2. 设置启动参数。r -7 -i lo
    3. 修改PC寄存器跳过2aa1e指令。$rip=$rip+5
    4. 修改返回值。set $rax=0
    5. 继续运行。c
    

![](https://p5.ssl.qhimg.com/t01232f77f363ac9d39.png)

经过上述几处修改，可以看到没有无效证书的提示了，证明跳过callq <license_init>指令确实能绕过证书检测。

###  修改程序

1）搜索 e89d fcff ff85 c0，将 e89d fcff ff 换成 b800 0000 00

![](https://p4.ssl.qhimg.com/t01dffc9a3fb513f40e.png)

2）再次反汇编PF_RING/userland/examples_ft/ftflow

![](https://p2.ssl.qhimg.com/t01ed87ca0a269129e5.png)

3）运行PF_RING/userland/examples_ft/ftflow，确认ftflow已经无证书验证流程，证书检查已经被破解。

![](https://p1.ssl.qhimg.com/t018a6fed4e1a01670e.png)

## 0x04 技术延申

通过上述方法我们能够利用证书验证的漏洞破解ft模式的可执行程序，但是每次修改源码、重新编译程序都要重新修改，这样显然太麻烦了。我们需要继续分析ftflow的编译过程。经过查询各个层级的Makefile，pfring_ft_create_table函数定义在PF_RING/lib/libs/libpfring_ft_x86_64_dl.a/pfring_ft_table.o，我们0x0303的方法重新修改pfring_ft_table.o，然后重打包libpfring_ft_x86_64_dl.a，这样以来我们便可以反复调试ft的代码了。

## 0x05 总结

漏洞利用之前要做好情报收集工作，情报分析时要有取其精华取其糟粕的能力，当前流传的利用文章只能在作者自己的工作的环境复现，而且只是一个调试版本。所以我整理了一份通用版本。

PS： 这个漏洞已向ntop官方反馈，后续版本应该会修复，此漏洞仅限学习交流，切勿用于非法用途。

引用:

  * <https://www.freebuf.com/vuls/195887.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **nfalse** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/212356](/post/id/212356)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __4赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/48_48_100/t018779546973081d89.jpg?f=e7d531597a0bce2c56ec8531e36b9f1d)
nfalse

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

