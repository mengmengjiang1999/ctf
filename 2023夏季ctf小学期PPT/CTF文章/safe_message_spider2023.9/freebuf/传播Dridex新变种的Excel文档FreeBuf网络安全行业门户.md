Dridex 也称为 Bugat 或 Cridex，可 **以从失陷主机上窃取敏感信息并执行恶意模块（DLL）的木马。**

FortiGuard Labs 最近捕获了新的网络钓鱼邮件活动，其中包括特制的 Excel 文档附件。分析研究后，发现一旦在受害者的机器上打开了恶意
Excel 文档就会下载 Dridex 的新变种。

## Dridex 钓鱼邮件

带有 Excel 附件的 Dridex 钓鱼邮件如下所示：

![](https://image.3001.net/images/20210911/1631373281_613cc7e118d23ddf69903.png!small)

钓鱼邮件伪装成向客户发送的进口关税数据，要求用户打开 Excel 附件（HF7.TRANS 2021.08.09.xlsb）查看详细信息。

## 宏代码解析

收件人打开 Excel 文档后会在顶部以红色粗体显示要求用户启用宏代码。Excel
则会显示黄色警告栏，通知用户当前已经禁用了宏，意味着启用内容可能存在风险。

![](https://image.3001.net/images/20210911/1631373329_613cc811d15b7aad68614.png!small)

Excel 文件内部不仅使用了自动运行的 VBA 代码（Workbook_Open），还使用了 Excel 4.0 宏代码。

    
    
    Sub Workbook_Open()ActiveWorkbook.Sheets("Macro1").Range("A1").Value=Environ("allusersprofile")& "\KgmsgJbgP.sct"End Sub

值 `Environ("allusersprofile")& "\KgmsgJbgP.sct"`设置成名为 `Macro1`的工作表的 `$A$1`单元格。

`Macro1`是一个隐藏的工作表，包含并执行 Excel 4.0 宏代码，在文件 `xl\workbook.xml`中定义。

![](https://image.3001.net/images/20210911/1631373354_613cc82a3cf43668698fc.png!small)

Excel 4.0 宏代码使用各种单元格中的公式执行代码，给定起始单元格后会从上到下、从左到右执行代码。本例代码从
`Macro1!$A$4`单元格开始执行。

宏代码提取的数据是带有一段 VBScript 代码的 HTML 应用程序（.hta 文件）。最后调用 `mshta`命令执行
`KgmsgJbgP.sct`文件，即 `=EXEC(CONCATENATE("mshta ", CHAR(34), A1, CHAR(34)))`。

## 下载 Dridex 的 HTML 程序

VBScript 代码包含十个 URL 组成的数组，这些 URL 与 Dridex 有关。循环从十个 URL 下载 Dridex 到本地文件
`%ALLUSERSPROFILE%\\icXBOuZukiASGnpfVowZ.dll`。该文件也硬编码在 VBScript 代码中，当 Dridex
下载成功后会执行 `wmic.exe`来创建一个新的 `rundll32.exe`进程。

![](https://image.3001.net/images/20210911/1631373402_613cc85adbd0503d2666e.png!small)

简化后的代码如下所示：

    
    
    CreateObject("Wscript.Shell").Exec("wmic process call create \"Rundll32.exe %ALLUSERSPROFILE%\\icXBOuZukiASGnpfVowZ.dll ReportDeviceAdd\"")

最后，Rundll32.exe 加载 Dridex 的 `icXBOuZukiASGnpfVowZ.dll`并调用其名为
`ReportDeviceAdd`的导出函数来执行其恶意功能。

## 深入理解 Dridex

Dridex 包含两个导出函数：

> DllEntryPoint 是 DLL 的入口函数
>
> FWroeeWqoinnmw 是恶意函数

![](https://image.3001.net/images/20210911/1631373429_613cc875c998abfcb228c.png!small)

Dridex 最终的导出函数列表如下所示：

![](https://image.3001.net/images/20210911/1631373451_613cc88bc197066d08344.png!small)

加载 Dridex 的步骤如下所示：

> Rundll32.exe 调用 LoadLibrary() 将 DLL 加载到内存中
>
> 调用 DLL 的入口点函数 DllEntryPoint 来初始化模块，包含脱壳
>
> 调用函数名 ReportDeviceAdd 中的 GetProcAddress，从初始化的模块中获取函数地址
>
> Rundll32.exe 调用函数地址

## 反分析

Dridex 使用了多种反分析技术：

> 所有 API 都被隐藏，通过 API 哈希调用
>
> 所有常量字符串都是加密的，在使用前解密
>
> 某些 API 通过触发异常（0x80000003）在异常处理函数中捕获异常进行调用

## 加密数据包

Dridex 将从失陷主机窃取的敏感数据加密发送到 C&C 服务器。

![](https://image.3001.net/images/20210911/1631373475_613cc8a35dcb515be2a85.png!small)

红色将数据包分割成多个字段，每个字段的含义如下所示：

![image.png-48.7kB](https://image.3001.net/images/20210911/1631373498_613cc8ba944cdc3f87b09.png!small)

## C&C 通信

和 Dridex 保持一致，C&C 服务器的 IP 地址和端口都硬编码在数据中。

![image.png-25.7kB](https://image.3001.net/images/20210911/1631373499_613cc8bb34edd10ac69f5.png!small)

循环选择一个 IP 地址和端口，与 C&C 服务器成功建立连接就会使用使用它进行通信。

`0x18F8C844`是第一个数据包的数据包 ID。收集的数据包括安装的软件（软件名称和版本）和失陷主机中定义的所有环境变量。

通过
`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall`查看安装软件。通过
`GetEnvironmentStringsW()`获取环境变量。

Dridex 将加密数据包通过 HTTP POST 方法发送到 C&C 服务器，并使用
InternetConnectW()、HttpOpenRequestW()、HttpSendRequestW()、HttpQueryInfoW() 和
InternetReadFile() 来发送和接收数据。

整个过程如下所示：

![](https://image.3001.net/images/20210911/1631373615_613cc92f54735cb5a5d9c.png!small)

## 持久化

得到 C&C 服务器的响应后，将会发送第二个数据包（0x11041F01）。Dridex
通过数据包的前四个字节作为哈希码验证响应数据包。成功接收后发送（0xD3EF7577）通知 C&C 服务器成功接收。

![](https://image.3001.net/images/20210911/1631373654_613cc956447064ea74e57.png!small)

Dridex 会从 `%windir%\system32`中随机选择一对 Windows EXE 程序和 DLL 文件，通过恶意软件覆盖 DLL  
文件。程序启动就会拉取恶意 DLL 执行。

![](https://image.3001.net/images/20210911/1631373708_613cc98ced9b3341907cd.png!small)

Dridex 创建计划任务实现持久化，每半个小时触发执行。计划任务名为 `vzwbtojdsmg`：

![](https://image.3001.net/images/20210911/1631373788_613cc9dcaeb0bc5b51497.png!small)

在 Dridex 退出前，会发送 ID 为 `0x69BE7CEE`的数据包，告知 C&C 服务器已经成功安装。

![](https://image.3001.net/images/20210911/1631373809_613cc9f15c4bbe8cdb6a1.png!small)

## IOC

> 103.75.201.2:443  
> 158.223.1.108:6225  
> 165.22.28.242:4664  
> 59C8D87A450F0647BEA930EBA1AA692B75D82DEF1358F1601C4FE9A561B4707E  
> C8065BD2A1443FF988E9BA95022554F6EE302E9BCB4082C3D9B2B8D74C5A4BE5  
> 6556E4029CF50C9538F4E02D0BCCA5356F28E6870E62838E164020A31B3DF096

## 参考来源

> [Fortinet﻿](https://www.fortinet.com/blog/threat-research/new-dridex-> variant-being-spread-by-crafted-excel-document)

