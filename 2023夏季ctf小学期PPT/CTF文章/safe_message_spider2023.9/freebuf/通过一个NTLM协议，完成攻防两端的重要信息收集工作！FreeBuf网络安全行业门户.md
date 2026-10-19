![1671417123_639fcd23044f0afc342ca.png!small?1671417123557](https://image.3001.net/images/20221219/1671417123_639fcd23044f0afc342ca.png!small?1671417123557)

## **一、NTLM 协议对于攻防两端的价值**

Windows 在很多接口中只要带有认证属性，基本上都是通过 NTLM 来进行的，这种情况下都能够利用。

NTLM 是基于各个协议的，在与 Windows 认证交互的过程中，NTLM 身份验证往往给出了大量的系统信息，如操作系统，主机名，版本号等等。

  * 攻击方通过该信息可以获得踩点的信息，内网横移的时候可以快速的进行资产的梳理，通过主机名也可以对该机器的账号密码做爆破等等；
  * 防守方通过该信息可以直接拿到攻击者服务器的信息，对收集线索、溯源等有很大的帮助。

通过 NTLM 可以远程获取大量关于当前机器的系统信息，本文将通过抓包的方式对 NTLM 协议进行介绍，同时对 FOFA 中已集成的 NTML
解析进行实战演示。

##  **二、什么是NTLM？**

NTLM 是 NT LAN Manager 的缩写，是 Microsoft 环境中使用的一种身份验证协议，也是 Windows NT 早期的标准版本协议。从
Windows 2000 开始对 NTLM 进行支持，至今已经存在了 20 多年。作为全球应用最广泛的操作系统之一，在 Windows 上存在了如此之久的
NTLM 协议仍然在所有Windows系统上维护， 足以见证其强大的生命力。

该协议系列包含在 Windows Msv1_0.dll 中，微软官方对 NTLM 的详细描述为：

    
    
    NTLM authentication is a family of authentication protocols that are encompassed in the Windows Msv1_0.dll. The NTLM authentication protocols include LAN Manager version 1 and 2, and NTLM version 1 and 2.The NTLM authentication protocols authenticate users and computers based on a challenge/response mechanism that proves to a server or domain controller that a user knows the password associated with an account.

 **核心知识点：NTLM 允许用户向服务器证明自己的身份，以便用户使用该服务器提供的服务。**

虽然年龄不小，但 NTLM 仍然在所有 Windows 系统上维护。大致有几点原因：

  * 强大的兼容性，兼容旧客户端；

  * NTLM 身份验证仍受支持，并且必须用于配置为工作组成员的系统的 Windows 身份验证；

  * NTLM 身份验证用于非域控制器上的本地登录身份验证。

##  **三、知识点-如何提取NTLM信息？**

我们先从 NTLM 的通信过程入手分析。NTLM 使用质询/应答（Challenge/Response）过程进行用户身份验证。此过程包含三个步骤：
**1\. 客户端 -- > 协商消息。** **2\. 服务器 -- > 质询消息。** **3\. 客户端 -- > 身份验证消息。**

###  **第一步，客户端发送协商消息**

（案例都是以 5985WinRM
为例）客户端向服务端发送协商消息。抓包查看对应的信息如下：![1671417273_639fcdb9d55b0fc4c6af8.png!small?1671417274509](https://image.3001.net/images/20221219/1671417273_639fcdb9d55b0fc4c6af8.png!small?1671417274509)

###  **第二步，服务端质询消息**

服务器用消息进行响应，这包含服务器支持和同意的功能列表。但是，最重要的是，它包含服务器产生的 **Challenge** 这个消息中包含
Target_Name、Product_Version、OS 等等， **能够非常准确的提取出来主机名和操作系统的版本。**
抓包查看对应的信息如下：![1671417300_639fcdd4ca20186498572.png!small?1671417301342](https://image.3001.net/images/20221219/1671417300_639fcdd4ca20186498572.png!small?1671417301342)官方文档：[MS-NLMP]: CHALLENGE_MESSAGE | Microsoft
Learn到这一步我们就获取到了想要的信息，介于本篇只讲NTLM对于信息收集的帮助，就不再讲此阶段的后续流程了。接下来给大家举一个NTLM信息提取的例子。

#  **四、WinRM的NTLM提取**

###  **4.1 选择过程**

我们先根据NTLM的介绍，通过FOFA进行初步的筛选，查找microsoft或者NTLM相关的资产。FOFA搜索语法：banner="ntlm" ||
banner="microsoft"![1671417467_639fce7b0c3af5d0107c0.png!small?1671417467731](https://image.3001.net/images/20221219/1671417467_639fce7b0c3af5d0107c0.png!small?1671417467731)通过搜索结果我们可以看到资产数量多的惊人，我们需要进一步的筛选，从端口排名出进行分析。可以看到
TOP5 的端口为: 80、3389、443、135、5985。这里先排除
80(http默认端口,后面再分析)、3389(rdp早已经提取)、443(https默认端口,后面再分析)、135(dcerpc早已经提取)。那么只剩一个
5985 端口，在这看到 5985 有 54w+ 的数据，我们推测它可能是 Microsoft 某个产品的默认端口，利用搜索引擎分析后，发现其为 WinRM
的默认端口。

  

 **4.2 WinRM简介**

WinRM 是 Windows 远程管理，Microsoft 对 WinRM 的介绍如下：

  

    
    
    WinRM 2.0: The default HTTP port is 5985, and the default HTTPS port is 5986.
    Windows Remote Management is one component of the Windows Hardware Management features that manage server hardwar.
    
    核心知识点：winRM可在本地和远程管理服务器硬件。

我们根据前文介绍中 NTLM 的交互流程：1. 首先我们发送 **Authorization: Negotiate TlRMTVN. AAAADw==**
进行消息协商；2. 服务器用消息进行响应，消息大致如下：

    
    
    WWW-Authenticate:NegotiateTlRMTVNTUAACAAAAHgAeADgAAAAF  HVY/dgBAAAAAA==

  
3\. 服务器返回时用了 base64 编码，我们解码后将 Challenge
消息解析，即可获得Target_Name、Product_Version、OS 等非常丰富的信息。 **亮点：该 NTLM 的交互流程已经在 FOFA
中进行集成，直接根据该语句进行搜索即可查询公开 NTLM 协议的机器。** FOFA 搜索语句：

    
    
    (banner="ntlm" || banner="microsoft") && (port="5985" || port="5986")

在搜索结果页右侧的响应信息中，可以直接看到当前机器的操作系统、版本号、主机名等。![1671417692_639fcf5cc8d431942491d.jpg!small?1671417693280](https://image.3001.net/images/20221219/1671417692_639fcf5cc8d431942491d.jpg!small?1671417693280)

###  **4.3 演示及场景**

NTLM 系列可以基于不同协议存在，例如：imap、http、mssql 协议等，看完文章后，大家一定要通过 FOFA
来感受一下效果：![1671417720_639fcf783eede9469b348.jpg!small?1671417720762](https://image.3001.net/images/20221219/1671417720_639fcf783eede9469b348.jpg!small?1671417720762)进阶用法：通过
NTLM 协议进行资产拓线可以利用提取的 name 对资产进行关联：

  * 分布在同一个地方
  * 组织相同
  * 集中分布在相同的网段
  * 主机名/版本号完全相同

如图：

![1671417753_639fcf99aaf2279847077.jpg!small?1671417754201](https://image.3001.net/images/20221219/1671417753_639fcf99aaf2279847077.jpg!small?1671417754201)

##  **五、结语**

NTLM 为 Windows 资产提供了丰富的系统信息，我们将继续进行深度挖掘，欢迎大家基于此协议开发出更多奇思妙想的用法，更欢迎大家投稿于
FOFA，让更多人看到你的创意。现阶段 FOFA 已经上线基于 rdp、dcerpc、winrm、imap、imaps、http、smtp 等的 NTLM
信息提取。还有很多协议等着我们去做，如：telnet、pop3 等，后续我们会持续跟进，敬请持续关注！

##  **六、参考文献**

<https://learn.microsoft.com/en-us/windows-server/security/kerberos/ntlm-overview><https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/801a4681-8809-4be9-ab0d-61dcfe762786>[https://learn.microsoft.com/en-us/windows/win32/winrm/about-windows-remote-management﻿](https://learn.microsoft.com/en-us/windows/win32/winrm/about-windows-remote-management)

