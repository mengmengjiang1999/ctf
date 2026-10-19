**严正声明：本文仅限于技术探讨，严禁用于其他用途。**

![1.png任意代码保护与内核代码注入的那些事儿](https://image.3001.net/images/20180612/15288074187971.png!small)

## 写在前面的话

 **类似 WannaCry 和 Slingshot 这样的恶意软件最常用的一种攻击技术就是内核代码注入，在近期刚刚发布的 Windows 10
Creators 更新中，微软引入了一种针对远程代码执行的新型缓解技术-任意代码守护卫士（ArbitraryCode
Guard）。在这篇文章中，我们将详细介绍Arbitrary Code Guard的工作机制，并利用内核代码注入攻击来测试这项缓解技术的有效性。**

## Arbitrary Code Guard（任意代码守护卫士）

微软将Arbitrary Code Guard（ACG）作为一个可选功能添加进了Windows操作系统中，它可以用来检测和防止下列情况的出现：

> 1\. 现有代码被恶意修改；
>
> 2\. 向一个数据段中写入并执行代码；

为了实现这两个目标，ACG会强制执行这条规则：内存不能同时拥有写入权限（W）和执行权限（X）。

ACG配合上代码完整性保护机制（Code Integrity Guard），Windows就可以防止攻击者将不安全或不可信的代码加载进内存之中了。

下面给出的是一份代码注入样本，它会将进程内存的状态修改为ACG想要防止出现的状态：

![任意代码保护与内核代码注入的那些事儿](https://image.3001.net/images/20180612/15288074381823.png!small)

我们可以看到，这些注入了代码的页面同时拥有执行和写入属性。

## ACG的工作流程

当系统[为特定进程创建好缓解方案](https://docs.microsoft.com/en-us/windows/security/threat-protection/overview-of-threat-mitigations-in-windows-10)时，会以下列注册表路径向注册表中添加一个键：

HKEY_LOCAL_MACHINE\Software\Microsoft\WindowsNT\CurrentVersion\Image File
Execution Options

接下来，Windows会在进程创建的过程中完成缓解方案的相关设置，下面给出的是进程创建过程中的调用栈：

    
    
    nt!PspAllocateProcess+0xb4b
    nt!NtCreateUserProcess+0x723
    nt!KiSystemServiceCopyEnd+0x13
    ntdll!NtCreateUserProcess+0x14
    KERNELBASE!CreateProcessInternalW+0x1b3f
    KERNELBASE!CreateProcessW

下面给出的是PspAllocateProcess函数的部分代码：

![任意代码保护与内核代码注入的那些事儿](https://image.3001.net/images/20180612/15288074659114.png!small)

其中，下面这两个函数主要负责加载缓解选项：

    
    
     PspReadIFEOMitigationOptions
     PspReadIFEOMitigationAuditOptions

这些函数会从注册表中读取下列键值：

    
    
    HKEY_LOCAL_MACHINE\Software\Microsoft\WindowsNT\CurrentVersion\Image File Execution Options

我们可以在进程监视器中看到以下活动：

![任意代码保护与内核代码注入的那些事儿](https://image.3001.net/images/20180612/1528807488103.png!small)

接下来，MitigationsFlagsValues的值将会存储在EPROCESS结构体中：

![任意代码保护与内核代码注入的那些事儿](https://image.3001.net/images/20180612/15288074988751.png!small)

### ACG如何检测和屏蔽动态代码？

正如之前的介绍，ACG会监控内存的分配情况，并防止同时拥有写入和执行权限，当我们尝试分配虚拟内存时，调用栈如下：

    
    
    nt!MiArbitraryCodeBlocked+0x30
    nt!MiAllocateVirtualMemory+0x96d
    nt!NtAllocateVirtualMemory+0x44
    nt!KiSystemServiceCopyEnd+0x13
    ntdll+0xa05c4

此时将会调用MiArbitraryCodeBlocked函数，该函数的功能如下图所示：

![任意代码保护与内核代码注入的那些事儿](https://image.3001.net/images/20180612/15288075337507.png!small)

我们可以看到，这个函数负责检测EPROCESS中的缓解选项，并判断是否允许分配虚拟内存。下面给出的是这个函数的流程图：

![任意代码保护与内核代码注入的那些事儿](https://image.3001.net/images/20180612/15288075432600.png!small)

该函数主要实现了下面三件事情：

> 1\. 获取EPROCESS，检测是否启用了缓解选项，并将MitigationsFlags分配进EPROCESS（偏移量0x828）。
>
> 2\. 检测ETHREAD中的CrossThreadFlags（0x6d0），以确定线程是否拥有内存分配权限或绕过缓解方案。
>
> 3\. 跟踪缓解结果，返回状态TATUS_DYNAMIC_CODE_BLOCKED（0xC0000604）。

## 内核代码注入

接下来我们一起看一看，如果我们尝试向内核注入代码时，ACG的表现如何。这里我们会使用恶意软件常用的两种内核代码注入技术：

> 1\. 创建一个新的线程并加载一个动态链接库文件（DLL）；
>
> 2\. 使用一个异步程序调用（APC）来向现有线程中加载一个DLL；

在这两种技术中，下面几个步骤是通用的：

> 1\. 绑定目标进程；
>
> 2\. 获取Ntdll地址；
>
> 3\. 获取LdrLoadDll地址；
>
> 4\. 通过shellcode分配虚拟内存；
>
> 5\. 通过shellcode调用LdrLoadDll；

在使用新的线程实现shellocde注入时，我们需要使用NtCreateThreadEx并在shellcode中调用LdrLoadDll。另一方面，如果我们想要使用一个APC来注入shellocde，我们则需要在相应线程中使用APC函数并通过shellcode调用LdrLoadDll。

在这两种注入方法中，我们需要在分配虚拟内存时同时分配写入和执行权限，并执行shellcode。正如之前所说的，ACG可以通过防止同时分配写入和执行权限来屏蔽代码注入。下面给出的是负责分配虚拟内存的代码：

![任意代码保护与内核代码注入的那些事儿](https://image.3001.net/images/20180612/15288075642746.png!small)

在调用ZwAllocateVirtualMemory之后设置断点（MiArbitraryCodeBlocked）。，我们将能够在windbg中看到下列信息：

![任意代码保护与内核代码注入的那些事儿](https://image.3001.net/images/20180612/15288075742522.png!small)

返回值为STATUS_DYNAMIC_CODE_BLOCKED，因此这两种代码注入技术都无法绕过ACG。

## 总结

对于防止用户模式或内核模式下的代码注入来说，ACG是一种非常好的选择，但ACG目前只是一种可选项，因此如果目标设备（进程）没有开启ACG的话，攻击者仍然能够实现代码注入。

### 参考资料

> 1\. Windows10
> 缓解方案改进（2016年美国黑帽黑客大会）：【[点我获取](https://www.youtube.com/watch?v=gCu2GQd0GSE)】
>
> 2\.
> 破解ACG的那些事儿（2017年Ekoparty安全大会）：【[点我获取](https://www.youtube.com/watch?v=gu_i6LYuePg)】

 *** 参考来源：[countercraft](https://www.countercraft.eu/blog/post/arbitrary-vs-kernel/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

