![](https://image.3001.net/images/20191010/1570697604_5d9ef184f18f6.png!small)

## 写在前面的话

在今年年初，研究人员Markus Wulftange（[
_@mwulftange_](https://twitter.com/mwulftange)）曾报告过Microsoft
SharePoint中的一个远程代码执行漏洞（RCE），该漏洞的CVE编号为[
_CVE-2019-0604_](https://www.zerodayinitiative.com/blog/2019/3/13/cve-2019-0604-details-of-a-microsoft-sharepoint-rce-vulnerability)。而在今年的九月初，Markus又在SharePoint中发现了另外三个新的远程代码执行漏洞，即[
_CVE-2019-1295_](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1295)，[
_CVE-2019-1296_](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1296)和[
_CVE-2019-1257_](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1257)。在这篇文章中，我们将对最后一个漏洞，也就是[
_CVE-2019-1257_](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-1257)（[
_ZDI-19-812_](https://www.zerodayinitiative.com/advisories/ZDI-19-812/)）进行详细分析。目前，所有版本的SharePoint都会受到该漏洞的影响，微软方面也将该漏洞的可利用等级评估为最高等级，这也就意味着在不久的将来，会有很多网络犯罪分子利用该漏洞实施攻击。

## 漏洞细节

这个漏洞存在于微软SharePoint中的业务数据（BDC）连接服务之中，由于自定义的BDC模型中可以使用任意的方法参数类型，从而导致Microsoft
SharePoint 2016中的业务数据连接（BDC）服务容易受到XmlSerializer流的任意反序列化的攻击。早在2017年的Black
Hat黑帽黑客大会上，研究人员Alvaro Muñoz和Oleksandr
Mirosh就曾介绍过如何通过对XmlSerializer流进行任意反序列化并实现任意代码执行【[
_参考文档_](https://www.blackhat.com/docs/us-17/thursday/us-17-Munoz-Friday-The-13th-JSON-Attacks-wp.pdf)】。

SharePoint允许使用业务数据连接模型文件格式（[ _MS-BDCMFFS_](https://docs.microsoft.com/en-us/openspecs/sharepoint_protocols/ms-bdcmffs/0c568f71-36de-4a89-b44f-cab48609b86a)）数据格式来指定自定义的BDC模型，这种规范中的部分内容为方法和参数定义。下面给出的是微软提供的[
_样本_](https://docs.microsoft.com/en-us/openspecs/sharepoint_protocols/ms-bdcmffs/6cca0070-2f26-40ad-9860-3ad0607f0bbb)：

![](https://image.3001.net/images/20191010/1570697618_5d9ef192bacbb.png!small)

上述代码定义了一个名叫GetCustomer的方法，它负责封装一个名叫sp_GetCustomer的程序，这两者的输入参数(Direction="In")和返回参数(Direction="Return")都使用了各自对应类型的描述来定义。

在上述样本中，输入参数的原始类型为System.Int32，这就没什么大问题。但如果定义的BDC模型参数类型为Microsoft.BusinessData.Runtime.DynamicType，就会出现问题了。这种方案的好处在于允许开发人员灵活地通过该参数传递不同类型的值，但坏处就是为反序列化的调用方提供了任意的XmlSerializer流。

## 漏洞利用

我们的测试设备为Microsoft SharePoint Server 2016，并且安装了KB4464594，操作系统版本为64位的Windows
Server 2016 update 14393.3025。

漏洞利用步骤及过程如下：

1、管理员首先需要自定义一个BDC模型，其中包括一个参数类型为Microsoft.BusinessData.Runtime.DynamicType的方法。针对自定义的BDC模型，程序会使用数据库模型样本来作为模板对其进行大规模简化：

![](https://image.3001.net/images/20191010/1570697637_5d9ef1a5e7724.png!small)

2、接下来，管理员需要通过SharePoint管理中心|应用管理|管理服务应用程序|业务数据连接服务来上传BDC模型。当然了，这个操作也可以通过PowerShell来完成：

![](https://image.3001.net/images/20191010/1570697641_5d9ef1a958a2e.png!small)

3、然后，攻击者就可以调用这个方法了，并通过函数参数来传递攻击Payload：

![](https://image.3001.net/images/20191010/1570697648_5d9ef1b000493.png!small)

在SharePoint服务器上，你将会发现生成了两个cmd.exe实例以及一个win32calc.exe实例，它们都会以SharePoint应用程序池的身份运行。

如果你想要查看代码路径的话，你可以把调试器绑定到SharePoint应用程序的w3wp.exe上，并在system.web.dll上设置断点。

我们可以通过System.Web.dll!System.Web.UI.ObjectStateFormatter.Deserialize来查看调用堆栈：

![](https://image.3001.net/images/20191010/1570697654_5d9ef1b6e4a4d.png!small)

## 总结

需要注意的是，即便是你能够成功利用该漏洞并实施攻击，你也无法拿到服务器端的管理员权限，不过攻击者可以利用该漏洞在SharePoint应用程序池以及SharePoint服务器账号的上下文环境中执行他们的代码。根据微软方面的描述，他们已经在9月份推送的补丁中修复了此漏洞。

## 参考资料

> 1、[ _https://docs.microsoft.com/en-us/openspecs/sharepoint_protocols/ms-> bdcmffs/0c568f71-36de-4a89-b44f-cab48609b86a_](https://docs.microsoft.com/en-> us/openspecs/sharepoint_protocols/ms-> bdcmffs/0c568f71-36de-4a89-b44f-cab48609b86a)
>
> 2、[ _https://twitter.com/thezdi_](https://twitter.com/thezdi)

 *** 参考来源：[
_zerodayinitiative_](https://www.zerodayinitiative.com/blog/2019/9/18/cve-2019-1257-code-execution-on-microsoft-sharepoint-through-bdc-deserialization)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

