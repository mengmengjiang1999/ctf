最近Window系统爆一个严重的安全漏洞，该漏洞使CryptoAPI无法正确验证椭圆曲线（ECC）密码证书，攻击者可以用该漏洞欺骗证书信任链。微软已经在昨天发布了一个重要软件更新，修复该漏洞。NSA同步也发布了安全升级公告，NSA评估该漏洞为严重漏洞。

该漏洞被编码为CVE-2020-0601，影响所有Microsoft
Windows版本加密功能。该漏洞将导致Windows证书验证的加密认证的证书信任体系失效，并且被利用执行远程代码。

# 漏洞概述

CVE-2020-0601漏洞位于Window的加密组件CryptoAPI。
CryptoAPI是微软提供给开发人员的Windows安全服务应用程序接口，可用于加密的应用程序，实现数据加密、解密、签名及验证等功能。

![2.jpg](https://image.3001.net/images/20200115/1579059291_5e1e885b08178.jpg!small)  

由Crypt32.dll提供的Microsoft Windows
CryptoAPI无法以正确验证ECC证书的信任链。攻击者可以利用该漏洞伪造受信任的根证书签发证书。Crypt32.dll中的CertGetCertificateChain()函数用来验证X.509的合法性，跟踪到受信任的根CA签发的证书，由于函数中存在漏洞，可以使证书，包括第三方非Microsoft的根证书，都不能得到正确的验证。

# 漏洞影响

支持使用带有指定参数的ECC密钥的证书的Microsoft Windows版本会受到影响。包括 **Windows 10以及Windows Server
2016和2019。Windows 8.1和更低版本以及Server 2012 R2和更低版本不支持带有参数的ECC密钥**
。因此，较早的Windows版本会直接不信任尝试利用此漏洞的此类证书，不受该漏洞影响。

利用此漏洞，攻击者可以越过Windows的认证信任体系，破坏可信的网络连接并交付可执行代码。可能影响信任的一些实例包括（不限于）： **HTTPS连接**
， **文件签名和电子邮件签名，以用户模式启动的签名可执行程序。**

漏洞使Windows终端将面临广泛的利用媒介攻击的风险。如果被利用，则将会使平台从根本上处于漏洞状态。如果不及时修补漏洞的可能会导致后果是严重风险。

# 缓解措施

及时升级补丁是目前唯一已知的缓解措施，建议大家立即升级。NSA建议尽快安装所有2020年1月星期二补丁程序(portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0601)，以有效缓解所有Windows 10和Windows Server
2016/2019系统上的漏洞。

![3.jpg](https://image.3001.net/images/20200115/1579059299_5e1e8863bb3c1.jpg!small)  

如果无法全范围的自动升级修补，建议系统所有者优先考虑提供基本和关键应用的主机，例如：

基于Windows的Web设备，Web服务器或执行TLS验证代理。

承载关键基础结构的主机：域控制器，DNS服务器，更新服务器，VPN服务器，IPSec协商终端。

还应优先考虑具有高利用风险的端点。包括：直接暴露于互联网的主机。特权用户经常使用的主机，比如运维机、堡垒机等。

管理员应及时升级这些主机，执行修补补丁。建议尽可能将补丁程序应用到所有受影响的主机，而不是优先处理特定类别的主机。除了安装补丁程序外，还可以通过其他措施来保护主机。网络设备和主机日志记录功能可能会阻止或检测某些利用方法，但是对所有平台升级修补补丁是最有效的缓解方法。

# 网络预防与证书检测

某些企业通过执行TLS检查但不使用Windows进行证书验证的代理设备来承载流量。这些设备可以帮助隔离代理后面的易受攻击的端点。

正确配置和管理的TLS检查代理可以独立地验证来自外部实体的TLS证书，并拒绝无效或不受信任的证书，从而保护主机免受试图利用漏洞的证书的攻击。

确保为TLS代理启用证书验证以限制暴露于此类漏洞并查看日志以发现利用迹象。

可使用数据包捕获分析工具（例如Wireshark）从网络协议数据中解析和提取证书以进行其他分析。我们可以用OpenSSL和Windows
certutil之类的安全应用来深入分析以检查有关证书恶意属性。

# 验证X509证书

Certutil检查X509证书：

certutil -asn <certificate_filename>

OpenSSL检查X509证书：

openssl asn1parse -inform DER -in <certificate_filename> -i -dump

或

openssl x509 -inform DER -in <certificate_filename> -text

该命令将解析并显示指定DER编码的证书文件中的ASN.1对象。

# 验证椭圆曲线证书

查看具有可疑属性的椭圆曲线对象的结果,具有明确椭圆OID值的椭圆曲线证书可以被判定为良性。例如，标准曲线nistP384的曲线OID值为1.3.132.0.34。具有明确定义的参数（例如，质数，a，b，基数，阶数和辅因子）与标准曲线的那些完全匹配的证书也可以被视为良性证书。

Certutil可用于列出已注册的椭圆曲线并通过运行以下命令查看其参数命令：

ocertutil -displayEccCurve

ocertutil -displayEccCurve <curve_name>

对应的OpenSSL可用：

openssl ecparam -list_curves

openssl ecparam -name <curve_name> -param_enc explicit -text

包含显式定义的椭圆曲线参数（仅与标准曲线部分匹配）的显式文本证书是可疑的，特别是如果它们包括受信任证书的公钥，并且可能表示善意利用尝试。

