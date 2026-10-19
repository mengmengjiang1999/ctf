微软支持诊断工具（MSDT，MicrosoftSupport Diagnostic
Tool）是一种实用程序，用于排除故障并收集诊断数据，供专业人员分析和解决问题。当从调用应用程序（例如Word）使用
URL协议调用MSDT时，存在远程代码执行漏洞。成功利用此漏洞的攻击者可以使用调用应用程序的权限运行任意代码。

## Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 有  
  
## Part2 漏洞描述

‍漏洞名称|

Microsoft Windows诊断工具 (MSDT) 远程代码执行漏洞  
  
---|---  
CVE编号| CVE-2022-30190  
漏洞类型| 任意代码执行  
漏洞等级| 7.8高危（HIGH）  
公开状态| 公开  
漏洞描述|

使用URL协议调用MSDT时，可通过构造特殊网页，做到远程代码执行。  
  
时间线|

2022-5-30 Microsoft发布

2022-5-31 JohnHammond 公开PoC

2022-6-14 发布更新补丁  
  
受影响版本  
  
|

未安装相关补丁，或使用缓解措施的:

Win7至Win11

Windows Server2008至2022  
  
 **分析环境：**

kali

Win10 19041

Office 2016

## Part3 漏洞复现

开启web服务并创建.doc文档。

![图片](https://image.3001.net/images/20230518/1684394576_6465d250bf832127b1e0c.jpg!small)

将生成的文档拷贝至靶机打开，靶机出现windows诊断工具，并运行计算器

![图片](https://image.3001.net/images/20230518/1684394587_6465d25b097cd9414a8dd.jpg!small)

查看进程树，WINWORD启动msdt.exe，命令行为"msdt.exe ms-msdt:/id PCWDiagnostic /skip force
/param "IT_RebrowseForFile=? IT_LaunchMethod=ContextMenu
IT_BrowseForFile=$("要执行的程序")。

msdt.exe是windows支持诊断工具，作用为自动诊断并修正各种windows功能的常见问题。

![图片](https://image.3001.net/images/20230518/1684394597_6465d265688eb55bc9114.jpg!small)

![图片](https://image.3001.net/images/20230518/1684394606_6465d26ee16fd9b94f3d8.jpg!small)

msdt使用WTP框架，会根据不同参数，使用sdiagnhost提供的接口，通过powershell作出处理。

![图片](https://image.3001.net/images/20230518/1684394618_6465d27abe2ced41f7242.jpg!small)

最终计算器被sdiagnhost.exe启动。

![图片](https://image.3001.net/images/20230518/1684394628_6465d28415a90b3ecf352.jpg!small)

在文档内的关系文件document.xml.rels中，可见指向外部链接的对象。

![图片](https://image.3001.net/images/20230518/1684394637_6465d28da229a8648c312.jpg!small)

查看index.html，利用ms-msdt协议，执行程序，并包含一段长度为4098的注释。

![图片](https://image.3001.net/images/20230518/1684394648_6465d298a14d7f2c6e165.png!small)

分析sdiagnhost，在CScriptedDiagNativeHost::RunScript函数内，出现要使用的powershell脚本路径。

![图片](https://image.3001.net/images/20230518/1684394660_6465d2a44389fb7d7894f.jpg!small)

powershell脚本的运行时环境，由Microsoft.Windows.Diagnosis.SDHost.dll提供，通过调试，RunScript()被调用了两次，分别为使用TS_ProgramCompatibilityWizard.ps1和RS_ProgramCompatibilityWizard.ps1脚本。

![图片](https://image.3001.net/images/20230518/1684394679_6465d2b7c2c405cf08b45.jpg!small)

在执行RS_ProgramCompatibilityWizard.ps1脚本时，包含传入的参数。

![图片](https://image.3001.net/images/20230518/1684394688_6465d2c03f1f9e3a128df.jpg!small)

在TS_ProgramCompatibilityWizard.ps1内，会获取传入的IT_BrowseForFile，并通过Test-Selection()检测。

![图片](https://image.3001.net/images/20230518/1684394697_6465d2c933759ee217621.jpg!small)

在Test-Selection()内，会对参数进行检测，使用test-path检测路径是否存在，并且参数后缀为".exe"或".msi"。

但只要传入路径在根目录外时(如/../../calc.exe)，test-path便会返回true。

![图片](https://image.3001.net/images/20230518/1684394707_6465d2d3ca5367e111af8.jpg!small)

检测通过后，会使用Update-DiagRootCause，再次调用RunScript()执行RS_ProgramCompatibilityWizard.ps1脚本，运行参数内目标的程序。

![图片](https://image.3001.net/images/20230518/1684394716_6465d2dc2414bca081e8f.jpg!small)

也可将文件保存为rft格式，在使用文件预览的情况下，无需打开文件即可触发漏洞。

![图片](https://image.3001.net/images/20230518/1684394724_6465d2e4613d0ee495ece.jpg!small)

## Part4 修复建议

按照微软给出的缓解措施进行操作，禁用msdt url协议。

https://msrc.microsoft.com/blog/2022/05/guidance-for-cve-2022-30190-microsoft-support-diagnostic-tool-vulnerability/

或根据系统安装链接内相应补丁。

