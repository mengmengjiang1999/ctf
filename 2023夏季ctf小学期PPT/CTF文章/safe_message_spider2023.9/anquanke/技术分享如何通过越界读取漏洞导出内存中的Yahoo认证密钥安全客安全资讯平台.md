# 【技术分享】如何通过越界读取漏洞导出内存中的Yahoo!认证密钥

阅读量 **121106**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-05-23 16:34:31

 **x**

##### 译文声明

本文是翻译文章，文章来源：scarybeastsecurity.blogspot.hk

原文地址：<https://scarybeastsecurity.blogspot.hk/2017/05/bleed-more-powerful-dumping-yahoo.html>

译文仅供参考，具体内容表达以及含义原文为准。

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**一、前言**

在我之前发布的关于Yahoobleed
#1（YB1）的一篇[文章](https://scarybeastsecurity.blogspot.com/2017/05/bleed-continues-18-byte-file-14k-bounty.html)中，我们了解到如何利用未初始化漏洞获取其他用户的私密图像信息。当时泄露的内存数据受制于JPEG图像的压缩机制，这种限制对某个图像大盗来说不成问题，然而如果我们想要窃取其他类型的内存内容，已泄露的这些数据仍稍显不足。

在这篇文章中，我会向大家介绍Yahoo!缩略图服务器上存在的另一个滴血（bleed）类的漏洞，我们可以将这个称之为Yahoobleed
#2（YB2）。我们可以利用这个JPEG压缩缺陷（现在这个缺陷依然存在）提取原始的内存字节。结合“strings”工具的使用，我们还可以发现更多惊喜。

