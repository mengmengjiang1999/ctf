阿里云安全近期发现利用STUN（Session Traversal Utilities for
NAT，NAT会话穿越应用程序）服务发起的DDoS反射攻击。阿里云DDoS防护系统在秒级识别到攻击，实时对攻击流量做了清洗，保护客户业务不受DDoS攻击影响。

## 背景概述

STUN（Session Traversal Utilities for
NAT，NAT会话穿越应用程序）是一种网络协议，目前定义了三种STUN用途：Interactive Connectivity
Establishment（ICE）[MMUSIC-ICE]，交互式连接建立、Client-initiated connections for SIP
[SIP-OUTBOUND]，用于SIP的客户端初始化连接、NAT Behavior Discovery [BEHAVE-NAT]，NAT行为发现。该协议由RFC 5389定义。

STUN支持使用UDP协议来发送，STUN请求/响应事务的可靠性是通过客户端应用程序本身重新传输请求消息来实现的。黑客利用UDP无状态的这种机制，伪造攻击目标请求STUN服务器，把开启该服务的主机作为反射源，进行DDoS反射攻击，实现伪装和攻击。

## 攻击方式分析

### 攻击包分析

STUN的UDP端口默认使用3478端口，如下图所示：  
![image](https://image.3001.net/images/20210526/1622009851_60ade7fbcaaf9db5755fd.png!small)![image](https://image.3001.net/images/20210526/1622009664_60ade740d51084071479a.png!small)

利用了STUN服务(其中software取决于服务器部署的软件名称及版本)的反射攻击载荷的示意图如下：  
![image](https://image.3001.net/images/20210526/1622009680_60ade75039751a13be3d9.png!small)  
![image](https://image.3001.net/images/20210526/1622009694_60ade75ed04e169ca950b.png!small)

### STUN协议分析

STUN是一种Client/Server的协议，也是一种Request/Response的协议，默认端口号是3478，支持UDP和TCP。  
STUN-UDP协议通信过程，发送一个Request，服务器处理验证，返回一个Response，response常见返回值MAPPED-ADDRESS(表示客户端地址)，RESPONSE-ORIGIN(表示响应的地址端口)，SOFTWARE(软件名称及版本)，FINGERPRINT(指纹扩展)，响应长度依赖于不同版本的STUN。详情参见RFC5389（https://www.rfc-editor.org/rfc/rfc5389.html）。

### 攻击模拟复现

模拟发送Binding Request请求，响应Binding Response报文：  
![image](https://image.3001.net/images/20210526/1622009709_60ade76d9a1ca9a543b7b.png!small)

模拟攻击返回的响应载荷与攻击载荷一致，复现完成：  
![image](https://image.3001.net/images/20210526/1622009722_60ade77a915a70bd996fa.png!small)

模拟发送20字节的Binding Request/数据帧62字节，获取到的响应载荷为124字节/数据帧166字节，放大倍数166/62=2.67倍。  
![image](https://image.3001.net/images/20210526/1622009736_60ade7884b975e7b5974f.png!small)

STUN服务器Softwafre的名称及版本不同，服务器IP长度不同，均会影响Response的长度，目前观察到的最大响应载荷为156字节/数据帧198字节，放大倍数198/62=3.19倍。  
![image](https://image.3001.net/images/20210526/1622009751_60ade7976317776e561a1.png!small)

Software版本示例如下：  
 Software: Coturn-4.5.1.3 'dan Eider'  
 Software: Amity-systems.com 0.96  
 Software: restund v.E5.1.140.1273 ( - / win32 )  
 Software: zt v0.4.13 (x86_64/linux)  
 Software: TANDBERG/4137 (X12.5.9)  
 Software: Citrix-3.2.3.8 'Marshal West'  
发送错误的Request到服务器，返回校验错误的response时，可以放大更大倍数，194/63.0=3.07倍，可以造成更明显的放大效果。  
![image](https://image.3001.net/images/20210526/1622009762_60ade7a2f1edc98dd5b67.png!small)  
![image](https://image.3001.net/images/20210526/1622009775_60ade7af2270a94f522da.png!small)

目前观察到的攻击反射源以海外地区为主，在zoomeye中查询3478开放端口IP数量级23万+，说明STUN服务可利用的IP量级还是比较大。STUN协议本身协议设计上已经优化过，response虽然会比request要大，但不会放大很多倍请求，利用成本会很高。对比其他常见反射攻击的反射倍数，STUN的反射倍数并不理想，但是作为新型的反射类型，市面上DDoS防护系统不一定能全部覆盖防御该攻击方式，反而可能攻击效果更佳。

## 防护建议

对于STUN互联网应用提供者，可限制可访问的源IP的地址范围减少利用情况，或者使用tcp发送STUN协议，对于企业用户，推荐接入DDoS防护产品对抗大流量DDoS攻击。

## 参考

https://www.rfc-editor.org/rfc/rfc5389.html  
https://www.zoomeye.org/

