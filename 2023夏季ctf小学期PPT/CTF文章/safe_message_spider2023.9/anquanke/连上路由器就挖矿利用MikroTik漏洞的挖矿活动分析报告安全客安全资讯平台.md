# 连上路由器就挖矿：利用MikroTik漏洞的挖矿活动分析报告

阅读量 **287427**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-10-23 14:35:00

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Avast，文章来源：avast.com

原文地址：<https://blog.avast.com/mikrotik-routers-targeted-by-cryptomining-campaign-avast>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/dm/1024_348_/t01c074a537cd41935e.png)

## 概述

在今年4月，公开披露了MikroTik的一个漏洞CVE-2018-14847，同时厂商也发布了相应补丁。然而，这一漏洞在披露之后很快被黑客利用，主要用来进行加密货币的挖掘。在9月19日至10月15日期间，Avast有效阻止了受该漏洞影响导致的MikroTik网关恶意挖矿URL连接事件超过22.4万次。在部署Avast的292456个网络上，共计有效保护超过362616位用户。我们将该挖矿恶意活动检测为JS:InfectedMikroTik。

近期，Avast Threat
Labs对该恶意软件进行了更深入的分析，最终确定了两台C&C服务器，并提升了相应防护能力。针对这一恶意活动，最主要的特点之一就是在7月下旬首次发现后具有较长时间的持久性。经过仔细分析后，我们发现了此前没有重点关注的一些技术细节：该恶意软件使用了几种独特的技术，控制数十万个网络的计算能力，确保在感染的路由器中具有持久性。

除了对该恶意活动进行分析之外，本文还将说明如何确认自己的路由器是否受到影响，以及如何保护网络免受该漏洞影响。

## 日益加剧的挖矿攻击活动

随着加密货币的使用范围日益扩大，再加上目前可以通过JavaScript在浏览器中实现挖掘加密货币，上述两点因素都推动了挖矿恶意软件数量的显著增加。越来越多的网络犯罪分子，借助企业或个人用户计算机设备的资源来挖掘加密货币。

对于攻击者来说，任何具有计算能力的设备都有吸引力，而其中一个最为明显的目标就是路由器。几乎是每个家庭以及每个企业中，都会有路由器，而且路由器经常会产生因弱密码或已知漏洞而导致的安全问题。

有人可能认为，该恶意活动只会使用路由器的计算能力来挖掘加密货币，然而事实并非如此。实际上，恶意软件会充分利用所有连接到被感染路由器的设备，可以运行在这些设备的浏览器上，可以在计算机、智能手机、智能电视上运行。更严重的问题在于，一旦路由器遭到入侵，用户甚至无法确认威胁的来源。

在研究过程中，我们对其中一个受感染的路由器进行分析，并调查和分析该恶意活动的运作方式。接下来，我们将详细阐述分析的内容。

Avast阻止MikroTik路由器攻击的地理位置分布图：

