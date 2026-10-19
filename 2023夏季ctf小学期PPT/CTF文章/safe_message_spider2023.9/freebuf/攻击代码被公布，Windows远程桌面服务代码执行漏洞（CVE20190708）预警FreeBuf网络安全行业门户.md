**2019年9月7日凌晨，深信服安全团队监测到关于CVE-2019-0708相关情报，该情报披露CVE-2019-0708漏洞利用代码，该EXP可以通过RDP协议进行远程代码执行攻击。官方描述此漏洞相关危害可参考2017年WannaCry事件，深信服强烈建议用户及时安装补丁以避免受到损失。**

![](https://image.3001.net/images/20190907/1567861101_5d73a96d28d8a.png!small)

> 漏洞名称：Remote Desktop Protocol漏洞
>
> 威胁等级：严重
>
> 影响范围：Windows XP;Windows 7 ;Windows Server 2003;Windows Server 2008;Windows
> Server 2008 R2
>
> 漏洞类型：任意代码执行漏洞
>
> 利用难度：容易

## 漏洞概述

CVE-2019-0708，属于任意代码远程执行漏洞，当未经身份验证的攻击者使用RDP连接到目标系统并发送特制请求时，即可以触发该漏洞。此漏洞属于预身份验证，无需用户交互，成功利用此漏洞的攻击者可以安装应用程序，查看、更改或删除数据或创建具有完全用户权限的新账户。

由于该漏洞可能导致的后果较为严重，今年5月份，深信服安全团队在追踪到该漏洞情报时已经第一时间向广大用户推送预警，并提供相应的防范措施：漏洞预警 |
Remote Desktop Protocol任意代码执行漏洞(CVE-2019-0708)

目前，由于EXP的公开发布，恶意攻击者还很有可能利用该漏洞编写定制的恶意软件，
利用此漏洞的恶意软件传播影响引发类似2017年WannaCry恶意软件遍布全球的事件，广大用户需要更加警惕利用该漏洞的恶意软件的出现，提前做好预防措施。

## 漏洞分析

成功利用漏洞的前提是将名称为“MS_T120”的静态信道成功绑定到正常信道以外。由于微软官方在内部会使用一个名为MS_T120的信道，因此此信道理论上不应该接收任意消息。

RDP的内部组件有很多，包括svchost.exe中的几个用户模式的dll，以及几个内核模式的驱动程序。漏洞触发的原因是攻击者在MS_T120信道上发送消息，这将导致termdd.sys驱动程序中触发一个双重释放漏洞(free-after-free)。

在完成RDP协议的握手过程后，将开始向已经绑定的各个信道中发送消息。MS_T120信道的消息是由用户模式组件——rdpwsx.dll进行管理，该dll创建一个线程，该线程将在函数rdpwsx!IoThreadFunc中进行循环，通过I/O端口读取消息。

![](https://image.3001.net/images/20190907/1567861129_5d73a98957ef7.png!small)

数据通过I/O数据包传入后，将进入rdpwsx!MCSPortData 函数进行处理：

![](https://image.3001.net/images/20190907/1567861155_5d73a9a3297f4.png!small)

从函数中可以看到，在rdpwsx!MCSPortData
函数中，有两个opcode：0x0和0x2。如果opcode为0x2，则调用rdpwsx！HandleDisconnectProviderIndication函数执行清理动作，然后使用rdpwsx！MCSChannelClose关闭通道。

![](https://image.3001.net/images/20190907/1567861175_5d73a9b77e0b1.png!small)

从理论上来说，发送的数据包大小都在合法范围的MS_T120消息，将会正常关闭MS_T120信道，并断开连接程序（此时opcode为0x2），并且进行清理操作，此时将不会产生远程代码执行和蓝屏崩溃的风险。如果发送的数据包大小无效，就会导致远程代码执行和拒绝服务。

## 漏洞复现

根据该EXP的发布者称，该EXP针对Windows 7和Windows Server 2008 R2
x64。深信服千里目第一时间进行了复现，证实该EXP确实可导致任意代码执行。

该EXP被发布者在Metasploit的官方Github的Pull Request中，但尚未加载进Metasploit的官方框架中。

![](https://image.3001.net/images/20190907/1567861253_5d73aa058a4be.png!small)

如上图中所示，按照Metaploit的正常使用流程即可加载该EXP。RHOSTS参数指定目标主机，target参数指定目标主机的系统版本，目前只有Windows
7 和 Windows Server 2008 R2两个版本。加载EXP后，执行，即可获取目标主机的权限。

## 影响范围

目前受影响的Windows版本：

> Microsoft Windows XP
>
> Microsoft Windows Server 2008 R2 for x64-based Systems SP1
>
> Microsoft Windows Server 2008 R2 for Itanium-based Systems SP1
>
> Microsoft Windows Server 2008 for x64-based Systems SP2
>
> Microsoft Windows Server 2008 for Itanium-based Systems SP2
>
> Microsoft Windows Server 2008 for 32-bit Systems SP2
>
> Microsoft Windows Server 2003
>
> Microsoft Windows 7 for x64-based Systems SP1
>
> Microsoft Windows 7 for 32-bit Systems SP1

## 解决方案

### 1、及时安装微软发布的安全更新补丁：

Microsoft官方已经在
2019年5月14日修复了该漏洞，用户可以通过安装微软的安全更新来给系统打上安全补丁，下载地址为：<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0708>

同时针对已不受微软更新支持的系统Windows Server 2003和Windows XP提供的安全更新，下载地址:

<https://support.microsoft.com/zh-cn/help/4500705/customer-guidance-for-cve-2019-0708>

### 2、缓解措施（在无法及时安装微软安全更新的情况下作为临时性解决方案）：

> （1）若用户不需要用到远程桌面服务，建议禁用该服务。
>
> （2）开启网络级别身份验证（NLA），此方案适用于Windows 7, Windows Server 2008, Windows Server 2008
> R2。

以上缓解措施只能暂时性针对该漏洞对系统进行部分缓解，强烈建议在条件允许的情况下及时安装微软安全更新。

## 漏洞追踪时间轴

> ### 2019/5/14
>
> Microsoft发布安全更新公告并披露漏洞
>
> ### 2019/5/15
>
> 深信服千里目安全实验室发布漏洞预警
>
> ### 2019/5/22
>
> 深信服千里目实验室根据漏洞跟踪分析结果发布二次漏洞预警
>
> ### 2019/5/30
>
> 深信服千里目实验室发布CVE-2019-0708攻击趋势分析
>
> ### 2019/6/29
>
> 深信服安全研究团队针对某特定版本构造出EXP，证实该漏洞影响巨大，再次发布预警
>
> ### 2019/9/7
>
> 深信服安全研究团队监测到EXP披露情报，对EXP复现验证，证实该EXP可导致服务器远程代码执行，特再次发布预警，提供解决方案给广大企业用户

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

