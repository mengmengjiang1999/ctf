在2021年的BlackHat大会上，由Will Schroeder和Lee Christensen发布了关于Active Directory
Certificate Services 利用白皮书《Certified Pre-Owned - Abusing Active Directory
Certificate
Services》，其中包含了大量的针对ADCS的攻击手法，通过对ADCS的攻击，将域渗透的攻击面扩展到了最大。尽管ADCS并不是默认安装在域环境中，但是在一些大型企业的域环境中却被广泛部署。

**本文分为上中下三篇，重点介绍如何在域环境中使用ADCS技术攻击域控制器，以及如何利用对象ACL来维持更高的权限。同时，我们将深入探讨ADCS的基础架构、攻击面以及后利用。这些内容将通过实战演练的方式进行讲解。**

##  **一、技术背景**

 **1.什么是PKI？**

 **公钥基础建设** (Public Key Infrastructure，简称PKI)
是一组由硬件、软件、参与者、管理者与流程组成的基础架构，其目的在于创造、管理、分配、使用、存储以及撤销 **数字证书**
。PKI依赖于经过身份验证的用户和受信任的资源之间的数字证书交换。可以使用证书来保护数据安全，并管理来自组织内外的用户和计算机的标识凭据。

 **2.什么是CA？**

 **数字证书认证机构** (Certificate Authority，简称CA)
是负责签发证书、认证证书、管理已颁发证书的权威机构。它要制定政策和具体步骤来验证、识别用户身份，并对用户证书进行签名，以确保证书持有者的身份和公钥的拥有权。

 **3.什么是证书？**

证书是一个小文件，此文件包含了公钥信息、拥有者身份信息、以及数字证书认证机构对这份文件的数字签名，以保证这个文件的整体内容正确无误。

拥有者凭此文件，可向电脑系统或者其他用户表明身份，从而获得对方的信任并授权访问或使用某些敏感的电脑服务。在证书注册过程中，客户端会生成公钥/私钥对，然后客户端将公钥发送到CA，而CA会确认客户端信息，用自己的私钥对其进行签名，随后再将包含客户端公钥的证书发送回客户端。

在概念上，证书相当于驾照，交警部门相当于CA。将身份信息与考核情况递交给交警部门，他们会给我们一个带有特有盖章的驾照，这样才可以开车上路。乘客会因为驾照而信任你的驾车技术，因为只有通过考核交警部门才会给你发驾照。如果严重违反了交通规则，你会被吊销驾照，不能开车载人。

 **4.什么是ADCS？**

AD域作为当前企业的办公内网广泛应用的集权管理方案，其域控在AD域内扮演着“大脑”的角色，至关重要，而不少企业在会在安装AD域的同时安装ADCS证书服务器来管理证书，攻击者会针对ADCS来进行攻击从何获取域控权限，导致AD集权安全收到威胁。

 **5.搭建ADCS**

