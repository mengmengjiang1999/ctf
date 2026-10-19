**今天给大家推荐的是一款名叫Spyse.Py的工具，它是一个Python API封装器和命令行客户端，专为托管在spyse.com上的工具而设计。**  

![1.png](https://image.3001.net/images/20190722/1563778535_5d355de792223.png!small)

Spyse是为互联网安全专业人员、公司和远程系统管理员、SSL/TLS加密证书提供商、数据中心和业务分析师开发的完整DAAS（数据即服务）解决方案。所有的Spyse在线解决方案都已主题服务的形式呈现，这些服务共同组成了一个具有信息收集、处理和聚合的平台。

该工具支持下列API：

> 1、[DNStable](https://dnstable.com/)
>
> 2、[FindSubdomains](https://findsubdomains.com/)
>
> 3、[CertDB](https://certdb.com/)
>
> 4、[ASlookup](https://aslookup.com/)
>
> 5、[PortMap](https://portmap.com/)
>
> 6、[DomainsDB](https://domainsdb.org/)

## 工具安装

    
    
    pip3 install spyse.py

## 工具更新

    
    
    pip3 install --no-cache-dir spyse.py

## 客户端使用

### 必选参数：

    
    
    -target

### 可选参数：

    
    
    -param
    
    -page
    
    -apikey
    
    --raw

## param参数介绍

Spyse允许我们搜索数据库中的IP地址、IP范围、域名和URL等数据。Param参数可以帮助指定用户输入参数的类型。比如说，针对“--domains-on-ip”的默认参数为“ip”，但是我们可以重写这个参数。

检测机制相对比较简单：

    
    
    # detect whether input is cidr or ip or searchquery (q)
    
    if "/" in args.target:
    
      param ="cidr"
    
    elif ":" in args.target:
    
      param ="q"
    
    else:
    
      param ="ip"

检测过程中的检测单位为函数，不同的函数需要用户提供不同的默认参数值。

参数列表：

    
    
    cidr
    
    domain
    
    ip
    
    page
    
    url
    
    hash
    
    q

## 使用搜索查询  

跟Shodan类似，Spyse同样允许我们使用搜索查询：

    
    
    spyse -target "org: Microsoft"--ssl-certificates

### 搜索子域名

    
    
    spyse -target xbox.com --subdomains

### 反向IP地址查询

    
    
    spyse -target 52.14.144.171 --domains-on-ip

### 搜索SSL证书

    
    
    spyse -target hotmail.com --ssl-certificates
    
    spyse -target "org: Microsoft"--ssl-certificates

### 获取所有的DNS记录

    
    
    spyse -target xbox.com --dns-all

### 手动重写参数

    
    
    spyse -target hackerone.com -param domain--subdomains

### 使用API密钥导航多个页面

    
    
    export SPYSEKEY="yourkeyhere"
    
    spyse -target xbox.com -apikey $SPYSEKEY -page 2---ssl-certificates

### 管道连接至JQ和Aquatone  

最初，当我决定编写这个客户端时，我主要关注的是命令行的灵活性，这就是为什么存在--raw选项的原因。现在，用户可以直接使用API返回的原始JSON数据了。

    
    
    spyse -target hackerone.com --dns-soa --raw | jq

演示视频：<https://asciinema.org/a/253602>

    
    
    spyse -target hackerone.com -param domain--subdomains --raw | aquatone

演示视频：<https://asciinema.org/a/253650>

### 其他选项：

    
    
    usage: spyse [-h] [-target TARGET] [-paramPARAM] [-page PAGE]
    
                [-apikey APIKEY] [--raw] [--dns-ptr] [--dns-soa] [--dns-mx]
    
                [--dns-aaaa] [--dns-ns] [--dns-a] [--dns-txt] [--dns-all]
    
                [--domains-with-same-ns] [--domains-using-as-mx]
    
                [--domains-on-ip] [--domains-with-same-mx]
    
                [--domains-using-as-ns] [--download-dns-aaaa]
    
                [--download-dns-soa] [--download-dns-ns] [--download-dns-ptr]
    
                 [--download-dns-mx] [--download-dns-a][--download-dns-txt]
    
                [--download-dns-all] [--ip-port-lookup]
    
                [--ip-port-lookup-aggregate] [--ssl-certificates] [--subdomains]
    
    Client for Spyse.com
    
    optional arguments:
    
      -h,--help            show this help messageand exit
    
      -targetTARGET        target
    
      -paramPARAM          parameter to use (ip,domain, cidr, url, hash)
    
      -pagePAGE            page
    
      -apikeyAPIKEY        set the api key
    
     --raw                 show rawjson
    
      --dns-ptr             show dns ptr records
    
     --dns-soa             show dns soarecords
    
     --dns-mx              show dns mxrecords
    
     --dns-aaaa            show dnsaaaa records
    
     --dns-ns              show dns nsrecords
    
     --dns-a               show dns a records
    
     --dns-txt             show dns txtrecords
    
     --dns-all             show all dnsrecords
    
     --domains-with-same-ns
    
                            show domains with samens
    
     --domains-using-as-mx
    
                            show domains using asmx
    
     --domains-on-ip       show domainson ip
    
     --domains-with-same-mx
    
                            show domains with samemx
    
     --domains-using-as-ns
    
                            show domains using asns
    
     --download-dns-aaaa   download dnsaaaa records
    
     --download-dns-soa    download dnssoa records
    
     --download-dns-ns     download dnsns records
    
     --download-dns-ptr    download dnsptr records
    
     --download-dns-mx     download dnsmx records
    
     --download-dns-a      download dnsa records
    
     --download-dns-txt    download dnstxt records
    
     --download-dns-all    download alldns records
    
     --ip-port-lookup      show ip portlookup
    
     --ip-port-lookup-aggregate
    
                            show ip port lookupaggregate
    
     --ssl-certificates    show sslcertificates associated with a target
    
     --subdomains          showsubdomains
    
    Usage: spyse -target hackerone.com --subdomains

## 代码库使用

### 无API密钥：

    
    
    from spyse import spyse
    
    s = spyse()
    
    subdomains = s.subdomains("xbox.com",param="domain")

### 有API密钥：

    
    
    from spyse import spyse
    
    # Using the API key allows us to go throughmultiple pages of results
    
    s = spyse('API_TOKEN_GOES_HERE')
    
    subdomains =s.subdomains_aggregate("xbox.com", param="domain", page=2)

### 使用CIDR搜索：

    
    
    from spyse import spyse
    
    s = spyse()
    
    results = s.domains_on_ip("172.217.1.0/24",param="cidr")

### 使用现有文件：

    
    
    from spyse import spyse
    
    s = spyse()
    
    results = []
    
    with open("domains.txt") as d:
    
        forline in d:
    
            #default value for param="domain", so we don't
    
            #need to specify here
    
            r= s.subdomains_aggregate(line)
    
           results.append(r)
    
    print(results)

## 可用方法

注：所有可用的方法都以在spyse的API文档中列出：【[API文档](https://api-doc.spyse.com/)】

    
    
    API_METHODS = {
    
       "DNS_PTR": "/dns-ptr",
    
       "DNS_SOA": "/dns-soa",
    
       "DNS_MX": "/dns-mx",
    
       "DNS_AAAA": "/dns-aaaa",
    
       "DNS_NS": "/dns-ns",
    
       "DNS_A": "/dns-a",
    
       "DNS_TXT": "/dns-txt",
    
       "domains_with_same_ns": "/domains-with-same-ns",
    
       "domains_using_as_mx": "/domains-using-as-mx",
    
       "domains_on_ip": "/domains-on-ip",
    
       "domains_with_same_mx": "/domains-with-same-mx",
    
       "domains_using_as_ns": "/domains-using-as-ns",
    
       "download_dns_aaaa": "/download-dns-aaaa",
    
       "download_dns_soa": "/download-dns-soa",
    
       "download_dns_ns": "/download-dns-ns",
    
        "download_dns_ptr":"/download-ns-ptr",
    
       "download_dns_mx": "/download-dns-mx",
    
       "download_dns_a": "/download-dns-a",
    
       "download_dns_txt": "/download-dns-txt",
    
       "download_domains_with_same_mx":"/download-domains-with-same-mx",
    
       "download_domains_on_ip": "/download-domains-on-ip",
    
       "download_domains_with_same_ns":"/download-domains-with-same-ns",
    
       "download_domains_using_as_ns":"/download-domains-using-as-ns",
    
       "download_domains_using_as_mx":"/download-domains-using-as-mx",
    
        "ip_port_lookup_aggregate":"/ip-port-lookup-aggregate",
    
       "ip_port_lookup": "/ip-port-lookup",
    
       "ssl_certificates": "/ssl-certificates",
    
       "ssl_certificate_raw": "/ssl-certificate-raw",
    
       "ssl_certificates_aggregate": "ssl-certificates-aggregate",
    
       "ssl_certificate": "/ssl-certificate",
    
       "ssl_certificate_public_key":"/ssl-certificate-public-key",
    
       "ssl_certificate_json": "/ssl-certificate-json",
    
       "subdomains": "/subdomains",
    
       "subdomains_aggregate": "/subdomains-aggregate",
    
       "domains_starts_with": "/domains-starts-with",
    
       "domains_starts_with_aggregate":"/domains-starts-with-aggregate"
    
      }

## 项目地址

> Spyse.py：【[GitHub传送门](https://github.com/zeropwn/spyse.py)】

 ***
参考来源：[zeropwn](https://github.com/zeropwn/spyse.py)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