Yahoo!通过弃用ImageMagic的方式，在修复YB1漏洞的同时也修复了YB2漏洞。大家可以参考我之前的一篇[文章](https://scarybeastsecurity.blogspot.com/2017/05/bleed-continues-18-byte-file-14k-bounty.html)，通过Yahoo!的回复进一步了解漏洞的修复细节。

  

**二、可视化**

当我们触发该漏洞时，Yahoo!服务器返回JPEG图片上会出现某些噪点。如上图所示，漏洞触发后，Yahoo!服务器返回了某张JPEG图片，将图片的某个64×4区域转化为PNG格式（即无损格式），放大后可以看到某些噪点，如上图所示。

这张图片有许多有趣的地方值得注意，就现在而言，我们可以观察到的是，图片的顶部存在几个指针图像。我曾在Project
Zero上发表过有关指针可视化的一篇[文章](https://googleprojectzero.blogspot.com/2014/08/what-does-pointer-look-like-anyway.html)，如果你对这篇文章有所了解，你可以在各种内存泄露场景中发现这类指针的存在。至少对于x86_64架构的Linux来说，该系统中的指针通常都包含一个0x00007f的前缀。这类指针的包含几个特点，如：

1、使用相同的对齐方式重复类似的结构（64位系统上使用8字节对齐）；

2、在指针块中，白色垂直条纹指向的是被对齐的最重要的字节，表示的是0x00（需要注意的是，由于输入文件的特殊格式，所泄露的字节实际上经过了取反处理）；

3、在指针块中，紧挨其后的黑色垂直条纹所代表的含义是某行的7个比特的值被设置为0x7f。

4、在指针块中，紧挨其后的白色垂直细长条纹所代表的含义是该行的1个比特的值没有被设置为0x7f。

但我们还是会遇到JPEG压缩算法，这会不会对逐字节数据提取造成困难？我们会慢慢揭开这个谜题。

**  
**

**三、漏洞分析**

我们不知道Yahoo!所使用的ImageMagic是否是最新版本，因此我们开始寻找相关的漏洞是否存在。我们已经知道Yahoo!支持RLE格式，之前我在一篇[文章](https://scarybeastsecurity.blogspot.com/2017/03/black-box-discovery-of-memory.html)中介绍了如何使用某个技巧挖掘Box.com的内存损坏漏洞，也许我们可以使用相同的技巧对Yahoo!进行测试。

非常有趣的是，漏洞利用文件并不会导致任何文件崩溃，但服务器依然渲染了所有的测试文件，而最新版本的ImageMagic完全不会渲染这些文件。经过一番思考，我认为最有可能的解释就是，Yahoo!所用的ImageMagic的确是存在漏洞的老版本，但根据我们对YB1漏洞的分析，Yahoo!使用了不一样的堆设置，受对齐方式影响，我们的堆越界访问测试用例无法在Yahoo!上生效。

为了验证这个假设，我们构造了一个堆越界写RLE文件，足以覆盖堆中的某一小块数据（64字节大小，大约会有16个字节被覆盖），并将该文件上传到Yahoo!上。访问缩略图URL后，服务器会较为稳定地（以大约50%左右的概率）返回如下结果：

这个结果看上去像是一个非常明显的后端错误，我们猜测它最有可能是一个SIGSEGV错误，这个错误与已有两年历史的[RLE内存损坏问题](http://git.imagemagick.org/repos/ImageMagick/commit/7131d8ff451a1d5163e7e35b7a910df80cb54fab)有关。

但是我们今天的目标并不是如何利用这个RCE内存损坏错误，虽然这个过程肯定非常有趣。我们的目标是通过滴血攻击来提取数据。现在，我们手上拥有的是一个已有2.5岁年龄的ImageMagick，对于这个版本的ImageMagick而言，肯定有许多漏洞已经被修复了。经过一番搜索，我们找到了一个候选漏洞：一个已有2年以上历史的、已经在SUN解码器中修复的[越界漏洞](http://git.imagemagick.org/repos/ImageMagick/commit/b8f17d08b7418204bf8a05a5c24e87b2fc395b75)。在这个漏洞的修复代码中，开发者似乎对长度做了相关检查，同时更加彻底地应用长度检查过程，使其能够将色深（bit
depth）为1的图像包含在内。让我们稍微研究一下没有打上补丁的代码，并且深入跟踪程序对色深为1的图片的解码路径，我们可以发现如下代码（位于[coders/sun.c](http://git.imagemagick.org/repos/ImageMagick/blob/acabb847a592ca5e430c1c0949d03acfc0b78bb9/coders/sun.c)中）：

    
    
    sun_info.width=ReadBlobMSBLong(image);
    sun_info.height=ReadBlobMSBLong(image);
    sun_info.depth=ReadBlobMSBLong(image);
    sun_info.length=ReadBlobMSBLong(image);
    [...]
    number_pixels=(MagickSizeType) image->columns*image->rows;
    if ((sun_info.type != RT_ENCODED) && (sun_info.depth >= 8) &&
    ((number_pixels*((sun_info.depth+7)/8)) > sun_info.length))
    ThrowReaderException(CorruptImageError,"ImproperImageHeader");
    bytes_per_line=sun_info.width*sun_info.depth;
    sun_data=(unsigned char *) AcquireQuantumMemory((size_t) sun_info.length,
    sizeof(*sun_data));
    [...]
        count=(ssize_t) ReadBlob(image,sun_info.length,sun_data);
        if (count != (ssize_t) sun_info.length)
          ThrowReaderException(CorruptImageError,"UnableToReadImageData");
     
        sun_pixels=sun_data;
        bytes_per_line=0;
    [...]
        p=sun_pixels;
        if (sun_info.depth == 1)
          for (y=0; y < (ssize_t) image->rows; y++)
          {
            q=QueueAuthenticPixels(image,0,y,image->columns,1,exception);
            if (q == (Quantum *) NULL)
              break;
            for (x=0; x < ((ssize_t) image->columns-7); x+=8)
            {
              for (bit=7; bit >= 0; bit--)
              {
                SetPixelIndex(image,(Quantum) ((*p) & (0x01 << bit) ? 0x00 : 0x01),
                  q);
                q+=GetPixelChannels(image);
              }
              p++;
            }

因此，我们发现代码在处理色深为1的图像时存在一个非常明显的问题：

1、假设该图片的属性为：width（宽度）=256, height（高度）=256, depth（色深）=1, length（长度）=8；

2、色深为1的图像会导致与sun_info.length对比的number_pixels的检查过程被绕过；

3、sun_data所分配的缓冲区大小为8字节，而程序从输入文件中读取了这8个字节；

4、然后程序按每个像素1个比特的方式对图片进行解码。在这个过程中，sun_data总共需要(256*256)/8 == 8192个字节，但只有8个字节可用；

5、然后就出现大量的越界读取问题；程序实际上是在一片越界内存中对图片进行渲染。

**  
**

**四、漏洞利用**

漏洞利用文件只有40个字节，因此我们可以在十六进制编辑器中观察这个图片的每个字节的含义：

59 A6 6A 95: 头部

00 00 01 00 00 00 01 00: 图片大小256 x 256

00 00 00 01: 图片色深：每像素1比特

00 00 00 08: 图片数据长度为8

00 00 00 01: 图片类型为1：标准图片

00 00 00 00 00 00 00 00: map类型为空，长度为0

41 41 41 41 41 41 41 41: 8字节的图片数据

对于这个漏洞利用文件，我们可以操纵的最为有趣的一个变量就是图片数据长度（image data length）变量。只要我们将其大小控制在(256 *
256) /
8以内，我们就能复现越界读取漏洞。但越界读取从哪个位置开始呢？它会在图片数据分配缓冲区的末尾开始。通过改变图片数据的大小，我们最终有可能操纵堆中不同的相对地址（也许这些地址与缓冲区的开始或结束位置在距离上关系更为密切）。这样一来我们有可能能够读取某些有趣的数据。

**  
**

**五、信息提取**

显然我们可以利用这个漏洞来提取信息，这也是这个漏洞真正有价值的地方所在。正如可视化部分所描述的内容，我们可以通过一个JPEG压缩文件来尝试提取信息。事实上我们可以通过ImageMagick获得一张JPEG灰度图像，因为前面每像素1比特的漏洞利用文件会生成一个黑白相间的图形。我们可以利用JPEG灰度图片较好地实现信息提取。人们之所以设计JPEG压缩算法，主要是想欺骗人眼对图片的直观感知。相对比真实的颜色而言，人类视觉对颜色的亮度更为敏感，因此在压缩算法中，颜色数据通常会比亮度数据丢失的信息更多（我们主要是通过[YCbCr颜色空间](https://en.wikipedia.org/wiki/YCbCr)实现这一点）。而JPEG灰度图像中只有亮度数据存在。

回头看看用于信息提取的那张JPEG图像，我们仍然会遇到JPEG压缩算法。我们会被这个困难所阻拦吗？答案是否定的。因为我们的漏洞利用图片是一张每像素1比特（黑色或白色）的图片，因此我们只需要在信息提取的JPEG文件中精确控制每个像素的1比特信息熵即可。虽然某些白色像素实际上是有点浅灰色而不是全白色，且某些黑色像素实际上是有点深灰色而不是全黑色，但每个像素仍然非常接近于黑色或者白色。我当然没有经过严密的数学计算，但事实上，对于Yahoo!服务器所使用的JPEG压缩算法而言，每个像素的确包含1比特的信息熵。根据我的统计，与白色偏差最大的那个像素颜色大约为85%的白色（即非常浅的灰色），而信息丢失的阈值当然更低，可以达到50%或者以下。

我们可以尝试从JPEG文件中恢复原始的字节，只需要使用如下的ImageMagick转换命令即可：

convert yahoo_file.jpg -threshold 50% -depth 1 -negate out.gray

对于本文开头的那个JPEG文件而言，恢复出来的原始内存字节如下所示：

    
    
    0000000 d0 f0 75 9b 83 7f 00 00 50 33 76 9b 83 7f 00 00
    0000020 31 00 00 00 00 00 00 00 2c 00 00 00 00 00 00 00

从中我们可以看到两个指针：0x00007f839b75f0d0以及0x00007f839b763350。

**  
**

**六、字符串及密钥**

因此，现在我们有了一个在字节数据上相当可靠的信息提取方法，我们可以从Yahoo!缩略图服务器上发现哪些有趣的字符串吗？我们找到了许多信息量很大的字符串，我们用“redacted”替换了其中敏感的信息：

**SSLCOOKIE** : SSL=v=1&s=redacted&kv=0

**Yahoo-App-Auth** :
v=1;a=yahoo.mobstor.client.mailtsusm2.prod;h=10.210.245.245;t=redacted;k=4;s=redacted

**https://dl-mail.ymail.com/ws/download/mailboxes
/**@.id==redacted/messages/@.id==redacted/content/parts/@.id==2/raw?appid=getattachment&token=redacted&ymreqid=redacted

是的，结果看起来非常严重。

除了会话密钥等有趣的字符串之外，我们还能看到其他信息吗？是的，我们可以通过某些路径、错误信息以及版本字符串发现服务器的确在使用ImageMagick，而且版本非常老：

    
    
    /usr/lib64/ImageMagick-6.8.9/modules-Q16/coders/sun.so
    ImageMagick 6.8.9-6 Q16 x86_64 2014-07-25 http://www.imagemagick.org
    unrecognized PerlMagick method

显然，这些字符串可以作为这个漏洞的佐证，同时我们还可以注意到字符串中涉及到PerlMagick。我对PerlMagick并不熟悉，可能PerlMagick是用来实现进程中的ImageMagick，这也是为什么我们的越界图像数据能够读取这么多有趣信息的原因所在。

**  
**

**七、总结**

这个漏洞非常有趣，我们发现服务器上存在内存泄露漏洞，可以将每个经过JPEG压缩的像素的少量数据编码后返回给我们，因此我们能够较为稳定地重新构造原始的字节，还原服务器所泄露的内存数据。

在已启用的解码器中，不加限制地使用老版本的ImageMagick是一件非常危险的事情，通过弃用ImageMagick，Yahoo!应该已经修复了这些问题。

本文翻译自scarybeastsecurity.blogspot.hk
[原文链接](https://scarybeastsecurity.blogspot.hk/2017/05/bleed-more-powerful-dumping-yahoo.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86146](/post/id/86146)

安全客 - 有思想的安全新媒体

本文转载自:
[scarybeastsecurity.blogspot.hk](https://scarybeastsecurity.blogspot.hk/2017/05/bleed-more-powerful-dumping-yahoo.html)

如若转载,请注明出处： <https://scarybeastsecurity.blogspot.hk/2017/05/bleed-more-powerful-dumping-yahoo.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

