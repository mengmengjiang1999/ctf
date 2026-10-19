RapperBot 是一个主要针对 IoT 设备的恶意软件家族，自从 2022 年 6
月以来一直保持活跃。此前以爆破攻击为主进行扩张，攻击者驱动僵尸网络发起 DDoS 攻击。研究人员近期发现，RapperBot 开始进行挖矿获利。

## 相似与差异

2023 年 1 月，RapperBot 的挖矿活动就浮出水面。RapperBot 样本最独特、最持久的特征是内嵌的 YouTube URL
地址：https://www.youtube.com/watch?v=4fm_ZZn5qaw，在该家族的大多数样本中都可以发现。但是，新样本中该字符串并没有什么实际用途，这与样本不同。在旧样本文件中，会在执行开始时将
URL 打印到控制台。另一个典型的特征是将 SSH 公钥增加到 ~/.ssh/authorized_keys 以保持对失陷主机的持续访问，公钥与 2022
年 6 月的攻击行动中使用的仍然相同。

除了这些相似之处，也存在一些明显的差异。例如通过 hxxp://109[.]206[.]243[.]207/ssh/arm7 传播的样本文件，只包含三种
DDoS 攻击而不包含 SSH 爆破以及自我传播的功能。但是，该样本中包含向 C&C 服务器上线发送失陷主机相关信息的新代码。而相同 URL
的其他样本文件，则新增了 SSH 爆破功能。与旧时的攻击不同，爆破的凭据内嵌在样本文件中，而不需要再通过 C&C 服务器下载。

与过去相同，所有样本仍然使用异或加密算法来处理敏感字符串。存在差异的是，本次使用了双层异或加密。第一层使用多字节异或密钥，第二层使用单字节异或密钥，这样来防止对异或加密算法的爆破，阻止分析人员直接获取相关字符串。

