## 前言

在某次金融类众测项目中，笔者发现了一个几乎无从下手的系统，直接访问系统无任何功能，几乎相当于404 Not
Found，甚至连JavaScript文件一个都不存在，最终通过渗透经验和一定的运气，拿下了这个高危SSRF漏洞，获得高额漏洞奖金，在此分享一下漏洞挖掘过程，带给大家渗透测试中的一点另类思路~

## 404 Not Found？

首先，给定的系统地址为：[http://xxx-desktop.xxx.com/](http://njbh-desktop.bcs.cmbchina.com/)

直接访问一下目录看一看：

![1614878018_6041154285fb4015089f1.png!small?1614878019267](https://image.3001.net/images/20210305/1614878018_6041154285fb4015089f1.png!small?1614878019267)

打开发现一片空白，但是页面空白并不代表是真的空白，HTML源码中可能会加载一些JavaScript文件，渗透测试时，往往会通过页面中直接泄露加载的
**JavaScript** 文件，进行审计 **JavaScript** 源码，从而挖掘出更多有用的信息。

对如何挖掘JavaScript文件中漏洞，可移步笔者之前发布的真实漏洞案例文章：[https://www.freebuf.com/vuls/255640.html](../vuls/255640.html
"前端JavaScript渗透测试步步为营")

回归正题，下一步找寻HTML源码中可能存在的泄露点，直接查看网页源码：

![1614878501_60411725c0c485abffe77.png!small?1614878501889](https://image.3001.net/images/20210305/1614878501_60411725c0c485abffe77.png!small?1614878501889)

仔细阅读源码，不知道细心的同学有没有发现，其中有3个线索可以延伸利用。

    
    
    libs/plugins/jquery.js
    ./html/apply.html?data=
    cxx/token/decrypt

第1点： **libs/plugins/jquery.js** ，加载了JavaScript文件，其路径是： **http://xxx-desktop.xxx.com/libs/plugins/jquery.js**

不过，此处 **jquery.js** 完全为前端文件，无任何可利用的信息，于是略过。

![1614878929_604118d174eb9826b5238.png!small?1614878929569](https://image.3001.net/images/20210305/1614878929_604118d174eb9826b5238.png!small?1614878929569)

第2点： **html/apply.html?data=** ，加载了当前目录下一个html文件，路径为： **http://xxx-desktop.xxx.com/html/apply.html?data=**

结果也是一无所获，经典Nginx的404 NOT Found。

![1614879118_6041198eb7676fd316ad8.png!small?1614879118798](https://image.3001.net/images/20210305/1614879118_6041198eb7676fd316ad8.png!small?1614879118798)

第3点： **cxx/token/decrypt** ，猜测为接口路径。

访问发现也是404，大概是还存在一层接口目录。

![1614879345_60411a715c27767ebb3ce.png!small?1614879346528](https://image.3001.net/images/20210305/1614879345_60411a715c27767ebb3ce.png!small?1614879346528)

一番信息收集后无果后，接下来就是展现真正的技术了！

## 403 Forbidden？

虽然上面的3个可用信息都Pass掉了，不过我们还是猜测，在两个路径之前，可能还存在一层Web应用目录亦或是接口目录，随后展开对Web目录的尝试性爆破，选用一些常见的一级目录。

最终获取到3个403禁止访问的目录：

![1614879604_60411b74aaf7a69731224.png!small?1614879604706](https://image.3001.net/images/20210305/1614879604_60411b74aaf7a69731224.png!small?1614879604706)

    
    
    http://xxx-desktop.xxx.com/html/
    http://xxx-desktop.xxx.com/css/
    http://xxx-desktop.xxx.com/js/

看来第一次发现得 **/html/** 目录确实存在，不过可能是 **apply.html** 不存在导致页面的404 Not Found。

一级目录爆破，未发现可用一级目录，仅仅发现了3个 **静态文件目录** 。

渗透测试的思路到这也即将中断了，不过此时突然萌生出一个想法：既然不存在能够正常使用的文件，那么我就继续去挖掘 **403** 目录下的文件，至少
**403** 比 **404** 要好多了，至少它是真实存在的目录！

## SSRF漏洞

继续对 **/html/** 目录、 **/css/** 目录尝试进行敏感文件扫描，未果。

使用 **Burpsuite** 的 **Intruder** 模块对 **/js/** 目录进行 **JavaScript**
文件爆破，终于获取到了可用信息！

![1614880052_60411d34a46296c3ec9a2.png!small?1614880052814](https://image.3001.net/images/20210305/1614880052_60411d34a46296c3ec9a2.png!small?1614880052814)

天哪，终于是获取到了3个JavaScript文件，是什么时候变成了连发现JavaScript文件都无比激动？

JavaScript文件如下：

> http://xxx-desktop.xxx.com/js/apply.js
>
> http://xxx-desktop.xxx.com/js/pagination.js
>
> http://xxx-desktop.xxx.com/js/common.js

通过进一步的信息收集，在 **/js/common.js** 文件中发现发现了一级接口目录： **/xxxapi/**

一级接口目录都做的这么复杂，也难怪目录爆破的时候没有成果了。

![1614880314_60411e3a592e9267dd789.png!small?1614880314457](https://image.3001.net/images/20210305/1614880314_60411e3a592e9267dd789.png!small?1614880314457)

在 **/js/apply.js** 文件中发现了系统接口： **file/pdf/view?file=**

![1614880492_60411eec0c2b95fbb8cc6.png!small?1614880492254](https://image.3001.net/images/20210305/1614880492_60411eec0c2b95fbb8cc6.png!small?1614880492254)

将一级接口目录 **/xxxapi/** 与系统接口 **file/pdf/view?file=** 进行拼接，组成可用接口：

    
    
    http://xxx-desktop.xxx.com/xxxapi/file/pdf/view?file=

并且发现JavaScript代码中的逻辑是： **接口 + ecsUrl** ，因此猜测 **file** 参数为一个URL。

接下来尝试调用接口进行SSRF利用。

首先，使用VPS监听端口，尝试直接利用SSRF访问我们的端口，发现成功接收到了Java语言进行的HTTP请求！

![1614880811_6041202bbdfcf160c878b.png!small?1614880811954](https://image.3001.net/images/20210305/1614880811_6041202bbdfcf160c878b.png!small?1614880811954)

至此证明了漏洞是存在的，接下来利用 **SSRF** 进行内网资源的请求尝试，由于在之前的测试中，已经收集到了一部分内网资产，所以直接拿过来测试访问即可。

测试访问内网 **Elasticsearch** 服务： **http://10.x.x.191:9200**

    
    
    GET /xxxapi/file/pdf/view?file=http://10.x.x.191:9200/ HTTP/1.1
    Host: xxx-desktop.xxx.com
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close

![1614881182_6041219e1e1293cec95b7.png!small?1614881182284](https://image.3001.net/images/20210305/1614881182_6041219e1e1293cec95b7.png!small?1614881182284)

测试访问内网 **Web应用** 服务：http://10.x.x.65:8081/

    
    
    GET /xxxhapi/file/pdf/view?file=http://10.x.x.65:8081 HTTP/1.1
    Host: xxx-desktop.xxx.com
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    

![1614881356_6041224c66dce862b7fb7.png!small?1614881356533](https://image.3001.net/images/20210305/1614881356_6041224c66dce862b7fb7.png!small?1614881356533)

至此，捕获了一枚相当于搭建了一条内网HTTP隧道的高危SSRF漏洞。

## 结语

此次漏洞挖掘中总结到如下几点：

 **1\. 系统无功能、无JavaScript文件、访问空白，尝试在HTML源码中获取一些信息；**

 **2\. 尽可能的在有用的信息中发掘更多的利用点，拓展思路；**

 **3\. “404”确实是“404”，而“403”有时候并不是“403”。**

> 从开始的 “404” Not Found，
>
> 到中间的 “403” Forbidden，
>
> 再到最后的高危SSRF漏洞；
>
> 每一步都仿佛是被上天安排好的剧本那样，
>
> 像是一次运气游戏，
>
> 又像是一场美丽的相遇。

也许挖洞一直都是这样，简单的漏洞随手可得，艰难的挖掘过程才会让人回味无穷~

希望能给大家带来一些简单的挖洞思路~

谢谢！

欢迎加入漏洞挖掘交流群交流~ 可加我：aedovo

