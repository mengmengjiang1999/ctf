# Exchange漏洞分析（一）：SSRF RCE（CVE-2021-26855、CVE-2021-27065）

阅读量 **484258**

发布时间 : 2021-11-21 10:00:47

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01f079f12841158d5e.jpg)

作者：雨夜

## 0x00 前言

在今年3月份，微软公布了多个Microsoft
Exchange的高危漏洞，通过组合利用这些漏洞可以在未经身份验证的情况下远程获取服务器权限。这套组合拳被称为ProxyLogon。安全研究员Orange
Tsai于2020年底发现该系列漏洞并命名。ProxyLogon是Exchange历史上最具影响力的漏洞之一，有上千台Exchange服务器被植入了webshell后门。

## 0x01 漏洞描述

CVE-2021-26855是一个SSRF漏洞，利用该漏洞可以绕过Exchange的身份验证，CVE-2021-27065是一个文件写入漏洞。二者结合可以在未登录的状态下写入webshell。

## 0x02 影响范围

Exchange Server 2019 < 15.02.0792.010

Exchange Server 2019 < 15.02.0721.013

Exchange Server 2016 < 15.01.2106.013

Exchange Server 2013 < 15.00.1497.012

## 0x03 调试环境及工具

|

版本  
  
---|---  
  
操作系统

|

Windows Server 2012  
  
应用名称

|

Microsoft Exchange Server 2016  
  
.NET反编译调试器

|

DnSpy  
  
.NET反编译对比器

|

Telerik ****  
  
****

## 0x04 CVE-2021-26855 SSRF漏洞

###  1. 补丁查看

通过对比补丁内容，快速定位漏洞位置。

Exchange版本号查看：

打开 ExchangeManagement Shell，并执行命令：

**Get-ExchangeServer | fl name,edition,admindisplayversion**

