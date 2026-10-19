本文首先介绍了Cobatl Strike的工作方式，总结了一些可以用来识别Cobalt
Strike服务器的特征，随后介绍了Beacon的安全机制以及如何扫描并解析出staging beacon配置的方法，最后搜集了一些Cobalt
Strike服务器、流量、staging beacon各方面的其特征技术。

## 0x00 Cobalt Strike简介

### Cobalt Strike

Cobalt Strike 作为一种 **后渗透工具** ，可以完成 **侦察** 、 **鱼叉式钓鱼** 、 **浏览器代理** 等攻击。

Cobalt Strike 分为 **客户端** 和 **服务器** 两部分，服务器端被称之为Team Server。

Team Server既是Beacon payload的 **控制器** ，也是Cobalt Strike提供 **社工功能** 的主机。Team
Server还存储了Cobalt Strike收集的 **数据** 以及 **日志记录** 。工作模式如下图所示：

![img](https://image.3001.net/images/20210518/1621330394_60a389dadb6c62028e06f.jpg!small)

### Beacon

 **Beacon是Cobalt Strike运行在目标主机上的payload，Beacon在隐蔽信道上我们提供服务，用于长期控制受感染主机**
。它的工作方式与Metasploit Framework Payload类似。在实际渗透过程中，我们可以将其嵌入到 **可执行文件** 、添加到
**Word文档** 或者通过 **利用主机漏洞** 来传递Beacon。

Beacon的功能包括以下几点：

> 使用HTTP或DNS检查是否有待执行任务
>
> 可连接到多个C2域名
>
> 能够在分段传输后自动迁移
>
> 与Cobalt Strike紧密集成，通过社工、主机漏洞和会话来传递Beacon

根据内置Listener的分类可以将Beacon分为：

> HTTP and HTTPS Beacon
>
> DNS Beacon
>
> SMB Beacon

 **Listener是用来接收Beacon请求信息的Cobalt Strike模块** ，此处不多介绍。

Beacon翻译为信标，就像信标一样在网络中标识自己的方位：“嘿，我是肉鸡，我在这...”。可以通过下图来看 **Beacon的工作原理** ：

![1621330674_60a38af2c2d2f03fb7397.jpg!small?1621330674666](https://image.3001.net/images/20210518/1621330674_60a38af2c2d2f03fb7397.jpg!small?1621330674666)

Beacon在目标主机上运行之后，会主动向我们提前设置好的 **Listener**
发送请求信息(叮，您有新的主机已上线)。![1621330493_60a38a3d679f4923de390.jpg!small?1621330493197](https://image.3001.net/images/20210518/1621330493_60a38a3d679f4923de390.jpg!small?1621330493197)

Team Server控制器接收到请求后会检查是否有 **待执行的任务** ，如果有就会将 **任务** 下发到Beacon。

![1621330656_60a38ae04157f65fef2db.jpg!small?1621330656151](https://image.3001.net/images/20210518/1621330656_60a38ae04157f65fef2db.jpg!small?1621330656151)

### Beacon Staging Server

值得一提的是 **payloading staging** ，很多攻击框架都是使用 **分段** 的payload，以 **防止payload过大**
，覆盖到了上一函数栈帧的数据，导致引发异常，另外为了适应不同的攻击场景，可以分阶段进行payload投递。

Cobalt Strike使用 **stager** 解决这个问题，stager是一段很精短的代码，它可以
**连接下载真正的payload并将其注入内存** 。攻击者首先投递一个小巧的stager payload，然后通过stager去beacon
staging server的某个URL下载完整的payload。

![1621330646_60a38ad662beb84a06329.jpg!small?1621330646367](https://image.3001.net/images/20210518/1621330646_60a38ad662beb84a06329.jpg!small?1621330646367)

当存储着Beacon配置和payload的stager服务器暴露在公网上的时候，是可以被所有人访问的。不幸的是，默认情况下访问该服务是一个伪装的404页面。这也导致了各类扫描器、空间测绘系统、威胁情报平台等并不能基于页面response信息进行有效判断。

![1621330633_60a38ac96791c26a54856.png!small?1621330633280](https://image.3001.net/images/20210518/1621330633_60a38ac96791c26a54856.png!small?1621330633280)

## 0x01 Cobalt Strike服务器识别

2019年2月19日，Strategic Cyber LLC发布了Cobalt Strike Team Server Population
Study。该研究的部分目的是调查Cobalt Strike软件的许可状态，并识别和分析对当前使用的软件版本所做的重大更改。

该研究确认了多种方法用于识别在野的Cobalt Stike服务器：

>  **默认证书** ：Cobalt Strike服务器附带 **默认安全证书** ，如果黑客没有修改默认证书，就可以使用该默认证书进行指纹识别。
>
>  **默认端口** ：Cobalt Strike服务器的默认控制端口是 **50050/TCP** ，这个端口基本上没有其他服务在使用。
>
>  **NanoHTTPDweb特征（适用于3.x）** ：Cobalt Strike服务器的”404 Not Found“
> HTTP响应与NanoHTTPDweb服务器有细微的不同，可以通过该细节来识别CS服务器。

另外2020年底salesforce新提出了唯一标识TLS服务端的 **JARM指纹** 也为我们提供了新的思路。

总的来说，上面列表中最可靠的方法是使用 **默认安全证书** 对Cobalt
Strike服务器进行指纹识别。其余的检测方法则不太能唯一确定，只有与其他方法交叉验证后才具有较高的可信度。例如，任何使用50050端口、同时提供NanoHTTP
web服务器特有的HTTP响应的服务器都更可能是Cobalt Strike服务器，而不是仅显示HTTP响应签名的服务器。

### 默认证书

Cobalt Strike默认证书如下:

![1621330689_60a38b0164499b51a10f5.png!small?1621330689264](https://image.3001.net/images/20210518/1621330689_60a38b0164499b51a10f5.png!small?1621330689264)

默认的证书具有很明显的特征，例如

    
    
    O=cobaltstrike, OU=AdvancedPenTesting, CN=Major Cobalt Strike

Cobalt Strike不同版本的证书指纹不同，但可以根据证书指纹进行识别是否是Cobalt Strike服务器。

### NanoHTTPD响应 （适用于3.x）

Cobalt
Strike服务器基于NanoHTTPD，于2012年首次发布。NanoHTTPD是一个基于java的开源web服务器框架。NanoHTTPD服务器响应中包含一个额外的空字节："HTTP/1.1"后面是一个
**空字节（0x20）** ，而在其他web服务器响应中不存在这个空字节。

![1621330698_60a38b0ab342cb3c10ffd.png!small?1621330698700](https://image.3001.net/images/20210518/1621330698_60a38b0ab342cb3c10ffd.png!small?1621330698700)

2019年1月2日， Cobalt Strike 3.13版发布。Cobalt
Strike发布的声明指出，该版本“从HTTP状态响应中删除了无关的空字节”。

所有3.13版本之前的Cobalt Strike服务器的HTTP响应都包含这个空字节，可以使用扫描器检索HTTP响应来识别。通过手动抓包Cobalt
Strike服务器的连接，也可以很容易看到这个额外的空字节。由于绝大部分的破解Cobalt Strike没有更新或补丁，通过这种方法发现恶意Cobalt
Strike服务器的概率仍然较大。

安全公司Fox-IT于2019年2月26日发布了关于Cobalt Strike服务器的[研究](https://blog.fox-it.com/2019/02/26/identifying-cobalt-strike-team-servers-in-the-wild/)，该研究不仅提供了细节和如何识别3.13版本之前的服务器（对应HTTP响应中额外的空字符），还包括从[Rapid7](https://opendata.rapid7.com/)公开数据中从2015到2019年使用该检测方法发现的超过7000
Cobalt Strike 主机IP列表。

类似的，2019年2月27日，知道创宇安全研究团队发表了一篇[博客](https://medium.com/@80vul/identifying-cobalt-strike-team-servers-in-the-wild-by-using-zoomeye-debf995b6798)，详细介绍了他们使用Strategic Cyber LLC报告的 **NanoHTTPD 404 Not Found响应异常**
以及 **空字节异常** 来识别Cobalt
Strike服务器。他们在ZoomEye的数据中发现的服务器更少，但仍然超过了3000台。知道创宇报告称，构建Cobalt
Strike的开源NanoHTTPD代码响应方式如下：

    
    
    HTTP/1.1 404 Not Found  
    Content-Type: text/plain  
    Date: Day, DD Mmm YYYY HH:MM:SS GMT  
    Content-Length: 0

知道创宇的检测逻辑就是基于这一发现。然而他们随后还观察到HTTP响应中的顺序实际上可能不同，在一些Cobalt Strike系统的响应中"Content-Type"在"Date"之后显示。

### JARM指纹

在介绍JARM之前回顾一下JA3指纹。

由三位Salesforce研究员开发的开源[JA3](https://github.com/salesforce/ja3)项目，可以通过对服务器和客户端之间的
**TLS协商** 进行 **指纹识别** 来检测可疑的HTTPS连接。

> TLS/SSL版本
>
> 可接受的加密套件
>
> elliptic curve细节（如elliptic curve point格式）等等特征都可以被做成指纹。

JA3用于客户端，JA3S则用于服务器。在Cobalt Strike的案例中，Client
beacon（使用Windows套接字来发起通信）和运行在Kali Linux上的Cobalt
Strike服务器的TLS协商就可以产生[指纹](https://engineering.salesforce.com/tls-fingerprinting-with-ja3-and-ja3s-247362855967)。这些指纹需要交叉验证才能可靠地发现Cobalt
Strike服务器，尽管Cobalt Strike服务器可以通过重定向来部分让这种检测，但仍然有许多Cobalt Strike服务器没有使用这种代理。

JA3和JA3S签名可以与[Zeek/Bro](https://github.com/salesforce/ja3/tree/master/bro)和[Suricata](https://github.com/OISF/suricata/blob/master/src/util-ja3.c)等工具一起使用。来这些网络检测工具输出数据可以输入到诸如Splunk这样的SIEM中。JA3和JA3S指纹可以从[Salesforce’s
Github
account](https://github.com/salesforce/ja3/tree/master/lists)和[其他来源](https://sslbl.abuse.ch/ja3-fingerprints/)获得。

#### JA3

Cobalt Strike默认的SSL/TLS证书是固定的，所以一般都是使用这个证书作为特征值来发现Cobalt
Strike服务器，服务端传给客户端的SSL默认证书有很明显的特征：

    
    
    C=Earth，ST=Cyberspace，L=Somewhere，O=CobaltStrike，OU=AdvancedPenTesting，CN=Major CobaltStrike

![1621330732_60a38b2c5e63b59726b03.png!small?1621330732780](https://image.3001.net/images/20210518/1621330732_60a38b2c5e63b59726b03.png!small?1621330732780)

JA3方法用于收集Client Hello数据包中以下字段的 **十进制** 字节值：

> 版本
>
> 可接受的密码
>
> 扩展列表
>
> 椭圆曲线密码
>
> 椭圆曲线密码格式。

然后将这些值串联到一起，在使用“,”分割开各个字段，同时用“-”来分隔各个字段中的各个值。

![1621330718_60a38b1e15fe31b2a9c9a.png!small](https://image.3001.net/images/20210518/1621330718_60a38b1e15fe31b2a9c9a.png!small)

这些字段的顺序如下： **TLS版本信息** 、 **可接受的密码** 、 **扩展列表** 、 **椭圆曲线密码** 和 **椭圆曲线密码格式** 。

用CobaltStrike4.1的连接流量举例。

![1621330772_60a38b54dc8ae2066d02a.png!small?1621330773953](https://image.3001.net/images/20210518/1621330772_60a38b54dc8ae2066d02a.png!small?1621330773953)

    
    
    771,49188-49192-61-49190-49194-107-106-49162-49172-53-49157-49167-57-56-49187-49191-60-49189-49193-103-64-49161-49171-47-49156-49166-51-50-49196-49195-49200-157-49198-49202-159-163-49199-156-49197-49201-158-162,67,,11-2-256(如果无上述字段，则这些字段的值为空)

然后会算这些字符串的MD5哈希值，以生成易于使用和共享的长度为32字符的指纹，他们就是JA3
TLS客户端的指纹。比如上述CobaltStrike4.1客户端指纹：

    
    
    fa704723a210632b2ff9ad03be418651

JA3S

创建JA3后，就可以使用同样的方式对TLS的服务端进行指纹识别，即对TLS Server Hello信息进行指纹识别。JA3S会收集Server
Hello数据包中以下各个字段的十进制字节值：版本、可接受的加密算法和扩展列表，然后将这些值串联起来，使用“,”来分隔各个字段，使用“-”分隔每个字段中的各个值。

这些字段的顺序如下：TLS版本信息、可接受的密码、扩展列表

![1621330778_60a38b5a7a7cba6ae2877.png!small?1621330778940](https://image.3001.net/images/20210518/1621330778_60a38b5a7a7cba6ae2877.png!small?1621330778940)

CobaltStrike4.1的服务端：

    
    
    771,49192,9-------->5513ab2983a0db88fadd353de0341e7c

同一台服务器会根据Client Hello信息机器内容以不同的方式创建Server
Hello消息，因此这里不能跟JA3那样，仅仅根据服务器的Hello消息来对其进行指纹识别。尽管服务器对不同客户端的响应不同，但是他们
**对同一客户端的响应总是一致** 的。

比如：客户端正在发送TLS Client
Hello数据包，其中数据都是A。因此，服务器会的响应的内容也是由A构成，并将始终用A来提供同样的响应。与此同时，另一个客户端也在发送数据包，并且内容都是B。类似的，服务器现在会用B进行响应，并且总是用B组成的B串进行响应。可以看到，对于不同的客户端，服务器会给予不同的响应，但是对于每个客户端来说，总是以相同的方式进行相应。

![1621330791_60a38b67f3f175a08f3bb.png!small?1621330792852](https://image.3001.net/images/20210518/1621330791_60a38b67f3f175a08f3bb.png!small?1621330792852)

在这个日志输出中，JA3位于左侧，JA3S位于右侧，使用同一客户端与同一服务器交互了4次。然后，再次使用不同的客户端进行了4次以上的交互。不难发现，服务器的响应方式对于同一客户端总是相同的，但对于不同的客户端却是不同的。

例如，MetaSploit 的 Meterpreter 和 CobaltStrike（并非4.1版本） 的 Beacon 都使用 Windows
套接字来启动 TLS 通信。在 Windows 10 上，

    
    
    JA3=72a589da586844d7f0818ce684948eea（指定 IP 地址），JA3=a0e9f5d64349fb13191bc781f81f42e1（指定域名）

由于 Windows 上的其他普普通通的应用程序也使用相同的套接字，因此，我们很难识别其中的恶意通信。但是，Kali Linux 上的 C2
服务器对该客户端应用程序的响应方式与 Internet
上的普通服务器对该套接字的响应方式相比来说是独一无二的。尽管服务器对不同客户端的响应不同，但它们对同一客户端的响应总是一致的。因此，如果结合
ja3+ja3s，就能够识别这种恶意通信，而不用考虑目的地 IP、域名或证书等细节信息。

#### 利用JARM指纹识别的问题

Salesforce研究人员发布了一篇名为[Easily Identify Malicious Servers on the Internet with
JARM](https://link.zhihu.com/?target=https%3A//engineering.salesforce.com/easily-identify-malicious-servers-on-the-internet-with-jarm-e095edac525a)的文章，并在github上发布了一个[JARM扫描工具](https://link.zhihu.com/?target=https%3A//github.com/salesforce/jarm)。

 **JARM** 是一个主动TLS服务端指纹工具，主要用途如下：

> 快速验证一组TLS服务器是否使用相同的TLS配置；
>
> 通过TLS配置划分TLS服务器，并识别可能归属的公司；
>
> 识别网站默认的应用或基础架构；
>
> 识别恶意软件C&C控制节点，以及其他恶意服务器。

JARM的核心在于：TLS Server根据TLS Client Hello中参数的不同，返回不同的Server Hello数据包。而Client
Hello的参数可以人为指定修改，因此通过发送多个精心构造的Client Hello获取其对应的特殊Server Hello，最终形成TLS
Server的指纹。具体能够产生影响的参数包括但不限于：

> 操作系统及其版本
>
> OpenSSL等第三方库及其版本
>
> 第三方库的调用顺序
>
> 用户自定义配置等等

而前文提到，TLS服务器对不同客户端的响应不同，但是他们对同一客户端的响应总是一致的。因此不能跟JA3那样，仅仅根据JA3S对服务器进行指纹识别。而JARM采取了一种类似fuzz的方式，主动向TLS服务器发送10个TLS
Hello数据包并对Server Hello中的特定字段进行分析，以特定方式对10个TLS服务器响应进行哈希处理，最终生成JARM指纹。

JARM中的10个TLS客户端Hello数据包经过特殊设计，目的就是提取TLS服务器中的唯一响应。总之JARM与我们在进行流量分析威胁时常用的JA3、JA3/S不同：

> JA3、JA3/S主要基于流量，服务器面对不同客户端产生不同的JA3S指纹。
>
> JARM则是完全主动的扫描并生成指纹，服务器可以生产唯一的JARM指纹。

在[Easily Identify Malicious Servers on the Internet with
JARM](https://link.zhihu.com/?target=https%3A//engineering.salesforce.com/easily-identify-malicious-servers-on-the-internet-with-jarm-e095edac525a)原文中，作者给出了一份C2和JARM对应的清单：

Malicious Server C2| JARM Fingerprint| Overlap with Alexa Top 1M  
---|---|---  
Trickbot| 22b22b09b22b22b22b22b22b22b22b352842cd5d6b0278445702035e06875c| 0  
AsyncRAT| 1dd40d40d00040d1dc1dd40d1dd40d3df2d6a0c2caaa0dc59908f0d3602943| 0  
Metasploit| 07d14d16d21d21d00042d43d000000aa99ce74e2c6d013c745aa52b5cc042d| 0  
Cobalt Strike| 07d14d16d21d21d07c42d41d00041d24a458a375eef0c576d23a7bab9a9fb1|
0  
Merlin C2| 29d21b20d29d29d21c41d21b21b41d494e0df9532e75299f15ba73156cee38| 303  
  
在理想情况下如果JARM与C2唯一对应，那么就多了一种主动发现C2节点的特征。然而在验证时，搜索Cobalt
Strike对应的JARM发现了2338个独立IP，但TOP5的应用为：

应用| 数量  
---|---  
Cobalt Strike团队服务器| 1,137  
CobaltStrike-Beacon服务端| 373  
Tomcat-Web服务器| 40  
Weblogic应用服务器| 21  
WordPressCMS博客系统| 14  
  
可以看到和上面CobaltStrike相同JARM的还有
Tomcat、Weblogic和WordPress等开启TLS的Web应用，也就是说CobaltStrike这个应用只是该JARM对应TLS服务器其中的一个子集。

而在之后的验证中发现，JARM指纹与上层应用无强关联性，使用相同JDK的Tomcat和Cobalt
Strike拥有相同的JARM指纹，这也解释了为什么会有那么多的Weblogic和Tomcat应用被识别出来了，因此不能直接通过JARM去判定CobaltStrike。同样，对于CobaltStrike而言JARM也并不唯一，其JARM与不同JDK环境下TLS服务有关。因此JARM仅仅是一种TLS服务端特征的标识方式，只能作为一个
**辅助手段** ，不能完全被用作Web上层应用的唯一指纹。

## 0x02 Beacon的安全性

设想这样一个问题，如果有人 **劫持** 了你的通信流量，并可以监听到你的Beacon向Team Server传回的数据，这时会发生什么呢？

![1621330813_60a38b7d87fd3281c61dd.jpg!small?1621330813557](https://image.3001.net/images/20210518/1621330813_60a38b7d87fd3281c61dd.jpg!small?1621330813557)

答案是什么都不会发生。因为Beacon内置了多种 **安全特性** （除了第四条）：

> 1.Beacon stage 在连接时会验证Team Server
>
> 2.Beacon 的任务请求和任务输出都是被加密的
>
> 3.Beacon 有重放保护机制
>
> 4.Beacon stagers本身 **没有任何安全机制**

### 通信加密机制

当你启动Team Server并创建了Beacon Listener时，Team Server就会创建 **公钥对** 来保证后续传输过程的安全性。

本文以分段传输payload为例，来详细讲解一下Cobalt Strike的安全特性。

1.当stager下载stage时， **公钥** 也会被一起发送：

![1621330851_60a38ba3bee48fb0c4a4d.jpg!small?1621330851631](https://image.3001.net/images/20210518/1621330851_60a38ba3bee48fb0c4a4d.jpg!small?1621330851631)

2.当Beacon stage准备check in的时候，第一步就是要发送关于beacon
session的元数据(Metadata)。元数据中包含了用户、PID、计算机名称、IP地址等基础信息，同时元数据中也包括了Beacon
stage创建的一个 **随机会话密钥** 。为了保证安全性，Beacon stage会使用 **公钥** 加密元数据(含会话密钥)，这意味着只有Team
Server才能够解密该数据包。

![1621330827_60a38b8b716269ca5fe53.jpg!small](https://image.3001.net/images/20210518/1621330827_60a38b8b716269ca5fe53.jpg!small)

3.当Beacon从Team Server下载任务的时候，团队服务器会使用 **会话密钥** 加密这些任务，Beacon stage也会使用
**会话密钥** 来解密任务列表。

![1621330868_60a38bb48558fac178d02.jpg!small?1621330868343](https://image.3001.net/images/20210518/1621330868_60a38bb48558fac178d02.jpg!small?1621330868343)

4.同样在返回任务结果的时候，Beacon stage也会使用 **会话密钥** 对任务输出加密。

![1621330879_60a38bbfaf6822a79bfb7.jpg!small?1621330879559](https://image.3001.net/images/20210518/1621330879_60a38bbfaf6822a79bfb7.jpg!small?1621330879559)

可以看到 **Raphael** 在设计Cobalt Strike的时候已经充分的考虑到了它的安全性问题。

### stager URL生成机制

当使用payload staging时，Cobalt
Strike会在其Web服务器上托管stager。任何人都能连接到这个服务器上，通过访问正确的URI来下载payload，否则直接访问会返回`404 Not
Found`。

![1621330886_60a38bc65111eb4f14103.png!small?1621330886331](https://image.3001.net/images/20210518/1621330886_60a38bc65111eb4f14103.png!small?1621330886331)

stager URI的生成规则如下：

    
    
    public static long checksum8(String text)  
    {  
    if (text.length() < 4) {  
    return 0L;  
    }  
    text = text.replace("/", "");  
    long sum = 0L;  
    for (int x = 0; x < text.length(); x++) {  
    sum += text.charAt(x);  
    }  
    return sum % 256L;   
    }  
    ​  
    public static boolean isStager(String uri)  
    {  
    return checksum8(uri) == 92L;  
    }  
    ​  
    public static boolean isStagerX64(String uri)  
    {  
    return (checksum8(uri) == 93L) && (uri.matches("/[A-Za-z0-9]{4}"));  
    }

可见当传入的`/+4个字符`经过checksum8计算后，符合相应的条件就可以下载对应的stager。

详细的逆向过程可参考[魔改CobaltStrike：免杀就像便秘一样](https://www.52pojie.cn/thread-1396671-1-1.html)

### stager加密机制

大多数stager是PE文件，beacon的代码存在其`.data`区块里并使用4字节异或加密，通过异或解密后可以从中解析出beacon的config文件。

![1621330894_60a38bceb552276ecdfa3.png!small?1621330895125](https://image.3001.net/images/20210518/1621330894_60a38bceb552276ecdfa3.png!small?1621330895125)

详细逆向过程参考[CobaltStrike4.0
远控分析](https://www.52pojie.cn/thread-1334525-1-1.html)。

其中，从3.x到4.x，cs自解密的算法一直没变。cs 3.x版本的异或密钥是0x69，4.x版本的异或密钥是0x2e。

## 0x03 Beacon staging server扫描

在上一节介绍Beacon的安全性时提到，如果开启了payload staging分阶段投递，任何人都能连到该Cobalt
Strike服务器上下载该payload并分析它的内容。因此可以在全网扫描可疑的服务器来下载、分析出Cobalt Strike beacon
stager的配置。

### 获取stager地址

根据默认的地址生成规则，可通过如下算法从URI逆推出stager地址，并且可以根据不同的输入生成32位或64位的payload的地址。

    
    
    def generate_checksum(input):  
    trial = ""  
    total = 0  
    while total != input:  
    total = 0  
    trial = ''.join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890")  
    for i in range(4))  
    for i in range(4):  
    total = (total + ord(trial[i:i+1])) % 256  
    return trial  
    ​  
    if __name__ == '__main__':  
    uri_x86 = generate_checksum(92) # 32位的payload  
    uri_x64 = generate_checksum(93) # 64位的payload

### 解密stager

可通过如下脚本对stager进行解密后再解析出beacon config：

    
    
    import sys  
    import struct  
    ​  
    filename = sys.argv[1]  
    data = open(filename, 'rb').read()  
    t = bytearray(data[0x45:])  
    (a,b) = struct.unpack_from('<II', t)  
    key = a  
    t2 = t[8:]  
    out = ""  
    with open(filename+'_decoded', 'wb') as f:  
    for i in range(len(t2)//4):  
    temp = struct.unpack_from('<I', t2[i*4:])[0]  
    temp ^= key  
    out = struct.pack('<I', temp)  
    print(out)  
    key ^= temp  
    f.write(out)

### 解析配置文件

解密后的文件使用如下脚本解析出beacon的配置文件：

<https://github.com/Sentinel-One/CobaltStrikeParser>

解析出的配置如下

![1621330903_60a38bd75f965fb68e83e.png!small?1621330903646](https://image.3001.net/images/20210518/1621330903_60a38bd75f965fb68e83e.png!small?1621330903646)

## 0x04 番外：Cobalt Strike去特征技术

### 服务器去特征：修改默认配置

默认的服务器配置很容易被溯源，MS08067团队发表了[Cobaltstrike去除特征](https://www.secpulse.com/archives/148377.html)，通过修改
**默认端口** 、 **默认证书** 的方式可以避免被直接发现。

### 服务器去特征：域前置

可以通过CDN节点将流量转发到真实的C2服务器，其中CDN节点ip通过识别请求的Host头进行流量转，利用配置的域名的高可信度来绕过流量审计。

![1621330908_60a38bdc698e2dd3642a8.png!small?1621330908478](https://image.3001.net/images/20210518/1621330908_60a38bdc698e2dd3642a8.png!small?1621330908478)

可参考[使用CobaltStrike搭建域前置](https://www.moonsec.com/archives/2928)

### 流量去特征：Malleable C2 Profile

Cobalt Strike提供了可自定义的Malleable C2
Profile，可以自定义Beacon流量交互内容，可以把传输流量伪装成高信誉的网站，比如Google、baidu等，也可以把加密指令隐藏到cookie、url参数中，从而绕过流量审计。可参考官方文档[Malleable
Command and Control](https://www.cobaltstrike.com/help-malleable-c2)

### Beacon staging server去特征：修改stager异或密钥

在前文提到，Cobalt Strike的解密算法一直没变，区别只在于异或密钥的不同。零队安全研究团队在公众号上发表了[Bypass cobaltstrike
beacon config
scan](https://cloud.tencent.com/developer/article/1764340)，通过修改异或密钥的方式来防止配置文件被解析。

## 参考

[1] [Cobalt Strike｜Beacon原理浅析 - SecPulse.COM |
安全脉搏](https://www.secpulse.com/archives/124454.html)

[2] [What is a stageless payload
artifact](https://blog.cobaltstrike.com/2016/06/15/what-is-a-stageless-payload-artifact/)`

[3] [魔改CobaltStrike：免杀就像便秘一样 - 『病毒分析区』 - 吾爱破解 - LCG - LSG
|安卓破解|病毒分析|www.52pojie.cn](https://www.52pojie.cn/thread-1396671-1-1.html)

[4] [CobaltStrike4.0 远控分析 - 『病毒分析区』 - 吾爱破解 - LCG - LSG
|安卓破解|病毒分析|www.52pojie.cn](https://www.52pojie.cn/thread-1334525-1-1.html)

[5] [浅析CobaltStrike Beacon Staging Server扫描 - 安全客，安全资讯平台
(anquanke.com)](https://www.anquanke.com/post/id/224535?display=mobile)

[6] [Bypass cobaltstrike beacon config scan - 云+社区 - 腾讯云
(tencent.com)](https://cloud.tencent.com/developer/article/1764340)

[7] [深入研究cobalt strike malleable C2配置文件 - 先知社区
(aliyun.com)](https://xz.aliyun.com/t/2796)

[8] [关于Cobalt Strike检测方法与去特征的思考|NOSEC安全讯息平台 -白帽汇安全研究院](https://nosec.org/home/detail/4529.html)

[9] [Easily Identify Malicious Servers on the Internet with
JARM](https://link.zhihu.com/?target=https%3A//engineering.salesforce.com/easily-identify-malicious-servers-on-the-internet-with-jarm-e095edac525a)

[10] [利用JARM指纹进行TLS服务端标记_Hello
(sohu.com)](https://www.sohu.com/a/438444023_750628)

[11] [使用CobaltStrike搭建域前置 |
(moonsec.com)](https://www.moonsec.com/archives/2928)

[12] [Malleable Command and Control - Cobalt
Strike](https://www.cobaltstrike.com/help-malleable-c2)

