#### [i春秋作家：天析](https://bbs.ichunqiu.com/thread-48125-1-1.html)  

0x1：关于APT的相关介绍：

APT是什么？

APT（AdvancedPersistent
Threat）高级持续性威胁。是指组织(特别是政府)或者小团体利用先进的攻击手段对特定目标进行长期持续性网络攻击的攻击形式。APT是黑客以窃取核心资料为目的，针对客户所发动的网络攻击和侵袭行为。

APT手法？

APT的攻击手法，在于隐匿自己，针对特定对象，长期、有计划性和组织性地窃取数据，此类攻击行为是传统安全检测系统无法有效检测发现，前沿防御方法是利用非商业化虚拟机分析技术，对各种邮件附件、文件进行深度的动态行为分析，发现利用系统漏洞等高级技术专门构造的恶意文件，从而发现和确认APT攻击行为。由于APT的特性，导致难发现、潜在威胁大，一旦被攻击将导致企业、政府、医疗组织等等的大量数据被窃取，公司重要财务、机密被盗窃。

  

0x2:初探APT大门（走进内网）

  

DMZ区域

A公司里，准备用一台服务器用来开放web服务以供给别人看和宣传一下自己公司的产品，小王（项目负责人）想到近来许多大公司数据都被窃取，于是他想了个办法把web服务器置于另一个网络，访问不了公司内网的一个空间，把smtp服务器、web服务器架设在dmz区里面防止因网站被入侵而导致公司数据被盗窃。

两个防火墙之间的空间被称为DMZ，与Internet相比，DMZ可以提供更高的安全性，但是其安全性比内部网络低，它是为了解决安装防火墙后外部网络的访问用户不能访问内部网络服务器的问题，而设立的一个非安全系统与安全系统之间的缓冲区。

该缓冲区位于企业内部网络和外部网络之间的小网络区域内，在这个小网络区域内可以放置一些必须公开的服务器设施，如企业Web服务器、FTP服务器和论坛等。另一方面，通过这样一个DMZ区域，更加有效地保护了内部网络。因为这种网络部署，比起一般的防火墙方案，对来自外网的攻击者来说又多了一道关卡。

  

DMZ区域既可以与外网通讯，也可以与内网通讯，但受安全策略的限制。

  

所以在现如今，用web服务器当跳板来入侵内网已经是不现实的了，那么有没有什么可以简单易操作，的入侵方法呢？

  

0x3:常见利用

  

你可能想到了办公套件这类神器，正所谓：最大的漏洞不是存在于任何系统上面，而是人

  

OFFICE 漏洞一览：

=======================================================================================

  
|  
  
---|---  
CVE-2009-2496| 堆损耗远程代码执行漏洞，又称作 “Office Web 组件堆损耗漏洞| 丰收行动  
CVE-2010-3333| RTF分析器堆栈溢出漏洞，又称”RTF栈缓冲区溢出漏洞”|  
  
CVE-2012-0158| Microsoft Windows Common Controls
ActiveX控件远程代码执行漏洞，栈内存拷贝溢出漏洞，又称“MSCOMCTL.OCX RCE漏洞”| 摩诃草  
蔓灵花  
白象  
Rotten Tomato  
CVE-2013-3906| Microsoft Graphics组件处理特制的TIFF图形时存在远程代码执行漏洞| 摩诃草  
白象  
CVE-2014-1761| Microsoft Word RTF文件解析错误代码执行漏洞| 摩诃草  
Pitty Tiger  
白象  
Rotten Tomato  
CVE-2014-4114| OLE包管理INF 任意代码执行漏洞| 摩诃草  
白象  
CVE-2015-1641| RTF解析中的类型混淆漏洞| MONSOON  
摩诃草  
白象  
奇幻熊  
Rotten Tomato  
丰收行动  
CVE-2015-2545| EPS图形文件任意执行代码| Rotten Tomato  
CVE-2015-2546| UAF（释放后重用）漏洞|  
  
