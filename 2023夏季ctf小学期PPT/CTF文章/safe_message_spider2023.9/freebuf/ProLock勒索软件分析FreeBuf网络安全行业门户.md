![](https://image.3001.net/images/20200813/1597258281.jpg!small)

## 写在前面的话

当各个组织正忙于应对全球疫情的时候，新一波的勒索软件攻击又悄悄开始了。这款名为ProLock的勒索软件，是2019年底出现的PwndLocker勒索软件的变种版本。PwndLocker的传播时间非常短，主要是因为很多用户发现解密文件所需的密钥可以从恶意软件本身来获取，这样就无需支付赎金了。但是，今年三月份出现的ProLock正好相反，因为目标用户在支付了赎金之后，接收到的却是一个存在问题的[
_解密工具_](https://www.bleepingcomputer.com/news/security/pwndlocker-ransomware-gets-pwned-decryption-now-available/)，而这个解密工具将会损坏目标用户设备中已被勒索软件加密的数据。

这种错误可能与ProLock加密文件时所采用的异常方式有关，因为ProLock在加密文件时，会跳过小于8192字节的文件，并且会对第一个8192字节之后的大文件进行加密。这样一来，将导致文件部分可读，部分被加密。

## ProLock准备工作

ProLock可以通过多种方式来获取目标网络的访问权，其中还涉及到一些第三方漏洞的利用。而且根据[ _Group-IB_](https://www.group-ib.com/blog/prolock)的研究人员透露的信息，有一些ProLock受害者是通过QakBot银行木马所执行的脚本感染的。FBI还指出，QakBot是ProLock的初始感染手段之一，除此之外还有利用网络钓鱼邮件和存在错误配置的[
_RDP服务器_](https://sophos.com/rdp)等等。研究人员表明，最早的ProLock入侵行为是通过远程桌面协议（RDP）连接来实现的。

ProLock攻击着还会利用初始攻击所获得的访问权限来进行一些网络侦察活动，并在开始勒索软件攻击之前窃取一些用户敏感数据。在研究的过程中，研究人员对目标系统中存储的四个与勒索软件相关的文件进行了分析，这些文件是从一个远程服务器下载下来的，相关的IP地址已经作为入侵威胁指标发布在了SophosLabs的GitHub库中了：

    
    
    C:\ProgramData\WinMgr.bmp
    
    C:\ProgramData\WinMgr.xml
    
    C:\ProgramData\clean.bat
    
    C:\ProgramData\run.bat

## ProLock攻击链

ProLock恶意软件依赖于Windows
Batch脚本，Windows计划任务（schtasks.exe）和PowerShell来发动其攻击。勒索软件链由run.bat脚本文件作为起始，它会创建一个Windows任务并使用WinMgr.xml来配置任务，然后执行clean.bat脚本。当该脚本由计划任务执行之后，clean.bat将会执行一个Base64编码的PowerShell脚本，并从一个名叫WinMgr.bmp的图片文件中提取出ProLock的可执行文件，然后将其加载进内存中并执行。

**下图显示的是clean.bat中嵌入的部分Base64编码脚本代码：**![](https://image.3001.net/images/20200813/1597258299.png!small)

**下图显示的是WinMgr.bmp中的部分脚本代码：**![](https://image.3001.net/images/20200813/1597258304.png!small)

**下图显示的是WinMgr.bmp的图形内容，其中隐藏了ProLock恶意软件Payload，这里使用了隐写术：**![](https://image.3001.net/images/20200813/1597258310.jpg!small)

## ProLock样本分析

我们在分析一个ProLock样本时发现，它使用了一段自修改的代码来隐藏了去中的部分内容，这段代码隐藏了部分文本字符串和其他元素。正如恶意软件开发中常见的那样，ProLock程序被故意设置为不允许调试，从而使研究人员更难通过受控的方式来运行它。

**下图显示的是恶意软件样本执行过程中的部分混淆代码：**![](https://image.3001.net/images/20200813/1597258333.png!small)

**下图显示的是ProLock二进制文件自修改前后的代码对比：**![](https://image.3001.net/images/20200813/1597258339.png!small)

接下来，代码会对其自修改的部分进行解码，导入DLL，并设置好其需要使用的功能函数。设置完成后，便会开启一个新的线程，然后将第一个线程设置为休眠（一种反分析技术）。随后，恶意软件将遍历目标设备的注册表以寻找潜在的安全策略设置。出于某种原因，恶意软件会将IE浏览器的安全策略设置进行修改，关掉IE的通用命名约定路径，并启用自动Intranet映射，然后开始寻找可能会阻碍数据加密/销毁的应用程序以及服务。

通过调用Windows的[ _CreateToolhelp32snapshot.dll_](https://docs.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot)，恶意软件还会存储所有正在运行进程的快照，并通过对照一个内置列表来进行进程检查，然后试用taskkill.exe实用工具来关闭所有与该列表匹配的进程，比如说一些Microsoft
Office程序、Firefox浏览器、Thunderbird邮件客户端以及安全软件组件等等。勒索软件会终止这类进程，以确保用户文件没有处于锁定或打开状态，从而实现数据的成功加密。

接下来，恶意软件将会试用net.exe来尝试关闭与企业应用程序、安全软件和备份软件相关的150多种服务和进程。这一操作的目的同样是为了排除数据加密的其他干扰因素。

然后，为了防止本地文件恢复，ProLock将会通过执行下列命令来删除本地文件的“卷影副本”vssadmin.exe文件（Windows的卷影复制服务）：

    
    
    delete shadows /all /quiet
    
    resize shadowstorage /for=c: /on=c: /maxsize=401MB
    
    resize shadowstorage /for=c: /on=c: /maxsize=unbounded

注意事项：勒索软件针对的进程和服务的完整列表发布在SophosLabs的GitHub上【[
_传送门_](https://github.com/sophoslabs/IoCs/blob/master/prolock_processes_stopped.csv)】。

此时，当目标主机上所有的安全防护措施都已经失效之后，勒索软件将会开始检测目标主机上所有已加载的存储介质，并遍历本地或网络驱动器的目录结构，这一部分操作都是通过powershell.exe进程来实现的。

当它每读取到一个文件时，首先会检查文件大小，如果文件小于8192字节（十六进制为0x2000），则跳过该文件。否则，它将从8192字节之后开始加密文件。加密文件后，扩展名.prolock会附加到其文件后缀之后。比如说，a_very_large_text_file.txt就会变成a_very_large_text_file.txt.prolock。

**下图显示的是PreLock加密后的文件截图：**![](https://image.3001.net/images/20200813/1597258355.png!small)

**下图显示的是文件加密前后的数据对比：**![](https://image.3001.net/images/20200813/1597258360.png!small)

当勒索软件完成每个目录内的文件加密之后，它会将一个名为[HOW TO RECOVER
FILES].TXT的文件写入到目录内，该文件包含的就是勒索信息。具体如下图所示：![](https://image.3001.net/images/20200813/1597258366.png!small)

但是，即使目标用户支付了赎金，目前也无法成功恢复数据，反而会使恢复数据的成本变得更高，因此我们建议广大用户不要轻易采取行动，请赶紧联系专业的勒索软件响应团队以获取技术支持。

## 参考资料

SophosLabs GitHub：【[
_传送门_](https://github.com/sophoslabs/IoCs/blob/master/prolock_processes_stopped.csv)】

