![](https://image.3001.net/images/20200513/1589353987_5ebb9e039c7ec.jpg!small)

**本文讲述了作者用Chrome浏览器开发工具DevTool，在Gmail的跨域通信中发现了隐蔽的DOM XSS漏洞，最终收获了谷歌$5000的奖励。**

## Gmail中的隐蔽消息

去年底，我在Gmail中研究起了DOM
XSS漏洞，我并没用url参数或邮件本身来构造攻击面，而是把关注点放到了其中那些细微但却频繁使用到的postMessage
api接口之上。初看起来，Gmail的收件箱像是一个简单网页，但是如果细细分析，你会发现，其背后是由多个不同框架（iframes）或网页进行相互通信的支撑。如下：

![](https://image.3001.net/images/20200513/1589353256_5ebb9b28c42e6.png!small)

首先，我去寻找跨域通信(cross-frames)，在Chrome的开发套件DevTools中并没有直接分析跨域通信的原生功能，这里，我们可以用这个简单的插件 -[ postMessage
logger](https://github.com/opnsec/postMessage-logger)，它可以记录下当前的跨域通信情况。如下当Gmail收件箱加载后，Chrome开发套件就可以显示出大量不同域下的各个框架间的通信，它们负责来回传递消息。

![](https://image.3001.net/images/20200513/1589353372_5ebb9b9c0137d.png!small)

上述每一个消息都有以下属性：

> 一个接收目标（即接收消息的框架frame）
>
> 一个消息发送源（发送消息的框架frame）
>
> 一个域（origin，消息源所在的域地址）
>
> 数据（一个字符串或一个JSON实体，或其它交互内容）

消息可在不同的框架frame间被传递，如果消息发送源对接收目标有指定的话，甚至可用window.opener、window.open() 和
window.frames方法，实现在不同域（Domain）或不同标签（Tab）下的框架进行消息传递。

接收目标用以下方法接收消息，就像上述插件postMessage logger中那样：

    
    
    addEventListener("message", function(message){/* handle message here */})

如果消息过多，可以在插件postMessage
logger中定制化过滤不同属性。在这些众多消息中，我发现了一个特别的消息，它在数据段中包含了一个url参数：

![](https://image.3001.net/images/20200513/1589353389_5ebb9bad07099.png!small)

该消息由域名“hangouts.google.com”发送至“mail.google.com”，其不仅在消息数据段中包含参数url，而且该url参数中还包含了“frame”的字眼，哦，看来有点意思。

## 运用Chrome浏览器开发者工具

用Chrome浏览器的开发者工具，在其Network的网络活动标签下，通过点击Document文档类请求的"Doc"过滤标签，以此过滤出那些顶层窗口或带有src属性的iframes，在这里我找到了上述提到的那条特别的消息。如下：

![](https://image.3001.net/images/20200513/1589353464_5ebb9bf80bc1f.png!small)

可以肯定该消息的请求referrer属性为“mail.google.com”
，这就太好了，因为“mail.google.com”同时也是消息的接收目标。上图红圈中的为请求发起者“initiator”，其中的JS代码负责加载调用到的iframe，可以点击“initiator”就能打开相应的JS代码，在该代码段中，通过设置和跟踪断点，就能发现加载上述消息请求的具体代码位置，如下：

![](https://image.3001.net/images/20200513/1589353477_5ebb9c057f45b.png!small)

如上图所示，appendChild()方法负责加载上述请求消息。从该可读代码中我们可以清楚地看到其调用机制，从调试器中可以看到其消息中包含了一个src参数设置为url的iframe框架。如果点击Chrome浏览器工具右边部分的Call
Stack区域，就能看到整个消息的运行机制和逻辑。

例如，以下描述是frame的消息接收机制：

![](https://image.3001.net/images/20200513/1589353501_5ebb9c1d3054e.png!small)

以下是消息发送源的发送机制：

![](https://image.3001.net/images/20200513/1589353517_5ebb9c2d49ee6.png!small)

这里要提醒一下：在消息的listener和url加载端之间，存在各种各样的文件和代码，可以使用浏览器开发工具对其进行不断的调试运行，总之这是一个反复试错的过程。

有了以下了解之后，利用上述消息，我在客户端中把消息中src涉及的url参数替换成了“javascript:alert(1)”
进行测试，然而，我并没有得到一个alert弹窗，原因在于内容安全策略CSP的阻挡。

![](https://image.3001.net/images/20200513/1589353565_5ebb9c5d7d292.png!small)

但是，好在发现该漏洞的时候，IE11 和 Edge 中没有强制CSP策略，因此在这两个浏览器中就能实现“javascript:alert(1)”
的触发实现。该漏洞原因在于未对消息源origin进行检查，一种简单的攻击场景就是，攻击者从Gmail页面中打开新标签，用postMessage方法在标签页中注入Payload。攻击者利用该方法可从受害者Gmail页面中执行任意代码，从Gmail标签中加载javascript形式的iframe，深入利用可读取并发送受害者邮件，甚至是更改受害者邮箱密码。

## 随机的频道名称（Channel Name）

最后还存在一个问题：在众多的通信frame之间，要找到上述那个特别的消息确实会有些困惑，因为每个消息都会有一个所谓的频道名称（Channel
Name），而由“hangouts.google.com”发送至“mail.google.com”的消息频道名称是一个6位数的数字组成，它包含在第一个交互消息中，在后续的交互消息中，“hangouts.google.com”会以该频道名称为验证，只有具备该频道名称的消息才会被“hangouts.google.com”发送处理。

所以对于攻击者来说，要想利用这种漏洞，那么首先这种随机性的频道名称（Channel
Name）确实很难捉摸确定，不过[2012年有安全研究者曾对这种消息机制中的随机数生成方法Math.random()
进行了利用](http://ifsec.blogspot.com/2012/09/of-html5-security-cross-domain.html)，并在Facebook API中发现了XSS漏洞，但是，该漏洞利用需要在跨域的网页中共享随机数生成器（random
generator ）的状态。

当然了，另外还可以在在Gmail标签页面的框架层次结构中加载由攻击者控制的iframe。由于iframe的跨域重定向在浏览器中的工作方式，且Gmail网页通信中的X-Frame-Options属性为SAMEORIGIN”，且消息发送参数targetOrigin的值为“*”，因此，在网络抓包中也是可以拦截到频道名称（Channel
Name）的 ，那最后也能实现XSS触发利用。

## 总结

反复试验后，我也没在Gmail中找到加载控制iframe的简单方法，但理论上来说，该漏洞是完全可以被攻击者进行利用的。最终我把漏洞上报给了谷歌安全团队，几天之后就收到了他们“Nice
Catch”（好洞）的回复，奖励是$5000美金。谷歌的修复方式是在消息发送源的url参数加入了安全检查。另外，Chrome浏览器的开发者工具是一个非常不错的调试套件，可以支持个性化的插件开发，对Web找洞很帮助。

 ***参考来源：[opensec](https://opnsec.com/2020/05/dom-xss-in-gmail-with-a-little-help-from-chrome/?fbclid=IwAR0lnN4bt_9j8qFcNBajDunxaXtShH2IvArO0VWPVAeYNL8ynz5zaGPsISU)，clouds
编译整理，转载请注明来自 FreeBuf.COM**

