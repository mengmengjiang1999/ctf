# 概述

  

“Ghost”盗版系统和系统激活工具一直都是国内病毒传播的重要渠道之一，尤其以Rootkit/Bootkit类型的顽固病毒居多，此类病毒安装普遍早于安全软件，大多会通过内核层来隐藏保护自身模块，并凭借植入时机的先手优势和安全杀软进行深层对抗。近期通过“捕风”威胁感知系统监控，我们发现“贪狼”Rootkit僵尸家族在近2个月开始再次活跃，“贪狼”病毒一直都是盗版系统预装渠道中的活跃家族，早期变种可以追溯到2015年，起初主要用于主页劫持和流量暗刷，从我们的监控记录看，“贪狼”基本上每年都会有一次较大的活跃更新，在17年初曾被安全友商命名为“狼人杀”并分析曝光，短暂潜伏以后在17年9月份又出现过小幅更新，今年6月份开始“贪狼”家族开始再度活跃，除了Http(s)劫持模块不断加强外，开始顺应黑产潮流加入“门罗币”挖矿功能模块，并且在6月4号开始通过更新渠道下发“Hydra”DDOS木马插件，“贪狼”僵尸网络的威胁度和攻击性正在不断加强。

# 正文

  

“贪狼”Rootkit病毒主要通过ghost系统等渠道感染用户计算机，通过多种方式隐藏自身、对抗杀软，同时模块众多，功能灵活复杂。不同模块分别实现浏览器劫持、ddos攻击、加密货币挖矿、刷量等功能。根据检测到的感染量估算全国超过50万机器遭到感染。

**模块名** |  **主要功能**  
---|---  
Platform.dll  |  功能模块更新、加载等  
ConsoleApplication8.dll  |  门罗币挖矿  
HydraClient.dll  |  DDOS攻击  
StevenRobot.dll  |  上报、下拉配置  
mLoader.dll  |  插件加载器  
UserFramework.dll  |  插件核心框架、  
KernelManager.dll  |  插件管理  
HSManager.dll  |  主页劫持  
WebBrowser.dll  |  后台广告刷量  
AppManage64.dll  |  浏览器劫持  
SSLHijack1.0.6-win64.dll  |  HTTPS劫持  
Hijack.dll  |  浏览器劫持  
KernelHijack.sys  |  内核劫持模块  
  
各模块通过联网下载到本地执行，被RC4或AES加密；且都有统一的导出名称BsProcessStartup、BsDllStartup、BsCleanup、BsEnvironment；

