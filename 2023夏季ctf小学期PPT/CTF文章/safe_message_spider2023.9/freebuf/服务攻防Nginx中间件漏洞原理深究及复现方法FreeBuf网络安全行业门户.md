## 一、简介

### 1、什么是Nginx

Ningx(engine
x)是一个高性能的HTTP和反向代理web服务器，同时也提供了IMAP/POP3/SMTP服务。其将源代码以类BSD许可证的形式发布，因它的稳定性、丰富的功能集、示例配置文件和低系统资源的消耗而闻名。

Nginx是一款轻量级的Web 服务器/反向代理服务器及电子邮件（IMAP/POP3）代理服务器，在BSD-like
协议下发行。其特点是占有内存少，并发能力强，nginx的并发能力在同类型的网页服务器中表现较好。

### 2、Nginx的特点

> 1、跨平台：Nginx 可以在大多数 Unix Linux OS 上编译运行，并有 Windows 移植版。
>
> 2、支持高并发：Nginx 是一个很强大的高性能Web和反向代理服务，可以支持高达 50,000 个并发连接数的响应。
>
> 3、内存低：Nginx采用C语言进行编写，系统资源开销还是CPU使用效率都比 Perlbal 要好很多。
>
> 4、负载均衡和HTTP服务器：Nginx作为负载均衡服务：Nginx 既可以在内部直接支持 Rails 和 PHP 程序对外进行服务，也可以支持作为
> HTTP代理服务对外进行服务。实现无缓存的反向代理加速，简单的负载均衡和容错。
>
> 5、稳定性高：用于反向代理，宕机的概率微乎其微。 等等...

### 3、nginx用来做什么

1、静态HTTP服务

首先，Nginx是一个HTTP服务器，可以将服务器上的静态文件（如HTML、图片）通过http协议展示给客服端。

Nginx相较于Apache\lighttpd具有占有内存少。稳定性高等优势，而且依靠并发能力强。丰富的模块库以及友好灵活的配置而闻名。

Nginx本身也是一个静态资源的服务器，当只有静态资源的时候，就可以使用Nginx来做服务器，同时现在也很流行动静分离，就可以通过Nginx来实现，动静分离是让动态网页很久一定规则吧不变得资源和经常变得资源区分开来，动静资源做好拆分之后，我们就可以根据静态资源的特点将其作缓存操作，这就是网站静态化处理的核心思路。

2、代理服务器

 **1）关于代理**

说到代理，我们首先明确一个概念，所谓代理就是一个渠道、一个通道。

就像我们去店里买鞋，分为客户、专卖店、鞋厂，我们需要鞋子的时候，如果直接去鞋厂买一定行不通的，我们需要去专卖店买，店里的鞋是鞋厂做的。客户对应客户端、专卖店对应代理、鞋厂对应服务端，客户端无法直接想服务端通信，代理可以向服务端通信，客户端向代理请求，代理将客户端的请求转发给服务端，实现客户端和服务器的通信。代理位于客户端与服务端之间，扮演“中间人”的角色。

 **2）正向代理**

正向代理是一个位于客户端和服务端之间。使用它，客户端不是直接到服务端请求数据，而是向地理服务器发送请求，请求先送到代理服务器，有代理服务器转发给服务端，数据返回也是如此。

 **3）反向代理**

在服务端结束客服端的请求，然后发请求分发给具体的服务器进行处理，然后再将服务器的响应结果反馈给客户端，Nginx就是其中的一个反向代理软件。正向代理，客户端必须设置正向代理服务器的IP地址和代理程序的端口，而反向代理正好与正向代理相反，对于客户端而言代理服务器就像服务端，并且客户端不需要进行任何特别设置。客户端向反向代理的命令空间中的内容发送普通请求，接着反向代理将判断向何处的服务端转交请求，并将获得的内容返回给客户端。

3、负载均衡

