华云安一直持续跟进和研究前沿漏洞、复现和编写漏洞检测脚本（PoC），并赋能给自身产品。

根据近期漏洞爆发与华云安安全实验室研究情况，本周输出以下重要PoC漏洞检测脚本。涉及Druid数据库、Tenda路由器、nacos服务平台、Jetty容器等。其风险等级、危害程度等多为高危。

华云安以下产品具有同步支持以下漏洞的检测和验证或者利用的能力：

灵洞威胁与漏洞管理平台Ai.Vul

灵鉴弱点识别与检测系统Ai.Scan

灵刃智能化渗透攻防系统Ai.Bot

蚂蚁PoC漏洞扫描工具

猎鹰Exp漏洞利用工具

##  **漏洞目录**

1、Alibaba nacos 认证绕过漏洞

2、Microsoft Azure 代码执行漏洞

3、Mkdocs 路径遍历漏洞

4、Eclipse Jetty信息泄露漏洞

5、Eclipse Jetty信息泄露漏洞

6、OFBiz反序列化代码执行漏洞

7、Tenda AC11代码执行漏洞

8、SaltStack Salt 远程命令执行漏洞

9、Apache Druid 远程命令执行漏洞

##  **01 CVE-2021-29442**

 **//基本信息**

编号：CVE-2021-29442

名称：Alibaba nacos 认证绕过漏洞

等级：HIGH

CVSS：7.5

发布时间：2021-04-27

 **// 漏洞描述及危害**

nacos是中国阿里巴巴（Alibaba）的一个动态服务发现、配置和服务管理平台。该软件支持基于 DNS 和基于 RPC
的服务发现，可提供提供实时健康检查，阻止服务向不健康的主机或服务实例发送请求等功能。Nacos
存在访问控制错误漏洞，该漏洞源于ConfigOpsController允许用户执行管理操作，比如查询数据库，甚至清除数据库。

 **//影响范围**

Alibaba Nacos <1.4.1

 **//解决方案**

当前官方已发布受影响版本的对应补丁，建议受影响的用户及时更新官方的安全补丁及时更新官方的安全补丁。

补丁链接：

