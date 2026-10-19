## 0x01 邮件传输协议简介

### 1.SMTP(Simple Mail Transfer Protocol)

SMTP(Simple Mail Transfer
Protocol)即简单邮件传输协议，这个协议主要用来从邮件客户端发送邮件到邮件服务器，也被用来把邮件从一个邮件服务器转发到另一个邮件服务器(比如从QQ转发到163)。默认使用端口25，也可以使用465或587。我们可以通过简单的六个命令来发送一份邮件

![](https://image.3001.net/images/20210301/1614565648_603c5110dac0c5b87b818.png!small)

### 2.POP3(Post Office Protocol 3)

因为它的版本3被广泛使用，所以被称为POP3。主要用来从邮件服务器上取回邮件到客户端，拥有认证机制

其工作流程:

> 1.连接邮件服务器的110端口(如果是SSL或TLS连接的话，则是995端口)
>
> 2.取回用户邮件
>
> 3.删除服务器上的邮件
>
> 4.同服务器断开连接

虽然POP客户端可以通过配置使得在服务器上继续存储邮件，但通常是删除服务器上的邮件，这与在IMAP上通常是不删除是不一样的

### 3.IMAP(Internet Message Access Protocol)

它用来在一个邮件服务器上存储邮件，并且允许用户查看和操作(删除、回复等)这些邮件

其工作流程:

> 1.连接邮件服务器的143端口(SSL或TLS连接则是993端口)
>
> 2.取回用户邮件
>
> 3.保持这个连接直到邮件客户端被关闭，在连接的过程中会按照需要下载信息

### 4.work together

可以参考下面的图片

![](https://image.3001.net/images/20210301/1614565684_603c51349d584e91aae5b.png!small)

首先发送方发送的邮件会被发送到SMTP服务器(比如你是163的邮箱账号，会被发送到smtp.163.com所在的服务器，或者是自己搭建的SMTP服务器)，然后再被转发到接收方所在的SMTP服务器，这都是通过SMTP协议实现的，之后接收方再通过POP3或IMAP协议取回自己的邮件或直接查看服务器上的邮件。当然，这是简化后的，只涉及这三个协议，真正的过程要比这个复杂。

可以看出SMTP是必须的，因为它与其他两个协议的主要功能是不同的，至于POP3和IMAP则是可以二选一的

## 0x02 邮件伪造防护协议简介

### 1.SPF

SPF(Sender Policy Framework)，它是以IP地址认证电子邮件发件人身份的技术。邮件接收方会检查我们的Mail
From下的域名，并去检查该域名的spf记录，如果spf记录存在，就会把邮件发送者的ip与spf记录进行匹配，如果匹配成功就认为是正确的邮件，否则则认为该邮件是伪造的，将邮件按照规则进行处理

### 2.DKIM

DKIM(DomainKeys Identified
Mail)，该协议主要作用是校验邮件标头签名信息，防止邮件内容被篡改。邮件的发送者先将DKIM的公钥设置到dns上去，然后将邮件的签名插入邮件头中一起发送出去，邮件的接收者接受到该邮件后，根据DKIM签名上标注的域名查询其dns获取公钥，验证邮件签名的有效性

    
    
    v=1; a=rsa-sha256; c=relaxed/simple; d=test.com; h=subject:subject:from:from:content-transfer-encoding:content-type:content-type; s=dkim; t=1612344789; x=1614936790; bh=whCdi8wMe31tExV/kY1u1K6C1IjBREx7llkl8PePKUU=; b=38b67jyXwMi00rGK78y9QVL39g0RnITLz7ysuwbgv/3yjMM8eYA+EDRRFGJohssAfD4fVi4VrhDgP+Bmnze9wxqqqH0ClwV7fpvMMlHT4cVHMP0eCzvVtfswu3RBhoK3vS3z7iFQbG/bLa650xRy1PNP1GF+DR5f7E4AErAw1Mg=

a：签名算法  
c：用于对标头和正文的算法规范化，simple&relaxed  
d：是这一个域的签名。在DMARC检查签名中的域是否和发送者的域相匹配中用到  
q：定义用于检索DKIM公钥的查询方法。它不必存在，默认为“ dns / txt”  
s：在DNS中寻找RSA密钥的参数  
h：应该包含在签名中的邮件头字段列表  
bh：邮件正文的hash  
b：是签名本身的核心，包括’h’给出的字段，以及DKIM-Signature头本身(视b=为空)

### 3.DMARC

DMARC(Domain-based Message Authentication, Reporting &
Conformance)是txt记录中的一种，是一种基于现有的SPF和DKIM协议的可扩展电子邮件认证协议，其核心思想是邮件的发送方通过特定方式（DNS）公开表明自己会用到的发件服务器（SPF）、并对发出的邮件内容进行签名(DKIM)，而邮件的接收方则检查收到的邮件是否来自发送方授权过的服务器并核对签名是否有效。对于未通过前述检查的邮件，接收方则按照发送方指定的策略进行处理，如直接投入垃圾箱或拒收。从而有效识别并拦截欺诈邮件和钓鱼邮件，保障用户个人信息安全

## 0x03 伪造的方法总结

### 1.第三方STMP的服务器认证用户名与Mail From字段可以不同导致的攻击

这样攻击者可以假装这个域下的所有其他用户，伪造该域下用户可以直接无视所有验证协议

### 2.Mail From头和From头不一样

邮箱一般以显示给用户的是Data内的From头，有些邮箱通过直接设置From的办法来欺骗受害者，但是目前大部分邮箱如果Mail
From头和From不一样会显示转发如图所示

![](https://image.3001.net/images/20210301/1614565754_603c517a941ad2264bb23.png!small)

### 3.空Mail From头

有些STMP服务器遇到空Mail From头可以通过，理论上按照SPF协议，如果服务器遇到空Mail
From需要去验证HELO字段，但是由于对HELO字段的滥用，所以就很多服务器不根据HELO字段完成SPF验证，所以碰到空Mail
From头的判断结果就变成none

### 4.多个From头

多个From头正常的处理方式是会被退信的，但是有一部分邮箱是只取部分显示，比如只显示第一个或只显示最后一个

### 5.From头上写多个Email地址

因为一个邮件可能被多个人编辑，所以可以在From上设置多个地址，然后设置一个Sender来确定真正的发件人，作为攻击者可以设置From头为  
<admin@qq.com>,<test@attack.com>或者增加一些基于基本规则的变化如[admin@qq.com],<test@attack.com>

### 6.解析不一致产生的攻击

1.Mail From和From字段都是支持富文本的。比如<@a.com,
@b.com:admin@c.com>依然是合法的地址，其中@a.com和@b.com是路由部分，admin@c.com是真正的发送者的地址  
2.From字段是可以设置为地址列表的，且列表种的元素可以为空，如<a@a.com>, ,<b@b.com>  
3.圆括号作为注释可以插入在地址中  
例子：<admin(username)@a.com(domain)>  
4.可以用截断字符或者有意义的符号尝试截断地址

![](https://image.3001.net/images/20210301/1614565782_603c519673fff45d98dd2.jpg!small)

### 7.字段编码产生的攻击

邮件本体的内容是可以被编码的，语法如下  
=?charset?encoding?encoded-text?=  
charset字段为字符集，如gbk，utf-8  
encoding是编码方式，b代表base64，q代表Quoted-printable编码  
encoded-text就是被编码的主体了  
攻击者可以设置From字段类似From: =?utf-8?b?QWxpY2VAYS5jb20=?=,  
大多数电子邮件服务在验证DMARC协议不会去解码，所以在DMARC验证中就会得到结果None，有些Mua会把编码解码后显示出来，就造成了攻击  
这种技术可以和截断字符串来联系在一起，如:

<b64(admin@qq.com)b64(\uffff)@attack.com>  
就有可能DMARC验证的域是attack.com但是显示的是admin@qq.com

### 8.利用Sender头进行伪造

Sender字段定义为代发用户，不同的邮箱对Sender头的处理并不一样，有些会把Sender头作为代发，有些会直接显示出来，有时可以利用此来绕过代发显示

### 9.利用子域名未设置SPF

因为未设置SPF的话，SPF检测结果是none，是放行的，所以虽然qq.com上设置了spf，但是mail.qq.com上没有设置spf，我们就可以伪造mail.qq.com域下的任何用户

![](https://image.3001.net/images/20210301/1614565933_603c522d1cd14c0ff9a05.png!small)

### 10.利用未作验证的邮件转发服务

如果该服务器可以在不做验证的情况下任意把邮件转发到任意账户，如果该邮件转发服务器比较有名被大家信任，接收者的MTA就会接受这份邮件，且我们的目标邮箱的域名和转发服务器邮箱的域名一样我们就可以用这个方法来绕过SPF和DMARC，但在实际操作中还是会显示代发  
![](https://image.3001.net/images/20210301/1614565982_603c525e1abb1cac24705.jpg!small)

### 11.利用转发服务器来骗一个合法的DKIM签名

如果我们发送的邮件没有DKIM签名，转发服务器会给我们的邮件签名  
所以我们先把邮件发到转发服务器转发到另一个我们可以控制的邮箱，这样我们就收到了签名，然后我们再把这个签名附在邮件上发给被害者，我们的邮件就能拥有一个合法的DKIM签名

  
![](https://image.3001.net/images/20210301/1614565995_603c526b76e7174839252.jpg!small)

### 12.利用IDN域名

就是利用IDN域名，找出域名看起来比较像但实际上字母不一样的域名  
[punycode在线转换工具](http://tools.jb51.net/punycode/index.php)

比如ԛԛ.com实际上是xn—y7aa.com

### 13.利用不可见字符，截断字符影响渲染结果

一些不可见字符(U+0000-U+001F,U+FF00-U+FFFF)，语义字符(@,:,;,”)可能会导致渲染结果出现偏差  
文字中的例子一些邮箱会把admin@gm@ail.com渲染成admin@gmail.com

### 14.控制字符串的显示顺序来影响渲染结果

一些字符是控制字符串的显示顺序其中U+202E这个字符能让字符从右到作显示,而U+202D能让字符从左到右显示  
\u202emoc.qq@\u202dadmin会被显示成admin@qq.com

## 0x04 邮件伪造实战

伪造的目的是为了把我们的邮件送进收件箱，并且视觉上与一封真正的邮件没有区别。我在测试的时候主要针对的是国内的邮箱，利用自己搭建的邮件服务器，发现在没有设置dkim，甚至dkim验证结果为fail的情况下，大部分邮箱仍然没有把我的邮件送入垃圾箱，因为dkim是增加邮件的可信程度，既然邮件能被送进收件箱也就没有必要想方设法去绕过dkim验证了。在实际的伪造过程中我们面对的难题主要是如何绕过SPF，和邮箱对代发邮件的提示。在实战过程中我可以伪造的邮箱分为三类

> 1.没有显示代发的邮箱  
> 没有显示代发的邮箱伪造起来非常简单，我们只需要把From设置成我们需要伪造的邮箱即可
>
> 2.支持IDN域名，或者支持Unicode字符串显示的邮箱  
> 这种邮箱我们可以通过利用形似字，控制显示顺序，截断字符等让受害者在视觉上无法辨别真伪
>
> 3.利用邮件接受服务器对邮件头的解析错误来进行伪造  
>
> 这种情况就很多了，其中大部分都能用之前列举的方法2~8来解决，但是每个公司的邮件接受服务器的配置，后端处理方案都有所不同所以会有一些针对性的伪造方法，需要一点点的去试验  
> 比如针对腾讯邮箱的伪造方式，其中一种是利用字段编码编码很多unicode字符，会使腾讯邮箱无法找到真实的邮件地址，但这个方法在别的邮箱并不适用
>
> 4.当我们遇到的邮箱不属于以上三类无法直接伪造的时候，最方便的办法还是利用未设置的spf子域名，虽然欺骗的效果不如直接伪造的，但也有较强的欺骗力度

我们针对国内邮箱厂商进行测试，并写成利用插件集成到了内部钓鱼平台上。最终的邮件伪造效果：

 **QQ邮箱(两种绕过方法)**

![](https://image.3001.net/images/20210301/1614566245_603c5365e358bb85df154.png!small)

![](https://image.3001.net/images/20210301/1614566257_603c5371eecb4e57b8758.png!small)

 **163邮箱**

![](https://image.3001.net/images/20210301/1614566276_603c53849dfe09b309aa0.png!small)

 **126邮箱**

![](https://image.3001.net/images/20210301/1614566299_603c539b87a64b1eea517.png!small)

 **TOM邮箱**  
  
![](https://image.3001.net/images/20210301/1614566310_603c53a677258ca519513.png!small)

 **搜狐邮箱**

![](https://image.3001.net/images/20210301/1614566362_603c53da72f267b8071fc.png!small)

 **88完美邮箱**

![](https://image.3001.net/images/20210301/1614566374_603c53e6a1e30f355e5ba.png!small)

 **新浪邮箱**

![](https://image.3001.net/images/20210301/1614566385_603c53f112119e312b1bc.png!small)

## 0x05 参考文章

> 《Weak Links in Authentication Chains: A Large-scale Analysis of Email Sender
> Spoofing Attacks》
>
> [邮件伪造组合拳](https://www.anquanke.com/post/id/218889#h2-0)
>
> [钓鱼邮件的投递和伪造](https://xz.aliyun.com/t/6325/)

