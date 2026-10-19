**作者：Longofo@知道创宇404实验室  
日期：2022年11月8日**

SAML始于2001年，最终的SAML 2.0版本发布于2005年，此后也没有发布大版本，SAML
2.0一直延续到了现在。SAML已经是老古董了，现在SSO里面使用更多的是OAuth。在某些漏洞平台看到过一些SAML漏洞报告，一些大型应用依然出现过它的身影，最近看到的一个议题《Hacking
the Cloud With
SAML》[[1]](https://drive.google.com/file/d/1p1tTTIjg3RoJecYSU3CetvNw6-ZZdMXn/view)也提到了，考考古学学也不亏，至少它的一些概念现在仍在延用。

## SAML 2.0

**SAML** : Security Assertion Markup Language，一种用于安全性断言标记的语言。

SAML的用途：

  * 单点登录（SSO Single Sign-ON）
  * 联合认证（Federated Identity）
  * 在其他架构内使用SAML，例如WS-Security

后续的内容主要是SAML SSO的部分。

SAML协议中的三方：浏览器，身份鉴别服务器(IDP，Identity Provider)，服务提供者(SP，Service
provider)，以及这三方相互的通讯次序，加密方法，传输数据格式。

可能大家在网络上看到的一些流程图会多一两个步骤或少一两个步骤，那只是开发人员在具体选择和实现SAML传输时存在的一些差异，对于我们了解整个SAML认证流程问题不大，知一反三就行。基本的认证流程如下：

![](https://images.seebug.org/content/images/2022/11/6a67deb0-34e5-448e-81d7-952245dc299f.png-w331s)

图先大概浏览下，后续会在OpenSAML的案例中看到每个环节的细节。

## 通过OpenSAML请求包看SAML SSO

**OpenSAML** 是SAML协议的一个开源实现，在github找了一个用OpenSAML实现的SSO
[demo](https://github.com/OpenConext/Mujina)，使用的是HTTP-POST传输SAML，有几百个star。将项目跑起来，正常的登录一遍看下完整的通信包过程，9090端口是SP，8080端口是IDP

### 用户访问SP服务

request:

    
    
    GET /user.html?force-authn=true HTTP/1.1
    Host: 192.168.0.104:9090
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Referer: http://192.168.0.104:9090/
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,vi;q=0.7
    Cookie: mujinaSpSessionId=2E15F753B56E4646FA4CACCE4DD2ED6D; mujinaIdpSessionId=6203026E878EFB44F90769F285FB05D9
    Connection: close

response:

    
    
    HTTP/1.1 200 
    X-Content-Type-Options: nosniff
    X-XSS-Protection: 1; mode=block
    Cache-Control: no-cache, no-store, max-age=0, must-revalidate
    Pragma: no-cache
    Expires: 0
    X-Frame-Options: DENY
    Content-Type: text/html;charset=UTF-8
    Content-Language: zh-CN
    Date: Sat, 22 Oct 2022 10:29:57 GMT
    Connection: close
    Content-Length: 889
    
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mujina Service Provider</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" type="text/css" href="/main.css"/>
        <script src="/sp.js"></script>
    </head>
    <body>
    <section class="login-container-wrapper">
        <section class="login-container">
            <section class="login">
                <h1>Mujina Service Provider</h1>
                <a id="user-link" class="button" href="/user.html?force-authn=false">Login</a>
                <section class="force-authn">
                    <input type="checkbox" id="force-authn" name="force-authn"/>
                    <label for="force-authn">Force Authn request?</label>
                </section>
            </section>
            <a class="powered-by" href="https://openconext.org/" target="_blank">Copyright ?? 2018 OpenConext</a>
        </section>
    </section>
    </body>
    </html>

返回SP登录页，用户点击登录。

### SP返回重定向

request:

    
    
    GET /user.html?force-authn=true HTTP/1.1
    Host: 192.168.0.104:9090
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Referer: http://192.168.0.104:9090/
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,vi;q=0.7
    Cookie: mujinaSpSessionId=2E15F753B56E4646FA4CACCE4DD2ED6D; mujinaIdpSessionId=6203026E878EFB44F90769F285FB05D9
    Connection: close

response:

    
    
    HTTP/1.1 200 
    Set-Cookie: mujinaSpSessionId=F6BCE4D93AA256056960B9459E27B374; Path=/; HttpOnly
    Cache-control: no-cache, no-store
    Pragma: no-cache
    X-Content-Type-Options: nosniff
    X-XSS-Protection: 1; mode=block
    X-Frame-Options: DENY
    Content-Type: text/html;charset=UTF-8
    Date: Sat, 22 Oct 2022 10:30:02 GMT
    Connection: close
    Content-Length: 4483
    
    
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
        <head>
        </head>
        <body onload="document.forms[0].submit()">
            <noscript>
                <p>
                    <strong>Note:</strong> Since your browser does not support JavaScript,
                    you must press the Continue button once to proceed.
                </p>
            </noscript>
    
            <form action="http&#x3a;&#x2f;&#x2f;192.168.0.104&#x3a;8080&#x2f;SingleSignOnService" method="post">
                <div>
    
    <input type="hidden" name="SAMLRequest" value="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48c2FtbDJwOkF1dGhuUmVxdWVzdCB4bWxuczpzYW1sMnA9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpwcm90b2NvbCIgQXNzZXJ0aW9uQ29uc3VtZXJTZXJ2aWNlVVJMPSJodHRwOi8vMTkyLjE2OC4wLjEwNDo5MDkwL3NhbWwvU1NPIiBEZXN0aW5hdGlvbj0iaHR0cDovLzE5Mi4xNjguMC4xMDQ6ODA4MC9TaW5nbGVTaWduT25TZXJ2aWNlIiBGb3JjZUF1dGhuPSJ0cnVlIiBJRD0iYWhnZzRhNDVkZWg5aTY3aDBmMmllZGdhMDc1NWciIElzUGFzc2l2ZT0iZmFsc2UiIElzc3VlSW5zdGFudD0iMjAyMi0xMC0yMlQxMDozMDowMi4xMTVaIiBQcm90b2NvbEJpbmRpbmc9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpiaW5kaW5nczpIVFRQLVBPU1QiIFZlcnNpb249IjIuMCI+PHNhbWwyOklzc3VlciB4bWxuczpzYW1sMj0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmFzc2VydGlvbiI+aHR0cDovL21vY2stc3A8L3NhbWwyOklzc3Vlcj48ZHM6U2lnbmF0dXJlIHhtbG5zOmRzPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjIj48ZHM6U2lnbmVkSW5mbz48ZHM6Q2Fub25pY2FsaXphdGlvbk1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMTAveG1sLWV4Yy1jMTRuIyIvPjxkczpTaWduYXR1cmVNZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNyc2Etc2hhMjU2Ii8+PGRzOlJlZmVyZW5jZSBVUkk9IiNhaGdnNGE0NWRlaDlpNjdoMGYyaWVkZ2EwNzU1ZyI+PGRzOlRyYW5zZm9ybXM+PGRzOlRyYW5zZm9ybSBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyNlbnZlbG9wZWQtc2lnbmF0dXJlIi8+PGRzOlRyYW5zZm9ybSBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMTAveG1sLWV4Yy1jMTRuIyIvPjwvZHM6VHJhbnNmb3Jtcz48ZHM6RGlnZXN0TWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8wNC94bWxlbmMjc2hhMjU2Ii8+PGRzOkRpZ2VzdFZhbHVlPlc0dGxMc3RsVWQ3Rk9zU25JNFBtTVMwMFhybTFQQmExRDExNU03RkRxbkk9PC9kczpEaWdlc3RWYWx1ZT48L2RzOlJlZmVyZW5jZT48L2RzOlNpZ25lZEluZm8+PGRzOlNpZ25hdHVyZVZhbHVlPm9lOGQzQTZMVU1Wd05FUmd4UHIwdEl1Uk9vKzBSdzV6MTJuOTlQSnhKS05XYXZlVEdiZkFBMVBNRTQ5NFQyalZnNUhtTmVLUHJDQk1Ubk93RGZpcm16VFNDc3hUT3F3aFpJMXNOcW5rSXNMSnljenVGUjUyWUVMbVpMbms5NzQzeWVRRDBkSndLR1lRR0JCcklEOEFKdWhvQUtIWU83NFkvYWJlZDBWYTZrdmV2ZjR2a3RxY1A0R1lhc2M2MW44ajhTc2VHZ0M0a1RYdE9wdWg2UFpnLzdlZlJlNndpT3JVNDZodjdRRVpQbjZKc09mbDZxSjd0TWVjZUV6b05zTnVvcjRidjZVV05ZemlPN3U3SmkzTkdOWnQ0RXdtekNTR1dxcWdoTE5XLzVZd2FwWnpxc0ppaTBYMHEvZnZSMXFkNVQwSmpheHZpZUtZS2tmTGV0SHhiZz09PC9kczpTaWduYXR1cmVWYWx1ZT48ZHM6S2V5SW5mbz48ZHM6WDUwOURhdGE+PGRzOlg1MDlDZXJ0aWZpY2F0ZT5NSUlERXpDQ0FmdWdBd0lCQWdJSkFLb0svaGVCamNPWU1BMEdDU3FHU0liM0RRRUJCUVVBTUNBeEhqQWNCZ05WQkFvTUZVOXlaMkZ1DQphWHBoZEdsdmJpd2dRMDQ5VDBsRVF6QWVGdzB4TlRFeE1URXhNREV5TVRWYUZ3MHlOVEV4TVRBeE1ERXlNVFZhTUNBeEhqQWNCZ05WDQpCQW9NRlU5eVoyRnVhWHBoZEdsdmJpd2dRMDQ5VDBsRVF6Q0NBU0l3RFFZSktvWklodmNOQVFFQkJRQURnZ0VQQURDQ0FRb0NnZ0VCDQpBTkJHd0ovcXBUUU5pU2dVZ2xTRTJVekVrVW93K3dTOHI2N2V0eG9FaGx6SlpmZ0svazVUZkcxd0lDRHFhcEhBeEVWZ1VNMTBhQkhSDQpjdE5vY0E1d21sSHR4ZGlkaHpSWnJvcUh3cEt5MkJtc0tYNVoyb0syNVJMcHN5dXNCMUtyb2VtZ0EvQ2pVbkk2cklMMXh4Rm4zS3lPDQpGaDFaQkxVUXRLTlFlTVM3SEZHZ1NEQXArc1h1VEZ1anoxMkxGRHVnWDBUMEtCNWExKzBsOHkwUEVhMHlHYTFvaTZzZU9OeDg0OVpIDQp4TTBQUnZVdW5Xa3VUTStmb1owalpwRmFwWGUwMnlXTXFoYy8yaVlNaWVFLzNHdk9ndUpjaEp0NlIrY3V0OFZCYjZ1YktVSUdLN3BtDQpvcS9UQjZEVlhwdnNIcXNESlhlY2h4Y2ljdTRwZEtWREhTZWM4NTBDQXdFQUFhTlFNRTR3SFFZRFZSME9CQllFRks3UnFqb29kU1lWDQpYR1RWRWRMZjNrSmZsUC9zTUI4R0ExVWRJd1FZTUJhQUZLN1Jxam9vZFNZVlhHVFZFZExmM2tKZmxQL3NNQXdHQTFVZEV3UUZNQU1CDQpBZjh3RFFZSktvWklodmNOQVFFRkJRQURnZ0VCQUROWmt4bEZYaDRGNDVtdUNiblFkK1dtYVhsR3ZiOXRrVXlBSXhWTDhBSXU4SjE4DQpGNDIwdnBuR3BvVUFFK0h5M2V2Qm1wMm5rckZBZ21yMDU1ZkFqcEhlWkZnRFpCQVBDd1lkM1ROTURlU3lNdGEzS2Erb1M3R1JGRGVQDQprTUVtK2tINC9ySVROS1VGMXNPdldCVFNvd2s5VHVkRUR5RnFnR250Y2R1L2wvelJ4dngzM3kzTE1HNVVTRDB4NFg0SUtqUnJSTjFCDQpiY0tnaThkcTEwQzNqZHFOYW5jVHVQb3FUM1dXelJ2VnRCL3EzNEI3Rjc0LzZKemdFb09DRUh1ZkJNcDRaRnU1NFAweUVHdFdmVHdUDQp6dW9ab2JyQ2hWVkJ0NHcvWFphZ3JSdFVDRE53UnBITmJwanhZdWRicUxxcGkxTVFwVjlvaHQvQnBUSFZKRzJpMHJvPTwvZHM6WDUwOUNlcnRpZmljYXRlPjwvZHM6WDUwOURhdGE+PC9kczpLZXlJbmZvPjwvZHM6U2lnbmF0dXJlPjwvc2FtbDJwOkF1dGhuUmVxdWVzdD4="/>                
    
                </div>
                <noscript>
                    <div>
                        <input type="submit" value="Continue"/>
                    </div>
                </noscript>
            </form>
        </body>
    </html>

返回了IDP登录URL，并附带了AuthnRequest，这里base64编码了，解开并格式化之后如下：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <saml2p:AuthnRequest
        xmlns:saml2p="urn:oasis:names:tc:SAML:2.0:protocol" AssertionConsumerServiceURL="http://192.168.0.104:9090/saml/SSO" Destination="http://192.168.0.104:8080/SingleSignOnService" ForceAuthn="true" ID="ahgg4a45deh9i67h0f2iedga0755g" IsPassive="false" IssueInstant="2022-10-22T10:30:02.115Z" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Version="2.0">
        <saml2:Issuer
            xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion">http://mock-sp
        </saml2:Issuer>
        <ds:Signature
            xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
            <ds:SignedInfo>
                <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
                <ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
                <ds:Reference URI="#ahgg4a45deh9i67h0f2iedga0755g">
                    <ds:Transforms>
                        <ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
                        <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
                    </ds:Transforms>
                    <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
                    <ds:DigestValue>W4tlLstlUd7FOsSnI4PmMS00Xrm1PBa1D115M7FDqnI=</ds:DigestValue>
                </ds:Reference>
            </ds:SignedInfo>
            <ds:SignatureValue>oe8d3A6LUMVwNERgxPr0tIuROo+0Rw5z12n99PJxJKNWaveTGbfAA1PME494T2jVg5HmNeKPrCBMTnOwDfirmzTSCsxTOqwhZI1sNqnkIsLJyczuFR52YELmZLnk9743yeQD0dJwKGYQGBBrID8AJuhoAKHYO74Y/abed0Va6kvevf4vktqcP4GYasc61n8j8SseGgC4kTXtOpuh6PZg/7efRe6wiOrU46hv7QEZPn6JsOfl6qJ7tMeceEzoNsNuor4bv6UWNYziO7u7Ji3NGNZt4EwmzCSGWqqghLNW/5YwapZzqsJii0X0q/fvR1qd5T0JjaxvieKYKkfLetHxbg==</ds:SignatureValue>
            <ds:KeyInfo>
                <ds:X509Data>
                    <ds:X509Certificate>MIIDEzCCAfugAwIBAgIJAKoK/heBjcOYMA0GCSqGSIb3DQEBBQUAMCAxHjAcBgNVBAoMFU9yZ2Fu
    aXphdGlvbiwgQ049T0lEQzAeFw0xNTExMTExMDEyMTVaFw0yNTExMTAxMDEyMTVaMCAxHjAcBgNV
    BAoMFU9yZ2FuaXphdGlvbiwgQ049T0lEQzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEB
    ANBGwJ/qpTQNiSgUglSE2UzEkUow+wS8r67etxoEhlzJZfgK/k5TfG1wICDqapHAxEVgUM10aBHR
    ctNocA5wmlHtxdidhzRZroqHwpKy2BmsKX5Z2oK25RLpsyusB1KroemgA/CjUnI6rIL1xxFn3KyO
    Fh1ZBLUQtKNQeMS7HFGgSDAp+sXuTFujz12LFDugX0T0KB5a1+0l8y0PEa0yGa1oi6seONx849ZH
    xM0PRvUunWkuTM+foZ0jZpFapXe02yWMqhc/2iYMieE/3GvOguJchJt6R+cut8VBb6ubKUIGK7pm
    oq/TB6DVXpvsHqsDJXechxcicu4pdKVDHSec850CAwEAAaNQME4wHQYDVR0OBBYEFK7RqjoodSYV
    XGTVEdLf3kJflP/sMB8GA1UdIwQYMBaAFK7RqjoodSYVXGTVEdLf3kJflP/sMAwGA1UdEwQFMAMB
    Af8wDQYJKoZIhvcNAQEFBQADggEBADNZkxlFXh4F45muCbnQd+WmaXlGvb9tkUyAIxVL8AIu8J18
    F420vpnGpoUAE+Hy3evBmp2nkrFAgmr055fAjpHeZFgDZBAPCwYd3TNMDeSyMta3Ka+oS7GRFDeP
    kMEm+kH4/rITNKUF1sOvWBTSowk9TudEDyFqgGntcdu/l/zRxvx33y3LMG5USD0x4X4IKjRrRN1B
    bcKgi8dq10C3jdqNancTuPoqT3WWzRvVtB/q34B7F74/6JzgEoOCEHufBMp4ZFu54P0yEGtWfTwT
    zuoZobrChVVBt4w/XZagrRtUCDNwRpHNbpjxYudbqLqpi1MQpV9oht/BpTHVJG2i0ro=</ds:X509Certificate>
                </ds:X509Data>
            </ds:KeyInfo>
        </ds:Signature>
    </saml2p:AuthnRequest>

挨个看下每个标签和属性的含义。

#### AuthnRequest

SP向IDP传达我想认证一个用户，这里面不包含用户信息，里面包含的是SP的基本信息。

  * AssertionConsumerServiceURL: 指定IDP认证成功之后，要将AuthnResponse发送到SP的哪个URL处理
  * Destination: 指定IDP认证的端点
  * ForceAuthn: 强制认证，就算之前认证过，浏览器携带了认证的session，如果这个值为true，还是会重新认证
  * ID: 随机标识，主要是用来方便在其他标签引用，例如在SignedInfo中的Reference
  * IsPassive: 默认为 false 。如果为 true，则IdP不能显示的通过浏览器与用户进行交互，用户不能感知到跳转的存在
  * IssueInstant: 请求的签发时间
  * ProtocolBinding: 使用什么来传输SAML消息，这里是通过HTTP POST来传输
  * Version: 2.0版本

#### Issuer

用于标识AuthnRequest请求消息的实际签发者，通常情况下也是 URI格式。

#### Signature

签名方式，这里使用的是xmldsig(XML Signature)，这是一个概念不是指具体的算法，具体的算法在 **SignedInfo** 中。

#### SignedInfo

  * CanonicalizationMethod: 规范化算法，作用对象是Signature标签里面的内容，这里用的xml-exc-c14n，是一种用来规范xml格式的算法
  * SignatureMethod: 用什么方法对DigestValue签名，注意这里签名的对象是摘要值而不是xml对象，摘要对象才是xml
  * Reference: 引用，这里引用的ID就是AuthnRequest里面的ID，表示Refernece里面其他标签信息都会作用到AuthnRequest标签以及子标签里的内容
  * Transforms: 可以指定多个transform，对引用对象进行链式处理，比如enveloped-signature是采用部分签名方式，即AuthnRequest中的Signature标签在计算摘要时是不会计入到摘要内容；xml-exc-c14n算法是对AuthnRequest里面的内容进行规范化处理
  * DigestMethod: 对AuthnRequest信息的摘要算法，sha256类似md5算法，单向算法，不可逆，采用这种方式进行摘要计算
  * DigestValue: 对AuthnRequest信息的摘要值

#### SignatureValue

签名结果，这里签名对象是SignedInfo标签。

#### KeyInfo

包含了X509公钥证书信息， **X509Certificate**
里面的公钥会被用于摘要，IDP收到AuthnRequest后，也会用这个公钥来解密签名信息，然后和摘要值对比，看信息是否被篡改。

**如何摘要，摘的是哪部分，签的是哪部分，后续分析代码细节会看到。**

### 浏览器重定向到IDP

request:

    
    
    POST /SingleSignOnService HTTP/1.1
    Host: 192.168.0.104:8080
    Content-Length: 3718
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    Origin: http://192.168.0.104:9090
    Content-Type: application/x-www-form-urlencoded
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Referer: http://192.168.0.104:9090/
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,vi;q=0.7
    Cookie: mujinaIdpSessionId=6203026E878EFB44F90769F285FB05D9; mujinaSpSessionId=F6BCE4D93AA256056960B9459E27B374
    Connection: close
    
    SAMLRequest=PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48c2FtbDJwOkF1dGhuUmVxdWVzdCB4bWxuczpzYW1sMnA9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpwcm90b2NvbCIgQXNzZXJ0aW9uQ29uc3VtZXJTZXJ2aWNlVVJMPSJodHRwOi8vMTkyLjE2OC4wLjEwNDo5MDkwL3NhbWwvU1NPIiBEZXN0aW5hdGlvbj0iaHR0cDovLzE5Mi4xNjguMC4xMDQ6ODA4MC9TaW5nbGVTaWduT25TZXJ2aWNlIiBGb3JjZUF1dGhuPSJ0cnVlIiBJRD0iYWhnZzRhNDVkZWg5aTY3aDBmMmllZGdhMDc1NWciIElzUGFzc2l2ZT0iZmFsc2UiIElzc3VlSW5zdGFudD0iMjAyMi0xMC0yMlQxMDozMDowMi4xMTVaIiBQcm90b2NvbEJpbmRpbmc9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpiaW5kaW5nczpIVFRQLVBPU1QiIFZlcnNpb249IjIuMCI%2BPHNhbWwyOklzc3VlciB4bWxuczpzYW1sMj0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmFzc2VydGlvbiI%2BaHR0cDovL21vY2stc3A8L3NhbWwyOklzc3Vlcj48ZHM6U2lnbmF0dXJlIHhtbG5zOmRzPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjIj48ZHM6U2lnbmVkSW5mbz48ZHM6Q2Fub25pY2FsaXphdGlvbk1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMTAveG1sLWV4Yy1jMTRuIyIvPjxkczpTaWduYXR1cmVNZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNyc2Etc2hhMjU2Ii8%2BPGRzOlJlZmVyZW5jZSBVUkk9IiNhaGdnNGE0NWRlaDlpNjdoMGYyaWVkZ2EwNzU1ZyI%2BPGRzOlRyYW5zZm9ybXM%2BPGRzOlRyYW5zZm9ybSBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyNlbnZlbG9wZWQtc2lnbmF0dXJlIi8%2BPGRzOlRyYW5zZm9ybSBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMTAveG1sLWV4Yy1jMTRuIyIvPjwvZHM6VHJhbnNmb3Jtcz48ZHM6RGlnZXN0TWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8wNC94bWxlbmMjc2hhMjU2Ii8%2BPGRzOkRpZ2VzdFZhbHVlPlc0dGxMc3RsVWQ3Rk9zU25JNFBtTVMwMFhybTFQQmExRDExNU03RkRxbkk9PC9kczpEaWdlc3RWYWx1ZT48L2RzOlJlZmVyZW5jZT48L2RzOlNpZ25lZEluZm8%2BPGRzOlNpZ25hdHVyZVZhbHVlPm9lOGQzQTZMVU1Wd05FUmd4UHIwdEl1Uk9vKzBSdzV6MTJuOTlQSnhKS05XYXZlVEdiZkFBMVBNRTQ5NFQyalZnNUhtTmVLUHJDQk1Ubk93RGZpcm16VFNDc3hUT3F3aFpJMXNOcW5rSXNMSnljenVGUjUyWUVMbVpMbms5NzQzeWVRRDBkSndLR1lRR0JCcklEOEFKdWhvQUtIWU83NFkvYWJlZDBWYTZrdmV2ZjR2a3RxY1A0R1lhc2M2MW44ajhTc2VHZ0M0a1RYdE9wdWg2UFpnLzdlZlJlNndpT3JVNDZodjdRRVpQbjZKc09mbDZxSjd0TWVjZUV6b05zTnVvcjRidjZVV05ZemlPN3U3SmkzTkdOWnQ0RXdtekNTR1dxcWdoTE5XLzVZd2FwWnpxc0ppaTBYMHEvZnZSMXFkNVQwSmpheHZpZUtZS2tmTGV0SHhiZz09PC9kczpTaWduYXR1cmVWYWx1ZT48ZHM6S2V5SW5mbz48ZHM6WDUwOURhdGE%2BPGRzOlg1MDlDZXJ0aWZpY2F0ZT5NSUlERXpDQ0FmdWdBd0lCQWdJSkFLb0svaGVCamNPWU1BMEdDU3FHU0liM0RRRUJCUVVBTUNBeEhqQWNCZ05WQkFvTUZVOXlaMkZ1DQphWHBoZEdsdmJpd2dRMDQ5VDBsRVF6QWVGdzB4TlRFeE1URXhNREV5TVRWYUZ3MHlOVEV4TVRBeE1ERXlNVFZhTUNBeEhqQWNCZ05WDQpCQW9NRlU5eVoyRnVhWHBoZEdsdmJpd2dRMDQ5VDBsRVF6Q0NBU0l3RFFZSktvWklodmNOQVFFQkJRQURnZ0VQQURDQ0FRb0NnZ0VCDQpBTkJHd0ovcXBUUU5pU2dVZ2xTRTJVekVrVW93K3dTOHI2N2V0eG9FaGx6SlpmZ0svazVUZkcxd0lDRHFhcEhBeEVWZ1VNMTBhQkhSDQpjdE5vY0E1d21sSHR4ZGlkaHpSWnJvcUh3cEt5MkJtc0tYNVoyb0syNVJMcHN5dXNCMUtyb2VtZ0EvQ2pVbkk2cklMMXh4Rm4zS3lPDQpGaDFaQkxVUXRLTlFlTVM3SEZHZ1NEQXArc1h1VEZ1anoxMkxGRHVnWDBUMEtCNWExKzBsOHkwUEVhMHlHYTFvaTZzZU9OeDg0OVpIDQp4TTBQUnZVdW5Xa3VUTStmb1owalpwRmFwWGUwMnlXTXFoYy8yaVlNaWVFLzNHdk9ndUpjaEp0NlIrY3V0OFZCYjZ1YktVSUdLN3BtDQpvcS9UQjZEVlhwdnNIcXNESlhlY2h4Y2ljdTRwZEtWREhTZWM4NTBDQXdFQUFhTlFNRTR3SFFZRFZSME9CQllFRks3UnFqb29kU1lWDQpYR1RWRWRMZjNrSmZsUC9zTUI4R0ExVWRJd1FZTUJhQUZLN1Jxam9vZFNZVlhHVFZFZExmM2tKZmxQL3NNQXdHQTFVZEV3UUZNQU1CDQpBZjh3RFFZSktvWklodmNOQVFFRkJRQURnZ0VCQUROWmt4bEZYaDRGNDVtdUNiblFkK1dtYVhsR3ZiOXRrVXlBSXhWTDhBSXU4SjE4DQpGNDIwdnBuR3BvVUFFK0h5M2V2Qm1wMm5rckZBZ21yMDU1ZkFqcEhlWkZnRFpCQVBDd1lkM1ROTURlU3lNdGEzS2Erb1M3R1JGRGVQDQprTUVtK2tINC9ySVROS1VGMXNPdldCVFNvd2s5VHVkRUR5RnFnR250Y2R1L2wvelJ4dngzM3kzTE1HNVVTRDB4NFg0SUtqUnJSTjFCDQpiY0tnaThkcTEwQzNqZHFOYW5jVHVQb3FUM1dXelJ2VnRCL3EzNEI3Rjc0LzZKemdFb09DRUh1ZkJNcDRaRnU1NFAweUVHdFdmVHdUDQp6dW9ab2JyQ2hWVkJ0NHcvWFphZ3JSdFVDRE53UnBITmJwanhZdWRicUxxcGkxTVFwVjlvaHQvQnBUSFZKRzJpMHJvPTwvZHM6WDUwOUNlcnRpZmljYXRlPjwvZHM6WDUwOURhdGE%2BPC9kczpLZXlJbmZvPjwvZHM6U2lnbmF0dXJlPjwvc2FtbDJwOkF1dGhuUmVxdWVzdD4%3D

response:

    
    
    HTTP/1.1 302 
    Set-Cookie: mujinaIdpSessionId=C54BBCAED0850B9E50195AD02DEAA9D6; Path=/; HttpOnly
    X-Content-Type-Options: nosniff
    X-XSS-Protection: 1; mode=block
    Cache-Control: no-cache, no-store, max-age=0, must-revalidate
    Pragma: no-cache
    Expires: 0
    X-Frame-Options: DENY
    Location: http://192.168.0.104:8080/login
    Content-Length: 0
    Date: Sat, 22 Oct 2022 10:30:02 GMT
    Connection: close

这里IDP会验证AuthnRequest信息是否正确，然后将用户重定向到IDP的登录页。

### IDP返回登录页

省点篇幅，这里的请求和响应信息就不贴了，对流程的熟悉没影响。

### 用户输入账号密码登录

request:

    
    
    POST /login HTTP/1.1
    Host: 192.168.0.104:8080
    Content-Length: 118
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    Origin: http://192.168.0.104:8080
    Content-Type: application/x-www-form-urlencoded
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Referer: http://192.168.0.104:8080/login
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,vi;q=0.7
    Cookie: mujinaSpSessionId=F6BCE4D93AA256056960B9459E27B374; mujinaIdpSessionId=C54BBCAED0850B9E50195AD02DEAA9D6
    Connection: close
    
    username=wewe&password=ererer&persist-me=on&urn%3Amace%3Aterena.org%3Aattribute-def%3AschacHomeOrganizationType=ererer

response:

    
    
    HTTP/1.1 302 
    X-Content-Type-Options: nosniff
    X-XSS-Protection: 1; mode=block
    Cache-Control: no-cache, no-store, max-age=0, must-revalidate
    Pragma: no-cache
    Expires: 0
    X-Frame-Options: DENY
    Location: http://192.168.0.104:8080/SingleSignOnService
    Content-Length: 0
    Date: Sat, 22 Oct 2022 10:30:12 GMT
    Connection: close

IDP对校验用户，用户认证成功，生成AuthnResponse缓存到session中，然后重定向到SingleSignOnService，后面浏览器会使用GET在请求一次SingleSignOnService端点。

### 浏览器重定向到SingleSignOnService

request:

    
    
    GET /SingleSignOnService HTTP/1.1
    Host: 192.168.0.104:8080
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Referer: http://192.168.0.104:8080/login
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,vi;q=0.7
    Cookie: mujinaSpSessionId=F6BCE4D93AA256056960B9459E27B374; mujinaIdpSessionId=C54BBCAED0850B9E50195AD02DEAA9D6
    Connection: close

response:

    
    
    HTTP/1.1 200 
    Cache-control: no-cache, no-store
    Pragma: no-cache
    X-Content-Type-Options: nosniff
    X-XSS-Protection: 1; mode=block
    X-Frame-Options: DENY
    Content-Type: text/html;charset=UTF-8
    Date: Sat, 22 Oct 2022 10:30:12 GMT
    Connection: close
    Content-Length: 13542
    
    
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
        <head>
        </head>
        <body onload="document.forms[0].submit()">
            <noscript>
                <p>
                    <strong>Note:</strong> Since your browser does not support JavaScript,
                    you must press the Continue button once to proceed.
                </p>
            </noscript>
    
            <form action="http&#x3a;&#x2f;&#x2f;192.168.0.104&#x3a;9090&#x2f;saml&#x2f;SSO" method="post">
                <div>
    
    
    <input type="hidden" name="SAMLResponse" value="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48c2FtbDJwOlJlc3BvbnNlIHhtbG5zOnNhbWwycD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOnByb3RvY29sIiBEZXN0aW5hdGlvbj0iaHR0cDovLzE5Mi4xNjguMC4xMDQ6OTA5MC9zYW1sL1NTTyIgSUQ9Il9jNTBjMjQzZi1hNjA2LTRhNDMtOTQ4Ni1lYWVjMTUyYzJjMTEiIEluUmVzcG9uc2VUbz0iYWhnZzRhNDVkZWg5aTY3aDBmMmllZGdhMDc1NWciIElzc3VlSW5zdGFudD0iMjAyMi0xMC0yMlQxMDozMDoxMi41NDRaIiBWZXJzaW9uPSIyLjAiIHhtbG5zOnhzPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYSI+PHNhbWwyOklzc3VlciB4bWxuczpzYW1sMj0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmFzc2VydGlvbiIgRm9ybWF0PSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6bmFtZWlkLWZvcm1hdDplbnRpdHkiPmh0dHA6Ly9tb2NrLWlkcDwvc2FtbDI6SXNzdWVyPjxkczpTaWduYXR1cmUgeG1sbnM6ZHM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyMiPjxkczpTaWduZWRJbmZvPjxkczpDYW5vbmljYWxpemF0aW9uTWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8xMC94bWwtZXhjLWMxNG4jIi8+PGRzOlNpZ25hdHVyZU1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMDQveG1sZHNpZy1tb3JlI3JzYS1zaGEyNTYiLz48ZHM6UmVmZXJlbmNlIFVSST0iI19jNTBjMjQzZi1hNjA2LTRhNDMtOTQ4Ni1lYWVjMTUyYzJjMTEiPjxkczpUcmFuc2Zvcm1zPjxkczpUcmFuc2Zvcm0gQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjZW52ZWxvcGVkLXNpZ25hdHVyZSIvPjxkczpUcmFuc2Zvcm0gQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzEwL3htbC1leGMtYzE0biMiPjxlYzpJbmNsdXNpdmVOYW1lc3BhY2VzIHhtbG5zOmVjPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzEwL3htbC1leGMtYzE0biMiIFByZWZpeExpc3Q9InhzIi8+PC9kczpUcmFuc2Zvcm0+PC9kczpUcmFuc2Zvcm1zPjxkczpEaWdlc3RNZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGVuYyNzaGEyNTYiLz48ZHM6RGlnZXN0VmFsdWU+ZjRCVEU3SDFRUkJPbUMxblJwbXcwc09GZ0RrK3VMZ0c3cS9jTWhraUQ1bz08L2RzOkRpZ2VzdFZhbHVlPjwvZHM6UmVmZXJlbmNlPjwvZHM6U2lnbmVkSW5mbz48ZHM6U2lnbmF0dXJlVmFsdWU+TWUwMU9VYW01bGVKRjR3U1BlTTNxK0IrbUttd0pSVUxhT1k3OWhYd3hxVWJEUG13bFNKYisxdFoxK25ZdGlOVUVrWXVkUFhaT2tmOFNkbFVoRFVLSUx2dHdmb2dYVEpsZXRXd05WTzB5NmhLSFhxbW5TYXpLWmVSK3RrMWJEYTUvSnQyR0l3WlFOZkEzYUUxQlJOaUplZEpCTHc5MUFPMDJuZ0VuUlhWY3RWdFU0WHdIbHJYYlRVYWNkNDQraERyV0JvblFid1JmMEZxUll2ZTNCNEp5dWJKUDAya2ZnL3RIYTlUN1dPc0MvaE9oS2crVzZURzMySzgwbXRCeFk1MEI1RkFoSGpZRDVZcURaN0ZVL2dOQXl5cGo4VVhsTTBvdDduNm9xL1h2Y3VZTDkvMEMwemUzVS92ZXNOczhMQzFqN3lDa1JReXhBbHlsSUhSYnY4QWt3PT08L2RzOlNpZ25hdHVyZVZhbHVlPjxkczpLZXlJbmZvPjxkczpYNTA5RGF0YT48ZHM6WDUwOUNlcnRpZmljYXRlPk1JSURFekNDQWZ1Z0F3SUJBZ0lKQUtvSy9oZUJqY09ZTUEwR0NTcUdTSWIzRFFFQkJRVUFNQ0F4SGpBY0JnTlZCQW9NRlU5eVoyRnUNCmFYcGhkR2x2Yml3Z1EwNDlUMGxFUXpBZUZ3MHhOVEV4TVRFeE1ERXlNVFZhRncweU5URXhNVEF4TURFeU1UVmFNQ0F4SGpBY0JnTlYNCkJBb01GVTl5WjJGdWFYcGhkR2x2Yml3Z1EwNDlUMGxFUXpDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUINCkFOQkd3Si9xcFRRTmlTZ1VnbFNFMlV6RWtVb3crd1M4cjY3ZXR4b0VobHpKWmZnSy9rNVRmRzF3SUNEcWFwSEF4RVZnVU0xMGFCSFINCmN0Tm9jQTV3bWxIdHhkaWRoelJacm9xSHdwS3kyQm1zS1g1WjJvSzI1Ukxwc3l1c0IxS3JvZW1nQS9DalVuSTZySUwxeHhGbjNLeU8NCkZoMVpCTFVRdEtOUWVNUzdIRkdnU0RBcCtzWHVURnVqejEyTEZEdWdYMFQwS0I1YTErMGw4eTBQRWEweUdhMW9pNnNlT054ODQ5WkgNCnhNMFBSdlV1bldrdVRNK2ZvWjBqWnBGYXBYZTAyeVdNcWhjLzJpWU1pZUUvM0d2T2d1SmNoSnQ2UitjdXQ4VkJiNnViS1VJR0s3cG0NCm9xL1RCNkRWWHB2c0hxc0RKWGVjaHhjaWN1NHBkS1ZESFNlYzg1MENBd0VBQWFOUU1FNHdIUVlEVlIwT0JCWUVGSzdScWpvb2RTWVYNClhHVFZFZExmM2tKZmxQL3NNQjhHQTFVZEl3UVlNQmFBRks3UnFqb29kU1lWWEdUVkVkTGYza0pmbFAvc01Bd0dBMVVkRXdRRk1BTUINCkFmOHdEUVlKS29aSWh2Y05BUUVGQlFBRGdnRUJBRE5aa3hsRlhoNEY0NW11Q2JuUWQrV21hWGxHdmI5dGtVeUFJeFZMOEFJdThKMTgNCkY0MjB2cG5HcG9VQUUrSHkzZXZCbXAybmtyRkFnbXIwNTVmQWpwSGVaRmdEWkJBUEN3WWQzVE5NRGVTeU10YTNLYStvUzdHUkZEZVANCmtNRW0ra0g0L3JJVE5LVUYxc092V0JUU293azlUdWRFRHlGcWdHbnRjZHUvbC96Unh2eDMzeTNMTUc1VVNEMHg0WDRJS2pSclJOMUINCmJjS2dpOGRxMTBDM2pkcU5hbmNUdVBvcVQzV1d6UnZWdEIvcTM0QjdGNzQvNkp6Z0VvT0NFSHVmQk1wNFpGdTU0UDB5RUd0V2ZUd1QNCnp1b1pvYnJDaFZWQnQ0dy9YWmFnclJ0VUNETndScEhOYnBqeFl1ZGJxTHFwaTFNUXBWOW9odC9CcFRIVkpHMmkwcm89PC9kczpYNTA5Q2VydGlmaWNhdGU+PC9kczpYNTA5RGF0YT48L2RzOktleUluZm8+PC9kczpTaWduYXR1cmU+PHNhbWwycDpTdGF0dXM+PHNhbWwycDpTdGF0dXNDb2RlIFZhbHVlPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6c3RhdHVzOlN1Y2Nlc3MiLz48L3NhbWwycDpTdGF0dXM+PHNhbWwyOkFzc2VydGlvbiB4bWxuczpzYW1sMj0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmFzc2VydGlvbiIgSUQ9Il9iM2E5MjEzMy1jMTkwLTQ5NzItODkxOC1kNmE1OGE3NWFiYjQiIElzc3VlSW5zdGFudD0iMjAyMi0xMC0yMlQxMDozMDoxMi41NDlaIiBWZXJzaW9uPSIyLjAiIHhtbG5zOnhzPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYSI+PHNhbWwyOklzc3VlciBGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpuYW1laWQtZm9ybWF0OmVudGl0eSI+aHR0cDovL21vY2staWRwPC9zYW1sMjpJc3N1ZXI+PGRzOlNpZ25hdHVyZSB4bWxuczpkcz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI+PGRzOlNpZ25lZEluZm8+PGRzOkNhbm9uaWNhbGl6YXRpb25NZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzEwL3htbC1leGMtYzE0biMiLz48ZHM6U2lnbmF0dXJlTWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8wNC94bWxkc2lnLW1vcmUjcnNhLXNoYTI1NiIvPjxkczpSZWZlcmVuY2UgVVJJPSIjX2IzYTkyMTMzLWMxOTAtNDk3Mi04OTE4LWQ2YTU4YTc1YWJiNCI+PGRzOlRyYW5zZm9ybXM+PGRzOlRyYW5zZm9ybSBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyNlbnZlbG9wZWQtc2lnbmF0dXJlIi8+PGRzOlRyYW5zZm9ybSBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMTAveG1sLWV4Yy1jMTRuIyI+PGVjOkluY2x1c2l2ZU5hbWVzcGFjZXMgeG1sbnM6ZWM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMTAveG1sLWV4Yy1jMTRuIyIgUHJlZml4TGlzdD0ieHMiLz48L2RzOlRyYW5zZm9ybT48L2RzOlRyYW5zZm9ybXM+PGRzOkRpZ2VzdE1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMDQveG1sZW5jI3NoYTI1NiIvPjxkczpEaWdlc3RWYWx1ZT51UWpWVCt0MTQySUluVVdIY1BkTmthMnhQNDYrZ1VOeCtXMGxmenMyZkI4PTwvZHM6RGlnZXN0VmFsdWU+PC9kczpSZWZlcmVuY2U+PC9kczpTaWduZWRJbmZvPjxkczpTaWduYXR1cmVWYWx1ZT5kb3NVZVorLzcvc0c0bWJXR1htVVc2eWkyaGx6eDAwUkVtVmQxdHZuSWptMTBkYnpJdnpmakpHVzN5WjhGUFc2VmovWkNXL2JtWlkvdktTT08zVDNTMlhDUGlLUEVSUzVaLzRMSUxoMmhFa1dTSUdlaFhUZm1EeHdzQ255RE9LMUVqeTdFeGp0OFRiTVdpRDlwRFFLWGlHeWtYbnJvYThJK0tJOU1ITUtkUDEzU2x4WnVIRDkzbG13bWFwWGF4NmN3NFptOE1CMXY5Q0RnVWZGUlY0amFndlRZTnFyS1Z0N2VtQmJuYzJ4eFF0aWFMZDNxNk5OUWdVWE5BUzVXMUJvUVJKd0wzQ2pKNzJzUFRZUXhPSGRxcWNMUU5qTW5wUlg3UmRxODBlOGRkejYza2ZWa2wwVXBSaW9ZS1FURnA4UzZlMnIxQ29JT2pNMHBhM2hlTmtSc3c9PTwvZHM6U2lnbmF0dXJlVmFsdWU+PC9kczpTaWduYXR1cmU+PHNhbWwyOlN1YmplY3Q+PHNhbWwyOk5hbWVJRCBGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjEuMTpuYW1laWQtZm9ybWF0OnVuc3BlY2lmaWVkIj53ZXdlPC9zYW1sMjpOYW1lSUQ+PHNhbWwyOlN1YmplY3RDb25maXJtYXRpb24gTWV0aG9kPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6Y206YmVhcmVyIj48c2FtbDI6U3ViamVjdENvbmZpcm1hdGlvbkRhdGEgSW5SZXNwb25zZVRvPSJhaGdnNGE0NWRlaDlpNjdoMGYyaWVkZ2EwNzU1ZyIgTm90T25PckFmdGVyPSIyMDIyLTEwLTIyVDE4OjMwOjEyLjU0NloiIFJlY2lwaWVudD0iaHR0cDovLzE5Mi4xNjguMC4xMDQ6OTA5MC9zYW1sL1NTTyIvPjwvc2FtbDI6U3ViamVjdENvbmZpcm1hdGlvbj48L3NhbWwyOlN1YmplY3Q+PHNhbWwyOkNvbmRpdGlvbnMgTm90QmVmb3JlPSIyMDIyLTEwLTIyVDEwOjI3OjEyLjU0NloiIE5vdE9uT3JBZnRlcj0iMjAyMi0xMC0yMlQxMDozMzoxMi41NDZaIj48c2FtbDI6QXVkaWVuY2VSZXN0cmljdGlvbj48c2FtbDI6QXVkaWVuY2U+aHR0cDovL21vY2stc3A8L3NhbWwyOkF1ZGllbmNlPjwvc2FtbDI6QXVkaWVuY2VSZXN0cmljdGlvbj48L3NhbWwyOkNvbmRpdGlvbnM+PHNhbWwyOkF1dGhuU3RhdGVtZW50IEF1dGhuSW5zdGFudD0iMjAyMi0xMC0yMlQxMDozMDoxMi41NDdaIj48c2FtbDI6QXV0aG5Db250ZXh0PjxzYW1sMjpBdXRobkNvbnRleHRDbGFzc1JlZj51cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YWM6Y2xhc3NlczpQYXNzd29yZDwvc2FtbDI6QXV0aG5Db250ZXh0Q2xhc3NSZWY+PHNhbWwyOkF1dGhlbnRpY2F0aW5nQXV0aG9yaXR5Pmh0dHA6Ly9tb2NrLWlkcDwvc2FtbDI6QXV0aGVudGljYXRpbmdBdXRob3JpdHk+PC9zYW1sMjpBdXRobkNvbnRleHQ+PC9zYW1sMjpBdXRoblN0YXRlbWVudD48c2FtbDI6QXR0cmlidXRlU3RhdGVtZW50PjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0idXJuOm1hY2U6ZGlyOmF0dHJpYnV0ZS1kZWY6ZGlzcGxheU5hbWUiIE5hbWVGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphdHRybmFtZS1mb3JtYXQ6dXJpIj48c2FtbDI6QXR0cmlidXRlVmFsdWUgeG1sbnM6eHNpPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYS1pbnN0YW5jZSIgeHNpOnR5cGU9InhzOnN0cmluZyI+Sm9obiBEb2U8L3NhbWwyOkF0dHJpYnV0ZVZhbHVlPjwvc2FtbDI6QXR0cmlidXRlPjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0idXJuOm1hY2U6ZGlyOmF0dHJpYnV0ZS1kZWY6dWlkIiBOYW1lRm9ybWF0PSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YXR0cm5hbWUtZm9ybWF0OnVyaSI+PHNhbWwyOkF0dHJpYnV0ZVZhbHVlIHhtbG5zOnhzaT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEtaW5zdGFuY2UiIHhzaTp0eXBlPSJ4czpzdHJpbmciPndld2U8L3NhbWwyOkF0dHJpYnV0ZVZhbHVlPjwvc2FtbDI6QXR0cmlidXRlPjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0idXJuOm1hY2U6ZGlyOmF0dHJpYnV0ZS1kZWY6Y24iIE5hbWVGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphdHRybmFtZS1mb3JtYXQ6dXJpIj48c2FtbDI6QXR0cmlidXRlVmFsdWUgeG1sbnM6eHNpPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYS1pbnN0YW5jZSIgeHNpOnR5cGU9InhzOnN0cmluZyI+Sm9obiBEb2U8L3NhbWwyOkF0dHJpYnV0ZVZhbHVlPjwvc2FtbDI6QXR0cmlidXRlPjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0idXJuOm1hY2U6ZGlyOmF0dHJpYnV0ZS1kZWY6c24iIE5hbWVGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphdHRybmFtZS1mb3JtYXQ6dXJpIj48c2FtbDI6QXR0cmlidXRlVmFsdWUgeG1sbnM6eHNpPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYS1pbnN0YW5jZSIgeHNpOnR5cGU9InhzOnN0cmluZyI+RG9lPC9zYW1sMjpBdHRyaWJ1dGVWYWx1ZT48L3NhbWwyOkF0dHJpYnV0ZT48c2FtbDI6QXR0cmlidXRlIE5hbWU9InVybjptYWNlOmRpcjphdHRyaWJ1dGUtZGVmOmVkdVBlcnNvblByaW5jaXBhbE5hbWUiIE5hbWVGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphdHRybmFtZS1mb3JtYXQ6dXJpIj48c2FtbDI6QXR0cmlidXRlVmFsdWUgeG1sbnM6eHNpPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYS1pbnN0YW5jZSIgeHNpOnR5cGU9InhzOnN0cmluZyI+ai5kb2VAZXhhbXBsZS5jb208L3NhbWwyOkF0dHJpYnV0ZVZhbHVlPjwvc2FtbDI6QXR0cmlidXRlPjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0idXJuOm1hY2U6ZGlyOmF0dHJpYnV0ZS1kZWY6Z2l2ZW5OYW1lIiBOYW1lRm9ybWF0PSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YXR0cm5hbWUtZm9ybWF0OnVyaSI+PHNhbWwyOkF0dHJpYnV0ZVZhbHVlIHhtbG5zOnhzaT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEtaW5zdGFuY2UiIHhzaTp0eXBlPSJ4czpzdHJpbmciPkpvaG48L3NhbWwyOkF0dHJpYnV0ZVZhbHVlPjwvc2FtbDI6QXR0cmlidXRlPjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0idXJuOm1hY2U6ZGlyOmF0dHJpYnV0ZS1kZWY6bWFpbCIgTmFtZUZvcm1hdD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmF0dHJuYW1lLWZvcm1hdDp1cmkiPjxzYW1sMjpBdHRyaWJ1dGVWYWx1ZSB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6dHlwZT0ieHM6c3RyaW5nIj5qLmRvZUBleGFtcGxlLmNvbTwvc2FtbDI6QXR0cmlidXRlVmFsdWU+PC9zYW1sMjpBdHRyaWJ1dGU+PHNhbWwyOkF0dHJpYnV0ZSBOYW1lPSJ1cm46bWFjZTp0ZXJlbmEub3JnOmF0dHJpYnV0ZS1kZWY6c2NoYWNIb21lT3JnYW5pemF0aW9uVHlwZSIgTmFtZUZvcm1hdD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmF0dHJuYW1lLWZvcm1hdDp1cmkiPjxzYW1sMjpBdHRyaWJ1dGVWYWx1ZSB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6dHlwZT0ieHM6c3RyaW5nIj5lcmVyZXI8L3NhbWwyOkF0dHJpYnV0ZVZhbHVlPjwvc2FtbDI6QXR0cmlidXRlPjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0idXJuOm1hY2U6dGVyZW5hLm9yZzphdHRyaWJ1dGUtZGVmOnNjaGFjSG9tZU9yZ2FuaXphdGlvbiIgTmFtZUZvcm1hdD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmF0dHJuYW1lLWZvcm1hdDp1cmkiPjxzYW1sMjpBdHRyaWJ1dGVWYWx1ZSB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6dHlwZT0ieHM6c3RyaW5nIj5leGFtcGxlLmNvbTwvc2FtbDI6QXR0cmlidXRlVmFsdWU+PC9zYW1sMjpBdHRyaWJ1dGU+PC9zYW1sMjpBdHRyaWJ1dGVTdGF0ZW1lbnQ+PC9zYW1sMjpBc3NlcnRpb24+PC9zYW1sMnA6UmVzcG9uc2U+"/>                
    <input type="hidden" name="Signature" value="LeMNm3aevRONrMuFm9o9GJvkF/fe3KdO9j7cU9bMS0YB5IxYzo7uSE6Kgt7dLkUC41puWhTg8lP861HqeAPUhwvoRIvRxac2aa3euPpOz+vcWepAkYTQuVxznH5gn24qYRIiBflWlVgcw7iGUHeCPP2Gk9Pf5pFaGnFeSc2CR47in1sq0tp1qTUSWTdADPV4S/K5njRLFXBYcO9YwHafFjVlEtMgeWyUxPpSBFuClpVfF8T91O3X43Q444yP4tJz7cEntI6FzRCH62N1lvz0bXz3Z6JKQ9G8MfOwvGNAIfC72cwCWyewUPRzrFR4Gw7ZV4ZYSLcMlVpGxKmxVv7o0A=="/>                
    <input type="hidden" name="SigAlg" value="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>                
    <input type="hidden" name="KeyInfo" value="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48ZHM6S2V5SW5mbyB4bWxuczpkcz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI+PGRzOlg1MDlEYXRhPjxkczpYNTA5Q2VydGlmaWNhdGU+TUlJREV6Q0NBZnVnQXdJQkFnSUpBS29LL2hlQmpjT1lNQTBHQ1NxR1NJYjNEUUVCQlFVQU1DQXhIakFjQmdOVkJBb01GVTl5WjJGdQ0KYVhwaGRHbHZiaXdnUTA0OVQwbEVRekFlRncweE5URXhNVEV4TURFeU1UVmFGdzB5TlRFeE1UQXhNREV5TVRWYU1DQXhIakFjQmdOVg0KQkFvTUZVOXlaMkZ1YVhwaGRHbHZiaXdnUTA0OVQwbEVRekNDQVNJd0RRWUpLb1pJaHZjTkFRRUJCUUFEZ2dFUEFEQ0NBUW9DZ2dFQg0KQU5CR3dKL3FwVFFOaVNnVWdsU0UyVXpFa1Vvdyt3UzhyNjdldHhvRWhsekpaZmdLL2s1VGZHMXdJQ0RxYXBIQXhFVmdVTTEwYUJIUg0KY3ROb2NBNXdtbEh0eGRpZGh6Ulpyb3FId3BLeTJCbXNLWDVaMm9LMjVSTHBzeXVzQjFLcm9lbWdBL0NqVW5JNnJJTDF4eEZuM0t5Tw0KRmgxWkJMVVF0S05RZU1TN0hGR2dTREFwK3NYdVRGdWp6MTJMRkR1Z1gwVDBLQjVhMSswbDh5MFBFYTB5R2Exb2k2c2VPTng4NDlaSA0KeE0wUFJ2VXVuV2t1VE0rZm9aMGpacEZhcFhlMDJ5V01xaGMvMmlZTWllRS8zR3ZPZ3VKY2hKdDZSK2N1dDhWQmI2dWJLVUlHSzdwbQ0Kb3EvVEI2RFZYcHZzSHFzREpYZWNoeGNpY3U0cGRLVkRIU2VjODUwQ0F3RUFBYU5RTUU0d0hRWURWUjBPQkJZRUZLN1Jxam9vZFNZVg0KWEdUVkVkTGYza0pmbFAvc01COEdBMVVkSXdRWU1CYUFGSzdScWpvb2RTWVZYR1RWRWRMZjNrSmZsUC9zTUF3R0ExVWRFd1FGTUFNQg0KQWY4d0RRWUpLb1pJaHZjTkFRRUZCUUFEZ2dFQkFETlpreGxGWGg0RjQ1bXVDYm5RZCtXbWFYbEd2Yjl0a1V5QUl4Vkw4QUl1OEoxOA0KRjQyMHZwbkdwb1VBRStIeTNldkJtcDJua3JGQWdtcjA1NWZBanBIZVpGZ0RaQkFQQ3dZZDNUTk1EZVN5TXRhM0thK29TN0dSRkRlUA0Ka01FbStrSDQvcklUTktVRjFzT3ZXQlRTb3drOVR1ZEVEeUZxZ0dudGNkdS9sL3pSeHZ4MzN5M0xNRzVVU0QweDRYNElLalJyUk4xQg0KYmNLZ2k4ZHExMEMzamRxTmFuY1R1UG9xVDNXV3pSdlZ0Qi9xMzRCN0Y3NC82SnpnRW9PQ0VIdWZCTXA0WkZ1NTRQMHlFR3RXZlR3VA0KenVvWm9ickNoVlZCdDR3L1haYWdyUnRVQ0ROd1JwSE5icGp4WXVkYnFMcXBpMU1RcFY5b2h0L0JwVEhWSkcyaTBybz08L2RzOlg1MDlDZXJ0aWZpY2F0ZT48L2RzOlg1MDlEYXRhPjwvZHM6S2V5SW5mbz4="/>                
                </div>
                <noscript>
                    <div>
                        <input type="submit" value="Continue"/>
                    </div>
                </noscript>
            </form>
    
        </body>
    </html>

响应中，IDP返回了AuthnResponse内容，还有其他两个参数。

### 浏览器重定向到SP

request:

    
    
    POST /saml/SSO HTTP/1.1
    Host: 192.168.0.104:9090
    Content-Length: 12712
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    Origin: http://192.168.0.104:8080
    Content-Type: application/x-www-form-urlencoded
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Referer: http://192.168.0.104:8080/
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,vi;q=0.7
    Cookie: mujinaSpSessionId=F6BCE4D93AA256056960B9459E27B374; mujinaIdpSessionId=C54BBCAED0850B9E50195AD02DEAA9D6
    Connection: close
    
    SAMLResponse=PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48c2FtbDJwOlJlc3BvbnNlIHhtbG5zOnNhbWwycD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOnByb3RvY29sIiBEZXN0aW5hdGlvbj0iaHR0cDovLzE5Mi4xNjguMC4xMDQ6OTA5MC9zYW1sL1NTTyIgSUQ9Il9jNTBjMjQzZi1hNjA2LTRhNDMtOTQ4Ni1lYWVjMTUyYzJjMTEiIEluUmVzcG9uc2VUbz0iYWhnZzRhNDVkZWg5aTY3aDBmMmllZGdhMDc1NWciIElzc3VlSW5zdGFudD0iMjAyMi0xMC0yMlQxMDozMDoxMi41NDRaIiBWZXJzaW9uPSIyLjAiIHhtbG5zOnhzPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYSI%2BPHNhbWwyOklzc3VlciB4bWxuczpzYW1sMj0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmFzc2VydGlvbiIgRm9ybWF0PSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6bmFtZWlkLWZvcm1hdDplbnRpdHkiPmh0dHA6Ly9tb2NrLWlkcDwvc2FtbDI6SXNzdWVyPjxkczpTaWduYXR1cmUgeG1sbnM6ZHM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyMiPjxkczpTaWduZWRJbmZvPjxkczpDYW5vbmljYWxpemF0aW9uTWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8xMC94bWwtZXhjLWMxNG4jIi8%2BPGRzOlNpZ25hdHVyZU1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMDQveG1sZHNpZy1tb3JlI3JzYS1zaGEyNTYiLz48ZHM6UmVmZXJlbmNlIFVSST0iI19jNTBjMjQzZi1hNjA2LTRhNDMtOTQ4Ni1lYWVjMTUyYzJjMTEiPjxkczpUcmFuc2Zvcm1zPjxkczpUcmFuc2Zvcm0gQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjZW52ZWxvcGVkLXNpZ25hdHVyZSIvPjxkczpUcmFuc2Zvcm0gQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzEwL3htbC1leGMtYzE0biMiPjxlYzpJbmNsdXNpdmVOYW1lc3BhY2VzIHhtbG5zOmVjPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzEwL3htbC1leGMtYzE0biMiIFByZWZpeExpc3Q9InhzIi8%2BPC9kczpUcmFuc2Zvcm0%2BPC9kczpUcmFuc2Zvcm1zPjxkczpEaWdlc3RNZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGVuYyNzaGEyNTYiLz48ZHM6RGlnZXN0VmFsdWU%2BZjRCVEU3SDFRUkJPbUMxblJwbXcwc09GZ0RrK3VMZ0c3cS9jTWhraUQ1bz08L2RzOkRpZ2VzdFZhbHVlPjwvZHM6UmVmZXJlbmNlPjwvZHM6U2lnbmVkSW5mbz48ZHM6U2lnbmF0dXJlVmFsdWU%2BTWUwMU9VYW01bGVKRjR3U1BlTTNxK0IrbUttd0pSVUxhT1k3OWhYd3hxVWJEUG13bFNKYisxdFoxK25ZdGlOVUVrWXVkUFhaT2tmOFNkbFVoRFVLSUx2dHdmb2dYVEpsZXRXd05WTzB5NmhLSFhxbW5TYXpLWmVSK3RrMWJEYTUvSnQyR0l3WlFOZkEzYUUxQlJOaUplZEpCTHc5MUFPMDJuZ0VuUlhWY3RWdFU0WHdIbHJYYlRVYWNkNDQraERyV0JvblFid1JmMEZxUll2ZTNCNEp5dWJKUDAya2ZnL3RIYTlUN1dPc0MvaE9oS2crVzZURzMySzgwbXRCeFk1MEI1RkFoSGpZRDVZcURaN0ZVL2dOQXl5cGo4VVhsTTBvdDduNm9xL1h2Y3VZTDkvMEMwemUzVS92ZXNOczhMQzFqN3lDa1JReXhBbHlsSUhSYnY4QWt3PT08L2RzOlNpZ25hdHVyZVZhbHVlPjxkczpLZXlJbmZvPjxkczpYNTA5RGF0YT48ZHM6WDUwOUNlcnRpZmljYXRlPk1JSURFekNDQWZ1Z0F3SUJBZ0lKQUtvSy9oZUJqY09ZTUEwR0NTcUdTSWIzRFFFQkJRVUFNQ0F4SGpBY0JnTlZCQW9NRlU5eVoyRnUNCmFYcGhkR2x2Yml3Z1EwNDlUMGxFUXpBZUZ3MHhOVEV4TVRFeE1ERXlNVFZhRncweU5URXhNVEF4TURFeU1UVmFNQ0F4SGpBY0JnTlYNCkJBb01GVTl5WjJGdWFYcGhkR2x2Yml3Z1EwNDlUMGxFUXpDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUINCkFOQkd3Si9xcFRRTmlTZ1VnbFNFMlV6RWtVb3crd1M4cjY3ZXR4b0VobHpKWmZnSy9rNVRmRzF3SUNEcWFwSEF4RVZnVU0xMGFCSFINCmN0Tm9jQTV3bWxIdHhkaWRoelJacm9xSHdwS3kyQm1zS1g1WjJvSzI1Ukxwc3l1c0IxS3JvZW1nQS9DalVuSTZySUwxeHhGbjNLeU8NCkZoMVpCTFVRdEtOUWVNUzdIRkdnU0RBcCtzWHVURnVqejEyTEZEdWdYMFQwS0I1YTErMGw4eTBQRWEweUdhMW9pNnNlT054ODQ5WkgNCnhNMFBSdlV1bldrdVRNK2ZvWjBqWnBGYXBYZTAyeVdNcWhjLzJpWU1pZUUvM0d2T2d1SmNoSnQ2UitjdXQ4VkJiNnViS1VJR0s3cG0NCm9xL1RCNkRWWHB2c0hxc0RKWGVjaHhjaWN1NHBkS1ZESFNlYzg1MENBd0VBQWFOUU1FNHdIUVlEVlIwT0JCWUVGSzdScWpvb2RTWVYNClhHVFZFZExmM2tKZmxQL3NNQjhHQTFVZEl3UVlNQmFBRks3UnFqb29kU1lWWEdUVkVkTGYza0pmbFAvc01Bd0dBMVVkRXdRRk1BTUINCkFmOHdEUVlKS29aSWh2Y05BUUVGQlFBRGdnRUJBRE5aa3hsRlhoNEY0NW11Q2JuUWQrV21hWGxHdmI5dGtVeUFJeFZMOEFJdThKMTgNCkY0MjB2cG5HcG9VQUUrSHkzZXZCbXAybmtyRkFnbXIwNTVmQWpwSGVaRmdEWkJBUEN3WWQzVE5NRGVTeU10YTNLYStvUzdHUkZEZVANCmtNRW0ra0g0L3JJVE5LVUYxc092V0JUU293azlUdWRFRHlGcWdHbnRjZHUvbC96Unh2eDMzeTNMTUc1VVNEMHg0WDRJS2pSclJOMUINCmJjS2dpOGRxMTBDM2pkcU5hbmNUdVBvcVQzV1d6UnZWdEIvcTM0QjdGNzQvNkp6Z0VvT0NFSHVmQk1wNFpGdTU0UDB5RUd0V2ZUd1QNCnp1b1pvYnJDaFZWQnQ0dy9YWmFnclJ0VUNETndScEhOYnBqeFl1ZGJxTHFwaTFNUXBWOW9odC9CcFRIVkpHMmkwcm89PC9kczpYNTA5Q2VydGlmaWNhdGU%2BPC9kczpYNTA5RGF0YT48L2RzOktleUluZm8%2BPC9kczpTaWduYXR1cmU%2BPHNhbWwycDpTdGF0dXM%2BPHNhbWwycDpTdGF0dXNDb2RlIFZhbHVlPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6c3RhdHVzOlN1Y2Nlc3MiLz48L3NhbWwycDpTdGF0dXM%2BPHNhbWwyOkFzc2VydGlvbiB4bWxuczpzYW1sMj0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmFzc2VydGlvbiIgSUQ9Il9iM2E5MjEzMy1jMTkwLTQ5NzItODkxOC1kNmE1OGE3NWFiYjQiIElzc3VlSW5zdGFudD0iMjAyMi0xMC0yMlQxMDozMDoxMi41NDlaIiBWZXJzaW9uPSIyLjAiIHhtbG5zOnhzPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYSI%2BPHNhbWwyOklzc3VlciBGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDpuYW1laWQtZm9ybWF0OmVudGl0eSI%2BaHR0cDovL21vY2staWRwPC9zYW1sMjpJc3N1ZXI%2BPGRzOlNpZ25hdHVyZSB4bWxuczpkcz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI%2BPGRzOlNpZ25lZEluZm8%2BPGRzOkNhbm9uaWNhbGl6YXRpb25NZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzEwL3htbC1leGMtYzE0biMiLz48ZHM6U2lnbmF0dXJlTWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS8wNC94bWxkc2lnLW1vcmUjcnNhLXNoYTI1NiIvPjxkczpSZWZlcmVuY2UgVVJJPSIjX2IzYTkyMTMzLWMxOTAtNDk3Mi04OTE4LWQ2YTU4YTc1YWJiNCI%2BPGRzOlRyYW5zZm9ybXM%2BPGRzOlRyYW5zZm9ybSBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvMDkveG1sZHNpZyNlbnZlbG9wZWQtc2lnbmF0dXJlIi8%2BPGRzOlRyYW5zZm9ybSBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMTAveG1sLWV4Yy1jMTRuIyI%2BPGVjOkluY2x1c2l2ZU5hbWVzcGFjZXMgeG1sbnM6ZWM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMTAveG1sLWV4Yy1jMTRuIyIgUHJlZml4TGlzdD0ieHMiLz48L2RzOlRyYW5zZm9ybT48L2RzOlRyYW5zZm9ybXM%2BPGRzOkRpZ2VzdE1ldGhvZCBBbGdvcml0aG09Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvMDQveG1sZW5jI3NoYTI1NiIvPjxkczpEaWdlc3RWYWx1ZT51UWpWVCt0MTQySUluVVdIY1BkTmthMnhQNDYrZ1VOeCtXMGxmenMyZkI4PTwvZHM6RGlnZXN0VmFsdWU%2BPC9kczpSZWZlcmVuY2U%2BPC9kczpTaWduZWRJbmZvPjxkczpTaWduYXR1cmVWYWx1ZT5kb3NVZVorLzcvc0c0bWJXR1htVVc2eWkyaGx6eDAwUkVtVmQxdHZuSWptMTBkYnpJdnpmakpHVzN5WjhGUFc2VmovWkNXL2JtWlkvdktTT08zVDNTMlhDUGlLUEVSUzVaLzRMSUxoMmhFa1dTSUdlaFhUZm1EeHdzQ255RE9LMUVqeTdFeGp0OFRiTVdpRDlwRFFLWGlHeWtYbnJvYThJK0tJOU1ITUtkUDEzU2x4WnVIRDkzbG13bWFwWGF4NmN3NFptOE1CMXY5Q0RnVWZGUlY0amFndlRZTnFyS1Z0N2VtQmJuYzJ4eFF0aWFMZDNxNk5OUWdVWE5BUzVXMUJvUVJKd0wzQ2pKNzJzUFRZUXhPSGRxcWNMUU5qTW5wUlg3UmRxODBlOGRkejYza2ZWa2wwVXBSaW9ZS1FURnA4UzZlMnIxQ29JT2pNMHBhM2hlTmtSc3c9PTwvZHM6U2lnbmF0dXJlVmFsdWU%2BPC9kczpTaWduYXR1cmU%2BPHNhbWwyOlN1YmplY3Q%2BPHNhbWwyOk5hbWVJRCBGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjEuMTpuYW1laWQtZm9ybWF0OnVuc3BlY2lmaWVkIj53ZXdlPC9zYW1sMjpOYW1lSUQ%2BPHNhbWwyOlN1YmplY3RDb25maXJtYXRpb24gTWV0aG9kPSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6Y206YmVhcmVyIj48c2FtbDI6U3ViamVjdENvbmZpcm1hdGlvbkRhdGEgSW5SZXNwb25zZVRvPSJhaGdnNGE0NWRlaDlpNjdoMGYyaWVkZ2EwNzU1ZyIgTm90T25PckFmdGVyPSIyMDIyLTEwLTIyVDE4OjMwOjEyLjU0NloiIFJlY2lwaWVudD0iaHR0cDovLzE5Mi4xNjguMC4xMDQ6OTA5MC9zYW1sL1NTTyIvPjwvc2FtbDI6U3ViamVjdENvbmZpcm1hdGlvbj48L3NhbWwyOlN1YmplY3Q%2BPHNhbWwyOkNvbmRpdGlvbnMgTm90QmVmb3JlPSIyMDIyLTEwLTIyVDEwOjI3OjEyLjU0NloiIE5vdE9uT3JBZnRlcj0iMjAyMi0xMC0yMlQxMDozMzoxMi41NDZaIj48c2FtbDI6QXVkaWVuY2VSZXN0cmljdGlvbj48c2FtbDI6QXVkaWVuY2U%2BaHR0cDovL21vY2stc3A8L3NhbWwyOkF1ZGllbmNlPjwvc2FtbDI6QXVkaWVuY2VSZXN0cmljdGlvbj48L3NhbWwyOkNvbmRpdGlvbnM%2BPHNhbWwyOkF1dGhuU3RhdGVtZW50IEF1dGhuSW5zdGFudD0iMjAyMi0xMC0yMlQxMDozMDoxMi41NDdaIj48c2FtbDI6QXV0aG5Db250ZXh0PjxzYW1sMjpBdXRobkNvbnRleHRDbGFzc1JlZj51cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YWM6Y2xhc3NlczpQYXNzd29yZDwvc2FtbDI6QXV0aG5Db250ZXh0Q2xhc3NSZWY%2BPHNhbWwyOkF1dGhlbnRpY2F0aW5nQXV0aG9yaXR5Pmh0dHA6Ly9tb2NrLWlkcDwvc2FtbDI6QXV0aGVudGljYXRpbmdBdXRob3JpdHk%2BPC9zYW1sMjpBdXRobkNvbnRleHQ%2BPC9zYW1sMjpBdXRoblN0YXRlbWVudD48c2FtbDI6QXR0cmlidXRlU3RhdGVtZW50PjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0idXJuOm1hY2U6ZGlyOmF0dHJpYnV0ZS1kZWY6ZGlzcGxheU5hbWUiIE5hbWVGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphdHRybmFtZS1mb3JtYXQ6dXJpIj48c2FtbDI6QXR0cmlidXRlVmFsdWUgeG1sbnM6eHNpPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYS1pbnN0YW5jZSIgeHNpOnR5cGU9InhzOnN0cmluZyI%2BSm9obiBEb2U8L3NhbWwyOkF0dHJpYnV0ZVZhbHVlPjwvc2FtbDI6QXR0cmlidXRlPjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0idXJuOm1hY2U6ZGlyOmF0dHJpYnV0ZS1kZWY6dWlkIiBOYW1lRm9ybWF0PSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YXR0cm5hbWUtZm9ybWF0OnVyaSI%2BPHNhbWwyOkF0dHJpYnV0ZVZhbHVlIHhtbG5zOnhzaT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEtaW5zdGFuY2UiIHhzaTp0eXBlPSJ4czpzdHJpbmciPndld2U8L3NhbWwyOkF0dHJpYnV0ZVZhbHVlPjwvc2FtbDI6QXR0cmlidXRlPjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0idXJuOm1hY2U6ZGlyOmF0dHJpYnV0ZS1kZWY6Y24iIE5hbWVGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphdHRybmFtZS1mb3JtYXQ6dXJpIj48c2FtbDI6QXR0cmlidXRlVmFsdWUgeG1sbnM6eHNpPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYS1pbnN0YW5jZSIgeHNpOnR5cGU9InhzOnN0cmluZyI%2BSm9obiBEb2U8L3NhbWwyOkF0dHJpYnV0ZVZhbHVlPjwvc2FtbDI6QXR0cmlidXRlPjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0idXJuOm1hY2U6ZGlyOmF0dHJpYnV0ZS1kZWY6c24iIE5hbWVGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphdHRybmFtZS1mb3JtYXQ6dXJpIj48c2FtbDI6QXR0cmlidXRlVmFsdWUgeG1sbnM6eHNpPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYS1pbnN0YW5jZSIgeHNpOnR5cGU9InhzOnN0cmluZyI%2BRG9lPC9zYW1sMjpBdHRyaWJ1dGVWYWx1ZT48L3NhbWwyOkF0dHJpYnV0ZT48c2FtbDI6QXR0cmlidXRlIE5hbWU9InVybjptYWNlOmRpcjphdHRyaWJ1dGUtZGVmOmVkdVBlcnNvblByaW5jaXBhbE5hbWUiIE5hbWVGb3JtYXQ9InVybjpvYXNpczpuYW1lczp0YzpTQU1MOjIuMDphdHRybmFtZS1mb3JtYXQ6dXJpIj48c2FtbDI6QXR0cmlidXRlVmFsdWUgeG1sbnM6eHNpPSJodHRwOi8vd3d3LnczLm9yZy8yMDAxL1hNTFNjaGVtYS1pbnN0YW5jZSIgeHNpOnR5cGU9InhzOnN0cmluZyI%2Bai5kb2VAZXhhbXBsZS5jb208L3NhbWwyOkF0dHJpYnV0ZVZhbHVlPjwvc2FtbDI6QXR0cmlidXRlPjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0idXJuOm1hY2U6ZGlyOmF0dHJpYnV0ZS1kZWY6Z2l2ZW5OYW1lIiBOYW1lRm9ybWF0PSJ1cm46b2FzaXM6bmFtZXM6dGM6U0FNTDoyLjA6YXR0cm5hbWUtZm9ybWF0OnVyaSI%2BPHNhbWwyOkF0dHJpYnV0ZVZhbHVlIHhtbG5zOnhzaT0iaHR0cDovL3d3dy53My5vcmcvMjAwMS9YTUxTY2hlbWEtaW5zdGFuY2UiIHhzaTp0eXBlPSJ4czpzdHJpbmciPkpvaG48L3NhbWwyOkF0dHJpYnV0ZVZhbHVlPjwvc2FtbDI6QXR0cmlidXRlPjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0idXJuOm1hY2U6ZGlyOmF0dHJpYnV0ZS1kZWY6bWFpbCIgTmFtZUZvcm1hdD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmF0dHJuYW1lLWZvcm1hdDp1cmkiPjxzYW1sMjpBdHRyaWJ1dGVWYWx1ZSB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6dHlwZT0ieHM6c3RyaW5nIj5qLmRvZUBleGFtcGxlLmNvbTwvc2FtbDI6QXR0cmlidXRlVmFsdWU%2BPC9zYW1sMjpBdHRyaWJ1dGU%2BPHNhbWwyOkF0dHJpYnV0ZSBOYW1lPSJ1cm46bWFjZTp0ZXJlbmEub3JnOmF0dHJpYnV0ZS1kZWY6c2NoYWNIb21lT3JnYW5pemF0aW9uVHlwZSIgTmFtZUZvcm1hdD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmF0dHJuYW1lLWZvcm1hdDp1cmkiPjxzYW1sMjpBdHRyaWJ1dGVWYWx1ZSB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6dHlwZT0ieHM6c3RyaW5nIj5lcmVyZXI8L3NhbWwyOkF0dHJpYnV0ZVZhbHVlPjwvc2FtbDI6QXR0cmlidXRlPjxzYW1sMjpBdHRyaWJ1dGUgTmFtZT0idXJuOm1hY2U6dGVyZW5hLm9yZzphdHRyaWJ1dGUtZGVmOnNjaGFjSG9tZU9yZ2FuaXphdGlvbiIgTmFtZUZvcm1hdD0idXJuOm9hc2lzOm5hbWVzOnRjOlNBTUw6Mi4wOmF0dHJuYW1lLWZvcm1hdDp1cmkiPjxzYW1sMjpBdHRyaWJ1dGVWYWx1ZSB4bWxuczp4c2k9Imh0dHA6Ly93d3cudzMub3JnLzIwMDEvWE1MU2NoZW1hLWluc3RhbmNlIiB4c2k6dHlwZT0ieHM6c3RyaW5nIj5leGFtcGxlLmNvbTwvc2FtbDI6QXR0cmlidXRlVmFsdWU%2BPC9zYW1sMjpBdHRyaWJ1dGU%2BPC9zYW1sMjpBdHRyaWJ1dGVTdGF0ZW1lbnQ%2BPC9zYW1sMjpBc3NlcnRpb24%2BPC9zYW1sMnA6UmVzcG9uc2U%2B&Signature=LeMNm3aevRONrMuFm9o9GJvkF%2Ffe3KdO9j7cU9bMS0YB5IxYzo7uSE6Kgt7dLkUC41puWhTg8lP861HqeAPUhwvoRIvRxac2aa3euPpOz%2BvcWepAkYTQuVxznH5gn24qYRIiBflWlVgcw7iGUHeCPP2Gk9Pf5pFaGnFeSc2CR47in1sq0tp1qTUSWTdADPV4S%2FK5njRLFXBYcO9YwHafFjVlEtMgeWyUxPpSBFuClpVfF8T91O3X43Q444yP4tJz7cEntI6FzRCH62N1lvz0bXz3Z6JKQ9G8MfOwvGNAIfC72cwCWyewUPRzrFR4Gw7ZV4ZYSLcMlVpGxKmxVv7o0A%3D%3D&SigAlg=http%3A%2F%2Fwww.w3.org%2F2001%2F04%2Fxmldsig-more%23rsa-sha256&KeyInfo=PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48ZHM6S2V5SW5mbyB4bWxuczpkcz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyI%2BPGRzOlg1MDlEYXRhPjxkczpYNTA5Q2VydGlmaWNhdGU%2BTUlJREV6Q0NBZnVnQXdJQkFnSUpBS29LL2hlQmpjT1lNQTBHQ1NxR1NJYjNEUUVCQlFVQU1DQXhIakFjQmdOVkJBb01GVTl5WjJGdQ0KYVhwaGRHbHZiaXdnUTA0OVQwbEVRekFlRncweE5URXhNVEV4TURFeU1UVmFGdzB5TlRFeE1UQXhNREV5TVRWYU1DQXhIakFjQmdOVg0KQkFvTUZVOXlaMkZ1YVhwaGRHbHZiaXdnUTA0OVQwbEVRekNDQVNJd0RRWUpLb1pJaHZjTkFRRUJCUUFEZ2dFUEFEQ0NBUW9DZ2dFQg0KQU5CR3dKL3FwVFFOaVNnVWdsU0UyVXpFa1Vvdyt3UzhyNjdldHhvRWhsekpaZmdLL2s1VGZHMXdJQ0RxYXBIQXhFVmdVTTEwYUJIUg0KY3ROb2NBNXdtbEh0eGRpZGh6Ulpyb3FId3BLeTJCbXNLWDVaMm9LMjVSTHBzeXVzQjFLcm9lbWdBL0NqVW5JNnJJTDF4eEZuM0t5Tw0KRmgxWkJMVVF0S05RZU1TN0hGR2dTREFwK3NYdVRGdWp6MTJMRkR1Z1gwVDBLQjVhMSswbDh5MFBFYTB5R2Exb2k2c2VPTng4NDlaSA0KeE0wUFJ2VXVuV2t1VE0rZm9aMGpacEZhcFhlMDJ5V01xaGMvMmlZTWllRS8zR3ZPZ3VKY2hKdDZSK2N1dDhWQmI2dWJLVUlHSzdwbQ0Kb3EvVEI2RFZYcHZzSHFzREpYZWNoeGNpY3U0cGRLVkRIU2VjODUwQ0F3RUFBYU5RTUU0d0hRWURWUjBPQkJZRUZLN1Jxam9vZFNZVg0KWEdUVkVkTGYza0pmbFAvc01COEdBMVVkSXdRWU1CYUFGSzdScWpvb2RTWVZYR1RWRWRMZjNrSmZsUC9zTUF3R0ExVWRFd1FGTUFNQg0KQWY4d0RRWUpLb1pJaHZjTkFRRUZCUUFEZ2dFQkFETlpreGxGWGg0RjQ1bXVDYm5RZCtXbWFYbEd2Yjl0a1V5QUl4Vkw4QUl1OEoxOA0KRjQyMHZwbkdwb1VBRStIeTNldkJtcDJua3JGQWdtcjA1NWZBanBIZVpGZ0RaQkFQQ3dZZDNUTk1EZVN5TXRhM0thK29TN0dSRkRlUA0Ka01FbStrSDQvcklUTktVRjFzT3ZXQlRTb3drOVR1ZEVEeUZxZ0dudGNkdS9sL3pSeHZ4MzN5M0xNRzVVU0QweDRYNElLalJyUk4xQg0KYmNLZ2k4ZHExMEMzamRxTmFuY1R1UG9xVDNXV3pSdlZ0Qi9xMzRCN0Y3NC82SnpnRW9PQ0VIdWZCTXA0WkZ1NTRQMHlFR3RXZlR3VA0KenVvWm9ickNoVlZCdDR3L1haYWdyUnRVQ0ROd1JwSE5icGp4WXVkYnFMcXBpMU1RcFY5b2h0L0JwVEhWSkcyaTBybz08L2RzOlg1MDlDZXJ0aWZpY2F0ZT48L2RzOlg1MDlEYXRhPjwvZHM6S2V5SW5mbz4%3D

response:

    
    
    HTTP/1.1 302 
    X-Content-Type-Options: nosniff
    X-XSS-Protection: 1; mode=block
    Cache-Control: no-cache, no-store, max-age=0, must-revalidate
    Pragma: no-cache
    Expires: 0
    X-Frame-Options: DENY
    Location: http://192.168.0.104:9090/user.html?force-authn=true
    Content-Length: 0
    Date: Sat, 22 Oct 2022 10:30:12 GMT
    Connection: close

这一步一共发送了三个参数:

  * SAMLResponse: IDP认证用户成功之后发送给SP的响应内容
  * SigAlg: 签名算法，这里是用HTTP-POST来传输数据内容，为了保证接收到的数据没有被修改过，对SAMLResponse这一堆字符串进行的签名
  * KeyInfo: IDP的公钥，IDP使用自己的私钥对SAMLResponse那一堆字符串签名，然后将自己的公钥传输过去

当SP校验AuthnResponse成功时，会正常显示访问的服务。这里看下AuthnResponse解码并格式化后的内容:

    
    
    <?xml version="1.0" encoding="utf-8"?>
    
    <saml2p:Response xmlns:saml2p="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:xs="http://www.w3.org/2001/XMLSchema" Destination="http://192.168.0.104:9090/saml/SSO" ID="_c50c243f-a606-4a43-9486-eaec152c2c11" InResponseTo="ahgg4a45deh9i67h0f2iedga0755g" IssueInstant="2022-10-22T10:30:12.544Z" Version="2.0">
      <saml2:Issuer xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://mock-idp</saml2:Issuer>
      <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
        <ds:SignedInfo>
          <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
          <ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
          <ds:Reference URI="#_c50c243f-a606-4a43-9486-eaec152c2c11">
            <ds:Transforms>
              <ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
              <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#">
                <ec:InclusiveNamespaces xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#" PrefixList="xs"></ec:InclusiveNamespaces>
              </ds:Transform>
            </ds:Transforms>
            <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
            <ds:DigestValue>f4BTE7H1QRBOmC1nRpmw0sOFgDk+uLgG7q/cMhkiD5o=</ds:DigestValue>
          </ds:Reference>
        </ds:SignedInfo>
        <ds:SignatureValue>Me01OUam5leJF4wSPeM3q+B+mKmwJRULaOY79hXwxqUbDPmwlSJb+1tZ1+nYtiNUEkYudPXZOkf8SdlUhDUKILvtwfogXTJletWwNVO0y6hKHXqmnSazKZeR+tk1bDa5/Jt2GIwZQNfA3aE1BRNiJedJBLw91AO02ngEnRXVctVtU4XwHlrXbTUacd44+hDrWBonQbwRf0FqRYve3B4JyubJP02kfg/tHa9T7WOsC/hOhKg+W6TG32K80mtBxY50B5FAhHjYD5YqDZ7FU/gNAyypj8UXlM0ot7n6oq/XvcuYL9/0C0ze3U/vesNs8LC1j7yCkRQyxAlylIHRbv8Akw==</ds:SignatureValue>
        <ds:KeyInfo>
          <ds:X509Data>
            <ds:X509Certificate>MIIDEzCCAfugAwIBAgIJAKoK/heBjcOYMA0GCSqGSIb3DQEBBQUAMCAxHjAcBgNVBAoMFU9yZ2Fu aXphdGlvbiwgQ049T0lEQzAeFw0xNTExMTExMDEyMTVaFw0yNTExMTAxMDEyMTVaMCAxHjAcBgNV BAoMFU9yZ2FuaXphdGlvbiwgQ049T0lEQzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEB ANBGwJ/qpTQNiSgUglSE2UzEkUow+wS8r67etxoEhlzJZfgK/k5TfG1wICDqapHAxEVgUM10aBHR ctNocA5wmlHtxdidhzRZroqHwpKy2BmsKX5Z2oK25RLpsyusB1KroemgA/CjUnI6rIL1xxFn3KyO Fh1ZBLUQtKNQeMS7HFGgSDAp+sXuTFujz12LFDugX0T0KB5a1+0l8y0PEa0yGa1oi6seONx849ZH xM0PRvUunWkuTM+foZ0jZpFapXe02yWMqhc/2iYMieE/3GvOguJchJt6R+cut8VBb6ubKUIGK7pm oq/TB6DVXpvsHqsDJXechxcicu4pdKVDHSec850CAwEAAaNQME4wHQYDVR0OBBYEFK7RqjoodSYV XGTVEdLf3kJflP/sMB8GA1UdIwQYMBaAFK7RqjoodSYVXGTVEdLf3kJflP/sMAwGA1UdEwQFMAMB Af8wDQYJKoZIhvcNAQEFBQADggEBADNZkxlFXh4F45muCbnQd+WmaXlGvb9tkUyAIxVL8AIu8J18 F420vpnGpoUAE+Hy3evBmp2nkrFAgmr055fAjpHeZFgDZBAPCwYd3TNMDeSyMta3Ka+oS7GRFDeP kMEm+kH4/rITNKUF1sOvWBTSowk9TudEDyFqgGntcdu/l/zRxvx33y3LMG5USD0x4X4IKjRrRN1B bcKgi8dq10C3jdqNancTuPoqT3WWzRvVtB/q34B7F74/6JzgEoOCEHufBMp4ZFu54P0yEGtWfTwT zuoZobrChVVBt4w/XZagrRtUCDNwRpHNbpjxYudbqLqpi1MQpV9oht/BpTHVJG2i0ro=</ds:X509Certificate>
          </ds:X509Data>
        </ds:KeyInfo>
      </ds:Signature>
      <saml2p:Status>
        <saml2p:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
      </saml2p:Status>
      <saml2:Assertion xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion" ID="_b3a92133-c190-4972-8918-d6a58a75abb4" IssueInstant="2022-10-22T10:30:12.549Z" Version="2.0">
        <saml2:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://mock-idp</saml2:Issuer>
        <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
          <ds:SignedInfo>
            <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
            <ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
            <ds:Reference URI="#_b3a92133-c190-4972-8918-d6a58a75abb4">
              <ds:Transforms>
                <ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
                <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#">
                  <ec:InclusiveNamespaces xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#" PrefixList="xs"></ec:InclusiveNamespaces>
                </ds:Transform>
              </ds:Transforms>
              <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
              <ds:DigestValue>uQjVT+t142IInUWHcPdNka2xP46+gUNx+W0lfzs2fB8=</ds:DigestValue>
            </ds:Reference>
          </ds:SignedInfo>
          <ds:SignatureValue>dosUeZ+/7/sG4mbWGXmUW6yi2hlzx00REmVd1tvnIjm10dbzIvzfjJGW3yZ8FPW6Vj/ZCW/bmZY/vKSOO3T3S2XCPiKPERS5Z/4LILh2hEkWSIGehXTfmDxwsCnyDOK1Ejy7Exjt8TbMWiD9pDQKXiGykXnroa8I+KI9MHMKdP13SlxZuHD93lmwmapXax6cw4Zm8MB1v9CDgUfFRV4jagvTYNqrKVt7emBbnc2xxQtiaLd3q6NNQgUXNAS5W1BoQRJwL3CjJ72sPTYQxOHdqqcLQNjMnpRX7Rdq80e8ddz63kfVkl0UpRioYKQTFp8S6e2r1CoIOjM0pa3heNkRsw==</ds:SignatureValue>
        </ds:Signature>
        <saml2:Subject>
          <saml2:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified">wewe</saml2:NameID>
          <saml2:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
            <saml2:SubjectConfirmationData InResponseTo="ahgg4a45deh9i67h0f2iedga0755g" NotOnOrAfter="2022-10-22T18:30:12.546Z" Recipient="http://192.168.0.104:9090/saml/SSO"/>
          </saml2:SubjectConfirmation>
        </saml2:Subject>
        <saml2:Conditions NotBefore="2022-10-22T10:27:12.546Z" NotOnOrAfter="2022-10-22T10:33:12.546Z">
          <saml2:AudienceRestriction>
            <saml2:Audience>http://mock-sp</saml2:Audience>
          </saml2:AudienceRestriction>
        </saml2:Conditions>
        <saml2:AuthnStatement AuthnInstant="2022-10-22T10:30:12.547Z">
          <saml2:AuthnContext>
            <saml2:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:Password</saml2:AuthnContextClassRef>
            <saml2:AuthenticatingAuthority>http://mock-idp</saml2:AuthenticatingAuthority>
          </saml2:AuthnContext>
        </saml2:AuthnStatement>
        <saml2:AttributeStatement>
          <saml2:Attribute Name="urn:mace:dir:attribute-def:displayName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
            <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John Doe</saml2:AttributeValue>
          </saml2:Attribute>
          <saml2:Attribute Name="urn:mace:dir:attribute-def:uid" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
            <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">wewe</saml2:AttributeValue>
          </saml2:Attribute>
          <saml2:Attribute Name="urn:mace:dir:attribute-def:cn" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
            <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John Doe</saml2:AttributeValue>
          </saml2:Attribute>
          <saml2:Attribute Name="urn:mace:dir:attribute-def:sn" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
            <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">Doe</saml2:AttributeValue>
          </saml2:Attribute>
          <saml2:Attribute Name="urn:mace:dir:attribute-def:eduPersonPrincipalName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
            <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">j.doe@example.com</saml2:AttributeValue>
          </saml2:Attribute>
          <saml2:Attribute Name="urn:mace:dir:attribute-def:givenName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
            <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John</saml2:AttributeValue>
          </saml2:Attribute>
          <saml2:Attribute Name="urn:mace:dir:attribute-def:mail" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
            <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">j.doe@example.com</saml2:AttributeValue>
          </saml2:Attribute>
          <saml2:Attribute Name="urn:mace:terena.org:attribute-def:schacHomeOrganizationType" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
            <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">ererer</saml2:AttributeValue>
          </saml2:Attribute>
          <saml2:Attribute Name="urn:mace:terena.org:attribute-def:schacHomeOrganization" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
            <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">example.com</saml2:AttributeValue>
          </saml2:Attribute>
        </saml2:AttributeStatement>
      </saml2:Assertion>
    </saml2p:Response>

Response多了一个InResponseTo属性，这个值就是前面AuthnRequest的ID值，然后后面第一个子Signature标签含义同AuthnRequest一样，这里看下其他标签。

#### Status

IDP认证用户结果的标志，这里为success，表示用户认证成功。

#### Assertion

Assertion是断言的意思，这里面包含的是用户的一些基本信息和属性。

其中包含的Issuer标签代表的意思和AuthnRequest一样，Signature也是类似，不过签名的内容不一样，在后续代码细节分析会看到签的是哪一部分。

#### Subject

  * NameID: 标识符，其中的Format属性为unspecified，表示IdP为其定义了格式，并假设SP知道如何解析来自 IdP的格式数据响应。例如，IdP给出一个格式数据"UserName=XXXXX Country=US"，SP得到断言，可以解析得到UserName为"XXXXX"。这里我们就只是一个字符username字符串格式，表示用户名为wewe
  * SubjectConfirmation: 用户如何进行认证的，这里method使用的bearer方式
  * SubjectConfirmationData: InResponseTo表示响应给谁，NotOnOrAfter表示在这之前有效，Recipient表示接收端点
  * Conditions: 限定Assertion有效时间，其中的带Audience相关标签是接收者的一些信息
  * AuthnStatement: idp对用户认证使用方式，认证机构等信息
  * AttributeStatement: 和用户有关的一些属性

## 通过OpenSAML源码看SAML SSO细节

还是之前那个项目，这里着重看SP生成AuthnRequest和IDP生成AuthnResponse生成以及IDP收到AuthnRequest和SP收到AuthnResponse的处理，其中的签名和摘要以及涉及到的一些转换和校验部分是重点。

### SP生成AuthnRequest

到摘要处调用栈如下：

    
    
    calculateDigest:719, Reference (org.apache.xml.security.signature)
    generateDigestValue:406, Reference (org.apache.xml.security.signature)
    generateDigestValues:206, Manifest (org.apache.xml.security.signature)
    sign:609, XMLSignature (org.apache.xml.security.signature)
    signObject:77, Signer (org.opensaml.xml.signature)
    signMessage:193, BaseSAML2MessageEncoder (org.opensaml.saml2.binding.encoding)
    doEncode:109, HTTPPostEncoder (org.opensaml.saml2.binding.encoding)
    encode:52, BaseMessageEncoder (org.opensaml.ws.message.encoder)
    sendMessage:224, SAMLProcessorImpl (org.springframework.security.saml.processor)
    sendMessage:42, ConfigurableSAMLProcessor (mujina.sp)
    sendMessage:148, AbstractProfileBase (org.springframework.security.saml.websso)
    sendAuthenticationRequest:107, WebSSOProfileImpl (org.springframework.security.saml.websso)
    initializeSSO:225, SAMLEntryPoint (org.springframework.security.saml)
    commence:152, SAMLEntryPoint (org.springframework.security.saml)
    sendStartAuthentication:215, ExceptionTranslationFilter

调用栈就是整个生成AuthnRequest的流程，这里主要看下摘要，摘的是哪一部分:

![](https://images.seebug.org/content/images/2022/11/b6c52332-a687-43c4-acae-66397b1e7f6f.png-w331s)

    
    
    <saml2p:AuthnRequest xmlns:saml2p="urn:oasis:names:tc:SAML:2.0:protocol" AssertionConsumerServiceURL="http://192.168.0.104:9090/saml/SSO" Destination="http://192.168.0.104:8080/SingleSignOnService" ForceAuthn="true" ID="a534936dfbc0a19e32g890f5f33i4ee" IsPassive="false" IssueInstant="2022-10-31T13:16:48.841Z" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Version="2.0"><saml2:Issuer xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion">http://mock-sp</saml2:Issuer></saml2p:AuthnRequest>

xml内容是经过两个transform处理之后的内容:

![](https://images.seebug.org/content/images/2022/11/365ee642-aef5-4148-9edc-58389f17cfb2.png-w331s)

`Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"`转换器会排除AuthnRequest中的Signature标签的内容，`Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"`会将xml规范化(移除注释等一些操作)并压缩，最后得到的内容就如上了。

然后对这一部分内容进行SHA-256摘要算法:

![](https://images.seebug.org/content/images/2022/11/0e5e2dd9-c953-400e-9b5a-05db8da78aff.png-w331s)

后续进行签名，到签名处调用栈如下:

    
    
    engineSign:190, RSASignature (sun.security.rsa)
    engineSign:1235, Signature$Delegate (java.security)
    sign:598, Signature (java.security)
    engineSign:133, SignatureBaseRSA (org.apache.xml.security.algorithms.implementations)
    sign:174, SignatureAlgorithm (org.apache.xml.security.algorithms)
    sign:628, XMLSignature (org.apache.xml.security.signature)
    signObject:77, Signer (org.opensaml.xml.signature)
    signMessage:193, BaseSAML2MessageEncoder (org.opensaml.saml2.binding.encoding)
    doEncode:109, HTTPPostEncoder (org.opensaml.saml2.binding.encoding)
    encode:52, BaseMessageEncoder (org.opensaml.ws.message.encoder)
    sendMessage:224, SAMLProcessorImpl (org.springframework.security.saml.processor)
    sendMessage:42, ConfigurableSAMLProcessor (mujina.sp)
    sendMessage:148, AbstractProfileBase (org.springframework.security.saml.websso)
    sendAuthenticationRequest:107, WebSSOProfileImpl

![](https://images.seebug.org/content/images/2022/11/51cf7d0a-5b5f-4d5f-8074-d798fedb65cb.png-w331s)

使用SP的私钥(在application.yml文件中有配置)，对SingedInfo进行签名:

    
    
    <ds:SignedInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#"><ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:CanonicalizationMethod><ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"></ds:SignatureMethod><ds:Reference URI="#a5856d7b1876hii3i40cda0c3fc38h"><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></ds:Transform><ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:Transform></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"></ds:DigestMethod><ds:DigestValue>UEOuyyx4dWr3X0XoQryWQfSzNpXleQ5zSg9LayAEX7E=</ds:DigestValue></ds:Reference></ds:SignedInfo>

经过这些处理之后，看到的AuthnRequest的xml就是之前抓包解码看到的了:

![](https://images.seebug.org/content/images/2022/11/331e950b-fd20-4987-b149-61ce5d5b24d1.png-w331s)

最后还有一个http post传输base64编码处理，所以抓包看到的也是base64编码。

### IDP收到AuthnRequest的处理

在`mujina.idp.SAMLMessageHandler#extractSAMLMessageContext`中对SP发送的AuthnRequest进行了提取并校验:

![](https://images.seebug.org/content/images/2022/11/7e4f8b3a-a171-49ca-943d-dfdfba928f10.png-w331s)

对AuthnRequest校验的安全策略只检测IssueInstant是否过期，没有其他策略。然后还有validatorSuites检测，可以看到有两种类型的validator，每个下面有多个标签对应的具体validator。不过测试发现这里IDP没有对AuthnRequest进行证书校验、签名校验、摘要校验的操作。

### IDP生成AuthnResponse

对Assertion签名，调用栈如下:

    
    
    calculateDigest:719, Reference (org.apache.xml.security.signature)
    generateDigestValue:406, Reference (org.apache.xml.security.signature)
    generateDigestValues:206, Manifest (org.apache.xml.security.signature)
    sign:609, XMLSignature (org.apache.xml.security.signature)
    signObject:77, Signer (org.opensaml.xml.signature)
    signAssertion:153, SAMLBuilder (mujina.saml)
    sendAuthnResponse:123, SAMLMessageHandler (mujina.idp)
    doSSO:77, SsoController (mujina.idp)
    singleSignOnServicePost:55, SsoController (mujina.idp)

摘要内容如下:

![](https://images.seebug.org/content/images/2022/11/6c8d3fbc-6eb7-4aae-b54f-dab0eb0f1d0e.png-w331s)

摘要内容:

    
    
    <saml2:Assertion xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:xs="http://www.w3.org/2001/XMLSchema" ID="_2f36cf83-55f7-415e-ba10-5d8188c58e31" IssueInstant="2022-11-01T14:00:37.681Z" Version="2.0"><saml2:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://mock-idp</saml2:Issuer><saml2:Subject><saml2:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified">111111</saml2:NameID><saml2:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer"><saml2:SubjectConfirmationData InResponseTo="a4ebjf264d9b7dja4hicahibc3d2jf8" NotOnOrAfter="2022-11-01T22:00:37.677Z" Recipient="http://192.168.0.104:9090/saml/SSO"></saml2:SubjectConfirmationData></saml2:SubjectConfirmation></saml2:Subject><saml2:Conditions NotBefore="2022-11-01T13:57:37.678Z" NotOnOrAfter="2022-11-01T14:03:37.678Z"><saml2:AudienceRestriction><saml2:Audience>http://mock-sp</saml2:Audience></saml2:AudienceRestriction></saml2:Conditions><saml2:AuthnStatement AuthnInstant="2022-11-01T14:00:37.678Z"><saml2:AuthnContext><saml2:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:Password</saml2:AuthnContextClassRef><saml2:AuthenticatingAuthority>http://mock-idp</saml2:AuthenticatingAuthority></saml2:AuthnContext></saml2:AuthnStatement><saml2:AttributeStatement><saml2:Attribute Name="urn:mace:dir:attribute-def:displayName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John Doe</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:uid" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">111111</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:oasis:names:tc:SAML:attribute:subject-id" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">sdsdsdsd</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:cn" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John Doe</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:sn" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">Doe</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:eduPersonPrincipalName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">j.doe@example.com</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:givenName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:mail" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">j.doe@example.com</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:terena.org:attribute-def:schacHomeOrganization" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">example.com</saml2:AttributeValue></saml2:Attribute></saml2:AttributeStatement></saml2:Assertion>

这里也是采用了和之前SP生成AuthnRequest相同的transform算法，所以排除了Signature标签以及进行了规范化处理。后面还会对SingedInfo进行签名，和AuthnRequest签名方式一样的方式，签名的私钥在application.yml文件中有配置。

后面还会对Response标签进行一次摘要和签名:

    
    
    calculateDigest:719, Reference (org.apache.xml.security.signature)
    generateDigestValue:406, Reference (org.apache.xml.security.signature)
    generateDigestValues:206, Manifest (org.apache.xml.security.signature)
    sign:609, XMLSignature (org.apache.xml.security.signature)
    signObject:77, Signer (org.opensaml.xml.signature)
    signMessage:193, BaseSAML2MessageEncoder (org.opensaml.saml2.binding.encoding)
    signMessage:97, HTTPPostSimpleSignEncoder (org.opensaml.saml2.binding.encoding)
    doEncode:109, HTTPPostEncoder (org.opensaml.saml2.binding.encoding)
    encode:52, BaseMessageEncoder (org.opensaml.ws.message.encoder)
    sendAuthnResponse:145, SAMLMessageHandler (mujina.idp)
    doSSO:77, SsoController (mujina.idp)
    singleSignOnServicePost:55, SsoController (mujina.idp)

摘要内容:

    
    
    <saml2p:Response xmlns:saml2p="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:xs="http://www.w3.org/2001/XMLSchema" Destination="http://192.168.0.104:9090/saml/SSO" ID="_cac5ad52-f303-4356-b061-177f2bc4247c" InResponseTo="a4ebjf264d9b7dja4hicahibc3d2jf8" IssueInstant="2022-11-01T14:00:37.675Z" Version="2.0"><saml2:Issuer xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://mock-idp</saml2:Issuer><saml2p:Status><saml2p:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"></saml2p:StatusCode></saml2p:Status><saml2:Assertion xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion" ID="_2f36cf83-55f7-415e-ba10-5d8188c58e31" IssueInstant="2022-11-01T14:00:37.681Z" Version="2.0"><saml2:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://mock-idp</saml2:Issuer><ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:CanonicalizationMethod><ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"></ds:SignatureMethod><ds:Reference URI="#_2f36cf83-55f7-415e-ba10-5d8188c58e31"><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></ds:Transform><ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"><ec:InclusiveNamespaces xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#" PrefixList="xs"></ec:InclusiveNamespaces></ds:Transform></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"></ds:DigestMethod><ds:DigestValue>XUf3yZB7j4wKYhl3K7Cp4dhfe/E0qKs3a8at+WjZ4Sc=</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>i97x4tGq3whwLpqCIXRsLAy2pn0Wx0+yuHBreiMTwGm4Ekao3DfFvzSfPN5rMVATV59ntBonmUayrZExxsEyVm2xMSFBBEx0JO2stJ6dx2XXPgIiHr7tV5oH9V9wK5OwG1rAHRDMyg4IBCQzLlQrrBZwMCAu/G9FaSw0vBq/COSS8YBrW5/vBH4tS9/NdtTQiXiDoXnGSVYZvXtE0W5anNAUiDytmQhai4dy4Yim/rtKRjIXJVAWD9djCcuR7N//7MWRw1XjWlr1RTwm2TtVvGEY5FL5fVRjdsXJdcc7HNq3UUMQnBpY5RKe+xhri8oZqBc6dmyF96PEUY54EVTdWw==</ds:SignatureValue></ds:Signature><saml2:Subject><saml2:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified">111111</saml2:NameID><saml2:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer"><saml2:SubjectConfirmationData InResponseTo="a4ebjf264d9b7dja4hicahibc3d2jf8" NotOnOrAfter="2022-11-01T22:00:37.677Z" Recipient="http://192.168.0.104:9090/saml/SSO"></saml2:SubjectConfirmationData></saml2:SubjectConfirmation></saml2:Subject><saml2:Conditions NotBefore="2022-11-01T13:57:37.678Z" NotOnOrAfter="2022-11-01T14:03:37.678Z"><saml2:AudienceRestriction><saml2:Audience>http://mock-sp</saml2:Audience></saml2:AudienceRestriction></saml2:Conditions><saml2:AuthnStatement AuthnInstant="2022-11-01T14:00:37.678Z"><saml2:AuthnContext><saml2:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:Password</saml2:AuthnContextClassRef><saml2:AuthenticatingAuthority>http://mock-idp</saml2:AuthenticatingAuthority></saml2:AuthnContext></saml2:AuthnStatement><saml2:AttributeStatement><saml2:Attribute Name="urn:mace:dir:attribute-def:displayName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John Doe</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:uid" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">111111</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:oasis:names:tc:SAML:attribute:subject-id" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">sdsdsdsd</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:cn" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John Doe</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:sn" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">Doe</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:eduPersonPrincipalName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">j.doe@example.com</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:givenName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:mail" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">j.doe@example.com</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:terena.org:attribute-def:schacHomeOrganization" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">example.com</saml2:AttributeValue></saml2:Attribute></saml2:AttributeStatement></saml2:Assertion></saml2p:Response>

**注意此时摘要包含了Assertion以及Assertion所有子标签，Response中的Signature标签也因为应用了和之前相同的transform，所以不包含在摘要中**
。后面还会对SingedInfo进行签名后，最终的xml就是抓包看到的样子。

#### SP收到AuthnResponse的处理

    
    
    evaluate:51, BasicSecurityPolicy (org.opensaml.ws.security.provider)
    processSecurityPolicy:132, BaseMessageDecoder (org.opensaml.ws.message.decoder)
    decode:83, BaseMessageDecoder (org.opensaml.ws.message.decoder)
    decode:70, BaseSAML2MessageDecoder (org.opensaml.saml2.binding.decoding)
    retrieveMessage:105, SAMLProcessorImpl (org.springframework.security.saml.processor)
    retrieveMessage:172, SAMLProcessorImpl (org.springframework.security.saml.processor)
    attemptAuthentication:85, SAMLProcessingFilter (org.springframework.security.saml)
    doFilter:223, AbstractAuthenticationProcessingFilter (org.springframework.security.web.authentication)
    doFilter:213, AbstractAuthenticationProcessingFilter (org.springframework.security.web.authentication)

主要的校验点是两个securityPolicies:

![](https://images.seebug.org/content/images/2022/11/7d4469bb-840a-42e2-a959-b77961cc39cb.png-w331s)

`SAML2HTTPPostSimpleSignRule`是校验post传输中数据的签名，这个很好理解。

`SAMLProtocolMessageXMLSignatureSecurityPolicyRule`是校验Saml
Response中的签名，首先会从本地提取IDP的证书(在`classpath:metadata/mujina.local.idp.metadata.xml`中有配置)，这里并没有从传过来的Response中提取证书，而是用配置好的信任的证书:

![](https://images.seebug.org/content/images/2022/11/1330d369-9e30-46dc-9013-a3d7143b8c43.png-w331s)

调用栈如下:

    
    
    checkSignatureValue:723, XMLSignature (org.apache.xml.security.signature)
    validate:69, SignatureValidator (org.opensaml.xml.signature)
    verifySignature:142, BaseSignatureTrustEngine (org.opensaml.xml.signature.impl)
    validate:100, BaseSignatureTrustEngine (org.opensaml.xml.signature.impl)
    validate:100, ExplicitKeySignatureTrustEngine (org.opensaml.xml.signature.impl)
    validate:49, ExplicitKeySignatureTrustEngine (org.opensaml.xml.signature.impl)
    evaluate:104, BaseTrustEngineRule (org.opensaml.ws.security.provider)
    evaluate:91, BaseTrustEngineRule (org.opensaml.ws.security.provider)
    doEvaluate:128, SAMLProtocolMessageXMLSignatureSecurityPolicyRule (org.opensaml.common.binding.security)
    evaluate:107, SAMLProtocolMessageXMLSignatureSecurityPolicyRule (org.opensaml.common.binding.security)
    evaluate:51, BasicSecurityPolicy (org.opensaml.ws.security.provider)
    processSecurityPolicy:132, BaseMessageDecoder (org.opensaml.ws.message.decoder)
    decode:83, BaseMessageDecoder (org.opensaml.ws.message.decoder)
    decode:70, BaseSAML2MessageDecoder (org.opensaml.saml2.binding.decoding)
    retrieveMessage:105, SAMLProcessorImpl (org.springframework.security.saml.processor)
    retrieveMessage:172, SAMLProcessorImpl (org.springframework.security.saml.processor)
    attemptAuthentication:85, SAMLProcessingFilter (org.springframework.security.saml)
    doFilter:223, AbstractAuthenticationProcessingFilter (org.springframework.security.web.authentication)
    doFilter:213, AbstractAuthenticationProcessingFilter

![](https://images.seebug.org/content/images/2022/11/e865014c-993b-4e76-b164-dfbe2520e381.png-w331s)

从证书中提取public key，用public
key对SignatureValue解密，解密值是Signedinfo的摘要，对Signedinfo重新摘要，和解密的摘要值进行对比。接着还会对比DigestValue摘要值，这个值是Response中除了Response子标签Signature的摘要，这里的处理是重新计算这部分的摘要，然后和DigestValue进行对比:

![](https://images.seebug.org/content/images/2022/11/1163fe87-2270-4f2e-aa15-2a4a08e97d7f.png-w331s)

当然过程中还存在其他校验，例如status的校验等。

后面还会对Assertion进行校验:

    
    
    processAuthenticationResponse:301, WebSSOProfileConsumerImpl (org.springframework.security.saml.websso)
    authenticate:88, SAMLAuthenticationProvider (org.springframework.security.saml)
    authenticate:182, ProviderManager (org.springframework.security.authentication)
    attemptAuthentication:92, SAMLProcessingFilter (org.springframework.security.saml)
    doFilter:223, AbstractAuthenticationProcessingFilter (org.springframework.security.web.authentication)
    doFilter:213, AbstractAuthenticationProcessingFilter (org.springframework.security.web.authentication)

![](https://images.seebug.org/content/images/2022/11/9e9d9454-8631-48d1-95b3-49a5b09a1357.png-w331s)

校验方式和Response中的校验一致，证书用的本地配置的而不是从Assertion中提取，校验了Assertion中的Sianature、摘要信息，还校验了Conditions是否过期，Subject中的接收者是否是预期的接收端点等校验，这一系列校验之后，就成功返回一个Credential，里面包含了用户的一些信息。

### SAML校验过程中存在的安全隐患

对于签名问题，在[Bypassing SAML 2.0 SSO with XML Signature
Attacks](https://research.aurainfosec.io/bypassing-saml20-SSO/)这篇文章中提到的几个问题感觉很好的说明了SAML可能存在的安全隐患:

  * 签名是否是必须的？可能一些SAML的实现从请求中判断是否携带了Signature，携带了就校验，没携带就不校验；或者设置一个签名校验开关让开发者进行处理，而开发者可能并不熟悉没有打开强制验证等情况
  * 签名是否经过验证？虽然生成AuthnRequest和Response都进行了签名，但是各自收到SAML消息时没有进行签名验证的情况
  * 签名是否来自正确的签名者？X509Certificate包含签名者信息，如果没有校验是否是信任的证书，那么可以伪造证书，然后对SAML消息进行篡改，重新签名
  * 是否对响应中正确的部分进行签名？SAML标准允许的签名存在的位置仅有两处:Response、Assertion，没有人仅仅为了使用SAML，就完整地实现复杂的XML签名机制。这一标准是通用的，标准的实现及其软件库也是如此。所以如果某些库如果验证签名没有验证到正确的位置，就可以将签名引用到文档的不同位置，并且让接受者认为签名是有效的，造成XSW攻击

Burp中有一个SAML Raider插件，可以很方便的进行修改和伪造SAML攻击，不过有时候也需要手动构造，所以理解SAML的处理流程也是有必要的。

在《Hacking the Cloud With SAML》中提到一个新的攻击面，就是SignedInfo的校验和摘要校验的先后顺序问题，从上面
**SP收到AuthnResponse的处理**
一节可以看到，摘要校验是会先经过transform处理的，而摘要的计算不包括Signature标签内容，所以如果先进行了摘要校验，那么transforms下的操作空间就不受限制，可以任意设置transform，这个ppt中也提到了两个CVE(CVE-2022-34716、CVE-2022-34169)，是transform进行攻击很好的例子。

#### Demo项目中存在的问题

Demo中使用的OpenSAML是比较新，经过测试，SP收到AuthnResponse的处理是没有上面的问题的，他的校验顺序如下:

  * 使用本地信任的证书
  * 校验SignedInfo
  * 校验摘要

所以Response的校验没有问题。

但是IDP收到AuthnRequest的处理只校验了Instant是否过期，不过因为没有处理签名和摘要的流程，所以不存在其他攻击的可能。不过IDP是从AuthnRequest拿的AssertionConsumerServiceURL，没有校验是否是预期的，所以后面将Reponse发送回去时，会导致一个SSRF问题，这一块的处理应该是开发人员来做的，不是库的问题。

## 最后

由于用的是比较新版的OpenSAML进行调试，在调试过程中可以发现一些修复痕迹，例如对XSW、ds:Object元素攻击的修复等。之前看到SAML或者SAML的漏洞报告就头大，因为里面涉及到了签名和摘要，而且还是对XML签名和摘要，是像字符串那样摘要和签名吗，不是的话又是如何签名XML，如何摘要XML，如何校验XML，我要攻击怎么篡改伪造，需要改哪些数据，怎么重新计算签名和摘要等，现在调试了一遍算是很清晰了。

## 参考

<https://research.aurainfosec.io/bypassing-saml20-SSO/>

<https://drive.google.com/file/d/1p1tTTIjg3RoJecYSU3CetvNw6-ZZdMXn/view>

<https://github.com/OpenConext/Mujina>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2006/>

