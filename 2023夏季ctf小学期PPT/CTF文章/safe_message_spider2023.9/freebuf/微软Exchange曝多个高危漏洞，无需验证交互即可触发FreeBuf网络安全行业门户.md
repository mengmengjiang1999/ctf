3月2日，微软发布了Microsoft Exchange Server的安全更新公告，其中包含多个Exchange
Server严重安全漏洞，危害等级为“高危”，漏洞编号分别为CVE-2021-26855、CVE-2021-26857、CVE-2021-26858、CVE-2021-27065。

Exchange
Server是微软公司的一套电子邮件服务组件，是个消息与协作系统，主要提供包括从电子邮件、会议安排、团体日程管理、任务管理、文档管理、实时会议和工作流等协作应用。

![](https://image.3001.net/images/20210303/1614762783_603f531fbd8d557a185f0.png!small)

## 漏洞详情

###  **CVE-2021-26855**

> 该漏洞是Exchange中的服务端请求伪造漏洞（SSRF），利用此漏洞的攻击者能够发送任意HTTP请求并绕过Exchange
> Server身份验证，远程未授权的攻击者可以利用该漏洞以进行内网探测，并可以用于窃取用户邮箱的全部内容。

###  **CVE-2021-26857**

> 该漏洞是Unified Messaging 服务中的不安全的反序列化漏洞。利用该漏洞，攻击者可以发送精心构造的恶意请求，从而在Exchange
> Server上以SYSTEM身份执行任意代码。

###  **CVE-2021-26858**

>
> 该漏洞是Exchange中的任意文件写入漏洞。该漏洞需要进行身份认证，利用此漏洞可以将文件写入服务器上的任何路径。并可以结合利用CVE-2021-26855
> SSRF漏洞或绕过权限认证进行文件写入。

###  **CVE-2021-27065**

>
> 该漏洞是Exchange中的任意文件写入漏洞。该漏洞需要进行身份认证，利用此漏洞可以将文件写入服务器上的任何路径。并可以结合利用CVE-2021-26855
> SSRF漏洞或绕过权限认证进行文件写入。

## 影响范围

> Microsoft Exchange 2013
>
> Microsoft Exchange 2016
>
> Microsoft Exchange 2019
>
> Microsoft Exchange 2010

## 防范措施

1、微软官方已经发布了解决上述漏洞的安全更新，建议受影响用户尽快升级到安全版本，官方安全版本下载可以参考以下链接：

> CVE-2021-26855: <https://msrc.microsoft.com/update-> guide/vulnerability/CVE-2021-26855>
>
> CVE-2021-26857: <https://msrc.microsoft.com/update-> guide/vulnerability/CVE-2021-26857>
>
> CVE-2021-26858: <https://msrc.microsoft.com/update-> guide/vulnerability/CVE-2021-26858>
>
> CVE-2021-27065: <https://msrc.microsoft.com/update-> guide/vulnerability/CVE-2021-27065>

2、若无法及时进行升级，建议采用官方的临时措施进行防御：

> <https://www.microsoft.com/security/blog/2021/03/02/hafnium-targeting-> exchange-servers/>

  

