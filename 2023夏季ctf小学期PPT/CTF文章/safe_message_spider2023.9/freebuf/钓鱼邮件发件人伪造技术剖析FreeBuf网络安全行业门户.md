## **简介**

攻击者为了让恶意邮件能达到攻击目的，会精心设计邮件的标题、内容、图片，而针对性更强的恶意邮件还会对邮件发件人地址进行伪造，比如：admin@qq.xx.com、admin@qq-mail.com,这种发信人地址显然只能骗过少部分人。

但是如果伪造的发件人地址和官方完全一致呢？事实上，电子邮件是不安全的，恶意邮件完全有可能伪造成任何发信地址。

 **本文将会分析发件人地址是如何被伪造的，以及现有的防御策略又是如何被绕过的。**

##  **01** 伪造原理浅析

邮件头：

    
    
    HELO helo.sender.com   
    Mail From: <s@mfrom.sender.com>   
    From: Secure Bank <noreply@bank.com>   
    Sender: <admin@bank.com>   
    Received：from ...

HELO 表示谁发送了邮件（一般不显示）

Mail From 表示谁发送了邮件（一般不显示），未指定情况下会使用From字段内容代替

From 表示谁写的邮件，邮件客户端显示为发件人地址

Sender 定义为代发用户，不同的邮箱对Sender头的处理并不一样，有些会把Sender头作为代发，有些会直接显示出来，有时可以利用此来绕过代发显示

Received 表示路由信息，记录了邮件传递过程

通过邮件头可以发现，我们只要搭建一个邮件发送服务器，然后将from字段和Mail
From字段改为我们想要伪造的任意邮件地址就可以了。拿现实生活打比方，就是自己开了一家不正规邮局，from字段就是发件人姓名，修改from字段就是修改了邮件发件人姓名，mail
from字段类似邮局名称，修改mail from字段就是让邮件看起来正规。

事情当然不可能这么简单╮(╯▽╰)╭，于是为了防止伪造邮件满天飞，出现了检测伪造邮件的spf/dkim/dmarc记录。

##  **02** 防御机制

###  **spf/dkim/dmarc记录**

 **spf：**

检查HELO、MAIL FROM的域名的spf ip记录，是否和发件服务器ip匹配

 **dkim：**

请求dkim域名下的公钥，通过该公钥验证dkim签名

 **dmarc：**

基于spf和dkim、不符合时怎么做，对应spf和dkim

检查是否spf和dmarc是否通过

检查from字段一致性，包括和spf域名一致性、和dkim域名一致性

###  **配置举例**

dkim记录：

    
    
    公钥：  
    k=rsa; p=MIGf...AQAB  
    通过查询“选择器参数.\_domainkey.test.com”的txt记录获得  
    签名：  
    v=1; a=rsa-sha256; c=relaxed/simple; d=test.com; h=subject:subject:from:from:content-transfer-encoding:content-type:content-type; s=dkim; t=1612344789; x=1614936790; bh=whCdi8wMe31tExV/kY1u1K6C1IjBREx7llkl8PePKUU=; b=38b67jyXwMi00rGK78y9QVL39g0RnITLz7ysuwbgv/3yjMM8eYA+EDRRFGJohssAfD4fVi4VrhDgP+Bmnze9wxqqqH0ClwV7fpvMMlHT4cVHMP0eCzvVtfswu3RBhoK3vS3z7iFQbG/bLa650xRy1PNP1GF+DR5f7E4AErAw1Mg=  
    d：dkim签名对应的域名  
    s：选择器参数，公钥dns查询时使用，例子：dkim.\_domainkey.test.com  
    bh：邮件正文的hash

spf记录：

    
    
    "v=spf1 ip4:192.168.0.1/16 -all" //表示spf只接受192.168.0.1/16

dmarc记录：

    
    
    v=DMARC1; p=reject; rua=mailto:634990a7@mxtoolbox.dmarc-report.com; ruf=mailto:634990a7@forensics.dmarc-report.com; fo=1; pct=100

举个例子简单说明下这几种记录的作用：

比如你自己搭建了一个邮件发送服务器，域名是hack.com，然后将邮件from字段和Mail
From字段改为bank.com，想达到伪造邮件发件人的效果，但是spf记录会检测出你的发信ip和spf记录中的白名单ip不符，于是你伪造的邮件就被打上了spf不通过的标签，同样当dkim检测请求dkim域名下的公钥，通过该公钥验证dkim签名也会失败，于是又被搭上了dkim
不通过的标签。

