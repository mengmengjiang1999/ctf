## 摘要

Cobalt Strike是一个渗透平台，供安全专业人员用于模拟高级黑客的定向攻击和后渗透行动。该工具由总部位于华盛顿的Strategic Cyber
LLC公司开发并授权，该公司对该工具的非法使用受到监管，并受到出口管制。尽管如此，Cobalt
Strike框架已经成为该类软件中的最热门的选择，其中包括Metasploit Pro、Core Impact等其他付费套件。在这类平台中，虽然Cobalt
Strike并不是唯一一个被盗版用户和网络罪犯使用的平台，但其已经被各种包括APT32在内的威胁集团使用，他们使用该工具进行初步渗透，而以同名命名的Cobalt集团也严重依赖该框架。

考虑到安全测试人员，更重要的是恶意攻击者，大量使用Cobalt Strike平台，识别Cobalt
Strike服务器连接到企业网络资产的必要性是显而易见的。

尽管检测方法已经公开，但仍由大量的Cobalt Strike服务器并没有打补丁，允许指纹识别和后续其他方式的探测。通过对在野的Cobalt
Strike服务器取样，并比较指纹识别的方法以帮助防御者更好地跟踪和监控该框架。追踪Cobalt Strike服务器可以帮助红队探测没有修改Cobalt
Strike默认配置蓝队的活动。

> 尽管补丁使得特定的指纹识别方法更加困难，Cobalt Strike服务器仍然相当暴露，相对容易被发现。许多Cobalt
> Strike服务器在补丁发布之前没有更新他们的系统，而新部署的使用了升级后的软件。
>
> 最近和部署的Cobalt Strike服务器更有可能部署更新的Cobalt
> Stike版本（超过3.12），同时继续使用默认的TLS证书，因此这仍然是一个可靠的检测机制。
>
> 当前Cobalt Strike服务器与历史威胁活动相比，大部分恶意和中立用户似乎都是用了默认的、未补丁的Cobalt
> Stike配置，也许是为了兼容其他Cobalt Stike服务器，或者仅仅因为默认设置运行良好因此使用者懒得改动什么东西。
>
> 对Cobalt Strike服务器的探测可以帮助防御者在其企业网络中建立预警机制，先于蓝队先发制人。

## 公开的Cobalt Strike服务器识别方法

