Cobalt Strike 广泛被攻击者所使用，暂时还没有可用于 Linux 平台的官方 Cobalt Strike。

2021 年 8 月，Intezer 发现了一个全新的、ELF 的 Cobalt Strike Beacon，将其命名为 Vermilion
Strike。该样本使用 Cobalt Strike 的 C&C 协议与 C&C 服务器通信，并且具备远程访问、上传文件、运行 Shell
命令、写入文件等功能。

在撰写本文时，没有任何引擎检出该恶意软件，该恶意软件由马来西亚上传。

自从 8 月以来的遥测数据，该攻击持续活跃，针对世界各地的电信公司、政府机构、IT
公司、金融机构和咨询公司。由于受害者的范围有限，该恶意软件应该是用于定向攻击而不是大规模传播。

进一步分析，也发现了使用相同 C&C 的 Windows 样本，也是 Cobalt Strike Beacon 的重新实现，且 Windows 和 ELF
样本共享相同的功能。

## Linux 样本

该样本从马来西亚上传到 VirusTotal 中，截止到撰写本文时 VirusTotal 仍然没有被检出。

![](https://image.3001.net/images/20210921/1632213131_6149988b6bb5948fa6448.png!small)

该恶意文件与此前发现的 Cobalt Strike 样本共享字符串，并且会触发相关的 Yara 检测规则。ELF 样本通过动态链接使用 OpenSSL，基于
RedHat 的发行版上的 OpenSSL 的共享对象名称与其他 Linux 发行版不同。因此，该恶意软件只能在基于 RedHat
的发行版上运行。![](https://image.3001.net/images/20210921/1632213134_6149988e3713bdc88a10f.png!small)

### 初始化

该样本使用守护进程维持自身运行，使用 `0x69`作为异或密钥解密配置文件，该密钥也是 Cobalt Strike 加密配置常用的数值。

Vermilion Strike 的配置格式与 Cobalt Strike 相同，因此提取 Cobalt Strike 配置的工具也可用于提取
Vermilion Strike
配置。![](https://image.3001.net/images/20210921/1632213140_61499894442142c135848.png!small)

在堆中进行进一步的解密，其中包含 Beacon 所需的解码字符串、密钥和值。随后生成一个 SHA256 哈希值，该哈希值来源于线程 ID
的随机数，该值将会在 DNS beaconing
中使用。![](https://image.3001.net/images/20210921/1632213143_614998976400e52ec0001.png!small)

接着对机器进行指纹识别，生成一个随机数并获取进程 ID。使用 `uname`获取机器的内核版本，并通过
`getifaddrs`对网络信息进行指纹识别。遍历网络接口收集不等于 `127.0.0.1`的 IPv4
地址接口。![](https://image.3001.net/images/20210921/1632213147_6149989b9c3b19a1876a6.png!small)

紧接着，对本地密码数据进行指纹识别，获取有关有效用户 ID
的信息。![](https://image.3001.net/images/20210921/1632213150_6149989e3652777a011b7.png!small)

随后对主机名进行指纹识别，收集到的信息被格式化成一个字符串，使用 RSA 加密并用 base64 编码，这也是 Cobalt Strike 的 C&C
通信的标准方式。![](https://image.3001.net/images/20210921/1632213153_614998a1a4172994661d1.png!small)

以 `1.0.1.LR`开始的字符串似乎表明内部版本。在 Windows 版本的 Vermilion Strike 中也有类似的字符串 `W1.0.1`。

加密的 Payload 以 `0xbeef`开头，与 Cobalt Strike 使用的相同。

### C&C

Vermilion Strike 支持通过 A 记录和 TXT 记录进行 DNS 隐蔽信道的传输。首先向硬编码的字符名发起 DNS 请求，获得返回的 IP
地址，触发 Beacon
的行为更改。![](https://image.3001.net/images/20210921/1632213157_614998a56bf9c44aa33e4.png!small)

TXT 查询的结果中包含 AES 加密结合 base64
编码的结构：![](https://image.3001.net/images/20210921/1632213159_614998a7bda8bf00e9af4.png!small)

解密如下所示：![](https://image.3001.net/images/20210921/1632213161_614998a9683decbd6528c.png!small)

支持的行为包括：

> 更改工作目录
>
> 获取当前工作目录
>
> 追加/写入文件
>
> 上传文件到 C&C 服务器
>
> 通过 popen 执行命令
>
> 获取磁盘分区
>
> 列出文件

恶意软件使用单独的线程来执行任务。Vermilion Strike 支持 DNS、HTTP、ICMP 三种方式与 C&C 服务器通信。

## Windows 样本

调查 Linux 样本时发现了 Windows
样本。首先发现的样本（3ad119d4f2f1d8ce3851181120a292f41189e4417ad20a6c86b6f45f6a9fbcfc）是一个
32 位的 Stager，通过 HTTP 从 C&C 服务器（160.202.163.100）获取 DLL 文件并在内存中执行。

下一阶段 DLL 文件（7129434afc1fec276525acfeee5bb08923ccd9b32269638a54c7b452f5493492）在
2019 年由 Silas Cutler 首次发现。除了 Windows
平台外，功能几乎完全相同，如下所示：![](https://image.3001.net/images/20210921/1632213165_614998aded0d73a5be68b.png!small)

DLL 文件具有与 ELF 文件相同的 C&C 服务器，以及一个额外的域名（amazon.hksupd.com）。

一个新 Payload（e40370f463b4a4feb2d515a3fb64af1573523f03917b2fd9e7a9d0a741ef89a5）与
2019 年的样本共享了很多代码。该样本与另一个 Windows 版本的 Vermilion Strike 包含 ELF
类似的字符串（`W1.0.1`）。![](https://image.3001.net/images/20210921/1632213170_614998b20ad98ae8097ec.png!small)

## 结论

Vermilion Strike 和其他 Linux 威胁仍然是一个持续的威胁。通常来说，Linux 威胁的检测率通常都低于 Windows 威胁。

Vermilion Strike 并不是 Cobalt Strike Beacon 的唯一 Linux 版本实现。另一个基于 Go 的开源项目
[geacon](https://github.com/darkr4y/geacon)，也是另一个实现，Vermilion Strike 也不会是最后一个。

## IOC

> 294b8db1f2702b60fb2e42fdc50c2cee6a5046112da9a5703a548a4fa50477bc  
> 3ad119d4f2f1d8ce3851181120a292f41189e4417ad20a6c86b6f45f6a9fbcfc  
> 7129434afc1fec276525acfeee5bb08923ccd9b32269638a54c7b452f5493492  
> c49631db0b2e41125ccade68a0fe7fb70939315f1c580510e40e5b30ead868f5  
> 07b815cee2b85a41820cd8157a68f35aa1ed0aa5f4093b8cb79a1d645a16273f  
> e40370f463b4a4feb2d515a3fb64af1573523f03917b2fd9e7a9d0a741ef89a5  
> 160.202.163.100  
> update.microsofthk.com  
> update.microsoftkernel.com  
> amazon.hksupd.com

## 参考来源

> [Intezer](https://www.intezer.com/blog/malware-analysis/vermilionstrike-> reimplementation-cobaltstrike/)

