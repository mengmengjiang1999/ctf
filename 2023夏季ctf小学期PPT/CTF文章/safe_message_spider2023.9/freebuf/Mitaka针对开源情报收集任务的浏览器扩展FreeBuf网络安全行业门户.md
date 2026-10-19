**今天给大家介绍的是一款针对开源情报收集任务的浏览器扩展，这款扩展名叫Mitaka，希望该工具可以给广大研究人员的OSINT搜索研究提供帮助。**

![](https://image.3001.net/images/20191008/1570500343_5d9beef7adeec.png!small)

**Mitaka可以完成的任务包括但不限于：**

>
> 1、从选取的文本块提取或重构IoC，例如将example[.]com更改为example.com，将test[at]example.com更改为test@example.com，或将hxxp://example.com更改为[http://example.com](http://example.com/)。
>
> 2、基于多种引擎实现搜索或扫描任务，例如VirusTotal、urlscan io、Censys和Shodan等。

##  功能介绍

###  支持的IoC类型

**名称** |  **描述** **.** |  **样例**  
---|---|---  
text  |  任意文本  |  any string(s)  
ip  |  IPv4地址  |  8.8.8.8  
domain  |  域名  |  github.com  
url  |  URL地址  |  [https://github.com](https://github.com/)  
email  |  电子邮件地址  |  test@test.com  
asn  |  ASN  |  AS13335  
hash  |  md5 / sha1 / sha256  |  44d88612fea8a8f36de82e1278abb02f  
cve  |  CVE编号  |  CVE-2018-11776  
btc  |  比特币地址  |  1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa  
gaPubID  |  Google Adsense Publisher ID  |  pub-9383614236930773  
gaTrackID  |  Google Analytics Tracker ID  |  UA-67609351-1  
  
###  支持的搜索引擎

**名称** |  **url** |  **支持的类型**  
---|---|---  
AbuseIPDB  |  [https://www.abuseipdb.com](https://www.abuseipdb.com/) |  ip地址  
Apility  |  [https://apility.io](https://apility.io/) |  ip地址 / 域名/ 电子邮件/ asn  
archive.org  |  [https://archive.org](https://archive.org/) |  url  
archive.today  |  [http://archive.fo](http://archive.fo/) |  url  
BGPView  |  [https://bgpview.io](https://bgpview.io/) |  ip地址 / asn  
BinaryEdge  |  [https://app.binaryedge.io](https://app.binaryedge.io/) |  ip地址
/ 域名  
BitcoinAbuse  |  [https://www.bitcoinabuse.com](https://www.bitcoinabuse.com/)
|  比特币  
Blockchain.com  |  [https://www.blockchain.com](https://www.blockchain.com/) |
比特币  
BlockCypher  |  [https://live.blockcypher.com](https://live.blockcypher.com/)
|  比特币  
Censys  |  [https://censys.io](https://censys.io/) |  ip地址 / 域名/ asn / 文本  
crt.sh  |  [https://crt.sh](https://crt.sh/) |  域名  
DNSlytics  |  [https://dnslytics.com](https://dnslytics.com/) |  ip地址 / 域名  
DomainBigData  |  [https://domainbigdata.com](https://domainbigdata.com/) |
域名  
DomainTools  |  [https://www.domaintools.com](https://www.domaintools.com/) |
ip地址 / 域名  
DomainWatch  |  [https://domainwat.ch](https://domainwat.ch/) |  域名/ 电子邮件  
EmailRep  |  [https://emailrep.io](https://emailrep.io/) |  电子邮件  
FindSubDomains  |  [https://findsubdomains.com](https://findsubdomains.com/) |
域名  
FOFA  |  [https://fofa.so](https://fofa.so/) |  ip地址 / 域名  
FortiGuard  |  [https://fortiguard.com](https://fortiguard.com/) |  ip地址 / url
/ cve  
Google Safe Browsing  |
[https://transparencyreport.google.com](https://transparencyreport.google.com/)
|  域名/ url  
GreyNoise  |  [https://viz.greynoise.io](https://viz.greynoise.io/) |  ip地址 /
域名/ asn  
Hashdd  |  [https://hashdd.com](https://hashdd.com/) |  ip地址 / 域名/ hash  
HybridAnalysis  |  [https://www.hybrid-analysis.com](https://www.hybrid-analysis.com/) |  ip地址 / 域名/ 哈希(sha256 only)  
Intelligence X  |  [https://intelx.io](https://intelx.io/) |  ip地址 / 域名/ url /
电子邮件/ btc  
IPinfo  |  [https://ipinfo.io](https://ipinfo.io/) |  ip地址 / asn  
IPIP  |  [https://en.ipip.net](https://en.ipip.net/) |  ip地址 / asn  
Joe Sandbox  |  [https://www.joesandbox.com](https://www.joesandbox.com/) |
哈希  
MalShare  |  [https://malshare.com](https://malshare.com/) |  哈希  
Maltiverse  |  [https://www.maltiverse.com](https://www.maltiverse.com/) |
域名/ 哈希  
NVD  |  [https://nvd.nist.gov](https://nvd.nist.gov/) |  cve  
OOCPR  |  [https://data.occrp.org](https://data.occrp.org/) |  电子邮件  
ONYPHE  |  [https://www.onyphe.io](https://www.onyphe.io/) |  ip地址  
OTX  |  [https://otx.alienvault.com](https://otx.alienvault.com/) |  ip地址 / 域名
/ 哈希  
PubDB  |  [http://pub-db.com](http://pub-db.com/) |  gaPubID / gaTrackID  
PublicWWW  |  [https://publicwww.com](https://publicwww.com/) |  文本  
Pulsedive  |  [https://pulsedive.com](https://pulsedive.com/) |  ip地址 / 域名/
url / 哈希  
RiskIQ  |  [http://community.riskiq.com](http://community.riskiq.com/) |  ip地址
/ 域名 / 电子邮件 / gaTrackID  
SecurityTrails  |  [https://securitytrails.com](https://securitytrails.com/) |
ip地址 / 域名 / 电子邮件  
Shodan  |  [https://www.shodan.io](https://www.shodan.io/) |  ip地址 / 域名 / asn  
Sploitus  |  [https://sploitus.com](https://sploitus.com/) |  cve  
SpyOnWeb  |  [http://spyonweb.com](http://spyonweb.com/) |  ip地址 / 域名 /
gaPubID / gaTrackID  
Talos  |  [https://talosintelligence.com](https://talosintelligence.com/) |
ip地址 / 域名  
ThreatConnect  |
[https://app.threatconnect.com](https://app.threatconnect.com/) |  ip地址 / 域名 /
电子邮件  
ThreatCrowd  |  [https://www.threatcrowd.org](https://www.threatcrowd.org/) |
ip地址 / 域名 / 电子邮件  
ThreatMiner  |  [https://www.threatminer.org](https://www.threatminer.org/) |
ip地址 / 域名 / 哈希  
TIP  |
[https://threatintelligenceplatform.com](https://threatintelligenceplatform.com/)
|  ip地址 / 域名  
Urlscan  |  [https://urlscan.io](https://urlscan.io/) |  ip地址 / 域名 / asn / url  
ViewDNS  |  [https://viewdns.info](https://viewdns.info/) |  ip地址 / 域名 / 电子邮件  
VirusTotal  |  [https://www.virustotal.com](https://www.virustotal.com/) |
ip地址 / 域名 / url / 哈希  
Vulmon  |  [https://vulmon.com](https://vulmon.com/) |  cve  
VulncodeDB  |  [https://www.vulncode-db.com](https://www.vulncode-db.com/) |
cve  
VxCube  |  [http://vxcube.com](http://vxcube.com/) |  ip地址 / 域名 / 哈希  
WebAnalyzer  |  [https://wa-com.com](https://wa-com.com/) |  域名  
We Leak Info  |  [https://weleakinfo.com](https://weleakinfo.com/) |  电子邮件  
X-Force Exchange  |
[https://exchange.xforce.ibmcloud.com](https://exchange.xforce.ibmcloud.com/)
|  ip地址 / 域名 / 哈希  
ZoomEye  |  [https://www.zoomeye.org](https://www.zoomeye.org/) |  ip地址  
  
###  支持的扫描引擎

**名称** |  **url** |  **支持的类型**  
---|---|---  
Urlscan  |  [https://urlscan.io](https://urlscan.io/) |  ip地址 / 域名/ url  
VirusTotal  |  [https://www.virustotal.com](https://www.virustotal.com/) |
url  
  
###  工具下载

>
> Chrome：【[点我下载](https://chrome.google.com/webstore/detail/mitaka/bfjbejmeoibbdpfdbmbacmefcbannnbg)】
>
> FireFox：【[点我下载](https://addons.mozilla.org/en-US/firefox/addon/mitaka/)】

##  工具使用

Mitaka这款浏览器扩展可以根据用户所选择的IoC类型来提供不同的功能选项菜单，并为广大用户提供更加丰富的OSINT功能。

###  工具使用样例

![](https://image.3001.net/images/20191008/1570500393_5d9bef299c585.gif!small)![](https://image.3001.net/images/20191008/1570500393_5d9bef29b8f6c.gif!small)

注意：如果你需要使用urlscan.io或VirusTotal扫描功能，那么你需要在工具的选项配置页面中设置你的urlscan.io或VirusTotal的API秘钥。

##  工具选项

我们可以在该工具的选项配置页面中，根据我们的需要来启用或禁用某个搜索引擎：

![](https://image.3001.net/images/20191008/1570500406_5d9bef36402a6.png!small)

##  工具构建（针对开发者）

这款浏览器扩展基于TypeScript开发，并使用Webpack构建。

TypeScript文件位于src目录中，可以通过TypeScript编译器运行，然后使用Webpack进行代码构建，最终在dist目录中生成JavaScript文件。

> git clone <https://github.com/ninoseki/mitaka.git>
>
> cd mitaka
>
> npm install
>
> npm run test
>
> npm run build

##  项目地址

> Mitaka：【[GitHub传送门](https://github.com/ninoseki/mitaka)】

 ***
参考来源：[ninoseki](https://github.com/ninoseki/mitaka)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