2019年2月19日，Strategic Cyber LLC发布了[Cobalt Strike Team Server Population
Study](https://blog.cobaltstrike.com/2019/02/19/cobalt-strike-team-server-population-study/)。该研究的部分目的是调查Cobalt Strike软件的许可状态，并识别和分析对当前使用的软件版本所做的重大更改。

该研究确认了多种方法用于识别在野的Cobalt Stike服务器：

Cobalt Strike服务器附带默认的安全证书，除非管理员修改了默认证书，否则可以使用该默认证书进行指纹识别：

> SHA256: 87f2085c32b6a2cc709b365f55873e207a9caa10bffecf2fd16d3cf9d94d390c
>
> Serial Number: 146473198

当启用时，Cobalt Strike DNS服务器会响应任何DNS请求与bogon（假）IP：0.0.0.0 （这并不是CS服务器独有的特征）

Cobalt Strike服务器的默认控制端口是50050/TCP，这个端口在其他服务器上大部分不会打开。

Cobalt Strike服务器的”404 Not Found“ HTTP响应与NanoHTTPDweb服务器不同，并且能被探测到。

总的来说，上面列表中最可靠的方法是使用默认安全证书对Cobalt
Strike服务器进行指纹识别。其余的检测方法不太确定，所有方法与其他方法相互印证后都具有较高的置信度。例如，任何使用50050端口、同时提供NanoHTTP
web服务器特有的HTTP响应的服务器都更像是Cobalt Strike服务器，而不是仅显示HTTP响应签名的服务器。

## 基于NanoHTTPD响应的方法

Cobalt
Strike服务器基于NanoHTTPD，于2012年首次发布。NanoHTTPD是一个基于java的开源web服务器框架。NanoHTTPD服务器响应中包含一个额外的空字节："HTTP/1.1"后面是一个空字节（0x20），而在其他web服务器响应中不存在这个空字节。

![1](https://image.3001.net/images/20210107/1610002282_5ff6af6a03afeb1b30613.png!small)

2019年1月2日， Cobalt Strike 3.13版发布。Cobalt
Strike发布的[声明](https://www.cobaltstrike.com/releasenotes.txt)指出，与以前的版本相比，其中一个变化是“从HTTP状态响应中删除了无关的空字节”。

任何来自3.13之前的Cobalt Strike服务器的HTTP响应都包含这个空字节，可以使用扫描器检索HTTP响应来搜索它们。也可以手动对Cobalt
Strike服务器的连接抓包，可以很容易看到这个额外的空位。由于运行破解版本的Cobalt
Strike实例没有更新或打补丁，这种方法增加了发现恶意Cobalt Strike服务器的可能性。

安全公司Fox-IT于2019年2月26日发布了关于Cobalt Strike服务器的[研究](https://blog.fox-it.com/2019/02/26/identifying-cobalt-strike-team-servers-in-the-wild/)，该研究不仅提供了细节和如何识别3.13版本之前的服务器（对应HTTP响应中额外的空字符），还包括从[Rapid7](https://opendata.rapid7.com/)公开数据中从2015到2019年使用该检测方法发现的超过7000
Cobalt Strike 主机IP列表。

类似的，2019年2月27日，知道创宇安全研究团队发表了一篇[博客](https://medium.com/@80vul/identifying-cobalt-strike-team-servers-in-the-wild-by-using-zoomeye-debf995b6798)，详细介绍了他们使用Strategic Cyber LLC报告的NanoHTTPD 404 Not
Found响应异常以及空字节异常来识别Cobalt
Strike服务器。他们在ZoomEye的数据中发现的服务器更少，但仍然超过了3000台。知道创宇报告称，构建Cobalt
Strike的开源NanoHTTPD代码响应方式如下：

    
    
    HTTP/1.1 404 Not Found  
    Content-Type: text/plain  
    Date: Day, DD Mmm YYYY HH:MM:SS GMT  
    Content-Length: 0

知道创宇的检测逻辑就是基于这一发现。然而他们随后还观察到HTTP响应中的顺序实际上可能不同，在一些Cobalt Strike系统的响应中"Content-Type"在"Date"之后显示。

## 基于JA3指纹的检测方式

对于由详细网络流量数据的用户，JA3是一种更可靠的发现Cobalt
Strike服务器的方法。由三位Salesforce研究员开发的开源[JA3](https://github.com/salesforce/ja3)项目，可以通过对服务器和客户端之间的TLS协商进行指纹识别来检测可疑的HTTPS浏览。TLS/SSL版本、可接受的加密套件和elliptic
curve细节（如elliptic curve point格式）可以被做成指纹，就像浏览器可以被其他版本、附加组件和特定于该浏览器的其他特性指纹一样。

JA3签名用于客户端，而JA3S签名用于服务器。在Cobalt Strike的案例中，Client
beacon（使用Windows套接字来发起通信）和运行在Kali Linux上的Cobalt
Strike服务器的TLS协商已经有了[指纹](https://engineering.salesforce.com/tls-fingerprinting-with-ja3-and-ja3s-247362855967)。这些指纹需要一起使用才能可靠地发现Cobalt Strike服务器。尽管Cobalt
Strike使用者可以通过重定向来部分避开这种检测，但许多Cobalt Strike服务器并不使用这种代理。

JA3和JA3S签名可以与[Zeek/Bro](https://github.com/salesforce/ja3/tree/master/bro)和[Suricata](https://github.com/OISF/suricata/blob/master/src/util-ja3.c)等工具一起使用。来自这些网络检测工具的数据可以随后输入到诸如Splunk这样的SIEM中。JA3和JA3S的签名可以从[Salesforce’s
Github
account](https://github.com/salesforce/ja3/tree/master/lists)和其他[sources](https://sslbl.abuse.ch/ja3-fingerprints/)获得。

### JA3

Cobalt Strike默认的SSL/TLS证书是固定的，所以一般都是使用这个证书作为特征值来发现Cobalt
Strike服务器，服务端传给客户端的SSL默认证书有很明显的特征：

    
    
    C=Earth，ST=Cyberspace，L=Somewhere，O=CobaltStrike，OU=AdvancedPenTesting，CN=Major CobaltStrike

![img](https://image.3001.net/images/20210107/1610002514_5ff6b0526cdab8432c8dd.png!small)

JA3方法用于收集Client
Hello数据包中以下字段的十进制字节值：版本、可接受的密码、扩展列表、椭圆曲线密码和椭圆曲线密码格式。然后将这些值串联到一起，在使用“,”分割开各个字段，同时用“-”来分隔各个字段中的各个值。

![img](https://image.3001.net/images/20210107/1610002516_5ff6b0542dd729fdc74f0.png!small)

这些字段的顺序如下：TLS版本信息、可接受的密码、扩展列表、椭圆曲线密码和椭圆曲线密码格式。

用CobaltStrike4.1的连接流量举例。

![img](https://image.3001.net/images/20210107/1610002519_5ff6b057a11e241d46798.png!small)

771,49188-49192-61-49190-49194-107-106-49162-49172-53-49157-49167-57-56-49187-49191-60-49189-49193-103-64-49161-49171-47-49156-49166-51-50-49196-49195-49200-157-49198-49202-159-163-49199-156-49197-49201-158-162,67,,11-2-256(如果无上述字段，则这些字段的值为空)

然后会计算这些字符串的MD5哈希值，以生成易于使用和共享的长度为32字符的指纹，他们就是JA3
TLS客户端的指纹。比如上述CobaltStrike4.1客户端指纹：fa704723a210632b2ff9ad03be418651

### JA3S

创建JA3后，就可以使用同样的方式对TLS的服务端进行指纹识别，即对TLS Server Hello信息进行指纹识别。JA3S会收集Server
Hello数据包中以下各个字段的十进制字节值：版本、可接受的加密算法和扩展列表，然后将这些值串联起来，使用“,”来分隔各个字段，使用“-”分隔每个字段中的各个值。

这些字段的顺序如下：TLS版本信息、可接受的密码、扩展列表

![img](https://image.3001.net/images/20210107/1610002522_5ff6b05a030af323d8577.png!small)

CobaltStrike4.1的服务端：771,49192,9-------->5513ab2983a0db88fadd353de0341e7c

同一台服务器会根据Client Hello信息机器内容以不同的方式创建Server
Hello消息，因此这里不能跟JA3那样，仅仅根据服务器的Hello消息来对其进行指纹识别。尽管服务器对不同客户端的响应不同，但是他们对同一客户端的响应总是一致的。

比如：客户端正在发送TLS Client
Hello数据包，其中数据都是A。因此，服务器会的响应的内容也是由A构成，并将始终用A来提供同样的响应。与此同时，另一个客户端也在发送数据包，并且内容都是B。类似的，服务器现在会用B进行响应，并且总是用B组成的B串进行响应。可以看到，对于不同的客户端，服务器会给予不同的响应，但是对于每个客户端来说，总是以相同的方式进行相应。

![img](https://image.3001.net/images/20210107/1610002524_5ff6b05c4289bc94c2fd2.png!small)

在这个日志输出中，JA3位于左侧，JA3S位于右侧，使用同一客户端与同一服务器交互了4次。然后，再次使用不同的客户端进行了4次以上的交互。不难发现，服务器的响应方式对于同一客户端总是相同的，但对于不同的客户端却是不同的。

例如，MetaSploit 的 Meterpreter 和 CobaltStrike（并非4.1版本） 的 Beacon 都使用 Windows
套接字来启动 TLS 通信。在 Windows 10 上，JA3=72a589da586844d7f0818ce684948eea（指定 IP
地址），JA3=a0e9f5d64349fb13191bc781f81f42e1（指定域名）。由于 Windows
上的其他普普通通的应用程序也使用相同的套接字，因此，我们很难识别其中的恶意通信。但是，Kali Linux 上的 C2 服务器对该客户端应用程序的响应方式与
Internet
上的普通服务器对该套接字的响应方式相比来说是独一无二的。尽管服务器对不同客户端的响应不同，但它们对同一客户端的响应总是一致的。因此，如果结合
ja3+ja3s，就能够识别这种恶意通信，而不用考虑目的地 IP、域名或证书等细节信息。

## 基于JARM的检测方式

### 介绍

近期，Salesforce研究人员发布了一篇名为[Easily Identify Malicious Servers on the Internet
with
JARM](https://link.zhihu.com/?target=https%3A//engineering.salesforce.com/easily-identify-malicious-servers-on-the-internet-with-jarm-e095edac525a)的文章，并在github上发布了一个[JARM扫描工具](https://link.zhihu.com/?target=https%3A//github.com/salesforce/jarm)，相关内容引起了国外部分研究人员的讨论。

JARM是一个主动TLS服务端指纹工具，主要用途如下：

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
> 用户自定义配置
>
> ……

而前文提到，TLS服务器对不同客户端的响应不同，但是他们对同一客户端的响应总是一致的。因此不能跟JA3那样，仅仅根据JA3S对服务器进行指纹识别。

而JARM采取了一种类似fuzz的方式，主动向TLS服务器发送10个TLS Hello数据包并对Server
Hello中的特定字段进行分析，以特定方式对10个TLS服务器响应进行哈希处理，最终生成JARM指纹。

JARM中的10个TLS客户端Hello数据包经过特殊设计，目的就是提取TLS服务器中的唯一响应。例如：

> JARM以不同的顺序发送不同的TLS版本，密码和扩展；
>
> TLS Clint将密码从最弱到最强排序，TLS Server将选择哪种密码？
>
> ……

总之JARM与我们在进行流量分析威胁时常用的JA3、JA3/S不同：

> JA3、JA3/S主要基于流量，服务器面对不同客户端产生不同的JA3S指纹。
>
> JARM则是完全主动的扫描并生成指纹，服务器可以生产唯一的JARM指纹。

### 利用JARM识别C2的问题

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
  
在理想情况下如果JARM与C2唯一对应，那么我们就多了一种主动发现C2节点的特征。

然而，360Quake团队在验证时，搜索Cobalt Strike对应的JARM发现了2338个独立IP，但TOP5的应用为：

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
Strike拥有相同的JARM指纹，这也解释了为什么会有那么多的Weblogic和Tomcat应用被识别出来了。

因此不能直接通过JARM去判定CobaltStrike；同样，对于CobaltStrike而言JARM也并不唯一，其JARM与不同JDK环境下TLS服务有关。JARM仅仅是一种TLS服务端特征的标识方式，只能作为一个辅助手段，不能完全被用作Web上层应用的唯一指纹。

Quake团队提取了部分CobaltStrike服务器的JARM数据放置在Quake的开源仓库中，仅供业界研究使用（不作为精准威胁情报）：[CobaltStrike-JARM](https://link.zhihu.com/?target=https%3A//github.com/360quake/CobaltStrike-JARM)

## 参考

> [https://www.recordedfuture.com/cobalt-strike-> servers/﻿](https://www.recordedfuture.com/cobalt-strike-servers/)
>
> <https://www.secpulse.com/archives/124454.html>
>
> <https://www.secrss.com/articles/24765>
>
> <https://my.oschina.net/u/3896378/blog/4555703>
>
> <https://link.zhihu.com/?target=https%3A//engineering.salesforce.com/easily-> identify-malicious-servers-on-the-internet-with-jarm-e095edac525a>
>
> [https://wangzhan.360.cn/296.html﻿](https://wangzhan.360.cn/296.html)

