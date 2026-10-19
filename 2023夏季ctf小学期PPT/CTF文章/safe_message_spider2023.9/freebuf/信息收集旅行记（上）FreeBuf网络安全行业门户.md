原创：Qftm 合天智汇

"只有不努力的黑客，没有攻不破的系统"。

这篇文章《信息收集-旅行记》是笔者几年的经验总结，在SRC漏洞挖掘中，信息收集占很大一部分，能收集到别人收集不到的资产，就能挖到别人挖不到的漏洞。

## 收集域名信息  

知道目标域名之后，我们要做的第一件事情就是获取域名的注册信息，包括该域名的DNS服务器信息和注册人的联系信息等。

## Whois 查询  

Whois
简单来说，就是一个用来查询域名是否已经被注册，以及注册域名的详细信息的数据库（如域名所有人、域名注册商、域名注册日期和过期日期、DNS等）。通过域名Whois服务器查询，可以查询域名归属者联系方式，以及注册和到期时间。

Kali下whois查询 https://www.kali.org/downloads/域名Whois查询 - 站长之家
http://whois.chinaz.com/Whois 爱站 http://whois.aizhan.com/ip138
https://site.ip138.com/Whois Lookup https://www.whois.net/ICANN Lookup
https://lookup.icann.org/域名信息查询 -腾讯云https://whois.cloud.tencent.com/domain?domain=nicolasbouliane
http://nicolasbouliane.com/utils/whois/?url=http://baidu.com新网 whois信息查询
http://whois.xinnet.com/IP WHOIS查询 - 站长工具 http://tool.chinaz.com/ipwhois/

