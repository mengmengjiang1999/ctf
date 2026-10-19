## **背景**

本月初美国著名安全公司kryptowire在其网站上发布了一篇Blog，他们的安全工程师在某智能终端的某个应用上发现了一个高危漏洞。通过该漏洞，终端上安装的恶意应用可以成功提权到system权限，实现启动任意Activity(LaunchAnywhere)，进而执行本地拨打电话到任意号码，恢复出厂设置，安装和卸载应用和安装证书等功能。

安珀实验室在第一时间针对该漏洞进行了深入分析和复现，确认该漏洞模型为Intent重定向，同时快速排查了我司的相关应用，排除了存在相同漏洞。由于该漏洞模型比较典型，不管是在Google
AOSP代码还是各大厂开发的应用中每年都会发现类似的漏洞，这种漏洞往往危害性极大。安珀实验室将此漏洞做深入的分析，并提供防范方法。

文中涉及的漏洞均已修复完成。

##  **原理介绍**

Intent重定向，即应用从不可信Intent 中提取数据，取出其中包含的Intent，或对提取的数据进行封装生成新的Intent，再调用
startActivity、startActivityForResult、startService、sendBroadcast等方法来启动或传递该Intent。

由于Android的Intent类实现了Parcelable，

![](https://image.3001.net/images/20220520/1653035679_6287529f1e8eb880b7fe3.png!small)

因此可以将Intent类的对象作为Intent的 extra数据对象传递到另一个组件中。

攻击者原本是无法直接访问非导出的组件，但是通过Intent重定向，就可以用导出的组件作为跳板来访问非导出的组件，达到launchanywhere或者broadcastanywhere的目的。

Intent重定向违反了Android的安全设计，导致Android的安全访问限制（应用的沙箱机制）失效，造成以下安全问题：

1）普通应用和系统应用中的Intent重定向：

如果是普通应用，可以启动该应用中的任意组件包括非导出组件；

![](https://image.3001.net/images/20220520/1653035722_628752ca7c354b230c9a0.png!small)

图1 普通应用中的Intent重定向原理

如果是system应用中存在这种漏洞，危害更大,可以启动手机中的任意组件(包括导出和非导出组件)；

![](https://image.3001.net/images/20220520/1653035771_628752fbb3b12015c9573.png!small)

图2 系统应用中的Intent重定向原理

2）通过非导出的contentprovider组件中的content://URI来窃取敏感文件。

3）通过IntentScheme URL漏洞模型访问任意组件。

4）通过PendingIntent越权漏洞模型，劫持和修改Intent来达到提权的目的。

##  **详细分析**

接下来详细介绍普通应用和报告中的系统应用中的存在的两个Intent重定向的例子。

###  **• 普通应用中Intent重定向漏洞分析**

某应用中存在一个导出的HomeActivity组件，该组件中存在Intent重定向漏洞，请参考代码中的注释。

![](https://image.3001.net/images/20220520/1653035857_6287535126f844ef98a12.png!small)

在该应用中还存在一个非导出组件WebViewActivity，终端上安装的恶意应用无法直接访问。

![](https://image.3001.net/images/20220520/1653035893_6287537590857b146564d.png!small)

该组件WebViewActivity中有以下代码，使用webview来加载URL。

![](https://image.3001.net/images/20220520/1653035917_6287538d678305eef324d.png!small)

攻击者可以通过导出的HomeActivity访问该应用中的任意未导出的Activity，显然WebViewActivity也在其中。

我们编写一个恶意应用嵌入一个指向未导出组件的Intent并发给HomeActivity，从而让WebViewActivity加载其传入的恶意网站链接，进而达成窃取应用token等目的。

![](https://image.3001.net/images/20220520/1653035977_628753c9c90de63a92d71.png!small)

###

###  **报告中的系统应用中的Intent重定向漏洞分析**

接下来，分析一下报告中的Intent重定向漏洞。该应用的AndroidManifest.xml配置文件中有android:sharedUserId="android.uid.system"，使用的系统签名且安装在priv-app目录中，因此该应用为system应用，具有system权限。该应用的testUsaWpsManager类中，动态注册了一个广播,action为USER_SELECT_WIFI_SERVICE_CALL:

![](https://image.3001.net/images/20220520/1653036005_628753e55a37faf5eaba0.png!small)

因此该receiver即为导出的，其onReceive方法可以接收从外部传入的Intent。然后在没有任何校验的情况下，获取Intent中的extra_call_intent，构造一个新的Intent，然后作为参数传入setCallIntent方法中。

![](https://image.3001.net/images/20220520/1653036040_62875408df209ed8535fc.png!small)

setCallIntent为该Intent添加FLAG_ACTIVITY_NEW_TASK，然后将Intent作为mtestTelecomManagerAdapter的makeCall方法的第二个参数。

![](https://image.3001.net/images/20220520/1653036064_628754204e5979c788dc5.png!small)

makeCall方法最终会调用到startActivityAsUser方法，作为该方法的第一个参数. 而第二个参数为 UserHandle.CURRENT。

![](https://image.3001.net/images/20220520/1653036095_6287543fe829e5c1ed5c2.png!small)

该漏洞中的Intent的流转如下图所示:

![](https://image.3001.net/images/20220520/1653036122_6287545a2f21e3669ebd9.png!small)

图3 Intent流转过程

在终端上安装和运行的零权限的恶意应用，可以实现在本地通过上述Intent重定向漏洞，在用户无感知情况下以system权限实现拉起任意终端上任意Activity，实现如拨打电话到任意号码，恢复出厂设置，安装和卸载应用，安装证书等高危操作，几乎完全控制了用户的终端。

###  **• Intent 重定向漏洞的修复方法**

方法 1：将被拉起的应用组件设为专用组件，即不对外暴露。如果被拉起的应用组件不需要接收来自其他应用的
Intent，则可以将此应用组件设为专用组件，只需在清单中设置android:exported="false" 即可。

方法 2：确保提取的 Intent
来自可信的来源。可以使用getCallingActivity等方法来验证源Activity是否可信,只适用startActivityForResult。

![](https://image.3001.net/images/20220520/1653036177_6287549158d21b79eb4a8.png!small)

方法 3：确保要重定向的Intent 安全。应该验证重定向的Intent，确保该 Intent不会被发送到应用的任何专用组件，以及不会将 URI
权限授予应用的某个专用contentprovider。在重定向 Intent 之前，应用可以先使用
resolveActivity等方法检查将使用哪个组件来处理该 Intent。

![](https://image.3001.net/images/20220520/1653036203_628754ab2a17185550121.png!small)

应用可使用 getFlags 等方法来检查 Intent 是否会授予 URI 权限。例如：

![](https://image.3001.net/images/20220520/1653036230_628754c62a89d542b3d32.png!small)

##

##  **总结**

攻击者结合了系统应用中的动态广播注册漏洞模型和Intent重定向漏洞模型，对终端造成了极大的威胁。Android应用漏洞利用的常态，是攻击者会结合若干漏洞，形成一个完整的攻击链，造成更大的危害。要防范Android终端中应用的漏洞，对安全从业人员和开发者提出了更高的要求，需要熟悉常见的漏洞模型和防范措施。

##  **参考链接**

> [1] Android App安全之Intent重定向详解
>
>
> [https://www.freebuf.com/articles/endpoint/271629.html](../articles/endpoint/271629.html)
>
> [2] 针对 Intent 重定向漏洞的修复方法
>
> [https://support.google.com/faqs/answer/9267555?hl=zh-> Hans﻿](https://support.google.com/faqs/answer/9267555?hl=zh-Hans)