![](https://blog.avast.com/hs-fs/hubfs/mikrotik-router-attacks-blocked-by-avast.png?t=1539979341325&width=812&name=mikrotik-router-attacks-blocked-by-avast.png)

JS:InfectedMikroTik主要针对的十大国家：

1、巴西（85230）

2、波兰（43677）

3、印度尼西亚（27102）

4、阿根廷（24255）

5、哥伦比亚（15300）

6、土耳其（15144）

7、印度（11809）

8、乌克兰（11614）

9、孟加拉国（9867）

10、委内瑞拉（9527）

![](https://blog.avast.com/hs-fs/hubfs/top-internet-providers-with-infected-routers.png?t=1539979341325&width=782&name=top-internet-providers-with-infected-routers.png)

## 引起关注的推文

在看到Twitter用户Bad Packets Report（[@bad_packets](https://github.com/bad_packets
"@bad_packets")）发布的推文后，我们决定对这一挖矿恶意活动进行分析。在他的推文中，提到大约有25万个受漏洞影响的路由器，并且目前这一恶意活动没有得到充分的关注。

![](https://blog.avast.com/hs-fs/hubfs/bad-packets-tweet.png?t=1539979341325&width=1024&name=bad-packets-tweet.png)

这条推文引起了我们的关注，所以我们决定更深入地找出其根本原因。通过多个消息来源，我们发现其原因在于WinBox协议中存在漏洞，该协议是一个路由器的GUI控制面板，其中存在CVE-2018-14847漏洞。然而，我们相信路由器也受到该漏洞的影响，因为其所有者没有对初始密码进行修改，或者使用了弱密码。

在使用Avast进行防护的设备中，大约有314000个MikroTik路由器，其中只有4.89%使用MikroTik的最新固件进行更新并修复了这一漏洞，有85.48%的设备容易受到Winbox漏洞利用攻击。

## 攻击方法及初步调查结果

我们开始对易受攻击和已感染的路由器进行扫描，发现这些设备具有一个共同点，就是作为Web代理的TCP/8080端口是开放的。我们可以在路由器的网络接口中发现一个开放的端口，并且，在连接到路由器代理后，其行为模式非常值得关注。

一个经过精心设计的错误提示页面，在显示用户实际尝试访问的Web内容之前，运行加密货币挖掘工具：

![](https://blog.avast.com/hs-fs/hubfs/cryptomining-code-1.png?t=1539979341325&width=802&name=cryptomining-code-1.png)

当用户尝试通过TCP 80端口，在被感染的路由器上访问以 http:// 开头的任意URL时，将会显示一个错误代码为403
Forbidden的自定义错误页面，其中包含上述HTML代码。仔细观察代码后，我们可以注意到，该过程试图运行一个脚本：

![](https://blog.avast.com/hs-fs/hubfs/cryptomining-code-2.png?t=1539979341325&width=377&name=cryptomining-code-2.png)

在针对几个不同程度的混淆进行反混淆之后，我们发现该脚本启动了一个在浏览器中运行的JavaScript加密货币挖掘工具。有趣的是，最初需要访问的网页将在10毫秒后重新加载到iframe元素中，因此用户可以通过iframe看到原始内容，同时挖矿程序在后台运行。这样一来，用户将会浏览到想要访问的内容，甚至对后台运行挖矿程序的事情毫不知情。

那么，同一个URL如何做到在10毫秒后显示真实内容，而不是再次启动挖矿呢？要了解其工作原理，我们需要深入了解MikroTik路由器的配置。因此，我们获得了配置脚本，并针对这一挖矿活动对MikroTik路由器进行了相应配置。接下来，我们详细分析该恶意活动的攻击过程。

## 攻击向量

该恶意活动，首先利用高危漏洞CVE-2018-14847实现对路由器的感染，该漏洞允许攻击者在未经授权的情况下，无需用户交互，即可访问路由器上的任意文件。在这种情况下，攻击者将目标瞄准了包含凭据的数据库文件，从而能够登录到设备上。

在这里，需要提醒大家，一定不要通过开放端口的方式，将管理界面暴露到互联网上。尽管这是一个高危漏洞，但假如攻击者不能访问管理界面，就无法利用这一漏洞。在我们的案例中，WinBox的TCP/8291端口容易受到攻击。因此，建议用户如果不需要通过网络远程管理路由器，应该关闭TCP/21的FTP端口、TCP/22的SSH端口、TCP/23的TELNET服务端口以及TCP/8291端口。

通过结合上述漏洞和弱口令，攻击者能够访问路由器，并执行多个阶段的攻击。攻击者的第一步是在路由器上放置一个脚本，该脚本计划每5分钟运行一次，从命令和控制（C&C）域名的/cmd-update.txt路径下载相应文件，并将其存储在路由器上，命名为i113.rsc。随后，通过/import命令来执行该文件：

![](https://blog.avast.com/hs-fs/hubfs/cryptomining-code-3.png?t=1539979341325&width=594&name=cryptomining-code-3.png)

在随后的阶段中，将会运行名为i113.rsc的脚本。6秒后，该脚本将被删除。由于这个脚本较长，所以我们只关注其中的几个重要部分：

首先，脚本尝试删除在路由器上运行的任何计划任务或其他脚本，包括规则、计划等等。这一部分有一个很长的列表，其中包含各种各样的脚本名称。我们认为，攻击者用了很长的一段时间来编写这个列表，并且仍然在不断调整其中的条目。

![](https://blog.avast.com/hs-fs/hubfs/cryptomining-code-4.png?t=1539979341325&width=384&name=cryptomining-code-4.png)

接下来，它将用于TELNET和SSH访问协议的端口重新映射到异常的端口，以防止恶意行为被检测到，同时防止其他人连接到路由器的管理端口。如果这些端口暂未启用，恶意软件将会将这些端口开放到网络上。正如大家在我们的分析中所看到的，在最初的脚本中，并没有这一部分。

![](https://blog.avast.com/hs-fs/hubfs/cryptomining-code-5.png?t=1539979341325&width=423&name=cryptomining-code-5.png)

下一步，是重置代理错误页面，该页面随后用于挖矿程序Payload的加载，同时启动Web代理。在其中，还添加了一条规则，以确保拒绝对该代理的任何其他请求，并将状态为403
Forbidden的error.html内容返回给用户。

![](https://blog.avast.com/hs-fs/hubfs/cryptomining-code-6.png?t=1539979341325&width=481&name=cryptomining-code-6.png)

现在，我们来到了最重要的一步，恶意软件添加了防火墙规则，将每次连接到TCP/80端口的尝试重定向到TCP/8080（Web代理）。这样一来，会将网络中任何计算机和其他设备向其发送的所有请求，通过Web代理重定向到不安全的网页（HTTP）。

![](https://blog.avast.com/hs-fs/hubfs/cryptomining-code-7.png?t=1539979341325&width=558&name=cryptomining-code-7.png)

请注意，src-address-list=!Ok是一个非常重要的细节。基本上，只有当发出请求计算机的IP地址不在!OK列表内时，才会触发这一规则。我们将在后面分析其具体原因。

这是该恶意活动的另一个关键代码，如果请求被重定向到代理，其源地址（也就是发出请求的IP地址）将会被添加到!OK列表中，并保留15秒。

![](https://blog.avast.com/hs-fs/hubfs/cryptomining-code-8.png?t=1539979341325&width=711&name=cryptomining-code-8.png)

上述两行代码表示，路由器在连接到不安全页面（HTTP）时，会每隔15秒检查一次，通过代理重定向流量。在这里，只需进行一次检查，因为在重定向时，计算机的IP地址将被添加到!Ok的清单中。基本上，每隔15秒将会注入一次挖矿工具，这也正是重复加载同一页面，最终能显示预期内容的原因。

![](https://blog.avast.com/hs-fs/hubfs/cryptominer-injection-block-diagram.png?t=1539979341325&width=1034&name=cryptominer-injection-block-diagram.png)

下一行证明了，这确实是一个恶意脚本：

![](https://blog.avast.com/hs-fs/hubfs/cryptomining-code-9.png?t=1539979341325&width=376&name=cryptomining-code-9.png)

它将日志记录设置为仅保留日志的最后一行。对于实际使用来说，这显然不是一个好的做法，但对攻击者来说，却能使管理员无法在日志文件中查看到命令的历史记录，从而给分析工作带来阻碍。

下面的一行，在端口上创建了SOCKS代理服务器，该服务器基于路由器的实际时间，使用分钟和秒来随机创建。

![](https://blog.avast.com/hs-fs/hubfs/cryptomining-code-10.png?t=1539979341325&width=567&name=cryptomining-code-10.png)

随后，下载一个恶意的error.html页面，该页面并不是常规的错误提示页面，其中包含一个注入的挖矿程序。

![](https://blog.avast.com/hs-fs/hubfs/cryptomining-code-11.png?t=1539979341325&width=704&name=cryptomining-code-11.png)

接下来，恶意软件通过计划任务，使脚本能够定期下载并安装“error.html”的最新版本，以此来实现持久化。

![](https://blog.avast.com/hs-fs/hubfs/cryptomining-code-12.png?t=1539979341325&width=748&name=cryptomining-code-12.png)

iDDNS脚本每隔5分钟运行一次，包含内容如下：

![](https://blog.avast.com/hs-fs/hubfs/cryptomining-code-13.png?t=1539979341325&width=731&name=cryptomining-code-13.png)

该代码将MAC地址、WinBox端口、SOCKS端口、PROXY端口、SOCKS和WEB代理的状态以及PPTN（VPN）服务器状态发送到C&C服务器，所有这些信息都以_分隔，合并成一个URL字符串后发送。然后，将从C&C服务器接收要运行的脚本。

随着攻击者对这些脚本的不断改进，脚本的内容仍在不断发展和变化。在撰写本文之后，可能该脚本还会发生变动，C&C服务器的域名也可能会发生变化。

## 与攻击者的猫鼠游戏

此时，由于有多种恶意软件同时存在，我们并不能清楚地掌握该恶意活动的详细情况。对这一恶意软件的分析过程，就如同在阅读一本所有人都签过名字的留言簿。据我们所知，本文中所分析的脚本，至少被两个域名使用过。

第一个服务器域名是mining117.com。更准确地说，脚本来自<http://mining117.com/update.txt> 和
<http://mining117.com/cmd-update.txt> 。

经过进一步调查，我们发现该域名自2018年3月4日开始，就一直处于活跃状态，并且由同一个托管服务提供商托管在3个不同的服务器上。

![](https://blog.avast.com/hs-fs/hubfs/mining117-scripts.png?t=1539979341325&width=1600&name=mining117-scripts.png)

我们与托管服务提供商取得了联系，并在10月5日共同关闭了这台服务器。仅仅1天之后，该恶意活动就立刻更换了另一个域名gazanew.com。令人惊讶的是，新域名来自于相同的托管网络。

![](https://blog.avast.com/hs-fs/hubfs/gazanew-scripts.png?t=1539979341325&width=1600&name=gazanew-scripts.png)

于是，我们再次要求服务提供商关闭该服务器。此后，攻击者就开始与我们玩起了“猫鼠游戏”。

![](https://blog.avast.com/hs-fs/hubfs/attacker-playing-games-after-taking-server-down.png?t=1539979341325&width=395&name=attacker-playing-games-after-taking-server-down.png)

在我们关停第二个域名之后不久，攻击者就开始禁用大量的管理接口，并将SSH和TELNET端口移动到TCP/10022和TCP/10023，这一点出乎我们的意料，甚至用户都可能不会注意到这一点。除此之外，攻击者还不断缩小他的暴露目标。例如，现在几乎不会连接到Telnet端口。此外，一旦使用泄露的凭据成功连接，几乎会立即断开连接。

![](https://blog.avast.com/hs-fs/hubfs/mikrotik-closing-hosts.png?t=1539979341325&width=1456&name=mikrotik-closing-hosts.png)

## 持续追踪攻击者

我们仍然在追击攻击者的过程中。然而，由于受感染的路由器数量庞大，因此很难进行有效的溯源。互联网上，甚至出现了一个Google文档的电子表格，跟踪被感染路由器上的所有挖掘活动：

![](https://blog.avast.com/hs-fs/hubfs/cryptominer-data-total-routers-421K.png?t=1539979341325&width=1470&name=cryptominer-data-total-routers-421K.png)

该文档位于：
<https://docs.google.com/spreadsheets/d/1RdT_r4fi4wPx5rY306FftVKaXiAZeQeb5fx78DmbVx0/edit?usp=sharing>
。

[@bad_packets](https://github.com/bad_packets
"@bad_packets")收集了来自Shodan、Censys和其他类似来源的挖矿统计数据，并进行分析。分析结果表明，用于某种挖矿活动的路由器总数已经超过421000台。并且，由于没有简单的方法能够获取关于CoinHive密钥的统计信息，我们在下面展示了能够获得加密货币余额的密钥活动。

其中一个分布式密钥的挖矿活动快照（xmr.omine.org）：

![](https://blog.avast.com/hs-fs/hubfs/mining-activity-distributed-key.png?t=1539979341325&width=1461&name=mining-activity-distributed-key.png)

其中一个分布式密钥的挖矿活动快照（MoneroOcean Pool）：

![](https://blog.avast.com/hs-fs/hubfs/moneroocean-mining-activity.png?t=1539979341325&width=1600&name=moneroocean-mining-activity.png)

## 影响用户范围

下图展现了在Avira用户群体中，MikroTik路由器的固件版本分布情况。事实上，目前仅有4.89%的用户使用了最新版本的固件（6.43.2），85.48%的用户仍然容易受到CVE-2018-14847
WinBox漏洞利用。

![](https://blog.avast.com/hs-fs/hubfs/router-os-distribution.png?t=1539979341325&width=600&name=router-os-distribution.png)

## 造成的危害

从表面上看，这一恶意活动的危害在于非法使用路由器的计算能力来挖掘加密货币，但事实并非如此。实际上，连接到受感染路由器上的所有计算机都会为攻击者执行挖矿任务，而并非仅有路由器。只要用户尝试访问不安全的Web地址（HTTP），路由器都会为用户提供一个恶意挖矿工具，从而实现这一目的。然而，更大的问题在于，一旦用户的路由器遭到入侵，用户将无法确定攻击者利用路由器具体做了什么，他们可以嗅探流量，也可以向用户提供恶意页面。

如下图所示，用户可以使用Avast Wi-Fi Inspector来查看自己的网络是否受到这一攻击的影响。此外，Wi-Fi
Inspector还可以检测MikroTik路由器服务（例如Telnet和FTP）的弱密码或默认密码，或者检测特定的HTTP篡改。

![](https://blog.avast.com/hs-fs/hubfs/wi-fi-inspector-winbox-vulnerability-screen.png?t=1539979341325&width=1010&name=wi-fi-inspector-winbox-vulnerability-screen.png)

## 恶意活动溯源

由于有多个恶意活动同时运行，因此很难对攻击者进行追溯。实际上，对这一系列恶意活动的溯源过程是一场噩梦，因为易受攻击的路由器被不同的恶意活动一遍又一遍的利用，所以这些路由器上就存在一个又一个恶意活动的运行痕迹。然而，我们仍然在密切关注一个疑似攻击者发起的特定活动。截至目前，我们暂时没有得出明确的结论，请继续关注我们接下来的更新。

## 被感染用户的清除方法

![](https://blog.avast.com/hs-fs/hubfs/security-reminder-warning-screen.png?t=1539979341325&width=1012&name=security-reminder-warning-screen.png)

尽管该漏洞源于路由器，但由于MikroTik及时发出了补丁和通告，因此不应该将被感染的责任归咎于他们。在这里，最主要的问题在于大部分用户都没有及时安装补丁。如果用户受到感染，可以采用以下步骤：

1、检查自己是否使用了MikroTik路由器。即使用户没有使用MikroTik路由器，也可能会受到这一漏洞的影响。如果确认没有使用，那么证明可能是ISP（互联网服务提供商）受到感染。如果是这种情况，请立即与ISP取得联系，以便让他们尽快解决这一问题。

2、确认是否能够使用WinBox、TELNET或SSH，从内部网络连接到路由器。

3、如果无法通过上述任一端口连接，请尝试使用攻击者的备用端口。针对TELNET和SSH，分别被修改为TCP/10023和TCP/10022端口。

4、如果仍然无法连接，唯一的方法是将路由器恢复出厂设置。在重置后，立即对固件进行更新。在此之后，如果再次进行重置，那么所有默认设置都保证是安全的，因为最新版本的MikroTik路由器默认已经关闭了外部对路由器的访问。MikroTik发表过一篇非常不错的文章（
<https://blog.mikrotik.com/security/winbox-vulnerability.html>
），我们可以按照文章中的描述，或者通过WinBox应用程序中的Quick Set选项来安装最新的固件，并设置一个新的密码，这一过程比较简单。

![](https://blog.avast.com/hs-fs/hubfs/quick-set-option-in-winbox-app.png?t=1539979341325&width=600&name=quick-set-option-in-winbox-app.png)

5、如果已经成功连接到路由器，首先需要关闭外部对路由器接口的访问。

6、随后，查看路由器中是否存在任何文末IoC中记录的脚本/文件/用户名/PPP挑战口令或计划任务。如果存在，则删除相应内容。借助调度程序，这些任务可以重新运行，导致路由器再次沦陷。

7、禁用Web代理和SOCKS（如果不需要），或检查其配置是否符合安全要求，同时检查防火墙规则是否符合安全要求。

8、在工具菜单中，检查数据包嗅探器（Packet Sniffer）。

9、如果不需要使用PPTP服务器功能，请关闭。

10、检查所有用户账户，删除其中的可疑账户，并为所有启用的账户设置强密码。

11、将路由器的固件更新到最新版本。

## IOC

域名：

gazanew.com

mining711.com

srcip.com

src-ips.com

srcips.com

hostingcloud.science

meaghan.pythonanywhere.com

计划任务名称：

DDNS

CrtDDNS

UpDDNS

Setschedule[1-9]_

upd[113-116]

system[111-114]

ip

a

u[3-6]

与恶意活动相关的用户账户：

toto

dodo

路由器上的恶意文件：

i113.rsc

i114.rsc

I116.rsc

exsvc.rsc

本文翻译自avast.com [原文链接](https://blog.avast.com/mikrotik-routers-targeted-by-cryptomining-campaign-avast)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **P!chu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/162495](/post/id/162495)

安全客 - 有思想的安全新媒体

本文转载自: [avast.com](https://blog.avast.com/mikrotik-routers-targeted-by-cryptomining-campaign-avast)

如若转载,请注明出处： <https://blog.avast.com/mikrotik-routers-targeted-by-cryptomining-campaign-avast>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [挖矿](/tag/挖矿)
  * [路由器](/tag/路由器)

 **+1** __8赞

 __收藏

![](https://p3.ssl.qhimg.com/t01bd1dba67fe13cdc6.png) P!chu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

