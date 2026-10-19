## 1、安全加固服务概述

为xxx单位提供为期n年的主机安全加固服务，加固的服务器数量n台。并每月提供安全加固报告。对xxx单位的重要业务服务器做资产清点，建立主机资产档案。实施网络隔离技术，防止攻击者入侵重要业务系统。持续监控主机潜在的风险，发现主机内漏洞、病毒、后门、木马。对主机攻击事件进行溯源分析，提供整改建议。

IT技术扩张迅猛，主机面对的各种高级攻击层出不穷。其中，超过80%的恶意攻击发生在应用层，且被攻击者往往损失惨重，同时，开源框架引入比率大幅度增高，面对突发漏洞往往束手无策。自身代码问题虽然可以修复,但修复周期长，期间损失无法避免。目前的主机安全解决方案无一例外的把重点放在网络安全层面，致使面临应用层攻击（如：针对WEB应用的SQL注入攻击、跨站脚本攻击等）发生时，传统的网络防火墙、IDS/IPS等安全产品对主机的攻击几乎不起作用。

## 2、安全加固服务目标

###  **解决服务器资产缺乏统一管控问题**

通过主机加固服务梳理主机内部账户、进程、网络连接、Web站点、Web应用、数据库、环境变量等多种类型资产，识别出发生变更的业务资产的安全风险，并随时跟踪资产风险。

###  **解决主机高级持续性威胁问题**

现有主机防护方案无法快速响应未知威胁，导致发生数据泄露等安全事件后无法追踪溯源。通过主机加固服务可降低主机被入侵风险，通过WAF探针、RASP探针、ASVE、管理中心沙箱、内核加固等多手段、多层级抵御已知/未知威胁。

###  **保护业务应用系统和应用**

对主机的操作系统文件、进程、注册表、服务进行保护，对用户业务应用系统进行保护，防止用户业务应用系统程序意外终止，确保xxx单位重要业务系统的业务连续性。

## 3、安全加固服务范围

xxx单位的重要业务信息系统。

##  ** **4、安全加固服务内容****

###  **资产清点**

通过主机加固服务工具，识别所有与该主机具有访问关系的资产，确保与相互访问的资产具有可靠性。梳理主机内部账户、进程、网络连接、Web站点、Web应用、数据库、环境变量等多种类型资产，通过对业务系统持续学习，自动发现并跟踪业务信息资产的变更（包括服务器、服务器上运行的软件、网站、以及web应用类型等），并采用交互式安全检测技术（IAST）自动识别出发生变更的业务资产的安全风险。以月为单位提供资产清点报告。

###  **流程控制**

通过主机加固服务工具获取流量信息（网络通信五元组及业务标签信息）上传到云管理中心。访问控制规则判断：基于流量中的ip、端口等数据信息以及识别到的业务角色标签与策略库规则做对比，符合的流量访问可以通过，不符合的流量访问将拒绝访问。通过细粒度的网络隔离技术，跨物理网络自定义虚拟安全边界以及自定义基于角色的访问控制策略，防止攻击者入侵内部业务网络后的东西向移动。并通过可视化把握业务系统网络信息流动情况。以月为单位提供流量控制报告。

###  **风险发现**

通过主机加固服务工具持续更新引擎库以及Agent探针发现主机中的病毒、木马及后门。扫描所有主机上的漏洞、病毒、后门、木马、合规基线性能指标，持续监控潜在风险。以月为单位提供风险发现报告。

###  **入侵检测**

通过安全服务工具详细记录应用层、系统层、内核层的所有行为，智能关联分析，通过IOC展示攻击者每次攻击的攻击流，快速定位风险点。对攻击事件进行分析，将攻击事件进行整理，汇总成风险报告呈现给用户，减少大量同类事件给用户带来的困扰。以月为单位提供入侵检测报告。

## 5、 ** **Windows Server平台加固****

###  **5.1** ** **系统防护-操作系统加固****

 **a. 禁止更改系统可执行文件**

加固方法：

Windows Server服务器安装Agent端，PC管理端开启禁止更改系统可执行文件

