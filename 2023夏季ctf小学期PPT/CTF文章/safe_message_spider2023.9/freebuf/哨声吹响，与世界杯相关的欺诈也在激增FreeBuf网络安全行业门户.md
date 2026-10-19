2022 年世界杯已经开始，通过虚假流媒体网站与彩票针对足球迷的诈骗激增。近日，Zscaler
发现与世界杯相关的新注册域名有所增加，尽管并非都是恶意的，也是值得警惕的。

## 流量趋势

随着世界杯的开赛，从 11 月 21 日流媒体流量就开始显著增加。

![image.png-46.9kB](https://image.3001.net/images/20221128/1669566092_63838e8c829d238ea6764.png!small)流量变化趋势

## 案例一：虚假流媒体网站

虚假流媒体网站和其他诈骗网站数量激增，这些网站会声称提供免费的世界杯比赛直播服务。但实际上会将用户重定向到其他网页，提示用户输入银行卡信息。类似的流媒体网站模板，在
2020 年东京奥运会期间也出现过。

这些虚假网站通常会使用新注册的恶意域名，有些也会滥用良性服务或者提供对外跳转的链接地址。

![image.png-167.1kB](https://image.3001.net/images/20221128/1669566093_63838e8d63679a6bfc6ae.png!small)Linkedin
对外跳转示例

![image.png-407.3kB](https://image.3001.net/images/20221128/1669566094_63838e8e214914e4643f4.png!small)虚假网站示例

受害者跳转到号称提供 2022 年世界杯开幕式直播的恶意网站，该网站再重定向到 Blogspot
上部署的虚假流媒体网站，提示用户创建账户并免费观看直播。除了 Linkedin，攻击者还利用了 OpenSea 等网站。

![image.png-180.3kB](https://image.3001.net/images/20221128/1669566094_63838e8ee7b5af4b3760f.png!small)OpenSea
对外跳转示例

![image.png-489.8kB](https://image.3001.net/images/20221128/1669566095_63838e8f967e18331ea83.png!small)虚假网站示例

用户输入电子邮件地址与密码后，会被多次重定向，最终跳转到 YouTube。

![image.png-379.5kB](https://image.3001.net/images/20221128/1669566096_63838e90724184e647da4.png!small)重定向链条

访问者都会要求在表单中提交银行卡的详细信息：

![image.png-577.9kB](https://image.3001.net/images/20221128/1669566097_63838e91d637464d8c42b.png!small)虚假支付页面

![image.png-377.7kB](https://image.3001.net/images/20221128/1669566099_63838e93b3b90e2354458.png!small)虚假支付页面

## 案例二：门票与彩票诈骗

许多与世界杯门票销售相关的网站被建立起来，引诱用户购买虚假门票。攻击者直接窃取银行卡信息或者收取机票、门票的费用。例如下 11 月 15
日，有攻击者部署了一个提供世界杯门票的网站。

![image.png-768.8kB](https://image.3001.net/images/20221128/1669566101_63838e9552c8e014ec98a.png!small)虚假门票销售网站

门票之外，与世界杯相关的事情都可以进行诈骗。如下，攻击者在 11 月 11 日部署的模拟卡塔尔航空的恶意网站。

![image.png-375.1kB](https://image.3001.net/images/20221128/1669566104_63838e981369e1f20515b.png!small)虚假机票销售网站

恶意邮件也开始以 2022 年世界杯彩票委员会的名义进行攻击：

![image.png-111kB](https://image.3001.net/images/20221128/1669566105_63838e99b658775caa4be.png!small)恶意邮件

恶意附件中表示用户是彩票的中奖者，用户可以填写个人信息领取奖金。

![image.png-529.7kB](https://image.3001.net/images/20221128/1669566106_63838e9a981211e36f2e9.png!small)恶意附件

## 案例三：SolarMarker

SolarMarker 是一个非常常见的恶意软件家族，经常进行信息窃密。攻击者经常在失陷的 WordPress 网站上部署恶意 PDF 文件，再通过 SEO
进行分发。研究人员发现，SolarMarker 开始攻击那些售卖世界杯贴纸的电子商务网站，将用户重定向到其他网站并进行攻击。

![image.png-123.6kB](https://image.3001.net/images/20221128/1669566108_63838e9c38b645110706c.png!small)失陷网站的恶意
PDF 文件

## 案例四：游戏诈骗

攻击者通过恶意 PDF 文件，引诱用户下载破解版 FIFA 游戏。此类攻击行为从 8 月就开始出现，一直持续到世界杯开幕。

![image.png-161.5kB](https://image.3001.net/images/20221128/1669566108_63838e9ce81b1e3f25e55.png!small)恶意
PDF 文件

点击下载后，用户会被重定向到其他域名，要求下载包含恶意可执行文件的压缩包。

![image.png-68.2kB](https://image.3001.net/images/20221128/1669566109_63838e9daabee1133ac6a.png!small)恶意压缩包

## 案例五：Parrot TDS 虚假更新

Parrot TDS 是 2017 年以来一直保持活跃的恶意软件，其将恶意 JavaScript 代码注入 CMS
中。大多数情况下，攻击者显示用户的浏览器需要更新来引诱下载。攻击者近日也瞄准上了世界杯相关的网站，发起了大量攻击。

![image.png-628.4kB](https://image.3001.net/images/20221128/1669566110_63838e9e5f84a4ef7640f.png!small)注入脚本

## IOC

> linkedin[.]com/pulse/official-fifa-world-cup-2022-live-micker-hukkker  
> fifaworldcupontv[.]blogspot[.]com  
> opensea[.]io/collection/fifa-world-cup-2022-qatar-vs-ecuador-watch-hd-onli  
> sportsevents4me[.]store  
> humourousretort[.]top  
> i13lc8k[.]cn  
> bestsports-stream[.]com  
> gatewaytoworld[.]com  
> Fifafootball[.]io  
> Fifa2022worldcup[.]net  
> 09FAF066833D24B049DBC3C824AE25E3  
> 556858D3B8629407A65E2737C1DED5DC  
> 277760FC389F8F21A50FB04D27519BEF  
> 8C436293FD1221FAD3E48ECEDAE683A5  
> 02E7CA1129049755697C8185AC8F98B9  
> D0DEE3AAC6A71AA9E9E4FC6E411574F0  
> 3E74F0F073E296460C52EEE06E914B25  
> 346E4B588F0A6EBE9E0E6B086D23E933  
> C87B80497B85B22BE53F52E0F2EBDF11  
> 854D5DFE2D5193AA4150765C123DF8AD

## 参考来源

> [Zscaler](https://www.zscaler.com/blogs/security-research/surge-fake-fifa-> world-cup-streaming-sites-targets-virtual-fans)

