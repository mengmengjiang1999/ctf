**译者：知道创宇404实验室翻译组  
原文链接：<https://blog.talosintelligence.com/2021/11/attackers-use-domain-fronting-technique.html>**

## 摘要

Cisco Talos在2021年9月发现了一个新的恶意活动，攻击者使用了泄露的Cobalt Strike版本。 尽管Cobalt
Strike最初是作为合法工具创建的，但它仍然是安全工作者需要监视的东西，因为攻击者正在使用它来设置攻击。本例中的攻击者使用Cloudflare内容分发网络的域前置，将缅甸政府拥有的域定向到攻击者控制的服务器。攻击者采用在其攻击链中重新注册知名域的策略来逃避检测。
该攻击展示了MITRE
ATT&CK框架的几种技术，最显著的是T1202-间接命令执行，T1027-模糊文件或信息，T1105-入口工具传输，T1071.001-应用层协议：Web协议。

## 新的发现

Cisco Talos在2021年9月发现了一个恶意活动，攻击者使用一个模糊的Meterpreter储存器部署Cobalt
Strike信标。该攻击者使用缅甸政府拥有和运营的一个域名，即缅甸数字新闻网，作为其信标的域名前置。
这一威胁的演变表明，至少自2021年8月以来，攻击者就一直在活动，他们使用Meterpreter储存器和Cobalt
Strike信标，在受害者的端点上建立存在。

## 机制

恶意软件通常是一个加载程序，并在受害者设备上运行，通过反射注入解码并执行Cobalt Strike beacon
DLL。它在运行时加载多个库，并根据嵌入的配置文件生成信标流量。配置文件包含与指挥和控制（C2）服务器相关的信息，该服务器指示受害者的机器发送初始DNS请求，试图连接到缅甸政府拥有的域`www[.]mdn[.]gov[.]mm`的主机。该站点托管在Cloudflare内容分发网络后面，实际C2流量重定向到攻击者控制的服务器`test[.]softlemon[.]net`,该域是基于信标配置数据中指定的HTTP主机头信息

## 进展

Cobalt Strike过去曾被许多攻击者使用，是post-exploitation和pivot的事实上的标准工具。攻击者利用它部署范围广泛的有效载荷，从商品恶意软件到复杂的国家支持的攻击行为。 Cobalt
Strike允许攻击者改造信标的流量，以模拟合法的流量模式。域前置是一种通过DNS过滤隐藏流量的技术。域名代理使用合法或高声誉的域名来保证不被安全员发现。攻击者选择缅甸特定的域名作为域名前置可能表明他对该地区的地缘政治感兴趣。
在这次攻击中，攻击者使用MeterMeter
stager使用分段有效载荷，这表明信标将用于进一步的攻击。安全员应时刻保持警惕，监控网络流量，以检测Cobalt Strike活动，因为Cobalt
Strike是犯罪软件和APT组织最常用的攻击工具之一。

## 攻击的演变

一项关于该攻击演变的研究显示，攻击者正在尝试不同的主机组合，目的是完善域名前置技术。 2021年8月中旬左右发现的最早的信标包含C2
URI集，用于test[.]softlemon[.]net，而HTTP Get和Post请求头部指向dark-forest-002[.]president[.]workers[.]dev，这是一个Cloudflare无服务器workers域。请求的默认主机头配置包含主机名test[.]softlemon[.]net，最近的样本也在使用它。
2021年8月底发现的另一个样本由C2主机URI xxx[.]xxxx[.]tk和配置为指向test[.]softlemon[.]net的主机头设置组成。
从2021年9月开始，攻击者开始使用缅甸数字新闻域作为其信标的前置。虽然默认C2域指定为www[.]mdn[.]gov[.]mm，但信标的流量通过信标配置中指定的HTTP
Get和POST元数据重新定向到事实上的C2 test[.]softlemon[.]net。
攻击者可能在发起攻击之前更改了配置，用来测试其基础设施和域前置功能。基于信标配置模板和真实C2主机test[.]softlemon[.]net，我们有一定底气判断评估样本是由单个攻击者创建的。

