**作者：启明星辰ADLab  
公众号：[ADLab](https://mp.weixin.qq.com/s/wb_eFxAjQMChegjlTB0lDw "ADLab")**

### **1、概述**

2019年2月中旬，启明星辰ADLab发现了一款全新的Android银行钓鱼木马，该木马将自身伪装成“Google
Play”应用（见图1），利用系统辅助服务功能监控感染设备，以便在合法的银行APP运行时，启用对应的伪造好的银行钓鱼界面将其覆盖掉，来窃取受害用户的银行登录凭证。此次攻击的目标银行默认包含包括花旗银行在内的三十多家银行（见图2），因此我们将之命名为“BankThief”。“BankThief”的存在和传播无疑对这数十银行客户的财产安全构成了严重的威胁。

![img](https://images.seebug.org/content/images/2019/03/07/1551936468000-wps5D5E.tmp.jpg-w331s)

图1 “BankThief”将自身伪装成“Google Play”

![img](https://images.seebug.org/content/images/2019/03/07/1551936469000-wps5D5F.tmp.jpg-w331s)

图2 目标银行的logo

“BankThief”会根据感染设备本地语言来配置自身显示语言，配置语言包括捷克语和波兰语，而且“BankThief”链接的钓鱼页面服务器上配置有针对波兰和捷克的伪装银行钓鱼页面，因此我们推测“BankThief”的主要攻击目标国家为波兰和捷克。该木马的证书签名起始时间是2019年2月13日，存放恶意钓鱼页面的服务器域名为“anlixes.at”，从该域名的解析记录来看，该域名主要活跃时间为2019年1月28日至2月21日。据此可推断，“BankThief”开发和传播的时间应该在2019年1月底到2月初这个时间段。

启明星辰ADLab研究人员对比了2018年9月LUKAS STEFANKO（ESET安全研究员）披露的一款银行木马（MD5 =
03720d4e7ae807f7c8ce56e772c19bcc）后发现，“BankThief”与其有少许相似之处。比如，两款银行木马的攻击目标都包含捷克和波兰；都是通过伪装的钓鱼页面覆盖掉目标银行合法的界面进行钓鱼攻击；都使用了Google
Firebase云消息传递服务进行控制命令的下发。不过，他们的整体设计和代码实现机制却完全不同，也没有很强证据表明这两款银行木马存在关联性，因此我们认为“BankThief”是一款全新的木马。

值得注意的是，“BankThief”是使用Google
Firebase云消息传递服务来控制感染设备的。该服务首次被用于恶意攻击要追溯到高级间谍软件“Skygofree”，
2018年3月启明星辰ADLab对已其进行详细分析，并发布深度分析报告[《首款利用Firebase云消息传递机制的高级间谍软件》](https://mp.weixin.qq.com/s?__biz=MzAwNTI1NDI3MQ==&tempkey=OTk4X0xTL3JXRDVCdGVJdEw5SEJtLUFYUmJnNXRqYVd3Yk9mTVpSemZNY3FWUUU3SVROQ0JqTS11SkFKLVFoTkdGb3lZMF9ackdFYWQ2RzY5UDNIWTFxZmtsU1dkNGdRa0NxTlpZeG10eGRUY2U5UnItbEVvZ1Q3WndFaDZvRzdNWHRIN0NhZzQyNDV3ak1DWFJPa3)。攻击者将恶意命令通过Firebase云消息服务进行传送，一方面不必耗费精力和资源去配置C&C服务器；另一方面，攻击者将恶意命令隐藏在安全的Firebase通信隧道中，避免了攻击流量被网络安全设备处置，攻击性更加隐蔽。Google
Firebase云消息传递服务此次又被“BankThief”用来进行恶意攻击，可以预见，越来越多的恶意应用将会使用Firebase云消息服务来实施攻击。

### **2、木马行为简介**

“BankThief”感染目标设备后，首先通过无障碍服务（无障碍服务是辅助身体不便或者操作不灵活的人来操作手机应用的，其可以被用于监控手机当前活动APP界面，实现对目标界面自动化操作。）监控感染设备。当监控到目标银行应用被打开时，银行木马会启动对应的伪装好的钓鱼页面覆盖掉真实的银行APP界面，在受害用户没有察觉的情况下窃取其银行登录凭证，“BankThief”会进一步将自身设置成默认短信应用来拦截银行短信，这样就绕过了基于SMS短信的双因素验证机制。其次，“BankThief主要利用Google
Firebase 云消息传递服务（Google Firebase
云消息传递服务是Google提供的能帮助开发者快速写出Web端和移动端应用通信的一种服务）来对感染设备进行远控，包含清空用户数据、卸载指定应用等恶意操作以及劫持包括花旗银行在内的数十家银行APP应用的恶意行为。“BankThief”的攻击示意图见图3。

![img](https://images.seebug.org/content/images/2019/03/07/1551936469000-wps5D60.tmp.jpg-w331s)

图3 “BankThief”攻击示意图

### **3、功能分析**

“BankThief”的代码中，大量的字符串被加密存储（如图4），只有在其运行的过程中，在需要时才会使用自定义的解密算法进行解密操作（图5只列出其中一个解密算法），并且从多个“ALLATORIXDEMO”命名的函数名来看，“BankThief”使用了混淆器“Allatori”的Demo版来保护自身，这无疑增加了研究人员分析的难度和工作量。

![img](https://images.seebug.org/content/images/2019/03/07/1551936469000-wps5D70.tmp.jpg-w331s)

图4 被加密存储的字符串

![img](https://images.seebug.org/content/images/2019/03/07/1551936469000-wps5D71.tmp.jpg-w331s)

图5 其中的一个字符串解密函数

“BankThief”利用无障碍服务对感染设备进行监控，实施钓鱼攻击。木马将自身伪装成“Google
Service”服务，在诱使受害者开启对应的无障碍服务权限成功后，会利用无障碍服务监控感染设备的运行。当目标银行APP启动时，它会启动伪造好的对应钓鱼界面覆盖掉合法的银行APP界面，窃取受害用户的银行凭证。

此外，“BankThief”还试图阻止用户取消其管理员权限和限制三星系统管理应用的正常运行等手段来保障自身的安全。

#### **3.1 诱使用户开启恶意服务**

“BankThief”诱使受害用户开启无障碍服务界面下伪装成“Google
Service”的恶意服务，并且还隐藏了自身图标（见图6），防止受害用户察觉到异常。

![img](https://images.seebug.org/content/images/2019/03/07/1551936469000-wps5D72.tmp.jpg-w331s)

图6伪装成“Google Service”服务

在诱导受害用户操作的过程中，应用会跳转到无障碍设置界面，诱导受害用户开启“Google
Service”服务。“BankThief”会根据受害用户手机系统来选择使用捷克语还是波兰语提示（很显然，攻击者主要攻击的目标为波兰和捷克），如果用户没有开启该权限，会不停提示，直到受害用户开启为止（见图7）。

![img](https://images.seebug.org/content/images/2019/03/07/1551936469000-wps5D73.tmp.jpg-w331s)

图7 诱导受害用户开启“Google Service”

#### **3.2 利用无障碍服务监控设备**

“BankThief”利用无障碍服务监控感染设备界面，来窃取受害用户银行登录凭证。当感染设备运行目标银行APP时，木马就会打开其设置好的对应钓鱼界面，覆盖在合法的银行APP上面，神不知鬼不觉地拿走受害用户的银行登录凭证（见图8）。

![img](https://images.seebug.org/content/images/2019/03/07/1551936469000-wps5D74.tmp.jpg-w331s)

图8 窃取受害用户银行登录凭证

#### **3.3 请求设备管理员权限并防止取消**

“BankThief”运行后，不但会将自身图标隐藏掉（见上图6），而且会激活其设备管理员权限（见图9）。这样，普通用户很难察觉并卸载掉它，从而达到长期驻留在受害用户设备中的目的。

![img](https://images.seebug.org/content/images/2019/03/07/1551936469000-wps5D75.tmp.jpg-w331s)

图9 诱导受害用户设置自身为管理员权限

此外，“BankThief”还利用无障碍服务监控感染设备，一旦发现受害用户试图取消管理员权限就强制返回，依靠这种流氓行为，阻止自身管理员权限被取消（见图10）。

![img](https://images.seebug.org/content/images/2019/03/07/1551936469000-wps5D76.tmp.jpg-w331s)

图10 阻止自身管理员权限被取消

#### **3.4 阻止三星应用“Device Maintenance”**

“BankThief”一旦发现感染设备运行三星设备维护软件“Device Maintenance”，就强制返回桌面。“Device
Maintenance”是三星研发的针对Android手机维护和优化的一款系统管理应用，可以对一些流氓和耗电的APP发出警告并且会主动关闭不必要的后台程序，“BankThief”大概是防止自身被该款应用检测和卸载才使用此流氓手段阻止其被打开（见图11）。“BankThief”的这一功能大概和三星手机在波兰领先的市场份额有很大关系。

![img](https://images.seebug.org/content/images/2019/03/07/1551936469000-wps5D87.tmp.jpg-w331s)

图11 阻止三星应用“Device Maintenance”

### **4、命令控制分析**

“BankThief”使用了Google
Firebase云消息传递服务来进行控制命令的下发。攻击者利用Firebase云消息传递控制命令和http协议回传执行结果到自己控制的恶意服务器“anlixes.at”来形成一个控制回路。木马一旦发现用户启动合法的银行应用，便利用劫持功能将自身伪造的钓鱼页面覆盖在合法的银行应用上面。当用户在伪造的界面上输入银行账号、密码等登录信息后，登陆凭证便会被上传到恶意服务器“anlixes.at”上。

#### **4.1 Firebase云消息传递机制利用**

Firebase云消息传递（Firebase Cloud
Messaging，简称FCM），也称Firebase云信息传递，前身为Google云消息传递（GCM），是一项针对Android、iOS以及网络应用程序的消息与通知的跨平台解决方案，目前可免费使用。开发者只需要在[https://firebase.google.com/](https://link.jianshu.com/?t=https%3A%2F%2Ffirebase.google.com%2F)上，登录自己的Google账户，经过简单的设置操作，便可以将Firebase服务配置到自己的移动APP中。完成移动端的APP设置后，开发者就可以在自己的Firebase网页中选择对应的APP，并在网页上编辑发送自定义的Message。客户端则会以Notifications的方式接收这些Message。

攻击者利用Firebase实时云服务发送恶意命令（分析后的命令和含义见表1），木马负责对这些恶意命令进行接收和解析执行（见图12），完成恶意任务。

![
](https://images.seebug.org/content/images/2019/03/353cff84-abb2-4a84-a678-9fa1569d029f.png-w331s)
表1 控制命令和含义

![img](https://images.seebug.org/content/images/2019/03/07/1551936469000-wps5D88.tmp.jpg-w331s)

图12 木马对恶意命令的接收和解析

从表1我们可以看到，控制命令分为两大部分，第一部分包含前9个命令，分别表示“木马上线、将自身设置为默认短信应用、清空用户数据、将指定号码设置成呼叫转移号码”等。第二部分包括后面的30个命令，当木马接收到Firebase传来的目标银行的APP包名字符串后，木马就打开对应的配置好的http钓鱼伪装界面，来窃取受害用户的银行登录凭证。

##### **4.1.1 木马上线**

木马收到“online”指令后，将自身是否激活管理员权限、是否开启无障碍服务等信息写入配置文件后，发送上线包到远程服务器（见图13）。

![img](https://images.seebug.org/content/images/2019/03/07/1551936470000-wps5D89.tmp.jpg-w331s)

图13 发送上线包

##### **4.1.2 将自身设置为默认短信应用**

“lock”命令会引导用户设置木马自身为系统短信应用，接管短信服务，以获得对短信数据库的操作权限（见图14）。Android
4.4及其以后，只能设置一个默认的SMS短信APP，当短信到达后会首先通知设置的默认APP，并且只有该APP对短信数据库有修改的权限和短信的发送权限。设置成功后，木马就劫持了系统短信，破解了基于短信的SMS短信双因素验证机制。

![img](https://images.seebug.org/content/images/2019/03/07/1551936470000-wps5D8A.tmp.jpg-w331s)

图14 设置自身为默认短信应用

##### **4.1.3 清空用户数据**

当木马接收到“clear”指令，就清空用户数据（见图15）。

![img](https://images.seebug.org/content/images/2019/03/07/1551936470000-wps5D9B.tmp.jpg-w331s)

图15 清空用户数据

##### **4.1.4 设置呼叫转移号码**

“21”命令是设置感染设备的呼叫转移号码为攻击者远程指定的手机号码（见图16）。攻击者首先打开感染设备的拨号程序，然后通过输入“ _21_
手机号码#”对感染设备设置呼叫转移。这样，攻击者就可以成功拦截受害用户的手机来电。

![img](https://images.seebug.org/content/images/2019/03/07/1551936470000-wps5D9C.tmp.jpg-w331s)

图16 设置呼叫转移号码

##### **4.1.5 设置配置文件“addm”为on**

当木马收到“addm”命令后，就会设置配置文件“addm”项为on，用于激活自身管理员权限（见图17）。木马激活自身管理员权限后，可以防止自身被受害用户轻易卸载掉。

![img](https://images.seebug.org/content/images/2019/03/07/1551936470000-wps5D9D.tmp.jpg-w331s)

图17 设置配置文件“addm”项为 on

##### **4.1.6 解密指定文件**

图18中，“lckscr”指令目的是解密“asset”目录下加密文件到自身应用目录下的“/location/”路径下，根据指令“dellckscr”，猜测解密后的文件名为“www.html”。

![img](https://images.seebug.org/content/images/2019/03/07/1551936470000-wps5D9E.tmp.jpg-w331s)

图18 解密指定文件到指定路径

##### **4.1.7 加载指定页面**

“dellckscr”指令用于加载自身应用目录下位置为“/location/www.html”的页面（见图19），不过我们在分析该木马时，并未发现此目录和相应文件，目的未知。

![img](https://images.seebug.org/content/images/2019/03/07/1551936470000-wps5D9F.tmp.jpg-w331s)

图19 加载指定页面

##### **4.1.8 卸载指定应用**

当接收到“src”指令时，木马会打开卸载APP界面，卸载掉攻击者指定的APP（见图20）。

![img](https://images.seebug.org/content/images/2019/03/07/1551936470000-wps5DA0.tmp.jpg-w331s)

图20 卸载指定应用

##### **4.1.9 将目标手机安装的所有应用列表发送给恶意服务器**

当收到的消息为“alpkg”时，木马就遍历系统应用名称，将收集的感染设备安装的应用列表发送给攻击者控制的远程服务器（见图21）。攻击者知道目标设备安装有哪些应用后，尤其是银行应用，就可以针对目标银行来进行攻击。

![img](https://images.seebug.org/content/images/2019/03/07/1551936470000-wps5DA1.tmp.jpg-w331s)

图21 发送应用列表到远程服务器

##### **4.1.10 启动钓鱼页面**

当木马接收到Firebase传来的目标银行的APP包名字符串后，木马就打开对应的配置好的http钓鱼伪装界面，来窃取受害用户的银行登录凭证。从表1中我们可以看到在钓鱼服务器路径“http://anlixes.at/cz
_”和“http://anlixes.at/pl_ ”下，至少配置有26个伪装的钓鱼页面在等待受害用户上钩，其中“http://anlixes.at/cz
_”针对捷克、“http://anlixes.at/pl_ ”针对波兰”。我们分别列出其中的两个页面（图22和图23）。

![img](https://images.seebug.org/content/images/2019/03/07/1551936470000-wps5DB1.tmp.jpg-w331s)

图22 针对捷克用户的伪装钓鱼页面

![img](https://images.seebug.org/content/images/2019/03/07/1551936471000-wps5DB2.tmp.jpg-w331s)

图23 针对波兰用户的伪装钓鱼页面

#### **4.2 监控数据返回**

木马在执行命令后，会将执行结果或者对感染设备的监控数据回传给自己控制的恶意服务器（见图24），从图中的代码我们可以看到木马是将感染机的监控行为数据赋值给p参数后，发送到恶意服务器地址“http://anlixes.at/api/log”。图25是我们抓包的一个结果，从图中可以看到，我们试图卸载该恶意木马时，木马发送给恶意服务器的监控数据。

![img](https://images.seebug.org/content/images/2019/03/07/1551936471000-wps5DB3.tmp.jpg-w331s)

图24 回传指令执行的结果给恶意服务器

![img](https://images.seebug.org/content/images/2019/03/07/1551936471000-wps5DB4.tmp.jpg-w331s)

图25 回传数据抓包的结果

### **5、总结及建议**

“BankThief”从2019年1月开始活跃，主要的攻击目标为波兰和捷克，不排除后期对其他国家或地区实行攻击的可能性。
“BankThief”利用无障碍服务监控感染设备，劫持合法银行应用来对受害用户进行钓鱼攻击，再结合其截获到的银行验证短信，窃取受害用户钱财。“BankThief”还使用了代码混淆和字符串加密，增加了安全研究人员分析的难度。同时，在攻击过程中，攻击者将恶意攻击流量隐藏在Google
Firebase云消息隧道中，以避免攻击流量被网络设备处置，进一步加大了攻击的隐蔽性。

启明星辰ADLab建议广大用户尽量从官网下载手机应用，尤其是涉及到金钱的银行类应用，以免被不法分子利用，威胁到您的财产安全，给您造成不必要的麻烦和损失。

* * *

**启明星辰积极防御实验室（ADLab）**

ADLab成立于1999年，是中国安全行业最早成立的攻防技术研究实验室之一，微软MAPP计划核心成员，“黑雀攻击”概念首推者。截止目前，ADLab已通过CVE累计发布安全漏洞近1000个，通过
CNVD/CNNVD累计发布安全漏洞近500个，持续保持国际网络安全领域一流水准。实验室研究方向涵盖操作系统与应用系统安全研究、移动智能终端安全研究、物联网智能设备安全研究、Web安全研究、工控系统安全研究、云安全研究。研究成果应用于产品核心技术研究、国家重点科技项目攻关、专业安全服务等。

![img](https://images.seebug.org/content/images/2019/03/07/1551936471000-wps5DB5.tmp.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/839/>

