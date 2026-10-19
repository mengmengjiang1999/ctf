# 【漏洞分析】Apache Struts2–052 漏洞分析预警

阅读量 **142801**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-09-06 14:17:39

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

****

**传送门**

[**【漏洞预警】Apache
Struts2插件高危漏洞(S2-052)**](http://bobao.360.cn/news/detail/4291.html)

****

**0x00 漏洞描述**

The REST Plugin is using a XStreamHandler with an instance of XStream for
deserialization without any type filtering and this can lead to Remote Code
Execution when deserializing XML payloads. — Apache Struts 官方安全通告(参考1)

2017年9月5日，Apache Struts发布最新安全公告，Apache
Struts2的REST插件存在远程代码执行的高危漏洞，该漏洞由lgtm.com的安全研究员汇报，漏洞编号为CVE-2017-9805（S2-052）。Struts2
REST插件的XStream组件存在反序列化漏洞，使用XStream组件对XML格式的数据包进行反序列化操作时，未对数据内容进行有效验证，存在安全隐患，可被远程攻击。

Struts2启用了rest-plugin后并编写并设置了 **XStreamHandler** 后，可以导致远程命令执行这一严重问题。

**0x01 漏洞影响面**

**影响面**

确定CVE-2017-9805为高危漏洞。 实际场景中存在一定局限性，需要满足一定条件，非struts本身默认开启的组件。

**影响版本**

Version 2.5.0 to 2.5.12

Version 2.3.0 to 2.3.33

**修复版本**

Struts 2.5.13

Struts 2.3.34

**0x02 漏洞详情**

**技术细节**

文件 **/org/apache/struts2/rest/ContentTypeInterceptor.java**

在struts2 rest-plugin 中的处理逻辑里接受到对应格式的消息时，会调用已经注册的对应 **handler** 的
**handler.toObject** 方法对其进行实例化，在这里传入的xml消息，所以就会跳转到已经定义的 **XStreamHandler**
的toObject方法

在经过此处的 **fromXML** 方法后导致实例化的恶意对象被执行，导致恶意代码执行

随即看到计算器被成功弹出

**漏洞修复**

新版本中增加了 **XStreamPermissionProvider**

并且对原先有问题的 **createXStream** 进行重写，增加了校验，拒绝不安全的类执行

**0x03 漏洞利用验证**

**0x04 修复建议**

1.官方建议设置插件处理的数据类型限定为json

    
    
    <constant name="struts.action.extension" value="xhtml,,json" />

2.升级Struts到2.5.13版本或2.3.34版本

3.在XStreamHandler中进行数据校验或检查

**0x05 时间线**

2017-09-05 漏洞披露

2017-09-06 360CERT发布预警分析通告

**0x06 参考链接**

Apache Struts 安全通告 <http://struts.apache.org/docs/s2-052.html>

**传送门**

[**【漏洞预警】Apache
Struts2插件高危漏洞(S2-052)**](http://bobao.360.cn/news/detail/4291.html)

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86777](/post/id/86777)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

