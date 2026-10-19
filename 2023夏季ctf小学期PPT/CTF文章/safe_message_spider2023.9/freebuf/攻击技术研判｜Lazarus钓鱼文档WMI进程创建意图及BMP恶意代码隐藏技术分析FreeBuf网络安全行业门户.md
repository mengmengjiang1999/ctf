## **情报背景**

Email、Office作为常见的攻击媒介，一直都受到微软及安全厂商的重点关注，针对相关攻击推出了许多执行限制和检测措施。

本文针对近期Lazarus组织攻击活动中钓鱼文档部分进行分析，包括试图绕过安全限制进行OFFICE进程创建的意图，并复现利用bmp图像隐藏恶意hta对象的隐写技术。

 **组织名称**

|

Lazarus  
  
---|---  
  
 **组织编号**

|

APT38  
  
 **战术标签**

|

文档钓鱼  
  
 **技术标签**

|

wmi进程创建 marco 图片隐写  
  
 **情报来源**

|

https://blog.malwarebytes.com/malwarebytes-news/2021/04/lazarus-apt-conceals-malicious-code-within-bmp-file-to-drop-its-rat/  
  
## 攻击技术分析

### 亮点一：宏代码中使用WMI创建进程

 **攻击者宏代码中用WMI创建进程，尝试规避OFFICE创建进程限制**

