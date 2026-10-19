![](https://image.3001.net/images/20221122/1669122838_637ccb16ebac7962eb53d.png!small)

## 关于Collect-MemoryDump

Collect-MemoryDump是一款针对Windows的数字取证与事件应急响应工具，该工具能够自动创建Windows内存快照以供广大研究人员或应急响应安全人员进行后续的分析和处理。

项目提供的Collect-MemoryDump.ps1是一个PowerShell脚本文件，该脚本主要功能就是从一个活动的Windows操作系统中收集内存快照。

## 功能介绍

> 1、开始获取内存之前检查主机名和物理内存大小；
>
> 2、检查是否有足够的可用磁盘空间来保存内存转储文件；
>
> 3、支持收集原始内存转储 w/ Dumplt；
>
> 4、从Magnet Idea Lab收集Microsoft Crash Dump w/DumpIt；
>
> 5、支持检查加密磁盘数据；
>
> 6、支持收集BitLocker恢复密钥；
>
> 7、支持检查已安装的终端安全工具（反病毒和EDR产品）；
>
> 8、支持枚举目标主机中的所有必要信息，以丰富DFIR工作流；
>
> 9、支持创建受密码保护的安全存档容器；

## 工具下载&部署

广大研究人员可以直接访问该项目的【[ _Releases页面_](https://github.com/evild3ad/Collect-MemoryDump/releases/latest)】下载最新版本的Collect-MemoryDump。

注意：Collect-MemoryDump默认并不包含所有的外部工具。因此，我们需要手动下载下列工具依赖组件：

> 1、[ _Belkasoft Live RAM Capturer_](https://belkasoft.com/ram-capturer)
>
> 2、[ _Comae-Toolkit_](https://www.magnetforensics.com/blog/how-to-get-> started-with-comae/)
>
> 3、[ _MAGNET Encrypted Disk
> Detector_](https://www.magnetforensics.com/resources/encrypted-disk-> detector/)
>
> 4、[ _MAGNET Ram Capture_](https://www.magnetforensics.com/resources/magnet-> ram-capture/)

接下来，将工具所需的文件拷贝到下列文件路径：

 **Belkasoft Live RAM Capturer**

    
    
    $SCRIPT_DIR\Tools\RamCapturer\x64\msvcp110.dll
    
    $SCRIPT_DIR\Tools\RamCapturer\x64\msvcr110.dll
    
    $SCRIPT_DIR\Tools\RamCapturer\x64\RamCapture64.exe
    
    $SCRIPT_DIR\Tools\RamCapturer\x64\RamCaptureDriver64.sys
    
    $SCRIPT_DIR\Tools\RamCapturer\x86\msvcp110.dll
    
    $SCRIPT_DIR\Tools\RamCapturer\x86\msvcr110.dll
    
    $SCRIPT_DIR\Tools\RamCapturer\x86\RamCapture.exe
    
    $SCRIPT_DIR\Tools\RamCapturer\x86\RamCaptureDriver.sys

 **Comae-Toolkit**

    
    
    $SCRIPT_DIR\Tools\DumpIt\ARM64\DumpIt.exe
    
    $SCRIPT_DIR\Tools\DumpIt\x64\DumpIt.exe
    
    $SCRIPT_DIR\Tools\DumpIt\x86\DumpIt.exe

 **MAGNET Encrypted Disk Detector**

    
    
    $SCRIPT_DIR\Tools\EDD\EDDv310.exe

 **MAGNET Ram Capture**

    
    
    $SCRIPT_DIR\Tools\MRC\MRCv120.exe

## 工具使用

### 参数

    
    
    .\Collect-MemoryDump.ps1 [-Tool] [--Pagefile]

### 使用样例1

    
    
    .\Collect-MemoryDump.ps1 -DumpIt

### 使用样例2

    
    
    .\Collect-MemoryDump.ps1 -Comae
    
    
    使用样例3
    
    .\Collect-MemoryDump.ps1 -WinPMEM --Pagefile

## 工具使用演示

### 查看帮助信息

![](https://image.3001.net/images/20221122/1669122963_637ccb939af27ebb25df1.png!small)

### 检查可用空间

![](https://image.3001.net/images/20221122/1669122970_637ccb9a63af53419a3e7.png!small)

### 自动创建Windows内存快照 w/ Dumplt

![](https://image.3001.net/images/20221122/1669122976_637ccba0d31c53dcaf497.png!small)

### 自动创建Windows内存快照 w/ Magnet RAM Capture

![](https://image.3001.net/images/20221122/1669122982_637ccba6ae46c0c379f0c.png!small)

### 自动创建Windows内存快照 w/ WinPMEM

![](https://image.3001.net/images/20221122/1669122989_637ccbad974c7656b2870.png!small)

### 自动创建Windows内存快照 w/ Belkasoft Live RAM Capturer

![](https://image.3001.net/images/20221122/1669122996_637ccbb486fae5220e5bc.png!small)

### 自动创建Windows内存快照 w/ DumpIt (Microsoft Crash Dump)

![](https://image.3001.net/images/20221122/1669123003_637ccbbbe99357e68c5c9.png!small)

### 自动创建Windows内存快照 w/ WinPMEM

![](https://image.3001.net/images/20221122/1669123010_637ccbc2423ad41c399ff.png!small)

### 消息盒子

![](https://image.3001.net/images/20221122/1669123016_637ccbc86e31c386dd617.png!small)

### 安全文档容器和Logfile.txt

![](https://image.3001.net/images/20221122/1669123023_637ccbcf2df5cd8491001.png!small)

### 输出目录

![](https://image.3001.net/images/20221122/1669123031_637ccbd7de1eb67c296d3.png!small)

### 内存目录（WinPMEM和Pagefile）

![](https://image.3001.net/images/20221122/1669123038_637ccbde9f53a66a90306.png!small)

### 内存快照

![](https://image.3001.net/images/20221122/1669123044_637ccbe4ea987b525b67c.png!small)

### Pagefile收集

![](https://image.3001.net/images/20221122/1669123052_637ccbec8e1ed6bfbea50.png!small)

### 收集到的系统信息

![](https://image.3001.net/images/20221122/1669123059_637ccbf32e23ecbbc6872.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_ _-3.0_](https://github.com/evild3ad/Collect-MemoryDump/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Collect-MemoryDump** ：【[ _GitHub传送门_](https://github.com/evild3ad/Collect-MemoryDump)】

## 参考资料

> [ _https://www.magnetforensics.com/_](https://www.magnetforensics.com/)
>
> [ _https://github.com/evild3ad/Collect-MemoryDump/wiki/How-to-add-or-update-> dependencies_](https://github.com/evild3ad/Collect-MemoryDump/wiki/How-to-> add-or-update-dependencies)
>
> [ _https://www.comae.com/_](https://www.comae.com/)
>
> [
> _https://github.com/ufrisk/MemProcFS_](https://github.com/ufrisk/MemProcFS)
>
> [
> _https://github.com/Velocidex/WinPmem_](https://github.com/Velocidex/WinPmem)
>
> [ _https://www.magnetforensics.com/resources/magnet-ram-> capture/_](https://www.magnetforensics.com/resources/magnet-ram-capture/)
>
> [ _https://www.magnetforensics.com/resources/encrypted-disk-> detector/_](https://www.magnetforensics.com/resources/encrypted-disk-> detector/)
>
> [ _https://github.com/orlikoski/CyLR_](https://github.com/orlikoski/CyLR)
>
> [ _https://www.magnetforensics.com/blog/how-to-get-started-with-> comae/_](https://www.magnetforensics.com/blog/how-to-get-started-with-> comae/)
>
> [ _https://belkasoft.com/ram-capturer_](https://belkasoft.com/ram-capturer)

