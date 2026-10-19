# CVE-2018-5318：D-Link soap.cgi 缓冲区溢出

阅读量 **251335**

|评论 **8**

发布时间 : 2018-01-10 16:09:23

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

#

> 老板前一段给买了几款路由把玩，研究了下D-Link DIR 629、DIR 823这两款板子。发现在 _soap.cgi_
> 中存在几处栈溢出，均可以远程利用，并且其他型号的路由也有对soap这一部分代码的复用。

## 逆向分析与漏洞挖掘

因为是想挖几个能远程利用的洞，首先去看了HTTP服务，也就是 _/htdocs/cgibin_ 。

D-Link HTTP服务由 _cgibin_ 提供，并通过软链接的文件名进入到不同的处理分支：

在各个cgi处理函数中，会通过 _cgibin_parse_request_ 来解析用户输入，其函数原型大致如下：

![](https://p3.ssl.qhimg.com/t01a873ec8e5cc360a6.jpg)

参数 _save_param_func_ 用于传入解析/存储HTTP请求的具体handler，读取HTTP请求后使用该handler具体处理用户输入。在
_soapcgi_main（0x00418E28）_ 中传入了漏洞函数 _vulnerable_sprintf_parser_ _（0x0041893C）_
：

![](https://p4.ssl.qhimg.com/t0108f14348964101a1.jpg)

跟进 _vulnerable_sprintf_parser_ 可以发现程序未进行边界检查便将全局变量 _g_http_soapaction_ 通过
_sprintf_ 写到栈上：

![](https://p4.ssl.qhimg.com/t01d43613e57baece34.jpg)

_g_http_soapaction_ 来自于 _soapcgi_main_ 中对HTTP Header _SOAPACTION_ 字段的解析：

取 _HTTP_SOAPACTION_ ：

![](https://p4.ssl.qhimg.com/t01eca57120ee2defa2.jpg)

取 _#_ 后的值：

![](https://p3.ssl.qhimg.com/t01a97980575b60255d.jpg)

至此漏洞原理已经明了： _soapcgi_main_ 中未进行边界检查便将HTTP Header中的SOAPACTION字段存储至栈上，导致栈溢出。

## 漏洞利用

基础信息：

![](https://p0.ssl.qhimg.com/t013ef042e5f66220ef.jpg)

MIPS大端序，开启了NX，未开启ASLR、PIE，只需要做个ROP。

溢出的崩溃现场如下：

![](https://p5.ssl.qhimg.com/t01c303139d187cf752.jpg)

$S0、$S2-S3、$FP、$SP指向的内存可控，要编写ROP只能在这几个寄存器上做文章，最终用ropper在uClibc中找了个很不错的gadget：

现在需要做的就是找到libc加载的实际基址。

在隔壁开锁王师傅的指导下把板子拆开，接上串口：

![](https://p0.ssl.qhimg.com/t01915453d91bcc7394.jpg)

成功获取到shell：

![](https://p4.ssl.qhimg.com/t01e386cd5b213c6d80.png)

拿到shell后读/proc/pid/maps就可以获取到libc的加载基址。

最终编写ROP如下：

![](https://p4.ssl.qhimg.com/t018a3416b0e9701236.jpg)

攻击演示：

![](https://p3.ssl.qhimg.com/t0137c8b54d3ce13fbc.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **0keeTeam** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/94289](/post/id/94289)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞](/tag/漏洞)
  * [D-Link](/tag/D-Link)
  * [缓冲区溢出](/tag/缓冲区溢出)

 **+1** __1赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) 0keeTeam

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

