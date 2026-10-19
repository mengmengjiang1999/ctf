![](https://image.3001.net/images/20230713/1689245451_64afd70b4eef4804867fb.png!small)

## 关于RTA

RTA全称为Red Team Arsenal，该工具是一款功能强大的企业网络资产安全漏洞扫描工具。

RTA是flipkart安全团队创建的一个内部框架，用于监控公司在线资产的外部攻击面，并提供关于任何安全异常的整体安全视图。它是一个由各种安全引擎和工具紧密整合的工具集，可以用于攻击模拟测试，并监控面向公众的资产是否存在异常和数据泄漏。

RTA是一个智能框架，可以检测所有Layer 7资产中的安全异常并报告异常情况。

## 支持的平台

RTA已经在Ubuntu/Debian（基于apt-get的发行版）发行版上进行了测试，它也可以与Mac OS一起使用（但如果你在Mac
OS上运行它，请用与系统架构匹配的程序二进制文件替换binaries文件夹中的内容）。

## 工具要求

该工具的正常运行还需要安装并配置下列环境：

> Python 3.8
>
> Python pip

接下来，我们还需要使用下列数据更新项目的配置文件和config_mail.yml文件：

> Google Chat Webhook URL地址
>
> SMTP凭证
>
> GitHub令牌
>
> 邮件列表
>
> 自定义搜索引擎API密钥

## 工具安装

首先，我们需要在本地设备上安装并配置好Python 3.8环境，并安装好pip工具：

    
    
    sudo apt-get install python3-pip

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/flipkart-incubator/RTA.git

下载完成后，我们就可以使用pip3命令和项目提供的requirements.txt文件来安装该工具所需的其他依赖组件：

    
    
    sudo pip3 install -r requirements.txt

## 工具使用

打开项目的'input_files/domains.txt'文件，在其中设置好需要监控的网络域名，然后运行下列命令即可使用RTA：

    
    
    python3 scheduler.py

### 配置Google Chat

我们还可以使用Google Chat来接收工具发送过来的通知消息，如需使用该功能，则需要在config.yml文件中添加Google Chat
Webhook URL地址。

## 工具输出样例

    
    
    a0xnirudh@exploitbox /RTA (master*) $ python rta.py --url "0daylabs.com" -v -s
    
     
    
                  ____          _   _____                         _                              _
    
                 |  _ \ ___  __| | |_   _|__  __ _ _ __ ___      / \   _ __ ___  ___ _ __   __ _| |
    
                 | |_) / _ \/ _` |   | |/ _ \/ _` | '_ ` _ \    / _ \ | '__/ __|/ _ \ '_ \ / _` | |
    
                 |  _ <  __/ (_| |   | |  __/ (_| | | | | | |  / ___ \| |  \__ \  __/ | | | (_| | |
    
                 |_| \_\___|\__,_|   |_|\___|\__,_|_| |_| |_| /_/   \_\_|  |___/\___|_| |_|\__,_|_|
    
     
    
     
    
    [i] Checking for Zonetransfer
    
    [i] Zone Transfer is not enabled
    
     
    
    [i] Checking for SPF records
    
    [+] SPF record lookups is good. Current value is: 9
    
     
    
    [-] Enumerating subdomains now for 0daylabs.com
    
    [-] Searching now in Baidu..
    
    [-] Searching now in Yahoo..
    
    [-] Searching now in Google..
    
    [-] Searching now in Bing..
    
    [-] Searching now in Ask..
    
    [-] Searching now in Netcraft..
    
    [-] Searching now in DNSdumpster..
    
    [-] Searching now in Virustotal..
    
    [-] Searching now in ThreatCrowd..
    
    [-] Searching now in SSL Certificates..
    
    [-] Searching now in PassiveDNS..
    
    [-] Total Unique Subdomains Found: 3
    
    blog.0daylabs.com
    
    www.0daylabs.com
    
    test.0daylabs.com
    
     
    
    [+] Verifying Subdomains and takeover options
    
     
    
    [+] Possible subdomain takeovers (Manual verification required):
    
     
    
     test.0daylabs.com
    
     
    
    [i] Verified and Analyzed Subdomains:
    
     
    
    [i] URL: blog.0daylabs.com
    
    [i] Wappalyzer: [u'jQuery', u'Varnish', u'Font Awesome', u'Twitter Bootstrap', u'Google Analytics', u'Google Font API', u'Disqus', u'Google AdSense']
    
     
    
    [i] Scraper Results
    
     
    
    [+] Shodan
    
    Hostname: test.0daylabs.com                 IP: 139.59.63.111       Ports: 179
    
    Hostname: test.0daylabs.com                 IP: 139.59.63.111       Ports: 179
    
     
    
    [+] Twitter
    
    URL: https://twitter.com/tweetrpersonal9/status/832624003751694340      search string: 0daylabs
    
    URL: https://twitter.com/ratokeshi/status/823957535564644355            search string: 0daylabs

## 项目地址

 **RTA** ：【[ _GitHub传送门_](https://github.com/flipkart-incubator/RTA)】

## 参考资料

> Amass: [_https://github.com/owasp-amass/amass_](https://github.com/owasp-> amass/amass)
>
> Aquatone:
> [_https://github.com/michenriksen/aquatone_](https://github.com/michenriksen/aquatone)
>
> Assetfinder:
> [_https://github.com/tomnomnom/assetfinder_](https://github.com/tomnomnom/assetfinder)
>
> Chaos-Client: [_https://github.com/projectdiscovery/chaos-> client_](https://github.com/projectdiscovery/chaos-client)
>
> Chrome Driver:
> [_https://chromedriver.chromium.org/downloads_](https://chromedriver.chromium.org/downloads)
>
> Ffuf: [_https://github.com/ffuf/ffuf_](https://github.com/ffuf/ffuf)
>
> Finddomain:
> [_https://github.com/Findomain/Findomain_](https://github.com/Findomain/Findomain)
>
> Gau: [_https://github.com/lc/gau_](https://github.com/lc/gau)
>
> Https:
> [_https://github.com/projectdiscovery/httpx_](https://github.com/projectdiscovery/httpx)
>
> Naabu:
> [_https://github.com/projectdiscovery/naabu_](https://github.com/projectdiscovery/naabu)
>
> Nmap: [_https://nmap.org/_](https://nmap.org/)
>
> Subfinder:
> [_https://github.com/projectdiscovery/subfinder_](https://github.com/projectdiscovery/subfinder)
>
> Scweet:
> [_https://pypi.org/project/Scweet/_](https://pypi.org/project/Scweet/)
>
> Cloud Enum:
> [_https://github.com/initstring/cloud_enum_](https://github.com/initstring/cloud_enum)
>
> DNStwist:
> [_https://github.com/elceef/dnstwist_](https://github.com/elceef/dnstwist)
>
> Phonebook: [_https://phonebook.cz/_](https://phonebook.cz/)
>
> SSLyze:
> [_https://github.com/nabla-c0d3/sslyze_](https://github.com/nabla-c0d3/sslyze)
>
> Shodan: [_https://shodan.io_](https://shodan.io)

