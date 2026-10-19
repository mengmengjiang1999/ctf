**今天为大家介绍一款基于.NET Core运行时实现的Windows HOOK库， **CoreHook** 。**

## 建立状态

构建服务器 | 平台  
---|---  
AppVeyor | windows  
Azure管道 | Linux，Windows  
Travis CI | Linux  
  
## 特征

> 1.拦截公共API函数，如`CreateFile`
>
> 2.如果符号文件可用，则按地址或名称拦截内部函数；
>
> 3.支持插件库的NuGet包引用；
>
> 4.支持插件的多种架构；
>
> 有关更多信息，请参阅[wiki](https://github.com/unknownv2/CoreHook/wiki)。

## 支持的平台

CoreHook支持在运行[Windows的](https://docs.microsoft.com/en-us/dotnet/core/windows-prerequisites?tabs=netcore2x)各种体系结构上进行应用程序函数调用拦截。还计划了Linux和macOS支持。

### 平台

Architecture | 操作系统  
---|---  
x86 | Windows  
x64 | Windows  
ARM | Windows 10 IoT Core  
  
### 经过测试的平台

操作系统 | 架构  
---|---  
Windows 7 SP1 | x86，x64  
Windows 8.1 | x86，x64  
Windows 10（Win32） | x86，x64，ARM  
Windows 10（UWP） | x86，x64  
Windows Server 2008 | x86，x64  
Windows Server 2012 | x86，x64  
Windows Server 2016 | x86，x64  
Windows Server 2019 | x86，x64  
  
### 依赖

1.[.NET核心](https://docs.microsoft.com/en-us/dotnet/core/)

2.[CoreHook.Hooking](https://github.com/unknownv2/CoreHook.Hooking)

3.[CoreHook.Host](https://github.com/unknownv2/CoreHook.Host)

## 例子

1.[FileMonitor -通用Windows平台（UWP）](https://github.com/unknownv2/CoreHook/blob/master/examples/Uwp/CoreHook.Uwp.FileMonitor)

2.[FileMonitor -Windows桌面应用程序（Win32）](https://github.com/unknownv2/CoreHook/blob/master/examples/Win32/CoreHook.FileMonitor)

### 插件示例

1.[可以在此存储库中找到更多插件示例](https://github.com/unknownv2/corehook-plugins)

## 用法

### windows

如果要构建CoreHook项目（例如，使用`dotnet build`）而不发布它，则必须按如下所述设置项目配置。

 **项目配置**

该项目提供了两个配置运行时的选项：

名为`CoreHook.CoreLoad.runtimeconfig.json`
（位于`CoreHook.CoreLoad.dll`CoreHook输出目录中的程序集）的本地配置文件，用于初始化CoreCLR。

全局配置文件`dotnet.runtimeconfig.json`。

主机模块将首先尝试使用本地配置文件，然后它将检查全局配置文件（如果存在），最后它将使用`CoreHook.CoreLoad.dll`程序集的目录来解析依赖项。

该`runtimeconfig`文件必须包含用于在目标应用程序中托管.NET Core的框架信息。构建任何.NET
Core应用程序时，会将这些文件生成到输出目录。[有关配置选项的更多信息，请参见此处](https://github.com/dotnet/cli/blob/master/Documentation/specs/runtime-configuration-file.md)。

你可以使用`CoreHook.FileMonitor.runtimeconfig.json`和`CoreHook.FileMonitor.runtimeconfig.dev.json`构建输出目录中文件作为创建全局或本地配置文件的参考。

运行时配置文件应如下所示，其中`additionalProbingPaths`包含主机模块可以检查其他依赖项的文件路径。本指南假设您已`.NET Core
2.2`为x86和x64体系结构安装了运行时或SDK。

 **注意：使用 <user>
本地计算机用户名替换或修改指向NuGet软件包安装位置的路径。看看CoreHook.FileMonitor.runtimeconfig.dev.json在输出目录中找到。**

    
    
      {   
        "runtimeOptions": {   
          "tfm": "netcoreapp2.2",   
          "framework": {   
            "name": "Microsoft.NETCore.App",   
            "version": "2.2.0   
          },   
          "additionalProbingPaths": [   
            "C:\\Users\\<user>\\.dotnet\\store\\|arch|\\|tfm|",   
            "C:\\Users\\<user>\\.nuget\\packages",   
            "C:\\Program Files\\dotnet\\sdk\\NuGetFallbackFolder"   
          ]   
        }   
      } 

**本地配置**

要使用本地配置，请创建一个包含上述内容的文件，`CoreHook.CoreLoad.runtimeconfig.json`并将其保存到所在的项目输出目录中`CoreHook.CoreLoad.dll`。

 **全局配置**

要使用全局配置，请首先`dotnet.runtimeconfig.json`使用上述内容创建一个文件并将其保存到文件夹中。这将是项目用于初始化目标进程中的运行时的全局配置文件。在此示例中，我们的文件保存在`C:\CoreHook\dotnet.runtimeconfig.json`。

将`x86`和`x64`应用程序的环境变量设置为运行时配置文件的目录。这允许您为应用程序`32-bit`和`64-bit`应用程序提供不同的配置文件。

例如（如果您将文件保存为另一个安装目录或驱动器，请确保使用该路径）:

1.设置`CORE_ROOT_32`到`C:\CoreHook`了`32-bit`应用。

2.设置`CORE_ROOT_64`到`C:\CoreHook`了`64-bit`应用。

    
    
    setx  CORE_ROOT_64  “C：\ CoreHook”    
    setx  CORE_ROOT_32  “C：\ CoreHook” 

或者将它们设置为当前命令提示会话：

    
    
    set CORE_ROOT_64=C:\CoreHook   
    set CORE_ROOT_32=C:\CoreHook 

然后，您可以打开`CoreHook`解决方案`Visual Studio`或运行`dotnet build`以构建库和示例。

## 安装依赖项

从[CoreHook.Hooking](https://github.com/unknownv2/CoreHook.Hooking)和[CoreHook.Host](https://github.com/unknownv2/CoreHook.Host)构建或下载二进制版本。您可以使用[download-deps](https://github.com/unknownv2/CoreHook/blob/master/download-deps.cmd)脚本，该脚本将最新的二进制版本下载到`deps`项目根目录中调用的文件夹中。将`coreload32.dll (X86,
ARM)`和/或`coreload64.dll (X64, ARM64)`二进制文件放在程序的输出目录中。然后，将`corehook32.dll (X86,
ARM)`和/或`corehook64.dll (X64, ARM64)`二进制文件放在同一个输出目录中。这些是使用上述示例所需的所有文件。

然后，您可以启动上面构建的程序。

### Windows 10 UWP

您可以使用[此脚本](https://docs.microsoft.com/en-us/windows/configuration/find-the-application-user-model-id-of-an-installed-app)获取为FileMonitor示例启动UWP应用程序所需的应用程序用户模型标识（AUMID）[：](https://docs.microsoft.com/en-us/windows/configuration/find-the-application-user-model-id-of-an-installed-app)

    
    
      $installedapps = get-AppxPackage   
          
      $aumidList = @()   
      foreach ($app in $installedapps)   
      {   
          foreach ($id in (Get-AppxPackageManifest $app).package.applications.application.id)   
          {   
              $aumidList += $app.packagefamilyname + "!" + $id   
          }   
      }   
         
      $aumidList 

您可以使用`$aumidList`变量打印列表。

 **注意：** 目前无法在.NET
Core平台上的管道上设置正确的访问控制，[此处正在跟踪问题，](https://github.com/dotnet/corefx/issues/31190)因此我们使用P
/ Invoke `kernel32.dll!CreateNamedPipe`直接调用。

### Windows 10物联网（ARM）

 **Raspberry Pi本身仅作为部署目标受支持，但也有不受支持的SDK版本。按照此链接阅读有关发布过程的更多信息。**

对于`Windows 10 IoT Core`，您可以通过运行`publish.ps1`
[PowerShell脚本](https://github.com/unknownv2/CoreHook#publishing-script)来发布应用程序。

    
    
    .\publish -example win32 -runtime win-arm

确保还要复制`coreload32.dll`和`corehook32.dll`程序目录。例如，应用程序目录结构应如下所示：

    
    
      [+]Publish\win32\win-arm\   
          [+]Hook\   
              ...   
              [-] CoreHook.FileMonitor.Hook.deps.json   
              [-] CoreHook.FileMonitor.Hook.dll   
              ...   
          ...       
          [-] CoreHook.FileMonitor.dll   
          [-] CoreHook.FileMonitor.exe   
          [-] corehook32.dll   
          [-] coreload32.dll   
          ... 

然后，您可以将该文件夹复制到您的设备并启动该`CoreHook.FileMonitor.exe`程序。

## 发布脚本

PowerShell脚本`publish.ps1`允许您将[示例](https://github.com/unknownv2/CoreHook/blob/master/examples)发布为自包含的可执行文件。默认配置是`Release`，输出将在`Publish`目录中，在与发布脚本相同的位置创建。

    
    
    .\publish -example [uwp|win32] -runtime [Runtime IDentifier] -configuration [Debug|Release] 

例如，命令

    
    
    .\publish -example win32 -runtime win10-arm    

将创建一个名为`Publish/win32/win10-arm/`包含该`CoreHook.FileMonitor`示例的文件夹。

### Windows符号支持

CoreHook支持从PDB查找符号名称以获取使用的函数地址`LocalHook.GetProcAddress`。要使符号查找起作用，您必须将PDB文件放在要挂钩的目标程序的目录中，或将环境变量`_NT_SYMBOL_PATH`设置为符号服务器。[您可以从此处的Microsoft文档中了解有关Windows符号支持的更多信息。](https://docs.microsoft.com/en-us/windows/desktop/dxtecharts/debugging-with-symbols#using-the-microsoft-symbol-server)

 **要点：**
要使用完整的符号查找，您需要同时拥有`dbghelp.dll`（提供符号查找API）和`symsrv.dll`（提供符号服务器查找）并在[DLL搜索路径中](https://docs.microsoft.com/en-us/windows/desktop/dlls/dynamic-link-library-search-order)。您可以将这些文件添加到目标程序的目录中，也可以将它们添加到路径中。您可以通过安装
[**Windows调试工具**](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/)来获取这两个DLL 。

您可以找到`dbghelp.dll`和的示例位置`symsrv.dll`：

1. **％PROGRAMFILES（X86）％\ Windows Kits \ 10 \ Debuggers \ x86** （适用于32位应用程序）

2. **％PROGRAMFILES（X86）％\ Windows Kits \ 10 \ Debuggers \ x64** （适用于64位应用程序）

您可以将环境变量设置为的示例`_NT_SYMBOL_PATH`如下：

    
    
    srv*C:\SymbolCache*https://msdl.microsoft.com/downloads/symbols 

该`C:\SymbolCache`文件夹是本地缓存目录，可以存储或下载符号文件。当Windows需要检索DLL的PDB时，它可以从中下载它们`<https://msdl.microsoft.com/downloads/symbols>`并将它们存储在一个文件夹中供调试器使用。

您可以通过运行[符号测试](https://github.com/unknownv2/CoreHook/blob/master/tests/CoreHook.Tests/Windows/SymbolsTest.cs)来确认是否正确配置了符号支持。

***参考来源：[github](https://github.com/unknownv2/CoreHook)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

