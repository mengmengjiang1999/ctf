作者：[ZSX](https://blog.zsxsoft.com/post/32 "ZSX")

随着前端技术的高速发展，越来越多的软件正在使用浏览器相关技术作为其组成的一部分。和完全使用传统客户端技术开发的软件相比，部分或完全使用网页前端技术开发的软件有着开发成本低、部署成本低的优势。但自然而然地，我们也可以用常用的针对
Web 进行攻击的技术来攻击这一些客户端。由于客户端软件拥有更大的权限，在 Web 上使用场景严重受限的攻击技术，往往能造成更大的危害。

#### 可以攻击到哪些软件呢？

这一种攻击手法真正做到了“一视同仁”，无论是桌面端还是移动端，不管是什么操作系统，只要是使用了浏览器相关技术，且代码存在缺陷的软件，都有潜在被攻击的可能。

本文在桌面端将围绕着 MSHTML、Electron、nwjs、CEF、QtWebKit
等展开讨论，移动端将围绕着直接引用`android.webkit.WebView`、使用 Cordova 、
5+Runtime（DCloud）等库展开讨论。

#### 攻击方式有哪些呢？

常用的客户端攻击技术，包括缓冲区溢出漏洞等，不在本文的讨论范围中。于是我们还剩下在 Web 里负责最终用户的 XSS / CSRF / MITM
等、负责服务器的 SQL Injection / SSRF / 命令注入 / 文件上传等，同时还能把一些客户端攻击技术与 Web 结合，处理成新的攻击手段。

#### 用途较少的 Web 攻击技术

负责服务器的 Web 攻击技术对客户端大部分都没有什么用途，原因包括：

  1. 我们一般不直接和客户端进行连接，往往都通过服务器中转，那直接攻击服务器会是更好的选择；
  2. 客户端的内网环境大多都没有什么敏感内容能作为进一步攻击的跳板（如攻击Redis、攻击MySQL、攻击SQL Server）。

SQL Injection还是有一定程度上的利用价值的，但客户端的 SQL 注入仍然比较鸡肋。大部分客户端都使用 SQLite
作为其本地关系型数据库，一般只能注入获得用户信息；而使用 Electron 编写的客户端在本地开个 PouchDB
之类的轻量级非关系型数据库也就是一两行的事情。即使注入成功，还可能缺少把信息传出的机制。需要配合其他漏洞使用。

CSRF和客户端更没有多大关系，它走的仍然是服务器的接口。

#### HTML Hijacking

在 Windows 下，有一种常见的攻击手段叫 DLL Hijacking。绝大部分程序都有代码重用的需求，不能把代码静态编译到 exe
内。为了解决这种问题，就出现了动态链接库（DLL）技术。程序使用 `LoadLibrary` 将DLL加载进内存，然后执行 DLL
内的代码。自然而然地，如果我们把程序要加载的 DLL 替换为我们自己的 DLL，那我们就可以让程序执行我们想要的任意代码。需要注意的是，这并不是
Windows 的专属问题，Linux 和 macOS 下也可以劫持 .so 文件。

而在 WebApp 中，我们可以注意到，几乎所有的 .html 文件都是外部资源。对这些外部资源进行修改，就达到了和 DLL Hijacking
相同的效果。

Electron 中，资源通常以 asar 格式打包或者不打包，存放在 resources 目录之下。asar 格式类似
tar，只做归档，不提供签名和校验功能。也就是说，我们只要把 resources 目录进行替换，就可以让 Electron App 执行任意代码。

我们举一个非常恶趣味的例子，让 WordPress.com 和 Ghost 的 Native App 的代码互换。

![](https://images.seebug.org/content/images/2017/11/056c4c00-6842-4287-89a4-7c7e25574025.png-w331s)

![](https://images.seebug.org/content/images/2017/11/1face5a7-47c6-4980-ba92-a6b80839ac71.png-w331s)

可以注意到，`Ghost.exe`的数字签名还是一切正常的状态。

——那边用 CEF 的别笑，你们也一样。只要你们的HTML文件存在本地，就拥有被劫持的可能。

这种攻击对目标用户有什么用呢？当然，它并不直接攻击目标用户。他的用途包括：

  1. 通过其他漏洞入侵用户电脑后，可以通过这种方式把恶意代码隐藏，达到就算用户使用杀毒软件清理病毒后，启动你的程序便又“春风吹又生”的效果。早年的`lpk.dll`系列病毒便是基于这个原理。
  2. 如果你的程序有数字签名，我就可以把恶意代码藏在JS里。这并不破坏数字签名，若用户在非官方网站下载到带料的你的程序，由于有数字签名的存在，用户会认为是你的程序有恶意代码，或是根本查不到源头。杀毒软件一般对于有数字签名的程序会更为信任，进一步可能达成“免杀”的效果。
  3. 方便黑客调试你的程序，找到其他的安全漏洞以便影响最终用户。

##### 如何防御

如果程序不带数字签名，那也不必花心思来防范这种攻击了，投入产出不成正比。

使用 CEF 和 QtWebKit 的可以在加载每一个HTML之前通过已经签名、且含有校验信息的DLL对其进行校验。

使用 nwjs 的话，因为它的HTML代码是通过 zip 压缩后直接通过`copy /b`附加到程序后部的，所以理论上直接打数字签名即可解决。而
Electron 我并没有找到特别好的方法，可以关注：<https://github.com/electron/electron/pull/9648>

#### RCE！

然后，就是 RCE(Remote Code Execution，任意代码执行) 了。我们可以进行 MITM 攻击，或者是利用 XSS 漏洞，还可以利用
Flash 的安全漏洞。针对 Web App 这一形式，如果其使用了`<iframe>`或`<webview>`我们甚至还可以进行所谓的“任意地址浏览”。

我们姑且不考虑利用浏览器内核本身的漏洞进行攻击的手段。这类漏洞本身数量稀少，而且相当多还需要浏览器其它组件的支持，仅有一个内核也没多大用途。况且这部分通常可以通过浏览器本身的安全通告发现，及时更新即可解决。在这之外，你可能没想到的是，MITM
和 XSS 会是最后的主角。这两种攻击方式一种难度大 + 面对客户端没什么用，一种拿个 Cookie 之后就没什么用了。但我们的战场可是 Web
客户端。如果我们的网页是通过明文 HTTP 协议传输的，便可以通过 MITM 让客户端处理任意代码。如果无法利用 MITM ，那么可以试图寻找 XSS
漏洞来写入任意代码。而在浏览器之外的客户端程序执行任意代码，可能是致命的。

现在有不少客户端的 Web 页面是通过 HTTP 协议从互联网上拉取的，不存储在本地。比如说
Steam。还有一部分客户端采取部分本地代码、部分加载远程网页的形式。反正大家都是浏览器嘛，看看迅雷9，那就真的把自己当成浏览器来处理了。——但无论是
Electron 还是 Cordova，实际上都并不设计为浏览器，因此直接使用它们便会产生相应的安全隐患。使用 CEF、QtWebKit
等，也在一定情况下存在安全问题。

通过 XSS 等手段想办法得到执行任意代码的权限后，我们看看怎么逃离这个客户端吧。

##### 通用攻击手段

首先是 Electron 和 Nwjs。这两个框架的 JavaScript 代码几乎拥有和 C++ 代码同等的权限，于是我们直接一行代码弹个计算器。

    
    
    require('child_process').execSync('c:\\windows\\system32\\calc.exe')

除去 XSS 之外，如果一个 Electron
同时负担了浏览器访问网页的职能，在没做安全配置的情况下照样可以一行代码弹个计算器。即使正确配置了`nodeIntegration`恐怕也无济于事，今年的
BlackHat 大会发布了这么一篇文章，即是讲述如何绕过该功能实现 RCE
的（`CVE-2017-12581`）：<https://www.blackhat.com/docs/us-17/thursday/us-17-Carettoni-Electronegativity-A-Study-Of-Electron-Security.pdf>

其次是国内 DCloud 出的 5+Runtime（<https://dcloud.io/runtime.html>
），自带`Native.js`（<https://ask.dcloud.net.cn/docs/#//ask.dcloud.net.cn/article/88>
），对其进行攻击效果也拔群。

而未正确配置的 CEF 和 QtWebKit，往往也可以造成任意代码执行。一个典型的例子，目前在网络上流传的在 CEF 里启用 Flash PPAPI
插件的代码，几乎无一例外关闭了`web_security`，同时打开了`no_sandbox`。很多开发者为了自己读写本地资源方便，也都关闭了它，如图。

![](https://images.seebug.org/content/images/2017/11/91a6724e-e778-441c-bfcd-6de0bdd094c7.png-w331s)

在低版本的 CEF 中，如果关闭了 `web_security`，只需要一行代码即可打开计算器（在默认浏览器被设置成 IE 的情况下）

    
    
    window.open('file://c:/windows/system32/calc.exe')

而在高版本的 CEF
中，无法打开计算器了。出于不知道什么原因，也无法读写文件（<https://bugs.chromium.org/p/chromium/issues/detail?id=40787>
，可以确认的是 QtWebKit 也不行），就不能使用通用的方案处理了。

——但别忘了 Flash 的存在。我们可以想办法看看这个程序有没有加载 Flash。

针对使用多进程的 CEF，直接看启动参数即可。

![](https://images.seebug.org/content/images/2017/11/e463b405-fbd2-49d0-bf3e-c6531ec7ab5a.png-w331s)

单进程的程序，就需要打开一个带有 Flash 的页面后，观察其 DLL 加载情况。或者直接开 IDA 逆向一波。

![](https://images.seebug.org/content/images/2017/11/350f19fe-c285-483f-8818-823c05973679.png-w331s)

拿到 Flash 版本后，查查该版本 Flash 有啥 Bug，一波带走即可。

至于MSHTML？感谢 COM 组件。

    
    
    (new ActiveXObject('WScript.Shell')).Run('calc.exe');

##### 定制攻击手段

通用的攻击手段实在不多，如果多的话，像 QQ 和微信早就被日穿了。所以，我们需要针对每个应用寻找有效的攻击代码。

以 Cordova 为例。`cordova-plugin-inappbrowser`基本上是大家都必装的插件。于是，我们调用系统浏览器，利用 URI
Scheme 弹个B站客户端先。

    
    
    window.open('bilibili://bangumi/season/6463', '_system')

想读通讯录？看看有没有`navigator.contacts`；读写文件？看看`window.requestFileSystem`。

从上面的例子可以发现，我们的重点就是，

  1. 找到 Native 代码与网页的通讯方式。
  2. 确认 Native 暴露了哪一些 API 给网页。

那具体应该怎么找呢？

首先先试试能不能打开浏览器开发者工具。针对 Android App，可以通过 Chrome 浏览器进行远程调试。大部分使用了 WebView 的 App
发布后都没有关闭远程调试这一功能，这为我们的攻击带来了极大的方便。

随手打开一个B站客户端看看

![](https://images.seebug.org/content/images/2017/11/6e235b0b-606e-4bf2-9437-f730bf7c044d.png-w331s)

如果能打开开发者工具，那要找特殊 API 就非常容易了；不能打开，也不是没有办法。

    
    
    document.write(Object.keys(window).join('\n'))

通过这种方法可以把 window 下的键值全部输出到屏幕上，下一步一步一步慢慢找。一般来说，浏览器可以调用的特殊 API
在`window`、`navigator`、`external`三个位置上都可以找到。找到可以利用的函数后，可以接着全文搜索函数名查找引用，模仿着直接调用即可。可以利用的功能包括“打开文件”（在
Windows
下一般使用`ShellExecute`实现，因`.exe`、`.scr`的文件关联为其自身，故可打开任意程序）、“打开程序”、“打开子窗口”等。

如果找不到可以利用的函数，或者在直接调用时做了一定程度上的过滤，则应当去找任意一个函数的源码，研究其如何与 Native 交互。

可以用

    
    
    document.write(someFunction.toString())

把函数源码输出到屏幕上（有开发者工具直接进 Source 看就好了）。

接着，我们需要配合逆向服用。

如果其显示的是`[native code]`，说明这是一个直接暴露给 JavaScript 的 API。对于 Android App 的
WebView，可以直接逆向为 .jar 后搜索`addJavaScriptInterface`函数，看到浏览器到底给 JavaScript
暴露了哪些东西。对于 CEF 等框架，可以从 Strings 搜索关键词直接一步一步 X 上去找到最终执行的函数，或者直接附加进程调试。

如果其显示的是 JavaScript 代码，则可一步一步跟踪上去直到顶层，看他的通信方式。目前比较流行的通信方式是自定义 URL Scheme
方式。其原理如下：

  1. JavaScript 通过 iframe 或者 `location.href` 尝试打开地址`my-custom-scheme://my-custom-data`
  2. 当检测到打开新地址时，Android WebView会触发`shouldOverrideUrlLoading`函数，由其来决定该地址应当如何处理；CEF 如果之前使用`CefRegisterSchemeHandlerFactory`注册过自定义 Scheme，则会交由其处理。
  3. 处理过程通常是异步的，并且地址切换后无法直接告知 JavaScript。所以，处理完成后，Native 代码通过`evaluateJavaScript`或者直接让框架访问`javascript:xxxxxxx`调用某个页面内的回调函数，完成通信。

所以对 Android 进行攻击的话，寻找那几个函数即可查到所有通讯方式。另外 Android 通常还会使用一些库包装 Scheme
处理，也不妨找找它们的特征，如：<https://github.com/lzyzsd/jsbridge>

##### 能攻击*Native吗？

React Native如果使用了`<webview>`也会受到相应的影响。但如果没有的话一般不用考虑，除非代码中存在`eval`等可能任意执行
JavaScript 的地方。对 NativeScript 这种可任意调用 Java 库的库，还是存在一定危险性的。

举一个比较有趣的知识+例子。在 IE8 之前，前端处理 JSON 通常使用以下代码：

    
    
    var json = eval('(' + data + ')')

当然现在的前端都已经用上了`JSON.parse`了，不过说不定有人坚持使用呢 :)

##### 如何防御

1.使用 HTTPS，在有条件的情况下校验证书，避免中间人攻击。

2.写入和输出数据时做好过滤，不信任所有的用户提交的数据。项目最初选型时就应该使用 React、Vuejs 等前端框架，避免自行拼接 HTML 出现问题。

3.在正式发布的软件上，关闭 WebView 的调试模式，Android 上：

    
    
    WebView.setWebContentsDebuggingEnabled(false);

4.对 Native 和 JavaScript 交互的代码进行白名单处理，当检测到域名非白名单域名时，拒绝 JavaScript 调用接口的请求。

5.在条件允许的情况下开启浏览器沙箱，同时杜绝`disable-web-security`行为，使用单个功能的命令行参数解决。

6.必须配置好CSP，预防真的出现 XSS 后的进一步利用。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/465/>

