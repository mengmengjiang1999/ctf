近日，ASEC 分析人员发现 Kimsuky 组织正在使用 xRAT（基于 Quasar RAT 定制的开源 RAT）恶意软件。

根据 AhnLab 收集到的日志，在 1 月 24 日攻击者在失陷主机上部署了 Gold Dragon 的变种。判断是 Gold Dragon 的依据如下：

> 样本注入方式与 Gold Dragon 的方法相同，都是在 iexplore.exe、svchost.exe 等进程上执行 process
> hollowing
>
> 通过 49B46336-BA4D-4905-9824-D282F05F6576 终止 AhnLab 产品
>
> 终止 Daum Cleaner (daumcleaner.exe) 进程

攻击者通过专属安装程序 `installer_sk5621.com.co.exe`安装 Gold Dragon，程序通过 C&C 服务器下载 Gzip
压缩的 Gold Dragon 样本并在 `%temp%`路径中将其解压为 `in[random 4 numbers].tmp`，再通过
rundll32.exe 执行。

本次发现的 Gold Dragon 有四个导出函数：

> Perform
>
> Process
>
> Start
>
> Work

安装程序通过 `Start`参数执行 Gold Dragon。在执行 `Start`导出函数后，Gold Dragon 会复制自身到指定位置并设置 DLL
文件持久化，注册表项中使用了 `Perform`参数。

![image.png-54.4kB](https://image.3001.net/images/20220211/1644558428_6205f85c414c4124f3c6f.png!small)注册表

发现的变种文件使用系统命令获取相关信息，这才过往的样本中并未发现。这意味着攻击者可能使用了模块化加载，攻击者可以通过 C&C
服务器下载其他模块获得更多功能。

> cmd.exe /c ipconfig/all >>”%s” & arp -a >>”%s”  
> cmd.exe /c systeminfo >>”%s”  
> cmd.exe /c tasklist >>”%s”

攻击者通过安装 xRAT（`cp1093.exe`）来为远程控制提供便利。样本执行后会复制正常的 PowerShell
进程（`powershell_ise.exe`）到 `C:\ProgramData\`路径并通过 process hollowing 执行。

![image.png-118.1kB](https://image.3001.net/images/20220211/1644558429_6205f85dd19244df0f143.png!small)xRAT

攻击者为了清除攻击痕迹，还开发了额外的程序（`UnInstall_kr5829.co.in.exe`）随着 xRAT 一起下发。

![image.png-157.9kB](https://image.3001.net/images/20220211/1644558430_6205f85e6a752aa6b7f77.png!small)清除痕迹代码

## IOC

> 40b428899db353bb0ea244d95b5b82d9  
> 4ea6cee3ecd9bbd2faf3af73059736df  
> 070f0390aad17883cc8fad2dc8bc81ba  
> b841d27fb7fee74142be38cee917eda5

## 参考来源

> [ASEC](https://asec.ahnlab.com/en/31089/)

