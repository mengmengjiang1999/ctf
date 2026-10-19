## **背景**

微软的 AD FS（联合身份验证） 服务是一种跨边界的身份识别认证服务，旨在让 AD 域外的服务使用 AD 域账户进行认证，可以在多个不同实体或组织之间实现
SSO（单点登录），经常用来完成云应用程序的单点登录，作为单点登录系统，其重要性不言而喻。

一个标准的 AD FS 部署拓扑如下图所示：

![1643102070_61efbf7698cfab4241324.png!small?1643102072007](https://image.3001.net/images/20220125/1643102070_61efbf7698cfab4241324.png!small?1643102072007)

AD FS 联合认证服务在域中一般需要至少两台服务器部署，一台位于 DMZ 区作为 Web 应用代理，代理来自域外的认证请求到另一台位于域内的 AD FS
服务器，域内的 AD FS 服务器验证用户的身份并且签名认证协议（如：SAML）中的令牌。

##  **01** 如何寻找 AD FS

1\. 访问默认的 adfs、fs 等子域名尝试发现 DMZ 区的 AD FS 代理

2\. 尝试访问一些默认路径 /adfs/ls、 /adfs/services/trust/2005/usernamemixed ...

3\. 访问 AD FS 部署后默认的测试页面 /adfs/ls/idpinitiatedsignon.aspx

4\. 登录相关服务查看是否重定向认证请求

##  **02** 窃取 Token Signing Certificate

AD FS 服务在用户认证成功后，会使用 Token Signing Certificate 对认证令牌进行签名
，如果该证书泄漏，攻击者可以用该证书签名任意令牌，从而伪造任意用户通过认证。该证书默认加密存储在 WID（Windows 的内部数据库）中，并只允许 AD
FS 服务账户访问。解密证书的关键数据在 AD（Active Directory）的属性中。

获取 Token Signing Certificate 并解密的步骤大概有如下 3 步：

### 1\. 获取 WID 中的加密数据

登录 AD FS 服务器后，用 AD FS 服务用户通过本地命名管道 .\pipe\microsoft##wid\tsql\query 连接到 WID
数据库，从数据库中可以查询出 AD FS 的配置，配置中的 EncryptedPfx 字段的值即为加密的 Token Signing Certificate

![1643102132_61efbfb418da04e044f69.png!small?1643102133974](https://image.3001.net/images/20220125/1643102132_61efbfb418da04e044f69.png!small?1643102133974)

### 2\. 获取推导解密密钥的 DKM key

![1643102144_61efbfc067ab62bf03305.png!small?1643102146286](https://image.3001.net/images/20220125/1643102144_61efbfc067ab62bf03305.png!small?1643102146286)

### 3\. 用 DKM key 计算解密密钥，密钥解密加密的 Token Signing Certificate

![1643102171_61efbfdb7e612ea985cb0.png!small?1643102173140](https://image.3001.net/images/20220125/1643102171_61efbfdb7e612ea985cb0.png!small?1643102173140)

获得解密后的证书，证书的默认有效期是一年，在此期间内可以签名任意认证令牌伪造任意用户登录使用了联合认证的系统，通常还会绕过 MFA。

##  **03** 滥用复制机制

企业环境中往往存在多台 AD FS 服务器，AD FS 使用 WCF 机制在多台 AD FS 服务器之间共享Token Signing
Certificate。这种方式会在 AD FS 服务器中启动一个监听 80 端口的 HTTP 服务来共享数据，虽然使用了 HTTP
协议传输数据，但传输的数据是加密的。在这种环境中，攻击者仅需要发起 HTTP 请求即可获取到加密的 Token Signing
Certificate，需要的用户权限是 AD FS 本地管理员权限，要求的权限更为宽松。而且整个复制事件没有日志记录，更加难以检测。

![1643102198_61efbff61d86e6c89526e.png!small?1643102199815](https://image.3001.net/images/20220125/1643102198_61efbff61d86e6c89526e.png!small?1643102199815)

##  **04** FoggyWeb 后门

FoggyWeb 是 Nobelium 组织用来从 AD FS 服务中窃取数据的恶意软件，微软对其进行了详细的分析。

FoggyWeb 后门会窃取 AD FS 的 Token Signing
Certificate，但使用了和已公开方法不同的方式获取证书，不同之处在于，FoggyWeb 在获取 DKM key 时，并没有使用公开方法去从 AD
属性中获取，而是直接从内存中已加载的 Assembly 的属性中获取，这样方式减少了被检测的可能。

现在企业越来越多的使用云服务，AD FS
作为跨边界单点登录的角色也日益重要。攻击者在域内除了攻击更容易被发现的域控外，另一个选择是攻击同等重要但防御并没有那么严格的 AD FS
，以后随着更多的安全研究员关注，可能会出现更多针对 AD FS 的多种攻击方式。

## 参考

https://o365blog.com/post/adfs/

https://www.mandiant.com/resources/abusing-replication-stealing-adfs-secrets-over-the-network

https://troopers.de/downloads/troopers19/TROOPERS19_AD_AD_FS.pdf

