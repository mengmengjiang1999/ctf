## 前言

​
一直以来都没有系统地总结过信息搜集方面的东西，都是看其他师傅的文章，最近想着自己也来总结总结，如有错误或不足欢迎各位师傅指出。关于信息搜集的重要性我也不再赘述了，想必各位都清楚。

​ 接下来进入正题~

## web信息收集

### 域名信息的收集

域名收集的必要性

有些域名其名字本身就能表示其特征，如含有mail的域名则是用于邮箱服务的。不同的域名可能对应不同的IP地址，收集到的域名越多，攻击面也会相应增大。

子域名收集的方法

 **工具**

[OneForAll](https://github.com/shmilylty/OneForAll)

优点：功能多、输出格式全、数量多

缺点：存在较多误收集

[Layer子域名挖掘机](https://www.aliyundrive.com/s/54jj9cnE2gb)

优点：字典很大

缺点：速度慢

[subDomainBrute](https://github.com/lijiejie/subDomainsBrute)

优点：爆破速度快、准确度高

缺点：数量相对较少

 **网站查询**

在线子域名查询 https://phpinfo.me/domain/ （速度快但有误报）

在线子域名查询 http://tools.bugscaner.com/subdomain/

在线子域名查询 https://chaziyu.com/

DNSGrep 子域名查询（支持导出）https://www.dnsgrep.cn/subdomain

在线查询（支持导出） https://dnsdumpster.com/

 **其他方法**

利用证书透明度收集子域

在线网站：https://crt.sh/

利用谷歌语法

site:example.com -www （-是不包含）

site:x.x.x.*(目标IP)

当获取到子域名的真实ip后可以使用该语法进行C段搜索，获取其他相关域名。

通过JavaScript文件搜集

工具：

SubDomainizer：https://github.com/nsonaniya2010/SubDomainizer

JSFinder：https://github.com/Threezh1/JSFinder

xray的rad爬虫 https://github.com/chaitin/rad

## whois信息查询

whois是用来查询域名注册所有者等信息的传输协议。通过whois查询可以知道网站的联系人、邮箱、电话等信息，这些信息可以通过whois反查获取更多相关的域名数据，并且这些信息如果是网站管理员的，可以保留下来用于生成密码字典，用于网站后台密码爆破等。

查询网站：站长之家 http://whois.chinaz.com/

## 备案信息查询

在备案查询中我们主要关注的是：单位信息例如名称、备案编号、网站负责人、法人、电子邮箱、联系电话等。

 **查询网站** ：

ICP/IP地址/域名信息备案管理系统：http://beian.miit.gov.cn/publish/query/indexFirst.action

备案吧吧：https://www.beian88.com/

天眼查：https://www.tianyancha.com/

查询域名对应IP

首先需要判断是否使用CDN。

> CDN的全称是Content Delivery
> Network，即[内容分发网络](https://baike.baidu.com/item/%E5%86%85%E5%AE%B9%E5%88%86%E5%8F%91%E7%BD%91%E7%BB%9C/4034265)。CDN是构建在现有网络基础之上的智能虚拟网络，依靠部署在各地的边缘服务器，通过中心平台的负载均衡、内容分发、调度等功能模块，使用户就近获取所需内容，降低网络拥塞，提高用户访问响应速度和命中率。--《百度百科》

简单说就是提高了用户的访问速度，同时隐藏了真实IP，有的还提供了WAF功能。

    
    
    判断是否使用CDN的方法：使用多地ping，查看对应IP是否唯一，如果不唯一则很可能使用了CDN。
    

ping测试网站：

https://wepcc.com/

https://www.17ce.com/

http://ping.chinaz.com/

[绕过CDN查找真实IP的8种方法](https://cloud.tencent.com/developer/article/1634648)

未使用CDN查找IP的方法

在线查询：

https://tools.ipip.net/domain.php

https://www.ip138.com/

## 网站指纹识别

识别出网站所用的cms能很大程度上提高后续渗透的成功率。

常见的CMS有Dedecms(织梦)、Discuz、PHPWEB、PHPWind、PHPCMS、ECShop、Dvbbs、SiteWeaver、ASPCMS、帝国、Z-Blog、WordPress等。

![image](https://image.3001.net/images/20210802/1627882045_6107823d307198e7a2be8.png!small)

在线指纹识别网站：

BugScaner：http://whatweb.bugscaner.com/look/

WhatWeb： https://whatweb.net/

数字观星指纹平台：https://fp.shuziguanxing.com/#/

云悉指纹：http://www.yunsee.cn/finger.html（需要注册登录）

Wappalyzer 指纹识别 (浏览器插件)：https://github.com/AliasIO/wappalyzer

## 网站容器识别

常用的网站容器有Apache、Nginx、Tomcat
、IIS等等。识别出容器有利于我们之后搜索是否有相应漏洞能直接利用，这一点与cms同理。一般手动就能测试出来。通过抓包分析http头、使网站显示404报错等方式即可得知。工具的话还是使用whatweb。

## 网站数据库识别

方法：

端口扫描

常见数据库的对应端口号：

MySQL：3306

Mssql：1433

Oracle：1521

Microsoft SQL Server：1433

PostgreSQL：5432

MongoDB：27017

Redis：6379

Access无端口

当然，一般都扫不出来，但是常用的就那几种

常用搭配

ASP和.NET：Microsoft SQL Server  
PHP：MySQL、PostgreSQL  
Java：Oracle、MySQL

JSP：Mssql、Oracle

通过SQL注入信息判断，参考文章https://www.bugfor.com/vuls/5167.html

服务器操作系统识别

 **通过大小写判断** 。windows对大小写不敏感，linux相反。

 **ping测试**
。Windows的TTL值都是一般是128，Linux则是64。所以大于100的肯定是Windows，而几十的肯定是Linux。但这个方法不是百分百准确，而且有的服务器禁止ping。

 **使用nmap** 。命令：nmap -O ip地址

robots协议

robots协议也叫robots.txt（统一小写）是一种存放于网站根目录下的ASCII编码的文本文件，它通常告诉网络搜索引擎的漫游器（又称网络蜘蛛），此网站中的哪些内容是不应被搜索引擎的漫游器获取的，哪些是可以被漫游器获取的。--《百度百科》

直接访问 **地址/robots.txt** 获取相关目录地址信息。一般是访问不了的，但是还是需要知道。

端口信息搜集

搜集端口的常用方法

工具

nmap（神器不用多说）

[masscan](https://github.com/robertdavidgraham/masscan)（号称可以5分钟扫遍互联网）

[Advanced Port Scanner](https://www.advanced-port-scanner.com/cn/)

在线网站

http://tool.chinaz.com/port/

http://coolaf.com/tool/port

常用端口及其对应服务

[常用端口及功能](https://docs.ksyun.com/documents/793)

常用的端口攻击可参考：https://www.cnblogs.com/botoo/p/10475402.html

目录信息搜集

网站敏感文件

源码备份文件（常见后缀）：

> .tar
>
> .tar.gz
>
> .zip
>
> .rar
>
> .7z
>
> .bak
>
> .old
>
> .txt
>
> .git
>
> .swp
>
> ........

如果扫描到备份文件，那就爽歪歪了。

目录扫描

常用工具：

御剑

[dirsearch](https://github.com/maurosoria/dirsearch)

[DirBuster](https://sourceforge.net/projects/dirbuster/)（如果打开发现没有启动按钮，记得把工具界面的尺寸调大！）

目录结构爬取

通过扫描工具爬行整个web目录结构，其中可能包括后台地址等。使用带有爬虫功能的工具即可。burpsuit也行。

信息搜集的其他方面或方法

方便好用的网络测绘工具

[zoomeye](https://www.zoomeye.org/?R1nG)

[fofa](https://fofa.so/)

[shodan](https://www.shodan.io/)

[360](https://quake.360.cn/quake/#/index)

公司相关信息搜集

[天眼查](https://www.tianyancha.com/)、[企查查](https://www.qcc.com/)、[启信宝](https://www.qixin.com/)等

github搜源码或相关敏感信息，搜索语法https://blog.csdn.net/qq_36119192/article/details/99690742

判断WAF类型

[wafw00f](https://github.com/EnableSecurity/wafw00f)

Google hacking

常用语法：

 **intitle** ：搜索网站标题含有的关键字

 **inurl** ：搜索url含有的关键字

 **intext** ：搜索网页正文含有的关键字

 **site** ：搜索特定网站和网站域名

 **filetype** ：搜索特定文档格式

旁站查询

主站往往防护很好，这时可以通过从旁站入手，达到“曲线救国”的目的。

一些在线查询网站：

https://chapangzhan.com/

https://www.webscan.cc/

https://dns.aizhan.com/

C段扫描

这里的C段指的是并非网络中的C类地址，而是C类地址中子网掩码为255.255.255.0/24中的IP地址段，共254个。对于红蓝对抗和护网比较有意义。

通常使用nmap进行扫描。

主机扫描(Nessus)

对目标主机进行扫描，扫描目标主机开放了哪些端口，扫描端口运行的服务，目标主机上有哪些漏洞。一般使用Nessus，Nessus针对的是操作系统及操作系统所安装的软件进行漏洞分析。

网站漏洞扫描

直接使用工具进行扫描，缺点是容易被封IP，小站容易被扫崩，有误报，且未授权使用不合法。优点是在授权的前提下，可以通过前期一系列的资产信息收集，使用自动化工具先替你扫一遍，剩下的再手动测试。

常用工具有AWVS、AppScan、OWASP-ZAP、goby、xray等等。

有无其他应用

七麦数据：https://www.qimai.cn/ 可以查到企业下一些比较冷门的app。

一些小推荐

github上面的一个项目：https://github.com/r0eXpeR/Online_Tools 里面有很多信息查询的网站，可自行选择使用。

VulScanner：https://github.com/passer-W/VulScanner 王小明师傅最近写的一款漏洞检测工具，给大家安利一波

总结

​
通过完成这篇小结文章，使自己对信息搜集的途径和方法都更加清晰了。引用一下安全圈的经典名句，“渗透的本质是信息搜集”。诚然，攻击面不仅取决于知识面，也取决于你所搜集到的信息是否足够全面。当你搜集到的信息足够多时，往往漏洞也就离你越来越近了。最后，这是本人写的第二篇文章，不足之处在所难免，希望看到的师傅们能够多多包涵。

## 参考链接

> https://blog.csdn.net/qq_36119192/article/details/84027438
>
> https://security.tencent.com/index.php/blog/msg/161
>
> https://blog.csdn.net/qq_36119192/article/details/84068625
>
> https://www.freebuf.com/articles/web/251083.html
>
> https://www.freebuf.com/sectool/266457.html
>
> https://xz.aliyun.com/t/8501

