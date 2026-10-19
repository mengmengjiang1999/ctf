**趋势科技在本周发表的一篇博文中指出，其研究人员已经发现了一个新的[漏洞利用工具包](https://www.trendmicro.com/vinfo/us/security/definition/exploit-kit)（Exploit Kit），并将其命名为Underminer。Underminer
EK使用了其他漏洞利用工具包所具备的功能，以阻碍安全研究人员追踪其活动或对其有效载荷进行逆向工程。**

Underminer EK交付了一个会感染系统的引导扇区的bootkit程序，以及一个名为Hidden
Mellifera的加密货币挖掘恶意软件。值得注意的是，Underminer
EK通过加密传输控制协议（TCP）隧道来传递恶意软件，并使用类似于ROM文件系统格式（romfs）的自定义格式打包恶意文件。这些技巧的应用使得对漏洞利用工具包及其有效载荷的分析变得极为困难。

基于Underminer EK的活动开始于7月17日，其有效载荷主要被分发给了亚洲国家。加密货币挖掘恶意软件Hidden
Mellifera于5月份[出现](http://www.freebuf.com/column/174581.html)，据[报道](http://www.freebuf.com/column/175106.html)影响了多达50万台设备。另外，Hidden
Mellifera的开发者也被证实与2017年8月被报道的劫持浏览器的木马Hidden Soul存在关联。这种关联性表明，Underminer
EK也是由同一伙网络犯罪分子开发的，因为Underminer EK也推送了Hidden Mellifera。据称，Underminer
EK是通过一个广告服务器分发的，而该服务器的域名则使用Hidden Mellifera开发者所持有的电子邮件地址注册。

![UnderminerEK活动的地理位置分布](https://image.3001.net/images/20180727/1532675298_5b5ac4e24bbed.png!small)

图1. UnderminerEK活动的地理位置分布，从7月17日到7月23日

## Underminer EK的功能

Underminer EK配备了其他漏洞利用工具包所具备功能：浏览器分析和筛选、防止客户端重访、URL随机化和有效载荷的非对称加密。Underminer
EK的登录页面可以通过用户代理对用户的Adobe Flash
Player版本和浏览器类型进行分析和检测。如果客户端的配置文件与其感兴趣的目标不匹配，则不会交付恶意内容，并将受害者重定向到一个常规网站。Underminer
EK还为浏览器cookie设置一个令牌，如果受害者已经访问了漏洞利用工具包的登录页面，则不会推送有效载荷，而是会传递HTTP
404错误消息。这可以防止Underminer
EK重复攻击同一个受害者，也可以阻碍研究人员通过重新访问他们的恶意链接来重现攻击。不仅如此，Underminer
EK还可以随机化在攻击中使用的每个URL中的路径，以规避传统防病毒（AV）解决方案的检测。

![UnderminerEK利用CVE-2016-0189
的流量模式](https://image.3001.net/images/20180727/1532675327_5b5ac4ff2c88c.png!small)![UnderminerEK利用CVE-2015-5119和CVE-2018-4878的流量模式](https://image.3001.net/images/20180727/1532675316_5b5ac4f434bab.png!small)

图2. UnderminerEK利用CVE-2016-0189（上）、CVE-2015-5119和CVE-2018-4878（下）的流量模式

## Underminer EK如何隐藏其漏洞利用

Underminer EK使用RSA加密来保护其漏洞利用代码，并防止其流量被重放。在利用漏洞之前，Underminer
EK会先生成一个随机密钥，并将其发送到其命令和控制（C＆C）服务器。然后，这个密钥用于加密其JavaScript代码和漏洞利用代码，在HTTP响应标头“X-Algorithm”中指定对称加密算法，并将其发送回受害者。在我们的测试中，其使用的对称算法是RC4或Rabbit。

在收到响应后，Underminer EK将使用生成的密钥解密代码并执行它。Underminer
EK还在密钥传输过程中使用了RSA加密来进一步保护它（随机密钥是使用嵌入在其代码中的公钥加密的）。它只能通过一个私钥解密，这个私钥只有Underminer
EK的运营商才知道。即使可以看到漏洞利用工具包的网络流量，或者手边有文件样本，也无法对漏洞利用有效载荷进行解密。这种技术类似于其他漏洞利用工具包所使用的技术，特别是[Angler](https://securelist.com/attacking-diffie-hellman-protocol-implementation-in-the-angler-exploit-kit/72097/)、
[Nuclear](https://blog.trendmicro.com/trendlabs-security-intelligence/how-exploit-kit-operators-are-misusing-diffie-hellman-key-exchange/)和[Astrum](https://blog.trendmicro.com/trendlabs-security-intelligence/astrum-exploit-kit-abuses-diffie-hellman-key-exchange/)，但它们使用的是Diffie-Hellman算法。

![使用RSA公钥加密随机密钥的JavaScript代码片段](https://image.3001.net/images/20180727/1532675339_5b5ac50bb262b.png!small)

图3. 使用RSA公钥加密随机密钥的JavaScript代码片段

## Underminer EK的漏洞利用

Underminer EK使用了几个也被其他[漏洞利用工具包](https://blog.trendmicro.com/trendlabs-security-intelligence/rig-exploit-kit-now-using-cve-2018-8174-to-deliver-monero-miner/)和[威胁参与者](https://www.trendmicro.com/vinfo/us/security/news/vulnerabilities-and-exploits/north-korean-hackers-allegedly-exploit-adobe-flash-player-vulnerability-cve-2018-4878-against-south-korean-targets)所使用的安全漏洞：

> [CVE-2015-5119](https://blog.trendmicro.com/trendlabs-security-> intelligence/unpatched-flash-player-flaws-more-pocs-found-in-hacking-team-> leak/)，一个存在于 AdobeFlash Player中的释放后重用（use-after-> free）漏洞，于2015年7月被[修补](https://helpx.adobe.com/security/products/flash-> player/apsa15-03.html)。
>
> [CVE-2016-0189](https://blog.trendmicro.com/trendlabs-security-> intelligence/may-2016-patch-tuesday-fixes-browser-scripting-engine-> flaws/)，一个InternetExplorer（IE）内存损坏漏洞，于2016年5月被修补。
>
> [CVE-2018-4878](https://blog.trendmicro.com/trendlabs-security-> intelligence/february-patch-tuesday-bouquet-fixes-privilege-escalation-> vulnerabilities/)，存在于AdobeFlash Player中的一个释放后重用（use-after-> free）漏洞，于2018年2月被修补。

在使用这些漏洞时，会执行一个恶意软件加载程序。每一个都有类似的感染链，但在执行上有所不同。在使用CVE-2016-0189时，将通过regsvr32.exe执行一个包含JScript代码的scriptlet（.sct文件）。JScript代码将释放一个将要使用rundll32.exe执行的动态链接库（DLL），该库将从漏洞利用工具包加载并执行第二阶段的downloader。

当使用Flash漏洞时，Underminer将直接执行shellcode以下载一个没有MZ标头的可执行文件。这类似于从scriptlet中释放的第一个loader或DLL。loader将检索相同的第二阶段的downloader，然后将其注入新打开的rundll32.exe进程。在恶意软件被安装到系统中之前，Flash漏洞的感染链实际上以无文件形式进行的。在趋势科技发布的[技术摘要](https://documents.trendmicro.com/assets/tech-brief-new-exploit-kit-underminer-delivers-bootkit-and-cryptocurrency-mining-malware.pdf)中，他们进一步解释了第二阶段downloader如何通过一个加密的TCP隧道交付bookit和加密货币挖掘恶意软件。

![UnderminerEK的漏洞利用的感染流程](https://image.3001.net/images/20180727/1532675356_5b5ac51c5d662.png!small)

图4. UnderminerEK的漏洞利用的感染流程

在这份[技术摘要](https://documents.trendmicro.com/assets/tech-brief-new-exploit-kit-underminer-delivers-bootkit-and-cryptocurrency-mining-malware.pdf)中，你可以找到趋势科技对Underminer EK感染链的详细分析以及IoCs。

 ***参考来源：[趋势科技](https://documents.trendmicro.com/assets/tech-brief-new-exploit-kit-underminer-delivers-bootkit-and-cryptocurrency-mining-malware.pdf)，Hydralab 编译整理，转载请注明来自 FreeBuf.COM**