这时，我们为了避免spf、dkim记录不通过，不修改mail
from字段、使用hack.com的dkim签名，但是dmarc会检测from字段和spf域名一致性、和dkim域名一致性，于是邮件会被打上dmarc不通过的标签。

##  **03** 伪造方法论

1\. 利用不存在的子域，下面的例子在检查MAIL
FROM时，notexist.bank.com未设置spf，所以spf检测为none，spf检查helo通过，最终spf 通过，dmarc检查MAIL
FROM字段和From字段的域是否符合，主域相同所以dmarc通过

    
    
    HELO attack.com  
    MAIL FROM: <any@notexist.bank.com>  
    From: <sec@bank.com>  
    To: <target@target.com>

2\. 利用特殊字符截断，dkim使用‘attack.com.\x00.any._domainkey.bank.com’请求公钥，dns
把\x00视为截断，所以最终将在attack.com请求公钥，导致dkim检测通过

    
    
    HELO attack.com  
    MAIL FROM: <any@attack.com>  
    DKIM-Signature: ...;d=bank.com;s=attack.com.\x00.any;...  
    From: <sec@bank.com>  
    To: <victim@victim.com>

3\. 利用多个From字段，下面类似的多个from字段，会导致有些接收方会显示第二个From字段为发件人

    
    
    exmaple1  
    From: <any@attack.com>  
    From: <admin@bank.com>  
    To: <victim@victim.com>  
      
    exmaple2  
    From\r\n: <any@attack.com>  
    From: <admin@bank.com>  
    To: <victim@victim.com>  
      
    exmaple3  
    _From: <any@attack.com>  
    From : <admin@bank.com>  
    To: <victim@victim.com>  
      
    exmaple4  
    From_: <any@attack.com>  
    From : <admin@bank.com>  
    To: <victim@victim.com>

4\. 利用解析错误，当From无法找到时会显示Sender为发件人

    
    
    From  
    : <any@attack.com>  
    Sender: <admin@bank.com>  
    To: <victim@victim.com>

5\. 利用From字段的复杂语法

如：

    
    
    From: zhang(b@b.com) san<@c.com, @d.com:a@a.com (e@e.com) > (f@f.com)   
    From: zhang(b@b.com) san<@c.com, @d.com:a@a.com (e@e.com) > (f@f.com)  
    注释：b@b.com e@e.com f@f.com  
    路由：@c.com, @d.com  
    发件人地址：a@a.com

From字段语法特性利用例子如下：

    
    
    //多个email地址  
    From: <any@attack.com>,<admin@bank.com>  
    //利用From语法  
    From: <any@attack.com,@any.com:admin@bank.com>  
    //利用字段编码  
    From: bs64(<any@bank.com>),<any@attack.com>  
    //利用反斜杠  
    From: <admin@bank.com>\,<any@attack.com>  
    //利用有无尖括号  
    From: admin@bank.com,<any@attack.com>  
    From: <any@attack.com>admin@bank.com

6\. 利用RLO字符

U+202E这个字符能让字符从右到左显示,而U+202D能让字符从左到右显示，如：\u202emoc.qq@\u202dadmin会被显示成admin@qq.com

7\. 利用IDN域名

注册域名看起来比较像但实际上字母不一样的idn域名，如看起来和qq.com一样的ԛԛ.com

##  **04** 实战思考

下面是我在实际测试过程中的一些发现：

国内主流邮箱，在dkim、dmarc验证不通过的情况下邮件还是能够进发件箱，主要是由于这两种记录主要在于提高邮件可信度，所以发件人伪造主要是如何绕过spf记录

利用邮件头解析错误来进行伪造需要对目标邮件接收服务器进行针对性测试，每个邮件接收服务器的解析策略都有所差异

如果目标子域名没有设置spf记录，可以选择伪造成该子域名

有些目标邮件接受服务器在from字段和mail from字段不一致的时候不会显示代发，这时只需要修改from字段即可完成伪造

某些邮件发送中转服务商对发件人校验不严格，可以利用他们的高信誉邮件发送服务伪造任意发信人，不过无法修改mail from字段，无法避免代发显示

##  **05** 总结

本文介绍了邮件发件人地址是如何被伪造的，以及针对发件人地址伪造技术进行了较为详细的分析。在实战攻防中，结合邮件话术伪造的发件人地址，往往能骗过绝大多数人的眼睛，让恶意邮件达到意想不到的效果。

## 参考

> [https://www.jianjunchen.com/p/composition-> kills.USESEC20.pdf﻿](https://www.jianjunchen.com/p/composition-> kills.USESEC20.pdf)

