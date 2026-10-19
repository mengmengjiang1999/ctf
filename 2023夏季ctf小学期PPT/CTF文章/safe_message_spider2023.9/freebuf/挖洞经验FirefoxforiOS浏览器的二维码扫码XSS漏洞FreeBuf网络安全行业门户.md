**![](https://image.3001.net/images/20191228/1577509361_5e06e1f14abd6.png!small)****在手机中，我们通常访问一个网站的做法是打开浏览器在地址栏中输入网站地址，一般来说这样的方法有些烦人，所以，有些网站访问对象通常也会生成一个二维码图片，方便用户直接扫码访问，只要用户手机扫码就能跳转到目标访问网站，或是把相应信息显示在用户手机中。几乎我们所有人都会用手机的扫码功能，但是，你是否想过，如果你信任的应用APP其扫码功能出现安全错误，会发生什么情况？今天，我们就来谈谈Firefox
IOS v10浏览器中的扫码XSS漏洞。**

##  Firefox IOS浏览器说明

根据苹果应用商店的说明，Firefox IOS
v10中加入了更多新东西，极简的用户界面，可以隐藏多余显示图片，增加了一个二维码扫码功能，能突出显示浏览记录和最新资讯。

也就是说，从Firefox IOS v10开始，火狐手机浏览器加入了二维码扫码功能，其中使用了WebKit web
view组件来加载内容，其余的为SWIFT架构，包含在Firefox的漏洞众测范围之内。以下为Firefox IOS v10扫码访问网站的一个动图：

##  用javascript URI构造XSS

所以，这里如何来发现其扫码功能的漏洞呢？首先我想到的就是构造一个javascript
URI形式去替代二维码中的URL，看看扫码功能如何判断，是否会把它当成正常的文本，还是会当成javascript代码去执行。我们试试看。

在这里，我们用到了一个很好的二维码生成网站<https://www.the-qrcode-generator.com/>，在其中输入你的内容就能自动生成一个二维码。因此，我们输入以下javascript URI形式内容看看：

> javascript:fetch('/').then(res=>res.text()).then(data=>alert(data));
>
> javascript:alert(document.body.innerHTML);

以上这两个javascript
URI功能为获取用户之前最后在浏览器中浏览过的网站信息。所以，假设有这么一种情况，当前用户处于浏览google.com的状态，但他通过Firefox扫码想访问另一网站，那么，如果扫码的嵌入内容是我们上述的javascript
URI，那么当他一扫码就会跳出其访问google.com的一些相关信息来。试试，确实可以，具体如下：

所以，这样一来，既然能在这个点上完成javascript
代码执行，恶意攻击者也就能用它窃取用户cookie或其他相关信息了。这种攻击范围不仅只限于网站地址访问可以用它来实现多种攻击场景，如浏览器的阅读模式。

##  浏览器阅读模式下的XSS漏洞触发

阅读模式是浏览器提供给用户的一种极简阅读体验，在这种模式的加载过程中，浏览器会剔除掉一些不必要的代码、框架、其它嵌入元素的渲染以及广告的干扰。同样，我用之前生成的形式看看是否能在阅读模式下实现XSS，确实可以：

![](https://image.3001.net/images/20191228/1577508931_5e06e04322d89.gif!small)

其中在代码执行后会跳出[http://localhost:6571](http://localhost:6571/)，这是javascript的window.location.href的用法，可以构造成这样的跳转链接：

> <http://localhost:6571/reader-mode/page?url=https://wwww.anysite.com>

在最后加入任意网站URL就能配合其它漏洞进行利用，形成对用户信息的进一步威胁。

##  本地文件加载过程的XSS触发

可以用该漏洞来触发一些手机本地的文件加载，扫码后，就有加载本地文件，以file:///test.html为例：

![](https://image.3001.net/images/20191228/1577509016_5e06e0981e098.png!small)

##  内联页面加载过程的XSS触发

在伪协议internal://页面加载过程中形成XSS ，如：

![](https://image.3001.net/images/20191228/1577509054_5e06e0be3c28f.png!small)

##  CSP绕过

该漏洞同样可以用来绕过CSP限制，比如某个网站只限于访问来自它自身的内容，如以下代码场景：

    
    
    // test.php
    
        <?php
    
        header("Content-Security-Policy: default-src 'self'");
    
        if(isset($_GET['xss'])) {
    
            echo $_GET['xss'];
    
        }
    
        ?>

所以即使是这样的限制，我们构造的二维码javascript代码也可以无限制运行。

##  其它场景

还可以在页面选定文本的查找中，如果选定文本是javascript
URI形式，那么Firefox手机浏览器就会执行其中的js代码，但这种利用危害较小，只会显示一个错误加载框，但好在还可以用它来把用户导向其它恶意网站。

![](https://image.3001.net/images/20191228/1577509105_5e06e0f131b5f.png!small)

##  其它浏览器的该漏洞情况

除了Firefox，Opera mini for IOS也存在上述XSS漏洞，我们已经及时告知了Opera官方，但他们目前为止还未给出回应。

##  漏洞原因分析

从v10一直到v19版本，Firefox 都在地址栏中支持 javascript URI 调用，这样就存在上述XSS可能。

![](https://image.3001.net/images/20191228/1577509140_5e06e11460814.png!small)经上报给Firefox之后，他们及时从地址栏中删除了javascript
URI功能，漏洞也获得CVE-2019-17003的分配。![](https://image.3001.net/images/20191228/1577509164_5e06e12c10248.png!small)
***参考来源：[payatu](https://payatu.com/blog/nikhil-mittal/firefox-ios-qr-code-reader-xss-\(cve-2019-17003\))，clouds 编译整理，转载请注明来自 FreeBuf.COM**

  

