# Apache Shiro权限绕过漏洞CVE-2020-11989分析

阅读量 **306799**

发布时间 : 2020-11-13 11:00:02

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01e57ddfa6712a0795.png)

## 简介

Apache Shiro作为Java框架，可被用于身份认证、授权等任务。

整合Apache Shiro至Spring Boot中时，请求可能会导致越权绕过身份验证现象的出现，存在两种较好的利用现象，称为利用方法1和利用方法2。

存在安全缺陷的版本：Apache Shiro 1.5.3以前的版本。JDK:1.8.0_181。

认为应清晰Spring Boot、Apache Shiro框架源码的逻辑功能。

清晰常见的反过滤、非常规字符的特点。

## 利用方法1

### 环境

设置Tomcat根目录为“/test/”【仅Apache Shiro
1.5.2有此严格限制】，端口为8088；设置“./admin/*”路径需要认证访问，成功则显示“hello, admin
page”，具体配置见源代码【https://github.com/HYWZ36/HYWZ36-CVE-2020-11989-code/tree/main/springboot-shiro-master0】。

### 目标

绕过认证访问“./admin/*”路径。

### 分析方法

对于输入的恶意URL http://localhost:8088/;/test/admin/page
，首先采用Shiro进行权限验证处理。Shiro框架的decodeAndCleanUriString方法会根据“；”截取URI“/;/test//admin/page”的前部分内容，从而使得此请求通过权限验证。依次经过的重要类、方法如下：

![](https://p2.ssl.qhimg.com/t01d569eb124f75c641.png)

随后，在Spring框架中解析URL。关键点是在解码过程中，仅剔除URI中“;”而保全其他所有内容，从而解析得目标路径“/admin/page”。依次经过的重要类、方法如下：

![](https://p1.ssl.qhimg.com/t017b5fd240349aae0b.png)

## 利用方法2

### 环境

设置Tomcat根目录为“/test/”【仅Apache Shiro
1.5.2有此严格限制】，端口为8081；设置“./admin/*”路径需要认证访问，成功则显示“hello,admin”，具体配置见源代码【https://github.com/HYWZ36/HYWZ36-CVE-2020-11989-code/tree/main/springboot-shiro-master】。

### 目标

绕过认证访问“./admin/{name}”路径。

### 分析方法

对于输入的恶意URL http://localhost:8081/test/admin/a%25%32%66a
首先采用Shiro进行权限验证处理。Shiro框架的decodeRequestString方法会进行两次解码得到URI
/admin/a/a，并因其分割后的数组长度大于模板“/admin/*”而使得此请求通过权限验证。依次经过的重要类、方法如下：

![](https://p4.ssl.qhimg.com/t012394d2f1472fd463.png)

随后，在Spring框架中解析URL。关键点是在解码过程中，仅解码得路径是“/test/admin/a%252f”，因此符合“/admin/{name}”规则得以正常访问。依次经过的重要类、方法如下：

![](https://p5.ssl.qhimg.com/t01f4831ad66948fb71.png)

## 补丁分析

如下图，修改了org.apache.shiro.web.util.WebUtils#getPathWithinApplication，采用两个标准方法获取URI有效应对了“/;/…”安全缺陷，且无解码操作从而有效应对了“a%25%32%66a”安全缺陷。

![](https://p2.ssl.qhimg.com/t013aeef6fbec622664.png)

## docker复现

加载容器tar为镜像的例子：

cat ./ubuntu-xxx.tar | docker import – ubuntu-new

设置局域网及容器ip、启动容器的例子：

（1）自定义网络

docker network create —subnet=192.168.10.1/24 testnet

（2）启动docker容器

docker run -p 8088:8088 -p 8081:8081 -it —name testt3 —hostname testt3
—network testnet —ip

10.10.10.100 ubuntuxxx:xxx /bin/bash

镜像名称为ubuntu_cve-2020-11989:v1，需开启8088和8081的端口映射功能。

启动进入容器后，复现利用方法1。切换到目录【/springboot-shiro-master0/target】下，执行命令【java -jar
srpingboot-shiro-0.0.1-SNAPSHOT.jar】。随后在宿主机浏览器输入

【http://localhost:8088/;/test/admin/page】， 成功访问表明复现成功，如下图。

![](https://p2.ssl.qhimg.com/t018cea09f14c06043f.png)

复现利用方法2。中断当前程序，切换到目录【/springboot-shiro-master1/target】下，执行命令【java -jar
srpingboot-shiro-0.0.1-SNAPSHOT.jar】。随后在宿主机浏览器输入

【http://localhost:8081/test/admin/a%25%32%66a】， 成功访问表明复现成功，如下图。

![](https://p4.ssl.qhimg.com/t018e5c5fed18d12cf2.png)

## 参考资料

https://www.freebuf.com/vuls/249380.html

https://xlab.tencent.com/cn/2020/06/30/xlab-20-002/

idea 快速创建spring boot项目 以及打包 – 知乎

https://zhuanlan.zhihu.com/p/149736921

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信代码卫士** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/222489](/post/id/222489)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Apache Shiro](/tag/Apache Shiro)

 **+1** __2赞

 __收藏

![](https://p4.ssl.qhimg.com/t015a32ce3696fa7636.png) 奇安信代码卫士

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

