## 前言

 **clrinject是一款可将C＃，EXE或DLL程序集，注入另一个进程CLR
Runtimes和AppDomain的工具。注入的程序集可访问injectee进程类的静态实例，从而影响其内部状态。**

## 使用

    
    
    clrinject-cli.exe -p <processId/processName> -a <assemblyFile>

打开id为<processId>或名称为<processName>的进程，注入<assemblyFile> EXE并执行Main方法。

### 其他选项

    
    
    -e：枚举所有已加载的CLR Runtimes时和创建的AppDomain。
    
    
    -d <#>：仅注入<#> -th AppDomain。如果未指定数字或指定为零，则会将程序集注入到所有AppDomain。
    
    
    -i <namespace>.<className>：从命名空间<namespace>创建类<className>的实例。

## 示例

### 使用示例

从victim.exe枚举Runtimes和AppDomains：

    
    
    clrinject-cli.exe -p victim.exe -e

将invader.exe从id为1234的进程注入第二个AppDomain：

    
    
    clrinject-cli.exe -p 1234 -a "C:\Path\To\invader.exe" -d 2

在victim.exe中的每个AppDomain中创建Invader实例：

    
    
    clrinject-cli.exe -p victim.exe -a "C:\Path\To\invader.dll" -i "Invader.Invader"

将x64程序集注入x64进程：

    
    
    clrinject-cli64.exe -p victim64.exe -a "C:\Path\To\invader64.exe"

### 可注入程序集示例

以下代码可编译为C#可执行文件，然后注入到一个PowerShell进程。这段代码将会访问内部PowerShell类的静态实例，并将控制台文本的颜色更改为绿色。

    
    
    using System;
    using System.Reflection;
    
    using Microsoft.PowerShell;
    using System.Management.Automation.Host;
    
    namespace Invader
    {
        class Invader
        {
            static void Main(string[] args)
            {
                try
                {
                    var powerShellAssembly = typeof(ConsoleShell).Assembly;
                    var consoleHostType = powerShellAssembly.GetType("Microsoft.PowerShell.ConsoleHost");
                    var consoleHost = consoleHostType.GetProperty("SingletonInstance", BindingFlags.Static | BindingFlags.NonPublic).GetValue(null);
    
                    var ui = (PSHostUserInterface)consoleHostType.GetProperty("UI").GetValue(consoleHost);
                    ui.RawUI.ForegroundColor = ConsoleColor.Green;
                }
                catch (Exception e)
                {
                    Console.WriteLine(e.ToString());
                }
            }
        }
    }

注入命令：

    
    
    clrinject-cli64.exe -p powershell.exe -a "C:\Path\To\invader64.exe"

结果：

![界面](https://image.3001.net/images/20181025/1540423571_5bd0ff93f01d0.png!small)

***参考来源：[github](https://github.com/jonatan1024/clrinject)，FB小编secist编译，转载请注明来自FreeBuf.COM**

