**Author: Longofo@Knownsec 404 Team  
Chinese version: <https://paper.seebug.org/2006/>**

SAML began in 2001, and the final version of SAML 2.0 was released in 2005.
Since then, no major version has been released. SAML 2.0 has continued to the
present. Nowadays, SAML is outdated, and OAuth is used more in SSO. I have
seen some SAML vulnerability reports on some vulnerability platforms, and it
still appears in some large application products. A recent topic, "Hacking the
Cloud With SAML"[[1]](https://drive.google.
com/file/d/1p1tTTIjg3RoJecYSU3CetvNw6-ZZdMXn/view), also mentioned that
archaeological study is still worthwhile, at least some of its concepts are
still in use.

### SAML 2.0

**SAML** : Security Assertion Markup Language，a language for security
assertion markup。

SAML application：

  * SSO Single Sign-ON
  * Federated Identity
  * Use SAML within other architectures such as WS-Security

Subsequent content is mainly part of SAML SSO.

Three parties in the SAML protocol：Browser, IDP(Identity Provider)，SP(Service
provider), and the communication sequence, encryption method, and transmission
data format of these three parties.

The basic authentication process is as follows：

![](https://images.seebug.org/content/images/2022/11/9958baff-5619-4c15-97b1-c5a7bc8e0211.png-w331s)

Just take a rough look at the flow chart, and you will see the details of each
link in the OpenSAML case later.

### See the SAML SSO authentication process through the OpenSAML request
package

**OpenSAML** is an open source implementation of the SAML protocol. I found an
SSO [demo](https://github.com/OpenConext/Mujina) implemented with OpenSAML in
github, using HTTP-POST to transmit SAML, there are Hundreds of stars. Run the
project and log in normally to see the complete communication package process.
Port 9090 is SP, and port 8080 is IDP.

#### User access to SP service

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

Return to the SP login page, and the user click Login.

#### SP returns redirect

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

The IDP login URL is returned with AuthnRequest, which is base64 encoded.
After unpacking and formatting, it is as follows:

    
    
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

Take a look at the meaning of each tag and attribute in turn.

##### AuthnRequest

The SP communicates to the IDP that I want to authenticate a user, which does
not contain user information, but contains the basic information of the SP.

  * AssertionConsumerServiceURL: Specify which URL of the SP to send the AuthnResponse to after the IDP authentication is successful.
  * Destination: Specify the endpoint for IDP authentication.
  * ForceAuthn: Fource authentication, even if it has been authenticated before, the browser carries the authenticated session. If this value is true, it will still re-authenticate.
  * ID: Random identification, mainly used to facilitate reference in other tags, such as Reference in SignedInfo.
  * IsPassive: Defaults to false . If true, the IdP cannot interact with the user through the browser, and the user cannot perceive the existence of the redirect.
  * IssueInstant: The time the request was issued.
  * ProtocolBinding: What to use to transport SAML messages, here is via HTTP POST
  * Version: here is 2.0 version.

##### Issuer

Used to identify the actual issuer of the AuthnRequest request message,
usually also in URI format.

##### Signature

The signature method in this case uses xmldsig (XML Signature). xmldsig is a
concept of xml signature rather than a specific algorithm. The specific
algorithm is in **SignedInfo**.

##### SignedInfo

  * CanonicalizationMethod: Normalization algorithm, the object is the content in the Signature tag, the xml-exc-c14n is an algorithm used to standardize the xml format.
  * SignatureMethod: Refers to what method is used to sign DigestValue, pay attention to the signature object is SignedInfo, and digest object is AuthnRequest.
  * Reference: Reference, here ID is the ID in the AuthnRequest, which means that other label information in the Reference will apply to the content of the AuthnRequest label and sub-labels.
  * Transforms: Multiple transforms can be specified to perform chain processing on the referenced object. For example, enveloped-signature adopts partial signature method, that is, the Signature tag in AuthnRequest is not included in the digest content when calculating the digest; the xml-exc-c14n algorithm is for The content in AuthnRequest is normalized.
  * DigestMethod: For the digest algorithm of AuthnRequest information, sha256 is similar to the md5 algorithm, one-way algorithm, irreversible, and digest calculation is performed in this way.
  * DigestValue: Digest value for AuthnRequest information.

##### SignatureValue

The signature result, where the signature object is the SignedInfo tag.

##### KeyInfo

Contains X509 public key certificate information. The public key in
**X509Certificate** will be used for the digest. After IDP receives the
AuthnRequest, it may use this public key to decrypt the signature information,
and then compare it with the digest value to see if the information is tamper.

**How to digest, which part is digested, and which part is signed, you will
see the details of the code in the subsequent analysis.**

#### Browser redirects to IDP

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

Here IDP will verify that the AuthnRequest information is correct, and then
redirect the user to the IDP's login page.

#### IDP returns to the login page

To save some space, the request and response information here will not be
posted, and the familiarity with the process will not be affected.

#### User enters account password to log in

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

The IDP verifies the user, the user authentication is successful, the
AuthnResponse is generated and cached in the session, and then redirected to
the SingleSignOnService. Later, the browser will use GET to request the
SingleSignOnService endpoint once.

#### Browser redirects to SingleSignOnService

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

In the response, the IDP returned the AuthnResponse content, along with two
other parameters.

#### Browser redirects to SP

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

This step sends a total of three parameters:

  * SAMLResponse: The content of the response sent to the SP after the IDP authenticates the user successfully
  * SigAlg: Signature algorithm, here is to use HTTP-POST to transmit data content. In order to ensure that the received data has not been modified, the SAMLResponse string is signed.
  * KeyInfo: SP's certificate, IDP uses its own private key to sign the bunch of strings in SAMLResponse, and then transmits its own public key When the SP verifies the AuthnResponse successfully, the accessed service will be displayed normally. Here's a look at the decoded and formatted content of AuthnResponse.

    
    
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

Response has an additional InResponseTo attribute. This value is the ID value
of the previous AuthnRequest, and then the meaning of the first sub-Signature
tag is the same as that of AuthnRequest. Let’s look at other tags here.

##### Status

The sign of the result of the IDP authentication user, here is success,
indicating that the user authentication is successful.

##### Assertion

Assertion means assertion, which contains some basic information and
attributes of the user.

The Issuer tag contained in it represents the same meaning as AuthnRequest,
and the Signature is also similar. However, the content of the signature is
different. You will see which part of the signature is signed in the
subsequent code detailed analysis.

##### Subject

  * NameID: Identifier, where the Format property is unspecified, indicating that the IdP has a format defined for it, and assuming that the SP knows how to parse the format data response from the IdP. For example, the IdP gives a format data "UserName=XXXXX Country=US", the SP gets an assertion, and the UserName can be parsed as "XXXXX". Here we are just a character username string format, indicating that the username is wewe.
  * SubjectConfirmation: How the user authenticates, the bearer method used by the method here.
  * SubjectConfirmationData: InResponseTo indicates who the response is to, NotOnOrAfter indicates that it is valid before, Recipient indicates the receiving endpoint.
  * Conditions: Limit the valid time of Assertion, in which the Audience-related tag is some information of the receiver.
  * AuthnStatement: idp uses information for user authentication, authentication authority, etc.
  * AttributeStatement: Some attributes related to users.

### See SAML SSO details through OpenSAML source code

It's the same project as before. Here we focus on the generation of
AuthnRequest by SP and the generation of AuthnResponse by IDP, and the
processing of IDP receiving AuthnRequest and SP receiving AuthnResponse. The
signature and digest, as well as some conversion and verification involved,
are the key points.

#### SP generates AuthnRequest

The call stack to the digest is as follows:

    
    
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

The call stack is the entire process of generating an AuthnRequest. Here we
mainly look at the digest and which part is extracted:

![](https://images.seebug.org/content/images/2022/11/c3ba613a-0dae-4150-aee0-1128e3b7345e.png-w331s)

    
    
    <saml2p:AuthnRequest xmlns:saml2p="urn:oasis:names:tc:SAML:2.0:protocol" AssertionConsumerServiceURL="http://192.168.0.104:9090/saml/SSO" Destination="http://192.168.0.104:8080/SingleSignOnService" ForceAuthn="true" ID="a534936dfbc0a19e32g890f5f33i4ee" IsPassive="false" IssueInstant="2022-10-31T13:16:48.841Z" ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST" Version="2.0"><saml2:Issuer xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion">http://mock-sp</saml2:Issuer></saml2p:AuthnRequest>

The xml content is the content after two transforms:

![](https://images.seebug.org/content/images/2022/11/819226a3-2722-4bfb-9174-ee16d713d4ea.png-w331s)

`Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"`will
excludes the contents of the Signature tag in the
AuthnRequest，`Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"`will
normalized (removing comments and other operations) and compressed, and the
final content will be as above.

Then perform the SHA-256 digest algorithm on this part of the content:

![](https://images.seebug.org/content/images/2022/11/b9cf0350-8822-42a8-834a-de413ca08445.png-w331s)

The call stack to the signature is as follows:

    
    
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

![](https://images.seebug.org/content/images/2022/11/4d1068a3-a4f5-4736-b6f4-7c4487464ff7.png-w331s)

Sign the SingedInfo using the SP's private key (configured in the
application.yml file):

    
    
    <ds:SignedInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#"><ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:CanonicalizationMethod><ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"></ds:SignatureMethod><ds:Reference URI="#a5856d7b1876hii3i40cda0c3fc38h"><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></ds:Transform><ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:Transform></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"></ds:DigestMethod><ds:DigestValue>UEOuyyx4dWr3X0XoQryWQfSzNpXleQ5zSg9LayAEX7E=</ds:DigestValue></ds:Reference></ds:SignedInfo>

After these processes, the xml of the AuthnRequest seen is the one that was
captured and decoded before:

![](https://images.seebug.org/content/images/2022/11/f22274eb-79ad-48a6-b806-b12b115ae2ff.png-w331s)

Finally, there is an http post that transmits base64 encoding, so what you see
in the capture is also base64 encoding.

#### IDP receives AuthnRequest processing

The AuthnRequest sent by SP is extracted and verified in
`mujina.idp.SAMLMessageHandler#extractSAMLMessageContext`:

![](https://images.seebug.org/content/images/2022/11/532cbdce-41c2-47fa-ac78-37e017b12898.png-w331s)

The security policy for AuthnRequest verification only detects whether the
IssueInstant has expired, and there are no other policies. Then there is the
validatorSuites detection, you can see that there are two types of validators,
each with multiple labels corresponding to the specific validator. However,
the test found that IDP did not perform certificate verification, signature
verification, and digest verification on AuthnRequest.

#### IDP generates AuthnResponse

For Assertion signature, the call stack is as follows:

    
    
    calculateDigest:719, Reference (org.apache.xml.security.signature)
    generateDigestValue:406, Reference (org.apache.xml.security.signature)
    generateDigestValues:206, Manifest (org.apache.xml.security.signature)
    sign:609, XMLSignature (org.apache.xml.security.signature)
    signObject:77, Signer (org.opensaml.xml.signature)
    signAssertion:153, SAMLBuilder (mujina.saml)
    sendAuthnResponse:123, SAMLMessageHandler (mujina.idp)
    doSSO:77, SsoController (mujina.idp)
    singleSignOnServicePost:55, SsoController (mujina.idp)

The summary is as follows:

![](https://images.seebug.org/content/images/2022/11/943bcd7f-dde2-4221-9931-261331bf2978.png-w331s)

Summary content:

    
    
    <saml2:Assertion xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:xs="http://www.w3.org/2001/XMLSchema" ID="_2f36cf83-55f7-415e-ba10-5d8188c58e31" IssueInstant="2022-11-01T14:00:37.681Z" Version="2.0"><saml2:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://mock-idp</saml2:Issuer><saml2:Subject><saml2:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified">111111</saml2:NameID><saml2:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer"><saml2:SubjectConfirmationData InResponseTo="a4ebjf264d9b7dja4hicahibc3d2jf8" NotOnOrAfter="2022-11-01T22:00:37.677Z" Recipient="http://192.168.0.104:9090/saml/SSO"></saml2:SubjectConfirmationData></saml2:SubjectConfirmation></saml2:Subject><saml2:Conditions NotBefore="2022-11-01T13:57:37.678Z" NotOnOrAfter="2022-11-01T14:03:37.678Z"><saml2:AudienceRestriction><saml2:Audience>http://mock-sp</saml2:Audience></saml2:AudienceRestriction></saml2:Conditions><saml2:AuthnStatement AuthnInstant="2022-11-01T14:00:37.678Z"><saml2:AuthnContext><saml2:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:Password</saml2:AuthnContextClassRef><saml2:AuthenticatingAuthority>http://mock-idp</saml2:AuthenticatingAuthority></saml2:AuthnContext></saml2:AuthnStatement><saml2:AttributeStatement><saml2:Attribute Name="urn:mace:dir:attribute-def:displayName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John Doe</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:uid" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">111111</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:oasis:names:tc:SAML:attribute:subject-id" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">sdsdsdsd</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:cn" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John Doe</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:sn" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">Doe</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:eduPersonPrincipalName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">j.doe@example.com</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:givenName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:mail" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">j.doe@example.com</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:terena.org:attribute-def:schacHomeOrganization" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">example.com</saml2:AttributeValue></saml2:Attribute></saml2:AttributeStatement></saml2:Assertion>

The same transform algorithm as the previous SP generated AuthnRequest is also
used here, so the Signature tag is excluded and normalized. The SingedInfo
will be signed later, in the same way as the AuthnRequest signature. The
private key for the signature is configured in the application.yml file.

The Response tag will be digested and signed later:

    
    
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

Digest content:

    
    
    <saml2p:Response xmlns:saml2p="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:xs="http://www.w3.org/2001/XMLSchema" Destination="http://192.168.0.104:9090/saml/SSO" ID="_cac5ad52-f303-4356-b061-177f2bc4247c" InResponseTo="a4ebjf264d9b7dja4hicahibc3d2jf8" IssueInstant="2022-11-01T14:00:37.675Z" Version="2.0"><saml2:Issuer xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://mock-idp</saml2:Issuer><saml2p:Status><saml2p:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"></saml2p:StatusCode></saml2p:Status><saml2:Assertion xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion" ID="_2f36cf83-55f7-415e-ba10-5d8188c58e31" IssueInstant="2022-11-01T14:00:37.681Z" Version="2.0"><saml2:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://mock-idp</saml2:Issuer><ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#"><ds:SignedInfo><ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></ds:CanonicalizationMethod><ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"></ds:SignatureMethod><ds:Reference URI="#_2f36cf83-55f7-415e-ba10-5d8188c58e31"><ds:Transforms><ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></ds:Transform><ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"><ec:InclusiveNamespaces xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#" PrefixList="xs"></ec:InclusiveNamespaces></ds:Transform></ds:Transforms><ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"></ds:DigestMethod><ds:DigestValue>XUf3yZB7j4wKYhl3K7Cp4dhfe/E0qKs3a8at+WjZ4Sc=</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>i97x4tGq3whwLpqCIXRsLAy2pn0Wx0+yuHBreiMTwGm4Ekao3DfFvzSfPN5rMVATV59ntBonmUayrZExxsEyVm2xMSFBBEx0JO2stJ6dx2XXPgIiHr7tV5oH9V9wK5OwG1rAHRDMyg4IBCQzLlQrrBZwMCAu/G9FaSw0vBq/COSS8YBrW5/vBH4tS9/NdtTQiXiDoXnGSVYZvXtE0W5anNAUiDytmQhai4dy4Yim/rtKRjIXJVAWD9djCcuR7N//7MWRw1XjWlr1RTwm2TtVvGEY5FL5fVRjdsXJdcc7HNq3UUMQnBpY5RKe+xhri8oZqBc6dmyF96PEUY54EVTdWw==</ds:SignatureValue></ds:Signature><saml2:Subject><saml2:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified">111111</saml2:NameID><saml2:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer"><saml2:SubjectConfirmationData InResponseTo="a4ebjf264d9b7dja4hicahibc3d2jf8" NotOnOrAfter="2022-11-01T22:00:37.677Z" Recipient="http://192.168.0.104:9090/saml/SSO"></saml2:SubjectConfirmationData></saml2:SubjectConfirmation></saml2:Subject><saml2:Conditions NotBefore="2022-11-01T13:57:37.678Z" NotOnOrAfter="2022-11-01T14:03:37.678Z"><saml2:AudienceRestriction><saml2:Audience>http://mock-sp</saml2:Audience></saml2:AudienceRestriction></saml2:Conditions><saml2:AuthnStatement AuthnInstant="2022-11-01T14:00:37.678Z"><saml2:AuthnContext><saml2:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:Password</saml2:AuthnContextClassRef><saml2:AuthenticatingAuthority>http://mock-idp</saml2:AuthenticatingAuthority></saml2:AuthnContext></saml2:AuthnStatement><saml2:AttributeStatement><saml2:Attribute Name="urn:mace:dir:attribute-def:displayName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John Doe</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:uid" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">111111</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:oasis:names:tc:SAML:attribute:subject-id" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">sdsdsdsd</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:cn" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John Doe</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:sn" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">Doe</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:eduPersonPrincipalName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">j.doe@example.com</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:givenName" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">John</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:dir:attribute-def:mail" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">j.doe@example.com</saml2:AttributeValue></saml2:Attribute><saml2:Attribute Name="urn:mace:terena.org:attribute-def:schacHomeOrganization" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"><saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">example.com</saml2:AttributeValue></saml2:Attribute></saml2:AttributeStatement></saml2:Assertion></saml2p:Response>

**Note that the summary now contains Assertion and all sub-tags of Assertion,
and the Signature tag in Response is not included in the summary because it
applies the same transform as before.** After the SingedInfo is signed, the
final xml is what the packet capture looks like.

#### SP receives AuthnResponse processing

    
    
    evaluate:51, BasicSecurityPolicy (org.opensaml.ws.security.provider)
    processSecurityPolicy:132, BaseMessageDecoder (org.opensaml.ws.message.decoder)
    decode:83, BaseMessageDecoder (org.opensaml.ws.message.decoder)
    decode:70, BaseSAML2MessageDecoder (org.opensaml.saml2.binding.decoding)
    retrieveMessage:105, SAMLProcessorImpl (org.springframework.security.saml.processor)
    retrieveMessage:172, SAMLProcessorImpl (org.springframework.security.saml.processor)
    attemptAuthentication:85, SAMLProcessingFilter (org.springframework.security.saml)
    doFilter:223, AbstractAuthenticationProcessingFilter (org.springframework.security.web.authentication)
    doFilter:213, AbstractAuthenticationProcessingFilter (org.springframework.security.web.authentication)

The main checkpoints are two securityPolicies:

![](https://images.seebug.org/content/images/2022/11/359f2c45-3f74-468e-be89-dee9f5f8e9a1.png-w331s)

`SAML2HTTPPostSimpleSignRule` is to verify the signature of the data in the
post transmission, which is easy to understand.

`SAMLProtocolMessageXMLSignatureSecurityPolicyRule` is to verify the signature
in the Saml Response. First, the certificate of the IDP will be extracted from
the local (configured in `classpath:metadata/mujina.local.idp.metadata.xml`),
which is not passed from the Response. Extract the certificate, but use the
configured trusted certificate

![](https://images.seebug.org/content/images/2022/11/566c6bb0-cba7-4f89-8821-b66385576f41.png-w331s)

The call stack is as follows:

    
    
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

![](https://images.seebug.org/content/images/2022/11/8f64a919-ec91-4766-8f58-d8e3291c5609.png-w331s)

Extract the public key from the certificate, decrypt the SignatureValue with
the public key, the decrypted value is the digest of Signedinfo, re-digest the
Signedinfo, and compare it with the decrypted digest value. Then, the digest
value of DigestValue will be compared. This value is the digest of the
Response sub-tag Signature except for the Response sub-tag. The processing
here is to recalculate the digest of this part, and then compare it with
DigestValue:

![](https://images.seebug.org/content/images/2022/11/b7f7ba74-bfe1-4848-90f8-e6f3175bea91.png-w331s)

Of course, there are other verifications in the process, such as status
verification.

Assertion will be verified later:

    
    
    processAuthenticationResponse:301, WebSSOProfileConsumerImpl (org.springframework.security.saml.websso)
    authenticate:88, SAMLAuthenticationProvider (org.springframework.security.saml)
    authenticate:182, ProviderManager (org.springframework.security.authentication)
    attemptAuthentication:92, SAMLProcessingFilter (org.springframework.security.saml)
    doFilter:223, AbstractAuthenticationProcessingFilter (org.springframework.security.web.authentication)
    doFilter:213, AbstractAuthenticationProcessingFilter (org.springframework.security.web.authentication)

![](https://images.seebug.org/content/images/2022/11/d7e80de6-e12a-4cff-8293-5c865b437f55.png-w331s)

The verification method is the same as the verification in the Response. The
certificate is configured locally instead of extracted from the Assertion. The
Sianature and summary information in the Assertion are verified, and whether
the Conditions have expired and whether the recipient in the Subject is The
expected receiving endpoint is verified. After this series of verifications, a
Credential is successfully returned, which contains some information of the
user.

### Security risks in the SAML verification process

For the signature issue, several issues mentioned in the article [Bypassing
SAML 2.0 SSO with XML Signature
Attacks](https://research.aurainfosec.io/bypassing-saml20-SSO/) feel like a
good illustration of SAML Possible security risks:

  * Is a signature required? Maybe some SAML implementations judge whether the signature is carried in the request, verify if it is carried, and not verify if it is not carried; or set a signature verification switch for developers to handle, and developers may not be familiar with not turning on the mandatory verification, etc.
  * Is the signature verified? Although the generated AuthnRequest and Response are signed, but the signature verification is not performed when each receives the SAML message.
  * Is the signature from the correct signer? X509Certificate contains the signer information. If there is no verification of whether it is a trusted certificate, then the certificate can be forged, and then the SAML message can be tampered with and re-signed.
  * Is the correct part of the response signed? There are only two places where the signatures allowed by the SAML standard exist: Response and Assertion. No one has completely implemented a complex XML signature mechanism just to use SAML. This standard is generic, as are its implementations and their software libraries. So if some library does not verify the signature to the correct location, it can refer the signature to a different location in the document, and make the receiver think the signature is valid, causing XSW attack.

There is a SAML Raider plugin in Burp, which can easily modify and forge SAML
attacks, but sometimes it needs to be constructed manually, so it is necessary
to understand the processing flow of SAML.

In "Hacking the Cloud With SAML", a new attack surface is mentioned, which is
the order of the checksum of SignedInfo and the digest check. As can be seen
from the above **SP receives AuthnResponse processing** section, the digest
verification will be processed by transform first, and the calculation of the
digest does not include the content of the Signature tag, so if the digest
verification is performed first, then the operation space under the transforms
is not limited, and the transform can be set arbitrarily, which is also
mentioned in this ppt. There are two CVEs (CVE-2022-34716, CVE-2022-34169),
which are good examples of transform attacks.

#### Problems in the Demo project

The OpenSAML used in the Demo is relatively new. After testing, the processing
of the AuthnResponse received by the SP does not have the above problem. His
verification sequence is as follows:

  * Use locally trusted certificates
  * Check SignedInfo
  * check Digest

So there is no problem with the verification of Response.

However, when IDP receives the AuthnRequest, it only checks whether the
Instant has expired. However, because there is no process for processing
signatures and digests, there is no possibility of other attacks. However, the
IDP is the AssertionConsumerServiceURL obtained from AuthnRequest, and there
is no verification to see if it is expected. Therefore, when the Reponse is
sent back later, it will cause an SSRF problem. The processing of this piece
should be done by the developer, not the library.

### Finally

Since a relatively new version of OpenSAML is used for debugging, some repair
traces can be found during the debugging process, such as the repair of XSW
and ds: Object element attacks. I saw SAML or SAML vulnerability reports
before, because it involves signatures and digests, and it is also for XML
signatures and digests. Is it digested and signed like strings? If not, how to
sign XML, how to digest XML, how to verify XML, how to tamper with forgery in
my attack, what data needs to be modified, how to recalculate signature and
digest, etc. Now it is very clear after debugging.

### Refer

<https://research.aurainfosec.io/bypassing-saml20-SSO/>

<https://drive.google.com/file/d/1p1tTTIjg3RoJecYSU3CetvNw6-ZZdMXn/view>

<https://github.com/OpenConext/Mujina>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2013/>

