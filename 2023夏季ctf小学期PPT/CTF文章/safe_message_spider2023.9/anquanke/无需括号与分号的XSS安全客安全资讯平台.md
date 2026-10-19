# 无需括号与分号的XSS

阅读量 **246226**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-05-20 11:01:47

 **x**

##### 译文声明

本文是翻译文章，文章原作者 portswigger，文章来源：portswigger.net

原文地址：<https://portswigger.net/blog/xss-without-parentheses-and-semi-colons>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01cfda804919193376.png)

几年前，我发现了一种技术，它可以使用`onerror`和`throw`语句，在JavaScript中调用函数而无需括号。它的工作原理是将`onerror`处理程序设置为您要调用的函数，并使用`throw`语句将参数传递给函数：

    
    
    <script>onerror=alert;throw 1337</script>
    

在每次JavaScript出现异常时都会调用`onerror`处理程序，然后`throw`语句允许您创建一个自定义异常，该异常包含一个发送到`onerror`处理程序的表达式。因为`throw`是一个语句，所以通常需要在`onerror`赋值后加上一个分号以开始一个新的语句，而不是形成一个表达式。

我曾遇到过一个过滤括号和分号的网站，我认为它肯定能够使用这种技术来执行一个没有分号的函数。第一种方法非常简单：您可以使用大括号来形成一个块语句，在这个语句中您有一个`onerror`可赋值。在块语句之后，您可以使用不带分号（或新的行内）的`throw`：

    
    
    <script>{onerror=alert}throw 1337</script>
    

块语句很好，但我想要一个更好的选择。有趣的是，因为`throw`语句接受一个表达式，所以你可以在`throw`语句中执行`onerror`赋值，并且因为表达式的最后一部分被发送到`onerror`处理程序，所以将使用所选参数调用该函数。以下是它的工作原理：

![](https://p4.ssl.qhimg.com/t01280760dfef4b9b2c.png)

    
    
    <script>throw onerror=alert,'some string',123,'haha'</script>
    

如果您已尝试运行代码，你将会注意到Chrome使用”Uncaught”作为将发送到异常处理程序字符串的前缀。

![](https://p4.ssl.qhimg.com/t01da0dc7425ba4c020.png)

在我之前的博客文章中，我展示了如何使用eval作为异常处理程序并执行字符串。我们来回顾一下，你可以在字符串前加上一个`=`，然后将’Uncaught’字符串变成一个变量并执行任意JavaScript。例如：

    
    
    <script>{onerror=eval}throw'=alertx281337x29'</script>
    

发送到eval的字符串是”Uncaught=alert(1337)”。这在Chrome上工作正常，但在Firefox上，异常会以两个字符串”uncaught
exception”作为前缀，这当然会在执行时导致语法错误。我开始寻找方法。

值得注意的是，当我在控制台执行`throw`时，`onerror/throw`的技巧并不能奏效。这是因为当throw在控制台中执行语句时，结果将发送到控制台而不是异常处理程序。

当你使用Error函数在Firefox中创建异常处理时，它将不会包含前缀”uncaught exception”，而只会回显字符串”Error”：

    
    
    throw new Error("My message")//Error: My message
    

我显然无法直接调用Error函数，因为它需要括号，但我想如果我使用带有Error原型的对象也许能达到一样的效果。但是这并不起作用 –
Firefox仍然使用相同的字符串作为前缀。然后我使用Hackability
Inspector检查Error对象以查看它具有的属性。我将所有属性添加到对象中，终于它奏效了！然后我一个接一个地删除属性，直到找到了所需的最小属性集：

    
    
    <script>{onerror=eval}throw{lineNumber:1,columnNumber:1,fileName:1,message:'alertx281x29'}</script>
    

您也可以使用fileName属性在Firefox上发送第二个参数：

    
    
    <script>{onerror=prompt}throw{lineNumber:1,columnNumber:1,fileName:'second argument',message:'first argument'}</script>
    

当我在Twitter上发布了这个技巧后，[@terjanq](https://github.com/terjanq
"@terjanq")和[@cgvwzq](https://github.com/cgvwzq "@cgvwzq")（Pepe
Vila）紧接着发布了一些很酷的操作，例如[@terjanq](https://github.com/terjanq
"@terjanq")删除所有字符串文字：

    
    
    <script>throw/a/,Uncaught=1,g=alert,a=URL+0,onerror=eval,/1/g+a[12]+[1337]+a[13]</script>
    

除此之外，通过使用类型错误将字符串发送到异常处理程序，Pepe完全删除了对throw语句的需要。

    
    
    <script>TypeError.prototype.name ='=/',0[onerror=eval]['/-alert(1)//']</script>
    

本文翻译自portswigger.net [原文链接](https://portswigger.net/blog/xss-without-parentheses-and-semi-colons)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Caramel** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/178610](/post/id/178610)

安全客 - 有思想的安全新媒体

本文转载自: [portswigger.net](https://portswigger.net/blog/xss-without-parentheses-and-semi-colons)

如若转载,请注明出处： <https://portswigger.net/blog/xss-without-parentheses-and-semi-colons>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [xss](/tag/xss)

 **+1** __16赞

 __收藏

![](https://p3.ssl.qhimg.com/t016101b17afc84f2ec.png) Caramel

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

