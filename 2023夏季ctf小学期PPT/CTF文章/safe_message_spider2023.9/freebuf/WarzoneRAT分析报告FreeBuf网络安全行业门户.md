**网络犯罪分子通过出售恶意软件服务（MaaS）获利，各种远程访问工具（RAT）变得越来越流行。
尽管这些RAT是恶意工具，但售卖者假装他们只是向系统管理员出售合法软件，并提供订阅服务和客户服务。开发人员正在不断改进这些工具并添加新功能，因此产生了越来越复杂的RAT。**

报告中详细分析了Warzone RAT，以及开发人员提供的各种不同功能。  

## RAT分析

Warzone RAT第一则广告于2018年秋季在warzone [.] io上出现， 目前销售服务托管在warzone [.]
pw上。开发人员还在warzonedns [.] com上运行了DNS服务。根据网站描述，该恶意软件具有以下功能：

> 不需要.NET
>
> 可通过VNC使用远程桌面
>
> 可通过RDPWrap获得隐藏的远程桌面
>
> 提权（包括最新的Win10）
>
> 远程WebCam控件
>
> 密码采集（Chrome，Firefox，IE，Edge，Outlook，Thunderbird，Foxmail）
>
> 下载并执行任何文件
>
> 实时键盘记录器
>
> Remote Shell
>
> 文件管理器
>
> 进程管理
>
> 反向代理

下图为该网站的广告：

