## 0x00 摘要

本文介绍了Kerberos认证过程，并用wireshark抓包解析内容方便读者理解。同时分析了认证过程中的漏洞点，从而引出Kerberoasting攻击方法。并以HTB-Scrambled为靶机，以kali为攻击机展示了实际攻击中所利用的工具和指令。

##  **0x01 简介**

> Kerberos 是一种网络认证协议，其设计目标是通过密钥系统为客户机 /
> 服务器应用程序提供强大的认证服务。该认证过程的实现不依赖于主机操作系统的认证，无需基于主机地址的信任，不要求网络上所有主机的物理安全，并假定网络上传送的数据包可以被任意地读取、修改和插入数据。在以上情况下，
> Kerberos 作为一种可信任的第三方认证服务，是通过传统的密码技术（如：共享密钥）执行认证服务的。

Windows提供两种认证服务，Kerberos就是其中之一，另一种是NTLM认证。Windows中常见的使用账户密码登陆的服务都使用了NTLM认证，例如：SMB服务、MSSQL服务、RDP服务。简而言之，只要是账户密码登陆，且该服务是微软自己搞的，就使用了NTLM认证。

既然Kerberos不是简单的使用账号密码登陆，那Kerberos使用什么登陆呢？

答案是：票据。

下图为Kerberos认证过程（本文主要介绍前四步）：

