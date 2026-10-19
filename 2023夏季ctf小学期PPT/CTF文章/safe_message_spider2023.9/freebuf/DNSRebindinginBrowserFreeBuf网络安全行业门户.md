在浏览器场景下的 DNS 重绑定攻击有什么不一样？

最近 Chrome 的正在推广（https://developer.chrome.com/blog/private-network-access-preflight/）的PNA(Private Network Access) ：https://wicg.github.io/private-network-access/策略真的能完全防御吗？

##  **DNS重绑定**

这里不过多介绍，不了解的师傅可以先看一下下面的文章：《从 0 到 1 认识 DNS
重绑定攻击》（[https://xz.aliyun.com/t/7495）](https://xz.aliyun.com/t/7495%EF%BC%89)

DNS 重绑定本质上是欺骗客户端请求的 IP 地址。

这个客户端可以在服务器上，就是 SSRF，攻击对象一般是各种后端语言的网络库，或者是无头浏览器。

SSRF 安全指北：<https://security.tencent.com/index.php/blog/msg/179>

这个客户端也可以在个人 PC 上，就是 CSRF，攻击对象一般是浏览器。

## 浏览器Tips

在浏览器中使用 DNS 重绑定技术一般是服务于 CSRF 攻击，实现绕过同源策略，实现访问本机服务，或者内网服务。如果服务没有对 host
进行校验，那么就可以进行攻击。

在GitHub
上有个项目：[https://gi](https://github.com/nccgroup/singularity)[thub.com/nccgroup/singularity](thub.com/nccgroup/singularity)实现了一个
DNS 重绑定的攻击框架，核心亮点在于实现多种 DNS 重绑定攻击策略，并有很多Bypass 技巧，在PPT
中：https://bit.ly/Singularity_Defcon27有比较完整的技术细节，这里我挑几个我认为很酷的技术点介绍一下：  

> 还有其他的比如缓存覆盖刷新，websocket 远控都很酷，感兴趣的师傅可以看代码。

### Multiple answers

使用这个重绑定策略能实现全平台全浏览器 3
秒内完成攻击。![](https://image.3001.net/images/20220217/1645090311_620e16076b1f9d5c9e276.png!small)

Multiple answers简称 ma，这个策略利用 DNS Multiple Answers，查询 dns 的时候响应两个 IP
地址，一个是真实的服务器 IP，另一个是内网 IP，比如 127.0.0.1，官方 PPT 上有一个很棒的图。

![](https://image.3001.net/images/20220217/1645090377_620e164949030a87c1a48.png!small)

浏览器在拿到多个 dns 响应时，会尝试用第一个连接，失败之后就会尝试另一个，这时就实现了 DNS 重绑定。这个其实算是一个正常功能，也非常常见，可以说是
DNS 层面的负载均衡技术。

![](https://image.3001.net/images/20220217/1645090400_620e16608f4bc0e4ec915.png!small)

 **ma策略下还有些小问题：**

* * *

  
 **1.当客户端拿到多个 dns 结果的时候会先选择哪一个？**

参考 How do DNS clients choose an IP address when they get multiple
answers?（<https://serverfault.com/questions/102879/how-do-dns-clients-choose-an-ip-address-when-they-get-multiple-answers>）。大多数都会按照响应的顺序连接，有些是随机的，有些则会根据子网掩码计算最近的 IP 进行连接。

* * *

 **2.客户端会尝试整个 IP 列表吗？**

完全看客户端实现，从测试看至少浏览器会。

* * *

 **3.公用 dns 服务器会打乱这个响应顺序吗？**

部分服务器存在打乱顺序和强制设置 TTL 的情况，所以 ma策略在使用某些 dns 服务器时有一定概率失败。

* * *

**原始响应**![](https://image.3001.net/images/20220217/1645090564_620e17043f5cf4db673bc.png!small)

 **8.8.8.8
查询多次尝试一致**![](https://image.3001.net/images/20220217/1645090650_620e175a6f5cf6abf19f9.png!small)

 **1.1.1.1
查询存在排序混乱**![](https://image.3001.net/images/20220217/1645090673_620e1771b4a9ee88e718d.png!small)

![](https://image.3001.net/images/20220217/1645090681_620e1779ada626dfc7a58.png!small)

 **119.29.29.29
失败**![](https://image.3001.net/images/20220217/1645090705_620e1791551518a9971d7.png!small)

 **223.5.5.5 存在排序混乱，强制
TTL**![](https://image.3001.net/images/20220217/1645090725_620e17a50a78d058c3d51.png!small)

![](https://image.3001.net/images/20220217/1645090738_620e17b2b67f7c4bc8d76.png!small)

 **114.114.114.114 首次查询正常，后续查询强制 TTL，并存在排序混乱**

![](https://image.3001.net/images/20220217/1645090778_620e17da0013a094d1e6e.png!small)

![](https://image.3001.net/images/20220217/1645090788_620e17e40cc83ac009b48.png!small)

所以… 一些不规范的 DNS 服务器一定程度上能缓解攻击…

### 0.0.0.0 Bypass

在 Linux 和 macOS 中 0.0.0.0实际上是 127.0.0.1，如果一个程序监听 127.0.0.1，使用 0.0.0.0也能访问到。

![](https://image.3001.net/images/20220217/1645090806_620e17f60918fc79c4d87.png!small)

而在 Windows
中，0.0.0.0就不是一个有效地址。![](https://image.3001.net/images/20220217/1645090948_620e1884ce58027f36ede.png!small)

![](https://image.3001.net/images/20220217/1645090960_620e1890eb3ced3b6b9ea.png!small)

## PNA策略

PNA (Private Network Access) 是目前 Chrome 正在推广的一个安全策略，目标就是缓解 CSRF
对本地或者内网服务的攻击利用。

  * https://wicg.github.io/private-network-access/
  * https://developer.chrome.com/blog/private-network-access-update/
  * https://developer.chrome.com/blog/private-network-access-preflight/

在 Chrome 94 版本中，开始拦截公网 http 网站对私有网络的请求。

在未来的 Chrome 98 版本中，在访问私有网络前会尝试 CORS preflight，纯测试警告提醒开发者，并不会拦截，和常规的跨域类似，只是响应头为
Access-Control-Request-Private-Network: true，后续预计在 Chrome 101 版本中将会严格执行安全策略，拦截
preflight 失败的请求。

目前 Chrome 是 97 版本，已经会拦截 http 网站的内网请求了，可以简单尝试一下。

![](https://image.3001.net/images/20220217/1645091059_620e18f3e882a0a0f632a.png!small)

> The request client is not a secure context and the resource is in more-> private address space private. 请求客户端不是安全上下文，资源位于更私密的地址空间 “private” 中。

这里多了一个概念 more-private address space，可以在 DevTools 中 Network
右键打开一列。![](https://image.3001.net/images/20220217/1645091072_620e190018f39430a320e.png!small)

可以看到 http://rebind.it/网站属于 Public，如果打开一个内网或者本地服务，可以看到是
Private。![](https://image.3001.net/images/20220217/1645091092_620e1914cedd335915cda.png!small)

可以猜到浏览器是根据远程地址进行空间划分，分为 Public，Private，Local 等，然后限制 Public 到 Private 或者 Local
的请求。![](https://image.3001.net/images/20220217/1645091117_620e192d5945e5e4d6bcf.jpeg!small)

在 issues 中也能看到 DNS 重绑定攻击在 Chrome 中失败的惨案，DNS 重绑定到内部地址的请求全部被拦截。

  * https://github.com/nccgroup/singularity/issues/44  

同时这里也没有特别注明是 fetch，使用 script或者
img自带跨域的标签加载也会被拦截。![](https://image.3001.net/images/20220217/1645091165_620e195dd137eb287b43d.png!small)

PNA 的防御还是挺狠的。

## PNA Bypass

PNA 一共 3 个判定条件，一个个看。在 CSRF 攻击场景中，目标服务一般都是 http，意味着攻击请求是 http 的，而且对于 DNS
重绑定来说，只能攻击 http 服务，https 服务直接就会因为证书错误而失败。同时 Chrome 又拦截了混合内容，意味着我们的服务也得是 http
的。![](https://image.3001.net/images/20220217/1645091199_620e197f561aa356fc066.png!small)

第一个条件 isFromHTTP==true，没法绕了，后两个条件似乎是类似的，问题都在于 Chrome 是如何给地址分类的？

### Bypass 1

还记得前面提到的 0.0.0.0吗？Chrome 认为 0.0.0.0是 Public。

![](https://image.3001.net/images/20220217/1645091216_620e19908fcf2e0464ca6.png!small)

同时在 Linux 和 macOS 上 0.0.0.0是指 127.0.0.1，isToPrivateOrLocal==false这样就绕过了
PNA，当然这个 Bypass 不适用于 Windows。

### Bypass 2

除了Chrome对IP的分类错误，还有一种情况让Chrome直接 “跳过” 分类。

如果有师傅按照上面自己操作一下，应该就能发现，在 Chrome 使用代理的时候，Remote Address
Space永远都是一样的，实际上都是代理服务器的 Address Space。

![](https://image.3001.net/images/20220217/1645091228_620e199ccea29adecf2ed.png!small)

因为浏览器配置代理后，浏览器就不解析 DNS 了，所有的请求直接转发给代理服务器，实际产生连接的也是代理服务器，这里标记的 Remote Address
Space自然也就是代理服务器了，isFromPublic==false，实现绕过 PNA。但是，此时发生 DNS
重绑定攻击就不是在浏览器中，而是在代理服务器中，因为实际客户端是代理软件，DNS Rebinding in Proxy Server 这就是另一个话题了。

## 最后

在 Linux 和 macOS 中，利用 0.0.0.0还是可以使用 DNS 重绑定攻击本地服务。在代理场景中，PNA 策略直接失效，DNS
重绑定如旧。PNA 还是很棒的，继 SameSite 之后 CSRF 漏洞又遭一锤，有认证的外部服务无了，无认证的内部服务也无了。

说起 SameSite，前几天发布的 Firefox 96 版本（<https://www.mozilla.org/en-US/firefox/96.0/releasenotes/>）

也开始默认设置 SameSite=lax了，现在好像就差 Safari 了。

（<https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Set-Cookie/SameSite#%E6%B5%8F%E8%A7%88%E5%99%A8%E5%85%BC%E5%AE%B9%E6%80%A7>）

> SameSite 的可以看这篇 《[CSRF 漏洞的末日？关于 Cookie SameSite
> 那些你不得不知道的事](http://mp.weixin.qq.com/s?__biz=MzIwMDk1MjMyMg==&mid=2247484949&idx=1&sn=73f32260765596aa0fe773c755561308&chksm=96f41978a183906e0b4f21fddcbe2d19f667b6e6cf2bdb66160a744d161a7bac7b420acac005&scene=21#wechat_redirect)》。

对于 CSRF 来说，在浏览器层面做防御，和服务端的修修补补比，可以说是降维打击了。

> 这让我想起了 NAT Slipstream ，Chrome 直接把相关端口都给 Block 了 ，简单粗暴。

