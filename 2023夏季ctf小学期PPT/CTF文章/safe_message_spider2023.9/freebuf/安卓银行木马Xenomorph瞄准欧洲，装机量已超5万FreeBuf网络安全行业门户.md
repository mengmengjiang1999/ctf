2022 年 2 月，ThreatFabric 的研究人员发现了一个新的安卓银行木马 Xenomorph。它与另一个臭名昭著的银行木马 Alien
存在明显的联系，公用了部分类名和字符串。

根据遥测数据，Xenomorph 将 56 家不同的欧洲银行作为攻击目标。该恶意软件在 Google Play 上的安装量已经超过 5 万。

Xenomorph 尽管与 Alien 存在关联，但二者的功能则截然不同。可能是 Alien 的开发者转而开发了 Xenomorph 或者是能够接触到
Alien 的代码。当然，这些都是推测。

## 分发

近来，越来越多的攻击者开始通过 Google Play 进行恶意软件分发。

攻击者冒充应用程序 `Fast Cleaner`，如下所示：

![image.png-139.9kB](https://image.3001.net/images/20220307/1646630204_6225953c2791bb5c842d8.png!small)应用市场

分析确定该应用程序属于 Gymdrop Dropper。Gymdrop 是 2021 年 11 月发现的 Dropper 家族，此前也发现过用于分发
Alien 银行木马。

研究人员发现一批归属于 `ExobotCompact.D`的恶意软件，在过去的几周内非常活跃。

![image.png-110.7kB](https://image.3001.net/images/20220307/1646630205_6225953d44ea87f5202bc.png!small)仿冒程序

这是首次观察到 ExobotCompact.D 与 Alien.A 通过同一个 Dropper 基础设施进行分发，与此同时也发现了全新的恶意软件家族
Xenomorph。

## 能力

Xenomorph 的功能特性如下所示：

![image.png-131.7kB](https://image.3001.net/images/20220307/1646630205_6225953dad93acc570a77.png!small)功能

### 无障碍服务

这种技术在安卓银行木马中被广泛使用，主要使用覆盖攻击窃取凭据，结合使用短信和通知拦截记录潜在存在的双因子认证。

该恶意软件的攻击基础设施与 C&C 协议都经过精心设计，可以后续扩展与更新。

    
    
    int v0 = arg4.getEventType();switch(v0) {case 1: {﻿UtilGlobal.Log("onAccessibilityEvent", "###    type: TYPE_VIEW_CLICKED");break;}case 2: {UtilGlobal.Log("onAccessibilityEvent", "###    type: TYPE_VIEW_LONG_CLICKED");break;}case 4: {UtilGlobal.Log("onAccessibilityEvent", "###    type: TYPE_VIEW_SELECTED");break;}case 8: {UtilGlobal.Log("onAccessibilityEvent", "###    type: TYPE_VIEW_FOCUSED");break;}. . . case 0x20: {UtilGlobal.Log("onAccessibilityEvent", "###    type: TYPE_WINDOW_STATE_CHANGED");this.windowStateChangedEvent(arg4); // function responsible for injectionsbreak;}case 0x40: {UtilGlobal.Log("onAccessibilityEvent", "###    type: TYPE_NOTIFICATION_STATE_CHANGED");this.notificationStateChanged(arg4); // function responsible for logging notificationsbreak;}. . .} ﻿

该恶意软件的日志记录功能非常强大，可以收集受害者的应用程序行为数据，即使不在潜在攻击应用程序范围内。

程序内实际上还有很多功能尚未实现，Xenomorph 可能仍然处在起步阶段。但 Xenomorph 在一开始就考虑了模块化设计，便于后续扩展更多功能。

与其他银行木马一样，该恶意软件也以来覆盖攻击机制来欺骗受害者泄露个人信息，然后犯罪分子可以利用这些信息进行诈骗。如果恶意软件在启动时获取了
Accessiblity Services 权限，后续就可以自动赋予自己需要的权限，在设备上静默执行。

![image.png-110.6kB](https://image.3001.net/images/20220307/1646630206_6225953e3634b80082bb2.png!small)屏幕截图

### 作案手法

Xenomorph 的攻击手段仍然是经典的 Accessibility Services
权限覆盖攻击。一旦恶意软件执行，后台服务就会在设备上接收可访问事件。打开的应用程序在目标应用程序列表中时，Xenomorph 就会触发覆盖注入目标应用程序的
WebView Activity。

![image.png-92kB](https://image.3001.net/images/20220307/1646630206_6225953eb7096503c1ea4.png!small)覆盖攻击

实现功能的部分代码如下所示：

    
    
    protected void onStart() {super.onStart();this.context = this;OverlayInjectResource v0 = UtilGlobal.getPackageInjection(this, UtilGlobal.SettingsRead(this, "AITG"));this.resource = v0;this.hideStop = true;if(!this.stopActivity && v0 != null) {try {WebView v0_2 = new WebView(this);this.wv = v0_2;v0_2.getSettings().setJavaScriptEnabled(true);this.wv.setScrollBarStyle(0);this.wv.setWebViewClient(new MyWebViewClient(null));this.wv.setWebChromeClient(new MyWebChromeClient(null));this.wv.addJavascriptInterface(new WebAppInterface(this), "Android");String v3 = this.resource.getPageResource(this);this.wv.loadDataWithBaseURL(null, v3, "text/html", "UTF-8", null);this.setContentView(this.wv);}catch(Exception v0_1) {v0_1.printStackTrace();}return;}}

此外，恶意软件能够滥用辅助功能记录设备上的所有活动。截至目前，收集的信息还只是存在本地设备日志上，但后续可能改动回传到攻击者处。

## 攻击目标

恶意软件会首先回传已安装应用程序列表，根据存在的应用程序下载相应的覆盖注入模块。Xenomorph
针对西班牙、葡萄牙、意大利和比利时的一些目标居多，也包括一些通用应用程序，如电子邮件和加密货币钱包等。

![image.png-147.6kB](https://image.3001.net/images/20220307/1646630207_6225953f57d79cf688923.png!small)攻击目标

## C&C 通信

Xenomorph 依赖于开源项目 Retrofit2 实现 C&C 通信。

> Retrofit 是 Square 开发的适用于 Android、Java 和 Kotlin 的 REST
> 客户端。该库提供了一个强大的框架，用于验证和与 API 交互以及使用 OkHttp 发送网络请求。

在获得无障碍服务权限后，Xenomorph 将首先向 C&C 服务器注册并验证：

    
    
    {"api":"%DEVICE_SDK_NUMBER%","apps":["%LIST%","%OF%","%INSTALLED%", "%APPS%"],"imei":"%IMEI%","model":"%MODEL%","numbers":["%LIST%","%OF%","%CONTACTS%"],"tag":"%BOT_TAG%","uid":"%UID%"}﻿

通信使用不断变化的 AES 密钥以及消息的哈希值进行加密，使用硬编码密钥的第一条信息格式如下：

    
    
    {﻿"hash":"%BASE64_ENCODED_SHA256%","id":"%ENCRYPTED_DATA%","iv":"%IV_FOR_AES%","type":"request_verify"}

之后就可以与 C&C 服务器正常通信，恶意软件通常会定期轮询 C&C 命令。响应如下所示：

    
    
    { "type": "get_coms","coms": ["<COMMANDS>"]}

coms 支持的命令如下所示：

![image.png-53.5kB](https://image.3001.net/images/20220307/1646630207_6225953feb9cf05b8c42f.png!small)C&C
命令

服务器有两个接口：

![image.png-13.7kB](https://image.3001.net/images/20220307/1646630208_62259540591e6562baac6.png!small)对外接口

## 与 Alien 相似

Xenomorph 的风格让人想起另一个强大的 Android 银行木马 SOVA，但该恶意软件实际上与另一个已经存在 2 年多的 Android 银行木马
Alien 存在很多相似之处。

Xenomorph 使用的变量命名风格让人联想到 Alien，最有趣的事实是用于存储 Xenomorph 配置的 sharedPreferences
文件的实际名称：`ring0.xml`。

这可能看起来像随机的字符串，但它恰好与 Alien 恶意软件开发者的名称一致。

![image.png-101.4kB](https://image.3001.net/images/20220307/1646630208_62259540a4376eae05896.png!small)相似之处

如果说这是巧合的话，还有许多非常奇特的日志记录字符串和类名，都与 Alien 是相似的。

![image.png-153.8kB](https://image.3001.net/images/20220307/1646630209_622595413d2babf86cdb0.png!small)相似之处

目前来看，Alien 的功能显然比 Xenomorph 要强大的多。但 Xenomorph 毕竟是新兴的恶意软件，后续可能会做出更多更新。

## 结论

Xenomorph 的出现再次表明，攻击者对 Google Play 的攻击越来越频繁。Xenomorph 目前是一个普通的 Android
银行木马，但仍然非常有潜力快速发展。

## IOC

> 64c0f71d9c903f7b22a193a7844ea98a5f9db62b4dcc139f75f6d9698645f369  
> 76e9359cfa98bb326f544577394b007132db63fd19fedde73a76162744b93c6f  
> 2d6f26c16d29d4e68ece44e3ac558cd557d906684ee1a546ea982e7a64ddf0ce  
> 2877b27f1b6c7db466351618dda4f05d6a15e9a26028f3fc064fa144ec3a1850  
> simpleyo5.tk  
> simpleyo5.cf  
> art12sec.ga  
> kart12sec.gq  
> homeandofficedeal.com

## 参考来源

> [ThreatFabric](https://www.threatfabric.com/blogs/xenomorph-a-newly-hatched-> banking-trojan.html)

