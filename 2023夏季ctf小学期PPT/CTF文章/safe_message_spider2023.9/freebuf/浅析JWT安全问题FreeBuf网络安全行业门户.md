前不久研究websocket时发现port-swigger出了新的靶场，一看，发现是关于jwt安全的，刚好来总结回忆一下。

# JWT简介

Json web token (JWT)，是为了在网络应用环境间传递声明而执行的一种基于JSON的开放标准（RFC 7519）。

RFC 7519:<https://datatracker.ietf.org/doc/html/rfc7519>

他定义了一种紧凑且自包含的方式，用于在各方之间安全地传输信息作为 JSON 对象，特别适用于分布式站点的单点登录（SSO）场景。

## JWT与cookie/session的异同

● JWT与cookie/session一样，都是作用于前后端认证。

●
cookie/session：后端有个session，前端有个cookie，这样的基于session的认证会要求服务端不断存储用户登录信息，而随着不同客户端用户的增加，独立的服务器会逐渐无法承载更多的用户，导致其服务器的压力十分巨大，且cookie一旦被窃取还可能造成CSRF攻击。

●
JWT：当我们把前后端分离开来，后端不再有session，当不再需要保存session文件，这就降低了服务端的负担，而我们就可以利用JWT这么一个基于token的鉴权认证，而基于token认证机制的应用就不需要去考虑用户在哪个服务器登录，客户端也可以将通过服务器认证后的json对象存储起来，下次访问时连同请求内容一同发送即可。

## JWT格式

JWT由`Header、Payload、Signature`组成

    
    
    Header.Payload.Signature

![1.png](https://image.3001.net/images/20220808/1659949703_62f0d287eae8bdb6a7bc9.png!small)

Header

    
    
    {"alg":"加密算法","typ":"JWT"}

Payload

    
    
    iss: The issuer of the token  
    sub: The subject of the token  
    aud: The audience of the token  
    exp: JWT expiration time defined in Unix time  
    nbf: "Not before" time that identifies the time before which the JWT must not be accepted for processing  
    iat: "Issued at" time, in Unix time, at which the token was issued  
    jti: JWT ID claim provides a unique identifier for the JWT  
    //可以自定义其它字段

Signature

    
    
    Signature = HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload),"secret")

secret保存在后端，就是来解析确定验证的key。

## JWT&JWS&JWE

● JWS，即JSON Web Signature，只是 JWT 的一种实现

● JWE，即JSON Web Encryption，也只是 JWT 的一种实现

## 潜在漏洞

● 签名未校验

● 算法被篡改

● 敏感信息泄露

● 加密算法不安全

● 伪造密钥(CVE-2018-0114)

# JWT安全问题

## 未对签名进行验证

我们前面说过，JWT存在一个Signature 签名，如若没对签名进行认证，就可能存在越权情况。

 **靶场**

Lab: JWT authentication bypass via unverified signature

 **解法**

    
    
    To solve the lab, modify your session token to gain access to the admin panel at /admin, then delete the user carlos.

我们需要把carlos删掉，而这就需要登录管理员账号，但是又没有给管理员的账号，只有一个普通用户，那我们就要想办法提升权限。

先抓包

