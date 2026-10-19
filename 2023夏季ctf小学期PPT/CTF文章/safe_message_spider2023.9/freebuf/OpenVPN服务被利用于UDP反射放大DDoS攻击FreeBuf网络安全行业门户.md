## 概述

 **2019年09月10日，
华为AntiDDoS8000设备某荷兰数据中心局点捕获新型UDP反射放大攻击，反射源端口为1194。客户在AntiDDoS8000清洗设备上配置硬件过滤规则有效阻断了攻击。华为未然实验室通过对攻击流量深入分析，很快发现攻击流量来自在网络中开放的OpenVPN服务。**

OpenVPN是一个用于创建虚拟专用网络加密通道的软件包，最早由James
Yonan编写。OpenVPN允许创建的VPN使用公开密钥、电子证书、或者用户名／密码来进行身份验证。

## 攻击原理

OpenVPN支持UDP、TCP两种隧道模式，默认使用UDP，在认证模式上支持Pre-sharedstatic key 和 TLS
两个模式，默认为TLS模式。

![屏幕快照 2019-09-23
下午11.33.02.png](https://image.3001.net/images/20190924/1569315993_5d89dc991e49b.png!small)

图1 TLS mode OpenVPN状态图（数据来源见参考资料1）  

OpenVPN有Data channel和Control channel两个通道，在UDP隧道模式下，Data
channel的可靠性需要业务层自己维护，Control
channel的可靠性则需要OpenVPN自己来维护，这也是问题的关键所在。通过分析OpenVPN可靠性实现代码，可以发现当OpenVPN发送出数据包后，若在超时时间内没有收到对应的确认包，则会进行多次数据重传，直到socket超时（默认30s）。超时时间计算逻辑有两种方式（见图2），一种是指数增长方式（默认配置），另一种是固定值（默认2秒）的方式。

![屏幕快照 2019-09-23
下午11.32.37.png](https://image.3001.net/images/20190924/1569315994_5d89dc9a79cef.png!small)图2
OpenVPN源码

## 攻击模拟

根据图1所示，我们让客户端向服务器发送P_ _CONTROL__ HARD_ _RESET__ CLIENT_ _V2_ _数据包，服务器则会响应_
_P__ CONTROL_ _HARD__ RESET_ _SERVER__ V2数据包，客户端对服务器响应的数据包不做P_ACK_V1应答，服务器便会对
_P__ CONTROL_ _HARD__ RESET_ _SERVER__ V2数据包进行多次重传。

以下是P_ _CONTROL__ HARD_ _RESET__ CLIENT_ _V2_ 数据包字符串的十六进制格式：

"\x38\x11\xad\x18\x24\xa7\x8a\xad\x41\x00\x00\x00\x01\x5d\x85\x8a"\

"\x31\x65\xc3\x17\xa6\xe9\x35\x8b\x51\xcf\xfb\x6c\xa5\x1b\xc4\x08"\

"\x90\x43\xa1\x6a\xa7\xa1\x20\xc8\x69\x37\x85\x60\xe3\x44\xa6\x4c"\

"\x33\x3f\xdc\x86\xd5\x29"

![屏幕快照 2019-09-23
下午6.47.18.jpg](https://image.3001.net/images/20190924/1569315993_5d89dc9961d1e.jpg!small)图3
默认配置“指数增加超时时间”下OpenVPN服务遭受攻击时数据抓包  

![屏幕快照 2019-09-23
下午11.51.13.jpg](https://image.3001.net/images/20190924/1569316001_5d89dca17781c.jpg!small)

图4 “固定超时时间”配置下OpenVPN服务遭受攻击时数据抓包  

根据图3、图4可见，服务器对未及时应答的数据包，会进行多次重传。根据该特性，结合UDP反射攻击手法，即可实现UDP反射放大攻击。为了更高效的利用反射源，客户端需要将每次请求的源端口设置为不一样，如果是同一个源端口，在30秒有效期内，将被忽略。

## 放大倍数

### 指数增加超时时间方式

如图3所示，客户端发送一个96字节的一个报文，服务器将在30秒内响应大小与请求包相当的5个数据包，所以放大倍数应该是 5 / 1 = **5**
倍，同时流量的PPS也放大了 **5** 倍。

### 固定超时时间方式

如图4所示，客户端发送一个96字节的一个报文，服务器将在后续的30秒内，以0.5秒的间隔响应一个大小为与请求包相当的数据包，所以放大倍数应该是 30 /
0.5 = **60** 倍，同时流量的PPS也放大了 **60** 倍。

## 攻击风险

通过shodan网络空间搜索引擎查询，可以发现在网络空间有将近70万个对外开放的OpenVPN服务。如果攻击者利用这些OpenVPN服务进行UDP反射放大攻击，将会对被攻击者造成严重影响。

![屏幕快照 2019-09-23
下午7.06.55.png](https://image.3001.net/images/20190924/1569316011_5d89dcabf0d20.png!small)
图5 网络空间1194端口统计图（数据来源shodan）

## 防范建议

> 1、在大带宽的数据中心场景， 可以在专业Anti-DDoS设备或者边界路由上配置过滤规则(protocol udp, source port 1194,
> packetlength >= 56 Bytes)
>
> 2、小带宽的企业数据中心当遭遇这种攻击时会引发链路带宽拥塞，只能靠上游云清洗过滤

## 参考资料

> [Protocol state fuzzing of
> anOpenVPN](https://www.ru.nl/publish/pages/769526/tomas_novickis.pdf)
>
> [OpenVPN](https://openvpn.net/)

 ***本文原创作者：null001，属于FreeBuf原创奖励计划，未经许可禁止转载**

