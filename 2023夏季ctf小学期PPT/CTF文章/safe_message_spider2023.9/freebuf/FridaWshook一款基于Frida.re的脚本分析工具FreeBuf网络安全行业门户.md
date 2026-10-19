**今天给大家介绍的是一款名叫Frida-Wshook的脚本[分析](https://www.kitploit.com/search/label/Analysis)工具，这款工具基于[Frida.re](https://www.frida.re/)开发，并且通过[挂钩](https://www.kitploit.com/search/label/Hook)恶意脚本文件([WScript](https://technet.microsoft.com/en-us/library/hh875526\(v=ws.11\).aspx)/
[CScript](https://technet.microsoft.com/en-us/library/bb490887.aspx))的常用函数来对脚本命令进行分析。**

![1111111111111.png](https://image.3001.net/images/20181107/1541569925_5be27d858a64b.png!small)

该工具可以拦截[Windows](https://www.kitploit.com/search/label/Windows)
API函数，并且不会干扰原始目标脚本语言的正常运行。该工具所支持的脚本语言类型如下：

1..js（[Jscript](https://en.wikipedia.org/wiki/JScript)）

2..vbs（[VBScript](https://en.wikipedia.org/wiki/VBScript)）

3..wsf（[WSFile](https://msdn.microsoft.com/en-us/library/ms995854.aspx)）（目前还不支持复杂任务，仍在开发中…）

默认使用csript.exe运行的脚本文件将会输出下列内容：

    
    
    >COMProjIds
    
    >DNS请求
    
    >Shell命令
    
    >网络请求

## 注意事项

请确保在专门搭建的分析系统环境下运行任意恶意脚本，建议大家使用虚拟机快照，因为当你在系统中运行了恶意脚本之后，系统快照可以帮助大家快速重置系统。

虽然该工具能够挂钩常用函数，但是Windows还给开发人员提供了各种网络交互、文件系统访问和命令执行的API，所以你在分析的过程中也有可能遇到一些不常见的API函数。

## 工具安装与配置

>安装Python 2.7

>使用pip命令安装Frida及依赖

    
    
    pip install frida

>克隆（或下载）Frida-Wshook库

### 支持的操作系统

Frida-Wshook已在Windows 10和Windows 7进行了测试，理论上该工具可以运行在Windows
7+环境。在x64系统上，CScript会从C:\Windows\SysWow64加载。

该工具也许可以在Windows XP上正常运行，但是我认为CScript可能会使用一些遗留API调用，这很有可能导致某些需要分析的指令被忽略。

## 工具使用

脚本支持多种可选的命令行参数，这些参数可以帮助我们控制脚本主机可调用的API。

    
    
    usage:frida-wshook.py [-h] [--debug] [--disable_dns] [--disable_com_init]
    
                           [--enable_shell][--disable_net]
    
                           script
    
    frida-wshook.pyyour friendly WSH Hooker
    
    positional arguments:
    
      script              Path to target .js/.vbs file
    
    optional arguments:
    
      -h, --help          show this help message and exit
    
      --debug             Output debug info
    
      --disable_dns       Disable DNS Requests
    
      --disable_com_init  Disable COM Object Id Lookup
    
      --enable_shell      Enable Shell Commands
    
      --disable_net       Disable Network Requests

使用默认参数分析目标脚本：

    
    
    python wshook.py bad.js

启用verbose调试：

    
    
    python wshook.py --debug bad.js

启用Shell命令执行：

    
    
    python frida-wshook.py --enable_shell bad.vbs

禁用WSASend：

    
    
    python frida-wshook.py --disable_net bad.vbs

检查脚本所使用的ProgIds：

    
    
    python frida-wshook.py --disable_com_init bad.vbs

## 钩子函数

    
    
    >ole32.dll
    
    >[CLSIDFromProgIDEx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms680113\(v=vs.85\).aspx)  
    
    >Shell32.dll
    
    >[ShellExecuteEx](https://msdn.microsoft.com/en-us/library/windows/desktop/bb762154\(v=vs.85\).aspx)
    
    >Ws2_32.dll
    
    >[WSASocketW](https://msdn.microsoft.com/en-us/library/windows/desktop/ms742212\(v=vs.85\).aspx)
    
    >[GetAddrInfoExW](https://msdn.microsoft.com/en-us/library/windows/desktop/ms738518\(v=vs.85\).aspx)
    
    >[WSASend](https://msdn.microsoft.com/en-us/library/windows/desktop/ms742203\(v=vs.85\).aspx)   
    
    >[WSAStartup](https://msdn.microsoft.com/en-us/library/windows/desktop/ms742213\(v=vs.85\).aspx)

[](https://msdn.microsoft.com/en-us/library/windows/desktop/ms742213\(v=vs.85\).aspx)

## 已知问题

1.网络响应无法捕捉；

2.禁用对象查询功能将导致脚本输出缺少第一个恶意软件QA的ProgId；

3.暂不支持需要进行特殊任务的WSF文件。

 ***参考来源：[kitploit](https://www.kitploit.com/2018/11/frida-wshook-script-analysis-tool-based.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

