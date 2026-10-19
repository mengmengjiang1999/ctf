近日，著名安全厂商火眼发布了一款用于威胁情报分析的虚拟机，事实上就是将大量分析需要使用的工具集成在一个windows系统中，并将安装脚本发布到了github中。

通过该虚拟机里面集
合的工具，我们可以看出，大洋彼岸的分析师们在进行情报分析过程中需要用到的比较前沿的工具以及对应的技能，也可以看出关于这个行业未来的一些趋势。

开发, 分析和机器学习工具:

  * Shogun
  * Tensorflow
  * Pytorch
  * Rstudio
  * RTools
  * Darwin
  * Keras
  * Apache Spark
  * Elasticsearch
  * Kibana
  * Apache Zeppelin
  * Jupyter Notebook
  * MITRE Caret
  * Python (x64)

从提及的工具不难看出，海量数据的处理是国外分析人员的日常，同时机器学习在对威胁情报类数据方面有帮助。

可视化工具：

  * Constellation
  * Neo4J
  * CMAP

用于威胁情报数据的展示，数据建模后的可视化结果。

取证, 建模 & 狩猎工具：

  * MISP（本地恶意软件信息共享平台）

![1604417770_5fa178ea926f4e2a5e0b5.png!small](https://image.3001.net/images/20201103/1604417770_5fa178ea926f4e2a5e0b5.png!small)  
推荐体验

![1604417781_5fa178f5e35731dcc8a27.png!small](https://image.3001.net/images/20201103/1604417781_5fa178f5e35731dcc8a27.png!small)

  * OpenCTI
  * Maltego
  * Splunk
  * MITRE ATT&CK Navigator
  * Greynoise API and GNQL
  * threatcrowd API
  * threatcmd
  * ViperMonkey
  * Threat Hunters Playbook
  * MITRE TRAM
  * SIGMA
  * YETI
  * Azure Zentinel
  * AMITT Framework

对抗仿真工具：

  * MITRE Calderra
  * Red Canary ATOMIC Red Team
  * MITRE Caltack Plugin
  * APTSimulator
  * FlightSim  
![1604417793_5fa17901401775c979b08.png!small](https://image.3001.net/images/20201103/1604417793_5fa17901401775c979b08.png!small)

信息收集工具

  * Maltego

![1604417802_5fa1790a1fdbcbbd046fa.png!small](https://image.3001.net/images/20201103/1604417802_5fa1790a1fdbcbbd046fa.png!small)

  * nmap
  * intelmq
  * dnsrecon
  * orbit
  * FOCA

实用的工具、用于连接网络的工具：

  * CyberChef
  * KeepPass
  * FLOSS
  * peview
  * VLC
  * AutoIt3
  * Chrome
  * OpenV PN
  * Sublime
  * Notepad++
  * Docker Desktop
  * HxD
  * Sysinternals
  * Putty

Github链接:

[https://github.com/fireeye/ThreatPursuit-VM](https://link.zhihu.com/?target=https%3A//github.com/fireeye/ThreatPursuit-VM)

虚拟机要求：

Windows 10 1903

120GB+ 硬盘

8GB以上内存

1个网络适配器

1024mb显卡内存

启用对VM的虚拟化支持（Docker必需）

安装说明:

在一台安装完最新Windows系统的全新虚拟机或docker上（需要先装好java和chrome浏览器），拷贝install.ps1，再用管理员权限打开powershell，运行两个命令解开脚本运行限制在运行安装脚本主体。

Unblock-File .\install.ps1

Set-ExecutionPolicy Unrestricted -f

.\install.ps1

![1604417812_5fa17914761c189f41aa0.png!small](https://image.3001.net/images/20201103/1604417812_5fa17914761c189f41aa0.png!small)

或者也可以加.\install.ps1 -password 来设置密码。

![1604417819_5fa1791b63ee96e17a056.png!small](https://image.3001.net/images/20201103/1604417819_5fa1791b63ee96e17a056.png!small)

最后安装效果如下图

![1604417825_5fa179216fd8b29bf471e.png!small](https://image.3001.net/images/20201103/1604417825_5fa179216fd8b29bf471e.png!small)

 **参考链接：**

[https://www.fireeye.com/blog/threat-research/2020/10/threatpursuit-vm-threat-intelligence-and-hunting-virtual-machine.html](https://link.zhihu.com/?target=https%3A//www.fireeye.com/blog/threat-research/2020/10/threatpursuit-vm-threat-intelligence-and-hunting-virtual-machine.html)

此前火眼还发布过两款虚拟机

恶意软件分析专用虚拟机：

[https://github.com/fireeye/flare-vm](https://link.zhihu.com/?target=https%3A//github.com/fireeye/flare-vm)

红队渗透测试专用虚拟机：

[https://github.com/fireeye/commando-vm](https://link.zhihu.com/?target=https%3A//github.com/fireeye/commando-vm)

有兴趣的都可以在保证安全的前提下使用。

