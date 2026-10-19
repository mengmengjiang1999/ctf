##  前言  

 **最近在攻防演练中经常会遇到蜜罐，这次就来唠唠蜜罐。**

蜜罐是对攻击者的欺骗技术，用以监视、检测、分析和溯源攻击行为，其没有业务上的用途，所有流入/流出蜜罐的流量都预示着扫描或者攻击行为，因此可以比较好的聚焦于攻击流量。

蜜罐可以实现对攻击者的主动诱捕，能够详细地记录攻击者攻击过程中的许多痕迹，可以收集到大量有价值的数据，如病毒或蠕虫的源码、黑客的操作等，从而便于提供丰富的溯源数据。

但是蜜罐存在安全隐患，如果没有做好隔离，可能成为新的攻击源。

##  一、蜜罐分类

按用途分类，蜜罐可以分为研究型蜜罐和产品型蜜罐。研究型蜜罐一般是用于研究各类网络威胁，寻找应对的方式，不增加特定组织的安全性。产品型蜜罐主要是用于防护的商业产品。

按交互方式分类，蜜罐可以分为三类，低交互式蜜罐，中交互式蜜罐，高交互式蜜罐。

> 低交互式蜜罐 ：通常是指与操作系统交互程度较低的蜜罐系统，仅开放一些简单的服务或端口，用来检测扫描和连接，这种容易被识别。
>
> 中交互式蜜罐
> ：介于低交互式和高交互式之间，能够模拟操作系统更多的服务，让攻击者看起来更像一个真实的业务，从而对它发动攻击，这样蜜罐就能获取到更多有价值的信息。
>
> 高交互式
> ：指的是与操作系统交互很高的蜜罐，它会提供一个更真实的环境，这样更容易吸引入侵者，有利于掌握新的攻击手法和类型，但同样也会存在隐患，会对真实网络造成攻击。

常见的比较优秀的蜜罐：

> Honeyd： <https://github.com/DataSoft/Honeyd>
>
> T-pot : <https://github.com/dtag-dev-sec/tpotce>

常见的WEB蜜罐：

> HFISH: <https://github.com/hacklcx/HFish>
>
> opencanary web : <https://github.com/p1r06u3/opencanary_web>

评分较高的蜜罐：

研究的过程中，发现了有人已经对市面上的大部分蜜罐进行了测试和评分，因为比较多，下面列举出排名前五名的蜜罐：

> Shadow Daemon： <https://shadowd.zecure.org/overview/introduction/>

影子守护进程是一组工具的集合，用于检测、记录和阻止对web应用程序的攻击。从技术上讲，影子守护进程是一个web应用程序防火墙，它拦截请求并过滤恶意参数。它是一个模块化的系统，将web应用程序、分析和接口分离开来，以提高安全性、灵活性和可扩展性。

影子守护进程是免费软件。它是在GPLv2许可下发布的，所以它是开源的，每个人都可以检查、修改和分发代码。

