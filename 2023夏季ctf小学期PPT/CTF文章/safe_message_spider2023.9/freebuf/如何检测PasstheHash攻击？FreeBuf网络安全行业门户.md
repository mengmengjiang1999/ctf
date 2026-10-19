**横向渗透技术是攻击者用来渗透目标网络，获取凭据和数据特权访问的最常见方法之一。在最近发现的勒索软件（如[Samsam和Ryuk](https://arstechnica.com/information-technology/2019/01/new-ransomware-rakes-in-4-million-by-adopting-a-big-game-hunting-strategy/)）中，就说明了这一点。**

最近我们研究了如何通过蜜罐检测[pass-the-hash](https://blog.stealthbits.com/detecting-pass-the-hash-honeypots/)攻击，在研究检测此类攻击的最有效方法时，我发现了其它几种有趣的方法。我认为非常有必要对它们进行测试，并进一步的研究pass-the-hash行为。

本文我将教大家如何使用本机Windows事件日志检测pass-the-hash，以及一些关于如何实现的实用建议。在这里我不会讨论有关什么是pass-the-hash的问题，如果你愿意你可以[阅读这篇文章以及观看它的演示视频](https://attack.stealthbits.com/pass-the-hash-attack-explained)。

## 基线正常事件

Pass-the-Hash依赖于NTLM身份验证。为了可靠地创建NTLM身份验证，我使用Sqlcmd实用程序通过其IP地址连接到Microsoft服务器。此命令将为SQL数据库生成NTLM身份验证：

    
    
    Sqlcmd –S [IP ADDRESS]

在查看如何检测pass-the-hash攻击之前，让我们先来获取执行NTLM登录活动时通常会生成的事件基线。要从我的PC工作站执行此操作，我将首先使用管理用户的实际密码启动一个新的命令提示符：

![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552012674_5c81d582dddab.png!small)

现在，在新的命令提示符下，我将使用Sqlcmd连接到SQL主机，并运行SELECT SYSTEM_USER命令查看我被认证为的用户：

![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552012692_5c81d594ab142.png!small)

很好，一切正常！现在让我们看看生成的日志。

## 工作站日志

在我的本地工作站上我看到以下事件。

 **4648事件：试图使用显式凭据登录（A logon was attempted usingexplicit credentials）**

 **![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552012709_5c81d5a5cd9b4.png!small)**

 **4624事件：成功登录帐户（An account was successfully logged on）**

[4624](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventID=4624)事件显示登录类型为2，这意味着交互式登录。这符合我使用runas的方式，我以交互方式输入凭据。

![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552012727_5c81d5b7e6036.png!small)

 **4672事件：分配给新的登录特权**

由于我使用的Franklin Bluth帐户是一个管理帐户，因此会记录4672显示正在分配的权限。这是跟踪管理帐户活动的非常实用的方法。

![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552012747_5c81d5cb29698.png!small)

## 目标服务器日志

在我的SQL服务器上我看到以下事件：

 **4624事件：成功登录帐户（An account was successfully logged on）**

现在，在SQL Server上你会看到4624事件，此事件的登录类型为3，即网络登录。

![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552012844_5c81d62ce3a03.png!small)

更重要的是，这表明使用的身份验证包（ Authentication Package）是NTLM。也证实了我们正在使用此方法执行NTLM身份验证。

![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552012880_5c81d6501d9b1.png!small)

我们还将看到4672事件，因为我们利用的用户帐户是一个特权帐户。

## 域控日志

在域控制器上，我将看到用户Franklin
Bluth被验证的迹象。在本例中，我将看到Kerberos和NTLM身份验证。首先发生Kerberos身份验证，这是Active
Directory的默认身份验证方式。这将生成两个事件：

 **4768事件：Kerberos 身份验证票证 (TGT) 请求**

 **![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552012905_5c81d66999667.png!small)**

以上显示了我们模拟的用户对域控制器的TGT请求。

 **4769事件：Kerberos 服务票证请求**

一旦我们有了TGT，我们就会为我们模拟用户的主机请求TGS。有了这个，我们的用户Franklin现在可以与PC交互并启动命令提示符。

![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552012929_5c81d6817e914.png!small)

 **4776事件：域控试图验证帐户凭据**

[4776](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/event.aspx?eventID=4776)事件特定于NTLM，并将在最后。
当我们使用强制NTLM身份验证的Sqlcmd执行命令时会发生这种情况。

![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552012949_5c81d69536922.png!small)

以下是我们在不使用pass-the-hash执行NTLM身份验证时看到的日志摘要。这为我们提供了正常行为的基线。

 **源主机**|  **目标主机**|  **域控制器**  
---|---|---  
4648事件：试图使用显式凭据登录| 4624 – 帐户已成功登录。登录类型为3，NTLM| 4768 – Kerberos 身份验证票证 (TGT)
请求。  
4624 - 帐户已成功登录。登录类型为2| 4672 – 分配给新的登录特权。| 4769 – Kerberos 服务票证请求。  
4672 – 分配给新的登录特权。|  | 4776 – 计算机试图验证帐户的凭据。  
  
现在，让我们来看看我们在Pass-the-Hash时看到的内容。

## Pass-the-Hash 事件

为了执行pass-the-hash测试，我们将做同样的练习，只是这次我们将使用mimikatz和pass the
hash命令，而不是使用runas作为用户启动进程。

我可以使用mimikatz命令，从内存中轻松获取用户Franklin的NTLM哈希值：

获取哈希后，我将使用以下命令执行pass-the-hash攻击：

    
    
    sekurlsa::logonpasswords
    
    
    Sekurlsa::pth /user:Franklin.Bluth /ntlm:[ntlm] /domain:jefflab.local

这将打开一个新的命令窗口，如果我使用相同的Sqlcmd命令连接到我的SQL Server的IP地址，你可以看到我现在被验证为Franklin Bluth：

![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552012977_5c81d6b1f1be3.png!small)

那么，让我们看看在执行pass-the-hash之后会生成什么事件：

## 工作站日志

在我的本地工作站上，我看到了事件4648，4624和4672与我正在进行合法的NTLM身份验证相同，但有一些关键的区别。

首先，4624事件的登录类型为9。这是一种NewCredential登录类型，是识别pass-the-hash的非常有用的方法。这是由安全研究人员确定的，我在我的测试中再现了它。

![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552013000_5c81d6c815eb1.png!small)

登录类型9非常罕见。但是，我能够生成一些运行使用模拟的应用程序的误报。关键的主要区别是登录进程对于pass-the-hash（来自我的测试）始终是“seclogo”，所以你可以过滤掉它以减少误报率。你可以在这里看到我能够让StealthAUDIT生成Logon Type
9事件，但它使用了Advapi登录进程。

![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552013022_5c81d6deda862.png!small)

另外，我注意到了4672事件的不同之处。此前，这确定了我模拟帐户Franklin Bluth的特权登录。这将为我登录到我的工作站的用户注册。

![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552013047_5c81d6f7349cc.png!small)

除此之外，SQL服务器上的日志是相同的。在域控制器上，关键区别在于你不会看到Kerberos身份验证。但是，这不是检测pass-the-hash的可靠方法，例如源自非受信任域的身份验证也会发生这种情况。

以下是我们在执行hash-hash时所看到的内容摘要。

 **源主机**|  **目标主机**|  **域控制器**  
---|---|---  
4648事件：试图使用显式凭据登录| 4624 – 帐户已成功登录。登录类型为3，NTLM| 474776 – 计算机试图验证帐户的凭据。  
4624 - 帐户已成功登录。 **(Logon type = 9** **Logon Process = Seclogo)**|  4672 –
分配给新的登录特权。|  
4672 – 分配给新的登录特权。 **(登录用户，而不是模拟用户)**|  
  
## Sysmon

为了最终检测pass-the-hash我使用了Sysmon，这有助于监视进程访问事件。我们在蜜罐检测中使用了它，你可以[阅读这篇文章了解如何对它进行设置](https://blog.stealthbits.com/implementing-detections-for-the-honeyhash/)。

当发生pass-the-hash时，你将看到事件ID 10显示从Mimikatz或你选择使用的pass-the-hash工具访问LSASS进程。

![如何检测Pass-the-Hash攻击？](https://image.3001.net/images/20190308/1552013075_5c81d71311a53.png!small)

## 构建 Pass-the-Hash 检测

现在，我们已经查看了所有有关pass-the-hash攻击的证据，构建检测pass the hash攻击的最简单方法是查找：

### 你工作站上的4624个事件

> Logon Type = 9
>
> Authentication Package = Negotiate
>
> Logon Process = seclogo

###  **LSASS进程访问关联Sysmon 10事件**

通过自定义事件日志过滤器，当这两件事同时发生时，你可以很容易地看到你网络上的pass-the-hash活动！

![16image-18.png](https://image.3001.net/images/20190308/1552013100_5c81d72c9761e.png!small)

以下是一个自定义事件过滤器，可用于显示特定信息。

    
    
    <QueryList>
      <Query Id="0" Path="Security">
        <Select Path="Security">
         *[System[(EventID='4624')]
          and
         EventData[Data[@Name='LogonType']='9']
          and
         EventData[Data[@Name='LogonProcessName']='seclogo']
         and
         EventData[Data[@Name='AuthenticationPackageName']='Negotiate']
         ]
         </Select>
      </Query>
      <Query Id="0" Path="Microsoft-Windows-Sysmon/Operational">
        <Select Path="Microsoft-Windows-Sysmon/Operational">
        *[System[(EventID=10)]]
        and
        *[EventData[Data[@Name='GrantedAccess'] and (Data='0x1010' or Data='0x1038')]]
    </Select>
      </Query>
    </QueryList>

希望通过本文的学习，能让你掌握学到如何通过事件日志检测pass-the-hash攻击。这需要在所有端点上启用日志记录。为了更简单地检测使用更高级技术的pass-the-hash攻击，你可能需要借助第三方威胁检测产品，如[StealthDEFEND](https://www.stealthbits.com/stealthdefend-product)。

在下一篇有关横向渗透的文章中，我将介绍pass-the-ticket的攻击及相关检测方法。欢迎大家阅读！谢谢！

## 参考文献

在撰写这篇文章时，我对该主题进行了大量的研究。以下内容可进一步的为你提供，有关如何理解和检测pass-the-hash的更多信息：

> [www.cyber](http://www.cyber)ark.com/threat-research-blog/detecting-pass-> the-hash-with-windows-event-viewer/
>
> <https://www.optiv.com/blog/pass-the-hash>
>
> <https://cyberwardog.blogspot.com/2017/04/chronicles-of-threat-hunter-> hunting-for.html>
>
> jblog.javelin-networks.com/blog/detecting-pass-ticket-pass-hash-attack-> using-simple-wmi-commands/
>
> silentbreaksecurity.com/windows-events-sysmon-elk-part-2/
>
> <https://www.sans.org/cyber-security-summit/archives/file/summit-> archive-1536265369.pdf>

 ***参考来源：[stealthbits](https://blog.stealthbits.com/how-to-detect-pass-the-hash-attacks/)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

