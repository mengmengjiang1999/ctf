****

**![Danger-zone
：一款可将域、IP和email地址关联并可视化输出的工具](https://image.3001.net/images/20180929/1538180247_5baec497379d4.png!small)**

**Danger-zone是一款可将域、IP 和email地址之间的数据关联，并可视化输出存储到Elasticsearch和JSON文件中。**

背景故事 ：<https://medium.com/@woj_ciech/osint-tool-for-visualizing-relationships-between-domains-ips-and-email-addresses-94377aa1f20a>

##  **特性**

> 根据给定的电子邮件关联域，并检查这些域查找其他关联电子邮件和IP。
>
> 检查域的IP和电子邮件，并查找其关联域。
>
> 从IP中提取域，并检查域查找其他关联IP和电子邮件。

##  **模块**

### Email：

> Trumail - 验证email地址 (<https://trumail.io/>)
>
> Whoxy - whois反查服务 (<https://whoxy.com/>) 需要密钥
>
> haveIbeenPwned - 检测账号是否泄露及泄露站点 (<https://haveibeenpwned.com/>)
>
> Username check - 检查社交网站上基于email地址的用户名 (<https://username-> availability.herokuapp.com/>)
>
> Google - Google查询

### IP：

> Geolocation - 地理定位IP (<https://extreme-ip-lookup.com/>)
>
> Threatcrowd - 有关IP信息 (<https://github.com/AlienVault-OTX/ApiV2>)
>
> VirusTotal - 有关IP信息 (<https://www.virustotal.com/>) 需要密钥

### Domain：

> TLD - 获取顶级域赞助商 (<https://raw.githubusercontent.com/mikewesthad/tld-> data/master/data/tlds.json>)
>
> Threatcrowd - 有关域的信息 (<https://github.com/AlienVault-OTX/ApiV2>)
>
> Whoxy - Whois服务 (<https://whoxy.com/>)
>
> Whois history - 有关域的历史信息 (<https://whoxy.com/>)
>
> Wayback Machine - 网站存档备份网站(<http://archive.org/>)
>
> VirusTotal - 有关域的信息 (<https://www.virustotal.com/>)

##  **设置 &配置**

    
    
    git clone
    pip install -r requirements.txt
    
    
    pip install Google-search-api

有关Elasticsearch设置请参考：<https://www.elastic.co/guide/en/elasticsearch/reference/current/_installation.html>

有关Kibana设置请参考：<https://www.elastic.co/guide/en/kibana/6.4/install.html>

编辑settings.json文件，并添加密钥和ElasticSearch信息：

    
    
    {
      "keys":{
        "whoxy": "xxx",
        "virustotal": "xxx"
      },
      "elastic":{
        "host":"127.0.0.1",
        "port":9200
      }
    }

###  **使用**

    
    
    python danger-zone.py -h
    usage: dangerzone.py [-h] [--email EMAIL] [--address ADDRESS] [--domain DOMAIN]
                   [--elasticsearch]
    
    Correlate data between domains, ips and email addresses and present it as a
    graph.
    
    optional arguments:
      -h, --help         显示帮助信息并退出
      --email EMAIL      Email 地址
      --address ADDRESS  IP 地址
      --domain DOMAIN    域名
      --elasticsearch    Elasticsearch 输出

###  **域检查示例**

    
    
    python danger-zone.py --domain example.net --elastic
    Successfully connected to ElasticSearch
    ----------------VirusTotal module---------------------------    [*] Domain was resolved to following IPs: 
    xxx.xxx.xxx.xxx on 2017-02-20 00:00:00
    [*] Saving output to Elasticsearch
    -------------------WhoIs history module---------------------    [*} Found 1 result(s)
    [*] Domain example.net was registered on 2017-02-15 in GoDaddy.com, LLC
    [*] Contact: 
    [REDACTED]
    [*] Name servers:
    ns47.domaincontrol.com
    ns48.domaincontrol.com
    ---    [*] Saving output to Elasticsearch
    .net is sponsored by VeriSign Global Registry Services
    [...]
    --------------------Threatcrowd module------------------------    Reputation of 0downcarleasedeals.com: no opinion
    [*] Domain was resolved to following IPs: 
    xxx.xxx.xxx.xxx
    xxx.xxx.xxx.xxx
    xxx.xxx.xxx.xxx
    [*] Saving output to Elasticsearch
    ----------------VirusTotal module---------------------------    API limitation, putting into sleep for 70 sec
    [*] Domain was resolved to following IPs: 
    xxx.xxx.xxx.xxx on 2017-09-28 00:00:00
    xxx.xxx.xxx.xxx on 2018-08-22 13:57:06
    xxx.xxx.xxx.xxx on 2018-09-21 00:28:27
    [*] Saving output to Elasticsearch
    -------------------WhoIs history module---------------------    [*} Found 1 result(s)
    [*] Domain example2.com was registered on 2017-01-24 in GoDaddy.com, LLC
    [*] Contact: 
    [REDACTED]
    [*] Name servers:
    ns47.domaincontrol.com
    ns48.domaincontrol.com
    ---    [*] Saving output to Elasticsearch
    [*] Saving graph to graph/20180920-185210-example.net.png
    Press Enter to quit...

##  **输出**

以下是生成的域和IP关联图（以fximperium[.]net为中心）：

![Danger-zone](https://image.3001.net/images/20180929/1538180285_5baec4bd0032f.png!small)

### Console

生成到控制台的报告信息会比保存文件的更详细。

其他信息包括Google搜索结果，用户名检查和HaveIBeenPwned模块。

重要的信息会在控制台中高亮显示，可以帮你更好的记忆和关联它们。

![Danger-zone](https://image.3001.net/images/20180929/1538180304_5baec4d00304c.png!small)

### Kibana

使用各个包含特定信息的模块名称创建索引。

![Danger-zone](https://image.3001.net/images/20180929/1538180330_5baec4ea4b439.png!small)

### JSON

创建结构如下：

![Danger-zone](https://image.3001.net/images/20180929/1538180344_5baec4f86c1df.png!small)

##  **限制**

我原本想添加更多的免费服务，但我发现大多数服务都需要收费。使用Danger-zone需要创建两个帐户，一个VirusTotal这是完全免费的，允许你每分钟发出4次请求。

Whoxy服务开始时也为我们提供了免费服务，但这已经足够我们使用的了。有个限制就是只能检查2-3
level，因为连接量过大图形将无法读取，但完整信息将被保存到JSON文件和ElasticSearch中。

 ** *参考来源：[github](https://github.com/woj-ciech/Danger-zone)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

