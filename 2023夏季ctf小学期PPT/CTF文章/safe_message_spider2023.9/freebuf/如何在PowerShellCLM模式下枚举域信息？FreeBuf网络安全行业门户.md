**本文我将快速简要的向大家介绍我近来一直在使用和拿来教学的技术。通过该技术你可以在没有获取RSAT和管理权限的情况下，使用Micorosft的PowerShell
ActiveDirectory模块。我是从[这篇博文](https://janikvonrotz.ch/2015/09/09/deploy-powershell-activedirectory-module-without-installing-the-remote-server-tools/)中了解到这种技术的。**

因此，如果你可以访问已安装模块的服务器（如DC），请将Microsoft.ActiveDirectory.Management.dll从
C:\Windows\Microsoft.NET\assembly\GAC_64\Microsoft.ActiveDirectory.Management复制到你自己的机器上，然后使用Import-Module cmdlet导入DLL：

    
    
    PS C:\> Import-Module C:\ADModule\Microsoft.ActiveDirectory.Management.dll -Verbose

![AD_Module.png](https://image.3001.net/images/20181110/1541808056_5be61fb80bcb3.png!small)

注意，如果你运行Get-Command -Module
ActiveDirectory，将不会返回任何内容。想要获取到，请从服务器以下位置复制模块目录：C:\Windows\System32\WindowsPowerShell\v1.0\Modules\ActiveDirectory\。然后，使用Import-Module命令，先导入DLL然后导入模块：

    
    
    PS C:\> Import-Module C:\ADModule\Microsoft.ActiveDirectory.Management.dll -Verbose
    PS C:\> Import-Module C:\AD\Tools\ADModule\ActiveDirectory\ActiveDirectory.psd1
    PS C:\> Get-Command -Module ActiveDirectory

使用cmdlet有许多好处，例如较低的AV检测率，覆盖范围广（在我之后的文章中我还将用到cmdlet），强大的过滤器，以及由Microsoft签名等。

我从Server 2016上传了一个模块副本到Github上：<https://github.com/samratashok/ADModule>

该模块可以在PowerShell约束语言模式（CLM）中完美运行。

![AD_Module_CLM.png](https://image.3001.net/images/20181110/1541808072_5be61fc8f3aa8.png!small)

好了，就那么多！就像我说的快速而简短~

***参考来源：[labofapenetrationtester](https://www.labofapenetrationtester.com/2018/10/domain-enumeration-from-PowerShell-CLM.html)，FB小编secist编译，转载请注明来自FreeBuf.COM**

