  

## CAS协议介绍

集中式认证服务（Central Authentication Service，简称CAS）是一种针对web应用的单点登录协议，旨在为 Web
应用系统提供一种可靠的单点登录方法，它允许一个用户访问多个应用程序，而只需向认证服务器提供一次凭证（如用户名和密码）。这样用户不仅不需在登陆web应用程序时重复认证，而且这些应用程序也无法获得密码等敏感信息。“CAS”也指实现了该协议的软件包。

### 发展历史

CAS最初由耶鲁大学的Shawn Bayern开发实现，后来由耶鲁大学的Drew Mazurek维护。CAS1.0实现了单点登录。
CAS2.0引入了多级代理认证（Multi-tier proxy authentication）。CAS其他几个版本已经有了新的功能。

2004年12月，CAS成为Jasig的一个项目，2008年该组织负责CAS的维护和发展。CAS原名“耶鲁大学CAS”，现在则被称为“Jasig CAS”。

2005年5月，CAS协议版本2发布，引入代理和服务验证。2006年12月，安德鲁·W·梅隆基金会授予耶鲁大学第一届梅隆技术协作奖，颁发50000美元的奖金对耶鲁大学开发CAS进行奖励。颁奖之时，CAS在“成百上千的大学校园”中使用。

2012年12月，JASIG与Sakai基金合并，CAS改名为Apereo CAS。2016年11月，基于Spring Boot的CAS软件版本5发布。

### CAS协议角色介绍

1.CAS Clients

客户端，也可以叫做服务，通常是我们浏览器访问的web应用。

2.CAS Server

认证服务器，它的主要用途是颁发票据和对用户进行身份验证。

### CAS协议常见概念以及数据的基本介绍

局部会话：浏览器-客户端之间的会话。

全局会话：浏览器-认证服务器之间的会话。

TGT(Ticket Granting Ticke)：建立全局会话的凭证，包含用户信息、票据生命周期等信息。

TGC(Ticket Granting
Cookie)：认证服务器认证成功后返回给浏览器的cookie，与存储在认证服务器上的TGT相对应，TGC和TGT类似于cookie和session的关系。

ST(Service Ticket)：服务凭证，用于客户端验证用户身份。

![?code=OTU1ZDY1YTEzN2RiNjZjYjk2NmM2YjI2ZmVjMGQ2N2FfQ1RCMFdMOUFEdFRwSE82dm44V1J5cWtiQWROSTVCUjRfVG9rZW46RVQ0RmIyR280b2RDcnV4QnZrcmNWMEVwbk1nXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544735_6458da9f5ecb544f4da53.png!small)

CAS经典架构

上面这图是CAS协议的经典架构，从图中我们可以看到，用户访问不同语言、不同架构的服务，服务又通过CAS、SAML、Oauth等协议与认证服务器进行交互，基于spring
mvc框架的认证服务器从LDAP、数据库、或AD获取数据对用户进行身份验证，然后向用户颁发凭据。

当前版本的CAS集成的身份验证机制有AD、Generic、LDAP、JDBC等等，由于发展的需要，现在的CAS已经支持其他的一些身份协议，例如OIDC、Oauth
2.0等等。

### CAS协议认证流程

以下为CAS官方规范协议流程：

![?code=YzYxYmM2MzIwZDhmNTJmMzdmYWJhYTkxN2YyMTZiZTJfZFVOVlVDb2Y3VVNaNEgwNzRUMUdzd29CS1pkNTdiaU1fVG9rZW46STdvR2JFZ0pqb0prT1Z4MG5rd2NZckRGbnJmXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544745_6458daa9c290839e36437.png!small)

我们可以将这个流程分为两个部分，第一个部分为未登陆时浏览器向第一个网站app1请求资源的过程，可以分为以下几步：

1\. 浏览器访问网站app1

2\.
网站app1对浏览器的请求进行解析，过滤器检测用户是否需要进行身份验证（AuthenticationFilter和TicketValidationFilter）

3\. 网站app1将浏览器重定向到认证服务器

4\. 用户输入账号密码进行登录

5\. 认证服务器向浏览器返回TGC，并将浏览器重定向回之前访问的URL，并在URL中添加参数ticket，也就是ST

6\. 网站app1携带ST去认证服务器进行认证（这个过程对于用户来讲是不可见的）

7\. 认证成功网站app1为浏览器生成cookie，并返回用户请求的资源。

  

