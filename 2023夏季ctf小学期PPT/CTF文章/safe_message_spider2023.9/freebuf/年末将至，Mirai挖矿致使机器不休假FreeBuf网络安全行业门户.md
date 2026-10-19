**近日，深信服安全团队基于SIP产品在国内发现一种新型的Mirai变种，该变种会进行门罗币挖矿并且通过SSH爆破来实现传播。**

整个流程如下：

![1.png](https://image.3001.net/images/20190122/1548161694_5c47129e8818e.png!small)

##  **0x01** **系统调用下载器**

然后我们分析一下另一个程序DDG这个文件，这个文件就是一个下载器，下载母体。

![2.png](https://image.3001.net/images/20190122/1548161702_5c4712a66c431.png!small)

该程序使用了大量的内联汇编，通过系统调用来实现下载的功能，容量体积更小，减少了被杀软引擎识别的风险。具体的系统调用可以在<https://syscalls.kernelgrok.com/>查询。

![3.png](https://image.3001.net/images/20190122/1548161711_5c4712af5b995.png!small)

我们使用strace来观察一下这个程序的行为，连接了5.63.159.203下载母体文件dl

![4.png](https://image.3001.net/images/20190122/1548161722_5c4712ba75fb5.png!small)![5.png](https://image.3001.net/images/20190122/1548161721_5c4712b9c609e.png!small)

##  **0x02** **多功能变种Mirai** **母体**

该Mirai母体已被多家引擎识别。

![6.png](https://image.3001.net/images/20190122/1548161732_5c4712c40b6c1.png!small)

跟踪一下母体的行为。

![7.png](https://image.3001.net/images/20190122/1548161745_5c4712d16daae.png!small)

程序将通过系统调用unlink将自身给删除了，这里说明一点，母体会一直运行，所以遇到这种找不到文件，但是母体还在运行的程序，可以通过查找PID,
然后进入/proc/PID/ 目录下，找到exe，使用cat /proc/PID/exe >>
mom_exe，可以拿到母体文件，如果直接将母体进程干掉，就拿不到这个文件了。本例有拿到下载器，所以可以通过下载器下载。

![8.png](https://image.3001.net/images/20190122/1548161760_5c4712e0b150d.png!small)![9.png](https://image.3001.net/images/20190122/1548161760_5c4712e0b990a.png!small)

检查是否存在重启信号设备watchdog(看门狗)，如果检测到则修改权限，让watchdog失效

![10.png](https://image.3001.net/images/20190122/1548161779_5c4712f3837b8.png!small)

然后检测同行的比特币挖矿软件,通过使用md5来识别。

![11.png](https://image.3001.net/images/20190122/1548161789_5c4712fde0c78.png!small)![12.png](https://image.3001.net/images/20190122/1548161790_5c4712fe9a726.png!small)
将http, https, ftp的代理信息写入.bashrc文件中。

![13.png](https://image.3001.net/images/20190122/1548161801_5c471309c7f91.png!small)![14.png](https://image.3001.net/images/20190122/1548161801_5c471309cd5fa.png!small)

下载挖矿软件到/tmp目录并且执行，挖矿软件的名称采用随机字符串的方式，长度不固定

![15.png](https://image.3001.net/images/20190122/1548161815_5c471317cec4f.png!small)![16.png](https://image.3001.net/images/20190122/1548161816_5c4713183129d.png!small)
![17.png](https://image.3001.net/images/20190122/1548161835_5c47132b43e44.png!small)![18.png](https://image.3001.net/images/20190122/1548161817_5c471319209ca.png!small)

可以看到创建了一个随机端口监听，等待连接，并且开启了一个ssh暴力破解攻击其他主机，实现传播，被攻击的为内网IP和随机生成IP。

![19.png](https://image.3001.net/images/20190122/1548162077_5c47141db388f.png!small)![20.png](https://image.3001.net/images/20190122/1548162078_5c47141e69ab3.png!small)

清除用户的计划任务

![21.png](https://image.3001.net/images/20190122/1548161853_5c47133d88180.png!small)

并且程序拥有着守护挖矿进程的能力，当把挖矿进程直接杀掉，母体会重新下载挖矿病毒并运行，所以这里是导致出现病毒文件再次出现，但是并没有运行的原因。

![22.png](https://image.3001.net/images/20190122/1548161871_5c47134f1af83.png!small)![23.png](https://image.3001.net/images/20190122/1548161866_5c47134af1cc2.png!small)

拥有着一个基本所有功能的Mirai，功能太过复杂，使用超多的fork和syscall汇编内联代码。

增加分析人员的分析难度。

## 0x03 挖矿程序

同样也被各大引擎识别了,这个是门罗币(XMR)挖矿，XMR由于匿名性被黑产热爱。

![24.png](https://image.3001.net/images/20190122/1548161881_5c4713595d983.png!small)

strace看一下程序的运行流程，连接矿池，发送任务，接受任务结果

![25.png](https://image.3001.net/images/20190122/1548161893_5c471365bfdb9.png!small)

首先通过gulf.moneroocean.stream这个地址登录矿工的信息，钱包等，然后连接矿池xmr.crypto-pool.fr(139.99.100.250)进行挖矿

![26.png](https://image.3001.net/images/20190122/1548161904_5c47137015328.png!small)![27.png](https://image.3001.net/images/20190122/1548161906_5c471372587c2.png!small)

我们抓取了一些数据包，可以发现程序通信的挖矿数据

![28.png](https://image.3001.net/images/20190122/1548161916_5c47137c0694f.png!small)

我们可以看到一次完整的挖矿通信的数据

![29.png](https://image.3001.net/images/20190122/1548161931_5c47138b1f253.png!small)

##  **0x04** **分析结论**

该程序经过测试，在执行病毒母体后，重启之后并不会再次出现感染情况。上次的重启重新下载了出现病毒文件初步估计是没有清理干净，清理顺序的问题。

挖矿信息：

> 矿工信息验证地址：gulf.moneroocean.stream
>
> 矿池地址：xmr.crypto-pool.fr
>
>
> 钱包地址：489nAwmiY4s8X95kvPDVvUaHsqmrs1NwsVKoBbqKftYzDAQJVUryJwJ7WMKansCeowe4vxg42p9VtbDKTPxkKp1pUXTnA5X
>
>
> 86V42mJ86Dg5uw9TYLWairZrjkhK1LkkiaAyDHeLTJhfEi1c9XbFPTHLCJWtM12Sv16P9aM6U64Ekc9drZ8or55Y3SqqiQK

IOC(MD5)：

> 挖矿：04e28bfd6f7e58701a7654d53d279100
>
> 下载器：d530cab45f1234ce35c0b56689516f42
>
> Mirai母体：9c699434f72e798ac42f72a82a30f997

##  **0x05** **解决方案**

清除方式：

将母体的所有进程先全部使用kill -9 强行杀死

然后到/tmp目录下将挖矿文件删掉（如果母体文件dl还在，也将母体文件删除）

然后使用kill -9 将挖矿进程干掉。

病毒检测查杀：

1、深信服EDR产品、SIP产品及防火墙等安全产品均具备病毒检测能力，部署相关产品用户可进行病毒检测。

![30.png](https://image.3001.net/images/20190122/1548161943_5c4713970316f.png!small)

病毒防御：

> 1、修补相关的web漏洞，防止被再次入侵。
>
> 2、更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。
>
> 3、病毒通过ssh传播，如果可以，可以将ssh的密码登录方式换成密钥登录。可防止ssh爆破传播。

全世界的安全研究专家们经常都需要对恶意软件来进行逆向工程分析，这样才能更加清楚地了解到网络攻击者的攻击方式以及真正意图。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

