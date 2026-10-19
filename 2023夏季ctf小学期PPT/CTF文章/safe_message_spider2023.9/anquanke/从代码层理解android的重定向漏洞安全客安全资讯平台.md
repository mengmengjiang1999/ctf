# 从代码层理解android的重定向漏洞

阅读量 **189805**

发布时间 : 2022-08-08 14:30:28

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0114bb5ad8d18c5451.jpg)

## 前言

Android
App中页面跳转主要通过Intent的显式，隐式传递来拉起其他的Activity组件，或是通过在AndroidManifest.xml中配置的android:scheme进行DeepLinks拉起app或跳转页面。相应的，跳转的时候传入参数未校验，就可能存在风险。

## Deeplinks格式

一般Deeplinks格式如下：

    
    
    Scheme://host:port/path?query=xxxxxxx
    

被拉起的的App可以在AndroidManifest.xml中配置，向操作系统提前注册一个URL，开头的Scheme
用于从浏览器或其他App中拉起本App。  
解析Scheme，判断Scheme属于哪个App，唤起App，传递参数给App由操作系统去完成。

## demo

写一个简单的demo。  
在AndroidManifest.xml中注册并配置两个活动。其中Main2Activity中定义了对应的url。

![](https://p2.ssl.qhimg.com/t01692bca3c338bf369.png)

编译后安装。  
可以通过如下adb命令去拉起App。

    
    
    adb shell am start -a "android.intent.action.VIEW" -d "xxapp://webview"
    

或者通过浏览器去拉起。

    
    
    <a href="xxapp://webview">run deme</a>
    

![](https://p0.ssl.qhimg.com/t01e3bb93f025d09d96.png)

可以看到手机中App已经启动。

![](https://p5.ssl.qhimg.com/t01e5fef6a69f991cb5.png)

## WebView中URL任意跳转

还是用上面额例子,这一次我们在Main2Activity中接收外部传入参数，进行加载。  
默认返回是baidu。

![](https://p1.ssl.qhimg.com/t0149102c8743c8a6ed.png)

按上面的adb命令执行，可以看到直接跳到baidu。

![](https://p0.ssl.qhimg.com/t013075f9105710d75b.png)

这里我们并未对传入的参数url进行校验，替换成其他的地址，也是可以加载的。

    
    
    <a href="xxapp://webview?url=https://www.bilibili.com">run deme</a>
    

![](https://p0.ssl.qhimg.com/t01a2f0452e6d926863.png)

## 稍稍深入

在Web中，任意URL跳转漏洞由于功能限制，一般都是低危。但在移动应用中，往往会在WebView通过js去调用java接口使功能更加丰富。  
通过注解[@JavascriptInterface](https://github.com/JavascriptInterface
"@JavascriptInterface")，表示方法可以被js调用。  
这里我写了一个Toast，执行会返回对应的信息。

![](https://p5.ssl.qhimg.com/t0107669b839ca3919b.png)

增加两行代码，开启js支持，绑定对象。

    
    
    webView.getSettings().setJavaScriptEnabled(true);
    webView.addJavascriptInterface(Main2Activity.this, "main");
    

测试html：

    
    
    <html>
    <body>
       <button type="button" onClick="window.main.jsinterface('hhhhhhhhhh123')" >invoke</button>
    </body>
    </html>
    

加载后，点击按钮会出现弹窗提示，表示调用成功。

![](https://p3.ssl.qhimg.com/t01c6db8ab15838df4c.png)

前面讲到过App中页面切换主要是通过Intent的传递，Webview中也是可以对Intent协议进行解析的，这就可能导致通过一条链，导致通过App拉起其他组件或者App，导致其他的问题。

![](https://p3.ssl.qhimg.com/t01cde484fa7856e80d.png)

因为这里我没有去实现Webview支持intent解析，这里就没有演示了。

## 总结

简单学习了一下Android中存在的URL跳转问题及其简单利用，剩下就是尽可能去收集app，逆向收集对应的Deeplinks，分析业务，扩大危害。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **雷石安全实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/277156](/post/id/277156)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Android](/tag/Android)
  * [移动安全](/tag/移动安全)

 **+1** __3赞

 __收藏

![](https://p2.ssl.qhimg.com/t01ebe472d127128939.png) 雷石安全实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

