## Dr.Semu

Dr.Semu是一款基于动态行为分析的恶意软件检测与分类工具，目前该工具仍处于早起开发阶段。Dr.Semu能够在一个隔离环境中运行目标可执行程序，并监控相关进程的各种行为。除此之外，广大用户还可以根据自己的需求或社区现成的信息来构建Dr.Semu检测规则，并对目标恶意软件或进程进行安全检测。

![](https://image.3001.net/images/20190915/1568480455_5d7d1cc7a7df3.png!small)

在Dr.Semu的帮助下，我们可以根据对进程动态行为检测的结果来创建恶意软件检测规则。

### 通过重定向实现隔离

该工具会在用户模式下运行，Windows项目文件系统（ProjFS）可以给我们提供一个虚拟文件系统，针对注册表重定向，该工具会将所有的注册表键拷贝到一个新的地址，并重定向所有的注册表键访问请求。

### 监控

Dr.Semu使用了[
_DynamoRIO_](https://github.com/DynamoRIO/dynamorio)（动态指令工具平台）来拦截线程，这种操作的效果等同于设置SSDT钩子，但是整个过程是在用户模式下实现的，而且无需设置任何钩子。

在这个阶段，Dr.Semu会生成一个JSON文件，其中包含有工具拦截下的所有数据信息。

### 检测

进程终止之后，根据[ _Dr.Semu规则_](https://github.com/secrary/DrSemu-Detections)，我们将会接受到目标应用程序的检测结果，即目标应用是否是恶意软件。

## Dr.Semu规则

Dr.Semu规则采用Python或LUA书写（位于dr_rules），需要使用到拦截过程中的动态信息以及关于待测目标的静态信息。

![](https://image.3001.net/images/20190915/1568480475_5d7d1cdb094e5.png!small)

规则参考样本-Python：【[
_点我获取_](https://gist.github.com/secrary/ac89321b8a7bde998a6e3139be49eb72)】

规则参考样本-LUA：【[
_点我获取_](https://gist.github.com/secrary/e16daf698d466136229dc417d7dbcfa3)】

## 工具使用

1、使用管理员权限运行PowerShell，并特权PowerShell窗口中启用ProjFS：

    
    
    Enable-WindowsOptionalFeature -Online -FeatureName Client-ProjFS -NoRestart

2、从该项目的[
_releases页面_](https://github.com/secrary/DrSemu/releases)中下载项目文档并解压缩ZIP文件；

3、下载DynamoRIO，并将文件提取至DrSemu目录中，然后重命名为[
_dynamorio_](https://github.com/DynamoRIO/dynamorio/releases)；

4、安装[ _Python 3（x64）_](https://www.python.org/downloads/release/python-372/)；

    
    
    DrSemu.exe --target file_path
    
    DrSemu.exe --target files_directory

### 工具演示

演示视频：【 _点我观看_】

## 代码构建

1、使用管理员权限运行PowerShell，并特权PowerShell窗口中启用ProjFS：

    
    
    Enable-WindowsOptionalFeature -Online -FeatureName Client-ProjFS -NoRestart

![3.png](https://image.3001.net/images/20190915/1568480515_5d7d1d036ab1b.png!small)

2、安装[ _Python 3（x64）_](https://www.python.org/downloads/release/python-372/)；

3、下载DynamoRIO，并将项目文件提取至bin目录，然后重命名为[
_dynamorio_](https://github.com/DynamoRIO/dynamorio/releases)；

4、构建[ _pe-parser-library.lib_](https://github.com/trailofbits/pe-parse)库：

> 使用cmake-gui并通过DrSemu\shared_libs\pe_parse中生成VS项目；
>
> 在build目录（\shared_libs\pe_parse\build\pe-parser-> library\Release\）下构建32位代码，或者在build64目录下构建64位代码；
>
> 将运行时库选项设置为Multi-threaded（/MT）；

5、将LauncherCLI设置为启动项目；

## 工具运行限制

唯一支持的Windows平台版本：Windows 10 v1809

## 项目地址

> Dr.Semu：【[ _GitHub传送门_](https://github.com/secrary/DrSemu)】

 *** 参考来源：[
_secrary_](https://github.com/secrary/DrSemu)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

