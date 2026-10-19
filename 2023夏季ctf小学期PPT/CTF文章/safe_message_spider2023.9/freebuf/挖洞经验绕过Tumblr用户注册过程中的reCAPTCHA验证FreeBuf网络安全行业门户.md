***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**大家好，本文分享的writeup是作者通过在Tumblr用户注册过程中，发现Tumblr的“人机身份验证”机制（reCAPTCHA）存在缺陷，可被轻松绕过。这种绕过形成的安全风险是恶意攻击者可进行大量虚假社交账户创建、进行针对账户的用户名和邮箱枚举，间接导致Tumblr网站应用出现流量异常甚至用户信息泄露。**

**![maxresdefault.jpg](https://image.3001.net/images/20190430/1556610869_5cc7ff351b2f6.jpg!small)**

## 我对漏洞众测的理解和经历分享

去年6月16日，HackerOne在伦敦举办的黑客马拉松大赛中，为发现漏洞支付的赏金有超过了8万多美金。漏洞众测确实是个未来可期的行业，对众测平台来说，有组织给赏金的测试活动，即可以激励安全研究人员发现漏洞，也能提高上报漏洞质量，还能把详细的漏洞信息转发给厂商进行及时修复。

安全是门复杂的学问，即使是大公司也难免犯错。企业在面对的内部资源和外部攻击者之间，往往存在不定的安全风险，而漏洞众测恰好可以很好地弥补其中存在的安全空白。如果你的组织机构无法从内部培养或选拔出高质量且多样化的安全测试人员，那么就可以借助外部的众测项目或咨询服务等方式，来进行安全产品或相关系统的测试和漏洞发现。

就我个人来说，在众测过程中也遇到过一些不好的经历。我曾给Myspace上报过一个访问任意账户的高危漏洞，但在我与Myspace的冗长协商过程中，他们简直就是漠不关心的态度，最终我选择了公开漏洞（[点此阅读](https://leigh-annegalloway.com/myspace/)）。该漏洞影响将近3.6亿多个用户帐户，我寄希望于能通过公众压力来促使漏洞修复，这种行为也是迫不得已。

而相反的是，我曾发现了Tumblr公司的一个reCaptcha验证码绕过漏洞，从Twitter方式上报给他们后，他们就直接私信我进行交流，只经过了两天漏洞就得到修复。以下就是我对该漏洞发现过程的分享。

## Tumblr的reCaptcha验证码绕过漏洞

在我访问[www.tumblr.com](http://www.tumblr.com)进行用户注册时，发现其中嵌入的谷歌reCAPTCHA验证码服务存在一个错误配置漏洞，那就是由客户端和应用发送的reCAPTCHA验证码请求中，其中名为‘g-recaptcha-response’
的参数值可以置空。该漏洞会对所有新注册用户产生影响，且不需要什么特别的工具进行利用，只需手动地点击网站上出现的按钮，或是通过抓包代理发起修改即可。

## 漏洞影响

通常来说，Captcha机制如果运行部署合理，是具有速率限制作用的（Rate
Limiting），可以用其来防止垃圾用户创建虚假社交账户，减少特定应用的请求量。我发现的这个Tumblr页面reCAPTCHA验证码绕过漏洞，可以被攻击者用来创建虚假账户；另外由于Tumblr的用户注册机制只允许注册邮箱绑定一个用户名，所以，也可以利用该漏洞进行针对用户邮箱和用户名的暴力枚举攻击，反复大量的枚举可以导致Tumblr的用户注册信息泄露。

## 漏洞复现

我们先来看[www.tumblr.com](http://www.tumblr.com)页面中正常的账户创建过程，首先来到登录页面<https://www.tumblr.com/login>，点击右上角的注册按钮“Sign
up”：

![01.jpg](https://image.3001.net/images/20190430/1556610506_5cc7fdcad2926.jpg!small)然后就跳转到了账户注册页面
<https://www.tumblr.com/register> :

![02.jpg](https://image.3001.net/images/20190430/1556610600_5cc7fe281c657.jpg!small)接着，点击开始按钮
‘Get Started’，之后就会出现一些必填选项，包括用户名、密码和邮箱：

![03.jpg](https://image.3001.net/images/20190430/1556610613_5cc7fe35b7ee2.jpg!small)完成以上必填项之后，还要输入年龄和勾选服务条款须知：

![04.jpg](https://image.3001.net/images/20190430/1556610628_5cc7fe44e4548.jpg!small)接下来，就会跳出一个“人机身份验证”（reCAPTCHA
）页面：

![05.jpg](https://image.3001.net/images/20190430/1556610650_5cc7fe5a9a75a.jpg!small)

![06.jpg](https://image.3001.net/images/20190430/1556610712_5cc7fe984af23.jpg!small)除了这么一个“人机身份验证”（reCAPTCHA
）选项部署在这里，其下方还有一个选项“完成了”（Almost
Done!）。搞笑的是，虽然通常来说需要完成“人机身份验证”才能进行下一步，但是，经我测试发现，可以直接不用勾选“人机身份验证”中的 “I’m not a
robot”，直接点击下方的“完成了”（Almost
Done!）即可完成这里所谓的“人机身份验证”，就直接进入下一步到用户的Tumblr主页。这种“人机身份验证”（reCAPTCHA
）部署在这里是当摆设的吗？

##
![07.jpg](https://image.3001.net/images/20190430/1556610723_5cc7fea3aff7a.jpg!small)![08.jpg](https://image.3001.net/images/20190430/1556610747_5cc7febbc4500.jpg!small)抓包分析

为了深入分析，我们用Burp来看看用户在“人机身份验证”（reCAPTCHA ）这一步发起具体的请求和响应。

发起“人机身份验证”时的POST请求如下：

![09.jpg](https://image.3001.net/images/20190430/1556610776_5cc7fed8b1213.jpg!small)仔细查看上述POST请求可以发现，其中的recaptcha质询是一个名为‘g-recaptcha-response’的参数值，也就是上图中的红字部分。但如果我们把这个参数值置空，也等同于就不去勾选它，会发生什么情况？这样构造的POST请求如下：

![10.jpg](https://image.3001.net/images/20190430/1556610795_5cc7feeb58595.jpg!small)后经测试发现，Tumblr服务器端对以上两种POST请求都返回了相同且有效的响应：

![11.jpg](https://image.3001.net/images/20190430/1556610811_5cc7fefbb0e2a.jpg!small)当然也就是说，Tumblr服务器端直接就是忘记了检查‘g-recaptcha-response’ 参数的值，才导致了上述的“人机身份验证”（reCAPTCHA ）机制被绕过。

尽管很多网站应用都要求用户群的高度可信，但类似这种验证绕过漏洞在这些网站中也很常见。这不，前不久Google才刚刚修复了一个[可完全绕过 reCAPTCHA
的漏洞](http://https//threatpost.com/google-patches-recaptcha-bypass/132335/)。

 ***参考来源：[leigh-annegalloway](https://leigh-annegalloway.com/tumblr/)，clouds编译，转载请注明来自FreeBuf.COM**  

 ****  

