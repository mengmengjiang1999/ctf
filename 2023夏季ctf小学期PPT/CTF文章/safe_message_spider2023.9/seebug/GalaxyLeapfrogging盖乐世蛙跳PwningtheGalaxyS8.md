**作者：Flanker  
公众号：[Galaxy Leapfrogging 盖乐世蛙跳 Pwning the Galaxy
S8](https://mp.weixin.qq.com/s?__biz=MzI3ODI4NDM2MA==&mid=2247483696&idx=1&sn=6cd0f9c9c5e5c93819b59477b7ed7346&chksm=eb581017dc2f9901fa944a1a9f680878bb116397f3168cb469fb54fbbc0bffa4b4e2f2de64bd&mpshare=1&scene=1&srcid=&sharer_sharetime=1570763241600&sharer_shareid=e441301c3c77aafdcfee7b13b86b2e66&key=e16964c072f0d5a7c29311b658815bdc181932bb2ab59834e63e52bb046d202d7a10871efb12ec8c849e6987f1382bb9b5422476096f1cfcbc925540e74bdbe4e4b9e1440f3f55a1f71c012642df2e4c&ascene=1&uin=MzM5ODEzOTY3MQ%3D%3D&devicetype=Windows+10&version=62060833&lang=zh_CN&pass_ticket=%2F94HOhdJ9Kefm8UMxXsXdKXQNR6sA0WRJLOMpjwsLi0NlWQoWRbeojVK25gSiC29
"成为")**