![?code=NmUzMTUzYTI5ZjhhYTVmNzc2ZWUwN2M4YTY3YmEzZDRfTUZwdnBjWVlTVjNQaTB6R0tnQjJLeXdYcWNUaTNyeFZfVG9rZW46V1NsWWIwTGNGb3NLdEl4Y1hPYWNiZnFTblliXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544757_6458dab516196ba6f1fa1.png!small)

第一部分示意图

  

![?code=OTVlNjQxNzkwYWU0YWJmNjUwMzgzNzk1Y2IyZTk1OTBfdUtBbUZ5QkZQamhZdEFybzlCdlFpMVNlQjVpTFRtQkRfVG9rZW46Wm90V2J4Z0syb2xWSzd4YnJ0Q2M3Tm9TblNoXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544764_6458dabca9098ca15c7e7.png!small)

认证服务器响应TGC和ST

  

![?code=YzkxNTg1Njg5ZjBjZjllZGYxM2UwNWEzYTliZjc3YjBfNGpwZ2theWxkbEJjeEJINnZjRUZIOWd5WWc1cjlNaXJfVG9rZW46T0M4Z2JmNXRwb2g3N3R4ak4xbmNudVc5bjJlXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544774_6458dac67ba92683cccfb.png!small)

浏览器使用ST请求资源

  

下面是第二部分：

我们已经经过了身份验证，这个时候用户再访问网站app2。

1\. 网站app2验证浏览器的cookie，但是因为网站app2没有登录过，所以没有网站app2的cookie。

2.网站app2将浏览器重定向到认证服务器，浏览器访问认证服务器时会带上cookie。

3.认证服务器发现cookie中有TGC，验证TGC与TGT的对应关系，TGC有效。

4.认证服务器将浏览器重定向到网站app2，并返回一个ST。

5.浏览器使用ST请求网站app2。

6.网站app2使用这个ST去认证服务器进行认证。

7.如果认证成功，网站app2为浏览器生成cookie，并返回用户请求的资源。

![?code=MzA3NzM2ZGUzZWY3MjJiZmI5YzVhNTEwODBmNjg5ZGNfTDVXR2ZCSmlGbTVCN0ZBRFBwUzlVU0tETUlxM1g4VGJfVG9rZW46QWlxc2JjZ0R1b3dBZDF4TnRCTGNwaDRGbnliXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544782_6458dacea8123c377d553.png!small)

用户请求网站app2

![?code=YzYwN2QyNGU5YTliYWZjNmYwZDFmZTJhMWQxZjUwYTZfek5CQTRYaXlyOW9kdzAzWnpPYmwyWDVLRm5RTUtTSU9fVG9rZW46RDRDU2Juajgwb1NuTlB4c2ZnUWNhWWtGbnJmXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544837_6458db0554bef5a1b0a78.png!small)

浏览器携带TGC请求认证服务器并跳转

以下为CAS认证流程中用到的两个过滤器，用于AuthenticationFilter用于检测用户是否登录，TicketValidationFilter用于验证票据是否存在，注意这个过滤器只是检测票据参数是否存在，并不对票据做正确性验证。这么做的目的减少跟认证服务器之间的不必要交互，减少通信，减轻网络负载，这些规则都是可以自定义的。CAS中的过滤器是可以配置的，所以具体效果与当前部署有关。

![?code=YmFjMDM0NDZkZDRlMjFkY2M1YjI1NzM2NzM3NWNjYTRfbUNDR2hRNFVTTDk1WFQwS09OY3drYmFQTWo1T2F6Y3NfVG9rZW46TXpLMmJRNnNSb3RXckR4ckdsYWNZdTlybmFiXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544848_6458db1049ccd94cecbe1.png!small)

AuthenticationFilter

![?code=MzAxNTM3YWI2M2RiZGU0NDliZWFlOThlY2JlNDQ2MTdfMmo2QVI4aVVBencwd0xQN0pubzZ1NDZUZHBMVG5QbkxfVG9rZW46RkhIUGI2Z1JZb2hpc1J4cHFTYmMzenhxbllkXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544855_6458db17d6e1995544fa4.png!small)

TicketValidationFilter

 **CAS** **注销流程**

