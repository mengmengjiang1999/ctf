**“紫狐”木马最早出现于2018年3月，通过与游戏外挂、第三方安装程序捆绑传播，该木马如同其名字一样具有狐狸般的狡猾，应用了极强的反检测能力，除了功能DLL文件加强壳外，还会通过加载驱动的方式进行隐藏，并且利用PendingFileRenameOperations实现延时删除，注入系统进程以躲避检测。**

近日，深信服安全团队监测到“紫狐”木马再次升级，在原有的“反侦察”能力上，新增了 **“永恒之蓝”漏洞利用** 功能和 **1** **433**
**端口扫描爆破** 功能，一旦感染便迅速蔓延内网，并不断对外网发起攻击。通过深信服安全感知平台报警提示多个安全事件，包含大量横向传播的恶意行为：

![](https://image.3001.net/images/20191101/1572591423_5dbbd73f26532.png!small)由深信服安全云脑对此次捕获到的相关域名进行统计，各省份均存在“紫狐”木马感染情况，推测原因是由于其利用了软件捆绑的方式进行传播，因此，下载运行不明来源安装程序的用户极易遭到感染：

![](https://image.3001.net/images/20191101/1572591545_5dbbd7b91141f.png!small)通过分析关联，“紫狐”木马母体的最新下载链接使用了域名bk.xdzxxf.xyz，而下载的文件一直在不断变化：

![](https://image.3001.net/images/20191101/1572591560_5dbbd7c89814a.png!small)木马母体为一个msi文件，通过解压可以看到其中包含了三个文件，分别是：

> x86下的dll文件winupdate32.log
>
> x64下的dll文件winupdate64.log
>
> 加密的PE文件sysupdate.log

**![](https://image.3001.net/images/20191101/1572592019_5dbbd993ab70a.png!small)**其中，两个DLL文件都加了VMP壳，成功运行后会删除母体和运行过程中的各个跳板进程，以躲避追踪检测，最终只残留驱动隐藏的DLL文件通过PendingFileRenameOperations实现延时删除。

##  **感染现象**

感染“紫狐”木马的主机会存在一个独立的svchost.exe进程，不断外连1433端口和445端口：

![](https://image.3001.net/images/20191101/1572592301_5dbbdaad5b85b.png!small)使用工具搜索*.dll，按修改时间降序，可以搜索到C:\Windows\System32目录下名为MsxxxxxxxxApp.dll的文件（中间“xxxxxxxx”为随机数字）：

![](https://image.3001.net/images/20191101/1572592322_5dbbdac23fcb7.png!small)使用cmd命令fltmc可以看到加载了一个驱动“dump_xxxxxxxx”（其中”
xxxxxxxx”为随机字符）：

![](https://image.3001.net/images/20191101/1572592401_5dbbdb11356bd.png!small)

##  **清除病毒**

1\. 进入安全模式；

2\. 删除文件MsxxxxxxApp.dll；

3\.
在注册表HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SessionManager\PendingFileRenameOperations中删除C:\Windows\System32\MsxxxxxxApp.dll；

![](https://image.3001.net/images/20191101/1572592441_5dbbdb392c0d5.png!small)4\.
删除注册表HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows
NT\CurrentVersion\Svchost的netsvcs值中删除MsxxxxxxApp相关值；

![](https://image.3001.net/images/20191101/1572592520_5dbbdb880611a.png!small)

##  **病毒防御**

1\. 深信服EDR产品、下一代防火墙及安全感知平台等安全产品均具备病毒检测能力，部署相关产品用户可进行病毒防御，如图所示：

![](https://image.3001.net/images/20191101/1572592646_5dbbdc06d2c4d.png!small)

2\. 主机打上“永恒之蓝”漏洞补丁；

3\. 不要下载来路不明的软件、不使用非法外挂软件；

4\. 数据库使用强密码，避免使用统一的密码；

5.使用深信服安全产品，接入安全云脑，使用云查服务可以即时检测防御新威胁；

6.深信服推出安全运营服务，通过以“人机共智”的服务模式帮助用户快速扩展安全能力，针对此类威胁安全运营服务提供设备安全设备策略检查、安全威胁检查、相关漏洞检查等服务，确保第一时间检测风险以及更新策略，防范此类威胁。

##  **IOC**

**域名：** ****

> bk.xdzxxf.xyz

**URL:**

> <http://bk.xdzxxf.xyz/smb1.jpg>
>
> <http://bk.xdzxxf.xyz/Sekf.Png>
>
> <http://bk.xdzxxf.xyz/sekf.png>
>
> <http://bk.xdzxxf.xyz/sqlexec/sps.jpg>
>
> <http://bk.xdzxxf.xyz/SMB2.jpg>
>
> <http://bk.xdzxxf.xyz/SMB2P.jpg>
>
> <http://bk.xdzxxf.xyz/smb2.jpg>
>
> <http://bk.xdzxxf.xyz/SMB1.jpg>
>
> <http://bk.xdzxxf.xyz/SBM2P.jpg>

**MSI文件MD5：**

> 4658ddc4e03f0003f590666ab73261e3
>
> be0384e85412a2668008f76dc3b3ccea
>
> 5bab2f1dd53b3ae08dab8a1a2d7c145c
>
> 2c62e2fbef311731ebbc26c785d10f2b

 ***本文作者： 深信服千里目安全实验室，转载请注明来自FreeBuf.COM**  
  