在最近的一系列文章中，我会介绍这些年以来通过Pwn2Own和官方渠道所报告的在各种Android厂商设备中发现的各种CVE，包括通过fuzz和代码审计发现的各式各样的内存破坏漏洞和逻辑漏洞。第一篇文章将会介绍在2017年末我们用来远程攻破Galaxy
S8并安装应用的利用链，一个V8漏洞来获取最开始的沙箱内代码执行，和五个逻辑漏洞来最终实现沙箱逃逸和提权来安装任意应用，demo视频可以在[这里](https://v.qq.com/x/page/e0568cb5wgx.html)看到。

所有的漏洞均已经报告并以CVE-2018-10496,CVE-2018-10497,CVE-2018-10498,CVE-2018-10499,CVE-2018-10500来标示。本文将主要介绍整个利用链，V8漏洞将在另外的文章中介绍。

# Bug 0: Pwning and Examining the browser’s renderer process

通过第一个V8漏洞（CVE-2018-10496，credit to Gengming Liu and Zhen
Feng）,我们现在获得了在三星浏览器renderer沙箱的代码执行。众所周知这是一个isolated process。Isolated
process是安卓中权限最低的进程，被传统的DAC权限和SELinux context policy所严格限制。 ![sbrowser
processes](https://images.seebug.org/content/images/2019/10/11/1570780297000-1kywjd.png-w331s)
那么在S8上相应的policy会不会有问题？通过反编译S8的SELinux
policy，我们很遗憾地发现三星在这块还是做了不错的工作，相比于原版Android没有增加任何的额外allow
policy。也就是说isolated进程仍然只能访问很少量的service和IPC，更别提启动activity之类的了。 ![SELinux access
vectors](https://images.seebug.org/content/images/2019/10/11/1570780343000-2mbedp.png-w331s)
对于想从头了解三星浏览器（或者说Chrome浏览器）沙箱架构的读者朋友，可以参考我之前在CanSecWest上的[PPT](https://cansecwest.com/slides/2017/CSW2017_QidanHe-GengmingLiu_Pwning_Nexus_of_Every_Pixel.pdf)，相应内容在此就不再赘述。鉴于看起来三星并没有对isolated
process增加额外的供给面，我们还是需要用old-fashion的办法 –
审计浏览器IPC。三星浏览器虽然在界面上和Chrome看起来大相径庭，但本质上还是Chromium内核，对应的沙箱架构也和Chrome一致。
前事不忘后事之师。说到IPC漏洞，我们就会想到当年东京文体两开花中日合拍的…

# Bug 1: 东京遗珠： CVE-2016-5197修复不完全可被绕过

老读者们应该都还记得之前东京我们用来攻破Pixel的CVE-2016-5197，具体内容可以在[这里](https://cansecwest.com/slides/2017/CSW2017_QidanHe-GengmingLiu_Pwning_Nexus_of_Every_Pixel.pdf)看到。回顾当年Google给出的[补丁](https://chromium.googlesource.com/chromium/src.git/+/abd993bfcdc18d41e5ea0f34312543bd6dae081e^!/#F0)

    
    
    public class ContentViewClient {
     public void onStartContentIntent(Context context, String intentUrl, boolean isMainFrame) {
     //...
    @@ -144,6 +148,14 @@
             // Perform generic parsing of the URI to turn it into an Intent.
             try {
                 intent = Intent.parseUri(intentUrl, Intent.URI_INTENT_SCHEME);
    +
    +            String scheme = intent.getScheme();
    +            if (!scheme.equals(GEO_SCHEME) && !scheme.equals(TEL_SCHEME)
    +                    && !scheme.equals(MAILTO_SCHEME)) {
    +                Log.w(TAG, "Invalid scheme for URI %s", intentUrl);
    +                return;
    +            }
    +
    //...
            try {
                context.startActivity(intent);
            } catch (ActivityNotFoundException ex) {
                Log.w(TAG, "No application can handle %s", intentUrl);
            }
        }

Google的修复是对该IPC接受的intent
string做了检查，只有特定scheme的intent才能通过，意图是只允许geo://，tel://和mailto://等隐式intent，从而禁止再传递显式string来启动activity。
然而这个修复漏掉了关键的部分：intent解析并不是只依赖于scheme部分，component参数的优先级远高于scheme解析。我们只要在之前的攻击payload头部添加”scheme=geo”，同时依然保持component，即可既绕过这个check，又继续在renderer沙箱中通过这个IPC启动任意activity，继续利用这个漏洞。如之前所述，三星浏览器是chromium内核，那么也包含相同的漏洞代码。
![Jumping from renderer
sandbox](https://images.seebug.org/content/images/2019/10/11/1570780352000-3jtcag.png-w331s)
当然受到parseUri参数的限制，我们构造出的intent只能含有string和其他基本类型参数，不能包含一些fancy的parcelable，这对后续攻击面选择提出了要求。这个activity需要能满足如下条件

  * 导出并会在webview中加载或执行攻击者通过intent指定的url或javascript
  * 接受基本参数类型，对parcelable没有强制检查

只要我们能在App的webview中执行任意代码，我们就获得了这个应用的权限。 [注1]

这个漏洞在报告后，Google分配了[issue
804969](https://bugs.chromium.org/p/chromium/issues/detail?id=804969)。幸运的是，Chrome在这个漏洞被报告前的一次无关的代码refactor中，把这个IPC整个全部去掉了…
故Chrome官方认为此问题已经不存在了，但是所有下游的Chromium内核浏览器都仍然受影响。一个奇葩的操作是三星并没有为这个漏洞单独分配CVE，而是在各个bug单独的CVE之外，又分配了CVE-2018-9140/SVE-2017-10747给整个利用链。

# Bug 2: The Email loves EML with a … XSS

在检索所有权限较高的应用过程中，我们发现了Samsung Email和它所导出的一个有趣的Activity。 ![Email
activity](https://images.seebug.org/content/images/2019/10/11/1570780375000-4yqmbx.png-w331s)
导出的`com.samsung.android.email.ui.messageview.MessageFileView`会在intent参数中接收并解析EML文件。什么是EML文件？EML文件是一个电子邮件导出格式，Samsung
Email对EML文件提供了非常完善的富文本支持 –
完善到直接用Webview来加载和渲染。这当然立即勾起了一个安全研究员的兴趣：这是否意味着接下来有XSS、脚本注入，以及对于我们的场景，代码执行的可能性。
Project
Zero的Natalie在CVE-2015-7893中报告了一个类似的漏洞，在此之后三星增加了一些检查。然而就像所有的漏洞修复第一次经常可能修不完一样，这个检查做的非常粗糙，粗糙到是对`<script>`关键字的匹配。我们只需通过`img
src document.onload=blablaba`并动态引入script即可绕过，从而导致XSS。 这个漏洞被分配了CVE-2018-10497。

# Bug 3: … 以及 file:/// 跨域

虽然在Bug 2中我们证实了这个XSS确实存在，但通过这个XSS引入js
exploit并获得代码执行权限（shell）还有一些问题。典型的是EML文件本身如果太大，将会影响WebView的堆布局，进而导致堆风水的成功率降低。但是Email应用并没有让我们失望，它开启了setAllowFileAccessFromFileUrls，这意味着我们可以将js
exploit拆分到单独的文件中，通过script src的方式引用，进而尽可能缩小EML文件的体积来提高V8漏洞的成功率。
一个小tip：Bug2和Bug3组合在一起，已经可以任意读取Email的私有文件了。 这个漏洞被分配了CVE-2018-10498
所以我们现在构造如下所示的样例攻击EML文件：

    
    
    MIME-Version: 1.0
    Received: by 10.220.191.194 with HTTP; Wed, 11 May 2011 12:27:12 -0700 (PDT)
    Date: Wed, 11 May 2011 13:27:12 -0600
    Delivered-To: jncjkq@gmail.com
    Message-ID: <BANLkTi=JCQO1h3ET-pT_PLEHejhSSYxTZw@mail.jncjkq.com>
    Subject: Test
    From: Bill Jncjkq <jncjkq@gmail.com>
    To: bookmarks@jncjkq.net
    Content-Type: multipart/mixed; boundary=bcaec54eecc63acce904a3050f79
    --bcaec54eecc63acce604a3050f77
    Content-Type: text/html; charset=ISO-8859-1
    <body onload=console.log("wtf");document.body.appendChild(document.createElement('script')).src='file:///sdcard/Download/exp.js'>
    <br clear="all">--    Bill Jncjkqfuck
    
    </body>
    --bcaec54eecc63acce604a3050f77—

通过在EML中捆绑V8
exploit并通过intent使Email打开，我们可以成功在Email进程中执行代码获得其权限，从而正式跳出renderer进程的isolate沙箱。Email应用本身具备读取相片、通讯录的权限故到这里我们已经满足了Pwn2Own的初步要求。截至目前，我们的攻击链步骤如下：

  1. 通过http header头attachment的方式强迫浏览器将含有攻击代码的EML文件和js文件下载。在安卓上，下载路径固定于例如`/sdcard/Download/test.eml`和`/sdcard/Download/test.js`中。
  2. 在获得renderer进程权限后，构造并调用brokerer IPCstartContentIntent，传入参数为`intent:#Intent;scheme=geo;package=com.samsung.android.email.provider;component=com.samsung.android.email.provider/com.samsung.android.email.ui.messageview.MessageFileView;type=application/eml;S.AbsolutePath=/sdcard/Download/test.eml;end`，从而唤起并exploit Email应用的webview
  3. 成功获取Email应用进程权限

# Bug 4: Go beyond the Galaxy (Apps) … but blocked?

以上结果虽然能满足Pwn2Own的初步要求，但是我们的终极目标是要能够任意安装应用，而Email显然没有这个权限。我们的下一步就是需要找到一个具有`INSTALL_PACKAGES`权限的进程或应用来作为目标。显而易见，Galaxy
Apps（三星应用商店）是一个目标。这个应用中有一个非常有潜力的Activity`com.samsung.android.sdk.ppmt.PpmtPopupActivity`，非常直接地接收intent传入的url参数，没有对来源做任何校验就在webview中打开。
不过天上不会掉馅饼，显然这个Activity被保护了 – 不导出。 … 但只是对外保护，不是对内保护

# Bug 5: Push SDK pushes vulnerability

在审计三星平台其他App的过程中，我们发现同样的component
`com.sec.android.app.samsungapps/com.samsung.android.sdk.ppmt.PpmtReceiver`和`com.samsung.android.themestore/com.samsung.android.sdk.ppmt.PpmtReceiver`出现在了多个应用，包括Galaxy
Apps中。通过分析其功能我们认为这应该是一个私有push
SDK，用于一些广告、活动通知相关的推送。这些receiver都是导出的，在PpmtReceiver的相关代码中，我们发现了如下有意思的代码片段：

    
    
    //The Ppmt receiver seems responsible for push message, and under certain intent configuration, it routes to path 
        private void a(Context arg5, Intent arg6, String arg7) {
            if("card_click".equals(arg7)) {
                CardActionLauncher.onCardClick(arg5, arg6);
                return;
            }
    //in onCardClick, it reaches CardActionLauncher, 
        private static boolean a(Context arg2, String arg3, CardAction arg4) {
            boolean v0;
            if("app".equals(arg4.mType)) {
                v0 = CardActionLauncher.b(arg2, arg3, arg4);
            }
    //If the CardAction.mType is "intent", we finally reaches the following snippet:
    private static boolean d(Context arg5, String arg6, CardAction arg7) {
            boolean v0 = false;
            if(TextUtils.isEmpty(arg7.mPackageName)) {
                Slog.w(CardActionLauncher.a, "[" + arg6 + "] fail to launch intent. pkg null");
                return v0;
            }
            Intent v1 = new Intent();
            v1.setPackage(arg7.mPackageName);
            if(!TextUtils.isEmpty(arg7.mData)) {
                v1.setData(Uri.parse(arg7.mData));
                v1.setAction("android.intent.action.VIEW");
            }
            if(!TextUtils.isEmpty(arg7.mAction)) {
                v1.setAction(arg7.mAction);
            }
            if(!TextUtils.isEmpty(arg7.mClassName)) {
                v1.setComponent(new ComponentName(arg7.mPackageName, arg7.mClassName));
            }
            if(arg7.mExtra != null && !arg7.mExtra.isEmpty()) {
                v1.putExtras(arg7.mExtra);
            }
            CardActionLauncher.a(v1, arg6);
            try {
                switch(arg7.mComponent) {
                    case 1: {
                        int v2 = 268435456;
            try {
                v1.setFlags(v2);
                arg5.startActivity(v1);
                goto label_78;
        //….

通过这段代码，我们可以通过发送broadcast以任意参数指定任意Activity启动，当然包括Galaxy
Apps内部未导出的Activity。我们通过这个漏洞来间接启动之前提到的PpmtPopupActivity，进而加载含有JS
exploit的攻击页面，从而获得Galaxy
Apps的权限（shell），利用它的`INSTALL_PACKAGES`权限来安装任意应用。一个有意思的地方是，这个Activity本身并没有直接的UI指向它，所以猜测这能是一个废弃的SDK，但忘记被去掉了。
这个漏洞被分配了CVE-2018-10499.

# Chaining it altogether

![Whole escape
chain](https://images.seebug.org/content/images/2019/10/11/1570780379000-5zyiyy.png-w331s)
这就是我们攻破Galaxy
S8的完整利用链。所有的漏洞均已在当时及时报告给了厂商并得到了修复。鉴于这个漏洞利用链每一步都是在寻找更高权限的进程或应用来作为跳板进行攻击的特点，我们将它命名为”Galaxy
Leapfrogging” (盖乐世蛙跳）。完成攻破的Galaxy
S8为当时的最新版本samsung/dreamqltezc/dreamqltechn:7.0/NRD90M/G9500ZCU1AQF7:user/release-keys.

在此感谢Samsung Mobile Security在修复漏洞中作出的工作，和腾讯科恩实验室以及科恩实验室的前同事们。 接下来还会有其他各大Android
Vendor的各式CVE writeup，请保持关注。Weibo:
[flanker_017](https://www.weibo.com/u/2214340953) .

# 注1： isolated webview的当前状态

从Android O开始，所有的应用在缺省状态下均在isolated
context运行webview，也就意味着攻破了webview不再意味着直接获取应用的权限，从而极大地阻止了我们的蛙跳战术。但部分用户量非常大的App（在此不直接点名），使用了自己编译的webview或第三方通用浏览服务提供的webview，例如X5/tbs和ucwebcore，而截至目前这些webview即使在最新版本Android上面仍然没有启用isolated限制，也意味着他们仍然是蛙跳战术巨大而明显的目标。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1050/>

