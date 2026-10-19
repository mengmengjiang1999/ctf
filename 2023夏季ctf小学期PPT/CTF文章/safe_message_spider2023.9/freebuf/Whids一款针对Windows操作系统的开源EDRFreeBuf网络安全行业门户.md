![](https://image.3001.net/images/20221101/1667312786_63612c926e48db62e5d93.png!small)  

## 关于Whids

Whids是一款针对Windows操作系统的开源EDR，该工具所实现的检测引擎基于先前的[
_Gene_](https://github.com/0xrawsec/gene)项目构建，并专门设计可以根据用户定义的规则匹配Windows事件。

## 功能特性

> 1、为社区提供一款功能强大且开源的Windows EDR；
>
> 2、支持检测规则透明化，允许分析人员了解规则被触发的原因；
>
> 3、通过灵活的规则引擎提供强大的检测原语；
>
> 4、通过大幅缩短检测和数据收集之间的时间来优化事件响应流程；
>
> 5、支持整合ATT&CK框架；
>
> 6、可以与任何防病毒产品共存（建议与MS Defender一起运行）；
>
> 7、有一个强大的管理API来简化大型部署的管理（目前还没有GUI）；
>
> 8、提供了非常强大且可定制的检测引擎；
>
> 9、专为高吞吐量而设计；
>
> 10、易于与其他工具集成（Splunk、ELK、MISP…）；

## 工具架构

![](https://image.3001.net/images/20221101/1667312807_63612ca79f464cdd4fbb2.png!small)

注意：EDR代理可以单独运行（可以不用跟EDR管理器连接）

## 工具运行机制

![](https://image.3001.net/images/20221101/1667312816_63612cb03d7e7eb06c247.png!small)

## 工具依赖

首先，我们需要安装并配置好Sysmon【[ _参考资料_](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon)】。接下来，完成Sysmon的配置，并记录所有的ProcessCreate和ProcessTerminate事件。最后，记录下Sysmon代码的路径，之后需要使用到。

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，并自行完成工具编译：

    
    
    git clone https://github.com/0xrawsec/whids.git

除此之外，我们还可以直接访问该项目的【[
_Releases页面_](https://github.com/0xrawsec/whids/releases)】直接下载最新版本的Whids可执行文件。

## 工具配置

为了最大化Whids的功能，我们需要做以下工具配置：

> 1、启用PowerShell模块日志功能：gpedit.msc -> Computer Configuration\Windows
> Settings\Security Settings\Advanced Audit Policy Configuration\System Audit
> Policies\System\Audit Security System Extension -> Enable；
>
> 2、启用文件系统审计功能：gpedit.msc -> Computer Configuration\Windows Settings\Security
> Settings\Advanced Audit Policy Configuration\System Audit Policies\Object
> Access\Audit File System -> Enable；
>
> 3、如果还需要在设备上运行反病毒产品的话，建议使用Microsoft Defender；

## 工具使用

### EDR终端代理（Whids.exe）

下载最新版本的Whids，然后以管理员权限运行manage.bat，并按照提示运行即可。

### EDR管理器

EDR管理器可以在不同平台上安装，预构建代码提供了Windows、Linux和Darwin平台的可执行文件。接下来，按照下列步骤操作即可：

> 1、如果需要使用HTTPS，则需要创建TLS证书；
>
> 2、然后创建一个[
> _配置文件_](https://github.com/0xrawsec/whids/blob/master/doc/configuration.md)；
>
> 3、最后运行代码即可；

## 许可证协议

本项目的开发与发布遵循[ _AGPL_
_-3.0_](https://github.com/0xrawsec/whids/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **Whids** ：【[ _GitHub传送门_](https://github.com/0xrawsec/whids)】

## 参考资料

> [ _https://github.com/0xrawsec/gene_](https://github.com/0xrawsec/gene)
>
> [ _https://docs.microsoft.com/en-> us/sysinternals/downloads/sysmon_](https://docs.microsoft.com/en-> us/sysinternals/downloads/sysmon)
>
> [ _https://attack.mitre.org/_](https://attack.mitre.org/)
>
> [
> _https://validator.swagger.io/?url=https://raw.githubusercontent.com/0xrawsec/whids/master/doc/admin.openapi.json_](https://validator.swagger.io/?url=https:/raw.githubusercontent.com/0xrawsec/whids/master/doc/admin.openapi.json)
>
> [ _https://www.fireeye.com/blog/threat-> research/2016/02/greater_visibilityt.html_](https://www.fireeye.com/blog/threat-> research/2016/02/greater_visibilityt.html)
>
> [ _https://docs.microsoft.com/en-us/windows/security/threat-> protection/windows-defender-antivirus/troubleshoot-windows-defender-> antivirus#windows-defender-av-ids_](https://docs.microsoft.com/en-> us/windows/security/threat-protection/windows-defender-> antivirus/troubleshoot-windows-defender-antivirus#windows-defender-av-ids)
>
> [ _https://rawsec.lu/doc/gene/1.6/_](https://rawsec.lu/doc/gene/1.6/)
>
> [ _https://github.com/ion-storm/sysmon-edr_](https://github.com/ion-> storm/sysmon-edr)
>
> [
> _https://github.com/ComodoSecurity/openedr_](https://github.com/ComodoSecurity/openedr)
>
> [
> _https://github.com/marcosd4h/sysmonx_](https://github.com/marcosd4h/sysmonx)

