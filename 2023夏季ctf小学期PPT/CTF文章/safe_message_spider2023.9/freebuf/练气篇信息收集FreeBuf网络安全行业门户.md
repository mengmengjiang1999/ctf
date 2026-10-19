  

## 渗透测试流程:

### 渗透测试与入侵的最大区别

渗透测试：出于保护系统的目的，更全面地找出测试对象的安全隐患。

入侵：不择手段地（甚至是具有破坏性的）拿到系统权限。

## 目标对象分析：

  * 单个目标服务器（非web）

  * Web服务器

  * 整个网络拓扑

  * 内网：

  * 网络设备：交换机、路由器、防火墙、ids、等

  * 网络中的服务器：文件服务器、dns、http、域控制器等

  * 外网：

  * 相关联的其他服务器（ip关联、服务关联）

  * 旁站、c段、邮件服务器、dns服务器、代理服务器等  
![图片1.png](https://image.3001.net/images/20220505/1651740565_62738f95842a7f3c01a5e.png!small)

## web方向信息收集：

  * 域名信息

  * 敏感目录

  * 旁站C段

  * 整站分析

  * 谷歌hacker

  * url采集

  * 信息分析  
![图片1.png](https://image.3001.net/images/20220505/1651740367_62738ecfb822ee90c5a45.png!small)  
![图片4.png](https://image.3001.net/images/20220505/1651740383_62738edfe2473ad263eb3.png!small)

## 整个网站站分析：

  * 服务器类型

  * 服务器平台、版本等

  * 网站容器

  * 搭建网站的服务组件，例如：iis、Apache、nginx、tomcat等

  * 脚本类型

  * ASP、PHP、JSP、aspx等

  * 数据库类型

  * access、sqlserver、mysql、oracle、postgresql等

  * CMS类型

  * WAF

![1651739519_62738b7f6e1c24bd27f55.png!small?1651739518528](https://image.3001.net/images/20220505/1651739519_62738b7f6e1c24bd27f55.png!small?1651739518528)

## 谷歌黑客:

  * 1\. Intext:

  * 查找网页中含有xx关键字的网站 例：Intext：管理员登录

  * 2\. Intitle：

  * 查找某个标题 例：intitle：后台登录

  * 3\. Filetype：

  * 查找某个文件类型的文件 例：数据挖掘 filetype：doc

  * 4\. Inurl:

  * 查找url中带有某字段的网站 例：inurl：php?id=

  * 5\. Site：

  * 在某域名中查找信息  
![图片2.png](https://image.3001.net/images/20220505/1651740433_62738f11135022c18e0f4.png!small)  
![图片3.png](https://image.3001.net/images/20220505/1651740444_62738f1cb0b895972ceee.png!small)

###

## 采集相关url的同类网站：

  1. 例如：php?id=

  2. 漏洞网站

  3. 相同某种指纹网站

  4. 常用工具

  5. 谷歌hacker

  6. url采集器!  
![图片7.png](https://image.3001.net/images/20220505/1651740404_62738ef4a27096f0ef720.png!small)  
![图片6.png](https://image.3001.net/images/20220505/1651740416_62738f0090f67df43c28a.png!small)

###

## 渗透测试一般流程:

1\. 项目前期准备工作  
2\. 信息收集：whois、网站源IP、旁站、C段网站、服务器系统版本、容器版本、程序版本、  
数据库类型、二级域名、防火墙、维护者信息  
3\. 漏洞扫描：Nessus, AWVS  
4\. 手动挖掘：逻辑漏洞  
5\. 验证漏洞  
6\. 修复建议  
7\. （如果有）基线检查/复验漏洞  
8\. 输出报告

  1. ![1651741510_627393464cf06cf85be87.png!small?1651741509979](https://image.3001.net/images/20220505/1651741510_627393464cf06cf85be87.png!small?1651741509979)

## 如何绕过CDN查真实IP:

1.多地ping看是否有cdn  
2.邮件订阅或者rss订阅  
3.二级域名可能不会做cdn  
4.nslookup http://xxx.com 国外dns  
5.查找域名历史解析记录，因为域名在上CDN之前用的IP，很有可能就是CDN的真实源IP地址  
6.phpinfo上显示的信息  
7.cloudflare github可以获取真实IP  
8.一个网站有icon 可以根据icon hash 来查找真实IP  
9.子域名绑定 测试子域可能回源

![1651741648_627393d06d2a46e3debb3.png!small?1651741647897](https://image.3001.net/images/20220505/1651741648_627393d06d2a46e3debb3.png!small?1651741647897)

  

