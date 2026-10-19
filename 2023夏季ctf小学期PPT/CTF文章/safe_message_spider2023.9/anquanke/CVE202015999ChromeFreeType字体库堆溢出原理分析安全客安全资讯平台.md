# CVE-2020-15999：Chrome FreeType字体库堆溢出原理分析

阅读量 **322194**

发布时间 : 2020-11-06 16:30:56

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t013e452edfb973e023.jpg)

## 漏洞简介

Google发布公告，旧版本的 chrome 浏览器的 FreeType字体库中存在堆溢出，被利用可能导致 RCE（远程代码执行）。

安全专家建议用户尽快升级到86.0.4240.111 之后的版本，以解决风险。

## 漏洞原理

###  一、TTF 嵌入图片

TTF 字体支持嵌入 PNG 格式的图片作为字形数据，在嵌入时图片数据会被保存在字体文件的 SBIX 表格中，在处理时会通过提取 SBIX 表中的 PNG
中存取的信息来实现字体渲染。SBIX 表中的格式如下图：

![](https://p0.ssl.qhimg.com/t0138925c1365aa103b.png)

SBIX 中的 strikeOffset 存储了 Strikes 的数据信息的偏移，Strikes 中的 glyphDataOffset
存储了具体的字形信息的偏移，Strikes 格式和字形信息的格式如下图：

![](https://p2.ssl.qhimg.com/t016fd8a4b325c8ccfd.png)

![](https://p3.ssl.qhimg.com/t01969b485d4d066d55.png)

字形信息中的 data 存储了被嵌入的图片信息。下面是样本中的 SBIX 和存储的图片信息。

![](https://p0.ssl.qhimg.com/t01ad1566d8a73105f2.png)

PNG 图片信息被保存在了 hex(0x1a30 + 0x5aaec + 0x8) = 0x5c524 处。通过 IHDR
可以看到图片的一些基本信息，具体信息如下图：

![](https://p5.ssl.qhimg.com/t01b849a5bd29ec8479.png)

###  二、Load_SBit_Png 函数实现

FreeType 库中 PNG 图片信息的提取是通过 Load_SBit_Png 函数实现的。Load_SBit_Png 函数的处理流程如下：

1、将字形信息中 data 指向的内存解析为 PNG  
2、提取被解析后图片的 IHDR 存储的信息（图像宽度和高度，深度及颜色类型等）  
3、将解析后的信息提取到字形信息中  
4、按照之前解析到信息开辟内存用于保存图片信息

###  三、漏洞原理

漏洞发生在将解析到的图片信息提取到字形信息过程中，PNG 图片中的 IHDR 存储的宽度和高度的数据类型为 uint32，在存储到字形信息时，会被转换为
unsigned short 类型，此时如果图片的宽度和高度信息大于 0x7FFF 则会发生截断。

![](https://p0.ssl.qhimg.com/t0196d15119f8b18e5b.png)

之后字形信息中存储的相应数据会被传递到用于存储 PNG 图片的字形信息的 bitmap 里，bitmap 中的 rows 对应图片的高度，width
对应图片的宽度，pitch 对应 bitmap 每行占据的字节数，即 宽度 4。之后会调用 ft_glyphslot_alloc_bitmap 函数完成
bitmap 中用于存储图片信息的内存的分配。如下图，分配的内存大小是 map->rows (FT_ULong)map->pitch，即高度 *
每行占据的字节数。之后调用 png_read_image 读取图片信息到 bitmap->buffer。如果 PNG
图片的高度被截断，则会导致分配的内存不足，在读取图片信息时发生堆溢出。

![](https://p2.ssl.qhimg.com/t01784a6c47f5cac6bc.png)

溢出后 bitmap 信息如下图，buffer 的长度即为 0xa3 * 0xc ，查看 buffer 之后的数据可以看到已经被覆盖。

![](https://p4.ssl.qhimg.com/t01e90a6d2172f33e70.png)

## 漏洞验证

###  一、在87.0.4247.0（开发者内部版本）验证

![](https://p0.ssl.qhimg.com/t010d81b7b98be78a6f.png)

###  二、86.0.4240.111 版本修复分析

比较 imgWidth 和 imgHeight 是否大于 0x7FFF, 大于则退出。

![](https://p2.ssl.qhimg.com/t013a9fc52276f17f2a.png)

## 参考

<https://bugs.chromium.org/p/chromium/issues/detail?id=1139963>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信代码卫士** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/221878](/post/id/221878)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Chrome](/tag/Chrome)

 **+1** __6赞

 __收藏

![](https://p4.ssl.qhimg.com/t015a32ce3696fa7636.png) 奇安信代码卫士

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

