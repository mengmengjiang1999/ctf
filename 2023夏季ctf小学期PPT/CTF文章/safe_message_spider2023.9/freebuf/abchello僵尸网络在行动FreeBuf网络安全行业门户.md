Lacework Labs 12月初在蜜罐中观察到一个 **使用 Golang 编写的暴力破解程序，分析确认该组件是 abc-hello 僵尸网络开发**
，该僵尸网络还 **利用 Weblogic 漏洞和其他模块来爆破 SSH、Redis、PostgreSQL** 。

## 背景

近年来，Golang 恶意软件的使用量显著增长，在云上的攻击尤为明显。Golang 在恶意软件中越来越普及，一方面是因为 Golang
在跨平台编译上的优势，检出率相对较低，另一方面是 Golang 在网络任务上的性能强劲。

通过对蜜罐数据的分析，abc-hello 是近四个月内大部分 WebLogic 漏洞攻击的罪魁祸首。其中，
**大量攻击流量位于中国，这可能说明僵尸网络在位于中国的云服务器上取得了巨大的成功** 。

## 传播

通过静态分析，发现恶意软件的路径中都包含 abc-hello，且开发了很多扫描、爆破的插件。例如，插件 plugin.Weblogic14882Check
就是 CVE-2021-14882 的 Exploit。

> abc-hello/plugin.SetConfig
>
> abc-hello/plugin.Scan
>
> abc-hello/plugin.try
>
> abc-hello/plugin.pluginRun.func2
>
> abc-hello/plugin/plugin.go
>
> abc-hello/plugin.Regist
>
> abc-hello/ plugin.SshPassCheck
>
> abc-hello/plugin.try.func1
>
> abc-hello/plugin.PostgresPassCheck
>
> abc-hello/plugin.pluginRun
>
> abc-hello/plugin.RedisPassCheck
>
> abc-hello/plugin.Check
>
> abc-hello/plugin.CheckErrs
>
> abc-hello /plugin.StartScan
>
> abc-hello/plugin.pluginRun.func1
>
> abc-hello/plugin.Weblogic14882Check
>
> abc-hello/plugin.init.0
>
> abc-hello/plugin.StartScan.func1

abc-hello 僵尸网络主要通过暴力破解和漏洞利用进行传播。

第一阶段的恶意软件是一个名为 ff.sh 的恶意 bash 脚本，下载其他恶意组件（如 XMRig 挖矿进程）。脚本会安装 abc-hello
恶意软件、配置名为 logger 的用户并复制 SSH 密钥。脚本中注释包含 cloudResetPwdUpdateAgent，是 Huwaii 云计算为
OpenStack 架构提供的密码重置工具。

ff.sh 将 abc-hello 写入 /etc/iptablesupdate，还会以 /usr/bin/dockerlogger 的形式运行自身的副本。

