# 0x01 写在前面

今天发现了个有趣的URL特性，跟大家分享下。授权项目，重马伺候~

# 0x02 漏洞发现

拿到系统，先找高危，看到一处文件上传：

![](https://image.3001.net/images/20210824/1629790322_6124a072cc404af8994bf.png!small)

本来想试下任意文件上传，结果白名单验证，遂放弃。但是测试过程中发现了个有趣的现象：

![](https://image.3001.net/images/20210824/1629790323_6124a07363a457a752701.png!small)![](https://image.3001.net/images/20210824/1629790323_6124a073f3ee8aa87a0ea.png!small)

附件名称可控！虽然附件名称不会影响上传的文件名，也就是对我们的上传没有帮助，但这里可能还存着其他的利用方式！安排：

![](https://image.3001.net/images/20210824/1629790324_6124a07474efda5655b52.png!small)![](https://image.3001.net/images/20210824/1629790325_6124a075261d8be288564.png!small)

没错，测试XSS，`script`标签被吃掉了，换`img`:

![](https://image.3001.net/images/20210824/1629790325_6124a075888e3852a7e2b.png!small)

上传成功，点击图片：

![](https://image.3001.net/images/20210824/1629790326_6124a0761af5266148cf5.png!small)![](https://image.3001.net/images/20210824/1629790326_6124a0769fbc5c281186d.png!small)

问题不大，成功弹窗。这里能执行js代码是因为附件名称引入到了`title`标签中：

![](https://image.3001.net/images/20210824/1629790327_6124a0775a60ca9802a60.png!small)

上XSS平台payload，同理我们还是用`img`标签：

![](https://image.3001.net/images/20210824/1629790327_6124a077cf073a48579a5.png!small)

上传后，发现payload不完整：

![](https://image.3001.net/images/20210824/1629790328_6124a07864d6f82d2d01c.png!small)![](https://image.3001.net/images/20210824/1629790328_6124a078c77618e8cbe02.png!small)

仔细研究后，得知`/`后面的内容才会被引入`title`，http协议都是带`/`的，不带协议的话又不能成功访问到链接，尝试URL编码后亦无法绕过。

正当我百思不得解时，突然想到，既然`/`不行，那何不用`\`试试？于是有了以下payload：

![](https://image.3001.net/images/20210824/1629790329_6124a0793ab1675e4274d.png!small)

来看一下结果：

![](https://image.3001.net/images/20210824/1629790330_6124a07a4b1e0690ff3f8.png!small)

这就舒服了，`\`果然可以带入执行，接下来就是解决`https:// ==> https:\\`：

![](https://image.3001.net/images/20210824/1629790330_6124a07abc74270234fec.png!small)![](https://image.3001.net/images/20210824/1629790331_6124a07b40941d66d4e5d.png!small)

看起来好像成功了，其实并没有，反斜杠被吃掉了一个：

![](https://image.3001.net/images/20210824/1629790331_6124a07bb1080edc0eacb.png!small)

于是构造`<Img+sRC=https:\\\xss.pt\\k7gmp.jpg>`，文件传上去了，但是发现死活点不开，此时又陷入了僵局。

正当我再次愁眉苦脸时，发现了一个非常有趣的现象：访问`https:\www.baidu.com`竟然可以成功访问到百度！！这就好办了，改一下payload：`<Img+sRC=https:\\xss.pt\\k7gmp.jpg>`，这次，他，终于来了！

![](https://image.3001.net/images/20210824/1629790332_6124a07c4b234441f8671.png!small)![](https://image.3001.net/images/20210824/1629790332_6124a07cd1d08c37d1daa.png!small)

成功get存储型XSS一枚~

# 0x03 写在最后

后来跟大佬们交流的时候发现，还有其他有趣的特性，比如`www.baidu。com`也可以成功访问，用来使用句号绕过点的过滤，interesting~

