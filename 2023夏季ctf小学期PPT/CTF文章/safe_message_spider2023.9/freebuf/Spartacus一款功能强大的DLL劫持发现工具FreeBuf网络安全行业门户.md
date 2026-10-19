![](https://image.3001.net/images/20230606/1686036344_647edf7858c292d8e2fe3.png!small)  

## 关于Spartacus

Spartacus是一款功能强大的DLL劫持发现工具，当一个易受DLL劫持攻击的进程请求加载DLL时，就有可能发生DLL劫持攻击。在该工具的帮助下，广大安全研究人员可以轻松识别和发现DLL劫持攻击的发生。

## 功能介绍

> 1、在本地解析ProcMon PML文件，PMC配置和PML日志解析器通过将[ _procmon_ _-_
> _parser_](https://github.com/eronnen/procmon-parser/)部分功能移植到C#来实现的；
>
>
> 2、Spartacus将为所有已识别的缺失DLL创建代理DLL。比如说，一个应用程序因为version.dll导致易受DLL劫持攻击的话，Spartacus将会创建一个version.dll.cpp文件，其中包含所有的export导出，我们可以插入自己的Payload或执行技术来对其进行编译；
>
> 3、支持处理大型PML文件，并将所有感兴趣的DLL存储在输出的CSV文件中。本地基准测试在45秒内处理了一个包含800万个事件的3GB文件；
>
> 4、[防御]支持监控模式，试图识别正在运行的应用程序所代理的调用行为；
>
> 5、支持为导出函数创建代理，以比main使用[ _DllMain_](https://www.redteam.cafe/red-team/dll-> sideloading/dll-sideloading-not-by-dllmain)，该技术需要使用到[
> _Ghidra_](https://github.com/NationalSecurityAgency/ghidra)；

## 工具执行流程

>
> 1、基于传递的参数创建一个ProcMon（PMC）配置文件，过滤器设置如下：操作为CreateFile；路径以.dll结束；进程名称不能是procmon.exe或procmon64.exe；启用Drop
> Filtered Events以确保最小化的PML输出大小；禁用Auto Scroll；
>
> 2、执行进程监控程序；
>
> 3、停止执行，直到用户按下ENTER键；
>
> 4、终止进程监控程序；
>
> 5、解析输出事件日志（PML）文件：使用NAMEW_NOT_FOUNDS和PATH_NOT_FOUND
> Dll创建一个CSV文件；与之前的DLL文件进行对比，并尝试识别实际加载的DLL文件；针对每一个找到的DLL，使用其所有的导出函数生成一个代理DLL；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Accenture/Spartacus.git

## 工具使用

收集所有的事件，并将其存储到C:\Data\logs.pml中。所有存在漏洞的DLL都将存储在C:\Data\VulnerableDLLFiles.csv，所有的代理DLL都存储在C:\Data\DLLExports中：

    
    
    --procmon C:\SysInternals\Procmon.exe --pml C:\Data\logs.pml --csv C:\Data\VulnerableDLLFiles.csv --exports C:\Data\DLLExports --verbose

仅收集与Teams.exe和OneDrive.exe相关的事件：

    
    
    --procmon C:\SysInternals\Procmon.exe --pml C:\Data\logs.pml --csv C:\Data\VulnerableDLLFiles.csv --exports C:\Data\DLLExports --verbose --exe "Teams.exe,OneDrive.exe"

仅收集与Teams.exe和OneDrive.exe相关的事件，并使用位于C:\Data\myProxySkeleton.cpp中的自定义代理DLL模版：

    
    
    --procmon C:\SysInternals\Procmon.exe --pml C:\Data\logs.pml --csv C:\Data\VulnerableDLLFiles.csv --exports C:\Data\DLLExports --verbose --exe "Teams.exe,OneDrive.exe" --proxy-dll-template C:\Data\myProxySkeleton.cpp

仅收集与Teams.exe和OneDrive.exe相关的事件，但不生成代理DLL：

    
    
    --procmon C:\SysInternals\Procmon.exe --pml C:\Data\logs.pml --csv C:\Data\VulnerableDLLFiles.csv --verbose --exe "Teams.exe,OneDrive.exe"

解析一个现有的PML事件日志输出，将结果存储到CSV文件，并生成代理DLL：

    
    
    --existing-log --pml C:\MyData\SomeBackup.pml --csv C:\Data\VulnerableDLLFiles.csv --exports C:\Data\DLLExports

以监控模式运行，并尝试检测任何代理DLL调用的应用程序：

    
    
    --detect

针对所有已识别的导出函数创建代理：

    
    
    --generate-proxy --ghidra C:\ghidra\support\analyzeHeadless.bat --dll C:\Windows\System32\userenv.dll --output-dir C:\Projects\spartacus-wtsapi32 --verbose

针对指定导出函数创建一个代理：

    
    
    --generate-proxy --ghidra C:\ghidra\support\analyzeHeadless.bat --dll C:\Windows\System32\userenv.dll --output-dir C:\Projects\spartacus-wtsapi32 --verbose --only-proxy "ExpandEnvironmentStringsForUserW"

## 工具运行截图

### Spartacus执行

![](https://image.3001.net/images/20230606/1686036459_647edfebbebc089b36703.png!small)

### CSV输出

![](https://image.3001.net/images/20230606/1686036470_647edff6926b77ead652f.png!small)

### 输出导出

![](https://image.3001.net/images/20230606/1686036484_647ee004946143abca62b.png!small)

### 导出DLL函数

![](https://image.3001.net/images/20230606/1686036492_647ee00ca3d769bea9204.png!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/Accenture/Spartacus/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Spartacus** ：【[ _GitHub传送门_](https://github.com/Accenture/Spartacus)】

## 参考资料

> [ _https://github.com/eronnen/procmon-> parser/_](https://github.com/eronnen/procmon-parser/)
>
> [ _https://www.redteam.cafe/red-team/dll-sideloading/dll-sideloading-not-by-> dllmain_](https://www.redteam.cafe/red-team/dll-sideloading/dll-sideloading-> not-by-dllmain)
>
> [
> _https://github.com/NationalSecurityAgency/ghidra_](https://github.com/NationalSecurityAgency/ghidra)

