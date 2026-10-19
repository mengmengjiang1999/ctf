![](https://image.3001.net/images/20210507/1620391779_60953763e9fb168c9f228.png!small)

## 关于WinPmem

WinPmem是一款功能强大的跨平台内存采集工具，在此之前，WinPmem一直都是Windows平台下的默认开源内存采集驱动器。该工具之前属于Rekall项目，近期被单独拆分出来作为一个代码库发布。

 **WinPmem本质上来说，是一款物理内存采集工具，该工具拥有下列特性：**

> 源代码开源。
>
> 支持32和64位的Windows XP和Windows 10，可以使用WDK7600以支持Windows
> XP。默认情况下，我们提供的WinPmem可执行程序将会结合WDK10编译以支持Windows 7-10。
>
> 使用了三种不同的独立方法来创建内存转储，总会有一种方法适用于内核模式rootkit。
>
> 支持原始内存转储镜像导出。
>
> 使用了一个读取设备接口，而不是像其他工具一样直接从内核写入镜像。这样可以允许我们使用复杂的用户空间镜像工具，并在系统上执行实时分析。

## 工具使用

我们这里提供了两个WinPmem可执行程序，即winpmem_mini_x86.exe和winpmem_mini_x64.exe。这两个版本都包含了针对32位和64位操作系统的驱动器。

文件名中的“mini”指的是这个工具仅使用了一个简单的镜像工具，它只能生成RAW格式的镜像。之前我们发布过一个基于AFF4的WinPmem镜像工具，但是现在我们对其进行了更新。

## Python采集工具-winpmem.py

WinPmem的Python版程序目前仍处于开发中，但是可以作为一个基于Python的镜像工具演示使用。

## winpmem_mini_x64.exe可执行程序

这个程序可以轻松用于事件应急响应任务种，因为它不需要任何其他的依赖组件，只需要这一个可执行程序即可执行，程序将自动加载对应的驱动器（32位或64位），并且是独立执行的。

## 工具使用样例

下列命令将使用默认的采集方法向physmem.raw写入原始镜像：

    
    
    winpmem_mini_x64.exe physmem.raw

下列命令将使用指定的MmMapIoSpace方法获取原始镜像：

    
    
    winpmem.exe -1 myimage.raw

驱动器将会在获取到镜像之后自动卸载。

## 许可证协议

本项目的开发与发布遵循Apache v2.0开源许可证协议。

## 项目地址

WinPmem：【[ _GitHub传送门_](https://github.com/Velocidex/WinPmem)】

## 参考资料

[ _https://docs.microsoft.com/en-us/windows-hardware/drivers/install/the-testsigning-boot-configuration-option_](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/the-testsigning-boot-configuration-option)

[ _https://binalyze.com/﻿_](https://binalyze.com/)

