# 看黑客如何利用安全漏洞窥探你的DJI无人机帐户

阅读量 **279851**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-11-09 15:34:35

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Checkpoint，文章来源：checkpoint.com

原文地址：<https://research.checkpoint.com/dji-drone-vulnerability/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0110d0723a7de84411.jpg)

DJI（大疆）一直都是民用无人机和航空成像技术行业的全球[领导者](https://en.wikipedia.org/wiki/DJI_\(company\))。除个人消费者外，它在企业市场也占有很大的份额，这些用户涵盖了关键基础设施、制造业、农业、建筑业、应急管理产业等领域。由于DJI无人机在全球拥有众多用户，因此无论是个人消费者还是企业用户，都可以从广泛的视角和题材中获取数据和图像。

在最近进行的一项调查中，Check
Point的研究人员发现了一个安全漏洞。如果被利用，攻击者可以在用户完全不知情的情况下访问其DJI账户，并提供了对大量敏感数据的访问：

l
如果DJI用户已经与DJI的云服务器同步，那么能够被访问的数据则包括在无人机飞行期间生成的飞行日志、照片和视频。（飞行日志包含无人机在整个飞行过程中的确切位置，以及在飞行过程中拍摄的照片和视频的预览。）

l 如果DJI用户正在使用DJI的FlightHub飞行管理软件，那么能够被访问的数据则包括无人机飞行期间的实时摄像头视图和地图视图。

l 与DJI用户帐户相关的信息，包括用户个人资料信息。

对于此漏洞的利用开始于DJI论坛（DJI Forum），这是由DJI运营的一个在线论坛，用于讨论其产品。登录DJI
Forum，然后点击一个由攻击者植入的恶意链接，用户的登录凭证就可能会被窃取，并允许攻击者访问用户的其他DJI在线资产：

l DJI的Web平台（账户、商店、论坛）

l 从DJI GO或DJI GO 4应用程序同步的云服务器数据

l DJI的FlightHub（集中式无人机操作管理平台）

我们在2018年3月就此漏洞通知了DJI，DJI也负责任地进行了回应。目前，此漏洞已经被修复。DJI将此漏洞分类为“高风险，低概率”，并表示没有证据表明此漏洞曾被Check
Point研究人员以外的任何人利用。

三种潜在攻击流的简化视图

视频地址：<https://youtu.be/dFDA9dYTkzQ>

漏洞利用演示视频

## 技术分析

以下内容解释了我们如何能够通过网站、移动应用程序和FlightHub这三个DJI平台访问到敏感的DJI无人机飞行信息以及敏感的用户数据。

首先，我们将解释漏洞位于何处以及它是如何工作的。

## 漏洞

简单来说，此漏洞存在于DJI的识别过程中。

DJI使用cookie来识别访问其平台的用户，而这个cookie存在被攻击者捕获的风险。通过使用这个cookie，攻击者可以很容易地劫持任何用户的帐户，并完全控制用户的DJI移动应用程序、Web帐户或DJI
FlightHub帐户。

我们首先研究了DJI网站的登录过程，因为我们首先想了解DJI后端是如何识别用户的，以及哪些参数或cookie对登录过程来说是足够重要的。因此，我们查看了所有通过客户端（浏览器）和DJI后端的流量。

我们很快注意到，DJI为其提供的服务使用了一些子域：

l forum.dji.com

l account.dji.com

l store.dji.com

此外，这些域之间的登录使用的是OAuth框架。接下来，我们开始检查这些子域的流量。

我们发现，一个发送给mobile.php URL的请求向我们提供了DJI测试用户的敏感信息，包括username、member_uid、token等数据。

这一个发现很重要，因为它促使我们想要弄清楚DJI后端是如何识别我们的用户，以及它是否使用的是相同的标识符ID。为此，我们查看了在那里使用的cookie，并发现其中一个名为“meta-key”的cookie被用于识别用户。

mobile.php请求

于是，我们接下来的目标就成了通过任何可能的方式获得这个“meta-key”cookie。为此，我们必须找到一个不受http-only属性保护的子域，因为这会阻止JavaScript泄漏cookie。

最终，符合我们需求的子域被确认为forum.dji.com。接下来，我们开始在这平台上查找漏洞。

## 发现漏洞

经过一番查找，我们偶然间发现了以下GET请求：

    
    
    https://forum.dji.com/forum.php?mod=ajax&action=downremoteimg&message=

在这里，我们看到消息参数已经反映在了响应中。但存在两个障碍：

1\. 这里还有一个“addslashes”函数，它为后面的字符添加了一个斜杠“/”；

2\. XSS
payload注入发生在一个名为“updateDownImageList”的未定义函数中，它是从其他一些JavaScript代码中导入的，而我们的上下文中没有这些代码。

我们假设对GET请求的响应类似于以下伪代码：

![](https://p1.ssl.qhimg.com/t012bb5e09f6b8d5c6b.jpg)

于是，从函数转义开始，我们开始使用反斜杠和单引号，如下所示：

    
    
    parent.updateDownImageList(‘ \’ ‘);

然后，“addslahes”也会添加一个反斜杠，它会转义我们的反斜杠，并将它更改为这样的字符串：

    
    
    parent.updateDownImageList(‘ \\ ‘  ‘);

接下来，我们不得不处理剩下的字符，以及未定义的函数“updateDownImageList”。

为了处理剩下的字符，我们添加了一个简单的html注释，比如“<!–”，它创建了以下payload：

    
    
    parent.updateDownImageList(‘ \'<!–  ‘);

现在，我们剩下的就是处理这个未定义函数了。为了搞定这个函数，我们必须自己定义它。

于是，我们的payload最终看起来像是这样的：

    
    
    \’ alert(document.cookie); function updateDownImageList (data) {} <!– 

使用我们的payload接收到的Cookie

然后，攻击者可以创建一个payload，将该meta-key cookie发送到他的网站。任何XSS
Auditor都不会阻止这种XSS，因为它驻留在JavaScript本身，而不是脚本或事件中。

想要触发这种XSS攻击，攻击者所需要做的就是在DJI论坛上编写一个简单的帖子，并将包含payload的链接插入其中。不过，由于DJI限制链接到论坛本身的内容，因此想要以这种方式来发送链接到恶意网站是不可能的。

DJI论坛中潜在攻击者通过帖子链接的恶意站点示例

但由于我们的XSS驻留在论坛本身，因此我们能够绕过这种链接限制。此外，由于有数十万用户在DJI论坛上进行交流，因此攻击者甚至不需要共享恶意链接，因为这会在用户转发消息和链接时自动完成。

在获得meta-key之后，我们继续检查了登录过程，并测试了DJ​​I后端是如何处理每个DJI平台的登录的。首先，我们从DJI网站开始。

## DJI网站

想要获得对DJI网站上任何用户帐户的访问权限，我们所需要的只是他们的“meta-key”，在子域account.dji.com上称被为“mck” 。

我们首先创建了一个DJI帐户并登录上去。通过分析登录过程，我们发现它使用OAuth在子域之间对用户进行身份验证。例如，从accounts.dji.com到forum.dji.com，或者返回dji.com。

因此，每当DJI想要对用户进行身份验证时，它都会发送带有一个“mck”cookie的initData.do请求，并且响应将是带有ticket的回调URL。

通过导航到URL，用户能够在不需要凭证的情况下进行身份验证。

因此，为了劫持一个帐户，我们需要进行以下操作：

l 以攻击者的身份登录dji.com，然后点击DJI.COM，将我们重定向到dji.com。

l 在initData.do请求中，将“mck”cookie值替换为受害者的“mck”（我们通过XSS漏洞获取）。

l 继续登录过程，并访问受害者的帐户。

以下是initData.do请求：

initData.do请求

## DJI App

想要劫持DJI移动应用程序中的帐户，我们必须绕过应用程序本身采取的一些缓解措施。

为此，我们不得不拦截从应用程序到DJI后端的请求，以便研究其登录过程。但是在这里我们遇到了一个SSL
pining机制，它阻止我们拦截应用程序流量并对其进行研究。

因此，我们尝试对应用程序进行反编译，以了解如何绕过SSL
pining机制。不幸的是，由于DJI的移动应用程序得到了SecNeo（一家移动应用程序安全公司）的保护，因此反编译没有取得成功。

根据SecNeo的描述，它提供了以下保护：

l 源代码逆向预防和敏感数据保护。

l 应用程序篡改、再包装和调试预防，以及anti-hooking检测功能。

l 动态代码注入和反编译/反汇编预防。

因此，我们试图通过使用Frida来绕过这些限制。事实上，我们试图搞定dji.go.v4应用程序，但没有取得任何成功。

然后，我们检查了一下为什么我们无法连接到dji.go.v4进程，并使用了“frida-ps –U” 命令来获取在我们的移动设备上运行的所有进程的列表。

在运行此命令后，我们注意到只有一个dji.go.v4进程。然而，在几秒钟之后，我们发现出现了另一个dji.go.v4进程。

通过查看/proc/11194/status，我们可以看到新生成的进程被附加到了第一个进程，并实际调试它。这也就解释了为什么我们无法使用Frida调试进程的原因——它已经被调试过了。

附加到第一个dji.go.v4进程的新进程

我们发现，启动的第一个进程并不是调试程序，而是实际应用程序。调试程序实际上已经附加到了实际应用程序，并开始保护它。这意味着，我们可以利用竞争条件并将我们的hook附加到应用程序进程，并在调试程序进程启动之前将其分离。

为了绕过这个问题，我们将Burp Suit证书复制到手机上并自行生成了DJI应用程序，这将使得应用程序以挂起模式启动（在调试程序初始化之前）。

然后，我们创建了一个使用以下逻辑的Frida脚本：

1\. 打开我们的Burp Suit证书，并生成X509Certificate。

2\. 加载KeyStore，并将证书放入其中。

3\. 创建TrustManagerFactory，并使用我们刚刚创建的包含Burp Suit证书的KeyStore对其进行初始化。

4\. 重载SSLContext，并将TrustManager与我们的TrustManager挂钩。

在挂钩完成后，我们恢复了挂起的应用程序并从中脱离。现在，调试程序就可以在我们完成所有挂钩之后才开始保护了。

通过这种方式，我们绕过了SSL pinning，然后流量开始出现在我们的Burp Suit中。

绕过SSL pinning后在Burp Suit中看到的流量

在绕过SSL pining之后，我们设置了一个代理，允许我们拦截移动应用程序的流量。

通过分析Web应用程序的登录过程，我们发现一旦用户插入其凭证，移动应用程序就会向/apis/apprest/v1/email_login发送一个请求，收到的响应如下：

    
    
    {“code”:0,”message”:”ok”,”data”:{“nick_name”:”XXXXXXXXX”,”cookie_name”:”_meta_key”,”cookie_key“:”NTUxNjM2ZTXXXXXXXXXXXXXXNmI2NjhmYTQ5NGMz“,”active”:false,”email”:”XXXXXXXX@gmail.com”,”token“:”XXXXXXXXX2139“,”validity”:15275XXXXX,”user_id”:”9629807625XXXXXX”,”register_phone”:””,”area_code”:””,”inner_email”:false,”subscription”:false,”vipLevel”:null,”vipInfos”:[]}} 

在这里，我们注意到两个重要参数：

l “cookie_key”–这是我们现在已经熟悉了的DJI论坛的meta-key/ mck。

l “token”–我们可以从本文一开始描述的mobile.php请求中获取此参数。

## 帐户劫持过程

劫持帐户的过程如下：

1\. 首先，我们需要一个meta-key和一个token来替换我们自己的。因此，我们需要将想要破解的meta-key发送到mobile.php，并接收相应的token。

2\. 然后输入自己的凭证，并发送登录请求。

3\. 收到步骤2的响应后，使用受害者的meta-key替换cookie_key值，并使用步骤1中的token替换我们自己的token。

4\. 这样，我们就可以访问受害者的帐户了。

通过利用DJI漏洞，攻击者可以接管受害者的帐户，并访问他们所有同步的飞行记录、无人机拍摄的照片等。

我们还进行了进一步的研究，发现通过解析飞行日志文件，我们可以获得更多的信息。例如，无人机飞行期间拍摄的每一张照片的位置和角度、无人机的标识位置、最后的已知位置等等。

为了能够访问飞行日志文件，攻击者所需要做的就是将飞行记录与他的手机同步。这样，所有手动上传到DJI云服务器上的飞行日志都将会保存到他的手机上。然后，他可以直接浏览到“DJI/dji.go.v4/FlightRecord”文件夹，找出所有的飞行记录文件，将它们上传到网站，并查看各种有关无人机飞行的信息。

## DJI-FlightHub

DJI-FlightHub是一个基于Web的应用程序，用于为企业用户提供完整的摄像头视图和对无人机的管理。实际上，它可以让用户在世界任何地方实时查看他们的无人机活动，包括一个地图视图、一个能够听到声音的实时摄像头视图，并且允许用户查看每台无人机的确切位置，以便协调任务。

DJI-FlightHub包含一个用于访问管理控制面板的桌面应用程序和一个用于操纵无人机的应用程序。幸运的是，我们还找到了一个可访问管理控制的Web门户，你可以通过这个URL找到它：www.dji-flighthub.com。

DJI-FlightHub包含一个admin账户、一个captain账户和一个pilot账户。admin账户可以管理DJI-FlightHub帐户并访问DJI-FlightHub平台、查看飞行数据，并可以创建新的captain或pilot。Captain账户则可以登录DJI-FlightHub平台，并创建新的pilot。Pilot账户则可以通过无人机操纵应用程序来操纵无人机，并将无人机绑定到DJI-FlightHub帐户。

基于此，如果我们能够访问admin或captain帐户，那么我们就能够实时查看无人机的操作。为了劫持admin或captain的DJI帐户，我们需要了解DJI-FlightHub的登录过程。

DJI-FlightHub登录页面

我们发现，当我们单击“login”时，initData.do请求确实是发送了，但在响应中没有接收到ticket（类似于我们通过account.dji.com门户接收到的ticket）。相反，只有在输入凭证时，我们才会在login.do响应中接收到ticket。由于这与我们之前通过account.dji.com门户劫持帐户不同，因此我们不得不考虑另一种在DJI-FlightHub中劫持帐户的方法。

虽然我们知道可以通过initData.do请求来生成ticket，但由于某种原因，在DJI-FlightHub中并非如此。因此，我们查看了请求，以便理解其中的原因。我们注意到，在DJI-FlightHub中，initData.do请求包含一个DJI-FlightHub的appId，这应该就是我们没有在响应中接收到ticket的原因。考虑到这一点，我们认为我们可以将appId替换我们所熟悉的东西来获得ticket。一旦获取到ticket，我们要做的就是检查另一个appid的ticket是否也适用于此。

需要采取的步骤如下：

1\. 发送一个带有“appId = store”的initdata.do请求，其中admin的mck旨在被劫持并在响应中获取ticket。

2\.
登录到FlightHub时，拦截请求，将login.do请求中的mck和响应切换中的mck替换为在inidata.do请求中接收到的ticket。然后，我们就将会被重定向到管理员/受害者的帐户。

此外，管理员将不会收到任何有关攻击者访问其帐户的通知。与此同时，在当前正在进行的任何飞行的实时操作期间，攻击者登录并查看无人机摄像头拍摄画面将完全不受限制，并且可以下载之前所有已经上传到FlightHub平台的飞行记录。

本文翻译自checkpoint.com [原文链接](https://research.checkpoint.com/dji-drone-vulnerability/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **圆圈** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/163910](/post/id/163910)

安全客 - 有思想的安全新媒体

本文转载自: [checkpoint.com](https://research.checkpoint.com/dji-drone-vulnerability/)

如若转载,请注明出处： <https://research.checkpoint.com/dji-drone-vulnerability/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [信息泄露](/tag/信息泄露)
  * [无人机](/tag/无人机)
  * [DJI](/tag/DJI)

 **+1** __1赞

 __收藏

![](https://p2.ssl.qhimg.com/t01a427938cfa1b52e2.png) 圆圈

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

