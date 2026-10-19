## 0x01 什么是 WebSocket

### WebSocket

简单地说，WebSocket 协议允许服务器可以主动向客户端推送信息，而传统的 HTTP 协议只能是客户端向服务器发出请求，服务器返回查询结果。

WebSocket 建议于 TCP 协议之上，与 HTTP 协议有良好的兼容性。  
协议标识符是`ws`；如果加密，则为`wss`，服务器网址就是 URL，看一段 WebSocket 的代码，比较通俗易懂，并不需要过多讲解。

    
    
    var ws = new WebSocket("vans.org");
    
    ws.onopen = function(evt) { 
      console.log("Connection open ..."); 
      ws.send("Hello WebSockets!");
    };
    
    ws.onmessage = function(evt) {
      console.log( "Received Message: " + evt.data);
      ws.close();
    };
    
    ws.onclose = function(evt) {
      console.log("Connection closed.");
    };
    

### WebSocket 与 HTTP

形象理解一下 WebSocket 与 HTTP
在发送数据的问题，参考[WebSocket原理](https://www.zhihu.com/question/20215561)。

WebSocket 允许服务器和用户 **互相** 发送消息。  
HTTP 只允许用户发送请求给服务器。

HTTP 小场景，模拟 ajax 轮询

> 客户端：啦啦啦，有没有新信息(Request)  
> 服务端：没有（Response）  
> 客户端：啦啦啦，有没有新信息(Request)  
> 服务端：没有。。（Response）  
> 客户端：啦啦啦，有没有新信息(Request)  
> 服务端：你好烦啊，没有啊。。（Response）-loop

WebSocket 小场景

> 客户端：啦啦啦，有没有新信息，没有的话就等有了才返回给我吧（Request）  
> 服务端：额。。 等待到有消息的时候。。来 给你（Response）  
> 客户端：啦啦啦，有没有新信息，没有的话就等有了才返回给我吧（Request） -loop

前文说到 WebSocket 是一种协议，且与 HTTP 兼容性很好，于是我们抓一个 WebSocket 的包观察一下；在 Burpsuite
当中存在一个专门为 WebSocket 服务的界面叫 "WebSockets History"。

![image](https://image.3001.net/images/20220410/1649594239_6252cf7f9e65cef0fe6da.png!small)

![image](https://image.3001.net/images/20220410/1649594245_6252cf8589436cceede87.png!small)

这边再放个 HTTP 的包对比一下。

![image](https://image.3001.net/images/20220410/1649594252_6252cf8cabeb397c9b48d.png!small)

很明显的看到 WebSocket 的 Response 非常不一样。

## 0x02 基于 WebSocket 的漏洞详解

在讲靶场与知识点之前，我们先介绍一下应用 WebSocket 最多的场景 —————— Live Chat，或者是一些直播，对于 Live Chat
这一场景来说，是需要用户与服务器的交互，服务器也与用户交互。

在 Burpsuite 当中，有一个专门的 WebSockets History，在这里我们可以看到 WebSocket 的记录。

### 1\. 尝试修改 WebSocket 的发送内容，造成 XSS 攻击

> ##### Lab: Manipulating WebSocket messages to exploit vulnerabilities

点开靶场，我们移步到 Live Chat 的界面。

![image](https://image.3001.net/images/20220410/1649594261_6252cf953e34493969acf.png!small)

先抓包，接着发送一条数据，并在 WebSockets History 中查看数据，修改包，构造成 XSS 的 POC。

    
    
    <img src=1 onerror='alert(1)'>
    

![image](https://image.3001.net/images/20220410/1649594270_6252cf9e28c326885bff5.png!small)

发包，再回到 Web 界面的时候成功实现 XSS。

![image](https://image.3001.net/images/20220410/1649594275_6252cfa39e3f33e713b43.png!small)

### 2\. 操纵 WebSocket 的握手过程利用漏洞

WebSocket 的握手过程：

WebSocket 的 Request 包在发送过程中，比 HTTP 包多了几个数据。

    
    
    Upgrade: websocket
    Connection: Upgrade
    Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==
    Sec-WebSocket-Protocol: chat, superchat
    Sec-WebSocket-Version: 13
    

这个就是Websocket的核心了，告诉Apache、Nginx等服务器：**注意啦，窝发起的是Websocket协议，快点帮我找到对应的助理处理~不是那个老土的HTTP。

Sec-WebSocket-Key 是一个Base64 encode的值，这个是浏览器随机生成的，负责验证。

Sec_WebSocket-Protocol 是一个用户定义的字符串，用来区分同URL下，不同的服务所需要的协议。

Sec-WebSocket-Version 是告诉服务器所使用的Websocket Draft（协议版本）

上述就是 WebSocket 的握手全过程，操纵 WebSocket 的握手过程一般有一下三种攻击方法，这些方法是用来辅助攻击的，而不是攻击的主题。

> 1.由于服务器过于信任用户的输入，在 HTTP Header 中伪造`X-Forwarded-For`，绕过一些安全策略。
>
> 2.WebSocket 消息修改，也就是上面的一个靶场，因为处理 WebSocket 消息的会话上下文通常由握手消息的会话上下文确定。
>
> 3.应用程序使用的自定义 HTTP Header 引入的攻击面。

##### Lab: Manipulating the WebSocket handshake to exploit vulnerabilities

先交代清楚这道题目的防御措施，不然讲起靶场来，乱七八糟。

这道靶场当中，服务器会过滤 WebSocket 消息中关于 XSS 的攻击，也就是说，当我们输入`<img src=1
onerror='alert(1)'>`时，会被过滤，而且我们的 IP 会被封禁，在短时间内无法再发起 WebSocket 连接。

由此我们可以尝试伪造 XFF，让自己成为不被封禁的 "IP"

 **靶场部分**  
同样去到 Live Chat 界面发完消息后抓包，修改 message 信息，构造 XSS 攻击的 POC。

    
    
    <img src=1 onerror='alert(1)'>
    

发出消息许久，无回显，很明显是被过滤了，而且再发消息也没有响应， IP 也被封禁。  
![image](https://image.3001.net/images/20220410/1649594285_6252cfadca10043087e68.png!small)接着点
Reconnect，修改 XFF 之后发包，可以立马连接上。再尝试绕过方法，构造 POC。

    
    
    <img src=1 oNeRrOr=alert`1`>
    

![image](https://image.3001.net/images/20220410/1649594296_6252cfb82c69da5a0b563.png!small)

成功过关 ~

## 0x03 基于 WebSocket 的 CSRF

CSRF 相关的知识可以移步至我的博客[CSRF攻击 | 芜风](https://withd-raw.github.io/2021/12/10/PortSwigger-CSRF%E6%94%BB%E5%87%BB/)下学习，这里简单提一提。

### 1\. 基于 WebSocket 的 CSRF 的定义

Cross-site WebSocket hijacking，也就是跨域 WebSocket 劫持攻击，是基于 WebSocket 的握手过程进行的
CSRF 攻击。

造成这种攻击的根本原因在于 WebSocket 的握手只依赖于 HTTP Cookie 进行会话处理，而没有任何其他不可预测的值。例如 CSRF Token
或是其他的。

### 2\. 跨站点 WebSocket 劫持的危害

#### (1) 越权

也就是熟知的访问控制，垂直越权与水平越权。

#### (2) 泄露数据

因为 WebSocket 的通信是全双工通信的，所以用户与服务器之间交互的信息有可能被攻击者监听，这种监听是无声的监听，被攻击者不知道自己处于被监听状态。

从而造成信息的泄露

### 3\. 实现跨站点的 WebSocket 劫持攻击

前面说到，跨站点的 WebSocket 劫持攻击一般是因为 WebSocket 的握手消息，只由 HTTP Cookie 判断，并且在请求参数中不使用
CSRF Token 或其他随机值。

就和之前的 CSRF 攻击差不多，我们直接看靶场。

> ##### Lab: Cross-site WebSocket hijacking

和之前一样，去到 Live Chat 界面，抓包发包。

![image](https://image.3001.net/images/20220410/1649594310_6252cfc63ff7ec84b37b9.png!small)

毕竟是 CSRF 嘛，去到 Port 提供的第三方服务器，exploit server，并使用 Burp Collaborator。

在 Exploit Server 中构造 payload

![image](https://image.3001.net/images/20220410/1649594949_6252d245d7467ba823006.png!small)

再 Deliver to victim，在 Burp Collaborator 界面点击`Poll now`。

![image](https://image.3001.net/images/20220410/1649594959_6252d24fb4218eeaa80ac.png!small)

去找到泄露的信息。

![image](https://image.3001.net/images/20220410/1649594965_6252d2558c12b99a64481.png!small)

去到 MyAccout 下登录即可 ~

## 0x04 基于 WebSocket 的一系列漏洞的防御措施

> 1.使用 wss 协议（WebSockets over TLS）。
>
> 2.对 WebSockets 端点的 URL 进行硬编码，此处要注意业务点，和用户的输入数据区分开，不要讲用户的输入数据也硬编码了。
>
> 3.保护 WebSocket 握手消息免受 CSRF 的攻击，以避免跨站点 WebSockets 劫持漏洞。
>
> 4.将通过 WebSocket 接收的数据视为在两个方向上都不受信任。在服务器端和客户端安全地处理数据，以防止基于输入的漏洞，如 SQL 注入和
> CSRF。

博客地址，还请大家多多支持 [芜风](https://drun1baby.github.io/)