![1646203021_621f108dadc3ebd7683a9.png!small?1646203024847](https://image.3001.net/images/20220302/1646203021_621f108dadc3ebd7683a9.png!small?1646203024847)

修改C:\Windows\hh.exe所有者为administrator

![1646203061_621f10b56ce507cf5150e.png!small?1646203062611](https://image.3001.net/images/20220302/1646203061_621f10b56ce507cf5150e.png!small?1646203062611)

修改C:\Windows\hh.exe权限administrator（具有完全控制）

![1646203084_621f10ccb79f280fafa9d.png!small?1646203089030](https://image.3001.net/images/20220302/1646203084_621f10ccb79f280fafa9d.png!small?1646203089030)

加固验证：

使用无驱动签名exe工具打开C:\Windows\hh.exe；打开路径C:\Windows\hh.exe；操作“追加”-确定

![1646204284_621f157c949a0803f4677.png!small?1646204288081](https://image.3001.net/images/20220302/1646204284_621f157c949a0803f4677.png!small?1646204288081)

观察PC管理端-日志查询-系统防护日志；

观察Web管理端-入侵检测-事件回溯；

观察Web管理端-入侵检测-安全日志。

 **b.禁止更改系统可引导文件**

加固方法：

Windows
Server服务器安装Agent端，PC管理端开启禁止更改系统可引导文件；通过在C盘搜索找到bootmgr文件，将文件复制到C盘根目录；修改C:\bootmgr文件所有者为administrator

![1646204404_621f15f4c237cfb0353af.png!small?1646204407367](https://image.3001.net/images/20220302/1646204404_621f15f4c237cfb0353af.png!small?1646204407367)

修改C:\bootmgr文件权限administrator

![1646204435_621f1613c94c7d44c3f5b.png!small?1646204438629](https://image.3001.net/images/20220302/1646204435_621f1613c94c7d44c3f5b.png!small?1646204438629)

加固验证：

使用无驱动签名工具exe工具打开C:\bootmgr；打开路径C:\bootmgr；操作“追加”-确定。

### c. **禁止非系统进程创建autorun.inf文件**

加固方法：

将测试工具中的inf文件拷贝至C盘根目录；将测试工具中的exe拷贝至C盘根目录；Windows
Server服务器安装Agent端，PC管理端开启非系统进程创建dll文件

![1646204578_621f16a2c0823f0fd3323.png!small?1646204579154](https://image.3001.net/images/20220302/1646204578_621f16a2c0823f0fd3323.png!small?1646204579154)

加固验证：

执行非驱动签名exe打开autorun.inf，另存为autorun.inf文件。

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯。

观察Web管理端-入侵检测-安全日志。

 **d.禁止非系统进程创建Usp10.dll文件**

加固方法：

准备程序：将测试工具文件夹中的exe拷贝至C盘根目录。将C:\windows\winhlp32.exe拷贝至C盘根目录。

Windows Server服务器安装Agent端，PC管理端开启非系统进程创建dll文件。

![1646205072_621f189033ef6e4c478f9.png!small?1646205072545](https://image.3001.net/images/20220302/1646205072_621f189033ef6e4c478f9.png!small?1646205072545)

加固验证：

执行exe，文件路径输入C:\winhlp32.exe，重命名文件名C:\usp10.dll，勾选“目标文件重命名”，选择确定。

![1646205101_621f18ad42cb047929a8d.png!small?1646205102961](https://image.3001.net/images/20220302/1646205101_621f18ad42cb047929a8d.png!small?1646205102961)

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯。

观察Web管理端-入侵检测-安全日志。

 **e.防止对外服务进程执行危险命令**

加固方法：

Windows Server服务器安装Agent端，PC管理端开启系统防护-操作系统加固-对外服务进程执行危险命令。

![1646205226_621f192aa1bb506335504.png!small?1646205227018](https://image.3001.net/images/20220302/1646205226_621f192aa1bb506335504.png!small?1646205227018)

确保开启以下防护开关

![1646205251_621f194396733f085e0b4.png!small?1646205254809](https://image.3001.net/images/20220302/1646205251_621f194396733f085e0b4.png!small?1646205254809)

将高级防护中小开关全部关闭

![1646205277_621f195d2fc8ed741e680.png!small?1646205281016](https://image.3001.net/images/20220302/1646205277_621f195d2fc8ed741e680.png!small?1646205281016)

加固验证：

访问服务器的域名，例如：http://192.168.8.22:8080/newShell/hello.jsp。在Execute
Command中执行net.exe

![1646205548_621f1a6ca43072c172d73.png!small?1646205549483](https://image.3001.net/images/20220302/1646205548_621f1a6ca43072c172d73.png!small?1646205549483)

观察Agent端拦截情况。

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯。

观察Web管理端-入侵检测-安全日志。

 **f.禁止非系统进程创建Lpk.dll文件**

加固方法:

准备程序：将测试工具文件夹中的exe拷贝至C盘根目录。

将C:\windows\winhlp32.exe拷贝至C盘根目录。

Windows Server服务器安装Agent端，PC管理端开启非系统进程创建dll文件

![1646205653_621f1ad59c36dd41f2bee.png!small?1646205653958](https://image.3001.net/images/20220302/1646205653_621f1ad59c36dd41f2bee.png!small?1646205653958)

加固验证：

执行File.exe，文件路径输入C:\winhlp32.exe，重命名文件名C:\lpk.dll，勾选“目标文件重命名”，选择确定。

![1646205683_621f1af395e6a1c1456e5.png!small?1646205685351](https://image.3001.net/images/20220302/1646205683_621f1af395e6a1c1456e5.png!small?1646205685351)

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯。

观察Web管理端-入侵检测-安全日志。

 **g.禁止非系统进程在系统目录下创建可执行文件**

加固方法：

将测试工具中的exe和Notepad.exe拷贝至C盘根目录。

关闭操作系统加固-禁止更改系统可执行文件（windows系统进程例外）[如无法单独关闭小开关，请先开启高级防护]

Windows Server服务器安装Agent端，PC管理端开启非系统进程在系统目录下创建可执行文件

![1646205781_621f1b5510fa9dab8557b.png!small?1646205781573](https://image.3001.net/images/20220302/1646205781_621f1b5510fa9dab8557b.png!small?1646205781573)

加固验证：

新建C:\Windows\test目录

将exe拷贝至C:\Windows\test目录

双击打开Notepad.exe，选择"文件"-"打开"找到目录"C:\Windows\test\"。

在打开窗口目录下右键重命名文件"123.exe"

![1646205823_621f1b7f00a74bbb6a9eb.png!small?1646205827589](https://image.3001.net/images/20220302/1646205823_621f1b7f00a74bbb6a9eb.png!small?1646205827589)

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯。

观察Web管理端-入侵检测-安全日志。

 **h.防止对外服务进程创建危险扩展名文件**

加固方法：

Windows Server服务器安装Agent端，PC管理端开启系统防护-操作系统加固-对外服务进程创建危险扩展名文件

![1646205955_621f1c0314232ee42c94e.png!small?1646205956048](https://image.3001.net/images/20220302/1646205955_621f1c0314232ee42c94e.png!small?1646205956048)

确保开启以下防护开关

![1646205972_621f1c14eef17658a3cca.png!small?1646205976205](https://image.3001.net/images/20220302/1646205972_621f1c14eef17658a3cca.png!small?1646205976205)

将高级防护中小开关全部关闭

![1646205990_621f1c26331fa40f3b84b.png!small?1646205994088](https://image.3001.net/images/20220302/1646205990_621f1c26331fa40f3b84b.png!small?1646205994088)

加固验证：

访问目标服务器地址，例如[
_http://192.168.8.22:8080/newShell_](http://192.168.8.22:8080/newShell)网站。选择55aa.vbs文件，并点击上传

![1646206037_621f1c5565283bc3107e1.png!small?1646206038449](https://image.3001.net/images/20220302/1646206037_621f1c5565283bc3107e1.png!small?1646206038449)

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-安全日志。

 **i.防止对外服务进程执行非正常扩展名执行文件**

加固方法:

Windows Server服务器安装Agent端，PC管理端开启系统防护-操作系统加固-对外服务进程执行非正常扩展名执行文件。

![1646206124_621f1cac932e97a68cb86.png!small?1646206125389](https://image.3001.net/images/20220302/1646206124_621f1cac932e97a68cb86.png!small?1646206125389)

确保开启以下防护开关

![1646206144_621f1cc0cc4ba5c1af1f6.png!small?1646206147472](https://image.3001.net/images/20220302/1646206144_621f1cc0cc4ba5c1af1f6.png!small?1646206147472)

将高级防护中小开关全部关闭

![1646206420_621f1dd45389e5c4881a9.png!small?1646206424331](https://image.3001.net/images/20220302/1646206420_621f1dd45389e5c4881a9.png!small?1646206424331)

加固验证:

将exe重命名为1.jpg后放在C:\xampp\tomcat\webapps\newShell目录下

![1646206457_621f1df9280053b67dbbd.png!small?1646206458994](https://image.3001.net/images/20220302/1646206457_621f1df9280053b67dbbd.png!small?1646206458994)

访问服务器地址：http://192.168.8.22:8080/newShell/hello.jsp网站,点击Execute
Command功能，输入C:/xampp/tomcat/webapps/newShell/1.jpg，点击Execute。

![1646206497_621f1e21c6bca027daecf.png!small?1646206498997](https://image.3001.net/images/20220302/1646206497_621f1e21c6bca027daecf.png!small?1646206498997)

观察Agent端拦截情况。

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯。

观察Web管理端-入侵检测-安全日志。

 **j.禁止粘连键命令被篡改**

加固方法：

准备程序：exe

Windows Server服务器安装Agent端，PC管理端开启系统防护粘连键命令被篡改

备份文件："C:\Windows\System32\sethc.exe"86系统 x64系统

备份文件："C:\Windows\SysWOW64\sethc.exe" x64系统

![1646206911_621f1fbf65f1ea4473f06.png!small?1646206911765](https://image.3001.net/images/20220302/1646206911_621f1fbf65f1ea4473f06.png!small?1646206911765)

加固验证：

修改文件所有者和权限

"sethc.exe"文件属性-安全-高级-所有者-编辑修改administrator-确定

![1646206968_621f1ff8632e8787d3161.png!small?1646206971143](https://image.3001.net/images/20220302/1646206968_621f1ff8632e8787d3161.png!small?1646206971143)

![1646206977_621f2001506f570d9b2c4.png!small?1646206980776](https://image.3001.net/images/20220302/1646206977_621f2001506f570d9b2c4.png!small?1646206980776)

"sethc.exe"文件属性-安全-编辑-administrator完全控制-确定

![1646206998_621f2016111b3f1e4dfa7.png!small?1646207001633](https://image.3001.net/images/20220302/1646206998_621f2016111b3f1e4dfa7.png!small?1646207001633)

将exe重命名为sethc.exe”

替换"C:\Windows\System32\sethc.exe" & "C:\Windows\SysWOW64\sethc.exe"

快速摁下shift五次观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯。

观察Web管理端-入侵检测-安全日志。

 **k.禁止加载无数字签名驱动**

加固方法;

准备程序：PCHunter64.exe

Windows Server服务器安装Agent端，PC管理端开启系统防护-禁止加载无数字签名驱动

![1646207188_621f20d40e0b248d2f1c4.png!small?1646207189446](https://image.3001.net/images/20220302/1646207188_621f20d40e0b248d2f1c4.png!small?1646207189446)

加固验证:

双击使用exe，产生一个持续变换名称的系统文件，等待消失即可。

![1646207242_621f210a2981634dd087c.png!small?1646207245329](https://image.3001.net/images/20220302/1646207242_621f210a2981634dd087c.png!small?1646207245329)

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯。

观察Web管理端-入侵检测-安全日志。

 **l.禁止非系统进程尝试劫持系统引导过程**

加固方法:

Windows Server服务器安装Agent端，PC管理端开启系统防护-操作系统加固-非系统进程尝试劫持系统引导过程

![1646207462_621f21e60d8bb26942098.png!small?1646207462439](https://image.3001.net/images/20220302/1646207462_621f21e60d8bb26942098.png!small?1646207462439)

加固验证：

使用工具

RegWorkshopX64.exe

查找HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows
NT\CurrentVersion\Winlogon"双击字符串键值Userinit修改数据数值

![1646207596_621f226c5523f95e9a901.png!small?1646207597990](https://image.3001.net/images/20220302/1646207596_621f226c5523f95e9a901.png!small?1646207597990)

观察结果。

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯。

观察Web管理端-入侵检测-安全日志。

 **m.禁止非系统进程尝试劫持EXE执行过程**

加固方法:

Windows Server服务器安装Agent端，PC管理端开启系统防护-操作系统加固-非系统进程尝试劫持EXE执行过程

![1646207674_621f22baa118cb4518589.png!small?1646207675009](https://image.3001.net/images/20220302/1646207674_621f22baa118cb4518589.png!small?1646207675009)

加固验证：

使用工具

RegWorkshopX64.exe

查找HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows
NT\CurrentVersion\Windows项。修改AppInit_DLLs的数据为任意值。

观察修改结果。

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯。

观察Web管理端-入侵检测-安全日志。

 **n.禁止非系统进程尝试劫持自启动过程可被禁止**

加固方法：

Windows Server服务器安装Agent端，PC管理端开启系统防护-操作系统加固-非系统进程尝试劫持自启动过程可被禁止。

![1646207806_621f233e942ff2d085f54.png!small?1646207806961](https://image.3001.net/images/20220302/1646207806_621f233e942ff2d085f54.png!small?1646207806961)

加固验证:

使用工具

RegWorkshopX64.exe

新建HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\run项。新建任意字符串值。

观察修改结果。

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯。

观察Web管理端-入侵检测-安全日志。

 **o.禁止非系统进程尝试劫持自启动过程可疑**

加固方法：

Windows Server服务器安装Agent端，PC管理端开启系统防护-操作系统加固-非系统进程尝试劫持自启动过程可疑。

![1646207908_621f23a4dc5d2480a80f7.png!small?1646207909268](https://image.3001.net/images/20220302/1646207908_621f23a4dc5d2480a80f7.png!small?1646207909268)

加固验证：

使用工具

RegWorkshopX64.exe

查找HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run。新建任意字符串值。

观察修改结果。

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯。

观察Web管理端-入侵检测-安全日志。

 **p.禁止非系统进程通过组策略劫持开机程序**

加固方法：

Windows Server服务器安装Agent端，PC管理端开启系统防护-操作系统加固-非系统进程通过组策略劫持开机程序。

![1646207991_621f23f7a2ed938fbb621.png!small?1646207991959](https://image.3001.net/images/20220302/1646207991_621f23f7a2ed938fbb621.png!small?1646207991959)

加固验证:

使用工具

RegWorkshopX64.exe

新建项HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Group
Policy\Scripts\Startup\test。新建字符串值script

观察修改结果。

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯，有告警信息。

观察Web管理端-入侵检测-安全日志。

 **q.禁止非系统进程通过组策略劫持关机程序**

加固方法：

Windows Server服务器安装Agent端，PC管理端开启系统防护-操作系统加固-非系统进程通过组策略劫持关机程序。

![1646208080_621f24507acbe3919393a.png!small?1646208081175](https://image.3001.net/images/20220302/1646208080_621f24507acbe3919393a.png!small?1646208081175)

加固验证：

使用工具

RegWorkshopX64.exe

新建项HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Group
Policy\Scripts\Shutdown\test。新建字符串值script

观察修改结果。

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯，有告警信息。

观察Web管理端-入侵检测-安全日志。

 **r.禁止非系统进程修改LSP**

加固方法：

Windows Server服务器安装Agent端，PC管理端开启系统防护-操作系统加固-非系统进程修改LSP

![1646208204_621f24cc8f8adecdd0f97.png!small?1646208204925](https://image.3001.net/images/20220302/1646208204_621f24cc8f8adecdd0f97.png!small?1646208204925)

加固验证：

使用工具

RegWorkshopX64.exe

修改HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\WinSock2\Parameters\NameSpace_Catalog5\Catalog_Entries\000000000001\下的LibraryPath为任意值。

使用工具

RegWorkshopX64.exe

修改HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\WinSock2\Parameters\NameSpace_Catalog5\Catalog_Entries64\000000000001\下的LibraryPath为任意值

观察修改结果。

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-安全日志。

观察Web管理端-入侵检测-事件回溯，有告警信息。

 **s.禁止非系统进程修改MSI提权**

加固方法:

Windows Server服务器安装Agent端，PC管理端开启系统防护-操作系统加固-非系统进程修改MSI提权。

![1646208303_621f252f82fcd3e05cbca.png!small?1646208304029](https://image.3001.net/images/20220302/1646208303_621f252f82fcd3e05cbca.png!small?1646208304029)

加固验证：

使用工具

RegWorkshopX64.exe

新建项HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Installer，新建值（字符串值）”
AlwaysInstallElevated”

使用工具

RegWorkshopX64.exe

新建项HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Installer，新建值（字符串值）”
AlwaysInstallElevated”

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-安全日志。

观察Web管理端-入侵检测-事件回溯，有告警信息。

 **t.禁止非系统进程通过修改屏保程序劫持启动过程**

加固方法：

打开操系统加固项-非系统进程通过修改屏保程序劫持启动过程

开启系统屏幕保护功能（开启方式自行百度学习）

Y_CURRENT_USER\Control Panel\Desktop\SCRNSAVE.EXE”

![1646208426_621f25aa996e463271897.png!small?1646208428065](https://image.3001.net/images/20220302/1646208426_621f25aa996e463271897.png!small?1646208428065)

加固验证：

x86系统执行exe

x64系统执行exe

编辑“HKEY_CURRENT_USER\Control Panel\Desktop\SCRNSAVE.EXE”双击修改数据数值.

 **u.禁止添加用户到管理员组**

加固方法：

Windows Server服务器安装Agent端，PC管理端开启系统防护-操作系统加固-禁止添加用户到管理员组。

![1646208516_621f2604abfc2109ff57b.png!small?1646208518329](https://image.3001.net/images/20220302/1646208516_621f2604abfc2109ff57b.png!small?1646208518329)

加固验证：

使用cmd命令新建用户test：net user test /add

使用cmd命令将用户test添加到Administrators组：net localgroup administrators test /add

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯。

观察Web管理端-入侵检测-安全日志。

 **v.防止对外服务进程创建可执行文件**

加固方法:

防护开关：需确保“进程监听端口监控开关”“文件防护开关”“进程防护开关”均为开启状态

![1646208577_621f2641848e2f6f80818.png!small?1646208580484](https://image.3001.net/images/20220302/1646208577_621f2641848e2f6f80818.png!small?1646208580484)

Windows Server服务器安装Agent端，PC管理端开启系统防护-操作系统加固-对外服务进程创建可执行文件

![1646208591_621f264f92ed1a41e436f.png!small?1646208592351](https://image.3001.net/images/20220302/1646208591_621f264f92ed1a41e436f.png!small?1646208592351)

加固验证：

访问服务器地址：http://192.168.8.22:8080/hello.jsp网站。选择File Manager选择 exe文件，并点击上传。

![1646208626_621f2672bcf08cccd691b.png!small?1646208628956](https://image.3001.net/images/20220302/1646208626_621f2672bcf08cccd691b.png!small?1646208628956)

现象：上传被拦截；

观察Agent端拦截情况。

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-事件回溯。

观察Web管理端-入侵检测-安全日志

 **w.防止窃取系统内存密码**

加固方法：

Windows Server服务器安装Agent端，PC管理端开启系统防护-操作系统加固-防止窃取系统内存密码

![1646208711_621f26c7f102786bd3778.png!small?1646208713011](https://image.3001.net/images/20220302/1646208711_621f26c7f102786bd3778.png!small?1646208713011)

加固验证：

  1. 打开

RegWorkshopX64.exe

工具

![1646208745_621f26e989dcfe640702d.png!small?1646208747121](https://image.3001.net/images/20220302/1646208745_621f26e989dcfe640702d.png!small?1646208747121)

在HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa\ 中找到Notification
Packages和 Security Packages并修改键值对为任意值

![1646208763_621f26fb2c07056c30b09.png!small?1646208764680](https://image.3001.net/images/20220302/1646208763_621f26fb2c07056c30b09.png!small?1646208764680)

观察Agent端拦截情况

观察PC管理端-日志查询-系统防护日志。

观察Web管理端-入侵检测-安全日志

## 内核加固技术作用

服务器内核加固技术主要加强操作系统自身对抗恶意代码和黑客攻击的能力，抵御非法提权、非法创建可执行文件等黑客行为。就算黑客通过后门成功进行到系统，但他啥也干不了，不能提权不能新建可执行程序，不能新建用户，甚至连开关机都做不到，那么他之前的渗透等于没有效果。

