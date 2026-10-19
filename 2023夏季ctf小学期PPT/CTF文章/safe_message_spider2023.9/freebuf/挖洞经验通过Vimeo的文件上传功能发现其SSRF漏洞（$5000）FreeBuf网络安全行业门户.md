![](https://image.3001.net/images/20191220/1576839600_5dfca9b00fa75.jpg!small)

**本文分享的是视频分享网站Vimeo的一个SSRF漏洞，作者通过Vimeo上传功能中Vimeo分次读取部份文件流的机制发现了该漏洞，漏洞最终获得了Vimeo官方$5,000美金奖励。以下是作者的分享。**

## 漏洞发现过程

之前我一直在学校学习我比较讨厌的科目知识，所以最近我决定放松休息一下，我告诉自己必须要在HackerOne平台中的Vimeo漏洞众测中有所发现。于是，我就直接想测试一下Vimeo平台的上传功能，尤其是通过Google云端硬盘
(Google
Drive)上传到Vimeo的一些功能特性，所以，在我的Google云端硬盘中我选择了一个特定视频文件，把它执行到Vimeo的上传操作，然后用BurpSuite查看它的具体上传请求信息。

![](https://image.3001.net/images/20191220/1576839291_5dfca87bd7950.png!small)

从上图可见，上传视频文件的具体URL链接中包含了Google云盘中的相关身份验证信息，以便让Vimeo后端服务器能有权限从Google云盘中获取到相应文件，具体的验证信息存在于请求头的header参数中。

所以，看到这里我就想在自己的VPS中架设一个环境，发起上传视频文件到Vimeo平台的操作，看看上传请求发起后，在Vimeo后端服务器和我的VPS服务器之间会发生什么情况。经测试，从我VPS端上传到Vimeo后，我VPS中的具体网络情况如下，Vimeo后端响应回来的消息有些奇怪，尤其是其黄色部分。

![](https://image.3001.net/images/20191220/1576839320_5dfca898b1656.png!small)

其黄色部分的Range,和Content-Range等引起了我的注意，但从其名字中我也大概能猜测到其大致用途。可以这样假设，大多数时候，因为用户上传的视频文件都是比较大的，所以Vimeo不会用一个上传请求来实现对整个文件的上传。但如果用户需要上传的视频文件较小，那么Vimeo就会实现一次请求上传了。所以这样来看，Vimeo对用户需要上传的大视频文件都是采取每次请求部份文件，然后多次请求，再实现最终整个文件的组装完成。整个上传流程大概的逻辑如下：

![](https://image.3001.net/images/20191220/1576839349_5dfca8b5284bc.png!small)

也就是说，Vimeo服务器请求用户需要上传的视频文件时，它会判断如果文件足够小，那么建立一次连接就可以上传完成，就不需要后续再建立连接了。基于此，我突然想到，如果我不向Vimeo服务端发送整个上传文件会如何呢？比如，按以上原理，如果我的VPS告诉Vimeo后端服务器，我需要上传的文件有500B，那么Vimeo后端服务器就会来取走这500B，但是，如果现在我的VPS告诉Vimeo后端服务器我的文件只有200B，那么之后会发生什么呢？说白了，也就是看看Vimeo后端对大文件上传的具体操作行为，来试试看。

![](https://image.3001.net/images/20191220/1576839377_5dfca8d10f276.png!small)

在此，我用Python编写了一个脚本来监测Vimeo的这种取大文件的操作，我需要上传的视频文件长度共554231B。测试发现，当Vimeo后端服务器来取我的这个554231B大文件时，监测脚本显示，第一次Vimeo后端只会读取8228B长度的部份文件内容！

![](https://image.3001.net/images/20191220/1576839426_5dfca9026d2a6.png!small)

Cool，Vimeo后端在取完8228B长度的部份文件后，会再接着往下取文件的其余部份，由此，一个SSRF场景在我脑海中油然而生。如果我的VPS告诉Vimeo后端服务器一个重定向响应，那Vimeo后端服务器会跟着跳转吗？还是会存储这个重定向响应？还是继续接着往下读取文件其余部份？我的构思场景逻辑如下，Vimeo后端在取完第一次的8228B长度的部份文件内容后，会继续发起对后续文件的读取，这个时候，我在后续文件内容中插入一个恶意文件内容-<http://evil.com/Hello.txt>，其文件内容为HelloWorld!zzz，共15个字节。那么Vimeo后端在读取余下的546094字节文件时，会一并请求我们恶意插入的链接<http://evil.com/Hello.txt>，把HelloWorld!zzz也顺利读取到。

由于一些Web托管服务端对上述攻击场景作了安全限制，所以我自己动手搭建了一个主机网站进行测试实现，很幸运，我的猜想是对的！按照以上思路在对Vimeo后端的视频文件上传中，可以成功实现上述预计的攻击测试场景。

Notice: 在Vimeo服务中，我们可以下载原始的上传文件，所以根据这种下载路径，我们也能轻松构造对响应的一些假冒伪造操作。

![](https://image.3001.net/images/20191220/1576839471_5dfca92f62f5d.png!small)

## 漏洞利用

经过测试，我发现Vimeo后端服务相关操作是建立在Google云上的，它后端部署了一个谷歌云实例，而且请求这个实例<http://metadata.google.internal/computeMetadata/v1beta1/instance/service-accounts/default/token>，可以发现其默认的API访问token！那么有了这个token之后，我就能把我的公共SSH密钥添加到实例中，然后再通过我的私钥去连接它，就能连接到Vimeo在Google云上的实例，按照上述我们预设的步骤成功实现SSRF。（此处可参考[另一Vimeo
SSRF漏洞](https://www.freebuf.com/vuls/197912.html)）

![](https://image.3001.net/images/20191220/1576839538_5dfca972bb3d6.png!small)

## 漏洞上报及处理进程

> 2019.4.29 漏洞初报
>
> 2019.4.29 Vimeo给予前期$100奖励
>
> 2019.5.1 Vimeo确认并修复漏洞
>
> 2019.5.1 Vimeo给予 $4900 奖励

 ***参考来源：[medium](https://medium.com/@dPhoeniixx/vimeo-upload-function-ssrf-7466d8630437)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

