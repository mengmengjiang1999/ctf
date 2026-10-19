***本文原创作者：fish1983，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 0×1 事件描述

**小Z所在公司的信息安全建设还处于初期阶段，而且只有小Z新来的一个信息安全工程师，所以常常会碰到一些疑难问题。一天，小Z接到运维同事的反映，一台tomcat
的web服务器虽然安装了杀软，但是还是三天两头会出现杀软病毒报警，希望他能查下原因。**

小Z首先设想了三种可能性:

> 1.存在系统漏洞
>
> 2.由于前期运维在服务器上装了一些工具软件，会不会工具软件引入的病毒
>
> 3.应用层漏洞。

于是，他从这三方面开始了调查。

首先，小Z用更新库的漏扫对系统层面的漏洞检测，未发现任何异常；由于会有开发连接进这台服务器，他去开发那里收集工具软件进行查毒处理，也没发现异常，排除通过软件带入病毒的可能；那难道是通过应用层漏洞进来的？因为系统上线前都会经过web渗透测试，文件上传，SQL注入等常规漏洞已经修复，虽然这样，小Z还是重新验证了一遍漏洞，没有问题，又用D盾webshell检测工具进行了扫面，未发现任何webshell。

那病毒是怎么产生的？

## 0×2 溯源准备

由于病毒无法清干净，也不清楚黑客是已经在机器上做了哪些手脚，业务方要求小Z重新搭建一个干净的环境，给系统打好最新的补丁，交给开发重新放入生产。由于前期没有在主机端做日志收集类工具，缺乏主机端的攻击溯源手段，小Z临时搭建了splunk日志分析系统，并在新搭建的服务器上安装了sysmon日志收集工具，对主机层面进行了日志收集。过了一星期左右，小Z发现系统进程里面居然多了个叫wcmoye的进程，凭感觉这不是个正常程序，那就先从这个程序开始入手调查吧。

## 0×3 常规排查

常规排查还是采用了微软经典系统工具systeminternals套件，分别对启动项，系统进程，网络连接等简单做了排查。

启动项除了services这一项发现了一个奇怪的StuvwxAbcdefg Jkl，其他没有特别值得注意的地方。

