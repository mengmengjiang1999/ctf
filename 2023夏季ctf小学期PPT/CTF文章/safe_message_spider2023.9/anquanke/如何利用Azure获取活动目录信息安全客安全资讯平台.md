# 如何利用Azure获取活动目录信息

阅读量 **184516**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-09-06 14:30:03

 **x**

##### 译文声明

本文是翻译文章，文章来源：blackhillsinfosec.com

原文地址：<https://www.blackhillsinfosec.com/red-teaming-microsoft-part-1-active-directory-leaks-via-azure/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0135cddb06f0b49a73.jpg)

## 一、前言

Microsoft现在无处不在，包括各种技术、服务、集成环境、应用以及配置等，在这种情况下，想做好管理并不是一件容易的事。现在想象一下，我们如果要管理远超自己能力范围的一个环境是多么困难的一件事。当我们把一切都迁移到云端时，可以在可扩展性、功能性甚至成本方面来带极大的好处，一定程度上也能达到隐蔽自身的目的。在过去一年中，我一直在研究如何攻击依托Microsoft作为云服务商的那些单位。我希望开发出各种技术，能够挖掘这些隐蔽节点，就像之前我与Beau
Bullock（@dafthack）对[Google](https://www.youtube.com/watch?v=ddoGGxt0vVk)所做的研究一样。

实话实说，我并没有对微软了如指掌。相反，当我对这方面产品及服务了解更多后，我也越来越感受到自己的不足。虽然在过去一年中，我已经可以熟练掌握和改进相关技术，从红队的角度更好地攻击目标，但我仍然努力尝试去理解各种不同的概念。比如默认的配置是什么、配置的同步机制如何、如果在云端做了些修改，这些修改是否最终会影响目标内部网络等等。当我私下分享这些技术时，总会不可避免地出现另一个问题。虽然我也认为在没有解决方案的情况下抛出问题某种程度上有点不负责任，但有时候解决方案并非非黑即白。我的建议是我们需要全面了解自己所使用的环境以及技术，如有需要可以直接联系服务提供商彻底澄清这些信息。

## 二、应用场景

举个应用场景，多年来我们一直本地环境中部署了微软Active Directory（活动目录）以及Exchange服务，但想为雇员快速部署Microsoft
Office服务，同时为雇员提供webmail入口、Sharepoint以及某些内部应用的SSO（单点登录）接口。此时我们决定迁移至Office
365，一切都非常顺利，所有的用户都可以使用自己的网络凭据进行认证，邮箱也正常工作。这种情况下，你是否认为自己仍处于本地环境中，亦或处于并不安全的云环境中？也许迁移过程中我们混合使用了的各种方法，同时处于这两种状态下。Microsoft的确提供了他们支持的大量集成技术，但我们如何知道自己是否可以正确管理所有对象？

## 三、复杂环境

如果想在本地管理用户，可以使用传统的Microsoft AD方案；想在云服务管理用户，可以使用Azure
AD方案；在邮件方面，本地端可以使用Exchange服务，但也可以将邮件迁移至Exchange Online；如果想使用全套Microsoft
Office产品，可以选择Office 365，但我觉得这些方案最终都用到了Exchange
Online，因此从技术方面来看，用户可以同时使用这些方案，但只支付一种产品的费用。购买了Office 365
Business后，用户还可以享受其他各种服务，比如Skype以及OneDrive（虽然公司文件共享使用的是GDrive或者Box）。用户引入了多因素认证解决方案，选择SMS令牌作为默认的验证机制，但由于某些原因，用户仍然可以绕过MFA（多因素认证）来使用Outlook（这主要归功于Microsoft
EWS）。总体而言，一切都工作正常，感谢微软提供的集成服务，比如Azure AD Connect，或者是Azure AD Synchronization
Services，亦或是有些年头的DirSync搭配Forefront Identity
Manager解决方案……不论如何，整个环境仍在正常运转，这样就足够了。

![](https://p4.ssl.qhimg.com/t01a1a5a6b54772d64c.jpg)

**那么问题到底出在哪里？**

刚才描述的那种复杂场景中存在各种问题，很少有蓝队可以准确防御或者响应各种不同的攻击场景：比如远程转储活动目录、绕过甚至劫持用户的多因素认证机制等。

在侦察阶段，想澄清目标单位内的人员信息情况通常借助的是LinkedIn或者其他OSINT技术等第三方服务。如果我们处在内部网络，那么获取这些信息至关重要，因为我们需要深入了解该单位的细节信息，比如目标配置了多少个组、这些组具体包含哪些成员等。如果能访问相关主机、根据用户的访问行为来确认目标对象，那么这个任务可以轻松完成。然而如果我们还没进入内部网络，尚需澄清哪些是目标对象呢？更进一步，如果目标对象托管在云端，我们完全没有接触到内部网络，此时应该怎么办？

对于Microsoft，如果我们使用了任何云服务（Office 365、Exchange Online等）以及Active
Directory（本地或者Azure环境），那么感谢Azure AD的大力支持，攻击者只需一个凭据就能获取整个Active
Directory结构信息。具体步骤如下：

1、通过webmail接口（如`https://webmail.domain.com/`）的认证；

2、将浏览器URL地址更改为：`https://azure.microsoft.com`；

3、从当前活跃的会话中选择一个账户；

4、选择Azure Active Directory，享受胜利果实。

![](https://p4.ssl.qhimg.com/t01de77758c61ac2b5e.png)

这样会造成很多不好的后果。比如如果我们能导出所有的用户以及组信息，我们就有可能澄清员工以及所属组情况。我们同样可以知道哪些组可以登录VPN、域管是谁、谁有数据库访问权限、哪些是云服务器、财务数据在哪等等。Azure
AD还有另一个好处，它会保存每个用户的设备信息，所以我们可以看到用户使用的是Mac、Windows主机还是iPhone，也能看到具体的版本号（比如Windows
10.0.16299.0）。如果这些信息还不够，我们还能了解用户终端所搭载的商务应用、SPN（service principal
name）信息、其他域名，甚至还包括用户可能具备访问权限的虚拟资源（比如虚拟机、网络、数据库等）。

![](https://p2.ssl.qhimg.com/t01be176af8d1433338.png)

**还有更多！**

以普通用户登陆Azure入口还有另一个好处，那就是我们可以创建后门……额，其实我说的是“Guest”（访客）账户，非常方便，具体步骤如下：

1、点击“Azure Active Directory”；

2、点击Manage下的“Users”选项；

3、点击“New Guest User”，然后邀请自己即可。

![](https://p0.ssl.qhimg.com/t018d66a1aa966ca8eb.png)

根据具体配置，这种操作有可能会同步回目标内部网络中。事实上虽然默认情况下可以创建访客账户，但我只碰到过有个客户符合这种情况，当时他们的Azure AD
Connect双向同步，访客账户可以进行身份认证、在内部注册多因素设备以及VPN权限。我们需要注意这个配置组件，因为它可能会带来不好的影响。

![](https://p1.ssl.qhimg.com/t01a89f09a210bcdee0.jpg)

## 四、对红队的意义

###  可用工具

通过Web浏览器访问Azure门户入口的确非常有用，具有很多优点，但我还需要找到另一个方法来直接导出信息。之前我写过一个工具，可以自动化进行身份认证，但操作起来比较麻烦。微软本身集成了许多强大的技术，可以帮我解决这个问题。我找到了许多解决方案，比如：

**Azure CLI（AZ CLI）**

作为一名Linux用户，我更偏向于使用[AZ CLI](https://docs.microsoft.com/en-us/cli/azure/ad/user?view=azure-cli-latest)，一方面是因为我习惯在一行命令中尽可能多的输入数据，另一方面也是因为我经常使用.NET工具。使用AZ
CLI我们可以快速且方便地使用OAUTH方式与Azure进行身份认证，也能快速导出原始数据。在本文中我们将重点关注这种解决方案。

**Azure Powershell**

随着[Powershell
Empire](https://github.com/EmpireProject/Empire)以及[MailSniper](https://github.com/dafthack/MailSniper)等Powershell工具的兴起，我惊讶的是[Azure
Powershell](https://docs.microsoft.com/en-us/powershell/module/azurerm.resources/?view=azurermps-6.8.1#active_directory)竟然还没有融入这些工具体系中。我们可以与大量的Active
Directory Cmdlet交互，大家可以先安装[Azure RM Powershell](https://docs.microsoft.com/en-us/powershell/azure/install-azurerm-ps?view=azurermps-6.8.1)，然后运行`Connect-AzureRmAccount`亲自测试一下。

**Azure .NET**

有些特立独行的人使用的是Linux系统，却会使用C#来开发工具，我就是其中的一份子。因此，能使用[Azure
.NET](https://docs.microsoft.com/en-us/dotnet/azure/?view=azure-dotnet)库来与Active Directory交互对我来说是非常有用的一件事。我并没有深入分析这些库，但整体看来它们似乎是Active
Directory Graph API的某种封装实现。

###  深入分析

前面我提到过，本文重点关注使用AZ
CLI来与Azure交互。首先我们需要与Azure建立活动会话。当面对的是使用Microsoft或者Google服务的目标时，我很少尝试直接去获取内部网络的shell权限。通常情况下我会使用[CredSniper](https://github.com/ustayready/CredSniper)这款工具，通过钓鱼方式获取凭据以及多因素令牌，然后以目标用户身份通过认证，追踪敏感邮件、文件、访问权限、各种信息以及VPN接口。

在本文中，我们假设攻击者已经通过某种方式事先获取了有效的用户凭据。

**1、安装AZ CLI**

首先我们需要将Microsoft源加入apt源中（假设我们使用的是Linux环境），安装Microsoft签名密钥，然后安装Azure CLI：

    
    
    AZ_REPO=$(lsb_release -cs) echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | sudo tee /etc/apt/sources.list.d/azure-cli.list
    
    curl -L https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -    
    sudo apt-get install apt-transport-https
    
    sudo apt-get update && sudo apt-get install azure-cli
    

**2、通过Web会话进行身份认证**

一切安装完毕后，我们需要使用已有的凭据获得Azure会话。最简单的一种方法就是在普通浏览器中使用ADFS或者OWA进行认证，然后输入如下命令：

    
    
    az login
    

该命令会在本地生成OAUTH令牌（token），打开浏览器标签页访问认证页面，然后我们可以在页面中选择已经通过身份认证的那个账户。选择账户后，服务器就会验证本地OAUTH令牌，直到令牌过期或者被销毁我们才需要重复该过程。我们也可以使用`-use
-device-code`标志运行该命令，自动生成提供给`https://microsoft.com/devicelogin`的令牌。

![](https://p5.ssl.qhimg.com/t013a0b3c6439dd2e65.png)

###  导出用户信息

接下来是我最喜欢的部分。之前已经有研究人员提供了各种方法来提取GAL信息，比如使用OWA中的`FindPeople`以及`GetPeopleFilter`
web
service方法。这些技术对红队来说都是非常好的资源，但有各自的限制，比如所能提取的数据范围、枚举用户所需的时间、所产生的web请求数量以及不适用的场景等。使用AZ
CLI后，我们很容易就能提取出每个用户的目录信息。如下所示，我使用了[JMESPath](http://jmespath.org/)过滤器来提取我感兴趣的数据，可以将数据导出为表格、JSON或者TSV格式。

**1、导出所有用户**

    
    
    az ad user list --output=table --query='[].{Created:createdDateTime,UPN:userPrincipalName,Name:displayName,Title:jobTitle,Department:department,Email:mail,UserId:mailNickname,Phone:telephoneNumber,Mobile:mobile,Enabled:accountEnabled}'
    

![](https://p5.ssl.qhimg.com/t01431cc3269b88c1cb.png)

**2、导出特定用户**

如果我们知道目标用户的UPN信息，我们可以使用`-upn`标志来提取特定用户的信息。如果我们想深入分析特定账户的活动目录信息，这一点对我们来说非常方便。具体命令如下所示，其中我将输出结果以JSON格式导出：

    
    
    az ad user list --output=json --query='[].{Created:createdDateTime,UPN:userPrincipalName,Name:displayName,Title:jobTitle,Department:department,Email:mail,UserId:mailNickname,Phone:telephoneNumber,Mobile:mobile,Enabled:accountEnabled}' --upn='<upn>'
    

![](https://p3.ssl.qhimg.com/t013155368e11dc87c8.png)

###  导出组信息

导出组是我喜欢的另一个功能。了解目标单位所使用的组可以为我们提供各种情报，比如目标的业务范围、用户情况以及管理员情况。这里AZ
CLI也为我们提供了一些有用的命令。

**1、导出所有组**

我做的第一件事就是导出所有组，然后就可以搜索关键词，比如：`Admin`、`VPN`、`Finance`、`Amazon`、`Azure`、`Oracle`、`VDI`以及`Developer`等。虽然我们可以提取很多元数据，但我通常只关心组名以及组描述：

    
    
    az ad group list --output=json --query='[].{Group:displayName,Description:description}'
    

![](https://p2.ssl.qhimg.com/t0175ef5c15e3ae5fe3.png)

**2、导出特定组成员**

浏览所有组并选定感兴趣的目标后，接下来我们可以导出特定的组成员，获取组中具体包含哪些对象，这些都是渔叉式钓鱼攻击的首选目标！与大家的观点不同，我认为目标单位的技术能力并不能避免目标泄露凭据信息（甚至是MFA令牌信息）。换句话说，每个人都可能受到攻击，所以我通常有针对性地攻击后端工程师以及研发团队，因为这些人员通常具备最多的访问权限，并且虽然我尚未进入目标内部网络，也能访问私人的GitHub/GitLab代码仓库来搜索凭据、访问Jenkins服务器来获取shell接口、访问OneDrive/GDrive文件共享盘来获取敏感信息、访问Slack来获取敏感文件以及其他第三方服务。总之，我们不一定要进入内部网络才能获取敏感信息。

    
    
    az ad group member list --output=json --query='[].{Created:createdDateTime,UPN:userPrincipalName,Name:displayName,Title:jobTitle,Department:department,Email:mail,UserId:mailNickname,Phone:telephoneNumber,Mobile:mobile,Enabled:accountEnabled}' --group='<group name>'
    

###  导出应用及Service Principal信息

Microsoft提供的另一个功能就是注册使用SSO/ADFS或者与其他技术集成的应用。许多公司会在内部应用上使用该功能，这一点对红队来说也非常好，因为应用关联的元数据可以提供许多有价值信息，比如URL等，这些信息在侦察阶段可能会被忽视掉。

**1、导出所有应用信息**

    
    
    az ad app list --output=table --query='[].{Name:displayName,URL:homepage}'
    

**2、导出特定应用信息**

如下所示，我们可以检查Azure中已注册应用所关联的元数据，发现Splunk实例的URL地址。

    
    
    az ad app list --output=json --identifier-uri='<uri>'
    

![](https://p5.ssl.qhimg.com/t0192c7838121704394.png)

**3、导出所有Service Principal信息**

    
    
    az ad sp list --output=table --query='[].{Name:displayName,Enabled:accountEnabled,URL:homepage,Publisher:publisherName,MetadataURL:samlMetadataUrl}'
    

**4、导出特定Service Principal信息**

    
    
    az ad sp list --output=table --display-name='<display name>'
    

###  使用JMESPath过滤器

在前面的例子中，我限制了输出结果的大小，这主要是因为我只想关注重要的信息。AZ
CLI可以过滤输出结果，使用`-query`标志以及`JMESPath`查询即可。我发现当`query`标志与`show`这个内置函数搭配使用时会存在一些bug。另外还需要注意默认的输出格式为JSON格式，这意味着如果我们想使用查询过滤器，我们需要使用大小写完全匹配的命名约定。不同格式的输出名称有些不同，比如JSON中可能使用的是小写字符，而table格式可能使用的是大写字符。

## 五、如何禁止访问Azure Portal

我专门花了点时间研究哪些对象需要禁用、如何禁止访问、如何限制访问权限、如何监控，也通过Twitter与许多研究人员积极交流，感谢所有帮助过我的人（特别感谢[Josh
Rickard](https://twitter.com/MS_dministrator)的大力支持）。我想我应该继续学习Microsoft的生态系统，才能提出更好的建议。在此之前，我可以先给出如何禁用Azure
Portal的方法，我还没有测试过这种方法，不确定该操作是否可以覆盖AZ CLI、Azure RM Powershell以及Microsoft Graph
API，但至少我们可以迈出第一步。

具体步骤如下：

1、使用`Global
Administrator`账户登录Azure（[https://portal.azure.com](https://portal.azure.com/)）；

2、在左侧面板，选择`Azure Active Directory`；

3、选择`Users Settings`；

4、选择`Restrict access to Azure AD administration portal`（限制访问Azure AD管理员门户）。

另一种方法是[Conditional Access Policies（条件访问策略）](https://docs.microsoft.com/en-us/azure/active-directory/conditional-access/overview)，大家可以尝试一下。

## 六、总结

现在已经有各种工具可以测试AWS环境，最近有些新工具甚至可以捕捉云凭据（如[SharpCloud](https://github.com/chrismaddalena/SharpCloud)）。云环境似乎是人们经常忽略的一个攻击面。

我即将发布[CloudBurst](https://github.com/ustayready/CloudBurst)（目前处于私有状态），这是一个红队框架，可以与云环境交互。该框架采用可插拔模式，用户可以与不同的云服务商交互，捕捉、破坏以及窃取敏感数据。

本文翻译自blackhillsinfosec.com [原文链接](https://www.blackhillsinfosec.com/red-teaming-microsoft-part-1-active-directory-leaks-via-azure/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/158926](/post/id/158926)

安全客 - 有思想的安全新媒体

本文转载自: [blackhillsinfosec.com](https://www.blackhillsinfosec.com/red-teaming-microsoft-part-1-active-directory-leaks-via-azure/)

如若转载,请注明出处： <https://www.blackhillsinfosec.com/red-teaming-microsoft-part-1-active-directory-leaks-via-azure/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [活动目录](/tag/活动目录)
  * [云安全](/tag/云安全)
  * [Azure](/tag/Azure)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

