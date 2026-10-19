## 简介

![1](https://image.3001.net/images/20211114/1636878845_6190c9fdd5cf2e1071a54.png!small)

Nginx（engine
x）是一个高性能的HTTP和反向代理web服务器，同时也提供了IMAP/POP3/SMTP服务器Nginx是由伊戈尔开发，因为它的稳定性、丰富的功能集、实例配置文件和低系统资源的消耗而闻名。

Nginx是一款轻量级的Web服务器/反向代理服务器及电子邮件（IMAP/POP3）代理服务器，在BSD-like协议下发行，其特点是占用内存少，并发能力强，事实上nginx的并发能力确实在同类型的网页服务器中表现较好

中国大陆使用 nginx 的网站用户有：百度、京东、新浪、网易、腾讯、淘宝

Nginx适用于高并发、可以做负载均衡服务器和HTTP服务器、具有代码特点、可以作为代理服务器

![2](https://image.3001.net/images/20211114/1636878847_6190c9ff6c3e299d4a0a7.png!small)

Nginx可以用作以下

  1. 静态服务器

首先，Nginx是一个HTTP服务器，可以将服务器上的静态文件（HTML、图片等）通过HTTP协议展现给客户端

Nginx是一款轻量级的Webserver/反向代理server以及电子邮件代理server。并在一个BSD-like协议下发行，特点是占用内存小，并发能力强，Nginx相较于Apache/lighttpd具有占用内存少，稳定性高等优势，并且依靠并发能力强，丰富的模块库以及友好灵活的配置而闻名

Nginx本身也是一个静态资源的服务器当只有静态资源的时候，就可以使用Nginx来做服务器，同时现在也很流行动静分离，可以通过Nginx来实现动静分离是让动态网站里的动态网页根据一定规则把不变的资源和经常变的资源区分开来动静资源做好了拆分以后，我们可以根据静态资源的特点将其作为缓存操作，这就是网站静态化处理的核心思路

  2. 反向代理服务器

客户端本来可以直接通过HTTP协议访问某网站应用服务器，网站管理员可以在中间加上一个Nginx，客户端请求Nginx，Nginx请求应用服务器，然后将结果返回客户端，此时Nginx就是反向代理服务器

用户A向反向代理的命名空间（name-space）中的内容发送普通请求，接着反向代理将推断向何处（原始server）转交请求，并将获得的内容返回给client。而用户A始终认为他访问的是原始server而不是nginx。因为防火墙作用，仅仅同意nginx进出，防火墙和反向代理的共同作用保护了院子内的资源
---原始server

![3](https://image.3001.net/images/20211114/1636878849_6190ca0168aaa3c82c802.png!small)

如果服务器可以直接HTTP访问，为什么要在中间加一个反向代理，下面的负载均衡、虚拟主机等都基于反向代理实现，当然反向代理的功能也不仅仅是这些

  3. 负载均衡

当网站访问量非常大，网站站长开心赚钱的同时，也摊上事了。因为网站越来越慢，一台服务器已经不够用了。于是将同一个应用部署在多台服务器上，将大量用户的请求分配给多台机器处理。同时带来的好处是，其中一台服务器万一挂了，只要还有其他服务器正常运行，就不会影响用户使用Nginx可以通过反向代理来实现负载均衡

负载均衡的意思就是分摊到多个操作单元上进行执行，例如Web服务器、FTP服务器、企业关键应用服务器和其它关键任务服务器等等，从而共同完成工作任务，简单而言就是当有2台或以上服务器时，根据规则随机的将请求分发到指定的服务器上处理，负载均衡一般都需要同时配置反向代理，通过反向代理跳转到负载均衡，而Nginx目前支持自带3种负载均衡策略，还有2种常用的第三方策略

  4. 虚拟主机

有的网站访问量大，需要负载均衡。然而不是所有的网站都如此出色，有的网站由于访问量太小，需要节省成本，将多个网站部署在同一台服务器上

例如将www.aaa.com和www.bbb.com两个网站部署在同一台服务器上，两个域名解析到同一个IP地址，但是用户通过两个域名却可以打开两个完全不同的网站，互不影响，就像访问两个服务器一样，所以叫两个虚拟主机

  5. 正向代理

正向代理是一个位于用户A和原始server之间的代理server
，为了从原始server取得内容，用户A向代理server发送一个请求并指定目标（原始server）。然后代理server向原始server转交请求并将获得的内容返回给用户，用户必须进行一些特别的设置才能使用正向代理

用途：在防火墙内的局域网用户提供访问Internet的途径。还能够使用缓冲特性降低网络使用率

从安全角度讲：

正向代理同意用户通过它访问任意站点而且隐藏用户自身，因此你必须采取安全措施以确保仅为经过授权的用户提供服务。

正反向代理对外都是透明的。访问者并不知道自己访问的是一个代理。

  6. Nginx vs Apache

![4](https://image.3001.net/images/20211114/1636878850_6190ca02b975e97890fec.png!small)

![5](https://image.3001.net/images/20211114/1636878852_6190ca04809db6172f050.png!small)

### Nginx环境

![6](https://image.3001.net/images/20211114/1636878854_6190ca062114c373585c9.png!small)

![7](https://image.3001.net/images/20211114/1636878855_6190ca075e6df12e77bbf.png!small)

## Nginx渗透

### 文件解析漏洞

漏洞简介：

​ 对于任意文件名，在后面添加 /xxx.php（xxx为任意字符）后，即可将文件作为php解析

漏洞范围：

​ 该漏洞是nginx配置所导致，与版本无关。

漏洞复现：

![8](https://image.3001.net/images/20211114/1636878856_6190ca08a58baf1811bee.png!small)

1.jpg后面加上 /xxx.php ，会将 1.jpg 以PHP解析

注意下图中的访问链接

![9](https://image.3001.net/images/20211114/1636878857_6190ca09d8b03095e0f9e.png!small)

![10](https://image.3001.net/images/20211114/1636878858_6190ca0ade4486df797e4.png!small)

该漏洞是Nginx配置所导致，与Nginx版本无关，下面是常见的漏洞配置：

![11](https://image.3001.net/images/20211114/1636878860_6190ca0c2717b3abbe14f.png!small)

    
    
    server { 
    	location ~ \.php$ { 
    		root /work/www/test; 
    		fastcgi_index index.php; 
    		fastcgi_param SCRIPT_FILENAME 
    	$document_root$fastcgi_script_name; 
    		include fastcgi_params; 
    	fastcgi_pass unix:/tmp/php-fpm.sock; 
    	} 
    }
    

当攻击者访问 /1.jpg/xxx.php 时，Nginx将查看URL，看到它以 .php 结尾，并将路径传递给 PHP fastcgi
处理程序.Nginx传给php的路径为 C:/phpStrudy/WWW/1.jpg/xxx.php ，在phpinf中可以查看
_SERVER["ORIG_SCRIPT_FILENAME"] 得到

![12](https://image.3001.net/images/20211114/1636878861_6190ca0d3b08dc09c5893.png!small)

PHP根据URL映射，在服务器上寻找xxx.php文件，但是xxx.php不存在，又由于 cgi.fix_pathinfo
默认是开启的，因此PHP会继续检查路径中存在的文件，并将多余的部分当作 PATH_INFO
。接着PHP在文件系统中找到.jpg文件，而后以PHP的形式执行.jpg的内容，并将 /xxx.php 存储在 PATH_INFO
后丢弃，因此我们在phpinfo中的$_SERVER['PATH_INFO'] 看到的值为空（no value），如果继续添加后缀则蠢顺势显示后缀

![13](https://image.3001.net/images/20211114/1636878862_6190ca0e2b5f07d37f3f4.png!small)

最后整理一下思路：cgi.fix_pathinfo

php的一个选项：cgi.fix_pathinfo，该选项默认开启，值为1，用于修理路径的

例如：当php遇到文件路径 /yxc.jpg/xxx.php/yxc.sec 时，若 /yxc.jpg/xxx.php/yxc.sec
不存在，则会去掉最后的 /yxc.sec ，然后判断 /yxc.jpg/xxx.php 是否存在，若存在则将 /yxc.jpg/xxx.php 当作文件
/yxc.jpg/xxx.php/yxc.sec ，若 /yxc.jpg/xxx.php 仍不存在，则继续去掉 xxx.php ，以此类推

修复建议：

  1. 配置cgi.fix_pathinfo(php.ini中)为0，并重启php-cgi程序

  2. 如果需要使用到cgi.fix_pathinfo这个特性（例如：wordpress），那么可以禁止上传目录的执行脚本权限或将上传存储的内容与网站分离，即站库分离

  3. 高版本PHP提供了security.limit_extensions 这个配置参数，设置 security.limit_extensions = .php

### 目录遍历

Nginx 的目录遍历与 Apache一样，属于配置方面的问题，错误的配置可导致目录遍历与源码泄露

先去www目录下随便新建一个文件夹，然后进行访问

![14](https://image.3001.net/images/20211114/1636878863_6190ca0f2a0bf560fd423.png!small)

修改 C:\phpstudy\nginx\conf\nginx.conf，在下面标示位置中添加 autoindex on ;

![15](https://image.3001.net/images/20211114/1636878864_6190ca102a2f9ee8a3af3.png!small)

重启nginx，再次访问即可

![16](https://image.3001.net/images/20211114/1636878865_6190ca1133929ffdafb76.png!small)

修复建议：on改为off即可

## 空字节任意代码执行漏洞

影响版本：

​ nginx 0.5.*

​ nginx 0.6.*

​ nginx 0.7 <\- 0.7.65

​ nginx 0.8 <\- 0.8.37

Nginx在遇到%00空字节时与后端FastCGI处理不一致，导致可以在图片中嵌入PHP代码然后通过访问 xxx.jpg%00.php 来执行其中的代码

复现环境：

​ nginx 0.7.65+php 5.3.2

在nginx-0.7.65/html/目录下创建 1.jpg，内容为：

    
    
    <?php phpinfo();?>
    

访问1.jpg，无法访问，所以在URL中输入 1.jpg..php

然后抓包，hex选项下，.的hex编码为2e，将第一个2e改为00

![17](https://image.3001.net/images/20211114/1636878866_6190ca121a84a19515280.png!small)

![18](https://image.3001.net/images/20211114/1636878867_6190ca13bdc339fffc36c.png!small)

成功绕过

该漏洞不受 cgi.fix_pathinfo 影响，当其为0时，依然解析

高版本不存在该漏洞

## CRLF注入漏洞

漏洞产生：

Nginx会将 $uri 进行编码，导致传入 %0a%0d 即可引入换行符，造成CRLF注入漏洞。

错误的配置文件原本的目的是为了让http的请求跳转到https上的，意思就是配置实现了强制跳转的功能，当用户访问nginx服务器时，由于此配置的存在会被强制跳转到以https协议访问之前访问的链接

![19](https://image.3001.net/images/20211114/1636878869_6190ca15f0ad081f583ec.png!small)

  1. 配置中的 $url 是我们可以控制的，这样我们就可以在 $url 处填入CRLF ，然后对服务器进行访问实现头部注入

  2. 服务器会返回一个302跳转给用户

漏洞危害：

​ 劫持合法用户会话，利用管理员身份进行恶意操作，篡改页面内容、进一步渗透网站

​ 利用CRLF injection设置一个 SESSION ，造成一个 "会话固定漏洞"

原理：

​ CRLF是“回车 + 换行”（\r\n）的简称。在HTTP协议中，HTTP Header与HTTP
Body是用两个CRLF分隔的，浏览器就是根据这两个CRLF（使用payload
%0a%0d%0a%0d进行测试）来取出HTTP内容并显示出来。所以，一旦我们能够控制HTTP消息头中的字符，注入一些恶意的换行，这样我们就能注入一些会话Cookie（[http://www.xx.com%0a%0d%0a%0dSet-cookie:JSPSESSID%3Dxxx）或者HTML代码（http://www.xx.com/?url=%0a%0d%0a%0d](https://www.freebuf.com/articles/web/265135.html?url=)<img
src=1 onerror=alert("xss")>），所以CRLF Injection又叫HTTP Response Splitting，简称HRS

Nginx会将$uri进行解码，导致传入%0a%0d即科引入换行符，造成CRLF注入漏洞

$uri跳转HTTPS，$uri就会产生%0a%0d换行符，换行符就一定存在CRLF注入漏洞

漏洞复现：

​ cd vulhub/nginx/insecure-configuration

​ docker-compose up -d

​ [http://127.0.0.1/%0ASet-cookie:JSPSESSID%3D36](http://127.0.0.1/ Set-cookie:JSPSESSID%3D36)

![20](https://image.3001.net/images/20211114/1636878872_6190ca182cdcfd3ec5529.png!small)

CRLF + XSS 配合：

    
    
    %0D%0A%0D%0A%3Cimg%20src=1%20onerror=alert(/xss/)%3E
    

![21](https://image.3001.net/images/20211114/1636878873_6190ca19eee6174138f9d.png!small)

使用旧版浏览器即可弹窗

#### CRLF深入：

攻击者操作：

  1. 攻击者打开一个网站，然后服务器会回复他一个session id。比如SID=abcdefg。Attack把这个id记下了

  2. Attack给被攻击者发送一个电子邮件，他假装抽奖或者推销，诱导攻击者点击链接：http://unsafe/?SID=abcdefg，SID后面是Attack自己的session id

  3. 被攻击者被吸引后，点击了http://unsafe/?SID=abcdefg，像往常一样，输入了自己的账号和口令从而登录到银行网站

  4. 因为服务器的session id不改变，现在被攻击者点击后，他就拥有了被攻击者的身份，就可以为所欲为了

### 文件名逻辑漏洞（CVE-2013-4547）

影响版本：

​ nginx 0.8.41 - 1.4.3 / 1.5.0 - 1.5.7

​ 复现时需要文件名的后面存在空格，而windows是不允许存在此类文件的，因此复现采用vulhub

漏洞复现：

![22](https://image.3001.net/images/20211114/1636878876_6190ca1c1d9899ffc6d5e.png!small)

cd vulhub/nginx/CVE-2013-4547

docker-compose build

docker-compose up -d

docker ps

![23](https://image.3001.net/images/20211114/1636878877_6190ca1d6b1328b09cf8b.png!small)

上传1.jpg

内容为：

    
    
    <?php phpinfo();?>
    

![24](https://image.3001.net/images/20211114/1636878878_6190ca1e70d23a420c369.png!small)

抓包在后缀名后面加个空格，成功绕过

修改名称为 2.jpg…php ，在hex编码下将jpg后面的两个2e改为20，00，

![25](https://image.3001.net/images/20211114/1636878879_6190ca1fb90ae5e4db1d6.png!small)

成功绕过

原理：

![26](https://image.3001.net/images/20211114/1636878881_6190ca21431109c78b930.png!small)

修复建议：

​ 升级版本

### 整数溢出 CVE-2017-7529

漏洞描述：

​ 在nginx的range filter 中存在整数溢出漏洞，可以通过带有特殊构造的range的HTTP头的恶意请求引发这个整数溢出漏洞，并导致信息泄露。

影响版本：

​ Nginx 0.5.6 - 1.13.2

危害程度：

​ 低

相关文章：

​ https://paper.seebug.org/353/

