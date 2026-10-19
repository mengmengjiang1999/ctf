***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **在近期的一项渗透测试实践中，我们在最新版本赛门铁克Management
Agent（Altiris）中发现了一个安全漏洞，而这个安全漏洞将允许攻击者实现提权。**

## 概述

![](https://image.3001.net/images/20181118/1542551011_5bf175e34f495.png!small)

当Altiris代理执行任务扫描时（例如软件扫描），SYSTEM级服务会在扫描任务执行完毕之后向NSI和OutBox目录重新申请权限。即：

    
    
    C:\ProgramFiles\Altiris\Inventory\Outbox
    
    C:\ProgramFiles\Altiris\Inventory\NSI

申请到的权限会给‘Everyone’组成员提供这两个文件目录的完整控制权，并允许任何一名标准用户创建其他代替目录的链接。因此，‘Everyone’权限将会赋予给其他代替目录，从而该目录下的任何一份文件或文件夹都会继承这种完全控制权限。

这也就意味着，任何一名低权限用户都可以在安装了Symantec Management Agent v7.6,
v8.0或v8.1RU7的终端设备上实现权限提升。

## 分析&发现

在执行渗透测试的过程中，我们经常会遇到各种各样安装了不同类型终端软件的主机设备。这些软件很可能就是我们的切入点，因为我们可以利用它们来实现提权，或者实现横向渗透。

在这些终端管理软件中，我们经常会见到的就是赛门铁克的Altiris。这个软件是一款终端管理框架，它不仅可以帮助组织或管理员确保设备及时安装了最新版本的操作系统补丁或软件更新，还可以检查用户或组权限。

我们这一次测试的版本是v7.6，不过赛门铁克方面也证实了，在最新补丁发布之前的所有Altiris版本都会受到这个问题的影响。

![分析&发现](https://image.3001.net/images/20181118/1542551024_5bf175f0b47fd.png!small)

我们发现，Altiris文件架构中的目录都应用了‘Everyone-完整控制’权限。这些目录看起来存储的是合法内容，例如扫描配置文件和XML文件等等。但是这些目录和文件的权限都使用了一行简单的PowerShell代码，并允许我们查看任意Windows主机的ACL权限：

    
    
    Get-ChildItemC:\ -Recurse -ErrorAction SilentlyContinue | ForEach-Object {try {Get-Acl -Path$_.FullName | Select-Object pschildname,pspath,accesstostring}catch{}}|Export-Csv C:\temp\acl.csv -NoTypeInformation

在查看这些文件目录的时间戳时，我们发现这些目录中的文件时间戳每天都会发生变化。深入研究之后，我们发现这些文件会在Altiris执行完系统或软件扫描之后被修改。现在，根据不同组织对配置和扫描任务的需求，这样的情况每天还有可能发生若干次。

接下来的事情就非常有趣了，当我们发现了这种特性之后，我们打算看看Cylance近期披露的攻击方式在这里是否有效【[参考资料](https://www.atredis.com/blog/cylance-privilege-escalation-vulnerability)】。

下面给出的是NSI文件夹的目录权限，这个目录的权限跟Outbox目录是相同的：

![Outbox目录](https://image.3001.net/images/20181118/1542551036_5bf175fcd4951.png!small)

接下来，我们可以尝试使用James
Forshaw的符号连接测试工具来将该目录重定向到其他位置，然后创建一个其他目录的挂载点，看看这个目录下的文件是否会被改写，而事实是我们成功了。当然了，我们还可以使用[sysinternals](https://docs.microsoft.com/en-us/sysinternals/)的链接工具，但是这个工具要求源目录不存在，但是我们这里的目录已经存在并拥有‘Everyone’权限了。比如说：

![拥有‘Everyone’权限](https://image.3001.net/images/20181118/1542551043_5bf17603ee984.png!small)

如果我们把这个目录删除，我们就没有权限去实现这种攻击了。而James Forshaw的工具允许覆盖已存在的目录：

![没有权限去实现这种攻击](https://image.3001.net/images/20181118/1542551050_5bf1760a9ccf9.png!small)

在这种攻击技术中还可以使用另一个名叫mklink.exe的Windows工具，但是该工具需要高级权限，这里就不适用了，因为我们要做的就是提权。

## 攻击分析

我们应该如何实现攻击呢？别担心，我们有很多种方法来利用这个漏洞，但是最简单的方法就是去尝试覆盖整个Altiris根目录(“C:\Program
Files\Altiris\AlritisAgent\”)权限，这样我们就可以修改SYSTEM账号下运行的服务代码了，也就是AeNXSAgent.exe。

下面的截图显示的是在挂载点修改权限之前Altiris Agent目录以及AsNXSAgent.exe服务代码的权限：

![AsNXSAgent.exe服务代码的权限](https://image.3001.net/images/20181118/1542551070_5bf1761e8d64e.png!small)

![AsNXSAgent.exe服务代码的权限](https://image.3001.net/images/20181118/1542551070_5bf1761ea0e14.png!small)

接下来，我们创建一个指向Altiris Agent目录的挂载点，运行之后我们就可以让每一个文件拥有完整权限了，实现起来非常简单。这里我们可以使用James
Forshaw的[符号链接测试工具](https://github.com/google/symboliclink-testing-tools)来创建和验证挂载点。

![创建和验证挂载点](https://image.3001.net/images/20181118/1542551077_5bf17625e7864.png!small)

接下来，我们只需要目标主机再次执行扫描任务，下面的截图显示的就是我们的成果：

![成果](https://image.3001.net/images/20181118/1542551085_5bf1762db92ef.png!small)

当我们拿到了AeXNSAgent.exe的完整控制权之后，我们就可以替换服务代码，然后重启主机来获取SYSTEM权限了。

## 总结

Altiris Management Agent v7.6, v8.0和8.1 RU7均会受到该漏洞的影响，我们强烈建议大家尽快升级更新自己的软件。

如果大家还有利用该漏洞的新姿势，欢迎大家在下方评论区踊跃讨论。

 *** 参考来源：[nettitude](https://labs.nettitude.com/blog/cve-2018-5240-symantec-management-agent-altiris-privilege-escalation/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