版本对应关系可以在微软官网中[查看](https://docs.microsoft.com/en-us/exchange/new-features/build-numbers-and-release-dates?view=exchserver-2016)：

搜索对应版本的补丁（Exchange 2016 RTM的补丁未找到，所以直接用 Exchange CU11 的补丁分析）：

[https://www.catalog.update.microsoft.com/Search.aspx?q=exchange%202016%20cu11](https://www.catalog.update.microsoft.com/Search.aspx?q=exchange%202016%20cu11)

下载补丁[KB5000871](https://www.catalog.update.microsoft.com/ScopedViewInline.aspx?updateid=67f2b6e2-ce5c-475f-9e92-949361e592aa)，使用winrar解压cab文件，解压后是一个msp文件，使用7-zip
对msp格式的文件内容进行提取。

使用[Telerik](https://www.telerik.com/download-trial-file/v2/justassembly)
对补丁内容做对比，内容有差异的dll文件如下，漏洞存在于Microsoft.Exchange.FrontEndHttpProxy.dll中：

使用Reflector对dll文件反编译并导出源码，方便对关键字进行搜索。

###  2. 漏洞调试

使用dnSpy对Microsoft.Exchange.FrontEndHttpProxy.dll 文件进行反编译，定位到class
BEResourceRequestHandler，下断点。

点击 【调试】–>【附加到进程】 MSExchangeECPAppPool，使用ProcessExplorer查看对应的进程ID。

使用进程ID进行过滤（注：必须以管理员权限运行dnSpy，否则无法获取进程信息）。

在BackEndCookieEntryParse 的TryParse()函数下断点，bp发请求，触发断点。

首先会根据uri来判断请求的协议类型，如果请求协议为ecp，即请求uri为/ecp/。跟踪进入CanHandle（）函数，验证cookie及uri的合法性。

获取cookie中X-BEResource的值

判断uri 是否合法

uri以 js，css，html，flt，xap等后缀结尾的文件（没有验证文件是否存在）都是合法的。拼接后 /ecp/xx.(js|css)
等都是有效uri。

接着对X-BEResource的值进行处理

获取到X-BEResource的值

并使用‘~’分割得到数组array

其中array[0] 为fqdn；array[1] 为version

接着进行版本比较

如果版本的值小于
E15MinVersion，进入if判断语句，并将类成员变量ProxyToDownLevel赋值为True，之后会调用身份认证函数EcpProxyRequestHandler.AddDownLevelProxyHeaders进行身份认证，如果没有通过认证，则返回401错误。同理如果version大于E15MinVersion则跳过if判断从而绕过身份认证。

经过一系列的解析

可以看到host的值是win2012，这个值我们可控，最后经过一系列的拼接得到AbsoluteUri的值：[https://host/autodiscover/autodiscover.xml](https://host/autodiscover/autodiscover.xml)
，autodiscover.xml 文件中包含有LegacyDN 的值。

进入CreateServerRequest函数，访问uri，

进入PrepareServerRequest函数，会进行授权认证判断，

接着进入AddProtocolSpecificHeadersToServerRequest，

由于ProxyToDownLevel被置为false不会进入if语句，从而导致可以直接绕过认证，进而在未授权的状态下获取autodiscover.xml文件内容。

## 0x05 CVE-2021-27065 任意文件写入漏洞

在Exchange服务器上依次打开【管理中心】 à 【服务器】 à 【虚拟目录】 à 【OAB虚拟目录】。

由于外部URL的内容可控，所以可在URL写入一句话木马（其中URL必须以http开头，以保持外部URL参数的合法性）。

之后可以通过重置虚拟目录，来把配置内容写入指定的路径。

注：路径必须是UNC路径格式：\\\host\ShareFolder\aaa.xml

修改路径为：[\\\win2012.test.local\C$\test.aspx](file://win2012.test.local/C%24/test.aspx)

可以看到OAB VirtualDirectory的配置信息已经被写入 C:/test.aspx。

l 上述操作请求内容如下：

写入配置

POST
/ecp/DDI/DDIService.svc/SetObject?schema=OABVirtualDirectory&msExchEcpCanary=pM2NWg8xu0euTUqTjiLwzquHekjm6dgIw6lt6YfDyflndCz1iGsGnnhEivzKafJL9vhOxpqYuAU.  
  
---  
  
请求中有一个关键参数msExchEcpCanary，如果没有这个参数，服务端返回500错误。这个参数的值可以利用CVE-2021-26855
SSRF漏洞通过多次请求获取。

## 0x06 漏洞利用过程

整个过程都是在未登录的状态下，利用SSRF漏洞访问内部资源，Cookie中的 X-BEResource字段内容为要访问的资源链接。利用过程如图：

1. 获取server name，/ecp/xx.js，cookie中 mail.skyeye.com 为目标exchange的域名；

2. 通过SSRF漏洞读取autodiscover.xml文件，获取LegacyDN的值；

3. 利用Legacy DN获取SID；

4. 利用SID获取Session、msExchEcpCanary；

5. 写入shell。

cookie中的 X-BEResource字段内容为利用SSRF漏洞访问的内网资源。

指定保存路径

webshell路径为：

https://[ip]/owa/auth/dkYAIm7ELFjJ3KVzXb1Q.aspx

## 0x07 检测修复方案

l **检测方案：**

针对上述漏洞，微软发布了一款工具，用于帮助用户检测Exchange是否被黑客利用相关漏洞入侵。链接如下：

[https://github.com/microsoft/CSS-Exchange/tree/main/Security](https://github.com/microsoft/CSS-Exchange/tree/main/Security#test-proxylogonps1)

脚本

|

描述  
  
---|---  
  
EOMT.ps1

|

通过 URL 重写配置缓解 CVE-2021-26855  
  
ExchangeMitigations.ps1

|

该脚本包含4个缓解措施，以帮助解决以下漏洞：cve-2021-26855、cve-2021-26857、cve-2021-27065、cve-2021-26858  
  
http-vuln-cve2021-26855.nse

|

nmap扫描脚本，检测指定URL是否存在CVE-2021-26855漏洞  
  
Test-ProxyLogon.ps1

|

该脚本检查CVE-2021-26855、26858、26857和27065漏洞是否存在被利用的迹象  
  
l **修复方案：**

安装微软提供的漏洞补丁，相关漏洞补丁如下：

https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-26855

https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-27065

## 0x08 参考链接

[https://www.freebuf.com/articles/web/265539.html](https://www.freebuf.com/articles/web/265539.html)

[https://www.praetorian.com/blog/reproducing-proxylogon-exploit/](https://www.praetorian.com/blog/reproducing-proxylogon-exploit/)

[https://docs.microsoft.com/en-us/exchange/architecture/architecture?view=exchserver-2019#client-access-protocol-architecture](https://docs.microsoft.com/en-us/exchange/architecture/architecture?view=exchserver-2019#client-access-protocol-architecture)

[https://secvery.com/5433.html](https://secvery.com/5433.html)

[https://www.4hou.com/posts/q66D](https://www.4hou.com/posts/q66D)

[https://www.anquanke.com/post/id/234607](https://www.anquanke.com/post/id/234607)

微信公众号搜索“ _云影实验室_ ”。

顺便插下招聘广告，安全研究员2名和安全开发工程师1名，有意者可以私信公众号。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **云影实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/259902](/post/id/259902)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Exchange](/tag/Exchange)
  * [ProxyLogon](/tag/ProxyLogon)

 **+1** __5赞

 __收藏

![](https://p0.ssl.qhimg.com/t012b723966029ed2c4.png) 云影实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