![image.png-209.5kB](https://image.3001.net/images/20211206/1638776213_61adbd951a12774bf16f9.png!small)

dockerlogger相关的IP地址

## 流量分析

通过对 16 分钟的 abc-hello 流量分析，十六分钟内恶意软件尝试连接超过 7.4 万个 IP 地址，共计 423MB。

 **恶意软件首先通过 26800 端口连接到 C &C 服务器，以明文传输受害者的相关上线信息**。

![image.png-119.7kB](https://image.3001.net/images/20211206/1638776240_61adbdb0029e41a728a07.png!small)

上线流量

每五秒发送一次到 /api/getlist 的 POST 请求，C&C 响应两段十六进制 ASCII 值。第一段十六进制 ASCII
值（73746f707c）是 stop，第二段是用于验证的数字签名。

![image.png-112.3kB](https://image.3001.net/images/20211206/1638776262_61adbdc653032bfa114c0.png!small)

POST请求与响应

首先扫描的是失陷主机所在的 B 类子网，程序随后会随机生成公网的 B 类地址（255.255.0.0）再扫描整个子网。在连接的 7.4 万 IP
地址中，2354 台主机在目标端口有服务。

![image.png-22kB](https://image.3001.net/images/20211206/1638776286_61adbdde2708b801fc8c3.png!small)

端口与相关服务

![image.png-141.2kB](https://image.3001.net/images/20211206/1638776307_61adbdf3966af52f2dc09.png!small)

C&C 通信流量

## 内核模块

abc-hello 的一个变种还带有扫描和 DDoS 功能的内核模块，模块复用了
[kdeb](https://github.com/millken/kdev)的开源代码。该开源存储库只有两个分支，传播量可能并不大。自从 2013
年来，项目创建者 millken 一直都很活跃，开发了 140 余个项目，但基本都没有描述文档。

 **millken 编写的代码中 10% 是 Golang 编写的，但暂不清楚其中是否和 abc-hello 的源码有关** 。该用户也写过一个名为
kscan 的扫描程序，还从他人处 fork 了许多和攻击相关的项目库。kscan 库包含一个配置文件，其中包含三个属于 ASN 37963（杭州某公司）的
IP 地址，这也是在蜜罐中观察到的攻击流量的主要来源。

> #!/bin/sh
>
> xl_x64scan1="http://103[.]209.103.16:26800/atk.tar.gz"
>
> xl_x64scan2="http://103[.]209.103.16:26800/atk.tar.gz"
>
>  
>
>
> if [ -x "$(command -v apt-get)" ]; then
>
> export DEBIAN_FRONTEND=noninteractive
>
> apt-get install -y debconf-doc
>
> apt-get install -y build-essential
>
> apt-get install -y make gcc git
>
> fi

根据 Netlab 的跟踪分析，该 DDoS 模块后续被弃用。尽管还需要更多证据才能将 millken 用户和 abc-hello
僵尸网络的运营关联起来，但相关的代码库仍然值得注意。

## 结论

尽管 abc-hello
僵尸网络并不是影响力最大的僵尸网络，但在蜜罐中持续能观察到相关的攻击流量，这说明该僵尸网络的攻击性仍然很强。此外，恶意软件也在不断进化与发展，根据研究人员分析攻击者可能在尝试使用
DGA 和 TOR 来作为 C&C 通信。Golang 已经成为许多暴力破解程序的首选，并且被很多僵尸网络广泛使用。

## IOC

> 4bacbb6a20958b20a0f806b051ae6f6c84ff64fb3da98fb74a143517469bd162
>
> ee06514351644d1a7b5568a6ba202e0451148df3f20e4367ea94625ebcfd3226
>
> 6473ead2efbbe010040f42ef1395c06c9deb7405ca89617d2318a419f90de4cc
>
> f7dc1998c6ea802a9db30a1dfd777e00de09f498ad1266b46ae16c301e4e0f63
>
> 56d677ed192b-5010aa780d09c23b8ee8fdff94d39b20a07c7de76705e5f8c51f
>
> f36d3996245dba06af770d1faf3bc0615e1124fa179ecf2429162abd9df8bbf8
>
> 6b900ff5ffd3ac1e8bc1fe7f921724f3e7f5dacca1dad98996011f70093b1a84
>
> 22b521f8d605635e1082f3f33a993979c37470fe2980956064aa4917ea1b28d5
>
> fc614fb4bda24ae8ca2c44e812d12c0fab6dd7a097472a35dd12ded053ab8474
>
> 3bf2c3f1ed9ad7edcb60802533878b5d74951f48c01b73775224c5d159d631bf
>
> b7fd3d0188966d606fdb24cb3ec471b9c7424799dbba09506bea923cf2bd2e2e
>
> 103.209.103.16
>
> 39.105.1.75
>
> 101.34.114.216
>
> 120.234.32.22
>
> 18.163.28.194
>
> 124.128.200.114
>
> 47.93.11.177
>
> 39.101.174.25
>
> 106.13.18.221
>
> 47.97.5.115

## 参考来源

[Lacework](https://www.lacework.com/blog/abc-botnet-attacks-on-the-rise/)

