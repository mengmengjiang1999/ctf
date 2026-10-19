![](https://image.3001.net/images/20191016/1571234977_5da724a17e059.png!small)

##  分析概述

**钓鱼网站的目标之一就是通过使用电子邮件、短信、社交媒体和即时通信App来诱导目标用户提供他们的个人敏感数据，例如个人身份信息、***数据和密码等等。在拿到这些数据之后，攻击者就可以用它们来访问目标用户的账号，并有可能给目标用户带来“毁灭性”的灾难。**

就在不久之前，Akamai的安全研究人员Larry
Cashdoller曾收到过一封网络钓鱼邮件，而这种类型的网络钓鱼邮件使用的技术非常新奇，它会尝试利用Google翻译来作为代理，并收集Larry
Cashdoller的Google以及Facebook凭证。Larry曾在【[这篇文章](https://blogs.akamai.com/sitr/2019/02/phishing-attacks-against-facebook-google-via-google-translate.html)】中对这项技术进行了分析，感兴趣的同学可以阅读了解。

根据Larry以及Akamai其他研究人员的分析成果，我们在这篇文章中将对一款名叫[Modlishka](https://github.com/drk1wi/Modlishka)的钓鱼工具进行分析。Modlishka是一款功能强大且灵活性非常高的反向代理，攻击者可以在网络钓鱼活动中使用该工具来辅助完成网络钓鱼攻击。它是一款开源工具，开发人员最初只是为了实现教育目的而开发了这款软件，以帮助渗透测试人员对网络钓鱼活动进行分析，并帮助社区提高对现代网络钓鱼技术以及策略的认知。但很明显，这种强大的工具也会为网络犯罪分子所用。

##  工具分析

虽然Modlishka最初仅是为了实现教育目的而开发的，它也足以给大家演示目前黑市上在售的网络钓鱼工具的强大功能。在大多数网络钓鱼攻击活动中，攻击者会尝试利用互联网主机的漏洞来安装钓鱼工具，并仿造出目标站点以欺骗用户，而这些伪造的站点可以帮助攻击者收**法用户的账号凭证以及敏感信息。

该工具的功能比一般的网络钓鱼工具要强大得多，因为它不需要使用网站模板，它主要通过在合法网站以及目标用户扮演代理的角色来实现攻击。

根据该工具主要开发人员Piotr Duszynski提供的信息，Modlishka旨在：

> 1、帮助渗透测试人员进行高效的网络钓鱼活动，并证明网络钓鱼攻击所能带来的安全风险。
>
> 2、突出当前双因素身份验证机制存在的安全缺陷，并促使社区研发新的安全解决方案。
>
> 3、提升整个社区对网络钓鱼技术和策略的认知。
>
> 4、可为其他需要使用全局反向代理的开源项目提供支持。

![](https://image.3001.net/images/20191016/1571234997_5da724b51e966.png!small)

上图显示了Modlishka针对启用了标准双因素身份验证机制的网站执行攻击的界面截图，我们使用了Google站点来进行概念验证PoC演示。

##  演示视频

开发人员还提供了一份演示视频，并在视频中使用了Modlishka来收集目标用户的凭证并伪造用户会话。在攻击过程中，攻击者的每一项活动看起来都是“合法”的，Modlishka作为用户与Google之间的流量代理，不过浏览器地址栏中的钓鱼域名URL还是“非法”的。

视频地址：【[点我观看](https://vimeo.com/308709275)】

根据该工具GitHub库提供的信息，Modlishka的功能包括：

> 1、支持大部分双因素身份验证机制；
>
> 2、无网站模板，工具在终端用户和真实网站之间以代理的形式存在；
>
> 3、JavaScript Payload注入；
>
> 4、将网站从所有的加密和安全Header中剔除；
>
> 5、用户凭证收集；
>
> 6、可在Web面板中显示收集到的用户凭证以及用户会话摘要；

##  工具安装

使用“go get”命令从该项目的GitHub库中源码克隆至本地：

    
    
    $ go get -u github.com/drk1wi/Modlishka

###  编译源码：

$ cd $GOPATH/src/github.com/drk1wi/Modlishka/

$ make

![](https://image.3001.net/images/20191016/1571235024_5da724d04a991.png!small)

###  工具运行：

    
    
    # ./dist/proxy -h
    
        Usage of ./dist/proxy:
    
          -cert string
    
            	base64 encoded TLS certificate
    
          -certKey string
    
            	base64 encoded TLS certificate key
    
          -certPool string
    
            	base64 encoded Certification Authority certificate
    
          -config string
    
            	JSON configuration file. Convenient instead of using command line switches.
    
          -controlCreds string
    
              Username and password to protect the credentials page.  user:pass format
    
          -controlURL string
    
              URL to view captured credentials and settings. (default "SayHello2Modlishka")
    
          -credParams string
    
              	Credential regexp with matching groups. e.g. : baase64(username_regex),baase64(password_regex)
    
          -debug
    
            	Print debug information
    
          -disableSecurity
    
            	Disable proxy security features like anti-SSRF. 'Here be dragons' - disable at your own risk.
    
          -dynamicMode
    
              	Enable dynamic mode for 'Client Domain Hooking'
    
          -forceHTTP
    
             	Strip all TLS from the traffic and proxy through HTTP only
    
          -forceHTTPS
    
             	Strip all clear-text from the traffic and proxy through HTTPS only
    
          -jsRules string
    
            	Comma separated list of URL patterns and JS base64 encoded payloads that will be injected - e.g.: target.tld:base64(alert(1)),..,etc
    
          -listeningAddress string
    
            	Listening address - e.g.: 0.0.0.0  (default "127.0.0.1")
    
          -log string
    
            	Local file to which fetched requests will be written (appended)
    
          -plugins string
    
            	Comma seperated list of enabled plugin names (default "all")
    
          -proxyAddress string
    
            Proxy that should be used (socks/https/http) - e.g.: [http://127.0.0.1:8080](http://127.0.0.1:8080/) 
    
          -proxyDomain string
    
            	Proxy domain name that will be used - e.g.: proxy.tld
    
          -postOnly
    
            	Log only HTTP POST requests
    
          -rules string
    
              	Comma separated list of 'string' patterns and their replacements - e.g.: base64(new):base64(old),base64(newer):base64(older)
    
          -target string
    
            	Target domain name  - e.g.: target.tld
    
          -targetRes string
    
            	Comma separated list of domains that were not translated automatically. Use this to force domain translation - e.g.: static.target.tld 
    
          -terminateTriggers string
    
            	Session termination: Comma separated list of URLs from target's origin which will trigger session termination
    
          -terminateUrl string
    
            	URL to which a client will be redirected after Session Termination rules trigger
    
          -trackingCookie string
    
            	Name of the HTTP cookie used to track the client (default "id")
    
          -trackingParam string
    
            	Name of the HTTP parameter used to track the client (default "id")

##  配置文件

该工具可以使用JSON配置文件来针对目标域名进行配置，该配置文件中包含的设置选项允许用户定义钓鱼域名、目标站点、日志文件和凭证设置等等。下面给出的是运行在本地回环IP地址的工具配置样本，目标域名为“
[https://target-victim-domain.com](https://target-victim-domain.com/)”：

![](https://image.3001.net/images/20191016/1571235048_5da724e81f8d3.png!small)

关于配置文件中的参数细节，可以参考【[这篇文档](https://github.com/drk1wi/Modlishka/wiki/How-to-use)】。

##  日志记录

收集到的用户凭证可以直接在工具代理的请求中实时查看到。除此之外，我们也可以通过访问日志文件来查看，其中也包括伪造的用户会话：

![](https://image.3001.net/images/20191016/1571235057_5da724f101891.png!small)

![](https://image.3001.net/images/20191016/1571235060_5da724f457da0.png!small)

##  项目地址

工具ZIP包下载：【[点我下载](https://github.com/drk1wi/modlishka/zipball/master)】

工具TAR包下载：【[点我下载](https://github.com/drk1wi/modlishka/tarball/master)】

Modlishka：【[GitHub传送门](https://github.com/drk1wi/Modlishka)】

##  缓解方案

Larry
Cashdollar建议广大用户，在操作任何邮件之前，请务必要花时间全面检查邮件的合法性以及安全性。除此之外，广大用户可以使用LastPass或1Password这样的密码管理工具来保存自己的凭证信息，这样可以防止浏览器直接将密码填写至钓鱼网站中。

##  参考资料

> 1、<https://www.owasp.org/index.php/Phishing>
>
> 2、<https://www.akamai.com/us/en/multimedia/documents/state-of-the-> internet/soti-security-financial-services-attack-economy-report-2019.pdf>
>
> 3、<https://learn.akamai.com/en-us/webhelp/enterprise-threat-> protector/enterprise-threat-> protector/GUID-4654BD70-9D3F-49AA-A06E-E4FED132A73F.html>
>
> 4、<https://blogs.akamai.com/>
>
> 5、<http://www.phishing.org/what-is-phishing>
>
> 6、<https://blogs.akamai.com/sitr/2019/02/phishing-attacks-against-facebook-> google-via-google-translate.html>
>
> 7、<https://www.akamai.com/us/en/resources/what-is-phishing.jsp>

 ***参考来源：[securityboulevard](https://securityboulevard.com/2019/10/phishing-tool-analysis-modlishka/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

