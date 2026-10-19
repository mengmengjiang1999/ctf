## 前言

本文来源于深圳网安检测关保团队核心成员编写。

## 介绍IFEO

其中文名字：映像劫持。

英文全名：Image File Execution Options。

缩写：IFEO。

IFEO 是一项允许操作人员将调试器附加到应用程序/进程的功能。这将导致我们可以将我们要运行的程序隐藏在平日里运行的程序中，如打开笔记本等。

## 如何设置IFEO

1、使用注册表；

2、使用 GFlags 工具。

## 直接调用

我们在HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution
Options\创建一个注册表项，它是我们要为其附加调试器的进程的名称。以下示例为
notepad.exe，其中Debugger的值为calc.exe，即它的调试器将是 calc.exe。

我们将添加一个名为 notepad.exe 的项，如下：

![1645801680_6218f0d09e29d7068c2ef.png!small?1645801679219](https://image.3001.net/images/20220225/1645801680_6218f0d09e29d7068c2ef.png!small?1645801679219)

设置Debugger的值为calc.exe。

![1645801691_6218f0db454b4774f37c8.png!small?1645801689843](https://image.3001.net/images/20220225/1645801691_6218f0db454b4774f37c8.png!small?1645801689843)

Debugger 现在是 calc.exe，我们设置的是每当我们打开notepad.exe ，就会执行调试器“calc.exe”。如下图：

![1645801709_6218f0ed9a4bbc1d12aba.png!small?1645801708212](https://image.3001.net/images/20220225/1645801709_6218f0ed9a4bbc1d12aba.png!small?1645801708212)

也可以使用命令直接调用添加。

> reg add "hklm\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File
> Execution Options\notepad.exe" /v debugger /t REG_SZ /d
> "c:\windows\system32\calc.exe"

![1645801755_6218f11b27f4dabac0aed.png!small?1645801753807](https://image.3001.net/images/20220225/1645801755_6218f11b27f4dabac0aed.png!small?1645801753807)

## 二次调用

二次调用相对直接调用更加隐秘，也不易被察觉，我们将设置一旦 notepad.exe 静默退出，我们将运行我们指定的程序。首先，我们将通过在 IFEO 键下的
notepad.exe 键中添加十六进制值为 200 的 GlobalFlag 名称来启用静默进程退出监控。

![1645801772_6218f12c9b2ee1fb24456.png!small?1645801771209](https://image.3001.net/images/20220225/1645801772_6218f12c9b2ee1fb24456.png!small?1645801771209)

我们将在 CurrentVersion 下创建 SilentProcessExit 键，并在此键下添加名为 notepad.exe 的子键，通过将
MonitorProcess 的值添​​加为 calc.exe，并将 ReportingMode 添加为 1，1表示失败。现在 notepad.exe
的每次静默退出都会触发 calc.exe 运行。

![1645801784_6218f138704b67fc405be.png!small?1645801783114](https://image.3001.net/images/20220225/1645801784_6218f138704b67fc405be.png!small?1645801783114)

![1645801792_6218f140b67031cf51350.png!small?1645801791334](https://image.3001.net/images/20220225/1645801792_6218f140b67031cf51350.png!small?1645801791334)

当退出notepad程序时候，calc.exe被执行。

![1645801799_6218f14749f0ebbe37881.png!small?1645801797930](https://image.3001.net/images/20220225/1645801799_6218f14749f0ebbe37881.png!small?1645801797930)

二次调用的命令：

> reg add "hklm\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File
> Execution
>
> Options\notepad.exe" /v GlobalFlag /t REG_DWORD /d "512"
>
> reg add "hklm\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File
> Execution
>
> Options\SilentProcessExit\notepad.exe" /v MonitorProcess /t REG_SZ /d
> "calc.exe"
>
> reg add "hklm\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File
> Execution
>
> Options\SilentProcessExit\notepad.exe" /v ReportingMode /t REG_DWORD /d "1"

![1645801844_6218f174920ebb455aaca.png!small?1645801843243](https://image.3001.net/images/20220225/1645801844_6218f174920ebb455aaca.png!small?1645801843243)

关闭记事本。

![1645801850_6218f17af328a604cf790.png!small?1645801849561](https://image.3001.net/images/20220225/1645801850_6218f17af328a604cf790.png!small?1645801849561)

计算器弹出。

![1645801856_6218f1807f7ee2815c8a4.png!small?1645801855129](https://image.3001.net/images/20220225/1645801856_6218f1807f7ee2815c8a4.png!small?1645801855129)

上线cs也是没有问题的。

![1645801863_6218f187397bc2d1f1811.png!small?1645801861801](https://image.3001.net/images/20220225/1645801863_6218f187397bc2d1f1811.png!small?1645801861801)

关闭记事本后，调用的程序是直接在后台运行，不易察觉。

![1645801868_6218f18cd551c7ce9cfb8.png!small?1645801867557](https://image.3001.net/images/20220225/1645801868_6218f18cd551c7ce9cfb8.png!small?1645801867557)

## 应急排查

1、排查CurrentVersion\Image File Execution Options
以及CurrentVersion\SilentProcessExit项值是否存在关联。

> reg query "hklm\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File
> Executi
>
> on Options"

![1645801897_6218f1a9dfb84945dfab3.png!small?1645801896693](https://image.3001.net/images/20220225/1645801897_6218f1a9dfb84945dfab3.png!small?1645801896693)

2、分析系统日志ID为3000和3001，异常退出，可能存在后门威胁。

![1645801908_6218f1b40dcf0a5519018.png!small?1645801906667](https://image.3001.net/images/20220225/1645801908_6218f1b40dcf0a5519018.png!small?1645801906667)

3、直接删除IFEO项或者设置管理员不可修改。

