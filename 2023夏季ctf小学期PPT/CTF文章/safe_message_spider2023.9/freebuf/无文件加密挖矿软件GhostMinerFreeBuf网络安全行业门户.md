**网络罪犯利用加密挖矿恶意软件盗用计算资源牟利。早在2017年，已经观察到他们如何应用无文件技术使检测和监测更加困难。**

8月观察到一个名为ghostminer的无文件加密货币挖掘恶意软件，该软件利用无文件技术和windows管理工具（wmi）。还观察到GhostMiner
变体修改了被Mykings、PowerGhost、PCASTLE和BuleHub等感染的主机文件。

##  GhostMiner细节

ghostminer使用wmi在受感染的计算机中执行任意代码并保持持久控制。

    
    
    Event Filter\\.\ROOT\subscription:__EventFilter.Name=”PowerShell Event Log Filter”EventNamespace : root\cimv2Query : SELECT * FROM __InstanceModificationEvent WITHIN 3600 WHERE TargetInstance ISA ‘Win32_PerfFormattedData_PerfOS_System’QueryLanguage : WQL
    
    
    FilterToConsumerBinding
    \\.\ROOT\subscription:__FilterToConsumerBinding.Consumer=”CommandLineEventConsumer.Name=\”PowerShell Event Log Consumer\””,Filter=”__EventFilter.Name=\”PowerShell Event Log Filter\””
    Consumer : CommandLineEventConsumer.Name=”PowerShell Event Log Consumer”
    Filter : __EventFilter.Name=”PowerShell Event Log Filter”
    Event Consumer
    \\.\ROOT\subscription:CommandLineEventConsumer.Name=”PowerShell Event Log Consumer”
    CommandLineTemplate : C:\Windows\System32\WindowsPowerShell\v1.0\PowerShell.eXe -NoP -NonI -EP ByPass -W Hidden -E <Base-64 encoded script>

GhostMiner在根目录默认命名空间中安装名为“powershell
command”的wmi类。这个wmi类包含entries命令和base-64编码函数的ccbot。

当触发eventconsumer时，它将从已安装的wmi“powershell command”对象的command和ccbot中读取条目。

执行命令脚本时，将执行以下操作：

![1.PNG](https://image.3001.net/images/20190922/1569124019_5d86eeb36b960.png!small)

除了上述功能外，命令脚本还有一个wmi_killer函数，该函数终止正在运行的进程，并删除与恶意软件系相关联的计划任务和服务，例如：

> 1.[Mykings](https://blog.trendmicro.com/trendlabs-security-> intelligence/uncovering-a-mykings-variant-with-bootloader-persistence-via-> managed-detection-and-response/)
>
> 2.[PowerGhost](https://www.trendmicro.com/vinfo/ph/security/news/cybercrime-> and-digital-threats/fileless-malware-powerghost-targets-corporate-systems)
>
> 3.[PCASTLE](https://blog.trendmicro.com/trendlabs-security-> intelligence/monero-mining-malware-pcastle-zeroes-back-in-on-china-now-uses-> multilayered-fileless-arrival-techniques/)
>
> 4.[BULEHERO](https://www.trendmicro.com/vinfo/us/threat-> encyclopedia/malware/trojan.win32.blueroh.rpb)
>
>
> 5.其他一些恶意软件家族使用的通用malxmr变体，例如：[BlackSquid](https://blog.trendmicro.com/trendlabs-> security-intelligence/blacksquid-slithers-into-servers-and-drives-> with-8-notorious-exploits-to-drop-xmrig-miner/)

wmi_killer还终止使用挖矿恶意软件常用端口列表的tcp通信。

![1.PNG](https://image.3001.net/images/20190922/1569124276_5d86efb49efa5.png!small)另一个命令脚本函数wmi_checkhosts能够修改受感染计算机的主机文件。

![1.PNG](https://image.3001.net/images/20190922/1569166094_5d87930e39b8e.png!small)

同时，ccbot使用两个ip地址，即118.24.63.208和103.105.59.68作为c&c服务器。它使用rot-13、base-64对send命令进行编码。后门通信仅在上午12点到5点之间启用。它每隔30秒使用“/update/cc/cc.php”连续尝试连接到上述IP地址。

除了command和ccbot，“powershell_command”类还包含以下对象：

![1.PNG](https://image.3001.net/images/20190922/1569166774_5d8795b6ce236.png!small)

Miner是一个64位的有效负载，在对命令进行解码和执行时丢弃。但是，在删除之前，ghostminer会确定根驱动器上的可用磁盘空间。如果可用空间小于1
GB，则会减少10 MB大小的负载。然后ghostminer将追加2130字节的随机值，该文件将保存为C:\windows\temp\lsass.exe。

恶意软件随后将执行以下命令：

##
![1.PNG](https://image.3001.net/images/20190922/1569167132_5d87971c8c0b6.png!small)IOCs

![1.PNG](https://image.3001.net/images/20190922/1569167462_5d8798664cfa4.png!small)

***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/fileless-cryptocurrency-miner-ghostminer-weaponizes-wmi-objects-kills-other-cryptocurrency-mining-payloads/)，由Kriston编译，转载请注明来自FreeBuf.COM**

