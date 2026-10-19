![kerberoasting](https://image.3001.net/images/20210523/1621744635_60a9dbfb91e80d33dcb09.png!small)

## 前言

往期文章：

[《内网渗透测试：Kerberos 协议与 Kerberos
认证原理》](https://www.freebuf.com/articles/network/273725.html%20)

[《内网渗透测试：Kerberos
协议相关安全问题分析与利用》](https://www.freebuf.com/articles/network/274035.html%20)

在上一篇文章《内网渗透测试：Kerberos 协议相关安全问题分析与利用》中，我们详细介绍了多种基于 Kerberos 协议进行的攻击，本节我们再来对
Kerberoast 攻击做一下介绍。

> 文中若有不当之处还请各位大佬多多点评
>
> 我的博客：<https://whoamianony.top/>

Kerberos 是一种支持票证身份验证的安全协议。如果客户端计算机身份验证请求包含有效的用户凭据和 SPN，则 Kerberos
身份验证服务器将授予一个票证以响应该请求。然后，客户端计算机使用该票证来访问网络资源。

## 什么是 SPN

SPN，ServicePrincipal Names，即服务主体名称，是服务实例（比如：HTTP、SMB、MySQL等服务）在使用 Kerberos
身份验证的网络上的唯一标识符，其由服务类、主机名和端口组成。Kerberos 认证过程使用 SPN 将服务实例与服务登录账户相关联，如果想使用
Kerberos 协议来认证服务，那么必须正确配置SPN。在使用 Kerberos 身份验证的网络中，必须在内置计算机帐户或域用户帐户下为服务器注册
SPN。对于内置机器帐户，SPN 将自动进行注册。但是，如果在域用户帐户下运行服务，则必须为要使用的帐户手动注册 SPN。

 **SPN 分为两种类型：**

一种是注册在活动目录的机器帐户（Computers）下。当一个服务的权限为 Local System 或 Network Service 时，则 SPN
注册在机器帐户（Computers）下。

另一种是注册在活动目录的域用户帐户（Users）下，当一个服务的权限为一个域用户时，则 SPN 注册在域用户帐户（Users）下。

### SPN的语法格式

    
    
    <service class>/<host>:<port> <servername>  
    服务类型    /对应机器名:服务端口[默认端口可不写]  
    ​  
    其中 <service class> 和 <host> 为必需元素

  * `<service class>`可以理解为服务的名称，常见的有 WWW、LDAP、SMTP、DNS、HOST 等，例如`MSSQLSvc/WIN-CKT0M35R6UO.top.pentest.top:1433`

  * `<host>`有两种形式，FQDN 和 NetBIOS 名，例如`WIN-CKT0M35R6UO.top.pentest.top`或者是`WIN-CKT0M35R6UO`

  * 如果服务运行在默认端口上，则端口号`<port>`可以省略

在内网中，SPN 扫描通过查询向域控服务器执行服务发现。这对于红队而言，可以帮助他们识别正在运行着重要服务的主机，如终端，交换机等。SPN 的识别与发现是
kerberoasting 攻击的第一步。

## Kerberoasting

Kerberos 协议在请求访问某个服务时存在一个缺陷，Kerberoasting
正是利用这个缺陷的一种攻击技术。首先，我们来整体了解一下正常情况下一个用户请求访问某个服务时会经过哪些步骤：

  * 首先用户将 AS-REQ 数据包发送给 KDC 密钥分发中心，要对一个域进行身份验证。

  * KDC 收到用户的请求后会验证用户的凭据，如果凭据有效，则返回 TGT 认购权证，该 TGT 认购权证用于以后的 ST 服务票据的请求。

  * 如果用户想通过身份认证访问某个服务的话，那么他需要发起票据授予请求，请求中包含 TGT 以及所请求服务的 SPN 服务主体名称。

  * 如果 TGT 有效并且没有过期，那么 TGS 会从 TGT 认购权证中提取信息创建一个用于访问目标服务的一个 ST 服务票据，该 ST 服务票据使用服务账户的凭据进行加密。然后，域控制器开始查找哪个帐户在 ServicedPrincipalName（SPN）字段中注册了所请求的 SPN。

  * 用户收到包含了服务票据的 TGS 响应数据包。

  * 最后，服务票据会转发给目标服务，然后使用服务账户的凭据进行解密。

整个过程比较简单，我们需要注意的是，服务票据会使用服务账户的哈希进行加密，这样一来，Windows域中任何经过身份验证的用户都可以从 TGS 处请求 ST
服务票据。由于服务票证是用链接到请求 SPN 的帐户的哈希加密的，所以攻击者可以离线破解这个加密块，恢复帐户的明文密码。

下面我们将我才能够一下几个步骤讲解 Kerberoasting 攻击的利用：

  * SPN 服务主体名称发现

  * 请求服务票据

  * 服务票据的导出

  * 服务票据的暴力破解

## SPN 服务主体名称发现

由于每台服务器都需要注册用于 Kerberos 身份验证服务的
SPN，因此这为在不进行大规模端口扫描的情况下收集有关内网域环境的服务运行信息提供了一个更加隐蔽的方法。

### 使用 SetSPN 查询

SetSPN 是 Windows 系统自带的工具，可以查询域内的 SPN：

    
    
    setspn -Q */*    # 查看当前域内所有的 SPN  
    setspn -T whoamianony.org -Q */*    # 查看指定域 whoamianony.org 注册的SPN, 如果指定域不存在, 则默认切换到查找本域的 SPN  
    setspn -L <username>/<hostname>    # 查找指定用户/主机名注册的 SPN

![image-20210523103513577](https://image.3001.net/images/20210523/1621744636_60a9dbfc09fb6d1ad37a2.png!small)

![image-20210523103814662](https://image.3001.net/images/20210523/1621744636_60a9dbfc6fcc30397b0fe.png!small)

### 使用 GetUserSPNs.ps1 脚本

  * 项目地址：<https://github.com/nidem/kerberoast.git>

GetUserSPNs 是 Kerberoast 工具集中的一个 PowerShell 脚本，可以用来查询域内用户注册的 SPN。

    
    
    Import-Module .\GetUserSPNs.ps1

![](https://image.3001.net/images/20210523/1621)

