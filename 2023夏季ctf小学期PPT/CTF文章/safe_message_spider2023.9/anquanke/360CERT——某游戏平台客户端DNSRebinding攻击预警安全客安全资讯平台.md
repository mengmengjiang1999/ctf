# 360CERT——某游戏平台客户端DNS Rebinding攻击预警

阅读量 **295537**

|评论 **2**

发布时间 : 2018-01-24 12:00:34

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://cert.360.cn/static/fileimg/blizzard-1_1516713643.png)

> 报告编号：B6-2018-012301
>
> 报告来源：360网络安全响应中心
>
> 报告作者： MerJerson，SuperXX
>
> 更新日期：2018年01月23日

## 0x00背景介绍

谷歌安全研究人员，发现某游戏平台存在漏洞。该平台应用中嵌套着 Blizzard Update Agent
组件，采用内建RPC代理的方式对应用进行维护，并随主程序一起启动。该组件在监听本地1120端口的JSON RPC服务时，有受DNS
Rebinding攻击的风险。

## 0x01漏洞影响

漏洞详情如下：

![](https://cert.360.cn/static/fileimg/blizzard-2_1516714797.png)

攻击流程如下：

![](https://cert.360.cn/static/fileimg/blizzard-3_1516713669.png)

## 0x02技术分析

### DNS rebinding攻击

DNS是互联网核心协议之一，在一次网络请求中，先根据域名查出IP地址，再向IP地址请求资源。

DNS rebinding 攻击步骤：

  1. 则是当用户第一次请求时，解析域名获取IP地址A；
  2. 域名持有者改变域名地址对应IP改为B；
  3. 用户再次请求，获取IP地址为B

用户两次请求相同域名获取的IP地址不同，在没有对IP地址做足够验证的情况下，很容易造成安全问题，DNS
rebinding常用在服务端请求伪造中。在此漏洞中，服务端没有对本地请求做权限认证，攻击者可以通过将域名重定向到本地IP，进行攻击

### RPC代理服务器没有进行DNS Rebinding攻击的防护

一些程序会采用内建RPC代理的方式进行应用维护。接口如果没有进行安全防护，会带来安全隐患。结合DNS
Rebinding攻击，甚至可以向本地Agent代理发送特权命令。

在某游戏平台客户端中，未对Blizzard Update
Agent进行任何安全防护，访问localhost:1120/agent可以得到本地RPC代理服务器信息。同时也可以通过发送向RPC代理服务器发送json格式的控制命令进行操作。

![](https://cert.360.cn/static/fileimg/blizzard-4_1516713681.png)

在结合DNS Rebinding攻击，任何网站可以将某个域名解析为本地主机。这意味着任何网站都可以向本地Agent代理发送特权命令。

## 0x03漏洞复现

将本地127.0.0.1和攻击网站地址199.241.29.227进行绑定。

![](https://cert.360.cn/static/fileimg/blizzard-5_1516713691.png)

在攻击网站上构建软件更新的RPC指令，指定目录到C:/exploit：

  1. {
  2. “uid”: “battle.net”,
  3. “instructions_product”: “Bna”,
  4. “game_dir”: “C:/exploit”,
  5. “finalized”: true
  6. }

![](https://cert.360.cn/static/fileimg/blizzard-6_1516713702.png)

攻击成功后：

![](https://cert.360.cn/static/fileimg/blizzard-7_1516713711.jpg)

![](https://cert.360.cn/static/fileimg/blizzard-8_1516713722.png)

## 0x04安全建议

相关厂家未对该漏洞推送补丁。请受影响的用户关注补丁推送，及时更新。

## 0x05时间线

2017年12月8日 taviso\@google将漏洞提交到暴雪

2018年1月23日 暴雪确定漏洞

2018年1月23日 360CERT发布相关预警

## 0x06参考链接

[https://bugs.chromium.org/p/project-zero/issues/detail?id=1471&desc=3](https://bugs.chromium.org/p/project-zero/issues/detail?id=1471&desc=3)

<http://lock.cmpxchg8b.com/yah4od7N.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/95895](/post/id/95895)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [DNS](/tag/DNS)
  * [游戏](/tag/游戏)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

