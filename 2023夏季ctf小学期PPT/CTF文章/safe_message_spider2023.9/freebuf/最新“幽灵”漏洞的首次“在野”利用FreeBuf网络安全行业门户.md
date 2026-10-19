## ****一. 漏洞简介****

近日，国外安全研究人员Julien
Voisin发现有用户在VirusTotal平台上传了针对Linux和Windows系统的漏洞利用程序，程序基于CVE-2017-5753漏洞。该漏洞于2018年1月被Google
ProjectZero研究人员披露。通过利用Intel、AMD和ARM处理器体系结构中存在的硬件设计缺陷，攻击者可以在易受攻击的系统上窃取敏感数据（包括密码、文档以及内存中可用的任何其他数据）。

![1620890788_609cd4a4b3b4acc605bfa.png!small](https://image.3001.net/images/20210513/1620890788_609cd4a4b3b4acc605bfa.png!small)

  

![1620890797_609cd4adaf53ed7c0fdbb.png!small](https://image.3001.net/images/20210513/1620890797_609cd4adaf53ed7c0fdbb.png!small)

##  ** **二. 影响版本****

Ø Windows系统

Ø Linux系统（目前仅影响Fedora、ArchLinux和Ubuntu）

##  ** **三. 漏洞详情****

研究人员在VirusTotal平台上分析两个可正常运行的漏洞程序后发现：该漏洞允许非特权用户从目标设备的内核内存中转储Windows系统和Linux/etc/shadow文件上的LM/NT哈希，该漏洞还允许转储Kerberos票据，该票据可与PsExec一起用于Windows系统上的本地提权和横向移动。

同时研究人员也将漏洞利用分为四个阶段：

> 1.找到超级区块；
>
> 2.查找要转储文件的索引节点；
>
> 3.查找对应的页面地址；
>
> 4.对文件内容进行转储。

本次发现的“幽灵”漏洞利用程序经初步证实属于软件包的一部分，而该软件包是Immunity
Inc公司开发的渗透测试工具CANVAS针对Windows和Linux系统的安装程序，对应版本号为7.26。

![1620890821_609cd4c5bfb97b8d65ca5.png!small](https://image.3001.net/images/20210513/1620890821_609cd4c5bfb97b8d65ca5.png!small)

更有知情人士表示，Canvas 7.26的破解版本早在2020年10月就已在私人Telegram频道和地下黑客论坛中传播。

![1620890837_609cd4d57dcb81f68726a.png!small](https://image.3001.net/images/20210513/1620890837_609cd4d57dcb81f68726a.png!small)

![1620890849_609cd4e1986d25c7cb803.png!small](https://image.3001.net/images/20210513/1620890849_609cd4e1986d25c7cb803.png!small)

针对本次事件，该公司已经发布声明会在未来的几个月内为专业安全人员和渗透测试人员提供有效的漏洞程序。相信在不久后github也会对该漏洞利用程序进行开源披露，对此我们会继续跟进并发布更详细的研究内容。

##  ** **四. 防御建议****

目前OS和CPU供应商已经发布了针对受影响产品的软件和固件缓解措施，请及时关注厂商发布的更新信息并及时进行更新处理。

同时请保持警惕，不要轻易接收或运行来历不明的可疑软件或程序。

##  ** **五. 参考链接****

https://dustri.org/b/spectre-exploits-in-the-wild.html

https://therecord.media/first-fully-weaponized-spectre-exploit-discovered-online/

https://www.bleepingcomputer.com/news/security/working-windows-and-linux-spectre-exploits-found-on-virustotal/

