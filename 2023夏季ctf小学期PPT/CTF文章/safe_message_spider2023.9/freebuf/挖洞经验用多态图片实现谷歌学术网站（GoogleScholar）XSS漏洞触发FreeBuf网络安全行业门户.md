![](https://image.3001.net/images/20200509/1589014520_5eb66ff8882a9.png!small)

**本文讲述了作者利用多态图片触发谷歌学术网站（ Google
Scholar）XSS漏洞的测试，漏洞最终获得了谷歌$9400的奖励。此前作者也曾分享过名为[《Funky_File_Formats》](https://fahrplan.events.ccc.de/congress/2014/Fahrplan/system/attachments/2562/original/Funky_File_Formats.pdf)的演讲，其中分析了可以用多态图片构造基于JavaScript的XSS，可对客户端浏览器安全形成威胁。**

> 多态图片（Polymorphic Image）：指包含或被嵌入了代码的图片，嵌入代码可以在图片文件头部、尾部、元数据或ECS等区域。

##  漏洞发现

几个月前，我在上谷歌学术网站（ Google Scholar）时发现了其一个奇怪的设计模式，
它在Web应用界面的获取呈现过程中，使用了location.hash参数和XHR请求方式，尤其是在一些模板片段显示时，会提取相关URI并以未转义方式加载到网页中，如下：

![](https://image.3001.net/images/20200509/1589013959_5eb66dc7e8cdf.png!small)本身来说这应该是安全的，除非允许用户上传任意内容并能以同源方式渲染加载，但不巧的是，谷歌学术网站在其图片上传机制中确实如此，存在问题。

基于上述描述，有经验的渗透测试人员可能会觉得这种利用非常简单，然而谷歌学术平台后端在对上传图片的处理中采用了多种转化方式，如元数据剥离后重新处理图片等。在最开始我上报该漏洞时，谷歌安全团队也仅只是要求我提供PoC验证，并未考虑多态图片包含XSS
Payload的可能。

在图片中嵌入代码的技术也可谓是一项老把戏了，我研究了过去的一些“众所周知”的技术以生成了各种多态图片，之后针对当前一些流行的图片处理库（如Imagemagick,
GraphicsMagick, Libvips），开发了一个测试套件工具[Standardized Image Processing Test
Suite](https://github.com/doyensec/StandardizedImageProcessingTest)，以测试其图片处理过程中的安全性。利用工具Standardized
Image Processing Test
Suite可以在一些图片处理过程中发现很多有意思的bug问题，如隐藏webshell或javascript实现内容安全策略(CSP)的绕过。这里，就我测试的几种图片代码嵌入技术做一些讨论总结，然后应用“Payload嵌入到JPG的ECS区域”方法实现谷歌学术网站的XSS漏洞触发。

##  隐藏在EXIF中的Payload

这里，最简单的方法就是在图片元数据（metadata）中嵌入Payload了。在JPEG/JFIF类型图片中，元数据（metadata）都存储在一些特定应用标记（APPX）中，然而大多数图片处理库都未把这些标记的安全性考虑在内。Exiftool就是编辑此类图片属性的一个流行工具，但是它针对某些字符却做了转义，所以，我只好手动进行了插入。但愿谷歌学术能有相对宽松的白名单EXIFs，所以我在测试图片中嵌入了1.2k的通用EXIF标记，包括了标准的CIPA标记和一些非标准的标记。

如下JPG测试图片，我在其中的每个通用元数据区域都嵌入了alert()的XSS Payload：

![](https://image.3001.net/images/20200509/1589014096_5eb66e50a45cf.jpg!small)![](https://image.3001.net/images/20200509/1589014109_5eb66e5d7d202.png!small)如下PNG测试图片，同样在每个通用元数据区域都嵌入了alert()的XSS
Payload：

![](https://image.3001.net/images/20200509/1589014123_5eb66e6b9380e.png!small)以上两张测试图片中，在所有元数据区域都嵌入了alert()代码，尽管有些EXIF字段是很多流行Web平台都在用的属性，但经测试发现，它们在上述谷歌学术网站服务端上却无法有效触发XSS。一些Web平台的图片处理库在进行图片转化时会有异常发生，如PNG转PNG时，原始的PNG元数据可以保留，但从PNG转JPG时，原始的元数据就会发生丢失。

##  Payload嵌入到图片末尾方式（JPG中嵌入到0xFFD9后，PNG嵌入到IEND后）

由于图片在上传到Web应用平台后会被执行转化，所以这里这种把代码嵌入到图片末尾的Payload仅对一些上传图片不做转化的场景适用。

以下为alert()代码嵌入到0xFFD9后的JPG图片:

![](https://image.3001.net/images/20200509/1589014171_5eb66e9b12d90.jpg!small)![](https://image.3001.net/images/20200509/1589014182_5eb66ea6487a1.png!small)以下为alert()代码嵌入到IEND后的PNG图片:

![](https://image.3001.net/images/20200509/1589014201_5eb66eb9c2563.png!small)![](https://image.3001.net/images/20200509/1589014213_5eb66ec582d5e.png!small)

##  Payload嵌入到PNG的iDAT区域

在PNG图片中，iDAT块常用来存储一些pixel像素信息，根据Web平台采用的转化机制，我们可以直接在iDAT块中插入XSS
Payload，或是想办法绕过一些调整大小或重新采样操作。这里，谷歌学术仅只是生成了JPG图片而非PNG图片，所以这种技术在此也不适用。

##  Payload嵌入到JPG的ECS区域

在标准的JPEG文件交换格式（JFIF）中，熵编码数据段（entropy-coded data
segment，ECS）包含了原始霍夫曼压缩位流的输出，该输出代表了包含图像数据的最小编码单位（MCU）。理论上说，可以将Payload嵌入到该区域中，但也不能保证Web后端在实施图片转化时会破坏Payload。所以，这就需要反复测试，创建一个在ECS区域嵌入Payload且不被图片转化机制破坏的JPG。

首先，我创建了与转化后图片质量相同的一个原始测试JPG图片，然后，基于[这张0长度字符可更改EXIF信息的图片](https://github.com/ianare/exif-samples/blob/master/jpg/tests/67-0_length_string.jpg)进行代码嵌入测试。经过反复实验，我发现把Payload放到距ESC不同偏移量的位置均不奏效，但是我发现一种方法：谷歌学术在处理图片时，如果用夹杂0x00
和 0x14字节把ESC分隔后，则ESC中的前几个字节信息将会得以保留，如下：

![](https://image.3001.net/images/20200509/1589014279_5eb66f07855d5.png!small)基于上述测试，我终于找到了正确的Payload安置点，可以保证其中的Payload在上传到谷歌学术后，不会被图片转化机制破坏。最终，也成功地在加载图片请求时触发了XSS弹窗alert(1)：

![](https://image.3001.net/images/20200509/1589014304_5eb66f20f1549.png!small)

另外，我们也提供了更多的XSS代码嵌入图片，如以下的[onclick()](https://blog.doyensec.com/public/images/onclick-xss-ecs.jpeg)：

![](https://image.3001.net/images/20200509/1589014348_5eb66f4c7a119.jpeg!small)![](https://image.3001.net/images/20200509/1589014358_5eb66f56800a8.png!small)

以下的[mouseover()](https://blog.doyensec.com/public/images/mouseover-xss-ecs.jpeg)：

![](https://image.3001.net/images/20200509/1589014382_5eb66f6e9e247.jpeg!small)![](https://image.3001.net/images/20200509/1589014392_5eb66f78f1c4d.png!small)

当然了，你也可以访问我们放在Github上的开源测试工具[StandardizedImageProcessingTest](https://github.com/doyensec/StandardizedImageProcessingTest)，用它来进行把玩研究。

##  谷歌学术XSS漏洞上报进程

> [2019-09-28] 上报给Google安全团队
>
> [2019-09-30] Google安全团队希望得到漏洞验证PoC
>
> [2019-10-04] 我提供了PoC #1
>
> [2019-10-10] Google安全团队再次要求我提供其它的漏洞验证PoC
>
> [2019-10-11] 我又提供了PoC #2
>
> [2019-11-05] Google安全团队在谷歌的两个服务端中复现了漏洞，奖励了我$6267.40
>
> [2019-11-19] Google安全团队用同样的技术发现另外一个服务端中同样存在该类型XSS漏洞，再次奖励了我$3133.70

***参考来源：[doyensec](https://blog.doyensec.com/2020/04/30/polymorphic-images-for-xss.html)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

  

