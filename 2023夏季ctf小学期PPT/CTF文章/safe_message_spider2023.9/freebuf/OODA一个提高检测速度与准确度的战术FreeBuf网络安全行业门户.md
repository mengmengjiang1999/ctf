本文通过模拟恶意软件使用 Microsoft Sysinternals 工具 [PsExec](https://docs.microsoft.com/en-us/sysinternals/downloads/psexec)进行横向移动、主机与网络侦察，展示如何使用
[OODA](http://www.infosecisland.com/blogview/20783-The-Information-Security-OODA-Loop-An-Introduction.html)循环帮助提高检测速度与准确性。对于没有了解过 OODA
的人来说，可以将其认为是一个战略军事概念。OODA
建议使用者比攻击者更快地经历以下四个阶段来赢得胜利：观察（Observe）、判断（Orient）、决策（Decide）、行动（Act）。

## 观察阶段

某天下午，端点触发了用于查找重命名 PsExec
实例检测用例。因为观测到过许多攻击者将工具重命名以逃避检测的情况，所以我们的检测团队开发了该检测用例。PsExec
存在许多合法的用法，但合法工具会被攻击者滥用，PsExec 已经成为攻击者进行横向移动时的首选工具。

首先观察到以下攻击事件：

![](https://image.3001.net/images/20210818/1629293521_611d0bd19c914592a0db3.png!small)

看起来用户已经从 Downloads 文件夹执行了 PsExec 的重命名文件，该操作尝试在另一台计算机上启动远程
Shell。继续排查时间线时，我们发现用户桌面启动了另一个高度可疑的批处理脚本。

![](https://image.3001.net/images/20210818/1629293535_611d0bdf3867900d700b9.png!small)

恶意软件可以将二进制文件释放到磁盘上，或者无文件利用命令快速地进行横向移动。此时的情况是，恶意软件释放了 PsExec
的副本文件，滥用合法工具。通过网络数据狩猎 PsExec 是很困难的，找到其真实意图的唯一方法是查看其在目标设备上执行了哪些命令以及什么释放了
PsExec。即使有端点数据，也需要更广泛地上下文信息来分析原始意图。

## 判断阶段

我们已经知道在另一个系统中尝试启动了远程 Shell，下一个问题是文件从何而来？我们注意到启动 PsExec 的同一个批处理脚本也进行了对域和网络的侦察。

让我们看一下已经写入的注册表键值，通过失陷主机上的 reg.exe 执行：

    
    
    REG QUERY "HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion" /v ProductNameREG QUERY "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\IEData" /v DisplayNameREG QUERY "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"REG QUERY HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\REG QUERY "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Sophos Endpoint Defense" /v DisplayName

根据这些执行的命令可以对检测提出几个问题：

> 这些命令通常在该环境下会被执行吗？
>
> 程序 reg.exe 执行的次数？
>
> 该环境下什么文件会产生 reg query 命令？
>
> 这些端点上运行了 Sophos 吗？

### 网络侦察

在 PsExec 启动前，该恶意软件会通过释放已重命名为 d.exe 的合法 Windows 文件来获取主机与账户信息。该工具正常情况下叫
csvde.exe，会在安装有 Active Directory Lightweight Directory 服务的 Windows
服务器上出现。主要用途是通过 CSV 格式导入导出活动目录信息。

恶意软件利用这个工具从活动目录中提取所有主机信息，利用其中提供的信息可以遍历每台计算机测试访问权限。

![](https://image.3001.net/images/20210818/1629293548_611d0bec151722b25fb8e.png!small)

恶意软件释放的另一个文件是 host2ip45.exe，该文件检查主机是否存活。根据文件名，该恶意软件能够快速找到下一个目标。

![](https://image.3001.net/images/20210818/1629293562_611d0bfa6f7a30ad61706.png!small)

现在该恶意软件掌握了从 host2ip45.exe 得到的主机与 IP 地址信息。随后通过开放、可写的网络共享查找简单的路由。使用 copy
命令测试每台主机都具有可访问的网络共享权限。

![](https://image.3001.net/images/20210818/1629293576_611d0c08624ca99b72b23.png!small)

最后，该恶意软件下载了另一个文件，该文件针对域控制器对网络账户进行爆破。该二进制文件的元数据暗示其使用 net 命令进行密码爆破：

![](https://image.3001.net/images/20210818/1629293590_611d0c166598630f4ea43.png!small)

该恶意软件尝试使用常用密码映射到域控制器的驱动器。

![](https://image.3001.net/images/20210818/1629293602_611d0c22288fe013e1081.png!small)

下图显示了一些爆破的命令行参数：

![](https://image.3001.net/images/20210818/1629293614_611d0c2ec42261d7b241a.png!small)

### 主机侦察

最初的批处理脚本不仅针对网络进行侦察，还在主机上查找与金融和社交网站有关的字符串，这是与信息窃密相关的常见手段。该恶意软件使用 Windows 中的
findstr 命令来查找包含特定字符串的文件名，如 paysurfer、paypal 与 coinbase：

![](https://image.3001.net/images/20210818/1629293633_611d0c4147a1a7a611cd2.png!small)

## 决策与行动阶段

我们已经非常确定这一行为是违规的恶意行为，快速的告警可以通知客户尽快进行应急处理。威胁检测团队依据观测数据撰写并发布了检测结果，事件处理团队根据客户的事件响应手册帮助协调了补救措施。

## 重复循环以提高速度与准确性

威胁检测团队会根据速度与准确性对检测报告进行评估，后续研究是否可以更快地检测该攻击行动，为接下来的改进提供帮助。比如开发[自动检测用例](https://www.redcanary.com/blog/breathing-life-detection-capability/)，帮助处理大量数据并快速发现威胁。

对于这种恶意软件感染，仍然使用 OODA 循环处理检测用例的过程。

### 观察阶段

就自动化与侦察技术而言，该恶意软件非常强大，仅在本次感染中就表现出包括横向移动、主机侦察与网络侦察。对于每个阶段都可以评估是否可以构造新的检测用例。

### 判断阶段

从蓝队的视角看，构造高度准确的检测用例是很难的。如果其检测面很窄，就可能会错过恶意行为。如果检测面过宽，就会显著增加噪声。但是如果将重点转移到创建更多从不同角度狩猎潜在威胁的检测用例，也许就能够平衡该风险。通过该方法，我们注意到了一些可行的新式检测技术。

以重命名技术为例，查看执行链的独特性非常有价值。当然，在不是 Windows 服务器上执行 csvde.exe
确实就非常罕见，尤其是对于非管理员用户。另一个是进行静态分析，如 Carbon Black 在本例中捕获的元数据：

![](https://image.3001.net/images/20210818/1629293645_611d0c4d3836ae50dc5e5.png!small)

这种恶意软件感染是由重命名检测用例发现的，另一个寻找重命名的检测用例也可能会提供有价值的数据。一种选择是检查内部名称是否等于
ldifldap.lib、进程名是否不等于常规进程名 csvde.exe。

### 决策阶段

这个新的检测用例看起来很有用，服务器管理员在日常操作中会重命名 Windows 文件吗？我们的判断是就像重命名 PsExec 一样，几乎永远不会发生。

快速搜索端点数据帮助我们确定这个检测用例是否可行。例如 `(internal_name:ldifldap.lib OR internal_name:
csvde.exe) AND -process_name:csvde.exe`就能证明存在该类感染。

![](https://image.3001.net/images/20210818/1629293655_611d0c5783a3da855fd4f.png!small)

### 行动阶段

这在我们所有的客户中都取得了不错的效果，对于新检测用例，这听起来确实不错。但部署新检测用例之前，仍然需要典型的开发与测试过程。进入平台的最终检测用例如下所示：

    
    
    detects dowindows? &&process_name? &&process_name_not_equal_to?(['csvde.exe']) &&( internal_name_downcased == 'ldifldap.lib' ||internal_name_downcased == 'csvde.exe' )

## 防御的要诀

防御者一直在寻找更好的、更新的、更简单的、更强大的检测技术，其实最重要的是花时间确保最大程度地利用已有工具、人员和技术。重新收集这类信息进行分析，不让它们闲置在角落，防御者应该时刻保持警惕性。

## 参考来源

> [RedCanary](https://redcanary.com/blog/ooda-loop-improving-detection/)

