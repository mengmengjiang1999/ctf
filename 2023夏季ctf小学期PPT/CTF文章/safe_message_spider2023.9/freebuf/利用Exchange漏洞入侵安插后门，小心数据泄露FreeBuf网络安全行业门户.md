## ****背景概述****

近日，深信服终端安全团队发现一起有针对性的黑产攻击事件，攻击者利用Exchange邮件服务漏洞入侵服务器，并通过部署恶意服务下载后门模块，获取用户信息、远程命令执行恶意程序、进行文件管理等，以此完成对受害主机的控制。

##  ** **攻击流程分析****

攻击者利用Exchange邮件服务漏洞上传webshell，随后部署恶意服务。恶意服务会隔一段时间访问一次后台，若后台开放则下载后门模块。并且攻击者自己实现了PE文件加载器，通过该加载器解密、修复并运行后门模块。

###  **
**攻击流程图****![](https://image.3001.net/images/20211101/1635768996_617fdaa441ed8e8e751cb.png!small)

从日志中可以看到攻击者多次访问webshell。

![](https://image.3001.net/images/20211101/1635769128_617fdb28269e7227e6bf8.png!small)

部署恶意服务，服务命名为Spooler。

![](https://image.3001.net/images/20211101/1635769142_617fdb366d921f3a63ff6.png!small)

服务拉起恶意进程，进程名称不固定，通常伪装成业务文件。

![](https://image.3001.net/images/20211101/1635769152_617fdb40d7bf7831d5dfa.png!small)

访问后台并且下载恶意模块，取随机数重新命名恶意模块。

![](https://image.3001.net/images/20211101/1635769162_617fdb4a87b647ca03045.png!small)

对下载下来的后门模块进行解密，解密之前会判断文件头是否是0xE1FED9D0。

![](https://image.3001.net/images/20211101/1635769172_617fdb54f0fe02578e051.png!small)

修复IAT、重定位表，并运行后门模块。

![](https://image.3001.net/images/20211101/1635769181_617fdb5d45cf7c92ecad1.png!small)

##  ** **后门模块分析****

安全专家在相关目录下发现几个随机名字的文件，经过解密分析可以确认为服务下载下来的后门模块。

后门模块不仅包含获取主机信息、远程命令执行、获取磁盘信息、下载文件、文件重命名等功能，还通过修改注册表、覆盖文件实现持久化。

将自身复制为schmet.exe并修改注册表加入启动项目。

![](https://image.3001.net/images/20211101/1635769199_617fdb6f75323413133f6.png!small)

将自身复制为schost.exe，并且覆盖FileSyncFalwb.dll文件，在FileSyncFalwb.dll中运行schost.exe

![](https://image.3001.net/images/20211101/1635769210_617fdb7a2e467f632f810.png!small)

将自身复制到mpetect.exe，修改注册表键值UserInitMprLogonScript

![](https://image.3001.net/images/20211101/1635769221_617fdb85446374398574c.png!small)

获取主机信息，包含用户名、计算机名、系统版本、CPU主频等信息。

![](https://image.3001.net/images/20211101/1635769231_617fdb8fc81f0d3ec4c2e.png!small)

利用匿名管道远程执行powershell指令。

![](https://image.3001.net/images/20211101/1635769243_617fdb9b64eee7516bcba.png!small)

获取主机各个磁盘的信息。

![](https://image.3001.net/images/20211101/1635769252_617fdba449e15cae34472.png!small)

下载主机的文件

![](https://image.3001.net/images/20211101/1635769260_617fdbacf19071e8d2900.png!small)

文件重命名

![](https://image.3001.net/images/20211101/1635769271_617fdbb7e7b4f1e82aa50.png!small)

##  ** **安全加固****

1.内网中的主机系统、服务软件保持安装最新的补丁，避免漏洞入侵。

2.服务器密码使用复杂密码，且不要与其他主机密码重复、不要与外部账号密码重复，防止泄露。

3.避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀。

