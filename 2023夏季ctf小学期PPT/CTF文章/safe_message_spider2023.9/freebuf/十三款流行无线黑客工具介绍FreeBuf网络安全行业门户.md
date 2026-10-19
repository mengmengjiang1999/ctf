**在本文中，我将讨论无线网络的安全和最佳的WiFi密码破解或恢复工具。我将解释无线网络使用的加密类型以及这些工具如何破解网络以获取访问权限。我们还将看到哪些工具可以让用户监控网络。**

**![96870_1a8b_5.jpg](https://image.3001.net/images/20190218/15504779372140.jpg!small)**

## 无线网络和黑客

无线网络基于由IEEE（电气和电子工程师协会）定义的用于ad hoc网络或基础设施网络的IEEE
802.11标准。基础设施网络具有一个或多个接入点，用于协调节点之间的流量。但在ad hoc网络中，没有接入点，每个节点以点对点的方式连接。

基本上有两种类型的漏洞可以在无线局域网中找到。一种是由于配置不当导致的，另一种是由于加密不当导致的。配置不当是由管理网络的网络管理员引起的。它可能包括弱密码，无安全设置，默认配置的使用以及其他与用户相关的事物。加密不当与用于保护无线网络的安全密钥有关，通常是由于WEP或WPA中的问题导致。

## WEP和WPA

WEP和WPA是WiFi
LAN中使用的两种主要的安全协议。WEP称为有线等效保密，它是一种被弃用的安全协议，于1997年作为原始802.11标准的一部分引入，但它很弱，在协议中发现了几个严重的弱点。现在，这可以在几分钟内被破解。因此，2003年引入了一种新的安全协议，这种协议称为WiFi加护访问（WPA）。它主要有两个版本，WPA和WPA2。现在它是无线网络中通常使用的协议。要获得对网络的未授权访问，需要破解这些安全协议。有许多工具可以破解WiFi加密。这些工具既可以利用WEP的弱点，还可以对WPA
/ WPA2进行暴力破解。

基本上无线黑客工具有两种类型。其中一个可用于嗅探网络并监控网络中发生的情况。其它类型的工具用于破解WEP
/WPA密钥。这些是用于无线密码破解和网络故障排出的常用工具。

## 1.Aircrack

Aircrack是最受欢迎的无线密码破解工具之一，可用于802.11a / b / g
WEP和WPA破解。Aircrack使用的算法是通过捕获数据包来恢复无线密码。收集到足够的数据包后，它会尝试恢复密码。为了使攻击更快，它通过一些优化实现标准的FMS攻击。

该工具背后的公司还提供一个在线教程，您可以在其中学习如何安装和使用此工具来破解无线密码。它来自Linux发行版，并提供Live
CD和VMWare镜像选项。您可以使用其中任何一种。它支持大多数无线适配器，基本都保证可以使用。如果您使用的是Linux发行版，该工具唯一缺点就是它需要了解Linux的知识。如果你对Linux不熟悉，你会发现很难使用这个工具。在这种情况下，请尝试Live
CD或VMWare镜像，VMWare镜像需要较少的准备知识，但它仅适用于一组有限的主机操作系统，并且需要支持USB设备。

在开始使用此功能之前，请确认无线网卡可以注入数据包，然后再开始WEP破解。阅读网上的在线教程，了解更多有关该工具的信息。

下载地址：[Aircrack-ng](http://www.aircrack-ng.org/)

## 2.AirSnort

Airsnort是另一种在WiFi
802.11b网络上解密WEP加密的工具，它是一个免费工具，支持Linux和Windows平台。虽然此工具已经不再维护，但是仍然可以从Sourceforge下载。一旦收集到足够的数据包，AirSnort就会通过被动监控传输和计算加密密钥来工作，该工具易于使用，如果您有兴趣，可以尝试使用此工具破解WEP密码。

下载地址：[AirSnort](https://sourceforge.net/projects/airsnort/)

## 3.Cain & Able

Cain &
Able是一种流行的密码破解工具。开发此工具是为了拦截网络流量，然后通过使用密码分析再进行暴力破解密码，它还可以通过分析路由协议来恢复无线网络密钥。如果你正在尝试学习无线安全和密码破解，你应该尝试这个工具。

下载地址：[Cain & Able](http://www.oxid.it/cain.html)

## 4.Kismet

Kismet是WiFi 802.11 a / b / g / n layer2无线网络嗅探器和IDS。它适用于支持RF-mon模式的任何无线网卡，它被动地收集数据包以识别网络并检测隐藏的网络。它建立在C/S模块化架构之上，适用于Linux、OSX、Windows和BSD平台。

下载地址： [Kismet](http://www.kismetwireless.net/)

## 5.NetStumbler

NetStumbler是一种流行的Windows工具，用于查找开放式无线接入点，此工具是免费的，支持Windows。该工具还存在精简版MiniStumbler。

基本上，NetStumbler用于入侵，验证网络配置，查找网络较差的位置，检测未经授权的接入等。

但该工具也有很大的劣势，大多数可用的无线入侵检测系统都可以轻松的检测到它，这是因为它主动探测网络以收集有用的信息。该工具的另一个缺点就是它无法正常工作在最新的64位Windows操作系统上，这是因为该工具最后一次更新于2011。

下载地址：[NetStumbler](http://www.stumbler.net/)

## 6.inSSIDer

inSSIDer是适用于Windows和OSX操作系统的流行WiFi扫描工具。最初工具是开源的，后来工具进行收费，现在售价将近20美元。它还被授予“最佳网络开源软件”。inSSIDer
WiFi扫描器可以执行各种任务，包括查找开发的WiFi接入点，跟踪信号强度以及使用GPS记录保存日志等。

下载地址：[inSSIDer](https://www.metageek.com/products/inssider/)

## 7.WireShark

WireShark是网络协议分析器，它可以让您检查网络中发生的情况，您可以实时捕获数据包并进行分析。它捕获数据包并允许您在微观级别检查数据，它可以在Windows、Linux、OS
X、Solaries、FreeBSD等上运行。WireShark需要很好的网络协议知识来分析使用该工具获得的数据。如果您对此不了解，可能会觉得这个工具并不有趣。因此，只有在确定自己的协议知识时才能进行尝试。

下载地址：[WireShark](https://www.wireshark.org/)

## 8.CoWPAtty

CoWPAtty是WPA-PSK的自动字典攻击工具，它运行在Linux上，该程序具有命令行界面，并使用字典进行密码攻击。

使用该工具非常简单，但速度很慢，因为使用的哈希是带有SSID的SHA1，这意味着相同的密码将具有不同的SSIM。因此，您不能简单地对所有接入点使用彩虹表。该工具使用密码字典，并使用SSID为字典中包含的每个关键字进行攻击。

该工具的新版本试图通过使用预先计算的哈希文件来提高速度，这个预先计算的文件包含大约17000个字典文件，用于大约1000个最受欢迎的SSID。但是如果您的SSID不在那1000个中，就很不走运了。

下载地址：[CoWPAtty](https://sourceforge.net/projects/cowpatty/)

## 9.Airjack

Airjack是一种WiFi 802.11数据包注入工具。这种无线破解工具在注入伪造数据包和通过拒绝服务攻击使网络崩溃时非常有用。此工具还可用于中间人攻击。

下载地址：[Airjack](https://sourceforge.net/projects/airjack/)

## 10.WepAttack

WepAttack是一个用于破解802.11
WEP密钥的开源Linux工具，此工具通过测试数百万个关键字来查找密钥执行自动字典攻击。只需要一张可用的无线网卡即可配合WepAttack使用。

下载地址：[WepAttack](http://wepattack.sourceforge.net/)

## 11.OmniPeek

OmniPeek是另一种不错的数据包嗅探器和网络分析工具，此工具是商业版，仅支持Windows操作系统。此工具用于捕获和分析无线流量，但它要求您具备良好的协议知识才能理解内容。有一个好处是该工具可与市场上的大多数网卡配合使用。这款工具用于网络故障排除，还支持扩展插件，并且已经有40多个插件可以扩展该工具的功能。

下载地址：[OmniPeek](https://www.liveaction.com/products/omnipeek/)

## 12.CommView for WiFi

CommView for WiFi是另一种流行的无线网络监视器和数据包分析工具，它带有易于理解的GUI，适用于802.11 a / b / g / n /
ac网络。它捕获每个数据包并以列表的形式显示有用的信息。您可以获得有用的信息，如接入点、站点、信号强度、网络连接和协议分配。

捕获的数据包通过由用户自定义的WEP/WPA密钥进行解密。

该工具主要面向希望监控其WiFi流量的网络管理员、安全人员和家庭用户以及致力于无线网络软件的开发人员。

下载地址： [CommView for WiFi](https://www.tamos.com/products/commwifi/)

## 13.CloudCracker

CloudCracker是用于破解受WPA保护的WiFi网络的在线密码破解工具，此工具还可用于破解不同的密码哈希，只需要上传握手文件，输入网络名称并启动该工具即可。这个工具有一个大约3亿字的字典来执行攻击。

CloudCracker：<https://crack.sh/>

 ***参考来源：[infosecinstitute](https://resources.infosecinstitute.com/13-popular-wireless-hacking-tools/)，本文由大学新生Bai编译，各位大佬非喜误喷，转载请注明来自FreeBuf.COM**

