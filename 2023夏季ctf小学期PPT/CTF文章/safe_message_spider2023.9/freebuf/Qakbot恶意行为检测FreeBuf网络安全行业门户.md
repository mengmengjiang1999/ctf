**Qakbot是一款窃取敏感信息的恶意软件，也被称为Qbot。该恶意软件家族已经活跃了多年，本文利用Wireshark分析Qakbot恶意流量数据包。了解分析这些流量模式对于检测和调查Qakbot至关重要。**

请注意，本教程中使用的是恶意软件的pcap流量包，应在非Windows环境中查看此pcap。如果是Windows计算机，建议安装Linux虚拟机查看pcap。

本文将包括以下内容：Qakbot传播方法、初始zip恶意附件、Qakbot
Windows可执行文件、感染后HTTPS的活动、其他感染后行为。本文使用的pcap[下载链接](https://www.malware-traffic-analysis.net/2020/01/29/index.html)，文件名为2020-01-29-Qbot-infection-traffic.pcap.zip，图1显示在Wireshark中打开的pcap。

![](https://image.3001.net/images/20200224/1582510799_5e5332cfaacce.png!small)

## Qakbot传播方式

Qakbot最常通过恶意垃圾邮件（malspam）传播，近期在2019年11月也通过漏洞传播。最近Qakbot基于恶意垃圾邮件攻击活动遵循图2流程。

![](https://image.3001.net/images/20200224/1582511129_5e533419409c0.png!small)

## 初始Zip恶意附件

最近Qakbot通过恶意垃圾电子邮件传播，示例如下：

![](https://image.3001.net/images/20200224/1582511263_5e53349f7b625.png!small)

电子邮件中的URL以简短的数字序列为结尾，后跟.zip。已检测到的url见表1。

![](https://image.3001.net/images/20200224/1582511420_5e53353cd646f.png!small)

在pcap中可以利用Wireshark过滤器，HTTP.request.uri contains.zip找到zip的HTTP请求，如图4所示。

![](https://image.3001.net/images/20200224/1582511497_5e533589076f5.png!small)

按照TCP stream查看zip，如图5和图6所示，然后从pcap导出zip存档，如图7所示。

![](https://image.3001.net/images/20200224/1582511556_5e5335c41e7d5.png!small)

![](https://image.3001.net/images/20200224/1582511570_5e5335d25ab9c.png!small)

![](https://image.3001.net/images/20200224/1582511588_5e5335e45cdfa.png!small)

在大多数情况下，File→Export
Objects→HTTP可导出zip文件。但如图8所示，无法导出名为9312.zip的文件，因为它被分成数百个较小的数据片段。

![](https://image.3001.net/images/20200224/1582511697_5e53365102615.png!small)

可以从TCP流窗口导出数据，并在十六进制编辑器中编辑二进制文件，步骤如下：查找9312.zip的TCP流、TCP流窗口中仅显示响应流量、将“Show and
save data
as”从ASCII更改为Raw、将数据保存为二进制文件、在十六进制编辑器中打开二进制文件，并删除‘PK’之前的HTTP请求头、将文件保存为zip、检查文件是否正确。

![](https://image.3001.net/images/20200224/1582511967_5e53375f86822.png!small)

![](https://image.3001.net/images/20200224/1582511983_5e53376f962d5.png!small)

![](https://image.3001.net/images/20200224/1582511997_5e53377d637d9.png!small)

上图显示了如何检查文件。zip文件中包含VBS文件，对提取的VBS文件分析表明，它会生成下一个与Qakbot相关的URL：Qakbot
Windows可执行文件。

## Qakbot Windows可执行文件

访问VBS文件生成的url会返回Qakbot
Windows可执行文件。自2019年12月以来，Qakbot可执行文件URL以44444.png或444444.png结尾，详情见表2。

![](https://image.3001.net/images/20200224/1582512324_5e5338c46078d.png!small)

在pcap中，使用Wireshark过滤器：hxxp.request.uri contains.png找到Qakbot可执行文件的HTTP
GET请求，如图15所示。

![](https://image.3001.net/images/20200224/1582512385_5e533901b14e5.png!small)

文件→导出对象→HTTP 从pcap导出此对象，并检查结果，如图17所示。

![](https://image.3001.net/images/20200224/1582512445_5e53393ded85f.png!small)

HTTPS活动

使用过滤器快速查看pcap中的web流量。找到Qakbot可执行文件alphaenergyeng[.]com的HTTP
GET请求。如图18所示，指向68.1.115[.]106的HTTPS或SSL/TLS流量。

![](https://image.3001.net/images/20200224/1582512608_5e5339e0041a7.png!small)

此流量为Qakbot异常证书颁发者数据，使用以下Wireshark检查Qakbot证书颁发者数据：Ip.addr eq
68.1.115.186和ssl.handshake.type eq 11

![](https://image.3001.net/images/20200224/1582512752_5e533a70e5849.png!small)

locality name,、organization name、common
name等通常在合法HTTPS、SSL或TLS通信的证书中找不到，发行人数据示例如下：

> id-at-countryName=ES
>
> id-at-stateOrProvinceName=IA
>
> id-at-localityName=Uorh Ofwa
>
> id-at-organizationName=Coejdut Mavmtko Qxyemk Dxsjie LLC.
>
> id-at-commonName=gaevietovp.mobi

## 其他行为

每个活动本身并不是恶意的，但是结合之前的发现可以拼凑出完整的Qakbot恶意行为。

Qakbot另一个特征是到cdn.speedof[.]me的HTTPS流量。在Qakbot感染的机器流量中经常看到与cdn.speedof[.]me通信的流量。

![](https://image.3001.net/images/20200224/1582513061_5e533ba58b9e4.png!small)

Qakbot还会从受感染的windows主机上打开所有浏览器。在沙盒（[测试视频回放](https://app.any.run/tasks/fb9cffb1-7797-4827-8446-05fee3d6a3de/)）中Qakbot在Windows
7打开Chrome、Firefox、Internet Explorer，具体访问以下地址：

> hxxp://store.nvprivateoffice[.]com/redir_chrome.html
>
> hxxp://store.nvprivateoffice[.]com/redir_ff.html
>
> hxxp://store.nvprivateoffice[.]com/redir_ie.html

域nvprivateoffice[.]com是2012年通过GoDaddy注册的，store.nvprivateoffice[.]com在Fedora服务器上显示nginx的默认网页。

本文测试环境中是未安装Chrome或Firefox的Windows 10主机，pcap只显示Internet Explorer和Microsoft
Edge的web流量，Qakbot生成的URL都是hxxp://store.nvprivateoffice[.]com/redir_ie.html。

查找此流量方式：http.request.full_uri contains store.nvprivateoffice

![](https://image.3001.net/images/20200224/1582513684_5e533e14db4d8.png!small)

头信息用户代理如下：

![](https://image.3001.net/images/20200224/1582513783_5e533e772a217.png!small)

受Qakbot感染主机流量中还有各种电子邮件协议（如SMTP、IMAP和POP3）的通信流量。如图25所示：

过滤条件：tcp.flags eq 0x0002 and !(tcp.port eq 80) and !(tcp.port eq 443)

![](https://image.3001.net/images/20200224/1582513873_5e533ed134105.png!small)

从上图可以看出其访问了25、110、143、465、587、993、995等email协议端口，前两行中显示与65400端口的通信流量应该也是email相关流量。

利用以下过滤条件进一步分析：smtp or imap or pop

![](https://image.3001.net/images/20200224/1582514064_5e533f9062391.png!small)

可以从中看到许多email相关未加密的通信流量。

## 总结

本文提供了检查Windows感染Qakbot的基本方法，更多Qakbot的恶意pcap包可以在[malware-traffic-analysis.net](https://www.malware-traffic-analysis.net/)上找到。

 ***参考来源：[unit42](https://unit42.paloaltonetworks.com/tutorial-qakbot-infection/)，由Kriston编译，转载请注明来自FreeBuf.COM**

