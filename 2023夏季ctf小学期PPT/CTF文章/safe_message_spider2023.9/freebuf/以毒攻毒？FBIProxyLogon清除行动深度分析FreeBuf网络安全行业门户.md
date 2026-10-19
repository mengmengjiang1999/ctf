## 01 背景

 **2021年3月2日** ，美国微软在其安全博客发布文章[1]，文中第一次直接指出 **某黑客组织（代号: HAFNIUM）利用Exchange
0day对美国多个行业部门的实体进行攻击** ，包括传染病研究人员、律师事务所、高等教育机构、国防承包商、政策智库和非政府组织。

 **同日，** volexity公司发布安全公告[2]并 **将该系列漏洞利用取名ProxyLogon** 。 **3月3日**
，微软提前发布了该系列Exchange漏洞[3]的补丁。

此后，该事件得到全球黑客和网络安全从业者的广泛关注，其中ESET发现在
**微软发布及修补ProxyLogon漏洞之前，被嵌入恶意webshell的服务器不超过200台。** 但 **3月10日** 时，
**全球115个国家已有超过5000台伺服器含有恶意webshell。**

该漏洞的影响力和破坏力得到了美国执法部门的关注。 **4月13日** ，据公开新闻[4]，美国司法部有史以来首次授权FBI 通过 webshell
向受影响的服务器发出了一系列命令。这些命令可以使服务器删除 webshell 文件（由其唯一的文件路径识别）。

