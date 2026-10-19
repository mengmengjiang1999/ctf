![](https://image.3001.net/images/20221227/1672137502_63aacb1eb55ce645ad508.png!small)

## 关于NetLlix

NetLlix是一款功能强大的数据过滤工具，在该工具的帮助下，广大研究人员可以通过不同的网络协议来模拟和测试数据过滤。该工具支持在不使用本地API（应用程序编程接口）的情况下执行数据的模拟写入/输出。

值得一提的是，该工具可以有效地帮助蓝队安全人员编写相关的规则，以检测任何类型的C2通信或数据泄漏。

## 工具机制

当前版本的NetLlix能够使用下列编程/脚本语言来生成HTTP/HTTPS流量（包含GET和POST）：

> 1、CNet/WebClient：基于CLang开发，使用了著名的WIN32 API（WININET &
> WINHTTP）和原始Socket编程来生成网络流量；
>
>
> 2、HashNet/WebClient：一个使用了.NET类的C#代码，可以生成网络流量，类似HttpClient、WebRequest和原始Socket；
>
> 3、PowerNet/WebClient：一个PowerShell脚本，使用了Socket编程来生成网络流量；

![](https://image.3001.net/images/20221227/1672137522_63aacb32e0bee4aca724f.png!small)

## 工具下载

在使用该工具之前，请先在本地设备上安装并配置好Python 3环境。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/advanced-threat-research/NetLlix.git

除此之外，我们也可以直接访问该项目的【[ _Releases页面_](https://github.com/advanced-threat-research/NetLlix/releases/tag/V0.1)】下载最新版本的NetLlix。

## 工具使用

### 服务器运行

使用SSL运行：

    
    
    python3 HTTP-S-EXFIL.py ssl

不使用SSL运行：

    
    
    python3 HTTP-S-EXFIL.py

### 客户端运行

CNet（选择任意选项）：

    
    
    CNet.exe <Server-IP-ADDRESS>

HashNet（选择任意选项）：

    
    
    ChashNet.exe <Server-IP-ADDRESS>

PowerNet：

    
    
    .\PowerHttp.ps1 -ip <Server-IP-ADDRESS> -port <80/443> -method <GET/POST>

## 许可证协议

本项目的开发与发布遵循[ _Apache_ _-2.0_](https://github.com/advanced-threat-research/NetLlix/blob/main/LICENSE.txt)开源许可证协议。

## 项目地址

 **NetLlix** ：【[ _GitHub传送门_](https://github.com/advanced-threat-research/NetLlix)】

