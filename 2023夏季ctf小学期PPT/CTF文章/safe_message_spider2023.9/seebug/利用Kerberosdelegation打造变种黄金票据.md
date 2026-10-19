作者：n1nty@360 A-TEAM  
公众号：[n1nty](https://mp.weixin.qq.com/s/gw1EIMnXQ9tCZLkdvKdzAg "n1nty")

正文开始前，再次感慨一下 mimikatz 与 impacket
二位作者的强大。在有了本文的思路后本来想着自己写一下代码实现一个小工具，来让本文显得有点技术含量，一查资料，发现他们早都已经把相关工具写好了。 :-(

所以，决定直接用 impacket
已经实现好的工具来跟大家介绍一下。但是，为了避免这篇文章堕落成一篇单纯的工具介绍类的水货，我会像以前一样，在文章内简述涉及到的相关背景知识。想深入真正地理解的话，还是建议自己去看一下
Kerberos RFC，我在最后会贴出我看过的与本文有关的资料。

#### 黄金票据，golden ticket

所谓黄金票据，就是我们自己通过窃取 KRBTGT 这个账号的 NTHASH 或者 AESKEY 后，自己离线伪造的 TGT，伪造 TGT 的全程不经过
KDC。 正常情况下 TGT 全是由 KDC 在验证了客户端的身份后（kerberos pre-authentication）发给客户端的。KDC
会对自己所发出去的所有票据进行加密，可以支持多种不同加密算法，不同的加密算法有不同的 key。

比如支持的加密算法有：

![](https://images.seebug.org/content/images/2018/06/148deea5-4979-491f-88ac-7c04d9b18e01.png-w331s)

我们通过 mimikatz 可以导出 KRBTGT 账号的这几种 KEY，然后离线生成加密的 TGT，这就是黄金票据的原理。我们可以利用 mimikatz
或者 impacket 的 ticketer.py 来生成黄金票据。

说到了这里，你是否明白 pass the key 的原理？:-)

#### 变种黄金票据优点及缺点

前面说到了，要生成黄金票据，我们是需要 KRBTGT 这个账号的相关 KEY 的（NT HASH，AES KEY）。而且一旦 KRBTGT
的账号密码被改过，以前生成的黄金票据就作废了。

而利用 Kerberos delegation 做成的另类的黄金票据，并不直接依赖于 KRBTGT
账号。当然也有它的不足之处，就是它会在系统日志里面留下一些痕迹，而且需要我们对域用户进行一些改动。

#### Delegation，委派

假如用户 A 利用 windows 身份验证（或者其他验证方式也可以，更复杂一些而已）登陆了远程服务器上的 Service1， **Service1
随后利用用户 A 的身份向另一台服务器上的 Service2 发起了某个请求** ，这就是委派。

实际的场景有可能是用户 A 利用 Windows 身份验证访问了一个网站，请求网站内的一个文件，但是这个网站服务器本身并没有这个文件， **它需要利用用户
A 的身份去访问另一台服务器** ，从另一台服务器上获取这个文件后再返回给用户。为什么网站会利用用户 A
的身份去获取文件，而不是直接利用网站自身的权限去获取呢？因为要充分利用 Windows
系统自身提供的权限控制啊，也许有的用户有权限访问那个文件而有的用户没有权限啊。

#### Kerberos delegation

前面说到了，delegation 的意思就是客户在访问一个服务的时候，这个服务利用客户端的身份又去访问了另一个服务。 delegation 是为了解决
authentication double hop 问题。我之前 PSEXEC 那篇公众号文章从另一个角度提到了 double hop。

user --> service1 --(以 user 的身份)--> service2

kerberos 实现 delegation 有以下几种方案：
![](https://images.seebug.org/content/images/2018/06/30697148-b6c2-4e7a-a02e-f8f8e0387d1a.png-w331s)

#### Forwardable TGT/Unconstrained delegation

指的是 user 在访问 service1 的时候，如果 service1 的账号开启了 unconstrained delegation
的功能（需要域管理员进行设置），则 user 访问 service1 时会将自己的 TGT 发送给 service1。随后 service1 就可以利用这张
TGT 以 user 的身份 **去访问任何服务，所以它叫 “无限制委派” 或者 “非受限委派”。** 这造成了很大的风险，用户的身份可能被这个
service1 滥用。

如果你打下一台有 unconstrained delegation 服务的机器，也许你可以从这台机器上导出大量用户的 TGT。为了避免这个问题，出现了
constrained delegation

#### Constrained delegation，受限委派

前面说到 unconstrained delegation 有可能导致 service1会 滥用 user 身份的风险。所以出现了 constrained
delegation。实现的方式就是，域管理员对 service1 的账号加以限制，当 user 访问 service1 的时候，使得 service1
只能利用 user 的身份去访问 service2，而无法像 unconstrained delegation 那样去访问域中的任何服务。

#### S4U, Service for user

S4U 是微软对 MIT Kerberos 的一个扩展，这个扩展带来了两个功能：

  1. Service for User to Proxy (S4U2proxy)，这个就是 constrained delegation
  2. Service for User to Self (S4U2self)，这个也被称为 Protocol transition

#### Protocol transition

也就是 S4U2self (Service for User to Self)，作用就是验证协议切换。

user --> service1 --> service2

user 访问了 service1 后，service1 要利用 kerberos 协议以 user 的身份去访问 service2，但是这要求 user
访问 service1 的时候，也是利用的 kerberos 协议去与 service 1 进行验证的。那么如果不是的话怎么办呢？

service1 有可能只是一个网站，user
在登陆这个网站的时候只是像登陆普通网站一样在一个表单里面输入了一个账号密码而已，而且这个账号密码可能只是网站内部的账号密码，并不是域的账号密码。

这个时候就需要 protocol transition 来进行验证协议切换。

这里涉及到 S4U 协议的细节内容，不太好描述，有兴趣的直接看协议文档吧：

<https://msdn.microsoft.com/en-us/library/cc246071.aspx>

简而言之一句话： 如果 service1 有了 protocol transition 权限的话，service1 可以 **以任何一个域内用户的身份**
向 KDC 申请一张访问 service1 自身的票据， **而且不需要知道目标用户的密码** 。比如 service1 可以以域管理员
Administrator 的身份向 KDC 申请一张访问
service1自身的票据。（如果你能找到这么一个服务，并且可以通过这个服务执行代码的话，你是有可能直接利用这个功能提权至域管理员的，当然这个时候你获取到的域管权限是被限制在这台机器上的，无法访问别的服务器。）

#### 汇总

背景知识介绍完成，下面讲一下如何利用 S4U2self 与 S4U2Proxy 的功能来实现变种黄金票据。这肯定是建立在你已经有了域管权限的基础上。

假如有域 EAST.COM  
域控名为：2008-EAST-DC  
域控 IP 为：192.168.99.150  
另一台域内机器名：2008-DM1，IP 为 192.168.99.101  
我自己使用的机器为 MAC，IP 为 192.168.99.1

同时，我的 /etc/hosts 中有如下配置，这是为了照顾 impacket 的代码逻辑（或者说 kerberos 的工作逻辑，在 kerbeors
的世界里机器的 netbios name 或 FQDN 是很重要的），否则工具无法正常工作：

192.168.99.101 2008-dm1  
192.168.99.150 east.com  
192.168.99.150 2008-EAST-DC

1.我们需要有一个普通域账号（你可以新建一个，或者选一个不怎么常用的），且这个域账号的密码一定要非常强壮。防止被别人利用 kerberoast
类的攻击破解出来。 假如我这里选择名为 ateam 的账号，因为只是演示，所以我把密码设置为 1qazCDE#

![](https://images.seebug.org/content/images/2018/06/ac7f8a5a-7cbb-4def-a515-f4fba9bfc19e.png-w331s)

2.要让这个域账号成为“服务账号”（并不需要以这个账号来启动任何服务），所以我们需要在这个域账号上面设置 spn。只有服务账号才可以开启 S4U 的功能。

setspn -U -A variant/golden ateam

![](https://images.seebug.org/content/images/2018/06/6331622f-5a23-422c-9844-ce7198cbffe6.png-w331s)

3.为 ateam 账号设置了 SPN 后，用域管理员权限为这个账号开启 s4u2self (protocol transition) 的权限，并设置
S4U2Proxy 列表。

![](https://images.seebug.org/content/images/2018/06/aefaf825-a672-42d0-be67-a8ba53450be6.jpg-w331s)

第一处箭头表示为此账号开通 constrained delegation 权限，也就是 S4U2Proxy 权限。第二处箭头表示为此账号开通
protocol transition 权限，也就是 S4U2self 权限。第三处本应是一个由目标 SPN 组成的列表，我们要添加的目标 SPN 是
krbtgt/EAST.COM。但是因为 krbtgt 这个域账号默认是禁用的而且无法启用，导致我们无法利用界面来添加这个 SPN。

可以用如下 powershell 脚本：

    
    
    Import-Module activedirectory
    $user = Get-ADUser ateam -Properties "msDS-AllowedToDelegateTo"
    Set-ADObject $user -Add @{ "msDS-AllowedToDelegateTo" = @("krbtgt/EAST.COM") }

我对 powershell 不熟，上面的代码执行完后好像会把选项改成 “仅使用 Kerberos”，还需要手动改回来，最终的设置应该如下：

![](https://images.seebug.org/content/images/2018/06/ff234210-7afb-404e-881d-8dd366b3bebe.jpg-w331s)

（考验你 Kerberos 基础的时刻到了，想一下为什么目标 SPN 要设置成 krbtgt/EAST.COM）

4.准备完成

下面来看一下效果，利用 impacket 的 getST.py 与 wmiexec.py：

1、`./getST.py` `-dc-ip` `192.168.99.150` `-spn krbtgt/EAST.COM` `-impersonate`
`Administrator east.com/ateam:1qazCDE#`

(注意，这条命令执行两次的话，先删除上一次执行生成的 Administrator.ccache 文件)

a. `getST.py` 先以 ateam 为账号 1qazCDE# 为密码向域控申请了一张 TGT，我们将这张 TGT 称为 ticket1 吧。这张
TGT 代表的是 ateam 这个账号的身份。

![](https://images.seebug.org/content/images/2018/06/8942379f-409b-40ba-a18c-6555e4f44963.jpg-w331s)

b. 然后利用这张 TGT 进行 S4U2self 请求，利用 S4U2self 以 Administrator 的名义向 TGS
申请了一张访问自身服务的票（虽然并没有任何服务以 ateam 这个账号启动，也许更准确地说应该是申请了一张访问 variant/golden 这个 SPN
的票，还记得前面我们在 ateam 这个账号上面注册了 variant/golden 这个 SPN 吧？） ，我们将这张票称为 ticket2 吧

![](https://images.seebug.org/content/images/2018/06/b1eadce5-cf57-4aff-968b-43a947894629.jpg-w331s)

c. 拿到了 ticket2 后，次向 KDC 发起 SU42Proxy 请求（会带上 ticket2，在下图的 addtitional-tickets
中），以 Administrator 的名义向 KDC 申请一张到 krbtgt/EAST.COM 的票，将这张票称为 ticket3 吧

![](https://images.seebug.org/content/images/2018/06/67bd640d-19cf-48ab-a820-1d2a40e284f4.jpg-w331s)

d. 最后，我们拿到了一张代表着 Administrator 身份的可以访问 krbtgt/EAST.COM 服务的票。 那这张 ticket3
到底是什么票？能做什么？这就是 Administrator 这个账号 TGT 啊！所谓的 TGT 跟其他的 Kerberos 票据没有任何区别。用来访问
TGS 服务或者说在这个例子里面 krbtgt/EAST.COM 这个服务的票就是 TGT。

e. 最终我们拿到的这个 TGT 会被保存到当前目录 Administrator.ccache 下。

export KRB5CCNAME=Administrator.ccache klist

![](https://images.seebug.org/content/images/2018/06/fcc29b9b-6c57-4d28-a1b4-9c41c8551504.jpg-w331s)

需要去看 SFU 的协议文档才能完全看明白这几步

所以实现的效果就是，我们通过 ateam 这个普通的域账号，通过利用 S4U 协议，拿回了 Adminstrator 这个账号（可以是域内任何账号）的一张
TGT。全程是不需要用到 krbtgt 这个账号的任何信息的。

#### 最终效果

用获取到的 Administrator 的 TGT 访问 2008-DM1 这台机器：

export KRB5CCNAME=Administrator.ccache  
./wmiexec.py -no-pass -k administrator@2008-dm1 -dc-ip 192.168.99.150

![](https://images.seebug.org/content/images/2018/06/d84b1d84-e9ee-46ca-b446-f9b832765926.jpg-w331s)

访问域控：

![](https://images.seebug.org/content/images/2018/06/a51e043f-203d-4f3b-be6d-db0499308d22.jpg-w331s)

需要在域里面做的所有操作都可以用 powershell 完成，不过我对 powershell 不熟，也没心情去现学了。

#### 总结

这种方法相对于传统的黄金票据动作稍微有点大。传统的黄金票据也没有太好的检查方案，而本文说到的这种说法好检查一些，只需要查一下域里面哪些账号开了
protocol transtition 权限，以及他们的 S4U2Proxy 的 SPN 列表就可以了。

#### 参考资料

  * <https://www.coresecurity.com/blog/kerberos-delegation-spns-and-more>
  * <https://labs.mwrinfosecurity.com/blog/trust-years-to-earn-seconds-to-break/>
  * <https://www.blackhat.com/docs/asia-17/materials/asia-17-Hart-Delegate-To-The-Top-Abusing-Kerberos-For-Arbitrary-Impersonations-And-RCE-wp.pdf>
  * <https://msdn.microsoft.com/en-us/library/cc246071.aspx>
  * <https://www.samba.org/~metze/caps/krb5/s4u2self-trusts/>
  * <https://journeyofthegeek.com/2016/11/03/deep-dive-into-resource-based-constrained-delegation-part-2/>
  * <https://techsupport.osisoft.com/Troubleshooting/KB/KB01222>
  * <https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc738207(v%3dws.10)>
  * <https://blog.kloud.com.au/2013/07/11/kerberos-constrained-delegation/>
  * <http://www.itprotoday.com/security/how-windows-server-2012-eases-pain-kerberos-constrained-delegation-part-1>
  * <https://support.citrix.com/content/dam/supportWS/kA460000000Cc8PCAS/KerberosSSO_NetScaler10.1_120.13.pdf>
  * <https://github.com/heimdal/heimdal/blob/master/lib/asn1/krb5.asn1>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/620/>

