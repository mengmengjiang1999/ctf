**作者：知道创宇404实验室**  
**英文版本：<https://paper.seebug.org/1089/>**

#### 1\. 背景概述

ActiveMQ 是 Apache 软件基金会下的一个开源消息驱动中间件软件。Jetty 是一个开源的 servlet 容器，它为基于 Java 的 web
容器，例如 JSP 和 servlet 提供运行环境。ActiveMQ 5.0 及以后版本默认集成了jetty。在启动后提供一个监控 ActiveMQ 的
Web 应用。

2016年4月14日，国外安全研究人员 Simon Zuckerbraun 曝光 Apache ActiveMQ Fileserver
存在多个安全漏洞，可使远程攻击者用恶意代码替代Web应用，在受影响系统上执行远程代码（CVE-2016-3088）。

#### 2\. 原理分析

ActiveMQ 中的 FileServer 服务允许用户通过 HTTP PUT 方法上传文件到指定目录,下载 [ActiveMQ 5.7.0
源码](http://archive.apache.org/dist/activemq/apache-activemq/5.7.0/activemq-parent-5.7.0-source-release.zip) ，可以看到后台处理 PUT 的关键代码如下

![](https://images.seebug.org/content/images/2017/07/--1-2.png-w331s)

用户可以上传文件到指定目录，该路径在 `conf/jetty.xml` 中定义，如下

![](https://images.seebug.org/content/images/2017/07/--2-2.png-w331s)

有趣的是，我们伪造一个特殊的上传路径，可以爆出绝对路径

![](https://images.seebug.org/content/images/2017/07/--3-2.png-w331s)

顺着 PUT 方法追踪，可以看到调用了如下函数

![](https://images.seebug.org/content/images/2017/07/--4-2.png-w331s)

同时看到后台处理 MOVE 的关键代码如下，可以看到该方法没有对目的路径做任何限制或者过滤。

![](https://images.seebug.org/content/images/2017/07/--5-2.png-w331s)

由此，我们可以构造PUT请求上传 webshell 到 fileserver 目录，然后通过 Move 方法将其移动到有执行权限的 admin/ 目录。

#### 3\. 漏洞利用的多种姿势

根据以上漏洞原理，我们可以想到多种利用姿势。

（注：以下结果均在 ActiveMQ 5.7.0 中复现，复现过程中出现了 MOVE 方法利用很不稳定的情况。）

  * 上传Webshell方式

首先 PUT 一个 Jsp 的 Webshell 到 fileserver 目录

![](https://images.seebug.org/content/images/2017/07/--6-2.png-w331s)

在 fileserver/ 目录中 Webshell 并没有执行权限

![](https://images.seebug.org/content/images/2017/07/--7-2.png-w331s)

爆一下绝对路径

![](https://images.seebug.org/content/images/2017/07/--8-2.png-w331s)

然后利用 MOVE 方法将 Webshell 移入 admin/ 目录（也可以利用相对路径）

![](https://images.seebug.org/content/images/2017/07/--9-2.png-w331s)

访问http://localhost:8161/admin/1.jsp?cmd=ls ，命令成功执行，效果如下

![](https://images.seebug.org/content/images/2017/07/--10-2.png-w331s)

  

  * 上传SSH公钥方式

既然可以任意文件上传和移动，很自然的可以想到上传我们的 ssh 公钥，从而实现 SSH 方式登录。

首先生成密钥对。（如果已存在则不需要）

![](https://images.seebug.org/content/images/2017/07/--11-2.png-w331s)

然后上传、移动到`/root/.ssh/`并重命名为`authorized_keys`

![](https://images.seebug.org/content/images/2017/07/--12-2.png-w331s)
![](https://images.seebug.org/content/images/2017/07/--13-2.png-w331s)

之后直接ssh登录即可。

![](https://images.seebug.org/content/images/2017/07/--14-2.png-w331s)

#### 4\. 漏洞影响

漏洞影响版本：Apache ActiveMQ 5.x ~ 5.14.0

在 [ZoomEye](https://www.zoomeye.org) 上用 日期 和 ActiveMQ
作为关键词检索，分别探测了2015年1月1日（漏洞爆发前一年）和2017年1月1日（漏洞爆发后一年）互联网上 ActiveMQ 的总量情况，如下。

![](https://images.seebug.org/content/images/2017/07/--15-2.png-w331s)
![](https://images.seebug.org/content/images/2017/07/--16-1.png-w331s)

可以看到，ActiveMQ的数量在漏洞爆发前后有很大幅度的减少，从这我们大致可以猜测漏洞爆发后很多ActiveMQ的Web服务限制了来自公网的访问。

#### 5\. 漏洞防护方案

1、ActiveMQ Fileserver 的功能在 5.14.0 及其以后的版本中已被移除。建议用户升级至 5.14.0 及其以后版本。

2、通过移除 `conf\jetty.xml` 的以下配置来禁用 ActiveMQ Fileserver 功能

![](https://images.seebug.org/content/images/2017/07/--17-1.png-w331s)

#### 6\. 参考链接

[1] <http://activemq.apache.org/security-advisories.data/CVE-2016-3088-announcement.txt>  
[2] <https://www.seebug.org/vuldb/ssvid-96268>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/346/>

