# 【漏洞分析】Struts2高危漏洞S2-048分析

阅读量 **342939**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-07-07 21:06:09

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

**作者： n1nty**

  

本次漏洞触发点在：

org.apache.struts2.s1.Struts1Action.execute() 方法中，如下图所示。

org.apache.struts2.s1.Struts1Action 类为一个 Wrapper 类，用于将 Struts1 时代的 Action 包装成为
Struts2 中的 Action，以让它们在 struts2 框架中继续工作。

在 Struts1Action 的 execute 方法中，会调用对应的 Struts1 Action 的 execute
方法（第一个红色箭头处）。在调用完后，会检查 request 中是否设置了 ActionMessage，如果是，则将会对 action messages
进行处理并回显给客户端。处理时使用了 getText 方法，这里就是漏洞的触发点。所以漏洞的触发条件是：在 struts1 action
中，将来自客户端的参数值设置到了 action message 中。

在官方提供的 Showcase 中，就存在漏洞，如下图：

getText 方法的主要作用就是实现网站语言的国际化，它会根据不同的 Locale 去对应的资源文件里面获取相关文字信息（这些文件信息一般保存在
.properties 文件中），这些文字信息往往会回显至客户端。

Action messages 会通过 getText 方法最终进入
com.opensymphony.xwork2.util.LocalizedTextUtil.getDefaultMessage(String,
Locale, ValueStack, Object[], String) 方法，如下：

此方法会将 action message 传入
com.opensymphony.xwork2.util.TextParseUtil.translateVariables(String,
ValueStack)。com.opensymphony.xwork2.util.TextParseUtil.translateVariables(String,
ValueStack) 方法主要用于扩展字符串中由 ${} 或 %{} 包裹的 OGNL 表达式，这里也就是 OGNL 的入口，随后 action
message 将进入 OGNL 的处理流程，漏洞被触发。

**关于 POC**

    
    
    暂不公布

**总结**

该漏洞触发需要非默认插件 struts2-struts1-plugin

需要手动寻找程序中将客户端参数值添加入 action message 的点

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86398](/post/id/86398)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

