今年早些时候，Apache HTTP
服务器被披露存在安全漏洞（CVE-2021-41773），攻击者可以利用该漏洞进行远程命令执行。官方给出的修复方案并不完全，在发现了可以绕过后该漏洞编码再次确认为
CVE-2021-42013。

在对滥用该漏洞的恶意样本进行分析时，研究人员发现了多个同类的漏洞利用，这些攻击与挖掘门罗币有关。攻击者将恶意软件部署在 GitHub 和 Netlify
中，分析人员已经将滥用行为通知官方删除了账户。

## 漏洞情况

通过蜜罐分析，攻击者利用 2020 年和 2021 年披露的漏洞针对多个产品进行挖矿活动，具体如下所示。

> Atlassian Confluence（CVE-2021-26084 和 CVE-2021-26085）
>
> F5 BIG-IP（CVE-2020-5902 和 CVE-2021-22986）
>
> VMware vCenter（CVE-2021-22005、CVE-2021-21985、CVE-2021-21972 和
> CVE-2021-21973）
>
> Oracle WebLogic Server（CVE-2020-14882、CVE-2020-14750 和 CVE-2020-14883）
>
> Apache HTTP Server（CVE-2021-40438、CVE-2021-41773 和 CVE-2021-42013）

![image.png-150.7kB](https://image.3001.net/images/20211208/1638964857_61b09e7985eb9b8f5bf3d.png!small)

相关漏洞利用的分类统计

所有漏洞都有相关的 POC 被公开披露，查看其中一个门罗币钱包可见其攻击势头并未减缓。

![image.png-124.5kB](https://image.3001.net/images/20211208/1638964880_61b09e900ea976b48567c.png!small)

门罗币钱包收入信息

## Windows 平台

挖矿程序在 Windows 和 Linux 平台上都可以工作。尽管它使用的漏洞和攻击基础设施有所不同，但脚本仍然适用。分析发现 Netlify 和
GitHub 被用作部署恶意脚本的服务器，该脚本下载后被重命名为临时文件，确认在后台成功运行后被删除。

![image.png-119.3kB](https://image.3001.net/images/20211208/1638964896_61b09ea0cbd6ffac47b96.png!small)

Windows 平台攻击过程

脚本 c3.bat 是基于 GitHub 开源项目 [Monero-mining](https://github.com/C3Pool)的修改版。

![image.png-110.4kB](https://image.3001.net/images/20211208/1638964912_61b09eb0868ef06f3dc74.png!small)

脚本部分内容

在检查当前会话是否具有管理员权限后，计算门罗币钱包地址的长度。如果长度不是 95 和 106 个字符，脚本正常退出。长度相等的话，则跳转到
WALLET_LEN_OK 语句。

![image.png-162.1kB](https://image.3001.net/images/20211208/1638964926_61b09ebe61e62f2881e92.png!small)

判断钱包地址长度

脚本文件还会进行其他检查，如是否定义 USERPROFILE 环境变量；wmic、powershell、find、findstr 和 tasklist
等程序是否可用。

![image.png-244.6kB](https://image.3001.net/images/20211208/1638964949_61b09ed558f3856e3a955.png!small)

检查命令是否可用

![image.png-503.8kB](https://image.3001.net/images/20211208/1638964966_61b09ee6a33ddb9fb5783.png!small)

检查系统相关信息

利用 wmic 进一步枚举系统的其他信息，如处理器数量、缓存大小等。这些信息后续用于计算门罗币挖矿速率，不同速率时使用不同的端口。

![image.png-428.7kB](https://image.3001.net/images/20211208/1638964986_61b09efa25af59e24ac8a.png!small)

决定挖矿的速率

通过攻击者控制的 GitHub 仓库下载压缩的挖矿程序（c3.zip）并使用 PowerShell 解压缩下载的文件。在解压失败的情况下，下载 7z
来解压再删除下载的文件（7za.exe 和 c3.zip）。

![image.png-837.5kB](https://image.3001.net/images/20211208/1638965006_61b09f0ea052e17c98852.png!small)

下载后续恶意软件

该脚本还会下载最新版本的 XMRig，解压后删除 7z 文件和 XMRig 文件。成功安装挖矿程序后，使用 PowerShell 修改配置文件。

![image.png-480.1kB](https://image.3001.net/images/20211208/1638965185_61b09fc12ba8df05b10fc.png!small)

安装挖矿程序

![image.png-418.5kB](https://image.3001.net/images/20211208/1638965207_61b09fd7e3b401f66e64b.png!small)

修改配置文件

如果挖矿程序（c3.exe）正在运行，则跳转执行 ALREADY_RUNNING。如果没有运行，则使用 start 启动执行。

如果用户具有管理权限，则跳转执行 ADMIN_MINER_SETUP。如果没有权限，进行持久化后使用配置文件执行 c3pool XMR 挖矿程序。

![image.png-362.9kB](https://image.3001.net/images/20211208/1638965226_61b09feac78ae98620937.png!small)

配置持久化

使用 Non-Sucking Service Manager（NSSM）将应用程序安装为服务，用户可以使用它指定对用户定义文件的日志记录。

![image.png-349.4kB](https://image.3001.net/images/20211208/1638965244_61b09ffceaf108ca3899f.png!small)

安装并启动服务

## Linux 平台

Shell 脚本以无限循环开始，清除在失陷主机中发现的挖矿程序，例如 kinsing、kdevtmpfsi、pty86 和 .javae。

![image.png-1032.5kB](https://image.3001.net/images/20211208/1638965259_61b0a00bd9f9fe310ae05.png!small)

清除其他挖矿程序

清除竞争对手后，修改 /var/spool/cron/root
的文件属性，再将特定程序（java、redis、weblogic、mongod、mysql、oracle、tomcat、grep、postgres、confluence、awk
和 aux ）外、高 CPU 占用率的进程终止。

![image.png-191.9kB](https://image.3001.net/images/20211208/1638965279_61b0a01f73a08cc1cee22.png!small)

终止符合条件的进程

每三十秒重复一次，调用函数 func1。在 func1 函数中，检查进程 java.xnk 的 CPU 占用率大于等于 60% 就将进程 ID 配置为变量
p。如果变量为空，则终止进程并创建三个目录：

> /var/tmp/java.xnk
>
> /var/lock/java.xnk
>
> /tmp/java.xnk

![image.png-372.4kB](https://image.3001.net/images/20211208/1638965298_61b0a03233978ac5cf524.png!small)

进程处理

在路径 $DIR 中检查文件 java.xnk.bionic，如果文件不存在则使用 wget 下载 bionic 挖矿程序和
config.json（挖矿配置程序）。为下载的二进制文件分配可执行权限，在维持后台执行。

类似的，重复下载并执行以下文件：

> focal as java.xnk.focal
>
> freebsd as java.xnk.freebsd
>
> linuxstatic as java.xnk.linux
>
> xenial as java.xnk.xenial
>
> xmr-stak as java.xnk.stak

![image.png-443.3kB](https://image.3001.net/images/20211208/1638965319_61b0a047923104bc272c2.png!small)

执行挖矿程序

## 结论

从失陷情况来看，攻击者将会继续利用这些漏洞攻击存在漏洞的服务器。挖矿程序可以在 Linux 平台和 Windows 平台上进行挖矿，而且攻击者仍然会利用
GitHub 和 Netlify 等平台用作部署渠道。

## IOC

> 3c1a2e702e7079f9d49373049eff5e59fcf35d526b7a157a4a963fbdf9c7c75f  
> 3b5ffd88a9762c68de551e63243fcc0549e3c31784285b312adf59832f7523ab  
> fd7e26f48dfb68284f5acda50eedb8e9a964fb8b8a1dbb2c1555d431da8182e0  
> a025a8b424c23856c42dbebcb67ff7c60c6cfd13aa12fcecb15679b98b3ba94d  
> 4fc7113ed150895587635fa58b8be66a32f2d41b06807ac8a9f1898dd1ee6b0c  
> 1489c404a110149b66476e0f41317770f0291da64a0d4b39f28900ccaf4d30f2  
> dd303c2644c2a58cf466a19f7c801aeae43a63d4efd56707f0dd531439d8dafd  
> b8a146284e8abf867ed86ff6cc4ee44648e47c7e857d5d2e5e52219c4b43f935  
> 93167030a5bb32e8d777f04a0853b2a55a0ae91a634afbcd55e2c981853d5506  
> 428340a0695393a0cec55513e700a479e252d9b034f27f80a29da3ac99afa459  
> 240fe01d9fcce5aae311e906b8311a1975f8c1431b83618f3d11aeaff10aede3  
> 61c0449a48cf9351f157d89deff88bd4df2ab5c1091b3504741f6c62274b099e  
> 9691bf237d879299984abb23b25ffb51a0f00567a364899466e1ad93694c0186  
> aaee6e01f4192caea86645bea741d85c240083b55341e47a206176df1892e740  
> feb4541172610b742552d3ee4bc9b114e9bf0d11dfff153b452e03804cd0f453  
> 747ceb6c37bae5670b0c469c998c66e58b4ec310ab8ddf3abc0c205fb5d15f1c  
> 5aa0da717d2e88682203f2831bfb550ed8530d98bed9232a2a3a1683ba11e052  
> fca6e56e74f94b29674528a8c4e82898f1ca7dc62b4a7d50c175464f9065c343  
> 4d1e20ef6d88436a7246e79987e71238021dbbbb80a3bc83c0ef814dfeda5c2e  
> cd291d2b3933ab914eed36d3c9c0200ae864fb4a5d29fb5be54f07c3d30bebdb  
> 62f854be8c9876e84a920231bdf7bbe0757beb609486aa3ea34df34da6b93b09  
> 73ef742834dfa72668fc423bd43204456c2f4effef5a99a1beeeff059ea64189  
> e94f04e2822fc7e2406cf2ad8f0d1e0359a13647cf26a8f31b2b83a033c3df94  
> 3b0a31a6889d129324d922b8861a6f06101ea9bc6a89bd7e7e2dd691b6247367  
> 73a7aa23e68c0bd6bd6960327cf0a24217544a913f83b85cedf59bdc0856b8e6  
> c5d9345a8a49f1109c2fcd1c649ceaa94421e6c3804284fca1f6c891dbc0869d  
> 7f2b0f01547d7d43c8bd33206faf78d6500a7f6f2a9e6612c507b220de5a08a9  
> b3215074ddb18e43771a51f3d3c8c49571bbf69b33b8bbbf2cab4559caa1ae6a  
> nervous-hodgkin-5c3bb4.netlify.app  
> heuristic-hermann-392016.netlify.app  
> amazing-nightingale-3617e1.netlify.app

## 参考来源

> [TrendMicro](https://www.trendmicro.com/en_us/research/21/l/vulnerabilities-> exploited-for-monero-mining-malware-delivered-via-gitHub-netlify.html)

