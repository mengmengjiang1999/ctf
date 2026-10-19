## 系统漏洞的利用与防范

这里用到虚拟机Win7作为靶机

### 1.nmap -sP

首先打开kali主机，打开终端，输入“nmap -sP
某网段”这条命令来扫描该网段存活主机，然后通过ifconfig查看本机IP地址来排除本机IP地址并排除网关地址，最后推断出目标IP地址。

![1614524427_603bb00bd828ab2e5135b.png!small?1614524428382](https://image.3001.net/images/20210228/1614524427_603bb00bd828ab2e5135b.png!small?1614524428382)

### 2.1.nmap --script=vuln

使用“nmap --script=vuln
某IP地址”来对服务器进行系统漏洞扫描。![1614524292_603baf84c8d004790e873.png!small?1614524293375](https://image.3001.net/images/20210228/1614524292_603baf84c8d004790e873.png!small?1614524293375)

### 2.2.nessus

或者打开nessus，点击“New Scan”，输入想要扫描的IP地址或者网段，然后使用“Advanced Scan”，开始扫描，最后得到结果。

![1614524364_603bafcc4269bcbfa0cdc.png!small?1614524364736](https://image.3001.net/images/20210228/1614524364_603bafcc4269bcbfa0cdc.png!small?1614524364736)

### 3.使用Msfconsole利用漏洞攻击

使用两种工具扫描后，发现靶机存在许多漏洞，有ms12-020漏洞、ms17-010漏洞等。这里我们分别利用

ms12-020漏洞、ms17-010漏洞对靶机进行攻击

1、首先打开kali主机，打开终端，输入“msfconsole，进入Metasploit控制台

![1614526366_603bb79e639c3a90ceac2.png!small?1614526366892](https://image.3001.net/images/20210228/1614526366_603bb79e639c3a90ceac2.png!small?1614526366892)

![1614526389_603bb7b56a1fc33b006dc.png!small?1614526389869](https://image.3001.net/images/20210228/1614526389_603bb7b56a1fc33b006dc.png!small?1614526389869)

2、搜索ms12-020漏洞

![1614526459_603bb7fb5673ee355cfcb.png!small?1614526461261](https://image.3001.net/images/20210228/1614526459_603bb7fb5673ee355cfcb.png!small?1614526461261)

3、使用Name为“……/ms12_020_check“并查看选项

![1614526475_603bb80b8aae6777ad6a1.png!small?1614526476077](https://image.3001.net/images/20210228/1614526475_603bb80b8aae6777ad6a1.png!small?1614526476077)![1614526484_603bb81436dc46b5d5227.png!small?1614526484825](https://image.3001.net/images/20210228/1614526484_603bb81436dc46b5d5227.png!small?1614526484825)

通过查看选项，这里可以看到第一个“RHOSTS“的Required栏是yes，说明需要配置，而这里的RHOSTS指的是目标主机的IP地址

4、配置RHOSTS![1614526507_603bb82b62be023136651.png!small?1614526507878](https://image.3001.net/images/20210228/1614526507_603bb82b62be023136651.png!small?1614526507878)

5、再次查看选项![1614526516_603bb834f2ea7f1080024.png!small?1614526517452](https://image.3001.net/images/20210228/1614526516_603bb834f2ea7f1080024.png!small?1614526517452)

6、开始运行![1614526525_603bb83d49b71324b13af.png!small?1614526525761](https://image.3001.net/images/20210228/1614526525_603bb83d49b71324b13af.png!small?1614526525761)

发现该主机存在该漏洞

7、接着使用……/ms12_020_maxchannelids，其余操作跟上面一样![1614526551_603bb857b6636cb0575f1.png!small?1614526552226](https://image.3001.net/images/20210228/1614526551_603bb857b6636cb0575f1.png!small?1614526552226)

然后运行，可见成功了![1614526564_603bb8640280ce390645a.png!small?1614526564516](https://image.3001.net/images/20210228/1614526564_603bb8640280ce390645a.png!small?1614526564516)ms17-010漏洞﻿利用同理，运行后结果如下

![1614526800_603bb950c0657623acc2b.png!small?1614526802568](https://image.3001.net/images/20210228/1614526800_603bb950c0657623acc2b.png!small?1614526802568)

### 4.漏洞的防护

具体操作：为win7系统打上补丁，并加固windows系统。并通过两种方式验证win7不存在ms17-010与ms12-020

Microsoft补丁网站：<http://www.catalog.update.microsoft.com/home.aspx>

![1614527028_603bba343dc2fa5f8df7f.png!small?1614527028773](https://image.3001.net/images/20210228/1614527028_603bba343dc2fa5f8df7f.png!small?1614527028773)

注意：下载补丁要根据电脑是32位还是64位的来下载！！

步骤以及截图：

1、先在网站上下载好ms17-010和ms12-020的补丁，先在win7系统上打上ms12-020的补丁，记得一定要重新启动才能生效，不然漏洞还是可以被利用。重启后再用kali的check运行，可以发现变成了Cannot
reliably check
exploitability.![1614527051_603bba4b6887959fc357d.png!small?1614527051871](https://image.3001.net/images/20210228/1614527051_603bba4b6887959fc357d.png!small?1614527051871)

而使用auxiliary/dos/windows/rdp/ms12_020_maxchannelids运行，则结果如下![1614527065_603bba594686739113f14.png!small?1614527066104](https://image.3001.net/images/20210228/1614527065_603bba594686739113f14.png!small?1614527066104)

失败了，可见补丁安装成功

这里拓展一下删除补丁：![1614527092_603bba744e921a15362b4.png!small?1614527092947](https://image.3001.net/images/20210228/1614527092_603bba744e921a15362b4.png!small?1614527092947)

如果想在win7系统中删除补丁，记得要重新启动才能生效

2、接下来安装ms17-010的补丁，记得要重新启动才能生效。如果想删除，记得也要重启，同理![1614527221_603bbaf55916f605d9bf8.png!small?1614527222031](https://image.3001.net/images/20210228/1614527221_603bbaf55916f605d9bf8.png!small?1614527222031)![1614527226_603bbafa8bce93a2a06d7.png!small?1614527227162](https://image.3001.net/images/20210228/1614527226_603bbafa8bce93a2a06d7.png!small?1614527227162)![1614527232_603bbb004e6826c6b106b.png!small?1614527232826](https://image.3001.net/images/20210228/1614527232_603bbb004e6826c6b106b.png!small?1614527232826)![1614527385_603bbb99b198fcb44145e.png!small?1614527386144](https://image.3001.net/images/20210228/1614527385_603bbb99b198fcb44145e.png!small?1614527386144)

