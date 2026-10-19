![](https://image.3001.net/images/20220104/1641292296_61d42208f2667452fc325.png!small)  

## 关于AzureHunter

AzureHunter是一款功能强大的云端信息安全取证PowerShell模块，可以帮助广大研究人员对来自Azure和O365的数据进行安全威胁搜索与分析。

## 工具使用前提

### 1、确保拥有正确的O365权限

我们需要下列Exchange Online角色，以确保针对UnifiedAuditLog仅有只读访问权：View-Only Audit Logs或Audit
Logs。

Exchange Admin Center默认会给Compliance Management角色组分配上述权限。

### 2、确保已安装了ExchangeOnlineManagement v2 PowerShell模块

请确保你已安装了ExchangeOnlineManagement (EXOv2)。

### 3、将项目源码克隆至本地或通过PSGallery安装AzureHunter

 **（1）使用下列命令将项目源码克隆至本地：**

    
    
    git clone https://github.com/darkquasar/AzureHunter.git

然后导入模块：

    
    
    Import-Module .\source\AzureHunter.psd1

 **（2）通过PSGallery安装AzureHunter**

    
    
    Install-Module AzureHunter -Scope CurrentUser
    
    Import-Module AzureHunter

## 工具架构

![](https://image.3001.net/images/20220104/1641292327_61d4222792de99a4b5532.png!small)

## 工具使用

### 确保你已连接至ExchangeOnline

在运行任何AzureHunter命令之前，请确保运行了Connect-ExchangeOnline，

### 运行AzureHunter

AzureHunter提供了两个主要命令，即Search-AzureCloudUnifiedLog和Invoke-AzHunterPlaybook。

Search-AzureCloudUnifiedLog命令负责实现复杂的数据逻辑以确保从Azure挖掘最高百分比的UnifiedAuditLog记录。默认情况下，它会将提取和消除重复的记录并导出到CSV文件中。

Invoke-AzHunterPlaybook命令负责提供一个针对playbooks目录中存储数据的灵活接口。这些playbook在设计时，就允许任何人提交自己的分析结果和总结。

在运行Search-AzureCloudUnifiedLog命令时，可以提供一个playbook列表，Search-AzureCloudUnifiedLog命令将会通过Invoke-AzHunterPlaybook来调用相关数据。

## 工具使用样例

### 样例一：针对Azure UnifiedAuditLog运行搜索并提取记录至CSV文件

Search-AzureCloudUnifiedLog -StartDate "2020-03-06T10:00:00" -EndDate
"2020-06-09T12:40:00" -TimeInterval 12 -AggregatedResultsFlushSize 5000
-Verbose

### 样例二：针对CSV文件运行playbook威胁搜索

我们假设你已经将UnifiedAuditLog记录导出至了一个CSV文件，那我们接下来就可以运行下列命令：

    
    
    $RecordArray = Import-Csv .\my-exported-records.csv
    
    Invoke-AzHunterPlaybook -Records $RecordArray -Playbooks 'AzHunter.Playbook.UAL.LogonAnalyser'

你还可以通过下列命令运行多个playbook：

    
    
    $RecordArray = Import-Csv .\my-exported-records.csv
    
    Invoke-AzHunterPlaybook -Records $RecordArray -Playbooks 'AzHunter.Playbook.UAL.Exporter', 'AzHunter.Playbook.UAL.LogonAnalyser'

### 样例三：运行playbook威胁搜索并生成eDiscovery概述报告

假设我们已经导出了一份eDiscovery报告至CSV文件，接下来我们就可以运行下列命令：

    
    
    $eDiscoReportFile = .\eDisco-Summary-Report-PersonOfInterest.csv
    
    Invoke-AzHunterPlaybook -Records $eDiscoReportFile -Playbooks 'AzHunter.Playbook.eDisco.SummaryReportCleaner'

或者，我们也可以传递某些参数选项：

    
    
    $eDiscoReportFile = .\eDisco-Summary-Report-PersonOfInterest.csv
    
    Invoke-AzHunterPlaybook -Records $eDiscoReportFile -Playbooks 'AzHunter.Playbook.eDisco.SummaryReportCleaner' -PlayBookParameters @{"CsvRecordsBatchSize" = 700}

其中的“CsvRecordsBatchSize”参数将控制playbook向磁盘写入数据。

## 工具运行演示

![](https://image.3001.net/images/20220104/1641292390_61d42266826e0d47680be.gif!small)

## 项目地址

 **AzureHunter：** 【[ _GitHub传送门_](https://github.com/darkquasar/AzureHunter)】

## 参考资料

> [ _https://docs.microsoft.com/en-us/microsoft-365/compliance/search-the-> audit-log-in-security-and-compliance?view=o365-worldwide#search-the-audit-> log_](https://docs.microsoft.com/en-us/microsoft-365/compliance/search-the-> audit-log-in-security-and-compliance?view=o365-worldwide#search-the-audit-> log)
>
> [ _https://docs.microsoft.com/en-us/office365/securitycompliance/search-the-> audit-log-in-security-and-compliance_](https://docs.microsoft.com/en-> us/office365/securitycompliance/search-the-audit-log-in-security-and-> compliance)
>
> [ _https://gcits.com/knowledge-base/enabling-unified-audit-log-delegated-> office-365-tenants-via-powershell/_](https://gcits.com/knowledge-> base/enabling-unified-audit-log-delegated-office-365-tenants-via-> powershell/)
>
> [ _https://docs.quasarops.com/en/public/the-soc-analyst-> scrolls/powershell#useful-powershell-> modules_](https://docs.quasarops.com/en/public/the-soc-analyst-> scrolls/powershell#useful-powershell-modules)
>
> [ _https://docs.microsoft.com/en-us/office/office-365-management-> api/office-365-management-activity-api-> schema#auditlogrecordtype_](https://docs.microsoft.com/en-> us/office/office-365-management-api/office-365-management-activity-api-> schema#auditlogrecordtype)
>
> [ _http://azurehunter.readthedocs.io/_](http://azurehunter.readthedocs.io/)
>
> [
> _https://github.com/darkquasar/AzureHunter_](https://github.com/darkquasar/AzureHunter)
>
> [ _https://threathunterz.com/_](https://threathunterz.com/)

