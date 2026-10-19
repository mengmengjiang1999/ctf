**本文所涉及的DoH加密传输信息的技术仅用于技术分享与讨论，严禁用于其他用途，所带来的法律风险与本文无关。**

##  **一、DoH（DNS-over-HTTPS）简介**  

**DNS服务器就像一个在线的电话本，记录域名和IP地址的映射关系。当用户想要访问某个网站的时候，先向DNS服务器请求解析域名，得到网站服务器的IP，再与网站服务器进行通信，请求网页的内容，最终得以在浏览器呈现内容。但是DNS请求是没有加密的，请求的域名会以明文的方式传输。**

为了有效防止用户上网时的中间人攻击(Man-in-Middle Attack,
MIMT攻击)，同时也更好地保护用户的隐私，HTTPS开始推行，即将用户的HTTP通信加密传输。于是由传统的DNS+HTTP变为DNS+HTTPS，这使得用户的HTTP通信变得安全，但是要注意到此时的DNS环节仍旧是明文传输，用户的上网行为（访问哪些域名）仍旧暴露在网络上。

于是，和HTTP通信类似，DNS请求环节也应该被加密以保护用户的隐私，即由DNS+HTTPS升级为DoH+HTTPS，这样用户的上网行为得到了全程的加密保护。目前已有多个服务提供商提供DoH服务，如Google（[https://dns.google.com/resolve](https://dns.google.com/resolve?)）、Quad9（<https://dns.quad9.net/dns-query>），firefox和Chrome浏览器也提供相应的设置或插件。

下图是通过浏览器普通访问[ _www.baidu.com时产生的DNS_](/)流量，可以在数据包中明显看出用户请求的域名是[
_www.baidu.com_](http://www.baidu.com/)。  

![图1普通DNS流量.jpg](https://image.3001.net/images/20190709/1562643534_5d240c4eb3395.jpg!small)

下图是通过quad9提供的DoH服务解析[
_www.baidu.com_](http://www.baidu.com/)时产生的流量，此时已经无法看到用户的上网行为。

![图2DoH流量.jpg](https://image.3001.net/images/20190709/1562643588_5d240c84d35d4.jpg!small)

##  **二、隐私不等于安全**

研究人员发现，在2017年HTTPS流量已经在全球Web流量中占比超过50%，但恶意软件作者的采用率高于普通用户。通过加密保护数据安全中所指的100%安全，其实也为恶意软件提供了更强的隐蔽性，为监管带来新的压力。HTTPS如此，DoH亦然。

下面提出一种基于DoH实现的隐蔽通信，恶意流量可以由加密保护“安全”送达不法分子的DNS服务器，并通过请求DNS
TXT记录获得不法分子预留在DNS服务器中的信息。

TXT记录是在DNS服务器上为某域名记录配置说明的一种方法，当请求域名的TXT记录时DNS服务器会返回对应字符串。

假设不法分子申请了域名fengrou2019.club，并配置了解析该域名及其子域名的DNS服务器（以下简称被控DNS服务器），在被控DNS服务器的域名映射表内添加[
_www.fengrou2019.club的TXT_](/)记录为“helloword”作为不法分子预留给恶意软件的信息。

![图3DoH通信结构图.png](https://image.3001.net/images/20190709/1562643626_5d240caad7a0c.png!small)

在受控DNS服务器上，设置本地未命中请求的转发表，将本地无法解析的请求转发给权威DNS服务器，本例中配置Google
DNS（ip：8.8s.8.8）。于是，该DNS服务器可以实现正常DNS服务器的功能，解析请求的域名。

![图4DNS转发表.png](https://image.3001.net/images/20190709/1562643647_5d240cbf79a0d.png!small)

在本地解析文件中配置[ _www.fengrou2019.club的TXT_](/)记录“helloword”。

![图5TXT记录创建.png](https://image.3001.net/images/20190709/1562643662_5d240cceba307.png!small)

###  **1** **恶意软件获取TXT记录信息**

恶意软件通过HTTPS通信向提供DoH服务的权威DNS服务器请求[
_www.fengrou2019.club的TXT_](/)记录，拿到了控制者预留的“helloword”。

![图6获取TXT记录.jpg](https://image.3001.net/images/20190709/1562643694_5d240cee7c09f.jpg!small)

通过抓包检测流量情况，可以看见被TLS加密的信息交互。

![图7流量被加密.jpg](https://image.3001.net/images/20190709/1562643721_5d240d094842e.jpg!small)

###  **2** **恶意软件通过DNS请求在受控DNS服务器留下信息**

假设恶意软件想向控制者发送“helloword”，则可以通过DoH解析“helloword.fengrou2019.club”来传递信息。由于DNS请求通过HTTPS发送，所以请求的域名不会被旁路知晓，但是受控DNS在响应请求时处理的是明文信息，所以控制者可以在受控DNS看到“helloword”。

①恶意软件请求解析“helloword.fengrou2019.club”。

![图8向DNS服务器发送helloword.png](https://image.3001.net/images/20190709/1562643743_5d240d1f0cb97.png!small)

②恶意软件的网络中无法知晓恶意软件的具体网络行为，捕获的流量与先前解析[www.fengrou2019.club](http://www.fengrou2019.club)时一样，是被加密保护的。

![图9传递的信息被加密.png](https://image.3001.net/images/20190709/1562643757_5d240d2d0de6d.png!small)

③在受控主机可以看到明文的helloword.fengrou2019.club请求。

![图10DNS服务器获取helloword.png](https://image.3001.net/images/20190709/1562643797_5d240d55602d4.png!small)

##  **三、防御建议**

技术是一把双刃剑，在保护用户私人数据隐私的技术不断发展的同时，也为不法分子提供了便利，给监控带来了新的挑战。

现有的监控工具常布置在网络边缘；此外，有的浏览器提供恶意域名检测，可以向用户告警或直接拦截访问请求；DNS服务器也部署有黑名单，不支持对黑名单内域名的解析请求。

对于本文所述的信息泄露方式，可以考虑在应用层监测域名请求，应用层位于TLS之上，在应用层可捕获到请求域名的明文字符串，对于不正常的域名，如长度过长，信息熵异常等域名，应予以拦截和告警；DNS服务提供商亦应当部署相应黑名单或恶意域名检测技术；对于自身不使用DoH技术进行网络活动的用户，可以在防火墙设置拦截自身不使用且支持DoH技术的DNS服务器。

 ** ***本文作者： BUPT/AG9GgG，ArkTeam/XHJ，转载请注明来自FreeBuf.COM****

