Nginx安全性分析

影响版本：0.5.6-1.13.2

漏洞危害：敏感信息泄露

 **HTTP-Range**

HTTP的Range 允许客户端分批次请求资源的一部分，如果服务端资源较大，可以通过Range来并发下载;如果访问资源时网络中断，可以断点续传。

Range 设置在HTTP请求头中，它是多个`byte-range-spec`(或`suffix-byte-range-spec`)的集合。

    
    
    byte-range-set = ( byte-range-spec | suffix-byte-range-spec)*N  
    byte-range-spec = first-byte-pos "-" [last-byte-pos]  
    suffix-byte-range-spec = "-" suffix-length

其中∶

  * `first-bytes-pos`指定了访问的第一个字节，

  * `last-byte-pos`指定了最后一个字节，

  * `suffix-length`则表示要访问资源的最后`suffix-length`个字节的内容，

  * `Range:bytes=O-1024`表示访问第0到第1024字节，

  * `Range:bytes=500-600`，`601-999`，`-300`表示分三块访问，分别是500到600字节，601到600字节，以及最后的300字节。

如果一次请求有多次range，需要`multipart`来组织

    
    
    HTTP/1.1 206 Partial Content  
    Date: Wed, 15 Nov 1995 06:25:24 GMT  
    Last-Modified: Wed, 15 Nov 1995 04:58:08 GMT  
    Content-type: multipart/byteranges;boundary=THIS_STRING_SEPARATES  
    ......  
    Content-type: application/pdf  
    Content-range: bytes 500-999/8000  
    ......  
    Content-type: application/pdf  
    Content-range: bytes 7000-7999/8000

利用`multipart`进行分片

> 对于普通文件来说，`Range`的开始和结束并不会有什么影响，因为服务器返回的就是完整文件的一部分，但是缓存文件不同，它和普通的文件相比
> **额外拥有一个文件头** ，里面保存了一些 **服务器的配置信息**
> （正常情况下服务器是不会返回缓存文件头部的）。所以，当我们针对一个缓存文件进行请求时，如果可以绕过服务器限制，使缓存文件被完整的返回，这时只要控制`Range`的起始字节为一个合理的负值，就可以读到缓存文件头部。

 **HTTP-Cache**

Nginx可以作为缓存服务器，将Web应用服务器返回的内容缓存起来。如果客户端请求的内容已经被缓存，那么就可以直接将缓存内容返回，而无需再次请求应用服务器。由此，可降低应用服务器的负载，并提高服务的响应性能。