[https://github.com/advisories/GHSA-36hp-jr8h-556f](https://link.zhihu.com/?target=https%3A//github.com/advisories/GHSA-36hp-jr8h-556f)

##  **02 CVE-2021-38647**

 **// 基本信息**

编号：CVE-2021-38647

名称：Microsoft Azure 代码执行漏洞

等级：CRITICAL

CVSS：9.8

发布时间：2021-09-14

 **//漏洞描述及危害**

Microsoft Azure是美国微软（Microsoft）公司的一套开放的企业级云计算平台。microsoft Azure Open
Management Infrastructure存在代码注入漏洞，远程攻击者可利用该漏洞执行代码。

 **//影响范围**

Azure Open Management Infrastructure ＜omi-1.6.8-1

 **//解决方案**

当前官方已发布受影响版本的对应补丁，建议受影响的用户及时更新官方的安全补丁及时更新官方的安全补丁。

补丁链接：

[https://about.gitlab.com/releases/2021/04/14/security-release-gitlab-13-10-3-released/](https://link.zhihu.com/?target=https%3A//about.gitlab.com/releases/2021/04/14/security-release-gitlab-13-10-3-released/)

##  **03 CVE-2021-40978**

 **//基本信息**

编号：CVE-2021-40978

名称：Mkdocs 路径遍历漏洞

等级：HIGH

CVSS：7.5

发布时间：2021-10-07

 **// 漏洞描述及危害**

Mkdocs是一个快速、简单和彻头彻尾的华丽静态站点生成器。用于构建项目文档。mkdocs 1.2.2 存在安全漏洞，该漏洞允许远程利用以获取敏感信息。

 **//影响范围**

mkdocs 1.2.2

 **//解决方案**

目前厂商暂未发布升级补丁以修复漏洞，建议用户随时关注官方动态：[https://github.com/mkdocs/mkdocs](https://link.zhihu.com/?target=https%3A//github.com/mkdocs/mkdocs)

##  **04 CVE-2021-28164**

 **//基本信息**

编号：CVE-2021-28164

名称：Eclipse Jetty信息泄露漏洞

等级：MEDIUM

CVSS：5.3

发布时间：2021-04-01

 **//漏洞描述及危害**

Eclipse Jetty是Eclipse基金会的一个开源的、基于Java的Web服务器和Java Servlet容器。Eclipse Jetty
9.4.37.v20210219 to 9.4.38.v20210224 存在信息泄露漏洞，该漏洞允许请求的uri包含\\\%2e or
\\\%2e\\\%2e访问WEB-INF目录中受保护资源。

 **//影响范围**

Eclipse Jetty 9.4.37.v20210219 to 9.4.38.v20210224

 **//解决方案**

当前官方已发布受影响版本的对应补丁，建议受影响的用户及时更新官方的安全补丁及时更新官方的安全补丁。

补丁链接：

[https://github.com/eclipse/jetty.project/security/advisories/GHSA-26vr-8j45-3r4w](https://link.zhihu.com/?target=https%3A//github.com/eclipse/jetty.project/security/advisories/GHSA-26vr-8j45-3r4w)

##  **05 CVE-2021-28169**

 **//基本信息**

编号：CVE-2021-28169

名称：Eclipse Jetty 信息泄露漏洞

等级：MEDIUM

CVSS：5.3

发布时间：2021-06-09

 **// 漏洞描述及危害**

Eclipse Jetty是Eclipse基金会的一个开源的、基于Java的Web服务器和Java Servlet容器。Eclipse Jetty
中存在信息泄露漏洞，该漏洞源于通过对ConcatServlet的双重编码路径请求访问WEB-INF目录中的受保护资源。以下产品及型号受到影响：Eclipse
Jetty 9.4.40 版本及之前版本、Eclipse Jetty 10.0.2 版本及之前版本、Eclipse Jetty 11.0.2
版本及之前版本。

 **//影响范围**

Eclipse Jetty 9.4.40 版本及之前版本

Eclipse Jetty 10.0.2 版本及之前版本

Eclipse Jetty 11.0.2 版本及之前版本

 **//解决方案**

目前厂商已经发布修复措施解决此安全问题，建议受影响的用户及时更新官方的安全补丁及时更新官方的安全补丁。

补丁链接：

[https://github.com/eclipse/jetty.project/security/advisories/GHSA-gwcr-j4wh-j3cq](https://link.zhihu.com/?target=https%3A//github.com/eclipse/jetty.project/security/advisories/GHSA-gwcr-j4wh-j3cq)

##  **06 CVE-2021-30128**

 **//基本信息**

编号：CVE-2021-30128

名称：OFBiz反序列化代码执行漏洞

等级：HIGH

CVSS：8.8

发布时间：2021-04-27

 **//漏洞描述及危害**

Apache
OFBiz是美国阿帕奇（Apache）基金会的一套企业资源计划（ERP）系统。该系统提供了一整套基于Java的Web应用程序组件和工具。Apache
OFBiz 17.12.07之前版本存在代码问题漏洞，该漏洞源于不安全的反序列化。攻击者可利用该漏洞进行任意命令执行。

 **//影响范围**

Apache OFBiz <17.12.07

 **//解决方案**

当前官方已发布受影响版本的对应补丁，建议受影响的用户及时更新官方的安全补丁及时更新官方的安全补丁。

补丁链接：

[https://lists.apache.org/thread.html/rb3f5cd65f3ddce9b9eb4d6ea6e2919933f0f89b15953769d11003743%40%3Cdev.ofbiz.apache.org%3E](https://link.zhihu.com/?target=https%3A//lists.apache.org/thread.html/rb3f5cd65f3ddce9b9eb4d6ea6e2919933f0f89b15953769d11003743%2540%253Cdev.ofbiz.apache.org%253E)

##  **07 CVE-2021-31755**

 **//基本信息**

编号：CVE-2021-31755

名称：Tenda AC11代码执行漏洞

等级：CRITICAL

CVSS：9.8

发布时间：2021-05-11

 **//漏洞描述及危害**

Tenda AC11是中国腾达（Tenda）公司的一款路由器。

Tenda AC11 devices with firmware
02.03.01.104_CN版本及之前版本存在安全漏洞，该漏洞源于/goform/setmac，攻击者可利用该漏洞通过一个精心制作的post请求在系统上执行任意代码。

 **//影响范围**

Tenda AC11 devices with firmware 02.03.01.104_CN版本及之前版本

 **// 解决方案**

目前厂商暂未发布修复措施解决此安全问题，建议使用此软件的用户随时关注厂商主页或参考网址以获取解决办法：[https://www.tenda.com.cn/default.html](https://link.zhihu.com/?target=https%3A//www.tenda.com.cn/default.html)

##  **08 CVE-2021-25281**

 **//基本信息**

编号：CVE-2021-25281

名称：SaltStack Salt 远程命令执行漏洞

等级：CRITICAL

CVSS：9.8

发布时间：2021-02-27

 **//漏洞描述及危害**

Saltstack SaltStack
Salt是SaltStack（Saltstack）公司的一套开源的用于管理基础架构的工具。该工具提供配置管理、远程执行等功能。SaltStack Salt
before 3002.5 存在安全漏洞，该漏洞源于salt-api不支持eauth凭据。攻击者可利用该漏洞可以远程运行主机上的任何模块。

 **//影响范围**

SaltStack Salt before 3002.5

 **//解决方案**

当前官方已发布受影响版本的对应补丁，建议受影响的用户及时更新官方的安全补丁及时更新官方的安全补丁。

补丁链接：

[https://saltproject.io/security_announcements/active-saltstack-cve-release-2021-feb-25/](https://link.zhihu.com/?target=https%3A//saltproject.io/security_announcements/active-saltstack-cve-release-2021-feb-25/)

##  **09 CVE-2021-25646**

 **//基本信息**

编号：CVE-2021-25646

名称：Apache Druid 远程命令执行漏洞

等级：HIGH

CVSS：8.8

发布时间：2021-01-29

 **//漏洞描述及危害**

Apache Druid是美国阿帕奇软件（Apache）基金会的一款使用Java语言编写的、面向列的开源分布式数据库。Apache Druid
0.20.0和更早的版本存在访问控制错误漏洞，该漏洞允许经过身份验证的用户强制Druid运行用户提供的JavaScript代码，并执行服务器进程特权的代码。

 **//影响范围**

Apache Druid <0.20.0

 **//解决方案**

当前官方已发布受影响版本的对应补丁，建议受影响的用户及时更新官方的安全补丁及时更新官方的安全补丁。

补丁链接：

[https://lists.apache.org/thread.html/rfda8a3aa6ac06a80c5cbfdeae0fc85f88a5984e32ea05e6dda46f866%40%3Cdev.druid.apache.org%3E](https://link.zhihu.com/?target=https%3A//lists.apache.org/thread.html/rfda8a3aa6ac06a80c5cbfdeae0fc85f88a5984e32ea05e6dda46f866%2540%253Cdev.druid.apache.org%253E)

##  **产品截图**

![v2-7e1d0cd4fad36581bf320c6133f2a708_720w.jpg](https://image.3001.net/images/20211111/1636600659_618c8b536624548078dc5.jpg!small)![v2-2178ac18c88296811abee2343a9ae82a_720w.jpg](https://image.3001.net/images/20211111/1636600659_618c8b53bb0b85551fdcc.jpg!small)![v2-60340d40fbc5dd4ebe6eb6d1809bc6e3_720w.jpg](https://image.3001.net/images/20211111/1636600659_618c8b53f412672476268.jpg!small)

