**Sudomy是一个使用bash脚本创建的子域枚举工具，用于快速全面地分析域和收集子域。**

##  特性

轻便，快速，功能强大。几乎所有的Linux发行版中都默认提供了Bash脚本。通过使用bash脚本的多进程处理功能，可以最佳地利用所有处理器。

子域枚举过程可以通过使用主动或被动方法来实现

**（1）主动方法**

Sudomy利用Gobuster工具，因为它在执行DNS Subdomain
Bruteforce攻击（支持通配符）时具有高速性能。使用的词汇表来自组合的SecList（Discover/DNS）列表，其中包含大约300万个条目

**（2）被动方法**

通过选择第三方站点可以优化枚举过程，节约大量时间并获得更多的结果。Sudomy可以从这16个第三方网站收集数据：

> <https://dnsdumpster.com>
>
> <https://web.archive.org>
>
> <https://shodan.io>
>
> <https://virustotal.com>
>
> <https://crt.sh>
>
> <https://www.binaryedge.io>
>
> <https://securitytrails.com>
>
> <https://sslmate.com/certspotter>
>
> <https://censys.io>
>
> <https://threatminer.org>
>
> <http://dns.bufferover.run>
>
> <https://hackertarget.com>
>
> <https://www.entrust.com/ct-search/>
>
> <https://www.threatcrowd.org>
>
> <https://riddler.io>
>
> <https://findsubdomains.com>

