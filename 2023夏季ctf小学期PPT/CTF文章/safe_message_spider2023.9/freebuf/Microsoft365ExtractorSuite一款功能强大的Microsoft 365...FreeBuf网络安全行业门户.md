![](https://image.3001.net/images/20220711/1657536063_62cbfe3f1cc056d898677.jpeg!small)

## 关于Microsoft 365 Extractor Suite

Microsoft 365 Extractor Suite是一款功能强大的Microsoft
365安全审计工具，该工具基于PowerShell开发，可以帮助广大研究人员对Microsoft
365进行安全研究，并获取相关的审计日志报告。该工具主要由以下两个不同的功能脚本组成：

> 1、Microsoft365_Extractor：该脚本基于Office 365 Extractor实现其功能，可以提供所有功能并允许自定义开发。
>
>
> 2、Microsoft365_Extractor_light：Microsoft365_Extractor的轻量级版本，只需最少的配置即可在操作期间获取所有可用的日志记录。

## 功能介绍

该脚本有四个选项，可以帮助广大研究人员从Microsoft 365环境中提取日志数据：

> 1、显示可用的日志源和日志记录数量；
>
> 2、提取所有的审计日志信息；
>
> 3、提取组审计日志信息；
>
> 4、提取指定的审计日志信息（高级模式）；

## 工具要求

> PowerShell
>
> Microsoft 365账号（拥有审计日志的访问/提取权）
>
> 支持PowerShell脚本执行的操作系统，建议选择Windows；

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/invictus-ir/Microsoft-365-Extractor-Suite.git

## 工具使用

### Microsoft365_Extractor使用

> 1、下载项目中的Microsoft365_Extractor.ps1脚本；
>
> 2、打开PowerShell窗口，切换到脚本所在路径，运行该脚本，或者直接在资源管理器中右键点击脚本文件，并选择“使用PowerShell运行”；
>
> 3、选择我们所需要的选项；
>
> 4、审计日志将写入到“Log_Directory”目录中；

### Microsoft365_Extractor_light使用

> 1、下载项目中的Microsoft365_Extractor_light.ps1脚本；
>
> 2、打开PowerShell窗口，切换到脚本所在路径，运行该脚本，或者直接在资源管理器中右键点击脚本文件，并选择“使用PowerShell运行”；
>
> 3、选择开始日期、结束日期或时间间隔，也可以直接使用默认配置选项，脚本将根据用户选项来提取日志信息；
>
> 4、审计日志将写入到“Log_Directory”目录中；

### 输出结果

> Amount_Of_Audit_Logs.csv：查看可用的日志以及RecordType；
>
> AuditLog.txt：AuditLog存储了所有有价值的调试信息；
>
> AuditRecords.csv：存储了所有提取出来的日志信息；
>
> [RecordType]__AuditRecords：在提取指定的RecordType时，会将所有信息写入到这个CSV文件中；

## 可用的RecordType记录类型

    
    
    ExchangeAdmin
    
    ExchangeItem
    
    ExchangeItemGroup
    
    SharePoint
    
    SyntheticProbe
    
    SharePointFileOperation
    
    OneDrive
    
    AzureActiveDirectory
    
    AzureActiveDirectoryAccountLogon
    
    DataCenterSecurityCmdlet
    
    ComplianceDLPSharePoint
    
    Sway
    
    ComplianceDLPExchange
    
    SharePointSharingOperation
    
    AzureActiveDirectoryStsLogon
    
    SkypeForBusinessPSTNUsage
    
    SkypeForBusinessUsersBlocked
    
    SecurityComplianceCenterEOPCmdlet
    
    ExchangeAggregatedOperation
    
    PowerBIAudit
    
    CRM
    
    Yammer
    
    SkypeForBusinessCmdlets
    
    Discovery
    
    MicrosoftTeams
    
    ThreatIntelligence
    
    MailSubmission
    
    MicrosoftFlow
    
    AeD
    
    MicrosoftStream
    
    ComplianceDLPSharePointClassification
    
    ThreatFinder
    
    Project
    
    SharePointListOperation
    
    SharePointCommentOperation
    
    DataGovernance
    
    Kaizala
    
    SecurityComplianceAlerts
    
    ThreatIntelligenceUrl
    
    SecurityComplianceInsights
    
    MIPLabel
    
    WorkplaceAnalytics
    
    PowerAppsApp
    
    PowerAppsPlan
    
    ThreatIntelligenceAtpContent
    
    TeamsHealthcare
    
    ExchangeItemAggregated
    
    HygieneEvent
    
    DataInsightsRestApiAudit
    
    InformationBarrierPolicyApplication
    
    SharePointListItemOperation
    
    SharePointContentTypeOperation
    
    SharePointFieldOperation
    
    MicrosoftTeamsAdmin
    
    HRSignal
    
    MicrosoftTeamsDevice
    
    MicrosoftTeamsAnalytics
    
    InformationWorkerProtection
    
    Campaign
    
    DLPEndpoint
    
    AirInvestigation
    
    Quarantine
    
    MicrosoftForms
    
    LabelContentExplorer
    
    ApplicationAudit
    
    ComplianceSupervisionExchange
    
    CustomerKeyServiceEncryption
    
    OfficeNative
    
    MipAutoLabelSharePointItem
    
    MipAutoLabelSharePointPolicyLocation
    
    MicrosoftTeamsShifts
    
    MipAutoLabelExchangeItem
    
    CortanaBriefing
    
    Search
    
    WDATPAlerts
    
    MDATPAudit
    
    SensitivityLabelPolicyMatch
    
    SensitivityLabelAction
    
    SensitivityLabeledFileAction
    
    AttackSim
    
    AirManualInvestigation
    
    SecurityComplianceRBAC
    
    UserTraining
    
    AirAdminActionInvestigation
    
    MSTIC
    
    PhysicalBadgingSignal
    
    AipDiscover
    
    AipSensitivityLabelAction
    
    AipProtectionAction
    
    AipFileDeleted
    
    AipHeartBeat
    
    MCASAlerts
    
    OnPremisesFileShareScannerDlp
    
    OnPremisesSharePointScannerDlp
    
    ExchangeSearch
    
    SharePointSearch
    
    PrivacyInsights
    
    MyAnalyticsSettings
    
    SecurityComplianceUserChange
    
    ComplianceDLPExchangeClassification
    
    MipExactDataMatch
    
    MS365DCustomDetection
    
    CoreReportingSettings
    
    ComplianceConnector

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/invictus-ir/Microsoft-365-Extractor-Suite/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Microsoft 365 Extractor Suite** ：【[
_GitHub传送门_](https://github.com/invictus-ir/Microsoft-365-Extractor-Suite)】

## 参考资料

> [ _https://invictus-ir.medium.com/introduction-of-the-> microsoft-365-extractor-suite-b85e148d4bfe_](https://invictus-> ir.medium.com/introduction-of-the-microsoft-365-extractor-> suite-b85e148d4bfe)
>
> [ _https://docs.microsoft.com/en-us/office365/securitycompliance/search-the-> audit-log-in-security-and-compliance_](https://docs.microsoft.com/en-> us/office365/securitycompliance/search-the-audit-log-in-security-and-> compliance)
>
> [ _https://docs.microsoft.com/en-us/office/office-365-management-> api/office-365-management-activity-api-> schema#auditlogrecordtype_](https://docs.microsoft.com/en-> us/office/office-365-management-api/office-365-management-activity-api-> schema#auditlogrecordtype)
>
> [ _https://gallery.technet.microsoft.com/scriptcenter/Export-Mail-logs-to-> CSV-d5b6c2d6_](https://gallery.technet.microsoft.com/scriptcenter/Export-> Mail-logs-to-CSV-d5b6c2d6)

