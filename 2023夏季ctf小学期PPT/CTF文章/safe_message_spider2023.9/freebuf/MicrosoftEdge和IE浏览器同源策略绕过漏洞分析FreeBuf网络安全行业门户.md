***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、前言  

**最近爆出了IE浏览器和Edge浏览器跨域获取敏感信息的漏洞（绕过同源策略），不过并未被微软承认，于是天融信阿尔法实验室进行了一系列深度测试，看看此漏洞是否真实严重。**

## 二、知识扩展

为了大家能够更流畅地理解测试流程，我们先来了解下什么是同源策略和跨域。

###  **1.同源策略**

同源策略（SOP）是在现代浏览器中实现的安全功能，它限制从一个源加载的Web页面或脚本与来自另一个源的资源交互，从而防止不相关的站点相互干扰。也就是说，不同源的客户端脚本在没有明确授权的情况下，是不能读写对方资源的。

所谓同源就是指域名、协议、端口都相同，URL由协议、域名、端口和路径组成，如果两个URL的协议、域名和端口相同，则表示他们同源。相反，只要协议，域名，端口有任何一个的不同，就被当作是跨域。

下表是相对于<http://www.topsec.com.cn/admin/index.html>的同源检测结果：

![image.png](https://image.3001.net/images/20190404/1554367102_5ca5c27e1f54f.png!small)

###  **2.跨域**

跨域是指从一个域的网页去请求另一个域的资源，比如从<http://www.a.com>去请求<http://www.b.com>的资源，但一般情况下是不允许进行跨域的。因为前面我们说过，浏览器受同源策略的影响，不是同源的脚本不能操作其他源下面的对象，而如果想要操作另一个源下的对象时就需要授权了。

###  **3.浏览器为什么一定要有同源策略呢？**

其实这样做的目的主要就是为了用户的上网安全。我们可以试想一下，如果没有同源策略的情况。比如一个恶意网站的页面通过iframe嵌入了银行的登录页面（二者不同源），在用户登录银行的时候恶意网页上的javascript脚本就可以获取其用户名和密码。因此，有了同源策略，我们才能更安全的上网。

## 三、测试流程

本次测试，我是通过在本地搭建环境重新复现了漏洞并多番修改poc进行了不同的测试。

先来测试下IE浏览器。

192.168.8.23/test.html这里有一处重定向：

![image.png](https://image.3001.net/images/20190404/1554367113_5ca5c289693fc.png!small)

Main.html

主要poc，这里是漏洞触发的对象performance.
getEntriesByType，在Edge浏览器中是performance.getEntries，下面会有详细介绍：

    
    
    setTimeout(function(){alert(performance. getEntriesByType ("resource")[0].name)},4000);

![image.png](https://image.3001.net/images/20190404/1554367121_5ca5c291e18fa.png!small)
这里有一处回跳history.html，这个回跳的作用是返回重新刷新页面，不然只能获取预先设定好的url。

![image.png](https://image.3001.net/images/20190404/1554367131_5ca5c29ba6787.png!small)

请求main.html，可以看到弹出了我们预先设定好的url：

![image.png](https://image.3001.net/images/20190404/1554367225_5ca5c2f936ee7.png!small)

此时，上图中的弹出的URL不等同于192.168.6.23
这个源，这表明我们已经成功绕过浏览器中的同源策略并访问了应该受限制的资源。但是，这有什么用？因为我们只是能获取到预先设定的url，并没有特别有用的信息，比如username，password等。别着急，我们继续看。

此时通过history.html重新刷新页面，也就是htstory.back()返回一步，这里接下来会重新跳转回blog.tepsec.com.cn/?s=php这个页面，然后我们点击Search进行搜索，在搜索框中输入topsec，现在让我们看下效果：

![image.png](https://image.3001.net/images/20190404/1554367250_5ca5c312462f0.png!small)

可以看到成功获取到了用户输入的信息topsec，实现了跨域获取敏感信息的功能。所以，现在我们可以得出个结论，当用户在与网页交互时，我们可以利用此漏洞来获取交互时的URL信息，试想一下，如果用户的敏感信息在url中的话，比如某网站的登陆账号密码和url做了关联[http://foo.com/username=admin&password=admin](http://foo.com/username=admin&password=admin)，或者其他敏感信息，那么危害就非常大了。

同时不仅仅是输入，点击其他页面时也可以抓到整个url信息：

![image.png](https://image.3001.net/images/20190404/1554367264_5ca5c320ba4e1.png!small)

下面再测试下Edge浏览器。

192.168.8.23/test.html还是这个没有变：

![image.png](https://image.3001.net/images/20190404/1554367270_5ca5c326bf2ba.png!small)

Main.html

这里修改的地方有两处，一处是getEntriesByType变成getEntries，另一处角标由[0]变成了[2]：

    
    
    setTimeout(function(){alert(performance. getEntries("resource")[2].name)},4000);

![image.png](https://image.3001.net/images/20190404/1554367278_5ca5c32e2a2f9.png!small)

同样有回跳跳转history.html（history.back）。

访问main.html，可以看到和IE浏览其一样同样弹出了我们预先设定好的url。

![image.png](https://image.3001.net/images/20190404/1554367285_5ca5c3356d70f.png!small)

但是和IE不同的是这里并不能动态获取用户修改的url，也就是用户输入信息还是点击都无法获取用户更改后的url信息，始终是弹出下面的url，所以暂时判断在Edge浏览器下此漏洞并没有什么危害
。

最后，我们再来看看关键的performance.getEntries这个api有哪些属性，从下图可以看到有四个属性，目前能被用上的就是url信息也就是name属性。

![image.png](https://image.3001.net/images/20190404/1554367294_5ca5c33ed2d1d.png!small)

    
    
           'url': perf.name, 
    
             'entryType': perf.entryType,
    
              'type': perf.initiatorType,
    
             'duration(ms)': perf.duration

这里修改下name变成duration，弹出了个时间并没啥用处：

![image.png](https://image.3001.net/images/20190404/1554367305_5ca5c3493cd7f.png!small)

也就是说这个漏洞获取到的name属性也就是url还有些利用价值，像类型和时间基本没什么利用价值。

## 四、漏洞利用

在实际利用过程中，攻击者不会像上述一样将信息弹出来显示给受害者，只会悄悄地将信息窃取。

我们简单修改下POC，模拟一下真实环境下的漏洞利用。

![image.png](https://image.3001.net/images/20190404/1554367313_5ca5c3518992b.png!small)Main.html

首先将页面高宽进行调整使其看起来真实一些，而不仅仅是那一小块，然后将alert弹出信息的方式改为通过访问cookie.php将信息发送至攻击者服务器。

![image.png](https://image.3001.net/images/20190404/1554367319_5ca5c357d8a1f.png!small)
cookie.php

现在来访问下Main.html：

![image.png](https://image.3001.net/images/20190404/1554367324_5ca5c35cd6185.png!small)

打开页面后进行随意搜索或点击，然后来看192.168.8.23服务器下的log.txt文件：

![image.png](https://image.3001.net/images/20190404/1554367331_5ca5c3634984a.png!small)

URL信息都发送到了攻击者的服务器下。

## 五、结语

从测试情况来看，漏洞危害性还是很大的，好在这个刷新的功能会被用户所察觉。所以还是在补丁未修补之前，不要使用IE和Edge浏览器浏览网页和点击不明链接。

***本文作者：alphalab，转载请注明来自FreeBuf.COM**

