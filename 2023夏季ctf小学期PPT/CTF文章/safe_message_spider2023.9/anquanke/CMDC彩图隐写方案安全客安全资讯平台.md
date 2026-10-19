# CMD-C彩图隐写方案

阅读量 **1506571**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-12-18 15:30:23

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01e3ae398ab0a4575e.jpg)

## 1.前言

本文提出了当前经典的彩图隐写方案，它具有聚类修改方向的特点，是第一个公认的彩色图隐写方案，为后续彩图隐写术和隐写分析工作提供了清晰的思路，具有深远的意义。

## 2.背景

现代灰度图像隐写方案是在最小化失真函数框架下设计的，流行的隐写方案包括HUGO、WOW、S-UNIWARD、MG、HILL等。

在彩色图像中，一些临时的隐写方案假定可以将每个颜色通道独立地视为灰度图像进行嵌入。由于这些方案未考虑颜色通道之间的相关性，因此可能会留下明显的隐写痕迹，而这些痕迹很容易被最新的彩色隐写分析模型捕获，例如CRM（color
rich model，彩色富模型）和CCRM（channel correlation rich model，色彩丰富的通道相关模型）等。

2015年，有学者提出了一个可应用于灰度图隐写领域的CMD（clustering modiﬁcation
directions，聚类修改方向）隐写策略，它保证了嵌入秘密信息后局部区域修改的方向相同，从而使得隐写痕迹不易被检测到，这有效提高了灰度图像隐写术的安全性。

## 3.彩图隐写方案

### 3.1综述

在本文中，借鉴灰度图的CMD策略，提出了一种应用于彩色图像的隐写策略，称为CMD-C（clustering modification directions
for color
components，彩色成分的聚类修改方向），其目的不仅在于保留颜色通道内的相关性，而且还保留颜色通道之间的相关性。为了实现此策略，可分解每个颜色通道图为几个子图像，将分段的秘密信息按照设定的顺序嵌入到所有子图像中。嵌入期间，嵌入成本根据邻域的六个像素值进行更新，其中四个像素值来自同一颜色通道的四个相邻像素，另两个像素值来自两个其他颜色通道但在相同像素位置的两个像素。提出的策略可以与WOW和HILL等最新的隐写方案结合使用，有效抵抗针对彩色图像的隐写分析，具有很高的安全性。

### 3.2彩色图像信息嵌入简述

嵌入到图像中的秘密信息都被转换成1或-1的形式，因此对于图像像素来说，嵌入修改的情况有三种，即+1、-1、0。这种嵌入形式即是典型的三元嵌入方式。  
做如下声明：

![](https://p1.ssl.qhimg.com/t01d5fc495492d06a9c.png)

则嵌入成本的三种表示方式为：

![](https://p2.ssl.qhimg.com/t01697838dbb8d1c72c.png)

上述公式中，L和W是图像的长度和宽度，D是颜色通道的数量。

### 3.3CMD-C隐写方案

CMD-C方案详细步骤如下。

![](https://p1.ssl.qhimg.com/t01ba1f204898d4a5e0.png)

![](https://p5.ssl.qhimg.com/t018836ca40b727cd03.png)

![](https://p1.ssl.qhimg.com/t013e68f5fd26f015fd.png)

![](https://p0.ssl.qhimg.com/t011bb2d6c52e786dd9.png)

![](https://p3.ssl.qhimg.com/t015d33550d6689fb47.png)

![](https://p1.ssl.qhimg.com/t016001e57fb6ddd547.png)

![](https://p3.ssl.qhimg.com/t0179347fb11dca8d07.png)

## 4隐写方案测试与分析

### 4.1实验基本配置

主要的隐写算法是：HILL、WOW、HILL-CMD、WOW-CMD、HILL-CMD-C、WOW-CMD-C。

使用了CFA去马赛克算法（PPG）和降采样算法（LAN、BIL、BIC、Nearest-neighbor）处理基础数据集BOSSBase，生成四个实验数据集：BOSS-LAN、BOSS-BIL、BOSS-BIC、BOSS-NN。

使用传统的隐写分析方案检测此隐写方案的安全性。本文涉及的传统隐写分析方法是：SRM、CRM、CCRM和SCCRM。

### 4.2隐写检测分析

实验结果如下图。结果表格中，纵轴是隐写术方案，它们的隐写率均为0.4，横轴是隐写分析方案，表格中数值是隐写检测的错误率。

分析可知，通过CRM和SCCRM可以很容易地检测到WOW和HILL，基于CMD的方案比WOW和HILL的隐写安全性较好，基于CMD-C的方案的隐写术安全性最佳。在SRM隐写检测结果中，HILL-CMD的性能优于WOW-CMD-C，但在CRM或CCRM隐写检测结果中，HILL-CMD性能不如WOW-CMD-C，这表明HILL-CMD比WOW-CMD-C保留的空间相关性更好，WOW-CMD-C比HILL-CMD保留的颜色通道相关性更好。

![](https://p1.ssl.qhimg.com/t01b662c3db1d581c8f.png)

### 4.3贡献

(1)基于仿真实验结果，证明了保留彩色图的颜色通道间的相关性带来了更高的安全性。

(2)提出了用于彩色图像隐写术的CMD-C策略，该策略可以灵活地将灰度图隐写术（例如WOW和HILL）应用于彩色图隐写领域中。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **nggq_HYWZ** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/194988](/post/id/194988)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [隐写](/tag/隐写)

 **+1** __1赞

 __收藏

![](https://p1.ssl.qhimg.com/t01a946574905e1feb3.png) nggq_HYWZ

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

