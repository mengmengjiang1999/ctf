**SlackExtract是一个用于从用户slack帐户中提取所有文件，消息和用户配置文件的PowerShell脚本。或者，你也可以指定channels频道（最多为默认限制）来提取这些数据。**

 **从 Windows 命令行输入 powershell 并启用脚本：**

    
    
    powershell -exec bypass

 **导入模块：**

    
    
    Import-Module .\SlackExtract.ps1

 **使用说明：**

    
    
    Get-Help Invoke-SlackExtract -full

 **必需参数：**

> SlackUrl（例如
> [https://slackextract.slack.com](https://slackextract.slack.com/)）
>
> OutputFolderName（例如 my-extraction）
>
> dCookie（例如 wvxP...8%3D）或 SlackToken（例如 xoxs-12...65）

 **示例1：提取所有文件和消息**

这将从用户有权访问的各个channel中提取所有消息和文件。默认输出保存到Document/SlackExtract目录下，并会为每个channel创建一个单独的文件夹，如下所示。

**![BasicUsage.png](https://image.3001.net/images/20181104/1541289078_5bde34763dc4f.png!small)**

 **提供 dCookie**

    
    
    Invoke-SlackExtract -OutputFolderName my-extraction -SlackUrl https://slackextract.slack.com -dCookie wvxPLsXuW%2BUjT2b5RiCvb%2BUBPlJEX2XWbnVpOTlQZUN1TFF6dkxrNlZJbExYTzN6TmNtdFZNTDY0Y2pVQlF6UXlannhZMkprcHRueE12TVpXaXRvRWtQZGhidlhPdEh2d0J1a0I0UjcxMlRJV2JmTndDMlh1czNlUCt0SWIyczExb0z1ZCtxL3JJRW9tenJFRDhIdmp2MWVIQytLc3Q0RWZLSEFvdTQxUFE9PSy1X4xNmoY5wXzFlw2GJL8%3D

### 提供 API Token

    
    
    Invoke-SlackExtract -OutputFolderName my-extraction -SlackUrl https://slackextract.slack.com -SlackToken xoxs-420083410720-421837374423-440811613314-977844f625b707d5b0b268206dbc92cbc85feef3e71b08e44815a8e6e7657190

 **获取 dCookie 和 API Token**

有关获取dCookie或SlackToken的方法，请[参阅此处](https://github.com/clr2of8/SlackExtract/wiki/Authorization)。

 **默认限制（可通过可选参数更改默认值）**

限制参数 | 默认值  
---|---  
MaxMessagesPerChannel | 10,000  
MaxFilesPerChannel | 2,000  
MaxUsers | 100,000  
MaxAccessLogs* | 1000,0000  
  
*** 仅付费工作区的管理员可访问**

 **示例2：提取用户配置文件**

通过MaxUsers参数最多可以指定提取1000个用户的配置文件。每个用户的详细信息都将作为单独的json文件，写入meta/Users目录中。
此外，还会为我们创建一个all_users.csv文件，以便于我们在Excel中查看和排序数据，如下所示。

    
    
    Invoke-SlackExtract -ExtractUsers -MaxUsers 1000 -OutputFolderName my-extraction -SlackUrl https://slackextract.slack.com -SlackToken xoxs-420083410720-421837374423-440811613314-977844f625b707d5b0b268206dbc92cbc85feef3e71b08e44815a8e6e7657190

**![UserProfiles.png](https://image.3001.net/images/20181104/1541289039_5bde344fdc6ab.png!small)**

 **示例3：仅从** **私人频道（Private Channels）** **提取数据**

    
    
    Invoke-SlackExtract -PrivateOnly -OutputFolderName my-extraction -SlackUrl https://slackextract.slack.com -SlackToken xoxs-420083410720-421837374423-440811613314-977844f625b707d5b0b268206dbc92cbc85feef3e71b08e44815a8e6e7657190

 **示例4：仅从特定 Channels 提取数据**

你可以提供一个以逗号分隔的Channel IDs列表，从这些特定频道中提取数据。连接到Slack工作区时，你可以在Web浏览器的URL栏中看到channel
ID。你还可以使用ExcludeChannelIds参数来将特定频道排除在外。

    
    
    Invoke-SlackExtract -ChannelIds DD0081E5C,CCC2FCAE4,GD00AAMFY -OutputFolderName my-extraction -SlackUrl https://slackextract.slack.com -SlackToken xoxs-420083410720-421837374423-440811613314-977844f625b707d5b0b268206dbc92cbc85feef3e71b08e44815a8e6e7657190

 **示例5：提取访问日志**

访问日志包含每个用户连接到Slack工作区时的IP地址和用户代理，如下所示。要提取访问日志，用户必须为付费工作区的管理员。

    
    
    Invoke-SlackExtract -ExtractAccessLogs -MaxAccessLogs 200 -OutputFolderName my-extraction -SlackUrl https://slackextract.slack.com -SlackToken xoxs-420083410720-421837374423-440811613314-977844f625b707d5b0b268206dbc92cbc85feef3e71b08e44815a8e6e7657190

**![AccessLogs.png](https://image.3001.net/images/20181104/1541288986_5bde341a9b7e0.png!small)**

 **搜索提取的数据**

提取的数据将以UTF-16格式写入文件，因此你将无法使用grep的方式来搜索数据。但你可以使用PowerShell搜索提取的数据，有关详情请[参阅此处](https://github.com/clr2of8/SlackExtract/wiki/Analyzing-Extracted-Results)。

***参考来源：[GitHub](https://github.com/clr2of8/SlackExtract)，FB小编secist编译，转载请注明来自FreeBuf.COM**

