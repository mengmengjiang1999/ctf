# Microsoft JET RCE漏洞预警

阅读量 **185000**

发布时间 : 2018-09-25 20:44:10

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0140c31eedc7f16b93.png)

## 0x00 漏洞背景

2018年9月20日 Zero Day Initiative（ZDI）团队已公开披露了Microsoft JET数据库引擎中的一个严重的远程执行代码漏洞。

JET数据库引擎和windows捆绑在一起，并且被多个windows产品所使用。

## 0x01 漏洞详情

该漏洞是JET数据库引擎中的一个越界（OOB）写入造成的。

微软的OLE DB Provider for JET和Access ODBC仅支持32位，这意味着在64位的主机上无法获得直接利用。  
但在64位主机上可以通过启动

    
    
    c：\ windows \ SysWOW64 \wscript.exe poc.js

来使用32位wscript.exe来触发该PoC。

同时这种攻击可以通过Internet Explorer进行触发，即使在64位Windows上，Internet Explorer渲染过程也是32位的。

但在IE11上 – 在Internet和Intranet区域中禁用了安全设置“跨域访问数据源”，这会导致JavaScript错误。无法触发漏洞。

同时从本地驱动器（或USB磁盘）启动恶意poc.html也会触发该漏洞。但需要户按下“允许阻止的内容”才会触发。

## 0x02 漏洞验证

PoC内容如下

![](https://p0.ssl.qhimg.com/t011f282744c6d7218e.png)

触发后引起wscript.exe崩溃

![](https://p1.ssl.qhimg.com/t011fdfa329faf14cc9.png)

## 0x03 防御措施

官方尚未发布针对的补丁

360CERT建议

  * 谨慎行事，不要打开来自不信任来源的文件
  * 更新IE浏览器版本，避免随意点击允许阻止内容按钮

## 0x04 时间线

2018-08-05 ZDI向微软提交漏洞

2018-09-20 ZDI公布漏洞细节以及PoC

2018-09-25 360CERT发布预警

## 0x05 参考链接

  1. <https://www.zerodayinitiative.com/blog/2018/9/20/zdi-can-6135-a-remote-code-execution-vulnerability-in-the-microsoft-windows-jet-database-engine>
  2. <https://support.microsoft.com/en-in/help/957570/the-microsoft-ole-db-provider-for-jet-and-the-microsoft-access-odbc-dr>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/160724](/post/id/160724)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞预警](/tag/漏洞预警)
  * [安全漏洞](/tag/安全漏洞)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

