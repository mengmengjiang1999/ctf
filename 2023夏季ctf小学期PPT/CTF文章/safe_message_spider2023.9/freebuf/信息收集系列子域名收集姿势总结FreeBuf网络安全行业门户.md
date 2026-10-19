## 概述

在渗透测试或SRC漏洞挖掘中，安全测试人员通常会得到一些域名资产。为了更好地进行渗透测试，通常都需要进行子域名收集。

> 为什么需要进行子域名收集？
>
>   1. 扩大资产范围，可以增加漏洞发现的概率
>
>   2. 众所周知，一般情况下主站的安全性可能相对较高，而一些不常用的子站或者上线不久的站点，可能安全方面的考虑还没有很周全，可能成为目标系统的脆弱点
>
>   3. 通常情况下，同一组织采用相同应用搭建多个服务的可能性很大，以及补丁的情况也可能大致相同，因此，存在相同漏洞的概率非常大
>
>

子域名收集通常分为两种方式，分别为被动收集和主动收集。

被动收集是指，在不与目标系统进行交互的情况下，通过第三方进行收集。这种方式有着明显的优势，因为不需要和目标系统进行交互，所以不会对目标系统造成任何影响，更不会触发任何安全产品的告警。

>  **被动子域名收集的方式：**
>
>   * 信息泄露
>
>   * 搜索引擎
>
>   * 网络空间测绘引擎
>
>   * 证书透明
>
>   * 第三方DNS服务
>
>   * AS 号码查询
>
>   * SAN 收集
>
>   * 使用公共数据集
>
>

主动收集是指，通过与目标系统进行交互，对子域名进行收集。因为需要和目标系统进行交互，很可能出现高频访问等情况，有触犯安全产品告警的风险。

>  **主动收集子域名的方式：**
>
>   * 字典枚举
>
>   * 置换扫描
>
>   * 域传送漏洞
>
>   * DNSSEC
>
>   * DNS缓存
>
>

## 被动子域名收集

### 信息泄露

  * corssdomain.xml  
跨站策略文件，主要是为web客户端(如Adobe Flash Player等)设置跨域处理数据的权限，里面可能包含部分域名信息。

  * Github 、Gitee等代码仓库中，可能有相关子域名的信息

  * 抓包分析获取，如一些静态资源的请求、一些APP或者小程序接口、邮件服务器等等

### 搜索引擎

常用的搜索引擎有Google和百度，基础的搜索语法：

    
    
    site:*.baidu.com
    

一般用作工具搜集的补充，也可以编写脚本进行批量操作

### 网络资产搜索引擎

