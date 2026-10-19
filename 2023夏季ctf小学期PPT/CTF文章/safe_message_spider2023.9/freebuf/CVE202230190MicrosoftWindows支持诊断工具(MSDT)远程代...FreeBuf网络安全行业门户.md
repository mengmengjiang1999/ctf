## 综述

近期，安全社区通过VirusTotal发现一个通过Office远程加载特性访问HTML页面进而利用ms-msdt协议在Word文档中执行恶意PowerShell的0day漏洞利用文档。其实该漏洞早在4月12日就已经被相关安全人员通过VT发现并提交给微软，其利用上和去年的CVE-2021-40444有很多相似之处，通过OLE的方式远程拉取一个恶意HTML，该HTML中通过msdt协议绕过了Office自带的保护视图。后续通过分析发现微软实际上之前已经尝试修复该问题，但是依旧存在rtf文件格式的绕过，最后通过msdt协议中的一处powershell注入导致最终的代码执行。

## 漏洞分析

样本通过构造一个ole对象远程拉取恶意的html文件，这里的加载方式和CVE-2021-40444类似。

![1655451354_62ac2edad575d9d20ea13.png!small?1655451355254](https://image.3001.net/images/20220617/1655451354_62ac2edad575d9d20ea13.png!small?1655451355254)

Html文件如下所示，其中使用了ms-msdt协议，该协议是Microsoft Support Diagnostics Tool
的缩写，它是一种实用程序，用于排除故障并收集诊断数据以支持专业人员分析以解决问题，其可以调用本地脚本，而不触发office的保护视图，从而导致代码执行，如下所示样本执行的代码通过base64编码。

![1655451361_62ac2ee10eae9cf1b7daf.png!small?1655451361783](https://image.3001.net/images/20220617/1655451361_62ac2ee10eae9cf1b7daf.png!small?1655451361783)

编码的数据如下所示，这里猜测其中实际执行的exe应该是通过某种方式部署到了目标机器中（目前未知）。

![1655451365_62ac2ee52dc5a57084ef9.png!small?1655451365463](https://image.3001.net/images/20220617/1655451365_62ac2ee52dc5a57084ef9.png!small?1655451365463)

这里构造poc就很简单了，替换换成模板注入的html即可，这里确保你的远端exp
存在这个路径下http://127.0.0.1:8080/www/RDF842l.html

![1655451372_62ac2eec0f4dae0d7c4a9.png!small?1655451372461](https://image.3001.net/images/20220617/1655451372_62ac2eec0f4dae0d7c4a9.png!small?1655451372461)

如下所示，确保RDF842l.html保存路径如下所示

![1655451379_62ac2ef3115c9a13e4682.png!small?1655451379504](https://image.3001.net/images/20220617/1655451379_62ac2ef3115c9a13e4682.png!small?1655451379504)

打开对应的52945af1d.docx，即可触发代码执行，这里的测试环境是office 2019

![1655451383_62ac2ef78cec885a0b634.png!small?1655451383984](https://image.3001.net/images/20220617/1655451383_62ac2ef78cec885a0b634.png!small?1655451383984)

可以看到在触发漏洞的时候，word会通过注册表选项查找对应的md-msdt这个协议，用于处理脚本中的ms-msdt后续的字段可以看到最终其实找到的就是执行代码的msdt.exe这个程序。

![1655451390_62ac2efe1f5a982d4b4e2.png!small?1655451390706](https://image.3001.net/images/20220617/1655451390_62ac2efe1f5a982d4b4e2.png!small?1655451390706)

  

![1655451397_62ac2f05de8027face7e8.png!small?1655451398205](https://image.3001.net/images/20220617/1655451397_62ac2f05de8027face7e8.png!small?1655451398205)

当你把office升级到大版本2205后，漏洞将不再触发，需要注意目前只有2019/2021提供自动更新功能。

![1655451405_62ac2f0d3e90693ed03f5.png!small?1655451405436](https://image.3001.net/images/20220617/1655451405_62ac2f0d3e90693ed03f5.png!small?1655451405436)

通过该功能可更新到大版本2205，该版本不受影响。

![1655451412_62ac2f14dcaae7aa9c692.png!small?1655451413222](https://image.3001.net/images/20220617/1655451412_62ac2f14dcaae7aa9c692.png!small?1655451413222)

如下所示，可以看到完全不会触发协议的访问，因为其中利用的特殊的 Office 远程 OLE
对象自动加载方式已经被作为非安全问题修复（没有CVE编号）。但是攻击者依然可以使用 rtf 格式样本来实现自动触发漏洞。

![1655451421_62ac2f1d8222d678cd8bb.png!small?1655451421862](https://image.3001.net/images/20220617/1655451421_62ac2f1d8222d678cd8bb.png!small?1655451421862)

其构造方式只需要将之前的docx文档按rtf另存一份即可。

![1655451426_62ac2f2244e262d01f326.png!small?1655451426593](https://image.3001.net/images/20220617/1655451426_62ac2f2244e262d01f326.png!small?1655451426593)

分析发现计算器是由sdiagnhost.exe这个程序启动的。

![1655451430_62ac2f26d5caa47fb5f4e.png!small?1655451431258](https://image.3001.net/images/20220617/1655451430_62ac2f26d5caa47fb5f4e.png!small?1655451431258)

分析sdiagnhost.exe发现其是通过CScriptedDiagNativeHost::RunScript函数来启动的calc。

![1655451440_62ac2f3067213fbb2a892.png!small?1655451440640](https://image.3001.net/images/20220617/1655451440_62ac2f3067213fbb2a892.png!small?1655451440640)

这里通过函数名可以猜测是用于调用本地的脚本，调试发现其参数传递了一个ps1脚本：

C:\Windows\diagnostics\system\PCW\TS_ProgramCompatibilityWizard.ps1

对应的参数就是构造的exp中的IT_BrowseForFile =
/../../$(calc).exe，这是最简的exp，在sdiagnhost.exe中没有任何相关的参数过滤操作。

![1655451452_62ac2f3c29b5bc2e04c9a.png!small?1655451452472](https://image.3001.net/images/20220617/1655451452_62ac2f3c29b5bc2e04c9a.png!small?1655451452472)

来看TS_ProgramCompatibilityWizard.ps1脚本可以看到通过注释发现其功能为”
如果在这些位置没有找到快捷方式，我们将转到浏览文件屏幕”，获取的IT_BrowseForFile保存在selectedProgram，并通过Test-Selection校验。

![1655451458_62ac2f420b3e38dafee59.png!small?1655451458444](https://image.3001.net/images/20220617/1655451458_62ac2f420b3e38dafee59.png!small?1655451458444)

Test-Selection逻辑如下，首先判断其路径是否为空，之后依次为test-path -literalpath
$appPath及判断是否以exe/msi后缀结尾，这也就是为什么我们exp中最后必须是.exe，.msi也是可以的。

![1655451464_62ac2f48d49ab62c1daf0.png!small?1655451465309](https://image.3001.net/images/20220617/1655451464_62ac2f48d49ab62c1daf0.png!small?1655451465309)

这里来看test-path -literalpath
$appPath，可以看到其用于判断一个路径，如下所示这里/../../也是合法的，因此exp中需要构造至少/../../，否则你就需要提供一个真实合法的路径。

![1655451475_62ac2f531a6e7beccd004.png!small?1655451475378](https://image.3001.net/images/20220617/1655451475_62ac2f531a6e7beccd004.png!small?1655451475378)

可以看到我们传入的参数实际上看着是有判断$()注入情况的。

![1655451479_62ac2f57796195bee5029.png!small?1655451479814](https://image.3001.net/images/20220617/1655451479_62ac2f57796195bee5029.png!small?1655451479814)

最终应该是以下位置的代码导致代码执行，这里$appName/$selectedProgram都来自于攻击者的输入，而这两个参数通过阅读代码可知，$selectedProgram是没有经过$检测的，而$appName有，详细我们可以通过修改脚本日志输出来看看具体的问题。

![1655451486_62ac2f5e15004ecd2127a.png!small?1655451486351](https://image.3001.net/images/20220617/1655451486_62ac2f5e15004ecd2127a.png!small?1655451486351)

通过查询也可知，这里疑似最终代码调用的cmdlet并不能直接通过powershell跑，其只能通过漏洞触发的路径有msdt.exe – >
sdiagnhost.exe->TS_ProgramCompatibilityWizard.ps1 来调用。

![1655451490_62ac2f62edb56f6acc9d8.png!small?1655451491255](https://image.3001.net/images/20220617/1655451490_62ac2f62edb56f6acc9d8.png!small?1655451491255)

当我们需要修改TS_ProgramCompatibilityWizard.ps1脚本进行日志输出的时候发现，无法修改这个文件，这里可以通过修改其对应访问策略来使得其他用户也能修改该文件，从而有助于我们的调试。

首先将selectedProgram获取的值输出，并在selectedProgram经过Test-Selection检测后同样输出，看是否有什么变化。

![1655451497_62ac2f69d0bf2e1472feb.png!small?1655451498341](https://image.3001.net/images/20220617/1655451497_62ac2f69d0bf2e1472feb.png!small?1655451498341)

之后经过while循环后的selectedProgram输出，看有什么变化，同样将关键参数appName输出，看看这里的Replace是否真正起到了过滤的作用。

![1655451502_62ac2f6e597d8dc76f60e.png!small?1655451502691](https://image.3001.net/images/20220617/1655451502_62ac2f6e597d8dc76f60e.png!small?1655451502691)

在关键代码执行前输出appName/selectedProgram这两个参数，并通过注释掉Update-DiagRootCause这行代码来确定真正触发代码执行的位置是否是这里。

![1655451506_62ac2f726de7e6dd1c758.png!small?1655451506772](https://image.3001.net/images/20220617/1655451506_62ac2f726de7e6dd1c758.png!small?1655451506772)

通过测试后发现Update-DiagRootCause这行代码注释后，漏洞无法触发，即该调用导致了最终的代码执行，而其传入的参数日志输出如下所示，可以看到selectedProgram全程都是/../../$(calc).exe，没有经过过滤，而appName经过replace之后的值为$(calc)，并不是我们期待的`$(calc)，那这里到底是appName/selectedProgram导致了代码执行？

![1655451512_62ac2f78efb99b73e86d3.png!small?1655451513375](https://image.3001.net/images/20220617/1655451512_62ac2f78efb99b73e86d3.png!small?1655451513375)

我们尝试对这个两个变量进行控制。

![1655451517_62ac2f7dbb9845e443697.png!small?1655451518147](https://image.3001.net/images/20220617/1655451517_62ac2f7dbb9845e443697.png!small?1655451518147)

如下所示可以看到运行后，二者只要用一个正常，漏洞都能触发，即导致漏洞的是$appName
/$selectedProgram这两个参数，由于对其过滤不严格，从而导致了powershell的代码注入。

![1655451522_62ac2f8238c1878c41d1c.png!small?1655451522803](https://image.3001.net/images/20220617/1655451522_62ac2f8238c1878c41d1c.png!small?1655451522803)

如下所示可以看到gui下的攻击入口其实就是下图的位置

![1655451527_62ac2f87b34fe0a5ec4af.png!small?1655451528004](https://image.3001.net/images/20220617/1655451527_62ac2f87b34fe0a5ec4af.png!small?1655451528004)

这里将其替换为/../../$(calc).exe

![1655451532_62ac2f8c2882212218050.png!small?1655451532446](https://image.3001.net/images/20220617/1655451532_62ac2f8c2882212218050.png!small?1655451532446)

将直接代码执行

![1655451537_62ac2f9136300c62beda4.png!small?1655451537620](https://image.3001.net/images/20220617/1655451537_62ac2f9136300c62beda4.png!small?1655451537620)

该样本通过ole对象拉取恶意html的动作会导致office落地文档直接被查杀。

![1655451542_62ac2f967b64ecfab4be4.png!small?1655451542737](https://image.3001.net/images/20220617/1655451542_62ac2f967b64ecfab4be4.png!small?1655451542737)

  

## 相关yara规则

文档打开后触发下载的html yara规则如下所示，其本身会出现在流量中。

rule CVE30190

{

strings:

$one1 = "PCWDiagnostic" nocase wide ascii

$one2 = "msdt" nocase wide ascii

$one3 = "/id" nocase wide ascii

$one4 = "/skip" nocase wide ascii

$one5 = "force" nocase wide ascii

  

$two1 = "IT_BrowseForFile" nocase wide ascii

$two2 = ")i/../"

  

$three1 = "/Interaction>"

$three2 = "IT_LaunchMethod"

$three3 = "IT_RebrowseForFile"

$three4 = "ContextMenu"

  

condition:

(all of ($one*) and all of ($two*)) or (all of ($three*) and all of ($two*))

}  
  
---  
  
  

## 总结

奇安信红雨滴团队在此提醒广大用户，切勿打开社交媒体分享的来历不明的链接，不点击执行未知来源的邮件附件，不运行夸张标题的未知文件，不安装非正规途径来源的APP。做到及时备份重要文件，更新安装补丁。

若需运行，安装来历不明的应用，可先通过奇安信威胁情报文件深度分析平台（https://sandbox.ti.qianxin.com/sandbox/page）进行判别。目前已支持包括Windows、安卓平台在内的多种格式文件深度分析。

目前，基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、奇安信天狗漏洞攻击防护系统、天擎、天眼高级威胁检测系统、奇安信NGSOC、奇安信态势感知等，都已经支持对此类攻击的精确检测。

![1655451563_62ac2fab52f5dfb2cb36d.png!small?1655451569510](https://image.3001.net/images/20220617/1655451563_62ac2fab52f5dfb2cb36d.png!small?1655451569510)

  