当网站访问量非常大的时候，需要将同一应用部署在多台服务器上，将大量用户的请求分配给多台机器处理。同时带来的好处是，其中一台服务器万一挂了，只要还有其他的服务器正常运行，就不会影响用户使用。

Nginx可以通过反向代理来实现负载均衡

负载均衡的意思就是分摊到多个操作单元上进行执行，例如：web服务器，FTP服务器等其他关键任务的服务器。从而共同完成工作任务，简单而言就是当有2台或以上服务器时，根据规则将请求分发到不同服务器处理，负载均衡配置一般都需要同时配置反向代理，通过反向代理跳转到负载均衡，而Nginx目前支持自带3种负载均衡策略，还有2种常用的第三方策略。

4、虚拟主机

有些网站访问量太小时，为了节约成本，将多个网站不符在同一台服务器上，例如将www.123.com和www.456.com两个网站部署在同一台服务器上，两个域名解析到同一个IP地址，但用户通过两个域名打开两个完全不同的网站，互不影响，就像访问两个服务器一样，所以叫虚拟主机。

    
    
    Nginx下载官网：
    http://nginx.org/en/download.html
    

![image.png](https://image.3001.net/images/20210429/1619680031_608a5b1f599b24fcf68a6.png!small)

## 二、Nginx环境安装

直接使用phpstudy部署Nginx+php环境

![1619678335_608a547f43729dcfae6c6.png!small?1619678335318](https://image.3001.net/images/20210429/1619678335_608a547f43729dcfae6c6.png!small?1619678335318)

访问80端口

![1619678345_608a54898af77cf47f75c.png!small?1619678346083](https://image.3001.net/images/20210429/1619678345_608a54898af77cf47f75c.png!small?1619678346083)

## 三 、Nginx文件解析漏洞

 **漏洞复现**

对于任意文件名，在后面添加/abc.php(abc为任意字符)后，即可将文件作为php解析。

创建一个jpg文件，并包含php代码

![1619678392_608a54b86af29675d8d26.png!small?1619678392738](https://image.3001.net/images/20210429/1619678392_608a54b86af29675d8d26.png!small?1619678392738)![1619678398_608a54be8e948b821a109.png!small?1619678399065](https://image.3001.net/images/20210429/1619678398_608a54be8e948b821a109.png!small?1619678399065)

访问phpinfo.jpg，在后面增加/abc.php，会将jpg文件以php格式解析

    
    
    http://192.168.43.136/phpinfo.jpg/abc.php
    

![1619678404_608a54c4a9daf63575686.png!small?1619678405061](https://image.3001.net/images/20210429/1619678404_608a54c4a9daf63575686.png!small?1619678405061)

**漏洞原理分析**

该漏洞是Nginx配置导致，与nginx版本无关，nginx.conf中配置

    
    
    /phpStudy/PHPTutorial/nginx/conf/nginx.conf`
    

![1619678460_608a54fc5b889eae4beb8.png!small?1619678460535](https://image.3001.net/images/20210429/1619678460_608a54fc5b889eae4beb8.png!small?1619678460535)

    
    
    server{
     location ~ \.php$ {
            #    root           html;
                fastcgi_pass   127.0.0.1:9000;
                fastcgi_index  index.php;
            #    fastcgi_param  SCRIPT_FILENAME  /scripts$fastcgi_script_name;
                fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;
                include        fastcgi_params;
            }
    }
    

当攻击者访问/phpinfo.jpg/abc.php时，Nginx将查看URL，看到他以.php结尾，并将路径传递给php
fastcgi处理程序，php看到/phpinfo.jpg/abc.php不存在，便删除去最后的/abc.php，看到phpinfo.jpg存在，而后以php的形式执行.jpg的内容。

这里php在执行/phpinfo.jpg/abc.php为什么找不到文件就会删除去最后的/abc.php呢？，这里涉及到php的有一个选择：cgi.fix_pathinfo，该配置默认为1，开启状态，表示对文件路径进行“修理”。何为”修理“，举个例子：当php遇到文件路径“/1.aaa/2.bbb/3.cccc"文件时，若“/1.aaa/2.bbb/3.cccc"不存在，则会去掉最后的”/3.ccc",然后判断“/1.aaa/2.bbb”是否存在，若不存在，则继续去掉“/2.bbb”,以此类推。

该配置在php.ini设置。若关闭该选项，访问/phpinfo.jpg/abc.php会返回找不到文件，但关闭该选项可能会导致一些其他初五，所有默认开启。

![image.png](https://image.3001.net/images/20210429/1619678561_608a55615ed6ab0386b4a.png!small)![image.png](https://image.3001.net/images/20210429/1619678568_608a5568a66f7124c9ff5.png!small)

在php.ini中为注释状态

在较新版本的php引入了“security.limit_extensions”配置，限制了php执行文件的后缀，默认只允许执行.php文件。该配置在php-fpm.conf文件中配置。如果想让php解析jpg，需要如下配置：

    
    
    security.limit_extensions = .php .jpg
    

根据上面测试，这一漏洞是有nginx中php配置不当而造成的，与nginx版本无关，但在高版本的php中，由于“security.limit_extensions”的引入，使得该漏洞难以被利用。

 **修复建议**

    
    
    1、配置cgi.fix_pathinfo(php.ini中)为0，并重启php-cgi程序。
    2、如果需要使用cgi.fix_pathinfo这个特性（例如：wordpress),那么就进制上传目录的执行脚本权限，或将上传存储的内容与网站分离，及站库分离。
    3、高版本php提供了security.limit_extensions（php-fpm.conf中)这个配置参数，设置security.limit_extensions = .php
    

## 四、目录遍历漏洞

 **漏洞简述**

Nginx的目录遍历与Apache一样，属于配置方面的问题，错误的配置可能导致目录遍历与源代码泄露。

 **漏洞复现**

修改C:\phpStudy\PHPTutorial\nginx\conf\nginx.conf，将autoindex修改为on，如下图所示：

![image.png](https://image.3001.net/images/20210429/1619678580_608a55742c83ccf42fd5a.png!small)

访问一个目录

![image.png](https://image.3001.net/images/20210429/1619678587_608a557b4254d0f5d9832.png!small)

 **修复建议**

    
    
    修改C:\phpStudy\PHPTutorial\nginx\conf\nginx.conf，将autoindex修改为off
    

## 五、空字节任意代码执行漏洞

 **漏洞简述**

Nginx在遇到%00空字节时与后段FastCGI处理不一致，导致可以在图中嵌入PHP代码然后通过访问1.jpg%00.php来执行其中的代码。

 **影响版本**

    
    
    nginx 0.5.*
    nginx 0.6.*
    nginx 0.7 <= 0.7.65
    nginx 0.8 <= 0.8.37
    

**漏洞复现**

在网上找到一个nginx 0.7.56+PHP 5.3.2环境的安装包，直接运行安装

![image.png](https://image.3001.net/images/20210429/1619678597_608a55859f0c49aa4fa8b.png!small)  
![image.png](https://image.3001.net/images/20210429/1619678605_608a558db2153945f8a9d.png!small)

访问80端口

![image.png](https://image.3001.net/images/20210429/1619678615_608a5597cc4fa100ce2ac.png!small)

在html目录下创建phpinfo.php测试nginx是否可以解析php

![image.png](https://image.3001.net/images/20210429/1619678627_608a55a3370fab4bc4307.png!small)

访问phpinfo.php

![image.png](https://image.3001.net/images/20210429/1619678640_608a55b05ab87f32b2f2a.png!small)

在html目录下创建1.jpg，内容为

    
    
    <?php phpinfo();?>
    

![image.png](https://image.3001.net/images/20210429/1619678678_608a55d63e2d8d6646c32.png!small)

访问1.jpg，无法解析文件中phpinfo函数

![image.png](https://image.3001.net/images/20210429/1619678701_608a55edadacb02f13f7c.png!small)

使用burp抓取访问1.jpg的请求报，并修改为1.jpg%00.php,请求成功。

![image.png](https://image.3001.net/images/20210429/1619678709_608a55f57845dde26aa28.png!small)

或者修改hex编码，将1.jpg修改为1.jpg..php，并将hex编码2e修改为00

修改前

![image.png](https://image.3001.net/images/20210429/1619678716_608a55fce242549833e71.png!small)

修改后

![image.png](https://image.3001.net/images/20210429/1619678722_608a56020a105409853d1.png!small)

重发请求，返回码为200，成功绕过

![image.png](https://image.3001.net/images/20210429/1619678736_608a56107c424b4d9601b.png!small)

该漏洞不受cgi.fix_pathinfo影响，当为0时，依旧可以解析

 **修复建议**

    
    
    1、临时解决方案：
    在nginx虚拟机配置或者fcgi.conf配置加如下代码
    if ( $fastcgi_script_name ~ \..*\/.*php ) {
    	return 403;
    }
    2、升级到最新版本的nginx可以很好解决问题。
    

## 六、CRLF（换行回车）注入漏洞

 **漏洞简述**

CRLF是“回车+换行”（\r\n)的检查，其十六进制编码分别为0x0d和0x0a。在HTTP协议中，HTTP header与HTTP
Body是用两个CRLF分隔的，浏览器就是根据这两个CRLF来取出HTTP内容显示出来。所以，一旦我们能够控制HTTP消息头中的字符，注入一些恶意的换行，这样我们就能注入一些回话Cookie或者HTML代码。CRLF漏洞常出现在Location与Set-cookie消息头中。

 **漏洞分析**

在nginx.conf中，在location位置添加配置，当用户访问nginx服务器时此配置实现强制跳转到https协议访问之前访问的链接。

![image.png](https://image.3001.net/images/20210429/1619678759_608a5627292f3272fe97d.png!small)

    
    
    location / {
    	return 302 https://$host$uri;
    }
    

上面的配置的关键利用点有两个：

1、配置中$uri是我们可以控制的，这样我们就可以在$uri处填入CRLF，然后对服务器进行访问实现头部注入。

2、服务器返回一个302跳转给用户，所以我们注入的头部参数又会返回到客户这里。

 **漏洞复现**

修改nginx.conf中配置，重启nginx

![image.png](https://image.3001.net/images/20210429/1619678766_608a562e81d59e5386b41.png!small)

访问链接

    
    
    http://192.168.43.136/%0ASet-cookie:JSPSESSID%3D1234
    

![image.png](https://image.3001.net/images/20210429/1619678812_608a565c8942c005cb040.png!small)

我们看到将1234通过set-cookie返回

CRLF+反射XSS配置

    
    
    http://192.168.43.136/%0D%0A%0D%0A%3Cimg%20src=1%20test=alert(/xss/)%3E
    

![image.png](https://image.3001.net/images/20210429/1619678830_608a566ebe8477ea3f10e.png!small)

为什么在浏览器没有返回弹窗呢，那是因为firefox对xss特征进行了过滤。

    
    
    原理请参考：
    https://www.leavesongs.com/PENETRATION/bottle-crlf-cve-2016-9964.html
    

老版本浏览器：

![image.png](https://image.3001.net/images/20210429/1619678843_608a567bbc4523e293d1c.png!small)

 **漏洞危害**

劫持合法用户回复，利用管理员身份进行恶意操作，篡改页面内容，进一步渗透网站等

利用CRLF Injection设置一个session，造成一个“回话固定漏洞”

 **CRLF深入配合渗透：**

    
    
    攻击者操作：
    1、攻击者先打开一个网站http://www.baidu.com,然后服务器回复他一个session id。比如SID=test。攻击者把这个ID记下来。
    2、攻击者给被攻击者发送一个电子邮件，他假装自己是推销什么，诱导攻击者点击链接http://yinhang/?SID=test,SID后面就是攻击者自己的session id。
    3、被攻击者被吸引了，点击了http://yinhang/?SID=test，像往常一样，输入了自己的账号口令从而登录到银行网站。
    4、因为服务器的seesion id不改变，现在攻击者点击http://yinhang/?SID=test后，他就拥有了被攻击者的身份了。就可以为所欲为了。
    

**修复建议**

    
    
    1、删除nginx.conf文件中return 302 https://$host$uri;部分，重启nginx
    

## 七、文件名逻辑漏洞（CVE-2013-4547)

 **漏洞简述**

这个漏洞主要原因是错误的解析了请求的URL，错误的获取到了用户请求的文件名，导致出现权限熬过，代码执行的连带影响。

我们需要上传一个空格结尾的文件，可使php解析。

 **影响版本**

    
    
    Nginx 0.8.41 ~ 1.4.3 / 1.5.0 ~ 1.5.7（linux系统）
    

**漏洞复现**

windows环境下不允许存在文件名后带空格的文件，因此复现使用vaulhub进行测试。

启动CVE=2013-4547环境

    
    
    cd /root/vulhub-master/nginx/CVE-2013-4547
    sudo docker-compose build
    sudo docker-compose up -d
    docker ps
    

![image.png](https://image.3001.net/images/20210429/1619678859_608a568b6c35eaa79fd86.png!small)

访问8080端口

![image.png](https://image.3001.net/images/20210429/1619678867_608a5693bc8f53c9b38f6.png!small)

上传1.jpg

![image.png](https://image.3001.net/images/20210429/1619678873_608a56997fecfcd836e1d.png!small)  
![image.png](https://image.3001.net/images/20210429/1619678878_608a569e038f0dcba99a1.png!small)

使用burp抓取，上传的1.jpg请求包,并在上传的文件名部分添加一个空格

![image.png](https://image.3001.net/images/20210429/1619678910_608a56be6dd73e6dd53fe.png!small)

上传文件

![image.png](https://image.3001.net/images/20210429/1619678920_608a56c8e4b43fb07f3f5.png!small)

访问连接

    
    
    http://192.168.43.129:8080/uploadfiles/1.jpg.php
    

![image.png](https://image.3001.net/images/20210429/1619678927_608a56cfdd9aca191ff0a.png!small)

修改请求头为/uploadfiles/1.jpg...php，并修改hex数据包将..修改为20（空格）、00（截止符\0）

修改前

![image.png](https://image.3001.net/images/20210429/1619678934_608a56d6d71e55e8228e3.png!small)

修改后

![image.png](https://image.3001.net/images/20210429/1619678940_608a56dc17ed9aff034b9.png!small)

访问成功

![image.png](https://image.3001.net/images/20210429/1619678947_608a56e302bf44c527a07.png!small)  
![image.png](https://image.3001.net/images/20210429/1619678951_608a56e770633b1d061ab.png!small)

成功绕过

 **漏洞分析**

Nginx匹配到.php结尾的请求，就会发送给php-fastcgi进行接，该源码如下：

![image.png](https://image.3001.net/images/20210429/1619678969_608a56f9b5ead2cece4ba.png!small)

    
    
    location ~ \.php$ {
               root           html;
               include        fastcgi_params;
               fastcgi_pass   php:9000;
               fastcgi_index  index.php;
               fastcgi_param  SCRIPT_FILENAME  /var/www/html$fastcgi_script_name;
               fastcgi_param  DOCUMENT_ROOT /var/www/html;
            }
    

关闭pathinfo的情况下，只有.php后缀的文件才会被php-fastcgi解析

而存在CVE-2013-4547的情况下，我们请求1.jpg0x\200x\00.php,这个URL可以匹配上正则.php$,可以进入这个location代码块，但进入后，nginx却错误的认为请求文件时1.jpg0x\20,就设置为SCRIPT_FILENAME进行解析，最后导致解析漏洞。所以，我们只需要上传一个空格结尾的文件，即可使php解析。

 **修复建议**

    
    
    去除location ~ \.php$中最后的$,重启nginx
    

