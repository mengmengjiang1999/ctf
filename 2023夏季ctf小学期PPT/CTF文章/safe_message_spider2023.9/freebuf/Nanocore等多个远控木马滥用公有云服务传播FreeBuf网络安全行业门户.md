攻击者越来越多的采用云来构建自己的基础设施，这样不仅能够使攻击者以最少的时间或金钱部署攻击基础设施，也能让追踪攻击行动变得更困难。

从 2021 年 10 月 26 日开始，研究人员发现多个远控木马开始通过云服务进行投递传播。

感染链从带有恶意 ZIP 附件的钓鱼邮件开始，ZIP 文件中包含一个带有恶意程序的 ISO 镜像文件。恶意程序的多种多样，如
JavaScript、Windows 批处理文件或 Visual Basic
脚本。脚本执行后，会通过下载服务器下载下一阶段的攻击载荷，攻击者将下载服务器部署在基于 Azure 的 Windows 服务器或基于 AWS 的 EC2
实例上。

![image.png-310.7kB](https://image.3001.net/images/20220114/1642152642_61e142c23c7e82de7b687.png!small)感染链

攻击者使用的远控木马是 Netwire、Nanocore 和 AsyncRAT，并且利用免费动态 DNS 服务 DuckDNS 注册了多个恶意域名。

## 攻击载荷

### Nanocore

Nanocore 通常是 32 位 .NET 可执行文件，在 2013 年被首次发现，后来被各种攻击者广泛使用。

从发现的 Nanocore 样本中提取配置信息后，可以确认攻击者使用的是 1.2.2.0 版本（已泄露版本）的 Nanocore。样本的构建日期为 2021
年 10 月 26 日，使用的 C&C 服务器为 `mback5338.duckdns.org`。

![image.png-239kB](https://image.3001.net/images/20220114/1642152644_61e142c44eecca11d3200.png!small)Nanocore
配置文件

后续发现的 Nanocore 样本也会使用其他不同的 C&C 服务器和端口号：

> nanoboss.duckdns.org
>
> justinalwhitedd554.duckdns.org

样本中携带的是 Client 插件和 SurveillanceEx 插件，前者用于处理与 C&C 服务器的通信，后者用于提供对音视频的捕获和远程桌面。

### Netwire

Netwire 通常会窃取受害者的密码、登录凭据和信用卡数据等隐私信息，同时兼具命令执行和窃取文件的功能。

通过写入注册表进行持久化：

> HKEY_CURRENT_USER\Software\NETwIRe\HostId
>
> HKEY_CURRENT_USER\Software\NETwIRe\Install Date
>
> HKEY_CURRENT_USER\SOfttware\Microsoft\WIndows\CurrentVersion\Run\SysWOW32

### AsyncRAT

AsyncRAT 通常会通过加密链接远程监控和控制计算机，攻击者还可以通过 AsyncRAT 对失陷主机进行击键记录、屏幕录像等操作。

AsyncRAT 创建互斥体 `AsyncMutex_6SI8OkPnk`作为失陷主机的感染标记。

![image.png-225.7kB](https://image.3001.net/images/20220114/1642152645_61e142c53b69bdce42cb1.png!small)AsyncRAT
互斥量

从 AsyncRAT 配置文件提取相关信息，C&C 域名是 `asyncmoney.duckdns.org`，使用的端口有 7829、7840、7841 和
7842。

![image.png-366.7kB](https://image.3001.net/images/20220114/1642152645_61e142c5ef96d066f48f3.png!small)AsyncRAT
连接 C&C 服务器

## 感染链

感染链起始的附件是一个 ISO 镜像文件，其中包含恶意的加载程序。如下所示，攻击者利用发-票文件来引诱用户点击打开：

![image.png-130.9kB](https://image.3001.net/images/20220114/1642152647_61e142c70d532017a4bd2.png!small)钓鱼邮件示例

ZIP 文件的起始字符是随机生成的，可能与特定的攻击行动有关。发现的一些文件名如下所示：

> WROOT_Invoice_Copy.zip
>
> YUEOP_Invoice_Copy.zip
>
> HOO8M_Invoice_Copy.zip
>
> TROOS_Invoice_Copy.zip
>
> TBROO1_Invoice_Copy.zip

### JavaScript Downloader

JavaScript Downloader 是一个有着四层混淆的脚本。

#### 第一层

第一层去混淆由 `ejv()`完成，该函数将混淆数据的每个字符保存在数组中，执行算术运算进行解密。

![image.png-168.6kB](https://image.3001.net/images/20220114/1642152647_61e142c7cf7751480f257.png!small)解密函数

紧接着继续解密：

![image.png-350.3kB](https://image.3001.net/images/20220114/1642152649_61e142c9584cddabe2e5d.png!small)解密函数

#### 第二层

其余加密内容在第二层进行解密，将 `ejv()`解密的结果传递给解密函数。

去混淆的结果包含另一个解密函数 `Ox$()`，这是第三层解密函数。

![image.png-160.4kB](https://image.3001.net/images/20220114/1642152650_61e142ca98e9246b4a1d5.png!small)解密函数

#### 第三层

第三层去混淆的结果是另一个混淆函数，包含多个函数调用来进行解密：

![image.png-1914.9kB](https://image.3001.net/images/20220114/1642152651_61e142cb6d19215455a6e.png!small)部分混淆恶意代码

在分析另一个发现的 JavaScript 脚本时，与首次发现的不相同。这说明代码有可能是自动生成和随机化的，攻击者想通过高度混淆使检测变得更困难。

![image.png-1118.4kB](https://image.3001.net/images/20220114/1642152657_61e142d1c2ff0c70b0a24.png!small)部分混淆恶意代码

#### 第四层

第四层是最后一层，在去混淆后可以发现这些代码不仅仅是一个 Downloader，还具有其他功能。例如：

  * 通过 `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`进行持久化
  * 通过 `schtasks.exe`配置计划任务

![image.png-21kB](https://image.3001.net/images/20220114/1642152661_61e142d598961b53ca1c3.png!small)计划任务命令

  * 通过 `http://gg1592661.duckdns.org:7924/vre`下载攻击载荷。下载的是 Netwire、Nanocore 和 AsyncRAT 的变种，保存在临时文件夹并执行。
  * 尝试通过 `Alternate Data Stream`隐藏下载来源
  * 通过 `HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProductId`收集设备信息

通过遥测数据，除了 JavaScript 还发现了 Batch 和 VBScript 的脚本。

### Batch Downloader

脚本中包含一个混淆命令，用以执行 PowerShell 下载攻击载荷，本例中通过 Azure Cloud 上的服务器
`13.78.209.105`进行下载。

![image.png-84.8kB](https://image.3001.net/images/20220114/1642152662_61e142d62f073fa65818e.png!small)Batch
Downloader 示例

### VBS Downloader

脚本通过 PowerShell 命令连接到服务器，服务器部署在 AWS EC2 上的 `52.27.15.250`。

![image.png-85.6kB](https://image.3001.net/images/20220114/1642152662_61e142d6c8c7a19721d91.png!small)VBScript
Downloader 示例

### PowerShell Dropper

在 Azure 的服务器上发现了一个使用 HCrypt 构建的 PowerShell 脚本。该脚本会在失陷主机上下载并运行 AsyncRAT
的变种，类似的程序也被趋势科技的研究人员在名为 `Water Basilisk`的攻击中发现。

![image.png-116.9kB](https://image.3001.net/images/20220114/1642152663_61e142d787a34ca8a16ab.png!small)PowerShell
Droper 示例

去混淆后的数据就是二进制文件本身。这个包含 Payload 的字符串，连同一个包含注入 .NET 程序 DLL 模块的字符串，一同被传递给函数 H2
转换为二进制字节数组。

![image.png-118.9kB](https://image.3001.net/images/20220114/1642152664_61e142d84bec465eacfc9.png!small)去混淆注入

这个数组将会被加载注入：

![image.png-227.9kB](https://image.3001.net/images/20220114/1642152665_61e142d91e74976eea62a.png!small)去混淆
PowerShell 命令

脚本会尝试启动进程 `aspnet_compiler.exe`并注入 Payload 执行。样本连接的 C&C 服务器是
`yuri101.duckdns.org`，部署在 `64.188.16.134`。

![image.png-118.9kB](https://image.3001.net/images/20220114/1642152666_61e142da114b55af3b060.png!small)PowerShell
感染链

## 攻击基础设施

攻击者维护了一个分布式攻击基础设施，包括下载服务器、C&C 服务器和恶意域名，下载服务器利用 Microsoft Azure 或 AWS 的云服务。

利用的 Azure 云服务包括：

  * 13.78.209.105 在美国西部区域，FQDN 名称为 `GOOGLE`
  * 23.102.1.5 在北欧区域，并启用了 SMB 身份验证
  * 40.85.140.7 在北欧区域
  * 52.150.26.35 在美国东部区域，FQDN 为 `spinxamp`
  * 13.82.65.56 在美国东部区域
  * 137.135.65.29 在美国东部区域，FQDN 为 `sj-2nd`并启用了 SMB 身份验证

利用 AWS 云服务是 `52.27.15.250`，FQDN 为 `ec2-52-27-15-250.us-west-2.compute.amazonaws.com`，但不确定此实例的操作系统。

一些下载服务器运行的是 Apache 服务器：

![image.png-174.2kB](https://image.3001.net/images/20220114/1642152666_61e142daee13e32f4ff06.png!small)开放目录

每个远控木马都根据配置文件连接对应的 C&C 服务器，IP 地址如下所示：

> 103.151.123.194
>
> 185.249.196.175
>
> 64.188.16.134

恶意域名如下所示：

> asyncmoney.duckdns.org
>
> nwire733.duckdns.org
>
> mback5338.duckdns.org
>
> yuri101.duckdns.org

## 恶意域名

攻击者利用免费的动态 DNS 服务 DuckDNS 创建恶意域名，一些域名绑定在 Azure Cloud 上的服务器，另一些域名绑定在 C&C 服务器上。

> gg1592661.duckdns.org
>
> btime1624.duckdns.org
>
> justinalwhitedd554.duckdns.org
>
> wz303811.duckdns.org
>
> js1994.duckdns.org
>
> backu4734.duckdns.org
>
> www.backu4734.duckdns.org
>
> mback5338.duckdns.org
>
> nwire733.duckdns.org
>
> asyncmoney.duckdns.org
>
> nanoboss.duckdns.org
>
> asyncspread.duckdns.org
>
> tdeasy.duckdns.org
>
> dingspread.duckdns.org
>
> asyncpcc.duckdns.org
>
> jw9428875.duckdns.org
>
> meunknown.duckdns.org
>
> yuri101.duckdns.org

从域名请求来看，攻击行动应该是从 2021 年 10 月开始的。

![image.png-150.8kB](https://image.3001.net/images/20220114/1642152667_61e142dbad22f29168760.png!small)gg1592661.duckdns.org
的 DNS 请求

## 受害者

通过遥测数据，受害者主要来自美国、加拿大、意大利和新加坡，少量分布在西班牙和韩国。

![image.png-290.4kB](https://image.3001.net/images/20220114/1642152668_61e142dc5a41f1117b27e.png!small)受害者分布

## 结论

攻击者正在积极利用云服务构建自己的攻击基础设施，研究发现 Nanocore、Netwire 和 AsyncRAT
就正在这么做。攻击通过钓鱼邮件进行传播，电子邮件仍然是需要防范的重点位置。

## IOC

> 13.78.209.105  
> 13.82.65.56  
> 103.151.123.194  
> 194.156.90.26  
> 52.27.15.250  
> 23.102.1.5  
> 137.135.65.29  
> 40.85.140.7  
> 52.150.26.35  
> gg1592661.duckdns.org  
> btime1624.duckdns.org  
> justinalwhitedd554.duckdns.org  
> wz303811.duckdns.org  
> js1994.duckdns.org  
> backu4734.duckdns.org  
> www.backu4734.duckdns.org  
> mback5338.duckdns.org  
> nwire733.duckdns.org  
> asyncmoney.duckdns.org  
> nanoboss.duckdns.org  
> tdeasy.duckdns.org  
> dingspread.duckdns.org  
> asyncspread.duckdns.org  
> jw9428875.duckdns.org  
> meunknown.duckdns.org  
> asyncpcc.duckdns.org  
> yuri101.duckdns.org  
> hxxp://13.78.209.105/  
> hxxp://13.78.209.105/b/  
> hxxp://13.78.209.105/b/7632JUST.exe  
> hxxp://13.78.209.105/b/7632just.exe/  
> hxxp://13.78.209.105/b/8903mback.exe  
> hxxp://13.78.209.105/B/8903MBACK.exe  
> hxxp://13.78.209.105/B/AsyncClient7842.exe  
> hxxp://13.78.209.105/B/Host.exe  
> hxxp://13.78.209.105/D/Servers/  
> hxxp://13.78.209.105/D/Servers/7632JUST.js  
> hxxp://13.78.209.105/d/servers/8093mm.exe  
> hxxp://13.78.209.105/D/Servers/AsyncClient.exe  
> hxxp://13.78.209.105/d/servers/hostkfkk.exe  
> hxxp://13.78.209.105/D/Servers/Netwire_prevent.exe  
> hxxp://13.78.209.105/d/servers/netwire_prevent.exe  
> hxxp://13.78.209.105/E  
> hxxp://13.78.209.105/E/AsyncClient6121.exe  
> hxxp://13.78.209.105/E/ClientDC.exe  
> hxxp://13.78.209.105/E/Er.txt  
> hxxp://13.78.209.105/E/nano6129.exe  
> hxxp://13.78.209.105/E/New%20folder/7632.exe  
> hxxp://13.78.209.105/E/New%20folder/8903.exe  
> hxxp://13.78.209.105/E/New%20folder/Async7842.exe  
> hxxp://13.78.209.105/E/New%20folder/Host.exe  
> hxxp://btime1624.duckdns.org:7923/  
> hxxp://btime1624.duckdns.org:7923/Vre  
> hxxp://btime1624.duckdns.org/  
> hxxp://btime1624.duckdns.org/B  
> hxxp://btime1624.duckdns.org/b/7632just.exe  
> hxxp://btime1624.duckdns.org/B/7632JUST.exe/  
> hxxp://btime1624.duckdns.org/b/8903mback.exe  
> hxxp://btime1624.duckdns.org/B/8903MBACK.exe/  
> hxxp://btime1624.duckdns.org/B/Host.exe  
> hxxp://btime1624.duckdns.org/D/Servers/  
> hxxp://btime1624.duckdns.org/D/Servers/7632KL.exe  
> hxxp://btime1624.duckdns.org/d/servers/8093mm.exe  
> hxxp://btime1624.duckdns.org/d/servers/asyncclient.exe  
> hxxp://btime1624.duckdns.org/d/servers/hostkfkk.exe  
> hxxp://btime1624.duckdns.org/D/Servers/HostKfkk.exe  
> hxxp://btime1624.duckdns.org/D/Servers/Netwire_prevent.exe  
> hxxp://btime1624.duckdns.org/e/asyncclient6121.exe  
> hxxp://btime1624.duckdns.org/E/ClientDC.exe  
> hxxp://btime1624.duckdns.org/E/New%20folder/7632.exe  
> hxxp://btime1624.duckdns.org/E/New%20folder/8903.exe  
> hxxp://btime1624.duckdns.org/e/new%20folder/async7842.exe  
> hxxp://btime1624.duckdns.org/E/New%20folder/Async7842.exe  
> hxxp://btime1624.duckdns.org/E/New%20folder/Host.exe  
> hxxp://gg1592661.duckdns.org/  
> hxxp://gg1592661.duckdns.org/B/  
> hxxp://gg1592661.duckdns.org/b/  
> hxxp://gg1592661.duckdns.org/B/7632JUST.exe  
> hxxp://gg1592661.duckdns.org/b/7632just.exe  
> hxxp://gg1592661.duckdns.org/B/8903MBACK.exe  
> hxxp://gg1592661.duckdns.org/b/8903mback.exe  
> hxxp://gg1592661.duckdns.org/B/AsyncClient7842.exe  
> hxxp://gg1592661.duckdns.org/b/asyncclient7842.exe  
> hxxp://gg1592661.duckdns.org/b/Host.exe  
> hxxp://gg1592661.duckdns.org/b/host.exe  
> hxxp://gg1592661.duckdns.org/D/Servers/  
> hxxp://gg1592661.duckdns.org/d/servers/7632kl.exe  
> hxxp://gg1592661.duckdns.org/D/Servers/8093mm.exe  
> hxxp://gg1592661.duckdns.org/D/Servers/AsyncClient.exe  
> hxxp://gg1592661.duckdns.org/D/Servers/HostKfkk.exe  
> hxxp://gg1592661.duckdns.org/D/Servers/Netwire_prevent.exe  
> hxxp://gg1592661.duckdns.org/d/servers/netwire_prevent.exe  
> hxxp://gg1592661.duckdns.org/E  
> hxxp://gg1592661.duckdns.org/E/ClientDC.exe  
> hxxp://gg1592661.duckdns.org/E/nano6129.exe  
> hxxp://gg1592661.duckdns.org/E/New%20folder/7632.exe  
> hxxp://gg1592661.duckdns.org/E/New%20folder/8903.exe  
> hxxp://gg1592661.duckdns.org/E/New%20folder/Async7842.exe  
> hxxp://gg1592661.duckdns.org/e/new%20folder/async7842.exe  
> hxxp://gg1592661.duckdns.org/Vre  
> hxxps://btime1624.duckdns.org/  
> hxxps://btime1624.duckdns.org/B/Host.exe/  
> hxxps://gg1592661.duckdns.org/  
> hxxps://gg1592661.duckdns.org/B/AsyncClient7842.exe  
> hxxps://gg1592661.duckdns.org/C  
> hxxps://gg1592661.duckdns.org/D/Servers/  
> hxxps://gg1592661.duckdns.org/E/AsyncClient6121.exe  
> hxxp://194.156.90.26:8012/Vre  
> hxxp://52.27.15.250/A/behdhdjdj.txt  
> hxxp://52.27.15.250/A/SJJS.txt  
> hxxp://52.27.15.250/A/HSHSJSJD.txt  
> hxxp://nanoboss.duckdns.org/  
> hxxp://nanoboss.duckdns.org/  
> hxxp://23.102.1.5/  
> hxxp://asyncspread.duckdns.org/  
> hxxp://tdeasy.duckdns.org/Vre  
> tcp://asyncspread.duckdns.org:6121/  
> tcp://nanoboss.duckdns.org:6129/  
> hxxp://23.102.1.5:6129/  
> hxxp://tdeasy.duckdns.org/  
> hxxps://tdeasy.duckdns.org/  
> hxxp://tdeasy.duckdns.org:6128/  
> hxxp://tdeasy.duckdns.org:6128/Vre  
> hxxp://dingspread.duckdns.org/vre/*  
> hxxp://dingspread.duckdns.org:6130/  
> hxxp://dingspread.duckdns.org:6130/Vre  
> hxxp://jw9428875.duckdns.org:1991/Vre  
> hxxp://meunknown.duckdns.org/  
> hxxp://52.150.26.35/bypass.txt  
> hxxp://52.150.26.35/PE.txt  
> hxxp://52.150.26.35/pe.txt  
> hxxp://40.85.140.7/bypass.txt  
> hxxp://40.85.140.7/PE.txt  
> hxxp://40.85.140.7/pe.txt  
> hxxp://137.135.65.29/bypass.txt  
> hxxp://137.135.65.29/PE.txt  
> hxxp://137.135.65.29/pe.txt  
> 5d64794cf6025bccda9ea93926894bc49599573a8f59905cdb394e5137496150  
> 44f5442b45a48365cdd6c7d1f16ba19dea4fb1865ea4e9178c5758929f59d0f7  
> 48951f6847400dd39cba2f5ba0376e08bb4b7e36a4c3567792289734758b7bf9  
> 5d7a0823b291315c81e35ed0c7ca7c81c6595c7ca9e5ebf0f56993a02d77c1f2  
> e3f46470aa9ef52628f741e07db33a6af854693ae2a761d397bf87fbfbe687c9  
> 5518f5e20b27a4b10ebc7abce37c733ab532354b5db6aed7edf19c25caba2ff3  
> 8ffde50491ef1cfc93f417b731186a08fb6c3e5aad21f131a60b87936bd3f850  
> a5d5de41b6546981f2284c07aa2fe17ac0b15727fb96fdff33db020a0826810e  
> bbceba6fd06b01bd5c69ccab1ea106189455e1e85e577e278f9f362940b5442c  
> 959484bfe98d39321a877e976a7cde13c9e2d0667a155dda17aeade58b68391c  
> 7257729274b6ab5c1a605900fa40b2a76f386b3dbb3c0f4ab29e85b780eaef73  
> eae81605341641ad10c18ab60b79339617f0219abaa1ab5ee7883fc9d429b885  
> d42e5f2e60b39e2aca3dd09a4dd5803a04b33821e6da8808ef9ef450d6771e30  
> be02ba931ff61e5fb9ea332d41cf347d12fc84b4557ad28d82d2b2551406e4da  
> bffb4b88ef53beb49ba2af08212870b203a29c7fcd1c8f02e0a905e71a8af6df  
> 574b348f67921ce34f660afe2ff75d0538bd5ea203739a77479dba7f026f0476  
> 6b4401690cb0a07ee98ff3c5fc351b20c6e0a4ba7474c6ad858e5dc69a60b36f  
> 843c5f7a818681e3df212c80515cdce0bd56c6e178412736b8a22b15ebb35435  
> 2605a1cb2b510612119fdb0e62b543d035ad4f3c873d0f5a7aa3291968c50bc8  
> ff66be4a8df7bd09427a53d2983e693489fbe494edd0244053b29b9f048df136  
> 988c1b9c99f74739edaf4e80ecaba04407e0ca7284f3dbd13c87a506bf0e97b7  
> 4b61697d61a8835a503f2ea6c202b338bde721644dc3ec3e41131d910c657545  
> dfdb008304c3c2a5ec1528fe113e26088b6118c27e27e5d456ff39d300076451  
> c8c69f36f89061f4ce86b108c0ff12ade49d665eace2d60ba179a2341bd54c40  
> 28ef1f6f0d8350a3fda0f604089288233d169946fca868c074fc16541b140055  
> 2605a1cb2b510612119fdb0e62b543d035ad4f3c873d0f5a7aa3291968c50bc8  
> b7f3d1dd2aa804eb498480b7a3b03ea003efb665005e844e51be5b8ab9dc8e79  
> 68106918876232b746129b1161c3ac81914672776522f722062945f55166ba68  
> 1dd6d37553168fa3929f5eaa5b2b0505aae5897809b532dd0b12eae8ffd8957f  
> 1490f6303a675ded86c22841f87868c6f0867e922671e0426f499e46a72060d2  
> 98e3e47c326aeb2e6001efca84737ae0ef78ce3576912aebfcbe05105db3f72a  
> c8dec500839b3698755d9304442aa9f3516218b7c6340e2b1202dbe83089ab1d

## 参考来源

> [CiscoTalos](https://blog.talosintelligence.com/2022/01/nanocore-netwire-> and-asyncrat-spreading.html)

