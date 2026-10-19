##
![a.jpg](https://image.3001.net/images/20190527/1558921182_5ceb3fdec2f7c.jpg!small)Machinae安全情报收集工具

**Machinae这款开源工具可以帮助广大研究人员从各个开放网站/feed收集跟网络安全有关的数据，例如IP地址、域名、URL、电子邮件地址、文件哈希和SSL指纹等等。该工具受到了[Automater](https://github.com/1aN0rmus/TekDefense-Automater)的启发，旨在从以下四个方面提升原工具的功能：**

1、 源代码：将Automater以Python 3进行重构，提升功能扩展性；

2、 配置：使用了可读性更强的配置格式-YAML；

3、 输入：支持JSON格式解析，需编写正则表达式；

4、 输出：支持额外的输出类型，包括JSON等可选项；

## 工具安装

大家可以使用pip3来安装Machinae：

    
    
    pip3 install machinae

或者，大家也可以直接从本项目的GitHub代码库上将代码克隆至本地：

    
    
    pip3 install git+https://github.com/HurricaneLabs/machinae.git

点击【[这里](https://github.com/HurricaneLabs/machinae/raw/master/machinae.yml)】获取最新版本的工具配置文件，并将其存入/etc/machinae.yml。

## 配置文件

Machinae提供了功能强大的配置整合系统，我们可以直接对系统默认配置文件machinae.yml进行修改来实现配置的更新，通过修改配置文件，我们可以实现整个系统环境中所有用户的配置修改。系统级配置文件位于项目当前目录下，可以使用MACHINAE_CONFIG环境变量来进行设置，或者直接在命令行中使用“-c”或“--config”来配置。当然了，如果你不想更新全局配置文件，你可以使用“--nomerge”选项来禁用该功能。

你可以在machinae.yml文件中进行下列设置来启用Fortinet Category站点：

    
    
    fortinet_classify:
    
    default: true  
    

或使用下列命令禁用类似Virus Total pDNS这样的站点：

    
    
    vt_ip:
    
      default: false
    
    vt_domain:
    
      default: false  
    

## 工具使用  

Machinae的使用跟Automater非常相似：

    
    
    usage:machinae [-h] [-c CONFIG] [--nomerge] [-d DELAY] [-f FILE] [-i INFILE] [-v]
                [-o {D,J,N,S}] [-O{ipv4,ipv6,fqdn,email,sslfp,hash,url}] [-q]
                [-s SITES] [-a AUTH] [-HHTTP_PROXY]
                [--dump-config | --detect-otype]
                ...  
    

1、 使用“-c/--config”和 “--nomerge”选项来查看命令细节；

2、 Machinae支持“-d/--delay”选项，这个跟Automater类似，但Machinae默认使用参数值为“0”。

3、 Machinae的输出由下列两个参数控制：

“-o“控制输出格式，可以使用下列命令实现控制：

（1）“N“为默认标准输出；

（2）“D“为默认标准输出格式，但“.”字符会被替换；

（3）“J“为JSON输出；

“-f/--file“指定输出文件的写入位置，默认“-”为stdout。

4、 Machinae还支持使用“-H”或“--http-proxy”命令行参数来设置HTTP代理。

## 数据源

Machinae支持以下数据来源（更多数据源正在添加中…）：

> IPVoid
>
> URLVoid
>
> URLUnshortener (<http://www.toolsvoid.com/unshorten-url>)
>
> Malc0de
>
> SANS
>
> FreeGeoIP(freegeoip.io)
>
> FortinetCategory
>
> VirusTotalpDNS (通过网络爬虫)
>
> VirusTotalpDNS (通过 JSONAPI)
>
> VirusTotalURL Report (通过 JSON API)
>
> VirusTotalFile Report (通过 JSON API)
>
> ReputationAuthority
>
> ThreatExpert
>
> VxVault
>
> ProjectHoneypot
>
> McAfee 威胁情报
>
> StopForumSpam
>
> CymruMHR
>
> ICSICertificate Notary
>
> TotalHash(默认禁用)
>
> DomainToolsParsed Whois (需要 API 密钥)
>
> DomainToolsReverse Whois (需要 API 密钥)
>
> DomainToolsReputation
>
> IPWHOIS (实用 RIRREST 接口)
>
> HackedIP
>
> MetadefenderCloud (需要 API 密钥)
>
> GreyNoise(需要 API 密钥)
>
> IBMXForce (需要 API 密钥)

## HTTP基础认证与配置

Machinae支持在目标站点的HTTP基础认证功能，广大用户可以实用“--auth/-a”参数来开启该功能。此时，我们将需要创建一个包含[用户凭证](https://www.kitploit.com/search/label/Credentials)的YAML文件，其中要填写网站的密钥和相应凭证信息，格式大致如下：

    
    
    passivetotal:['myemail@example.com', 'my_api_key']

在request配置域中，你还会看到如下格式的密钥：

    
    
    json:
      request:
        url: '...'
    auth: passivetotal  
    

其中，auth: passivetotal指的是认证配置文件中的密钥，通过命令行传递。

### 默认禁用的站点

下面这些是该工具禁用的站点：

> FortinetCategory (fortinet_classify)
>
> TelizeGeo IP (telize)
>
> TotalHash(totalhash_ip)
>
> DomainToolsParsed Whois (domaintools_parsed_whois)
>
> DomainToolsReverse Whois (domaintools_reverse_whois)
>
> DomainToolsReputation (domaintools_reputation)
>
> PassiveTotalPassive DNS (passivetotal_pdns)
>
> PassiveTotalWhois (passivetotal_whois)
>
> PassiveTotalSSL Certificate History (passivetotal_sslcert)
>
> PassiveTotalHost Attribute Components (passivetotal_components)
>
> PassiveTotalHost Attribute Trackers (passivetotal_trackers)
>
> MaxMindGeoIP2 Passive Insight (maxmind)
>
> FraudGuard(fraudguard)
>
> Shodan(shodan)
>
> HackedIP
>
> MetadefenderCloud (需要 API 密钥)
>
> GreyNoise(需要 API 密钥)
>
> IBMXForce (需要 API 密钥)

## 数据输出格式

Machinae默认支持三种数据输出格式，即“常规格式”、“字符转义模式”和“JSON格式”，我们计划在将来添加更多的工具输出格式。

### 项目地址

Machinae：【[GitHub传送门](https://github.com/HurricaneLabs/machinae)】

***参考来源：[machinae](https://github.com/HurricaneLabs/machinae)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

