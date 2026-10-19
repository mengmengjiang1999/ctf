***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：davichi8282，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 0×00概述

 **近期在审计HDWiki
6.0最新版cms的时候发现由referer导致的sql注入问题。SQL注入我们知道是由于代码与数据没有严格区别限制分离而导致的问题，OWASP TOP
10常年把SQL注入放在TOP 1的位置，可知SQL注入的危害以及影响力是很大的。**

SQL注入我们一般平时寻找的时候习惯性的只从GET,POST提交的数据进行测试（比如跑sqlmap的时候），但是其实如果我们仔细一想注入产生的条件是什么，SQL注入是客户端提交的数据未严格过滤限制进入数据库执行而导致的问题，只要是与数据库可以交互的地方都可能存在SQL注入问题，这点白盒审计的时候经常会遇到，比如cookie注入，User-Agent注入，referer注入，X-Forwarded-For注入等，这些点都是可以与数据库进行交互的，如果未作严格限制，就会导致注入问题。

## 0×01 白盒审计

源码信息：HDwiki v6.0  

问题文件： \hdwiki\control\user.php

漏洞类型：sql注入

站点地址：<http://kaiyuan.hoodong.com/download/>

环境：php版本小于5.4且开启gpc

具体安装就不讲了，遇到问题可以百度一下哈。

安装成功之后进入主界面如下，

![3.png](https://image.3001.net/images/20180430/15250661114071.png!small)

可以看到存在登录页面，好我们去看下登录部分存不存在问题；

通过白盒审计工具seay我们找到登录部分为control/user.php

![@VXVXK9L6J3Z7H}6W3I02VS.png](https://image.3001.net/images/20180430/15250663722235.png!small)

可以看到dologin()函数里add_referer()函数，继续跟进此函数；

![RVBC~\(\(W\]S3@TI5A`J41Y`Q.png
](https://image.3001.net/images/20180430/15250666438843.png!small)

在model/user.class.php文件里，超全局变量$_SERVER['HTTP_REFERER']带入数据库而执行，也就是referer参数，但是我们看到前面存在haddslashes函数，是用来过滤的，继续跟进此函数；

在lib/string.class.php文件里

![4`$\(_MTSX\(CDM}MLJ_84Y}K.png
](https://image.3001.net/images/20180430/1525066994524.png!small)

此函数确实是过滤用户输入的，当gpc未开启的时候使用addslashes()函数进行过滤，当开启gpc的时候直接返回，那么问题就来了，当php开启gpc的时候直接返回字符串，但是gpc是只针对$_GET,$_POST,$_COOKIE三种超全局变量进行过滤的，即referer是不受限制的，还有gpc在php版本大于等于5.4之后是弃用的，所以当php版本小于5.4的时候只要php开启gpc,referer就不受任何过滤直接带入数据库执行，所以就存在注入问题了。

##  **0×02 漏洞利用**

此处由于没有任何数据的回显只能通过盲注进行SQL注入，我们使用延时注入，我们使用抓包工具burpsuite抓取登录界面如下；

    
    
    http://127.0.0.1/HDWiki-v6.0UTF8-20170209(2)/hdwiki/index.php?user-login

![O{L_II~SVZ5OK6_X3B{WHAU.png](https://image.3001.net/images/20180430/15250677701059.png!small)  

可以看到没有referer参数，我们手工添加referer并且带上payload；

    
    
    $this->db->query("UPDATE ".DB_TABLEPRE."session SET referer ='".string::haddslashes($_SERVER['HTTP_REFERER'])."' WHERE sid='".base::hgetcookie('sid')."'");    

由于带入数据库的时候是UPDATE语句并且使用WHERE语句所以我们不能使用and需要使用where接入payload并且使用注释符过滤后面程序原有的语句，最终payload为；

    
    
    referer:' where if((substr((select password from wiki_user where username='admin'),1,1))='e',sleep(3),0)#

但是刚开始测试的时候发现延迟不了，后来发现需要登陆进去，可以随便注册一个账号进去。

![\[506R`KI\[7QIL61DFP1H{6L.png
](https://image.3001.net/images/20180430/15250680621145.png!small)

可以看到成功延时注入，当管理员账号密码第一位为'e'的时候延时三秒返回。

##  **0x03POC**

用python完成poc把管理员账号的密码打出来；

![Clipboard
Image.png](https://image.3001.net/images/20180430/15250711818279.png!small)

测试结果如下；

![WS2QZCCCORQM}E\]E9_0QUVN.png](https://image.3001.net/images/20180430/15250684878175.png!small)

成功打出admin的密码信息了。  

***本文原创作者：davichi8282，本文属FreeBuf原创奖励计划，未经许可禁止转载**

