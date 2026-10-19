# Apktool未正确解析XML导致的XXE漏洞分析

阅读量 **184482**

|评论 **3**

发布时间 : 2017-12-07 15:55:12

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t019f463e0b3d104403.jpg)

## 简介

Apktool未正确解析XML导致 **XXE漏洞** 。以下做一个简单的分析和演示Apktool在进行回编译操作时产生XXE漏洞的过程。

## 漏洞描述

潜在的攻击者可通过构造XML文件，在受影响版本的Apktool对该XML文件解析时触发，造成受害者电脑上任意文件的访问。

## 演示

从Apktool的Github项目下载受影响的apktool_2.2.2.jar（<https://github.com/iBotPeaches/Apktool/releases/download/v2.2.2/apktool_2.2.2.jar>）

使用受影响的Apktool版本v2.2.2进行回编译打包的过程中触发XXE漏洞。

    
    
    java -jar ~/Downloads/apktool_2.2.2.jar b ApkIDE_test -o ApkIDE_test_modified1.apk

![](https://p5.ssl.qhimg.com/t01a7a9acf547f8897f.gif)

而使用刚修复的版本v2.2.3 commit **f19317d87c316ed254aafa0a27eddd024e25ec6c** 进行回编译打包时

则产生以下提示：

从而修复了漏洞。

## 漏洞分析

先来一张修复之后的commit的diff图

<https://github.com/iBotPeaches/Apktool/commit/f19317d87c316ed254aafa0a27eddd024e25ec6c#diff-84f49a5539f89dd92ae7ff22216416d9>

在 [brut.apktool/apktool-lib/src/main/java/brut/androlib/res/xml/ResXmlPatcher.java](https://github.com/iBotPeaches/Apktool/blob/f19317d87c316ed254aafa0a27eddd024e25ec6c/brut.apktool/apktool-lib/src/main/java/brut/androlib/res/xml/ResXmlPatcher.java)

![](https://p0.ssl.qhimg.com/t01805c84040666f035.png)

这里加了一句：

    
    
    docFactory.setFeature(FEATURE_DISABLE_DOCTYPE_DECL, true);
    private static final String FEATURE_DISABLE_DOCTYPE_DECL = "http://apache.org/xml/features/disallow-doctype-decl";

作者的log为 **“Prevent doctypes declarations”** ，即不允许XML中的doctypte声明了。

这里作者还专门增加了一个

[brut.apktool/apktool-lib/src/test/java/brut/androlib/ExternalEntityTest.java](https://github.com/iBotPeaches/Apktool/blob/f19317d87c316ed254aafa0a27eddd024e25ec6c/brut.apktool/apktool-lib/src/test/java/brut/androlib/ExternalEntityTest.java)

配合一个测试用的payload

[brut.apktool/apktool-lib/src/test/resources/brut/apktool/doctype/AndroidManifest.xml](https://github.com/iBotPeaches/Apktool/blob/f19317d87c316ed254aafa0a27eddd024e25ec6c/brut.apktool/apktool-lib/src/test/resources/brut/apktool/doctype/AndroidManifest.xml
"brut.apktool/apktool-lib/src/test/resources/brut/apktool/doctype/AndroidManifest.xml")

作为检测XXE的测试。

## 代码追踪

当我们使用这个命令

    
    
    java -jar ~/Downloads/apktool_2.2.2.jar b ApkIDE_test -o ApkIDE_test_modified1.apk

进行回编译打包时，

在brut.apktool.Main类的main()方法中，对命令行参数进行解析，若使用b选项，则调用cmdBuild()方法，

cmdBuild()方法对命令行的-o（指定输出目录）等进行解析，并最终调用Androlib的build()方法，将命令行中待回编译打包的目录（例子中是`ApkIDE_test`）和最终生成的apk文件的路径，作为参数传入Androlib的build(ExtFile
appDir, File outFile)方法。

在Androlib的build(ExtFile appDir, File outFile)方法中，

先对AndroidManifest.xml进行了备份，然后调用brut.androlib.res.xml.ResXmlPatcher类的

fixingPublicAttrsInProviderAttributes()方法对传入的manifest文件进行解析。

fixingPublicAttrsInProviderAttributes()调用了loadDocument(file)方法

而loadDocument(file)未对传入的file进行检查和限制就执行了parse(file)，直接对AndroidManifest.xml文件进行解析。

**于是恶意攻击者可构造恶意的AndroidManifest.xml使得安全分析人员调用Apktool的b选项进行回编译打包时，触发XXE漏洞。**

而修复版（参考上面的diff）正是在这里增加了一个setFeature()方法，

    
    
    docFactory.setFeature(FEATURE_DISABLE_DOCTYPE_DECL, true);

从而避免了由于对DOCTYPE的解析导致的XXE漏洞。

## 已知受影响版本

Apktool v2.2.1
<https://github.com/iBotPeaches/Apktool/releases/download/v2.2.1/apktool_2.2.1.jar>

Apktool v2.2.2:
<https://github.com/iBotPeaches/Apktool/releases/download/v2.2.2/apktool_2.2.2.jar>

![](https://p2.ssl.qhimg.com/t016fe5d897c59a7fe5.gif)

## 给开发者和安全分析人员的建议

使用 **apktool v2.2.3** 及其以上版本；

检查所有集成了apktool的工具，确保其依赖的apktool在 **v2.2.3** 及其以上版本。

## 参考：

<https://research.checkpoint.com/parsedroid-targeting-android-development-research-community/>

<http://www.theregister.co.uk/2017/12/06/java_and_android_vulns/>

<http://www.wjdiankong.cn/android%E9%80%86%E5%90%91%E4%B9%8B%E6%97%85-%E5%8F%8D%E7%BC%96%E8%AF%91%E5%88%A9%E5%99%A8apktool%E5%92%8Cjadx%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%E4%BB%A5%E5%8F%8A%E9%94%99%E8%AF%AF%E7%BA%A0/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **77caikiki** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/89316](/post/id/89316)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [apktool](/tag/apktool)
  * [XXE](/tag/XXE)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t0142708c469a213013.png) 77caikiki

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