CAS的注销流程大概可以分为以下四步：

  1. 浏览器向网站app1发起注销请求

  2. 浏览器跳转到认证服务器发起注销请求

  3. 认证服务器校验浏览器请求里的TGC

  4. 认证服务器注销TGT，同时通知已经登录的系统注销已经颁发的ST

![?code=NzVmNmQ2MjcxMWRhYWUwNDZlY2EyNDcxOGFlZDkzYjBfazQ5dEc3NllPQVZWdENKWTJuY2JNcVZBcW1HM2V0TUdfVG9rZW46RXZsdmJ0SmVWb0xQdGt4UjVvZmNDSVdzblNlXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544867_6458db23493f5d68314cb.png!small)

CAS注销流程图示

### CAS 2.0代理模式认证流程

CAS V2引入了代理模式，代理模式的出现解决了不同网站之间的资源相互引用的问题。

![?code=NWFkMmI1YTExNTBiMzU1ZTY3YzY5ODkzZGQwYmIwNjZfY0Z3R1lheGZBbmxlUjFxQlRKYVBPOWRzdjFFSm5ndUlfVG9rZW46Q2VITmJmcjBNbzA1SHF4R1hzYmNjbzRqbkFlXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544905_6458db495c8cbcb93f28c.png!small)

CAS V2流程图

为了解决用户访问CAS单点登录客户端1的某资源，客户端1代表用户从客户端2上获取授权性资源的情况，CAS 2.0出现了代理模式

下面简述一下CAS代理模式的认证流程。

  1. 首先用户去加载代理应用程序“Proxy 网站app”。

  2. proxy发现用户没有登录，将浏览器重定向到认证服务器。

  3. 用户被重定向到认证服务器之后，认证服务器发现用户没有携带SSO Session。要求用户输入账号密码。

  4. 认证服务器收到用户名和密码，如果验证通过，会创建包含TGT的单点登录(SSO)会话TGC cookie，TGT是用户会话密钥SSO session，给用户设置cookie，签发ST，同时会将页面重定向到Proxy。

  5. 用户使用ST请求proxy。

  6. Proxy收到ST并向认证服务器发起验证，验证成功后认证服务器向Proxy返回PGT和PGTIOU。

  7. Proxy收到PGT和PGTIOU之后，会将PGTIOU存储为PGT的映射，并为用户设置cookie。

  8. 用户携带之前Proxy设置的cookie去访问网站app。

  9. 用户的请求到达Proxy，它会验证cookie，如果验证通过，Proxy会通过之前保存的PGT，去认证服务器获取PT。

  10. 认证服务器返回PT给Proxy，Proxy再拿着PT去请求网站app。

  11. 网站app收到带着PT的请求之后，会将PT发送到认证服务器的proxyValidate接口去验证。

  12. 认证服务器验证成功后响应重定向URI。

  13. 网站app收到认证服务器的响应之后，会查看代理URI链并验证该链是否可信，验证通过，网站app会给proxy设置cookie。

  14. Proxy有了cookie之后，会携带这个cookie去访问网站app。

  15. 网站app验证cookie并向proxy返回资源，代理再将收到的响应转发到浏览器。

  

PT(Proxy
Ticket)：如果用户访问的不是一个Web应用，而是一个C/S架构的应用，因为C/S结构的应用得不到cookie，所以用户不能自己去CAS获取ST，而是通过访问proxy
service的接口，凭借proxy service的PGT去获取一个PT，然后才能访问到此应用。

  

## CAS攻击面

CAS在安全方面都做了些什么？

  1. 强制认证，很多CAS客户端都支持强制认证，用户必须重新进行身份验证才能访问特定的资源，一般这种都是基于服务配置的。

  2. 加密传输，4.x之后的版本都默认不允许http传输，但是CAS的安全问题也在于他只对https进行了强制要求。

  3. 设置标头，禁止浏览器缓存，避免凭据重放。

![?code=NGQ1YzYzMGQ5NjNkYjUxMWMxYTExOWEzNTNhMmZjN2NfNzRzMDFtbW4wa3dWeGVmNHZwbE1GekFpR0lOTlJaOUdfVG9rZW46SWRhbWJBcVJzb1hKZnB4eHQ2aWNHRkdjbkdiXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544920_6458db588570effcfc365.png!small)

CAS设置的标头

CAS Server为java实现，不可避免的就是反序列化漏洞，最新版本的CAS Server使用Spring框架，也受到了去年的Spring
framework
RCE漏洞的影响，但是因为使用默认CAS部署的web应用并不是很多，影响倒不是很大。根据不同的实现和配置情况也会出现一些凭据泄漏未授权访问等情况。

