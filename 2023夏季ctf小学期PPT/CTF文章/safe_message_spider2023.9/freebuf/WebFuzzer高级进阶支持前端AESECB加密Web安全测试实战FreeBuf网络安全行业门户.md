# 背景知识：

随着 Yakit Web Fuzzer
的广泛使用，我们遇到了很多非常复杂且需要针对前端加密的处理场景，为此，虽然在独一无二的热加载机制理论中可以解决这类问题，但是在某些更贴近实战的场景还是会有水土不服。为此我们在
Web Fuzzer 中恢复了`{{params(...)}}`标签的使用，这个标签可以在一个 Web Fuzzer
中做各种便捷操作。当然`{{params(...)}}`作为一个 Yaklang Fuzz Tag，我们采用了 “构造函数” 的内置 Hook
让他更具备实战价值。

我们以非常常见的 AES-ECB 进行前端加密的场景来使用 Yakit 解决测试问题。

# Web Fuzzer 核心流程

我们实现 Web Fuzzer 的时候，其实并不是简单的把一个数据包发送出去，同时为了保证数据包的自动纠错，自动修复`Content-Type`，实现自动热加载，我们实现了下面非常复杂的流程

![](https://image.3001.net/images/20220729/1659083339_62e39a4b3011ea986beb0.png!small)

依托于 Yak 引擎内置的动态代码加载能力，我们可以很容易进行预处理，参数预加载，动态代码执行，beforeRequest 和 afterRequest
Hook。

# 如何在 Web Fuzzer 中使用 params?

> 版本要求： Yakit-1.0.16-sp2 以及以上

![](https://image.3001.net/images/20220729/1659083351_62e39a57f2fac106537cf.png!small)

我们通过 Web Fuzzer Request 区域的 “热加载标签” 打开热加载代码调试界面，然后点击 “预加载参数展开”
即可看到`__getParams__`函数，我们填写这个函数，可以快速生成一个可适配在`{{params(...)}}`标签中的参数列表

## 基础使用：使用 params 标签替换同时替换一个或多个值

![](https://image.3001.net/images/20220729/1659083363_62e39a63814f2f7a76acf.png!small)

  1. ### 构造一段 params 生成代码：

  2.     __getParams__ = func() {
        /*
            __getParams__ 是一个用户可控生成复杂数据初始数据的参数：
            可以在这个函数中同时处理所有数据：
            
            1. CSRF Bypass
            2. 获取额外信息，进行强关联的信息变形
        */
        return {
            "test2": "test2的值",
            "test": ["test 有两个值", "123123"],
        }
    }

``

上述代码，返回一个`map`，这个结构体包含两个不同的
key，分别为`test`和`test2`于是我们可以在我们的数据包中使用`{{params(test)}}`和`{{params(test2)}}`，分别会替换成大家返回的两个值。

  2. ### 使用标签构造 Request

![](https://image.3001.net/images/20220729/1659083463_62e39ac727c253d9e5768.png!small)

我们使用上述设置好的标签，数据包修改为上述内容，将会把生成的标签内容渲染到数据包中，上述内容，我们返回了一个数组和一个字符串，那么发送数据包将得到两个结果

![](https://image.3001.net/images/20220729/1659083485_62e39add84dd270068d2c.png!small)

这两个结果分别为如下内容

![](https://image.3001.net/images/20220729/1659083494_62e39ae644403f2baad34.png!small)

![](https://image.3001.net/images/20220729/1659083503_62e39aef0cd46b038c3cc.png!small)

# 实战案例：前端加密的解决方案

## 加密分析：前端 AES-ECB 加密

![](https://image.3001.net/images/20220729/1659083515_62e39afb227a39653f4ce.png!small)

我们观察目标网站中的内容，发现实际上 S1 是硬编码的，经过验证后，我们可以用 yak 实现上述加密：

![](https://image.3001.net/images/20220729/1659083524_62e39b0404720c66c7089.png!small)

除此之外，每一次刷新之后，我们发现 COOKIE_DT_T 和 code 在 Set-Cookie 中会被携带：

![](https://image.3001.net/images/20220729/1659083531_62e39b0bd619443a5ecac.png!small)

这两个值对应了表单中的 t1 和验证码（... 并不鼓励大家这么实现应用，验证码应该和 Cookie / JSESSIONID 进行绑定，而不应该出现在
Cookie 明文）

T1 对应的值大体是 CSRF Token 类似的作用。

当每一次刷新页面时，HTML 中下面内容会动态变化（渲染 value 的值）``

    
    
    <input type="hidden" id="t1" class="form-control pword m-b" value="....">

``

## 如何测试该接口？

整体的数据包大致为这个样子

![](https://image.3001.net/images/20220729/1659083559_62e39b273c3f11d60a610.png!small)

我们发现：

  1. token 是 HEX 编码的字符串

  2. password 是加密之后的结果；一般来说，这个数据包我们需要同时替换 password 才能让它生效；但幸运的是，这个 AES 的 Key 被硬编码到了前端

那针对这种情况我们应该如何测试？

### 简易方案：仅针对 password 进行编码

![](https://image.3001.net/images/20220729/1659083585_62e39b41ccf286ceb3fb1.png!small)

当我们实现了这个加密函数之后，我们可以直接编写一个 Yak 热加载标签，加载 `aesecbpcks7 这个函数，这个函数实现具体内容如下

![](https://image.3001.net/images/20220729/1659083594_62e39b4ad417ef9a914ee.png!small)

我们在热加载中加入如下代码，可以实现对这个点的测试

![](https://image.3001.net/images/20220729/1659083603_62e39b531f9140735682a.png!small)

### 完美方案：解决 CSRF Token 问题

>
> 跨站请求伪造（CSRF）：简单地说，是攻击者通过一些技术手段欺骗用户的浏览器去访问一个自己曾经认证过的网站并执行一些操作（如发邮件，发消息，甚至财产操作如转账和购买商品）。由于浏览器曾经认证过，所以被访问的网站会认为是真正的用户操作而去执行。这利用了web中用户身份验证的一个漏洞：
> **简单的身份验证只能保证请求是发自某个用户的浏览器，却不能保证请求本身是用户自愿发出的** 。

如果说我们这个案例的网站更 “安全” 一些，CSRF Token 在表单中被加载，那么我们每一次测试之前，需要访问这个网站，获取 Set-Cookie 中的
Session ID 以及其他内容来设置我们新的 “敏感请求”。

于是我们编写了一段 Yak 代码来获取 t1 的值

![](https://image.3001.net/images/20220729/1659083614_62e39b5ec898daaa7c769.png!small)

我们把这段代码融合到上述模块中，可以同时解决 CSRF 的问题以及加密的问题

![](https://image.3001.net/images/20220729/1659083623_62e39b67775d3b21ce17e.png!small)

在上述热加载调试中，我们实现了 CSRF Token 的自动替换，同时也实现了前端加密解密的问题。

# 结语：

本文实践难度并不低，我们实现了在 Burp Suite 中也非常难以测试的场景；通过 Yak 热加载代码与 Params 机制轻松支持了 AES-ECB
的安全测试；实际在这种场景下，我们一般需要编写一个 Python 脚本来实现全套的测试流程；同样在 Yak 中也需要编写，Yakit 可以很好地让用户只关注
“加密解密” 逻辑和 CSRF 的问题。

新人往往对这些场景束手无策，但是通过 Yakit 的进阶，将会逐渐掌握高度复杂的 Web 应用测试技术。

当然，我们也可以稍加扩展，除了解决 CSRF 的问题，我们也可以自动完成 “签名” 等各种复杂操作。

![](https://image.3001.net/images/20220729/1659083010_62e3990238be54e3a4076.gif!small)

