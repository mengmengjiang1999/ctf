接上文

##  ** **SPF绕过****

简单了解SPF规则之后，我们总结一下，如果你模拟一个MTA向对端MTA发送邮件是行不通的，因为MTA后端会检查你的ip地址是否通过spf规则。前文向gmail发出的1634.com后缀的钓鱼邮件是因为1634.com这个域名没有mx和spf配置：

> p1pp0@h33l0:~$ nslookup -type=txt 1634.com
>
> Server: 223.5.5.5
>
> Address: 223.5.5.5#53
>
>  
>
>
> Non-authoritative answer:
>
> *** Can't find 1634.com: No answer
>
> p1pp0@h33l0:~$ nslookup -type=mx 1634.com
>
> Server: 223.5.5.5
>
> Address: 223.5.5.5#53
>
>  
>
>
> Non-authoritative answer:
>
> *** Can't find 1634.com: No answer

所以gmail无处校验spf规则，那对于没有spf记录配置的发件MTA，各大运营商的规则都是接受的，而企业自建的服务器要依靠管理员的配置，但是也基本都是接受的。

那么有防守就有攻，如何绕过spf规则呢？

###  ** **1.**** ** **getshell一台在合法MTA列表里的机器****

由于合法的MTA列表可以通过简单的DNS查询获取到，最直接的思路就是打下来对面的邮件服务器，这主要对于使用多台邮件服务器、或者出口不固定的情况，这时候管理员为了方便都是配置为192.168.1.0/24的形式。

不过成本有点高，而且没有授权。

###  ** **2**** ** **找一个与其相似但没有配置spf的域名****

可以使用前文提供的工具，crazy出一个相似的域名，然后用此域名发送给受害者,这里用weib0.com仿冒weibo.com：

> root@h33l0:/home/p1pp0# nslookup -type=txt weib0.com
>
> Server: 202.96.209.133
>
> Address: 202.96.209.133#53
>
>  
>
>
> Non-authoritative answer:
>
> *** Can't find weib0.com: No answer
>
>  
>
>
> Authoritative answers can be found from:
>
> weib0.com

使用swaks模拟一下：

> proxychains swaks --to XXXX@gmail.com --from
> _[admin@weib0.com](mailto:admin@weib0.com)_