![2.png](https://image.3001.net/images/20220808/1659949704_62f0d288d86d17d60d7da.png!small)

观察确定为JWT，将payload处字符base64解码得。

![3.png](https://image.3001.net/images/20220808/1659949705_62f0d289c7c5caca9366f.png!small)

把sub的wiener修改为administrator，重新传参，

![4.png](https://image.3001.net/images/20220808/1659949706_62f0d28ab116866b4b729.png!small)

成功越权，然后就是删除用户即可。

![a.png](https://image.3001.net/images/20220808/1659949707_62f0d28b4f0cd49d96333.png!small)

## 未对加密算法进行强验证

回顾一下Header的构成，

    
    
    {"alg":"加密算法","typ":"JWT"}

这里alg可以说明加密算法，但如果对该设置不进行强认证也会造成越权问题，

我们可以把加密算法设成none来进行验证绕过。

 **靶场**

Lab: JWT authentication bypass via flawed signature verification

 **解法**

先和上题一致，将sub内容修改为administrator，然后发现还是没能成为管理员，接着修改header的alg为none，把后续的Signature删除，因为Signature是通过alg算法生成的，既然alg都为none了，那Signature也应该为空了。

![5.png](https://image.3001.net/images/20220808/1659949708_62f0d28c00c39dd91a0ad.png!small)

成功变成管理员，

![6.png](https://image.3001.net/images/20220808/1659949708_62f0d28cd2d110f9fc053.png!small)

然后就是正常删除用户就行。

## 绕过弱签名密钥进行越权

    
    
    Signature = HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload),"secret")

我们知道，签名存在一个secret密钥，这个一般都会保存在后端，别人无法查看，但是类同于弱口令，一旦这个密钥不复杂就有可能被爆破，gayhub上也有很多爆破的字典。

 **靶场**

Lab: JWT authentication bypass via weak signing key

 **解法**

还是一样先抓包得到JWT，

然后用到hashcat来进行爆破，kali自带。

    
    
    hashcat -a 0 -m 16500 <YOUR-JWT> /path/to/jwt.secrets.list

![7.png](https://image.3001.net/images/20220808/1659949709_62f0d28d8a497365de8fa.png!small)

爆破得到`secret`为secret1，

然后前往jwt.io生成我们需要的的jwt，把sub和secret进行修改。

![8.png](https://image.3001.net/images/20220808/1659949710_62f0d28e7944ee42bcf5d.png!small)

重新传包，成功

![9.png](https://image.3001.net/images/20220808/1659949711_62f0d28f982e1cc8a7cea.png!small)

## JWT标头注入

与很多注入一样，JWT标头注入也可大致分为两种情况，一是与数据库连接，搭配sql注入使用，一是不与数据库连接，单独进行越权操作。

### 通过jwk参数注入自签名的JWT

还记得我们说过的JWS吗

    
    
    JWS，即JSON Web Signature，只是 JWT 的一种实现

我们就可以通过JWK注入JWT，形成JWS，

那什么是JWK呢，

JWK 英文全称为 JSON Web Key，是一个JSON对象，表示一个加密的密钥，他不同于alg属性，JWK是可选的，以下就是一个示例。

    
    
    {  
    "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG",  
    "typ": "JWT",  
    "alg": "RS256",  
    "jwk": {  
    "kty": "RSA",  
    "e": "AQAB",  
    "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG",  
    "n": "yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9m"  
    }  
    }

在理想情况下，服务器应该是只使用公钥白名单来验证JWT签名的，但对于一些相关配置错误的服务器会用JWK参数中嵌入的任何密钥进行验证，攻击者就可以利用这一行为，用自己的RSA私钥对修改过的JWT进行签名，然后在JWK头部中嵌入对应的公钥进行越权操作。

 **靶场**

Lab: JWT authentication bypass via jwk header injection

 **解法**

需要先安装一个插件，方便后续的操作

然后正常抓包，将sub内容修改为administrator

然后切换到JWT Editor Keys选项new一个RSA Key

![11.png](https://image.3001.net/images/20220808/1659949712_62f0d2907cfad17e0a73c.png!small)

我是已经生成的了，然后保存后回到Repeater选择Embedded JWK攻击

![13.png](https://image.3001.net/images/20220808/1659949713_62f0d2913a8cc0aeb52aa.png!small)

成功越权

![12.png](https://image.3001.net/images/20220808/1659949713_62f0d291ed0c4403cadb3.png!small)

JWT Editor

![10.png](https://image.3001.net/images/20220808/1659949714_62f0d292b85ab49bb059b.png!small)

### 通过jku参数注入自签名的JWT

有些服务器并不会直接使用JWK头部参数来嵌入公钥，而是使用JKU（JWK Set URL）来引用一个包含了密钥的JWK
Set，我们就可以借此来构造一个密钥从而实现越权操作。

 **靶场**

Lab: JWT authentication bypass via jku header injection

 **解法**

先还是正常抓包修改sub内容，然后去到JWT Editor Keys生成一个RSA密钥，或者用上一道题目的也行，然后复制公钥。

![14.png](https://image.3001.net/images/20220808/1659949715_62f0d2935a18fc86d8280.png!small)

然后加上key头

    
    
    {  
    "keys": [  
      
    ]  
    }

保存到exploit的body中

![15.png](https://image.3001.net/images/20220808/1659949716_62f0d29408717c3540d58.png!small)

然后将kid修改成自己生成的JWK中的kid值，将jku的值改为exploit，使其导入。

![16.png](https://image.3001.net/images/20220808/1659949716_62f0d294d40c4c5983325.png!small)

然后回到点击下面的sign，选择 **Don’t modify header** 模式，Sign 即可。

![17.png](https://image.3001.net/images/20220808/1659949718_62f0d29626a81629e4fae.png!small)

成功越权

![18.png](https://image.3001.net/images/20220808/1659949718_62f0d296c3d5673a80872.png!small)

### 通过kid参数注入自签名的JWT

服务器可能会使用多个加密密钥来为不同类型的数据进行签名，出于这个原因，在JWT头部有时会包含一个kid参数，以避免服务器验证签名时出现错误，而在JWT规范中并没有对这个kid定义具体的结构，他仅仅是开发人员任意选择的一个字符串，可能只是一个指向数据库中的一个特定条目，甚至只是一个文件的名称也有可能。

而安全问题就出现在这里，一旦这个参数受到目录遍历影响，就易被攻击者使用服务器任意文件的文件名作为验证密钥形成攻击链。

 **靶场**

Lab: JWT authentication bypass via kid header path traversal

 **解法**

先生成一个`Symmetric Key`，也就是对称密钥，并将 k 的值修改为 `AA==`即为null

![19.png](https://image.3001.net/images/20220808/1659949719_62f0d297811328f385492.png!small)

然后抓包修改kid值和sub进行目录遍历，

/dev/null是linux中的“黑洞”，代表空设备文件。

![20.png](https://image.3001.net/images/20220808/1659949720_62f0d2982c69d7562707b.png!small)

 **/dev/null文件名与AA==一致都为null** ，对称密钥，应该可以成功绕过，

然后回到repeater点击sign选择OCT8 的密钥攻击。

![21.png](https://image.3001.net/images/20220808/1659949720_62f0d298dacd8200bc4e6.png!small)

成功越权

### 其他有趣的JWT头部参数

● cty（内容类型）如果已经找到了绕过签名验证的方法，可以尝试注入cty参数，将内容类型改为text/xml或application/x-java-serialized-object，这有可能为XXE和反序列化攻击提供新的向量。

● x5c（X.509证书链）类似于上面讨论的jwk头部注入攻击，由于此标头参数可用于注入自签名证书，且由于 X.509
格式及其扩展的复杂性，引入这些证书时也有可能引入漏洞，可见CVE-2017-2800 和 CVE-2018-2633

## JWT算法混淆

● 即使服务器的密码是攻击者无法破解的复杂密码，但是由于JWT库的一些原生安全问题，攻击者可能会以开发者想不到的算法来伪造有效的JWT

● portswigges里也有相关靶场，目前尚未完全理解，先挖个坑，后续补上

# JWT攻击的防御

我们可以看到，JWT攻击千奇百怪，但是万变不离其宗，主要的潜在漏洞为

● 签名未校验

● 算法被篡改

● 敏感信息泄露

● 加密算法不安全

● 伪造密钥

我们也可围绕这些进行JWT攻击进行防御

● 使用最新的 JWT 库，虽然最新版本的稳定性有待商榷，但是安全性都是较高的

● 对 jku 标头进行严格的白名单设置

● 确保 kid 标头不容易受到通过 header 参数进行目录遍历或 SQL 注入的攻击

● 始终为颁发的任何令牌设置一个到期日

● 尽可能避免通过URL参数发送令牌

● 提供aud声明（或类似内容），以指定令牌的预期接收者，防止其应用在不同网站

● 让颁发服务器能够撤销令牌

