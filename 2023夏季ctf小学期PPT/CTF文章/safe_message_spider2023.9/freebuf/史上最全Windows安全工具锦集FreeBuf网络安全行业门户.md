**“工欲善其事，必先利其器。”**

**近日，深信服安全团队整理了一些常见的PE工具、调试反汇编工具、应急工具、流量分析工具和WebShell查杀工具，希望可以帮助到一些安全行业的初学者。**

## PE工具篇

### PEiD

一款著名的PE侦壳工具，可以检测PE常见的一些壳，但是目前已经无法从官网获得：

![](https://image.3001.net/images/20190929/1569728934_5d9029a618a81.png!small)

### EXEInfoPE

PE侦壳工具，PEiD的加强版，可以查看EXE/DLL文件编译器信息、是否加壳、入口点地址、输出表/输入表等等PE信息：

![](https://image.3001.net/images/20190929/1569728938_5d9029aaa3168.png!small)

下载地址：<http://www.exeinfo.xn.pl/>

### DetectIt Easy

开源的PE侦壳工具，是一个跨平台的应用程序，有Windows、Linux、Mac OS多个可用版本：

![](https://image.3001.net/images/20190929/1569728942_5d9029ae57e0b.png!small)

下载地址：<http://ntinfo.biz/index.html>

### CFFExplorer

一款优秀的PE32 &PE64编辑工具，可以方便的查看及编辑PE文件。完全支持.NET文件格式：

![](https://image.3001.net/images/20190929/1569728949_5d9029b53a0af.png!small)

下载地址：<https://ntcore.com/?page_id=388>

### StudyPE

PE32 & PE64 查看分析集成工具，具有强大的PE结构处理分析功能，在查壳方面功能略显薄弱：

![](https://image.3001.net/images/20190929/1569728959_5d9029bf2eb23.png!small)

下载地址：<https://bbs.pediy.com/thread-246459-1.htm>

## 调试/反编译工具篇

### OllyDbg

Ring3级调试器，支持插件扩展功能，唯一不足的是OD是一个32位调试器，不支持调试64位程序。官方给出的原版程序是无插件的，有需要的童鞋可以在吾爱破解论坛自行搜索：

![](https://image.3001.net/images/20190929/1569728986_5d9029dac9c6e.png!small)

下载地址：<http://www.ollydbg.de/>

### WinDbg

支持Windows平台，用户态和内核态的调试器，有图形界面和命令行两种调试方式。其强大的内核调试功能收获了众多的追捧者：

![](https://image.3001.net/images/20190929/1569729012_5d9029f43e1f6.png!small)

下载地址：<https://docs.microsoft.com/zh-cn/windows-hardware/drivers/debugger/debugger-download-tools>

### x32dbg/x64dbg

一款开源的调试器，从界面和操作使用和OD相似，支持32位和64位应用程序的调试。解决了OD对64位应用程序调试上的缺陷：

![](https://image.3001.net/images/20190929/1569729019_5d9029fbe4916.png!small)

下载地址：<https://x64dbg.com/#start>

### dnSpy

一款针对.NET程序的开源逆向程序的工具。包含了反汇编器，调试器和汇编编辑器等功能组件，支持插件功能：

![](https://image.3001.net/images/20190929/1569729025_5d902a012d1a6.png!small)

下载地址：<https://github.com/0xd4d/dnSpy>

### IDAPro

全称：InteractiveDisassembler Professional，交互式反汇编器专业版，目前最棒的静态反编译工具，是众多安全人士的首选：

![](https://image.3001.net/images/20190929/1569729032_5d902a08e3fda.png!small)

下载地址：<https://www.hex-rays.com/products/ida/>

### VB Decompiler

针对Visual Basic 5.0/6.0开发的程序的反编译器：

![](https://image.3001.net/images/20190929/1569729047_5d902a177f42d.png!small)

下载地址：<https://www.vb-decompiler.org/products/cn.htm>

## 应急工具篇

 **日志相关**

### Sysmon

WindowsSysinternals出品的一款Sysinternals系列中的工具。它以系统服务和设备驱动程序的方法安装在系统上，并保持常驻性。用来监视和记录系统活动，并记录到windows事件日志，可以提供有关进程创建，网络链接和文件创建时间更改的详细信息：

![](https://image.3001.net/images/20190929/1569729069_5d902a2ddfbe7.png!small)

下载地址：<https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon>

### LastActivityView

是一款电脑操作记录查看器，直接调用系统日志，显示安装软件、系统启动、关机、网络连接、执行exe 的发生时间和路径：

![](https://image.3001.net/images/20190929/1569729093_5d902a453a4f0.png!small)

下载地址：<http://www.nirsoft.net/utils/computer_activity_view.html>

 **注册表相关**

### Regshot

注册表比较工具，通过抓取两次注册表快速比较得出两次注册表的不同之处：

![](https://image.3001.net/images/20190929/1569729101_5d902a4d1832d.png!small)

下载地址：<https://sourceforge.net/projects/regshot/>

### Autoruns

基于Windows平台的自动运行程序的管理工具。可以控制登录时的加载程序、驱动程序加载、服务启动、任务计划等 Windows 中各种方面的启动项：

![](https://image.3001.net/images/20190929/1569729105_5d902a51960dc.png!small)

下载地址：<https://docs.microsoft.com/en-us/sysinternals/downloads/autoruns>

 **进程相关**

### ProcessHacker

一款功能丰富的开源系统进程辅助工具，可以方便的查看进程的运行情况、内存以及模块信息，还可以对进程进行管理：

![](https://image.3001.net/images/20190929/1569729111_5d902a5757c12.png!small)

下载地址：[https://processhacker.sourceforge.io/](https://www.jishuwen.com/jump/aHR0cHM6Ly9wc**jZXNzaGFja2VyLnNvdXJjZWZvcmdlLmlvLw==)

### PowerTool

一款免费的进程管理器，可以Unlock占用文件的进程，查看文件或文件夹被占用的情况，内核模块和驱动的查看管理，进程模块的内存dump等工具：

![](https://image.3001.net/images/20190929/1569729120_5d902a6073af3.png!small)

下载地址：<https://www.portablesoft.org/>

### ProcessLasso

一款独特的调试进程级别的系统优化工具，主要功能是基于其特别的算法动态调整各个进程优先级以实现为系统减负的目的。可以用来监视进程动作：

![](https://image.3001.net/images/20190929/1569729126_5d902a66c19b7.png!small)

下载地址：<https://bitsum.com/>

 **文件相关**

### HashTab

文件校验工具，分为免费个人版以及付费版。下载安装后可以通过查看文件属性中的HashTab快速得到文件的哈希值，支持多种哈希算法：

![](https://image.3001.net/images/20190929/1569729136_5d902a700a273.png!small)

下载地址：<http://implbits.com/products/hashtab/>

### HashChecker

一款开源的文件校验工具，安装完成后可以通过文件属性中的文件校验快速得到文件的哈希值。支持右键菜单创建校验文件功能和批量校验功能：

![](https://image.3001.net/images/20190929/1569729153_5d902a811190c.png!small)

下载地址：<http://code.kliu.org/hashcheck/>

### Unlocker

一款右键扩充工具，通过删除文件和程序关联的方式解除文件的占用。在解除占用时不会强制关闭占用文件进程：

![](https://image.3001.net/images/20190929/1569729160_5d902a880ad79.png!small)

下载地址：<http://emptyloop.com/unlocker/>

### Everything

强大的Windows桌面搜索引擎，可以在NTFS卷上快速的根据名称查找文件和目录：

![](https://image.3001.net/images/20190929/1569729168_5d902a90a719d.png!small)

下载地址：<https://www.voidtools.com/zh-cn/>

### Winhex

是一款优秀的十六进制编辑器，在计算机取证，数据恢复，低级数据处理和IT安全领域非常有用：

![](https://image.3001.net/images/20190929/1569729188_5d902aa4f1954.png!small)

下载地址：<https://www.x-ways.net/winhex/>

### BinDiff

一款开源的二进制文件对比工具，可帮助安全人员快速发现反汇编代码中的差异和相似之处。支持x86、MIPS、ARM/AArch64、PowerPC等架构进行二进制文件的对比：

![](https://image.3001.net/images/20190929/1569729201_5d902ab140df9.png!small)

下载地址：<https://www.zynamics.com/software.html>

### BeyondCompare

一款由ScooterSoftware推出的文件比较工具。主要用于比较两个文件夹或者文件并将差异以颜色标记，比较的范围包括目录，文档内容等：

![](https://image.3001.net/images/20190929/1569729211_5d902abbe3cbf.png!small)

下载地址：<http://www.beyondcompare.cc/xiazai.html>

 **内存相关**

### SfAntiBotPro

内存检索工具，可以根据输入的字符串快速检索计算机内存，输出包含该字符串的进程信息，在进行恶意域名检测时有事半功倍的效果：

![](https://image.3001.net/images/20190929/1569729223_5d902ac7ab6fb.png!small)

下载地址：

（32位）<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

（64位）<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>

### DumpIt

是一款免安装的Windows内存镜像取证工具，可以使用其轻松的将一个系统的完整内存镜像下来，并用于后续的调查取证工作：

![](https://image.3001.net/images/20190929/1569729229_5d902acd396e6.png!small)

下载地址：<https://my.comae.com/tools>

 **设备监控**

### USBLogView

一款USB设备监控软件，后台运行，可以记录插入或拔出系统的任何USB的详情信息：

![](https://image.3001.net/images/20190929/1569729240_5d902ad864008.png!small)

下载地址：<https://www.nirsoft.net/utils/usb_log_view.html>

 **集成工具**

### PC Hunter

一款驱动级的系统维护工具，能够查看各种Windows的各类底层系统信息，包括进程、驱动模块、内核、内核钩子、应用层钩子，网络、注册表、文件、启动项、系统杂项、电脑体检等：

![](https://image.3001.net/images/20190929/1569729253_5d902ae599816.png!small)

下载地址：<http://www.xuetr.com/>

### MalwareDefender

一款 HIPS
(主机入侵防御系统)软件，用户可以自己编写规则来防范病毒、木马的侵害。另外，MalwareDefender提供了很多有效的工具来检测和删除已经安装在您的计算机系统中的恶意软件：

![](https://image.3001.net/images/20190929/1569729274_5d902afaee6d4.png!small)

下载地址：<https://labs.360.cn/malwaredefender/>

### 火绒剑

一款用于分析、处理恶意程序的安全工具软件，提供了“程序行为监控”、“进程管理”、“文件管理”、“注册表管理”、“系统启动项管理”、”内核程序管理“、“代码钩子扫描”七大功能：

![](https://image.3001.net/images/20190929/1569729279_5d902affc47a7.png!small)

下载地址：

（火绒剑独立版，不支持win8.1以上的系统）down4.huorong.cn/hrsword.exe

## 流量分析工具篇

### WireShark

一款网络封包分析工具，可以帮助用户深入分析网络协议，涵盖上百种协议以及各类主要平台。通过GUI或TTY-mode浏览数据：

![](https://image.3001.net/images/20190929/1569729291_5d902b0bc1e66.png!small)

下载地址：wireshark.org/download.html

### Fiddler

C#编写的http抓包改包工具，相较wireshark更加轻量级，在http和https数据包的抓取上更加专业。还能设置断点，修改请求和响应的数据，模拟弱网络环境。支持插件扩展:

![](https://image.3001.net/images/20190929/1569729300_5d902b14e5bf6.png!small)

下载地址：<https://www.telerik.com/download/fiddler>

### MicrosoftNetwork Monitor

只支持Windows平台的网络数据分析工具，提供了一个专业的网路实时流量图形界面，拥有识别和监控超过300种网络协议的能力：

下载地址：<https://www.microsoft.com/en-us/download/details.aspx?id=4865>

### CapsaPacket Sniffer

网络分析工具，用于网络监控、故障排除和网络诊断等功能：

![](https://image.3001.net/images/20190929/1569729369_5d902b5936415.png!small)

下载地址：<https://www.colasoft.com/capsa-free/>

### NetworkMiner

支持Windows平台的网络取证分析工具，通过嗅探或者分析PCAP文件可以侦测到操作系统，主机名和开放的网络端口主机：

![](https://image.3001.net/images/20190929/1569729376_5d902b601a65a.png!small)

下载地址：<https://sourceforge.net/projects/networkminer/files/networkminer/>

### AngryIP Scanner

这是一款开源的网络扫描仪，支持Linux，Windows和Mac OS
X平台，可以在最短的时间内扫描远端主机IP运作情况，包括主机名，目前开放的端口和IP的运作情况：

![](https://image.3001.net/images/20190929/1569729381_5d902b65da6c8.png!small)

下载地址：[https://angryip.org](https://angryip.org/)

## WebShell查杀工具篇

### D盾

D盾是一个专为IIS设计的主动防御保护软件，有一句话免疫，主动后门拦截，SESSION保护，防WEB嗅探，防CC，防篡改，注入防御，防XSS，防提权，上传防御，未知0day防御，异形脚本防御等功能，以内外保护的方式防止网站和服务器被入侵。

![](https://image.3001.net/images/20190929/1569729398_5d902b76cc523.png!small)

下载地址：<http://www.d99net.net/>

### WebShellKiller

WebShellKiller是个Web后门专杀工具，不仅支持Webshell扫描，还支持暗链扫描。该工具将传统的技术与人工智能技术相结合、静态扫描和动态分析相结合，更精准的检测出Web网站已知和未知的后门文件：

![](https://image.3001.net/images/20190929/1569729447_5d902ba7ac926.png!small)

下载地址：

（Windows平台）<https://edr.sangfor.com.cn/tool/WebShellKillerTool.zip>

（Linux平台）<http://edr.sangfor.com.cn/api/download/WebShellKillerForLinux.tar.gz>

### WEBDIR+

在线WebShell扫描器：

![](https://image.3001.net/images/20190929/1569729452_5d902bac67c91.png!small)

链接地址：<https://scanner.baidu.com/#/pages/intro>

### WebShellDetector

在线WebShell扫描器：

![](https://image.3001.net/images/20190929/1569729456_5d902bb03355c.png!small)

链接地址：[http://www.shelldetector.com](http://www.shelldetector.com/)

### WEBSHELL.PUB

在线WebShell扫描器：

![](https://image.3001.net/images/20190929/1569729460_5d902bb447161.png!small)

下载链接：[http://www.shellpub.com](http://www.shellpub.com/)

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

