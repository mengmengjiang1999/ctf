**译者：知道创宇404实验室翻译组  
原文链接：<https://www.threatfabric.com/blogs/deceive-the-heavens-to-cross-the-sea.html>**

“瞒天过海”策略来源于《三十六计》第一章，这是中国著名的战术和技巧集，适用于政治、战争和人民生活。它的意思就是“隐藏在显而易见的地方”或者“掩盖你真正的目标”。

安卓银行木马黑客已经牢记这一策略，并且多年来一直非常习惯了新的谷歌应用商店对他们的运营的限制。这些限制包括对某些(危险的)应用程序权限的使用设置限制，这些权限常常用于分发或自动化恶意软件策略。

在这个博客中，我们将讨论最近通过 Google Play (MITRE T1475)传播 Android
银行木马所使用的技术，这些技术给目标银行造成了巨大的财务损失。我们还将讨论该技术造成的后果，即银行木马程序收集联系人和按键而导致的严重数据泄露。

## 攻击者使用的战术

![tactics](https://images.seebug.org/content/images/2021/12/07/1638844899000-1owfzw.png-w331s)

从自动化(沙盒)和机器学习的角度来看，这些 Google Play 分发活动很难被发现，因为dropper应用程序的恶意足迹很小。它的内存占用很小是由
Google Play 强制执行的许可限制造成的。

一个很好的例子是2021年11月13日谷歌引入的修改，它限制了无障碍服务的使用，因为在早期，这个服务常常被自动化和安装应用程序的攻击利用，但并没有经过用户的同意。

谷歌的这种监管方式就迫使攻击者另寻他法，大幅度减少dropper 应用程序的占用空间。除了恶意软件代码进一步改进，Google Play
的分发活动也比以前的攻击更加精细。例如，通过在 Google Play 中引入精心策划的小型恶意代码更新，以及使用dropper
c2后端来完全匹配dropper应用程序的主题(例如，一个针对健身的应用程序Fitness 的正常运行的网站)。

为了让木马更难被发现，这些dropper应用程序背后的攻击者只是手动激活被感染设备上的银行木马安装，以控制他们在某个特定地区的受害者数量。这使得安全组织的自动检测策略效用大大降低。

VirusTotal 并没有展示反病毒产品检测的演变，但是几乎所有的活动在 VirusTotal 上都有或者曾有0/62 FUD
评分，这证实了用最小的内存占用检测dropper应用程序的难度。

![tactics](https://images.seebug.org/content/images/2021/12/07/1638844902000-2zwnoy.png-w331s)

## 组织和数据

在下面的段落中，我们概述了最近通过 Google Play 分发的每个团伙的作案手法(MO)。这些组织都有自己的银行应用程序目标列表（见附录）。

![tactics](https://images.seebug.org/content/images/2021/12/07/1638844903000-3odllu.png-w331s)

## Anatsa 攻击活动

在不同恶意软件家族分布技术的研究过程中，我们的分析师发现了大量位于 Google Play 中的dropper应用程序，专门用来分布银行木马
Anatsa。ThreatFabric在2021年1月发现了 Anasta。

Anatsa 是一个相当高级的 Android 银行木马，具有 RAT 和半 ats
功能。它还可以执行经典的覆盖攻击，以窃取凭证、可访问性日志(捕获用户屏幕上显示的所有内容)和键盘记录。此前，ThreatFabric曾报道过
Anatsa与Cabassous一起在欧洲各地的短信诈骗活动的[案例](https://www.threatfabric.com/blogs/smishing-campaign-in-nl-spreading-cabassous-and-anatsa.html)。我们的最新调查结果显示，Anatsa现在使用的是
Google Play dropper应用程序。

**成千上万的受害者**

2021年6月，我们发现了第一个伪装成扫描文档应用程序的dropper。自2021年6月以来，ThreatFabric 分析师总共能够识别出6个发布在
Google Play 上的 Anatsa 软件漏洞。

![Droppers](https://images.seebug.org/content/images/2021/12/07/1638844905000-4qvlsm.png-w331s)

这些应用包括 QR 码扫描器、 PDF 扫描器和加密货币应用程序。有一个dropper应用程序被安装了超过 **5万**
次，所有dropper的安装总数超过 **10万** 次。

![QR
Scanner](https://images.seebug.org/content/images/2021/12/07/1638844907000-5bxtig.png-w331s)

感染 Anatsa 的过程是这样的: 从 Google Play
开始安装时，用户被迫更新应用程序以便继续使用该应用程序。此时，Anatsa有效载荷从C2服务器下载，并安装在毫无戒备的受害者的设备上。

背后的攻击者努力让他们的应用程序看起来合法且有用。它们的评论区有大量的正面评价，安装的次数和评论可能会诱使 Android
用户安装这个应用程序。此外，这些应用程序确实拥有所声称的功能，安装后它们确实正常运行，这进一步说服受害者它们的合法性。

尽管安装了大量的设备，但并不是每一个安装了这些dropper的设备都会接收到
Anatsa，因为攻击者只针对他们感兴趣的地区用户。我们将在下一节讨论这个和其他技术细节。

**技术细节**

所有 Anatsa dropper 在代码级别上看起来很相似。在应用程序启动时，会启动一个服务来检查是否安装了“更新”。dropper向
c2发送关于设备的信息，包括设备 ID、设备名、地区、国家、 Android SDK 版本。

![C2
communication](https://images.seebug.org/content/images/2021/12/07/1638844909000-6amnev.png-w331s)

正如前面提到的，并不是每个设备都会收到“更新”。此时，C2后端根据设备信息决定是否提供 Anatsa
有效载荷，同时，根据C2的响应，dropper将决定是否下载 Anatsa。

![Filtering](https://images.seebug.org/content/images/2021/12/07/1638844910000-7mcgqk.png-w331s)

这种方法使攻击者能够针对特定区域的设备，还可以轻松地将重点转移到另一个区域。这种行为与Anatsa
从一个地区转移到另一个地区，不断更新其目标金融机构名单的行为是一致的。此外，过滤允许网络犯罪分子在 Google Play
上发布应用程序时，阻止dropper在评估过程中下载“更新”。

我们的分析师已经确认， Anatsa dropper最初在 Google Play
上发布的第一个版本中没有恶意功能，但是在后来的版本中修改了他们的行为，增加了植入功能，并且需要更多的权限。

![Versions](https://images.seebug.org/content/images/2021/12/07/1638844912000-8bsgox.png-w331s)

当所有条件都满足并且有效负载准备就绪时，系统将提示用户下载并安装它。

![Update
process](https://images.seebug.org/content/images/2021/12/07/1638844914000-9hnmho.png-w331s)

成功下载“更新”后，用户将被要求安装来自未知来源的应用程序的权限。用户确信更新是应用程序正常工作所必需的，然后授予许可。安装完成后，Anatsa
在设备上运行，并立即请求受害者授予可访问性服务特权。

![Anatsa](https://images.seebug.org/content/images/2021/12/07/1638844915000-10pysoh.png-w331s)

启用可访问性服务后，Anatsa可以完全控制设备，并可以代表受害者执行操作。与此同时，dropper应用程序也作为合法应用程序运行和运行，但受害者可能仍然毫无戒心。

## Hydra 和 Ermac 活动

**Brunhilda : Valkyrie 的回归**

ThreatFabric识别了Brunhilda 组织团伙植入的多个恶意软件案例，与之前的活动一致，它由木马程序化的应用程序组成。

在第一个案例中，我们发现Brunhilda伪装成二维码编码创建应用程序，Brunhilda在已有的软件系列，比如 [Hydra
](https://www.threatfabric.com/blogs/bianlian_from_rags_to_riches_the_malware_dropper_that_had_a_dream.html)以及新奇的软件系列，比如
[Ermac ](https://www.threatfabric.com/blogs/ermac-another-cerberus-reborn.html)中置入样本。

![Brunhilda  dropping Hydra and Ermac on
GP](https://images.seebug.org/content/images/2021/12/07/1638844917000-11fstqq.png-w331s)

这次Brunhilda
攻击中放置的应用程序与我们在2021年观察到的旧版本的应用程序在功能上没有太大的不同。正如它在之前的迭代中所做的那样，Brunhilda 使用 gRPC
协议向其 C2发送注册请求。成功注册后，在传递更多关于设备的详细信息之后，C2指示dropper下载并安装有效载荷包。

![Brunhilda
installation](https://images.seebug.org/content/images/2021/12/07/1638844919000-12gaogd.png-w331s)

在过去的几个月里，两个木马都非常活跃，甚至冒险进入以前没有开发过的市场，比如美国。这种新的恶意软件浪潮始于2021年8月，其中也包括像 Gustuff 和
Anatsa 这样的恶意软件。

![US
campaigns](https://images.seebug.org/content/images/2021/12/07/1638844920000-13nozjt.png-w331s)

## Alien 攻击活动

正如前面提到的，ThreatFabric发现，Brunhilda提供不同的恶意软件家族。一些样本有超过5万次的安装，并且置入了安卓木马[Alien
](https://www.threatfabric.com/blogs/alien_the_story_of_cerberus_demise.html)。

![Brunhilda dropping Alien on
GP](https://images.seebug.org/content/images/2021/12/07/1638844922000-14jmcry.png-w331s)

在这种情况下，正如[Vultur ](https://www.threatfabric.com/blogs/vultur-v-for-vnc.html)的部署一样，这些应用软件在从商店下架之前达到了数千次下载。这些样本取得了非常显著的效果，从5前多次到5万多次的下载量足以见得。考虑到这个数字，可以肯定地说，这个dropper家族可能在运行期间感染了成千上万的受害者。

**Gymdrop**

2021年11月，ThreatFabric分析师在 Google Play 中发现了另一个dropper。它伪装成一个健身的应用程序，有10.000次安装。

![Gymdrop](https://images.seebug.org/content/images/2021/12/07/1638844924000-15luywr.png-w331s)

这个dropper，我们称之为“
Gymdrop”，背后的黑客试图说服受害者和检测系统他们的应用程序是合法的。这个应用程序网站的设计初看起来是正常的，然而，它只是一个健身网站的模板，没有任何有用的信息，甚至在它的页面上仍然包含着“
Lorem Ipsum”占位符文本。

![Developer
website](https://images.seebug.org/content/images/2021/12/07/1638844926000-16glouk.png-w331s)

开发者的网站也是 Gymdrop 的
C2。就像之前观察到的一样，这个dropper试图说服受害者安装一个虚假的更新。然而，在这种情况下，它是以一种更具创造性的方式完成的:
有效载荷是按照应用程序的要求，作为一个新的锻炼练习资源。当用户单击“ OK”后，dropper将请求所需的权限。

![Gymdrop update
process](https://images.seebug.org/content/images/2021/12/07/1638844927000-17rwljh.png-w331s)

在dropper从C2得到它的配置后不久。配置文件包含下载有效负载的链接。此外，配置包含基于设备模型的过滤规则。根据被过滤掉的模型和dropper的代码，我们可以得出这样的结论:
这样做是为了避免在模拟器或研究环境中下载有效负载。

![Gymdrop
filtering](https://images.seebug.org/content/images/2021/12/07/1638844929000-18azzfg.png-w331s)

如果满足所有条件，将下载并安装有效载荷。这个dropper也没有请求无障碍服务特权，它只是请求安装软件包的许可，并承诺安装新的锻炼资源——用以吸引用户授予这种许可。安装完成后，有效载荷就启动了。我们的威胁情报显示此时此刻这个dropper被用来分发外银行木马
Alien。

![Alien
installation](https://images.seebug.org/content/images/2021/12/07/1638844931000-19jwdiu.png-w331s)

在写这篇博文的时候，Gymdrop 更新了(一个新版本被上传到了 Google Play)。但是，在 C2上没有找到配置文件。在 Google Play
上发布更新之前，不提供有效载荷或许是为了通过 Google 执行的安全检查。

**2个dropper应用程序推动僵尸网络建设**

值得一提的是，这个活动的 Alien样本与之前描述的由Brunhilda dropper驱动的攻击活动样本连接到相同的C2。

![Alien
campaigns](https://images.seebug.org/content/images/2021/12/07/1638844932000-20tdslv.png-w331s)

于是我们得出结论，这些Alien活动背后的攻击者在他们的分发策略中使用至少2种不同的dropper服务。

## 总结

![timeline on
GP](https://images.seebug.org/content/images/2021/12/07/1638844934000-21wfcyw.png-w331s)

在仅仅4个月的时间里，4个大的安卓木马家族通过 Google Play 传播，30多万人受到多个dropper应用程序感染。

在新的dropper运动中，一个明显的趋势是，黑客们更关注装载机，减少了 Google Play 中的恶意足迹，大大增加自动化和机器学习技术检测它们的难度。

这种小规模的恶意行为是用来应对 Google Play 的新限制(目前和计划中的)，Google Play
限制了与应用程序权限有关的隐私权的使用，如可访问性服务这样的权限，在以前的活动中，可访问性服务是 dropper 应用程序自动化安装 Android
银行木马的核心策略之一。

通过限制这些权限的使用，攻击者们被迫选择更传统的安装应用的方式，也就是请求安装许可，这样做的话，木马程序便与合法的应用程序难以区分了。这是移动银行木马攻击者成功潜入谷歌信任的应用程序商店的核心原因之一。

成功背后的第二个重要因素是攻击者设置了限制，通过机制确保有效载荷只安装在受害者的设备上，而不是安装在测试环境中。为了实现这一点，犯罪分子使用了多种技术，从位置检查到恶意增量更新，逃过了基于时间的解模糊处理和服务器端仿真检查。

攻击者格外的专注于规避不必要的注意，自动化的恶意软件检测不那么有效了。我们在这篇博文中调查了9个dropper，他们的总体 VirusTotal
得分非常低，这证实了我们的观点。

## IOC

### Brunhilda Dropper Samples

App name | Package name | SHA-256  
---|---|---  
Two Factor Authenticator | com.flowdivison |
a3bd136f14cc38d6647020b2632bc35f21fc643c0d3741caaf92f48df0fc6997  
Protection Guard | com.protectionguard.app |
d3dc4e22611ed20d700b6dd292ffddbc595c42453f18879f2ae4693a4d4d925a  
QR CreatorScanner | com.ready.qrscanner.mix |
ed537f8686824595cb3ae45f0e659437b3ae96c0a04203482d80a3e51dd915ab  
Master Scanner Live | com.multifuction.combine.qr |
7aa60296b771bdf6f2b52ad62ffd2176dc66cb38b4e6d2b658496a6754  
  
### Brunhilda Dropper C2 URL

**URL**  
hxxps://protectionguardapp[.]club  
hxxps://readyqrscanner[.]club  
hxxps://flowdivison[.]club  
hxxps://multifuctionscanner[.]club

### Anatsa Dropper Samples

App name | Package name | SHA-256  
---|---|---  
QR Scanner 2021 | com.qr.code.generate |
2db34aa26b1ca5b3619a0cf26d166ae9e85a98babf1bc41f784389ccc6f54afb  
QR Scanner | com.qr.barqr.scangen |
4e9a95719e4b4748dba1338fdc5e4c7622b029bbcd9aac8a1caec30b5508db4  
PDF Document Scanner - Scan to PDF | com.xaviermuches.docscannerpro2 |
2080061fe7f219fa0ed6e4c765a12a5bc2075d18482fa8cf27f7a090deca54c5  
PDF Document Scanner | com.docscanverifier.mobile |
974eb933d687a9dd3539b97821a6a777a8e5b4d65e1f32092d5ae30991d4b544  
PDF Document Scanner Free | com.doscanner.mobile |
16c3123574523a3f1fb24bbe6748e957afff21bef0e05cdb3b3e601a753b8f9d  
CryptoTracker | cryptolistapp.app.com.cryptotracker |
1aafe8407e52dc4a27ea800577d0eae3d389cb61af54e0d69b89639115d5273c  
  
### Anatsa Dropper C2 URL

**URL**

hxxp://195.201.70.88/api/update hxxp://178.63.27.179/api/update
hxxp://91.242.229.85/api/update hxxp://195.201.70.89/api/update

### Gymdrop Dropper Samples

App name | Package name | SHA-256  
---|---|---  
Gym and Fitness Trainer | com.gym.trainer.jeux |
30ee6f4ea71958c2b8d3c98a73408979f8179159acccc01b6fd53ccb20579b6b  
Gym and Fitness Trainer | com.gym.trainer.jeux |
b3c408eafe73cad0bb989135169a8314aae656357501683678eff9be9bcc618f  
  
### Gymdrop Dropper C2 URL

**URL**

hxxps://onlinefitnessanalysis[.]com/

### 置入的恶意软件样本

Malware Family | App name | Package name | SHA-256  
---|---|---|---  
Alien.A | Master Scanner Live | leaf.leave.exchang |
74407e40e1c01e73087442bcdf3a0802121c4263ab67122674d9d09b3edf856e  
Alien.A | Gym and Fitness Trainer | gesture.enlist.say |
e8cbcc34af3bd352767b7a9270dd684a50da2e68976a3712675526a7398550a0  
Anatsa.A | PDF AI : TEXT RECOGNIZER | com.uykxx.noazg |
d42e0d3db3662e809af3198da67fdbd46d5c2a1052b5945401e4cdd06c197714  
Hydra.C | QR CreatorScanner | com.cinnamon.equal |
9ab66c1b7db44abaa53850a3d6a9af36c8ad603dab6900caba592497f632349f  
Ermac.A | QR CreatorScanner | com.tag.right |
fd7e7e23db5f645db9ed47a5d36e7cf57ca2dbdf46a37484eafa1e04f657bf02  
  
* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1778/>

