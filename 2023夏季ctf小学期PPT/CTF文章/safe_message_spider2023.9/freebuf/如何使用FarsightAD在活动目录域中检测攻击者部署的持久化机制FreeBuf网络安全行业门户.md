![](https://image.3001.net/images/20221220/1671538748_63a1a83c394c06bc0762f.jpeg!small)

## 关于FarsightAD

FarsightAD是一款功能强大的PowerShell脚本，该工具可以帮助广大研究人员在活动目录域遭受到渗透攻击之后，检测到由攻击者部署的持久化机制。

该脚本能够生成并导出各种对象及其属性的CSV/JSON文件，并附带从元数据副本中获取到的时间戳信息。除此之外，如果使用了复制权限执行该工具的话，则可以利用目录复制服务（DRS）协议来检测完全或部分隐藏的对象。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地

    
    
    git clone https://github.com/Qazeer/FarsightAD.git

## 工具要求

FarsightAD需要[ _PowerShell_ _7_](https://docs.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows)以及对应版本的ActiveDirectory模块。在Windows 10/11操作系统上，可以通过[
_可选功能_](https://docs.microsoft.com/en-us/troubleshoot/windows-server/system-management-components/remote-server-administration-tools)来安装该模块。

如果安装成功，则可以使用下列命令来更新该模块：

    
    
    Add-WindowsCapability -Online -Name Rsat.ServerManager.Tools~~~~0.0.1.0

如果模块成功更新完成，那么Get-Command Get-ADObject则会返回下列信息：

    
    
    CommandType     Name                                               Version    Source
    
    -----------     ----                                               -------    ------    
    Cmdlet          Get-ADObject                                       1.0.X.X    ActiveDirectory

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Qazeer/FarsightAD.git

## 工具基础使用

    
    
    . .\FarsightAD.ps1
    
     
    
    Invoke-ADHunting [-Server <DC_IP | DC_HOSTNAME>] [-Credential <PS_CREDENTIAL>] [-ADDriveName <AD_DRIVE_NAME>] [-OutputFolder <OUTPUT_FOLDER>] [-ExportType <CSV | JSON>]

## 工具使用演示

在下列使用样例中，我们将进行完整/部分的隐藏对象检测。

 **添加一个完整的隐藏用户：**

**![](https://image.3001.net/images/20221220/1671538801_63a1a8716f60d3f6deef1.gif)**

 **隐藏一个用户的SID History属性：**

**![](https://image.3001.net/images/20221220/1671538815_63a1a87f9f772c6e06041.gif)**

 **使用Export-ADHuntingHiddenObjectsWithDRSRepData发现完整/部分隐藏用户：**

![](https://image.3001.net/images/20221220/1671538826_63a1a88a12ec924280975.gif)

## 许可证协议

本项目的开发与发布遵循[ _CC_
_0-1.0_](https://github.com/Qazeer/FarsightAD/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **FarsightAD** ：【[ _GitHub传送门_](https://github.com/Qazeer/FarsightAD)】

## 参考资料

> [
> _https://github.com/Qazeer/FarsightAD/blob/main/SANS_DFIR_Summit_2022-Hunting_for_Active_Directory_persistence-v1.2.pdf_](https://github.com/Qazeer/FarsightAD/blob/main/SANS_DFIR_Summit_2022-Hunting_for_Active_Directory_persistence-v1.2.pdf)
>
> [ _https://docs.microsoft.com/en-us/troubleshoot/windows-server/system-> management-components/remote-server-administration-> tools_](https://docs.microsoft.com/en-us/troubleshoot/windows-server/system-> management-components/remote-server-administration-tools)
>
> [
> _https://github.com/vletoux/MakeMeEnterpriseAdmin_](https://github.com/vletoux/MakeMeEnterpriseAdmin)
>
> [
> _https://github.com/gentilkiwi/mimikatz_](https://github.com/gentilkiwi/mimikatz)
>
> [
> _https://github.com/b4rtik/SharpKatz_](https://github.com/b4rtik/SharpKatz)
>
> [
> _https://www.powershellgallery.com/packages/ADComputerKeys/1.0.0/Content/ADComputerKeys.psm1_](https://www.powershellgallery.com/packages/ADComputerKeys/1.0.0/Content/ADComputerKeys.psm1)
>
> [ _https://posts.specterops.io/certified-pre-> owned-d95910965cd2_](https://posts.specterops.io/certified-pre-> owned-d95910965cd2)
>
> [ _https://www.riskinsight-wavestone.com/en/2021/06/microsoft-adcs-abusing-> pki-in-active-directory-environment/_](https://www.riskinsight-> wavestone.com/en/2021/06/microsoft-adcs-abusing-pki-in-active-directory-> environment/)
>
> [ _https://github.com/adbertram/Random-PowerShell-> Work/blob/master/ActiveDirectory/ActiveDirectorySPN.psm1_](https://github.com/adbertram/Random-> PowerShell-Work/blob/master/ActiveDirectory/ActiveDirectorySPN.psm1)
>
> [ _https://twitter.com/_Qazeer_](https://twitter.com/_Qazeer)

