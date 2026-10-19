![](https://image.3001.net/images/20210716/1626450631_60f1aac7909f6f6b6cd66.png!small)

## 关于FalconEye

FalconEye是一款功能强大的Windows终端安全检测工具，可以帮助广大研究人员实时检测Windows进程注入行为。FalconEye也是一个内核模式驱动工具，旨在实现实时的进程注入行为。由于FalconEye需要以内核模式运行，它可以提供一个强大可靠的安全防御机制来抵御那些尝试绕过各种用户模式钩子的进程注入技术。

## 工具架构

![](https://image.3001.net/images/20210716/1626450640_60f1aad0c13b27c56a5af.png!small)

> FalconEye驱动器是一种按需加载的驱动程序；
>
> 初始化包括通过libinfinityhook设置回调和syscall钩子；
>
> 回调维护从跨流程活动（如OpenProcess）构建的Pids的映射，但不限于OpenProcess；
>
> 随后的回调和syscall钩子使用这个Pid映射来减少处理中的噪声；
>
> 作为降噪的一部分，syscall钩子可以过滤掉相同的进程活动；
>
> 检测逻辑分为多种子类，即无状态（例如：Atombombing）、有状态（Unmap+Overwrite）和浮动代码（多种技术实现的Shellcode）；
>
>
> 针对有状态的检测，syscall钩子会记录一个ActionHistory（历史活动），比如说，它会记录所有的NtWriteVirtualMemory调用；
>
> 检测逻辑具有常见的异常检测功能，如浮动代码检测和远程进程中Shellcode触发器的检测。回调和syscall钩子都会调用这个公共功能来进行实际检测；

需要注意的是，我们的重点一直是检测任务本身，而不是创建一个高性能的检测引擎。

## 项目目录结构

    
    
    .
    
    ├── src
    
    │   ├── FalconEye ---------------------------# FalconEye user and kernel space
    
    │   └── libinfinityhook ---------------------# Kernel hook implementation
    
    ├── 2021BHASIA_FalconEye.pdf
    
    └── README.md

## 工具要求

> Windows 10 Build 1903/1909
>
> Microsoft Visual Studio 2019
>
> VmWare、Hyper-V等虚拟化软件

## 工具安装

### 项目构建

> 使用Microsoft Visual Studio 2019打开解决方案；
>
> 选择x64作为构建平台；
>
>
> 构建解决方案，此时将在“src\kernel\FalconEye\x64\Debug”或“src\kernel\FalconEye\x64\Release”路径下生成sys源码；

### 测试设备部署

在虚拟机中安装好Windows 10 Build 1903/1909；

配置虚拟机以测试未签名的驱动程序，使用bcdedit，禁用完整性检测：

    
    
    BCDEDIT /set nointegritychecks ON

在虚拟机中运行DbgView，或使用WinDbg开启一个调试连接；

## 工具使用

我们需要将sys文件拷贝到测试设备（Windows 10虚拟机）中；

使用OSR加载器或类似的工具，以“按需”加载驱动器的形式加载sys；

运行类似pinjectra或minjector之类的注入测试工具；

通过WinDbg或DbgView监控调试日志；

## 项目地址

 **FalconEye：** 【[ _GitHub传送门_](https://github.com/rajiv2790/FalconEye)】

## 参考资料

> [ _https://www.blackhat.com/asia-21/arsenal/schedule/#falconeye-windows-> process-injection-techniques---catch-them-> all-22612_](https://www.blackhat.com/asia-21/arsenal/schedule/#falconeye-> windows-process-injection-techniques---catch-them-all-22612)
>
> [
> _https://github.com/rajiv2790/FalconEye/blob/main/2021BHASIA_FalconEye.pdf_](https://github.com/rajiv2790/FalconEye/blob/main/2021BHASIA_FalconEye.pdf)、
>
> [ _https://modexp.wordpress.com/2018/08/30/windows-process-injection-> control-handler/_](https://modexp.wordpress.com/2018/08/30/windows-process-> injection-control-handler/)
>
> [ _http://blog.txipinet.com/2007/04/05/69-a-paradox-writing-to-another-> process-without-openning-it-nor-actually-writing-to-> it/_](http://blog.txipinet.com/2007/04/05/69-a-paradox-writing-to-another-> process-without-openning-it-nor-actually-writing-to-it/)
>
> [
> _https://modexp.wordpress.com/2019/06/15/4083/_](https://modexp.wordpress.com/2019/06/15/4083/)
>
> [ _https://modexp.wordpress.com/2018/09/12/process-injection-user-> data/_](https://modexp.wordpress.com/2018/09/12/process-injection-user-> data/)
>
> [ _https://modexp.wordpress.com/2018/08/26/process-injection-> ctray/_](https://modexp.wordpress.com/2018/08/26/process-injection-ctray/)
>
> [
> _https://github.com/everdox/InfinityHook/_](https://github.com/everdox/InfinityHook/)
>
> [ _https://github.com/SafeBreach-> Labs/pinjectra/_](https://github.com/SafeBreach-Labs/pinjectra/)
>
> [ _https://github.com/antonioCoco/Mapping-> Injection﻿_](https://github.com/antonioCoco/Mapping-Injection)

