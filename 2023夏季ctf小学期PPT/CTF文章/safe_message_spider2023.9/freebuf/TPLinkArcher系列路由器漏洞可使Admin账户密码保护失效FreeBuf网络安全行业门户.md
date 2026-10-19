**Internet路由器是连接我们工作，服务和休闲的无所不在的设备，已经成为每个家庭，企业和公共场所不可或缺的一部分。尽管它们对于我们与世界的连接至关重要，但它们却是我们每天使用的最不安全的设备之一。**

本文将分析TP-Link Archer
C5（v4）路由器中发现的固件漏洞。这是一个零日漏洞，以前没有报告过，并且可能影响家庭和企业环境。如果利用此路由器漏洞，则远程攻击者可以通过局域网（LAN）上的Telnet来控制路由器的配置，并通过LAN或广域网（WAN）连接到文件传输协议（FTP）服务器。

该缺陷被认为是至关重要的，因为它可以授予未经授权的第三方使用管理员特权访问路由器，而这是所有用户在该设备上的默认设置，而无需进行适当的身份验证。在使用此类路由器启用访客Wi-Fi的商业网络上，风险更大。如果将其放置在企业网络上，则受损的路由器可能成为攻击者的切入点，并且成为侦察和横向移动策略中枢转的场所。

结尾部分是TP-Link发布的用于解决其固件问题的补丁。

##  密码溢出问题

在深入研究如何发现此问题之前，描述此缺陷的简短方法是使用户密码无效的易受攻击的HTTP请求。在各种各样的溢出问题中，当将比预期的字符串长度短的字符串作为用户密码发送时，密码值会失真为一些非ASCII字节。

但是，如果字符串太长，密码将完全无效，由空值代替。此TP-Link设备仅具有一种用户类型（具有root特权的admin），并且所有进程均由用户在此访问级别下运行，这可以使攻击者以admin的身份操作并接管设备。

##  触发路由器漏洞

当我们调查引发脆弱情况的原因时，我们可以看到，只需发送正确的请求即可获得对设备的访问权限。请参阅图1，以直观地看到我们用来举例说明此触发器的HTTP请求。

我们这里有两种类型的请求：可以说是安全的和易受攻击的。对于对HTML内容的安全请求，必须验证两个参数：TokenID和JSESSIONID。但是，此处的通用网关接口（CGI）验证仅基于引用者的HTTP标头。如果它与IP地址或与tplinkwifi.net关联的域匹配，则路由器的主要服务HTTPD会将其识别为有效。

