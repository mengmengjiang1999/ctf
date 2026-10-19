原文：[brokenbrowser](https://www.brokenbrowser.com/sop-bypass-uxss-tweeting-like-charles-darwin/)  
原作者: Manuel Caballero  
译： **Holic (知道创宇404安全实验室)**

今天我们探索 Microsoft Edge 上的另一个 SOP 绕过，而此处 data/meta 标签的滥用，侧面证实了无域页面是可以随意访问有域的页面的。

着急吗？可以先看这 59 秒的视频，其中我们[代表 Charles Darwin
发了条推特](https://youtu.be/K3Ui3JxZGnE)，或者，观看我们手动[发推并抓取用户的密码](https://youtu.be/PlxQBmLrnQA)（利用了
Microsoft Edge 的默认密码管理器）。Charles Darwin
是一个案例，该漏洞可以让攻击者用已经登录的用户的名义发推（或是更多的事情）。欲知详情如何，请继续阅读。

如果你第一次看本博客，我建议你先阅读这两篇 SOP 绕过的文章： [Adventures in a Domainless World
(Edge)](https://www.brokenbrowser.com/uxss-edge-domainless-world/) 和 [More
Adventures in a Domainless World (IE)](https://www.brokenbrowser.com/uxss-ie-domainless-world/)。后续文章基于相同的思路，只是用了一点新技术。

（对应 Paper 译文：http://paper.seebug.org/143/ 和 http://paper.seebug.org/254/ ）

接下来快速回顾一个重要概念： **about:blank 始终是其 referrer 的域** ，意味着来自 Twitter 的 about:blank
iframe 不能访问 google 的 blank 页面。即使他们之间的地址是匹配的（about:blank），document.domain
却是不同的。

过去，我们无须域名就能创建 about:blank ，或者 **无域的 about:blank** 。那些都有权访问每个 about:blank
而无视其域。比如，假设我们在主页上有一个无域的 blank，渲染了一个指向 Twitter，另一个指向 google 的 iframe。那些 iframe
中同样有空的子 iframe，其域当然也是 twitter 和 google。在这种情况下，顶部窗口可以访问有域的空页面，意味着可以访问 google 和
Twitter 的 DOM 了。

![](https://images.seebug.org/content/images/2017/04/00-domainless-blank-chart.png-w331s)

上述情景效果很好，但是微软三个月前用一个[很机智的技巧](https://www.brokenbrowser.com/free-ticket-to-the-intranet-zone/) [修复了这个 bug](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-0002):无域的 blank 已经不再是无域的了，而被设置为其域名的
GUID，比如{53394a4f-8c04-46ab-94af-3ab86ffcfd4c}。还有一些更有意思的东西（向微软开发者致敬）：域看起来像是空的，其实不是。换句话说，Edge
隐藏 GUID 并返回空，而在其内部仍是 GUID。

试一下便知！打开 Edge 启用 Devtools（F12)，然后在地址栏输入
about:blank。用于创建一个无域的空白页面，它仍然看起来没有变化，这是 Edge 在给我们上演戏法。请稍事欣赏，我们有足够的时间打破它的魔咒。

![](https://images.seebug.org/content/images/2017/04/01-about-lies.png-w331s)

如你所见，DevTools 认为我们在空域之下，其实并不是。

### 打破魔咒

如果就连 DevTools 都被欺骗了，又如何了解其中发生了什么呢？比想象中简单，仅需尝试加载有相对路径的东西，或者改变 window 的
location，甚至 document.write 都会揭露这个把戏。使用 location.href=1，看看会发生什么。

![](https://images.seebug.org/content/images/2017/04/02-real-url.png-w331s)

### 顶层 data:uri 被修复以及 Flash 禁用的情况

我们之前[创建无域空白页面](https://www.brokenbrowser.com/uxss-edge-domainless-world/)的技术已修复。我们也曾借助 Flash/GetURL 在主（顶层） window 上设置
data:uri。而这些技巧都被修复了，更糟糕的是，已经不会自动运行 Flash 了！Windows 创意者更新中，运行 Flash 之前 Edge
会请求权限。

注意，捉虫猎手！之前文章的 [PoC](http://unsafe.cracking.com.ar/demos/edge-domainless-uxss/bing/index.html)现在看起来很不美观！表扬下 Edge 团队，这一措施减少了攻击面。

![](https://images.seebug.org/content/images/2017/04/03-enable-flash-madam.png-w331s)

### 寻找新的无域空页面

针对顶层的 data:uri 技巧已经没有用了，那么我们又如何攻克呢。首先，我先研究 iframe 而不是顶层，因为我们在过去看到，Edge 不喜欢主窗口的
data:uri。

    
    
    top.location.href = "data:text/html,SOMETHING"; // Fails badly, error page

而将 data:uri 设置为 iframe 的 location 则颇为有效。但这并不是一个 bug，iframe 的域是与顶层隔离的。

![](https://images.seebug.org/content/images/2017/04/04-setting-data-uri.png-w331s)

正如在[阅读模式 SOP 绕过](https://www.brokenbrowser.com/sop-bypass-abusing-read-protocol/)中看过的，data:uri 的『隔离』限制微不足道（仅一个 self document.write
就能访问父页面），但不是我们现在想要的。访问顶层现在毫无意义，我们想要能访问无域空白页面方法。为此，我们需要三连击：data-meta-data。然后重获
Edge 那些修复的特性。

具体来说，我们使用 data uri 设置 iframe 的 location，该 uri 会渲染 meta 刷新，重定向至另一个 data
uri。这都是我们和 Edge 忽略的地方。

> 创建无域空白页面的方法：
>
>   1. 设置 iframe 的 location 为 data:uri
>
>   2. data:uri 渲染了 meta refresh 标签
>
>   3. meta refresh 重定向至另一个 data:uri
>
>

我们构建一个 URL ，将常规的（有域）的 iframe 转换为无域的。如果在脑海中不断重复『data-meta-data』，会更容易一些，因为...实际就是这样。

![](https://images.seebug.org/content/images/2017/04/05-domainless-recipe.png-w331s)

我知道它没有 E=mc2 那么漂亮，但是这一技巧可以用来偷取爱因斯坦的登录凭据，电子邮件，PayPal
账户，甚至以他的名义发推。我们先测试所学的技巧，直到这点生效为止。我们用 bing.com 做演示，颇为简单，因为它内部有一个空白页面的 iframe
而且不使用 XFO。

### 用 bing.com 热身

我们将创建有两个 iframe 的页面：其一是 bing.com ，另一个是无域的。无域页面将在 bing 内部的blank iframe
中执行代码。Bing 图片正是我们想要的。我先打开 Chrome 展示下我想表达的意思。

![](https://images.seebug.org/content/images/2017/04/06-bing-is-easy.png-w331s)

很不错。现在我们借助 **无域的 data-meta-data** 构建页面并将代码注入到 blank iframe 中。但有一些话我还没讲。你还记得在那篇
[domainless SOP](https://www.brokenbrowser.com/uxss-edge-domainless-world/) 中用
nature.com 演示的命名问题吗？若是没有，我给你快速回顾一下。

这一点上，我们的无域 iframe 能够访问 bing 中的 blank 页面，而访问机制尤其重要。我们不能直接访问 DOM，必须使用
window.open 方法。换句话说，我们无法以这种方式访问 iframe 的内部：

    
    
    alert(top[0][0].document.cookie); // ACCESS DENIED

其实我们甚至不能这样做：

    
    
    top[0][0].location.href = "javascript:alert(document.cookie)"; // ACCESS DENIED

那我们应该怎么办呢？很简单，利用 JavaScript url 和 iframe 的名称(name 属性，后统称名称)打开窗口。如果 bing 内部
iframe 名称为 " **INNER_IFRAME** "，以下代码将运行正常。

    
    
    window.open("javascript:alert(document.cookie)", "INNER_IFRAME"); // SOP BYPASSED!

可恶， Bing 中嵌套的 iframe 没有名称（name）！不要惊慌，要么我们请求 Bing 团队为我们设置一个名称，要么继续推进。更好地继续推进！

### 设置 iframe 的名称（name）

我们不能设置不属于我们的 iframe 的名称，除非它与我们在同一个域中。然后要渲染一个内有 blank 页面的 iframe。外部 iframe
属于不同的域，但标签本身（元素，对象）位于我们的域中，因此我们可以设置我们想要的任何名称。

    
    
    <iframe name="ANY_NAME" src="http://bing.com">
       <iframe src="about:blank"></iframe>
    </iframe>

而内部 iframe 是通过 bing 渲染的，即使它是空白页面，更改它名称的方法也只能是将其 location
设置为我们可以访问的，然后才能更改其名称。如果现在改变 about:blank 的 location，无异于搬石头砸脚，因为我们需要改成 bing.com
以便之后访问无域的页面。

记住，我们的目标是利用无域的空白页面访问一个有域的页面。若是将域设置为相同的，那么这种访问毫无意义。因此我们要做的就是：设置 location，更改
iframe 的名称，然后 **把 location 恢复回来** ，使其保持原始的域。听起来挺复杂的？

> 设置x-domain-iframe 的 name：
>
>   1. 将 iframe 的 location 设置为 about:blank，将其域更改为可控的 crack.com.ar
>   2. 随意更改 iframe 的名称。
>   3. 再把 location **改回来** ，但这次使用 meta refresh，使其域==其创建者：bing.com 。
>

就酱。现在内部 iframe 有了名称，它的域也恢复到了 bing.com！代码如下：

    
    
    // Sets the location of Bing's inner iframe to about:blank
    // But now it is in our domain so we can set a name to it.
    window[0][0].location = "about:blank";
    
    // Set the inner iframe name to "CHARLES" so we can later inject code
    // using a window.open("javascript:[...]","CHARLES");
    window[0][0].name = "CHARLES";
    
    // Restore Bing's domain to the about:blank that we've just renamed.
    window[0][0].document.write('<meta http-equiv="refresh" content="0;url=about:blank">');
    window[0][0].document.close();

好消息是：我们并不需要带有"about:blank" iframe 的网站，因为按照以上方法就行了。换而言之， bing 的内部的 iframe 是不是
about:blank 并不重要，因为我们最后都能用它原来的域将其设为
blank！我不知道你怎么想的，捉虫猎手，但我感觉这就像演员中的[汤姆·汉克斯（Tom
Hanks），看看便知](https://youtu.be/LUDEjulbqzk?t=68)。

大门为我们敞开！我们可以从我们的 data-meta-data iframe 中运行 window.open:

    
    
    window.open("javascript:alert(document.cookie)", "CHARLES"); // Fireeeeeeeeeee!!!

![](https://images.seebug.org/content/images/2017/04/07-bing-likes-cookies.png-w331s)

**[[Test the PoC Live on
Edge]](http://unsafe.cracking.com.ar/demos/edgedatametadata/bing.html)**

**[[Video in YouTube]](https://youtu.be/E_6OFcTi5kQ)**

有关 PoC 的一个重要事项：上述示例中，我们使用 http（不安全）连接，因为在 https（安全）中，meta refresh
是会被阻止的，所以不会重定向至最终的data uri。Edge 误以为重定向是不安全的。然而，这点可以通过使用 document.write 取代 data
uri 轻松绕过。所以将 data-meta-data 应该替换为 document.write(meta-data) 。是不是这个理？

在上述 PoC 中我没有用到这点，因为它在进行演示交互时（你需要按下按钮运行）Edge 有三分之一的几率崩溃。所以我选择使用 http 下可控且可靠的自动化
PoC 而没在 HTTPS 下。无论如何，下面可以看到这并不重要：我们的不安全（http）无域空白页面可以访问安全的页面，所以我们来构建一个真实的例子。

### 真实情况下的攻击：偷取 Charles 的 cookie

下面是攻击演示了，捉虫猎手。时光机带我们飞到过去，把我们带到有电脑和互联网之前时代。查尔斯·达尔文在考虑物种随时间的变化，阿尔弗雷德·华莱士也有类似的想法。查尔斯意识到黑客的存在，所以他只使用他自己的电脑，近乎偏执：他从来没有使用同一个浏览器窗口打开他的
Gmail，Twitter 已经个人文档。

看，他在任务栏打开了一个新的隐身窗口！

![](https://images.seebug.org/content/images/2017/04/08-paranoid-charles.png-w331s)

他心情不错，直到他用新标签打开了 Twitter 账号，并向阿尔弗雷德·华莱士（Alfred Wallace）调侃谁先发推的消息。

![](https://images.seebug.org/content/images/2017/04/09-charles-tweeting.png-w331s)

几分钟后，华莱士带着证件回应了他。但是别忘了，Charles不信任任何人，所以他复制了链接，将其粘贴至一个新的窗口中，远离他个人数据（gmail，twitter）的窗口。

![](https://images.seebug.org/content/images/2017/04/09-wallace-response.png-w331s)

哪里错了呢？一切！Twitter 有几个 iframe，像大多数网站一样。其实它有两个名为 about:blank 的 iframe，所以这应该比 Bing
容易！但是回到故事之前，我们使用 DevTools 枚举 Twitter 的 iframe，找到一个很好的方案。此处打开一个不同的窗口，与查尔斯的
session 无关。

![](https://images.seebug.org/content/images/2017/04/10-twitter-enumeration.png-w331s)

很好！dm-post-iframe 貌似不错，所以我们需要做的就是接管查理的帐户了。

查尔斯打开一个新的隐身窗口，并加载了华莱士给他的网址。他不知道即使在隐身窗口，也是可以相互通信的。那么，如果我们在无域 iframe
下执行以下代码，会发生什么？

    
    
    window.open("javascript:alert(document.cookie)", "dm-post-iframe");

是的。我们获得了达尔文的 cookie。

![](https://images.seebug.org/content/images/2017/04/11-charles-has-cookies.png-w331s)

> 警告：以下 PoC 将会 alert（仅在您屏幕上显示）您的 Twitter cookie。

[[ Test the PoC Live on Edge
]](http://unsafe.cracking.com.ar/demos/edgedatametadata/cookiesfromcharlie.html)

请记住，我们真的不需要 InPrivate 窗口。上面的例子说明了一个颇为偏执的情景，但通常情况更简单，因为人们一般直接就点开链接了，不会像 Charles
那样做。此外，考虑到攻击者可能会使用[恶意广告](https://blog.malwarebytes.com/101/2015/02/what-is-malvertising/)，在热门网站的廉价 banner 上部署恶意内容。如果攻击者托管于雅虎 banner 内，用户登录她的 Twitter
账户，她就在无须交互的情况下受控了。

### 像达尔文一样发推

来构造一个更好的 PoC 吧。这回不再读取它的 cookie，我们会以他的名义发推，甚至抓取他的密码。请记住，大多数用户（比如
Charles）使用了密码管理器自动填充密码。Edge 密码管理器不出其右，所以如果 Charles
保存了他的密码，我们就能获取到。这不是很难，只是强制让他注销，然后登陆页面就会加载，其所有数据（用户名与密码）都在一个银色播放器中呈现。实际上，这种情况如果用户没进行交互，表单是隐藏的。而
Edge 正进行填充，所以我们甚至不必让表单可见。

在运行 PoC 之前，请记得这是你的账户，而不是 Charles 的。没有其他东西会发送到网络，如果你身后有人，她会在一个常规 alert
中看到你的密码。请小心。

**[Video: Automatic Tweeting 1″](https://youtu.be/K3Ui3JxZGnE)**  
**[Video: Manual Tweeting 2″](https://youtu.be/PlxQBmLrnQA)**  
**[Test the PoC Live on
Edge](http://unsafe.cracking.com.ar/demos/edgedatametadata/tweet-like-charlie.html)**

### 脑海中闪过的问题

我们可以在没有 about:blank iframe 的站点使用这个技巧吗？当然！我们甚至可以在没有 iframe
的网站上使用。请阅读这篇博文，[inject an iframe on a different
origin](https://www.brokenbrowser.com/referer-spoofing-patch-bypass/)，而且在 [IE
上也可以](https://www.brokenbrowser.com/uxss-ie-htmlfile/)。

**在 Facebook 上也可以吗？** 我没有 Facebook 账户，所以没有测试。但是 SOP bypass
可以访问地球上的每个域。开发可能有点难，但不可能吗？记住[攻防安全研究员](https://www.offensive-security.com/)的口头禅：再接再厉。

**在其它浏览器中有效吗？** 我没有试过，但也不是不可能。UXSS / SOP 绕过往往针对特定浏览器。

**[下载所有 PoC](http://paper.seebug.org/papers/Archive//poc/tweeting-like-charles-darwin.zip)**

[利用代码](https://goo.gl/8UY2y5)很简单，请仔细阅读，如果你有问题，[请问](https://twitter.com/magicmac2000)！到此为止，不然这个博客就叫
brokenmarriage.com 了。布宜诺斯艾利斯的深夜。

Have a nice day!

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/287/>

