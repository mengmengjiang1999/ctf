# CVE-2019-1257：通过BDC反序列化在Microsoft SharePoint上执行代码

阅读量 **600336**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-09-26 16:30:33

 **x**

##### 译文声明

本文是翻译文章

原文地址：<https://www.zerodayinitiative.com/blog/2019/9/18/cve-2019-1257-code-execution-on-microsoft-sharepoint-through-bdc-deserialization>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t014edf771fb35ca2ba.jpg)

今年早些时候，研究人员Markus Wulftange（[@mwulftange](https://github.com/mwulftange
"@mwulftange")）报告了Microsoft SharePoint中的一个远程代码执行（RCE）漏洞，最终被修补为CVE-2019-0604
。话音未落，9月Microsoft又处理了Markus报告的其他三个SharePoint
RCE：CVE-2019-1295，CVE-2019-1296和CVE-2019-1257。这篇博客将更详细地介绍了最后一个CVE，也被称为ZDI-19-812。此错误会影响所有受支持的SharePoint版本，获得了微软最高的漏洞攻击指数评级—高危，他们预计在不久的将来会看到关于它的攻击。

## 漏洞详情

由于自定义的BDC模型中可以使用任意方法参数类型，Microsoft SharePoint
2016中的业务数据连接（BDC）服务容易受到XmlSerializer流的任意反序列化的攻击。如AlvaroMuñoz和Oleksandr
Mirosh在Black Hat 2017黑帽大会报告中所言，对XmlSerializer流进行任意反序列化可以导致任意代码执行。

SharePoint支持使用业务数据连接模型文件格式（MS-BDCMFFS）[1]来指定自定义BDC模型。该规范的一部分是方法和参数的定义。这是Microsoft提供的示例摘录：

![](https://p1.ssl.qhimg.com/t01a8e2bc78139479c0.png)

这将定义一个名为GetCustomer的方法，该方法包装一个名为sp_GetCustomer的存储过程（详情请参阅rdbcommandtext属性）。输入参数（Direction=”In”）和返回参数（Direction=”Return”）都用它们各自的类型描述来定义的。

在上面显示的示例中，输入参数的原始类型为System.Int32，这是安全的。但是如果定义的BDC模型的参数类型为Microsoft.BusinessData.Runtime.DynamicType，则会出现此问题。这样做好处在于允许调用者灵活地为该参数传递许多不同类型的值。后果就是反序列化调用方提供了任意XmlSerializer流。

## 漏洞利用

我们在已安装了KB4464594的Microsoft SharePoint Server 2016上测试此漏洞。它在Windows Server
2016更新14393.3025的64位版本上运行。

为了演示利用过程，需要执行以下步骤：

1：管理员必须自行定义一个BDC模型，其中包括一个参数类型为Microsoft.BusinessData.Runtime.DynamicType的方法。对于自定义的BDC模型，将数据库模型示例用作模板并进行了大幅简化：

![](https://p3.ssl.qhimg.com/t01e0126a4bb9b1b692.png)

2：然后，管理员必须通过SharePoint管理中心|应用管理|管理服务应用程序|业务数据连接服务去上传BDC模型。当然，这也可以通过PowerShell完成：

![](https://p0.ssl.qhimg.com/t013fb6e0d899a82cc9.png)

3：然后，攻击者可以调用该方法，在参数中传递有效的payload。

![](https://p5.ssl.qhimg.com/t01526eaf16b1f77bed.png)

在SharePoint服务器上，您会发现已经生成两个cmd.exe实例和一个win32calc.exe实例，它们将作为SharePoint应用程序池的标识运行。

若要查看代码的路径，可以将调试器附加到SharePoint应用程序的w3wp.exe。在system.web.dll上设置断点！

System.Web.dll!System.Web.UI.ObjectStateFormatter.Deserialize显示以下调用堆栈：

![](https://p1.ssl.qhimg.com/t015dcd6e57a0966057.png)

## 结论

成功利用此漏洞并不会使您成为服务器管理员，但攻击者可借助特制的SharePoint应用程序包利用该漏洞在SharePoint应用程序池和SharePoint服务器场帐户的上下文中运行任意代码。根据Microsoft的说法，他们通过更正SharePoint使其去检查应用程序包的源标记的方式，在9月补丁中解决了此漏洞。再次感谢Markus的提交，我们希望将来能收到他的更多报告。

九月发布还包括修补Azure DevOps（ADO）和Team Foundation
Server（TFS）中的漏洞的补丁，该漏洞允许攻击者在TFS或ADO服务帐户的上下文中在服务器上执行代码。我们将在不久的将来提供该bug的其他详细信息。在此之前，请跟随团队了解最新的利用漏洞技术和安全修补程序。

[1]<https://docs.microsoft.com/en-us/openspecs/sharepoint_protocols/ms-bdcmffs/0c568f71-36de-4a89-b44f-cab48609b86a>

本文翻译自
[原文链接](https://www.zerodayinitiative.com/blog/2019/9/18/cve-2019-1257-code-execution-on-microsoft-sharepoint-through-bdc-deserialization)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **寅儿** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/187377](/post/id/187377)

安全客 - 有思想的安全新媒体

本文转载自: [](https://www.zerodayinitiative.com/blog/2019/9/18/cve-2019-1257-code-execution-on-microsoft-sharepoint-through-bdc-deserialization)

如若转载,请注明出处：
<https://www.zerodayinitiative.com/blog/2019/9/18/cve-2019-1257-code-execution-on-microsoft-sharepoint-through-bdc-deserialization>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞利用](/tag/漏洞利用)
  * [SharePoint](/tag/SharePoint)

 **+1** __10赞

 __收藏

![](https://p2.ssl.qhimg.com/t010857340ce46bb672.jpg) 寅儿

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

