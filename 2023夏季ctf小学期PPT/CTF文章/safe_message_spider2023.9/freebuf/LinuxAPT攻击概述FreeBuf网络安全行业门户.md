Windows可以运行大多数APT攻击工具，与此同时，人们普遍认为Linux系统较为安全，不易受到恶意代码攻击。多年来，Linux未遇到大量病毒、蠕虫和木马，但Linux中仍存在恶意软件，包括PHP后门，rootkit等。

Linux服务器中承载了各种业务使其成为攻击者的首要目标。如果攻击者能够攻陷Linux服务器，他们不仅可以访问存储在服务器上的数据，还可以攻击与之通联的Windows或macOS的服务器。

## Barium

在2013年首次报告有关[Winnti APT集团（又名APT41或Barium）](https://securelist.com/winnti-more-than-just-a-game/37029/)，当时他们主要针对游戏公司获得直接的经济收益。他们的业务不断扩大，开发了许多新工具，攻击也更为复杂。

MESSAGETAP是该小组使用的Linux恶意软件，可用于选择性地[拦截来自电信运营商的SMS消息](https://www.fireeye.com/blog/threat-research/2019/10/messagetap-who-is-reading-your-text-messages.html)。据FireEye称，该组织将该恶意软件部署在SMS网关系统上，渗透ISP和电信公司，建立监视网格。

最近发现了另一种Barium /
APT41工具，它以编程语言Go（也称为Golang）编写，尚不清楚它是为系统管理任务开发的工具，还是它也是APT41工具集的一部分，有关此工具的更多详细信息，请参见“Suspected
Barium network control tool in GO for Linux”。

## Cloud Snooper

2020年2月，Sophos发布一份报告，描述了一套恶意工具[Cloud Snooper](https://www.sophos.com/en-us/medialibrary/PDFs/technical-papers/sophoslabs-cloud-snooper-report.pdf)。其核心是面向服务器的Linux内核rootkit，该内核挂钩了netfilter流量控制功能，启用了穿越防火墙的隐蔽C2（命令和控制）通信。发现了许多样本，以及位于亚洲的目标服务器。至少从2016年开始，该工具集就一直在开发中。

## Equation

在2015年发现了Equation，其历史可追溯到2001年，早在1996年就参与了多个CNE（计算机网络利用）。该小组拥有强大的工具库。目前发现：“
EQUATIONLASER”，“ EQUATIONDRUG”，“ DOUBLEFANTASY”，“ TRIPLEFANTASY”，“ FANNY”和“
GRAYFISH”。 Equation的创新不仅仅限于Windows平台。该小组的POSIX兼容代​​码库允许在其他平台上进行开发。
2015年发现了针对Linux的早期DOUBLEFANTASY恶意软件，可以收集系统信息和凭据，并提供受感染计算机的访问权限。

![sl_overview_of_atps_02.png](https://image.3001.net/images/20200914/1600049521.png!small)

## HackingTeam

HackingTeam是一家意大利信息技术公司，向世界各国政府，执法机构和企业销售“监视软件”。在2015年遭受数据泄露，400GB公司数据（包括源代码和用户数据）被盗，这些工具被全球的攻击者（例如DancingSalome（又名Callisto））获取，改编和使用。泄漏的工具包括针对Adobe
Flash的零日漏洞利用（CVE-2015-5119），以及能够提供远程访问，按键记录，常规信息记录和渗透的复杂平台，可以检索Skype音频和视频，绕过流加密，RCS（远程控制系统）恶意软件（又名Galileo，Da
Vinci，Korablin，Morcut和Crisis）。

## Lazarus

研究人员在2018年末发现一个未知的恶意框架MATA。该框架用于攻击韩国，印度，德国和波兰的商业公司，与Manuscrypt（Lazarus又名Hidden
Cobra）代码有相似之处。

2020年6月，研究人员分析了金融间谍活动攻击中使用的Lazarus Operation
AppleJeus和TangoDaiwbo的macOS样本，样本证明该小组正在积极开发非Windows恶意软件。

## Sofacy

Sofacy（又名APT28，Fancy Bear, STRONTIUM, Sednit Tsar Team）是活跃多产的APT组织。
从大规模的零日部署到丰富的恶意软件集，Sofacy是研究人员监控的顶级APT组织之一。Sofacy开发了用于多个平台的模块，其中包括2016年用于Linux的模块，被称为“
Fysbis”。 在Windows，macOS，iOS和Linux上发现的样本表明核心团队正在修改和维护代码。

## The Dukes

Dukes是一个复杂攻击组织，于2013年首次对其进行记录。该组织目标有车臣，乌克兰，格鲁吉亚以及西方政府和非政府组织，北约等。Dukes工具集包括一套完整功能的恶意软件，由几种不同的编程语言进行编写。
该小组的恶意软件和活动包括PinchDuke，GeminiDuke，CosmicDuke，MiniDuke，CozyDuke，OnionDuke，SeaDuke，HammerDuke和CloudDuke。

## Lamberts

Lamberts是一个高度复杂的攻击组织，拥有庞大的恶意软件库，包括网络驱动后门，模块化后门，收集工具和用于破坏性攻击的攻击。2017年发布了[Lamberts家族概述，](https://securelist.com/unraveling-the-lamberts-toolkit/77990/)确定了针对Windows和Linux编译的SilverLambert后门。

## Tsunami后门

自2002年首次在野出现，Tsunami（又名Kaiten）成为多个攻击者使用的UNIX后门，现在有70多个变体。
源代码可以在各种嵌入式设备上编译；，并可适用于ARM，MIPS，Sparc和Cisco 4500 /
PowerPC的版本，对基于Linux的路由器，DVR和越来越多的IoT（物联网）设备构成威胁。

## Turla

Turla（又名Uroboros，Venomous Bear和Waterbug）是一个俄语组织，该组织曾使用被劫持的卫星连接，对政府网站的注水等攻击策略。
攻击者多年来对其工具集进行了重大更改，2014年前所有Turla使用的恶意软件样本都是针对32位或64位版本的Windows设计。

2014年12月发布了Turla工具库中Linux组件[Penguin Turla](https://securelist.com/the-penquin-turla-2/67962/)，该后门不需要提升特权。即使系统访问受到限制，后门也可以拦截传入的数据包并运行来自攻击者的命令，如果将其安装在受感染的服务器上，它很难被发现。今年5月，Leonardo研究人员发表了有关[Penguin_x64](https://www.leonardocompany.com/documents/20142/10868623/Malware+Technical+Insight+_Turla+%E2%80%9CPenquin_x64%E2%80%9D.pdf/541d279e-a827-38b4-99e8-3c23553cd66a)的报告，Penguin_x64是Penguin
Turla Linux后门的先前未记录的变体。

## Two-Sail Junk

2020年1月，研究人员发现水坑攻击中完整的利用远程iOS漏洞链部署了LightSpy。该网站的目的是香港的用户。该项目支持Android，并且可能支持Windows，Linux和MacOS。

## WellMess

2020年3月，研究人员开始跟踪名为WellMess的恶意软件。该恶意软件最初由JPCERT在2018年7月记录在案，其可能与CozyDuke（aka
APT29）有关，目前的活动主要集中在医疗保健行业。
WellMess使用.NET和Go（Golang）编写的远程访问木马，可以交叉编译兼容Windows和Linux。

## WildNeutron

2015年首次发布了有关WildNeutron的信息。该组织在2012-2013年对Twitter，Microsoft，Apple和Facebook发动攻击。他们的武器库包括LSA后门，IIS插件，以及基于零日的攻击与后门程序。在几种已知的攻击中，WildNeutron使用了定制的Linux后门。

## Zebrocy

Zebrocy最初使用的恶意软件是Sofacy，与其他APT组也有相似之处。该组织利用多种语言开发恶意软件，包括Delphi，AutoIT，.NET，C＃，PowerShell和Go。
Zebrocy主要针对中亚政府相关组织。该组织广泛使钓鱼来攻击Windows。它的后门通过80端口与Web服务器通信。该组织使用Linux作为其基础架构的一部分，尤其喜欢使用Debian
Linux上运行的Apache 2.4.10。

![1603673701_5f961e656009c59b89e00.png!small?1603673701183](https://image.3001.net/images/20201026/1603673701_5f961e656009c59b89e00.png!small?1603673701183)

## Linux系统保护建议

1、维护软件的受信任来源列表；

2、安全的获取应用程序，必须使用HTTPS或SSH协议进行加密；

3、检查与网络相关的设置，过滤掉主机上所有不必要打开的端口，避免使用不需要或不使用的网络应用程序，正确设置防火墙；

4、使用密码保护本地存储的SSH密钥（用于网络服务）；

5、定期监视主要配置文件以及系统二进制文件的完整性，防文件病毒感染。

## 原文链接

[securelist](https://securelist.com/an-overview-of-targeted-attacks-and-apts-on-linux/98440/)

  

  

  

  

  

  

  

