![](https://image.3001.net/images/20220913/1663037051_631fee7b1e53c99321d95.png!small)

## 关于SystemInformer

SystemInformer是一款功能强大的系统安全检测工具，该工具功能十分强大，不仅可以帮助广大研究人员监控系统资源，而且还支持软件调试和恶意软件检测。

## 功能介绍

> 1、提供系统活动的详细概述（带高亮/突出显示）；
>
> 2、图形和统计数据允许我们快速跟踪占用的系统资源和失控进程；
>
> 3、无法编辑或删除文件？该工具可以发现哪些进程正在使用该文件；
>
> 4、支持查看哪些程序具有活动网络连接，并在必要时关闭它们；
>
> 5、可以获取有关磁盘访问的实时信息；
>
> 6、支持使用内核模式、WOW64和.NET查看详细的堆栈跟踪数据；
>
> 7、基于services.msc实现了更多功能，可创建、编辑和控制服务；
>
> 8、体积小，无需安装，随处可用；
>
> 9、100%免费，遵循[
> _MIT_](https://github.com/winsiderss/systeminformer/blob/master/LICENSE.txt)开源许可证协议；

## 系统要求

Windows 7或更高版本，支持32位和64位操作系统。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/winsiderss/systeminformer.git

## 项目构建

构建项目代码需要使用Visual Studio 2022或更高版本。

我们可以执行项目build目录中的build_release.cmd来编译项目代码，或者使用Visual
Studio加载SystemInformer.sln和Plugins.sln解决方案。

我们可以点击【[ _这里_](https://www.visualstudio.com/vs/community/)】下载Visual
Studio社区版来构建SystemInformer的源代码。

## 工具设置

如果你正在从USB驱动器运行SystemInformer，那么你还需要保存SystemInformer工具的所有配置信息。为此，我们需要在SystemInformer.exe所在目录中创建一个名为SystemInformer.exe.settings.xml的空文件，接下来按照下列步骤操作：

> 1、在Windows资源管理器中，确保取消勾选“工具 > 文件夹选项 > 视图”中的“隐藏已知文件类型的扩展名”；
>
> 2、右键单击文件夹中的空白区域，然后选择“新建 > 文本文档”；
>
> 3、将文件名重命名为SystemInformer.exe.settings.xml；

## 插件系统

我们可以点击“Options -> Plugins”来配置工具插件。

如果你在使用插件的过程中遇到了错误或者问题，可以通过更新插件来解决。

ExtendedTools插件提供的磁盘和网络信息仅在以管理员权限运行SystemInformer时可用。

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/winsiderss/systeminformer/blob/master/LICENSE.txt)开源许可证协议。

## 项目地址

 **SystemInformer** ：【[
_GitHub传送门_](https://github.com/winsiderss/systeminformer)】

## 参考资料

> [
> _https://www.visualstudio.com/vs/community/﻿_](https://www.visualstudio.com/vs/community/)

