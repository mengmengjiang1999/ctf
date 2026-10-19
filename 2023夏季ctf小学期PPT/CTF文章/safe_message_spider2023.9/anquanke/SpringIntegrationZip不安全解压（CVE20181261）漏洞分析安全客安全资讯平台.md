# Spring Integration Zip不安全解压（CVE-2018-1261）漏洞分析

阅读量 **187224**

发布时间 : 2018-05-12 13:43:39

 **x**

##### 译文声明

本文是翻译文章，文章来源：https://mp.weixin.qq.com/

原文地址：<https://mp.weixin.qq.com/s/SJPXdZWNKypvWmL-roIE0Q>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01b74f8c481b63d2d3.png)

作者：Gyyyy@猎户安全实验室

## 0x00 漏洞概览

**漏洞名称：** Spring Integration Zip不安全解压

**漏洞编号：** CVE-2018-1261

**漏洞级别：** 严重（官方定级，比高危还高）

**漏洞危害** **：** 在spring-integration-zip.v1.0.1.RELEASE之前的版本中，恶意用户通过在压缩文件中构造包含有特定文件名称的文件（受影响文件格式有bzip2, tar, xz,
war, cpio, 7z），应用程序使用spring-integration-zip进行解压时，会导致跨目录任意写入文件漏洞的攻击。进而有可能被Getshell， **远程控制** 。

**漏洞加固：** 更新升级， _zip.v1.0.2.RELEASE版本_

**漏洞利用前置条件：**

  1. 使用了spring-integration-zip库
  2. 接收并解压了来自不可信来源的压缩文件

## 0x01 漏洞分析

补丁比对

![](https://p5.ssl.qhimg.com/t012c2a00d437ad7da8.jpg)

zip.v1.0.1.RELEASE在`UnZipTransformer`调用`ZipUtil.iterate()`时定义的回调中增加了一段对文件名称校验的代码片段
_（在5月11日凌晨更新的zip.v1.0.2.RELEASE版本中，对`Byte[]`类型的分支逻辑也增加了文件名称校验，并且删除了对名称中`..`的判断，直接校验名称是否以工作区目录开头）_。

通过上述内容我们大致可以猜测这个漏洞的原理：攻击者可以通过构造一个包含名称带`../`前缀的文件的压缩包，使spring-integration-zip进行解压时该文件跳出解压目录被创建。

而且在zip.v1.0.1.RELEASE也增加了对这类压缩包的测试用例，并且十分贴心的附上了一个“恶意”的压缩包测试文件zip-malicious-traversal.zip。

我们先看看这个压缩包长什么样子：

![](https://p0.ssl.qhimg.com/t0186cdffcde64cd2ff.jpg)

稍微说明一下：

  * 右上，压缩包正常打开的目录结构
  * 右下，压缩包的文本形式数据
  * 左，压缩包解压后的目录结构

从文本数据中不难看出，这个压缩包中存在一个以很多`../`开头为名称的文件evil.txt。以压缩工具打开查看时，它以目录树形式显示，而解压后最深层的有效目录及文件被提取至根目录
_（说明使用的这个工具不存在这类解压漏洞）_ 。

这样就可以很清楚的知道，这个压缩包如果被zip.v1.0.0.RELEASE解压，evil.txt文件将会被写入工作区目录对应盘符下的tmp目录中。

搭个调试环境跑起来看看。

## 0x02 环境搭建

  1. IDE：IDEA
  2. JDK：1.7
  3. Libraries 
    * spring-integration-zip.1.0.0.RELEASE
    * spring-integration-core.4.3.10.RELEASE
    * spring-integration-file.4.3.10.RELEASE
    * zt-zip.1.11

关键代码如下 _（参考官方测试用例即可）_ ：

![](https://p0.ssl.qhimg.com/t01d610bc15c3a3b3ff.jpg)

#### **流程跟踪**

流程很简单，示例中的`UnZipTransformer.transform()`会调用`doZipTransform()`解压，在遍历压缩包内目录及文件时，回调`ZipEntryCallback.process()`对其进行处理。

当遍历到evil.txt时，它被识别为一个文件，而并不是多层的目录结构，那一堆乱七八糟的只是它的文件名：

![](https://p4.ssl.qhimg.com/t01e5c26c3533b1c8fc.jpg)

_而对正常压缩包遍历到目录时应该是这样的：_

![](https://p2.ssl.qhimg.com/t016b9f59f45aced514.jpg)

然后根据文件名在工作区目录中创建对应文件 _（子目录会在遍历时被提前创建）_
，并调用org.apache.commons.io包中的`IOUtils.copy()`复制文件数据。

此时，解压的文件名被转换为绝对路径： __

_程序运行结束，查看E:\tmp\目录下发现evil.txt文件（由于Win操作系统默认没有/tmp目录，因此我在测试前提前创建了一个，也可以直接使用已存在目录，如Web
Root:P）：_ __

## 0x03 POC生成

知道了漏洞原理后，我们比较好奇的是如何生成这种特殊的压缩文件，已知方法有 _（如果有更方便的方法，请告诉我）_ ：

  1. 用二进制数据构造符合压缩包数据结构的文件
  2. 使用spring-integration-zip压缩

我们用方法2做个测试，关键代码如下：

![](https://p3.ssl.qhimg.com/t01c5c94a8bef815989.jpg)

![](https://p3.ssl.qhimg.com/t01754d8aae21393ba5.jpg)

再解压试试

![](https://p3.ssl.qhimg.com/t01c8a0d39555f11455.jpg)

**可以看到hw.txt跳出解压目录外层来了，OK，打完收工。**

## 参考

  1. https://pivotal.io/security/cve-2018-1261
  2. https://github.com/spring-projects/spring-integration-extensions/

本文翻译自https://mp.weixin.qq.com/
[原文链接](https://mp.weixin.qq.com/s/SJPXdZWNKypvWmL-roIE0Q)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **猎户攻防实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/144775](/post/id/144775)

安全客 - 有思想的安全新媒体

本文转载自: [https://mp.weixin.qq.com/](https://mp.weixin.qq.com/s/SJPXdZWNKypvWmL-roIE0Q)

如若转载,请注明出处： <https://mp.weixin.qq.com/s/SJPXdZWNKypvWmL-roIE0Q>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全漏洞](/tag/安全漏洞)
  * [远程执行](/tag/远程执行)
  * [CVE-2018-1261](/tag/CVE-2018-1261)
  * [Spring Integration Zip不安全解压](/tag/Spring Integration Zip不安全解压)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t0135f56f976068ac41.png) 猎户攻防实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

