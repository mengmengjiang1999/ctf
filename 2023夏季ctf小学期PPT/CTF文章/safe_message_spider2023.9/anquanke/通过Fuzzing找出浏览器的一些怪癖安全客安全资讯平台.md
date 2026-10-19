# 通过Fuzzing找出浏览器的一些怪癖

阅读量 **237198**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-05-31 11:00:20

 **x**

##### 译文声明

本文是翻译文章，文章原作者 portswigger，文章来源：portswigger.net

原文地址：<https://portswigger.net/blog/provoking-browser-quirks-with-behavioural-fuzzing>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t0172a38871c4689ce6.jpg)

在这篇文章中我将向你展示我如何通过Fuzzing找出Firefox浏览器的多个”怪癖”。一般来说，研究者Fuzzing的目的大多是找出引发内存损坏的行为，但我是个例外；我要找的是浏览器一些其他的有趣行为。例如某些字符可以引起标签发生异常（打开或闭合），或某些字符可以绕过JavaScript解析器作出某种行为。上述这些意外行为通常可以绕过安全策略和实现Javascript沙盒逃逸，从而有助于[XSS](https://portswigger.net/web-security/cross-site-scripting)攻击。

我想讨论的第一个Bug是关于如何通过其他的方式闭合HTML注释。如果你阅读过HTML规范，你应该知道可以使用`-->`或`--!`来闭合注释，但还有其他方法吗？这是一个好问题，很适合我们展开Fuzzing。我们只要准备一些代码就可以找出该问题的答案。

时间回到2008年，我在构造[Shazzer](http://shazzer.co.uk/)用于对浏览器进行模糊测试，那时我被限制每页只能导入10000个攻击向量，但回到2019一切都更快了，我们可以一次性对更多目标进行模糊测试。同时也可以使用DOM来加速Fuzzing，因为我不用再把向量逐个加载到当前文档中。但需要注意这不是万能的，你得到的结果可能不完整，实际我发现DOM在属性(例如`href`)赋值中允许NULL字符，但HTML解析器不会解析。这里还有一些其他很酷的bug，但你不能轻信浏览器的结果，你需要深入研究HTML解析器的行为。尽管这种输出HTML的方法比使用服务端语言快得多，但在大多数情况下都不适用。

第一步已经完成——我们找出问题”有什么字符可以闭合HTML注释？”。为了找出答案我们要利用已知可闭合HTML注释的字符，然后fuzz那些我们目前不知道的字符。下一步则是使用工具开展Fuzz，这里我使用的是[Hackvertor](https://hackvertor.co.uk/public)（也可以在本地web服务器搭建）。加载完Hackvertor，通常是向输入框中写入内容并使用特定标记做一些转换，对输出做某些操作后然后获取最终输出。但我们没有要转换的内容，因此我们直接导入内容到输出框中。点击输出框区域的按钮，创建数组存储字符，然后创建`div`元素开始测试HTML：

    
    
    log = [];
    div=document.createElement('div');
    

接下来我们要fuzz超过1000000个unicode字符（准确地说是`0x10ffff`）。所以先创建一个`for`循环：

    
    
    for(i=0;i<=0x10ffff;i++){
    

然后再使用`div`元素，这里我测试的是`!`之后的位置，所以字符要注入到`!`后面。然后使用一个`img`元素来查看结果是否有效，如果这个元素为显性则代表HTML注释已闭合。我们已经准备好了一些有趣的字符！

    
    
    div.innerHTML = '<!-- --!'+String.fromCodePoint(i)+'><img>-->';
    

使用`querySelector`检查`img`是否存在，然后将字符添加到日志，然后关闭`if`语句和`for`循环，最后把结果会显示在左侧的输入框中：

    
    
    if(div.querySelector('img')){
     log.push(i);
     }
    }
    input.value=log
    

这里有[完整的代码](https://hackvertor.co.uk/public#bG9nPVtdOwpkaXY9ZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgnZGl2Jyk7CmZvcihpPTA7aTw9MHgxMGZmZmY7aSsrKXsKIGRpdi5pbm5lckhUTUwgPSAnPCEtLSAtLSEnK1N0cmluZy5mcm9tQ29kZVBvaW50KGkpKyc+PGltZz4tLT4nOyAKaWYoZGl2LnF1ZXJ5U2VsZWN0b3IoJ2ltZycpKXsKIGxvZy5wdXNoKGkpOwogfQp9IAppbnB1dC52YWx1ZT1sb2c=)，你只需在Firefox中打开URL，然后把内容放到输出框，点击“Execute
JS”按钮开始字符fuzz。Fuzz完毕后你应该在输入框中可以看到数字，数字对应有效的字符代码。在撰写本文时Firefox（67版本）仍允许通过把换行字符`-n`和`r-`放到`!`后面来闭合注释。很快我就收到消息，告知该bug已修复。Fuzzing最后的阶段就是开始组装Payload，这很简单你只要用换行符替换字符代码，然后添加XSS
Payload：

    
    
    <!-- --!
    ><img src=1 onerror=alert(1)> -->
    

你可以再次使用Hackvertor来测试它是否有效，只需将上面的内容粘贴到输出框中，然后点击“Test HTML”引发弹窗。

![](https://p2.ssl.qhimg.com/t01828973fa8a6a2859.png)

这样我们就在Firefox
HTML解析器里找到了一个很cool的bug。OK，让我们继续找下一个，一个新问题：“什么字符可以作为注释开头？”。我们现在的目标是通过HTML注释打破存在的HTML属性，而不是闭合HTML注释。我相信大家都知道可以把`<!--`作为HTML注释的开头。OK，这里我会再次使用相同的代码，但会做一些小调整，我修改innerHTML的赋值，以检查注释的开头：

    
    
    div.innerHTML = '<!-'+String.fromCodePoint(i)+'- ><div title="--><img>">';
    

所以我们把Fuzzing的字符放到第一个连字符后面，如果某个字符可以用作注释开头，那将注释掉`div`元素，从而突破`title`属性。这次点击“Excute
JS”后，我们在Firefox上得到两个结果：“0 ,
45”。由于连字符，`45`是存在的，而`0`代表NULL字符！这意味着Firefox会将`<!-NULL-`视为注释开头。有点不可思议（我觉得浏览器服务商应该对产品做足够多的行为Fuzzing）。为完整这次测试，我们现在要创建攻击向量，将`String.fromCodePoint`函数替换为`NULL`字符，然后插入XSS
Payload：

    
    
    document.body.innerHTML = '<!-x00- ><div title="--><img src=1 onerror=alert(1)>"></div>';
    

让我们跳出HTML，转向JavaScript。我测试了大部分浏览器，Sorry，Mozilla的Firefox再次让我惊讶。我是从
@jinmo123的一篇推文获得灵感，他们使用一个很酷的ES6新特性来实现无括号调用函数，但结合Fuzzing来说我的问题是哪些字符可以放到`in`或者说`instanceof`运算符后面，我们仍需用到Hackvertor，遵循上面模版创建代码，但这次不需要DOM。我们先创建数组和for循环：

    
    
    log = [];
    for(i=0;i<=0x10ffff;i++){
    

然后我们将使用`eval`替换`innerHTML`进行Fuzzing。首先用一个`try catch`块来包围它，以捕获无效字符引发的异常。

    
    
    try{
    eval("/a/"+String.fromCodePoint(i)+"instanceof function(){}");
    

`eval`函数用来验证JavaScript是否有效，如果有效，程序将跳转到下一行，如果无效，它将抛出一个异常并且异常立马被捕获，然后Fuzz下一个字符。下面一行只记录成功字符，剩下的代码关闭`try
catch`块和`for`循环，最后把结果反馈至输入框。

    
    
    log.push(i);
    }catch(e){}
    }
    input.value=log
    

使用“Execute
JS”运行此代码，可以得到非常多结果！这是因为Firefox忽视了很多字符。但如果你在Chrome上运行，结果则会好一些。你可以在输入框结果中选择字符，这里我使用的是十六进制的“1114110”，也可以用hex编码的“0x10fffe”。现在我们组合最终的JavaScript向量：

    
    
    eval("1337"+String.fromCodePoint(1114110)+"in"+String.fromCodePoint(1114110)+"alert(1337)");
    

你也可以在SVG脚本中利用它：

    
    
    <svg><script>alert&#x10fffe(1)&#x10fffe</script></svg>
    

本文翻译自portswigger.net [原文链接](https://portswigger.net/blog/provoking-browser-quirks-with-behavioural-fuzzing)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **NullCoopX** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/179498](/post/id/179498)

安全客 - 有思想的安全新媒体

本文转载自: [portswigger.net](https://portswigger.net/blog/provoking-browser-quirks-with-behavioural-fuzzing)

如若转载,请注明出处： <https://portswigger.net/blog/provoking-browser-quirks-with-behavioural-fuzzing>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [浏览器](/tag/浏览器)
  * [Fuzz](/tag/Fuzz)

 **+1** __9赞

 __收藏

![](https://p4.ssl.qhimg.com/t0179f0dddab9c078ca.jpg) NullCoopX

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

