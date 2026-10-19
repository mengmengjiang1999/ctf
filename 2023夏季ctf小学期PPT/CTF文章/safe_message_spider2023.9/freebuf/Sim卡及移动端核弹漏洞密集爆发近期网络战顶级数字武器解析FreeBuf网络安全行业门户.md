2019年下半年以来，伴随着两个核弹级Sim卡漏洞披露，多个Android和IOS漏洞的曝光，关于对应漏洞的移动设备武器又将纳入各国网络武器库，而需要注意的是，其中有多个漏洞已经被武器化且被利用。

  

奇安信威胁情报中心红雨滴安全团队在对这几起曝光的漏洞事件进行分析后，综合得出以下结论：网络战争将携移动设备武器，针对随身携带设备对目标进行监听和攻击。

  

为了更好理解事态的严重性，我们将这几起漏洞事件进行简单分析后，公布于此，以供参考。

**S** **imjacker** **漏洞** **与S** **S7** **攻击** ****

首先是曝光的第一个Sim卡漏洞，在此之前，先介绍一下现代SIM卡，

现代SIM卡是一个软件和硬件的组合产品，如下图[1]所示，具有系统、文件、指令、业务四层结构。其中需要过多谈及软件部分，COS也就是SIM卡的操作系统。

![图片.png](https://image.3001.net/images/20191010/1570702442_5d9f046a8b1dc.png!small)  

而这里的卡，指的是USIM卡，也就是通用用户识别模块，其中UICC(通用集成电路卡)上便搭载着S@T 浏览器。

![图片.png](https://image.3001.net/images/20191010/1570702455_5d9f04771b5af.png!small)  

而Simjacker漏洞触发的原因主要由于，部分运营商发行的SIM卡中S@T
浏览器对收到的消息有效性所对应的安全配置存在校验错误，由于S@T浏览器通常使用短信与S@T网关进行交互，因此如果Sim卡的网关侧不过滤构造的漏洞利用数据包，并可成功将载荷发送到目标的S@T浏览器，即可满足第一个攻击条件。而第二条件则需要确定目标的SIM卡确实安装了S@T浏览器。

![图片.png](https://image.3001.net/images/20191010/1570702466_5d9f0482806d4.png!small)

满足条件后，则实现对目标进行远程攻击，例如：

1、发送虚假信息（例如通过发送带有攻击者控制内容的SMS / MMS消息）

2、欺诈（例如通过拨打额外费率号码），

3、间谍活动（以及通过拨打号码来检索攻击设备的位置，充当窃听设备），

4、恶意软件传播（通过强制浏览器打开包含恶意软件的网页）

5、拒绝服务攻击（例如禁用SIM卡）

6、信息检索（检索语言，无线电类型，电池电量等其他信息）

其中，需要注意的是，Simjacker已经被国家网军所使用至少两年之久，在野攻击中所使用的Simjacker消息具有以下结构

![图片.png](https://image.3001.net/images/20191010/1570702486_5d9f0496d2c2d.png!small)

  

而根据Adaptive的白皮书显示，网军的攻击目标绝大多数目标移动用户来自 **墨西哥** ，而这些特定的攻击者偶尔会针对来自 **哥伦比亚和秘鲁**
的移动用户，但与针对墨西哥的目标设备相比，这些用户量要小的多。

  

而在这其中，有45%的用户仅被攻击了一次，而少数用户被攻击了数千次。

  

需要注意的是，发起Simjacker攻击消息的绝大多数来源均为真实设备，在这里有需要提及一个概念。

  

7号信令，又称为公共信道信令。即以时分方式在一条高速数据链路上传送一群话路信令的信令方式，通常用于局间。SS7网络是一个带外数据通信网，它叠加在运营者的交换网之上，是支撑网的重要组成部分。

这里提到的SS7，就是攻击者接入用于攻击的网络，Adaptive记录了多个SS7地址，发现其遍布全球，并试图向墨西哥移动用户发送带有Simjacker
Attack的SMS(短信)消息。

通过这些地址，还发现网军除了使用Simjacker发起攻击外，还会使用经典的SS7攻击，即通过老旧的SS7漏洞进行电话窃听。因为平时根本用不到SS7，算是电信骨干网中用于在特定时候维护通信的存在，目前被用于设置漫游，以便能在在所属运营商范围之外也能拨打电话收发短信。域外运营商会通过SS7向所属运营商发送获取手机唯一ID的请求以便跟踪手机，还会请求手机通信被重定向到它的网络以便投递呼叫和短信。这是一种确保跨网络通信的手段。

因此，任何能登入SS7网络服务器或网关的人，都可以向电信公司发送位置漫游和重定向请求，而电信公司多半会遵从请求，即使漫游请求是从圣彼得堡或孟买发出而你的手机却在纽约。这就使得攻击者可以远程窃听立法者、公司高管、军方人员、激进分子和其他人士。[2]值得注意的是，通过劫持你的短信和通话，攻击者也就能够获取Gmail和其他服务通过短信发送的双因子身份验证登录码。已经知道用户名和密码的攻击者就能在你收到之前拦截验证码，登录你的账户。目前这类漏洞已经得到缓解，但是仍然存在。

这也说明为什么，能登入SS7网络发起攻击的黑客，很大概率具备国家背景的原因。

最后，除了SS7来源外，网军还会通过VASP短代码发送的SMS
Simjacker攻击，该代码直接将这些消息提交给目标运营商SMSC。这样做是为了避免过滤设置，因为这样做可以使得目标认为来自VASP源的消息是安全可信的。

![图片.png](https://image.3001.net/images/20191010/1570702528_5d9f04c0ce0d2.png!small)  

最后，白皮书提到了一点，这个负责进行监视的攻击者，实际上是一个监视公司，然后其会将SS7攻击的访问权出售给众多国家，因此造成了攻击目标的不同，目前他们不便透露具体的监视公司。

目前有以下范围的国家使用了未设置安全级别的S@T浏览器的SIM卡。

![图片.png](https://image.3001.net/images/20191010/1570702536_5d9f04c89f685.png!small)  

更多细节请见文末的白皮书[3]

**WIBattack漏洞** ****

 ****

上面提到的Simjacker漏洞被披露后不久，Ginno安全实验室介绍了一个名为WIBattack的漏洞，而这也在Adaptive白皮书中记录了：
**S@** **T** **浏览器不是唯一可以被利用的S** **IM** **卡应用程序，从理论上讲，任何S** **IM**
**卡应用程序也可能受到类似Sim** **J** **acker的攻击，W** **IB** **也是。**

WIB，无线因特网浏览器，他可以使移动运营商能够提供先进的动态更新和下载机制，下载应用和插件（浏览器功能的延伸）到SIM卡。这是一种SmartTrust公司提出的集成在SIM卡中的浏览引擎标准，能解释WML（Wireless
Markup Language）无线标识语言。

此外，WIB起着菜单驱动器的作用，并会预先驻留在手机SIM卡中，负责解释并处理已经转换为WML的下载请求和菜单数据。

Ginno称，他们发现该漏洞在2015年对全球数亿电信用户造成了严重损害，并且该漏洞尚未发布。

通过向受害人的电话号码发送恶意短信，攻击者可以使用WIB sim浏览器中的漏洞来
**远程控制受害人的手机以执行有害操作，例如：发送短信，打电话，获取受害人的位置，启动其他浏览器（例如WAP浏览器），获取受害者的IMEI等。** ****

 ****

攻击场景如下所示，首先攻击者向受害人的电话号码发送了恶意的OTA SMS，也就是空中下载短信，OTA
SMS中包含了WIB命令，当受害者受到信息后，其会立即使用Envelop命令(一条在手机和SIM卡之间进行通信的应用协议数据单元APDU命令)将OTA
SMS的传送协议数据单元转发到受害者Sim卡中的WIB浏览器。

需要注意的是，OTA SMS的接收过程是静默处理，不会有任何提醒。

**![图片.png](https://image.3001.net/images/20191010/1570702559_5d9f04df9d367.png!small)**

****

紧接着，WIB浏览器遵循OTA SMS的TPDU中的WIB命令，并将上面提及到的例如要求发送短信的命令发送到受害者手机上。这样受害者就会按照命令执行。

下图未几个敏感的WIB命令。

![图片.png](https://image.3001.net/images/20191010/1570702568_5d9f04e883b7d.png!small)  

如果SIM卡开启了关键安全功能，那么攻击者无法通过短信的形式实现攻击，由于装载了无线互联网浏览器功能WIB的SIM卡理论上都会面临威胁，初步估算影响数量达到上亿级。

更多细节请见文末链接[4]

**I** **OS** **越狱漏洞** ****

在讨论完SIM卡的威胁后，我们把注意力放回到移动端操作系统层面，下面将搬出日前沸沸扬扬的IOS硬件越狱漏洞，由iOS安全研究者@axi0mX披露，存在于iOS设备上的BootROM漏洞，他将其命名为checkm8，读作checkmate，也就是国际象棋术语中的“将死”。

目前他已经将漏洞的利用方法更新进了他自己编写的开源越狱工具ipwndfu中，并且目前已经有人成功使用该工具在有漏洞的设备上面读取苹果的SecureROM。

![图片.png](https://image.3001.net/images/20191010/1570702580_5d9f04f4d3f5c.png!small)  

BootROM漏洞存在于硬件之上，无法通过软件来修复。而这个漏洞存在于从A5开始到A11的所有Apple A系列处理器之上，影响了从iPhone
4S开始到iPhone 8、iPhone X的所有iPhone，还有其他使用同款A系列处理器的iPad、iPod touch等iOS设备。

而该漏洞，虽说因为要进入DFU模式才可以越狱，但是对于攻击者来说，将仍是利器：这将会导致在通过某些渠道获取到用户苹果手机后，在进行越狱操作后获取用户的资料，这对于某些部门来说将是一把利剑。

代码细节请见文末github[5]

**安卓高危提权漏洞** ****

10月4日，谷歌发布安卓高危漏洞，华为、三星、小米等手机型号设备受影响。目前该提权漏洞已被修复，并将在10月安全更新中发布。谷歌发现该漏洞被以色列的NSO集团利用并武器化售卖。

谷歌ProjectZero研究小组成员Maddie
Stone发帖称，该小组日前发现安卓系在野0day漏洞。上述漏洞于9月27日首次向安卓团队公开，并被要求在7天之内修复，10月4日向社会公开。

![图片.png](https://image.3001.net/images/20191010/1570702597_5d9f05058d98d.png!small)

作为本地特权升级漏洞，此次发布的漏洞只需要很少或根本不需要定制即可完全获得被攻击手机的root权限，可通过安装不受信任的应用或于Chrome浏览器内容结合攻击受影响的手机。谷歌随后公布了多款可受攻击的手机型号，包括多款三星手机、谷歌Pixel手机，还有华为、小米、OPPO等品牌。

1) Pixel 2 with Android 9 and Android 10 preview

2) Huawei P20

3) Xiaomi Redmi 5A

4) Xiaomi Redmi Note 5

5) Xiaomi A1

6) Oppo A3

7) Moto Z3

8) Oreo LG phones (run same kernel according to website)

9) Samsung S7, S8, S9

谷歌发现该漏洞在现实世界中已经被利用，并认为以色列的NSO集团正在利用此漏洞。后者是一家涉嫌袭击人权和政治活动家的公司。

该漏洞最初出现在Linux内核中，并于2018年初进行了修补。但并未解释漏洞为何会出现在安卓系统中。

![图片.png](https://image.3001.net/images/20191010/1570702615_5d9f05179318f.png!small)  

POC与相关细节见文末[6]:

**IOS** **漏洞利用链** ****

 ****

谷歌的安全团队Project Zero威胁分析小组（Threat Analysis
Group）发现，iPhone存在14个安全漏洞，目前漏洞均被修复，而这些漏洞被构造成一个攻击链，并且已经被使用两年之久。

具体的利用场景大致为，只要用户访问一个网站，就有可能让黑客获得信息、照片、联系人和位置信息。类似于我们所说的水坑攻击。

这条漏洞链先从水坑攻击出发，通过如下图所示的钓鱼方式，诱使用户点击链接，从而触发漏洞，获取低权限，在通过提权漏洞，突破沙箱，从而最后通过恶意软件时刻监视目标。

![图片.png](https://image.3001.net/images/20191010/1570702634_5d9f052adc1d8.png!small)  

Project Zero 团队预计，这些网站的每周访问数量在数千人。

目前，有五个独立、完整、且独特的 iPhone 漏洞利用链条，发现其影响从 iOS 10 到 iOS 12
的几乎每一个版本。其中涉及内核提权漏洞，以及Chrome浏览器漏洞等。

![图片.png](https://image.3001.net/images/20191010/1570702641_5d9f0531da3ec.png!small)

IOS恶意软件截图

![图片.png](https://image.3001.net/images/20191010/1570702648_5d9f0538d9808.png!small)  

更多细节，见文末链接[7][8]

#  **总结** ****

除了上述的底层漏洞外，APP应用漏洞也极为重要，像近日报道的WhatsApp安全漏洞，通过该漏洞，攻击者可以用恶意GIF动图入侵该软件。当用户在他们的图库中打开一个恶意GIF动图时，就可能触发漏洞，从而导致WhatsApp软件里面的内容被窃取，内容包括用户个人信息和聊天记录。5月，该软件还曾爆出一个漏洞，通过WhatsApp呼叫联系人，并放置恶意代码来查看他们的个人信息。

而这类日常用的聊天软件，或是工具类软件的漏洞，将会在攻击者在使用高价值利用的底层操作系统漏洞之外，更具有目标针对性的漏洞攻击。

而从整体趋势来看，无论是安卓、iOS、Sim卡，还是APP应用漏洞，均与人们日常生活息息相关，现如今按照中国人口比例，拥有智能手机人员可达到人均一部，可想而知，当全面网络战出现之时，敌方若拥有一个相关系统或应用的致命的漏洞，那将会在短期内造成不可恢复的结果，通讯能力必将造成全面瘫痪。

众所周知，当前从桌面端到移动端，所有的操作系统供应商巨头均掌握在美国人手中，而在操作系统受制于人的情况下，拥有全球性自主操作系统权限的一方若发动网络战，结果可想而知。

这也充分说明了，自研操作系统在网络战中的重要性，在确保独立产权，自主创新，才能在日渐激烈的网络对抗中占有一席之地。

然而，现状来看，在等待可用自研操作系统问世前，我们仍然需要使用美国操作系统，因此，我们必须要做到全民戒备状态，所有曝光的操作系统底层漏洞必须及时更新，所有应用程序同样要开启后台自动更新，同时运营商方面也要配合安全研究人员进行Sim卡漏洞修补，这样才能在Nday漏洞打击中，立于不败之地。

奇安信移动安全团队将对移动设备相关的漏洞保持密切的关注，正在开发相应的防护工具和解决方案补上移动安全这个重要的一环。

# **相关链接** ****

[1] SIM卡知识介绍

[
_https://wenku.baidu.com/view/8ea0ab6ca98271fe910ef9aa.html_](https://wenku.baidu.com/view/8ea0ab6ca98271fe910ef9aa.html)

[ _https://mp.weixin.qq.com/s/nDmeTKZE1d2Y5kjn-DswgA_](https://mp.weixin.qq.com/s/nDmeTKZE1d2Y5kjn-DswgA)

[2] 再谈SS7：电话窃听原理揭秘

[ _https://www.aqniu.com/news-views/15581.html_](https://www.aqniu.com/news-views/15581.html)

[3]
[_https://simjacker.com/downloads/technicalpapers/AdaptiveMobile_Security_Simjacker_Technical_Paper.pdf_](https://simjacker.com/downloads/technicalpapers/AdaptiveMobile_Security_Simjacker_Technical_Paper.pdf)

[4]

[ _https://ginnoslab.org/2019/09/21/wibattack-vulnerability-in-wib-sim-browser-can-let-attackers-globally-take-control-of-hundreds-of-millions-of-the-victim-mobile-phones-worldwide-to-make-a-phone-call-send-sms-to-any-phone-numbers/_](https://ginnoslab.org/2019/09/21/wibattack-vulnerability-in-wib-sim-browser-can-let-attackers-globally-take-control-of-hundreds-of-millions-of-the-victim-mobile-phones-worldwide-to-make-a-phone-call-send-sms-to-any-phone-numbers/)

[5]

[ _https://github.com/axi0mX/ipwndfu_](https://github.com/axi0mX/ipwndfu)

[6]

[ _https://bugs.chromium.org/p/project-zero/issues/detail?id=1942_](https://bugs.chromium.org/p/project-zero/issues/detail?id=1942)

[7]

[ _https://googleprojectzero.blogspot.com/2019/08/a-very-deep-dive-into-ios-exploit.html_](https://googleprojectzero.blogspot.com/2019/08/a-very-deep-dive-into-ios-exploit.html)

[8]

[
_https://www.freebuf.com/column/213129.html_](https://www.freebuf.com/column/213129.html)

