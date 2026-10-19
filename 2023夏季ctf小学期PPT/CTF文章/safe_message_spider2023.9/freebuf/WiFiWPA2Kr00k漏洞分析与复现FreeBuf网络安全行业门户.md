##  一、研究背景

 **在今年2月份的RSA大会上，ESET的研究人员公开披露Wi-Fi芯片存在严重安全漏洞CVE-2019-15126，并将其命名为“Kr00k”。攻击者可以利用“Kr00k”解密无线网络流量，获取传输过程中的敏感数据。**

Kr00k漏洞影响部分安装Broadcom和CypressWi-Fi芯片的设备，这两家芯片产品被广泛应用于手机、平板电脑及IOT设备中。保守估计，全球总计超过10亿的设备受该漏洞的影响。

##  二、漏洞分析

###  2.1 漏洞原理

在介绍Kr00k漏洞之前，先简单了解下WPA2协议。目前基于AES-CCMP的WPA2协议是Wi-Fi网络中最普遍的标准。下图是客户端（Station,
STA）连接接入点（Access Point, AP）的消息交互过程。

![](https://image.3001.net/images/20200410/1586502081_5e9019c1c1d95.png!small)

STA和AP在四次握手中，协商会话密钥PTK（Pairwise Transient
Key），PTK是由PMK和PKE计算生成，而PMK由ANonce、SNonce和双方MAC地址等计算生成。PTK分为KCK、KEK和TK三部分，其中，KCK用于MIC校验，KEK用于加密GTK，TK为数据加密密钥。四次握手完成后，传输数据使用TK进行加密。

![](https://image.3001.net/images/20200410/1586502137_5e9019f9ce5c9.png!small)

在WPA2协议中，解除关联操作可以由未经身份验证和未加密的管理帧触发，Kr00k漏洞与解除关联操作密切相关。在下图所示中，当站点的连接会话解除关联后，保存在Wi-Fi芯片中的会话密钥(TK)被置零，如果使用已置零的TK密钥对芯片缓存中的数据进行加密并传输，将导致漏洞产生。

![](https://image.3001.net/images/20200410/1586502157_5e901a0da2a19.png!small)

攻击者利用无线网卡即可完成入侵，通过不断触发解除关联、重新关联，然后使用全零TK对捕获的数据帧进行解密，从而获取敏感信息。

###  2.2固件分析

本文选取Nexus5中的BCM4339芯片固件进行分析。首先，定位固件中计算ptk的位置，如下图所示。

![](https://image.3001.net/images/20200410/1586502198_5e901a36063ae.png!small)

然后，对其上层函数wlc_wpa_sup_eapol进行分析。

![](https://image.3001.net/images/20200410/1586502230_5e901a56bd5cf.png!small)![](https://image.3001.net/images/20200410/1586502259_5e901a7332881.png!small)

wlc_wpa_sup_eapol调用wpa_pmk_to_ptk时，传入的参数分别为mac1、mac2、Nonce1、Nonce2、pmk、pmk_len、ptk、ptk_len。
ptk计算结果被保存在wpa_ptk结构体偏移0x8c位置中。

wlc_sup_attach函数用于处理STA的初始化连接，该函数对wpa_ptk结构体进行内存分配和初始化，wpa_ptk结构体大小为0x13C。

![](https://image.3001.net/images/20200410/1586502286_5e901a8e0435e.png!small)

当初始化失败、连接超时或解除连接的时候，则会调用wlc_sup_detach函数对wpa_ptk结构体进行置零操作。

![](https://image.3001.net/images/20200410/1586502324_5e901ab4b56b9.png!small)![](https://image.3001.net/images/20200410/1586502361_5e901ad97bfbc.png!small)![](https://image.3001.net/images/20200410/1586502408_5e901b08782a8.png!small)

##  三、漏洞验证

###  3.1 测试环境

|  设备名称  |  数量  
---|---|---  
受影响的设备  |  Nexus5  |  1  
iphone6s手机  |  1  |  
Attacker  |  NETGEAR网卡  |  2  
  
###  3.2 测试步骤

> （1）对wireshark解密数据包的相关功能进行patch，使其能够成功解密全零TK加密的数据。
>
> （2）使用patch后的wireshark监听目标设备和AP通信的数据包。
>
> （3）使用目标设备连接AP并任意访问网页。
>
> （4）对AP和测试目标发送Disassocation包。
>
> （5）重复执行步骤（3）和（4），观察wireshark中数据包是否解密。

###  3.3测试结果

Nexus 5:

![](https://image.3001.net/images/20200410/1586502526_5e901b7e1e8d0.png!small)

iphone 6s:

![](https://image.3001.net/images/20200410/1586502559_5e901b9fe6287.png!small)

可以看出，Nexus 5和iphone 6s部分数据被成功解密。

##  四、影响范围

目前已知受影响的设备有：

> Amazon Echo 2nd gen
>
> Amazon Kindle 8th gen
>
> Apple iPad mini 2
>
> Apple iPhone 6, 6S, 8, XR
>
> Apple MacBook Air Retina 13-inch 2018
>
> Google Nexus 5
>
> Google Nexus 6
>
> Google Nexus 6P
>
> Raspberry Pi 3
>
> Samsung Galaxy S4 GT-I9505
>
> Samsung Galaxy S8
>
> Xiaomi Redmi 3S
>
> Asus RT-N12
>
> Huawei B612S-25d
>
> Huawei EchoLife HG8245H
>
> Huawei E5577Cs-321

##  五、安全建议

设备制造商已发布的安全建议如下：

> <https://support.apple.com/en-us/HT210721>
>
> <https://support.apple.com/en-us/HT210722>
>
> <https://support.apple.com/en-us/HT210788>
>
> <https://www.arubanetworks.com/assets/alert/ARUBA-PSA-2020-003.txt>
>
>
> <https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-> sa-20200226-wi-fi-info-disclosure>
>
> <https://www.huawei.com/en/psirt/security-notices/huawei-> sn-20200228-01-kr00k-en>
>
> <https://www.microchip.com/design-centers/wireless-connectivity/embedded-wi-> fi/kr00k-vulnerability>
>
> <https://www.mist.com/documentation/mist-security-advisory-kr00k-attack-> faq/>
>
> <https://www.zebra.com/us/en/support-downloads/lifeguard-> security/kr00k-vulnerability.html>

***本文作者：ADLab，转载请注明来自FreeBuf.COM**

