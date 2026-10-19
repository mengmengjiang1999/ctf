# 【技术分享】Edge浏览器上的SOP绕过/UXSS（含演示视频）

阅读量 **119656**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-04-28 14:17:13

 **x**

##### 译文声明

本文是翻译文章，文章来源：brokenbrowser.com

原文地址：<https://www.brokenbrowser.com/sop-bypass-uxss-tweeting-like-charles-darwin/>

译文仅供参考，具体内容表达以及含义原文为准。

****

****

翻译：[ **興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**一、前言**

在这篇文章中，我们将探索微软Edge浏览器上的另一种SOP（Same Origin
Policy，同源策略）绕过方法。无域化（domainless）页面能够自由访问其他域（domain）的页面，基于这个事实，我们通过滥用data/meta标签，完成了Edge浏览器的SOP绕过任务。

如果你时间宝贵，你可以先看一下这个59秒的漏洞利用[视频](http://v.youku.com/v_show/id_XMjcyNjYyOTM4OA==.html)，这个视频中我们以达尔文的身份发布了推文。你也可以看一下这个2分钟的[视频](http://v.youku.com/v_show/id_XMjcyNjY0MjY3Mg==.html)，我们在这个视频中以查尔斯的身份手动发布推文，同时抓取了用户的密码（感谢微软Edge浏览器的默认密码管理器）。如果你想看更多的技术细节，可以继续往下看。

如果你是第一次看这类文章，我建议你可以先看一下这两篇SOP绕过文章：[【技术分享】Edge浏览器上的SOP绕过/UXSS（含演示视频）](http://bobao.360.cn/learning/detail/3789.html)以及[【技术分享】IE上的UXSS/SOP绕过-再次冒险在无域的世界](http://bobao.360.cn/learning/detail/3659.html)。本文的核心思想与这两篇一样，但利用技术更加新颖。

让我们快速回顾下一个重要事实：about:blank页面总是与他的引用页面处于同一个域（domain），这也意味着来自于twitter的iframe中的“about:blank”页面无法访问google的空白页。即便这两者的地址能够匹配成功（都为about:blank），但他们的“document.domain”是不同的。

在早些时候，我们可以在没有domain的前提下创建about:blank页面，或者创建domainless的about:blank页面。这些页面可以访问每个about:blank页面，而无视这些页面的domain值。举个例子，我们的主页面中有个domainless的空白页，渲染了两个iframe，其中一个指向twitter，另一个指向google。这些iframe内部都包含空白的子iframe，它们的domain分别为twitter以及google。在这种场景下，顶层窗口能够访问具有domain的空白页，也就是说，能够访问google和twitter的DOM（Document
Object Model，文档对象模型）。如下图所示：

在早些时候，上面描述的这个漏洞场景可以正常工作，直到微软在三个月之前发布了补丁，修复了这个漏洞。微软使用了一个非常巧妙的方法来修复这个漏洞：domainless的空白页再也不是真正的domainless了，这些页面在漏洞修复后都使用了随机的GUID作为他们的domain，比如“{53394a4f-8c04-46ab-94af-3ab86ffcfd4c}”。还有另外一点也十分有趣，那就是这些页面的domain值看上去像是空白的（或者是空的），但实际情况并非如此。换句话说，Edge浏览器会隐藏GUID的值，并返回空的domain值，但在浏览器内部，domain的值仍为GUID。

让我们开始实验。打开Edge浏览器，同时打开开发者工具（DevTools，F12开启），在地址栏输入“about:blank”，在之前，我们这样做会创建一个domainless的空白页，现在看起来貌似一切如故，但这其实是Edge的障眼法。让我们好好欣赏一下Edge的表演，我们有足够的时间来揭开它的伪装。

如我们所看到的一般，DevTools认为我们的domain值为空，但事实并非如此。

  

**二、打破障眼法**

现在DevTools已经被欺骗，我们怎么能看透事实的真相呢？实际上并不难，我们可以尝试使用相对路径，随意加载一个页面，或者改变一下这个窗口的位置，或者使用一个“document.write”语句，就可以打破这种障眼法。我们试一下“location.href=1”这个语句，看一下会发生什么。

  

**三、之前的漏洞已被修复**

我们之前使用的创建domainless空白页的[漏洞](https://www.brokenbrowser.com/uxss-edge-domainless-world/)已经被修复。在之前的这个漏洞中，我们借助Flash/GetURL机制在主窗口（顶层窗口）设置了一个“data:uri”地址。但漏洞修复后，情况变得更加糟糕，我们再也不能自动运行Flash了！在Windows
Creators更新之后，Edge浏览器在运行Flash之前会征求用户的许可。

这种情况下，以前的[PoC](http://unsafe.cracking.com.ar/demos/edge-domainless-uxss/bing/index.html)就显得毫无作用，不过还是应该感谢Edge团队在安全方面的工作。

  

**四、再次找到一个新的domainless空白页**

我们之前的“data:uri”技巧不能再起作用了，那么我们怎么克服这个困难呢？首先，我放弃了钻研顶层窗口的方式，再次与iframe搏斗，因为就我们以前的经验来看，Edge浏览器并不喜欢主窗口中存在“data:uri”形式的地址。

    
    
    top.location.href = "data:text/html,SOMETHING"; // Fails badly, error page

我们发现iframe的地址还是可以成功设为“data:uri”的地址形式。然而，这并不是一个bug，因为iframe的domain与顶层窗口的domain是相互隔离的。

正如我们之前在“[读者模式的SOP绕过](https://www.brokenbrowser.com/sop-bypass-abusing-read-protocol/)”这篇文章中看到的一样，Edge浏览器对“data:uri”的隔离方式可以被绕过（只需要在自身使用document.write语句，我们就可以访问上层窗口），但我们现在不想使用这种方式。现在访问顶层窗口没有任何意义，我们需要的是找到获取domainless空白页的方法。为此，我们需要使用三重组合，也就是data-meta-data组合。这样就可以迫使Edge浏览器把从我们这里夺取的果实再次还回来。

具体说来，我们会将某个iframe的地址设置为“data:uri”形式，这个iframe会触发一个meta refresh，重定向到另一个data:uri。

**小贴士：如何创建一个domainless空白页：**

**1\. 设置iframe的地址为“data:uri”形式**

**2\. 这个“data:uri”会渲染一个meta refresh标签**

**3\. “meta refresh”会重定向到另一个“data:uri”地址**

我们先来构造一个URL，这个URL可以将常规的（即有domain）的iframe转换为domainless的iframe。脑海里牢记“data-meta-data”这个组合，你就能理解我们为什么要这么构造。

我知道上面这种构造方式没那么完美（当然没有像E=mc2那么完美），但是我们使用这种技巧可以窃取爱因斯坦的凭证、邮件、paypal账户，甚至以他的名义发一些推文。我们先来测试一下目前的进展是否顺利。我们的测试对象是bing.com，因为它包含一个内部空白iframe，同时没有使用[XFO](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options)。

  

**五、使用bing.com来热身**

我们将会创建带有两个iframe的web页面，其中一个为bing.com的iframe，另一个是domainless的iframe。我们最终会在domainless的iframe中执行bing内部空白iframe中的代码。Bing的图片恰好满足我们的需求。我会打开Chrome浏览器，向大家描述我想表达的具体含义。

现在进展不错，我们会将该页面frame化，同时借助我们前面提到的domainless的“data-meta-data“方式，将代码注入到空白的iframe中。但有一点我没有提到，你是否还记得，在我们最开始的domainless
SOP文章中，我们在处理nature.com时碰到了一个命名问题。如果你没有印象，我们可以来快速回顾一下。

此时此刻，我们的domainless
iframe已经可以访问bing的空白页，但选择具体的访问机制是非常重要的。我们不能直接访问DOM，必须使用window.open方法才可以。换句话说，如果bing是主页面的第一个iframe，我们无法使用以下这种方式访问它的内部iframe：

    
    
    alert(top[0][0].document.cookie); // ACCESS DENIED

事实上，我们也不能使用以下这种方式：

    
    
    top[0][0].location.href = "javascript:alert(document.cookie)"; // ACCESS DENIED

那么我们该怎么做呢？非常简单，我们可以使用window.open方法，利用iframe的名字打开一个javascript
url就可以了。比如，如果bing的内部iframe名字是“INNER_IFRAME”，那么以下这行代码就能成功运行：

    
    
    window.open("javascript:alert(document.cookie)", "INNER_IFRAME"); // SOP BYPASSED!

但非常讨厌的是，bing的内部iframe并没有名字！不要灰心，我们可以请求Bing团队为这个iframe设置一个名字（开玩笑的），或者我们需要继续往前努力。

  

**六、设置iframe的名字**

如果我们不具备某个iframe的所有权，我们就不能设置它的名字，除非它与我们处于同一个domain。接下来我们要渲染一个包含空白页面的bing
iframe。外部iframe处于不同的domain中，但标签（tag）本身（元素和对象）处于我们的domain中，因此我们可以随心所欲任意设置它的名称。

    
    
    <iframe name="ANY_NAME" src="http://bing.com">
       <iframe src="about:blank"></iframe>
    </iframe>

然而内部的iframe属于bing，即使它是空白iframe，它的domain仍然是bing.com。改变它名字的唯一方法，是先将它的地址设置为我们能够访问的某个地址，之后我们才能修改它的名字。现在，如果我们想要修改about:blank的地址，这就像在搬起石头砸自己的脚，因为我们首先得成为bing.com，然后才能访问domainless空白页。

请记住：我们的目标是从某个domainless空白页访问某个具有domain的页面。如果我们设置该页面的domain，使之与我们的domain相匹配，那么即使能够访问它也是毫无意义的。因此，在这里我们需要这么做：我们要设置页面的地址，改变iframe的名字然后还原页面地址。这样做我们就能保持原始的domain值，听起来是不是比较复杂？

**小贴士：如何设置x-domain-iframe的名字：**

**1\.
将iframe的地址设为about:blank，这样我们就可以将它的domain设置为我们能够控制的某个domain，如cracking.com.ar**

**2\. 修改iframe的名字**

**3\. 再次将iframe的地址设为about:blank，但这次我们使用的是meta
refresh机制，使它的domain与它的创建者一致（本例中即bing.com）**

就是这么简单。现在内部的iframe已经拥有一个名字，并且它的domain已经恢复为bing.com！代码如下所示：

    
    
    // Sets the location of Bing's inner iframe to about:blank
    // But now it is in our domain so we can set a name to it.
    window[0][0].location = "about:blank";
    // Set the inner iframe name to "CHARLES" so we can later inject code
    // using a window.open("javascript:[...]","CHARLES");
    window[0][0].name = "CHARLES";
    // Restore Bing's domain to the about:blank that we've just renamed.
    window[0][0].document.write('<meta http-equiv="refresh" content="0;url=about:blank">');
    window[0][0].document.close();

现在有个好消息，那就是我们没必要要求站点包含“about:blank”的iframe，因为我们总是能够使用上面那种方法完成任务。换句话说，不管bing的内部iframe是否是about:blank都不重要，上面那种方法总是能够奏效。现在好好看一下我们的表演。

成功之门已经开启，我们可以在我们的“data-meta-data” iframe中运行window.open方法，如下所示：

    
    
    window.open("javascript:alert(document.cookie)", "CHARLES"); // Fireeeeeeeeeee!!!

你可以使用Edge浏览器[在线测试](http://unsafe.cracking.com.ar/demos/edgedatametadata/bing.html)这个漏洞PoC。

关于这个PoC，有一点需要注意。我们在上面的例子中，使用的是一个http（不安全）连接，因为在https（安全）连接中，使用meta
refresh跳转是被禁止的，因此我们无法重定向到最终的data:uri地址。Edge浏览器错误地认为这种重定向是不安全的。然而，我们在第一步中可以不使用data:uri，换而使用document.write方法，就可以成功绕过这种限制。因此，上面的“data-meta-data”三元组需要换成“document.write(meta-data)”。

我们在上面的PoC中并没有使用这种方法，因为访问上面这个交互式演示网站时，Edge浏览器有三分之一的概率会崩溃。因此，我选择了一个向导式的稳定PoC，而不是上面这个自动化http(s)
PoC。但如下文所示，这种处理无关紧要，因为我们的不安全（http）的domainless空白页仍然可以访问安全的页面。接下来我们来看看一个实际的案例。

  

**七、真实案例：窃取查尔斯的cookie**

现在是时候看看真实案例了。跟我一起乘坐时光机器，回到过去，将计算机和互联网一起带到天才辈出的那个年代。当时查尔斯·达尔文（Charles
Darwin）正在思考物种的进化问题，阿尔弗雷德·华莱士（Alfred
Wallace）也有类似的想法。查尔斯对黑客有防范意识，因此他使用电脑的方式有点偏执：他从来没有使用已经打开gmail、twitter以及个人文档的浏览器窗口来访问其他链接。

比如，他正在通过任务栏启动一个浏览器的隐私窗口，如下所示：

他心情不错，在另一个浏览器标签中打开了他的Twitter页面，调戏阿尔弗雷德·华莱士，告诉华莱士，自己将要发布一条推文，公布自己的发现。

华莱士的回复几个小时后才姗姗来迟，回复中包含某个链接，用来支持他自己的理论。还记得吗，查尔斯不信任任何人，因此他复制这个链接，将其粘贴到一个新窗口中，这个窗口远离他的私人数据（比如gmail、twitter）。

这种情况下会有什么问题呢？问题多多！就如同世界上大多数网站一样，twitter使用了好几个iframe。事实上，twitter拥有两个具备名字的about:blank
iframe，因此搞定它会比搞定Bing更加容易！在回到我们的故事之前，我们先使用DevTools，枚举一下twitter的iframe以找到合适的利用对象。我打开了一个不同的窗口，与查尔斯的会话没有任何关系。

非常棒！dm-post-iframe这个iframe看起来不错，万事俱备，我们马上可以搞定查尔斯的账户。

现在，查尔斯打开了一个新的隐私窗口，加载了华莱士发送给他的URL。他所不知道的是，即使浏览器处于隐私浏览状态下，它们之间也会相互通信。因此，如果我们在自己的domainless
iframe中执行如下代码，情况会怎么样呢？

    
    
    window.open("javascript:alert(document.cookie)", "dm-post-iframe");

正如你所看到的，我们现在已经拥有了查尔斯·达尔文的cookie。

你可以使用Edge浏览器[在线测试](http://unsafe.cracking.com.ar/demos/edgedatametadata/cookiesfromcharlie.html)这个漏洞PoC（注意：这个PoC真的会弹出你的Twitter
cookie信息）。

请大家记住，我们并不是真的需要使用隐私模式访问这个网站。我们之所以举上面这个例子，是为了说明在某些特殊场景下我们的漏洞也是可以奏效，但通常情况下我们面临的情况并没有那么复杂，因为人们并没有像查尔斯那样，对链接那么敏感。此外，考虑到攻击者会在流行站点上使用[恶意广告](https://blog.malwarebytes.com/101/2015/02/what-is-malvertising/)等攻击方式来展开攻击，如果攻击者寄生在雅虎广告中，同时用户已经登录到他们的Twitter账户，那么攻击者不需要用户交互就能完成攻击任务。

  

**八、使用查尔斯·达尔文的身份发布推文**

让我们构造一个更好的PoC。此时我们将以达尔文的身份发布推文，甚至尝试抓取他的密码，而不单单满足于读取他的cookie。请时刻记住，大多数用户（比如查尔斯）会使用密码管理器来自动填写密码。Edge浏览器的密码管理器没有什么特别的地方，因此，如果查尔斯已经保存了他的密码，我们就能抓取到这个密码。这个任务并不是特别难，我们只需要强迫他注销登录，那么登录页面就会自动加载，同时他的信息（用户名和密码）就会通过一个silver播放器发送给我们的服务器。事实上，在这种情况下，除非用户主动与页面交互，否则页面中的表单会处于隐藏状态，然而Edge浏览器使用自动填充方式填写表单，因此我们甚至没有必要设置表单为可见状态。

在运行PoC之前，你要注意到，这个PoC暴露的是你自己的账户信息，而不是查尔斯的。当然没有任何数据会发往服务器，但如果有某人躲在你的背后，他还是可以在常规的alert对话框中看到你的密码，还是小心为好。

**视频一：自动发表推文**

**视频二：手动发表推文**

你可以使用Edge浏览器在线测试这个PoC。

  

**九、其他的问题**

我也想到了其他问题，比如，我们能够对那些没有about:blank
iframe的页面使用这种技巧吗？当然可以！我们这种方法甚至对那些没有任何iframe的网站都是有效的！请阅读[这篇文章](https://www.brokenbrowser.com/referer-spoofing-patch-bypass/)，其中我们将一个iframe注入到了另一个不同源上。[另一篇文章](https://www.brokenbrowser.com/uxss-ie-htmlfile/)针对的是Internet Explorer浏览器。

对于Facebook而言，这种方法是否也能奏效？我没有facebook账户，因此我没有测试这种情况。但是成功绕过SOP后我们就可以访问地球上的任何一个domain。当然利用情况可能会有些复杂，大家可以努力一下。

这种方法在其他浏览器上是否也能奏效？我没有尝试，但答案显然是否定的。因为UXSS/SOP绕过方法对于不同浏览器来说都是不一样的。

你可以访问这个[网址](https://goo.gl/8UY2y5)下载漏洞利用代码。

本文翻译自brokenbrowser.com [原文链接](https://www.brokenbrowser.com/sop-bypass-uxss-tweeting-like-charles-darwin/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85987](/post/id/85987)

安全客 - 有思想的安全新媒体

本文转载自: [brokenbrowser.com](https://www.brokenbrowser.com/sop-bypass-uxss-tweeting-like-charles-darwin/)

如若转载,请注明出处： <https://www.brokenbrowser.com/sop-bypass-uxss-tweeting-like-charles-darwin/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

