***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**我在FreeBuf上每天都可以学到很多新思路新技术，感谢这个平台，为了回馈FreeBuf的小伙伴们，写下这篇文章，希望在可以为奋斗在网络安全路上的小伙伴们提供一些新奇小思路，其实挖洞并不难，也希望大家能把分享的精神发扬光大。**

## 概述

天睿PHP内容管理框架（简称TPCMF）基于PHPCMF框架采用PHP7技术+CodeIgniter4作为系统核心部件，由系统框架+应用插件快速组建Web应用。

## 相关环境  

> 源码信息：TPCMF框架-安装包-201905171230.zip
>
> 漏洞类型：储存型XSS
>
> 下载地址：<http://www.tpcmf.com/down/>  
>
>
> 漏洞文件：/dayrui/Fcms/Library/Form.php

## 漏洞分析  

1.首先我们来看看这次漏洞的配角
/dayrui/Core/Controllers/Member/Register.php文件，这里把注册用户的函数写出这个样子（代码敲的是真漂亮。反正我是敲不出这么漂亮的代码）。

![对于TPCMF框架的一次代码审计](https://image.3001.net/images/20190518/1558110598_5cdee186b8e6d.png!small)2.这里呢，我们发现第75行对用户名的检查的时候调用了check_username（）这个函数（打了个哈欠点了跟烟），嗯，好的，我们来跟进一下check_username（）这个函数看看这个函数都干了什么，这个函数的位置在
/dayrui/Fcms/Library/Form.php， 这个文件是我们这次漏洞的的主角。

![对于TPCMF框架的一次代码审计](https://image.3001.net/images/20190518/1558110813_5cdee25dcdb6c.png!small)3.跟进函数之后我们发现check_username（）似乎并没有对$value的值进行检查（淫笑中~~），那么这次我们的漏洞成因就十分明确了，由于check_username函数只对用户名是否注册过进行了检查，并没有对其中的内容进行检查，所以我们可以通过注册账户，在账户名中插入xss的payload对其进行攻击，对于没有开启httponly的站直接钓走cookie。（对于开启httponly的站我们怎么办呢，我会在下一篇文章中讲述一下如何对开启httponly的站点进行钓鱼攻击）。

## 漏洞复现  

1\. （打个哈欠灭了烟继续写文章）
好了，现在我们进入本地搭建好的环境的主页的注册页面。![对于TPCMF框架的一次代码审计](https://image.3001.net/images/20190518/1558111213_5cdee3edae6c4.png!small)

2\. 填入注册信息，其中用户名为我们的xss攻击测试代码
`</tExtArEa>'"><sCRiPt>alert(“xss”)</sCrIpT>`![对于TPCMF框架的一次代码审计](https://image.3001.net/images/20190518/1558111301_5cdee445208fc.png!small)

3\. 单机确认，储存XSS用户权限漏洞复现（再一次淫笑~~~）。

![对于TPCMF框架的一次代码审计](https://image.3001.net/images/20190518/1558111417_5cdee4b9a7a18.png!small)4\.
好了，现在进入我们的后台。

![对于TPCMF框架的一次代码审计](https://image.3001.net/images/20190518/1558111469_5cdee4ed3975b.jpg!small)5\.
登陆后台，我们来选择一下我们可爱的用户列表选项。

![对于TPCMF框架的一次代码审计](https://image.3001.net/images/20190518/1558111535_5cdee52fbbdef.png!small)6\.
储存XSS管理员权限复现（又一次淫笑~~~）。

##
![对于TPCMF框架的一次代码审计](https://image.3001.net/images/20190518/1558111592_5cdee56892e7b.png!small)

## 结语  

很多刚刚入坑的萌新们认为代码审计似乎很难，想挖到漏洞似乎只有大佬们才能实现，但是其实我想说挖到属于自己的漏洞其实并不难，需要的是你能够平静下急功近利的心，耐得住漏洞挖掘中的乏味，不断去磨练自己的意志，增长自己的经验，相信自己，你是醉棒的，你也可以成为别人眼中的大佬！

 ***本文作者：chenchuan，转载请注明来自FreeBuf.COM**

