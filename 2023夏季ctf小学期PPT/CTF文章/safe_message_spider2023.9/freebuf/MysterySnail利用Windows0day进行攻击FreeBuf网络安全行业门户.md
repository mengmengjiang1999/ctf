2021年8月底，研究人员在多台Windows服务器上检测到提权攻击。漏洞利用中存在许多CVE-2016-3309的调试字符串，但深入分析表明这是一个0Day漏洞。它利用了Win32k驱动程序中的未知漏洞，该漏洞严重依赖于内核模块基址泄露技术。Microsoft于2021年10月12日进行了修补，漏洞分配编号CVE-2021-40449。除了在野外发现0Day之外，研究人员还分析了与零日攻击一起使用的恶意软件，通过C2服务器将这一系列攻击活动归属于“MysterySnail”。

##  **提权攻击分析**

发现的攻击针对以下版本：

Microsoft Windows Vista

Microsoft Windows 7

Microsoft Windows 8

Microsoft Windows 8.1

Microsoft Windows Server 2008

Microsoft Windows Server 2008 R2

Microsoft Windows Server 2012

Microsoft Windows Server 2012 R2

Microsoft Windows 10 (build 14393)

Microsoft Windows Server 2016 (build 14393)

Microsoft Windows 10 (build 17763)

Microsoft Windows Server 2019 (build 17763)

可见漏洞攻击是以提升服务器权限为目的开发的。CVE-2021-40449是Win32k NtGdiResetDC函数中的use-after-free漏洞。

##  **MysterySnail RAT** **分析**

MysterySnail RAT通过提升权限漏洞执行，它由OpenSSL库静态编译，样本大小为8.29MB，其中包含该库未使用代码和数据。

![1634746400_6170402087eedaa37e53a.png!small?1634746393961](https://image.3001.net/images/20211021/1634746400_6170402087eedaa37e53a.png!small?1634746393961)

反分析随机字符串

它使用了两个非常大的函数来规避检测，但实际运行中只调用了其中的一个，实际的业务逻辑从“GetInfo”开始执行。

![1634746413_6170402d46fa2aca40977.png!small?1634746406418](https://image.3001.net/images/20211021/1634746413_6170402d46fa2aca40977.png!small?1634746406418)

导出函数的名称

样本中有两个硬编码URL—“www.disktest.com”和“www.runblerx.com”，但未被使用；实际C2地址为“http.ddspadus.com”。

恶意软件枚举“Software\Microsoft\Windows\CurrentVersion\Internet
Settings\ProxyServer”注册表项下的值，在代理服务器无法直接连接C2时使用这些值通过代理服务器进行隧道传输。其命令格式如下，所有通信都使用SSL加密。

Offset

|

Description  
  
---|---  
  
0

|

Size of additional data  
  
4

|

Session ID  
  
8

|

Command ID  
  
0xC

|

Additional data  
  
在收到命令前，恶意软件会收集并发送受害PC的机器名、当前OEM代码页、windows版本、IP地址、当前用户等。恶意软件命令如下表：

Command ID

|

Description  
  
---|---  
  
1F4h

|

启用cmd.exe shell  
  
1F5h

|

创建新进程  
  
1F6h

|

创建新进程（console）  
  
1F7h

|

获取硬盘信息  
  
1F8h

|

上传文件  
  
1FAh

|

获取目录  
  
1FBh

|

杀死进程  
  
1FFh

|

删除文件  
  
202h

|

读取文件  
  
205h

|

重连  
  
208h

|

设置睡眠时间  
  
209h

|

关闭网络连接并退出  
  
20Ah

|

退出  
  
20Bh

|

杀掉shell  
  
20Ch

|

终止读取文件  
  
217h

|

无操作  
  
21Bh

|

利用代理连接  
  
21Ch

|

利用代理发送数据  
  
21Eh

|

关闭所有代理  
  
21Fh

|

关闭特定代理  
  
研究人员发现‘MysterySnail’与‘IronHusky’具有较高的同源性，并且重复使用了C2地址，其攻击可追溯到2012年。检测到的CVE-2021-40449漏洞攻击和相关恶意软件如下：

PDM:Exploit.Win32.Generic

PDM:Trojan.Win32.Generic

Trojan.Win64.Agent*

##  **IoCs**

www.disktest.com

www.runblerx.com

http.ddspadus.com

MD5 e2f2d2832da0facbd716d6ad298073ca

SHA1 ecdec44d3ce31532d9831b139ea04bf48cde9090

SHA256 b7fb3623e31fb36fc3d3a4d99829e42910cad4da4fa7429a2d99a838e004366e

## 原文链接

[securelist](https://securelist.com/mysterysnail-attacks-with-windows-zero-day/104509/)

  

