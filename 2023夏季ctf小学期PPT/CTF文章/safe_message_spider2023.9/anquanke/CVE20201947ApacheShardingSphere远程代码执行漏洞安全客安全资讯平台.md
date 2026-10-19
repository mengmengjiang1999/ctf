# CVE-2020-1947：Apache ShardingSphere远程代码执行漏洞

阅读量 **753150**

发布时间 : 2020-03-11 10:30:06

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01f8581defc9d27aaa.jpg)

近日监测到友商关于CVE-2020-1947的漏洞公告，360灵腾安全实验室判断漏洞等级为高，利用难度低，威胁程度高，影响面中。建议使用用户及时安装最新补丁，以免遭受黑客攻击。

## 0x00 漏洞概述

ShardingSphere是一套开源的分布式数据库中间件解决方案组成的生态圈，它由Sharding-JDBC、Sharding-Proxy和Sharding-Sidecar（计划中）这3款相互独立的产品组成。
他们均提供标准化的数据分片、分布式事务和数据库治理功能，可适用于如Java同构、异构语言、云原生等各种多样化的应用场景。

![](https://shardingsphere.apache.org//document/current/img/shardingsphere-hybrid.png)

该漏洞起于Sharding-UI配置项中可直接进行yaml的代码解析，从而造成反序列化远程代码执行漏洞。

## 0x01 漏洞详情

Sharding-UI的默认密码为admin/admin

![](https://p3.ssl.qhimg.com/t0172b06ec07a781ecf.png)

经过身份验证的攻击者在前端输入的data未经处理直接传入`unmarshal()`方法

![](https://p5.ssl.qhimg.com/t01e0d1ac55de812365.png)

可以看到`unmarshal()`方法直接将内容传入 yaml.snakeyaml 的`load()`方法进行解析

![](https://p4.ssl.qhimg.com/t0122479f9cec7d4847.png)

因为SnakeYaml支持反序列化Java对象，所以当`yaml.load()`函数的参数可控时，攻击者就可以传入一个恶意的yaml格式序列化内容，最终造成远程命令执行

![](https://p4.ssl.qhimg.com/t0125c1ffc0b5b84596.png)

## 0x02 影响版本

Apache ShardingSphere < =4.0.0

## 0x03 处置建议

1.安装最新版本：

在最新版4.0.1中，引入了ClassFilterConstructor()进行白名单校验

![](https://p2.ssl.qhimg.com/t0164aacf174e0e18b3.png)

<https://github.com/apache/incubator-shardingsphere/releases>

2.修改admin的默认密码：

位于`/incubator-shardingsphere-4.0.0/sharding-ui/sharding-ui-backend/src/main/resources/application.properties`文件中，并重启服务

## 0x04 关于我们

灵腾安全实验室(REDTEAM)正式成立于2020年，隶属于360政企-实网威胁感知部；主攻研究方向包括红队技术、物理攻防、安全狩猎等前瞻技术，为
**360AISA全流量威胁分析系统** 、 **360天相资产威胁与漏洞管理系统** 、 **360虎安服务器安全管理系统** 、
**360蜃景攻击欺骗防御系统** 核心产品提供安全赋能。

## 0X05 Reference

<https://mp.weixin.qq.com/s/1vmXLZ_Dn7_BLDtSlj07Cw>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360灵腾安全实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/200554](/post/id/200554)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __1赞

 __收藏

![](https://p1.ssl.qhimg.com/t01fae47a70f20e70ec.png) 360灵腾安全实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