![?code=MTVlOGE5NzVhZmMxY2QxYjExNDlhMjE0NzA1M2I1MmJfcFplZWxRaElEeFVOVFpjUmhuenNaZk1FMldoRU9DVGtfVG9rZW46QWhWSWIyWFZsb3hiYjF4YUpmaWNCQTUybkllXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544928_6458db60dc8fb859fb248.png!small)

  

### CAS攻击面-XSS

通过POST请求CAS的REST API(默认是不开启的)，输入用户名密码。

如果身份验证失败会将用户名输出在页面上，导致xss,由于这个信息也会写入日志，且CAS
6.X一些版本使用了log4j组件，会有log4j2的漏洞。这个洞产生的原因是认证失败后抛出AuthenticationException异常，并输出这部分信息。

![?code=Y2RhZjVkYmI0OTYxOGNhZTNjZTU1ZGRmNDQ5OGM5MmRfNTRZRzYyZ0F4YU05cXVFeWlQZXBKb0hOTldraVhnSkJfVG9rZW46SnJwemJ4TGZqb2M2aDB4M3BPcmNWZUtObm0zXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544943_6458db6f55de68184e40a.png!small)

漏洞信息

### CAS攻击面-统一注销错误

如果服务注销时只注销局部会话，这种情况大部分是由于认证服务器配置出错导致的。由于配置不当等原因，用户在网站app1注销，如果是局部会话注销，这个时候浏览器与认证服务器的cookie，也就是TGC依然是活跃的状态，这个时候访问网站app2，网站app2与认证服务器进行交互的时候发现我们的账户依然是登录状态，所以就可以直接从网站app2获取资源，其实这个时候，注销是失败的。

还有一种情况和这种情况是类似的，就是当我们集群部署CAS的时候，由于负载均衡或者一些别的转发配置的原因，从认证服务器到客户端的注销请求可能会被转发到不是浏览器提交注销请求的客户端，那这个时候客户端验证ST就会失败，注销操作也就失败了。

### CAS攻击面-凭据泄漏

在CAS
V1里最重要的凭据为TGC，而TGC又保存在浏览器的cookie里，如果TGC泄露，则我们可以构造请求向认证服务器请求服务，而认证服务器验证TGC后，会向我们返回服务的ST，前面认证流程然后我们说了，浏览器将ST放入参数请求服务，服务验证ST，那么这个时候我们就可以从服务获取数据了。当然这个凭据泄露仅仅指的是TGC。相信大家刚开始接触web的时候都用过一些xss平台，本质上是一样的，就是获取cookie。

![?code=OTUyM2IwY2M4MmFlMmVkOThiOWI1Zjc4ZmJjYWYyZDVfMVEyUUtVMGVQS01VYXE3S2ppT2Q0UXo0R1V6cVU4S0FfVG9rZW46U21DMGJuSEs0b3hDUjd4TWNVTmNjdjR5bkhWXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544955_6458db7be2e5a47f00ad4.png!small)

cookie中的TGC

![?code=NDE3OWZjZDkzYzM4NDUyZTNjNmQ2MDQ4Y2Y5MGE0ZjNfQXF6azBKbUFBWkZ0ZnhIdGx5VXJLMzI0MDc1TUtyVTBfVG9rZW46QVZqdmJEYnlvb3ZEbHF4YU04SmNRbEdrbjFnXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544962_6458db82e293ec34a361b.png!small)

使用泄露的TGC请求ST

### CAS攻击面-凭据爆破

如果凭据在生成时不遵守随机不可猜测的开发原则，那么用户可以通过爆破来猜测凭据。比如ST生成有规律性，那么用户可以通过猜测ticket来请求其他服务，因为CAS授权是统一的，所以在经过身份认证后，只要知道服务的ST就可以向服务发起请求。

### CAS攻击面-其他问题

1.凭据重放，在一些早期版本的Safari浏览器可以通过回退按钮，浏览器会被迫重放用户凭据。CAS官方也意识到了这个问题并在登录页显示了提示。

![?code=YWU3ZTU3YjU1ZmUyN2U0ZDc4ODFmMjc3OGRhODM0NTZfSzI3bEdRNEJLYVdyUXpBeTNVWlRlTWI3YXR6TlBVS0dfVG9rZW46UjFOd2JqZFhub3NjVFd4alVCZGN2SVNsbjRnXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683544977_6458db91dd1c0cf964c33.png!small)

