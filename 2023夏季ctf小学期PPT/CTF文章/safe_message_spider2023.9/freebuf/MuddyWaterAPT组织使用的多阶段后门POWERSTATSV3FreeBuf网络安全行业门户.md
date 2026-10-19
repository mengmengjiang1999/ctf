**近期，我们又对MuddyWater APT组织的活动进行了分析，并且发现他们使用了新的攻击工具以及更加有效的Payload，这也表明MuddyWater
APT仍然在不断地优化他们的攻击方案。在这篇文章中，我们将对MuddyWater
APT所使用的新型多阶段后门和Android恶意软件变种等攻击组件进行分析。**

在其中的一次攻击活动中，他们向约旦的一所大学和土耳其政府发送了网络钓鱼邮件，虽然邮件发件人的合法性是有保证的，但攻击者已经提前入侵了这个电子邮件账号，并欺骗目标用户安装恶意软件（通过邮件中的钓鱼链接或恶意附件）。

![](https://image.3001.net/images/20190707/1562483215_5d219a0f0d7cc.png!small)

![](https://image.3001.net/images/20190707/1562483219_5d219a13cb8c4.png!small)

我们通过分析发现，攻击者采用了一种名为POWERSTATS
v3的新型多阶段PowerShell后门（趋势科技检测为Trojan.PS1.POWERSTATS.C）。钓鱼邮件中包含了一个恶意VBE文件，使用了微软脚本编码工具进行编码，其中包含恶意宏。这个VBE文件中，包含了一段Base64编码的数据块，其中包含的是一个经过混淆处理的PowerShell脚本，而且会自动执行。这段数据会被解码并存储至%PUBLIC%目录中，文件后缀名为.jpeg和.png。PowerShelldiamagnetic接下来会使用自定义字符串对代码进行混淆处理：

![](https://image.3001.net/images/20190707/1562483225_5d219a19e803f.jpg!small)

后门首先会获取目标设备的操作系统信息，并将其存储在日志文件中。经过反混淆后的部分后门代码段如下：

![](https://image.3001.net/images/20190707/1562483232_5d219a20288c0.jpg!small)

这个文件会被上传至C2服务器中，每一台目标设备都会生成一个个随机的GUID码，用于帮助攻击者识别目标设备。接下来，恶意软件变种会开启循环模式，不断地获取GUID命名的文件，如果找到了文件，就会在目标设备上使用PowerShell.exe进程来下载并执行。

攻击者还会通过发送异步命令来开启第二阶段的攻击，比如说，可以下载另一个后门Payload，并在目标设备上安装：

![](https://image.3001.net/images/20190707/1562483237_5d219a2569775.png!small)

攻击者下载第二阶段攻击Payload时，需要下列命令的支持：

> 1、 获取屏幕截图；
>
> 2、 通过cmd.exe执行命令；
>
> 3、 如果没有检测到关键词，恶意软件变种会假设输入内容为PowerShell代码，并通过“Invoke-Expression”工具来执行。

![](https://image.3001.net/images/20190707/1562483243_5d219a2bccb9d.png!small)

C2通信通过PHP脚本实现，其中包含硬编码令牌，以及一系列后端函数，例如sc（屏幕截图）、res（命令执行结果）、reg（注册新用户）和uDel（遇到错误时删除自身）等等。

![](https://image.3001.net/images/20190707/1562483249_5d219a31d5d54.png!small)

## 2019年上半年MuddyWater的其他活动

MuddyWater APT组织一直都在开发新的技术来进行更加“高端”的攻击。当然了，前文所分析的活动并不是唯一一个使用了POWERSTATS
v3的攻击活动，我们还发现他们在其他活动中改进了Payload的传递方式以及感染的恶意文件类型。

![](https://image.3001.net/images/20190707/1562483258_5d219a3a7e1b4.png!small)

在2019年1月份，我们还发现攻击者使用了SHARPSTATS（Trojan.Win32.SHARPSTATS.A），一种基于.NET的后门，支持下载、上传和运行函数。同月，又出现了基于Delphi编程语言开发的后门DELPHSTATS(Trojan.Win32.DELPSTATS.A)。DELPHSTATS会在其通过PowerShell.exe进程执行自身之前，向C2服务器请求一个.dat文件，并且实现了自定义PowerShell脚本：

![](https://image.3001.net/images/20190707/1562483263_5d219a3f2e628.png!small)

![](https://image.3001.net/images/20190707/1562483268_5d219a44b3a08.png!small)

当然了，我们还遇到了经过重度混淆处理的POWERSTATS v2（Trojan.PS1.POWERSTATS.B）代码：

![](https://image.3001.net/images/20190707/1562483273_5d219a4910821.png!small)

反混淆处理后，我们发现后门的主循环会请求不同的URL来从C2服务器获取命令执行的结果：

![](https://image.3001.net/images/20190707/1562483278_5d219a4e69144.png!small)

攻击者还使用了不同的后渗透利用工具

![](https://image.3001.net/images/20190707/1562483295_5d219a5f51e55.png!small)

## 总结与安全建议

虽然MuddyWater目前还没有涉及到任何0
day和高级恶意软件变种，但是他们仍然能够成功入侵目标设备。当然了，攻击者还使用了钓鱼邮件来作为其中一种感染向量，而且攻击成功率欸长高。除了使用智能邮件安全解决方案之外，组织还需要对员工进行反垃圾邮件（钓鱼邮件）的基础培训。

【[点我访问](https://documents.trendmicro.com/assets/white_papers/wp_new_muddywater_findings_uncovered.pdf)】完整报告。

 *** 参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/muddywater-resurfaces-uses-multi-stage-backdoor-powerstats-v3-and-new-post-exploitation-tools/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

