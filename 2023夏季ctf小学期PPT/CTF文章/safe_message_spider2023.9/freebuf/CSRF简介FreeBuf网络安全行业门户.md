CSRF是跨站请求伪造，不攻击网站服务器，而是冒充用户在站内的正常操作。通常由于服务端没有对请求头做严格过滤引起的。CSRF会造成密码重置，用户伪造等问题，可能引发严重后果。

我们知道，绝大多数网站是通过 cookie 等方式辨识用户身份，再予以授权的。所以要伪造用户的正常操作，最好的方法是通过 XSS
或链接欺骗等途径，让用户在本机（即拥有身份 cookie 的浏览器端）发起用户所不知道的请求。CSRF攻击会令用户在不知情的情况下攻击自己已经登录的系统。

![1.jpg](https://image.3001.net/images/20181017/1539764806_5bc6f2465902f.jpg!small)  

CSRF攻击的目的是滥用基本的Web功能。如果该网站可以使服务器上的状态变化，如改变受害者的电子邮件地址或密码，或购买的东西，强迫受害人检索数据等等。CSRF攻击会修改目标状态。在这一过程中，受害者会代替攻击者执行这些攻击，攻击者中不会收到响应，受害者会代替攻击者执行这些攻击。

在跨站点请求伪造(CSRF)攻击中，攻击者经由用户的浏览器注入网络请求来破坏用户与网站的会话的完整性。浏览器的安全策略允许网站将HTTP请求发送到任何网络地址。此策略允许控制浏览器呈现的内容的攻击者使用此用户控制下的其他资源。

需要对页面参数做修改时，可以使用burpsuit生成csrf
poc，从而进行poc测试，测试完成之后一定要验证，浏览器执行了我们生成的poc测试，令数据产生变化。

学习csrf可以与XSS联系在一起，XSS获取cookie，CSRF伪造跨站请求完成指令。Webgoat，DVWA，webug等平台都有CSRF相关练习。下面是一些简单的CSRF应用场景。

Webgoat  

Webgoat中CSRF被归类至请求伪造：

![2.png](https://image.3001.net/images/20181017/1539764920_5bc6f2b80cf12.png!small)

例如通过修改referer的主机地址，让其他主机代为执行发送评论，修改密码等功能。

或者利用burpsuit生成csrf poc，诱导其他用户点击生成的poc链接，从而让其他其他用户执行poc中设计好的操作。

除了可以生成poc诱导其他用户执行，和修改request headers,也可以结合xss窃取cookie并进行其他操作。

在webgoat中通过修改referer

或利用burpsuit生成poc,并诱导其他用户执行其中的操作

DVWA  

DVWA中的CSRF题目比webgoat中的题目的目标更明确。

![12.png](https://image.3001.net/images/20181017/1539764934_5bc6f2c65bacb.png!small)Low等级的url是get型，直接构造url就可以实现更改用户密码的目的。所以，我们可以构造相应的url诱导受害者点击，从而实现修改受害者密码的目的。

Medium等级修改referer参数，令referer参数包含host中的主机名，以绕过对referer的检测。

![1223.png](https://image.3001.net/images/20181017/1539765235_5bc6f3f35c205.png!small)  

HIGH等级，直接修改密码，会提示“CSRF token is
incorrect”，即需要获取token进行认证,才可以完成CSRF。这种情况会将XSS与csrf结合，利用xss获取token,csrf则利用xss获取的cookie进行注入。

总而言之，CSRF是一个相对简单的漏洞。提高安全意识，增加对token，referer的认证，可以有效减少CSRF。

*本文作者：EVA。本文属丁牛科技原创，如需转载请标明出处。

