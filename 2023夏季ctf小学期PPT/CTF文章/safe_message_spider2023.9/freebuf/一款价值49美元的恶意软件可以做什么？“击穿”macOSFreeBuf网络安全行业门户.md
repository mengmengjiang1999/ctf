网络犯罪分子对一款针对Windows系统的著名恶意软件进行了编码修改，并将其改造成了一款新型的信息窃取型恶意软件——XLoader。

> 值得一提的是， **XLoader这个恶意软件变种不仅能够攻击Windows系统，而且还可以针对macOS系统执行信息窃取任务** 。

XLoader目前在一个暗网地下论坛中以“僵尸网络加载服务” ( MaaS
)的形式提供给网络犯罪分子使用。由于该恶意软件不仅便宜，而且很简单，傻瓜模式的操作使得其在竞争恶意软件中脱颖而出。

![](https://image.3001.net/images/20210722/1626928290_60f8f4a2c35e5480c81f3.jpg!small)

XLoader可以从网络浏览器和一些电子邮件客户端（Chrome、Firefox、Opera、Edge、IE、Outlook、Thunderbird、Foxmail）中恢复并窃取密码

## 从不起眼的键盘记录器到炙手可热的恶意软件

 **XLoader的前身是针对Windows系统的信息窃取型恶意软件——Formbook**
，这款恶意软件从去年2月份开始一直活跃至今，它也被认为是一款无依赖的跨平台僵尸网络，并且同时支持Windows系统和macOS系统。

![CPR-Formbook-victims-figure-1.png](https://image.3001.net/images/20210722/1626937561_60f918d9282301bbe72d0.png!small)

受害者通过包含恶意 Microsoft Office 文档的欺骗性电子邮件被诱骗下载 XLoader

安全社区的一名研究人员在对XLoader进行了逆向工程分析，并且发现它与Formbook具有相同的可执行文件后，确认了这两个恶意软件之间的联系。

地下论坛的XLoader恶意软件推广人员解释称， **Formbook的开发人员为创建XLoader做出了很大贡献**
，这两个恶意软件具有相似的功能，其中包括窃取登录凭据、捕捉屏幕截图、记录键盘击键信息和执行恶意文件等。

![](https://image.3001.net/images/20210722/1626928299_60f8f4ab851bd37050b5c.jpg!small)

据了解，每一个客户可以以49美元（一个月）的价格租用macOS恶意软件版本，并可以访问卖家提供的服务器。通过维护一个中心化的命令和控制基础设施，攻击者将能够控制客户端使用恶意软件的方式。

而XLoader的Windows版本则更贵，运营商给出的套餐价格为59美元（一个月）和129美元（三个月）。

正如地下论坛广告中所提到的那样，XLoader的制造商还免费提供了一个Java绑定器，允许客户使用Mach-O和EXE二进制文件创建一个独立的JAR文件。

![](https://image.3001.net/images/20210722/1626928309_60f8f4b576bf8a654af63.jpg!small)

## 全球范围内传播，低成本的“威胁”

CheckPoint的恶意软件研究人员对XLoader进行了长达六个月的跟踪分析，截止至6月1日，他总共发现了来自69个国家的请求，表明XLoader在全球范围内的传播非常广泛，而且有超过一半的受害者位于美国地区。

虽然Formbook现在已经不在地下论坛打广告了，但它所能带来的威胁仍不容小觑。在过去的三年里，它是至少参与了1000个恶意软件的攻击活动，根据AnyRun提供的恶意软件趋势分析报告，这款信息窃取型恶意软件在过去的12个月内排名第四，影响仅次于Emotet。

 **如果说Formbook的流行是一个起点的话，那么XLoader可能会更流行，因为它针对的是消费者使用的两种最流行的操作系统。**

CheckPoint的研究人员表示，XLoader的隐蔽性足以让普通的非技术用户很难发现它。

## 安全建议

macOS的日益普及使它越来越受到网络犯罪分子的关注了，而macOS目前也已经成为了网络犯罪分子眼中极具吸引力的目标之一。

虽然Windows和MacOS恶意软件之间可能存在差距，但随着时间的推移，这种差距正在慢慢缩小。研究人员也认为，将来会有越来越多针对macOS系统的恶意软件诞生，而现有的恶意软件也会逐步将macOS系统添加到自己受支持的操作系统列表中。

最后，研究人员建议广大用户使用macOS的Autorun检查操作系统中的用户名，并查看LaunchAgents目录[/Users/[username]/Library/LaunchAgents]，然后删除包含可疑文件名的内容。

## 参考

> [bleepingcomputer](https://www.bleepingcomputer.com/news/security/xloader-> malware-steals-logins-from-macos-and-windows-systems/)
>
> [threatpost](https://threatpost.com/macos-49-xloader-data-stealer/167971/)

