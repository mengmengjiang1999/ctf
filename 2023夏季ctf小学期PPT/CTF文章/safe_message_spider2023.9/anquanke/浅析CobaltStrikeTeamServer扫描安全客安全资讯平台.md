# 浅析Cobalt Strike Team Server扫描

阅读量 **375336**

发布时间 : 2021-04-16 15:30:28

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t015207c9883bfa3674.png)

## 前言

Cobalt Strike 是由Strategic
Cyber公司开发的一款商业化渗透测试工具。该软件具有简单易用、可扩展性高等优点，并且具备团队协作等特点，因此被广大黑客、白帽子和安全研究人员等大量装备使用。网络空间测绘就是利用扫描发掘互联网中一切可发掘的资产和目标。Cobalt
Strike 的发掘，是360 Quake团队一直以来的核心目标之一。

在本文中我们将站在蓝方角度思考，通过研究Cobalt Strike客户端与服务端交互的代码逻辑，来发掘出Cobalt Strike Team
Server特征，并且进行进一步探测与分析。

## 逻辑分析

Cobalt Strike 的是C/S（Client-Server）架构，有一个客户端与Team
Server进行通信。首先，简单看下代码。在完成Swing组件的加载后，用户输入用户名、密码等信息后，点击Connect按钮，触发aggressor.dialogs下的Connet类的dialogAction方法。如图所示，代码逻辑会将密码传入一个SecureSocket实例的authenticate方法中。

![](https://p1.ssl.qhimg.com/t0121c5a216dff55c31.png)

然后创建数据输出流实例，将\x00\x00\xbe\xef+ 密码长度 + 密码 + 填充字符等数据传给Team
Server，如果返回51966（\x00\x00\xco\xfe）则证明密码正确。

![](https://p4.ssl.qhimg.com/t01f0400fb2cd415389.png)

查看服务端的代码认证逻辑(ssl.SecureServerSocket.java)，发现在密码正确后返回51966(\x00\x00\xca\xfe)，密码错误返回0（\x00\x00\x00\x00）。

![](https://p3.ssl.qhimg.com/t01b7639f2fd87edf94.png)

通过Wireshark抓包如图所示，可以看到客户端发送的密码及填充字符串。

![](https://p4.ssl.qhimg.com/t01f99ac2c2514346c8.png)

通过以上代码逻辑，可以找到一个识别Cobalt Strike Team Server的方法，流程图及部分代码如下图所示：

![](https://p3.ssl.qhimg.com/t0132ee4cc185440493.png)

![](https://p1.ssl.qhimg.com/t01a98d0f44dbf0a734.png)

为了利用该特征获取更多资产，我们希望把Cobalt Strike 中被控制的IP给提取出来，就是Cobalt Strike 登陆后的Session
Table提取出来，如图所示。

![](https://p0.ssl.qhimg.com/t015ae159ba74f59746.png)

同样先看下代码，在通过密码验证后，会创建一个TeamQueue的实例。

![](https://p1.ssl.qhimg.com/t0155df63b491134c8e.png)

通过查看该类的构造方法，发现在创建该实例的时候，同时启动了两个线程来对TeamQueue中请求和响应进行监控。

![](https://p5.ssl.qhimg.com/t01f3a79e487d7c5c75.png)

如图所示，TeamQueue类的call方法中会根据传入的参数实例化一个Request对象,并添加进队列，之后TeamQueue
Writer线程从队列获取请求对象，使用socket进行发送。

![](https://p2.ssl.qhimg.com/t018cf9bbedbc1e5594.png)

![](https://p5.ssl.qhimg.com/t0168f65a07d149b30e.png)

TeamQueue Reader时刻监听着来自Team Server的响应。

![](https://p0.ssl.qhimg.com/t018bb3975f1e05e910.png)

以上就是Cobalt
Strike客户端发包和接收响应的大致逻辑。在创建TeamQueue实例后开始调用call方法来发送不同阶段的请求。我们进一步抓包分析。如图所示

![](https://p5.ssl.qhimg.com/t012b92b7f35eb60051.png)

结合抓包和查看代码发现客户端与服务端交互的流程如下图所示。

![](https://p5.ssl.qhimg.com/t01cf53fe1bf0fb4e77.png)

在客户端发送aggressor.ready请求后，表示一切准备就绪，开始和服务端进行数据同步，这其中就有session
table的数据。根据以上的逻辑，然后手动代码实现这几个请求，就能够在识别出Cobalt
Strike后进一步爆破密码，在爆破出密码后提取出目标的受控IP。如图所示。

![](https://p3.ssl.qhimg.com/t017c2ae0b58012c652.png)

最终的扫描流程图见附录。

## 扫描结果分析

网络空间测绘始于扫描，不止于扫描。在找到该特征后，我们开始在互联网中进行挖掘。  
使用搜索语句： response:”\x00\x00\xca\xfe” AND port: “50050”，可以找到存在弱口令的Cobalt
Strike，我们只对部分主机进行了受控IP的提取，这步骤稍微敏感，大家可以自行操作。

![](https://p0.ssl.qhimg.com/t015687a9388311b429.png)

![](https://p3.ssl.qhimg.com/t013ac78a9ae0aab3b8.png)

![](https://p1.ssl.qhimg.com/t0164422ff3e3910be9.png)

随机登录一台如图：

![](https://p3.ssl.qhimg.com/t01463c69c85605d5d9.png)

通过搜索语法 response:”\x00\x00\x00\x00” AND port: “50050” AND service: “http/ssl”  
可以找到没有爆破出密码的Cobalt Strike，可以看到共有5173条扫描记录，1049个IP。

![](https://p5.ssl.qhimg.com/t0115ea7fb9c9b44fd0.png)

## 部分IoC

![](https://p3.ssl.qhimg.com/t013413203c2280a186.png)

## 结论

网络空间测绘，始于资产，但不止于资产。

我们认为，主动测绘数据将会与终端行为样本数据、网络流量通信数据一样，是未来网络安全大数据&&威胁情报数据的重要源头。主动测绘数据和基于测绘数据分析后形成的知识将能够极大补充我们的视野，从而开拓出更多的攻击面和领域。  
更多网络空间测绘领域研究内容，敬请期待~

## 附录

![](https://p1.ssl.qhimg.com/t012c51d7b443f785ec.png)

## 文末福利

360Quake首次推出用户激励计划“当红蓝对抗遇上空间测绘”。

![](https://p4.ssl.qhimg.com/t01236bd0ef97401c35.jpg)

![](https://p2.ssl.qhimg.com/t0151f2be3edafb26fb.jpg)

**添加微信：quake_360 邀您入群！**

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360Quake空间测绘系统** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/238391](/post/id/238391)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [网络空间测绘](/tag/网络空间测绘)
  * [Quake](/tag/Quake)

 **+1** __3赞

 __收藏

![](https://p1.ssl.qhimg.com/t012b988516a9bc9afd.png) 360Quake空间测绘系统

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