![image.png](https://image.3001.net/images/20200512/15892747183874.png!small)
难易性★★★★☆

可用性★★★★★

展示性★★★★★

交互性★★★★★

> RDPy： <https://github.com/citronneur/rdpy>

RDPY是Microsoft
RDP远程桌面协议协议客户端和服务器端的纯Python实现。RDPY是在事件驱动的网络引擎Twisted上构建的。RDPY支持标准RDP安全层基于SSL的RDP和NLA身份验证通过ntlmv2身份验证协议。

![image.png](https://image.3001.net/images/20200512/15892747302526.png!small)难易性★☆☆☆☆

可用性★★★★★

展示性★★★★★

交互性★★★★★

snare

这个蜜罐是复制别人网站的源码程序原理跟钓鱼网站差不多

![image.png](https://image.3001.net/images/20200512/15892747436325.png!small)难易性★★☆☆☆

可用性★★★★★

展示性★★★★★

交互性★★★★☆

django-admin-honeypot

![image.png](https://image.3001.net/images/20200512/15892747538359.png!small)难易性★☆☆☆☆

可用性★★★★★

展示性★★★★★

交互性★★★★☆

> Artillery ： <https://github.com/trustedsec/artillery/>

开源蓝队工具，旨在通过多种办法保护 Linux 和 Windows 操作系统。

![image.png](https://image.3001.net/images/20200512/15892747637366.png!small)

难易性★☆☆☆☆

可用性★★★★★

展示性★★★★★

交互性★★★★☆

##  二、如何识别

攻击者也会尝试对蜜罐进行识别。比较容易的识别的是低交互的蜜罐，尝试一些比较复杂且少见的操作能比较容易的识别低交互的蜜罐。相对困难的是高交互蜜罐的识别，因为高交互蜜罐通常以真实系统为基础来构建，和真实系统比较近似。对这种情况，通常会基于虚拟文件系统和注册表的信息、内存分配特征、硬件特征、特殊指令等来识别。

我们可以通过以下方式去做蜜罐识别：

> 1\. BOF的识别；BOF（Back Officer Friendly）
>
> 2\. 假代理技术，关注Honeypot Hunter软件；
>
> 3\. Honeyd的识别；
>
> 4\. 利用Sebek识别蜜网，第二、三代蜜网都有这个软件；
>
> 5\. Tarpits的识别；
>
> 6\. 外联数据控制识别，一般蜜罐会严格限制系统向外的流量；
>
> 7\. 识别VMware虚拟机，重点关注MAC地址的范围
>
> 8\. 用Nmap等Scan工具，同一个机器同时开放很多Port的。
>
> 9\. 因为很多蜜罐都设置在相同或临近的网段。所以，同一个网段（e.g. ／24），很多机器都开放相同的Port，回应相似的Response。
>
> 10\. 去Shodan／Censys查

##  三、常见蜜罐展示

###  1.无交互蜜罐: 只针对网络批量扫描器

通过释放大量指纹诱导扫描器攻击

> <http://121.196.52.0:88/>
>
> <http://47.110.66.64:5560/>

![image.png](https://image.3001.net/images/20200512/15892747775638.png!small)

可以发现此web有许多组件 ，右键查看源代码，可以发现如下内容：

![image.png](https://image.3001.net/images/20200512/15892747967455.png!small)![image.png](https://image.3001.net/images/20200512/15892748015366.png!small)![image.png](https://image.3001.net/images/20200512/15892748067148.png!small)

###  **2.低交互蜜罐: HFISH (被动/主动收集信息)**

> <https://github.com/hacklcx/HFish>

页面展示如下, 一般开放在9001端口, 查询title "HFish - 扩展企业安全测试主动诱导型开源蜜罐框架系统", 可以检索到一部分开放在公网的

> <http://182.92.157.178:9001/login>

![image.png](https://image.3001.net/images/20200512/1589274830511.png!small)一般用户拿来使用的时候也不会进行修改,
所以很好识别

而且由于秘钥硬编码, 攻击者可以直接利用默认配置中的key访问日志信息，反日蜜罐。

> 比如：
> <http://localhost:9001/api/v1/get/passwd_list?key=X85e2ba265d965b1929148d0f0e33133>
>
> 另外其它的 API可以见官方 Document 说明 ：
> [https://hfish.io/docs/#/help/api](file:///C:/Users/Tophanter030/Documents/WeChat%20Files/sxc13959216473/FileStorage/File/2020-05/%E6%94%BB%E9%98%B2%E5%AF%B9%E6%8A%97%E4%B8%AD%E7%BA%A2%E9%98%9F%E5%A6%82%E4%BD%95%E8%AF%86%E5%88%AB%E8%9C%9C%E7%BD%90%E4%BF%9D%E6%8A%A4%E8%87%AA%E5%B7%B1.doc#/help/api)

还有其它的一些地址：

>
> 182.92.157.178:9001/api/v1/get/fish_info?key=X85e2ba265d965b1929148d0f0e33133
>
>
> <http://182.92.157.178:9001/api/v1/get/fish_info?key=X85e2ba265d965b1929148d0f0e33133>
>
>
> <http://182.92.157.178:9001/api/v1/get/passwd_list?key=X85e2ba265d965b1929148d0f0e33133>
>
>
> <http://182.92.157.178:9001/api/v1/get/ip?key=X85e2ba265d965b1929148d0f0e33133>

###  3.高交互蜜罐: 真实环境部署探针

通过在真实环境安插探针, 保留原有业务功能的情况下, 也可以获取攻击者信息

> <http://61.50.134.234:8080/www>

![image.png](https://image.3001.net/images/20200512/15892748527495.png!small)

![image.png](https://image.3001.net/images/20200512/15892748632141.png!small)

![image.png](https://image.3001.net/images/20200512/15892754136547.png!small)

***本文作者：Elina3000，转载请注明来自FreeBuf.COM**

