## 前言

 **如果要评选最近一年内国内信息安全圈最火的一个安全新名词，那一定是“MITRE ATT
&CK”了。这个词在其被引入国内的那一刻起，就似乎备受青睐，常见于各种文章、PPT、演讲之中，大有赶超前几年的安全热词“威胁情报”之势。一时间造成了一种如果在2019年没听说过“MITRE
ATT&CK”的安全从业人员不算是真正的业内人士的错觉。可是，物极必反，但凡被吹捧的越高往往跌的越惨，笔者私下里也在多个场合听到一些对“MITRE
ATT&CK”被过度吹捧的反感言论，其实看待任何新鲜的事物和概念都需要冷静分析、客观思考、取其精华、去其糟粕，最后为我所用才是正道。**

根据MITRE
ATT&CK的官方描述，我们可以知道其是一个梳理攻击者的入侵行为（包括战术和技术）的知识库，其目的在于帮助防守方全面地了解和分析攻击者的TTPs。对于乙方安全公司，可以利用ATT&CK来开发各种安全产品或服务的威胁检测方法提高入侵检测的覆盖面；而对于甲方企业，则可以利用ATT&CK来设计各种威胁模型来检测与之对应的攻击手法，提高整体的防御检测的能力。

本文将探讨如何利用ATT&CK站在攻击者视角来组织和实践Red
Teaming行动，更加有针对性的模拟真实世界的攻击者以达到“实战养兵”的目的。至于什么是Red
Teaming，本文将不再赘述，具体可参阅笔者之前的文章《Red Team从0到1的实践与思考》。

## 规划

有效的Red Teaming行动是离不开充分的事前准备和行动规划的。那么如何利用Red Teaming行动来模拟真实攻击者呢？目前比较流行的方法有以下几种：

模拟直接威胁者：根据特定的威胁情报来模拟攻击者，所谓“以情报驱动的Red Teaming行动”，目前深受国际主流互联网企业的Red
Team团队的青睐，例如针对某些特定行业或者国家的APT组织的TTPs的模拟；

模拟已知威胁者：根据已披露的APT组织的TTPs来模拟攻击者，例如利用MITRE ATT&CK来规划Red Teaming行动所需的TTPs；

模拟未知威胁者：根据真实入侵的各个阶段收集到的具体目标信息实时地规划攻击路径从而模拟攻击者。

这三种方法其实应该算是Red Teaming行动在企业处于不同的威胁阶段时应该采用的不同方法，个人以为前两种应该作为甲方企业自身Red
Team的主要工作方向，第三种可作为前两种的进阶补充或者乙方Red
Teaming服务的工作重心。具体而言，第一种方法主要是模拟直接威胁者，通过威胁情报提前发现直接威胁者的TTPs并加以模拟来检测防守团队应对直接威胁的防御能力，这是Red
Teaming行动的基本目标；第二种方法主要是模拟已知威胁者，通过模拟目前所有已知的攻击组织的TTPs来全面而系统地识别防守团队的防御弱点并帮助其提高检测所有已知威胁的覆盖率，这是Red
Teaming行动的主要目标；第三种方法主要是模拟未知威胁者，通过模拟真实黑客的潜在入侵行为来检测当前企业面对未知威胁的防御能力，这是Red
Teaming的进阶目标。

本文将重点介绍一下第二种方法即利用MITRE ATT&CK来规划Red
Teaming行动从而全面而系统地模拟已知威胁者，换句话说就是以ATT&CK里所列的TTPs以“连点成线”的方式来规划所有可行的攻击路径。

## 实践

我们都知道官方的ATT&CK框架只是笼统地归纳总结了所有目前已知的攻击者的Tactics（战术阶段）和每个Tactics对应的Techniques（技术点），但却并没有深入地介绍每个Technique的具体技术细节，这实际上就为Red
Teaming行动的模拟带来了很大的不便，也就意味着Red
Team自己需要分析和整理一个包含每个技术点详细介绍的ATT&CK框架，笔者根据自身的实践经验已经做了类似的落地工作如下：

