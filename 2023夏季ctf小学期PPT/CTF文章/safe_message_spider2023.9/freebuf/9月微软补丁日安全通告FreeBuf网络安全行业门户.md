## **一、** ** **漏洞概要****

2020年9月9日（北京时间），微软发布2020年9月份安全更新，共发布了129个CVE的补丁程序，同比上月增长9个，涵盖了Active
Directory、Internet Explorer（IE）、Office、Microsoft Windows DNS等众多组件和软件。

漏洞等级如下：23个漏洞被微软官方标记为“critical”，105个漏洞被标记为“importent”。

漏洞类型如下：38个远程代码执行漏洞，5个拒绝服务漏洞，41个权限提升漏洞，23个信息泄露漏洞。

##  **二、** ** **漏洞数据分析****

###  ** **2.1 微软在2020年修复漏洞数量趋势****

截至2020年9月9日，微软2020年各月修复的漏洞数量，”critical”漏洞数量如下所示：![](https://image.3001.net/images/20200910/1599703225.png!small)

总体来看，微软今年每月修复的漏洞数量保持在110个以上，很大程度上降低了这些漏洞在未公开情况下被利用的影响。

9月份总计公布漏洞129个，与6月持平，比上月增长了9个漏洞，严重等级漏洞也保持在今年第二高。根据各方数据评估，这种持续多数量漏洞态势会一直持续到今年年底。

除6月之外，其余月份的严重等级漏洞和总漏洞数保持同趋势（增加/降低）。

千里目实验室综合分析了往年微软公布漏洞数据和今年的特殊情况，初步估计微软在10月份公布的漏洞数量仍然在110个以上，严重等级漏洞数量应该会下降，但仍然保持在15个左右。

从侧面看，2020年漏洞公布数量已创历史新高。微软在历史上首次持续7个月保持110个以上漏洞安全补丁的发布，充分说明了微软官方对漏洞的重视程度，避免了漏洞在被利用后才进行修复和更新，一定程度上做到了事前预防，提前给用户警示，减小漏洞的实际影响力。

###  ** **2.2 历史9月份漏洞补丁情况对比****

从漏洞数来看，2017年9月份发布的漏洞补丁数为81，2018年为61，2019年升至80，而今年为129，漏洞补丁数对比趋势如下图：

![](https://image.3001.net/images/20200910/1599703266.png!small)

从漏洞的危险等级来看，今年9月份漏洞的危险等级分布相较以往基本处于平稳状态，增长趋势图如下所示：

![](https://image.3001.net/images/20200910/1599703353.png!small)

![](https://image.3001.net/images/20200910/1599703365.png!small)

在漏洞类型方面，相较于以往的对比图如下：

![](https://image.3001.net/images/20200910/1599703662.png!small)

从漏洞总数来看，今年出现了明显增长。微软在2020年已经连续7个月发布110个以上的CVE补丁程序，这是微软有史以来连续发布CVE安全补丁数量最多的一年。

从漏洞的危险等级来看，“important”等级漏洞数量明显增长。单个的重点高可利用漏洞并未出现过度增长，但单个具有普通影响力的漏洞明显增多，这加大了漏洞利用链形成的风险。这种趋势，对于APT组织或成熟的攻击组织来说是一个好消息，大幅度增加的普通影响力的漏洞提供了诸多的攻击路径和攻击手段组合的选择。

从漏洞类型来看，权限提升漏洞(EoP)大幅增加。远程代码执行漏洞(RCE)和信息泄露漏洞(Info)基本与2019年持平，相较于2017和2018年有增长。同样，信息泄露漏洞的增多有可能会扩大攻击面和攻击路径。权限提升漏洞(EoP)大幅增加，虽然影响力不如远程代码执行漏洞，但是权限提升漏洞在内网和局域网等场景下有很大的发挥空间，需要引起高度重视，尤其是在配合社工手段的前提下，甚至可以直接接管整个局域网并进行进一步扩展攻击。欺骗类型漏洞(spoof)明显增加，说明有更多的研究者开始关注逻辑类问题，这类问题基本符合产品自身的验证机制，所以在防御上比较困难。而一旦成功利用spoof类型漏洞，大多可以直接实现代码执行，需要引起重视。

##  **三、** ** **9月重要漏洞分析****

###  ** **3.1**** ** **漏洞分析****

CVE-2020-0664/0761/0718/0856，这四个漏洞均为Active Directory integrated
DNS（ADIDNS）的漏洞。攻击者可以利用CVE-2020-0664/0856漏洞读取有关系统的敏感信息，且可以通过CVE-2020-0718/0761漏洞执行任意代码。为了利用这些漏洞，经过身份验证的攻击者需要将特制请求发送到ADIDNS服务，此服务在域控制器上以SYSTEM权限运行。如果任意一个AD域以集成模式运行，则其中的DNS服务器容易受到多个漏洞的攻击（存储在AD中）。

CVE-2020-16875，Microsoft
Exchange内存损坏漏洞，当该软件无法正确处理内存中的对象时将会造成远程代码执行漏洞。成功利用此漏洞的攻击者可以在系统用户的上下文中运行任意代码，然后攻击者可以安装程序，查看、更改、删除数据或创建新帐户。一般该漏洞的攻击方式为攻击者向受影响的Exchange
Server发送特制电子邮件，以SYSTEM权限执行代码。现在已经发现了今年2月份修补的Exchange漏洞CVE-2020-0688的在野利用，建议用户注意防范。

CVE-2020-0836/1228/0839，这三个漏洞均为Windows
DNS的漏洞。CVE-2020-0836/1228，这两个漏洞为拒绝服务漏洞，Windows
DNS无法正确处理查询时将会造成拒绝服务，成功利用此漏洞的攻击者可能导致DNS服务无响应。攻击者为了利用此漏洞必须通过身份验证，因此我们建议用户提高账户的安全性，可以一定程度上规避风险，但仍然建议用户及时更新安全补丁。CVE-2020-0839为提权漏洞，dnsrslvr.dll处理内存中对象的方式出现问题，导致特权提升。成功利用此漏洞的攻击者，可以用提升的权限执行代码。

###  ** **3.2 影响范围****

 ** **CVE编号****

|

 ** **受影响版本****  
  
---|---  
  
CVE-2020-0664/0718/0761/0856

|

Windows Server 2008 Service Pack 2

Windows Server 2008 R2 Service Pack 1

Windows Server 2012, 2012 R2, 2016, 2019

Windows Server version 1903, 1909, 2004  
  
CVE-2020-16875

|

Microsoft Exchange Server 2016 Cumulative Update 16, 17

Microsoft Exchange Server 2019 Cumulative Update 5, 6  
  
CVE-2020-0836/1228

|

Windows Server 2008 Service Pack 2

Windows Server 2008 R2 Service Pack 1

Windows Server 2012, 2012 R2, 2016, 2019

Windows Server version 1903, 1909, 2004  
  
CVE-2020-0839

|

Windows 10

Windows 10 Version 1607, 1709, 1803, 1809, 1903, 1909, 2004

Windows Server 2016, 2019

Windows Server version 1903, 1909, 2004  
  
###

###  ** **3.3 修复建议****

微软官方已更新受影响软件的安全补丁，用户可根据不同版本系统下载安装对应的安全补丁，安全更新链接如下：

[ _https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-_ _0664_](https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-0664)

[ _https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-_ _0718_](https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-0718)

[ _https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-_ _0761_](https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-0761)

[ _https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-_ _0856_](https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-0856)

[ _https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-_ _16875_](https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-16875)

[ _https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-0836_](https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-0836)

[ _https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-1228_](https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-1228)

[ _https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-0839_](https://portal.msrc.microsoft.com/en-us/security-guidance/advisory/CVE-2020-0839)

