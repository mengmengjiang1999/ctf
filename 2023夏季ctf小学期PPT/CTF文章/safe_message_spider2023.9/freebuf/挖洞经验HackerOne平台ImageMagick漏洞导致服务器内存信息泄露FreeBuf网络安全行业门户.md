***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **![PC-HackerOne.jpg](https://image.3001.net/images/20181119/1542612092_5bf2647c7240c.jpg!small)**
**大家好，今天我要分享的是关于HackerOne平台GIF图像处理的ImageMagick漏洞（CVE-2017–15277），漏洞很简单，最终也获得了HackerOne官方奖励的$500美金。**  

##  CVE-2017–15277介绍

[CVE-2017–15277](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-15277)最早于2017年10月被安全研究人员Emil
Lerner发现，它属于开源图像处理组件ImageMagick漏洞，受影响软件为ImageMagick 7.0.6–1和Graphicsmagick
1.3.26。原因在于，当ImageMagick在处理不具备全局或本地调色板的GIF图片时，ImageMagick
7.0.6–1和Graphicsmagick
1.3.26中存在未初始化的调色板，其coders/gif.c文件中ReadGIFImage存在安全漏洞，如果攻击者利用ReadGIFImage来处理GIF图片，构造操作，可以通过未初始化的调色板来间接获取到服务器中的内存数据信息。

简单地说就是，如果服务器中部署了ImageMagick 7.0.6–1和Graphicsmagick
1.3.26，且其中具备未初始化的调色板机制，那么，利用CVE-2017–15277，通过构造图片文件，上传至服务器中的任何可上传地方，之后，服务器通过处理这种构造图片，就会利用未初始化的调色板机制，把其转化成不同像素的图片预览文件，而在这些图片预览文件中，可能包含了一些和服务器内存相关的信息，如Stack
trace（堆栈跟踪）和String value（字符串值）信息等。

此外，从实际功能来说，ImageMagick是一个显示、转换和编辑光栅图像和矢量图像文件的开源软件，它被用于许多web应用中的裁剪、调整大小和改变颜色功能，且支持多种图像格式。

## 漏洞利用

让我们直接来到漏洞利用部分吧，这里，我们以HackerOne网站为漏洞测试目标。

首先，我下载了Emil Lerner在Github上公布的漏洞利用包<https://github.com/neex/gifoeb>；

之后，利用下述命令来创建512x512像素的GIF漏洞利用（exploitable）图片：

> ./gifoeb gen 512x512 dump.gif

当然了，你也可以把生成的图片文件改成其它后缀格式，如.jpg 、.tiff 、.bmp等，也可以创建生成其它不同像素的漏洞利用图片：

![01.png](https://image.3001.net/images/20181119/1542611739_5bf2631bacd01.png!small)![02.png](https://image.3001.net/images/20181119/1542611746_5bf26322257a6.png!small)接着，登录我的HackerOne账户，尝试在用户资料的头像处上传上述命令生成的漏洞利用GIF图片：

![03.png](https://image.3001.net/images/20181119/1542611757_5bf2632dcb42b.png!small)之后，服务器后端处理这种漏洞利用GIF图片后，就会生成相应的512x512像素的预览图片；

然后，在GIF格式下，我尝试生成了不同像素的漏洞利用图片，并把它们一一上传，以获取服务器后端生成的不同像素的预览图片：

![04.png](https://image.3001.net/images/20181119/1542611804_5bf2635c4982a.png!small)把这些不同像素的预览图片保存在一个文件夹中：

![05.png](https://image.3001.net/images/20181119/1542611820_5bf2636c2a27f.png!small)最后，用以下命令恢复出这些预览图片中包含的服务器内存信息：

> for p in previews/*; do ./gifoeb recover $p | strings; done

![06.jpeg](https://image.3001.net/images/20181119/1542611853_5bf2638d48d3e.jpeg!small)![07.jpeg](https://image.3001.net/images/20181119/1542611863_5bf2639735213.jpeg!small)可以看到，这些不同像素的预览图片中泄露了服务器内存中的运行信息，这些信息包含了服务器路径（path）、操作系统（OS）、软件版本等。

## 漏洞影响

该ImageMagick漏洞（CVE-2017–15277），可能会导致一些邮件、Cookie、SQL查询语句以及文件目录等服务器相关信息泄露。在上述的漏洞测试中，我们仅发现
了HackerOne的操作系统、文件目录和一些堆栈跟踪泄露信息。漏洞修复当然是升级ImageMagick组件至最新版本了。

## 漏洞利用建议

>
> 1、在最新的ImageMagick组件中，该漏洞利用被缓解修复了，如果向服务器上传漏洞利用图片后，你只会获得一张黑色的预览图片，这种图片不会泄露任何服务器内存信息；
>
> 2、即使你在一些漏洞利用场景中，可以获得服务器生成的预览图片，也要看看它是否存在涉及文件目录、操作系统版本等服务器相关的信息泄露，如果仅只是像
> {{{*a/!a^a;bb(b|} 的一些堆栈跟踪信息，那还需要继续测试，别忙着上报漏洞；
>
>
> 3、构造不同分辨率和扩展名的漏洞利用图片，尤其是那些具有灰色像素的图片，它们包含的信息比蓝色、绿色或红色图片多得多。最终的可利用性和效果还得依不同网站和ImageMagick组件版本而言。

## 漏洞上报进程  

经向HackerOne上报漏洞后，他们认为这属于内存泄露漏洞，并向我奖励了$500 美金，作为我的第一上漏洞，这对我有很大鼓励。当然，也要感谢 Emily
Lerner 公布的漏洞利用方法。

> 2018.1.6 向HackerOne上报漏洞
>
> 2018.1.7 HackerOne评估并分类漏洞
>
> 2018.1.7 CVE官方向Emil Lerner分配了漏洞编号 CVE-2017–15277
>
> 2018.1.20 HackerOne向我奖励了$500
>
> 2018.2.7 漏洞被成功处理修复

 ***参考来源：[medium](https://medium.com/@kunal94/imagemagick-gif-coder-vulnerability-leads-to-memory-disclosure-hackerone-e9975a6a560e)，clouds编译，转载请注明来自FreeBuf.COM**