![1665972550_634cb946c35898c8f8e63.png!small?1665972551494](https://image.3001.net/images/20221017/1665972550_634cb946c35898c8f8e63.png!small?1665972551494)

（图片来源：https://www.tarlogic.com/blog/how-kerberos-works/）

后续会用到的一些英文简称的汇总，方便查看：

  * Client: 访问服务的客户端
  * Server: 提供服务的服务器
  * KDC (Key Distribution Center): 密钥分发中心
  * AS (Authentication Service): 认证服务器
  * TGS (Ticket Granting Service): 票据授予服务
  * DC (Domain Controller): 域控制器
  * AD (Account Database): 用户数据库
  * TGT (Ticket Granting Ticket): 票据授予票据
  * ST (Servre Ticket): 服务票据

KDC（Key Distribution
Center）是默认安装在DC（域控制器）上Kerberos的主要服务，负责发行票据。它包含了协议中用到的AS认证服务和TGS服务。中文名为密钥分发中心。

## 0x02 Kerberos认证第一步：KRB_AS

### 通俗点说：

认证第一步解决的问题是：我是我。用户将使用的账户和密码发送至KDC上的AS（Authentication
Service），AS确认无误后返回一张TGT(Ticket Granting Ticket)票据，这个票据就像是ID
card，身份受到了官方的确认。后续我可以拿着这个票据去申请服务访问。

TGT翻译为中文后是：票据授予票据。初看会觉得这个名字很奇怪，他用于第二阶段的服务申请，在分析完第二阶段后大概就能理解这个名字的意思。

### 具体点说：

使用包分析能快速理解一个协议的运作过程。因此本文会借助网络包解释认证过程。包应该怎么生成呢，这就需要用到impacket包中的getTGT.py。impacket包内置在kali中。

    
    
    impacket-getTGT scrm.local/ksimpson:ksimpson

命令内容就是，使用Ksimpson作为账户，Ksimpson作为密码，向scrm.local申请TGT票据。scrm.local是靶机的域名，它的ip已经提前在/etc/hosts文件中写入，所以攻击机才能识别域名并连接到靶机。Ksimpson:ksimpson分别是账户和密码，使用冒号分割。账户和密码的获得其实是利用了kerberos的一个漏洞，将在后续分析完包后详细说明。

![1665991218_634d0232be8fd67c3f636.png!small?1665991219242](https://image.3001.net/images/20221017/1665991218_634d0232be8fd67c3f636.png!small?1665991219242)

拿到的ksimpson.ccache包含了TGT以及一个login session
key。现在我们来看一下这个过程产生的包。![1665991430_634d0306f1ce0b84c8d9c.png!small?1665991431425](https://image.3001.net/images/20221017/1665991430_634d0306f1ce0b84c8d9c.png!small?1665991431425)

此过程总共产生了四个包。第一个包是AS-REQ，但是返回了错误信息，导致第二次又发了一遍AS-REQ，才成功返回了AS-REP。

### 那么这两个包有什么区别呢？

第一个AS-REQ包：

![1665991871_634d04bf33bbf6aeb611b.png!small?1665991871842](https://image.3001.net/images/20221017/1665991871_634d04bf33bbf6aeb611b.png!small?1665991871842)

第二个AS-REQ包：  
![1665993758_634d0c1ec39f770e3abdb.png!small?1665993760648](https://image.3001.net/images/20221017/1665993758_634d0c1ec39f770e3abdb.png!small?1665993760648)我们发现差别就是在第二个包的padata类下多了pA-ENC-TIMESTAMP这一条信息，就是我鼠标选中的阴影部分。TIMESTAMP也就是大家都熟悉的时间戳。

![1665992437_634d06f55efd6340994f9.png!small?1665992437911](https://image.3001.net/images/20221017/1665992437_634d06f55efd6340994f9.png!small?1665992437911)

这条数据包含值、加密类型、密钥。也就是说，第一次向AS服务发送请求没有包含时间戳信息，因此AS服务器不予通过认证，告知攻击机需要满足预认证要求，使得攻击机第二次发出AS-REQ包，并包含了时间戳信息用于预认证。因此AS-REQ阶段，核心信息就是加密后的时间戳。只要时间戳信息满足要求，就能通过认证。那么时间戳的值是如何加密的呢，我们已经能够看到加密类型、密钥，实际上值的生成还需要一个额外输入：用户密码的NTLM_HASH。NTLM_HASH算法已经公开，getTGT.py会自动将我们输入的密码转换为NTLM_HASH格式，并使用它和密钥对当前时间戳进行加密。

对于AS服务器来说，由于AS服务是运行在域控上的，而域控保存了所有用户的NTLM-HASH值，因此只要AS服务器能够成功使用该用户的NTLM-HASH值解密，且解密出的时间戳在合理范围内，那么就通过了预认证，向该用户发放TGT。

AS-REP包内容如下：

![1665994427_634d0ebb2d7e855fd75cf.png!small?1665994427887](https://image.3001.net/images/20221017/1665994427_634d0ebb2d7e855fd75cf.png!small?1665994427887)

返回包包含两个主要信息：ticket和enc-part。

ticket包含了TGT，而TGT就是ticket分类下的enc-part。此部分enc-part内容是由域控的NTLM-HASH加密的，只有域控上的KDC能够解密，用于下一步的凭证。TGT中包含了一个关键信息：login session key。独立出来的另一个enc-part包含用户hash加密后的login session key。用户解密该部分后可以拿到原始的login session key。

### 为什么需要一个login session key，且用户和KDC都要知晓呢？

我们可以思考一下，一个单纯的TGT票据能不能在下一步中验证用户的身份？实际上，login session key机制就是要防止中间人窃取了AS-REP包拿到了TGT，从而在下一步骗取服务器信任的情况发生。login session key将在下一步和TGT一起使用。因为只有用户能解密拿到login
session key，防止了中间人冒充用户。

### 这中间有什么漏洞呢？

其实到现在为止，所介绍的内容是没有漏洞的，但是如果我用错误的用户名错误的密码和正确的用户名错误的密码发出getTGT请求，会发生什么事情呢？

### 错误的用户名错误的密码

命令：

![1665995856_634d1450429986ccfdeed.png!small?1665995856578](https://image.3001.net/images/20221017/1665995856_634d1450429986ccfdeed.png!small?1665995856578)

包内容：

![1665995911_634d14872a10462a0778e.png!small?1665995911453](https://image.3001.net/images/20221017/1665995911_634d14872a10462a0778e.png!small?1665995911453)

使用错误的用户名时，返回包会告知UNKNOWN，也就是说无法识别用户。

### 正确的用户名错误的密码

命令：

![1665996036_634d15041ab50b32e6194.png!small?1665996036419](https://image.3001.net/images/20221017/1665996036_634d15041ab50b32e6194.png!small?1665996036419)

包内容：

![1665996070_634d1526b2f641abf7f10.png!small?1665996071067](https://image.3001.net/images/20221017/1665996070_634d1526b2f641abf7f10.png!small?1665996071067)

此种情况下，还是会产生四个数据包，且第一个回包与用户密码正确时相同，都是需要预认证。第二个回包显示预认证失败。

### 结论

通过这两个小实验可以看出，用户名错误时，会显示UNKNOWN。密码错误时，会显示预认证失败。基于这些已知条件，我们马上就能想到一种攻击方式：枚举。实际上，ksimpson:ksimpson这一对用户名密码对就是通过枚举的方式得到。市面上已经有不少Kerberos用户名密码爆破工具，笔者使用的是Kerbrute。

    
    
    kerbrute userenum -d scrm.local --dc dc1.scrm.local A-ZSurnames.txt
    kerbrute passwordspray -d scrm.local --dc dc1.scrm.local users.txt ksimpson

第二条指令是密码喷射，指定用户密码去爆破用户名。为什么不能指定用户名爆破密码呢，因为Kerberos内置安全机制，失败次数过多会锁定账户。由于该靶机在其他地方提示了用户名和密码相同，所以可以根据爆破的用户名作为密码去进行爆破。

## 0x03 Kerberos认证第二步：KRB_TGS

此时用户拥有了一个TGT，一个原始login session key，然后他需要拿着这两样东西向TGS(Ticket Granting
Service)申请对某个服务的访问权限。我们作为一个攻击人员，事先当然不知道该域中运行着什么服务，那么有没有什么办法能够拿到服务列表呢？答案就是SPN扫描。

### SPN

我们知道，域是基于微软的活动目录(AD)服务工作的。每一个在域内运行的服务都需要在AD上注册SPN(Service Principal
Names)。每一条SPN信息都包含一个服务与一个允许登陆的账户。一个服务可以注册多条SPN以绑定多个账户。只有这样，当一个用户拿着TGT请求访问某个服务时，TGS才能通过查询SPN确定域内是否存在请求的服务。而查询SPN的操作并不是只有KDC才能做，拥有TGT的普通用户也能完成。所以，我们可以通过查询SPN来发现域内运行的服务列表。查询SPN同样可以使用impacket工具包。

    
    
    export KRB5CCNAME=ksimpson.ccache  
    python3 GetUserSPNs.py scrm.local/ksimpson -k -no-pass -dc-host dc1.scrm.local

第一条指令先设定环境变量。ksimpson.ccache文件是上一步中执行getTGT命令生成的，包含了login session
key和TGT。前面也已经解释，TGT是由域控NTLM-HASH加密的，包含了login session key和一些用户以及域信息。

第二条指令就是拿着TGT和login session key查询SPN。不使用kali内置的impacket-getUserSPNs的原因是，内置版本不支持-dc-host，而只支持-dc-ip。-dc-ip在此环境中会出现问题。而github上下载的最新版已经支持这个参数，所以笔者下载了最新的包，使用里面的python文件。

![1666056314_634e007acf73ee5c3d113.png!small?1666056313280](https://image.3001.net/images/20221018/1666056314_634e007acf73ee5c3d113.png!small?1666056313280)

这样我们就查询到了域内跑的服务：MSSQL，且允许登陆的用户名为sqlsvc。由于只有这一条SPN，自然而然，sqlsvc就是这个服务的所有者。

接下来看一下这个过程的包：

![1666058179_634e07c3c31a5050f968e.png!small?1666058178180](https://image.3001.net/images/20221018/1666058179_634e07c3c31a5050f968e.png!small?1666058178180)

总体来看，先发了两个KRB5的包，再发两个LDAP的包，又发了两个KRB5的包（编号越小发送时间越早）。TGS-REQ和TGS-REP就是Kerberos第二阶段的认证过程，TGS也是负责第二阶段的认证服务。这时候大家可能会奇怪，

### 第二阶段不是拿着TGT和login session key去请求访问某个服务的权限吗，为什么我扫描SPN服务也执行了第二阶段？

我们前面提到了，扫描SPN是需要拥有TGT的，而TGT就是在请求TGS服务起作用的，所以扫描SPN的过程中必然与TGS进行了交互。而与TGS服务交互必然是去请求一个服务的访问权限，我在扫描SPN时请求了什么服务呢？我们看一下具体的包内容，解答问题的同时顺便分析一下第二阶段认证的原理。

### No.7 TGS-REQ包：

![1666059143_634e0b87d2e20a857c569.png!small?1666059142285](https://image.3001.net/images/20221018/1666059143_634e0b87d2e20a857c569.png!small?1666059142285)

所有与认证相关的信息都在padata类下，req-body类下包含的是请求服务的信息。padata类下包含两个关键信息：ticket和authenticator。ticket已经提过多次，就是TGT，它是用域控HASH加密的，包含login
session key和一些其他信息。authenticator是用login session
key加密的时间戳，同时也包含了ip等客户端信息。拥有这两样信息，TGS就能完成认证。

首先，TGS先用域控HASH解密ticket，拿到login session key。再用login session
key解密authenticator，拿到时间戳和用户信息。如果时间戳在合理范围内，且ip等客户端信息也符合，那么认证通过。

### 接下来我们聚焦双方交换的对我们有用的body信息块

我们可以发现，SNameString的内容是ldap，也就是说我们此时请求的服务是ldap服务。我明明是扫描SPN，为什么请求了ldap服务呢？

前面介绍SPN时说过，域是基于微软的活动目录(AD)服务工作的，SPN也是注册在AD上的。再具体点说，SPN是注册在AD的LDAP上的。

> LDAP（LightweightDirectory Access Protocol），中文名为轻量目录访问协议。是一种用来查询与更新 Active
> Directory 的目录服务通信协议。AD 域服务利用 LDAP 命名路径（LDAP naming path）来表示对象在 AD
> 内的位置，以便用它来访问 AD 内的对象。更直观的说，可以把 LDAP
> 协议理解为一个关系型数据库，其中存储了域内主机的各种配置信息。（引用自https://zhuanlan.zhihu.com/p/474062138）

这样我们就能够理解为什么向TGS请求了LDAP服务。接下来我们看一下TGS返回了什么。

### No.12 TGS-REP包

![1666061118_634e133ed5015856b6ed1.png!small?1666061117330](https://image.3001.net/images/20221018/1666061118_634e133ed5015856b6ed1.png!small?1666061117330)

TGS-REP结构和AS-REP结构相同，都包含两个核心部分，ticket和enc-part。ticket是下阶段用到的服务票据，简称ST(Servre
Ticket)。里面是用该服务所有者NTLM-HASH加密的servive key，也包含了一些用户信息。而enc-part是用login session
key加密的service key，自然而然，用户就能解密该部分拿到login session key。到此为止，大家也应该能大致猜到第三部分的交互过程了。

### 简单介绍Kerberos第三步：

用户只要在和对应服务通信过程中首先发出ST，对应服务就能拿自己的HASH解密ST。拿到service
key和用户信息。这样，用户和服务都持有相同的sevice key，能使用它加密解密，互相通信。

### 回到攻击

至此，大家应该已经大致理解了Kerberos认证过程。我们通过Kerberos第一步认证的“信息泄漏”，可以爆破拿到域用户名和密码。借助LDAP服务，通过扫描SPN可以知道域内运行了什么服务以及绑定的账户名。接下去，又该如何进行攻击呢？毕竟，我们现在的用户没有MSSQL登陆权限，TGS自然不会发给我们ST和service
key。

### 诶，等等。。TGS真的不会发吗？

我们在扫描SPN的命令中添加一项参数-request，看看会发生什么

    
    
    python3 GetUserSPNs.py -request scrm.local/ksimpson -k -no-pass -dc-host dc1.scrm.local

![1666062373_634e18254f7f9dfb07581.png!small?1666062371835](https://image.3001.net/images/20221018/1666062373_634e18254f7f9dfb07581.png!small?1666062371835)

当当当当，我们拿到了ST！

再看一下这条命令包含的流量包：

![1666062456_634e1878c053bf8f054b3.png!small?1666062455213](https://image.3001.net/images/20221018/1666062456_634e1878c053bf8f054b3.png!small?1666062455213)

它多了两个KRB5包。那么这两个包包含了什么呢？

No.62 TGS-REQ

![1666062604_634e190ccc8dc2fc0eb77.png!small?1666062603365](https://image.3001.net/images/20221018/1666062604_634e190ccc8dc2fc0eb77.png!small?1666062603365)

它向TGS请求了scrm.local\sqlsvc的服务访问。

No.67 TGS-REP

![1666062725_634e1985b2b4873b65e68.png!small?1666062724094](https://image.3001.net/images/20221018/1666062725_634e1985b2b4873b65e68.png!small?1666062724094)

TGS返回了一个ST和service key！！WOW！Amazing！

### 柳暗花明又一村

这个现象的解释就涉及到TGS的一个工作逻辑了。在TGS的工作思维上，我只负责认证你TGT是否有效，以及你想要访问的服务是否存在。只要满足这两点，OK，你就通过了我的认证，我就发放给你ST，允许你和服务接触。

这之中最关键的一点是，TGS不检查用户是否有访问服务的权限！！！！

我不管你有没有权限，只要你证明了你是你，那么我就给发门票，上面写着你的名字。而让不让你进去，那是你要访问的服务该操心的事。如果你没有访问服务的权限，那么即使你拿到了ST，去和对应服务打招呼时，人家也完全不会让你进门。

既然我们即使拿到ST，也无法登入MSSQL服务，那么这个ST有什么用呢？

大家想一下，ST是由什么加密的？是由服务账户的NTLM-HASH。NTLM-HASH是根据密码hash而来，且其算法是公开的，同时加密算法也在包里明明白白的写着，那么，要生成ST，不确定的数据就是服务账户原始密码以及ST包含的原始数据。原始数据包括客户端信息、IP、客户端待访问的服务端信息、ST
有效信息、时间戳以及service
key。这一串数据可分辨性很强，IP以及时间戳都可以作为是否成功解密的特征。因此，只要枚举服务账户原始密码，进行爆破，再匹配解密后的格式特征，就能拿到服务账户的密码，前提是密码在你的密码字典中。

### 爆破服务密码

笔者使用hashcat作为爆破工具，主机是公司的服务器上跑的虚拟机，分配64核CPU，16G内存。跑了16个G的字典，也只跑了10分钟不到就跑出了密码。

![1666081536_634e63000eeeead0a1366.png!small?1666081536874](https://image.3001.net/images/20221018/1666081536_634e63000eeeead0a1366.png!small?1666081536874)

密码是：Pegasus60

到此，我们拿到了MSSQL密码是Pegasus60，账户名前面通过扫描SPN也知道了，是sqlsvc。因此我们拿到了服务账户的用户密码。

到此，大家可能会有一个疑惑，KDC也用了域控HASH加密了TGT，不是也能爆破吗？不错，但是这个靶机设置的域控密码很复杂，笔者没有跑出来，所以就没有展示了。额外一提，知道域控密码后，攻击者就能制作黄金票据。知道服务密码后，攻击者就能制作白银票据。对这两个感兴趣的可以搜搜其他资料，这里只是展示下白银票据的制作过程。

我们知道，我们拿到的ST里包含了用户名这个信息，由于TGT是Ksimpson这个用户的，所以ST里也说明了用户是Ksimpson。而这个用户没有访问MSSQL的权限，MSSQL服务自然不会允许登陆。

### 但是现在我们拥有了服务账户密码！

ST是用服务账户HASH生成的，我们拥有了服务账户密码，就能自己制作一个ST。只要里面包含用户名sqlsvc，自然就能登陆MSSQL服务了。这个ST就叫做白银票据。制作白银票据需要的信息包括：SPN，NTLM-hash，Domain SID，domain，user ID。

SPN已知，就是MSSQLSVC/dc1.scrm.local。

NTLM-HASH算法公开，根据原始密码就能计算。在线转换网站：https://codebeautify.org/ntlm-hash-generator

domain已知，就是scrm.local。

user ID，代表账户权限，500就是管理员。所以这里默认填写500.

我们只差Domain SID。它的数据格式和各部分含义读者可自行搜索资料。这里提供一个工具，impacket工具包中secretsdump.py。

    
    
    impacket-secretsdump -k scrm.local/ksimpson@dc1.scrm.local -no-pass -debug

![1666078279_634e5647b63743a9d83c7.png!small?1666078279990](https://image.3001.net/images/20221018/1666078279_634e5647b63743a9d83c7.png!small?1666078279990)

至此，拿到了domain SID。

使用impacket中的ticketer.py就能制作白银票据。

> impacket-ticketer -domain scrm.local -spn MSSQLSVC/dc1.scrm.local -user-id
> 500 Administrator -nthash b999a16500b87d17ec7f2e2a68778f05 -domain-sid
> S-1-5-21-2743207045-1827831105-2542523200

![1666078436_634e56e44d39d5e39e17a.png!small?1666078436546](https://image.3001.net/images/20221018/1666078436_634e56e44d39d5e39e17a.png!small?1666078436546)

至此，就拿到了权限为500的ST，可以登陆MSSQL。

![1666078600_634e578849c1c10da5070.png!small?1666078600602](https://image.3001.net/images/20221018/1666078600_634e578849c1c10da5070.png!small?1666078600602)

我们能够执行whoami命令。接下去只要一个反向shell，就能拿到该用户的shell了。

### 后记

自己花了四天学习了这部分内容，又花了两天时间写下了过程和分析。这也是第一次写文章，不足之处希望大家海涵。有错误之处也欢迎各位老师指正！

