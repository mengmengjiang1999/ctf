# Impress-CMS-1.4.2-自动任务处rce

阅读量 **147982**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-18 16:29:36

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t015d083188b9cec4b2.jpg)

## 前言

ImpressCMS 是一个开源内容管理系统，旨在轻松安全地管理多语言网站。

自动任务处存在任意代码执行，从而导致RCE

## 功能点分析

cms安装好之后，登陆管理员账号密码。大概是下面这个样子。

![](https://langke.bj.bcebos.com/delete/e6cfe4ce74904a5587257b42a4deeb40.png)

来到`Administration Menu`–`Auto Tasks`

![](https://langke.bj.bcebos.com/delete/255f21e026794a73b66ade006ea00e98.png)

点击`Create new task`，红框中自动执行就是自动执行的任务的源代码。

![](https://langke.bj.bcebos.com/delete/7fa9fae979ed405eb03fbd99ee34cf30.png)

现在我们不知道这个框中是否可以输入任意代码？即使可以输入任意代码，后续有没有过滤？  
下面从源码层面来分析一下。

## 源码分析

首先想到的是找到这个功能点对应的源码，一步步跟。但是这里看了下，过程有点多。于是决定采用关键字的方法。  
先随便创建一个任务

![](https://langke.bj.bcebos.com/delete/24da7d38f7514249b32c76de9c06e156.png)

通过抓包，找到`Source Code`窗口对应的关键字，关键字`sat_code`，响应了一个跳转，响应体为空。

![](https://langke.bj.bcebos.com/delete/bc84cb7d5420429e8da1f85f1e65d96c.png)

下面搜索这个关键字，跟一下它的处理过程。可以看到，主要集中在这三个文件中。

![](https://langke.bj.bcebos.com/delete/3f9a0582e87546c4bc80e9d014783b16.png)

先看下对这个关键字调用最少的文件：
`update-112-to-122.php`。是在一个创建数据库表的字段的位置。同时也通读了下这个文件，没有变量，没有输入，直接忽略。也并不一定说这个文件肯定没问题，只是这里不考虑。

![](https://langke.bj.bcebos.com/delete/a993777a17364a0283934f73c300af62.png)

下面看一下第二个相关文件：`modulesadmin.php`。  
第一处：将自动任务模块的任务添加到系统自动任务列表。生成处理程序对象，设置用户输入的值，传递给处理程序进行处理。

![](https://langke.bj.bcebos.com/delete/3dac640271724cd885a38b851fcc6910.png)

下面继续跟进处理程序  
处理程序位置：`/modules/system/admin/autotasks/class/autotasks.php`  
处理程序：`SystemAutotasksHandler`

![](https://langke.bj.bcebos.com/delete/62effd2252f64101954ec0aa28cd20e2.png)

最后，来到`/modules/system/admin/autotasks/class/autotasks.php`文件  
第一处：

![](https://langke.bj.bcebos.com/delete/daa9fcf3ba8447ca88d1d6447ac678ca.png)

第二处：

![](https://langke.bj.bcebos.com/delete/a4c5ea9c067b455ab0393648a77d72ac.png)

至此，`Source Code`窗口的处理过程基本分析完毕。可以看到，中间并没有对其进行过滤。可以直接执行任意代码。  
我的这种方法跟平时的过程调试不太一样，比过程调试、一步步跟代码，要快很多。  
当然，也可以补充一下过程调试，前面分析过，用户创建的任务，传递给了系统。

在核心启动过程结束时触发的函数，在如下位置下断点：

![](https://langke.bj.bcebos.com/delete/f336373548244e84a3438c8f9d037b86.png)

然后创建新的自动任务

![](https://langke.bj.bcebos.com/delete/55a569428c774d0ebe4b7e183d8653f7.png)

来到断点

![](https://langke.bj.bcebos.com/delete/eb4983c28ab0493d80644c58a11910db.png)

跟进`execTasks()`

![](https://langke.bj.bcebos.com/delete/98d10512ff974ced8ebc99c8452a88dd.png)

跟进`exec()`，可以看到，没有对要执行的代码做任何过滤和拦截。

![](https://langke.bj.bcebos.com/delete/24e1dd2ce8e24edda715f1e09619b363.png)

## 验证

创建自动任务

![](https://langke.bj.bcebos.com/delete/25f5029c6d5d45e0974471b0231cebd3.png)

执行

![](https://langke.bj.bcebos.com/delete/1cbe1a84c00e430ebdbeedabb40be8e6.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **langke** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254633](/post/id/254633)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [代码审计](/tag/代码审计)
  * [Impress](/tag/Impress)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhimg.com/t010857340ce46bb672.jpg) langke

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

