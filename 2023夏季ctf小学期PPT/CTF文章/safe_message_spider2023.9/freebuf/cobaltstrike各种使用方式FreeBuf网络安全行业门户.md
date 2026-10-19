本文仅用于记录自身学习过程。、

## cobalt strike简称

cobalt strike(简称CS）是一款团队作战渗透测试神器，分为客户端及服务端，一个服务端可以对应多个客户端，一个客户端可以连接多个服务端。

CS主要是用来后期持久渗透、横向移动、流量隐藏、数据窃取的工具。当已经在目标机器上执行了CS的payload，它会创建一个Beacon(远控木马功能）回连到C2服务器。

## cobalt strike启动

启动服务端

chmod 777 teamserver

./teamserver [server_ipaddress] [password]

例: ./teamserver 192.168.138.136 123456

启动客户端

手动启动：

Java -XX:ParallelGCThreads=4-XX:+AggressiveHeap -XX:+UseParallelGC
-Xms512M-Xmx1024M jarcobaltstrike.jar

bat脚本自动启动：

start.bat

![1645772915_621880734d7840ddeb5a3.png!small?1645772915526](https://image.3001.net/images/20220225/1645772915_621880734d7840ddeb5a3.png!small?1645772915526)

## cobalt strike介绍

![1645773039_621880efb4b73f92e8202.png!small?1645773040014](https://image.3001.net/images/20220225/1645773039_621880efb4b73f92e8202.png!small?1645773040014)

listener监听器-所有的操作都依赖listener

![1645773114_6218813ab664b6203217e.png!small?1645773114967](https://image.3001.net/images/20220225/1645773114_6218813ab664b6203217e.png!small?1645773114967)

攻击模块Attacks

![1645773164_6218816c286eeffe0bd1a.png!small?1645773164537](https://image.3001.net/images/20220225/1645773164_6218816c286eeffe0bd1a.png!small?1645773164537)

![1645773509_621882c537efd267a02fc.png!small?1645773509454](https://image.3001.net/images/20220225/1645773509_621882c537efd267a02fc.png!small?1645773509454)

![1645773528_621882d87c6fc95e29fa0.png!small?1645773528901](https://image.3001.net/images/20220225/1645773528_621882d87c6fc95e29fa0.png!small?1645773528901)

## HTML application

1.生成hta文件

![1645773282_621881e2533b2beaa4b55.png!small?1645773282493](https://image.3001.net/images/20220225/1645773282_621881e2533b2beaa4b55.png!small?1645773282493)![1645773298_621881f2bedbfcb31909d.png!small?1645773299999](https://image.3001.net/images/20220225/1645773298_621881f2bedbfcb31909d.png!small?1645773299999)

2.提供端口下载文件

![1645773312_62188200cd705cbc2f3ed.png!small?1645773313062](https://image.3001.net/images/20220225/1645773312_62188200cd705cbc2f3ed.png!small?1645773313062)![1645773325_6218820d9551c8e3e5724.png!small?1645773325763](https://image.3001.net/images/20220225/1645773325_6218820d9551c8e3e5724.png!small?1645773325763)

3.靶机执行远程命令-利用命令执行权限

![1645773415_62188267ca8913d2cfbee.png!small?1645773415942](https://image.3001.net/images/20220225/1645773415_62188267ca8913d2cfbee.png!small?1645773415942)

4.靶机上线

![1645773438_6218827e63797f0ebada1.png!small?1645773438529](https://image.3001.net/images/20220225/1645773438_6218827e63797f0ebada1.png!small?1645773438529)

5.控制目标主机 sleep睡眠时间。 shell+cmd命令

![1645773462_62188296a1dda0f9f4c9e.png!small?1645773462789](https://image.3001.net/images/20220225/1645773462_62188296a1dda0f9f4c9e.png!small?1645773462789)

## 生成后门木马

Windows Executable

1.生成可执行文件

![1645773580_6218830c395d64adb25b4.png!small](https://image.3001.net/images/20220225/1645773580_6218830c395d64adb25b4.png!small)

![1645773621_621883358dcf7addbc391.png!small?1645773621728](https://image.3001.net/images/20220225/1645773621_621883358dcf7addbc391.png!small?1645773621728)

2.上传目标机器

通过webshell上传运行

通过互联网钓鱼

## Office宏病毒

1.创建宏，设置监听

![1645773679_6218836f8c7594956b08e.png!small?1645773679726](https://image.3001.net/images/20220225/1645773679_6218836f8c7594956b08e.png!small?1645773679726)

![1645773697_62188381056be50acf64e.png!small?1645773697197](https://image.3001.net/images/20220225/1645773697_62188381056be50acf64e.png!small?1645773697197)

2.为文档添加宏，保存

-打开正常的office文件，如test.docx-视图->宏-→>查看宏

-选择宏的位置为当前文档-→输入宏名->创建- copy Macro粘贴到宏命令处

![1645773710_6218838ec534365ce49a1.png!small?1645773711002](https://image.3001.net/images/20220225/1645773710_6218838ec534365ce49a1.png!small?1645773711002)

-选择否，另存为docm文件

![1645773718_62188396d1f8c1ead65ae.png!small?1645773718978](https://image.3001.net/images/20220225/1645773718_62188396d1f8c1ead65ae.png!small?1645773718978)

3.上传至目标机器

-通过互联网邮箱、社交媒体、论坛传播-诱导点击

## Windows靶机提权

提权的前提条件

-拥有普通用户权限

-拥有某些软件的账户密码

-本地或远程服务器上存在漏洞

-拥有漏洞利用工具代码

提权过程

User（普通用户）--->Administrator（管理员用户）--->system（系统用户不可登录）

1.首先呢拥有一个会话，利用系统漏洞提权。

![1645773794_621883e253b2ce3af7bf1.png!small?1645773794522](https://image.3001.net/images/20220225/1645773794_621883e253b2ce3af7bf1.png!small?1645773794522)

![1645773812_621883f45ea457e201dbf.png!small](https://image.3001.net/images/20220225/1645773812_621883f45ea457e201dbf.png!small)

2.利用bypass_uac提权（绕过uac ）

概念：用户帐户控制(User Account Control，简写作UAC)是微软公司在其Windows
Vista及更高版本操作系统中采用的一种控制机制。其原理是通知用户是否对应用程序使用硬盘驱动器和系统文件授权，以达到帮助阻止恶意程序(有时也称为“恶意软件”)损坏系统的效果。Uac消除了以管理员账户所带来的风险。

手动关闭uac 控制面板-用户账户-更改用户控制设置

![1645773847_621884173b915efff3a22.png!small?1645773847441](https://image.3001.net/images/20220225/1645773847_621884173b915efff3a22.png!small?1645773847441)

whoami

Net user 用户名

![1645773871_6218842fbf56c794212e0.png!small?1645773871902](https://image.3001.net/images/20220225/1645773871_6218842fbf56c794212e0.png!small?1645773871902)

在管理员组中，说明它是有管理员权限的，但是是受uac控制的，

1.创建一个新的listener

![1645773879_6218843751d2d0e610d9c.png!small?1645773879472](https://image.3001.net/images/20220225/1645773879_6218843751d2d0e610d9c.png!small?1645773879472)

2.bypass_uac提权管理员权限

![1645773886_6218843ea097f8693f2e1.png!small?1645773886812](https://image.3001.net/images/20220225/1645773886_6218843ea097f8693f2e1.png!small?1645773886812)![1645773892_6218844477deb98aef489.png!small?1645773892628](https://image.3001.net/images/20220225/1645773892_6218844477deb98aef489.png!small?1645773892628)

3.svc-ese提权system权限（利用提权之后的会话提权）![1645773906_6218845211279aff8d0c9.png!small?1645773906211](https://image.3001.net/images/20220225/1645773906_6218845211279aff8d0c9.png!small?1645773906211)

4.利用

>查询3389开发情况

shell REG QUERY "HKEY_LOCAL_MACHINE\SYSTEM(CurrentControlSet\ControlNTerminal
Server"/v fDenyTSConnections

1表示关闭，0表示开启

>开启3389远程连接

shell REG ADD "HKLM\SYSTEM\CurrentControlSet\ControlNTerminal Server"/v
fDenyTSConnections /t REG_DWORD/d00000000 /f

>连接

win+R -> mstsc ->输入账号密码

## Web克隆钓鱼：

![1645773978_6218849a62d22ba7b4483.png!small?1645773978549](https://image.3001.net/images/20220225/1645773978_6218849a62d22ba7b4483.png!small?1645773978549)

![1645773991_621884a79167406abcc54.png!small?1645773991740](https://image.3001.net/images/20220225/1645773991_621884a79167406abcc54.png!small?1645773991740)

