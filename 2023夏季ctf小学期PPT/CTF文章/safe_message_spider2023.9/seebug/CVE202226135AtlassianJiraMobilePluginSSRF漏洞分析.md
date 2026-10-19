**作者：xxhzz@星阑科技PortalLab  
原文链接：<https://mp.weixin.qq.com/s/VaHYzhkn2gZhHcCPTdO-Tg>**

## **漏洞描述**

6月29日，Atlassian官方发布安全公告，在Atlassian Jira
多款产品中存在服务端请求伪造漏洞(SSRF)，经过身份验证的远程攻击者可通过向Jira Core REST
API发送特制请求，从而伪造服务端发起请求，从而导致敏感信息泄露，同时为下一步攻击利用提供条件。需注意的是，若服务端开启注册功能，则未授权用户可通过注册获取权限进而利用。

## **利用范围**

Jira Core Server, Jira Software Server, and Jira Software Data Center:

  * Versions after 8.0 and before 8.13.22
  * 8.14.x
  * 8.15.x
  * 8.16.x
  * 8.17.x
  * 8.18.x
  * 8.19.x
  * 8.20.x before 8.20.10
  * 8.21.x
  * 8.22.x before 8.22.4

Jira Service Management Server and Data Center:

  * Versions after 4.0 and before 4.13.22
  * 4.14.x
  * 4.15.x
  * 4.16.x
  * 4.17.x
  * 4.18.x
  * 4.19.x
  * 4.20.x before 4.20.10
  * 4.21.x
  * 4.22.x before 4.22.4

## **漏洞分析**

### **环境搭建**

使用docker搭建，在docker仓库（<https://hub.docker.com/r/weareogury/atlassian-jira-software/tags>）中可找到漏洞版本的Jira Software Server镜像。

![](https://images.seebug.org/content/images/2022/10/d7963695-63f3-449c-9a16-3e96c39288e7.png-w331s)

![](https://images.seebug.org/content/images/2022/10/5b656595-8e48-44c3-aff8-d3d3d67d58d0.png-w331s)

按步骤进行配置即可。

![](https://images.seebug.org/content/images/2022/10/96803b1b-ceb7-4790-a4d8-a2a4750fe829.png-w331s)

环境搭建成功

![](https://images.seebug.org/content/images/2022/10/8b87ab48-81f5-4b38-95a5-ffe6bd513526.png-w331s)

### **代码分析**

分析Jira Mobile
插件，在com.atlassian.jira.plugin.mobile.rest.v1_0.BatchResource中存在barch
API接口，阅读代码，该API应该是用于接收多个请求并在服务端执行。

![](https://images.seebug.org/content/images/2022/10/3c361e0e-6589-4b1c-a7e5-4321732be6da.png-w331s)

分析下方的executeBatch函数。

![](https://images.seebug.org/content/images/2022/10/19108c7f-a6b3-40f2-b213-864bca623bb2.png-w331s)

在如图所示代码，实际负责发送HTTP请求。其中batchService接口的实现类BatchServiceImpl位于com.atlassian.jira.plugin.mobile.service.impl.BatchServiceImpl.class

分析batch函数。

![](https://images.seebug.org/content/images/2022/10/6580b6e3-645a-4426-9e4d-e10cf76b8152.png-w331s)

根据如上代码，定位execute函数。

![](https://images.seebug.org/content/images/2022/10/62669c7a-0d66-4dec-8951-1d9e1314edb7.png-w331s)

其中relativeLocation来自于requestBean.getLocation中的location。

![](https://images.seebug.org/content/images/2022/10/5d049613-7b3d-433e-8451-93b8473bb633.png-w331s)

后续传入toJiraLocation函数

![](https://images.seebug.org/content/images/2022/10/709024e5-e980-417c-98e8-ad2f84b9a4a1.png-w331s)

![](https://images.seebug.org/content/images/2022/10/9395ef51-4e8e-4bb0-8946-e02b67bece08.png-w331s)

继续跟进，位于com.atlassian.jira.plugin.mobile.util.LinkBuilder.class

![](https://images.seebug.org/content/images/2022/10/6517e613-9306-41df-9fb6-0589159ecbbb.png-w331s)

URL通过简单的拼接构造，而其中的path来自于location，完全可控。

继续回到execute函数。

![](https://images.seebug.org/content/images/2022/10/2027d1ff-2ad1-4984-98d8-94379dabf9e8.png-w331s)

location会从json对象中获取，在获取到URL对象后，再调用httpClientProvider发送Http请求。

因为URL的后半部分是可控的，如果我们简单指定location为@xx.com，那么最终的URL为<https://jira-host.com@xx.com>，httpClientProvider实际上会对xx.com发送http请求，所以导致了SSRF漏洞产生。

## **漏洞复现**

使用burpsuite自带的dnslog功能进行探测，成功发送请求。

![](https://images.seebug.org/content/images/2022/10/39c126ce-2276-4e3c-b424-e30e101469f3.png-w331s)

## **修复建议**

**1\. 将受影响的产品升级到最新安全版本:**

Jira Core Server、Jira Software Server 和 Jira Software Data Center 可升级至：

  * 8.13.22
  * 8.20.10
  * 8.22.4 
  * 9.0.0

Jira Service Management Server 和 Data Center 可升级至：

  * 4.13.22
  * 4.20.10
  * 4.22.4 
  * 5.0.0

**2\. 缓解措施**

(1) 关闭用户注册功能。

(2) 禁用Mobile Plugin，具体步骤如下：

a、在应用程序的顶部导航栏中，选择设置 -> 管理加载项或管理应用程序。

b、找到Mobile Plugin for Jira Data Center and Server应用程序，然后选择禁用即可。

(3) 升级Mobile Plugin至最新版本。

## **参考材料**

<https://confluence.atlassian.com/jira/jira-server-security-advisory-29nd-june-2022-1142430667.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1998/>

