# Apache OpenOffice RCE（CVE-2020-13958）漏洞预警

阅读量 **259321**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-11-12 17:30:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01fc08294692e9ab9c.jpg)

Apache OpenOffice 4（包括经过测试的最新版本4.1.7）容易受到远程代码执行的攻击；
如果受害者在Windows上打开了精心制作的.odt文档，则攻击者可以完全控制他们的计算机。

漏洞问题是，该产品无法像宏执行一样处理script：event-listener处理程序。

使用这样的构造：

    
    
    <office:scripts>
    <office:event-listeners>
    
    <script:event-listener script:language="ooo:script" xlink:href=".uno:OpenHyperlinkOnCursor" script:event-name="dom:load"/>
    </office:event-listeners>
    </office:scripts>

在OpenOffice中，无需任何确认对话框即可触发打开URL，包括专门供内部使用的特殊.uno或.service链接处理程序。

![](https://p5.ssl.qhimg.com/t01b17fed808d9a4ccc.gif)

PoC可以在Windows上弹出计算器。 还支持UNC目标，在这种情况下，它们受操作系统的“网络标记”安全警告的约束。

触发.uno或.service动作在Linux上也能正常工作-尽管找不到将其转变为在该OS上执行代码的实用方法。

受影响的版本

Apache OpenOffice 4 versions before 4.1.8.

参考链接：<https://github.com/irsl/apache-openoffice-rce-via-uno-links>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **剑思庭** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/222281](/post/id/222281)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CVE-2020-13958](/tag/CVE-2020-13958)
  * [OpenOffice](/tag/OpenOffice)

 **+1** __2赞

 __收藏

![](https://p5.ssl.qhimg.com/t0182efdec4d3825ae2.png) 剑思庭

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

