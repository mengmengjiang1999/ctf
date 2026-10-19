![](https://image.3001.net/images/20210123/1611390963_600bdff3a58e61ab9ec05.jpg!small)

## 写在前面的话

Windows Defender for Endpoint（以前称为Windows Defender
ATP）是一种“云驱动”的终端安全检测响应系统（EDR），比如说，警报和事件可以被推送到云端，防御人员可以直接在云端做出响应。

在执行红队任务时，最大的障碍之一通常在于规避EDR产品，并确保我们的行动不会被发现。虽然社区在规避和绕过Windows Defender for
Endpoint方面已经投入了大量的工作和研究，但很少有研究探讨是否可以简单地禁用Microsoft Defender，这样就不会有数据发送到云端了。

本文将探讨一种可能的方法，通过利用防火墙规则来阻止Microsoft Defender，以确保没有事件发送到Microsoft
Defender安全中心，即https://securitycenter.windows.com。

Chris Thompson（@retBandit）曾在BlackHat Europe
2017年发表的演讲《红队规避、绕过和禁用MS高级威胁保护和高级威胁分析技术》中详细介绍了修改终端节点Microsoft
Defender的方法。在这篇文章中，我们将讨论如何使用防火墙规则来阻止已知的Windows Defender for Endpoint流量。

## 技术分析

虽然这种技术目前仍然有效，但想要创建一个包含了所有已知MD主机服务URL的防火墙规则其实是非常麻烦的。除此之外，URL列表中还需要包含类似如下的条目：

    
    
    *.blob.core.windows.net
    
    *.azure-automation.net

这样可能会破坏某些Windows服务。在红队研究或渗透测试的情况下，你不想对客户产生过多的负面影响，也不想通过妨碍正常的工作流程来提醒防御者。

因此，我们不想阻止与某些URL的通信，而是想评估是否有可能阻止特定服务和进程的通信，，从而使端点的MD保持“沉默”。为此，我们需要找出哪些进程与端点URL的已知MD通信，并阻止这些特定进程。这里，我们需要的所有信息都已由MD
for Endpoint收集，并通过Microsoft Defender安全中心提供给我们！

MD for Endpoint从所有正在运行的进程收集网络连接，因此可以用来找出哪些进程与已知MD for Defender
URL通信。此时，我们可以通过运行下列[ _Kusto_](https://docs.microsoft.com/en-us/azure/data-explorer/kusto/concepts/)查询来查看这些进程。

    
    
    DeviceNetworkEvents
    
    | where ActionType  ==          "ConnectionSuccess"
    
        and (RemoteUrl  endswith    "ods.opinsights.azure.com"
    
        or  RemoteUrl   endswith    "oms.opinsights.azure.com"
    
        or  RemoteUrl   endswith    "azure-automation.net"
    
        or  RemoteUrl   endswith    "wdcp.microsoft.com"
    
        or  RemoteUrl   endswith    "wdcpalt.microsoft.com"
    
        or  RemoteUrl   endswith    "wd.microsoft.com"
    
        or  RemoteUrl   in      
    
                            (
    
                                    "europe.x.cp.wd.microsoft.com"
    
                            ,       "eu.vortex-win.data.microsoft.com"
    
                            ,       "eu-v20.events.data.microsoft.com"
    
                            ,       "usseu1northprod.blob.core.windows.net"
    
                            ,       "usseu1westprod.blob.core.windows.net"
    
                            ,       "winatp-gw-neu.microsoft.com"
    
                            ,       "winatp-gw-weu.microsoft.com"
    
                            ,       "wseu1northprod.blob.core.windows.net"
    
                            ,       "wseu1westprod.blob.core.windows.net"
    
                            ,       "automatedirstrprdweu.blob.core.windows.net"
    
                            ,       "automatedirstrprdneu.blob.core.windows.net"
    
                            ,       "unitedkingdom.x.cp.wd.microsoft.com"
    
                            ,       "uk.vortex-win.data.microsoft.com"
    
                            ,       "uk-v20.events.data.microsoft.com"
    
                            ,       "ussuk1southprod.blob.core.windows.net"
    
                            ,       "ussuk1westprod.blob.core.windows.net"
    
                            ,       "winatp-gw-uks.microsoft.com"
    
                            ,       "winatp-gw-ukw.microsoft.com"
    
                            ,       "wsuk1southprod.blob.core.windows.net"
    
                            ,       "wsuk1westprod.blob.core.windows.net"
    
                            ,       "automatedirstrprduks.blob.core.windows.net"
    
                            ,       "automatedirstrprdukw.blob.core.windows.net"
    
                            ,       "unitedstates.x.cp.wd.microsoft.com"
    
                            ,       "us.vortex-win.data.microsoft.com"
    
                            ,       "us-v20.events.data.microsoft.com"
    
                            ,       "ussus1eastprod.blob.core.windows.net"
    
                            ,       "ussus1westprod.blob.core.windows.net"
    
                            ,       "ussus2eastprod.blob.core.windows.net"
    
                            ,       "ussus2westprod.blob.core.windows.net"
    
                            ,       "ussus3eastprod.blob.core.windows.net"
    
                            ,       "ussus3westprod.blob.core.windows.net"
    
                            ,       "ussus4eastprod.blob.core.windows.net"
    
                            ,       "ussus4westprod.blob.core.windows.net"
    
                            ,       "winatp-gw-cus.microsoft.com"
    
                            ,       "winatp-gw-eus.microsoft.com"
    
                            ,       "wsus1eastprod.blob.core.windows.net"
    
                            ,       "wsus1westprod.blob.core.windows.net"
    
                            ,       "wsus2eastprod.blob.core.windows.net"
    
                            ,       "wsus2westprod.blob.core.windows.net"
    
                            ,       "automatedirstrprdcus.blob.core.windows.net"
    
                            ,       "automatedirstrprdeus.blob.core.windows.net"
    
                            ,       "ussus1eastprod.blob.core.windows.net"
    
                            ,       "ussus1westprod.blob.core.windows.net"
    
                            ,       "usseu1northprod.blob.core.windows.net"
    
                            ,       "usseu1westprod.blob.core.windows.net"
    
                            ,       "ussuk1southprod.blob.core.windows.net"
    
                            ,       "ussuk1westprod.blob.core.windows.net"
    
                            ,       "ussas1eastprod.blob.core.windows.net"
    
                            ,       "ussas1southeastprod.blob.core.windows.net"
    
                            ,       "ussau1eastprod.blob.core.windows.net"
    
                            ,       "ussau1southeastprod.blob.core.windows.net"
    
                            ))
    
    | summarize     Count                           = count()
    
        ,           RemoteUrl                       = make_set(RemoteUrl)
    
        ,           InitiatingProcessCommandLine    = make_set(InitiatingProcessCommandLine)
    
                by  InitiatingProcessFileName
    
    | where         Count > 10
    
    | sort      by  InitiatingProcessFileName

 **下图显示的是查询结果：**

![](https://image.3001.net/images/20210123/1611390998_600be016b30b8e01d34a1.png!small)

浏览一下这个列表，我们发现有几个进程显示为与MD for
Endpoint无关的进程。比如说Teams.exe，它是微软的官方团队客户端，虽然它会给已知的MD URL发送事件。

对于那些比较熟悉MD for Endpoint的人来说，对这些进程的透彻理解将有助于使用Windows防火墙有效地阻止它们。

> SenseIR.exe：在Microsoft Defender安全中心启动“实时响应会话”时，作为MsSense.exe生成的子进程运行。
>
>
> SenseCncProxy.exe：作为MsSense.exe生成的子进程运行，可以将其描述为“通信模块”，因此可能会处理与前面提到的url的通信，并且如果应用了此功能，还会启动代理。
>
> SenseCncProxy.exe：Defender for
> Endpoint的主服务可执行文件，它将以服务的形式运行，服务名为“Sense”。（Windows 10）
>
> MpCmdRun.exe：Microsoft Defender
> Antivirus主服务的可执行文件，它将以服务的形式运行，服务名为“WinDefend”。（Windows 10）
>
> MpCmdRun.exe：用于执行各种Microsoft Defender防病毒功能的命令行工具。
>
> MonitoringHost.exe：作为HealthService的子进程生成的可执行文件，它是Microsoft Monitoring
> Agent的一部分，在使用以前版本的Windows（Server 2016及以下版本+Windows 8.1
> Enterprise及以下版本）登录设备时会安装。
>
> HealthService.exe：Microsoft Monitoring Agent的主服务可执行文件，在使用以前版本的Windows（Server
> 2016及以下版本+Windows 8.1 Enterprise及以下版本）登录设备时会安装。

此外，还有一系列本机Windows服务（如utcsvc和diagtrack）也与已知的URL通信，但在我们的测试中，它们没有为Defender for
Endpoint发送任何与MD相关的事件或警报数据。

## PoC-防火墙规则

### Windows 10和Windows Server 2019

在Windows 10和Windows Server 2019上禁用MD for
Endpoint相对来说比较简单，因为我们只需要阻止MsMpEng、SenseCncProxy和MsSense三个进程在端口443上向外发送流量即可。运行以下PowerShell脚本将有效地屏蔽Windows
Defender，并且不会触发任何警报：

    
    
    New-NetFirewallRule -DisplayName "Block 443 MsMpEng" -Name "Block 443 MsMpEng" -Direction Outbound -Service WinDefend -Enabled True -RemotePort 443 -Protocol TCP -Action Block
    
    New-NetFirewallRule -DisplayName "Block 443 SenseCncProxy" -Name "Block 443 SenseCncProxy" -Direction Outbound -Program "%ProgramFiles%\Windows Defender Advanced Threat Protection\SenseCncProxy.exe" -RemotePort 443 -Protocol TCP -Action Block
    
    New-NetFirewallRule -DisplayName "Block 443 MsSense" -Name "Block 443 MsSense" -Direction Outbound -Program "%ProgramFiles%\Windows Defender Advanced Threat Protection\MsSense.exe" -RemotePort 443 -Protocol TCP -Action Block

在Windows中添加防火墙规则需要本地管理员权限，因此无法使用低权限用户帐户进行攻击。从以下Microsoft
Defender安全中心界面来看，一旦应用防火墙规则，就不会收到任何事件。

![](https://image.3001.net/images/20210123/1611391019_600be02befc57b90b6af1.png!small)

但是，似乎所有事件都在本地缓存，因此一旦删除防火墙规则，事件和警报将开始显示在Microsoft Defender Security Center中。

![](https://image.3001.net/images/20210123/1611391029_600be035111d09d33f094.png!small)

