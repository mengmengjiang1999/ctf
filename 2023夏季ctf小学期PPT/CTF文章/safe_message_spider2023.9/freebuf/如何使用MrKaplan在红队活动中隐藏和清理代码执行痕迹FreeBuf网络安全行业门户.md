![](https://image.3001.net/images/20220825/1661386221_6306bded88da718edf636.png!small)

## 关于MrKaplan

MrKaplan是一款功能强大的红队安全研究工具，该工具可以帮助广大红队研究人员清理和隐藏活动中的代码执行痕迹。该工具可以通过保存文件运行时间、存储文件快照等信息来辅助红队活动，并将所有的取证信息与相关用户关联起来。

## 功能介绍

> 1、关闭系统事件日志记录功能
>
> 2、清理文件和代码组件
>
> 3、清理注册表
>
> 4、支持多用户运行
>
> 5、支持以普通用户或管理员身份运行（建议以管理员权限运行）
>
> 6、支持保存文件时间戳
>
> 7、支持排除指定操作，并将组件留给蓝队人员

## 工具下载

该工具本质上是一个PowerShell脚本，因此我们需要确保目标主机支持运行PowerShell。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Idov31/MrKaplan.git

## 参数解释

-Users：该参数不支持与-RunAsUser参数一起使用，该参数允许删除其他用户在当前设备上的工具组件；

-RunAsUser：该参数不支持与-Users参数一起使用，该参数允许删除当前用户权限下的工具组件；

-EtwBypassMethod：该参数不支持与-RunAsUser参数一起使用，该参数允许选择用于终止事件日志记录程序执行的方法；

-Exclusions：该参数允许我们控制哪些痕迹不需要被清理，其中包括：

> eventlogs => 不终止ETW
>
> pshistory => 不覆盖PowerShell历史记录
>
> userassist => 不清理UserAssist注册表键
>
> bamkey => 不清理BAM注册表键
>
> comdlg32 => 不清理ComDlg32注册表键
>
> appcompatcache => 不清理AppCompatCache注册表键
>
> inetcache => 不清理INet缓存文件夹
>
> windowshistory => 不清理Windows历史记录文件夹
>
> officehistory => 不清理Office历史记录文件夹
>
> cryptnetcache => 不清理CryptNetUrlCache文件夹
>
> prefetch => 不清理prefetch

## 工具使用

当我们需要在目标设备上进行红队操作之前，使用默认参数运行MrKaplan即可。注意，不要移除MrKaplan的注册表键，否则MrKaplan将无法正常运行。

## 许可证协议

本项目的开发与发布遵循[ _BSD_
_-2-Clause_](https://github.com/Idov31/MrKaplan/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **MrKaplan** ：【[ _GitHub传送门_](https://github.com/Idov31/MrKaplan)】

## 参考资料

> [
> _https://github.com/mufeedvh/moonwalk_](https://github.com/mufeedvh/moonwalk)
>
> [
> _https://github.com/PowerShellMafia/PowerSploit_](https://github.com/PowerShellMafia/PowerSploit)
>
> [ _https://github.com/hlldz/Phant0m_](https://github.com/hlldz/Phant0m)
>
> [
> _https://github.com/ForensicArtifacts/artifacts/blob/main/data/windows.yaml_](https://github.com/ForensicArtifacts/artifacts/blob/main/data/windows.yaml)