![](https://images.seebug.org/content/images/2021/11/044266b2-0111-40bf-a244-ff50aa6daebd.jpg-w331s)
首次发现的恶意软件样本时间线

## Cobalt Strike信标配置

我们从负载中提取了beacon配置，该配置显示，攻击者在本次活动的不同恶意软件中使用了不同的用户代理、C2服务器和主机头值。
样本的信标配置通常有一个与Mozilla兼容的Windows 7用户代理。

![](https://images.seebug.org/content/images/2021/11/ac385008-0934-4f48-8cd2-1f2db80b374b.png-w331s)

![](https://images.seebug.org/content/images/2021/11/8fa4619b-2d7c-4929-af23-9a38836cb342.png-w331s)
信标中C2服务器、用户代理和事实上的C2变体

## 水印

Cobalt Strike水印是从许可证文件生成的数字，对于Cobalt
Strike许可证来说该水印是独有的。此攻击中使用的信标上的水印为305419896（十六进制：0x12345678）。
这一特定的水印之前被认为是泄露的Cobalt
Strike版本，其他恶意攻击者（如勒索软件Maze和Trickbot组织）使用这一水印也就不足为奇了，这使得基于水印编号判定归属变得不可能。很难评估先前注册的C2服务器过期域和泄露的Cobalt
Strike的使用是因为攻击者的操作安全意识增强还是可用资源有限。

## 域前置

这次攻击中的参与者使用了域名前置技术，这是一种可以使用著名域名来隐藏Cobalt Strike
C2流量的技术。在今天分析的案例种，攻击者使用了缅甸政府域名www.]mdn[.]gov[.]mm。
前置域名mdn[.]gov[.]mm是缅甸数字新闻（一家国有数字报纸）的合法域名。该网站曾于2月被缅甸兄弟会组织（一个民兵组织）攻破。虽然没有迹象表明缅甸兄弟会先前对该领域的诽谤与本文所述的攻击行为有关，但该域名本身显然引起了各路黑客的兴趣。
域前置可以通过恶意服务器和目标之间的重定向来实现。恶意参攻击者可能会滥用各种内容分发网络（CDN），将服务内容重定向到由攻击者控制的C2主机所服务的内容。Cloudflare是CDN服务之一，它为用户的服务器上托管的文件提供了一个全局分布式缓存。Cloudflare通过用于请求资源的FQDN进行标记分发。Cloudflare用户可以选择使用自己的子域并创建指向Cloudflare的DNS记录。此子域告诉Cloudflare将该DNS记录与特定分发相关联。
信标调用主页www[.]mdn[.]gov[.]mm,/api/3，并将主机头设置为实际的C2服务器test[.]softlemon[.]net。信标流量解析为Cloudflare
IP地址,引导流量到达该地址的DNS请求将丢失，并依赖于HTTP请求的其他部分，包括主机头和实际的C2 test[.]softlemon[.]net。

![](https://images.seebug.org/content/images/2021/11/9fd82e61-7f95-4801-a17e-782b633c4d1d.jpg-w331s)

## Cobalt Strike有效载荷

由于攻击者的域名前置技术使用了政府主机作为初始DNS诱饵，这些信标尤其令人感兴趣。此恶意软件使用的MITRE ATT&CK框架技术包括：

  * T1202-间接命令执行
  * T1027-模糊文件或信息
  * T1105-入口工具转移
  * T1071.001-应用层协议：Web协议

我们还分析了加载程序二进制文件，尝试找到其内存加载和功能的细节。
我们发现了一个可疑的部分`.kxrt`，其中包含打包和编码的恶意代码。该恶意软件在运行时链接多个函数，并具有MeterMeter暂存代码。
当恶意软件运行时，`.tls`部分首先运行，加载库并在`.kxrt`部分的入口点开始执行恶意代码。入口点代码调用函数在其自己的进程空间中分配虚拟内存。

![](https://images.seebug.org/content/images/2021/11/44e3f8bb-a7d4-4642-b139-461fb290fce1.png-w331s)
地址00401550处的函数显示虚拟内存的分配

加载程序接下来调用VirtualProtect函数，将虚拟内存页权限设置为读写执行，并写入将在新线程中执行的Cobalt Strike信标的映像库。

![](https://images.seebug.org/content/images/2021/11/12a5b070-7f04-40fa-a15c-6380c6261646.png-w331s)
函数将虚拟内存页权限设置为读写执行

我们发现两个库在运行时链接。除此之外，还有其他几个标准库在运行时与恶意软件链接。

![](https://images.seebug.org/content/images/2021/11/a1282066-2605-485f-adfe-b6a39438dd85.png-w331s)
在运行时加载库的函数

分配虚拟内存并将页面权限设置为读写执行后，将执行解密例程，对`.kxrt`部分中剩余的恶意代码进行解密并将其写入虚拟内存。

![](https://images.seebug.org/content/images/2021/11/41f1bb5a-fb53-40a9-836f-b8db36b92f81.png-w331s)
解密信标DLL的解码器例程

解密的恶意代码是实际的攻击信标。一旦解码，加载程序的执行跳转到DLL的开头，导致信标反射加载到加载程序进程内存中。该信标现在负责解码配置。

![](https://images.seebug.org/content/images/2021/11/4e1caed8-c4f0-4099-9a86-78b613315fb5.png-w331s)
从信标配置加载的信息的堆栈视图

信标通过调用`WinHTTPGetProxyForUrlEx`和`WinHTTPCreateProxyResolve`r绕过URL的代理来解析代理。

![](https://images.seebug.org/content/images/2021/11/926e54e2-94c4-46d7-9fa3-f070903a4e33.png-w331s)
用于解析URL的受害者系统代理的函数

此后不久，信标向C2服务器发起Cobalt
Strike信标通信。初始主机的DNS请求解析为Cloudflare拥有的IP地址，该地址允许攻击者使用域前置并将流量发送到实际的C2主机test[.]softlemon[.]net，该域名也由Cloudflare代理。
在分析时，样本C2主机基础设施未在线，我们收到404错误。

![](https://images.seebug.org/content/images/2021/11/07ce2637-da08-47e7-83ff-d877ce4eb7bf.png-w331s)
Cobalt Strike信标流量

信标使用的技术有GetTickCount、IsDebuggerPresent和NtDelayExecution调用检测调试器的，用来延迟恶意软件的执行，从而规避基于沙盒的动态分析系统。信标还可以管理系统电源策略注册表项，以设置最小和最大睡眠时间以及盖子打开和关闭操作策略。

![](https://images.seebug.org/content/images/2021/11/fa185618-3deb-44f0-9f04-7804c9260edb.png-w331s)
信标修改受害者在注册表中的系统电源和盖子打开/关闭策略

## 指挥与控制

C2服务器test[.]softlemon[.]网是softlemon[.]网的子域。直到2019年8月，softlemon[.]net域名才在谷歌域名下注册，并可能在那时候就过期了。该攻击者于2021年8月5日重新注册了该域。序列号为`4AA6AF6D719BFDD1C6DFF3D7B640AED7EE3`的域softlemon[.]net的SSL证书由免费SSL证书提供商Let's
Encrypt颁发。 Talos声誉引擎已将其归类为不受信任的域，Cisco
Umbrella在2021年9月显示DNS查询量激增。这一攻击与早些时候说明的Cobalt
Strike信标的演变是一致的。攻击者在9月初开始检测数字新闻领域前置的信标。

![](https://images.seebug.org/content/images/2021/11/41b77ecf-516f-42df-9568-45bfb69a283a.jpg-w331s)
test[.]softlemon[.]净查询与日期的DNS峰值

我们的研究发现C2 `test[.]softlemon[.]net`是一个运行Internet信息服务（IIS）的Windows服务器。

![](https://images.seebug.org/content/images/2021/11/3996c75f-f9a5-430f-93c5-bd391b48a7c3.png-w331s)
从主机test[.]softlemon[.]net提供的IIS服务响应

根据Shodan的说法，俄罗斯提供商托管的IP地址`193[.]135[.]134[.]124`可能是受Cloudflare基础设施保护的真实C2
IP地址，因为端口8443上提供的SSL证书属于Cloudflare，并将X509v3主体备选名称列为`DNS:*.softlemon.net`。

## 结论

域前置是攻击者利用DNS过滤规避保护的一种技术。在此攻击中，恶意Cobalt
Strike信标被配置为利用Cloudflare和其他内容分发网络使用的机制，去指示代理用于服务内容的主机。
当信标启动时，它将提交一个针对Cloudflare
infrastructure背后托管的合法高信誉域的DNS请求，并修改后续HTTPs请求标头，以指示CDN将流量定向到攻击者控制的主机。
安全员应监控其网络流量，甚至监控高信誉域的流量，以便使用Cobalt
Strike和其他攻击工具识别潜在的域正面攻击。XDR工具应部署到端点，以便检测Cobalt Strike装载程序和Meterpreter
储存器的行为，因为它们经常被各种攻击者使用。

## IOCs

### Hashes

    
    
    658d550322cefa6efc51fbfd1a3e02839d1e519a20f8f17f01c534c0eaf36f27
    e806e55713b9e46dc7896521ffb9a8b3abaa597147ea387ff2e93a2469546ba9
    a0aec3e9cb3572a71c59144e9088d190b4978056c5c72d07cb458480213f2964

## Network IOCs

### 主机

    
    
    test[.]softlemon[.]net
    dark-forest-002.president[.]workers[.]dev

### IP 地址

193[.]135[.]134[.]124[.]192

### URLs

hxxp://test[.]softlemon[.]net:8081/api/3 hxxp://test[.]softlemon[.]net/
tcp://test[.]softlemon[.]net:8080/ hxxps://193[.]135[.]134[.]124:8443
hxxp://193[.]135[.]134[.]124:8080 hxxp://193[.]135[.]134[.]124:8081

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1763/>

