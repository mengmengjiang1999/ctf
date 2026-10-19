## 背景

PowerGhost是从2018年被发现使用powershell无文件方式进行攻击感染的挖矿以及DDOS病毒，本次深信服安全团队捕获到其最新样本，其感染方式利用了永恒之蓝，MSSQL爆破，SSH爆破，wmi以及smb爆破远程命令执行等，同时对windows和linux进行攻击，一旦该病毒进入内网，会在内网迅速传播。目前其主要感染地区在广东、浙江、上海以及江苏。

![](https://image.3001.net/images/20191112/1573521016_5dca06788f5db.png!small)

## 详细分析

该病毒母体模块分为2个版本，x86和x64，x86使用antitrojan.ps1，x64使用antivirus.ps1，本次分析x64版本的antivirus.ps1。

![](https://image.3001.net/images/20191112/1573521049_5dca0699bfc29.png!small)

当前病毒版本为1.5。

![](https://image.3001.net/images/20191112/1573521074_5dca06b2e5f2f.png!small)

母体payload分布以及执行图，antivirus.ps1中主要分为3个部分，如下图：

![](https://image.3001.net/images/20191112/1573521215_5dca073f48923.png!small)

第一段payload，开头部分如下：

![](https://image.3001.net/images/20191112/1573521227_5dca074bad7ca.png!small)

Invoke-WmiExec以及Invoke-SmbExec远程命令执行。

![](https://image.3001.net/images/20191112/1573521295_5dca078fb64b7.png!small)

永恒之蓝利用，$sc为shellcode，主要从网上下载恶意脚本进行感染。

![](https://image.3001.net/images/20191112/1573521337_5dca07b90340b.png!small)

![](https://image.3001.net/images/20191112/1573521343_5dca07bfe1eed.png!small)

SSH爆破，加载的SSH模块Rence.SshNet。

![](https://image.3001.net/images/20191112/1573521360_5dca07d038240.png!small)

![](https://image.3001.net/images/20191112/1573521372_5dca07dc0f9c4.png!small)

![](https://image.3001.net/images/20191112/1573521379_5dca07e344956.png!small)

MSSQL爆破。

![](https://image.3001.net/images/20191112/1573521398_5dca07f6e9338.png!small)

![](https://image.3001.net/images/20191112/1573521405_5dca07fdaafc9.png!small)

随着最近网络加密货币升值，会有更多的黑产将注意力转到挖矿，其挖矿流量如下，到目前为止该地址已经赚取了3个币。

![](https://image.3001.net/images/20191112/1573521428_5dca081478679.png!small)

![](https://image.3001.net/images/20191112/1573521442_5dca08228cece.png!small)

Middle部分，一段混淆的代码，主要功能执行第一段payload。

![](https://image.3001.net/images/20191112/1573521460_5dca0834a7a8c.png!small)

![](https://image.3001.net/images/20191112/1573521472_5dca0840ad77b.png!small)

第二段payload，也是混淆过的，部分内容如下。主要创建两个定时任务，更改电源计划，创建netbc的ipsec策略封堵445端口(防止被其他病毒利用)，创建一个wmi持久任务。

![](https://image.3001.net/images/20191112/1573521485_5dca084da7b6c.png!small)

![](https://image.3001.net/images/20191112/1573521497_5dca0859c887b.png!small)

![](https://image.3001.net/images/20191112/1573521504_5dca08600a2a9.png!small)

### Linux部分分析

当PowerGhost成功爆破ssh之后，就会下载shell进行病毒的更一步植入。

![](https://image.3001.net/images/20191112/1573521551_5dca088fb7cc3.png!small)

当前Linux版本为1.2版本，前面进行信息的初始化，声明C2地址和默认下载目录、以及文件hash，文件校验方式等:

> temp_remote_host: 远程地址
>
> sodd_info_arr: DDoS木马
>
> tiktoor_info_arr: brootkit后门
>
> pxe_info_arr: CVE-2016-5195内核提权源码以及程序及其hash
>
> DownloadPath=”/usr/lib/...” 默认下载路径
>
> Ver=1.2 当前版本
>
> Shell_privilege=1 当前shell默认权限
>
> OsType=1 系统类型默认为Centos系列
>
> Verify_method=”md5sum” 下载文件校验方式，默认使用md5

![](https://image.3001.net/images/20191112/1573521585_5dca08b194104.png!small)

![](https://image.3001.net/images/20191112/1573521592_5dca08b8c7acb.png!small)

整个Linux端PowerGhost执行流程如下：

1、进行初始化。

![](https://image.3001.net/images/20191112/1573521609_5dca08c9a39de.png!small)

2、检测执行参数是否为/sbin/init。

![](https://image.3001.net/images/20191112/1573521625_5dca08d99b079.png!small)

3、杀死自身相同进程名的shell进程或者挖矿进程(WorkProc "shell"
"$ShellProceName")。本例$shellProceName="diskmanagerd"。

![](https://image.3001.net/images/20191112/1573521638_5dca08e66e346.png!small)

4、使用ssh进行横向传播。

![](https://image.3001.net/images/20191112/1573521652_5dca08f44da84.png!small)

5、检测当前是否为root权限，如果是则检测安全产品，创建启动项，安装rootkit(brootkit)，否则使用CVE-2016-5195（脏牛漏洞）进行提权。

![](https://image.3001.net/images/20191112/1573521679_5dca090fd6615.png!small)

Install.sh。

![](https://image.3001.net/images/20191112/1573521693_5dca091d7bfab.png!small)

Brootkit.sh会对文件隐藏，进程隐藏，劫持命令(ps, ls, dir, netstat)等。

![](https://image.3001.net/images/20191112/1573521705_5dca0929b282f.png!small)

6、进入循环，检测更新，下载执行billgats木马，清除挖矿进程，休眠等待下次循环。

![](https://image.3001.net/images/20191112/1573521740_5dca094c43901.png!small)

## 防护建议

> 1、打上永恒之蓝补丁；
>
> 2、关闭135，139，445等端口，如果没有业务必要，建议封堵；
>
> 3、不要使用域管账号随意登录域内机器，域内机器密码应互不相同；
>
> 4、将密码更改为强密码；
>
> 5、修补CVE-2016-5195。

## IOC

### IP&Domain:

> 185.128.41.90
>
> 111.90.140.59
>
> owa.conf1g.com
>
> box.conf1g.com
>
> auth.to0ls.com

### MD5:

> b6c71db65a0a9341857f2107872dc33a
>
> 4fe2de6fbb278e56c23e90432f21f6c8
>
> 6a971a24a418ce99e9a0cd65ba14078d
>
> 4e117357b8a5bf51aaba6e939cace26b
>
> 48f0de466c907cfb202f006bb0ff0d0b
>
> ad593f6a17598bdd12fd3bd0f3b2a925
>
> 20788d837f33f5e735bdc99d68fc71b1
>
> d9bbb758e3831839558d80f381f9d4b1
>
> 795acc900cb55882629e7ce3f65130c4
>
> 1195ea4886acf3a857913c448af78d11

### 钱包：

>
> 47tRdmg92kbTtZrrAy4RF71QcENfV6Ym5RB8QyTBrHsNExBW7MRXXbNPBaB2J4hL8X9SHFRs7quLJfsYP1hnVo5xSUBDo4r

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

