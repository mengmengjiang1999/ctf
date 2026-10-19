**近日，亚信安全截获新型挖矿病毒FakeMsdMiner，该病毒利用永恒之蓝，永恒浪漫等NSA漏洞进行攻击传播。该病毒具有远控功能，可以获取系统敏感信息。其通过修改HOST文件方式截获其他挖矿病毒的成果。由于该病毒的挖矿程序伪装成微软系统服务msdtc.exe进行启动，所以我们将其命名为FakeMsdMiner。**

## 攻击流程

![](https://image.3001.net/images/20190605/1559724360_5cf78148cb441.png!small)

## 详细分析

### 内网渗透模块分析（windowsd.exe程序分析）

此程序会在C:\WINDOWS\Fonts\Mysql目录释放多个文件，其中包括BAT脚本处理文件、端口扫描文件、永恒之蓝漏洞攻击文件、payload以及下载程序wget。

![](https://image.3001.net/images/20190605/1559724385_5cf781617ebaa.png!small)

![](https://image.3001.net/images/20190605/1559724395_5cf7816b49d46.png!small)

mysql.bat脚本文件：

该脚本主要功能是删除感染过该病毒的系统中存在的旧服务，安装并开启新的服务MicrosoftMysql，并添加计划任务cmd.bat。

![](https://image.3001.net/images/20190605/1559724439_5cf7819753ce4.png!small)

![](https://image.3001.net/images/20190605/1559724448_5cf781a03dc98.png!small)

cmd.bat脚本文件

该脚本主要功能是端口和IP扫描，通过查询固定地址寻找出口IP和本机IP，获取IP地址的前2段，拼接后面2段地址，然后扫描445和450端口，将结果保存在ips.txt中，启动load.bat脚本进行攻击。

![](https://image.3001.net/images/20190605/1559724482_5cf781c276501.png!small)

![](https://image.3001.net/images/20190605/1559724500_5cf781d485ffb.png!small)

![](https://image.3001.net/images/20190605/1559724506_5cf781da6f6e9.png!small)

load.bat脚本：

该脚本主要功能是运行永恒之蓝、永恒浪漫等NSA漏洞攻击程序，进行内网渗透。

![](https://image.3001.net/images/20190605/1559724536_5cf781f818da9.png!small)

### 挖矿程序模块（mm.exe文件分析）

该模块同样会释放很多文件，其中包括挖矿程序、注入系统的DLL文件以及远控木马程序。通过调用1.bat脚本，依次启动和运行这些程序。

![](https://image.3001.net/images/20190605/1559724555_5cf7820b37d21.png!small)

通过修改LoadAppInit_DLLs注册表项，将DLL文件注入到相应的系统中。

![](https://image.3001.net/images/20190605/1559724573_5cf7821d05c6c.png!small)

将挖矿程序复制到msdtc.exe文件中，伪装成微软系统服务文件msdtc，并为其安装服务启动门罗币挖矿，其使用的矿机版本为：XMRig 2.14.1。

![](https://image.3001.net/images/20190605/1559724589_5cf7822df2155.png!small)

![](https://image.3001.net/images/20190605/1559724612_5cf78244c36af.png!small)

![](https://image.3001.net/images/20190605/1559724628_5cf78254276db.png!small)

关闭防火墙

![](https://image.3001.net/images/20190605/1559724661_5cf7827547177.png!small)

删除与本次病毒相关的文件 temp2.exe(本模块文件)和temp3.exe(漏洞攻击模块母体文件)。

![](https://image.3001.net/images/20190605/1559724693_5cf7829553210.png!small)

在host文件中追加相关域名指向139.180.214.175，该地址为本次挖矿的矿池IP,
挖矿木马试图通过将其他矿池映射到自己的矿池对应的ip地址，来劫持其他挖矿程序或木马的收益。

![](https://image.3001.net/images/20190605/1559724709_5cf782a5c3727.png!small)

### 远程控制木马模块（work.exe文件分析）

首先从资源截取释放病毒核心程序，然后添加注册表，开启服务。我们使用资源工具也同样可以看到，该资源区段其实就是一个PE文件。

![](https://image.3001.net/images/20190605/1559724727_5cf782b71547e.png!small)

![](https://image.3001.net/images/20190605/1559724734_5cf782be6e88f.png!small)

![](https://image.3001.net/images/20190605/1559724751_5cf782cf40942.png!small)

值得注意的是，我们在分析时发现了Gh0st字样，Gh0st是著名的开源远程控制程序，我们猜测该远控模块很有可能是用Gh0st远控程序修改而来。

![](https://image.3001.net/images/20190605/1559724770_5cf782e201cd0.png!small)

Dump出资源模块，我们分析发现其主要功能就是接受不同指令执行不同的功能。这也是常见的远控功能。

![](https://image.3001.net/images/20190605/1559724789_5cf782f54906b.png!small)

其中包括录音功能：

![](https://image.3001.net/images/20190605/1559724805_5cf78305632d5.png!small)

录制屏幕功能：

![](https://image.3001.net/images/20190605/1559724823_5cf783174403a.png!small)

在系统中提权，获取相关进程等信息：

![](https://image.3001.net/images/20190605/1559724841_5cf7832929b92.png!small)

获取机器窗口信息：

![](https://image.3001.net/images/20190605/1559724870_5cf78346e5c0e.png!small)

获取机器驱动器信息

![](https://image.3001.net/images/20190605/1559724913_5cf78371a8263.png!small)

获取机器屏幕信息：

![](https://image.3001.net/images/20190605/1559724922_5cf7837abe810.png!small)

获取日志文件：

![](https://image.3001.net/images/20190605/1559724940_5cf7838c24226.png!small)

将收集的信息发送至远端：

![](https://image.3001.net/images/20190605/1559724960_5cf783a01b8bb.png!small)

## 关联性分析

我们在分析远控时发现了Gh0st字样，Gh0st是之前一款较为流行的开源远程控制程序，目前使用Gh0st以获取远程访问和控制的主要群体是“铁虎（Iron
Tiger）”，自称来自中国的APT组织。

我们通过对Gh0st木马导入函数分析，可知该程序从Winsock库中导入了很多函数，这也意味着该程序可能与远程服务器建立连接或者从远端服务器接收连接。同样也使用了winmm库函数，此函数wave与录音操作有关系。在本次远控核心代码中也同样使用了该库的函数，用于将录音信息发送至远端服务器。

![](https://image.3001.net/images/20190605/1559725060_5cf78404938ef.png!small)

![](https://image.3001.net/images/20190605/1559725090_5cf78422a7674.png!small)

通过导入的库，我们看到一个msvfw32.dll文件被导入。看起来这个DLL为该程序提供了视频功能，这也与我们本次远控程序中将录屏信息发送至远端服务器相呼应。

![](https://image.3001.net/images/20190605/1559725110_5cf784364c5e2.png!small)

们将两者对比，他们都使用了很多相同的库函数，以便实现相应的操作。

![](https://image.3001.net/images/20190605/1559725137_5cf78451da4b5.png!small)

通过代码我们也发现，他们的确有很多相似的地方，都是通过switch语句接收不同的指令，进而完成不同的功能。例如录音功能、录屏功能等。

通过以上分析我们认为，本次挖矿程序的远控代码很大程度上是通过Gh0st程序修改而来。

![](https://image.3001.net/images/20190605/1559725160_5cf784683bb62.png!small)

## 解决方案

> 利用系统防火墙高级设置阻止向445端口进行连接（该操作会影响使用445端口的服务）。
>
> 尽量关闭不必要的文件共享；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 打开系统自动更新，并检测更新进行安装。
>
> 系统打上MS17-010对应的Microsoft Windows SMB 服务器安全更新 (4013389)补丁程序。

详细信息请参考链接：<http://www.catalog.update.microsoft.com/Search.aspx?q=MS17-010>

 ***本文作者：亚信安全，转载请注明来自FreeBuf.COM**

