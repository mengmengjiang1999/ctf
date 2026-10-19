![](https://image.3001.net/images/20210720/1626749752_60f63b38ca60a4d4f0b95.jpg!small)

对CDProjekt Red大肆宣传的攻击背后的勒索软件团伙使用Linux变体，该变体以VMware的ESXi虚拟机平台为目标，实施最大限度地破坏。

随着企业越来越多地转向虚拟机，以实现更轻松的备份和资源管理，勒索软件团伙正在演变他们的策略，以创建针对这些服务器的Linux加密器。

VMware ESXi 是最受欢迎的企业虚拟机平台之一，在过去的一年中，越来越多的勒索软件团伙发布了针对该平台的Linux加密器。

虽然ESXi并非严格意义上的Linux，因为它使用自己的客户内核，但它们确实具有许多相似的特性，包括运行ELF64 Linux可执行文件的能力。

## HelloKitty迁移到ESXi

上周，安全研究员发现了许多Linux ELF64版本的Hello Kitty勒索软件，其目标是ESXi服务器和在其上运行的虚拟机。

众所周知，Hello Kitty使用Linux加密器，但这是研究人员公开发现的第一个样本。

网络安全研究人员共享了勒索软件的样本，可以清楚地看到引用ESXi的字符串以及勒索软件试图关闭正在运行的虚拟机。

> First try kill VM:%ld ID:%d %s
>
> esxcli vm process kill -t=soft -w=%d
>
> Check kill VM:%ld ID:%d
>
> esxcli vm process kill -t=hard -w=%d
>
> Unable to find
>
> Killed VM:%ld ID:%d
>
> still running VM:%ld ID:%d try force
>
> esxcli vm process kill -t=force -w=%d
>
> Check VM:%ld ID: %d manual !!!
>
> .README_TO_RESTORE
>
> Find ESXi:%s
>
> esxcli vm process list
>
> World ID:
>
> Process ID:
>
> Running VM:%ld ID:%d %s
>
> Total VM run on host: %ld

从调试信息中，我们可以看到勒索软件利用ESXi的esxcli命令行管理工具列出服务器上正在运行的虚拟机，然后将其关闭。

针对ESXi服务器的勒索软件团伙将在加密文件之前关闭虚拟机，以防止文件被锁定并避免数据损坏。

一些Darkside附属公司倾向于在开始加密之前忘记停止所有ESXi守护进程。结果是有时加密的数据可能与未加密的数据交错，或者包含文件密钥的页脚被部分覆盖。

关闭虚拟机时，勒索软件将首先使用“soft”命令尝试正常关闭：

> esxcli vm process kill -t=soft -w=%d

如果仍有虚拟机在运行，它将尝试使用“hard”命令立即关闭虚拟机：

> esxcli vm process kill -t=hard -w=%d

最后，如果虚拟机仍在运行，恶意软件将使用“force”命令强制关闭任何正在运行的虚拟机。

> esxcli vm process kill -t=force -w=%d

虚拟机关闭后，勒索软件将开始加密.vmdk(虚拟硬盘)、.vmsd(元数据和快照信息)和 .vmsn(包含VM的活动状态)文件。

这种方法非常有效，因为它允许勒索软件团伙使用单个命令加密许多虚拟机。

上个月，网络安全研究人员还发现了一个Linux版本的REvil勒索软件，它针ESXi服务器并使用esxcli命令作为加密过程的一部分。

Emsisoft首席技术官当时告诉记者，其他勒索软件操作，如 Babuk、RansomExx/Defray、Mespinoza、Go
Google和现已解散的DarkSide，也创建了Linux加密器来针对ESXi虚拟机。

大多数勒索软件组织实施基于Linux版本的勒索软件的原因是专门针对ESXi。

## 关于HelloKitty的一些信息

HelloKity自2020年11月开始运营，当时受害者首次在论坛上发布了有关勒索软件的信息。从那时起，与其他人为操作的勒索软件操作相比，HelloKity并没有特别积极。

他们最著名的攻击是针对CD Projekt Red，攻击者加密设备并声称窃取Cyberpunk 2077、Witcher 3、Gwent等的源代码。

攻击者后来声称有人购买了从CD Projekt Red窃取的文件。该勒索软件或其变体曾以不同的名称使用，例如DeathRansom和Fivehands。

随着勒索软件横行，网络安全问题已广受重视。包括中国在内，美国、俄罗斯及德国等国家均已纷纷出台相关政策及法规。不难发现，确保网络安全和数据安全已经成为国际上的重点工作。

伴随恶意软件的升级，犯罪团伙通过窃取数据或加密等方式不断打击国家关键基础设施，从而造成除经济之外的重大影响，严重影响社会生活运转。而作为网络最基础的部分之一——软件安全，在确保网络安全上起到重要作用。不难发现，恶意软件大多数通过软件系统的安全漏洞实施入侵，从而进行横向移动或发生软件供应链攻击，因此确保
**[软件安全](https://www.woocoom.com/b031.html)** 在一定程度上可以阻止大部分犯罪分子的攻击，为网络安全增加保障。

> 参读链接：
>
> <https://www.bleepingcomputer.com/news/security/linux-version-of-hellokitty-> ransomware-targets-vmware-esxi-servers/>

