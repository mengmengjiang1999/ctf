# 伪装QQ红包&绕过URL检测

阅读量 **198068**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-09-24 10:23:49

 **x**

##### 译文声明

本文是翻译文章，文章来源：mtfly@360安全播报

译文仅供参考，具体内容表达以及含义原文为准。

**一、绕过PC端恶意URL提示**

“腾讯外部漏洞报告处理流程”中提到了一个越权的url检测网址[http://www.qq.com_521_qq_diao_yu_wangzhan_789.com/
](http://www.qq.com_521_qq_diao_yu_wangzhan_789.com/)直接发出来的话肯定是提示恶意链接的。

(其实可以手机QQ是无法正常识别出这个url的,所以希望能够改进一下手机客户端的URL识别。)

并且是无法直接打开的,只能复制url。

直接用QQ浏览器的手机采用打开,刚开始是提示恶意链接,不用管,然后点击分享

分享给QQ好友以后,手机还有PC上分别显示为

PC:

手机QQ:

PC端已经不再红色恶意链接提示了。可直接打开url。

此时测试结果:

PC端QQ URL检测:绕过

手端QQ URL检测:提示

欺骗性:弱

  

**二、伪装“红包”**

只是这种绕过恶意url检测,是没有多大意义的,毕竟很多用户又不傻,不会去点击类似这种:

的链接的。下面就去改进一下,首先我们需要一个被腾讯报恶意链接并且可控的网站。(毕竟钓鱼网站都是可控的):

<http://www.bzxlcj.com/>

添加一个test.html

    
    
    <html>
    <head>
    <meta itemprop="name" content="发红包啦!">
    <meta itemprop="image"   content="https://mqq-imgcache.gtimg.cn/res/mqq/hongbao/img/message_logo_100.png">  
    <meta name="description"   itemprop="description" content="赶紧点击拆开吧!">
    <meta http-equiv="Content-Language"   content="zh-CN">
    <meta HTTP-EQUIV="Content-Type"   CONTENT="text/html; charset=gb2312">
    <title></title>
    </head>
    <body>
    钓鱼网站
    </body>
    </html>

这时候发出来还是会报恶意url

还是用手机QQ打开(会有恶意提示)

,并且分享给QQ好友。

(经过测试,发现这个拉取摘要的过程并不是在本地进行的。)

PC端还有手机QQ端分别显示为

PC:

手机QQ:

这样就可以达到欺骗用户的目的了。

此时测试结果:

PC端QQ URL检测:绕过

手端QQ URL检测:提示

欺骗性:中

  

**三、绕过手机端QQ恶意url检测**

其实一二两种情况只能绕过PC端,局限性非常大!下面来绕过手机端的恶意url检测。

当手机QQ打开一个连接的时候

[http://111.161.83.162/cgi-bin/httpconn?htcmd=0x6ff0080&u=http%3A%2F%2Fwww.bzxlcj.com%2Ftest.html](http://111.161.83.162/cgi-bin/httpconn?htcmd=0x6ff0080&u=http%3A%2F%2Fwww.bzxlcj.com%2Ftest.html)

这是一个url跳转链接,类似的还有很多,之前有人在wooyun上报过此类的url跳转,腾讯之所以不认为是漏洞,是因为这种跳转会对url进行恶意url检测,一旦发现是恶意的url,那么将会自动进行屏蔽!

所以我们想要绕过就很简单,就是绕过这个url检测机制即可。

首先把<http://www.bzxlcj.com/test.html>转换成短域名

[http://t.cn/RyGbYXw](http://t.cn/RyGbYXw)

当我直接给好友发送短域名的时候,是这么显示的

PC:

手机QQ:

这个时候打开已经无提示了。

有人说,这不就是一个普通的跳转么?怎么能算一个漏洞?可以看到手机是直接解析短域名的302跳转,去读取概要的。既然已经可以进行跳转了,并且读取出概要解析成链接形式了,为什么不再进行一次检测呢?漏洞的关键就出在这里!

当然这样有一个弊端,就是电脑是不显示红包效果的。只是一个跳转链接。

我们可以这么解决,

1.随便找个好友发送信息<http://t.cn/RyGbYXw>

2.断网,打开网址,并且稍等知道出现无法连接。此时网站是不进行跳转的。

3.连网,点击分享给好友。

这个时候转发出来,就是完美的过手机+PC恶意url检测机制,并且伪装红包。

手机端:

PC端:

PC端QQ URL检测:绕过

手端QQ URL检测:绕过

欺骗性:中

最终版:修改PC端角标&一键生成

还有两个问题:

1.右下角有QQ浏览器字样

2.太TM麻烦了!

有没有简单一键生成的!,并且左下角显示QQ红包的啊!?

有!

一键生成版:

[http://connect.qq.com/widget/shareqq/index.html?url=http%3A%2F%2Fmtfly.net&desc=&title=%E5%8F%91%E7%BA%A2%E5%8C%85%E5%95%A6%EF%BC%81&summary=%E8%B5%B6%E7%B4%A7%E7%82%B9%E5%87%BB%E6%8B%86%E5%BC%80%E5%90%A7%EF%BC%81&pics=http%3A%2F%2Fmqq-imgcache.gtimg.cn%2Fres%2Fmqq%2Fhongbao%2Fimg%2Fmessage_logo_100.png&flash=&site=QQ%E7%BA%A2%E5%8C%85&style=101&width=96&height=24&showcount=](http://connect.qq.com/widget/shareqq/index.html?url=http%3A%2F%2Fmtfly.net&desc=&title=%E5%8F%91%E7%BA%A2%E5%8C%85%E5%95%A6%EF%BC%81&summary=%E8%B5%B6%E7%B4%A7%E7%82%B9%E5%87%BB%E6%8B%86%E5%BC%80%E5%90%A7%EF%BC%81&pics=http%3A%2F%2Fmqq-imgcache.gtimg.cn%2Fres%2Fmqq%2Fhongbao%2Fimg%2Fmessage_logo_100.png&flash=&site=QQ%E7%BA%A2%E5%8C%85&style=101&width=96&height=24&showcount=)

web版:

    
    
    <script type="text/javascript">
    (function(){
    var p = {
    url:'http://mtfly.net',
    desc:'',
    title:'发红包啦!',
    summary:'赶紧点击拆开吧!',
    pics:'https://mqq-imgcache.gtimg.cn/res/mqq/hongbao/img/message_logo_100.png',
    flash: '',
    site:'QQ红包',
    style:'101',
    width:96,
    height:24
    };
    var s = [];
    for(var i in p){
    s.push(i + '=' + encodeURIComponent(p[i]||''));
    }
    document.write(['<a href="http://connect.qq.com/widget/shareqq/index.html?',s.join('&'),'" target="_blank">分享到QQ</a>'].join(''));
    })();
    </script>
    <script src="http://connect.qq.com/widget/loader/loader.js" widget="shareqq" charset="utf-8"></script>

其实这就是腾讯的分享组件修改的。<http://connect.qq.com/intro/sharetoqq/>

PC:

手机:

完美!

PS:其实腾讯的恶意url跳转是指网站url跳转的时候的恶意url判断,比如http://111.161.83.162/cgi-bin/httpconn?htcmd=0x6ff0080&u=http%3A%2F%2Fwww.bzxlcj.com%2Ftest.html

我上面的理解有些偏差吧。

本文翻译自mtfly@360安全播报 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/82466](/post/id/82466)

安全客 - 有思想的安全新媒体

本文转载自: [mtfly@360安全播报]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

