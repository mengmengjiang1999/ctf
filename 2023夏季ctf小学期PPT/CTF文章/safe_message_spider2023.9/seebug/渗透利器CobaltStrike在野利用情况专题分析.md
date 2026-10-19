**作者：启明星辰ADLab**  
**原文链接：<https://mp.weixin.qq.com/s/Agr3doBvYMK6Bs0tH6urcw>**

## 引言

Cobalt Strike是一款商业化的渗透测试利器，由著名的攻防专业团队Strategic
Cyber开发。该工具被广泛应用于渗透测试项目中，在提高政府和企业网络设施安全性上起到了重要的作用。同时，随着网络空间的红蓝对抗不断发展，该框架成为对手模拟和红队行动中最为流行的一款软件。但由于该框架具备团队协作攻击、流量防检测、防安全软件查杀等优势，因而也被大量黑客组织用于真实的高危害性的攻击。目前已知的多个APT组织都曾经使用过Cobalt
Strike攻击框架，如FIN6、Cobalt Group组织和“海莲花”等。但是，目前所披露出来的攻击情报只是黑客利用Cobalt
Strike进行非法攻击的冰山一角。由于该框架集成有丰富的逃避流量监测和沙箱检测技术，且具备优秀的反追踪能力，再结合黑客团体积累的免杀技术和C&C隐藏技术，使得业内对Cobalt
Strike框架的在野利用状况知之甚少，也很难有一个全面的了解和清晰的认知。这种情况直接导致大量依赖于Cobalt
Strike框架进行的网络攻击行为被忽视或者漏掉，如目前仍然存在许多VT查杀率为0的样本以及因利用C&C隐藏技术而存活至今的控制命令服务器。

因此，本文通过逆向工程的手段提取出深度有效的指纹特征，通过各种渠道和自有样本平台对关联样本进行采集分析，最后我们利用其C&C加密与存放的机制来自动化的提取这些被深度隐藏的C&C服务器地址。通过已有数据的分析和追踪我们将对Cobalt
Strike框架的在野利用情况进行一次全面分析。最后，我们还溯源到10个已知的APT组织在使用该框架进行攻击，并且发现了大量使用流量伪装技术、DNS隧道技术、CDN技术、域名前置技术进行流量隐藏的未知APT攻击。当然还收获了大量的使用Cobalt
Strike框架的仿冒域名。这些数据在我们进一步的威胁分析与情报挖掘中起到了重要的作用。

本文将揭秘Cobalt
Strike的在野使用情况，对具体所使用的部分APT攻击组织进行披露，同时对在野利用的各种技术如流量伪装和C&C隐藏技术进行分析，并对Cobalt
Strike服务器“NanoHTTPD
Servers”特征探测的价值进行评估。木马分析部分，我们通过以上情报发现了一起攻击案例，通过分析最后确定该攻击是由攻防实战演练的一个红队发起的，文中我们会阐述这次攻击案例的攻击过程及其攻击手法，并进一步的对黑客所采用的一些特种技术包括逃逸管道、DNS隧道、SMB隧道技术等进行深入分析。

## 分析简述

### 2.1 Cobalt Strike简介

Cobalt Strike是一款基于Java编写的全平台多方协同后渗透攻击框架，也称为CS。早期版本依赖Metasploit框架，Cobalt Strike
3.0之后则是作为单独的平台使用。其支持多种通信协议，包括http、https、dns、smb等，同时集成了提权、凭据导出、端口转发、端口扫描、横向移动、Socks代理、钓鱼攻击等功能，且支持丰富的扩展插件，几乎可以覆盖APT攻击链所需的各个技术环节。木马生成方面也涵盖了大多数的平台和攻击场景，包括
PE木马、ELF木马、网页木马、Office宏病毒木马等。不过Cobalt
Strike是一款商业运营的收费软件，每位使用者一年的许可证费用为3500美元，许可证续签费用为每年2500美元。

