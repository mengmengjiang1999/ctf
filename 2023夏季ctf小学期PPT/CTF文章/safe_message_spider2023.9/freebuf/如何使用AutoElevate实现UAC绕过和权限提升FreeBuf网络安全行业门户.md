## 关于Auto-Elevate

Auto-Elevate是一款功能强大的Windows系统安全测试工具，该工具可以在不需要离邕任何LPE漏洞的 情况下，通过结合COM
UAC绕过技术和令牌伪造技术，帮助广大研究人员将低完整性的管理员账号提升至NT AUTHORITY\SYSTEM。

该工具能够实现UAC以及其他一些Windows内置功能的绕过，该工具能够自动定位winlogon.exe，并能够窃取和模拟该程序的进程令牌，然后使用窃取来的令牌生成一个新的系统级进程。

值得一提的是，该工具结合了UACME实用工具的UAC绕过技术，感兴趣的同学可以搜索了解该工具所实现的ICMLuaUtil UAC绕过方法（#41）。

## 技术介绍

该工具是一款功能强大的提权和系统安全测试工具，下图显示的是Auto-Elevate将一个低等级权限的管理员账号提升为SYSTEM的步骤流程：

![](https://image.3001.net/images/20220413/1649863584_6256eba0142ce1d3f09d9.png!small)

## 工具运行流程

>
> 1、工具通过使用CreateToolhelp32Snapshot、Process32First和Process32Next来枚举目标系统中正在运行的进程以查找定位winlogon.exe；
>
>
> 2、通过调用AdjustTokenPrivileges来为当前进程启动SeDebugPrivilege，因为我们需要为winlogon.exe开启一个句柄；
>
> 3、通过调用OpenProcess来打开一个winlogon.exe进程句柄，此时将会调用到PROCESS_ALL_ACCESS；
>
> 4、工具将通过调用OpenProcessToken并结合之前获得的进程句柄来检索winlogon的进程令牌句柄；
>
> 5、通过调用ImpersonateLoggedOnUser来伪造winlogon用户；
>
> 6、通过使用SecurityImpersonation来调用DuplicateTokenEx并复制伪造的令牌句柄，这将创建一个我们可以使用的令牌副本；
>
> 7、在令牌副本的帮助下，我们就可以通过调用CreateProcessWithTokenW来生成一个新的CMD实例了；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/FULLSHADE/Auto-Elevate.git

接下来，将.cpp文件导入到Visual Studio中编译后即可直接使用。

## 工具使用

下图中演示了如何在Windows 10 21H1操作系统平台上，使用UACME结合Auto-Elevate来将一个低等级权限的管理员账号提升为NT
AUTHORITY\SYSTEM：

![](https://image.3001.net/images/20220413/1649863628_6256ebcce6dd3d2e29b12.png!small)

下图演示了如何在不使用UAC绕过技术的情况下，将一个高低等级权限的管理员账号提权为SYSTEM：

![](https://image.3001.net/images/20220413/1649863635_6256ebd3d0a3cb75dad72.png!small)

## 项目地址

 **Auto-Elevate：** 【[ _GitHub传送门_](https://github.com/FULLSHADE/Auto-Elevate)】

## 参考资料

> [
> _https://attack.mitre.org/techniques/T1134/_](https://attack.mitre.org/techniques/T1134/)
>
> [
> _https://attack.mitre.org/techniques/T1134/001/_](https://attack.mitre.org/techniques/T1134/001/)
>
> [
> _https://attack.mitre.org/techniques/T1134/002/_](https://attack.mitre.org/techniques/T1134/002/)
>
> [
> _https://attack.mitre.org/techniques/T1134/003/_](https://attack.mitre.org/techniques/T1134/003/)

