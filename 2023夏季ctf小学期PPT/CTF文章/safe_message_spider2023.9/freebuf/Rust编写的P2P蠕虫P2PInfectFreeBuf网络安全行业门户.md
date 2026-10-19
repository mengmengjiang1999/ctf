近日研究人员发现了一个新型 P2P 蠕虫，将其命名为 P2PInfect。该蠕虫采用 Rust 语言编写，以 Redis
服务为攻击目标。研究人员在超过三十万个对外暴露的 Redis 中发现了 934 个可能受到该蠕虫影响的实例。

P2PInfect 利用 Lua 沙盒逃逸漏洞 CVE-2022-0543 进行攻击，该漏洞 CVSS 评分为 10 分。P2PInfect
可能是攻击者利用该漏洞攻击最典型的一个例子。研究人员认为，P2PInfect 只是攻击者进行潜在攻击的第一阶段。尽管样本有命名为 miner
的，但并未发现实际的挖矿行为。

## P2P 蠕虫

研究人员在 2023 年 7 月 11 日发现了第一个 P2PInfect 样本。命名为 P2PInfect 是由于攻击者的目录中反复出现该词汇，如下所示。

![image.png-205.5kB](https://image.3001.net/images/20230802/1690988240_64ca6ed07e2fe086f714d.png!small)项目路径结构

所有发现的 P2PInfect 样本都是 Rust 开发的，这使得攻击者可以跨平台感染 Linux 与 Windows 系统上的 Redis
实例（请注意，Redis 并不正式支持 Windows 操作系统）。

该蠕虫利用 Lua 沙盒逃逸漏洞 CVE-2022-0543 对 Redis 进行攻击。尽管最初该漏洞被 Muhstik 僵尸网络所使用，但
P2PInfect 与 Muhstik 并无关系。

感染成功后，失陷主机会与 P2P 网络进行通信。在节点间传递各种恶意样本文件，并且对外扫描 Redis 服务。

传统利用定时任务入侵 Redis 的方式，在容器下并不可行。而 P2PInfect 使用了 CVE-2022-0543 漏洞，尽可能覆盖更多场景。

## CVE-2022-0543

P2PInfect 主要依靠 Lua 沙盒逃逸漏洞（CVE-2022-0543） 针对 Redis 服务进行攻击。Redis
是一个被攻击者经常利用的服务，TeamTNT、WatchDog 与 Kinsing、8220 等团伙都会针对 Redis 进行攻击。

CVE-2022-0543 是 Lua 库存在的漏洞，影响 Debian Linux 包管理器安装的 Redis。所以，只有 Debian 系操作系统的
Redis 用户会受到影响。由于限定了操作系统与 Redis 组件才能攻击，P2PInfect 的利用方式十分复杂。如下所示：

![image.png-335kB](https://image.3001.net/images/20230802/1690988241_64ca6ed12bb44ad0b1ec4.png!small)Debain
系统中的漏洞利用

上图显示了该漏洞如何被武器化利用的。首先通过 /dev/tcp 网络请求利用 60100 端口连接到 C&C 服务器。端口 60100 是
P2PInfect 用于维护与 C&C 服务器通信的端口之一。恶意代码通过 GET 请求获取名为 linux 的核心样本文件。

## 网络通信

P2PInfect 使用 P2P 网络进行恶意软件分发，失陷主机会与 P2P 网络建立连接并下载恶意样本。如下所示，通过 GET /linux
请求核心样本：

![image.png-526.6kB](https://image.3001.net/images/20230802/1690988242_64ca6ed2743e9041b1f6a.png!small)下载样本文件

Linux 平台下与 Windows 平台下的 P2PIfect 样本都以相同的方式进行通信。下载的多个恶意样本如下所示：

![image.png-120.4kB](https://image.3001.net/images/20230802/1690988243_64ca6ed348b4dc54c33cd.png!small)恶意样本列表

核心样本执行完成，将会开始扫描其他主机。主要扫描的是对外暴露的 Redis 服务，也对 SSH 服务进行了扫描。

## 节点通信

Dropper 使用 TLS 1.3 与已知节点列表中的其他 P2P 节点进行通信。失陷主机向 P2P 网络发送包含已知节点的 JSON 请求时，C&C
基础设施就会更新。节点更新如下所示：

![image.png-119.7kB](https://image.3001.net/images/20230802/1690988243_64ca6ed3e29e27bc8a7f6.png!small)P2P
节点更新

其中，XXXX 为当前节点 IP 或者新发现的节点 IP。

## 扫描行为

失陷主机会对外扫描 SSH 服务，P2PInfect 会在随机网络范围内进行扫描：

![image.png-543.3kB](https://image.3001.net/images/20230802/1690988244_64ca6ed49176268cefd44.png!small)扫描
SSH 服务

除了 SSH 服务，Redis 服务也在扫描的范围内：

![image.png-536.5kB](https://image.3001.net/images/20230802/1690988245_64ca6ed566532f908b251.png!small)扫描
Redis 服务

## P2PInfect 的其他特征

收集到的 P2PInfect 样本有些是 UPX 加壳的，后续阶段的其他恶意样本则没有经过 UPX 加壳。

第一个 Dropper 运行后，解密配置信息获取有关 P2P 网络其他节点的信息。其 P2P 通信端口是可变的，这对检查技术的缓解是十分有效的。

![image.png-51kB](https://image.3001.net/images/20230802/1690988246_64ca6ed6451cf7bf1cfc9.png!small)可变端口情况

研究人员发现所有样本都是 Rust 开发的，其中有部分符号反映了恶意软件开发者的项目结构。例如，Windows
执行主要代码中泄露了项目名称以及攻击者使用的文件目录。

![image.png-285.2kB](https://image.3001.net/images/20230802/1690988246_64ca6ed6cb097b5d64ab5.png!small)样本代码

还发现了攻击者使用的 PowerShell 脚本，旨在维护失陷主机与 P2P 网络间的通信。该脚本利用 encode 命令混淆建立通信的代码。

![image.png-85.6kB](https://image.3001.net/images/20230802/1690988247_64ca6ed7daeaed04507d4.png!small)PowerShell
命令

PowerShell 命令执行首先会修改系统防火墙，阻止对 Redis
服务的访问。随后，脚本打开一个端口让攻击者可以访问。这是一种持久化方法，维持攻击者对失陷主机的访问。

![image.png-523.8kB](https://image.3001.net/images/20230802/1690988248_64ca6ed8c969c50b28f68.png!small)脚本代码

解码后的 PowerShell 代码中，可见对防火墙进行了如下修改：

  * 对等端口为 60102（可变端口）
  * Redis 的 6379 端口只能连接 C&C 服务器的 IP
  * 防火墙规则名为 Microsoft Sync

## 监控进程

在 Windows 中感染时，一个名为 Monitor 的进程吸引了分析人员的注意。Monitor 进程主要维持 P2PInfect
进程在失陷主机上的运行。该进程主要通过 C:\Users\username\AppData\Local\Temp\cmd.exe 获取系统运行的进程：

![image.png-262.7kB](https://image.3001.net/images/20230802/1690988250_64ca6edae1bc2aab9e6e7.png!small)进程树

启动 cmd.exe 后，P2PInfect 就会通过 P2P 网络下载最新的样本文件，并随机命名到同一原始文件夹中。然后，样本将删除加密配置文件。

![image.png-22.9kB](https://image.3001.net/images/20230802/1690988251_64ca6edbad7ed78c9bda3.png!small)随机文件命名

下载最新版本的 P2PInfect 样本后，随即启动扫描行为。最初的 Dropper 会尝试将自身删除：

![image.png-37.8kB](https://image.3001.net/images/20230802/1690988252_64ca6edc2c5ba021b8a7d.png!small)删除文件

## 结论

P2PInfect 蠕虫是很成熟的，运用了多种现代开发技巧。Rust 语言的使用也为攻击者提供了更大的灵活性，蠕虫可以跨系统快速传播。

分析人员经过统计，发现其 P2P 节点的数量在快速增长。尚且没有明确的数字确认 P2PInfect 规模增长的速度。

## IOC

> 35.183.81[.]182  
> 66.154.127[.]38  
> 66.154.127[.]39  
> 8.218.44[.]75  
> 97.107.96[.]14  
> 88601359222a47671ea6f010a670a35347214d8592bceaf9d2e8d1b303fe26d7  
> b1fab9d92a29ca7e8c0b0c4c45f759adf69b7387da9aebb1d1e90ea9ab7de76c  
> 68eaccf15a96fdc9a4961daffec5e42878b5924c3c72d6e7d7a9b143ba2bbfa9  
> 89be7d1d2526c22f127c9351c0b9eafccd811e617939e029b757db66dadc8f93

## 参考来源

> [Unit42](https://unit42.paloaltonetworks.com/peer-to-peer-worm-p2pinfect/)

