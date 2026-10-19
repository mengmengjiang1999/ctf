**作者：heige@知道创宇404高级威胁情报团队  
时间：2023年6月2日**

2023年6月1日，卡巴斯基发布了一篇最新的ATP分析报告《Operation Triangulation: iOS devices targeted
with previously unknown malware》[1] 称发现了一种针对iOS的iMessage
0day漏洞攻击，“远程无感”的那种，随即同一天俄罗斯联邦安全局发布公告，翻译如下图：

![图片](https://images.seebug.org/content/images/2023/06/06/1686036165000-1nbgfy.png-w331s)

虽然这篇公告没有直接表明就是同一件事情，那么我们看到俄罗斯cert发布的预警[3]基本上就直接对应上了，所以一时间国内国外都在密切关注这件事件，在推特上卡巴斯基本人亲自站台引起热议[4]，在推特上也透露了很多其他的细节点，在这里一起整理一下整个事件的关键点：

卡巴斯基的报告：

  1. 卡巴斯基是在监控自己公司的Wifi流量时候发现了可疑的行为，这意味着卡巴斯基已经被攻击。

  2. 攻击目前最早能到2019年，攻击在卡巴斯基发布报告时仍然在感染

  3. 漏洞攻击方式发送带有附件iMessage消息给目标iOS设备，无需任何用户交互可以直接触发漏洞，说明是一个0-Click类型漏洞，漏洞执行后远程下载触发提权漏洞，这符合以往完整攻击链利用

另外在推特上卡巴斯基本人又补充了几点：

  1. Important: The activity observed in Operation Triangulation does not overlap with already known iOS campaigns, such as Pegasus, Predator or Reign.

[重要提示：在 Operation Triangulation 中观察到的活动与已知的 iOS 活动不重叠，例如 Pegasus、Predator 或
Reign。]

  2. I sent the details to Apple. No reply so far. But the vulns has already been patched back in Feb I guess. The 1-days Triangulation uses were once 0-days

[我把细节发给了苹果。至今没有回复。但我猜这些漏洞已经在2月修复了。1-days Triangulation曾经是0-days]

在这条推文的回复里有卡巴斯基的研究人员回复[5]可能有一个漏洞是 CVE-2022-46690 [6]

![图片](https://images.seebug.org/content/images/2023/06/06/1686036167000-2lkdus.png-w331s)

  3. We are quite confident that Kaspersky was not the main target of this cyberattack. The coming days will bring more clarity and further details on the worldwide proliferation of the spyware

[我们非常有信心卡巴斯基实验室不是这次网络攻击的主要目标。未来几天，间谍软件在全球范围内的扩散将变得更加清晰和详细。]

### 威胁情报追踪

在卡巴斯基的报告里是给出了一些C&C domains：

    
    
    addatamarket.net
    ans7tv.net
    anstv.net
    backuprabbit.com
    businessvideonews.com
    cloudsponcer.com
    datamarketplace.net
    mobilegamerstats.com
    snoweeanalytics.com
    tagclick-cdn.com
    topographyupdates.com
    unlimitedteacup.com
    virtuallaughing.com
    web-trackers.com
    growthtransport.com

因为这个攻击周期非常大长，时间跨度非常大，卡巴也没给出详细的分析及对应的时间，所以追踪起来是非常麻烦的。首先我们创宇智脑里的whois数据查询如下：

    
    
    "mobilegamerstats.com";"ns1.bitdomain.biz,ns2.bitdomain.biz,ns3.bitdomain.biz,ns4.bitdomain.biz";"15.164.228.250";"US";"";"";"";""
    "tagclick-cdn.com";"ns1.bitdomain.biz,ns2.bitdomain.biz,ns3.bitdomain.biz,ns4.bitdomain.biz";"15.206.93.78";"US";"";"";"";""
    "businessvideonews.com";"ns1.dnsowl.com,ns2.dnsowl.com,ns3.dnsowl.com";"51.79.214.251";"GB";"";"";"";""
    "growthtransport.com";"ns1.dnsowl.com,ns2.dnsowl.com,ns3.dnsowl.com";"165.22.89.102";"US";"";"";"";""
    "virtuallaughing.com";"braden.ns.cloudflare.com,elaine.ns.cloudflare.com";"104.21.60.240";"US";"";"";"";""
    "backuprabbit.com";"morgan.ns.cloudflare.com,nelci.ns.cloudflare.com";"104.21.21.154";"US";"";"";"";""
    "unlimitedteacup.com";"javon.ns.cloudflare.com,nelci.ns.cloudflare.com";"104.21.55.58";"US";"";"";"";""
    "cloudsponcer.com";"joyce.ns.cloudflare.com,kipp.ns.cloudflare.com";"188.114.96.3";"US";"";"";"";""
    "topographyupdates.com";"dalary.ns.cloudflare.com,nero.ns.cloudflare.com";"";"";"";"";"";""
    "snoweeanalytics.com";"cody.ns.cloudflare.com,harlee.ns.cloudflare.com";"172.67.184.201";"US";"";"";"";""
    "datamarketplace.net";"hunts.ns.cloudflare.com,phoenix.ns.cloudflare.com";"";"";"";"";"";""
    "addatamarket.net";"doug.ns.cloudflare.com,sandy.ns.cloudflare.com";"172.67.220.52";"US";"";"";"";""
    "web-trackers.com";"dns1.registrar-servers.com,dns2.registrar-servers.com";"15.164.228.250";"US";"";"";"";""

然后就是通过ZoomEye
"kuangkuang"一顿乱搜索，因为使用cloudflare.com的那些目标的IP一般都是cdn节点，所以直接就抛弃了，重点关注剩下的几个：

[注：在这里我有必要提一下，因为卡巴没有给详细的细节，实际上我们是不知道这些域名具体是提供什么服务的，但是从这个dns解析来大体可以分为两个类别：用cloudflare.com及没用cloudflare.com，以我个人的经验来判断，用cloudflare.com可能是第一步提供提取插件下载的使用的，而其他非cloudflare.com的可能是真正数据回传控制平台（也就是木马的控制台服务器），当然反过来也有可能]

    
    
    mobilegamerstats.com 15.164.228.250
    tagclick-cdn.com  15.206.93.78
    businessvideonews.com 51.79.214.251
    growthtransport.com 165.22.89.102
    web-trackers.com  15.164.228.250

web-trackers.com及mobilegamerstats.com 都在同一IP：15.164.228.250，用ZoomEye
IP域名反查得到如下图结果：

![图片](https://images.seebug.org/content/images/2023/06/06/1686036167000-3xsrjz.png-w331s)

新增加了2个域名：

    
    
    ec2-15-164-228-250.ap-northeast-2.compute.amazonaws.com
    toppull.net

15.206.93.78 新增

    
    
    ec2-15-206-93-78.ap-south-1.compute.amazonaws.com
    janicaherbals.com 

51.79.214.251 新增

    
    
    ip251.ip-51-79-214.net

165.22.89.102 新增

    
    
    weightlossappsforu.com

可以看出 15.164.228.250 及 15.206.93.78
用的都是amazonaws.com主机，这里需要强调下的是要注意域名解析时间，不一定就属于攻击者。

我们继续通过ZoomEye程序这些IP地址，通过行为测绘来进一步拓展：

15.164.228.250:443

    
    
    HTTP/1.1 404 Not Found
    
    Server: nginx
    Date: Sat, 13 May 2023 11:35:14 GMT
    Content-Type: text/html
    Content-Length: 146
    Connection: close
    
    <html>
    <head><title>404 Not Found</title></head>
    <body>
    <center><h1>404 Not Found</h1></center>
    <hr><center>nginx</center>
    </body>
    </html>
    
    
    SSL Certificate
    Version: TLS 1.2
    CipherSuit: TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
    Handshake Message: x509: cannot validate certificate for 15.164.228.250 because it doesn't contain any IP SANs
    Certificate:
        Data:
            Version: 3 (0x2)
            Serial Number: 182282035563670704559472620325359925476 (0x89223e3948d9e89e1c602965a01138e4)
        Signature Algorithm: SHA256-RSA
            Issuer: C=GB,ST=Greater Manchester,UnknownOID=2.5.4.7,O=Sectigo Limited,CN=Sectigo RSA Domain Validation Secure Server CA
            Validity
                Not Before: Oct 28 00:00:00 2022 UTC
                Not After : Nov 4 23:59:59 2023 UTC
            Subject: CN=mobilegamerstats.com
    ....
    
    
    jarm:2ad2ad0002ad2ad22c2ad2ad2ad2adc2ddcfd203d071c45b4b0ffe3d7b4b89

15.206.93.78:443

    
    
    HTTP/1.1 404 Not Found
    Date: Mon, 08 May 2023 18:23:21 GMT
    Server: Apache
    Content-Length: 196
    Connection: close
    Content-Type: text/html; charset=iso-8859-1
    
    <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <html><head>
    <title>404 Not Found</title>
    </head><body>
    <h1>Not Found</h1>
    <p>The requested URL was not found on this server.</p>
    </body></html>
    
    
    SSL Certificate
    Version: TLS 1.3
    CipherSuit: TLS_AES_256_GCM_SHA384
    Handshake Message: x509: cannot validate certificate for 15.206.93.78 because it doesn't contain any IP SANs
    Certificate:
        Data:
            Version: 3 (0x2)
            Serial Number: 178722881683709264493282432063425747940 (0x8674c663a8d4eb66cef841962b401be4)
        Signature Algorithm: SHA256-RSA
            Issuer: C=GB,CN=Sectigo RSA Domain Validation Secure Server CA,L=Salford,O=Sectigo Limited,ST=Greater Manchester
            Validity
                Not Before: Feb 24 00:00:12 2023 UTC
                Not After : Feb 24 23:59:11 2024 UTC
            Subject: CN=tagclick-cdn.com
    ....
    
    
    jarm:2ad2ad16d2ad2ad00042d42d00000061256d32ed7779c14686ad100544dc8d

51.79.214.251:443

    
    
    HTTP/1.1 404 Not Found
    
    Server: openresty
    Date: Sat, 29 Apr 2023 16:15:47 GMT
    Content-Type: text/html
    Content-Length: 150
    Connection: close
    
    <html>
    <head><title>404 Not Found</title></head>
    <body>
    <center><h1>404 Not Found</h1></center>
    <hr><center>openresty</center>
    </body>
    </html>
    
    
    SSL Certificate
    Version: TLS 1.2
    CipherSuit: TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
    Handshake Message: x509: cannot validate certificate for 51.79.214.251 because it doesn't contain any IP SANs
    Certificate:
        Data:
            Version: 3 (0x2)
            Serial Number: 282523145376381852661219844478979689339192 (0x33e42ca90f8006d6a3434a44da98656d938)
        Signature Algorithm: SHA256-RSA
            Issuer: C=US,CN=R3,O=Let's Encrypt
            Validity
                Not Before: Apr 21 20:47:08 2023 UTC
                Not After : Jul 20 20:47:08 2023 UTC
            Subject: CN=businessvideonews.com
    ....
    
    
    jarm:2ad2ad16d2ad2ad22c2ad2ad2ad2ad47321614530b94a96fa03d06e666d6d6

165.22.89.102:443

可能是ZoomEye探测时丢包 443端口的banner没有获取到，只有证书内容：

    
    
    SSL Certificate
    Version: TLS 1.2
    CipherSuit: TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
    Handshake Message: x509: cannot validate certificate for 165.22.89.102 because it doesn't contain any IP SANs
    Certificate:
        Data:
            Version: 3 (0x2)
            Serial Number: 235615233180455988417485264570865572800 (0xb141d7e216ea091712a1ebefc2ea5bc0)
        Signature Algorithm: SHA256-RSA
            Issuer: C=GB,CN=Sectigo RSA Domain Validation Secure Server CA,L=Salford,O=Sectigo Limited,ST=Greater Manchester
            Validity
                Not Before: Mar 28 00:00:12 2023 UTC
                Not After : Mar 19 23:59:11 2024 UTC
            Subject: CN=www.growthtransport.com
    ....
    
    
    jarm:2ad2ad0002ad2ad0002ad2ad2ad2ad02098c5f1b1aef82f7daaf9fed36c4e8

从“行为测绘”角度上来看，上面4个IP的部署还是有典型的“行为”的：

1、Banner都是404页面，但是Server不一样，所以对应的Content-Length及html不一样

2、证书有统一性：

  * 有三个的Issuer是一样的，另外一个是“C=US,CN=R3,O=Let's Encrypt” 这个按我的经验来看属于正常的
  * Subject 的格式一样，都直接是CN为域名根，没有其他的信息，这个行为很重要！
  * 虽然每个的jarm不一样，但是我们可以通过Jarm来帮助排除

所以根据上面每个IP的banner进行了一些尝试，过程就不详细说了

    
    
    mobilegamerstats.com 这个扩展出一个 "Subject: CN=nextor.rlbvlf.net" 
    tagclick-cdn.com 扩展出 "Subject: CN=protocdn.net" 、 "Subject: CN=secure.platon-online.com" 、"Subject: CN=secureanalytics87.com" 
    businessvideonews.com 没有扩展出新的
    growthtransport.com 没有扩展出新的

再结合上面提到的证书行为，我个人觉得nextor.rlbvlf.net 及 secure.platon-online.com
是子域名不太符合前面的“行为”，应该作为次要考虑。

我们这里还有一个很关键的点没有做，就是域名关联email的操作，如果你用whois库查询可以看到域名基本上都是处于保护状态是没办法关联到数据，直接通过我们知道创宇的威胁情报系统里到如下结果：

    
    
    tagclick-cdn.com --> victorvasquez541991@gmail.com
    mobilegamerstats.com --> yoshidaharu2208@protonmail.com

这个从邮件命名“行为”还是比较统一的，前面一串字母+数字，那么这个字母是啥意思呢？丢给Google及ChatGPT，如下图：

![图片](https://images.seebug.org/content/images/2023/06/06/1686036167000-4zoviu.png-w331s)

![图片](https://images.seebug.org/content/images/2023/06/06/1686036168000-5yslja.png-w331s)

可以确定都是一个名字，yoshidaharu --> Haru Yoshida
看起来是一个动漫里的人物可能觉得这个攻击者喜欢“二次元”风格，我个人觉得这个是巧合，因为victorvasquez -->Victor Vazquez
有很多老外都叫这个名字，从ChatGPT给出的结果来都符合“常用名”的风格。

随后我们最后又做了通过这些邮件去关联域名等包括其他数据库的“交叉”分析，可惜并没有找到新的关联数据线索。

### 归因

从上面的数据分析来看，目标画像有几点：

  1. 习惯使用amazonaws主机
  2. 习惯使用cloudflare.com
  3. 习惯证书Sectigo、Subject主域名
  4. 邮件地址常用名+数字用gmail及protonmail
  5. 样本目前排除以往同类武器（Pegasus、Predator 或 Reign）关联
  6. 攻击目标：“属于各个大使馆的工作人员和俄罗斯政府的成员”，“另外包括北约集团国家和后苏联地区，以及以色列，特区和中国等”
  7. 相关细节报告给苹果，苹果没有回应

单独从目前的技术方向上的细节来看，披露的细节非常有限，很难得到明确的归因，但是说美帝的嫌疑确实很大用的核心资产都是美帝可控资产，也就说俄罗斯不好直接查水表，我相信俄罗斯肯定是掌握更多的细节，尤其是被攻击的目标，而俄罗斯FSB的直接把矛头指向了美帝，顺带提了下苹果公司与美帝NSA的合作勾当，如果卡巴斯基本人说的细节报告给苹果，苹果没有做任何回应的细节是真的话，那确实有点不好说？！

另外从历史上来看，美帝泄露的那些高端网络攻击武器里，都主要在传统的服务器OS，而没有看到针对移动设备的，所以在这个角度上来看这个属于后泄露时代的大杀器是非常有可能的。至于说这个是不是苹果给NSA专门留的“后门”漏洞，就不好说了...

### 漏洞有没有修复？

这个问题在上面其实都说过了，考虑到关心的人比较多，单独提一下。从卡巴斯基本人在推特上说可能漏洞在2月份已经修复（注意是可能），然后从卡巴斯基的报告里说他们抓到的被攻击设备最新为iOS
15.7（目前我用的最新版本为iOS
16.6），另外卡巴斯基的一个研究员回复可能有一个漏洞为CVE-2022-46690是一个提权的。我个人觉得要实现这个完整攻击链，可能是需要一系列的漏洞做组合攻击才能实现，所以在现阶段攻击者之前使用的武器很大程度上不能直接来攻击最新的iOS，但这个不意味着所有攻击链的漏洞都已经修复，攻击者是否还存在其他攻击链武器。所以对于有安全洁癖的可以考虑直接禁用iMessage，虽然我觉得这种级别的武器是不可能来搞一般用户的，只是iMessage这玩意对于中国用户来说确实没啥用，禁用还少个攻击面也挺好，对于iOS设备来说，实现远程0-Click的RCE，常用的wifi、蓝牙等攻击面，实际上还是有具体的物理距离的，而基带相关短信等接口包括iMessage这种是真正实现超越距离的“指哪打哪”～

![图片](https://images.seebug.org/content/images/2023/06/06/1686036168000-6essdv.png-w331s)

感谢团队练哥的数据分析支持

![
](https://images.seebug.org/content/images/2023/06/1c14dd94-96aa-4593-8272-10866987495b.png-w331s)

### 参考链接

[1] <https://securelist.com/operation-triangulation/109842/>  
[2]
<http://www.fsb.ru/fsb/press/message/single.htm!id=10439739@fsbMessage.html?continueFlag=7ad933cf9013b5183b483ffdeff43bb2>  
[3] <https://safe-surf.ru/upload/ALRT/ALRT-20230601.1.pdf>  
[4] <https://twitter.com/e_kaspersky/status/1664263801490014208>  
[5] <https://twitter.com/kucher1n/status/1664398539193974786>  
[6] <https://support.apple.com/en-us/HT213530>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2076/>

