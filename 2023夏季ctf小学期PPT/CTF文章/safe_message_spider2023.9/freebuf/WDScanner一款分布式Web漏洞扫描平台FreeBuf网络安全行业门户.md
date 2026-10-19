***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  WDScanner 简介

 **随着互联网各种安全漏洞愈演愈烈，JAVA 反序列化漏洞、STRUTS 命令执行漏洞、ImageMagick
命令执行漏洞等高危漏洞频繁爆发。在这种情况下，为了能在漏洞爆发后快速形成漏洞检测能力，同时能对网站或主机进行全面快速的安全检测，开发了一套简单易用的分布式
web 漏洞检测系统 WDScanner。**

![1557984931_5cdcf6a34e7b7.png](https://image.3001.net/images/20190516/15580082806024.png!small)

WDScanner 平台目前实现了如下功能：

> **客户管理：添加客户、添加客户持有系统、设置客户持有系统的扫描策略、周期性扫描等**
>
> **漏洞扫描：分布式 web 扫描、漏洞定期扫描、敏感信息泄露扫描、漏洞管理等**
>
> **信息搜集：网站标题、banner、端口开放、子域名、CMS 指纹、操作系统版本、开发语言、WAF、CDN、中间件等**
>
> **网站爬虫：网站链接爬取、暗链检测、坏链检测、敏感字检测**
>
> **其他功能：代理搜集、检索中心、导出报告**

* * *

##  声明

**本平台只是对目标系统进行信息搜集和端口开放性探测，漏洞扫描调用了 wvs 的扫描核心，主要是为了方便大家对目标系统进行安全检测并出具中文报告。**

**对互联网任何目标的检测均需在取得授权后方可进行，如需测试本平台可用性请自行搭建靶机环境。若使用者因此做出危害网络安全的行为后果自负，与作者无关，特此声明。**

##  更新说明

**v1.0 版本：** 在 2019 年 3 月开源在 github
上，但之前没想到大家会对这个小平台关注度这么高，所以提供的安装方法也比较简陋，导致很多朋友在安装时遇到一些问题浪费了一些时间，在此表示歉意。

**v1.1 版本：** 2019 年 5
月，根据大家的反馈，重新打包了整个环境，提供了三种详细的安装方式。由于里面有个别模块是对接的我们内网其他系统，比如社工库、poc
库之类的，所以这里就不再提供。

* * *

##  安装方式

###  方式 1：虚拟机环境

1、下载虚拟机镜像

    
    
    链接: https://pan.baidu.com/s/1wGATRO57d8jNzZz4N3mNPQ 提取码:27ks  解压密码 www.tidesec.net

打包好的 vmware 镜像，使用 VMware Workstation 15 Pro 制作，直接下载后解压，用 vmware 打开即可，理论上 15.0
以上版本都可以。

**在 VMware Workstation 15 及以上版本如果提示「导入失败」，提示「规范一致性和硬件合规性」检查什么的，直接点「重试」即可。**

    
    
    提供一个 VMware Workstation 15 Pro 的下载地址：
    链接: https://pan.baidu.com/s/1lqglKWzknAjeyrEnAaXLJA 提取码: icmv

虚拟机为 win7 系统，用户名 TideSec，密码 123456。虚拟机默认是 nat 模式联网，理论上可自动分配 ip 地址可直接使用。

另外，虚拟机为 win7 sp1，没打任何补丁，ms17010 什么的应该也有，如有必要请自行加固虚拟机。

2、运行桌面上的 phpstudy，启动服务。

3、运行桌面上的 Tide-proxy-bat.bat 和 Tide-WDScanner-bat.bat 两个文件。

4、本机访问 <http://127.0.0.1> ，用户名密码为 admin/123456，登录即可，然后进行添加客户、添加任务、执行扫描等。

###  方式 2：半集成安装

1、下载软件包

    
    
    链接：https://pan.baidu.com/s/1ojKxbrDabLqtL4HDgjljlg  提取码：vb3h  解压密码 www.tidesec.net

这里面打包好了 phpstudy 环境，把它解压到 C 盘根目录下，目录名不要变，即 C:\WDScanner 目录下。

2、安装 python2.7、ruby、nmap、awvs10.5、pip 等。

从安装包的 wdscan-soft 目录下安装相应软件，进行环境变量配置。

3、安装 python 依赖库

因为后台脚本都是使用的 python 来运行，所以调用了一些第三方库，在 TaskPython 目录下有个 requirements.txt 文件

在 TaskPython 目录下执行 pip install -r requirements.txt 即可。

4、在 TaskPython 目录下分别执行 Tide-proxy-bat.bat 和 Tide-WDScanner-bat.bat 两个文件，则分别开启了
WDScanner 后台任务和代理搜集任务。

5、本机访问 <http://127.0.0.1> ，用户名密码为 admin/123456，登录即可，然后进行添加客户、添加任务、执行扫描等。

###  方式 3：手工安装

1、安装 python2.7、ruby、nmap、awvs10.5、pip 等。

建议使用 windows 环境，因为 wvs 当时只能运行在 windows 环境下（现在好像有了 linux 版），wvs 建议使用 wvs10.5
版本。python 和 pip 安装后配置好环境变量。

我把上面需要几个软件进行了打包，在 wdscan-soft 目录下，逐个安装即可，下载地址：

    
    
    链接：https://pan.baidu.com/s/1ojKxbrDabLqtL4HDgjljlg  提取码：vb3h  解压密码 www.tidesec.net

2、安装 php 运行环境

建议使用 apache，php 版本 5.*不要太高，建议使用 phpstudy，简单便捷，一键部署。

将所有文件放在 c:\wdscanner\www 目录下。因为有些偷懒，把一些路径写的绝对路径，如果自己有代码编辑能力，强烈建议自行二次开发。

3、安装 python 依赖库

因为后台脚本都是使用的 python 来运行，所以调用了一些第三方库，在 TaskPython 目录下有个 requirements.txt 文件

在 TaskPython 目录下执行 pip install -r requirements.txt 即可。

4、解压缩 wdscanner.sql.zip，在 mysql 中新建数据库 wdscan，将其中的 wdscanner.sql 导入，在 include
目录下的 config.inc.php 中修改数据库密码。

5、在扫描节点上运行 TaskPython 目录下的 taskscan.py、taskspider.py、taskinfo.py
即可分别进行任务扫描、网站爬取关键字分析、信息搜集等。（由于 w3af 配套部署比较麻烦，所以本版本未集成 w3af）

6、执行 TaskPython/proxy 目录下的 ip_pool.py、assess_quality.py 可进行代理搜集及代理评分。

7、本机访问 <http://127.0.0.1> ，用户名密码为 admin/123456，登录即可，然后进行添加客户、添加任务、执行扫描等。

##  功能介绍

###  1、登录界面

![](https://image.3001.net/images/20190516/1557984948_5cdcf6b41694a.jpg!small)

项目大厅，配色比较恶俗

![](https://image.3001.net/images/20190516/1557984955_5cdcf6bba2ff3.jpg!small)

###  2、分布式扫描

WDScanner 使用了分布式 web 漏洞扫描技术，前端服务器和用户进行交互并下发任务，可部署多个扫描节点服务器，能更快速的完成扫描任务。

![](https://image.3001.net/images/20190516/1557984965_5cdcf6c5071f2.jpg!small)

因为 wvs 的结果是英文的，如果需要提供报告给客户的话友好度不高，所以对 wvs 的扫描结果、加固建议、漏洞描述等进行了汉化。

对 wvs 的汉化主要是爬取了 wvs 官方的漏洞库，对较为常见的漏洞进行了人工翻译，然后使用谷歌翻译对其他漏洞进行了翻译，人工进行了核对，最终大约包含
670 个漏洞。

汉化后的数据库可从这个表中获取，<https://github.com/TideSec/WDScanner>，在数据库文件的 vul_cn 表中。

![](https://image.3001.net/images/20190516/1557985257_5cdcf7e962923.jpg!small)

扫描核心库使用了 secscanner+w3af+awvs 三款工具（secscanner 是在建的另一套 web 扫描器，w3af
是最好的开源扫描器），使用较多的扫描工具可能导致扫描速度有所降低，但误报率也会大大降低，扫描时也可选择最实用的扫描策略以节省时间。

![](https://image.3001.net/images/20190516/1557984975_5cdcf6cf79034.jpg!small)

![](https://image.3001.net/images/20190516/1557984986_5cdcf6da9191e.jpg!small)

###  3、客户管理

能对客户和资产进行管理，根据客户需求定制化扫描和监测方案，对网站进行定期扫描和网站爬取，检索敏感字、坏链、暗链、信息泄露等威胁，发现风险能及时提醒并告知客户。

![](https://image.3001.net/images/20190516/1557984998_5cdcf6e6ef226.jpg!small)

###  4、网站信息收集

在添加新任务后，后台可主动识别目标 banner 和操作系统信息、端口开放、敏感文件扫描等。

![](https://image.3001.net/images/20190516/1557985005_5cdcf6ed3b94b.jpg!small)

自动识别开发语言、WAF、CMS 和中间件等，并对常见端口进行扫描并判断其服务。

![](https://image.3001.net/images/20190516/1557985012_5cdcf6f423748.jpg!small)

子域名的搜集使用了暴力枚举和互联网检索两种方式，保证了子域名的可用性并缩短了检索时间。

![](https://image.3001.net/images/20190516/1557985021_5cdcf6fd17e1d.jpg!small)

###  5、网站爬虫

目前政府类网站对暗链、敏感字和坏链等内容比较敏感，而网站爬虫可较好的解决这部分需求。

![](https://image.3001.net/images/20190516/1557985027_5cdcf7035c966.jpg!small)

网站爬虫主要是周期性对目标整站页面进行爬取，爬虫算法主要采用了宽度优先遍历策略，可进行网页链接搜集、动态 URL
搜集、网站敏感字检索、暗链检索、坏链检测、存储网页快照等。

![](https://image.3001.net/images/20190516/1557985034_5cdcf70a0ceff.jpg!small)

###  6、专项检测

WDScanner 集成了专项漏洞检测功能，可在发生高危漏洞时快速部署检测 POC，对客户网站进行批量安全性检测。

![](https://image.3001.net/images/20190516/1557985040_5cdcf7109d6a0.jpg!small)

###  7、检索中心

检索中心可使用关键字对漏洞扫描、信息搜集、网站爬虫等进行检索，如漏洞类型、操作系统类型、开放端口、中间件类型、开发技术等。

![](https://image.3001.net/images/20190516/1557985047_5cdcf717e2543.jpg!small)

网站 URL 检索，以检索包含.action 的 URL 为例。

![](https://image.3001.net/images/20190516/1557985056_5cdcf720af029.jpg!small)

###  8、代理资源池

内置了代理资源池功能，对搜集到的代理地址的可用性进行动态打分排序，可以在扫描探测被封 ip 时智能切换 IP 地址。

![](https://image.3001.net/images/20190516/1557985066_5cdcf72a0121f.jpg!small)

###  9、节点管理

对扫描节点进行管理，不在范围内的节点无法请求平台任务。

![](https://image.3001.net/images/20190516/1557985074_5cdcf7329e91c.jpg!small)

###  10、报告输出

报告输出是专业扫描器不可缺少的部分，看起来功能不是很起眼，但的确花了我们很多时间和精力来实现这个功能。现在还只是实现了一个常规报告模板，而且在漏洞分类里还有些重复，后续还会慢慢完善。

在任务管理里每个任务都可以进行报告导出，大家可以看下报告的大体版式和内容，本想加入图表，暂时没能实现。生成的报告大体这样。

概述部分：

![](https://image.3001.net/images/20190516/1557985083_5cdcf73b25d2a.jpg!small)

漏洞展示：

![](https://image.3001.net/images/20190516/1557985091_5cdcf743205be.jpg!small)

敏感字：

![](https://image.3001.net/images/20190516/1557985097_5cdcf749a8914.jpg!small)

信息泄露：

![](https://image.3001.net/images/20190516/1557985106_5cdcf7523c1b1.jpg!small)

##  Tips

1、平台是之前开发的，有些代码可能存在 bug，不要部署在互联网上；

2、部分功能因为耗时较长，已在代码中注释掉，建议有兴趣的可以进行二次开发。

3、提供的虚拟机镜像为 win7 sp1，没打任何补丁，ms17010 什么的应该也有，如有必要请自行加固虚拟机。

 ***本文作者：Tide重剑无锋，转载请注明来自FreeBuf.COM**

