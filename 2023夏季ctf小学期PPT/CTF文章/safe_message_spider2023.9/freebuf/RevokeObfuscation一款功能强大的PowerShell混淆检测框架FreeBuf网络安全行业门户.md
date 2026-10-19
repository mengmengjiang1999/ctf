![](https://image.3001.net/images/20230420/1681922791_64401ae72df6a860c64dd.png!small)  

## 关于Revoke-Obfuscation

Revoke-Obfuscation是一款功能强大的PowerShell混淆检测框架，该框架基于PowerShell开发，并且兼容PowerShell
v3.0+脚本。在该工具的帮助下，广大研究人员可以轻松实现大规模的PowerShell命令或脚本的混淆检测。

它依靠PowerShell的AST（抽象语法树）从任何输入的PowerShell脚本中快速提取数千个特征，并将该特征向量与一个包含了40多万个PowerShell脚本的[
_语料库_](https://aka.ms/PowerShellCorpus)进行计算和对比。

## 工作机制

由于Revoke-Obfuscation依赖于特征提取和比较，而不是纯粹的IOC或RegEx匹配，因此它在识别未知模糊技术的能力方面更为强大，即使攻击者试图通过填充未经模糊的脚本内容来推翻字符频率分析等基本检查来抑制其模糊，也难逃Revoke-Obfuscation的法眼。

Revoke-Obfuscation可以在100-300毫秒内轻松检测大多数输入的PowerShell脚本。而且Revoke-Obfuscation支持支持简单的白名单功能，并且能够提取PowerShell操作事件日志记录。

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/danielbohannon/Revoke-Obfuscation.git

接下来，切换到项目目录中，运行下列命令完成安装：

    
    
    Import-Module .\Revoke-Obfuscation.psd1

除此之外，我们也可以直接从PowerShell Gallery来安装Revoke-Obfuscation：

    
    
    Install-Module Revoke-Obfuscation
    
    Import-Module Revoke-Obfuscation

## 工具使用

下列命令可以针对EID 4104脚本块日志执行分析检测：

    
    
    Get-RvoScriptBlock -Path 'C:\Windows\System32\Winevt\Logs\Microsoft-Windows-PowerShell%4Operational.evtx' -Verbose
    
    Get-ChildItem .\Demo\demo.evtx | Get-RvoScriptBlock -Verbose
    
    Get-WinEvent -LogName Microsoft-Windows-PowerShell/Operational | Get-RvoScriptBlock -Verbose

下列命令可以针对demo.evtx中的数据记录执行完整检测：

    
    
    $obfResults = Get-WinEvent -Path .\Demo\demo.evtx | Get-RvoScriptBlock | Measure-RvoObfuscation -OutputToDisk -Verbose

下列命令可以对本地或远程托管的测试脚本执行检测：

    
    
    Measure-RvoObfuscation -Url 'http://bit.ly/DBOdemo1' -Verbose -OutputToDisk
    
    Get-Content .\Demo\DBOdemo*.ps1 | Measure-RvoObfuscation -Verbose -OutputToDisk
    
    Get-ChildItem .\Demo\DBOdemo*.ps1 | Measure-RvoObfuscation -Verbose -OutputToDisk

## 工具运行截图

![](https://image.3001.net/images/20230420/1681922860_64401b2ca8876cad61484.png!small)

## 工具使用演示

![](https://image.3001.net/images/20230420/1681922886_64401b465e5ba126adc3d.gif)

## 许可证协议

本项目的开发与发布遵循[ _Apache_ _-2_ _._ _0_](https://github.com/danielbohannon/Revoke-Obfuscation/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Revoke-Obfuscation** ：【[
_GitHub传送门_](https://github.com/danielbohannon/Revoke-Obfuscation)】

## 参考资料

> [ _https://www.fireeye.com/blog/threat-research/2017/07/revoke-obfuscation-> powershell.html_](https://www.fireeye.com/blog/threat-> research/2017/07/revoke-obfuscation-powershell.html)
>
> [ _https://www.fireeye.com/content/dam/fireeye-www/blog/pdfs/revoke-> obfuscation-report.pdf_](https://www.fireeye.com/content/dam/fireeye-> www/blog/pdfs/revoke-obfuscation-report.pdf)
>
> [ _https://aka.ms/PowerShellCorpus_](https://aka.ms/PowerShellCorpus)