![](https://image.3001.net/images/20180621/15295816361657.bmp!small)

进程排查就是那个叫wcmoye.exe的进程

![](https://image.3001.net/images/20180621/1529573204357.png!small)

进程依赖于StuvwxAbcdefgh Jkl这个服务

![](https://image.3001.net/images/20180621/15295732159362.png!small)

网络通信：用tcpview观察wcmoye.exe会不定时连接一公网ip的9999端口

![](https://image.3001.net/images/20180621/15295810269521.png!small)

同时会有一些注册表及文件系统上的行为，确定wcmoye躲在C:\windows\syswow64目录下

![](https://image.3001.net/images/20180621/15295817278809.png!small)

初步排查得出的结论是：wcmoye进程依赖于名叫Stuvwx Abcdefg Jkl系统服务，去syn链接公网ip的9999端口，是个木马程序。

在对wcmoye有了一定认识之后，小Z想它是从哪里来的，这时，小Z之前搭建的日志分析系统派上了用场。

## 0×4 日志排查

这个问题得从wcmoye.exe在系统中产生的第一时间着手调查。于是打开splunk开始搜索：通过
wcmoye关键字的搜索，发现6月6日20：24发生如下可疑事件：

20：24：11
Tomcat目录下有一个叫NewRat的可执行文件生成wcmoye.exe，原来wcmoye是有一个叫NewRat的可执行文件生成的，但是回到Tomcat目录下查看，并没有发现NewRat.exe这个文件.

![](https://image.3001.net/images/20180621/1529581051521.png!small)

不急，进一步搜索NewRat，小Z发现了更大的信息量:在wcmoye被创建的前一秒
20：24：10，tomcat7.exe去调用cmd.exe执行了一段比较长的脚本，

![](https://image.3001.net/images/20180621/15295810724605.png!small)

随着时序跟踪事件的发展，发现在20：24：12 调用cmd.exe删除了NewRat.exe

![](https://image.3001.net/images/20180621/15295811017916.png!small)

同时还观察到services.exe的执行，系统服务创建

![](https://image.3001.net/images/20180621/15295811102261.png!small)

关注sysmon的EventCode 3 ，wcmoye的进程会与下载NewRat的那个公网ip的9999端口有通信日志，

![](https://image.3001.net/images/20180621/15295811218642.png!small)

其实到这里，wcmoye是从哪里进来的已经基本搞清楚了，接下来的问题就是为什么会进来？Tomcat为什么去执行这些恶意命令？现在唯一的线索就是日志中的那个ftp登陆的ip以及账号密码了，继续吧。

## 0×5 顺藤摸瓜

小Z带着好奇心，继续探索过程，直接进入了这个ftp服务器!

![](https://image.3001.net/images/20180621/15295811347623.png!small)

使用FileZilla进入ftp服务器的目录，以一目十行地速度快速扫了一遍，首先蹦入小Z眼帘的就是NewRat.exe，不错，和前面的调查结果相吻合，NewRat就安静地躺在这里。

![](https://image.3001.net/images/20180621/15295811458234.png!small)

还有个独特专版st2-045 winlinux小组版文件夹，潜意识告诉小Z这个文件夹里面很可能有谜底的答案，先直接百度一下

![](https://image.3001.net/images/20180621/15295811592698.png!small)

好家伙，双系统传马还Kill国内外主流杀毒软件，关键是st2-045这个就是远程代码执行（RCE）漏洞(S2-045,CVE-2017-5638)，小Z不禁一颤，之前居然没想到测试这个高危的提权漏洞。

![](https://image.3001.net/images/20180621/15295811694841.png!small)

start.bat开始看吧

![](https://image.3001.net/images/20180621/15295811798490.png!small)

![](https://image.3001.net/images/20180621/15295811855099.png!small)

有一个叫wincmd.txt的文件，是winows平台下的执行脚本，红框的内容和前面splunk日志中的那段日志一模一样，也就是帮小Z引导到这里的那段关键日志。

![](https://image.3001.net/images/20180621/15295811972059.png!small)

Linux平台的脚本：关闭防火墙，下载一个叫tatada的ELF文件，把netstat等系统命令改名，清空日志等等

![](https://image.3001.net/images/20180621/15295812065849.png!small)

![](https://image.3001.net/images/20180621/15295812196684.png!small)

Result.txt文件，记录着一些扫描到的ip的端口开放情况

![](https://image.3001.net/images/20180621/15295812418799.png!small)

![](https://image.3001.net/images/20180621/15295812496265.png!small)

Windows.txt和linux.txt里面貌似都是存在漏洞的网址。。。

而且其中有一个关键的发现，就是小Z所在公司的网站接口居然在一个叫http.txt的list里面

![](https://image.3001.net/images/20180621/15295812594417.png!small)

到这里，小Z已经大致猜得出自己的公司网站是怎么被盯上的了。再看下几个可执行文件:

S.exe就是扫描器

![](https://image.3001.net/images/20180621/15295812703442.png!small)

IDA载入str045

![](https://image.3001.net/images/20180621/15295812798327.png!small)

![](https://image.3001.net/images/20180621/15295812866312.png!small)

![](https://image.3001.net/images/20180621/15295812986948.png!small)

![](https://image.3001.net/images/20180621/15295813056606.png!small)

![](https://image.3001.net/images/20180621/15295813138805.png!small)

看得出Str045.exe就是struts2-045的利用脚本程序，他会去读取S.exe扫描出的ip及端口开放情况的文件，组合do，action等开启多线程去exploit，然后根据被攻击的系统版本，去执行相应的脚本，像小Z公司的这台web服务器是windows的，就会去执行wincmd.txt。

## 0×6 网络架构

目前调查到的种种迹象让小Z坚信黑客是通过struts2-45漏洞进来的！于是小Z去网上下载了一个最新的struts漏洞检查工具，直接对网站的80端口进行检测，但结果出乎意料，居然没有漏洞报警。

![](https://image.3001.net/images/20180621/15295813233544.png!small)

黑客服务器上只有针对strusts2-045的攻击脚本，但是检测又没有发现漏洞。这个矛盾的问题不禁让小Z思考更多的可能性。

在陷入迷茫的深思同时，
小Z不经意的翻看着tomcat的localhost_access_log日志，突然一批ABAB型日志出现在他眼前，一个公网地址，一个内网地址，时间就在NewRat出现的前几分钟20:20:36：

![](https://image.3001.net/images/20180621/15295813333628.png!small)

这串高度相关的日志
究竟隐藏着什么意义？会不会是解开谜团的入口？带着强烈的好奇心，小Z咨询了网络组的同事，什么情况下才会出现这样的情况，网络组给出了网站如下的网络架构，并说明了由于业务的临时需求，新对网络架构做了新的调整。

![](https://image.3001.net/images/20180621/15295813418835.png!small)

服务器的内网端口是7070，公网防火墙上开放了80，443和8090端口。公网端口8090作了NAT对应内网的7070端口，据说是因为业务新需求开放的；同时为了安全考虑，公网用户如果只访问了80后，F5会做强制443端口跳转访问F5的一个vip地址。

这种网络架构，当有人在公网扫描到80和8090端口时，就会出现ABAB型日志，即A就是通过NAT进来的，B是从vip地址过来的。所以才会出现上述奇怪日志的原因，那个时刻，是黑客服务器在扫描
80和8090端口。

## 0×7 水落石出

NewRat也是在那个奇怪的日志后产生的，这时一个念头闪现在小Z脑海里，还是用struts漏洞利用工具，不过这次是去尝试web的的8090端口！一串清晰的红字,警告:存在Struts远程代码执行漏洞S2-045
！

![](https://image.3001.net/images/20180621/15295813552100.png!small)

再试试443端口，也能检测出：

![](https://image.3001.net/images/20180621/15295813639365.png!small)

获取web系统内网IP信息

![](https://image.3001.net/images/20180621/15295813713531.png!small)

![](https://image.3001.net/images/20180621/15295813786161.png!small)

而且通过搜索tomcat目录找到 struts的版本为2.5.10，的确是存在S2-045漏洞的版本。

至此，这次入侵的来龙去脉，小Z已经调查清楚了。由于网站使用了struts框架
版本为2.5.10，存在struts2-045漏洞，黑客通过公网扫描找到网站，进而执行exploit把病毒程序传到服务器里面执行，不停的病毒警告是因为不断有人在公网利用漏洞入侵服务器。

## 0×8 题外话

但同时，小Z也注意到了另一个问题，为什么struts漏洞利用工具直接访问80端口无法检测出漏洞?

小Z于是想到了Wireshark，这个网络放大镜或许能给出点蛛丝马迹。还是抓包对比一下吧。

抓一下未检测出漏洞的80端口的包，

![](https://image.3001.net/images/20180621/15295813889893.png!small)

![](https://image.3001.net/images/20180621/15295813968228.png!small)

![](https://image.3001.net/images/20180621/15295814047308.png!small)

![](https://image.3001.net/images/20180621/15295814113947.png!small)

第一次get请求，F5返回了一个https的302重定向后，由于connection:close，F5直接做出了FIN ACK

![](https://image.3001.net/images/20180621/15295814219361.png!small)

![](https://image.3001.net/images/20180621/15295814281665.png!small)

![](https://image.3001.net/images/20180621/15295814361270.png!small)

第二次，软件请求的还是与80端口，而且get请求是带完整https
url路径[的,这种请求格式导致F5](https://www.xxx.com/test/test.do,%E8%BF%99%E7%A7%8D%E9%94%99%E8%AF%AF%E7%9A%84%E8%AF%B7%E6%B1%82%E5%AF%BC%E8%87%B4F5)返回一个奇怪的重定向[https://WWW.XXX.COMhttps://WWW.XXX.COM/test/test.do](https://www.xxx.comhttps/WWW.XXX.COM/test/test.do).导致漏洞验证失败。

再来对比一下浏览器页面访问80端口测试：经过tcp三次握手，浏览器发出get请求之后，F5返回一个302重定向，浏览器于是向443端口开始了三次握手，接下来就是https的通信过程，

![](https://image.3001.net/images/20180621/15295814437457.png!small)

![](https://image.3001.net/images/20180621/15295814524678.png!small)

通过对比实验分析，发现在漏洞利用工具在测试80端口时，如果网站做了80转443端口的强制跳转，浏览器在得到302重定向后就开始向443端口开始3次握手，而测试软件的数据包处理过程就有问题，这时候直接测试80端口软件就会存在误报
**。**

小Z之前由于粗心，只测试网站的80端口，得出错误的结论，原因也找到了。

## 0×9 结尾

到此为止，所有的谜团一一解开，小Z结束了这次曲折的入侵取证之路。

参考链接：

> <https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon>
>
> <http://www.freebuf.com/sectool/125846.html>

 ***本文原创作者：fish1983，本文属FreeBuf原创奖励计划，未经许可禁止转载**

