***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文作者：q601333824，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 概述

 **帝国CMS简称Empire CMS，当前的最新版本为7.5，个人空间可以匿名留言和登录留言，由于权限控制不当，可以伪造任意用户登录留言，
**自己无聊挖着玩的东西，喜欢的可以自己复现玩玩。****

## 相关环境

    
    
    源码信息：EmpireCMS_7.5_SC_UTF8      
    漏洞类型：越权      
    下载地址：<http://www.phome.net/download/>      
    漏洞文件：/e/member/mspace/gbookfun.php

## 漏洞分析

1\.
查看代码文件,插入留言的时候,从getcvar('mluserid')获取uid,然后当$uid存在时候再从getcvar('mlusername')获取用户名,最后再进行插入留言,如果uid不存在的话,就设置uid=0,就是匿名留言了。

![](https://image.3001.net/images/20190226/1551156896_5c74c6a0c3137.png!small)

![](https://image.3001.net/images/20190226/1551151870_5c74b2fecb12d.png!small)

2\. 最后再查看getcvar函数的定义,参数的来源是从$_COOKIE里面取出来了,前缀+$_COOKIE的值。

![3.png](https://image.3001.net/images/20190226/1551152102_5c74b3e677e1d.png!small)

3\. 看到这里有的人就可以想到利用方法了,这个时候只要构造mluserid和mlusername参数就可以伪造任意用户登录留言了。

## 利用方法

1\. 先获取$_COOKIE参数需要的前缀,打开浏览器就可以知道$_COOKIE的前缀是啥玩意了,我本地的$_COOKIE的前缀是ugbve。

![4.png](https://image.3001.net/images/20190226/1551152488_5c74b56814bc3.png!small)

2\.
然后在控制台运行document.cookie='ugbvemluserid=1;path=/'和document.cookie='ugbvemlusername=admin;path=/',指定COOKIE为根目录,因为留言页面和提交接口不在同一个目录,如果不设置根目录,接口获取不到COOKIE的(不用这个方法也可以自己抓包修改COOKIE就行,我懒得打开burpsuite,所以直接在控制台运行了)。

![](https://image.3001.net/images/20190226/1551157306_5c74c83aeae3e.png!small)  

![](https://image.3001.net/images/20190226/1551155715_5c74c203299ca.png!small)

6\. 这个时候在别人空间留言,都会以登录状态的admin,进行留言了,测试效果,刚才的留言是以admin的身份进行的留言,并且可以点击查看对方的空间。

![9.png](https://image.3001.net/images/20190226/1551155940_5c74c2e4cc128.png!small)

## 最后总结

1\. 其实就是判断是不是匿名留言的时候,没有判断用户是否是真的登录状态而进行留言。

2\. 漏洞挖挖总还是有的。

## 修复建议

1\. 从_COOKIE取出用户uid的时候,这个位置少了判断用户是否在登录状态下留言,想修复的同志,可以在这个位置加上登录判断。

![10.png](https://image.3001.net/images/20190226/1551156202_5c74c3eabfbcb.png!small)

 ***本文作者：q601333824，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

