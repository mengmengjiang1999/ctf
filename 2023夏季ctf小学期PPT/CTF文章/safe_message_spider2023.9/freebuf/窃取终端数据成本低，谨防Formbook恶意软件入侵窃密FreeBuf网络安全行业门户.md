## ****背景概述****

科学技术的高速发展，带来了大量的商业发展机会，同时也为终端安全带来巨大的挑战。近日，深信服终端安全团队捕获了Formbook样本病毒。这是一款著名的商业恶意软件，自2016以来在黑客论坛出售，因其隐蔽且易用的特点闻名。其主要利用钓鱼邮件进行传播，一旦用户不小心下载打开邮件附件，该恶意软件将会安装到终端上窃取机密数据和敏感信息。

Formbook窃密软件在黑客论坛上的售价并不是非常高昂，使得窃密的犯罪成本降低，很容易对用户的终端数据造成威胁。

![](https://image.3001.net/images/20210527/1622115346_60af841202c274cd342ac.png!small)

（图片来自于海外媒体）

FormBook主要会从受害者的设备（如键盘记录器）中窃取受害者的键盘输入以及某些软件的数据，例如浏览器，Email客户端和FTP客户端等个人信息，并使用C2的控制命令来操纵他们的设备或者服务器。

##  ** **技术分析****

![](https://image.3001.net/images/20210527/1622115374_60af842ecb74575ff789b.png!small)

该病毒上使用”傀儡“进程进行释放以防止分析人员的调试：通过GetProcAddress获取函数名并释放动态库文件ek0j.dll，并调用其恶意导出函数Rcxlxosdkhvclf：

![](https://image.3001.net/images/20210527/1622115392_60af8440232ff29e88561.png!small)

在temp文件下写入加密文件：

![](https://image.3001.net/images/20210527/1622115415_60af845734b6001b9ba25.png!small)

加密文件经解密后为一段shellcode，将其加载到内存并执行：

![](https://image.3001.net/images/20210527/1622115433_60af84697dd6610029ea0.png!small)

创建子进程：

![](https://image.3001.net/images/20210527/1622115465_60af8489c46e9e17db8e9.png!small)

对子进程的dump进行分析病毒真正的操纵，通过使用ida Lumina进行 f12匹配分析；

初始化内存，该buffer区域在整个FormBook中进行读写，包含配置选项；

![](https://image.3001.net/images/20210527/1622115487_60af849fb81509dcd9fcc.png!small)

该buffer内存区域：

具有标记组用来检测该病毒是否在被调试状态下进行，在buffer+0x29的位置上，所以flag正确的check为：00 01 01 00 00 01 00
01 00 01 00

![](https://image.3001.net/images/20210527/1622115511_60af84b752f11dfa2a77b.png!small)

Base+0x34位置上检查ASM执行时间差来判断是否在调试状态：

![](https://image.3001.net/images/20210527/1622115526_60af84c613df1cadb763f.png!small)

存在该病毒的base，以及后面所运用到的检索API的hash值，当前的os的位数，以及许多的dll的模块

![](https://image.3001.net/images/20210527/1622115542_60af84d6394e1fc2e3db0.png!small)

全程使用计算以及比较hash，来获取api的名字以及地址：

![](https://image.3001.net/images/20210527/1622115574_60af84f6320854d3cf3ab.png!small)![](https://image.3001.net/images/20210527/1622115585_60af8501e270ba27a61a0.png!small)

重载两份ntdll，构建部分ntdll从而防止杀软在3环对原始ntdll做检测

![](https://image.3001.net/images/20210527/1622115636_60af8534c85d4fa96f74b.png!small)

![](https://image.3001.net/images/20210527/1622115617_60af85217b5099aeb486b.png!small)

反调试检查: r3与r0层的调试，查询SystemKernelDebuggerInformation，以及ProcessDebugPort

![](https://image.3001.net/images/20210527/1622115674_60af855acfa3e9d7dfc99.png!small)

(SYSTEM_INFORMATION_CLASS)SystemKernelDebuggerInformation

当为0x23时为获取系统是否在被调试信息存放到第2个参数指向的结构中,该结构是2个1字节的结构,当处于调试时这2字节都会被写入1从而判断是否在r0层进行调试

检查黑名单进程：

![](https://image.3001.net/images/20210527/1622115708_60af857c7209913002ad9.png!small)

进程也是通过hash的比对进行，进程列表为:

VBoxService.exe, VBoxTray.exe, VBoxService.exe,vmwareuser.exe,
vmwareservice.exe, vmtoolsd.exe, vmusrvc.exe, vmsrvc.exe,
sandboxiedcomlaunch.exe, procmon.exe, filemon.exe, wireshark.exe, NetMon.exe,
python.exe, perl.exe

![](https://image.3001.net/images/20210527/1622115730_60af85928c229f1414d8c.png!small)

通过checkfilename ModulePath Username来判断是否存在沙箱行为，沙箱一般会将用户名变成特定用户名从而该病毒进行检查

检查用户名列表: Cuckoo sandbox nmsdbox wilbert xpamast

0x19996921为explorer进程hash，获取线程进行劫持

![](https://image.3001.net/images/20210527/1622115759_60af85af22b3e26232739.png!small)

Windows 进程名称列表在初始化的buffer中被加密，通过索引选择，Explorer中读取到某32位进程信息，explorer.exe

![](https://image.3001.net/images/20210527/1622116095_60af86ffc9baa61c2ec32.png!small)![](https://image.3001.net/images/20210527/1622116105_60af8709e0f717ad5edf7.png!small)![](https://image.3001.net/images/20210527/1622116115_60af87136ea1f0cb73363.png!small)

记录下的进程列表为：

explorer.exe，wininit.exe，cmmon32.exe，
svchost.exe，lsass.exe，raserver.exe，netsh.exe，rundll32.exe，control.exe，
services.exe，ipconfig.exe等等

FormBook 随机获取 explorer.exe 返回的悬挂如上进程列表的进程信息，将 FormBook
有效负载文件复制到这些进程当中中，并将其主线程的入口点代码修改为注入的 FormBook 的OEP，执行 FormBook
的恶意代码，调用exitprocess来终止注入的formbook

![](https://image.3001.net/images/20210527/1622115876_60af8624782bd71a84fec.png!small)

该病毒使用explorer主线程来劫持以及进行APC注入且创建一个挂起的进程，在该挂起进程中实现迁移从而实现explorer进程中没有创建新的进程，而创建挂起的进程父进程为explorer

在C:\Program File(x86)下建立了随机的文件夹里面有病毒程序formbook的重载

![](https://image.3001.net/images/20210527/1622115904_60af86408fb4d43eaa6df.png!small)

并通过注册表进行注册

![](https://image.3001.net/images/20210527/1622115920_60af8650643febdb284a5.png!small)

并使用这两个文件进行记录获取键盘等的数据，并进行通信

![](https://image.3001.net/images/20210527/1622116147_60af87332324a4e3904b9.png!small)

![](https://image.3001.net/images/20210527/1622116175_60af874f3b8647bc470c9.png!small)

与c2服务器进行通信，随机选择十六台主机作为它自己的 c 2服务器，并将窃取的数据发送到这台服务器

C2列表:

34.102.136.180:80, 45.56.79.23:80, 52.200.25.77:80, 75.126.163.75:80,
167.114.6.31:80, 52.79.124.173:80, 163.44.239.71:80, 176.104.107.18:80,
162.0.239.203:80 ........

![](https://image.3001.net/images/20210527/1622116203_60af876b8a1a0626ca007.png!small)

构造的新的控制块

![](https://image.3001.net/images/20210527/1622116218_60af877a0b6c716d789e4.png!small)

获取样本的路径，设置当前的互斥，将病毒文件重载内存

![](https://image.3001.net/images/20210527/1622116231_60af8787d136187635a25.png!small)

经过上述的恶意操作后，该病毒会删除自身的文件: C del “C:\Users\Simp1er\Desktop\virus”

![](https://image.3001.net/images/20210527/1622116252_60af879c9ec48c917500e.png!small)

##  ** **加固建议****

1.日常生活工作中的重要的数据文件资料设置相应的访问权限，关闭不必要的文件共享功能并且定期进行非本地备份；

2.使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；

3.避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；

4.定期检测系统漏洞并且及时进行补丁修复。

