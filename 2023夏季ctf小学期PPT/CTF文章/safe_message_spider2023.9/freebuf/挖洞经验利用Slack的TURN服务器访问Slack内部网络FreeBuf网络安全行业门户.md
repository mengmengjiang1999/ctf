![Unfurl-Why-Slack.jpg](https://image.3001.net/images/20200415/1586953582_5e96fd6ed2111.jpg!small)

**该篇Writeup介绍了作者通过TURN服务器的中继作用，实现对Slack的内部网络和AWS元数据资源的访问。文中涉及到了STUN、TURN协议和WebRTC知识，还用到了一个未公开的STUN协议安全测试工具Stunner。我们一起来看看。**

## STUN和TURN介绍

在现实的互联网环境中，大多数客户端主机都位于防火墙或NAT之后，像在视频会议、视频通话、在线教育等实时传输场景下，我们都希望网络中的两台主机能够直接穿透NAT限制进行通信，即所谓的P2P通信，而不需要其他公共服务器的中转。因此，STUN和TURN协议就应运而生了。

STUN协议（Simple Traversal of UDP Through
NATs），在RFC3489中定义为一种简单的NAT穿透解决方案，即用UDP实现的简单NAT穿透方法。在新的RFC5389修订中把STUN协议定义为穿透NAT的提供工具，在原有UDP的基础增加了TCP穿透，英文全称为Session
Traversal Utilities for NAT，即NAT会话穿透。

TURN协议（Traversal Using Relays around
NAT），在RFC5766中的定义是，使用中继穿透NAT，它是STUN协议的一种中继扩展。即在STUN的基础上实现中继或“中间人”方式的NAT穿透。

## 漏洞概况

Slack部署的TURN服务器允许把客户端请求的UDP包和TCP请求，中继到Slack内部网络和架设在AWS服务上的元数据资源中。

由于TURN是STUN的一个扩展协议，它通过中继方式来连接NAT之后的对等客户端，这有点类似我们渗透测试视角下的“代理”。在TCP中继模式下，TURN使用了RFC
6062规范中提到的[0x000A消息连接方法](https://tools.ietf.org/html/rfc6062#section-4.3)；而在UDP中继模式下，TURN则使用了RFC
5766规范中[提到的0x006消息指示方法](https://tools.ietf.org/html/rfc5766#section-10)，和另外具有
[同样功能的channel方法](https://tools.ietf.org/html/rfc5766#section-11)。

这里，可能有人会有疑问，那么，这和WebRTC又有啥关系呢？

### WebRTC应用中的TURN实现

WebRTC（Web Real-Time
Communication），即网页实时通信，它实现了基于网页的语音对话或视频通话，目的是无插件实现web端的实时通信的能力，Web开发者也无需关注多媒体的数字信号处理过程，只需编写简单的Javascript程序即可实现。WebRTC提供了视频会议的核心技术，包括音视频的采集、编解码、网络传输、显示等功能，并且还支持跨平台：windows，linux，mac，android。

通常，基于NAT的限制条件下，在WebRTC和VoIP应用中，棘手的问题是如何让通信双方或多方的媒体流信息能互相流通，因此，STUN的出现在很大程度上解决了这一问题，且TURN的扩展使用也弥补了相应的不足。之后，交互式连接（Interactive
Connectivity
Establishment，ICE）机制更让STUN和TURN的应用更加完美，它通过综合运用STUN、TURN、RSIP等NAT穿透方式，优化性能，以弥补单独使用其中任何一种方法所带来的固有缺陷。其实也可以说，ICE机制是绑定TURN来使用的。

因此，对大多WebRTC系统来说，一个关键因素是当防火墙或NAT设备不允许对等实体之间进行直接的媒体流量通信交互时，那么就需要有一个TURN服务器在对等实体之间来中继消息。

## Slack部署的TURN服务

在我们测试Slack应用时发现，TURN被用来基于安全实时传输协议（Secure Real-time Transport
Protocol，SRTP）建立媒体流通信，Slack的这种TURN用法在Yoshimasa Iwase的文章[《Is Slack’s WebRTC
Really Slacking?》](https://webrtchacks.com/slack-webrtc-slacking/)中有过详细阐述，在此就不作深入讨论。但这里要强调的一点是，相对于解决媒体通信，TURN服务器被部署在Slack架构中的关键位置却是我们更关心的。

## 测试Slack的TURN服务器时发现的问题

经过测试我们发现，利用Slack的TURN服务器，客户端的TCP/UDP流量不仅可以中继到其TURN服务器本身，还能中继到Slack架设在AWS上的内部地址。这对于Web应用类型的渗透测试来说有些熟悉，因为这可能成为SSRF（服务端请求伪造）的利用方式
。然而，与常规SSRF漏洞不同之处在于，这里可以利用（或滥用）的不仅局限于HTTP协议，可能还涉及到一种开放式代理，比如socks
proxy或基于CONNECT方法的web proxy。

那利用Slack的这种TURN服务器问题，可以实现哪些安全测试目的呢？

1、可以连接到AWS的元数据服务端<http://169.254.169.254>获取一些临时的身份识别和访问管理凭据，如下图；

2、可以连接到Slack本地主机探测一些未曝露在互联网上的开放端口，如node exporter的系统监测服务，22, 25, 53, 443, 515,
5666, 8500, 8888, 9090或9100端口等；

3、在Slack 的AWS架构-10.41.0.0/16 中进行端口扫描，发现一些服务器管理应用，然而进一步利用这些“可信”服务。

![01.png](https://image.3001.net/images/20200415/1586954971_5e9702db1e3cd.png!small)至此，有些人可能会觉得Slack的TURN服务器貌似没有做任何身份验证或授权限制，但其实Slack是做了身份验证的。而且，每当客户端有WebRTC会话请求过来时，Slack的TURN服务器都会为其生成一个临时凭据，作为攻击者来说，要深入利用必须获取到这些凭据信息。因此，我们采取了以下步骤来进行尝试：

1、把我们的浏览器设置成Burp代理模式；

2、在Burp中的 Proxy > HTTP history 按键下，过滤Slack的桌面协作应用关键字screenhero；

3、在Slack中点Call发起一个通话；

4、Slack的TURN服务器发起对/api/screenhero.rooms.create的请求，响应消息中包含了临时的用户名密码信息，以及TURN主机名和端口；

5、我们编写了一个内部测试工具Stunner对这些信息进行了利用，最终形成了一个有效的漏洞。

![02.png](https://image.3001.net/images/20200415/1586955033_5e970319cc387.png!small)

Stunner就是一个STUN协议的测试工具，当然也能检测一些TURN下的不同协议漏洞。其中有意思的一个子命令就是TURN对等端扫描，它针对特定的对等端主机，通过TURN中继进行端口扫描。下列视频中我们用到了turn
peer
httpproxy命令，它能通过让Web浏览器配置成HTTP代理模式与Stunner工作，由于Stunner会把HTTP请求和响应代理到Slack的TURN服务器，这样Stunner和TURN服务器之间就形成了一个HTTP流量交互。

## 演示视频

视频展示了以下几个方面：

> 获取TURN服务器为客户端生成的凭据；
>
> 利用我们自己的IP地址测试TURN服务器到互联网端的中继；
>
> 连接到Slack的内部网络和架设在AWS上的元数据服务。

## 漏洞修复

修复该漏洞，可以在TURN服务器中设置访问控制规则，去阻止一些内部非公开地址在TURN消息中被指定为对端地址XOR-PEER-ADDRESS。实际环境中，包括Slack在内的大多系统都用到了集成STUN/TURN/ICE 协议且支持 P2P
穿透防火墙的Coturn应用，因此，我们建议实施以下规则：

    
    
    no-multicast-peers
    
    denied-peer-ip=0.0.0.0-0.255.255.255
    
    denied-peer-ip=10.0.0.0-10.255.255.255
    
    denied-peer-ip=100.64.0.0-100.127.255.255
    
    denied-peer-ip=127.0.0.0-127.255.255.255
    
    denied-peer-ip=169.254.0.0-169.254.255.255
    
    denied-peer-ip=127.0.0.0-127.255.255.255
    
    denied-peer-ip=172.16.0.0-172.31.255.255
    
    denied-peer-ip=192.0.0.0-192.0.0.255
    
    denied-peer-ip=192.0.2.0-192.0.2.255
    
    denied-peer-ip=192.88.99.0-192.88.99.255
    
    denied-peer-ip=192.168.0.0-192.168.255.255
    
    denied-peer-ip=198.18.0.0-198.19.255.255
    
    denied-peer-ip=198.51.100.0-198.51.100.255
    
    denied-peer-ip=203.0.113.0-203.0.113.255
    
    denied-peer-ip=240.0.0.0-255.255.255.255

## 漏洞上报和处理进程

> 2017.11 把TURN滥用方式加入到了我们的内部测试工具Stunner中
>
> 2017.12 在某邀请测试中发现了TURN漏洞
>
> 2018.2 对Slack进行了测试且发现了其漏洞
>
> 2018.4 向Slack上报漏洞，并帮助其在不同场景下复现了漏洞
>
> 2018.5 Slack向现用的服务器打补丁
>
> 2010.1 征求Slack漏洞公开意见
>
> 2020.3 公布漏洞，更多详情参考[HackerOne](https://hackerone.com/reports/333419)

PS: 我们在视频语音服务的测试中都用到了Stunner工具，但现阶段我们暂不打算开源该工具。

 ***参考来源：[rtcsec](https://www.rtcsec.com/2020/04/01-slack-webrtc-turn-compromise/)，clouds 编译整理，转载请注明来自 FreeBuf.COM**  