![image.png-68.4kB](https://image.3001.net/images/20230510/1683731210_645bb30a0cf726c098d9a.png!small)异或字符串解密

最大的更新升级其实在于 C&C 协议。此前每个请求会携带唯一的 32 字节 Bot
ID，目前已经弃用。新版本的请求大小可变，会生成随机字节来填充请求的未使用部分，请求数据也不再位于每个请求的固定偏移处。

## 改良的 C&C 协议

RapperBot 连接到硬编码的 C&C 服务器并发送包含有关失陷主机相关信息的上线请求：

![image.png-519.9kB](https://image.3001.net/images/20230510/1683731210_645bb30ab17841867f83c.png!small)上线请求

  1. 硬编码值：0x3 0xd3 0x4a 0xb6
  2. 感染向量：例如 scan.ssh.x86_64
  3. 本机 IP 地址
  4. UID
  5. 当前目录
  6. 处理器数量
  7. 总内存大小
  8. 打开文件限制
  9. 主机名
  10. 处理器型号

上线后，恶意软件以 60 秒到 600 秒的随机间隔发送保活信息，告知 C&C 服务器已准备好接收命令。

与字符串加密类似，C&C 通信也使用两层加密。首先必须对消息头进行处理，才能获取加密数据的位置以及解密所需的密钥。恶意软件首先生成一个介于 4 到 128
之间的随机数（RAND_VALUE），并为数据生成一个 4 到 32 字节长的随机异或密钥（KEY_SIZE）。请求大小是随机的，计算方式如下所示：

REQUEST_SIZE = RAND_VALUE + KEY_SIZE + CONTENT_SIZE + 6

然后恶意软件生成一个相同大小的缓冲区并用随机字节填充。此缓冲区的第一个字节将用作异或密钥（HEADER_KEY），用于对头数据进行加密处理。第二个字节将被与
HEADER_KEY 异或的 RAND_VALUE 覆盖。请求数据存储在从 HEADER_OFFSET 到 RAND_VALUE/2。

![image.png-764.9kB](https://image.3001.net/images/20230510/1683731211_645bb30bd278400e42b69.png!small)加密数据结构

从 HEADER_OFFSET 开始，结构为：

  * 偏移量 0x2：ENC_REQ_TYPE（请求类型异或 HEADER_KEY）
  * 偏移量 0x3：ENC_KEY_SIZE（KEY_SIZE 异或 HEADER_KEY）
  * 偏移量 0x4：KEY
  * 偏移量 KEY_SIZE+0x4：ENC_CODE_SIZE（（包含 CONTENT_SIZE 的小端字序 rol 8） 异或 HEADER_KEY）
  * 偏移量 KEY_SIZE+0x6：加密数据（ENC_CONTENT）

上图中未标记的字节都是随机生成的填充字节，使用 HEADER_KEY 与 KEY 解密数据的 Python 代码如下所示：

![image.png-239kB](https://image.3001.net/images/20230510/1683731213_645bb30d69d6c28c55ce3.png!small)解密代码

分析人员并没实际收到 C&C 服务器下发的命令，但样本分析表示 RapperBot 支持以下命令：

  * 4：执行 DDoS 攻击
  * 5：停止 DDoS 攻击
  * 6：停止执行

## 加密货币挖掘

C&C 通信协议的变更并非唯一的重大更新，攻击者也开始利用失陷的 64 位 Intel 机器来进行加密货币挖掘。针对 64 位机器提供的 Shell
脚本会下载并执行 XMRig 挖矿程序与 RapperBot 二进制文件，如下所示：

![image.png-653.9kB](https://image.3001.net/images/20230510/1683731214_645bb30e77c1cd4fe837d.png!small)Shell
脚本

2023 年 1 月发现的样本文件中，分析人员发现攻击者将 RapperBot 的 C 代码与 XMRig 的 C++ 代码合并，以创建具备挖矿功能的
Bot 程序。

## 检测逃避

除了在执行时将挖矿程序作为子进程执行外，这些样本在功能上与针对 ARM 设备的样本基本相同，同样不具有 SSH 暴破以及自我复制功能。合并 Bot
与挖矿代码可能是试图使用相同的双层异或加密算法来保护矿池与门罗币钱包地址。读取外部配置文件的代码被攻击者删除，挖矿程序只能使用内嵌的配置。启动挖矿程序前，Bot
会解密矿池与门罗币钱包地址并更新配置信息。

攻击者还使用了多个矿池来实现冗余备份与隐私保护，其中两个是部署在 RapperBot 的 C&C
服务器上的代理矿池，这样就无需钱包地址与实际矿池地址即可挖矿。除此之外，也使用了公共矿池来作为后备。

为了防止挖矿程序被终止，SIGTERM、SIGUSR1、SIGINT 和 SIGHUP 信号的默认信号处理程序均已被删除。

攻击者会终止特定文件名的其他挖矿程序，例如：

> xmrig  
> .rsync  
> miner  
> dota.  
> moner  
> UPX!  
> \--algo  
> network01  
> faster than light  
> dota2  
> .rsync  
> cat /proc/cpuinfo  
> /etc/cron.hourly/gcc.sh  
> /etc/daemon.cfg  
> denyip=

除了文件名外，文件路径也是检查的重点，例如：

> /shm/  
> /dev/netslink/  
> /tmp/  
> xmrig  
> .X19-unix  
> netwalker  
> (deleted)  
> .rsync  
> /a/  
> /b/  
> /c/  
> miner  
> dota  
> network01  
> xrx  
> /.x

最后根据命令行参数终止进程，如下所示：

> wget  
> curl  
> netstat  
> kill  
> 3333  
> zmap  
> tsm  
> passwd  
> netwalk  
> zzh  
> xrx  
> pnscan  
> xri

但路径或命令行参数包含 /zvx/ 的进程被列入白名单，不会终止。

内嵌挖矿功能的 RapperBot 并没有自我传播能力，可能存在其他 Loader 帮助进行传播。但目前来说，研究人员尚未发现直接传播 64 位
RapperBot 的感染媒介。

## 总结

攻击者总是试图将失陷主机的利益最大化，RapperBot 僵尸网络背后的运营方也不例外。RapperBot
不断更新以逃避检测，这表明其仍然是一个重要的威胁。

## IOC

> 7c9e6d63bc1f26e9c8a8703439e12de12da9892f2d6cd9bda5f45ec00c98a29f  
> 912e151641f20f9d689c6ea26cf6f11d5ee0b6fdc4d4a1179fac413391748c65  
> f06d698967cee77e5a7bf9835b0a93394097e7590c156ed0d8c6304345701cfa  
> 6c034ff9b5447da62822e3231e5e2d5db225756b3e216f6fc469469cb1d81813  
> dfaffe78b8ccb03626c2f55596f977da917e8e9a00ee7576ce9eca688d88447d  
> 95aa6882f5ea5a892ef832ef15dea77261394a7fec6db9d91267d40f1cf2bfa5  
> 0ad68d5804804c25a6f6f3d87cc3a3886583f69b7115ba01ab7c6dd96a186404  
> bd87ac780e574ae8415907f88a3b48af578bb269308b56826e2f33438559e4b7  
> 3296598c79748322dfff8eb786705d048725c04b23dd3a293f52a1acafe9e7ae  
> 7f6e0fa785820075a61819ca6b272a239733b770eb8a92a4056cf5d26d89795f  
> hxxp://109[.]206[.]243[.]207/d  
> hxxp://109[.]206[.]243[.]207/ssh/arm4  
> hxxp://109[.]206[.]243[.]207/ssh/arm5  
> hxxp://109[.]206[.]243[.]207/ssh/arm6  
> hxxp://109[.]206[.]243[.]207/ssh/arm7  
> hxxp://109[.]206[.]243[.]207/ssh/bot  
> hxxp://109[.]206[.]243[.]207/ssh/scan_arm4  
> hxxp://109[.]206[.]243[.]207/ssh/scan_arm5  
> hxxp://109[.]206[.]243[.]207/ssh/scan_arm6  
> hxxp://109[.]206[.]243[.]207/ssh/scan_arm7  
> hxxp://109[.]206[.]243[.]207/ssh/x86_64  
> hxxp://109[.]206[.]243[.]207/ssh/xmrig  
> hxxp://171[.]22[.]136[.]15/arm4  
> hxxp://171[.]22[.]136[.]15/arm5  
> hxxp://171[.]22[.]136[.]15/arm6  
> hxxp://171[.]22[.]136[.]15/arm7  
> 109[.]206[.]243[.]207  
> 171[.]22[.]136[.]15  
> 109[.]206[.]243[.]207:31271  
> 109[.]206[.]243[.]207:25621  
> pool[.]hashvault[.]pro:80

## 参考来源

> [Fortinet](https://www.fortinet.com/blog/threat-research/rapperbot-ddos-> botnet-expands-into-cryptojacking)

