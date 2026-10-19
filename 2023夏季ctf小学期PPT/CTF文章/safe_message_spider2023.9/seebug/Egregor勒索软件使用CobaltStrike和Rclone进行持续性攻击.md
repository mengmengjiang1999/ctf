**译者：知道创宇404实验室翻译组**  
**原文链接：<https://labs.sentinelone.com/egregor-raas-continues-the-chaos-with-cobalt-strike-and-rclone/>**

### 概述

Egregor勒索软件是Sekhmet恶意软件家族的一个分支，该家族自2020年9月中旬以来一直处于活跃状态。勒索软件以危害组织，窃取敏感用户数据，加密数据，并要求勒索交换加密文件的方式运作。Egregor是一种勒索软件，它与针对GEFCO、Barnes&Noble、Ubisoft和其他许多公司的网络攻击有关。

![](https://images.seebug.org/content/images/2020/11/9225f22b-cd2c-479a-b34c-166d34fc89ee.jpg-w331s)

多家情报安全公司认为，过去（现已倒闭）的[Maze分支机构](https://labs.sentinelone.com/enter-the-maze-demystifying-an-affiliate-involved-in-maze-snow/
"Maze分支机构")和Egregor之间存在联系。有报道称[Egregor](https://securityboulevard.com/2020/10/egregor-sekhmets-cousin/
"Egregor")与[Sekhmet](https://securityboulevard.com/2020/10/egregor-sekhmets-cousin/
"Sekhmet")、[ProLock](https://www.helpnetsecurity.com/2020/11/23/egregor-ransomware/ "ProLock")和[LockBit](https://www.recordedfuture.com/
"LockBit")也有关联。而ProLock和LockBit都与Maze有关系。对于Sekhmet，我们可以在其配置格式和模糊处理风格上看到很多[相似之处](https://twitter.com/VK_Intel/status/1323534149081272320
"相似之处")。

![](https://images.seebug.org/content/images/2020/11/3b9b0c3a-e0d1-49a2-bae3-8d0713aaabd1.jpg-w331s)

与其他的勒索软件组织一样，Egregor背后的攻击者会过滤受害者的数据，并在受害者不遵守赎金要求时将其公开曝光。

### Egregor分发方法

Egregor的主要分发方式是Cobalt
Strike。攻击者通过各种手段（[RDP攻击](https://labs.sentinelone.com/case-study-catching-a-human-operated-maze-ransomware-attack-in-action/
"RDP攻击")、[网络钓鱼](https://www.sentinelone.com/blog/technical-analysis-paypal-phishing-scam/ "网络钓鱼")）破坏目标环境，一旦Cobalt
Strike信标有效负载建立并持续存在，就可以利用它来交付和启动Egregor有效负载。

由于Egregor是一个拥有多个分支机构的RaaS，因此交付和武器化策略可能会有所不同。关于Egregor利用[CVE-2020-0688](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-0688 "CVE-2020-0688")（Microsoft
Exchange中的一个远程代码执行漏洞）的报告很少，且未经证实。有[消息](https://www.recordedfuture.com/
"消息")称Egregor可能利用了[CVE-2018-8174](https://nvd.nist.gov/vuln/detail/CVE-2018-8174
"CVE-2018-8174")（VBScript引擎）、[CVE-2018-4878](https://nvd.nist.gov/vuln/detail/CVE-2018-4878
"CVE-2018-4878")（Adobe Flash
Player）和[CVE-2018-15982](https://nvd.nist.gov/vuln/detail/CVE-2018-15982
"CVE-2018-15982")（Adobe Flash
Player）这些漏洞。Egregor被证明使用了[LOTL](https://www.sentinelone.com/blog/how-do-attackers-use-lolbins-in-fileless-attacks/
"LOTL")工具（如bitsadmin）来下载或更新DLL组件。此外，在[最近的活动](https://www.bleepingcomputer.com/news/security/qbot-partners-with-egregor-ransomware-in-bot-fueled-attacks/
"最近的活动")中，我们观察到一些较大的恶意软件家族和框架（如QBot）在使用Egregor。

### Egregor有效负载分析

Egregor有效负载（DLL）是高度模糊的，包括Salsa20加密的配置数据。文件加密是通过ChaCha流密码和RSA的组合实现的。每个有效负载包含一个RSA-2048公钥。

基于DLL的有效负载在启动时需要一个密钥/密码，该密钥特定于每个样本。`-p`参数被传递给与所述密钥连接的有效负载。例如，如果密钥是`123EVILBADGUYS`，则需要参数`-p123EVILBADGUYS`才能成功启动负载。

这种方法还增加了恶意软件逃避检测分析的能力。如果没有传递有效密钥，有效负载将无法解密，并且无法启动或终止。这是在对Egregor有效载荷进行静态和动态分析时需要考虑的一个关键点。

启动有效载荷时，内存中似乎存在其他参数。其中一些是不言自明的，而另一些仍在进行分析。我们在下面总结了参数的用法。

    
    
    --nomimikatz
    --fast
    --full ; encryption of entire system (local & network-accessible), no exclusions
    --multiproc
    --killrdp
    --nonet ; exclude encryption of network drives
    --path ; encrypt only specific path in this parameter
    --target
    --append ; customize the file extension to be used for encrypted files
    --norename ; skip the process of renaming encrypted files
    --greetings ; directly address target (by victim company name, typically)
    --samba

对Egregor有效负载的初步分析表明，勒索软件将避免加密系统，那些系统的主要设备语言是以下之一：

  * Armenian
  * Azerbaijani
  * Belarusian
  * Georgian
  * Kazakh
  * Kyrgyz
  * Romanian
  * Russian
  * Tajik
  * Tatar
  * Turkmen
  * Ukrainian
  * Uzbek

数据溢出的主要方法似乎是Rclone，它是一个可用于管理远程存储的开源实用程序。Egregor有效负载会将自己的Rclone副本与特殊的配置数据一起发布，从而控制渗透过程。

![](https://images.seebug.org/content/images/2020/11/bc7854ad-c7bd-4639-9fd1-7b6e1aafb066.jpg-w331s)

### Post-Compromise行为

Egregor有一个受害者博客，他们利用这个博客来威胁受害者，并在受害者不遵守赎金要求的情况下发布泄露的数据。截至2020年11月24日，Egregor博客上共有152家公司上榜，涵盖全球多个行业。最常见的行业有:

  * 信息技术与服务
  * 建设
  * 零售
  * 消费品
  * 汽车

![](https://images.seebug.org/content/images/2020/11/bb2a1fb9-a88e-4995-a663-a36b6665b232.jpg-w331s)

![](https://images.seebug.org/content/images/2020/11/d0019f5c-f406-451f-b9f9-d2d95fbe2bc1.jpg-w331s)

![](https://images.seebug.org/content/images/2020/11/32c2075c-cae9-4945-8a15-864c13d4f9e4.jpg-w331s)

与其他勒索软件一样，Egregor赎金记录遵循一个熟悉的模板。指示受害者访问其基于TOR的支付门户以获取进一步的指示。每个赎金票据的底部还有一个加密的blob，其中包含受害者特定的系统数据以及已编码的RSA公钥。

示例：

    
    
    ---EGREGOR---    
    pWEzuKkw9nY82VRKYfrw4f4wvrnfnKEApQ5JTkf/YQPzxJtJmwKUjXV759aYQnPIZdGN1RUckdpMZWiYGmsWFYzkNJZpsPihvk9c14zLJDJdmpitYvoy22JFox9iBHqhFAjDC37kzpVH6bafVABdUgUdr0r2EzK+ysJBiR0Ge28ToH94wJTXwBC7hi3G42vk4KmLncPm55NUuz9ZzQ+xqovtN/RyDNL8MDbW4lHWe9Lmi5qlNN/ckIgwDh+sI1rO/T+DmS1Uoo62QWeYTgmlRaCp91AfeC7mNFkXvXUVMs3GlqpIrgbMLPBbBi04sra/pmXp9oteZK4b1fAWKgDZ2B0f11AiX9SFIpJn8odT+Z0tVL2H8IKvANB1507SGq3S2JR3a6SLGODy3yjm3vwfnyaVqL1gNNudkDc5dLVx0tavBj2h5v1PMDCFYpuSZ56qYY1VeQfA56bsPKI2J102ztOktaFmU9jI3G3oxBCV9j1JKOJhltPRjyXAmg9o3sqB5VCxPzmMIL+bxJnEelHdBzVdRpY4pPyEPmdrn2mQ5sXwIA1RfdvF9JruxQF/0yl2WKqK0CE4pKazQWdrYdQaLTPCdMxZv7JKO8Dy5vyHBW08+UTJEuEiQa6Q/1qVkGipUPgK4Wpg3iP6xas9SaV1ovy1o2yC0beVhD+Ean6/5/lfIiG1w/ouzyq0Vprhfmr59ftnduimCDgAPi9mv2Fzg1BcGYt5P0qE7Ya0ycGFyvNvS2eoiA5mjvN67R6jeJ8JF0fPnz7O2QMldjZj0uVfAoMHlgaRP74vOKfOzFHCiPhyXwe8V9Wd3xjctlG4PCVMuUvYn7BFSW82AMefXIWTeIhHD4UdoAuZ3sHsgsFyyaTdVo1WCEWJtMMN0FOyhF0m1R5ozQPJSyuaOUzrDU1fKD57v3Cf5T860kath1w+CQAeWXdbXSR0mvN45rPgYN24qVvvB6kle5Vr20x0EZJ4viCERcreKcJqOV/0GwZU4BR8jUGQkokgD3UvJQf0Vu4mIv6vLZUtvRvEl3URsZNWh7nnKR5jjq3Tx911IH+UQznFncGD402REUpyADZpv0aRfyMZzZFecaxlo/EMS8lhkeukkZQJiwXJH2SV77olADcOfnaOQEq+YU23kRJf+YOdKW3E9NsqF1MKLTdn5+31ka4OyN7wed9HVyJj+clXkNT/YJkS/E869Hm1MPBQv+25451tiXgGcKo/9L5BFmmy77TxYuZMjuRVIanXWwK8tQ+kz0gEj1BG4I477yrhqN2yaQQ2cZ7QhpNPFlnsereCoI8rNBRBp/VgxKS+AKqkKj9UyghlABrYlRypEsM7FDC44tvDJILfb+9IL70qEe+BdPmIIv4/HWHJSEI7K9MWLah7cX4OGLG2eqT9pSkLISFvyEM+9ylo3WYWx2G0m5s0r7O+jRAOdZ1Joy5eGx7PPRCnVcEv0IyhNnFpz4HsNibUAR664rZ+Os05SDNitn3t8RgtAcvTdNHAbtNGLZZj/7KFIyGb1f37teR9/oty8BFsaHhRNVHx22+u+AFR/HbucnbY+prvzAWY3dpjQIO2O+3HoCuz2MXx5gFIfJ0pIA6V9px/j4LOPGPfN159CRItKeOy3ZLtKByaD+FwHBzYHpIWgCvL2vWo+eRWF66oYNvDhB5yVtDgXx0LU789ypKu/vjuvo7obGEoF3NoxJhmNS4DfVMzsy4YdBRhHrBfF36a8ahFSBApu9cd0RmuT09hKmV7m+EGGCXr+MNvzlFQSMzt5Ce5Mj9w507PN/IDLQz8h6236WGZSH2iM2PGUq/UF1wADoHSjPXRcfPparHHHPTcZZkil4HMWP6Y+gDlN0BKKl9ntqyd8QiiqDqwcJIZZG4Jm6lRIhvpBZ14P+z83zePzjMNhVkNVnU4sfDRaemkxZFPF+hGM/PEvqFuEOsX4LfWxOpwLAf+OLLpe71+6QdKDAcwf6553t0TOPCqGr3B+flGGAhi0pqCeAsB0KzS28MakLBxJQPkR/E+F0tHmwBYCCl0haxZnBZ9rJVApq2rAAENA2gQLPaStc0DzrdkIRY6r789la7OzAUqvcTyX8fq/xfYJpz+zUt4PUcVWxoO1+1g9+BpCAlPgZEkIKSbqoSNtkeIMz65CthNiCsX817p8nqBb4BdpcuCihoL49fK6fn/WUnj3xaTiQuNDnvcW9NARgIzqu2lvsZa+qvDBW99gsaeLb4feNlGqZUk98zht7GvywgFEAEYASCAAigAOg5QAEgAWABGAFMAMgAAAEIiQgAwADIARAAwAEYAMwAyAEEAMQBDADkAMgBFADAAOAAAAEqQAXwAQQA6AFIAXwAwAC8AMAB8AEMAOgBGAF8ANAA0ADMAMAA4AC8ANwA2ADQANAA3AHwARAA6AEMAXwAwAC8AMAB8AEUAOgBGAF8AMQA3ADEANgA0ADQALwAyADAAOQA3ADEANAA5AHwARgA6AEYAXwAyADkANAA5ADQANQAvADIAMAA0ADcAOAA2ADgAfAAAAFIQagBnAHIAYQBuAGoAYQAAAGgDckBXAGkAbgBkAG8AdwBzACAAUwBlAHIAdgBlAHIAIAAyADAAMQAyACAAUgAyACAAUwB0AGEAbgBkAGEAcgBkAAAAehJJAE0AUABSAEkATQBJAFMAAAA=
    
    ---EGREGOR---
这个“blob”包括与受害者可用的本地驱动器、驱动器的空间和总大小、主机名、发现的任何AV或安全产品的名称、以及用户/域上下文相关的数据。“blob”主要是用base64编码的。解码后，在明文的末尾可以看到相关数据。

![](https://images.seebug.org/content/images/2020/11/5c993bb7-3b72-4a08-9d17-225f06692eb8.jpg-w331s)

### 结论

Egregor是过去6到8个月里最激进、最复杂的勒索软件之一。它造成的损失不仅仅是赎金，还包括任何与数据泄露、公开发布私人数据、GDPR
/合规后果相关的[惩罚](https://www.sentinelone.com/blog/another-business-risk-from-ransomware-beware-ofac-sanctions-before-paying-the-cyber-criminals/ "惩罚")。

### IOC

#### SHA256 Hashes

8483aaf9e1fa5b46486c9f2a14c688c30d2006e88de65d0295a57892de0bf4c9  
3fd510a3b2e0b0802d57cd5b1cac1e61797d50a08b87d9b5243becd9e2f7073f  
2b3518937fd231560c7dc4f5af672a033b1c810d7f2f82c8151c025ce75775bf  
444a6897058fd4965770167b15a2ab13e6fd559a3e6f6cf5565d4d3282587459  
c3c50adcc0a5cd2b39677f17fb5f2efca52cc4e47ccd2cdbbf38815d426be9e1  
004a2dc3ec7b98fa7fe6ae9c23a8b051ec30bcfcd2bc387c440c07ff5180fe9a  
608b5bf065f25cd1c6ac145e3bcdf0b1b6dc742a08e59ec0ce136fe5142774e9  
3e5a6834cf6192a987ca9b0b4c8cb9202660e399ebe387af8c7407b12ae2da63  
4ea8b8c37cfb02ccdba95fe91c12fb68a2b7174fdcbee7ddaadded8ceb0fdf97  
9017c070ad6ac9ac52e361286b3ff24a315f721f488b53b7aaf6ac35de477f44  
ee06c557f1acd5c4948b1df0413e49f3885f8ac96185a9d986b91a1231444541  
765327e1dc0888c69c92203d90037c5154db9787f54d3fc8f1097830be8c76ab  
14e547bebaa738b8605ba4182c4379317d121e268f846c0ed3da171375e65fe4  
3fc382ae51ceca3ad6ef5880cdd2d89ef508f368911d3cd41c71a54453004c55  
f0adfd3f89c9268953f93bfdfefb84432532a1e30542fee7bddda14dcb69a76c  
a9d483c0f021b72a94324562068d8164f8cce0aa8f779faea304669390775436  
3aad14d200887119f316be71d71aec11735dd3698a4fcaa50902fce71bdccb07  
6ad7b3e0873c9ff122c32006fdc3675706a03c4778287085a020d839b74cd780  
932778732711cd18d5c4aabc507a65180bf1d4bd2b7d2d4e5506be4b8193596e

#### SHA1 Hashes

3c03a1c61932bec2b276600ea52bd2803285ec62  
f0215aac7be36a5fedeea51d34d8f8da2e98bf1b  
948ef8caef5c1254be551cab8a64c687ea0faf84  
50c3b800294f7ee4bde577d99f2118fc1c4ba3b9  
38c88de0ece0451b0665f3616c02c2bad77a92a2  
95aea6b24ed28c6ad13ec8d7a6f62652b039765e  
3cc616d959eb2fe59642102f0565c0e55ee67dbc  
5c99dc80ca69ce0f2d9b4f790ec1b57dba7153c9  
beb48c2a7ff957d467d9199c954b89f8411d3ca8  
03cdec4a0a63a016d0767650cdaf1d4d24669795  
c9da06e3dbf406aec50bc145cba1a50b26db853a  
ceca1a691c736632b3e98f2ed5b028d33c0f3c64  
f6ad7b0a1d93b7a70e286b87f423119daa4ea4df  
56eed20ea731d28d621723130518ac00bf50170d  
fa33fd577f5eb4813bc69dce891361871cda860c  
f7bf7cea89c6205d78fa42d735d81c1e5c183041  
f1603f1ddf52391b16ee9e73e68f5dd405ab06b0  
8768cf56e12a81d838e270dca9b82d30c35d026e  
ac6d919b313bbb18624d26745121fca3e4ae0fd3

#### IP Addresses

45[.]153.242.129（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=45.153.242.129
"ZoomEye搜索结果")）  
217[.]8.117.148（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=217.8.117.148
"ZoomEye搜索结果")）  
45[.]153.242.129（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=45.153.242.129
"ZoomEye搜索结果")）  
45[.]11.19.70（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=45.11.19.70
"ZoomEye搜索结果")）  
49[.]12.104.241:81（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=49.12.104.241
"ZoomEye搜索结果")）  
185[.]238.0.233（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=185.238.0.233
"ZoomEye搜索结果")）

#### Full URL Examples

http://185.238.0[.]233/p.dll  
http://185.238.0[.]233/b.dll  
http://185.238.0[.]233/sed.dll  
http://185.238.0[.]233/hnt.dll  
http://185.238.0[.]233/88/k057.exe  
http://185.238.0[.]233/newsvc.zip

#### Victim Blog / Archive

http://egregoranrmzapcv[.]onion  
https://egregornews[.]com/

#### Payment Portal

http://egregor4u5ipdzhv[.]onion/

#### MITRE ATT&CK

Indicator Removal on Host: File Deletion
[T1070.004](https://attack.mitre.org/techniques/T1070/004/ "T1070.004")  
Modify Registry [T1112](https://attack.mitre.org/techniques/T1112/ "T1112")  
Query Registry [T1012](https://attack.mitre.org/techniques/T1012/ "T1012")  
System Information Discovery
[T1082](https://attack.mitre.org/techniques/T1082/ "T1082")  
Native API [T1106](https://attack.mitre.org/techniques/T1106/ "T1106")  
Hijack Execution Flow: DLL Side-Loading
[T1574.002](https://attack.mitre.org/techniques/T1574/002/ "T1574.002")  
Process Injection [T1055](https://attack.mitre.org/techniques/T1055/ "T1055")  
Masquerading [T1036](https://attack.mitre.org/techniques/T1036/ "T1036")  
System Time Discovery [T1124](https://attack.mitre.org/techniques/T1124/
"T1124")  
Archive Collected Data [T1560](https://attack.mitre.org/techniques/T1560/
"T1560")  
Virtualization/Sandbox Evasion
[T1497](https://attack.mitre.org/techniques/T1497/ "T1497")  
Software Discovery: Security Software Discovery
[T1518.001](https://attack.mitre.org/techniques/T1518/001/ "T1518.001")  
Peripheral Device Discovery [T1120](https://attack.mitre.org/techniques/T1120/
"T1120")  
Inhibit System Recovery [T1490](https://attack.mitre.org/techniques/T1490/
"T1490")  
Create or Modify System Process: Windows Service
[T1031](https://attack.mitre.org/techniques/T1543/003/ "T1031")  
Exfiltration [TA0010](https://attack.mitre.org/tactics/TA0010/ "TA0010")

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1409/>

