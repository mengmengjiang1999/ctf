## 一、正常报文排查

 **一次抓包，可能会有几万个报文，熟练地使用过滤功能，可以快速定位到需要分析的内容。在这里过滤http报文，直接对http报文进行分析。**

### 1.1查看请求包

第一个http是访问<http://www.msftncsi.com/ncsi.txt>。

![](https://image.3001.net/images/20200525/1590389804_5ecb6c2c61681.png!small)

由于无法判断URL的安全性，可以根据URL查询威胁情报库，看看是否为恶意URL。根据云沙箱分析为安全。基本可以判断是安全的网站。

![](https://image.3001.net/images/20200525/1590389828_5ecb6c449239b.png!small)

### 1.2查看返回包

也可以查看返回包的报文，通过返回结果判断。这个报文返回的只有一句Microsoft NCSI，不像是恶意网站。

![](https://image.3001.net/images/20200525/1590389844_5ecb6c547ee19.png!small)

直接访问网站，网页也确实只有一句话。该操作建议在沙箱环境执行，以免连接到恶意网站。

![](https://image.3001.net/images/20200525/1590389852_5ecb6c5c414db.png!small)

### 1.3借助网络知识库排查

一个人的知识是有限，因此我们需要借助网络的力量，如百度等；通过在网上查询，可发现该网站是微软用来测试网络连接情况的，证明其为安全的访问。

![](https://image.3001.net/images/20200525/1590391581_5ecb731dbb075.png!small)

## 二、可疑文件传输报文排查

由于我们是要对病毒入侵进行分析，应该先从包含文件传输的报文开始。因此可直接看由外网进入内网的报文，查找包含文件传输的报文。

### 2.1文件传输报文

通过排查发现第一个文件传输报文，报文中包含了一个2018_11Details_zur_Transaktion.doc文件

![](https://image.3001.net/images/20200525/1590392595_5ecb7713e11d3.png!small)

### 2.2 查看请求包

查看对应的请求包，发现文件下载的URL:<http://ifcingenieria.cl/QpX8It/BIZ/Firmenkunden/>

![](https://image.3001.net/images/20200525/1590392608_5ecb77205df73.png!small)

根据访问地址，暂时无法判断是否为恶意网站。在这里可以借助URL威胁情报库确定。根据云沙箱分析该URL是可疑网站。

![](https://image.3001.net/images/20200525/1590392620_5ecb772c4d9fe.png!small)

### 2.3导出文件

可以直接在文件传输包中使用导出分级字节流的功能导出报文中的文件。

![](https://image.3001.net/images/20200525/1590389917_5ecb6c9db8075.png!small)

### 2.4分析文件

把导出的文件放到云沙箱上进行检测。发现文件为恶意文件Firmenkunden。

![](https://image.3001.net/images/20200525/1590389929_5ecb6ca9dd6ee.png!small)

阅读检测结果，分析恶意文件的行为。

![](https://image.3001.net/images/20200525/1590389937_5ecb6cb193807.png!small)

在检测报告中的低危行为中可以发现存在网络相关的行为，该恶意文件会访问timlinger.com（IP：216.37.42.32）。因此，可以通过流量包中是否包含与该地址的连接来判定恶意文件是否已经运行。

![](https://image.3001.net/images/20200525/1590389950_5ecb6cbe85fdf.png!small)

![](https://image.3001.net/images/20200525/1590389970_5ecb6cd276689.png!small)

![](https://image.3001.net/images/20200525/1590389977_5ecb6cd9c1b52.png!small)

### 2.5根据网络行为分析是否执行成功

继续分析流量包，在流量包中可以发现与216.37.42.32的通信，可以断定该恶意文件已经运行。

![](https://image.3001.net/images/20200525/1590389991_5ecb6ce78c14b.png!small)

查看通信内容，发现恶意文件Firmenkunden访问timlinger.com，与云沙箱的分析报告中的网络行为一致。

![](https://image.3001.net/images/20200525/1590390000_5ecb6cf0b8a6a.png!small)

## 三、第二个可疑文件

由访问timlinger.com的返回包可知，下载了另一个文件6169583.exe

![](https://image.3001.net/images/20200525/1590390011_5ecb6cfbe2bd0.png!small)

### 3.1分析文件

把文件导出，然后放到云沙箱检测。该文件为恶意文件。

![](https://image.3001.net/images/20200525/1590390026_5ecb6d0a59e8d.png!small)

由威胁情报可知，该恶意文件也会访问一些IP地址。

![](https://image.3001.net/images/20200525/1590390032_5ecb6d10de9fc.png!small)

### 3.2根据网络行为分析是否执行成功

发现与24.206.17.102的网络通信

![](https://image.3001.net/images/20200525/1590390042_5ecb6d1aacb26.png!small)

发现与67.43.253.189的网络通信

![](https://image.3001.net/images/20200525/1590390050_5ecb6d226d643.png!small)

通过其网络行为可知，文件已经被执行。

### 3.3使用追踪流查看完整对话

使用追踪流进行http报文分析

![](https://image.3001.net/images/20200525/1590390058_5ecb6d2a98b89.png!small)

这个返回包都是乱文，本人技术有限，就不分析了。

![](https://image.3001.net/images/20200525/1590390070_5ecb6d3614af8.png!small)

## 四、防御手段

### 4.1确实受攻击的范围

通过查看网络通信情况确认范围，把存在病毒网络行为的计算机列为受攻击的计算机。

### 4.2遏制病毒扩散

把受攻击的计算机断网，防止病毒进一步传播。

### 4.3清除病毒

使用防病毒软件对受害主机进行全盘扫描。确保清除下载的恶意文件（2018_11Details_zur_Transaktion.doc、6169583.exe），以及下载后释放的文件（473.exe、nirmalacolorer.exe等）、删除服务nirmalacolorer。

### 4.4预防

> (1)安装防病毒软件，及时更新。
>
> (2)使用防病毒安全网关，防止病毒进入内网。
>
> (3)在防火墙上设置网络策略，禁止与病毒相关的IP进行通信。
>
> (4)安全教育，提高员工的网络安全意识，不要随意点击来路不明的网址等。

## 五、总结

本文主要讲述针对流量包的分析，一些简单的Wireshark使用技巧：过滤、文件导出、追踪流，以及威胁情报的解读。

## 六、参考

> Win 7 NCSI判断机制：[https://answers.microsoft.com/zh-> hans/windows/forum/windows_7-networking/win-7-ncsi%E5%88%A4%E6%96%AD%E6%9C%BA%E5%88%B6/ff8e279a-5f08-4279-ad20-7a47fd89f977](https://www.freebuf.com/wp-> admin/post.php?post=237631&action=edit)
>
> 微步云沙箱分析报告-> Firmenkunden：[https://s.threatbook.cn/report/file/09ebe4229a74cdb1212671e6391742cc6bee387bf14da02974b07857b27f9223/?sign=history&env=win7_sp1_enx86_office2013](https://s.threatbook.cn/report/file/09ebe4229a74cdb1212671e6391742cc6bee387bf14da02974b07857b27f9223/?sign=history&env=win7_sp1_enx86_office2013)
>
> 微步云沙箱分析报告-> 6169583.exe：[https://s.threatbook.cn/report/file/69e731afb5f27668b3a77e19a15e62cce84e623404077a8563fcf61450d8b741/?sign=history&env=win7_sp1_enx86_office2013](https://www.freebuf.com/wp-> admin/post.php?post=237631&action=edit)

 ***本文作者：GalaxyLu，转载请注明来自FreeBuf.COM**