CVE-2016-7193| RTF文件解析漏洞，可远程执行任意代码|  
  
CVE-2017-0199| 首个Microsoft Office RTF漏洞| 暗黑客栈  
CVE-2017-0261| EPS中的UAF漏洞| 摩诃草  
白象  
Turla  
CVE-2017-0262| EPS中的类型混淆漏洞| 摩诃草  
白象  
CVE-2017-11826| OOXML解析器类型混淆漏洞| 东亚某组织  
CVE-2017-11882| “噩梦公式”公式编辑器中的栈溢出漏洞，可远程代码执行| 白象  
响尾蛇  
寄生兽  
摩诃草  
人面马  
黑凤梨  
CVE-2017-8464| 解析快捷方式时存在远程执行任意代码的高危漏洞|  
  
CVE-2017-8570| OLE对象中的逻辑漏洞 (CVE-2017-0199的补丁绕过)，“沙虫”二代漏洞| 白象  
寄生兽  
摩诃草  
CVE-2017-8759| .NET Framework中的逻辑漏洞|  
  
CVE-2018-0802| “噩梦公式二代”利用office内嵌的公式编辑器EQNEDT32.EXE发起攻击| 黑凤梨  
CVE-2018-0798| Microsoft Office远程内存破坏漏洞|  
  
CVE-2018-8174| 利用浏览器0day漏洞的新型Office文档攻击|  
  
  
======================================================================================================

Adobe漏洞一览：

======================================================================================================

CVE-2007-5659| Adobe Acrobat/Reader PDF文件 多个缓冲区溢出漏洞| Adobe Acrobat 8  
Adobe Reader 8  
Adobe Reader 7| 丰收行动  
---|---|---|---  
CVE-2008-2992| Adobe Reader util.printf() JavaScript函数栈溢出漏洞| Adobe Acrobat <
8.1.3  
Adobe Reader < 8.1.3| 丰收行动  
CVE-2009-0927| Adobe Acrobat和Reader Collab getIcon() JavaScript方式栈溢出漏洞| Adobe
Acrobat 9  
Adobe Acrobat 8  
Adobe Acrobat 7.0  
Adobe Reader 9  
Adobe Reader 8  
Adobe Reader 7| 丰收行动  
CVE-2009-4324| Adobe Reader和Acrobat newplayer() JavaScript方式内存破坏漏洞| Adobe
Acrobat <= 9.2  
Adobe Reader <= 9.2| 丰收行动  
CVE-2010-0188| Adobe Reader和Acrobat TIFF图像处理缓冲区溢出漏洞| Adobe Acrobat < 9.3.1  
Adobe Acrobat < 8.2.1  
Adobe Reader < 9.3.1  
Adobe Reader < 8.2.1| 丰收行动  
CVE-2010-3653| Adobe Shockwave Player Director文件rcsL块解析内存破坏漏洞| Adobe Shockwave
Player 11.5.8.612| 丰收行动  
CVE-2012-0773| Adobe Flash Player / AIR NetStream类任意代码执行或拒绝服务漏洞| Adobe Flash
Player 11.x  
Adobe AIR 3.x| The mask  
CVE-2013-0640| Adobe Acrobat和Reader远程代码执行漏洞| Adobe Acrobat 9.x  
Adobe Acrobat 11.x  
Adobe Acrobat 10.x  
Adobe Reader 9.x  
Adobe Reader 11.x  
Adobe Reader 10.x| 丰收行动  
| | |  
CVE-2014-0497| Adobe Flash Player远程代码执行漏洞| Adobe Flash Player 12.x  
Adobe Flash Player 11.x| 暗黑客栈  
CVE-2015-5119| Adobe Flash Player ActionScript 3 ByteArray释放后重用远程漏洞| Adobe
Flash Player <= 18.0.0.194  
Adobe Flash Player <= 18.0.0.194  
Adobe Flash Player Extended Support Release 13.x  
Adobe Flash Player Extended Support Release 13.0.0.296  
Adobe Flash Player for Linux 11.x  
Adobe Flash Player for Linux 11.2.202.468| 蓝白蚁  
Hacking Team  
CVE-2015-8651| Adobe Flash Player整数溢出漏洞| Adobe Flash Player < 18.0.0.324  
Adobe Flash Player < 11.2.202.559  
Adobe Flash Player 20.x-20.0.0.267  
Adobe Flash Player 19.x  
Adobe AIR < 20.0.0.233| 暗黑客栈  
CVE-2016-0984| Adobe Flash远程代码执行漏洞| Adobe Flash Player before 18.0.0.329 and
19.x and 20.x before 20.0.0.306| BlackOasis  
CVE-2016-4117| Adobe Flash Player 任意代码执行漏洞| Adobe Flash Player <= 21.0.0.226|
奇幻熊  
CVE-2016-7855| Adobe Flash Player 释放后重利用远程代码执行漏洞| Adobe Flash Player <=
23.0.0.185  
Adobe Flash Player <= 11.2.202.637|  
  
