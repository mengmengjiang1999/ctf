## 0x00 HinataBot 僵尸网络

今年初，Akamai 的研究人员发现了一个新型恶意僵尸网络,它以 Realtek SDK、华为路由器和 Hadoop YARN 服务器为目标,将设备引入到
DDoS 群中,有可能进行大规模攻击。这个新型僵尸网络是研究人员在自己的 HTTP 和 SSH 蜜罐上发现的,该僵尸网络利用了 CVE-2014-8361
和 CVE-2017-17215
等漏洞。![](https://image.3001.net/images/20230825/1692965725_64e89b5d994ff379b2a34.png!small)

Akamai 表示， **HinataBot** 以 **Mirai** 为基础，是基于 **Golang** 的变体。

该恶意软件通过对 SSH 端点进行暴力攻击或使用已知漏洞的感染脚本和 RCE
有效载荷进行分发。感染设备后,恶意软件会默默地运行,等待来自命令和控制服务器的命令执行。

HinataBot 的旧版本支持 HTTP、UDP、ICMP 和 TCP
洪泛攻击，但较新的变体只具有前两种。然而，即使只有两种攻击模式,该僵尸网络也可以潜在地进行非常强大的 DDOS。

来源：[参开资料 [1]](https://www.bleepingcomputer.com/news/security/new-hinatabot-botnet-could-launch-massive-33-tbps-ddos-attacks/)

## 0x01 Golang 逆向概览

随着 Golang 恶意软件的增多，Golang 逆向无论分析手法还是工具插件也逐渐成熟。本文并不打算详细展开，只在这里简单提及要点，下图来自 [go-parser](https://github.com/0xjiayu/go_parser)的 Golang
二进制文件可获得的关键信息：![](https://image.3001.net/images/20230825/1692965971_64e89c53affac2da08b91.png!small)

### 0x01-00 要点

  *  **符号**

Golang 二进制编译后的大小一直受到诟病，通过聊胜于无的 strip
可以稍微缩小空间，但符号缺失给逆向造成困难，所以第一步(如果缺少符号)一般是函数符号恢复。

恢复函数符号的关键是 **pclntab** ( **Program Counter Line Table / 程序计数器行数映射表** )
的定位和解析。pclntab 包含了函数表 (Function Table) 和 源码文件路径列表 (File Table)
。![](https://image.3001.net/images/20230825/1692965983_64e89c5f3513cbc3b05a1.png!small)

通过 Function Table 结构偏移可以恢复其函数符号，遍历整个 Function Table
可恢复所有的函数名，当然可以直接使用插件恢复，这里不再赘述。

  *  **调用**

Go 语言和 C 不同，不是使用栈指针寄存器和栈基址寄存器确定函数栈的，而是使用
[**连续栈**](https://tiancaiamao.gitbooks.io/go-internals/content/zh/03.5.html)。在Go的运行时库中，每个 goroutine 对应一个结构体
G，大致相当于进程控制块的概念。这个结构体中存了 stackbase 和stackguard，用于确定这个 goroutine 使用的栈空间信息。每个 Go
函数调用的前几条指令，先比较栈指针寄存器跟 g->stackguard，检测是否发生栈溢出。如果栈指针寄存器值超越了 stackguard
就需要扩展栈空间。![](https://image.3001.net/images/20230825/1692965995_64e89c6b438ab824b4c4d.png!small)

Go 语言函数中调用的栈空间由上层调用函数来维护，调用参数、返回值都由调用者在栈中预留空间， **传入参数和返回值都是通过栈空间里的内存**
，所以参数和返回值不好区分。一般来说，如果函数有返回值的话，返回值总是最后面的 arg，即距离栈底较近的位置。

  *  **调试**

绝大部分 Golang 调试资料跟 [**go-delve**](https://github.com/go-delve/delve)和 **[GDB 的
Go 调试插件](https://golang.org/doc/gdb)有关。但是这两个工具的使用需要有调试符号甚至 Go 项目的源码。然而我们要分析的
Go 恶意软件，绝大部分是没有调试符号的。而无符号调试归根结底还是下断点**的问题，这样只能结合静态分析，还有通过经验排除 runtime
内部协程操作的干扰。

>   *  **tips**
>

>   1. 字符串分割：go中的字符串并不以‘/0’分割，每次引用都会有参数标识长度。
>   2. GC write barrier 机制：Golang
> 内部有比较高效的垃圾回收（GC）机制，逆向时会遇到很多runtime.gcWriteBarrier() 函数调用，只要知道是 runtime GC
> Barrier 相关的常规操作即可。
>

### 0x01-01 工具

  *  **[redress](https://go-re.tk/redress/)**

Go 逆向工程工具包 （[go-re.tk](https://go-re.tk/)） 是一个新的开源工具集，用于 分析 Go
二进制文件。该工具旨在从Go二进制文件中提取尽可能多的元数据，以协助逆向工程和恶意软件分析。

 **redress** 使用十分简单，可提取还原编译信息、Struct、interface 、源码路径等信息辅助逆向，在后文分析中也将使用到。

    
    
    $ redress -h
    Usage of redress:
      -compiler
        	Print information
      -filepath
        	Include file path for packages
      -interface
        	Print interfaces
      -method
        	Print type's methods
      -pkg
        	List packages
      -src
        	Print source tree
      -std
        	Include standard library packages
      -struct
        	Print structs
      -type
        	Print all type information
      -unknown
        	Include unknown packages
      -vendor
        	Include vendor package
    

  * [go-parser](https://github.com/0xjiayu/go_parser)

go-parser 是其作者受
[golang_loader_assist](https://github.com/strazzere/golang_loader_assist)和
[jeb-golang-analyzer](https://github.com/pnfsoftware/jeb-golang-analyzer)启发，为
IDAPro 写了一个更完备的 Go 二进制文件解析工具。其核心功能如下：

  1. 自动定位 **firstmoduledata** 的位置并解析；

  2. 根据 firstmoduledata 中的信息定位到 **pclntab** (PC Line Table)，并从 pclntab 入手解析、恢复 **函数符号** ，抽取 **源码文件列表** ；

  3. 解析 **strings** 和 **string pointers** ；

  4. 根据 **firstmoduledata** 中的信息，解析所有 **types** 并为 **types** 各种属性打上有意义的 **comment** 或 dref；

  5. 解析 **itab** (Interface Table)。![](https://image.3001.net/images/20230825/1692966373_64e89de5decb51607cdd7.png!small)

  * [Delve](https://github.com/go-delve/delve)

Delve 是一个 Go 语言的第三方调试器，是 GDB 调试器的有效替代品。与GDB相比，它能更高的理解 Go 的运行时，数据结构以及表达式。Delve
目前支持 Linux，OSX 以及 Windows 的 amd64
平台。![](https://image.3001.net/images/20230825/1692966399_64e89dff1168911b92976.png!small)

## 0x02 HinataBot 分析

### 0x02-00 样本获取

样本获取途径可参考文末资料中的[链接](https://bbs.kanxue.com/thread-265627.htm)。

由于样本本身具备破坏性，从公开手段获取也并不容易。在此次分析中，笔者使用的方式是先找到恶意软件Hash列表，通过Hash在上述样本网站中搜索。![](https://image.3001.net/images/20230825/1692966411_64e89e0b89c56aee694df.jpg!small)

在 **hybrid-analysis** 和 **[tria.ge](http://tria.ge)** 样本网站都找到了 Linux X86_64 (
**sha256** : 8a84dc2a9a06b1fae0dd16765509f88f6f54559c36d4353fd040d02d4563f703)
的二进制样本，前者对下载有所限制，后者可以直接下载，密码解压默认为 **infected** 。

 **经过分析测试，样本真实有效，请谨慎下载 ！！！**

### 0x02-01 样本分析

  * 基本信息

该样本为 x86-64 ELF 格式，SHA256 与样本网站提供的也相符合，注意这里显示是 stripped：

    
    
    iot@attifyos ~/> file hinata
    hinata: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/l, stripped
    iot@attifyos ~/> sha256sum hinata
    8a84dc2a9a06b1fae0dd16765509f88f6f54559c36d4353fd040d02d4563f703  hinata
    

首先通过 redess
获取一些基本信息：![](https://image.3001.net/images/20230825/1692966430_64e89e1e369e669417d5a.png!small)

查看使用的
packages:![](https://image.3001.net/images/20230825/1692966439_64e89e27e2fd94eb19b17.png!small)

source
文件信息：![](https://image.3001.net/images/20230825/1692966449_64e89e31d5de50ef35249.png!small)

gomod
信息：![](https://image.3001.net/images/20230825/1692966459_64e89e3bcf2a3fdd947da.png!small)

Struct
信息：![](https://image.3001.net/images/20230825/1692966469_64e89e4575a4ebeb4975d.png!small)

interface
信息：![](https://image.3001.net/images/20230825/1692966479_64e89e4fca3c1fa1ddd00.png!small)

使用 IDA 7.5
打开，符号没有识别：![](https://image.3001.net/images/20230825/1692966490_64e89e5abd62e3abb7af9.png!small)

上文提到，该二进制文件是stripped，但是对于golang 二进制文件来说，可以通过 **pclntab** 恢复，也可以直接使用 go-parser
等插件辅助恢复。当然还有更简单的方式，就是用 IDA 7.7 以上的版本打开，虽然 F5
的结果明显是错的，但是已足够强大：![](https://image.3001.net/images/20230825/1692966500_64e89e64c466674031ca9.png!small)

  * 结构剖析

直接从 **main.main ()** 函数入手，可以看出 hinata
的主体结构并不复杂：![](https://image.3001.net/images/20230825/1692966523_64e89e7b43b13339e45e5.png!small)

这里只使用了一次 F5，在主函数错误还不是很明显，之后的分析直接通过汇编代码更加清晰。

程序首先使用 **os_stat()** 作系统检查，如果发现错误或者已经有实例运行即退出，并保留日志。通过系统校验后就进入
**main_startProcess()** ，并调用 **os_startProcess()** 开始工作。但是这里只显示出一条 goroutiue
的分支，通过汇编的图模式可以清楚看到 main 函数在初始化后执行了循环程序 **main_runForever()**
，主功能在这个函数中。![](https://image.3001.net/images/20230825/1692966534_64e89e863966c63251285.png!small)

 **main_runforever** 又调用了 **main_runforever_fun1** ，最后执行 **startAttack**
：![](https://image.3001.net/images/20230825/1692966552_64e89e982b4a09b2f11b1.png!small)

![](https://image.3001.net/images/20230825/1692966574_64e89eae0ed4aa92c84f8.png!small)

其主功能调用为：

    
    
     **main.main - > main.runForever -> main.runForever.func1 -> main.startAttack
    **

在 **main.startAttack** 函数中执行攻击操作。

  * 功能澄清

分析 hinata 这类的 Bot 比较关心的是 C2 连接、命令下发和主要功能。选择 Golang
语言主要功能实现一般依靠标准库，简单方便，单从函数名字符串就能大概知道有哪些功能：![](https://image.3001.net/images/20230825/1692966584_64e89eb8438d90c954893.png!small)

首先是 C2 服务器，该 Bot 会连接 **77.73.131.247** 的 **1420** 端口，返回系统信息，之后等候命令，该功能在
**main.runForever**
函数中实现：![](https://image.3001.net/images/20230825/1692966592_64e89ec0cba1f948b8e7a.png!small)

连接时会做一些校验：![](https://image.3001.net/images/20230825/1692966601_64e89ec91947b3f6733a3.png!small)

连接成功后会打印相关信息，也是从这里定位到 C2
连接的位置：![](https://image.3001.net/images/20230825/1692966609_64e89ed168c4a9af35763.png!small)

命令的格式如下，根据不同类型的攻击略有不同：

    
    
     **API_CONNECTION_ATTACK: [ATTACK_TYPE] [TARGET] [DURATION] [OPTIONS]**

![](https://image.3001.net/images/20230825/1692966628_64e89ee4270a881d29886.png!small)

通过逆向 **main.startAttack**
函数可以看到功能分支：![](https://image.3001.net/images/20230825/1692966636_64e89eec509ba854be161.png!small)

基本是实现各种类型的 DOS 攻击。可以看到所有的攻击函数都有 4 各参数，通过 C2 服务器下发。

这里就以最左边的 **main_udp_flood**
为例作分析，其他功能大同小异。![](https://image.3001.net/images/20230825/1692966647_64e89ef76820d778096a4.png!small)

函数使用 Golang 的标准函数 **net_ResolveUDPAddr** 解析地址和端口，通过 **net_DialUDP** 函数连接 UDP
实现 DOS 攻击。值得注意的是 **mov ebx,num** ，这里分别是 3 和 5，就是上文 tips
提到的字符串长度标识，需要手动识别设置，IDA 无法自动分割。当然也利用 Golang 自身优势，使用 work pool 来增加 DOS
效果。http、icmp 等 flood
也都是这个逻辑，这里不再赘述。![](https://image.3001.net/images/20230825/1692966655_64e89eff7074ebf4608c7.png!small)

  * 动态测试

 **运行需谨慎！！！**

新版的 hinata 需要 **HINATA_START_NICE** 关键字启动，笔者只下载到旧版的样本，可以直接运行。

可以调试改变代码逻辑修改 C2 地址，笔者直接将其设为了本地地址。通过监听 1420 端口发现 Bot
实现回连，并返回了系统信息：![](https://image.3001.net/images/20230825/1692966664_64e89f08151471cfc9cb2.png!small)

为了和 Bot 交互，需要完善 C2 功能，这里直接使用了 Akamai 的现成脚本：

    
    
    #!/usr/bin/env python
    from pwn import *
    import time
    l = listen(1420)
    l.wait_for_connection()
    time.sleep(1)
    l.send(b'API_CONNECTION_SIGNAL_OK')
    while True:
        data = l.recv()
        if data: 
            print(time.time(), data)
            if data == b'API_CONNECTION_SIGNAL_CHECK':
                continue
        else:
            print(time.time(), 'no data recv\\'d')
        cmdf = open('cmd.txt','r')
        cmdt = cmdf.read()
        cmdf.close()
        if cmdt == "":
            cmdt = b'API_CONNECTION_SIGNAL_OK'
        print(time.time(), 'SENT:', cmdt)
        l.send(cmdt)
    
    # cmd.txt
    # API_CONNECTION_ATTACK: 1 127.127.127.127 120 1522222
    

主要测试了 **udp_flood**
功能：![](https://image.3001.net/images/20230825/1692966675_64e89f1326853e83d17b8.png!small)

调试过程不再展开，笔者觉得，对于没有源码的 Golang 程序可能使用带插件的 GDB 比 Delve 更优。

最后给出 hinata 二进制文件的 yara rules，更多 IOC 可查看参考链接中 [Akamai
相关分析](https://www.akamai.com/blog/security-research/hinatabot-uncovering-new-golang-ddos-botnet)。

    
    
    rule detect_hinatabot_strings {
        Meta:
                     description = "This rule detects HinataBot binaries."
            confidence = "high"
        strings:
            $s1 = "HINATA_START_NICE"
            $s2 = "API_CONNECT_BOT"
            $s3 = "Connection to CNC is OK!"
            $s4 = "API_CONNECTION_SIGNAL_CHECK"
            $s5 = "API_CONNECTION_SIGNAL_OK"
            $s6 = "API_CONNECTION_ATTACK"
            $s7 = "Hinata already running"
            $s8 = "API_CONNECTION_KILL_ALL"
            $s9 = "hinata_exists"
            $s10 = "hinata_loaded"
            $s11 = "HINATA_"
        condition:
            3 of ($s*)
    }
    

## 0x03 参考资料

[New ‘HinataBot’ botnet could launch massive 3.3 Tbps DDoS
attacks](https://www.bleepingcomputer.com/news/security/new-hinatabot-botnet-could-launch-massive-33-tbps-ddos-attacks/)

<https://github.com/0xjiayu/go_parser>

[New GoLang-Based HinataBot Exploiting Router and Server Flaws for DDoS
Attacks](https://thehackernews.com/2023/03/new-golang-based-hinatabot-exploiting.html)

[新的 "HinataBot "僵尸网络可以发动大规模的 DDoS攻击 -FreeBuf网络安全行业门户](https://www.freebuf.com/news/361013.html)

[连续栈 · 深入解析Go](https://tiancaiamao.gitbooks.io/go-internals/content/zh/03.5.html)

[Free Automated Malware Analysis Service - powered by Falcon
Sandbox](https://www.hybrid-analysis.com/sample/8a84dc2a9a06b1fae0dd16765509f88f6f54559c36d4353fd040d02d4563f703)

[Uncovering HinataBot: A Deep Dive into a Go-Based Threat |
Akamai](https://www.akamai.com/blog/security-research/hinatabot-uncovering-new-golang-ddos-botnet)

[Malware sandboxing report by Hatching
Triage](https://tria.ge/230320-vgdlhagf2w)

[\\[分享\\]分享一些平时在进行恶意代码分析时常用的网站-软件逆向-看雪-安全社区|安全招聘|kanxue.com](https://bbs.kanxue.com/thread-265627.htm)

[连续栈 · 深入解析Go](https://tiancaiamao.gitbooks.io/go-internals/content/zh/03.5.html)

