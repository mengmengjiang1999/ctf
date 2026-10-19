FritzFrog 是一个 P2P 僵尸网络，每个失陷主机都是网络中的一部分，能够发送、接收、执行命令来控制网络中的机器。

![image.png-66.3kB](https://image.3001.net/images/20220214/1644831648_620a23a00af880b8f7963.png!small)典型特征

FritzFrog 主要通过 SSH 爆破进行传播，爆破成功后部署恶意软件。恶意软件在失陷主机上监听端口等待命令，支持的命令如下所示：

![image.png-65kB](https://image.3001.net/images/20220214/1644831648_620a23a0820fba8f6825c.png!small)命令列表

研究人员认为 FritzFrog 是“下一代”僵尸网络，主要有以下特点：

> 持续更新，既是失陷主机又是 C&C 服务器
>
> 侵略性强，使用的字典很强大，其他 P2P 僵尸网络如 DDG 只使用`root`一个用户名
>
> 效率很高，攻击目标在节点间均匀分布
>
> 私有协议，使用的 P2P 协议是私有的，不依赖已知的 P2P 协议

## FritzFrog v2

2020 年 8 月，FritzFrog 被披露后不久，攻击强度有所下降。但在 2021 年 12 月初，根据遥测数据发现其攻击在惊人地增加。

![image.png-76.4kB](https://image.3001.net/images/20220214/1644831648_620a23a0ea98a4d8a56f5.png!small)

攻击数量

FritzFrog 从 SSH 爆破开始，释放可执行文件后监听 1234 端口，并且扫描 22 端口和 2222 端口。

本轮攻击与此前的攻击区别之一是恶意进程名，此前使用的是 `ifconfig`或 `nginx`，而本次使用了 `apache2`。

## 受害者分析

研究人员开发了名为 `Frogger`的工具，利用僵尸网络的基础设施来收集失陷主机的相关信息。

![image.png-107.8kB](https://image.3001.net/images/20220214/1644831649_620a23a18749fb5923679.png!small)攻击节点数量

通过发现攻击的计算机 IP 地址和 `Frogger`提供的信息来收集受害者 IP 地址。

![image.png-80.5kB](https://image.3001.net/images/20220214/1644831650_620a23a20b1968f7ff0fc.png!small)趋势差异

这段时间内，FritzFrog 成功感染了 1500
多台计算机。这些设备属于各种不同的组织与行业，如医疗、教育和政府等，在欧洲电视频道网络、俄罗斯医疗设备制造商和东亚多所大学中都发现了失陷主机。

![image.png-293.8kB](https://image.3001.net/images/20220214/1644831650_620a23a274b4f17ed1332.png!small)失陷主机分布

## 新功能

FritzFrog 使用 Golang 编写，可在多种架构上运行。通过 UPX 加壳，进程通常名为 ifconfig、nginx、apache2 或
php-fpm。FritzFrog 每天都在保持更新，有时甚至一天更新多次，有时是修复 BUG 有时是增加功能。

### WordPress

FritzFrog 会通过名为 Wordpress 和 WordpressTargetsTTL 的列表，实现跟踪 WordPress
服务器的基础设施。对应的 P2P 命令为 `put wordpress`，代码如下所示：

![image.png-573.2kB](https://image.3001.net/images/20220214/1644831659_620a23abc252c41f15b0c.png!small)部分代码

截至发布时，列表仍然为空。FritzFrog 实际上并不包含识别 WordPress 目标的模块，研究人员认为是为新版本做准备，用于信息泄露或者勒索软件等。

### Tor

FritzFrog 可以使用 Tor 代理转发 SSH 连接，通过本地端口 9050 使 FritzFrog 能够通过 SSH 控制失陷主机。

失陷主机只能发现直连邻居节点，以此来隐藏其他失陷主机。但该功能尽管存在，却并未启用。

### SCP

最初时，FritzFrog 使用 cat 命令部署恶意样本。现在，FritzFrog 会使用 SCP 进行远程复制。攻击者利用了开源的 Golang 编写的
[SCP](https://github.com/povsister/scp)库，二者之间区别应该不大，但 SCP 库的作者是中国人。

### 黑名单

FritzFrog 有一个预制的不攻击列表，攻击者也可以通过 P2P 命令 `putbleentry`后期动态插入。

    
    
    [ {"Address": "","Uname_match": "[redacted]dddz.me 3.10.0-693.2.2.el7.x86_64 #1 SMP Tue Sep 12 22:26:13 UTC 2017"},{"Address": "","Uname_match": "[redacted]-1 4.4.0-151-generic #178-Ubuntu SMP Tue Jun 11 08: 30: 22 UTC 2019"},{"Address": "","Uname_match": "[redacted].amzn2.x86_64 #1 SMP Mon Jun 18 22: 33: 07 UTC 2018 x86_64 GNU/Linux"},{"Address": "","Uname_match": "[redacted]-generic #113-Ubuntu SMP Thu Jul 9 23: 41: 39 UTC 2020"},{"Address": "","Uname_match": "[redacted] raspberrypi 4.4.32-v7+ #924 SMP Tue Nov 15 18: 11: 28 GMT 2016 armv7l GNU/Linux"},{"Address": "","Uname_match": [redacted] 3.10.0-123.4.4.el7.x86_64 #1 SMP Fri Jul 25 05: 07: 12 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux"},{"Address": "","Uname_match": [redacted] 4.18.0-193.28.1.el8_2.x86_64 #1 SMP Thu Oct 22 00: 20: 22 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux"},{"Address": "[redacted].24: 22","Uname_match": ""},{"Address": "[redacted].88: 22","Uname_match": ""},{"Address": "[redacted].26: 22","Uname_match": ""}]

攻击者试图避免感染低端设备，如 Raspberry Pi 或 AWS 上较差的 EC2 主机。

列表中来自俄罗斯的 IP 地址，有一个开放了一系列端口并且存在各种各样的漏洞，极有可能是一个蜜罐，另外一个 IP
地址指向开源僵尸网络水坑。这表明，攻击者积极逃避检测分析。

两个位于美国的 IP 地址，一个是马里兰大学的，另一个会在浏览时警告“好奇害死猫”。

![image.png-215.9kB](https://image.3001.net/images/20220214/1644831661_620a23ad4477231b9481e.png!small)好奇害死猫

## 归因

新版本利用了使用 Golang 编写的 scp
库，仓库[持有人](https://github.com/povsister)的位置位于上海，其中一位[作者](https://github.com/chulinx)也位于上海。

FritzFrog
的钱包地址：（47BD6QNfkWf8ZMQSdqp2tY1AdG8ofsEPf4mcDp1YB4AX32hUjoLjuDaNrYzXk7cQcoPBzAuQrmQTgNgpo6XPqSBLnfsjaV）和矿池也与
Mozi 僵尸网络活动有关，而 Mozi 的作者最近在中国被捕。

截至目前，大约 37% 的失陷主机位于中国。中国及其周边地区的攻击活动也是频繁的，攻击者很有可能是说中文的或者伪装成与中国有关。

## 检测工具

Akamai 提供了一个 FritzFrog
[检测脚本](https://github.com/guardicore/labs_campaigns/blob/master/FritzFrog/detect_fritzfrog.sh)，如下所示：

![image.png-103.2kB](https://image.3001.net/images/20220214/1644831661_620a23adf13bc9eefb37e.png!small)工具截图

## 参考来源

> [Akamai](https://www.akamai.com/blog/security/fritzfrog-p2p)