![1612432329_601bc3c9eb7bf6826eede.png!small?1612432330190](https://image.3001.net/images/20210204/1612432329_601bc3c9eb7bf6826eede.png!small?1612432330190)

###  ** **3.**** ** **spf设置软拒绝****

前面说到spf可以配置四种规则：

> "+" Pass（通过）
>
> "-" Fail（拒绝）
>
> "~" Soft Fail（软拒绝）
>
> "?" Neutral（中立）

当要仿冒的MTA spf中配置了软拒绝，这时候是否接受就依照收件MTA的配置了，演示一下：

![1612432502_601bc476acabb4e6606fd.png!small?1612432503090](https://image.3001.net/images/20210204/1612432502_601bc476acabb4e6606fd.png!small?1612432503090)

这里找了一个前客户，打码一下，配置了软拒绝，那么：

> proxychains swaks --to XXXX@gmail.com --from
> [_admin@xxxgrouptest.com_](mailto:admin@xxxgrouptest.com)

![1612432519_601bc4878b213f2cb8a79.png!small?1612432519830](https://image.3001.net/images/20210204/1612432519_601bc4878b213f2cb8a79.png!small?1612432519830)

这里这一封邮件没有扔进垃圾箱，也成功接收到了。其他邮箱提供商可自行测试效果。

具体上可以urlcrazy 一下要仿冒的域名，如果有~all配置的域名想要使用的话，可以不妨一试。

当然如果你的目标的MTA就是软拒接的话，也可以尝试直接模拟对端MTA，企业邮箱配置的都是-all，这招只有在目标自建了邮件服务器才有可能出现且极少成功。

###  ** **4.**** ** **SPF实现不当****

猜想一下收件MTA检测SPF的逻辑：

> 1.取域名。
>
> 2.取对应域名的SPF记录。
>
> 3.比对连接过来的ip是否通过SPF。

显然，ip我们不能伪造，要伪造域名的SPF记录我们也不能控制，好消息是我们可以控制所有的域名，还记得我们开篇的MTA交互流程吗？有域名的地方有这三个：

> 1.与接收者MTA打招呼时的EHLO命令
>
> 2.指定发送人的MAIL FROM命令
>
> 3.正文里的From头部

这三个有邮箱域名的地方，我想先讨论MAIL FROM和正文的FROM部分，重贴一小段MTA之间交互过程：

> -> MAIL FROM:[ _admin@noahgrouptest.com_](mailto:admin@noahgrouptest.com)
>
> <\- 250 Ok
>
> -> RCPT TO:<xxxx@cagetest.com>
>
> <\- 250 Ok
>
> -> DATA--------------------正文开始------------------------------>
> <\- 354 End data with <CR><LF>.<CR><LF>
>
> -> Date: Mon, 25 Jan 2021 15:18:32 +0800
>
> -> To: xxxx@cagetest.com
>
> -> From: admin@xxxxgrouptest.com
>
> -> Subject: test Mon, 25 Jan 2021 15:18:32 +0800
>
> -> Message-Id: <20210125151832.170069@cagetest-phishingemail1>
>
> -> X-Mailer: swaks v20181104.0 jetmore.org/john/code/swaks/
>
> -> from: admin@qq.com
>
> ->
>
> -> This is a test mailing
>
> ->
>
> ->
>
> -> .-----------------------正文结束-------------------------------
这里DATA域包含了正文部分，也就是在客户端看到的内容，所以这个From头是会展示给用户看的（报文地址）。而MAIL-FROM是MTA之间的交互，是在投递的时候使用的，并不会被客户看到（信封地址），所以，存在一种可能：

如果收件MTA中取信封地址，不检查报文地址且不检查两个地址是否一致，我们就可以在报文地址上使用一个可以通过SPF的记录，然后定义一个想要的报文地址，就能实现绕过。

具体实现上可以自建一个域名，自行配置一个SPF记录:

> v = spf1 ip4:192.168.1.1 -all

如果没有域名的话，可以自行从[ _FDNS数据集_](https://opendata.rapid7.com/sonar.fdns_v2/)里找：

![1612432615_601bc4e7e20ab6b327c03.png!small?1612432616232](https://image.3001.net/images/20210204/1612432615_601bc4e7e20ab6b327c03.png!small?1612432616232)

这个解压出来筛选spf记录：

![1612432624_601bc4f011b1a1f1aa6b6.png!small?1612432624526](https://image.3001.net/images/20210204/1612432624_601bc4f011b1a1f1aa6b6.png!small?1612432624526)

从里面找到合适的SPF记录也可以，另外，这个数据集很有趣，对平时渗透也可以找到一些子域名的查找工作，可以下载回来扔进ES。

这一招也只对自建的mail系统有可能有用，测试下来各大云邮件提供商都有完备的SPF验证。

再来说一下被忘记的EHLO头，这里无关紧要，不想看的可以跳到下一章。

首先和MAIL-FROM一样，EHLO也不会被展示给收件人，我们试一下伪造ehlo：

> swaks --to xxx@gmail.com --from admin@1634.com --ehlo admin.com

这里admin.com的spf记录是全部拒绝的：

![1612432652_601bc50cef2cabdd7240c.png!small?1612432653405](https://image.3001.net/images/20210204/1612432652_601bc50cef2cabdd7240c.png!small?1612432653405)![1612432659_601bc513ea893a78ae5bf.png!small?1612432660573](https://image.3001.net/images/20210204/1612432659_601bc513ea893a78ae5bf.png!small?1612432660573)成功发出，也成功收到了：

![1612432681_601bc529a3f32fb2019ab.png!small?1612432681977](https://image.3001.net/images/20210204/1612432681_601bc529a3f32fb2019ab.png!small?1612432681977)

后面测试了outlook邮箱、腾讯企业邮、sina邮箱也都是成功的。不过有的被识别为垃圾邮件了。不再一一演示。

而exchange的使用发件人信誉，会将ehlo域作为一个判断是否为垃圾邮件的指标，也并不会直接拿去检查SPF。不过有一些邮件网关是可配置检查EHLO域的：

>  ** **Helo/ehlo 分析**** ： HELO 和 ehlo SMTP 命令用于向接收 smtp 服务器提供发送 smtp 服务器的域名（如
> Contoso.com）或 IP 地址。 恶意用户（或垃圾邮件制造者）经常通过不同方式伪造 HELO/EHLO 语句。 例如，键入与发起连接的 IP
> 地址不匹配的 IP 地址。 垃圾邮件制造者还将已知在接收服务器本地支持的域放入 HELO 语句，尝试像域处于组织中一样显示。
> 其他情况下，垃圾邮件制造者更改在 HELO 语句中传递的域。 合法用户通常可能会在 HELO 语句中使用不同但是相对恒定的一组域。
>
> 因此，按发件人分析 HELO/EHLO 语句可能表明发件人很可能是垃圾邮件制造者。例如，在特定时段内提供许多不同的唯一 HELO/EHLO
> 语句的发件人更可能是垃圾邮件制造者。如果发件人在 HELO 语句中提供的 IP 地址一直与连接筛选代理确定的来源 IP
> 地址不匹配，则也很可能是垃圾邮件制造者。如果远程发件人在 HELO 语句中提供的本地域名与 Exchange
> 服务器在同一组织中，则也很可能是垃圾邮件制造者。

[ _https://docs.microsoft.com/zh-cn/exchange/antispam-and-antimalware/antispam-protection/sender-reputation?view=exchserver-2019_](https://docs.microsoft.com/zh-cn/exchange/antispam-and-antimalware/antispam-protection/sender-reputation?view=exchserver-2019)

事实上，翻阅RFC的文档，EHLO后应该接FQDN，即全限定域名：同时带有主机名和域名的名称。，但是测试下来，厂商几乎不检测这里。

###  ** **5.**** ** **祈祷对方不校验SPF记录或者配置错了****

同样，托管在云上的都是校验的，自建的依靠配置，不过实测下来exchange2016默认是不开启的，需要[
_手动配置发件人信誉_](https://docs.microsoft.com/zh-cn/exchange/antispam-and-antimalware/antispam-protection/antispam-on-mailbox-servers?view=exchserver-2019)。碰到了这种这情况建议买DLT。

###  ** **6.**** ** **其他****

其他师傅还有一些技巧，利用条件都比较苛刻，想看的可以点击[
_这里_](https://mp.weixin.qq.com/s/dqntjRLgcOD3D2bi1oDFAw)。

##  ** **发件人前端伪造****

综上所述，SPF规则被绕过的概率几乎没有，只要上云就GG。既然不能伪造，我们退一步，追求客户端展示上的相似。这是个古老的技术，客户端有以下几种:

> 1.web网页端
>
> 2.手机app
>
> 3.foxmail
>
> 3.小程序和其他

需要说明的是由于每种客户端的显示方式都不相同，所以一些技巧都只对个别的客户端有效。

我们先从基本的swaks开始：

> swaks --to xxx@cagetest.com --from XXX@163.com --body "hello,world"
>
> -au au -ap ap --server smtp.163.com

这里解释一下-au -ap,
这是swaks的另一种用法，它使用用户名（au）授权码（ap）模拟客户端登录到自己的MTA，然后发送邮件，起一个邮件代理的功能，这时候你用的是一个合法的用户，当然是可以成功发送的。

后面的都会有-au -ap –server，后面就省略了。

![1612432807_601bc5a7876cd3d1fb0d1.png!small?1612432808036](https://image.3001.net/images/20210204/1612432807_601bc5a7876cd3d1fb0d1.png!small?1612432808036)

这里我们用--from指定了收件人，1.5中提到，我们有两个收件人地址，一个是信封地址（MAIL-FROM），一个是报文地址（from），这里swaks的
--from是指定了信封地址，我们可以通过—h-from指定报文地址。

> \--from ==》信封地址
>
> \--h-from ==》报文地址

如果不指定--h-from，所有的smtp服务器处理都是继承—from的值：

![1612432826_601bc5ba1aa4f0da4ced3.png!small?1612432828209](https://image.3001.net/images/20210204/1612432826_601bc5ba1aa4f0da4ced3.png!small?1612432828209)

那理所当然的我们尝试直接指--h-from为我们想要的邮箱：

> swaks --to xxxx@cagetest.com --from jianxxx@163.com --h-From:
> 'admin@163.com' --ehlo gmail.com --body hello --server smtp.163.com -p 25

![1612432841_601bc5c96a8c09c77b072.png!small?1612432841827](https://image.3001.net/images/20210204/1612432841_601bc5c96a8c09c77b072.png!small?1612432841827)

这里变成了admin，但是丢失163.com，点进去的话：

![1612432852_601bc5d4793261ece17a3.png!small?1612432852989](https://image.3001.net/images/20210204/1612432852_601bc5d4793261ece17a3.png!small?1612432852989)

显示了代发，事实上使用一个左尖括号<加任意汉字就能去掉代发的标识：

> swaks --to xxx@cagetest.com --from jianghpxxx@163.com --h-From:
> '管理员<任意汉字<admin@163.com>管理员' --ehlo gmail.com --body hello

 **
**![1612432866_601bc5e2595908a27f2e3.png!small?1612432866676](https://image.3001.net/images/20210204/1612432866_601bc5e2595908a27f2e3.png!small?1612432866676)****

web端上也不显示，不过地址变成了奇怪的样子。

![1612432885_601bc5f536018504f6d8c.png!small?1612432885553](https://image.3001.net/images/20210204/1612432885_601bc5f536018504f6d8c.png!small?1612432885553)

其他客户端对于代发的显示不一：

![1612432892_601bc5fc90b28847ff29e.png!small?1612432893029](https://image.3001.net/images/20210204/1612432892_601bc5fc90b28847ff29e.png!small?1612432893029)

查看原始邮件的基本信息也是admin：

![1612432900_601bc604e14db4b9ae157.png!small?1612432901326](https://image.3001.net/images/20210204/1612432900_601bc604e14db4b9ae157.png!small?1612432901326)

在原文中才看得出来：

![1612432909_601bc60da8f06e986beb2.png!small?1612432910438](https://image.3001.net/images/20210204/1612432909_601bc60da8f06e986beb2.png!small?1612432910438)

outlook.com也不显示代发：

![1612432917_601bc6154da624cb1f061.png!small?1612432917682](https://image.3001.net/images/20210204/1612432917_601bc6154da624cb1f061.png!small?1612432917682)

新浪显示代发：

![1612432925_601bc61d23d084d3ed44b.png!small?1612432925492](https://image.3001.net/images/20210204/1612432925_601bc61d23d084d3ed44b.png!small?1612432925492)

foxmail上：

12月10日最新的7.2.20版本，changlog说加入了代发的显示，其实老版本也是显示代发的：

![1612432932_601bc624efb95780b9352.png!small?1612432933382](https://image.3001.net/images/20210204/1612432932_601bc624efb95780b9352.png!small?1612432933382)

不过我们可以用MIME的方式绕过它：

> import smtplib  
> from email import encoders  
> from email.mime.text import MIMEText  
> from email.mime.base import MIMEBase  
> from email.mime.multipart import MIMEMultipart  
> sender = 'sender@sina.com'  
> username = 'sender'  
> password = 'password'  
> smtp = smtplib.SMTP()  
> smtp.connect('smtp.sina.com',25)  
> smtp.login(username, password)  
> receiver = ['recevier@cagetest.com']  
> msg = MIMEMultipart()  
> msg['From'] = "admin@cagetest.com;<real_sender@sina.com>"  
> msg_content = u"你好，cagetest!"  
> msg.attach(MIMEText(msg_content, 'plain', 'utf-8'))  
> print(msg.as_string())  
> smtp.sendmail(sender, receiver, msg.as_string())  
> smtp.quit()

可以达到完全看不出来的效果哦：

![1612433016_601bc678b7e8c65fd1f96.png!small?1612433017142](https://image.3001.net/images/20210204/1612433016_601bc678b7e8c65fd1f96.png!small?1612433017142)

更新到最新版本就不行了，腾讯企业邮会自动加载msg['From']中的红色部分的头像，还是有代发：

![1612433027_601bc6835aac05263da1b.png!small?1612433027797](https://image.3001.net/images/20210204/1612433027_601bc6835aac05263da1b.png!small?1612433027797)

这里尝试把前面去代发的payload同时拿来用就不行了。

> smtplib.SMTPDataError: (553, b'Envolope sender mismatch with header from..')

也可以这样夹带一个邮件地址，企业邮会去掉一对尖括号,并不是递归的，所以用两对尖括号,使用两对尖括号的好处是其中的邮箱地址不会被检测：

> swaks –to xxxxx@cagetest.com --from real_addr@163.com --h-From:
> '管理员<<admin@cagetest.com>><real_addr@163.com>' --ehlo gmail.com --body hello

![1612433077_601bc6b5b75aa09d7ee09.png!small?1612433078071](https://image.3001.net/images/20210204/1612433077_601bc6b5b75aa09d7ee09.png!small?1612433078071)

不过在点开详情和在web端依旧露馅了：

![1612433086_601bc6be429b9ab9bc70d.png!small?1612433086602](https://image.3001.net/images/20210204/1612433086_601bc6be429b9ab9bc70d.png!small?1612433086602)

这时候可以注册一个域名，比如cagetast.com, cagetest.cn, cagetest.com.cn，效果就可以达到（图是P的）：

![1612433097_601bc6c97e7b1464f2dbc.png!small?1612433097943](https://image.3001.net/images/20210204/1612433097_601bc6c97e7b1464f2dbc.png!small?1612433097943)

其他的邮箱或多或少都有这类问题，可以自行研究如何在前端显示的比较像，但是很难找到在各种客户端都很像的伪造办法。

##  ** **让邮件进入收件箱****

当检查过SPF后，这时候MTA会首先判断你的IP，一般发的过快会被MTA暂时拉进黑名单，经常发垃圾邮件的ip会被永久拉黑，像这样：

> <** 554 Rejected due to the sending MTA's poor reputation. Please refer
> [_http://mail.sina.com.cn/help2/rwmail.html_](http://mail.sina.com.cn/help2/rwmail.html)

不过个别MTA不会告诉你为啥封你，可以去[
_http://multirbl.valli.org/_](http://multirbl.valli.org/)查询一下ip有没有被封。

![1612433123_601bc6e3b1af3bd7553b6.png!small?1612433124360](https://image.3001.net/images/20210204/1612433123_601bc6e3b1af3bd7553b6.png!small?1612433124360)

经过检测后，判断邮件内容、标题。加一些其他元信息，最终判断是否为垃圾邮件，从而决定这封邮件是进入垃圾箱或收件箱，甚至直接不发送到客户端。

这里实测使用自建邮箱基本没有问题，有钱可以给SSL上一个贵的证书，越贵信誉度越高，也可以使用一些信誉度很高的邮件服务商mailgun代发也不会进入垃圾箱，不过mailgun收费了。[
_https://www.aliyun.com/product/directmail_](https://www.aliyun.com/product/directmail)aliyun这个，一天200封。

后面会说内容的部分，内容伪装得当也很容易进入收件箱。

### 后续内容敬请期待......

![](https://image.3001.net/images/20210220/1613791610_6030817acda840cf49676.jpg!small)