![tek-9.png](https://image.3001.net/images/20200326/1585182115_5e7bf5a3bae91.png!small)![tek-9.png](https://image.3001.net/images/20200326/1585182184_5e7bf5e8e632b.png!small)

网站还提供了作者联系方式，买家可以选择不同订阅服务。

![image.png](https://image.3001.net/images/20200326/1585182317_5e7bf66d136b4.png!small)可以在VirusTotal上找到Warzone，可能是客户自己泄漏的。  

![image.png](https://image.3001.net/images/20200326/1585182372_5e7bf6a42db7c.png!small)

## 技术细节

Warzone是一种用C
++编写并与所有Windows版本兼容的RAT。恶意软件开发人员在warzonedns.com上提供了DNS服务，购买者不受IP地址更改的影响。Warzone绕过UAC（用户帐户控制）与Windows
Defender，并写入启动程序列表中，处理C＆C命令。 它有几种不同的版本，同时在不断改进， 某些描述可能会因版本变化而不同。

### 绕过UAC

如果Warzone RAT以高权限运行，会添加路径到Windows Defender白名单中：

> powershell Add-MpPreference -ExclusionPath C：\  
>

恶意软件会通过两种不同的方法绕过UAC并提权：  

> 对于Windows 10以下的版本，它使用存储在其资源中UAC绕过模块。  
>
>
> 对于Windows 10，它利用sdclt.exe的自动提升功能，该功能在Windows备份和还原中使用。

![image.png](https://image.3001.net/images/20200326/1585182753_5e7bf8218fffd.png!small)![image.png](https://image.3001.net/images/20200326/1585182765_5e7bf82d569f4.png!small)

#### Windows 10 UAC绕过

标准用户权限进程调用sdclt.exe时，会发生以下事件：  

> 以高权限运行另一个sdclt.exe进程。  
>
>
> 高权限sdclt进程调用C：\Windows\System32\control.exe。
>
> control.exe进程以高权限运行，并打开HKCU\Software\Classes\Folder\shell\open\command注册表值。

恶意软件将其自身路径设置为HKCU\Software\Classes\Folder\shell\open\command执行COM劫持。这些操作可以用以下命令代替：

> reg add "HKCU\Software\Classes\Folder\shell\open\command" /d
> "<PATH_TO_MALWARE>" /f
>
> reg add HKCU\Software\Classes\Folder\shell\open\command /v "DelegateExecute"
> /f

最后恶意软件自行终止， 由sdclt.exe以高权限运行。

####
![image.png](https://image.3001.net/images/20200326/1585183081_5e7bf9699cfe7.png!small)Windows
10以下的版本  

对于Windows
10以下的Windows版本，该恶意软件进行IFileOperation攻击。首先，它在HKCU\SOFTWARE中创建注册表hive_rptls，Install值指向其自身路径。

![image.png](https://image.3001.net/images/20200326/1585183207_5e7bf9e7a0d7b.png!small)

然后恶意软件从WM_DSP资源加载可执行文件，运行shellcode（在使用XOR
0x45对其进行解密之后）。Shellcode解析功能函数，在挂起状态下运行cmd.exe执行进程替换。(ZwUnmapViewOfSection –
VirtualAllocEx – GetThreadContext – WriteProcessMemory – SetThreadContext).

![image.png](https://image.3001.net/images/20200326/1585183297_5e7bfa4183c21.png!small)

负责UAC绕过的代码来自AVE_MARIA恶意软件。以下代码片段显示了如何在cmd.exe中进行提权。

![image.png](https://image.3001.net/images/20200326/1585183339_5e7bfa6beae0d.png!small)恶意软件从WM_DISM资源中提取dismcore.dll，并将其与xml文件ellocnak.xml一起放到％TEMP％目录中。

![image.png](https://image.3001.net/images/20200326/1585183377_5e7bfa91c567e.png!small)然后伪装成PEB（Process
Environment Block）调用IFileOperation。

![image.png](https://image.3001.net/images/20200326/1585183452_5e7bfadccfdf4.png!small)使用pkgmgr.exe加载dismcore.dll。  

![image.png](https://image.3001.net/images/20200326/1585183486_5e7bfafea2563.png!small)加载的DLL从HKCU\SOFTWARE\\_rptls\Install中检索Warzone恶意文件的路径，对正在运行的进程进行迭代，并杀死已存在的Warzone进程。
然后再次使用管理员权限运行Warzone。  

### 持久性

恶意软件会将自身复制到C：\Users\User\AppData\Roaming\<INSTALL_NAME>.exe，并将此路径添加到HKCU\Software\Microsoft\Windows\CurrentVersion\Run。
默认情况下，<INSTALL_NAME>是images.exe。它还会创建HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\UIF2IS2OVK，inst值为256字节的伪随机生成序列。如果恶意软件没有管理员权限下运行且未被终止，它将自身复制到C：\ProgramData\<PREDEFINED_NAME>。

### 网络通信

恶意软件通过TCP5200端口与C＆C服务器通信。 数据包使用密码“ warzone160 \ x00”通过R**加密，数据包格式如下：

![image.png](https://image.3001.net/images/20200326/1585183886_5e7bfc8ec3523.png!small)返回包格式如下：

  
  

![image.png](https://image.3001.net/images/20200326/1585183914_5e7bfcaaab448.png!small)![image.png](https://image.3001.net/images/20200326/1585183939_5e7bfcc3a5e28.png!small)虽然Warzone支持tcp数据包加密，但是有的版本仍然选择不加密通信数据：

![image.png](https://image.3001.net/images/20200326/1585184004_5e7bfd04d7f35.png!small)数据包中的有效负载会以以下格式存储：

![image.png](https://image.3001.net/images/20200326/1585184042_5e7bfd2a97ae3.png!small)恶意软件解密C＆C服务器域并连接，
服务器接受连接后将向客户端发送消息ID=0和空负载。 此时恶意软件会收集计算机信息发送回服务器。 数据包包含以下数据：

> MachineGUID的SHA-1值  
> 攻击ID  
> 系统版本  
> 管理员状态  
> WOW64进程状态  
> 计算机名称  
> 恶意软件存储位置  
> 恶意软件MurmurHash3  
> RAM大小  
> CPU信息  
> 视频控制器信息  
>

bot ID是HKLM\Software\Microsoft\Cryptography中MachineGUID的SHA-1哈希。

程序会等待来自服务器的其他命令。服务器消息ID是从0x00到0x3C的偶数。
攻击者能够使用远程shell，RDP或VNC控制台控制受感染的PC，还可以远程任务文件管理，桌面监控，使用网络摄像头等等。

交互信息如下：

![image.png](https://image.3001.net/images/20200326/1585184471_5e7bfed739e3d.png!small)![image.png](https://image.3001.net/images/20200326/1585184483_5e7bfee3bee7a.png!small)![image.png](https://image.3001.net/images/20200326/1585184522_5e7bff0a6768f.png!small)C&C通信示例可见[原文](https://research.checkpoint.com/2020/warzone-behind-the-enemy-lines/)。

## 管理Panel

发现1.84版本的Warzone panels/builders，由.net编写并使用了混淆。

![image.png](https://image.3001.net/images/20200326/1585184710_5e7bffc638848.png!small)

混淆代码使用了大量的算术计算和switch结构使代码更难以理解，这些算术计算和switch结构不影响控制流，并能够隐藏有用的指令。通过界面化操作，可以完全控制被感染的机器。

![image.png](https://image.3001.net/images/20200326/1585184852_5e7c005408d87.png!small)panel
bundle包含以下项：

##
![image.png](https://image.3001.net/images/20200326/1585184908_5e7c008ca4c45.png!small)总结

虽然Warzone被掩饰为合法工具，但它实际上是木马程序，可以通过其他恶意软件或垃圾邮件进行传播。Warzone是使用C
++代码编写，有自己的TCP的网络协议，没有使用HTTP通信。除了自定义网络协议和基础结构外，Warzone还包括2种不同的UAC绕过，对于Windows
10和早期版本非常有效。

## IOCs

### [样本](https://www.kernelmode.info/forum/viewtopic8b5f.html?f=16&t=5525)

> SHA256
>
> 531d967b9204291e70e3aab161a5b7f1001339311ece4f2eed8e52e91559c755
>
> a03764da06bbf52678d65500fa266609d45b972709b3213a8f83f52347524cf2
>
> 263433966d28f1e6e5f6ae389ca3694495dd8fcc08758ea113dddc45fe6b3741

### Processes  

> Command Line
>
> powershell Add-MpPreference -ExclusionPath C:\

### Registry Detection  

Registry Path  
| Registry Key  
| Values  
  
---|---|---  
HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings  
| Settings MaxConnectionsPer1_0Server  
| 10  
HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings  
| MaxConnectionsPerServer  
| 10  
HKCU\Software\\_rptls  
| Install| <PATH_TO_MALWARE>  
  
  
### File System Detection  

File Name  
| Comments  
  
---|---  
%LOCALAPPDATA%\Microsoft Vision\  
|  Directory  
  
%LOCALAPPDATA%\Microsoft
Vision\\([0-2][0-9]|(3)[0-1])(-)(((0)[0-9])|((1)[0-2]))(-)\d{4}_(?:[01]\d|2[0123])\\.(?:[012345]\d)\\.(?:[012345]\d)  
| Regex for datetime in format: DD-MM-YYYY_HH.mm.SS  
  
  
### C&C servers  

Domains  
| Communication Type  
  
---|---  
*.warzonedns[.]com  
| TCP over 5200  
  
  
 ***参考来源：[checkpoint](https://research.checkpoint.com/2020/warzone-behind-the-enemy-lines/)，由Kriston编译，转载请注明来自FreeBuf.COM**

