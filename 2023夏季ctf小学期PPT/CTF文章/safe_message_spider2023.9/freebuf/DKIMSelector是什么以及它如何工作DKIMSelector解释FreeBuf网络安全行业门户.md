在这篇文章中我们将讨论什么是 DKIM selector (DKIM 选择子)，为什么需要它们，以及它们在 DKIM 验证中如何工作。

## DKIM selector 是什么？

DKIM selector，又名 DKIM 选择子或 DKIM
选择器，是一个被邮件发送服务器用来确定私有密钥来对邮件签名的字符串。在邮件接收服务器上，它被用来在 DNS 中获取公有密钥来验证邮件的完整性。

每创建一个私有/公有密钥对时，将会产生一个 { selector, 私有密钥, 公有密钥 } 元组，其中 selector 被用来获取私有密钥和公有密钥。

## 如何选择 DKIM selector？

当用户为邮件发送服务(例如 SendGrid)创建一个私有/公有密钥对时，需要指定一个 DKIM selector，该 DKIM selector
可以是任何字符串。

## 为什么需要多个 DKIM selectors？

基于以下的理由，需要有多个私有/公有密钥对：

> DKIM key rotation，下面将会解释；
>
> 在单一的域名上为多个邮件发送服务设置 DKIM；每个服务可以有自己单独的 selector，这样每个服务的签名/验证不会干扰其他服务。

每当一封邮件发送/验证的时候，只有一对密钥会被用到。这时候 DKIM selector 就会派上用场：该 DKIM selector
被签名服务器用来在密钥对中获取私有密钥，验证服务器则用同一个 DKIM selector 来获取公有密钥。

## DKIM selector 在 DKIM 验证中如何工作？

一旦签名服务器确定了 DKIM selector，该服务器就用它来找到对应的密钥，来计算签名。一旦签名计算完毕，该 DKIM selector
被插入到邮件头部的 `s=`标签中，然后发送该邮件。

例如，假定选择的 selector 是 `s1`，该标签就是 `s=s1`。再次提醒一下，该 selector 可以是任何字符串，像
`thisismyselector1234`，只要它指向一个有效的私有/公有密钥对就可以了。

这是一个实际的 DKIM 签名头域例子：

    
    
    DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed; d=dmarcly.com; h=content-transfer-encoding:content-type:from:mime-version:subject: x-feedback-id:to; s=s1; bh=jCC0oQBCKfJ10bCI3PCG52Zwowyeh1haGJPACkWN9F4=; b=GzLBVZ0M1hMt1Y7hVT+ajaNrswTv+/FFVMrcaixD70hpTJwAmNwZUKJIzLslSC+iWHby 9gm+yfx6Z1qnXIL6qgBPnlZD4zwyK4D3Umd1je82jniuD7RJWYDqJH0zL+EevCDdoVZGmT IlxzZB6v95bws6539z/5qee+Xmu5KYe4Y=

上述 DKIM 签名所用的 DKIM selector 是 `s=s1`。

当邮件抵达接收服务器时，服务器检查邮件头域来找到 `s=`标签。如果该标签存在，服务器从中抽取 selector，然后在 DNS 的以下位置寻找公有密钥：

    
    
    s1._domainkey.example.com

如果公有密钥被找到，服务器用它来检查邮件的完整性。如果检查通过，DKIM 验证成功，否则失败。

如果无法找到公有密钥，DKIM 验证失败。

## DKIM key rotation 是什么？

DKIM 已经证明是用来验证邮件完整性的有效手段。但是 DKIM 也有自身的弱点。如果保存 DKIM
的私有密钥的系统被入侵的话，安全性将大打折扣。因此，为了最小化被破解的风险，应该定期改变 DKIM 密钥对。这叫 DKIM key rotation
(DKIM 密钥轮换)。

每次密钥轮换的时候，一个新的 {selector, 私有密钥, 公有密钥} 元组将被产生。然后公有密钥将被发布在 DNS
中，你需要重新配置邮件发送服务器来使用新的私有密钥。完成以后，该服务器将会使用新的私有密钥来对所有即将被发送的邮件签名。

原来的密钥应当继续保存7天，然后就可以安全地移除。原因是在邮件发送以后和到达接受服务器之间可能会有延迟。如果在接受服务器上有临时错误的话，这样的延迟可能长达几天。为了让
DKIM 验证通过，接收服务器必须能够在 DNS 中找到对应的公有密钥。

只有当你运行自己的邮件发送服务器的时候，你才需要手工做 DKIM 密钥轮换。如果你使用类似 SendGrid, Office 365, 或者 GSuite
等服务来发送邮件的话，你无需做任何事 -- DKIM 密钥轮换是自动完成的。

## DKIM selector VS DKIM 记录

如果你在类似 SendGrid 的邮件发送服务中设置 DKIM 的话，它将会为你创建 CNAME 类型的 DKIM 记录。下面是一条 CNAME 类型的
DKIM 记录：

    
    
    s1.domainkey.u5022280.wl431.sendgrid.net

你需要在 DNS 中发布类似的记录，使得接收服务器可以访问。留意上面记录中的 `s1`部分：这是 DKIM
selector，被接收服务器用来获取公有密钥，然后将其用来验证 DKIM 签名。

#### 如何用 DKIM selector 来检查 DKIM 记录

如果你需要检查某个域名上的 selector 是否有 DKIM 记录，可以用这个 [免费 DKIM
记录检查器](https://dmarcly.com/tools/dkim-record-checker).

输入需要检查的域名和 selector 即可。

参阅 DKIM RFC 来获取更多信息：[DKIM RFC6376](https://tools.ietf.org/html/rfc6376).

