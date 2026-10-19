![](https://image.3001.net/images/20200312/1584005707_5e6a024b61378.jpg!small)

**在该篇Writeup中，介绍了作者在某漏洞测试项目中发现JSON类型跨站请求伪造漏洞（Cross-Site Request
Forgery,CSRF）的过程。**

通常来说，JSON CSRF漏洞主要在于Web应用本身的身份验证机制上，简单来看存在该漏洞，其HTTP请求须满足以下三个条件：

> 1、Web应用身份验证机制是基于Cookie形式的（Cookie形式的验证机制本身存在CSRF攻击风险）；
>
> 2、Web应用的HTTP请求中无针对用户的特定token保护；
>
> 3、Web应用的HTTP请求无同源策略保护。

如果具备上述三个条件，那么就可以从其它源中以创建AJAX请求的方式实现JSON请求伪造。注意，这只是实现JSON
CSRF的主要条件，但有时候，即使是第2或第3个条件不满足，也有可能实现JSON CSRF。

## 我最近发现的JSON CSRF漏洞

当我测试Web应用时，我会特意去分析身份验证机制，如果其是基于Cookie形式的验证方式，那么我就会直接测试CSRF漏洞。这里的情况和上述三个主要条件有点不同，这里只满足第1，而第2第3个条件都不满足。因为这里的Web应用HTTP请求中，针对不同用户都在‘X-Auth-Token’头中指定了不同的Token值，而且还对Origin头进行了验证。以下是Web应用的PUT请求：

![](https://image.3001.net/images/20200312/1584005740_5e6a026ca62a3.png!small)

![](https://image.3001.net/images/20200312/1584005747_5e6a0273491d5.png!small)

![](https://image.3001.net/images/20200312/1584005826_5e6a02c2a75ca.png!small)

平时，我从Twitter中学习到了一些请求测试方法，所以这里我就来尝试尝试：

> 1、把请求方法更改为GET，增加一些内容作为请求参数；
>
> 2、删除请求中原本的用户特定Token和一些验证头信息；
>
> 3、以相同的长度不同的Token验证测试请求。

很幸运，其中的第2种方法是有效的，删除请求中包含Token的‘X-Auth-Token’头后，Web应用后端竟然还能正常响应：

![](https://image.3001.net/images/20200312/1584005840_5e6a02d051249.png!small)

到此，尽管Web应用存在Token头验证漏洞，但由于请求是PUT方式且Web后端还对 Origin
有验证，所以我们还是无法深入利用。如果Web后端接受其它Origin头就好了，那样的话，至少可以用PUT方法伪造JSON形式的AJAX请求。怎么办呢？

接着，我把PUT请求方法更改为POST，并把其中的Origin头删掉，然后出现了以下错误提示：

![](https://image.3001.net/images/20200312/1584005859_5e6a02e300ffe.png!small)

Web后端不允许POST方法？但没关系，还可以用另外一种重写方法来测试一下，我们在POST方法后加上_method=PUT试试看：

![](https://image.3001.net/images/20200312/1584005930_5e6a032ab73d4.png!small)

竟然是可以的！所以到此，CSRF的实现条件基本成立，可创建以下POC代码进行深入测试：

    
    
    <body onload='document.forms[0].submit()'>
    
    <form action="https://<vulnerable-url>?_method=PUT" method="POST" enctype="text/plain">
    
    <input type="text" name='{"username":"blob","dummy":"' value='"}'>
    
    <input type="submit" value="send">
    
    </form>
    
    <!---This results in a request body of:
    
    {"username":"blob", "dummy": "="} -->

## 总结

该漏洞原因在于Web应用对anti-csrf
token和请求头存在不安全的校验，测试者在进行漏洞验证时不但需要理解基本的CSRF原理，还需掌握一些独特的请求重写技巧，就可能找到突破口。

 ***参考来源：[medium](https://medium.com/@secureITmania/how-i-exploit-the-json-csrf-with-method-override-technique-71c0a9a7f3b0)，clouds 编译整理，转载请注明来自
FreeBuf.COM1**

