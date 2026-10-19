# 国密wget的用法指南

## 1.wget是什么

​ wget 是一个GNU开发的从网络上自动下载文件的自由工具，支持通过 HTTP、HTTPS、FTP 三个最常见的 TCP/IP协议 下载，并可以使用
HTTP 代理。“wget”这个名称来源于 “World Wide Web” 与 “get” 的结合。

![image](https://image.3001.net/images/20220812/1660286266_62f5f53a4c1fe5bb20718.png!small)

## 2.国密wget是什么

​
wget自身不支持国密SSL协议（TLCP）。国密SSL实验室（www.gmssl.cn）做了国密适配，生成了一个国密版wget，简称gmwget。gmwget可免费下载和使用。

![image](https://image.3001.net/images/20220812/1660286286_62f5f54e08e7929419cd2.png!small)

## 3.国密wget使用（单向国密SSL）

### 3.1 简单执行

    
    
    [root@206test ~]# ./gmwget 
    GM version 1.0.0 Ported by www.gmssl.cn
    GM options:
    --gmssl,             use TLCP protocol
    --certificate=FILE,  use sm2 sig pem cert
    --private-key=FILE,  use sm2 sig pem key
    --certificate2=FILE, use sm2 enc pem cert
    --private-key2=FILE, use sm2 enc pem key
    
    gmwget: missing URL
    Usage: gmwget [OPTION]... [URL]...
    
    Try `gmwget --help' for more options.
    

### 3.2 简单访问

    
    
    [root@206test ~]# ./gmwget --gmssl --no-check-certificate https://ebssec.boc.cn
    GM version 1.0.0 Ported by www.gmssl.cn
    GM options:
    --gmssl,             use TLCP protocol
    --certificate=FILE,  use sm2 sig pem cert
    --private-key=FILE,  use sm2 sig pem key
    --certificate2=FILE, use sm2 enc pem cert
    --private-key2=FILE, use sm2 enc pem key
    
    --2022-08-11 14:40:19--  https://ebssec.boc.cn/
    Resolving ebssec.boc.cn... 123.124.191.183
    Connecting to ebssec.boc.cn|123.124.191.183|:443... connected.
    WARNING: cannot verify ebssec.boc.cn's certificate, issued by ‘/C=CN/O=CFCA SM2 OCA1’:
      Unable to locally verify the issuer's authority.
    HTTP request sent, awaiting response... 200 OK
    Length: 156 [text/html]
    Saving to: ‘index.html.3’
    
    index.html.3                    100%[=========================================================>]     156  --.-KB/s   in 0s     
    
    2022-08-11 14:40:19 (33.0 MB/s) - ‘index.html’ saved [156/156]
    

注释：

1）--gmssl表示启用国密SSL

2）--no-check-certificate表示不验证服务端证书

### 3.3 验证证书

    
    
    [root@206test ~]# ./gmwget --gmssl --ca-certificate=boc.ca.pem https://ebssec.boc.cn
    GM version 1.0.0 Ported by www.gmssl.cn
    GM options:
    --gmssl,             use TLCP protocol
    --certificate=FILE,  use sm2 sig pem cert
    --private-key=FILE,  use sm2 sig pem key
    --certificate2=FILE, use sm2 enc pem cert
    --private-key2=FILE, use sm2 enc pem key
    
    --2022-08-11 14:41:06--  https://ebssec.boc.cn/
    Resolving ebssec.boc.cn... 112.64.122.183
    Connecting to ebssec.boc.cn|112.64.122.183|:443... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 156 [text/html]
    Saving to: ‘index.html.4’
    
    index.html.4                    100%[=========================================================>]     156  --.-KB/s   in 0s     
    
    2022-08-11 14:41:06 (33.6 MB/s) - ‘index.html’ saved [156/156]
    

注释：

1）--ca-certificate=FILE表示加载本地可信证书链

2）boc.ca.pem下载见后面“相关下载”

### 3.4 开启调试

    
    
    [root@206test ~]# ./gmwget --gmssl --no-check-certificate -d https://ebssec.boc.cn
    GM version 1.0.0 Ported by www.gmssl.cn
    GM options:
    --gmssl,             use TLCP protocol
    --certificate=FILE,  use sm2 sig pem cert
    --private-key=FILE,  use sm2 sig pem key
    --certificate2=FILE, use sm2 enc pem cert
    --private-key2=FILE, use sm2 enc pem key
    DEBUG output created by Wget 1.16 on linux-gnu.
    
    --2022-08-11 14:53:22--  https://ebssec.boc.cn/
    Resolving ebssec.boc.cn... 112.64.122.183
    Caching ebssec.boc.cn => 112.64.122.183
    Connecting to ebssec.boc.cn|112.64.122.183|:443... connected.
    Created socket 3.
    Releasing 0x000000000145a340 (new refcount 1).
    Initiating SSL handshake.
    Handshake successful; connected socket 3 to SSL handle 0x000000000145c180
    SSL connection using GMSSLv1.1/ECC-SM4-CBC-SM3
    certificate:
      subject: /C=CN/ST=\\xE5\\x8C\\x97\\xE4\\xBA\\xAC/L=\\xE5\\x8C\\x97\\xE4\\xBA\\xAC/O=\\xE4\\xB8\\xAD\\xE5\\x9B\\xBD\\xE9\\x93\\xB6\\xE8\\xA1\\x8C\\xE8\\x82\\xA1\\xE4\\xBB\\xBD\\xE6\\x9C\\x89\\xE9\\x99\\x90\\xE5\\x85\\xAC\\xE5\\x8F\\xB8/OU=Local RA/OU=SSL/CN=ebssec.boc.cn
      issuer:  /C=CN/O=CFCA SM2 OCA1
    WARNING: cannot verify ebssec.boc.cn's certificate, issued by ‘/C=CN/O=CFCA SM2 OCA1’:
      Unable to locally verify the issuer's authority.
    
    ---request begin---    GET / HTTP/1.1
    User-Agent: Wget/1.16 (linux-gnu)
    Accept: */*
    Host: ebssec.boc.cn
    Connection: Keep-Alive
    
    ---request end---    HTTP request sent, awaiting response... 
    ---response begin---    HTTP/1.1 200 OK
    Date: Thu, 11 Aug 2022 06:53:23 GMT
    Last-Modified: Sat, 27 Jun 2015 16:48:38 GMT
    Accept-Ranges: bytes
    Content-Length: 156
    Cache-Control: max-age=300
    Expires: Thu, 11 Aug 2022 06:58:23 GMT
    Vary: Accept-Encoding,User-Agent
    Keep-Alive: timeout=10, max=100
    Connection: Keep-Alive
    Content-Type: text/html
    
    ---response end---    200 OK
    Registered socket 3 for persistent reuse.
    Length: 156 [text/html]
    Saving to: ‘index.html.10’
    
    index.html.10                   100%[=========================================================>]     156  --.-KB/s   in 0s     
    
    2022-08-11 14:53:22 (51.5 MB/s) - ‘index.html’ saved [156/156]
    

注释：

1）-d可以看到SSL信息

2）可以看到协议GMSSLv1.1和算法 **ECC-SM4-CBC-SM3**

## 4.国密wget使用（双向国密SSL）

### 4.1生成用户国密双证书

![image](https://image.3001.net/images/20220812/1660286246_62f5f52619b084c8eed04.png!small)

### 4.2 使用用户国密双证书访问

    
    
    [root@206test ~]# ./gmwget --gmssl --no-check-certificate --certificate=./sm2.user1.sig.crt.pem --private-key=./sm2.user1.sig.key.pem --certificate2=./sm2.user1.enc.crt.pem --private-key2=./sm2.user1.enc.key.pem https://demo.gmssl.cn:1443
    GM version 1.0.0 Ported by www.gmssl.cn
    GM options:
    --gmssl,             use TLCP protocol
    --certificate=FILE,  use sm2 sig pem cert
    --private-key=FILE,  use sm2 sig pem key
    --certificate2=FILE, use sm2 enc pem cert
    --private-key2=FILE, use sm2 enc pem key
    
    --2022-08-11 14:55:47--  https://demo.gmssl.cn:1443/
    Resolving demo.gmssl.cn... 101.200.216.127
    Connecting to demo.gmssl.cn|101.200.216.127|:1443... connected.
    WARNING: cannot verify demo.gmssl.cn's certificate, issued by ‘/C=CN/O=GMSSL/OU=PKI/SM2/CN=MiddleCA for Test’:
      Unable to locally verify the issuer's authority.
    HTTP request sent, awaiting response... 200 
    Length: 1273 (1.2K) [text/html]
    Saving to: ‘index.html.11’
    
    index.html.11                            100%[=================================================================================>]   1.24K  --.-KB/s   in 0s     
    
    2022-08-11 14:55:48 (267 MB/s) - ‘index.html’ saved [1273/1273]
    

注释：

1） --certificate=FILE表示指定用户签名证书(pem格式)

2） --private-key=FILE表示指定用户签名私钥(pem格式)

3） --certificate2=FILE表示指定用户加密证书(pem格式)

4） --private-key2=FILE表示指定用户加密私钥(pem格式)

## 5.相关下载

  1. XP/Vista/Win7/Win10/Win11

https://www.gmssl.cn/gmssl/down/gmwget.exe

  2. CentOS 7/8 x86_64

https://www.gmssl.cn/gmssl/down/gmwget

  3. MacOS x86_64

https://www.gmssl.cn/gmssl/down/gmwget_macos_x64

  4. CA证书

https://www.gmssl.cn/gmssl/down/boc.ca.pem

## 6.联系与反馈

 **gmwget@gmssl.cn**

