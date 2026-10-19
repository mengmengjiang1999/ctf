2023年3月，Money
Message勒索团伙针对微星(MSI)公司的网络攻击成功后，泄露了MSI的一些内部资料，其中包括BootGuard私钥等敏感数据。BootGuard安全机制是Intel硬件信任体系中重要的组成部分，而其私钥被泄露，预示着对于某些型号的设备，BootGuard这一主要的安全机制将被绕过。同时，泄露资料中还包括UEFI固件镜像签名密钥。

主板UEFI固件是计算机体系中的底层关键软件，而BootGuard是Intel安全体系中基于硬件信任根的重要完整性保护机制，它和CPU
microcode、CSME组成了Intel体系中最核心的安全保障机制。如果BootGuard被成功攻击，或攻击者取得OEM/ODM厂商的BootGuard私钥，则攻击者可以利用UEFI的实现缺陷、底层配置错误等方式并结合其他漏洞，可以完全绕过或对抗几乎所有已知安全机制，突破系统重重防御措施，如：SMM_BWP、BWE/BLE、PRx硬件安全机制，以及SecureBoot，HCVI、PatchGuard、kASLR、KDEP、SMEP、SMAP等内核安全防护技术；以及各类主流杀毒软件和EDR/XDR系统，获得对设备的持久性控制。

HardcoreMatrix团队经过深入研究，并重写了部分缺失的厂商内部工具，针对MSI Modern 15 B12M(Intel 12代CPU
i5-1235U)成功实现了BootGuard私钥重签名、胶囊更新重签名，以及SMM
Rootkit等完整攻击链，以此展示此类供应链威胁的严重性。事实证明，MSI资料泄露所带来的供应链威胁是真实的，严重的，可操作的。

![](https://image.3001.net/images/20230906/1693975147_64f8026bdf9b6be7fcc0d.jpg!small)

![1693975349_64f803353af739bb4e005.jpg!small](https://image.3001.net/images/20230906/1693975349_64f803353af739bb4e005.jpg!small)

团队认为，本次MSI资料泄露是严重的攻击事件。由于BootGuard私钥的特殊性（公钥hash固化在FPFs中），其属于最基本的信任根之一，暂时无法修补，这将造成众多型号的设备面临长期的安全威胁。

