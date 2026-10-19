![1.png](https://image.3001.net/images/20180820/1534707625_5b79c7a9a73f1.png!small)

**近期，卡巴斯基实验室的检测雷达发现了一款非常有意思的恶意挖矿软件，该恶意软件名叫PowerGhost，它在感染了目标主机之后不仅可以悄悄在后台挖矿，而且还能够感染企业大型网络内的其他主机，包括工作站和服务器等等。**

毫无疑问，对于攻击者来说，被感染的设备数量越多，驻留的时间越长，他们的利润也就越大。因此，我们经常会看到很多合法软件被挖矿软件感染，因为攻击者可以利用合法软件来传播自己的恶意软件。但需要注意的是，PowerGhost的开发者更有创新力，因为他们已经开始使用无文件技术来在目标系统中实现恶意挖矿软件感染了。由此看来，加密货币的流行以及价格的不断增长，已经开始让很多网络犯罪分子投身于恶意挖矿技术了。正如卡巴斯基实验室的调查数据一样，恶意挖矿软件正在逐步取代勒索软件的地位。

## 技术分析及传播途径

PowerGhost其实是一个经过了混淆处理的PowerShell脚本，其中包含的核心组件有：挖矿主程序、mimikatz、一个用于实现反射PE注入的模块、用于利用EternalBlue漏洞的ShellCode以及相关的依赖库（msvcp120.dll和msvcr120.dll）。下面给出的是部分代码片段：

![2.png](https://image.3001.net/images/20180820/1534707632_5b79c7b096735.png!small)

采用Base64编码的插件模块代码：

![3.png](https://image.3001.net/images/20180820/1534707637_5b79c7b577602.png!small)

这款恶意软件使用了各种无文件技术来隐藏自己的活动踪迹，并利用漏洞和远程管理工具（Windows管理工具）来远程感染目标设备。在实现感染的过程中，恶意软件会运行一个PowerShell脚本，下载了挖矿主程序之后，脚本会立即启动恶意软件，而不是直接将其存入主机的硬盘中。

### 恶意脚本的运行分为以下几个阶段：

 **自动更新：** PowerGhost会定期检查C&C服务器是否有新版本，有则自动下载并实现更新，而不会启动之前的版本。

![4.png](https://image.3001.net/images/20180820/1534707647_5b79c7bf27980.png!small)

 **传播：**
在mimikatz的帮助下，恶意软件会收集受感染系统的用户凭证，然后完成登录并通过WMI在本地网络中传播恶意软件副本。除此之外，PowerGhost还会利用臭名昭著的EternalBlue漏洞（MS17-010,
CVE-2017-0144）在本地网络中实现恶意软件传播。

 **提权：** 感染设备后，PowerGhost会利用漏洞MS16-032、MS15-051和CVE-2018-8120来在目标设备上实现提权。

 **持久化感染：** PowerGhost会将所有模块存储为WMI类，挖矿主体会以PowerShell脚本的形式存储，每90分钟激活一次。

![5.png](https://image.3001.net/images/20180820/1534707653_5b79c7c5bb5ee.png!small)

 **Payload：** 最后，该脚本会通过反射型PE注入来加载PE文件并启动挖矿程序。

在其中一个PowerGhost样本中，研究人员还发现了用于执行DDoS攻击的代码，显然PowerGhost的作者还想通过提供额外的DDoS攻击服务来赚取外快。

![6.png](https://image.3001.net/images/20180820/1534707660_5b79c7cc192bc.png!small)

### 统计与地理分布

PowerGhost的主要攻击目标是企业用户，因为根据它的特性，公司的本地局域网更适合传播。

![7.png](https://image.3001.net/images/20180820/1534707673_5b79c7d94fad9.png!small)

目前，感染了PowerGhost的用户主要分布在印度、巴西、哥伦比亚和土耳其等国家。

卡巴斯基实验室的产品的检测标识如下：

    
    
    DM:Trojan.Win32.Generic
    
    PDM:Exploit.Win32.Generic
    
    HEUR:Trojan.Win32.Generic
    
    not-a-virus:HEUR:RiskTool.Win32.BitMiner.gen

nanopool.org和minexmr.com的电子钱包地址：

    
    
    43QbHsAj4kHY5WdWr75qxXHarxTNQDk2ABoiXM6yFaVPW6TyUJehRoBVUfEhKPNP4n3JFu2H3PNU2Sg3ZMK85tPXMzTbHkb
    
    49kWWHdZd5NFHXveGPPAnX8irX7grcNLHN2anNKhBAinVFLd26n8gX2EisdakRV6h1HkXaa1YJ7iz3AHtJNK5MD93z6tV9H

## 入侵威胁指标

C&C主机名：

    
    
    update.7h4uk[.]com
    
    185.128.43.62
    
    info.7h4uk[.]com

MD5：

    
    
    AEEB46A88C9A37FA54CA2B64AE17F248
    
    4FE2DE6FBB278E56C23E90432F21F6C8
    
    71404815F6A0171A29DE46846E78A079
    
    81E214A4120A4017809F5E7713B7EAC8

 ***参考来源：[securelist](https://securelist.com/a-mining-multitool/86950/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

