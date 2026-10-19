**今天给大家介绍的是一款名叫sRDI的注入工具，它可以基于Shellcode实现反射型DLL注入，并能够将DLL转换成独立的Shellcode。**

![11.png](https://image.3001.net/images/20180819/1534684403_5b796cf342336.png!small)

## 工具介绍

sRDI的所有功能基于以下两个组件：

1.一个C语言项目，可将PE Loader编译为Shellcode；

2.转换代码负责将DLL、RDI和用户数据进行绑定。

该项目由以下元素组成：

    
    
    - ShellcodeRDI:编译Shellcode；
    
    -NativeLoader:在必要情况下将DLL转换为Shellcode，并将其注入至内存；
    
    -DotNetLoader:NativeLoader 的C#实现；
    
    -Python\ConvertToShellcode.py:将DLL转换为Shellcode；
    
    -Python\EncodeBlobs.py:对已编译的sRDI进行编码，并实现动态嵌入；
    
    -PowerShell\ConvertTo-Shellcode.ps1:将DLL转换为Shellcode；
    
    -FunctionTest:导入sRDI的C函数，用于调试测试；
    
    -TestDLL:样本Dll，包含两个导出函数，可用于后续的加载和调用；

## 使用样例

在使用该工具之前，我建议大家先对反射型DLL注入有一个基本了解，可以先阅读一下【[这篇文章](https://disman.tl/2015/01/30/an-improved-reflective-dll-injection-technique.html)】。

使用Python将DLL转换为Shellcode：

    
    
    from ShellcodeRDI import *
    
    dll =open("TestDLL_x86.dll", 'rb').read()
    
    shellcode= ConvertToShellcode(dll)

使用C#加载器将DLL加载进内存：

    
    
    DotNetLoader.exe TestDLL_x64.dll

使用Python脚本转换DLL，并用NativeLoader完成加载：

    
    
    python ConvertToShellcode.py TestDLL_x64.dll
    
    NativeLoader.exe TestDLL_x64.bin

使用PowerShell转换DLL，并用Invoke-Shellcode完成加载：

    
    
    Import-Module.\Invoke-Shellcode.ps1
    
    Import-Module.\ConvertTo-Shellcode.ps1
    
    Invoke-Shellcode-Shellcode (ConvertTo-Shellcode -File TestDLL_x64.dll)

## 工具隐蔽性

目前社区有多种方法可检测内存注入，加载功能实现了两种增强隐蔽性的方法：

1.适当的权限：在对内存空间进行定位时，工具会根据内存区域的特征来设置内存权限；

2.PEHeader清理（可选）：目标DLL的DOS Header和DOS
Stub会在加载完成之后被清空为NULL字节，这一步可通过C/C#代码，或命令行参数（Python或PowerShell）来实现。

### 工具构建

本项目采用Visual Studio 2015（V140）和Windows SDK 8.1构建，Python脚本基于Python
3开发，Python和Powershell脚本位于：

    
    
    Python\ConvertToShellcode.py
    
    PowerShell\ConvertTo-Shellcode.ps1

项目构建完成之后，可在下列位置找到其他组件代码：

    
    
    bin\NativeLoader.exe
    
    bin\DotNetLoader.exe
    
    bin\TestDLL_.dll
    
    bin\ShellcodeRDI_.bin

### 使用到的其他项目

本项目用于将C代码编译为Shellcode时所采用的项目框架为Mathew
Graeber的PIC_BindShell：【[传送门](http://www.exploit-monday.com/2013/08/writing-optimized-windows-shellcode-in-c.html)】

Python脚本中的代码解析模块采用的是PEFile项目：【[传送门](https://github.com/erocarrera/pefile)】

***参考来源：[sRDI](https://github.com/monoxgas/sRDI)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

