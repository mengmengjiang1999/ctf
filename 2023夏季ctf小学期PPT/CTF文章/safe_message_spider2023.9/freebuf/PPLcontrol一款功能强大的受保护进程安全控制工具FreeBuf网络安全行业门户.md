![](https://image.3001.net/images/20230824/1692883441_64e759f17e3762c8d4a0e.png!small)  

## 关于PPLcontrol

PPLcontrol是一款功能强大的受保护进程安全控制工具，在该工具的帮助下，广大研究人员可以快速枚举出目标操作系统中受保护的进程，并获取指定进程的保护级别，或给目标进程设置任意保护级别。

## 工具下载

该工具基于C++开发，因此我们首先需要在本地设备上完成C++环境及代码构建工具的安装与配置，例如Visual Studio等。

广大研究人员可以使用下列命令将该项目源码克隆至本地，并手动完成代码构建：

    
    
    git clone https://github.com/itm4n/PPLcontrol.git

## 代码构建

> 1、在Visual Studio中打开工具的解决方案.sln文件；
>
> 2、选择Release/x64（该工具不支持x86）；
>
> 3、构建当前解决方案即可；

## 工具使用

### 1、下载MSI驱动程序

我们可以点击【[
_这里_](https://github.com/RedCursorSecurityConsulting/PPLKiller/tree/master/driver)】获取MSI驱动程序RTCore64.sys文件。

### 2、安装MSI驱动程序

注意事项：千万不要直接在你自己的本地主机中安装该驱动程序，请一定要使用虚拟机！！！

    
    
    sc.exe create RTCore64 type= kernel start= auto binPath= C:\PATH\TO\RTCore64.sys DisplayName= "Micro - Star MSI Afterburner"
    
    net start RTCore64

### 3、使用PPLcontrol

枚举受保护的进程：

    
    
    PPLcontrol.exe list

获取指定进程的保护级别：

    
    
    PPLcontrol.exe get 1234

给目标进程设置任意保护级别：

    
    
    PPLcontrol.exe set 1234 PPL WinTcb

保护一个未受保护的进程，并设置任意保护级别。此时将会自动调整相应的签名等级：

    
    
    PPLcontrol.exe protect 1234 PPL WinTcb

让一个受保护进程取消保护，此时会将保护级别设置为0，并将EXE/DLL签名等级设置为0:

    
    
    PPLcontrol.exe unprotect 1234

### 4、卸载驱动程序

    
    
    net stop RTCore64
    
    sc.exe delete RTCore64

## 工具使用样例

### 使用WinDbg调试一个受保护进程

WinDbg只需要打开目标进程，因此我们可以使用PPLcontrol来给windbg.exe进程设置任意的保护级别：

1、获取windbg.exe进程的进程ID，即PID；

2、使用PPLcontrol设置任意保护级别；

    
    
    C:\Temp>tasklist | findstr /i windbg
    
    windbg.exe                    1232 Console                    1     24,840 K
    
    C:\Temp>PPLcontrol.exe protect 1232 PPL WinTcb
    
    [+] The Protection 'PPL-WinTcb' was set on the process with PID 1232, previous protection was: 'None-None'.
    
    [+] The Signature level 'WindowsTcb' and the Section signature level 'Windows' were set on the process with PID 1232.

### 使用API Monitor（API监控工具）审查一个受保护的进程

除了打开目标进程外，API
Monitor还会向其中注入DLL。因此，在apimonitor.exe进程上设置任意保护级别是不够的。由于注入的DLL没有正确的签名，因此目标进程的Section签名标志可能会阻止加载它。但是，我们可以暂时禁用目标进程上的保护，然后在监控完成后恢复保护即可。

    
    
    Failed to load module in target process - Error: 577, Windows cannot verify the digital signature for this file. A recent hardware or software change might have installed a file that is signed incorrectly or damaged, or that might be malicious software from an unknown source.

> 1、获取目标进程的进程ID，即PID；
>
> 2、使用PPLcontrol获取目标进程的保护级别；
>
> 3、取消进程保护；
>
> 4、使用API Monitor对进程执行监控；
>
> 5、恢复目标进程的保护；
    
    
    C:\Temp>tasklist | findstr /i target
    
    target.exe                    1337 Services                   1     14,160 K
    
    C:\Temp>PPLcontrol.exe get 1337
    
    [+] The process with PID 1337 is a PPL with the Signer type 'WinTcb' (6).
    
    C:\Temp>PPLcontrol.exe unprotect 1337
    
    [+] The process with PID 1337 is no longer a PP(L).
    
     
    
    C:\Temp>PPLcontrol.exe protect 1337 PPL WinTcb
    
    [+] The Protection 'PPL-WinTcb' was set on the process with PID 1337, previous protection was: 'None-None'.
    
    [+] The Signature level 'WindowsTcb' and the Section signature level 'Windows' were set on the process with PID 1337.

## 项目地址

 **PPLcontrol** ：【[ _GitHub传送门_](https://github.com/itm4n/PPLcontrol)】

## 参考资料

> [ _https://itm4n.github.io/debugging-protected-> processes/_](https://itm4n.github.io/debugging-protected-processes/)
>
> [
> _https://github.com/RedCursorSecurityConsulting/PPLKiller/tree/master/driver_](https://github.com/RedCursorSecurityConsulting/PPLKiller/tree/master/driver)

