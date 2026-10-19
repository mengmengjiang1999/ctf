***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**想像一下这种场景，当你初次用Twitter服务，登录其附属或授权的第三方app应用时，Twitter会按惯例执行OAuth授权验证，如以下这个界面。仔细查看查看，可以看到，Twitter应用会列出在授权登录之后，其会进行（will
be able to）和不会执行（will not be able
to）的操作。而在其不会执行的操作中，它清楚地列出了：不会读取用户的推特私信（Direct Messages）。真是这样的吗？**

![01.png](https://image.3001.net/images/20181221/1545381687_5c1ca737d1095.png!small)
但实际是，如果你点击 Authorize app之后，你的推特私信（Direct
Messages）将会被Twitter完全读取，和你个人相关的私信聊天内容，如性别、段子笑话、表情包等等将会被Twitter收集得到，从而导致个人信息间接泄露，非常悲剧！换句话说，Twitter附属或其第三方app应用服务，是有权限读取用户推特私信（Direct
Messages）内容的，也就是说，我们用户完全被Twitter欺骗了！怎么会像这样呢？一起来听听漏洞发现者Terence Eden的验证和阐述。

## 漏洞原因

2013年，Twitter官方应用app的用户接入 OAuth授权API
相关私钥（key）和密码(secrect)遭到泄露，被人[放到了Github](https://gist.github.com/shobotch/5160017)上，这些API密钥信息都用于Twitter官方应用，如Twitter
for Android、Twitter for iPhone、Twitter for Google TV、TweetDeck等app的用户接入授权验证。

这种信息泄露导致的问题就是，一些未被Twitter官方认证的第三方app应用可以用这些密钥信息实行假冒，接入Twitter官方应用API。

为了防止第三方app获取这些密钥并使用它们将用户直接重定向到app应用中，Twitter作了 “[callback address
restrictions](https://developer.twitter.com/en/docs/basics/apps/guides/callback-urls.html)”（回调地址限制）的设置，也就是说，这个回调地址会在app配置中要求用户输入一个预先设定的URL地址，告诉用户，当用户用Twitter账号密码登录app之后，将会被重定向到这个URL链接页面，这个URL链接对用户来说，相当于登录后的重定向跳转。

另外，Terence
Eden还强调，针对一些用户直接无法访问或嵌入web浏览器的app应用，像命令行应用、嵌入式系统、游戏控制端或某些类型的移动app，Twitter对这些应用的验证授权相对困难，为此，Twitter推出了一种替代性的次要解决方案，那就是使用PIN码验证，用户使用Twitter账号密码登录这些应用后，跳出的不是直接的回调页面（callback
url,），而是一个需要进一步验证的7位数PIN码。之后，用户在其app应用中输入这个PIN码作为oauth_verifier，之后即可在后台得到一个access_token，以此继续使用app。在这个PIN验证过程中，Twitter并没有显示出恰当的验证后权限信息，为此可能会对用户造成误导。

![02.png](https://image.3001.net/images/20181221/1545381860_5c1ca7e439352.png!small)总结来说，漏洞发现者Terence
Eden对该漏洞有以下几方面的理解：

> 1.2013年，遭到泄露的Twitter官方应用app用户接入授权API密钥信息，现在仍可被利用；
>
>
> 2.Twitter官方应用和一些其它第三方应用利用这些授权API密钥信息进行OAuth授权，提示界面明确指出“不会读取用户推特私信”，但实际上，这些应用是能读取到用户的推特私信（Direct
> Messages）内容的；
>
> 3.未经Twitter认证的其它第三方应用，在授权接入Twitter
> API时，会被要求输入一个7位数PIN码，用户按照指示输入后，并未显示完整的Twitter具备权限，对用户造成误导。

## PoC

针对该漏洞的以上理解，Terence Eden给出了以下验证性代码，并称在点击Authorize
app授权，并输入PIN码后，能读取并打印出自己的推特私信内容：

    
    
    #!/usr/bin/env python
    
    import tweepy
    
    # Official Keys
    
    consumer_key    = 'IQKbtAYlXLripLGPWd0HUA'
    
    consumer_secret = 'GgDYlkSvaPxGxC4X8liwpUoqKwwr3lCADbz8A7ADU'
    
    # Set up the authorisation
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    
    auth.secure = True
    
    auth_url = auth.get_authorization_url()
    
    print 'Visit this URL and authorise the app to use your Twitter account: ' + auth_url
    
    # The above URL says that there's no access to DMs
    
    verifier = raw_input('Type in the generated PIN: ').strip()
    
    auth.get_access_token(verifier)
    
    # Full Auth
    
    full_auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    
    full_auth.set_access_token(auth.access_token, auth.access_token_secret)
    
    api = tweepy.API(full_auth)
    
    # Print all the user's Direct Messages
    
    print api.direct_messages()

## 漏洞修复和总结

针对该漏洞，重点在于以上代码可读取并打印出自己的推特私信内容，因此Twitter一开始和Terence
Eden进行了积极沟通，并认为他们关注的是，第三方app应用程序是否可能在未经用户同意的情况下访问用户数据。另外，Twitter说明，其 Twitter
for iOS 和 Twitter for Android
没有显示用户同意对话框的原因在于，因为OAuth是一个基本的技术细节，而不是一个授权认证会话的批准过程。Twitter还声称，他们已经取消Twitter
for Google TV 的应用，并将会审查其它第三方app应用，以确定是否有任何app有可能访问他们未被授权访问的数据。

但是，最终待漏洞完全披露后，Twitter的态度有了转变，其在漏洞总结中声称：

> 漏洞上报者所说的使用PIN码或非预期OAuth流验证机制，我们认为并不会对用户造成误导，另外，我们也不认为用户数据会被Twitter for
> iPhone 或 Twitter for Google TV
> 在未授权情况下读取，而且据目前情况来看，没有任何Twitter用户因此漏洞遭受个人隐私信息泄露。

呵呵......但好在最终该漏洞，Twitter还是奖励了Terence Eden $2,940，漏洞原因被HackerOne定义为隐私侵犯。Terence
Eden表示，虽然该漏洞很难被攻击者利用，但是，这是一种对用户隐私的欺骗和漠视。尤其是在现今GDPR（通用数据保护条例）的前提下，大公司更应该做出良好典范。

## 漏洞上报进程

> 2018-11-06 通过HackerOne上报漏洞；
>
> 2018-11-06 提供更多技术性说明和POC代码；
>
> 2018-11-15 因美国假期原因，漏洞披露被推后；
>
> 2018-11-16 Twitter奖励了$2,940美金；
>
> 2018-12-06 Twitter修复了漏洞；
>
> 2018-12-14 发表这篇文章。

 ***参考来源：[shkspr](https://shkspr.mobi/blog/2018/12/twitter-bug-bounty/)、[threatpost](https://threatpost.com/twitter-data-privacy-bugs/140007/)、[hackerone](https://hackerone.com/reports/434763)，clouds编译，转载请注明来自FreeBuf.COM
**  

