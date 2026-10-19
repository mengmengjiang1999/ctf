![](https://image.3001.net/images/20220627/1656321409_62b97581ef3deae563c37.jpeg!small)

## 关于COM-Hunter

COM-Hunter是一款针对持久化COM劫持漏洞的安全检测工具，该工具基于C#语言开发，可以帮助广大研究人员通过持久化COM劫持技术来检测目标应用程序的安全性。

## 关于COM劫持

微软在Windows 3.11中引入了(Component Object Model,
COM)，作为一种实现对象的方法，这些对象可以被不同的框架(ActiveX, COM+，
DCOM等)使用，并且在不同的Windows环境中允许互操作性，进程间通信和代码重用。COM对象的滥用使安防团队能够代表受信任的进程执行任意代码。执行COM劫持不需要管理员权限，因为HKCU注册表配置单元中的类在HKLM中的类之前执行。唯一影响高完整性进程(提升)的例外情况是，仅从HKLM位置加载对象，以防止特权提升。

## 功能介绍

> 1、在目标用户的计算机中查找有效的CLSID；
>
> 2、通过目标用户计算机中的任务调度器（Task Scheduler）查找有效的CLSID；
>
> 3、找出是否有人已经使用了这些有效的CLSID来进行持久化COM劫持（LocalServer*32/InprocServer*32）；
>
> 4、找出是否有人通过任务调度器（Task
> Scheduler）使用了任何有效的CLSID来执行持久化COM劫持（LocalServer*32/InprocServer*32）；
>
> 5、尝试通过任务调度器（Task Scheduler）自动执行持久化COM劫持；
>
> 6、尝试使用“TreatAs”键来引用其他组件；

## 工具要求

> .NET Framework v4.8

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/nickvourd/COM-Hunter.git

## 工具帮助信息

    
    
    [+] Usage:
    
     
    
        .\COM-Hunter.exe <mode> <options>
    
     
    
    -> General Options:
    
        -h, --help      显示帮助信息和退出
    
        -v, --version    显示工具当前版本
    
        -a, --about     显示跟工具相关的其他信息
    
     
    
    -> Modes:
    
        Search  搜索模式
    
        Persist  持久化模式
    
     
    
    -> Search Mode:
    
        Get-Entry     搜索有效的CLSID条目
    
        Get-Tasksch  通过任务调度器搜索有效的CLSID条目
    
        Find-Persist   搜索是否有人已经使用了一个有效的CLSID（安全防御）
    
        Find-Tasksch 搜索是否有人通过任务调度器（Task Scheduler）使用了任何有效的CLSID（安全防御）
    
     
    
    -> Persist Mode:
    
        General     使用常用方法在注册表中实现持久化COM劫持
    
        Tasksch     尝试通过任务调度器实现持久化COM劫持
    
        TreatAs     在注册表中尝试使用TreatAs注册表键实现持久化COM劫持
    
     
    
    -> General Usage:
    
        .\COM-Hunter.exe  持久化General <clsid> <full_path_of_evil_dll>
    
     
    
    -> Tasksch Usage:
    
        .\COM-Hunter.exe  持久化Tasksch <full_path_of_evil_dll>
    
     
    
    -> TreatAs Usage:
    
    .\COM-Hunter.exe  持久化TreatAs <clsid> <full_path_of_evil_dll>

## 工具使用样例

### 搜索包含有效CLSID的条目（搜索模式）

    
    
    .\COM-Hunter.exe Search Get-Entry

### 寻找持久化劫持点（搜索模式）

    
    
    .\COM-Hunter.exe Search Find-Persist

### 常用方法（持久化模式）

    
    
    .\COM-Hunter.exe Persist General 'HKCU:Software\Classes\CLSID\...' C:\Users\nickvourd\Desktop\beacon.dll

### 计划任务（持久化模式）

    
    
    .\COM-Hunter.exe Persist Tasksch C:\Users\nickvourd\Desktop\beacon.dll

## 有效CLSID格式样例

    
    
    Software\Classes\CLSID\...
    
    HKCU:Software\Classes\CLSID\...
    
    HKCU:\Software\Classes\CLSID\...
    
    HKCU\Software\Classes\CLSID\...
    
    HKEY_CURRENT_USER:Software\Classes\CLSID\...
    
    HKEY_CURRENT_USER:\Software\Classes\CLSID\...
    
    HKEY_CURRENT_USER\Software\Classes\CLSID\...

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/nickvourd/COM-Hunter/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **COM-Hunter** ：【[ _GitHub传送门_](https://github.com/nickvourd/COM-Hunter)】

## 参考资料

> [ _https://courses.zeropointsecurity.co.uk/courses/red-team-> ops_](https://courses.zeropointsecurity.co.uk/courses/red-team-ops)
>
> [
> _https://twitter.com/zeropointsecltd_](https://twitter.com/zeropointsecltd)
>
> [ _https://twitter.com/dimtsikopoulos_](https://twitter.com/dimtsikopoulos)
>
> [ _https://twitter.com/0xvm_](https://twitter.com/0xvm)