2.未授权访问，用户绕过授权流程，通过请求CAS
Server接口获得票据。再请求向服务发起请求获取特定的受保护的资源，因为CAS架构下的服务使用统一身份认证，导致攻击者可以访问权限内的所有服务。

## CAS漏洞案例

### 漏洞案例-XSS

一些CAS版本提供了reset功能来创建或查询凭据，右边是reset协议的处代码。用户输入用户密码请求reset接口，如果认证失败就抛出AuthenticationException异常。

![?code=ODc0NTAwMjNjMWRkMTMxYjNlNjFhMDdhZmFiOGQwZDZfYUhsVUhyUHg5OFNaczcxWVRuTU5lMU1WZXp0OUFoMm9fVG9rZW46VDNxemJRME1zb1Zsdjd4V1FTNmNiZ0RHbkpmXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683545023_6458dbbfe2a93410e3281.png!small)

  

进入ResponseEntity，将用户信息输出。

  

![?code=MGMwZjlkYzQ3NzRhZGFmNDE0MmUxNWQyNDIxZDg2YmJfOGk2aXY0VWtBSWxZbVEydEpTWDdrOWtxSE5jaTIzSEdfVG9rZW46T3EzU2J0Zjhmb2NBeFZ4SnFsMmNWRW1Fbk5lXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683545005_6458dbadde1953016ca79.png!small)

### 漏洞案例-反序列化

在CAS的一些版本里面，数据传输加密的key硬编码到了源码，如果部署的时候不修改，就会导致用户通过传入精心构造的序列化数据达到命令执行的效果。

  

环境搭建:

Vulhub

/apereo/4.1-rce

影响版本：CAS 4.X

漏洞原因：数据传输加密的key硬编码

![?code=YjAzODI5NTIwM2NmM2U1MTg0MThmYTM3ZjAzNjRmMzRfanQxUE12ZDZ0aGpHTVRFRkxqNjBCTWtlbklGWGt4Zk5fVG9rZW46SnYyaGJ3WVBrb0tjZEN4NkRVNmNSMzk3blcwXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683545042_6458dbd2296a6a52326fb.png!small)

key硬编码

漏洞利用：

  1. 使用工具生成反序列化payload

![?code=MGNkZDM4NDFlNTYwMjQ3Njg0ZGJjMzBlZDljZmMyYWRfRGc4aHB0MGdjWmlXWVJhRTJkeXFmeVhjYWNhNW1DcFlfVG9rZW46SUU0bGJJVnA5b2V5YXB4MW9nR2M5bVQxbmVkXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683545051_6458dbdbe7aa0cca92480.png!small)

  2. 将payload传入excution参数

![?code=YTI4MGNlMzliODcyY2MwYjAyZWI4ODNjNmFjMTY3MmZfQXdPYWMwUGJlVWtuVlh0d01ubzNDU0oxMUtEZEpVak1fVG9rZW46U2t1NWJLMnZZb01zR2l4NmpGa2NXcmpJbkxoXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683545061_6458dbe589a6b88e75ce2.png!small)

传参数据包

![?code=NzM2MjUzOTViNTJjOGQ5ZjJjODEyNTI1YzI3MDRiN2JfYTdyZXN1TjhXZWJ4dWkxdnRDbEJmQ3VtS25FTklFa3RfVG9rZW46RElzdGJMZFlob0E3Yk54N0RhSWN5QlNyblViXzE2ODM1NDM5NjM6MTY4MzU0NzU2M19WNA](https://image.3001.net/images/20230508/1683545070_6458dbeec1153adb828e4.png!small)

命令执行结果

CAS
V1相对其他身份协议并没有任何优势，甚至因为它的B/S架构，导致很多应用场景无法接入。相比CAS，其实OIDC、OAuth和SAML优势更加明显，但是经过了这么多年的发展，CAS因为融入了越来越多其他的身份协议，已经不再是一个简单的身份协议了，它更像是一个协议架构。现在的CAS
Server可以接入多种身份协议，比如你可以用CAS认证服务器，也可以使用SAML、OAuth等协议进行认证，当然，接入更多的场景也会伴随着更多的漏洞，这需要我们更深入的研究。

