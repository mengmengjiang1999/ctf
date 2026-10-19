**AssassinGo是一款使用Golang开发，集成了信息收集、基础攻击探测、Google-Hacking域名搜索和PoC批量检测等功能的Web渗透框架，并且有着基于Vue的WebGUI，前后端交互主要采用WebSocket，结果实时显示在前台。并且扩展性强，实现各模块接口即可添加功能。**  

> 网站地址：[https://assassin-go.ink](https://assassin-go.ink/)
>
> github地址：<https://github.com/AmyangXYZ/AssassinGo>

![](https://image.3001.net/images/20180528/15275056123014.png!small)

##  0x00 主要功能

###  1.信息收集部分a) 检查HTTP安全头

> b) CMS版本识别
>
> c) 蜜罐概率检测
>
> d) CloudFlare绕过
>
> e) 路由节点跟踪并标记在googlemap上
>
> f) 端口扫描
>
> g) 目录爆破和可视化的sitemap
>
> h) Whois信息

![](https://image.3001.net/images/20180529/15275735249755.png!small)

###  ![](https://image.3001.net/images/20180528/15275085568920.png!small)

###  2\. 基础攻击部分

> a) 整站爬虫
>
> b) SQLi检测
>
> c) 反射型xss
>
> d) Burp的Intruder功能
>
> e) SSH爆破

下个版本会将爬虫和XSS检测也升级成headless-chrome版本

![](https://image.3001.net/images/20180528/15275087532681.png!small)

###  3\. Google-Hacking

后端调用Headless-Chrome爬取google或bing搜索结果，完全支持google-hacking语法，而且不会被反爬虫检测。

###  ![](https://image.3001.net/images/20180528/15275087704715.png!small)4\.
PoC检测

选择PoC进行单个或批量检测。

![](https://image.3001.net/images/20180528/15275087326509.png!small)

##  **0x01 概要设计**

后端实现选用了组合模式，

![](https://image.3001.net/images/20180528/15275057297764.png!small)

信息收集接口Gatherer、基本攻击接口Attacker、漏洞PoC验证接口基本相同，均包含下列三种方法：

> a) Set(...interface{})：设置本函数或PoC所必需的参数，如目标、端口、并发数量等等。
>
> b) Run()：函数启动入口。
>
> c) Report() map[string]interface{}：返回执行结果，为后续生成报告准备。

而PoC接口还需要额外实现Info() string方法，返回该漏洞的基本信息。

当添加新的功能或更新PoC时仅需编写一个新的.go文件并实现对应接口的方法。

例如当新公布出一个远程代码执行漏洞的PoC时，我们可直接新建一个xx-rce.go文件（参考已写好的几个PoC），实现上述接口，重新编译整个项目之后（Go语言的编译时间仅为数秒）即可在前台调用该PoC去检测目标。

##  0x02 项目进度

基本功能已开发完，部署了一个demo版本，

由于服务器性能有限，并未开放注册，大家想体验可以联系我手动注册（amyang.xyz@gmail.com），

或者在自己本地搭建，必要的shell脚本和docker-compose已写好。

由于团队人手十分有限，很多地方不是很完善，PoC也没有积攒几个，希望大家体谅。

 ***本文作者：Amyang，转载请注明来自FreeBuf.COM**

