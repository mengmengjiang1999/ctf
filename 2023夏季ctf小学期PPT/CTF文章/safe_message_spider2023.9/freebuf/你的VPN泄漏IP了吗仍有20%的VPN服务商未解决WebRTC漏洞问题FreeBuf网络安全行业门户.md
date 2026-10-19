**其实自 2015 年 1 月开始，大约有 20% 的 VPN 方案提供商会因为 WebRTC 漏洞泄漏用户 IP 。但这个问题几遍在今天，一些 VPN
厂商也并没有对此作出改进。**

这个问题是由安全研究员 Paolo Stagno （VoidSec）发现，他对 83 款VPN应用程序进行了安全审计测试，发现了旧版本的 WebRTC IP
泄漏问题。

![VPN-WebRTC-Leak.png](https://image.3001.net/images/20180329/15222929535696.png!small)  

Stagno 表示在他的调查过程中有 17 款 VPN 会通过网页浏览器直接泄漏用户的IP地址。具体的研究成果已经公开在 [Google Doc
](https://docs.google.com/spreadsheets/d/1Nm7mxfFvmdn-3Az-BtE5O0BIdbJiIAWUnkoAF_v_0ug/edit#gid=0)在线文档中。但Stangno
表示，自己的工作并不是最完整的版本，因为他没有财力对所有的商用 VPN 服务进行测试。

## VPN 安全测试地址

即便如此，目前这项 VPN 安全测试计划仍在发展。研究员 Stagno 正在社区中呼吁其他的安全研究员对自己使用的 VPN
客户端进行测试，并将安全测试的结果分享出来。

![屏幕快照 2018-03-29
上午11.36.07.png](https://image.3001.net/images/20180329/15222946246095.png!small)  

他制作了一个[ Demo 测试网页](https://ip.voidsec.com)
（<https://ip.voidsec.com>）用于浏览器环境的VPN测试。

同时在 [GitHub](https://github.com/VoidSec/WebRTC-Leak)
也有公开测试代码，如果用户想要进行本地测试也可以自行下载。

***如发现问题，大家也可以将测试结果评论在汇总文档中：[地址](https://docs.google.com/spreadsheets/d/1Nm7mxfFvmdn-3Az-BtE5O0BIdbJiIAWUnkoAF_v_0ug/edit#gid=0)**

## 自 2015 年开始出现的 WebRTC 问题

早在在 2015 年，安全研究员 Daniel Roesler 发现了 WebRTC 漏洞。 当时他发现如果客户端是基于 NAT ，代理或 VPN
的，WebRTC STUN 服务器在 WebRTC 连接时会保留用户公网以及私网 IP 。

STUN 服务器会将这些数据泄漏给那些已经与用户浏览器进行了 WebRTC 连接的站点。

该漏洞出现之后，许多广告商以及执法机构都会使用 WebRTC 漏洞来获取网站访客的IP地址。

![webrtc.jpg](https://image.3001.net/images/20180329/15222954082267.jpg!small)  

## 多数浏览器默认开启WebRTC

多年以来，浏览器们一直绞尽脑汁才将 WebRTC 集成到他们的代码之中。

但为了应对这个漏洞，浏览器都推出了可以防止IP泄漏的官方插件，以削弱部分实时通讯功能为代价，换取安全性。
**但即便如此，除了Tor，Edge和Internet Explorer之外，多数浏览器都是默认开启 WebRTC 的状态。**

以下是 Stagno 发现的受到IP泄漏影响 VPN提供商列表，详细信息可以参阅 Stagno 的 [Google
文档](https://docs.google.com/spreadsheets/d/1Nm7mxfFvmdn-3Az-BtE5O0BIdbJiIAWUnkoAF_v_0ug/edit#gid=0)。  

    
    
    BolehVPN (仅在美国地区)
    ChillGlobal (Chrome 及 Firefox 插件)
    Glype (不同配置情况不同)
    hide-me.org
    Hola!VPN
    Hola!VPN Chrome 扩展程序
    HTTP PROXY navigation in browsers that support Web RTC
    IBVPN Browser Addon
    PHP Proxy
    phx.piratebayproxy.co
    psiphon3 (如果使用 L2TP/IP并不泄漏)
    PureVPN
    SmartHide Proxy (不同配置情况不同)
    SOCKS Proxy on browsers with Web RTC enabled
    SumRando Web Proxy
    TOR as PROXY on browsers with Web RTC enabled
    Windscribe Addons

在其他的研究中，安全团队还发现 115 个 VPN 客户端中有 26 款保留了用户某些类型的日志文件。

***参考来源：[bleepingcomputer](https://www.bleepingcomputer.com/news/security/many-vpn-providers-leak-customers-ip-address-via-webrtc-bug/)，编译Elaine，转载请注明FreeBuf.COM**

