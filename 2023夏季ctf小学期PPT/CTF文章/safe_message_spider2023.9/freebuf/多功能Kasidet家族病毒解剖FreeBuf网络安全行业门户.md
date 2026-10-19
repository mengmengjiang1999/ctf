## 一、 背景介绍

**近日，深信服安全团队在云查记录中捕获到一款高度活跃的病毒，并对其进行了深入分析后确定该病毒为Kasidet家族。此次分析的病毒主要通过窃取系统信息然后连接服务器根据攻击者分发不同的命令执行不同的功能，攻击者可以利用受感染的计算机作为攻击平台实施各种网络攻击,如DDoS攻击、局域网感染、散布蠕虫病毒、窃取机密资料等，其隐秘性、破坏性和威胁程度都远大于单一的网络攻击模式。**

## 二、 样本信息

该病毒的图标及详细信息，如下：

![1.jpg](https://image.3001.net/images/20181226/1545810051_5c23308339493.jpg!small)

## 三、 样本分析

1\. 该病毒的核心代码经过加密处理，运行后首先会调用VirtualAlloc申请空间在内存进行PE文件解密，然后再执行到PE文件入口点，如下：

![图1解密后的PE文件
](https://image.3001.net/images/20181226/1545810057_5c23308987475.png!small)图1解密后的PE文件  

2\.
解密后的PE文件分析，调用函数SetUnhandledExceptionFilter设置异常捕获，获取当前进程句柄，提升自身权限为Debug权限，如下：

![图2提升权限
](https://image.3001.net/images/20181226/1545810064_5c233090d730c.png!small)图2提升权限

3\. 创建互斥体变量“4ZBR19116-NNIF”，为避免程序重复运行，如果存在该变量则退出，如下：

![图3创建互斥体变量
](https://image.3001.net/images/20181226/1545810071_5c23309710833.png!small)图3创建互斥体变量  

4\.
创建文件夹%APPDATA%\4ZBR19116-NNIF\,并将自身重命名为{随机名}.exe复制到该目录下，判断当前用户是否为管理组成员，设置注册表HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run，达到开机自启动的目的，复制explorer.exe的创建时间修改为自身文件的创建时间，然后启动进程复制后的文件{随机名}.exe，如下：

![图4复制自身修改文件时间、设置Run启动
](https://image.3001.net/images/20181226/1545810077_5c23309d4b5d5.png!small)图4复制自身修改文件时间、设置Run启动

5\. 创建线程，监视注册表活动状态使应用程序可以接收事件通知指定的注册表项及其子项的更改，如下：

![图5监视注册表](https://image.3001.net/images/20181226/1545810084_5c2330a4bd2a6.png!small)图5监视注册表

6\.
获取系统的安装时间RegId，判断系统的版本号，获取系统安装的杀毒软件信息，扫描获取本地局域网内的IP地址，获取受感染机的安装密钥，动态解密上线地址，发送上线验证数据，等待远控命令。检查%APPDATA%，%TEMP%和%ALLUSERSPROFILE%中的所有可执行文件，代码如下：

![图6获取系统信息、发送上线验证数据
](https://image.3001.net/images/20181226/1545810093_5c2330adbe4b6.png!small)图6获取系统信息、发送上线验证数据  

![图7解密后的C&C地址
](https://image.3001.net/images/20181226/1545810093_5c2330adcdcce.png!small)图7解密后的C&C地址

该病毒对于发送的每一个请求，都会检查其中的验证密钥，建立连接后，发送验证密钥

“21232f297a57a5a743894a0e4a801fc3”，等待接收远控指令，如下：

![图8建立连接，发送上线验证数据
](https://image.3001.net/images/20181226/1545810104_5c2330b85e6aa.png!small)图8建立连接，发送上线验证数据  

7\. 调用CreateToolhelp32Snapshot函数遍历系统进程，查找浏览器进程firefox.exe、chrome.exe
、iexplore.exe 、Opera.exe,然后选择对应的浏览器以POST请求的方式发送受感染机的数据，如下：

![图9遍历进程，查找chrome浏览器
](https://image.3001.net/images/20181226/1545810134_5c2330d63d97d.png!small)图9遍历进程，查找chrome浏览器  

![图10 firefox浏览器进行网络通信
](https://image.3001.net/images/20181226/1545810134_5c2330d645509.png!small)图10
firefox浏览器进行网络通信  

![图11 IExplore浏览器进行网络通信
](https://image.3001.net/images/20181226/1545810134_5c2330d653e73.png!small)图11
IExplore浏览器进行网络通信  

![图12 Opera浏览器进行网络通信
](https://image.3001.net/images/20181226/1545810134_5c2330d6b9753.png!small)图12
Opera浏览器进行网络通信

8\.
数据以“getcmd=1&uid=%s&os=%s&av=%s&nat=%s&version=%s&serial=%s&quality=%i”字符串的形式进行发送，其中uid表示受感染的计算机guid，os表示操作系统上的数据，av表示已安装的防病毒软件，
nat表示本地IP地址信息，version表示安装的版本，quality 是检测到的病毒数量，如下：

![图13 发送字符串的形式
](https://image.3001.net/images/20181226/1545810146_5c2330e2a79f9.png!small)图13
发送字符串的形式

9\. 如果连接服务器成功，可接收执行的远控命令，如下：

rate  |  设置服务器请求之间的时间间隔  
---|---  
update  |  更新自身文件下载文件  
loader  |  下载.dll文件并使用regsvr32工具运行它  
Findfile  |  查找指定文件并将其上传到远程服务器  
cmd  |  启动并执行cmd.exe  
spread  |  感染局域网的计算机  
archive  |  感染可移动磁盘  
usb  |  感染usb  
Botkiller  |  删除其他恶意病毒程序  
http  |  发送GET或POST请求  
slow  |  发送带有“Xa：b \ r \ n”有效负载的POST请求  
dwflood  |  请求下载和删除文件  
tcp  |  启动TCP Flood攻击  
udp  |  启动UDP Flood攻击  
https  |  启动HTTPS Flood攻击  
keylogger  |  获取前盘记录，剪贴板内容和击键，并在按下鼠标按钮时截取屏幕截图，然后保存到一个logs.rar文件中  
  
接收可执行的远控命令，相关代码如下：

![图14 远控命令部分代码1
](https://image.3001.net/images/20181226/1545810156_5c2330ecb839a.png!small)图14
远控命令部分代码1  

![图15 远控命令部分代码2
](https://image.3001.net/images/20181226/1545810156_5c2330ecc1337.png!small)图15
远控命令部分代码2  

![17.png](https://image.3001.net/images/20181226/1545810156_5c2330ecc3747.png!small)

图16 远控命令部分代码3

10\. 反调试技术分析：

a. 通过IsDebuggerPresent和CheckRemoteDebuggerPresent检查程序是否为调试状态。

b.
通过获取系统用户名及模块用于检查沙箱和虚拟机，受检查的用户名“MALTEST、TEQUILABOOMBOOM、SANDBOX、VIRUS、MALWARE、SAMPLE、VIRUS、SANDBOX”。

c. 通过kernel32.dll检查是否有导出函数”wine_get_unix_file_name”来检测wine软件。

d. 通过注册表来检查VMware虚拟机、VirtualBox虚拟机、QEMU模拟器，相关注册表及值如下：

SOFTWARE\\\VMware,Inc.\\\VMware Tools

HARDWARE\\\DEVICEMAP\\\Scsi\\\ScsiPort0\\\ScsiBus0\\\TargetId0\\\Logical Unit
Id0 ，值：“Identifier”、“VBOX”。

HARDWARE\\\Description\\\System，值：“SystemBiosVersion”、“VBOX”

SOFTWARE\\\Oracle\\\VirtualBox Guest Additions
HARDWARE\\\Description\\\System，值：“VideoBiosVersion”、“VIRTUALBOX”

HARDWARE\\\DEVICEMAP\\\Scsi\\\Scsi Port 0\\\Scsi Bus 0\\\Target Id
0\\\LogicalUnit Id 0，值：“Identifier”、“QEMU”

"HARDWARE\\\Description\\\System，值：“SystemBiosVersion”、“QEMU”

如果其中有一项条件满足，则弹出错误对话框，启动自我删除，退出程序，代码如下：

  
![图17
反调试、反虚拟机、反沙箱](https://image.3001.net/images/20181226/1545810166_5c2330f66efa9.png!small)图17
反调试、反虚拟机、反沙箱  

## 四、 相关IOC

### MD5

> 原始样本：99F5AD74262E5CD0509D5DCE82262D02
>
> 解密后的PE：C6530B4293D79D73D4FF0822A5DB98A8

### DNS

> nutqss123a10cc.com
>
> nutqss123a2cc.com
>
> nutqss123a3cc.com
>
> nutqss123a4cc.com
>
> nutqss123a5cc.com
>
> nutqss123a6cc.com
>
> nutqss123a9cc.com
>
> nutqss123a1cc.com
>
> nutqss123a11cc.com
>
> nutqss123a12cc.com
>
> nutqss123a13cc.com

###  URL

> <http://nutqss123a10cc.com/newfiz5/tasks.php>
>
> <http://nutqss123a2cc.com/newfiz5/tasks.php>
>
> <http://nutqss123a3cc.com/newfiz5/tasks.php>
>
> <http://nutqss123a4cc.com/newfiz5/tasks.php>
>
> <http://nutqss123a5cc.com/newfiz5/tasks.php>
>
> <http://nutqss123a6cc.com/newfiz5/tasks.php>
>
> <http://nutqss123a9cc.com/newfiz5/tasks.php>
>
> <http://nutqss123a1cc.com/newfiz5/tasks.php>
>
> <http://nutqss123a11cc.com/newfiz5/tasks.php>
>
> <http://nutqss123a12cc.com/newfiz5/tasks.php>
>
> <http://nutqss123a13cc.com/newfiz5/tasks.php>

## 五、 解决方案

###  **病毒检测查杀**

1\. 使用查杀工具，进行检测查杀：<http://edr.sangfor.com.cn/tool/SfabAntiBot.zip>

2\. 使用防火墙、安全感知平台等安全产品均具备病毒检测能力，部署相关产品用户可进行病毒检测。

###  **病毒防御**

> 1\. 及时给电脑打补丁，修复漏洞。
>
> 2\. 陌生人发来的陌生文档，邮件不要轻易打开
>
> 3\. 对重要的数据文件定期进行非本地备份

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。

 ***本文作者：千里目安全实验室，转载请注明来自 FreeBuf.COM**  

