Atlassian已针对其Jira数据中心和Jira服务管理数据中心产品多个版本中的一个严重漏洞发布了补丁，该漏洞可能导致任意代码执行。

Atlassian是一个被 180,000名客户用来设计软件和管理项目的平台，而Jira是其专有的缺陷跟踪和敏捷项目管理工具。

前几天，Atlassian的发布了一个安全咨询有关的漏洞，被跟踪的CVE-2020-36239。该漏洞可能使未经身份验证的远程攻击者能够在某些Jira数据中心产品中执行任意代码。

## 漏洞产生原因

该漏洞与Jira的Ehcache实现中缺少身份验证检查有关，Ehcache是一种开源Java分布式缓存，用于通用缓存、Java
EE和轻量级容器，用于提高性能并简化可扩展性。

Atlassian表示，该漏洞是在Jira Data Center、Jira Core Data Center、Jira Software Data
Center 和 Jira Service Management Data Center(在 4.14 之前称为 Jira Service Desk)的
6.3.0 版本中引入的。

根据 Atlassian 的安全公告，该产品列表公开了一个Ehcache远程方法调用 (RMI)
网络服务，攻击者可以使用该服务在端口40001和潜在的40011上连接到该服务，由于缺少身份验证，通过反序列化可以“在Jira 中执行他们选择的任意代码”。

RMI是一种API，作为一种机制，允许用Java编写的程序之间进行远程通信。它允许驻留在一个Java虚拟机 (JVM)
中的对象调用在另一个JVM上运行的对象;通常，它涉及服务器上的一个程序和客户端上的一个程序。

RMI的优势在于“程序员可以调用远程对象中存在的方法——比如运行在共享网络上的应用程序中的方法，就像运行本地方法或过程一样。”

![](https://image.3001.net/images/20210727/1627351822_60ff6b0e0c3868332c20f.png!small)

RMI的工作原理。

## 受影响的版本

以下是Jira数据中心和Jira服务管理数据中心的受影响版本：

![](https://image.3001.net/images/20210727/1627351811_60ff6b03e4c1c24d9b167.jpg!small)

Atlassian公告称，下载并安装任何受影响版本的客户“必须立即升级他们的安装以修复此漏洞。” 话虽如此，Atlassian
还指出，“关键”评级是它自己的评估，客户“应该评估其对您自己的IT环境的适用性。”

## 不受影响的版本

Atlassian云

吉拉云

Jira 服务管理云

Jira Server(核心和软件)和Jira服务管理的非数据中心实例

Jira Data Center产品用户应升级到以下版本以消除此漏洞，具体取决于他们所在的版本情况：

Jira Data Center、Jira Core Data Center 和 Jira Software Data Center 用户：升级到
8.5.16、8.13.8 或 8.17.0。

Jira 服务管理数据中心用户：升级到 4.5.16、4.13.8 或 4.17.0。

对于那些无法升级其实例的人，Atlassian在安全公告中提供了解决方法。

Atlassian建议客户升级到最新版本的产品，并限制对Ehcache RMI端口的访问。

Ehcache RMI端口40001和40011应使用防火墙或类似技术进行屏蔽，以便只有Jira Data Center、Jira Core Data
Center、Jira Software Data Center和Jira Service Management Data
Center的集群实例可以访问这些。

“虽然Atlassian强烈建议限制对Ehcache端口的访问仅限于数据中心实例，但Jira的固定版本现在需要共享密钥才能访问Ehcache服务，”Atlassian
在安全公告中表示。

## Atlassian 是攻击者猫薄荷

很多使用Atlassian产品的用户均为开发成熟的大企业。在Jira超过65,000名用户中拥有一些大粉丝，包括Apache软件基金会、思科、Fedora
Commons、Hibernate、辉瑞和Visa等公司。

不幸的是，它的受欢迎程度及其功能使其成为攻击者的诱人目标。

今年6月，研究人员发现了可能导致一键接管的Atlassian
漏洞：这种情况让人想起与SolarWinds供应链攻击类似的漏洞利用潜力，在这种情况下，攻击者使用默认密码作为打开软件更新机制的大门。

摩根预测，CVE-2020-36239可以被远程利用以实现任意代码执行，并且可能会引起网络犯罪分子和与民族国家相关的参与者的极大兴趣，他指出了最近的几次供应链攻击，包括针对软件供应商Accellion和Kaseya
的攻击，这些攻击利用漏洞获得初始访问权限并破坏“已知被不同客户群使用”的软件版本。

## 谨防供应链攻击

尽管目前发现此漏洞，但真正的影响取决于RMI
API的公开程度。这可能导致针对开发人员进行有针对性的恶意活动。而更应该注意的是，从技术角度来看，这种漏洞为供应链攻击提供了很好的途径，这也要求安全团队必须有效监控和管理这些软件应用。

尤其随着软件开发过程中存在更多的依赖项，在使用时对依赖项的任何更新都应该在使用前进行审查，并且系统应该使用版本锁定的依赖项来防止CI/CD系统默认获取最新的更新。

除此之外，对于软件开发公司自身所完成的软件代码及框架也应及时进行
**[安全漏洞检测](https://www.woocoom.com/b031.html)**
，以减少自己编写过程中出现的代码缺陷及第三方开源代码库中出现的漏洞，在发现问题时可以第一时间进行定位改正及修补，避免造成重大损失和影响。

> 参读链接：
>
> <https://www.woocoom.com/b021.html?id=268a1f91f8bc44359edac1d065e51fed>
>
> [https://threatpost.com/atlassian-critical-jira-> flaw/168053/﻿](https://threatpost.com/atlassian-critical-jira-flaw/168053/)

