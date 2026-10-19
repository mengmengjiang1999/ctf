## 关键词理解

KDC（Key Distributed Centre）：密钥分发中心，由以下两部分组成

  * AS（Authentication Server）：认证服务器，认证通过给你TGT

  * TGS（Ticket Granting Server）：票证发放服务器，通过你的TGT来发放ST

TGT（Ticket Granting Ticket）：授予票证

ST（Service Ticket）：服务票据

Client：访问特定资源的客户

Server：拥有特定资源的爹

## 特定账号

krbtgt是KDC的账号，密码是随机生成的，无法登陆

可以使用以下语句查询

    
    
    net user krbtgt

net user 账户名

![1661995611_63100a5b8ef0055da247d.png!small?1661995611791](https://image.3001.net/images/20220901/1661995611_63100a5b8ef0055da247d.png!small?1661995611791)

## Kerberos认证流程

KDC存着所有用户的账号和密码

### Client与AS的交互

双向认证，AS确认客户不是伪造的客户，客户确认AS不是伪造的AS

客户把自己个人信息发给AS，AS验证客户ID是不是在自己的KDC数据库中

AS检查到老铁没毛病，然后随机生成一个TGS-SessionKey

AS再给客户发送两个宝物：

  * 用客户的NTML HASH加密TGS-SessionKey之后，发送给客户

  * AS将客户个人信息（客户ID，需要访问的服务ID，IP地址，时间戳，存活时间和TGS-SessionKey）用TGS（krbtgt）的密钥加密打包成一个TGT发给客户

![1661995620_63100a64f000b69d4e081.png!small?1661995621227](https://image.3001.net/images/20220901/1661995620_63100a64f000b69d4e081.png!small?1661995621227)

客户拿到加密的TGS-Sessionkey后用自己的NTLM HASH解密得到TGS-SessionKey，因为没有TGS的密钥所以无法解密TGT

### Client与TGS的交互

第二次交流，客户将第一次交流的TGT完好无整的送给了TGS，同时还有用TGS-SessionKey加密的Authenticator（包含了客户ID和时间戳）

TGS利用自己的密钥解密TGT，获取TGT解密出来的TGS-SessionKey，然后用TGS-SessionKey去解密加密过的Authenticator，从而得到客户ID，然后比对一下Authenticator中的客户ID和TGT中的客户ID是否相等，比较来自
Authenticator 的时间戳和TGT的时间戳
(典型的Kerberos系统的容忍度是2分钟，但也可以另行配置)，检查TGT有没有过期（通过TGT中的存活时间），检查Authenticator是否已经在TGS的缓存中（不检查TGS缓存的话，那么如果TGS缓存中有Authenticator，会导致刷新TGS缓冲中的Authenticator，从而篡改客户ID和时间戳，导致重放攻击），所有检查过了之后，TGS随机生成一个Key（包含了客户ID和时间戳），用于加密后续客户和服务的通信数据，这个key就是Service-SessionKey，将这个Service-SessionKey用TGS-SessionKey加密，以及将客户ID、服务ID、IP地址、时间戳、存活时间和TGS-SessionKey用服务的密钥加密打包成ST（服务票据），然后将这两个发给客户

![1661995627_63100a6b0f3d4cd12a3b2.png!small?1661995627420](https://image.3001.net/images/20220901/1661995627_63100a6b0f3d4cd12a3b2.png!small?1661995627420)

客户拿到ST，ST无法解密，因为解密他的密钥只有服务才有，客户有TGS-SessionKey所以可以解密Service-SessionKey

### Client与Service的交互

客户将ST以及使用Service-SessionKey加密的个人信息Authenticator（包含客户ID和时间戳）发送给Service，然后Service利用自身密钥解密出ST，然后用ST中的Service-SessionKey去解密加密的Authenticator获取他的客户ID，然后比较两个ID是否相等，比较来自 Authenticator
的时间戳和来自ST的时间戳 (典型的 Kerberos 系统对差异的容忍度是 2
分钟，但也可以另行配置)，检查ST是否过期（根据ST里面的存活时间字段判断），检查 Authenticator
是否已经在对应服务的服务器的缓存中（为了避免重播攻击，前面说过了重播攻击）

![1661995637_63100a758b17ee13be3db.png!small?1661995637790](https://image.3001.net/images/20220901/1661995637_63100a758b17ee13be3db.png!small?1661995637790)

至此，所有的认证过程通过，客户端即可与远程服务完成了身份认证，可以进行后续的信息通信。

## PAC

PAC（Privilege Attribute Certificate，特权属性证书），是为了区分不同权限的客户。

PAC包含两个数字签名PAC_SERVER_CHECKSUM和PAC_PRIVSVR_CHECKSUM，以及客户的sid和客户所在的组，第一个PAC_SERVER_CHECKSUM是由服务的NTLM
HASH加密的，第二个PAC_PRIVSVR_CHECKSUM是由KDC（krbtgt）的NTLM HASH加密的

PAC在第一步过程中被放在TGT中，然后返回给客户，然后在第二步过程中客户发送自己的TGT给TGS，TGS会验证PAC（其实就是验证两个数字签名）是否被篡改，然后重新构造新的PAC放在ST中返回给客户，然后在第三步过程中将客户的ST发送给服务，让服务进行验证，服务用自身密钥解密ST后，然后用ST中的Service-SessionKey去解密加密的Authenticator获取他的客户ID，然后比较两个ID是否相等，比较来自 Authenticator
的时间戳和ST的时间戳 (典型的 Kerberos 系统对差异的容忍度是 2
分钟，但也可以另行配置)，检查ST是否过期（根据ST里面的存活时间字段判断），检查 Authenticator
是否已经在对应服务的服务器的缓存中（为了避免重播攻击，前面说过了重播攻击），检查完毕后，服务为了判断客户是否有合法的权限，需要将客户的信息传递给KDC，
KDC通过客户的信息判断客户所属的用户组信息，
用户权限等，然后KDC将结果返回给服务，服务利用结果（客户所属的用户组信息，用户权限等）与客户所索取的资源的ACL（Access Control
List，权限控制列表，这个列表记录了哪个用户哪个用户组可以访问此资源）对比，判断客户是否有权限访问此资源。

## 黄金票据和白银票据

### 黄金票据

黄金票据的原理就是，用krbtgt的NTLM HASH（也就是krbtgt的密码（密钥））来伪造TGT的内容。更改里面的ClientID参数与TGS-SessionKey等。让TGS以为我就是那个我所声称的人，当然我一般会声称自己是administrator![1661995643_63100a7bd9ce7442d29c5.png!small?1661995644168](https://image.3001.net/images/20220901/1661995643_63100a7bd9ce7442d29c5.png!small?1661995644168)

前提是：拥有krbtgt的NTLM HASH或者明文密码

### 白银票据

白银票据的原理就是伪造ST（Service Ticket，服务票据）。伪造ST的核心点是能够得到目标服务的服务器的NTLM
HASH（也就是对应资源服务器的密码（密钥））

前提是：拥有目标服务的服务器的NTLM HASH或者明文密码

### SPN攻击

SPN(Service Principal name)服务器主体名称。 SPN是服务在使用Kerberos
身份验证的网络上的唯一标识符（说白了他是某某服务的id，用来标识他是谁）。它由服务类、主机名和端口组成。

#### SPN分为两种类型：

一种是注册在活动目录的机器帐户(Computers)下，当一个服务的权限为 Local System 或 Network
Service，则SPN注册在机器帐户(Computers)下。

域中的每个机器都会注册两个2个SPN：HOST/用户名和HOST/用户名.域名

比如：![1661995648_63100a80e002f0fcfc985.png!small?1661995649156](https://image.3001.net/images/20220901/1661995648_63100a80e002f0fcfc985.png!small?1661995649156)

另一种是注册在活动目录的域用户帐户(Users)下，当一个服务的权限为一个域用户，则SPN注册在域用户帐户(Users)下。

SPN格式：

<service class>/<host>:<port>/<service name>

  * <service class>：标识服务类的字符串

  * <host>：服务所在主机名称

  * <port>：服务端口(存在一个实例且有默认端口可省略)

  * <service name>：服务名称(可省略)

例如：MySQL/DC.china.com/MySQL

SPN攻击就是找到那个“主人”是krbtgt的服务器（一般那台服务器为域控）。这样子就可以去请求到用krbtgt的NTML
HASH加密的TGT了。这个TGT加密的内容有客户ID，需要访问的服务ID，客户IP地址，时间戳，存活时间和TGS-SessionKey
。这时候可以用暴力破解技术来破解这个TGT，破解结果中有客户的相关信息，即可算作破解成功。进而得到krbtgt的密码，可以做黄金票据拿下整个域环境。

## 引用

[一文搞定Kerberos] https://zhuanlan.zhihu.com/p/266491528

[NTLM认证与kerberos认证与PAC相关知识]
https://blog.csdn.net/qq_41874930/article/details/108124366

