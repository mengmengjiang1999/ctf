![](https://image.3001.net/images/20210119/1611056577_6006c5c1351cc1611c144.png!small)

## 漏洞概述

近期，研究人员在流行的[
_Shazam_](https://play.google.com/store/apps/details?id=com.shazam.android)应用程序中发现了一个漏洞。在该漏洞的帮助下，攻击者只需单击一个链接就可以窃取用户的精确位置！目前，受该漏洞影响的用户数量已经超过了一个亿，攻击者只需要通过单击链接即可访问受应用程序权限保护的设备功能。实际上，如果攻击者更聪明的话，这个漏洞也可以被转换为零点击漏洞。但不幸的是，苹果和谷歌拒绝为这个漏洞提供任何的漏洞奖励，不过大家不用担心，因为问题已经解决了...

该漏洞同时影响了Android和iOS设备，并且已被标记为了[
_CVE-2019-8791_](https://nvd.nist.gov/vuln/detail/CVE-2019-8791)和[
_CVE-2019-8792_](https://nvd.nist.gov/vuln/detail/CVE-2019-8792)。

## 漏洞分析

Shazam在整个应用程序中的功能导航部分使用了DeepLink技术，但是在对该应用程序进行分析的过程中研究人员发现在导出某个DeepLink（负责在webview中加载网站）时并没有对其参数进行验证，从而允许外部资源来对其进行控制。这个webview包含一些JavaScript接口，允许内容与Android&iOS
API进行通信，从而可以提取特定的设备信息以及用户最后已知的精确位置。

存在问题的DeepLink为“shazam://launchurl?url=”，这里的url参数可以是一个网站，也可以是JavaScript脚本。当webview加载时，应用程序将附加一个名为WebViewJavascriptBridge的JavaScript接口，该接口可以听过window对象进行访问。

通过对应用程序进行反编译之后，我们弄清楚了这些接口的运行机制。分析发现，这这两个对象提供了两个主要函数，即etMessageHandler和sendMessage。

setMessageHandler是一个函数，我们可以重写它来捕获通过sendMessage函数请求的操作所对应的响应信息。这个函数需要一个JSON对象，其中将包含另外两个参数，即type和data。经过编码之后，我们设计出了下列PoC：

![](https://image.3001.net/images/20210119/1611056625_6006c5f1594b753434b0b.png!small)

### 整个攻击流程大致如下图示所示：

![](https://image.3001.net/images/20210119/1611056634_6006c5fab14fbaee5664a.png!small)

## 漏洞影响

在这种攻击技术的帮助下，攻击者就可以轻松地消除目标用户的匿名性保护了。在坏人手中，这可能是危险的。只要掌握了正确的方法，就可以辨认出隐藏在网络背后的匿名用户。这样一来，隐私问题也就变成了道德问题甚至是法律问题了。

