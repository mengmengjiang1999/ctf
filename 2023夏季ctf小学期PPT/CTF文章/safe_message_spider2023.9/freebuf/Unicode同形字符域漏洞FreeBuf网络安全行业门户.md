**攻击者使用同形字符在gTLD（.com，.net等）以及某些公司的子域中注册同形字符域名，其外观上与其合法的域或子域并无明显差别。攻击者利用该手段对目标组织进行有针对性的攻击。**

##  漏洞综述

从2017年到今天，已有十二个同形字符域拥有有效的HTTPS证书。其中包括金融，互联网购物，专业技术和《财富》100强网站，该技术已用于针对性强的社会工程学网络攻击活动中。下表显示了“外观相似”Unicode
Latin IPA Extension同形符及其对应拉丁字符：

![](https://image.3001.net/images/20200306/1583460191_5e61af5f8ad40.png!small)

> “ɡ”是具有迷惑性的字符，通常与拉丁语的对应字符无法区分。
>
> “ɑ”当不与拉丁字母“a”相邻时也容易被错认。
>
> “ɩ”在某些系统和字体上，这个字符看起来与小写字母“L”非常相似，但这个字符可以辨别出来。

![](https://image.3001.net/images/20200306/1583460372_5e61b014e8a1d.png!small)

同形异义字符攻击不是最新的技术，这种攻击手段已经出现了很多年，并且域提供商已经采取了防范措施，包括限制某些字符的使用并禁止使用混合字符，例如Latin和Cyrillic。但是Verisign和其他域提供商尚未意识到Unicode
Latin IPA Extension字符集中的同形字符。

##  漏洞披露

Verisign和IaaS服务（Google，Amazon，Wasabi，DigitalOcean）已获悉此漏洞。据发现从2017年至今，第三方已经使用这种字符为300个测试域中的15个注册并生成了HTTPS证书。此外，还发现了一个同形字符域包含一个非官方的恶意jQuery库。

披露时间表如下所示：

> 2019年11月22日：发现漏洞
>
> 2019年11月23日—2020年2月2日：提交亚马逊漏、Google、Wasabi、Verisign、DigitalOcean洞报告并确认
>
> 2020年2月10日：通知Verisign已注册的同形字符域。
>
> 2020年2月13日：Verisign，Google，Amazon，Wasabi，DigitalOcean收到了0day重新分类的通知
>
> 2020年2月14日：由于Verisign未及时回应，美国CERT已协助修复漏洞
>
> 2020年2月20日：向ICANN提供有关IDN修订草案，延长了披露期限
>
> 2020年2月24日：Amazon更改了S3 存储服务名称验证策略，防止注册以“ xn--”开头的存储服务名称
>
> 2020年3月3日：Verisign实施了针对“ .com”和“ .net”的缓解措施，防止注册带有同形字符的域
>
> 2020年3月4日：公开披露

##  gTLD域名

在撰写本文时，可以使用上述Unicode拉丁IPA扩展字符来注册同形域名，为了防止恶意第三方注册，研究人员使用IPA扩展字符注册了以下域：

> amɑzon.com**
>
> chɑse.com
>
> sɑlesforce.com
>
> ɡmɑil.com
>
> ɑppɩe.com
>
> ebɑy.com
>
> ɡstatic.com
>
> steɑmpowered.com
>
> theɡuardian.com
>
> theverɡe.com
>
> washinɡtonpost.com
>
> pɑypɑɩ.com
>
> wɑlmɑrt.com
>
> wɑsɑbisys.com
>
> yɑhoo.com
>
> cɩoudfɩare.com
>
> deɩɩ.com
>
> gmɑiɩ.com
>
> gooɡleapis.com
>
> huffinɡtonpost.com
>
> instaɡram.com
>
> microsoftonɩine.com
>
> ɑmɑzonɑws.com**
>
> ɑndroid.com
>
> netfɩix.com
>
> nvidiɑ.com
>
> ɡoogɩe.com

Verisign禁止使用混合字符注册域名。
例如，不可能使用西里尔字母“о”注册“gооgle.com”之类的域名，但大多数注册服务机构都可以申请混合字符域名。虽然不能使用混合字符注册，但可以使用Unicode和拉丁字符混合注册域，只要Unicode字符本身就是拉丁字符即可。
Verisign的[拉丁字母允许表](https://www.iana.org/domains/idn-tables/tables/com_latn_1.2.txt)中列出了此通报中讨论的同形符号，Verisign通过删除这些字符来修补此漏洞，他们会很快更新此表。

###  建议措施

应防止注册包含Unicode Latin IPA
Extension同形字符的域名，建议组织检查其域的同形排列和相关的证书，相关[辅助工具](https://homoglyphs.storage.googleapis.com/index.html)。

##  子域

像Verisign这样的注册商不希望在顶级域名（gTLD）中存在相似的域名，因此会明确禁止使用混合字符。与此同时一些子域上的服务（例如“
s3.amazonaws.com”，“ storage.googleapis.com”）或其他允许用户创建任意子域的服务也应有相同的限制。

Google了解此相似域会存在社会工程攻击的风险，特别禁止创建名称为“ google”的存储服务，并且存储服务名称不能包含“
google”或近似得拼写错误，例如“
g00gle”。但是Google允许注册使用Unicode拉丁IPA扩展同形字符的存储服务名称。此外与gTLD注册域名不同，Google允许注册包含混合字符的存储服务名称。

###  建议措施

应以与Verisign限制域名注册相同的机制来限制子域服务注册，应当拒绝包含混合字符的任何子域以及同形字符。另一种补救措施是采用Amazon用于限制S3存储服务名注册的方法，拒绝所有以前缀“
xn--”开头的存储服务名。

##  Q&A

###  如果有人注册了我的同形字符域该怎么办？

向相关组织提交情况报告：

> Amazon: abuse@amazonaws.com
>
> Google:
> <https://support.google.com/code/contact/cloud_platform_report?hl=en>
>
> Wasabi: support@wasabi.com
>
> DigitalOcean: <https://www.digitalocean.com/company/contact/abuse/>
>
> Verisign: <https://www.verisign.com/en_US/company-information/contact-> us/index.xhtml>

###  其它拉丁字符是否存在问题？

其他一些IPA字符也可以被视为同形文字。在对各种平台和字体设置测试中，这些字符比本文提到的三个IPA字符更具可分辨性。

###  这三个字符中哪个最“严重”？

从Voiced_velar_stop可以看出‘g’排在第一位。拉丁字母Alpha排第二，尤其是在字符串中没有ASCII“
a”字符的情况下。‘ɩ’排在最后，因为在许多系统和字体上，可以从字符中识别出来。

###  同形字符是一个旧问题，为什么要如此重视？

同形字符是一个旧问题。但是，拉丁Unicode IPA字符可以注册而不违反混合字符规则，在此之前并没有人发现并详细报告此类问题，只在Mike
Schiffman的2018年第二季度全球域名同形文字报告上证明了这种可能性。

###  哪些供应商已纠正此问题？

在撰写本文时，仅Amazon（S3）和Verisign修补了漏洞。Verisign已对gTLD注册规则进行了更改，防止使用这些同形文字进行域注册。

###  Verisign gTLD是唯一受影响的TLD吗？

任何允许拉丁IPA字符的TLD都可能受到影响，但是互联网上大多数最受欢迎的网站都使用gTLD，即“ .com”。

###  为什么划归0day后才将推迟披露？

Verisign要求更多的时间来修补漏洞。考虑到此问题涉及范围，以及修补的重要性和独特性，从而延迟了公开披露时间，延迟披露可以最大程度保护Internet用户的最大利益。

###  为什么工具链接代码不是公开？

该代码将在漏洞披露后两周内公开，防止攻击者使用代码自动进行同形字符域的注册。该代码以Go语言编写，编译为WebAssembly。

###  在域中使用IPA字符是合法的，为什么要禁止它？

使用IPA拉丁字符的域名“ɑlphɑ.com”是对IPA字符的巧妙而合法的使用，这很容易与先前存在的“
alpha.com”域混淆。但这并不能说明它是“合法用例”。

###  对于此次漏洞有何想法？

供应商反应迟钝，总体上令人失望。Amazon和Verisign是唯一认真对待此问题并及时更改其策略的供应商。

###  相关组织都做出了什么回应？

在提供了有关漏洞和多种利用方案说明之后，一些组织并不认为这是需要修复的问题，也有表示这是可接受的风险，并且是DNS的已知问题。其他供应商在确认收到披露报告后根本就没有回应。供应商需要认真对待这个问题，应采取积极主动的措施防止包含这些字符的域和子域被注册。

###  从2017年至今生成了HTTPS证书的同形字符域有多少？

在测试大约300个域名中发现了15个。

###  此漏洞被利用了多长时间？

有证据表明是从2017年至今。

为什么近年来活动同形字域和证书的数量减少了？ 我是这次攻击的受害者吗？

推测此漏洞仅在针对性强的社会工程学攻击中使用，普通民众并不会成为目标。由于最近CT日志和浏览器处理URL中的Unicode方面的更改，该漏洞在三年前被利用的更加普遍。

 ***参考来源：[soluble](https://www.soluble.ai/blog/public-disclosure-emoji-to-zero-day)，由Kriston编译，转载请注明来自FreeBuf.COM**

  

