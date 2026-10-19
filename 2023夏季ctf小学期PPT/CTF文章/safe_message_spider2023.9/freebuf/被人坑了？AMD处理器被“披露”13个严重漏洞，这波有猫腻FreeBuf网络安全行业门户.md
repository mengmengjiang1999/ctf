***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **名不见经传的以色列安全公司CTS-Labs突然向媒体公开了一份白皮书，披露了 AMD 处理器中存在的 13 个安全漏洞，却仅给 AMD 24
小时的响应时间，消息一出，引发安全行业的轩然大波……**  

 **目前 AMD正在针对以色列安全公司发布的一份漏洞报告进行紧急调查，该公司的这份报告披露了影响 AMD Ryzen 和 EPYC
处理器的13个安全漏洞。而这13个漏洞分布在四个名为 RyzenFall，MasterKey，Fallout和 Chimera 的漏洞类别之中。**

发现这些漏洞的是来自以色列的安全实验室 CTS Labs
，他们在报告中描述了漏洞的细节信息，并直接发布了白皮书。AMD方面回应称，对这种传播方式他们表示担忧。AMD发言人表示，

>
> “我们正在积极调查和分析白皮书中指出的芯片漏洞问题。由于这家安全公司过去并没有与AMD的合作经历，我们认为它们处理这件事情的方式并不恰当————他们没有给
> AMD **合理的时间** 去调查研究漏洞，就 **向媒体公布** 了它们发现的漏洞。”

 **攻击者如果成功利用这些漏洞，可以完全控制系统，也可以从CPU区域提取出数据，和此前臭名昭注、让人紧张的 Meltdown 和 Specter
漏洞有相似之处。**

 **
**![5a97b31a46a78.jpg](https://image.3001.net/images/20180314/15209972692504.jpg!small)**  
**

## **事出紧急，AMD 也仅在昨天得到通知**

由于AMD正在对披露的漏洞进行调查，目前还没有可用的修复补丁。据报道，CTS 实验室是在昨天向 AMD 通报了漏洞信息，目前具体的影响结果还没有得到 AMD
方面的完全证实。  

CTS 实验室表示，一些漏洞的波及范围会比所列出的更大，因为他们并未尝试为所有AMD CPU系列创建PoC。

 **下图详细介绍了这些漏洞内容以及它们所能影响的 AMD 处理器。 [ **白皮书见文末]****

![AMD-flaws-stations.png](https://image.3001.net/images/20180314/15209958364956.png!small)  

##  **CTS实验室面临舆论批评和质疑**

信息安全社区则对CTS实验室公司仅给 AMD 只有一天的时间紧急响应来处理问题之事提出不少批评！

此外，另有专家还指出：白皮书中没有提供技术实现的细节，且由于漏洞利用的苛刻条件（需要 **管理员级别的权限**
），该公司提出的这些漏洞可能造成的实际危害不大。

Linux之父 Linus Torvalds 也公开评价道，他认为这次突如其来的“安全白皮书”更像是在博取关注或扰乱股价。

> 我觉得信息安全行业已经堕落了，但现在正在变得越来越荒谬。

![DYMWKt-W0AAZSeW.jpg-large.jpeg](https://image.3001.net/images/20180314/15210154979365.jpeg!small)

## 具体是哪些漏洞?

 **以下是CTS实验室研究员公开的漏洞描述，但截至目前尚未完全得到AMD方面的确认。**

### MasterKey 1, 2, 3

可在AMD安全处理器内运行的持久化恶意软件

> \- 它可以绕过固件的安全功能，如安全加密虚拟化SEV，和固件可信平台模块fTPM
>
> \- 进行网络凭证窃取，绕过微软的 VBS、Windows Credential Guard
>
> \- 对硬件造成物理伤害
>
> \- 影响型号： EPYC, Ryzen, Ryzen Pro, Ryzen Mobile。目前已经在EPYC和RYZen上进行了成功测试。

### RyzenFall 1 & Fallout 1

> \- 在受保护内存区域写入数据，如WIndows隔离模式和DRAM（仅在Ryzen主板上）
>
> \- 网络凭证盗用，绕过VBS
>
> \- 支持VTL1 恶意软件在内存的存留
>
> \- 影响型号：EPYC，Ryzen，Ryzen Pro，Ryzen Mobile。已成功测试EPYC，Ryzen，Ryzen Pro和Ryzen
> Mobile。

### RyzenFall 2 & Fallout 2

> \- 禁用安全管理RAM的读写保护功能
>
> \- 抵御绝大多数的端点安全解决方案，支持SMM类恶意软件
>
> \- 影响型号：EPYC，Ryzen，Ryzen Pro。已成功测试EPYC，Ryzen，Ryzen Pro。

### RyzenFall 3 and Fallout 3

> \- 读取受保护的内存区域，包括VTL1、安全管理RAM以及DRAM。
>
> \- 盗用网络凭证。绕过 Windows Credential Guard。
>
> \- 影响型号：EPYC, Ryzen, Ryzen Pro. 已经成功利用EPYC, Ryzen, Ryzen Pro.

### RyzenFall 4

> \- 在AMD安全处理器上进行任意代码执行
>
> \- 绕过基于固件的安全功能，如固件可信平台模块fTPM
>
> \- 盗用网络凭证。 绕过基于VBS、Windows Credential Guard
>
> \- 进行hardware硬件的物理损坏
>
> \- 影响型号：Ryzen，Ryzen Pro。

### Chimera (Firmware, Hardware versions)

> \- 两套后门: 固件／硬件ASIC
>
> \- 帮助恶意软件注入到芯片组的内部8051架构中
>
> \- 将CPU连接到USB，SATA和PCI-E设备。
>
> \- 芯片组内运行的恶意软件可以利用芯片组作为硬件外设中间人
>
> \- 影响类型：Ryzen，Ryzen Pro。已经 成功利用Ryzen和Ryzen Pro。

**更详细的信息可以参考CTS发布的白皮书报告和视频介绍【[白皮书](https://safefirmware.com/amdflaws_whitepaper.pdf)】【[视频](https://amdflaws.com)】**

***参考来源：[bleepingcomputer](https://www.bleepingcomputer.com/news/security/amd-investigating-ryzenfall-masterkey-fallout-and-chimera-cpu-vulnerabilities/)／[donews](http://www.donews.com/news/detail?type=4&id=2989898)
，编译整理kylin1415，转载请注明FreeBuf.COM**

