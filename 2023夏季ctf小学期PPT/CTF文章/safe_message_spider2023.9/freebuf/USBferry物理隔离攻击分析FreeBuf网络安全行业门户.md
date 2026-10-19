**Tropic
Trooper组织自2011年来，主要针对台湾，菲律宾、香港的政府，军事，医疗保健，运输和高科技行业进行攻击。该组织使用带有恶意附件的鱼叉式网络钓鱼邮件为主要手段。**

近期发现Tropic
Trooper在利用USBferry进行攻击，主要针对台湾和菲律宾的物理隔离网络，还发现了军事/海军机构，政府机构，军事医院甚至国家银行等受害目标。USBferry是一种USB恶意软件，可以对特定目标执行不同的命令，在目标环境中隐藏自身，通过USB存储设备窃取关键数据。USBferry自2014年以来一直保持活跃，该组织专注于从目标网络窃取与国防，海洋和船舶有关的文档。

##
![](https://image.3001.net/images/20200522/1590106417_5ec7193165e99.png!small)版本分析

目前已发现USBferry恶意软件的三个版本，以下是分析要点：

第一个版本具有[TROJ_YAHOYAH](https://documents.trendmicro.com/assets/wp/wp-operation-tropic-trooper.pdf)的一小部分。
该恶意软件会检查目标计算机是否有USB插件，并将USBferry安装程序复制到USB中，从而执行命令，获取目标文件或文件夹列表，将文件从物理隔离的主机复制到受感染的主机等。  

![](https://image.3001.net/images/20200522/1590106660_5ec71a2415f33.png!small)第二个版本与第一个版本功能相同，并将组件组合成一个可执行文件。该版本还将恶意软件的位置及其名称更改为UF，即USBferry的缩写。  

![](https://image.3001.net/images/20200522/1590106717_5ec71a5d89f4e.png!small)第三个版本保留了先前版本的功能，并提高了其在目标环境中的隐蔽性。

##
![](https://image.3001.net/images/20200522/1590106791_5ec71aa7aeb5e.png!small)技术分析

该组织通过USB蠕虫感染策略，将USB将恶意软件安装到物理隔离主机中来实现感染。  

![](https://image.3001.net/images/20200522/1590106882_5ec71b0242610.png!small)下图分析了在UF1.0
20160226版本中该组织的攻击链：

![](https://image.3001.net/images/20200522/1590106966_5ec71b564887f.png!small)

> 1、诱饵文件首先植入flash_en.inf DLL文件（即USBferry加载器），然后加载加密的USBferry恶意软件
>
> 2、加密的USBferry恶意软件嵌入在加载程序资源中，加载程序将其放入C:\Users\Public\Documents\Flash
> 文件夹并命名为flash.dat
>
>
> 3、加载有效负载后，加载程序会将恶意DLL注入rundll32.exe，USBferry恶意软件还会加载C＆C配置文件和flash_en.dat，它们也位于C:\Users\Public\Documents\Flash
>
> 4、USBferry恶意软件尝试连接到c&c，并使用Windows命令收集/复制目标主机数据。

如果发现网络不可用，它将尝试从目标计算机收集信息，并将收集的数据复制到USB存储设备中，等待可访问网络后再发送。

接下来介绍Tropic Trooper使用的后门：  

WelCome To Svchost 3.2 20110818后门（检测为BKDR_SVCSHELL.ZAHC-A）。
根据恶意软件的版本号，此后门的第一个版本是在2011年或之前开发的，这意味着Tropic Trooper攻击活动已经进行了至少十年。  

![](https://image.3001.net/images/20200522/1590107309_5ec71cadf0871.png!small)WelCome
To IDShell 1.0
20150310后门（检测为BKDR_IDSHELL.ZTFC-A），此后门具有两种类型，其中包括隐写jpg版本，目的是对目标计算机进行侦察。
与其他版本一样，它使用DNS协议与服务器通信，并加密通信流量来逃避检测。  

![](https://image.3001.net/images/20200522/1590107420_5ec71d1ce2abd.png!small)Hey!
Welcome Server 2.0’s后门（检测为BKDR_TEBSHELL.ZTGK），这是最新版本后门，有32位和64位版本，它使用不可见的Web
Shell远程控制目标。它会以服务的形式运行，将后门通信隐藏在正常流量中，并使用自定义的TCP协议。  

![](https://image.3001.net/images/20200522/1590107539_5ec71d939b853.png!small)Tropic
Trooper在攻击中还使用了其他工具，例如：

> 1、多版本Command-line远程侦听/端口中继工具，可与目标后门进行通信。  
>
>
> 2、后门/隐写载荷加载器，可用加载加密的有效载荷并删除自身和有效载荷。
>
> 3、端口扫描工具。

隐写术不仅用于传递加密的有效载荷，也可以将信息传输到C＆C服务器。Tropic Trooper使用不可见的Web
Shell来隐藏其C＆C服务器位置，使事件响应分析变得更加复杂。  

## MITRE ATT&CK Matrix  

![](https://image.3001.net/images/20200522/1590107884_5ec71eececd52.png!small)

## 解决方案

Tropic
Trooper最新发现表明，它们已经可以针对政府机构和军事机构窃取情报。该组织还需要很长时间来执行前期侦察，渗透到物理隔离的网络中。可以采取以下措施来阻止高级持续性威胁：

> 1、强制执行最小特权原则，使用网络分段和数据分类来阻止横向移动。  
>
>
> 2、保持系统及其应用程序更新，实行补丁管理策略。
>
> 3、定期监察网关，端点，网络和服务器之间的检测响应，及时发现各种网络安全威胁。防火墙和入侵检测系统可以帮助发现阻止网络攻击。

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/tropic-troopers-back-usbferry-attack-targets-air-gapped-environments/)，由Kriston编译，转载请注明来自FreeBuf.COM**

