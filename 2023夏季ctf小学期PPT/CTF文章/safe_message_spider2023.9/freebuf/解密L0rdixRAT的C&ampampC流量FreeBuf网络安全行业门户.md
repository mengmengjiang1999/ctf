**本文介绍了 L0rdix 的控制面板与构建组件，并发现了控制面板中硬编码的密钥`3sc3RLrpd17`。根据该密钥计算的 SHA-256
值用于加密/解密 C&C 流量的 AES 密钥，样本构建时也可以指定该密钥。本文也详细介绍了 L0rdix 的 C&C
通信中使用的加密/解密函数的更多细节，还会讨论如何使用 Python 在 PCAP 文件中自动识别、解密、提取 L0rdix 的 C&C 流量。**

L0rdix 是一个多用途 RAT，2018 年十一月首次在地下犯罪论坛被发现。随后有分析人员分析了该 RAT 的功能，尽管 L0rdix
的作者将价格设置为 4000 卢布（64 美元），这一价格对于很多网络犯罪者来说仍然是一个不可接受的高价。2019 年 6 月，该 RAT
的破解版和管理面板开始通过地下论坛传播。我对它的管理面板特别好奇，通过深入分析可以更好地在野检测该类威胁。

![111.png](https://image.3001.net/images/20200411/1586598061_5e9190ad0b74c.png!small)

## 管理面板

管理面板由三个组件组成，一个 HTTP Web 服务器，运营者通过该页面管理 Bot；一个预制的 MySQL 数据库存储失陷主机的数据；一个向 Bot
发送命令并接收数据的 PHP 脚本。默认情况下，其登录页的 URI 为 webserver.tld/admin_login。不像其他 RAT，L0rdix
的登陆页面非常简单并且不显示其名称。

![222.png](https://image.3001.net/images/20200411/1586598073_5e9190b97590b.png!small)

![333.png](https://image.3001.net/images/20200411/1586598084_5e9190c42cd2b.png!small)

通过查询 MySQL 数据库可以读取其失陷主机的相关信息，L0rdix 数据库默认包含七张表，这表明该 RAT 也并不复杂。

![444.png](https://image.3001.net/images/20200411/1586598096_5e9190d091947.png!small)

失陷主机信息包括基本的硬件和配置信息、主机位置使用一个 IP 定位库、矿工的哈希率（使用开源的
XMRig）、下载持久化的控制命令。除此之外还有许多与挖矿相关的配置信息，例如失陷主机使用的 GPU 型号。在我们的跟踪中，L0rdix 参与挖矿行动可能与
2019 上半年的加密货币升值有关。

## 默认凭据

该控制面板带有默认的凭据（用户名：root、密码：toor），这表明该开发者可能十分熟悉 Kali 发行版，给出的默认凭据是相同的。

![555.png](https://image.3001.net/images/20200411/1586598107_5e9190db7b056.png!small)

面板支持向 Bot 发送八个命令，也可以添加自定义新命令。包括：

  * 下载与执行
  * 升级
  * 打开页面（可见）
  * 打开页面（不可见）
  * cmd
  * 终止进程
  * 上传文件
  * HTTP 洪水

## C&C 命令的加密与解密

L0rdix 的 C&C 通信使用 256 位密钥、CBC 模式的 AES 对称加密。构建样本时攻击者可以确定其加密的密钥，根据其密钥计算 SHA-256
值。前 32 个字符被用作 AES 加密密钥，面板的加密函数使用 PHP 的 openssl_encrypt 函数。该函数要求 16 个字节的初始化向量，但
L0rdix 的开发者使用了 16 个空字节。分析的面板也带有默认密钥 `3sc3RLrpd17`。密文再使用 base64 进行编码，随后调用 PHP 的
str_replace 函数将所有的 `+` 字符替换为 `~`。解密方法是标准的反向操作，字符串替换 -> base64 解码 ->
openssl_decrypt。

基于该加密和解密功能的实现，每个面板的运营者都为每个 Bot 使用相同的密钥。这样就可以从已知密钥的控制面板对应的任何 Bot 之间解密 C&C 流量。

![666.png](https://image.3001.net/images/20200411/1586598118_5e9190e63dc58.png!small)

![777.png](https://image.3001.net/images/20200411/1586598127_5e9190efec24b.png!small)

## 构建

构建过程非常简单，只有几个可配置的选项，包括指定控制面板的 IP 地址或域名、生成的 Mutex、与启用某些恶意软件的功能。

![888.png](https://image.3001.net/images/20200411/1586598144_5e9191006182d.png!small)

L0rdix 具备反分析措施，如枚举正在运行的进程，如果发现常见的分析工具就停止运行。该 RAT 还会检测运行环境是否为虚拟机或 Sandboxie。

![999.png](https://image.3001.net/images/20200411/1586598155_5e91910bb5a51.png!small)

L0rdix 试着将 C&C 流量隐藏在 Windows 10 中的 Firefox 53 中，硬编码使用了相同的 User-Agent
字符串：`Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101
Firefox/53.0`。

还包含了 WMI 的命名空间 `root\SecurityCenter2` 来识别安装的反病毒软件并发送到控制面板。

![101010.png](https://image.3001.net/images/20200411/1586598168_5e9191189a266.png!small)

## 配置结构

L0rdix 的配置包括十个字段，这些配置信息会在加密后通过 HTTP POST 请求发送给控制面板的 connect.php 页面。Bot
会根据配置设置发送相似的 POST 请求进行升级。

## 配置字段

请求字符串| 配置字段  
---|---  
h=| 硬件 ID  
o=| 操作系统  
c=| CPU  
g=| GPU  
w=| 安装的反病毒软件  
p=| 当前用户权限  
r=| HASH Rate  
f=| 当前使用配置  
rm=| 内存  
d=| Drives  
  
## 加解密步骤

L0rdix 按照如下步骤对 C&C 流量进行加密：

  1. 使用 CBC 模式的 AES 算法加密明文，密钥长度为 256 比特，初始向量长度为 16 字节
  2. 密文使用 base64 编码
  3. 使用 ~ 替换 + 字符
  4. 密文使用 URL 编码进行编码

![11.png](https://image.3001.net/images/20200416/1587018536_5e97fb2885a8a.png!small)

例如，明文 `Windows 7 Enterprise` 最终结果为
`buNpZksa9PSEshjHiM9XNI84ku2X6Zy2Syr7zdzvxMM%3d`。可以按照上述操作步骤逆序处理即可得到明文：

  * URL 解码后：buNpZksa9PSEshjHiM9XNI84ku2X6Zy2Syr7zdzvxMM=
  * base64 解码后：6ee369664b1af4f484b218c788cf57348f3892ed97e99cb64b2afbcddcefc4c3
  * AES 解密后：Windows 7 Enterprise

## 默认密钥

分析了很多在野样本后可以发现许多控制面板都使用默认密钥来进行加密。重复利用可能存在两个原因：

  1. 买家并未修改控制面板默认提供的密码
  2. 这些样本都是由一个攻击者部署的

基于加密/解密的实现方式，每个控制面板的运营者都必须在每个受控主机上使用相同的密钥。除此之外还有更加有力的证据表明第一个猜测可能是真实原因。其他的编程教程中有使用
C# 和 PHP 语言编写 AES 加解密代码的示例，L0rdix 服务端加解密函数与教程类似，共享了加密方法（CBC-256）、初始向量（16 NULL
字节）、程序语言（C# 与 PHP）。L0rdix 可能复用了教程的程序实现，并决定不修改加密密钥。

![22.png](https://image.3001.net/images/20200416/1587018551_5e97fb3776f1b.png!small)

![33.png](https://image.3001.net/images/20200416/1587018562_5e97fb425975a.png!small)

## 自动解密

由于使用对称密钥进行加密，因此可以使用 Python 编写解密脚本。该脚本解析 PCAP 文件中 L0rdix 的 C&C 流量并解密。脚本使用
Pyshark 解析 PCAP 文件并基于预期的结构识别 C&C 流量。例如，L0rdix 配置中具有十个字段，C&C
的字符串中应该具有至少十个字符串。这些字符串使用 Pycryptodome 库进行 AES 解密与后续操作。

脚本也可以提取 L0rdix 在失陷主机上采集的屏幕截图。可疑流量使用默认密钥进行解密，或者使用用户通过 -k
参数提供的密钥进行解密。如果攻击者未改变默认的密钥可以直接通过脚本进行处理，否则也可以通过静态分析样本提取得到 L0rdix 的密钥。

下图显示了执行 `decrypt_l0rdix_c2.py -p l0rdix_c2.pcap` 解密 L0rdix 的 C&C 流量：

![44.png](https://image.3001.net/images/20200416/1587018575_5e97fb4f96354.png!small)

![55.png](https://image.3001.net/images/20200416/1587018585_5e97fb59cfeb2.png!small)

## 结论

基于泄露的数据，L0rdix 自从被发现以来没有表现出高度进化的特性。尽管该 RAT 被认为是一种通用型的
RAT，但主要还是聚焦于挖矿。这可能也是作者为了迎合挖矿僵尸网络日益增长的需求。

## Yara 规则

    
    
    rule win_l0rdix {
        meta:
            author = "Alex Holland (Bromium Labs)"
            date = "2019-07-19"
            sample_1 = "18C6AAF76985404A276466D73A89AC5B1652F8E9659473F5D6D656CA2705B0D3"
            sample_2 = "C2A4D706D713937F47951D4E6E975754C137159DC2C30715D03331FC515AE4E8"
    
        strings:
            $ua = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0" wide // Firefox 53 on Windows 10
            $sig = "L0rdix" wide ascii
            $sched_task = "ApplicationUpdateCallback" wide
            $exe = "syscall.exe" wide
            $cnc_url_1 = "connect.php?" wide
            $cnc_url_2 = "show.php" wide 
            $browser_1 = "\\Kometa\\User Data\\Default\\Cookies" wide 
            $browser_2 = "\\Orbitum\\User Data\\Default\\Cookies" wide
            $browser_3 = "\\Amigo\\User\\User Data\\Default\\Cookies" wide
            $coin_regex_1 = "[13][a-km-zA-HJ-NP-Z1-9]{25,34}" wide // Bitcoin
            $coin_regex_2 = "0x[a-fA-F0-9]{40}" wide // Ethereum
            $coin_regex_3 = "L[a-zA-Z0-9]{26,33}" wide // Litecoin
    
        condition:
            uint16(0) == 0x5A4D and (any of ($ua,$sig,$sched_task,$exe)) and (any of ($cnc_url_*)) and (any of ($browser_*)) and (any of ($coin_regex_*))
    }
    

***参考来源：[Bromium](https://www.bromium.com/an-analysis-of-l0rdix-rat-panel-and-builder/)，FB 小编 Avenger 编译，转载请注明来自 FreeBuf.COM**

