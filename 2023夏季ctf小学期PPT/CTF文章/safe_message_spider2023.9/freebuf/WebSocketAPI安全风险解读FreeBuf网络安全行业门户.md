## 1\. WebSocket协议

### 1.1 简介

WebSocket协议是基于TCP的一种新的网络协议。它实现了客户端与服务器全双工（full-duplex）通信，即允许服务器主动发送信息给客户端。因此，在WebSocket中，客户端和服务器只需要完成一次握手，两者之间就直接可以创建持久性的连接，并进行双向数据传输，这样也使得客户端和服务器之间的数据交换变得更加简单。

![v2-eaeb5903ffaf33e6bc89cdeaa09dba0a_720w.png](https://image.3001.net/images/20230703/1688371124_64a27fb4edc82810ac543.png!small)

### 1.2 特点

WebSocket特点如下：

  * 较少的控制开销。在连接建立后，服务器和客户端之间交换数据时，用于协议控制的数据包头部相对较小。在不包含扩展的情况下，对于服务器到客户端的内容，此头部大小只有2至10字节（和数据包长度有关）；对于客户端到服务器的内容，此头部还需要加上额外的4字节的掩码。

  * 更强的实时性。由于协议是全双工的，所以服务器可以随时主动给客户端下发数据。

  * 保持连接状态。与HTTP不同的是，Websocket需要先建立连接，这就使得其成为一种有状态的协议，之后通信时可以省略部分状态信息。而HTTP请求可能需要在每个请求都携带状态信息（如身份认证等）。

  * 更好的二进制支持。Websocket定义了二进制帧，相对HTTP，可以更轻松地处理二进制内容。

  * 可以支持扩展。Websocket定义了扩展，用户可以扩展协议、实现部分自定义的子协议。

  * 更好的压缩效果。相对于HTTP压缩，Websocket在适当的扩展支持下，可以沿用之前内容的上下文，在传递类似的数据时，可以显著地提高压缩率。

### 1.3 WebSocket 和 HTTP 的区别

![v2-6ad5a2ebc51022dd7c185260cf245b37_720w.png](https://image.3001.net/images/20230703/1688371125_64a27fb59eb8ad3f50c5f.png!small)

  * HTTP 是一个无状态的协议，使客户端向服务器请求资源，并从服务器接收响应。客户端使用 HTTP 请求/响应语法，即请求发送到服务器之后，服务器向客户端返回 HTML 文件、图像和其他媒体内容。

  * WebSocket 通信协议尝试在较大范围内改进 Web 实时通信和插件技术，并提供全双工、基于事件的通信而无需采用低效的轮询方式。开发人员可以从 Web 浏览器的 JS 端轻松地创建 WebSocket 连接并发送数据，进而实现应用程序的实时数据传输的实现。

  * 由于 WebSocket 是面向消息的，因此它更加适用于实时通信，而 HTTP 更适用于请求和服务器-客户端通信的响应。

## 2\. WebSocket API

Websocket 使用 ws 或 wss 的统一资源标志符（URI），其中 wss 表示使用了 TLS 的
Websocket，类似于HTTP协议的http和https。wss协议通过TLS连接建立一个WebSocket，即加密传输；ws协议即明文传输。

ws://echo.websocket.org

wss://echo.websocket.org

WebSocket API与传统API一样都是由通信协议、域名、版本号、路径、请求参数等要素组成，只是由于WebSocket
API在完成握手流程之后，客户端和服务端之间就创建了持久性的连接，并且可以直接用文本消息或者二进制消息进行通信的数据交互，这样我们在WebSocket
API流量报文中看到的一般都是JSON格式文本消息。

从开发的角度，WebSocket API还包括了：

  * 构造函数，构造函数的语法示例为：const myWebSocket = new WebSocket(url [, protocols])，其中url表示连接的 URL；protocols表示为一个协议字符串或者一个包含协议字符串的数组，为可选。

  * 属性：属性分为很多主要有bufferedAmount，表示未发送至服务器的字节数；onopen，表示用于指定连接成功后的回调函数，等等。

  * 方法：方法主要分为close和send，分别表示WebSocket关闭连接和数据传入服务器。

  * 事件：事件主要有close、error、message、open。

## 3\. WebSocket API业务场景

WebSocket API作为一种重要客户端-服务器通信接口，究竟在哪些业务场景下能够用到WebSocket API呢？主要分为三大类：

  * 实时数据更新的应用程序：对于一些需要服务端不断发送数据在客户端实时显示的应用，使用WebSocket API作为数据传输接口无疑是最好的选择。

  * 游戏应用程序：在游戏应用中，一般的场景是服务器需要不断接收数据，无需刷新UI，传输的数据就会在屏幕上生效，UI也会自动刷新，不需要建立新的连接。

  * 聊天应用程序：聊天应用程序一般会有较长的连接状态，以方便用户与用户之间的实时交流，采用WebSocket API只需建立一次连接便可以实现一对一的消息传输，并且保持长时间的通讯连接。

具体业务场景列举：

![v2-fd2e05193759e51100c7de40a5e3ccd7_720w.png](https://image.3001.net/images/20230703/1688371126_64a27fb65717ec86987f4.png!small)

## 4\. WebSocket API安全风险

WebSocket API的安全风险主要分为两大类：常规攻击风险和特有攻击风险。以下是这两大类风险的详细解读。

### 4.1 WebSocket API常规攻击风险

（1）消息体输入漏洞

和HTTP协议一样，WebSocket
API在传输消息的时候一般采用json格式传输文本，所以对于消息体中参数依然可以可以进行SQL注入、XSS、命令执行、文件读取、SSFR、任意文件上传......等常规输入性漏洞攻击。![v2-9d6b1c0dc9d5fd7d25107904b1551ad2_720w.png](https://image.3001.net/images/20230703/1688371126_64a27fb6e79edf606f8e7.png!small)

漏洞案例：

在线聊天应用中使用WebSocket API在客户端和服务端之间传输消息。当一个用户输入聊天消息时，如下的一个WebSocket消息被发送到服务端：

![v2-37d40b826131065beebb6072ee62c445_720w.png](https://image.3001.net/images/20230703/1688371127_64a27fb78313253d789a9.png!small)

​服务端会将这个消息内容通过WebSocket API转发给另外一个用户，然后在另一个用户的浏览器中被JS渲染为一段HTML代码。

![v2-a676febc1f2b431be9e3d6c97ed5a754_720w.png](https://image.3001.net/images/20230703/1688371128_64a27fb804dc155696ea0.png!small)

​当服务器没有对转发的内容做安全防御或过滤时，通过修改WebSocket API消息体实施xss攻击。

![v2-adc4d3a63a187fc97b5de2bdfcfd0e78_720w.png](https://image.3001.net/images/20230703/1688371128_64a27fb8b19aa69e6d358.png!small)

​

![v2-82f7c6246f5fd561062f15983bf4496e_720w.png](https://image.3001.net/images/20230703/1688371129_64a27fb995eb70812e973.png!small)

​（2）身份认证绕过

WebSocket API没有规定服务器在握手阶段应该如何认证客户端身份。服务器可以采用任何 HTTP 服务器的客户端身份认证机制，如
cookie认证，HTTP 基础认证，TLS 身份认证等，在WebSocket
API在身份认证面临的攻击风险和传统的API面临的风险是一样的，因此WebSocket API同样面临着OWASP API
2023十大安全风险中的API2：身份认证失效风险。

![v2-a2fafd63e6f6a44486e05b79c84ea085_720w.png](https://image.3001.net/images/20230703/1688371130_64a27fba92a712b6f362c.png!small)

（3）授权失效

同身份认证一样，WebSocket API没有明确指定任何授权方式，API中用户资源访问等的授权策略由服务端或开发者实现。WebSocket
API也会存在和传统Web应用相同的安全风险，如：垂直越权、水平越权、未授权访问等等安全风险。所以WebSocket API同样面临OWASP API
2023十大安全风险中API1:对象级别授权失效、API3:对象属性级别授权失效、API5:功能级别授权失效的安全风险。

![v2-22d41d2a72a72361085a43f17835a5b9_720w.png](https://image.3001.net/images/20230703/1688371131_64a27fbb630a15a362b15.png!small)

（4）拒绝服务

WebSocket API同样易遭受拒绝服务攻击，其面临风险分为客户端拒绝服务风险和服务端拒绝服务风险。

  * 客户端拒绝服务：WebSocket 连接限制不同于HTTP连接限制，WebSocket有一个更高的连接限制，不同的浏览器的最大连接数也存在差异，通过发送恶意内容，占用所有Websocket，导致浏览器资源耗尽，引起拒绝服务。

  * 服务端拒绝服务：WebSocket建立的是持久连接，只有客户端或服务端其中一方发起关闭连接的请求，连接才会关闭。攻击者可以通过发起请求并建立大量的连接，导致服务器资源耗尽，引发拒绝服务攻击。

### 4.2 WebSocket API 特有攻击面

（1）跨站WebSockets劫持

在WebSocket
API发起WebSocket握手请求时，浏览器会在请求中添加一个名为Origin的HTTP头，Oringin字段表示发起请求的源，以此来防止未经授权的跨站点访问请求。WebSocket
规范中没有强制规定握手阶段的 Origin
头是必需的，且WebSocket不受浏览器同源策略的限制。如果服务端没有针对Origin头部进行验证可能会导致跨站点WebSocket劫持攻击，当WebSocket握手请求仅依靠HTTP
cookie进行会话处理并且不包含任何CSRF
token或其他不可预测的值时，也有可能会造成这种漏洞。这攻击风险类似于JSONP劫持，是属于CSRF攻击的一种。

漏洞示例：

通过实时聊天发送聊天消息：

![v2-12aa71fcc98ab9fe7e3fd4a1853f3883_720w.png](https://image.3001.net/images/20230703/1688371132_64a27fbc8efa4de0ddb4e.png!small)

在WebSocket握手请求中发现仅仅是靠cookie进行会话处理，并没有CSRF的防护手段。

![v2-6a3447a3f23a03aed4ff4920081d9c3d_720w.png](https://image.3001.net/images/20230703/1688371133_64a27fbd4a92261ba5136.png!small)

​查看WebSocket历史消息记录。

![v2-6df66fe50ea439ef152d6b667e1b4821_720w.png](https://image.3001.net/images/20230703/1688371134_64a27fbe244d7d2e062e4.png!small)

​在浏览器中找到漏洞利用服务器。

![v2-869076f6e55fc145efbc641c6a22b56c_720w.png](https://image.3001.net/images/20230703/1688371134_64a27fbedb7a30b491d2b.png!small)

同时我们在burp设置一个burp client，这里模拟的是攻击者。

![v2-320d3c6a61e3b208624afcd8af62de93_720w.png](https://image.3001.net/images/20230703/1688371135_64a27fbf65dea0a217018.png!small)

在漏洞利用服务器中贴入利用JS代码。

![v2-48434ddde136f8ea6b5dfe9fe19326ea_720w.png](https://image.3001.net/images/20230703/1688371136_64a27fc017e47a556456d.png!small)

漏洞利用服务器并将漏洞利用程序传递给受害者，然后在攻击者也就是我们创建的burp client中返回了受害者相关敏感信息。

![v2-9c2f3f730e321548f0248ee4173b4016_720w.png](https://image.3001.net/images/20230703/1688371136_64a27fc09055cf0b995f6.png!small)

解码发现用户登陆凭证。

![v2-90d818e38cc3af805225d032ac90b4bd_720w.png](https://image.3001.net/images/20230703/1688371137_64a27fc140e60e266f713.png!small)

​（2）中间人攻击

同样是出现在操控WebSocket握手流程时的攻击风险，可以通过获取并篡改WebSocket握手请求，实施以下攻击：

通过伪造客户端信息与服务器建立WebSocket连接；无条件信任HTTP头，导致某些安全策略可以被绕过。例如：X-Forwarded-For头，XSS绕过WAF；应用程序自定义的HTTP标头引入的攻击面。

漏洞案例：

在线聊天中使用了XSS攻击之后，攻击已被阻止，并且WebSocket 连接已终止。

![v2-da949c72221eb0d489c125c2b2ac001b_720w.png](https://image.3001.net/images/20230703/1688371138_64a27fc2b0bbb615c7478.png!small)

拦截WebSocket 握手请求并使用X-Forwarded-For头来绕过黑名单。

![v2-dec3fafcec9c6445b2184cfc37ee7394_720w.png](https://image.3001.net/images/20230703/1688371139_64a27fc325600451edfab.png!small)

一直采用这种方式进行绕过后，等到聊天框重新出现就说明绕过了黑名单的检测，并且可以实施xss攻击，后续步骤可以参考上述消息体输入漏洞攻击中的案例。

![v2-713cf32b07bc93611c4c4aeb5fed9f9f_720w.png](https://image.3001.net/images/20230703/1688371139_64a27fc3db400d3c144a0.png!small)

### 4.3 安全风险总结

实际上，几乎所有的Web漏洞都有可能出现在WebSocket中。因为，WebSocket本质上就是一个通过HTTP建立连接的双向全双工的通信协议而已，但由于其相比HTTP多了一“工”的特性，可能会出现一些WebSocket
API特有的攻击场景。所以，WebSocket
API除了面临着传统API的安全风险之外，还有容易遭受由于自己特殊性而产生的攻击，这些攻击来自于WebSocket API的握手请求流程。