![v2-8a0d70f620271d60c4d88df5a522395c_hd.j](https://pic4.zhimg.com/80/v2-8a0d70f620271d60c4d88df5a522395c_hd.jpg)

Whois网络注册信息探测：http://www.hetianlab.com/expc.do?ec=66a18063-8287-4b7c-9dfd-97faf52282f1（通过本实验的学习，了解Whois的概念，掌握Whois网络注册信息探测的目的和技术方法。）复制链接做实验。

备案信息查询

国内网站注册需要向国家有关部门申请备案，防止网站从事非法活动，而国外网站不需要备案2333。

ICP备案查询网 http://www.beianbeian.com/ ICP备案查询 - 站长工具 http://icp.chinaz.com/
SEO综合查询 - 爱站 https://www.aizhan.com/seo/ 批量查询 - 站长工具
http://icp.chinaz.com/searchs 工业和信息化部ICP/IP/域名信息备案管理
http://www.beian.miit.gov.cn/publish/query/indexFirst.action

![v2-5a6d1c3ceecbbee6bf89d01261550c25_hd.j](https://pic4.zhimg.com/80/v2-5a6d1c3ceecbbee6bf89d01261550c25_hd.jpg)

## 信用信息查询  

国家企业信用信息公示系统 http://www.gsxt.gov.cn/index.html

全国企业信息查询 http://company.xizhi.com/

个人信用查询搜索-企业信息查询搜索-统一社会信用代码查询-信用中国 https://www.creditchina.gov.cn/

![v2-64d000150d2b4a035aa2b141fb942a8b_hd.j](https://pic2.zhimg.com/80/v2-64d000150d2b4a035aa2b141fb942a8b_hd.jpg)

## IP反查站点的站  

在线网站

Dnslytics

Dnslytics地址：https://dnslytics.com/

利用Dnslytics反查IP可以得到如下信息

IP information Network information Hosting information SPAM database lookup
Open TCP/UDP ports Blocklist lookup Whois information Geo information Country
information Update information

利用Dnslytics反查域名可以得到如下信息

Domain and Ranking InformationHosting Information{ A / AAAA Record NS Record
MX Record SPF Record}Web InformationWhois Information

浏览器插件

通过Google、FireFox等插件的使用，收集域名信息

myip.ms

![v2-8a4f7c9ed8594fa179886feaa1d0c925_hd.j](https://pic2.zhimg.com/80/v2-8a4f7c9ed8594fa179886feaa1d0c925_hd.jpg)

![v2-ef30c3d9c23e5299d8***3f069eb0f04_hd.j](https://pic1.zhimg.com/80/v2-ef30c3d9c23e5299d8***3f069eb0f04_hd.jpg)

![v2-34cb357de873bf7fd71a1007317288a5_hd.j](https://pic3.zhimg.com/80/v2-34cb357de873bf7fd71a1007317288a5_hd.jpg)

浏览器插件的使用：

[实验:浏览器插件的使用(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECID9d6c0ca797abec2017042513322900001)

（学习常见浏览器插件的使用。）

## 收集相关应用信息  

天眼查 <https://www.tianyancha.com/>

企查查 <https://www.qichacha.com/>

## 微信公众号&微博  

天眼查

根据前面获取的企业名称可以获取目标企业的微信公众号、微博、备案站点、软件著作权等信息。

天眼查-商业安全工具 <https://www.tianyancha.com/>

![v2-c2db5fc0ce26d9d27e74d18afa027dda_hd.j](https://pic4.zhimg.com/80/v2-c2db5fc0ce26d9d27e74d18afa027dda_hd.jpg)

微信公众号

![v2-f4e1407a6f7f4902d3f82b9604a56add_hd.j](https://pic4.zhimg.com/80/v2-f4e1407a6f7f4902d3f82b9604a56add_hd.jpg)

微博

![v2-b70855ab4c3c95df17dc6f5f6c85c5fc_hd.j](https://pic2.zhimg.com/80/v2-b70855ab4c3c95df17dc6f5f6c85c5fc_hd.jpg)

APP

七麦数据

https://www.qimai.cn/

通过当前APP查询同开发商应用，得到目标所有APP应用

![v2-48813176846e989236140a3f02622317_hd.j](https://pic3.zhimg.com/80/v2-48813176846e989236140a3f02622317_hd.jpg)

AppStore

<https://apps.apple.com/>

通过当前APP查询同开发商应用，得到目标所有APP应用

![v2-19c2d5faa236377b2d54fc6970e247ea_hd.j](https://pic2.zhimg.com/80/v2-19c2d5faa236377b2d54fc6970e247ea_hd.jpg)

## 收集子域名信息  

子域名也就是二级域名，是指顶级域名下的域名。假设我们的目标网络规模比较大，直接从主域入手显然是很不理智的，因为对于这种规模的目标，一般其主域都是重点防护区域，所以不如先进入目标的某个子域，然后再想办法迂回接近真正的目标，这无疑是个比较好的选择。那么问题来了，怎样才能尽可能多地搜集目标的高价值子域呢？常用的方法有以下这几种。

在线平台

第三方平台查询

主要是一些第三方网站和一些博主提供的服务

ip138 https://site.ip138.com/ 站长工具 http://tool.chinaz.com/subdomain/?domain=
hackertarget https://hackertarget.com/find-dns-host-records/ phpinfo
https://phpinfo.me/domain/ t1h2ua https://www.t1h2ua.cn/tools/ dnsdumpster
https://dnsdumpster.com/ chinacycc https://d.chinacycc.com/ zcjun
http://z.zcjun.com/

## 权重综合查询  

爱站 <https://www.aizhan.com/seo/>

站长工具 <http://rank.chinaz.com/all/>

![v2-b85c0784a8b2c273c3d4dfef0a15db76_hd.j](https://pic2.zhimg.com/80/v2-b85c0784a8b2c273c3d4dfef0a15db76_hd.jpg)

## 全国政府网站基本数据库  

[全国政府网站基本信息数据库](http://114.55.181.28/databaseInfo/index)

![v2-becf16a4317a294929368aa05f69ad00_hd.j](https://pic2.zhimg.com/80/v2-becf16a4317a294929368aa05f69ad00_hd.jpg)

## IP反查绑定域名网站  

IP关联域名，大部分网站一个IP多个域名

http://s.tool.chinaz.com/same?shttp://dns.aizhan.com/

## 资产搜索引擎  

google、shodan、FOFA、zoomeye

Google语法查询

搜索子域名 "site:xxxxx"

![v2-fd4a1d97b558ec7e2893fe5bee3f1e1a_hd.j](https://pic4.zhimg.com/80/v2-fd4a1d97b558ec7e2893fe5bee3f1e1a_hd.jpg)

### FOFA语法查询  

https://fofa.so/

搜索子域名 "domain:xxxxx"

domain="baidu.com"

![v2-a0d57364fdb14a573dd2857b9d82f69f_hd.j](https://pic2.zhimg.com/80/v2-a0d57364fdb14a573dd2857b9d82f69f_hd.jpg)

工具枚举

常用子域名工具如下（Github上都可搜到）

OneForAll Layer Sublist3r subDomainsBrute K8 wydomain dnsmaper dnsbrute
Findomain fierce等

个人推荐：OneForAll、Layer、Sublist3r、subDomainsBrute

OneForAll

OneForAll是一款功能强大的子域收集工具，拥有多个模块和接口扫描，收集子域信息很全，包括子域、子域IP、子域常用端口、子域Title、子域Banner、子域状态等。

项目地址：https://github.com/shmilylty/OneForAll

子域名收集：python3 oneforall.py --target=target.com run

![v2-60fd661cac68661e5c3cd5637e974d53_hd.j](https://pic1.zhimg.com/80/v2-60fd661cac68661e5c3cd5637e974d53_hd.jpg)

Layer

Layer子域名挖掘机的使用方法比较简单，在域名对话框中直接输入域名就可以进行扫描，它的显示界面比较细致，有域名、解析IP、开放端口、Web服务器和网站状态等

![v2-aa27878d8df0020357cfd35860f94ffa_hd.j](https://pic1.zhimg.com/80/v2-aa27878d8df0020357cfd35860f94ffa_hd.jpg)

subDomainsBrute

subDomainsBrute的特点是可以用小字典递归地发现三级域名、四级域名,甚至五级域名等不容易被探测到的域名。

项目地址：https://github.com/lijiejie/subDomainsBrute

子域名收集：python subDomainsbrute.py xtarget.com

Sublist3r

Sublist3r也是一个比较常用的工具， 它能列举多种资源，如在Google、Yahoo、 Bing、
Baidu和Ask等搜索引擎中可查到的子域名，还可以列出Netcraft、VirusTotal、ThreatCrowd、 DNSdumpster、SSL
Certificates、和Reverse DNS查到的子域名。

项目地址：https://github.com/aboul3la/Sublist3r

子域名收集：python sublist3r.py -d target.com -b -t 50 -p 80,443,21,22

![v2-9292bb19936c60990dc9811d71b68882_hd.j](https://pic1.zhimg.com/80/v2-9292bb19936c60990dc9811d71b68882_hd.jpg)

## 证书透明度公开日志枚举  

证书透明度(Certificate Transparency, CT)是证书授权机构(CA)
的一个项目，证书授权机构会将每个SSL/TLS证书发布到公共日志中。一个SSL/TLS证书通常包含域名、子域名和邮件地址，
这些也经常成为攻击者非常希望获得的有用信息。查找某个域名所属证书的最简单的方法就是使用搜索引|擎搜索一些公开的CT日志。

### 在线第三方平台查询  

crt.sh: https://crt.sh censys: https://censys.io myssl：https://myssl.com

crt: https://crt.sh/?q=baidu.com

![v2-b211b5fa6590c85acb2a8bb918780fff_hd.j](https://pic1.zhimg.com/80/v2-b211b5fa6590c85acb2a8bb918780fff_hd.jpg)

![v2-19a65139d9997146be8299541e9a0136_hd.j](https://pic4.zhimg.com/80/v2-19a65139d9997146be8299541e9a0136_hd.jpg)

![v2-f31738e49d1eac6053eb803bd4ef4951_hd.j](https://pic3.zhimg.com/80/v2-f31738e49d1eac6053eb803bd4ef4951_hd.jpg)

## 工具枚举查询  

通过工具可以调用各个证书接口进行域名查询

常用工具

Findomain Sublist3r（SSL Certificates）等

Findomain

Findomain不使用子域名寻找的常规方法，而是使用证书透明度日志来查找子域，并且该方法使其工具更加快速和可靠。该工具使用多个公共API来执行搜索

CertspotterCrt.shVirustotalSublist3rFacebook **Spyse (CertDB)
*BufferoverThreadcrowVirustotal with apikey **

项目地址：https://github.com/Edu4rdSHL/findomain

子域名收集：findomain -t target.com

使用所有API搜索子域并将数据导出到CSV文件：findomain -t target.com -a -o csv

## DNS历史解析  

dnsdb https://www.dnsdb.io

viewdns https://viewdns.info/

## DNS域传送漏洞  

目前来看"DNS域传送漏洞"已经很少了。

### DNS记录分类  

常见的DNS记录有以下几类：

A记录 IP地址记录,记录一个域名对应的IP地址 AAAA记录 IPv6地址记录，记录一个域名对应的IPv6地址 CNAME记录
别名记录，记录一个主机的别名 MX记录 电子邮件交换记录，记录一个邮件域名对应的IP地址 NS记录 域名服务器记录 ,记录该域名由哪台域名服务器解析
PTR记录 反向记录，也即从IP地址到域名的一条记录 TXT记录 记录域名的相关文本信息

DNS信息收集-dnsrecon、fierce和dnsmap：

http://www.hetianlab.com/expc.do?ec=ECID172.19.104.182016012111000300001（通过该实验了解dnsrecon、fierce、dnsmap这三个工具的使用方法，并使用该工具对DNS服务器进行信息收集整理，了解并熟悉他们的常用参数意义。）复制链接做实验。

DNS注册信息

Whois查询

DNS域传送漏洞原理

DNS服务器分为：主服务器、备份服务器和缓存服务器。在主备服务器之间同步数据库，需要使用“DNS域传送”。域传送是指备份服务器从主服务器拷贝数据，并用得到的数据更新自身数据库。

若DNS服务器配置不当，可能导致攻击者获取某个域的所有记录。造成整个网络的拓扑结构泄露给潜在的攻击者，包括一些安全性较低的内部主机，如测试服务器。同时，黑客可以快速的判定出某个特定zone的所有主机，收集域信息，选择攻击目标，找出未使用的IP地址，绕过基于网络的访问控制。

## DNS域传送漏洞检测  

nslookup

基本过程

1) nslookup #进入交互式shell 2) server dns.xx.yy.zz #设定查询将要使用的DNS服务器 3) ls xx.yy.zz
#列出某个域中的所有域名 4) exit #退出

漏洞检验-不存在漏洞

> nslookup Server: lkwifi.cn Address: 192.168.68.1 *** lkwifi.cn can't find
> nslookup: Non-existent domain > server ss2.bjfu.edu.cn Default Server:
> ss2.bjfu.edu.cn Address: 202.204.112.67 > ls bjfu.edu.cn
> [ss2.bjfu.edu.cn]*** Can't list domain bjfu.edu.cn: Query refusedThe DNS
> server refused to transfer the zone bjfu.edu.cn to your computer. If thisis
> incorrect, check the zone transfer security settings for bjfu.edu.cn on the
> DNSserver at IP address 202.204.112.67.> exit

漏洞检验-存在漏洞

> nslookup > server dns1.xxx.edu.cn > ls xxx.edu.cn

![v2-5d576dbc2a7800e6973bf02ad8349085_hd.j](https://pic3.zhimg.com/80/v2-5d576dbc2a7800e6973bf02ad8349085_hd.jpg)

nmap

利用nmap漏洞检测脚本"dns-zone-transfer"进行检测

nmap --script dns-zone-transfer --script-args dns-zone-transfer.domain=xxx.edu.cn -p 53 -Pn dns.xxx.edu.cn

\--script dns-zone-transfer 表示加载nmap漏洞检测脚本dns-zone-transfer.nse，扩展名.nse可省略
\--script-args dns-zone-transfer.domain=xxx.edu.cn 向脚本传递参数，设置列出某个域中的所有域名 -p 53
设置扫描53端口 -Pn 设置通过Ping发现主机是否存活

![v2-e2268ab5173d5c1614152dd39992273d_hd.j](https://pic2.zhimg.com/80/v2-e2268ab5173d5c1614152dd39992273d_hd.jpg)

dig

使用说明 dig -h

漏洞测试

dig @dns.xxx.edu.cn axfr xxx.edu.cn

axfr 是q-type类型的一种: axfr类型是Authoritative Transfer的缩写，指请求传送某个区域的全部记录。

![v2-53019fdfd478d5a2fa1d53e0acc5bd41_hd.j](https://pic1.zhimg.com/80/v2-53019fdfd478d5a2fa1d53e0acc5bd41_hd.jpg)

## 查找真实IP  

如果挖掘的目标购买了CDN服务，可以直接ping目标的域名，但得到的并非真正的目标Web服务器，只是离我们最近的一台目标节点的CDN服务器，这就导致了我们没法直接得到目标的真实IP段范围。

## CDN简介  

CDN的全称是Content Delivery
Network，即内容分发网络。其基本思路是尽可能避开互联网上有可能影响数据传输速度和稳定性的瓶颈和环节，使内容传输的更快、更稳定。通过在网络各处放置节点服务器所构成的在现有的互联网基础之上的一层智能虚拟网络，CDN系统能够实时地根据网络流量和各节点的连接、负载状况以及到用户的距离和响应时间等综合信息将用户的请求重新导向离用户最近的服务节点上。

## 国内外CND  

国内常见CDN

阿里云 腾讯云 百度云 网宿科技(ChinanNet Center) 蓝汛 金山云 UCloud 网易云 世纪互联 七牛云 京东云等

国外常见CDN

Akamai(阿卡迈) Limelight Networks(简称LLNW) AWS Cloud(亚马逊) Google(谷歌) Comcast(康卡斯特)

## 判断目标是否存在CDN  

由于CDN需要代价，一般小企业很大几率不会存在CDN服务。

假如一些企业存在CDN服务，那该如何寻找其真实IP呢，往下看，常见几种手法

### Ping目标主域  

通常通过ping目标主域，观察域名的解析情况，以此来判断其是否使用了CDN

对京东和阿里还有一家电器企业进行ping测试，观察域名的解析情况，可以看到京东和阿里都采用了自家CDN，而那个电器企业没有CDN服务

C:\Users\Qftm>ping www.jd.com C:\Users\Qftm>ping www.alibaba.com
C:\Users\Qftm>ping www.dfle.com.cn

![v2-337c99ded92c8d8a3cd7878b723f9c86_hd.j](https://pic3.zhimg.com/80/v2-337c99ded92c8d8a3cd7878b723f9c86_hd.jpg)

Nslookup

不同DNS域名解析

不同DNS域名解析情况对比，判断其是否使用了CDN

不同DNS解析结果若不一样，很有可能存在CDN服务

C:\Users\Qftm>nslookup www.dfle.com.cn 8.8.8.8 C:\Users\Qftm>nslookup
www.dfle.com.cn 114.114.114.114

![v2-aa5377776d9d8b2e421c68065e2cc124_hd.j](https://pic1.zhimg.com/80/v2-aa5377776d9d8b2e421c68065e2cc124_hd.jpg)

λ Qftm >>>: nslookup www.baidu.com 8.8.8.8 λ Qftm >>>: nslookup www.baidu.com
114.114.114.114

![v2-162a5b74bfbb91df1e4e4e9d79619b54_hd.j](https://pic4.zhimg.com/80/v2-162a5b74bfbb91df1e4e4e9d79619b54_hd.jpg)

nslookup默认解析

若解析结果有多个，很有可能存在CDN，相反，若解析结果有一个，可能不存在CDN(不能肯定)

![v2-9211362ed8987e6e956ab219b748453c_hd.j](https://pic3.zhimg.com/80/v2-9211362ed8987e6e956ab219b748453c_hd.jpg)

全国Ping

利用全国多地区的ping服务器操作，然后对比每个地区ping出的IP结果，查看这些IP是否一致，
如果都是一样的，极有可能不存在CDN。如果IP大多不太一样或者规律性很强，可以尝试查询这些IP的归属地，判断是否存在CDN。

在线网址

Ping检测-站长工具 http://ping.chinaz.com/ 17CE https://www.17ce.com/ ipip
https://tools.ipip.net/newping.php (支持国内、国外)

### 站长工具  

测试目标：[www.jd.com](http://www.jd.com/)

![v2-6b03d225c5ba6e76a6a38f3c788d4a8d_hd.j](https://pic3.zhimg.com/80/v2-6b03d225c5ba6e76a6a38f3c788d4a8d_hd.jpg)

17CE

测试目标：[www.baidu.com](http://www.baidu.com/)

![v2-6f312e74f1398c8f845fd9dce49eeef7_hd.j](https://pic4.zhimg.com/80/v2-6f312e74f1398c8f845fd9dce49eeef7_hd.jpg)

IPIP

![v2-7061b2c555b72652e45f2be2bbcf6698_hd.j](https://pic3.zhimg.com/80/v2-7061b2c555b72652e45f2be2bbcf6698_hd.jpg)

工具查询

这里工具只能作为辅助，有一定误报的概率，只能作为参考

Cdnplanet

cdnplanet https://www.cdnplanet.com/tools/cdnfinder/ （查询可能比较慢）

![v2-c7a540793364bf264a4234752d965b86_hd.j](https://pic3.zhimg.com/80/v2-c7a540793364bf264a4234752d965b86_hd.jpg)

## 绕过CDN查找真实IP  

在确认了目标确实用了CDN以后，就需要绕过CDN寻找目标的真实IP，下面介绍一些常规的方法。

内部邮箱源

一般的邮件系统都在内部，没有经过CDN的解析，通过利用目标网站的邮箱注册、找回密码或者RSS订阅等功能，查看邮件、寻找邮件头中的邮件服务器域名IP，ping这个邮件服务器的域名,就可以获得目标的真实IP。

注意：必须是目标自己的邮件服务器，第三方或公共邮件服务器是没有用的。

![v2-b6eaf65899b47f89b15301f882464ede_hd.j](https://pic1.zhimg.com/80/v2-b6eaf65899b47f89b15301f882464ede_hd.jpg)

国外请求

很多时候国内的CDN对国外得覆盖面并不是很广，故此可以利用此特点进行探测。通过国外代理访问就能查看真实IP了，或者通过国外的DNS解析，可能就能得到真实的IP。

国际Ping

国际ping测试站点

ipip https://tools.ipip.net/newping.phpASM https://asm.ca.com/en/ping.php

测试站点：www.yeah.net

![v2-c0fe95d5819944fd1a747c2066eec9b9_hd.j](https://pic3.zhimg.com/80/v2-c0fe95d5819944fd1a747c2066eec9b9_hd.jpg)

### 国外DNS解析  

世界各地DNS服务器地址大全：http://www.ab173.com/dns/dns_world.php

测试站点：www.yeah.net

美国加利福尼亚州山景市谷歌公司DNS服务器： 8.8.4.4

![v2-5fa0c60defa8717d60a5919ce86a2050_hd.j](https://pic3.zhimg.com/80/v2-5fa0c60defa8717d60a5919ce86a2050_hd.jpg)

### 分站域名&C段查询  

很多网站主站的访问量会比较大，所以主站都是挂CDN的，但是分站可能没有挂CDN,可以通过ping二级域名获取分站IP，
可能会出现分站和主站不是同一个IP但在同一个C段下面的情况，从而能判断出目标的真实IP段。

### 分站域名  

具体见上面<收集子域名信息>部分

![v2-6e58ca4edbb8b3d54023dcc36ae6f600_hd.j](https://pic1.zhimg.com/80/v2-6e58ca4edbb8b3d54023dcc36ae6f600_hd.jpg)

### C段查询  

  * 在线查询  

![v2-dbc25ef715455c531a346f2c1cc24bf6_hd.j](https://pic4.zhimg.com/80/v2-dbc25ef715455c531a346f2c1cc24bf6_hd.jpg)

  * 工具  

K8_C段旁注工具6.0、nmap、IISPutScanner、小米范WEB查找器 等

小米范WEB查找器：http://pan.baidu.com/s/1pLjaQKF

![v2-bd839a6ba6cfd33605dd8ef81084acd3_hd.j](https://pic4.zhimg.com/80/v2-bd839a6ba6cfd33605dd8ef81084acd3_hd.jpg)

  * 网络资产搜索引擎  

Fofa、Shodan、ZoomEye

利用这些网络空间资产搜索引擎来搜索暴露在外的端口信息

利用语法搜索C段信息

![v2-8f24e419e9464c66e962e3a397994ee4_hd.j](https://pic3.zhimg.com/80/v2-8f24e419e9464c66e962e3a397994ee4_hd.jpg)

### 网站漏洞  

通过网站的信息泄露如phpinfo泄露，github信息泄露，命令执行等漏洞获取真实ip。

### 一些测试文件  

phpinfo、test等

![v2-6c6c786217f46c39e212adc943588b5c_hd.j](https://pic2.zhimg.com/80/v2-6c6c786217f46c39e212adc943588b5c_hd.jpg)

SSRF漏洞

服务器主动向外发起连接，找到真实IP地址

查询域名解析记录

一般网站从部署开始到使用cdn都有一个过程，周期如果较长的话
则可以通过这类历史解析记录查询等方式获取源站ip，查看IP与域名绑定的历史记录，可能会存在使用CDN前的记录。

在线网站查询

dnsdb https://www.dnsdb.io NETCRAFT https://sitereport.netcraft.com/?url=
viewdns https://viewdns.info /threatbook https://x.threatbook.cn/
securitytrails https://securitytrails.com/

![v2-1a117230cfd617bab82c4aee3f62a942_hd.j](https://pic2.zhimg.com/80/v2-1a117230cfd617bab82c4aee3f62a942_hd.jpg)

### 目标网站APP应用  

如果目标网站有自己的App，可以尝试利用Fiddler或Burp Suite抓取App的请求，从里面找到目标的真实IP。

### 网络空间引擎搜索  

shodan、FOFA、zoomeye

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

  