![1628586449_611241d168b7da5d77dc6.png!small?1628586450430](https://image.3001.net/images/20210810/1628586449_611241d168b7da5d77dc6.png!small?1628586450430)
关于创建进程的等效代码如下

![1628586488_611241f844de091a0920a.png!small?1628586489175](https://image.3001.net/images/20210810/1628586488_611241f844de091a0920a.png!small?1628586489175)

代码使用base64解密后，调用GetObject获取Win32_Process对象，并使用Create方法创建子进程mshta.exe。

攻击者可能是意图调用WMI托管组件的方式启用新进程，规避掉与office word进程的父子关系。

样本在any.run中的运行结果，创建后的mshta.exe确实是和winword.exe脱离进程父子关系。![1628586548_6112423470620fec5e8ba.png!small?1628586549504](https://image.3001.net/images/20210810/1628586548_6112423470620fec5e8ba.png!small?1628586549504)

Any.Run链接：https://app.any.run/tasks/4a257566-2cc3-4e64-bd7f-79614caca349/

我们创建一个启动计算器的POC代码，测试下WMI创建进程效果。

![1628586539_6112422bc21c440961cf3.png!small?1628586540712](https://image.3001.net/images/20210810/1628586539_6112422bc21c440961cf3.png!small?1628586540712)

![1628586582_611242561317da2a8a497.png!small?1628586583087](https://image.3001.net/images/20210810/1628586582_611242561317da2a8a497.png!small?1628586583087)

可以看到计算器确实已经是独立的进程。

 **安全厂商对此类攻击技术的安全防护措施**

Microsoft Defender for
Endpoint中针对此类攻击提出攻击面缩小(ASR)方案，为企业提供了一组内置的组策略配置，拦截这些恶意攻击的底层行为。

比如对email、office等常见攻击媒介进程的行为进行审查，当这些进程出现有创建子进程，注入代码到其他进程或执行脚本代码时，其恶意行为将会被阻止。

微软文档-自定义减少攻击面规则

https://docs.microsoft.com/zh-cn/microsoft-365/security/defender-endpoint/customize-attack-surface-reduction?view=o365-worldwide

微软文档-使用组策略配置ASR

https://docs.microsoft.com/zh-cn/microsoft-365/security/defender-endpoint/enable-attack-surface-reduction?view=o365-worldwide

 **ASR中和进程创建相关的有**

1\. 阻止所有Office应用程序创建子进程（Block all Office applications from creating child
processes）

此规则阻止Office创建子进程。Office应用程序包括Word、Excel、PowerPoint、OneNote和Access。

创建子进程是一种常见的恶意软件行为。滥用Office合法组件的恶意软件通常会运行VBA宏，并执行下载运行更多恶意载荷。但是，某些合法的应用程序也可能出于正常业务目的创建子进程，例如生成命令提示符或使用
PowerShell 配置注册表设置的情况。

Intune 名称：Office apps launching child proc esses

Configuration Manager 名称：Block Office application from creating child
processes

GUID：D4F940AB-401B-4EFC-AADC-AD5F3C50688A

2\. 阻止源自PSExec和WMI命令的进程创建（Block process creations originating from PSExec and
WMI commands）

此规则阻止通过PsExec（https://docs.microsoft.com/zh-cn/sysinternals/downloads/psexec）和WMI（https://docs.microsoft.com/zh-cn/windows/win32/wmisdk/about-wmi）创建进程。PsExec和WMI都可以远程执行代码，因此经常存在恶意软件滥用此功能用于命令控制目的，存在在整个组织的网络中传播感染的风险。

Intune 名称：Process creation from PSExec and WMI commands

Configuration Manager 名称：不适用

GUID：d1e49aac-8f56-4280-b9ba-993a6d77406c

 **配置ASR测试绕过**

配置组策略

![1628586691_611242c3370202d042e91.png!small?1628586692455](https://image.3001.net/images/20210810/1628586691_611242c3370202d042e91.png!small?1628586692455)

准备的测试代码

![1628586845_6112435d00c4a30518331.png!small?1628586845967](https://image.3001.net/images/20210810/1628586845_6112435d00c4a30518331.png!small?1628586845967)

1\. 启用阻止所有Office应用程序创建子进程

![1628586947_611243c38dd3aad3e4ce2.png!small?1628586948506](https://image.3001.net/images/20210810/1628586947_611243c38dd3aad3e4ce2.png!small?1628586948506)

![1628586960_611243d07f335da4fe600.png!small?1628586961574](https://image.3001.net/images/20210810/1628586960_611243d07f335da4fe600.png!small?1628586961574)

2\. 启用阻止源自PSExec和WMI命令的进程创建

![1628587012_6112440444a41893f3664.png!small?1628587013211](https://image.3001.net/images/20210810/1628587012_6112440444a41893f3664.png!small?1628587013211)

![1628587033_61124419c1f18901e8bf0.png!small?1628587034744](https://image.3001.net/images/20210810/1628587033_61124419c1f18901e8bf0.png!small?1628587034744)

可以看到，两张图中ASR都成功的对WMI创建计算器的行为进行了拦截。

在2019年的时候，法国的安全研究员Emeric Nasi撰写了一篇绕过ASR的相关文章[Bypass Windows Defender Attack
Surface Reduction]

https://blog.sevagas.com/IMG/pdf/bypass_windows_defender_attack_surface_reduction.pdf

里面提到使用wmi可以绕过阻止所有Office应用程序创建子进程 （D4F940AB-401B-4EFC-AADC-AD5F3C50688A）这一项。

在本文撰写时，发现其相关方式都已经失效，但我们对其稍加更改，仍可绕过。

 **使用LOLBins绕过ASR防护**

我们在Emeric Nasi提出的方式基础上稍加改动，使用explorer这类lolbins代理启动计算器，成功绕过ASR弹出计算器。

![1628587127_611244776fdfaa790dd49.png!small?1628587128427](https://image.3001.net/images/20210810/1628587127_611244776fdfaa790dd49.png!small?1628587128427)

### 亮点二：使用bmp图像进行数据压缩隐藏hta对象

样本中的宏代码，将PNG图片解压为BMP图片，然后另存为ZIP文件，最后使用mshta调用ZIP，成功执行里面包含的js代码。

![1628587328_611245403b9f1ba6f4975.png!small?1628587329161](https://image.3001.net/images/20210810/1628587328_611245403b9f1ba6f4975.png!small?1628587329161)

因为PNG是ZLIB压缩格式的图片，攻击者利用这一点可以避免检测到图片中镶嵌的恶意对象。

 **复现**

1\. 准备一个BMP图片，并将里面图片数据部分替换成hta对象内容。

![1628587353_611245591d37e690ada6e.png!small?1628587354096](https://image.3001.net/images/20210810/1628587353_611245591d37e690ada6e.png!small?1628587354096)

2\. 将BMP图片header 0×1c处修改为24。

![1628587375_6112456f976453206d56e.png!small?1628587376501](https://image.3001.net/images/20210810/1628587375_6112456f976453206d56e.png!small?1628587376501)

3\. 调用ConvertBMPtoPNG转换，过程中BMP会被压缩为PNG，至此样本制作成功。

![1628587398_611245866811ea8c4c21e.png!small?1628587399285](https://image.3001.net/images/20210810/1628587398_611245866811ea8c4c21e.png!small?1628587399285)

![1628587409_61124591f1af66363026b.png!small?1628587411347](https://image.3001.net/images/20210810/1628587409_61124591f1af66363026b.png!small?1628587411347)

4\. 调用ConvertPNGtoZIP转换，过程中PNG会被解压缩为BMP。

![1628587425_611245a14f3ea3cdff0b0.png!small?1628587426201](https://image.3001.net/images/20210810/1628587425_611245a14f3ea3cdff0b0.png!small?1628587426201)

5\. 执行mshta C:\hta.zip，成功弹出计算器，复现成功。

![1628587441_611245b1692723c0adb61.png!small?1628587442381](https://image.3001.net/images/20210810/1628587441_611245b1692723c0adb61.png!small?1628587442381)

## 总结

无论是该组织之前利用UUIDFromString隐藏shellcode还是此次利用bmp图像隐藏恶意HTA对象，说明该组织擅长滥用系统合法API的方式来隐藏其恶意行为。这种鲜有出现的攻击方式对安全团队的检测能力提出了新的挑战，虽然微软的ASR减少攻击面的策略能有效的防范该类攻击，但在高级对抗中依旧存在被绕过的风险。

