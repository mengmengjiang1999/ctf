**作者：天融信阿尔法实验室  
公众号：<https://mp.weixin.qq.com/s/ezs56qtTEzFUQKDW1a0_XQ>**

### 一、前言

最近爆出了IE浏览器和Edge浏览器跨域获取敏感信息的漏洞（绕过同源策略），不过并未被微软承认，于是进行了一系列深度测试，看看此漏洞是否真实严重。

### 二、知识扩展

为了大家能够更流畅地理解测试流程，我们先来了解下什么是同源策略和跨域。

**1\. 同源策略**

同源策略（SOP）是在现代浏览器中实现的安全功能，它限制从一个源加载的Web页面或脚本与来自另一个源的资源交互，从而防止不相关的站点相互干扰。也就是说，不同源的客户端脚本在没有明确授权的情况下，是不能读写对方资源的。

所谓同源就是指域名、协议、端口都相同，URL由协议、域名、端口和路径组成，如果两个URL的协议、域名和端口相同，则表示他们同源。相反，只要协议，域名，端口有任何一个的不同，就被当作是跨域。

下表是相对于 http://www.topsec.com.cn/admin/index.html 的同源检测结果：

![img](https://images.seebug.org/content/images/2019/04/04/1554369274000-433ab010e9fbcc13d88b3673c811f1ef.png-w331s)

**2．跨域**

跨域是指从一个域的网页去请求另一个域的资源，比如从http://www.a.com去请求http://www.b.com的资源，但一般情况下是不允许进行跨域的。因为前面我们说过，浏览器受同源策略的影响，不是同源的脚本不能操作其他源下面的对象，而如果想要操作另一个源下的对象时就需要授权了。

**3.浏览器为什么一定要有同源策略呢？**

其实这样做的目的主要就是为了用户的上网安全。我们可以试想一下，如果没有同源策略的情况。比如一个恶意网站的页面通过iframe嵌入了银行的登录页面（二者不同源），在用户登录银行的时候恶意网页上的javascript脚本就可以获取其用户名和密码。因此，有了同源策略，我们才能更安全的上网。

### 三、测试流程

本次测试，我是通过在本地搭建环境重新复现了漏洞并多番修改poc进行了不同的测试。

先来测试下IE浏览器

192.168.8.23/test.html 这里有一处重定向

![img](https://images.seebug.org/content/images/2019/04/04/1554369275000-923ce4c60f5997c733d5a75591f5263c.png-w331s)

Main.html

主要poc ，这里是漏洞触发的对象performance.
getEntriesByType，在Edge浏览器中是performance.getEntries，下面会有详细介绍

    
    
    setTimeout(function(){alert(performance. getEntriesByType (“resource”)[0].name)},4000);

![img](https://images.seebug.org/content/images/2019/04/04/1554369275000-1ba72849f3000ed08a1f94098391c083.png-w331s)

这里有一处回跳history.html，这个回跳的作用是返回重新刷新页面，不然只能获取预先设定好的url。

![img](https://images.seebug.org/content/images/2019/04/04/1554369275000-7f23b3752f56180db662d6c33887b1ac.png-w331s)

请求main.html，可以看到弹出了我们预先设定好的url

![img](https://images.seebug.org/content/images/2019/04/04/1554369275000-b06fad29750f6cef2c83bdac605112cf.png-w331s)

此时，上图中的弹出的URL不等同于192.168.6.23
这个源，这表明我们已经成功绕过浏览器中的同源策略并访问了应该受限制的资源。但是，这有什么用？因为我们只是能获取到预先设定的url，并没有特别有用的信息，比如username，password等。别着急，我们继续看。

此时通过history.html重新刷新页面，也就是htstory.back()返回一步，这里接下来会重新跳转回blog.tepsec.com.cn/?s=php这个页面，然后我们点击Search进行搜索，在搜索框中输入topsec，现在让我们看下效果：

![img](https://images.seebug.org/content/images/2019/04/04/1554369275000-46b67667baa3d59a3729db40fefa0bc2.png-w331s)

可以看到成功获取到了用户输入的信息topsec，实现了跨域获取敏感信息的功能。所以，现在我们可以得出个结论，当用户在与网页交互时，我们可以利用此漏洞来获取交互时的URL信息，试想一下，如果用户的敏感信息在url中的话，比如某网站的登陆账号密码和url做了关联http://foo.com/username=admin&password=admin,或者其他敏感信息，那么危害就非常大了。

同时不仅仅是输入，点击其他页面时也可以抓到整个url信息。

![img](https://images.seebug.org/content/images/2019/04/04/1554369275000-adee81fd255e639132e94976dbce5966.png-w331s)

下面再测试下Edge浏览器

192.168.8.23/test.html还是这个没有变

![img](https://images.seebug.org/content/images/2019/04/04/1554369276000-8ifdvn.png-w331s)

Main.html

这里修改的地方有两处，一处是getEntriesByType变成getEntries，另一处角标由[0]变成了[2]

    
    
    setTimeout(function(){alert(performance. getEntries(“resource”)[2].name)},4000);

![img](https://images.seebug.org/content/images/2019/04/04/1554369276000-e1ce3a175536b49675a417a4b8e0e312.png-w331s)

同样有回跳跳转history.html（history.back）。

访问main.html，可以看到和IE浏览其一样同样弹出了我们预先设定好的url。

![img](https://images.seebug.org/content/images/2019/04/04/1554369276000-572e1248e1e2f5b88414ea208373b044.png-w331s)

但是和IE不同的是这里并不能动态获取用户修改的url，也就是用户输入信息还是点击都无法获取用户更改后的url信息，始终是弹出下面的url，所以暂时判断在Edge浏览器下此漏洞并没有什么危害
。

最后，我们再来看看关键的performance.getEntries这个api有哪些属性，从下图可以看到有四个属性，目前能被用上的就是url信息也就是name属性。

![img](https://images.seebug.org/content/images/2019/04/04/1554369276000-d9138bb0bd1eaf0ce26cb3b0922affb4.png-w331s)

    
    
    ‘url’: perf.name,
    
    ‘entryType’: perf.entryType,
    
    ‘type’: perf.initiatorType,
    
    ‘duration(ms)’: perf.duration

这里修改下name变成 duration，弹出了个时间并没啥用处

![img](https://images.seebug.org/content/images/2019/04/04/1554369276000-d15c3c13dd8218fcdc3c3f00bda19830.png-w331s)

也就是说这个漏洞获取到的name属性也就是url还有些利用价值，像类型和时间基本没什么利用价值。

### 四、漏洞利用

在实际利用过程中，攻击者不会像上述一样将信息弹出来显示给受害者，只会悄悄地将信息窃取。

我们简单修改下POC，模拟一下真实环境下的漏洞利用。

Main.html

![img](https://images.seebug.org/content/images/2019/04/04/1554369276000-98ad773d1a414df5f1e2fb7c0534ab6f.png-w331s)

首先将页面高宽进行调整使其看起来真实一些，而不仅仅是那一小块，然后将alert弹出信息的方式改为通过访问cookie.php将信息发送至攻击者服务器。

cookie.php

![img](https://images.seebug.org/content/images/2019/04/04/1554369276000-e9ab703d71faa12b80878534d1a63d58.png-w331s)

现在来访问下Main.html

![img](https://images.seebug.org/content/images/2019/04/04/1554369276000-38fdf94f4cb550a7684d62ebcc3bee2f.png-w331s)

打开页面后进行随意搜索或点击，然后来看192.168.8.23服务器下的log.txt文件

![img](https://images.seebug.org/content/images/2019/04/04/1554369276000-db93f9a6631230b74f0fa98f0344eac2.png-w331s)

URL信息都发送到了攻击者的服务器下。

### 五、结语

从测试情况来看，漏洞危害性还是很大的，好在这个刷新的功能会被用户所察觉.所以还是在补丁未修补之前，不要使用IE和Edge浏览器浏览网页和点击不明链接。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/883/>

