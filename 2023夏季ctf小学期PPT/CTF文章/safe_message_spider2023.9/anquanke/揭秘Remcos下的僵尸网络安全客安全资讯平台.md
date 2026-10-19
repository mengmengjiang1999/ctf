# 揭秘Remcos下的僵尸网络

阅读量 **291184**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-09-06 16:30:30

 **x**

##### 译文声明

本文是翻译文章，文章来源：talosintelligence.com

原文地址：<https://blog.talosintelligence.com/2018/08/picking-apart-remcos.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t014f347e1819cba941.jpg)

## 一、概述

思科Talos团队最近发现多起使用Remcos远程控制工具的事件，该工具由一家名为Breaking
Security的公司出售，虽然该公司表示他们出售的软件只能用于合法用途，对于不遵守其最终用户许可协议的用户将撤销其许可证。但远程控制工具的贩卖给攻击者建立一个潜在的僵尸网络提供了所需的一切条件。

每个Remcos许可证的价格从58欧元到389欧元不等。Breaking
Security还支持用户使用数字货币进行支付。这种远控可以完全控制和监测任何Windows XP及其之后的包括服务器在内的Windows系统。

除了Remcos之外，Breaking Security还提供一种名为Octopus
Protector的加密工具，它可以通过加密磁盘软件的方式使恶意软件绕过反恶意软件产品的检测。在YouTube的Breaking
Security频道上展示了这款工具绕过反病毒软件的能力。这个公司还提供一种键盘记录器，它具有记录和发送功能。还有可以发送大量垃圾邮件的邮件系统以及可以发送命令控制C2通信的DynDNS服务。当这些和Remcos相结合，就提供了构建一个持久性僵尸网络的基础设施。

