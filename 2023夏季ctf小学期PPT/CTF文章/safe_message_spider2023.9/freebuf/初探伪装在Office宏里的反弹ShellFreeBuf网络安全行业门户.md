***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：si1ence，本文属FreeBuf原创奖励计划，未经许可禁止转载**

##  **0x0** **背景**

**通常的钓鱼邮件场景中office的安全问题一直都受到关注，恶意宏文档制作简单，兼容性强，并且攻击成本较小，所以整体占比较大。但是使用恶意宏进行攻击，往往需要用户进行交互，攻击的隐蔽性不强，结合Powershell的攻击方式二者结合还是可以搞一点大事情的。**

前段时间在接触到一些基于鱼叉邮件攻击的案例时针对里面的银行木马与攻击方式进行了简单的分析，对powershell与office的宏巧妙结合的方式产生了一些兴趣。  

##  **0x1** **主要思路**

宏病毒是一种寄存在文档或模板的宏中的计算机病毒。一旦打开这样的文档，其中的宏就会被执行，于是宏病毒就会被激活，转移到计算机上，并驻留在Normal模板上。

我们通过工具生成一个有powershelldownloader功能的一个excel，victim服务器打开此excel之后会从CC服务器下载并执行一个基于powershell的payload到本地的计算机后就可以通过CC服务器当中的Metasploit操控Victim服务器。

##  **0x2** **攻击方法**

首先在kali下面生成一个powershell的后门，设置好相关的参数。

![](https://image.3001.net/images/20181103/1541258858_5bddbe6a29bff.jpg!small)本地开启http的服务器，kali2集成好了apache的服务，将生成好的后门改名为payload.txt后门复制到网站的根目录。

![](https://image.3001.net/images/20181103/1541258892_5bddbe8cb1dca.jpg!small)

通过浏览器访问，确认可以访问成功。

![](https://image.3001.net/images/20181103/1541258921_5bddbea93363d.jpg!small)

之后本地设置好Metasploit的参数，开始监听，这里的payload主要reverse_https可以避开一些基于流量检测的安全设备。

![](https://image.3001.net/images/20181103/1541258948_5bddbec437e5a.jpg!small)在github下载一个powershell工具用于生成excel后门，这里使用了Generate-Macro一个评价很不错的小工具。  

连接如下：[https://github.com/enigma0x3/Generate-Macro](http://www.example.com)

![](https://image.3001.net/images/20181103/1541258970_5bddbeda68dc1.jpg!small)

本地生成excel的后门excel文档设置好相关的参数选项，比较温馨的是会自动的将宏与文档打包到一起，目前只支持http协议和https协议，在选择后门的自启动方式这里还是有很多选择，设置计划任务也是很多后门常用的手段之一。

![](https://image.3001.net/images/20181103/1541258998_5bddbef607d48.jpg!small)victim端打开此文档后启用宏之后，会执行相关的宏代码连接到Metasploit的客户端，使用shell命令可以可以获得一个命令行对应的windows系统此时应该会拉起一个cmd.exe

![](https://image.3001.net/images/20181103/1541259025_5bddbf11c6877.jpg!small)![](https://image.3001.net/images/20181103/1541259034_5bddbf1ab96ff.jpg!small)

##  **0x3 进程拉起顺序**  

在victim端口查看相关进程可以发现依次的启动顺序为：svchost.exe-> WmiPrvSE.exe -> powershell.exe
->powershell.exe ->cmd.exe

![](https://image.3001.net/images/20181103/1541259066_5bddbf3a5e1a1.jpg!small)待用户执行了宏代码之后，会调用windows系统的当中的wmi拉起powershell进行下载并连接远程CC端。

关键代码如下：  

![](https://image.3001.net/images/20181103/1541260695_5bddc597b30e5.png!small)可以在第一个powershell.exe的启动参数找到痕迹

![](https://image.3001.net/images/20181103/1541259136_5bddbf80b4827.jpg!small)第一个powershell.exe之后拉起第二个powershell.exe执行保存在payload.txt里面的恶意代码，会设置自启动。

![](https://image.3001.net/images/20181103/1541259173_5bddbfa5c08ca.jpg!small)之后在执行了shell命令执行，第二个powershell.exe会主动拉起一个cmd.exe
进行远程命令执行。

##  **0x4** **其他行为**

可以在注册表当中找到已经设置好的自启动项目，主要内容保存在C盘C:\Users\Public\config.vbs目录下并设置隐藏属性。

![](https://image.3001.net/images/20181103/1541259295_5bddc01f9a0c2.jpg!small)生成开机启动的恶意文件代码如下：![](https://image.3001.net/images/20181103/1541260597_5bddc53516d68.png!small)添加到注册表的恶意代码如下：

  

![](https://image.3001.net/images/20181104/1541260987_5bddc6bb1e6f3.png!small)

通过抓包分析获取到的流量数据基本都是是乱码,流量分析起来有一定的困难。![](https://image.3001.net/images/20181103/1541259330_5bddc042a9cdd.jpg!small)

##  **0x5** **总结**

1.如果投递特定主题及内容的电子邮件来进行攻击，安全意识薄弱的用户很容易中招。攻击者从远程获取恶意软件或者攻击负载powershell脚本经过混淆之后进行base64编码，对于检测这些攻击行为无论是静态扫描还是动态检测都造成了一定的难度。

2.office本身也有CVE2017-0262、CVE–2017–8759、CVE-2017-0199、CVE-2017-11882等多个安全问题，攻击手法也有了较多的差异性，作为普通用户在日常的工作生活当中还是应该提升自身的安全意识，安装杀毒软件支持国产office，对于陌生的邮件一定要慎点。

***本文原创作者：si1ence，本文属FreeBuf原创奖励计划，未经许可禁止转载**

