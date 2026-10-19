## 1、Nginx简介

Nginx是一款轻量级的web服务器/反向代理服务器及电子邮件服务器，特点是占用内存小，并发能力强

## 2、漏洞原理

CGI：是一种协议，定义了web服务器传递的数据格式。

FastCGI：优化版的CGI程序

PHP-CGI：PHP解释器，能够对PHP文件进行解析并返回相应的解析结果

PHP-FPM：FastCGI进程管理程序

当Nginx得到一个用户请求时，首先对url进行解析，进行正则匹配，如果匹配到以.php后缀结尾的文件名，会将请求的PHP文件交给PHP-CGI去解析。其中处理模块如下：

    
    
    location ~ \.php$ {
        root           html;
        include        fastcgi_params;
    
        fastcgi_pass   IP:9000;
        fastcgi_index  index.php;
        fastcgi_param  SCRIPT_FILENAME  /var/www/html$fastcgi_script_name;
        fastcgi_param  DOCUMENT_ROOT /var/www/html;
    }
    

以.php结尾的文件都会交给该模块处理，其中fastcgi_pass就是Nginx与PHP-FPM之间的媒介，通过ip+port的方式将请求转发给PHP解释器

 **CVE-2013-4547漏洞**
是由于非法字符空格和截止符导致Nginx在解析URL时的有限状态机混乱，导致攻击者可以通过一个非编码空格绕过后缀名限制。假设服务器中存在文件‘123.png
'，则可以通过访问如下网址让服务器认为'123.png '的后缀为php

    
    
    http://192.168.146.1/123.png \0.php
    

从代码层面来说，我们请求的url中123.png[0x20][0x00].php正好与location模块中的.php相匹配，但进入该模块后Nginx确认为请求的文件名是'123.png
'，就设置其为script_name的值交给CGI进行解析，最终造成解析漏洞

## 3、影响版本

Nginx 0.8.41 ~ 1.4.3 / 1.5.0 ~ 1.5.7

## 4、漏洞复现

进入/vulhub/nginx/CVE-2013-4547，启动靶场环境：docker-compose up -d

利用攻击主机浏览器访问：http://靶机ip:8080，利用该图片上传页面，上传一个图片webshell，代码如下：

    
    
    GIF98A
    <?php phpinfo(); ?>
    

上传时抓包进行重命名：’phpinfo.png '，记得后面有空格

![图片.png](https://image.3001.net/images/20210812/1628772702_6115195ea6b9eaee93db8.png!small)

访问上传的图片马，可以正常访问

使用0x00截断将图片马解析为PHP文件，访问该url并抓包修改http://192.168.146.134/uploadfiles/phpinfo.png
a.php  
原始请求抓包如下：  
![图片.png](https://image.3001.net/images/20210812/1628772729_611519795e5ab3ff1bd67.png!small)

a作为占位符，将%20删除后进入Hex中把表示a的61修改为00，最后发送请求

![图片.png](https://image.3001.net/images/20210812/1628772760_61151998ec622c074f95c.png!small)

最终发送的请求包如下

![图片.png](https://image.3001.net/images/20210812/1628773110_61151af6ab23328edaa54.png!small)

按照上述修改后Nginx收到的请求就变为了：http://192.168.146.134/uploadfiles/phpinfo.png
\0.php，使得png被解析为了PHP

![图片.png](https://image.3001.net/images/20210812/1628772775_611519a76a07cec1d27c6.png!small)

## 5、漏洞修复

将Nginx升级到1.5.7之后

