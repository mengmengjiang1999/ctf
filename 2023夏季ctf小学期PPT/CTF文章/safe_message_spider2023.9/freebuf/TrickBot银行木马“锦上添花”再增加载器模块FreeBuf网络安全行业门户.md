**TrickBot银行木马自2016年问世以来，一直活跃至今。它从最初的银行木马发展到今天已经成为一款强大的恶意家族软件，其功能包括盗取用户电子邮箱、收集系统信息以及盗取浏览器隐私信息等等。经过几年的发展，TrickBot银行木马已经变得高度模块化，其可以由威胁参与者根据目标环境进行配置，进而实现不同的恶意功能。亚信安全也曾多次披露该木马的攻击活动（具体可见参考链接），如下表格是TrickBot银行木马主要模块的详细信息。**

![](https://image.3001.net/images/20200413/1586760797_5e940c5d82744.png!small)

近期，亚信安全网络实验室关注到该木马新增了加载器模块，该模块可以使TrickBot银行木马自身加载其他的恶意程序，例如勒索程序，挖矿程序等。其实早在去年有友商披露Trickbot木马下发Ryuk勒索病毒的攻击活动，此模块的增加使其加载其他恶意程序变得更加快捷，本文将会对此模块进行详细的分析。

在今年2月份，此木马为了更加快速扩散自身，添加了RDP扫描模块，其主要使用蛮力破解RDP，成功后将自身投放到新的设备中，亚信安全检测此模块为TrojanSpy.Win32.TRICKBOT.SMZM3。短短2个月的时间，该木马再度更新模块，可见其制作团队仍然在不断地扩展功能，不断地进行商业化。亚信安全将会持续关注TrickBot银行木马的发展动态。

##  **病毒详细分析**

TrickBot银行木马的加载器模块目前已经更新多个版本，其主要执行流程没有变化，主要的执行函数在导出的Control函数中，通过创建线程执行主要的恶意行为。

![](https://image.3001.net/images/20200413/1586760810_5e940c6ad2d9d.png!small)

![](https://image.3001.net/images/20200413/1586760816_5e940c70e256e.png!small)

其首先通过WinHTTP函数访问远程地址下载文件到本地。如下图是本次样本访问的IP以及文件名称。值得注意的是，主要的字符串使用宽UNICODE字符混淆，静态下无法直接查看。

![](https://image.3001.net/images/20200413/1586760828_5e940c7c5b602.png!small)![](https://image.3001.net/images/20200413/1586760834_5e940c82ac033.png!small)

其具体下载执行流程如下：

![](https://image.3001.net/images/20200413/1586760847_5e940c8fb7a03.png!small)

然后将文件写到本地。

![](https://image.3001.net/images/20200413/1586760856_5e940c9805a69.png!small)

该病毒首先会依次判断系统目录，APPDATA目录和Temp目录，可以访问的目录将会作为下载文件本地的存放路径。

![](https://image.3001.net/images/20200413/1586760862_5e940c9ec46de.png!small)

然后利用Windows
API函数GetNamedSecurityInfoA、SetNamedSecurityInfoW和SetEntriesInAclW修改文件的安全访问权限，目的是为了绕过从远程位置下载的文件执行保护。

![](https://image.3001.net/images/20200413/1586760869_5e940ca5542b2.png!small)

最后创建进程执行远程下载的文件。

![](https://image.3001.net/images/20200413/1586760878_5e940caed9896.png!small)

##  **关联分析**

我们通过样本获取到相关的IP和文件信息，通过亚信安全高级威胁情报平台关联到相关URL的活动。

![](https://image.3001.net/images/20200413/1586760886_5e940cb67a73f.png!small)

通过进一步分析和关联，发现此模块已经更新了多个版本并且交付多个恶意样本。

![](https://image.3001.net/images/20200413/1586760893_5e940cbd9a38f.png!small)

更多关联URL和样本信息如下所示，可见该模块近期使用频繁。由于TrickBot银行木马攻击活动多数是通过垃圾邮件方式投递，所以我们建议用户勿随意点击电子邮件的附件和链接，亚信安全邮件网关DDEI和IMSA等安全产品都可以提前有效拦截恶意的邮件和邮件附件以及其中的可疑链接。

![](https://image.3001.net/images/20200413/1586760899_5e940cc3f0795.png!small)

##  **解决方案**

> 不要点击来源不明的邮件以及附件；
>
> 不要点击来源不明的邮件中包含的链接；
>
> 请到正规网站下载程序；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 打开系统自动更新，并检测更新进行安装；

##  **IOC**

**文件** **SHA-1** |  **文件名称** |  **亚信安全检测名**  
---|---|---  
44e2946d58a37fc9ed0650f60d0979f9  |  exec_dec  |
TrojanSpy.Win32.TRICKBOT.TIGOCHF  
85fb47d7fd559eaf98ca59ed11010135  |  exec_dec  |
TrojanSpy.Win32.TRICKBOT.TIGOCHF  
2515656851cff78b9b9b356d62a970e6  |  rdpscan.dll  |
TrojanSpy.Win32.TRICKBOT.SMZM3  
  
##  **参考信息**

> 亚信安全披露TrickBot银行木马活动
>
> <https://www.freebuf.com/articles/terminal/224581.html>
>
> <https://mp.weixin.qq.com/s/N9c_y4IokWhrrUI7rE6rFg>
>
> 友商披露Trickbot木马下发Ryuk勒索病毒的攻击活动
>
> <https://www.freebuf.com/articles/system/208537.html>

***本文作者：亚信安全，转载请注明来自FreeBuf.COM**

