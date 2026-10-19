![](https://image.3001.net/images/20221122/1669119624_637cbe88b55ee6b46f16d.jpg!small)

## 关于Dismember

Dismember是一款针对Linux内存安全的测试与扫描工具，该工具本质上是一个基于命令行的工具，专为Linux操作系统而设计，可以帮助广大研究人员扫描Linux系统上的所有进程，并尝试从中搜索常见的敏感信息或自定义的正则表达式匹配项。

该工具基于Go语言开发，目前仍在积极开发阶段，之后可能会升级为一个完整的渗透测试工具。

## 工具要求

该工具基于Go语言开发，因此我们首先需要在本地设备上安装并配置好Go语言环境。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/liamg/dismember.git

或直接访问该项目的【[
_Releases页面_](https://github.com/liamg/dismember/releases/latest)】下载最新版本的Dismember代码，并将其添加到环境变量PATH中。

## 工具命令

该工具可以使用grep命令在所有内存中为所有（可访问）进程匹配正则表达式，这种方法可以用于查找内存中的敏感数据，通过内存中包含的内容识别进程，或者查询进程的内存以获取有趣的信息。scan命令中包含了许多内置模式，它可以有效地作为机器内存的敏感数据扫描器。

Dismember可用于搜索它访问的所有进程的内存，因此以root身份运行它是最有效的方法。除此之外，该工具还提供了进程枚举、进程状态获取、进程信息收集和绘制进程树等功能。

### 主要命令

 ** **命令****

|

 ** **描述****  
  
---|---  
  
grep

|

根据给定字符串或正则表达式搜索进程内存数据  
  
scan

|

根据预定义的敏感数据模式搜索进程内存数据  
  
### 实用工具命令

 ** **命令****

|

 ** **描述****  
  
---|---  
  
files

|

显示进程可访问的文件列表  
  
find

|

搜索一个给定进程名称的PID，如果匹配到了多个进程，则返回第一个匹配项  
  
info

|

显示目标进程的相关信息  
  
kernel

|

显示关于内核的信息  
  
kill

|

使用SIGKILL终止一个或多个进程的执行  
  
list

|

枚举目标系统中所有的进程  
  
resume

|

使用SIGCONT恢复挂起的进程  
  
suspend

|

使用SIGSTOP挂起一个进程  
  
tree

|

显示一个进程和所有子进程的进程树  
  
## 工具使用

### 通过PID搜索目标进程中的某个模式匹配

搜索进程1234（PID）中的内存信息：

    
    
    dismember grep -p 1234 'the password is .*'

### 通过进程名称搜索目标进程中的某个模式匹配

搜索进程“nginx”的内存相关信息：

    
    
    dismember grep -n nginx 'username=liamg&password=.*'

### 搜索所有进程中的某个模式匹配

搜索所有进程中的GitHub API令牌：

    
    
    dismember grep 'gh[pousr]_[0-9a-zA-Z]{36}'

### 搜索所有进程中的内存敏感信息

搜索所有可访问进程内存中的常见敏感信息：

    
    
    dismember scan

## 工具使用演示

![](https://image.3001.net/images/20221122/1669119680_637cbec03af0d824032e4.gif)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/liamg/dismember/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Dismember** ：【[ _GitHub传送门_](https://github.com/liamg/dismember)】

