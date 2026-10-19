## 关于PersistBOF

PersistBOF是一款针对Windows系统安全的持久化工具，该工具能够以自动化的形式实现常见的持久化技术。当前版本的PersistBOF支持Print
Monitor（系统服务）、Time Provider（网络服务）和启动目录快捷方式劫持（用户服务）等。

PersistBOF所实现的所有技术都依赖于一个DLL文件，这个DLL文件会以分布式的形式存储到目标系统 磁盘中。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/IcebreakerSecurity/PersistBOF.git

接下来，我们需要切换到项目目录，并运行make命令来构建源码：

    
    
    make

最后，将生成的.cna文件添加到Cobalt Strike客户端即可。

 **参考语句：**

    
    
    persist-ice [PrintMon, TimeProv, Shortcut] [persist or clean] [key/folder name] [dll / lnk exe name];

![](https://image.3001.net/images/20220610/1654798047_62a236dfa2424b6147b0e.jpeg!small)

## 工具使用

### Print Monitor

工具所使用的DLL文件必须要存储在目标设备磁盘中，而且必须要在BOF运行之前在PATH环境变量中设置好DLL的路径位置（DLL搜索顺序），否则将无法正常实现持久化。

这种方式可以将管理员权限提升至SYSTEM权限，并实现持久化。

 **PrintMonitorDll使用样例：**

> 1、将NotMalware.dll上传到C:\Windows\NotMalware.dll；
>
> 2、NotMalware.dll将通过PrintMon以TotesLegitMonitor来实现持久化；
>
> 3、程序将立即以SYSTEM权限执行；
>
> 4、程序会在系统启动时自动执行；

### Time Provider

运行了PersistBOF之后，程序将通过svchost.exe以NETWORK SERVICE的形式在系统启动时执行。

 **TimeProvider使用样例：**

> 工具使用TimeProv并通过TotesLegitTimeProvider实现持久化（C:\anywhere\NotMalware.dll）；

### 启动目录劫持

创建一个新的、用户可写的目录，然后将可劫持的Windows代码拷贝到该目录中，并在启动目录中创建一个指向该文件的快捷方式。最后，该程序将会在用户登录时执行。

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/IcebreakerSecurity/PersistBOF/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **PersistBOF：** 【[
_GitHub传送门_](https://github.com/IcebreakerSecurity/PersistBOF)】

## 参考资料

> [ _https://stmxcsr.com/persistence/print-> monitor.html_](https://stmxcsr.com/persistence/print-monitor.html)
>
> [ _https://stmxcsr.com/persistence/time-> provider.html_](https://stmxcsr.com/persistence/time-provider.html)
>
> [ _https://pentestlab.blog/2019/10/28/persistence-port-> monitors/_](https://pentestlab.blog/2019/10/28/persistence-port-monitors/)
>
> [ _https://blog.f-secure.com/hunting-for-junction-folder-> persistence/_](https://blog.f-secure.com/hunting-for-junction-folder-> persistence/)
>
> [
> _https://attack.mitre.org/techniques/T1547/010/_](https://attack.mitre.org/techniques/T1547/010/)
>
> [
> _https://attack.mitre.org/techniques/T1547/003/_](https://attack.mitre.org/techniques/T1547/003/)
>
> [
> _https://attack.mitre.org/techniques/T1547/009/_](https://attack.mitre.org/techniques/T1547/009/)

