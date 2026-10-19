Rootkit 是非常危险的恶意软件，一旦侵入就很难被发现。开发 Rootkit 通常更加困难，很多攻击者都倾向于重用开源项目。

Adore-Ng 是一个相对较老的、开源的 Linux 内核 Rootkit，最初针对内核 2.x 版本开发，但目前已更新为针对内核 3.x 版本适用。该
Rootkit 可以隐藏进程、文件甚至内核模块，使其更难被发现。它还允许经过身份验证的用户模式进程与 Rootkit 交互以控制进程，从而允许攻击者使用单个
Rootkit 隐藏许多其他恶意软件。

2022 年早期，研究人员发现基于 Adore-Ng 开发而来的在野 Rootkit。根据 .modinfo 可以看出这是为特定内核版本编译的：

![image.png-65.8kB](https://image.3001.net/images/20220712/1657627683_62cd64237fb2645ebbcdb.png!small)内核版本

如果使用 insmod --force 的命令强制将模块加载到内核中，内核找不到所需的符号就会导致系统奔溃。发现的 Rootkit
可以在不强制加载的情况下，在 CentOS 6.10 中成功加载。

Rootkit 中硬编码的文件名为 PgSD93ql，这也是要引用的 Payload 文件名。攻击者想将该名称贴近 PostgreSQL
的文件名称，不被发现。

![image.png-35.7kB](https://image.3001.net/images/20220712/1657627684_62cd64244bf1e847b1acc.png!small)硬编码文件

按图索骥找到被 Rootkit 隐藏的文件，实际为 C 写的后门。由于写入文件时显示 /proc/syslogk，将其命名为 Syslogk
Rootkit。

## 分析 Syslogk

Syslogk Rootkit 主要基于 Adore-Ng 开发，但也包含一些更为隐蔽的新功能。

### 加载内核模块

要将 Rootkit 加载到内核空间，需要与编译时使用的内核版本大致匹配，但不必严格相同。

通过 insmod 命令，即可在 Centos 6.10 中轻松加载该 Rootkit。但加载后使用 lsmod
命令，并不会看到内核模块列表中出现该恶意驱动程序。

### 掀开隐藏面纱

Rootkit 中的 hide_module 函数，使用内核 API list_del 从内核模块的链表中删除该模块。不过，Rootkit 在函数中实现了
proc_write 函数，当 /proc/syslogk 文件被写入 1 时，就会显示 Rootkit。

![image.png-55.7kB](https://image.3001.net/images/20220712/1657627685_62cd6425013025ff0c10f.png!small)现形

一旦 Rootkit 被确认，就可以使用 rmmod 命令将其删除。

### 功能概述

Syslogk 使用了多种方式隐藏自身：

> 通过 hk_proc_readdir 隐藏包含恶意文件的目录
>
> 通过 hk_getpr 隐藏特定进程
>
> 通过 hk_t4_seq_show 隐藏特定服务
>
> 通过安装 netfilter hook 控制接收到的特制 TCP 数据包
>
> 通过硬编码的密钥利用特制 TCP 数据包远程启动 Payload

Syslogk 非常隐蔽，在特制的 TCP 数据包发送到实现主机前并不会加载后门，执行时也是打着 SMTP 合法服务的旗号进行隐蔽传输。

在为 PTE 增加了写权限后，Rootkit 就可以 Hook 指定函数：

![image.png-41.9kB](https://image.3001.net/images/20220712/1657627685_62cd6425b467d784c8b15.png!small)Hook
函数

通过 /proc/kallsyms 获取到可 Hook 的内核符号地址后，Rootkit 使用
[udis86](https://github.com/vmt/udis86)对指定函数进行 Hook。

### 目录隐藏

Syslogk Rootkit Hook 了 VFS 函数来隐藏 /etc/rc-Zobk0jpi/PgSD93ql 文件。Hook 是通过
hk_root_readdir 调用 nw_root_filldir 目录过滤实现的。

![image.png-34.6kB](https://image.3001.net/images/20220712/1657627686_62cd64267e8071a1f1d7e.png!small)部分代码

如上所示，任何包含 -Zobk0jpi 字符串的目录都会被隐藏。这一方式一点都不新鲜，可以查看 Adore-Ng
的[源码](https://github.com/yaoyumeng/adore-ng/blob/master/adore-ng.c#L300)是如何实现的。

### 进程隐藏

Syslogk 进程隐藏的方式比 Adore-Ng 更简单，默认隐藏名为 PgSD93ql 的进程。

![image.png-84.6kB](https://image.3001.net/images/20220712/1657627687_62cd64272197e74ce70d8.png!small)版本比较

### 流量隐藏

Rootkit 通过在 adore_tcp4_seq_show() 函数中利用 strnstr 函数查找特定端口的十六进制字符串，如果发现即删掉。以此，将如
netstat 的 Linux 应用程序查询监听连接时的结果进行过滤。

![image.png-96.6kB](https://image.3001.net/images/20220712/1657627688_62cd64282603a8c5b5d2b.png!small)流量隐藏

这样，在查看失陷主机的连接情况时，就不会出现后门的连接。

### 特制 TCP 数据包

启动虚假 SMTP 服务器的特制 TCP 数据包非常简单，只要数据包符合 TCP 且来源端口为 59318 即可触发。

![image.png-101kB](https://image.3001.net/images/20220712/1657627688_62cd6428ed7e2ea293834.png!small)启动

启动服务前，Rootkit 会调用 pkill_clone_0 终止所有实例。然后通过
call_usermodehelper_setup、call_usermodehelper_setfns 和
call_usermodehelper_exec 的内核 API 启动服务。

> /bin/sh -c /etc/rc-Zobk0jpi/PgSD93ql

停止服务的特制 TCP 数据包要求高很多：

> 检查启用执行标志
>
> 检查 TCP 头中的 ReservedTCP 为 0x08
>
> 检查源端口在 63400 到 63411 之间
>
> 检查源 IP 与目的端口与启动的特制 TCP 数据包一致
>
> 检查硬编码的密钥 D9sd87JMaij

硬编码的密钥的偏移量是通过 TCP 头中的 data offset 进行设置的，将 4 bit 的字节向右移动并乘以 4 后即可指向预期偏移量。

![image.png-29.8kB](https://image.3001.net/images/20220712/1657627689_62cd6429b1f5a076f5653.png!small)偏移量

在分析时，data offset 使用的值为 0x50，右移后会得到 20。这正好是 TCP 头的大小，使用这个值可以将密钥放在数据包数据部分的开头位置。

## 分析 Rekoobe

通过特制 TCP 数据包启动 Rekoobe 后，Rekoobe 看起来像一个普通的 SMTP 服务器。但其中存在后门指令
starttls，在正常情况下该指令是要开始 TLS 协商。

![image.png-69.6kB](https://image.3001.net/images/20220712/1657627690_62cd642a5b909f062df3d.png!small)后门指令

为了触发 Rekoobe 后门，攻击者通过 TLS 发送 0x03 字节，随后是 TLV 格式的编码数据。

![image.png-118.7kB](https://image.3001.net/images/20220712/1657627691_62cd642b35dd429498a5c.png!small)传送数据

## 溯源

如下所示，Rekoobe 显然是基于
[TinySHell](https://github.com/creaktive/tsh/blob/master/tshd.c#L693)开源项目。

![image.png-116.4kB](https://image.3001.net/images/20220712/1657627692_62cd642cb7a949901e631.png!small)相似对比

另一方面，在 Syslogk Rootkit 中也有对 TinySHell 的引用，如下所示：

![image.png-94.6kB](https://image.3001.net/images/20220712/1657627693_62cd642de55121d0ed74d.png!small)相似引用

## 结论

内核 Rootkit 非常难以检测与删除，这些恶意软件已经在高权限层中运行，这种攻击者值得非常注意。

## IOC

> 68facac60ee0ade1aa8f8f2024787244c2584a1a03d10cda83eeaf1258b371f2  
> 11edf80f2918da818f3862246206b569d5dcebdc2a7ed791663ca3254ede772d  
> fa94282e34901eba45720c4f89a0c820d32840ae49e53de8e75b2d6e78326074  
> fd92e34675e5b0b8bfbc6b1f3a00a7652e67a162f1ea612f6e86cca846df76c5  
> 12c1b1e48effe60eef7486b3ae3e458da403cd04c88c88fab7fca84d849ee3f5  
> 06778bddd457aafbc93d384f96ead3eb8476dc1bc8a6fbd0cd7a4d3337ddce1e  
> f1a592208723a66fa51ce1bc35cbd6864e24011c6dc3bcd056346428e4e1c55d  
> 55dbdb84c40d9dc8c5aaf83226ca00a3395292cc8f884bdc523a44c2fd431c7b  
> df90558a84cfcf80639f32b31aec187b813df556e3c155a05af91dedfd2d7429  
> 160cfb90b81f369f5ba929aba0b3130cb38d3c90d629fe91b31fdef176752421  
> b4d0f0d652f907e4e77a9453dcce7810b75e1dc5867deb69bea1e4ecdd02d877  
> 3a6f339df95e138a436a4feff64df312975a262fa16b75117521b7d6e7115d65  
> 74699b0964a2cbdc2bc2d9ca0b2b6f5828b638de7c73b1d41e7fe26cfc2f3441  
> 7a599ff4a58cb0672a1b5e912a57fcdc4b0e2445ec9bc653f7f3e7a7d1dc627f  
> f4e3cfeeb4e10f61049a88527321af8c77d95349caf616e86d7ff4f5ba203e5f  
> 31330c0409337592e9de7ac981cecb7f37ce0235f96e459fefbd585e35c11a1a  
> c6d735b7a4656a52f3cd1d24265e4f2a91652f1a775877129b322114c9547deb  
> 2e81517ee4172c43a2084be1d584841704b3f602cafc2365de3bcb3d899e4fb8  
> b22f55e476209adb43929077be83481ebda7e804d117d77266b186665e4b1845  
> a93b9333a203e7eed197d0603e78413013bd5d8132109bbef5ef93b36b83957c  
> 870d6c202fcc72088ff5d8e71cc0990777a7621851df10ba74d0e07d19174887  
> ca2ee3f30e1c997cc9d8e8f13ec94134cdb378c4eb03232f5ed1df74c0a0a1f0  
> 9d2e25ec0208a55fba97ac70b23d3d3753e9b906b4546d1b14d8c92f8d8eb03d  
> 29058d4cee84565335eafdf2d4a239afc0a73f1b89d3c2149346a4c6f10f3962  
> 7e0b340815351dab035b28b16ca66a2c1c7eaf22edf9ead73d2276fe7d92bab4  
> af9a19f99e0dcd82a31e0c8fc68e89d104ef2039b7288a203f6d2e4f63ae4d5c  
> 6f27de574ad79eb24d93beb00e29496d8cfe22529fc8ee5010a820f3865336a9  
> d690d471b513c5d40caef9f1e37c94db20e6492b34ea6a3cddcc22058f842cf3  
> e08e241d6823efedf81d141cc8fd5587e13df08aeda9e1793f754871521da226  
> da641f86f81f6333f2730795de93ad2a25ab279a527b8b9e9122b934a730ab08  
> e3d64a128e9267640f8fc3e6ba5399f75f6f0aca6a8db48bf989fe67a7ee1a71  
> d3e2e002574fb810ac5e456f122c30f232c5899534019d28e0e6822e426ed9d3  
> 7b88fa41d6a03aeda120627d3363b739a30fe00008ce8d848c2cbb5b4473d8bc  
> 50b73742726b0b7e00856e288e758412c74371ea2f0eaf75b957d73dfb396fd7  
> 8b036e5e96ab980df3dca44390d6f447d4ca662a7eddac9f52d172efff4c58f8  
> 8b18c1336770fcddc6fe78d9220386bce565f98cc8ada5a90ce69ce3ddf36043  
> f04dc3c62b305cdb4d83d8df2caa2d37feeb0a86fb5a745df416bac62a3b9731  
> 72f200e3444bb4e81e58112111482e8175610dc45c6e0c6dcd1d2251bacf7897  
> d129481955f24430247d6cc4af975e4571b5af7c16e36814371575be07e72299  
> 6fc03c92dee363dd88e50e89062dd8a22fe88998aff7de723594ec916c348d0a  
> fca2ea3e471a0d612ce50abc8738085f076ad022f70f78c3f8c83d1b2ff7896b  
> 2fea3bc88c8142fa299a4ad9169f8879fc76726c71e4b3e06a04d568086d3470  
> 178b23e7eded2a671fa396dd0bac5d790bca77ec4b2cf4b464d76509ed12c51a  
> 3bff2c5bfc24fc99d925126ec6beb95d395a85bc736a395aaf4719c301cbbfd4  
> 14a33415e95d104cf5cf1acaff9586f78f7ec3ffb26efd0683c468edeaf98fd7  
> 8bb7842991afe86b97def19f226cb7e0a9f9527a75981f5e24a70444a7299809  
> 020a6b7edcff7764f2aac1860142775edef1bc057bedd49b575477105267fc67  
> 6711d5d42b54e2d261bb48aa7997fa9191aec059fd081c6f6e496d8db17a372a  
> 48671bc6dbc786940ede3a83cc18c2d124d595a47fb20bc40d47ec9d5e8b85dc  
> b0d69e260a44054999baa348748cf4b2d1eaab3dd3385bb6ad5931ff47a920de  
> e1999a3e5a611312e16bb65bb5a880dfedbab8d4d2c0a5d3ed1ed926a3f63e94  
> fa0ea232ab160a652fcbd8d6db8ffa09fd64bcb3228f000434d6a8e340aaf4cb  
> 11edf80f2918da818f3862246206b569d5dcebdc2a7ed791663ca3254ede772d  
> 73bbabc65f884f89653a156e432788b5541a169036d364c2d769f6053960351f  
> 8ec87dee13de3281d55f7d1d3b48115a0f5e4a41bfbef1ea08e496ac529829c8  
> 8285ee3115e8c71c24ca3bdce313d3cfadead283c31a116180d4c2611efb610d  
> 958bce41371b68706feae0f929a18fa84d4a8a199262c2110a7c1c12d2b1dce2  
> 38f357c32f2c5a5e56ea40592e339bac3b0cabd6a903072b9d35093a2ed1cb75  
> bcc3d47940ae280c63b229d21c50d25128b2a15ea42fe8572026f88f32ed0628  
> 08a1273ac9d6476e9a9b356b261fdc17352401065e2fc2ad3739e3f82e68705a  
> cf525918cb648c81543d9603ac75bc63332627d0ec070c355a86e3595986cbb3  
> 42bc744b22173ff12477e57f85fa58450933e1c4294023334b54373f6f63ee42  
> 337674d6349c21d3c66a4245c82cb454fea1c4e9c9d6e3578634804793e3a6d6  
> 4effa5035fe6bbafd283ffae544a5e4353eb568770421738b4b0bb835dad573b  
> 5b8059ea30c8665d2c36da024a170b31689c4671374b5b9b1a93c7ca47477448  
> bd07a4ccc8fa67e2e80b9c308dec140ca1ae9c027fa03f2828e4b5bdba6c7391  
> bf09a1a7896e05b18c033d2d62f70ea4cac85e2d72dbd8869e12b61571c0327e  
> 79916343b93a5a7ac7b7133a26b77b8d7d0471b3204eae78a8e8091bfe19dc8c  
> c32e559568d2f6960bc41ca0560ac8f459947e170339811804011802d2f87d69  
> 864c261555fce40d022a68d0b0eadb7ab69da6af52af081fd1d9e3eced4aee46  
> 275d63587f3ac511d7cca5ff85af2914e74d8b68edd5a7a8a1609426d5b7f6a9  
> 031183e9450ad8283486621c4cdc556e1025127971c15053a3bf202c132fe8f9

## 参考来源

> [Avast](https://decoded.avast.io/davidalvarez/linux-threat-hunting-syslogk-> a-kernel-rootkit-found-under-development-in-the-wild/)