搭建ADCS可参考文章[https://learn.microsoft.com/zh-cn/windows-server/networking/core-network-guide/cncg/server-certs/install-the-certification-authority](https://link.zhihu.com/?target=https%3A//learn.microsoft.com/zh-cn/windows-server/networking/core-network-guide/cncg/server-certs/install-the-certification-authority)，注意不要将证书服务器和域控搭建在一台主机上。

##  **二、什么是证书模板？**

证书模板定义了用户和设备如何根据模板来请求和使用企业CA颁发的证书。例如你可以创建一个模板来提供文件加密或电子邮件签名功能。CA依赖于ADDS来存储配置的模板。注意，只有在使用企业CA时才可以使用证书模板，这意味着，在使用独立CA时，必须手动创建每个证书请求，并添加需要在证书中包含的必须信息。

CA针对用户和计算机提供了模板， **可以向证书模板分配相应的权限**
，以定义可以管理模板的人员、可以执行注册或自动注册的人员，以及默认的有效期和续订期。可以 **通过复制预定义的证书模板来应用其他修改** 。

 **1.模板版本**

Windows Server AD CS 中的 CA 支持四个版本的证书模板，它们具有以下功能差异：

  * 版本 1 模板。这些模板只允许修改与证书相关的权限。在安装 CA 时，默认情况下会创建版本 1 证书模板。
  * 版本 2 模板。利用这些模板，可以自定义其他设置，如有效期和续订期。这也是支持自动注册的最低版本。AD CS 的默认安装内容包含多个预配置的版本 2 模板。你可以创建版本 2 模板，也可以复制版本 1 证书模板来创建新的版本 2 模板。
  * 版本 3 模板。版本 3 证书模板支持下一代加密技术 (CNG)。CNG 支持高级加密算法。可以复制默认版本 1 和版本 2 模板，并将其升级到版本 3。使用版本 3 证书模板时，可以将 CNG 加密和哈希算法用于证书请求、颁发的证书，以及密钥交换和密钥存档方案的私钥保护。
  * 版本 4 模板。版本 4 证书模板支持加密服务提供程序 (CSP) 和密钥存储提供者。还可以将其配置为要求使用相同的密钥进行续订。

可以使用certtmlp.msc打开证书模板控制台，使用certsrv.msv打开证书颁发机构。

![v2-94826a4f2c5b847e53952789dc7cd923_720w.webp](https://image.3001.net/images/20230421/1682055529_644221697b2a3550d272a.png!small)

其中版本架构就是我们上面所说的模板版本，预期用途就是这个证书模板申请之后用来干什么，例如可以客户端身份验证、服务器身份验证等，
**如果要设置模板特定用途可以右击模板属性在应用程序策略中添加或删除证书模板用途。**

![v2-7d4d9f7b3dd2f4279055481d45ff59cb_720w.webp](https://image.3001.net/images/20230421/1682055545_644221790fda73587aa14.png!small)

在证书模板属性中我们主要关注使用者名称、发布要求、扩展和安全。

 **2.使用者名称**

使用者名称就是我们后面申请证书要用到的SAN（subjectAltname）来指定身份，如果设置了在请求中提供，可以在申请证书的时候为指定的人生成证书。

![v2-92fadda95f6d614f3260f8dc7f22d5cb_720w.webp](https://image.3001.net/images/20230421/1682055558_64422186ae3b0a2aed303.png!small)

 **3.发布要求**

在发布要求中主要关注是否勾选了CA证书管理程序批准。如果用户有注册权限，但是在证书模板中勾选了CA证书管理程序批准，那么只有等到CA管理员批准才能够申请证书。

![v2-033f57ce6733be5e7b34374c1b66cffe_720w.webp](https://image.3001.net/images/20230421/1682055571_64422193aa7bc1d31a771.png!small)

 **4.扩展**

扩展中主要关注在上面我们说到的应用程序策略(pKIExtendedKeyUsage) **EKU**
,根据Specterops的研究，拥有以下的证书可用于kerberos身份认证。

  * 客户端认证
  * PKINIT客户端身份认证
  * 智能卡登录
  * 任何目的
  * 子CA

PKINIT默认是不存在的，我们可以手动创建。

![v2-9423880e7f7e510d2d838d1fe4ae24a8_720w.webp](https://image.3001.net/images/20230421/1682055589_644221a55cd874adce2b1.png!small)

其中对象标识符如下所示

描述 对象描述符（OID）

客户端认证 1.3.6.1.5.5.7.3.2

PKINIT客户端认证 1.3.6.1.5.2.3.4

智能卡登录 1.3.6.1.4.1.311.20.2.2

任何目的 2.5.29.37.0

子CA (no EKUs)

  

 **5.安全**

安全中我们主要关注Authenticated User组是否具有完全控制、写入和注册权限，如果拥有这些权限，则会造成一些安全问题。

![v2-28eb4e9d3f481107feabef34f87c1897_720w.webp](https://image.3001.net/images/20230421/1682055603_644221b3e13eb56c5618b.png!small)

  

 **三、如何注册证书？**

1. **证书注册流程**

![v2-f65a99156e4a847ff2b46ce315521b13_720w.webp](https://image.3001.net/images/20230421/1682055617_644221c128e15b67b57e4.png!small)

（1）客户端创建公钥和私钥

（2）客户端向企业 CA 服务器发送证书请求 (CSR)

（3）CA会判断，证书模板是否存在？证书模板是否允许 CSR 中的设置？用户是否允许注册证书？

（4）若符合上面条件CA 生成证书并使用 CA 私钥对其进行签名

  

2. **手动申请证书**

（1）客户端首先生成一个证书申请文件，我们可以通过openssl生成。

  

首先生成私钥

openssl genrsa -out server.key 1024

![v2-6d3ca8856fcca4002ddb7821835daf48_720w.webp](https://image.3001.net/images/20230421/1682055628_644221ccd9d67a6a1c0bf.png!small)

生成公钥

openssl rsa -in server.key -pubout -out public.key

![v2-4d217a36a2558e24f854c641899604bc_720w.webp](https://image.3001.net/images/20230421/1682055638_644221d6d6d8f9d772abc.png!small)

（2）根据私钥生成证书申请文件CSR

openssl req -new -key server.key -out server.csr

![v2-c07af1b6e14887af15870cd4aac0aa34_720w.webp](https://image.3001.net/images/20230421/1682055696_644222102ee8fc33329fe.png!small)

![v2-ae5eff34203efa1b791d4a8e97cb33ed_720w.webp](https://image.3001.net/images/20230421/1682055712_644222206cc236f08ccad.png!small)

（3）客户端把证书申请文件(CSR)发送给CA，然后选择一个证书模板。接着CA会判断证书模板是否存在，CSR请求的内容在模板中是否被允许使用，是否允许用户注册证书。注意此时我已经安装了证书web服务。

![v2-aa0e05ef6ad1894e304b3dabb1db8867_720w.webp](https://image.3001.net/images/20230421/1682055726_6442222e6ba23e810a710.png!small)

![v2-8b79a73e3032094d1204284bbeac682c_720w.webp](https://image.3001.net/images/20230421/1682055737_6442223968d19b703da78.png!small)

（4）CA用自己的私钥来签署证书，然后将其返回给客户端。

![v2-61961d13d9b6cb59c9d7165a0594c375_720w.webp](https://image.3001.net/images/20230421/1682055747_64422243c3b0f9b9db799.png!small)

 **3.使用网页注册证书**

在此之前我已经安装了证书Web服务，使用[http://ip/certsrv/](https://link.zhihu.com/?target=http%3A//ip/certsrv/)打开输入域账户密码

![v2-b6d016a72f6835e538fba2cb7b4da3ba_720w.webp](https://image.3001.net/images/20230421/1682055756_6442224c8ba40683357a8.png!small)

点击申请证书，高级证书申请

![v2-5c33ef463bd7007b5a2b82d8280e141c_720w.webp](https://image.3001.net/images/20230421/1682055773_6442225d277c3af68ea99.png!small)

接着创建并向此CA提交一个申请

![v2-7a76e27761fe0e33ad202dd45d9fac69_720w.webp](https://image.3001.net/images/20230421/1682055811_644222839fe66ecf480dc.png!small)

![v2-73f8f33e8058324bc680e4f903a4e77f_720w.webp](https://image.3001.net/images/20230421/1682055827_64422293b73d5c5c6d335.png!small)

![v2-a902b75ebc8d694ea58c60d2c40ae4b7_720w.webp](https://image.3001.net/images/20230421/1682055840_644222a02fd0a8fecfb27.png!small)

  

 **4.域内用户使用GUI请求证书**

如果在域内则可以启动certmgr.msc来申请用户证书，或者使用certlm.msc申请计算机证书。

![v2-865b0112464deeaa5ae5f2a80e1911e0_720w.webp](https://image.3001.net/images/20230421/1682055851_644222ab1391cf1f03400.png!small)

![v2-68b07502a15ec2c385c9855f4e178c69_720w.webp](https://image.3001.net/images/20230421/1682055866_644222ba1c8903121c731.png!small)

![v2-45904a36da55bac5f829961c17ce5268_720w.webp](https://image.3001.net/images/20230421/1682055882_644222ca187bc7099146e.png!small)

  

##  **四、ADCS在LDAP中的体现**

ADCS在ldap容器中位置位于

CN=Public Key Services,CN=Services,CN=Configuration,DC=<DOMAIN>,DC=<COM>

![v2-7b7960c2a918cf2a0f15ef481fd9393f_720w.webp](https://image.3001.net/images/20230421/1682055896_644222d867c230722b5dd.png!small)

其中Certification Authorities存放了受信任的根证书，AIA为证书的授权信息访问，CDP为吊销发布点，certificate
Templates 为证书模板，Enrollment Services为企业CA，OID为对象描述符。

##  **五、PKINIT协议**

PKINIT协议为kerberos
协议的一个扩展协议，可通过X.509证书来获取kerberos的TGT票据，PKINIT与kerberos差别主要在AS阶段，一种是基于对称密钥加密的认证方式，PKINIT是基于非对称密钥加密的认证方式，我们可以首先来看看正常kerberos的AS认证流程：

![v2-a1beae922aa7263bc4b8932d02ea2f76_720w.webp](https://image.3001.net/images/20230421/1682055912_644222e8211ce07c5e5dd.png!small)

（1）当域内某个客户端用户Client访问域内的某个服务，于是输入用户名和密码，此时客户端本机的Kerberos服务会向KDC的AS认证服务发送一个AS_REQ认证请求。请求的凭据是Client的哈希值NTLM-Hash加密的时间戳以及Client-info、Server-info等数据，以及一些其他信息。

（2）当client发送身份信息给AS后，AS会先向活动目录AD请求，询问是否有此Client用户，如果有的话，就会取出它的 NTLM-Hash，并对
AS_REQ 请求中加密的时间戳进行解密，如果解密成功，则证明客户端提供的密码正确，如果时间戳在五分钟之内，则预认证成功。

然后 AS 会生成一个临时秘钥 Session-Key AS，并使用客户端 Client 的 NTLM-Hash 加密 Session-key AS
作为响应包的一部分内容。此Session-key AS用于确保客户端和TGS之间的通信安全。还有一部分内容就是TGT，使用KDC一个特定账户的NTLM-Hash， 对 Session-key AS、时间戳、Client-info 进行加密。这个特定账户就是创建域控时自动生成的 Krbtgt
用户，然后将这两部分以及 PAC 等信息回复给 Client，即 AS_REP 。PAC 中包含的是用户的 SID、用户所在的组等一些信息。

 **接着来看PKINIT的认证流程：**

（1）client使用向CA申请的证书与client自己的私钥加密的时间戳发送给KDC。

（2）KDC 通过CA证书链验证client的身份，并获取到client证书里面的公钥，然后用公钥解密时间戳，并判断时间戳是否符合规定时间。

（3）若上述身份验证通过，并且时间戳符合规则则返回TGT与一个会话密钥（其中会话密钥使用下面两种算法生成）。

  

![v2-0c8234957524c5f609c99079412f3d86_720w.webp](https://image.3001.net/images/20230421/1682055925_644222f59ff5d85799ab0.png!small)

PKINIT 是不太常见的非对称密钥方法。客户端有一个公/私密钥对，并用他们的私钥对预验证数据进行加密，KDC 用客户端的公钥对其进行解密。KDC
还有一个公/私密钥对，允许使用以下两种方法之一交换会话密钥：

（1）Diffie-Hellman Key Delivery

该方法允许 KDC 和客户端安全地建立共享会话密钥，即使攻击者拥有客户端或 KDC 的私钥。会话密钥将存储在 TGT 的加密部分，它是用 Krbtgt
帐户的密钥（哈希）加密的。关于Diffie-Hellman，可参考这篇文章

[https://www.liaoxuefeng.com/wiki/1252599548343744/1304227905273889](https://link.zhihu.com/?target=https%3A//www.liaoxuefeng.com/wiki/1252599548343744/1304227905273889)

（2）Public Key Encryption Key Delivery

该方法使用 KDC 的私钥和客户端的公钥来封装由 KDC 生成的会话密钥。

具体流量方面的分析我会在后面的文章中介绍正常的kerberos与PKINIT之间的不同。

##  **六、证书模板错误配置攻击**

在2021年BlackHat发布的《Certified_Pre-Owned》白皮书中详细介绍了ADCS的滥用手法，下面针对不同的证书模板错误下导致域权限提升的攻击手法进行配置与分析。

 **1.ESC1**

  * 颁发CA授予低权限用户请求权限（默认）
  * 模板中CA管理员审批未启用（默认）
  * 模板中不需要授权的签名（默认）
  * 模板允许低权限用户注册
  * 模板定义了启用认证的EKU
  * 证书模板允许请求者在CSR中指定一个SAN

满足上面条件时，当攻击者在请求证书时可以通过

CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT字段来声明自己的身份，从而获取到伪造身份的证书。

使用certsrv.msc打开证书颁发机构，首先创建一个模板，右击证书模板 ->管理 -> 右击现有的证书模板 -> 复制模板，然后配置错误模板。

![v2-888fcc699d86d93f122075893764b9cc_720w.webp](https://image.3001.net/images/20230421/1682055944_64422308eb9d50eade589.png!small)

我们可以利用certify.exe find 来查看我们配置，发现我们的msPKI-Certificate-Name-Flag的属性值为ENROLLEE_SUPPLIES_SUBJECT,也就是可以指定使用者身份，即可以在请求中提供。

![v2-1720954d67f0784889ff1a4f1f53c65a_720w.webp](https://image.3001.net/images/20230421/1682055958_64422316cb788d7fd962f.png!small)

利用此模板来申请一个证书，此时我的账户名为test1，是一个域内本地管理员权限。

![v2-e41ce3de6a20353a9d53e05f88b87848_720w.webp](https://image.3001.net/images/20230421/1682055970_64422322a7dc643663c05.png!small)

使用命令：

Certify.exe request /ca:DC03Server.lohack.cm\lohack-DC03Server-CA-2/template:ESC1 /altname:administrator

![v2-baf172d8c9abcb4e4ff074364ae89896_720w.webp](https://image.3001.net/images/20230421/1682055983_6442232f7b6823d6a5a81.png!small)

查看我们申请证书的使用者名称。

![v2-ef52428bdd2db60732f553a3c5d6ccf5_720w.webp](https://image.3001.net/images/20230421/1682055996_6442233cf413914d40678.png!small)

接着从-----BEGIN RSA PRIVATE KEY-----到-----END CERTIFICATE-----复制出来，保存为ESC1.pem，然后利用openssl来转换为ESC1.pfx，无需设置密码。

①key后缀的，只包含私钥

②crt/cer 后缀的，只包含公钥

③csr后缀的，证书申请文件，不包含公钥，也不包含私钥。没啥用

④pfx,pem,p12后缀的，包含公私钥，我们最喜欢的。

![v2-4ab780a0ae63afe33044fd777709825a_720w.webp](https://image.3001.net/images/20230421/1682056016_644223509cf1624a1ce79.png!small)

利用工具Rubeus.exe来申请我们所需要的TGT，此处的ESC1.pfx就是我们刚刚申请的证书，可以发现在我们申请证书之前，我们dir域控是不行的。

![v2-a2e228e791e37be8fac371e975888e09_720w.webp](https://image.3001.net/images/20230421/1682056451_644225031034621c95d2b.png!small)

此时dir域控，可以发现成功dir。

![v2-993f14785ea1ac1b154f696214bd2cfd_720w.webp](https://image.3001.net/images/20230421/1682056487_6442252731ceba9a696fe.png!small)

此时查看凭据，存在cifs服务票据。

![v2-3d6c554cc0997efed155cc3727ad2393_720w.webp](https://image.3001.net/images/20230421/1682056553_6442256950f8f94b26624.png!small)

 **2.ESC2**

  * 颁发CA授予低权限用户请求权限
  * 模板中管理员审批未启用
  * 模板中不需要授权的签名
  * 模板允许低权限用户注册
  * 证书模板中定义了No EKU或Any EKU

同ESC1一样，生成模板，此时设置应用程序策略为空，也就是EKU为空或ANY EKU。

![v2-3c2ca29ccdc92537ef33188d74a0c647_720w.webp](https://image.3001.net/images/20230421/1682056572_6442257cd281cf89b0d7c.png!small)

利用certify.exe find 命令来查看模板ESC2配置,可以发现msPKI-Certificate-Name-Flag为ENROLLEE_SUPPLIES_SUBJECT,pkiextendedkeyusage与mspki-certificafte-application-policy都为空。

![v2-0a3da1d76f57900cc4b9a08af803c9b2_720w.webp](https://image.3001.net/images/20230421/1682056587_6442258b774688d580efd.png!small)

此时利用certify生成证书

Certify.exe request /ca:DC03Server.lohack.cm\lohack-DC03Server-CA-2/template:ESC2 /altname:administrator

![v2-7e019958c09c05b145ee72de905ac0a2_720w.webp](https://image.3001.net/images/20230421/1682056606_6442259e67e9c81db807e.png!small)

同ESC1一样生成pfx证书，然后利用rubues请求TGT票据，尝试列出域控目录

![v2-428c660accc96a36807214a2dcefcd1a_720w.webp](https://image.3001.net/images/20230421/1682056619_644225ab61d4451e13c5f.png!small)

![v2-ea49cd0cd037728b350818008fc55c56_720w.webp](https://image.3001.net/images/20230421/1682056631_644225b70c91fc79f3ca7.png!small)

 **3.ESC3**

模版一为颁发“注册代理”证书

  * 颁发CA授予低权限用户请求权限
  * 模板中CA管理员审批未启用
  * 模板中不需要授权的签名
  * 模板允许低权限用户注册
  * 证书模板中定义了证书请求代理EKU(1.3.6.1.4.1.311.20.2.1)

![v2-b7d31c0d4cf8470cb3ec120ef24a66b9_720w.webp](https://image.3001.net/images/20230421/1682056644_644225c40b93a6ba93059.png!small)

模板二为允许使用“注册代理”证书去代表其他用户申请身份认证证书：

  * 颁发CA授予低权限用户请求权限 (默认)；
  * 模板中CA管理员审批未启用 (默认)；
  * 模板中不需要授权的签名 (默认)；
  * 模板允许低权限用户注册；
  * 模板定义了启用认证的EKU；
  * 模板模式版本1或大于2并指定应用策略，签发要求证书请求代理EKU；
  * 没有在CA上对登记代理进行限制 (默认)。

![v2-6f39774922de4e37b96e0b8ad4b6ff98_720w.webp](https://image.3001.net/images/20230421/1682056656_644225d003341383f1f6a.png!small)

![v2-20a7eb5302c53ff6826166090ee02a57_720w.webp](https://image.3001.net/images/20230421/1682056667_644225dbd459ddd7ebe8b.png!small)

![v2-00857a12681e2c56a7a2689b80092fc2_720w.webp](https://image.3001.net/images/20230421/1682056678_644225e6bb78e26517de6.png!small)

Certify.exe request /ca:DC03Server.lohack.cm\lohack-DC03Server-CA-2
/template:ESC3

![v2-5679ae8777a04d333d67370ffdba04df_720w.webp](https://image.3001.net/images/20230423/1682228105_6444c389d731ceef7a9ba.png!small)

Certify.exe request /ca:DC03Server.lohack.cm\lohack-DC03server-CA-2/template:ESC32 onbehalfof:lohack\administrator /enrollcert:ESC32

![v2-3995724a2dcfeb33b00d40d89732712a_720w.webp](https://image.3001.net/images/20230423/1682228119_6444c397836abcd79932b.png!small)

Rubeus.exe asktgt /user:administrator /certificate:ESC44.pfx /dc:10.10.21.2
/ptt

![v2-724475ec4cef948435d98d366c8a426c_720w.webp](https://image.3001.net/images/20230423/1682228134_6444c3a6659f7901e51e9.png!small)

![v2-8a393fc63128f6d6e70e62d8f594e047_720w.webp](https://image.3001.net/images/20230423/1682228147_6444c3b3c5c5427c26124.png!small)

 **4.ESC4**

证书模板是 AD 中的安全对象，这意味着它们具有安全描述符指定哪些 AD
主体对模板具有特定权限。如果模板具有允许非特权的AD主机编辑权限，那么此模板便可面临攻击。

如果攻击者对模板对象拥有writeProperty权限，可以修改模板AD对象属性，则可以将错误配置写到模板中，例如允许域成员在mspki-certificate-name-flag属性中启用CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT标志，则与ESC1具有相同的滥用场景。

下面配置模板

![v2-57998cff64eafad2a6a44c5178f1a299_720w.webp](https://image.3001.net/images/20230423/1682228161_6444c3c1e5d3f0b3709b3.png!small)

查看模板配置

![v2-ac9affe7b5bd460f7249a4493ef467c1_720w.webp](https://image.3001.net/images/20230423/1682228173_6444c3cdbbb28e4396290.png!small)

接着使用admod修改mspki-certificate-name-flag

![v2-02b16b39f43c746739e105ccf6215589_720w.webp](https://image.3001.net/images/20230423/1682228191_6444c3df0842b19e09959.png!small)

![v2-3da07a38094c3f7b8305f326d794c976_720w.webp](https://image.3001.net/images/20230423/1682228270_6444c42e431a89ef020af.png!small)

申请证书

![v2-f72c7d1701f8aac1629fe1e2dc2a46ca_720w.webp](https://image.3001.net/images/20230423/1682228281_6444c43974ce05ad3e861.png!small)

最后可通过证书申请并导入票据

![v2-5b413b034ff5f1ce4891cab514e52404_720w.webp](https://image.3001.net/images/20230423/1682228291_6444c443b0e1f4ca8a0b0.png!small)

