2022 年 11 月，研究人员发现一个使用 Go 语言编写的僵尸网络 Zerobot。攻击者使用 WebSocket 协议与 C&C 服务器进行通信，在
11 月中旬开始对外分发当前版本样本。

![image.png-58.1kB](https://image.3001.net/images/20221209/1670517501_639212fd59baf120ed8b4.png!small)IPS
设备的检出情况

![image.png-94kB](https://image.3001.net/images/20221209/1670517502_639212fe0d905dddfe91e.png!small)IPS
设备的检出情况

![image.png-92.5kB](https://image.3001.net/images/20221209/1670517502_639212feb193fd23108e5.png!small)IPS
设备的检出情况

## 感染

Zerobot 利用多个漏洞发起攻击，下载脚本如下所示，下载的 URL 从 zero[.]sudolite[.]ml 切换到
176[.]65.137[.]5。僵尸网络针对各种架构进行攻击，包括
i386、amd64、arm、arm64、mips、mips64、mips64le、mipsle、ppc64、ppc64le、riscv64 和
s390x。

![image.png-664.2kB](https://image.3001.net/images/20221209/1670517503_639212ff684b89a9582e5.png!small)2022年11月24日前使用的下载脚本

![image.png-896.2kB](https://image.3001.net/images/20221209/1670517504_63921300ca91e6504b010.png!small)最新使用的下载脚本

Zerobot 有两个版本，11 月 24 日之前的版本只包含基本功能。新版本增加了名为 selfRepo 的模块进行自我复制与攻击。

旧版函数列表如下所示：

![image.png-201.1kB](https://image.3001.net/images/20221209/1670517505_63921301e1ea63a937975.png!small)旧版本主要函数

## 初始化

Zerobot 首先检查其与 Cloudflare 的 DNS 解析服务器 1.1.1.1 的连接情况。

![image.png-119.3kB](https://image.3001.net/images/20221209/1670517506_639213029a2fbc0cf879b.png!small)检查网络连接

随后，根据受害者的操作系统情况进行复制。针对 Windows 平台，会将自身命名为 FireWall.exe 并复制到启动文件夹中。针对 Linux
平台，路径为 %HOME%、/etc/init/ 和 /lib/systemd/system/。

![image.png-192.3kB](https://image.3001.net/images/20221209/1670517507_639213039ad78ea5aede6.png!small)复制功能代码

随后利用 AntiKill 模块阻止用户终止 Zerobot 程序，该模块监视特定的十六进制值并使用 signal.Notify
拦截发送的任何终止进程的信号。

![image.png-279.6kB](https://image.3001.net/images/20221209/1670517508_63921304da01483ce8214.png!small)AntiKill
功能代码

## 命令

Zerobot 使用 WebSocket 协议启动与其 C&C 服务器 ws[:]//176.65.137.5/handle 的连接。

![image.png-163.1kB](https://image.3001.net/images/20221209/1670517510_63921306b03b489311f76.png!small)连接
C&C 服务器

通过 WebSocket 协议，受害者上传的数据如下所示。解密后为失陷主机的相关信息构成的 JSON，如
{"Platform":"linux","GCC":"386","CPU":1,"Payload":"Direct","Version":1}。

![image.png-1214kB](https://image.3001.net/images/20221209/1670517511_6392130773ff57614f280.png!small)C&C
流量

支持的命令如下所示：

命令| 描述  
---|---  
ping| 心跳保活  
attack| TCP、UDP、TLS、HTTP、ICMP 多种协议攻击  
stop| 停止攻击  
update| 更新升级并重启  
enable_scan| 扫描开放端口并进行攻击  
disable_scan| 停止扫描  
command| 执行命令  
kill| 终止进程  
  
![image.png-287.1kB](https://image.3001.net/images/20221209/1670517512_63921308e2f56e9342f78.png!small)zero.mips
中接收命令

![image.png-110.9kB](https://image.3001.net/images/20221209/1670517513_63921309ef926a813fada.png!small)zero.386
中接收到命令

## 漏洞利用

Zerobot 中包含 21 个漏洞，如下所示。

![image.png-450.9kB](https://image.3001.net/images/20221209/1670517514_6392130ab2bd1c0920d62.png!small)漏洞利用列表

受到影响的产品如下所示，除了一些 IoT 设备外，还包括 Spring4Shell、phpAdmin、F5 Big 等。

![image.png-417kB](https://image.3001.net/images/20221209/1670517516_6392130c2697788f390da.png!small)受影响的产品列表

名为 ZERO_xxxxx 的两个漏洞是从 0day.today 网站收集的，该站点披露了很多漏洞。

![image.png-179.6kB](https://image.3001.net/images/20221209/1670517517_6392130d53aaeb1bb7567.png!small)0day.today
网页

漏洞利用中的 Payload 与前述的脚本文件相同。

![image.png-252.8kB](https://image.3001.net/images/20221209/1670517518_6392130e274ad5610f673.png!small)Payload

## 结论

Zerobot 是一个用 Go 语言编写的新型僵尸网络，通过 WebSocket 协议进行 C&C 通信。在 11 月 18
日首次出现，很短时间内就进行了大幅更新，提高了攻击与感染能力。

## IOC

> 176[.]65[.]137[.]5  
> 7ae80111746efa1444c6e687ea5608f33ea0e95d75b3c5071e358c4cccc9a6fc  
> df76ab8411ccca9f44d91301dc2f364217e4a5e4004597a261cf964a0cd09722  
> cd9bd2a6b3678b61f10bb6415fb37ea6b9934b9ec8bb15c39c543fd32e9be7bb  
> 7722abfb3c8d498eb473188c43db8abb812a3b87d786c9e8099774a320eaed39  
> 2955dc2aec431e5db18ce8e20f2de565c6c1fb4779e73d38224437ac6a48a564  
> 191ce97483781a2ea6325f5ffe092a0e975d612b4e1394ead683577f7857592f  
> 447f9ed6698f46d55d4671a30cf42303e0bd63fe8d09d14c730c5627f173174d  
> e0766dcad977a0d8d0e6f3f58254b98098d6a97766ddac30b97d11c1c341f005  
> 6c284131a2f94659b254ac646050bc9a8104a15c8d5482877d615d874279b822  
> 5af002f187ec661f5d274149975ddc43c9f20edd6af8e42b6626636549d2b203  
> 74f8a26eb324e65d1b71df9d0ed7b7587e99d85713c9d17c74318966f0bead0a  
> 9c16171d65935817afd6ba7ec85cd0931b4a1c3bafb2d96a897735ab8e80fd45  
> b1d67f1cff723eda506a0a52102b261769da4eaf0551b10926c7c79a658061fd  
> f0bb312eacde86d533c922b87e47b8536e819d7569baaec82b9a407c68084280  
> 2460434dabafe5a5dde0cce26b67f0230dbcd0d0ab5fabad1a1dbc289dc6432f  
> 2af33e1ff76a30eb83de18758380f113658d298690a436d817bd7e20df52df91  
> 4483c4f07e651ce8218216dd5c655622ff323bf3cdfe405ffeb69eafa75efad5  
> 7c085185f6754aef7824c201d8443300ff2b104521d82f9a8b8feb5d4c8d3191  
> 6ac49092ee1bdd55ddbf57df829f20aac750597d85b5904bb7bafa5b51fbb44d  
> f9fc370955490bdf38fc63ca0540ce1ea6f7eca5123aa4eef730cb618da8551f  
> 6dd71163b6ab81a35ce373875a688ad9b31e0d1c292f02e8b2bafa7b3d1e3731  
> d88e9248ff4c983aa9ae2e77cf79cb4efc833c947ec2d274983e45c41bbe47e1  
> 96bbb269fd080fedd01679ea82156005a16724b3cde1eb650a804fa31f18524e  
> 439b2e500e82c96d30e1ef8a7918e1f864e6d706d944aeddffe61b8bf81ef6d3  
> af48b072d0070fa09bca0868848b62df5228c34ef24d233d8eb75a1fde8ac23f  
> 5824fc51fcfba1a6315fd21422559d63c56f0e2192937085d65f9a0ac770eb3a  
> c9ea4cda12c14c895e23988229831b8f04ccab315c1cbc76a9efae888be55a3b  
> e2c2a0cccefc4314c110f3c0b887e5008073e607c61e1adde5000efb8e630d50

## 参考来源

> [Fortinet](https://www.fortinet.com/blog/threat-research/zerobot-new-go-> based-botnet-campaign-targets-multiple-vulnerabilities)

