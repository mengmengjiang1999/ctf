##### 1、Active Directory 安全概述

不同的`AD`对象的信息是以对象和属性的格式存储在`AD`中的，所有这些都是在我们前面讨论的活动目录模式中定义的。因为`AD`具有高度的可扩展性，其设计方式是通过验证请求并以访问所需资源的方式处理大量的读取和搜索操作以及更改和更新。所以这些存储在`Active
Directory`中的数据会在整个森林中复制。在这一节中，我们将从安全的角度讨论`Active
Directory`，并了解`AD`环境中身份认证是如何进行的。我们将讨论在`AD`中使用的不同安全协议，以及不同级别的权限。

##### 2、Kerberos

`Kerberos`是一种身份验证协议，最初由
`MIT`开发并使用对称密钥加密技术。为了验证用户身份，`AD`需要可信的第三方授权。微软使用`Kerberos`作为域环境中的首选认证协议。`Kerberos`（或
`Cerberus`）是希腊神话中守卫地狱入口的三头犬的名字，就像它的名字一样，它需要三个实体来进行认证：

  * 客户端（或需要访问某项服务的用户）
  * KDC（密钥分发中心）
  * 资源服务器（托管用户所需的服务）

有关`Kerberos`协议的详细信息可以在`RFC
4120`https://datatracker.ietf.org/doc/html/rfc4120中找到。

##### 3、Kerberos的组成部分

`Kerberos`有以下几个组成部分：

  * 委托人（Principal）：客户端（用户）或服务。
  * 领域（Realm）：一个逻辑 Kerberos 网络。
  * 票据（Ticket）：验证主体身份的数据。
  * 凭据（Credentials）：一个票据和一个服务密钥。
  * KDC：密钥分发中心，负责验证委托人的身份。
  * TGT：授予票据
  * TGS：票据授权服务
  * C/S：客户服务器，关于两者之间的通信。

在 `Active Directory`环境中，每个域控制器就像一个密钥分配中心，提供两个核心服务：

  * 认证服务：对客户进行认证并向他们发放票据。
  * 票据授予服务：向经过认证的客户发放票据，以访问其他资源。

在这种情况下，用户被允许证明他们的身份，以安全地访问域资源。`Kerberos`使用票据来允许用户对一个主体（如服务）进行身份验证。要请求一个服务的票据，你必须指定它的服务主体名称，例如`HTTP/RDSWEB01`。`SPN`是服务账户的唯一标识符。

##### 4、TGT

`TGT`是 "`Ticket Granting Ticket`(授予票据)"的缩写。授予票据 (`TGT`)
是一种特殊票据，它允许客户端在同一`Kerberos`领域内获得额外的
`Kerberos`票据。当客户端向密钥分发中心（`KDC`）发送票据请求时，`KDC`为客户端创建一个票据授予票据（TGT），（用客户端的密码作为密钥对其进行加密）并将加密的`TGT`发回给客户。然后，客户使用其密码来解密`TGT`。如果客户成功地解密了`TGT`（即，如果客户给出了正确的密码），它将保留解密的`TGT`，该`TGT`用于表明客户端的身份的证明。

> TGT 允许客户端获得额外的票证（如 TGS），从而获得特定服务的许可。

##### 5、TGS

`TGS`是 "`Ticket granting service`（票据授予服务）"的缩写。`TGS`是一个 `KDC`组件，当客户端请求连接到
`Kerberos`服务时，它将签发服务票据。客户端需要有一个有效的 `TGT`，只有这样 `TGS`才会被签发给它。

##### 6、Inter-Realm TGT（跨领域TGT）

如果在森林间信任的认证中，则不是使用`Domain1`的`krbtgt`账户进行加密。而是用各域之前交换的域间信任密钥对票据进行加密/签名，这被称为
"域间票据-授予-票据/TGT"。然后`Domain2`验证转介中包含的`TGT`，使用先前协商的跨域信任密钥对其进行解密并继续进行后续工作。跨领域的`TGT`是可以伪造的。我们将在后续文章中进行介绍。将在后续文章中详细解释执行`kerberoasting`时的`Kerberos`过程。

