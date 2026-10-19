***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ****
**大家好，今天分享的writeup是作者在针对印度最大的股票经纪公司进行安全测试时，通过不同层面的绕过技巧（Bypass），最终获取到该公司AWS密码凭据的过程。其中用到了WAF绕过，以及进一步的Web
Cache绕过，实现SSRF攻击，最后获取到了目标系统的AWS密码凭据。（本文的发表已经获得该股票经纪公司许可）。**

 ** **![stock-market.jpg](https://image.3001.net/images/20190429/1556526797_5cc6b6cdd79b2.jpg!small)****

## 发现WAF防护

测试刚开始，我注意到目标系统的一个服务路径（Endpoint）会与一些后台的文件系统进行交互，因此接下来我就自然而然地测试了本地文件包含漏洞（LFI），之后发现，目标系统应用受Cloudflare
WAF防火墙保护。如下：

![01.png](https://image.3001.net/images/20190429/1556526037_5cc6b3d5eb30a.png!small)CloudFlare是一家提供DNS、WAF和DDOS防护的云安全供应商，由它提供的安全服务可以很好地隐藏目标网站的真实IP并发挥CloudFlare的安全过滤能力，对目标网站系统起到保护作用。通常，攻击者在不知道服务器真实IP的情况下，很难直接对目标系统发起攻击。但是，攻击者也经常会以一些间接方法发现目标网站真实IP，以此来绕过CloudFlare
WAF（更多CloudFlare WAF绕过案例请自行百度）。

基于这种部署架构的Web应用服务器来说，客户端发起对应用的请求，要经过CDN、WAF或负载均衡等中间层代理设备，才能真正地到达后端服务器中。所以，本质上看，如果知道目标系统真实IP，我发起的请求不在后端负载均衡或服务器过滤白名单之列，那么就能直接与应用的后端服务器进行交互了，这样就能绕过CloudFlare
WAF了。逻辑如下：

![02.png](https://image.3001.net/images/20190429/1556526140_5cc6b43c49b4b.png!small)

## 绕过WAF防护但又遇上缓存服务（Web Cache)

当然了，这里我们要来先发现目标应用系统的真实IP，我简单地执行 “dig
[www.readacted.com](http://www.readacted.com)” 命令，竟然就找到了：

![03.png](https://image.3001.net/images/20190429/1556526156_5cc6b44c672d7.png!small)之后，我在本地的hosts文件中，增加了一条真实IP和其域名对应的条目，查看域名访问的变化情况，貌似是可行的，那么，我们结合上面的LFI漏洞情况来试试密码读取。当在URL后加上/etc/passwd命令执行后，竟幸运地得到了以下的有效响应：

![04.png](https://image.3001.net/images/20190429/1556526182_5cc6b46603c2a.png!small)所以，就这样，我就轻易地绕过了CloudFlare
WAF并实现了LFI漏洞攻击。接下来，我Whois了该真实IP后发现，它是一个AWS服务架构。思路到了这里，我认为下一步的目标就是，看看能否实现SSRF进而读取出其中的AWS账户密码凭据。因为按AWS的特定页面或URL功能部署来看，是可能获取到相应的账户密码信息的，但愿如此。不多啰嗦，我立马以该目标应用系统身份，在URL链接之后，针对AWS官方的实例元数据实例
- **<http://169.254.169.254/latest/meta-data/>** ，发起了一个GET请求，如下：

![05.png](https://image.3001.net/images/20190429/1556526398_5cc6b53ece12f.png!small)应用后端服务器对该请求的响应是
200 ok，但响应内容却是空的，如下：

    
    
    HTTP/1.1 200 OK
    
    Server: nginx
    
    Date: Fri, 06 Apr 2019 14:32:48 GMT
    
    Content-Type: text/css;charset=UTF-8
    
    Connection: close
    
    Vary: Accept-Encoding
    
    Strict-Transport-Security: max-age=15552000
    
    X-Frame-Options: DENY
    
    X-Content-Type-Options: nosniff
    
    X-XSS-Protection: 1; mode=block
    
    X-Proxy-Cache: HIT
    
    Content-Length: 0

这表明交互确实发生了，但为什么响应是空的呢？查看以上响应消息，可以发现，其中的server header为“nginx”，另外还有一个值为HIT的X-Proxy-Cache。也就是说，我们发起的请求遇到了中间的Nginx缓存服务，然后该缓存服务向我们响应了空消息。

## 绕过Web Cache实现SSRF获取AWS密码凭据

所以，从这种情况来看，为了获取到真实的应用服务端响应，就必要绕过这个Nginx缓存服务。为此，我还进一步了解了Nginx缓存的URL页面缓存规则。

> <https://www.digitalocean.com/community/tutorials/how-to-implement-browser-> caching-with-nginx-s-header-module-on-centos-7>
>
> <https://www.howtoforge.com/make-browsers-cache-static-files-on-nginx>

经过学习之后，我了解到通常的缓存服务是以URL路径路由为基础的，所以，如果请求的URL为：<https://somewebsite.com/a.html>，且与缓存规则中的路由路径相匹配，那么，它就会被引入缓存服务中，从其中获取响应。但如果请求URL为：<https://somewebsite.com/a.html?>，且与缓存规则中的路由路径不匹配，那么该请求就会会经由缓存服务，而是会直接从后端的应用服务器中获取响应。因此，我在读取AWS官方的实例元数据的请求末尾也加上了一个“？”问号（当然其它符号也可以），如此-<http://169.254.169.254/latest/meta-data?>，这样这种请求就不符合Nginx中的缓存匹配规则了。那我们来看看这样的请求，后端的应用服务器会不会给出响应。

<http://169.254.169.254/latest/meta-data?>为从运行实例内部查看所有类别的实例元数据请求：

![06.png](https://image.3001.net/images/20190429/1556526653_5cc6b63d50d29.png!small)心动的是，后端应用服务器确实给出了响应，且列出了目标系统运行实例内部的所有元数据：

    
    
    HTTP/1.1 200 OK
    
    Server: nginx
    
    Date: Fri, 06 Apr 2019 14:32:48 GMT
    
    Content-Type: text/css;charset=UTF-8
    
    Connection: close
    
    Vary: Accept-Encoding
    
    Strict-Transport-Security: max-age=15552000
    
    X-Frame-Options: DENY
    
    X-Content-Type-Options: nosniff
    
    X-XSS-Protection: 1; mode=block
    
    X-Proxy-Cache: MISS
    
    Content-Length: 315
    
    ami-id
    
    ami-launch-index
    
    ami-manifest-path
    
    block-device-mapping/
    
    events/
    
    hostname
    
    identity-credentials/
    
    instance-action
    
    instance-id
    
    instance-type
    
    local-hostname
    
    local-ipv4
    
    mac
    
    metrics/
    
    network/
    
    placement/
    
    product-codes
    
    profile
    
    public-hostname
    
    public-ipv4
    
    public-keys/
    
    reservation-id
    
    security-groups
    
    services/

仔细观察上述响应消息，其“X-Proxy-Cache” 值为 **MISS**
，也就是说，我们发起的请求没有经由Nginx的缓存服务层，它是直接从后端应用服务器获取响应的。

这样来看，我已经可以绕过缓存服务来实现SSRF攻击了，那么，按照AWS的实例元数据机制，我们来看看它能不能读取后端应用服务器中的AWS密码凭据。为此，我们让后端应用服务器发起针对以下AWS实例的请求：

> <http://169.254.169.254/latest/meta-data/identity-credentials/ec2/security-> credentials/ec2-instance?>

该请求适用于 向 Amazon EC2 基础设施的其余部分标识出运行实例的凭据信息。不出意外，果然我们就成功地读取到了其中的密码凭据了：

![07.png](https://image.3001.net/images/20190429/1556526959_5cc6b76fd9ef1.png!small)其中包括了目标系统的AWS访问ID，访问密码和token值，利用它们我可以以其AWS账户身份远程登录目标应用系统中的AWS资产，获取其中的重要数据信息。总结来说，我是先通过绕过Cloudflare
WAF发现目标应用服务器的真实IP，然后，利用LFI和缓存服务绕过提权执行SSRF攻击，最终获取了目标系统中的AWS密码凭据信息。还真是一次有意思的测试过程！

## 漏洞上报进程

> 2019.4.6 — 漏洞初报给公司
>
> 2019.4.7 — 公司着手修复漏洞
>
> 2019.4.7 — 我确认漏洞修复
>
> 2019.4.7 — 漏洞赏金发放

 ***参考来源：[medium](https://medium.com/@logicbomb_1/the-journey-of-web-cache-firewall-bypass-to-ssrf-to-aws-credentials-compromise-b250fb40af82)，clouds编译，转载请注明来自FreeBuf.COM**  

