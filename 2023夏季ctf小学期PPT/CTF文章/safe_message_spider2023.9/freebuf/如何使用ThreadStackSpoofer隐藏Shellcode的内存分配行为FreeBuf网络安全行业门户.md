![](https://image.3001.net/images/20211122/1637571034_619b59daed4d51707d5a8.png!small)

## 关于ThreadStackSpoofer

ThreadStackSpoofer是一种先进的内存规避技术，它可以帮助广大研究人员或红/蓝队人员更好地隐藏已注入的Shellcode的内存分配行为，以避免被扫描程序或分析工具所检测到。

ThreadStackSpoofer是线程堆栈欺骗技术的一个示例实现，旨在规避恶意软件分析、反病毒产品和EDR在检查的线程调用堆栈中查找Shellcode帧的引用。其思想是隐藏对线程调用堆栈上针对Shellcode的引用，从而伪装包含了恶意代码的内存分配行为。

在该工具的帮助下，可以帮助现有的商业C2产品安全性有更好的提升，并协助红队研究人员开发出更好的安全产品/工具。

## 工具运行机制

ThreadStackSpoofer的大致运行机制和算法如下所示：

> 从文件中读取Shellcode的内容；
>
> 从dll获取所有必要的函数指针，然后调用SymInitialize；
>
> 设置kernel32!Sleep狗子，并指向回我们的回调；
>
> 通过VirtualAlloc + memcpy +
> CreateThread注入并启动Shellcode。线程应该通过我们的runShellcode函数启动，以避免线程的StartAddress节点进入某些意外或异常的地方（比如说ntdll!RtlUserThreadStart+0x21）；
>
> 当Beacon尝试休眠的时候，我们的MySleep回调便会被调用；
>
> 接下来，我们将栈内存中最新返回的地址重写为0；
>
> 最后，会发送一个针对::SleepEx的调用来让Beacon继续等待后续的连接；
>
> 休眠结束之后，我们将恢复之前存储的原始函数返回地址并继续执行挂起的任务；

函数的返回地址会分散在线程的堆栈内存区域周围，由RBP/EBP寄存器存储其指向。为了在堆栈上找到它们，我们需要首先收集帧指针，然后取消对它们的引用以进行覆盖：

![](https://image.3001.net/images/20211122/1637570963_619b5993710f290024d4a.png!small)

    
    
    *(PULONG_PTR)(frameAddr + sizeof(void*)) = Fake_Return_Address;

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/mgeeky/ThreadStackSpoofer.git

## 工具使用

### 使用样例

    
    
    C:\> ThreadStackSpoofer.exe <shellcode> <spoof>

其中：

> <shellcode>：Shellcode的文件路径；
>
> <spoof>：“1”或“true”代表启用线程栈内存欺骗，其他参数表示禁用该技术；

### 欺骗Beacon的线程调用栈示例

    
    
    PS D:\dev2\ThreadStackSpoofer> .\x64\Release\ThreadStackSpoofer.exe .\tests\beacon64.bin 1
    [.] Reading shellcode bytes...
    [.] Hooking kernel32!Sleep...
    [.] Injecting shellcode...
    [+] Shellcode is now running.
    [>] Original return address: 0x1926747bd51. Finishing call stack...
    ===> MySleep(5000)
    [<] Restoring original return address...
    [>] Original return address: 0x1926747bd51. Finishing call stack...
    ===> MySleep(5000)
    
     
    
    [<] Restoring original return address...
    
    [>] Original return address: 0x1926747bd51. Finishing call stack...

## 工具使用演示

下面的例子中，演示了没有执行欺骗技术时的堆栈调用情况：

![](https://image.3001.net/images/20211122/1637571060_619b59f4ac763c3c5adb0.png!small)

开启线程堆栈欺骗之后的堆栈调用情况如下图所示：

![](https://image.3001.net/images/20211122/1637571067_619b59fb39adf449e56f7.png!small)

上述例子中，我们可以看到调用栈中最新的帧为MySleep回调。我们可以通过搜索规则查找调用堆栈未展开到系统库中的线程入口点：

    
    
    kernel32!BaseThreadInitThunk+0x14
    ntdll!RtlUserThreadStart+0x21

![](https://image.3001.net/images/20211122/1637570876_619b593cdbe6f774202bd.png!small)

上图所示为未修改的Total Commander x64线程。正如我们所看到的，它的调用堆栈在初始调用堆栈帧方面与我们自己的调用堆栈非常相似。

## 项目地址

 **ThreadStackSpoofer：** 【[
_GitHub传送门_](https://github.com/mgeeky/ThreadStackSpoofer)】

## 参考资料

> [ _https://www.arashparsa.com/hook-heaps-and-live-> free/_](https://www.arashparsa.com/hook-heaps-and-live-free/)
>
> [
> _https://github.com/mgeeky/ShellcodeFluctuation﻿_](https://github.com/mgeeky/ShellcodeFluctuation)
>
> [ _https://twitter.com/namazso_](https://twitter.com/namazso)
>
> [ _https://docs.microsoft.com/en-us/windows/win32/api/winnt/nf-winnt-> rtllookupfunctionentry_](https://docs.microsoft.com/en-> us/windows/win32/api/winnt/nf-winnt-rtllookupfunctionentry)
>
> [ _https://docs.microsoft.com/ru-ru/windows/win32/api/winnt/nf-winnt-> rtlvirtualunwind_](https://docs.microsoft.com/ru-> ru/windows/win32/api/winnt/nf-winnt-rtlvirtualunwind)
>
> [ _https://github.com/mgeeky/unhook-bof_](https://github.com/mgeeky/unhook-> bof)
>
> [ _https://github.com/Cobalt-Strike/unhook-> bof/pull/1_](https://github.com/Cobalt-Strike/unhook-bof/pull/1)
>
> [ _https://docs.microsoft.com/en-us/cpp/build/exception-> handling-x64?view=msvc-160_](https://docs.microsoft.com/en-> us/cpp/build/exception-handling-x64?view=msvc-160)
>
> [
> _https://github.com/mic101/windows/blob/master/WRK-v1.2/base/ntos/rtl/amd64/exdsptch.c_](https://github.com/mic101/windows/blob/master/WRK-v1.2/base/ntos/rtl/amd64/exdsptch.c)
>
> [ _https://docs.microsoft.com/en-us/windows/win32/debug/pe-format#the-pdata-> section_](https://docs.microsoft.com/en-us/windows/win32/debug/pe-> format#the-pdata-section)
>
> [
> _https://github.com/hzqst/unicorn_pe/blob/master/unicorn_pe/except.cpp#L773_](https://github.com/hzqst/unicorn_pe/blob/master/unicorn_pe/except.cpp#L773)