![](https://image.3001.net/images/20191022/1571725038_5dae9eee9af1e.jpg!small)

有了这样的基本框架，作为Red Teaming行动的实施者就可以按照以下的步骤来规划和实施具体的Red Teaming行动了。

![](https://image.3001.net/images/20191022/1571725062_5dae9f0692459.jpg!small)

### 确定目标

确定Red
Teaming行动的目标通常是评估行动结果与效果的最有价值的衡量标准，因此行动前制定明确可度量的目标是非常重要的。比如，我们可以制定以下的行动目标：

成功地在目标系统或者网络里执行所有已经选取的TTPs；

识别所有选取TTPs被防守团队检测和中断所花费的时间。

### 制定计划

一旦确定了行动目标，我们就可以依据ATT&CK框架来制定具体的行动计划了。首先，我们可以按照不同的Tactics把整体的行动分为以下几个阶段。

### 事前准备(Pre-Attack)

T1266 - Acquire OSINT data sets and information. 从开源情报数据中收集目标企业员工的邮箱信息。

### 初始访问（Initial-Access）

T1192 - Spearphishing Link. 利用第三方可信的云存储服务来存放恶意的Word文档作为钓鱼链接。

### 执行（Execution）

T1155 – AppleScript. 利用AppleScript在Mac上运行Python脚本。

T1059 - Command-Line Interface. 使用cmd.exe执行系统命令和恶意代码。

T1085 - Rundll32. 利用Rundll32执行恶意DLL文件。

T1118 - InstallUtil. 利用InstallUtil执行恶意代码。

T1086 - PowerShell. 利用PowerShell在Windows上下载和执行恶意代码。

### 持久化与特权提升（Persistence & Privilege Escalation）

T1197 - BITS Jobs. 使用BITSAdmin下载恶意文件。

T1053 - Scheduled Task. 利用schtasks建立计划任务实现持久化和特权提升。

### 防御绕过（Defensive Evasion）

T1221 - Template Injection. 使用Word远程模版注入的方式执行恶意宏绕过邮件网关的沙箱检测。

T1088 - Bypass User Account Control. 利用Windows计划任务中的环境变量绕过UAC。

### 凭据访问（Credential Access）

T1003 - Credential Dumping. 利用Procdump拉取lsass.exe进程的内存并从中获取明文的用户凭据。

### 命令与控制（Command and Control）

T1104 - Multi-Stage Channels. 使用各种后门工具，Metasploit反向Shell，甚至是RAT工具来作为多层C2通道。

T1219 - Remote Access Tools. 利用开源RAT打造自己的远程控制平台。

### 数据渗出（Exfiltration）

T1041 - ExfiltraOon Over Command and Control Channel. 通过C2通道渗出目标数据。

然后，我们就可以根据上述选择的TTPs设计具体的模拟攻击路径，如下图：

![](https://image.3001.net/images/20191022/1571725162_5dae9f6a39a5f.jpg!small)

### 准备TTPs

根据上面制定的行动计划，我们接下来需要分析所有已选取TTPs的具体技术实现，准备payload以及相应的测试，这时我们就需要依赖在本节一开始提到的包含每个Techniques具体技术细节的ATT&CK攻击框架，以下以部分在上述已制定的行动计划中选取的TTPs的准备为例。

T1192 - Spearphishing Link. 利用第三方可信的云存储服务来存放恶意的Word文档作为钓鱼链接。

![](https://image.3001.net/images/20191022/1571725181_5dae9f7d749ad.jpg!small)

T1155 – AppleScript. 利用AppleScript在Mac上运行Python脚本。

![](https://image.3001.net/images/20191022/1571725197_5dae9f8d88f3a.jpg!small)

T1085 - Rundll32. 利用Rundll32执行恶意DLL文件。

![](https://image.3001.net/images/20191022/1571725222_5dae9fa6ba327.jpg!small)

![](https://image.3001.net/images/20191022/1571725283_5dae9fe35a284.jpg!small)

![](https://image.3001.net/images/20191022/1571725302_5dae9ff6be194.jpg!small)

![](https://image.3001.net/images/20191022/1571725313_5daea0014e1b7.jpg!small)

T1197 - BITS Jobs. 使用BITSAdmin下载恶意文件。

![](https://image.3001.net/images/20191022/1571725329_5daea011b00e6.jpg!small)

T1221 - Template Injection. 使用Word远程模版注入的方式执行恶意宏。

![](https://image.3001.net/images/20191022/1571725343_5daea01fce41b.jpg!small)

![](https://image.3001.net/images/20191022/1571725354_5daea02a6b8c6.jpg!small)

T1003 - Credential Dumping. 利用Procdump拉取lsass.exe进程的内存并从中获取明文的用户凭据。

![](https://image.3001.net/images/20191022/1571725370_5daea03a45c04.jpg!small)

T1219 - Remote Access Tools. 利用开源RAT打造自己的远程控制平台。

![](https://image.3001.net/images/20191022/1571725387_5daea04be6d0e.jpg!small)

T1041 - ExfiltraOon Over Command and Control Channel. 通过C2通道渗出目标数据。

![](https://image.3001.net/images/20191022/1571725405_5daea05de1992.jpg!small)

依据以上TTPs的技术细节，我们就可以快速地制作Red
Teaming行动各个阶段所需的payload（如钓鱼样本，反弹shell样本，持久化与特权提升样本等）和工具（如C2平台，RAT远控工具等）。

### 实施攻击

计划好Red
Teaming行动的具体时间表（例如尽量避开公司业务高峰期和敏感期，尽可能地减少对实际业务的潜在影响），按照规划好的攻击路径和已经准备好的TTPs对目标企业网络实施攻击。

### 完成报告

在完成攻击后，完整且详细地记录以上各个步骤的详细信息和攻击行为时间线，对照行动开始前确定的目标完成结果分析，并最终形成报告，提交至防守团队进行复盘和改进。

## 总结

洋洋洒洒写了这么多，总结起来其实就是一句话：Red
Teaming的攻击形式多种多样、纷繁复杂，然而究其攻击思路其实可以通过ATT&CK框架来梳理和模拟，利用ATT&CK来指导和落地Red
Teaming行动也是帮助防守团队识别当前企业面临的TOP安全威胁的有效方法之一。

## 参考

> <https://attack.mitre.org/>
>
> [Red Team从0到1的实践与思考](http://avfisher.win/archives/1081)

 ***本文作者：安全小飞侠，转载请注明来自FreeBuf.COM**