> 常见的空间测绘引擎：
>
>   * [Shodan](https://exploits.shodan.io/welcome)
>
>   * [Zoomeye](https://www.zoomeye.org/)
>
>   * [Fofa](https://fofa.info/)
>
>

直接在搜索框使用语法进行搜素，基础语法：

    
    
    domain=Your_domain
    

也可以利用API进行搜索

    
    
    echo 'domain="baidu.com"' | base64 - | xargs -I{} curl "https://fofa.info/api/v1/search/all?email=${Your_Mail}&key=${Your_Key}&page=1&qbase64={}"
    

再编写个脚本，对返回的数据进行简单的处理，即可获得一个子域名列表。

    
    
    import requests
    from base64 import b64encode
    import json
    
    
    # 配置信息
    domain = 'domain="baidu.com"'
    domain = str(b64encode(domain.encode("utf-8")), "utf-8")
    email = "Your_email"
    key = "Your_key"
    # end
    url = "https://fofa.info/api/v1/search/all?email={email}&key={key}&qbase64={domain}".format(email=email, key=key, domain=domain) + "&page={page}"
    page = 1
    subdomain = list()
    
    while True:
    	url = url.format(page=str(page))
    	req = requests.get(url=url).text
    	result = json.loads(req)['results']
    	if result:
    		tmp = [i[0] for i in result]
    		subdomain += tmp
    	else:
    		break
    	page += 1
    print(set(subdomain))		# 去重
    

> 注：这里的代码仅仅是展现处理的逻辑，暂未考虑优化处理，师傅们轻喷~

### 第三方DNS服务

#### [VirusTotal](https://www.virustotal.com/gui/home/search)

> VirusTotal会运行DNS复制功能，通过存储用户访问URL时执行的DNS解析来构建数据库。

![](https://image.3001.net/images/20220413/1649857546_6256d40a2ea87243bc8f1.jpg!small)

![](https://image.3001.net/images/20220413/1649857547_6256d40b1fb642760c520.jpg!small)

![](https://image.3001.net/images/20220413/1649857548_6256d40c43a18b739c1b7.jpg!small)

> 其他在线DNS工具汇总：
>
>   * https://decoder.link/
>
>   * https://searchdns.netcraft.com/
>
>   * https://dnsdumpster.com/
>
>   * https://pentest-tools.com/information-gathering/find-subdomains-of-> domain
>
>   * https://www.pkey.in/tools-i/search-subdomains
>
>   * https://hackertarget.com/find-dns-host-records/
>
>   * https://findsubdomains.com/
>
>   * https://spyse.com/
>
>

### 证书透明

  * 证书  
当通过HTTPS访问web时，网站向浏览器提供数字证书，此证书用于识别网站的主机名，由证书颁发机构(CA,Certificate Authority)颁发。

  * 证书透明  
证书透明（CT）是证书颁发机构（CA）必须将其发布的每个SSL/TLS证书发布到公共日志的项目。SSL/TLS证书通常包含域名，子域名和电子邮件地址等信息。

> 常用证书透明查询网站
>
>   * censys：https://censys.io/certificates
>
>   * crtsh：https://crt.sh/
>
>   * spyse：https://spyse.com/search/certificate
>
>   * certspotter：https://sslmate.com/certspotter/api/
>
>   * entrust：https://www.entrust.com/ct-search/
>
>   * facebook：https://developers.facebook.com/tools/ct
>
>   * google：https://developers.facebook.com/tools/ct
>
>

使用也是比较简单，直接搜索主域名即可。因为这种方法的原理是根据日志信息收集，只增不减，所以可能会出现一些失效的子域名。

### ASN

> AS 号码帮助识别属于组织的网络块，而该网络快又可能具有有效域

  1. 查找ASN

    * 基于IP查找：https://asn.cymru.com/cgi-bin/whois.cgi

    * 基于域名查找：https://bgp.he.net/  
![](https://image.3001.net/images/20220413/1649857549_6256d40dc4cc22b242592.jpg!small)

  2. 使用nmap进行查找

    
    
    nmap --script targets-asn --script-args targets-asn.asn=Your_asn > netblocks.txt
    

像fofa这类的网络空间测绘引擎也支持ASN查找

### SAN

SAN(Subject Alternative Name) 是 SSL 标准 x509 中定义的一个扩展。使用了 SAN 字段的 SSL
证书，可以扩展此证书支持的域名，使得一个证书可以支持多个不同域名的解析。

允许在安全证书中使用 `subjectAltName`字段将多种值与证书关联，这些值被称为主题备用名称。名称可包括：IP地址、DNS名称等。

这里用火狐浏览器作为例子：

![](https://image.3001.net/images/20220413/1649857550_6256d40ebc6b62bf6cb96.jpg!small)

![](https://image.3001.net/images/20220413/1649857551_6256d40f93dd79a6cf67e.jpg!small)

![](https://image.3001.net/images/20220413/1649857552_6256d41084343ff0c2b95.jpg!small)

![](https://image.3001.net/images/20220413/1649857553_6256d41155f7c4a880b96.jpg!small)

也可以使用 appsecco 提供的shell脚本：

    
    
    sed -ne 's/^\( *\)Subject:/\1/p;/X509v3 Subject Alternative Name/{
      N;s/^.*\n//;:a;s/^\( *\)\(.*\), /\1\2\n\1/;ta;p;q; }' < <(
      openssl x509 -noout -text -in <(
          openssl s_client -ign_eof 2>/dev/null <<<$'HEAD / HTTP/1.0\r\n\r' \
              -connect baidu.com:443 ) )
    

### 公开数据集

利用已有公开的扫描数据集，对子域名信息进行收集。推荐常用的两个：

> https://scans.io/study/sonar.rdns_v2  
> https://opendata.rapid7.com/

通常这些数据集都是比较大，可以使用命令进行快速查找

    
    
    wget https://scans.io/data/rapid7/sonar.fdns_v2/20170417-fdns.json.gz
    cat 20170417-fdns.json.gz | pigz -dc | grep ".Your_Target.org" | jq
    

## 主动子域名收集

### 字典枚举

字典枚举即利用常见的子域名字典，进行暴力破击，最终获得有效的子域名。这种方法有比较大的局限，能收集到多少子域，取决于字典的覆盖程度，同时还有比较致命的缺点，即会造成较大的流量，可能会让目标系统的安全产品造成告警。

常用工具：

  * [Aquatone](https://github.com/michenriksen/aquatone)

  * [Bluto-Old](https://github.com/darryllane/Bluto-Old)

  * [DNS-Discovery](https://github.com/m0nad/DNS-Discovery)

  * [Dnssearch](https://github.com/evilsocket/dnssearch)

  * [Amass](https://github.com/OWASP/Amass)

  * [Subbrute](https://github.com/TheRook/subbrute)

  * [subDomainBrute](https://github.com/lijiejie/subDomainsBrute)

  * [Sublist3r](https://github.com/aboul3la/Sublist3r)

  * [OneForAll](https://github.com/shmilylty/OneForAll)

  * [DNSBrute](https://github.com/Q2h1Cg/dnsbrute)

> 部分工具可能长时间没更新，字典可能比较老旧，可以根据需求修改成自己的字典

### 置换扫描

使用已知域/子域名的排列组合来识别新的子域名，使得字典有一定的针对性，提高准确率

比较常用的工具是 [altdns](https://github.com/infosec-au/altdns)（具体的工具使用见下一节）

### 域传送漏洞

DNS区域传输是将DNS数据库或DNS记录从主名称服务器复制到辅助名称服务器的过程。如果DNS服务器没有进行严格的配置，只要收到AXFR请求就进行域传送，便造成了该漏洞。域传送过程中，传递的信息除了子域外，还有电子邮件地址、电子邮件服务器等信息，可用于钓鱼攻击。其实，域传送漏洞本身就是一个高危漏洞。

域传送漏洞的即常见验证方式：

#### nslookup

    
    
    # 1.nslookup命令进入交互式shell
    $ nslookup
    
    # 2.server命令 参数设定查询将要使用的DNS服务器
    $ server xxx.com
    
    # 3.如果漏洞存在的话，可以使用ls命令列出所有域名
    $ ls
    
    # 4.退出
    $ exit
    

#### dig

在Linux下，可以使用dig命令来发送DNS请求，这里只需要发送axfr类型的DNS请求，如果存在该漏洞，则会返回所有解析记录。

    
    
    dig @Target_DNS_Server_IP axfr 查询的域名
    

#### dnswalk

在Kali中已经预装的工具，这里需要注意的是，要使用域名的完整形式，即 `.`不能省略

    
    
    dnswalk your_domain.
    

#### nmap

namap 中也有域传送漏洞的检测脚本：

    
    
    nmap --script dns-zone-transfer --script-args dns-zone-transfer.domain=Your_domain -p 53 -Pn dns.xxx.yyy.com
    

### DNSSEC

DNSSEC，即域名系统安全扩展，主要功能是通过建立信任链来保护DNS中数据的完整性和真实性。由于DNSSEC处理不存在域名的方式，可以遍历DNSSEC域并枚举该域中的所有域名

常用的工具：

  * ldns-walk  
可以使用 apt-get 安装

    
    
    apt-get install ldnsutils
    

  * [nsec3walker](https://dnscurve.org/nsec3walker.html)

  * [nsec3map](https://github.com/anonion0/nsec3map)

### DNS缓存

在常见的企业网络中，通常都会配置DNS服务器，为网络内的主机提供域名解析服务。DNS服务器除了解析私有域名外，还会用递归方式，向公网的DNS服务器请求解析第三方域名。为了提升性能，通常会使用缓存记录，记录解析过的域名，尤其是第三方域名。  
域名缓存侦测（DNS Cache
Snooping）技术就是向这些服务器发送域名解析请求，但要求不使用递归模式。这样DNS只能解析私有域名和缓存中保存的域名。借助该项技术，渗透测试人员就知道哪些域名是否被过请求过。

    
    
    ./dnsrecon.py -t snoop -n Sever -D <Dict>
    

## 自动化工具

### OneForAll

>
> OneForAll是一款比较综合的子域名扫描工具，拥有多个模块和接口扫描，收集子域信息很全，包括子域、子域IP、子域常用端口、子域Title、子域Banner、子域状态等。

  * [Download](https://github.com/shmilylty/OneForAll)

  * 使用  
这里用Docker方式演示

    
    
    git clone https://gitee.com/shmilylty/OneForAll.git
    docker pull shmilylty/oneforall
    docker run -it --rm -v ~/results:/OneForAll/results -v ~/OneForAll/config:/OneForAll/config shmilylty/oneforall --target baidu.com run
    

>   * 扫描结果路径：~/results
>
>   * 置文件路径：~/OneForAll/config
>
>   * 目标域名：baidu.com
>
>

### ksubdomain

>
> ksubdomain是一款基于无状态子域名爆破工具，支持在Windows/Linux/Mac上使用，它会很快的进行DNS爆破，在Mac和Windows上理论最大发包速度在30w/s,linux上为160w/s的速度。
>
> TIPS：在linux下，还需要安装`libpcap-dev`,在Windows下需要安装`WinPcap`，mac下可以直接使用。

  * [Download](https://github.com/knownsec/ksubdomain/releases)

  * 使用

    
    
    # 使用内置字典爆破
    ksubdomain -d baidu.com
    
    # 使用字典爆破域名
    ksubdomain -d baidu.com -f subdomains.dict
    
    # 字典里都是域名，可使用验证模式
    ksubdomain -f dns.txt -verify
    
    # 爆破三级域名
    ksubdomain -d baidu.com -l 2
    

### Sublist3r

> Sublist3r使用许多搜索引擎（如Google，Yahoo，Bing，Baidu和Ask）进行子域名探测。
>
> Sublist3r还使用Netcraft，Virustotal，ThreatCrowd，DNSdumpster和ReverseDNS进行子域名探测。

  * [Download](https://github.com/aboul3la/Sublist3r)

  * 使用

    
    
    python sublist3r.py -b -d baidu.com
    

> -d -domain要枚举子域的域名
>
> -b -bruteforce启用subbrute bruteforce模块
>
> -p -ports根据特定的tcp端口扫描找到的子域
>
> -v --verbose启用详细模式并实时显示结果
>
> -t -threads用于subbrute bruteforce的线程数
>
> -e - 引擎指定逗号分隔的搜索引擎列表
>
> -o -output将结果保存到文本文件
>
> -h -help显示帮助信息并退出

### altdns

>
> Altdns是一款运用置换扫描技术的子域发现工具，它可以帮助我们查找与某些排列或替换匹配的子域。AltDNS接受可能存在于域下的子域中的单词(例如测试，开发，分期)，以及获取你知道的子域列表。
>
> 使用者只需提供两个输入列表，altdns就可以为我们生成输出大量可能存在的潜在子域并保存。这些保存好的子域列表，用作DNS爆破字典是个不错的选择。

  * [Download](https://github.com/infosec-au/altdns)

  * 使用

    
    
    python altdns.py -i subdomains.txt -o data_output -w words.txt -r -s results_output.txt
    

>   * subdomains.txt 文件包含了目标的已知子域
>
>   * data_output文件将包含大量的更改和置换的子域列表
>
>   * words.txt是需要置换子域的单词列表（即admin，staging，dev，qa）- 单词以行分隔
>
>   * results_output.txt 将包含被发现有效的且具有DNS记录的排列后子域的最终列表。
>
>   * -r命令解析每个生成的已排列的子域
>
>   * -s命令用于指定altdns在哪保存已解析的排列子域结果。
>
>   * -t命令用于指定解析器同时使用的线程数
>
>

当然，优秀的工具还有许多，这里仅仅是举了几个我个人觉得比较常用工具的使用方法。只有合理地使用，才能把工具的作用发挥到最大。常见的工具还有：

  * [Aquatone](https://github.com/michenriksen/aquatone)

  * [Bluto-Old](https://github.com/darryllane/Bluto-Old)

  * [DNS-Discovery](https://github.com/m0nad/DNS-Discovery)

  * [Dnssearch](https://github.com/evilsocket/dnssearch)

  * [Amass](https://github.com/OWASP/Amass)

  * [Subbrute](https://github.com/TheRook/subbrute)

  * [subDomainBrute](https://github.com/lijiejie/subDomainsBrute)

  * [Sublist3r](https://github.com/aboul3la/Sublist3r)

  * [OneForAll](https://github.com/shmilylty/OneForAll)

  * [DNSBrute](https://github.com/Q2h1Cg/dnsbrute)

  * [Layer](https://github.com/euphrat1ca/LayerDomainFinder)

  * ……

## 总结

在渗透测试中，介于项目的周期，大部分测试人员都是使用自动化工具进行收集。然而，当对于已经收集到的资产束手无策时，尝试多种手段进一步扩大资产的范围也不失为一种方法。因此，本文较为系统地整理了一些常见的收集方法，希望对各位师傅有所帮助~

## 声明

  1. 本文初衷为分享网络安全知识，请勿利用技术做出任何危害网络安全的行为，由于传播、利用此文所提供的信息而造成的任何直接或者间接的后果及损失，均由 **使用者** 本人负责，与SpaceSec安全团队及作者无关！

  2. 文章中部分学习内容来自于网络，回馈予网络，如涉及版权问题，请联系删除。

  3. SpaceSec 保留对文章绝对的解释权，转载与传播时须保证文章的完整性，同时标明出处。未经允许，禁止转载或用于商业用途。

## 参考

https://www.freebuf.com/sectool/162774.html

https://www.freebuf.com/articles/web/260743.html

https://www.freebuf.com/articles/web/220344.html