CVE-2017-11292| 类型混淆漏洞导致的远程代码执行| Adobe Flash Player Desktop Runtime  
Adobe Flash Player for Google Chrome  
Adobe Flash Player for Microsoft Edge and Internet Explorer 11  
Adobe Flash Player Desktop Runtime| 黑色绿洲  
Lazarus  
CVE-2018-4878| Adobe Flash Player释放后重利用远程代码执行漏洞| Adobe Flash Player <=
28.0.0.137| Lazarus  
  
============================================================================

以上是一些APT用烂了的漏洞资料，接下来看看最常见的攻击方式：（来源于百度百科）

  

1、 鱼叉式钓鱼攻击

由于鱼叉式网络钓鱼锁定之对象并非一般个人，而是特定公司、组织之成员，故受窃之资讯已非一般网络钓鱼所窃取之个人资料，而是其他高度敏感性资料，如知识产权及商业机密。

一次简单的点击相当于为攻击者开启了一扇电子门，这样他就可以接触到你的内部了，因为你已经同意他进入！

2、 水坑攻击

水坑攻击是一种计算机入侵手法，其针对的目标多为特定的团体，攻击者首先通过猜测或观察确定这组目标经常访问的网站，并入侵其中一个或多个，植入恶意软件，最后，达到感染该组目标中部分成员的目的。

由于此种攻击借助了目标团体所信任的网站，攻击成功率很高，即便是那些对鱼叉攻击或其他形式的钓鱼攻击具有防护能力的团体。