假设一个来自`Domain1`的客户想要访问位于`Domain2`的服务器。以下是它的发生过程：

1、一个来自`Domain1`的客户向`DC1`请求一个`TGT`。

2、`DC1`返回一个`TGT`（使用用`krbtgt`哈希加密）。

3、客户端出示`TGT`并请求`TGS`以访问`Domain2`的服务器。

  * 由于`DC1`在当前域中没有找到服务器，并且意识到`TGS`需要由（`Domain2`的）`DC2`发出，因为服务器位于`Domain2`中。所以它用`Inter-Realm TGT`响应给客户。

4、客户端向`Domain2`中的`DC2`出示`Inter-Realm`信任密钥加密的`TGT`，并请求`TGS`访问服务器。

5、`DC2 `发回使用服务器帐户哈希加密的服务器的 `TGS`。

6、客户端向服务器出示`TGS`（用服务器的账户哈希值加密），以便访问。

##### 7、Kerberos 认证流程

![image-20220414103511527](https://image.3001.net/images/20220426/1650953304_62678c58be80f6c40c7e9.png!small)

`Kerberos`认证的工作方式是这样的：

  * 客户端向密钥分发中心（`KDC`）请求认证票据（`TGT`）。
  * 密钥分发服务器验证证书，并发回一个加密的`TGT`和会话密钥。
  * `TGT`由客户端存储，当它过期时，本地会话管理器将请求另一个`TGT`。

当客户端需要访问网络上的服务/资源时，遵循以下流程：

  * 客户端向`TGS`发送当前的`TGT`，并附上想要访问的资源的服务主体名称（`SPN`）。
  * `KDC`验证客户的`TGT`，同时验证客户是否有权访问服务。
  * `TGS`向客户端发送一个有效的服务会话密钥。
  * 客户端将会话密钥转发给服务，以证明它有访问权，而服务则授予访问权。

 **PAC validation（PAC 验证）**

在上图中，`PAC`验证发生在资源服务器和`KDC`之间。让我们更多地讨论一下`PAC`验证。`PAC(Privilege Attribute
Certificate
)`(特权属性证书)代表一种结构（几乎包括在所有票据中），它包含有用的信息，如安全标识符、组成员资格、用户配置文件信息和密码凭证。`PAC`是用`KDC`的密钥签署的。

`PAC`验证是根据活动目录验证用户在服务器上的`PAC`以确保它其有效的过程。服务器的操作系统执行`Kerberos
PAC`验证，以防止中间人攻击篡改`PAC`结构，避免伪造的`PAC`。

可以使用注册表项`ValiateKdcPacSignature`启用它，该注册表项位于以下位置：

    
    
    HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa\Kerberos\Parameters
    "ValidateKdcPacSignature"=dword:00000001
    

当这个条目的值为`0`时，`Kerberos`不会对作为服务运行的进程进行`PAC`验证。当这个条目的值为`1`时，`Kerberos`执行`PAC`验证。修改此注册表项后，你必须重新启动计算机。当该条目不存在时，系统的行为就像该条目存在并且值为`1`。在`Windows
Server 2008`中，该条目的默认值为`0`。

##### 8、NTLM

`NTLM`是`NT Lan Manager`的缩写。它是一种质询-响应身份验证协议。在 `Kerberos`之前，`Microsoft `使用
`NTLM`进行身份验证。目标计算机或域控制器对密码进行质询和检查，并存储密码哈希值以便继续使用。它仍然适用于工作组中的老旧客户端和系统。

`NTLM`依靠一个质询-响应身份验证协议来确认用户，而无需他们提交密码。

参考资料：

https://docs.microsoft.com/en-us/archive/blogs/openspecification/understanding-microsoft-kerberos-pac-validation

##### 9、说明

本文由笔者在原文上编译，转载请注明原文出处。

原文出处：[Active Directory Security Fundamentals (Part 1)-Kerberos](https://rootdse.org/posts/active-directory-security-1/)