![1.png](https://image.3001.net/images/20180727/1532658072_5b5a8198418a8.png!small)  

模块被注入到目标进程后直接调用BsProcessStartup或BsDllStartup；BsProcessStartup和BsDllStartup首先确定加载基址，并获取peb、teb相关信息初始化导出结构体BsEnvironment，然后进行重定位修复、导入表初始化、CRT初始化、添加异常处理表等前置工作，最后进入主功能函数。

模块自加载，自初始化流程：

![2.png](https://image.3001.net/images/20180727/1532658104_5b5a81b8d5fdd.png!small)![3.png](https://image.3001.net/images/20180727/1532658116_5b5a81c4da661.png!small)  

由于模块众多，下面简单分析其中几个模块的主要行为。

# 核心驱动模块

  

1、驱动加了VMP壳保护，加载后注册进程回调、映像回调、注册表回调、关机回调，并创建3个内核线程；

2、通过进程回调APC注入内置Platform.dll到lsass.exe，Platform.dll执行真正的病毒行为；

3、映像回调拦截浏览器进程的杀软模块加载；

4、注册表回调保护自身驱动服务项；

5、关机回调回写自身驱动文件和注册表服务项；

![4.png](https://image.3001.net/images/20180727/1532658169_5b5a81f9267dc.png!small)  

# R3层核心框架Platform.dll

  

该模块是驱动内置的模块，核心功能是加载挖矿模块和下载配置文件并更新其他模块；

1、加载内置的ConsoleApplication8.dll（挖矿模块）；

2、挂钩NtQuerySystemInformation（针对taskmgr.exe，进程名过滤）；

3、挂钩LdrLoadDll（针对360se.exe、360chrome.exe），过滤杀软的浏览器保护模块；

![5.png](https://image.3001.net/images/20180727/1532658190_5b5a820e9b6c9.png!small)  

4、访问C&C服务器，内置多个备用服务器地址；上传机器信息并下载配置文件，hxxps://client.115ww.com/api/_mv_bamboo.html?REV=0&RC=0&PID=3&CID=0&UID=0&VER=0&RM=&DMJ=0&DMN=0&DBL=0&UMJ=0&UMN=0&UBL=0&MID=&BW=64&NTMJ=6&NTMN=1&NTBL=7601&NTSPMJ=1&NTSPMN=0&NP=1&MM=2146951168&OSTC=1843198&SVSN=C6BDE606&SVFS=NTFS；

![6.png](https://image.3001.net/images/20180727/1532658213_5b5a822506185.png!small)  

配置文件解密后如下：

![7.png](https://image.3001.net/images/20180727/1532658231_5b5a82372a442.png!small)  

5、根据配置文件进一步下载其他模块并加载执行；

# 内嵌“门罗币”挖矿模块ConsoleApplication8.dll

  

pdb路径：L:\github\ConsoleApplication8\x64\Release\ConsoleApplication8.pdb

1、 ConsoleApplication8.dll内置一个zip文件，包含config.json、start.cmd、xmrig.exe；

2、
查询注册表[HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\KingsoftInternet
Security]的值“UninstallString”，成功则直接返回，不进行挖矿；

![8.png](https://image.3001.net/images/20180727/1532658255_5b5a824f0c374.png!small)  

3、 解压zip文件并加载挖矿模块进行挖矿；

4、 挖矿钱包和矿池地址如下：

![9.png](https://image.3001.net/images/20180727/1532658273_5b5a826182041.png!small)

# 浏览器劫持模块AppManage.dll

  

pdb路径：E:\Code\Ivipm\source\AppManger\AppManger\x64\Release\AppManage.pdb

通过APC方式被注入到进程，如果进程是360se.exe、360chrome.exe，则查找并删除文件sesafe.dll；

![10.png](https://image.3001.net/images/20180727/1532658298_5b5a827acc60a.png!small)  

如果进程是以下杀软进程，则查找并删除文件QMProtect.dll、QMProtect64.dll、QMIESafeDll.dll、QMIESafeDll64.dll；如果进程名包含qqpc则直接退出进程。

![11.png](https://image.3001.net/images/20180727/1532658328_5b5a8298ceb5f.png!small)

![12.png](https://image.3001.net/images/20180727/1532658347_5b5a82abd20ab.png!small)  

如果进程是explorer.exe，则挂钩CreateProcessInternalW、RtlCreateProcessParameters、ZwCreateUserProcess、RtlCreateProcessParametersEx，对以下浏览器进程的命令行参数进行劫持；

![13.png](https://image.3001.net/images/20180727/1532658366_5b5a82bee537e.png!small)

![14.png](https://image.3001.net/images/20180727/1532658388_5b5a82d48c73a.png!small)  

同时还会向系统添加根证书，用于https劫持：

![15.png](https://image.3001.net/images/20180727/1532658407_5b5a82e7ec50d.png!small)

# DDOS攻击插件HydraClient.dll

  

pdb路径：C:\Users\Lon\source\repos\DDos\x64\Release\HydraClient.pdb

该模块通过APC方式被注入到进程wuauclt.exe，是DDOS攻击模块；CC地址为115.231.219.32；支持常见的DDOS攻击方式。

![16.png](https://image.3001.net/images/20180727/1532658430_5b5a82fe39099.png!small)

![17.png](https://image.3001.net/images/20180727/1532658464_5b5a8320c794a.png!small)

![18.png](https://image.3001.net/images/20180727/1532658478_5b5a832e4be56.png!small)  
  

# 附录IOC:

  

 **MD5** **：**

2ECEE431A394538DD8B451B147D684AD

**IP** **：**

115.231.219.32

**URL** **：**

hxxps://down.135h.com/save/chilli/DwYQ0YY0x6.jpg

hxxps://down.135h.com/save/chilli/CUYQ0YY0x6.jpg

hxxp://ix.135gg.com/api/_mcv_chillis.html

hxxp://client.135gg.com/api/_msv_software.html

hxxp://client.115ww.com/api/_mv_bamboo.html

hxxp://client.335dh.com/api/_mv_bamboo.html

hxxp://client.115ll.com/api/_mv_bamboo.html

**DOMAIN** **：**

ix2.135gg.com

ix.135gg.com

ixs.115rr.com

lps.115rr.com

ixs.135h.com

50star.com

tj.16610.com

pp.fatdit.com

[www.faafox.com](http://www.faafox.com)

ix.faafox.com

client.faafox.com

aoyouw.cftmon.com

osipad.fatdit.com

bs.xobvb.com

bs.unaout.com

gang[1|2|3|5|6].info

