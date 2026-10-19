![0.jpg](https://image.3001.net/images/20200218/1582026804_5e4bd0349ad92.jpg!small)

**在这篇文章中，我们将讨论Windows Service Tracing中的一个任意文件移动漏洞。在我们的测试过程中，该漏洞将影响从Windows
Vista至Windows 10的所有版本操作系统，但是Windows XP也很有可能会受此漏洞影响，因为XP系统中也有这项功能。**

##  Windows Service Tracing

Service
Tracing这项服务在Windows平台上历史悠久，早在XP就已经引入了这个功能。该功能可以给分析人员提供当前正在运行的服务及模块的相关基本调试信息，任意本地用户都可以通过编辑注册表键值（`HKLM\SOFTWARE\Microsoft\Tracing`）来对其进行配置。

在Windows中，每一个服务或模块都对应了一个注册表键，每一个键包含六个值，我们主要针对其中的三个值，即`EnableFileTracing`（启用/禁用“tracing”）、`FileDirectory`（设置日志输出文件的地址）和`MaxFileSize`（设置日志文件的最大文件大小）。

EnableFileTracing启用之后，目标服务将会开始向我们所选择的文件路径写入其日志文件，当日志文件超过`MaxFileSize`的大小时，它将会被移动（即将原本的.LOG后缀替换为.OLD），并在原处创建一个新的日志文件。

安全研究人员James
Forshaw曾发布过一个[符号链接测试工具](https://github.com/googleprojectzero/symboliclink-testing-tools)，漏洞利用也非常简单。我们只需要将目标目录设置为挂载点，指向\RPC Control对象目录，然后创建如下2个符号链接即可：

> 1、创建一个从MODULE.LOG到我们某个文件的符号链接（该文件大小必须大于`MaxFileSize`）；
>
>
> 2、创建一个从MODULE.OLD到系统任意文件的符号链接，例如“`C:\Windows\System32\WindowsCoreDeviceInfo.dll`”。

最后，我们需要以“`NT AUTHORITY\SYSTEM`”权限运行的服务作为目标来触发文件“移动”操作，然后利用`Update Session
Orchestrator`服务来获取任意代码执行权限。

##  服务的Tracing功能

文章开头介绍过，任意本地用户都可以通过编辑注册表键值（`HKLM\SOFTWARE\Microsoft\Tracing`）来配置Service
Tracing功能。

此时，通过使用Windows Sysinternals工具集中的AccessChk工具，我们可以看到普通用户拥有相关注册表项下几乎所有子项的读写权限：

![1.png](https://image.3001.net/images/20200218/1582026818_5e4bd042e98a1.png!small)

接下来，我们将以`RASTAPI`模块为例来进行漏洞利用演示。IKEEXT服务会使用这个模块，因此我们可以通过启动任意VPN连接来触发事件日志行为。相关注册表键值的默认设置如下图所示，其他的服务及模块也使用的是完全相同的值：

![2.png](https://image.3001.net/images/20200218/1582026879_5e4bd07fd20a1.png!small)

从本地攻击者的角度来看，下面的值会有利用价值：

参数名称  |  值范围  |  描述  
---|---|---  
EnableFileTracing  |  0 - 1  |  开始/停止写入日志文件  
FileDirectory  |  A String  |  目录的绝对路径  
MaxFileSize  |  0x00000000 - 0xffffffff  |  输入日志文件的最大文件大小  
  
通过设置这些值，我们可以做到：

1、将`EnableFileTracing`修改为0或者1，强制特定服务或模块开始/停止将调试信息写入日志文件。

2、通过`FileDirectory`设置日志文件的具体位置。

3、通过`MaxFileSize`设置输出文件大小的最大值。

需要注意的是，我们无法选择输出日志文件的名称，日志文件名称取决于被调用服务或模块的名称，但我们可以通过符号链接来解决这个问题。

##  任意文件移动漏洞

###  场景一：`MaxFileSize`为默认值

在这个场景中，我们将路径“`C:\LOGS`”设置为日志文件的输出目录，并启用“`File Tracing`”功能：

![3.png](https://image.3001.net/images/20200218/1582026913_5e4bd0a18d799.png!small)

接下来，我们需要生成一些事件来触发目标服务开始写入日志文件。这里我们可以使用`rasdial`命令并配合`PBK`文件来初始化一个VPN连接：

![4.png](https://image.3001.net/images/20200218/1582026918_5e4bd0a64096f.png!small)

成功了！日志文件由“`NT AUTHORITY\SYSTEM`”写入，当前日志文件大小约为24KB：

![5.png](https://image.3001.net/images/20200218/1582026935_5e4bd0b7767cd.png!small)

###  场景二：`MaxFileSize `\- 自定义值

在之前的测试中，我们可以看到输出日志文件的大小约为24KB，因此这一次，我们要将MaxFileSize的值设置为“0x4000”（16384个字节大小），然后重新进行测试：

![6.png](https://image.3001.net/images/20200218/1582026946_5e4bd0c2104e5.png!small)

根据“`Process Monitor`”捕捉到的事件，我们可以知道：

1、服务会获取日志文件的基础信息。我们可以看到`EndOfFile`的偏移量为23,906，这也是目前文件的大小值。由于我们设定的最大文件大小值为`16,384`个字节，因此这里系统会判断没有更多空间可用。

2、服务调用`SetRenameInformationFile`，其中`FileName=C:\LOGS\RASTAPI.OLD`。由于系统认为当前文件已满，因此会将“`C:\LOGS\RASTAPI.LOG`”更改为“`C:\LOGS\RASTAPI.OLD`”。

3、服务创建一个新的“`C:\LOGS\RASTAPI.LOG`”文件，开始写入数据。

![7.png](https://image.3001.net/images/20200218/1582027016_5e4bd1082f043.png!small)

这里的文件移动操作由“`NT
AUTHORITY\SYSTEM`”完成。因此，我们可以利用这一点将用户所有的文件移动到目标系统中的任意位置，比如说“`C:\Windows\System32\`”。

##  漏洞利用

###  漏洞利用过程如下：

1、创建（或拷贝）一个大小超过0x8000（32,768）个字节的文件。

2、创建一个新的目录，例如“`C:\EXPLOIT\mountpoint\`”，然后将其设置为一个指向“`\RPC Control`”的挂载点。

3、创建下列符号链接：

    
    
    \RPC Control\RASTAPI.LOG -> \??\C:\EXPLOIT\FakeDll.dll (owner = current user)\RPC Control\RASTAPI.OLD -> \??\C:\Windows\System32\WindowsCoreDeviceInfo.dll

4、在注册表中配置下列值：

    
    
    FileDirectory = C:\EXPLOIT\mountpointMaxFileSize = 0x8000 (32,768‬ bytes)EnableFileTracing = 1

5、使用Windows API中的`RasDial`函数，触发与`RASTAPI`相关的事件。

6、触发`Update Session Orchestrator`服务，并利用“`NT AUTHORITY\SYSTEM`”权限加载相关DLL。

###  演示样例

![Image](https://image.3001.net/images/20200220/15821820911372.gif!small)

##  参考资料

> 1、<https://portal.msrc.microsoft.com/en-US/security-> guidance/advisory/CVE-2020-0668>
>
> 2、<https://googleprojectzero.blogspot.com/2018/04/windows-exploitation-> tricks-exploiting.html>
>
> 3、<https://github.com/googleprojectzero/symboliclink-testing-tools>
>
> 4、<https://github.com/itm4n/UsoDllLoader>

***参考来源：[itm4n](https://itm4n.github.io/cve-2020-0668-windows-service-tracing-eop/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