![](https://images.seebug.org/content/images/2020/04/42995c5e-9ab6-404e-bf69-966a540ce58f.png-w331s)

图1 Cobalt Strike软件界面

### 2.2 样本采集与处理

为了对Cobalt
Strike的在野使用情况进行全方位的了解和评估，启明星辰ADLab安全研究人员通过长期追踪，采集和分析了大量的关联木马样本，并针对其多种类型和版本的样本提取了指纹特征。

Cobalt Strike的木马生成基于其框架下的模版文件如：beacon.dll、artifact32.dll(存放于Cobalt
Strike.jar文件内的resources目录下)。使用者在配置C&C、端口及其他信息时，Cobalt
Strike会将这些信息加密存放于这些模板文件中。通过分析这些信息加密算法和存放规则，便可以大批量地提取Cobalt
Strike样本的C&C服务器地址。目前我们分析了包含有Beacon、Artifact、Payload、Shellcode等类的Cobalt
Strike样本，并实现了批量样本的C&C解密和提取。这种方法相对来说比自动化沙箱更快速有效。有了这些C&C我们可以进一步描绘出CS使用者的分布情况，以此为线索还可以挖掘出更多情报。

通过长期的样本收集，我们共得到了8380个Cobalt
Strike样本，样本文件包含有EXE、DLL、VBScript、PowerShell等。我们将逆向分析得到的C&C定位规则和C&C解密算法脚本化，得到了自动化处理脚本。通过脚本处理后，最终提取到了973个C&C。在分析过程中我们还发现这批样本中有6410个左右使用了相似的C&C地址，通过溯源发现这些样本的主体为一款名为XMRig的挖矿病毒。这批样本背后的黑客不仅在该病毒中嵌入了Cobalt
Strike木马(全部为beacon.dll木马，C&C为ns7.softline.top、ns8.softline.top、
ns9.softline.top)以获得更为强大的远程控制的功能，而且还在病毒中加入一些可以自动改变HASH的功能（在自我复制过程中变换复制体的数据），在一定程度上达到了自动变异的效果，这也会导致以HASH作为病毒检测的方法失效。

接下来，我们将对这批C&C进行分析处理，并对其中一些有价值的情报进行挖掘，以进一步的掌握Cobalt Strike在野使用者的现实情况。

## CS攻击方情报分析

在这里我们通过CS回连的C&C数据作为线索，以分析Cobalt
Strike木马攻击来源的分布情况，进一步关联出一些已知APT组织并发现一些新的未知黑客组织。同时我们还对Cobalt
Strike木马使用者所采用的一些特种技术进行分析和评估。

### 3.1 分布概况

首先，我们针对Cobalt Strike的C&C服务器地理位置进行了统计分析，从而评估该框架在全球的分布情况和流行程度。从结果来看，Cobalt
Strike服务器的分布范围非常广泛，包括42个国家和地区，其中分布较为密集的国家为中国、美国、荷兰、俄罗斯和日本，上述国家同样也是黑客组织聚集和遭受网络攻击较多的国家。图2是根据C&C数据绘制的Cobalt
Strike C&C全球分布图。

![](https://images.seebug.org/content/images/2020/04/16ece4bb-5523-41c4-9c5e-a1d81ada2e82.png-w331s)

图2 C&C全球分布图

之后，我们对这批C&C的所属运营商进行了细分。结果表明，大量服务器归属于规模较小或无法识别的运营商(图3中以XX表示)。此类厂商的安全管理工作通常较为松散、混乱，相应的租金也较为低廉，攻击者往往倾向于选择此类厂商架设服务器以降低攻击成本和躲避监管。除此之外，内网IP、阿里云、电信、亚马逊、脸书以及谷歌的C&C服务器数量较多。相关占比分布如图3所示。

![](https://images.seebug.org/content/images/2020/04/0f5c95c5-6612-4a94-8b6c-dfca20b50707.png-w331s)

图3 C&C所属运营商占比分布图

考虑到Cobalt
Strike支持多种通信协议，我们进一步提取了样本中的端口特征，从而评估在实际攻击中其端口和通信协议的使用情况。结果显示，443(https)、80(http)和8080端口的使用频率较高，这三种常见端口均具有较强的穿透性和隐蔽性，可以有效避开一些防御方案的网络出站规则限制。虽然Cobalt
Strike也支持攻击者自定义配置端口，但在实际攻击中结合通信协议设置端口显然更具迷惑性。其中，443端口结合https协议加密传输的隐蔽性较高；80端口结合http协议，再配合流量伪装技术也具有不错的隐蔽效果。相关通信端口占比分布如图4所示。

![](https://images.seebug.org/content/images/2020/04/ee194e27-82ca-4ab3-80d4-9b72b7b19994.png-w331s)

图4 通信端口占比分布图

由于样本中存在大量C&C指向内网IP和域名，我们继续对C&C的类型进行了分类整理。973个C&C共涵盖了公网IP、内网IP和域名三类，数量分别为548个、227个和198个，其中公网IP占比超过56%，内网IP和域名数量接近，分别占比23.33%和20.35%。C&C类型占比如图5所示。

![](https://images.seebug.org/content/images/2020/04/aeab919e-1175-46ce-b36c-1c7a4fb9aaf9.png-w331s)

图5 C&C类型占比图

针对C&C数据中出现的大量内网IP和域名，我们推测连接内网IP的样本可能存在如下情况：

  1. 攻击者/渗透测试人员在攻陷某内网主机后，通过横向渗透获取了更多内网机器权限，并进一步借助可连接公网的内网主机作为跳板C&C进行流量转发，从而达到其它主机上线的目的。

  2. 攻击者/渗透测试人员在内网环境部署Cobalt Strike服务器并进行免杀功能测试。

对于连接C&C域名的样本，我们在深入分析后发现了更多有价值的线索，也将在下个小节进行详细的介绍。

### 3.2 隐匿技术

随着网络安全审查制度的不断完善，隐匿技术正越来越受到攻击者的重视。在对C&C为域名的样本进行整理分析时，我们发现了大量特殊的域名，例如仿冒的知名网站域名、CDN域名、DNS服务器NS记录地址、甚至是合法网站的白域名等等，这也引起了我们的疑问，是否攻击者在利用白域名进行免杀测试，或是采用了一些更高级的隐匿技术？

经过筛选发现，C&C为域名的样本中16%的样本存在C&C冗余机制（包含多个备用C&C域名），这种机制也给攻击者提供了更加多样和可靠的连接选择，我们将这些备用C&C也列入了统计，去重整理后共计247个域名。经过VirusTotal扫描分析，超过61%的域名并未报毒。在进一步分析后，我们发现攻击者运用了多种C&C隐藏技术和通信隐匿技术来对抗监管审查和流量分析，从而确保更稳定的权限维持，相关技术说明如表1所示。

隐匿技术 | 技术说明  
---|---  
域名仿造技术 | 通过仿造合法域名干扰普通用户或日志分析人员  
CDN技术 | 借助CDN服务进行流量中转，隐藏真实C&C地址  
域前置+CDN技术 | 借助合法域名作为前置域，结合CDN隐藏真实C&C地址  
DNS隧道技术 | 将恶意流量隐藏在DNS协议中对抗流量检测  
流量伪装技术 | 借助Malleable-C2-Profiles配置文件自定义通信流量规则对抗流量检测  
  
表1 隐匿技术说明

我们进一步统计了这批域名样本中各类隐匿技术的使用占比情况，其中，部分样本融合了多项技术，例如同时运用域名仿造和DNS隧道技术(归类至DNS隧道)、同时使用域名仿造和流量伪装技术(归类至流量伪装)等，由于此类样本数量较少，对分析结果的影响有限，故进行了调整处理，得到隐匿技术占比图。

![](https://images.seebug.org/content/images/2020/04/5a742290-c08a-4cc5-8450-a8dc145b3894.png-w331s)

图6 隐匿技术占比图

由图6可知，超过72%的攻击者尝试通过隐匿技术来增强自身隐蔽性。其中，约37%的攻击者采用通信隐匿技术（流量伪装、DNS隧道）来躲避流量检测，且往往会结合域名仿造进一步增强伪装性。约15%的攻击者采用C&C隐藏技术（CDN技术、域前置+CDN技术）来逃避审查和溯源分析，相关技术将结合样本中的示例进行介绍。

#### 3.2.1 域名仿造技术

通过仿造合法域名干扰普通用户或日志分析人员。攻击者通常采用插入“-”连字符、替换形近字符、颠倒词语顺序、更改顶级域名等方式仿冒合法域名，从而将域名伪装成知名公司、软件、更新服务等网站域名进一步开展恶意活动，包括Baidu、Chrome、Windows、Office等都是常常被选择的伪造目标。由于此类伪装方式具有很强的迷惑性和隐蔽性，会对普通用户或日志分析人员产生较大干扰，且技术门槛和成本较低，俨然成为许多攻击组织的标准配置。一些仿造示例如表2所示。

**C &C** | **仿造目标** | **备注** |  
---|---|---|---  
baidu-search.net | Baidu | 仿造知名公司或软件域名 |  
dns-chrome.com | Chrome |  |  
ns1.fackbook.gq,ns2.fackbook.gq,ns3.fackbook.gq | Fackbook |  |  
update.server.evevnote.com,server.evevnote.com | Evernote |  |  
windows-system.host | Windows | 仿造系统或更新服务域名 |  
windwosupdate-beijing2019.com-system2019-micortsoftewindowschina2019.com.glxqn.cn | Windowsupdate |  |  
upgrade-services.com | Upgrade |  |  
fedex.global | Fedex | 仿造商业公司或社会机构域名 |  
update.safebuikers.com | Safebulkers |  |  
thimunsingapore.org | singapore.thimun.org |  |  
officewps.net | office、wps | 攻击组织 | APT32  
helpdesk-oracle.com | Oracle | Cobalt Group |  
mcafee-analyzer.com | Mcafee | CopyKittens |  
update.cisc0.net,developer.cisc0.net,res.cisc0.net | Cisco | Darkhydrus |  
**……** |  |  |  
  
表2 域名仿造示例

#### 3.2.2 CDN技术

CDN(Content Delivery Network 内容分发网络是高效地向用户分发 Web
内容的分布式服务器网络，其在网络访问加速、防御DDoS攻击等方面有着重要的作用。例如网站借助CDN进行DDoS防御时，如果将域名指向CDN，网站流量就会经过CDN中转后再进一步转发至真实IP地址，从而隐藏真实的服务器IP，防止服务器直接遭到攻击。同理，这种防护思路也被黑客所利用，攻击者通过CDN中转流量可以将真实C&C隐藏在CDN之后，将攻击溯源复杂化。C&C中常见的云服务提供商包括亚马逊(cloudfront.net)、谷歌(appspot.com)
、微软（azureedge.net）等。一些示例见表3。

**C &C** | **Hash**  
---|---  
dvvdhxuyj5ec8.cloudfront.net | f1340bcb2b6736f3df874181ff95f198  
ds1wgtx86lg0f.cloudfront.net | 0f10ec8e18209e7a8e46e428815a3430  
djo62u1ouhtae.cloudfront.net | d2a67209e2669e48876522472b60a6da  
msedgesecure.appspot.com | ca0dc3e6d9ed03c6ddb7397bfcdf0597  
update-162303.appspot.com | 0391ba787cc32a40617051561e59902d  
secure-adn.appspot.com,msftncs.appspot.com, trendmicro.appspot.com |
8bc55a7d07cbc663b4afb18c961b6b64  
endpoint18290.azureedge.net | 2867280baf00ff424418377260dcb5d2  
365live.azureedge.net | bfc93e18fad9f7bb93163ed70f527e88  
**……** |  
  
表3 CDN技术示例

#### 3.2.3 域前置+CDN技术

域前置(Domain Fronting)的核心思想是在不同通信层使用不同的域名，在基于Domain
Fronting的HTTP(S)请求中，DNS查询以及SNI携带一个合法域名(前域)，而在HTTP
Host头中携带另一个域名(隐蔽或被禁止访问的域名C&C)，当请求被发送给合法域名后会由相应云服务解析并转发至隐蔽域名，使其不以明文暴露给网络审查者，从而隐藏攻击者的真实C&C。技术说明如图7所示。

![](https://images.seebug.org/content/images/2020/04/4a27f2c0-ecea-48cd-a138-f1eb499c6275.png-w331s)

图7 Domain Fronting技术

起初我们并未能发现这类技术的运用，但是样本C&C中出现的大量合法白域名非常可疑。在进一步逆向分析后，我们发现这些样本请求包的Host字段指向了一些与C&C不同的域名，即使用了域前置技术。域前置技术在CDN等重要的基础设施和各类云服务中尤其适用，虽然部分厂商已停止支持域前置功能，但技术思路可以引伸触类。从统计结果来看，约有10%的域名样本采用了域前置技术，其中隐蔽域名使用较多的云服务厂商包括微软(Microsoft
Azure)、亚马逊(Amazon CloudFront)和谷歌(Google App
Engine)等，合法域名则通常可以从相关CDN子域进行寻找，攻击者常采用一些知名网站或网络安全公司相关的域名来逃避检测，部分示例如表4所示。

**前域（合法域名）** | **Host** **(隐蔽域名)**  
---|---  
do.skype.com | fastflowers.azureedge.net  
mscrl.microsoft.com,software-download.office.microsoft.com,ajax.microsoft.com
| wsus-update.azureedge.net  
ajax.microsoft.com, cdn.wallet.microsoft.com | ms-cloud.azureedge.net  
crl.paloaltonetworks.com | d1ol1waxbvmde2.cloudfront.net  
status.symantec.com | dul0hrsepuj7q.cloudfront.net  
www.asisupportforums.com | dc5plq2mqf9wk.cloudfront.net  
www.google.ca, mail.google.com,calendar.google.com | assets54721.appspot.com  
www.google.com | translateserviceupdate.appspot.com  
www.google.com,mail.google.com | img371935.appspot.com  
**……** |  
  
表4 Domain Fronting技术示例

#### 3.2.4 DNS隧道技术

DNS隧道是隐蔽信道的一种，通过将其他协议封装在DNS协议中，然后利用DNS查询过程进行数据传输。由于大多数防火墙和入侵检测设备会放行DNS流量，故可以利用放行特点和协议解析流程进行隧道攻击，将恶意流量隐藏在DNS协议中逃避流量检测。

在整理冗余C&C样本（包含多个备用C&C域名）的过程中，我们发现了一些疑似DNS服务器NS（Name
Server）记录地址的域名，例如ns1.microsoftonlines.net、ns1.fackbook.gq、ns5.thepatestid.online等等。通过更深入的逆向分析和特征提取，确认这些样本使用了DNS隧道技术。从统计结果来看，约有15%的域名样本采用了DNS隧道技术进行通信，且大多数攻击者会设置多个域名服务器NS记录来提高连接的可靠性，同时结合域名仿造技术进行伪装，即使用户查看流量也难以察觉。相关样例如表5所示(更加详细的DNS隧道分析可参考技术分析章节内容)。

C&C | Hash  
---|---  
dns2.loocallhosts.com,dns.loocallhosts.com,dns3.loocallhosts.com |
ebd2381b811c38efbb706c2a8ebfb55c  
img.statcontent.co,content.statcontent.co | 4ebe65ad6598d6903253dd4461c46e7d  
hus1.ptps.tk,hus2.ptps.tk,hus3.ptps.tk | e51ed5e2df75c3663eecac61db3493b4  
ns5.thepatestid.online;ns5.thepatestid.online |
7d816e122b0d07682b222eaadb66aa51  
ns1.fackbook.gq,ns2.fackbook.gq,ns3.fackbook.gq |
fec4bc410bedc904d3967c910a7e92d5  
ns1.ssz4v.com,ns2.ssz4v.com,ns3.ssz4v.com | 9ea8353ce4c98df601cbb15ac303ea88  
ns1.aeo22662.xyz,ns2.aeo22662.xyz,ns3.aeo22662.xyz |
1a5c192915669d87942f7f8b1f6cbf3e  
ns1.microsoftonlines.net,ns2.microsoftonlines.net |
85b87c8933a0f8f128467ae34928f97f  
**……** |  
  
表5 DNS隧道技术示例

#### 3.2.5 流量伪装技术

流量伪装技术是指借助Cobalt
Strike的Malleable-C2-Profiles配置文件自定义通信流量规则对抗流量检测的技术。攻击者通过加载定制的配置文件（如amazon.profile、jquery.profile等模板）来改变目标主机与Server端的流量特征，将HTTP通信流量伪装成正常Web流量或加密混淆流量，从而达到通信隐匿的效果。

在提取域名样本连接请求的Host字段特征时，我们除了挖掘到使用Domain
Fronting技术的样本，还发现了大量使用此类流量伪装技术的样本。其在域名样本中的使用占比超过21%，也是攻击者运用最多的伪装技术。该类样本的Host字段通常会由配置文件设置为指定的Web域名以模拟相关请求，常见的请求包括Amazon、Jquery、Bing等，更多的样例如表6所示。

**C &C** | **Host**  
---|---  
informedia.info | code.jquery.com  
greatdirectmail.com | code.jquery.com  
olosirsch.com | www.amazon.com  
ssl2.blockbitcoin.com | www.amazon.com  
update.microsoft-update-ru.com | www.bing.com  
f.cdn-global.com | www.espn.go.com  
cache.violet-cdn.com | en.wikipedia.org  
thedivineshoppe.com | www.fidelity.com  
iosios1937cn.firedog.ml | www.firedog.com  
http.pc-rekcah.com | www.hulu.com  
**……** |  
  
表6 Malleable-C2-Profiles流量伪装技术示例

通常来说，如果是针对特定目标的攻击，攻击者还会根据目标机器存在的网络环境、通信软件、常用网站等来伪造流量特征，Host设置的内容则可能与相应域名有关。从Host统计来看，部分域名指向了fidelity（富达投资-金融服务公司）、ESPN（娱乐与体育节目电视网）、Firedog(小型发动机动力设备制造商)、Hulu（流媒体服务商）在内的多家商业服务公司，黑客的攻击目标也很可能会与相关公司或服务的使用群体有关。此外，黑客还可以借助Malleable-C2-Profiles配置文件模仿其它恶意软件的通信协议，从而达到掩盖、伪装自身的行动目的，欺骗流量检测系统。

显然，这些隐匿技术给审查机构和溯源分析者带来了极大的困难，随着攻击者越来越多的使用类似技术，从情报端(威胁情报分析平台)到防御端(IDS、IPS等终端防御系统)都将面临更加严峻的挑战，也迫切需要更加强大的特征指纹、流量分析及关联分析能力。

### 3.3 版本和特征探测

目前，对于防御方来说，除了通过威胁情报平台的IOC特征进行关联分析，还可以借助一种特征探测的手段对Cobalt
Strike服务器进行识别和追踪。该规则由安全公司Fox-IT提出，由于Cobalt Strike的 "Team Server"
基于开源Web服务器NanoHTTPD,可通过NanoHTTPD Servers在其HTTP响应中返回的多余“空白符”特征识别Cobalt
Strike服务器，此特征可影响Cobalt
Strike服务器3.13版本之前的所有旧版本。因此，如果能够获取近期大量样本的对应版本，就能够在一定程度上反映出各版本的使用率，同时推测当前该特征识别对于Cobalt
Strike服务器的影响程度。进一步收集和分析后，我们发现Cobalt
Strike的版本众多，其中部分版本的母体样本存在编译时间重叠，而其payload的编译时间则相对独立准确，且不会随母体样本生成而改变，故可解密提取样本的payload编译时间来归类其所属版本，编译时间轴如图8所示。

![](https://images.seebug.org/content/images/2020/04/b6c6d9df-690c-40e9-bece-ac0d4902802a.png-w331s)

图8 payload编译时间轴-样本数

我们针对目前传播较广的几类Cobalt
Strike版本进行了收集，并提取了对应木马的payload编译时间，相关数据与图8展示的实际编译时间分布基本相符。值得注意的是，这几类版本均存在破解版，也间接表明Cobalt
Strike的大量用户可能是非商业付费人群。

**Cobalt Strike版本** | **payload编译时间** | **数量**  
---|---|---  
Cobalt Strike 3.6 | 2016/12/08 | 350  
Cobalt Strike 3.8 | 2017/05/23 | 281  
Cobalt Strike 3.12 | 2018/09/06 | 212  
Cobalt Strike 3.13 | 2018/12/29 | 222  
Cobalt Strike 3.14 | 2019/04/19、2019/05/04 | 90  
Cobalt Strike 4.0 | 2019/12/05 | 115  
  
表7 Cobalt Strike版本及对应信息

为了更好的反映各版本的流行程度，我们将相关版本的捕获数量与时间进行了关联统计（以此批样本为例，仅体现变化趋势），如图9。

![](https://images.seebug.org/content/images/2020/04/6d585909-f81c-4812-afbc-84b22c51da21.png-w331s)

图9 Cobalt Strike各版本样本捕获时间折线图-样本数

从各版本的流行趋势来看，虽然历次的版本更新都会造成前期版本一定程度的用户流失，但旧版本始终保有相对稳定的用户量。参考2020年3月的数据情况，已有大量攻击者开始采用Cobalt
Strike
4.0实施攻击，但3.13之前的旧版本使用量占比仍然有23%。可见，部分使用者不会及时更新或倾向于使用已有的破解版本，因此未来通过旧版本服务器发动攻击的现象可能长期存在，该特征检测规则对于打击恶意活动方面仍具有一定的价值。

### 3.4 框架使用者

那么，究竟是哪些人员或组织在使用Cobalt Strike框架呢？我们针对这批Cobalt
Strike样本的IOC进行了更加深入的溯源，结合关联样本的出现时间、技术运用、攻击链条以及公开的研究报告等资料，发现了多个著名的攻击团伙和APT组织，关联信息如表8所示。

**Groups** | **Cobalt Strike C &C** | **Hash**  
---|---|---  
**Darkhydrus** | update.cisc0.net, developer.cisc0.net, res.cisc0.net |
7a4f8fffb1041bf6b19f76ded41b90b616f733b00e7957fbc94c4ea120f1903de999963fc3654937  
**CopyKittens** | cloud-analyzer.com, fb-statics.com, mpmicrosoft.com,
officeapps-live.org, cachevideo.online, fbstatic-akamaihd.com, mcafee-analyzer.com | af18959b5204853ef347fb05b518fca26a08ae57  
**Leviathan** | www.thyssenkrupp-marinesystems.org |
1875db18a7c01ec011b1fe2394dfc49ed8a53956  
**Cobalt Group** | 46.21.147.61, helpdesk-oracle.com |
8c6a264d5fd2d9f9d93d5350fccd52046b5007d2  
5.135.237.216 | 1232a214b510a6b306e51a166c19fad5ac63bfc8 |  
86.106.131.207 | ba4d490c97a7ba6a2d7f374919e56bd3f6fd88d9
99210a1bd725ebedb3a0cb5420e466069794300e
8fb192e336f83bf17d6bbb931de97d168e584239 |  
104.144.207.207 | cc794e4a1f7e23008e6e648b1aacb87db446fc98 |  
176.9.99.134 | 1f50d16316c9896e3ea8cb5e8cfee195bc4aa92b
5b2f84580c863d6482d05c79ef7d7169bde2593f |  
52.15.209.133 | fe61c78a331e82d4ed8e8fe975fb0e14384ab2c0 |  
206.189.144.129 | 46742e6096cd417ea6b2803ec4b5d0a5f1dfe4f0 |  
**FIN7** | 165.22.71.42 | 009c97361fdc7d912c4154ab7c739b606b5bf79d  
**Bokbot** | 185.82.202.214 | 343f1e5e072887d7b77375028999d078ac7ccdca  
**APT10** | 95.128.168.227 | 5122094dbd6fc8d3da0acfa02234104d927f27c6  
**APT19** | autodiscover.2bunny.com | 7b0d8394b32cb59c59e4ac9471dba676678fd91a  
**APT29** | pandorasong.com |
9858d5cb2a6614be3c48e33911bf9f7978b441bfa968c95ee054af28e88edb77c60e8c035de97237  
**APT32** | officewps.net | 5c0ad0af431ca32d0050052c17eb8c72a2ad8a43  
api.blogdns.com | 3e65b4fefa92cbf3e146a096eaa0aeec5c1be42a |  
load.newappssystems.com | 78c549a7f4119aa876763426e6f76be3d4f43dd3 |  
  
表8 攻击组织IOC信息

这些组织善于借助域名仿造、多级跳板、DNS隧道、流量伪装等技术手段隐蔽自身。其中，很多组织都热衷于使用DNS隧道攻击，以绕过防火墙或IDS的流量检测，且其域名往往会精心伪装设计，即使用户查看流量也难以辨别。使用Cobalt
Strike频率较高的组织则是Cobalt
Group和APT32(海莲花)，在它们的多次攻击行动中都能发现相关证据。此外，通过溯源关联和厂商披露，还发现FIN6、BITTER(蔓灵花)、Ordinaff等组织也曾使用过Cobalt
Strike。

不仅是以上披露的攻击组织，我们在样本溯源过程中同样发现了不少红队攻击的案例，后文也将举例进行详细分析。显而易见的是，当前攻防双方都非常热衷于运用该框架进行安全对抗。目前我们发现与Cobalt
Strike有关联的攻击组织已经达到13个，而基于逐渐成熟的C&C隐藏技术和溯源的困难性，这些可能只是未知网络的冰山一角，还有大量隐藏的攻击组织和未知的APT攻击并未得到披露，这也给网络安全秩序的维护提出了更大挑战。

综合以上分析结果，汇总Cobalt Strike框架的在野使用情况如下：

  1. 分布情况：这批样本的973个C&C服务器共分布在42个国家和地区，Cobalt Strike使用群体广，分布范围大。

  2. 端口使用情况：443(https)、80(http)和8080端口的使用率较高。

  3. 使用人员：黑客组织、红队人员、安全研究人员等。 

  4. 关联攻击组织：Darkhydrus、CopyKittens、Leviathan、Cobalt Group、FIN7、Bokbot、APT10、APT19、APT29、APT32、FIN6、BITTER、Ordinaff等。

  5. C&C域名查杀率：61%的C&C域名VirusTotal未报毒或无关联记录。

  6. 隐匿技术：包括域名仿造技术、CDN技术、域前置+CDN技术、DNS隧道技术、流量伪装技术等。

  7. 版本使用情况：Cobalt Strike自2012年发布起共经历70余次版本更新，最新版本为Cobalt Strike 4.0，目前其3.6至3.12间的版本用户量依旧不少，相关服务器受NanoHTTPD Servers影响可被特征探测。

## 攻击案例分析

在基于以上数据的情报分析过程中，我们发现了一起以某金融类公司为幌子的攻击案例，该案例最终确认为攻防实战演练的一个红队的攻击活动。本文选择这样一个案例来阐述CS木马的利用手法，并以此为背景，我们来分析和探讨Cobalt
Strike木马所采用的一些特殊技术如管道逃避检测技术、DNS隧道、SMB隧道技术等。

在本攻击案例中，国内一个红队在Github故意投放一些与某金融类公司相关的信息如公司VPN登录网址、账号和密码等敏感信息，以此引诱对该目标感兴趣的对手团队。登录网站为仿冒该金融类公司的钓鱼网站，仿冒网站登录后会诱导对手团队下载页面提供的VPN客户端，一旦对手下载并执行该客户端，便会感染CS木马，成为受控主机。仿冒网站见图10。

![](https://images.seebug.org/content/images/2020/04/777feeef-cce0-4ae5-88aa-b40a52167a59.png-w331s)

图10 木马下载页面

下载得到的VPN客户端名称为“vpnclient.rar”，其中包含有两个文件分别为“vpnclient.exe”和“wwlib.dll”，其中文件“vpnclient.exe”为带有微软签名的word2007官方程序，“wwlib.dll”文件为word程序必加载组件，这里被嵌入了CS木马。这是一种利用合法白文件+DLL劫持的手段进行攻击的技术，此前多个组织如海莲花等都采用过此种技术进行攻击。

![](https://images.seebug.org/content/images/2020/04/30935d73-08ac-41ff-adc4-6394b3ae886a.jpg-w331s)

图11 木马传播和执行图

当vpnclient.exe运行后，表面上会打开一个名为“vpnclient..docx”的word文档，而背地里则会解密执行shellcode来下载CS的远控模块以执行从C&C传来的恶意指令（整个木马的发现和执行见图11）。经进一步深入分析，该远控模块由beacon模板生成，其包含有丰富功能，如服务扫描、端口转发、多模式端口监听等功能。Cobalt
Strike框架的精髓之处是攻击者可以利用不同的通信方式和C&C服务器通信，我们这里主要介绍其比较有特色的几个功能，分别是基于DNS协议的DNS隧道攻击、基于SMB协议的命名管道内网攻击和基于socks流量代理的内网攻击。同时，Cobalt
Strike框架还可以和Metasploit框架相互配合，来进行联合的网络渗透和内网攻击。

### 4.1借壳启动

该CS木马借用微软官方程序来加载自己核心组件执行，通过利用白文件和DLL劫持的方法来绕过安全检测，以达到落地攻击目标的目的。其中压缩包文件中的文件“vpnclient.exe”可以正常绕过任意安全软件的检查得以执行，但是其运行后会加载同目录下伪装为微软组件“wwlib.dll”的CS木马加载器。当目标运行“vpnclient.exe”后，表面上会打开一个名为“vpnclient..docx”的word文档（该文档是一款名为“VPN
Client”程序的安装和配置操作说明文件，见图12），目的是迷惑受害用户。而背地里，恶意代码则会执行“wwlib.dll”并下载执行CS远控模块，以达到控制对手主机的目的。

![](https://images.seebug.org/content/images/2020/04/8444abdc-4f41-4414-85b3-8696d8fe3c8f.png-w331s)

图12 用于迷惑受害用户的文档

“wwlib.dll”恶意文件的资源文件包含两部分数据，分别为名为“CODE”的shellcode和名为“WORD”的word文档（见图13）。CS木马运行时，一方面提取“WORD”资源并使用word软件打开来迷惑受害用户，另一方面提取“CODE”资源来解密执行，下载CS远控模块，对受害用户实施网络攻击。

![](https://images.seebug.org/content/images/2020/04/f1c36733-d353-4253-ba5f-fb196ddf4d54.png-w331s)

图13 wwlib.dll恶意文件的资源数据

### 4.2 上线分析

远控模块执行后，首先收集感染设备信息，准备上线。远控模块将感染设备的IP地址、管理员账户、计算机名和本进程id等信息（见图14）加密后作为上线包发送到C&C服务器。

![](https://images.seebug.org/content/images/2020/04/2e563a4b-a353-4d7a-97a4-accf41dca122.png-w331s)

图14 收集设备信息

图15是我们模拟C&C服务器，使用Wireshark抓到的上线包，从该上线包中，我们可以看到加密后的信息被伪装成Cookie字段，隐藏在了http协议里面。

![](https://images.seebug.org/content/images/2020/04/f438bd1c-b517-4a97-965d-c1636edde1d8.png-w331s)

图15 抓取到的上线包

命令加密后使用tcp协议发送，部分执行结果则使用http协议进行回传。如下是我们模拟木马命令，使用shell dir
列出感染设备当前目录所抓取到的数据包。从图16中可以看到，命令执行后的结果回传使用了http协议。

![](https://images.seebug.org/content/images/2020/04/096fed1e-61be-43f9-a768-263974ee84f9.png-w331s)

图16 控制命令执行后，返回的数据包

### 4.3 远程控制

从CS木马远控模块的控制命令和相关代码的反汇编结果来看（见图17），远控模块包含多种恶意功能。主要包括屏幕截图、键盘记录、socks代理、网络和主机枚举、端口扫描、文件上传和下载、执行powershell命令、提权、注入会话到特定进程以及DNS隧道攻击等（详细的的命令和功能介绍见附录部分）。由以上的分析可知，当对手下载并运行该伪造的“vpn客户端”，打开“vpn安装配置指南”文档研究的同时，红队方的木马已悄悄上线。红队方攻破对手内网后，能够利用该木马窃取对手的作战计划、掌握的工具和利用的漏洞等信息，红队方根据掌握的这些信息，可以有效调整自己的作战策略和应对计划。

![](https://images.seebug.org/content/images/2020/04/544171c4-504b-40e4-baa0-fad40ad4820c.png-w331s)

图17 控制命令和代码执行

## 对抗技术分析

以上攻击案例中我们仅仅对CS木马从落地到远程控制的过程做了简要分析，在更多的案例中，CS木马还具备更加强大而丰富的安全对抗手段，如逃逸管道技术、DNS隧道、SMB隧道、Socks代理技术以及可定制的代码注入技术等等，这些技术手段的使用在很大程度上不但断提高自身的成活率，增强黑客攻击活动隐秘性，极好的保护黑客自身。本节将对CS使用到的此类技术的实现原理和机制进行详细的分析和讨论。

### 5.1 管道逃逸技术

CS木马使用了管道逃逸技术来躲避安全软件的查杀。该技术利用管道作为恶意代码的暂存通道，在很大程度上避免了安全软件的查杀，通过测试验证，该技术可以绕过很多主流杀毒软件（如360、ESET
Nod32）的安全检查。经我们的安全研究人员多次验证，该技术截至本文撰写时依然有效。CS木马利用管道逃逸技术执行远控模块的实现过程如下。

首先新起一个线程创建名为"\\.\pipe\MSSE-594-server"的命名管道（其中594为随机值）如图18，接着木马将长度为0x34200的加密数据写入到该命名管道中，等待后续读取和进一步的解密，写入的加密数据见图19。

![](https://images.seebug.org/content/images/2020/04/6a053bfb-ecf9-4e0c-b35e-9c3c0126042e.png-w331s)

图18 创建命名管道，写入加密数据

![](https://images.seebug.org/content/images/2020/04/74120441-c792-499e-9ce3-e324bb5ac3e5.png-w331s)

图19 加密数据

睡眠1024毫秒后，木马从前面创建的命名管道中读取加密数据，见图20。

![](https://images.seebug.org/content/images/2020/04/fdb31a69-acdb-420e-ba8f-05e8d665fff6.png-w331s)

图20 从命名管道读取数据

在解密数据之前，木马首先申请一段内存空间，用于存放解密后的payload，见图21。

![](https://images.seebug.org/content/images/2020/04/d597285b-81b4-403a-bb57-71f79e2865fb.png-w331s)

图21 申请内存空间

木马将读取到的加密数据，每4个字节为一组，依次和整形数据0x1aa64991（不同的样本该数值会有不同）异或，异或运算后的值即为解密数据，最终解密出CS远控模块文件。

![](https://images.seebug.org/content/images/2020/04/e5f51004-5997-4b3c-b0bc-c89f9a0ee5a0.png-w331s)

图22 解密数据

通过解密后的数据可以看出，该CS远控模块文件为Windows平台的PE文件，如图23。

![](https://images.seebug.org/content/images/2020/04/2fd686db-1a35-4bc4-8cda-08e0021da04b.png-w331s)

图23 CS远控模块文件

CS木马在解密完远控模块后，将远控模块所在的内存属性修改为rx，并使用函数CreateThread执行远控模块代码，实现对感染机器的攻击和远程控制，如图24：

![](https://images.seebug.org/content/images/2020/04/2f4053c7-58af-421a-9e25-a7424a44512c.png-w331s)

图24 启动线程执行CS远控模块

### 5.2 DNS隧道

DNS隧道是将其他的协议内容封装在DNS协议中，然后利用DNS查询过程来进行数据传输的技术。CS支持使用DNS隧道技术来和C&C服务器通信以应对复杂的网络环境。如图25，封装后的流量通过DNS递归查询，最终到达C&C服务器解密。同样，来自C&C服务器的指令也可以通过这种方式顺利下发到受控端。使用DNS隧道技术可以有效躲避防火墙、IDS、IPS等传统网络安全设备的检测（因为这些设备很难做到对DNS流量的友好规则控制），大大提高了渗透测试或攻击的隐蔽性。

![](https://images.seebug.org/content/images/2020/04/6e5d4579-0ef7-4b96-86e0-d881ef144f63.png-w331s)

图25 DNS隧道攻击

图26是一个使用DNS隧道模式进行通信的数据包，从图中我们可以看到，控制端发送的命令和受控端返回的流量都被隐藏在了DNS隧道中加密传输。

![](https://images.seebug.org/content/images/2020/04/00db222d-57a9-4f7b-8b17-1eb91652ca86.png-w331s)

图26 DNS隧道模式通信的数据包

如图27，命令执行完后，受控端将回显信息封装成DNS字符串，通过DNS隧道回传给C&C服务器。

![](https://images.seebug.org/content/images/2020/04/493318cb-97e2-42d1-9627-71aa0458f87b.png-w331s)

图27 回显信息加密传输

### 5.3 SMB隧道

CS支持内网主机之间使用基于SMB协议的 Beacon 来进行数据交换。这允许让一台受感染的计算机与 C&C 服务器进行正常的 beacon
连接，并使内部网络上的所有其他的服务器通过 SMB
协议与最初受感染的主机进行通信。如图28，在攻击者成功攻破内网主机目标1后再进行内网横向移动，将基于SMB的Beacon木马植入目标2主机。这样目标2上线后，就会通过SMB协议的命名管道和目标1通信，目标1再通过DNS或者HTTP协议将恶意流量转发出去。通过这样，攻击者可以操纵
Beacon
通信，实现让所有来自受感染主机的流量看起来和普通流量无异。采用这种连接方式，当安全管理人员检测到一个二级系统有问题并进行取证分析时，他们可能会无法识别与实际攻击相关的
C&C 服务器域名。

![](https://images.seebug.org/content/images/2020/04/26b58f15-8a00-42ff-b477-6e212ed8eab9.png-w331s)

图28 SMB内网渗透

图29是内网中目标2和目标1的通信数据包，从图中可以看到，在完成SMB协议协商和会话后，目标2连接到了目标1的IPC$共享，然后利用该命名管道进行基于SMB协议的数据通信。

![](https://images.seebug.org/content/images/2020/04/4b9193a6-62df-4ce2-8d58-76ec8e4e633b.png-w331s)

图29 SMB通信数据包

### 5.4 Socks代理

Cobalt Strike自带socks代理功能，在攻破组织内网后，beacon socks代理功能可以被用来对目标网络做进一步的内网渗透。如图30，web
server是一个位于内网的web服务器，其仅为组织内部服务。目标1为内网中一台可以访问外网的设备，攻击者在拿到目标1的控制权限后，可以在控制端开启beacon的socks功能，然后利用proxychains等本地代理工具访问webserver内网服务器，对目标组织进行更加深入的渗透攻击。

![](https://images.seebug.org/content/images/2020/04/5c942739-1473-43e3-b91c-a6cf8dfa1bc0.png-w331s)

图30 Socks代理功能

如图31，是目标1通过beacon的socks代理转发给攻击者的内网服务器流量，从图中可以看到，攻击者成功访问了位于组织内部的Web Server服务。

![](https://images.seebug.org/content/images/2020/04/085370a8-e8f8-4b3e-b71a-e6346cb26a9e.png-w331s)

图31 Beacon转发的流量

### 5.5 代码注入技术分析

在分析CS远控模块的过程中，我们发现根据不同的上下文条件，远控模块使用了不同的代码注入技术来实现远程代码的注入（图32为使用了远程线程及APC注入技术）。

![](https://images.seebug.org/content/images/2020/04/14347a27-324f-4d3f-98cc-8e17d970e8db.png-w331s)

图32 恶意代码的注入和执行

CS木马的注入方式是非常灵活的，其可以通过配置文件来进行灵活的配置，从官方博客中我们就可以看到beacon模块的代码注入配置样例。自从Cobalt
Strike更新至3.6版本后，官方给出了一个Malleable-C2，也就是在启动团队服务器的时候加载一些配置文件，Malleable-C2配置文件中的进程注入块（process-inject block）决定了进程注入行为的内容并且控制进程注入行为。

![](https://images.seebug.org/content/images/2020/04/f2699876-6348-4df7-9f6b-ef74c2c5a683.png-w331s)

图33 process-inject block

进程注入块是围绕进程注入流程的生命周期组织的，分为以下4步：

![](https://images.seebug.org/content/images/2020/04/b0392ab4-87ae-4151-9bc4-0bcb141ca5ac.png-w331s)

图34 进程注入流程

第一步是隐式的，如果生成一个临时进程，例如后开发工作（post-exploitation
job），实际上已经有了对远程进程进行操作的句柄。如果要对现有的远程进程注入代码，恶意payload会使用OpenProcess函数。

对于第二步和第三步，恶意payload有两个选择来分配远程进程中的内存并将数据复制到其中。第一个选择是经典的VirtualAllocEx->WriteProcessMemory模式，另一个选择是CreateFileMapping->MapViewOfFile->NtMapViewOfSection模式。

第四步，这一步之前，要注入的内容已经复制到了远程进程当中，这一步需要做的就是执行这些内容，这就是process-inject->execute块的作用。执行块控制着恶意payload注入代码到进程的方法，恶意payload检查执行块中的每个选项，以确定该选项是否可用于当前上下文，在方法可用时尝试该方法，如果没有执行代码，则继续执行下一个选项。可以看到，执行块中的执行选项包括“CreateThread”、CreateRemoteThread、NtQueueApcThread、NtQueueApcThread
s、RtlCreateUserThread等函数。

CreateThread和CreateRemoteThread函数有一些变体，这些变体使用另一个函数的地址生成一个挂起的线程，更新挂起的线程以执行注入的代码，并恢复该线程。使用[function]”module!function+0x##”指定要欺骗的起始地址。对于远程进程，多使用ntdll和kernel32模块。可选的0x##部分是添加到起始地址的偏移量。这些变体只适用于x86到x86和x64到x64注入。

SetThreadContext和NtQueueApcThread-s函数特定于为恶意payload的后开发作业（Post Exploitation
Jobs）启动临时进程。这些函数会挂起进程的主线程，并使用它执行被注入的后开发恶意功能。

NtQueueApcThread、RtlCreateUserThread和CreateRemoteThread是向远程进程注入代码的常用函数。RtlCreateUserThread函数有一个用于x86到x64注入的实现变体。CreateRemoteThread和RtlCreateUserThread都处理x64到x86注入。所有其他函数包括x86到x86和x64到x64的注入。

Post Exploitation Jobs-很多Cobalt Strike的后开发（post-exploitation）特性（比如屏幕截图、键盘记录、哈希存储等）被实现为Windows的dll。为了执行这些特性，Cobalt
Strike生成一个临时进程，并将这些功能注入其中，进程控制块（process-inject block）控制这一进程注入步骤。后开发控制块（post-ex
block）（见图35）则控制Cobalt Strike后开发特性的特定内容和行为。

![](https://images.seebug.org/content/images/2020/04/cbc90608-da2b-4b50-841f-ad77d2110df2.png-w331s)

图35 post-ex block

下图是我们的研究人员在搭建的Cobalt
Strike攻击环境后，执行恶意命令，受害机器进程的监控情况，从图中可以看到，每当执行一个截图命令或者“spawn”等“后渗透”相关命令，在受害机器上都会新起一个rundll32进程和攻击服务器通信。

![](https://images.seebug.org/content/images/2020/04/e2a3f8af-6c13-4540-9654-57e13d020736.png-w331s)

图36 后渗透相关功能

## 总结

本文揭秘了Cobalt Strike框架的在野使用情况并深入介绍了相关木马的核心技术。Cobalt
Strike使用者遍布全球，不论是APT组织还是红队人员，都被该框架出色的易用性、可扩展性以及隐匿性所吸引。我们也观察到几类现象，一是越来越多的攻击者开始选择商业软件作为攻击武器，一方面能够降低代码被溯源的可能性，另一方面也可以有效降低攻击成本；二是攻击者越发重视自身的隐蔽性，大量采用了域名仿造、CDN、域前置、DNS隧道、流量伪装等技术对抗检测，而Cobalt
Strike框架本身在通信隐匿方面具有很大的优势，其不仅提供了http、https、dns、smb等多种主流上线协议，还支持自定义通信流量特征，这也促成了其在全世界的广泛流行；三是目前主流的威胁情报平台和检测防御系统面临越来越大的压力，在面对Cobalt
Strike这类隐匿方式多样、对抗手段丰富的攻击武器时，大量未知的APT攻击难以被发现和披露，这也需要持续加强深度有效的特征指纹、流量分析和关联分析等能力，以应对越来越复杂的网络攻击活动。

无论怎样，恶意攻击的关键步骤是传播和落地，防重于治，在恶意攻击造成严重损失后再去修补漏洞显然只是无奈的选择，安全管理最重要的还是对人的管理，需要从源头把好关、“治病于未病”。因此，不管是对于企业还是个人，都应该加强安全意识，不要轻易打开未知来源的邮件和附件，不轻易点击未知链接，不打开不可靠的文档，不执行未知的程序，及时更新系统补丁和应用程序，守住我们的系统和数据安全。

## 附录

beacon命令列表

**命令** | **描述**  
---|---  
argue | Spoof arguments for matching processes  
browserpivot | Setup a browser pivot session  
bypassuac | Spawn a session in a high integrity process  
cancel | Cancel a download that's in-progress  
cd | Change directory  
checkin | Call home and post data  
clear | Clear beacon queue  
connect | Connect to a Beacon peer over TCP  
covertvpn | Deploy Covert VPN client  
cp | Copy a file  
dcsync | Extract a password hash from a DC  
desktop | View and interact with target's desktop  
dllinject | Inject a Reflective DLL into a process  
dllload | Load DLL into a process with LoadLibrary()  
download | Download a file  
downloads | Lists file downloads in progress  
drives | List drives on target  
elevate | Try to elevate privileges  
execute | Execute a program on target (no output)  
execute-assembly | Execute a local .NET program in-memory on target  
exit | Terminate the beacon session  
getprivs | Enable system privileges on current token  
getsystem | Attempt to get SYSTEM  
getuid | Get User ID  
hashdump | Dump password hashes  
help | Help menu  
inject | Spawn a session in a specific process  
jobkill | Kill a long-running post-exploitation task  
jobs | List long-running post-exploitation tasks  
kerberos_ccache_use | Apply kerberos ticket from cache to this session  
kerberos_ticket_purge | Purge kerberos tickets from this session  
kerberos_ticket_use | Apply kerberos ticket to this session  
keylogger | Inject a keystroke logger into a process  
kill | Kill a process  
link | Connect to a Beacon peer over a named pipe  
logonpasswords | Dump credentials and hashes with mimikatz  
ls | List files  
make_token | Create a token to pass credentials  
mimikatz | Runs a mimikatz command  
mkdir | Make a directory  
mode dns | Use DNS A as data channel (DNS beacon only)  
mode dns-txt | Use DNS TXT as data channel (DNS beacon only)  
mode dns6 | Use DNS AAAA as data channel (DNS beacon only)  
mode http | Use HTTP as data channel  
mv | Move a file  
net | Network and host enumeration tool  
note | Assign a note to this Beacon  
portscan | Scan a network for open services  
powerpick | Execute a command via Unmanaged PowerShell  
powershell | Execute a command via powershell.exe  
powershell-import | Import a powershell script  
ppid | Set parent PID for spawned post-ex jobs  
ps | Show process list  
psexec | Use a service to spawn a session on a host  
psexec_psh | Use PowerShell to spawn a session on a host  
psinject | Execute PowerShell command in specific process  
pth | Pass-the-hash using Mimikatz  
pwd | Print current directory  
reg | Query the registry  
rev2self | Revert to original token  
rm | Remove a file or folder  
rportfwd | Setup a reverse port forward  
run | Execute a program on target (returns output)  
runas | Execute a program as another user  
runasadmin | Execute a program in a high-integrity context  
runu | Execute a program under another PID  
screenshot | Take a screenshot  
setenv | Set an environment variable  
shell | Execute a command via cmd.exe  
shinject | Inject shellcode into a process  
shspawn | Spawn process and inject shellcode into it  
sleep | Set beacon sleep time  
socks | Start SOCKS4a server to relay traffic  
socks stop | Stop SOCKS4a server  
spawn | Spawn a session  
spawnas | Spawn a session as another user  
spawnto | Set executable to spawn processes into  
spawnu | Spawn a session under another PID  
ssh | Use SSH to spawn an SSH session on a host  
ssh-key | Use SSH to spawn an SSH session on a host  
steal_token | Steal access token from a process  
timestomp | Apply timestamps from one file to another  
unlink | Disconnect from parent Beacon  
upload | Upload a file  
wdigest | Dump plaintext credentials with mimikatz  
winrm | Use WinRM to spawn a session on a host  
wmi | Use WMI to spawn a session on a host  
  
## 参考

  1. <https://blog.fox-it.com/2019/02/26/identifying-cobalt-strike-team-servers-in-the-wild/>

  2. <https://blog.cobaltstrike.com/category/cobalt-strike-2/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1190/>

