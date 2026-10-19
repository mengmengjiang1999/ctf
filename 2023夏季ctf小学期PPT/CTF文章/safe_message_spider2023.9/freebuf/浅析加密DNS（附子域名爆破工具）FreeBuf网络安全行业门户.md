**本文章简单介绍一下两种加密DNS协议：DNS over HTTPS 和 DNS over
TLS。这两种协议主要为了解决DNS带来的隐私和中间人篡改问题。**

## 0x01 DNS的安全及隐私

DNS设计之初并没有考虑安全问题，所以大部分DNS查询使用UDP传输，当然也可以用TCP。这两种方式既没有加密也没有签名。这就意味着中间人可以监听到用户访问的域名，导致隐私泄露。另外因为没有签名验证，中间人也可以篡改DNS返回的IP地址，导致用户访问钓鱼网站。后来有了DNSSEC，引入了签名机制，保证了从权威DNS服务器，到DNS递归服务器，再到客户端都没有被篡改。但是这依然没有解决隐私问题。

其实隐私问题之所以没被重视，主要有几点：第一，中间人肯定能知道你要访问的服务器IP地址，多数情况下知道IP就知道是什么网站了。第二，有一些上层协议也会泄露域名，明文HTTP就不说了，TLS协议也有Server
Name Indication（SNI），会暴露明文域名。（注：IETF TLS工作组目前正在探讨草案《[SNI Encryption in TLS
Through Tunneling](https://tools.ietf.org/html/draft-ietf-tls-sni-encryption)》，计划加密SNI）。第三，一些上层协议，如TLS，能够识别DNS是否被篡改，这使得签名DNS本身显得不那么重要。[1]

但即使有上述三点，加密DNS数据也有显而易见的好处。第一，减小攻击面。第二，用户请求DNS之后，未必就非得访问它呀，比如本文下述的子域名爆破，我们只对DNS数据本身感兴趣，而不访问其域名，这样加密DNS就有了实际意义。

所以本文就要探讨一下DNS over TLS和DNS over
HTTPS。这两个协议目前仅限于用户客户端和DNS递归服务器间的通信。截至2018年4月，递归服务器和权威服务器之间的通信不在这两个协议的适用范围内。也许以后递归服务器和权威服务器也会纳入DNS
over TLS协议里，不过目前我没听说有人实现它。

## 0x01 两个协议

DNS over
TLS的标准文档是[RFC7858](https://tools.ietf.org/html/rfc7858)。文档很短，也比较易懂。客户端先和递归服务器进行TLS握手，使用的TCP端口号是853。握手之后，把DNS数据包作为TLS的payload发给DNS递归服务器即可。请求和回答的报文与普通的DNS
over TCP的报文格式一样。

DNS over HTTPS目前没有RFC文档。只有草案《[DNS Queries over
HTTPS](https://tools.ietf.org/html/draft-ietf-doh-dns-over-https)》。这个草案规定可以用GET和POST方法，如果用POST，就把普通的DNS over UDP报文作为HTTP的body发送，并且在HTTP
Header中设置Content-Type为`application/dns-message`。如果用GET，就把普通DNS over
UDP报文用base64编码，把编码后的字符串作为URL的`dns`参数发送。

有一些厂商还支持JSON格式的DNS over
HTTPS协议，比如Google和CloudFlare的DNS服务器。出于兼容考虑，在格式方面，CloudFlare选择和Google保持一致。具体格式参见[Google文档](https://developers.google.com/speed/public-dns/docs/dns-over-https)或[CloudFlare文档](https://developers.cloudflare.com/1.1.1.1/dns-over-https/json-format/)。

为了让用户好记，Google的DNS服务器是8.8.8.8和8.8.4.4，CloudFlare的DNS服务器是1.1.1.1和1.0.0.1。CloudFlare的DNS服务是2018年4月1日上线的，他们自称是因为我们的IP有4个1，所以是4月1日。[2]

## 0x02 子域名爆破

我用C#写了一个非常简易的子域名爆破工具，为了演示DNS over HTTPS。（ **仅为技术讨论使用，请勿用于违法用途！**
）使用的是JSON格式的DNS over
HTTPS，可以从UI上选服务器。纯字典搜索，字典是从[dnsrecon项目](https://github.com/darkoperator/dnsrecon/blob/master/subdomains-top1mil-5000.txt)复制过来的。

这个工具我只测试了Windows 10 + Visual Studio 2017 + .NET Framework 4.6.1。特别是Windows
10以前的操作系统可能连不上<https://1.1.1.1> 。我记得老版Windows不支持IP地址作为证书的Subject Alt
Name，所以证书校验可能会失败。

![浅析加密DNS（附子域名爆破工具）](https://image.3001.net/images/20180415/15237589355016.jpg!small)

工具的地址：<https://github.com/xiaoyinl/securedns> 。欢迎大家提交issues和PR。

## 0x03 参考资料

[1] [RFC7626 - DNS Privacy
Considerations](https://tools.ietf.org/html/rfc7626)

[2] [Announcing 1.1.1.1: the fastest, privacy-first consumer DNS
service](https://blog.cloudflare.com/announcing-1111/)

[3] [DNS over TLS - Cloudflare
Resolver](https://developers.cloudflare.com/1.1.1.1/dns-over-tls/)

[4] [DNS over HTTPS - Cloudflare
Resolver](https://developers.cloudflare.com/1.1.1.1/dns-over-https/)

 ***本文作者：tocttou，转载请注明来自 FreeBuf.COM**

