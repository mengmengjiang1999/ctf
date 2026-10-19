# Joomla 3.2 到 3.4.4 注入漏洞允许管理员权限访问站点

阅读量 **108819**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-10-23 16:49:20

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

原文地址：<https://www.trustwave.com/Resources/SpiderLabs-Blog/Joomla-SQL-Injection-Vulnerability-Exploit-Results-in-Full-Administrative-Access/>

译文仅供参考，具体内容表达以及含义原文为准。

**受影响版本:3.2 到 3.4.4**

**补救措施:**

如果你正在使用低版本的joomla,请立即去官方更新到最新版<https://github.com/joomla/joomla-cms/releases/download/3.4.5/Joomla_3.4.5-Stable-Full_Package.zip>

**  
**

**概述:**

漏洞出在核心模块,因此不需要任何扩展,所有使用joomla 3.2以上版本的站点,都受此漏洞影响

/administrator /components
/com_contenthistory/models/history.php,漏洞出在getListQuery()函数,代码如下

当请求

能够通过注入从数据库里返回session ID

如果得到的是管理员的session ID ,则可以通过修改当前浏览器的cookies里的session ID ,然后访问/administrator/

就可以登陆后台了。

**更多技术细节:**

<https://www.trustwave.com/Resources/SpiderLabs-Blog/Joomla-SQL-Injection-Vulnerability-Exploit-Results-in-Full-Administrative-Access/>

本文翻译自360安全播报 [原文链接](https://www.trustwave.com/Resources/SpiderLabs-Blog/Joomla-SQL-Injection-Vulnerability-Exploit-Results-in-Full-Administrative-Access/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/82778](/post/id/82778)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报](https://www.trustwave.com/Resources/SpiderLabs-Blog/Joomla-SQL-Injection-Vulnerability-Exploit-Results-in-Full-Administrative-Access/)

如若转载,请注明出处： <https://www.trustwave.com/Resources/SpiderLabs-Blog/Joomla-SQL-Injection-Vulnerability-Exploit-Results-in-Full-Administrative-Access/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

