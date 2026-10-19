## 1\. 事件

早上，正在处理日常工作，收到销售的电话，说一客户昨天晚上邮件服务器被黑客入侵，发送了一些诈骗邮件。直接和用户沟通，相关信息如下所示：

![](https://image.3001.net/images/20201127/1606475216_5fc0ddd023f92e75dfaf8.jpg!small)

![](https://image.3001.net/images/20201127/1606475238_5fc0dde6460bfc25d82c6.jpg!small)

## 2\. 分析

### 2.1 邮件分析

看到里面的“点击备案”，很常规的钓鱼链接，直接附件另存以后，使用chrome打开，相关信息如下所示：

![](https://image.3001.net/images/20201127/1606475258_5fc0ddfaa8eedb43ed836.jpg!small)

打开这个链接看一下，很明确的钓鱼URL，输入以后就会被记录账号和密码。

![](https://image.3001.net/images/20201127/1606475278_5fc0de0e3d61d0033bdf4.jpg!small)

### 2.2 发件人分析

刚看到这个情况，第一眼感觉就是伪造发件人。前期这一块分析研究了较多，顺手来测试一下， 先查一个mx记录，通过nslookup –type=mx
xxx.com查到其mx记录为mail.xx.com

![](https://image.3001.net/images/20201127/1606475296_5fc0de20af76cdb19cef4.jpg!small)

伪造个发件人test@XXX.com，返回“250 2.1.0 Sender OK”果然验证了我的推测，可以伪造发件人。

![](https://image.3001.net/images/20201127/1606475310_5fc0de2e795e16b3f9902.jpg!small)

### 2.3 验证

直接上工具,https://github.com/Macr0phag3/email_hack上下载相应的工具，kali里面内置的swaks也可以进行邮件钓鱼。分分钟发了封邮件，

![](https://image.3001.net/images/20201127/1606475326_5fc0de3e9738dc4c28732.jpg!small)

同时，用户也收到了我伪造发件人发送的测试邮件。至此，这个事件已经明白了，用户收到的他们内部人员发的钓鱼邮件应该是黑客伪造发件人发送的钓鱼邮件。

![](https://image.3001.net/images/20201127/1606475348_5fc0de542c89fd302bcf0.jpg!small)

![](https://image.3001.net/images/20201127/1606475368_5fc0de683e4a7d7848cdf.jpg!small)

### 2.4 加固

伪造发件人，目前使用较多的方式就是开启SPF，用户使用的是exchange，通过微软官方找了一下，参考微软官方的关于exchange中反垃圾邮件的建议如下，链接如下：

<https://docs.microsoft.com/zh-cn/exchange/antispam-and-antimalware/antispam-protection/antispam-protection?view=exchserver-2019>

![](https://image.3001.net/images/20201127/1606475389_5fc0de7dcb71e78f84d11.jpg!small)

## 3\. 钓鱼邮件技术介绍

你以为到这里就结束了？天真！里面虽然介绍了相关的技术，但是没有详细介绍，网上找了一些，也有很多的介绍，个人也做了一些收集和分析，个人分析研究以后主流的技术总结了一下。

### 3.1 SMTP

钓鱼邮件里面很多重要的一项技术是伪造发件人，关于SMTP协议，网上找了一张图。

![](https://image.3001.net/images/20201127/1606475416_5fc0de9831d1c44bdb6bb.jpg!small)

关于SMTP协议的过程大家可以参考下面链接学习，协议是后期代码实现的关键，建议想了解SMTP原理的学习一下。

https://blog.csdn.net/sinat_36219858/article/details/71069515

里面有很重要的一点，就是sender-smtp，发件人。如果我伪造如admin@qq.com发送一封邮件，发件人是admin@qq.com，对方收到以后怎么判断我这个发件人是不是真实的呢？大家可以思考一下。

### 3.2 DNS 类型之SPF

上面一个问题想必聪明的你一定想到答辩了,SPF。

SPF 是为了防范垃圾邮件而提出来的一种 DNS 记录类型，它是一种 TXT 类型的记录，它用于登记某个域名拥有的用来外发邮件的所有 IP
地址。通过nslookup –q=txt xxx.com来查询相关的SPF记录。下面是查询QQ的DNS中的txt记录，也就是其邮件服务器的IP地址。

![](https://image.3001.net/images/20201127/1606475437_5fc0dead41baf9f17f769.jpg!small)

上面通过nslookup –q=txt
qq.com找到了QQ的邮箱服务器的IP地址，这样收件人收到一封来自qq的邮件以后，若开启了SPF校验，它会校验发件人的IP地址是不是在上面的IP地址范围内，如果在的话就认为是真实的发件人；否则就认为是伪造发件人。

这里面，我们演示一下SPF校验失败的案例，我们伪造admin@qq.com给163发送一封邮件，可以看到返回的是550 MI:SPF

![](https://image.3001.net/images/20201127/1606475452_5fc0debc759c7a7206501.jpg!small)

关于 550 MI:SPF网上找了一个，相关的原因如下“发信IP未被发送域的SPF许可”

![](https://image.3001.net/images/20201127/1606475466_5fc0decae38bb4fc78a09.jpg!small)

上面可以看到，只要对方去校验我们的发件人的IP是不是在其DNS的txt返回的IP地址中我们就可以识别是不是伪造发件人。那么在实际环境中有没有存在没有开启SPF校验或未配置DNS的txt的呢？于是，根据猜想进行了一系列的实验。

### 3.3 伪造发件人案例

 **3.3.1 未配置DNS的txt类型**

大家可能认为邮件服务器都会配置txt类型，但是实际测试，却发现很多未配置txt类型的，

![](https://image.3001.net/images/20201127/1606475490_5fc0dee2ed291ac664ac1.jpg!small)

对于这种没有配置DNS的txt类型的，收件方收到以后存在不同的处置方法：

1.直接接受

![](https://image.3001.net/images/20201127/1606475513_5fc0def92ff23881bf5d0.jpg!small)

![](https://image.3001.net/images/20201127/1606475531_5fc0)

