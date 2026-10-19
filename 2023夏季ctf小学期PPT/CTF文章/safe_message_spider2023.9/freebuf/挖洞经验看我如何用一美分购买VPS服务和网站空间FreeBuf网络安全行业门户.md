**![online-payment-security.png](https://image.3001.net/images/20191120/1574223274_5dd4bdaa8b89b.png!small)**

**今天分享的Writeup是作者发现VPS和建站托管服务商的支付漏洞，通过一美分（$0.01）交易实现购买VPS和网站空间服务。**

##  **漏洞情况**

存在漏洞的两家网站

> 1\. redaced.net ( 某VPS服务网站 )
>
> 2\. redaced.com ( 某建站托管服务 )

某天，我想购买一个VPS服务作为网络侦测使用，于是我打开了VPS服务网站 redacted.net，我看到在它的购买项中有Paypal结算选项“Paypal
Checkout” 。通常来说，在线支付服务会向Paypal(/cgi-bin/webscr)发送包含需要支付金额在内的POST数据请求，当然，如果在交易过程中的Paypal支付网关（Braintrees
Payments）未设置合理的数据过滤/验证/措施，那么，攻击者就能修改需要支付的金额和其它相关数据。

例如，这里redacted.net网站在用户提交给Paypal的支付请求中，包含类似以下请求数据：

> ….&amount=1321&tax=12&….

然后，我找到了这个数据包，把它进行了一些修改，如下：

> ….&amount=0.01&tax=0&….

也就是说，我用一美分（$0.01）提交支付，之后，我竟然收到了redacted.net的确认邮件：

![1_Moa-wJxoxCv-pIooT3IBrA.png](https://image.3001.net/images/20191120/1574223215_5dd4bd6f59e4e.png!small)

点击其中的 “Confirm My Payment” 支付确认后，我购买的VPS服务竟支付成功了！

第二是在某建站托管服务网站中，当我用虚拟货币购买其网站空间服务时，我发现交易过程中它仅检验Trx
ID（TRONIX支付ID）的有效性，并不对实际需要支付的金额进行验证，所以，我又用上述方法，以一美分（$0.01）的价格，成功购买了价值差不多印尼卢比1.226.954（折合$90-&95）的网站空间。

![1_Ai80WI5wpHBypmUp0plzVA.png](https://image.3001.net/images/20191120/1574223228_5dd4bd7c12a77.png!small)

## 漏洞上报和处理进程

> 2019.11.1 发现redacted.net支付漏洞并上报
>
> 2019.11.2 发现redacted.com支付漏洞并上报
>
> 2019.11.3 redacted.com奖励了我$500美金
>
> 2019.11.4 redacted.net奖励了我一百万印尼卢比 折合$71美金

 ***参考来源：[medium](https://medium.com/@androgaming1912/got-vps-hosting-domain-only-0-01-bug-bounty-edeea1a7d5e6)，clouds 编译整理，转载请注明来自 FreeBuf.COM **  

