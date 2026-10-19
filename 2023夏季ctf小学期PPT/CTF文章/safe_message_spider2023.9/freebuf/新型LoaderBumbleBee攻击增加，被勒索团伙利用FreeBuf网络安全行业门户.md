BumbleBee 恶意软件由 Google TAG 于 2022 年 3 月首次披露。最近，研究人员发现 BumbleBee
的在野活动变得频繁，经常与勒索团伙配合投递勒索软件。该恶意软件仍然在不断开发与改进，提醒注意该威胁。

研究人员发现近期 BumbleBee 的活跃 C&C 服务器数量显著增加，并且发现了多个版本的更新与改进。

## 技术分析

BumbleBee 恶意软件是一个比较复杂的 Loader，为了阻碍安全人员进行分析，使用了多种规避技术手段进行隐藏。

### 感染链

攻击者向目标发送一封电子邮件，带有一个 ISO 附件文件，ISO 文件中通常包含用于执行 DLL 文件的 LNK 文件。

LNK 被执行时，会使用 `rundll32.exe`运行命令（`C:\\Windows\\System32\\rundll32.exe
procsvc.dll,HWgullOFkZ`）启动恶意 DLL 文件：

![image.png-263.5kB](https://image.3001.net/images/20220620/1655717475_62b03e63e0f63e17a020b.png!small)示例附件文件

这种攻击方式越来越被广大攻击者所使用，甚至 APT 组织也开始使用。因为 Microsoft Office 产品中默认禁用 VBA
宏，传统的攻击方式成功率开始降低。

### 版本更新

BumbleBee 的 DLL 文件解密后将一个 PE 文件加载到内存中，转存数据即可得到负载文件。该恶意软件几乎完整拷贝开源项目 al-khaser
中的反检测技术。例如对虚拟环境的检查，避免在分析环境中执行：

![image.png-208.5kB](https://image.3001.net/images/20220620/1655717476_62b03e64aecdd7335df9e.png!small)检查虚拟机

加载 PE 后，恶意软件进行 RC4 解密获得 C&C 的 IP 地址。该方法还用于其他去混淆处理：

![image.png-403.3kB](https://image.3001.net/images/20220620/1655717477_62b03e656f39a38f879f8.png!small)去混淆

发现的大多数样本都使用 RC4 算法对三个数据块进行了混淆：

> C&C 的 IP 地址与端口
>
> 标识 ID
>
> 一个数字（通常为 444 或者 4444）

![image.png-216.5kB](https://image.3001.net/images/20220620/1655717478_62b03e66779b8aa42ebeb.png!small)去混淆

BumbleBee 通过 C&C 服务器拉取后续 Payload，如 Meterpreter、Cobalt Strike 或其他。

## 追踪 BumbleBee C&C 基础设施

根据 BumbleBee C&C 服务器使用的 SSL 证书与 HTTP 响应，借助网空搜索引擎就能够以独特的模式发现 BumbleBee C&C 服务器。

四月初只有 5 个 C&C 服务器，到六月份已有一百余个：

![image.png-23.7kB](https://image.3001.net/images/20220620/1655717479_62b03e6734063eb57b81e.png!small)C&C
服务器数量演化

由此可见，BumbleBee 在攻击者中越来越受欢迎。

## 总结

BumbleBee
在短短两个月内快速发展，已经成为一个不可忽视的主要威胁。获取访问能力后，攻击者就可以进一步进行攻击。随着勒索团伙开始与之合作，组织必须保护自己的资产免受
BumbleBee 的侵害。

## IOC

> e2147cb6039d1b065b0d59d6e60a1e5f526415afefdfddcbbd7b1e8a33194d64  
> 064d21a62fc8718a707c3cf6ca91fddeb2fd407dfee47a923638a91a57b338a4  
> 7140becbc882cab84038ad87e977cd3cb0dc864d2437eb1e2aebab78cc3eb193  
> 0f78561577ce1a5ab8b98634fb9b2ff0392e173fb354e3625f6bab53e0f28b05  
> 94f7bc1e910866c5ed1b06242e82c8d5379d143123ff255b87fc78db98c49ae2  
> 2ca8fcce17d0ca5dc6c260c34b14b969fbc20c4a4520e19aed0a0be23a199243  
> 7b3a33baf89095f9b7d2be8dfa184c274e7f27a05a7e57faf8b32882a60bfe5c  
> 3a2112ed78bbec16929d9f39aca09efe2eb44abb80bbfa765e451a87aef84a99  
> 85019644110b9473b93e3757ed9b324666ac515a1b91afdfbc3b17241b2d9376  
> 873aa6d30e38c79b478eb04a83104bb31fd62989d3cca4b61164065038dadd29  
> 7413426f5afd78b7abc0ca0a3035c2f8578c41e18548ad530ead3ee93f638a3c  
> 86984171de311b006bc86780e5a415b3698edb864d42e72f851a7d64c2656748  
> 9d6808021c1336763e212c787a669eb0400b089e586457b88373dd87dfcf41c9  
> ea6690f028157aec343e21484eab136379e35c6296b3e8eab4a7ba7bdfe13e5d  
> 8709e8dfe6bf8b8fdc91c342fc2da948d5b77b05e7a6dba79866f42dfe8ca04b  
> 1389ec4bde4a8970e95d8a48438395578ae81e0649f33c5ca0febe062e56712c  
> fad36c037c93c48ef5cdf31b8ed31e452a100ad14b75dce88597ef1eea115e9e  
> 23.82.140.133  
> 23.254.217.20  
> 23.254.227.144  
> 37.120.198.248  
> 49.12.241.35  
> 51.68.144.94  
> 51.68.146.200  
> 51.68.147.233  
> 51.75.62.99  
> 51.83.251.245  
> 51.83.253.244  
> 51.83.254.164  
> 54.37.130.166  
> 54.37.131.107  
> 54.38.136.187  
> 54.38.137.18  
> 54.38.138.141  
> 54.38.139.20  
> 64.44.101.250  
> 64.44.102.6  
> 64.44.102.150  
> 64.44.135.230  
> 64.44.135.250  
> 70.34.216.103  
> 104.168.156.224  
> 145.239.29.119  
> 145.239.30.26  
> 146.70.95.244  
> 146.70.106.47  
> 167.235.245.35  
> 176.107.177.124  
> 192.236.161.191  
> 192.236.162.127  
> 192.236.194.136  
> 193.29.104.147  
> 193.233.203.156  
> 194.37.97.135  
> 209.141.52.25

## Yara

> rule loader_win_bumblebee {  
> meta:  
> version = "1.0"  
> malware = "BumbleBee"  
> reference = "<https://blog.sekoia.io/bumblebee-a-new-trendy-loader-for-> initial-access-brokers/>"  
> source = "SEKOIA.IO"  
> classification = "TLP:WHITE"
>
> strings:
>
> $str0 = { 5a 00 3a 00 5c 00 68 00 6f 00 6f 00 6b 00 65 00 72 00 32 00 5c 00
> 43 00 6f 00 6d 00 6d 00 6f 00 6e 00 5c 00 6d 00 64 00 35 00 2e 00 63 00 70
> 00 70 00 } // Z:\hooker2\Common\md5.cpp  
> str1 = "/gates" ascii  
> $str2 = "3C29FEA2-6FE8-4BF9-B98A-0E3442115F67" wide
>
> condition:  
> uint16be(0) == 0x4d5a and all of them  
> }

## 参考来源

> [Sekoia](https://blog.sekoia.io/bumblebee-a-new-trendy-loader-for-initial-> access-brokers/)

