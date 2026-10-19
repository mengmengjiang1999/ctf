## 关于ImpulsiveDLLHijack

ImpulsiveDLLHijack是一款功能强大的DLL劫持技术安全研究工具，该工具基于C#开发实现，可以帮助广大研究人员以自动化的方式扫描、发现并利用目标设备二进制文件中的DLL安全问题，并实现DLL劫持。红队研究人员也可以利用该工具来识别劫持路径，并在定制工具中实现该技术以绕过EDR产品的检测。

## 工具机制

该工具能够通过下列两个自动化阶段步骤实现DLL劫持检测：

发现：寻找潜在的DLL劫持路径；

利用：判断并确认DLL是否已从劫持路径加载，从而确定目标DLL劫持路径是否100%可利用；

## 工具要求

exe：【[ _点我获取_](https://docs.microsoft.com/en-us/sysinternals/downloads/procmon)】

自定义DLL路径确认：下面这些DLL文件，可帮助工具确认DLL是否已从已识别的劫持路径成功加载：dll（从本项目的MalDLL目录中获取）、maldll64.dll（从本项目的MalDLL目录中获取）、PeNet（【[
_点我获取_](https://www.nuget.org/packages/PeNet/)】）

## 工具安装

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/knight0x07/ImpulsiveDLLHijack.git

接下来，在Visual Studio中导入ImpulsiveDLLHijack项目源码，然后点击"Project" --> "Manage NuGet
packages" --> 浏览工具包并安装 "PeNet" -> https://www.nuget.org/packages/PeNet/

然后构建项目，此时项目的bin目录中就会出现ImpulsiveDLLHijack.exe文件了。

### DLL路经确认

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/knight0x07/ImpulsiveDLLHijack.git

接下来，根据目标系统架构构建x86或x64版本。

将x86编译结果重命名为maldll32.dll，将x64编译结果重命名为maldll64.dll。

最后，将编译生成的路经确认DLL（maldll32 &
maldll64）拷贝至ImpulsiveDLLHijack.exe目录下，然后执行ImpulsiveDLLHijack.exe即可。

## 工具使用

![](https://image.3001.net/images/20211126/1637896239_61a0502f5b18f793edadf.png!small)

## 工具使用样例

> 目标可执行程序：OneDrive.exe

### 操作阶段：DLL劫持路径发现

![](https://image.3001.net/images/20211126/1637896264_61a05048e76d2e07c580f.png!small)

### 操作阶段：DLL劫持利用

DLL劫持成功：

![](https://image.3001.net/images/20211126/1637896277_61a050550210429270cf4.png!small)

DLL劫持失败：

![](https://image.3001.net/images/20211126/1637896282_61a0505a461b5194ca20b.png!small)

DLL没有以入口点进行加载，手动分析后即可成功实现DLL劫持：

![](https://image.3001.net/images/20211126/1637896287_61a0505fd3763a168d736.png!small)

![](https://image.3001.net/images/20211126/1637896293_61a0506586eddc844cfd1.png!small)

### 操作阶段：最终结果和日志记录

> 日志文件路径：C:\DLLLogs\output_logs.txt

![](https://image.3001.net/images/20211126/1637896306_61a050727c0ce85ea6041.png!small)

## 项目地址

 **ImpulsiveDLLHijack：** 【[
_GitHub传送门_](https://github.com/knight0x07/ImpulsiveDLLHijack)】

## 参考资料

> [ _https://arxiv.org/abs/2108.10422_](https://arxiv.org/abs/2108.10422)
>
> [ _https://docs.microsoft.com/en-> us/sysinternals/downloads/procmon_](https://docs.microsoft.com/en-> us/sysinternals/downloads/procmon)
>
> [
> _https://www.nuget.org/packages/PeNet/﻿_](https://www.nuget.org/packages/PeNet/)