在思科的高级恶意软件防护（AMP）系统内，我们监测到了几种尝试在各终端安装此RAT的实例。我们还看到许多恶意软件散布Remcos的行为，这些行为使用不同的方法绕过检测。为了帮助那些感染Remcos的受害者，思科Talos团队提供了一个从二进制文件中提取C2服务器地址及其他信息的[脚本](https://github.com/Cisco-Talos/remcos-decoder/blob/master/remcos_decryptor.py)。详细信息请看下面的技术细节部分。

## 二、Remcos在野利用

由于Remcos在许多与黑客相关的论坛上进行广告宣传和销售，我们观察到几起恶意软件尝试传播Remcos给大量受害者的活动。我们认为大量不相关的攻击者利用这种软件，使用不同的方式去感染系统。今年早些时候，RiskIQ发布了一份关于一名攻击者的报告，这名攻击者的目标是土耳其国防承包商。从那之后，这个攻击者持续活动，并把目标指向特定类型的组织。我们确信，除了国防承包商，这名攻击者还把以下组织作为目标，如：

  * 国际新闻机构
  * 柴油机设备制造商和海事及能源部门服务提供商
  * 能源部门的HVAC服务提供商

在观察到的活动中，攻击始于用土耳其语编写的特制鱼叉式钓鱼邮件，这些邮件看起来像土耳其政府部门发的，声称与受害组织的税务报告有关。下面是其中的一份邮件，作为示例：  
攻击者尽力使邮件看起来更像是来自Gelir İdaresi Başkanlığı
(GIB)的官方邮件，土耳其税务局在财政部下运作，负责处理土耳其的税务事务。邮件甚至还包括官方GIB图形和底部的文本，这些文字翻译后为：  
 _“感谢您参与[税务局]电子邮件服务的电子邮件通知系统。此消息包含已被GIB邮件通知系统发送给您。请不要回复此邮件。”_

和其他的鱼叉式钓鱼攻击一样，恶意的Microsoft
Office被附加在邮件内。大部分的文档为Excel表格，我们观察到使用Word文档攻击时，许多情况下，文档的内容会被故意模糊，来诱使受害者开启宏来查看文档。下面是一个活动中发现的，伪装成税款单的Word文档。  

我们分析的大多数Excel表格都是空白的，只有以下的图片和警告，用土耳其语提示用户开启宏。  

我们还观察到一些针对英文用户的活动，下面是一个恶意附件，看起来像是西班牙的旗舰航空公司lberia的发票。  

除了以lberia为主题的恶意文档，我们还发现了与波兰航空公司AMC有关的大量恶意文档，如下是用Excel和Word制作的行程诱导图。  

如RiskIQ所报道，包含小的可执行文件的宏以数组的方式被嵌入文档，一旦执行，宏重构可执行文件，将其保存到系统的特殊的位置并执行它，指定的文件位置会在恶意文档中发生更改，包括恶意软件作者常用的目录，例如％APPDATA％和％TEMP％。可执行文件名也会在文档中更改。

提取的可执行文件很简单，被作为Remcos恶意软件的下载程序。它是一个很普通的程序，用于从攻击者控制的服务器检索Remcos并执行它，从而感染系统。下面是一个例子：  

Remcos是一个强大的RAT，可在被感染的系统执行键盘记录，远程截屏，文件管理，命令执行等多个功能，一些情况下，除了Remcos，还检测到一些与这些活动相关的分发服务器上寄存了几个恶意二进制文件。

## 三、谁是Remcos的幕后推手？

正如前面所提到，名为Breaking
Security的公司在官网出售Remcos及其他一些可疑的软件。在官网上，没有这家公司的细节信息或幕后人信息，但在官网列出了增值税号码来说明公司已经在德国注册。有趣的是，你可以在几乎任何欧盟（EU）国家/地区查找公司的名称和地址网站。但考虑到个人隐私，德国并不会公布这项信息。由于Breaking
Security已在德国注册，因此我们无法确定该公司背后的个人姓名和地址。尽管如此，我们还是能够鉴别一些特征，让我们了解谁可能是公司背后的人。  

公共和私人增值税项目的比较

Breaking
Security的域名目前在Cloudflare上托管，可以隐秘的保护注册信息。我们费了很大的功夫去解密谁在这家公司幕后以及和这些软件有关。通过分析，我们可以找到一些有关这个公司幕后人的个人线索，但也可能是错误的或者是攻击者在互联网上故意构造的虚假信息。

我们首先证实的是如Viotto Keylogger截图所示的邮箱和域名。

  * logs[@viotto](https://github.com/viotto "@viotto")[.]it
  * viotto-security[.]net

![](https://p0.ssl.qhimg.com/t01ee0e315b0922896f.png)

虽然viotto-security[.]net域名服务器的注册信息受到和breaking-security[.]net一样的保护。域名viotto[.]it在”Sender’s e-mail”无法找到。但这个域名相关的Whois信息如下图所示：

因为这些数据在很多地方已经公开，所以我们不对它做模糊化处理。我们还通过从网站收集的数据确定了REMCOS作者似乎经常使用的其他的email,
jabber和xmpp地址:

  * viotto[@null](https://github.com/null "@null")[.]pm
  * viotto24[@hotmail](https://github.com/hotmail "@hotmail")[.]it
  * viotto[@xmpp](https://github.com/xmpp "@xmpp")[.]ru

很多情况下，很多被调查的域名采用了Cloudflare的服务，这通常会隐藏服务器托管域的真正地址。因为DNS配置通常将名称解析指向Cloudflare
IP而不是Web服务器本身的IP。一个常见的错误是，虽然域本身可能受Cloudflare保护，但在许多情况下，存在一个不指向Cloudflare服务器的子域，允许取消屏蔽服务器IP地址。

这是breaking-security[.]net的情况，虽然域被Cloudflare保护，但邮件子域没有被保护，邮件子域的A记录配置如下：

  * mail[.]breaking-security[.]net. A 146.66.84[.]79
  * webmail[.]breaking-security[.]net A 146.66.84[.]79

146.66.84[.]79这个IP被托管在SiteGround Amsterdam.经过一系列测试，我们确定这也是breaking-security[.]net的主要托管地址。

另一个我们证实的与Remcos相关的域名是viotto-security[.]net.，这个域名目前被配置重定向到breaking-security[.]net，然而，情况并非总是如此。在Wayback
Machine中搜索与该域相关联的页面，这个站点允许使用者浏览网页过去的版本，并以个人传记的方式展现，和出售各种工具的大公司的利益有明显的重叠：  

我们还找到了Viotto在黑客论坛上打的几个广告，自2016年后，他在HackForums等黑客论坛上出售或支持Remcos。这使得他的意图很可疑。  
  

尽管这家公司声明如果用户使用Remcos做违法活动，将撤销其许可证。如下图，有人在官方声明下声称使用该软件控制了200台肉鸡，但官方却似乎毫不在意。  
  
  
  

Viotto在其他黑客论坛也很活跃，像OpenSC，他是版主，以下是他宣传Remcos 和Octopus Protector的帖子。  
  

## 四、Remcos的技术细节

根据[其他博客](https://krabsonsecurity.com/2018/03/02/analysing-remcos-rats-executable/)的描述，Remcos看起来是用C++开发的。  

从发布说明来看，它目前仍很活跃，作者几乎每个月都在更新。  
v2.0.5 – July 14, 2018  
v2.0.4 – April 6, 2018  
v2.0.3 – March 29, 2018  
v2.0.1 – Feb. 10, 2018  
v2.0.0 – Feb. 2, 2018  
v1.9.9 – Dec. 17, 2017

Remcos具有RAT的典型功能，它可以隐藏在系统中，使用恶意软件技术，使普通用户难以察觉到它的存在。

一些常规模块看起来像拷贝或对开源代码的轻微修改，下面的反调试代码块是个很好的例子：  

这是检测早已过时的“SbieDll.dll”在我们看来，现在很少有分析人员使用沙盒。进一步分析可以看出很多其他功能代码与开源项目代码有很高的相似度。下面是Remcos的VMware检测代码：  

下面的样例代码来自[aldeid.com](https://www.aldeid.com/wiki/VMXh-Magic-Value):  

上面提到的博客已经详细描述几个Remcos功能特性。我们关注Remcos如何实现加密。在需要加解密数据时，它几乎全部使用的RC4算法。如注册入口，C2服务器通信，文件路径等：  

Exepath注册数据用base64编码。RC4加密，解密后可得到可执行文件路径：  
C:TEMP1cc8f8b1487893b2b0ff118faa2333e1826ae1495b626e206ef108460d4f0fe7.exe

RC4的实现遵循标准RC4算法，在网上可以找到很多样例代码，下面是第一次在00402F01设置密钥调度算法(KSA) S_array。  

转换为典型的RC4伪代码如下：

    
    
    for i from 0 to 255
            S[i] := i
    endfor
    j := 0
    for i from 0 to 255
            j := (j + S[i] + key[i mod keylength]) mod 256
            swap values of S[i] and S[j]
    endfor
    

在00402F5B是对RC4伪随机数生成算法的实现：  

其伪代码如下：

    
    
    i := 0
    j := 0
    while GeneratingOutput:
            i := (i + 1) mod 256
            j := (j + S[i]) mod 256
            swap values of S[i] and S[j]
            K := S[(S[i] + S[j]) mod 256]
            output K
    endwhile
    

如截图所示，Remcos使用RC4算法加解密数据，使用PE资源块中的’SETTINGS’存储初始加密密钥。这个密钥是可变的，从40字节到250字节不等。  

存储数据的格式如下：

  * 密钥长度
  * 加密密钥
  * 加密配置数据

被加密的配置数据块包括命令和控制服务器，RAT命令及其他数据，如下图：  

加密数据包括C2服务器e.g.
ejiroprecious[.]ddns[.]net和通信端口号，以及密码，此密码用于为RC4加密的C2通信生成单独的S_array。下面是RC4密钥调度算法（KSA）相关代码：  

即使使用比上例更强的密码，使用这种弱加密算法意味着每个人都可以提取密码并解密C2流量或将自己的命令注入C2通道控制RAT。好消息是，成为Remcos受害者的公司可以通过存储网络的流量和Remcos二进制文件对威胁进行分析。

为了使取证人员更轻松，我们提供了一个简单的[Python解码器脚本](https://github.com/Cisco-Talos/remcos-decoder/blob/master/remcos_decryptor.py)，可以解码资源部分的配置数据：  

如上所述，Remcos对各种其他功能也使用相同的加密例程。因此，解码器程序还提供了手动切换加密字节的选项。这可以用于解码，例如exepath的注册表键值。

我们使用此工具提取下面的所有IOC。它使用最新的2.0.4和2.0.5版本的Remcos进行测试，但也可能适用于其他版本。  

用户还可以将字节从网络嗅探器复制到二进制文件，通过解密C2通信中的字节，来查看C2服务器发送给受害者的命令。请记住使用提取的密码，例如“通过”。  

## 五、结论

虽然销售Remcos的公司声称该应用程序仅供合法使用，但我们的研究表明它仍然被恶意攻击者广泛使用。在某些情况下，攻击者战略性地选择目标，试图进入各种关键基础设施部门供应链上的机构。机构应确保实施安全控制以对抗Remcos以及其他威胁。Remcos是一个强大的工具，正在积极开发，增加攻击者可以获取更多信息的新功能。为了与其对抗，各机构应该意识到这种威胁以及可能在互联网上传播的相关威胁。

## 六、IOCs

恶意文档：  
0409e5a5a78bfe510576b516069d4119b45a717728edb1cd346f65cfb53b2de2  
0ebfbcbf8c35ff8cbf36e38799b5129c7b70c6895d5f11d1ab562a511a2ec76e  
18f461b274aa21fc27491173968ebe87517795f24732ce977ccea5f627b116f9  
2f81f5483bbdd78d3f6c23ea164830ae263993f349842dd1d1e6e6d055822720  
3772fcfbb09ec55b4e701a5e5b4c5c9182656949e6bd96bbd758947dfdfeba62  
43282cb81e28bd2b7d4086f9ba4a3c538c3d875871bdcf881e58c6b0da017824  
48dec6683bd806a79493c7d9fc3a1b720d24ad8c6db4141bbec77e2aebad1396  
4938f6b52e34768e2834dfacbc6f1d577f7ab0136b01c6160dd120364a1f9e1a  
4e0bcef2b9251e2aaecbf6501c8df706bf449b0e12434873833c6091deb94f0e  
72578440a76e491e7f6c53e39b02bd041383ecf293c90538dda82e5d1417cad1  
77cf87134a04f759be3543708f0664b80a05bb8315acb19d39aaa519d1da8e92  
8abcb3084bb72c1cb49aebaf0a0c221a40538a062a1b8830c1b48d913211a403  
94ff6d708820dda59738401ea10eb1b0d7d98d104a998ba6cee70e728eb5f29f  
9cccdb290dbbedfe54beb36d6359e711aee1b20f6b2b1563b32fb459a92d4b95  
aa7a3655dc5d9e0d69137cb8ba7cc18137eff290fde8c060ac678aa938f16ec7  
ad78b68616b803243d56593e0fdd6adeb07bfc43d0715710a2c14417bba90033  
bb3e5959a76a82db52840c4c03ae2d1e766b834553cfb53ff6123331f0be5d12  
c5b9c3a3bbfa89c83e1fb3955492044fd8bf61f7061ce1a0722a393e974cec7c  
d3612813abf81d0911d0d9147a5fe09629af515bdb361bd42bc5a79d845f928f  
e302fb178314aa574b89da065204bc6007d16c29f1dfcddcb3b1c90026cdd130  
e7c3c8195ff950b0d3f7e9c23c25bb757668b9c131b141528183541fc125d613  
ef5e1af8b3e0f7f6658a513a6008cbfb83710f54d8327423db4bb65fa03d3813  
f2c4e058a29c213c7283be382a2e0ad97d649d02275f3c53b67a99b262e48dd2

第1阶段可执行文件：  
07380d9df664ef6f998ff887129ad2ac7b11d0aba15f0d72b6e150a776c6a1ef  
1e5d5226acaeac5cbcadba1faab4567b4e46b2e6724b61f8c705d99af80ca410  
224009a766eef638333fa49bb85e2bb9f5428d2e61e83425204547440bb6f58d  
27dd5a3466e4bade2238aa7f6d5cb7015110ceb10ba00c1769e4bc44fe80bcb8  
502c4c424c8f435254953c1d32a1f7ae1e67fb88ebd7a31594afc7278dcafde3  
5a9fa1448bc90a7d8f5e6ae49284cd99120c2cad714e47c65192d339dad2fc59  
91032c5ddbb0447e1c772ccbe22c7966174ee014df8ada5f01085136426a0d20  
9114a31330bb389fa242512ae4fd1ba0c9956f9bf9f33606d9d3561cc1b54722  
9fe46627164c0858ab72a7553cba32d2240f323d54961f77b5f4f59fe18be8fa  
c2307a9f18335967b3771028100021bbcf26cc66a0e47cd46b21aba4218b6f90  
c51677bed0c3cfd27df7ee801da88241b659b2fa59e1c246be6db277ce8844d6  
da352ba8731afee3fdbca199ce8c8916a31283c07b2f4ebaec504bda2966892b

PE32可执行文件：  
Remcos PE32可执行文件的哈希值列表可在[此处](https://alln-extcloud-storage.cisco.com/ciscoblogs/5b7d854a894cb.txt)找到

IP地址：  
109.232.227 [.] 138  
54.36.251 [.] 117  
86.127.159 [.] 17  
195.154.242 [.] 51  
51.15.229 [.] 127  
212.47.250 [.] 222  
191.101.22 [.] 136  
185.209 .20 [.] 221  
92.38.86 [.] 175  
139.60.162 [.] 153  
192.0.2 [.] 2  
185.209.85 [.] 185  
82.221.105 [.] 125  
185.125.205 [.] 74  
77.48. 28 [.] 223  
79.172.242 [.] 28  
79.172.242 [.] 28  
192.185.119 [.] 103  
181.52.113 [.] 172  
213.152.161 [.] 165

域名：  
dboynyz [.] pdns [.] cz  
streetz [.] club  
mdformo [.] ddns [.] net  
mdformo1 [.] ddns [.] net  
vitlop [.] ddns [.] net  
ns1 [.] madeinserverwick [.] club  
uploadtops [.]is  
prince[.] jumpingcrab [.] com  
timmason2 [.] com  
lenovoscanner [.] duckdns [.] org  
lenovoscannertwo [.] duckdns [.] org  
lenovoscannerone [.] duckdns [.] org  
google [.] airdns [.] org  
civita2 [.] no-ip [.] biz  
www [.] pimmas [.] com [.] tr  
www [.] mervinsaat [.] com.tr  
samurmakina [.] com [.] tr  
www [.] paulocamarao [.] com  
midatacreditoexperian [.] com [.] co  
www [.] lebontour [.] com  
businesslisting [.] igg [.] biz  
unifscon [.] com

本文翻译自talosintelligence.com
[原文链接](https://blog.talosintelligence.com/2018/08/picking-apart-remcos.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **西格玛** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/158934](/post/id/158934)

安全客 - 有思想的安全新媒体

本文转载自:
[talosintelligence.com](https://blog.talosintelligence.com/2018/08/picking-apart-remcos.html)

如若转载,请注明出处： <https://blog.talosintelligence.com/2018/08/picking-apart-remcos.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [僵尸网络](/tag/僵尸网络)
  * [RAT](/tag/RAT)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t019d477bc1e93f1cf7.png) 西格玛

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

