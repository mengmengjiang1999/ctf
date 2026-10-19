**近两年来，Shlayer木马一直是Mac OS平台上最常见的恶意软件，十分之一的Mac
OS用户受到它的攻击，占该操作系统检测到攻击行为的30%。第一批样本发现于2018年2月，此后收集了近32000个不同的木马恶意样本，并确定了143个C
&C服务器。**

![](https://image.3001.net/images/20200218/1581987922_5e4b3852b801e.png!small)

自Shlayer首次被发现以来，其使用的算法几乎没有变化，活动行为保持平稳。

![](https://image.3001.net/images/20200218/1581988037_5e4b38c5afe51.png!small)

## 技术细节

从技术角度来看，Shlaye是一个相当普通的恶意软件。在所有变体中，只有最新的木马下载程序OSX.Shlayer.e与众不同。此恶意软件的变体是用Python编写的，其算法也有不同。具体分析如下（样本MD5：4d86ae25913374cfcb80a8d798b9016e）：

### 感染第一阶段

安装此DMG映像后，将提示用户运行“安装”文件，安装程序是Python脚本。

![](https://image.3001.net/images/20200218/1581988231_5e4b39875a490.png!small)

应用程序包内可执行文件目录包含两个Python脚本：GJPWVUUD847
DZQPYBI(main)和GoqWajdBuV6(auxiliary)。后者用来实现数据加密功能：

![](https://image.3001.net/images/20200218/1581988358_5e4b3a066e41b.png!small)

![](https://image.3001.net/images/20200218/1581988374_5e4b3a16153bc.png!small)

接下来，主脚本生成唯一用户和系统ID，收集macOS版本的信息。基于这些数据生成GET query参数，下载ZIP文件：

![](https://image.3001.net/images/20200218/1581988491_5e4b3a8bed6d5.png!small)

下载到/tmp/%（sessionID）目录的ZIP文件使用unzip函数解压到/tmp/tmp目录：

![](https://image.3001.net/images/20200218/1581988529_5e4b3ab1e4782.png!small)

ZIP包含可执行文件84cd5bba3870应用程序包：

![](https://image.3001.net/images/20200218/1581988595_5e4b3af3d3960.png!small)

解压文件后，python脚本使用chmod赋予文件84cd5bba3870在系统中运行的权限：

![](https://image.3001.net/images/20200218/1581988637_5e4b3b1d5598c.png!small)

样本使用moveIcon和findVolumePath函数将原始DMG图标复制到新下载的应用程序包所在的目录中：

![](https://image.3001.net/images/20200218/1581988694_5e4b3b56ec52b.png!small)

木马程序使用内置工具下载和解压，并删除下载的文件及其解压内容：

![](https://image.3001.net/images/20200218/1581988771_5e4b3ba335c1b.png!small)

### 感染第二阶段

Shlayer本身只执行攻击的初始阶段，穿透系统，加载payload运行。调查AdWare.OSX.Cimpli可以看出其对用户的负面影响。

Cimpli安装程序看起来无害，只是提供安装：

![](https://image.3001.net/images/20200218/1581989097_5e4b3ce97a068.png!small)

但实际上Cimpli执行用户看不到的操作。首先，它在Safari中安装一个恶意扩展，将操作系统安全通知隐藏在恶意软件伪造窗口后。单击通知中的按钮，用户就会同意安装扩展。

![](https://image.3001.net/images/20200218/1581989173_5e4b3d3515de8.png!small)

其中一个扩展名为ManagementMark，检测为非病毒：HEUR:AdWare.Script.SearchExt.gen。它监视用户搜索并将其重定向到地址hxxp://lkysearchex41343-a.akamaihd[.]net/as?q=c：

![](https://image.3001.net/images/20200218/1581989271_5e4b3d97640fe.png!small)

样本还加载PyInstaller打包的mitmdump工具。系统中添加了一个特殊的可信证书，允许mitmdump查看HTTPS流量，所有的用户流量被重定向到mitmdump的SOCKS5代理。

![](https://image.3001.net/images/20200218/1581990451_5e4b42335e355.png!small)

通过mitmdump（SearchSkilledData）的所有流量都由脚本SearchSkilledData.py（-s选项）处理：

![](https://image.3001.net/images/20200218/1581990514_5e4b42721e35c.png!small)

此脚本将所有用户搜索查询重定向到hxxp://lkysearchds3822-a.akamaihd[.]net。Cimpli并不是Shlayer唯一一个广告软件应用程序系列，还包括AdWare.OSX.Bnodlero、AdWare.OSX.Geonei和AdWare.OSX.Pirrit。

### 软件传播

恶意软件传播是其生命周期的重要组成部分，Shlayer为了解决这个问题制定了很多方案：在找你最喜欢的电视节目的最新一集吗？想看足球比赛的直播吗？要格外小心，因为感染Shlayer的几率很高。

![](https://image.3001.net/images/20200218/1581990754_5e4b4362aff34.png!small)

![](https://image.3001.net/images/20200218/1581990769_5e4b437132bdc.png!small)

![](https://image.3001.net/images/20200218/1581990891_5e4b43eb56938.png!small)

在大多数情况下广告登陆页面把用户带到精心制作的假页面，在Flash播放器更新提示下安装恶意软件。

![](https://image.3001.net/images/20200218/1581990957_5e4b442db3c67.png!small)

在YouTube视频描述中发现了指向恶意软件下载的链接：

![](https://image.3001.net/images/20200218/1581991003_5e4b445b08dfd.png!small)

文章脚注中的Shlayer：

![](https://image.3001.net/images/20200218/1581991046_5e4b4486dae8e.png!small)

根据WHOIS判断，它们属于同一个人，这样的域名总数已经超过700个。

统计数据显示，Shlayer攻击主要针对美国用户（31%），其次是德国（14%）、法国（10%）和英国（10%），几乎所有假冒的Flash
Player下载页面网站都有英语内容。

![](https://image.3001.net/images/20200218/1581991152_5e4b44f0ee21f.png!small)

## 总结

通过对Shlayer家族的研究可以得出结论，macOS平台是网络罪犯的一个很好的收入来源。木马链接甚至存在于合法的资源上，攻击者擅长于社会工程学，很难预测下一个欺骗技术会有多复杂。

## IOCS:

> 4d86ae25913374cfcb80a8d798b9016e
>
> fa124ed3905a9075517f497531779f92
>
> 594aa050742406db04a8e07b5d247cdd

Malicious links:

> hxxp://80.82.77.84/.dmg
>
> hxxp://sci-hub[.]tv
>
> hxxp://kodak-world[.]com

C&C Urls:

> hxxp://api.typicalarchive[.]com
>
> hxxp://api.entrycache[.]com
>
> hxxp://api.macsmoments[.]com

 ***参考来源：[securelist](https://securelist.com/shlayer-for-macos/95724/)，由Kriston编译，转载请注明来自FreeBuf.COM**