![NGINX
中的缓存策略](https://image.3001.net/images/20220620/1655725530_62b05ddab6a1df1ef30cb.png!small)

Nginx对Range 的支持包括`header`处理和`body`处理，分别用来解析客户端发送过来的`Range
header`和裁剪返回给客户端的请求数据Body。`ngx_http_range_header_filter_module`——负责对`header`数据的处理`ngx_http_range_body_filter_module`——负责对`body`数据的处理

## 漏洞原理分析

> [漏洞文件
> ngx_http_range_filter_module.c](https://github.com/nginx/nginx/blob/release-1.12.0/src/http/modules/ngx_http_range_filter_module.c)

在header中range的解析过程

![image-20220615220120448](https://image.3001.net/images/20220620/1655725531_62b05ddbd258b2e53eaa3.png!small)

在`ngx_http_range_parse`函数中有这样一个循环，
这段代码是要把`“-”`两边的数字取出分别赋值给`start`和`end`变量，字符串指针`p`中即为`bytes=`后面的内容

    
    
    //部分源码如下  
    cutoff = NGX_MAX_OFF_T_VALUE / 10;  
    cutlim = NGX_MAX_OFF_T_VALUE % 10;  
    ​  
    for(;;)  
    {  
    start=0;  
    end=0;  
    suffix=0;  
    //...  
    while(*p == ' ') { p++; }  
      
    if (*p != '-')  
    {  
    if (*p < '0' || *p > '9')   
    {  
    return NGX_RANGENOT_SATISFIABLE;  
    }  
      
    while (*p >= '0' && *p <= '9')   
    {  
    if (start >= cutoff && (start > cutoff || *p - '0' > cutlim))   
    {  
    return NGX_RANGENOT_SATISFIABLE;  
    }  
      
    start = start * 10 + *p++ - '0';  // 更新start  
    }  
      
    while (*p == ' ') { p++; }  
      
    if (*p++ != '-')   
    {  
    return NGX_RANGENOT_SATISFIABLE;  
    }  
      
    while (*p == ' ') { p++; }  
      
    if (*p == ','  || *p == '\0')   
    {  
    end = content_length;  // 对end做更新  
    goto found;  
    }  
      
    }else{  
    suffix = 1;  
    p++;  
    }  
    //...  
    if (suffix)  
    {  
    start = content_length - end;   // 第一次byte以“-end”格式传入时，end=0，start = content_length  
    end = content_length - 1;       // start > end 不会进入found  
    }  
    //...  
    found:  
    ​  
    if (start < end)   
    {  
    range = ngx_array_push(&ctx->ranges);  
    if (range == NULL)   
    {  
    return NGX_ERROR;  
    }  
    ​  
    range->start = start;  
    range->end = end;  
    ​  
    size += end - start;  
    ​  
    if (ranges-- == 0)   
    {  
    return NGX_DECLINED;  
    }  
    }  
      
    if (*p++ != ',')  
    {  
    break;  
    }  
    }  
    //...  
    if (size > content_length)  
    {  
    return NGX_DELINED;  
    }  
    //...

在该段代码中存在`cutoff`和`cutlim`阈值限定了从字符串中读取时不会让`start`或`end`为负值， 所以这里需要进入`suffix =
1`的分支，因此使用`Range:bytes=-xxx`，（`-end`的格式）即省略初始`start`值的形式，由此可以绕过`*p !=
'-'`的限制，进入`suffix=1`的分支。

    
    
    if (suffix)  
    {  
    start = content_length - end;  
    end = content_length - 1;  
    }

`start`等于`content_length`减去`end`值，所以如果传入的`end`比实际长度还要长，就可以使`start`变为负数。其中`content_length`为不包含文件头的文件长度。最终`end`的值会被设定为`content_length
- 1`（因此我们需要构造一个小包）

    
    
    if (start < end)   
    {  
    range = ngx_array_push(&ctx->ranges);  
    if (range == NULL)   
    {  
    return NGX_ERROR;  
    }  
    ​  
    range->start = start;  
    range->end = end;  
    ​  
    size += end - start;  
    if (ranges-- == 0)   
    {  
    return NGX_DECLINED;  
    }  
    }

`start`相当于分片区间的头指针，`end`相当于分片区间的尾指针。如果此时`end`值要比文件长度（`content_length`）数值大的话，就可以将`start`解析为负值。与`Range`相关的还有一个`size`值，它是每段`Range`相加后的总长度

    
    
    if (size > content_length)  
    {  
    return NGX_DELINED;  
    }

当`size`（即所有`range`相加的总长度）超过文件长度`content_length`时，会返回默认的`NGX_DELINED`。

注意到此处有一个退出条件：

    
    
    if (*p++ != ',')  
    {  
    break;  
    }

支持支持`range`的值为`start1-end1,start2-end2……`的形式。

因此，可以构造`range:bytes=-x,-y`。一大一小两个`end`值，只需要
控制前面一个`end`值小而后一个`end`值大，从而实现`start`值和`size`值皆为负数，控制`start`值负到一个合适的位置，那么就能成功读到缓存文件头部了。

> 以下验证和POC来源于：
>
> <http://www.hacksee.com/blog/nginx-int-overflow.html>

 **CentOS搭建Nginx服务**

安装依赖库

    
    
    yum install gcc-c++ wget  
    yum install pcre pcre-devel  
    yum install zlib zlib-devel  
    yum install openssl openssl-devel

下载指定版本的Nginx包

    
    
    wget http://nginx.org/download/nginx-1.12.0.tar.gz

解压

    
    
    tar -zxvf nginx-1.12.0.tar.gz

安装Nginx

    
    
    cd nginx-1.12.0  
    ./configure --prefix=/usr/local/nginx  
    make && make install  
    ln -s /usr/local/nginx/sbin/nginx /usr/bin  
    systemctl stop firewalld  
    nginx

修改Nginx配置文件

    
    
    vi /usr/local/nginx/conf/nginx.conf

设置 Nginx 服务器反向代理百度，开启缓存功能，具体配置如下：

    
    
    #user  nobody;  
    worker_processes  1;  
      
    #error_log  logs/error.log;  
    #error_log  logs/error.log  notice;  
    #error_log  logs/error.log  info;  
      
    #pid        logs/nginx.pid;  
      
      
    events {  
    worker_connections  1024;  
    }  
      
      
    http {  
    include       mime.types;  
    default_type  application/octet-stream;  
      
    #log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '  
    #                  '$status $body_bytes_sent "$http_referer" '  
    #                  '"$http_user_agent" "$http_x_forwarded_for"';  
      
      
    proxy_cache_key "$scheme$request_method$host$request_uri";  
    proxy_cache_path /tmp/nginx levels=1:2 keys_zone=zone:10m;  
    proxy_cache_valid 200 10m;  
      
      
    #access_log  logs/access.log  main;  
      
    sendfile        on;  
    #tcp_nopush     on;  
      
    #keepalive_timeout  0;  
    keepalive_timeout  65;  
      
    #gzip  on;  
      
    server {  
    listen       80;  
    server_name  localhost;  
      
    #charset koi8-r;  
      
    #access_log  logs/host.access.log  main;  
      
    location / {  
    #root   html;  
    #index  index.html index.htm;  
    proxy_pass http://www.baidu.com;  
    proxy_set_header Host www.baidu.com;  
      
    proxy_cache zone;  
    add_header X-Proxy-Cache $upstream_cache_status;  
    proxy_ignore_headers Set-Cookie;  
    }  
      
    #error_page  404              /404.html;  
      
    # redirect server error pages to the static page /50x.html  
    #  
    error_page   500 502 503 504  /50x.html;  
    location = /50x.html {  
    root   html;  
    }  
      
    # proxy the PHP scripts to Apache listening on 127.0.0.1:80  
    #  
    #location ~ \.php$ {  
    #    proxy_pass   http://127.0.0.1;  
    #}  
      
    # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000  
    #  
    #location ~ \.php$ {  
    #    root           html;  
    #    fastcgi_pass   127.0.0.1:9000;  
    #    fastcgi_index  index.php;  
    #    fastcgi_param  SCRIPT_FILENAME  /scripts$fastcgi_script_name;  
    #    include        fastcgi_params;  
    #}  
      
    # deny access to .htaccess files, if Apache's document root  
    # concurs with nginx's one  
    #  
    #location ~ /\.ht {  
    #    deny  all;  
    #}  
    }  
      
      
    # another virtual host using mix of IP-, name-, and port-based configuration  
    #  
    #server {  
    #    listen       8000;  
    #    listen       somename:8080;  
    #    server_name  somename  alias  another.alias;  
      
    #    location / {  
    #        root   html;  
    #        index  index.html index.htm;  
    #    }  
    #}  
      
      
    # HTTPS server  
    #  
    #server {  
    #    listen       443 ssl;  
    #    server_name  localhost;  
      
    #    ssl_certificate      cert.pem;  
    #    ssl_certificate_key  cert.key;  
      
    #    ssl_session_cache    shared:SSL:1m;  
    #    ssl_session_timeout  5m;  
      
    #    ssl_ciphers  HIGH:!aNULL:!MD5;  
    #    ssl_prefer_server_ciphers  on;  
      
    #    location / {  
    #        root   html;  
    #        index  index.html index.htm;  
    #    }  
    #}  
      
    }

>
> `proxy_cache_key`用来指定生成的`key`的字段内容，用以区分缓存文件，这部分内容会在之后我们利用漏洞时被泄露。`proxy_cache_path`设置了缓存文件的路径和参数。`proxy_cache_valid`用来指定不同状态码下的缓存时间。`server`代码块设置了代理的内容，并对响应头进行了一些设置。`add_header
> X-Proxy-Cache`表示在响应头里添加一条`X-Proxy-Cache`，用以区分是否命中缓存，它一共有 5
> 种状态，`MISS`表示未命中，请求被传送到后端；`HIT`表示缓存命中；`EXPIRED`表示缓存已经过期请求被传送到后端；`UPDATING`表示正在更新缓存，将使用旧的应答；`STALE`表示后端将得到过期的应答。

重新加载配置

    
    
    nginx -s reload

使用另一台服务器进行访问

![image-20220616211003939](https://image.3001.net/images/20220620/1655725533_62b05ddd39807cf16fc50.png!small)

    
    
      
    print check(target)  
    except Exception,e:  
    print '[-]Error: ' + str(e)  
    exit(0)  
      
    if __name__=='__main__'::  
    main()

测试

    
    
    python2 nginx_poc.py [your ip]

![image-20220616215100390](https://image.3001.net/images/20220620/1655725536_62b05de0beda4d88f9218.png!small)

成功爆key`KEY: httpGETx.x.x.x/favicon.ico`

漏洞利用成功!

参考文章：

> <http://www.hacksee.com/blog/nginx-int-overflow.html>
>
> <https://paper.seebug.org/353/#5>
>
> <https://gitee.com/geektime-> geekbang/WebSecurity/raw/master/PDF/%E7%AC%AC%E5%9B%9B%E7%AB%A0%EF%BC%882%EF%BC%89%EF%BC%9ANginx%E5%AE%89%E5%85%A8%E4%B8%93%E9%A2%98.pdf>

