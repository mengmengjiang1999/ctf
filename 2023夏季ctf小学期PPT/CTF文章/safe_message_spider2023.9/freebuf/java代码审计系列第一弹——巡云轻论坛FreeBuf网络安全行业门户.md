## 项目介绍

巡云轻论坛系统包含论坛、问答模块。采用JAVA+MYSQL架构，自适应手机端和电脑端，界面简洁，性能高效。本系统适合企业建设官方交流论坛,进行产品展示、营销、客服、用户交流的平台，用最小的成本将你的产品推向数以亿计的用户，成为他们生活中的热点话题。项目官网http://www.diyhi.com/cms.html

巡云轻论坛系统5.3版本后台存在多处漏洞，攻击者通过上传恶意文件可以控制网站服务器。

## 后台多处任意文件上传漏洞

登录管理员后台，找到话题列表，新建话题，插入图片

![image.png](https://image.3001.net/images/20211106/1636188988_6186433c64a42e390afe7.png!small)

抓包，根据url定位到对应的后台代码

![image.png](https://image.3001.net/images/20211106/1636189008_618643509630958e4b0bb.png!small)

通过搜索url关键字，发现代码在TopicManageAction.java中

![image.png](https://image.3001.net/images/20211106/1636189031_6186436743dcfa4110321.png!small)

下断点调试，发现该函数对文件后缀进行了限制并且重命名了上传的文件。但是有一段代码如下。当Content-Type是application/octet-stream时进入。

![image.png](https://image.3001.net/images/20211106/1636189043_61864373a2943739d9b9a.png!small)

getType获取了文件类型，但是这个函数是根据文件开头的几个字节判断文件类型的，因此可以绕过。  
![image.png](https://image.3001.net/images/20220119/1642583605_61e7d63545097c85933f6.png!small)  
直接修改Content-Type为 application/octet-stream，filename修改为1.jsp上传。

![image.png](https://image.3001.net/images/20211106/1636189074_618643928d1f761338a28.png!small)

访问上传的webshell，可以成功执行命令

![image.png](https://image.3001.net/images/20211106/1636189094_618643a60cb823d073575.png!small)

这部分代码存在多处，因此存在多个上传点

![image.png](https://image.3001.net/images/20211106/1636189106_618643b289aae61ce6cdd.png!small)

## unzip 解压漏洞任意文件上传

问题出在系统升级功能处

![image.png](https://image.3001.net/images/20211106/1636189209_6186441938902d13667f4.png!small)

上传一个特制的压缩文件

![image.png](https://image.3001.net/images/20211106/1636189270_618644561f7b1f93ab076.png!small)

问题出在升级功能

![image.png](https://image.3001.net/images/20211106/1636189229_6186442d1bb76c82dc1af.png!small)

由于这个接口在前台没看到，因此直接访问升级接口，触发解压缩代码

访问上传的木马

![image.png](https://image.3001.net/images/20211106/1636189306_6186447a96eb041c4e40c.png!small)

## 后台多处FreeMaker代码注入漏洞

后台管理模板处

![image.png](https://image.3001.net/images/20211106/1636189318_6186448664feded3b357d.png!small)

查看源码，发现采用了freemaker模板，尝试freemaker模板注入

![image.png](https://image.3001.net/images/20211106/1636189331_6186449346536ec323b86.png!small)

访问首页，成功执行命令

![image.png](https://image.3001.net/images/20211106/1636189343_6186449f298adbde9cf92.png!small)

后台所有修改模板的地方全部存在漏洞。

## 修复方案

目前厂商已经发布了升级补丁以修复此安全问题，补丁获取链接：

https://github.com/diyhi/bbs/releases/download/5.4/bbs-5.3to5.4.zip

