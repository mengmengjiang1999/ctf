## 漏洞简介

Google发布公告，旧版本的 chrome 浏览器的 FreeType字体库中存在堆溢出，被利用可能导致 RCE（远程代码执行）。

安全专家建议用户尽快升级到86.0.4240.111 之后的版本，以解决风险。

## 漏洞原理

  

 **一、TTF 嵌入图片**

TTF 字体支持嵌入 PNG 格式的图片作为字形数据，在嵌入时图片数据会被保存在字体文件的 SBIX 表格中，在处理时会通过提取 SBIX 表中的 PNG
中存取的信息来实现字体渲染。SBIX 表中的格式如下图：

![1604646034_5fa4f492b0c85e9b0c6c8.png!small](https://image.3001.net/images/20201106/1604646034_5fa4f492b0c85e9b0c6c8.png!small)

  

SBIX 中的 strikeOffset 存储了 Strikes 的数据信息的偏移，Strikes 中的 glyphDataOffset
存储了具体的字形信息的偏移，Strikes 格式和字形信息的格式如下图：

![1604646054_5fa4f4a6e70178c682f49.png!small](https://image.3001.net/images/20201106/1604646054_5fa4f4a6e70178c682f49.png!small)

![1604646061_5fa4f4adac7c510baaad4.png!small](https://image.3001.net/images/20201106/1604646061_5fa4f4adac7c510baaad4.png!small)

  

字形信息中的 data 存储了被嵌入的图片信息。下面是样本中的 SBIX 和存储的图片信息。

![1604646107_5fa4f4db88ea03c7b7d49.png!small?1604646107975](https://image.3001.net/images/20201106/1604646107_5fa4f4db88ea03c7b7d49.png!small?1604646107975)

PNG 图片信息被保存在了 hex(0x1a30 + 0x5aaec + 0x8) = 0x5c524 处。通过 IHDR
可以看到图片的一些基本信息，具体信息如下图：

![1604646115_5fa4f4e3c8de0fe4b9450.png!small?1604646116270](https://image.3001.net/images/20201106/1604646115_5fa4f4e3c8de0fe4b9450.png!small?1604646116270)

  

 **二、Load_SBit_Png 函数实现**

FreeType 库中 PNG 图片信息的提取是通过 Load_SBit_Png 函数实现的。Load_SBit_Png 函数的处理流程如下：

1\. 将字形信息中 data 指向的内存解析为 PNG

2\. 提取被解析后图片的 IHDR 存储的信息（图像宽度和高度，深度及颜色类型等）

3\. 将解析后的信息提取到字形信息中

4\. 按照之前解析到信息开辟内存用于保存图片信息

  

 **三、漏洞原理**

漏洞发生在将解析到的图片信息提取到字形信息过程中，PNG 图片中的 IHDR 存储的宽度和高度的数据类型为 uint32，在存储到字形信息时，会被转换为
unsigned short 类型，此时如果图片的宽度和高度信息大于 0x7FFF 则会发生截断。

![1604646123_5fa4f4eb9fc6039eeebaa.png!small?1604646123943](https://image.3001.net/images/20201106/1604646123_5fa4f4eb9fc6039eeebaa.png!small?1604646123943)

  

之后字形信息中存储的相应数据会被传递到用于存储 PNG 图片的字形信息的 bitmap 里，bitmap 中的 rows 对应图片的高度，width
对应图片的宽度，pitch 对应 bitmap 每行占据的字节数，即 宽度 * 4。之后会调用 ft_glyphslot_alloc_bitmap 函数完成
bitmap 中用于存储图片信息的内存的分配。如下图，分配的内存大小是 map->rows * (FT_ULong)map->pitch，即高度 *
每行占据的字节数。之后调用 png_read_image 读取图片信息到 bitmap->buffer。如果 PNG
图片的高度被截断，则会导致分配的内存不足，在读取图片信息时发生堆溢出。

![1604646129_5fa4f4f1b617f2b69e920.png!small?1604646130023](https://image.3001.net/images/20201106/1604646129_5fa4f4f1b617f2b69e920.png!small?1604646130023)

  

溢出后 bitmap 信息如下图，buffer 的长度即为 0xa3 * 0xc ，查看 buffer 之后的数据可以看到已经被覆盖。

    
    
      
    

![1604646136_5fa4f4f8db815ae6b0f0b.png!small?1604646137159](https://image.3001.net/images/20201106/1604646136_5fa4f4f8db815ae6b0f0b.png!small?1604646137159)

  

## 漏洞验证

  

 **一、在87.0.4247.0（开发者内部版本）验证**

![1604646153_5fa4f50988325776c95e1.png!small?1604646153823](https://image.3001.net/images/20201106/1604646153_5fa4f50988325776c95e1.png!small?1604646153823)

  

 **二、86.0.4240.111 版本修复分析**

比较 imgWidth 和 imgHeight 是否大于 0x7FFF, 大于则退出。

![1604646161_5fa4f511ba47360b0a23e.png!small?1604646162070](https://image.3001.net/images/20201106/1604646161_5fa4f511ba47360b0a23e.png!small?1604646162070)

  

## 参考

  

https://bugs.chromium.org/p/chromium/issues/detail?id=1139963

  

  

