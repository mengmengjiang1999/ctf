2021年8月初，一款针对Android银行APP的恶意软件出现在人们的视野中，ThreatFabric
安全研究人员首次发现了这一木马，在其C2服务器的登录面板，研究人员发现，攻击者将其称之为SOVA。![](https://image.3001.net/images/20220906/1662463236_63172d0426c88214f58c6.png!small)

##  ** **SO**** ** **V**** ** **A简介****

在俄语中，SOVA译为猫头鹰，或许是攻击者期望该恶意软件如同猫头鹰一般，成为夜间的优秀捕食者。研究人员确认这是一个全新的Android银行木马，且被发现时正处于开发和测试阶段。

与之同时，研究人员还发现，攻击者已经为其未来可实现的功能建立了清晰的路线图。随后几个月的时间里，SOVA陆续更新了多个版本，真的实现了其更新路线图中提到的诸多功能，包括双因素身份验证
(2FA) 拦截、cookie
窃取和针对新目标、国家（例如多家菲律宾银行）的注入等。![](https://image.3001.net/images/20220906/1662463303_63172d47abab121c817f9.png!small)

SOVA 路线图（2021 年 9 月）

很明显，SOVA表现出想要“大干一场”的强烈意愿，这也是其在初始阶段就进行分发的原因之一。该恶意软件希望将分布式拒绝服务（DDoS）、中间人（MiTM）和RANSOMSORT功能整合到其武器库中——在现有的银行覆盖、通知操作和键盘记录服务之上，足以给目标用户造成难以置信的伤害。它还有一个其他Android
恶意软件中不常见的功能：窃取会话cookie，这意味着犯罪分子无需知道银行凭据即可访问用户的有效登录会话，这也是很多银行APP感到非常头痛的地方。

此外，SOVA 以完全使用 Kotlin 开发而著称，Kotlin 是一种 Android 支持的编码语言，被许多人认为是 Android
开发的未来。如果作者对未来功能的承诺保持不变，那么 SOVA 可能会成为迄今为止在 Kotlin 中完全开发的最完整、最先进的 Android 恶意软件。

在迭代了V2和V3版本后，SOVA在一段时间内陷入了“沉睡”状态，但却在2022年5月再次被研究人员监测到处于活跃状态，并更新至V4版本，针对的目标也从2021年的90个增加至200个，包括银行应用程序和加密货币交易所/钱包。

有意思的是，安全研究人员还发现SOVA增加了一个令人意想不到的新功能——可对手机等移动端进行数据加密和勒索攻击。

##  ** **起底SO**** ** **V**** ** **A****

### 1、语境

如下图所示，该截图包含了SOVA 混淆和打包版本的 VirusTotal 页面。在文件哈希下方突出显示的字符串是文件上传到 VirusTotal
时使用的名称，文件名为“Vormastor test
crypted.apk”。![](https://image.3001.net/images/20220906/1662463338_63172d6a5e4df1f36c271.jpg!small)

根据作者的说法，美国和西班牙的不同银行机构已经有多种叠加可供选择，但它们提供了在买方有需要的情况下创造更多叠加的可能性。该恶意软件未来的版本可能会再次切换到JaVa，以解决其使用混淆软件的兼容性问题。

### 2、命令

以下是SOVA常用的命令列表：![](https://image.3001.net/images/20220906/1662463380_63172d94e29f8dedc6f59.png!small)

### 3、能力

SOVA 的一大特点是不容易被发现，为了实现这一点，SOVA
滥用覆盖机制来诱骗受害者泄露他们的密码和其他重要的私人信息。在覆盖攻击中，用户在他们认为是合法的银行应用程序中输入他们的凭据，于是这些信息就交到了攻击者手中。SOVA
也有可能从设备中窃取会话 cookie，该功能并非第一次出现，但在现代 Android 木马中绝对不常见，且绝对是攻击者获取账户凭证的利器。

与大多数银行木马一样，SOVA 严重依赖 Accessibility
SerVices。首次启动时，该恶意软件会隐藏其应用程序图标，并滥用辅助功能服务来获取正常运行所需的所有权限。在其更新路线图中我们还可以看到，该恶意软件具备躲避双因素身份验证的能力。

具体来说，SOVA恶意软件的主要能力如下：

  * 窃取设备数据
  * 发信息
  * 覆盖和 Cookie 注入
  * 通过推送通知进行覆盖和 Cookie 注入
  * USSD 执行
  * 信用卡覆盖有效性检查
  * SMS的隐藏拦截
  * 通知的隐藏拦截
  * 键盘记录器
  * 卸载应用程序
  * 从受害者卸载中恢复

此外，在其之前发布的路线图中，研究人员还发现了以下的能力：

  * 自动 3 阶段叠加注射
  * 自动 cookie 注入
  * 剪贴板操作
  * 分布式拒绝服务
  * 改善面板健康
  * 勒索软件（卡号覆盖）
  * 中间人（MitM）
  * 普通推送通知
  * 更多叠加
  * VNC
  * 2FA拦截

从上述能力可以看出，SOVA 背后的组织者的思路非常激进，尝试将恶意软件和僵尸网络的功能相结合，并力推SOVA 进入Android
银行恶意软件的不同领域。随着这些功能在后续版本中陆续变成现实，SOVA 也逐渐成为Android领域中具备高危险性的恶意软件。

 **（1）、覆盖攻击**

与大多数 Android 银行木马一样，SOVA 依靠覆盖攻击从受害者那里窃取 PII。如果用户试图访问包含在 SOVA
的活动目标列表中的银行应用程序，恶意软件将收到 Accessibility SerVices 的通知，并将显示一个 WebView
覆盖，伪装成预期的银行应用程序。

此外，攻击者声称未来的 SOVA 版本将具有所谓的 3-stage-oVerlay，如下图所示：![](https://image.3001.net/images/20220906/1662463419_63172dbbedcc3378433f7.jpg!small)

可以预见的是，3段叠加之后SOVA将拥有更强大的功能，甚至将额外的软件下载到目标设备上。

而目标列表包含在名为“packageList.txt”的资产文件中，此列表非常广泛，包含需要信用卡访问权限才能运行的银行应用程序、加密货币钱包和购物应用程序。

 **（2）、cookie窃取**

SOVA 的另一个关键能力是窃取 cookie 的能力。由于Cookie允许用户在浏览器上保持打开的会话而无需输入任何凭据，因此攻击者窃取 cookie
后就可以直接访问受害者的 Web 会话。具体来说，SOVA 将创建一个 WebView 以打开目标应用程序的合法 Web URL，并在受害者成功登录后使用
Android CookieManager 窃取
cookie。![](https://image.3001.net/images/20220906/1662463456_63172de0165ee3d3315d8.jpg!small)

根据已发现的代码片段，研究人员已经知晓攻击者是如何创建覆盖 WebView，具体代码如下：

    
    
    this.setContentView(0x7F070001);  // layout:actiVity_web_View
    
        WebView V1 = (WebView)this.a(0x7F05001D);  // id:web_View
    
        Checks.checkNotNullWithName(V1, "web_View");
    
        WebSettings webSettings = V1.getSettings();
    
        Checks.checkNotNullWithName(webSettings, "web_View.settings");
    
        webSettings.setJaVaScriptEnabled(true);
    
        ((WebView)this.a(0x7F05001D)).setLayerType(2, null);  // id:web_View
    
        String link = this.getIntent().getStringExtra("link");
    
        boolean getCookieFlag = this.getIntent().getBooleanExtra("getCookie", false);
    
        CookieManager cookieManager = CookieManager.getInstance();
    
        CookieSyncManager.createInstance(this.getApplicationContext());
    
        cookieManager.setAcceptThirdPartyCookies(((WebView)this.a(0x7F05001D)), true);  // id:web_View
    
        cookieManager.acceptCookie();
    
        CookieSyncManager.getInstance().startSync();
    
        WebView webView2 = (WebView)this.a(0x7F05001D);  // id:web_View
    
        Checks.checkNotNullWithName(webView2, "web_View");
    
        Checks.checkNotNullWithName(cookieManager, "cookieManager");
    
        webView2.setWebViewClient(new CustomWebViewClient(this, ((boolean)(((int)getCookieFlag))), cookieManager));
    
        if(link != null) {
    
            ((WebView)this.a(0x7F05001D)).loadUrl(link);  // id:web_View
    
        }

需要注意的是，该恶意软件不需要特定权限即可运行此代码，研究人员在测试过程中发现，SOVA可轻松地从 Gmail 或 PayPal 等主要网站窃取会话
cookie，甚至是创建应用程序列表自动监控 cookie 的选项。

 **（3）、DDoS攻击**

DDoS 攻击是SOVA的核心能力之一，也是当前 Android
恶意软件生态系统中不常见的功能，其目标是耗尽设备的资源，使其对目标用户不可用。在最初的版本中这个功能并没有出现，但是背后的组织者已经设置了一个startddos命令，它将在
Kotlin 协程中执行以下代码：

    
    
    do {
    
            retrofitManager V3 = this.mRetrofitManager;
    
                    if(!V3.isActiVe) {
    
                        return l.a;
    
                    }
    
                    Objects.requireNonNull(V3.retrofitClient);
    
                    this.i = V1_1;
    
                    this.j = 1;
    
        }
    
        while(retrofitClient.ddosEndpoint.request(this.link, this) != V0);

在SOVA的路线进化图中，我们可以发现这个功能还在继续开发之中，但尽管如此，SOVA实际上能够使用 RetroFit 为给定的 URL 创建请求。

    
    
    RetroFitBuilder DDOSretroFitBuilder = new RetroFitBuilder();
    
        DDOSretroFitBuilder.setHTTPClient(okHTTPClient);
    
        DDOSretroFitBuilder.setBaseUrl("http://google.com/");
    
        myConVerterFactory DDoSConVerterFactory = myConVerterFactory.c();
    
        DDOSretroFitBuilder.conVerterFactories.add(DDoSConVerterFactory);
    
        retrofitClient.ddosEndpoint = (ddosEndpoint)DDOSretroFitBuilder.buildRetrofit().getProxyClass(ddosEndpoint.class);

如上所示，尽管它将 “google.com” 设置为基本 URL，但通过使用 RetroFit 的 @Url 注释，作者能够动态输入一个全新的 URL。

##  ** **SO**** ** **V**** ** **A**** ** **V**** ** **4****

SOVA V4版本是一次阶段性更新，在这个版本中SOVA的威胁指数更高，且传播能力、隐藏能力也都有了相应的提升。例如在V4版本中，SOVA 背后的组织者
(TA) 尝试将恶意软件隐藏在假冒的 Android 应用程序中，这些应用程序带有流行应用程序的徽标，例如 Chrome、亚马逊、NFT
平台或其他。![](https://image.3001.net/images/20220906/1662463029_63172c3520e3df23878d2.png!small)

SOVA V4 使用的主要图标

SOVA
V4版本还更新了一项新的功能，即获取受感染设备的屏幕截图，以此从受害者那里获取更多信息。例如该恶意软件可以投射/录制屏幕，悄无声息获取用户的关键信息，并对对敏感信息进行记录和存储（如下图所示）。这些功能与可访问性服务相结合，使
TA 能够执行手势，从而实现在受感染设备上进行欺诈活动。这和目前我们常见的Android
银行木马（Oscorp或BRATA）的做法并无二致。![](https://image.3001.net/images/20220906/1662463010_63172c2295b50b5f55bd3.png!small)

SOVA V4 的投射/录制功能

在SOVA
V4版本，攻击者可以轻松管理多个命令。其中包括屏幕点击、滑动、复制/粘贴、显示覆盖屏幕以此隐藏屏幕信息获取的能力等。所有已经获取或存储的敏感信息都会发送回C2服务器，这是一个十分明显的指标，意味着SOVA仍然只是一个过渡版本，其背后的组织者还在不断开发新的功能和特性。

同时，SOVA V4版本还对其核心功能cookie 窃取机制进行了重构和改进。其组织者详细列出了他们感兴趣的 Google 服务（如 Gmail、GPay
、Google 密码管理器等），以及其他应用程序的列表。对于每一个被盗的 cookie，SOVA 还将收集附加信息，以便更精细化实施欺诈活动。

另一个重构的功能是其“保护模块”，该模块最主要的功能是保护恶意软件被卸载。当用户试图从设置中卸载该恶意软件时，SOVA
能够拦截这些操作，自动返回主屏幕，并弹出一个小窗口“此应用程序是安全的”。![](https://image.3001.net/images/20220906/1662462987_63172c0bb1fa77afef871.png!small)

SOVA V3 和 V4 之间的“保护”代码比较

和市场上主流Android 银行木马一样，SOVA 使用 .apk后缀只是为了解压恶意软件，释放真正具备恶意功能的 .dex 文件。在之前的版本中，SOVA
将 .dex 文件存储在应用程序的目录中，而在当前版本中，它使用设备的共享存储目录（“Android/obb/”）进行存储，更直接也更加有效。

此外SOVA V4还增加了一个全新的模块，专门用于Binance交易所和Trust Wallet（Binance
官方加密钱包）。对于这两种应用程序，攻击者旨在获取不同的信息，例如账户余额、受害者在应用程序内执行的不同操作，最后甚至是用于访问加密钱包的助记词（单词集合）等。

##  ** **SO**** ** **V**** ** **A**** ** **V**** ** **5****

就在SOVA V4版本重出江湖之际，Cleafy ASK又在野外发现了多个SOVA变异样本，疑似是SOVA
V5版本。在对其新版本的代码进行分析后，安全研究人员再次发现其代码又有了重大的变化，增加了不少新的功能，此外恶意软件与 C2
服务器之间通信也发生了一些小变化。

例如在 SOVA V5版本中并未观察到
V4版本的VNC模块，安全人员认为这个功能尚未集成到V5版本中。有意思的是，安全人员发现了多个用于调试的日志，综合这些信息 SOVA
V5很有可能还处于开发之中。![](https://image.3001.net/images/20220906/1662462956_63172bec347957a0e96c2.png!small)

SOVA V5 命令列表

尽管还在开发初期，但是SOVA V5有一个核心功能值得引起行业的注意，新增加了一个勒索软件模块，该模块在2021 年 9
月公布的路线图中宣布，没想到如今真的成为了现实。![](https://image.3001.net/images/20220906/1662462924_63172bcc99f21cb675122.png!small)

SOVA V5 的勒索软件模块

虽然目前勒索软件功能似乎并未全部完成，但是不妨碍大家对此感兴趣，这在Android
银行木马领域十分罕见。毕竟在用户的普遍认知中，勒索软件一般是针对PC端。该恶意组织十分敏锐地顺应了近年来的发展趋势，目前移动设备已成为大多数的个人和商业数据的中央存储。一旦勒索软件功能落地，SOVA将一骑绝尘。

##  ** **SOVA正气势汹汹****

根据Cleafy ASK的报告，2022年 Android
银行恶意软件家族呈爆炸式增长；无论是从数量上还是质量上皆是如此。随着进入数字化转型期，以及移动支付使用量急剧增加，攻击者开始转换思路跟随这一大趋势，因此积极新技术、新方法强化移动端的攻击力度也就不足为奇了。

SOVA就是其中代表之一，虽然它仍然处于起步阶段，但是已表现出极大的野心，正气势汹汹而来。目前SOVA的基础功能已经完善，并且可以和其他现代 Android
银行恶意软件一较长短。关键是SOVA没有停下更新迭代的脚步，其背后的组织者显然也对其寄予厚望，那份明确的功能路线图也从侧面印证了这一观点。

如果真的按照路线图所展示的功能，那么在不久的将来，SOVA可通过 VNC、DDoS
功能、勒索软件和高级覆盖攻击来识别设备上的欺诈行为。这些功能将使它成为市场上功能最丰富的 Android 恶意软件，并可能成为Android
银行木马的“新标杆”。

## 参考来源

> [ _https://www.cleafy.com/cleafy-labs/sova-malware-is-back-and-is-evolving-> rapidly_](https://www.cleafy.com/cleafy-labs/sova-malware-is-back-and-is-> evolving-rapidly)
>
> [ _https://www.threatfabric.com/blogs/sova-new-trojan-with-fowl-> intentions.html_](https://www.threatfabric.com/blogs/sova-new-trojan-with-> fowl-intentions.html)

