![微信公众号-青莲晚报封面图-55.jpg](https://image.3001.net/images/20190814/1565775214_5d53d56e773c2.jpg!small)  

**CVE-2018-1158 MikroTik RouterOS漏洞分析之发现CVE-2019-13955**

 **  
**

CVE-2018-1158是MikroTik路由器中存在的一个堆栈耗尽漏洞。认证的用户通过构造并发送一个特殊的json消息，处理程序在解析该json消息时会出现递归调用，造成堆栈耗尽，导致对应的服务崩溃重启。

该漏洞由Tenable的Jacob
Baines发现，同时提供了对应的PoC脚本。另外，他的关于RouterOS漏洞挖掘的议题“RouterOS中的虫虫狩猎”非常不错，对MikroTik路由器中使用的一些自定义消息格式进行了细致介绍，同时还提供了很多工具来辅助分析。相关工具，议题以及的PoC脚本可在混帐库RouterOS的获取，强烈推荐给对的MikroTik设备感兴趣的人。

下面利用已有的PoC脚本和搭建的MikroTik RouterOS仿真环境，对该漏洞的形成原因进行分析。

详文阅读：

<https://www.anquanke.com/post/id/183451>

  

 **分析Belkin SURF路由器中的多个漏洞**

  

我们将分析由Josep Pi Rodriguez以及Pedro Guillén
Núñez在该平台上发现的十多个漏洞。虽然Belkin已确认我们的报告，但表示该产品已经停产，不再提供支持服务。这些漏洞会影响Belkin
SuperTask!
RTOS，特别是其中的UPnP功能。这些漏洞包括多个基于栈的缓冲区溢出问题，涉及AddPortMapping、GetSpecificPortMappingEntry、DeletePortMapping
SOAP接口以及upgrade.exe、dnsproxy、dhcpd中的缓冲区溢出问题。

研究人员最开始通过分析Belkin N150（Model F9K1001）以及Belkin N300（Model
F9K1002）固件发现这些问题，我们也在Belkin N300（Model F7D2301v1）路由器上验证了这些漏洞报告。

UPnP（Universal Plug and
Play，通用即插即用）是为了简化一般用户的网络配置过程而提出的一种协议，方便各组件“正常工作”，该协议允许本地客户端配置路由器。然而，这个过程的前提是假设所有本地客户端都是可信的单元，但恶意软件可以轻松利用该功能，在启用UPnP的路由器上打洞穿透防火墙。因此UPnP通常被认为是不安全协议，包括FBI在内的各单位都建议用户禁用并不再使用该功能。

研究人员发现路由器UPnP功能的WANPPPConnection:1Service中存在多个栈缓冲区溢出漏洞。当路由器处理AddPortMapping
SOAP请求时，会调用strcpy()将攻击者可控的NewRemoteHost参数拷贝至大小固定为0x20字节的栈缓冲区中，同时没有去验证参数的大小。

详文阅读：

<https://www.anquanke.com/post/id/183326>

  

 **黑客可能会利用新漏洞破解WiFi密码，你家的WiFi 还好吗？**

 **  
**

据外媒报道，网络安全专家在WPA3WiFi安全标准中再次发现两个严重漏洞，可能会帮助攻击者破解WiFi密码。

据了解，WPA全称为WiFi访问保护（WiFi Protected
Access），是一种WiFi安全标准，旨在通过使用高级加密标准（AdvancedEncryption
Standard）协议对无线设备进行身份验证，以防止黑客窃取用户的无线数据。而WPA3协议是在一年前刚推出的新版本标准。

然而，在WAP3协议推出后不久，研究人就察觉到该协议存在漏洞。尽管WiFi联盟已经发布了相关补丁并提供了安全建议，但这些补救措施不仅没有起作用，反而带来了两个新的漏洞。

第一个漏洞被标记为CVE-2019-13377。该漏洞允许黑客针对WPA3的Dragonfly握手（handshake）进行旁路攻击。这个旁路泄漏错误位于Dragonfly的密码编码算法中。研究人员表示，黑客可能会借机使用暴力攻击（brute-force attack）攻击破解密码。

第二个漏洞（CVE-2019-13456）是一个存在于FreeRADIUS中的信息泄漏错误。据了解，FreeRADIUS是一种被广泛使用的开源RADIUS服务器，多被用做验证远程用户的中央数据库。专家声称，攻击者可以通过发起数次EAP-pwd握手来窃取信息，然后通过执行字典攻击（dictionary attack）和蛮力攻击来重置用户的WiFi密码。

据悉，研究人员已经与WiFi联盟分享了这两个漏洞的信息，相信不久之后就会出现相应的解决方案。

详文阅读：

[http://www.yidianzixun.com/article/0MqGnioo?s=yunos&appid=s3rd_yunos](http://www.yidianzixun.com/article/0MqGnioo?s=yunos&appid=s3rd_yunos)

  

 **当心！你家的摄像头可能正在直播你的语音聊天**  

  

几位研究人员近日发现一款家用摄像头存在明显漏洞，用户通话可能会被黑客监听。

据外媒报道，几名研究人员发现一款名为AmcrestIP2M-841B
IP的家庭安全摄像头存在漏洞。该漏洞被标记为CVE-2019-3948，存在于某中国供应商提供的OEM代码中。  

据了解，CVE-2019-3948允许黑客在未经身份验证的情况下通过网络远程监听摄像头录下的音频。和与许多支持Wi-Fi的该厂商设备一样，这款摄像头可以通过TCP端口37777提供s

除此之外，研究人员还发现该款摄像头在组件HTTP端点中公开了一个名为“/videotalk”的文件，使得任何可以解码DHAV格式的黑客都能在未经身份验证的情况下发出HTTP请求，并收听摄像头的音频。

详文阅读：

<http://bbs.mzsky.cc/thread-2267580-1.html>

 **  
**

 **这款 MOD 能将特斯拉 Model S 变成移动的监控设备**

  

为了能够让自动驾驶汽车根据路况做出自主决策，开发团队往往需要为其装备复杂的计算机大脑和丰富的传感器。上周末在拉斯维加斯举办的Defcon
27黑客大会上，安全研究人员Truman Kain通过研制的MOD将特斯拉Model S转换成为移动的监控设备。

这款MOD的组成基本上就是一台NVIDIA Jetson Xavier迷你电脑，通过汽车的USB端口进行连接，能够收集汽车周围看到的所有东西。利用Model
S现有的Autopilot和哨兵模式（Sentry Mode），以及开源框架该MOD能够识别车辆型号，甚至能够收集和记录车牌信息。

或许很多人认为这个MOD并没有太大的杀伤力，不过安全研究专家Kain并不这么认为，他在Defcon 27黑客大会上现场演示了已经改装好的Model
S，不仅能够识别车辆型号，识别重复出现的目标，标记看到对方所在的位置，从而了解更多有关车主的相关信息。

详文阅读：

<http://hackernews.cc/archives/26916>

  

