![](https://image.3001.net/images/20210311/1615475443_604a32f395242e56008fa.png!small)

## WdToggle技术

WdToggle技术本质上来说，是Cobalt Strike Beacon Object File（BOF-信标对象文件）的一种概念验证，它可以使用[
_直接系统调用_](https://outflank.nl/blog/2019/06/19/red-team-tactics-combining-direct-system-calls-and-srdi-to-bypass-av-edr/)来开启WDigest凭证缓存并尝试绕过凭证守护程序。

 **本技术的开发与实现基于前辈的下列工作：**

> 1、《[ _探索Mimikatz-第一部分-WDigest_](https://blog.xpnsec.com/exploring-mimikatz-> part-1/)》
>
> 2、《[ _绕过凭证守护程序_](https://teamhydra.blog/2020/08/25/bypassing-credential-> guard/)》

通过BOF代码中的内联程序集使用直接系统调用，提供了一种更为安全地与LSASS进程交互的操作方式，而且使用直接系统调用可避免AV/EDR软件拦截用户模式API调用。

VisualStudio（C++）不支持X64处理器的内联汇编。因此，为了编写包含编译/汇编代码的单个信标对象文件（BOF），我们必须使用[
_Mingw-w64_](http://mingw-w64.org/)（GCC for Windows）编译器。

## WdToggle库

为了方便大家实验WdToggle技术，我们专门提供了一个【[
_GitHub库_](https://github.com/outflanknl/WdToggle)】供大家使用。

 **这个库的主要作用如下：**

> 演示使用内联程序集进行直接系统调用的用法，以提供与LSASS进程交互的更为安全的操作方式。
>
> 通过在LSASS进程中将g_IsCredGuardEnabled变量切换为1来启用WDigest凭据缓存(wdigest.dll模块）。
>
> 通过在LSASS进程中将g_IsCredGuardEnabled变量切换为0来绕过凭证保护（如果启用）(wdigest.dll模块）。
>
> 使用[ _信标对象文件_ _（BOF）_](https://www.cobaltstrike.com/help-beacon-object-> files)在信标（Beacon）进程中执行此代码。

## 如何配置实验环境

在这里，我们并不打算给大家提供已编译好的源码，因此大家需要自行动手完成代码编译。

首先，我们需要使用下列命令将WdToggle项目源码克隆至本地：

    
    
    git clone https://github.com/outflanknl/WdToggle.git

确保你已经正确安装了Mingw-w64编译器。如果使用的是macOS的话，我们可以使用下列命令来安装Mingw-w64：

    
    
    sudo port install mingw-w64

接下来，运行下列命令来编译信标对象文件（BOF）：

    
    
    make

在一个Cobaltstrike Beacon上下文环境中，运行inline-execute命令并提供对象WdToggle.o文件的路径。

然后，运行Cobaltstrike的logonpasswords命令（Mimikatz），别忘了针对新用户登录或未锁定桌面会话的用户要再次开启密码清理选项。

## 限制条件

这种技术无法实现重启持久化，因此设备重启后我们需要重新运行代码。

wdigest!g_fParameter_UseLogonCredential和wdigest!g_IsCredGuardEnabled全局变量的内存偏移量可能会因Windows操作系统版本的不同而发生改变。大家可以使用Windows调试器工具来查看并添加自己对应系统版本的偏移量：

    
    
    C:\Program Files (x86)\Windows Kits\10\Debuggers\x64>cdb.exe -z C:\Windows\System32\wdigest.dll
    
     
    
    0:000>x wdigest!g_fParameter_UseLogonCredential
    
    00000001`800361b4 wdigest!g_fParameter_UseLogonCredential = <no type information>
    
    0:000> x wdigest!g_IsCredGuardEnabled
    
    00000001`80035c08 wdigest!g_IsCredGuardEnabled = <no type information>
    
    0:000>

## 检测方式

要通过LSASS内存访问检测凭证盗窃，我们可以使用Sysmon之类的工具，可以将Sysmon配置为记录打开lsass.exe文件过程。应用此配置后，我们可以为访问LSASS进程的可疑进程收集遥测信息，并帮助检测可能的凭据转储活动。当然，我们还有更多的选项来检测凭证被盗，例如使用Windows
Defender ATP之类的高级检测平台。但是，如果你没有足够的预算和豪华的设备去使用这些平台的话，那么Sysmon是一个免费的工具，可以帮助填补空白。

## WdToggle运行界面

![](https://image.3001.net/images/20210311/1615475484_604a331c124c60fe5274e.png!small)

## 参考资料

> [ _https://outflank.nl/blog/?p=1592_](https://outflank.nl/blog/?p=1592)
>
> [ _https://blog.xpnsec.com/exploring-mimikatz-> part-1/_](https://blog.xpnsec.com/exploring-mimikatz-part-1/)
>
> [ _https://teamhydra.blog/2020/08/25/bypassing-credential-> guard/_](https://teamhydra.blog/2020/08/25/bypassing-credential-guard/)
>
> [ _https://www.cobaltstrike.com/help-beacon-object-> files_](https://www.cobaltstrike.com/help-beacon-object-files)

