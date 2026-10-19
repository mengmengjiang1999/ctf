# 虎汪大战之phpmyadmin篇

阅读量 **544089**

发布时间 : 2022-06-01 15:30:47

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0191c7a1ae70f9b16a.jpg)

> 欢迎 **《黑客X档案》作者 yizhigu** 入驻银弹实验室。  
>  **《黑客X档案》** ：黑客X档案是国内发行量最大的网络安全（电脑黑客）类杂志，也是一本面向大众的普及类网络安全杂志。

* * *

> 作者 | yizhigu,master  
>  编辑 | Ann

## 01 开战

**【大家好，我是汪星人yizhigu】**

虎汪大战即将拉开帷幕，这日我正在筹备我的兵器库。汪星好友Master在群中发来求助，遇到 **AppServ的WAMP套件**
不知如何下手，正巧另一汪星好友CNIU也闻声赶来，虎汪大战一触即发。

![](https://p4.ssl.qhimg.com/t0110e140a5518ee310.png)

CNIU说时迟那时快，使用dirsearch对WEB目录进行了一番雷达探测，结果令人失望。这种套件我在多年前经常遇到，也是非常熟悉。这时CNIU查到了一个万能账户’localhost’@’@”顺利进入了phpmyadmin的控制台，实际上用户名中包含@字符，即可成功进入控制台，
汪星的前辈曾经告诉过我们， **当用户名输入@@，密码为空即可成功登录**
。phpmyadmin的版本2.10.3，确实很古老，我们进来的账户是匿名权限，仅可看到test库。

## 02 协作

多年前，自己对APPSERV套件曾经做过研究，利用@@进入到phpmyadmin控制台后，如果存在CMS系统就读取数据库配置文件，
**如果没有CMS系统拿不到配置文件的情况下是可以另辟蹊径的，就是读取mysql数据下的MYD文件进行分析**
，最终拿到root密码并实现最终的getshell。（贴出N年前的记录）

![](https://p3.ssl.qhimg.com/t0178c56dfb9eb216f8.png)

成功的语句历历在目，马上执行SQL语句开始我们的攻城拔寨。

![](https://p2.ssl.qhimg.com/t013de989d73dee7c7c.png)

沃勒个去，居然被WAF无情拦截

![](https://p2.ssl.qhimg.com/t01a4f782832d74a5af.png)

**一般情况下WAF是不会拦截phpmyadmin的数据库语句操作，这里可能是某些硬防进行了全方位的拦截**
，记得之前APPSERV自带的phpinfo页面也是访问直接被拦截。在SQL语句处进行了一些简单测试，就是一个很常规的正则，同时出现相关字符串就进行拦截。

看来目标开启了 **“虎视眈眈”**
模式，让我们无处遁形。汪星好友Master和CNIU也顿时陷入僵局，这个时候我想到了之前phpmyadmin的XXE漏洞，测试以下代码进行导入操作，也被WAF拦截了。

<?xml version=”1.0” encoding=”ISO-8859-1”?>  
<!DOCTYPE foo [  
<!ELEMENT foo ANY >  
<!ENTITY xxe SYSTEM “file:///c:/boot.ini” >]><foo>&xxe;</foo>

正当我一愁莫展的时候，CNIU在群里告知可以在 **导入处提交sql文件，写入语句即可绕过WAF** 。

whatfuck!原来“虎视眈眈”也不过是个 **“纸老虎”** 。

![](https://p5.ssl.qhimg.com/t011c5b29600922b06b.png)

这下问题来了，没有phpinfo，又不是默认路径，难道要猜测？要爆破？

正当我的大脑飞速运转时，Master大汪居然想到了老版本的路径报错漏洞，顺利拿到了web路径。有两位大汪坐镇，我也开启了SPORT模式，以180迈冲了出去。

![](https://p2.ssl.qhimg.com/t016c74d5ca21c9444e.png)

新建一个1.sql贴入以下语句

> create table test(cmd blob);  
>  LOAD DATA LOCAL INFILE ‘D:/AppServ/MySQL/data/mysql/user.MYD’ INTO TABLE
> test fields terminated by ‘’ LINES TERMINATED BY ‘\0’;  
>  select hex(cmd) from test;

**执行后把结果复制并粘贴到HEXWORKSHOP,组成40位MYSQL5的SHA1哈希。**

![](https://p4.ssl.qhimg.com/t01b9987f604a2b0b4d.png)

成功破解出明文后以root权限进入后台，由于WAF不拦截select into outfile的语句，所以可以随意写入一个文件。

![](https://p1.ssl.qhimg.com/t017e9abd7e5c7f4321.png)

## 03 攻陷

因为此处存在WAF，写入常规的一句话十有八九会被拦截。所以需要写入哥斯拉等其他加密shell并进行连接，为了照顾某些新手小汪，这里还是提及一下getshell的流程。

首先把shell代码贴入到相关转换工具，由于我是个老汪，用的是CAL9000，大家可根据自我喜好使用例如burpsuite等工具。

![](https://p2.ssl.qhimg.com/t0141b1d9ebe0eb681c.png)

转换成功后可使用语句写入webshell，最后成功连上。  
 **select converthex into dumpfile ‘D:/AppServ/www/pthwaf.php’**

![](https://p1.ssl.qhimg.com/t0106b4023abbac1997.png)

## 04 收官

回望此次虎汪大战，感触颇深。最后的成功在于团队的通力协作，
**没有CNIU对于phpmyadmin控制台的探索以对抗WAF，没有Master丰富的作战经验想到的报错路径，可能此番交手并非一帆风顺**
。谨以此文，告知各位小伙伴，再聪明的大脑，也敌不过团队的高效，正所谓“三个臭皮匠,顶个诸葛亮”。希望大家以后遇到此类环境和WAF的时候，能够举一反三，为虎汪大战添上浓墨重彩的徽章！

多年未撰稿，笔下意犹未尽。古语曰“万般皆下品，惟有读书高”，
今日我云“万物皆是唯一，协作才最牛逼”。希望大家都能“厚德载物，一言九鼎”，物鼎安全欢迎小伙伴的加入！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **银弹实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/273746](/post/id/273746)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [phpMyAdmin](/tag/phpMyAdmin)

 **+1** __2赞

 __收藏

![](https://p1.ssl.qhimg.com/t01ab7127bf75817f0a.png) 银弹实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

