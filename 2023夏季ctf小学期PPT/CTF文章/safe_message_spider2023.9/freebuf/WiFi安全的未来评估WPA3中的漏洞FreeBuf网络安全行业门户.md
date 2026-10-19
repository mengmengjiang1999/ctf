***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **近期，安全研究专家Matty Vanhoef和Eyal Ronen对WPA3 Wi-Fi标准进行了一次安全分析研究，并成功从中发现了五个安全漏洞。其中，有四个安全漏洞会严重影响互联网安全，那么接下来我们一起看看研究人员到底发现了什么。**

![1.jpg](https://image.3001.net/images/20190727/1564213636_5d3c01843d64b.jpg!small)

## WPA3

WPA3，全称为Wi-Fi ProtectedAccess 3，它是[Wi-Fi联盟组织](https://www.wi-fi.org/)发布的最新一代Wi-Fi安全加密协议。WPA3基于已成熟的[WPA2](https://www.hackread.com/vulnerability-in-wpa2-protocol-allows-attackers-intercept-decrypt-encrypted-data-traffic/)基础上实现，并在2018年底大规模投入使用，当时的WPA3还曾被誉为是“最前沿的安全协议”。

WPA3增加了一系列旨在简化[WiFi安全实施](https://www.hackread.com/security-risks-round-up-of-public-wi-fi-networks/)的新功能，其中包括安全性更加强大的身份验证机制、加密强度以及更具弹性的网络。新标准保留了与WPA2设备的互操作性，也就是向下兼容做得很到位。尽管WPA3目前是可选协议项，但它最终将会成为市场上强制采用的安全加密标准。

![2.jpg](https://image.3001.net/images/20190727/1564213646_5d3c018e27426.jpg!small)

虽然WPA3旨在为个人和企业用户提供更强大的隐私和安全保护性，但研究人员仍然从中[发现](https://www.top10vpn.com/news/privacy/researchers-uncover-vulnerabilities-in-wpa3-security-standard/)了多个严重的安全漏洞。

## WPA3被曝安全缺陷

目前，研究人员已经在安全报告中[详细介绍](https://wpa3.mathyvanhoef.com/)了一系列侧信道攻击以及降级攻击，而这些攻击向量将允许攻击者入侵采用了WPA3加密标准的Wi-Fi网络。在研究报告中，安全人员将这一系列漏洞命名为了“[Dragonfly](https://www.hackread.com/hackers-have-reportedly-infiltrated-the-us-power-grids/)”。

### Wi-Fi联盟组织在其[公告](https://www.wi-fi.org/news-events/newsroom/wi-fi-alliance-security-update-april-2019)中声称：

>
> “WPA3-Personal协议目前仍处于开发部署的前期阶段，因此只有少部分制造商会受到影响，但我们也已经提供了相应的补丁来解决这些问题。[…]这些安全问题都可以通过软件更新来缓解，而且不会对设备的协同工作能力产生任何的影响。目前，还没有任何证据可以表明已有攻击者在利用这些漏洞实施攻击。”

其实在披露这些漏洞之前，研究人员Vanhoef和Ronen就已经在跟Wi-Fi联盟沟通和合作了，并且在WP3完全部署之前解决/缓解了已发现的问题。

## 研究人员发现了什么？

据推测，破解使用了WPA3的给定网络的密码几乎是不可能的。然而，安全研究人员Mathy Vanhoef和Eyal
Ronen发现，即使是采用了WPA3，在信号范围内的攻击者仍然可以破解目标网络的密码，并读取经过了WPA3安全加密的信息。

研究人员将这些漏洞分成了两类，即WPA3设备上的Dragonfly握手漏洞以及降级攻击漏洞。研究人员表示，攻击者可以利用这些漏洞来恢复目标Wi-Fi网络的密码，发动攻击消耗目标设备资源，并迫使设备使用较弱的安全组。如果没有对HTTPS采用额外的保护，攻击者甚至可以窃取到用户的敏感信息，例如信用卡卡号、密码、聊天信息和电子邮件信息等等。

实际上，其他要求用户名和密码作为访问控制机制的设备同样有可能存在Dragonfly握手漏洞，也就是那些使用了EAP-pwd协议的设备。这也就意味着，攻击者可以利用相同的漏洞来入侵其他相关的网络，而且完全不要考虑认证机制的干扰。

Vanhoef和Ronen还在大多数实现了EAP-pwd的产品中发现了多个严重漏洞，这些漏洞不仅可以允许攻击者伪装成其他用户，而且还可以在不使用密码的情况下访问网络。虽然EAP-pwd使用场景很少，但这些发现仍然会给许多用户带来安全风险。

![3.jpg](https://image.3001.net/images/20190727/1564213669_5d3c01a52df1f.jpg!small)

### 攻击成本

基于这些漏洞的攻击实现起来非常简单，而且成本也很低。攻击者可以使用现成的WPA破解设备来完成攻击，而且根据安全报告的描述，攻击者可以利用侧信道攻击来破解所有8个字符的小写密码，而且工具成本仅为125美元。

### 安全组降级攻击

这种漏洞利用方式需要通过Dragonfly握手来迫使目标设备使用弱安全组。一般来说，攻击设备需要发送一个提交帧，其中包括了它希望使用的安全组。如果接入点（AP）不支持这个组，它将响应一个拒绝消息，并强制客户端尝试其他组。此过程将一直持续，直到找到了双方都支持的安全组为止。

在次攻击中，攻击者可以模拟AP反复发送拒绝消息，以强制客户端选择易受攻击的安全组。

### 侧信道攻击

研究人员发现，一个AP可以根据时间或内存访问模式来显示网络密码的信息。在响应提交帧时，如果给定情况下的AP支持MODP安全组，而不是基于椭圆曲线的安全组，那么响应时间则会根据网络密码来确定。此时，攻击者就可以基于这种定时消息来执行字典攻击了：“模拟AP在处理每个密码时所需的时间，并通过数据比较来破解密码。”

![4.jpg](https://image.3001.net/images/20190727/1564213683_5d3c01b3c5aaf.jpg!small)

### 降级&字典攻击

为了帮助旧设备采用新的WPA3，开发人员还提供了一种“转换模式”。在使用此模式时，网络系统可以使用共享密码来兼容WPA3和WPA2，降级攻击利用的就是这种向下兼容性。

此时，攻击者可以搭建一个恶意网络，并迫使支持WPA3的客户端通过WAP2来建立连接。此时，攻击者就可以使用暴力破解攻击来恢复共享密码了。

值得一提的是，[三星Galaxy S10](https://www.hackread.com/new-samsung-galaxy-s10-review-features/)以及其他设备同样存在这种漏洞。

 *** 参考来源：[hackread](https://www.hackread.com/future-of-wi-fi-security-assessing-vulnerabilities-in-wpa3/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

