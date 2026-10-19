# app抓包的另一种姿势

阅读量 **437926**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-24 16:30:37

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t015f307557d0f8ce5d.png)

## 前言

​
在测试某app时发现无法常规抓包，于是用端口转发解决了该问题。做一个记录帮助大佬们拓展思路。经过研究发现该app是在本地监听起了一个服务，用来处理业务逻辑，之后把数据进行加密发送到服务端。

## 抓包分析

  1. 常规抓包分析

小弟先是尝试常规的抓包方案，在WiFi里面设置代理，然后burp+xp模块justTrustMe。疯狂操作之后发现根本没包过来，于是猜测是用tcp传输的。

  1. 肉丝大佬的r0capture也没成功，这里不多bb
  2. tcpdump抓包尝试

直接抓全部网卡流量，保存到login.pcap

    
    
    ./tcpdump -i any -w login.pcap
    

![](https://p4.ssl.qhimg.com/t0181c5f798ccbbab9e.png)

然后在app上疯狂操作，此处无图自行脑补。

把包拖回本地wireshark分析。此处直接过滤http请求

![](https://p4.ssl.qhimg.com/t01c7031a1c25029c4f.png)

经过分析后发现http是在本地通信的，还有一些加密数据用了tcp。既然实在本地通信的，那么它本地肯定起了一个服务，我们就从这里入手。

看一下该app监听的端口

![](https://p0.ssl.qhimg.com/t01394d4e611d855130.png)

发现的确监听了一个端口,然后尝试把端口转发出来进行测试。

![](https://p0.ssl.qhimg.com/t01d265802b91c2a6f2.png)

直接访问发现没任何反应。

![](https://p4.ssl.qhimg.com/t01d6916b2f09d559b9.png)

猜测是不是服务端对ua有判断，接着尝试用浏览器访问发现也不行。

![](https://p1.ssl.qhimg.com/t01428a33aef8e34f12.png)

于是回过头来仔细分析抓到的包。

先跟着http流，能更直观的看到干了什么。

![](https://p4.ssl.qhimg.com/t01b8ff71aad17aabd0.png)

一目了然

![](https://p1.ssl.qhimg.com/t01c72ac4af5756f467.png)

发现请求的域名是自定义的，于是我构造一个一样的包发过去。

![](https://p4.ssl.qhimg.com/t015680a4b68391b126.png)

直接起飞！

接下来就可以愉快的测试了。

## 最后

这算是一个小小的思路，对于大佬来说骚操作肯定还有很多，可惜我是菜狗啊。如有不足之处欢迎大佬指点和纠正，小弟感激不尽。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Safe6Sec** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/253303](/post/id/253303)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [移动安全](/tag/移动安全)
  * [流量分析](/tag/流量分析)
  * [抓包](/tag/抓包)

 **+1** __10赞

 __收藏

![](https://p2.ssl.qhimg.com/t012c98ac855fe79cd5.jpg) Safe6Sec

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

