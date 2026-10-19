2018 年 4 月，dhpcd 挖矿团伙首次浮出水面，此后一直处于活跃状态。尽管被揭露，但该团伙仍然不断更新迭代加强潜伏能力。

![image.png-239.8kB](https://image.3001.net/images/20221109/1668005807_636bbfaf7ee29f3d7f088.png!small)整体概览

该团伙将文件命名与 Linux 上合法程序相似，例如负责 DHCP 服务器运行的守护进程为 dhcpd，攻击者将恶意文件命名为
dhpcd。这种命名方式在该团伙使用的样本文件中广泛存在，这也是其能够在长达四年的时间里持续运营的一个原因。并且，攻击者使用 Tor
的出口节点对攻击基础设施进行隐藏，这使得追踪溯源变得非常困难。攻击者主要通过挖掘门罗币来进行获利。

## 攻击活动

自从 2018 年 4 月以来，Akamai 确认了来自 800 余个 IP 地址的两千余次攻击事件。这些 IP
地址主要归属于运营商与托管服务商，也有相当部分来自大学与非营利组织，这些主机成为了攻击者的基础设施。

2022 年 3 月，研究人员注意到 dhpcd 的挖矿程序进行了更新迭代，从 XMRig 2.13.0 升级为 XMRig
5.2.0。与此同时，其规模与攻击范围也都有较大的提高。2022 年 5 月，攻击频度达到年内最高。尽管没有 2021
年的峰值高，但也说明了攻击者希望能够通过更新迭代获取更大的收益。

![image.png-159.7kB](https://image.3001.net/images/20221109/1668005808_636bbfb065a20eab4ab62.png!small)时间趋势

自从检测发现该团伙，确认了 2215 次攻击，分布在 843 个不同的 IP 地址中，平均每个 IP 发起 2.6 次攻击。总体来看，每个 IP
地址攻击次数为 1 到 27 不等。

![image.png-231.6kB](https://image.3001.net/images/20221109/1668005809_636bbfb13a036e3bbf900.png!small)全球分布

在 840 个攻击者 IP 中，大约 80% 都是 Tor
的出口节点，这使得追踪攻击者变得极为困难。其中就包含美国大学、欧洲非盈利组织与其他各种组织的机器。将这些 Tor 出口节点按国家划分，大多数的攻击者 IP
地址都位于美国、德国与荷兰。

![image.png-248.6kB](https://image.3001.net/images/20221109/1668005810_636bbfb2139b84e9b4137.png!small)国家百分比

## 获利

攻击者使用多个钱包来进行获利，研究人员分析时发现了 13 个不同的门罗币钱包。每个钱包在收入 150
美元左右后，就会轮换到使用另一个钱包。由于每个钱包的余额都比较少，很有可能攻击者持有的钱包数量远比已知的更多。将收益分散到多个钱包，也可以不那么引人注目。

目前为止，跟踪已知钱包地址发现总利润约为 2000 美元，但推测攻击者的实际收益应该高得多。

攻击者最初使用 minexmr[.]com矿池。在 8 月 19 日这些矿池被关停后，攻击者转向使用 pool[.]supportxmr[.]com。

## 攻击链

![image.png-445.7kB](https://image.3001.net/images/20221109/1668005810_636bbfb2dc95757a30f83.png!small)攻击链

### 初始攻击

攻击者通过爆破 SSH 服务来入侵 Linux 主机，随后使用 SCP 命令将测试验证程序写入失陷主机。测试验证程序并无实际功能，文件名也为随机字符串，例如
/bin/cpuufcdmorv9crpa8h6wgh6iq2。

### 挖矿程序

攻击者将挖矿程序（名为 dhpcd）通过 SCP 下载到同一目录，挖矿程序通过 4444 端口的 TCP 协议来连接矿池。

> fr14[.]minexmr[.]com
>
> ca61[.]minexmr[.]com
>
> sg97[.]minexmr[.]com
>
> fr13[.]minexmr[.]com
>
> us40[.]minexmr[.]com

### 持久化

攻击者会通过多种方式为挖矿程序完成持久化。首先，更改已有用户（例如root、admin、test、oracle、test1、ubuntu等）的密码，并且通过修改
/etc/shadow 的文件属性来保护这种更改。

随后，攻击者将 SSH 密钥添加到 ~/.ssh/authorized_keys 文件中，同样修改文件属性保护更改。

> ssh-rsa
> AAAAB3NzaC1yc2EAAAADAQABAAABAQCuhPmv3xdhU7JbMoc/ecBTDxiGqFNKbe564p4aNT6JbYWjNwZ5z6E4iQQDQ0bEp7uBtB0aut0apqDF/SL7pN5ybh2X44aCwDaSEB6bJuJi0yMkZwIvenmtCA1LMAr2XifvGS/Ulac7Qh5vFzfw562cWC+IOI+LyQZAcPgr+CXphJhm8QQ+O454ItXurQX6oPlA2rNfF36fnxYss1ZvUYC80wWTi9k2+/XR3IoQXZHKCFsJiwyKO2CY+j

攻击者通过配置定时任务来确保每小时运行一次挖矿程序。

> /bin/dhpcd -o ca.minexmr.com:4444 -B >/dev/null 2>/dev/null exit 0

### 清除竞争对手

攻击者要努力清除其他攻击者，最大化独占失陷主机的资源。在 /dev/shm 目录下执行两个脚本，名为 knrm 与 r。该目录是一个 tmpfs
文件系统，其中的文件保存在虚拟内存中，写入该位置不会在文件系统中留下痕迹。

攻击者会查询系统上消耗资源最多的进程、占用内存最多的进程，将其全部终止，确保自己的资源够用。

> /etc/cron.hourly/gcc.sh  
> /etc/cron.hourly/cron.sh  
> /etc/cron.hourly/gcc4.sh/lib/libudev.so

紧接着清除掉如 XorDdos、Tsunami 和 aliyun.one 等其他攻击者的恶意进程（如 Xm64、Ceurnad、/tmp/samba 和
Sc64u）、恶意文件与定时任务。

> /root/pty  
> /tmp/bash  
> /dev/shm/bash  
> /var/tmp/bash  
> /var/lock/bash  
> /var/run/bash  
> /bin/httpsd  
> /lib/udev/udev  
> /lib/udev/debug  
> /root/sysem  
> /root/systma  
> /etc/jourxlv  
> /tmp/sysem  
> /tmp/su  
> /tmp/ddgs.*  
> /root/pty10  
> /root/pty4  
> /root/xmr64  
> /usr/local/sbin/t  
> /usr/local/sbin/rsync  
> /etc/ceurnad

为了感知最新的竞争者，脚本运行 atq 命令获取待处理作业列表与系统目录中的各种文件。过滤掉已知的文件，如 dump、docker、mount
等，留下可能是其他攻击者的挖矿程序的文件列表。

## 检测与缓解

SSH 服务非常普及，但如果使用专用的私钥和公钥并且拦截基于密码的登录，就可以阻拦针对 SSH 服务的爆破攻击。

在 SSH 配置文件 /etc/ssh/sshd_config 中修改为如下即可：

> PermitRootLogin no
>
> PasswordAuthentication no

针对 dhpcd 的话，可以拦截 4444 端口的 TCP 通信或者拦截与已知矿池的通信。

## 结论

dhpcd 是一个长期活跃的挖矿团伙，主要通过 SSH 爆破进行传播，通过挖掘门罗币进行获利。利用 Tor
扩展攻击基础设施后，该团伙的攻击确实比其他攻击者具有更好的稳定性和对抗性。

dhpcd
长达四年的活跃期再次向世人证明，即使是最简单的攻击仍然具备非常广阔的“市场前景”。维持攻击的运营与迭代，可以进行持续获利。每个人都应该提高安全意识，哪怕是在细微之处也能使整体更安全。

## IOC

> fr14[.]minexmr[.]com  
> ca61[.]minexmr[.]com  
> sg97[.]minexmr[.]com  
> fr13[.]minexmr[.]com  
> us40[.]minexmr[.]com  
> pool[.]supportxmr[.]com  
> eb808932714c9533962e129e61d84c29536497e62b2a7d89dce3376d882c6965  
> e971fa0c392a9f43c37dccfdd4f8e6bc109e162716d9b206170f7bb133634ffd  
> 76005592ad7d8901c64a5cfbcdde589a960ba35c9672da6182d131cd67ae0c97  
> 2cca764d24212f8fc58780b9135740929f38b45bcd5fc82c4a2ff47e90890d06  
> 3ea8cc0977e5542053353bcf3e58de947dd727259369707a13a4d0c8f14b7486

## 参考来源

> [Akamai](https://www.akamai.com/blog/security-research/dhpcd-cryptominer-> hid-four-years)

