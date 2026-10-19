![](https://image.3001.net/images/20210522/1621664561_60a8a3318efcf3e18a227.png!small)

## 关于CIMplant

CIMplant是WMImplant项目的C#实现，并扩展了原项目的相关功能，该工具
能够使用CIM或WMI来查询远程系统，并且可以使用用户提供的凭据或当前用户的会话来执行操作。

注意：某些命令仍然会使用PowerShell与WMI结合的方式来实现。

CIMplant使用了C#对[ _@christruncer_](https://twitter.com/christruncer)的[
_WMImplant_](https://github.com/FortyNorthSecurity/WMImplant)项目进行了重写和功能扩展，可以帮助广大研究人员从远程系统中收集数据、执行命令以及提取数据等等。该工具允许使用[
_WMI_](https://docs.microsoft.com/en-us/windows/win32/wmisdk/about-wmi)或[
_CIM_](https://www.dmtf.org/standards/cim)来进行连接，并且需要目标系统中中的本地管理员权限来执行任务操作。

## 工具安装

为了方便起见，广大研究人员可以直接访问该项目的【[
_Releases页面_](https://github.com/FortyNorthSecurity/CIMplant/releases)】来获取最新的构建版本，如果你想要手动构建的话，请参照下列步骤：

> 在Visual Studio中加载sln；
>
> 点击顶部菜单中的“Build”，然后选择构建解决方案；

## 工具使用

    
    
    CIMplant.exe --help
    
    CIMplant.exe --show-commands
    
    CIMplant.exe --show-examples
    
    CIMplant.exe -s [remote IP address] -c cat -f c:\users\user\desktop\file.txt
    
    CIMplant.exe -s [remote IP address] -u [username] -d [domain] -p [password] -c cat -f c:\users\test\desktop\file.txt
    
    CIMplant.exe -s [remote IP address] -u [username] -d [domain] -p [password] -c command_exec --execute "dir c:\\"

## 工具使用演示

 **查看命令选项：**
【[点我查看](https://raw.githubusercontent.com/FortyNorthSecurity/CIMplant/main/Extras/CIMplant-Help.gif)】

 **命令执行样例：**
【[点我查看](https://raw.githubusercontent.com/FortyNorthSecurity/CIMplant/main/Extras/CIMplant-Usage.gif)】

## 重要文件

> cs：该文件是工具的核心文件，负责驱动整个工具的运行。
>
> cs：该文件负责初始化CIM/WMI连接，并将连接传递给应用程序进行后续操作。
>
> cs：包含了WMI命令中的所有函数代码。
>
> cs：包含了CIM(IM)命令中的所有函数代码。

## 安全检测解决方案

当然，我们首先要注意的是初始的WMI或CIM连接。通常，WMI使用DCOM作为通信协议，而CIM使用的是WSMan（或WinRM）。对于DCOM，我们可以做的第一件事是通过端口135寻找初始TCP连接。然后，连接和接收系统将决定使用一个新的端口。对于WSMan，初始TCP连接使用的是端口5985。

接下来，你需要在事件查看器中查看Microsoft Windows WMI活动/跟踪事件日志。如果可能，搜索事件ID
11并在IsLocal属性上进行筛选。你还可以在Microsoft Windows WinRM/分析日志中查找事件ID 1295。

最后，你需要使用Win32_OSRecoveryConfiguration类查找对DebugFilePath属性的任何修改。

## 项目地址

CIMplant：【[ _GitHub传送门_](https://github.com/FortyNorthSecurity/CIMplant)】

## 参考资料

[ _https://fortynorthsecurity.com/blog/cimplant-part-1-detections/_](https://fortynorthsecurity.com/blog/cimplant-part-1-detections/)

[
_https://github.com/FortyNorthSecurity/WMImplant_](https://github.com/FortyNorthSecurity/WMImplant)

[ _https://docs.microsoft.com/en-us/windows/win32/wmisdk/about-wmi_](https://docs.microsoft.com/en-us/windows/win32/wmisdk/about-wmi)

[ _https://www.dmtf.org/standards/cim_](https://www.dmtf.org/standards/cim)

