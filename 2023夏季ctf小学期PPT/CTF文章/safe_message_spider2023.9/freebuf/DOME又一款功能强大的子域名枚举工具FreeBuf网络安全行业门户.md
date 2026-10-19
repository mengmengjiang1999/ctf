![](https://image.3001.net/images/20220318/1647615985_62349ff18e606160e82ff.jpeg!small)

## 关于DOME

DOME是一款功能强大的子域名枚举工具，该工具是一个快速可靠的Python脚本，可以实现主动或被动扫描，以搜索目标子域名以及开放的端口信息。该工具主要针对漏洞奖励Hunter以及渗透测试人员设计，可以在网络侦查和数据收集阶段使用。

## 功能介绍

> 1、易于使用，只需安装好requirements.txt中的依赖组件即可运行；
>
> 2、支持主动扫描和被动扫描模式；
>
> 3、比其他子域名枚举工具速度更快；
>
> 4、支持7种不同的解析器/域名服务器，其中包括Google、CloudFare（最快）、Quad9和Cisco
> DNS等（可以使用“--resolvers filename.txt”命令来使用自定义解析器列表）；
>
> 5、支持21种不同的OSINT源；
>
> 6、会对通过OSINT获取的子域名进行测试以确保为活动域名（仅主动模式）；
>
> 7、支持收集需要API令牌才可访问的网站；
>
> 8、支持检测API密钥何时失效；
>
> 9、通配符检测和绕过；
>
> 10、支持针对Top100、Top1000或Top Web端口进行自定义端口扫描和内置参数；
>
> 11、输出支持颜色高亮显示，便于阅读；
>
> 12、支持Windows和Python 2/3（推荐Python 3）；
>
> 13、支持通过参数进行高度定制；
>
> 14、支持同时扫描多个域；
>
> 15、使用了多线程机制提升暴力破解的速度；
>
> 16、支持以txt、json、html等不同格式导出输出；

## OSINT搜索引擎

DOME使用了下列Web资源来获取子域名信息：

 **不需要API：**

> AlienVault
>
> HackerTarget
>
> RapidDNS
>
> ThreatMiner
>
> urlscan.io
>
> threatcrowd.org
>
> web.archive.org
>
> crt.sh
>
> bufferover.run
>
> CertSpotter
>
> Anubis-DB
>
> Hunt.io
>
> Sonar
>
> SiteDossier
>
> DNSrepo

 **需要API：**

> VirusTotal
>
> Shodan
>
> Spyse
>
> SecurityTrails
>
> PassiveTotal
>
> BinaryEdge

提示：如果你想使用更多的OSINT引擎，可以通过“config.api”文件配置API令牌来进行添加。

## 工具安装

我们可以在Python 2或Python 3环境下安装和运行DOME，不过建议大家使用Python 3。

下列命令可以将该项目源码克隆至本地，并安装好工具所需的依赖组件，然后查看工具的帮助信息：

    
    
    git clone https://github.com/v4d1/Dome.git
    
    cd Dome
    
    pip install -r requirements.txt
    
    python dome.py --help

## 工具使用

### 被动模式

该工具主要基于OSINT技术来从目标获取子域名信息。这个模式并不会跟目标主机建立任何的连接，因此这种子域名扫描方式是不会被检测到的。该模式的基础使用方法如下：

    
    
    python dome.py -m passive -d domain

### 主动模式

该模式基于暴力破解技术来收集活动的子域名，该工具实现的爆破技术有以下两种类型：

> 1、纯暴力破解：检测范围从a.domain.com到zzz.domain.com（26 + 26^2 + 26^3 =
> 18278个子域名），该功能可以通过“-nb, --no-bruteforce”参数来禁用；
>
> 2、基于字典的暴力破解：通过“-w, --wordlist”选项来提供用户的自定义字典，如果不指定字典文件，则该模式无法运行。

该模式同样还会执行被动模式扫描，并会通过建立连接来确保目标子域名为活动状态。我们可以使用“--no-passive”选项来禁用主动扫描模式中的被动扫描。

 **主动模式扫描的基础使用：**

    
    
    python dome.py -m active -d domain -w wordlist.txt

 **添加“-p”选项或内置端口选项来执行端口扫描：**

    
    
    python dome.py -m active -d domain -w wordlist.txt -p 80,443,8080

## 工具使用样例

执行主动和被动扫描，显示每一个子域名的IP地址，使用端口源执行端口扫描，数据将会被写入至/results目录：

    
    
    python dome.py -m active -d domain -w wordlist.txt -i --top-web-ports -o

以静默模式执行被动扫描，并将结果输出至文件：

    
    
    python dome.py -m passive -d domain --silent --output

执行主动模式扫描（不执行被动模式）和端口扫描：

    
    
    python dome.py -m active -d domain -w wordlist.txt --no-passive

执行基于字典的暴力破解：

    
    
    python dome.py -m active -d domain -w wordlist.txt --no-bruteforce

执行主动扫描、被动扫描和端口扫描（仅22、80、3306）：

    
    
    python dome.py -m active -d domain -w wordlist.txt -p 22,80,3306

## 工具运行截图

![](https://image.3001.net/images/20220318/1647616136_6234a088bdbe11c9c2e1e.png!small)

![](https://image.3001.net/images/20220318/1647616145_6234a091523e118b97256.png!small)

### 被动模式

![](https://image.3001.net/images/20220318/1647616165_6234a0a5ce174456bfa49.png!small)

### 主动模式 + 端口扫描

![](https://image.3001.net/images/20220318/1647616173_6234a0ad749aadd87b995.png!small)

## 项目地址

 **DOME：** 【[ _GitHub传送门_](https://github.com/v4d1/Dome)】

## 参考资料

> [ _https://www.python.org/_](https://www.python.org/)
>
> [
> _https://publicsuffix.org/list/public_suffix_list.dat_](https://publicsuffix.org/list/public_suffix_list.dat)
>
> [ _https://spyse-dev.readme.io/reference/domain_search_](https://spyse-> dev.readme.io/reference/domain_search)

