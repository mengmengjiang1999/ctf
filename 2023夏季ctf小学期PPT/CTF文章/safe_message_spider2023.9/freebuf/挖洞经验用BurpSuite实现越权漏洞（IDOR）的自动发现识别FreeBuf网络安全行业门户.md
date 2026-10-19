![](https://image.3001.net/images/20200116/1579177713_5e2056f1c073c.jpeg!small)

**这里分享一个自动化发现IDOR（越权）漏洞的方法，那就是在BurpSuite中利用Autozie和Autorepeater插件实现IDOR漏洞的探测识别，而无需针对每个请求手动去变化参数或请求。**

>
> IDOR（越权）漏洞：也称“不安全的直接对象引用”，场景发生于当用户对内部资源的访问请求，或基于用户提供的输入对象进行访问时，服务端未进行合理的权限验证，导致当前用户可以未经授权访问获取到不属于自己账户权限的资源或数据。

我们可以在BurpSuite的插件库Bapp中对Autorize 和 Autorepeater进行安装：

![](https://image.3001.net/images/20200116/1579177551_5e20564f8ee04.png!small)

## 用Autorize发现IDOR漏洞

先来看Autorize，对于客户端发送的任何请求来说，它会执行一个等效请求，只是其中的Cookies需要是其他用户的会话Cookie，或是加入其它授权验证头，如下我们假设两个用户：

> 用户A — 管理员
>
> 用户B — 普通用户

现在，我们用管理员（用户A）账户访问Web应用，然后在Autorize的请求配置中我们把用户B的会话Cookie加入，之后，请求将会以用户B的身份地起。配置如下：

![](https://image.3001.net/images/20200116/1579177578_5e20566adeb56.png!small)

对作用域过滤器中我们稍微做一些设置，以此能直观地显示出响应消息，避免收到大量无用结果。接下来，开启Autorize，对Web应用来说，表面上的访问客户端是用户A，但其实其中用的是用户B的会话Cookie：

![](https://image.3001.net/images/20200116/1579177596_5e20567c7d988.png!small)

可以看到，在这种情况下，原始长度（Original length）和修正长度（Modified
length）之间都没有任何差异，且响应回来的状态码都是200，因此，这样来看，Web服务端可能存在IDOR漏洞。当然，如果收到的状态码是403
Forbidden，那么说明就不存在IDOR漏洞，是不行的。

## 用Autorepeater发现IDOR漏洞

Autorepeater可以说是复杂版本的Autorize，它可以针对细化参数实现更加准确的测试，如通常涉及到的uuid,、suid、uid等用户参数。但是，它的设置有些麻烦，比如下面这种uuid的替换测试，需要手动设置：

![](https://image.3001.net/images/20200116/1579177640_5e2056a8e7669.png!small)

这种自动化的IDOR探测，在一些云应用中，不仅可针对内部租户，还能针对跨域租户进行安全功能审计。比如在下面这里的设置中，我们可以选择添加替换变量来实现请求主体的变化，另外，还可以对其它参数或请求进行修改，如：

> User = Admin
>
> False = True
>
> JSON = XML

![](https://image.3001.net/images/20200116/1579177669_5e2056c516955.png!small)

Autorize主页：<https://github.com/Quitten/Autorize>

AutoRepeater主页：<https://github.com/nccgroup/AutoRepeater>

具体应用可参考视频：

>
> https://[www.youtube.com/watch?v=3K1-a7dnA60&t=357s](http://www.youtube.com/watch?v=3K1-a7dnA60&t=357s)

 ***参考来源：[medium](https://medium.com/cyberverse/automating-burp-to-find-idors-2b3dbe9fa0b8)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

