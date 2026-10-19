Resecurity 的研究人员最近发现了一个新的网络钓鱼即服务（PhaaS）平台 EvilProxy，该平台正在暗网中大肆宣传。在其他表述中，也有叫做
Moloch 的。该平台与此前出现的网络钓鱼工具包存在某种关联，这些工具包由针对金融机构和电子商务公司发起攻击的著名攻击者开发。

此前，针对 Twilio 的供应链攻击导致双因子验证代码泄露。而 EvilProxy 这样的平台能够大规模攻击启用双因子验证的用户，而无需侵入供应链中。

EvilProxy 尝试使用反向代理与 Cookie 注入来绕过双因子认证，以此代理受害者的会话。这种攻击方式此前在 APT
攻击中已有发现，EvilProxy 将其成功产品化。调查发现攻击者已经攻击了多位财富五百强公司的员工。

首次发现 EvilProxy 在 2022 年 5
月上旬，攻击者发布了一段演示视频（<https://player.vimeo.com/video/746020364>），介绍了针对
Apple、Facebook、GoDaddy、GitHub、Google、Dropbox、Instagram、Microsoft、Twitter、Yahoo、Yandex
等品牌的攻击。

![image.png-251.6kB](https://image.3001.net/images/20220907/1662548145_631878b1beca0176cc3b4.png!small)后台控制列表

值得注意的是，EvilProxy 还支持针对 Python 语言的官方软件存储库 Python Package Index（PyPi）的网络钓鱼攻击。

![image.png-91kB](https://image.3001.net/images/20220907/1662548146_631878b28d0832b008465.png!small)针对
PyPi 的攻击

不久前，PyPi 官方表示项目贡献者遭到了网络钓鱼攻击，最后使用了 JuiceStealer 作为 Payload 部署。根据分析调查，攻击就是与
EvilProxy 有关。

除了 PyPi，EvilProxy 还支持 GitHub 和 npmjs。攻击者希望通过钓鱼攻击切入供应链，入侵下游的软件开发人员和 IT 人员。

![image.png-100.1kB](https://image.3001.net/images/20220907/1662548147_631878b350af3ca64d280.png!small)针对
GitHub 与 npmjs 的攻击

## 反向代理

EvilProxy
利用反向代理的原理，将受害者引导至钓鱼网站，并且通过反向代理为用户提供所有合法的内容，包括登录页面等。当流量经过反向代理，攻击者就能够获取有效的会话
Cookie 并且绕过双因子认证的校验。

![image.png-121.1kB](https://image.3001.net/images/20220907/1662548148_631878b410ad89e8c5266.png!small)运作模式

Google 双因子验证示例（<https://player.vimeo.com/video/746020880>）如下所示：

![image.png-128.6kB](https://image.3001.net/images/20220907/1662548148_631878b4d2ba1f0fc817c.png!small)Google
双因子验证

微软双因子验证示例（<https://player.vimeo.com/video/746021195>）如下所示：

![image.png-153.8kB](https://image.3001.net/images/20220907/1662548149_631878b590da7cf74c250.png!small)微软双因子验证

EvilProxy 是订阅制，用户可以选择 10 日、20 日或者 31 日。由 John_Malkovich 担任管理员，在 XSS、Exploit 与
Breached 在内的主要黑客社区都有出售。

![image.png-873.8kB](https://image.3001.net/images/20220907/1662548150_631878b651b3185ba224b.png!small)论坛广告

EvilProxy 通过 Telegram 进行联系与付款。

![image.png-512kB](https://image.3001.net/images/20220907/1662548151_631878b7571ce09fd764c.png!small)订阅价格

EvilProxy 提供了使用教程与教学视频，坦率地说攻击者在易用性上做的非常优秀。

![image.png-275.5kB](https://image.3001.net/images/20220907/1662548152_631878b837da7b801ac08.png!small)官方网站

攻击者使用 Docker 容器和一组脚本进行部署，自动安装程序部署在 Gitlab 的 ksh8h297aydO 用户中。

    
    
    apt update -qqy && apt dist-upgrade --no-install-recommends --no-install-suggests -o Dpkg::options::="--force-confdef" -y \ && apt install --no-install-recommends --no-install-suggests -y git \ && rm -rf /srv/control-agent && git clone --recurse-submodules https://gitlab.com/ksh8h297ayd0/docker-control-agent.git /srv/control-agent \ && cd /srv/control-agent && chmod +x ./install.sh \ && /srv/control-agent/install.sh '[license_key]' ===*=

部署成功后，就会通过上游的两个网关转发来自受害者的流量。

![image.png-86.3kB](https://image.3001.net/images/20220907/1662548153_631878b97870d2f10a529.png!small)配置信息

例如一个模拟微软电子邮件服务的钓鱼网站地址为

>
> `https://lmo.msdnmail[.]net/common/oauth2/v2.0/authorize?client_id=4765445b-32c6-49b0-83e6-1d93765276ca&redirect_uri=https%3A%2Fopenid%20profile%20https%3
> A%2F%2Fwwwofc.msdnmail.net%2Fv2%2FOfficeHome.All&response_mode=form_post&nonce=637975588496970710
> .Zjg3YzFkMmEtYTUxYy00NDliLWEzYzAtMTExZTliNjBkY2ZkY2U3NzM2MDMtZWNhZC00ZWFmLWE5YjMtYzgzZTFjM2E1ZDdl&ui_locales=en-> US&mkt=en-US&state=jHi-> CP0Nu4oFHIxklcT1adstnCWbwJwuXQWTxNSSsw-23qiXK-6EzyYoAyNZ6rHuHwsIYSkRp99F-bqPqhN4JVCnT4-3MQIDvdTKapKarcqaMFi6_xv2__3D0KfqBQ070ykGBGlwxFQ6Mzt9CwUsz2zdgcB4jFux2BhZQwcj-> WumSBz0VQs5VePV-wz00E8rDxEXfQdlv-> AT29EwdG77AmGWinyf3yQXSZTHJyo8s-IWSHoly3Kbturwnc87sDC3uwEn6VDIjKbbaJ-c-> WOzrg&x-client-SKU=ID_NETSTANDARD2_0&x-client-ver=6.16.0.0﻿`

获取授权后的 URL 为

>
> `https://473126b6-bf9a-4a96-8111-fb04f6631ad8-571c4b21.msdnmail[.]net/mail/?realm=[victim_domain]&exsvurl=1&ll-> cc=1033&modurl=0&JitExp=1&url=%2Fowa%2F%3Frealm%253d%2526exsvurl%253d1%2526ll-> cc%253d1033%2526modurl%253d0%2526login_hint%253[victim_email]%252540[victim_domain]﻿`

![image.png-263.5kB](https://image.3001.net/images/20220907/1662548154_631878ba5281512b0edc4.png!small)模拟微软电子邮件服务的钓鱼

![image.png-222.8kB](https://image.3001.net/images/20220907/1662548155_631878bb203130313c2f8.png!small)模拟微软电子邮件服务的钓鱼

攻击者汇总了已知的 VPN 服务、代理服务与 Tor 出口节点等数据，判断潜在受害者为机器人或者研究人员，就会自动断开链接。

![image.png-204.4kB](https://image.3001.net/images/20220907/1662548156_631878bc30baf5f08986c.png!small)安全防护配置

另一种方法是基于指纹：

![image.png-221.1kB](https://image.3001.net/images/20220907/1662548157_631878bd2addc68471e03.png!small)指纹识别配置

攻击者也十分警惕虚拟机：

![image.png-432.7kB](https://image.3001.net/images/20220907/1662548158_631878be3311acb7179e4.png!small)虚拟机检测

![image.png-499kB](https://image.3001.net/images/20220907/1662548159_631878bfaf3e62a2e707e.png!small)虚拟机检测

## 总结

EvilProxy 为攻击者提供了一种低成本、可扩展的解决方案来进行钓鱼攻击，能够绕过双因子认证使用户更加不安全。

## IOC

> 147[.]78[.]47[.]250  
> 185[.]158[.]251[.]169  
> 194[.]76[.]226[.]166  
> msdnmail[.]net  
> evilproxy[.]pro  
> top-cyber[.]club  
> rproxy[.]io  
> login-live.rproxy[.]io  
> gw1.usd0182738s80[.]click:9000  
> gw2.usd0182738s80[.]click:9000  
> cpanel.evilproxy[.]pro  
> cpanel.pua75npooc4ekrkkppdglaleftn5mi2hxsunz5uuup6uxqmen4deepyd[.]onion

## 参考来源

> [Resecurity](https://resecurity.com/blog/article/evilproxy-phishing-as-a-> service-with-mfa-bypass-emerged-in-dark-web)

