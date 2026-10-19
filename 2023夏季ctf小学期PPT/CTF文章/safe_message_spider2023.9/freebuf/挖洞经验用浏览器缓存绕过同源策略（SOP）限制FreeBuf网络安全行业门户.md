![](https://image.3001.net/images/20200106/1578302735_5e12fd0f821db.png!small)

**本文分享的Writeup是作者在做Keybase.io的漏洞众测中发现的SOP（同源策略）绕过漏洞，由于Keybase.io在用的多个API端点都启用了CORS（跨域资源共享）机制，这种缓解同源策略的机制某种程度上克服了同源策略的严格限制，可以让不同域服务器间实现交互请求。而作者在测试中发现了Keybase的CORS策略错误配置，利用这种缺陷，可以操纵浏览器缓存获取用户敏感数据信息。一起来看看。**

> Keybase 是一个开源的跨平台即时通讯工具，在 PC 设备上支持 macOS、Linux 和 Windows 平台，并提供
> Chrome/Firefox 浏览器扩展。此外还提供 iOS 和 Android 版本。和众多 IM 工具相比，Keybase
> 最吸引人的地方在于免费使用且不会受到任何广告骚扰，最重要的是它还是一个开源项目。

在安全性和隐私方面，Keybase 采用了端到端的加密方式，承诺会为每个用户的群组、文件和聊天等数据提供安全保护。如果这些数据上传到云中，也会进行加密处理。

##  漏洞前言

Keybase在当前用户向其他用户发送加密消息时，可以让当前用户通过一个API接口去查找其他Keybase用户，在该接口中提供了加密发送消息时所需的，如公钥等其他Keybase用户公共信息。这听起来貌似是安全的，是吧？

该API接口的CORS（跨域资源共享）策略配置如下：

> Access-Control-Allow-Origin: *
>
> Access-Control-Allow-Methods: GET
>
> Access-Control-Allow-Headers: Content-Type, Authorization, Content-Length,
> X-Requested-With
>
> Access-Control-Allow-Credentials: false

在了解这个CORS配置问题之前，我们先来厘清几个重要的知识点：

> 1、Access-Control-Allow-Origin中的星号“*”说明，任意外部域名都能与该API进行交互，执行跨域的请求调用；
>
> 2、Access-Control-Allow-Credentials中的“false”说明，
> 这里可能出于安全考虑，服务器不允许用户在跨域请求中包含代表身份信息的Cookie。此处Access-Control-Allow-> Headers暴露的用户认证头信息和接下来要讲的漏洞关系不大，因为在查询上述API接口中用不到。

##  漏洞情况

自然地，由于上述那个可查询的API接口是公共的，所以在进行跨域请求时无需携带防御CSRF（跨站请求伪造）的token信息，因为用户在使用Keybase.io时是经过身份验证的，且他的会话信息存储在了Cookie中，只有一些非常敏感的API接口会要求在请求头中携带用户认证头token。

后来我发现，如果在消息加密验证和发送环节，用上述那个查找其他Keybase用户的API来查找我自己，哪怕输入我名字中的一个字母，搜索结果中就会匹配到我的一些账户信息，其中竟然包含了我的一些敏感信息，如：

> 邮箱地址
>
> 我使用和剩余的邀请码数量
>
> 计费信息
>
> 上一次登录的时间戳、邮件形式的时间/日期验证码
>
> TripleDes加密的PGP私钥

但是，我并没有私钥存储在Keybase上啊，之后我才了解到这是Keybase的在2015到2016年的一个遗留功能，现在已经不再实施。

经测试，一旦我在上述API请求中Cookie信息被删除，我的个人敏感信息也不会再返回显示。但是，我在服务端对该API的响应消息中发现了一个名为 ‘Etag’
的消息头，这是一个浏览器缓存标记头，代表客户端请求资源未发生变化，那么浏览器就可以从用户的缓存内容中去取出然后响应给用户。

##  Payload与漏洞利用

我想起Twitter用户@Bitk_[曾用过一个技巧](https://blog.bi.tk/chrome-cors/)，那就是用javascript的fetch API方法去强制从浏览器缓存中直接发起一个跨域请求，而恰巧 Keybase
在这里未曾对服务端响应头部署过任何缓存控制头（Cache-Control）措施，于是，我就在本地构造了如下的Payload

    
    
    <html>
    
        <script>  
    
        var url = "<https://keybase.io/_/api/1.0/user/lookup.json?username=>{YOUR_USERNAME}";  
    
        fetch(url, {    
    
            method: 'GET',    
    
            cache: 'force-cache'
    
            });
    
        </script>
    
        </html>

如果上述Payload请求能成功执行，可能就会返回响应一些Keybase的缓存信息，基于此，我执行了一个身份验证请求，最终有效地返回了与我账户相关的一些个人敏感信息。如下：

![](https://image.3001.net/images/20200106/1578302625_5e12fca15d18b.png!small)

为了确认Payload是否被成功执行，从下图的浏览器请求信息中可以看到，fetch方法直接从浏览器缓存中读取了我的身份信息。

![](https://image.3001.net/images/20200106/1578302639_5e12fcaf40ace.png!small)

##  漏洞上报及处理进程

> 2019.12.19 漏洞初报
>
> 2019.12.19 两小时后，Keybase在响应消息中中加入了‘Cache-Control: no-store’
>
> 2019.12.24 Keybase奖励了$1,500 公布漏洞

***参考来源：[enumerated](https://enumerated.wordpress.com/2019/12/24/sop-bypass-via-browser-cache/)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

