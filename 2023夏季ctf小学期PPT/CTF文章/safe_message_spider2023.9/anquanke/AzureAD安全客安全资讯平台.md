# Azure AD

阅读量 **436253**

发布时间 : 2021-11-26 12:00:03

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t013ea7dade961fce89.jpg)

## 0x01什么是Azure AD

经过之前中安网星的一系列科普，相信大家对AD已经不陌生了。在Azure AD出现前，微软早在 Windows 2000 中就已引入了 Active
Directory
域服务，使组织能够使用每个用户的单一标识管理多个本地基础结构组件和系统。传统AD域服务的核心价值是提供一套完整的用户身份验证系统，是一个基础身份验证平台。而在2021年的今天，随着企业业务场景的扩张，AD逐渐不能适应高速发展的企业IT架构变化，微软也在寻求新的解决方案而推出了Azure
AD。

通常，对Azure AD最大的误解就是把它当成云中的 Active Directory，但事实并非如此，Azure
AD的覆盖范围更为广泛。简而言之，Azure AD不是在Azure云中直接搭建一套AD，而旨在将现有的Active Directory 实例扩展到云。

为了更好地理解 AD 和 Azure AD 的关系，我们可以看下图中的微软的参考架构。

![](https://p5.ssl.qhimg.com/t016f02359a67035190.png)

Azure AD 通过为组织提供一种适用于在云中和本地所有应用的标识即服务解决方案，将目录服务方案提升到了一个新层次。同时，Azure
AD是基于云的身份和访问管理解决方案，它也可以与本地AD同步，为本地和基于云的系统提供身份验证。Azure AD的应用还拓展出以下的功能：

1.Azure AD 通过多重身份验证和无密码技术显著的提高了密码安全性。

在AD中的凭据是基于密码、证书或智能卡的身份验证，通过密码策略来管理密码的长度、到期时间和复杂性，以此确保AD中密码的安全性；而在Azure
AD中对云和本地使用智能密码保护，Azure
AD通过多重身份验证和无密码技术显著的提高了密码安全性，同时也为用户提供了自助重置密码的功能来提升用户体验，降低技术支持成本。

2.Azure AD访问本地应用的方式产生变化

AD当中大多数本地应用都使用LDAP、NTLM或kerberos协议来控制用户的访问。Azure AD则可使用在本地运行的Azure
AD应用程序代理程序来访问这些类型的本地应用。

3.Azure AD完全基于云

Azure AD 的优势在于它完全基于云所提供的灵活性。这意味着它既可以充当组织的唯一目录，也可以通过 Azure AD Connect
与本地AD目录服务同步。无论采取哪种方式，它都使本地和基于云的用户能够访问相同的应用程序和资源，同时受益于诸如单点登录 (SSO)、多重身份验证
(MFA)、条件访问等功能。更重要的是，它提供了一个单一位置来管理整个 IT 资产中的身份、安全性和合规性控制。

## 0x02 如何加入Azure AD

Azure AD提供了广泛的功能以简化和集中管理，同时也集成了跨环境的应用程序，下面介绍如何将一台设备加入Azure AD。

以下步骤都建立在已注册了一个Azure AD账号的基础上。

登录Azure AD ，设备中可以看到目前还没有设备加入Azure AD。

![](https://p5.ssl.qhimg.com/t01775df2f3a0bf5d42.png)

在系统设置中，找到连接工作或学校账户，点击连接来加入Azure AD。

![](https://p1.ssl.qhimg.com/t014ae4af9a6d6d92d1.png)

在弹出的页面点击将此设备加入Azure Active Directory。

![](https://p5.ssl.qhimg.com/t0106f00bb8c1fbd940.png)

输入Azure AD的账号密码后，确认无误后点击加入。

![](https://p4.ssl.qhimg.com/t0191a56b7ebc3a3cbc.png)

加入后即可看到组织名称。

![](https://p0.ssl.qhimg.com/t01e703f3770c695e60.png)

在加入Azure AD后即可在Azure 的web页面里看到设备信息。

![](https://p3.ssl.qhimg.com/t01af2bbd07031025d8.png)

注销后用Azure AD账户登录。

![](https://p1.ssl.qhimg.com/t010c4f69ab8f30b136.png)

登陆后需要设置一些验证方式。

![](https://p5.ssl.qhimg.com/t01e3afc62da2a51cab.png)

如果需要进行二次认证的话，在进行二次认证之后，即可设置解锁这台设备的pin码。

![](https://p2.ssl.qhimg.com/t01f090c56f8e394cf0.png)

![](https://p0.ssl.qhimg.com/t013d788e90e4746293.png)

设置好后，现在就已经可以通过Azure AD的账户登入这台机器了。

![](https://p0.ssl.qhimg.com/t012b57dfa20be5c47a.png)

## 0x03 Azure AD 身份认证安全性

Azure AD
的主要功能之一，是在用户登陆设备、应用程序或服务时进行直接验证或验证凭据。如果只使用密码对用户进行身份验证，换言之，攻击者若通过爆破或抓取的方式获取到用户密码，也一样可以凭用户本人的信息登录，这也是AD域的弱点之一。  
因此为了提高安全性并减少对技术支持的需求，Azure AD身份验证包括以下组件：

自助服务密码重置  
支持在自助服务平台进行密码重置，减少管理员的工作量。  
条件访问  
通过使用条件访问策略，可以在需要时应用正确的访问控制，以确保组织安全。

![](https://p4.ssl.qhimg.com/t01bd573aedd6cb7ca5.png)

图源微软官方文档

无密码认证  
使用无密码方法登录时，凭据通过使用 Windows Hello 企业版生物识别或 FIDO2 安全密钥等方法提供。攻击者无法轻易复制这些身份验证方法。  
将密码更改写回本地AD  
密码写回可用于将 Azure AD 中的密码更改同步回本地 AD DS 环境。Azure AD Connect 提供了一种安全机制，可将这些密码更改从
Azure AD 发送回现有的本地目录。

## 0x04 总结

总体来说，Azure
AD是微软对传统AD的演进，引进了很多新的思想理念，比如无密码的概念、条件访问的概念，这也是身份验证的未来，但是纯云化的环境需要企业将核心数据托管在微软的Azure上，对于企业而言，面临着监管以及合规的挑战。

了解更多AD域协议相关，欢迎关注中安网星

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **御守实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/260031](/post/id/260031)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全研究](/tag/安全研究)
  * [AD](/tag/AD)
  * [Azure AD](/tag/Azure AD)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t015bd9ae31452d2c73.png) 御守实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