3、 [社会工程学](http://www.ichunqiu.com/#profession)

社会工程学是一种通过人际交流的方式获得信息的非技术渗透手段。不幸的是，这种手段非常有效，而且应用效率极高。

  

然而事实上，社会工程学已是[企业安全](http://www.ichunqiu.com/courses/313)最大的威胁之一

我们来看看毒云藤（APT-C-01）组织的鱼叉式钓鱼攻击文档的页面

（携带漏洞文档界面，图片来源于freebuf）

![image.png](https://image.3001.net/images/20181123/1542945224_5bf779c888ed2.png!small)![image.png](https://image.3001.net/images/20181123/1542945238_5bf779d674f01.png!small)

（携带二进制程序的文档图片来源于freebuf）

![image.png](https://image.3001.net/images/20181123/1542945257_5bf779e93870e.png!small)

从上面文档内容简要来看，apt组织在事前已经对xx部门做了许多信息收集的迹象，伪造的文档如果不是内部成员很难看出端倪。

回放一下攻击流程：

![image.png](https://image.3001.net/images/20181123/1542945269_5bf779f595f97.png!small)

在确定目标公司后，APT组织会开始收集目标的一切信息，如：公司用户的电子邮箱，手机号码，通讯软件号码、姓名、你的工作岗位。接着APT组织会对目标开始构造钓鱼文档并准备投放，当内部工作人员打开恶意文档了之后，电脑会触发相关的漏洞为apt成员打开了一道通往内部网络的大门,这时候他们会开始寻找存放着信息的服务器并开始[攻击服务器](http://www.ichunqiu.com/courses/277)拿到自己想要的东西后，在植入木马进行权限维持。

0x4：场景回放

钓鱼是APT组织最常用的攻击方式，但以上数据仅表面我们只是知道了APT组织的一些攻击，并没有掌握全部资料，APT攻击隐秘，有组织，能力强。“影子经纪人”泄露的NSA武器库“EternalBlue”就是来源自APT组织“方程组”，可见APT组织的破坏力有多大。

在询问了几个大表哥后得知，现如今通过钓鱼邮件进行攻击方式在互联网上占了将近一半，在当前能找到的apt攻击防御资料中，至少有一半的攻击都是通过钓鱼邮件进行的，而于传统黑客行动不同的是，apt组织会用一切手段去攻击目标，对于他们来说，并不在乎人力、物力和财力，他们只在乎成功率。

我们来模拟一个简单的APT攻击：

环境搭建：

> Windows7虚拟机 *1  
>  Ubuntu  
>  Windows2008 *1  
>

我将采用几个知名漏洞来为大家演示：“震网3代”、“永恒之蓝”以及“钓鱼邮件”

这些简单便捷的0day可以为APT组织省下不少力气去花时间去破解目标系统。

实验本来是想用office漏洞+flash或者是pdf，考虑到自身硬件配置和实验时间，就粗略的讲下思路来和大家分享一下，这次选用的两个漏洞均可在msf框架里面找到对应的模块去测试。

> 模块编号分别为：  
> Cve-2017-8464  
> Ms17_010  
>

生成cve-2017-8464的exp，震网三代的利用是快捷方式，把恶意快捷方式藏在u盘里面，当电脑设置自动播放，或者访问u盘时可触发漏洞

![image.png](https://image.3001.net/images/20181123/1542945286_5bf77a06e58e8.png!small)

生成的恶意文件后，我们在目标机上面执行恶意payload，使用

exploit/multi/handler模块

进行监听

![image.png](https://image.3001.net/images/20181123/1542945300_5bf77a149ce7a.png!small)

![image.png](https://image.3001.net/images/20181123/1542945311_5bf77a1fc824b.png!small)

  

把这台“钥匙”添加到路由表里面  

![image.png](https://image.3001.net/images/20181123/1542945330_5bf77a324d37e.png!small)

  
这样子我们的流量就会经过这台机子转发，接着我们使用永恒之蓝攻击服务器

![image.png](https://image.3001.net/images/20181123/1542945346_5bf77a42138e5.png!small)

  
攻击成功后我们获取了一个meterpreter会话

![image.png](https://image.3001.net/images/20181123/1542945357_5bf77a4db158c.png!small)

  
再来看看钓鱼邮件

首先我利用了cve-2017-8759

![image.png](https://image.3001.net/images/20181123/1542945382_5bf77a669d219.png!small)

生成了恶意rtf文档（windows写字板可以打开或者office而且通杀office）

然后生成了一个恶意exe

把恶意rtf文档发了过去，在在目标机接收该邮件

（在这个过程中我发现邮箱附件安全检测并没有检测出恶意文档）

![image.png](https://image.3001.net/images/20181123/1542945398_5bf77a762aac8.png!small)

开启监听等待目标机反回的会话  

![image.png](https://image.3001.net/images/20181123/1542945409_5bf77a819a103.png!small)

  
成功获得了一个meterpreter会话！

至此一次简单粗暴的攻击演示到此结束！

0x5：结语

APT组织的攻击难以捉摸，以现在掌握到的情报可能还只是冰山一角，本次演示所使用的永恒之蓝这个漏洞在很久之前就已经有了，只是在这两年被泄露出来，由此可见APT组织的恐怖之处！

  
  

  

