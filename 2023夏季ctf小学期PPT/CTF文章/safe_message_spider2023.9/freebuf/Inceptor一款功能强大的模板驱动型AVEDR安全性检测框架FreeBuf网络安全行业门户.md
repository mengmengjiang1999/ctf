![](https://image.3001.net/images/20211125/1637813587_619f0d530a63b5f420969.png!small)

## 关于Inceptor

Inceptor是一款功能强大的模板驱动型AV/EDR安全性检测/规避框架，在很多场景中，渗透测试人员或红队研究人员如果想在目标系统上执行代码，通常需要绕过常见的AV/EDR安全防护程序。随着时间的推移和技术的革新，安全防御也变得越来越复杂，从本质上来说，应该是安全防护产品的持续性绕过会变得更加的困难。

因此，Inceptor便应运而生。Inceptor这款工具可以通过自动化的形式实现AV/EDR产品的绕过，可以帮助广大研究人员检测AV/EDR的安全性。

## 功能介绍

Inceptor是一个针对Windows的基于模板的PE封装方法，可以帮助广大渗透测试人员和红队研究人员绕过常见的AV和EDR解决方案。Inceptorr的设计着眼于可用性，并允许用户进行自定义配置或扩展功能。

## Shellcode转换/加载

Inceptor支持通过下列开源转换工具将现有的EXE/DLL转换为Shellcode：

  * [ _Donut_](https://github.com/TheWover/donut)
  * [ _sRDI_](https://github.com/monoxgas/sRDI)
  * [ _Pe2Sh_](https://github.com/hasherezade/pe_to_shellcode)

## 工具运行机制

![](https://image.3001.net/images/20211125/1637813602_619f0d62d55af37c9e349.png!small)

### AV规避机制

Inceptor本身也实现AV规避机制，并且以模块插件的形式将此功能引入到了Payload之中。广大研究人员可以将下列技术嵌入至插件之中：

  * AMSI绕过
  * WLDP绕过
  * ETW绕过
  * 沙盒（行为）欺骗

### EDR规避机制

Inceptor也实现了EDR规避技术，比如卸载事件钩子、直接系统调用和手动DLL映射等等。直接系统调用是通过C#并使用“DInvoke”项目实现的，在C/C++中，系统调用功能是基于“SysWhispers”和“SysWhispers2”项目实现的。除此之外，Inceptor还内置了针对x86系统调用的支持。

EDR规避技术同样可以作为模块来使用，跟AV规避技术在使用上唯一的区别在于EDR规避技术需要在相关的支持模板上操作，当前版本的Inceptor实现了以下几种EDR规避技术：

  * 完全卸载钩子
  * 手动DLL映射
  * 直接系统调用

## Payload混淆

Inceptor还支持使用各种外部工具来对Payload代码进行混淆处理，比如说ConfuserEx和Chameleon等等。除此之外，Inceptor还支持使用LLVM-Obfuscator来对C/C++代码进行混淆处理。当前版本的Inceptor支持以下代码的混淆处理：

  * PowerShell
  * C#
  * C/C++

## 代码签名

Inceptor的另一个功能就是通过使用[
_CarbonCopy_](https://github.com/paranoidninja/CarbonCopy)工具来对生成的代码或DLL文件进行代码签名。一般来说，安全产品对代码签名证书或签名文件的分析和审查都不是非常严格，很多反恶意软件产品都不会对这些证书进行验证。

## 工具安装

Inceptor主要针对的是Windows平台下的用户，我们可以使用项目内的update-config.py脚本来配置所需的微软代码，或对配置进行对应的更新操作。在使用过程中，我们可能需要安装微软构建工具、Windows SDK和Visual
Studio等。工具的下载、安装和配置命令如下所示：

    
    
    git clone --recursive https://github.com/klezVirus/inceptor.git
    cd inceptor
    virtualenv venv
    venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd inceptor
    python update-config.py

## 工具使用

    
    
    $ usage: inceptor.py [-h] [-hh] [-Z] {native,dotnet,powershell} ...
    inceptor: A Windows-based PE Packing framework designed to help
              Red Team Operators to bypass common AV and EDR solutions
    positional arguments:
      {native,dotnet,powershell}
        native              Native Binaries Generator
        dotnet              .NET Binaries Generator
        powershell          PowerShell Wrapper Scripts Generator
    optional arguments:
      -h, --help            show this help message and exit
      -hh                   Show functional table
      -Z, --check           Check file against ThreatCheck

## 项目地址

 **Inceptor：** 【[ _GitHub传送门_](https://github.com/klezVirus/inceptor)】

## 参考资料

  * [ _https://klezvirus.github.io/RedTeaming/AV_Evasion/CodeExeNewDotNet/_](https://klezvirus.github.io/RedTeaming/AV_Evasion/CodeExeNewDotNet/)
  * [ _https://github.com/klezVirus/inceptor/blob/main/slides/Inceptor%20-%20Bypass%20AV-EDR%20solutions%20combining%20well%20known%20techniques.pdf_](https://github.com/klezVirus/inceptor/blob/main/slides/Inceptor%20-%20Bypass%20AV-EDR%20solutions%20combining%20well%20known%20techniques.pdf)
  * [ _https://s3cur3th1ssh1t.github.io/A-tale-of-EDR-bypass-methods_](https://s3cur3th1ssh1t.github.io/A-tale-of-EDR-bypass-methods)

