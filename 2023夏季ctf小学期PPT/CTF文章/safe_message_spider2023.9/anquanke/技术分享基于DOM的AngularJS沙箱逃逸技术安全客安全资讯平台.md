# 【技术分享】基于DOM的AngularJS沙箱逃逸技术

阅读量 **126103**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-05-15 12:00:31

 **x**

##### 译文声明

本文是翻译文章，文章来源：portswigger.net

原文地址：<http://blog.portswigger.net/2017/05/dom-based-angularjs-sandbox-escapes.html>

译文仅供参考，具体内容表达以及含义原文为准。

****

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**0x00 前言**

去年，在发表的“[XSS Without HTML: Client-Side Template Injection with
AngularJS](http://blog.portswigger.net/2016/01/xss-without-html-client-side-template.html)”中，我们展示了使用AngularJS框架会导致网站遭遇跨站脚本攻击（XSS），只需有个合适的沙箱逃逸。在本文中，我们将介绍如何开发一个能工作在之前不可利用的上下文中的沙箱逃逸——过滤器排序。我已经编写了整个利用开发过程，包括各种不太完善的技术。

**  
**

**0x01 Angular沙箱历史**

当第一次发布Angular时还没有沙箱，因此在版本1.0-1.1.5是没有沙箱的。但是Angular表达式被开发者限定为局部对象定义，这阻止了在窗口对象中调用函数，因为你将被作用域限制，如果你试图调用alert，将调用的是作用域对象而不是窗口对象，函数调用将失败。Mario
Heiderich找到了一种方式，使用构造函数属性绕过这个限制。他发现使用Function构造函数你能在表达式中执行任意代码。

在这里，constructor的作用域是Object构造函数。constructor.constructor是Function构造函数，允许你生成一个以字符串为参数的函数，因此能执行任意代码。

在Mario的利用之后，ensureSafeMemberName函数出现了。这个函数针对构造函数属性检查JavaScript属性，同时拒绝包含下划线开头或结尾的字符串。

Jan horn发现第一个公开的沙箱逃逸是针对版本1.2.0的。

他使用sub函数（是一个很古老的javascript的string方法）作为一个快捷方式，能在Angular中获得一个函数，因为它是一个非常短的名字。然后使用call.call能得到一个类call方法；正常情况当你是用单独的call方法将在当前函数执行，但是使用call.call的类call方法将允许你选择一个函数执行。

他然后使用getOwnPropertyDescriptor得到函数原型对象的描述符和构造函数的属性。描述符是描述一个对象属性的对象文字；它能告诉你属性是否是可枚举、可配置和可写的，和它是否有getter和setter。“value”也将包含属性值的引用。

Value将包含Function构造函数的引用，是他发送给call方法的第一个参数。第二个参数不重要——它的目的是指定执行函数时使用的对象，但是Function构造函数会忽略它并使用窗口对象代替。最后他传递他希望执行的代码，通过Function构造函数生成一个新的函数成功沙箱逃逸了。

为了回应这个精彩的绕过，Angular增强了他们的沙箱。他们增强了ensureSafeMemberName函数，以检查指定的属性名（如__proto__）。

他们也增加了一个新的函数来检查引用或调用函数时指定的对象。函数ensureSafeObject检查Function构造函数，窗口对象，DOM元素和Object构造函数。

然后，关于沙箱逃逸有个小爆发，每个版本的Angular沙箱都被打破了。我写了[一篇博文](http://blog.portswigger.net/2016/01/xss-without-html-client-side-template.html)关于我的沙箱逃逸，并且也列举了从早前的逃逸到最新版本(1.5.11)的逃逸。最终Angular决定为了性能在1.6版本中完全[移除沙箱](http://angularjs.blogspot.co.uk/2016/09/angular-16-expression-sandbox-removal.html)，因为他们不考虑将沙箱作为一个安全特性了。

**0x02 开发基于DOM的沙箱逃逸**

****你可能认为沙箱逃逸没啥意思了，因为在Angular 1.6将被移除了。然而却完全不是。在我在伦敦的演讲后，[Lewis
Ardern](https://twitter.com/lewisardern)指出了[在过滤器排序中也能执行Angular表达式](https://blogs.synopsys.com/software-integrity/2016/12/28/angularjs-1-6-0-sandbox/)，并且开发者可能使用用户的输入（如location.hash）来设置过滤器顺序。  

我注意到解析的代码在没有“｛｛”和“｝｝”的情况下被解析和执行，并且$
eval和$$watcher在沙箱环境中不可用。这使得之前大量的沙箱逃逸都失效了，因为我们依赖$
eval和$$watcher。如果我们看过下面公开的沙箱逃逸，你能看见只有一个内容排序的可以使用，其他的都失效了。

我决定从1.3.0版本开始。首先的问题是我不得不解决如何在这个环境中枚举对象，以便我能看见什么属性是可靠的。修改String原型提供了一个有用的方法以检查沙箱代码；我能分配我想要的属性来检查相同的名字的字符串原型，然后使用setTimeout得到那个值。代码如下：

然后我从Angular源代码中提取了所有的关键字和变量，并在[沙箱中运行](https://jsfiddle.net/0Lh8rw3b/3/)。尽管代码无法告诉我有类似$eval危险的函数能用来沙箱逃逸，但是我还是发现了有趣的行为。当使用带有[].toString的Object原型定义一个getter时，我发现join函数会被调用。这里的想法是的到join函数以调用Function构造函数，传参，并执行任意的JavaScript。我使用的fiddle在[这里](https://jsfiddle.net/0Lh8rw3b/4/)可以找到。在主流的浏览器中使用toString函数作为对象的getter或方法将自动调用join。不幸的是，我不能找到一种方式来传递参数。下面是在Angular代码之前的工作原理。

它甚至能在Windows上工作。下面的例子使用[].toString覆盖了窗口的toString属性，并且你能看到join被调用了。

因此，我模糊测试了所有的对象和属性，看到了其他的函数也调用了join。当是使用定义数组中的getter也会调用join：copyWithin, fill,
reverse, sort, valueOf, toString。

**  
**

**0x03 打破1.3.0**

****非常酷的行为，但是我决定改变方向，并尝试些别的东西。我继续研究1.3.0，注意到当改变Object原型时，你能引用Function和Object构造函数。当调用Function构造函数时，Angular将抛出异常，但是因为我能访问Object构造函数，我就能访问它所有的方法。  

我是用数组属性访问器来绕过Angular的ensureSafeMemberName检查，因为Angular使用严格的等号运算符来查找危险字符串。使用之前提到的对象枚举技术，我看见了Object构造函数成功被赋值了。我首先创建一个getOwnPropertyDescriptor的引用，然后给它赋值变量“g”。

接下来，我使用getOwnPropertyDescriptor获得Function原型描述符。我将稍后使用它得到Function构造函数。

我也需要defineProperty，因此我能覆盖构造函数的属性以绕过Angular的ensureSafeObject检查。

下面是我使用defineProperty覆盖构造函数为false。

最后，我使用getOwnPropertyDescriptor得到描述符，以得到不使用构造函数属性的Function构造函数。

完整的沙箱逃逸代码如下，在Angular 1.2.24-1.2.26/1.3.0-1.3.1中有效。

**[沙箱逃逸PoC 1.3.0](http://portswigger-labs.net/angular_dom_based_sandbox_escapes/?version=1.3.0#%7B%7D%5B%5B%27__proto__%27%5D%5D%5B%27x%27%5D=constructor.getOwnPropertyDescriptor;g=%7B%7D%5B%5B%27__proto__%27%5D%5D%5B%27x%27%5D;%7B%7D%5B%5B%27__proto__%27%5D%5D%5B%27y%27%5D=g%28%27%27.sub%5B%5B%27__proto__%27%5D%5D,%)**

**  
**

**0x04 1.3的分支**

沙箱逃逸非常酷，但是它只能工作于有限的Angular版本中。我想覆盖整个1.3分支。我开始查看他们如何解析表达式。在测试版本1.2.27中我在1192行中添加了断点，开始测试各种对象属性，看他们如何重写代码。我得到了一些有趣的事，如果没有包含字母数字属性，Angular似乎会吃掉分号字符，并将它作为对象属性。

下面是Angular如何重写代码（注意必须在调试器中继续5次）：

如你所见，Angular在重写输出中包含两次分号。要是我们打破双引号会怎样？我们能使用基本的XSS攻击重写代码，并绕过沙箱。为了实现这个，我们需要提供一个可靠的字符串给Angular，因此我们不能破环初始的表达式解析。Angular也能很好的解析带有引号的对象属性，因此我能最小程度上沙箱逃逸：

重写输出如下：

[沙箱逃逸PoC 1.2.27](http://portswigger-labs.net/angular_dom_based_sandbox_escapes/?version=1.2.27#%7B%7D.%22,alert%281%29,%22;)

为了将这个应用于1.3分支，我们只需要稍微改变向量，以打破重写代码。如果你观察1.3.4版本的重写代码，你能注意到它创建了一个语法错误。

我们只需要打破这个，注释输出语法错误，下面是最终的向量，能在1.2.27-1.2.29/1.3.0-1.3.20中有效。

[沙箱逃逸PoC 1.3.20](http://portswigger-labs.net/angular_dom_based_sandbox_escapes/?version=1.3.20#%7B%7D.%22%29%29%29;alert%281%29//%22;)

**0x05 攻破1.4**

****接下来，我决定研究1.4分支。在1.4之前的版本可以使用数组访问__proto__，__defineSetter__的技巧。我认为我可以使用那些属性/方法中的部分来完成沙箱逃逸。我需要覆盖构造函数并能访问Function构造函数的，但是这次我不能访问Object构造函数，因为沙箱的功能增强了。  

在Safari/IE11中，设置全局变量使用__proto__是可能的。你不能覆盖已存在的属性，但是你能创建新的。这是个死胡同，因为定义属性的优先级高于Object原型。

因为Angular在ensureSafeObject使用有效的检查，我认为使用boolean可能会是检查失败，然后能访问到Function构造函数。然而，Angular检查了对象链中所有的属性，因此它能检测到构造函数。下面是它如何工作的。

通过将它的__proto__属性赋值为null来覆盖Function的构造函数属性也是可能的，这将使得构造函数未定义，但是如果使用Function.prototype.constructor，您能得到原始的Function构造函数。这被证明是另一个死胡同，因为为了覆盖Function构造函数的__proto__属性，你需要先访问它，
但是Angular会阻止。你能覆盖每个函数的构造函数属性，但是很不幸你不能访问原始的。

在Firefox
51中，使用__lookupGetter__得到函数的调用者是可能的。所有的其他的浏览器阻止使用这种方式。但是在Angular中没有提供函数，再次是个死胡同。

我继续看了使用__defineGetter__和valueOf来创建Function构造函数的别名。

你也能使用getter执行一个函数，通常需要一个对象。因此“this”值成为赋值给getter的对象。例如，__proto__函数不会无对象执行，使用getter允许你使用__proto__函数得到对象原型。

上面的技术将失败，因为即使我创建了Function构造函数的别名，还是没有办法在不破坏构造函数属性的情况下访问Function构造函数。但是它给了我一个想法。也许我可以在窗口作用域内使用__lookupGetter__/__defineSetter__。

在Chrome中，你能保存__lookupGetter__的引用，并且使用窗口作为默认的对象，使你能访问文档对象。

你也能使用__defineSetter__。

Angular将直接函数调用（如alert()）转化为Angular对象的方法调用。为了解决这个，我使用间接调用‘(l=l)’，使得__lookupGetter__执行于窗口上下文中，保证了文档对象的访问。

现在有了文档对象的访问，因此能终结Angular了？还没有。Angular还会检查每个对象是否是DOM值：

当getter函数被调用时，Angular将阻止文档对象。我认为我能使用__defineGetter__赋值getter函数，但是这将破环窗口的引用，因此文档不会被返回。我测试了Chrome
56.0.2924.87中的每个属性以观察哪个getter是可靠的，只有__proto__和文档是可靠的。然后我决定测试Chrome beta
57.0.2987.54，得到了大量的getter。

我浏览了所有的getter，开始测试观察我是否能执行任意代码。我发现我能盗取localStorage和向导历史记录，但是没啥威胁。在测试一段时间后，我注意到事件对象是可靠的。每个事件对象有一个target属性，其引用了事件当前的DOM对象。结果是Angular不会检查这个属性，我能使用target属性执行代码得到文档对象和defaultView，以访问窗口然后赋值location。

[沙箱逃逸PoC 1.4.5（只支持chrome）](http://portswigger-labs.net/angular_dom_based_sandbox_escapes/?version=1.4.5#o=%7B%7D;l=o%5B%5B%27__lookupGetter__%27%5D%5D;%28l=l%29%28%27event%27%29%28%29.target.defaultView.location=%27javascript:alert%281%29%27;)

**0x06 打破更新版本的沙箱**

****在更新版本的Angular沙箱中，__lookupGetter__函数被保护了。你不再能使用数组对象访问它。为了在这些版本中利用，我需要一些Angular
eval，因此我们回顾下在上下文排序中的常规的Angular表达式中的利用。过滤器排序能使用一个字符串作为Angular表达式，因此我们能通过从外部排序调用嵌套的排序来得到我们的eval。  

首先我们执行第一部分的沙箱逃逸，确保charAt返回一个比单个字符长的字符串，打破我在[上篇文章](http://blog.portswigger.net/2016/01/xss-without-html-client-side-template.html)中提到的isIdent函数。然后针对我们的字符串payload调用过滤器排序。

[沙箱逃逸PoC 1.5.0（只支持chrome）](http://portswigger-labs.net/angular_dom_based_sandbox_escapes/?version=1.5.0#x=%7By:%27%27.constructor.prototype%7D;x.y.charAt=%5B%5D.join;%5B1%5D%7CorderBy:%27x=alert%281%29%27)

**0x07 打破CSP模式**

****之前的沙箱逃逸能在版本1.5.0-1.5.8上面有效。因此我从1.5.11开始，观察有什么可以破环。不幸的是，我不能在基于DOM的上下文中打破它，即使我发现了在属性中的一个绕过。使用我的对象枚举策略，我发现在chrome中，Angular中的$event对象在它的path属性中包含了一个数组。这个path属性包含的数组存储了文档和窗口。通过传递这个数组给过滤器排序，我能改变表达式的作用域，在窗口中执行：  

这个逃逸能在属性上下文中有效，但是当你启用了CSP，将失败。Angular似乎在CSP模式下会检查调用函数的窗口对象，因此能阻止沙箱逃逸运行。为了绕过这个，我需要间接调用alert函数，同时Array.from函数提供了简单的方法实现这个。它有两个参数；一个类似对象的数组和在数组每个对象执行的一个函数。我将在第一个参数中传递数组，在第二个参数中传递要调用的alert函数。这将绕过CSP模式，应该能在所有的Angular的版本中有效。

[CSP绕过1.5.11（只支持chrome）](http://portswigger-labs.net/angular_csp_bypass_1.5.11/?x=%3Cinput+autofocus%20ng-focus=%22%24event.path%7CorderBy:%27%21x?%5b%5d.constructor.from%28%5bx=1%5d,alert%29:0%27%22%3E)

**0x08 总结**

****当使用Angular时，避免用户输入直接传递给排序过滤器，用户输入的服务端反射也是。不管使用哪个版本的Angular，要明白正在解释的用户输入在什么上下文中，它通常最容易被利用绕过沙箱。  

如果你想在你的语言中添加沙箱，仔细考虑安全效益是够大于开发成本，以及是否有潜在的隐患。

**0x09 基于DOM的Angular沙箱逃逸的列表**

本文翻译自portswigger.net [原文链接](http://blog.portswigger.net/2017/05/dom-based-angularjs-sandbox-escapes.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **root** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86093](/post/id/86093)

安全客 - 有思想的安全新媒体

本文转载自: [portswigger.net](http://blog.portswigger.net/2017/05/dom-based-angularjs-sandbox-escapes.html)

如若转载,请注明出处： <http://blog.portswigger.net/2017/05/dom-based-angularjs-sandbox-escapes.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) root

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

