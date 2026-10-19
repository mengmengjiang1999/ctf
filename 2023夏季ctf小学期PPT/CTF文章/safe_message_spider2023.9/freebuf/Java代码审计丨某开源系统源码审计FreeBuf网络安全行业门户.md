***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ** ***本文作者：黑客小平哥，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**  
**

**java源代码审计相关资料一直比较少，今天抽空给大家写一篇简单的开源代码审计，这是个做公司网站的开源模板，由于项目比较小，本次就针对几个比较严重的漏洞讲解一下发现的过程，其它的一些小漏洞，包括XSS一类的就不写了，希望给大家学习帮助。**

编译别人的源代码是一项比较痛苦的过程，各种错误都是很蛋疼的，基础原理我就不讲了，大家都知道，还是不喜勿喷。

## Struts2系列漏洞：

导入项目后，浏览下项目的目录结构，发现一个比较老的Struts2版本，不用说了就是一堆Struts系统漏洞，工具来一波：

![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319816853616.jpg!small)![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319817323222.jpg!small)

上传个webshell，发现乱码，算了这不是重点。

![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319817459376.jpg!small)![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319817453395.jpg!small)

## 文件上传：

当浏览action文件的时候，发现如下上传代码，其实是对文件进行复制，“uploadFileName”为文件名，格式为：时间戳+_+文件名，重点是没有对文件后缀进行校验。

![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319817776888.jpg!small)

想要找出上传的位置，继续找出使用该方法的位置，全局搜索一下，发现4处js使用了该方法，我们查看其中“add_ajax_upload.js”,发现的确使用了该方法。

![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319818679931.jpg!small)![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319819944508.jpg!small)

继续查找使用该js的页面，发现“productInfoManage.jsp”使用了该js

![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319820492519.jpg!small)

那么我们继续进入“productInfoManage.jsp”去看看，发现该页面的添加功能有该上传点：

![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319820967168.jpg!small)

![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319821762428.jpg!small)

我们抓包上传个jsp文件，发现上传成功，至此该上传漏洞确认：

![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319821461144.jpg!small)![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319821469131.jpg!small)

## SQL注入：

继续浏览action文件时，发现此处一个查询功能，入参为noticeInfo：

![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319826336180.jpg!small)

进入noticeService.queryNotice查看  

![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319826651965.jpg!small)

继续追溯到dao层，看到sql拼接，此处存在SQL注入：  

![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319826696493.jpg!small)

既然存在注入，那么我们查找入参在哪个页面，发现在noticeManage.jsp的查询功能使用了该方法：  

![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319826911382.jpg!small)

进入“noticeManage.jsp”页面查看  

![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319826957082.jpg!small)

对搜索查询功能抓包注入，发现存在SQL注入，到此注入验证存在：![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319827022477.jpg!small)![java代码审计系列-某开源系统源码审计](https://image.3001.net/images/20180719/15319827059429.jpg!small)

## 结语：

此次审计源代码项目较小，漏洞问题不多，希望借此给小白打开审计大门，若有部分遗漏和错误希望各位大佬指正，项目和文章仅供参考。

 ***本文作者：黑客小平哥，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