测试收集的子域列表并探测工作的http或https服务器。此功能使用第三方工具[httprobe](https://github.com/tomnomnom/httprobe)来完成。

基于Ping Sweep和/或获取的HTTP状态码测试子域可用性。

检测虚拟主机的能力（解析为单个IP地址的多个子域）。Sudomy会将收集的子域解析为IP地址，然后在多个子域解析为单个IP地址时对其进行分类。此功能对于下一次渗透测试/bug
bounty非常有用。例如，在端口扫描中，不会重复的扫描单个IP地址

从收集的子域/虚拟主机IP地址执行端口扫描

子域名接管攻击测试

子域截图

以HTML或CSV格式输出报告

##  Sudomy 是如何工作的？

Sudomy使用cURL库以从第三方站点获取HTTP响应主体，然后执行正则表达式获取子域。此过程充分利用了多处理器，将节约大量时间并获得更多的结果。

##  对比

以下是Sublist3r，Subfinder和Sudomy的被动枚举DNS测试的结果的对比。使用的域为bugcrowd.com。

![](https://image.3001.net/images/20190916/1568591471_5d7ece6fec01b.jpg!small)

Asciinema：

> [Subfinder](https://asciinema.org/a/260323)
>
> [Sudomy](https://asciinema.org/a/260324)
>
> [Sublist3r](https://asciinema.org/a/260325)

##  安装

目前，Sudomy包含了以下的扩展工具。有关应用的安装和使用说明请点击相应链接。

Tools  |  License  |  Info  
---|---|---  
[Gobuster](https://github.com/OJ/gobuster) |  Apache License 2.0  |  非强制性  
[httprobe](https://github.com/tomnomnom/httprobe/) |  Tom Hudson -  |  强制性  
[nmap](https://github.com/nmap/nmap) |  GNU General Public License v2.0  |
非强制性  
  
**依赖项**

    
    
    $ pip install -r requirements.txt

Sudomy需要[jq](https://stedolan.github.io/jq/download/)来运行和解析。有关jq的下载和安装[请参阅此处](https://stedolan.github.io/jq/download/)

    
    
    # Linux
    apt-get install jq nmap phantomjs
    # Mac
    brew cask install phantomjs
    brew install jq nmap

**如果你已准备好了Go环境，那么键入以下命令：**

    
    
    export GOPATH=$HOME/go
    export PATH=$PATH:$GOROOT/bin:$GOPATH/bin
    go get -u github.com/tomnomnom/httprobe
    go get -u github.com/OJ/gobuster

**从 Github 下载 Sudomy**

    
    
    # Clone this repository
    git clone --recursive https://github.com/screetsec/Sudomy.git
    # Go into the repository
    sudomy --help

##  在 Docker 容器中运行

    
    
    # Pull an image from DockerHub
    docker pull screetsec/sudomy:v1.1.0
    # Run an image, you can run the image on custom directory but you must copy/download config sudomy.api on current directory
    docker run -v "${PWD}/output:/usr/lib/sudomy/output" -v "${PWD}/sudomy.api:/usr/lib/sudomy/sudomy.api" -it --rm screetsec/sudomy:v1.1.0 [argument]

**安装后**

查询第三方网站之前需要API密钥，例如Shodan，Censys，SecurityTrails，Virustotal和BinaryEdge。

> API密钥设置可以在sudomy.api文件中完成。
    
    
    # Shodan
    # URL :  http://developer.shodan.io
    # Example :
    #      - SHODAN_API="VGhpc1M0bXBsZWwKVGhmcGxlbAo"
    SHODAN_API=""
    # Censys
    # URL : https://censys.io/register
    CENSYS_API=""
    CENSYS_SECRET=""
    # Virustotal
    # URL : https://www.virustotal.com/gui/
    VIRUSTOTAL=""
    # Binaryedge
    # URL : https://app.binaryedge.io/login
    BINARYEDGE=""
    # SecurityTrails
    # URL : https://securitytrails.com/
    SECURITY_TRAILS=""

##  使用

    
    
    ___         _ _  _
    / __|_  _ __| (_)(_)_ __ _  _
    \__ \ || / _  / __ \  ' \ || |
    |___/\_,_\__,_\____/_|_|_\_, |
                              |__/ v{1.1.0#dev} by @screetsec
    Sud⍥my - Fast Subdmain Enumeration and Analyzer
       http://github.com/screetsec/sudomy
    Usage: sud⍥my.sh [-h [--help]] [-s[--source]][-d[--domain=]]
    Example: sud⍥my.sh -d example.com
             sud⍥my.sh -s Shodan,VirusTotal -d example.com
             sud⍥my.sh -pS -rS -sC -nT -sS -d example.com
    Optional Arguments:
      -a,  --all		 Running all Enumeration, no nmap & gobuster
      -b,  --bruteforce	 Bruteforce Subdomain Using Gobuster (Wordlist: ALL Top SecList DNS)
      -d,  --domain		 domain of the website to scan
      -h,  --help		 show this help message
      -o,  --html		 Make report output into HTML
      -s,  --source		 Use source for Enumerate Subdomain
      -tO, --takeover	 Subdomain TakeOver Vulnerabilty Scanner
      -pS, --ping-sweep	 Check live host using methode Ping Sweep
      -rS, --resolver	 Convert domain lists to resolved IP lists without duplicates
      -sC, --status-code     Get status codes, response from domain list
      -nT, --nmap-top	 Port scanning with top-ports using nmap from domain list
      -sS, --screenshot	 Screenshots a list of website
      -nP, --no-passive	 Do not perform passive subdomain enumeration
           --no-probe	 Do not perform httprobe

将所有16个源和探针用于工作的http或https服务器：

    
    
    $ sudomy -d hackerone.com

使用其中一个源：

    
    
    $ sudomy -s shodan,dnsdumpster,webarchive -d hackerone.com

使用一个或多个插件：

    
    
    $ sudomy -pS -sC -sS -d hackerone.com

使用所有插件：测试主机状态，http/https状态码，子域名接管和屏幕截图

    
    
    $ sudomy --all -d hackerone.com

以HTML格式创建报告

    
    
    $ sudomy --all -d hackerone.com --html

HTML报告示例：

仪表板

![](https://image.3001.net/images/20190916/1568591424_5d7ece4070376.png!small)

报告

![](https://image.3001.net/images/20190916/1568591435_5d7ece4b6783b.png!small)

##  工具概述

> Youtube视频：点击[这里](http://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=DpXIBUtasn0)

##  感谢

> [Tom Hudson](https://github.com/tomnomnom/) \- Tomonomnom
>
> [OJ Reeves](https://github.com/OJ/) \- Gobuster
>
> [Thomas D Maaaaz](https://github.com/maaaaz) \- Webscreenshot
>
> [Daniel Miessler](https://github.com/danielmiessler/) \- SecList
>
> [EdOverflow](https://github.com/EdOverflow/) \- can-i-take-over-xyz
>
> [jerukitumanis](https://github.com/myugan) \- Docker Maintainer
>
> [NgeSEC](https://ngesec.id/) Community
>
> [Gauli(dot)Net](https://gauli.net/)
>
> [Bugcrowd](https://www.bugcrowd.com/) &
> [Hackerone](https://www.hackerone.com/)

***参考来源：[GitHub](https://github.com/Screetsec/Sudomy)，FB小编secist编译，转载请注明来自FreeBuf.COM**

  

