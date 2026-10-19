![](https://image.3001.net/images/20191017/1571323065_5da87cb9e32a2.png!small)

##  工具概述

> 工具当前版本：v1.12.0
>
> Python环境：支持Python v3.5+

 **EAPHammer可以针对WPA2-Enterprise企业网络执行Evil
Twin攻击测试，广大研究人员可以将其用于全范围的无线网络安全评估以及红队安全研究。因此，该工具提供了一个易于使用的用户界面，研究人员可以利用这个界面以最少的手动配置交互执行功能强大的无线渗透测试。**

![](https://image.3001.net/images/20191017/1571323082_5da87ccac877e.png!small)

##  快速开始指引（Kali）

首先，使用下列命令将EAPHammer源码从该项目的GitHub库克隆至本地：

    
    
    git clone https://github.com/s0lst1c3/eaphammer.git

接下来，运行kali-setup文件来完成EAPHammer的安装过程，下面的命令将会自动完成依赖组件的安装以及项目源码的编译：

    
    
    ./kali-setup

完成项目安装后，我们就可以使用下列命令来对一个WPA/2-EAP网络执行Evil Twin凭证窃取攻击测试了：

生成证书

    
    
    ./eaphammer --cert-wizard

发动攻击

    
    
    ./eaphammer -i wlan0 --channel 4 --auth wpa-eap --essid CorpWifi --creds

##  功能介绍

> 1、从WPA-EAP以及WPA2-EAP网络中窃取RADIUS凭证。
>
> 2、针对恶意网站发动攻击，窃取广告凭证。
>
> 3、执行门户网站攻击。
>
> 4、集成了内置响应程序。
>
> 5、支持开放网络和WPA-EAP/WPA2-EAP。
>
> 6、大多数攻击均可自动完成。
>
> 7、安装过程无需手动配置。
>
> 8、使用了最新版本的hostapd(2.8)。
>
> 9、支持Evil Twin和Karma攻击。
>
> 10、生成PowerShell攻击Payload。
>
> 11、针对恶意门户网站攻击，集成了HTTP服务器。
>
> 12、支持SSID隐藏。
>
> 13、支持使用hcxtools对PSK网络执行自动PMKID攻击。
>
> 14、可针对单个ESSID执行爆破攻击。

##  工具支持的EAP方法

###  当前版本的EAPHammer支持下列EAP方法：

> EAP-PEAP/MSCHAPv2
>
> EAP-PEAP/GTC
>
> EAP-PEAP/MD5
>
> EAP-TTLS/PAP
>
> EAP-TTLS/MSCHAP
>
> EAP-TTLS/MSCHAPv2
>
> EAP-TTLS/MSCHAPv2 (no EAP)
>
> EAP-TTLS/CHAP
>
> EAP-TTLS/MD5
>
> EAP-TTLS/GTC
>
> EAP-MD5

##  OWE

> EAPHammer目前支持针对OWE以及OWE-Transition模式的网络执行流氓AP攻击。

##  PMF

> EAPHammer目前支持802.11w、Loud Karma攻击以及Known Beacon攻击。

##  GTC降级攻击

> EAPHammer可以自动尝试针对已连接的客户端执行GTC降级攻击，并尝试捕捉明文凭证。
>
>
> 攻击演示：【[油管](https://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=-uqTqJwTFyU&feature=youtu.be&t=22m34s)】

##  项目地址

> EAPHammer：【[GitHub传送门](https://github.com/s0lst1c3/eaphammer)】

###  许可证协议

> 本项目遵循[GNU Public License
> v3.0](https://github.com/s0lst1c3/eaphammer/blob/master/LICENSE.md)开源许可证协议。

***参考来源：[s0lst1c3](https://github.com/s0lst1c3/eaphammer)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

