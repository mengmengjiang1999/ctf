​ **作者：京东物流 殷世杰**

Nginx已经广泛应用于J-one和Jdos的环境部署上，本文对Nginx的常用的配置和基本功能进行讲解，适合Nginx入门学习。

# 1 核心配置

找到Nginx安装目录下的conf目录下nginx.conf文件，Nginx的基本功能配置是由它提供的。

Nginx的配置文件(conf/nginx.conf)整体上分为如下几个部分： ：

区域| 职责  
---|---  
全局块| 配置和Nginx运行相关的全局配置  
events块| 配置和网络链接相关的配置  
http块| 配置代理、缓存、日志记录、虚拟主机等配置  
server块| 配置虚拟主机的相关参数，一个http快中可以有多个server块  
location块| 配置请求的路由，以及各种页面的处理情况  
  
配置层级图如下所示。

![1682393057_644747e1aa5bcb2ce191b.png!small?1682393058195](https://image.3001.net/images/20230425/1682393057_644747e1aa5bcb2ce191b.png!small?1682393058195)

###  **1.2 配置文件示例**

一个比较全的配置文件示例如下。

    
    
    # 以下是全局段配置
    #user administrator administrators;  #配置用户或者组，默认为nobody nobody。
    #worker_processes 2;  #设置进程数，默认为1
    #pid /nginx/pid/nginx.pid; #指定nginx进程运行文件存放地址
    error_log log/error.log debug;  #制定日志路径，级别：debug|info|notice|warn|error|crit|alert|emerg
    # events段配置信息
    events {
        accept_mutex on;   #设置网路连接序列化，防止惊群现象发生，默认为on
        multi_accept on;  #设置一个进程是否同时接受多个网络连接，默认为off
        #use epoll;      #事件驱动模型，select|poll|kqueue|epoll|resig|/dev/poll|eventport
        worker_connections  1024;    #最大连接数，默认为512
    }
    # http、配置请求信息
    http {
        include       mime.types;   #文件扩展名与文件类型映射表
        default_type  application/octet-stream; #默认文件类型，默认为text/plain
        #access_log off; #取消服务日志    
        log_format myFormat '$remote_addr–$remote_user [$time_local] $request $status $body_bytes_sent $http_referer $http_user_agent $http_x_forwarded_for'; #自定义格式
        access_log log/access.log myFormat;  #combined为日志格式的默认值
        sendfile on;   #允许sendfile方式传输文件，默认为off，可以在http块，server块，location块。
        sendfile_max_chunk 100k;  #每个进程每次调用传输数量不能大于设定的值，默认为0，即不设上限。
        keepalive_timeout 65;  #连接超时时间，默认为75s，可以在http，server，location块。
    
    
        upstream mysvr {   
          server 127.0.0.1:7878;
          server 192.168.10.121:3333 backup;  #热备
        }
        error_page 404 https://www.baidu.com; #错误页
        # 第一个Server区块开始，表示一个独立的虚拟主机站点
        server {
            keepalive_requests 120; #单连接请求上限次数。
            listen       4545;   #监听端口
            server_name  127.0.0.1;   #监听地址       
            location  ~*^.+$ {       #请求的url过滤，正则匹配，~为区分大小写，~*为不区分大小写。
               #root path;  #根目录
               #index vv.txt;  #设置默认页
               proxy_pass  http://mysvr;  #请求转向mysvr 定义的服务器列表
               deny 127.0.0.1;  #拒绝的ip
               allow 172.18.5.54; #允许的ip           
            } 
        }
    }
    
    

### **1.3 locat路径映射讲解**

###  **1.3.1格式：**

location [ = | ~ | ~* | !~ | !~* | @ ] uri {...}

###  **1.3.2解释：**

= 表示精确匹配，如果找到，立即停止搜索并立即处理此请求。

~ 表示执行一个正则匹配，区分大小写匹配

~* 表示执行一个正则匹配，不区分大小写匹配

!~ 区分大小写不匹配

!~* 不区分大小写不匹配

^~ 即表示只匹配普通字符（空格）。使用前缀匹配，^表示“非”，即不查询正则表达式。如果匹配成功，则不再匹配其他location。

@ 指定一个命名的location，一般只用于内部重定向请求。例如 error_page, try_files

uri 是待匹配的请求字符串，可以不包含正则表达式，也可以包含正则表达式；

###  **1.3.3优先级和示例：**

  * [不加] < [~/~*] < [^~] < [=]

  * 示例如下：

    
    
    location = / {
        # 精确匹配/，主机名后面不能带任何字符串 /
        # 只匹配http://abc.com
        # http://abc.com [匹配成功]
        # http://abc.com/index [匹配失败]
    }
    location ^~ /img/ {
          #以 /img/ 开头的请求，都会匹配上
        #http://abc.com/img/a.jpg   [成功]
        #http://abc.com/img/b.mp4  [成功]
        }
    location ~* /Example/ {
      # 则会忽略 uri 部分的大小写
      #http://abc.com/test/Example/ [匹配成功]
      #http://abc.com/example/ [匹配成功]
    }
    location /documents {
        # 如果有正则表达式可以匹配，则优先匹配正则表达式。
        #http://abc.com/documentsabc [匹配成功]
    }
    location / {
        #http://abc.com/abc [匹配成功]
    }
    
    
    

# 2 反向代理

###  **2.1 反向代理概念：**

反向代理(Reverse
Proxy)是指以代理服务器来接受internet上的连接请求，然后将请求转发给内部网络上的服务器，并将从服务器上得到的结果返回给internet上请求连接的客户端。真实的服务器不能直接被外部网络访问，所以需要一台代理服务器，而代理服务器能被外部网络访问的同时又跟真实服务器在同一个网络环境，当然也可能是同一台服务器，端口不同而已。

反向代理通过proxy_pass指令来实现。

###  **2.2 反向代理示例：**

    
    
    server {
        listen       80;
        server_name  localhost;
    
    
        location / {
             proxy_pass http://localhost:8081;
             proxy_set_header Host $host:$server_port;#为请求头添加Host字段，用于指定请求服务器的域名/IP地址和端口号。  
    
    
             # 设置用户ip地址
             proxy_set_header X-Forwarded-For $remote_addr;#为请求头添加XFF字段，值为客户端的IP地址。
             # 当请求服务器出错去寻找其他服务器
             proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
        
    

当我们访问localhost的时候，ngnix就将我们的请求转到 localhost:8081了

# 3 负载均衡

###  **3.1 负载均衡概念：**

当有2台或以上服务器时，代理服务器根据规则将请求分发到指定的服务器上处理。

###  **3.2 负载均衡策略及示例：**

Nginx目前支持多种负载均衡策略，这里讲解常用的6种。

3.2.1RR(round robin :轮询 默认)：

每个请求按时间顺序逐一分配到不同的后端服务器，也就是说第一次请求分配到第一台服务器上，第二次请求分配到第二台服务器上，如果只有两台服务器，第三次请求继续分配到第一台上，这样循环轮询下去，也就是服务器接收请求的比例是
1:1， 如果后端服务器down掉，能自动剔除。轮询是默认配置，不需要太多的配置

同一个项目分别使用8081和8082端口启动项目

    
    
    upstream web_servers {
       server localhost:8081;
       server localhost:8082;
    }
    
    
    
    
    server {
        listen       80;
        server_name  localhost;
        #access_log  logs/host.access.log  main;
        location / {
            proxy_pass http://web_servers;
            proxy_set_header Host $host:$server_port;
        }
    

**3.2.2 热备：**

假设有2台服务器，当一台服务器发生事故时，才启用第二台服务器给提供服务。服务器处理请求的顺序：AAAAAA突然A挂了，服务器处理请求的顺序：BBBBBBBBBBBBBB.....

    
    
    upstream web_servers {
          server 127.0.0.1:7878; 
          server 192.168.10.121:3333 backup;  #热备     
        }
    

3.2.3 权重

跟据配置的权重的大小而分发给不同服务器不同数量的请求。如果不设置，则默认为1。下面服务器的请求顺序为：ABBABBABBABBABB....。

    
    
    upstream web_servers {
        server localhost:8081 weight=1;
        server localhost:8082 weight=2;
    }
    

3.2.4 ip_hash

这样每个ip地址固定访问一个后端服务器，可以解决session的问题。

    
    
    upstream test {
        ip_hash;
        server localhost:8080;
        server localhost:8081;
    }
    

**3.2.5 fair(第三方)**

按后端服务器的响应时间来分配请求，响应时间短的优先分配。这个配置是为了更快的给用户响应。

    
    
    upstream backend {
        fair;
        server localhost:8080;
        server localhost:8081;
    }
    

**3.2.6 url_hash(第三方)**

按访问url的hash结果来分配请求，使每个url定向到同一个后端服务器，后端服务器为缓存时比较有效。在upstream中加入hash语句，hash_method是使用的hash算法

    
    
    upstream backend {
        hash_method crc32;
        hash $request_uri;
        server localhost:8080;
        server localhost:8081;
    }
    

以上6种负载均衡各自适用不同情况下单独或者混合使用，可以根据实际情况选择使用，fair和url_hash需要安装第三方模块才能使用。

# 4 动静分离：

###  **4.1 动静分离概念：**

动静分离是指在web服务器架构中，将静态页面与动态页面或者静态内容接口和动态内容接口分开不同系统访问的架构设计方法，进而提升整个服务访问性能和可维护性。

###  **4.2 动静分离示例：**

    
    
    upstream web_servers {
           server localhost:8081;
           server localhost:8082;
    }
    server {
        listen       80;
        server_name  localhost;
        set $doc_root /usr/local/var/www;
    
    
        location ~* \.(gif|jpg|jpeg|png|bmp|ico|swf|css|js)$ {
           root $doc_root/img;
        }
        location / {
            proxy_pass http://web_servers;
            proxy_set_header Host $host:$server_port;
        }
        error_page 500 502 503 504  /50x.html;  #出现 500 502 503 504错误时走内部跳转
        location = /50x.html { 
            root $doc_root;
        }
     }
    
    
    

结果：访问http://localhost/test.jpg时直接返回/usr/local/var/www/img路径下的图片.

访问http://localhost/index.html就会访问后端服务器(tomcat等)

# 5 其他常用的指令：

###  **5.1.return指令**

返回http状态码和可选的第二个参数可以是重定向的URL

    
    
    return code [text];
    return code URL;
    return URL;
    例如：
    location / {
     return 404; # 直接返回状态码
    }
    location / {
     return 404 "pages not found"; # 返回状态码 + 一段文本
    }
    location / {
     return 302 /bbs ; # 返回状态码 + 重定向地址
    }
    location / {
     return https://www.baidu.com ; # 返回重定向地址
    }
    

### **5.2 rewrite指令**

重写URI请求 rewrite，通过使用rewrite指令在请求处理期间多次修改请求URI，该指令具有一个可选参数和两个必需参数。

第一个(必需)参数是请求URI必须匹配的正则表达式。

第二个参数是用于替换匹配URI的URI。

可选的第三个参数重写策略

  * last 重写后的 URL 发起新请求，再次进入 server 段，重试 location 的中的匹配；

  * break 直接使用重写后的 URL ，不再匹配其它 location 中语句；

  * redirect 返回302临时重定向；

  * permanent 返回301永久重定向；

    
    
    location /users/ {
        rewrite ^/users/(.*)$ /show?user=$1 break;
    }
    

### **5.3 error_page指令**

使用error_page指令，您可以配置NGINX返回自定义页面以及错误代码，替换响应中的其他错误代码，或将浏览器重定向到其他URI。在以下示例中，error_page指令指定要返回404页面错误代码的页面(/404.html)。

    
    
    server{
        	error_page 500 502 503 504 /50x.html;
        	location =/50x.html{
        		root html;
        	}
        }
    
    

### **5.4 日志**

访问日志：需要开启压缩 gzip on; 否则不生成日志文件，打开log_format、access_log注释

    
    
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                          '$status $body_bytes_sent "$http_referer" '
                          '"$http_user_agent" "$http_x_forwarded_for"';
    
    
    
    
    access_log  /usr/local/etc/nginx/logs/host.access.log  main;
    
    
    
    
    gzip 
    
    
    

### **5.5 deny 、allow指令**

    
    
    #禁止访问某个目录
    location / {
        allow 192.168.0.0;
        allow 127.0.0.1;
        deny all;
    #这段配置值允许192.168.0./24网段和127.0.0.1的请求，其他来源IP全部拒绝。
    }
    

### **5.6 内置变量**

nginx的配置文件中可以使用的内置变量以美元符$开始。其中，大部分预定义的变量的值由客户端发送携带。

  * $args ：#这个变量等于请求行中的参数，同$query_string

  * $content_length ：请求头中的Content-length字段。

  * $content_type ：请求头中的Content-Type字段。

  * $document_root ：当前请求在root指令中指定的值。

  * $host ：请求行的主机名，为空则为请求头字段 Host 中的主机名，再为空则与请求匹配的server_name

  * $http_user_agent ：客户端agent信息

  * $http_cookie ：客户端cookie信息

  * $limit_rate ：这个变量可以限制连接速率。

  * $request_method ：客户端请求的动作，通常为GET或POST。

  * $remote_addr ：客户端的IP地址。

  * $remote_port ：客户端的端口。

  * $remote_user ：已经经过Auth Basic Module验证的用户名。

  * $request_filename ：当前请求的文件路径，由root或alias指令与URI请求生成。

  * $scheme ：HTTP方法（如http，https）。

  * $server_protocol ：请求使用的协议，通常是HTTP/1.0或HTTP/1.1。

  * $server_addr ：服务器地址，在完成一次系统调用后可以确定这个值。

  * $server_name ：服务器名称。

  * $server_port ：请求到达服务器的端口号。

  * $request_uri ：包含请求参数的原始URI，不包含主机名，如：”/foo/bar.php?arg=baz”。

  * $uri ：不带请求参数的当前URI，$uri不包含主机名，如”/foo/bar.html”。

  * $document_uri ：与$uri相同

# 6 总结

Ngnix是一款高性能反向代理服务器，学习它非常有必要，本文讲解了Ngnix核心配置，介绍了反向代理，负载均衡，动静分离三大功能，最后扩展了一些常用的指令。本文介绍了Ngnix的基础用法，后续的Ngnix内核以及原理部分有待研究。

​

