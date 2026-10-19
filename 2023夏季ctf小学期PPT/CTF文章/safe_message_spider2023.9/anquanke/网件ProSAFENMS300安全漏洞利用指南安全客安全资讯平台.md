# 网件 ProSAFE NMS300安全漏洞利用指南

阅读量 **106416**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-02-06 13:42:57

 **x**

##### 译文声明

本文是翻译文章，文章来源： E安全

原文地址：[http://mp.weixin.qq.com/s?__biz=MzI4MjA1MzkyNA==&mid=404448728&idx=1&sn=7c8ed250b8eb9b02696a204fb0a3c859&scene=23&srcid=0206fGyweKkz9ajgI7zhXg11#rd](http://mp.weixin.qq.com/s?__biz=MzI4MjA1MzkyNA==&mid=404448728&idx=1&sn=7c8ed250b8eb9b02696a204fb0a3c859&scene=23&srcid=0206fGyweKkz9ajgI7zhXg11#rd)

译文仅供参考，具体内容表达以及含义原文为准。

一位安全研究人员已经发布相关代码，指出Netgear ProSAFE NMS300网络管理系统中存在两项可利用之严重安全漏洞。

大家是否正在使用Netgear ProSAFE NMS300管理系统？如果答案是肯定的，那各位恐怕要担心一下了——因为安全研究员Pefro
Ribeiro已经在这台网络设备当中发现了两项严重安全漏洞。

Netgear ProSAFE NMS300管理系统允许管理员利用一套用户友好型Web界面对网络体系进行监控与管理。

此次影响该设备的安全漏洞（不限上传任何高危文件类型）被认证为CVE-2016-1524，其能够被远程、未授权攻击者用于向该系统上传任意文件。

一旦文件上传完成，其将获得如下所示之服务器root目录URL：

    
    
    http://<IP>:8080/null<文件名>

另外，其可利用SYSTEM权限加以执行。

这项远程代码执行漏洞在CVSS处得到了8.3评分，攻击者可以向NMS300当中默认安装的两个Java
servlet小型服务程序之一发送一段经过特制的POST请求对其加以利用。

“通过向该servlet发送一段特制POST请求，攻击者能够成功上传任意文件，并通过NMS300服务器的root目录利用http://<IP>:8080/null<文件名>进行访问。该NMS300服务器将以SYSTEM权限对其加以运行。”卡内基梅隆大学CERT发布的这份报告指出（地址https://www.kb.cert.org/vuls/id/777024）。

第二项漏洞（对受限目录（‘路径遍历’）之名称做出不当限制）被收录为CVE-2016-1525。这项同样存在于Netgea ProSAFE
NMS300中的漏洞属于目录遍历机制，允许通过身份验证的攻击者从该设备中下载任意文件。

“经过身份验证的攻击者能够向http://<IP>:8080/data/config/image.do?method=add发送一条特制POST请求以修改其realName参数，从而从服务器主机中将任意本地文件载入至Web服务中的可预测位置。该文件随后可通过http://<IP>:8080/data/config/image.do?method=export&imageId=&lt;ID>进行下载，其中的<ID>为数字形式，每次有文件上传其计数将加1.”这份报告补充称。

安全专家Ribeiro早在去年12月就已经通过CERT/CC报告了这项Netgear漏洞，但该问题截至目前仍存在于系统当中。

Riberio同时针对该漏洞发布了概念验证代码，大家可以点击此处下载这两个Metasploit模块（http://seclists.org/fulldisclosure/2016/Feb/30）。

在等待修复的过程中，建议大家将该Web管理界面同互联网隔离开来。

本文翻译自 E安全
[原文链接](http://mp.weixin.qq.com/s?__biz=MzI4MjA1MzkyNA==&mid=404448728&idx=1&sn=7c8ed250b8eb9b02696a204fb0a3c859&scene=23&srcid=0206fGyweKkz9ajgI7zhXg11#rd)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83458](/post/id/83458)

安全客 - 有思想的安全新媒体

本文转载自: [
E安全](http://mp.weixin.qq.com/s?__biz=MzI4MjA1MzkyNA==&mid=404448728&idx=1&sn=7c8ed250b8eb9b02696a204fb0a3c859&scene=23&srcid=0206fGyweKkz9ajgI7zhXg11#rd)

如若转载,请注明出处：
[http://mp.weixin.qq.com/s?__biz=MzI4MjA1MzkyNA==&mid=404448728&idx=1&sn=7c8ed250b8eb9b02696a204fb0a3c859&scene=23&srcid=0206fGyweKkz9ajgI7zhXg11#rd](http://mp.weixin.qq.com/s?__biz=MzI4MjA1MzkyNA==&mid=404448728&idx=1&sn=7c8ed250b8eb9b02696a204fb0a3c859&scene=23&srcid=0206fGyweKkz9ajgI7zhXg11#rd)

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

