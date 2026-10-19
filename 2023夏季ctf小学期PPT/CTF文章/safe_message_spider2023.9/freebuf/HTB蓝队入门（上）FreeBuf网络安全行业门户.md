## **前言**

HTB是大三时期一直想氪的一个平台，比较适合做一个方向上的深入学习。可惜大学生太穷了，只能工作后找个小伙伴AA，勉强付起这个昂贵的VIP。蓝队系列是我第一个开始学习（复习）的模块，需要好好记录下～也给想练HTB，但英语不好的同学一点帮助。

##  **Chase-easy**

简介：One of our web servers triggered an AV alert, but none of the sysadmins say
they were logged onto it. We've taken a network capture before shutting the
server down to take a clone of the disk. Can you take a look at the PCAP and
see if anything is up?

大概翻译就是：我们的一台web服务器触发了AV警告，但没有一个管理员表示他们曾经登陆过。在关闭服务器以克隆磁盘之前，我们已经进行了网络捕获。让我看看PCAP的数据包，究竟被黑客打到了什么程度。

题目是给到的一个数据包，不得不吐槽的就是找了半天密码，原来就写我脸上了。。

![image-20220306172238970.png](https://image.3001.net/images/20220323/1648025892_623ae1242678db8bef52f.png!small)

压缩包解压之后是一个PCAP的文件，拿到包前先statistics-》Capture File
Properties看下数据包大小、截取时间、操作系统等等基本信息，如果单纯是CTF的话帮助或许不大，但是在蓝军视角，获取更多的数据会更有助于我们定位问题。

![image-20220306172307202.png](https://image.3001.net/images/20220323/1648025895_623ae12766656783b36f4.png!small)

数据包基本上是22.22.22.7与22.22.22.5通信，且量不大，很容易看到5号机器通过一个HTTP GET请求获取7号机器上的nc64.exe。

![image-20220306172324566.png](https://image.3001.net/images/20220323/1648025898_623ae12a5e24a27c07231.png!small)

作为一个完整的攻击事件来说，这个显然不是入口。作为一般的应急响应事件来说，捕获到攻击情报的时候，很有可能已经达到内网，所以很有可能七号机器在此之前已经沦陷了，我们只能通过反推的方式去一层层的寻找最初的脆弱点（此题7号机不需要我们做溯源）。尝试筛选一下HTTP的请求，使用follow对HTTP流进行追踪。

![image-20220306172345052.png](https://image.3001.net/images/20220323/1648025900_623ae12c90039cfd0197d.png!small)

很清晰的还原出7号机器通过5号机器的一个上传点，实现了文件上传漏洞，上传后的文件为/cmd.aspx，并且通过远程命令执行的方式，从7号机器获取nc64.exe，进而执行持久化控制。

![image-20220306172414907.png](https://image.3001.net/images/20220323/1648025904_623ae130469951d55f13d.png!small)

![image-20220306172429007.png](https://image.3001.net/images/20220323/1648025906_623ae132be3ec3c5bb186.png!small)

从上面对5号机器进行的命令执行中，可以看到到反弹shell的端口在七号机的4444端口，所以我们可以通过tcp.port ==
4444的方式，查看七号机器远程执行了什么命令。

![image-20220306172442274.png](https://image.3001.net/images/20220323/1648025907_623ae133da5731af7df8a.png!small)

前面“象征性”执行了whoami、ipconfig，到这步又从7号机拉取了一个名字很长的文件，感觉很可疑，就看一下吧，这里用过滤字符串的功能进行查看，提示“Hey
there”，应该是Flag无误了。

![image-20220306172458571.png](https://image.3001.net/images/20220323/1648025909_623ae1352a7c51696ea85.png!small)

![image-20220306172511608.png](https://image.3001.net/images/20220323/1648025910_623ae136cffa8cdde03af.png!small)

##  **Event Horizon**

简介：Our CEO's computer was compromised in a phishing attack. The attackers took
care to clear the PowerShell logs, so we don't know what they executed. Can
you help us?

大致翻译：我们CEO的电脑在一次网络钓鱼中被攻击。攻击者小心地清理PowerShell日志，所以我们不知道他们执行了什么。大佬帮帮我们。

考点在于日志分析，题目给到的日志文件就高达323个

![image-20220306204459707.png](https://image.3001.net/images/20220323/1648025912_623ae138699e6d09f90c9.png!small)

这里用的日志分析工具是Event Log
Explorer,图形界面看起来非常的清晰。日志分析中排查优先级最高的，不出意外应该是powershell，但Windows
Powershell的日志已经被攻击者删掉了。排序了下文件大小，发现还有个"Microsoft-Windows-PowerShell%4Operational"，该日志会记录攻击者执行的Powershell命令都记录下来，把该日志放到工具里进行查看，在执行的第一个脚本注释处找到flag。

![image-20220306205220162.png](https://image.3001.net/images/20220323/1648025916_623ae13c35cd180eeeb67.png!small)

关于PowerShell5.0新功能的更多描述可以看这里：<https://docs.microsoft.com/zh-tw/powershell/scripting/windows-powershell/whats-new/what-s-new-in-windows-powershell-50?view=powershell-7.2>

##  **Export**

简介：We spotted a suspicious connection to one of our servers, and immediately
took a memory dump. Can you figure out what the attackers were up to?

大概翻译：我们发现一个可疑的连接在我们的服务器上，并且很快进行内存存储，你能发现攻击者在干嘛吗？

题目是给的一个Raw文件，众所周知常见的内存文件格式有dmp、raw、img等等，既然跟内存文件有关就离不开做内存取证。这里推荐一个开源的内存取证框架
<https://github.com/volatilityfoundation/volatility>，以及对新手非常友好的autovolatility：<https://github.com/carlospolop/autoVolatility>前者可以对数十个接口进行内存取证，后者可以批量将所有的接口进行取证并输出文件到本地。

![image-20220308012336301.png](https://image.3001.net/images/20220323/1648025925_623ae1454ebc87dd315c5.png!small)

跑完上述命令，可以获取到进程列表、事件日志、设备树、剪贴板内容、命令行等等信息

![image-20220308012418411.png](https://image.3001.net/images/20220323/1648025927_623ae147b9e74f7196536.png!small)

题目提到可疑链接，第一反应就是去看cmdline和cmdscan，前者显示进程的命令行参数，后者显示命令行的历史记录。在cmdscan文件里找到攻击者曾经执行过的一段Powershell无文件落地攻击![image-20220308012444395.png](https://image.3001.net/images/20220323/1648025930_623ae14a1b4d8a1ca151c.png!small)

链接过一下URL的解码，ps1文件的名称感觉有点像flag了，再过一下Base64解密拿到flag。

![image-20220308012738853.png](https://image.3001.net/images/20220323/1648025931_623ae14b453d9d20e4927.png!small)

##  **Insider**

简介：A potential insider threat has been reported, and we need to find out what
they accessed. Can you help?

大概翻译：一个潜在的威胁被爆出，我们需要知道他们访问了什么，你能帮忙吗？

给到的是客户端上火狐浏览器的一些文件，尝试查一下如何读取火狐浏览器配置文件，寄了。。全网无资料。国外的师傅提到了一款工具
**firefox_decrypt**
，地址：<https://github.com/unode/firefox_decrypt>。可以从Mozilla配置文件中提取密码，这种方法倒是很适合红队的同学在拿到靶标后使用，后面就是抄作业的过程：

![image-20220306230328950.png](https://image.3001.net/images/20220323/1648025932_623ae14c54b3f0baafcd5.png!small)

好了作业抄完，再回顾下firefox_decrypt工具大概的实现原理，我们的用户记住密码后，数据一般都是放在本地，如果没有主密码的保护，这些密码应该是可以暴露出来的，所以firefox_decrypt就是对没有正确配置的本地密码进行读取（没理解错的话）。

##  **Intel**

简介：It seems a huge trove of credit card details is being sold by a group going
by the name flinchsec. Can you find any sites or artefacts associated with
this group that we can use to detect them?

大概翻译：看起来有一个叫 flinchsec的团伙正在售卖大量的信用卡详细信息，你能找到任何与这个团队关联的网站或文件，以至于我们可以使用来检测他们吗？

一道社工类型的题目。给的信息不多，我们只知道团队名叫flinchsec，谷歌搜索一下，在领英找到了这个团队![image-20220306212607968.png](https://image.3001.net/images/20220323/1648025933_623ae14dceee960c5d9b5.png!small)

但是点击公司网站，返回了500，说明网站已经下掉了。但是如果我还想看到的话怎么办呢，想到了类似于网页快照之类的应用，百度查了一下有相关的实现：Wayback
machine。并且在页面上看到有一个github的链接

![image-20220306214725054.png](https://image.3001.net/images/20220323/1648025936_623ae1503f0aa9f860f29.png!small)

![image-20220306214831672.png](https://image.3001.net/images/20220323/1648025940_623ae154a977c46a549d3.png!small)

到Releases下载文件后，strings命令看下程序里有没有flag的明文字符，结果失败了。后面看了大佬发的WP，竟然要用VT去查，脑洞太大了。。。

![image-20220306222901343.png](https://image.3001.net/images/20220323/1648025941_623ae155bc8dafd8a9b18.png!small)

![image-20220306223034353.png](https://image.3001.net/images/20220323/1648025942_623ae156de9d5a95b163b.png!small)

 **实验推荐**

 **实验：内存镜像取证**
**[点击进入实操>>﻿](https://www.yijinglab.com/expc.do?ec=ECID6a2f-ed6f-4f85-9363-731535a5c3c4)**

 **更多网安工具及学习资料，扫码免费领：**

![](https://image.3001.net/images/20220316/1647401226_6231590a179e079268478.png!small)

  