![](https://image.3001.net/images/20211101/1635735857_617f59314e7af06ef4815.png!small)

 **同日，** 司法部国家安全司助理司法部长 John Demers 在声明中说 ：“ 今天法院授权删除恶意
webshell，表明了司法部门在积极利用我们的法律工具。”

 **此次行动的其他技术细节仍然处于保密状态**
。至截稿，宁静之盾安全团队也未发现FBI发布更多相关信息。但根据已知信息，我们可以推断FBI在未经网站所有者授权的情况下使用了攻击技术去删除可能的webshell，简而言之就是
**以毒攻毒** 。

在注意到上述FBI的秘密行动后，宁静之盾团队随即针对此行动展开了技术溯源工作。经过数周努力，通过架设的蜜罐成功捕获了FBI此次行动所使用的未公开技术，成功复现了整个漏洞利用链。

## 02 调查

4月13日，上述新闻发布后，宁静之盾斩月安全实验室讨论了FBI可能采用的技术路线。结合公开新闻和对ProxyLogon漏洞的分析，推测FBI最有可能使用下述三种技术：

> 1．在获取到各黑客团伙此次攻击的webshell样本后，提取webshell中内置的明文密码，尝试远程访问webshell并清除；  
> 2．使用ProxyLogon漏洞清除后门；  
> 3．使用其它漏洞比如未公开的Exchange漏洞清除后门。

前两种技术路线都有很大的限制。对于第一种方式，很多webshell内置密码都是通过hash算法加密，不一定能够快速解密，并且有些APT组织的webshell中aspx文件名是随机的[5]。对于第二种方式，如果管理员被攻击后已经打了补丁则此种方式完全无效，同时Proxylogon漏洞在利用时需要一个有效且登陆过OWA的用户名。

同时，我们注意到微软在4月13日的星期二补丁日中发布了Exchange中的4个漏洞补丁（CVE-2021-28480至CVE-2021-28483），并且这些漏洞是由NSA发现并报告的！[6]

难道真的是巧合？当天的Exchange补丁让我们更有理由推测FBI使用了NSA提供的未公开漏洞，走了第三种技术路线。

随后我们根据三种技术路线，对蜜罐机做了针对性设置，同时也收集了大量利用ProxyLogon漏洞生成的webshell部署在蜜罐机上，不管FBI使用哪一种技术路线，我们都能在第一时间发现尝试清除已知webshell的行为。

 **最终我们通过Exchange HttpProxy 日志、Exchange 日志文件和专用监控程序发现了FBI
ProxyLogon清除行动所使用的技术细节，**
同时结合补丁比较对该未公开利用链进行了复现，该利用链共使用了三个在当时均是未公开状态的漏洞，分别是CVE-2021-34473/ 34523/
28482，这个利用链到现在同样没有公开分析。

其中比较有意思的是CVE-2021-34473这个SSRF漏洞，直到7月13日微软才发布安全公告，其实该漏洞早在4月份的补丁中就已被修复，该漏洞由台湾省的orange发现并用于今年4月的P2O大赛。

另外由于CVE-2021-34523到8月份才有公开分析，因此斩月安全实验室推迟了近半年才将FBI的此次行动技术细节完全公开。

## 03 技术分析

总结FBI行动中的漏洞利用链，与已公开的Proxyshell和Proxylogon最大的不同就是不需要账号（可使用administrator）、不需要写webshell直接高权限RCE，攻击成功后只要清除日志和28482创建的用户和会议请求，被攻击者就很难发现痕迹。

> 下文称该利用链为ProxyClean，使用了如下漏洞：  
> CVE-2021-34473：SSRF  
> CVE-2021-34523：Exchange PowerShell特权提升  
> CVE-2021-28482：反序列化漏洞

### CVE-2021-34473

CVE-2021-34473类似于ProxyLogon中的SSRF。当前端发起HTTP显式登录请求时，Exchange将删除邮箱地址部分然后路由到后端。显式登录是Exchange中的一项特殊功能，可让浏览器通过单个URL嵌入特定用户的邮箱。例如：https://exchange/OWA/user@test.com/Default.aspx

通过分析发现，Exchange并没有对邮箱地址进行足够的检查，我们可以在URL重建过程中通过参数删除URL部分字符串以访问任意后端URL。

![](https://image.3001.net/images/20211101/1635736798_617f5cde463d6113b94dc.png!small)

利用手法类似ProxyLogon，首先使用该SSRF获取管理员LegacyDN。

![](https://image.3001.net/images/20211101/1635736819_617f5cf3ba548b16ab99c.png!small)  
然后通过管理员用户的LegacyDN获取到管理员SID。

###
![](https://image.3001.net/images/20211101/1635736835_617f5d03ce41f683fa1d7.png!small)

###  
CVE-2021-34523

Exchange PowerShell Remoting是一项允许用户远程发送邮件、阅读邮件，甚至从命令行更新配置的功能。该功能建立在WS-Management之上，并实现了大量Cmdlet以实现自动化。但是，其授权部分仍然基于原始的CAS架构。

Exchange PowerShell Remoting通过X-CommonAccessToken请求头标识不同的用户，但是当PowerShell后端在当前请求中找不到X-CommonAccessToken标头时，它会尝试从URL请求参数X-Rps-CAT中反序列化并恢复用户身份。

所以可以使用Admin用户的SID序列化生成X-Rps-CAT参数，然后携带此参数访问Powershell接口，如此便可获取到Admin权限的远程Exchange Powershell会话权限。

###
![](https://image.3001.net/images/20211101/1635736852_617f5d14f2f04fed11069.png!small)

###  
CVE-2021-28482

CVE-2021-28482是今年4月份修补的一个漏洞，该漏洞位于Exchange
Server处理会议的组件中，是一个十分严重的反序列化漏洞。通过身份验证的用户可以利用该漏洞远程执行任意命令。

首先通过调试器拿到MeetingPollHandler处理过程的调用堆栈。

![](https://image.3001.net/images/20211101/1635736868_617f5d24b4f3400f6d174.png!small)  
继续分析发现反序列化创建PropertyBag对象时，对源数据没有作任何的安全限定。

![](https://image.3001.net/images/20211101/1635736878_617f5d2e500f0176510f1.png!small)  
由于反序列化生成对象没有任何限制，攻击者就能够使用ObjectDataProvider对象序列化生成XML类型的Gadget（可执行任意命令），然后将其插入到正常的XML中。最后将该XML发送给Exchange的会议处理接口上，即可完成RCE。

### ProxyClean

因为CVE-2021-28482需要至少一个Exchange用户的账号密钥，所以并不太好用。但另外两个漏洞却给CVE-2021-28482提供了必要的前置条件，将两者结合起来便可以做到远程执行命令且无需认证。

首先需要获取Exchange PowerShell会话权限。具体步骤是使用SSRF漏洞获取到管理员用户的SID，使用该SID制作管理员用户的X-Rps-CAT参数，携带该参数向Powershell接口POST序列化后的PowerShell命令。

由于远程Exchange
PowerShell基于WinRM协议，且该协议比较复杂，很难手动将PowerShell命令序列化后通过协议传输。故采取另一种简单的方案，转发协议数据。通过搭建HTTP代理，获取序列化后的Exchange
PowerShell命令，再添加X-Rps-CAT参数，最后转发给目标Exchange服务器。

![](https://image.3001.net/images/20211101/1635736900_617f5d4473be385a19ed9.png!small)  
搭建好WinRM代理后，通过本地的WinRM服务连接到代理服务器上。

![](https://image.3001.net/images/20211101/1635736914_617f5d520bda9d57fbd75.png!small)

此时的本地PowerShell窗口已经拥有了远程Exchange
Powershell会话权限，通过得到的Session即可管理远程的Exchange。我们使用New-Mailbox命令创建新的Exchange邮箱账户并查看结果。

![](https://image.3001.net/images/20211101/1635736930_617f5d623233622d89324.png!small)

![](https://image.3001.net/images/20211101/1635736937_617f5d69a49dfca35185c.png!small)

第二步，使用创建的账户通过ews/Exchange.asmx接口的认证，认证通过后向该接口POST会议数据，并保存返回的会议ItemID。最后使用ItemID向/owa/MeetingPollHandler.ashx接口发起GET请求，随即便会触发服务端反序列化精心构造的XML数据从而完成RCE。

![](https://image.3001.net/images/20211101/1635736954_617f5d7a1971e11adef23.png!small)

## 04 复现日志记录

### ExchangeLog

通过排查蜜罐机上的Exchange前端访问日志，可以还原ProxyClean完整的攻击链。

利用CVE-2021-34473获取管理员SID的前端访问日志

![](https://image.3001.net/images/20211101/1635736972_617f5d8c7a9452b230fb1.png!small)  
利用CVE-2021-34523执行远程Exchange PowerShell命令的前端访问日志

![](https://image.3001.net/images/20211101/1635736981_617f5d95e8db97bbf940a.png!small)  
利用CVE-2021-28482添加会议的前端访问日志

![](https://image.3001.net/images/20211101/1635736994_617f5da295db9fbc58fc1.png!small)  
利用CVE-2021-28482触发反序列化漏洞的前端访问日志

![](https://image.3001.net/images/20211101/1635737007_617f5daf79210e79c5da4.png!small)  
  
[点击查看演示录像](https://mp.weixin.qq.com/s?__biz=Mzg3NjY3MTE5Nw==&tempkey=MTEzN19PaG8yMGtlaHpnQTlrcjRXeUhhNXpHNjhySHpyRHVSUFE5MlVhTjRVR0JEb054M3JhUVJKU3RjaTYyS0xFZ3lDNElrYjdjeFJJODE5YURTWmpIV0pSVUo2VE5rTlhPa0ZEY2NKcnBqUUVVdTBHSVRGM29fUERqUW9IQURvbFliSy1zMnRQalBvcUZQTjhPcC05TW8wd2pmU0cwQUNJZlR5a2szMnFRfn4%3D&chksm=4f2ffb7e785872682b00f339c8870d8e839cb68734ce984c9d907e691bfdc7a0659238cd0881#rd
"查看演示录像")

## 05 结语

攻击与防御本是两位一体犹如太极阴阳两极。孤阴不生，孤阳不长，交通成和，万物化生。

斩月实验室常把“漏洞利用”比作利刃，带刀的可能是穷凶极恶的歹徒，也可能是嫉恶如仇的侠客。以攻击手段为防御体系作补全，不仅仅是文中的FBI，也是我们设计自动化渗透测试产品的基理。

通过这个案例可以看出，
**0day漏洞过度到时差型漏洞这个周期，对企业泛安全体系威胁性很大。自动化渗透测试产品以攻御防的主动防御方式，是企业防御体系的一个有效补全。**

### 参考链接

> [1]https://www.microsoft.com/security/blog/2021/03/02/hafnium-targeting-> exchange-servers/
>
> [2]https://www.volexity.com/blog/2021/03/02/active-exploitation-of-> microsoft-exchange-zero-day-vulnerabilities/
>
> [3] <https://jishuin.proginn.com/p/763bfbd5ac72>
>
> [4]https://threatpost.com/fbi-proxylogon-web-> shells/165400https://www.4hou.com/posts/o8KL
>
> [5]https://www.welivesecurity.com/2021/03/10/exchange-servers-under-> siege-10-apt-groups/
>
> [6]
> <https://zhuanlan.zhihu.com/p/364744970https://msrc.microsoft.com/update-> guide/en-us/vulnerability/CVE-2021-28480>