![fig1.png](https://image.3001.net/images/20191217/1576561346_5df86ac2dcda6.png!small)

图1：易受攻击的HTTP POST请求未验证所需的参数

如果该引荐来源网址已从标头中删除，则请求将返回“禁止访问”响应。

![fig2.png](https://image.3001.net/images/20191217/1576561359_5df86acf5ce7e.png!small)

图2：从请求中移除Reffer头— HTTP响应返回“ 403 Forbidden”

此问题以相同的方式影响HTTP POST和GET请求，当字符串长度超过允许的字节数时，将取消管理员密码。

![fig3.png](https://image.3001.net/images/20191217/1576561366_5df86ad6d65d3.png!small)

图3：HTTP GET请求同样会使密码无效

##  分析固件

此时，看到这些请求使密码无效后，我们想分析一下设备的固件。由于固件并不总是在供应商的网站上可用，因此我们不得不从设备的闪存芯片中提取固件。

有了存储芯片的版本号，可以更轻松地在线查找有关它的更多信息，并且我们能够使用芯片夹和二进制文件分析工具BinWalk直接从芯片中提取固件。

![fig4.png](https://image.3001.net/images/20191217/1576561372_5df86adc29f26.png!small)

图4：使用BinWalk提取的路由器固件

请注意，在提取期间，有一个RSA私钥存储在内存中。访问Web服务时，此密钥用于加密和解密用户密码。

解压缩固件后，我们发现登录数据存储在rootfs /
etc文件夹中。默认的用户名和密码非常弱。保留默认组合可以允许访问FTP服务器并授予控制台访问权限。如此弱的密码有很多访问权限，几乎任何人都可以猜到，而且不幸的是，它也是传播诸如Mirai的僵尸网络恶意软件的自动攻击的源头。

![fig6.png](https://image.3001.net/images/20191217/1576561378_5df86ae2b0995.png!small)

图5：对路由器的根访问

通过root级访问，我们现在可以获得对二进制文件的一些控制。我们也有TFTP，因此我们下载了MIPS
gdbServer，这是一个用于Unix系统的控制程序，允许操作员从另一个系统远程调试其他程序。这样，调试器不需要驻留在同一设备上，只需要我们要调试的可执行文件驻留在目标系统上即可。

我们将此工具与IDA（一种多处理器反汇编程序和调试器）结合使用，以进行静态和动态分析，因此我们可以找到路由器漏洞的来源，并通过此过程来说明如何在没有漏洞的情况下找到该漏洞。实际触发它。

下图显示了在IDA上查看的已解析HTTP标头的相关部分：

![fig7.png](https://image.3001.net/images/20191217/1576561386_5df86aeab235c.png!small)

图6：已解析的HTTP标头显示了引荐来源网址设置

请注意，此处使用函数strncmp来验证带有字符串tplinkwifi.net的Referrer标头。前面的分支还验证了IP地址。附加调试器以查看这些详细信息，确认此确实是可利用的路由器漏洞。

##  漏洞请求

我们的下一步是检查当我们使用不同的字符串长度发送易受攻击的请求时，密码文件会如何处理。首先，我们尝试发送一个较短的字符串，只有几个字节。

![fig9.png](https://image.3001.net/images/20191217/1576561392_5df86af0ddca4.png!small)

图7：使用较短的密码字符串发送HTTP GET请求

该短字符串通过并损坏了密码文件。结果是用户将无法登录，攻击者也将无法登录。此问题影响Telnet，FTP和Web服务。

![fig10.png](https://image.3001.net/images/20191217/1576561397_5df86af57b47d.png!small)

图8：密码文件被用户提交的较短字节串破坏

接下来，我们尝试通过密码发送超过允许的字符数的密码。

![fig11.png](https://image.3001.net/images/20191217/1576561403_5df86afb9b1e4.png!small)

图9：通过发送长密码

这次，密码完全无效，并且该值现在为空。从那时起，我们仅使用“
admin”作为用户名即可访问TELNET和FTP，而无需输入任何密码，默认情况下，该用户名是设备上唯一可用的用户。

![fig12.png](https://image.3001.net/images/20191217/1576561409_5df86b0134d23.png!small)

图10：管理员密码已失效

##  其他问题

在无需真正身份验证即可获得管理员访问权限后，我们发现该特定设备还允许在WAN上配置FTP。此外，我们可以通过安全的HTTPS连接远程管理路由器，这也容易受到CGI攻击。如果被恶意第三方利用，此路由器漏洞的影响可能是有害的。

攻击者不仅可以获得特权访问，而且合法用户也可以被锁定，并且不再能够通过用户界面登录Web服务，因为该页面将不再接受任何密码（用户不知道）。在这种情况下，受害者可能无法访问控制台，甚至无法访问外壳程序，从而无法重新建立新密码。即使有办法设置新密码，下一个易受攻击的LAN
/ WAN / CGI请求也将再次使密码无效。因此，唯一的访问将是通过USB端口连接的FTP文件。

潜在影响的另一个方面是RSA加密密钥可能会失败，因为它不是设计用于空密码值的。

最重要的是，受害者的设备FTP（如果配置为在WAN上使用）和Telnet（仅LAN）可以完全暴露给攻击者。

##  易受攻击的路由器比比皆是-如何保护您的数据

TP-Link路由器上最近出现的严重漏洞是物联网（IoT）安全世界中一个更大问题的一部分。根据美国消费者协会（American Consumer
Institute）的一项研究，如今，几乎每个家庭都在使用路由器，但是六分之三的路由器由于安全漏洞而没有得到充分更新。当这些缺陷浮出水面时，它们使数百万家庭和企业用户面临数据泄露的风险。而且不仅是文字信息的泄露，比如可能会是来自网络摄像头，监视器和其他使用同一路由器连接到互联网的家庭连接设备的录像。

为了减轻这些风险，用户必须更加重视路由器的安全性，并且要做的第一件事就是更改默认密码。如果设备不允许修改用户名和密码，那么这无疑是查看更多故障的可靠方法。使用无法更改密码的默认设备的企业应应用缓解措施，并在可能的情况下对此类设备访问启用两因素身份验证（2FA）。

##  TP-Link修补程序

TP-Link已发布以下修补程序，以解决TP-Link Archer C5 v4版本和可能公开的其他版本上的此问题。我们建议尽快修补设备。

**Archer C5 V4的固件：**

> <https://static.tp-link.com/2019/201909/20190917/Archer_C5v4190815.rar>

****Archer** MR200v4：**

> [https://static.tp-> link.com/2019/201909/20190903/Archer%20MR200(EU)_V4_20190730.zip](https://urldefense.proofpoint.com/v2/url?u=https-3A__static.tp-2Dlink.com_2019_201909_20190903_Archer-2520MR200-28EU-29-5FV4-5F20190730.zip&d=DwMGaQ&c=jf_iaSHvJObTbx-> siA1ZOg&r=PLBNUfYUCqq_QRL6ODBz0k4R1V299UtnS-k2qEIzw8U&m=zCkLQ3bx_fODtQpVOUYJrY1FpQjUjvVyxo9UP9GZASg&s=5y1-PSEBMnmS3fEF5uER7EQi5bRgejG3L56mbPb7lQA&e=)

****Archer** MR6400v4：**

> [https://static.tp-> link.com/2019/201908/20190826/Archer%20MR6400(EU)_V4_20190730.zip](https://urldefense.proofpoint.com/v2/url?u=https-3A__static.tp-2Dlink.com_2019_201908_20190826_Archer-2520MR6400-28EU-29-5FV4-5F20190730.zip&d=DwMGaQ&c=jf_iaSHvJObTbx-> siA1ZOg&r=PLBNUfYUCqq_QRL6ODBz0k4R1V299UtnS-k2qEIzw8U&m=zCkLQ3bx_fODtQpVOUYJrY1FpQjUjvVyxo9UP9GZASg&s=zJnkCt8s-u8PAvpIwM-> Qi6-ZMHxTeLbooxjUBIKqG7s&e=)

****Archer** MR400v3：**

> [https://static.tp-> link.com/2019/201908/20190826/Archer%20MR400(EU)_V3_20190730.zip](https://urldefense.proofpoint.com/v2/url?u=https-3A__static.tp-2Dlink.com_2019_201908_20190826_Archer-2520MR400-28EU-29-5FV3-5F20190730.zip&d=DwMGaQ&c=jf_iaSHvJObTbx-> siA1ZOg&r=PLBNUfYUCqq_QRL6ODBz0k4R1V299UtnS-k2qEIzw8U&m=zCkLQ3bx_fODtQpVOUYJrY1FpQjUjvVyxo9UP9GZASg&s=HT_FLjNc8UteGuwVzrNCTk8Hm68Q2xmK-> oemmsoWvaE&e=)

 ***本文作者： freexploit，转载请注明来自FreeBuf.COM**

