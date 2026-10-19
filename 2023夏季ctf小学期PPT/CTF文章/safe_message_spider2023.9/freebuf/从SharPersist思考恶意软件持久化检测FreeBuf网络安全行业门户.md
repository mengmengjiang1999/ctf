**持久化（** **Persistence** **）**
是一个攻击链周期中非常重要的环节，攻击者会利用各种技术确保恶意软件在系统上驻留的时间更加长久，即使在设备重启、凭据修改或其他可能破坏当前恶意活动的操作发生后，也能够重新拉起和保持恶意的行为。

建立持久化又分为 **持久化注入** 和 **持久化触发**
两个部分。持久化注入通常指植入恶意payload，通常包括进程注入、EXE文件注入、动态链接库（DLL）注入、HTML应用程序（HTA）注入、脚本注入等；而持久化触发则包括添加自启动项、服务、计划任务等。

国外安全研究人员在九月发布了一个用C#编写的持久化工具包SharPersist，主要用于实现Windows下的各类持久化操作，该项目的开源地址为：https://github.com/fireeye/SharPersist

SharPersist支持的持久化技术包括以下几种：

![2.PNG](https://image.3001.net/images/20191021/1571624076_5dad148c78585.png!small)使用SharPersist实现持久化非常简单，命令行下添加参数即可实现指定的功能，会用到的参数表如下：  

![表格.PNG](https://image.3001.net/images/20191021/1571624100_5dad14a4e5441.png!small)使用-h参数可以获取到非常详细的使用说明，下面用一些实例如何使用SharPersist实现持久化，例如，把notepad.exe添加到注册表自启动：  

> SharPersist.exe -t reg -m add -k "hkcurun" -v "notepad" -c
> "C:\Windows\System32\cmd.exe" -a "/c notepad.exe"

![图片1.png](https://image.3001.net/images/20191021/1571624153_5dad14d987519.png!small)

将powershell命令添加到计划任务：

>SharPersist.exe -t schtask -m add -c
"%SystemRoot%\system32\WindowsPowerShell\v1.0\powershell.exe" -a "-e bypass
C:\Windows\notepad.exe" -n notepad

![图片2.png](https://image.3001.net/images/20191021/1571624162_5dad14e2f198c.png!small)SharPersist中实现的几项持久化功能都是比较容易识别的，实际上还有更多可被利用的持久化技术，MITRE
ATT&CK给出了一份更为详细的列表：  

![表格.PNG](https://image.3001.net/images/20191021/1571624179_5dad14f3d2e18.png!small)

随着对抗手段日益复杂化，持久化技术也将演变得更加隐蔽，想要在端点上识别出攻击者的持久化手段，就需要采集大量的数据进行分析判别，看起来简单的检测工作，在实际环境中面临着很多困难。

在真实环境中捕获有效恶意样本是一个难题，况且还要对采集到的样本进行确认和分类，好在很多渗透测试工具提供了能够实现持久化的功能，如本文提到的SharPersist，还有Metasploit以及Persistence
Aggressor Script等，可以用于模拟各种常见的恶意软件持久化操作，以便安全研究人员从中提取特征。

实际应用中，仍然还会存在很多阻碍，如某些正常软件和运维工具，也可能会触发检测规则，要如何减少类似的误报；在采集和存储系统安全日志时，是否会影响到系统性能，并且在大量的日志中如何有效的进行检测，避免过度消耗资源，都是安全研究人员要面临的挑战。

